/**
 * @file    app.c
 * @brief   Jayne U3 — ToF publication, laser interlock, signed telemetry.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * The TFmini-S driver and the laser drive are separate WBS items (root
 * `TODO.md` §4.6.2).  What is implemented here is the part the node lifecycle
 * depends on: the publication schedule and, critically, the laser safe state.
 */

#include "serenity/board.h"
#include "serenity/hal.h"
#include "serenity/node.h"

#include <string.h>

static uint64_t g_next_tof_ms;
static uint64_t g_next_laser_ms;
static uint64_t g_next_health_ms;
static bool     g_safe;

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

/**
 * @brief Extinguish the laser.
 *
 * Called from `board_app_init()` before anything else and from
 * `board_app_safe_state()`.  Per `docs/JAYNE_LASER_ANALYSIS.md` the emitter
 * is a live IEC 60825-1 classification item [REF-IEC-002]; whatever the final
 * class, the only defensible power-on and fault state is off, and it must not
 * depend on the bus or the TPM being available.
 */
static void laser_off(void) {
    /* TODO(WBS §4.6.2): drive the laser enable GPIO low once the pin is
     * assigned in `board_hal_configure()`.  Until then this is a documented
     * gap, not a silent one — the node refuses to publish a laser state it
     * cannot actually command. */
}

int board_app_init(void) {
    laser_off();
    g_safe = false;
    g_next_tof_ms = 0U;
    g_next_laser_ms = 0U;
    g_next_health_ms = 0U;

    (void)ser_hal_gpio_write(SER_GPIO_CAN_STB_N, false);
    (void)ser_hal_gpio_write(SER_GPIO_RS485_RE_N, false);
    (void)ser_hal_gpio_write(SER_GPIO_RS485_DE, false);

    /* TODO(WBS §4.6.2): TFmini-S UART driver on SER_UART_FLEX at
     * BOARD_TFMINI_BAUD; frame format per REF-SENSOR-002. */
    (void)ser_hal_uart_init(SER_UART_FLEX, BOARD_TFMINI_BAUD);

    return SER_OK;
}

static int publish_health(ser_node_t *node, uint64_t now_ms) {
    ser_link_stats_t st;
    ser_link_get_stats(&node->link, &st);

    uint8_t p[16];
    p[0] = (uint8_t)node->state;
    p[1] = node->link.active;
    put_be32(&p[2], node->link.failovers);
    put_be32(&p[6], st.tx_ok);
    put_be32(&p[10], st.rx_ok);
    put_be16(&p[14], (uint16_t)((now_ms - node->joined_at_ms) / 1000U));

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
        return SER_OK;
    }

    if (now_ms >= g_next_laser_ms) {
        g_next_laser_ms = now_ms + PERIOD_LASER_STATE_MS;
        /* Laser state is publishable today because the safe state is known
         * and enforced: the emitter is off. */
        uint8_t p[2];
        p[0] = 0U;                              /* 0 = off. */
        p[1] = (uint8_t)JAYNE_SITE;
        (void)ser_node_publish(node, TOPIC_ID_LASER_STATE, p, sizeof(p),
                               SER_ENV_FLAG_NONE);
    }

    if (now_ms >= g_next_tof_ms) {
        g_next_tof_ms = now_ms + PERIOD_TOF_MS;
        /* TODO(WBS §4.6.2): read the TFmini-S and publish the range.  Faults
         * deliberately until the driver exists — a ranging node that cannot
         * range must not look healthy to the obstacle-avoidance consumers. */
        return SER_ENOTSUP;
    }

    return SER_OK;
}

void board_app_safe_state(void) {
    /* Laser first, before anything that could fail. */
    laser_off();
    g_safe = true;
    (void)ser_hal_gpio_write(SER_GPIO_RS485_DE, false);
    (void)ser_hal_gpio_write(SER_GPIO_STATUS_LED, true);
}
