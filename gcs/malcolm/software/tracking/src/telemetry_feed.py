"""
telemetry_feed.py — Malcolm GCS MAVLink position consumer.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
Revision: Q1 (2026-06-10)

Connects to the mavlink-router MAVLink stream (UDP on localhost:14550, or
serial to PB2-I USB) and extracts GLOBAL_POSITION_INT messages.  Publishes
aircraft position as JSON UDP datagrams to tracker.py on MAL_TRACKER_UDP_PORT.

This module is the host-PC-side complement to mal_telemetry.c (which runs on
Malcolm's PB2-I).  Running both provides redundant position extraction: if the
PB2-I path fails, this host-side path continues to feed tracker.py.

Usage:
    python3 telemetry_feed.py [--config malcolm_config.yaml]
"""

from __future__ import annotations

import argparse
import json
import logging
import socket
import sys
import time
from pathlib import Path

import yaml
from pymavlink import mavutil  # type: ignore[import]


DEFAULT_CONFIG_PATH = (
    Path(__file__).parent.parent.parent / "config" / "malcolm_config.yaml"
)
MAVLINK_SYS_ID_AIRCRAFT = 1  # Must match MAL_AIRCRAFT_SYS_ID in mal_config.h

log = logging.getLogger(__name__)


def run(config: dict) -> None:
    """
    Connect to mavlink-router and forward GLOBAL_POSITION_INT to tracker.py.

    Args:
        config: Loaded malcolm_config.yaml content.
    """
    mav_cfg    = config.get("mavlink", {})
    listen_str = mav_cfg.get("source", "udpin:localhost:14550")
    tracker_port = int(config.get("tracker", {}).get("telemetry_port", 14560))

    # UDP socket for publishing to tracker.py.
    tx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    tracker_addr = ("127.0.0.1", tracker_port)

    log.info("Connecting to MAVLink source: %s", listen_str)
    mav = mavutil.mavlink_connection(listen_str, source_system=255)

    log.info(
        "Waiting for heartbeat from aircraft (sysid=%d)...",
        MAVLINK_SYS_ID_AIRCRAFT,
    )
    mav.wait_heartbeat(blocking=True, timeout=30)
    log.info("Heartbeat received — starting position feed to UDP :%d", tracker_port)

    while True:
        msg = mav.recv_match(
            type="GLOBAL_POSITION_INT",
            blocking=True,
            timeout=5.0,
        )

        if msg is None:
            log.warning(
                "No GLOBAL_POSITION_INT received within 5 s"
                " — link may be degraded"
            )
            continue

        # Ignore messages from non-aircraft systems.
        if msg.get_srcSystem() != MAVLINK_SYS_ID_AIRCRAFT:
            continue

        payload = {
            "lat_degE7":   msg.lat,
            "lon_degE7":   msg.lon,
            "alt_mm":      msg.alt,
            "vx_cms":      msg.vx,
            "vy_cms":      msg.vy,
            "hdg_cdeg":    msg.hdg,
            "timestamp_s": time.time(),
        }
        data = json.dumps(payload).encode("utf-8")
        tx_sock.sendto(data, tracker_addr)
        log.debug(
            "Position: lat=%.6f lon=%.6f alt=%.1f m",
            msg.lat / 1e7, msg.lon / 1e7, msg.alt / 1000.0,
        )


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Malcolm GCS MAVLink telemetry feed")
    parser.add_argument(
        "--config", "-c",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to malcolm_config.yaml (default: %(default)s)",
    )
    parser.add_argument(
        "--log-level", "-l",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
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

    try:
        run(config)
    except KeyboardInterrupt:
        log.info("telemetry_feed stopped by operator.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
