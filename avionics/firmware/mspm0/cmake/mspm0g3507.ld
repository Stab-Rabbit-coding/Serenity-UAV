/*
 * mspm0g3507.ld — link script for the TI MSPM0G3507.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 *
 * Memory sizes are the MSPM0G3507 device row of the datasheet feature list:
 * 128 KB flash, 32 KB SRAM [REF-SENSOR-004].  Base addresses are the MSPM0G
 * family map (flash at 0x0000_0000, SRAM at 0x2000_0000).
 *
 * The two ASSERTs at the end are the point of this file: they turn "the image
 * outgrew the part" into a link error with a number, rather than a device that
 * fails to program on the bench.
 */

MEMORY
{
    FLASH (rx)  : ORIGIN = 0x00000000, LENGTH = 128K
    SRAM  (rwx) : ORIGIN = 0x20000000, LENGTH = 32K
}

/* Stack lives at the top of SRAM and grows down.  4 KB covers the deepest
 * path measured so far (TPM command marshalling inside a publish). */
_stack_size = 4K;
_estack = ORIGIN(SRAM) + LENGTH(SRAM);

ENTRY(Reset_Handler)

SECTIONS
{
    .isr_vector : { KEEP(*(.isr_vector)) } > FLASH

    .text :
    {
        *(.text*)
        *(.rodata*)
        KEEP(*(.init))
        KEEP(*(.fini))
        . = ALIGN(4);
        _etext = .;
    } > FLASH

    .ARM.exidx : { *(.ARM.exidx*) } > FLASH

    .data : AT (_etext)
    {
        . = ALIGN(4);
        _sdata = .;
        *(.data*)
        . = ALIGN(4);
        _edata = .;
    } > SRAM

    .bss :
    {
        . = ALIGN(4);
        _sbss = .;
        *(.bss*)
        *(COMMON)
        . = ALIGN(4);
        _ebss = .;
    } > SRAM

    .heap (NOLOAD) :
    {
        . = ALIGN(8);
        _sheap = .;
        /* Whatever is left between .bss and the stack.  The firmware itself
         * makes no dynamic allocations; this exists only for newlib's
         * internals. */
    } > SRAM

    _eheap = ORIGIN(SRAM) + LENGTH(SRAM) - _stack_size;
}

ASSERT(_etext + (_edata - _sdata) <= ORIGIN(FLASH) + LENGTH(FLASH),
       "Image exceeds the MSPM0G3507's 128 KB flash [REF-SENSOR-004]")
ASSERT(_ebss + _stack_size <= ORIGIN(SRAM) + LENGTH(SRAM),
       "Static RAM plus stack exceeds the MSPM0G3507's 32 KB SRAM [REF-SENSOR-004]")
