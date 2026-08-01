/**
 * @file    skipper_telemetry.c
 * @brief   Skipper GCS — MAVLink telemetry parser and forwarder implementation.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 * Revision: R (2026-06-11)
 *
 * See skipper_telemetry.h for API documentation and parsed message list.
 *
 * Implementation notes:
 *   - Uses the MAVLink C library (mavlink2) header-only parser.
 *     Include path must contain mavlink/common/mavlink.h.
 *     Build with: cmake option MAVLINK_INCLUDE_DIR=/path/to/mavlink/headers
 *   - Position UDP publish: datagram to 127.0.0.1:SKIPPER_TRACKER_UDP_PORT,
 *     JSON-encoded for tracker.py.  Format:
 *       {"lat_degE7":<int>,"lon_degE7":<int>,"alt_mm":<int>,
 *        "vx_cms":<int>,"vy_cms":<int>,"hdg_cdeg":<int>}
 *   - Thread safety: not thread-safe; call from a single reader task.
 */

#define _GNU_SOURCE

#include "skipper_telemetry.h"
#include "skipper_config.h"

#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <time.h>
#include <unistd.h>

/*
 * MAVLink C library — header-only include.
 * If the build system has not resolved this path yet, the build will fail
 * with a clear error message rather than silently missing functionality.
 */
#include <mavlink/common/mavlink.h>

/* ---------------------------------------------------------------------------
 * Internal state
 * ---------------------------------------------------------------------------*/

/** MAVLink parser state machine (one per GCS node). */
static mavlink_message_t s_msg;
static mavlink_status_t  s_mav_status;

/** Latest aircraft position (protected by calling convention — single thread).
 */
static skipper_aircraft_pos_t s_aircraft_pos;
static int                    s_has_position = 0;

/** Link status. */
static skipper_telemetry_status_t s_status;

/** UDP socket to tracking software. */
static int                s_udp_fd = -1;
static struct sockaddr_in s_tracker_addr;

/* ---------------------------------------------------------------------------
 * Internal helpers
 * ---------------------------------------------------------------------------*/

/**
 * @brief  Handle a fully-parsed MAVLink GLOBAL_POSITION_INT message.
 */
static void handle_global_position(const mavlink_message_t *msg) {
    mavlink_global_position_int_t gpi;
    mavlink_msg_global_position_int_decode(msg, &gpi);

    s_aircraft_pos.lat_degE7 = gpi.lat;
    s_aircraft_pos.lon_degE7 = gpi.lon;
    s_aircraft_pos.alt_mm = gpi.alt;
    s_aircraft_pos.relative_alt_mm = gpi.relative_alt;
    s_aircraft_pos.vx_cms = gpi.vx;
    s_aircraft_pos.vy_cms = gpi.vy;
    s_aircraft_pos.vz_cms = gpi.vz;
    s_aircraft_pos.hdg_cdeg = gpi.hdg;
    s_has_position = 1;

    /* Publish position to tracker.py via UDP JSON datagram. */
    char json[256];
    int  len = snprintf(json, sizeof(json),
                        "{\"lat_degE7\":%d,\"lon_degE7\":%d,\"alt_mm\":%d,"
                        "\"vx_cms\":%d,\"vy_cms\":%d,\"hdg_cdeg\":%u}",
                        gpi.lat, gpi.lon, gpi.alt, gpi.vx, gpi.vy, gpi.hdg);

    if (s_udp_fd >= 0 && len > 0) {
        sendto(s_udp_fd, json, (size_t)len, 0,
               (const struct sockaddr *)&s_tracker_addr,
               sizeof(s_tracker_addr));
    }
}

/**
 * @brief  Handle a fully-parsed HEARTBEAT message.
 */
static void handle_heartbeat(const mavlink_message_t *msg) {
    (void)msg; /* Source sysid already checked before dispatch. */
    clock_gettime(CLOCK_MONOTONIC, &s_status.last_heartbeat);
    s_status.link_ok = 1;
}

/**
 * @brief  Dispatch a fully-parsed MAVLink message to the appropriate handler.
 *
 * @note   Sysid filtering only — this does NOT verify the MAVLink v2
 *         [REF-PROTO-002] HMAC-SHA256 message signature, despite
 *         SKIPPER_TPM_KEY_HANDLE (skipper_config.h) provisioning a TPM key slot
 * for that purpose.  CLAUDE.md requires every message, internal and external,
 * to be digitally signed and authenticated [REF-NIST-001 §2.1, §2.2].  Tracked
 * as an open functional gap in
 *         TODO.md §0.5 — do not treat sysid filtering as authentication.
 */
static void dispatch_message(const mavlink_message_t *msg) {
    /* Only process messages from the aircraft system. */
    if (msg->sysid != SKIPPER_AIRCRAFT_SYS_ID) {
        return;
    }

    s_status.msgs_received++;

    switch (msg->msgid) {
        case MAVLINK_MSG_ID_HEARTBEAT:
            handle_heartbeat(msg);
            break;

        case MAVLINK_MSG_ID_GLOBAL_POSITION_INT:
            handle_global_position(msg);
            break;

        default:
            /* Forward unhandled messages silently — mavlink-router relays them.
             */
            break;
    }
}

/* ---------------------------------------------------------------------------
 * Public API
 * ---------------------------------------------------------------------------*/

int skipper_telemetry_init(void) {
    memset(&s_aircraft_pos, 0, sizeof(s_aircraft_pos));
    memset(&s_status, 0, sizeof(s_status));
    memset(&s_mav_status, 0, sizeof(s_mav_status));

    /* Open UDP socket for publishing to tracker.py. */
    s_udp_fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (s_udp_fd < 0) {
        perror("skipper_telemetry_init: socket");
        return -1;
    }

    memset(&s_tracker_addr, 0, sizeof(s_tracker_addr));
    s_tracker_addr.sin_family = AF_INET;
    s_tracker_addr.sin_port = htons((uint16_t)SKIPPER_TRACKER_UDP_PORT);
    s_tracker_addr.sin_addr.s_addr = inet_addr("127.0.0.1");

    return 0;
}

void skipper_telemetry_deinit(void) {
    if (s_udp_fd >= 0) {
        close(s_udp_fd);
        s_udp_fd = -1;
    }
}

void skipper_telemetry_feed(const uint8_t *buf, size_t len) {
    for (size_t i = 0U; i < len; i++) {
        if (mavlink_parse_char(MAVLINK_COMM_0, buf[i], &s_msg, &s_mav_status) ==
            1) {
            dispatch_message(&s_msg);
        }
    }
    s_status.msgs_forwarded +=
        (uint32_t)len; /* Approximate; mavlink-router does actual fwd. */
}

int skipper_telemetry_get_position(skipper_aircraft_pos_t *pos) {
    if (pos != NULL) {
        *pos = s_aircraft_pos;
    }
    return s_has_position;
}

void skipper_telemetry_get_status(skipper_telemetry_status_t *status) {
    if (status != NULL) {
        *status = s_status;
    }
}

int skipper_telemetry_is_link_lost(void) {
    if (!s_status.link_ok || s_status.last_heartbeat.tv_sec == 0) {
        return 1;
    }
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);
    long elapsed_ms =
        (now.tv_sec - s_status.last_heartbeat.tv_sec) * 1000L +
        (now.tv_nsec - s_status.last_heartbeat.tv_nsec) / 1000000L;
    return (elapsed_ms > (long)SKIPPER_HEARTBEAT_TIMEOUT_MS) ? 1 : 0;
}
