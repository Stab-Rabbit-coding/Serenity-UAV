/**
 * @file    mag_mmc5983ma.h
 * @brief   MMC5983MA 3-axis magnetometer driver — public API.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Drives the MEMSIC MMC5983MA 3-axis magnetometer via Linux userspace
 * i2c-dev.  Used by serenity-fc on Wash (EMI-hardened variant).
 *
 * ── Device Overview ───────────────────────────────────────────────────────
 *
 * The MMC5983MA is an AEC-Q100 Grade 2 qualified 3-axis AMR magnetometer.
 * It provides 18-bit resolution per axis via a split 8+8+2 register scheme,
 * and includes internal SET/RESET coils for bridge sensitivity refresh.
 *
 *   I2C address      : 0x30 (SA0 tied to GND on Wash; SA0 = 1 → 0x31)
 *   Supply voltage   : 1.71–3.6 V (I/O), 1.71–1.89 V (VDD) typical
 *   Full-scale range : ±8 G (fixed)
 *   Resolution       : 18-bit (4 mG / LSB at full-scale center)
 *   Output data rate : up to 1000 Hz in continuous mode
 *   Product ID reg   : 0x2F → reads 0x30
 *
 * ── 18-bit Reconstruction ─────────────────────────────────────────────────
 *
 * Each axis result is spread across three register bytes:
 *
 *   Register 0x00 — Xout[17:10]  (bits 7:0 = X bits 17 down to 10)
 *   Register 0x01 — Xout[9:2]   (bits 7:0 = X bits 9 down to 2)
 *   Register 0x02 — Yout[17:10]
 *   Register 0x03 — Yout[9:2]
 *   Register 0x04 — Zout[17:10]
 *   Register 0x05 — Zout[9:2]
 *   Register 0x06 — Xout[1:0] in bits [7:6], Yout[1:0] in bits [5:4],
 *                   Zout[1:0] in bits [3:2]  (other bits reserved)
 *
 * Reconstruction (X example):
 *   x_raw = (reg[0] << 10) | (reg[1] << 2) | ((reg[6] >> 6) & 0x03)
 *   x_raw is an 18-bit unsigned value; zero-field output = 2^17 = 131072
 *
 * ── Scaling ───────────────────────────────────────────────────────────────
 *
 * Sensitivity: 16384 LSB/G (18-bit, ±8 G range).
 * Zero-field offset: 2^17 = 131072 (unsigned).
 *
 * Output unit: nt100 (100 nT steps).
 *   1 G = 100 µT = 1000 nt100
 *   1 LSB = 10000 nt100 / 16384 ≈ 0.61 nt100
 *
 *   nt100 = ((int32_t)raw - 131072) * 10000 / 16384
 *
 * Integer arithmetic: ((int32_t)raw - 131072) range is ±131071.
 * After × 10000: ±1 310 710 000 — fits in int32_t (max 2 147 483 647).
 *
 * ── SET/RESET ─────────────────────────────────────────────────────────────
 *
 * The MMC5983MA includes internal SET and RESET coils that restore AMR
 * bridge sensitivity and remove bridge offset.  This driver issues SET
 * during open() and optionally at the application's request.
 *
 * ── Continuous Measurement Mode ───────────────────────────────────────────
 *
 * ODR and bandwidth are configured via CTRL0 (0x09), CTRL1 (0x0A), and
 * CTRL2 (0x0B).  This driver initialises to:
 *   BW  = 100 Hz bandwidth (fastest settling, matches QMC5883L on Cape-A-1)
 *   ODR = 100 Hz continuous measurement
 *   CMM_freq_en = 1, Take_meas_M = 1 (enable continuous measurement)
 *
 * ── Thread Safety ─────────────────────────────────────────────────────────
 *
 * mag_mmc5983ma_read() is not thread-safe.  Ensure exclusive context access
 * when calling from multiple threads.
 *
 * References:
 *   [1] MMC5983MA Datasheet DS-MMC5983MA Rev. C, MEMSIC Inc.
 *       https://www.memsic.com/magnetometer-sensor.html
 *   [2] Linux i2c-dev interface — Documentation/i2c/dev-interface.rst.
 *
 * Target platform: PocketBeagle 2 Industrial (AM6254), Debian Trixie.
 */

#ifndef MAG_MMC5983MA_H
#define MAG_MMC5983MA_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ---------------------------------------------------------------------------
 * Device constants
 * ---------------------------------------------------------------------------*/

/** I2C bus address with SA0 = 0 (Wash hardware strapping). */
#define MMC5983MA_I2C_ADDR      (0x30U)

/** Product ID register value that confirms MMC5983MA identity. */
#define MMC5983MA_PRODUCT_ID    (0x30U)

/**
 * 18-bit zero-field output code (2^17).
 * Subtract this from raw unsigned readings before scaling to get a
 * signed magnetic field value.
 */
#define MMC5983MA_ZERO_OFFSET   (131072U)

/**
 * Sensitivity for ±8 G full-scale range.
 * Units: LSB per Gauss.  16384 LSB = 1 G = 100 µT.
 */
#define MMC5983MA_SENS_LSB_PER_G (16384)

/* ---------------------------------------------------------------------------
 * Register addresses
 * ---------------------------------------------------------------------------*/

#define MMC5983MA_REG_XOUT_MSB  (0x00U)  /**< X[17:10] output MSB.          */
#define MMC5983MA_REG_XOUT_LSB  (0x01U)  /**< X[9:2] output LSB.            */
#define MMC5983MA_REG_YOUT_MSB  (0x02U)  /**< Y[17:10] output MSB.          */
#define MMC5983MA_REG_YOUT_LSB  (0x03U)  /**< Y[9:2] output LSB.            */
#define MMC5983MA_REG_ZOUT_MSB  (0x04U)  /**< Z[17:10] output MSB.          */
#define MMC5983MA_REG_ZOUT_LSB  (0x05U)  /**< Z[9:2] output LSB.            */
#define MMC5983MA_REG_XYZ_LSB2  (0x06U)  /**< X[1:0], Y[1:0], Z[1:0] bits.  */
#define MMC5983MA_REG_STATUS    (0x08U)  /**< Status register.               */
#define MMC5983MA_REG_CTRL0     (0x09U)  /**< Control register 0.            */
#define MMC5983MA_REG_CTRL1     (0x0AU)  /**< Control register 1 (BW, ST).   */
#define MMC5983MA_REG_CTRL2     (0x0BU)  /**< Control register 2 (ODR, CMM). */
#define MMC5983MA_REG_CTRL3     (0x0CU)  /**< Control register 3 (SPI mode). */
#define MMC5983MA_REG_PROD_ID   (0x2FU)  /**< Product ID (reads 0x30).       */

/* ---------------------------------------------------------------------------
 * Register field bitmasks and values
 * ---------------------------------------------------------------------------*/

/** STATUS register: measurement done flag (Meas_M_Done). */
#define MMC5983MA_STATUS_MEAS_M_DONE    (0x01U)

/** STATUS register: SET/RESET done flag (Meas_T_Done). */
#define MMC5983MA_STATUS_MEAS_T_DONE    (0x02U)

/** CTRL0: trigger a single magnetic measurement (Take_meas_M). */
#define MMC5983MA_CTRL0_TAKE_MEAS_M     (0x01U)

/** CTRL0: initiate a SET operation (restore sensitivity after saturation). */
#define MMC5983MA_CTRL0_SET             (0x08U)

/** CTRL0: enable continuous measurement mode (CMM_freq_en). */
#define MMC5983MA_CTRL0_CMM_FREQ_EN     (0x80U)

/**
 * CTRL1 bandwidth value: 100 Hz (BW[1:0] = 0b10).
 * Controls measurement settling time and noise-bandwidth tradeoff.
 *   0b00 = 6.6 ms settling
 *   0b01 = 3.5 ms settling
 *   0b10 = 2.0 ms settling (100 Hz BW)
 *   0b11 = 1.2 ms settling (200 Hz BW)
 */
#define MMC5983MA_CTRL1_BW_100HZ        (0x02U)

/**
 * CTRL2 ODR value for 100 Hz continuous mode (ODR[3:0] = 0b0110).
 * CMM_en bit is also set here (bit 4 = 0b1).
 *
 *   CTRL2[4]   = CMM_en  (enable continuous measurement mode)
 *   CTRL2[3:0] = ODR     (0110 = 100 Hz)
 *   Combined:  0b0001_0110 = 0x16
 */
#define MMC5983MA_CTRL2_INIT            (0x16U)

/* ---------------------------------------------------------------------------
 * Data types
 * ---------------------------------------------------------------------------*/

/**
 * @brief Raw 18-bit axis readings from a single measurement.
 *
 * Unsigned values; zero field corresponds to MMC5983MA_ZERO_OFFSET (131072).
 * These are provided for diagnostics and calibration use.
 */
typedef struct {
    uint32_t x;   /**< Raw 18-bit X-axis reading (0–262143; zero = 131072). */
    uint32_t y;   /**< Raw 18-bit Y-axis reading. */
    uint32_t z;   /**< Raw 18-bit Z-axis reading. */
} mmc5983ma_raw_t;

/**
 * @brief Scaled magnetometer sample in nt100 units.
 *
 * nt100 = 100 nT per count.  1 µT = 10 nt100.
 * Signed; positive values indicate field along the positive axis direction.
 */
typedef struct {
    int32_t x_nt100;   /**< X-axis magnetic field in units of 100 nT. */
    int32_t y_nt100;   /**< Y-axis magnetic field in units of 100 nT. */
    int32_t z_nt100;   /**< Z-axis magnetic field in units of 100 nT. */
} mmc5983ma_sample_t;

/**
 * @brief Driver context.
 *
 * Initialise with mag_mmc5983ma_open(); release with mag_mmc5983ma_close().
 */
typedef struct mmc5983ma_ctx mmc5983ma_ctx_t;

/* ---------------------------------------------------------------------------
 * API
 * ---------------------------------------------------------------------------*/

/**
 * @brief Open the MMC5983MA driver and initialise the device.
 *
 * Opens the I2C bus, sets slave address to MMC5983MA_I2C_ADDR (0x30),
 * verifies the product ID register (0x2F → 0x30), issues a SET pulse
 * (restores AMR bridge offset), then configures continuous measurement
 * at 100 Hz with 100 Hz bandwidth.
 *
 * @param[in]  i2c_dev  Path to I2C bus, e.g. "/dev/i2c-1".
 * @param[out] ctx_out  Set to driver context on success.
 * @return 0 on success, negative errno on error:
 *         -EINVAL : i2c_dev or ctx_out is NULL.
 *         -ENOMEM : memory allocation failed.
 *         -EIO    : product-ID mismatch or register I/O error.
 *         -errno  : open/ioctl failure.
 */
int mag_mmc5983ma_open(const char *i2c_dev, mmc5983ma_ctx_t **ctx_out);

/**
 * @brief Close the driver and release resources.
 *
 * @param[in] ctx  Driver context from mag_mmc5983ma_open().  May be NULL.
 */
void mag_mmc5983ma_close(mmc5983ma_ctx_t *ctx);

/**
 * @brief Read a magnetometer sample (blocking poll for measurement done).
 *
 * In continuous mode the STATUS.Meas_M_Done bit is set when a new sample
 * is available.  This function polls that bit up to @p timeout_ms
 * milliseconds, then reads the 7-byte output burst and fills @p sample.
 *
 * @param[in]  ctx        Driver context.
 * @param[out] sample     Filled with scaled nt100 values on success.
 * @param[in]  timeout_ms Maximum wait for Meas_M_Done (0 = no wait).
 * @return 0 on success, negative errno on error:
 *         -EINVAL    : ctx or sample is NULL.
 *         -ETIMEDOUT : Meas_M_Done not set within timeout_ms.
 *         -EIO       : I2C error.
 */
int mag_mmc5983ma_read(mmc5983ma_ctx_t *ctx,
                       mmc5983ma_sample_t *sample,
                       unsigned int timeout_ms);

/**
 * @brief Read raw 18-bit axis counts.
 *
 * @param[in]  ctx        Driver context.
 * @param[out] raw        Filled with raw unsigned 18-bit counts.
 * @param[in]  timeout_ms Maximum wait for Meas_M_Done (0 = no wait).
 * @return 0 on success, negative errno on error.
 */
int mag_mmc5983ma_read_raw(mmc5983ma_ctx_t *ctx,
                            mmc5983ma_raw_t *raw,
                            unsigned int timeout_ms);

/**
 * @brief Issue a SET pulse to restore AMR bridge sensitivity.
 *
 * Should be called if the device was exposed to a strong external magnetic
 * field that may have demagnetised the AMR bridges.  The open() call
 * issues SET automatically; explicit calls are rarely needed in flight.
 *
 * @param[in] ctx  Driver context.
 * @return 0 on success, -EIO on I2C error.
 */
int mag_mmc5983ma_set(mmc5983ma_ctx_t *ctx);

#ifdef __cplusplus
}
#endif

#endif /* MAG_MMC5983MA_H */
