/**
 * @file    main.c
 * @brief   Shared entry point for every MSPM0G3507 trust node.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Identical on CAN-PERIPH-GW-1, Jayne U3 and Kaylee U_MCU.  Everything that
 * differs between them is in `boards/<board>/`.
 */

#include "serenity/board.h"
#include "serenity/hal.h"
#include "serenity/node.h"

#include <string.h>

/** @brief Milliseconds of XRCE session servicing per main-loop pass. */
#define MAIN_SPIN_BUDGET_MS     (10U)

/** @brief Delay between restart attempts after a fault, milliseconds. */
#define MAIN_FAULT_RETRY_MS     (1000U)

/** @brief Topic table for this board, from `boards/<board>/board.c`. */
extern const ser_topic_t board_topics[];
extern const uint8_t     board_topic_count;

/** @brief Bearer configuration for this board, from `boards/<board>/board.c`. */
extern void board_configure_link(ser_link_t *link);

static ser_node_t g_node;

int main(void) {
    if (ser_hal_init() != SER_OK) {
        /* Without a HAL there is no log and no bus; the watchdog is the only
         * remaining recovery path, so spin and let it fire. */
        for (;;) {
        }
    }

    ser_hal_log("\n%s starting (node %u, domain %u)\n",
                BOARD_NAME, (unsigned)BOARD_NODE_ID,
                (unsigned)BOARD_ROS_DOMAIN_ID);

    (void)ser_hal_watchdog_start();

    for (;;) {
        memset(&g_node, 0, sizeof(g_node));
        g_node.node_id = BOARD_NODE_ID;
        g_node.domain_id = BOARD_ROS_DOMAIN_ID;
        g_node.participant_ref = BOARD_PARTICIPANT_REF;
        g_node.topics = board_topics;
        g_node.topic_count = board_topic_count;
        board_configure_link(&g_node.link);

        if (ser_node_start(&g_node) == SER_OK) {
            while (g_node.state == SER_NODE_RUN) {
                ser_hal_watchdog_pet();
                (void)ser_node_spin(&g_node, MAIN_SPIN_BUDGET_MS);
            }
        }

        /*
         * Reaching here means the node faulted.  The board is already in its
         * safe state (`ser_node_fault()` did that first).  Retry from scratch
         * rather than resetting the MCU: a full restart re-runs the TPM
         * attestation and re-establishes identity, which is what a transient
         * bus or Agent outage needs, without losing the fault log to a reset.
         */
        ser_hal_watchdog_pet();
        ser_hal_log("%s: restarting after fault rc=%d\n",
                    BOARD_NAME, g_node.last_error);
        ser_hal_delay_us(MAIN_FAULT_RETRY_MS * 1000U);
    }
}
