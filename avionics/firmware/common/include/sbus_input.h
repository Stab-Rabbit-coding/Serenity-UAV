/**
 * @file    sbus_input.h
 * @brief   SBUS RC protocol decoder — public API.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * This module implements a background receive thread that reads and decodes
 * Futaba S.BUS frames from a UART device.  It is used by both serenity-fc
 * (Cape-A UART2 SBUS input) and serenity-cn (Cape-B UART5 in SBUS mode).
 *
 * ── SBUS Protocol Overview ────────────────────────────────────────────────
 *
 * S.BUS is a proprietary serial RC protocol developed by Futaba.  The
 * physical layer uses an inverted UART signal:
 *
 *   Baud rate : 100000 bps (100 kbaud)
 *   Data bits : 8
 *   Parity    : Even (PARENB, no PARODD)
 *   Stop bits : 2 (CSTOPB)
 *   Logic     : Inverted — idle = low, start bit = high
 *               (On Cape-A / Cape-B, the 74LVC1G14 Schmitt-trigger inverter
 *               re-inverts the signal to standard idle-high UART logic.)
 *
 * Frame structure (25 bytes total):
 *   Byte  0   : Start byte (0x0F)
 *   Bytes 1-22: Channel data — 16 channels × 11 bits packed LSB-first
 *   Byte 23   : Flags byte
 *                 Bit 0 (SBUS_CH17_MASK)      : Digital channel 17
 *                 Bit 1 (SBUS_CH18_MASK)      : Digital channel 18
 *                 Bit 2 (SBUS_FRAME_LOST_MASK): Frame lost (link dropout)
 *                 Bit 3 (SBUS_FAILSAFE_MASK)  : Receiver failsafe active
 *   Byte 24   : End byte (0x00)
 *
 * Channel values are 11-bit unsigned integers in the range 0–2047.
 * Futaba standard mapping:
 *   172  → 988 µs (minimum pulse width)
 *   992  → 1500 µs (centre / neutral)
 *   1811 → 2012 µs (maximum pulse width)
 *
 * Inter-frame gap: 14 ms nominal (standard Futaba SBUS at 72 Hz frame rate).
 * Frame duration:  25 bytes × 10 bits/byte ÷ 100000 baud = 2.5 ms.
 *
 * ── Hardware Signal Path ──────────────────────────────────────────────────
 *
 * Cape-A SBUS path (UART2):
 *   RC receiver → J_SBUS (JST-GH 3P) → 100 Ω R_SBUS
 *   → U_SBUS (74LVC1G14 Schmitt inverter) → UART2_RXD
 *
 * Cape-B SBUS path (UART5, SW1-2 position):
 *   J_XCVR JST-GH 6P → PRTR5V0U2X TVS (Zoë) → 74LVC1G14 U_SBUS_B
 *   → 100 Ω R_SBUS_RX → UART5_RX
 *
 * ── Baud Rate Configuration ───────────────────────────────────────────────
 *
 * 100000 baud is not available as a named POSIX B-constant.  The driver
 * uses struct termios2 and TCSETS2 ioctl with BOTHER to set an arbitrary
 * baud rate.  This requires _GNU_SOURCE and <asm/termbits.h>.  Available
 * since Linux 3.7.
 *
 * ── Thread Safety ─────────────────────────────────────────────────────────
 *
 * sbus_open() starts a background receive thread.  The rx_callback is
 * invoked from this thread.  The callback MUST NOT call sbus_open() or
 * sbus_close() (deadlock risk).  Use a lock-free queue or pipe to pass
 * decoded frames to the main application thread.
 *
 * References:
 *   [1] Futaba S.BUS protocol specification (as documented by community
 *       reverse engineering; no official Futaba public specification exists).
 *       Reference implementation: ArduPilot AP_SBusReceiver.cpp (MIT).
 *   [2] Linux termios2 / BOTHER documentation — linux/termios.h comments.
 *
 * Target platform: PocketBeagle 2 Industrial (AM6254), Debian Trixie.
 */

#ifndef SBUS_INPUT_H
#define SBUS_INPUT_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ---------------------------------------------------------------------------
 * Protocol constants
 * ---------------------------------------------------------------------------*/

/** UART baud rate for SBUS (not a standard POSIX B-constant; use BOTHER). */
#define SBUS_UART_BAUD       (100000U)

/** Total number of bytes in one SBUS frame (start + data + flags + end). */
#define SBUS_FRAME_LEN       (25U)

/** SBUS frame start byte — first byte of every valid frame. */
#define SBUS_START_BYTE      (0x0FU)

/** SBUS frame end byte — last byte of every valid frame. */
#define SBUS_END_BYTE        (0x00U)

/** Number of proportional RC channels encoded in each SBUS frame. */
#define SBUS_NUM_CHANNELS    (16U)

/**
 * Minimum 11-bit channel value (corresponds to ≈ 988 µs pulse width).
 * Futaba standard; may vary slightly by transmitter calibration.
 */
#define SBUS_CHANNEL_MIN     (172U)

/**
 * Centre / neutral 11-bit channel value (corresponds to ≈ 1500 µs).
 * Used as the default failsafe value for non-critical channels.
 */
#define SBUS_CHANNEL_MID     (992U)

/**
 * Maximum 11-bit channel value (corresponds to ≈ 2012 µs pulse width).
 * Futaba standard; may vary slightly by transmitter calibration.
 */
#define SBUS_CHANNEL_MAX     (1811U)

/** Flags byte (byte 23) bitmask: digital channel 17 state. */
#define SBUS_CH17_MASK       (0x01U)

/** Flags byte (byte 23) bitmask: digital channel 18 state. */
#define SBUS_CH18_MASK       (0x02U)

/**
 * Flags byte (byte 23) bitmask: frame-lost flag.
 * Set by the receiver when one or more consecutive frames were not received
 * from the transmitter.  Does NOT imply failsafe (see SBUS_FAILSAFE_MASK).
 */
#define SBUS_FRAME_LOST_MASK (0x04U)

/**
 * Flags byte (byte 23) bitmask: receiver failsafe active.
 * Set when the receiver has not received valid signal for its configured
 * failsafe timeout and has applied failsafe channel positions.
 */
#define SBUS_FAILSAFE_MASK   (0x08U)

/* ---------------------------------------------------------------------------
 * Data types
 * ---------------------------------------------------------------------------*/

/**
 * @brief Decoded SBUS frame.
 *
 * Populated by the internal frame decoder and passed to the rx_callback.
 */
typedef struct {
    /**
     * Proportional channel values (channels 1–16, zero-indexed 0–15).
     * Each value is an 11-bit unsigned integer in the range 0–2047.
     * Futaba standard: 172 = min, 992 = centre, 1811 = max.
     */
    uint16_t channels[SBUS_NUM_CHANNELS];

    /** Digital channel 17 state (true = active/high). */
    bool ch17;

    /** Digital channel 18 state (true = active/high). */
    bool ch18;

    /**
     * Frame-lost flag (true = receiver did not receive this frame from TX).
     * The channel values in this frame are the last valid values received.
     */
    bool frame_lost;

    /**
     * Failsafe active flag (true = receiver failsafe has engaged).
     * Channel values reflect the failsafe positions programmed into the
     * receiver, not the current transmitter stick positions.
     */
    bool failsafe;
} sbus_frame_t;

/**
 * @brief RX callback type.
 *
 * Called from the background receive thread each time a complete, valid
 * SBUS frame is decoded.  The @c frame pointer is valid only for the
 * duration of this call; copy the data if needed beyond the call.
 *
 * @param[in] frame    Pointer to the decoded SBUS frame (do NOT free).
 * @param[in] userdata Opaque pointer from sbus_config_t.rx_userdata.
 */
typedef void (*sbus_rx_callback_t)(const sbus_frame_t *frame, void *userdata);

/**
 * @brief Driver initialisation parameters.
 *
 * All pointer fields must remain valid for the lifetime of the driver context.
 */
typedef struct {
    /**
     * Path to the UART device, e.g. "/dev/ttyS2" (Cape-A) or "/dev/ttyS5"
     * (Cape-B).  Must not be NULL.
     */
    const char *uart_dev;

    /**
     * Callback invoked for each decoded SBUS frame.  Must not be NULL.
     * The callback is called from the internal RX thread.
     */
    sbus_rx_callback_t rx_callback;

    /**
     * Opaque pointer forwarded unchanged to rx_callback.  May be NULL.
     */
    void *rx_userdata;
} sbus_config_t;

/**
 * @brief Opaque driver context.
 *
 * Initialise with sbus_open(); release with sbus_close().
 * Do not access the internal fields directly.
 */
typedef struct sbus_ctx sbus_ctx_t;

/* ---------------------------------------------------------------------------
 * API
 * ---------------------------------------------------------------------------*/

/**
 * @brief Open the SBUS decoder and start the receive thread.
 *
 * Opens the UART specified by config->uart_dev, configures it for 100000
 * baud 8E2 using struct termios2 / BOTHER (required because B100000 is not
 * a POSIX-defined baud rate constant), and starts a background thread that
 * reads bytes from the UART and decodes SBUS frames.
 *
 * On each successfully decoded frame, config->rx_callback is invoked with
 * the decoded sbus_frame_t and config->rx_userdata.
 *
 * @param[in]  config   Initialisation parameters (must remain valid).
 * @param[out] ctx_out  Set to the allocated driver context on success.
 * @return 0 on success, negative errno on error:
 *         -EINVAL : config or ctx_out is NULL, or required fields are NULL.
 *         -ENOMEM : memory allocation failed.
 *         -errno  : UART open or configuration failed (see errno).
 */
int sbus_open(const sbus_config_t *config, sbus_ctx_t **ctx_out);

/**
 * @brief Stop the receive thread and release all resources.
 *
 * Signals the receive thread to exit, waits for it to terminate, closes
 * the UART file descriptor, and frees the context.  Safe to call with a
 * NULL pointer (no-op).
 *
 * @param[in] ctx  Driver context returned by sbus_open().  May be NULL.
 */
void sbus_close(sbus_ctx_t *ctx);

/**
 * @brief Convert an 11-bit SBUS channel value to pulse width in microseconds.
 *
 * Maps the 11-bit SBUS channel range (172–1811) linearly to standard RC
 * servo pulse widths (988–2012 µs).  Uses integer arithmetic only (no
 * floating-point).
 *
 * Values outside the normal range (< 172 or > 1811) are clamped to the
 * corresponding limit (988 µs or 2012 µs) to protect downstream servo
 * and ESC drivers from out-of-range commands.
 *
 * Mapping formula (integer):
 *   us = 988 + ((channel - 172) * (2012 - 988)) / (1811 - 172)
 *      = 988 + ((channel - 172) * 1024) / 1639
 *
 * Accuracy: ±1 µs error over the full range (verified by exhaustive
 * integer evaluation across all 11-bit input values).
 *
 * @param[in] channel  11-bit SBUS channel value (0–2047; normally 172–1811).
 * @return Pulse width in microseconds (normally 988–2012).
 */
int sbus_channel_to_us(uint16_t channel);

#ifdef __cplusplus
}
#endif

#endif /* SBUS_INPUT_H */
