/**
 * @file    link.c
 * @brief   Bearer-agnostic XRCE link layer with redundant-bus failover.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Binds each bearer to eProsima's custom-transport interface
 * (`uxr_set_custom_transport_callbacks`, Apache-2.0, [REF-SW-001]).  Nothing
 * in the eProsima tree is modified; this file only implements the four
 * callbacks upstream declares.
 *
 * The CAN-FD length-prefix framing implemented here is the format the
 * Micro XRCE-DDS Agent's CAN transport uses on the wire, determined by
 * reading the Agent's published transport source for interoperability
 * [REF-SW-002].  No Agent or Client code is reproduced.
 *
 * See `link.h` for the bearer table and the design rationale.
 */

#include "serenity/link.h"

#include <uxr/client/profile/transport/custom/custom_transport.h>

#include <string.h>

/** @brief Default silence before failing over to the standby bearer. */
#define LINK_DEFAULT_FAILOVER_MS    (2000U)

/**
 * @brief Per-bearer transport instances.
 *
 * File-scope because upstream's callbacks receive a `uxrCustomTransport *`
 * and carry a single `void *args`, and because a node has exactly one link
 * pair.  Index matches `ser_link_t.cfg`.
 */
static uxrCustomTransport g_transport[2];
static ser_link_t *g_link;

/**
 * @brief Round a CAN-FD data-field length up to a legal value.
 *
 * ISO 11898-1:2015 [REF-ISO-001] permits data fields of 0–8, 12, 16, 20, 24,
 * 32, 48 and 64 bytes only.  Padding is invisible to the peer because the
 * true length travels in `data[0]`.
 */
static uint8_t canfd_dlen(uint8_t len) {
    static const uint8_t steps[] = {12U, 16U, 20U, 24U, 32U, 48U, 64U};
    if (len <= 8U) {
        return len;
    }
    for (size_t i = 0U; i < (sizeof(steps) / sizeof(steps[0])); ++i) {
        if (len <= steps[i]) {
            return steps[i];
        }
    }
    return 64U;
}

/** @brief Recover the bearer index from a transport instance. */
static uint8_t index_of(const uxrCustomTransport *t) {
    return (t == &g_transport[1]) ? 1U : 0U;
}

/* ---------------------------------------------------------------------------
 * Custom transport callbacks
 * ---------------------------------------------------------------------------*/

static bool link_open_cb(uxrCustomTransport *t) {
    const uint8_t i = index_of(t);
    const ser_link_cfg_t *cfg = &g_link->cfg[i];

    if (cfg->kind == SER_LINK_CANFD) {
        return ser_hal_can_init(cfg->nominal_bps, cfg->data_bps,
                                cfg->can_id) == SER_OK;
    }
    return ser_hal_uart_init(cfg->uart, cfg->baud) == SER_OK;
}

static bool link_close_cb(uxrCustomTransport *t) {
    (void)t;
    return true;
}

static size_t link_write_cb(uxrCustomTransport *t,
                            const uint8_t *buf,
                            size_t len,
                            uint8_t *errcode) {
    const uint8_t i = index_of(t);
    const ser_link_cfg_t *cfg = &g_link->cfg[i];
    ser_link_stats_t *st = &g_link->stats[i];

    if (len > SER_LINK_MTU) {
        /* Upstream never asks for more than the MTU it was configured with;
         * if it does, the build is inconsistent and truncating would corrupt
         * the XRCE stream. */
        *errcode = 1U;
        st->tx_fail++;
        return 0U;
    }

    int rc;
    if (cfg->kind == SER_LINK_CANFD) {
        ser_can_frame_t frame;
        memset(&frame, 0, sizeof(frame));
        frame.id = cfg->can_id;
        frame.data[0] = (uint8_t)len;
        if (len > 0U) {
            memcpy(&frame.data[1], buf, len);
        }
        frame.len = canfd_dlen((uint8_t)(len + 1U));
        rc = ser_hal_can_send(&frame);
    } else {
        /* Stream bearers carry upstream's framing protocol, which has already
         * delimited the message; write the bytes as given. */
        rc = ser_hal_uart_write(cfg->uart, buf, len);
    }

    if (rc != SER_OK) {
        /*
         * Reporting zero written is the correct signal: upstream compares the
         * return against the requested length and treats a mismatch as a
         * failed send, which the reliable stream then retries.  Silently
         * dropping would lose an XRCE submessage.
         */
        *errcode = 1U;
        st->tx_fail++;
        return 0U;
    }

    st->tx_ok++;
    *errcode = 0U;
    return len;
}

static size_t link_read_cb(uxrCustomTransport *t,
                           uint8_t *buf,
                           size_t len,
                           int timeout,
                           uint8_t *errcode) {
    const uint8_t i = index_of(t);
    const ser_link_cfg_t *cfg = &g_link->cfg[i];
    ser_link_stats_t *st = &g_link->stats[i];

    *errcode = 0U;

    if (cfg->kind == SER_LINK_CANFD) {
        ser_can_frame_t frame;
        const int rc = ser_hal_can_recv(&frame, timeout);
        if (rc == SER_ETIMEDOUT) {
            return 0U;      /* Idle is normal, not an error. */
        }
        if (rc != SER_OK) {
            *errcode = 1U;
            return 0U;
        }

        /*
         * `data[0]` is the sender's declared length.  It must fit inside the
         * frame that arrived and inside the caller's buffer.  A frame failing
         * either check is dropped whole rather than delivered partially —
         * feeding a truncated submessage to the XRCE parser desynchronises
         * the stream.
         */
        const uint8_t declared = frame.data[0];
        if ((frame.len < 1U) ||
            ((size_t)declared > (size_t)(frame.len - 1U)) ||
            ((size_t)declared > len)) {
            st->rx_malformed++;
            *errcode = 1U;
            return 0U;
        }
        if (declared > 0U) {
            memcpy(buf, &frame.data[1], declared);
        }
        st->rx_ok++;
        st->last_rx_ms = ser_hal_time_ms();
        return (size_t)declared;
    }

    size_t got = 0U;
    const int rc = ser_hal_uart_read(cfg->uart, buf, len, &got, timeout);
    if (rc != SER_OK) {
        *errcode = 1U;
        return 0U;
    }
    if (got > 0U) {
        st->rx_ok++;
        st->last_rx_ms = ser_hal_time_ms();
    }
    return got;
}

/* ---------------------------------------------------------------------------
 * Public interface
 * ---------------------------------------------------------------------------*/

int ser_link_open(ser_link_t *link) {
    if ((link == NULL) || (link->count == 0U) || (link->count > 2U)) {
        return SER_EINVAL;
    }

    g_link = link;
    link->active = 0U;
    link->failovers = 0U;
    if (link->failover_ms == 0U) {
        link->failover_ms = LINK_DEFAULT_FAILOVER_MS;
    }
    memset(link->stats, 0, sizeof(link->stats));

    for (uint8_t i = 0U; i < link->count; ++i) {
        /*
         * Framing is on for stream bearers and off for CAN-FD: a CAN frame is
         * already a delimited message, so running the framing protocol over
         * it would spend bytes re-delimiting what the bearer delimits.
         */
        const bool framing = (link->cfg[i].kind == SER_LINK_STREAM);
        uxr_set_custom_transport_callbacks(&g_transport[i], framing,
                                           link_open_cb, link_close_cb,
                                           link_write_cb, link_read_cb);
        if (!uxr_init_custom_transport(&g_transport[i], NULL)) {
            ser_hal_log("link: bearer %u failed to open\n", (unsigned)i);
            if (i == 0U) {
                /* Primary down: fall straight to the standby rather than
                 * failing the node — a single failed bearer is exactly the
                 * case the redundant pair exists for. */
                continue;
            }
        } else if (!link->open) {
            link->active = i;
            link->open = true;
        }
    }

    if (!link->open) {
        return SER_ENODEV;
    }

    ser_hal_log("link: up on bearer %u (%s)\n",
                (unsigned)link->active,
                (link->cfg[link->active].kind == SER_LINK_CANFD)
                    ? "CAN-FD" : "stream");
    return SER_OK;
}

int ser_link_close(ser_link_t *link) {
    if (link == NULL) {
        return SER_EINVAL;
    }
    for (uint8_t i = 0U; i < link->count; ++i) {
        (void)uxr_close_custom_transport(&g_transport[i]);
    }
    link->open = false;
    return SER_OK;
}

bool ser_link_maintain(ser_link_t *link, uint64_t now_ms) {
    if ((link == NULL) || !link->open || (link->count < 2U)) {
        return false;
    }

    const ser_link_stats_t *st = &link->stats[link->active];

    /*
     * A bearer that has never received anything is treated as silent from
     * link-open time, so a bearer that is up electrically but has no Agent on
     * it still triggers failover instead of stalling the node forever.
     */
    const uint64_t last = (st->last_rx_ms != 0U) ? st->last_rx_ms : 0U;
    if ((now_ms - last) < (uint64_t)link->failover_ms) {
        return false;
    }

    link->active = (uint8_t)((link->active + 1U) % link->count);
    link->failovers++;
    link->stats[link->active].last_rx_ms = now_ms;   /* Grant a fresh window. */

    ser_hal_log("link: failover -> bearer %u (%lu total)\n",
                (unsigned)link->active, (unsigned long)link->failovers);
    return true;
}

void *ser_link_comm(ser_link_t *link) {
    if ((link == NULL) || !link->open) {
        return NULL;
    }
    return &g_transport[link->active].comm;
}

void ser_link_get_stats(const ser_link_t *link, ser_link_stats_t *out) {
    if ((link == NULL) || (out == NULL)) {
        return;
    }
    *out = link->stats[link->active];
}
