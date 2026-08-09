# Deferred Work — Agent Instructions

> *See the root `AGENTS.md` for project-wide policies. This file provides specific guidance for deferred (Phase 11+) design work, planned upgrades, and items awaiting future implementation.*

## Scope

This folder contains design specifications, analysis, and artifacts for work that is **intentionally deferred** beyond the current build phase (Phases 5–10). These items are planned but not part of the active build baseline.

Deferred work is organized by:

- **Planned upgrades to current components** (Commo Rev R1, XO Rev R1, Flight Engineer Rev A1)
- **Future system additions** (Phase 11: rear EDF + RCS, aft intake scoop geometry)
- **Analysis of alternative designs** evaluated but not selected for current baseline
- **Long-term enhancements** (Phase 12+: advanced autonomy, extended payload, etc.)

## Status Categories

### Planned (High Priority — Next Release)

**Planned for the next major revision (Rev R1 detailed changes, target integration date: Phase 6–7):**

- **Commo Rev R1:** Add LoRa, replace JST GH 6P with P1+P2 socket rails
- **XO Rev R1:** Remove LoRa (migrated to Commo), add P1+P2 passthrough rails matching Commo pinout on River and Simon stacks
- **Flight Engineer Rev A1:** Remove 6V servo BEC; tilt servos to run on 5V rail (~21 kg·cm capacity vs ~16 kg·cm tilt load requirement)

Per-item status changes often and is not tracked here — read the current state directly from
each board's own `.md` (`avionics/kicad/Commo/Commo.md`, `avionics/kicad/XO/XO.md`,
`avionics/kicad/FlightEngineer/FlightEngineer.md`) and `TODO.md` §1.2b before starting work.

### Phase 11 (Medium Priority — Cruise and RCS)

- **Rear EDF (55 mm 6S):** Fuselage-mounted, horizontal-thrust-only propulsion
    - Purpose: Extend endurance, enable sustained forward flight (cruise phase)
    - Status: Motor and intake design deferred; duct geometry speculative
    - Technical note: The 55 mm EDF feeds 4 RCS (reaction-control) thrusters tapping ~15% of mass flow; remainder exits the canonical nozzle as forward thrust
    - Deferred: Aft EDF intake scoop carving into the middle-section inner neck (Phase 11 or later)

- **RCS Thrusters (4×):** Low-authority pitch/yaw attitude control via bleed air from rear EDF
    - Purpose: Reduce nacelle servo load, extend battery life in hover, improve stability
    - Status: Plumbing concept only; sizing pending EDF performance data
    - Deferred pending: Rear EDF motor selection and thrust-curve validation

- **Build phasing:** Phase 11 work requires completion of Phases 5–10 and includes:
    - Rear fuselage EDF bay fabrication and intake duct carving
    - RCS plumbing and thruster integration
    - Flight control firmware update for multi-axis thrust vectoring
    - Revised T/W and hover performance calculations

### Phase 12+ (Lower Priority — Extended Capabilities)

**Future enhancements under consideration (not yet scoped):**

- **Advanced autonomous maneuvers:** Carrier landing simulation, formation flight
- **Extended payload:** Modular payload bay for different sensors or tools
- **Solar power augmentation:** Ultra-light solar cell integration for extended endurance
- **Swarm coordination:** Multi-UAV formation control and task distribution

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

## Phase Numbering Convention

- **Phases 1–4:** Prototype airframe (archived)
- **Phases 5–10:** Current baseline (active, in production)
- **Phase 11:** Rear EDF + RCS (deferred)
- **Phase 12+:** Advanced autonomy, extended payload, etc. (deferred, not yet scoped)

When deferred work becomes active, it will be incorporated into the relevant phase's documentation and build guide.

## Work Tracking

Items in this folder are tracked in `TODO.md` with cross-references:

- `TODO.md §1.2b` — Planned PCB revisions (Commo R1, XO R1, Flight Engineer A1)
- `TODO.md §1.3` — Phase 11 system integration (rear EDF, RCS)
- `TODO.md §2.x` — Phase 12+ capability planning

## Legal and Licensing Notes

All deferred work is covered under the same dual license as active work — CERN-OHL-W 2.0 for
hardware/CAD (e.g. `deferred/aft-edf/` SCAD/STL), CC BY-SA 4.0 for docs/code — see
`deferred/LICENSE` and `docs/attribution_and_licencing.md`. Deferred designs may be:

- **Shared publicly** on version control
- **Used by others** for their own UAV projects
- **Cited with attribution** to Steve Griffing and this project

---

For project-wide standards, see the root `AGENTS.md`.
