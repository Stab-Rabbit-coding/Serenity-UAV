/**
 * @file    mag_mmc5983ma.c
 * @brief   MMC5983MA 3-axis magnetometer driver — implementation.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Implements the MMC5983MA driver described in mag_mmc5983ma.h.
 * Uses Linux userspace i2c-dev (ioctl(I2C_SLAVE) + read/write syscalls).
 *
 * Register I/O protocol (same as QMC5883L driver):
 *   Write 2 bytes : write(fd, {reg, val}, 2)
 *   Burst read N  : write(fd, &reg, 1) then read(fd, buf, N)
 *
 * References:
 *   [1] MMC5983MA Datasheet DS-MMC5983MA Rev. C, MEMSIC Inc.
 *   [2] Linux i2c-dev interface — Documentation/i2c/dev-interface.rst.
 *
 * Target platform: PocketBeagle 2 Industrial (AM6254), Debian Trixie.
 */

#include "mag_mmc5983ma.h"

#include <errno.h>
#include <fcntl.h>
#include <linux/i2c-dev.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <time.h>
#include <unistd.h>

/* ---------------------------------------------------------------------------
 * Internal context
 * ---------------------------------------------------------------------------*/

struct mmc5983ma_ctx {
    int fd; /**< Open /dev/i2c-N file descriptor. */
};

/* ---------------------------------------------------------------------------
 * Internal helpers
 * ---------------------------------------------------------------------------*/

/**
 * @brief Write a single byte to a device register.
 */
static int reg_write(int fd, uint8_t reg, uint8_t val) {
    uint8_t buf[2];

    buf[0] = reg;
    buf[1] = val;

    if (write(fd, buf, 2U) != 2) {
        return -EIO;
    }
    return 0;
}

/**
 * @brief Burst-read @p len bytes starting at register @p reg.
 */
static int reg_read(int fd, uint8_t reg, uint8_t *buf, size_t len) {
    if (write(fd, &reg, 1U) != 1) {
        return -EIO;
    }
    if (read(fd, buf, len) != (ssize_t)len) {
        return -EIO;
    }
    return 0;
}

/**
 * @brief Poll STATUS.Meas_M_Done until set or @p timeout_ms expires.
 *
 * Polls every 2 ms.  The device issues a new measurement every 10 ms at
 * 100 Hz ODR, so 2 ms granularity is adequate.
 */
static int wait_meas_done(int fd, unsigned int timeout_ms) {
    static const struct timespec poll_interval = {
        .tv_sec = 0, .tv_nsec = 2000000L /* 2 ms */
    };

    unsigned int elapsed_ms = 0U;
    uint8_t      status = 0U;
    int          rc;

    if (timeout_ms == 0U) {
        return 0;
    }

    for (;;) {
        rc = reg_read(fd, MMC5983MA_REG_STATUS, &status, 1U);
        if (rc != 0) {
            return rc;
        }
        if ((status & MMC5983MA_STATUS_MEAS_M_DONE) != 0U) {
            return 0;
        }
        if (elapsed_ms >= timeout_ms) {
            return -ETIMEDOUT;
        }
        nanosleep(&poll_interval, NULL);
        elapsed_ms += 2U;
    }
}

/* ---------------------------------------------------------------------------
 * Public API
 * ---------------------------------------------------------------------------*/

int mag_mmc5983ma_open(const char *i2c_dev, mmc5983ma_ctx_t **ctx_out) {
    mmc5983ma_ctx_t *ctx;
    uint8_t          prod_id;
    int              rc;

    if (i2c_dev == NULL || ctx_out == NULL) {
        return -EINVAL;
    }

    ctx = calloc(1U, sizeof(*ctx));
    if (ctx == NULL) {
        return -ENOMEM;
    }

    ctx->fd = open(i2c_dev, O_RDWR | O_CLOEXEC);
    if (ctx->fd < 0) {
        rc = -errno;
        free(ctx);
        return rc;
    }

    if (ioctl(ctx->fd, I2C_SLAVE, (long)MMC5983MA_I2C_ADDR) < 0) {
        rc = -errno;
        close(ctx->fd);
        free(ctx);
        return rc;
    }

    /* Verify product ID. */
    rc = reg_read(ctx->fd, MMC5983MA_REG_PROD_ID, &prod_id, 1U);
    if (rc != 0) {
        close(ctx->fd);
        free(ctx);
        return rc;
    }
    if (prod_id != MMC5983MA_PRODUCT_ID) {
        close(ctx->fd);
        free(ctx);
        return -EIO;
    }

    /* Issue SET to restore AMR bridge sensitivity on power-up. */
    rc = reg_write(ctx->fd, MMC5983MA_REG_CTRL0, MMC5983MA_CTRL0_SET);
    if (rc != 0) {
        close(ctx->fd);
        free(ctx);
        return rc;
    }

    /*
     * Allow SET pulse to complete.  Datasheet states SET operation
     * completes within 500 µs; wait 2 ms to be safe.
     */
    {
        static const struct timespec set_wait = {.tv_sec = 0,
                                                 .tv_nsec = 2000000L};
        nanosleep(&set_wait, NULL);
    }

    /* Configure bandwidth: 100 Hz (CTRL1[1:0] = 0b10). */
    rc = reg_write(ctx->fd, MMC5983MA_REG_CTRL1, MMC5983MA_CTRL1_BW_100HZ);
    if (rc != 0) {
        close(ctx->fd);
        free(ctx);
        return rc;
    }

    /* Enable continuous measurement at 100 Hz ODR (CTRL2 = 0x16). */
    rc = reg_write(ctx->fd, MMC5983MA_REG_CTRL2, MMC5983MA_CTRL2_INIT);
    if (rc != 0) {
        close(ctx->fd);
        free(ctx);
        return rc;
    }

    *ctx_out = ctx;
    return 0;
}

void mag_mmc5983ma_close(mmc5983ma_ctx_t *ctx) {
    if (ctx == NULL) {
        return;
    }
    close(ctx->fd);
    free(ctx);
}

int mag_mmc5983ma_set(mmc5983ma_ctx_t *ctx) {
    static const struct timespec set_wait = {.tv_sec = 0, .tv_nsec = 2000000L};
    int                          rc;

    if (ctx == NULL) {
        return -EINVAL;
    }

    rc = reg_write(ctx->fd, MMC5983MA_REG_CTRL0, MMC5983MA_CTRL0_SET);
    if (rc != 0) {
        return rc;
    }
    nanosleep(&set_wait, NULL);
    return 0;
}

int mag_mmc5983ma_read_raw(mmc5983ma_ctx_t *ctx, mmc5983ma_raw_t *raw,
                           unsigned int timeout_ms) {
    /*
     * 7 bytes: XOUT_MSB (0x00) through XYZ_LSB2 (0x06).
     * Burst-read from register 0x00.
     */
    uint8_t buf[7];
    int     rc;

    if (ctx == NULL || raw == NULL) {
        return -EINVAL;
    }

    rc = wait_meas_done(ctx->fd, timeout_ms);
    if (rc != 0) {
        return rc;
    }

    rc = reg_read(ctx->fd, MMC5983MA_REG_XOUT_MSB, buf, sizeof(buf));
    if (rc != 0) {
        return rc;
    }

    /*
     * 18-bit reconstruction (X example):
     *   buf[0] = Xout[17:10]  → shift left 10
     *   buf[1] = Xout[9:2]    → shift left  2
     *   buf[6] bits [7:6] = Xout[1:0] → shift right 6, mask 0x03
     *
     * Y: buf[2] << 10, buf[3] << 2, (buf[6] >> 4) & 0x03
     * Z: buf[4] << 10, buf[5] << 2, (buf[6] >> 2) & 0x03
     */
    raw->x = ((uint32_t)buf[0] << 10U) | ((uint32_t)buf[1] << 2U) |
             (((uint32_t)buf[6] >> 6U) & 0x03U);

    raw->y = ((uint32_t)buf[2] << 10U) | ((uint32_t)buf[3] << 2U) |
             (((uint32_t)buf[6] >> 4U) & 0x03U);

    raw->z = ((uint32_t)buf[4] << 10U) | ((uint32_t)buf[5] << 2U) |
             (((uint32_t)buf[6] >> 2U) & 0x03U);

    return 0;
}

int mag_mmc5983ma_read(mmc5983ma_ctx_t *ctx, mmc5983ma_sample_t *sample,
                       unsigned int timeout_ms) {
    mmc5983ma_raw_t raw;
    int             rc;

    if (ctx == NULL || sample == NULL) {
        return -EINVAL;
    }

    rc = mag_mmc5983ma_read_raw(ctx, &raw, timeout_ms);
    if (rc != 0) {
        return rc;
    }

    /*
     * Convert unsigned 18-bit counts to signed nt100.
     *
     *   Zero-field output = MMC5983MA_ZERO_OFFSET = 131072 (2^17).
     *   Sensitivity       = 16384 LSB/G.
     *   1 G               = 100 µT = 1000 nt100.
     *   1 LSB             = 10000 nt100 / 16384.
     *
     *   nt100 = ((int32_t)raw - 131072) * 10000 / 16384
     *
     * Intermediate: ((int32_t)raw - 131072) is at most ±131071.
     * After × 10000: ±1 310 710 000 — within int32_t range (±2 147 483 647).
     */
    sample->x_nt100 = ((int32_t)raw.x - (int32_t)MMC5983MA_ZERO_OFFSET) *
                      10000 / (int32_t)MMC5983MA_SENS_LSB_PER_G;

    sample->y_nt100 = ((int32_t)raw.y - (int32_t)MMC5983MA_ZERO_OFFSET) *
                      10000 / (int32_t)MMC5983MA_SENS_LSB_PER_G;

    sample->z_nt100 = ((int32_t)raw.z - (int32_t)MMC5983MA_ZERO_OFFSET) *
                      10000 / (int32_t)MMC5983MA_SENS_LSB_PER_G;

    return 0;
}
