/**
 * @file    main.c
 * @brief   Serenity UAV CN node daemon — entry point.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * The CN node (Communications/Payload) daemon runs on each of the four
 * Cape-B / AM6254 PocketBeagle 2 Industrial nodes.  This file provides:
 *
 *   - Command-line argument parsing.
 *   - Signal handling (SIGTERM / SIGINT for clean shutdown).
 *   - Driver initialisation: XCVR-49MHZ-1 KISS/AX.25 link.
 *   - Placeholder loops for the CAN FD, RS-485, MIL-STD-1553, Ethernet,
 *     and log subsystems (Phase 7 implementation).
 *
 * Usage:
 *   serenity-cn [OPTIONS]
 *
 *   -u <device>   UART device for XCVR-49MHZ-1 (default: /dev/ttyS2)
 *   -i <bus>      I²C bus number for Si5351A DDS (default: 1)
 *   -g <chip>     GPIO chip for PTT_N (default: /dev/gpiochip0)
 *   -l <line>     GPIO line offset for PTT_N (default: 10)
 *   -c <channel>  Initial RCRS channel 0–4 (default: 0 = 49.830 MHz)
 *   -h            Print this help and exit
 *
 * Exit codes:
 *   0  Clean shutdown (SIGTERM / SIGINT received).
 *   1  Fatal initialisation error.
 */

/* _GNU_SOURCE enables getopt(), sigaction(), and other POSIX/GNU extensions. */
#define _GNU_SOURCE

#include "xcvr_kiss.h"

#include <errno.h>
#include <limits.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

/* ---------------------------------------------------------------------------
 * Default configuration values
 * ---------------------------------------------------------------------------*/

#define DEFAULT_UART_DEV      "/dev/ttyS2"
#define DEFAULT_I2C_BUS       (1)
#define DEFAULT_GPIO_CHIP     "/dev/gpiochip0"
#define DEFAULT_PTT_LINE      (10U)
#define DEFAULT_RCRS_CHANNEL  (0U)

/* ---------------------------------------------------------------------------
 * Shutdown flag — set by signal handler
 * ---------------------------------------------------------------------------*/

/** Accessed from signal handler and main loop — volatile for visibility. */
static volatile sig_atomic_t g_shutdown = 0;

static void sig_handler(int sig)
{
    (void)sig;
    g_shutdown = 1;
}

/* ---------------------------------------------------------------------------
 * RX callback — invoked by the XCVR driver's RX thread
 * ---------------------------------------------------------------------------*/

/**
 * @brief Receive callback: called for every decoded AX.25 frame from the
 *        49 MHz RCRS link.
 *
 * In Phase 7 this function will forward the frame to the AX.25 stack,
 * authenticate the HMAC, and log it via the CN node log subsystem.
 * For Phase 6, it prints a summary to stderr for ground-test verification.
 */
static void on_rx_frame(const kiss_frame_t *frame, void *userdata)
{
    (void)userdata;

    (void)fprintf(stderr,
                  "xcvr_rx: port=%u type=0x%02X len=%zu\n",
                  frame->port,
                  frame->type,
                  frame->data_len);
}

/* ---------------------------------------------------------------------------
 * Argument parsing helpers
 * ---------------------------------------------------------------------------*/

static void print_usage(const char *prog)
{
    (void)fprintf(stderr,
        "Usage: %s [OPTIONS]\n"
        "  -u <device>   UART device for XCVR-49MHZ-1 (default: %s)\n"
        "  -i <bus>      I2C bus number for Si5351A   (default: %d)\n"
        "  -g <chip>     GPIO chip path for PTT_N     (default: %s)\n"
        "  -l <line>     GPIO line offset for PTT_N   (default: %u)\n"
        "  -c <channel>  Initial RCRS channel 0-4     (default: %u = 49.830 MHz)\n"
        "  -h            Print this help and exit\n",
        prog,
        DEFAULT_UART_DEV,
        DEFAULT_I2C_BUS,
        DEFAULT_GPIO_CHIP,
        DEFAULT_PTT_LINE,
        DEFAULT_RCRS_CHANNEL);
}

/**
 * @brief Parse a non-negative integer from a string.
 *
 * @return Parsed value, or -1 on error.
 */
static long parse_int(const char *str)
{
    if (str == NULL || str[0] == '\0') { return -1; }
    char *end = NULL;
    errno = 0;
    long val = strtol(str, &end, 10);
    if (errno != 0 || *end != '\0' || val < 0) { return -1; }
    return val;
}

/* ---------------------------------------------------------------------------
 * main
 * ---------------------------------------------------------------------------*/

int main(int argc, char *argv[])
{
    /* --- Configuration with defaults --- */
    const char   *uart_dev      = DEFAULT_UART_DEV;
    int           i2c_bus       = DEFAULT_I2C_BUS;
    const char   *gpio_chip     = DEFAULT_GPIO_CHIP;
    unsigned int  ptt_line      = DEFAULT_PTT_LINE;
    unsigned int  rcrs_channel  = DEFAULT_RCRS_CHANNEL;

    /* --- Argument parsing --- */
    int opt;
    while ((opt = getopt(argc, argv, "u:i:g:l:c:h")) != -1) {
        switch (opt) {
            case 'u':
                uart_dev = optarg;
                break;
            case 'i': {
                long v = parse_int(optarg);
                if (v < 0 || v > 31) {
                    (void)fprintf(stderr, "Invalid I2C bus: %s\n", optarg);
                    return 1;
                }
                i2c_bus = (int)v;
                break;
            }
            case 'g':
                gpio_chip = optarg;
                break;
            case 'l': {
                long v = parse_int(optarg);
                if (v < 0 || v > 511) {
                    (void)fprintf(stderr, "Invalid GPIO line: %s\n", optarg);
                    return 1;
                }
                ptt_line = (unsigned int)v;
                break;
            }
            case 'c': {
                long v = parse_int(optarg);
                if (v < 0 || (unsigned long)v >= SI5351_RCRS_NUM_CHANNELS) {
                    (void)fprintf(stderr,
                                  "Invalid RCRS channel: %s (must be 0-%u)\n",
                                  optarg,
                                  SI5351_RCRS_NUM_CHANNELS - 1U);
                    return 1;
                }
                rcrs_channel = (unsigned int)v;
                break;
            }
            case 'h':
                print_usage(argv[0]);
                return 0;
            default:
                print_usage(argv[0]);
                return 1;
        }
    }

    /* --- Signal handling --- */
    struct sigaction sa;
    (void)memset(&sa, 0, sizeof(sa));
    sa.sa_handler = sig_handler;
    (void)sigemptyset(&sa.sa_mask);
    (void)sigaction(SIGTERM, &sa, NULL);
    (void)sigaction(SIGINT,  &sa, NULL);

    /* --- Initialise XCVR-49MHZ-1 driver --- */
    xcvr_kiss_config_t xcvr_cfg = {
        .uart_dev        = uart_dev,
        .gpio_chip       = gpio_chip,
        .ptt_gpio_line   = ptt_line,
        .si5351_i2c_bus  = i2c_bus,
        .default_channel = rcrs_channel,
        .rx_callback     = on_rx_frame,
        .rx_userdata     = NULL,
    };

    xcvr_kiss_ctx_t *xcvr = NULL;
    int rc = xcvr_kiss_open(&xcvr_cfg, &xcvr);
    if (rc != 0) {
        (void)fprintf(stderr,
                      "serenity-cn: XCVR init failed (%s)\n",
                      strerror(-rc));
        return 1;
    }

    (void)fprintf(stderr,
                  "serenity-cn: XCVR-49MHZ-1 ready — UART %s, channel %u"
                  " (%.3f MHz)\n",
                  uart_dev,
                  rcrs_channel,
                  (double)(49830U + rcrs_channel * 15U) / 1000.0);

    /*
     * Phase 6 main loop — minimal: runs until SIGTERM/SIGINT.
     *
     * Phase 7 will add:
     *   - CAN FD heartbeat and telemetry forwarding
     *   - MIL-STD-1553 bus controller / remote terminal tasks
     *   - RS-485 inter-board messaging
     *   - Ethernet RSTP ring management
     *   - Signed-log write via CPLD write-blocker interface
     *   - TPM-bound HMAC on all outbound AX.25 payloads
     */
    while (g_shutdown == 0) {
        /* Future: select() / epoll on all bus file descriptors. */
        sleep(1);
    }

    (void)fprintf(stderr, "serenity-cn: shutting down.\n");
    xcvr_kiss_close(xcvr);
    return 0;
}
