#!/usr/bin/python3
"""Place the LG Option A1b flank-housing envelope at the fore corners.

Owner 2026-10-27: the fore-corner A1b members and CF backbone run up and
outboard (strut az 65 deg) and cross 85-253 mm^3 of the 2 mm cargo flank
skin (tools/lg_a1b_census.py).  The canonical resolution is a recessed
housing in the flank above each fore bay, as QMx Sheet 5 [REF-CAD-003] and
the Henning renders [REF-CAD-002] show where the jack enters the hull.

This renders a1b_housing_envelope() (canonical_leg_r6_3_0in.scad: hull of
the backbone and the members at rest and full flex) for the fore station,
places it at each fore corner with the bay generator's corner transform, and
writes it in the hull frame to
airframe/stls/fuselage/landing-gear/lg_a1b_housing_<corner>.stl, which
airframe/blender-scripts/merge_cargo_interior.py reads to cut the pocket
and wall it.

Run:  /usr/bin/python3 tools/generate_lg_a1b_housing.py

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, 2026-10-27, per AGENTS.md section 3 AI attribution.
License: CERN-OHL-W-2.0 (writes hardware geometry) -- see LICENSE.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import landing_gear_bay_function as lgbf  # noqa: E402

OUT = os.path.join(HERE, "..", "airframe", "stls", "fuselage", "landing-gear")
FORE = ("fore-port", "fore-stbd")


def main() -> int:
    """Write one hull-frame housing envelope STL per fore corner."""
    corners = lgbf.parse_corners(lgbf.SCAD)
    env = lgbf.render(lgbf.SCAD, "fore", "a1b housing envelope", "a1b_housing_envelope();")
    for label in FORE:
        m = lgbf.posed(env, lgbf.corner_tf(corners[label]))
        path = os.path.join(OUT, f"lg_a1b_housing_{label}.stl")
        lgbf.cbc.tri(m).export(path)
        print(f"{label}: housing envelope {m.volume():.0f} mm3 -> {os.path.relpath(path, HERE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
