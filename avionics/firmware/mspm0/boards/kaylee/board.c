/**
 * @file    board.c
 * @brief   Kaylee U_MCU — topic table, QoS and bearer configuration.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 */

#include "serenity/board.h"
#include "serenity/node.h"

#define QOS_SENSOR      { 0U, 0U, 0U, 1U }
#define QOS_HEALTH      { 1U, 1U, 0U, 1U }

/**
 * @brief Kaylee's topics.
 *
 * Battery state is RELIABLE and TRANSIENT_LOCAL rather than best-effort: a
 * flight-control node that joins late needs the current pack state
 * immediately to make a go/no-go decision, and a dropped low-voltage sample
 * is not self-correcting the way a dropped tilt angle is.
 */
const ser_topic_t board_topics[] = {
    {
        .id = TOPIC_ID_BATTERY,
        .name = "rt/serenity/power/battery",
        .type_name = "serenity_msgs::msg::dds_::SignedSample_",
        .dir = SER_TOPIC_PUB,
        .qos = QOS_HEALTH,
        .env_flags = SER_ENV_FLAG_SAFETY,
    },
    {
        .id = TOPIC_ID_RAIL_STATUS,
        .name = "rt/serenity/power/rails",
        .type_name = "serenity_msgs::msg::dds_::SignedSample_",
        .dir = SER_TOPIC_PUB,
        .qos = QOS_SENSOR,
        .env_flags = SER_ENV_FLAG_SAFETY,
    },
    {
        .id = TOPIC_ID_NODE_HEALTH,
        .name = "rt/serenity/node/health",
        .type_name = "serenity_msgs::msg::dds_::SignedSample_",
        .dir = SER_TOPIC_PUB,
        .qos = QOS_HEALTH,
        .env_flags = SER_ENV_FLAG_NONE,
    },
};

const uint8_t board_topic_count =
    (uint8_t)(sizeof(board_topics) / sizeof(board_topics[0]));

void board_configure_link(ser_link_t *link) {
    link->cfg[0].kind = SER_LINK_CANFD;
    link->cfg[0].can_id = BOARD_XRCE_CAN_ID;
    link->cfg[0].nominal_bps = BOARD_CAN_NOMINAL_BPS;
    link->cfg[0].data_bps = BOARD_CAN_DATA_BPS;

    link->cfg[1].kind = SER_LINK_STREAM;
    link->cfg[1].uart = SER_UART_RS485;
    link->cfg[1].baud = BOARD_RS485_BAUD;

    link->count = 2U;
    link->failover_ms = 2000U;
}

/**
 * @brief Map the logical HAL resources onto this board's pins.
 *
 * On the sim HAL there is nothing to map — the bearers come from environment
 * variables — so this succeeds trivially.  The MSPM0 port overrides the pin
 * table it consults; see `hal/mspm0/hal_mspm0.c` and the board's KiCad
 * schematic for the authoritative pin assignment.
 */
int board_hal_configure(void) {
    return SER_OK;
}
