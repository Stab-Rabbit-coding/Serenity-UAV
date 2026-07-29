/**
 * @file    sec_envelope.c
 * @brief   TPM-anchored message envelope carried inside every DDS sample.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * See `sec_envelope.h` for the wire layout, the DDS-Security relationship and
 * the MAC-truncation citation.
 */

#include "serenity/sec_envelope.h"

#include "serenity/hal.h"
#include "serenity/sha256.h"

#include <string.h>

/* Header field offsets; see the table in sec_envelope.h. */
#define ENV_OFF_MAGIC_VER   (0U)
#define ENV_OFF_FLAGS       (1U)
#define ENV_OFF_NODE_ID     (2U)
#define ENV_OFF_EPOCH       (4U)
#define ENV_OFF_COUNTER     (8U)
#define ENV_OFF_TIMESTAMP   (12U)
#define ENV_OFF_KEY_ID      (20U)

#if (ENV_OFF_KEY_ID + 4U) != SER_ENV_HDR_LEN
#error "sec_envelope: field offsets disagree with SER_ENV_HDR_LEN"
#endif
#if (SER_ENV_MAC_LEN < 4U) || (SER_ENV_MAC_LEN > TPM2_SHA256_LEN)
#error "sec_envelope: SER_ENV_MAC_LEN outside NIST SP 800-107 Rev 1 §5.3.3 range"
#endif

/* --- Big-endian accessors -------------------------------------------------*/

static void put_be16(uint8_t *p, uint16_t v) {
    p[0] = (uint8_t)(v >> 8);
    p[1] = (uint8_t)v;
}

static void put_be32(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)(v >> 24);
    p[1] = (uint8_t)(v >> 16);
    p[2] = (uint8_t)(v >> 8);
    p[3] = (uint8_t)v;
}

static void put_be64(uint8_t *p, uint64_t v) {
    put_be32(p, (uint32_t)(v >> 32));
    put_be32(&p[4], (uint32_t)v);
}

static uint16_t get_be16(const uint8_t *p) {
    return (uint16_t)(((uint16_t)p[0] << 8) | (uint16_t)p[1]);
}

static uint32_t get_be32(const uint8_t *p) {
    return ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16)
           | ((uint32_t)p[2] << 8) | (uint32_t)p[3];
}

static uint64_t get_be64(const uint8_t *p) {
    return ((uint64_t)get_be32(p) << 32) | (uint64_t)get_be32(&p[4]);
}

/**
 * @brief Constant-time byte comparison.
 *
 * `memcmp` returns at the first differing byte, so its timing leaks how many
 * leading bytes of a forged MAC were correct — enough, over many attempts, to
 * forge a MAC byte by byte.  This accumulates every difference before
 * testing, so timing is independent of where the mismatch is.
 */
static bool ct_equal(const uint8_t *a, const uint8_t *b, size_t len) {
    uint8_t diff = 0U;
    for (size_t i = 0U; i < len; ++i) {
        diff |= (uint8_t)(a[i] ^ b[i]);
    }
    return diff == 0U;
}

/**
 * @brief Compute the truncated MAC over header, payload and topic identity.
 *
 * SHA-256 over `header || payload || topic_id_be16` in one streaming pass,
 * then TPM2_HMAC over the resulting 32-byte digest.  Hashing first keeps the
 * TPM command a fixed 32-byte input, so signing cost does not grow with
 * payload size — the property that makes per-message TPM signing affordable
 * at all on an SPI-attached TPM.
 *
 * `topic_id` is appended to the hash input but never transmitted, binding the
 * MAC to the topic without spending wire bytes.
 */
static int env_mac(ser_env_t *env,
                   const uint8_t *hdr,
                   const uint8_t *payload,
                   size_t payload_len,
                   uint16_t topic_id,
                   uint8_t mac_out[SER_ENV_MAC_LEN]) {
    uint8_t digest[SER_SHA256_DIGEST_LEN];
    uint8_t topic_be[2];
    ser_sha256_t sha;

    put_be16(topic_be, topic_id);

    ser_sha256_init(&sha);
    ser_sha256_update(&sha, hdr, SER_ENV_HDR_LEN);
    if ((payload != NULL) && (payload_len > 0U)) {
        ser_sha256_update(&sha, payload, payload_len);
    }
    ser_sha256_update(&sha, topic_be, sizeof(topic_be));
    ser_sha256_final(&sha, digest);

    uint8_t full[TPM2_SHA256_LEN];
    const int rc = ser_tpm2_hmac(env->tpm, digest, sizeof(digest), full);
    memset(digest, 0, sizeof(digest));
    if (rc != SER_OK) {
        memset(full, 0, sizeof(full));
        return rc;
    }

    /* Leftmost bytes, per NIST SP 800-107 Rev 1 §5.3.3 [REF-NIST-006]. */
    memcpy(mac_out, full, SER_ENV_MAC_LEN);
    memset(full, 0, sizeof(full));
    return SER_OK;
}

int ser_env_init(ser_env_t *env, ser_tpm2_t *tpm, uint16_t node_id) {
    if ((env == NULL) || (tpm == NULL) || !tpm->ready) {
        return SER_EINVAL;
    }

    memset(env, 0, sizeof(*env));
    env->tpm = tpm;
    env->node_id = node_id;

    /* A cached key Name is the proof that a signing key exists at the
     * persistent handle.  Without one the node has no identity and must not
     * be allowed to publish. */
    if (tpm->key_name_len < sizeof(env->key_id)) {
        if (ser_tpm2_load_key_name(tpm) != SER_OK) {
            return SER_ENODEV;
        }
    }
    if (tpm->key_name_len < sizeof(env->key_id)) {
        return SER_ENODEV;
    }
    memcpy(env->key_id, tpm->key_name, sizeof(env->key_id));

    uint8_t seed[4];
    const int rc = ser_tpm2_get_random(tpm, seed, sizeof(seed));
    if (rc != SER_OK) {
        return rc;
    }
    env->epoch = get_be32(seed);
    env->counter = 0U;
    env->ready = true;

    ser_hal_log("env: node=%u epoch=%08lx key=%02x%02x%02x%02x\n",
                (unsigned)node_id, (unsigned long)env->epoch,
                env->key_id[0], env->key_id[1],
                env->key_id[2], env->key_id[3]);
    return SER_OK;
}

int ser_env_seal(ser_env_t *env,
                 uint16_t topic_id,
                 uint8_t flags,
                 const uint8_t *payload,
                 size_t len,
                 uint8_t *out,
                 size_t out_cap,
                 size_t *out_len) {
    if ((env == NULL) || !env->ready || (out == NULL) || (out_len == NULL) ||
        ((payload == NULL) && (len > 0U))) {
        return SER_EINVAL;
    }
    if (out_cap < (len + SER_ENV_TOTAL_LEN)) {
        return SER_ENOSPC;
    }

    /*
     * Increment before use, so the first message of an epoch carries counter
     * 1 and a receiver's "last accepted" can start at 0 with no special case.
     * Wrap is a hard stop, not a rollover: reusing (epoch, counter) reopens
     * the replay window, so the node faults visibly instead of silently
     * losing replay protection.  2^32 messages at 50 Hz is over two and a
     * half years of continuous flight, so this is unreachable in practice.
     */
    if (env->counter == 0xFFFFFFFFUL) {
        return SER_EBUSY;
    }
    env->counter++;

    out[ENV_OFF_MAGIC_VER] = (uint8_t)(SER_ENV_MAGIC | SER_ENV_VERSION);
    out[ENV_OFF_FLAGS] = flags;
    put_be16(&out[ENV_OFF_NODE_ID], env->node_id);
    put_be32(&out[ENV_OFF_EPOCH], env->epoch);
    put_be32(&out[ENV_OFF_COUNTER], env->counter);
    put_be64(&out[ENV_OFF_TIMESTAMP], ser_hal_time_ns() / 1000ULL);
    memcpy(&out[ENV_OFF_KEY_ID], env->key_id, sizeof(env->key_id));

    if (len > 0U) {
        memcpy(&out[SER_ENV_HDR_LEN], payload, len);
    }

    const int rc = env_mac(env, out, payload, len, topic_id,
                           &out[SER_ENV_HDR_LEN + len]);
    if (rc != SER_OK) {
        /* Zero the buffer rather than leave a well-formed header with a
         * garbage MAC where a caller ignoring the return code could publish
         * it. */
        memset(out, 0, len + SER_ENV_TOTAL_LEN);
        *out_len = 0U;
        return rc;
    }

    *out_len = len + SER_ENV_TOTAL_LEN;
    return SER_OK;
}

int ser_env_parse_header(const uint8_t *msg,
                         size_t msg_len,
                         ser_env_hdr_t *hdr) {
    if ((msg == NULL) || (hdr == NULL)) {
        return SER_EINVAL;
    }
    if (msg_len < SER_ENV_TOTAL_LEN) {
        return SER_EPROTO;
    }
    if ((msg[ENV_OFF_MAGIC_VER] & 0xF0U) != SER_ENV_MAGIC) {
        return SER_EPROTO;
    }
    /* An unknown version means an unknown layout; verifying a MAC over the
     * wrong byte range would be worse than refusing. */
    if ((msg[ENV_OFF_MAGIC_VER] & 0x0FU) != SER_ENV_VERSION) {
        return SER_EPROTO;
    }

    hdr->version = (uint8_t)(msg[ENV_OFF_MAGIC_VER] & 0x0FU);
    hdr->flags = msg[ENV_OFF_FLAGS];
    hdr->node_id = get_be16(&msg[ENV_OFF_NODE_ID]);
    hdr->epoch = get_be32(&msg[ENV_OFF_EPOCH]);
    hdr->counter = get_be32(&msg[ENV_OFF_COUNTER]);
    hdr->timestamp_us = get_be64(&msg[ENV_OFF_TIMESTAMP]);
    memcpy(hdr->key_id, &msg[ENV_OFF_KEY_ID], sizeof(hdr->key_id));
    return SER_OK;
}

int ser_env_verify(ser_env_t *env,
                   uint16_t topic_id,
                   const uint8_t *msg,
                   size_t msg_len,
                   ser_env_hdr_t *hdr,
                   const uint8_t **body,
                   size_t *body_len) {
    if ((env == NULL) || !env->ready || (msg == NULL)) {
        return SER_EINVAL;
    }

    ser_env_hdr_t parsed;
    int rc = ser_env_parse_header(msg, msg_len, &parsed);
    if (rc != SER_OK) {
        return rc;
    }

    const size_t payload_len = msg_len - SER_ENV_TOTAL_LEN;
    const uint8_t *payload = (payload_len > 0U) ? &msg[SER_ENV_HDR_LEN] : NULL;

    uint8_t expected[SER_ENV_MAC_LEN];
    rc = env_mac(env, msg, payload, payload_len, topic_id, expected);
    if (rc != SER_OK) {
        return rc;
    }

    const bool match = ct_equal(expected,
                                &msg[SER_ENV_HDR_LEN + payload_len],
                                SER_ENV_MAC_LEN);
    memset(expected, 0, sizeof(expected));
    if (!match) {
        return SER_EPROTO;
    }

    if (hdr != NULL) {
        *hdr = parsed;
    }
    if (body != NULL) {
        *body = payload;
    }
    if (body_len != NULL) {
        *body_len = payload_len;
    }
    return SER_OK;
}
