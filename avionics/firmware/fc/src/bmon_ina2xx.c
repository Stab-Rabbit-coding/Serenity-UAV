/**
 * @file    bmon_ina2xx.c
 * @brief   INA219 / INA226 battery voltage monitor driver — implementation.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Implements the INA219/INA226 driver described in bmon_ina2xx.h.
 * Both devices expose 16-bit big-endian register values over I2C.
 *
 * Register read sequence for both devices:
 *   write(fd, &reg, 1)       — set register pointer
 *   read(fd, buf, 2)         — read 16-bit big-endian value
 *   val = (buf[0] << 8) | buf[1]
 *
 * References:
 *   [1] INA219 Datasheet SBOS448G, Texas Instruments.
 *   [2] INA226 Datasheet SBOS547E, Texas Instruments.
 *   [3] Linux i2c-dev interface — Documentation/i2c/dev-interface.rst.
 *
 * Target platform: PocketBeagle 2 Industrial (AM6254), Debian Trixie.
 */

#include "bmon_ina2xx.h"

#include <errno.h>
#include <fcntl.h>
#include <linux/i2c-dev.h>
#include <stdint.h>
#include <stdlib.h>
#include <sys/ioctl.h>
#include <unistd.h>

/* ---------------------------------------------------------------------------
 * Internal context
 * ---------------------------------------------------------------------------*/

struct bmon_ina2xx_ctx {
    int             fd;    /**< Open /dev/i2c-N file descriptor. */
    bmon_ina_type_t type;  /**< INA219 or INA226. */
};

/* ---------------------------------------------------------------------------
 * Internal helpers
 * ---------------------------------------------------------------------------*/

/**
 * @brief Read a 16-bit big-endian register value from the device.
 *
 * @param fd   Open i2c-dev file descriptor.
 * @param reg  Register address to read.
 * @param val  Destination for the 16-bit register value.
 * @return 0 on success, -EIO on error.
 */
static int reg_read16(int fd, uint8_t reg, uint16_t *val)
{
    uint8_t buf[2];

    /* Set register pointer. */
    if (write(fd, &reg, 1U) != 1) {
        return -EIO;
    }

    /* Read 2 bytes (big-endian). */
    if (read(fd, buf, 2U) != 2) {
        return -EIO;
    }

    *val = ((uint16_t)buf[0] << 8U) | (uint16_t)buf[1];
    return 0;
}

/* ---------------------------------------------------------------------------
 * Public API
 * ---------------------------------------------------------------------------*/

int bmon_ina2xx_open(const char *i2c_dev,
                     bmon_ina_type_t type,
                     bmon_ina2xx_ctx_t **ctx_out)
{
    bmon_ina2xx_ctx_t *ctx;
    uint16_t           die_id;
    int                rc;

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

    if (ioctl(ctx->fd, I2C_SLAVE, (long)INA2XX_I2C_ADDR) < 0) {
        rc = -errno;
        close(ctx->fd);
        free(ctx);
        return rc;
    }

    if (type == BMON_INA_AUTO) {
        /*
         * Probe by reading die-ID register 0xFF.
         * INA226 returns 0x2260; INA219 has no die-ID register and the
         * read will return a mirror value or undefined data that won't
         * be 0x2260.
         */
        rc = reg_read16(ctx->fd, INA226_REG_DIE_ID, &die_id);
        if (rc != 0) {
            /* Cannot read die-ID; assume INA219 for safety. */
            ctx->type = BMON_INA_INA219;
        } else if (die_id == INA226_DIE_ID) {
            ctx->type = BMON_INA_INA226;
        } else {
            ctx->type = BMON_INA_INA219;
        }
    } else {
        ctx->type = type;
    }

    *ctx_out = ctx;
    return 0;
}

void bmon_ina2xx_close(bmon_ina2xx_ctx_t *ctx)
{
    if (ctx == NULL) {
        return;
    }
    close(ctx->fd);
    free(ctx);
}

bmon_ina_type_t bmon_ina2xx_get_type(const bmon_ina2xx_ctx_t *ctx)
{
    if (ctx == NULL) {
        return BMON_INA_AUTO;
    }
    return ctx->type;
}

int bmon_ina2xx_read_mv(bmon_ina2xx_ctx_t *ctx, uint32_t *voltage_mv)
{
    uint16_t reg_val;
    int      rc;

    if (ctx == NULL || voltage_mv == NULL) {
        return -EINVAL;
    }

    if (ctx->type == BMON_INA_INA226) {
        rc = reg_read16(ctx->fd, INA226_REG_BUS_VOLT, &reg_val);
        if (rc != 0) {
            return rc;
        }
        /*
         * INA226: 1.25 mV per LSB (1250 µV per LSB).
         * voltage_mv = (uint32_t)reg_val × 1250 / 1000
         *
         * Maximum reg_val = 65535; 65535 × 1250 = 81 918 750 — within
         * uint32_t range (max 4 294 967 295).
         */
        *voltage_mv = ((uint32_t)reg_val * INA226_LSB_UV) / 1000U;
    } else {
        /* INA219 (default). */
        rc = reg_read16(ctx->fd, INA219_REG_BUS_VOLT, &reg_val);
        if (rc != 0) {
            return rc;
        }
        /*
         * INA219 bus voltage register 0x02:
         *   Bits [15:3] = BD[12:0] — voltage in 4 mV steps.
         *   Bit  1      = CNVR — conversion ready flag (not voltage data).
         *   Bit  0      = OVF  — math overflow flag (not voltage data).
         *
         * Shift right 3 to extract voltage bits, then multiply by 4 mV.
         * Maximum BD = 8191; 8191 × 4 = 32764 mV — within uint32_t.
         */
        *voltage_mv = (uint32_t)(reg_val >> 3U) * INA219_LSB_MV;
    }

    return 0;
}
