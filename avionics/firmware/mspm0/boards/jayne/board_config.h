/**
 * @file    board_config.h
 * @brief   Jayne U3 — nose/cargo vision board control MCU configuration.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Hardware: `avionics/kicad/Jayne/Jayne.md`.  U3 MSPM0G3507 owns the CAN-FD
 * trunk (native MCAN → U4 ISOW1044), UART1 to the TFmini-S ToF sensor, the
 * SPI management link to U2 KSZ9477, the SPI link to U5 SLB9670, UART0 to the
 * AM62A7 SoM, and the laser enable GPIO.
 *
 * One board design is installed at two sites — the bow sensor pod and the
 * cargo-bay nadir mount — which differ in laser class and therefore in
 * interlock behaviour, so the site is a build-time selection.
 */

#ifndef BOARD_CONFIG_H_
#define BOARD_CONFIG_H_

#define JAYNE_SITE_NOSE     (1U)
#define JAYNE_SITE_CARGO    (2U)

#ifndef JAYNE_SITE
#define JAYNE_SITE          JAYNE_SITE_NOSE
#endif

#define BOARD_NAME          "Jayne"

/** @brief Jayne nodes occupy 0x0300..0x03FF. */
#if JAYNE_SITE == JAYNE_SITE_NOSE
#define BOARD_NODE_ID           (0x0301U)
#define BOARD_XRCE_CAN_ID       (0x1000301U)
#define BOARD_XRCE_CLIENT_KEY   (0xA5000301UL)
#define BOARD_PARTICIPANT_REF   "serenity_jayne_nose"
#else
#define BOARD_NODE_ID           (0x0302U)
#define BOARD_XRCE_CAN_ID       (0x1000302U)
#define BOARD_XRCE_CLIENT_KEY   (0xA5000302UL)
#define BOARD_PARTICIPANT_REF   "serenity_jayne_cargo"
#endif

#define BOARD_ROS_DOMAIN_ID     (42U)

#define BOARD_CAN_NOMINAL_BPS   (1000000UL)
#define BOARD_CAN_DATA_BPS      (5000000UL)
#define BOARD_RS485_BAUD        (1000000UL)

/** @brief TFmini-S default UART rate [REF-SENSOR-002]. */
#define BOARD_TFMINI_BAUD       (115200UL)

/* --- Fleet topic identifiers ---------------------------------------------*/

#define TOPIC_ID_TOF_RANGE      (0x0310U)
#define TOPIC_ID_LASER_STATE    (0x0311U)
#define TOPIC_ID_LASER_COMMAND  (0x0312U)
#define TOPIC_ID_NODE_HEALTH    (0x0201U)

#define PERIOD_TOF_MS           (100U)     /* 10 Hz */
#define PERIOD_LASER_STATE_MS   (200U)     /* 5 Hz  */
#define PERIOD_HEALTH_MS        (1000U)    /* 1 Hz  */

#endif /* BOARD_CONFIG_H_ */
