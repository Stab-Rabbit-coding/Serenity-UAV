/**
 * @file    ax25_types.h
 * @brief   AX.25 v2.2 frame type definitions and address constants.
 *
 * Copyright 2026 Steve Griffing
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Reference: AX.25 Link Access Protocol for Amateur Packet Radio, Version 2.2,
 *   Tucson Amateur Packet Radio (TAPR) / ARRL, 1998 [REF-PROTO-001].
 *   Available: https://www.tapr.org/pdf/AX25.2.2.pdf
 *
 * Only the subset of AX.25 needed for the Serenity UAV 49 MHz link (Commo,
 * 47 CFR Part 15 §15.235 [REF-FCC-003]) is defined here.  The UAV uses
 * UI (unnumbered information) frames for telemetry and command packets;
 * connection-oriented modes are not required.
 *
 * AX.25 address field:
 *   Each callsign occupies 7 bytes: 6 bytes of ASCII callsign (left-justified,
 *   space-padded, each byte shifted left by 1) followed by 1 SSID byte.
 *   Bit 0 of every address byte is 0 except for the last address byte in the
 *   complete address field, which has bit 0 = 1 (end-of-address flag).
 *
 * Frame structure (UI frame):
 *   [Destination address — 7 bytes]
 *   [Source address — 7 bytes]
 *   [0..8 Digipeater addresses — 7 bytes each]
 *   [Control — 1 byte: 0x03 for UI]
 *   [PID — 1 byte: 0xF0 = no layer-3 protocol]
 *   [Information — 0..256 bytes]
 */

#ifndef AVIONICS_FIRMWARE_COMMON_INCLUDE_AX25_TYPES_H_
#define AVIONICS_FIRMWARE_COMMON_INCLUDE_AX25_TYPES_H_

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ---------------------------------------------------------------------------
 * Constants
 * ---------------------------------------------------------------------------*/

/** Length of one AX.25 address field (callsign + SSID byte). */
#define AX25_ADDR_LEN      (7U)

/** Maximum number of digipeater hops. */
#define AX25_MAX_DIGI      (8U)

/** Control field value for UI (unnumbered information) frames. */
#define AX25_CTRL_UI       ((uint8_t)0x03U)

/** Protocol ID: no layer-3 protocol (raw data / telemetry). */
#define AX25_PID_NO_L3     ((uint8_t)0xF0U)

/** Maximum information field length per AX.25 v2.2 §2.1. */
#define AX25_MAX_INFO_LEN  (256U)

/**
 * Maximum total AX.25 frame length (excl. HDLC flags and FCS, which are
 * added/stripped by the modem).  Destination + source + 8 digi + ctrl + pid
 * + info = 7 + 7 + 56 + 1 + 1 + 256 = 328 bytes.
 */
#define AX25_MAX_FRAME_LEN (328U)

/* ---------------------------------------------------------------------------
 * Address field
 * ---------------------------------------------------------------------------*/

/**
 * @brief One AX.25 address element (callsign + SSID).
 *
 * The @c raw field contains the on-wire encoding: each character shifted left
 * by one bit with the SSID byte as the final byte.  Use ax25_addr_encode()
 * and ax25_addr_decode() to convert between printable callsigns and this
 * representation.
 */
typedef struct {
    uint8_t raw[AX25_ADDR_LEN]; /**< 6 shifted-ASCII chars + SSID byte */
} ax25_addr_t;

/* ---------------------------------------------------------------------------
 * UI frame
 * ---------------------------------------------------------------------------*/

/**
 * @brief Decoded AX.25 UI frame.
 *
 * Populated by ax25_ui_decode() after stripping HDLC flags and FCS (the modem
 * strips these before handing the frame to the CN node via KISS).
 */
typedef struct {
    ax25_addr_t dest;                /**< Destination station address */
    ax25_addr_t src;                 /**< Source station address */
    ax25_addr_t digi[AX25_MAX_DIGI]; /**< Digipeater addresses (if any) */
    uint8_t     n_digi; /**< Number of digipeaters present (0..8) */
    uint8_t     ctrl;   /**< Control byte (should be CTRL_UI = 0x03) */
    uint8_t     pid;    /**< Protocol ID byte */
    uint8_t     info[AX25_MAX_INFO_LEN]; /**< Information field payload */
    uint16_t    info_len;                /**< Number of valid info bytes */
} ax25_ui_frame_t;

/* ---------------------------------------------------------------------------
 * SSID field bit masks (in the raw 7th byte of each address)
 * ---------------------------------------------------------------------------*/

/** Command/Response bit (bit 7 of SSID byte). */
#define AX25_SSID_CR_BIT   ((uint8_t)0x80U)

/** Reserved bit 1 (must be 1 per spec). */
#define AX25_SSID_RES1_BIT ((uint8_t)0x40U)

/** Reserved bit 2 (must be 1 per spec). */
#define AX25_SSID_RES2_BIT ((uint8_t)0x20U)

/** SSID value mask (bits 4..1 of the SSID byte → values 0..15). */
#define AX25_SSID_MASK     ((uint8_t)0x1EU)

/** End-of-address flag: set in the last address byte of the whole field. */
#define AX25_SSID_EOA_BIT  ((uint8_t)0x01U)

/* ---------------------------------------------------------------------------
 * Station identifier constants for the Serenity UAV
 *
 * AX.25 is used here only as a frame format; the 49 MHz RF link itself is
 * authorized under 47 CFR Part 15 §15.235 [REF-FCC-003], a license-exempt
 * unlicensed-intentional-radiator rule, NOT the Amateur Radio Service.
 * No FCC amateur license (47 CFR Part 97) is required to operate this link,
 * and these AX.25 address fields are station identifiers for protocol
 * addressing only — they are not amateur callsigns [REF-PROTO-001].
 * Replace SERENITY_CALLSIGN with the assigned station identifier and set
 * the SSID to the node number (0–15) as appropriate.
 *
 * IMPORTANT: Aircraft registration display is a separate requirement under
 * 14 CFR Part 48 §48.205 [REF-FAA-001] (NOT Part 47, which applies to manned
 * aircraft), and is independent of this AX.25 station identifier.
 * ---------------------------------------------------------------------------*/

/** Ground control station identifier (AX.25 addressing only). */
#define AX25_CALLSIGN_GCS  "GCS000"

/** UAV station identifier placeholder — replace with assigned identifier. */
#define AX25_CALLSIGN_UAV  "UAV000"

#ifdef __cplusplus
}
#endif

#endif  // AVIONICS_FIRMWARE_COMMON_INCLUDE_AX25_TYPES_H_
