# Serenity UAV — Claude Code Project Instructions

## Project Objective

- **Design and build a fully functional EDF Tilt Rotor UAV version of the Firefly Class Spaceship "Serenity" from the Joss Whedon TV show and movie.**
- **Provide redundancy and failover in all systems possible**:
- Avionics:  4 pairs of pocketbeagle2 industrial SBCs: 4 with a Flight Control and Sensor Cape, (called "Wash") (with GPS,  imu, compass, barometer, anti-collision range sensors,  airspeed, pid motor speed control, and nacelle tilt servos), and 4 with a Communications, Logging, and payload Cape, ( called "Zoë") .
- Node variant placement (Rev R1):  All 8 nodes carry Wash (Cape-A-2) and Zoë (Cape-B-2), providing uniform 5 kV galvanic isolation on CAN FD, RS-485, and Ethernet at every node.
  Emma XCVR boards are installed only in **River's Room and Simon's Medbay** — the two bays whose primary external radio is 49 MHz (47 CFR Part 15 §15.235, not RCRS — see REF-FCC-003); Shepherd's Room and Inara's Shuttle do not carry Emma boards.
  Cape-A-1, Cape-B-1, and XCVR-49MHZ-1 are archived as of Rev Q (2026-06-05).
- **Emma (add LoRa, replace JST GH 6P with P1+P2 socket rails): RECONCILED 2026-07-04 via a
  schematic-first migration (user decisions locked).** A complete `Emma.kicad_sch` was
  authored from the as-placed PCB (`avionics/kicad/gen_emma_sch.py`; loads, ERC 0 errors) and
  the PCB transformed to match (`avionics/kicad/mod_emma_pcb.py`); sch↔pcb parity is exact (74
  refs, 104 nets). J1 (JST-GH-6P) was DROPPED (modem UART moved onto the PB2 rails), PTT_N and
  a new RSSI carrier-detect (`RSSI_DCD`, on-board comparator) ride presence-gated PB2-P2
  payload GPIOs. Open items (final placement/routing of 4 new parts, comparator datasheet
  vetting, pinmux firmware sign-off) are in TODO.md §1.2b.
- **Zoë (remove LoRa, add P1+P2 passthrough rails): PCB already at end-state, schematic
  lags.** Verified 2026-07-04: `Zoë.kicad_pcb` already has LoRa removed and the P1/P2 (+TOP)
  passthrough rails placed; `Zoë.kicad_sch` still carries the LoRa block, the obsolete
  `J_XCVR` Emma-cable connector, and an SBUS block, AND uses a **different reference-designator
  convention** from the PCB. A load-blocking stray-`(comment)` bug in `Zoë.kicad_sch` was fixed
  (it now opens in kicad-cli). The remaining schematic reconciliation needs a user-confirmed
  sch↔pcb reference remap (flight-hardware footprint↔symbol association must not be guessed) —
  see `avionics/CLAUDE.md` and TODO.md §1.2b.
- **Kaylee — remove the 6 V servo BEC; tilt servos to run on the 5 V rail** (~21 kg·cm capacity
  vs the ~16 kg·cm tilt load requirement) — planned, not yet implemented in KiCad; the
  numbering of this modification (previously mislabeled "Rev A1") should follow the current
  Rev S baseline once picked up (i.e. Rev S1, matching Emma/Zoë) — flagged, not renumbered here
  since Kaylee's own schematic/PCB have not been touched to verify current state the way Emma/
  Zoë were.
  Kaylee.kicad_sch still carries the 6 V/5 A `U_BEC_6V` (TPS54540DDAR) servo rail — see
  Kaylee.md, which describes the as-built (pre-modification) design.
- Onboard Communications:  Each of the 8 sbcs will be connected to the others via: Canbus FD, MILSTD 1553, RS485, & Ethernet
- External Communications: The UAV uses Wi-Fi at 5ghz, Zigbee at 2.4ghz, MavLink /SiK at 915Mhz, and AX.25 on the 49Mhz channel (47 CFR Part 15 §15.235, an unlicensed band — not Part 95 RCRS).  All four are usable for command and control of the aircraft.  The avionics capes also support sbus, but it's  not used.
- Powerplant: Each Nacelle has two EDFs in series, under PID control.  The forward EDF in each nacelle is controlled primarily by one of the flight control SBCs and the aft is primarily controlled by a different sbc.

- **Each Nacelle EDF is specified as a 50mm 6S EDF generating 1240g thrust based on the x-fly 2627-3200kv 12 fin design.**  Estimate a 90% efficiency on the 11 fin stator.  **Use 2232g per nacelle for static thrust.**  All thrust calculations will use this baseline.

- The large fuselage EDF is controlled by a third one.  **The fuselage EDF is a 55 mm 6S unit housed in the tail cone.  The tail cone retains its canonical Serenity nozzle — a fixed elliptical exit 2.06 in (52.3 mm) wide (X) × 1.76 in (44.7 mm) tall (Z); it is NOT modified into an iris.
  The fuselage EDF also feeds 4 RCS (reaction-control) bleed-air thrusters that provide pitch/yaw attitude authority, tapping ~15 % of the EDF mass flow; the remainder exits the canonical aft nozzle as forward thrust.**
  Because the canonical nozzle exhausts longitudinally, the fuselage EDF contributes horizontal (forward-flight) thrust only and is **not** counted in hover thrust-to-weight.
  Each of the 4 fc sbcs can take over for all EDFs. **This EDF is now an optional addition once everything else works.**

- All Avionics shall be suitable for use in a variety of Unmanned Air, ground, or water vehicles and robots, not just this implementation.

- Avionics are designed to operate in extremely hostile em/rf environments, such as  experienced when inspecting commercial radio or cellular antennas while they are radiating. - **Design objective is operating in a 500 W/m^2 environment.**

- **Every message is secure, everything is logged**

- Every Cape has a TPM.
- Every message, internal and external, is digitally signed and authenticated.
- Everything is logged.  Sensors, messages, camera feed.
- The logs are saved to hardware-enforced non-executable microsd cards
- Everything complies with NIST SP 800-207 Zero Trust Architecture [REF-NIST-001 §2.1, §2.2, §3.3]

- See README.md for design mission profile.

## Design Philosophy

- All design decisions are for an **actual physical build**, not hypothetical or conceptual work.
Every component will be fabricated or procured; design accordingly.

## Scope-Specific Guidance

This root `CLAUDE.md` provides **project-wide standards** applicable to all folders. For specific guidance within a particular subsystem, consult the federated `CLAUDE.md` file in that folder:

- **[airframe/CLAUDE.md](airframe/CLAUDE.md)** — Structural design, CAD/3D modeling, hull-frame coordinate system, fabrication standards (CF-PETG, wall thickness, infill), STL validation, SCAD conventions, FreeCAD assembly
- **[avionics/CLAUDE.md](avionics/CLAUDE.md)** — KiCad PCB design, cape naming (Wash, Zoë, Emma, Kaylee), avionics stacks, security and cryptography, DRC workflow, communications protocols
- **[docs/CLAUDE.md](docs/CLAUDE.md)** — Documentation standards, standards vetting policy, references management, measurements and units, version control
- **[gcs/CLAUDE.md](gcs/CLAUDE.md)** — Ground Control Station (Malcolm), command and control, telemetry display, communications channels, operator interface
- **[tools/CLAUDE.md](tools/CLAUDE.md)** — Build scripts and automation, hull-frame bake tool, Blender pipeline, SCAD generation, mesh validation
- **[current-specification/CLAUDE.md](current-specification/CLAUDE.md)** — Active design specifications, revision numbering, traceability matrix, standards citations
- **[graphical-build-guide/CLAUDE.md](graphical-build-guide/CLAUDE.md)** — Phased build instructions, fabrication checklists, assembly sequences, troubleshooting guides
- **[deferred/CLAUDE.md](deferred/CLAUDE.md)** — Phase 11+ work (rear EDF, RCS), planned upgrades (Emma R1, Zoë R1, Kaylee A1), alternative designs

Each federated file assumes you have already read this root document. **This root file is authoritative for all project-wide standards.** Subordinate files provide additional detail and scope-specific workflows.

## Standards Vetting Policy

- **Every design specification with any effect beyond cosmetic appearance must be vetted against applicable industry standards and/or regulations before implementation.**  Standards citations shall be recorded in `REFERENCES.md`, which catalogs every applicable standard with:
    - Standard designation and full title
    - Validated URL for official access (verified against the issuing body)
    - Specific chapter, section, and paragraph applied
    - Every repository location where the standard is cited

- **All citations throughout the codebase** — in code comments, documentation, schematics, and build guides — shall reference the `REFERENCES.md` REF-ID (e.g., `[REF-FCC-001 §15.247(b)(3)(ii)]`) and shall include chapter, section, and paragraph to enable auditing.

- **No fabricated, unverifiable, or incorrectly attributed references are permitted.**  Any citation that cannot be traced to a specific published document with a validated URL must be removed or corrected.  Removed or superseded citations are documented in the "Removed / Superseded Citations" section of `REFERENCES.md`.

- **Applicable standards bodies for this project:** FAA (airworthiness, registration, operations), FCC (radio frequency), NIST (cybersecurity and information security), DoD/DLA (MIL-STD bus protocols), ISO (data bus protocols), IEC (component safety), VDE (isolator certification), IEEE (networking standards), ISA/IEC 62443 (OT/ICS cybersecurity),
  AUVSI/ASTM F38 (UAS design guidelines), and ICAO (international aviation rules).

## Engineering Requirements

- **Weight, balance, power, space, and component capabilities must always be accounted for.**

  Size fasteners, walls, and structural members for real loads. Quote actual masses and CG shifts
  when adding or removing geometry. Do not leave these as "TBD."

- **All measurements shall be expressed imperial-primary with metric in parentheses: e.g. 10 in (254 mm), 2.5 lbm (1.13 kg), 4.8 lbf (21.4 N).**
    - Use **lbm** for mass (pounds-mass) and **lbf** for force (pounds-force); never write bare "lb" where the distinction matters.
    - Metric equivalents use **kg** for mass and **N** for force.
    - Thrust, lift, and aerodynamic loads are forces → lbf / (N).  Component weights and payload capacity are masses → lbm / (kg).
    - **Airspeed and wind speed are expressed in knots (kt)** with m/s in parentheses where needed for calculation.  Never use mph or km/h for airspeed.

- **Failover capability is a first-class requirement.**  Wherever possible, every system must have

  a fallback mode or redundant path (dual ESCs, independent battery rails, manual override, etc.).

- **All EDF housings will be printed as part of the build.** Treat them as structural components,

  not wrappers. Wall thickness, infill, and material must be specified for each housing.

- **PCBs are tightly packed. all final component footprint positions will be done manually, after pcbs are populated and nets are built by script.**  If a kicad drc violation requires repositioning a component footprint, refer the action to the user.  Other modifications are allowed.

### Aircraft Geometery

- **Keep the skin geometry of Serenity true to the reference models** to the greatest extent possible. Interior modifications (bore carving, sleeve insertion, boss protrusions) must blend into the canonical exterior hull.  Do not alter the outer mold line unless structurally required.

- **Serenity has a very complex geometry, so bounding boxes and centroid calculations will  be inadequate for positioning and orienting parts.** Use the validated orientation and positions listed below for determining where parts fit in space.  If there's uncertainty, ask the user to do a manual placement in freecad.  Be ready to tweak final fine alignment after receiving rough positioning.

- The head section contains the bridge, and forms a narrow forward portion.

- The cargo section connects to it, as a broad, rounded section with a squared off bottom.  **The wings attach to the cargo section**

- The middle section consists of a narrow neck surrounded by a horseshoe-like ring that is open at the bottom.  **The middle section is one printed piece comprising two distinct structural elements:** (1) the outer horseshoe ring (the U-shaped exterior frame visible on the outside of the ship, open at −Z/ventral), and
  (2) the inner neck (a tube-like passage that canonically connects the cargo bay interior to the rear engine room interior through the centre of the horseshoe, within the outer hull skin).
  These elements are inseparable in the canonical Blender-derived geometry.  The aft EDF intake scoops (reduced-area radial cuts into the inner neck feeding the 55 mm rear EDF) are **deferred to Phase 11** — the inner neck is a closed, uncut tube in Phases 5–10 prints.

- The rear section consists of a conical engine room with a pod centered above it and two skids below it. the skids are extensions of the horseshoe ring from the middle section, bent aft and extending past the end of the tail cone.

- **Canonical landing leg model (Rev R5): vertical post + 4-wire brace.** The original
  canonical single-blade leg (misubisu Thingiverse hull, CC BY 4.0) is itself a vertical
  part with two branch points of its own — one at the apex (top) and one about 1/3 of
  the way down from the apex. Each of the 4 cargo-corner landing gear assemblies keeps
  only a short CF-PETG **vertical post** (foot up through the 1/3-down branch height,
  100% infill, not expected to ever yield) and braces it to the hull with **four simple
  wires**: 2 **spring** wires at the apex (elastic, fully recoverable for ordinary hard
  landings) and 2 **ductile** wires at the 1/3-down branch (each independently sized to
  absorb the entire 6 ft full-AUW worst-case impact energy on its own, by progressively
  deepening a single pre-formed bow — a visible, field-replaceable "fired" indicator).
  Each wire is a single piece of wire stock with one shallow pre-bend, chosen
  specifically for manufacturability and field replacement over more complex shapes
  (an elastic spring-steel leaf and a closed-ring wire fuse were both evaluated and
  rejected in earlier revisions — see `docs/LANDING_GEAR_ANALYSIS.md` Rev R3/R4 history).
  This retires the Rev R1.4 parametric corner V-brace concept
  (`airframe/openscad/fuselage/landing_leg_assy.scad`, never rendered or printed) and
  the intermediate "Strong-Leg" forked-CF-PETG-arm concept (Rev R2–R4). SCAD source:
  `airframe/openscad/fuselage/wire_brace_leg.scad`. Full structural analysis and
  joint-fitting specs: `docs/LANDING_GEAR_ANALYSIS.md` (Rev R5); build tasks: `TODO.md`
  §1.1.4.

- Each nacelle has a variable diameter exhaust nozzle, driven passively by gear train, based on nacelle tilt. **The nozzles shall provide a smooth conical exit for the edf thrust tube, no matter its final diameter** exit diameter will be 75% of bore at 0 deg (forward) and 105% of bore at or above 90 deg (virtical or backing).

#### Hull-Frame Coordinate Standard (Rev R1 — baked, canonical)

The canonical assembly document is `airframe/freecad/assembly/SerenityAssembly.FCStd`.
The headless assembly script is `airframe/FreeCAD-scripts/serenity_assembly.py` (run with `freecadcmd`).

**All design artifacts — SCAD sources, STLs, Blender/FreeCAD scripts, and documentation — use one coordinate system, the hull frame:**

- **X** — positive port (left) — the lateral axis
- **Y** — positive aft (back) — the longitudinal axis (nose tip at Y ≈ −305.6 mm)
- **Z** — positive dorsal (up)
- **Origin** — the `SerenityAssembly.FCStd` world origin

**R1 (2026-06-11) — placements are baked into the STLs.** The placements that were manually validated in FreeCAD on 2026-06-10 have been applied directly to the STL vertex data by `tools/bake_hull_frame.py`. Every primary STL in `airframe/stls/` is therefore stored **directly in hull-frame coordinates** and imports into FreeCAD with an **identity placement**.
No per-part transform may be applied or re-derived when positioning these components. Baked files carry the marker `SerenityUAV HULL-FRAME R1` in their binary STL header; the bake tool refuses to transform a marked file, so the bake can never be applied twice.

**Canonical fuselage source — Blender pipeline (Rev R1, 2026-06-13):**
The four fuselage shell STLs are generated by the Blender hollowing pipeline
(`airframe/blender-scripts/`) and stored as the pre-bake source files in
`airframe/blender-scripts/files-hollowed-24in/`.  These are the **authoritative
canonical sources** for all fuselage geometry.  Any future geometry change to a
fuselage section must start from the corresponding Blender source file in that
directory — SCAD files for fuselage shells are secondary references only.

Bake pipeline for fuselage sections:

1. Update source in `airframe/blender-scripts/files-hollowed-24in/`
2. Copy updated file to `airframe/stls/fuselage/` (or `fuselage/cargo/` for cargo)
3. Run bake tool (step 3 below)

**Pipeline rule:** generator scripts may model parts in a convenient part-local frame, but any regenerated primary-component STL must be re-baked before publishing:

```sh
python3 tools/bake_hull_frame.py            # all components (idempotent)
python3 tools/bake_hull_frame.py --check    # report baked state only
```

Never bake a mesh *derived from* an already-baked file (e.g. a Blender repair output of a baked STL is already hull-frame but loses the header marker).

**Validated baked extents (hull frame, mm) — updated 2026-06-13 from Blender-canonical source:**

| Component | X min..max | Y min..max | Z min..max |
| --- | --- | --- | --- |
| Head_Shell | −232.9..−103.5 | −305.7..−70.7 | +61.1..+201.5 |
| Cargo_Shell | −267.0..−72.7 | −71.5..+132.0 | 0.0..+163.2 |
| Middle_Shell | −258.5..−81.6 | +130.4..+203.6 | +1.3..+166.1 |
| Rear_Shell | −246.1..−105.5 | +203.2..+384.3 | +3.3..+161.1 |
| Wing_Port | −93.0..+4.7 | −7.0..+122.0 | +48.0..+77.0 |
| Wing_Stbd | −347.7..−250.0 | −12.0..+117.0 | +48.0..+77.0 |
| Nacelle_Port | +4.0..+86.0 | −58.2..+108.3 | +21.4..+104.7 |
| Nacelle_Stbd | −428.1..−346.1 | −64.2..+102.3 | +23.3..+106.6 |

The historical bake transforms (position + quaternion per component) live solely in `tools/bake_hull_frame.py` `COMPONENTS` — do not duplicate them elsewhere. Nacelle STLs are stored in **cruise / forward-flight attitude**; hover is a downstream rotation about the tilt pivot (duct station 83 mm), never a stored orientation. Minor joint fine-tuning (fractions of mm / degree) is still pending.

**R1 audit findings:**

- ~~Nacelle port/stbd labels swapped~~ — **RESOLVED 2026-06-11** (Rev R1/nacelle-swap). STL files renamed, binary headers patched, SCAD build commands corrected. Port nacelle: hull +X, SWIRL_DIR=−1, PYLON_SIDE=−1. Stbd nacelle: hull −X, SWIRL_DIR=+1, PYLON_SIDE=+1.
- The 2026-06-10 head↔cargo joint analysis used hull X as the longitudinal mating axis; in the validated frame the longitudinal axis is **Y** (head and cargo mate at hull Y ≈ −71 mm). Re-verify BOSS_FORE/BOSS_AFT positions (TODO.md §1.1.1.1). **Open.**

**Documented exceptions to the hull-frame standard:**

- Avionics KiCad files keep KiCad board coordinates (each stack mounts in a different orientation).
- Malcolm GCS hardware (ground-support equipment) uses part-local print frames.
- G-code / printer files use printer-bed coordinates; slicers reorient baked STLs for printing as needed.

**Spatial relationships (qualitative):**

- **Head** is the forwardmost section; it contains the bridge and tapers to a narrow nose. The nose tip reaches the most negative Y extent in the assembly (Y=aft, so most negative Y = most forward).
- **Cargo** is immediately aft of and below the head. The wing attachment flanges are on its upper outer edges. The cargo bay door opens toward −Z (belly/ventral). The cargo section has the largest cross-sectional area of the four fuselage sections.
- **Middle** is the narrow horseshoe-ring neck between cargo and rear. The ring is open at the bottom (−Z, ventral). The middle section is **one printed piece** comprising the outer horseshoe ring and the inner neck tube (which passes through the centre of the horseshoe connecting the cargo bay interior to the rear engine room interior).
  Aft EDF intake scoops into the inner neck (reduced-area, sized for the 55 mm rear EDF) are deferred to Phase 11. The avionics bays are distributed along this section and the cargo section.
- **Rear** is the aftmost fuselage section. It houses the engine room / tail cone, the dorsal pod, and the two landing skids. The skids run aft past the tail cone end.
- **Wings** are symmetric about the aircraft lateral (X) centerline at approximately X ≈ −171 mm. Each wing spans outboard in ±X from its root at the cargo section lateral walls.
- **Nacelles** are outboard of the wings at the pylon tips. The STLs and assembly are stored in forward-flight / cruise attitude. In hover the nacelles tilt to fire thrust downward.

- **All legal and regulatory requirements will be based on United States jurisdiction**
  All radio transmissions shall comply with FCC regulations [REF-FCC-001, REF-FCC-002, REF-FCC-003].
  Markings shall comply with [REF-FAA-001 §48.205].
  Navigation lights shall comply with [REF-FAA-003 §91.209(a)].
  Flight operations shall comply with [REF-FAA-002].

- **All designs will be validated against appropriate industry best practice.**
  Applicable standards bodies and specific references: AUVSI [REF-AUVSI-001], IEEE [REF-IEEE-001,
  REF-IEEE-002, REF-IEEE-003], ISA [REF-ISA-001], ISO [REF-ISO-001], IEC [REF-IEC-001],
  VDE [REF-VDE-001], ICAO [REF-ICAO-001].  See `REFERENCES.md` for the full catalog.

## Coding Standards

- All code shall be clean and syntactically correct.  **Secure coding practices shall be used throughout.**

- All code and documentation shall be written in accordance with **strict linting rules and all linting standards shall be observed.**

- NIST SP 800-82 Rev 3 [REF-NIST-002 §5.3, §5.4, §6.2.5], NIST SP 800-160 Vol 1 Rev 1
  [REF-NIST-003 Ch.3], and NIST SP 800-207 [REF-NIST-001 §2.1] shall be complied with
  in information processing and system security engineering

- All code shall use 4 space indenting, whether or not required by the language.

- All code shall use verbose commenting, in strict conformity to each language.  In the case of a language that doesn't allow inline comments, such as kicad files, comments shall be included in an accompanying Markdown file.

- Commenting in KiCad files using ; or # is strictly prohibited. All comments for kiCad files must be either in a Markdown file or comment blocks such as: ( comment 1 "hello world" )

## Licensing and Attribution

- All work is **published under CC BY 4.0**.
- The author of this project is Steve Griffing, PE(CSE), CISSP-ISSEP, CPP.  The avionics boards are marked with his personally owned LLC name, but he retains personal copyright.

- Every design decision, algorithm, or geometry technique that draws on an external reference
  **must be cited** in the relevant source file docstring or commit message.

- Derivative files must carry the full attribution chain back to upstream sources.

## Fabrication Standards

- **CF-PETG** (0.15 mm layer height, 4 perimeters, ≥ 40% infill for load-bearing regions; 25% infill for non-structural fill).

    - Legacy references to PETG must be updated to CF-PETG when found in the repository.  References to any other print material must be verified.
    - The prototype designed for printing on an DaVinci Jr isn't expected to be a fully functional or full size prototype, and won't meet these standards.

- The canonical exterior skin **shall be hollowed to 2.0 mm while maintaining a watertight mesh surface without any voids or holes**, except as explicitly specified in build. The mating surfaces between the four fuselage sections, (head, cargo, middle, rear), will be open to allow construction access.

- The shell will be filled with 2lb/cf low-density foam to provide internal structure.

- Bosses and ribs will be added to the interior of the shell as needed for mounting hardware, components, or other structural flight requirements.

- To the greatest extent possible, mounting brackets for avionics, servos, sensors, antennas, and other hardware shall be integrated and printed as part of the shell.

- All mating surfaces that carry load must have a minimum 2-wall contact annulus and a positive-stop shoulder. Friction fits alone are not acceptable for flight-critical joints.

- **All stls, openscad, and other 3D models shall be clean and have watertight surface meshes.**  They should be ready to slice for printing.  A mesh verification **shall** be run after every 3D model modification.  All findings shall be reported, added to the repository TODO.md, and resolved.

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

The Power Distribution Board is named "Kaylee" - "Everything is shiny."  Kaylee's room (the PDB bay) is located in the **inner neck of the middle section**, accessible through the open ventral face of the horseshoe ring.  This central location minimises power run lengths to all four nacelles, all four avionics stacks, and the battery.

The 49 MHz (Part 15 §15.235) + LoRa 915 MHz Transceiver Cape (XCVR-49MHZ-2 Rev R1) is named "Emma".  Emma connects to the stack via P1+P2 socket rails (replaces JST GH 6P as of Rev R1).  Only 2 Emma boards are installed: River's Room and Simon's Medbay.

The Cargo handling system is named "Jayne" - "I was aiming for his head."

The nose/cargo-bay Vision, ToF & Laser board is named "Vera" - Jayne's rifle, "she's a good gun."
Vera is a **standalone, compact PCB — not a PocketBeagle 2 Industrial cape** (it does not use
the P1+P2 header stack or plug onto a Wash/Zoë node); it connects to the rest of the airframe
only via the shielded JST-GH Ethernet ring and CAN-FD trunk connectors, with its own 5V power
input. One shared board design (TI AM62A vision SoC + TI MSPM0G3507 CAN-FD coprocessor +
Infineon SLB9670 TPM + Microchip KSZ9477 HSR/PRP-capable Ethernet switch) is installed at two
locations: the bow sensor pod (nose, `airframe/openscad/fuselage/bow_sensor_pod.scad`) and the
cargo bay nadir FPV mount (`cargo_fpv_bezel`).  Both locations share a **single 520 nm green
laser source + driver**, both **Class 2** (≤1 mW; a thin-line green crosshair detected by
Vera's camera via strobe + frame-difference — *not* an inherently Class 3B module). The
crosshair doubles as a **projected metrology reference** — a PB2-I derives detected-object size
and orientation from ToF range + the crosshair's known angle + trigonometry, so its fan angle
is sized for camera pixel coverage (cargo 3"×3" @ 5 ft; nose sized larger than the nominal
2"×2" @ 50 ft) — see `docs/VERA_LASER_ANALYSIS.md`, `avionics/CLAUDE.md` for the full architecture and
`REFERENCES.md` Part XII for component citations.  Vera **supersedes** the RunCam Nano 4 analog
camera (REF-SENSOR-001, retained in REFERENCES.md as a superseded citation) originally
specified for the bow sensor pod.

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

Shepherd is the crew's conscience and therefore takes care of primarily watchdog, fault detection, failover, and authentication. His stack has SiK primary and Wi-Fi secondary.

Inara has primarily camera, external sensors, and high bandwidth ground communication. Her stack is connected to Wi-Fi primarily and SiK/MAVLink secondary.  (LoRa is no longer on Inara's stack — LoRa moved to Emma boards on River and Simon; Rev R1.)

River provides primary control of the forward EDFs, and provides EDF and nacelle control command and syncing, and the most resilient comms. She may be crazy, but she comes through when no one else can. She has 49 MHz (Part 15 §15.235) primary and LoRa 915 MHz secondary — both via her Emma board (Rev R1).

Simon is the alternate watchdog for the ship, but most of his attention is on River. He's got aft EDF control and alternate nacelle control. He follows River's lead but makes sure she doesn't crash the ship. Simon also controls Jayne, and ensures that the cargo isn't jettisoned or the crew abandoned.
He's got 49 MHz (Part 15 §15.235) primary and SiK as his backup — both external radios co-resident on his Emma board (Rev R1 adds LoRa to Emma; Simon thus carries 49 MHz + LoRa + SiK via Cape-B-2).

## Workflow Notes

- **When adding a standards citation:** look up the standard in `REFERENCES.md` by REF-ID; if it is not yet in the catalog, add it to `REFERENCES.md` with a validated URL and the specific section cited, then use the REF-ID in the code or doc.
  Never invent or guess a section number — if the section cannot be verified, mark it as "requires verification" in `REFERENCES.md` and add a TODO §0.x item.

- Run Blender scripts with `blender --background --python <script>.py` — the machine supports headless execution.

- Output STLs go to `airframe/stls/` (subdirectories: `fuselage/`, `nacelles/`, `wings/`).
- When a script regenerates STLs, verify Z-range and bore-diameter in the console output before committing.
- **File-naming — `s_` prefix dropped (Rev R1).**  The legacy `s_` prefix on shell/STL/SCAD
  basenames (e.g. `s_cargo_sect_shell24_2mm_repaired.stl`) was dropped to simplify naming.
  The only place the prefixed names survive is deep in `airframe/archive/`.  All active
  references shall use the unprefixed name (e.g. `cargo_sect_shell24_2mm_repaired.stl`); when
  a stale `s_`-prefixed reference is encountered in active code or docs, drop the prefix and
  correct the string in place as part of whatever task touches it (do not open a dedicated
  hunt for them).

- Any time that an assistant creates a todo list to accomplish a task for the build, the steps shall be added as sup-tasks in the appropriate paragraph of the root repository TODO.md wbs, conforming to proper style, so that unresolved issues can be picked up in future sessons.

- The AI assistant shall update PROJECT_INDEX.md, which lists the directory structure and all folders and files in the active project, whenever new active files are added to the repository.  When filess are archived, their names shall be moved from PROJECT_INDEX.md to ARCHIVE_INDEX.md, which describes the file tree of the archive.

- From time to time, when editing documentation, the AI assistant should add a tasteful Firefly/Serenity quote or reference as a small easter egg (in the style already present in `docs/PHASED_BUILD_GUIDE.md` and the `TODO.md` footer). Keep them sparse, relevant to the surrounding content, and never in place of required technical content.
