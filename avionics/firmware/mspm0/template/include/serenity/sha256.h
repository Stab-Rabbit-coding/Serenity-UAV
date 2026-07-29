/**
 * @file    sha256.h
 * @brief   SHA-256 message digest, FIPS 180-4.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Why a software hash on a board that has a TPM: the TPM signs, but the
 * message being signed has to be reduced to something small enough to hand
 * over SPI in one command.  Hashing the envelope in software and having the
 * TPM HMAC the 32-byte hash keeps the TPM round-trip constant-cost regardless
 * of payload size.  The security property is unchanged — the key stays inside
 * the TPM — because HMAC-SHA256(k, SHA256(m)) binds the whole message.
 *
 * The MSPM0G3507 has no hardware SHA accelerator [REF-SENSOR-004], so this is
 * a plain C implementation, written directly from the algorithm specification
 * in FIPS PUB 180-4 §6.2 [REF-NIST-005].  Constants are the specification's
 * own published values (§4.2.2 K, §5.3.3 H(0)).
 */

#ifndef SERENITY_SHA256_H_
#define SERENITY_SHA256_H_

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/** @brief SHA-256 digest length in bytes (FIPS 180-4 §1). */
#define SER_SHA256_DIGEST_LEN   (32U)

/** @brief SHA-256 block length in bytes (FIPS 180-4 §5.1.1: 512 bits). */
#define SER_SHA256_BLOCK_LEN    (64U)

/** @brief Streaming SHA-256 state. */
typedef struct {
    uint32_t state[8];                      /**< Working variables H0..H7.    */
    uint64_t bit_count;                     /**< Total message length, bits.  */
    uint8_t  block[SER_SHA256_BLOCK_LEN];   /**< Partial block buffer.        */
    size_t   block_len;                     /**< Bytes buffered in `block`.   */
} ser_sha256_t;

/** @brief Initialise to the FIPS 180-4 §5.3.3 initial hash value. */
void ser_sha256_init(ser_sha256_t *ctx);

/** @brief Absorb @p len bytes. */
void ser_sha256_update(ser_sha256_t *ctx, const uint8_t *data, size_t len);

/**
 * @brief Pad, absorb the length, and emit the digest.
 *
 * @param ctx     Context; unusable afterwards without a fresh init.
 * @param digest  Out: 32-byte digest, big-endian per FIPS 180-4 §6.2.2.
 */
void ser_sha256_final(ser_sha256_t *ctx, uint8_t digest[SER_SHA256_DIGEST_LEN]);

/** @brief One-shot convenience wrapper over init/update/final. */
void ser_sha256(const uint8_t *data,
                size_t len,
                uint8_t digest[SER_SHA256_DIGEST_LEN]);

#ifdef __cplusplus
}
#endif

#endif /* SERENITY_SHA256_H_ */
