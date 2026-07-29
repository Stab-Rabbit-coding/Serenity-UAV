/**
 * @file    board_config.h
 * @brief   Kaylee U_MCU — power-distribution board trust module configuration.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Hardware: `avionics/kicad/Kaylee/Kaylee.md` Section H — U_MCU MSPM0G3507,
 * U_TPM SLB9670, U_ISOCAN ISOW1044, U_RS485 ISOW1412.  Kaylee's own context
 * is battery and power-rail state, so that is all this node publishes.
 */

#ifndef BOARD_CONFIG_H_
#define BOARD_CONFIG_H_

#define BOARD_NAME              "Kaylee"

/** @brief Kaylee occupies 0x0400..0x04FF; it is a single node. */
#define BOARD_NODE_ID           (0x0401U)
#define BOARD_XRCE_CAN_ID       (0x1000401U)
#define BOARD_XRCE_CLIENT_KEY   (0xA5000401UL)
#define BOARD_PARTICIPANT_REF   "serenity_kaylee_pdb"

#define BOARD_ROS_DOMAIN_ID     (42U)

#define BOARD_CAN_NOMINAL_BPS   (1000000UL)
#define BOARD_CAN_DATA_BPS      (5000000UL)
#define BOARD_RS485_BAUD        (1000000UL)

/* --- Fleet topic identifiers ---------------------------------------------*/

#define TOPIC_ID_BATTERY        (0x0410U)
#define TOPIC_ID_RAIL_STATUS    (0x0411U)
#define TOPIC_ID_NODE_HEALTH    (0x0201U)

#define PERIOD_BATTERY_MS       (500U)     /* 2 Hz */
#define PERIOD_RAIL_MS          (500U)     /* 2 Hz */
#define PERIOD_HEALTH_MS        (1000U)    /* 1 Hz */

#endif /* BOARD_CONFIG_H_ */
