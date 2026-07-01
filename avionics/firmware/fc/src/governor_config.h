/**
 * @file    governor_config.h
 * @brief   EDF PID controller compile-time constants — thrust model, control
 *          parameters, and ESC safety thresholds.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * This header provides all compile-time tuning constants for the EDF PID RPM
 * controller implemented in the Cape-A / FC node Phase 7 firmware.  The
 * governing thrust equation for each EDF is:
 *
 *   T [N]  =  EDF_THRUST_K_<ID>  ×  RPM²
 *
 * The k coefficients here are initial design estimates derived from
 * manufacturer performance data (see References [1][2]).  They MUST be
 * replaced with measured values from a physical thrust-stand calibration run
 * before first flight.  Run:
 *
 *   avionics/firmware/fc/tools/governor_cal.py --help
 *
 * to perform the calibration sweep; the script will auto-update the
 * EDF_THRUST_K_* values in this file.
 *
 * EDF propulsion assignment (CLAUDE.md avionics architecture):
 * ┌─────┬─────────────┬─────────┬────────────────────────────────┐
 * │ ID  │ Label       │ Size    │ Primary FC node                │
 * ├─────┼─────────────┼─────────┼────────────────────────────────┤
 * │  0  │ PORT_FWD    │  50 mm  │ FC1                            │
 * │  1  │ PORT_AFT    │  50 mm  │ FC2 (secondary to port fwd)    │
 * │  2  │ STBD_FWD    │  50 mm  │ FC2                            │
 * │  3  │ STBD_AFT    │  50 mm  │ FC3 (secondary to stbd fwd)    │
 * │  4  │ FUSE        │  55 mm  │ FC3                            │
 * └─────┴─────────────┴─────────┴────────────────────────────────┘
 *
 * References:
 *   [1] FlightLine / Freewing 50 mm EDF product data sheet, 2023 —
 *       typical performance: ~7.85 N (800 gf) at 28 000 RPM on 6S LiPo.
 *   [2] Freewing 55 mm 4400 kV 6S EDF product data sheet, 2023 —
 *       typical performance: ~29.4 N (3 000 gf) at 16 000 RPM on 6S LiPo.
 *   [3] Mahony, R., Hamel, T., Pflimlin, J.-M., "Nonlinear Complementary
 *       Filters on the Special Orthogonal Group," IEEE Trans. Autom.
 *       Control, vol. 53, no. 5, pp. 1203–1218, 2008.
 *       — discrete-time PID velocity formulation basis.
 *   [4] Ziegler, J. G., Nichols, N. B., "Optimum Settings for Automatic
 *       Controllers," Trans. ASME, vol. 64, no. 8, pp. 759–768, 1942.
 *       — initial Kp/Ki/Kd estimates via ZN step-response method
 *         (simulated first-order EDF model: τ₅₀ ≈ 80 ms, τ₁₂₀ ≈ 150 ms).
 *
 * Target platform: PocketBeagle 2 Industrial (AM6254), Debian Trixie.
 * Compiled as part of avionics/firmware/fc via CMake.
 */

#ifndef GOVERNOR_CONFIG_H
#define GOVERNOR_CONFIG_H

/* ============================================================================
 * EDF Identification Indices
 * ============================================================================
 *
 * These constants identify each EDF throughout controller firmware, CAN FD
 * message IDs, fault registers, and the calibration tool.  The index
 * matches the EDF_THRUST_K_* array position used in controller logic.
 */

/**
 * @defgroup edf_ids  EDF channel indices
 * @{
 */

/** Port-nacelle forward EDF (50 mm, 6S).  Primary FC node: FC1. */
#define EDF_ID_PORT_FWD     (0U)

/** Port-nacelle aft EDF (50 mm, 6S).  Primary FC node: FC2. */
#define EDF_ID_PORT_AFT     (1U)

/** Stbd-nacelle forward EDF (50 mm, 6S).  Primary FC node: FC2. */
#define EDF_ID_STBD_FWD     (2U)

/** Stbd-nacelle aft EDF (50 mm, 6S).  Primary FC node: FC3. */
#define EDF_ID_STBD_AFT     (3U)

/** Fuselage rear EDF (55 mm, 6S).  Primary FC node: FC3. */
#define EDF_ID_FUSE         (4U)

/** Total number of distinct EDF channels in the propulsion system. */
#define EDF_COUNT           (5U)

/** @} */

/* ============================================================================
 * Thrust Model Coefficients   [T = k × RPM²]
 * ============================================================================
 *
 * Units: N / RPM²   (equivalently  N·min²·rev⁻²)
 *
 * Design-estimate basis — see References [1] and [2]:
 *   50 mm  — 7.85 N at 28 000 RPM  →  k = 7.85 / (28 000)² ≈ 1.00×10⁻⁸
 *   55 mm — 29.4 N at 16 000 RPM  →  k = 29.4  / (16 000)² ≈ 1.15×10⁻⁷
 *
 * !! UNCALIBRATED — run governor_cal.py on a thrust stand before flight !!
 *
 * governor_cal.py identifies each constant by its CAL:<NAME> inline tag.
 * Do not alter those tags.
 */

/**
 * @defgroup thrust_k  Thrust model k coefficients (N / RPM²)
 * @{
 */

/** Thrust coefficient — port-nacelle forward EDF.  [UNCALIBRATED] */
#define EDF_THRUST_K_PORT_FWD   (1.00e-8)   /* CAL:PORT_FWD */

/** Thrust coefficient — port-nacelle aft EDF.  [UNCALIBRATED] */
#define EDF_THRUST_K_PORT_AFT   (1.00e-8)   /* CAL:PORT_AFT */

/** Thrust coefficient — stbd-nacelle forward EDF.  [UNCALIBRATED] */
#define EDF_THRUST_K_STBD_FWD   (1.00e-8)   /* CAL:STBD_FWD */

/** Thrust coefficient — stbd-nacelle aft EDF.  [UNCALIBRATED] */
#define EDF_THRUST_K_STBD_AFT   (1.00e-8)   /* CAL:STBD_AFT */

/** Thrust coefficient — fuselage rear EDF.  [UNCALIBRATED] */
#define EDF_THRUST_K_FUSE       (1.15e-7)   /* CAL:FUSE */

/** @} */

/* ============================================================================
 * RPM Operating Limits
 * ============================================================================
 *
 * The idle floor is the minimum RPM maintained whenever an EDF is armed.
 * It keeps bearings lubricated and prevents controller integrator wind-up.
 * The maximum is the software redline; the ESC's own over-speed protection
 * provides a hardware backstop above this value.
 */

/**
 * @defgroup rpm_limits  RPM operating limits (rev/min)
 * @{
 */

/** 50 mm EDF — minimum armed idle RPM. */
#define EDF_RPM_IDLE_50MM       (8000U)

/** 50 mm EDF — software redline.  Do not command above this. */
#define EDF_RPM_MAX_50MM        (35000U)

/** 55 mm EDF — minimum armed idle RPM. */
#define EDF_RPM_IDLE_55MM      (4000U)

/** 55 mm EDF — software redline.  Do not command above this. */
#define EDF_RPM_MAX_55MM       (18000U)

/** @} */

/* ============================================================================
 * Nacelle Tandem-Pair RPM Balance
 * ============================================================================
 *
 * Each nacelle houses two EDFs in series (forward + aft) that are commanded
 * to the same RPM setpoint.  If |RPM_FWD − RPM_AFT| exceeds the threshold
 * below, the controller latches FAULT_EDF_MISMATCH, broadcasts the fault on
 * CAN FD, and idles both EDFs in that nacelle.  Recovery requires an explicit
 * GCS acknowledgement — no auto-recovery (per CLAUDE.md fault semantics).
 *
 * Threshold chosen per CLAUDE.md target: equalization |RPM_FWD − RPM_AFT|
 * < 100 RPM.
 */

/**
 * Maximum permissible RPM difference within one nacelle's tandem pair (RPM).
 */
#define EDF_RPM_PAIR_MISMATCH_MAX   (100U)

/* ============================================================================
 * PID Controller Tuning Constants
 * ============================================================================
 *
 * Velocity-form discrete-time PID executed at EDF_GOV_LOOP_HZ (1 kHz,
 * synchronised to the BDSHOT600 telemetry packet rate).
 *
 * Error signal:
 *   e[n]  =  RPM_setpoint[n]  −  RPM_bdshot[n]
 *
 * Control output is a 16-bit EHRPWM duty-cycle word (0–65535 ≡ 0–100 %).
 *
 * Kp / Ki / Kd derived via ZN step-response method on a first-order EDF
 * model, then discretised for the 1 kHz loop.  Must be validated on a
 * thrust stand before flight (see References [3] and [4]).
 */

/**
 * @defgroup pid_gains  PID controller tuning constants
 * @{
 */

/** Proportional gain — 50 mm EDF class. */
#define EDF_GOV_KP_50MM     (0.000180)

/** Integral gain — 50 mm EDF class (per controller tick at 1 kHz). */
#define EDF_GOV_KI_50MM     (4.500e-6)

/** Derivative gain — 50 mm EDF class. */
#define EDF_GOV_KD_50MM     (9.000e-6)

/** Proportional gain — 55 mm EDF class. */
#define EDF_GOV_KP_55MM    (0.000120)

/** Integral gain — 55 mm EDF class. */
#define EDF_GOV_KI_55MM    (3.000e-6)

/** Derivative gain — 55 mm EDF class. */
#define EDF_GOV_KD_55MM    (6.000e-6)

/** @} */

/* ============================================================================
 * ESC Safety Thresholds
 * ============================================================================
 *
 * The BDSHOT600 extended telemetry frame carries ESC temperature (°C) and
 * phase-current magnitude (A) for each EDF.  Exceeding either threshold
 * below triggers an immediate fault latch on the responsible FC node.
 *
 * Fault is broadcast on CAN FD IDs 0x010–0x014 (one ID per EDF channel).
 * No auto-recovery — GCS acknowledgement required before the EDF may be
 * re-armed.
 */

/**
 * @defgroup esc_fault  ESC safety thresholds
 * @{
 */

/**
 * Over-temperature limit (°C).
 * Exceeding this value triggers FAULT_ESC_OVERTEMP on the responsible EDF.
 */
#define EDF_ESC_OVERTEMP_C          (100)

/**
 * Peak phase-current limit (A).
 * Exceeding this value triggers FAULT_ESC_OVERCURRENT on the responsible EDF.
 */
#define EDF_ESC_OVERCURRENT_A       (80)

/** @} */

/* ============================================================================
 * Governor Loop Timing
 * ============================================================================ */

/**
 * Governor control loop execution rate (Hz).
 * Matches the BDSHOT600 telemetry packet rate so every telemetry sample
 * produces exactly one control output update.
 */
#define EDF_GOV_LOOP_HZ             (1000U)

/**
 * Maximum RPM setpoint change per governor tick (RPM/tick = RPM/ms).
 * Limits slew rate to reduce mechanical shock on the nacelle gear train
 * and avoid large EHRPWM duty-cycle transients.
 */
#define EDF_GOV_RPM_RAMP_RATE       (50U)

/**
 * Delay after a setpoint step before fault monitors are re-armed (ms).
 * Allows the RPM to settle before FAULT_EDF_MISMATCH and overshoot checks
 * become active.  Per CLAUDE.md target: settle < 200 ms.
 */
#define EDF_GOV_SETTLE_MS           (200U)

/**
 * Maximum permissible RPM overshoot during a setpoint transition, expressed
 * as a percentage of the step magnitude.
 * Per CLAUDE.md target: overshoot < 5 %.
 */
#define EDF_GOV_OVERSHOOT_MAX_PCT   (5U)

#endif /* GOVERNOR_CONFIG_H */
