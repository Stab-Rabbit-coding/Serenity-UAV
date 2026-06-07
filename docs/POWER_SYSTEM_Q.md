# Serenity UAV — Power System Analysis (Rev Q)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Revision:** Q
**Date:** 2026-06-06
**Status:** Design baseline — PCB layout pending

---

## 1. Powerplant Configuration

| Location | Count | Model (interim / Phase 7) | Battery | Notes |
|---|---|---|---|---|
| Port nacelle | 2 | Budget 50 mm 6S (Phase 2–6) / XRP 80 mm 6S (Phase 7) | 6S | Tandem series, CCW from intake |
| Starboard nacelle | 2 | Budget 50 mm 6S / XRP 80 mm 6S | 6S | Tandem series, CW from intake |
| Rear fuselage | 1 | XFLY X4 PRO 40 mm 12-blade 5850 KV | 4 S tap (cells 1–4 of 6S pack) | Longitudinal — forward thrust only |

Total EDFs: 5 (4 nacelle + 1 fuselage)
Nacelle tilt: 0° (cruise / horizontal) → 90° (VTOL / vertical) → 120° (reverse thrust)
Rear EDF orientation: fixed horizontal — **provides zero vertical thrust in any nacelle position.**

---

## 2. VTOL / Hover Thrust Analysis

### 2.1 Thrust model

In VTOL hover the nacelles are tilted to 90° (vertical). The rear fuselage EDF exhausts
straight aft and contributes **no vertical force** regardless of throttle.

| EDF group | Unit count | Thrust per unit | Group thrust | Contributes to VTOL lift? |
|---|---|---|---|---|
| Nacelle EDFs (50 mm budget, Phase 2–6) | 4 | ~228 g | **~911 g × 2 nacelles = ~1 822 g** | **YES** |
| Nacelle EDFs (XRP 80 mm, Phase 7) | 4 | ~1 325 g | **~2 650 g × 2 nacelles = ~5 300 g** | **YES** |
| Rear fuselage EDF (120 mm) | 1 | ~3 500 g | ~3 500 g | **NO — horizontal thrust** |

> Note: The "total thrust ~5 322 g, T/W ≈ 1.47" figure quoted in the README
> erroneously sums the horizontal rear EDF into vertical lift. This is only valid
> if the rear EDF thrust vector is redirected downward — which it is not in the
> current fixed-longitudinal installation.

### 2.2 AUW and hover T/W (Phase 2–6 budget EDFs)

| Component | Mass (g) |
|---|---|
| Airframe + foam fill | 1 350 |
| 4× nacelle 50 mm EDFs + motor mounts | 300 |
| 1× 120 mm fuselage EDF + mount | 350 |
| 4× 50–60 A BLHeli32 nacelle ESCs | 220 |
| 1× 40 A BLHeli32 fuselage ESC | 40 |
| 2× tilt servos (≥ 25 kg·cm @ 6 V) | 160 |
| 3× nozzle servos (SG90 class) | 30 |
| 8× PocketBeagle 2 Industrial SBC | 102 |
| 8× Cape-A-2 / Cape-B-2 avionics capes | 400 |
| 4× XCVR-49MHZ-2 transceiver boards | 80 |
| Wiring harness + connectors + hardware | 260 |
| PWR-DIST-1 power distribution board | 80 |
| 6S 4 000 mAh LiPo (baseline battery) | 410 |
| **AUW (estimated)** | **~3 782 g** |

**VTOL hover thrust (Phase 2–6):** ~1 822 g
**VTOL T/W (Phase 2–6):** 1 822 / 3 782 = **0.48 : 1**

> **CONCLUSION: The Phase 2–6 50 mm budget EDF configuration CANNOT achieve
> VTOL. Thrust is less than half of AUW. First flights must be conventional
> fixed-wing or hand-launched with nacelles at 0° (cruise), transitioning
> gradually as phase 7 hardware is installed.**

### 2.3 AUW and hover T/W (Phase 7 — XRP 80 mm EDFs)

Replace 4× budget 50 mm EDFs + 4× 50–60 A ESCs with:
- 4× Changesun XRP 3660-2700KV 80 mm 6S EDFs (adds ~20 g/unit vs. budget = +80 g total)
- 4× Hobbywing Platinum PRO V4 120 A ESCs (adds ~20 g/unit vs. budget = +80 g total)

Adjusted AUW: 3 782 + 160 = **~3 942 g**

**VTOL hover thrust (Phase 7 XRP):** ~5 300 g
**VTOL T/W (Phase 7):** 5 300 / 3 942 = **1.34 : 1**

Minimum recommended T/W for stable VTOL hover: **1.5 : 1** (allows attitude control margin
and 15% headroom against gusty conditions).

> **CONCLUSION: Phase 7 XRP 80 mm EDFs achieve 1.34 : 1 hover T/W — below the
> recommended 1.5 : 1 minimum. VTOL is marginally possible in calm conditions
> with the 6S 4 000 mAh battery. Any heavier battery or payload degrades this further.**

### 2.4 Path to ≥ 1.5 : 1 hover T/W with 80 mm EDFs

Required nacelle thrust: 3 942 × 1.5 = 5 913 g → 5 913 / 4 EDF = **1 478 g per EDF**

The XRP 3660-2700KV 80 mm 6S achieves ~1 325 g per EDF (spec). Gap = 153 g/EDF.

Options (in order of preference):

| Option | ΔMass | ΔThrust | Net T/W | Feasibility |
|---|---|---|---|---|
| A: Battery reduction — 6S 2 500 mAh (−120 g) | −120 g | 0 | 5 300 / 3 822 = **1.39** | Limited flight time |
| B: EDF upgrade to higher KV (3000KV on same 80mm fan) | ~0 | +120 g/EDF | 5 780 / 3 942 = **1.47** | Requires new motor + rewinding ESC demag |
| C: 6S 4P (4 cells in parallel — 14.8V tap) on rear EDF, free phase for nacelles | complex | — | — | Not recommended |
| D: Nacelle EDF to 12-blade fan at same motor (Changesun 80mm 12-blade kit) | ~0 | +80 g/EDF | 5 620 / 3 942 = **1.43** | Bolt-on, recommended first step |
| E: CF-PETG shell infill reduction to save 150 g airframe | −150 g | 0 | 5 300 / 3 792 = **1.40** | Structural risk — analyse first |

**Recommended immediate actions:**
1. Install 12-blade fan upgrade on XRP 80 mm EDFs (Option D) — easiest, ~+80 g/EDF thrust
2. Reduce battery to 6S 3 000 mAh (−80 g vs. 4 000 mAh) during VTOL proving flights
3. Combined: T/W ≈ 5 620 / (3 942 − 80) = **1.46** — very close to the 1.5 target

### 2.5 Rear EDF VTOL contribution

The rear 120 mm EDF currently provides zero VTOL lift. If a variable-deflection
duct or "bucket" thrust reverser is added:

- At 45° deflection angle: vertical component = 3 500 × sin(45°) = ~2 475 g
- Combined with XRP nacelles (5 300 g): total = 7 775 g
- T/W = 7 775 / 3 942 = **1.97 : 1** — excellent VTOL margin with minimal ESC cost increase

This is the recommended long-term architectural improvement for confident VTOL.
The "variable-area nozzle" (iris mechanism) Rev O already fitted to all three EDF exits
provides the mechanical basis; only the duct itself needs a deflection vane or bucket.

---

## 3. Electrical Power Budget

### 3.1 EDF / ESC loads at 22.2 V nominal (6S)

| Designator | Description | Peak current (A) | Cruise current (A) | Power peak (W) |
|---|---|---|---|---|
| ESC1 | Port-fwd nacelle EDF (50 mm budget) | 55 | 28 | 1 221 |
| ESC2 | Port-aft nacelle EDF (50 mm budget) | 55 | 28 | 1 221 |
| ESC3 | Stbd-fwd nacelle EDF (50 mm budget) | 55 | 28 | 1 221 |
| ESC4 | Stbd-aft nacelle EDF (50 mm budget) | 55 | 28 | 1 221 |
| ESC5 | Rear fuselage 120 mm EDF | 40 | 20 | 888 |
| **Subtotal EDF** | | **260 A** | **132 A** | **5 772 W** |

Phase 7 XRP upgrade: ESC1–4 each rise to 84 A peak / 55 A cruise. New totals:
peak 376 A, cruise 240 A, peak power 8 347 W.

### 3.2 Avionics loads (5 V regulated)

| Subsystem | Count | Current per unit (A @ 5V) | Total (A @ 5V) |
|---|---|---|---|
| PocketBeagle 2 Industrial | 8 | 0.5 | 4.0 |
| Cape-A-2 / Cape-B-2 peripherals | 8 | 0.4 | 3.2 |
| XCVR-49MHZ-2 transceiver | 4 | 0.2 | 0.8 |
| Misc (LEDs, TPM, sensors) | — | — | 0.5 |
| **Avionics total** | | | **8.5 A @ 5 V = 42.5 W** |

UBEC input current (at 22.2 V, 90% efficiency): 42.5 / (22.2 × 0.9) = **2.1 A**
Deploy 2× 10 A UBECs in active parallel → 5.25 A each (well within rating)

### 3.3 Servo loads (5 V)

| Servo | Count | Stall current (A) | Operating current (A) |
|---|---|---|---|
| Nacelle tilt (≥ 25 kg·cm) | 2 | 3.0 | 0.8 |
| Nozzle (SG90) | 3 | 0.5 | 0.2 |
| **Servo total** | | **7.5 A** | **2.2 A** |

Servo power from UBEC output (+5 V rail). Peak overlap (both nacelle tilt servos stall
simultaneously): 6.0 A — within UBEC capacity.

### 3.4 Total system power summary

| Rail | Peak draw | Continuous | Source |
|---|---|---|---|
| VBAT (22.2 V main) | 260–376 A (EDF) + 2.1 A (BEC in) | 132–240 A | 6S LiPo |
| +5 V avionics | 8.5 A | 8.5 A | UBEC1 + UBEC2 |
| +5 V servo | 7.5 A peak | 2.2 A | UBEC (servo tap) |
| **Fuse rating required** | **400 A ANL (EDF phase 2–6); 500 A ANL (phase 7)** | | |

---

## 4. Battery Sizing

### 4.1 Phase 2–6 sizing (budget 50 mm EDFs, conventional flight only)

Target: 8 minutes at 60% throttle (cruise, nacelles horizontal)
Estimated cruise current: 132 A × 0.6 throttle factor ≈ **80 A**

Capacity = 80 A × (8/60) h = **10.7 Ah → use 6S 10 000 mAh**

However, the 6S 10 000 mAh weighs ~950 g, increasing AUW to ~4 320 g, further
degrading VTOL impossibility in Phase 2–6. For Phase 2–6 (conventional flight):
this is acceptable.

**Phase 2–6 battery recommendation:** 6S 10 000 mAh LiPo, 60C, XT90, ~950 g

### 4.2 Phase 7 sizing (XRP 80 mm EDFs, VTOL-capable)

Target: 5 minutes VTOL hover + 3 minutes transition/cruise
VTOL hover current: 4 × 84 A ESC = 336 A peak → derate 30% for actual hover ≈ **235 A**
Cruise current: 4 × 55 A nacelle + 20 A rear ≈ **240 A**

Total Ah at VTOL: 235 A × (5/60) h = 19.6 Ah
Total Ah at cruise: 240 A × (3/60) h = 12.0 Ah
Total mission: ~31.6 Ah

A single 6S pack cannot realistically reach 32 Ah at flight weight. Options:
- 2× 6S 16 000 mAh in parallel (1 400 g each = 2 800 g added) → AUW rises to ~6 700 g → T/W collapses
- 1× 6S 8 000 mAh, accept ~4 min VTOL hover: **recommended Phase 7 baseline**

**Phase 7 battery recommendation:** 1× 6S 8 000 mAh LiPo, 100C (800 A burst), ~720 g, XT90/AS150

### 4.3 Battery connector selection

| Battery capacity | Peak current | Connector |
|---|---|---|
| ≤ 6 000 mAh / ≤ 150 A continuous | 150 A | XT90 (90 A continuous, 120 A burst) |
| 6 000–12 000 mAh / 150–300 A | 300 A | AS150 (150 A cont., 200 A burst) |
| ≥ 12 000 mAh / ≥ 300 A | 400 A | XT150 or Anderson SB175 |

**Phase 7 with 8 000 mAh (376 A peak EDF):** use **AS150 or XT150** on battery leads.

---

## 5. Wire Gauge Sizing

All ratings at 60°C ambient, continuous duty, silicone insulation (105°C rated).

| Segment | Peak current | Required AWG | Recommended | Length |
|---|---|---|---|---|
| Battery to PDB main bus | 260–376 A | 2/0 AWG | 4/0 AWG silicone (double conductor) | ≤ 150 mm |
| PDB to nacelle ESC (one EDF) | 55–84 A | 10 AWG | 8 AWG silicone | ≤ 250 mm |
| PDB to rear EDF ESC | 40 A | 12 AWG | 10 AWG silicone | ≤ 350 mm |
| ESC to EDF motor phase leads | 55–84 A | 10 AWG | 10 AWG silicone | ≤ 400 mm |
| UBEC output to avionics bay | 5 A | 22 AWG | 20 AWG silicone | ≤ 600 mm |
| Servo power | 8 A peak | 20 AWG | 18 AWG silicone | ≤ 500 mm |
| Signal / telemetry | < 1 A | 28 AWG STP | Belden 9367 STP | ≤ 600 mm |
| PGND bonding strap | fault current | MIL-B-5087B | 19 mm flat braid (below) | ≤ 250 mm/segment |

---

## 6. ESC Selection

### 6.1 Phase 2–6 (50 mm budget EDFs)

| Position | EDF current | ESC model | Rating | Cost ea. |
|---|---|---|---|---|
| Each nacelle EDF (×4) | ≤ 55 A peak | Generic BLHeli32 60 A 6S | 60 A / 6S | ~$20 |
| Rear fuselage EDF | ≤ 40 A peak | Generic BLHeli32 40 A 4S | 40 A / 4S | ~$15 |

### 6.2 Phase 7 (XRP 80 mm EDFs)

| Position | EDF current | ESC model | Rating | Cost ea. |
|---|---|---|---|---|
| Each nacelle EDF (×4) | 84 A peak, 55 A cont. | Hobbywing Platinum PRO V4 120A | 120 A / 6S, BDSHOT | ~$65 |
| Rear fuselage EDF | ≤ 40 A | BLHeli32 40 A 4S (unchanged) | 40 A / 4S | ~$15 |

All nacelle ESCs programmed to:
- Current limit: 100 A (leaves 20 A margin)
- Timing: 15° auto-advance
- Demag compensation: high
- BDSHOT telemetry: enabled (FC reads RPM + current + temperature)

---

## 7. Low-Impedance PGND Bonding Strap

### 7.1 Requirement

All four avionics bay Faraday enclosures (bays A, B, D, E) must be bonded to a
common chassis PGND reference with a total point-to-point resistance of ≤ 2.5 mΩ
per MIL-B-5087B Class H.

### 7.2 Strap specification

| Parameter | Specification |
|---|---|
| Standard | MIL-B-5087B Class H bonding — aircraft internal bond |
| Material | 19 mm × 0.127 mm tinned copper flat braid (equivalent to ~1/0 AWG) |
| Part number | Belden 8663 (19 mm flat copper braid) or equivalent |
| Surface finish | Tin-plated copper; no aluminium |
| Length per segment | ≤ 250 mm bay-to-bay (keel run) |
| DC resistance per segment | ≤ 0.5 mΩ (typ. 0.35 mΩ @ 250 mm) |
| Total chain resistance | 4 segments × 0.5 mΩ = ≤ 2.0 mΩ (meets Class H) |
| Terminal | Crimped + soldered M3 tin-plated copper lug both ends |
| Fastener | M3 × 6 SS pan-head screw into captured M3 brass insert in bay PGND pad |
| Torque | 0.5 N·m (M3 into brass) |

### 7.3 Topology

```
BAY A PGND pad
    │
    ├─ strap (≤250mm) ─┤
                       BAY B PGND pad
                           │
                           ├─ strap (≤250mm) ─┤
                                              BAY D PGND pad
                                                  │
                                                  ├─ strap (≤250mm) ─┤
                                                                     BAY E PGND pad
                                                                         │
                                                                         ├─ strap (≤250mm) ─┐
                                                                                            │
                                                                                      KEEL CHASSIS STAR
                                                                                            │
                                                                                      BATTERY (−) TERMINAL
                                                                                      (single-point ground)
```

- **Single-point earth:** Battery (−) terminal is the chassis star point. All PGND
  straps terminate there. No parallel return paths between avionics bays.
- **Separation from signal GND:** The PGND (chassis) and GND (signal return) are
  bonded at one point only — at the PWR-DIST-1 board battery (−) terminal. Elsewhere
  they are separate rails.
- **Strap routing:** Run all straps along the keel rib (inside the belly), away from
  EDF motor phase leads and ESC output wires. Minimum 25 mm separation from power wires.

### 7.4 PGND bond point on Faraday enclosures

Each bay's Faraday enclosure has a designated bond pad:
- M3 × 10 mm machine screw into the bay mounting plate boss
- 3M 1181 copper foil tape lap-folded over the boss provides electrical continuity
  from the foil liner to the lug terminal
- Bond resistance ≤ 0.5 mΩ from foil liner to strap lug (verify with Kelvin 4-wire milliohm meter)

---

## 8. Weight and Balance

### 8.1 CG target

**Longitudinal CG target: 190 mm aft of nose tip** (from existing rev build guides).
CG is maintained by adjusting the battery position on the keel rail.

### 8.2 Weight distribution of power system components

| Component | Mass (g) | Station (mm from nose) | Moment (g·mm) |
|---|---|---|---|
| 6S 8 000 mAh LiPo | 720 | 190 (adjustable) | 136 800 |
| PWR-DIST-1 PDB | 80 | 200 (fixed, keel mid) | 16 000 |
| 4× nacelle ESCs | 220 | 90 (wing root) | 19 800 |
| 1× rear EDF ESC | 40 | 490 (aft bay) | 19 600 |
| Bonding strap (keel) | 35 | 250 | 8 750 |
| **Subtotal** | **1 095** | CG contribution: 200 800 / 1 095 = **183 mm** | |

The power system CG at 183 mm is slightly forward of the 190 mm target — add 7 mm
of forward servo and wiring mass to the tail to compensate, or slide the battery
aft 10 mm.

### 8.3 Impact of battery change on CG

Each 10 mm aft shift of battery from the default rail position shifts CG by:
ΔCG ≈ (battery mass / AUW) × 10 mm = (720 / 3 942) × 10 = **1.8 mm aft**

Battery travel on the 50 mm adjustable keel rail: ±25 mm → ±4.6 mm CG travel.
This is sufficient to trim for normal payload variation.

---

## 9. PWR-DIST-1 Mounting

- **Location:** Keel at station 200 mm from nose, directly below the avionics bay
  stack centre. Mounted on M3 standoffs (10 mm) above keel rib.
- **Orientation:** Battery connector face pointing aft; avionics output connectors
  pointing port; ESC lead connectors pointing forward/starboard as routed.
- **Clearance:** Minimum 10 mm from any CF structural member; 25 mm from EDF motor
  phase leads.
- **Access:** Reachable through cargo bay belly plate (60 × 80 mm access cutout,
  secured with 4× M2.5 captive screws). Battery connection requires belly plate removal.

---

## Related Files

- `avionics/kicad/PWR-DIST-1.kicad_sch` — Power distribution board schematic
- `avionics/kicad/PWR-DIST-1.md` — PDB component list, PCB spec, connector assignments
- `avionics/kicad/CAPE-A-2.md` — Avionics cape (receives +5V from PWR-DIST-1)
- `avionics/kicad/CAPE-B-2.md` — Comms cape (receives +5V from PWR-DIST-1)
- `docs/PHASED_BUILD_GUIDE.md` — Build sequence, ESC commissioning, servo calibration

---

## References

1. README.md — Serenity UAV propulsion specification and AUW tables
2. MIL-B-5087B — Bonding, Electrical, and Lightning Protection for Aerospace Systems
3. NEC Table 310.15 — Ampacity of conductors (silicone insulation reference)
4. Hobbywing Platinum PRO V4 120A ESC Data Sheet
5. ACS758ECB-300B Data Sheet — Allegro MicroSystems
6. AUVSI: UAS Best Practices for Electrical Systems Design (2022)
