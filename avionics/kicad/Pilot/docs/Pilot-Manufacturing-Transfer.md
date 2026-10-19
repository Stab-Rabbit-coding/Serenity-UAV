# Pilot Manufacturing Transfer Package

**Document:** Pilot-MFG, Revision A (draft; **not released for fabrication**)  
**Board:** Pilot cape (CAPE-A-2), 6-layer, 55.0 mm x 35.0 mm  
**Date:** 2026-10-19  
**Owner:** sgriffing (Griffing Technology LLC)  
**Prepared by:** Claude Sonnet 5.5 (Anthropic)  
**License:** CC BY-SA 4.0

> **Release status: BLOCKED.** The board has 130 unconnected items (`Pilot-Design-Review.md`),
> so Gerbers exported today would describe an unfinished board. This package fixes everything that
> can be fixed before routing completes, and lists what Sunstone needs from the owner. Do not send
> an RFQ for a build until the blockers in section 8 are closed.

## 1. Fabricator and assembler

| Role | Choice | Basis |
| --- | --- | --- |
| Bare-board fab | **Sunstone Circuits** (owner direction 2026-10-19) | US-domiciled, AS9100D / ISO 9001 / ITAR-registered [REF-FAB-001]; 6 layers is a standard count; their capabilities list 1, 2 and 3 oz finished copper and nominal 0.062 in thickness |
| Assembly | Cyber City Circuits (owner direction 2026-10-19) | RFQ by e-mail with the quote form, Gerber package, board renders, firmware/QC notes; kitted parts accepted |

Cyber City Circuits suggests Sunstone (US-made), JLCPCB, PCBBuy and PCBWay as fabs and says fab is
arranged separately from assembly. JLCPCB and PCBWay remain fallback fabs. The board's 0.005 in
(0.127 mm) track and clearance rule is at or inside every limit verified for any of the three on
inner layers; outer-layer limits at Sunstone are not verified (section 3).

## 2. Sunstone data package (their PCB Data Checklist, 2026 edition) [REF-FAB-001]

| Checklist item | Status for Pilot |
| --- | --- |
| One Gerber per copper layer (1 to n) | Produced by `scripts/export_pilot_gerbers.sh`: F.Cu, In1 to In4, B.Cu |
| One per soldermask, silkscreen, paste layer | F/B.Mask, F/B.SilkS, F/B.Paste produced |
| Outline layer incl. slots and cutouts | Edge.Cuts produced; no slots, no cutouts except 4 mounting holes |
| Fabrication drawing in Gerber, 1:1 | **OPEN:** not produced (section 5 supplies the notes) |
| RS274X or ODB++, 2:5 imperial or 3:3 metric preferred | Script writes X2 with precision 6. **OPEN:** confirm Sunstone's preferred 2:5 / 3:3 against the script (`--precision 6` is KiCad's 4:6 metric) |
| PTH, NPTH, blind, buried, backdrill, slot files | Excellon, PTH and NPTH split. No blind, buried or backdrill. Slot file not needed |
| Part number and revision on silk or drawing, consistent | **OPEN:** board has no silk part-number / revision text |
| Overall dimensions to three decimals | 2.165 x 1.378 in (55.000 x 35.000 mm) |
| Board thickness | 0.063 in (1.6 mm) drawn. Sunstone's nearest listed options are 0.062 in and 0.078 in: **OPEN: choose 0.062 in or ask for 0.063 in** |
| Copper layers | 6 |
| Copper weight per layer and finished outer thickness | **OPEN:** not specified. Proposed for review: 1 oz finished on all layers |
| Minimum trace and space | 0.005 in / 0.005 in (0.127 mm) on all layers |
| Smallest drilled hole | 0.012 in (0.30 mm), plated vias. Sunstone's minimum drill is **not verified** (section 3) |
| Laminate | Default 150 Tg FR-4. **OPEN:** confirm no Tg requirement; lead-free assembly suggests Tg 170 |
| Solder mask color and sides | Proposed default, satin green both sides. Owner may change |
| Silkscreen color | Proposed default, white. Reference designators are on Fab, so silk carries only outlines and marks |
| Surface finish | **OPEN:** owner decision. The board has 0.016 in (0.4 mm) pitch QFNs and 0201 parts, which favor a flat finish (ENIG or similar) over HASL |
| Controlled impedance (layer, width, spacing, ohms) | **OPEN:** 90 ohm USB1, 100 ohm Ethernet pairs (`Pilot-HDD.md` 7); stackup not yet defined |
| IPC class | Default IPC-6012 Class 2 / IPC-A-600 Class 2 [REF-IPC-002]. **OPEN:** owner to decide whether Class 3 applies to the airframe |
| Special compliance (ITAR, aerospace) | **OPEN:** owner to state. Sunstone is ITAR-registered |
| First article inspection | **OPEN:** owner to state |
| Panelization | See section 6 |

## 3. What is verified about Sunstone's limits

Verified from sunstone.com on 2026-10-19 [REF-FAB-001]:

* 6 layers is one of the standard counts (4 to 20); finished copper 1, 2 or 3 oz;
  thickness 0.021 to 0.125 in; FR-4 stocked stackups.
* Inner-layer minimum trace/space at 1 oz: 0.005 in (Limited Review), 0.004 / 0.004 in (Online NRE),
  0.003 / 0.003 in (Custom). Inner clearances: 0.020 in larger than the finished hole; via pads
  0.016 in larger than the finished hole.

**Not verified** (the detailed-capabilities tabs are script-loaded and could not be read):
outer-layer trace/space, minimum drill and annular ring, copper-to-edge, solder-mask dam and
clearance, silkscreen minimums, surface finishes. The board's minimums are below.

| Board minimum | Value |
| --- | --- |
| Track / clearance | 0.005 in (0.127 mm) |
| Via | 0.024 in pad / 0.012 in drill (0.6 / 0.3 mm), annular ring 0.006 in (0.15 mm) |
| Hole to hole | 0.020 in (0.5 mm) |
| Copper to board edge | 0.012 in (0.3 mm) rule; the analyzer lists `C-IN1` at 0.014 in (0.36 mm) and the CAN-FD connector at 0.020 in (0.5 mm) |
| Finest pitch | AX88772E QFN-32, 0.016 in (0.4 mm); HI-6138 QFN-48, 0.016 in (0.4 mm); 0201 passives |

**Action:** ask Sunstone to confirm these against its tier that meets them, and whether copper-to-edge
0.012 in is acceptable (the 2008 DFM note found for the legacy EAGLE rule set quoted 0.020 in, which
this board would not meet at its edge connectors; the figure is dated and unverified).

## 4. Output set to generate when routing is complete

```bash
bash avionics/kicad/Pilot/scripts/export_pilot_gerbers.sh        # Gerber X2 + Excellon + drill map
kicad-cli pcb export pos --format csv --units mm --side both ... # position file
```

The position file and BOM are specified in sections 6 and 7. Run the gates first:
`kicad-cli pcb drc --schematic-parity --severity-all` (0 errors, 0 unconnected, parity 0) and
`kicad-cli sch erc` (0).

## 5. Fabrication notes (for the drawing, once the OPEN items above are decided)

1. Fabricate per IPC-6012 Class [2/3] and inspect per IPC-A-600 Class [2/3] [REF-IPC-002].
2. Material: FR-4, Tg [150/170] C minimum, 6 layers, finished thickness [0.062/0.063] in +/- 10 %.
3. Copper: 1 oz finished, all layers [owner to confirm].
4. Minimum trace and space 0.005 in. Minimum drilled hole 0.012 in (plated vias, 0.006 in annular ring).
5. Controlled impedance: USB1 pair 90 ohm differential, Ethernet pairs 100 ohm differential, +/- 10 %,
   on layers and widths per the fabricator's stackup proposal; supply a coupon.
6. Solder mask: satin [green], both sides, LPI. Silkscreen: white, both sides.
7. Surface finish: [owner to select; flat finish recommended].
8. Mounting holes: 4 x 0.106 in (2.7 mm) M2.5 clearance, **plated**, 0.142 in (3.6 mm) pad ring bonded to PGND (footprint `MountingHole_2.7mm_M2.5_PGND_Ring`).
9. No blind, buried or backdrilled holes. No slots. No castellations.
10. Mark with fabricator logo, UL flammability, date code on the back, outside the copper areas.
11. Netlist test required (100 %); report with the shipment.
12. Part number `[PILOT-PCB]` revision `[A]` on both silk layers **(not yet on the board)**.

## 6. Assembly data (Cyber City Circuits)

| Item | Status |
| --- | --- |
| Quote form | `CCC-Quote-Form.xlsx` (their template, updated 31 Dec 2025); owner to complete |
| Position (centroid) file | Generate from the PCB. The footprints in `Serenity-Custom.pretty` use KiCad rotation conventions; **OPEN:** confirm Cyber City's rotation convention on the first article |
| Both sides populated | Yes (67 F, 69 B); the B side sits under the PB2-I, height limit 0.020 in margin (`Pilot-HDD.md` 2) |
| Fiducials | **OPEN, a design gap:** the analyzer reports none on B.Cu, and the 0.016 in pitch QFNs and 0201 parts need them. The 55 x 35 mm board has no free edge; plan rail fiducials or 3 small copper fiducials (0.040 in dot, 0.080 in mask opening) per side |
| Panelization | The board is below JLCPCB's 2.76 in (70 mm) shorter-side rule. Cyber City asks for 0.2 in (5 mm) edge rails on all four sides and tooling holes of 1.05, 1.55, 2.05, 2.55 or 3.05 mm, panels under 5.9 in (150 mm) square. The board's own holes are 2.7 mm (not a listed size). **OPEN:** build a panel with rails, or assemble on tooling holes |
| Stencil | Framed stencil for volume; flex or framed for prototype. Paste layers are exported |
| Parts supply | Kitted, with each bag marked "job number + BOM line number" (their request); 10 % overage on parts, 20 % on 0402 and smaller |
| DNP | `R-CANT`, `R-485T` (120 ohm terminations) are DNP by default |
| Through-hole / hand parts | `PWR-IN` (Nano-Fit), `J-PWM` strips if not SMT, PB2 rails (5 THT total) |

## 7. Bill of materials

Generated from `Pilot.kicad_sch`, 56 grouped lines. **26 lines have no manufacturer part number**
(generic passives, the mounting holes, and `L-USB1`). A kitted or turnkey order needs one per line.
They are specified below by electrical value and package so the owner can approve makers; no part
numbers are guessed.

| Qty class | Spec | Package |
| --- | --- | --- |
| 100 nF, 10 nF, 1 uF, 15 pF C0G | MLCC, 10 V minimum, X7R / X5R (C0G for 15 pF) | 0201, 0402 |
| 4.7 uF, 10 uF | MLCC X5R, 6.3 to 10 V, DC-bias derating checked per REF-PWR-011 for 22 uF only; **OPEN:** repeat for the others | 0603, 0805, 1210 |
| 10 nF 2 kV | MLCC X7R, 2 kV, `C-RMII2-BS`, `C-USB1-BS` (Bob-Smith) | 1808 |
| 0 R, 55 R 2 % (use 54.9 R 1 %), 75 R, 120 R, 200 R, 2.49 k, 4.7 k, 6.49 k 1 %, 10 k, 24 k 1 % | Thick-film chip resistor, 1 % unless stated | 0201, 0402, 0603, 0805 |
| 2.2 uH | Power inductor for `L-USB1`, >= 0.2 A saturation | 2016 (0806) **OPEN:** MPN, datasheet not on file |
| Mounting hole | Not a purchased part (`H1`..`H4`); drop from the BOM | n/a |

Parts with known part numbers are in the schematic's `MPN` and `Manufacturer` fields (for example
`TC1G00`, `ESD2CAN24DCKRQ1`, `CDSOT23-SM712`, `SMAJ33CA` by Bourns, `ECS-200-20-33-AGM-TR`, `AX88772EQF`).

## 8. Release blockers

1. Finish routing: 130 unconnected items.
2. Define the stackup and set impedance targets (needs Sunstone's proposal).
3. Resolve OPEN items in section 2 (thickness, copper, finish, IPC class, ITAR, FAI).
4. Add fiducials, board part number and revision, and decide the panel.
5. Assign part numbers to the 26 BOM lines; get the `L-USB1` datasheet.
6. Run all gates, regenerate Gerbers, run `kicad` fab-release gate and a Gerber viewer check.
7. Engineer-of-record review of the TC1G00 suitability and footprint transcription.
