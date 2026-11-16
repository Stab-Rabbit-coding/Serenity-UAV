"""test_bay_a_fwd_mounts.py -- Bay A forward mounts and hatch (plan
2026-11-01-001 U3, R2; KTD2, KTD7).

The real-mesh clearance proof is tools/head_layout_fit.py, which gates every
generated part.  These tests pin what the gate does not: every part is a
closed solid, the service path is stated and names every removable part, the
hatch screws stay clear of the Observer, and CN1's removal sweep is free once
FC1, its shelf and the gate are out.

Plain asserts so the file runs under pytest or as a script:
    /usr/bin/python3 tools/tests/test_bay_a_fwd_mounts.py
(run tools/gen_bay_a_fwd_mounts.py first; the tests read its STLs)

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5.5, Anthropic) under the
author's direction, 2026-11-01, per `AGENTS.md` §3 AI attribution.
License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import trimesh  # noqa: E402

import gen_bay_a_fwd_mounts as g  # noqa: E402
import head_layout_fit as h  # noqa: E402
from cargo_layout_fit import box, to_man  # noqa: E402

PARTS = ("bay_a_cn1_drawer", "bay_a_cn1_gate", "bay_a_fc1_shelf", "bay_a_hatch_cover",
         "bay_a_hatch_flange")


def _load(name):
    return trimesh.load(os.path.join(g.OUT_DIR, name + ".stl"))


def test_every_part_is_a_closed_solid():
    for name in PARTS:
        m = _load(name)
        assert m.is_watertight and m.volume > 0, name
    assert trimesh.load(g.HULL_OUT).is_watertight


def test_service_path_is_stated_in_order():
    sp = g.SERVICE_PATH
    steps = ["1.", "2.", "3.", "4."]
    assert all(st in sp for st in steps)
    order = [sp.index(k) for k in ("hatch screws", "FC1:", "FC1 shelf", "CN1:")]
    assert order == sorted(order), "service steps out of order"
    assert "Observer stays in place" in sp


def test_hatch_screws_clear_of_observer():
    pts = g.hatch_fastener_xy()
    assert len(pts) == 8
    for x, y in pts:
        assert y >= g.FLANGE_Y0, (x, y)
        assert abs(x) <= h.HATCH_X and y <= h.HATCH_Y1, (x, y)


def test_hatch_is_on_the_canonical_panel():
    """Seams: window-aft frame Y 60, transverse frame Y 137 (REF-CAD-003/002)."""
    assert (h.HATCH_Y0, h.HATCH_Y1, h.HATCH_X) == (60.0, 137.0, 27.0)


def test_cn1_removal_sweep_is_clear_of_the_drawer():
    """CN1 slides aft 26 mm inside the drawer: the swept box never meets it."""
    sweep = box(-18.5, 18.5, h.CN1F_Y0, h.CN1F_Y0 + 58.0 + 26.0, h.CN1F_Z0 + 0.1,
                h.CN1F_Z0 + 22.0)
    drawer = _load("bay_a_cn1_drawer")
    assert (to_man(sweep) ^ to_man(drawer)).volume() < 0.5


def test_cn1_slid_aft_clears_the_observer():
    L, _ = h.layout()
    slid = box(-18.5, 18.5, h.CN1F_Y0 + 26.0, h.CN1F_Y0 + 84.0, h.CN1F_Z0, 270.0)
    assert (to_man(slid) ^ to_man(L["Observer board"]["solid"])).volume() < 0.5


def test_statics_load_is_reported_provisional():
    f = g.statics()
    assert abs(f - 3.0 * 0.058 * 79.4 * 9.80665) < 0.1


if __name__ == "__main__":
    fails = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception as exc:  # noqa: BLE001 -- script runner reports every failure
                fails += 1
                print(f"FAIL {name}: {type(exc).__name__}: {exc}")
    sys.exit(1 if fails else 0)
