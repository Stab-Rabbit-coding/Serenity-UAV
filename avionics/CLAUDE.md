# Avionics Design — Claude Code Project Instructions

> *See the root `CLAUDE.md` for project-wide policies. This file provides specific guidance for avionics design, KiCad PCBs, capes, and microcontroller configuration.*

## Scope

This folder contains all electronics design and implementation: KiCad schematics and PCB layouts for avionics capes, microcontroller firmware, boot loaders, TPM configurations, and communications stack documentation. The avionics architecture is built on redundancy and failover across eight industrial SBCs distributed throughout the airframe.

## Onboard Avionics Architecture — 8-Node Cooperative System

**Platform:** Four pairs of **PocketBeagle2 Industrial SBCs** (8 nodes total, Rev R1 placement):
- All 8 nodes carry **Wash** (Flight Control and Sensor Cape) and **Zoë** (Communications, Logging, and Payload Cape)
- All 8 nodes carry **TPM** (Trusted Platform Module) for cryptographic operations

**Emma Transceiver Cape** (49 MHz Part 15 §15.235 + LoRa 915 MHz):
- Installed in **River's Room** (Bay C, starboard cargo) and **Simon's Medbay** (Bay D, middle section) only
- Emma Rev R1: adds LoRa, replaces JST GH 6P with P1+P2 socket rails
- Connects via P1+P2 socket rails on Wash and Zoë (as of Rev R1)

**Power Distribution — Kaylee (PDB):**
- Central location: inner neck of middle section, minimizes power run lengths to all four nacelles, all four avionics stacks, and the battery
- Interfaces with all four flight-control nodes for EDF and servo control

### Node Workload Balancing and PACE Failover

All Wash capes are identical and all Zoë capes are identical, but each stack has **primary and alternative tasking** with PACE prioritization (Primary, Alternative, Contingency, Emergency):

#### Shepherd's Room (Bay A) — Forward Avionics
**Primary tasking:** watchdog, fault detection, failover, authentication  
**Stack:** Wash + Zoë  
**Comms:** SiK primary / Wi-Fi secondary  
**PACE assignments:**
- Watchdog: **P**rimary
- Comms: **A**lternative
- Flight Control: **C**ontingency
- Payload Control: **E**mergency

#### Inara's Shuttle (Bay B) — Port Avionics
**Primary tasking:** camera, external sensors, high-bandwidth ground communications  
**Stack:** Wash + Zoë  
**Comms:** Wi-Fi primary / LoRa secondary (Note: LoRa moved to Emma boards on River/Simon in Rev R1)  
**PACE assignments:**
- Watchdog: **A**lternative
- Comms: **P**rimary
- Flight Control: **E**mergency
- Payload Control: **C**ontingency

#### River's Room (Bay C) — Starboard Avionics
**Primary tasking:** forward EDF control, nacelle tilt command/sync, resilient comms  
**Stack:** Wash + Zoë + **Emma** (49 MHz primary, LoRa secondary)  
**Comms:** 49 MHz (Part 15 §15.235) primary / LoRa 915 MHz secondary  
**PACE assignments:**
- Watchdog: **C**ontingency
- Comms: **E**mergency
- Flight Control: **P**rimary
- Payload Control: **A**lternative

#### Simon's Medbay (Bay D) — Aft Avionics
**Primary tasking:** aft EDF control, alternate watchdog, cargo/payload oversight  
**Stack:** Wash + Zoë + **Emma** (49 MHz primary, LoRa secondary)  
**Comms:** 49 MHz (Part 15 §15.235) primary / SiK secondary  
**PACE assignments:**
- Watchdog: **A**lternative
- Comms: **C**ontingency
- Flight Control: **A**lternative
- Payload Control: **P**rimary

### Communication Protocols

**Onboard:**
- CAN FD (galvanically isolated at every node via Cape-A-2 and Cape-B-2)
- MIL-STD 1553 (legacy, being phased)
- RS-485 (galvanically isolated at every node)
- Ethernet (galvanically isolated at every node)

**External command and control (all four usable for autonomous or manual C2):**
- Wi-Fi at 5 GHz
- Zigbee at 2.4 GHz
- MAVLink / SiK at 915 MHz
- AX.25 on 49 MHz channel (47 CFR Part 15 §15.235 — unlicensed, not Part 95 RCRS)

**S-Bus:** Supported by avionics capes but not currently used.

## Cape Naming and Revision History

### Wash — Flight Control and Sensor Cape

Provides flight control input, sensor fusion, and motor speed control via PID:
- GPS receiver
- Inertial Measurement Unit (IMU)
- Compass / magnetometer
- Barometer / altimeter
- Anti-collision range sensors
- Airspeed sensor
- PID motor speed control for EDFs
- Nacelle tilt servo control

**Current revision:** Cape-A-2 (Rev S, carrying forward the Rev R1 hull-frame/naming baseline unchanged)  
**Status:** Archived: Cape-A-1

### Zoë — Communications, Logging, and Payload Cape

Provides external communications, onboard logging, and payload interface:
- All four external radio transceivers (Wi-Fi, Zigbee, SiK/MAVLink, protocol stack software)
- Onboard data logging to hardware-enforced non-executable microSD card
- Payload I/O interfaces

**Current revision:** Cape-B-2 (Rev R1)  
**Planned (not yet in KiCad):** Rev R1 (remove LoRa, add P1+P2 passthrough rails matching Emma's pinout on River and Simon stacks)  
**Status:** Archived: Cape-B-1  
**LoRa note:** As of Rev R1, LoRa functionality migrated to Emma boards (River and Simon stacks only); Zoë.kicad_sch still carries JST-GH 6P Emma connector from earlier revision but this will be replaced with P1+P2 rails in the planned Rev R1 redesign.

### Emma — 49 MHz + LoRa Transceiver Cape (Rev R1)

Provides unlicensed-band communications for environments with restricted radio access:
- 49 MHz transceiver (47 CFR Part 15 §15.235 — unlicensed, suitable for high-RF-field environments)
- LoRa 915 MHz radio (Rev R1 addition)
- Galvanically isolated transceiver interfaces

**Current revision:** XCVR-49MHZ-2 Rev R1 (adds LoRa, replaces JST GH 6P with P1+P2 socket rails)  
**Installed in:** River's Room (Bay C) and Simon's Medbay (Bay D) only  
**Status:** Archived: XCVR-49MHZ-1, Cape-A-1, Cape-B-1

### Vera — Nose/Cargo-Bay Vision, ToF & Laser Board

**Vera is a standalone, compact PCB — not a PocketBeagle 2 Industrial cape.** Unlike
Wash/Zoë/Emma, it does not use the P1+P2 header stack and does not mount onto a PB2-I node.
It is its own independent board with its own power input (5V VCC, GND, PGND) and its own
processors (AM62A vision SoC + MSPM0G3507 MCU), connecting to the rest of the airframe only
through the shielded JST-GH Ethernet ring and CAN-FD trunk connectors, as a peer network node
rather than a stacked daughterboard.

One shared PCB design installed at **two physical locations**: the bow sensor pod (nose) and
the cargo bay nadir FPV mount (`cargo_fpv_bezel`).  Supersedes the RunCam Nano 4 analog
camera (REF-SENSOR-001, superseded) originally specified for the bow sensor pod.  Vera is
deliberately split into a **vision half** and a **control half** on the same board — two
real, currently-produced silicon vendors, not a fictional single-chip "port":

**Vision half:**

- **TI AM62A3/AM62A7** (Sitara, in production) — MIPI CSI-2 v1.3 camera input, 7th-gen VPAC/ISP,
  H.264 (Level 5.2) / H.265 (Level 5.1 High-tier) hardware encode up to 4K.
- Runs **TI's own open-source Linux BSP** (mainline-adjacent kernel, V4L2 capture, GStreamer
  encode pipeline) — genuinely open-source tooling, but explicitly **not** OpenIPC. OpenIPC's
  supported-hardware list (SigmaStar/GokeMicro/HiSilicon/Ingenic/Fullhan/Anyka/Allwinner/
  Ambarella/Novatek/Rockchip/Xiongmai) does not include any TI part, and TI's earlier DaVinci
  DM38x family (DM385/DM388) that an earlier design iteration considered is **NRND** (Not
  Recommended for New Designs) — excluded from this design for that reason.
- Chosen over a SigmaStar/OpenIPC path specifically for toolchain uniformity with the
  PocketBeagle 2 Industrial's TI Sitara AM6254 SoC (shared cross-compiler, kernel driver
  patterns, and debug tooling across Wash/Zoë and Vera).

**Control half:**

- **TI MSPM0G3507** MCU — native hardware MCAN (CAN-FD) peripheral; shares TI toolchain
  with the vision half and with the AM6254 real-time domain on Wash/Zoë.
- **Infineon OPTIGA SLB9670** SPI TPM 2.0 — same part already standardized fleet-wide on all
  8 Wash/Zoë nodes (REFERENCES.md §3.3/§4.2); Vera reuses it rather than introducing a new TPM
  part number.
- **Microchip KSZ9477** Ethernet switch — the only part in this family confirmed (via AN3474)
  to hardware-offload HSR/PRP ring redundancy per IEC 62439-3; LAN9355/KSZ9563 do **not**
  implement this and must not be substituted for the ring-redundancy role.
- **TI ISOW1044BDFMR** galvanically isolated CAN-FD transceiver (SOIC-16W, 5 kV reinforced
  insulation) — matches the Wash/Zoë Rev R EMI-hardening standard (TODO.md §1.2a); an earlier
  pass of this board used the non-isolated TCAN1042HG-Q1, corrected 2026-07-03.
- Shielded JST-GH connectors for the Ethernet ring (in/out, 5-pin: GND + TX±/RX±) and the
  CAN-FD trunk (4-pin), per the project's field-connector convention; metal shroud tied to
  PGND (chassis), never to the digital signal GND.

**EMI hardening (added 2026-07-03, matches Wash/Zoë Rev R baseline exactly):** each Ethernet
port carries Wurth 749010012A magnetics + 2× Bourns SRF2012-100Y CMC + 2× Nexperia
PRTR5V0U2X TVS before the ring connector; the CAN-FD bus carries the same CMC + TVS pairing
after U4. All parts/pinouts reused verbatim from this project's own verified
`gen_cape_a2.py`/`gen_cape_a2_pcb.py` — not fabricated. See `Vera.md` "EMI Hardening Status".

**ToF sensor:** Benewake TFmini-S (REF-SENSOR-002), unchanged from the existing bow sensor
pod design — read by the MSPM0G3507 over UART, republished signed over both the Ethernet
ring and CAN-FD.

**Laser (crosshair pointer) — location-specific, do not use one part for both sites:**

- **Nose:** 2"×2" (51×51 mm) crosshair at 50 ft (15.2 m) requires ≈0.19° fan angle — a
  near-collimated, high-power 520 nm green module. No off-the-shelf catalog part publishes
  this tight a divergence; a custom-collimated module is required, and at the optical power
  needed to be camera-visible in daylight it falls in **IEC 60825-1 Class 3B** (5–500 mW CW),
  not the Class 3R (≤5 mW) used elsewhere in this design. Class 3B requires a key-controlled
  interlock, an emission indicator, a beam-stop/shutter, and warning labeling — the existing
  GPIO-default-off pull-down is necessary but not sufficient on its own. **Do not source or
  wire this module until REFERENCES.md carries a verified Class 3B datasheet citation with a
  real part number** (tracked in TODO.md §1.2c).
- **Cargo bay:** 3"×3" (76×76 mm) at 5 ft (1.5 m) requires only ≈2.86° fan angle — well within
  the existing 5 mW 650 nm Class 3R crosshair module already vetted (REF-IEC-002, REF-FDA-001)
  for the bow sensor pod. No safety-class escalation needed at this location; reuse the
  existing Class 3R module and driver circuit (2N7002 MOSFET, 10 kΩ pull-down, GPIO enable).

**Status:** Design exploration only — no `.kicad_sch`/`.kicad_pcb` exists yet. See TODO.md
§1.2c (hardware) and §4.6 (firmware) for the WBS breakdown.

### Kaylee — Power Distribution Board (PDB)

Central power management and distribution:
- Battery management system
- 6V servo rail: TPS54540DDAR regulator (planned removal in Kaylee Rev A1; tilt servos to run on 5V rail)
- 5V main avionics rail
- EDF power distribution and PID control lines to all flight-control nodes

**Current revision:** Kaylee (pre-A1)  
**Planned (not yet in KiCad):** Rev A1 (remove 6V servo BEC; tilt servos to run on 5V rail with ~21 kg·cm capacity vs ~16 kg·cm tilt load requirement)  
**Location:** Inner neck of middle section (Kaylee's room), adjacent to Simon's Medbay

## PCB Design Standards

### Design Rules Checker (DRC) Workflow

Every schematic and PCB modification **must** be verified:

1. Open the schematic file in KiCad
2. Run **Electrical Rules Checker** (ERC) — resolve all violations and warnings
3. Open the PCB layout
4. Run **Design Rules Checker** (DRC) — resolve all violations and errors
5. Document any violations that cannot be resolved in `TODO.md` with the specific DRC rule and reason
6. Commit only after all DRC violations are either resolved or documented

### Footprint and Component Placement

**Critical note:** PCBs are tightly packed. All final component footprint positions will be placed manually after PCBs are populated and nets are built by script.

- If a DRC violation requires repositioning a component footprint, **refer the action to the user**
- Other modifications (net routing, trace widening, via placement) are allowed without user confirmation

### Schematics and PCB Files

- Every cape requires:
    - Complete schematic file (`.kicad_sch`)
    - Complete PCB layout (`.kicad_pcb`)
    - Copper traces ready for production
    - Proper IC footprints for all components
    - Production-ready Gerber files

## Security and Cryptography Requirements

Every message, internal and external, must be:
- **Digitally signed** and authenticated
- **Logged** for forensic analysis
- **Timestamped** by the TPM

### TPM (Trusted Platform Module)

- Every node carries a TPM for cryptographic operations
- All keys are generated and stored on the TPM, never in software
- All messages are signed using TPM-held keys

### Data Logging

- Everything is logged: sensor data, CAN messages, MAVLink commands, camera feed, authentication events
- Logs are saved to **hardware-enforced non-executable microSD cards** (write-once, never executable)
- All logs are signed and timestamped

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
- **915 MHz SiK/MAVLink:** 47 CFR Part 15 §15.247 (unlicensed ISM)
- **2.4 GHz Zigbee:** 47 CFR Part 15 §15.247 (unlicensed ISM)
- **5 GHz Wi-Fi:** 47 CFR Part 15 §15.407 (unlicensed UNII)

Citations: [REF-FCC-001, REF-FCC-002, REF-FCC-003]

## Work Tracking and Documentation

When modifying or creating cape designs:

1. Update the relevant `.kicad_sch` and `.kicad_pcb` files
2. Run ERC and DRC; document any violations in `TODO.md` with the reason
3. Update the cape description in `REFERENCES.md` if the design scope has changed
4. If planning a new cape revision, record it in `TODO.md` and cite this file
5. Keep `PROJECT_INDEX.md` up to date with new KiCad files
6. Archive old cape revisions in `archives/` with a note in `ARCHIVE_INDEX.md`

---

For project-wide standards, see the root `CLAUDE.md`.
