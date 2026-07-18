/**
 * @file    sbus_input.c
 * @brief   SBUS RC protocol decoder — implementation.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * See sbus_input.h for design overview, protocol description, and
 * hardware signal-path documentation.
 *
 * Implementation notes:
 *   - UART is configured with struct termios2 / BOTHER ioctl because
 *     100000 baud is not available as a named POSIX B-constant.  The
 *     <asm/termbits.h> header is included instead of <termios.h> to
 *     avoid redefinition conflicts between the two.
 *   - Raw mode flags are set explicitly (no cfmakeraw(), which requires
 *     the conflicting <termios.h>).
 *   - Frame sync uses a simple byte-scan: look for SBUS_START_BYTE (0x0F),
 *     collect 24 additional bytes, validate end byte (0x00), then decode.
 *     False starts are discarded and re-sync is immediate.
 *   - The RX thread blocks on read() with a 100 ms VTIME timeout, allowing
 *     clean shutdown when rx_running is cleared.
 *   - All error paths release resources in reverse acquisition order.
 *
 * References:
 *   [1] Futaba S.BUS protocol (community reverse-engineered documentation;
 *       ArduPilot AP_SBusReceiver.cpp, MIT licence, used as reference only).
 *   [2] Linux kernel termios2 / BOTHER — include/uapi/asm-generic/termbits.h.
 *   [3] POSIX.1-2017 threads specification (pthread_create, pthread_join).
 */

/*
 * _GNU_SOURCE enables nanosleep(), pthread extensions, and other
 * POSIX/GNU features used in this file.
 * IMPORTANT: <asm/termbits.h> is included instead of <termios.h> for
 * struct termios2 / BOTHER support.  Do NOT add a <termios.h> include to
 * this file — it will cause redefinition errors for termios structures.
 */
#define _GNU_SOURCE

#include "sbus_input.h"

/* System headers — <asm/termbits.h> replaces <termios.h> in this file. */
#include <asm/termbits.h>
#include <errno.h>
#include <fcntl.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

/* ---------------------------------------------------------------------------
 * Internal context (opaque to callers — exposed only via sbus_ctx_t *)
 * ---------------------------------------------------------------------------*/

struct sbus_ctx {
    int                uart_fd;     /**< UART file descriptor */
    pthread_t          rx_thread;   /**< Background receive thread */
    volatile bool      rx_running;  /**< Set false to request thread exit */
    sbus_rx_callback_t rx_callback; /**< Frame-ready callback */
    void              *rx_userdata; /**< Opaque pointer forwarded to callback */
};

/* ---------------------------------------------------------------------------
 * Internal: UART configuration
 *
 * Configures the UART for 100000 baud, 8 data bits, even parity, 2 stop
 * bits (8E2).  Uses struct termios2 / TCSETS2 ioctl because B100000 is not
 * defined in POSIX termios.  All input/output/local processing is disabled
 * (equivalent to cfmakeraw plus the SBUS-specific parity and stop-bit flags).
 * ---------------------------------------------------------------------------*/

/**
 * @brief Open and configure a UART for SBUS reception (100000 baud 8E2).
 *
 * @param[in] dev  Path to the UART device, e.g. "/dev/ttyS2".
 * @return Open file descriptor, or -errno on failure.
 */
static int uart_open_sbus(const char *dev) {
    int fd = open(dev, O_RDWR | O_NOCTTY | O_NDELAY);
    if (fd < 0) {
        return -errno;
    }

    /* Switch from O_NDELAY to blocking I/O so VTIME works correctly. */
    if (fcntl(fd, F_SETFL, 0) < 0) {
        int err = -errno;
        (void)close(fd);
        return err;
    }

    /*
     * Fetch the current termios2 state as a baseline, then overwrite all
     * relevant flags.  Using TCGETS2 + TCSETS2 (rather than the standard
     * TCGETS + TCSETS) enables the BOTHER custom-baud extension.
     */
    struct termios2 tio;
    (void)memset(&tio, 0, sizeof(tio));
    if (ioctl(fd, TCGETS2, &tio) != 0) {
        int err = -errno;
        (void)close(fd);
        return err;
    }

    /*
     * Raw-mode flags (equivalent to cfmakeraw):
     *   c_iflag: disable all input transformations (parity strip, NL/CR
     *            mapping, XON/XOFF, break detection).
     *   c_oflag: disable output post-processing.
     *   c_lflag: disable canonical mode, echo, signal generation, and
     *            extended input processing.
     */
    tio.c_iflag &= ~(tcflag_t)(IGNBRK | BRKINT | PARMRK | ISTRIP | INLCR |
                               IGNCR | ICRNL | IXON);
    tio.c_oflag &= ~(tcflag_t)OPOST;
    tio.c_lflag &= ~(tcflag_t)(ECHO | ECHONL | ICANON | ISIG | IEXTEN);

    /*
     * SBUS framing: 8 data bits, even parity, 2 stop bits, custom baud.
     *   CS8    — 8 data bits per frame.
     *   PARENB — enable parity generation/checking.
     *   PARODD cleared — even parity (not odd).
     *   CSTOPB — 2 stop bits.
     *   CLOCAL — ignore modem control lines.
     *   CREAD  — enable receiver.
     *   BOTHER — use c_ispeed / c_ospeed for custom baud rate.
     */
    tio.c_cflag = CS8 | PARENB | CSTOPB | CLOCAL | CREAD | BOTHER;
    tio.c_cflag &= ~(tcflag_t)PARODD; /* even parity */

    /* Custom baud rate: 100000 bps. */
    tio.c_ispeed = (speed_t)SBUS_UART_BAUD;
    tio.c_ospeed = (speed_t)SBUS_UART_BAUD;

    /*
     * Read timeout: VMIN=0, VTIME=1 (100 ms).
     * read() returns after at most 100 ms, even if no bytes arrive.
     * This allows the RX thread to poll rx_running at 10 Hz and exit
     * promptly when sbus_close() is called.
     */
    tio.c_cc[VMIN] = 0;
    tio.c_cc[VTIME] = 1; /* 100 ms (VTIME units = 100 ms tenths) */

    if (ioctl(fd, TCSETS2, &tio) != 0) {
        int err = -errno;
        (void)close(fd);
        return err;
    }

    return fd;
}

/* ---------------------------------------------------------------------------
 * Internal: SBUS frame decoder
 *
 * Unpacks the 16 × 11-bit channel values and flags from a raw 25-byte
 * SBUS frame buffer.  The bit layout is LSB-first, packed continuously
 * across byte boundaries.
 * ---------------------------------------------------------------------------*/

/**
 * @brief Decode a raw 25-byte SBUS buffer into an sbus_frame_t.
 *
 * @param[in]  buf        Raw 25-byte SBUS frame (buf[0] must be 0x0F,
 *                        buf[24] must be 0x00).
 * @param[out] frame_out  Destination for the decoded frame.
 * @return 0 on success, -EBADMSG if start/end bytes are invalid.
 */
static int sbus_decode_frame(const uint8_t buf[SBUS_FRAME_LEN],
                             sbus_frame_t *frame_out) {
    /* Validate frame delimiters. */
    if (buf[0] != SBUS_START_BYTE || buf[24] != SBUS_END_BYTE) {
        return -EBADMSG;
    }

    /*
     * Unpack 16 channels × 11 bits from bytes 1-22.
     * Each channel value is packed LSB-first across consecutive bytes.
     * The unpacking pattern below is the standard SBUS bit layout as
     * documented in ArduPilot AP_SBusReceiver.cpp and numerous community
     * references.  All casts to uint16_t are required to prevent implicit
     * sign extension on left shifts of uint8_t values.
     */
    frame_out->channels[0] =
        ((uint16_t)buf[1] | ((uint16_t)buf[2] << 8U)) & 0x07FFU;
    frame_out->channels[1] =
        (((uint16_t)buf[2] >> 3U) | ((uint16_t)buf[3] << 5U)) & 0x07FFU;
    frame_out->channels[2] =
        (((uint16_t)buf[3] >> 6U) | ((uint16_t)buf[4] << 2U) |
         ((uint16_t)buf[5] << 10U)) &
        0x07FFU;
    frame_out->channels[3] =
        (((uint16_t)buf[5] >> 1U) | ((uint16_t)buf[6] << 7U)) & 0x07FFU;
    frame_out->channels[4] =
        (((uint16_t)buf[6] >> 4U) | ((uint16_t)buf[7] << 4U)) & 0x07FFU;
    frame_out->channels[5] =
        (((uint16_t)buf[7] >> 7U) | ((uint16_t)buf[8] << 1U) |
         ((uint16_t)buf[9] << 9U)) &
        0x07FFU;
    frame_out->channels[6] =
        (((uint16_t)buf[9] >> 2U) | ((uint16_t)buf[10] << 6U)) & 0x07FFU;
    frame_out->channels[7] =
        (((uint16_t)buf[10] >> 5U) | ((uint16_t)buf[11] << 3U)) & 0x07FFU;
    frame_out->channels[8] =
        ((uint16_t)buf[12] | ((uint16_t)buf[13] << 8U)) & 0x07FFU;
    frame_out->channels[9] =
        (((uint16_t)buf[13] >> 3U) | ((uint16_t)buf[14] << 5U)) & 0x07FFU;
    frame_out->channels[10] =
        (((uint16_t)buf[14] >> 6U) | ((uint16_t)buf[15] << 2U) |
         ((uint16_t)buf[16] << 10U)) &
        0x07FFU;
    frame_out->channels[11] =
        (((uint16_t)buf[16] >> 1U) | ((uint16_t)buf[17] << 7U)) & 0x07FFU;
    frame_out->channels[12] =
        (((uint16_t)buf[17] >> 4U) | ((uint16_t)buf[18] << 4U)) & 0x07FFU;
    frame_out->channels[13] =
        (((uint16_t)buf[18] >> 7U) | ((uint16_t)buf[19] << 1U) |
         ((uint16_t)buf[20] << 9U)) &
        0x07FFU;
    frame_out->channels[14] =
        (((uint16_t)buf[20] >> 2U) | ((uint16_t)buf[21] << 6U)) & 0x07FFU;
    frame_out->channels[15] =
        (((uint16_t)buf[21] >> 5U) | ((uint16_t)buf[22] << 3U)) & 0x07FFU;

    /* Byte 23: flags and digital channels. */
    frame_out->ch17 = (buf[23] & SBUS_CH17_MASK) != 0U;
    frame_out->ch18 = (buf[23] & SBUS_CH18_MASK) != 0U;
    frame_out->frame_lost = (buf[23] & SBUS_FRAME_LOST_MASK) != 0U;
    frame_out->failsafe = (buf[23] & SBUS_FAILSAFE_MASK) != 0U;

    return 0;
}

/* ---------------------------------------------------------------------------
 * Background RX thread
 *
 * Reads bytes from the UART, scans for SBUS_START_BYTE (0x0F), accumulates
 * a 25-byte frame, validates the end byte, decodes, and invokes the callback.
 *
 * Framing strategy:
 *   1. Discard bytes until SBUS_START_BYTE is found.
 *   2. Attempt to read 24 more bytes (total frame = 25 bytes).
 *   3. If the 25th byte is SBUS_END_BYTE (0x00), decode and callback.
 *   4. If validation fails, discard the candidate start byte and rescan
 *      from byte 1 of the buffer (no seeking — simple linear scan).
 * ---------------------------------------------------------------------------*/

/**
 * @brief SBUS receive thread entry point.
 *
 * @param[in] arg  Pointer to the sbus_ctx_t for this UART.
 * @return NULL (thread return value unused).
 */
static void *rx_thread_func(void *arg) {
    sbus_ctx_t  *ctx = (sbus_ctx_t *)arg;
    sbus_frame_t frame;
    uint8_t      buf[SBUS_FRAME_LEN];
    size_t       buf_idx = 0U;   /* index into accumulation buffer */
    bool         synced = false; /* true once start byte received */

    (void)memset(&frame, 0, sizeof(frame));
    (void)memset(buf, 0, sizeof(buf));

    while (ctx->rx_running) {
        uint8_t byte;
        ssize_t n = read(ctx->uart_fd, &byte, 1U);

        if (n < 0) {
            if (errno == EINTR || errno == EAGAIN) {
                continue; /* signal or transient error — retry */
            }
            (void)fprintf(stderr, "sbus_input: RX UART read error: %s\n",
                          strerror(errno));
            break;
        }

        if (n == 0) {
            /* Timeout (VTIME expired) — no data; loop to check rx_running. */
            continue;
        }

        if (!synced) {
            /* Scanning for start byte. */
            if (byte != SBUS_START_BYTE) {
                continue; /* discard non-start bytes */
            }
            /* Found potential start byte — begin frame accumulation. */
            buf[0] = byte;
            buf_idx = 1U;
            synced = true;
            continue;
        }

        /* Accumulating frame bytes after the start byte. */
        buf[buf_idx++] = byte;

        if (buf_idx < SBUS_FRAME_LEN) {
            continue; /* frame not yet complete */
        }

        /* Full 25-byte candidate frame accumulated — validate and decode. */
        buf_idx = 0U;
        synced = false; /* require re-sync for next frame */

        int rc = sbus_decode_frame(buf, &frame);
        if (rc == 0) {
            /* Valid frame — invoke caller's callback. */
            if (ctx->rx_callback != NULL) {
                ctx->rx_callback(&frame, ctx->rx_userdata);
            }
        } else {
            /* Invalid frame (bad end byte or start byte mismatch).
             * Log at debug level only to avoid flooding stderr at 72 Hz. */
            (void)fprintf(stderr,
                          "sbus_input: invalid frame (start=0x%02X end=0x%02X)"
                          " — resyncing\n",
                          buf[0], buf[24]);
        }
    }

    return NULL;
}

/* ---------------------------------------------------------------------------
 * Public API
 * ---------------------------------------------------------------------------*/

int sbus_open(const sbus_config_t *config, sbus_ctx_t **ctx_out) {
    if (config == NULL || ctx_out == NULL) {
        return -EINVAL;
    }
    if (config->uart_dev == NULL || config->rx_callback == NULL) {
        return -EINVAL;
    }

    sbus_ctx_t *ctx = (sbus_ctx_t *)calloc(1U, sizeof(*ctx));
    if (ctx == NULL) {
        return -ENOMEM;
    }

    /* Open and configure the UART. */
    ctx->uart_fd = uart_open_sbus(config->uart_dev);
    if (ctx->uart_fd < 0) {
        int rc = ctx->uart_fd;
        free(ctx);
        return rc;
    }

    ctx->rx_callback = config->rx_callback;
    ctx->rx_userdata = config->rx_userdata;
    ctx->rx_running = true;

    /* Start the background receive thread. */
    if (pthread_create(&ctx->rx_thread, NULL, rx_thread_func, ctx) != 0) {
        int rc = -errno;
        (void)close(ctx->uart_fd);
        free(ctx);
        return rc;
    }

    *ctx_out = ctx;
    return 0;
}

void sbus_close(sbus_ctx_t *ctx) {
    if (ctx == NULL) {
        return;
    }

    /* Signal the RX thread to stop and wait for it to exit. */
    ctx->rx_running = false;
    (void)pthread_join(ctx->rx_thread, NULL);

    (void)close(ctx->uart_fd);
    (void)memset(ctx, 0, sizeof(*ctx));
    free(ctx);
}

int sbus_channel_to_us(uint16_t channel) {
    /* Clamp to valid SBUS range before conversion. */
    uint16_t clamped;
    if (channel < SBUS_CHANNEL_MIN) {
        clamped = SBUS_CHANNEL_MIN;
    } else if (channel > SBUS_CHANNEL_MAX) {
        clamped = SBUS_CHANNEL_MAX;
    } else {
        clamped = channel;
    }

    /*
     * Linear map: [172, 1811] → [988, 2012] µs
     *
     * us = 988 + (clamped - 172) * (2012 - 988) / (1811 - 172)
     *    = 988 + (clamped - 172) * 1024 / 1639
     *
     * Integer arithmetic: multiply before divide to preserve precision.
     * Maximum intermediate value: (1811 - 172) * 1024 = 1,678,336 — fits
     * comfortably in int32_t.
     */
    return 988 + (int)((int32_t)(clamped - SBUS_CHANNEL_MIN) * 1024 / 1639);
}
