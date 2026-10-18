# Serenity UAV — Documentation Index

**Author:** Steve Griffing, PE(CSE) [Control Systems Engineering], CISSP-ISSEP, CPP  
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)  
**Current design revision:** Rev T (2026-09-06, see `WBS.md` §6.4 for the changelog)  
**Last updated:** 2026-10-07

> **Rev T baseline:** 24-inch CF-PETG hull, 8-node cooperative avionics (Pilot + TACCO on every
> PB2-I), fixed CF wing spar (Rev S1g) with a worm-driven tilt actuator, 50 mm tandem EDF nacelles
> (Rev S4c) with a 64 mm redesign in progress, servo-driven variable nozzles, a cargo bay with
> SPT5425LV/LibreServo winch, and a standalone Commo node (Rev T, approved 2026-09-29). The
> aircraft is in design and PCB layout; nothing is assembled. This file indexes the design
> documents, analyses, and build guides.

## Quick Navigation

- **[Root README.md](../README.md)** — project overview, mission profile, architecture
- **[AGENTS.md](../AGENTS.md)** — authoritative project policy (standards, coding, fabrication,
  licensing, attribution)
- **[REFERENCES.md](../REFERENCES.md)** — master citation catalog (standards, regulations,
  suppliers, datasheets)
- **[WBS.md](./WBS.md)**, **[TODO.md](./TODO.md)**, **[WBS_FEDERATION.md](./WBS_FEDERATION.md)** —
  documentation work record, open items, and the inventory of every federated WBS/TODO pair
- **[FIRST_FLIGHT_READINESS.md](./FIRST_FLIGHT_READINESS.md)** — ordered path to first flight,
  rolled up from the live WBS federation
- **[PHASED_BUILD_GUIDE.md](./PHASED_BUILD_GUIDE.md)** — Rev S phases 0–10 assembly steps (not yet
  updated for Rev T geometry; tracked in `WBS.md` §1.5)
- **[REVN_BUILD_GUIDE_24IN.md](./REVN_BUILD_GUIDE_24IN.md)** — Phase 1–4 guidance for the 24-inch
  hull structure
- **[DOC_TEMPLATES.md](./DOC_TEMPLATES.md)** — required content templates for specifications,
  analyses, and compliance records

## Design Documentation by Domain

### Airframe and Structures

- **[airframe/README.md](../airframe/README.md)** — fuselage, wings, nacelles, landing gear
- **[airframe/AGENTS.md](../airframe/AGENTS.md)** — CAD standards, STL generation, printing specs
- **[TILT_SPAR_ANALYSIS.md](./TILT_SPAR_ANALYSIS.md)** — spar material selection and stress
  analysis
- **[TILT_ACTUATOR_SELECTION.md](./TILT_ACTUATOR_SELECTION.md)**,
  **[TILT_ACTUATOR_OPTIONS.md](./TILT_ACTUATOR_OPTIONS.md)**,
  **[TILT_DRIVE_CONTROL_SPEC.md](./TILT_DRIVE_CONTROL_SPEC.md)**,
  **[TILT_ENCODER_WIRING_EMI_SPEC.md](./TILT_ENCODER_WIRING_EMI_SPEC.md)** — tilt drive selection,
  control, and encoder wiring
- **[WING_ATTACH_INTERFACE.md](./WING_ATTACH_INTERFACE.md)** — wing-to-fuselage joint (Rev S1g)
- **[NOZZLE_DRIVE_TRADE.md](./NOZZLE_DRIVE_TRADE.md)** — nacelle nozzle drive trade and the
  2026-09-28 servo-drive decision
- **[NACELLE_64MM_VERIFICATION.md](./NACELLE_64MM_VERIFICATION.md)**,
  **[HULL_SCALE_36IN_EDF64MM_EVALUATION.md](./HULL_SCALE_36IN_EDF64MM_EVALUATION.md)** — 64 mm EDF
  nacelle verification and the hull-scale evaluation
- **[LANDING_GEAR_ANALYSIS.md](./LANDING_GEAR_ANALYSIS.md)** — wire schedule, drop-height
  testing, fail-safe design
- **[CARGO_SECTION_LAYOUT.md](./CARGO_SECTION_LAYOUT.md)**,
  **[CARGO_WINCH_SPECIFICATION.md](./CARGO_WINCH_SPECIFICATION.md)**,
  **[CARGO_DOOR_LATCH_SPEC.md](./CARGO_DOOR_LATCH_SPEC.md)**,
  **[CARGO_DOOR_GATEWAY_SPEC.md](./CARGO_DOOR_GATEWAY_SPEC.md)** — cargo bay layout, winch, door
  latch, and door gateway
- **[BATTERY_MOUNT.md](./BATTERY_MOUNT.md)**, **[POWER_DISTRIBUTION.md](./POWER_DISTRIBUTION.md)**,
  **[electrical_fault_margins.md](./electrical_fault_margins.md)** — battery mount, power
  distribution, and fault margins
- **[structural_analysis.md](./structural_analysis.md)**,
  **[MASS_AUDIT_CARGO_WING_ROOT.md](./MASS_AUDIT_CARGO_WING_ROOT.md)**,
  **[flight_envelope.md](./flight_envelope.md)**,
  **[failsafe_thresholds.md](./failsafe_thresholds.md)** — structural, mass, envelope, and
  failsafe analyses

### Avionics and Electronics

- **[avionics/README.md](../avionics/README.md)** — 8-node PACE failover, PCB boards, firmware
- **[avionics/AGENTS.md](../avionics/AGENTS.md)** — PCB design standards, security, EMI hardening
- **[avionics/kicad/README.md](../avionics/kicad/README.md)** — board index and status snapshot
- **[Pilot.md](../avionics/kicad/Pilot/Pilot.md)** — flight control and sensor cape
- **[TACCO.md](../avionics/kicad/TACCO/TACCO.md)** — comms, logging, and payload cape
- **[FlightEngineer.md](../avionics/kicad/FlightEngineer/FlightEngineer.md)** — power
  distribution board
- **[Commo.md](../avionics/kicad/Commo/Commo.md)** — 49 MHz + SiK transceiver (Rev S cape history
  and the Rev T standalone node)
- **[Observer.md](../avionics/kicad/Observer/Observer.md)** — vision, ToF, and laser board
- **[CAN-PERIPH-GW-1.md](../avionics/kicad/Bus-Gateway/CAN-PERIPH-GW-1.md)** — secure CAN-FD /
  RS-485 edge node
- **[ENC-NACELLE-1.md](../avionics/kicad/Encoder/ENC-NACELLE-1.md)** — nacelle tilt encoder
- **[AVIONICS_PB2_REDESIGN.md](./AVIONICS_PB2_REDESIGN.md)**,
  **[ETHERNET_PHY_TRADE.md](./ETHERNET_PHY_TRADE.md)** — PB2 avionics redesign and Ethernet PHY trade
- **[OBSERVER_LASER_ANALYSIS.md](./OBSERVER_LASER_ANALYSIS.md)**,
  **[OBSERVER_MANUFACTURING_READINESS.md](./OBSERVER_MANUFACTURING_READINESS.md)** — Observer
  laser class and safety, and manufacturing readiness

### Ground Control Station

- **[gcs/README.md](../gcs/README.md)** — Skipper hardware, multi-radio comms, antenna gimbal
- **[gcs/AGENTS.md](../gcs/AGENTS.md)** — GCS firmware, QGroundControl integration, tracking

### Build Tools and Automation

- **[tools/README.md](../tools/README.md)** — validation scripts (STL mesh, KiCad ERC/DRC), CI
  pipeline, design automation
- **[tools/AGENTS.md](../tools/AGENTS.md)** — build tool specifications and usage

### Bill of Materials and Procurement

- **[current-specification/README.md](../current-specification/README.md)** — Rev T BOM, parts
  list, revision history
- **[bom_revT.json](../current-specification/bom_revT.json)** — structured Rev T BOM (suppliers,
  mass, cost)
- **[bom_revT.csv](../current-specification/bom_revT.csv)** — flat BOM for spreadsheet import

### Plans, Solutions, and Prototypes

- **`plans/`** — dated implementation plans (for example the Commo Rev T and fleet 1553C plans)
- **`solutions/`** — documented solutions to past problems, by category (conventions, design
  patterns, logic errors, runtime errors, workflow issues)
- **[PROTO_PRINT_DAVINCI_JR.md](./PROTO_PRINT_DAVINCI_JR.md)** — DaVinci Jr prototype print notes
- **`references/`** — vendor and canonical reference captures (excluded from linting)

## Regulatory and Compliance

- **[attribution_and_licensing.md](./attribution_and_licensing.md)** — licensing strategy
  (CERN-OHL-W 2.0 hardware, MIT software, CC BY-SA 4.0 documents) and attribution chains
- **[OSHW_CERTIFICATION.md](./OSHW_CERTIFICATION.md)** — open-source hardware certification
  tracking
- **Regulatory checklist** (open; items in `WBS.md` §1.5):
  - FAA Part 48 (sUAS registration) [REF-FAA-001]
  - FAA Part 107 (remote pilot certificate) [REF-FAA-002]
  - FCC Part 15 §15.235 (49 MHz unlicensed) [REF-FCC-003]
  - IEC 62368-1 (safety, creepage and clearance) [REF-IEC-001]
  - ASTM F2910-22 (sUAS design and construction) [REF-ASTM-001]

## Revision History

| Rev | Hull | Nacelle EDFs | Avionics | Build status |
|-----|------|--------------|----------|--------------|
| T | 24 in (610 mm) | 50 mm X-Fly tandem (Rev S4c); 64 mm redesign in progress | 8-node Pilot + TACCO, Flight Engineer, standalone Commo (Rev T), Observer | Current baseline; design and PCB layout |
| S | 24 in | 50 mm X-Fly tandem | 8-node Pilot + TACCO, Flight Engineer, Commo cape, Observer (Rev S1) | Superseded by Rev T (`WBS.md` §6.3) |
| R1 | 24 in | 50 mm X-Fly tandem | 8-node (pre-S1), hull-frame baking | Design complete (`git log`) |
| R | 24 in | 50 mm X-Fly tandem | 8-node, first 24 in iteration | Archived |
| Q | 24 in | 50 mm X-Fly tandem | 8-node architecture finalized | Archived |
| P | 18 in (457 mm) | 80 mm Changesun 2700 KV | 4-node prototype | Archived |
| M and earlier | 18 in | Various | 2–4 node prototypes | Archived |

**Note:** Rev M (18 in, dual 80 mm EDFs) and earlier are not the current design baseline. All
new work targets Rev T. The former Rev M quick-spec and attribution tables that followed this
index moved to `archives/docs-superseded/docs-README-revM-tail-2026-10-07.md`; the current
attribution record is [attribution_and_licensing.md](./attribution_and_licensing.md).
