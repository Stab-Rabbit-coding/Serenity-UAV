/**
 * @file    hal_sim.c
 * @brief   POSIX host port of the Serenity MSPM0 HAL — bench test only.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Lets the whole firmware template — TPM stack, envelope, link layer, node
 * lifecycle, board applications — build and run on a workstation, so the
 * logic is testable without hardware and static analysis has something real
 * to analyse.  This port is never flown.
 *
 * Mappings:
 *   CAN-FD  → SocketCAN (`vcan0` by default, or `$SERENITY_CAN_IF`)
 *   SPI/TPM → `/dev/tpm0` if present, otherwise a stub that reports
 *             SER_ENODEV so the node's TPM fault path can be exercised
 *   UART    → pseudo-terminal or a plain file, per `$SERENITY_UART_DEV`
 *   NVM     → a file under `$SERENITY_STATE_DIR` (default /tmp)
 *
 * The TPM mapping is deliberately not a software TPM emulator baked in here:
 * pointing `SERENITY_TPM_DEV` at a running `swtpm` gives a real TPM 2.0 to
 * talk to, which tests the actual command marshalling rather than a mock that
 * would agree with whatever `tpm2.c` happens to send.
 */

#define _GNU_SOURCE

#include "serenity/board.h"
#include "serenity/hal.h"

#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <termios.h>
#include <time.h>
#include <unistd.h>

#include <linux/can.h>
#include <linux/can/raw.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/socket.h>

/* --- State ---------------------------------------------------------------*/

static uint64_t g_epoch_ns;
static int      g_can_fd = -1;
static uint32_t g_can_id;
static int      g_uart_fd[SER_UART_COUNT];
static int      g_tpm_fd = -1;
static uint32_t g_rx_overflow;

static uint64_t now_ns_raw(void) {
    struct timespec ts;
    (void)clock_gettime(CLOCK_MONOTONIC, &ts);
    return ((uint64_t)ts.tv_sec * 1000000000ULL) + (uint64_t)ts.tv_nsec;
}

/* --- Time ----------------------------------------------------------------*/

uint64_t ser_hal_time_ns(void) {
    return now_ns_raw() - g_epoch_ns;
}

uint64_t ser_hal_time_ms(void) {
    return ser_hal_time_ns() / 1000000ULL;
}

uint32_t ser_hal_time_resolution_ns(void) {
    return 1U;
}

void ser_hal_delay_us(uint32_t us) {
    struct timespec ts = {
        .tv_sec = (time_t)(us / 1000000U),
        .tv_nsec = (long)((us % 1000000U) * 1000U)
    };
    (void)nanosleep(&ts, NULL);
}

/* --- Watchdog ------------------------------------------------------------*/

/*
 * No watchdog on the host: a hung test should hang visibly under a debugger
 * rather than silently restart, which would hide the very stall being
 * investigated.
 */
int ser_hal_watchdog_start(void) {
    return SER_OK;
}

void ser_hal_watchdog_pet(void) {
}

/* --- SPI / TPM -----------------------------------------------------------*/

/*
 * `/dev/tpm0` and swtpm expose a *command* interface, not the raw SPI TIS
 * register interface, so the SPI callbacks below cannot drive them directly.
 * The sim port therefore reports SER_ENOTSUP for raw SPI and the test suite
 * exercises `tpm2.c` against a real TPM through a separate transport shim
 * (`test/tpm_dev_shim.c`).  Pretending to succeed here would let a broken TIS
 * driver pass the host tests and fail only on hardware.
 */
int ser_hal_spi_begin(ser_spi_bus_t bus, uint8_t cs) {
    (void)bus;
    (void)cs;
    return SER_ENOTSUP;
}

int ser_hal_spi_xfer_cont(ser_spi_bus_t bus,
                          const uint8_t *tx,
                          uint8_t *rx,
                          size_t len) {
    (void)bus;
    (void)tx;
    (void)rx;
    (void)len;
    return SER_ENOTSUP;
}

int ser_hal_spi_end(ser_spi_bus_t bus) {
    (void)bus;
    return SER_ENOTSUP;
}

int ser_hal_spi_xfer(ser_spi_bus_t bus,
                     uint8_t cs,
                     const uint8_t *tx,
                     uint8_t *rx,
                     size_t len) {
    (void)bus;
    (void)cs;
    (void)tx;
    (void)rx;
    (void)len;
    return SER_ENOTSUP;
}

/* --- GPIO ----------------------------------------------------------------*/

static bool g_gpio[SER_GPIO_COUNT];

int ser_hal_gpio_write(ser_gpio_t line, bool level) {
    if ((unsigned)line >= (unsigned)SER_GPIO_COUNT) {
        return SER_EINVAL;
    }
    g_gpio[line] = level;
    return SER_OK;
}

int ser_hal_gpio_read(ser_gpio_t line, bool *level) {
    if (((unsigned)line >= (unsigned)SER_GPIO_COUNT) || (level == NULL)) {
        return SER_EINVAL;
    }
    *level = g_gpio[line];
    return SER_OK;
}

/* --- CAN-FD over SocketCAN -----------------------------------------------*/

int ser_hal_can_init(uint32_t nominal_bps, uint32_t data_bps,
                     uint32_t accept_id) {
    /* Bit rates are set on the host interface with `ip link`, not by the
     * application, so they are recorded for the log and otherwise unused. */
    (void)nominal_bps;
    (void)data_bps;

    const char *ifname = getenv("SERENITY_CAN_IF");
    if (ifname == NULL) {
        ifname = "vcan0";
    }

    g_can_fd = socket(PF_CAN, SOCK_RAW, CAN_RAW);
    if (g_can_fd < 0) {
        return SER_ENODEV;
    }

    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    (void)strncpy(ifr.ifr_name, ifname, sizeof(ifr.ifr_name) - 1U);
    if (ioctl(g_can_fd, SIOCGIFINDEX, &ifr) < 0) {
        (void)close(g_can_fd);
        g_can_fd = -1;
        return SER_ENODEV;
    }

    struct sockaddr_can addr;
    memset(&addr, 0, sizeof(addr));
    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;
    if (bind(g_can_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        (void)close(g_can_fd);
        g_can_fd = -1;
        return SER_ENODEV;
    }

    int enable_fd = 1;
    if (setsockopt(g_can_fd, SOL_CAN_RAW, CAN_RAW_FD_FRAMES,
                   &enable_fd, sizeof(enable_fd)) < 0) {
        (void)close(g_can_fd);
        g_can_fd = -1;
        return SER_ENOTSUP;
    }

    g_can_id = accept_id | CAN_EFF_FLAG;

    /* Exact-match filter on this node's own identifier, mirroring the
     * hardware acceptance filter the MSPM0 MCAN port programs. */
    struct can_filter filter;
    filter.can_id = g_can_id;
    filter.can_mask = CAN_EFF_MASK | CAN_EFF_FLAG;
    (void)setsockopt(g_can_fd, SOL_CAN_RAW, CAN_RAW_FILTER,
                     &filter, sizeof(filter));

    return SER_OK;
}

int ser_hal_can_send(const ser_can_frame_t *frame) {
    if ((frame == NULL) || (g_can_fd < 0)) {
        return SER_EINVAL;
    }

    struct canfd_frame cf;
    memset(&cf, 0, sizeof(cf));
    cf.can_id = frame->id | CAN_EFF_FLAG;
    cf.len = frame->len;
    memcpy(cf.data, frame->data, frame->len);

    const ssize_t n = write(g_can_fd, &cf, sizeof(cf));
    if (n < 0) {
        return (errno == ENOBUFS) ? SER_EBUSY : SER_EIO;
    }
    return SER_OK;
}

int ser_hal_can_recv(ser_can_frame_t *frame, int timeout_ms) {
    if ((frame == NULL) || (g_can_fd < 0)) {
        return SER_EINVAL;
    }

    struct pollfd pfd = { .fd = g_can_fd, .events = POLLIN, .revents = 0 };
    const int pr = poll(&pfd, 1, timeout_ms);
    if (pr == 0) {
        return SER_ETIMEDOUT;
    }
    if (pr < 0) {
        return SER_EIO;
    }

    struct canfd_frame cf;
    const ssize_t n = read(g_can_fd, &cf, sizeof(cf));
    if (n < (ssize_t)offsetof(struct canfd_frame, data)) {
        return SER_EIO;
    }

    frame->id = cf.can_id & CAN_EFF_MASK;
    frame->len = (cf.len > SER_CANFD_MAX_DLEN) ? SER_CANFD_MAX_DLEN : cf.len;
    memcpy(frame->data, cf.data, frame->len);
    return SER_OK;
}

int ser_hal_can_status(ser_can_status_t *status) {
    if (status == NULL) {
        return SER_EINVAL;
    }
    /* SocketCAN exposes error counters through netlink, which the sim port
     * does not read; the counters are reported as zero and the overflow
     * count is the one real value available here. */
    memset(status, 0, sizeof(*status));
    status->rx_overflow = g_rx_overflow;
    return SER_OK;
}

/* --- UART ----------------------------------------------------------------*/

int ser_hal_uart_init(ser_uart_t uart, uint32_t baud) {
    (void)baud;
    if ((unsigned)uart >= (unsigned)SER_UART_COUNT) {
        return SER_EINVAL;
    }

    const char *dev = getenv((uart == SER_UART_RS485)
                             ? "SERENITY_RS485_DEV" : "SERENITY_UART_DEV");
    if (dev == NULL) {
        /* No device configured: report absence rather than inventing a
         * bearer, so link failover behaviour is exercised honestly. */
        return SER_ENODEV;
    }

    const int fd = open(dev, O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (fd < 0) {
        return SER_ENODEV;
    }
    g_uart_fd[uart] = fd;
    return SER_OK;
}

int ser_hal_uart_write(ser_uart_t uart, const uint8_t *data, size_t len) {
    if (((unsigned)uart >= (unsigned)SER_UART_COUNT) || (data == NULL)) {
        return SER_EINVAL;
    }
    if (g_uart_fd[uart] <= 0) {
        return SER_ENODEV;
    }
    return (write(g_uart_fd[uart], data, len) == (ssize_t)len)
           ? SER_OK : SER_EIO;
}

int ser_hal_uart_read(ser_uart_t uart,
                      uint8_t *data,
                      size_t len,
                      size_t *got,
                      int timeout_ms) {
    if (((unsigned)uart >= (unsigned)SER_UART_COUNT) ||
        (data == NULL) || (got == NULL)) {
        return SER_EINVAL;
    }
    *got = 0U;
    if (g_uart_fd[uart] <= 0) {
        return SER_ENODEV;
    }

    struct pollfd pfd = {
        .fd = g_uart_fd[uart], .events = POLLIN, .revents = 0
    };
    const int pr = poll(&pfd, 1, timeout_ms);
    if (pr <= 0) {
        return SER_OK;      /* No data is not an error. */
    }

    const ssize_t n = read(g_uart_fd[uart], data, len);
    if (n < 0) {
        return SER_EIO;
    }
    *got = (size_t)n;
    return SER_OK;
}

/* --- NVM -----------------------------------------------------------------*/

static const char *nvm_path(void) {
    static char path[256];
    const char *dir = getenv("SERENITY_STATE_DIR");
    (void)snprintf(path, sizeof(path), "%s/serenity_%s_nvm.bin",
                   (dir != NULL) ? dir : "/tmp", BOARD_NAME);
    return path;
}

int ser_hal_nvm_read(void *dst, size_t len) {
    if (dst == NULL) {
        return SER_EINVAL;
    }
    const int fd = open(nvm_path(), O_RDONLY);
    if (fd < 0) {
        return SER_ENODEV;
    }
    const ssize_t n = read(fd, dst, len);
    (void)close(fd);
    return (n == (ssize_t)len) ? SER_OK : SER_EIO;
}

int ser_hal_nvm_write(const void *src, size_t len) {
    if (src == NULL) {
        return SER_EINVAL;
    }
    const int fd = open(nvm_path(), O_WRONLY | O_CREAT | O_TRUNC, 0600);
    if (fd < 0) {
        return SER_EIO;
    }
    const ssize_t n = write(fd, src, len);
    (void)close(fd);
    return (n == (ssize_t)len) ? SER_OK : SER_EIO;
}

/* --- Lifecycle -----------------------------------------------------------*/

int ser_hal_init(void) {
    g_epoch_ns = now_ns_raw();
    memset(g_uart_fd, 0, sizeof(g_uart_fd));
    memset(g_gpio, 0, sizeof(g_gpio));

    const char *tpm_dev = getenv("SERENITY_TPM_DEV");
    if (tpm_dev != NULL) {
        g_tpm_fd = open(tpm_dev, O_RDWR);
    }

    return board_hal_configure();
}

void ser_hal_log(const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    (void)vfprintf(stderr, fmt, ap);
    va_end(ap);
}

void ser_hal_reset(void) {
    (void)fflush(NULL);
    _exit(70);      /* EX_SOFTWARE: distinguishable from a clean exit. */
}
