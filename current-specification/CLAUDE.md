# Current Specification — Claude Code Project Instructions

> *See the root `CLAUDE.md` for project-wide policies. This file provides specific guidance for active design specifications and version control.*

## Scope

This folder contains the active (in-progress) design specifications and requirements documents for the current revision of Serenity-UAV. These files define the current design baseline and are subject to change as the design evolves.

**Important:** This folder is for **active, current work**. Completed specifications are archived in the `archives/` folder and referenced in `ARCHIVE_INDEX.md`.

## Revision Policy

All specifications follow the Serenity-UAV revision numbering scheme:

### Revision Letters (Comprehensive Baselines)

A **revision with a letter** (e.g., Rev R, Rev N, Rev L) is a **comprehensive design checkpoint**. All components referenced as of a revision letter are understood to:
- Have current specifications
- Have been integrated and tested together
- Be ready for fabrication or continued development
- Have all documentation updated to match the hardware baseline

All components are referenced as of the latest revision, even if there was no change to that component's specifications since an earlier revision.

### Revision Numbers (Incremental Modifications)

**Modifications after a revision** are numbered sequentially: Rev N1, Rev N2, Rev N3, etc.

These represent incremental changes to specific components while maintaining the overall revision baseline. The numbers reset with each new letter revision.

**Example:**
- Rev N — baseline, released
- Rev N1 — first modification after Rev N
- Rev N2 — second modification (both components from N1 carry forward)
- Rev O — new comprehensive revision (all active components carry forward; numbering resets)

## Specification Document Structure

Each specification document shall include:

### Header Information
- **Title:** e.g., "Serenity-UAV Rev R Specifications"
- **Revision:** Letter and date (e.g., "Rev R — 2026-06-11")
- **Status:** Draft / Release Candidate / Released / Superseded
- **Change summary:** What changed from the previous revision

### Sections

1. **Overview:** Purpose, mission profile, design constraints
2. **Requirements:** Functional, performance, safety, regulatory
3. **System architecture:** High-level blocks and interfaces
4. **Component specifications:** Detailed specs for each major assembly
5. **Interface specifications:** Electrical, mechanical, software contracts between systems
6. **Test and verification plan:** How requirements will be verified
7. **Known limitations:** Deferred work, open issues, Phase 11+ items
8. **Standards and references:** All applicable standards cited with REF-IDs

### Change Tracking

Include a "Changes from Rev [X]" section that lists:
- New components or requirements
- Modified specifications (with old and new values)
- Removed components or features
- Known issues or deferred items

## Active Specification Maintenance

### When to Update This Folder

**Update specifications in this folder when:**
- A new revision is being prepared (all changes integrated)
- A design change requires coordination across multiple systems
- A specification needs clarification or correction
- A new analysis or test result changes the baseline

**Do NOT use this folder for:**
- Drafting new ideas or experimental designs (use a separate draft folder)
- Tracking day-to-day modifications to individual components (use subdirectory CLAUDE.md files and git history)

### Specification Approval Workflow

Before publishing a revised specification:

1. Ensure all cited standards are verified in `REFERENCES.md`
2. Verify that all cited components and measurements are correct
3. Update all cross-references to other specifications
4. If this is a new revision letter:
   - Archive the previous revision to `archives/`
   - Update `ARCHIVE_INDEX.md`
   - Update `PROJECT_INDEX.md`
   - Ensure all active component documentation points to the new revision

### Version Control Best Practices

- Commit specification changes with detailed messages explaining the rationale
- Reference applicable TODO.md items or GitHub issues
- If a specification change requires updates to code, PCBs, or CAD, commit those updates in the same PR
- Tag revision releases in git: `git tag -a "v-Rev-R" -m "Serenity-UAV Rev R release"`

## Traceability and Audit

Every specification requirement shall be traceable to:
- **One or more standards** (cited by REF-ID in REFERENCES.md)
- **One or more design artifacts** (code, PCB, CAD model, test result) that implement it
- **One or more test cases or verification steps** that confirm compliance

Maintain a **traceability matrix** (in a separate document or spreadsheet) that maps:
- Requirement ID → applicable standard(s) → implementation artifact(s) → test case(s)

This allows auditors and reviewers to quickly verify that every requirement has a design and test basis.

## Standards Citations in Specifications

When citing a standard requirement:
- **Format:** Use the REF-ID and section number: `[REF-FAA-001 §48.205]`
- **Verification:** Every citation must be verifiable by looking it up in `REFERENCES.md`
- **Context:** Explain why that requirement applies to this design

**Example:**
> "Per [REF-FAA-001 §48.205], the aircraft shall be marked with the registration number on the fuselage, applied so that the letters are 3/8 in (9.5 mm) tall minimum. This 24 in (609 mm) aircraft will use 0.5 in (12.7 mm) characters printed on a removable decal mounted on the starboard vertical stabilizer."

## Known Deferred Items

This folder may include a `DEFERRED_ITEMS.md` document listing:
- **Phase 11+:** Rear EDF + RCS (deferred), aft intake scoop carving (deferred)
- **Planned revisions:** Emma Rev R1, Zoë Rev R1, Kaylee Rev A1 (planned but not yet implemented)
- **Known limitations:** Open issues that do not block the current baseline

Deferred items should reference `TODO.md` for the specific work items.

---

For project-wide standards, see the root `CLAUDE.md`.
