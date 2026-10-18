# Deferred Item Template and Handling Procedures

Governing file: `deferred/AGENTS.md` — this document holds the per-item field template and the
contributor/planner procedures that `deferred/AGENTS.md` points to. For project-wide standards
see the root `AGENTS.md`.

## Deferred Item Field Template

Each deferred item in this folder shall include:

- **Title and revision:** e.g., "Rev R1 — Commo PCB Redesign"
- **Status:** Planned / In Analysis / Waiting (for dependency) / Phase 11 / Phase 12+
- **Scope:** What problem does it solve? What capability does it add?
- **Technical approach:** Proposed solution or design
- **Dependencies:** What must be complete first?
- **Blockers:** Open questions or risks
- **Estimated effort:** Design, prototyping, integration, testing
- **Integration date:** Target revision or phase
- **Owner or next reviewer:** Who should drive this when it becomes active

## For Contributors

If you are asked to work on a deferred item:

1. **Check the status:** Is it "Planned" or "Phase 11+" or "Phase 12+"?
2. **Understand the scope:** Read the item description and design notes
3. **Identify dependencies:** What must be complete before this work can start?
4. **Check for blockers:** Are there open design questions (marked in TODO.md)?
5. **Create a task in TODO.md:** Link to the relevant deferred document
6. **Keep this folder updated:** As you progress, update the status and document blockers

## For Planners

To integrate deferred work into the next phase:

1. Review items in the "Planned" category
2. Validate that dependencies are met (earlier phases complete)
3. Move the item to active specification folder once integration planning begins
4. Create phase-specific build guide steps
5. Archive design notes to `archives/` once work is complete and released

## Adding New Deferred Work

1. Create a Markdown document with the item details (fields above)
2. Add a tracking item to `TODO.md` with a cross-reference
3. Link from `deferred/AGENTS.md` or this folder's index
