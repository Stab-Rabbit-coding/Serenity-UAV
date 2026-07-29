/**
 * @file    tpm2.h
 * @brief   Minimal TPM 2.0 command layer for the Serenity trust-node firmware.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Marshals and unmarshals the small set of TPM 2.0 commands this firmware
 * actually issues, on top of the `tpm_tis.h` byte pipe.  It is deliberately
 * NOT a general TPM stack: there is no TSS, no ESAPI, no session encryption
 * and no policy support, because none of those are needed to sign a telemetry
 * frame and every one of them would cost flash the MSPM0G3507 does not have
 * [REF-SENSOR-004: 128 KB flash, 32 KB SRAM].
 *
 * Command and structure definitions come from the TPM 2.0 Library
 * specification [REF-TCG-001]:
 *   - Command codes ................ Part 2 §6.5.2 (TPM_CC constants)
 *   - Algorithm identifiers ........ Part 2 §6.3 (TPM_ALG_ID)
 *   - Permanent handles ............ Part 2 §7.4 (TPM_RH), §7.2 (handle types)
 *   - TPMA_OBJECT attributes ....... Part 2 §8.3
 *   - Command/response formats ..... Part 3 (per-command)
 *   - Big-endian marshalling ....... Part 1 §4.9 / [REF-TCG-002 §7.5]
 *
 * ## Signing model
 *
 * Every outbound message is authenticated with **TPM2_HMAC** over a
 * SHA-256-keyed-hash key that was created by TPM2_CreatePrimary in the owner
 * hierarchy and made persistent with TPM2_EvictControl.  The key's private
 * area never leaves the TPM, satisfying `avionics/AGENTS.md` "All keys are
 * generated and stored on the TPM, never in software".
 *
 * TPM2_Sign with an ECDSA P-256 key was considered and is **not** used for
 * per-message authentication: an SLB 9670 ECDSA signature is a multi-tens-of-
 * milliseconds operation, which does not fit a per-publication budget, while
 * an HMAC over a short buffer is a single-digit-millisecond operation.  The
 * asymmetric key still has a role — attesting the node to the ROS 2 domain at
 * join time, once per boot rather than once per message — and that is tracked
 * as its own WBS item rather than being half-built here.
 *
 * ## What this layer does not do
 *
 * There is no HMAC *session* (TPM2_StartAuthSession) protecting the command
 * channel between the MCU and the TPM.  The SPI link between them is a
 * point-to-point trace inside the board's own copper, and adding session
 * encryption would double the command round-trips.  This is a deliberate,
 * bounded acceptance: an attacker with physical probe access to that trace is
 * already inside the airframe, which is outside the threat model in
 * `avionics/AGENTS.md` "Zero Trust Architecture Compliance" (that model is
 * about the *bus* between nodes, not the traces within one node).
 */

#ifndef SERENITY_TPM2_H_
#define SERENITY_TPM2_H_

#include "serenity/tpm_tis.h"

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ---------------------------------------------------------------------------
 * Constants from the TPM 2.0 Library specification [REF-TCG-001 Part 2]
 * ---------------------------------------------------------------------------*/

/* Structure tags, Part 2 §6.9 (TPM_ST). */
#define TPM2_ST_NO_SESSIONS         (0x8001U)
#define TPM2_ST_SESSIONS            (0x8002U)

/* Command codes, Part 2 §6.5.2 (TPM_CC). */
#define TPM2_CC_EVICT_CONTROL       (0x00000120UL)
#define TPM2_CC_CREATE_PRIMARY      (0x00000131UL)
#define TPM2_CC_SELF_TEST           (0x00000143UL)
#define TPM2_CC_STARTUP             (0x00000144UL)
#define TPM2_CC_SHUTDOWN            (0x00000145UL)
#define TPM2_CC_HMAC                (0x00000155UL)
#define TPM2_CC_FLUSH_CONTEXT       (0x00000165UL)
#define TPM2_CC_READ_PUBLIC         (0x00000173UL)
#define TPM2_CC_GET_CAPABILITY      (0x0000017AUL)
#define TPM2_CC_GET_RANDOM          (0x0000017BUL)
#define TPM2_CC_PCR_READ            (0x0000017EUL)
#define TPM2_CC_PCR_EXTEND          (0x00000182UL)

/* Algorithm identifiers, Part 2 §6.3 (TPM_ALG_ID). */
#define TPM2_ALG_HMAC               (0x0005U)
#define TPM2_ALG_KEYEDHASH          (0x0008U)
#define TPM2_ALG_SHA256             (0x000BU)
#define TPM2_ALG_NULL               (0x0010U)

/* Permanent handles, Part 2 §7.4 (TPM_RH). */
#define TPM2_RH_OWNER               (0x40000001UL)
#define TPM2_RH_NULL                (0x40000007UL)
#define TPM2_RS_PW                  (0x40000009UL)   /**< Password session.   */

/* Handle ranges, Part 2 §7.2/§7.3. */
#define TPM2_PERSISTENT_FIRST       (0x81000000UL)
#define TPM2_PERSISTENT_LAST        (0x81FFFFFFUL)

/* Startup types, Part 2 §6.9 (TPM_SU). */
#define TPM2_SU_CLEAR               (0x0000U)
#define TPM2_SU_STATE               (0x0001U)

/* Object attributes, Part 2 §8.3 (TPMA_OBJECT). */
#define TPM2_OBJ_FIXEDTPM           (0x00000002UL)
#define TPM2_OBJ_FIXEDPARENT        (0x00000010UL)
#define TPM2_OBJ_SENSITIVEDATAORIGIN (0x00000020UL)
#define TPM2_OBJ_USERWITHAUTH       (0x00000040UL)
#define TPM2_OBJ_NODA               (0x00000400UL)
#define TPM2_OBJ_RESTRICTED         (0x00010000UL)
#define TPM2_OBJ_SIGN_ENCRYPT       (0x00040000UL)

/* Session attributes, Part 2 §8.4 (TPMA_SESSION). */
#define TPM2_SESSION_CONTINUE       (0x01U)

/** @brief Successful responseCode, Part 2 §6.6 (TPM_RC_SUCCESS). */
#define TPM2_RC_SUCCESS             (0x00000000UL)

/** @brief SHA-256 digest length in bytes. */
#define TPM2_SHA256_LEN             (32U)

/**
 * @brief Persistent handle the node's HMAC signing key is evicted to.
 *
 * Chosen from the persistent range reserved for owner-hierarchy application
 * objects, Part 2 §7.3.  Keeping it identical on every board in the fleet
 * means one provisioning procedure covers all of them; the *key material*
 * behind the handle is of course unique per TPM, which is exactly what makes
 * the handle a usable per-node identity.
 */
#define SER_TPM_SIGNING_KEY_HANDLE  (0x81010010UL)

/**
 * @brief PCR index this firmware extends with its own boot measurement.
 *
 * PCR 16 is the debug/application PCR in the PC Client profile
 * [REF-TCG-002 §4.3, Table 6] — resettable and not claimed by platform
 * firmware, so an application is entitled to use it.  PCRs 0–15 are reserved
 * for the platform's own measured-boot chain and this firmware does not
 * touch them.
 */
#define SER_TPM_BOOT_PCR            (16U)

/* ---------------------------------------------------------------------------
 * Context
 * ---------------------------------------------------------------------------*/

/**
 * @brief TPM 2.0 command-layer context.
 *
 * Wraps the TIS transport and carries the last responseCode so a caller that
 * gets SER_EIO can report *which* TPM error occurred in node health
 * telemetry rather than a generic failure.
 */
typedef struct {
    ser_tpm_tis_t tis;              /**< Underlying TIS transport.            */
    uint32_t      last_rc;          /**< responseCode of the last command.    */
    uint8_t       cmd[TPM_TIS_BUF_SIZE];  /**< Command marshalling buffer.    */
    uint8_t       rsp[TPM_TIS_BUF_SIZE];  /**< Response buffer.               */
    uint8_t       key_name[TPM2_SHA256_LEN + 2U]; /**< Signing key Name.      */
    size_t        key_name_len;     /**< Bytes valid in `key_name`.           */
    bool          ready;            /**< Startup + self-test completed.       */
} ser_tpm2_t;

/* ---------------------------------------------------------------------------
 * Lifecycle
 * ---------------------------------------------------------------------------*/

/**
 * @brief Reset the TPM, run TPM2_Startup(CLEAR) and TPM2_SelfTest.
 *
 * TPM2_Startup is issued unconditionally; TPM_RC_INITIALIZE (already started)
 * is treated as success, because on a warm MCU reset the TPM may not have
 * been reset with it.
 *
 * @return SER_OK, or a negative `SER_E*` code.  On a TPM-level failure the
 *         responseCode is left in `ctx->last_rc`.
 */
int ser_tpm2_open(ser_tpm2_t *ctx);

/** @brief Issue TPM2_Shutdown(CLEAR) and release the locality. */
int ser_tpm2_close(ser_tpm2_t *ctx);

/* ---------------------------------------------------------------------------
 * Provisioning — run once per board, on the bench, not in flight
 * ---------------------------------------------------------------------------*/

/**
 * @brief Create the node's HMAC signing key and make it persistent.
 *
 * TPM2_CreatePrimary in the owner hierarchy with a SHA-256 keyed-hash
 * template (sign, unrestricted, sensitiveDataOrigin, noDA), then
 * TPM2_EvictControl to @ref SER_TPM_SIGNING_KEY_HANDLE, then
 * TPM2_FlushContext on the transient handle.
 *
 * `restricted` is deliberately CLEAR: a restricted signing key may only sign
 * data the TPM itself produced [REF-TCG-001 Part 1 §11.4.6], which would make
 * it useless for authenticating an arbitrary telemetry payload.
 *
 * @return SER_OK if the key now exists at the persistent handle — including
 *         the case where it already existed (TPM_RC_NV_DEFINED is treated as
 *         success, so re-running provisioning is idempotent and does not
 *         destroy a node's established identity).
 */
int ser_tpm2_provision_signing_key(ser_tpm2_t *ctx);

/**
 * @brief Read the persistent signing key's public area and cache its Name.
 *
 * The Name (the hash of the public area, [REF-TCG-001 Part 1 §16]) is the
 * TPM's own stable identifier for that key.  It goes in the signed envelope
 * so a receiver can tell *which* node's key authenticated a message without
 * trusting a self-declared node ID.
 *
 * @return SER_OK, SER_ENODEV if no key is present at the handle, or another
 *         negative `SER_E*` code.
 */
int ser_tpm2_load_key_name(ser_tpm2_t *ctx);

/* ---------------------------------------------------------------------------
 * Operations used in flight
 * ---------------------------------------------------------------------------*/

/**
 * @brief Compute HMAC-SHA256 over @p data with the node's persistent key.
 *
 * This is the per-message signing primitive.  @p len is bounded by the TPM's
 * TPM2B_MAX_BUFFER and, more tightly, by this layer's command buffer: the
 * caller must pass a *digest* of the message, not the message itself, for
 * anything larger than a few dozen bytes.  `sec_envelope.c` does exactly
 * that — it hashes the envelope in software and has the TPM HMAC the hash.
 *
 * @param ctx   Open context with a provisioned key.
 * @param data  Bytes to authenticate.
 * @param len   Length of @p data; must leave room in the command buffer.
 * @param mac   Out: 32-byte HMAC-SHA256.
 * @return SER_OK, or a negative `SER_E*` code.
 */
int ser_tpm2_hmac(ser_tpm2_t *ctx,
                  const uint8_t *data,
                  size_t len,
                  uint8_t mac[TPM2_SHA256_LEN]);

/**
 * @brief Draw @p len bytes from the TPM's NIST SP800-90A RNG.
 *
 * Used to seed the node's replay-protection nonce at boot.  The MSPM0G3507
 * has no on-die TRNG, so the TPM is the only real entropy source on these
 * boards — a fact worth stating explicitly, because a software PRNG seeded
 * from a boot counter would make the anti-replay counter predictable.
 */
int ser_tpm2_get_random(ser_tpm2_t *ctx, uint8_t *out, size_t len);

/**
 * @brief Extend @p digest into @ref SER_TPM_BOOT_PCR.
 *
 * Called once at boot with a measurement of the running firmware image, so
 * the node's PCR state reflects what code is actually signing messages.
 */
int ser_tpm2_pcr_extend(ser_tpm2_t *ctx,
                        uint32_t pcr_index,
                        const uint8_t digest[TPM2_SHA256_LEN]);

/** @brief Read the current SHA-256 value of @p pcr_index. */
int ser_tpm2_pcr_read(ser_tpm2_t *ctx,
                      uint32_t pcr_index,
                      uint8_t digest[TPM2_SHA256_LEN]);

#ifdef __cplusplus
}
#endif

#endif /* SERENITY_TPM2_H_ */
