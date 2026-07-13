# Avionics Design — Claude Code Project Instructions

> *See the root `CLAUDE.md` for project-wide policies. This file provides specific guidance for avionics design, KiCad PCBs, capes, and microcontroller configuration.*

## Scope

This folder contains all electronics design and implementation: KiCad schematics and PCB layouts for avionics capes, microcontroller firmware, boot loaders, TPM configurations, and communications stack documentation. The avionics architecture is built on redundancy and failover across eight industrial SBCs distributed throughout the airframe.

## Onboard Avionics Architecture — 8-Node Cooperative System

**Platform:** Four pairs of **PocketBeagle2 Industrial SBCs** (8 nodes total, Rev S placement,
established at Rev R1):
- All 8 nodes carry **Wash** (Flight Control and Sensor Cape) and **Zoë** (Communications, Logging, and Payload Cape)
- All 8 nodes carry **TPM** (Trusted Platform Module) for cryptographic operations

**Emma Transceiver Cape** (49 MHz Part 15 §15.235, as-built; LoRa 915 MHz + P1/P2 rails are
IN PROGRESS, PCB-ahead-of-schematic — see "Cape Naming and Revision History" below for the
full, verified real status):
- Installed in **River's Room** (Bay C, starboard cargo) and **Simon's Medbay** (Bay D, middle section) only

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
**Comms:** Wi-Fi primary / LoRa secondary (Zoë still carries a real LoRa radio today; moving it
to Emma boards on River/Simon is IN PROGRESS, PCB-ahead-of-schematic — see "Cape Naming and
Revision History" below)  
**PACE assignments:**
- Watchdog: **A**lternative
- Comms: **P**rimary
- Flight Control: **E**mergency
- Payload Control: **C**ontingency

#### River's Room (Bay C) — Starboard Avionics
**Primary tasking:** forward EDF control, nacelle tilt command/sync, resilient comms  
**Stack:** Wash + Zoë + **Emma** (49 MHz primary today; LoRa secondary via Emma is IN
PROGRESS, PCB-ahead-of-schematic — Zoë still carries the live LoRa radio too until this is
reconciled, see "Cape Naming and Revision History" below)  
**Comms:** 49 MHz (Part 15 §15.235) primary / LoRa 915 MHz secondary  
**PACE assignments:**
- Watchdog: **C**ontingency
- Comms: **E**mergency
- Flight Control: **P**rimary
- Payload Control: **A**lternative

#### Simon's Medbay (Bay D) — Aft Avionics
**Primary tasking:** aft EDF control, alternate watchdog, cargo/payload oversight  
**Stack:** Wash + Zoë + **Emma** (49 MHz primary today; LoRa secondary via Emma is IN
PROGRESS, PCB-ahead-of-schematic — Zoë still carries the live LoRa radio too until this is
reconciled, see "Cape Naming and Revision History" below)  
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

**Current revision:** Cape-A-2 (Rev S; see `Wash.md` "Revision: R" — no design changes since
Rev R, carried forward unchanged)  
**Status:** Archived: Cape-A-1

### Zoë — Communications, Logging, and Payload Cape

Provides external communications, onboard logging, and payload interface:
- All four external radio transceivers (Wi-Fi, Zigbee, SiK/MAVLink, protocol stack software)
- Onboard data logging to hardware-enforced non-executable microSD card
- Payload I/O interfaces

**Current revision / real status (verified 2026-07-04, not assumed from prior doc text):**
Cape-B-2 (Rev S; `Zoë.md` "Revision: R" — same partial-migration state as Emma, see that
section):

- `Zoë.kicad_sch` still has a real `RFM95W` (LoRa) symbol — LoRa has NOT been removed from
  the schematic. Still has `Conn_JST_GH_06P`/`04P`/`03P` symbols too.
- **Updated finding 2026-07-04 (verified against the files, deeper than prior text):**
  `Zoë.kicad_pcb` is actually already at the intended end-state — **LoRa (RFM95W) is REMOVED
  from the PCB** and the `2x18_P1/P2_Socket` + `PB2-P1/P2-TOP` passthrough rails are placed.
  The **schematic lags the PCB** here (opposite of the earlier assumption). Worse, schematic
  and PCB use **different reference-designator conventions for the same parts** (`CMC_CAN`
  vs `CMC-CAN`, `X2Y_RS485` vs `X2Y-RS485`, `WINCH-DRV` vs `WINCH DRV`, `RS485` vs `RS-485`,
  `WIFI-BT` vs `WIFI & BT`, …) — only ~10 of ~50 refs match exactly. `Zoë.kicad_sch` also
  still carries the **LoRa block** (`LORA`/RFM95W, `FL_LORA`, `D_ANT_LORA`, `J_SMA_LORA`,
  `BPF_915`×2), the now-obsolete **`J_XCVR`** Emma-cable connector (should disappear for the
  same reason Emma's J1 did), and an **SBUS block** the PCB lacks.
- **Load-blocking bug FIXED 2026-07-04:** `Zoë.kicad_sch` would not open in `kicad-cli` 9.0.2
  at all — three `(comment …)` blocks were at the schematic top level (only valid inside
  `title_block`); converted to a `(text …)` annotation. Zoë now loads and ERC runs.
- **Net effect:** "remove LoRa" is DONE on the PCB, PENDING on the schematic; "add P1+P2
  rails" is DONE on the PCB, PENDING on the schematic. The remaining schematic-side
  reconciliation needs a **user-confirmed sch↔pcb reference-designator remap** before edits
  (flight-hardware footprint↔symbol association must not be guessed) — REFERRED TO USER,
  TODO.md §1.2b.

**Status:** Archived: Cape-B-1

### Emma — 49 MHz Transceiver Cape (Rev R baseline; LoRa+P1P2 addition IN PROGRESS — PCB layout ahead of schematic, see below)

Provides unlicensed-band communications for environments with restricted radio access:

- 49 MHz transceiver (47 CFR Part 15 §15.235 — unlicensed, suitable for high-RF-field environments) — as-built
- LoRa 915 MHz radio — **real HOPERF_RFM9XW_SMD (RFM95W) footprint with real nets
  (LORA_RESETN, LORA_DIO0, SPI1_CS_LORA) is physically placed and routed on
  `Emma.kicad_pcb`, but there is NO corresponding symbol anywhere in `Emma.kicad_sch`**
  (verified 2026-07-04: 11 LoRa/RFM95 references in the PCB, 0 in the schematic)
- Galvanically isolated transceiver interfaces

**Current revision / real status (verified 2026-07-04, not assumed from prior doc text):**
this board is in a genuine, uncomfortable in-between state, not a clean "done" or "not
started":

- `Emma.kicad_pcb` physically has BOTH the legacy `JST_GH_6P` "CAPE-B IF" connector (real
  nets: GND, UART_TX, UART_RX, PTT_N, RSSI_ANA, +3V3 — actively connected, not vestigial)
  AND the new `2x18_P1_Socket` / `2x18_P2_Socket` footprints AND the LoRa module, all three
  present simultaneously.
- `Emma.kicad_sch` (Emma.md "Revision: R") only contains a minimal EMI-hardening stub
  (CMC/TVS/ferrite/SMA coax/one JST_GH_06P symbol) — none of the LoRa module, the P1/P2
  sockets, or the 49 MHz transceiver IC itself appear in the schematic at all.
- Root cause: `avionics/kicad/complete_xcvr_49mhz2.py` added the PCB-side components and
  routing directly via the `pcbnew` Python API (BOM placement, net assignment, RF routing,
  silk labels) without ever touching the schematic — a real schematic/PCB parity gap, not
  a documentation-only inconsistency. This explains the "35 hard, 305 soft" DRC/ERC finding
  count seen when Emma is checked outside the `--changed-since`-scoped CI job.
- **RECONCILED 2026-07-04 (schematic-first migration, user decisions locked).** The gap was
  closed by making the schematic the source of truth. `avionics/kicad/gen_emma_sch.py`
  authored a complete `Emma.kicad_sch` from the as-placed PCB (loads in `kicad-cli` 9.0.2,
  **ERC 0 errors**); `avionics/kicad/mod_emma_pcb.py` (pcbnew) transformed the PCB to match.
  **sch↔pcb parity is exact** (74 refs, 104 nets, 0 per-net pin-count mismatches). User
  decisions applied: (a) **J1 (JST_GH_6P) DROPPED** — modem UART moved onto the PB2 rails
  (`UART_RCRS_RX`/`_TX`, honoring the "replace JST GH 6P with P1+P2" intent over keeping J1);
  (b) **PTT_N** → PB2-P2 payload GPIO, presence-gated by a cape-detect DT overlay (Emma has no
  MCU; the fixed PB2 pinout has no spare GPIO); (c) **RSSI → 1-bit `RSSI_DCD`** via a new
  on-board comparator `RSSI_CMP` (analog RSSI can't ride the rail — AM6254 GPADC uses dedicated
  analog balls). Remaining open items (TODO.md §1.2b): final placement+routing of the 4 new
  parts (parked off-board, refer to user), `RSSI_CMP` part/pinout datasheet vetting, PTT/RSSI
  pinmux firmware sign-off (Simon payload contention), and 3 pre-existing in-circuit stubs the
  schematic surfaced (`RF_ANT_SW`, `PA_EMIT`, `DDS_FSYNC`). Old EMI-stub schematic kept as
  `Emma.kicad_sch.stub-bak`.  
**Installed in:** River's Room (Bay C) and Simon's Medbay (Bay D) only  
**Status:** Archived: XCVR-49MHZ-1, Cape-A-1, Cape-B-1

### Jayne — Cargo-Handling System and Nose/Cargo-Bay Vision, ToF & Laser Board

**Jayne now names one integrated subsystem, not two separate identities.** It covers both
the mechanical cargo-handling hardware (winch, latch, cargo bay door — "I was aiming for
his head") and the vision/ToF/laser sensing board formerly documented under the working
name "Vera." The board gives the mechanical cargo system its eyes: it watches and measures
what the winch and latch are handling. Historical references to "Vera" in commit history,
older revisions of this document, and file headers refer to this same board and should be
read as "Jayne."

**The Jayne board is a standalone, compact PCB — not a PocketBeagle 2 Industrial cape.**
Unlike Wash/Zoë/Emma, it does not use the P1+P2 header stack and does not mount onto a PB2-I
node. It is its own independent board with its own power input (5V VCC, GND, PGND) and its
own processors (AM62A vision SoC + MSPM0G3507 MCU), connecting to the rest of the airframe
only through the shielded JST-GH Ethernet ring and CAN-FD trunk connectors, as a peer
network node rather than a stacked daughterboard.

One shared PCB design installed at **two physical locations**: the bow sensor pod (nose) and
the cargo bay nadir FPV mount (`cargo_fpv_bezel`), the latter co-located with the mechanical
cargo-handling hardware it supervises.  Supersedes the RunCam Nano 4 analog camera
(REF-SENSOR-001, superseded) originally specified for the bow sensor pod.  The board is
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
  patterns, and debug tooling across Wash/Zoë and the Jayne board).

**Control half:**

- **TI MSPM0G3507** MCU — native hardware MCAN (CAN-FD) peripheral; shares TI toolchain
  with the vision half and with the AM6254 real-time domain on Wash/Zoë.
- **Infineon OPTIGA SLB9670** SPI TPM 2.0 — same part already standardized fleet-wide on all
  8 Wash/Zoë nodes (REFERENCES.md §3.3/§4.2); Jayne reuses it rather than introducing a new TPM
  part number.
- **Microchip KSZ9477** Ethernet switch — the only part in this family confirmed (via AN3474)
  to hardware-offload HSR/PRP ring redundancy per IEC 62439-3; LAN9355/KSZ9563 do **not**
  implement this and must not be substituted for the ring-redundancy role.
- **TI ISOW1044BDFMR** galvanically isolated CAN-FD transceiver (**20-pin DFM package** —
  verified against TI datasheet SLLSFF7A Fig 7-1 / §8.4 "DFM/20 PINS"; earlier docs wrongly
  said "SOIC-16W", a fleet-wide footprint error flagged in TODO.md, 5 kV reinforced
  insulation) — matches the Wash/Zoë Rev R EMI-hardening standard (TODO.md §1.2a); an earlier
  pass of this board used the non-isolated TCAN1042HG-Q1, corrected 2026-07-03.
- Shielded JST-GH connectors for the Ethernet ring (in/out, 5-pin: GND + TX±/RX±) and the
  CAN-FD trunk (4-pin), per the project's field-connector convention; metal shroud tied to
  PGND (chassis), never to the digital signal GND.

**EMI hardening (added 2026-07-03, matches Wash/Zoë Rev R baseline exactly):** each Ethernet
port carries Wurth 749010012A magnetics + 2× Bourns SRF2012-100Y CMC + 2× Nexperia
PRTR5V0U2X TVS before the ring connector; the CAN-FD bus carries the same CMC + TVS pairing
after U4. All parts/pinouts reused verbatim from this project's own verified
`gen_cape_a2.py`/`gen_cape_a2_pcb.py` — not fabricated. See `Jayne.md` "EMI Hardening Status".

**ToF sensor:** Benewake TFmini-S (REF-SENSOR-002), unchanged from the existing bow sensor
pod design — read by the MSPM0G3507 over UART, republished signed over both the Ethernet
ring and CAN-FD.

**Laser — single 520 nm green source, per-location optic + hardware current limit**
(revised 2026-07-05, `docs/JAYNE_LASER_ANALYSIS.md`; supersedes the earlier "do not use one
part for both sites" split). Both installs share ONE green diode + driver; they differ only in
(1) a terminal optic that sets the spread angle and (2) a hardware current limit that sets the
optical power / IEC 60825-1 class:

- **Spread (terminal optic, 15× difference):** nose 2"×2" @ 50 ft ⇒ ≈0.19° (3.3 mrad),
  custom near-collimated; cargo 3"×3" @ 5 ft ⇒ ≈2.86° (50 mrad), stock DOE or diverging-lens
  dot. Same collimated green source both places.
- **Both sites — Class 2** (≤1 mW green). The nose is **not** inherently Class 3B: 3B was the
  worst-case corner (a power-diluted *spread* crosshair judged by a *naked eye* in *full sun*
  = ~82 mW). Jayne's actual requirement is *camera* visibility, detected by Jayne's own strobed
  camera + frame-difference, so a **thin-line green crosshair needs only ~0.2–0.8 mW → Class 2**
  (see `docs/JAYNE_LASER_ANALYSIS.md`). Cargo is likewise Class 2. **Class 2 at both sites
  eliminates the Class 3B key-interlock and mechanical shutter** — `LASER_KEY_IN`/`LASER_IND`
  become optional defense-in-depth. Keep the ≤1 mW cap **hardware-enforced**. 3B only returns
  if a *human at the 50 ft target* must see the pattern in full sun — not Jayne's use case.
- **Pattern is a thin-line CROSSHAIR (not a bare dot) — it is a projected metrology reference.**
  A PB2-I computes a detected object's **size and relative orientation** from ToF range + the
  crosshair's known projected angle + trigonometry (size = (obj_px/cross_px)·2R·tan(θ/2); tilt
  from arm foreshortening — `docs/JAYNE_LASER_ANALYSIS.md §4.4`). The binding constraint is
  camera pixel coverage, so the fan angle must be sized for it (the nominal 2" @ 50 ft is too
  small — target ≈4–8" for ~24–48 px). Thin lines keep it Class 2. **Do not source** until
  REFERENCES.md carries a verified datasheet citation (REF-IEC-002 pending; TODO.md §1.2c.4).

**Status:** Schematic net-correct and EMI-hardened (ERC clean of shorts); PCB footprints
placed, double-sided, corners rounded, 1.0 × 2.75 in (25.4 × 69.85 mm); traces not yet
routed — NOT fabrication-ready. See TODO.md §1.2c (hardware) and §4.6 (firmware) for the
WBS breakdown.

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
