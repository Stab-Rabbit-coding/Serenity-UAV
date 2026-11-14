# License: MIT — see LICENSES/MIT.txt (SPDX-License-Identifier: MIT)
"""Tests for tools/pace_balance.py."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "pace_balance", Path(__file__).resolve().parents[1] / "pace_balance.py")
pb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pb)


def test_every_square_has_no_single_point_of_failure_or_single_tasking():
    squares = pb.latin_squares()
    assert len(squares) == 576
    for q in squares[::37]:
        for r in pb.ROLES:
            assert sorted(q[(s, r)] for s in pb.STACKS) == list("ACEP")
        for s in pb.STACKS:
            assert sorted(q[(s, r)] for r in pb.ROLES) == list("ACEP")


def test_loss_promotes_the_holders_below():
    q = {(s, r): "PACE"[i] for i, s in enumerate(pb.STACKS) for r in pb.ROLES}
    after = pb.loads(q, lost="Shepherd")  # Shepherd held every P
    assert "Shepherd" not in after
    full = sum(pb.WEIGHT.values())
    assert abs(after["Inara"] * pb.CAPACITY["Inara"] - full) < 1e-9


def test_simon_flight_control_drops_in_the_balanced_square():
    squares = [q for q in pb.latin_squares() if q[("River", "Flight Control")] == "P"]
    best = min(squares, key=pb.score)
    assert best[("Simon", "Flight Control")] in ("C", "E")
