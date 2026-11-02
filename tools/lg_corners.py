#!/usr/bin/env python3
"""The landing-gear corner stations, read from their single source.

canonical_leg_r6_3_0in.scad CORNERS is the one place the four hip stations
are defined (aircraft datum R2: [hip_x, hip_y, hip_z, swing_azimuth_deg,
hand]).  Every tool that needs them imports this module instead of keeping its
own copy -- before 2026-10-19 four tools did, and they had drifted into three
different sets (owner direction: "standardize the generator scripts to
prevent future drift").

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, 2026-10-19, per AGENTS.md AI attribution.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import re
from pathlib import Path

SCAD = (Path(__file__).resolve().parent.parent
        / "airframe/openscad/fuselage/canonical_leg_r6_3_0in.scad")
NAMES = ("fore-port", "fore-stbd", "aft-port", "aft-stbd")
STATION = {n: n.split("-")[0] for n in NAMES}


def _row(txt: str, name: str) -> list[float]:
    """Parse `NAME = [ v, v, ... ];` (one literal port row) from the SCAD."""
    m = re.search(rf"^{name}[ \t]*=[ \t]*\[([^\]]*)\]", txt, re.M)
    if m is None:
        raise RuntimeError(f"{name} row not found in {SCAD.name}")
    return [float(v) for v in m.group(1).split(",")]


def corners(path: Path = SCAD) -> dict[str, list[float]]:
    """{name: [hip_x, hip_y, hip_z, azimuth_deg, hand]} from the SCAD.

    2026-11-01 (owner: symmetric across the centreline): the SCAD types only
    the PORT rows (LG_FORE_PORT, LG_AFT_PORT); starboard is DERIVED by
    lg_mirror_row() about X_CL.  This mirrors the SCAD function exactly:
    x -> 2 X_CL - x, az -> 180 - az, hand -> -hand.
    """
    import hull_datums as hd  # tools/ is on sys.path for every caller
    txt = Path(path).read_text(encoding="utf-8")
    fore, aft = _row(txt, "LG_FORE_PORT"), _row(txt, "LG_AFT_PORT")

    def mirror(c: list[float]) -> list[float]:
        return [2.0 * hd.X_CL - c[0], c[1], c[2], 180.0 - c[3], -c[4]]

    rows = [fore, mirror(fore), aft, mirror(aft)]
    if any(len(r) != 5 for r in rows):
        raise RuntimeError(f"expected 5-value port rows, parsed {fore} / {aft}")
    return dict(zip(NAMES, rows, strict=True))


def table() -> list[tuple[str, float, float, float, float]]:
    """[(name, hip_x, hip_y, hip_z, azimuth)] -- the legacy tuple layout."""
    return [(n, c[0], c[1], c[2], c[3]) for n, c in corners().items()]


if __name__ == "__main__":
    for row in table():
        print(row)
