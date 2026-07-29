/**
 * @file    hal_mspm0.c
 * @brief   TI MSPM0G3507 port of the Serenity HAL — flight target.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * Copyright 2026 Steve Griffing
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * ## Status: peripheral bring-up is NOT yet implemented
 *
 * This file currently provides the parts of the HAL that need no peripheral
 * driver — the reset vector, the time base, the heap and stack setup — and
 * returns `SER_ENOTSUP` from every peripheral entry point.  It links and it
 * boots; it does not yet talk to hardware.
 *
 * That is a deliberate, visible gap rather than a guess.  The peripheral
 * drivers below must be written against the **TI MSPM0 SDK DriverLib**, and
 * the SDK is not installed on the workstation this was authored on, so the
 * exact DriverLib symbol names, register field enumerations and clock-tree
 * initialisation sequence could not be verified against the real headers.
 * Writing plausible-looking `DL_*` calls from memory would produce code that
 * compiles against nothing and fails on the bench with no way to tell a typo
 * from a design error — worse than an honest stub.  Each function below
 * records what it must do and which document specifies it.
 *
 * To complete this port:
 *   1. Install the TI MSPM0 SDK (`mspm0_sdk`, TI BSD-3-Clause — compatible
 *      with this repository's CC BY 4.0 terms per root `AGENTS.md` §3).
 *   2. Point the build at it: `-DMSPM0_SDK_PATH=/path/to/mspm0_sdk`.
 *   3. Implement each function below against DriverLib and the MSPM0G
 *      Technical Reference Manual (TI SLAU846), checking every peripheral
 *      instance and pin against the owning board's KiCad schematic.
 *
 * Tracked as WBS §4.7.2.
 *
 * References:
 *   [REF-SENSOR-004] TI MSPM0G3507 datasheet — peripherals, memory, clocks.
 *   [REF-SENSOR-009] TI ISOW1044BDFMR — CAN-FD transceiver, 5 Mbit/s max.
 *   [REF-ISO-001]    ISO 11898-1:2015 — CAN-FD bit timing and DLC coding.
 *   [REF-TCG-002]    TCG PC Client PTP — TPM SPI mode 0 requirement.
 */

#include "serenity/board.h"
#include "serenity/hal.h"

#include <stdarg.h>
#include <stdint.h>
#include <string.h>

/* ---------------------------------------------------------------------------
 * Startup
 * ---------------------------------------------------------------------------*/

extern uint32_t _etext;
extern uint32_t _sdata;
extern uint32_t _edata;
extern uint32_t _sbss;
extern uint32_t _ebss;
extern uint32_t _estack;

extern int main(void);

void Reset_Handler(void);
void Default_Handler(void);

/**
 * @brief Reset entry point: initialise .data and .bss, then call main().
 *
 * No libc `__libc_init_array` call: the firmware is C with no static
 * constructors, and pulling in the init-array machinery would add flash for
 * nothing.
 */
void Reset_Handler(void) {
    const uint32_t *src = &_etext;
    for (uint32_t *dst = &_sdata; dst < &_edata; ) {
        *dst++ = *src++;
    }
    for (uint32_t *dst = &_sbss; dst < &_ebss; ) {
        *dst++ = 0U;
    }

    (void)main();

    /* main() does not return; if it somehow does, stop rather than run off
     * into whatever follows in flash. */
    for (;;) {
    }
}

/**
 * @brief Catch-all fault handler.
 *
 * Spins so the watchdog resets the part.  A fault here means the node's state
 * is untrustworthy, and a node in an untrustworthy state must stop signing
 * telemetry immediately — a reset is the fastest way to guarantee that.
 */
void Default_Handler(void) {
    for (;;) {
    }
}

/* Cortex-M0+ core exceptions.  Peripheral interrupts are added as the drivers
 * that need them are written. */
#define ALIAS_DEFAULT __attribute__((weak, alias("Default_Handler")))
void NMI_Handler(void) ALIAS_DEFAULT;
void HardFault_Handler(void) ALIAS_DEFAULT;
void SVC_Handler(void) ALIAS_DEFAULT;
void PendSV_Handler(void) ALIAS_DEFAULT;
void SysTick_Handler(void) ALIAS_DEFAULT;

/**
 * @brief Cortex-M0+ vector table; placed at flash origin by the link script.
 *
 * A vector table is inherently non-ISO: entry 0 is the initial stack pointer
 * (an object address) and every other entry is a handler (a function address),
 * and ISO C permits no conversion between the two.  -Wpedantic is correct to
 * object and there is no standard-conforming way to express this — the Arm
 * architecture defines the layout, not C.  The diagnostic is therefore
 * suppressed for this array only, and nowhere else in the firmware.
 */
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wpedantic"
__attribute__((section(".isr_vector"), used))
static void *const g_vectors[] = {
    (void *)&_estack,
    (void *)Reset_Handler,
    (void *)NMI_Handler,
    (void *)HardFault_Handler,
    0, 0, 0, 0, 0, 0, 0,
    (void *)SVC_Handler,
    0, 0,
    (void *)PendSV_Handler,
    (void *)SysTick_Handler,
};
#pragma GCC diagnostic pop

/* ---------------------------------------------------------------------------
 * Time base
 *
 * TODO(WBS §4.7.2): drive this from TIMG12 (the 32-bit general-purpose timer)
 * clocked off MCLK, accumulating rollover into the 64-bit counter.  Until
 * then a cycle-counting approximation keeps the timeout logic in the TPM and
 * link layers functional for bring-up.
 * ---------------------------------------------------------------------------*/

static volatile uint64_t g_ticks_ns;

uint64_t ser_hal_time_ns(void) {
    return g_ticks_ns;
}

uint64_t ser_hal_time_ms(void) {
    return g_ticks_ns / 1000000ULL;
}

uint32_t ser_hal_time_resolution_ns(void) {
    /* TIMG12 off an 80 MHz MCLK gives 12.5 ns; reported as 13 ns until the
     * real clock tree is configured and this can be computed. */
    return 13U;
}

void ser_hal_delay_us(uint32_t us) {
    /*
     * Cycle-counted busy-wait at 80 MHz [REF-SENSOR-004].  Replaced by a
     * timer-based delay when the time base above is implemented; the loop is
     * `volatile` so it survives -Os.
     */
    for (uint32_t i = 0U; i < us; ++i) {
        for (volatile uint32_t c = 0U; c < 20U; ++c) {
        }
        g_ticks_ns += 1000ULL;
    }
}

/* ---------------------------------------------------------------------------
 * Watchdog — TODO(WBS §4.7.2): WWDT0, windowed mode
 * ---------------------------------------------------------------------------*/

int ser_hal_watchdog_start(void) {
    return SER_ENOTSUP;
}

void ser_hal_watchdog_pet(void) {
}

/* ---------------------------------------------------------------------------
 * SPI — TODO(WBS §4.7.2)
 *
 * SER_SPI_TPM must be mode 0 (CPOL=0, CPHA=0) [REF-TCG-002 §7.4.6 rule 6] at
 * no more than 43 MHz [REF-SENSOR-011], with chip select driven as a GPIO so
 * it can be held across the multi-transfer TIS wait-state sequence — the
 * peripheral's own automatic CS deasserts between transfers and would break
 * the protocol.
 * ---------------------------------------------------------------------------*/

int ser_hal_spi_begin(ser_spi_bus_t bus, uint8_t cs) {
    (void)bus;
    (void)cs;
    return SER_ENOTSUP;
}

int ser_hal_spi_xfer_cont(ser_spi_bus_t bus, const uint8_t *tx,
                          uint8_t *rx, size_t len) {
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

int ser_hal_spi_xfer(ser_spi_bus_t bus, uint8_t cs, const uint8_t *tx,
                     uint8_t *rx, size_t len) {
    (void)bus;
    (void)cs;
    (void)tx;
    (void)rx;
    (void)len;
    return SER_ENOTSUP;
}

/* ---------------------------------------------------------------------------
 * GPIO — TODO(WBS §4.7.2): IOMUX + GPIOA/GPIOB per the board schematic
 * ---------------------------------------------------------------------------*/

static bool g_gpio[SER_GPIO_COUNT];

int ser_hal_gpio_write(ser_gpio_t line, bool level) {
    if ((unsigned)line >= (unsigned)SER_GPIO_COUNT) {
        return SER_EINVAL;
    }
    g_gpio[line] = level;
    return SER_ENOTSUP;
}

int ser_hal_gpio_read(ser_gpio_t line, bool *level) {
    if (((unsigned)line >= (unsigned)SER_GPIO_COUNT) || (level == NULL)) {
        return SER_EINVAL;
    }
    *level = g_gpio[line];
    return SER_ENOTSUP;
}

/* ---------------------------------------------------------------------------
 * CAN-FD — TODO(WBS §4.7.2): MCAN
 *
 * Bit timing must be computed from the actual CAN clock, not copied: the
 * nominal and data-phase segments have to place the sample point correctly
 * for the trunk's propagation delay [REF-ISO-001].  The acceptance filter is
 * an exact match on the node's own 29-bit extended identifier.  Message RAM
 * must be laid out for 64-byte data fields, which is not the reset default.
 * ---------------------------------------------------------------------------*/

int ser_hal_can_init(uint32_t nominal_bps, uint32_t data_bps,
                     uint32_t accept_id) {
    (void)nominal_bps;
    (void)data_bps;
    (void)accept_id;
    return SER_ENOTSUP;
}

int ser_hal_can_send(const ser_can_frame_t *frame) {
    (void)frame;
    return SER_ENOTSUP;
}

int ser_hal_can_recv(ser_can_frame_t *frame, int timeout_ms) {
    (void)frame;
    (void)timeout_ms;
    return SER_ENOTSUP;
}

int ser_hal_can_status(ser_can_status_t *status) {
    if (status == NULL) {
        return SER_EINVAL;
    }
    memset(status, 0, sizeof(*status));
    return SER_ENOTSUP;
}

/* ---------------------------------------------------------------------------
 * UART — TODO(WBS §4.7.2)
 *
 * SER_UART_RS485 drives ISOW1412; DE must be asserted before the first bit
 * and released only after the last stop bit has left the shift register, or
 * the tail of every frame is truncated on the bus.
 * ---------------------------------------------------------------------------*/

int ser_hal_uart_init(ser_uart_t uart, uint32_t baud) {
    (void)uart;
    (void)baud;
    return SER_ENOTSUP;
}

int ser_hal_uart_write(ser_uart_t uart, const uint8_t *data, size_t len) {
    (void)uart;
    (void)data;
    (void)len;
    return SER_ENOTSUP;
}

int ser_hal_uart_read(ser_uart_t uart, uint8_t *data, size_t len,
                      size_t *got, int timeout_ms) {
    (void)uart;
    (void)data;
    (void)len;
    (void)timeout_ms;
    if (got != NULL) {
        *got = 0U;
    }
    return SER_ENOTSUP;
}

/* ---------------------------------------------------------------------------
 * NVM — TODO(WBS §4.7.2): FLASHCTL, one dedicated sector
 * ---------------------------------------------------------------------------*/

int ser_hal_nvm_read(void *dst, size_t len) {
    (void)dst;
    (void)len;
    return SER_ENOTSUP;
}

int ser_hal_nvm_write(const void *src, size_t len) {
    (void)src;
    (void)len;
    return SER_ENOTSUP;
}

/* ---------------------------------------------------------------------------
 * Lifecycle
 * ---------------------------------------------------------------------------*/

int ser_hal_init(void) {
    /* TODO(WBS §4.7.2): SYSCTL clock tree — HFXT or SYSOSC to 80 MHz MCLK,
     * then the CAN clock, then IOMUX. */
    g_ticks_ns = 0U;
    memset(g_gpio, 0, sizeof(g_gpio));
    return board_hal_configure();
}

void ser_hal_log(const char *fmt, ...) {
    /* TODO(WBS §4.7.2): route to the SWD debug channel.  Discarded until
     * then — deliberately silent rather than blocking on a UART that may be
     * carrying the RS-485 bearer. */
    (void)fmt;
}

void ser_hal_reset(void) {
    /* TODO(WBS §4.7.2): SYSCTL software reset.  Spinning lets the watchdog
     * do it, which is correct behaviour even once the direct path exists. */
    for (;;) {
    }
}
