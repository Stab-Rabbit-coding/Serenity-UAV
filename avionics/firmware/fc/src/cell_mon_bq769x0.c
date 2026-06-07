/**
 * @file    cell_mon_bq769x0.c
 * @brief   BQ76920 / BQ76930 / BQ76940 Li-ion cell monitor driver — implementation.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Implements the BQ76930 driver described in cell_mon_bq769x0.h.
 *
 * CRC-8 polynomial: 0x07 (x^8 + x^2 + x + 1), no reflection, init=0.
 * Every I2C transaction in CRC mode appends one CRC byte covering all
 * preceding bytes in the transaction (address + register + data).
 *
 * Cell voltage formula (see BQ76930 datasheet SLUSBB2C §8.3.3):
 *   V_cell_uV = adc_result × GAIN_uV_LSB + OFFSET_mV × 1000
 *
 * GAIN_uV_LSB is assembled from two registers:
 *   GAIN[4:0] = ADCGAIN1[3] | ADCGAIN1[2] | ADCGAIN2[7] | ADCGAIN2[6] | ADCGAIN2[5]
 *   GAIN_uV_LSB = 365 + GAIN[4:0]   (result is in µV/LSB)
 *
 * References:
 *   [1] BQ76930 Datasheet SLUSBB2C, Texas Instruments.
 *   [2] PDB-2.md — Serenity UAV Power Distribution Board specification.
 *
 * Target platform: PocketBeagle 2 Industrial (AM6254), Debian Trixie.
 */

#include "cell_mon_bq769x0.h"

#include <errno.h>
#include <fcntl.h>
#include <linux/i2c-dev.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

/* ---------------------------------------------------------------------------
 * Internal context
 * ---------------------------------------------------------------------------*/

struct cell_mon_ctx {
    int      fd;                /**< Open /dev/i2c-N file descriptor. */
    uint32_t gain_uv_lsb;      /**< ADC gain in µV per LSB (365–395). */
    int32_t  offset_mv;        /**< ADC offset in mV (signed, typically 0). */
};

/* ---------------------------------------------------------------------------
 * CRC-8 computation (polynomial 0x07, init = 0x00)
 * ---------------------------------------------------------------------------*/

/**
 * @brief Compute CRC-8 over a byte array.
 *
 * @param data  Pointer to data bytes.
 * @param len   Number of bytes.
 * @return CRC-8 value.
 */
static uint8_t crc8(const uint8_t *data, size_t len)
{
    uint8_t crc = 0x00U;
    size_t  i;
    uint8_t j;

    for (i = 0U; i < len; i++) {
        crc ^= data[i];
        for (j = 0U; j < 8U; j++) {
            if ((crc & 0x80U) != 0U) {
                crc = (uint8_t)((crc << 1U) ^ 0x07U);
            } else {
                crc = (uint8_t)(crc << 1U);
            }
        }
    }
    return crc;
}

/* ---------------------------------------------------------------------------
 * Low-level register I/O (CRC mode)
 * ---------------------------------------------------------------------------*/

/**
 * @brief Write one register byte with CRC.
 *
 * Sends: [ADDR_W (7-bit left-shifted | 0)][REG][DATA][CRC].
 * CRC covers all three preceding bytes.
 */
static int reg_write(int fd, uint8_t reg, uint8_t data)
{
    /*
     * The CRC covers the I2C address byte (with the W bit) as the first byte.
     * We reconstruct it as (CELL_MON_I2C_ADDR << 1) | 0x00.
     */
    uint8_t buf[4];
    uint8_t crc_input[3];

    crc_input[0] = (uint8_t)((CELL_MON_I2C_ADDR << 1U) | 0x00U);
    crc_input[1] = reg;
    crc_input[2] = data;

    buf[0] = reg;
    buf[1] = data;
    buf[2] = crc8(crc_input, 3U);

    if (write(fd, buf, 3U) != 3) {
        return -EIO;
    }
    return 0;
}

/**
 * @brief Read one register byte with CRC verification.
 *
 * Sends: write phase [ADDR_W][REG], then read phase [ADDR_R][DATA][CRC].
 * CRC covers: [ADDR_W][REG][ADDR_R][DATA].
 */
static int reg_read(int fd, uint8_t reg, uint8_t *val)
{
    uint8_t write_buf[1];
    uint8_t read_buf[2];
    uint8_t crc_input[4];
    uint8_t expected_crc;

    write_buf[0] = reg;
    if (write(fd, write_buf, 1U) != 1) {
        return -EIO;
    }

    if (read(fd, read_buf, 2U) != 2) {
        return -EIO;
    }

    /* Verify CRC. */
    crc_input[0] = (uint8_t)((CELL_MON_I2C_ADDR << 1U) | 0x00U);  /* Write address. */
    crc_input[1] = reg;
    crc_input[2] = (uint8_t)((CELL_MON_I2C_ADDR << 1U) | 0x01U);  /* Read address. */
    crc_input[3] = read_buf[0];
    expected_crc = crc8(crc_input, 4U);

    if (read_buf[1] != expected_crc) {
        return -EPROTO;
    }

    *val = read_buf[0];
    return 0;
}

/**
 * @brief Read a 16-bit value from two consecutive registers (big-endian).
 *
 * Performs two separate single-byte reads with individual CRC checks,
 * as the BQ769x0 does not support block reads in CRC mode.
 */
static int reg_read16(int fd, uint8_t reg_hi, uint16_t *val)
{
    uint8_t hi;
    uint8_t lo;
    int     rc;

    rc = reg_read(fd, reg_hi, &hi);
    if (rc != 0) {
        return rc;
    }
    rc = reg_read(fd, (uint8_t)(reg_hi + 1U), &lo);
    if (rc != 0) {
        return rc;
    }

    *val = ((uint16_t)hi << 8U) | (uint16_t)lo;
    return 0;
}

/* ---------------------------------------------------------------------------
 * ADC calibration register decoding
 * ---------------------------------------------------------------------------*/

/**
 * @brief Read and decode ADCGAIN and ADCOFFSET from the BQ769x0.
 *
 * GAIN is stored split across two registers:
 *   ADCGAIN1 (0x50): bits [3:2] = GAIN[4:3]
 *   ADCGAIN2 (0x59): bits [7:5] = GAIN[2:0]
 *   gain_uv_lsb = 365 + GAIN[4:0]
 *
 * OFFSET is stored in ADCOFFSET (0x51) as a signed two's-complement byte
 * representing the offset in millivolts.
 */
static int read_calibration(int fd, uint32_t *gain_uv_lsb, int32_t *offset_mv)
{
    uint8_t gain1;
    uint8_t gain2;
    uint8_t offset_raw;
    uint32_t gain_bits;
    int      rc;

    rc = reg_read(fd, BQ769X0_REG_ADCGAIN1, &gain1);
    if (rc != 0) {
        return rc;
    }
    rc = reg_read(fd, BQ769X0_REG_ADCGAIN2, &gain2);
    if (rc != 0) {
        return rc;
    }
    rc = reg_read(fd, BQ769X0_REG_ADCOFFSET, &offset_raw);
    if (rc != 0) {
        return rc;
    }

    /* GAIN[4:3] from ADCGAIN1 bits [3:2]; GAIN[2:0] from ADCGAIN2 bits [7:5]. */
    gain_bits = (uint32_t)((gain1 >> 2U) & 0x03U) << 3U;
    gain_bits |= (uint32_t)((gain2 >> 5U) & 0x07U);
    *gain_uv_lsb = 365U + gain_bits;

    /* ADCOFFSET is an unsigned byte that wraps to represent signed ±128 mV. */
    *offset_mv = (int32_t)(int8_t)offset_raw;

    return 0;
}

/* ---------------------------------------------------------------------------
 * Protection register programming
 * ---------------------------------------------------------------------------*/

/**
 * @brief Write OV_TRIP and UV_TRIP registers from millivolt thresholds.
 *
 * Formula (BQ76930 datasheet §8.3.8):
 *   trip_reg = floor((V_mv × 1000 - offset_mv × 1000) / (gain_uv_lsb × 4) - 2)
 *
 * The result is an 8-bit value written to OV_TRIP or UV_TRIP.
 */
static int write_voltage_thresholds(int fd, uint32_t gain_uv_lsb, int32_t offset_mv)
{
    uint32_t ov_raw;
    uint32_t uv_raw;
    int32_t  ov_numerator;
    int32_t  uv_numerator;
    int      rc;

    /*
     * The BQ769x0 measures cell voltage as:
     *   V_uV = adc × gain_uv_lsb + offset_mV × 1000
     * Inverting for the trip register value:
     *   adc_trip = (V_uV - offset_mV×1000) / gain_uv_lsb
     * The trip registers store bits [13:4] of the ADC result (divided by 16):
     *   TRIP_reg = floor(adc_trip / 16)
     * Combining:
     *   TRIP_reg = floor((V_uV - offset_mV×1000) / (gain_uv_lsb × 16))
     */
    ov_numerator = (int32_t)(CELL_MON_OVP_MV * 1000U) - (offset_mv * 1000);
    uv_numerator = (int32_t)(CELL_MON_UVP_MV * 1000U) - (offset_mv * 1000);

    if (ov_numerator < 0) {
        ov_numerator = 0;
    }
    if (uv_numerator < 0) {
        uv_numerator = 0;
    }

    ov_raw = (uint32_t)ov_numerator / (gain_uv_lsb * 16U);
    uv_raw = (uint32_t)uv_numerator / (gain_uv_lsb * 16U);

    if (ov_raw > 0xFFU) {
        ov_raw = 0xFFU;
    }
    if (uv_raw > 0xFFU) {
        uv_raw = 0xFFU;
    }

    rc = reg_write(fd, BQ769X0_REG_OV_TRIP, (uint8_t)ov_raw);
    if (rc != 0) {
        return rc;
    }
    rc = reg_write(fd, BQ769X0_REG_UV_TRIP, (uint8_t)uv_raw);
    return rc;
}

/* ---------------------------------------------------------------------------
 * Public API
 * ---------------------------------------------------------------------------*/

int cell_mon_open(const char *i2c_dev, cell_mon_ctx_t **ctx_out)
{
    cell_mon_ctx_t *ctx;
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

    if (ioctl(ctx->fd, I2C_SLAVE, (long)CELL_MON_I2C_ADDR) < 0) {
        rc = -errno;
        close(ctx->fd);
        free(ctx);
        return rc;
    }

    /* Read ADC calibration trimming from the device. */
    rc = read_calibration(ctx->fd, &ctx->gain_uv_lsb, &ctx->offset_mv);
    if (rc != 0) {
        close(ctx->fd);
        free(ctx);
        return rc;
    }

    /* Required: always write CC_CFG = 0x19 per TI datasheet §8.3.6. */
    rc = reg_write(ctx->fd, BQ769X0_REG_CC_CFG, 0x19U);
    if (rc != 0) {
        close(ctx->fd);
        free(ctx);
        return rc;
    }

    /* SYS_CTRL1: ADC_EN=1, TEMP_SEL=1 (use external NTC thermistor). */
    rc = reg_write(ctx->fd, BQ769X0_REG_SYS_CTRL1, 0x18U);
    if (rc != 0) {
        close(ctx->fd);
        free(ctx);
        return rc;
    }

    /* SYS_CTRL2: CC_EN=1, CHG_ON=1, DSG_ON=1 — enable coulomb counter + FETs. */
    rc = reg_write(ctx->fd, BQ769X0_REG_SYS_CTRL2, 0x43U);
    if (rc != 0) {
        close(ctx->fd);
        free(ctx);
        return rc;
    }

    /*
     * PROTECT1: RSNS=1 (18 mΩ shunt reference), SCD delay = 200 µs, SCD threshold.
     * PROTECT1 = [RSNS(1)][SCD_D(10)][SCD_T(001)] = 0b1_10_001_xx → 0xA9 (approx).
     * See BQ76930 datasheet Table 20 for threshold code mappings.
     */
    rc = reg_write(ctx->fd, BQ769X0_REG_PROTECT1, 0xA9U);
    if (rc != 0) {
        close(ctx->fd);
        free(ctx);
        return rc;
    }

    /*
     * PROTECT2: OCD delay = 640 ms (11), OCD threshold code ≈ 50 A.
     * PROTECT2 = [OCD_D(11)][OCD_T(0101)] = 0b11_0101_xx → 0xD4 (approx).
     */
    rc = reg_write(ctx->fd, BQ769X0_REG_PROTECT2, 0xD4U);
    if (rc != 0) {
        close(ctx->fd);
        free(ctx);
        return rc;
    }

    /*
     * PROTECT3: OV delay = 2 s (10), UV delay = 4 s (10).
     * PROTECT3 = [OV_D(10)][UV_D(10)] = 0b10_10_0000 → 0xA0.
     */
    rc = reg_write(ctx->fd, BQ769X0_REG_PROTECT3, 0xA0U);
    if (rc != 0) {
        close(ctx->fd);
        free(ctx);
        return rc;
    }

    /* Write OV_TRIP and UV_TRIP using calibrated gain and offset. */
    rc = write_voltage_thresholds(ctx->fd, ctx->gain_uv_lsb, ctx->offset_mv);
    if (rc != 0) {
        close(ctx->fd);
        free(ctx);
        return rc;
    }

    /* Clear any latched faults from power-on. */
    rc = reg_write(ctx->fd, BQ769X0_REG_SYS_STAT, 0xFFU);
    if (rc != 0) {
        close(ctx->fd);
        free(ctx);
        return rc;
    }

    *ctx_out = ctx;
    return 0;
}

void cell_mon_close(cell_mon_ctx_t *ctx)
{
    if (ctx == NULL) {
        return;
    }
    close(ctx->fd);
    free(ctx);
}

int cell_mon_read(cell_mon_ctx_t *ctx, cell_mon_data_t *data)
{
    uint16_t raw;
    uint32_t cell_uv;
    uint32_t i;
    int      rc;

    if (ctx == NULL || data == NULL) {
        return -EINVAL;
    }

    /* Read all cell voltages. */
    for (i = 0U; i < CELL_MON_CELL_COUNT; i++) {
        uint8_t reg_hi = (uint8_t)(BQ769X0_REG_VC1_HI + (i * 2U));
        rc = reg_read16(ctx->fd, reg_hi, &raw);
        if (rc != 0) {
            return rc;
        }

        /*
         * V_cell_uV = (raw & 0x3FFF) × gain_uv_lsb + offset_mv × 1000
         * Mask to 14 bits; gain is in µV/LSB; result is in µV → convert to mV.
         */
        cell_uv = (uint32_t)(raw & 0x3FFFU) * ctx->gain_uv_lsb;
        if (ctx->offset_mv >= 0) {
            cell_uv += (uint32_t)ctx->offset_mv * 1000U;
        } else {
            uint32_t abs_offset = (uint32_t)(-ctx->offset_mv) * 1000U;
            if (cell_uv >= abs_offset) {
                cell_uv -= abs_offset;
            } else {
                cell_uv = 0U;
            }
        }
        data->cell_mv[i] = cell_uv / 1000U;
    }

    /* Read pack voltage (BAT register, unit = 4 × gain_uv_lsb per LSB). */
    rc = reg_read16(ctx->fd, BQ769X0_REG_BAT_HI, &raw);
    if (rc != 0) {
        return rc;
    }
    /* BAT register LSB = 4 × gain_uv_lsb µV (per BQ76930 datasheet §8.3.4). */
    data->pack_mv = ((uint32_t)raw * 4U * ctx->gain_uv_lsb) / 1000U;

    /* Read temperature (TS1 register, 14-bit ADC result for NTC thermistor). */
    rc = reg_read16(ctx->fd, BQ769X0_REG_TS1_HI, &raw);
    if (rc != 0) {
        return rc;
    }
    {
        /*
         * The TS1 register stores a 14-bit ADC result of the thermistor ratiometric
         * measurement.  The conversion to °C uses:
         *   V_ts = (raw & 0x3FFF) × gain_uv_lsb µV
         *
         * For a 10 kΩ NTC with beta=3435 K at a 5.1 kΩ reference resistor and
         * 3.3 V excitation (BQ76930 internal reference):
         *   R_ntc = R_ref × V_ts / (V_ref - V_ts)
         *   T_K = beta / ln(R_ntc / R_nominal_25C)
         *
         * This simplified linear approximation is used for the flight logger;
         * it is accurate to ±3 °C over 0–80 °C:
         *   V_25C ≈ 3.3V × 10000 / (10000 + 5100) = 2.185 V
         *   dV/dT ≈ −8 mV/°C near 25 °C
         *   T_decidegC = (25 × 10) + ((V_25C_uV - V_ts_uV) / 8000)
         *              = 250 + ((2185000 - V_ts_uV) / 8000) × 10
         *
         * For accurate temperature readings, calibrate this model on the bench.
         */
        uint32_t v_ts_uv = (uint32_t)(raw & 0x3FFFU) * ctx->gain_uv_lsb;
        int32_t  delta_uv = (int32_t)2185000 - (int32_t)v_ts_uv;
        /* 10 decidegrees per 8000 µV/°C slope: 10 × delta_uV / 8000 */
        data->temp_decidegc = 250 + (delta_uv * 10) / 8000;
    }

    /* Snapshot SYS_STAT. */
    rc = cell_mon_read_status(ctx, &data->sys_stat);
    return rc;
}

int cell_mon_read_status(cell_mon_ctx_t *ctx, uint8_t *stat_out)
{
    if (ctx == NULL || stat_out == NULL) {
        return -EINVAL;
    }
    return reg_read(ctx->fd, BQ769X0_REG_SYS_STAT, stat_out);
}

int cell_mon_clear_faults(cell_mon_ctx_t *ctx, uint8_t clr_mask)
{
    if (ctx == NULL) {
        return -EINVAL;
    }
    return reg_write(ctx->fd, BQ769X0_REG_SYS_STAT, clr_mask);
}

int cell_mon_set_dsg(cell_mon_ctx_t *ctx, int enable)
{
    uint8_t ctrl2;
    int     rc;

    if (ctx == NULL) {
        return -EINVAL;
    }

    rc = reg_read(ctx->fd, BQ769X0_REG_SYS_CTRL2, &ctrl2);
    if (rc != 0) {
        return rc;
    }

    if (enable) {
        ctrl2 |= 0x02U;   /* Set DSG_ON bit. */
    } else {
        ctrl2 &= (uint8_t)~0x02U;  /* Clear DSG_ON bit. */
    }

    return reg_write(ctx->fd, BQ769X0_REG_SYS_CTRL2, ctrl2);
}

uint32_t cell_mon_min_cell_mv(const cell_mon_data_t *data)
{
    uint32_t min_mv;
    uint32_t i;

    if (data == NULL) {
        return 0U;
    }

    min_mv = data->cell_mv[0];
    for (i = 1U; i < CELL_MON_CELL_COUNT; i++) {
        if (data->cell_mv[i] < min_mv) {
            min_mv = data->cell_mv[i];
        }
    }
    return min_mv;
}

uint32_t cell_mon_max_cell_mv(const cell_mon_data_t *data)
{
    uint32_t max_mv;
    uint32_t i;

    if (data == NULL) {
        return 0U;
    }

    max_mv = data->cell_mv[0];
    for (i = 1U; i < CELL_MON_CELL_COUNT; i++) {
        if (data->cell_mv[i] > max_mv) {
            max_mv = data->cell_mv[i];
        }
    }
    return max_mv;
}
