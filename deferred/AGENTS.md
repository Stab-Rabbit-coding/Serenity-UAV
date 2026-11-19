# Deferred Work — Agent Instructions

Adds deferred-work rules to root `AGENTS.md`, which wins wherever it speaks. Scope: work
intentionally deferred beyond the current build baseline, planned upgrades, and designs
evaluated but not selected.

## Status

- **Not deferred:** the tail EDF, its speed controller, and the RCS are part of the first build
  (Phase 5, flight-critical in hover; root `AGENTS.md` §1). The old "Phase 11 — Aft EDF" records
  in this folder are pre-shift history until TEDF-01 rewrites them — **do not apply them** as
  requirements. There is no longer a rear-EDF phase.
- **Phase 11** is the cargo-bay range-extender battery module, promoted into the active build on
  2026-10-26 (still titled "Phase 12" in `deferred/WBS.md` §Phase12 until PHASE-RENUMBER lands).
  The tail EDF and RCS open steps moved to build Phases 5 and 9 on 2026-11-17.
- **Phase 12+** items are speculative and unscoped.
- Phase descriptions, status, and work items: `deferred/README.md` and `deferred/WBS.md`. The
  phase table is owned by `graphical-build-guide/AGENTS.md` "Phases".
- Planned avionics board revisions are owned by each board's `.md`, `avionics/WBS.md`, and
  `avionics/rev-s1/WBS.md`, not by this folder.

## Using This Folder

- `deferred/DEFERRED_ITEM_TEMPLATE.md` holds the required fields and the procedures for
  opening, advancing, or promoting a deferred item. Follow it.
- When an item becomes active, move it into the owning phase's documentation and build guide,
  and record the move in `deferred/WBS.md`.
- Record each design evaluated but not selected, with its reasons, so it is not proposed again
  (e.g., landing-gear alternatives in `docs/LANDING_GEAR_ANALYSIS.md`; tail-EDF intake
  alternatives under `deferred/aft-edf/`).
- Record open work in `deferred/WBS.md` (root §10 federation).

Licensing follows root `AGENTS.md` §3 (`deferred/LICENSE`).
