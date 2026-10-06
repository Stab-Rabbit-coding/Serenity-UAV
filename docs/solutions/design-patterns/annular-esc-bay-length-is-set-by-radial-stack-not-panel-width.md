---
title: Annular ESC bay length is set by the radial stack, not the panel width
date: 2026-10-03
category: design-patterns
module: nacelle ESC bay (64 mm pod) / Open-Secure-ESC 80 A
problem_type: design_pattern
component: tooling
severity: high
applies_when:
  - "A flat or hinged PCB must sit in the annulus between a duct and a skin"
  - "Trading board width against board length to make an ESC fit a nacelle"
  - "Choosing which components go on the duct-facing PCB face"
tags: [nacelle, esc, annulus, sagitta, hinged-pcb, radial-stack, ce-optimize]
---

# Annular ESC bay length is set by the radial stack, not the panel width

## Context

WBS NAC-64-ESC-80A (owner, 2026-10-03) needs two 6S / 80 A Open-Secure-ESC
boards against the 64 mm thrust tube. Both the bay and the ESC topology may be
restacked. `tools/esc80_cooptimize.py` co-optimises them. It ray-casts the 64 mm
skin by reusing the corner test in `tools/nacelle_esc_bay_fit.py`, sizes the
board from courtyard areas measured on the as-placed 50 A faceted board, and
reuses the lane-convection model in `tools/nacelle_esc_thermal.py`. Twenty
serial experiments took the fit margin from −199 mm to −6.5 mm. The run log is
in `.context/compound-engineering/ce-optimize/esc80-bay/`, which is gitignored.
Authors: Claude Opus 5.5 under Stab-Rabbit-coding.

## Guidance

1. **Shrink the radial stack before you shrink the board.** The usable bay
   length falls steeply with the envelope (stack plus cooling lane). With the
   hinged 23 + 10 mm pair at 37.2 mm inner radius:

   | envelope (mm) | 3 | 4 | 5 | 6 | 7 |
   |---|---|---|---|---|---|
   | bay length (mm) | 86 | 80 | 64 | 46 | 18 |

   Keep the duct-facing (inner) face down to FET-height parts. TPHR8504PL is
   1.0 ± 0.1 mm [OSE 49, p. 9]. Put every tall part (2.65 mm SOIC-20W
   isolators, the shield can) on the outer face. That one move added 32 mm of
   bay. A thinner access cover (0.10 → 0.06 in, 2.5 → 1.5 mm, structurally unverified) added
   10 mm more.
2. **Don't widen a hinged panel to buy length.** A flat chord of width w on
   radius R stands off the arc by R − √(R² − (w/2)²). Each extra millimetre of
   width pushes the outer corners into the skin, which costs more bay length
   than the width saves. Widths of 16 + 16, 20 + 14, 22 + 13 and 24 + 12 all
   lost to 23 + 12.
3. **Use both faces of the logic panel.** The 50 A logic panel had nothing on
   F.Cu. Using both faces was the single largest gain (−92 mm of required
   length).
4. **Read package areas from the schematic, not a stale PCB.** The 50 A
   faceted `.kicad_pcb` still carries an LQFP-64 MCU, but the schematic's U1 is
   MSPM0G3518-Q1 **RHB (VQFN-32)**. An area model built from the PCB alone
   overstates logic area by 139 mm².

**Update, same day (model 2):** the shortfall above was closed by giving each
ESC two neighbouring bays (power + logic), capping the power bay's outer face at
0.08 in (2.0 mm) because it holds no isolators, and parking harness loops in
the skin-thin rings beyond the board. Result: +0.13 in (+3.2 mm) and
+0.12 in (+2.96 mm) margin, T_ch 76.6 °C, with packing 0.75 counting 80 A pours
and thermal-via keep-outs (WBS NAC-64-ESC-80A.i).

## Why This Matters

An ESC that fits only on paper turns into an airframe respin. Following
intuition (make the board wider, because the board is "too long") made the fit
worse in every case tested.

## When to Apply

- Any PCB sited in a nacelle, boom or pod annulus.
- Before you lengthen an airframe bay to fit a board, check whether moving tall
  parts to the outer face recovers the length.

## Examples

Best point found, design file `tools/esc80_design.json`: 23 + 12 mm panels,
2 × TPHR8504PL per leg, inner face ≤ 1.1 mm, cover 1.5 mm, packing 0.60.
Result: 2.38 in (60.5 mm) needed against 2.13 in (54 mm) available. T_ch is 120 °C against the
125 °C design limit. The power panel is now the constraint. The 388 mm²
WE-SHC 3670209 frame is the biggest single area item. A smaller sourced can, or
two bays per ESC (both still need owner approval), would close the gap.

## Related

- `docs/solutions/design-patterns/probe-the-published-hull-and-change-the-placement-class-not-the-margins.md`
- `tools/nacelle_esc_bay_fit.py`: the corner-not-centre test this builds on
