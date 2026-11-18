"""The RCS jet table, one source for tools/rear_cone_layout_fit.py (which gates it against the
published aft hull) and tools/hover_trim_rcs.py (which credits its moments).  Plan 002 U5,
TEDF-05.

Hull frame R2, mm: X port, Y aft, Z up; azimuth about the thrust axis from +X, 90 = up,
270 = straight down.

Owner decision 2026-11-18 (brief 3, option B): one ventral jet at 270 deg, canted 25 deg aft,
whose exhaust sides lie on the port and starboard joints of the centre belly panel (joint
grooves at 245.5 and 294.5 deg, measured on the Rev U hull from Y 632 to Y 648), from Y 635
(clear of the skid crossbar) to Y 649.  The upper pair stays at 45 and 135 deg, normal to the
axis.  The planned pair (245/295 deg at Y 632, S43) is kept only as a comparison.

`r_mm` and `area_mm2` are measured on the hull; tools/tests/test_rear_cone_layout_fit.py ties
them back to the mesh, so a hull change that moves them fails a test.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (Anthropic) under the author's direction, 2026-11-18, per AGENTS.md
         section 3.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""
from __future__ import annotations

import math
from dataclasses import dataclass

BORE_MM = 0.71 * 25.4  # plan 002 RCS sizing: four jets of 0.71 in bore
BORE_AREA_MM2 = math.pi / 4.0 * BORE_MM ** 2


@dataclass(frozen=True)
class RcsJet:
    name: str
    az_deg: float
    cant_deg: float  # aft cant of the exhaust direction
    y0: float  # exhaust forward edge on the skin
    y1: float  # exhaust aft edge on the skin
    area_mm2: float  # exhaust flow area
    r_mm: float  # outer skin radius at the exhaust centre (measured)
    sector: tuple[float, float]  # passage sector in the tube-to-skin gap (azimuths, deg)
    edges: str = "centred"  # "centred": width = area / length; "panel": sides on the joints
    panel: tuple[float, float] = (0.0, 0.0)  # joint azimuths bounding a "panel" exhaust

    @property
    def y(self) -> float:
        return 0.5 * (self.y0 + self.y1)

    @property
    def ventral(self) -> bool:
        return math.sin(math.radians(self.az_deg)) < 0.0


# The upper passage sectors are 45 deg until the owner settles brief 4 (proposed: 55 deg).
JETS: tuple[RcsJet, ...] = (
    RcsJet("upper 45", 45.0, 0.0, 632.0, 642.0, BORE_AREA_MM2, 39.44, (22.5, 67.5)),
    RcsJet("upper 135", 135.0, 0.0, 632.0, 642.0, BORE_AREA_MM2, 39.39, (112.5, 157.5)),
    RcsJet("ventral 270", 270.0, 25.0, 635.0, 649.0, 428.0, 36.84, (220.0, 320.0),
           edges="panel", panel=(245.5, 294.5)),
)

# S43 / plan 002 as first written: 245/295 at Y 632 (strike the skid pods; comparison only).
PLAN_JETS: tuple[RcsJet, ...] = (
    RcsJet("ventral 245", 245.0, 25.0, 627.0, 637.0, BORE_AREA_MM2, 43.4, (222.5, 267.5)),
    RcsJet("ventral 295", 295.0, 25.0, 627.0, 637.0, BORE_AREA_MM2, 43.4, (272.5, 317.5)),
    RcsJet("upper 45", 45.0, 0.0, 627.0, 637.0, BORE_AREA_MM2, 43.4, (22.5, 67.5)),
    RcsJet("upper 135", 135.0, 0.0, 627.0, 637.0, BORE_AREA_MM2, 43.4, (112.5, 157.5)),
)
