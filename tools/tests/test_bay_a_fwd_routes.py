"""test_bay_a_fwd_routes.py -- Bay A forward harness route table (plan
2026-11-01-001 U1/U2, R3/R4, KTD3/KTD6).

The real-mesh clearance proof is the gate itself (tools/head_layout_fit.py,
tools/twin_head_pack_fit.py); these tests pin the route table's contract:
every route names real envelopes, the FC1 path reaches the port channel with
no gap, uncited stub limits never report PASS, and the side reference mode is
read-only.

Plain asserts so the file runs under pytest or as a script:
    /usr/bin/python3 tools/tests/test_bay_a_fwd_routes.py

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (model: Claude Opus 5.5, Anthropic) under the
author's direction, 2026-11-01, per `AGENTS.md` §3 AI attribution.
License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import head_layout_fit as h  # noqa: E402

_SOLIDS: dict = {}


def _solids():
    """Fwd layout envelopes, built once (layout() runs mesh booleans)."""
    if not _SOLIDS:
        assert h.BAYA_MODE == "fwd", "Bay A forward is the published default (KTD1)"
        L, _ = h.layout()
        _SOLIDS.update({k: e["solid"] for k, e in L.items()})
    return _SOLIDS


def test_every_route_names_real_envelopes():
    lengths = h.route_lengths(_solids())
    assert set(lengths) == set(h.ROUTES)
    assert all(mm > 0 for mm, _ in lengths.values())


def test_unknown_envelope_raises():
    h.ROUTES["bogus"] = (("no such envelope",), "nothing")
    try:
        h.route_lengths(_solids())
    except KeyError as exc:
        assert "no such envelope" in str(exc)
    else:
        raise AssertionError("unknown envelope did not raise")
    finally:
        del h.ROUTES["bogus"]


def test_drop_chain_is_contiguous_to_port_channel():
    """Each envelope in the CN1 -> port channel chain touches the next."""
    s = _solids()
    chain = h.ROUTES["CN1 run -> port channel -> aft"][0]
    for a, b in zip(chain, chain[1:]):
        (alo, ahi), (blo, bhi) = s[a].bounds, s[b].bounds
        assert (alo <= bhi + 1e-6).all() and (blo <= ahi + 1e-6).all(), f"{a} / {b} gap"


def test_crossover_stays_forward_of_tray_stop():
    # twin tray stop plate is Y 159..163 (TRAY_Y0 163 - 4 mm); 1 mm gap
    assert _solids()["trunk: crossover"].bounds[1][1] <= 159.0 - 1.0


def test_stub_status():
    assert h.stub_status(0.0, None) == "PROVISIONAL (limit not cited)"
    assert h.stub_status(50.0, 100.0) == "PASS"
    assert h.stub_status(100.0, 100.0) == "PASS"  # boundary: at the limit
    assert h.stub_status(150.0, 100.0) == "FAIL"


def test_uncited_limits_never_pass():
    for lim in h.STUB_LIMIT_MM.values():
        if lim is None:
            assert h.stub_status(0.0, lim) != "PASS"


def test_side_mode_refuses_write():
    argv = sys.argv
    sys.argv = ["head_layout_fit.py", "--bay-a", "side", "--write-scad"]
    try:
        h.main()
    except SystemExit as exc:
        assert exc.code != 0
    else:
        raise AssertionError("side --write-scad did not exit")
    finally:
        sys.argv = argv
        h.BAYA_MODE = "fwd"


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
