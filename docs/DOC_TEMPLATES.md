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

## Owner Decision Briefs

Owner direction, 2026-11-08: every option put to the owner for a decision (an OD-x item, a design
choice, a part or spec change) is presented with the six checks below, each with a picture, and with
vectors (force, moment, load-path or motion arrows) wherever a load or a motion is involved. A check
that does not apply says so in one line and why; none is silently skipped. Units follow root
`AGENTS.md` §5 (imperial first, metric in parentheses). Record the brief, or its figures, in the owning
`WBS.md` entry and `docs/figures/`.

| Check | What it must show |
|---|---|
| **Statics and dynamics** | Free-body diagram of the affected part(s): applied loads, reactions, moments as vectors with magnitudes; the governing load case (hover, gust, landing, tilt slew, vibration); stresses or allowables where one exists, and "requires verification" where it does not (`current-specification/allowables.json`). |
| **Function** | What the part has to do and whether each option still does it (stroke, clearance, electrical or flow path, service access, install/remove). |
| **Structural integrity** | Minimum walls (`AGENTS.md` §7), load path continuity, stress concentrations, fastener/insert margins, print orientation where it governs strength. |
| **Mechanism and component interactions** | Every neighbour the change touches, at rest and through the full range of motion (tilt −5…+135°, nozzle stroke, doors): interference volumes, nearest gaps, wire/harness routes. Run both sides when the parts are handed. |
| **Weight and balance** | Mass change per part and per aircraft (lbm (g)), CG shift, the nacelle pivot residual, hover arm and ground clearance, T/W; say which ledger picks the change up and when. |
| **Canonical shape** | Effect on the outer mould line against the canonical references (`docs/AGENTS.md` authority order: QMx REF-CAD-003, then REF-CAD-002, then REF-CAD-004); "internal only" is an answer when true. |

Each brief ends with the options side by side, a recommendation and its reason, and what is still
unverified.

### Avionics and power-electrical check set

Owner direction, 2026-11-14 (PR #289): a brief or design review for an avionics board, a power
electrical system, a motor or a sensor uses the six checks below. Two of the airframe checks are
swapped and a thermal check is added; Function, Structural integrity and Mechanism and component
interactions carry over from the table above. The rule that no check is silently skipped still
applies.

| Check | What it must show |
|---|---|
| **Electrical engineering** (replaces Statics and dynamics) | Electrical load: each rail's typical and peak current against its source, regulator, connector and wire rating, with margin. Emissions: switching and clock frequencies, radio transmit bands and powers, the nearest victim (GNSS, magnetometer, receivers) and the isolation or filtering between them, against the board's stated EMC targets. |
| **Function** | As above. |
| **Structural integrity** | As above, for the board, its mounts and its connectors. |
| **Mechanism and component interactions** | As above, plus every bus, harness and neighbouring board the change touches. |
| **Weight and balance** | As above. In addition, the mass and CG of the board's **fasteners, connectors and wire harness** are tracked as their own ledger lines for each PCB, not folded into the board mass. |
| **Wire harness, fastener and mounting fit** (replaces Canonical shape) | Harness route and bend radius, connector mating and unmating clearance, fastener type, length and engagement, mount and saddle fit, and service access, checked on the real meshes. |
| **Thermal load** (added) | Heat dissipated at typical and peak electrical load, the heat path to ambient, the design ambient, and each part's computed or measured temperature against its datasheet limit. Applies to all avionics and power electrical systems, motors and sensors included. |

A change to the outer mould line caused by an avionics item (an antenna, a vent, a sensor window)
still gets the Canonical shape check from the airframe table.

## Compliance Records
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
