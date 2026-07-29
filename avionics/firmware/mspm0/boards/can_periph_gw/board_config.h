/**
 * @file    board_config.h
 * @brief   MAL-CAN-PERIPH-GW-PCB — trust-module gateway board configuration.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Hardware: `avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md`.
 * U1 MSPM0G3507, U2 SLB9670 TPM, U3 ISOW1044 (CAN-FD), U4 ISOW1412 (RS-485),
 * J_ENC (AK7455 SPI pigtail), J_FLEX (UART/TTL/PWM/BDSHOT).
 *
 * One PCB carries `N_STACKS` complete, independent trust modules, each with
 * its own MCU and TPM.  Each stack is its own DDS participant, so each needs
 * its own node id, CAN identifier and participant profile — selected at build
 * time by `GW_STACK_INDEX` and `GW_ROLE`, which the build sets per image.
 */

#ifndef BOARD_CONFIG_H_
#define BOARD_CONFIG_H_

/** @brief Which stack on the PCB this image is built for (1..4). */
#ifndef GW_STACK_INDEX
#define GW_STACK_INDEX      (1U)
#endif

/**
 * @brief Deployment role, selecting the topic set.
 *
 * `CAN-PERIPH-GW-1.md` defines three roles for the identical board:
 *   1 = nacelle tilt-encoder gateway (AK7455 over J_ENC)
 *   2 = per-EDF ESC gateway (DSHOT out, BDSHOT telemetry in, over J_FLEX)
 *   3 = servo actuator gateway (PWM/TTL command out, over J_FLEX)
 */
#define GW_ROLE_ENCODER     (1U)
#define GW_ROLE_ESC         (2U)
#define GW_ROLE_SERVO       (3U)

#ifndef GW_ROLE
#define GW_ROLE             GW_ROLE_ENCODER
#endif

#define BOARD_NAME          "CAN-PERIPH-GW-1"

/**
 * @brief Fleet node identifier.
 *
 * Gateways occupy 0x0200..0x02FF.  Blocks are assigned in the subsystem
 * README's node-identity table; keeping the blocks disjoint is what stops two
 * boards silently claiming one identity on the bus.
 */
#define BOARD_NODE_ID       (0x0200U + GW_STACK_INDEX)

/**
 * @brief 29-bit extended CAN identifier for this node's XRCE session.
 *
 * One identifier per client: the Agent replies to whatever identifier a frame
 * arrived on, so two nodes sharing one would interleave into a single XRCE
 * session and corrupt both.
 */
#define BOARD_XRCE_CAN_ID   (0x1000200U + GW_STACK_INDEX)

/** @brief XRCE client key; must be unique per Agent. */
#define BOARD_XRCE_CLIENT_KEY   (0xA5000200UL + GW_STACK_INDEX)

/**
 * @brief Fast DDS participant profile the Agent resolves for this node.
 *
 * Carries this node's own DDS-Security identity certificate, governance and
 * permissions — see `agent/README.md` and `agent/profiles.xml`.
 */
#if GW_ROLE == GW_ROLE_ENCODER
#define BOARD_PARTICIPANT_REF   "serenity_gw_encoder"
#elif GW_ROLE == GW_ROLE_ESC
#define BOARD_PARTICIPANT_REF   "serenity_gw_esc"
#else
#define BOARD_PARTICIPANT_REF   "serenity_gw_servo"
#endif

#define BOARD_ROS_DOMAIN_ID     (42U)

/*
 * CAN-FD bit timing.  5 Mbit/s data phase is the ISOW1044 rating
 * [REF-SENSOR-009] and matches the trunk rate recorded in
 * `avionics/kicad/Wash/Wash.md`.
 */
#define BOARD_CAN_NOMINAL_BPS   (1000000UL)
#define BOARD_CAN_DATA_BPS      (5000000UL)

/** @brief RS-485 standby bearer rate. */
#define BOARD_RS485_BAUD        (1000000UL)

/* --- Fleet topic identifiers ---------------------------------------------
 * Bound into every envelope MAC, so a value must never be reused for a
 * different meaning once flown.
 * --------------------------------------------------------------------------*/

#define TOPIC_ID_TILT_ANGLE     (0x0210U)
#define TOPIC_ID_ESC_STATUS     (0x0211U)
#define TOPIC_ID_ESC_COMMAND    (0x0212U)
#define TOPIC_ID_SERVO_COMMAND  (0x0213U)
#define TOPIC_ID_NODE_HEALTH    (0x0201U)

/** @brief Publication periods, milliseconds. */
#define PERIOD_TILT_MS          (50U)      /* 20 Hz */
#define PERIOD_ESC_STATUS_MS    (50U)      /* 20 Hz */
#define PERIOD_HEALTH_MS        (1000U)    /* 1 Hz  */

#endif /* BOARD_CONFIG_H_ */
