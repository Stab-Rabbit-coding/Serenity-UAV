/**
 * @file    pwr_fault.c
 * @brief   Power fault monitor and load-shedding manager — implementation.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Implements the power fault state machine described in pwr_fault.h.
 *
 * INA226 I2C address layout on Kaylee (all on i2c_dev_pdb bus):
 *   0x40 — ESC1 (Port Fwd, EDF0)
 *   0x41 — ESC2 (Port Aft,  EDF1)
 *   0x42 — ESC3 (Stbd Fwd,  EDF2)
 *   0x43 — ESC4 (Stbd Aft,  EDF3)
 *   0x44 — Main bus monitor
 *   0x08 — BQ76930 cell monitor
 *
 * Shunt resistor values (see Kaylee.md §INA226 Calibration):
 *   ESC channels: 1 mΩ, I_max = 60 A
 *   Main bus:     1 mΩ, I_max = 75 A
 *
 * References:
 *   [1] pwr_fault.h — API and threshold documentation.
 *   [2] docs/POWER_DISTRIBUTION.md — load analysis and fault matrix.
 *
 * Target platform: PocketBeagle 2 Industrial (AM6254), Debian Trixie.
 */

#include "pwr_fault.h"

#include <errno.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

/* ---------------------------------------------------------------------------
 * INA226 I2C addresses and shunt configuration
 * ---------------------------------------------------------------------------*/

/** I2C addresses for ESC current monitors on Kaylee. */
static const uint8_t ESC_I2C_ADDR[PWR_FAULT_ESC_COUNT] = {0x40U, 0x41U, 0x42U,
                                                          0x43U};

/** I2C address for main bus current monitor. */
#define MAIN_BUS_I2C_ADDR (0x44U)

/** Shunt resistance for ESC monitors (mΩ). */
#define ESC_SHUNT_MOHM    (1U)

/** Maximum current for ESC monitors (mA). */
#define ESC_IMAX_MA       (60000U)

/** Shunt resistance for main bus monitor (mΩ). */
#define MAIN_SHUNT_MOHM   (1U)

/** Maximum current for main bus monitor (mA). */
#define MAIN_IMAX_MA      (75000U)

/* ---------------------------------------------------------------------------
 * Poll divisor for cell monitor
 * Evaluated every CELL_DIVISOR calls to pwr_fault_poll().
 * ---------------------------------------------------------------------------*/
#define CELL_POLL_DIVISOR (PWR_FAULT_POLL_HZ / PWR_FAULT_CELL_POLL_HZ)

/* ---------------------------------------------------------------------------
 * Internal context
 * ---------------------------------------------------------------------------*/

struct pwr_fault_ctx {
    /* INA226 driver contexts: [0..PWR_FAULT_ESC_COUNT-1] = ESC,
     * [PWR_FAULT_ESC_COUNT] = main. */
    bmon_ina2xx_ctx_t *ina[PWR_FAULT_ESC_COUNT + 1U];

    /* BQ76930 cell monitor. */
    cell_mon_ctx_t *cell;

    /* Snapshot of most recent measurement. */
    pwr_fault_snapshot_t snap;

    /* Current fault state. */
    pwr_fault_state_t state;

    /* Per-ESC sustained-overcurrent timer (ms-equivalent poll count). */
    uint32_t esc_overcurrent_ticks[PWR_FAULT_ESC_COUNT];

    /* Poll counter for cell-monitor decimation. */
    uint32_t poll_count;

    /* Load-shedding callback. */
    void (*shed_fn)(pwr_fault_state_t, void *);
    void *shed_user_data;
};

/* ---------------------------------------------------------------------------
 * Internal helpers
 * ---------------------------------------------------------------------------*/

/**
 * @brief Evaluate voltage-based fault state from snapshot values.
 *
 * Returns the severity level implied by the current pack/cell voltages,
 * WITHOUT applying hysteresis (hysteresis is applied at the transition site).
 */
static pwr_fault_state_t voltage_state(const pwr_fault_snapshot_t *snap) {
    uint32_t min_cell = snap->min_cell_mv;
    uint32_t pack = snap->pack_mv;

    if (min_cell < PWR_FAULT_CELL_EMERG_MV || pack < PWR_FAULT_PACK_EMERG_MV) {
        return PWR_STATE_EMERGENCY;
    }
    if (min_cell < PWR_FAULT_CELL_CRITICAL_MV ||
        pack < PWR_FAULT_PACK_CRITICAL_MV) {
        return PWR_STATE_CRITICAL;
    }
    if (min_cell < PWR_FAULT_CELL_WARN_MV || pack < PWR_FAULT_PACK_WARN_MV) {
        return PWR_STATE_WARN;
    }
    return PWR_STATE_NORMAL;
}

/**
 * @brief Evaluate current-based fault state from snapshot values.
 */
static pwr_fault_state_t current_state(const pwr_fault_snapshot_t *snap) {
    uint32_t i;

    if (snap->main_current_ma > (int32_t)PWR_FAULT_MAIN_CRITICAL_MA) {
        return PWR_STATE_CRITICAL;
    }
    if (snap->main_current_ma > (int32_t)PWR_FAULT_MAIN_WARN_MA) {
        return PWR_STATE_WARN;
    }

    for (i = 0U; i < PWR_FAULT_ESC_COUNT; i++) {
        if (snap->esc_fault[i] == ESC_DISARMED) {
            return PWR_STATE_CRITICAL;
        }
        if (snap->esc_fault[i] == ESC_CRIT) {
            return PWR_STATE_CRITICAL;
        }
        if (snap->esc_fault[i] == ESC_WARN) {
            return PWR_STATE_WARN;
        }
    }
    return PWR_STATE_NORMAL;
}

/**
 * @brief Apply hysteresis when transitioning to a lower severity state.
 *
 * A state transition downward requires that the triggering voltage recover by
 * PWR_FAULT_HYST_MV above the threshold that caused the transition.
 *
 * Implemented by raising the effective transition threshold: if the computed
 * new state is below current, only allow the transition if min_cell exceeds
 * the current-level threshold + hysteresis.
 */
static pwr_fault_state_t apply_hysteresis(pwr_fault_state_t current,
                                          pwr_fault_state_t computed,
                                          uint32_t          min_cell_mv) {
    uint32_t hyst_threshold_mv;

    if (computed >= current) {
        /* Worsening or unchanged — no hysteresis needed. */
        return computed;
    }

    /* Determine the voltage that would exit the current state with hysteresis.
     */
    switch (current) {
        case PWR_STATE_EMERGENCY:
            hyst_threshold_mv = PWR_FAULT_CELL_EMERG_MV + PWR_FAULT_HYST_MV;
            break;
        case PWR_STATE_CRITICAL:
            hyst_threshold_mv = PWR_FAULT_CELL_CRITICAL_MV + PWR_FAULT_HYST_MV;
            break;
        case PWR_STATE_WARN:
            hyst_threshold_mv = PWR_FAULT_CELL_WARN_MV + PWR_FAULT_HYST_MV;
            break;
        default:
            return computed;
    }

    if (min_cell_mv < hyst_threshold_mv) {
        /* Voltage has not recovered enough to leave current state. */
        return current;
    }
    return computed;
}

/* ---------------------------------------------------------------------------
 * Public API
 * ---------------------------------------------------------------------------*/

int pwr_fault_open(const char *i2c_dev_pdb, pwr_fault_ctx_t **ctx_out) {
    pwr_fault_ctx_t *ctx;
    uint32_t         i;
    int              rc;

    if (i2c_dev_pdb == NULL || ctx_out == NULL) {
        return -EINVAL;
    }

    ctx = calloc(1U, sizeof(*ctx));
    if (ctx == NULL) {
        return -ENOMEM;
    }

    /* Open INA226 contexts for each ESC channel. */
    for (i = 0U; i < PWR_FAULT_ESC_COUNT; i++) {
        /*
         * Each INA226 on the Kaylee shares the same I2C bus but has a distinct
         * address (0x40–0x43 for ESC1–ESC4).  Each bmon_ina2xx_open() call
         * opens a separate file descriptor and programs the address via
         * ioctl I2C_SLAVE, so all contexts are fully independent.
         */
        rc = bmon_ina2xx_open(i2c_dev_pdb, ESC_I2C_ADDR[i], BMON_INA_INA226,
                              &ctx->ina[i]);
        if (rc != 0) {
            goto fail;
        }

        rc = bmon_ina226_configure_shunt(ctx->ina[i], ESC_SHUNT_MOHM,
                                         ESC_IMAX_MA, NULL);
        if (rc != 0) {
            goto fail;
        }

        /* Alert: overcurrent at 55 A (burst limit). */
        {
            /*
             * SOL alert limit for INA226:
             *   raw = I_limit_ma / current_lsb_ma
             *   current_lsb_ma = ESC_IMAX_MA / 32768 ≈ 1.831 mA
             *   I_limit = 55000 mA; raw = 55000 / 1.831 ≈ 30038
             */
            uint16_t alert_raw = (uint16_t)((55000UL * 32768UL) / ESC_IMAX_MA);
            rc = bmon_ina226_configure_alert(
                ctx->ina[i], INA226_MASK_SOL | INA226_MASK_LEN, alert_raw);
            if (rc != 0) {
                goto fail;
            }
        }
    }

    /* Open main bus INA226 (address 0x44). */
    rc = bmon_ina2xx_open(i2c_dev_pdb, MAIN_BUS_I2C_ADDR, BMON_INA_INA226,
                          &ctx->ina[PWR_FAULT_ESC_COUNT]);
    if (rc != 0) {
        goto fail;
    }
    rc = bmon_ina226_configure_shunt(ctx->ina[PWR_FAULT_ESC_COUNT],
                                     MAIN_SHUNT_MOHM, MAIN_IMAX_MA, NULL);
    if (rc != 0) {
        goto fail;
    }

    /* Open BQ76930 cell monitor. */
    rc = cell_mon_open(i2c_dev_pdb, &ctx->cell);
    if (rc != 0) {
        goto fail;
    }

    /* Initialise state. */
    ctx->state = PWR_STATE_NORMAL;
    ctx->poll_count = 0U;
    memset(&ctx->snap, 0, sizeof(ctx->snap));
    ctx->snap.state = PWR_STATE_NORMAL;

    *ctx_out = ctx;
    return 0;

fail:
    pwr_fault_close(ctx);
    return rc;
}

void pwr_fault_close(pwr_fault_ctx_t *ctx) {
    uint32_t i;

    if (ctx == NULL) {
        return;
    }

    for (i = 0U; i < (PWR_FAULT_ESC_COUNT + 1U); i++) {
        if (ctx->ina[i] != NULL) {
            bmon_ina2xx_close(ctx->ina[i]);
            ctx->ina[i] = NULL;
        }
    }

    if (ctx->cell != NULL) {
        cell_mon_close(ctx->cell);
        ctx->cell = NULL;
    }

    free(ctx);
}

int pwr_fault_poll(pwr_fault_ctx_t *ctx) {
    uint32_t          i;
    pwr_fault_state_t new_state;
    pwr_fault_state_t v_state;
    pwr_fault_state_t c_state;
    int               rc;

    if (ctx == NULL) {
        return -EINVAL;
    }

    ctx->poll_count++;

    /* ── INA226 reads ─────────────────────────────────────────────────── */

    for (i = 0U; i < PWR_FAULT_ESC_COUNT; i++) {
        int32_t  cur_ma = 0;
        uint32_t volt_mv = 0U;

        rc = bmon_ina2xx_read_mv(ctx->ina[i], &volt_mv);
        if (rc != 0) {
            cur_ma = -1; /* Sentinel for I2C error. */
        } else {
            rc = bmon_ina226_read_current_ma(ctx->ina[i], &cur_ma);
            if (rc != 0) {
                cur_ma = -1;
            }
        }

        ctx->snap.esc_current_ma[i] = cur_ma;

        /* Update ESC fault sub-state. */
        if (cur_ma < 0) {
            /* I2C error — preserve existing fault state. */
        } else if ((uint32_t)cur_ma >= PWR_FAULT_ESC_BURST_MA) {
            /* Instantaneous burst: disarm immediately. */
            ctx->snap.esc_fault[i] = ESC_DISARMED;
            ctx->esc_overcurrent_ticks[i] = 0U;
            /* Caller must send DSHOT disarm command. */
        } else if ((uint32_t)cur_ma >= PWR_FAULT_ESC_CRITICAL_MA) {
            ctx->esc_overcurrent_ticks[i]++;
            if (ctx->esc_overcurrent_ticks[i] >=
                (PWR_FAULT_ESC_CRITICAL_DURATION_MS /
                 (1000U / PWR_FAULT_POLL_HZ))) {
                ctx->snap.esc_fault[i] = ESC_CRIT;
            } else {
                ctx->snap.esc_fault[i] = ESC_WARN;
            }
        } else if ((uint32_t)cur_ma >= PWR_FAULT_ESC_WARN_MA) {
            ctx->esc_overcurrent_ticks[i] = 0U;
            ctx->snap.esc_fault[i] = ESC_WARN;
        } else {
            ctx->esc_overcurrent_ticks[i] = 0U;
            if (ctx->snap.esc_fault[i] != ESC_DISARMED) {
                /* Only clear if not latched as DISARMED. */
                ctx->snap.esc_fault[i] = ESC_OK;
            }
        }
    }

    /* Main bus current. */
    {
        int32_t  main_ma = 0;
        uint32_t volt_mv = 0U;

        rc = bmon_ina2xx_read_mv(ctx->ina[PWR_FAULT_ESC_COUNT], &volt_mv);
        if (rc == 0) {
            ctx->snap.pack_mv =
                volt_mv; /* Main bus voltage approximates pack voltage. */
            (void)bmon_ina226_read_current_ma(ctx->ina[PWR_FAULT_ESC_COUNT],
                                              &main_ma);
        }
        ctx->snap.main_current_ma = main_ma;
    }

    /* ── BQ76930 poll (decimated to PWR_FAULT_CELL_POLL_HZ) ──────────── */

    if ((ctx->poll_count % (uint32_t)CELL_POLL_DIVISOR) == 0U) {
        cell_mon_data_t cell_data;
        memset(&cell_data, 0, sizeof(cell_data));

        rc = cell_mon_read(ctx->cell, &cell_data);
        if (rc == 0) {
            ctx->snap.pack_mv = cell_data.pack_mv;
            ctx->snap.min_cell_mv = cell_mon_min_cell_mv(&cell_data);
            ctx->snap.max_cell_mv = cell_mon_max_cell_mv(&cell_data);
            ctx->snap.temp_decidegc = cell_data.temp_decidegc;
            ctx->snap.bq769x0_stat = cell_data.sys_stat;
        }

        /* If BQ76930 reports any hardware protection event, force EMERGENCY. */
        if ((ctx->snap.bq769x0_stat &
             (BQ769X0_STAT_OCD | BQ769X0_STAT_SCD | BQ769X0_STAT_UV)) != 0U) {
            /* Hardware protection has already tripped a FET. */
            ctx->state = PWR_STATE_EMERGENCY;
            ctx->snap.state = PWR_STATE_EMERGENCY;
        }
    }

    /* ── State evaluation ─────────────────────────────────────────────── */

    v_state = voltage_state(&ctx->snap);
    c_state = current_state(&ctx->snap);
    new_state = (v_state > c_state) ? v_state : c_state;

    /* Apply hysteresis on voltage when transitioning downward. */
    new_state = apply_hysteresis(ctx->state, new_state, ctx->snap.min_cell_mv);

    /* BQ76930 hardware OV flag should not force a state downgrade. */
    if ((ctx->snap.bq769x0_stat & BQ769X0_STAT_OV) != 0U) {
        if (new_state < PWR_STATE_WARN) {
            new_state = PWR_STATE_WARN;
        }
    }

    /* ── State transition ─────────────────────────────────────────────── */

    if (new_state != ctx->state) {
        pwr_fault_state_t old_state = ctx->state;
        ctx->state = new_state;
        ctx->snap.state = new_state;

        /* Invoke load-shedding callback on severity increase. */
        if (new_state > old_state && ctx->shed_fn != NULL) {
            ctx->shed_fn(new_state, ctx->shed_user_data);
        }
    } else {
        ctx->snap.state = ctx->state;
    }

    return 0;
}

int pwr_fault_get_snapshot(const pwr_fault_ctx_t *ctx,
                           pwr_fault_snapshot_t  *snap) {
    if (ctx == NULL || snap == NULL) {
        return -EINVAL;
    }
    memcpy(snap, &ctx->snap, sizeof(*snap));
    return 0;
}

int pwr_fault_encode_canfd(const pwr_fault_ctx_t *ctx, uint8_t buf[8]) {
    uint32_t i;
    uint16_t pack_mv_16;
    uint8_t  min_cell_10mv;
    uint8_t  main_a;
    uint8_t  esc_bits_hi;
    uint8_t  esc_bits_lo;

    if (ctx == NULL || buf == NULL) {
        return -EINVAL;
    }

    /* Byte 0: power state. */
    buf[0] = (uint8_t)ctx->snap.state;

    /* Bytes 1–2: pack voltage in mV (uint16_t big-endian, saturated at 65535).
     */
    pack_mv_16 = (ctx->snap.pack_mv > 65535U) ? (uint16_t)65535U
                                              : (uint16_t)ctx->snap.pack_mv;
    buf[1] = (uint8_t)(pack_mv_16 >> 8U);
    buf[2] = (uint8_t)(pack_mv_16 & 0xFFU);

    /* Byte 3: min cell voltage / 10 mV (0–255 represents 0–2550 mV). */
    min_cell_10mv = (ctx->snap.min_cell_mv > 2550U)
                        ? (uint8_t)255U
                        : (uint8_t)(ctx->snap.min_cell_mv / 10U);
    buf[3] = min_cell_10mv;

    /* Byte 4: main bus current in A (saturated at 255 A). */
    main_a = (ctx->snap.main_current_ma > 255000) ? (uint8_t)255U
             : (ctx->snap.main_current_ma < 0)
                 ? (uint8_t)0U
                 : (uint8_t)(ctx->snap.main_current_ma / 1000);
    buf[4] = main_a;

    /*
     * Bytes 5–6: per-ESC fault bitmap.
     * 2 bits per ESC (ESC1–ESC4): bits [7:6]=ESC1, [5:4]=ESC2 in byte 5;
     * [7:6]=ESC3, [5:4]=ESC4 in byte 6.
     */
    esc_bits_hi = 0U;
    esc_bits_lo = 0U;
    for (i = 0U; i < PWR_FAULT_ESC_COUNT; i++) {
        uint8_t fault_bits = (uint8_t)(ctx->snap.esc_fault[i] & 0x03U);
        if (i < 2U) {
            esc_bits_hi |= (uint8_t)(fault_bits << (6U - (i * 2U)));
        } else {
            esc_bits_lo |= (uint8_t)(fault_bits << (6U - ((i - 2U) * 2U)));
        }
    }
    buf[5] = esc_bits_hi;
    buf[6] = esc_bits_lo;

    /* Byte 7: BQ76930 SYS_STAT register snapshot. */
    buf[7] = ctx->snap.bq769x0_stat;

    return 0;
}

void pwr_fault_set_shed_callback(pwr_fault_ctx_t *ctx,
                                 void (*shed_fn)(pwr_fault_state_t, void *),
                                 void *user_data) {
    if (ctx == NULL) {
        return;
    }
    ctx->shed_fn = shed_fn;
    ctx->shed_user_data = user_data;
}
