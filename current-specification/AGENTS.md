# Current Specification — Agent Instructions

> *See the root `AGENTS.md` for project-wide policies. This file provides specific guidance for active design specifications and version control.*

## Scope

This folder contains the active (in-progress) design specifications and requirements documents for the current revision of Serenity-UAV. These files define the current design baseline and are subject to change as the design evolves.

**Important:** This folder is for **active, current work**. Completed specifications are archived in the `archives/` folder and referenced in `ARCHIVE_INDEX.md`.

## Revision Policy

All specifications follow the Serenity-UAV revision numbering scheme (root `AGENTS.md` §8):

- A **revision with a letter** (e.g., Rev R, Rev N, Rev L) is a **comprehensive design
  checkpoint**. All components referenced as of a revision letter have current specifications,
  have been integrated and tested together, are ready for fabrication or continued development,
  and have all documentation updated to match the hardware baseline. All components are
  referenced as of the latest revision, even if nothing changed for that component since an
  earlier revision.
- **Modifications after a revision** are numbered sequentially — Rev N1, Rev N2, Rev N3 — each
  an incremental change to specific components while the overall revision baseline holds. The
  numbers reset with each new letter revision. Example: Rev N (baseline, released) → Rev N1
  (first modification) → Rev N2 (second modification; N1 components carry forward) → Rev O (new
  comprehensive revision, all active components carry forward, numbering resets).

## Specification Document Structure and Workflow

**`current-specification/SPEC_TEMPLATE.md`** is the authoritative template: header fields
(title, revision, status, change summary), the eight numbered sections every specification
carries, the "Changes from Rev [X]" change-tracking block, the pre-publication approval
workflow, version-control practice, the traceability-matrix requirement, and the standards
citation format with a worked `[REF-FAA-001 §48.205]` example. Follow it whenever you author or
revise a specification in this folder.

## Active Specification Maintenance

**Update specifications in this folder when:**

- A new revision is being prepared (all changes integrated)
- A design change requires coordination across multiple systems
- A specification needs clarification or correction
- A new analysis or test result changes the baseline

**Do NOT use this folder for:**

- Drafting new ideas or experimental designs (use a separate draft folder)
- Tracking day-to-day modifications to individual components (use subdirectory AGENTS.md files and git history)

## Known Deferred Items

This folder may include a `DEFERRED_ITEMS.md` document listing:

- **Phase 11+:** Rear EDF + RCS (deferred), aft intake scoop carving (deferred)
- **Planned revisions:** Commo Rev R1, XO Rev R1, Flight Engineer Rev A1 (planned but not yet implemented)
- **Known limitations:** Open issues that do not block the current baseline

Deferred items should reference `TODO.md` for the specific work items.

---

For project-wide standards, see the root `AGENTS.md`.
