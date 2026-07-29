/**
 * @file    sec_envelope.h
 * @brief   TPM-anchored message envelope carried inside every DDS sample.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * ## Why this exists alongside DDS-Security
 *
 * The PocketBeagle nodes are full Fast DDS peers with OMG DDS-Security
 * [REF-OMG-002] fully enabled, so every RTPS hop between them is
 * authenticated and AES-GCM protected by the builtin plugins.  The
 * MSPM0G3507 trust modules cannot be RTPS peers — the part has no Ethernet
 * MAC and 128 KB of flash [REF-SENSOR-004], against a measured 54.9 KB just
 * for the DDS-Security crypto dependency on this core — so they join the
 * domain as Micro XRCE-DDS clients behind an Agent co-located with a
 * PocketBeagle peer.
 *
 * That would normally make the Agent a trust anchor: whatever it publishes,
 * DDS-Security signs with the *Beagle's* identity, and a subscriber could not
 * tell an MSPM0 measurement from an Agent fabrication.  Each node carries its
 * own TPM precisely so that it owns its own identity, so this envelope closes
 * that gap: it is generated inside the MSPM0, keyed to that MCU's own SLB9670,
 * and travels inside the DDS sample payload.  DDS-Security protects the
 * hop; the envelope proves the origin.  The Agent relays and cannot forge.
 *
 *     MSPM0 ─XRCE/CAN─► Agent ─RTPS + DDS-Security─► ROS 2 subscriber
 *       │                                                    │
 *       └────────── envelope MAC, TPM-keyed ─────────────────┘
 *
 * ## Wire format (little on the wire by design)
 *
 *   off  size  field
 *   ---  ----  ----------------------------------------------------------
 *     0     1  magic/version: 0x50 | version    (version 0..15)
 *     1     1  flags
 *     2     2  node_id            (big-endian)
 *     4     4  epoch              TPM-random, redrawn each boot
 *     8     4  counter            increments per signed message
 *    12     8  timestamp_us       sender monotonic microseconds
 *    20     4  key_id             leading 4 bytes of the TPM key Name
 *    24     n  payload
 *  24+n    16  MAC                leftmost bytes of HMAC-SHA256
 *
 * `topic_id` is deliberately **not transmitted**.  It is mixed into the MAC
 * input, so a receiver that knows which topic it subscribed to gets binding
 * against cross-topic substitution for free, without spending wire bytes on a
 * value the DataWriter already implies.
 *
 * Total overhead is @ref SER_ENV_TOTAL_LEN = 40 bytes.  On the 63-byte
 * CAN-FD transport MTU that is real cost, and it is the reason fast inner
 * loops stay local to the MCU and only their telemetry is published — see
 * `README.md` "Publication rate budget".
 *
 * ## Truncated MAC
 *
 * The TPM returns a full 32-byte HMAC-SHA256; the envelope carries the
 * leftmost @ref SER_ENV_MAC_LEN.  NIST SP 800-107 Rev 1 §5.3.3
 * [REF-NIST-006]: "the λ left-most bits of the HMAC output shall be used as
 * the MacTag ... λ shall be no less than 32 bits".  The default λ = 128 bits
 * is four times that floor.
 *
 * ## Replay protection
 *
 * `epoch` is drawn from the TPM RNG at each boot; `counter` increments per
 * signed message.  A receiver accepts only a strictly increasing counter
 * within a known epoch, or any counter in a newly-seen epoch.  The epoch is
 * what lets a node reboot without every subsequent message looking like a
 * replay of one already seen.
 */

#ifndef SERENITY_SEC_ENVELOPE_H_
#define SERENITY_SEC_ENVELOPE_H_

#include "serenity/tpm2.h"

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/** @brief High nibble of byte 0; identifies an envelope. */
#define SER_ENV_MAGIC       (0x50U)

/** @brief Wire-format version, low nibble of byte 0.  Bump on any change. */
#define SER_ENV_VERSION     (1U)

/** @brief Serialised header length in bytes, excluding the MAC. */
#define SER_ENV_HDR_LEN     (24U)

/**
 * @brief Truncated MAC length in bytes.  Range 4..32 [REF-NIST-006 §5.3.3].
 *
 * Do not reduce without recording the analysis in the subsystem README.
 */
#define SER_ENV_MAC_LEN     (16U)

/** @brief Total envelope overhead prepended to and appended to a payload. */
#define SER_ENV_TOTAL_LEN   (SER_ENV_HDR_LEN + SER_ENV_MAC_LEN)

/** @brief Envelope flag bits. */
#define SER_ENV_FLAG_NONE       (0x00U)
#define SER_ENV_FLAG_SAFETY     (0x01U) /**< Safety-relevant; log verbatim.   */
#define SER_ENV_FLAG_FAULT      (0x02U) /**< Reports a latched fault.         */
#define SER_ENV_FLAG_DEGRADED   (0x04U) /**< Sender is running degraded.      */
#define SER_ENV_FLAG_ENCRYPTED  (0x08U) /**< Payload is AES-GCM ciphertext.   */

/** @brief Signing context.  One per node. */
typedef struct {
    ser_tpm2_t *tpm;        /**< Open TPM context; not owned.                 */
    uint16_t    node_id;    /**< This node's fleet identifier.                */
    uint32_t    epoch;      /**< TPM-random, redrawn every boot.              */
    uint32_t    counter;    /**< Increments per signed message.               */
    uint8_t     key_id[4];  /**< Leading 4 bytes of the TPM key Name.         */
    bool        ready;
} ser_env_t;

/** @brief Parsed header, host byte order. */
typedef struct {
    uint8_t  version;
    uint8_t  flags;
    uint16_t node_id;
    uint32_t epoch;
    uint32_t counter;
    uint64_t timestamp_us;
    uint8_t  key_id[4];
} ser_env_hdr_t;

/**
 * @brief Bind a signing context to an open, provisioned TPM.
 *
 * Draws the boot epoch from the TPM RNG and caches the key identifier from
 * the key Name.  The MSPM0G3507 does have its own TRNG, but the epoch comes
 * from the TPM so that the value is bound to the same root of trust that
 * signs with it.
 *
 * @return SER_OK, SER_ENODEV if no signing key is provisioned, else `SER_E*`.
 */
int ser_env_init(ser_env_t *env, ser_tpm2_t *tpm, uint16_t node_id);

/**
 * @brief Wrap @p payload in a signed envelope.
 *
 * Layout: `[24-byte header][payload][16-byte MAC]`.  The MAC covers the
 * header, the payload, and @p topic_id (which is not transmitted).
 *
 * @param out_cap Must be at least @p len + @ref SER_ENV_TOTAL_LEN.
 * @return SER_OK, else `SER_E*`.  A TPM failure is reported, never silently
 *         downgraded to an unsigned message.
 */
int ser_env_seal(ser_env_t *env,
                 uint16_t topic_id,
                 uint8_t flags,
                 const uint8_t *payload,
                 size_t len,
                 uint8_t *out,
                 size_t out_cap,
                 size_t *out_len);

/**
 * @brief Verify a sealed message against the local TPM key.
 *
 * Cross-node verification happens on the PocketBeagle side, where the
 * registry of peer TPM key Names lives.  On the MCU this is the loopback
 * self-test that proves the signing path works before the node is permitted
 * to join the bus.
 */
int ser_env_verify(ser_env_t *env,
                   uint16_t topic_id,
                   const uint8_t *msg,
                   size_t msg_len,
                   ser_env_hdr_t *hdr,
                   const uint8_t **body,
                   size_t *body_len);

/**
 * @brief Parse a header without verifying the MAC — logging and triage only.
 *
 * Never gate an action on the result; an unverified header is
 * attacker-controlled data.
 */
int ser_env_parse_header(const uint8_t *msg,
                         size_t msg_len,
                         ser_env_hdr_t *hdr);

#ifdef __cplusplus
}
#endif

#endif /* SERENITY_SEC_ENVELOPE_H_ */
