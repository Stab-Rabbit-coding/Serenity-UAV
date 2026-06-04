/**
 * @file    mag_qmc5883l.h
 * @brief   QMC5883L 3-axis magnetometer driver — public API.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Drives the QMC5883L 3-axis magnetometer via Linux userspace i2c-dev
 * (ioctl/read/write on /dev/i2c-N).  Used by serenity-fc on Cape-A-1.
 *
 * ── Device Overview ───────────────────────────────────────────────────────
 *
 * The QMC5883L (QST Corporation) is a 3-axis AMR magnetometer with an I2C
 * interface.  It is register-compatible with the HMC5883L in many operating
 * modes but uses a different register map and command set.
 *
 *   I2C address      : 0x0D (fixed; no SA0 pin)
 *   Supply voltage   : 2.16–3.6 V
 *   Full-scale range : ±2 G or ±8 G (configured via RNG bits)
 *   Output rate      : 10/50/100/200 Hz (ODR bits)
 *   Resolution       : 16-bit two's-complement per axis
 *   Chip-ID register : 0x0D → always reads 0xFF
 *
 * ── Sensitivity ───────────────────────────────────────────────────────────
 *
 * For the ±2 G full-scale range (this driver's default):
 *   Sensitivity = 12000 LSB/G = 120 LSB/(100 nT)
 *
 * Measurement output in this driver is in units of 100 nT (nanotesla × 100),
 * i.e. "nt100".  This preserves integer sub-microtesla resolution without
 * floating-point arithmetic.  1 µT = 10 nt100.
 *
 *   nt100 = raw_signed × 100 / 120     (integer division, truncates toward 0)
 *
 * ── Register Map (relevant registers) ────────────────────────────────────
 *
 *   0x00  XOUT_L  — X-axis data low byte
 *   0x01  XOUT_H  — X-axis data high byte
 *   0x02  YOUT_L  — Y-axis data low byte
 *   0x03  YOUT_H  — Y-axis data high byte
 *   0x04  ZOUT_L  — Z-axis data low byte
 *   0x05  ZOUT_H  — Z-axis data high byte
 *   0x06  STATUS  — Status register (DRDY bit 0, OVL bit 1, DORS bit 2)
 *   0x09  CTRL1   — Control register 1 (MODE, ODR, RNG, OSR)
 *   0x0A  CTRL2   — Control register 2 (INT_ENB, POL, SRST)
 *   0x0B  SET_RESET — Set/Reset period register (must be written 0x01)
 *   0x0D  CHIP_ID — Chip identification (reads 0xFF on QMC5883L)
 *
 * ── CTRL1 Configuration ───────────────────────────────────────────────────
 *
 *   Bits [1:0] MODE : 00 = Standby, 01 = Continuous
 *   Bits [3:2] ODR  : 00 = 10 Hz, 01 = 50 Hz, 10 = 100 Hz, 11 = 200 Hz
 *   Bits [5:4] RNG  : 00 = ±2 G, 01 = ±8 G
 *   Bits [7:6] OSR  : 00 = 512, 01 = 256, 10 = 128, 11 = 64
 *
 * This driver initialises to:
 *   MODE = Continuous, ODR = 100 Hz, RNG = ±2 G, OSR = 512
 *   CTRL1 = 0b00_00_10_01 = 0x09
 *
 * ── DRDY Signal ───────────────────────────────────────────────────────────
 *
 * Cape-A hardware connects DRDY (STATUS.0) to a GPIO line named
 * CAPE_A_GPIO_MAG_DRDY.  This driver polls the STATUS register rather than
 * using the GPIO interrupt, to keep the driver self-contained and avoid
 * platform-specific libgpiod dependencies in the FC daemon.
 *
 * ── Thread Safety ─────────────────────────────────────────────────────────
 *
 * mag_qmc5883l_read() is not thread-safe.  The caller must ensure exclusive
 * access to the context if called from multiple threads.
 *
 * References:
 *   [1] QMC5883L Datasheet Rev. 1.0, QST Corporation.
 *       (Public specification available from QST and third-party MCU vendors.)
 *   [2] Linux i2c-dev interface — Documentation/i2c/dev-interface.rst.
 *
 * Target platform: PocketBeagle 2 Industrial (AM6254), Debian Trixie.
 */

#ifndef MAG_QMC5883L_H
#define MAG_QMC5883L_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ---------------------------------------------------------------------------
 * Device constants
 * ---------------------------------------------------------------------------*/

/** I2C bus address of the QMC5883L (fixed; no address-select pin). */
#define QMC5883L_I2C_ADDR       (0x0DU)

/** Value returned by chip-ID register 0x0D on a genuine QMC5883L. */
#define QMC5883L_CHIP_ID        (0xFFU)

/**
 * Sensitivity for ±2 G full-scale range.
 * Units: LSB per Gauss.  12000 LSB = 1 G = 100 µT = 1000 nt100.
 */
#define QMC5883L_SENS_LSB_PER_G (12000)

/* ---------------------------------------------------------------------------
 * Register addresses
 * ---------------------------------------------------------------------------*/

#define QMC5883L_REG_XOUT_L     (0x00U)  /**< X output — low byte.          */
#define QMC5883L_REG_XOUT_H     (0x01U)  /**< X output — high byte.         */
#define QMC5883L_REG_YOUT_L     (0x02U)  /**< Y output — low byte.          */
#define QMC5883L_REG_YOUT_H     (0x03U)  /**< Y output — high byte.         */
#define QMC5883L_REG_ZOUT_L     (0x04U)  /**< Z output — low byte.          */
#define QMC5883L_REG_ZOUT_H     (0x05U)  /**< Z output — high byte.         */
#define QMC5883L_REG_STATUS     (0x06U)  /**< Status register.               */
#define QMC5883L_REG_CTRL1      (0x09U)  /**< Control register 1.            */
#define QMC5883L_REG_CTRL2      (0x0AU)  /**< Control register 2.            */
#define QMC5883L_REG_SET_RESET  (0x0BU)  /**< Set/Reset period (write 0x01). */
#define QMC5883L_REG_CHIP_ID    (0x0DU)  /**< Chip identification register.  */

/* ---------------------------------------------------------------------------
 * Register field bitmasks
 * ---------------------------------------------------------------------------*/

/** STATUS register: data-ready flag (new sample available). */
#define QMC5883L_STATUS_DRDY    (0x01U)

/** STATUS register: data overflow — output saturated on at least one axis. */
#define QMC5883L_STATUS_OVL     (0x02U)

/** CTRL1 MODE field: continuous measurement mode. */
#define QMC5883L_MODE_CONT      (0x01U)

/**
 * CTRL1 value used by this driver:
 *   MODE = Continuous (01), ODR = 100 Hz (10), RNG = ±2 G (00), OSR = 512 (00)
 *   = 0b00_00_10_01 = 0x09
 */
#define QMC5883L_CTRL1_INIT     (0x09U)

/** CTRL2 value used by this driver: interrupts disabled, no soft-reset. */
#define QMC5883L_CTRL2_INIT     (0x00U)

/** SET_RESET period register: must be written 0x01 on startup (per datasheet). */
#define QMC5883L_SET_RESET_VAL  (0x01U)

/* ---------------------------------------------------------------------------
 * Data types
 * ---------------------------------------------------------------------------*/

/**
 * @brief Raw 16-bit axis readings from a single measurement.
 *
 * Raw two's-complement values directly from the device registers before
 * any scaling.  These are provided for diagnostic and calibration use.
 * Normally applications should use the scaled fields in qmc5883l_sample_t.
 */
typedef struct {
    int16_t x;   /**< Raw X-axis ADC count (signed, ±2G range = ±12000 LSB). */
    int16_t y;   /**< Raw Y-axis ADC count. */
    int16_t z;   /**< Raw Z-axis ADC count. */
} qmc5883l_raw_t;

/**
 * @brief Scaled magnetometer sample.
 *
 * Field values are in units of 100 nT (nt100).  To convert to µT, divide
 * by 10.  To convert to mGauss, divide by 100.
 *
 *   nt100 = raw_signed × 100 / 120
 *   1 µT  = 10 nt100
 *   1 mG  = 100 nt100
 */
typedef struct {
    int32_t x_nt100;   /**< X-axis magnetic field in units of 100 nT. */
    int32_t y_nt100;   /**< Y-axis magnetic field in units of 100 nT. */
    int32_t z_nt100;   /**< Z-axis magnetic field in units of 100 nT. */

    /** True if STATUS.OVL was set — at least one axis is saturated. */
    bool    overflow;
} qmc5883l_sample_t;

/**
 * @brief Driver context.
 *
 * Initialise with mag_qmc5883l_open(); release with mag_qmc5883l_close().
 * Do not access internal fields directly.
 */
typedef struct qmc5883l_ctx qmc5883l_ctx_t;

/* ---------------------------------------------------------------------------
 * API
 * ---------------------------------------------------------------------------*/

/**
 * @brief Open the QMC5883L driver and initialise the device.
 *
 * Opens the specified I2C bus device, sets the I2C slave address to
 * QMC5883L_I2C_ADDR (0x0D), verifies the chip ID register (0x0D → 0xFF),
 * and writes the initialisation sequence:
 *   CTRL2      ← 0x00  (interrupts off, no soft-reset)
 *   SET_RESET  ← 0x01  (required per datasheet)
 *   CTRL1      ← 0x09  (continuous, 100 Hz, ±2 G, OSR 512)
 *
 * @param[in]  i2c_dev  Path to the I2C bus device, e.g. "/dev/i2c-1".
 * @param[out] ctx_out  Set to the allocated driver context on success.
 * @return 0 on success, negative errno on error:
 *         -EINVAL : i2c_dev or ctx_out is NULL.
 *         -ENOMEM : memory allocation failed.
 *         -EIO    : chip-ID mismatch (device not present or not a QMC5883L).
 *         -errno  : I2C open, ioctl, or register-write failure.
 */
int mag_qmc5883l_open(const char *i2c_dev, qmc5883l_ctx_t **ctx_out);

/**
 * @brief Close the driver and release all resources.
 *
 * Closes the I2C file descriptor and frees the context.  Safe to call with
 * a NULL pointer (no-op).
 *
 * @param[in] ctx  Driver context from mag_qmc5883l_open().  May be NULL.
 */
void mag_qmc5883l_close(qmc5883l_ctx_t *ctx);

/**
 * @brief Read a magnetometer sample (blocking poll for data-ready).
 *
 * Polls the STATUS register until DRDY is set (up to @p timeout_ms
 * milliseconds), then reads the six output registers in a single burst
 * and fills @p sample with scaled values.
 *
 * @param[in]  ctx        Driver context from mag_qmc5883l_open().
 * @param[out] sample     Filled with the scaled magnetometer sample.
 * @param[in]  timeout_ms Maximum time to wait for DRDY, in milliseconds.
 *                        Pass 0 to read immediately without waiting.
 * @return 0 on success, negative errno on error:
 *         -EINVAL : ctx or sample is NULL.
 *         -ETIMEDOUT : DRDY not asserted within timeout_ms.
 *         -EIO    : I2C read error.
 */
int mag_qmc5883l_read(qmc5883l_ctx_t *ctx,
                      qmc5883l_sample_t *sample,
                      unsigned int timeout_ms);

/**
 * @brief Read raw (unscaled) axis counts.
 *
 * Same poll-then-read sequence as mag_qmc5883l_read() but returns the
 * raw two's-complement 16-bit ADC counts without scaling.  Intended for
 * calibration and diagnostics.
 *
 * @param[in]  ctx        Driver context from mag_qmc5883l_open().
 * @param[out] raw        Filled with the raw axis counts.
 * @param[in]  timeout_ms Maximum wait for DRDY (0 = no wait).
 * @return 0 on success, negative errno on error.
 */
int mag_qmc5883l_read_raw(qmc5883l_ctx_t *ctx,
                          qmc5883l_raw_t *raw,
                          unsigned int timeout_ms);

#ifdef __cplusplus
}
#endif

#endif /* MAG_QMC5883L_H */
