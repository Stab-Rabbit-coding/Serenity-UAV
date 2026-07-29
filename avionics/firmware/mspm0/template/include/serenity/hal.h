/**
 * @file    hal.h
 * @brief   Serenity MSPM0 trust-node firmware — hardware abstraction contract.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * This header is the ONLY interface the shared firmware template
 * (the sources under template/src) is permitted to use to touch hardware.  Every
 * board and every MCU port implements it:
 *
 *   - `hal/mspm0/` — TI MSPM0G3507 port, built on the TI MSPM0 SDK DriverLib.
 *                    This is the flight port; it is what runs on
 *                    `MAL-CAN-PERIPH-GW-PCB`, Jayne (U3) and Kaylee (U_MCU).
 *   - `hal/sim/`   — POSIX host port (SocketCAN vcan + a TPM simulator or a
 *                    real /dev/tpm0).  Used for unit and integration test on a
 *                    workstation; never flown.
 *
 * Keeping the template hardware-free is what makes one firmware template
 * serve all three MSPM0G3507 boards in the fleet — the boards differ only in
 * `boards/<board>/board_config.h` (pin map, CAN identity, topic set) and
 * `boards/<board>/app.c` (what the node actually senses or actuates).
 *
 * Error convention (whole firmware, not just this header):
 *   0        = success
 *   negative = failure; the value is one of the `SER_E*` codes below.
 * Byte counts are returned as `size_t` with a separate status out-parameter
 * only where a short transfer is a legal, non-error outcome.
 *
 * References (see repository-root `REFERENCES.md`):
 *   [REF-SENSOR-004] TI MSPM0G3507 — Mixed-Signal MCU with CAN-FD Interface.
 *   [REF-SENSOR-009] TI ISOW1044BDFMR — isolated CAN-FD transceiver (5 Mbps max).
 *   [REF-SENSOR-011] Infineon OPTIGA SLB 9670 — SPI TPM 2.0 (SPI clock <= 43 MHz).
 *   [REF-ISO-001]    ISO 11898-1:2015 — CAN data link layer, CAN-FD DLC coding.
 */

#ifndef SERENITY_HAL_H_
#define SERENITY_HAL_H_

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* ---------------------------------------------------------------------------
 * Status codes
 *
 * Deliberately a small, closed set: every one of these must be distinguishable
 * in a fault log written to the airframe bus, and the set has to stay stable
 * across firmware revisions because ground software decodes it.
 * ---------------------------------------------------------------------------*/

#define SER_OK              (0)     /**< Operation completed successfully.     */
#define SER_EINVAL          (-1)    /**< Caller passed an invalid argument.    */
#define SER_EIO             (-2)    /**< Peripheral-level transfer failure.    */
#define SER_ETIMEDOUT       (-3)    /**< Operation did not complete in time.   */
#define SER_ENOSPC          (-4)    /**< Destination buffer too small.         */
#define SER_ENODEV          (-5)    /**< Expected device did not respond.      */
#define SER_EPROTO          (-6)    /**< Peer violated the wire protocol.      */
#define SER_EBUSY           (-7)    /**< Resource in use; retry later.         */
#define SER_ENOTSUP         (-8)    /**< Not implemented on this port.         */

/* ---------------------------------------------------------------------------
 * Time base
 *
 * The XRCE client calls `clock_gettime(CLOCK_REALTIME, ...)` through its own
 * `util/time.c`.  On the MSPM0 port that call is retargeted onto
 * `ser_hal_time_ns()` by a newlib syscall shim (`hal/mspm0/syscalls.c`) so
 * that the upstream eProsima sources compile completely unmodified — see
 * `README.md` "Vendoring policy".
 * ---------------------------------------------------------------------------*/

/**
 * @brief Monotonic milliseconds since HAL init.
 *
 * Never wraps within a realistic mission: the counter is 64-bit and the
 * underlying timer rollover is accumulated by the port.
 */
uint64_t ser_hal_time_ms(void);

/**
 * @brief Monotonic nanoseconds since HAL init.
 *
 * Resolution is port-defined and is NOT guaranteed to be 1 ns; the MSPM0 port
 * derives it from a 32-bit timer running off the same clock tree as CAN, so
 * its true granularity is one timer tick.  Callers that need a guaranteed
 * resolution must query `ser_hal_time_resolution_ns()`.
 */
uint64_t ser_hal_time_ns(void);

/** @brief Granularity of `ser_hal_time_ns()` in nanoseconds. */
uint32_t ser_hal_time_resolution_ns(void);

/**
 * @brief Busy-wait for at least @p us microseconds.
 *
 * Used only in device bring-up paths (TPM reset timing, transceiver enable);
 * never in the steady-state control or publication loop.
 */
void ser_hal_delay_us(uint32_t us);

/* ---------------------------------------------------------------------------
 * Watchdog
 *
 * Every board runs the MSPM0 windowed watchdog.  The node main loop is the
 * only permitted petting site, so a stuck driver reboots the node rather than
 * letting it keep publishing stale, validly-signed telemetry — a signed stale
 * message is strictly more dangerous than no message, because downstream
 * consumers have no way to tell it is stale beyond the envelope timestamp.
 * ---------------------------------------------------------------------------*/

/** @brief Start the watchdog with the board's configured timeout. */
int ser_hal_watchdog_start(void);

/** @brief Pet the watchdog.  Called once per pass of the node main loop. */
void ser_hal_watchdog_pet(void);

/* ---------------------------------------------------------------------------
 * SPI — used for the SLB9670 TPM and (board-dependent) local sensors
 * ---------------------------------------------------------------------------*/

/**
 * @brief Logical SPI buses available to the template.
 *
 * The template never names a physical peripheral instance; the board maps
 * these logical buses onto SPI0/SPI1 in `board_config.h`.  The split matters:
 * `SER_SPI_TPM` must not be shared with a high-rate sensor, because a TPM
 * transaction can hold the bus for the duration of a TPM command.
 */
typedef enum {
    SER_SPI_TPM = 0,        /**< Dedicated bus to U_TPM / U2 / U5 SLB9670.     */
    SER_SPI_SENSOR = 1,     /**< Board-local sensor bus (e.g. AK7455, KSZ9477).*/
    SER_SPI_COUNT
} ser_spi_bus_t;

/**
 * @brief Full-duplex SPI transfer with the bus's chip select asserted for the
 *        whole transfer.
 *
 * @param bus   Logical bus selector.
 * @param cs    Chip-select index within that bus (0 for a single-device bus).
 * @param tx    Bytes to clock out.  May be NULL to clock out 0x00 padding.
 * @param rx    Buffer for bytes clocked in.  May be NULL to discard.
 * @param len   Number of bytes to transfer.
 * @return SER_OK, or a negative `SER_E*` code.
 *
 * @note SPI mode 0 (CPOL=0, CPHA=0) is mandatory for the TPM bus
 *       [REF-TCG-002 §7.4.6 rule 6]; the port configures it, the caller does
 *       not select it.
 */
int ser_hal_spi_xfer(ser_spi_bus_t bus,
                     uint8_t cs,
                     const uint8_t *tx,
                     uint8_t *rx,
                     size_t len);

/**
 * @brief Begin a multi-transfer SPI transaction, holding chip select asserted
 *        across several `ser_hal_spi_xfer_cont()` calls.
 *
 * Required by the TPM's SPI wait-state protocol: the header, the wait-state
 * polling window and the data phase are separate transfers that must all
 * occur inside one assertion of CS# [REF-TCG-002 §7.4.5].
 */
int ser_hal_spi_begin(ser_spi_bus_t bus, uint8_t cs);

/** @brief Transfer bytes inside an open transaction (CS# stays asserted). */
int ser_hal_spi_xfer_cont(ser_spi_bus_t bus,
                          const uint8_t *tx,
                          uint8_t *rx,
                          size_t len);

/** @brief End the transaction and deassert chip select. */
int ser_hal_spi_end(ser_spi_bus_t bus);

/* ---------------------------------------------------------------------------
 * GPIO — TPM reset, transceiver enables, fault inputs, board-local discretes
 * ---------------------------------------------------------------------------*/

/**
 * @brief Logical GPIO lines the shared template needs on every board.
 *
 * Board-specific lines beyond these are handled entirely inside
 * `boards/<board>/app.c` and never appear here.
 */
typedef enum {
    SER_GPIO_TPM_RST_N = 0, /**< SLB9670 RST# — active low.                   */
    SER_GPIO_CAN_STB_N,     /**< ISOW1044 STB — low = normal mode.            */
    SER_GPIO_CAN_FLT_N,     /**< ISOW1044 fault indication input, active low. */
    SER_GPIO_RS485_DE,      /**< ISOW1412 driver enable, active high.         */
    SER_GPIO_RS485_RE_N,    /**< ISOW1412 receiver enable, active low.        */
    SER_GPIO_STATUS_LED,    /**< Node liveness indicator.                     */
    SER_GPIO_COUNT
} ser_gpio_t;

/** @brief Drive an output line.  No-op with SER_ENOTSUP if unmapped. */
int ser_hal_gpio_write(ser_gpio_t line, bool level);

/** @brief Read an input line into @p level. */
int ser_hal_gpio_read(ser_gpio_t line, bool *level);

/* ---------------------------------------------------------------------------
 * CAN-FD — the XRCE transport and the airframe trunk
 *
 * The template does not implement CAN protocol logic; it hands frames to
 * `template/src/can_transport_mspm0.c`, which is the eProsima Micro-XRCE-DDS
 * CAN platform port.  These calls are what that port sits on.
 * ---------------------------------------------------------------------------*/

/** @brief Maximum CAN-FD payload, ISO 11898-1:2015 [REF-ISO-001]. */
#define SER_CANFD_MAX_DLEN  (64U)

/**
 * @brief One CAN-FD frame as the firmware handles it.
 *
 * `len` is the true payload length (0..64).  The port is responsible for
 * rounding up to a legal CAN-FD DLC and zero-padding the gap on transmit; the
 * eProsima wire format carries its own length in `data[0]`, so the padding is
 * harmless to the peer.
 */
typedef struct {
    uint32_t id;                        /**< 29-bit identifier (extended).    */
    uint8_t  len;                       /**< True payload length, 0..64.      */
    uint8_t  data[SER_CANFD_MAX_DLEN];  /**< Payload.                         */
} ser_can_frame_t;

/**
 * @brief Bring up the CAN-FD peripheral and its isolated transceiver.
 *
 * @param nominal_bps   Arbitration-phase bit rate, bit/s.
 * @param data_bps      Data-phase bit rate, bit/s.  Must not exceed the
 *                      transceiver's rating — 5 000 000 for ISOW1044
 *                      [REF-SENSOR-009].
 * @param accept_id     29-bit identifier this node accepts frames on.
 * @return SER_OK, or a negative `SER_E*` code.
 *
 * The filter is exact-match on @p accept_id, matching the eProsima Agent's
 * CAN endpoint model: the Agent addresses each client by that client's own
 * identifier, and replies to the identifier it saw a frame arrive on.
 */
int ser_hal_can_init(uint32_t nominal_bps, uint32_t data_bps, uint32_t accept_id);

/**
 * @brief Queue one frame for transmission.  Non-blocking.
 *
 * @return SER_OK if queued, SER_EBUSY if no transmit buffer is free,
 *         or another negative `SER_E*` code.
 */
int ser_hal_can_send(const ser_can_frame_t *frame);

/**
 * @brief Take one received frame from the RX queue.
 *
 * @param frame     Destination.
 * @param timeout_ms Milliseconds to wait; 0 polls, negative blocks forever.
 * @return SER_OK if a frame was returned, SER_ETIMEDOUT if none arrived,
 *         or another negative `SER_E*` code.
 */
int ser_hal_can_recv(ser_can_frame_t *frame, int timeout_ms);

/** @brief CAN controller error/health counters, for node health telemetry. */
typedef struct {
    uint16_t tx_error_count;    /**< CAN TEC.                                 */
    uint16_t rx_error_count;    /**< CAN REC.                                 */
    bool     bus_off;           /**< Controller is bus-off.                   */
    bool     error_passive;     /**< Controller is error-passive.             */
    uint32_t rx_overflow;       /**< Frames dropped for lack of queue space.  */
} ser_can_status_t;

/** @brief Read CAN controller health. */
int ser_hal_can_status(ser_can_status_t *status);

/* ---------------------------------------------------------------------------
 * UART — RS-485 mirror bus and board-local serial devices
 * ---------------------------------------------------------------------------*/

/** @brief Logical UARTs the template may use. */
typedef enum {
    SER_UART_RS485 = 0,     /**< Isolated RS-485 trunk via ISOW1412.          */
    SER_UART_FLEX,          /**< Board flexible header / local serial device. */
    SER_UART_COUNT
} ser_uart_t;

/** @brief Configure a UART.  @p baud in bit/s, 8N1 assumed. */
int ser_hal_uart_init(ser_uart_t uart, uint32_t baud);

/**
 * @brief Write bytes.  Blocks until the last byte has left the shift register
 *        when @p uart is SER_UART_RS485, so the caller can safely drop DE.
 */
int ser_hal_uart_write(ser_uart_t uart, const uint8_t *data, size_t len);

/**
 * @brief Read up to @p len bytes, returning the count actually read in @p got.
 *
 * @return SER_OK (possibly with *got == 0), or a negative `SER_E*` code.
 */
int ser_hal_uart_read(ser_uart_t uart,
                      uint8_t *data,
                      size_t len,
                      size_t *got,
                      int timeout_ms);

/* ---------------------------------------------------------------------------
 * Non-volatile storage — TPM key handle persistence and node identity
 * ---------------------------------------------------------------------------*/

/**
 * @brief Read the node's persisted configuration blob.
 *
 * Holds the persistent TPM handle of the node's signing key and the node's
 * assigned CAN identifier.  Backed by a dedicated MSPM0 flash sector on the
 * target port and by a file on the sim port.
 *
 * @return SER_OK, SER_ENODEV if never written, or a negative `SER_E*` code.
 */
int ser_hal_nvm_read(void *dst, size_t len);

/** @brief Erase and rewrite the node configuration blob. */
int ser_hal_nvm_write(const void *src, size_t len);

/* ---------------------------------------------------------------------------
 * Port lifecycle
 * ---------------------------------------------------------------------------*/

/**
 * @brief Bring up clocks, the time base, GPIO and the watchdog.
 *
 * Called once, first thing in `main()`, before any other HAL call.  CAN, SPI
 * and UART are brought up separately and later, because the node lifecycle
 * needs to attest the TPM before it is allowed to join the bus.
 */
int ser_hal_init(void);

/**
 * @brief Emit a diagnostic line on the port's debug channel.
 *
 * On the MSPM0 port this is the SWD ITM/console; on the sim port it is stderr.
 * Diagnostics are for bench bring-up only — flight-relevant events go out as
 * signed telemetry, never here.
 */
void ser_hal_log(const char *fmt, ...);

/** @brief Reset the MCU.  Does not return. */
void ser_hal_reset(void) __attribute__((noreturn));

#ifdef __cplusplus
}
#endif

#endif /* SERENITY_HAL_H_ */
