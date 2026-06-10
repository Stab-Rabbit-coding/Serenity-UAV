/**
 * @file    mal_telemetry.h
 * @brief   Malcolm GCS — MAVLink telemetry parser and forwarder API.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 * Revision: Q1 (2026-06-10)
 *
 * This module parses inbound MAVLink telemetry frames received on any of
 * Malcolm's radio links (SiK, LoRa, WiFi, RCRS-49) and:
 *
 *   1. Publishes the current aircraft position to the tracking software via
 *      a UDP datagram on MAL_TRACKER_UDP_PORT.
 *   2. Forwards all MAVLink frames to the host PC via the USB CDC-ECM link
 *      (mavlink-router handles this; this module handles the position extract).
 *   3. Monitors MAVLink heartbeat and raises a link-lost flag if no heartbeat
 *      is received within MAL_HEARTBEAT_TIMEOUT_MS.
 *
 * Parsed message types:
 *   HEARTBEAT            (#0)  — link health monitoring
 *   GLOBAL_POSITION_INT  (#33) — aircraft lat/lon/alt → tracking software
 *   ATTITUDE             (#30) — aircraft roll/pitch/yaw → optional display
 *   SYS_STATUS           (#1)  — battery voltage and load
 */

#ifndef MAL_TELEMETRY_H
#define MAL_TELEMETRY_H

#include <stdint.h>
#include <time.h>

/* ---------------------------------------------------------------------------
 * Types
 * ---------------------------------------------------------------------------*/

/** Aircraft global position (from GLOBAL_POSITION_INT). */
typedef struct {
    int32_t  lat_degE7;    /**< Latitude  × 10^7 (WGS-84 degrees × 1e7). */
    int32_t  lon_degE7;    /**< Longitude × 10^7.                          */
    int32_t  alt_mm;       /**< Altitude MSL (millimetres).                */
    int32_t  relative_alt_mm; /**< Altitude above home (millimetres).      */
    int16_t  vx_cms;       /**< Ground speed N component (cm/s).           */
    int16_t  vy_cms;       /**< Ground speed E component (cm/s).           */
    int16_t  vz_cms;       /**< Ground speed D component (cm/s, +down).    */
    uint16_t hdg_cdeg;     /**< Heading (centidegrees, 0–36000, UINT16_MAX = unknown). */
} mal_aircraft_pos_t;

/** Telemetry link status. */
typedef struct {
    int         link_ok;           /**< Non-zero if link is alive.           */
    struct timespec last_heartbeat; /**< Monotonic time of last heartbeat.   */
    uint32_t    msgs_received;     /**< Total MAVLink frames received.       */
    uint32_t    msgs_forwarded;    /**< Total frames forwarded to host PC.   */
} mal_telemetry_status_t;

/* ---------------------------------------------------------------------------
 * Initialisation
 * ---------------------------------------------------------------------------*/

/**
 * @brief  Initialise telemetry parser and open UDP socket to tracking software.
 *
 * @return 0 on success; −1 on failure (errno set).
 */
int mal_telemetry_init(void);

/**
 * @brief  Close all sockets and release resources.
 */
void mal_telemetry_deinit(void);

/* ---------------------------------------------------------------------------
 * Frame processing
 * ---------------------------------------------------------------------------*/

/**
 * @brief  Feed raw bytes from any radio link into the MAVLink parser.
 *
 * Parse incrementally; call repeatedly as bytes arrive from UART, UDP,
 * or SPI reads.  Internally invokes message handlers and publishes position
 * updates over UDP.
 *
 * @param[in] buf   Pointer to received bytes.
 * @param[in] len   Number of bytes.
 */
void mal_telemetry_feed(const uint8_t *buf, size_t len);

/* ---------------------------------------------------------------------------
 * State readback
 * ---------------------------------------------------------------------------*/

/**
 * @brief  Return the most recently received aircraft position.
 *
 * @param[out] pos  Populated with latest position; zeroed if no fix yet.
 * @return 1 if a position has been received since init; 0 if no data yet.
 */
int mal_telemetry_get_position(mal_aircraft_pos_t *pos);

/**
 * @brief  Return the current telemetry link status.
 *
 * @param[out] status  Populated with current link status.
 */
void mal_telemetry_get_status(mal_telemetry_status_t *status);

/**
 * @brief  Return non-zero if the heartbeat timeout has expired (link lost).
 */
int mal_telemetry_is_link_lost(void);

#endif /* MAL_TELEMETRY_H */
