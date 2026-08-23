"""
gimbal_ctrl.py — Skipper GCS gimbal controller: sends servo commands to PB2-I.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
Revision: R (2026-06-11)

Receives gimbal target JSON from tracker.py (UDP on gimbal_port) and
forwards the target to Skipper's PB2-I firmware via a serial or UDP
command interface.  Also enforces travel limits and rate limiting at
the software level as a second safety check before commands reach
the firmware (which enforces the same limits in skipper_gimbal.c).

Command interface to PB2-I:
    JSON over UDP to PB2-I usb0 interface (192.168.7.2:14571) or
    alternatively over the USB CDC serial /dev/ttyACM0 at 115200 Bd.

    Command format:
        {"cmd": "GIMBAL_TARGET", "az": <float>, "el": <float>}

    Response (async status):
        {"status": "GIMBAL_ON_TARGET"} or {"status": "GIMBAL_SLEWING"}

Usage:
    python3 gimbal_ctrl.py [--config skipper_config.yaml]
"""

from __future__ import annotations

import argparse
import json
import logging
import socket
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

DEFAULT_CONFIG_PATH = (
    Path(__file__).parent.parent.parent / "config" / "skipper_config.yaml"
)

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Travel limits (mirrors skipper_config.h — change both if limits change)
# ---------------------------------------------------------------------------

GIMBAL_PAN_MAX_DEG: float = 170.0  # |pan|  must not exceed this
GIMBAL_TILT_UP_DEG: float = 90.0  # +elevation hard limit
GIMBAL_TILT_DOWN_DEG: float = 10.0  # magnitude of negative elevation hard limit
GIMBAL_MAX_SLEW_DPS: float = 90.0  # Maximum slew rate (degrees per second)

# Rate-limit period for software-layer slew clamping (seconds)
CTRL_PERIOD_S: float = 0.1  # 10 Hz control rate


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------


@dataclass
class GimbalState:
    """Current software-layer gimbal state (may lag firmware reality)."""

    pan_deg: float = 0.0
    tilt_deg: float = 0.0
    timestamp: float = 0.0  # time.monotonic() of last command


def _clamp(value: float, lo: float, hi: float) -> float:
    """Clamp *value* to the interval [*lo*, *hi*]."""
    return max(lo, min(hi, value))


def _rate_limit(current: float, target: float, max_rate: float, dt: float) -> float:
    """
    Return a new position step-limited to *max_rate* × *dt* from *current*.

    Args:
        current:  Current position (degrees).
        target:   Desired position (degrees).
        max_rate: Maximum slew rate (degrees/second).
        dt:       Time elapsed since last call (seconds).

    Returns:
        New position no further from *current* than max_rate * dt.
    """
    max_step = max_rate * dt
    delta = target - current
    if abs(delta) <= max_step:
        return target
    return current + max_step * (1.0 if delta > 0.0 else -1.0)


# ---------------------------------------------------------------------------
# Gimbal controller class
# ---------------------------------------------------------------------------


class GimbalController:
    """
    Reads gimbal target datagrams from tracker.py and sends commands to
    Skipper's PB2-I via UDP.
    """

    def __init__(self, config: dict) -> None:
        """
        Initialise from configuration.

        Args:
            config: Loaded skipper_config.yaml content.
        """
        gimbal_cfg = config.get("gimbal_ctrl", {})
        self._listen_port: int = int(gimbal_cfg.get("gimbal_port", 14570))
        self._pb2i_host: str = gimbal_cfg.get("pb2i_host", "192.168.7.2")
        self._pb2i_port: int = int(gimbal_cfg.get("pb2i_cmd_port", 14571))
        self._state = GimbalState(timestamp=time.monotonic())

    def run(self) -> None:
        """Enter the gimbal control loop (blocking)."""
        rx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        rx_sock.bind(("127.0.0.1", self._listen_port))
        rx_sock.settimeout(CTRL_PERIOD_S)

        tx_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        log.info(
            "GimbalCtrl listening on UDP :%d, forwarding to %s:%d",
            self._listen_port,
            self._pb2i_host,
            self._pb2i_port,
        )

        while True:
            now = time.monotonic()
            dt = now - self._state.timestamp
            self._state.timestamp = now

            # Receive latest target from tracker.py (non-blocking with timeout).
            target_pan: Optional[float] = None
            target_tilt: Optional[float] = None

            try:
                data, _ = rx_sock.recvfrom(256)
                payload = json.loads(data.decode("utf-8"))
                target_pan = float(payload["azimuth_deg"])
                target_tilt = float(payload["elevation_deg"])
            except socket.timeout:
                pass
            except (json.JSONDecodeError, KeyError, ValueError) as exc:
                log.warning("GimbalCtrl: malformed target datagram: %s", exc)
                continue

            if target_pan is None or target_tilt is None:
                continue

            # Apply travel limit clamps (software safety layer).
            target_pan = _clamp(target_pan, -GIMBAL_PAN_MAX_DEG, GIMBAL_PAN_MAX_DEG)
            target_tilt = _clamp(target_tilt, -GIMBAL_TILT_DOWN_DEG, GIMBAL_TILT_UP_DEG)

            # Apply software rate limiting (firmware enforces the same in skipper_gimbal.c).
            new_pan = _rate_limit(
                self._state.pan_deg,
                target_pan,
                GIMBAL_MAX_SLEW_DPS,
                dt,
            )
            new_tilt = _rate_limit(
                self._state.tilt_deg,
                target_tilt,
                GIMBAL_MAX_SLEW_DPS,
                dt,
            )

            # Only send command if the position has changed meaningfully (>0.2°).
            if (
                abs(new_pan - self._state.pan_deg) > 0.2
                or abs(new_tilt - self._state.tilt_deg) > 0.2
            ):
                self._state.pan_deg = new_pan
                self._state.tilt_deg = new_tilt
                self._send_command(tx_sock, new_pan, new_tilt)

    def _send_command(
        self, sock: socket.socket, pan_deg: float, tilt_deg: float
    ) -> None:
        """Send a GIMBAL_TARGET command to Skipper's PB2-I."""
        cmd = json.dumps(
            {
                "cmd": "GIMBAL_TARGET",
                "az": round(pan_deg, 2),
                "el": round(tilt_deg, 2),
            }
        ).encode("utf-8")
        try:
            sock.sendto(cmd, (self._pb2i_host, self._pb2i_port))
            log.debug("GIMBAL_TARGET az=%.1f° el=%.1f°", pan_deg, tilt_deg)
        except OSError as exc:
            log.warning("GimbalCtrl: send failed: %s", exc)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Skipper GCS gimbal controller")
    parser.add_argument(
        "--config",
        "-c",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to skipper_config.yaml (default: %(default)s)",
    )
    parser.add_argument(
        "--log-level",
        "-l",
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

    ctrl = GimbalController(config)
    try:
        ctrl.run()
    except KeyboardInterrupt:
        log.info("GimbalCtrl stopped by operator.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
