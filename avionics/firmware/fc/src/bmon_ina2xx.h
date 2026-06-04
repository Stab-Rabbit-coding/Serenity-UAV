/**
 * @file    bmon_ina2xx.h
 * @brief   INA219 / INA226 battery voltage monitor driver — public API.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Drives the Texas Instruments INA219AIDR (Cape-A-1) and INA226AIDGSR
 * (Cape-A-2) via Linux userspace i2c-dev.  Both devices are configured
 * in voltage-only measurement mode (no shunt resistor on Cape-A hardware;
 * IN+ and IN− are tied together at the battery terminal).
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
 * ── INA226AIDGSR (Cape-A-2) ───────────────────────────────────────────────
 *
 *   I2C address : 0x40 (A0, A1 tied to GND)
 *   Bus voltage : 0–36 V, register 0x02, full 16-bit unsigned.
 *   Resolution  : 1.25 mV per LSB.
 *   die_id register 0xFF: always reads 0x2260.
 *   Manufacturer ID register 0xFE: reads 0x5449 ("TI").
 *   Cape-A-2 usage: voltage-only.
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
 * bmon_ina2xx_read_mv() is not thread-safe; ensure exclusive context access.
 *
 * References:
 *   [1] INA219 Datasheet SBOS448G, Texas Instruments.
 *       https://www.ti.com/lit/ds/symlink/ina219.pdf
 *   [2] INA226 Datasheet SBOS547E, Texas Instruments.
 *       https://www.ti.com/lit/ds/symlink/ina226.pdf
 *   [3] Linux i2c-dev interface — Documentation/i2c/dev-interface.rst.
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
#define INA2XX_I2C_ADDR         (0x40U)

/** INA219 bus voltage register address. */
#define INA219_REG_BUS_VOLT     (0x02U)

/**
 * INA219 bus voltage LSB value in millivolts.
 * Bits [15:3] of register 0x02; each LSB = 4 mV.
 * Bit 1 (CNVR) and bit 0 (OVF) are status flags, not voltage data.
 */
#define INA219_LSB_MV           (4U)

/* ---------------------------------------------------------------------------
 * Device constants — INA226
 * ---------------------------------------------------------------------------*/

/** INA226 bus voltage register address. */
#define INA226_REG_BUS_VOLT     (0x02U)

/** INA226 die-ID register address. */
#define INA226_REG_DIE_ID       (0xFFU)

/** INA226 manufacturer ID register address. */
#define INA226_REG_MFR_ID       (0xFEU)

/** Expected value in INA226 die-ID register; used for auto-detection. */
#define INA226_DIE_ID           (0x2260U)

/**
 * INA226 bus voltage LSB value in microvolts × 1000 (i.e. 1250 µV = 1.25 mV).
 * Register 0x02 is a 16-bit unsigned count; voltage_mv = count × 1250 / 1000.
 */
#define INA226_LSB_UV           (1250U)  /* µV per LSB */

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
    BMON_INA_AUTO    = 0,

    /** Texas Instruments INA219 (Cape-A-1). */
    BMON_INA_INA219  = 1,

    /** Texas Instruments INA226 (Cape-A-2). */
    BMON_INA_INA226  = 2,
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
 * @brief Open the INA219/INA226 driver.
 *
 * Opens the I2C bus device, sets slave address to INA2XX_I2C_ADDR (0x40).
 * If @p type is BMON_INA_AUTO, reads the die-ID register (0xFF); if the
 * result is 0x2260 the device is treated as INA226, otherwise INA219.
 *
 * Both devices operate in their power-on default configuration (continuous
 * bus voltage conversion, 12-bit averaging).  No configuration register
 * writes are performed.
 *
 * @param[in]  i2c_dev  Path to I2C bus device, e.g. "/dev/i2c-1".
 * @param[in]  type     Device variant, or BMON_INA_AUTO to auto-detect.
 * @param[out] ctx_out  Set to driver context on success.
 * @return 0 on success, negative errno on error:
 *         -EINVAL : i2c_dev or ctx_out is NULL.
 *         -ENOMEM : memory allocation failed.
 *         -errno  : open/ioctl failure.
 */
int bmon_ina2xx_open(const char *i2c_dev,
                     bmon_ina_type_t type,
                     bmon_ina2xx_ctx_t **ctx_out);

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

#ifdef __cplusplus
}
#endif

#endif /* BMON_INA2XX_H */
