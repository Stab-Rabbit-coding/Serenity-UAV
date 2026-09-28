"""Tests for tools/nozzle_servo_linkage.py — servo nozzle drive (plan U2).

Plan: docs/plans/2026-09-28-001-feat-nacelle-nozzle-servo-drive-plan.md, U2.
Author: Steve Griffing (GitHub Stab-Rabbit-coding) — requirements and decisions.
AI contribution: Claude (Claude Opus 5.5, Anthropic) — test authoring.
License: CC BY 4.0 <https://creativecommons.org/licenses/by/4.0/>
"""

import math
import unittest

from tools import nozzle_servo_linkage as nsl


class ScheduleTest(unittest.TestCase):
    """Tilt -> ring -> exit radius schedule (requirement R1)."""

    def test_zero_tilt_gives_75_percent_exit(self) -> None:
        # Happy path: 0 deg tilt (cruise) -> 75 % of the 25 mm bore radius.
        psi = nsl.ring_angle_for_tilt(0.0)
        self.assertAlmostEqual(nsl.exit_radius_for_ring(psi), 18.75, delta=0.1)

    def test_ninety_tilt_gives_105_percent_exit(self) -> None:
        # Happy path: 90 deg tilt (hover) -> 105 % of bore radius.
        psi = nsl.ring_angle_for_tilt(90.0)
        self.assertAlmostEqual(nsl.exit_radius_for_ring(psi), 26.25, delta=0.1)

    def test_hold_flat_from_90_to_145(self) -> None:
        # Edge: the requirement holds 105 % over the whole 90-145 deg band.
        ref = nsl.ring_angle_for_tilt(90.0)
        for tilt in (90.0, 105.0, 120.0, 145.0):
            self.assertEqual(nsl.ring_angle_for_tilt(tilt), ref)

    def test_beyond_limit_clamps_with_warning(self) -> None:
        # Edge: 150 deg is past the 145 deg tilt limit -> clamp, and warn.
        with self.assertWarns(UserWarning):
            psi = nsl.ring_angle_for_tilt(150.0)
        self.assertEqual(psi, nsl.ring_angle_for_tilt(90.0))

    def test_invalid_tilt_commands_open(self) -> None:
        # Error path: NaN or None tilt -> fail-safe 105 % command (R2).
        open_psi = nsl.ring_angle_for_tilt(90.0)
        self.assertEqual(nsl.ring_angle_for_tilt(float("nan")), open_psi)
        self.assertEqual(nsl.ring_angle_for_tilt(None), open_psi)

    def test_schedule_monotonic_0_to_90(self) -> None:
        # Edge: no reversal anywhere across the scheduled band.
        prev = -math.inf
        for tilt in range(91):
            psi = nsl.ring_angle_for_tilt(float(tilt))
            self.assertGreaterEqual(psi, prev)
            prev = psi


class LinkageTest(unittest.TestCase):
    """Servo arm -> pull link -> ring lever geometry."""

    def test_arm_radius_for_default_sweep(self) -> None:
        # 13.2 mm lever chord over a 90 deg servo sweep -> ~9.3 mm arm.
        arm = nsl.arm_radius_for_stroke(sweep_deg=90.0)
        self.assertAlmostEqual(arm, 9.33, delta=0.1)

    def test_pwm_table_endpoints(self) -> None:
        # Integration: table rows run from 75 % to 105 % and stay in 1000-2000 us.
        rows = nsl.build_table()
        self.assertAlmostEqual(rows[0]["exit_pct"], 75.0, delta=0.5)
        self.assertAlmostEqual(rows[-1]["exit_pct"], 105.0, delta=0.5)
        for row in rows:
            self.assertGreaterEqual(row["pulse_us"], 1000)
            self.assertLessEqual(row["pulse_us"], 2000)

    def test_slot_covers_full_stroke(self) -> None:
        # R2 / KTD3: the pull-only slot must exceed the full lever chord + 1 mm.
        self.assertGreaterEqual(nsl.SLOT_LEN_MM, nsl.lever_chord_mm() + 1.0)


class MarginTest(unittest.TestCase):
    """Spring / servo force margins (KTD2, KTD3)."""

    def test_spring_over_40_percent_fails(self) -> None:
        # Error path: a spring > 40 % of servo pull must fail the check.
        res = nsl.check_margins(servo=nsl.SERVOS["BMS-101DMG"],
                                spring_n=5.0, flap_load_n=0.0, measured=True)
        self.assertFalse(res["pass"])

    def test_placeholder_load_reports_pending_not_pass(self) -> None:
        # The 20 N placeholder is never reported as PASS.
        res = nsl.check_margins(servo=nsl.SERVOS["BMS-101DMG"],
                                spring_n=2.0, flap_load_n=None, measured=False)
        self.assertEqual(res["status"], "PENDING-U8")

    def test_linear_servo_fails_at_placeholder_passes_below_1n(self) -> None:
        # The AGFRC linear servo (2.4 N) fails at 20 N and only passes under ~1 N.
        agfrc = nsl.SERVOS["AGFRC-C1.5CLS"]
        hi = nsl.check_margins(servo=agfrc, spring_n=0.5, flap_load_n=20.0, measured=True)
        lo = nsl.check_margins(servo=agfrc, spring_n=0.5, flap_load_n=0.3, measured=True)
        self.assertFalse(hi["pass"])
        self.assertTrue(lo["pass"])


if __name__ == "__main__":
    unittest.main()
