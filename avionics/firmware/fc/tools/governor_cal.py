#!/usr/bin/env python3
"""
governor_cal.py — EDF thrust-stand calibration tool for Serenity UAV.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0 — creativecommons.org/licenses/by/4.0

Purpose
-------
Perform a swept-throttle calibration run on a single EDF installed in a
thrust stand, fit the aerodynamic thrust model

    T [N]  =  k  ×  RPM²

to the measured (RPM, thrust) data, and write the calibrated k coefficient
back into avionics/firmware/fc/src/governor_config.h.

Hardware requirements
---------------------
- Target EDF mounted in a thrust stand with an axial load cell.
- ESC wired to the EDF, powered from the correct cell-count LiPo
  (4S for 50 mm nacelle EDFs, 6S for the 120 mm fuselage EDF).
- PocketBeagle 2 Industrial running serenity-fc in calibration mode:

      serenity-fc --cal <edf_id>

  This mode activates BDSHOT600 telemetry logging on the EDF's ESC and
  reads the HX711 load-cell amplifier over SPI, exposing both data streams
  over USB serial (115200 8N1, see Protocol section below).

- USB serial cable from host machine to PocketBeagle 2 USB-OTG / UART port.

Serial protocol  (serenity-fc calibration mode)
------------------------------------------------
All messages are ASCII, terminated with a single LF character ('\\n').
No carriage return.  Baud rate: 115200 8N1.

Commands (host → FC):
    VER\\n            Query identity.
    THR <pct>\\n      Set throttle to <pct> percent (float, 0.0–100.0).
    SAM <n>\\n        Request <n> raw samples (int, 1–500).
    SAFE\\n           Emergency throttle-off; always acknowledged.

Responses (FC → host):
    VER SERENITY-FC-CAL 1 <edf_id>\\n   Identity confirmation.
    ACK\\n                               Command accepted.
    SAM <rpm> <hx711_raw> <esc_temp_c>\\n   One raw sample line.
                                         Emitted <n> times, then ACK\\n.
    ERR <code> <text>\\n                 Error; codes:
        1  NOT_ARMED
        2  THROTTLE_OUT_OF_RANGE
        3  ESC_FAULT
        4  BAD_COMMAND

Field types:
    <pct>          float, one decimal place  (e.g. "75.0")
    <rpm>          unsigned 32-bit int  (rev/min)
    <hx711_raw>    signed 32-bit int    (raw 24-bit ADC counts from HX711)
    <esc_temp_c>   unsigned int         (degrees Celsius, BDSHOT600 telemetry)
    <edf_id>       0–4, matches EDF_ID_* constants in governor_config.h

HX711 scale-factor determination
----------------------------------
Before the calibration sweep, determine the load-cell scale factor
(counts per gram):

    1. With the EDF OFF and the thrust stand empty, tare the scale:
           python3 governor_cal.py --tare-only -p /dev/ttyUSB0
       Record the tare count.

    2. Place a known mass (e.g., 200 g calibration weight) on the platform
       and run:
           python3 governor_cal.py --weigh-only -p /dev/ttyUSB0 \\
               --tare-count <tare_count>
       The script prints <hx711_raw_with_weight> - <tare_count>.

    3. Compute scale:
           scale = (raw_with_weight - tare_count) / known_mass_g

    Pass this value as --hx711-scale in subsequent calibration runs.

Calibration sweep
-----------------
The sweep ascends from 0 % to 100 % throttle in --steps equal steps, dwells
--dwell seconds at each step, collects --samples raw readings, averages them,
then descends back to 0 % in the same fashion.  Ascent and descent data are
pooled before fitting.  Points with RPM < EDF_RPM_IDLE (EDF spinning up or
not fully settled) are excluded from the fit.

Thrust-model fit
----------------
scipy.optimize.curve_fit solves for k in T = k × RPM² using a Levenberg–
Marquardt non-linear least-squares algorithm.  The script reports R², the
RMS residual in Newtons, and the one-sigma standard error on k.

References
----------
[1] FlightLine / Freewing 50 mm EDF product data sheet, 2023.
[2] Freewing 120 mm 4400 kV 6S EDF product data sheet, 2023.
[3] More, J. J., "The Levenberg–Marquardt Algorithm: Implementation and
    Theory," in Numerical Analysis, Lecture Notes in Mathematics, vol. 630,
    Springer, 1978, pp. 105–116.
[4] HX711 24-Bit Analog-to-Digital Converter datasheet, AVIA Semiconductor.

Dependencies (pip install):
    pyserial >= 3.5
    numpy    >= 1.21
    scipy    >= 1.7

Example
-------
    # Calibrate the port-nacelle forward EDF (ID 0) on /dev/ttyUSB0:
    python3 governor_cal.py \\
        --port /dev/ttyUSB0 \\
        --edf-id 0 \\
        --hx711-scale 412.3 \\
        --steps 20 \\
        --dwell 3.0 \\
        --samples 60 \\
        --csv port_fwd_cal.csv \\
        --output ../src/governor_config.h
"""

import argparse
import csv
import datetime
import logging
import os
import re
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

try:
    import numpy as np
    from scipy.optimize import curve_fit
except ImportError as _exc:
    print(
        f"Missing dependency: {_exc}\n"
        "Install with:  pip install numpy scipy",
        file=sys.stderr,
    )
    sys.exit(1)

try:
    import serial
except ImportError:
    print(
        "Missing dependency: pyserial\n"
        "Install with:  pip install pyserial",
        file=sys.stderr,
    )
    sys.exit(1)

# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

#: EDF display names indexed by EDF_ID_* constant.
EDF_NAMES: dict = {
    0: "PORT_FWD",
    1: "PORT_AFT",
    2: "STBD_FWD",
    3: "STBD_AFT",
    4: "FUSE",
}

#: Total EDF count — must match EDF_COUNT in governor_config.h.
EDF_COUNT: int = 5

#: Minimum idle RPM below which sweep points are excluded from the fit
#: (EDF still spinning up or coasting).  50 mm and 120 mm share this floor
#: for conservatism; individual limits from governor_config.h apply in flight.
EDF_RPM_FLOOR_FOR_FIT: int = 5000

#: Default serial baud rate for calibration mode.
CAL_BAUD_DEFAULT: int = 115200

#: Serial read timeout when waiting for a response line (seconds).
CAL_READ_TIMEOUT_S: float = 5.0

#: Number of response retries before declaring a communication error.
CAL_MAX_RETRIES: int = 3

#: Gravitational acceleration used to convert gram-force to Newtons.
G_MPS2: float = 9.80665

#: Header constant name stem; the full macro is EDF_THRUST_K_<NAME>.
#: governor_cal.py uses the inline ``/* CAL:<NAME> */`` tag to locate each
#: line — see governor_config.h.
_CAL_TAG_PREFIX: str = "CAL:"

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class RawSample:
    """
    One raw telemetry sample returned by the FC node in calibration mode.

    :param rpm:        Motor speed reported by BDSHOT600 telemetry (rev/min).
    :param hx711_raw:  Signed 24-bit ADC count from the HX711 load cell.
    :param esc_temp_c: ESC temperature in degrees Celsius (BDSHOT600 field).
    """

    rpm: int
    hx711_raw: int
    esc_temp_c: int


@dataclass
class SweepPoint:
    """
    Averaged measurement at one throttle step.

    :param throttle_pct: Commanded throttle (percent, 0–100).
    :param rpm_mean:     Mean RPM across collected samples.
    :param rpm_std:      Standard deviation of RPM samples.
    :param thrust_n:     Mean thrust in Newtons.
    :param thrust_std:   Standard deviation of thrust in Newtons.
    :param esc_temp_c:   Mean ESC temperature (°C).
    :param n_samples:    Number of raw samples averaged.
    """

    throttle_pct: float
    rpm_mean: float
    rpm_std: float
    thrust_n: float
    thrust_std: float
    esc_temp_c: float
    n_samples: int


@dataclass
class CalibrationResult:
    """
    Fitted thrust model  T = k × RPM²  for one EDF.

    :param edf_id:          EDF index (0–4).
    :param edf_name:        Human-readable EDF label (e.g. "PORT_FWD").
    :param k:               Fitted thrust coefficient (N / RPM²).
    :param k_stderr:        One-sigma standard error on k.
    :param r_squared:       Coefficient of determination for the fit.
    :param rms_residual_n:  RMS fit residual in Newtons.
    :param n_points:        Number of sweep points used in the fit.
    :param calibrated_at:   ISO 8601 timestamp of the calibration run.
    """

    edf_id: int
    edf_name: str
    k: float
    k_stderr: float
    r_squared: float
    rms_residual_n: float
    n_points: int
    calibrated_at: str = field(
        default_factory=lambda: datetime.datetime.utcnow().isoformat(
            timespec="seconds"
        )
        + "Z"
    )

# ---------------------------------------------------------------------------
# Serial helpers
# ---------------------------------------------------------------------------

log = logging.getLogger(__name__)


def open_serial(port: str, baud: int) -> serial.Serial:
    """
    Open the serial port to the PocketBeagle 2 in calibration mode.

    :param port: Device path, e.g. "/dev/ttyUSB0".
    :param baud: Baud rate (typically 115200).
    :returns: Opened serial.Serial object.
    :raises SystemExit: On port-open failure.
    """
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baud,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=CAL_READ_TIMEOUT_S,
            write_timeout=2.0,
            xonxoff=False,
            rtscts=False,
        )
        log.debug("Opened serial port %s at %d baud.", port, baud)
        return ser
    except serial.SerialException as exc:
        log.error("Cannot open serial port %s: %s", port, exc)
        sys.exit(1)


def send_cmd(ser: serial.Serial, cmd: str) -> None:
    """
    Send an ASCII command terminated with LF.

    :param ser: Open serial port.
    :param cmd: Command string without trailing newline.
    """
    raw = (cmd + "\n").encode("ascii")
    log.debug("→ %r", raw)
    ser.write(raw)


def read_line(ser: serial.Serial) -> Optional[str]:
    """
    Read one LF-terminated ASCII line from the serial port.

    :param ser: Open serial port.
    :returns: Stripped line string, or None on timeout.
    """
    try:
        line = ser.readline()
        if not line:
            return None
        decoded = line.decode("ascii", errors="replace").strip()
        log.debug("← %r", decoded)
        return decoded
    except serial.SerialException as exc:
        log.error("Serial read error: %s", exc)
        return None


def verify_cal_mode(ser: serial.Serial, expected_edf_id: int) -> None:
    """
    Send ``VER`` and confirm the FC node is in calibration mode for the
    expected EDF.

    :param ser:             Open serial port.
    :param expected_edf_id: EDF index expected in the VER response.
    :raises RuntimeError:   If not in cal mode or wrong EDF reported.
    """
    send_cmd(ser, "VER")
    line = read_line(ser)
    if line is None:
        raise RuntimeError(
            "No response to VER command.  Is serenity-fc running in "
            "--cal mode on the target?"
        )
    # Expected: "VER SERENITY-FC-CAL 1 <edf_id>"
    parts = line.split()
    if len(parts) < 4 or parts[0] != "VER" or parts[1] != "SERENITY-FC-CAL":
        raise RuntimeError(
            f"Unexpected VER response: {line!r}.  "
            "Ensure serenity-fc --cal <edf_id> is running."
        )
    try:
        reported_id = int(parts[3])
    except ValueError as exc:
        raise RuntimeError(f"Non-integer EDF ID in VER response: {line!r}") from exc

    if reported_id != expected_edf_id:
        raise RuntimeError(
            f"FC node reports EDF {reported_id} "
            f"({EDF_NAMES.get(reported_id, '?')}), "
            f"but --edf-id {expected_edf_id} "
            f"({EDF_NAMES.get(expected_edf_id, '?')}) was requested.  "
            "Restart serenity-fc with the correct EDF ID."
        )
    log.info(
        "FC node confirmed: calibration mode, EDF %d (%s).",
        reported_id,
        EDF_NAMES.get(reported_id, "?"),
    )


def cmd_safe(ser: serial.Serial) -> None:
    """
    Send SAFE command to force throttle to zero.

    Attempts CAL_MAX_RETRIES times.  Always logs the outcome; never raises
    so that cleanup paths remain robust.
    """
    for attempt in range(CAL_MAX_RETRIES):
        send_cmd(ser, "SAFE")
        line = read_line(ser)
        if line == "ACK":
            log.debug("SAFE acknowledged.")
            return
        log.warning(
            "SAFE attempt %d/%d: unexpected response %r.",
            attempt + 1,
            CAL_MAX_RETRIES,
            line,
        )
    log.error("SAFE command failed after %d attempts!", CAL_MAX_RETRIES)


def cmd_throttle(ser: serial.Serial, pct: float) -> None:
    """
    Set the EDF throttle.

    :param ser: Open serial port.
    :param pct: Throttle percentage in [0.0, 100.0].
    :raises ValueError:    If pct is out of range.
    :raises RuntimeError:  If the FC node returns an error or no ACK.
    """
    if not (0.0 <= pct <= 100.0):
        raise ValueError(f"Throttle {pct} out of range [0.0, 100.0].")

    for attempt in range(CAL_MAX_RETRIES):
        send_cmd(ser, f"THR {pct:.1f}")
        line = read_line(ser)
        if line == "ACK":
            log.debug("Throttle %.1f%% acknowledged.", pct)
            return
        if line is not None and line.startswith("ERR"):
            raise RuntimeError(f"FC error on THR {pct:.1f}: {line}")
        log.warning(
            "THR attempt %d/%d: unexpected response %r.",
            attempt + 1,
            CAL_MAX_RETRIES,
            line,
        )
    raise RuntimeError(
        f"No ACK for THR {pct:.1f} after {CAL_MAX_RETRIES} attempts."
    )


def collect_samples(
    ser: serial.Serial,
    n_samples: int,
    hx711_scale: float,
    hx711_offset: int,
) -> List[RawSample]:
    """
    Request ``n_samples`` raw telemetry samples from the FC node.

    The FC node emits exactly ``n_samples`` ``SAM`` lines, then ``ACK``.
    Each line has the form::

        SAM <rpm> <hx711_raw> <esc_temp_c>

    The HX711 raw counts are not converted here; conversion to Newtons is
    performed in :func:`_average_samples` after all samples are collected.

    :param ser:           Open serial port.
    :param n_samples:     How many samples to request (1–500).
    :param hx711_scale:   HX711 counts-per-gram scale factor (unused here,
                          passed through for documentation clarity).
    :param hx711_offset:  HX711 zero-offset counts from the tare procedure.
    :returns: List of RawSample objects.
    :raises RuntimeError: On protocol or parse error.
    """
    if not (1 <= n_samples <= 500):
        raise ValueError(f"n_samples {n_samples} outside valid range [1, 500].")

    send_cmd(ser, f"SAM {n_samples}")

    samples: List[RawSample] = []
    for idx in range(n_samples):
        line = read_line(ser)
        if line is None:
            raise RuntimeError(
                f"Timeout waiting for SAM line {idx + 1}/{n_samples}."
            )
        if line.startswith("ERR"):
            raise RuntimeError(f"FC error during SAM collection: {line}")
        parts = line.split()
        if len(parts) != 4 or parts[0] != "SAM":
            raise RuntimeError(f"Malformed SAM line: {line!r}")
        try:
            rpm = int(parts[1])
            hx711_raw = int(parts[2])
            esc_temp_c = int(parts[3])
        except ValueError as exc:
            raise RuntimeError(
                f"Non-integer field in SAM line: {line!r}"
            ) from exc
        samples.append(RawSample(rpm=rpm, hx711_raw=hx711_raw, esc_temp_c=esc_temp_c))

    # Consume trailing ACK.
    ack = read_line(ser)
    if ack != "ACK":
        raise RuntimeError(f"Expected ACK after SAM block, got: {ack!r}")

    return samples


def _average_samples(
    samples: List[RawSample],
    hx711_scale: float,
    hx711_offset: int,
) -> Tuple[float, float, float, float, float]:
    """
    Average a block of raw samples into a single (rpm_mean, rpm_std,
    thrust_n, thrust_std, esc_temp_c) tuple.

    Thrust conversion:

        thrust_g  =  (hx711_raw  −  hx711_offset)  /  hx711_scale
        thrust_N  =  thrust_g  ×  9.80665  /  1000.0

    :param samples:       List of RawSample from :func:`collect_samples`.
    :param hx711_scale:   HX711 counts per gram (from scale calibration).
    :param hx711_offset:  Tare offset (counts at zero thrust).
    :returns: (rpm_mean, rpm_std, thrust_n, thrust_std, esc_temp_mean).
    :raises ValueError: If the sample list is empty.
    """
    if not samples:
        raise ValueError("Cannot average an empty sample list.")

    rpms = np.array([s.rpm for s in samples], dtype=np.float64)
    raws = np.array([s.hx711_raw for s in samples], dtype=np.float64)
    temps = np.array([s.esc_temp_c for s in samples], dtype=np.float64)

    # Convert HX711 ADC counts to Newtons.
    thrust_g = (raws - hx711_offset) / hx711_scale
    thrust_n = thrust_g * G_MPS2 / 1000.0

    return (
        float(np.mean(rpms)),
        float(np.std(rpms)),
        float(np.mean(thrust_n)),
        float(np.std(thrust_n)),
        float(np.mean(temps)),
    )

# ---------------------------------------------------------------------------
# Sweep logic
# ---------------------------------------------------------------------------


def arm_esc(ser: serial.Serial) -> None:
    """
    Send the ESC arm sequence: throttle minimum (0 %) followed by a brief
    pause.  Typical ESC arm: send 0 % for at least 1–2 seconds.

    The BDSHOT600 protocol requires the ESC to see a valid zero-throttle
    signal at power-up before it will respond to higher throttle commands.
    """
    log.info("Arming ESC (throttle 0%% for 2 s)…")
    cmd_throttle(ser, 0.0)
    time.sleep(2.0)
    log.info("ESC armed.")


def run_sweep(
    ser: serial.Serial,
    edf_id: int,
    steps: int,
    dwell_s: float,
    n_samples: int,
    hx711_scale: float,
    hx711_offset: int,
) -> List[SweepPoint]:
    """
    Execute the full 0 % → 100 % → 0 % throttle sweep.

    Ascent and descent share the same step size.  At each step the function:
      1. Commands the throttle.
      2. Waits ``dwell_s`` seconds for the RPM to stabilise.
      3. Requests ``n_samples`` raw samples from the FC node.
      4. Averages the samples into a :class:`SweepPoint`.

    The safety net calls :func:`cmd_safe` if an exception escapes so the EDF
    is never left running unattended.

    :param ser:           Open serial port to FC node in calibration mode.
    :param edf_id:        EDF index (for logging only).
    :param steps:         Number of throttle steps from 0 % to 100 %.
    :param dwell_s:       Seconds to dwell at each step.
    :param n_samples:     Samples to average at each step.
    :param hx711_scale:   HX711 counts per gram.
    :param hx711_offset:  HX711 tare offset (counts).
    :returns: List of SweepPoint objects (ascending + descending).
    """
    throttle_steps = [i * (100.0 / steps) for i in range(steps + 1)]
    # Full sweep: ascend then descend.
    profile = throttle_steps + list(reversed(throttle_steps))

    points: List[SweepPoint] = []
    edf_name = EDF_NAMES.get(edf_id, str(edf_id))

    log.info(
        "Starting sweep: EDF %d (%s), %d steps × %.1f s dwell, "
        "%d samples/step.",
        edf_id,
        edf_name,
        len(profile),
        dwell_s,
        n_samples,
    )

    try:
        for thr_pct in profile:
            cmd_throttle(ser, thr_pct)
            log.info(
                "  Throttle %.1f %% — dwelling %.1f s…", thr_pct, dwell_s
            )
            time.sleep(dwell_s)

            raw_samples = collect_samples(ser, n_samples, hx711_scale, hx711_offset)
            rpm_mean, rpm_std, thrust_n, thrust_std, esc_temp = _average_samples(
                raw_samples, hx711_scale, hx711_offset
            )

            point = SweepPoint(
                throttle_pct=thr_pct,
                rpm_mean=rpm_mean,
                rpm_std=rpm_std,
                thrust_n=thrust_n,
                thrust_std=thrust_std,
                esc_temp_c=esc_temp,
                n_samples=len(raw_samples),
            )
            points.append(point)
            log.info(
                "  → RPM=%.0f±%.0f  T=%.3f±%.3f N  ESC=%d°C",
                rpm_mean,
                rpm_std,
                thrust_n,
                thrust_std,
                int(esc_temp),
            )

    except Exception:
        log.error("Exception during sweep — issuing SAFE command.")
        cmd_safe(ser)
        raise

    # Always return throttle to zero after the sweep.
    cmd_throttle(ser, 0.0)
    log.info("Sweep complete.  Collected %d points.", len(points))
    return points

# ---------------------------------------------------------------------------
# Tare / weigh utilities
# ---------------------------------------------------------------------------


def tare_only(ser: serial.Serial, n_samples: int) -> int:
    """
    Collect ``n_samples`` readings at zero throttle and print the mean
    HX711 raw count for use as --hx711-offset in a subsequent calibration.

    :param ser:       Open serial port.
    :param n_samples: Number of samples to average.
    :returns: Mean tare count (integer, for command-line printing).
    """
    log.info("Tare mode: collecting %d samples at zero throttle…", n_samples)
    cmd_throttle(ser, 0.0)
    time.sleep(1.0)
    raw_samples = collect_samples(ser, n_samples, hx711_scale=1.0, hx711_offset=0)
    counts = [s.hx711_raw for s in raw_samples]
    mean_count = int(round(float(np.mean(counts))))
    std_count = float(np.std(counts))
    print(f"Tare result:  mean={mean_count}  std={std_count:.1f}")
    print(f"Use --hx711-offset {mean_count} for calibration runs.")
    return mean_count


def weigh_only(ser: serial.Serial, n_samples: int, tare_count: int) -> None:
    """
    Collect ``n_samples`` readings with a known mass on the load cell and
    print the net count for scale-factor calculation.

    :param ser:         Open serial port.
    :param n_samples:   Number of samples to average.
    :param tare_count:  Zero-offset count from a prior :func:`tare_only` run.
    """
    log.info("Weigh mode: collecting %d samples…", n_samples)
    raw_samples = collect_samples(ser, n_samples, hx711_scale=1.0, hx711_offset=0)
    counts = [s.hx711_raw for s in raw_samples]
    mean_count = float(np.mean(counts))
    net_count = mean_count - tare_count
    print(f"Raw mean count:  {mean_count:.1f}")
    print(f"Tare offset:     {tare_count}")
    print(f"Net count:       {net_count:.1f}")
    print()
    print("To compute scale factor, divide net count by the known mass in grams:")
    print(f"  scale  =  {net_count:.1f}  /  <known_mass_g>")

# ---------------------------------------------------------------------------
# Thrust-model fitting
# ---------------------------------------------------------------------------


def _thrust_model(rpm: np.ndarray, k: float) -> np.ndarray:
    """
    Aerodynamic thrust model: T = k × RPM².

    Used as the fitting function for scipy.optimize.curve_fit.

    :param rpm: Motor speed array (rev/min).
    :param k:   Thrust coefficient (N / RPM²).
    :returns:   Thrust array (N).
    """
    return k * np.square(rpm)


def fit_thrust_model(
    points: List[SweepPoint], edf_id: int
) -> CalibrationResult:
    """
    Fit T = k × RPM² to the swept data and return the calibration result.

    Points with RPM below EDF_RPM_FLOOR_FOR_FIT are excluded (EDF still
    spinning up or coasting below minimum reliable telemetry).  Points with
    non-positive thrust are also excluded to prevent fitting artefacts from
    load-cell mechanical noise at idle.

    :param points:  List of averaged SweepPoints from :func:`run_sweep`.
    :param edf_id:  EDF index for labelling the result.
    :returns: Fitted CalibrationResult.
    :raises ValueError: If too few usable points remain after filtering.
    """
    # Filter out idle / noise points.
    usable = [
        p for p in points
        if p.rpm_mean >= EDF_RPM_FLOOR_FOR_FIT and p.thrust_n > 0.0
    ]
    if len(usable) < 3:
        raise ValueError(
            f"Only {len(usable)} usable sweep points after filtering "
            f"(need ≥ 3).  Check HX711 scale factor and EDF connection."
        )

    rpms = np.array([p.rpm_mean for p in usable], dtype=np.float64)
    thrusts = np.array([p.thrust_n for p in usable], dtype=np.float64)
    thrust_stds = np.array([max(p.thrust_std, 1e-6) for p in usable], dtype=np.float64)

    # Initial guess: k derived from first usable point.
    k0 = float(thrusts[0] / (rpms[0] ** 2)) if rpms[0] > 0 else 1e-8

    try:
        popt, pcov = curve_fit(
            _thrust_model,
            rpms,
            thrusts,
            p0=[k0],
            sigma=thrust_stds,
            absolute_sigma=True,
            maxfev=10000,
        )
    except RuntimeError as exc:
        raise ValueError(f"curve_fit failed to converge: {exc}") from exc

    k_fit = float(popt[0])
    k_stderr = float(np.sqrt(pcov[0, 0]))

    # Compute R² against the fit.
    thrusts_pred = _thrust_model(rpms, k_fit)
    ss_res = float(np.sum((thrusts - thrusts_pred) ** 2))
    ss_tot = float(np.sum((thrusts - np.mean(thrusts)) ** 2))
    r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 0.0 else 0.0
    rms_residual = float(np.sqrt(ss_res / len(usable)))

    return CalibrationResult(
        edf_id=edf_id,
        edf_name=EDF_NAMES.get(edf_id, str(edf_id)),
        k=k_fit,
        k_stderr=k_stderr,
        r_squared=r_squared,
        rms_residual_n=rms_residual,
        n_points=len(usable),
    )

# ---------------------------------------------------------------------------
# Header update
# ---------------------------------------------------------------------------

#: Pattern matches the value field of a EDF_THRUST_K_* #define line.
#: Group 1: everything before the value.
#: Group 2: the value in parentheses.
#: Group 3: the trailing comment (includes CAL:<NAME> tag).
_THRUST_K_PATTERN = re.compile(
    r"(#define\s+EDF_THRUST_K_{name}\s+)(\([^)]+\))(.*)"
)


def update_governor_config(
    config_path: Path, results: List[CalibrationResult]
) -> None:
    """
    Regex-replace the EDF_THRUST_K_* constant values in governor_config.h
    with the calibrated k values from ``results``.

    The update is atomic: the new content is written to a temporary file in
    the same directory, then renamed over the original so a partial write
    can never corrupt the header.

    :param config_path: Absolute or relative path to governor_config.h.
    :param results:     Calibration results (one per EDF being updated).
    :raises FileNotFoundError: If config_path does not exist.
    :raises RuntimeError:      If a constant pattern is not found in the file.
    """
    config_path = Path(config_path).resolve()
    if not config_path.is_file():
        raise FileNotFoundError(
            f"governor_config.h not found at {config_path}.  "
            "Use --output to specify the correct path."
        )

    content = config_path.read_text(encoding="ascii")

    for result in results:
        name = result.edf_name  # e.g. "PORT_FWD"
        pattern = _THRUST_K_PATTERN.pattern.replace("{name}", name)
        rx = re.compile(pattern)

        # Format k to 6 significant figures in scientific notation.
        new_value = f"({result.k:.6e})"
        # Mark the line as calibrated (replace [UNCALIBRATED] in the comment).
        replacement_func = lambda m: (  # noqa: E731
            m.group(1)
            + new_value
            + m.group(3).replace("[UNCALIBRATED]", f"[cal {result.calibrated_at}]")
        )

        new_content, n_subs = rx.subn(replacement_func, content)
        if n_subs == 0:
            raise RuntimeError(
                f"Pattern for EDF_THRUST_K_{name} not found in {config_path}.  "
                "Has the header been modified manually?"
            )
        content = new_content
        log.info(
            "Updated EDF_THRUST_K_%s → %.6e  (R²=%.4f)",
            name,
            result.k,
            result.r_squared,
        )

    # Atomic write: write to a temp file, then rename.
    tmp_fd, tmp_path = tempfile.mkstemp(
        dir=config_path.parent, prefix=".governor_config_tmp_", suffix=".h"
    )
    try:
        with os.fdopen(tmp_fd, "w", encoding="ascii") as tmp_file:
            tmp_file.write(content)
        os.replace(tmp_path, config_path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    log.info("governor_config.h updated at %s.", config_path)

# ---------------------------------------------------------------------------
# CSV output
# ---------------------------------------------------------------------------


def write_csv(
    csv_path: Path, edf_id: int, points: List[SweepPoint]
) -> None:
    """
    Write sweep data to a CSV file for post-analysis.

    Columns: edf_id, throttle_pct, rpm_mean, rpm_std, thrust_n,
             thrust_std, esc_temp_c, n_samples.

    :param csv_path: Output file path.
    :param edf_id:   EDF index (written to every row for multi-EDF files).
    :param points:   Sweep points to write.
    """
    csv_path = Path(csv_path)
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "edf_id",
                "edf_name",
                "throttle_pct",
                "rpm_mean",
                "rpm_std",
                "thrust_n",
                "thrust_std",
                "esc_temp_c",
                "n_samples",
            ]
        )
        edf_name = EDF_NAMES.get(edf_id, str(edf_id))
        for pt in points:
            writer.writerow(
                [
                    edf_id,
                    edf_name,
                    f"{pt.throttle_pct:.1f}",
                    f"{pt.rpm_mean:.1f}",
                    f"{pt.rpm_std:.1f}",
                    f"{pt.thrust_n:.6f}",
                    f"{pt.thrust_std:.6f}",
                    f"{pt.esc_temp_c:.1f}",
                    pt.n_samples,
                ]
            )
    log.info("Sweep data saved to %s.", csv_path)

# ---------------------------------------------------------------------------
# Summary reporting
# ---------------------------------------------------------------------------


def print_summary(result: CalibrationResult) -> None:
    """
    Print a human-readable calibration summary to stdout.

    :param result: Completed CalibrationResult.
    """
    print()
    print("=" * 60)
    print(f"  Calibration result — EDF {result.edf_id} ({result.edf_name})")
    print("=" * 60)
    print(f"  k  =  {result.k:.6e}  N / RPM²")
    print(f"  k σ =  {result.k_stderr:.3e}  (one-sigma)")
    print(f"  R²  =  {result.r_squared:.6f}")
    print(f"  RMS residual  =  {result.rms_residual_n * 1000:.2f} mN")
    print(f"  Points fitted =  {result.n_points}")
    print(f"  Calibrated at =  {result.calibrated_at}")

    if result.r_squared < 0.990:
        print()
        print("  WARNING: R² < 0.99.  Check load-cell mounting, EDF alignment,")
        print("  and HX711 scale factor.  Re-run calibration before using k.")
    elif result.r_squared >= 0.999:
        print()
        print("  Excellent fit (R² ≥ 0.999).  k is suitable for flight firmware.")
    else:
        print()
        print("  Good fit.  k is suitable for ground tests; re-run before flight.")
    print("=" * 60)
    print()

# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def _edf_id_type(value: str) -> int:
    """
    Validate --edf-id argument.

    :param value: String from argparse.
    :returns: Integer EDF ID.
    :raises argparse.ArgumentTypeError: If out of range.
    """
    try:
        n = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"EDF ID must be an integer 0–{EDF_COUNT - 1}, got {value!r}."
        ) from exc
    if not (0 <= n < EDF_COUNT):
        raise argparse.ArgumentTypeError(
            f"EDF ID {n} out of range [0, {EDF_COUNT - 1}]."
        )
    return n


def build_parser() -> argparse.ArgumentParser:
    """
    Build and return the command-line argument parser.

    :returns: Configured ArgumentParser.
    """
    parser = argparse.ArgumentParser(
        prog="governor_cal.py",
        description=(
            "EDF thrust-stand calibration tool for Serenity UAV.\n"
            "Sweeps 0%%→100%%→0%% throttle, fits T = k × RPM², and updates\n"
            "governor_config.h with the calibrated k coefficient.\n\n"
            "Run with --tare-only first to determine --hx711-offset, then\n"
            "--weigh-only with a known mass to find --hx711-scale."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Connection.
    conn = parser.add_argument_group("Serial connection")
    conn.add_argument(
        "-p", "--port",
        default="/dev/ttyUSB0",
        metavar="DEVICE",
        help="Serial device for FC node (default: /dev/ttyUSB0).",
    )
    conn.add_argument(
        "-b", "--baud",
        type=int,
        default=CAL_BAUD_DEFAULT,
        metavar="RATE",
        help=f"Baud rate (default: {CAL_BAUD_DEFAULT}).",
    )

    # EDF selection.
    edf_grp = parser.add_argument_group("EDF selection")
    names_str = ", ".join(f"{k}={v}" for k, v in EDF_NAMES.items())
    edf_grp.add_argument(
        "-e", "--edf-id",
        type=_edf_id_type,
        default=None,
        metavar="ID",
        help=f"EDF index to calibrate (0–{EDF_COUNT - 1}).  ({names_str})",
    )

    # HX711 load cell.
    lc = parser.add_argument_group("HX711 load cell")
    lc.add_argument(
        "--hx711-scale",
        type=float,
        default=None,
        metavar="COUNTS_PER_GRAM",
        help=(
            "HX711 counts per gram (required for calibration).  "
            "Determine with --tare-only then --weigh-only."
        ),
    )
    lc.add_argument(
        "--hx711-offset",
        type=int,
        default=0,
        metavar="COUNTS",
        help="HX711 tare offset in raw counts (default: 0).",
    )

    # Sweep parameters.
    sweep = parser.add_argument_group("Sweep parameters")
    sweep.add_argument(
        "-s", "--steps",
        type=int,
        default=20,
        metavar="N",
        help="Throttle sweep steps from 0%% to 100%% (default: 20).",
    )
    sweep.add_argument(
        "-d", "--dwell",
        type=float,
        default=3.0,
        metavar="SEC",
        help="Dwell time per throttle step in seconds (default: 3.0).",
    )
    sweep.add_argument(
        "-n", "--samples",
        type=int,
        default=60,
        metavar="N",
        help="Raw samples to average at each step (default: 60).",
    )

    # Output.
    out = parser.add_argument_group("Output")
    out.add_argument(
        "-o", "--output",
        default=None,
        metavar="PATH",
        help=(
            "Path to governor_config.h to update (default: auto-detect "
            "relative to script location)."
        ),
    )
    out.add_argument(
        "--csv",
        default=None,
        metavar="FILE",
        help="Save raw sweep data to a CSV file.",
    )

    # Utility modes.
    util = parser.add_argument_group("Utility modes (mutually exclusive with sweep)")
    util_mx = util.add_mutually_exclusive_group()
    util_mx.add_argument(
        "--tare-only",
        action="store_true",
        help=(
            "Collect samples at zero throttle and print the mean HX711 raw "
            "count for use as --hx711-offset."
        ),
    )
    util_mx.add_argument(
        "--weigh-only",
        action="store_true",
        help=(
            "Collect samples with a known mass on the load cell and print the "
            "net count for scale-factor calculation.  Requires --tare-count."
        ),
    )
    util.add_argument(
        "--tare-count",
        type=int,
        default=None,
        metavar="COUNTS",
        help="Tare offset from a prior --tare-only run (required for --weigh-only).",
    )

    # Verbosity.
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable DEBUG-level logging.",
    )

    return parser

# ---------------------------------------------------------------------------
# Default output path resolution
# ---------------------------------------------------------------------------


def _default_config_path() -> Path:
    """
    Resolve the default path to governor_config.h relative to this script.

    Script location:  avionics/firmware/fc/tools/governor_cal.py
    Config location:  avionics/firmware/fc/src/governor_config.h

    :returns: Resolved Path to governor_config.h.
    """
    return (Path(__file__).parent / ".." / "src" / "governor_config.h").resolve()

# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------


def main() -> int:
    """
    Parse arguments, connect to the FC node, run the calibration sweep,
    fit the thrust model, and update governor_config.h.

    :returns: 0 on success, non-zero on error.
    """
    parser = build_parser()
    args = parser.parse_args()

    # Configure logging.
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s  %(levelname)-7s  %(message)s",
        datefmt="%H:%M:%S",
    )

    # ── Utility modes (tare / weigh) ────────────────────────────────────────

    if args.tare_only or args.weigh_only:
        if args.weigh_only and args.tare_count is None:
            parser.error("--weigh-only requires --tare-count.")
        ser = open_serial(args.port, args.baud)
        try:
            if args.tare_only:
                tare_only(ser, n_samples=min(args.samples, 100))
            else:
                weigh_only(
                    ser,
                    n_samples=min(args.samples, 100),
                    tare_count=args.tare_count,
                )
        finally:
            cmd_safe(ser)
            ser.close()
        return 0

    # ── Calibration sweep ────────────────────────────────────────────────────

    if args.edf_id is None:
        parser.error("--edf-id is required for a calibration sweep.")
    if args.hx711_scale is None:
        parser.error(
            "--hx711-scale is required for a calibration sweep.  "
            "Determine it with --tare-only then --weigh-only."
        )
    if args.hx711_scale <= 0.0:
        parser.error("--hx711-scale must be positive.")
    if args.steps < 5:
        parser.error("--steps must be at least 5 for a valid fit.")
    if args.dwell < 0.5:
        parser.error("--dwell must be at least 0.5 seconds.")
    if args.samples < 5:
        parser.error("--samples must be at least 5 per step.")

    # Resolve output path.
    config_path = Path(args.output) if args.output else _default_config_path()
    log.info("Will update %s.", config_path)

    # Open serial and verify target.
    ser = open_serial(args.port, args.baud)
    try:
        verify_cal_mode(ser, args.edf_id)
        arm_esc(ser)

        # Run the sweep.
        points = run_sweep(
            ser=ser,
            edf_id=args.edf_id,
            steps=args.steps,
            dwell_s=args.dwell,
            n_samples=args.samples,
            hx711_scale=args.hx711_scale,
            hx711_offset=args.hx711_offset,
        )

    finally:
        # Always safe the EDF before closing serial.
        cmd_safe(ser)
        ser.close()

    # ── Save raw CSV if requested ────────────────────────────────────────────

    if args.csv:
        write_csv(Path(args.csv), args.edf_id, points)

    # ── Fit the thrust model ─────────────────────────────────────────────────

    log.info("Fitting T = k × RPM² to %d sweep points…", len(points))
    try:
        result = fit_thrust_model(points, args.edf_id)
    except ValueError as exc:
        log.error("Fit failed: %s", exc)
        return 1

    print_summary(result)

    # ── Update governor_config.h ─────────────────────────────────────────────

    try:
        update_governor_config(config_path, [result])
    except (FileNotFoundError, RuntimeError) as exc:
        log.error("Failed to update governor_config.h: %s", exc)
        return 1

    log.info("Done.  Rebuild serenity-fc to compile the updated constants.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
