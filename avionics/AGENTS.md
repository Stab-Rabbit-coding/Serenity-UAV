# Avionics Design — Agent Instructions

> *See the root `AGENTS.md` for project-wide policies. This file provides specific guidance for avionics design, KiCad PCBs, capes, and microcontroller configuration.*

## Scope

This folder contains all electronics design and implementation: KiCad schematics and PCB layouts for avionics capes, microcontroller firmware, boot loaders, TPM configurations, and communications stack documentation. The avionics architecture is built on redundancy and failover across eight industrial SBCs distributed throughout the airframe.

## Onboard Avionics Architecture — 8-Node Cooperative System

Root `AGENTS.md` §1 owns the node roster, the onboard bus list, and the external C2 channel
list (including S-Bus status); root §9 "Naming and Roles" owns the bay/role naming table and
the PACE assignment table. Read them there — this file carries only the electrical and
board-level detail, plus the band-by-band FCC citations under "External Communications
Regulations Compliance" below.

**Platform:** four pairs of **PocketBeagle2 Industrial SBCs** (8 nodes total, Rev S placement,
established at Rev R1). Every node carries a **TPM** (Trusted Platform Module) for cryptographic
operations in addition to its Pilot and XO capes.

**Bus isolation:** CAN FD, RS-485, and Ethernet are galvanically isolated at every node through
Cape-A-2 and Cape-B-2. MIL-STD 1553 is legacy and is being phased out.

**Commo transceiver cape** (49 MHz Part 15 §15.235 + LoRa 915 MHz): installed in **River's
Room** (Bay C, starboard cargo) and **Simon's Medbay** (Bay D, middle section) only — see "Cape
Naming and Revision History" below for current build status.

**Power Distribution — Flight Engineer (PDB):** central location in the inner neck of the middle
section, minimizing power-run lengths to all four nacelles, all four avionics stacks, and the
battery; interfaces with all four flight-control nodes for EDF and servo control.

### Node Workload Balancing and PACE Failover

All Pilot capes are identical and all XO capes are identical, but each stack has **primary and
alternative tasking** with PACE prioritization (**P**rimary, **A**lternative, **C**ontingency,
**E**mergency). The per-stack PACE assignment, primary tasking, and radio priority are in root
`AGENTS.md` §9 "Naming and Roles" — read that table, do not copy it here. Board-level facts it
does not carry:

- River's Room (Bay C) and Simon's Medbay (Bay D) run **Pilot + XO + Commo**; Shepherd's Room
  (Bay A) and Inara's Shuttle (Bay B) run Pilot + XO only.
- LoRa is migrating from XO to Commo on the River and Simon stacks — see "Cape Naming and
  Revision History" below for current build status.
- The Inara stack's secondary link is LoRa in the current build but SiK-MAVLink in root §9.
  That discrepancy is unreconciled: per root §11 item 2, **stop and get user adjudication**
  before relying on either.

## Cape Naming and Revision History

Board architecture, sch↔pcb parity status, and reconciliation progress change frequently and
are tracked at the source, not duplicated here. **For any board, the authoritative,
most-current status is that board's own `.md` file** under `avionics/kicad/<board>/` (e.g.
`Pilot.md`, `XO.md`, `Commo.md`, `FlightEngineer.md`, `Observer.md`) plus the matching `TODO.md` §1.2
subsection — read those before starting work, and do not assume this file's stable-fact
summary below reflects today's as-built state.

### Pilot — Flight Control and Sensor Cape

Flight control input, sensor fusion, and PID motor speed control: GPS, IMU, compass,
barometer, anti-collision range sensors, airspeed sensor, EDF PID control, nacelle tilt servo
control. Current build designation: Cape-A-2. Status/history: `avionics/kicad/Pilot/Pilot.md`.

### XO — Communications, Logging, and Payload Cape

External communications, onboard logging, payload interface: all four external radio
transceivers, onboard data logging to hardware-enforced non-executable microSD, payload I/O.
Current build designation: Cape-B-2. Status/history: `avionics/kicad/XO/XO.md`, TODO.md
§1.2b.

### Commo — 49 MHz + LoRa Transceiver Cape

Unlicensed-band communications for high-RF-field environments: 49 MHz transceiver (47 CFR
Part 15 §15.235) plus LoRa 915 MHz, both galvanically isolated. Installed only in River's Room
(Bay C) and Simon's Medbay (Bay D). Connects via P1+P2 socket rails (Rev R1; replaces the
legacy JST GH 6P). Status/history: `avionics/kicad/Commo/Commo.md`, TODO.md §1.2b.

### Observer — Cargo-Handling System and Nose/Cargo-Bay Vision, ToF & Laser Board

One integrated subsystem covering both the mechanical cargo-handling hardware (winch, latch,
cargo bay door) and the vision/ToF/laser sensing board. Historical references to "Vera" (an
earlier working name for the sensing board) refer to this same board.

**Observer is a standalone PCB — not a PocketBeagle 2 Industrial cape.** It does not use the
P1+P2 header stack and does not mount on a Pilot/XO node; it connects to the rest of the
airframe only via the shielded JST-GH Ethernet ring and CAN-FD trunk connectors, with its own
5V power input. One shared board design is installed at two physical locations: the bow
sensor pod (nose) and the cargo bay nadir FPV mount, the latter co-located with the mechanical
cargo-handling hardware it supervises. It supersedes the RunCam Nano 4 analog camera
(REF-SENSOR-001, superseded).

**Do not restate Observer's chip-level architecture, EMI hardening, or fabrication status here —
it has changed materially between doc passes and this section has gone stale before.**
Canonical source: `avionics/kicad/Observer/Observer.md`, TODO.md §1.2c (hardware) and §4.6
(firmware).

**Laser indicator:** single shared 520 nm green source; per-site optics and IEC 60825-1
class are a live engineering analysis, not a fixed spec — canonical source:
`docs/OBSERVER_LASER_ANALYSIS.md` (current revision), TODO.md §1.2c.4.

### Flight Engineer — Power Distribution Board (PDB)

Battery management, EDF power distribution, and PID control-line routing to all
flight-control nodes. Location: inner neck of the middle section (Flight Engineer's room), adjacent to
Simon's Medbay — minimizes power-run length to all nacelles, all four stacks, and the battery.
Status/history (including the planned 6V-servo-BEC removal): `avionics/kicad/FlightEngineer/FlightEngineer.md`,
TODO.md §1.2b.

## PCB Design Standards

### Design Rules Checker (DRC) Workflow

Every schematic and PCB modification **must** be verified: run **ERC** on the `.kicad_sch` and
resolve all violations and warnings, then run **DRC** on the `.kicad_pcb` and resolve all
violations and errors. Document anything that cannot be resolved in `TODO.md` with the specific
DRC rule and reason; commit only after every violation is resolved or documented. All routing
and component spacing will maintain 0.3mm minimum copper spacing (as enforced by the
min_copper_edge_clearance DRC check) per [REF-IPC-001]. Root `AGENTS.md` §7 states the
production-completeness bar for every cape (schematic, PCB layout, copper traces, correct IC
footprints, production-ready Gerbers).

### Footprint and Component Placement

**Critical note:** PCBs are tightly packed. All final component footprint positions will be
placed manually after PCBs are populated and nets are built by script (root `AGENTS.md` §5).

- If a DRC violation requires repositioning a component footprint, **refer the action to the user**
- Other modifications (net routing, trace widening, via placement) are allowed without user confirmation

## Security and Cryptography Requirements

Every message, internal and external, must be **digitally signed** and authenticated,
**logged** for forensic analysis, and **timestamped** by the TPM.

- **TPM:** every node carries one; all keys are generated and stored on the TPM, never in
  software; all messages are signed using TPM-held keys.
- **Data logging:** everything is logged — sensor data, CAN messages, MAVLink commands, camera
  feed, authentication events — to **hardware-enforced non-executable microSD cards**
  (write-once, never executable). All logs are signed and timestamped.

### Zero Trust Architecture Compliance

All avionics design shall comply with **NIST SP 800-207 Zero Trust Architecture** [REF-NIST-001 §2.1, §2.2, §3.3]:

- Assume breach: expect both external and internal attacks
- Verify every transaction: no implicit trust based on network location
- Authenticate every message and every node state change
- Least privilege: each node operates with minimum required permissions
- Micro-segmentation: isolate avionics bays with galvanic isolation and message authentication

## External Communications Regulations Compliance

All radio transmissions must comply with **FCC regulations**:

- **49 MHz band:** 47 CFR Part 15 §15.235 (unlicensed ISM, not Part 95 RCRS) — used for high-RF-field environments
- **915 MHz SiK/MAVLink:** 47 CFR Part 15 §15.247 (900 MHz unlicensed ISM band)
- **2.4 GHz Zigbee:** 47 CFR Part 15 §15.247 (unlicensed ISM)
- **5 GHz Wi-Fi:** 47 CFR Part 15 §15.407 (unlicensed UNII)

Citations: [REF-FCC-001, REF-FCC-002, REF-FCC-003]

## Work Tracking and Documentation

When modifying or creating cape designs:

1. Update the relevant `.kicad_sch` and `.kicad_pcb` files
2. Run ERC and DRC; document any violations in `TODO.md` with the reason
3. Update the cape description in `REFERENCES.md` if the design scope has changed
4. If planning a new cape revision, record it in `TODO.md` and cite this file
5. Archive old cape revisions in `archives/`; index and archive upkeep (`PROJECT_INDEX.md`,
   `ARCHIVE_INDEX.md`) follows root `AGENTS.md` §10
6. Check for component datasheets in the `avionics/datasheets` folder, kicad symbols in the `avionics/kicad/symbols` folder, and footprints in the `avionics/kicad/symbols/footprints` folder before searching online
7. Use OEM Datasheets as authitative component references.
