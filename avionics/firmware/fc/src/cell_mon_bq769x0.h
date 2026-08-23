/**
 * @file    cell_mon_bq769x0.h
 * @brief   BQ76920 / BQ76930 / BQ76940 Li-ion cell monitor driver — public API.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Drives the Texas Instruments BQ76930PWRQ1 on the Flight Engineer power
 * distribution board via Linux userspace i2c-dev.  The BQ76930 monitors 6–10
 * series LiPo cells and provides per-cell OVP, UVP, OCD, and SCD hardware
 * protection.
 *
 * This driver is configured for the Serenity UAV 6S (6-cell) application
 * but can support 9S and 15S with the BQ76930 and BQ76940 respectively
 * by adjusting CELL_MON_CELL_COUNT.
 *
 * ── Communication — CRC mode ──────────────────────────────────────────────
 *
 * The BQ76930 supports I2C with optional CRC-8 error checking.  CRC mode is
 * selected by the hardware CHEM / DFSEL pin configuration at power-on.
 * On Flight Engineer, CRC mode IS enabled (DFSEL tied appropriately during
 * board layout).
 *
 * In CRC mode every I2C transaction includes an 8-bit CRC byte:
 *   Write: [ADDR_W][REG][DATA][CRC]
 *   Read:  [ADDR_W][REG] then [ADDR_R][DATA][CRC]
 *
 * CRC polynomial: x^8 + x^2 + x + 1 (0x07 representation).
 * CRC is calculated over all bytes in the transaction including the address
 * byte.
 *
 * ── Cell voltage calculation ───────────────────────────────────────────────
 *
 * Cell voltage registers (0x0C–0x1A, two bytes per cell) store a 14-bit ADC
 * result.  The actual cell voltage is:
 *
 *   V_cell_uV = (uint16_t)(VC_n_HI << 8 | VC_n_LO) × GAIN + OFFSET
 *
 * where GAIN (µV/LSB, register 0x50) and OFFSET (mV, register 0x51) are
 * device-specific trimmed calibration values read from the IC at open time.
 *
 * ── ALERT output ──────────────────────────────────────────────────────────
 *
 * The BQ76930 open-drain ALERT pin is connected to Pilot GPIO.  On any
 * hardware fault (OVP, UVP, OCD, SCD) the ALERT pin asserts LOW.  Firmware
 * should configure a falling-edge GPIO interrupt and call
 * cell_mon_read_status() from the interrupt service thread.
 *
 * ── DSG / CHG FET control ─────────────────────────────────────────────────
 *
 * The BQ76930 DSG (discharge) and CHG (charge) output pins drive the gate
 * of Q_BATT_DSG / Q_BATT_CHG MOSFETs on FlightEngineer.  In normal operation,
 * both FETs are ON (driven by firmware via SYS_CTRL2 CHG_ON / DSG_ON bits). On
 * any hardware protection trigger, the BQ76930 independently asserts the
 * appropriate FET gate OFF without firmware intervention.
 *
 * References:
 *   [1] BQ76930 Datasheet SLUSBB2C, Texas Instruments.
 *       https://www.ti.com/lit/ds/symlink/bq76930.pdf
 *   [2] BQ76920/30/40 EVM User Guide SLUU431, TI.
 *   [3] FlightEngineer.md — Serenity UAV Power Distribution Board
 * specification.
 *
 * Target platform: PocketBeagle 2 Industrial (AM6254), Debian Trixie.
 */

#ifndef CELL_MON_BQ769X0_H
#define CELL_MON_BQ769X0_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ---------------------------------------------------------------------------
 * Device I2C address
 * ---------------------------------------------------------------------------*/

/**
 * BQ76930 I2C address (7-bit) when CRC mode is enabled and CHEM pin selects
 * the default address.  On Flight Engineer this is 0x08.
 */
#define CELL_MON_I2C_ADDR          (0x08U)

/* ---------------------------------------------------------------------------
 * Application constants — adjust for cell count variant
 * ---------------------------------------------------------------------------*/

/** Number of series cells in the Serenity UAV battery pack. */
#define CELL_MON_CELL_COUNT        (6U)

/** Overvoltage protection threshold per cell (millivolts). */
#define CELL_MON_OVP_MV            (4200U)

/** Undervoltage protection threshold per cell (millivolts). */
#define CELL_MON_UVP_MV            (3000U)

/** Overcurrent detection threshold (milliamps). */
#define CELL_MON_OCD_MA            (50000U)

/** Short-circuit detection threshold (milliamps). */
#define CELL_MON_SCD_MA            (150000U)

/** Over-temperature threshold (°C × 10, for integer arithmetic). */
#define CELL_MON_OTP_DECIDEGC      (600) /* 60.0 °C */

/* ---------------------------------------------------------------------------
 * Register addresses
 * ---------------------------------------------------------------------------*/

/** Status register — OCD, SCD, OV, UV, OVRD_ALERT, DEVICE_XREADY. */
#define BQ769X0_REG_SYS_STAT       (0x00U)

/** Cell balancing 1 register — balance switches for cells 1–5. */
#define BQ769X0_REG_CELLBAL1       (0x01U)

/** System control 1 — TEMP_SEL, ADC_EN, SHUT_A, SHUT_B. */
#define BQ769X0_REG_SYS_CTRL1      (0x04U)

/** System control 2 — DELAY_DIS, CC_EN, CC_ONESHOT, CHG_ON, DSG_ON. */
#define BQ769X0_REG_SYS_CTRL2      (0x05U)

/** Overcurrent and short-circuit protection 1. */
#define BQ769X0_REG_PROTECT1       (0x06U)

/** Overcurrent protection 2. */
#define BQ769X0_REG_PROTECT2       (0x07U)

/** Overvoltage / undervoltage protection delays. */
#define BQ769X0_REG_PROTECT3       (0x08U)

/** Overvoltage trip threshold register. */
#define BQ769X0_REG_OV_TRIP        (0x09U)

/** Undervoltage trip threshold register. */
#define BQ769X0_REG_UV_TRIP        (0x0AU)

/** Coulomb counter configuration (always write 0x19). */
#define BQ769X0_REG_CC_CFG         (0x0BU)

/** Cell voltage registers: VC1_HI=0x0C, VC1_LO=0x0D, ... VC6_LO=0x1A. */
#define BQ769X0_REG_VC1_HI         (0x0CU)

/** Pack voltage high byte. */
#define BQ769X0_REG_BAT_HI         (0x2AU)

/** Pack voltage low byte. */
#define BQ769X0_REG_BAT_LO         (0x2BU)

/** Temperature sensor 1 high byte. */
#define BQ769X0_REG_TS1_HI         (0x2CU)

/** Temperature sensor 1 low byte. */
#define BQ769X0_REG_TS1_LO         (0x2DU)

/** Coulomb counter high byte. */
#define BQ769X0_REG_CC_HI          (0x32U)

/** Coulomb counter low byte. */
#define BQ769X0_REG_CC_LO          (0x33U)

/** ADC gain trim register (µV/LSB offset from 365 µV). */
#define BQ769X0_REG_ADCGAIN1       (0x50U)

/** ADC gain trim register 2. */
#define BQ769X0_REG_ADCGAIN2       (0x59U)

/** ADC offset trim register (signed mV). */
#define BQ769X0_REG_ADCOFFSET      (0x51U)

/* ---------------------------------------------------------------------------
 * SYS_STAT bit masks
 * ---------------------------------------------------------------------------*/

/** SYS_STAT: overcurrent-in-discharge detected. */
#define BQ769X0_STAT_OCD           (0x01U)

/** SYS_STAT: short-circuit-in-discharge detected. */
#define BQ769X0_STAT_SCD           (0x02U)

/** SYS_STAT: overvoltage detected on at least one cell. */
#define BQ769X0_STAT_OV            (0x04U)

/** SYS_STAT: undervoltage detected on at least one cell. */
#define BQ769X0_STAT_UV            (0x08U)

/** SYS_STAT: OVRD_ALERT (externally triggered alert). */
#define BQ769X0_STAT_OVRD_ALERT    (0x10U)

/** SYS_STAT: DEVICE_XREADY (internal fault, should not occur). */
#define BQ769X0_STAT_DEVICE_XREADY (0x20U)

/** SYS_STAT: CC_READY (coulomb counter data is ready). */
#define BQ769X0_STAT_CC_READY      (0x80U)

/* ---------------------------------------------------------------------------
 * Data types
 * ---------------------------------------------------------------------------*/

/**
 * @brief Driver context.  Initialise with cell_mon_open(); release with
 * cell_mon_close().
 */
typedef struct cell_mon_ctx cell_mon_ctx_t;

/**
 * @brief Cell voltage measurement set for all cells in the pack.
 */
typedef struct {
    uint32_t
        cell_mv[CELL_MON_CELL_COUNT]; /**< Per-cell voltage in millivolts. */
    uint32_t pack_mv;                 /**< Pack total voltage in millivolts. */
    int32_t  temp_decidegc;           /**< Battery temperature in °C × 10. */
    uint8_t  sys_stat;                /**< Last SYS_STAT register snapshot. */
} cell_mon_data_t;

/* ---------------------------------------------------------------------------
 * API
 * ---------------------------------------------------------------------------*/

/**
 * @brief Open the BQ769x0 driver and configure the device.
 *
 * Opens the I2C bus, reads ADCGAIN and ADCOFFSET calibration trimming from
 * the device, writes the default protection registers (OVP, UVP, OCD, SCD,
 * OTP thresholds from the CELL_MON_* constants), enables ADC and coulomb
 * counter, and enables CHG_ON / DSG_ON to turn on the power path FETs.
 *
 * @param[in]  i2c_dev  Path to I2C bus device (e.g. "/dev/i2c-2").
 * @param[out] ctx_out  Set to driver context on success.
 * @return 0 on success, negative errno on error:
 *         -EINVAL : i2c_dev or ctx_out is NULL.
 *         -ENOMEM : memory allocation failed.
 *         -EIO    : I2C communication error.
 *         -EPROTO : CRC mismatch on initial register reads.
 */
int cell_mon_open(const char *i2c_dev, cell_mon_ctx_t **ctx_out);

/**
 * @brief Close the driver and release resources.
 *
 * Does NOT disable DSG/CHG FETs — the power path remains active after close.
 * Call cell_mon_set_dsg() / cell_mon_set_chg() explicitly before close if
 * intentional FET disable is required.
 *
 * @param[in] ctx  Driver context.  May be NULL (no-op).
 */
void cell_mon_close(cell_mon_ctx_t *ctx);

/**
 * @brief Read all cell voltages, pack voltage, and temperature.
 *
 * Reads VC1–VC6, BAT, TS1 registers and converts using the calibrated GAIN
 * and OFFSET.  Also snapshots SYS_STAT into data->sys_stat.
 *
 * @param[in]  ctx   Driver context.
 * @param[out] data  Measurement results.
 * @return 0 on success, -EINVAL on NULL args, -EIO on I2C error,
 *         -EPROTO on CRC mismatch.
 */
int cell_mon_read(cell_mon_ctx_t *ctx, cell_mon_data_t *data);

/**
 * @brief Read the raw SYS_STAT register.
 *
 * Use to detect and identify hardware protection events (OVP, UVP, OCD, SCD).
 * Check individual bits against BQ769X0_STAT_* constants.
 *
 * @param[in]  ctx      Driver context.
 * @param[out] stat_out SYS_STAT register value.
 * @return 0 on success, -EINVAL on NULL, -EIO or -EPROTO on error.
 */
int cell_mon_read_status(cell_mon_ctx_t *ctx, uint8_t *stat_out);

/**
 * @brief Clear one or more SYS_STAT fault flags.
 *
 * Writes a mask of flag bits to SYS_STAT to clear them.  Per BQ769x0
 * datasheet, writing a 1 to a status bit clears it; writing 0 has no effect.
 *
 * @param[in] ctx      Driver context.
 * @param[in] clr_mask Bitmask of BQ769X0_STAT_* bits to clear.
 * @return 0 on success, -EINVAL on NULL, -EIO or -EPROTO on error.
 */
int cell_mon_clear_faults(cell_mon_ctx_t *ctx, uint8_t clr_mask);

/**
 * @brief Enable or disable the discharge path FET (DSG).
 *
 * Sets or clears the DSG_ON bit in SYS_CTRL2.  Call with enable=false to
 * disconnect the discharge path (propulsion power off) in an emergency.
 * Note: the BQ76930 hardware protection may also assert this independently.
 *
 * @param[in] ctx    Driver context.
 * @param[in] enable true to enable DSG FET; false to disable (open circuit).
 * @return 0 on success, -EINVAL on NULL ctx, -EIO or -EPROTO on error.
 */
int cell_mon_set_dsg(cell_mon_ctx_t *ctx, int enable);

/**
 * @brief Return the minimum cell voltage across all monitored cells.
 *
 * Convenience wrapper: scans data->cell_mv[0..CELL_MON_CELL_COUNT-1] and
 * returns the lowest value.
 *
 * @param[in] data  Measurement data from cell_mon_read().
 * @return Minimum cell voltage in millivolts, or 0 if data is NULL.
 */
uint32_t cell_mon_min_cell_mv(const cell_mon_data_t *data);

/**
 * @brief Return the maximum cell voltage across all monitored cells.
 *
 * @param[in] data  Measurement data from cell_mon_read().
 * @return Maximum cell voltage in millivolts, or 0 if data is NULL.
 */
uint32_t cell_mon_max_cell_mv(const cell_mon_data_t *data);

#ifdef __cplusplus
}
#endif

#endif /* CELL_MON_BQ769X0_H */
