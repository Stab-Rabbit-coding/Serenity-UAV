u# Serenity UAV — Claude Code Project Instructions

## Project Objective

- **Design and build a fully functional EDF Tilt Rotor UAV version of the Firefly Class Spaceship "Serenity" from the Joss Whedon TV show and movie.**
- **Provide redundancy and failover in all systems possible:
-- Avionics:  4 pairs of pocketbeagle2 industrial SBCs: 4 with a Flight Control and Sensor Cape, and 4 with a Communications, Logging, and payload Cape.
-- Onboard Communications:  Each of the 8 sbcs will be connected to the others via: Canbus FD, MILSTD 1553, RS485, & Ethernet
-- External Communications: The UAV uses WIFI at 5ghz, Zigbee at 2.4ghz, MavLink /SiK at 915Mhz, and AX.25 on the 49Mhz RCRS channels.
-- Powerplant: Each Nacelle has two EDFs in series, under PID control.  The forward EDF in each nacelle is controlled primarily by one of the flight control SBCs and the aft is primarily controlled by a different sbc.  The large fuselage EDF is controlled by a third one.  Each of the 4 fc sbcs can take over for all EDFs.

- **Every message is secure, everything is logged**

-- Every Cape has a TPM.
-- Every message, internal and external, is digitally signed and authenticated.
-- Everything is logged.  Sensors, messages, camera feed.
-- The logs are saved to hardware-enforced non-executable microsd cards

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

- **Keep the skin geometry of Serenity true to the reference models** to the greatest extent possible. Interior modifications (bore carving, sleeve insertion, boss protrusions) must blend into the canonical exterior hull.  Do not alter the outer mold line unless structurally required.
-- Serenity has a very complex geometry, so bounding boxes and centroid calculations will  be inadequate for positioning and orienting parts. Use this low detail model of Serenity https://www.thingiverse.com/thing:4677565 as a guide to the geometry of the hull, when orienting the head, cargo, middle, and rear sections of the fuselage. 

- **All legal and regulatory requirements will be based on United States jurisdiction**  All Radio transmissions shall comply with appropriate FCC regulations.  Markings, lights, and operation shall comply with all appropriate FAA aircraft regulations.
- **All designs will be validated against appropriate industry best practice.**  Specific applicable standards bodies are AUVSI, IEEE, and ISA.

## Coding Standards

- All code shall be clean and syntactically correct.  **Secure coding practices shall be used throughout.**
- All code and documentation shall be written in accordance with strict linting rules and all linting standards shall be observed.
- All code shall use 4 space indenting, whether or not required by the language.
- All code shall use verbose commenting, in strict conformity to each language.  In the case of a language that doesn't allow inline comments, such as kicad files, comments shall be included in an accompanying markdown file.
- Commenting in KiCad files using ; or # is strictly prohibited. All comments for kiCad files must be either in a markdown file or comment blocks such as: ( comment 1 "hello world" )

## Licensing and Attribution

- All work is **published under CC BY 4.0**.
- The author of this project is Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
- Every design decision, algorithm, or geometry technique that draws on an external reference
  **must be cited** in the relevant source file docstring or commit message.
- Derivative files must carry the full attribution chain back to upstream sources.

## Fabrication Standards

- Primary structural material: **CF-PETG** (0.15 mm layer height, 4 perimeters, ≥ 40% infill for load-bearing regions; 25% infill for non-structural fill).

- Secondary / non-structural: **PETG** at same layer height.

- The canonical exterior skin shall be hollowed to 2.0 mm while maintaining a watertight mesh surface without any voids or holes, except as explicitly specified in build. The mating surfaces between the four fuselage sections, (head, cargo, middle, rear), will be open to allow construction access.

- The shell will be filled with 2lb/cf low-density foam to provide internal structure.

- Bosses and ribs will be added to the interior of the shell as needed for mounting hardware, components, or other structural flight requirements.

- To the greatest extent possible, mounting brackets for avionics, servos, sensors, antennas, and other hardware shall be integrated and printed as part of the shell.

- All mating surfaces that carry load must have a minimum 2-wall contact annulus and a positive-stop shoulder. Friction fits alone are not acceptable for flight-critical joints.

- All stls, openscad, and other 3d models shall be clean and have watertight surface meshes.  They should be ready to slice for printing. 

- All PCBs must be fully developed, with complete schematics files, pcb files, copper traces, proper ic footprints, and production ready gerber files.

- Design for **Common Hand-tool field disassembly** of any component that may need in-field replacement.

-
## Workflow Notes

- Run Blender scripts with `blender --background --python <script>.py` — the machine supports
  headless execution.
- Output STLs go to `airframe/stls/` (subdirectories: `fuselage/`, `nacelles/`, `wings/`).
- When a script regenerates STLs, verify Z-range and bore-diameter in the console output before
  committing.