/**
 * @file    node.c
 * @brief   Trust-node lifecycle: TPM attest, join the DDS domain, publish.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * See `node.h` for how a node presents itself to the domain as a full peer.
 */

#include "serenity/node.h"

#include "serenity/board.h"
#include "serenity/hal.h"

#include <uxr/client/client.h>

#include <string.h>

/* ---------------------------------------------------------------------------
 * XRCE stream sizing
 *
 * These buffers dominate the node's RAM budget, so they are sized against the
 * MSPM0G3507's 32 KB SRAM [REF-SENSOR-004] rather than left at library
 * defaults.  History must be a power of two (upstream requirement).
 * ---------------------------------------------------------------------------*/

#define NODE_STREAM_HISTORY     (4U)
#define NODE_OUT_STREAM_SIZE    (SER_LINK_MTU * NODE_STREAM_HISTORY)
#define NODE_IN_STREAM_SIZE     (SER_LINK_MTU * NODE_STREAM_HISTORY)

/** @brief Largest sealed sample the node will build. */
#define NODE_SEAL_BUF_SIZE      (SER_ENV_TOTAL_LEN + 96U)

/** @brief Milliseconds the session waits for the Agent to confirm entities. */
#define NODE_ENTITY_TIMEOUT_MS  (2000)

/** @brief XRCE object-id index base for the per-topic entities. */
#define NODE_OBJ_PARTICIPANT    (0x01U)
#define NODE_OBJ_PUBLISHER      (0x01U)
#define NODE_OBJ_SUBSCRIBER     (0x01U)
#define NODE_OBJ_TOPIC_BASE     (0x10U)
#define NODE_OBJ_WRITER_BASE    (0x20U)
#define NODE_OBJ_READER_BASE    (0x30U)

/* Session state kept out of `ser_node_t` so `node.h` stays free of the
 * Micro XRCE-DDS headers; one node per MCU makes file scope safe. */
static uxrSession    g_session;
static uxrStreamId   g_out_stream;
static uxrStreamId   g_in_stream;
static uint8_t       g_out_buf[NODE_OUT_STREAM_SIZE];
static uint8_t       g_in_buf[NODE_IN_STREAM_SIZE];
static uxrObjectId   g_writer[SER_NODE_MAX_TOPICS];
static uxrObjectId   g_reader[SER_NODE_MAX_TOPICS];
static ser_node_t   *g_node;

/** @brief Translate this project's QoS struct into upstream's. */
static uxrQoS_t to_uxr_qos(const ser_qos_t *q) {
    uxrQoS_t out;
    out.durability = q->transient ? UXR_DURABILITY_TRANSIENT_LOCAL
                                  : UXR_DURABILITY_VOLATILE;
    out.reliability = q->reliable ? UXR_RELIABILITY_RELIABLE
                                  : UXR_RELIABILITY_BEST_EFFORT;
    out.history = q->keep_all ? UXR_HISTORY_KEEP_ALL : UXR_HISTORY_KEEP_LAST;
    out.depth = q->depth;
    return out;
}

/**
 * @brief Deliver a received sample to the board after verifying nothing.
 *
 * Inbound samples arrive already authenticated at the DDS layer by
 * DDS-Security on the peer-to-Agent hops.  End-to-end envelope verification
 * of *inbound* traffic needs the sending node's TPM key, which lives in the
 * PocketBeagle-side registry, not on this MCU — so a subscribing MSPM0 treats
 * the DDS-Security guarantee as its authorisation boundary and logs the
 * envelope header for the ground-side forensic record.  This is recorded as
 * an explicit limitation in the subsystem README rather than papered over.
 */
static void on_topic(uxrSession *session,
                     uxrObjectId object_id,
                     uint16_t request_id,
                     uxrStreamId stream_id,
                     struct ucdrBuffer *ub,
                     uint16_t length,
                     void *args) {
    (void)session;
    (void)request_id;
    (void)stream_id;
    (void)args;

    if ((g_node == NULL) || (ub == NULL)) {
        return;
    }

    for (uint8_t i = 0U; i < g_node->topic_count; ++i) {
        if ((g_node->topics[i].dir == SER_TOPIC_SUB) &&
            (g_reader[i].id == object_id.id)) {
            uint8_t buf[NODE_SEAL_BUF_SIZE];
            const size_t take = (length > sizeof(buf)) ? sizeof(buf) : length;
            ucdr_deserialize_array_uint8_t(ub, buf, (uint32_t)take);

            ser_env_hdr_t hdr;
            if (ser_env_parse_header(buf, take, &hdr) == SER_OK) {
                ser_hal_log("rx: topic=%u from node=%u ctr=%lu\n",
                            (unsigned)g_node->topics[i].id,
                            (unsigned)hdr.node_id,
                            (unsigned long)hdr.counter);
            }
            return;
        }
    }
}

/**
 * @brief Create the node's DDS entities: participant, pub/sub, and one
 *        topic + endpoint per entry in the board's topic table.
 *
 * The participant is created *by reference* so the Agent resolves a per-node
 * Fast DDS profile carrying this node's own DDS-Security identity — see
 * `node.h`.  Everything else is created binary-encoded, which costs no
 * Agent-side configuration and keeps the CREATE submessages small.
 */
static int create_entities(ser_node_t *node) {
    const uxrObjectId participant =
        uxr_object_id(NODE_OBJ_PARTICIPANT, UXR_PARTICIPANT_ID);

    uint16_t reqs[1 + (SER_NODE_MAX_TOPICS * 2U) + 2U];
    uint8_t  status[1 + (SER_NODE_MAX_TOPICS * 2U) + 2U];
    uint8_t  n = 0U;

    reqs[n++] = uxr_buffer_create_participant_ref(&g_session, g_out_stream,
                                                  participant,
                                                  node->domain_id,
                                                  node->participant_ref,
                                                  UXR_REPLACE | UXR_REUSE);

    bool need_pub = false;
    bool need_sub = false;
    for (uint8_t i = 0U; i < node->topic_count; ++i) {
        if (node->topics[i].dir == SER_TOPIC_PUB) {
            need_pub = true;
        } else {
            need_sub = true;
        }
    }

    const uxrObjectId publisher =
        uxr_object_id(NODE_OBJ_PUBLISHER, UXR_PUBLISHER_ID);
    const uxrObjectId subscriber =
        uxr_object_id(NODE_OBJ_SUBSCRIBER, UXR_SUBSCRIBER_ID);

    if (need_pub) {
        reqs[n++] = uxr_buffer_create_publisher_bin(&g_session, g_out_stream,
                                                    publisher, participant,
                                                    UXR_REPLACE | UXR_REUSE);
    }
    if (need_sub) {
        reqs[n++] = uxr_buffer_create_subscriber_bin(&g_session, g_out_stream,
                                                     subscriber, participant,
                                                     UXR_REPLACE | UXR_REUSE);
    }

    if (!uxr_run_session_until_all_status(&g_session, NODE_ENTITY_TIMEOUT_MS,
                                          reqs, status, n)) {
        ser_hal_log("node: participant/pub/sub creation failed\n");
        return SER_ETIMEDOUT;
    }

    /* Topics and endpoints, one round trip per topic so a single bad entry
     * is attributable rather than failing the whole batch anonymously. */
    for (uint8_t i = 0U; i < node->topic_count; ++i) {
        const ser_topic_t *t = &node->topics[i];
        const uxrObjectId topic =
            uxr_object_id((uint16_t)(NODE_OBJ_TOPIC_BASE + i), UXR_TOPIC_ID);
        uint16_t r[2];
        uint8_t  s[2];

        r[0] = uxr_buffer_create_topic_bin(&g_session, g_out_stream, topic,
                                           participant, t->name, t->type_name,
                                           UXR_REPLACE | UXR_REUSE);

        const uxrQoS_t qos = to_uxr_qos(&t->qos);
        if (t->dir == SER_TOPIC_PUB) {
            g_writer[i] = uxr_object_id((uint16_t)(NODE_OBJ_WRITER_BASE + i),
                                        UXR_DATAWRITER_ID);
            r[1] = uxr_buffer_create_datawriter_bin(&g_session, g_out_stream,
                                                    g_writer[i], publisher,
                                                    topic, qos,
                                                    UXR_REPLACE | UXR_REUSE);
        } else {
            g_reader[i] = uxr_object_id((uint16_t)(NODE_OBJ_READER_BASE + i),
                                        UXR_DATAREADER_ID);
            r[1] = uxr_buffer_create_datareader_bin(&g_session, g_out_stream,
                                                    g_reader[i], subscriber,
                                                    topic, qos,
                                                    UXR_REPLACE | UXR_REUSE);
        }

        if (!uxr_run_session_until_all_status(&g_session,
                                              NODE_ENTITY_TIMEOUT_MS,
                                              r, s, 2U)) {
            ser_hal_log("node: topic '%s' creation failed\n", t->name);
            return SER_ETIMEDOUT;
        }

        if (t->dir == SER_TOPIC_SUB) {
            uxrDeliveryControl ctrl = {0};
            ctrl.max_samples = UXR_MAX_SAMPLES_UNLIMITED;
            (void)uxr_buffer_request_data(&g_session, g_out_stream,
                                          g_reader[i], g_in_stream, &ctrl);
        }
    }

    return SER_OK;
}

/**
 * @brief Establish the XRCE session over the currently active bearer.
 */
static int join(ser_node_t *node) {
    uxrCommunication *comm = (uxrCommunication *)ser_link_comm(&node->link);
    if (comm == NULL) {
        return SER_ENODEV;
    }

    uxr_init_session(&g_session, comm, (uint32_t)BOARD_XRCE_CLIENT_KEY);
    uxr_set_topic_callback(&g_session, on_topic, node);

    if (!uxr_create_session(&g_session)) {
        ser_hal_log("node: no Agent on bearer %u\n", (unsigned)node->link.active);
        return SER_ETIMEDOUT;
    }

    g_out_stream = uxr_create_output_reliable_stream(&g_session, g_out_buf,
                                                     sizeof(g_out_buf),
                                                     NODE_STREAM_HISTORY);
    g_in_stream = uxr_create_input_reliable_stream(&g_session, g_in_buf,
                                                   sizeof(g_in_buf),
                                                   NODE_STREAM_HISTORY);

    const int rc = create_entities(node);
    if (rc != SER_OK) {
        (void)uxr_delete_session(&g_session);
        return rc;
    }

    /*
     * Synchronise the session clock with the Agent.  The envelope timestamp
     * stays the MCU's own monotonic time — an Agent-derived time would make
     * the forensic record depend on the very component the envelope exists to
     * distrust — but session timing benefits from the sync.
     */
    (void)uxr_sync_session(&g_session, 100);

    node->joined_at_ms = ser_hal_time_ms();
    return SER_OK;
}

int ser_node_start(ser_node_t *node) {
    if ((node == NULL) || (node->topics == NULL) ||
        (node->topic_count == 0U) ||
        (node->topic_count > SER_NODE_MAX_TOPICS) ||
        (node->participant_ref == NULL)) {
        return SER_EINVAL;
    }

    g_node = node;
    node->state = SER_NODE_BOOT;

    /* ---- TPM ------------------------------------------------------------ */
    int rc = ser_tpm2_open(&node->tpm);
    if (rc != SER_OK) {
        ser_node_fault(node, rc);
        return rc;
    }
    rc = ser_tpm2_provision_signing_key(&node->tpm);
    if (rc != SER_OK) {
        ser_node_fault(node, rc);
        return rc;
    }
    rc = ser_env_init(&node->env, &node->tpm, node->node_id);
    if (rc != SER_OK) {
        ser_node_fault(node, rc);
        return rc;
    }

    /*
     * Loopback self-test: seal a known buffer and verify it.  This proves the
     * whole signing path — TIS transport, TPM command marshalling, hashing,
     * MAC truncation — before the node is allowed to publish.  A node whose
     * signing is subtly broken would otherwise emit plausible, unverifiable
     * telemetry and only be caught on the far side of the bus.
     */
    {
        static const uint8_t probe[8] = {
            0xA5U, 0x5AU, 0x00U, 0xFFU, 0x12U, 0x34U, 0x56U, 0x78U
        };
        uint8_t sealed[SER_ENV_TOTAL_LEN + sizeof(probe)];
        size_t sealed_len = 0U;

        rc = ser_env_seal(&node->env, 0xFFFFU, SER_ENV_FLAG_NONE,
                          probe, sizeof(probe),
                          sealed, sizeof(sealed), &sealed_len);
        if (rc == SER_OK) {
            rc = ser_env_verify(&node->env, 0xFFFFU, sealed, sealed_len,
                                NULL, NULL, NULL);
        }
        if (rc != SER_OK) {
            ser_hal_log("node: signing self-test FAILED rc=%d\n", rc);
            ser_node_fault(node, rc);
            return rc;
        }
    }

    node->state = SER_NODE_TPM;
    ser_hal_log("node: TPM ready, identity established\n");

    /* ---- Link and domain ------------------------------------------------ */
    rc = ser_link_open(&node->link);
    if (rc != SER_OK) {
        ser_node_fault(node, rc);
        return rc;
    }

    node->state = SER_NODE_JOIN;
    rc = join(node);
    if (rc != SER_OK) {
        ser_node_fault(node, rc);
        return rc;
    }

    /* ---- Application ---------------------------------------------------- */
    rc = board_app_init();
    if (rc != SER_OK) {
        ser_node_fault(node, rc);
        return rc;
    }

    node->state = SER_NODE_RUN;
    ser_hal_log("node: joined domain %u as '%s'\n",
                (unsigned)node->domain_id, node->participant_ref);
    return SER_OK;
}

int ser_node_publish(ser_node_t *node,
                     uint16_t topic_id,
                     const uint8_t *payload,
                     size_t len,
                     uint8_t extra_flags) {
    if ((node == NULL) || (node->state != SER_NODE_RUN)) {
        return SER_EINVAL;
    }

    uint8_t idx = SER_NODE_MAX_TOPICS;
    for (uint8_t i = 0U; i < node->topic_count; ++i) {
        if ((node->topics[i].id == topic_id) &&
            (node->topics[i].dir == SER_TOPIC_PUB)) {
            idx = i;
            break;
        }
    }
    if (idx == SER_NODE_MAX_TOPICS) {
        return SER_EINVAL;
    }

    uint8_t sealed[NODE_SEAL_BUF_SIZE];
    size_t sealed_len = 0U;
    const int rc = ser_env_seal(&node->env, topic_id,
                                (uint8_t)(node->topics[idx].env_flags
                                          | extra_flags),
                                payload, len,
                                sealed, sizeof(sealed), &sealed_len);
    if (rc != SER_OK) {
        /* Signing failed: publish nothing.  Unsigned telemetry is worse than
         * silence, because a subscriber cannot tell it from forged data. */
        node->publish_errors++;
        node->last_error = rc;
        return rc;
    }

    /*
     * The sample is an opaque octet sequence: a 4-byte CDR length followed by
     * the sealed bytes.  Keeping the DDS type opaque means the envelope is
     * never re-encoded in transit, so the MAC still covers exactly the bytes
     * that were signed when it reaches a subscriber.
     */
    ucdrBuffer ub;
    const uint32_t topic_size = (uint32_t)(4U + sealed_len);
    (void)uxr_prepare_output_stream(&g_session, g_out_stream, g_writer[idx],
                                    &ub, topic_size);
    ucdr_serialize_uint32_t(&ub, (uint32_t)sealed_len);
    ucdr_serialize_array_uint8_t(&ub, sealed, (uint32_t)sealed_len);

    node->published++;
    return SER_OK;
}

int ser_node_spin(ser_node_t *node, uint32_t budget_ms) {
    if ((node == NULL) || (node->state == SER_NODE_FAULT)) {
        return SER_EINVAL;
    }

    const uint64_t now = ser_hal_time_ms();

    /*
     * A bearer switch changes which Agent endpoint the node is talking to, so
     * the XRCE session must be recreated rather than resumed — session state
     * is per-endpoint and replaying it onto a different bearer would leave
     * the Agent and the node disagreeing about stream sequence numbers.
     */
    if (ser_link_maintain(&node->link, now)) {
        (void)uxr_delete_session(&g_session);
        node->state = SER_NODE_JOIN;
        const int rc = join(node);
        if (rc != SER_OK) {
            return rc;      /* Stay in JOIN; the next spin retries. */
        }
        node->rejoins++;
        node->state = SER_NODE_RUN;
    }

    const int rc = board_app_step(now);
    if (rc != SER_OK) {
        ser_node_fault(node, rc);
        return rc;
    }

    (void)uxr_run_session_time(&g_session, (int)budget_ms);
    return SER_OK;
}

ser_node_t *ser_node_current(void) {
    return g_node;
}

void ser_node_fault(ser_node_t *node, int error) {
    if (node == NULL) {
        return;
    }
    node->state = SER_NODE_FAULT;
    node->last_error = error;

    /* Hardware first: the safe state must not depend on the bus being
     * usable, because a bus fault is one of the reasons we get here. */
    board_app_safe_state();
    ser_hal_log("node: FAULT rc=%d\n", error);
}
