#!/usr/bin/env python3
"""Joint register loader and checker for the build-guide torque method.

Plan docs/plans/2026-11-02-001-feat-build-guide-joint-torque-and-sequence-plan.md, unit U1
(requirements R1, R3): one authoritative list of joints, so that every fastener on the bill of
materials belongs to a joint, and so that no torque can be released for a joint whose inputs are
still unknown.

The register lives in current-specification/joint_register.json.  This tool:

  * validates its structure (unique IDs, joint classes, threaded joints name a fastener size);
  * checks every joint's BOM references exist in current-specification/bom_revT.json;
  * checks coverage: every BOM row in the register's scope (hardware-class categories plus the
    explicit extra refs) is in a joint or in the exempt list with a reason, and no exempt row is
    also claimed by a joint;
  * reports which threaded joints are BLOCKED because a field is still "unknown";
  * reports, as advisory only, build-guide cards that mention fasteners (cards are being
    re-audited under graphical-build-guide/WBS.md BG-SEQ-1, so they do not yet cite joint IDs).

Usage::

    /usr/bin/python3 tools/joint_register.py --check      # exit 1 on a structural or coverage error
    /usr/bin/python3 tools/joint_register.py --summary    # list joints and blockers

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (requirement and direction).
Written by Claude Sonnet 5.5 (Anthropic) under the author's direction, 2026-11-02,
per AGENTS.md section 3 AI attribution.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "current-specification" / "joint_register.json"
BOM = ROOT / "current-specification" / "bom_revT.json"
CARD_DIR = ROOT / "graphical-build-guide"

JOINT_CLASSES = {"threaded", "pinned", "pressed", "bonded", "clamped"}
REQUIRED = ("id", "name", "subsystem", "bom_refs", "joint_class", "fasteners", "members",
            "retention", "unknown_fields")
FASTENER_WORDS = re.compile(r"\bM[1-6](\.5)?\b|screw|bolt|insert|torque", re.I)


def load() -> tuple[dict, dict[str, dict]]:
    """Return (register, BOM rows keyed by Ref)."""
    reg = json.loads(REGISTER.read_text())
    bom = {r["Ref"]: r for r in json.loads(BOM.read_text())["items"]}
    return reg, bom


def validate(reg: dict, bom: dict[str, dict]) -> list[str]:
    """Structural, reference and coverage errors; empty list means clean."""
    errs: list[str] = []
    ids: set[str] = set()
    claimed: dict[str, str] = {}
    for j in reg["joints"]:
        jid = j.get("id", "?")
        for key in REQUIRED:
            if key not in j:
                errs.append(f"{jid}: missing field '{key}'")
        if jid in ids:
            errs.append(f"{jid}: duplicate joint ID")
        ids.add(jid)
        if j.get("joint_class") not in JOINT_CLASSES:
            errs.append(f"{jid}: joint_class '{j.get('joint_class')}' not in {sorted(JOINT_CLASSES)}")
        if j.get("joint_class") == "threaded" and not any(f.get("size") for f in j.get("fasteners", [])):
            errs.append(f"{jid}: threaded joint names no fastener size")
        for ref in j.get("bom_refs", []):
            if ref not in bom:
                errs.append(f"{jid}: BOM ref '{ref}' not in bom_revT.json")
            elif ref in reg["exempt"]:
                errs.append(f"{jid}: BOM ref '{ref}' is both in a joint and exempt")
            else:
                claimed.setdefault(ref, jid)
    scope = set(reg["scope"]["extra_refs"])
    scope |= {ref for ref, r in bom.items() if r["Category"] in reg["scope"]["categories"]}
    for ref in sorted(scope):
        if ref not in claimed and ref not in reg["exempt"]:
            errs.append(f"BOM ref '{ref}' ({bom[ref]['Category']}) is in no joint and not exempt")
    for ref, why in reg["exempt"].items():
        if ref not in bom:
            errs.append(f"exempt ref '{ref}' not in bom_revT.json (stale exemption: {why})")
        if not why:
            errs.append(f"exempt ref '{ref}' has no reason")
    return errs


def blocked(reg: dict) -> list[dict]:
    """Threaded joints that cannot receive a torque yet (any unknown field)."""
    return [j for j in reg["joints"] if j["joint_class"] == "threaded" and j["unknown_fields"]]


def card_advisory() -> list[str]:
    """Cards that mention fasteners (advisory: cards are not yet joint-ID aware)."""
    out = []
    for svg in sorted(CARD_DIR.glob("build_guide_[0-9][0-9]_*.svg")):
        if FASTENER_WORDS.search(svg.read_text()):
            out.append(svg.name)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 on any error")
    ap.add_argument("--summary", action="store_true", help="list joints and blockers")
    args = ap.parse_args()
    reg, bom = load()
    errs = validate(reg, bom)
    for e in errs:
        print(f"joint_register: ERROR: {e}", file=sys.stderr)
    bl = blocked(reg)
    if args.summary or not args.check:
        by_class: dict[str, int] = {}
        for j in reg["joints"]:
            by_class[j["joint_class"]] = by_class.get(j["joint_class"], 0) + 1
        print(f"{len(reg['joints'])} joints {by_class}; {len(reg['exempt'])} exempt BOM rows")
        print(f"{len(bl)} threaded joints BLOCKED (no torque can be released):")
        for j in bl:
            print(f"  {j['id']:24s} needs: {', '.join(j['unknown_fields'])}")
        cards = card_advisory()
        print(f"advisory: {len(cards)} cards mention fasteners and do not yet cite joint IDs (BG-SEQ-1)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
