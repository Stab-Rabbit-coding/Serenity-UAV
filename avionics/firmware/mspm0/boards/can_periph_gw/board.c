/**
 * @file    board.c
 * @brief   MAL-CAN-PERIPH-GW-PCB — topic table, QoS and bearer configuration.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * A node declares only the entities its own context needs: an encoder
 * gateway publishes a tilt angle, an ESC gateway publishes status and
 * subscribes to setpoints, a servo gateway subscribes to commands.  All three
 * publish node health.
 */

#include "serenity/board.h"
#include "serenity/node.h"

/* QoS shorthand, in the order of `ser_qos_t`: reliable, transient, keep_all,
 * depth.  Sensor streams are BEST_EFFORT + KEEP_LAST(1): a late sample is
 * worthless to a control loop, so retransmitting one costs bus time and
 * delivers stale data.  Commands are RELIABLE: a dropped setpoint is not
 * self-correcting. */
#define QOS_SENSOR      { 0U, 0U, 0U, 1U }
#define QOS_COMMAND     { 1U, 0U, 0U, 4U }
#define QOS_HEALTH      { 1U, 1U, 0U, 1U }

/**
 * @brief This node's topics.
 *
 * Type names must match what the PocketBeagle peers register, or SEDP will
 * not match the endpoints.  `serenity_msgs::msg::dds_::SignedSample_` is the
 * opaque-octet-sequence wrapper every signed sample uses — the envelope is
 * carried verbatim so the MAC still covers exactly the signed bytes on
 * arrival.
 */
const ser_topic_t board_topics[] = {
#if GW_ROLE == GW_ROLE_ENCODER
    {
        .id = TOPIC_ID_TILT_ANGLE,
        .name = "rt/serenity/nacelle/tilt_angle",
        .type_name = "serenity_msgs::msg::dds_::SignedSample_",
        .dir = SER_TOPIC_PUB,
        .qos = QOS_SENSOR,
        .env_flags = SER_ENV_FLAG_SAFETY,
    },
#elif GW_ROLE == GW_ROLE_ESC
    {
        .id = TOPIC_ID_ESC_STATUS,
        .name = "rt/serenity/esc/status",
        .type_name = "serenity_msgs::msg::dds_::SignedSample_",
        .dir = SER_TOPIC_PUB,
        .qos = QOS_SENSOR,
        .env_flags = SER_ENV_FLAG_SAFETY,
    },
    {
        .id = TOPIC_ID_ESC_COMMAND,
        .name = "rt/serenity/esc/command",
        .type_name = "serenity_msgs::msg::dds_::SignedSample_",
        .dir = SER_TOPIC_SUB,
        .qos = QOS_COMMAND,
        .env_flags = SER_ENV_FLAG_SAFETY,
    },
#else
    {
        .id = TOPIC_ID_SERVO_COMMAND,
        .name = "rt/serenity/servo/command",
        .type_name = "serenity_msgs::msg::dds_::SignedSample_",
        .dir = SER_TOPIC_SUB,
        .qos = QOS_COMMAND,
        .env_flags = SER_ENV_FLAG_SAFETY,
    },
#endif
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
 * @brief Both isolated buses, CAN-FD active and RS-485 standby.
 *
 * `CAN-PERIPH-GW-1.md` specifies republication on both isolated buses so
 * peers see the gateway without trusting an unsigned local link.  One XRCE
 * session over an active bearer with failover achieves that without doubling
 * the discovery traffic — and the TPM envelope makes which bearer carried a
 * sample irrelevant to a subscriber.
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
