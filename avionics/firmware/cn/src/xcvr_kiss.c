/**
 * @file    xcvr_kiss.c
 * @brief   XCVR-49MHZ-1 KISS/AX.25 UART driver — implementation.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * See xcvr_kiss.h for design overview and interface description.
 *
 * Implementation notes:
 *   - UART is opened in raw mode (no line discipline processing) via termios.
 *   - PTT_N GPIO is managed through the Linux GPIO character device (libgpiod).
 *     libgpiod is preferred over sysfs gpio for correctness and safety on
 *     kernels ≥ 4.8 (sysfs gpio is deprecated).
 *   - The RX thread blocks on read(); no busy-wait or polling.
 *   - TX is serialised by a mutex; the PTT window is held for the minimum
 *     required duration and no longer, to respect Part 95 channel access rules.
 *   - All error paths close resources in reverse acquisition order to avoid
 *     resource leaks.
 *
 * References:
 *   [1] POSIX.1-2017 termios specification.
 *   [2] libgpiod 2.2.1 API — libgpiod.readthedocs.io/en/latest
 *       Target: Debian Trixie (libgpiod 2.2.1-2+deb13u1) on PocketBeagle 2 Industrial.
 *   [3] Chepponis & Karn, "KISS TNC," ARRL 6th Computer Networking Conf., 1987.
 */

/*
 * _GNU_SOURCE enables cfmakeraw(), nanosleep(), and other POSIX/GNU extensions
 * used throughout this file.  Must precede all system header includes.
 */
#define _GNU_SOURCE

#include "xcvr_kiss.h"

#include <errno.h>
#include <fcntl.h>
#include <gpiod.h>
#include <limits.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <termios.h>
#include <time.h>
#include <unistd.h>

/* ---------------------------------------------------------------------------
 * Internal context
 * ---------------------------------------------------------------------------*/

struct xcvr_kiss_ctx {
    int                        uart_fd;         /**< UART file descriptor */
    si5351_ctx_t              *si5351;          /**< DDS driver context */
    struct gpiod_chip         *gpio_chip;       /**< libgpiod 2.x chip handle */
    struct gpiod_line_request *ptt_req;         /**< libgpiod 2.x line request */
    unsigned int               ptt_offset;      /**< GPIO line offset for PTT_N */
    pthread_t                  rx_thread;       /**< Background receive thread */
    pthread_mutex_t            tx_mutex;        /**< Serialises transmit calls */
    volatile bool              rx_running;      /**< Set false to stop rx_thread */
    unsigned int               current_channel; /**< Currently selected RCRS channel */
    xcvr_rx_callback_t         rx_callback;     /**< RX frame callback */
    void                      *rx_userdata;     /**< Caller context for rx_callback */
};

/* ---------------------------------------------------------------------------
 * Internal: UART setup
 * ---------------------------------------------------------------------------*/

/**
 * @brief Open and configure the UART in raw 8N1 mode at XCVR_UART_BAUD.
 *
 * @return Open file descriptor, or -errno on failure.
 */
static int uart_open(const char *dev)
{
    int fd = open(dev, O_RDWR | O_NOCTTY | O_NDELAY);
    if (fd < 0) {
        return -errno;
    }

    /* Switch to blocking I/O. */
    if (fcntl(fd, F_SETFL, 0) < 0) {
        int err = -errno;
        (void)close(fd);
        return err;
    }

    struct termios tty;
    if (tcgetattr(fd, &tty) != 0) {
        int err = -errno;
        (void)close(fd);
        return err;
    }

    /* Raw mode: no canonical processing, no echo, no signals. */
    cfmakeraw(&tty);

    /* 57600 baud, 8N1. */
    (void)cfsetispeed(&tty, B57600);
    (void)cfsetospeed(&tty, B57600);
    tty.c_cflag  = (tty.c_cflag & ~(tcflag_t)CSIZE) | CS8;
    tty.c_cflag &= ~(tcflag_t)(PARENB | CSTOPB);
    tty.c_cflag |= (tcflag_t)CLOCAL | (tcflag_t)CREAD;

    /* Blocking read with 100 ms timeout (VTIME in tenths of a second). */
    tty.c_cc[VMIN]  = 0;
    tty.c_cc[VTIME] = 1;

    if (tcsetattr(fd, TCSANOW, &tty) != 0) {
        int err = -errno;
        (void)close(fd);
        return err;
    }

    return fd;
}

/* ---------------------------------------------------------------------------
 * Internal: PTT GPIO (libgpiod 2.x API)
 *
 * PTT_N is active-low.  In libgpiod 2.x semantics for a non-inverted output:
 *   GPIOD_LINE_VALUE_INACTIVE (0) → line electrically LOW  → PTT asserted
 *   GPIOD_LINE_VALUE_ACTIVE   (1) → line electrically HIGH → PTT released
 * ---------------------------------------------------------------------------*/

/**
 * @brief Assert PTT_N (drive line LOW — active-low, TX keyed).
 */
static int ptt_assert(xcvr_kiss_ctx_t *ctx)
{
    int rc = gpiod_line_request_set_value(ctx->ptt_req,
                                          ctx->ptt_offset,
                                          GPIOD_LINE_VALUE_INACTIVE);
    return (rc == 0) ? 0 : -EIO;
}

/**
 * @brief Release PTT_N (drive line HIGH — TX unkeyed).
 */
static int ptt_release(xcvr_kiss_ctx_t *ctx)
{
    int rc = gpiod_line_request_set_value(ctx->ptt_req,
                                          ctx->ptt_offset,
                                          GPIOD_LINE_VALUE_ACTIVE);
    return (rc == 0) ? 0 : -EIO;
}

/* ---------------------------------------------------------------------------
 * Internal: microsecond sleep (POSIX)
 * ---------------------------------------------------------------------------*/

static void sleep_us(unsigned long us)
{
    struct timespec ts = {
        .tv_sec  = (time_t)(us / 1000000UL),
        .tv_nsec = (long)((us % 1000000UL) * 1000UL)
    };
    /* Retry on signal interruption. */
    while (nanosleep(&ts, &ts) != 0 && errno == EINTR) { /* retry */ }
}

/* ---------------------------------------------------------------------------
 * KISS frame encoder
 * ---------------------------------------------------------------------------*/

int kiss_encode(const uint8_t *payload,  size_t payload_len,
                uint8_t       *out_buf,  size_t out_buf_len,
                size_t        *out_len)
{
    if (payload == NULL || out_buf == NULL || out_len == NULL) {
        return -EINVAL;
    }

    /* Worst case: every byte is FEND/FESC (doubled) + 2 FEND + 1 type byte. */
    size_t worst = payload_len * 2U + 4U;
    if (out_buf_len < worst) {
        return -ENOSPC;
    }

    size_t i = 0U;

    /* Opening frame delimiter. */
    out_buf[i++] = KISS_FEND;

    /* Type byte: data frame, port 0. */
    out_buf[i++] = KISS_CMD_DATA;

    /* Escape-encode payload. */
    for (size_t j = 0U; j < payload_len; j++) {
        uint8_t b = payload[j];
        if (b == KISS_FEND) {
            out_buf[i++] = KISS_FESC;
            out_buf[i++] = KISS_TFEND;
        } else if (b == KISS_FESC) {
            out_buf[i++] = KISS_FESC;
            out_buf[i++] = KISS_TFESC;
        } else {
            out_buf[i++] = b;
        }
    }

    /* Closing frame delimiter. */
    out_buf[i++] = KISS_FEND;

    *out_len = i;
    return 0;
}

/* ---------------------------------------------------------------------------
 * KISS frame decoder (byte-at-a-time state machine)
 * ---------------------------------------------------------------------------*/

int kiss_decode_byte(kiss_frame_t         *frame_out,
                     kiss_decoder_state_t *state,
                     uint8_t               byte)
{
    if (frame_out == NULL || state == NULL) {
        return -EINVAL;
    }

    if (byte == KISS_FEND) {
        if (!state->in_frame) {
            /* Opening FEND — start a new frame. */
            state->in_frame = true;
            state->escaped  = false;
            state->idx      = 0U;
            frame_out->data_len = 0U;
            return 0;
        }

        /* Closing FEND — frame complete (idx > 0 means we got the type byte). */
        if (state->idx > 0U) {
            frame_out->data_len = state->idx - 1U; /* exclude type byte slot */
            state->in_frame = false;
            return 1; /* frame ready */
        }

        /* Empty frame (two consecutive FENDs) — discard and restart. */
        state->in_frame = false;
        return 0;
    }

    if (!state->in_frame) {
        /* Data outside a frame — discard. */
        return 0;
    }

    if (byte == KISS_FESC) {
        /* Next byte is an escaped character. */
        state->escaped = true;
        return 0;
    }

    if (state->escaped) {
        state->escaped = false;
        if (byte == KISS_TFEND) {
            byte = KISS_FEND;
        } else if (byte == KISS_TFESC) {
            byte = KISS_FESC;
        } else {
            /* Invalid escape sequence — discard frame and reset. */
            state->in_frame = false;
            return -EBADMSG;
        }
    }

    /* First byte after opening FEND is the type indicator. */
    if (state->idx == 0U) {
        frame_out->port = (byte >> 4U) & 0x0FU;
        frame_out->type = byte & 0x0FU;
        state->idx++;
        return 0;
    }

    /* Subsequent bytes are payload. */
    size_t data_idx = state->idx - 1U; /* offset into data[] */
    if (data_idx >= KISS_MAX_AX25_LEN) {
        /* Frame too large — discard. */
        state->in_frame = false;
        return -EMSGSIZE;
    }

    frame_out->data[data_idx] = byte;
    state->idx++;
    return 0;
}

/* ---------------------------------------------------------------------------
 * Background RX thread
 * ---------------------------------------------------------------------------*/

static void *rx_thread_func(void *arg)
{
    xcvr_kiss_ctx_t      *ctx   = (xcvr_kiss_ctx_t *)arg;
    kiss_frame_t          frame;
    kiss_decoder_state_t  state;

    (void)memset(&frame, 0, sizeof(frame));
    (void)memset(&state, 0, sizeof(state));

    while (ctx->rx_running) {
        uint8_t  byte;
        ssize_t  n = read(ctx->uart_fd, &byte, 1U);

        if (n < 0) {
            if (errno == EINTR || errno == EAGAIN) {
                continue; /* signal or timeout — retry */
            }
            /* Unrecoverable UART error — log and exit thread. */
            (void)fprintf(stderr,
                          "xcvr_kiss: RX UART read error: %s\n",
                          strerror(errno));
            break;
        }

        if (n == 0) {
            /* Timeout (VTIME expired) — no data, loop. */
            continue;
        }

        int rc = kiss_decode_byte(&frame, &state, byte);
        if (rc == 1) {
            /* Complete frame received — deliver to caller. */
            if (frame.type == KISS_CMD_DATA && ctx->rx_callback != NULL) {
                ctx->rx_callback(&frame, ctx->rx_userdata);
            }
            /* Reset state for next frame. */
            (void)memset(&state, 0, sizeof(state));
        } else if (rc < 0) {
            /* Protocol error — reset and continue. */
            (void)fprintf(stderr,
                          "xcvr_kiss: RX decode error %d, resetting\n", rc);
            (void)memset(&state, 0, sizeof(state));
        }
    }

    return NULL;
}

/* ---------------------------------------------------------------------------
 * Public API — open / close
 * ---------------------------------------------------------------------------*/

int xcvr_kiss_open(const xcvr_kiss_config_t *config,
                   xcvr_kiss_ctx_t          **ctx_out)
{
    if (config == NULL || ctx_out == NULL) {
        return -EINVAL;
    }
    if (config->uart_dev == NULL || config->gpio_chip == NULL) {
        return -EINVAL;
    }
    if (config->default_channel >= SI5351_RCRS_NUM_CHANNELS) {
        return -EINVAL;
    }

    xcvr_kiss_ctx_t *ctx = (xcvr_kiss_ctx_t *)calloc(1U, sizeof(*ctx));
    if (ctx == NULL) {
        return -ENOMEM;
    }

    int rc;

    /* --- UART --- */
    ctx->uart_fd = uart_open(config->uart_dev);
    if (ctx->uart_fd < 0) {
        rc = ctx->uart_fd;
        goto err_free_ctx;
    }

    /* --- Si5351A DDS --- */
    rc = si5351_open(config->si5351_i2c_bus, SI5351_I2C_ADDR, &ctx->si5351);
    if (rc != 0) {
        goto err_close_uart;
    }

    rc = si5351_set_rcrs_channel(ctx->si5351, config->default_channel);
    if (rc != 0) {
        goto err_close_si5351;
    }
    ctx->current_channel = config->default_channel;

    /* --- PTT_N GPIO (libgpiod 2.x) --- */
    ctx->gpio_chip = gpiod_chip_open(config->gpio_chip);
    if (ctx->gpio_chip == NULL) {
        rc = -errno;
        goto err_close_si5351;
    }
    ctx->ptt_offset = config->ptt_gpio_line;

    /*
     * Build the libgpiod 2.x request in three steps:
     *   1. line_settings  — direction and initial output value
     *   2. line_config    — bind settings to the specific GPIO offset
     *   3. request_config — set the consumer name for /dev/gpiochipN label
     * Then call gpiod_chip_request_lines() to claim the line.
     *
     * Initial value: GPIOD_LINE_VALUE_ACTIVE (line HIGH = PTT released).
     */
    struct gpiod_line_settings *ls = gpiod_line_settings_new();
    if (ls == NULL) {
        rc = -ENOMEM;
        goto err_close_gpio_chip;
    }
    (void)gpiod_line_settings_set_direction(ls, GPIOD_LINE_DIRECTION_OUTPUT);
    (void)gpiod_line_settings_set_output_value(ls, GPIOD_LINE_VALUE_ACTIVE);

    struct gpiod_line_config *lc = gpiod_line_config_new();
    if (lc == NULL) {
        rc = -ENOMEM;
        gpiod_line_settings_free(ls);
        goto err_close_gpio_chip;
    }
    rc = gpiod_line_config_add_line_settings(lc, &ctx->ptt_offset, 1U, ls);
    gpiod_line_settings_free(ls);
    if (rc != 0) {
        rc = -EIO;
        gpiod_line_config_free(lc);
        goto err_close_gpio_chip;
    }

    struct gpiod_request_config *rc_cfg = gpiod_request_config_new();
    if (rc_cfg == NULL) {
        rc = -ENOMEM;
        gpiod_line_config_free(lc);
        goto err_close_gpio_chip;
    }
    gpiod_request_config_set_consumer(rc_cfg, "serenity-cn-xcvr-ptt");

    ctx->ptt_req = gpiod_chip_request_lines(ctx->gpio_chip, rc_cfg, lc);
    gpiod_request_config_free(rc_cfg);
    gpiod_line_config_free(lc);
    if (ctx->ptt_req == NULL) {
        rc = -errno;
        goto err_close_gpio_chip;
    }

    /* --- TX mutex --- */
    if (pthread_mutex_init(&ctx->tx_mutex, NULL) != 0) {
        rc = -errno;
        gpiod_line_request_release(ctx->ptt_req);
        goto err_close_gpio_chip;
    }

    /* --- RX thread --- */
    ctx->rx_callback = config->rx_callback;
    ctx->rx_userdata = config->rx_userdata;
    ctx->rx_running  = true;

    if (pthread_create(&ctx->rx_thread, NULL, rx_thread_func, ctx) != 0) {
        rc = -errno;
        goto err_destroy_mutex;
    }

    *ctx_out = ctx;
    return 0;

    /* Error unwind in reverse acquisition order. */
err_destroy_mutex:
    (void)pthread_mutex_destroy(&ctx->tx_mutex);
err_close_gpio_chip:
    gpiod_chip_close(ctx->gpio_chip);
err_close_si5351:
    si5351_close(ctx->si5351);
err_close_uart:
    (void)close(ctx->uart_fd);
err_free_ctx:
    free(ctx);
    return rc;
}

void xcvr_kiss_close(xcvr_kiss_ctx_t *ctx)
{
    if (ctx == NULL) { return; }

    /* Signal and join the RX thread. */
    ctx->rx_running = false;
    (void)pthread_join(ctx->rx_thread, NULL);

    /* Release PTT (safety: ensure line is high). */
    (void)ptt_release(ctx);

    (void)pthread_mutex_destroy(&ctx->tx_mutex);
    gpiod_line_request_release(ctx->ptt_req);
    gpiod_chip_close(ctx->gpio_chip);
    si5351_close(ctx->si5351);
    (void)close(ctx->uart_fd);
    (void)memset(ctx, 0, sizeof(*ctx));
    free(ctx);
}

/* ---------------------------------------------------------------------------
 * Public API — transmit
 * ---------------------------------------------------------------------------*/

int xcvr_kiss_transmit(xcvr_kiss_ctx_t *ctx,
                       unsigned int     channel,
                       const uint8_t   *ax25_payload,
                       size_t           payload_len)
{
    if (ctx == NULL || ax25_payload == NULL) {
        return -EINVAL;
    }
    if (channel >= SI5351_RCRS_NUM_CHANNELS) {
        return -EINVAL;
    }
    if (payload_len == 0U || payload_len > KISS_MAX_AX25_LEN) {
        return -EINVAL;
    }

    /* Worst-case KISS frame buffer size: (payload × 2) + 4 bytes overhead. */
    uint8_t kiss_buf[KISS_MAX_AX25_LEN * 2U + 4U];
    size_t  kiss_len = 0U;

    int rc = kiss_encode(ax25_payload, payload_len,
                         kiss_buf, sizeof(kiss_buf), &kiss_len);
    if (rc != 0) {
        return rc;
    }

    (void)pthread_mutex_lock(&ctx->tx_mutex);

    /* 1. Select RCRS channel on the Si5351A DDS. */
    if (channel != ctx->current_channel) {
        rc = si5351_set_rcrs_channel(ctx->si5351, channel);
        if (rc != 0) {
            goto tx_done;
        }
        ctx->current_channel = channel;
    }

    /* 2. Assert PTT_N (active-low — drives GPIO low). */
    rc = ptt_assert(ctx);
    if (rc != 0) {
        goto tx_done;
    }

    /* 3. Wait ≥ 5 ms (XCVR_PTT_ASSERT_DELAY_US = 7 ms) for PA to stabilise.
     *    This satisfies the project requirement of ≥ 5 ms key-up before TX.  */
    sleep_us(XCVR_PTT_ASSERT_DELAY_US);

    /* 4. Write KISS frame to UART. */
    size_t written = 0U;
    while (written < kiss_len) {
        ssize_t n = write(ctx->uart_fd,
                          &kiss_buf[written],
                          kiss_len - written);
        if (n < 0) {
            if (errno == EINTR) { continue; }
            rc = -errno;
            (void)ptt_release(ctx);
            goto tx_done;
        }
        written += (size_t)n;
    }

    /*
     * 5. Wait for the modem to finish transmitting the frame over the air.
     *
     * The Bell 202 modem encodes each byte as 8 bits at 1200 baud.  AX.25
     * HDLC framing adds an opening flag (8 bits), CRC-16 (16 bits), closing
     * flag (8 bits), plus bit-stuffing overhead (~20%).
     *
     * Conservative estimate: (payload_len + 10) bytes at 1200 baud.
     * air_time_us = (payload_len + 10) * 8 * 1_000_000 / 1200
     *
     * We add XCVR_PTT_TAIL_US = 50 ms margin for UART FIFO latency and
     * modem TX tail.
     *
     * Future enhancement: if XCVR Rev 2 adds a TX_DONE GPIO, eliminate this
     * calculated delay and wait on the hardware signal instead.
     */
    unsigned long air_bits = (unsigned long)(payload_len + 10U) * 8UL;
    unsigned long air_us   = (air_bits * 1000000UL) / (unsigned long)XCVR_RF_BAUD;
    sleep_us(air_us + XCVR_PTT_TAIL_US);

    /* 6. Release PTT_N. */
    rc = ptt_release(ctx);

tx_done:
    (void)pthread_mutex_unlock(&ctx->tx_mutex);
    return rc;
}

unsigned int xcvr_kiss_get_channel(const xcvr_kiss_ctx_t *ctx)
{
    return (ctx != NULL) ? ctx->current_channel : UINT_MAX;
}
