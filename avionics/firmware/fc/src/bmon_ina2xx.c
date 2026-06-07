/**
 * @file    bmon_ina2xx.c
 * @brief   INA219 / INA226 battery voltage / current monitor driver — implementation.
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
 * Register write sequence:
 *   buf[0] = reg; buf[1] = val_hi; buf[2] = val_lo
 *   write(fd, buf, 3)
 *
 * References:
 *   [1] INA219 Datasheet SBOS448G, Texas Instruments.
 *   [2] INA226 Datasheet SBOS547E, Texas Instruments.
 *   [3] Linux i2c-dev interface — Documentation/i2c/dev-interface.rst.
 *   [4] PDB-2.md — Serenity UAV Power Distribution Board specification.
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
    int             fd;                /**< Open /dev/i2c-N file descriptor. */
    bmon_ina_type_t type;              /**< INA219 or INA226. */
    uint32_t        current_lsb_ua;    /**< INA226 current LSB in µA (0 = voltage-only mode). */
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

/**
 * @brief Write a 16-bit big-endian value to a device register.
 *
 * @param fd   Open i2c-dev file descriptor.
 * @param reg  Register address to write.
 * @param val  16-bit value to write (will be sent big-endian).
 * @return 0 on success, -EIO on error.
 */
static int reg_write16(int fd, uint8_t reg, uint16_t val)
{
    uint8_t buf[3];

    buf[0] = reg;
    buf[1] = (uint8_t)(val >> 8U);
    buf[2] = (uint8_t)(val & 0xFFU);

    if (write(fd, buf, 3U) != 3) {
        return -EIO;
    }

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

/* ---------------------------------------------------------------------------
 * INA226-only current-sense API
 * ---------------------------------------------------------------------------*/

int bmon_ina226_configure_shunt(bmon_ina2xx_ctx_t *ctx,
                                uint32_t           shunt_mohm,
                                uint32_t           imax_ma,
                                uint32_t          *current_lsb_ua_out)
{
    uint32_t current_lsb_ua;
    uint32_t cal;
    int      rc;

    if (ctx == NULL) {
        return -EINVAL;
    }
    if (ctx->type != BMON_INA_INA226) {
        return -ENOTSUP;
    }
    if (shunt_mohm == 0U || imax_ma == 0U) {
        return -EINVAL;
    }

    /*
     * Current LSB in microamps: CURRENT_LSB = imax_ma × 1000 / 32768 µA.
     * Use ceiling to ensure full-scale fits in 16 bits without overflow.
     * Maximum intermediate: 150000 mA × 1000 = 150 000 000 µA — fits in uint32_t.
     */
    current_lsb_ua = ((imax_ma * 1000U) + 32767U) / 32768U;

    /*
     * Calibration register per INA226 datasheet §8.5:
     *   CAL = floor(0.00512 / (CURRENT_LSB_A × R_SHUNT_Ω))
     *       = floor(5120000 / (current_lsb_ua × shunt_mohm / 1000))
     *       = floor(5120000000 / (current_lsb_ua × shunt_mohm))
     *
     * Intermediate: 5120000000 fits in uint64_t.
     */
    {
        uint64_t numerator   = 5120000000ULL;
        uint64_t denominator = (uint64_t)current_lsb_ua * (uint64_t)shunt_mohm;
        if (denominator == 0U) {
            return -EINVAL;
        }
        cal = (uint32_t)(numerator / denominator);
        if (cal > 0xFFFFU) {
            cal = 0xFFFFU;  /* Clamp to 16-bit register width. */
        }
    }

    rc = reg_write16(ctx->fd, INA226_REG_CALIBRATION, (uint16_t)cal);
    if (rc != 0) {
        return rc;
    }

    ctx->current_lsb_ua = current_lsb_ua;

    if (current_lsb_ua_out != NULL) {
        *current_lsb_ua_out = current_lsb_ua;
    }

    return 0;
}

int bmon_ina226_read_current_ma(bmon_ina2xx_ctx_t *ctx, int32_t *current_ma)
{
    uint16_t reg_val;
    int      rc;

    if (ctx == NULL || current_ma == NULL) {
        return -EINVAL;
    }
    if (ctx->type != BMON_INA_INA226) {
        return -ENOTSUP;
    }

    rc = reg_read16(ctx->fd, INA226_REG_CURRENT, &reg_val);
    if (rc != 0) {
        return rc;
    }

    /*
     * INA226 current register (0x04) is a signed 16-bit two's-complement
     * value where each LSB = ctx->current_lsb_ua µA.
     *
     * current_ma = (int16_t)reg_val × current_lsb_ua / 1000
     *
     * Maximum intermediate: 32767 × 2289 = 74 983 263 µA — within int32_t range.
     * current_lsb_ua is 0 in voltage-only mode; result is 0 mA (no division by zero).
     */
    if (ctx->current_lsb_ua == 0U) {
        *current_ma = 0;
    } else {
        int32_t raw = (int32_t)(int16_t)reg_val;
        *current_ma = (raw * (int32_t)ctx->current_lsb_ua) / 1000;
    }

    return 0;
}

int bmon_ina226_read_power_mw(bmon_ina2xx_ctx_t *ctx, uint32_t *power_mw)
{
    uint16_t reg_val;
    int      rc;

    if (ctx == NULL || power_mw == NULL) {
        return -EINVAL;
    }
    if (ctx->type != BMON_INA_INA226) {
        return -ENOTSUP;
    }

    rc = reg_read16(ctx->fd, INA226_REG_POWER, &reg_val);
    if (rc != 0) {
        return rc;
    }

    /*
     * INA226 power register (0x03) is unsigned 16-bit.
     * Each LSB = 25 × current_lsb_ua µA × bus_V (reported in mW here).
     * power_lsb_uw = 25 × current_lsb_ua µW (since bus LSB is 1.25 mV per LSB
     * and V × I gives µW when I is in µA).
     *
     * power_mw = (uint32_t)reg_val × 25 × current_lsb_ua / 1 000 000
     *
     * Maximum intermediate (uint64_t): 65535 × 25 × 4578 = 7 495 403 250 — fits.
     */
    if (ctx->current_lsb_ua == 0U) {
        *power_mw = 0U;
    } else {
        uint64_t uw = (uint64_t)reg_val * 25ULL * (uint64_t)ctx->current_lsb_ua;
        *power_mw = (uint32_t)(uw / 1000000ULL);
    }

    return 0;
}

int bmon_ina226_configure_alert(bmon_ina2xx_ctx_t *ctx,
                                uint16_t           alert_mask,
                                uint16_t           alert_limit)
{
    int rc;

    if (ctx == NULL) {
        return -EINVAL;
    }
    if (ctx->type != BMON_INA_INA226) {
        return -ENOTSUP;
    }

    rc = reg_write16(ctx->fd, INA226_REG_ALERT_LIMIT, alert_limit);
    if (rc != 0) {
        return rc;
    }

    return reg_write16(ctx->fd, INA226_REG_MASK_ENABLE, alert_mask);
}
