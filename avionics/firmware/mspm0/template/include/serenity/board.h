/**
 * @file    board.h
 * @brief   Contract every MSPM0G3507 board must satisfy to use this template.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Three boards in this fleet carry an MSPM0G3507 and all three run this same
 * firmware template:
 *
 *   - `MAL-CAN-PERIPH-GW-PCB` (`boards/can_periph_gw/`) — the standalone
 *     trust-module gateway, 1..N independent stacks per PCB, bridging a tilt
 *     encoder, an ESC or a servo onto the isolated CAN-FD and RS-485 trunks.
 *     See `avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md`.
 *   - Jayne U3 (`boards/jayne/`) — the control half of the nose/cargo vision
 *     board: CAN-FD trunk, TFmini-S UART, KSZ9477 management SPI, laser GPIO.
 *     See `avionics/kicad/Jayne/Jayne.md`.
 *   - Kaylee U_MCU (`boards/kaylee/`) — the power-distribution board's Section
 *     H trust module.  See `avionics/kicad/Kaylee/Kaylee.md`.
 *
 * What a board supplies is deliberately small: a static description of itself
 * (`board_config.h`), a HAL pin map, and an application (`app.c`) with three
 * entry points.  Everything else — TPM bring-up, XRCE session, signing,
 * publication, fault handling — is the template's, identically on all three.
 * That is the whole point of the split: a change to the security or transport
 * behaviour is made once and every board inherits it.
 */

#ifndef SERENITY_BOARD_H_
#define SERENITY_BOARD_H_

#include "serenity/hal.h"

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Board-specific constants: pin map, identity, topic set, publication rates. */
#include "board_config.h"

/* --- Values every board_config.h must define ------------------------------
 *
 * The checks below turn a missing or malformed board configuration into a
 * compile error rather than a node that boots with a wrong CAN identity and
 * quietly collides with another node on the trunk.
 * --------------------------------------------------------------------------*/

#ifndef BOARD_NAME
#error "board_config.h must define BOARD_NAME (a string literal)"
#endif

#ifndef BOARD_NODE_ID
#error "board_config.h must define BOARD_NODE_ID (uint16_t, fleet-unique)"
#endif

#ifndef BOARD_XRCE_CAN_ID
#error "board_config.h must define BOARD_XRCE_CAN_ID (29-bit, fleet-unique)"
#endif

#ifndef BOARD_XRCE_CLIENT_KEY
#error "board_config.h must define BOARD_XRCE_CLIENT_KEY (uint32_t)"
#endif

#ifndef BOARD_ROS_DOMAIN_ID
#error "board_config.h must define BOARD_ROS_DOMAIN_ID"
#endif

#ifndef BOARD_CAN_NOMINAL_BPS
#error "board_config.h must define BOARD_CAN_NOMINAL_BPS"
#endif

#ifndef BOARD_CAN_DATA_BPS
#error "board_config.h must define BOARD_CAN_DATA_BPS"
#endif

#if BOARD_XRCE_CAN_ID > 0x1FFFFFFFU
#error "BOARD_XRCE_CAN_ID exceeds the 29-bit extended CAN identifier range"
#endif

/*
 * The isolated transceiver caps the data-phase rate: ISOW1044 is rated to
 * 5 Mbit/s [REF-SENSOR-009].  A board asking for more would run outside the
 * part's datasheet, so it is refused at compile time rather than discovered
 * as intermittent bus errors on the bench.
 */
#if BOARD_CAN_DATA_BPS > 5000000U
#error "BOARD_CAN_DATA_BPS exceeds the ISOW1044 rated 5 Mbit/s [REF-SENSOR-009]"
#endif

/**
 * @brief Application hook: called once after the TPM and XRCE session are up.
 *
 * The node is fully joined to the ROS 2 domain by this point and may publish.
 * Use it to bring up board-local sensors and actuators.
 *
 * @return SER_OK to continue, or a negative `SER_E*` code to fault the node.
 */
int board_app_init(void);

/**
 * @brief Application hook: called once per pass of the node main loop.
 *
 * Must not block for longer than the watchdog period.  Sample sensors, run
 * local control, and call `ser_node_publish()` for anything that should reach
 * the domain.
 *
 * @param now_ms Monotonic milliseconds, passed in so every hook in one pass
 *               sees a consistent timestamp.
 * @return SER_OK, or a negative `SER_E*` code to fault the node.
 */
int board_app_step(uint64_t now_ms);

/**
 * @brief Application hook: called when the node enters the FAULT state.
 *
 * Put board-local hardware into its safe state.  For an ESC gateway that
 * means commanding zero throttle; for a servo gateway, releasing drive; for
 * Jayne, extinguishing the laser.  This runs even when the bus is unusable,
 * so it must not depend on publication succeeding.
 */
void board_app_safe_state(void);

/**
 * @brief Board hook: map the logical HAL resources onto this board's pins.
 *
 * Called by `ser_hal_init()` before any peripheral is used.  Implemented in
 * `boards/<board>/board.c`.
 */
int board_hal_configure(void);

#ifdef __cplusplus
}
#endif

#endif /* SERENITY_BOARD_H_ */
