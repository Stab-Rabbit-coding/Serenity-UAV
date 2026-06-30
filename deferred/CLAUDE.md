# Deferred Work — Claude Code Project Instructions

> *See the root `CLAUDE.md` for project-wide policies. This file provides specific guidance for deferred (Phase 11+) design work, planned upgrades, and items awaiting future implementation.*

## Scope

This folder contains design specifications, analysis, and artifacts for work that is **intentionally deferred** beyond the current build phase (Phases 5–10). These items are planned but not part of the active build baseline.

Deferred work is organized by:
- **Planned upgrades to current components** (Emma Rev R1, Zoë Rev R1, Kaylee Rev A1)
- **Future system additions** (Phase 11: rear EDF + RCS, aft intake scoop geometry)
- **Analysis of alternative designs** evaluated but not selected for current baseline
- **Long-term enhancements** (Phase 12+: advanced autonomy, extended payload, etc.)

## Status Categories

### Planned (High Priority — Next Release)

**Planned for the next major revision (Rev R1 detailed changes, target integration date: Phase 6–7):**

- **Emma Rev R1:** Add LoRa, replace JST GH 6P with P1+P2 socket rails
  - Status: Schematic/PCB design in progress
  - Dependencies: None (Emma is optional, not critical path)
  - Effort: 1–2 weeks design + prototyping

- **Zoë Rev R1:** Remove LoRa (migrated to Emma), add P1+P2 passthrough rails matching Emma pinout on River and Simon stacks
  - Status: Schematic/PCB design in progress
  - Dependencies: Emma Rev R1 completion (for pinout validation)
  - Effort: 1–2 weeks design

- **Kaylee Rev A1:** Remove 6V servo BEC; tilt servos to run on 5V rail (~21 kg·cm capacity vs ~16 kg·cm tilt load requirement)
  - Status: Power budget analysis complete, schematic redesign pending
  - Dependencies: Tilt servo load testing (completed)
  - Effort: 1–2 weeks design + validation

### Phase 11 (Medium Priority — Cruise and RCS)

**Phase 11 work scope:**

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

### For Contributors

If you are asked to work on a deferred item:

1. **Check the status:** Is it "Planned" or "Phase 11+" or "Phase 12+"?
2. **Understand the scope:** Read the item description and design notes
3. **Identify dependencies:** What must be complete before this work can start?
4. **Check for blockers:** Are there open design questions (marked in TODO.md)?
5. **Create a task in TODO.md:** Link to the relevant deferred document
6. **Keep this folder updated:** As you progress, update the status and document blockers

### For Planners

To integrate deferred work into the next phase:

1. Review items in the "Planned" category
2. Validate that dependencies are met (earlier phases complete)
3. Move the item to active specification folder once integration planning begins
4. Create phase-specific build guide steps
5. Archive design notes to `archives/` once work is complete and released

## Deferred Items Tracking

Each deferred item in this folder shall include:

- **Title and revision:** e.g., "Rev R1 — Emma PCB Redesign"
- **Status:** Planned / In Analysis / Waiting (for dependency) / Phase 11 / Phase 12+
- **Scope:** What problem does it solve? What capability does it add?
- **Technical approach:** Proposed solution or design
- **Dependencies:** What must be complete first?
- **Blockers:** Open questions or risks
- **Estimated effort:** Design, prototyping, integration, testing
- **Integration date:** Target revision or phase
- **Owner or next reviewer:** Who should drive this when it becomes active

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

- `TODO.md §1.2b` — Planned PCB revisions (Emma R1, Zoë R1, Kaylee A1)
- `TODO.md §1.3` — Phase 11 system integration (rear EDF, RCS)
- `TODO.md §2.x` — Phase 12+ capability planning

When adding new deferred work to this folder:
1. Create a markdown document with the item details
2. Add a tracking item to `TODO.md` with a cross-reference
3. Link from this document's index

## Legal and Licensing Notes

All deferred work is covered under the same CC BY 4.0 license as active work. Deferred designs may be:
- **Shared publicly** on version control
- **Used by others** for their own UAV projects
- **Cited with attribution** to Steve Griffing and this project

---

For project-wide standards, see the root `CLAUDE.md`.
