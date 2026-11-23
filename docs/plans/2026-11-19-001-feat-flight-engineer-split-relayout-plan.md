---
title: Flight Engineer Split Re-layout and High-Current Fix - Plan
type: feat
date: 2026-11-19
topic: flight-engineer-split-relayout
artifact_contract: ce-unified-plan/v1
artifact_readiness: requirements-only
product_contract_source: ce-brainstorm
execution: code
---

# Flight Engineer Split Re-layout and High-Current Fix - Plan

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (Anthropic) under the author's direction, 2026-11-19, per AGENTS.md section 3.
License: CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)

> ENGINEERING REVIEW REQUIRED. Every figure here is an estimate from the session tools named below and must be reviewed and accepted by a qualified engineer before hardware is built. CAUTION per `AGENTS.md`: the power-path findings are aircraft-loss findings; WARNING only if people are under the hover.

---

## Goal Capsule

- **Objective:** re-architect the Flight Engineer (FE) power distribution unit as two modules that fit the TEDF-06 cargo duct, with a power path rated for today's loads; fold Flight Engineer Rev S1 into the new logic module; also grow the belly service panel and reserve the nacelle cable corridor in the duct tool.
- **Product authority:** owner (Steve Griffing). Scope chosen 2026-11-19 in the S44 session and in the PR #309 review threads.
- **Open blockers:** an in-line packing at the 8,000 mm2 floor is found by a session search and still needs confirming in the tool and in CAD (OQ6).

---

## Product Contract

### Summary

Split the Flight Engineer into a bus-bar power module (about 45 x 70 x 45 mm, 1.77 x 2.76 x 1.77 in) at the roof centre over the spar bore and a logic module (about 60 x 40 x 18 mm, 2.36 x 1.57 x 0.71 in), with every board in the duct lying in line with the airflow.
Rebuild the power path for the 190-214 A sustained bus.
Extend `tools/cargo_duct_layout_fit.py` so the duct's inner walls wrap the modules, a nacelle cable corridor is kept clear, and the belly panel reaches every fuselage avionics unit without its own hatch.

### Problem Frame

The U6 duct tool finds no station for the 75 x 94 x 36 mm (2.95 x 3.70 x 1.42 in) FE unit in any orientation.
A session free-space search through the whole interior (floor, roof and wall pockets, using the height the retired cargo freed: Z 88-234 on the centreline) also rejects a slimmer can and a single long narrow board. The hull is narrow rather than low: 70-154 mm (2.8-6.1 in) wide at Z 150, narrowest at Y 288 and at the pivot. Against the bare hull the single can fits only on edge on the centreline from Y 334 aft, into N2/N4 and the Observer tray, and at the 11,800 mm2 floor the bay is also cut along Y by stream headroom (Y 312 has 49 mm2, Y 328 has 307 mm2).
Separately, Rev R was sized for 18 A per fan. Today's design currents are 44 A sustained and 63 A peak (10 s or less) per nacelle fan (`docs/ESC_RATING_OD3_BRIEF.md`, ESTIMATE), plus 32 A for the tail fan at hover. That puts the main bus at about 190 A mean, 214 A worst sustained (4 x 44 A + 32.4 A tail + 5.1 A BEC input) and 320 A for 10 s or less (4 x 63 A + 63.3 A tail at full throttle + 5.1 A), or 107 A per pack with the twin packs sharing evenly. Several Rev R parts are below those currents:

| Rev R part | Rating in the repo | Today's duty |
|---|---|---|
| Q_BATT_DSG, one DFN5x6 FET | 30 A | 214 A, about 68 W at an ASSUMED 1.5 mOhm |
| F1, 150 A MAXI | about 120 A derated at 122 F (50 C) | 190-214 A sustained |
| J_ESC1-4, XT30 | 30 A continuous | 44 A |
| CM1, CM2, CM_ESC1-4, Wurth 7440640500 | 10 A (part number not found in the maker's catalog; requires verification) | 44 A per branch, 214 A on the bus |
| RS_MAIN, 1 mOhm 2512, 3 W | 3 W | 46 W at 214 A |
| RS1-4, 1 mOhm 2512, 3 W | 3 W | 4.0 W at 63 A |
| Main bus as 4 oz pours | IPC-2221 gives about 79 mm (3.1 in) of one-layer width at 214 A for a 36 F (20 C) rise, extrapolated beyond the chart's range | -- |

### Key Decisions

- **The duct changes only at its inner walls.** The hull outer mold line stays; the sealed duct partition is reshaped to pocket the modules. Governs R10. (session-settled: user-directed -- chosen over changing the outer mold line or keeping the duct fixed: least disruption to aero and the published hull)
- **One plan covers the split and the high-current fix.** Governs R1-R9. (session-settled: user-approved -- chosen over fixing the power path first in its own plan, and over a split that keeps the on-board 44 A common-mode chokes: the power path sets the module's form, and the on-board chokes are unlikely to fit)
- **The belly panel grows to reach every fuselage avionics unit that has no hatch of its own, and may span the whole flat bottom of the cargo section, edge to edge, from the intake ramp to where the hull necks down toward the tail EDF, cut out only for the landing gear bays, inside a sealing frame land for the gasket and captive fasteners.** Governs R12. (session-settled: user-directed -- owner PR #309 review and session, 2026-11-19; no restriction to the door field's width; the sealing frame land kept by the owner in the plan review)
- **The spar bore carries the four nacelle EDF cables.** Any seal is a pass-through around them, and the bay keeps a corridor from the bore to the FE. Governs R11, R13. (session-settled: user-directed -- owner PR #309 review, 2026-11-19)
- **Every PCB lies in line with the airflow; no board stands across the stream as an air dam.** Governs R16. (session-settled: user-directed -- owner, 2026-11-19; a standing rule in `airframe/AGENTS.md`)
- **The stream floor is 12.4 in2 (8,000 mm2) at every bay station, and future changes hold it.** About -0.7 % hover tail thrust in `tools/tail_edf_flow.py` (a lower bound: constant k_cargo, no obstruction loss), against -1.6 % at 6,000 mm2; both pack every board in line, and 11,800 mm2 leaves the Observer no in-line station. Governs R15. (session-settled: user-directed -- chosen over 11,800 mm2, where the in-line Observer has no station, and 6,000 mm2, at -1.6 %: owner, 2026-11-19)
- **Per-branch noise suppression moves to the cables and the ESCs (option A), plus a source-side common-mode choke on each ESC input where it fits (option C).** Governs R9. (session-settled: user-directed -- chosen over 44 A chokes kept on the Flight Engineer (option B), which are unlikely to fit the power module: owner, 2026-11-19)
- **Heavy current runs in copper bars, lugs and bolt-down or blade fuses, not PCB copper.** A 3 x 10 mm (0.118 x 0.394 in) bar dissipates 1.8 W and drops 8.6 mV per 70 mm (2.76 in) at 214 A; two 30 mm (1.2 in) 4 oz pours dissipate 6.5 W. Governs R3, R4.

### Requirements

**Form and placement**

- R1. The FE is two modules, a power module and a logic module, each fitting the duct with the hull gap, every placed envelope's gap and the stream floor of R15.
- R2. The power module sits within reach of the spar-bore corridor (R11) so the nacelle cables run straight from the bore to their branch fuses; the in-line packing of OQ6 places it at X -33..12, Y 304-374, Z 162-207 mm (an earlier fit at Y 330-400 predates R16).

**Power path (power module)**

- R3. The main bus and every branch carry their design current continuously, and their peaks for 10 s, without exceeding the conductor's or terminal's rating at a 122 F (50 C) bay ambient.
- R4. Each nacelle branch has a fuse that carries 44 A continuous and 57-63 A for 10 s and clears a wiring fault before the pack fuse; the coordination is the NAC-64-FUSE-COORD study, which this plan adopts.
- R5. Each pack input has its own fuse, and no single fault, a blown fuse included, dumps its load or fault energy onto the other pack or ends in an uncontrolled descent: losing one pack leaves a deterministic degraded mode in which the flight control limits load to what the surviving pack and its fuse can carry and flies a controlled landing. (The twin packs share about 107 A each at the 214 A bus; how they are isolated and how the load is limited is OQ10.)
- R6. Branch outputs use connectors or bolted lugs rated at or above the branch current.
- R7. Branch current is measured with a shunt that stays inside its continuous rating at 44 A and inside its pulse rating at 63 A for 10 s; the session sizing gives 0.5 mOhm (1.0 W and 2.0 W).
- R8. The pack's state and disconnect function survives, but no series element carries the bus current unless its dissipation fits the module's cooling.

**EMC**

- R9. The per-branch noise isolation of Rev R moves off the Flight Engineer: shielded twisted-pair ESC cables with clamp-on ferrites at both ends outside the spar bore (inside it the four unbound 10 AWG conductors of NAC-64-WIRE-QUAL stay as built), one bus-level filter at the power module input, RC filters on the INA226 sense lines, and the bulk ripple capacitance on each ESC; a common-mode choke rated for the branch current is added at each ESC's input wherever it fits on the ESC board. The 500 W/m2 immunity stays with the enclosure, glands, Y-capacitors and TVS.

**Duct tool**

- R10. `tools/cargo_duct_layout_fit.py` places equipment in wall and roof pockets anywhere in the cross-section, not only on the floor or hung from the roof, and gates the two FE modules.
- R11. The tool keeps a nacelle cable corridor clear from the spar bore at each hull wall to the power module (the session used X +-55, Y 327-352, Z 135-159 mm).
- R12. The tool takes the belly panel opening as the flat bottom of the cargo section from the ramp to the neck-down, less the gear bays and the frame land, and every fuselage avionics unit without a dedicated hatch passes the reach gate as a hard pass/fail (at least 0.5 of its footprint inside the opening inset 0.4 in (10 mm), the tool's REACH_MIN rule; vertical access to roof pockets is a separate CAD check).
- R13. The U13 spar-bore seal is specified as a pass-through around the four 10 AWG conductors in each spar (two per nacelle ESC, 5.5 mm envelope, a 13.28 mm bundle in the 16.3 mm bore, `airframe/wings-nacelles/WBS.md` SPAR-20-WIREOD), keeping the bore's free area for them.
- R15. The tool gates the stream against 8,000 mm2 (12.4 in2) of free area at every bay station, kept equipment included (a station below the floor today does not stay below it), and reports the tail-fan thrust cost of that floor from `tools/tail_edf_flow.py` as a lower bound.
- R16. Every PCB envelope in the duct (FE modules, speed controller, gateway, N2/N4, Observer, chin nodes, tilt controller) has its thinnest side across the flow (along X or Z), never along Y, and the tool fails any board that faces the stream. Re-laying the kept N2/N4 nodes and the Observer tray on edge is part of this plan (OQ6).

**Logic module**

- R14. The logic module carries the trust module (MCU, TPM, isolated CAN-FD and RS-485), the cell monitor and the BECs, and folds in Rev S1 (the 6 V BEC removed, a third 5 V BEC added); it carries no current above the BEC inputs (about 5 A).

### Acceptance Examples

- AE1. **Covers R1.** Given the U6 layout with the FE modules placed first, when the speed controller, gateway and three RCS servos are placed after them, then all place and every bay station keeps at least the R15 floor.
- AE2. **Covers R11.** Given the corridor keep-out, when any equipment envelope overlaps it, then the tool reports the overlap as a failure.
- AE3. **Covers R12.** Given a fuselage avionics unit with no dedicated hatch whose footprint is less than half inside the inset panel opening, then the tool exits nonzero and names the unit.

### Scope Boundaries

- Outside this plan: the outer mold line. The hull throat at Y 288-296 has 11,259 mm2 (17.5 in2) of cavity with nothing in it; TEDF-03 takes the least station area, not the 12,750 mm2 midpoint, as a_cargo.
- Deferred: the ideal-diode ORing of the twin packs (`docs/POWER_DISTRIBUTION.md`) beyond what R5 and R8 need.

### Dependencies / Assumptions

- The currents are ESTIMATES from `docs/ESC_RATING_OD3_BRIEF.md` and `tools/tail_edf_flow.py` (1,368 W full, cube law at 0.8 throttle, 21.6 V).
- The module envelopes have almost no margin. A 90 mm long or 50 mm wide power module, a larger logic module, or a taller power module that displaces RCS servos does not fit. A CAD pass of the real part stack is needed before the envelopes are fixed.
- `tools/tail_edf_flow.py` takes k_cargo = 1.0 (ASSUMED) and counts only the free area, so the thrust cost of R15 is a lower bound that leaves out drag from the placed modules; the TEDF-03 bench run calibrates it.
- The bar's temperature rise assumes a convective h of 50 W/m2K in duct air (ASSUMED), giving about 11 K/W per 70 mm bar.

### Outstanding Questions

**Resolve Before Planning**


- OQ6. Packing under R16. The kept N2/N4 nodes (58 x 37 mm boards, 22 mm along Y) and the Observer tray stand across the flow today and must be re-laid. The cargo Observer is the nose design's trapezoid (25.4 mm narrow end, 58 mm wide end, 69.85 mm long, `avionics/kicad/Observer/mod_vera_trapezoid.py`) with its camera, laser and ToF on cables, so it can stand on edge (modelled as the outline grown 2 mm for the Faraday can, 20 mm across X, ASSUMED). A session greedy fit (boards toward the walls, corridor kept) places every board in line and every moved item at a floor of 8,000 mm2 (least station 8,084 mm2 at Y 288) or 6,000 mm2 (6,962 mm2): FE power module X -33..12, Y 304-374, Z 162-207; FE logic module flat over it or on the port wall; Observer on edge, wide end down, at X -18..2, Y 368-430; N2 and N4 on edge at X -48..-20 and 7..35, Y 376-417. At 11,800 mm2 no greedy order places the Observer. Planning confirms a packing in the tool and in CAD, and checks the forward items' effect on the ramp inflow and on the tail motor lead.

**Deferred to Planning**

- OQ2. Pack fuse form (MAXI with a holder, or a bolt-down MEGA/ANL class) and branch fuse form (60 A MAXI, derated to 48 A at 122 F), from the NAC-64-FUSE-COORD curves.
- OQ3. R8's disconnect: a parallel FET bank (about 8 x 0.6 mOhm, 3.4 W at 214 A) or an arming plug that leaves BQ76930 as monitor only.
- OQ4. Where the INA226s sit: beside the shunts in the power module (short Kelvin lines, I2C across) or on the logic module.
- OQ5. The CG effect of the two module masses against the 158 g single-unit row (TEDF-04 pricing).
- OQ7. R9 verification before G1: one ESC at full PWM, measure the noise it couples into the other branches' INA226 readings and the conducted emissions on the bus (MIL-STD-461G [REF-MIL-002] as the guide, limits to be checked against the standard); and whether the source choke fits each ESC board (OSESC-NAC 44 x 33 mm, OSESC-TAIL-1) without moving the nacelle mass budget.
- OQ8. R8's disconnect: must the surviving pack disconnect act automatically on a BQ76930 overcurrent or short-circuit fault, or may it be a manual arming plug with the fuses as the only automatic protection? (Plan review finding, deferred.)
- OQ9. R9's acceptance limit: the branch-to-branch noise coupled into the INA226 readings and the bus conducted emissions at which the cable-ferrite-only fix passes G1 if the source choke does not fit an ESC board.
- OQ10. R5's mechanism: how the twin packs are isolated so a fault or full bus never lands on the survivor, how the load is limited in the degraded mode, and whether a second pack is always fitted (`docs/POWER_DISTRIBUTION.md` section 11 RBM) or optional.

### Sources / Research

- Session scripts (not committed): the free-space search and the FE-first placement over `tools/cargo_duct_layout_fit.py`.
- `avionics/kicad/FlightEngineer/FlightEngineer.md`: Rev R BOM, enclosure, connectors.
- `docs/POWER_DISTRIBUTION.md` sections 5.2, 5.3 and 9.4: XT30 rating, fuse derating, main fuse sizing.
- `airframe/wings-nacelles/WBS.md`: NAC-64-FUSE-COORD.
- `avionics/rev-s1/WBS.md`: Flight Engineer Rev S1.
- Littelfuse MIDI 498 series, product pages: bolt-down and in-line holders only; no PCB holder was found.
