/**
 * @file    app.c
 * @brief   Kaylee U_MCU — battery and rail telemetry, signed.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * The BQ76930 cell-monitor driver is a separate WBS item, and Kaylee.md
 * records that U_CELL is not yet on the PCB at all.  This file is the
 * publication skeleton; it does not fabricate pack voltages.
 */

#include "serenity/board.h"
#include "serenity/hal.h"
#include "serenity/node.h"

#include <string.h>

static uint64_t g_next_batt_ms;
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

int board_app_init(void) {
    g_safe = false;
    g_next_batt_ms = 0U;
    g_next_health_ms = 0U;

    (void)ser_hal_gpio_write(SER_GPIO_CAN_STB_N, false);
    (void)ser_hal_gpio_write(SER_GPIO_RS485_RE_N, false);
    (void)ser_hal_gpio_write(SER_GPIO_RS485_DE, false);

    /* TODO(WBS §4.7.6): BQ76930 cell-monitor I2C driver.  Blocked upstream:
     * `Kaylee.md` records U_CELL as still missing from the PCB, so there is
     * no hardware to talk to yet. */
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

    if (now_ms >= g_next_batt_ms) {
        g_next_batt_ms = now_ms + PERIOD_BATTERY_MS;
        /* TODO(WBS §4.7.6): read the BQ76930 and publish pack state.  Faults
         * deliberately: a PDB node that cannot read the pack must not appear
         * healthy to a flight-control node making a go/no-go decision. */
        return SER_ENOTSUP;
    }

    return SER_OK;
}

void board_app_safe_state(void) {
    g_safe = true;
    /* Kaylee's power stages are hardware-latched; the trust module does not
     * gate them, so there is nothing for it to shed here.  Dropping the
     * RS-485 driver keeps a faulted node off the standby bus. */
    (void)ser_hal_gpio_write(SER_GPIO_RS485_DE, false);
    (void)ser_hal_gpio_write(SER_GPIO_STATUS_LED, true);
}
