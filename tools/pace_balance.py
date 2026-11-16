#!/usr/bin/env python3
# License: MIT — see LICENSES/MIT.txt (SPDX-License-Identifier: MIT)
"""PACE assignment search for the four Serenity control stacks.

Every role (Watchdog, Comms, Flight Control, Payload) needs a Primary, Alternative, Contingency
and Emergency holder on four different stacks (no single point of failure), and every stack
holds exactly one level of every role (no stack has a single tasking). Those two rules make the
assignment a Latin square; this tool scores all 576 of them.

Score: each stack's load is the sum over roles of role weight x level duty, divided by the
stack's compute capacity. The search minimises the worst stack load in normal flight and after
any one stack is lost (the Alternative of each role the lost stack held as Primary takes over,
and every level below moves up one). Weights and duties are planning assumptions, not measured
CPU figures; replace them when bench loading exists (`--show` prints the inputs used).

Drafted by Claude (Anthropic) for S. Griffing, 2026-11-14.
"""
from __future__ import annotations

import argparse
import itertools
import sys
from typing import Dict, List, Tuple

STACKS = ["Shepherd", "Inara", "River", "Simon"]
ROLES = ["Watchdog", "Comms", "Flight Control", "Payload"]
LEVELS = "PACE"
# [ASSUMED] relative real-time CPU demand of a role when it is Primary.
WEIGHT = {"Watchdog": 1.0, "Comms": 3.0, "Flight Control": 4.0, "Payload": 2.0}
# [ASSUMED] share of the Primary load a holder carries at each level (hot, warm, cold, cold).
DUTY = {"P": 1.0, "A": 0.5, "C": 0.2, "E": 0.1}
# Compute capacity in PB2-I units: full stacks carry two (FC + CN node); the merged stern
# stack carries one PB2-I plus a trust-module MCU (owner decision OD-18, B+, 2026-11-14).
CAPACITY = {"Shepherd": 2.0, "Inara": 2.0, "River": 2.0, "Simon": 1.0}
# Physical affinities on record (root AGENTS.md §9 tasking; avionics/WBS.md §1.9).
FIXED = {("River", "Flight Control"): "P"}


def latin_squares() -> List[Dict[Tuple[str, str], str]]:
    out = []
    for cols in itertools.product(itertools.permutations(LEVELS), repeat=len(ROLES)):
        if all(len({c[i] for c in cols}) == 4 for i in range(4)):
            out.append({(s, r): cols[j][i] for j, r in enumerate(ROLES)
                        for i, s in enumerate(STACKS)})
    return out


def loads(sq: Dict[Tuple[str, str], str], lost: str = "") -> Dict[str, float]:
    res = {}
    for s in STACKS:
        if s == lost:
            continue
        tot = 0.0
        for r in ROLES:
            lvl = sq[(s, r)]
            if lost and LEVELS.index(lvl) > LEVELS.index(sq[(lost, r)]):
                lvl = LEVELS[LEVELS.index(lvl) - 1]  # everyone below the lost holder moves up
            tot += WEIGHT[r] * DUTY[lvl]
        res[s] = tot / CAPACITY[s]
    return res


def score(sq) -> Tuple[float, float]:
    normal = max(loads(sq).values())
    worst = max(max(loads(sq, lost).values()) for lost in STACKS)
    return (worst, normal)


def table(sq) -> str:
    rows = ["| Stack | " + " | ".join(ROLES) + " | Load (normal) | Load (worst one-stack loss) |",
            "|---" * (len(ROLES) + 3) + "|"]
    for s in STACKS:
        w = max(loads(sq, lost).get(s, 0) for lost in STACKS if lost != s)
        rows.append(f"| {s} | " + " | ".join(sq[(s, r)] for r in ROLES)
                    + f" | {loads(sq)[s]:.2f} | {w:.2f} |")
    return "\n".join(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--show", action="store_true", help="print the assumed inputs")
    args = ap.parse_args()
    if args.show:
        print("weights", WEIGHT, "\nduties", DUTY, "\ncapacity", CAPACITY, "\nfixed", FIXED)
    squares = [q for q in latin_squares() if all(q[k] == v for k, v in FIXED.items())]
    current = {("Shepherd", "Watchdog"): "P", ("Inara", "Watchdog"): "A",
               ("Simon", "Watchdog"): "C", ("River", "Watchdog"): "E",
               ("Inara", "Comms"): "P", ("Shepherd", "Comms"): "A",
               ("River", "Comms"): "C", ("Simon", "Comms"): "E",
               ("River", "Flight Control"): "P", ("Simon", "Flight Control"): "A",
               ("Shepherd", "Flight Control"): "C", ("Inara", "Flight Control"): "E",
               ("Simon", "Payload"): "P", ("River", "Payload"): "A",
               ("Inara", "Payload"): "C", ("Shepherd", "Payload"): "E"}
    # Ties on load break toward the fewest changed cells from the current assignment.
    best = min(squares, key=lambda q: (score(q), sum(q[k] != current[k] for k in q)))
    changed = sum(best[k] != current[k] for k in best)
    print(f"{len(squares)} candidate assignments with {FIXED}\n")
    print("Current (avionics/WBS.md §1.9), worst %.2f, normal %.2f" % score(current))
    print(table(current), "\n")
    print("Best, worst %.2f, normal %.2f, %d of 16 cells changed" % (*score(best), changed))
    print(table(best))
    return 0


if __name__ == "__main__":
    sys.exit(main())
