# Documentation — Agent Instructions

> *See the root `AGENTS.md` for project-wide policies. This file provides specific guidance for documentation standards, references vetting, and compliance tracking.*

## Scope

This folder contains all project documentation: design specifications, analysis reports, standards references, build guides, and compliance records. Documentation is a **design artifact** — every specification and analysis must be traceable to authoritative sources and vetted against applicable standards.

## Standards Vetting Policy

**Every design specification with any effect beyond cosmetic appearance must be vetted against applicable industry standards and/or regulations before implementation.**

### Reference Management

All standards citations are cataloged in `REFERENCES.md`, which must contain:

- Standard designation and full title
- Validated URL for official access (verified against the issuing body)
- Specific chapter, section, and paragraph applied
- Every repository location where the standard is cited (in code comments, docs, schematics, build guides, etc.)

### Citation Format

All citations throughout the codebase — in code comments, documentation, schematics, and build guides — shall reference the `REFERENCES.md` REF-ID and include chapter, section, and paragraph to enable auditing:

**Format:** `[REF-ID §section.subsection.paragraph]`

**Examples:**

- `[REF-FCC-001 §15.247(b)(3)(ii)]` — FCC Part 15 compliance for 915 MHz operation
- `[REF-FAA-001 §48.205]` — FAA markings requirements
- `[REF-NIST-001 §2.1, §2.2, §3.3]` — NIST Zero Trust Architecture sections

### Citation Auditing

**No fabricated, unverifiable, or incorrectly attributed references are permitted.**

When auditing a citation:

1. Look up the REF-ID in `REFERENCES.md`
2. Verify the URL is valid and points to the official document
3. Check that the section/paragraph cited actually exists in the referenced document
4. If the section cannot be verified, mark it as "requires verification" in `REFERENCES.md` and add a TODO §0.x item
5. If a citation is found to be incorrect, remove it and correct the reference, then document the removal in the "Removed / Superseded Citations" section of `REFERENCES.md`

### Reference Lifecycle

**When adding a new standards citation:**

1. Look up the standard in `REFERENCES.md` by REF-ID
2. If not yet in the catalog, add it with:
    - Full title and issuing body
    - Validated URL (tested against official issuing body)
    - Date accessed and verification date
    - Specific section cited
3. Use the REF-ID in the code or doc
4. Add the code/doc location to the REF-ID's citation index in `REFERENCES.md`

**When removing or superseding a citation:**

1. Update all references in the codebase to point to the correct standard (or remove the reference)
2. Document the removal in the "Removed / Superseded Citations" section of `REFERENCES.md`
3. Explain why it was removed or superseded (e.g., "Superseded by REF-FCC-002 Rev 2020", "Misattributed — the rule was from Part 97, not Part 95")

### Canonical / Reference Ground-Truth Sources

Beyond standards, `docs/references/` holds the project's **canonical-accuracy** reference library
for the ship's shape and proportion, cataloged in `REFERENCES.md` Part XIV (REF-CAD-002/003/004).
Use these as ground truth in this authority order (highest first):

1. **QMx *Official Serenity Blueprints Reference Pack* (2007)** — REF-CAD-003. Most authoritative;
   officially licensed canon. Where it disagrees with any other reference, it wins. A **copyrighted
   commercial product retained for internal reference only — NOT relicensed under CC BY.**
2. **Nick Henning render collection** — REF-CAD-002. Derived from show/QMx canon; more mechanical
   detail than the blueprints; used by email permission (2026-07-06).
3. **misubisu Thingiverse model, Thing 7330462** — REF-CAD-004 (CC BY-SA 4.0, Available Component
   under CERN-OHL-W 2.0 — see `docs/attribution_and_licencing.md` §3). The `s_*.stl` origin;
   still usable but **verify against the two above** before treating any detail as canonical.

The creative-universe attribution and fan-engineering terms (Joss Whedon, cast/crew, Universal /
Fox-Disney, QMx) are summarized in `REFERENCES.md` ("Creative-Universe Attribution and
Fan-Engineering Terms") and given in full in
`current-specification/LICENSE_AND_ATTRIBUTION.md`. Geometry-usage detail lives in
`airframe/HULL_FRAME_REFERENCE.md` "Canonical Accuracy References."

## Applicable Standards Bodies

Design specifications in Serenity-UAV shall be vetted against standards from these bodies:

| Body | Focus Areas |
| --- | --- |
| **FAA** | Airworthiness, registration, flight operations |
| **FCC** | Radio frequency emissions, interference, unlicensed band use |
| **NIST** | Cybersecurity, information security, zero-trust architecture |
| **DoD/DLA** | MIL-STD bus protocols, MIL-STD 1553, encrypted communications |
| **ISO** | Data bus protocols, safety standards |
| **IEC** | Component safety, isolator certification |
| **VDE** | High-voltage isolator certification |
| **IEEE** | Networking standards, communication protocols |
| **ISA / IEC 62443** | Operational technology (OT) and industrial control system (ICS) cybersecurity |
| **AUVSI / ASTM F38** | UAS design guidelines, flight operations |
| **ICAO** | International aviation rules and standards |

## Documentation Structure

**`docs/DOC_TEMPLATES.md`** is the authoritative content template set: the required fields for
design specifications, analysis/calculation documents (e.g. `LANDING_GEAR_ANALYSIS.md`), and
compliance records; the build-guide/fabrication-instruction content requirements including the
*WARNING* (hazard to personnel) / *CAUTION* (hazard to equipment) marking rule; plus the
documentation-quality, code-comment, and revision/changelog conventions. Follow it when
authoring or revising any document in this folder.

## Measurements and Units

Every measurement in this folder follows the units convention in root `AGENTS.md` §5
"Engineering Requirements" — read it there; the convention is not restated in this file.

## Work Tracking and Documentation

When creating or updating documentation:

1. Explain the change in the commit message
2. When adding or modifying a standards citation, verify the reference and update
   `REFERENCES.md` with the validation details
3. Archive superseded documents in `archives/`; index and archive upkeep (`PROJECT_INDEX.md`,
   `ARCHIVE_INDEX.md`) follows root `AGENTS.md` §10
4. If the documentation work is complex or spans multiple documents, track subtasks in `TODO.md`
