/**
 * @file    si5351.c
 * @brief   Si5351A DDS frequency synthesiser driver — implementation.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Register calculation method (Silicon Labs AN619, §4):
 *
 *   Choose integer output divider d = 14 (VCO = 14 × f_out ≈ 698 MHz,
 *   within the 600–900 MHz operating range of the PLLA VCO).
 *
 *   PLLA multiplier: a + b/c = (14 × f_out) / 25 MHz
 *   where a is the integer part and b/c is the reduced fractional part.
 *
 *   Intermediate register values (AN619 §4.1):
 *     P1 = 128×a + floor(128×b / c) − 512
 *     P2 = 128×b − c × floor(128×b / c)
 *     P3 = c
 *
 *   PLLA register map (registers 26–33):
 *     R26 = P3[15:8]          R27 = P3[7:0]
 *     R28 = P1[17:16]         R29 = P1[15:8]     R30 = P1[7:0]
 *     R31 = (P3[19:16]<<4) | P2[19:16]
 *     R32 = P2[15:8]          R33 = P2[7:0]
 *
 *   MS0 (CLK0 output divider = 14, integer mode):
 *     P1 = 128×14 − 512 = 1280 = 0x500
 *     P2 = 0,  P3 = 1
 *     Register 44 bit 6 (MS0_INT) = 1 for integer mode.
 *
 * References:
 *   [1] Silicon Labs AN619, "Manually Calculating Si5351 Registers," Rev 0.3.
 *   [2] Si5351A/B/C-B Datasheet, Skyworks, Rev 1.4.
 *   [3] Linux i2c-dev kernel documentation — /doc/i2c/dev-interface.rst
 */

#include "si5351.h"

#include <errno.h>
#include <fcntl.h>
#include <linux/i2c-dev.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

/* ---------------------------------------------------------------------------
 * Si5351A register addresses
 * ---------------------------------------------------------------------------*/

/** Device status register — SYS_INIT, LOL_A, LOL_B, LOS, REVID. */
#define REG_DEVICE_STATUS   (0U)

/** Output enable control: bit N = 0 → CLKn enabled, 1 → disabled. */
#define REG_OUTPUT_ENABLE   (3U)

/** CLK0 control: power-down, integer mode, source, invert, drive. */
#define REG_CLK0_CTRL       (16U)

/** PLLA Multisynth numerator registers 26–33 (MSNa). */
#define REG_MSNA_BASE       (26U)

/** MS0 (CLK0 output divider) registers 42–49. */
#define REG_MS0_BASE        (42U)

/** PLL reset register — bit 5 resets PLLA, bit 7 resets PLLB. */
#define REG_PLL_RESET       (177U)

/** Crystal load capacitance register. */
#define REG_XTAL_LOAD       (183U)

/* ---------------------------------------------------------------------------
 * Register field values
 * ---------------------------------------------------------------------------*/

/**
 * CLK0 control byte: powered on, integer mode, MS0 as source,
 * non-inverted, 8 mA output drive.
 * Bits: [7]=0 (on), [6]=1 (INT), [5:4]=11 (MS0 src), [3]=0 (normal),
 *       [2:0]=011 (8 mA).
 */
#define CLK0_CTRL_ON   ((uint8_t)(0x00U | (1U<<6) | (3U<<4) | 3U))

/**
 * CLK0 control byte: powered down.
 * Bit 7 = 1.  All other bits preserved to avoid re-configuration.
 */
#define CLK0_CTRL_OFF  ((uint8_t)(1U<<7))

/** PLL reset: reset PLLA (bit 5). */
#define PLL_RESET_PLLA ((uint8_t)(1U<<5))

/** Crystal load = 10 pF (bits [6:5] = 11, bits [1:0] = 10). */
#define XTAL_LOAD_10PF ((uint8_t)0xD2U)

/* ---------------------------------------------------------------------------
 * Precomputed PLLA register sets for each RCRS channel
 *
 * Each entry encodes the 8 bytes written to registers 26–33.
 * Calculation verified against AN619 Table 1 formulas.
 * Integer output divider MS0=14 is constant across all channels.
 *
 * Channel | f_out (MHz) | VCO (MHz)  | PLL mult (a + b/c)
 *   0     | 49.830      | 697.620    | 27 + 1131/1250
 *   1     | 49.845      | 697.830    | 27 + 2283/2500
 *   2     | 49.860      | 698.040    | 27 + 576/625
 *   3     | 49.875      | 698.250    | 27 + 93/100
 *   4     | 49.890      | 698.460    | 27 + 1173/1250
 * ---------------------------------------------------------------------------*/

typedef struct {
    uint32_t freq_hz;     /**< Output frequency in Hz */
    uint8_t  msna[8];     /**< Bytes for PLLA registers 26–33 */
} rcrs_channel_reg_t;

/**
 * @brief Pack PLLA parameters into the 8-byte register block.
 *
 * Parameters P1, P2, P3 are laid out as described in AN619 §4.1.
 * This macro is evaluated at compile time via designated initialiser.
 */
#define MSNA_REGS(p1, p2, p3)                              \
{                                                          \
    (uint8_t)(((p3) >> 8U) & 0xFFU),    /* R26 P3[15:8] */ \
    (uint8_t)((p3) & 0xFFU),            /* R27 P3[7:0]  */ \
    (uint8_t)(((p1) >> 16U) & 0x03U),   /* R28 P1[17:16]*/ \
    (uint8_t)(((p1) >> 8U) & 0xFFU),    /* R29 P1[15:8] */ \
    (uint8_t)((p1) & 0xFFU),            /* R30 P1[7:0]  */ \
    (uint8_t)((((p3) >> 12U) & 0xF0U) | (((p2) >> 16U) & 0x0FU)), /* R31 */ \
    (uint8_t)(((p2) >> 8U) & 0xFFU),    /* R32 P2[15:8] */ \
    (uint8_t)((p2) & 0xFFU)             /* R33 P2[7:0]  */ \
}

static const rcrs_channel_reg_t s_rcrs_channels[SI5351_RCRS_NUM_CHANNELS] = {
    /*
     * CH0: 49.830 MHz — VCO=697.620 MHz — mult=27+1131/1250
     *   P1 = 128*27 + floor(128*1131/1250) - 512 = 3456 + 115 - 512 = 3059
     *   P2 = 128*1131 - 1250*115 = 144768 - 143750 = 1018
     *   P3 = 1250
     */
    { SI5351_RCRS_CH0_HZ, MSNA_REGS(3059U, 1018U, 1250U) },

    /*
     * CH1: 49.845 MHz — VCO=697.830 MHz — mult=27+2283/2500
     *   P1 = 128*27 + floor(128*2283/2500) - 512 = 3456 + 116 - 512 = 3060
     *   P2 = 128*2283 - 2500*116 = 292224 - 290000 = 2224
     *   P3 = 2500
     */
    { SI5351_RCRS_CH1_HZ, MSNA_REGS(3060U, 2224U, 2500U) },

    /*
     * CH2: 49.860 MHz — VCO=698.040 MHz — mult=27+576/625
     *   P1 = 128*27 + floor(128*576/625) - 512 = 3456 + 117 - 512 = 3061
     *   P2 = 128*576 - 625*117 = 73728 - 73125 = 603
     *   P3 = 625
     */
    { SI5351_RCRS_CH2_HZ, MSNA_REGS(3061U, 603U, 625U) },

    /*
     * CH3: 49.875 MHz — VCO=698.250 MHz — mult=27+93/100
     *   P1 = 128*27 + floor(128*93/100) - 512 = 3456 + 119 - 512 = 3063
     *   P2 = 128*93 - 100*119 = 11904 - 11900 = 4
     *   P3 = 100
     */
    { SI5351_RCRS_CH3_HZ, MSNA_REGS(3063U, 4U, 100U) },

    /*
     * CH4: 49.890 MHz — VCO=698.460 MHz — mult=27+1173/1250
     *   P1 = 128*27 + floor(128*1173/1250) - 512 = 3456 + 120 - 512 = 3064
     *   P2 = 128*1173 - 1250*120 = 150144 - 150000 = 144
     *   P3 = 1250
     */
    { SI5351_RCRS_CH4_HZ, MSNA_REGS(3064U, 144U, 1250U) },
};

/*
 * MS0 registers 42–49 for integer output divider = 14.
 * Integer mode: P1 = 128*14 - 512 = 1280, P2 = 0, P3 = 1.
 * Register 44 bit 6 (MS0_INT) is set via CLK0_CTRL_ON instead.
 */
static const uint8_t s_ms0_regs[8] = MSNA_REGS(1280U, 0U, 1U);

/* ---------------------------------------------------------------------------
 * Driver context (internal)
 * ---------------------------------------------------------------------------*/

struct si5351_ctx {
    int      fd;           /**< File descriptor for /dev/i2c-N */
    uint8_t  i2c_addr;     /**< 7-bit I²C address */
    uint32_t clk0_freq_hz; /**< Currently programmed CLK0 frequency, or 0 */
};

/* ---------------------------------------------------------------------------
 * Internal helpers
 * ---------------------------------------------------------------------------*/

/**
 * @brief Write a single byte to a Si5351A register via i2c-dev.
 */
static int reg_write(const si5351_ctx_t *ctx, uint8_t reg, uint8_t val)
{
    uint8_t buf[2] = { reg, val };
    ssize_t n = write(ctx->fd, buf, sizeof(buf));
    if (n != (ssize_t)sizeof(buf)) {
        return (n < 0) ? -errno : -EIO;
    }
    return 0;
}

/**
 * @brief Write a block of consecutive registers starting at @c reg_base.
 */
static int reg_write_block(const si5351_ctx_t *ctx, uint8_t reg_base,
                           const uint8_t *data, size_t len)
{
    /* Prepend the starting register address in a single buffer. */
    uint8_t buf[32];
    if (len == 0U || len > (sizeof(buf) - 1U)) {
        return -EINVAL;
    }
    buf[0] = reg_base;
    (void)memcpy(&buf[1], data, len);

    ssize_t n = write(ctx->fd, buf, len + 1U);
    if (n != (ssize_t)(len + 1U)) {
        return (n < 0) ? -errno : -EIO;
    }
    return 0;
}

/* ---------------------------------------------------------------------------
 * Public API
 * ---------------------------------------------------------------------------*/

int si5351_open(int bus_num, uint8_t i2c_addr, si5351_ctx_t **ctx_out)
{
    if (ctx_out == NULL) {
        return -EINVAL;
    }

    /* Build device path. */
    char path[32];
    int n = snprintf(path, sizeof(path), "/dev/i2c-%d", bus_num);
    if (n < 0 || (size_t)n >= sizeof(path)) {
        return -EINVAL;
    }

    /* Open the I²C bus. */
    int fd = open(path, O_RDWR);
    if (fd < 0) {
        return -errno;
    }

    /* Bind to the Si5351A I²C address. */
    if (ioctl(fd, I2C_SLAVE, (long)i2c_addr) < 0) {
        int err = -errno;
        (void)close(fd);
        return err;
    }

    /* Allocate driver context. */
    si5351_ctx_t *ctx = (si5351_ctx_t *)calloc(1U, sizeof(*ctx));
    if (ctx == NULL) {
        (void)close(fd);
        return -ENOMEM;
    }
    ctx->fd        = fd;
    ctx->i2c_addr  = i2c_addr;
    ctx->clk0_freq_hz = 0U;

    int rc;

    /* Set crystal load capacitance to 10 pF (Si5351A default XTAL spec). */
    rc = reg_write(ctx, REG_XTAL_LOAD, XTAL_LOAD_10PF);
    if (rc != 0) {
        goto err_close;
    }

    /* Disable all outputs while programming. */
    rc = reg_write(ctx, REG_OUTPUT_ENABLE, 0xFFU);
    if (rc != 0) {
        goto err_close;
    }

    /* Power down all CLK outputs (registers 16–23). */
    for (uint8_t r = REG_CLK0_CTRL; r <= (REG_CLK0_CTRL + 7U); r++) {
        rc = reg_write(ctx, r, CLK0_CTRL_OFF);
        if (rc != 0) {
            goto err_close;
        }
    }

    *ctx_out = ctx;
    return 0;

err_close:
    (void)close(fd);
    free(ctx);
    return rc;
}

int si5351_set_rcrs_channel(si5351_ctx_t *ctx, unsigned int channel)
{
    if (ctx == NULL || channel >= SI5351_RCRS_NUM_CHANNELS) {
        return -EINVAL;
    }

    const rcrs_channel_reg_t *ch = &s_rcrs_channels[channel];
    int rc;

    /* Disable CLK0 output while reprogramming the PLL. */
    rc = reg_write(ctx, REG_OUTPUT_ENABLE, 0xFFU);
    if (rc != 0) { return rc; }

    rc = reg_write(ctx, REG_CLK0_CTRL, CLK0_CTRL_OFF);
    if (rc != 0) { return rc; }

    /* Program PLLA (MSNa, registers 26–33). */
    rc = reg_write_block(ctx, (uint8_t)REG_MSNA_BASE, ch->msna, sizeof(ch->msna));
    if (rc != 0) { return rc; }

    /* Program MS0 output divider (registers 42–49), integer div=14. */
    rc = reg_write_block(ctx, (uint8_t)REG_MS0_BASE, s_ms0_regs, sizeof(s_ms0_regs));
    if (rc != 0) { return rc; }

    /* Reset PLLA to phase-align outputs after frequency change (AN619 §4.4). */
    rc = reg_write(ctx, (uint8_t)REG_PLL_RESET, PLL_RESET_PLLA);
    if (rc != 0) { return rc; }

    /* Enable CLK0 output: integer mode, MS0 source, 8 mA drive. */
    rc = reg_write(ctx, REG_CLK0_CTRL, CLK0_CTRL_ON);
    if (rc != 0) { return rc; }

    /* Enable only CLK0 (bit 0 = 0 → enabled). */
    rc = reg_write(ctx, REG_OUTPUT_ENABLE, 0xFEU);
    if (rc != 0) { return rc; }

    ctx->clk0_freq_hz = ch->freq_hz;
    return 0;
}

int si5351_disable_clk0(si5351_ctx_t *ctx)
{
    if (ctx == NULL) { return -EINVAL; }

    int rc = reg_write(ctx, REG_CLK0_CTRL, CLK0_CTRL_OFF);
    if (rc == 0) {
        rc = reg_write(ctx, REG_OUTPUT_ENABLE, 0xFFU);
    }
    if (rc == 0) {
        ctx->clk0_freq_hz = 0U;
    }
    return rc;
}

uint32_t si5351_get_clk0_freq_hz(const si5351_ctx_t *ctx)
{
    return (ctx != NULL) ? ctx->clk0_freq_hz : 0U;
}

void si5351_close(si5351_ctx_t *ctx)
{
    if (ctx == NULL) { return; }

    /* Silence the device before closing. */
    (void)reg_write(ctx, REG_OUTPUT_ENABLE, 0xFFU);
    (void)close(ctx->fd);
    (void)memset(ctx, 0, sizeof(*ctx));
    free(ctx);
}
