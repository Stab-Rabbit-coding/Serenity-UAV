# Specification Document Template and Approval Workflow

Governing file: `current-specification/AGENTS.md` — this document holds the document structure,
approval workflow, and traceability requirements that `current-specification/AGENTS.md` points
to. For project-wide standards see the root `AGENTS.md`.

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

## Specification Approval Workflow

Before publishing a revised specification:

1. Ensure all cited standards are verified in `REFERENCES.md`
2. Verify that all cited components and measurements are correct
3. Update all cross-references to other specifications
4. If this is a new revision letter:
    - Archive the previous revision to `archives/`
    - Update `ARCHIVE_INDEX.md`
    - Update `PROJECT_INDEX.md`
    - Ensure all active component documentation points to the new revision

## Version Control Best Practices

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
Requirement ID → applicable standard(s) → implementation artifact(s) → test case(s).

This allows auditors and reviewers to quickly verify that every requirement has a design and
test basis.

## Standards Citations in Specifications

When citing a standard requirement:

- **Format:** Use the REF-ID and section number: `[REF-FAA-001 §48.205]`
- **Verification:** Every citation must be verifiable by looking it up in `REFERENCES.md`
- **Context:** Explain why that requirement applies to this design

**Example:**

> "Per [REF-FAA-001 §48.205], the aircraft shall be marked with the registration number on the
> fuselage, applied so that the letters are 3/8 in (9.5 mm) tall minimum. This 24 in (609 mm)
> aircraft will use 0.5 in (12.7 mm) characters printed on a removable decal mounted on the
> starboard vertical stabilizer."
