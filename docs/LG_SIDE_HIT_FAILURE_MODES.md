# Landing Gear Side-Hit Failure Modes

**Status:** analysis of the gear **as built** on PR #276 (fore swing −65°, aft +28°, baseline thigh).  The owner is not changing the gear now (2026-11-02).  This document answers **how and when to expect a failure**, and so what will likely need repair or replacement after one.

**Scope (owner 2026-11-02):** any nacelle ground strike is a **crash**, not normal operations.  The co-strike cases predict the damage to expect after such a crash; they are not an operating envelope or a technique to use intentionally.
**Tool:** `tools/lg_side_hit_study.py` (reproducible; all numbers below come from one run).
**AI note:** analysis by Claude Opus 5.5 (Anthropic) under the direction of Stab-Rabbit-coding.  No independent review agents were dispatched.

> **ENGINEERING REVIEW REQUIRED.**  A qualified engineer must review and accept every figure here before it is used to accept risk to life or safety.

## 1. Answer first

| Event | Failure | When |
|---|---|---|
| Level landing, any drop up to the 4 ft crash case | No thigh failure.  At the crash case the **ductile fuses fire** by design: the gear is scrap and must be replaced. | Fuses fire at the plateau, 1,218 N/leg (the 4 ft crash case; spring limit 626 N/leg for 1.5 ft). |
| **One-pair (side) landing, crash energy** | **Fore thigh breaks out-of-plane** (side bending + torsion at the thigh root) | Bank ≥ **10.4°** (fore leg); the aft leg follows at ≥ **21.8°**. |
| One-pair landing, ordinary 1.5 ft | Fore thigh reaches UTS only at bank ≥ **35.0°**, which is practically only in a nacelle co-strike. | Aft thigh does not reach UTS at any bank. |
| **Gear + nacelle co-strike, crash** | **Fore thigh breaks** (1.54–1.96 × UTS).  The nacelle takes 1.3–6.5 kN. | Every tilt (0/45/90/135°). |
| Gear + nacelle co-strike, low energy (1.5 ft sink) — still a crash | **Fore thigh at or near break** (0.79–1.01 × UTS; breaks at tilt 0°).  The nacelle takes 0.9–4.1 kN. | Every tilt; worst at 0° (cruise attitude). |

**The weak link in a side hit is the fore thigh.**  Its −65° swing plane faces the lateral load almost edge-on: 91 % of a side load acts out of plane, against 47 % on the aft leg.  The leg force is capped by the fuse plateau, so the failure is set by **bank angle, not drop height**: once the fuse is on its plateau, a harder drop does not raise the thigh stress; a larger bank does.  The hip pin (4,241 N double shear) never governs.  The intended failure order holds: leg first, then mount, then hull.

## 2. Cases and geometry

Port side shown; starboard is the exact mirror.  Ground = the sole plane.  Feet (contact centres):
- fore-port (88.8, 217.2), az −65°;
- aft-port (148.2, 443.2), az +28°.

Mass: heaviest ledger case 6.253 kg (13.79 lbm), CG (0.6, 353.9, 157.3).

- **Case A, one-pair landing.**  The aircraft lands banked port-down on the two port feet.
- **Case B, co-strike.**  The bank at which the port feet and the port nacelle touch together.  It is found from the real nacelle mesh (`nacelle_port_64mm.stl`), rotated about the spar axis (Y 339.4, Z 146.85).  Tilt convention as in `landing_gear_ground_clearance.py`: 0° = cruise, 90° = nozzle straight down.

| Nacelle tilt | Co-strike bank | Nacelle contact point | Arm, gear / nacelle (mm) |
|---|---|---|---|
| 0° (cruise) | 35.5° | intake lip, (289.5, 222.0) | 6 / 199 |
| 45° | 30.5° | (281.1, 379.8) | 24 / 168 |
| 90° (hover) | 23.8° | nozzle region, (275.9, 318.2) | 46 / 202 |
| 135° | 27.6° | (269.1, 300.4) | 34 / 187 |

At every co-strike bank the hull, gear box and wing stay **75–84 mm clear**: the nacelle and the feet are the only contacts.  The side tip-over angle is 37.4°, so a 0° co-strike happens only just short of tip-over.

## 3. Results

### 3.1 Critical bank, per leg (force-limited: independent of drop height)

| Load | Leg | Level σ_vm | Exceeds 27.5 MPa at | Reaches UTS 85 MPa at |
|---|---|---|---|---|
| Ordinary (626 N) | fore −65° | 26.0 MPa | 1.0° | 35.0° |
| Ordinary (626 N) | aft +28° | 26.0 MPa | 1.9° | never |
| Crash (1,218 N) | fore −65° | 50.6 MPa | 0° | **10.4°** |
| Crash (1,218 N) | aft +28° | 50.6 MPa | 0° | **21.8°** |

### 3.2 One-pair landing, crash plateau

| Bank | Fore σ_vm (in / out / τ) | Aft σ_vm (in / out / τ) |
|---|---|---|
| 5° | 66.5 (50.4 / 14.5 / 8.1) | 58.4 (50.4 / 7.5 / 4.2) |
| 10° | 83.6 (49.8 / 29.0 / 16.2) | 66.4 (49.8 / 15.0 / 8.4) |
| 15° | 101.1 (48.9 / 43.2 / 24.1) | 74.5 (48.9 / 22.4 / 12.5) |
| 20° | 118.3 (47.6 / 57.0 / 31.9) | 82.2 (47.6 / 29.5 / 16.5) |
| 25° | 134.9 (45.9 / 70.5 / 39.4) | 89.6 (45.9 / 36.5 / 20.4) |
| 30° | 150.7 (43.8 / 83.4 / 46.6) | 96.5 (43.8 / 43.2 / 24.2) |

All values in MPa.

### 3.3 Co-strike dynamics

Nacelle contact stiffness is unknown, so it is swept over 100, 300 and 1,000 N/mm.  Gear energies are for the port pair.

| Tilt | Drop | Nacelle peak (N) | Nacelle energy (J) | Gear pair energy / stroke | Worst leg σ_vm / UTS |
|---|---|---|---|---|---|
| 0° | 1.5 ft | 979 – 3,787 | 4.8 – 7.2 | 18.9 – 9.8 J / 15.1 – 7.9 mm | fore 1.01 |
| 0° | 4 ft | 1,502 – 6,057 | 11.3 – 18.3 | 53.7 – 28.7 J / 22.1 – 11.8 mm | fore 1.96 |
| 45° | 1.5 ft | 1,009 – 4,117 | 5.1 – 8.5 | 17.7 – 7.9 J / 14.1 – 6.3 mm | fore 0.92 |
| 45° | 4 ft | 1,526 – **6,549** | 11.6 – **21.4** | 50.8 – 24.2 J / 20.9 – 9.9 mm | fore 1.79 |
| 90° | 1.5 ft | 859 – 3,605 | 3.7 – 6.5 | 16.2 – 7.2 J / 12.9 – 5.8 mm | fore 0.79 |
| 90° | 4 ft | 1,293 – 5,723 | 8.4 – 16.4 | 46.6 – 22.1 J / 19.1 – 9.1 mm | fore 1.54 |
| 135° | 1.5 ft | 931 – 3,832 | 4.3 – 7.3 | 17.1 – 7.6 J / 13.6 – 6.1 mm | fore 0.87 |
| 135° | 4 ft | 1,405 – 6,093 | 9.9 – 18.6 | 49.1 – 23.3 J / 20.2 – 9.6 mm | fore 1.68 |

A stiffer nacelle takes a larger share and a higher peak.  The worst nacelle load is at **45° tilt** (transition attitude).  The worst leg case is **0° tilt**, at the largest bank.

## 4. What fails, in order, in a banked hard landing (repair expectations)

1. **Spring row yields and the ductile fuses fire** at the plateau, by design.  The leg force is now capped at 1,218 N.
2. **Fore thigh root fails** if the bank exceeds about 10° (crash energy).  Failure is out-of-plane bending plus torsion at the thigh root, the hub end of the twin cylinders.
3. **Aft thigh root** fails beyond about 22° bank.
4. **Nacelle strike (crash)** happens beyond about 24–36° bank, depending on tilt.  It puts 1–6.5 kN through the nacelle shell, trunnion and tilt spar.  **That load path has no strength check yet** (see §6), so which of those parts is damaged is not yet predicted.

**Expect after a banked crash:** replace the corner cartridge(s) whose fuses fired.  Replace the fore thigh(s) if the bank exceeded about 10°.  After any nacelle strike, inspect and likely replace the nacelle shell, nozzle flaps, trunnion and tilt-spar joint on that side.

The hip pins (4,241 N) and the hull keep their margin throughout.

## 5. Method and assumptions

- **Dynamics.**  Two-contact planar rigid body in the roll plane about the port feet line.  The gear is a constant-force (plateau) pair; the nacelle is an elastic contact.  This is `tail_strike_requirement.co_strike()` (plan 2026-10-31-002 KTD4, REF-NCEES-009), with sink speed √(2gh).
- **Leg forces.**  From `landing_gear_r6_sizing.wire_schedule()` at the ledger AUW.  Ordinary = spring-row limit, F_leg × P_spring / P_wire.
- **Thigh stress.**
  - The ground reaction is resolved into the body frame at bank φ.
  - In-plane M = R cos φ · R_H (80 mm) on Z = 1,925 mm³ (the sizing basis).
  - The lateral force R sin φ is split by swing azimuth: |sin az| acts out of plane.  Its moment arm is the hip height (118 mm), split into bending (cos 48.2° on S = 520.6 mm³, twin Ø14/Ø6) and torsion (sin 48.2°, conservatively on one cylinder).
  - Combined with von Mises.
  - The relief from the inboard lateral force on the in-plane moment is ignored (conservative).
- **Strength.**  PA 602-CF UTS 85 MPa **in XY only** (datasheet).  There is **no Z value**: a leg printed with the bending stress across layers may break lower.  The sizing tool's 27.5 MPa (CF-PETG yield/2) is shown for reference.
- **Roll inertia.**  An estimate: k = 133 mm, from 2 × 937 g nacelles at X 228.5 plus the remainder at k 55 mm.  The ledger has no roll inertia.
- **Ground contact.**  Normal reaction only; no side-slip friction.  Friction adds lateral load and lowers every critical bank.  Contact is at the foot centres.  The aft toe tip is the first rigid contact; the canonical ankle pivots so the pad seats.  If the ankle does not articulate, the contact line moves outboard by up to 43 mm.

## 6. Open items this exposes

- **Nacelle / trunnion / tilt-spar strength under a 1–6.5 kN ground strike: not checked.**  Needed to predict which of those parts a nacelle-strike crash damages (repair planning).  It is not an operating case.  Testing the nacelle contact stiffness would pin the 100–1,000 N/mm sweep.
- **PA12-CF strength through the layers (Z) and in impact.**  Needed to turn "UTS (XY)" into a real failure prediction.  Question for 3D Systems is in the plan.
- The `LANDING_GEAR_ANALYSIS.md` lateral case (163 N) is stale; the sizing tool now gives 308 N.  The sizing gate still lacks this combined check (see the PR #276 review).
