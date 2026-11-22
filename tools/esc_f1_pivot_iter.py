#!/usr/bin/env python3
"""esc_f1_pivot_iter.py -- forward ESC-bay room under F1, with the tilt pivot held at the CG.

WHY THIS EXISTS
---------------
Owner direction 2026-11-22: "See how much room is available further forward.  Don't forget to
account for cg and that the pivot must remain at cg, so if cg shifts, so does the pivot."  Under
F1 (brief F) the 70 A ESC bays lose the pod aft of Z 158.25.  Moving the bays forward moves ESC
mass forward, which moves the CG and therefore the pivot (PIVOT_Z is an OUTPUT of the mass roll-up,
plan 003 KTD7), which in turn moves the pivot-tied keep-outs that bound the bays.  This tool runs
the OD-3 bay optimiser (tools/esc80_cooptimize.py, design tools/esc70_design_f1.json) and the
off-axis CG to a fixed point.

METHOD
  * Pivot = CG of everything OFF the tilt axis (nacelle_mass_cg_64.roll_up: on-axis items cannot
    move it).  Start: today's roll-up (1,052.5 g off-axis, CG 118.86) plus the F1 deltas of
    tools/nozzle64_hinge_root_brief.py (-79.47 g, CG 112.10); the two ESC rows (52.7 g each) and
    the four covers (29.7 g) are removed and re-placed at the optimiser's per-ESC centroids with
    its ESC mass estimate.
  * Pivot-tied keep-outs (esc70_design.json "Inboard/nav measured"): the inboard trunnion /
    disconnect keep-out ends 25.26 mm aft of the pivot (144.16 at 118.9 today); the outboard
    nav-light channel keep-out ends 2.3 mm forward of it (NAV_CHAN_Z_HI = PIVOT_Z - boss - 1).
  * Forward limit (z_min): 75.85 = today's (aft face of the Z 74.3 cavity web), or 49.41 = the aft
    face of the Z 47.9 web.  The 74.3 web is bay-tied (it moves with the bays); the 10 AWG
    disconnect bay stays inside the inboard keep-out.
  * Iterate until the pivot moves < 0.05 mm.

Usage:  /usr/bin/python3 tools/esc_f1_pivot_iter.py Z_MIN [--json PATH]

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (GitHub Stab-Rabbit-coding) -- owner direction.
AI note: Analysis and tool by Claude (Claude Opus 5.5, Anthropic), 2026-11-22, per AGENTS.md
         sec. 3.  Analytical; ENGINEERING REVIEW REQUIRED before any result is applied.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SN = 1.06
P0 = 118.86  # today's off-axis CG = pivot
TR_AFT, NAV_FWD = 144.16 - 118.9, 118.9 - 116.6

# off-axis mass, today (nacelle_mass_cg_64 roll-up): total 1112.5 g incl. 60.0 g on axis
M_OFF0 = 1112.5 - 60.0
# F1 deltas (nozzle64_hinge_root_brief.py, brief F): mass -79.47 g, CG 118.86 -> 112.10
M_F1 = M_OFF0 - 79.47
MOM_F1 = M_F1 * 112.10
# remove today's ESC rows and covers (they move with the bays)
ESC_ROWS = [(52.7, 125.4), (52.7, 136.4)]
COVERS = (29.7, 130.9)
M_REST = M_F1 - sum(m for m, _ in ESC_ROWS) - COVERS[0]
MOM_REST = MOM_F1 - sum(m * z for m, z in ESC_ROWS) - COVERS[0] * COVERS[1]


def run(pivot, z_min, tag):
    d = json.loads((REPO / "tools/esc70_design_f1.json").read_text())
    d["z_min"] = z_min
    ko = d["keepouts"]
    ko[1] = [146.0, 214.0, 40.0, (pivot + TR_AFT) / SN]  # inboard trunnion / disconnect
    ko[2] = [350.0, 370.0, 70.0, (pivot - NAV_FWD) / SN]  # outboard nav light / channel
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / f"fwd_{tag}.json"
        f.write_text(json.dumps(d))
        out = subprocess.run(
            ["/usr/bin/python3", str(REPO / "tools/esc80_cooptimize.py"), str(f)],
            capture_output=True,
            text=True,
            cwd=REPO / "tools",
        )
    return json.loads(out.stdout)


def iterate(z_min, tag):
    p = 112.10
    hist = []
    for it in range(12):
        r = run(p, z_min, f"{tag}_{it}")
        m_esc = r["esc_mass_g_estimate"]
        zc = {k: v["z_centre_mm"] for k, v in r["esc"].items()}
        m_cov = COVERS[0] * 1.0  # cover area scales are second order; keep the mass, move it
        mom = MOM_REST + sum(m_esc * z for z in zc.values()) + m_cov * sum(zc.values()) / 2
        M = M_REST + 2 * m_esc + m_cov
        p_new = mom / M
        hist.append(
            dict(
                it=it,
                pivot_in=round(p, 2),
                pivot_out=round(p_new, 2),
                margin=r["fit_margin_mm"],
                esc={
                    k: (
                        v["margin_mm"],
                        v["m_power_mm"],
                        v["m_logic_mm"],
                        v["board_span_mm"],
                        v["z_board"],
                        v["bays_az"],
                        v["z_centre_mm"],
                    )
                    for k, v in r["esc"].items()
                },
                m_esc=m_esc,
                tch=r["tch_c"],
                M=round(M, 1),
            )
        )
        print(json.dumps(hist[-1]), flush=True)
        if abs(p_new - p) < 0.05:
            break
        p = p_new
    return hist


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    ap.add_argument("z_min", type=float)
    ap.add_argument("--json", type=Path)
    a = ap.parse_args(argv)
    h = iterate(a.z_min, f"z{int(a.z_min)}")
    if a.json:
        a.json.write_text(json.dumps(h, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
