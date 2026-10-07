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

### Planned board revisions

Planned changes to avionics boards are owned by those boards, not by this folder. Per-item scope,
status, and history are descriptive and live in each board's own `.md`
(`avionics/kicad/<board>/<board>.md`), in `avionics/WBS.md`, and in `avionics/rev-s1/WBS.md`.
Read them before starting work; do not restate them here.

### Phase 11 (Medium Priority — Cruise and RCS)

- **Rear EDF:** fuselage-mounted, horizontal-thrust-only propulsion for endurance and sustained
  forward flight. Motor, intake, and duct geometry are deferred and shall not be treated as
  settled. It feeds the RCS thrusters from a bleed-air tap; the remainder exits the fixed
  canonical nozzle as forward thrust. Carving the aft EDF intake scoop into the middle-section
  inner neck is deferred to Phase 11 or later. Every figure for the EDF, its ESC, and the bleed
  split shall come from a manufacturer datasheet or a user-verified measurement; the current
  working values are in `deferred/aft-edf/README.md`.
- **RCS thrusters:** low-authority pitch/yaw attitude control on bleed air from the rear EDF.
  Sizing is blocked pending rear-EDF motor selection and thrust-curve validation.
- **Build phasing:** Phase 11 requires Phases 5–10 complete. It covers rear fuselage EDF bay
  fabrication and intake duct carving, RCS plumbing and thruster integration, flight-control
  firmware for multi-axis thrust vectoring, and revised hover performance calculations. Results
  are recorded in the descriptive documents, not here.

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

- **Landing gear alternatives:** the rejected variants and the reasons are in
  `docs/LANDING_GEAR_ANALYSIS.md`.
- **Fuselage intake approaches for rear EDF:** record any evaluation of alternatives under
  `deferred/aft-edf/`; none is written yet.

These documents support traceability: if future work requires revisiting a design choice, the full evaluation is available in this folder.

## Work Tracking

Items in this folder are tracked in `TODO.md` with cross-references:

- `deferred/WBS.md` §Phase11 — Phase 11 system integration (rear EDF, RCS)
- `deferred/WBS.md` §Phase12 — range-extender battery module
- `avionics/WBS.md` and `avionics/rev-s1/WBS.md` — planned board revisions

## Legal and Licensing Notes

All deferred work is covered under the same dual license as active work — CERN-OHL-W 2.0 for
hardware/CAD (e.g. `deferred/aft-edf/` SCAD/STL), CC BY-SA 4.0 for docs/code — see
`deferred/LICENSE` and `docs/attribution_and_licensing.md`. Deferred designs may be:

- **Shared publicly** on version control
- **Used by others** for their own UAV projects
- **Cited with attribution** to Steve Griffing and this project
