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

### Design Specifications

Design specifications shall include:
- **Objective:** What capability is being specified
- **Standards basis:** Which regulation(s) or industry standard(s) the spec is drawn from
- **Functional requirements:** What the system must do
- **Performance requirements:** Quantified performance (thrust, power, mass, etc.)
- **Safety requirements:** Failure modes and mitigation
- **Testing/verification:** How compliance will be verified

### Analysis and Calculation Documents

Detailed analysis documents (e.g., `LANDING_GEAR_ANALYSIS.md`) shall include:
- **Title and revision:** e.g., "Rev R5 — Landing Gear Structural Analysis"
- **Problem statement:** What is being analyzed and why
- **Assumptions:** All simplifications and constraints
- **Calculations:** Detailed steps with units
- **Results:** Clear summary of findings and safety margins
- **Standards citations:** Which regulations/standards informed the analysis
- **References:** Sources for material properties, formulas, etc.

### Compliance Records

When implementing a standards requirement:
1. Document where the requirement is enforced (code file, PCB, structural detail, etc.)
2. Add a note with the REF-ID and section number
3. If testing is required, record the test result or link to the test report

### Build Guides and Fabrication Instructions

Build documentation shall include:
- **Step numbers** with clear, sequential instructions
- **Component lists** with part numbers, quantities, and sources
- **Material specifications** (filament type, print settings, fastener grade)
- **Safety hazard markings** for hazardous operations will in 
    - A *WARNING* signifies a hazard to personnel
    - A *CAUTION* signifies a hazard to equipment
    - All instructions that pose hazards to personnel and or equipment if not done correctly shall have a caution and or warning note specifying the nature of the hazard.

- **Tool requirements** (specialized fixtures, soldering iron settings, etc.)
- **Verification steps** to confirm correct assembly
- **Troubleshooting** for common issues

## Measurements and Units

### Imperial-Primary Convention

All measurements shall be expressed **imperial-primary with metric in parentheses**:

**Examples:**
- Length: `10 in (254 mm)`
- Mass: `2.5 lbm (1.13 kg)` — always use **lbm** for pounds-mass
- Force: `4.8 lbf (21.4 N)` — always use **lbf** for pounds-force
- Airspeed: `25 kt (12.8 m/s)` — use **kt** for knots

**Key distinctions:**
- **lbm** = pounds-mass (component weight, payload capacity)
- **lbf** = pounds-force (thrust, lift, loads)
- **kg** = kilogram (metric mass)
- **N** = newton (metric force)
- **kt** = knots (airspeed, wind speed) — never mph or km/h for aviation

## Documentation Quality Standards

### Clarity and Completeness

- Every document should be understandable to someone with domain knowledge but no prior context
- Define acronyms on first use: "Thrust-to-weight ratio (T/W)"
- Use section headers and subsections for readability
- Include tables and figures where appropriate
- Cross-reference related documents

### Code Comments vs. Documentation

**Comments in code:**
- Should explain the *why*, not the *what* (code already shows what it does)
- For KiCad files: use Markdown companion files (comments in KiCad files using `;` or `#` are **prohibited**). Use structured comment blocks: `( comment 1 "hello world" )`

**External documentation:**
- Should provide high-level context, design rationale, and usage examples
- Should be maintained in sync with code changes
- Should cite applicable standards

## Version Control in Documentation

- Use revision letters for comprehensive design checkpoints (e.g., "Rev R5 — Landing Gear Analysis")
- Use revision numbers for incremental updates within a revision (e.g., "Rev L1", "Rev L2")
- Update the revision date when publishing a new version
- Keep a brief changelog for significant revisions

### Revision Numbering Rules

- A **revision with a letter** is a comprehensive update (e.g., Rev R, Rev N)
- **Modifications after a revision** are numbered: e.g., Rev N1, Rev N2 (incremental changes after Rev N)
- Numbers reset with each new letter revision
- Document all breaking changes or supersessions in the changelog

## Work Tracking and Documentation

When creating or updating documentation:

1. Add a commit message explaining the changes
2. If adding a new standard citation, update `REFERENCES.md` with validation details
3. If modifying a standards citation, verify the reference and update `REFERENCES.md`
4. Update `PROJECT_INDEX.md` when adding new active documentation files
5. Archive superseded documents in `archives/` and update `ARCHIVE_INDEX.md`
6. If the documentation work is complex or spans multiple documents, track subtasks in `TODO.md`

---

For project-wide standards, see the root `AGENTS.md`.
