# Avionics Design — Agent Instructions

Adds avionics-specific rules to root `AGENTS.md`, which wins wherever it speaks. Scope: KiCad
schematics and PCBs, capes and nodes, firmware, boot loaders, TPM/SE configuration, and the
communications stack.

## Architecture (routing)

Root `AGENTS.md` §1 owns the node roster (seven PB2-I compute nodes), buses, and external C2
channels; `avionics/PACE.md` owns the PACE matrix and per-stack tasking (root §9 gates changes).
Terms (node, cape, stack, bay): `CONCEPTS.md`.

Board-level rules not stated in root:

- **Boards in the fuselage air path lie in line with the flow, never as an air dam,** and the stream keeps 12.4 in² (8,000 mm²) at every bay station: `airframe/AGENTS.md` "Interior Air Path" owns both rules. Outline and mounting choices (on edge, trapezoids, split boards) follow from them.
- **Bus isolation:** every bus terminal on every PCB (Pilot, TACCO, Commo, Observer, Flight
  Engineer, Bus-Gateway) is galvanically isolated, for CAN FD, RS-485, Ethernet, and
  MIL-STD-1553C alike. CAN FD and RS-485 reach every PCB, actuator, and sensor; Observer
  also has Ethernet. 1553C does not extend to non-SBC nodes, with one exception: Commo is a
  1553C remote terminal (no Ethernet).
- **Security element:** every PB2-I cape (Pilot, TACCO) carries a TPM; every other PCB
  (Commo, Observer, Flight Engineer, Bus-Gateway) carries an SE.
- Loss of the single Commo node is an accepted single point of failure for 49 MHz and SiK;
  TACCO's mLRS is the long-range fallback.

## Boards

Each board's own `.md` under `avionics/kicad/<board>/` is authoritative for architecture,
location, sch↔pcb parity, and status. Read it, and its `avionics/WBS.md` section, before work.

| Board | Function | Authoritative file |
| --- | --- | --- |
| Pilot (cape) | Flight control, sensor fusion, EDF PID, nacelle tilt servo control | `kicad/Pilot/Pilot.md` |
| NoNFO-Pilot-PB2 | Simon's single-board stern stack (`avionics/WBS.md` §1.11) | `kicad/NoNFO-Pilot-PB2/` |
| TACCO (cape) | Wi-Fi, ZigBee, mLRS; non-executable microSD logging; payload I/O | `kicad/TACCO/TACCO.md` |
| Commo (node) | 49 MHz Part 15 §15.235 + SiK 915 MHz; standalone, MCU-driven, at the antennas | `kicad/Commo/Commo.md` |
| Observer (board) | Cargo handling (winch, latch) + bow and cargo-bay vision/ToF/laser | `kicad/Observer/Observer.md` |
| Flight Engineer (PDB) | Battery management, EDF power distribution, PID control-line routing | `kicad/FlightEngineer/FlightEngineer.md` |
| Bus-Gateway (`CAN-PERIPH-GW-1`) | Secure CAN FD/RS-485 edge for tilt Hall sensors, servos, RCS valves, ESC telemetry | `kicad/Bus-Gateway/CAN-PERIPH-GW-1.md` |

Commo, Observer, and Bus-Gateway are standalone PCBs, not PB2-I capes. Observer's laser specs:
`docs/OBSERVER_LASER_ANALYSIS.md`. Superseded designs are in `archives/avionics-archives.tar.gz`.

## PCB Design Rules

- **Part selection:** root `AGENTS.md` §5 gate (`docs/SOURCING_POLICY.md`) before any part
  enters a schematic.
- **Coordinates:** a board keeps KiCad coordinates only while designed in KiCad; every PCB STEP
  or STL used for fitting is exported or placed in the aircraft datum at its installed position.
- **ERC/DRC:** root `AGENTS.md` §7 gate. Resolve every ERC violation and warning and every DRC
  violation and error, or record it (rule + reason) per root §7.
- **Clearance floors** (500 W/m² EMI objective, REF-NIST-002 §6.2.5; values per REF-IPC-001,
  IPC-2221B §3–4.2; never cite REF-IPC-002 for them):
    - copper-to-edge (`min_copper_edge_clearance`): 0.012 in (0.3 mm), all boards;
    - copper-to-copper (every netclass `clearance` and the board-wide `rules.clearance` /
      `rules.min_clearance`): 0.012 in (0.3 mm), applied to each board the next time it is
      touched.
- **Fine-pitch exception** (REF-IPC-003, IPC-7351): a ≤0.020 in (0.5 mm) pitch QFN/QFP's
  nominal land pattern can place different-net pads 0.008–0.012 in (0.20–0.30 mm) apart. Do
  not lower the clearance floor and do not edit pad geometry. Record the footprint reference,
  pitch, and measured gaps in the board's `.md` citing REF-IPC-003 + REF-IPC-002 (pattern:
  `CAN-PERIPH-GW-1.md` "DRC"), and exclude those violations in the KiCad GUI (Board Setup →
  DRC → right-click → "Exclude this violation"); kicad-cli cannot author exclusions.
- Justify each deviation in the affected board's `.md`.
- **Placement:** root §5 — refer any footprint move to the user; route, widen traces, and
  place vias without confirmation.
- Check `avionics/datasheets/`, `avionics/kicad/symbols/`, and
  `avionics/kicad/symbols/footprints/` before searching online; OEM datasheets are
  authoritative.

## Security and Cryptography

- Every message is signed with keys generated and held in the TPM/SE (never in software),
  authenticated, timestamped, and logged.
- Log everything (sensor data, CAN messages, MAVLink commands, camera feed, authentication
  events) to hardware-enforced non-executable microSD; logs are signed and timestamped.
- NIST SP 800-207 [REF-NIST-001 §2.1, §2.2, §3.3]: assume breach; verify every transaction with
  no implicit trust by network location; authenticate every message and node state change;
  least privilege; every node, down to a Hall sensor or microservo, is a microsegment
  authenticated at startup and throughout the mission.

## External Communications Regulations Compliance

All radio transmissions shall comply with FCC rules [REF-FCC-001, REF-FCC-002, REF-FCC-003]:

- **49 MHz:** 47 CFR Part 15 §15.235 (unlicensed; not Part 95 RCRS)
- **915 MHz SiK/MAVLink:** 47 CFR Part 15 §15.247
- **2.4 GHz ZigBee:** 47 CFR Part 15 §15.247
- **5 GHz Wi-Fi:** 47 CFR Part 15 §15.407 (U-NII)

## Work Tracking

Record a new board revision, an unresolved violation, or other open work in `avionics/WBS.md`
(root §10 federation). Archive old board revisions under `archives/`.
