# Graphical Build Guide — Agent Instructions

Adds build-guide rules to root `AGENTS.md`, which wins wherever it speaks. Scope: illustrated
build guides, assembly sequences, fabrication checklists, and troubleshooting, organized by
build phase. Each phase adds capability while keeping earlier phases testable.

## Phases

This table is the one home for the phase plan.

| Phase | What's built | Goal | Status |
| --- | --- | --- | --- |
| **1–4** | Fuselage, landing gear, wing attachment | Physical airframe | Archived/prototype |
| **5–10** | Avionics stacks, nacelles, battery, power distribution, tail EDF + speed controller + RCS | Full VTOL hover | **Current** |
| **11** | Cargo-bay range-extender battery module | Endurance | Deferred |
| **12+** | Autonomous mission system and other speculative items | — | Unscoped |

- The tail EDF and RCS are flight-critical in hover, so a nacelle-only first hover is not the
  plan (`airframe/fuselage-mid/WBS.md` §1.1.1.4.0; TEDF-16 brings their installation into
  Phase 5).
- Measured performance figures (mass, thrust-to-weight) do not belong in any AGENTS.md; read
  them in `current-specification/auw_ledger.json`, `airframe/README.md`, and
  `current-specification/README.md`.
- Each phase guide shall state the as-built capability it verifies, with measured values taken
  from those documents.

## Guide Structure

`graphical-build-guide/BUILD_GUIDE_TEMPLATE.md` is the authoritative template for every phase
guide: introduction fields, the step format, material lists, the fabrication-standards block,
verification checklists, tests, troubleshooting, sign-off, and the illustration and graphics
guidelines. Follow it.

## Work Tracking

When creating or updating a phase guide:

1. Test the procedure yourself or with a technical reviewer; no untested instructions.
2. Include every necessary figure and dimension.
3. Cite standards (e.g., fastener grades) by REF-ID from `REFERENCES.md`.
4. Link deferred work to its `deferred/WBS.md` item.
5. Archive superseded guides under `archives/`; record open work in
   `graphical-build-guide/WBS.md` (root §10 federation).
