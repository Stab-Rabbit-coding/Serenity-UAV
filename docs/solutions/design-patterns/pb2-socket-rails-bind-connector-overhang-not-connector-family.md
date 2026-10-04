---
title: "PB2 socket rails, not connector families, bind field-connector placement on a 55 x 35 mm cape"
date: 2026-10-04
category: design-patterns
module: avionics/kicad/TACCO
problem_type: design_pattern
component: tooling
severity: high
applies_when:
  - "Moving or swapping field connectors (JST-GH, CLIK-Mate, Pico-Clasp, ZE) to overhang PocketBeagle 2 socket rails on a cape"
  - "Top-side SMD pads are placed over bottom-mounted THT rail sockets whose pads exist on every copper layer"
  - "Evaluating an SMT rail socket (e.g. Samtec SSM-DV, Mill-Max SMT) to free rail-area copper"
  - "Courtyard checks pass but connector and socket courtyards are on opposite faces (F.CrtYd vs B.CrtYd)"
  - "Measuring layout what-ifs on a generator-built board instead of hand-edited PCB copies"
symptoms:
  - "kicad-cli DRC on hand-edited TACCO-2 reported 129 violations incl. 34 shorting_items and 48 solder_mask_bridge"
  - "Connector MP (PGND) pads short PB2-P1/P2 rail pads while courtyard overlap checks report nothing"
root_cause: logic_error
resolution_type: workflow_improvement
related_components:
  - documentation
  - development_workflow
tags:
  - pocketbeagle2
  - cape-layout
  - socket-rails
  - jst-gh
  - samtec-ssm
  - kicad-drc
  - courtyard
  - tacco
---

# PB2 socket rails, not connector families, bind field-connector placement on a 55 x 35 mm cape

## Context

On the TACCO cape (`avionics/kicad/TACCO`, 55 x 35 mm, 6-layer, ~170 parts) the owner hand-sketched `TACCO-2.kicad_pcb`, sliding J-CAN, J-485, J-ETH and J-FAN 3.9-4.3 mm toward the board edges so they sat over the PocketBeagle 2 (PB2) P1/P2 socket rails, and asked for a connector swap that would let the connectors overhang the rails with every solder point still in a legal area.

The connector was not the limit. The PB2 rail footprint is. A rail of plated through-hole pads on every copper layer, spaced on a 2.54 mm grid, leaves almost no room for another part's pads. Swapping connector families can't fix that. The only thing that frees the rail area is a rail socket whose SMT pads sit under its own body, on the pin grid. Samtec SSM-DV does not meet that requirement.

## Guidance

1. **Check what the rail pads leave before you propose a connector swap.** The PB2 socket footprint places 1.700 mm pads with 1.000 mm drills at a 2.54 mm pitch, in two rows at y = -1.270 and +1.270 mm from the rail centreline, on `*.Cu` (`avionics/kicad/Serenity-Custom.pretty/PocketBeagle2_2x18_P2_Socket.kicad_mod:18-53`, descr at line 6). The gap between adjacent pad edges is 2.54 - 1.70 = 0.84 mm on every layer. At the board's 0.127 mm clearance, nothing wider than 0.84 - 2 x 0.127 = 0.586 mm fits in that gap.
2. **A courtyard check does not catch this. Run DRC.** The sockets mount on the bottom face (courtyard on B.CrtYd), while the field connectors are on the top (F.CrtYd). Overlapping courtyards on opposite faces raise no error, but the THT pads are on F.Cu as well. Run `kicad-cli pcb drc --severity-all --schematic-parity` after moving any part near a rail. On the TACCO-2 sketch, DRC reported 129 violations, including 34 `shorting_items` and 48 `solder_mask_bridge` (measured this session). Examples: the J-CAN MP [PGND] pad shorted PB2-P2 pads 3, 4, 9 and 10, and the J-ETH MP pad landed on PB2-P1 pads 29, 30, 35 and 36.
3. **No library connector family has a long enough cantilevered nose.** A screen of the KiCad 9 libraries (3/4-position SMD latching wire-to-board connectors from JST, Molex, Hirose, Harwin, TE, Amphenol, Wuerth and AMASS) found at most 2.0 mm of courtyard overhang beyond the outermost pad (JST ZE SM0xB-ZESS-TB, 117-134 mm²). Molex CLIK-Mate reached 1.8-1.84 mm, Molex Pico-Clasp 202396-0407 1.25 mm at 58.0 mm², and JST-GH4 0.55 mm at about 62 mm²; every Hirose, Harwin, TE, Amphenol, Wuerth and AMASS candidate overhung less than the 2.0 mm maximum (all measured this session). Clearing a two-row 2.54 mm rail takes more than any of these. JST-GH's 1.25 mm pitch also can't interleave with the 2.54 mm grid. Keep the fleet convention of shielded JST-GH with SHIELD tied to PGND (`avionics/kicad/TACCO/TACCO.md:446`).
4. **An SMT rail socket only helps if its pads stay under its body.** On TACCO the rail centreline is 2.565 mm from the board edge (P1 rows at y = 88.77/91.31 mm, edge at 87.475 mm; measured this session). With 0.3 mm of edge clearance, the outer pad edge must be no more than about 2.26 mm from the centreline. Samtec SSM-DV fails this (see Examples).
5. **Measure layout ideas on a regenerated board, not by hand-editing.** Use the generator's what-if hook: `TACCO_WHATIF=<file.json>` (`avionics/kicad/TACCO/scripts/gen_tacco_pcb.py:61-68`) overrides fixed positions, footprints and the rail cells (`RAIL_CELLS`, `gen_tacco_pcb.py:318`; dropped by `"rail_cells": false` at `:651`) and writes to a scratch directory. The placer walks each part's anchor nets in sorted order (`:707`); before that fix the walk followed `PYTHONHASHSEED` and about 23 parts moved between identical runs, so a what-if comparison is only meaningful on the deterministic generator. Blind straight-line offsets applied to the GH connectors produced 17 DRC errors; each offset has to be solved against the actual pad geometry.

## Why This Matters

- A connector-swap request near the rails can burn a full sourcing and footprint cycle and still not work, because the rail geometry is what limits the layout.
- The existing convention (`docs/solutions/conventions/pb2-cape-datasheet-verified-footprints-and-courtyard-budget-before-layout.md:85-93`, "The rails stay THT") stated the SSM-DV conclusion without the drawing figures. This learning adds the figures and the cross-face DRC trap. One small discrepancy: that doc gives 2.54 mm from the rail to the cape edge, while 2.565 mm was measured on TACCO. The conclusion holds either way. The same doc (`:121-131`) already lists populating F.Cu between the rail pins as a failed idea, because a 0402 needs about 1.25 mm against the 0.84 mm gap.

## When to Apply

- Any PB2 cape layout where parts on the opposite face are moved toward or over the P1/P2 rails.
- Any proposal to replace the THT rail sockets with SMT sockets.
- Any time someone asks for a "smaller connector" to recover edge area beside the rails.

## Examples

**Pad-to-rail geometry check (Samtec SSM-DV).** Source: `avionics/datasheets/samtec_ssm_footprint.pdf`, Rev D. Figure 4 (-DV) gives an inner pad span of .135 in (3.43 mm), an outer span of .310 in (7.87 mm) and a pad width of .040 in (1.02 mm). Figure 6 (-DV-BE) gives an outer span of .315 in (8.00 mm). Confirmed with `pdftotext -layout`.

```
outer pad edge from CL = 7.87/2 = 3.94 mm        (BE: 8.00/2 = 4.00 mm)
rail CL to board edge  = 2.565 mm (TACCO)
overhang               = 3.94 - 2.565 ≈ 1.4 mm off the board  -> fails
budget                 = 2.565 - 0.3 edge clearance = 2.26 mm max outer pad edge
```

**JST-GH 0.60 mm signal pad in the rail inter-pad gap:**

```
need = 0.60 + 2 x 0.127 = 0.854 mm  >  0.84 mm available  -> short by 0.014 mm
```

**Pad-to-rail-pad slack at the current deterministic placement** (measured this session): J-CAN 0.52 mm, J-485 0.64 mm, J-ETH 0.94 mm, J-FAN 0.94 mm, J-1553 1.96 mm, J-SD (bottom) 1.70 mm, PWR-IN (Nano-Fit) 3.31 mm, J-ANT-RADIO 1.85 mm. Sliding GH connectors right up to the rail recovers only 0.4-0.8 mm each.

**What-if area results** (generator what-if hook, commit on branch `claude/tacco-pcb-manufacturing-pi49u8` (merged in PR #228); 0.25 mm grid, courtyards plus THT pad rectangles +0.2 mm; measured this session):

| Scenario | Placement DRC | Free top-face area | Free inner-layer area |
|---|---|---|---|
| Baseline: THT rail sockets | 0 | 177.0 mm² | 1336.1 mm² |
| GH connectors slid toward the rails (THT rails), blind offsets | 17 errors | 235.2 mm² (about +58 mm² ceiling) | 1341.8 mm² |
| Hypothetical SMT rails (1.0 mm pads on 2.54 grid, bottom only, no barrels) | 0, parity 0, 170/170 placed | 504.9 mm² | 1701.9 mm² |

The routing comparison between these scenarios is still pending.

**Unverified leads.** Vendor sites are blocked by this environment's network policy, so none of these has been checked:
- Mill-Max double-row SMT tape-and-reel machined sockets. A press release says the tails sit under the body, but no part number or drawing has been confirmed. Check its footprint against the 2.26 mm budget before relying on it.
- PB2 mounting holes are not confirmed against the PB2 drawing. The cape currently has H1-H4 at the rail ends, and TACCO.md notes "Mounting holes × 4: PGND via 0 Ω solder-selectable links". If SMT rails are adopted, the mechanical retention approach still needs analysis: through-pins only at the rail ends, anti-vibration measures, and trimming the socket tails flush plus conformal coating.

## Related

- `docs/solutions/conventions/pb2-cape-datasheet-verified-footprints-and-courtyard-budget-before-layout.md` — parent convention (rails stay THT, courtyard budget, failed area levers); this doc adds the Samtec drawing figures, the cross-face DRC trap and the connector-family screen.
- `CONCEPTS.md` — Cape Usable Band.
