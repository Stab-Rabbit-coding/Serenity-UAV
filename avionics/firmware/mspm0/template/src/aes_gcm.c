/**
 * @file    aes_gcm.c
 * @brief   AES-GCM authenticated encryption — portable reference implementation.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-29
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Implemented from FIPS PUB 197 [REF-NIST-007] and NIST SP 800-38D
 * [REF-NIST-008].  The S-box and round constants are the specification's own
 * published tables (FIPS 197 §5.1.1 Figure 7, §5.2).
 *
 * Written from the specifications; no code taken from any implementation.
 *
 * Implementation choices, both driven by the 128 KB flash budget:
 *   - No T-tables.  The classic 4 × 1 KB T-table AES is faster but costs 4 KB
 *     of flash and leaks through cache timing on parts that have a cache.
 *     Plain SubBytes/MixColumns costs ~1 KB and the MSPM0's hardware engine
 *     handles the flight path anyway.
 *   - GHASH is the bitwise "shift and xor" form of SP 800-38D §6.3 rather
 *     than a 4-bit or 8-bit table method, saving a 4 KB table.  It is slower
 *     per byte, which is acceptable because the samples are tens of bytes.
 */

#include "serenity/aes_gcm.h"

#include "serenity/hal.h"

#include <string.h>

/** @brief AES S-box, FIPS 197 §5.1.1 Figure 7. */
static const uint8_t SBOX[256] = {
    0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
    0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
    0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
    0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
    0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
    0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
    0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
    0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
    0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
    0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
    0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
    0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
    0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
    0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
    0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
    0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16
};

/** @brief Round constants, FIPS 197 §5.2. */
static const uint8_t RCON[11] = {
    0x00,0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1b,0x36
};

/** @brief Multiply by x in GF(2^8) with the AES polynomial, FIPS 197 §4.2. */
static uint8_t xtime(uint8_t a) {
    return (uint8_t)((uint8_t)(a << 1) ^ (uint8_t)(((a >> 7) & 1U) * 0x1BU));
}

static uint32_t sub_word(uint32_t w) {
    return ((uint32_t)SBOX[(w >> 24) & 0xFFU] << 24)
           | ((uint32_t)SBOX[(w >> 16) & 0xFFU] << 16)
           | ((uint32_t)SBOX[(w >> 8) & 0xFFU] << 8)
           | (uint32_t)SBOX[w & 0xFFU];
}

static uint32_t rot_word(uint32_t w) {
    return (w << 8) | (w >> 24);
}

/** @brief Encrypt one 16-byte block in place (FIPS 197 §5.1 Cipher). */
static void aes_encrypt_block(const ser_aes_gcm_t *ctx,
                              const uint8_t in[16],
                              uint8_t out[16]) {
    uint8_t s[16];
    memcpy(s, in, 16);

    /* AddRoundKey, round 0. */
    for (unsigned c = 0U; c < 4U; ++c) {
        const uint32_t k = ctx->rk[c];
        s[(c * 4U) + 0U] ^= (uint8_t)(k >> 24);
        s[(c * 4U) + 1U] ^= (uint8_t)(k >> 16);
        s[(c * 4U) + 2U] ^= (uint8_t)(k >> 8);
        s[(c * 4U) + 3U] ^= (uint8_t)k;
    }

    for (unsigned round = 1U; round <= ctx->rounds; ++round) {
        /* SubBytes. */
        for (unsigned i = 0U; i < 16U; ++i) {
            s[i] = SBOX[s[i]];
        }

        /* ShiftRows — the state is column-major, so element (r, c) is s[4c+r]. */
        uint8_t t;
        t = s[1];  s[1] = s[5];  s[5] = s[9];  s[9]  = s[13]; s[13] = t;
        t = s[2];  s[2] = s[10]; s[10] = t;
        t = s[6];  s[6] = s[14]; s[14] = t;
        t = s[15]; s[15] = s[11]; s[11] = s[7]; s[7] = s[3];  s[3]  = t;

        /* MixColumns — omitted in the final round, FIPS 197 §5.1. */
        if (round != ctx->rounds) {
            for (unsigned c = 0U; c < 4U; ++c) {
                uint8_t *p = &s[c * 4U];
                const uint8_t a0 = p[0], a1 = p[1], a2 = p[2], a3 = p[3];
                const uint8_t all = (uint8_t)(a0 ^ a1 ^ a2 ^ a3);
                p[0] ^= (uint8_t)(all ^ xtime((uint8_t)(a0 ^ a1)));
                p[1] ^= (uint8_t)(all ^ xtime((uint8_t)(a1 ^ a2)));
                p[2] ^= (uint8_t)(all ^ xtime((uint8_t)(a2 ^ a3)));
                p[3] ^= (uint8_t)(all ^ xtime((uint8_t)(a3 ^ a0)));
            }
        }

        /* AddRoundKey. */
        for (unsigned c = 0U; c < 4U; ++c) {
            const uint32_t k = ctx->rk[(round * 4U) + c];
            s[(c * 4U) + 0U] ^= (uint8_t)(k >> 24);
            s[(c * 4U) + 1U] ^= (uint8_t)(k >> 16);
            s[(c * 4U) + 2U] ^= (uint8_t)(k >> 8);
            s[(c * 4U) + 3U] ^= (uint8_t)k;
        }
    }

    memcpy(out, s, 16);
}

int ser_aes_gcm_init(ser_aes_gcm_t *ctx, const uint8_t *key, size_t key_len) {
    if ((ctx == NULL) || (key == NULL)) {
        return SER_EINVAL;
    }
    if ((key_len != 16U) && (key_len != 32U)) {
        return SER_EINVAL;
    }

    memset(ctx, 0, sizeof(*ctx));
    const unsigned nk = (unsigned)(key_len / 4U);   /* 4 or 8 words. */
    ctx->rounds = (uint8_t)(nk + 6U);               /* 10 or 14.     */

    /* KeyExpansion, FIPS 197 §5.2. */
    for (unsigned i = 0U; i < nk; ++i) {
        ctx->rk[i] = ((uint32_t)key[4U * i] << 24)
                     | ((uint32_t)key[(4U * i) + 1U] << 16)
                     | ((uint32_t)key[(4U * i) + 2U] << 8)
                     | (uint32_t)key[(4U * i) + 3U];
    }
    const unsigned total = 4U * ((unsigned)ctx->rounds + 1U);
    for (unsigned i = nk; i < total; ++i) {
        uint32_t temp = ctx->rk[i - 1U];
        if ((i % nk) == 0U) {
            temp = sub_word(rot_word(temp))
                   ^ ((uint32_t)RCON[i / nk] << 24);
        } else if ((nk > 6U) && ((i % nk) == 4U)) {
            /* The extra SubWord applies only to AES-256, FIPS 197 §5.2. */
            temp = sub_word(temp);
        } else {
            /* No transformation. */
        }
        ctx->rk[i] = ctx->rk[i - nk] ^ temp;
    }

    /* GHASH subkey H = CIPH_K(0^128), SP 800-38D §6.3. */
    uint8_t zero[16] = {0};
    aes_encrypt_block(ctx, zero, ctx->h);
    return SER_OK;
}

/**
 * @brief GF(2^128) multiply, SP 800-38D §6.3 Algorithm 1.
 *
 * The field uses the "reflected" bit ordering of the GCM specification: bit 0
 * of byte 0 is the most significant coefficient, and the reduction polynomial
 * appears as 0xE1 applied to the leading byte.  Getting that convention
 * backwards produces a cipher that is self-consistent but interoperates with
 * nothing, which is why this is validated against the CAVP vectors rather
 * than against itself.
 */
static void gf_mult(const uint8_t x[16], const uint8_t y[16], uint8_t out[16]) {
    uint8_t z[16] = {0};
    uint8_t v[16];
    memcpy(v, y, 16);

    for (unsigned i = 0U; i < 128U; ++i) {
        const uint8_t bit = (uint8_t)((x[i / 8U] >> (7U - (i % 8U))) & 1U);
        if (bit != 0U) {
            for (unsigned j = 0U; j < 16U; ++j) {
                z[j] ^= v[j];
            }
        }
        /* v = v >> 1, with reduction by R = 0xE1000...0 when bit 127 was set. */
        const uint8_t lsb = (uint8_t)(v[15] & 1U);
        for (unsigned j = 15U; j > 0U; --j) {
            v[j] = (uint8_t)((v[j] >> 1) | (uint8_t)(v[j - 1U] << 7));
        }
        v[0] >>= 1;
        if (lsb != 0U) {
            v[0] ^= 0xE1U;
        }
    }
    memcpy(out, z, 16);
}

/** @brief GHASH accumulate: Y = (Y ^ block) * H. */
static void ghash_update(const ser_aes_gcm_t *ctx,
                         uint8_t y[16],
                         const uint8_t *data,
                         size_t len) {
    size_t off = 0U;
    while (off < len) {
        uint8_t block[16] = {0};
        const size_t n = ((len - off) >= 16U) ? 16U : (len - off);
        memcpy(block, &data[off], n);
        for (unsigned i = 0U; i < 16U; ++i) {
            y[i] ^= block[i];
        }
        gf_mult(y, ctx->h, y);
        off += n;
    }
}

/** @brief Increment the rightmost 32 bits of a counter block (SP 800-38D §6.2). */
static void inc32(uint8_t ctr[16]) {
    for (unsigned i = 16U; i > 12U; --i) {
        if (++ctr[i - 1U] != 0U) {
            break;
        }
    }
}

/**
 * @brief The GCTR keystream pass shared by encrypt and decrypt.
 *
 * GCM is a stream construction, so encryption and decryption are the same
 * operation; only the order of the GHASH and XOR steps differs between them.
 */
static void gctr(const ser_aes_gcm_t *ctx,
                 uint8_t ctr[16],
                 const uint8_t *in,
                 size_t len,
                 uint8_t *out) {
    uint8_t ks[16];
    size_t off = 0U;
    while (off < len) {
        inc32(ctr);
        aes_encrypt_block(ctx, ctr, ks);
        const size_t n = ((len - off) >= 16U) ? 16U : (len - off);
        for (size_t i = 0U; i < n; ++i) {
            out[off + i] = (uint8_t)(in[off + i] ^ ks[i]);
        }
        off += n;
    }
    memset(ks, 0, sizeof(ks));
}

/**
 * @brief Compute the tag: GHASH over AAD ‖ C ‖ len(A) ‖ len(C), then XOR
 *        with the round-0 counter block (SP 800-38D §7.1 step 6).
 */
static void gcm_tag(const ser_aes_gcm_t *ctx,
                    const uint8_t j0[16],
                    const uint8_t *aad, size_t aad_len,
                    const uint8_t *ct, size_t ct_len,
                    uint8_t tag[SER_GCM_TAG_LEN]) {
    uint8_t y[16] = {0};
    ghash_update(ctx, y, aad, aad_len);
    ghash_update(ctx, y, ct, ct_len);

    /* The length block is two 64-bit big-endian bit counts. */
    uint8_t lenblk[16] = {0};
    const uint64_t abits = (uint64_t)aad_len * 8U;
    const uint64_t cbits = (uint64_t)ct_len * 8U;
    for (unsigned i = 0U; i < 8U; ++i) {
        lenblk[7U - i] = (uint8_t)(abits >> (8U * i));
        lenblk[15U - i] = (uint8_t)(cbits >> (8U * i));
    }
    ghash_update(ctx, y, lenblk, sizeof(lenblk));

    uint8_t s[16];
    aes_encrypt_block(ctx, j0, s);
    for (unsigned i = 0U; i < SER_GCM_TAG_LEN; ++i) {
        tag[i] = (uint8_t)(y[i] ^ s[i]);
    }
    memset(y, 0, sizeof(y));
    memset(s, 0, sizeof(s));
}

/**
 * @brief Build J0 for a 96-bit IV: IV ‖ 0^31 ‖ 1 (SP 800-38D §7.1 step 2).
 *
 * Only the 96-bit case is implemented.  SP 800-38D §8.2 recommends exactly
 * this length, every IV this firmware builds is 96 bits, and the general case
 * would add a GHASH pass of dead code.
 */
static void build_j0(const uint8_t iv[SER_GCM_IV_LEN], uint8_t j0[16]) {
    memcpy(j0, iv, SER_GCM_IV_LEN);
    j0[12] = 0U;
    j0[13] = 0U;
    j0[14] = 0U;
    j0[15] = 1U;
}

int ser_aes_gcm_encrypt(ser_aes_gcm_t *ctx,
                        const uint8_t iv[SER_GCM_IV_LEN],
                        const uint8_t *aad, size_t aad_len,
                        const uint8_t *pt, size_t pt_len,
                        uint8_t *ct,
                        uint8_t tag[SER_GCM_TAG_LEN]) {
    if ((ctx == NULL) || (iv == NULL) || (tag == NULL) ||
        ((pt_len > 0U) && ((pt == NULL) || (ct == NULL))) ||
        ((aad_len > 0U) && (aad == NULL))) {
        return SER_EINVAL;
    }

    uint8_t j0[16];
    uint8_t ctr[16];
    build_j0(iv, j0);
    memcpy(ctr, j0, sizeof(ctr));

    gctr(ctx, ctr, pt, pt_len, ct);
    gcm_tag(ctx, j0, aad, aad_len, ct, pt_len, tag);

    memset(ctr, 0, sizeof(ctr));
    return SER_OK;
}

/** @brief Constant-time comparison; see the note in `sec_envelope.c`. */
static bool ct_equal(const uint8_t *a, const uint8_t *b, size_t len) {
    uint8_t diff = 0U;
    for (size_t i = 0U; i < len; ++i) {
        diff |= (uint8_t)(a[i] ^ b[i]);
    }
    return diff == 0U;
}

int ser_aes_gcm_decrypt(ser_aes_gcm_t *ctx,
                        const uint8_t iv[SER_GCM_IV_LEN],
                        const uint8_t *aad, size_t aad_len,
                        const uint8_t *ct, size_t ct_len,
                        const uint8_t tag[SER_GCM_TAG_LEN],
                        uint8_t *pt) {
    if ((ctx == NULL) || (iv == NULL) || (tag == NULL) ||
        ((ct_len > 0U) && ((ct == NULL) || (pt == NULL))) ||
        ((aad_len > 0U) && (aad == NULL))) {
        return SER_EINVAL;
    }

    uint8_t j0[16];
    uint8_t ctr[16];
    uint8_t expected[SER_GCM_TAG_LEN];
    build_j0(iv, j0);

    /*
     * Tag first, over the ciphertext, before any plaintext is produced.
     * SP 800-38D §7.2 step 5 is explicit that the plaintext must not be
     * released if verification fails.
     */
    gcm_tag(ctx, j0, aad, aad_len, ct, ct_len, expected);
    const bool ok = ct_equal(expected, tag, SER_GCM_TAG_LEN);
    memset(expected, 0, sizeof(expected));
    if (!ok) {
        if ((pt != NULL) && (ct_len > 0U)) {
            memset(pt, 0, ct_len);
        }
        return SER_EPROTO;
    }

    memcpy(ctr, j0, sizeof(ctr));
    gctr(ctx, ctr, ct, ct_len, pt);
    memset(ctr, 0, sizeof(ctr));
    return SER_OK;
}
