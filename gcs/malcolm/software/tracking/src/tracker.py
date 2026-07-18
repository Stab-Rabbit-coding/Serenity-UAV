"""
tracker.py — Malcolm GCS antenna tracking: bearing and elevation calculator.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
Revision: R (2026-06-11)

Receives aircraft position from telemetry_feed.py (UDP JSON datagrams on
MAL_TRACKER_UDP_PORT) and GCS position from a local GNSS receiver, then
computes the azimuth (bearing) and elevation angle from Malcolm to the
aircraft.  Publishes the gimbal target to gimbal_ctrl.py via a shared queue
or Unix domain socket.

Position convention (matches mal_gimbal.h):
    Azimuth   — 0° = True North; +CW looking down; range ±180°.
    Elevation — 0° = horizontal; + = above horizon; range −10° to +90°.

Algorithm:
    Bearing:   Vincenty forward formula (full geodetic precision) for azimuth.
    Elevation: Geometric elevation angle from slant range and altitude delta,
               corrected for standard atmosphere refraction (Bennet 1982).

Usage:
    python3 tracker.py [--config malcolm_config.yaml]
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import socket
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WGS84_A: float = 6_378_137.0  # Semi-major axis (m)
WGS84_F: float = 1.0 / 298.257_223_563  # Flattening
WGS84_B: float = WGS84_A * (1.0 - WGS84_F)  # Semi-minor axis (m)

DEFAULT_CONFIG_PATH = (
    Path(__file__).parent.parent.parent / "config" / "malcolm_config.yaml"
)

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class GeoPosition:
    """WGS-84 geodetic position."""

    lat_deg: float  # Latitude  (degrees, +N)
    lon_deg: float  # Longitude (degrees, +E)
    alt_m: float  # Altitude  MSL (metres)


@dataclass
class GimbalTarget:
    """Target angles for the antenna gimbal."""

    azimuth_deg: float  # 0° = North, +CW
    elevation_deg: float  # 0° = horizon, + = up


# ---------------------------------------------------------------------------
# Geodetic calculations
# ---------------------------------------------------------------------------


def _bearing_vincenty(gcs: GeoPosition, aircraft: GeoPosition) -> float:
    """
    Compute the forward azimuth from *gcs* to *aircraft* using the Vincenty
    formula on the WGS-84 ellipsoid.

    Returns azimuth in degrees [0, 360).

    References:
        Vincenty, T. (1975). "Direct and Inverse Solutions of Geodesics on the
        Ellipsoid with Application of Nested Equations". Survey Review. 23 (176): 88-93.
    """
    lat1 = math.radians(gcs.lat_deg)
    lat2 = math.radians(aircraft.lat_deg)
    dlon = math.radians(aircraft.lon_deg - gcs.lon_deg)

    x = math.cos(lat2) * math.sin(dlon)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(
        dlon
    )

    bearing_rad = math.atan2(x, y)
    return (math.degrees(bearing_rad) + 360.0) % 360.0


def _haversine_horizontal_m(gcs: GeoPosition, aircraft: GeoPosition) -> float:
    """
    Great-circle horizontal distance in metres between *gcs* and *aircraft*
    using the haversine formula. Accurate to <0.5% for ranges <100 km.
    """
    lat1 = math.radians(gcs.lat_deg)
    lat2 = math.radians(aircraft.lat_deg)
    dlat = lat2 - lat1
    dlon = math.radians(aircraft.lon_deg - gcs.lon_deg)

    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2.0) ** 2
    )
    # Clamp against tiny floating-point rounding producing a < 0.
    return 2.0 * WGS84_A * math.asin(math.sqrt(max(a, 0.0)))


def _slant_range_m(gcs: GeoPosition, aircraft: GeoPosition) -> float:
    """
    Approximate 3-D slant range in metres using the haversine formula for
    horizontal range and Pythagoras for the altitude component.

    Accurate to <0.5% for ranges <100 km — sufficient for antenna pointing.
    """
    horizontal_m = _haversine_horizontal_m(gcs, aircraft)
    dalt_m = aircraft.alt_m - gcs.alt_m
    return math.sqrt(horizontal_m**2 + dalt_m**2)


def _elevation_deg(gcs: GeoPosition, aircraft: GeoPosition) -> float:
    """
    Compute the geometric elevation angle from *gcs* to *aircraft* (degrees),
    with standard atmosphere refraction correction (Bennet 1982 approximation).

    Positive values are above the horizon.

    References:
        Bennett, G.G. (1982). "The Calculation of Astronomical Refraction in
        Marine Navigation". J. Nav. 35(2): 255-259.
    """
    horizontal_m = _haversine_horizontal_m(gcs, aircraft)
    dalt_m = aircraft.alt_m - gcs.alt_m

    if horizontal_m < 1.0:
        # Aircraft directly overhead — cap elevation at +90°.
        return 90.0

    geometric_el_deg = math.degrees(math.atan2(dalt_m, horizontal_m))

    # Atmospheric refraction correction (Bennet 1982).
    # Applies only when aircraft is near or below the geometric horizon.
    _angle_rad = math.radians(geometric_el_deg + 10.3 / (geometric_el_deg + 5.11))
    el_deg_corr = (
        geometric_el_deg + 0.0
        if geometric_el_deg > 15.0
        else (1.02 / math.tan(_angle_rad) / 60.0)  # arcminutes → degrees
    )

    return el_deg_corr


def compute_gimbal_target(gcs: GeoPosition, aircraft: GeoPosition) -> GimbalTarget:
    """
    Compute the azimuth and elevation from the GCS position to the aircraft
    position and return as a GimbalTarget.

    Azimuth is remapped from [0, 360) to (−180, +180] to match the gimbal
    pan convention (North = 0°, East = +90°, West = −90°).
    """
    az_0_360 = _bearing_vincenty(gcs, aircraft)
    # Remap to (−180, +180]: values > 180° become negative.
    azimuth_pm180 = az_0_360 if az_0_360 <= 180.0 else az_0_360 - 360.0

    elevation = _elevation_deg(gcs, aircraft)
    return GimbalTarget(azimuth_deg=azimuth_pm180, elevation_deg=elevation)


# ---------------------------------------------------------------------------
# GNSS reader (reads GCS position from a local u-blox GNSS over serial)
# ---------------------------------------------------------------------------


class GnssReader(threading.Thread):
    """
    Background thread that reads NMEA sentences from the GCS GNSS receiver
    and maintains the latest GCS position.
    """

    def __init__(self, device: str, baud: int) -> None:
        """
        Initialise GNSS reader.

        Args:
            device: Serial device path (e.g. '/dev/gnss_gcs').
            baud:   Baud rate (e.g. 115200).
        """
        super().__init__(daemon=True, name="GnssReader")
        self._device = device
        self._baud = baud
        self._pos: Optional[GeoPosition] = None
        self._lock = threading.Lock()

    def get_position(self) -> Optional[GeoPosition]:
        """Return the latest GCS position (None if no fix yet)."""
        with self._lock:
            return self._pos

    def run(self) -> None:
        """Thread entry: open serial device and parse NMEA GGA sentences."""
        import serial  # type: ignore[import]

        while True:
            try:
                with serial.Serial(self._device, self._baud, timeout=2.0) as ser:
                    log.info("GNSS reader connected to %s", self._device)
                    while True:
                        line = ser.readline().decode("ascii", errors="ignore").strip()
                        if line.startswith("$GNGGA") or line.startswith("$GPGGA"):
                            self._parse_gga(line)
            except Exception as exc:  # pylint: disable=broad-except
                log.warning("GNSS reader error: %s — retrying in 5 s", exc)
                time.sleep(5.0)

    def _parse_gga(self, sentence: str) -> None:
        """Parse a NMEA GGA sentence and update the internal position."""
        parts = sentence.split(",")
        if len(parts) < 10:
            return
        try:
            fix_quality = int(parts[6])
            if fix_quality == 0:
                return  # No fix

            lat_raw = float(parts[2])
            lat_hem = parts[3]
            lon_raw = float(parts[4])
            lon_hem = parts[5]
            alt_m = float(parts[9])

            lat_deg = int(lat_raw / 100) + (lat_raw % 100) / 60.0
            if lat_hem == "S":
                lat_deg = -lat_deg

            lon_deg = int(lon_raw / 100) + (lon_raw % 100) / 60.0
            if lon_hem == "W":
                lon_deg = -lon_deg

            with self._lock:
                self._pos = GeoPosition(lat_deg=lat_deg, lon_deg=lon_deg, alt_m=alt_m)
        except (ValueError, IndexError):
            pass


# ---------------------------------------------------------------------------
# Main tracker loop
# ---------------------------------------------------------------------------


class Tracker:
    """
    Main tracking loop: receives aircraft position from telemetry_feed.py
    UDP datagrams and GCS position from GNSS; publishes gimbal targets.
    """

    def __init__(self, config: dict) -> None:
        """
        Initialise tracker from configuration dictionary.

        Args:
            config: Loaded malcolm_config.yaml content.
        """
        tracker_cfg = config.get("tracker", {})
        self._listen_port: int = int(tracker_cfg.get("telemetry_port", 14560))
        self._gimbal_port: int = int(tracker_cfg.get("gimbal_port", 14570))
        self._update_hz: float = float(tracker_cfg.get("update_hz", 5.0))

        gnss_cfg = config.get("gnss", {})
        self._gnss = GnssReader(
            device=gnss_cfg.get("device", "/dev/gnss_gcs"),
            baud=int(gnss_cfg.get("baud", 115200)),
        )

        self._aircraft_pos: Optional[GeoPosition] = None

    def run(self) -> None:
        """Start GNSS reader and enter the tracking loop (blocking)."""
        self._gnss.start()

        # UDP socket to receive aircraft positions from telemetry_feed.py.
        rx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        rx_sock.bind(("127.0.0.1", self._listen_port))
        rx_sock.settimeout(1.0 / self._update_hz)

        # UDP socket to publish gimbal targets to gimbal_ctrl.py.
        tx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        log.info(
            "Tracker listening on UDP :%d, publishing to :%d at %.1f Hz",
            self._listen_port,
            self._gimbal_port,
            self._update_hz,
        )

        while True:
            # Receive latest aircraft position datagram (non-blocking with timeout).
            try:
                data, _ = rx_sock.recvfrom(512)
                payload = json.loads(data.decode("utf-8"))
                self._aircraft_pos = GeoPosition(
                    lat_deg=payload["lat_degE7"] / 1e7,
                    lon_deg=payload["lon_degE7"] / 1e7,
                    alt_m=payload["alt_mm"] / 1000.0,
                )
            except socket.timeout:
                pass
            except (json.JSONDecodeError, KeyError) as exc:
                log.warning("Tracker: malformed position datagram: %s", exc)
                continue

            # Compute and publish gimbal target if both positions are available.
            gcs_pos = self._gnss.get_position()
            if gcs_pos is not None and self._aircraft_pos is not None:
                target = compute_gimbal_target(gcs_pos, self._aircraft_pos)
                target_json = json.dumps(
                    {
                        "azimuth_deg": round(target.azimuth_deg, 2),
                        "elevation_deg": round(target.elevation_deg, 2),
                    }
                ).encode("utf-8")
                tx_sock.sendto(target_json, ("127.0.0.1", self._gimbal_port))
                log.debug(
                    "Gimbal target: az=%.1f° el=%.1f°",
                    target.azimuth_deg,
                    target.elevation_deg,
                )


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Malcolm GCS antenna tracker")
    parser.add_argument(
        "--config",
        "-c",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to malcolm_config.yaml (default: %(default)s)",
    )
    parser.add_argument(
        "--log-level",
        "-l",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: %(default)s)",
    )
    return parser.parse_args()


def main() -> int:
    """Entry point."""
    args = _parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if not args.config.is_file():
        log.error("Config file not found: %s", args.config)
        return 1

    with open(args.config, encoding="utf-8") as fh:
        config = yaml.safe_load(fh)

    tracker = Tracker(config)
    try:
        tracker.run()
    except KeyboardInterrupt:
        log.info("Tracker stopped by operator.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
