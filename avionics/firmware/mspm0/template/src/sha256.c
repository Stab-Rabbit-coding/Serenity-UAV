/**
 * @file    sha256.c
 * @brief   SHA-256 message digest, FIPS 180-4.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Implemented from FIPS PUB 180-4 [REF-NIST-005]:
 *   - §4.1.2  the six logical functions Ch, Maj, Sigma0/1, sigma0/1
 *   - §4.2.2  the sixty-four K constants
 *   - §5.1.1  padding
 *   - §5.3.3  the initial hash value H(0)
 *   - §6.2.2  the round function
 *
 * The K and H(0) tables below are the specification's own published constants
 * (the first thirty-two bits of the fractional parts of the cube roots and
 * square roots, respectively, of the first prime numbers), transcribed from
 * FIPS 180-4 — not copied from any implementation.
 *
 * Verified against the FIPS 180-4 example digests and the NIST CAVP short
 * message vectors by `test/test_sha256.c`.
 */

#include "serenity/sha256.h"

#include <string.h>

/** @brief Rotate a 32-bit word right by @p n bits (FIPS 180-4 §3.2). */
static uint32_t rotr32(uint32_t x, unsigned n) {
    return (x >> n) | (x << (32U - n));
}

/* FIPS 180-4 §4.1.2 logical functions. */
static uint32_t ch(uint32_t x, uint32_t y, uint32_t z) {
    return (x & y) ^ (~x & z);
}

static uint32_t maj(uint32_t x, uint32_t y, uint32_t z) {
    return (x & y) ^ (x & z) ^ (y & z);
}

static uint32_t big_sigma0(uint32_t x) {
    return rotr32(x, 2U) ^ rotr32(x, 13U) ^ rotr32(x, 22U);
}

static uint32_t big_sigma1(uint32_t x) {
    return rotr32(x, 6U) ^ rotr32(x, 11U) ^ rotr32(x, 25U);
}

static uint32_t small_sigma0(uint32_t x) {
    return rotr32(x, 7U) ^ rotr32(x, 18U) ^ (x >> 3);
}

static uint32_t small_sigma1(uint32_t x) {
    return rotr32(x, 17U) ^ rotr32(x, 19U) ^ (x >> 10);
}

/** @brief The sixty-four round constants, FIPS 180-4 §4.2.2. */
static const uint32_t K[64] = {
    0x428a2f98UL, 0x71374491UL, 0xb5c0fbcfUL, 0xe9b5dba5UL,
    0x3956c25bUL, 0x59f111f1UL, 0x923f82a4UL, 0xab1c5ed5UL,
    0xd807aa98UL, 0x12835b01UL, 0x243185beUL, 0x550c7dc3UL,
    0x72be5d74UL, 0x80deb1feUL, 0x9bdc06a7UL, 0xc19bf174UL,
    0xe49b69c1UL, 0xefbe4786UL, 0x0fc19dc6UL, 0x240ca1ccUL,
    0x2de92c6fUL, 0x4a7484aaUL, 0x5cb0a9dcUL, 0x76f988daUL,
    0x983e5152UL, 0xa831c66dUL, 0xb00327c8UL, 0xbf597fc7UL,
    0xc6e00bf3UL, 0xd5a79147UL, 0x06ca6351UL, 0x14292967UL,
    0x27b70a85UL, 0x2e1b2138UL, 0x4d2c6dfcUL, 0x53380d13UL,
    0x650a7354UL, 0x766a0abbUL, 0x81c2c92eUL, 0x92722c85UL,
    0xa2bfe8a1UL, 0xa81a664bUL, 0xc24b8b70UL, 0xc76c51a3UL,
    0xd192e819UL, 0xd6990624UL, 0xf40e3585UL, 0x106aa070UL,
    0x19a4c116UL, 0x1e376c08UL, 0x2748774cUL, 0x34b0bcb5UL,
    0x391c0cb3UL, 0x4ed8aa4aUL, 0x5b9cca4fUL, 0x682e6ff3UL,
    0x748f82eeUL, 0x78a5636fUL, 0x84c87814UL, 0x8cc70208UL,
    0x90befffaUL, 0xa4506cebUL, 0xbef9a3f7UL, 0xc67178f2UL
};

/**
 * @brief Process one 512-bit block, FIPS 180-4 §6.2.2.
 *
 * The message schedule W is computed on the fly in a rolling 16-word window
 * rather than as a full 64-word array — the two are algebraically identical,
 * and the window saves 192 bytes of stack on a part with 32 KB of SRAM.
 */
static void sha256_block(ser_sha256_t *ctx, const uint8_t *block) {
    uint32_t w[16];
    uint32_t a, b, c, d, e, f, g, h;

    for (unsigned i = 0U; i < 16U; ++i) {
        w[i] = ((uint32_t)block[(i * 4U) + 0U] << 24)
               | ((uint32_t)block[(i * 4U) + 1U] << 16)
               | ((uint32_t)block[(i * 4U) + 2U] << 8)
               | (uint32_t)block[(i * 4U) + 3U];
    }

    a = ctx->state[0];
    b = ctx->state[1];
    c = ctx->state[2];
    d = ctx->state[3];
    e = ctx->state[4];
    f = ctx->state[5];
    g = ctx->state[6];
    h = ctx->state[7];

    for (unsigned t = 0U; t < 64U; ++t) {
        if (t >= 16U) {
            /* W[t] = sigma1(W[t-2]) + W[t-7] + sigma0(W[t-15]) + W[t-16],
             * with the window indexed modulo 16. */
            w[t & 15U] = small_sigma1(w[(t + 14U) & 15U])
                         + w[(t + 9U) & 15U]
                         + small_sigma0(w[(t + 1U) & 15U])
                         + w[t & 15U];
        }

        const uint32_t t1 = h + big_sigma1(e) + ch(e, f, g) + K[t]
                            + w[t & 15U];
        const uint32_t t2 = big_sigma0(a) + maj(a, b, c);

        h = g;
        g = f;
        f = e;
        e = d + t1;
        d = c;
        c = b;
        b = a;
        a = t1 + t2;
    }

    ctx->state[0] += a;
    ctx->state[1] += b;
    ctx->state[2] += c;
    ctx->state[3] += d;
    ctx->state[4] += e;
    ctx->state[5] += f;
    ctx->state[6] += g;
    ctx->state[7] += h;
}

void ser_sha256_init(ser_sha256_t *ctx) {
    /* Initial hash value H(0), FIPS 180-4 §5.3.3. */
    ctx->state[0] = 0x6a09e667UL;
    ctx->state[1] = 0xbb67ae85UL;
    ctx->state[2] = 0x3c6ef372UL;
    ctx->state[3] = 0xa54ff53aUL;
    ctx->state[4] = 0x510e527fUL;
    ctx->state[5] = 0x9b05688cUL;
    ctx->state[6] = 0x1f83d9abUL;
    ctx->state[7] = 0x5be0cd19UL;
    ctx->bit_count = 0U;
    ctx->block_len = 0U;
    memset(ctx->block, 0, sizeof(ctx->block));
}

void ser_sha256_update(ser_sha256_t *ctx, const uint8_t *data, size_t len) {
    if ((ctx == NULL) || ((data == NULL) && (len > 0U))) {
        return;
    }

    ctx->bit_count += (uint64_t)len * 8U;

    size_t off = 0U;

    /* Top up a partially filled block first. */
    if (ctx->block_len > 0U) {
        size_t need = SER_SHA256_BLOCK_LEN - ctx->block_len;
        if (need > len) {
            need = len;
        }
        memcpy(&ctx->block[ctx->block_len], data, need);
        ctx->block_len += need;
        off += need;
        if (ctx->block_len == SER_SHA256_BLOCK_LEN) {
            sha256_block(ctx, ctx->block);
            ctx->block_len = 0U;
        }
    }

    /* Then consume whole blocks straight from the caller's buffer. */
    while ((len - off) >= SER_SHA256_BLOCK_LEN) {
        sha256_block(ctx, &data[off]);
        off += SER_SHA256_BLOCK_LEN;
    }

    /* Whatever is left is a new partial block. */
    if (off < len) {
        const size_t rem = len - off;
        memcpy(ctx->block, &data[off], rem);
        ctx->block_len = rem;
    }
}

void ser_sha256_final(ser_sha256_t *ctx,
                      uint8_t digest[SER_SHA256_DIGEST_LEN]) {
    if ((ctx == NULL) || (digest == NULL)) {
        return;
    }

    const uint64_t bits = ctx->bit_count;

    /*
     * Padding, FIPS 180-4 §5.1.1: append 0x80, then the fewest zero bytes
     * that leave room for a 64-bit big-endian length in the final block.
     */
    ctx->block[ctx->block_len++] = 0x80U;
    if (ctx->block_len > (SER_SHA256_BLOCK_LEN - 8U)) {
        memset(&ctx->block[ctx->block_len], 0,
               SER_SHA256_BLOCK_LEN - ctx->block_len);
        sha256_block(ctx, ctx->block);
        ctx->block_len = 0U;
    }
    memset(&ctx->block[ctx->block_len], 0,
           (SER_SHA256_BLOCK_LEN - 8U) - ctx->block_len);

    for (unsigned i = 0U; i < 8U; ++i) {
        ctx->block[(SER_SHA256_BLOCK_LEN - 1U) - i] =
            (uint8_t)((bits >> (8U * i)) & 0xFFU);
    }
    sha256_block(ctx, ctx->block);

    for (unsigned i = 0U; i < 8U; ++i) {
        digest[(i * 4U) + 0U] = (uint8_t)((ctx->state[i] >> 24) & 0xFFU);
        digest[(i * 4U) + 1U] = (uint8_t)((ctx->state[i] >> 16) & 0xFFU);
        digest[(i * 4U) + 2U] = (uint8_t)((ctx->state[i] >> 8) & 0xFFU);
        digest[(i * 4U) + 3U] = (uint8_t)(ctx->state[i] & 0xFFU);
    }

    /* Leave no working state behind — the block buffer held message bytes. */
    memset(ctx, 0, sizeof(*ctx));
}

void ser_sha256(const uint8_t *data,
                size_t len,
                uint8_t digest[SER_SHA256_DIGEST_LEN]) {
    ser_sha256_t ctx;
    ser_sha256_init(&ctx);
    ser_sha256_update(&ctx, data, len);
    ser_sha256_final(&ctx, digest);
}
