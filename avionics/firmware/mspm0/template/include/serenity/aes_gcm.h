/**
 * @file    aes_gcm.h
 * @brief   AES-GCM authenticated encryption — portable reference implementation.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-29
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * The MSPM0G3507 has a hardware AES-128/256 engine [REF-SENSOR-004 §8.20], and
 * the flight path uses it through `ser_hal_aes_gcm_*()`.  This file is the
 * portable fallback behind that interface, and serves three purposes:
 *
 *   1. It makes the host (`sim`) build a real, testable cipher rather than a
 *      stub, so the envelope and node logic can be exercised end to end on a
 *      workstation.
 *   2. It is the known-good reference the hardware path is checked against —
 *      `test/test_crypto.c` runs both through the same NIST CAVP vectors.
 *   3. The MSPM0's engine accelerates the AES block function but not GHASH,
 *      so the hardware port reuses the GF(2^128) multiply here regardless.
 *
 * Implemented from:
 *   FIPS PUB 197 (AES)                       [REF-NIST-007]
 *   NIST SP 800-38D (GCM and GMAC)           [REF-NIST-008]
 *
 * Verified against the NIST CAVP `gcmEncryptExtIV256` response file.
 *
 * @warning GCM security collapses if an (key, IV) pair is ever reused.  The
 *          IV construction that guarantees uniqueness for this firmware is
 *          documented in `sec_envelope.h`; do not call this directly from
 *          application code.
 */

#ifndef SERENITY_AES_GCM_H_
#define SERENITY_AES_GCM_H_

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/** @brief GCM authentication tag length, bytes (SP 800-38D §5.2.1.2). */
#define SER_GCM_TAG_LEN     (16U)

/** @brief IV length this firmware uses; the value SP 800-38D §8.2 recommends. */
#define SER_GCM_IV_LEN      (12U)

/** @brief Expanded AES key schedule; AES-256 is 15 round keys of 16 bytes. */
typedef struct {
    uint32_t rk[60];        /**< Round keys, big-endian words.                */
    uint8_t  rounds;        /**< 10 for AES-128, 14 for AES-256.              */
    uint8_t  h[16];         /**< GHASH subkey H = AES_K(0^128).               */
} ser_aes_gcm_t;

/**
 * @brief Expand @p key and derive the GHASH subkey.
 *
 * @param key_len 16 (AES-128) or 32 (AES-256).  AES-192 is not supported:
 *                nothing in this fleet uses it and the extra key schedule
 *                case is dead flash on a 128 KB part.
 */
int ser_aes_gcm_init(ser_aes_gcm_t *ctx, const uint8_t *key, size_t key_len);

/**
 * @brief Encrypt and authenticate.
 *
 * @param iv      12-byte IV.  Must never repeat under one key.
 * @param aad     Additional authenticated data — authenticated, not encrypted.
 * @param pt      Plaintext; may alias @p ct for in-place operation.
 * @param ct      Ciphertext out, @p pt_len bytes.
 * @param tag     Out: 16-byte authentication tag.
 */
int ser_aes_gcm_encrypt(ser_aes_gcm_t *ctx,
                        const uint8_t iv[SER_GCM_IV_LEN],
                        const uint8_t *aad, size_t aad_len,
                        const uint8_t *pt, size_t pt_len,
                        uint8_t *ct,
                        uint8_t tag[SER_GCM_TAG_LEN]);

/**
 * @brief Verify and decrypt.
 *
 * The tag is checked in constant time and the plaintext is zeroed on failure,
 * so a caller that ignores the return value cannot act on unauthenticated
 * data.
 *
 * @return SER_OK, or SER_EPROTO if the tag does not verify.
 */
int ser_aes_gcm_decrypt(ser_aes_gcm_t *ctx,
                        const uint8_t iv[SER_GCM_IV_LEN],
                        const uint8_t *aad, size_t aad_len,
                        const uint8_t *ct, size_t ct_len,
                        const uint8_t tag[SER_GCM_TAG_LEN],
                        uint8_t *pt);

#ifdef __cplusplus
}
#endif

#endif /* SERENITY_AES_GCM_H_ */
