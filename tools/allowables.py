#!/usr/bin/env python3
"""Cited-allowables database and selector for the joint-torque method.

Plan docs/plans/2026-11-02-001-feat-build-guide-joint-torque-and-sequence-plan.md, unit U3
(requirements R2, R3, R5).  Data live in current-specification/allowables.json and
current-specification/safety_factors.json.

Rules enforced here (and by ``--check``):

  * every property that carries a value also carries a source REF-ID and location;
  * a property with no value says "requires_verification" and what would establish it --
    the selector NEVER returns a default for it (raises Unknown);
  * material selection follows the owner's preference order (printable composite, laid-up
    CF/Kevlar/glass, aluminum, brass, spring steel, stainless); the first candidate that has a
    CITED value for the requested property wins;
  * the fastener factor of safety is 1.5 (owner 2026-11-02) unless an override that cites a
    VERIFIED more-conservative source exists; the larger value governs.

Usage::

    /usr/bin/python3 tools/allowables.py --check
    /usr/bin/python3 tools/allowables.py --open       # list unresolved (requires_verification) data

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (requirement and direction).
Written by Claude Sonnet 5.5 (Anthropic) under the author's direction, 2026-11-02,
per AGENTS.md section 3 AI attribution.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "current-specification" / "allowables.json"
SF = ROOT / "current-specification" / "safety_factors.json"


class Unknown(LookupError):
    """The requested allowable is not established; says what would establish it."""


def load() -> dict:
    return json.loads(DB.read_text())


def get(db: dict, material: str, prop: str) -> dict:
    """Return the cited property record, or raise Unknown."""
    try:
        rec = db["materials"][material]["props"][prop]
    except KeyError as exc:
        raise Unknown(f"{material}.{prop}: not in the database") from exc
    if rec.get("value") is None:
        raise Unknown(
            f"{material}.{prop}: requires verification -- {rec.get('would_establish', '?')}"
        )
    return rec


def select(db: dict, candidates: list[str], prop: str) -> tuple[str, dict]:
    """Highest-preference candidate with a cited value for ``prop``."""
    order = db["preference_order"]

    def rank(m: str) -> int:
        cat = db["materials"][m]["category"]
        return order.index(cat) if cat in order else len(order)

    unknown: list[str] = []
    for m in sorted(candidates, key=rank):
        try:
            return m, get(db, m, prop)
        except Unknown as exc:
            unknown.append(str(exc))
    raise Unknown("no candidate has a cited value: " + "; ".join(unknown))


def fastener_fos(sf: dict | None = None, fitting_exempt: bool = False) -> float:
    """Effective factor of safety for a fastened joint.

    1.5 (owner default) unless a VERIFIED, independently derived override is larger.  The NASA
    fitting factor is deliberately NOT stacked on the owner's factor: it multiplies NASA's own
    program-levied factor, so it can only be compared as ``nasa_equivalent_fos`` (below).  It is
    applied here only if the owner sets ``fitting_factor.apply_by_default``.
    """
    sf = sf or json.loads(SF.read_text())
    best = float(sf["fastener_default"])
    ff = sf.get("fitting_factor", {})
    if ff.get("apply_by_default") and not fitting_exempt:
        best *= float(ff["value"])
    for o in sf.get("overrides", []):
        if o.get("verified") and float(o["value"]) > best:
            best = float(o["value"])
    return round(best, 4)


def nasa_equivalent_fos(fs_program: float, sf: dict | None = None) -> float:
    """NASA-STD-5020B's independent total: its program-levied factor times the fitting factor.

    Compare the result against ``fastener_default``; it is an override only when larger AND
    ``fs_program`` comes from a verified source (NASA-STD-5001 is not yet catalogued).
    """
    sf = sf or json.loads(SF.read_text())
    return round(fs_program * float(sf["fitting_factor"]["value"]), 4)


def validate(db: dict, sf: dict) -> list[str]:
    errs: list[str] = []
    for mname, m in db["materials"].items():
        if m.get("category") not in db["preference_order"]:
            errs.append(f"{mname}: category '{m.get('category')}' not in preference_order")
        for pname, rec in m["props"].items():
            if rec.get("value") is None:
                if rec.get("status") != "requires_verification" or not rec.get("would_establish"):
                    errs.append(f"{mname}.{pname}: empty value needs status and would_establish")
            else:
                src = rec.get("source", {})
                if not src.get("ref") or not src.get("location"):
                    errs.append(f"{mname}.{pname}: value without a cited source ref and location")
    if sf["fastener_default"] < 1.5:
        errs.append("fastener_default is below the owner's 1.5 minimum")
    for o in sf.get("overrides", []):
        if o.get("verified") and not o.get("ref"):
            errs.append("a verified override must cite a ref")
        if float(o.get("value", 0)) <= sf["fastener_default"]:
            errs.append(f"override {o.get('ref')} is not more conservative than the default")
    return errs


def open_items(db: dict) -> list[str]:
    out = []
    for mname, m in db["materials"].items():
        for pname, rec in m["props"].items():
            if rec.get("value") is None:
                out.append(f"{mname}.{pname}: {rec['would_establish']}")
    if db["nut_factor_K"].get("value") is None:
        out.append("nut_factor_K: " + db["nut_factor_K"]["would_establish"])
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--open", action="store_true")
    args = ap.parse_args()
    db, sf = load(), json.loads(SF.read_text())
    errs = validate(db, sf)
    for e in errs:
        print(f"allowables: ERROR: {e}", file=sys.stderr)
    if args.open or not args.check:
        items = open_items(db)
        print(f"{len(items)} unresolved allowables; fastener FoS = {fastener_fos(sf)}")
        for i in items:
            print("  " + i)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
