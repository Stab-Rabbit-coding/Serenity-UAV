---
title: "PB2 / PB2-I header capability comes from the SoC and co-processor data sheets, not the SRM summary"
date: 2026-10-17
category: conventions
module: "avionics/kicad (Pilot, TACCO and any PocketBeagle 2 / PB2-I cape)"
problem_type: convention
component: tooling
severity: high
applies_when:
  - "Allocating PB2 or PB2-I P1/P2 header pins to cape functions"
  - "Deciding whether an interface (Ethernet port, CAN-FD, UART, I2C, SPI, timestamp) is available to a cape"
  - "Routing a fast signal (RMII/RGMII, DShot, SPI) through a header pin"
  - "Reading the PocketBeagle 2 SRM or schematic mux list as if it were complete"
tags: [pocketbeagle2, pb2-i, am625, mspm0l1105, pinmux, header, ethernet, can-fd]
related_components:
  - avionics/kicad/PB2I_AM625_HEADER_CAPABILITIES.md
  - avionics/kicad/PB2_HEADER_PINMAP.md
  - avionics/datasheets/extracted/AM625_PB2I_header_mux.json
---

# PB2 / PB2-I header capability comes from the SoC and co-processor data sheets, not the SRM summary

## Context

Pilot and TACCO pin maps were built from the PocketBeagle 2 System Reference Manual (SRM)
§4.2 tables and the PB2 schematic. Those list only the mux options BeagleBoard chose to
print. On 2026-10-17 the owner pointed out that the AM625 data sheet (SPRSP58C, p. 2) lists
two Ethernet ports, which the project had treated as one. Checking every header ball against
SPRSP58C Table 5-1, and the PB2-I's MSPM0L1105 co-processor against its own data sheet and
TRM, turned up several facts the summaries hide.

## Guidance

1. **Take SoC capability from SPRSP58C Table 5-1 (ALW column).** Use the header subset in
   `avionics/datasheets/extracted/AM625_PB2I_header_mux.json`, or re-derive it from the data
   sheet. Do not use the SRM or schematic mux strings, which are incomplete. For example, the
   SRM P1-12 entry "SPI2_DI" is a typo for SPI2_D1.
2. **Check whole-interface reachability, not chip-level counts.**
    - The CPSW3G has two external ports, but port 1 (RGMII1/RMII1) has no alternate balls and
      does not reach the header. Only port 2 does (RMII2, or RGMII2 with all 12 balls).
    - A cape Ethernet ring therefore needs a second, non-CPSW MAC. The project uses a USB NIC
      on USB1.
    - All three MCAN controllers do reach the header: MCAN0, MCU_MCAN0 (P1-26/28) and
      MCU_MCAN1 (P2-9/11).
3. **Count every load on a header pin.**
    - 17 header pins are tied to two AM625 balls, so only one ball per pin shall drive.
    - 8 header pins (P1-2, P1-19, P1-21, P1-23, P1-25, P1-27, P2-35, P2-36) are also wired
      directly to MSPM0L1105 pins. Each adds 5 pF and an on-board stub.
    - After power-up, P2-35 (PA20 = SWCLK) is pulled low (SLAU847F §2.4.1.2).
4. **Do not rest wiring on firmware state.** What the MSPM0 or the unused ball does after boot
   is a firmware setting. Treat it as possibly driving or pulling, which is the owner rule.
5. **Re-count after parsing.** pdftotext-based parsing of Table 5-1 silently dropped P2.35 and
   P2.36 once. Check the ball count against the SRM ball list: 72 balls, including 3 USB.

## Why This Matters

- Treating the SoC as single-port nearly drove the Ethernet ring decision on a false premise.
  It happened to survive only because port 1 really is unreachable.
- The dual-ball and MSPM0 loads sit on the Pilot's RMII2 and DShot lines without being
  visible in the cape's own schematic.
- A third CAN-FD bus was available and unconsidered.

## When to Apply

- Any new PB2 or PB2-I cape pin allocation or re-map.
- Any decision that says "the SoC can't do X on the header."
- Any fast signal placed on an AIN-shared header pin.

## Examples

- Before: "Only RMII2 reaches the header, so the SoC has one usable Ethernet port."
  After: "The SoC has two CPSW ports; port 1's balls are unreachable on the PB2-I; port 2 is
  available as RMII2 or RGMII2."
- Before: P1-2 listed as AA19 (+AIN6). After: AA19 + E18 + MSPM0 PA16/A8.

## Related

- `avionics/kicad/PB2I_AM625_HEADER_CAPABILITIES.md` (full table, §6 MSPM0)
- `docs/solutions/conventions/pb2-cape-datasheet-verified-footprints-and-courtyard-budget-before-layout.md`
  (same principle for lands: OEM data sheet over memory or summaries)
- REFERENCES.md REF-SENSOR-041, -049, -050, -051, -052
