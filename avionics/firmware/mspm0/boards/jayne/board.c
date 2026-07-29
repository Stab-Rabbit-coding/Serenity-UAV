/**
 * @file    board.c
 * @brief   Jayne U3 — topic table, QoS and bearer configuration.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 */

#include "serenity/board.h"
#include "serenity/node.h"

#define QOS_SENSOR      { 0U, 0U, 0U, 1U }
#define QOS_COMMAND     { 1U, 0U, 0U, 4U }
#define QOS_HEALTH      { 1U, 1U, 0U, 1U }

/**
 * @brief Jayne's topics.
 *
 * The laser state is TRANSIENT_LOCAL and RELIABLE: a subscriber joining late
 * must immediately learn whether the laser is emitting, which a VOLATILE
 * topic would not tell it until the next periodic sample.  For a laser
 * product under IEC 60825-1 [REF-IEC-002] that gap is not acceptable.
 */
const ser_topic_t board_topics[] = {
    {
        .id = TOPIC_ID_TOF_RANGE,
        .name = "rt/serenity/jayne/tof_range",
        .type_name = "serenity_msgs::msg::dds_::SignedSample_",
        .dir = SER_TOPIC_PUB,
        .qos = QOS_SENSOR,
        .env_flags = SER_ENV_FLAG_SAFETY,
    },
    {
        .id = TOPIC_ID_LASER_STATE,
        .name = "rt/serenity/jayne/laser_state",
        .type_name = "serenity_msgs::msg::dds_::SignedSample_",
        .dir = SER_TOPIC_PUB,
        .qos = QOS_HEALTH,
        .env_flags = SER_ENV_FLAG_SAFETY,
    },
    {
        .id = TOPIC_ID_LASER_COMMAND,
        .name = "rt/serenity/jayne/laser_command",
        .type_name = "serenity_msgs::msg::dds_::SignedSample_",
        .dir = SER_TOPIC_SUB,
        .qos = QOS_COMMAND,
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

/**
 * @brief CAN-FD active, RS-485 standby.
 *
 * Jayne also sits on the Ethernet ring, but through U2 KSZ9477 — and U3
 * reaches that switch only over its SPI *management* port, not a MAC data
 * path (`Jayne.md`).  Video egress uses the ring via U1 AM62A7; the control
 * MCU's DDS traffic does not.
 */
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
