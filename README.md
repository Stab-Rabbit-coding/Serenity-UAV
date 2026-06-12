# Serenity-UAV

> *Can't stop the signal, and can't take the sky from me.*

## Authoritative Project Instructions

The canonical workspace instructions and design policy are maintained in `CLAUDE.md`. All
contributors and automated tools (including assistants) must follow the requirements and
standards documented there (coding style, fabrication specs, licensing, and attribution).

A functional, security-conscious Unmanned Aerial Vehicle based on the Firefly-class spacecraft
Serenity from the 2002 show. Designed using Claude AI.

> Design mission profile:
>
> 1. Take off VTOL.
> 2. Land vertically with cargo bay open and load and secure a 4" x 3" x 3" 8oz Payload.
> 3. Take off VTOL with payload.
> 4. Fly into a 500W/m^2 broadband radio frequency environment.
> 5. Lower and release the payload from the cargo bay onto a platform.
> 6. Identify a 4x3x3 inch payload on a moving platform.
> 7. Synchronise flight with the platform.
> 8. Attach the payload to the hoist and lift it from the platform.
> 9. Pull the payload into the cargo bay and close the clamshells.
> 10. Exit the hazardous environment and return to origin.
>
> During execution of this mission profile, be able to perform the following:
>
> 1. Identify, categorized, log, and report rogue or unauthorized C2 commands and/or malicious logic from unauthorized or authorized transmitters.
> 2. Identify unauthorized or unsafe behavior from one or more of the onboard compute nodes.
> 3. Isolate effected node(s), gracefully failover functions, log, and report to ground control, while maintaining safety of flight.

---

## Specifications

| Parameter | Value |
|-----------|-------|
| Length | 24.0 in (609 mm) |
| Wingspan | 19.1 in (486 mm) |
| Height | 7.2 in (182 mm) |
| AUW — Phases 5–10 (nacelles only) | ~6.10 lbm (2,768 g) |
| AUW — Phase 11 (full system) | ~7.95 lbm (3,608 g) |
| Payload capacity (minimum) | 8.0 oz (226 g) in a 4″ × 3″ × 3″ bay |
| Thrust — nacelles only | 9.84 lbf (4,464 g) |
| Thrust — Phase 11 total | ~17.6 lbf (7,964 g) |
| T/W — nacelles only | ≈ 1.61 (full VTOL hover capable) |
| T/W — Phase 11 | ≈ 2.21 |

---

## Airframe

Airframe engineered to FAA and AUVSI standards for UAVs rather than relying on the
source desktop-model specifications.

### Coordinate Standard (Rev R1)

All design artifacts (SCAD, STL, Blender/FreeCAD scripts, documentation) use the
single validated **hull frame**: X = +port (lateral), Y = +aft (longitudinal),
Z = +dorsal, origin at the `SerenityAssembly.FCStd` world origin. As of R1
(2026-06-11) the validated component placements are **baked into the published
STL vertex data** by `tools/bake_hull_frame.py` (header marker
`SerenityUAV HULL-FRAME R1`); the FreeCAD assembly imports every primary
component at identity. Re-run the bake tool after regenerating any primary STL.
Documented exceptions: avionics KiCad files (board coordinates), Malcolm GCS
hardware (part-local), and G-code (printer bed). See CLAUDE.md
"Hull-Frame Coordinate Standard" for the full rule set and baked extents.

### Fuselage

The design retains the four canonical sections — head, cargo, middle, and rear — from the source hull model:
[thingiverse.com/thing:7330462](https://www.thingiverse.com/thing:7330462)
("Serenity Firefly with landing gear and swivel engines" by misubisu, CC BY 4.0).
Scaled to 24 in (609 mm) overall length.

- Shell walls hollowed to 0.079 in (2.0 mm) CF-PETG, watertight exterior surface.
- All unoccupied interior volume filled with 2 lb/ft³ (32 kg/m³) closed-cell foam for
  structural support and buoyancy.
- Bosses and ribs added to interior as needed for joints and component mounting.
- Mating faces between sections are left open to allow construction access and
  inter-compartment cable routing.

#### Compartments and Bays

Seven named compartments are specified:

**Shepherd's room** — Forward avionics bay (Bay A), head section near the bridge.
Primary tasking: watchdog, fault detection, failover, and authentication.
Wash + Zoë stack. SiK primary / WiFi secondary comms.
Ventilation ducting, cable conduits, and low-impedance bonding to other avionics bays.
External access via a removable hull panel on the head section.

**Inara's shuttle** — Avionics bay (Bay B), port side of the cargo section.
Primary tasking: camera, external sensors, and high-bandwidth ground communications.
Wash + Zoë stack. WiFi primary / LoRa secondary comms.
Ventilation ducting, cable conduits, and low-impedance bonding to other avionics bays.
External access via a removable hull panel above the port wing (resembles the shuttle
fairing in the canonical model). Also accessible via Jayne's cargo bay.

**River's room** — Avionics bay (Bay C), starboard side of the cargo section.
Primary tasking: forward EDF control, nacelle tilt command/sync, and resilient comms.
Wash + Zoë stack. 49 MHz RCRS primary / LoRa secondary comms.
Ventilation ducting, cable conduits, and low-impedance bonding to other avionics bays.
External access via a removable hull panel above the starboard wing. Also accessible
via Jayne's cargo bay.

**Simon's medbay** — Aft avionics bay (Bay D), middle section.
Primary tasking: aft EDF control, alternate watchdog, and cargo/payload oversight.
Wash + Zoë stack. 49 MHz RCRS primary / SiK secondary comms.
Ventilation ducting, cable conduits, and low-impedance bonding to other avionics bays.
Adjacent to Kaylee's room. Accessible via Jayne's cargo bay.

**Kaylee's room** — EMI-hardened power distribution bay, middle section, aft of the
cargo bay and adjacent to Simon's medbay and the engine cone.
Houses the Kaylee Power Distribution Board (PDB) and battery management system.
Accessible via Jayne's cargo bay.

**Battery compartment** — Middle/cargo section, accessible via Jayne's cargo bay.
Designed for quick field-swapping of the flight battery.

**Jayne's cargo bay** — Belly clamshell cargo bay with actuated doors.
Provides payload loading/release and access to Kaylee's room, the battery compartment,
Simon's medbay, and the port/starboard avionics bays (Inara's and River's).

**Deferred — Fuselage EDF compartment** *(Phase 11 only)*: EDF and motor bay in the
rear cone. Design files in `deferred/aft-edf/`.

### Wings

Wings modified to a high-lift airfoil profile (Selig S1223) while maintaining canonical
chord and span proportions. Carbon-fiber spars, pivot linkages, and cableways run through
each wing to the nacelles.

### Nacelles

Two nacelles (port + starboard), each housing two 1.97 in (50 mm) EDFs in tandem series.

**Nacelle tilt (Rev O — CG pivot):** 0° (cruise / horizontal) → 90° (hover / vertical)
→ 120° (backing thrust). Hard stops at −5° and 140°. Pivot at 3.27 in (83 mm) from
forward nacelle face (nacelle CG) — eliminates gravity torque on the tilt servo at all
angles. One digital servo ≥ 347 oz·in (25 kg·cm) @ 6 V per nacelle, fuselage-mounted.

**Variable-area nozzles (Rev O — M=1.0 / DP 25.4 gear train):** 8-petal iris on all
EDF exits.

- Nacelle nozzles (2×): gear-linked passively to the tilt pivot — no dedicated servo.
  0° nacelle tilt = nozzle fully closed; 90° tilt = nozzle fully open (full burn).
  Gear train: sector R = 0.87 in (22 mm) → pinion N = 12T → bevel pair N = 14T 45°
  → crown N = 12T → ring rack R = 1.10 in (28 mm) → ~70.7° ring travel per 90° nacelle sweep.
- Inner petal face: translucent-blue PETG, backlit by WS2812B LED ring inside each duct.

Iris mechanism concept:
[Variable-area EDF nozzle by BamJr](https://www.thingiverse.com/thing:2991269)
(CC BY 4.0) — all Rev O/P/Q nozzle geometry is original.

11-fin twisted inter-stage stator per nacelle, integral to the CF-PETG nacelle print.
33° vane angle. Generated by `blender_nacelle_revo.py` / `nacelle_pod_50mm_tandem.scad`.

Counter-rotating EDF pairs: port nacelle CW from intake, starboard CCW — zero net
torque reaction.

### Landing Gear

Four legs and tripod feet, geometry derived from the source Thingiverse model.

---

## Powerplant

### Power Distribution

**Kaylee** — EMI-hardened Power Distribution Board provides clean, filtered, monitored,
and decoupled power to all powerplant, avionics, flight control, and cargo-handling
systems with graceful degradation. Kaylee receives direction from the flight control node
(Wash). Faraday enclosure; located in Kaylee's room, middle section.

### Battery

| Parameter | Value |
|-----------|-------|
| Chemistry | LiPo, 6S (22.2 V nominal) |
| Capacity | 4000 mAh |
| Discharge rating | 60 C |
| Mass | 26.5 oz (750 g) |
| Dimensions (L × W × H) | 5.59″ × 1.97″ × 1.50″ (142 mm × 50 mm × 38 mm) |

### Propulsion — Rev R baseline

**Nacelle EDFs (4 total — active all phases):**

- Baseline EDF: XFly Galaxy X5 50 mm 12-blade 6S 3200 KV — **2.73 lbf (1,240 g) thrust per EDF**
  ([xfly-model.eu](https://xfly-model.eu))
- Per nacelle (tandem pair, 90% additive via 11-fin inter-stage stator):
  2 × 2.73 × 0.90 = **4.92 lbf (2,232 g)**
- Total nacelle thrust (2 nacelles): **9.84 lbf (4,464 g)**

**Phase 5–10 (nacelles only):**
AUW ~6.10 lbm (2,768 g) | Thrust 9.84 lbf (4,464 g) | T/W ≈ **1.61** — full VTOL hover capable.

---

#### DEFERRED — Phase 11: Fuselage EDF

Design files in `deferred/aft-edf/`. Physical build deferred until all other systems are proven.
Nacelle-only T/W ≈ 1.61 is sufficient for VTOL hover.

- 1 × 4.72 in (120 mm) EDF in the rear fuselage cone — ~7.72 lbf (3,500 g) thrust, exhaust straight aft.
- Deferred EDF system mass: ~1.85 lbm (840 g) total
  (EDF ~14.1 oz / 400 g + ESC ~4.6 oz / 130 g + CF-PETG intake frame ~3.2 oz / 90 g
  + PETG plenum ~2.8 oz / 80 g + nozzle frame/petals/servo/wiring ~4.9 oz / 140 g)
- **Phase 11 full-system:** AUW ~7.95 lbm (3,608 g) | Total thrust ~17.6 lbf (7,964 g) | T/W ≈ **2.21**
- Fuselage EDF intake: 4 radial scoops at neck station ~12.2 in (310 mm) via
  `neck_intake_frame.stl` + `aft_edf_plenum.stl` (cross-shaped 4-to-1 plenum manifold).

---

### Servos and Motors

| Item | Qty | Spec |
|------|-----|------|
| Nacelle tilt servo | 2 | Digital, ≥ 347 oz·in (25 kg·cm) @ 6 V |
| Cargo door servo | 1 | SG90 class |
| Cargo release servo | 1 | SG90 class |
| Cargo winch motor | 1 | N20 gear motor, ~300 RPM |
| **Deferred Phase 11** rear nozzle servo | 1 | SG90 class |

Cargo door + release controlled via DRV8833 H-bridge on the Simon node.

---

## Avionics

EMI hardening design objective: operation in a **500 W/m²** RF environment (e.g., in the
near field of radiating commercial antenna systems).

### Ground Control — Mal

- ArduPilot-compatible Ground Control Station.
- Name: **Malcolm** ("CAPT Reynolds / CAPT Tight Pants") — *"I aim to misbehave."*
- Requires a paired Zoë + PocketBeagle 2 Industrial stack for communications.

### Onboard — 8-node cooperative architecture

8 × PocketBeagle 2 Industrial (AM6254) boards arranged as 4 stacks of 1 Wash + 1 Zoë,
one stack per avionics bay.

**Wash** (flight control cape — 4 nodes):
GPS, IMU, barometer, airspeed sensor, FPV camera, TPM 2.0, ADC, ESC telemetry, PWM, GPIO.
EMI-hardened v2 design (CAPE-A-2).

**Zoë** (comms/logging cape — 4 nodes):
MAVLink/SiK 915 MHz, LoRa RFM95W 915 MHz, TI WL1837MOD WiFi/BT, 49 MHz RCRS transceiver
(Emma sub-module), CAN FD, MIL-STD-1553B, RS-485, Ethernet RSTP ring, TPM 2.0,
ATF16V8BQL CPLD hardware write-blocker, non-executable log microSD.
EMI-hardened v2 design (CAPE-B-2).

**Rev R — EMI-hardened v2 capes at ALL 8 positions.**
All nodes use 5 kV galvanic isolation:
- CAN FD: ISOW1044BDFMR (TI)
- RS-485: ADM2795EBRWZ (ADI)
- Ethernet: ADIN1300BCPZ PHY via dual ISO7642FDWRR + Würth 749010012A transformer (JST GH 4P)
- Emma: SRF2012-100Y CMC, PRTR5V0U2X TVS, X2Y bridging capacitor on antenna feed

All isolation barriers IEC 62368-1 / VDE 0884-11 certified at 5 kV.
Cape-A-1, Cape-B-1, and XCVR-49MHZ-1 archived Rev Q (2026-06-05).
Gerbers for v2 capes pending DRC sign-off.

**Intra-vehicle networks (all nodes):** CAN FD, MIL-STD-1553B, RS-485, Ethernet RSTP ring.

**External communications:**

| Link | Frequency | Node (primary) |
|------|-----------|---------------|
| SiK / MAVLink | 915 MHz | Shepherd (primary), Inara (secondary) |
| WiFi | 5 GHz | Inara (primary), Shepherd (secondary) |
| LoRa | 915 MHz | River (primary), Simon (secondary) |
| AX.25 / RCRS | 49 MHz | River + Simon (FCC Part 95 RCRS) |
| Zigbee | 2.4 GHz | Zoë nodes (secondary mesh) |

**Security:** Every message (internal and external) is digitally signed and authenticated.
All sensor data, messages, and camera feeds are logged to hardware-enforced non-executable
microSD cards (ATF16V8BQL CPLD write-blocker on each Zoë node). NIST SP 800-207 Zero Trust
architecture; NIST SP 800-82 Rev 3 ICS security; every board has a TPM 2.0.

**PACE workload assignments:**

| Function | Primary | Alternate | Contingency | Emergency |
|----------|---------|-----------|-------------|-----------|
| Watchdog | Shepherd | Inara | Simon | River |
| Comms | Inara | Shepherd | River | Simon |
| Flight control | River | Simon | Shepherd | Inara |
| Payload control | Simon | River | Inara | Shepherd |

---

## Cargo Handling — Jayne

*"I was aiming for his head."*

- Payload design minimum: **8.0 oz (226 g)** in a 4″ × 3″ × 3″ bay (Rev P spec).
- Payload capacity (PDB-rated): 14.1 oz (400 g).
- Belly clamshell doors (CF-PETG, port + starboard), 8-barrel piano hinge on 0.118 in (3 mm)
  CF rod.
- SG90 door servo + SG90 release servo via DRV8833 H-bridge.
- N20 winch motor + Dyneema SK75 0.020 in (0.5 mm) line, auto-latch payload cradle.
- HX711 load cell, FPV camera bezel, GPS retention ring, 3M foam gasket door seal.
- Winch/gondola system supports loading and releasing cargo in flight.
  *(Just be careful about taking jobs from Mr. Niska.)*

---

## References

- Design conversation: [claude.ai/share/a1e3900e-d2bf-4690-ba63-25178e7de666](https://claude.ai/share/a1e3900e-d2bf-4690-ba63-25178e7de666)
- Latest design revision spec: `current-specification/serenity-rev-r.jsx`

---

## License

Published under **Creative Commons Attribution 4.0 International** by Steve Griffing,
PE(CSE), CISSP-ISSEP, CPP. Revision R, June 2026.
[creativecommons.org/licenses/by/4.0](https://creativecommons.org/licenses/by/4.0)

## Attribution

> "Serenity Tiltrotor Drone Project, CC BY 4.0, based on:
> · Serenity Firefly-class hull by misubisu (thingiverse.com/thing:7330462, CC BY 4.0)
> · Variable-area EDF nozzle by BamJr (thingiverse.com/thing:2991269, CC BY 4.0)
> Include a link to creativecommons.org/licenses/by/4.0 and indicate if changes were made."

### Component License Map

| Component | Original Author | Source | License | Derivative Notes |
|-----------|----------------|--------|---------|-----------------|
| Hull | misubisu | [thingiverse.com/thing:7330462](https://www.thingiverse.com/thing:7330462) | CC BY 4.0 | Scaled to 24 in, hollowed to 0.079 in (2.0 mm) CF-PETG shell, foam-filled |
| Nozzle mechanism concept | BamJr | [thingiverse.com/thing:2991269](https://www.thingiverse.com/thing:2991269) | CC BY 4.0 | Iris petal concept reference; all Rev O/P/Q nozzle geometry original |
| Design | This project | — | CC BY 4.0 | All original work: PCBs, firmware spec, wiring, flight system |

### What This License Covers

Covered under CC BY 4.0:

- 3D-printable hull, nacelle, and nozzle design files (STL/SCAD/FCStd)
- PCB schematics and Gerber files for Wash, Zoë, Kaylee, and Emma
- Circuit diagrams, pinout tables, and wiring specifications
- Mechanical drawings and assembly specifications
- Firmware architecture specifications and algorithm descriptions
- This design document in all its revisions (A–R and beyond)
- Any derived works must carry CC BY 4.0 and attribute all upstream authors

Not covered / separate terms:

- Third-party commercial components (EDFs, ESCs, PocketBeagle 2, etc.) — their own terms
- SiK radio firmware — GPL-3.0
- ArduPilot / QGroundControl — GPL-3.0
- tpm2-tools / tpm2-tss — BSD-2
- CPLD Verilog write-blocker firmware — separately MIT licensed
- Proprietary flight controller firmware (your compiled code) — your terms
- FAA/ICAO regulatory compliance is YOUR responsibility as operator

### Patent Notice

This license does NOT grant rights to any patents held by component manufacturers or the
design authors. The design uses standard open hardware interfaces (CAN FD, Ethernet, SDIO,
SPI, I²C, MAVLink). If you commercialise products based on this design, conduct your own
freedom-to-operate analysis. The write-blocker CPLD design follows published NIST SP 800-72
principles; no patent claims are made on the implementation.

### Forensic Evidence Integrity Note

The write-blocker and NX enforcement hardware described in this design are intended to
support forensic data integrity in UAV operations contexts. They are NOT certified forensic
tools per NIST/SWGDE standards. Do not use this design as the sole mechanism for evidence
preservation in legal proceedings without independent verification of the implementation
against your jurisdiction's evidence handling requirements.
