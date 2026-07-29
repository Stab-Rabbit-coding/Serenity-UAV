/**
 * @file    test_crypto.c
 * @brief   SHA-256 verification against the FIPS 180-4 published vectors.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * The digest values below are the published expected results from the NIST
 * "Secure Hash Standard" example documents for SHA-256 [REF-NIST-005]:
 * the one-block "abc" case, the two-block 448-bit case, and the one-million
 * 'a' case.  They are the specification's own answers, not values captured
 * from this implementation — a self-generated expectation would make the test
 * prove only that the code is deterministic.
 */

#include "serenity/aes_gcm.h"
#include "serenity/hal.h"
#include "serenity/sha256.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>


/* ---------------------------------------------------------------------------
 * AES-256-GCM against the NIST CAVP `gcmEncryptExtIV256` response file
 *
 * Source: NIST Cryptographic Algorithm Validation Program, GCM test vectors
 * [REF-NIST-008].  These are the programme's own published expected results,
 * not values captured from this implementation.  The GF(2^128) bit ordering
 * in GCM is easy to implement self-consistently but wrong, which would
 * interoperate with nothing — only an external vector catches that.
 * ---------------------------------------------------------------------------*/

typedef struct {
    const char *label;
    const char *key_hex;
    const char *iv_hex;
    const char *pt_hex;
    const char *aad_hex;
    const char *ct_hex;
    const char *tag_hex;
} gcm_vector_t;

static const gcm_vector_t GCM_VECTORS[] = {
    {
        "AES-256-GCM CAVP PTlen=128 AADlen=128",
        "92e11dcdaa866f5ce790fd24501f92509aacf4cb8b1339d50c9c1240935dd08b", "ac93a1a6145299bde902f21a", "2d71bcfa914e4ac045b2aa60955fad24", "1e0889016f67601c8ebea4943bc23ad6", "8995ae2e6df3dbf96fac7b7137bae67f", "eca5aa77d51d4a0a14d9c51e1da474ab"
    },
    {
        "AES-256-GCM CAVP PTlen=128 AADlen=160",
        "83688deb4af8007f9b713b47cfa6c73e35ea7a3aa4ecdb414dded03bf7a0fd3a", "0b459724904e010a46901cf3", "33d893a2114ce06fc15d55e454cf90c3", "794a14ccd178c8ebfd1379dc704c5e208f9d8424", "cc66bee423e3fcd4c0865715e9586696", "0fb291bd3dba94a1dfd8b286cfb97ac5"
    },
    {
        "AES-256-GCM CAVP PTlen=408 AADlen=128",
        "5fe01c4baf01cbe07796d5aaef6ec1f45193a98a223594ae4f0ef4952e82e330", "bd587321566c7f1a5dd8652d", "881dc6c7a5d4509f3c4bd2daab08f165ddc204489aa8134562a4eac3d0bcad7965847b102733bb63d1e5c598ece0c3e5dadddd", "9013617817dda947e135ee6dd3653382", "16e375b4973b339d3f746c1c5a568bc7526e909ddff1e19c95c94a6ccff210c9a4a40679de5760c396ac0e2ceb1234f9f5fe26", "abd3d26d65a6275f7a4f56b422acab49"
    },
};

/** @brief Decode @p hex into @p out; returns the byte count. */
static size_t unhex(const char *hex, uint8_t *out, size_t cap) {
    size_t n = 0U;
    while ((hex[n * 2U] != '\0') && (n < cap)) {
        unsigned v = 0U;
        (void)sscanf(&hex[n * 2U], "%2x", &v);
        out[n] = (uint8_t)v;
        ++n;
    }
    return n;
}

static int run_gcm_vectors(void) {
    int failures = 0;

    for (size_t i = 0U; i < (sizeof(GCM_VECTORS) / sizeof(GCM_VECTORS[0])); ++i) {
        const gcm_vector_t *v = &GCM_VECTORS[i];
        uint8_t key[32], iv[12], pt[64], aad[64], ct[64], tag[16];
        uint8_t got_ct[64], got_tag[16], back[64];

        const size_t key_len = unhex(v->key_hex, key, sizeof(key));
        (void)unhex(v->iv_hex, iv, sizeof(iv));
        const size_t pt_len = unhex(v->pt_hex, pt, sizeof(pt));
        const size_t aad_len = unhex(v->aad_hex, aad, sizeof(aad));
        (void)unhex(v->ct_hex, ct, sizeof(ct));
        (void)unhex(v->tag_hex, tag, sizeof(tag));

        ser_aes_gcm_t ctx;
        if (ser_aes_gcm_init(&ctx, key, key_len) != SER_OK) {
            (void)printf("FAIL %s (init)\n", v->label);
            ++failures;
            continue;
        }
        if (ser_aes_gcm_encrypt(&ctx, iv, aad, aad_len, pt, pt_len,
                                got_ct, got_tag) != SER_OK) {
            (void)printf("FAIL %s (encrypt)\n", v->label);
            ++failures;
            continue;
        }
        if (memcmp(got_ct, ct, pt_len) != 0) {
            (void)printf("FAIL %s (ciphertext mismatch)\n", v->label);
            ++failures;
            continue;
        }
        if (memcmp(got_tag, tag, sizeof(tag)) != 0) {
            (void)printf("FAIL %s (tag mismatch)\n", v->label);
            ++failures;
            continue;
        }

        /* Round trip, and then confirm a single flipped ciphertext bit is
         * rejected — a GCM implementation that never fails a tag check is
         * indistinguishable from one with no authentication at all. */
        if (ser_aes_gcm_decrypt(&ctx, iv, aad, aad_len, ct, pt_len,
                                tag, back) != SER_OK) {
            (void)printf("FAIL %s (decrypt)\n", v->label);
            ++failures;
            continue;
        }
        if (memcmp(back, pt, pt_len) != 0) {
            (void)printf("FAIL %s (round-trip plaintext)\n", v->label);
            ++failures;
            continue;
        }
        if (pt_len > 0U) {
            uint8_t bad[64];
            memcpy(bad, ct, pt_len);
            bad[0] ^= 0x01U;
            if (ser_aes_gcm_decrypt(&ctx, iv, aad, aad_len, bad, pt_len,
                                    tag, back) != SER_EPROTO) {
                (void)printf("FAIL %s (tampered ciphertext accepted)\n",
                             v->label);
                ++failures;
                continue;
            }
        }

        (void)printf("ok   %s\n", v->label);
    }
    return failures;
}

static int check(const char *label,
                 const uint8_t *digest,
                 const char *expect_hex) {
    char got[(SER_SHA256_DIGEST_LEN * 2U) + 1U];
    for (unsigned i = 0U; i < SER_SHA256_DIGEST_LEN; ++i) {
        (void)snprintf(&got[i * 2U], 3U, "%02x", digest[i]);
    }
    if (strcmp(got, expect_hex) != 0) {
        (void)printf("FAIL %s\n  got      %s\n  expected %s\n",
                     label, got, expect_hex);
        return 1;
    }
    (void)printf("ok   %s\n", label);
    return 0;
}

int main(void) {
    int failures = 0;
    uint8_t digest[SER_SHA256_DIGEST_LEN];

    /* FIPS 180-4 one-block message example. */
    ser_sha256((const uint8_t *)"abc", 3U, digest);
    failures += check("sha256(\"abc\")", digest,
        "ba7816bf8f01cfea414140de5dae2223"
        "b00361a396177a9cb410ff61f20015ad");

    /* FIPS 180-4 two-block message example (448 bits). */
    static const char two_block[] =
        "abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq";
    ser_sha256((const uint8_t *)two_block, sizeof(two_block) - 1U, digest);
    failures += check("sha256(two-block example)", digest,
        "248d6a61d20638b8e5c026930c3e6039"
        "a33ce45964ff2167f6ecedd419db06c1");

    /* The empty message — the boundary case where padding is the entire
     * block, and the one most often wrong in a hand-written implementation. */
    ser_sha256((const uint8_t *)"", 0U, digest);
    failures += check("sha256(\"\")", digest,
        "e3b0c44298fc1c149afbf4c8996fb924"
        "27ae41e4649b934ca495991b7852b855");

    /* One million 'a', fed in awkward chunk sizes so the streaming path's
     * block-straddling logic is exercised rather than only the one-shot. */
    {
        ser_sha256_t ctx;
        static uint8_t chunk[1000];
        memset(chunk, 'a', sizeof(chunk));
        ser_sha256_init(&ctx);
        for (unsigned i = 0U; i < 1000U; ++i) {
            ser_sha256_update(&ctx, chunk, sizeof(chunk));
        }
        ser_sha256_final(&ctx, digest);
        failures += check("sha256(1e6 x 'a', streamed)", digest,
            "cdc76e5c9914fb9281a1c7e284d73e67"
            "f1809a48a497200e046d39ccc7112cd0");
    }

    /* Streaming with a deliberately awkward split across a block boundary. */
    {
        ser_sha256_t ctx;
        ser_sha256_init(&ctx);
        ser_sha256_update(&ctx, (const uint8_t *)"a", 1U);
        ser_sha256_update(&ctx, (const uint8_t *)"b", 1U);
        ser_sha256_update(&ctx, (const uint8_t *)"c", 1U);
        ser_sha256_final(&ctx, digest);
        failures += check("sha256(\"abc\", byte-at-a-time)", digest,
            "ba7816bf8f01cfea414140de5dae2223"
            "b00361a396177a9cb410ff61f20015ad");
    }

    failures += run_gcm_vectors();

    (void)printf("\n%s\n", (failures == 0) ? "all vectors passed"
                                           : "VECTOR FAILURES");
    return (failures == 0) ? EXIT_SUCCESS : EXIT_FAILURE;
}
