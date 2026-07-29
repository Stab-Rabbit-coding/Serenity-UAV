/**
 * @file    node.h
 * @brief   Trust-node lifecycle: TPM attest, join the DDS domain, publish.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * ## How an MSPM0 node is a full DDS peer
 *
 * The node creates its XRCE Participant **by reference**
 * (`uxr_buffer_create_participant_ref`), naming a Fast DDS participant
 * profile that the Agent resolves in its own XML configuration.  The Agent
 * then calls `create_participant_with_profile(domain_id, ref)`, which
 * instantiates a *separate* Fast DDS DomainParticipant for this node — its
 * own GUID, its own participant name, its own endpoints, announced by SPDP
 * and SEDP exactly like any other peer.  Other nodes in the domain discover
 * it as a peer, not as a proxy of the Agent.
 *
 * Because the profile is per-node, it carries **that node's own**
 * DDS-Security properties — identity CA, identity certificate, private key,
 * governance and permissions [REF-OMG-002 §9.3, §9.4].  Peers authenticate
 * the node's own credential during the DDS-Security handshake.
 *
 * The one thing the profile cannot give it: the DDS-Security private key
 * lives on the Agent host, because the ECDSA/ECDH handshake cannot run on a
 * Cortex-M0+ with no PKA engine.  That is precisely why each node also has
 * its own TPM.  `sec_envelope.h` carries a TPM-keyed MAC inside every sample,
 * so origin is proved by hardware the Agent does not hold:
 *
 *   DDS-Security  → this participant is `serenity/gw/enc_port`   (per-hop)
 *   TPM envelope  → this sample came out of that node's SLB9670  (end-to-end)
 *
 * A node implements only the entities its own context needs — the topics in
 * its `board_config.h` topic table, and nothing else.
 *
 * ## Lifecycle
 *
 *   BOOT ──► TPM ──► JOIN ──► RUN ──┬──► FAULT (latched, safe state)
 *                      ▲            │
 *                      └── REJOIN ◄─┘  (link failover or session loss)
 *
 * A node that cannot attest its TPM never reaches JOIN: publishing unsigned
 * data would be worse than publishing nothing, because a subscriber has no
 * way to distinguish it from data that was never sent.
 */

#ifndef SERENITY_NODE_H_
#define SERENITY_NODE_H_

#include "serenity/link.h"
#include "serenity/sec_envelope.h"
#include "serenity/tpm2.h"

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/** @brief Node lifecycle states. */
typedef enum {
    SER_NODE_BOOT = 0,  /**< HAL up, nothing else.                            */
    SER_NODE_TPM,       /**< TPM open, key provisioned, self-test passed.     */
    SER_NODE_JOIN,      /**< XRCE session up, DDS entities being created.     */
    SER_NODE_RUN,       /**< Joined; publishing.                              */
    SER_NODE_FAULT      /**< Latched fault; hardware in its safe state.       */
} ser_node_state_t;

/**
 * @brief DDS QoS for one topic, mirroring `uxrQoS_t`.
 *
 * Expressed by the node so the QoS a subscriber matches against is the
 * node's own declaration, not an Agent-wide default.
 */
typedef struct {
    uint8_t  reliable;  /**< 1 = RELIABLE, 0 = BEST_EFFORT.                   */
    uint8_t  transient; /**< 1 = TRANSIENT_LOCAL durability, 0 = VOLATILE.    */
    uint8_t  keep_all;  /**< 1 = KEEP_ALL history, 0 = KEEP_LAST.             */
    uint16_t depth;     /**< History depth when `keep_all` is 0.              */
} ser_qos_t;

/** @brief Direction of a topic from this node's point of view. */
typedef enum {
    SER_TOPIC_PUB = 0,  /**< Node publishes it.                               */
    SER_TOPIC_SUB       /**< Node subscribes to it.                           */
} ser_topic_dir_t;

/**
 * @brief One entry in a board's topic table.
 *
 * `type_name` is the ROS 2 / DDS type name the Agent registers, and must
 * match the type the PocketBeagle peers use, or discovery will not match the
 * endpoints.
 */
typedef struct {
    uint16_t        id;         /**< Fleet topic identifier; bound into MACs. */
    const char     *name;       /**< DDS topic name.                          */
    const char     *type_name;  /**< DDS type name.                           */
    ser_topic_dir_t dir;
    ser_qos_t       qos;
    uint8_t         env_flags;  /**< Default `SER_ENV_FLAG_*` for this topic. */
} ser_topic_t;

/** @brief Maximum topics a single node may declare. */
#define SER_NODE_MAX_TOPICS     (8U)

/** @brief Node context. */
typedef struct {
    ser_node_state_t state;
    ser_tpm2_t       tpm;
    ser_env_t        env;
    ser_link_t       link;

    const ser_topic_t *topics;
    uint8_t            topic_count;

    uint16_t         node_id;
    uint16_t         domain_id;
    const char      *participant_ref;    /**< Agent-side profile name.        */

    uint32_t         published;
    uint32_t         publish_errors;
    uint32_t         rejoins;
    uint64_t         joined_at_ms;
    int              last_error;
} ser_node_t;

/**
 * @brief Bring the node up: HAL, TPM, link, XRCE session, DDS entities.
 *
 * Runs the full BOOT → TPM → JOIN → RUN sequence, including the loopback
 * signing self-test that proves the TPM path works before the node publishes
 * anything.
 *
 * @return SER_OK when the node reaches RUN, else a negative `SER_E*` code
 *         with the node left in FAULT.
 */
int ser_node_start(ser_node_t *node);

/**
 * @brief Run one pass: service the XRCE session, maintain the link, and call
 *        the board's `board_app_step()`.
 *
 * Non-blocking beyond @p budget_ms.  Pet the watchdog around it.
 */
int ser_node_spin(ser_node_t *node, uint32_t budget_ms);

/**
 * @brief Seal @p payload in a TPM envelope and publish it on @p topic_id.
 *
 * The board's application calls this; it never touches the TPM or XRCE
 * directly.  A signing failure is reported and nothing is published — the
 * node does not fall back to sending unsigned data.
 */
int ser_node_publish(ser_node_t *node,
                     uint16_t topic_id,
                     const uint8_t *payload,
                     size_t len,
                     uint8_t extra_flags);

/** @brief Latch a fault, drive the board to its safe state, and stop publishing. */
void ser_node_fault(ser_node_t *node, int error);

/**
 * @brief The node currently running, for use inside the board hooks.
 *
 * The hooks are called from the node's own spin, so this is always the node
 * that invoked them.  Returns NULL before `ser_node_start()`.
 */
ser_node_t *ser_node_current(void);

#ifdef __cplusplus
}
#endif

#endif /* SERENITY_NODE_H_ */
