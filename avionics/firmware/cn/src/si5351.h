/**
 * @file    si5351.h
 * @brief   Si5351A DDS frequency synthesiser driver — public API.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * The Si5351A (Skyworks / Silicon Labs) is an I²C-programmable clock
 * synthesiser used as the carrier-frequency DDS on the XCVR-49MHZ-1 board.
 * It is connected to the CN node (AM6254) via the Cape-B I²C bus (J1 pin).
 *
 * This driver programs CLK0 to one of the five FCC Part 95 Subpart D (RCRS)
 * channels:
 *
 *   Channel 0 — 49.830 MHz
 *   Channel 1 — 49.845 MHz
 *   Channel 2 — 49.860 MHz
 *   Channel 3 — 49.875 MHz
 *   Channel 4 — 49.890 MHz
 *
 * The PLLA VCO is set to (channel_freq × 14) ≈ 698 MHz (within the 600–900 MHz
 * operating range) and CLK0 uses an integer output divider of 14.  All five
 * PLL configurations are precomputed and stored in a lookup table.
 *
 * Reference:
 *   Silicon Labs AN619 — Manually Calculating Si5351 Registers, Rev 0.3.
 *   Si5351A/B/C-B Datasheet, Skyworks, Rev 1.4.
 */

#ifndef SI5351_H
#define SI5351_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ---------------------------------------------------------------------------
 * I²C device parameters
 * ---------------------------------------------------------------------------*/

/** Default I²C 7-bit address of the Si5351A (ADDR pin tied low). */
#define SI5351_I2C_ADDR  ((uint8_t)0x60U)

/* ---------------------------------------------------------------------------
 * RCRS channel definitions (47 CFR 95.623)
 * ---------------------------------------------------------------------------*/

/** Number of legal 49 MHz RCRS channels. */
#define SI5351_RCRS_NUM_CHANNELS  (5U)

/** RCRS channel 0 — 49.830 MHz. */
#define SI5351_RCRS_CH0_HZ  (49830000UL)

/** RCRS channel 1 — 49.845 MHz. */
#define SI5351_RCRS_CH1_HZ  (49845000UL)

/** RCRS channel 2 — 49.860 MHz. */
#define SI5351_RCRS_CH2_HZ  (49860000UL)

/** RCRS channel 3 — 49.875 MHz. */
#define SI5351_RCRS_CH3_HZ  (49875000UL)

/** RCRS channel 4 — 49.890 MHz. */
#define SI5351_RCRS_CH4_HZ  (49890000UL)

/* ---------------------------------------------------------------------------
 * Driver handle
 * ---------------------------------------------------------------------------*/

/**
 * @brief Opaque driver context.
 *
 * Initialise with si5351_open(); release with si5351_close().
 */
typedef struct si5351_ctx si5351_ctx_t;

/* ---------------------------------------------------------------------------
 * API
 * ---------------------------------------------------------------------------*/

/**
 * @brief Open the Si5351A on the specified I²C bus.
 *
 * Opens /dev/i2c-<bus_num>, verifies the device responds at @c i2c_addr, and
 * performs the initial startup sequence (disable all outputs, clear status
 * sticky bits, release PLL reset).
 *
 * @param[in]  bus_num   Linux I²C bus number (e.g. 1 for /dev/i2c-1).
 * @param[in]  i2c_addr  7-bit I²C address (typically SI5351_I2C_ADDR = 0x60).
 * @param[out] ctx_out   Set to an allocated driver context on success.
 *                       The caller must free it with si5351_close().
 * @return 0 on success, negative errno on error.
 */
int si5351_open(int bus_num, uint8_t i2c_addr, si5351_ctx_t **ctx_out);

/**
 * @brief Program CLK0 to the specified RCRS channel and enable the output.
 *
 * Sets PLLA to (channel_freq_hz × 14) and CLK0 output divider to 14 (integer
 * mode).  Resets the PLLA to guarantee phase alignment after the PLL
 * frequency changes.
 *
 * @param[in] ctx          Driver context from si5351_open().
 * @param[in] channel      RCRS channel index 0–4 (maps to 49.830–49.890 MHz).
 * @return 0 on success, -EINVAL if channel ≥ SI5351_RCRS_NUM_CHANNELS,
 *         negative errno on I²C error.
 */
int si5351_set_rcrs_channel(si5351_ctx_t *ctx, unsigned int channel);

/**
 * @brief Disable CLK0 output (mute the carrier).
 *
 * Powers down the CLK0 output driver.  Call si5351_set_rcrs_channel() again
 * to re-enable.
 *
 * @param[in] ctx  Driver context.
 * @return 0 on success, negative errno on I²C error.
 */
int si5351_disable_clk0(si5351_ctx_t *ctx);

/**
 * @brief Read the current CLK0 frequency in Hz (from the driver's state,
 *        not from the hardware).
 *
 * Returns 0 if CLK0 has not been programmed yet.
 *
 * @param[in] ctx  Driver context.
 * @return Programmed frequency in Hz, or 0.
 */
uint32_t si5351_get_clk0_freq_hz(const si5351_ctx_t *ctx);

/**
 * @brief Close the driver and release all resources.
 *
 * Disables all Si5351A clock outputs before releasing the I²C file descriptor
 * and freeing the context.
 *
 * @param[in] ctx  Driver context (may be NULL — this is a no-op in that case).
 */
void si5351_close(si5351_ctx_t *ctx);

#ifdef __cplusplus
}
#endif

#endif /* SI5351_H */
