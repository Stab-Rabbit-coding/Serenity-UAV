# Documentation Structure Templates

Governing file: `docs/AGENTS.md` — this document holds the per-document-type content templates
(design specifications, analysis/calculation documents, compliance records, build guides) and
the documentation-quality conventions that `docs/AGENTS.md` points to. For project-wide
standards see the root `AGENTS.md`.

## Design Specifications

Design specifications shall include:

- **Objective:** What capability is being specified
- **Standards basis:** Which regulation(s) or industry standard(s) the spec is drawn from
- **Functional requirements:** What the system must do
- **Performance requirements:** Quantified performance (thrust, power, mass, etc.)
- **Safety requirements:** Failure modes and mitigation
- **Testing/verification:** How compliance will be verified

## Analysis and Calculation Documents

Detailed analysis documents (e.g., `LANDING_GEAR_ANALYSIS.md`) shall include:

- **Title and revision:** e.g., "Rev R5 — Landing Gear Structural Analysis"
- **Problem statement:** What is being analyzed and why
- **Assumptions:** All simplifications and constraints
- **Calculations:** Detailed steps with units
- **Results:** Clear summary of findings and safety margins
- **Standards citations:** Which regulations/standards informed the analysis
- **References:** Sources for material properties, formulas, etc.

## Compliance Records

When implementing a standards requirement:

1. Document where the requirement is enforced (code file, PCB, structural detail, etc.)
2. Add a note with the REF-ID and section number
3. If testing is required, record the test result or link to the test report

## Build Guides and Fabrication Instructions

Build documentation shall include:

- **Step numbers** with clear, sequential instructions
- **Component lists** with part numbers, quantities, and sources
- **Material specifications** (filament type, print settings, fastener grade)
- **Safety hazard markings** for hazardous operations:
    - A *WARNING* signifies a hazard to personnel
    - A *CAUTION* signifies a hazard to equipment
    - All instructions that pose hazards to personnel and or equipment if not done correctly shall have a caution and or warning note specifying the nature of the hazard.
- **Tool requirements** (specialized fixtures, soldering iron settings, etc.)
- **Verification steps** to confirm correct assembly
- **Troubleshooting** for common issues

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
