/**
 * @file    tpm_tis.c
 * @brief   Infineon OPTIGA SLB 9670 TPM 2.0 — TIS-over-SPI transport layer.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Implements the TCG PC Client Platform TPM Profile SPI interface
 * [REF-TCG-002 §7.4] on top of the four-call SPI transaction API in `hal.h`.
 * See `tpm_tis.h` for the clause-by-clause citation list; this file cites the
 * specific clause at each non-obvious step rather than repeating the list.
 *
 * Clean-room note: this driver was written from the TCG PTP specification
 * text (revision 14, 2020-09-04, downloaded from trustedcomputinggroup.org
 * for this task) and the SLB 9670 datasheet.  No code was taken from the
 * Linux kernel `tpm_tis_spi` driver, from tpm2-tss, or from any other
 * implementation — those are GPL-2.0 and BSD-2-Clause respectively, and this
 * repository is CC BY 4.0 (root `AGENTS.md` §3).
 */

#include "serenity/tpm_tis.h"

#include "serenity/hal.h"

#include <string.h>

/* ---------------------------------------------------------------------------
 * SPI header construction
 *
 * [REF-TCG-002 §7.4.6 Table 48]: the transaction opens with a 4-byte header.
 *
 *   byte 0: bit 7    = 1 for read, 0 for write
 *           bit 6    = reserved
 *           bits 5:0 = zero-based transfer size, so 0x00 is 1 byte and
 *                      0x3F is 64 bytes
 *   bytes 1..3: the 24-bit register address, most significant byte first
 * ---------------------------------------------------------------------------*/

/** @brief Byte 0 of the SPI header: direction plus zero-based length. */
#define TIS_HDR0(read, len)  ((uint8_t)(((read) ? 0x80U : 0x00U) | \
                                        (uint8_t)((len) - 1U)))

/**
 * @brief Number of wait-state polling windows before giving up.
 *
 * [REF-TCG-002 §7.4.5]: "The TPM may insert any number of wait states that it
 * needs", polled in 8-clock (1-byte) windows.  The specification sets no
 * bound, so the driver imposes one: without it a wedged TPM would hang the
 * node's main loop indefinitely, which the watchdog would then turn into a
 * reboot loop with no diagnostic.  Exceeding this bound is reported as
 * SER_ETIMEDOUT so the node lifecycle can latch a TPM fault instead.
 */
#define TIS_WAIT_POLLS_MAX   (64U)

/**
 * @brief Absolute address of a TIS register in the current locality.
 *
 * [REF-TCG-002 §7.4.6 rule 5, §6.4 Table 9]: locality n lives at
 * base + n * 0x1000.
 */
static uint32_t tis_addr(const ser_tpm_tis_t *tis, uint16_t reg) {
    return TPM_TIS_SPI_BASE
           + ((uint32_t)tis->locality * TPM_TIS_LOCALITY_STRIDE)
           + (uint32_t)reg;
}

/**
 * @brief Run one TIS SPI transaction: header, wait states, then data.
 *
 * @param tis   Transport context (supplies the locality).
 * @param read  True for a register read, false for a register write.
 * @param reg   Register offset within the locality.
 * @param buf   Data to write, or destination for data read.
 * @param len   Transfer length, 1..TPM_TIS_MAX_XFER.
 * @return SER_OK, or a negative `SER_E*` code.
 *
 * The wait-state handling is the subtle part.  [REF-TCG-002 §7.4.5]: the TPM
 * may hold MISO low to stall, starting in the clock window in which the last
 * address bit (A[0]) is driven.  The host must therefore look at the MISO
 * byte captured *while it was clocking out header byte 3*: if its least
 * significant bit is 0, the TPM is stalling and the host polls one byte at a
 * time until it reads a 1.  Once a 1 is seen there is no further flow
 * control and the whole data phase proceeds.
 */
static int tis_xfer(ser_tpm_tis_t *tis,
                    bool read,
                    uint16_t reg,
                    uint8_t *buf,
                    size_t len) {
    if ((tis == NULL) || (buf == NULL) ||
        (len == 0U) || (len > TPM_TIS_MAX_XFER)) {
        return SER_EINVAL;
    }

    const uint32_t addr = tis_addr(tis, reg);
    uint8_t header[4];
    uint8_t hdr_miso[4];

    header[0] = TIS_HDR0(read, len);
    header[1] = (uint8_t)((addr >> 16) & 0xFFU);
    header[2] = (uint8_t)((addr >> 8) & 0xFFU);
    header[3] = (uint8_t)(addr & 0xFFU);

    int rc = ser_hal_spi_begin(SER_SPI_TPM, 0U);
    if (rc != SER_OK) {
        return rc;
    }

    rc = ser_hal_spi_xfer_cont(SER_SPI_TPM, header, hdr_miso, sizeof(header));
    if (rc != SER_OK) {
        (void)ser_hal_spi_end(SER_SPI_TPM);
        return rc;
    }

    /*
     * The wait-state indication rides on the MISO byte returned during header
     * byte 3.  Bit 0 of that byte is the level MISO held in the A[0] clock
     * window: 1 means the TPM is ready, 0 means it is stalling.
     * [REF-TCG-002 §7.4.5, Figure 7]
     */
    if ((hdr_miso[3] & 0x01U) == 0U) {
        bool ready = false;
        for (unsigned poll = 0U; poll < TIS_WAIT_POLLS_MAX; ++poll) {
            uint8_t wait_byte = 0U;
            rc = ser_hal_spi_xfer_cont(SER_SPI_TPM, NULL, &wait_byte, 1U);
            if (rc != SER_OK) {
                (void)ser_hal_spi_end(SER_SPI_TPM);
                return rc;
            }
            /* The TPM holds MISO low for a whole 8-clock window, so a ready
             * indication appears as a non-zero byte with bit 0 set. */
            if ((wait_byte & 0x01U) != 0U) {
                ready = true;
                break;
            }
        }
        if (!ready) {
            (void)ser_hal_spi_end(SER_SPI_TPM);
            return SER_ETIMEDOUT;
        }
    }

    if (read) {
        rc = ser_hal_spi_xfer_cont(SER_SPI_TPM, NULL, buf, len);
    } else {
        rc = ser_hal_spi_xfer_cont(SER_SPI_TPM, buf, NULL, len);
    }

    const int end_rc = ser_hal_spi_end(SER_SPI_TPM);
    return (rc != SER_OK) ? rc : end_rc;
}

/** @brief Read one 8-bit TIS register. */
static int tis_read8(ser_tpm_tis_t *tis, uint16_t reg, uint8_t *value) {
    return tis_xfer(tis, true, reg, value, 1U);
}

/** @brief Write one 8-bit TIS register. */
static int tis_write8(ser_tpm_tis_t *tis, uint16_t reg, uint8_t value) {
    uint8_t v = value;
    return tis_xfer(tis, false, reg, &v, 1U);
}

/**
 * @brief Read TPM_STS_x as a 32-bit value.
 *
 * [REF-TCG-002 §7.5]: multi-byte registers transfer least significant byte
 * first, so byte offset 0 on the wire is bits 7:0 of the register.  Note that
 * this is the opposite of the *payload* byte order, which is big-endian —
 * conflating the two is the classic TIS porting bug.
 */
static int tis_read_sts(ser_tpm_tis_t *tis, uint32_t *sts) {
    uint8_t raw[4] = {0U, 0U, 0U, 0U};
    const int rc = tis_xfer(tis, true, TPM_TIS_REG_STS, raw, sizeof(raw));
    if (rc != SER_OK) {
        return rc;
    }
    *sts = (uint32_t)raw[0]
           | ((uint32_t)raw[1] << 8)
           | ((uint32_t)raw[2] << 16)
           | ((uint32_t)raw[3] << 24);
    return SER_OK;
}

/**
 * @brief Extract burstCount from a TPM_STS_x value.
 *
 * [REF-TCG-002 Table 21]: burstCount is bits 23:8 — "the number of bytes that
 * the TPM can return on reads or accept on writes without inserting wait
 * states on the bus".
 */
static uint16_t tis_burst_count(uint32_t sts) {
    return (uint16_t)((sts >> 8) & 0xFFFFU);
}

/**
 * @brief Poll TPM_STS_x until all bits in @p mask are set.
 *
 * @param require_valid  When true, also require stsValid, because dataAvail
 *                       and Expect are only meaningful when stsValid is 1
 *                       [REF-TCG-002 Table 21, "Valid indicator"].
 */
static int tis_wait_sts(ser_tpm_tis_t *tis,
                        uint8_t mask,
                        bool require_valid,
                        uint32_t timeout_ms,
                        uint32_t *last_sts) {
    const uint64_t deadline = ser_hal_time_ms() + (uint64_t)timeout_ms;
    const uint8_t want = require_valid ? (uint8_t)(mask | TPM_TIS_STS_VALID)
                                       : mask;

    for (;;) {
        uint32_t sts = 0U;
        const int rc = tis_read_sts(tis, &sts);
        if (rc != SER_OK) {
            return rc;
        }
        if (last_sts != NULL) {
            *last_sts = sts;
        }
        if (((uint8_t)(sts & 0xFFU) & want) == want) {
            return SER_OK;
        }
        if (ser_hal_time_ms() >= deadline) {
            return SER_ETIMEDOUT;
        }
        /* A short backoff keeps a busy TPM from monopolising the SPI bus
         * while the node's main loop still needs to service CAN. */
        ser_hal_delay_us(100U);
    }
}

/**
 * @brief Move the TPM to the Ready state and confirm it got there.
 *
 * Writing commandReady both aborts any command in progress and flushes the
 * FIFO [REF-TCG-002 §6.5.2.5].  TIMEOUT_B is the TCG budget for this
 * transition.
 */
static int tis_command_ready(ser_tpm_tis_t *tis) {
    int rc = tis_write8(tis, TPM_TIS_REG_STS, TPM_TIS_STS_COMMAND_READY);
    if (rc != SER_OK) {
        return rc;
    }
    rc = tis_wait_sts(tis, TPM_TIS_STS_COMMAND_READY, false,
                      TPM_TIS_TIMEOUT_B_MS, NULL);
    return rc;
}

int ser_tpm_tis_init(ser_tpm_tis_t *tis) {
    if (tis == NULL) {
        return SER_EINVAL;
    }

    memset(tis, 0, sizeof(*tis));
    tis->locality = 0U;     /* The SLB 9670 in every Serenity board is used
                             * from locality 0 only; nothing in this firmware
                             * runs at a higher locality. */

    /*
     * _TPM_INIT: for an SPI-packaged TPM this is the low-to-high transition
     * of RST# [REF-TCG-002 §6.5.1.5 rule 2].  The 10 ms low time and 100 ms
     * settle are conservative against the SLB 9670's own reset timing
     * (datasheet Table 12 / Figure 3); the TPM is allowed up to TIMEOUT_A to
     * present a valid TPM_ACCESS_0 afterwards, which the poll below honours.
     */
    int rc = ser_hal_gpio_write(SER_GPIO_TPM_RST_N, false);
    if ((rc != SER_OK) && (rc != SER_ENOTSUP)) {
        return rc;
    }
    ser_hal_delay_us(10000U);
    rc = ser_hal_gpio_write(SER_GPIO_TPM_RST_N, true);
    if ((rc != SER_OK) && (rc != SER_ENOTSUP)) {
        return rc;
    }
    ser_hal_delay_us(100000U);

    /*
     * Wait for tpmRegValidSts.  [REF-TCG-002 §6.5.2.2]: "If this field remains
     * a 0 for longer than the period specified in Section 6.5.1.4 Timeouts,
     * Software may assume that the TPM is broken and should not use it."
     */
    const uint64_t valid_deadline = ser_hal_time_ms() + TPM_TIS_TIMEOUT_A_MS;
    uint8_t access = 0U;
    for (;;) {
        rc = tis_read8(tis, TPM_TIS_REG_ACCESS, &access);
        if (rc != SER_OK) {
            return rc;
        }
        if ((access & TPM_TIS_ACCESS_VALID) != 0U) {
            break;
        }
        if (ser_hal_time_ms() >= valid_deadline) {
            return SER_ENODEV;
        }
        ser_hal_delay_us(1000U);
    }

    /* Claim the locality if we do not already hold it [REF-TCG-002 Table 20]. */
    if ((access & TPM_TIS_ACCESS_ACTIVE_LOC) == 0U) {
        rc = tis_write8(tis, TPM_TIS_REG_ACCESS, TPM_TIS_ACCESS_REQUEST_USE);
        if (rc != SER_OK) {
            return rc;
        }
        const uint64_t loc_deadline = ser_hal_time_ms() + TPM_TIS_TIMEOUT_A_MS;
        for (;;) {
            rc = tis_read8(tis, TPM_TIS_REG_ACCESS, &access);
            if (rc != SER_OK) {
                return rc;
            }
            if ((access & (TPM_TIS_ACCESS_VALID | TPM_TIS_ACCESS_ACTIVE_LOC))
                == (TPM_TIS_ACCESS_VALID | TPM_TIS_ACCESS_ACTIVE_LOC)) {
                break;
            }
            if (ser_hal_time_ms() >= loc_deadline) {
                return SER_ETIMEDOUT;
            }
            ser_hal_delay_us(1000U);
        }
    }

    /*
     * Read the vendor/device identity.  This is the presence check that
     * distinguishes "a TPM is fitted and talking" from "MISO is floating
     * high": with no TPM present the pull-up makes every read return 0xFF
     * [REF-TCG-002 §7.4.5, last paragraph on master-abort behaviour].
     */
    uint8_t id[4] = {0U, 0U, 0U, 0U};
    rc = tis_xfer(tis, true, TPM_TIS_REG_DID_VID, id, sizeof(id));
    if (rc != SER_OK) {
        return rc;
    }
    tis->did_vid = (uint32_t)id[0]
                   | ((uint32_t)id[1] << 8)
                   | ((uint32_t)id[2] << 16)
                   | ((uint32_t)id[3] << 24);
    if ((tis->did_vid == 0xFFFFFFFFUL) || (tis->did_vid == 0UL)) {
        return SER_ENODEV;
    }

    rc = tis_read8(tis, TPM_TIS_REG_RID, &tis->rid);
    if (rc != SER_OK) {
        return rc;
    }

    tis->open = true;
    ser_hal_log("tpm: DID_VID=0x%08lx RID=0x%02x locality=%u\n",
                (unsigned long)tis->did_vid,
                (unsigned)tis->rid,
                (unsigned)tis->locality);
    return SER_OK;
}

int ser_tpm_tis_close(ser_tpm_tis_t *tis) {
    if ((tis == NULL) || !tis->open) {
        return SER_EINVAL;
    }
    /* Writing 1 to activeLocality relinquishes control [REF-TCG-002 Table 20]. */
    const int rc = tis_write8(tis, TPM_TIS_REG_ACCESS,
                              TPM_TIS_ACCESS_ACTIVE_LOC);
    tis->open = false;
    return rc;
}

int ser_tpm_tis_transmit(ser_tpm_tis_t *tis,
                         const uint8_t *cmd,
                         size_t cmd_len,
                         uint8_t *rsp,
                         size_t rsp_cap,
                         size_t *rsp_len,
                         uint32_t timeout_ms) {
    if ((tis == NULL) || !tis->open || (cmd == NULL) || (rsp == NULL) ||
        (rsp_len == NULL) || (cmd_len < 10U) || (rsp_cap < 10U)) {
        /* 10 bytes is the smallest legal TPM 2.0 command or response header:
         * tag (2) + size (4) + commandCode/responseCode (4). */
        return SER_EINVAL;
    }

    *rsp_len = 0U;

    int rc = tis_command_ready(tis);
    if (rc != SER_OK) {
        return rc;
    }

    /* ---- Command phase: burst into TPM_DATA_FIFO_0 ---------------------- */
    size_t sent = 0U;
    while (sent < cmd_len) {
        uint32_t sts = 0U;

        /* burstCount is only meaningful once the TPM reports it; poll for a
         * non-zero value rather than assuming one [REF-TCG-002 Table 21]. */
        const uint64_t burst_deadline =
            ser_hal_time_ms() + TPM_TIS_TIMEOUT_A_MS;
        uint16_t burst = 0U;
        for (;;) {
            rc = tis_read_sts(tis, &sts);
            if (rc != SER_OK) {
                return rc;
            }
            burst = tis_burst_count(sts);
            if (burst != 0U) {
                break;
            }
            if (ser_hal_time_ms() >= burst_deadline) {
                return SER_ETIMEDOUT;
            }
            ser_hal_delay_us(100U);
        }

        size_t chunk = cmd_len - sent;
        if (chunk > (size_t)burst) {
            chunk = (size_t)burst;
        }
        if (chunk > TPM_TIS_MAX_XFER) {
            chunk = TPM_TIS_MAX_XFER;
        }

        /*
         * The last byte of the command is written on its own.  Until it is
         * written the TPM must keep Expect set; writing it clears Expect and
         * is what makes the "did the TPM get the whole command" check below
         * meaningful [REF-TCG-002 Table 21, Expect].
         */
        if (((sent + chunk) == cmd_len) && (chunk > 1U)) {
            chunk -= 1U;
        }

        /* tis_xfer takes a non-const pointer because it shares the read path;
         * the write direction does not modify the buffer. */
        uint8_t scratch[TPM_TIS_MAX_XFER];
        memcpy(scratch, &cmd[sent], chunk);
        rc = tis_xfer(tis, false, TPM_TIS_REG_DATA_FIFO, scratch, chunk);
        if (rc != SER_OK) {
            return rc;
        }
        sent += chunk;

        if (sent < cmd_len) {
            /* More to send: the TPM must still be expecting data. */
            rc = tis_wait_sts(tis, TPM_TIS_STS_EXPECT, true,
                              TPM_TIS_TIMEOUT_C_MS, &sts);
            if (rc != SER_OK) {
                return rc;
            }
        }
    }

    /* All bytes written: Expect must now be clear, or the TPM and this
     * driver disagree about the command length. */
    {
        uint32_t sts = 0U;
        rc = tis_wait_sts(tis, TPM_TIS_STS_VALID, false,
                          TPM_TIS_TIMEOUT_C_MS, &sts);
        if (rc != SER_OK) {
            return rc;
        }
        if ((sts & TPM_TIS_STS_EXPECT) != 0U) {
            (void)tis_command_ready(tis);
            return SER_EPROTO;
        }
    }

    /* ---- Execute -------------------------------------------------------- */
    rc = tis_write8(tis, TPM_TIS_REG_STS, TPM_TIS_STS_GO);
    if (rc != SER_OK) {
        return rc;
    }

    rc = tis_wait_sts(tis, TPM_TIS_STS_DATA_AVAIL, true, timeout_ms, NULL);
    if (rc != SER_OK) {
        /* Leave the TPM in a defined state so the next command can proceed. */
        (void)tis_command_ready(tis);
        return rc;
    }

    /* ---- Response phase ------------------------------------------------- */
    /*
     * Read the 10-byte header first so the real response length is known;
     * reading past the end of a response is what makes a TIS driver hang
     * waiting on dataAvail that will never come back.
     */
    size_t got = 0U;
    while (got < 10U) {
        uint32_t sts = 0U;
        rc = tis_read_sts(tis, &sts);
        if (rc != SER_OK) {
            return rc;
        }
        uint16_t burst = tis_burst_count(sts);
        if (burst == 0U) {
            ser_hal_delay_us(100U);
            continue;
        }
        size_t chunk = 10U - got;
        if (chunk > (size_t)burst) {
            chunk = (size_t)burst;
        }
        if (chunk > TPM_TIS_MAX_XFER) {
            chunk = TPM_TIS_MAX_XFER;
        }
        rc = tis_xfer(tis, true, TPM_TIS_REG_DATA_FIFO, &rsp[got], chunk);
        if (rc != SER_OK) {
            return rc;
        }
        got += chunk;
    }

    /* responseSize is bytes 2..5, big-endian [REF-TCG-002 §7.5]. */
    const size_t rsp_size = ((size_t)rsp[2] << 24)
                            | ((size_t)rsp[3] << 16)
                            | ((size_t)rsp[4] << 8)
                            | (size_t)rsp[5];
    if (rsp_size < 10U) {
        (void)tis_command_ready(tis);
        return SER_EPROTO;
    }
    if (rsp_size > rsp_cap) {
        (void)tis_command_ready(tis);
        return SER_ENOSPC;
    }

    while (got < rsp_size) {
        uint32_t sts = 0U;
        rc = tis_read_sts(tis, &sts);
        if (rc != SER_OK) {
            return rc;
        }
        uint16_t burst = tis_burst_count(sts);
        if (burst == 0U) {
            ser_hal_delay_us(100U);
            continue;
        }
        size_t chunk = rsp_size - got;
        if (chunk > (size_t)burst) {
            chunk = (size_t)burst;
        }
        if (chunk > TPM_TIS_MAX_XFER) {
            chunk = TPM_TIS_MAX_XFER;
        }
        rc = tis_xfer(tis, true, TPM_TIS_REG_DATA_FIFO, &rsp[got], chunk);
        if (rc != SER_OK) {
            return rc;
        }
        got += chunk;
    }

    *rsp_len = got;

    /* Return the TPM to Ready so the next command does not pay for the
     * transition [REF-TCG-002 §6.5.2.5]. */
    (void)tis_command_ready(tis);
    return SER_OK;
}
