/**
 * @file    bmon_ina2xx.h
 * @brief   INA219 / INA226 battery voltage / current monitor driver — public
 * API.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Drives the Texas Instruments INA219AIDR (Cape-A-1) and INA226AIDGSR
 * (Wash and FlightEngineer) via Linux userspace i2c-dev.
 *
 * Two operating modes are supported:
 *
 *   VOLTAGE-ONLY   Wash INA226 on-cape pack-voltage tap.
 *                  IN+ and IN− tied; no shunt; calibration register = 0.
 *
 *   CURRENT-SENSE  FlightEngineer INA226 devices (U_IS1–U_IS4, U_IS_MAIN).
 *                  IN+ / IN− across a Kelvin shunt resistor.
 *                  Call bmon_ina226_configure_shunt() after open() to program
 *                  the calibration register and unlock current / power reads.
 *
 * ── INA219AIDR (Cape-A-1) ─────────────────────────────────────────────────
 *
 *   I2C address : 0x40 (A0, A1 tied to GND)
 *   Bus voltage : 0–26 V, register 0x02, bits [15:3] = voltage / 4 mV.
 *   Resolution  : 4 mV per LSB in the voltage register.
 *   Configuration register 0x00 defaults to:
 *     PGA = ±320 mV, BADC = 12-bit, SADC = 12-bit, MODE = Continuous both
 *   Cape-A-1 usage: voltage-only; shunt disabled by tying IN+/IN−.
 *
 * ── INA226AIDGSR (Wash on-cape) ──────────────────────────────────────
 *
 *   I2C address : 0x40 (A0, A1 tied to GND)
 *   Bus voltage : 0–36 V, register 0x02, full 16-bit unsigned.
 *   Resolution  : 1.25 mV per LSB.
 *   die_id register 0xFF: always reads 0x2260.
 *   Manufacturer ID register 0xFE: reads 0x5449 ("TI").
 *   Wash usage: voltage-only (IN+ / IN− tied).
 *
 * ── INA226AIDGSR (FlightEngineer current monitors) ────────────────────────────────
 *
 *   I2C addresses: 0x40–0x44 (see FlightEngineer.md §INA226 Address Assignment).
 *   Shunt resistors: 1 mΩ (ESC channels, 60 A full scale),
 *                    1 mΩ (main bus, 75 A full scale).
 *   After bmon_ina226_configure_shunt() the following registers are valid:
 *     0x04 CURRENT_REG : signed 16-bit, LSB = CURRENT_LSB as programmed.
 *     0x05 CALIBRATION  : set by configure_shunt; do not overwrite.
 *     0x03 POWER_REG    : unsigned 16-bit, LSB = 25 × CURRENT_LSB.
 *     0x07 ALERT_LIMIT  : threshold register (bmon_ina226_configure_alert).
 *     0x06 MASK_ENABLE  : alert configuration (bmon_ina226_configure_alert).
 *
 * ── Auto-detection ────────────────────────────────────────────────────────
 *
 * The driver probes the die-ID register (0xFF) to distinguish devices:
 *   Reads 0x2260 → INA226
 *   Any other value → INA219 (INA219 has no die-ID register; the read
 *     returns a mirror or undefined value that is not 0x2260)
 *
 * The caller may override detection by passing bmon_ina_type_t explicitly.
 *
 * ── Register I/O ──────────────────────────────────────────────────────────
 *
 * Both devices use 8-bit register addresses and 16-bit big-endian register
 * values.  Register read sequence:
 *   1. write(fd, &reg, 1) to set the internal register pointer
 *   2. read(fd, buf, 2) to read the 16-bit big-endian value
 *
 * ── Thread Safety ─────────────────────────────────────────────────────────
 *
 * None of the public functions are thread-safe; ensure exclusive context
 * access.
 *
 * References:
 *   [1] INA219 Datasheet SBOS448G, Texas Instruments.
 *       https://www.ti.com/lit/ds/symlink/ina219.pdf
 *   [2] INA226 Datasheet SBOS547E, Texas Instruments.
 *       https://www.ti.com/lit/ds/symlink/ina226.pdf
 *   [3] Linux i2c-dev interface — Documentation/i2c/dev-interface.rst.
 *   [4] FlightEngineer.md — Serenity UAV Power Distribution Board specification.
 *
 * Target platform: PocketBeagle 2 Industrial (AM6254), Debian Trixie.
 */

#ifndef BMON_INA2XX_H
#define BMON_INA2XX_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ---------------------------------------------------------------------------
 * Device constants — INA219
 * ---------------------------------------------------------------------------*/

/** I2C address with A0 = A1 = GND (both INA219 and INA226 on Cape-A). */
#define INA2XX_I2C_ADDR        (0x40U)

/** INA219 bus voltage register address. */
#define INA219_REG_BUS_VOLT    (0x02U)

/**
 * INA219 bus voltage LSB value in millivolts.
 * Bits [15:3] of register 0x02; each LSB = 4 mV.
 * Bit 1 (CNVR) and bit 0 (OVF) are status flags, not voltage data.
 */
#define INA219_LSB_MV          (4U)

/* ---------------------------------------------------------------------------
 * Device constants — INA226
 * ---------------------------------------------------------------------------*/

/** INA226 configuration register address. */
#define INA226_REG_CONFIG      (0x00U)

/** INA226 shunt voltage register address (signed 16-bit, 2.5 µV/LSB). */
#define INA226_REG_SHUNT_VOLT  (0x01U)

/** INA226 bus voltage register address. */
#define INA226_REG_BUS_VOLT    (0x02U)

/** INA226 power register address (unsigned, LSB = 25 × CURRENT_LSB). */
#define INA226_REG_POWER       (0x03U)

/** INA226 current register address (signed 16-bit, LSB = CURRENT_LSB). */
#define INA226_REG_CURRENT     (0x04U)

/** INA226 calibration register address. */
#define INA226_REG_CALIBRATION (0x05U)

/** INA226 mask/enable register address (alert configuration). */
#define INA226_REG_MASK_ENABLE (0x06U)

/** INA226 alert limit register address. */
#define INA226_REG_ALERT_LIMIT (0x07U)

/** INA226 die-ID register address. */
#define INA226_REG_DIE_ID      (0xFFU)

/** INA226 manufacturer ID register address. */
#define INA226_REG_MFR_ID      (0xFEU)

/** Expected value in INA226 die-ID register; used for auto-detection. */
#define INA226_DIE_ID          (0x2260U)

/**
 * INA226 bus voltage LSB value in microvolts × 1000 (i.e. 1250 µV = 1.25 mV).
 * Register 0x02 is a 16-bit unsigned count; voltage_mv = count × 1250 / 1000.
 */
#define INA226_LSB_UV          (1250U) /* µV per LSB */

/**
 * INA226 shunt voltage LSB in nanovolts (2500 nV = 2.5 µV).
 * Register 0x01 is signed 16-bit; shunt_uv = (int16_t)reg × 2500 / 1000.
 */
#define INA226_SHUNT_LSB_NV    (2500U) /* nV per LSB */

/**
 * INA226 mask/enable bit: over-current alert on shunt-over-limit (SOL).
 * Set this bit in MASK_ENABLE to trigger ALERT when shunt voltage exceeds
 * ALERT_LIMIT register value.
 */
#define INA226_MASK_SOL        (0x8000U)

/**
 * INA226 mask/enable bit: bus-over-voltage alert (BOV).
 * Triggers ALERT when bus voltage exceeds ALERT_LIMIT register value.
 */
#define INA226_MASK_BOV        (0x4000U)

/**
 * INA226 mask/enable bit: bus-under-voltage alert (BUV).
 * Triggers ALERT when bus voltage falls below ALERT_LIMIT register value.
 */
#define INA226_MASK_BUV        (0x2000U)

/** INA226 mask/enable bit: alert polarity (active-high if set). */
#define INA226_MASK_APOL       (0x0002U)

/** INA226 mask/enable bit: alert latch enable. */
#define INA226_MASK_LEN        (0x0001U)

/* ---------------------------------------------------------------------------
 * Data types
 * ---------------------------------------------------------------------------*/

/**
 * @brief Identifies which INA device variant is being driven.
 *
 * Passed to bmon_ina2xx_open() or determined automatically.
 */
typedef enum {
    /** Automatically detect device type from die-ID register. */
    BMON_INA_AUTO = 0,

    /** Texas Instruments INA219 (Cape-A-1). */
    BMON_INA_INA219 = 1,

    /** Texas Instruments INA226 (Wash). */
    BMON_INA_INA226 = 2,
} bmon_ina_type_t;

/**
 * @brief Driver context.
 *
 * Initialise with bmon_ina2xx_open(); release with bmon_ina2xx_close().
 * Do not access internal fields directly.
 */
typedef struct bmon_ina2xx_ctx bmon_ina2xx_ctx_t;

/* ---------------------------------------------------------------------------
 * API
 * ---------------------------------------------------------------------------*/

/**
 * @brief Open the INA219/INA226 driver at a specific I2C address.
 *
 * Opens the I2C bus device and sets the slave address to @p i2c_addr via
 * ioctl I2C_SLAVE.  Pass INA2XX_I2C_ADDR (0x40) for the default Wash
 * on-cape device.  For FlightEngineer multi-device buses, pass the per-channel address
 * directly (0x40–0x44); a separate open() per device is required because each
 * context holds its own file descriptor and slave address.
 *
 * If @p type is BMON_INA_AUTO, reads the die-ID register (0xFF); if the
 * result is 0x2260 the device is treated as INA226, otherwise INA219.
 *
 * Both devices operate in their power-on default configuration (continuous
 * bus voltage conversion, 12-bit averaging).  No configuration register
 * writes are performed at open.
 *
 * @param[in]  i2c_dev   Path to I2C bus device, e.g. "/dev/i2c-2".
 * @param[in]  i2c_addr  7-bit I2C slave address of the target device
 *                       (e.g. 0x40, 0x41, 0x42, 0x43, or 0x44 for FlightEngineer).
 * @param[in]  type      Device variant, or BMON_INA_AUTO to auto-detect.
 * @param[out] ctx_out   Set to driver context on success.
 * @return 0 on success, negative errno on error:
 *         -EINVAL : i2c_dev or ctx_out is NULL, or i2c_addr is 0.
 *         -ENOMEM : memory allocation failed.
 *         -errno  : open/ioctl failure.
 */
int bmon_ina2xx_open(const char *i2c_dev, uint8_t i2c_addr,
                     bmon_ina_type_t type, bmon_ina2xx_ctx_t **ctx_out);

/**
 * @brief Close the driver and release resources.
 *
 * @param[in] ctx  Driver context from bmon_ina2xx_open().  May be NULL.
 */
void bmon_ina2xx_close(bmon_ina2xx_ctx_t *ctx);

/**
 * @brief Read the bus voltage in millivolts.
 *
 * Reads register 0x02 from the device and returns the bus voltage.
 *
 * INA219: voltage_mv = (reg >> 3) × 4
 * INA226: voltage_mv = (uint32_t)reg × 1250 / 1000
 *
 * @param[in]  ctx        Driver context from bmon_ina2xx_open().
 * @param[out] voltage_mv Bus voltage in millivolts on success.
 * @return 0 on success, negative errno on error:
 *         -EINVAL : ctx or voltage_mv is NULL.
 *         -EIO    : I2C read error.
 */
int bmon_ina2xx_read_mv(bmon_ina2xx_ctx_t *ctx, uint32_t *voltage_mv);

/**
 * @brief Return the device type that was detected or configured at open().
 *
 * @param[in] ctx  Driver context.
 * @return BMON_INA_INA219 or BMON_INA_INA226.
 *         If ctx is NULL, returns BMON_INA_AUTO (0) as a safe default.
 */
bmon_ina_type_t bmon_ina2xx_get_type(const bmon_ina2xx_ctx_t *ctx);

/* ---------------------------------------------------------------------------
 * INA226-only current-sense API
 *
 * These functions are only valid on INA226 devices.  They return -ENOTSUP if
 * called on an INA219 context.
 * ---------------------------------------------------------------------------*/

/**
 * @brief Configure the INA226 for current sensing by programming the
 *        calibration register.
 *
 * Computes CAL = floor(0.00512 / (current_lsb_ma × shunt_mohm × 1e-6)) and
 * writes it to register 0x05.  After this call, bmon_ina226_read_current_ma()
 * and bmon_ina226_read_power_mw() return valid data.
 *
 * In voltage-only mode (Wash on-cape INA226), do NOT call this function;
 * the calibration register remains 0 and the current / power registers read 0.
 *
 * @param[in] ctx           Driver context (must be INA226).
 * @param[in] shunt_mohm    Shunt resistance in milli-ohms (e.g. 1 for 1 mΩ).
 * @param[in] imax_ma       Maximum expected current in milliamps (e.g. 60000
 * for 60 A). Sets the current LSB to imax_ma / 32768 mA.
 * @param[out] current_lsb_ua_out  If non-NULL, receives the programmed
 *                          current LSB in microamps.
 * @return 0 on success, -ENOTSUP if ctx is INA219, -EINVAL if arguments are
 *         invalid (shunt_mohm == 0 or imax_ma == 0), -EIO on I2C error.
 */
int bmon_ina226_configure_shunt(bmon_ina2xx_ctx_t *ctx, uint32_t shunt_mohm,
                                uint32_t imax_ma, uint32_t *current_lsb_ua_out);

/**
 * @brief Read the current register from an INA226 in current-sense mode.
 *
 * Reads register 0x04 (signed 16-bit) and scales by the current LSB programmed
 * by bmon_ina226_configure_shunt().
 *
 * bmon_ina226_configure_shunt() must have been called first; otherwise the
 * calibration register is 0 and this function returns 0 mA regardless of load.
 *
 * @param[in]  ctx         Driver context (INA226 only).
 * @param[out] current_ma  Signed current in milliamps.  Positive = current
 *                         flowing from IN+ to IN− (load current through shunt).
 *                         Negative = reverse current (regen / charging).
 * @return 0 on success, -ENOTSUP if ctx is INA219, -EINVAL on NULL args,
 *         -EIO on I2C error.
 */
int bmon_ina226_read_current_ma(bmon_ina2xx_ctx_t *ctx, int32_t *current_ma);

/**
 * @brief Read the power register from an INA226 in current-sense mode.
 *
 * Reads register 0x03 (unsigned 16-bit) and scales by 25 × current_lsb.
 * The power register represents bus_voltage × current (apparent power at
 * the INA226 measurement point, not delivered power).
 *
 * bmon_ina226_configure_shunt() must have been called first.
 *
 * @param[in]  ctx      Driver context (INA226 only).
 * @param[out] power_mw Power in milliwatts.
 * @return 0 on success, -ENOTSUP if ctx is INA219, -EINVAL on NULL args,
 *         -EIO on I2C error.
 */
int bmon_ina226_read_power_mw(bmon_ina2xx_ctx_t *ctx, uint32_t *power_mw);

/**
 * @brief Configure the INA226 ALERT function.
 *
 * Writes the MASK_ENABLE register (0x06) and ALERT_LIMIT register (0x07)
 * to enable alert assertion on the specified condition.
 *
 * Common alert_mask values (may be OR'd):
 *   INA226_MASK_SOL  — alert on shunt-over-limit (overcurrent)
 *   INA226_MASK_BOV  — alert on bus-over-voltage
 *   INA226_MASK_BUV  — alert on bus-under-voltage
 *
 * The ALERT_LIMIT register value is the raw comparison threshold:
 *   SOL: alert_limit = I_limit_ma / current_lsb_ma (use current_lsb returned
 *        by configure_shunt, convert to mA; alert_limit = I_limit_ma × 32768
 *        / imax_ma)
 *   BOV/BUV: alert_limit = V_limit_mv / 1.25 (INA226 bus voltage LSB = 1.25 mV)
 *
 * @param[in] ctx          Driver context (INA226 only).
 * @param[in] alert_mask   Bitmask for MASK_ENABLE register (INA226_MASK_*).
 * @param[in] alert_limit  Raw 16-bit value for the ALERT_LIMIT register.
 * @return 0 on success, -ENOTSUP if ctx is INA219, -EINVAL on NULL ctx,
 *         -EIO on I2C error.
 */
int bmon_ina226_configure_alert(bmon_ina2xx_ctx_t *ctx, uint16_t alert_mask,
                                uint16_t alert_limit);

#ifdef __cplusplus
}
#endif

#endif /* BMON_INA2XX_H */
