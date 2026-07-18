/**
 * @file    mag_qmc5883l.c
 * @brief   QMC5883L 3-axis magnetometer driver — implementation.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Implements the QMC5883L driver described in mag_qmc5883l.h.
 * Uses Linux userspace i2c-dev (ioctl(I2C_SLAVE) + read/write syscalls).
 *
 * I2C protocol:
 *   Write N bytes : write(fd, buf, N)   where buf[0] = register address
 *   Burst read    : write(fd, &reg, 1) then read(fd, buf, N)
 *
 * References:
 *   [1] QMC5883L Datasheet Rev. 1.0, QST Corporation.
 *   [2] Linux i2c-dev interface — Documentation/i2c/dev-interface.rst.
 *   [3] POSIX.1-2017 — nanosleep(2) for sub-millisecond polling interval.
 *
 * Target platform: PocketBeagle 2 Industrial (AM6254), Debian Trixie.
 */

#include "mag_qmc5883l.h"

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

struct qmc5883l_ctx {
    int fd; /**< Open file descriptor for /dev/i2c-N. */
};

/* ---------------------------------------------------------------------------
 * Internal helpers
 * ---------------------------------------------------------------------------*/

/**
 * @brief Write a single byte to a device register.
 *
 * @param fd   Open i2c-dev file descriptor (slave address already set).
 * @param reg  Register address.
 * @param val  Value to write.
 * @return 0 on success, -EIO on write error.
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
 * @brief Read @p len bytes starting at register @p reg into @p buf.
 *
 * Sets the internal register pointer by writing the register address,
 * then performs a burst read of @p len bytes.
 *
 * @param fd   Open i2c-dev file descriptor.
 * @param reg  Starting register address.
 * @param buf  Destination buffer (must be at least @p len bytes).
 * @param len  Number of bytes to read.
 * @return 0 on success, -EIO on error.
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
 * @brief Read the STATUS register and return the raw byte.
 *
 * @param fd      Open i2c-dev file descriptor.
 * @param status  Destination for the STATUS register value.
 * @return 0 on success, -EIO on error.
 */
static int read_status(int fd, uint8_t *status) {
    return reg_read(fd, QMC5883L_REG_STATUS, status, 1U);
}

/**
 * @brief Poll STATUS.DRDY until set or @p timeout_ms expires.
 *
 * Polls every 2 ms (nanosleep) to avoid hammering the I2C bus.
 * When timeout_ms == 0 the function returns immediately without polling.
 *
 * @param fd         Open i2c-dev file descriptor.
 * @param timeout_ms Maximum wait in milliseconds (0 = no wait).
 * @return 0 when DRDY is set, -ETIMEDOUT if not set within timeout,
 *         -EIO on read error.
 */
static int wait_drdy(int fd, unsigned int timeout_ms) {
    /* 2 ms poll interval — well within 10 ms ODR minimum period. */
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
        rc = read_status(fd, &status);
        if (rc != 0) {
            return rc;
        }
        if ((status & QMC5883L_STATUS_DRDY) != 0U) {
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

int mag_qmc5883l_open(const char *i2c_dev, qmc5883l_ctx_t **ctx_out) {
    qmc5883l_ctx_t *ctx;
    uint8_t         chip_id;
    int             rc;

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

    /* Set the I2C slave address. */
    if (ioctl(ctx->fd, I2C_SLAVE, (long)QMC5883L_I2C_ADDR) < 0) {
        rc = -errno;
        close(ctx->fd);
        free(ctx);
        return rc;
    }

    /* Verify chip identity before touching configuration registers. */
    rc = reg_read(ctx->fd, QMC5883L_REG_CHIP_ID, &chip_id, 1U);
    if (rc != 0) {
        close(ctx->fd);
        free(ctx);
        return rc;
    }
    if (chip_id != QMC5883L_CHIP_ID) {
        close(ctx->fd);
        free(ctx);
        return -EIO;
    }

    /* Datasheet-specified initialisation sequence. */
    rc = reg_write(ctx->fd, QMC5883L_REG_CTRL2, QMC5883L_CTRL2_INIT);
    if (rc != 0) {
        close(ctx->fd);
        free(ctx);
        return rc;
    }

    rc = reg_write(ctx->fd, QMC5883L_REG_SET_RESET, QMC5883L_SET_RESET_VAL);
    if (rc != 0) {
        close(ctx->fd);
        free(ctx);
        return rc;
    }

    rc = reg_write(ctx->fd, QMC5883L_REG_CTRL1, QMC5883L_CTRL1_INIT);
    if (rc != 0) {
        close(ctx->fd);
        free(ctx);
        return rc;
    }

    *ctx_out = ctx;
    return 0;
}

void mag_qmc5883l_close(qmc5883l_ctx_t *ctx) {
    if (ctx == NULL) {
        return;
    }
    close(ctx->fd);
    free(ctx);
}

int mag_qmc5883l_read_raw(qmc5883l_ctx_t *ctx, qmc5883l_raw_t *raw,
                          unsigned int timeout_ms) {
    uint8_t buf[7]; /* XOUT_L … STATUS (regs 0x00–0x06, 7 bytes) */
    int     rc;

    if (ctx == NULL || raw == NULL) {
        return -EINVAL;
    }

    rc = wait_drdy(ctx->fd, timeout_ms);
    if (rc != 0) {
        return rc;
    }

    /* Burst-read six data bytes + status byte starting at XOUT_L (0x00). */
    rc = reg_read(ctx->fd, QMC5883L_REG_XOUT_L, buf, sizeof(buf));
    if (rc != 0) {
        return rc;
    }

    /*
     * Register byte order: little-endian per datasheet.
     *   buf[0] = XOUT_L, buf[1] = XOUT_H
     *   buf[2] = YOUT_L, buf[3] = YOUT_H
     *   buf[4] = ZOUT_L, buf[5] = ZOUT_H
     *   buf[6] = STATUS
     *
     * Cast to uint8_t before widening to avoid signed-extension of the
     * high byte before the OR.
     */
    raw->x = (int16_t)(((uint16_t)buf[0]) | ((uint16_t)buf[1] << 8U));
    raw->y = (int16_t)(((uint16_t)buf[2]) | ((uint16_t)buf[3] << 8U));
    raw->z = (int16_t)(((uint16_t)buf[4]) | ((uint16_t)buf[5] << 8U));

    return 0;
}

int mag_qmc5883l_read(qmc5883l_ctx_t *ctx, qmc5883l_sample_t *sample,
                      unsigned int timeout_ms) {
    uint8_t        buf[7];
    int            rc;
    uint8_t        status;
    qmc5883l_raw_t raw;

    if (ctx == NULL || sample == NULL) {
        return -EINVAL;
    }

    rc = wait_drdy(ctx->fd, timeout_ms);
    if (rc != 0) {
        return rc;
    }

    /* Burst-read 7 bytes: six data bytes + STATUS. */
    rc = reg_read(ctx->fd, QMC5883L_REG_XOUT_L, buf, sizeof(buf));
    if (rc != 0) {
        return rc;
    }

    status = buf[6];

    raw.x = (int16_t)(((uint16_t)buf[0]) | ((uint16_t)buf[1] << 8U));
    raw.y = (int16_t)(((uint16_t)buf[2]) | ((uint16_t)buf[3] << 8U));
    raw.z = (int16_t)(((uint16_t)buf[4]) | ((uint16_t)buf[5] << 8U));

    /*
     * Scale raw LSB counts to nt100 (units of 100 nT).
     *
     *   Sensitivity: 12000 LSB/G = 120 LSB/(100 nT) = 120 LSB/nt100
     *   nt100 = raw × 100 / 120
     *
     * Integer arithmetic: multiply first to preserve precision.
     * Intermediate range: ±32767 × 100 = ±3 276 700, fits in int32_t.
     */
    sample->x_nt100 = ((int32_t)raw.x * 100) / 120;
    sample->y_nt100 = ((int32_t)raw.y * 100) / 120;
    sample->z_nt100 = ((int32_t)raw.z * 100) / 120;

    sample->overflow = ((status & QMC5883L_STATUS_OVL) != 0U);

    return 0;
}
