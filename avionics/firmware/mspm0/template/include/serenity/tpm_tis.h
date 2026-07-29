/**
 * @file    tpm_tis.h
 * @brief   Infineon OPTIGA SLB 9670 TPM 2.0 — TIS-over-SPI transport layer.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * This is the byte-pipe half of the TPM stack: it moves a marshalled TPM 2.0
 * command buffer into the TPM and pulls the response buffer back out.  It
 * knows nothing about TPM commands themselves — that is `tpm2.h`.
 *
 * The SLB 9670 datasheet (Infineon Rev 1.4, 2018-12-07, in
 * `avionics/datasheets/SLB_9670VQ20_Infineon.pdf`) specifies the part but
 * deliberately does NOT specify the host interface protocol; it defers to the
 * TCG specifications in its own References list.  Every register offset,
 * status bit and wire-protocol rule implemented here therefore comes from the
 * TCG PC Client Platform TPM Profile [REF-TCG-002], not from the datasheet:
 *
 *   - Register offsets ...................... [REF-TCG-002 §6.5.2, Table 19]
 *   - TPM_ACCESS_x bit definitions ........... [REF-TCG-002 §6.5.2.2, Table 20]
 *   - TPM_STS_x bit definitions .............. [REF-TCG-002 §6.5.2.5, Table 21]
 *   - Interface timeouts A/B/C/D ............. [REF-TCG-002 §6.5.1.4, Table 18]
 *   - SPI bit protocol (header layout) ....... [REF-TCG-002 §7.4.6, Table 48]
 *   - SPI flow control / wait states ......... [REF-TCG-002 §7.4.5]
 *   - Big-endian payload byte ordering ....... [REF-TCG-002 §7.5]
 *
 * From the datasheet itself we take only the electrical envelope:
 * SPI clock <= 43 MHz at VDD 3.3 V with slew >= 1 V/ns, and mode 0
 * [REF-SENSOR-011; SLB 9670 datasheet Table 13].
 */

#ifndef SERENITY_TPM_TIS_H_
#define SERENITY_TPM_TIS_H_

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ---------------------------------------------------------------------------
 * TIS register map, locality 0
 *
 * [REF-TCG-002 §6.5.2 Table 19].  The SPI header carries a 24-bit address
 * that is the low 24 bits of the memory-mapped address 0xFED4_xxxx; the
 * 0xD4_0000 base below is that truncation, and locality n adds n * 0x1000
 * [REF-TCG-002 §7.4.6 rule 5, §6.4 Table 9].
 * ---------------------------------------------------------------------------*/

#define TPM_TIS_SPI_BASE        (0x00D40000UL)  /**< Low 24 bits of 0xFED40000. */
#define TPM_TIS_LOCALITY_STRIDE (0x00001000UL)  /**< Address delta per locality. */

#define TPM_TIS_REG_ACCESS      (0x0000U)   /**< TPM_ACCESS_x,    1 byte.      */
#define TPM_TIS_REG_INT_ENABLE  (0x0008U)   /**< TPM_INT_ENABLE_x, 4 bytes.    */
#define TPM_TIS_REG_STS         (0x0018U)   /**< TPM_STS_x,       4 bytes.     */
#define TPM_TIS_REG_DATA_FIFO   (0x0024U)   /**< TPM_DATA_FIFO_x, 1 byte port. */
#define TPM_TIS_REG_DID_VID     (0x0F00U)   /**< TPM_DID_VID_x,   4 bytes.     */
#define TPM_TIS_REG_RID         (0x0F04U)   /**< TPM_RID_x,       1 byte.      */

/* TPM_ACCESS_x bits [REF-TCG-002 Table 20]. */
#define TPM_TIS_ACCESS_VALID        (0x80U) /**< tpmRegValidSts.               */
#define TPM_TIS_ACCESS_ACTIVE_LOC   (0x20U) /**< activeLocality.               */
#define TPM_TIS_ACCESS_BEEN_SEIZED  (0x10U) /**< beenSeized.                   */
#define TPM_TIS_ACCESS_REQUEST_USE  (0x02U) /**< requestUse.                   */

/* TPM_STS_x bits [REF-TCG-002 Table 21]. */
#define TPM_TIS_STS_VALID           (0x80U) /**< stsValid (bit 7).             */
#define TPM_TIS_STS_COMMAND_READY   (0x40U) /**< commandReady (bit 6).         */
#define TPM_TIS_STS_GO              (0x20U) /**< tpmGo (bit 5).                */
#define TPM_TIS_STS_DATA_AVAIL      (0x10U) /**< dataAvail (bit 4).            */
#define TPM_TIS_STS_EXPECT          (0x08U) /**< Expect (bit 3).               */
#define TPM_TIS_STS_SELF_TEST_DONE  (0x04U) /**< selfTestDone (bit 2).         */

/* Interface timeouts, milliseconds [REF-TCG-002 §6.5.1.4 Table 18]. */
#define TPM_TIS_TIMEOUT_A_MS    (750U)
#define TPM_TIS_TIMEOUT_B_MS    (2000U)
#define TPM_TIS_TIMEOUT_C_MS    (200U)
#define TPM_TIS_TIMEOUT_D_MS    (30U)

/**
 * @brief Maximum bytes in one SPI transaction.
 *
 * [REF-TCG-002 §7.4.6]: "it is legal to transmit any number of bytes of data
 * from 1 byte to 64 bytes", encoded as a zero-based count in header bits 5:0.
 */
#define TPM_TIS_MAX_XFER        (64U)

/**
 * @brief Command/response buffer size.
 *
 * The SLB 9670 advertises a 1420-byte I/O buffer (datasheet "Key Features"),
 * but this firmware never issues a command anywhere near that size — the
 * largest is TPM2_HMAC over a 64-byte digest-plus-header.  256 bytes is
 * generous for every command in `tpm2.h` and keeps two of these buffers well
 * inside the MSPM0G3507's 32 KB SRAM [REF-SENSOR-004].  A command that would
 * exceed it is rejected with SER_ENOSPC rather than truncated.
 */
#define TPM_TIS_BUF_SIZE        (256U)

/**
 * @brief TIS transport context.
 *
 * One instance per TPM.  Every board in this fleet has exactly one.
 */
typedef struct {
    uint8_t  locality;      /**< Locality in use; 0 on all Serenity boards.   */
    bool     open;          /**< True once `ser_tpm_tis_init()` has succeeded.*/
    uint32_t did_vid;       /**< TPM_DID_VID_0 read at init, for the log.     */
    uint8_t  rid;           /**< TPM_RID_0 read at init.                      */
} ser_tpm_tis_t;

/**
 * @brief Reset the TPM, claim locality 0, and read out DID/VID/RID.
 *
 * Drives SER_GPIO_TPM_RST_N low then high — the low-to-high transition is
 * _TPM_INIT for an SPI-packaged TPM [REF-TCG-002 §6.5.1.5 rule 2] — then
 * waits for TPM_ACCESS_0.tpmRegValidSts and requests locality 0.
 *
 * @return SER_OK, SER_ENODEV if the TPM never reports a valid status,
 *         SER_ETIMEDOUT on a TIS timeout, or another negative `SER_E*` code.
 */
int ser_tpm_tis_init(ser_tpm_tis_t *tis);

/**
 * @brief Release locality 0 and put the TPM back to a quiescent state.
 */
int ser_tpm_tis_close(ser_tpm_tis_t *tis);

/**
 * @brief Execute one TPM 2.0 command: write it in, run it, read the response.
 *
 * Implements the full FIFO command sequence: assert commandReady, burst the
 * command into TPM_DATA_FIFO_0 honouring burstCount, verify Expect has
 * cleared, write tpmGo, poll dataAvail, then drain the response.
 *
 * @param tis       Initialised transport context.
 * @param cmd       Marshalled TPM 2.0 command, big-endian [REF-TCG-002 §7.5].
 * @param cmd_len   Command length in bytes; must equal the commandSize field.
 * @param rsp       Response buffer.
 * @param rsp_cap   Capacity of @p rsp.
 * @param rsp_len   Out: bytes written to @p rsp.
 * @param timeout_ms Command execution budget; TPM_TIS_TIMEOUT_B_MS is the
 *                  TCG default for a long command.
 * @return SER_OK, or a negative `SER_E*` code.  A non-zero TPM responseCode
 *         is NOT an error here — the response is returned intact and it is
 *         `tpm2.c`'s job to decode it.
 */
int ser_tpm_tis_transmit(ser_tpm_tis_t *tis,
                         const uint8_t *cmd,
                         size_t cmd_len,
                         uint8_t *rsp,
                         size_t rsp_cap,
                         size_t *rsp_len,
                         uint32_t timeout_ms);

#ifdef __cplusplus
}
#endif

#endif /* SERENITY_TPM_TIS_H_ */
