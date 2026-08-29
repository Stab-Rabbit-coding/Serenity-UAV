# Nacelle Tilt-Angle Feedback (AK7455) — EMI Wiring Specification

**Task:** 1.9.1 — Nacelle Tilt-Angle Feedback (Hall encoder)  
**Subtask:** Wiring per EMI spec  
**Design Objective:** Correct operation in 500 W/m² RF field  
**Reference Standards:**  
- NIST SP 800-207 Zero Trust [REF-NIST-001 §2.1, §2.2, §3.3]
- Serenity AGENTS.md §1 (EMI hardening objective)
- avionics/emi-hardening/WBS.md §1.4.4, §1.4.6  
**Date:** 2026-08-01

---

## 1. Overview

The AK7455 nacelle tilt-angle encoder sits on the fixed wing (non-rotating) and reads a diametric magnet ring on the rotating spar hub. In the 500 W/m² RF environment, the encoder's SPI data lines and power supply are susceptible to:

1. **RF ingress via sensor leads** — unshielded 100 mm wires in high-field region
2. **Conducted noise on twisted-pair from nacelle to fuselage** — coupling into isolated CAN-FD and RS-485
3. **Ground loops** — improper shield termination at the nacelle/wing boundary

This specification defines wiring and routing rules to maintain data integrity under EMI stress.

---

## 2. Encoder-to-Gateway Wiring (Nacelle → Wing Root)

### 2.1 Sensor Lead Routing (Nacelle Interior)

**Lead runs:** AK7455 SPI pins (CS, CLK, MOSI, MISO) + power/ground from encoder PCB to CAN-PERIPH-GW-1 gateway located at nacelle pivot housing.

| Signal | Cable Type | Length | Shielding | Termination |
|--------|-----------|--------|-----------|-------------|
| SPI_CS | Shielded twisted pair, 28 AWG | 50–80 mm | Braid, drain wire to GND at both ends | Connector shell |
| SPI_CLK | Shielded twisted pair, 28 AWG | 50–80 mm | Braid, drain wire to GND at both ends | Connector shell |
| SPI_MOSI | Shielded twisted pair, 28 AWG | 50–80 mm | Braid, drain wire to GND at both ends | Connector shell |
| SPI_MISO | Shielded twisted pair, 28 AWG | 50–80 mm | Braid, drain wire to GND at both ends | Connector shell |
| +3V3, GND | Shielded twisted pair, 24 AWG | 50–80 mm | Braid, continuous bond to nacelle local GND plane | Connector shell |

**Routing Rules:**
1. **Separation:** Keep SPI leads ≥10 mm away from 40 A EDF power feeds (motor phase + ESC PWM return paths)
2. **Strain Relief:** Use ferrite bead (Würth 742792512 or equivalent, 100 MHz resonance) on +3V3 entry to encoder PCB
3. **Shielding Coverage:** 100% braid coverage; no unshielded segments
4. **Drain Wire:** One continuous drain wire per shielded pair; solder to connector shell at both encoder and gateway ends (see §2.2)

### 2.2 Shield Termination at Connector Interfaces

**AK7455 Encoder Connector (SPI header on encoder board):**
- Connector type: JST-GH 5-pin (SPI_CS, SPI_CLK, SPI_MOSI, SPI_MISO, NC) or custom header
- Shield termination: Drain wire soldered to pin 4 (GND) or local via on encoder PCB; braid soldered to metal shield/shell
- **Do NOT float the shield** — 100% connection to encoder-local GND plane

**CAN-PERIPH-GW-1 Gateway Connector (SPI input header on gateway board):**
- Connector type: Matching SPI header footprint on gateway
- Shield termination: Drain wire soldered to CAN-PERIPH-GW-1 local GND via; braid to connector shell
- Gateway GND: Bonded to nacelle structural ground plane (see §3.1)

### 2.3 Cable Grouping and Separation

Within the nacelle:
- **Group 1 (SPI signals):** CS, CLK, MOSI, MISO as a single shielded quad (e.g., Lapp ETHERLINE® TORSION or equivalent: 4-pair shielded, foil + braid)
- **Group 2 (Power):** +3V3 and GND in separate shielded twisted pair
- **Minimum Spacing:** 15 mm separation between Groups 1 and 2 (to prevent capacitive coupling)
  - **DOCUMENTED DEVIATION (Rev T1, wing conduit only):** inside the wing both
    groups share one Ø6.5 mm bore at chord station 44.5. 15 mm of separation is
    not achievable at any bore the S1223 section can hold there, and a second
    15-mm-separated conduit would have to sit in the shallow aft region where
    the Ø7 EDF conduits already could not hold wall. Both groups are 100 %
    braid-shielded per §2.1, which is the actual mitigation; this rule guards
    UNSHIELDED proximity. Separation from the 40 A feeds — the clearance that
    matters — is now far better than before: those conductors run inside the
    spar's own grounded CF wall, 26 mm forward, rather than in an open conduit
    9 mm away. See `docs/WING_ATTACH_INTERFACE.md` §4.5.
- **EDF Feed Clearance:** ≥20 mm horizontal clearance from 40 A power leads (motor + ESC returns); cross perpendicular if unavoidable (to minimize flux coupling)

---

## 3. Gateway-to-Bus Wiring (Wing Root → Fuselage Avionics Bay)

### 3.1 CAN-PERIPH-GW-1 Local Grounding

**Nacelle Structural Ground Plane:**
- CAN-PERIPH-GW-1 board mounted on composite spacer or bracket at nacelle pivot housing
- Mounting: M3 nylon or stainless standoffs (no direct metal contact unless bonded)
- **Local GND:** 0.5 mm² (20 AWG equivalent) dedicated bonding strap from gateway board GND via to nacelle aluminum frame boss or carbon-fiber structural rib
- Purpose: Provides local current return path; prevents ground loops by isolating gateway GND from fuselage common GND

**Inter-Node Ground Bond (Gateway → Fuselage):**
- Bonding strap run: Nacelle pivot housing → fuselage keel via dedicated 20 AWG (0.5 mm²) bare copper wire
- Length: ~200 mm (port nacelle), ~200 mm (stbd nacelle)
- Routing: Through dedicated ferrite-lined conduit (see §3.3) separate from signal bundles
- **Termination:** Crimp lugs on both ends; torque M3 screws to 2.0 N·m; apply dielectric grease
- **Critical Rule:** Each nacelle has **one and only one** ground return path to fuselage (no parallel ground loops)

### 3.2 Isolated CAN-FD and RS-485 from Gateway to Fuselage Nodes

**Architecture:**
Each CAN-PERIPH-GW-1 gateway (port and starboard nacelles) publishes tilt-angle measurements on both isolated CAN-FD and isolated RS-485. River (FC3) and Simon (FC4) firmware subscribe to these bus messages.

| Bus Type | Connector | Shielding | Run Length | Isolation Requirement |
|----------|-----------|-----------|------------|----------------------|
| **CAN-FD (Isolated)** | 3-pin JST-GH (CAN_H, CAN_L, GND) | Shielded twisted pair, 24 AWG | ~1000 mm (nose to aft bay) | ISOW1044BDFMR (5 kV working) on each gateway |
| **RS-485 (Isolated)** | 3-pin JST-GH (RS485_A, RS485_B, GND) | Shielded twisted pair, 24 AWG | ~1000 mm (nose to aft bay) | ISOW1412 (5 kV working) on each gateway |

**Routing Rules:**
1. **Separation:** Keep CAN-FD and RS-485 pairs ≥20 mm apart to avoid crosstalk
2. **Common Conduit:** Use separate ferrite-lined PTFE conduits for CAN-FD and RS-485; route through dedicated channels in fuselage keel or internal structure
3. **Shield Continuity:** 100% braid coverage, continuous from gateway connector to receiving node (Pilot/XO/Commo cape connectors)
4. **Drain Wires:** One continuous drain per shielded pair; solder to J_CAN / J_RS485 connector shells at receiving nodes (see §4 below)

### 3.3 Ferrite-Lined Conduit

**Conduit Spec (per EMI hardening §1.4.3):**
- **Type:** PTFE tubing, internal Ni-Zn ferrite powder fill (or bifilar winding)
- **Size:** 6 mm OD, 4 mm ID (accommodates two 24 AWG shielded pairs + drain wire slack)
- **Length:** Nacelle exit point → first avionics bay (Shepherd's room / Bay A); approximately 1.2 m per side
- **Termination:** Ferrite-lined connector ferrules at both nacelle (gateway) and fuselage (Pilot) ends
- **Purpose:** Attenuates RF ingress over 100 kHz–1 GHz range; typical insertion loss ≥20 dB at 500 MHz

---

## 4. Fuselage Avionics Bay Terminations (Pilot/XO Capes)

### 4.1 CAN-FD Connector (J_CAN-FD on Pilot / J_CAN-FD on XO)

**Connector:** 3-pin JST-GH (CAN_H, CAN_L, GND) on Pilot and XO capes (already populated per AGENTS.md §1.2a)

**Wiring:**
- CAN_H (pin 1): Shielded wire from gateway CAN_H → Pilot/XO CAN_H pad
- CAN_L (pin 2): Shielded wire from gateway CAN_L → Pilot/XO CAN_L pad
- Drain Wire: Soldered to J_CAN-FD connector shell (metal); shell bonded to cape GND plane via via-stitching (existing)
- Shield: Continuous from gateway to Pilot; termination: solder braid to shell

**Isolation on Cape:**
- ISOW1044BDFMR (or verified drop-in) provides 5 kV galvanic isolation; already present on Pilot.kicad_sch (§1.2a.1)
- CAN termination: 120 Ω resistor soldered across CAN_H/CAN_L at **Shepherd's room bay terminus only** (see routing topology in §5 below)

### 4.2 RS-485 Connector (J_RS485 on Pilot / J_RS485 on XO)

**Connector:** 3-pin JST-GH (RS485_A, RS485_B, GND) on Pilot and XO capes

**Wiring:**
- RS485_A (pin 1): Shielded wire from gateway RS485_A → Pilot/XO RS485_A pad
- RS485_B (pin 2): Shielded wire from gateway RS485_B → Pilot/XO RS485_B pad
- Drain Wire: Soldered to J_RS485 connector shell
- Shield: Continuous from gateway to Pilot; termination: solder braid to shell

**Isolation on Cape:**
- ISOW1412 provides 5 kV galvanic isolation; already present on Pilot.kicad_sch (via fleet-wide upgrade in §1.9.2)
- RS-485 termination: 120 Ω resistor soldered across RS485_A/B at **the two physical bus ends only** (see topology in §5)

---

## 5. Bus Topology & Termination Strategy

### 5.1 CAN-FD Ring Configuration

```
                     Shepherd's Room (Bay A)
                     ├─ CN1 XO (Comms)
                     ├─ FC1 Pilot (Flight Control)
                     └─ 120 Ω termination (SOLDERED)
                              ↓
              [Port Nacelle Gateway] ──CAN_H/L──→ [Shielded pair in ferrite conduit]
              Port AK7455 tilt data                         ↓
              [ISOW1044BDFMR on gateway]          Inara's Shuttle (Bay B)
                              ↑                   ├─ CN2 XO
                              │                   ├─ FC2 Pilot
                    [Daisy-chain to other nodes]  └─ No termination
                              ↑
              [Stbd Nacelle Gateway] ──CAN_H/L──→ [Shielded pair in ferrite conduit]
              Stbd AK7455 tilt data                        ↓
              [ISOW1044BDFMR on gateway]           River's Room (Bay C)
                                                  ├─ CN3 XO
                                                  ├─ FC3 Pilot
                                                  └─ No termination
                                                           ↓
                                                  Simon's Medbay (Bay D)
                                                  ├─ CN4 XO
                                                  ├─ FC4 Pilot
                                                  └─ 120 Ω termination (SOLDERED)
```

**Rule:** CAN terminations soldered at Bay A and Bay D only (first and last nodes in the daisy-chain); port and starboard encoder gateways **do not** provide termination (they are intermediate nodes on the ring).

### 5.2 RS-485 Daisy-Chain Configuration

```
     Shepherd's Room (Bay A)
     ├─ 120 Ω termination (SOLDERED, Bay A end)
              ↓
     Inara's Shuttle (Bay B) → River's Room (Bay C) → Simon's Medbay (Bay D)
     ├─ No termination          ├─ No termination     ├─ 120 Ω termination (SOLDERED, Bay D end)
```

**Port and Stbd Nacelle Gateways:** Each gateway provides RS-485_A/B output that joins the daisy-chain at Bay A; same termination rule applies (ends only).

---

## 6. Ferromagnetic Spar Interaction (Magnetic Sensor Siting)

### 6.1 Spar Proximity Effects

> **CORRECTED 2026-08-29 (Rev T1, WA-R13).** The premise below is no longer
> true. The tilt spar is now a **fixed roll-wrapped CARBON FIBRE tube**
> (20 × 16.3 mm, `docs/plans/2026-08-29-003-...` KTD4), not 4130 steel, so the
> ferromagnetic-shaft field distortion this section was written about **is
> removed, not mitigated**. The mitigations below are RETAINED anyway, with a
> changed target: the nearby ferrous parts are now the Ø4 mm steel tilt drive
> shaft and its pinion, plus any fasteners and the nacelle-side collar. The
> in-situ zero-calibration therefore stays mandatory — it now absorbs drive-train
> field effects rather than the spar's. §6.2's clearance rules stand unchanged.
>
> Two further Rev T1 changes affect this section's geometry: the ring magnet
> grew to **ID 27 / OD 41 mm** (ID 10 could not pass over a Ø20 spar) and
> `HALL_SENS_R` moved **11 → 17 mm** so the IC still reads mid-annulus. See
> `docs/WING_ATTACH_INTERFACE.md` §4.5.

**Context (superseded — see the correction above):** The tilt spar is 4130 steel (ferromagnetic). The AK7455 magnet's field interacts with the ferrous spar, creating residual field distortion that shifts the encoded angle reading.

**Mitigation Strategy (already addressed in §3 of AK7455_CALIBRATION_SPECIFICATION.md):**
1. **Zero-calibration** absorbs static spar field effects at each tilt angle
2. **Wiring separation:** Keep sensor/gateway leads ≥50 mm from the ferrous spar itself
3. **SPI shielding:** Braid shielding on sensor leads attenuates RF that would otherwise couple into the encoder and distort readings

### 6.2 Sensor Mounting Clearance

**Encoder Placement Rule (avionics/emi-hardening/WBS.md §1.4.6):**
- Minimum 30 mm clearance from the tilt spar centerline
- Magnet ring must sit in a non-ferrous pocket (aluminum or composite; see airframe CAD)
- Encoder PCB mounted on non-ferrous standoff (nylon M2.5 or phenolic)
- No ferrous fasteners within 40 mm of magnet ring

---

## 7. Testing and Validation

### 7.1 Continuity and Resistance Checks (Pre-Flight)

| Test Point | Target | Acceptance |
|-----------|--------|-----------|
| AK7455_GND → Nacelle frame | Shielded pair twisted 1 m / 50 Ω | < 0.05 Ω @ 1 kHz |
| Gateway CAN_H/L via J_CAN | Twisted pair, 120 Ω characteristic | 100–140 Ω (@1 MHz) |
| Gateway RS485_A/B via J_RS485 | Twisted pair, 120 Ω characteristic | 100–140 Ω (@1 MHz) |
| Shield drain wire (encoder → gateway) | Continuous, single strand | < 0.01 Ω |
| Shield continuity (gateway → Pilot) | Braid + drain, full run | < 0.1 Ω |

### 7.2 EMI Susceptibility (Bench, Phase 4)

1. **RF Field Exposure (3 W / 100 mm antenna, 500 MHz):**
   - Bring radiating RF source to 100 mm of nacelle in 50 mm increments
   - Monitor AK7455 angle readings via CAN bus
   - **Acceptance:** Angle variation < 2° RMS; no dropouts; no data corruption

2. **Conducted Noise (40 A transient on EDF phase leads):**
   - Inject 40 A pulse (1 ms rise, 10 ms duration) into EDF motor phase lead
   - Monitor CAN and RS-485 bus traffic
   - **Acceptance:** No frame loss; no message corruption (HMAC validation on RS-485 messages)

### 7.3 Flight Validation (Phases 5–6)

1. **Tethered Hover (Phase 5):**
   - Nacelle sweep at 10°/s while monitoring CAN tilt-angle messages
   - **Acceptance:** Message rate 100 Hz steady; no dropouts; angle updates monotonic

2. **Free Hover + Transition (Phase 5–6):**
   - Autonomous nacelle transition 0° ↔ 90° at commanded rates
   - Monitor feedback latency (target < 50 ms from command to measured angle)
   - **Acceptance:** Angle tracks command within 2°; no oscillation

---

## 8. Documentation References

- **Firmware Spec:** `avionics/firmware/AK7455_CALIBRATION_SPECIFICATION.md`
- **EMI Hardening Guide:** `avionics/emi-hardening/WBS.md` §1.4.3, §1.4.4, §1.4.6
- **Gateway Board:** `avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md`
- **Airframe/Spar:** `docs/TILT_SPAR_ANALYSIS.md` §1, §3.5; `airframe/wings-nacelles/WBS.md` §1.1.3.6
- **Datasheet:** REF-SENSOR-008 — AK AK7455 SPI Angle Encoder, 200800064-E-00

---

## 9. Implementation Owner & Schedule

**Lead:** Avionics wiring/integration team  
**Secondary:** Airframe/structures (sensor mounting, spar clearance verification)  
**Start Date:** Upon task 1.9 approval; board fab completion (Phase 4)  
**Completion Milestone:** Phase 1 (Hull Structure) final assembly check; Phase 5 (Minimum Viable Flyer) pre-flight validation

---

*Drafted by Claude Haiku 4.5 (2026-08-01) in compliance with NIST SP 800-207 and Serenity EMI design objectives.*
