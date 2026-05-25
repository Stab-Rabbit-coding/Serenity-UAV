/**
 * @file    kiss_types.h
 * @brief   KISS TNC protocol constants and frame types.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * KISS (Keep It Simple, Stupid) is the host-to-TNC protocol used between
 * the CN node (AM6254) and the XCVR-49MHZ-1 physical-layer modem board.
 * The protocol is defined in:
 *
 *   Chepponis, M. K3MC and Karn, P. KA9Q, "The KISS TNC: A Simple
 *   Host-to-TNC Communications Protocol," ARRL 6th Computer Networking
 *   Conference, 1987.  (Widely referred to as "RFC 1055 for packet radio.")
 *
 * Frame format (TNC2 mode, single port):
 *   FEND | TYPE | data bytes (with FEND/FESC escaped) | FEND
 *
 * Escape encoding within the data region:
 *   A literal 0xC0 (FEND) in data is sent as:  0xDB 0xDC  (FESC TFEND)
 *   A literal 0xDB (FESC) in data is sent as:  0xDB 0xDD  (FESC TFESC)
 */

#ifndef KISS_TYPES_H
#define KISS_TYPES_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ---------------------------------------------------------------------------
 * Special byte values
 * ---------------------------------------------------------------------------*/

/** Frame delimiter — marks start and end of every KISS frame. */
#define KISS_FEND   ((uint8_t)0xC0U)

/** Escape byte — the byte that follows modifies the next byte's meaning. */
#define KISS_FESC   ((uint8_t)0xDBU)

/** Transposed FEND — when preceded by FESC, represents a literal 0xC0. */
#define KISS_TFEND  ((uint8_t)0xDCU)

/** Transposed FESC — when preceded by FESC, represents a literal 0xDB. */
#define KISS_TFESC  ((uint8_t)0xDDU)

/* ---------------------------------------------------------------------------
 * Frame type byte (first byte after opening FEND).
 * High nibble = TNC port (0 for single-port devices such as XCVR-49MHZ-1).
 * Low nibble  = command code.
 * ---------------------------------------------------------------------------*/

/** Data frame: payload is a complete AX.25 frame (no HDLC flags/CRC). */
#define KISS_CMD_DATA       ((uint8_t)0x00U)

/** TX delay: sets inter-frame gap in units of 10 ms. */
#define KISS_CMD_TXDELAY    ((uint8_t)0x01U)

/** Persistence: P = data[0] / 256 for CSMA. */
#define KISS_CMD_P          ((uint8_t)0x02U)

/** Slot time: random back-off interval in units of 10 ms. */
#define KISS_CMD_SLOTTIME   ((uint8_t)0x03U)

/** TX tail: time to hold PTT after last byte, in units of 10 ms. */
#define KISS_CMD_TXTAIL     ((uint8_t)0x04U)

/** Full duplex: 0 = half-duplex CSMA (default), 1 = full-duplex. */
#define KISS_CMD_FULLDUPLEX ((uint8_t)0x05U)

/** Set hardware: implementation-specific hardware control. */
#define KISS_CMD_SETHARDWARE ((uint8_t)0x06U)

/** Return: switch TNC from KISS mode back to command mode (not used here). */
#define KISS_CMD_RETURN     ((uint8_t)0xFFU)

/* ---------------------------------------------------------------------------
 * Frame size limits
 * ---------------------------------------------------------------------------*/

/**
 * Maximum AX.25 frame payload size (bytes).
 * AX.25 v2.2 UI frame: up to 256 bytes info field + headers ≈ 330 bytes.
 * Add KISS overhead (worst case every byte escaped): × 2 + 2 FEND = 662.
 * We round up to 1024 for comfortable headroom.
 */
#define KISS_MAX_FRAME_LEN  (1024U)

/** Maximum raw AX.25 content that can be carried in one KISS frame. */
#define KISS_MAX_AX25_LEN   (512U)

/* ---------------------------------------------------------------------------
 * Parsed KISS frame
 * ---------------------------------------------------------------------------*/

/**
 * @brief Decoded KISS frame after de-escaping.
 *
 * After calling kiss_decode(), @c type holds the command nibble and @c data
 * holds the de-escaped payload (the raw AX.25 octets for a data frame).
 */
typedef struct {
    uint8_t  port;                   /**< KISS port (high nibble of type byte) */
    uint8_t  type;                   /**< KISS command code (low nibble of type byte) */
    uint8_t  data[KISS_MAX_AX25_LEN]; /**< De-escaped payload */
    size_t   data_len;               /**< Number of valid bytes in @c data */
} kiss_frame_t;

#ifdef __cplusplus
}
#endif

#endif /* KISS_TYPES_H */
