# Serenity UAV — Claude Code Project Instructions

## Project Objective

- **Design and build a fully functional EDF Tilt Rotor UAV version of the Firefly Class Spaceship "Serenity" from the Joss Whedon TV show and movie.**
- **Provide redundancy and failover in all systems possible**:
- Avionics:  4 pairs of pocketbeagle2 industrial SBCs: 4 with a Flight Control and Sensor Cape, (called "Wash") (with GPS,  imu, compass, barometer, anti-collision range sensors,  airspeed, pid motor speed control, and nacelle tilt servos), and 4 with a Communications, Logging, and payload Cape, ( called "Zoë") .
- Node variant placement (v2 · v2 · v2 · v2, nose → tail, Rev Q):  All 8 nodes use EMI-hardened -2 capes (Wash, Zoë, XCVR-49MHZ-2) at every position.  Rev Q standardises on the single hardened SKU across all bays, providing uniform 5 kV galvanic isolation on CAN FD, RS-485, and Ethernet at every node.  Cape-A-1, Cape-B-1, and XCVR-49MHZ-1 are archived as of Rev Q (2026-06-05).
- Onboard Communications:  Each of the 8 sbcs will be connected to the others via: Canbus FD, MILSTD 1553, RS485, & Ethernet
- External Communications: The UAV uses WIFI at 5ghz, Zigbee at 2.4ghz, MavLink /SiK at 915Mhz, and AX.25 on the 49Mhz RCRS channels.  All four are usable for command and control of the aircraft.  The avionics capes also support sbus, but it's  not used.
- Powerplant: Each Nacelle has two EDFs in series, under PID control.  The forward EDF in each nacelle is controlled primarily by one of the flight control SBCs and the aft is primarily controlled by a different sbc.

- **Each Nacelle EDF is specified as a 50mm 6S EDF generating 1240g thrust based on the x-fly 2627-3200kv 12 fin design.**  Estimate a 90% efficiency on the 11 fin stator.  **Use 2232g per nacelle for static thrust.**  All thrust calculations will use this baseline.

- The large fuselage EDF is controlled by a third one.  **The fuselage EDF is housed in the tail cone. The cone is modified from canon by making it an expanding iris nozzle for the EDF.**  Each of the 4 fc sbcs can take over for all EDFs. **This EDF is now an optional addition once everything else works.**

- All Avionics shall be suitable for use in a variety of Unmanned Air, ground, or water vehicles and robots, not just this implementation.

- Avionics are designed to operate in extremely hostile em/rf environments, such as  experienced when inspecting commercial radio or cellular antennas while they are radiating. - **Design objective is operating in a 500 W/m^2 environment.**

- **Every message is secure, everything is logged**

- Every Cape has a TPM.
- Every message, internal and external, is digitally signed and authenticated.
- Everything is logged.  Sensors, messages, camera feed.
- The logs are saved to hardware-enforced non-executable microsd cards
- Everything complies with NIST SP800-207

## Design Philosophy

- All design decisions are for an **actual physical build**, not hypothetical or conceptual work.
Every component will be fabricated or procured; design accordingly.

## Engineering Requirements

- **Weight, balance, power, space, and component capabilities must always be accounted for.**

  Size fasteners, walls, and structural members for real loads. Quote actual masses and CG shifts
  when adding or removing geometry. Do not leave these as "TBD."

- **Failover capability is a first-class requirement.**  Wherever possible, every system must have

  a fallback mode or redundant path (dual ESCs, independent battery rails, manual override, etc.).

- **All EDF housings will be printed as part of the build.** Treat them as structural components,

  not wrappers. Wall thickness, infill, and material must be specified for each housing.

### Aircraft Geometery

- **Keep the skin geometry of Serenity true to the reference models** to the greatest extent possible. Interior modifications (bore carving, sleeve insertion, boss protrusions) must blend into the canonical exterior hull.  Do not alter the outer mold line unless structurally required.

- **Serenity has a very complex geometry, so bounding boxes and centroid calculations will  be inadequate for positioning and orienting parts.** Use this low detail model of Serenity <https://www.thingiverse.com/thing:4677565> as a guide to the geometry of the hull, when orienting the head, cargo, middle, and rear sections of the fuselage.

- The head section contains the bridge, and forms a narrow forward portion.

- The cargo section connects to it, as a broad, rounded section with a squared off bottom.  **The wings attach to the cargo section**

- The middle section consists of a narrow neck surrounded by a horseshoe like ring that is open at the bottom

- The rear section consists of a conical engine room with a pod centered above it and two skids below it. the skids are extensions of the horseshoe ring from the middle section, bent aft and extending past the end of the tail cone.

- **All legal and regulatory requirements will be based on United States jurisdiction**  All Radio transmissions shall comply with appropriate FCC regulations.  Markings, lights, and operation shall comply with all appropriate FAA aircraft regulations.

- **All designs will be validated against appropriate industry best practice.**  Specific applicable standards bodies are AUVSI, IEEE, and ISA.

## Coding Standards

- All code shall be clean and syntactically correct.  **Secure coding practices shall be used throughout.**

- All code and documentation shall be written in accordance with **strict linting rules and all linting standards shall be observed.**

- NIST SP800-82R3, 160, and 207 shall be complied with in information processing

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

- The canonical exterior skin **shall be hollowed to 2.0 mm while maintaining a watertight mesh surface without any voids or holes**, except as explicitly specified in build. The mating surfaces between the four fuselage sections, (head, cargo, middle, rear), will be open to allow construction access.

- The shell will be filled with 2lb/cf low-density foam to provide internal structure.

- Bosses and ribs will be added to the interior of the shell as needed for mounting hardware, components, or other structural flight requirements.

- To the greatest extent possible, mounting brackets for avionics, servos, sensors, antennas, and other hardware shall be integrated and printed as part of the shell.

- All mating surfaces that carry load must have a minimum 2-wall contact annulus and a positive-stop shoulder. Friction fits alone are not acceptable for flight-critical joints.

- **All stls, openscad, and other 3d models shall be clean and have watertight surface meshes.**  They should be ready to slice for printing.  A mesh verification **shall** be run after every 3d model modification.  All findings shall be reported, added to the repo TODO.md, and resolved.

- **All PCBs shall be fully developed**, with complete schematics files, pcb files, copper traces, proper ic footprints, and production ready gerber files.  After every modification, each schematic and pcb **shall** be run through kicad's Design Rules Checker (DRC) and all violations and errors shall be documented and corrected.

- Design for **Common Hand-tool field disassembly** of any component that may need in-field replacement.

## Revisions and Version Control

- A project revision with a letter is a comprehensive update and checkpoint for the project. All changes from the previous Revisions are integrated, all documents are updated and all capabilities are baseline.

- All components are referenced as of the latest revision, even if there was no change on that component's specifications since a much earlier revision.

- Modifications to components after a Revision are shown as the Revision letter followed by a number, such as: J1, as the first odifications after Revision J, or M4, as the fourth modification of that component after Revision M.  These numbers reset with every revision. all active components carried forward to a new revision are part of that Revisions baseline.

- All items that are archived prior to a Revision retain the Revision label which they held at the time of archival, and are not included in future revisions.

### Component Naming (yes, I realize that this is very nerdy, but "Number 2, make it so!")

 The ground control station is named "Malcolm" aka "CAPT Reynolds" or "CAPT Tight Pants" - "I aim to misbehave"

 The Flight Control Avionics Cape is named "Wash" - "I'm a leaf on the wind"

 The Comms/Logging/Payload Cape is named "Zoë" - "Big Damn Heros, sir."

 The Power Distribution Board is named "Kaylee" - "Everything is shiny."

 The Cargo handling system is named "Jayne" - "I was aiming for his head."

 The forward avionics bay is named "Shepherd's room" - "I have heathens enough right here."

 The second avionics bay is named "Inara's shuttle" - "Mal, I will never understand you."

 The third avionics bay is named "River's room" - "Also, I can kill you with my mind."

 The aft avionics bay is named "Simon's medbay" - "What did they do to you?"

Avionics Workload Balancing
While all Wash capes are identical and all Zoë capes are also identical, they have different primary tasking. All Stacks are capable to communicate and control the UAV safety in a benign environment on their own.*

UAV Tasks with PACE prioritization and failover per stack (primary, alternative, contingency, emergency)

-- Watchdog: P - Shepherd; A - Inara; C - Simon, E - River

-- Comms: P - Inara; A - Shepherd; C - River; E - Simon

-- Flight Control: P - River; A - Simon; C - Shepherd; E - Inara

-- Payload Control: P - Simon; A - River; C - Inara; E - Shepherd

Mal is the ground control station - He's the boss.

Shepherd is the crew's conscience and therefore takes care of primarily watchdog, fault detection, failover, and authentication. His stack has SiK primary and WiFi secondary.

Inara has primarily camera, external sensors, and high bandwidth ground communication. Her stack is connected to WiFi primarily and LoRa secondary.

River provides primary control of the forward EDFs, and provides EDF and nacelle control command and syncing, and the most resilient comms. She may be crazy, but she comes through when no one else can. She has 49Mhz RCRS primary and LoRa secondary.

Simon is the alternate watchdog for the ship, but most of his attention is on River. He's got aft EDF control and alternate nacelle control. He follows River's lead but makes sure she doesn't crash the ship. Simon also controls Jayne, and ensures that the cargo isn't jettisoned or the crew abandoned. He's got 49MHz as his primary antenna and SiK as his backup.
## Workflow Notes

- Run Blender scripts with `blender --background --python <script>.py` — the machine supports headless execution.

- Output STLs go to `airframe/stls/` (subdirectories: `fuselage/`, `nacelles/`, `wings/`).
- When a script regenerates STLs, verify Z-range and bore-diameter in the console output before committing.

- Any time that an assistant creates a todo list to accomplish a task for the build, the steps shall be added as sup-tasks in the appropriate paragraph of the root repo TODO.md wbs, conforming to proper style, so that unresolved issues can be picked up in future sessons.
