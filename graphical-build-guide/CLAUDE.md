# Graphical Build Guide — Claude Code Project Instructions

> *See the root `CLAUDE.md` for project-wide policies. This file provides specific guidance for the phased build process and fabrication documentation.*

## Scope

This folder contains illustrated build guides, assembly sequences, fabrication checklists, and troubleshooting documentation for constructing a Serenity-UAV. The guides are organized by build phase and provide step-by-step instructions with graphics, material lists, and verification checkpoints.

## Phased Build Approach

Serenity-UAV is constructed in sequential **phases**, each adding specific capabilities while maintaining the ability to test and verify previous phases. This approach allows:
- Early detection of integration problems
- Incremental verification of avionics and flight control
- Parallel work on future phases while earlier phases are in flight testing
- Clear handoff points for documentation and team coordination

### Phases Overview

| Phase | What's Built | Goal | T/W | Status |
| --- | --- | --- | --- | --- |
| **1–4** | Fuselage, landing gear, wing attachment | Physical airframe | — | Archived/prototype |
| **5–10** | Avionics (4 stacks), nacelles, battery, power dist | Full VTOL hover | 1.61 | **Current** |
| **11+** | Rear EDF + RCS, autonomous mission system | Cruise + hover | 1.43 | Deferred |

### Current Build Phase (5–10)

**Current capability:** Full vertical-takeoff-and-landing (VTOL) hover with two nacelles per pylon, networked avionics, autonomous command and control, redundant communications, and full secure logging.

**Excluded from current phase:**
- Rear fuselage EDF (thrust-vectoring horizontal propulsion)
- RCS (reaction-control) thrusters (attitude control)
- Aft EDF intake scoops into the middle-section inner neck
- Advanced autonomous maneuvers requiring forward propulsion

## Build Guide Structure

Each phase build guide shall include:

### Phase Introduction
- **Objective:** What capability is added in this phase
- **Duration estimate:** Expected build time
- **Tools required:** Special fixtures, instruments, or safety equipment
- **Required materials:** Filament types, fastener specifications, electrical components
- **Prerequisites:** Which earlier phases must be complete

### Step-by-Step Instructions

Each step shall include:
1. **Step number and title** (e.g., "Step 5.2: Print Cargo Section Shell")
2. **Objective:** What is being accomplished
3. **Materials and tools** needed for this step
4. **Instructions:** Detailed, sequential procedure
5. **Illustrations:** Photos, diagrams, or CAD screenshots showing correct assembly
6. **Verification checkpoint:** How to confirm the step was done correctly
7. **Common mistakes:** Pitfalls to avoid
8. **Troubleshooting:** What to do if something goes wrong

### Material Lists

For each phase, provide a comprehensive bill of materials (BOM):
- Component name (part number, source, alternative suppliers)
- Quantity required
- Fastener specifications (size, grade, material)
- Filament type and color
- Electrical components (voltage rating, capacity, connector type)
- Unit cost estimate

### Fabrication Standards Reference

Reference the fabrication standards from the root `CLAUDE.md`:
- **CF-PETG print parameters:** 0.15 mm layers, 4 perimeters, ≥40% infill (load-bearing)
- **Shell wall thickness:** 2.0 mm hollow with 2 lb/ft³ foam fill
- **Fastener standards:** Grade specifications, torque values
- **Joint preparation:** Cleaning, fitting verification before assembly

### Assembly Verification Checklist

After completing a phase section, verify:
- [ ] All parts are printed and validated (mesh check)
- [ ] All fasteners are present and correct grade
- [ ] All glue/epoxy joints are fully cured
- [ ] Electrical connectors are properly seated
- [ ] Cable routing does not pinch or restrict movement
- [ ] All structural joints meet the 2-wall contact + positive-stop requirement
- [ ] Mass budget is within specification
- [ ] Center of gravity is within design envelope

### Test and Verification Steps

Each phase includes specific tests to verify the build is correct:
- **Structural:** Load testing (if applicable), no-load fit check
- **Electrical:** Continuity testing, polarity check, no short circuits
- **Mechanical:** Servo range of motion, landing gear shock response
- **Software:** System boot, node-to-node CAN communication, node-to-ground Wi-Fi

## Illustrations and Graphics

### Acceptable Formats

- **CAD screenshots:** FreeCAD or Blender rendered views showing part placement
- **Assembly photos:** High-resolution images of completed subassemblies
- **Exploded diagrams:** 3D renderings showing how parts fit together
- **Wiring diagrams:** Schematic or labeled photos of electrical connections
- **Dimension drawings:** Technical drawings with key measurements

### Graphics Guidelines

- Use clear, well-lit photographs (outdoor natural light preferred)
- Include a **reference object** (ruler, coin, or part with known size) for scale
- Label key features and critical dimensions
- Add arrows and annotations to highlight assembly sequence or proper orientation
- Ensure text is readable (minimum 10-point font)
- Provide both overview and detail views for complex assemblies

## Troubleshooting Guides

### Common Print Issues

For each fabrication method, provide solutions for:
- **Layer adhesion problems:** Under-extrusion, nozzle too high, bed temperature issues
- **Supports and stringing:** Over-hanging geometry, stringing between parts
- **Dimensional accuracy:** Holes too small, parts warping, scaling issues

### Assembly Problems

- **Parts don't fit:** Dimensional mismatch, orientation error, burrs on printed parts
- **Electrical shorts:** Wrong wire gauge, exposed conductor, wet components
- **Structural weakness:** Gaps in joints, insufficient infill, fasteners too tight/loose

### Flight Test Issues

- **Avionics failure to boot:** Power distribution, SD card not present, corrupted firmware
- **Communication loss:** Wrong radio frequency, antenna damage, RF interference
- **Control instability:** CG out of range, ESC tuning, PID controller divergence

## Phase Completion Sign-Off

Each phase build guide includes a **completion checklist** that must be verified before proceeding to the next phase:

**Phase 5–10 Completion Sign-Off:**
- [ ] All four fuselage sections printed, validated, and assembled
- [ ] Landing gear installed and load-tested
- [ ] Wings and nacelles attached and balanced
- [ ] All four avionics stacks populated and tested (CAN communication verified)
- [ ] Battery and power distribution installed and voltage-verified
- [ ] Radio links tested (Wi-Fi, SiK/MAVLink, optional 49 MHz, optional Zigbee)
- [ ] Sensors functional (IMU, GPS, compass, airspeed)
- [ ] Motor controllers programmed and motor spin test completed (props removed)
- [ ] Servo tests completed (nacelle tilt, cargo bay, hoist)
- [ ] SD card formatted and logged test flights recorded
- [ ] System security: TPM enrollment, key generation, operator certificates installed
- [ ] Ground station (Malcolm) communication verified
- [ ] First hover test completed and stable

## Work Tracking and Documentation

When creating or updating a build guide phase:

1. Test the procedure yourself or with a technical reviewer (no untested instructions)
2. Include all necessary figures and dimensions in the guide
3. If standards citations are needed (e.g., fastener grades), use REF-IDs from `REFERENCES.md`
4. Add the guide to `PROJECT_INDEX.md`
5. If the guide references deferred work, link to `TODO.md` items
6. Archive superseded build guides (older phasing, obsolete components) to `archives/`

---

For project-wide standards, see the root `CLAUDE.md`.
