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

from pathlib import Path

SCAD = (Path(__file__).resolve().parent.parent
        / "airframe/openscad/fuselage/canonical_leg_r6_3_0in.scad")
NAMES = ("fore-port", "fore-stbd", "aft-port", "aft-stbd")
STATION = {n: n.split("-")[0] for n in NAMES}


def corners(path: Path = SCAD) -> dict[str, list[float]]:
    """{name: [hip_x, hip_y, hip_z, azimuth_deg, hand]} parsed from the SCAD."""
    txt = path.read_text(encoding="utf-8")
    blk = txt[txt.index("CORNERS = ["):]
    blk = blk[:blk.index("\n];")]          # the closing line, not a "];" in a comment
    rows = []
    for line in blk.splitlines()[1:]:
        line = line.split("//")[0].strip()
        if line.startswith("["):
            rows.append([float(v) for v in line.strip("[],").split(",")])
    if len(rows) != 4 or any(len(r) not in (4, 5) for r in rows):
        raise RuntimeError(f"expected 4 CORNERS rows of 4-5 values, parsed {rows}")
    return {n: (r + [1.0])[:5] if len(r) == 4 else r for n, r in zip(NAMES, rows, strict=True)}


def table() -> list[tuple[str, float, float, float, float]]:
    """[(name, hip_x, hip_y, hip_z, azimuth)] -- the legacy tuple layout."""
    return [(n, c[0], c[1], c[2], c[3]) for n, c in corners().items()]


if __name__ == "__main__":
    for row in table():
        print(row)
