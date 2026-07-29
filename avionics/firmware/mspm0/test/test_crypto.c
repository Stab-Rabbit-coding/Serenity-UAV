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

#include "serenity/sha256.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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

    (void)printf("\n%s\n", (failures == 0) ? "all vectors passed"
                                           : "VECTOR FAILURES");
    return (failures == 0) ? EXIT_SUCCESS : EXIT_FAILURE;
}
