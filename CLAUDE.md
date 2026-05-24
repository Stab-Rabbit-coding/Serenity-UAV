# Serenity UAV — Claude Code Project Instructions

## Design Philosophy

All design decisions are for an **actual physical build**, not hypothetical or conceptual work.
Every component will be fabricated or procured; design accordingly.

## Engineering Requirements

- **Weight, balance, power, space, and component capabilities must always be accounted for.**
  Size fasteners, walls, and structural members for real loads. Quote actual masses and CG shifts
  when adding or removing geometry. Do not leave these as "TBD."
- **Failover capability is a first-class requirement.**  Wherever possible, every system must have
  a fallback mode or redundant path (dual ESCs, independent battery rails, manual override, etc.).
- **All EDF housings will be printed as part of the build.** Treat them as structural components,
  not wrappers. Wall thickness, infill, and material must be specified for each housing.
- **Keep the skin geometry of Serenity true to the reference models** to the greatest extent
  possible. Interior modifications (bore carving, sleeve insertion, boss protrusions) must blend
  into the canonical exterior hull.  Do not alter the outer mold line unless structurally required.
- **All legal and regulatory requirements will be based on United States jurisdiction**  All Radio transmissions shall comply with appropriate FCC regulations.  Markings, lights, and operation shall comply with all appropriate FAA aircraft regulations.
- **All designs will be validated against appropriate industry best practice.**  Specific applicable standards bodies are AUVSI, IEEE, and ISA.

## Coding Standards

- All code shall be clean and syntactically correct.  **Secure coding practices shall be used throughout.**
- All code and documentation shall be written in accordance with strict linting rules and all linting standards shall be observed.
- All code shall use 4 space indenting, whether or not required by the language.
- All code shall use verbose commenting, in strict conformity to each language.  In the case of a language that doesn't allow inline comments, such as kicad files, comments shall be included in an accompanying markdown file.


## Licensing and Attribution

- All work is **published under CC BY 4.0**.
- Every design decision, algorithm, or geometry technique that draws on an external reference
  **must be cited** in the relevant source file docstring or commit message.
- Derivative files must carry the full attribution chain back to upstream sources.

## Fabrication Standards

- Primary structural material: **CF-PETG** (0.15 mm layer height, 4 perimeters, ≥ 40% infill
  for load-bearing regions; 25% infill for non-structural fill).
- Secondary / non-structural: **PETG** at same layer height.
- The Shell will be filled with 2lb/cf low-density foam to provide internal structure
- All mating surfaces that carry load must have a minimum 2-wall contact annulus and a
  positive-stop shoulder. Friction fits alone are not acceptable for flight-critical joints.
- All stls, - All PCBs must be fully developed, with complete schematics files, pcb files, copper traces, proper ic footprints, and production ready gerber files.

- Design for **Common Hand-tool field disassembly** of any component that may need in-field replacement.

-
## Workflow Notes

* Run Blender scripts with `blender --background --python <script>.py` — the machine supports
  headless execution.
- Output STLs go to `thingverse-serenity/files-hollowed-18in/`.
- When a script regenerates STLs, verify Z-range and bore-diameter in the console output before
  committing.


