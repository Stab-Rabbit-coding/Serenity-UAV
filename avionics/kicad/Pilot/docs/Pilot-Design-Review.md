# Pilot Design Review Package

**Document:** Pilot-DR, Revision A (draft)  
**Date:** 2026-10-19 (commit `848d78bb` plus the documentation commit that follows it)  
**Prepared by:** Claude Sonnet 5.5 (Anthropic), from the kidoc / kicad analyzers and the DRC run  
**License:** CC BY-SA 4.0

## 1. Gate summary

| Gate | Result | Source |
| --- | --- | --- |
| ERC | 0 | `kicad-cli sch erc` |
| Schematic parity | 0 | `kicad-cli pcb drc --schematic-parity` |
| DRC copper / hole / rule errors | 0 | same |
| DRC warnings | 13 | same: 9 silkscreen over copper, 3 dangling track ends < 0.1 mm, 1 silkscreen near edge |
| Unconnected items | **130** | same |
| Routing complete | **No** (analyzer: 94 of 112 nets routed, 18 nets unrouted) | `docs/analysis/pcb.json` |
| Analyzer errors | 83: 50 keepout flags (section 3: most are not defects, **5 are unresolved**), 18 unrouted nets, 13 board-edge flags, 2 fiducial flags | `docs/analysis/pcb.json` |

The analyzer counts nets and KiCad counts ratsnest items, so the two unrouted figures differ;
use the KiCad figure. **The board is not releasable.**

## 2. Findings that are real

| ID | Finding | Evidence | Action |
| --- | --- | --- | --- |
| R-1 | 130 unconnected items, 31 of them GND / +3V3 plane pads with no legal via site | DRC | Owner decision: hand route, add a signal layer, or cut a function |
| R-2 | No stackup, so no verified impedance for USB1 (90 ohm) or the Ethernet pairs (100 ohm) | Board setup has no stackup block | Obtain Sunstone's 6-layer proposal; set widths |
| R-3 | No fiducials | None in the board file (search of `Pilot.kicad_pcb`; analyzer FD-001 for B.Cu) | Add per `Pilot-Manufacturing-Transfer.md` 6 |
| R-4 | Copper close to the board edge: `C-IN1` 0.014 in (0.36 mm), `CAN-FD` 0.020 in (0.5 mm) | Analyzer PM-002 (13 + 7) | Confirm Sunstone's copper-to-edge limit |
| R-5 | 9 courtyard overlaps between the isolators and their section 13.1 parts, largest 0.0013 in2 (0.837 mm2) (`RS485`/`C-485-1`, `C-CAN1`/`CAN-TR`) | Analyzer PM-001 | The project rule `iso_section_13_1_courtyard` exempts `C-CAN1/3/4/6`, `CMC-CAN`, `C-485-1/4/6`, `CMC-RS485`, which is all nine pairs; confirm no pad contact |
| R-6 | Thermal vias under `1553-XCVR`: 4 of 9 minimum | Analyzer TV-001 | Add vias or accept; not a DRC rule |
| R-7 | Test-point coverage 7 / 104 nets | Analyzer TE-001 | Add test points or rely on the PB2 / JTAG access; owner decision |
| R-8 | 26 BOM lines lack a manufacturer part number | Schematic BOM export | Owner approves makers (`Pilot-Manufacturing-Transfer.md` 7) |
| R-9 | `L-USB1` datasheet not on file; land is a placeholder | WBS | Owner to download Darfon IP20162R2MP59 or equivalent datasheet |
| R-10 | TC1G00 is characterised for 1000BASE-T; 100BASE-TX suitability and the footprint transcription are unreviewed | REF-SENSOR-061 | Engineer-of-record review |
| R-11 | Power budget for the final 136-part design is not written down | `Pilot-HDD.md` 5 | Write it before release |
| R-12 | Mass and CG not computed | `Pilot-HDD.md` 2 | BOM mass roll-up |
| R-13 | `PWR-IN` connector land not datasheet-verified | WBS 1.2a | Obtain Molex drawing |
| R-14 | Part number / revision not on silkscreen | Manufacturing 2 | Add before release |
| R-15 | **Five through vias on non-exempt nets have their centers inside the section 13.1 bubble outlines, yet KiCad DRC does not flag them** | `+5V` (132.37, 97.46) and `GND` (141.95, 104.50), `GND` (145.33, 97.58), `SPI0_CLK` (146.97, 97.55), `GND2_RS485` (148.69, 106.27), mm. A test via planted at (145.8, 102.0) in `BUBBLE_485` **is** flagged (`items_not_allowed`), so the rule works; why these five escape was not found | Treat TI section 13.1 item 5 as **unverified** for these five. Relocate them (all are re-routable) and re-run DRC, or find the cause before any release |

## 3. Analyzer findings explained (not defects)

* **KO-001, 50 "keepout violations".** The analyzer reads only each rule area's own restriction list
  (`vias allowed` for the three areas) and tests bounding boxes, so it does not know the
  `bubble_*` and `iso_*` rules in `Pilot.kicad_dru`. The 50 split into 26 findings on components
  (21 against `ISO_BAND`, where the isolated parts belong, and 5 against a bubble, which were not
  individually checked: **OPEN**) and 24 on vias. Of the 24 vias: 6 are inside the `ISO_BAND`
  bounding box but outside its outline, 6 are inside a bubble's bounding box but outside its
  outline, 7 are on the converter nets the bubble rules exempt (`GND2_*_DCDC`, `VCC2_*_DCDC`), and
  5 are R-15 above, the only unresolved vias.
* **RT-001, 18 "errors".** Real, but already counted in R-1.
* **CP-002 (136 info), TB-001 (41 info), OR-001, CC-DET.** Informational.
* **CC-002, 20 warnings, `BUS_1553_N` narrow signal 0.127 mm.** A 0.005 in track on the 1553 stub is
  is a power-class question: the HI-6138 transmit bursts are 695 mA (DS6138 section 24.3, per the
  `refloorplan_pilot.py` note). **OPEN:** size the stub width for that current and the 1553 voltage
  levels before release.

## 4. Decision requested from the owner

1. How to finish routing (hand route in KiCad's interactive router; or a layer or function change).
2. Fab choices: thickness 0.062 / 0.063 in, finish, IPC class, Tg, ITAR / FAI flags.
3. Approve manufacturers for the 26 unnumbered BOM lines, or supply a DigiKey API key.
4. Fiducials and panel strategy for assembly at Cyber City Circuits.

## 5. Traceability

Requirement sources: `Pilot.md` (design history), `AGENTS.md` sections 3 to 5 (attribution, standards
vetting, component sourcing), owner decisions logged in `avionics/WBS.md` 1.2a. Analysis inputs:
`docs/analysis/schematic.json`, `pcb.json`, `emc.json`, `thermal.json` (kidoc / kicad analyzers,
2026-10-19; regenerate with the commands in `docs/README.md`).
