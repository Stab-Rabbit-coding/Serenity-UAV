/**
 * @file    failsafe_config.h
 * @brief   Cross-node failsafe threshold compile-time constants.
 *
 * Copyright 2026 Steve Griffing
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Full design rationale, citations, and derivation for every threshold in
 * this file are recorded in docs/failsafe_thresholds.md — that document is
 * authoritative; this header is its compile-time expression per the
 * Phase 0 pre-print documentation gate in the project work-breakdown
 * structure ("All thresholds must be defined as compile-time constants in
 * firmware/common/failsafe_config.h").
 *
 * Scope note — what belongs here vs. elsewhere:
 *   This header holds only the cross-node coordination thresholds that do
 *   NOT already have an authoritative compile-time home elsewhere in the
 *   tree.  Two threshold families are DELIBERATELY NOT redefined here
 *   because they are already implemented and documented:
 *     - Battery/pack/current fault thresholds -> avionics/firmware/fc/src/
 *       pwr_fault.h (PWR_FAULT_CELL_*_MV, PWR_FAULT_PACK_*_MV,
 *       PWR_FAULT_ESC_*_MA), backed by docs/POWER_DISTRIBUTION.md S8.
 *     - EDF RPM ceilings and the existing single-stage ESC over-temperature
 *       cutoff -> avionics/firmware/fc/src/governor_config.h
 *       (EDF_RPM_MAX_50MM/55MM, EDF_ESC_OVERTEMP_C).
 *   See docs/failsafe_thresholds.md S1 and S4 for the reconciliation notes
 *   between this file's two-stage ESC thermal scheme and
 *   governor_config.h's existing single-stage EDF_ESC_OVERTEMP_C=100C
 *   value — that reconciliation is an open firmware follow-up item, not
 *   yet applied to governor_config.h.
 *
 * Target platform: PocketBeagle 2 Industrial (AM6254), Debian Trixie.
 * Shared across FC (Pilot) and CN (XO) node firmware.
 */

#ifndef AVIONICS_FIRMWARE_COMMON_INCLUDE_FAILSAFE_CONFIG_H_
#define AVIONICS_FIRMWARE_COMMON_INCLUDE_FAILSAFE_CONFIG_H_

#ifdef __cplusplus
extern "C" {
#endif

/* ============================================================================
 * CAN FD Node Heartbeat / Master (Bus Controller) Re-Election
 * ============================================================================
 *
 * The PRU0 MIL-STD-1553B bus controller role and general node-primary role
 * are elected via CAN FD heartbeat (see avionics/firmware/dts/cape-a/
 * k3-am6254-pocketbeagle2-serenity-cape-a2.dts S8, and
 * docs/POWER_DISTRIBUTION.md S10 "T+30s: CAN FD heartbeat election
 * complete; FC1 assumes primary role").  This constant governs the
 * steady-state re-election path: if the current primary's heartbeat frame
 * is not observed within this window by the next PACE-tier node (see
 * CLAUDE.md "Avionics Workload Balancing"), that node assumes the primary
 * role for its tier.
 *
 * Design decision (docs/failsafe_thresholds.md S2): unchanged from the
 * Phase 0 pre-print documentation gate default.
 */

/** CAN FD node heartbeat re-election timeout (ms). */
#define FAILSAFE_CANFD_HEARTBEAT_TIMEOUT_MS       (100U)

/* ============================================================================
 * External Radio Loss -> Automatic RTL
 * ============================================================================
 *
 * Per-link timer from last-received valid command/telemetry exchange before
 * the owning node autonomously initiates Return-To-Launch.  Two links have
 * an assigned RTL timer today; Wi-Fi (5 GHz) and Zigbee (2.4 GHz) do not yet
 * — see docs/failsafe_thresholds.md S2 open-item note.
 *
 * Consistent with the Phase 10 work-breakdown-structure pass criterion:
 * "Emergency RTL validation ... verify automatic RTL initiates within 5s
 * of link loss."
 */

/** SiK (915 MHz) / LoRa (915 MHz) link-loss timer before autonomous RTL (ms).
 */
#define FAILSAFE_RADIO_LOSS_RTL_SIK_LORA_MS       (5000U)

/**
 * 49 MHz (Commo, 47 CFR Part 15 S15.235) link-loss timer before autonomous
 * RTL (ms).  Longer than the SiK/LoRa timer because 49 MHz is the
 * designated backup/high-RF-environment link (River/Simon Commo boards,
 * CLAUDE.md) — a slower AFSK/KISS link legitimately has more inter-frame
 * gap, so the timer must not nuisance-trigger RTL during normal operation.
 */
#define FAILSAFE_RADIO_LOSS_RTL_49MHZ_MS          (10000U)

/* ============================================================================
 * ESC Thermal — Two-Stage Cutback / Shutdown
 * ============================================================================
 *
 * DESIGN TARGET (docs/failsafe_thresholds.md S4).  NOT YET reconciled with
 * the single-stage EDF_ESC_OVERTEMP_C=100C hard fault already implemented
 * in governor_config.h — see that file and docs/failsafe_thresholds.md S4
 * for the open reconciliation item.  BDSHOT600 extended telemetry already
 * carries the ESC temperature reading these thresholds would consume.
 */

/**
 * ESC temperature at which the governor begins throttle cutback on the
 * affected EDF (deg C).  Below FAILSAFE_ESC_THERMAL_SHUTDOWN_C — the EDF
 * stays armed at reduced throttle rather than latching a hard fault.
 */
#define FAILSAFE_ESC_THERMAL_CUTBACK_C            (85)

/**
 * ESC temperature at which the governor latches a hard shutdown fault on
 * the affected EDF (deg C).  Mirrors the PWR_STATE_EMERGENCY / GCS-ack
 * no-auto-recovery semantics already used by pwr_fault.h.
 */
#define FAILSAFE_ESC_THERMAL_SHUTDOWN_C           (95)

/**
 * Throttle percentage commanded on an EDF in thermal cutback (%).  Reuses
 * the PWR_FAULT_EMERGENCY_THROTTLE_PCT=70 convention (pwr_fault.h) for
 * consistency across the codebase's fault-response vocabulary rather than
 * introducing a new unrelated percentage.
 */
#define FAILSAFE_ESC_THERMAL_CUTBACK_THROTTLE_PCT (70U)

/* ============================================================================
 * ToF Obstacle Avoidance — Halt / Resume Clearance
 * ============================================================================
 *
 * Applies to the 12x VL53L5CX obstacle-avoidance array (docs/
 * PHASED_BUILD_GUIDE.md Phase 5), rated 4 m effective range (REFERENCES.md
 * REF-SENSOR-002 note) — both thresholds sit comfortably inside that range.
 * Not the Vera bow/cargo TFmini-S ranging sensor (REF-SENSOR-002 itself),
 * which serves object-metrology, not flight-path obstacle avoidance.
 *
 * Hysteresis band (halt 1.0 m, resume 1.5 m) prevents halt/resume chatter
 * when hovering near a fixed clearance boundary.
 */

/** Obstacle range below which forward/lateral motion is halted (m). */
#define FAILSAFE_TOF_HALT_CLEARANCE_M             (1.0f)

/** Obstacle range above which halted motion may resume (m). */
#define FAILSAFE_TOF_RESUME_CLEARANCE_M           (1.5f)

#ifdef __cplusplus
}
#endif

#endif /* AVIONICS_FIRMWARE_COMMON_INCLUDE_FAILSAFE_CONFIG_H_ */
