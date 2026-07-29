/**
 * @file    link.h
 * @brief   Bearer-agnostic XRCE link layer with redundant-bus failover.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * DDS is transport-agnostic, and so is this: the node's link to its Agent is
 * described by a small vtable, and every bearer the MSPM0G3507 can physically
 * reach implements it.
 *
 * ## Which bearers live where
 *
 * The MSPM0 boards reach exactly two of the airframe's four onboard buses.
 * The rest are on the far side of the Agent, where Fast DDS rides them
 * natively and needs nothing from this file:
 *
 * | Bus / net              | On the MSPM0?                | Carried by        |
 * |------------------------|------------------------------|-------------------|
 * | CAN-FD (isolated)      | yes — MCAN + ISOW1044        | `SER_LINK_CANFD`  |
 * | RS-485 (isolated)      | yes — UART + ISOW1412        | `SER_LINK_STREAM` |
 * | Ethernet ring          | no — no MAC on the part      | Fast DDS peer     |
 * | MIL-STD-1553B          | no — PRU-ICSS on the Beagle  | Fast DDS peer     |
 * | Wi-Fi 5 GHz            | no                           | Fast DDS peer     |
 * | Zigbee 2.4 GHz         | no                           | Fast DDS peer     |
 * | SiK / MAVLink 915 MHz  | no                           | Fast DDS peer     |
 * | AX.25 on 49 MHz        | no — and not a DDS bearer    | (see below)       |
 *
 * AX.25 is correctly excluded.  47 CFR Part 15 §15.235 [REF-FCC-003] limits
 * that channel to a narrow, low-duty-cycle link, and AX.25 over it is a
 * connectionless packet service with no useful throughput for RTPS discovery
 * traffic; it stays a MAVLink/telemetry backup path, not a DDS transport.
 *
 * `SER_LINK_STREAM` is a generic framed byte stream, so a future board that
 * wires a UART-attached bearer (a SiK modem, a 1553 bridge) to an MSPM0 gets
 * that bearer for free — nothing above this layer changes.
 *
 * ## Why the custom transport rather than upstream's CAN profile
 *
 * Micro XRCE-DDS ships a CAN-FD transport profile whose platform half is
 * SocketCAN-only.  Porting it would have meant one code path per bearer, a
 * force-include to supply `struct uxrCANPlatform`, and no way to switch
 * bearers at runtime.  Binding every bearer to upstream's *custom* transport
 * instead gives one code path, per-bearer framing selection, and runtime
 * failover, without modifying anything in the eProsima tree.
 *
 * ## Framing
 *
 * `SER_LINK_CANFD` is packet-oriented: a CAN-FD frame already delimits a
 * message, so framing is off and the length-prefix format the Agent's CAN
 * transport expects is applied here (`data[0]` = payload length, payload in
 * `data[1..]`, DLC rounded up to a legal CAN-FD length per ISO 11898-1:2015
 * [REF-ISO-001] and zero-padded).
 *
 * `SER_LINK_STREAM` is byte-oriented, so upstream's stream framing protocol
 * is enabled and does the delimiting.
 *
 * ## MTU
 *
 * One MTU for every bearer, set to 63 bytes — the CAN-FD ceiling (64-byte
 * data field less the length prefix).  A stream bearer could carry more, but
 * a single MTU means a sample that fits one bearer fits the other, which is
 * what makes failover transparent instead of a reconfiguration.  Samples
 * larger than the MTU are fragmented by the XRCE reliable output stream.
 */

#ifndef SERENITY_LINK_H_
#define SERENITY_LINK_H_

#include "serenity/hal.h"

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Transport MTU, bytes.  Must equal `UCLIENT_CUSTOM_TRANSPORT_MTU`
 *        in the build's client configuration.
 */
#define SER_LINK_MTU        (63U)

/** @brief Bearer kinds. */
typedef enum {
    SER_LINK_CANFD = 0,     /**< Packet bearer: MCAN + isolated transceiver.  */
    SER_LINK_STREAM,        /**< Framed byte stream: RS-485, UART bearers.    */
    SER_LINK_KIND_COUNT
} ser_link_kind_t;

/** @brief Per-bearer configuration. */
typedef struct {
    ser_link_kind_t kind;
    uint32_t        can_id;         /**< CAN only: 29-bit client identifier.  */
    uint32_t        nominal_bps;    /**< CAN only: arbitration bit rate.      */
    uint32_t        data_bps;       /**< CAN only: data-phase bit rate.       */
    ser_uart_t      uart;           /**< Stream only: which logical UART.     */
    uint32_t        baud;           /**< Stream only: bit rate.               */
} ser_link_cfg_t;

/** @brief Health counters, published as node telemetry. */
typedef struct {
    uint32_t tx_ok;
    uint32_t tx_fail;
    uint32_t rx_ok;
    uint32_t rx_malformed;
    uint64_t last_rx_ms;    /**< Monotonic time of the last accepted frame.   */
} ser_link_stats_t;

/**
 * @brief A bearer pair with automatic failover.
 *
 * `CAN-PERIPH-GW-1.md` specifies that a gateway republishes on both isolated
 * buses so every other node sees its telemetry without trusting an unsigned
 * local link.  Rather than run two XRCE sessions (two Agent sessions, two
 * sets of DDS entities, double the discovery traffic), the node runs one
 * session over an active bearer and fails over to the standby when the active
 * one stops carrying traffic.  The published data is identical either way,
 * and the TPM envelope makes the choice of bearer irrelevant to a subscriber.
 */
typedef struct ser_link {
    ser_link_cfg_t  cfg[2];         /**< [0] primary, [1] standby.            */
    uint8_t         count;          /**< 1 or 2 bearers configured.           */
    uint8_t         active;         /**< Index of the bearer in use.          */
    uint32_t        failover_ms;    /**< Silence before switching bearers.    */
    uint32_t        failovers;      /**< Times the node has switched.         */
    ser_link_stats_t stats[2];
    bool            open;
} ser_link_t;

/**
 * @brief Bring up the configured bearers and bind them to the XRCE session.
 *
 * @param link  Link state, with `cfg` and `count` already filled in by the
 *              board.  `failover_ms` of 0 selects the default of 2000 ms.
 * @return SER_OK, or a negative `SER_E*` code if no bearer came up.
 */
int ser_link_open(ser_link_t *link);

/** @brief Shut the bearers down. */
int ser_link_close(ser_link_t *link);

/**
 * @brief Consider switching to the standby bearer.
 *
 * Called once per node main-loop pass.  Switches when the active bearer has
 * seen no traffic for `failover_ms` and a standby exists.  Returns true if a
 * switch happened, so the caller can re-establish the XRCE session — an Agent
 * reached over a different bearer is a different endpoint and the session
 * must be recreated, not resumed.
 */
bool ser_link_maintain(ser_link_t *link, uint64_t now_ms);

/**
 * @brief Access the `uxrCommunication` for the active bearer.
 *
 * Returned as `void *` so this header does not drag the whole Micro XRCE-DDS
 * client into every translation unit that touches a link.  The node layer
 * casts it back.
 */
void *ser_link_comm(ser_link_t *link);

/** @brief Copy out the active bearer's statistics. */
void ser_link_get_stats(const ser_link_t *link, ser_link_stats_t *out);

#ifdef __cplusplus
}
#endif

#endif /* SERENITY_LINK_H_ */
