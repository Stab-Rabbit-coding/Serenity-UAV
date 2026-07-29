/**
 * @file    tpm2.c
 * @brief   Minimal TPM 2.0 command layer for the Serenity trust-node firmware.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Command and response structures are marshalled by hand from the TPM 2.0
 * Library specification Part 3 [REF-TCG-001]; each command below cites the
 * Part 3 section that defines its parameter order.  All integers are
 * big-endian on the wire [REF-TCG-001 Part 1 §4.9].
 *
 * Clean-room note: written from the specification, not derived from tpm2-tss,
 * wolfTPM, or any other implementation — see the note in `tpm_tis.c`.
 */

#include "serenity/tpm2.h"

#include "serenity/hal.h"

#include <string.h>

/* TPM_RC_VER1-based response codes used below [REF-TCG-001 Part 2 §6.6.2]. */
#define TPM2_RC_VER1                (0x00000100UL)
#define TPM2_RC_INITIALIZE          (TPM2_RC_VER1 + 0x000UL)  /**< 0x100. */
#define TPM2_RC_NV_DEFINED          (TPM2_RC_VER1 + 0x04CUL)  /**< 0x14C. */

/**
 * @brief Execution budget for a TPM command, milliseconds.
 *
 * TIMEOUT_B is the TCG interface budget [REF-TCG-002 Table 18]; the SLB 9670
 * completes every command this firmware issues well inside it.  Provisioning
 * (TPM2_CreatePrimary) is the slow one and gets its own longer budget.
 */
#define TPM2_CMD_TIMEOUT_MS         (TPM_TIS_TIMEOUT_B_MS)
#define TPM2_CREATE_TIMEOUT_MS      (20000U)

/* ---------------------------------------------------------------------------
 * Marshalling helpers
 *
 * A tiny cursor over the command buffer.  `ok` latches false on the first
 * overflow so a caller can build a whole command and check once at the end,
 * instead of testing after every field — which is how length-check bugs get
 * into hand-marshalled protocol code.
 * ---------------------------------------------------------------------------*/

typedef struct {
    uint8_t *buf;   /**< Destination buffer.                                  */
    size_t   cap;   /**< Capacity of `buf`.                                   */
    size_t   len;   /**< Bytes written so far.                                */
    bool     ok;    /**< False once an append has overflowed.                 */
} tpm_wr_t;

static void wr_init(tpm_wr_t *w, uint8_t *buf, size_t cap) {
    w->buf = buf;
    w->cap = cap;
    w->len = 0U;
    w->ok = true;
}

static void wr_u8(tpm_wr_t *w, uint8_t v) {
    if (!w->ok || ((w->len + 1U) > w->cap)) {
        w->ok = false;
        return;
    }
    w->buf[w->len++] = v;
}

static void wr_u16(tpm_wr_t *w, uint16_t v) {
    wr_u8(w, (uint8_t)((v >> 8) & 0xFFU));
    wr_u8(w, (uint8_t)(v & 0xFFU));
}

static void wr_u32(tpm_wr_t *w, uint32_t v) {
    wr_u16(w, (uint16_t)((v >> 16) & 0xFFFFU));
    wr_u16(w, (uint16_t)(v & 0xFFFFU));
}

static void wr_bytes(tpm_wr_t *w, const uint8_t *src, size_t n) {
    if (!w->ok || ((w->len + n) > w->cap)) {
        w->ok = false;
        return;
    }
    if (n > 0U) {
        memcpy(&w->buf[w->len], src, n);
        w->len += n;
    }
}

/** @brief Append a TPM2B: a UINT16 size followed by that many bytes. */
static void wr_tpm2b(tpm_wr_t *w, const uint8_t *src, size_t n) {
    wr_u16(w, (uint16_t)n);
    wr_bytes(w, src, n);
}

/** @brief Read a big-endian UINT16 from @p p. */
static uint16_t rd_u16(const uint8_t *p) {
    return (uint16_t)(((uint16_t)p[0] << 8) | (uint16_t)p[1]);
}

/** @brief Read a big-endian UINT32 from @p p. */
static uint32_t rd_u32(const uint8_t *p) {
    return ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16)
           | ((uint32_t)p[2] << 8) | (uint32_t)p[3];
}

/**
 * @brief Patch the commandSize field and run the command.
 *
 * Every TPM 2.0 command header is tag (UINT16), commandSize (UINT32),
 * commandCode (UINT32) [REF-TCG-001 Part 1 §18.2].  commandSize cannot be
 * known until the parameters are marshalled, so it is written last, over the
 * placeholder left at offset 2.
 *
 * @param ctx       Context supplying the TIS transport and buffers.
 * @param w         Completed command writer.
 * @param timeout_ms Execution budget.
 * @param rsp_len   Out: response length in bytes.
 * @return SER_OK if the TPM returned TPM_RC_SUCCESS.  A non-success
 *         responseCode yields SER_EIO with the code in `ctx->last_rc`.
 */
static int tpm_run(ser_tpm2_t *ctx,
                   tpm_wr_t *w,
                   uint32_t timeout_ms,
                   size_t *rsp_len) {
    if (!w->ok) {
        return SER_ENOSPC;
    }

    w->buf[2] = (uint8_t)((w->len >> 24) & 0xFFU);
    w->buf[3] = (uint8_t)((w->len >> 16) & 0xFFU);
    w->buf[4] = (uint8_t)((w->len >> 8) & 0xFFU);
    w->buf[5] = (uint8_t)(w->len & 0xFFU);

    size_t got = 0U;
    const int rc = ser_tpm_tis_transmit(&ctx->tis,
                                        w->buf, w->len,
                                        ctx->rsp, sizeof(ctx->rsp),
                                        &got,
                                        timeout_ms);
    if (rc != SER_OK) {
        return rc;
    }
    if (got < 10U) {
        return SER_EPROTO;
    }

    ctx->last_rc = rd_u32(&ctx->rsp[6]);
    if (rsp_len != NULL) {
        *rsp_len = got;
    }
    return (ctx->last_rc == TPM2_RC_SUCCESS) ? SER_OK : SER_EIO;
}

/**
 * @brief Start a command header.
 *
 * Leaves a four-byte placeholder for commandSize that `tpm_run()` fills in.
 */
static void tpm_begin(ser_tpm2_t *ctx,
                      tpm_wr_t *w,
                      uint16_t tag,
                      uint32_t code) {
    wr_init(w, ctx->cmd, sizeof(ctx->cmd));
    wr_u16(w, tag);
    wr_u32(w, 0UL);         /* commandSize placeholder. */
    wr_u32(w, code);
}

/**
 * @brief Append a password authorization area with an empty password.
 *
 * [REF-TCG-001 Part 1 §19.6.9]: the authorization area is preceded by its own
 * UINT32 size and, for a password session, contains sessionHandle TPM_RS_PW,
 * a zero-length nonce, the session attributes byte, and a zero-length hmac
 * (the password itself).  Every key this firmware creates uses an empty
 * authValue, so the password field is always empty.
 *
 * The nine bytes are: 4 (handle) + 2 (nonce size) + 1 (attributes)
 * + 2 (password size).
 */
static void wr_password_auth(tpm_wr_t *w) {
    wr_u32(w, 9UL);                         /* authorizationSize.             */
    wr_u32(w, TPM2_RS_PW);                  /* sessionHandle.                 */
    wr_u16(w, 0U);                          /* nonce: empty.                  */
    wr_u8(w, TPM2_SESSION_CONTINUE);        /* sessionAttributes.             */
    wr_u16(w, 0U);                          /* hmac/password: empty.          */
}

/* ---------------------------------------------------------------------------
 * Lifecycle
 * ---------------------------------------------------------------------------*/

/** @brief TPM2_Startup [REF-TCG-001 Part 3 §9.3]. */
static int tpm2_startup(ser_tpm2_t *ctx, uint16_t startup_type) {
    tpm_wr_t w;
    tpm_begin(ctx, &w, TPM2_ST_NO_SESSIONS, TPM2_CC_STARTUP);
    wr_u16(&w, startup_type);

    const int rc = tpm_run(ctx, &w, TPM2_CMD_TIMEOUT_MS, NULL);
    /*
     * TPM_RC_INITIALIZE here means "already initialized", which happens on a
     * warm MCU reset that did not reset the TPM.  That is a normal, expected
     * state, not a failure.
     */
    if ((rc == SER_EIO) && (ctx->last_rc == TPM2_RC_INITIALIZE)) {
        return SER_OK;
    }
    return rc;
}

/** @brief TPM2_SelfTest [REF-TCG-001 Part 3 §10.2]. */
static int tpm2_self_test(ser_tpm2_t *ctx, bool full_test) {
    tpm_wr_t w;
    tpm_begin(ctx, &w, TPM2_ST_NO_SESSIONS, TPM2_CC_SELF_TEST);
    wr_u8(&w, full_test ? 1U : 0U);         /* fullTest, a TPMI_YES_NO.       */
    return tpm_run(ctx, &w, TPM2_CMD_TIMEOUT_MS, NULL);
}

int ser_tpm2_open(ser_tpm2_t *ctx) {
    if (ctx == NULL) {
        return SER_EINVAL;
    }

    memset(ctx, 0, sizeof(*ctx));

    int rc = ser_tpm_tis_init(&ctx->tis);
    if (rc != SER_OK) {
        ser_hal_log("tpm: TIS init failed rc=%d\n", rc);
        return rc;
    }

    rc = tpm2_startup(ctx, TPM2_SU_CLEAR);
    if (rc != SER_OK) {
        ser_hal_log("tpm: startup failed rc=%d tpm_rc=0x%08lx\n",
                    rc, (unsigned long)ctx->last_rc);
        return rc;
    }

    /*
     * Incremental self-test, not a full one: the SLB 9670 self-tests the
     * algorithms needed for a command on first use anyway
     * [REF-TCG-002 §6.5.1.6], and a full test costs seconds that would delay
     * the node joining the bus at every power-up.
     */
    rc = tpm2_self_test(ctx, false);
    if (rc != SER_OK) {
        ser_hal_log("tpm: self-test failed rc=%d tpm_rc=0x%08lx\n",
                    rc, (unsigned long)ctx->last_rc);
        return rc;
    }

    ctx->ready = true;
    return SER_OK;
}

int ser_tpm2_close(ser_tpm2_t *ctx) {
    if (ctx == NULL) {
        return SER_EINVAL;
    }

    tpm_wr_t w;
    tpm_begin(ctx, &w, TPM2_ST_NO_SESSIONS, TPM2_CC_SHUTDOWN);
    wr_u16(&w, TPM2_SU_CLEAR);
    (void)tpm_run(ctx, &w, TPM2_CMD_TIMEOUT_MS, NULL);

    ctx->ready = false;
    return ser_tpm_tis_close(&ctx->tis);
}

/* ---------------------------------------------------------------------------
 * Provisioning
 * ---------------------------------------------------------------------------*/

/**
 * @brief Append the keyed-hash signing-key template as a TPM2B_PUBLIC.
 *
 * TPMT_PUBLIC field order [REF-TCG-001 Part 2 §12.2.4]: type, nameAlg,
 * objectAttributes, authPolicy, parameters, unique.  For a keyedhash object
 * the parameters are a TPMS_KEYEDHASH_PARMS holding a TPMT_KEYEDHASH_SCHEME
 * [Part 2 §12.2.3.3], which for HMAC is the scheme selector followed by the
 * hash algorithm.
 *
 * The whole TPMT_PUBLIC is wrapped in a UINT16 size, so it is written to a
 * scratch buffer first and then emitted as a TPM2B.
 */
static void wr_hmac_key_template(tpm_wr_t *w) {
    uint8_t inner[64];
    tpm_wr_t t;
    wr_init(&t, inner, sizeof(inner));

    wr_u16(&t, TPM2_ALG_KEYEDHASH);     /* type.                              */
    wr_u16(&t, TPM2_ALG_SHA256);        /* nameAlg.                           */
    wr_u32(&t, TPM2_OBJ_FIXEDTPM
               | TPM2_OBJ_FIXEDPARENT
               | TPM2_OBJ_SENSITIVEDATAORIGIN
               | TPM2_OBJ_USERWITHAUTH
               | TPM2_OBJ_NODA
               | TPM2_OBJ_SIGN_ENCRYPT); /* objectAttributes; note that
                                          * RESTRICTED is deliberately clear —
                                          * see `tpm2.h`. */
    wr_u16(&t, 0U);                     /* authPolicy: empty TPM2B_DIGEST.    */
    wr_u16(&t, TPM2_ALG_HMAC);          /* scheme.scheme.                     */
    wr_u16(&t, TPM2_ALG_SHA256);        /* scheme.details.hmac.hashAlg.       */
    wr_u16(&t, 0U);                     /* unique: empty TPM2B_DIGEST.        */

    if (!t.ok) {
        w->ok = false;
        return;
    }
    wr_tpm2b(w, inner, t.len);
}

/** @brief TPM2_FlushContext [REF-TCG-001 Part 3 §28.4]. */
static int tpm2_flush_context(ser_tpm2_t *ctx, uint32_t handle) {
    tpm_wr_t w;
    tpm_begin(ctx, &w, TPM2_ST_NO_SESSIONS, TPM2_CC_FLUSH_CONTEXT);
    /* flushHandle is a *parameter* here, not a handle-area entry
     * [REF-TCG-001 Part 3 §28.4.1] — one of the few commands where that is
     * true, and an easy place to marshal a command incorrectly. */
    wr_u32(&w, handle);
    return tpm_run(ctx, &w, TPM2_CMD_TIMEOUT_MS, NULL);
}

int ser_tpm2_provision_signing_key(ser_tpm2_t *ctx) {
    if ((ctx == NULL) || !ctx->ready) {
        return SER_EINVAL;
    }

    /*
     * If a key is already at the persistent handle, provisioning is a no-op.
     * Re-creating it would give the node a new identity and silently
     * invalidate every peer's record of it, so the idempotent path matters.
     */
    if (ser_tpm2_load_key_name(ctx) == SER_OK) {
        ser_hal_log("tpm: signing key already present at 0x%08lx\n",
                    (unsigned long)SER_TPM_SIGNING_KEY_HANDLE);
        return SER_OK;
    }

    /* ---- TPM2_CreatePrimary [REF-TCG-001 Part 3 §24.1] ------------------ */
    tpm_wr_t w;
    tpm_begin(ctx, &w, TPM2_ST_SESSIONS, TPM2_CC_CREATE_PRIMARY);
    wr_u32(&w, TPM2_RH_OWNER);          /* primaryHandle (handle area).       */
    wr_password_auth(&w);

    /*
     * inSensitive is a TPM2B_SENSITIVE_CREATE wrapping a TPMS_SENSITIVE_CREATE
     * of { userAuth, data } [REF-TCG-001 Part 2 §11.1.15].  Both are empty:
     * no authValue on the key, and no caller-supplied seed (the key material
     * comes from the TPM's own RNG because sensitiveDataOrigin is SET).
     */
    wr_u16(&w, 4U);                     /* size of the TPMS_SENSITIVE_CREATE. */
    wr_u16(&w, 0U);                     /* userAuth: empty.                   */
    wr_u16(&w, 0U);                     /* data: empty.                       */

    wr_hmac_key_template(&w);           /* inPublic.                          */
    wr_u16(&w, 0U);                     /* outsideInfo: empty TPM2B_DATA.     */
    wr_u32(&w, 0UL);                    /* creationPCR: empty TPML_PCR_SEL.   */

    size_t rsp_len = 0U;
    int rc = tpm_run(ctx, &w, TPM2_CREATE_TIMEOUT_MS, &rsp_len);
    if (rc != SER_OK) {
        ser_hal_log("tpm: CreatePrimary failed rc=%d tpm_rc=0x%08lx\n",
                    rc, (unsigned long)ctx->last_rc);
        return rc;
    }
    if (rsp_len < 14U) {
        return SER_EPROTO;
    }

    /* Response: header (10) + objectHandle (4) + parameterSize + ... */
    const uint32_t transient = rd_u32(&ctx->rsp[10]);

    /* ---- TPM2_EvictControl [REF-TCG-001 Part 3 §28.5] ------------------- */
    tpm_begin(ctx, &w, TPM2_ST_SESSIONS, TPM2_CC_EVICT_CONTROL);
    wr_u32(&w, TPM2_RH_OWNER);          /* auth (handle area).                */
    wr_u32(&w, transient);              /* objectHandle (handle area).        */
    wr_password_auth(&w);
    wr_u32(&w, SER_TPM_SIGNING_KEY_HANDLE);  /* persistentHandle (parameter). */

    rc = tpm_run(ctx, &w, TPM2_CMD_TIMEOUT_MS, NULL);
    if ((rc == SER_EIO) && (ctx->last_rc == TPM2_RC_NV_DEFINED)) {
        /* Something is already at the handle — treat as already provisioned. */
        rc = SER_OK;
    }

    (void)tpm2_flush_context(ctx, transient);

    if (rc != SER_OK) {
        ser_hal_log("tpm: EvictControl failed rc=%d tpm_rc=0x%08lx\n",
                    rc, (unsigned long)ctx->last_rc);
        return rc;
    }

    return ser_tpm2_load_key_name(ctx);
}

int ser_tpm2_load_key_name(ser_tpm2_t *ctx) {
    if ((ctx == NULL) || !ctx->ready) {
        return SER_EINVAL;
    }

    /* ---- TPM2_ReadPublic [REF-TCG-001 Part 3 §12.4] --------------------- */
    tpm_wr_t w;
    tpm_begin(ctx, &w, TPM2_ST_NO_SESSIONS, TPM2_CC_READ_PUBLIC);
    wr_u32(&w, SER_TPM_SIGNING_KEY_HANDLE);

    size_t rsp_len = 0U;
    const int rc = tpm_run(ctx, &w, TPM2_CMD_TIMEOUT_MS, &rsp_len);
    if (rc != SER_OK) {
        return (ctx->last_rc != TPM2_RC_SUCCESS) ? SER_ENODEV : rc;
    }

    /*
     * Response parameters [REF-TCG-001 Part 3 §12.4.1]: outPublic
     * (TPM2B_PUBLIC), name (TPM2B_NAME), qualifiedName (TPM2B_NAME).  With
     * TPM_ST_NO_SESSIONS there is no parameterSize field, so outPublic starts
     * immediately after the 10-byte header.
     */
    size_t off = 10U;
    if ((off + 2U) > rsp_len) {
        return SER_EPROTO;
    }
    const size_t pub_len = (size_t)rd_u16(&ctx->rsp[off]);
    off += 2U + pub_len;

    if ((off + 2U) > rsp_len) {
        return SER_EPROTO;
    }
    const size_t name_len = (size_t)rd_u16(&ctx->rsp[off]);
    off += 2U;
    if (((off + name_len) > rsp_len) || (name_len > sizeof(ctx->key_name))) {
        return SER_EPROTO;
    }

    memcpy(ctx->key_name, &ctx->rsp[off], name_len);
    ctx->key_name_len = name_len;
    return SER_OK;
}

/* ---------------------------------------------------------------------------
 * In-flight operations
 * ---------------------------------------------------------------------------*/

int ser_tpm2_hmac(ser_tpm2_t *ctx,
                  const uint8_t *data,
                  size_t len,
                  uint8_t mac[TPM2_SHA256_LEN]) {
    if ((ctx == NULL) || !ctx->ready || (data == NULL) || (mac == NULL)) {
        return SER_EINVAL;
    }

    /* ---- TPM2_HMAC [REF-TCG-001 Part 3 §15.4] --------------------------- */
    tpm_wr_t w;
    tpm_begin(ctx, &w, TPM2_ST_SESSIONS, TPM2_CC_HMAC);
    wr_u32(&w, SER_TPM_SIGNING_KEY_HANDLE);     /* handle (handle area).      */
    wr_password_auth(&w);
    wr_tpm2b(&w, data, len);                    /* buffer (TPM2B_MAX_BUFFER). */
    wr_u16(&w, TPM2_ALG_SHA256);                /* hashAlg.                   */

    size_t rsp_len = 0U;
    const int rc = tpm_run(ctx, &w, TPM2_CMD_TIMEOUT_MS, &rsp_len);
    if (rc != SER_OK) {
        return rc;
    }

    /*
     * With TPM_ST_SESSIONS the response carries a UINT32 parameterSize before
     * the parameters [REF-TCG-001 Part 1 §18.4], so outHMAC starts at
     * offset 14, not 10.  Getting this wrong yields a plausible-looking but
     * wrong MAC, which is precisely the class of bug that only shows up as an
     * unexplained verification failure on the far side of the bus.
     */
    const size_t off = 14U;
    if ((off + 2U) > rsp_len) {
        return SER_EPROTO;
    }
    const size_t mac_len = (size_t)rd_u16(&ctx->rsp[off]);
    if ((mac_len != TPM2_SHA256_LEN) || ((off + 2U + mac_len) > rsp_len)) {
        return SER_EPROTO;
    }

    memcpy(mac, &ctx->rsp[off + 2U], TPM2_SHA256_LEN);
    return SER_OK;
}

int ser_tpm2_get_random(ser_tpm2_t *ctx, uint8_t *out, size_t len) {
    if ((ctx == NULL) || !ctx->ready || (out == NULL)) {
        return SER_EINVAL;
    }

    size_t done = 0U;
    while (done < len) {
        size_t want = len - done;
        if (want > TPM2_SHA256_LEN) {
            /* The TPM may legitimately return fewer bytes than requested
             * [REF-TCG-001 Part 3 §16.1]; keeping requests to one digest
             * length at a time makes the short-return path routine rather
             * than exceptional. */
            want = TPM2_SHA256_LEN;
        }

        /* ---- TPM2_GetRandom [REF-TCG-001 Part 3 §16.1] ------------------ */
        tpm_wr_t w;
        tpm_begin(ctx, &w, TPM2_ST_NO_SESSIONS, TPM2_CC_GET_RANDOM);
        wr_u16(&w, (uint16_t)want);

        size_t rsp_len = 0U;
        const int rc = tpm_run(ctx, &w, TPM2_CMD_TIMEOUT_MS, &rsp_len);
        if (rc != SER_OK) {
            return rc;
        }
        if ((10U + 2U) > rsp_len) {
            return SER_EPROTO;
        }
        const size_t got = (size_t)rd_u16(&ctx->rsp[10]);
        if ((got == 0U) || ((10U + 2U + got) > rsp_len)) {
            return SER_EPROTO;
        }
        const size_t take = (got > (len - done)) ? (len - done) : got;
        memcpy(&out[done], &ctx->rsp[12], take);
        done += take;
    }
    return SER_OK;
}

int ser_tpm2_pcr_extend(ser_tpm2_t *ctx,
                        uint32_t pcr_index,
                        const uint8_t digest[TPM2_SHA256_LEN]) {
    if ((ctx == NULL) || !ctx->ready || (digest == NULL)) {
        return SER_EINVAL;
    }

    /* ---- TPM2_PCR_Extend [REF-TCG-001 Part 3 §22.2] --------------------- */
    tpm_wr_t w;
    tpm_begin(ctx, &w, TPM2_ST_SESSIONS, TPM2_CC_PCR_EXTEND);
    wr_u32(&w, pcr_index);              /* pcrHandle (handle area).           */
    wr_password_auth(&w);
    /* digests is a TPML_DIGEST_VALUES: UINT32 count, then each entry is a
     * TPMT_HA of { hashAlg, digest bytes } [REF-TCG-001 Part 2 §10.3.2]. */
    wr_u32(&w, 1UL);
    wr_u16(&w, TPM2_ALG_SHA256);
    wr_bytes(&w, digest, TPM2_SHA256_LEN);

    return tpm_run(ctx, &w, TPM2_CMD_TIMEOUT_MS, NULL);
}

int ser_tpm2_pcr_read(ser_tpm2_t *ctx,
                      uint32_t pcr_index,
                      uint8_t digest[TPM2_SHA256_LEN]) {
    if ((ctx == NULL) || !ctx->ready || (digest == NULL) ||
        (pcr_index > 23U)) {
        return SER_EINVAL;
    }

    /* ---- TPM2_PCR_Read [REF-TCG-001 Part 3 §22.4] ----------------------- */
    tpm_wr_t w;
    tpm_begin(ctx, &w, TPM2_ST_NO_SESSIONS, TPM2_CC_PCR_READ);
    /*
     * pcrSelectionIn is a TPML_PCR_SELECTION: UINT32 count, then per entry a
     * TPMS_PCR_SELECTION of { hashAlg, sizeofSelect, bitmap }
     * [REF-TCG-001 Part 2 §10.6.2].  A 3-byte bitmap covers PCRs 0..23; the
     * selected index sets one bit, little-endian within the byte array.
     */
    uint8_t select[3] = {0U, 0U, 0U};
    select[pcr_index / 8U] = (uint8_t)(1U << (pcr_index % 8U));

    wr_u32(&w, 1UL);
    wr_u16(&w, TPM2_ALG_SHA256);
    wr_u8(&w, (uint8_t)sizeof(select));
    wr_bytes(&w, select, sizeof(select));

    size_t rsp_len = 0U;
    const int rc = tpm_run(ctx, &w, TPM2_CMD_TIMEOUT_MS, &rsp_len);
    if (rc != SER_OK) {
        return rc;
    }

    /*
     * Response parameters: pcrUpdateCounter (UINT32), pcrSelectionOut
     * (TPML_PCR_SELECTION), pcrValues (TPML_DIGEST).  Walk past the first two
     * to reach the digest list rather than assuming a fixed offset, because
     * pcrSelectionOut's length depends on what the TPM echoes back.
     */
    size_t off = 10U + 4U;              /* header + pcrUpdateCounter.         */
    if ((off + 4U) > rsp_len) {
        return SER_EPROTO;
    }
    const uint32_t sel_count = rd_u32(&ctx->rsp[off]);
    off += 4U;
    for (uint32_t i = 0U; i < sel_count; ++i) {
        if ((off + 3U) > rsp_len) {
            return SER_EPROTO;
        }
        const size_t size_of_select = (size_t)ctx->rsp[off + 2U];
        off += 3U + size_of_select;
    }

    if ((off + 4U) > rsp_len) {
        return SER_EPROTO;
    }
    const uint32_t digest_count = rd_u32(&ctx->rsp[off]);
    off += 4U;
    if (digest_count == 0U) {
        /* The PCR exists but the TPM returned no value for it — a selection
         * mismatch, not a transport error. */
        return SER_EPROTO;
    }
    if ((off + 2U) > rsp_len) {
        return SER_EPROTO;
    }
    const size_t dlen = (size_t)rd_u16(&ctx->rsp[off]);
    off += 2U;
    if ((dlen != TPM2_SHA256_LEN) || ((off + dlen) > rsp_len)) {
        return SER_EPROTO;
    }

    memcpy(digest, &ctx->rsp[off], TPM2_SHA256_LEN);
    return SER_OK;
}
