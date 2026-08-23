# Deferred Work — Agent Instructions

> *See the root `AGENTS.md` for project-wide policies. This file provides specific guidance for deferred (Phase 11+) design work, planned upgrades, and items awaiting future implementation.*

## Scope

This folder holds design specifications, analysis, and artifacts for work that is
**intentionally deferred** beyond the current build baseline (Phases 5–10): planned upgrades to
current components, future system additions (Phase 11 — rear EDF + RCS, aft intake scoop
geometry), analyses of alternative designs evaluated but not selected, and Phase 12+ long-term
enhancements. Phase 1–4 prototype-airframe work is archived. Nothing here is part of the active
build baseline. When a deferred item becomes active it is incorporated into the relevant phase's
documentation and build guide; the phase table itself lives in `graphical-build-guide/AGENTS.md`
"Phases Overview" and must not be restated here.

## Status Categories

### Planned (High Priority — Next Release)

Rev R1 detailed changes, target integration Phase 6–7:

- **Commo Rev R1:** add LoRa; replace JST GH 6P with P1+P2 socket rails
- **XO Rev R1:** remove LoRa (migrated to Commo); add P1+P2 passthrough rails matching the Commo
  pinout on the River and Simon stacks
- **Flight Engineer Rev A1:** remove the 6V servo BEC; tilt servos run on the 5V rail
  (~21 kg·cm capacity vs ~16 kg·cm tilt load requirement)

Per-item status changes often and is not tracked here — read the current state directly from
each board's own `.md` (`avionics/kicad/Commo/Commo.md`, `avionics/kicad/XO/XO.md`,
`avionics/kicad/FlightEngineer/FlightEngineer.md`) and `TODO.md` §1.2b before starting work.

### Phase 11 (Medium Priority — Cruise and RCS)

- **Rear EDF (55 mm 6S):** fuselage-mounted, horizontal-thrust-only propulsion to extend
  endurance and enable sustained forward flight. Motor and intake design are deferred and duct
  geometry is speculative — do not treat either as settled. It feeds 4 RCS thrusters tapping
  ~15% of mass flow; the remainder exits the canonical nozzle as forward thrust. Carving the aft
  EDF intake scoop into the middle-section inner neck is deferred to Phase 11 or later.
- **RCS thrusters (4×):** low-authority pitch/yaw attitude control on bleed air from the rear
  EDF — reduces nacelle servo load, extends battery life in hover, improves stability. Plumbing
  concept only; sizing is blocked pending rear-EDF motor selection and thrust-curve validation.
- **Build phasing:** Phase 11 requires Phases 5–10 complete, and covers rear fuselage EDF bay
  fabrication and intake duct carving, RCS plumbing and thruster integration, flight-control
  firmware for multi-axis thrust vectoring, and revised T/W and hover performance calculations.

### Phase 12+ (Lower Priority — Extended Capabilities)

Under consideration, not yet scoped: advanced autonomous maneuvers (carrier landing simulation,
formation flight), a modular extended-payload bay for different sensors or tools, ultra-light
solar power augmentation for extended endurance, and swarm coordination (multi-UAV formation
control and task distribution).

## How to Use This Folder

**`deferred/DEFERRED_ITEM_TEMPLATE.md`** holds the required field template for every deferred
item (title/revision, status, scope, technical approach, dependencies, blockers, estimated
effort, integration date, owner) plus the step-by-step "For Contributors" and "For Planners"
procedures and the routine for adding new deferred work. Follow it whenever you open, advance,
or promote an item in this folder.

## Design Decisions Leading to Deferral

Some deferred items document **design decisions evaluated but not selected** for the current baseline:

- **Landing gear alternatives (Rev R1–R4):** Parametric V-braces, forked-CF-PETG arms (rejected in favor of wire-brace design per Rev R5 landing gear analysis)
- **Fuselage intake approaches for rear EDF:** Rearward-facing scoop vs. side-mounted duct vs. belly-mounted intake

These documents support traceability: if future work requires revisiting a design choice, the full evaluation is available in this folder.

## Work Tracking

Items in this folder are tracked in `TODO.md` with cross-references:

- `TODO.md §1.2b` — Planned PCB revisions (Commo R1, XO R1, Flight Engineer A1)
- `TODO.md §1.3` — Phase 11 system integration (rear EDF, RCS)
- `TODO.md §2.x` — Phase 12+ capability planning

## Legal and Licensing Notes

All deferred work is covered under the same dual license as active work — CERN-OHL-W 2.0 for
hardware/CAD (e.g. `deferred/aft-edf/` SCAD/STL), CC BY-SA 4.0 for docs/code — see
`deferred/LICENSE` and `docs/attribution_and_licensing.md`. Deferred designs may be:

- **Shared publicly** on version control
- **Used by others** for their own UAV projects
- **Cited with attribution** to Steve Griffing and this project
