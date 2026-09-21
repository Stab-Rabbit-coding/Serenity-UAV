---
title: "PocketBeagle 2 capes: verify every land against its OEM datasheet and budget real courtyards before layout"
date: 2026-09-19
category: conventions
module: "avionics/kicad (Pilot, XO, Observer, FlightEngineer, CAN-PERIPH-GW-1 capes)"
problem_type: convention
component: tooling
severity: high
applies_when:
  - "starting or re-spinning any PocketBeagle 2 cape or other avionics PCB in avionics/kicad/"
  - "a schematic symbol or PCB footprint was authored from memory, a prior board, or an AI brainstorm rather than the OEM datasheet"
  - "deciding whether a board's content fits before placement and routing begin"
  - "choosing packages, connectors, layer count or passive sizes for a 55 x 35 mm cape"
  - "a PCB DRC is red and the cause might be placement density rather than routing"
related_components:
  - avionics/kicad/Pilot/scripts/gen_pilot_sch.py
  - avionics/kicad/Pilot/scripts/gen_pilot_footprints.py
  - avionics/kicad/Pilot/scripts/gen_pilot_pcb.py
  - avionics/kicad/Serenity-Custom.pretty
  - avionics/datasheets
  - docs/ideation/2026-09-19-pilot-cape-four-bus-area-ideation.html
tags: [kicad, pocketbeagle-2, cape, footprint-verification, courtyard-budget, datasheet, isolation, pcb-layout, generator]
---

# PocketBeagle 2 capes: verify every land against its OEM datasheet and budget real courtyards before layout

## Context

The Pilot cape (Rev Q → Rev T, 2026-07 → 2026-09) was rebuilt schematic-first
because its schematic and PCB had become different designs. Every gate along
the way exposed the same two failure classes, and each one was invisible to
ERC/DRC until the board was already placed:

**Class 1 — parts that were never checked against silicon.** Found on Pilot
alone, each one a board that could not have worked or could not be soldered:

| Part | What the board had | What the datasheet says |
|---|---|---|
| u-blox SAM-M10Q | 16-pin symbol, 7-pad placeholder land | **20-pin** LCC; the omitted pins were VCC (17), RESET_N (18), EXTINT (19), GND (20) — no main supply |
| Würth 749010012A LAN xfmr | 12-pin symbol, 8-pad land | **16 mechanical pads** (4/5/12/13 have no winding); pad count must match for sch↔pcb parity |
| Infineon SLB 9672 TPM | SLB 9670 pin map, QFN-32 4x4 0.4 mm land | VDD 1/14/22, GND 2/9/23/32, 16 = NCI/GND, 10 = NCI/VDD pull-up, 6/29/30 must float; **UQFN-32 5x5 0.5 mm, EP 3.6** |
| Bourns SRF2012 CMC | pins 1 and 2 on the same end | windings are **1↔2 and 4↔3 across the length**; the old land put a winding across the differential pair (a short) |
| TI ISOW1044 | SOIC-16W land | **20-pin** SOIC-20W (DFM) |
| ADI ADM2795E | 20-pad land | 16-lead RW-16 — the 20-pad land actually fits the ISOW1412 the fleet later standardised on |
| Bosch BMP388 | 8-pad LGA 2x2.5 | **10-pin** LGA 2x2 |
| "1553 transceiver" | DS26LV31/32 RS-422 drivers | ~2 V differential cannot meet MIL-STD-1553B §4.5.2 bus levels; a real transceiver (Holt HI-1573, 3.3 V) + a 1:2.5 transformer (Premier PM-DB2791S) is required |
| ADIN1300 gigabit PHY | drifted in during EMI-hardening | `docs/AVIONICS_PB2_REDESIGN.md` §3.1 specifies **DP83825I** (3x3 mm WQFN, single 3.3 V, RMII Leader sources REF_CLK); the ADIN1300 dragged in a 0.9 V rail, 12 straps and two 50 MHz oscillators |

**Class 2 — content that cannot fit.** After every symbol was datasheet-correct
and every passive the datasheets ask for was added, a placement with the real
KiCad courtyards came to ≈ 95 % of both sides of the 55 x 35 mm cape; a 1 mm
free-cell map was 100 % black and four capacitors had nowhere to go. No router
finishes that. The estimates that had said "it fits" used body sizes, not
courtyards: a horizontal JST GH4 is 9.55 x 6.5 mm (62 mm²), not "about 8 x 4";
an SOIC-20W is 12 x 13.4 mm (160 mm²); a Würth 749010012A is 12.9 x 11.3 mm.

## Guidance

1. **Every symbol pin table and every land pattern comes from the OEM PDF in
   `avionics/datasheets/`, transcribed pin-for-pin, and the docstring cites the
   table/figure.** Connection diagrams in datasheets are usually raster images
   — `pdftotext` returns nothing; render the page (`pdftoppm -r 120 -f N -l N`)
   and read it. Record pins that "must not be connected" (SLB 9672 6/29/30) as
   explicit no-connects, and mechanical-only pads (749010012A 4/5/12/13,
   PM-DB2791S 5/6/7) as pins in the symbol so pad parity holds.
   The `datasheets` skill and `PILOT_FOOTPRINT_VERIFICATION.md` are the
   pattern; a land that cannot be traced to a drawing is a placeholder, not a
   footprint.

2. **When a datasheet is unreachable, say so in the footprint and pick the
   conservative land.** analog.com blocks this environment, so the ADIN1300
   CP-40-26 exposed-pad size could not be read; the footprint docstring named
   the source that was blocked and chose the smaller EP (a PCB pad smaller
   than the package pad still solders; a larger one bridges to the bus bars).
   Same rule for the Molex Nano-Fit land carried over without a drawing.

3. **Budget area with KiCad courtyards, not body sizes, before placing
   anything.** Load each footprint once and read its courtyard
   (`gen_pilot_pcb.py::courtyard()` does this via `GetCourtyard(F_CrtYd)`),
   sum per side, and compare against the usable band. On a PB2 cape the usable
   band between the two stacking rails is v 5.7–29.3 mm ≈ 1300 mm² per side,
   not 55 x 35. Anything above ~70 % per side is not routable on two signal
   layers; treat ~85 % as the ceiling even on six.

4. **THT parts cost both sides.** A THT header or connector blocks the
   opposite face too (pins, annular rings, keep-out). The 4x4 0.1 in
   PWM/DSHOT header reserved ≈ 130 mm² on B.Cu for nothing; the Samtec
   TSM-108 -DV SMT 0.1 in header (pads 1.27 x 3.68 mm, verified from the
   Samtec footprint print) keeps the same 0.1 in lead pattern on one face.
   **Do not** try this on the PB2 stacking rails: Samtec SSM-DV SMT sockets
   put their outer pad edge 3.94 mm from the rail centre-line and the PB2
   rails sit 2.54 mm from the cape edge, so the outer pad row would hang
   1.4 mm off the board. The rails stay THT.

5. **Isolation is what the board delivers, not what the chip is rated.**
   A 5 kV-reinforced ISOW1044/ISOW1412 terminated on a 0.5 mm ISOLATION
   netclass moat delivers a 0.5 mm barrier (IEC 60664-1 basic insulation
   alone wants ≈ 0.56 mm at 250 V working). Either restate the fleet claim
   as functional isolation at the cape with real creepage at the harness
   couplers, or design the barrier for real; do not carry a "5 kV" line the
   layout cannot honour. Encode the moat as a named rule area plus a
   `.kicad_dru` rule so DRC, not a reviewer's eye, enforces which nets may
   sit inside it.

6. **Generate, then gate.** Pilot's schematic, custom footprints and PCB are
   produced by three generators (`gen_pilot_sch.py`, `gen_pilot_footprints.py`,
   `gen_pilot_pcb.py`) from one part table; the gates are
   `kicad-cli sch erc --severity-all` (must be 0), `kicad-cli sch export
   netlist`, and `kicad-cli pcb drc --severity-all --schematic-parity`.
   Because the generator is the source, a part swap (SAM-M10Q → MAX-M10S,
   ADIN1300 → DP83825I) is a table edit that regenerates every downstream
   artifact, and the placer's collision report tells you immediately whether
   the swap fits. Hand-edit neither the `.kicad_sch` nor the `.kicad_pcb`.

7. **Prefer the part the architecture document already chose.** Two of the
   Pilot area problems were drift: the gigabit PHY that replaced the specified
   10/100 PHY, and an integrated-patch GPS module on a board that flies inside
   a Faraday pouch with external antennas in the dorsal cups
   (`docs/CARGO_SECTION_LAYOUT.md`). Check `docs/AVIONICS_PB2_REDESIGN.md`
   before accepting a "better" part.

8. **When the content still does not fit, decide with evidence, not by
   shaving margins.** The 2026-09-19 ideation
   (`docs/ideation/2026-09-19-pilot-cape-four-bus-area-ideation.html`)
   ranked the levers: SMT header + 6-layer (no electrical change), PHY per
   spec, one isolated island, 1553 as one placed unit, 0201 straps/arrays,
   connector consolidation, multidrop Ethernet. Three tempting ideas failed
   verification and should not be re-proposed: populating F.Cu between the
   THT rail pins (0.84 mm gap, a 0402 needs ≈ 1.25 mm), vertical GH4 to save
   area (62.4 vs 60.5 mm² — no gain), and sharing one magnetic core between
   1553 and Ethernet (incompatible ratio/impedance/bandwidth).

## Why This Matters

ERC and DRC only prove a design agrees with itself. A symbol with the wrong
pin map, a land with the wrong pad count, or an RS-422 driver labelled "1553
transceiver" passes both and produces a board that cannot power up, cannot be
soldered, or cannot meet the standard it claims. Every one of the Class 1
items above had passed ERC on at least one earlier revision. Area is the same
shape of problem one level up: a placement that "looks tight but OK" at body
size is unroutable at courtyard size, and discovering that after routing
starts wastes the whole layout pass. Both checks are cheap at the table-edit
stage and unrecoverable after fab. Every other cape (XO, Observer, Flight
Engineer, CAN-PERIPH-GW-1) shares the PB2 rails, the same isolators, the same
GH connectors and the same generator pattern, so the same checks apply
verbatim.

## When to Apply

- Before authoring or accepting any symbol/footprint pair: OEM PDF open, pin
  table cited, land pattern traced to a drawing.
- Before the first `gen_*_pcb.py` run: courtyard budget per side computed and
  under ~70 % (4-layer) / ~85 % (6-layer).
- Before adding a THT part to a cape: confirm the opposite face can afford it.
- Before writing "isolated" or a kV rating in a board document: check the
  moat the layout can actually hold.
- Before adopting a part not named in `docs/AVIONICS_PB2_REDESIGN.md`.
- XO is the next board to hit exactly this wall (same four buses, same
  envelope, ERC baseline 234); run the budget first.

## Examples

Courtyard budget, straight from the loaded footprints (the pattern the Pilot
generator uses):

```python
import pcbnew
fp = pcbnew.FootprintLoad("/usr/share/kicad/footprints/Connector_JST.pretty",
                          "JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal")
bb = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
print(bb.GetWidth() / 1e6, bb.GetHeight() / 1e6)   # 9.46 x 6.40 mm, not "8 x 4"
```

Pin table transcription with the source in the docstring (Pilot generator
style):

```python
{
    "ref": "GPS", "value": "MAX-M10S-00B", "fp": "RF_GPS:ublox_MAX",
    "ds": "MAX-M10S_DataSheet_UBX-20035208.pdf §3.1 Fig 2 / Table 10 (18-pin LCC)",
    "pins": [("8", "VCC", "+3V3", "L"), ("7", "V_IO", "+3V3", "L"), ...,
             ("11", "RF_IN", "GPS_RF", "R"), ("14", "VCC_RF", "GPS_VCC_RF", "R")],
}
```

Before / after for the isolation moat: a prose target of "≥ 8 mm creepage"
that no check enforced, versus a rule area named `ISO_BAND` on every copper
layer and a `Pilot.kicad_dru` rule that disallows any non-ISOLATION-class
track or via inside it — the DRC report, not a reviewer, now says whether the
barrier is intact.

## Related

- `avionics/kicad/Pilot/PILOT_FOOTPRINT_VERIFICATION.md` — the per-footprint
  verification report that started this.
- `docs/ideation/2026-09-19-pilot-cape-four-bus-area-ideation.html` — ranked
  options for the area problem, with the refuted ideas and their reasons.
- `docs/solutions/workflow-issues/generate-open-item-views-never-hand-patch-them.md`
  — the same generate-then-gate discipline applied to the WBS/TODO federation.
- `docs/AVIONICS_PB2_REDESIGN.md` §3.1 (part list), `docs/CARGO_SECTION_LAYOUT.md`
  (node envelope 58 x 37 x 22 mm, Faraday pouch, external GPS antennas).
