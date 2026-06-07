/**
 * @file    pwr_fault.h
 * @brief   Power fault monitor and load-shedding manager — public API.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Integrates the INA226 current monitors on Kaylee and the BQ76930 cell
 * monitor to provide a unified power fault state machine for the Serenity UAV.
 *
 * The fault manager runs as a periodic task on the primary FC node (FC1).
 * It polls all INA226 current sensors and the BQ76930 at the rates defined
 * by PWR_FAULT_POLL_HZ and PWR_FAULT_CELL_POLL_HZ, computes the system
 * power state, and broadcasts the state on CAN FD.
 *
 * ── State machine ─────────────────────────────────────────────────────────
 *
 *   NORMAL ──→ WARN ──→ CRITICAL ──→ EMERGENCY
 *              ←─────────────────────────────── (hysteresis)
 *
 * State transitions are governed by voltage and current thresholds defined
 * in this header.  Hysteresis of PWR_FAULT_HYST_MV prevents chattering on
 * transitions.
 *
 * ── Load shedding ─────────────────────────────────────────────────────────
 *
 * On entering CRITICAL, the manager sends GPIO / CAN FD commands to disable
 * non-essential loads in order of PWR_FAULT_SHED_* priority constants.
 * On EMERGENCY, all non-propulsion loads are disabled and the EDF throttle
 * is capped at PWR_FAULT_EMERGENCY_THROTTLE_PCT.
 *
 * ── CAN FD broadcast ──────────────────────────────────────────────────────
 *
 * Power state is broadcast on CAN FD frame ID 0x020 (PWR_FAULT_CANFD_ID)
 * at PWR_FAULT_BCAST_HZ regardless of state.  State changes also trigger
 * an immediate additional broadcast.
 *
 * Frame layout (8 bytes):
 *   Byte 0    : pwr_fault_state_t (current state)
 *   Bytes 1–2 : pack voltage mV (uint16_t, big-endian)
 *   Byte 3    : minimum cell voltage / 10 mV (uint8_t, 0–255 = 0–2550 mV)
 *   Byte 4    : main bus current A (uint8_t, saturated at 255)
 *   Bytes 5–6 : per-ESC current bitmap × 4 (2 bits per ESC: 0=OK 1=WARN 2=CRIT 3=FAULT)
 *   Byte 7    : BQ76930 SYS_STAT register snapshot
 *
 * References:
 *   [1] docs/POWER_DISTRIBUTION.md — Serenity UAV power design document.
 *   [2] bmon_ina2xx.h — INA226 driver API.
 *   [3] cell_mon_bq769x0.h — BQ76930 driver API.
 *
 * Target platform: PocketBeagle 2 Industrial (AM6254), Debian Trixie.
 */

#ifndef PWR_FAULT_H
#define PWR_FAULT_H

#include "bmon_ina2xx.h"
#include "cell_mon_bq769x0.h"
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ---------------------------------------------------------------------------
 * Number of Kaylee ESC current monitor channels
 * ---------------------------------------------------------------------------*/

/** Number of ESC current channels on Kaylee (Phases 5–10; ESC5 is Phase 11). */
#define PWR_FAULT_ESC_COUNT         (4U)

/* ---------------------------------------------------------------------------
 * Poll rates
 * ---------------------------------------------------------------------------*/

/** INA226 poll frequency (Hz). */
#define PWR_FAULT_POLL_HZ           (10U)

/** BQ76930 cell-level poll frequency (Hz). */
#define PWR_FAULT_CELL_POLL_HZ      (1U)

/** CAN FD power-state broadcast frequency (Hz). */
#define PWR_FAULT_BCAST_HZ          (2U)

/* ---------------------------------------------------------------------------
 * Voltage thresholds (per cell, millivolts)
 * See docs/POWER_DISTRIBUTION.md §8.1
 * ---------------------------------------------------------------------------*/

/** Cell voltage below which WARN state is entered (mV). */
#define PWR_FAULT_CELL_WARN_MV      (3500U)

/** Cell voltage below which CRITICAL state is entered (mV). */
#define PWR_FAULT_CELL_CRITICAL_MV  (3300U)

/** Cell voltage below which EMERGENCY state is entered (mV). */
#define PWR_FAULT_CELL_EMERG_MV     (3000U)

/** Hysteresis for downward state transition (mV). */
#define PWR_FAULT_HYST_MV           (100U)

/* ---------------------------------------------------------------------------
 * Pack-level voltage thresholds (millivolts)
 * ---------------------------------------------------------------------------*/

/** Pack voltage below which WARN state is entered (mV). */
#define PWR_FAULT_PACK_WARN_MV      (21000U)

/** Pack voltage below which CRITICAL state is entered (mV). */
#define PWR_FAULT_PACK_CRITICAL_MV  (19800U)

/** Pack voltage below which EMERGENCY state is entered (mV). */
#define PWR_FAULT_PACK_EMERG_MV     (18000U)

/* ---------------------------------------------------------------------------
 * Current thresholds (milliamps)
 * See docs/POWER_DISTRIBUTION.md §8.2
 * ---------------------------------------------------------------------------*/

/** Per-ESC current threshold for WARN (mA). */
#define PWR_FAULT_ESC_WARN_MA       (35000U)

/**
 * Per-ESC sustained current threshold for CRITICAL (mA).
 * Fault latches after PWR_FAULT_ESC_CRITICAL_DURATION_MS continuous exceedance.
 */
#define PWR_FAULT_ESC_CRITICAL_MA   (40000U)

/** Duration ESC current must exceed PWR_FAULT_ESC_CRITICAL_MA before latching (ms). */
#define PWR_FAULT_ESC_CRITICAL_DURATION_MS (5000U)

/** Per-ESC instantaneous burst threshold — immediate DSHOT disarm (mA). */
#define PWR_FAULT_ESC_BURST_MA      (55000U)

/** Main bus WARN threshold (mA). */
#define PWR_FAULT_MAIN_WARN_MA      (65000U)

/** Main bus CRITICAL threshold (mA, sustained). */
#define PWR_FAULT_MAIN_CRITICAL_MA  (75000U)

/* ---------------------------------------------------------------------------
 * Emergency throttle cap
 * ---------------------------------------------------------------------------*/

/**
 * Maximum EDF throttle percentage allowed in EMERGENCY state (%).
 * Thrust at 70% throttle ≈ 49% of max (T ∝ throttle²); results in
 * T/W < 1.0 requiring transition to fixed-wing descent / RTH profile.
 */
#define PWR_FAULT_EMERGENCY_THROTTLE_PCT (70U)

/* ---------------------------------------------------------------------------
 * CAN FD frame parameters
 * ---------------------------------------------------------------------------*/

/** CAN FD frame ID for power-state broadcast (11-bit standard ID). */
#define PWR_FAULT_CANFD_ID          (0x020U)

/* ---------------------------------------------------------------------------
 * Data types
 * ---------------------------------------------------------------------------*/

/**
 * @brief Power system fault state.
 *
 * Values are ordered by severity so that integer comparison identifies
 * the higher-severity state.
 */
typedef enum {
    PWR_STATE_NORMAL    = 0, /**< All parameters within normal limits. */
    PWR_STATE_WARN      = 1, /**< One or more parameters approaching limits. */
    PWR_STATE_CRITICAL  = 2, /**< Limit exceeded; load shedding initiated. */
    PWR_STATE_EMERGENCY = 3, /**< Emergency: throttle capped; RTH active. */
} pwr_fault_state_t;

/**
 * @brief Per-ESC fault sub-state.
 */
typedef enum {
    ESC_OK      = 0, /**< Current within normal range. */
    ESC_WARN    = 1, /**< Current above PWR_FAULT_ESC_WARN_MA. */
    ESC_CRIT    = 2, /**< Current above PWR_FAULT_ESC_CRITICAL_MA for > duration. */
    ESC_DISARMED = 3, /**< ESC disarmed by fault manager. */
} pwr_esc_fault_t;

/**
 * @brief Snapshot of the full power system state.
 */
typedef struct {
    pwr_fault_state_t state;                        /**< System-level power state. */
    uint32_t          pack_mv;                      /**< Pack voltage (mV). */
    uint32_t          min_cell_mv;                  /**< Minimum cell voltage (mV). */
    uint32_t          max_cell_mv;                  /**< Maximum cell voltage (mV). */
    int32_t           esc_current_ma[PWR_FAULT_ESC_COUNT]; /**< Per-ESC current (mA). */
    int32_t           main_current_ma;              /**< Main bus current (mA). */
    pwr_esc_fault_t   esc_fault[PWR_FAULT_ESC_COUNT];      /**< Per-ESC fault sub-state. */
    uint8_t           bq769x0_stat;                 /**< BQ76930 SYS_STAT snapshot. */
    int32_t           temp_decidegc;                /**< Battery temperature (°C × 10). */
} pwr_fault_snapshot_t;

/**
 * @brief Manager context.  Initialise with pwr_fault_open(); release with pwr_fault_close().
 */
typedef struct pwr_fault_ctx pwr_fault_ctx_t;

/* ---------------------------------------------------------------------------
 * API
 * ---------------------------------------------------------------------------*/

/**
 * @brief Initialise the power fault manager.
 *
 * Opens INA226 devices on the PDB I2C bus (i2c_dev_pdb) and the BQ76930
 * cell monitor (same bus).  Configures each INA226 for current-sense mode
 * using the shunt and full-scale values from docs/POWER_DISTRIBUTION.md.
 *
 * ESC INA226 devices are at I2C addresses 0x40–0x43 (ESC1–ESC4).
 * Main bus INA226 is at 0x44.  BQ76930 is at 0x08.
 *
 * @param[in]  i2c_dev_pdb  Path to the I2C bus connected to Kaylee monitors
 *                          (e.g. "/dev/i2c-2"; Cape-A-2 Bay A J_EXT_I2C).
 * @param[out] ctx_out      Set to the manager context on success.
 * @return 0 on success, negative errno on error.
 */
int pwr_fault_open(const char *i2c_dev_pdb, pwr_fault_ctx_t **ctx_out);

/**
 * @brief Release the power fault manager and close all I2C connections.
 *
 * @param[in] ctx  Manager context.  May be NULL (no-op).
 */
void pwr_fault_close(pwr_fault_ctx_t *ctx);

/**
 * @brief Poll all power monitors and update the fault state machine.
 *
 * Call this function at PWR_FAULT_POLL_HZ (10 Hz) from the FC node main loop.
 * It performs the following operations on each call:
 *
 *   1. Reads all INA226 current and voltage registers.
 *   2. Reads BQ76930 cell voltages (on every PWR_FAULT_POLL_HZ /
 *      PWR_FAULT_CELL_POLL_HZ calls; i.e. every 10th call at 10 Hz / 1 Hz).
 *   3. Evaluates voltage and current thresholds to determine fault state.
 *   4. Applies load shedding commands if state has worsened.
 *   5. Calls shed_fn and bcast_fn callbacks if provided at open.
 *   6. Updates snapshot.
 *
 * @param[in] ctx  Manager context.
 * @return 0 on successful poll, -EINVAL on NULL ctx.
 *         I2C errors during polling are logged internally and reflected
 *         in pwr_fault_get_snapshot() esc_current_ma values (set to −1).
 */
int pwr_fault_poll(pwr_fault_ctx_t *ctx);

/**
 * @brief Return a snapshot of the most recent power state.
 *
 * Thread-safe if the caller ensures no concurrent pwr_fault_poll() call.
 *
 * @param[in]  ctx   Manager context.
 * @param[out] snap  Destination for snapshot copy.
 * @return 0 on success, -EINVAL on NULL args.
 */
int pwr_fault_get_snapshot(const pwr_fault_ctx_t *ctx, pwr_fault_snapshot_t *snap);

/**
 * @brief Encode the current snapshot into the 8-byte CAN FD frame payload.
 *
 * Formats the frame per the layout documented in the header comment.
 * buf must be at least 8 bytes.
 *
 * @param[in]  ctx  Manager context.
 * @param[out] buf  Output buffer (8 bytes).
 * @return 0 on success, -EINVAL on NULL args.
 */
int pwr_fault_encode_canfd(const pwr_fault_ctx_t *ctx, uint8_t buf[8]);

/**
 * @brief Register a load-shedding callback.
 *
 * The callback is invoked by pwr_fault_poll() whenever the power state
 * changes to a higher severity level.  Use it to disable GPIO-controlled
 * loads (LEDs, WiFi, cargo winch) as appropriate for the new state.
 *
 * @param[in] ctx      Manager context.
 * @param[in] shed_fn  Callback: fn(new_state, user_data).  May be NULL to
 *                     deregister.
 * @param[in] user_data  Opaque pointer passed through to shed_fn.
 */
void pwr_fault_set_shed_callback(pwr_fault_ctx_t   *ctx,
                                 void (*shed_fn)(pwr_fault_state_t new_state,
                                                 void             *user_data),
                                 void              *user_data);

#ifdef __cplusplus
}
#endif

#endif /* PWR_FAULT_H */
