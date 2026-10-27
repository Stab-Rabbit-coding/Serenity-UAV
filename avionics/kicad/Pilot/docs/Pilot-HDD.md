# Pilot Hardware Design Description

**Document:** Pilot-HDD, Revision A (draft for engineer review)  
**Board:** Pilot flight-control and sensor cape (CAPE-A-2) for the PocketBeagle 2 Industrial  
**Date:** 2026-10-19  
**Owner:** sgriffing (Griffing Technology LLC)  
**Prepared by:** Claude Sonnet 5.5 (Anthropic). The kidoc scaffold and the KiCad analyzers supplied the
figures and counts; the text was written from `Pilot.md`, the generator scripts and the datasheets
cited. Earlier design work in `Pilot.md` is by Claude Opus 4.8, Opus 5 and Opus 5.5 as recorded there.  
**License:** CC BY-SA 4.0

> **Status:** schematic complete (ERC 0, 136 parts, schematic parity 0). PCB placed but **not fully
> routed**: 130 connections are open (section 8). Nothing in this document is a release approval.
> Items marked **OPEN** need an engineering decision or a document that is not on file.

## 1. Purpose and scope

Pilot is the flight-control cape of the Serenity UAV's node stack. It carries the sensors, the
four field buses, the supply and the servo/ESC outputs that the PocketBeagle 2 Industrial (AM625)
does not provide. Related documents: [`Pilot-ICD-External.md`](Pilot-ICD-External.md),
[`Pilot-ICD-PB2I.md`](Pilot-ICD-PB2I.md), [`Pilot-Manufacturing-Transfer.md`](Pilot-Manufacturing-Transfer.md),
[`Pilot-Design-Review.md`](Pilot-Design-Review.md), `../Pilot.md` (design history).

## 2. Physical definition

| Item | Value |
| --- | --- |
| Outline | 2.165 in x 1.378 in (55.0 mm x 35.0 mm), 3 mm corner radius, area 2.98 in2 (1 925 mm2) |
| Layers | 6 copper: F.Cu signal, In1 GND plane, In2 signal, In3 signal, In4 +3V3 plane, B.Cu signal |
| Thickness | 0.063 in (1.6 mm) as drawn in the board setup; **no stackup is defined** (section 7) |
| Components | 136: 67 on F, 69 on B (131 SMD, 5 through-hole) |
| Nets | 112 with pads (205 in the schematic including unconnected pins) |
| Mounting | 4 x M2.5 on PGND rings (r 2.75 mm keep-out); stacks on the PB2-I's two 2 x 18 rails, 0.218 in (5.54 mm) gap |
| Mass | **OPEN:** not computed. The bare 6-layer FR-4 board is of the order of 6 g; component mass needs the BOM mass roll-up (WBS). |

The PB2-I's tall parts (microSD socket 1.0 mm, JST-SH 2.95 mm) limit B-side component height under
the module to 0.020 in (0.5 mm) clear margin: the placer enforces it (`OBSTRUCTIONS`
in `refloorplan_pilot.py`).

## 3. Architecture

| Block | Parts | Role |
| --- | --- | --- |
| Compute host | PB2-I (AM625), rails `PB2-P1`, `PB2-P2` | Linux, PRU DSHOT, CPSW3G, MCAN |
| Power entry | `PWR-IN` (Molex Nano-Fit), `FB1` pi filter, `C-IN1/2/3` | 5 V in, filtered `+5V` |
| 3.3 V supply | `U-3V3` TPSM828224SILR module | Cape-local +3V3 so the PB2's 3.3 V budget stays unloaded |
| CAN FD | `CAN-TR` ISOW1044, `CMC-CAN`, `TVS-CAN` (ESD2CAN24-Q1), `CAN-FD` | Isolated, 5 Mbps CAN FD |
| RS-485 | `RS485` ISOW1412, `CMC-RS485`, `TVS-RS485` (CDSOT23-SM712), `RS-485` | Isolated, 500 kbps |
| MIL-STD-1553B | `1553-XCVR` Holt HI-6138, `1553-XFM` PM-DB2791S, 2 x 55 R, `TVS-1553P/N` | Bus A, BC/RT/MT |
| Ethernet ring | `PHY-RMII2` DP83825I + `T-RMII2-TX/RX` + `J-ETH-RMII2`; `NIC-USB1` AX88772E + `T-USB1-TX/RX` + `J-ETH-USB1` | Two 10/100 legs, bridged in Linux |
| Sensors | `IMU` ICM-42688-P (SPI0), `BARO` BMP388 (SPI0) | Attitude, altitude |
| Security | `TPM` SLB9672 (SPI0) | Platform trust (fleet trust module) |
| Clocks | `X-25M` (DP83825I), `X-50M` (HI-6138 MCLK), `Y-USB1` 20 MHz (AX88772E) | One per timing domain |
| Outputs | `J-PWM` 4 x DSHOT/PWM, `J-SPI` expansion | Servos / ESCs, external SPI or UART |

Figures: system architecture and bus topology in `figures/diagrams/`; full schematic render in
`figures/schematics/Pilot.svg` (kidoc output).

## 4. Isolation architecture

The two isolators (ISOW1044, ISOW1412) are rated 5 000 Vrms with 1 000 Vrms / 1 500 Vpk working
voltage [REF-SENSOR-009, REF-SENSOR-010]. The board keeps their isolated domains in a rule area
`ISO_BAND` and enforces, through `Pilot.kicad_dru`:

* logic copper may not enter `ISO_BAND`; isolated copper may not leave it (`iso_band_logic_copper`,
  `iso_nets_stay_in_band`);
* 0.020 in (0.5 mm) clearance between isolated and other copper (`iso_cross_domain_clearance`);
* the TI section 13.1 4 mm "bubbles" around VISOOUT (pin 12) and GND2 (pin 11) on every copper
  layer (`bubble_can`, `bubble_485`), with the section 13.1 ferrite beads (Murata BLM15EX331SN1D)
  between VISOOUT / VISOIN and GND2 / GISOIN [REF-SENSOR-043].

The Ethernet transformers are the third isolation barrier (1 500 Vac, 60 s [REF-SENSOR-061]).

## 5. Power

| Rail | Source | Loads |
| --- | --- | --- |
| `+5V_IN` | `PWR-IN` | Pi filter only |
| `+5V` | `FB1` (742792512, 600 R at 100 MHz, 2 A) after `+5V_IN` | PB2-I VIN (P1-01), U-3V3, isolator DC-DC inputs, J-PWM, J-SPI (0.35 A fuse) |
| `+3V3` | `U-3V3` TPSM828224SILR [REF-PWR-008] | All cape logic, sensors, PHY, NIC |
| Isolated rails | ISOW1044 / ISOW1412 integrated DC-DC | `VCC2_CAN`, `VCC2_RS485` and their grounds |

Verified facts: AX88772E full load is 35.3 mA at 3.3 V plus 25 mA at 1.1 V (data sheet 5.2), about
0.2 W, 6.6 C junction rise at 33.3 C/W; the 3V3 module's output capacitors keep at least 5 uF
effective at 3.333 V bias [REF-PWR-011]; at 85 C ambient with continuous 1553 transmit the module
reaches about 119 C against 125 C (`Pilot.md`, estimated 85 % efficiency).

**OPEN:** a single rail-by-rail current budget (worst-case sum against the 3V3 module's rating and the
5 V input) has not been written down for the final 136-part design. It is the next analysis to do.

## 6. Interfaces

See the ICDs. In short: seven cable connectors (power, CAN FD, RS-485, MIL-1553, two Ethernet,
one expansion) plus the servo/ESC block and the two PB2-I rails. Direction, ratings and open items
are tabulated there from the netlist.

## 7. Signal integrity and stackup

| Interface | Target | Basis |
| --- | --- | --- |
| USB1 D+/D- | 90 ohm differential | AX88772E app note 9-1 [REF-SENSOR-057]; USB 2.0 |
| Ethernet MDI pairs (both legs) | 100 ohm differential, 50 ohm to ground | DP83825I data sheet 8.2.2.2 [REF-SENSOR-029]; app note 10 |
| RMII2 | 50 ohm single-ended, 2 to 6 in | DP83825I 8.2.2.1 |

The board file defines **no stackup** and the netclass `DIFF_PAIR` is 0.006 in (0.15 mm) width /
0.006 in gap with no calculated impedance. **OPEN:** choose a stackup with the fabricator
(Sunstone offers stocked FR-4 6-layer builds and a controlled-impedance service), compute widths
for the targets above, and set them in the board setup. Until then the impedance values are
design intent, not a verified property of the layout. Routing rules on the board: 0.005 in (0.127 mm)
track and clearance, 0.012 in / 0.024 in (0.3 mm / 0.6 mm) vias.

TC1G00 magnetics: the data sheet characterises the part for 1000BASE-T and faster
[REF-SENSOR-061]; suitability for 100BASE-TX is **OPEN** pending engineer-of-record review.

## 8. Layout and routing status

| Check | Result (2026-10-19, commit `848d78bb`) |
| --- | --- |
| ERC | 0 |
| Schematic parity | 0 |
| DRC copper errors | 0 |
| DRC warnings | 13 (9 silkscreen over copper, 3 dangling track ends under 0.1 mm, 1 silkscreen near edge) |
| Unconnected items | **130**: 31 plane pads (17 +3V3, 14 GND) with no legal via site; the rest are signals (SPI0, AX88772E rails, RMII2, 1553 and RS-485 control) |
| Reference designators | on the Fab layers, not silkscreen (252 of 263 silkscreen warnings were designators) |

Two automatic routers stalled: a rule-aware grid router with rip-up (254 to 130 open) and
freerouting 2.2.4 on a stripped board (about 190 unrouted after 38 passes). Hand routing in the
KiCad interactive router, an added signal layer, or removing a function is the owner's decision
(`Pilot-Design-Review.md` section 4).

## 9. Test and bring-up

Test-point coverage is 7 of 104 nets (7 %, analyzer TE-001). Bring-up steps that the design
already requires: verify RMII2 timing on P1-02/19/25/27 with the MSPM0 AIN load; hold P1-31
(GPIO0_59) as an input; hold every unused second ball as a GPIO input with no pull; confirm
AX88772E attach and detach through P1-31. **OPEN:** a test plan and test-point additions.

## 10. Compliance (United States)

* Bus electrical: MIL-STD-1553C bus-coupling arrangement [REF-MIL-001 4.5.1.5.2].
* ESD: IEC 61000-4-2 level 4 design target at field connectors [REF-IEC-003]; the CAN and RS-485
  TVS parts and the isolators' own 8 kV bus-pin ratings carry the ports.
* EMC: radiated and conducted limits are product-level and set by the installation
  (DO-160 / MIL-STD-461 style requirements are not a Pilot-level claim). Part 15 (47 CFR) applies to
  the finished device; **OPEN:** the assembled-node EMC class and test plan are not written.
* Sourcing and openness: every IC maker is outside the restricted-country list and every data sheet
  is public (AGENTS.md section 5); the fleet audit of the other boards is open (WBS).

## 11. References

REF-MIL-001, REF-IEC-003, REF-SENSOR-009, -010, -021, -022, -023, -029, -041, -043, -044, -049, -050,
-056 to -061, REF-PWR-008, -011, -013, REF-CONN-001 to -003, REF-FAB-001 (all in `/REFERENCES.md`).
