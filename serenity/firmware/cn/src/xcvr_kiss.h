/**
 * @file    xcvr_kiss.h
 * @brief   XCVR-49MHZ-1 KISS/AX.25 UART driver — public API.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * This driver manages the UART link between the CN node (AM6254) and the
 * XCVR-49MHZ-1 physical-layer modem board.  It provides:
 *
 *   1. KISS frame encode / decode (RFC 1055 / Chepponis & Karn 1987).
 *   2. PTT_N GPIO sequencing: assert PTT_N (active-low), wait ≥ 5 ms to let
 *      the PA stabilise, then write the KISS frame to the UART.
 *   3. Si5351A channel select before each transmission.
 *   4. Background receive thread: decodes inbound KISS frames and delivers
 *      the AX.25 payload to the caller via a registered callback.
 *
 * Interface wiring (Cape-B J1):
 *   Pin 1  +5 V supply (200 mA max)
 *   Pin 2  GND
 *   Pin 3  UART_TX  (CN node → XCVR) — 57600 baud 8N1 3.3 V LVTTL
 *   Pin 4  UART_RX  (XCVR → CN node)
 *   Pin 5  PTT_N    (CN node GPIO, active-low, assert ≥ 5 ms before TX)
 *   Pin 6  RSSI_ANA (0–3.3 V, read-only, not used by this driver)
 *
 * Thread safety:
 *   xcvr_kiss_transmit() may be called from any thread.  Concurrent TX calls
 *   are serialised by an internal mutex.  The receive callback is invoked from
 *   the driver's internal RX thread and MUST NOT call xcvr_kiss_transmit()
 *   (deadlock risk).  Use a queue to decouple RX and TX if needed.
 *
 * References:
 *   [1] Chepponis & Karn, "KISS TNC," ARRL 6th Computer Networking Conf., 1987.
 *   [2] AX.25 v2.2, TAPR / ARRL, 1998.
 *   [3] libgpiod 2.2.1 API documentation — libgpiod.readthedocs.io
 *
 * Target platform: PocketBeagle 2 Industrial (AM6254), Debian Trixie.
 * Requires libgpiod ≥ 2.x (Debian Trixie: libgpiod 2.2.1-2+deb13u1).
 * Not compatible with libgpiod 1.x — the 2.x API is a complete redesign.
 */

#ifndef XCVR_KISS_H
#define XCVR_KISS_H

#include "kiss_types.h"
#include "ax25_types.h"
#include "si5351.h"

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ---------------------------------------------------------------------------
 * Configuration constants
 * ---------------------------------------------------------------------------*/

/** UART baud rate to/from XCVR-49MHZ-1 (Cape-B J1 pins 3/4). */
#define XCVR_UART_BAUD          (57600U)

/**
 * Minimum PTT_N assert-to-transmit delay in microseconds.
 * Per project requirements: ≥ 5 ms key-up before first TX bit.
 * This value adds a 2 ms margin above the 5 ms requirement.
 */
#define XCVR_PTT_ASSERT_DELAY_US (7000U)

/**
 * Air-interface bit rate for the Bell 202 AFSK modem (bps).
 * Used to calculate the PTT hold time after the last byte is sent.
 */
#define XCVR_RF_BAUD            (1200U)

/**
 * Extra PTT hold time after the last expected RF bit (microseconds).
 * Provides margin for UART FIFO latency and TX tail timing.
 */
#define XCVR_PTT_TAIL_US        (50000U)

/* ---------------------------------------------------------------------------
 * Callback type
 * ---------------------------------------------------------------------------*/

/**
 * @brief Called by the RX thread when a complete, valid KISS data frame is
 *        received from the XCVR board.
 *
 * @param[in] frame    Decoded KISS frame (do NOT free — owned by the driver).
 * @param[in] userdata Pointer passed to xcvr_kiss_open().
 */
typedef void (*xcvr_rx_callback_t)(const kiss_frame_t *frame, void *userdata);

/* ---------------------------------------------------------------------------
 * Driver handle
 * ---------------------------------------------------------------------------*/

/**
 * @brief Opaque driver context.
 *
 * Initialise with xcvr_kiss_open(); release with xcvr_kiss_close().
 */
typedef struct xcvr_kiss_ctx xcvr_kiss_ctx_t;

/* ---------------------------------------------------------------------------
 * Configuration structure
 * ---------------------------------------------------------------------------*/

/**
 * @brief Driver initialisation parameters.
 *
 * All string fields must remain valid for the lifetime of the driver context.
 */
typedef struct {
    /** UART device path, e.g. "/dev/ttyS2". */
    const char     *uart_dev;

    /** libgpiod chip path for PTT_N GPIO, e.g. "/dev/gpiochip0". */
    const char     *gpio_chip;

    /** GPIO line offset for PTT_N on the chip specified by @c gpio_chip. */
    unsigned int    ptt_gpio_line;

    /** I²C bus number for Si5351A, e.g. 1 for /dev/i2c-1. */
    int             si5351_i2c_bus;

    /** Default RCRS channel (0–4) at startup. */
    unsigned int    default_channel;

    /** RX callback — invoked for every received AX.25 frame. */
    xcvr_rx_callback_t rx_callback;

    /** Opaque pointer forwarded to @c rx_callback unchanged. */
    void           *rx_userdata;
} xcvr_kiss_config_t;

/* ---------------------------------------------------------------------------
 * API
 * ---------------------------------------------------------------------------*/

/**
 * @brief Open the XCVR-49MHZ-1 driver.
 *
 * Opens and configures the UART, initialises the Si5351A DDS to
 * @c config->default_channel, claims the PTT_N GPIO line as an output
 * (inactive, i.e. high), and starts the background RX thread.
 *
 * @param[in]  config   Driver configuration (pointer must remain valid).
 * @param[out] ctx_out  Set to the driver context on success.
 * @return 0 on success, negative errno on error.
 */
int xcvr_kiss_open(const xcvr_kiss_config_t *config,
                   xcvr_kiss_ctx_t          **ctx_out);

/**
 * @brief Transmit an AX.25 frame over the 49 MHz RCRS link.
 *
 * Sequence:
 *   1. Select @c channel on the Si5351A DDS.
 *   2. Assert PTT_N (GPIO low).
 *   3. Sleep XCVR_PTT_ASSERT_DELAY_US µs (≥ 5 ms, per project requirement).
 *   4. KISS-encode @c ax25_payload and write to the UART.
 *   5. Sleep until the modem has finished transmitting the frame over the air
 *      (frame_bytes × 8 / 1200 baud + XCVR_PTT_TAIL_US margin).
 *   6. Release PTT_N (GPIO high).
 *
 * This call blocks until step 6 completes.  Concurrent calls are serialised
 * by an internal mutex; they will block but will not fail.
 *
 * @param[in] ctx          Driver context.
 * @param[in] channel      RCRS channel index 0–4.
 * @param[in] ax25_payload Raw AX.25 frame bytes (no HDLC flags / FCS).
 * @param[in] payload_len  Length of @c ax25_payload in bytes (≤ KISS_MAX_AX25_LEN).
 * @return 0 on success, negative errno on error.
 */
int xcvr_kiss_transmit(xcvr_kiss_ctx_t *ctx,
                       unsigned int     channel,
                       const uint8_t   *ax25_payload,
                       size_t           payload_len);

/**
 * @brief Query the currently selected RCRS channel.
 *
 * @param[in] ctx  Driver context.
 * @return Channel index 0–4, or UINT_MAX if not yet set.
 */
unsigned int xcvr_kiss_get_channel(const xcvr_kiss_ctx_t *ctx);

/**
 * @brief Close the driver and release all resources.
 *
 * Stops the RX thread, releases PTT_N GPIO, closes the UART, silences the
 * Si5351A, and frees the context.  Safe to call with a NULL pointer.
 *
 * @param[in] ctx  Driver context (may be NULL).
 */
void xcvr_kiss_close(xcvr_kiss_ctx_t *ctx);

/* ---------------------------------------------------------------------------
 * KISS framing utilities (used internally; exposed for unit testing)
 * ---------------------------------------------------------------------------*/

/**
 * @brief Encode an AX.25 payload into a KISS data frame.
 *
 * Wraps @c payload with FEND delimiters and applies FESC escaping.
 * Output is written to @c out_buf.
 *
 * @param[in]  payload      AX.25 frame bytes.
 * @param[in]  payload_len  Byte count of @c payload.
 * @param[out] out_buf      Output buffer, must be ≥ (payload_len × 2 + 4) bytes.
 * @param[in]  out_buf_len  Size of @c out_buf.
 * @param[out] out_len      Number of bytes written to @c out_buf.
 * @return 0 on success, -ENOSPC if @c out_buf is too small, -EINVAL on bad args.
 */
int kiss_encode(const uint8_t *payload,  size_t payload_len,
                uint8_t       *out_buf,  size_t out_buf_len,
                size_t        *out_len);

/**
 * @brief Feed one byte into the KISS decoder state machine.
 *
 * Call this function for every byte received from the XCVR UART.  When a
 * complete frame is available, @c frame_out is populated and the function
 * returns 1.  Returns 0 while the frame is still being received, or a
 * negative errno for a protocol error (decoder is reset on error).
 *
 * @param[in,out] frame_out  Output frame (must be pre-allocated by caller).
 * @param[in]     byte       Next byte from the UART.
 * @param[in,out] state      Decoder state (caller allocates and zero-initialises
 *                           before the first call; do NOT modify externally).
 * @return 1 if frame complete, 0 if frame in progress, negative errno on error.
 */

/** Opaque decoder state — zero-initialise before first call. */
typedef struct {
    bool    in_frame;    /**< True once the opening FEND has been seen. */
    bool    escaped;     /**< True if the previous byte was FESC. */
    size_t  idx;         /**< Write index into @c frame_out.data. */
} kiss_decoder_state_t;

int kiss_decode_byte(kiss_frame_t         *frame_out,
                     kiss_decoder_state_t *state,
                     uint8_t               byte);

#ifdef __cplusplus
}
#endif

#endif /* XCVR_KISS_H */
