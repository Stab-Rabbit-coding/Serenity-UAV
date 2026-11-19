# Current Specification — Agent Instructions

Adds specification rules to root `AGENTS.md`, which wins wherever it speaks. Scope: the active
design specifications and requirements for the current revision. Completed specifications are
archived under `archives/` (listed in `ARCHIVE_INDEX.md`).

## Rules

- Revision labels follow root `AGENTS.md` §8 (one project-wide letter; currently Rev U). Every
  specification here carries its revision label in its header.
- **`current-specification/SPEC_TEMPLATE.md`** is the authoritative template: header fields,
  the numbered sections, the "Changes from Rev [X]" block, approval workflow, traceability
  matrix, and citation format. Follow it.
- Update a specification here when a revision is being prepared, a design change needs
  coordination across systems, a specification needs correction, or a new analysis or test
  result changes the baseline.
- Do not use this folder for drafts or experimental designs, or for day-to-day component
  changes (those live in the owning subsystem's records and git history).
- Deferred work is described in `deferred/`; a `DEFERRED_ITEMS.md` here, if present, only
  points there.
- Record open work in the owning subsystem's `WBS.md` (this folder owns no WBS branch;
  `docs/WBS_FEDERATION.md`).
