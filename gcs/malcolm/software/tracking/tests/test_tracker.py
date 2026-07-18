"""
test_tracker.py — Unit tests for tracker.py bearing and elevation calculations.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
Revision: R (2026-06-11)

Run with:
    cd gcs/malcolm/software/tracking
    pytest tests/test_tracker.py -v
"""

import sys
from pathlib import Path

# Add the src directory to the module search path.
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tracker import (  # noqa: E402
    GeoPosition,
    compute_gimbal_target,
)

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def approx(value: float, expected: float, tol: float = 0.5) -> bool:
    """Return True if |value − expected| < tol."""
    return abs(value - expected) < tol


# ---------------------------------------------------------------------------
# Bearing tests
# ---------------------------------------------------------------------------


class TestBearing:
    """Tests for bearing calculation (azimuth from GCS to aircraft)."""

    def test_due_north(self) -> None:
        """Aircraft directly north of GCS → azimuth ≈ 0°."""
        gcs = GeoPosition(lat_deg=30.0, lon_deg=-90.0, alt_m=0.0)
        aircraft = GeoPosition(lat_deg=30.1, lon_deg=-90.0, alt_m=50.0)
        target = compute_gimbal_target(gcs, aircraft)
        assert approx(
            target.azimuth_deg, 0.0
        ), f"Expected ~0° (North), got {target.azimuth_deg:.2f}°"

    def test_due_east(self) -> None:
        """Aircraft directly east of GCS → azimuth ≈ +90°."""
        gcs = GeoPosition(lat_deg=30.0, lon_deg=-90.0, alt_m=0.0)
        aircraft = GeoPosition(lat_deg=30.0, lon_deg=-89.9, alt_m=50.0)
        target = compute_gimbal_target(gcs, aircraft)
        assert approx(
            target.azimuth_deg, 90.0
        ), f"Expected ~90° (East), got {target.azimuth_deg:.2f}°"

    def test_due_south(self) -> None:
        """Aircraft directly south of GCS → azimuth ≈ ±180°."""
        gcs = GeoPosition(lat_deg=30.0, lon_deg=-90.0, alt_m=0.0)
        aircraft = GeoPosition(lat_deg=29.9, lon_deg=-90.0, alt_m=50.0)
        target = compute_gimbal_target(gcs, aircraft)
        # Both ±180° are valid; check absolute value.
        assert approx(
            abs(target.azimuth_deg), 180.0, tol=1.0
        ), f"Expected ~±180° (South), got {target.azimuth_deg:.2f}°"

    def test_due_west(self) -> None:
        """Aircraft directly west of GCS → azimuth ≈ −90°."""
        gcs = GeoPosition(lat_deg=30.0, lon_deg=-90.0, alt_m=0.0)
        aircraft = GeoPosition(lat_deg=30.0, lon_deg=-90.1, alt_m=50.0)
        target = compute_gimbal_target(gcs, aircraft)
        assert approx(
            target.azimuth_deg, -90.0
        ), f"Expected ~−90° (West), got {target.azimuth_deg:.2f}°"

    def test_bearing_northeast(self) -> None:
        """Aircraft northeast → azimuth in (0°, 90°)."""
        gcs = GeoPosition(lat_deg=30.0, lon_deg=-90.0, alt_m=0.0)
        aircraft = GeoPosition(lat_deg=30.05, lon_deg=-89.95, alt_m=50.0)
        target = compute_gimbal_target(gcs, aircraft)
        assert (
            0.0 < target.azimuth_deg < 90.0
        ), f"Expected bearing in (0°, 90°), got {target.azimuth_deg:.2f}°"


# ---------------------------------------------------------------------------
# Elevation tests
# ---------------------------------------------------------------------------


class TestElevation:
    """Tests for elevation angle calculation."""

    def test_horizontal_same_altitude(self) -> None:
        """Aircraft at same altitude 1 km away → elevation ≈ 0°."""
        gcs = GeoPosition(lat_deg=30.0, lon_deg=-90.0, alt_m=50.0)
        aircraft = GeoPosition(lat_deg=30.009, lon_deg=-90.0, alt_m=50.0)
        target = compute_gimbal_target(gcs, aircraft)
        assert approx(
            target.elevation_deg, 0.0, tol=1.0
        ), f"Expected ~0° elevation, got {target.elevation_deg:.2f}°"

    def test_aircraft_above(self) -> None:
        """Aircraft at 100 m altitude, 100 m away → elevation ≈ 45°."""
        gcs = GeoPosition(lat_deg=30.0, lon_deg=-90.0, alt_m=0.0)
        # 0.0009° ≈ 100 m at lat 30°.
        aircraft = GeoPosition(lat_deg=30.0009, lon_deg=-90.0, alt_m=100.0)
        target = compute_gimbal_target(gcs, aircraft)
        assert (
            30.0 < target.elevation_deg < 60.0
        ), f"Expected elevation ~45°, got {target.elevation_deg:.2f}°"

    def test_aircraft_directly_overhead(self) -> None:
        """Aircraft at same lat/lon, above GCS → elevation ≈ 90°."""
        gcs = GeoPosition(lat_deg=30.0, lon_deg=-90.0, alt_m=0.0)
        aircraft = GeoPosition(lat_deg=30.0, lon_deg=-90.0, alt_m=200.0)
        target = compute_gimbal_target(gcs, aircraft)
        assert (
            target.elevation_deg >= 80.0
        ), f"Expected ~90° elevation overhead, got {target.elevation_deg:.2f}°"

    def test_elevation_positive_for_airborne(self) -> None:
        """Any aircraft above the GCS altitude should have positive elevation."""
        gcs = GeoPosition(lat_deg=30.0, lon_deg=-90.0, alt_m=10.0)
        aircraft = GeoPosition(lat_deg=30.01, lon_deg=-90.01, alt_m=120.0)
        target = compute_gimbal_target(gcs, aircraft)
        assert target.elevation_deg > 0.0, (
            "Airborne aircraft should have positive elevation, "
            f"got {target.elevation_deg:.2f}°"
        )


# ---------------------------------------------------------------------------
# Sanity / edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Edge cases and sanity checks."""

    def test_azimuth_range(self) -> None:
        """Azimuth must be in [−180, +180]."""
        positions = [
            (GeoPosition(30.0, -90.0, 50.0), GeoPosition(30.1, -89.9, 100.0)),
            (GeoPosition(30.0, -90.0, 50.0), GeoPosition(29.9, -90.1, 100.0)),
            (GeoPosition(30.0, -90.0, 50.0), GeoPosition(30.1, -90.1, 100.0)),
        ]
        for gcs, aircraft in positions:
            target = compute_gimbal_target(gcs, aircraft)
            assert (
                -180.0 <= target.azimuth_deg <= 180.0
            ), f"Azimuth {target.azimuth_deg:.2f}° out of range"

    def test_elevation_range(self) -> None:
        """Elevation must be in [−90, +90]."""
        positions = [
            (GeoPosition(30.0, -90.0, 0.0), GeoPosition(30.1, -90.0, 500.0)),
            (GeoPosition(30.0, -90.0, 100.0), GeoPosition(30.0, -90.0, 50.0)),
        ]
        for gcs, aircraft in positions:
            target = compute_gimbal_target(gcs, aircraft)
            assert (
                -90.0 <= target.elevation_deg <= 90.0
            ), f"Elevation {target.elevation_deg:.2f}° out of range"
