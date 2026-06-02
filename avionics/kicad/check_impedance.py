#!/usr/bin/env python3
"""
check_impedance.py — Microstrip characteristic-impedance calculator.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0 — creativecommons.org/licenses/by/4.0

Implements the IPC-2141A / Hammerstad-Jensen closed-form microstrip
formulas with a Wheeler thick-conductor width correction.  Used to
verify XCVR-49MHZ-1 RF trace dimensions meet the 50 Ω ± 5 Ω design
target before board spin (TODO.md Phase 4 — "50 Ω trace impedance
check").

Reference formulas:
  * H.A. Wheeler, "Transmission-Line Properties of a Strip on a
    Dielectric Sheet on a Plane," IEEE Trans. MTT-25(8), Aug 1977.
  * E. Hammerstad and O. Jensen, "Accurate Models for Microstrip
    Computer-Aided Design," IEEE MTT-S Digest, 1980, pp. 407-409.
  * IPC-2141A, "Design Guide for High-Speed Controlled Impedance
    Circuit Boards," IPC, 2004.

XCVR-49MHZ-1 design parameters (from PCB layout TODO):
  Trace width W  : 2.75 mm (F.Cu)
  Substrate height H : 1.6 mm (board total thickness; single-layer or
                       thick prepreg assumption — see Phase 3 stack-up)
  Relative permittivity εr : 4.5 (standard FR4 at 49 MHz)
  Conductor thickness T : 0.035 mm (1 oz Cu, 35 µm)
  Target impedance Z0_target : 50 Ω ± 5 Ω
"""

import argparse
import math
import sys


# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------

_FREE_SPACE_IMPEDANCE_OHM: float = 120.0 * math.pi   # η₀ ≈ 376.73 Ω


# ---------------------------------------------------------------------------
# Core formula functions
# ---------------------------------------------------------------------------

def effective_width(
    w_mm: float,
    h_mm: float,
    t_mm: float,
) -> float:
    """
    Return the effective trace width W_eff (mm) corrected for finite
    conductor thickness T using Wheeler (1977) thick-microstrip extension.

    For W/H > 1/(2π) (the far more common case for 50 Ω wide traces on
    FR4):
        ΔW/H = (T / (π·H)) · (1 + ln(2·H / T))

    For W/H ≤ 1/(2π):
        ΔW/H = (T / (π·H)) · (1 + ln(4·π·W / T))

    Args:
        w_mm: Nominal trace width in mm.
        h_mm: Dielectric substrate height in mm.
        t_mm: Conductor (copper) thickness in mm.

    Returns:
        Effective width W_eff in mm.
    """
    if t_mm <= 0.0:
        # Zero-thickness conductor — no correction required.
        return w_mm

    threshold = 1.0 / (2.0 * math.pi)

    if (w_mm / h_mm) > threshold:
        # Wide-trace branch (typical for 50 Ω on FR4).
        dw = (t_mm / math.pi) * (1.0 + math.log(2.0 * h_mm / t_mm))
    else:
        # Narrow-trace branch.
        dw = (t_mm / math.pi) * (1.0 + math.log(4.0 * math.pi * w_mm / t_mm))

    return w_mm + dw


def effective_permittivity(
    er: float,
    w_eff_mm: float,
    h_mm: float,
) -> float:
    """
    Return the effective relative permittivity ε_eff for a microstrip
    using the Hammerstad-Jensen closed-form approximation.

    For W/H > 1 (wide trace):
        ε_eff = ((εr+1)/2) + ((εr-1)/2) · (1 + 12·H/W)^(-0.5)

    For W/H ≤ 1 (narrow trace), an additional higher-order term is
    included:
        ε_eff = ((εr+1)/2) + ((εr-1)/2) · [(1 + 12·H/W)^(-0.5) +
                0.04·(1 - W/H)²]

    Args:
        er: Substrate relative permittivity (dimensionless).
        w_eff_mm: Effective trace width in mm (after thickness correction).
        h_mm: Dielectric substrate height in mm.

    Returns:
        Effective relative permittivity ε_eff (dimensionless).
    """
    ratio = w_eff_mm / h_mm   # W_eff / H

    base = (er + 1.0) / 2.0
    delta = (er - 1.0) / 2.0

    radical = 1.0 / math.sqrt(1.0 + 12.0 / ratio)

    if ratio > 1.0:
        # Wide trace — no higher-order correction term.
        return base + delta * radical
    else:
        # Narrow trace — additional (1 - W/H)² term.
        correction = 0.04 * (1.0 - ratio) ** 2.0
        return base + delta * (radical + correction)


def microstrip_impedance(
    w_mm: float,
    h_mm: float,
    er: float,
    t_mm: float = 0.035,
) -> tuple[float, float, float]:
    """
    Return the characteristic impedance Z₀ (Ω) of a microstrip trace
    together with the intermediate quantities W_eff and ε_eff.

    Uses Wheeler (1977) thick-conductor width correction followed by
    Hammerstad-Jensen (1980) impedance formulas:

    For W_eff/H ≤ 1 (narrow):
        Z₀ = (60 / √ε_eff) · ln(8·H/W_eff + W_eff/(4·H))

    For W_eff/H > 1 (wide):
        Z₀ = η₀ / (√ε_eff · (W_eff/H + 1.393 + 0.667·ln(W_eff/H + 1.444)))

    Args:
        w_mm: Nominal trace width in mm.
        h_mm: Dielectric substrate height in mm.
        er:   Substrate relative permittivity (dimensionless).
        t_mm: Conductor thickness in mm (default 0.035 mm = 1 oz Cu).

    Returns:
        Tuple (Z0_ohm, w_eff_mm, eps_eff).
    """
    w_eff = effective_width(w_mm, h_mm, t_mm)
    eps_eff = effective_permittivity(er, w_eff, h_mm)
    sqrt_eps = math.sqrt(eps_eff)

    ratio = w_eff / h_mm

    if ratio <= 1.0:
        # Narrow-trace formula — logarithmic.
        z0 = (60.0 / sqrt_eps) * math.log(8.0 * h_mm / w_eff + w_eff / (4.0 * h_mm))
    else:
        # Wide-trace formula — linear denominator.
        denominator = ratio + 1.393 + 0.667 * math.log(ratio + 1.444)
        z0 = _FREE_SPACE_IMPEDANCE_OHM / (sqrt_eps * denominator)

    return z0, w_eff, eps_eff


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def run_check(
    w_mm: float,
    h_mm: float,
    er: float,
    t_mm: float,
    z0_target: float,
    tolerance_ohm: float,
) -> int:
    """
    Calculate Z₀ and print a formatted compliance report to stdout.

    Args:
        w_mm:          Nominal trace width (mm).
        h_mm:          Substrate height (mm).
        er:            Relative permittivity (dimensionless).
        t_mm:          Conductor thickness (mm).
        z0_target:     Target impedance (Ω).
        tolerance_ohm: Allowed deviation from target (Ω, ±).

    Returns:
        0 if Z₀ is within tolerance, 1 if out of tolerance.
    """
    z0, w_eff, eps_eff = microstrip_impedance(w_mm, h_mm, er, t_mm)

    low = z0_target - tolerance_ohm
    high = z0_target + tolerance_ohm
    in_spec = low <= z0 <= high
    status = "PASS" if in_spec else "FAIL"

    print("=" * 60)
    print("  Serenity UAV — XCVR-49MHZ-1 Microstrip Impedance Check")
    print("  IPC-2141A / Hammerstad-Jensen / Wheeler (1977)")
    print("=" * 60)
    print(f"\n  Input parameters")
    print(f"    Trace width        W  = {w_mm:.4f} mm")
    print(f"    Substrate height   H  = {h_mm:.4f} mm")
    print(f"    Permittivity       εr = {er:.2f}")
    print(f"    Cu thickness       T  = {t_mm * 1000:.1f} µm  ({t_mm:.4f} mm)")
    print(f"\n  Computed values")
    print(f"    Effective width    W_eff  = {w_eff:.4f} mm")
    print(f"    Effective ε_eff           = {eps_eff:.4f}")
    print(f"    W_eff / H                 = {w_eff / h_mm:.4f}")
    print(f"\n  Result")
    print(f"    Z₀ = {z0:.2f} Ω")
    print(f"\n  Specification: {z0_target:.0f} Ω ± {tolerance_ohm:.0f} Ω "
          f"  [{low:.0f} – {high:.0f} Ω]")
    print(f"\n  Status: {status}")

    if not in_spec:
        # Suggest a corrective trace width for the target impedance.
        # Binary-search W to find Z0 ≈ z0_target.
        suggested_w = _find_width_for_impedance(z0_target, h_mm, er, t_mm)
        if suggested_w is not None:
            print(f"\n  Suggested correction:")
            print(f"    Width for Z₀={z0_target:.0f} Ω ≈ {suggested_w:.3f} mm")

    print("=" * 60)
    return 0 if in_spec else 1


def _find_width_for_impedance(
    z0_target: float,
    h_mm: float,
    er: float,
    t_mm: float,
    iterations: int = 64,
) -> float | None:
    """
    Binary-search for the trace width that achieves z0_target within 0.01 Ω.

    Args:
        z0_target:  Desired characteristic impedance (Ω).
        h_mm:       Substrate height (mm).
        er:         Relative permittivity.
        t_mm:       Conductor thickness (mm).
        iterations: Maximum binary-search steps.

    Returns:
        Width in mm, or None if the search fails to converge.
    """
    # Z₀ decreases as W increases; bracket accordingly.
    w_lo, w_hi = 0.01, 50.0   # mm — wide enough for any practical trace

    for _ in range(iterations):
        w_mid = (w_lo + w_hi) / 2.0
        z_mid, _, _ = microstrip_impedance(w_mid, h_mm, er, t_mm)

        if abs(z_mid - z0_target) < 0.005:
            # Converged to within 0.005 Ω.
            return w_mid

        if z_mid > z0_target:
            # Impedance too high → trace too narrow → widen it.
            w_lo = w_mid
        else:
            # Impedance too low → trace too wide → narrow it.
            w_hi = w_mid

    return None   # Did not converge (should not occur with sane inputs).


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _build_arg_parser() -> argparse.ArgumentParser:
    """Return a configured ArgumentParser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="check_impedance",
        description=(
            "Microstrip characteristic-impedance calculator (IPC-2141A / "
            "Hammerstad-Jensen).  Verifies XCVR-49MHZ-1 RF trace against "
            "the 50 Ω ± 5 Ω design target."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-W",
        "--width",
        type=float,
        default=2.75,
        metavar="MM",
        help="Trace width in mm.",
    )
    parser.add_argument(
        "-H",
        "--height",
        type=float,
        default=1.6,
        metavar="MM",
        help="Substrate (dielectric) height in mm.",
    )
    parser.add_argument(
        "-e",
        "--epsilon-r",
        type=float,
        default=4.5,
        metavar="ER",
        dest="er",
        help="Substrate relative permittivity (εr).",
    )
    parser.add_argument(
        "-t",
        "--thickness",
        type=float,
        default=0.035,
        metavar="MM",
        help="Conductor (Cu) thickness in mm  [1 oz = 0.035 mm].",
    )
    parser.add_argument(
        "-z",
        "--target",
        type=float,
        default=50.0,
        metavar="OHM",
        help="Target characteristic impedance in Ω.",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=5.0,
        metavar="OHM",
        help="Allowed tolerance around target (±) in Ω.",
    )
    return parser


def main() -> int:
    """Parse CLI arguments and run the impedance check."""
    parser = _build_arg_parser()
    args = parser.parse_args()

    # Validate inputs — reject physically impossible values to prevent
    # math-domain errors inside the formula functions.
    errors: list[str] = []
    if args.width <= 0.0:
        errors.append(f"Trace width must be > 0 mm (got {args.width}).")
    if args.height <= 0.0:
        errors.append(f"Substrate height must be > 0 mm (got {args.height}).")
    if args.er <= 1.0:
        errors.append(f"εr must be > 1.0 (got {args.er}).")
    if args.thickness < 0.0:
        errors.append(f"Conductor thickness must be ≥ 0 mm (got {args.thickness}).")
    if args.target <= 0.0:
        errors.append(f"Target impedance must be > 0 Ω (got {args.target}).")
    if args.tolerance <= 0.0:
        errors.append(f"Tolerance must be > 0 Ω (got {args.tolerance}).")

    if errors:
        for msg in errors:
            print(f"ERROR: {msg}", file=sys.stderr)
        return 2

    return run_check(
        w_mm=args.width,
        h_mm=args.height,
        er=args.er,
        t_mm=args.thickness,
        z0_target=args.target,
        tolerance_ohm=args.tolerance,
    )


if __name__ == "__main__":
    sys.exit(main())
