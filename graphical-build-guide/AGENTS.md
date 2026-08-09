# Graphical Build Guide — Agent Instructions

> *See the root `AGENTS.md` for project-wide policies. This file provides specific guidance for the phased build process and fabrication documentation.*

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

**Excluded from the current phase** — the rear fuselage EDF, the RCS thrusters, the aft EDF
intake scoops into the middle-section inner neck, and advanced autonomous maneuvers requiring
forward propulsion. Those are described in `deferred/AGENTS.md` "Phase 11"; do not restate them
here.

## Build Guide Structure and Checklists

**`graphical-build-guide/BUILD_GUIDE_TEMPLATE.md`** is the authoritative template for every
phase guide: the phase-introduction fields, the eight-part step format, the material-list/BOM
template, the fabrication-standards reference block, the assembly-verification checklist, the
per-phase test and verification steps, the troubleshooting catalog (print issues, assembly
problems, flight-test issues), and the Phase 5–10 completion sign-off checklist. Follow it
whenever you author or revise a phase guide in this folder.

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

## Work Tracking and Documentation

When creating or updating a build guide phase:

1. Test the procedure yourself or with a technical reviewer (no untested instructions)
2. Include all necessary figures and dimensions in the guide
3. If standards citations are needed (e.g., fastener grades), use REF-IDs from `REFERENCES.md`
4. If the guide references deferred work, link to `TODO.md` items
5. Archive superseded build guides (older phasing, obsolete components) to `archives/`; index
   and archive upkeep (`PROJECT_INDEX.md`, `ARCHIVE_INDEX.md`) follows root `AGENTS.md` §10
