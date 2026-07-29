/**
 * @file    app.c
 * @brief   MAL-CAN-PERIPH-GW-PCB — application: sample locally, publish signed.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * The device drivers this calls (AK7455, DSHOT/BDSHOT, servo PWM) are
 * separate WBS items; this file is the publication skeleton and the safe-state
 * behaviour, which is what the node lifecycle depends on.  Each unimplemented
 * driver is marked and reports a fault rather than publishing a fabricated
 * value — a node that invents plausible telemetry is more dangerous than one
 * that admits it has none.
 */

#include "serenity/board.h"
#include "serenity/hal.h"
#include "serenity/node.h"

#include <string.h>

/** @brief The node this application runs on; set by `board_app_init()`. */
extern ser_node_t *ser_node_current(void);

/* Publication schedule. */
static uint64_t g_next_sample_ms;
static uint64_t g_next_health_ms;

/** @brief Latched safe state; set by `board_app_safe_state()`. */
static bool g_safe;

/* --- Payload serialisation ------------------------------------------------
 * Payloads are packed big-endian by hand rather than by struct layout, so the
 * MSPM0 and the PocketBeagle agree byte-for-byte without depending on
 * compiler padding.
 * --------------------------------------------------------------------------*/

static void put_be16(uint8_t *p, uint16_t v) {
    p[0] = (uint8_t)(v >> 8);
    p[1] = (uint8_t)v;
}

static void put_be32(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)(v >> 24);
    p[1] = (uint8_t)(v >> 16);
    p[2] = (uint8_t)(v >> 8);
    p[3] = (uint8_t)v;
}

int board_app_init(void) {
    g_safe = false;
    g_next_sample_ms = 0U;
    g_next_health_ms = 0U;

    /* Bring the ISOW1044 out of standby: STB low is normal mode
     * [REF-SENSOR-009]. */
    (void)ser_hal_gpio_write(SER_GPIO_CAN_STB_N, false);

    /* RS-485 receiver enabled, driver disabled until there is traffic to
     * send — leaving DE asserted would hold the standby bus busy. */
    (void)ser_hal_gpio_write(SER_GPIO_RS485_RE_N, false);
    (void)ser_hal_gpio_write(SER_GPIO_RS485_DE, false);

#if GW_ROLE == GW_ROLE_ENCODER
    /* TODO(WBS §4.7.3): AK7455 SPI driver on SER_SPI_SENSOR.
     * Datasheet: avionics/datasheets/ak7455-en-datasheet-myakm.pdf,
     * REF-SENSOR-008.  Until it exists this role cannot publish a real
     * angle, so `board_app_step()` faults rather than emitting zero. */
#elif GW_ROLE == GW_ROLE_ESC
    /* TODO(WBS §4.7.4): DSHOT command output and BDSHOT telemetry capture on
     * FLEX_BSHOT_IO, per CAN-PERIPH-GW-1.md deployment mode 2. */
#else
    /* TODO(WBS §4.7.5): servo PWM generation on FLEX_PWM_IO, with the
     * −5°/140° travel limits enforced in firmware (avionics/firmware/WBS.md
     * §4.2 "Nacelle tilt servo PWM generation"). */
#endif

    return SER_OK;
}

/**
 * @brief Publish this node's health.
 *
 * Health is the one topic that works with no device driver at all, so it is
 * also the node's liveness proof: a peer that sees health but no sensor data
 * knows the node is alive and its sensor path is not.
 */
static int publish_health(ser_node_t *node, uint64_t now_ms) {
    ser_link_stats_t st;
    ser_can_status_t can;

    ser_link_get_stats(&node->link, &st);
    if (ser_hal_can_status(&can) != SER_OK) {
        memset(&can, 0, sizeof(can));
    }

    /* node_state, active_bearer, failovers, tx_ok, rx_ok, rx_malformed,
     * publish_errors, can_tec, can_rec, can_flags, uptime_ms */
    uint8_t p[26];
    p[0] = (uint8_t)node->state;
    p[1] = node->link.active;
    put_be32(&p[2], node->link.failovers);
    put_be32(&p[6], st.tx_ok);
    put_be32(&p[10], st.rx_ok);
    put_be32(&p[14], st.rx_malformed);
    put_be16(&p[18], (uint16_t)node->publish_errors);
    p[20] = (uint8_t)can.tx_error_count;
    p[21] = (uint8_t)can.rx_error_count;
    p[22] = (uint8_t)((can.bus_off ? 0x01U : 0U)
                      | (can.error_passive ? 0x02U : 0U));
    p[23] = 0U;
    put_be16(&p[24], (uint16_t)((now_ms - node->joined_at_ms) / 1000U));

    return ser_node_publish(node, TOPIC_ID_NODE_HEALTH, p, sizeof(p),
                            g_safe ? SER_ENV_FLAG_DEGRADED
                                   : SER_ENV_FLAG_NONE);
}

int board_app_step(uint64_t now_ms) {
    ser_node_t *node = ser_node_current();
    if (node == NULL) {
        return SER_EINVAL;
    }

    if (now_ms >= g_next_health_ms) {
        g_next_health_ms = now_ms + PERIOD_HEALTH_MS;
        (void)publish_health(node, now_ms);
    }

    if (g_safe) {
        /* In the safe state the node keeps publishing health so the fault is
         * visible to the domain, but publishes no sensor or command data. */
        return SER_OK;
    }

#if GW_ROLE == GW_ROLE_ENCODER
    if (now_ms >= g_next_sample_ms) {
        g_next_sample_ms = now_ms + PERIOD_TILT_MS;
        /* TODO(WBS §4.7.3): read the AK7455 and publish the angle.  Returning
         * SER_ENOTSUP here faults the node deliberately: an encoder gateway
         * that cannot read its encoder must not look healthy. */
        return SER_ENOTSUP;
    }
#elif GW_ROLE == GW_ROLE_ESC
    if (now_ms >= g_next_sample_ms) {
        g_next_sample_ms = now_ms + PERIOD_ESC_STATUS_MS;
        /* TODO(WBS §4.7.4): decode BDSHOT telemetry and publish it. */
        return SER_ENOTSUP;
    }
#endif

    return SER_OK;
}

void board_app_safe_state(void) {
    g_safe = true;

#if GW_ROLE == GW_ROLE_ESC
    /* TODO(WBS §4.7.4): command zero throttle before anything else. */
#elif GW_ROLE == GW_ROLE_SERVO
    /* TODO(WBS §4.7.5): release servo drive; do not hold a stale setpoint. */
#endif

    /* Drop the RS-485 driver so a faulted node cannot jam the standby bus. */
    (void)ser_hal_gpio_write(SER_GPIO_RS485_DE, false);
    (void)ser_hal_gpio_write(SER_GPIO_STATUS_LED, true);
}
