# Serenity UAV — Landing Gear Structural Analysis

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Revision:** R1 (2026-06-14)

---

## 1. Purpose and Requirements

This document provides the structural analysis and design rationale for the
Serenity UAV main landing gear.  The landing gear system must:

1. **Survive a 6 ft (1.829 m) vertical drop** onto hard level ground at
   design all-up weight (AUW) without cracking the hull shell.
2. **Absorb lateral loads** from not-quite-vertical landings (design case ±15°
   from vertical).
3. **Fail internally under overload** — if the leg is overstressed, the failure
   mode must be a defined sacrificial fuse element inside the leg/boss interface,
   not cracking of the cargo shell or hull boss.
4. **Be field-replaceable** using only common hand tools.

The landing gear system does NOT need to be reusable after a 6 ft drop.  The
legs may take permanent plastic set under the design drop; the hull must remain
undamaged.

---

## 2. Aircraft Data and Landing Geometry

### 2.1 All-Up Weight

| Configuration | AUW |
|---|---|
| Phase 5–10 (no aft EDF) | **6.10 lbm (2,768 g)** |
| Phase 11 (full system, design case) | **6.90 lbm (3,130 g)** |

The **Phase 11 AUW of 6.90 lbm (3,130 g) is the design case** — worst-case
load for the landing gear.

### 2.2 Landing Gear Configuration

- **4 × main legs** — flat-spring cantilever (CF-PETG), field-replaceable
  via M3 nylon shear bolts in a hull boss slot on the cargo belly.
- **4 × TPU feet** — TPU 95A, press-fit + 2× M3 screws.  Provides initial
  elastic cushioning and ground friction.
- **2 × rear skids** — integral to the horseshoe ring of the middle/rear
  section (Kaylee's room area); NOT field-replaceable without disassembly.
  The rear skids provide stability; primary structural energy absorption is
  by the 4 main legs.

### 2.3 CG Location and Load Split

The aircraft CG is estimated at approximately Y ≈ 290 mm from nose (hull
frame), near the forward avionics bays in the cargo section.  The 4 main
legs attach to the cargo belly in the range Y ≈ 20–100 mm from origin
(see `HULL_ATTACH_POS[]` in `landing_leg_assy.scad`).  The rear skids are
approximately Y ≈ 350 mm.

For a level landing, the CG is forward of the rear skids; the 4 main legs
carry the dominant load.  **Conservative design assumption: all kinetic
energy is absorbed by the 4 main legs; rear skids provide 0% contribution.**
This is the worst-case split for leg design.

---

## 3. Impact Velocity and Kinetic Energy

### 3.1 Free-Fall Velocity

From rest at height h = 6 ft (1.829 m = 72.0 in) above the ground:

```
v = √(2 g h)
  = √(2 × 386.09 in/s² × 72.0 in)
  = √55,597 in²/s²
  = 235.8 in/s  (19.65 ft/s, 5.99 m/s)
```

### 3.2 Total Kinetic Energy at Impact

```
KE_total = ½ m v²
         = ½ × (6.90 lbm / 386.09 lbm·in/lbf·s²) × 235.8² in²/s²
         = ½ × 0.01787 lbf·s²/in × 55,602 in²/s²
         = 496.8 in·lbf  (56.1 J)
```

### 3.3 Energy per Main Leg

With conservative assumption (4 legs, no rear skid contribution):

```
KE_per_leg = 496.8 / 4 = 124.2 in·lbf  (14.0 J) per leg
```

---

## 4. Flat-Spring Cantilever Leg Analysis

### 4.1 Leg Cross-Section

The leg is a hollow box tube (CF-PETG, 4 perimeters, 40% gyroid infill):

| Parameter | Value |
|---|---|
| Outer width | 22.0 mm (0.866 in) |
| Outer depth (spring direction) | 10.0 mm (0.394 in) |
| Wall thickness | 2.5 mm |
| Inner width | 17.0 mm |
| Inner depth | 5.0 mm |
| Printed E (CF-PETG, in-plane) | 5,500 MPa (800 ksi) conservative |
| Printed σ_yield (CF-PETG) | 55 MPa (7,977 psi) conservative |

Second moment of area about the neutral bending axis (resisting primary vertical loads):

```
I = (b × d³ - b_i × d_i³) / 12
  = (22 × 10³ - 17 × 5³) / 12
  = (22,000 - 2,125) / 12
  = 19,875 / 12
  = 1,656 mm⁴
```

### 4.2 Effective Spring Length

From parametric SCAD (`landing_leg_assy.scad`):

| Segment | Length |
|---|---|
| Foot socket (rigid, not spring) | 20 mm |
| Free cantilever spring zone | 145 mm |
| Boss insert stub (rigid, clamped) | 20 mm |
| **Total leg length** | **185 mm (7.28 in)** |

Effective cantilever length (free end to fixed end) = **145 mm**.

### 4.3 Spring Rate

For a cantilever beam with tip load:

```
k = 3 E I / L³
  = 3 × 5,500 N/mm² × 1,656 mm⁴ / (145 mm)³
  = 27,324,000 / 3,048,625
  = 8.96 N/mm  (51.2 lbf/in) per leg
```

### 4.4 Energy Absorbed to Peak Force

The spring absorbs energy quadratically with deflection.  To absorb the
full 14.0 J (14,000 N·mm) per leg:

```
½ k δ² = KE_per_leg
δ = √(2 × KE / k) = √(2 × 14,000 / 8.96) = √3,125 = 55.9 mm (2.20 in)
F_peak = k × δ = 8.96 × 55.9 = 500.9 N (112.6 lbf)
```

Peak deceleration:

```
g_peak = F_total / W
       = (4 legs × 500.9 N) / (3.130 kg × 9.81 m/s²)
       = 2,003.6 / 30.7
       = 65.3g
```

### 4.5 Maximum Bending Stress at Hull Boss

The leg is splayed 30° outboard from vertical (SPLAY_ANGLE = 30°).  For a
vertical landing load F_vertical per leg, the bending component at the boss:

```
F_bending = F_vertical × sin(SPLAY_ANGLE)
          = 500.9 × sin(30°)
          = 250.5 N

M_max (at boss root) = F_bending × L_eff
                     = 250.5 × 145
                     = 36,323 N·mm

c = d / 2 = 5.0 mm (distance from neutral axis to outer fibre)

σ_max = M × c / I
       = 36,323 × 5.0 / 1,656
       = 181,615 / 1,656
       = 109.7 MPa
```

**Conclusion:** σ_max = 109.7 MPa exceeds the conservative printed CF-PETG
yield stress of 55 MPa.  The leg **will plastically deform** at the design
6 ft drop load.  This is intentional — the leg is a sacrificial energy absorber.
Hull integrity is protected separately by the fuse mechanism (§7).

For reference, drops of approximately 3 ft (0.9 m) or less will keep the
leg within the elastic range:

```
Elastic limit: M_max = σ_yield × I / c = 55 × 1,656 / 5 = 18,216 N·mm
F_bend_elastic = 18,216 / 145 = 125.6 N → F_vert = 125.6 / sin(30°) = 251.2 N
KE_elastic = ½ × 251.2² / 8.96 = ½ × 7,050 = 3,525 N·mm per leg
             Total: 4 × 3,525 = 14,100 N·mm (1.55 ft drop elastic)
```

**Legs stay elastic for drops ≤ approximately 1.55 ft (0.47 m).  Drops
1.55–6 ft cause progressive plastic set.  Drops > 6 ft activate the fuse.**

---

## 5. Lateral Load Analysis (±15° Off-Vertical)

For a landing at 15° from vertical (tilt of impact direction):

```
F_vert_component   = F_per_leg × cos(15°) = 500.9 × 0.966 = 483.9 N
F_lateral_component = F_per_leg × sin(15°) = 500.9 × 0.259 = 129.7 N
```

### 5.1 Lateral Bending in the Wide Plane (resisting lateral loads)

The leg's wide dimension (22 mm) resists lateral loads perpendicular to the
primary spring direction.

```
I_lateral = (d × b³ - d_i × b_i³) / 12
          = (10 × 22³ - 5 × 17³) / 12
          = (106,480 - 24,565) / 12
          = 81,915 / 12
          = 6,826 mm⁴

M_lat = F_lateral × L_eff = 129.7 × 145 = 18,807 N·mm

σ_lat = M × c / I = 18,807 × 11 / 6,826 = 206,877 / 6,826 = 30.3 MPa
```

**σ_lat = 30.3 MPa < σ_yield = 55 MPa → lateral loads do NOT cause
additional yielding above the primary vertical load case.** ✓

### 5.2 Combined Stress Check

Using von Mises superposition (bending stresses orthogonal, no torsion):

```
σ_combined = √(σ_primary² + σ_lateral²)
           = √(109.7² + 30.3²)
           = √(12,034 + 918)
           = √12,952
           = 113.8 MPa
```

The combined stress is only 3.7% higher than primary alone — lateral
loading does not significantly worsen the primary drop case.  The leg
will still deform plastically on a 6 ft drop at 15° tilt, but the
failure mode remains distributed bending (not sudden fracture), because
CF-PETG has elongation at break of approximately 3–5% — above the 2%
strain reached at yield.

---

## 6. Foot Impact Cushioning

The TPU 95A foot (existing Thingiverse geometry, ≈78 × 98 × 9 mm) provides
initial cushioning at contact.  With 25% gyroid infill, the effective modulus
of the foot structure is approximately:

```
E_foot_eff ≈ 0.25 × E_TPU95A ≈ 0.25 × 35 MPa = 8.75 MPa (approximate)
A_foot ≈ 78 × 98 = 7,644 mm²
k_foot = E_eff × A / t = 8.75 × 7,644 / 9 ≈ 7,432 N/mm (approximate)
```

The foot is extremely stiff compared to the leg spring (k_leg = 8.96 N/mm).
The TPU foot absorbs energy primarily through rubber viscoelastic damping
(hysteresis), not through significant compression.  It provides ground
friction, surface compliance over gravel/rough terrain, and protects the
printed leg bottom from direct impact with hard surfaces.

**No credit is taken for foot energy absorption in the primary drop
analysis.** The conservative analysis (§4) attributes all energy to the
leg spring/plastic deformation.

---

## 7. Fuse Mechanism — Hull Boss Protection

### 7.1 Design Intent

The hull boss is cast in CF-PETG as an integral feature of the cargo belly
shell.  Under a crash that exceeds the 6 ft design drop (or any overload
scenario), the hull boss must NOT fracture or delaminate from the shell.
The fuse elements sacrifice before the hull.

### 7.2 Fuse Configuration

Three (3) M3 × 12 mm nylon (PA6) bolts pass through the leg boss insert
stub in the Y direction (through the 10 mm depth of the leg).  These bolts
are loaded in **single shear** across the leg–boss interface when an axial
overload lifts the leg relative to the hull boss slot.

### 7.3 Fuse Load Estimate

| Parameter | Value |
|---|---|
| Bolt material | Nylon PA6 (M3 × 12, DIN 912 equivalent, nylon grade) |
| Shear strength (PA6, per ASTM D638 Type I) | ≈ 40 MPa |
| Bolt core area (M3, major diameter 3.0 mm) | A = π × 3²/4 = 7.07 mm² |
| Shear force per bolt | 40 × 7.07 = 282.8 N (63.6 lbf) |
| 3 bolts total | **848 N (190.7 lbf) per leg** |

### 7.4 Margin Check

| Load case | Force per leg | Fuse state |
|---|---|---|
| 3 ft drop (elastic limit) | 251 N | No activation ✓ |
| 6 ft drop (design, Phase 11) | 501 N | No activation ✓ |
| Fuse trigger | **848 N (190.7 lbf)** | Bolts shear |
| Estimated hull boss fracture | > 2,000 N | Hull intact ✓ |

**Fuse activates at 1.69× the 6 ft design load**, well below the estimated
hull boss fracture load.  The hull boss is never at risk under the design drop.

> **Verification required:** The 40 MPa shear value is a literature value
> for PA6.  Actual printed nylon bolts, M3 dimensional accuracy, and bearing
> contact condition must be verified by shear test on representative samples
> before first flight.  See TODO.md §1.4.x landing gear test item.

### 7.5 Safety Cord (Leg Retention After Fuse)

After the fuse bolts shear, the leg is no longer fastened to the hull.  A
2 mm Dyneema SK75 safety cord (minimum break strength 750 N) threads through
the TETHER_D hole in the leg body and is anchored inside the airframe.  This
retains the detached leg to prevent it from:

- Contacting a spinning EDF or rotor system
- Falling into crowd or personnel
- Being lost for post-incident analysis

**Break strength check:** 750 N safety cord vs 848 N fuse force → the cord
must NOT be pulled taut during fuse activation (it is sized to retain the
free-falling leg mass of ≈ 0.04 lbm / 18 g, not to bear the crash load).
The cord is slack during normal operation; it only tensions after the bolts
shear and the leg is free.

---

## 8. Rear Skids

The two rear skids are built into the horseshoe ring of the middle section
(see `airframe/openscad/fuselage/middle_canonical_shell24.scad`).  They
must be reinforced with a CF rod (3 mm diameter, pultruded carbon fibre,
fitted into a printed channel) before first flight.  CF rod specification:

- Outer diameter: 3 mm
- Material: pultruded CF (unidirectional, ~130 GPa modulus)
- Length per skid: approximately 140 mm (rear EDF area to skid tip)
- Adhesive: thin cyanoacrylate (wicks into channel gap)

Rear skid structural analysis is deferred to the middle section integration
design document (TODO.md §1.1.4 rear skid CF rod open item).

---

## 9. Materials Specification

### 9.1 Leg Body (CF-PETG)

| Parameter | Value |
|---|---|
| Print material | CF-PETG (carbon-fibre reinforced PETG) |
| Layer height | 0.15 mm |
| Perimeters | 4 |
| Infill pattern | 40% gyroid |
| Print orientation | Upright (leg long axis = printer Z) |
| Post-process | None required |
| Estimated mass | ≈ 18 g per leg (4 legs = 72 g total) |

Print upright so that the CF fibers run parallel to the leg long axis,
maximizing axial tensile/compressive strength.  In-plane modulus ≈ 5.5 GPa
outperforms the through-layer modulus (≈ 2.5 GPa); upright print exploits
this advantage.

### 9.2 Hull Boss (CF-PETG)

| Parameter | Value |
|---|---|
| Print material | CF-PETG |
| Layer height | 0.15 mm |
| Perimeters | 4 |
| Infill | 40% gyroid |
| Integration | Integral to `cargo_sect_shell24.scad` belly region |
| Boss slot tolerance | LEG_W +0.4 mm × LEG_D +0.4 mm (0.2 mm clearance each side) |

### 9.3 Fuse Bolts

| Parameter | Value |
|---|---|
| Fastener | M3 × 12 mm nylon socket head cap screw, PA6 |
| Quantity per leg | 3 |
| Installation torque | Finger-tight + 1/4 turn (do not exceed; nylon strips easily) |
| Replacement interval | After each activation (shear) or every 50 hard landings |

### 9.4 TPU Feet

| Parameter | Value |
|---|---|
| Material | TPU 95A |
| Layer height | 0.2 mm |
| Infill | 25% gyroid |
| Fasteners | 2× M3 × 10 mm stainless SHCS per foot |
| Source | Existing Thingiverse geometry (misubisu, CC BY 4.0) or regenerate from SCAD |

### 9.5 Safety Cord

| Parameter | Value |
|---|---|
| Material | Dyneema SK75 |
| Diameter | 2.0 mm |
| Break strength | ≥ 750 N (168 lbf) |
| Length per leg | ≈ 400 mm (allows leg to hang clear of rotors) |
| Termination (leg end) | Loop through TETHER_D hole, overhand knot |
| Termination (airframe end) | Loop around M3 anchor post printed in boss interior |

---

## 10. Bill of Materials (per aircraft, 4 legs)

| Item | Qty | Description |
|---|---|---|
| Leg body | 4 | CF-PETG, per SCAD PART="leg" |
| TPU foot | 4 | TPU 95A, existing Thingiverse STL or SCAD |
| M3 × 12 nylon SHCS | 12 | Fuse bolts (3 per leg) |
| M3 × 10 SS SHCS | 8 | Foot retention (2 per foot) |
| Dyneema SK75, 2 mm | 1.6 m | Safety cord (4 × 400 mm) |
| M3 anchor post | 4 | Printed in hull boss interior (integral) |
| 3 mm CF rod | 280 mm | Rear skid reinforcement (2 × 140 mm) |
| CA thin | — | CF rod adhesive, rear skids |
| Spare fuse bolt set | 12 | Replacement M3 nylon (one full set spare per aircraft) |

---

## 11. Assembly Procedure

1. **Hull boss preparation:** Print `PART="boss"` and verify the leg insert slot
   dimensions (LEG_W + 0.4 mm × LEG_D + 0.4 mm).  Integrate the boss geometry
   into `cargo_sect_shell24.scad` belly (subtract boss slot, add boss walls).

2. **Leg preparation:** Print `PART="leg"` upright.  Verify M3 fuse holes
   (3 clearance holes through depth) and foot socket cavity.

3. **Safety cord installation:** Thread 400 mm Dyneema through TETHER_D hole
   in each leg body.  Tie overhand knot at leg end.  Route cord up through boss
   safety pass-through hole into airframe interior.  Anchor to M3 post in boss.

4. **Leg insertion:** Slide leg boss insert stub up into hull boss slot from below.
   Align M3 holes.  Install 3× M3 nylon shear bolts — finger-tight + 1/4 turn only.

5. **Foot installation:** Press TPU foot over leg foot socket (bottom end).
   Install 2× M3 SS SHCS from the foot sole up through leg bottom flange.
   Torque to 0.3 N·m.

---

## 12. Field Replacement Procedure

After fuse activation (crash landing):

1. Locate the detached leg on the safety cord.
2. Remove the 3 sheared M3 nylon bolts (drill out or use push-pin for remnants).
3. Slide the damaged leg out of the hull boss slot.
4. Inspect hull boss slot for damage; if slot walls are cracked, repair with
   CF-PETG epoxy fill before re-installation.
5. Install replacement leg per Assembly Procedure steps 3–5 above.
6. Inspect TPU foot; replace if torn or deformed past 20% compression set.

**Required tools:** 2.5 mm hex key (M3), 3 mm push-pin or 3.3 mm drill
(bolt removal), finger pressure for TPU foot.

---

## 13. Open Items and Verification Requirements

| ID | Item | Blocks |
|---|---|---|
| LG-01 | Shear-test 10 samples of M3 × 12 PA6 nylon at representative cross-section; confirm fuse load 848 ± 150 N | First flight |
| LG-02 | Integrate hull boss geometry into `cargo_sect_shell24.scad`; run DRC mesh check | Hull print |
| LG-03 | Add CF rod channel to `middle_canonical_shell24.scad` rear skid section | Hull print |
| LG-04 | Verify HULL_ATTACH_POS[] in SCAD against cargo belly contour in FreeCAD assembly | Hull print |
| LG-05 | Regenerate `leg_body_r1.stl` and `hull_boss_r1.stl` via OpenSCAD; verify mesh watertight | STL export |
| LG-06 | Conduct drop test at 3 ft (elastic) and 6 ft (design) on prototype leg mounted to a mass-equivalent fixture | Pre-flight |
| LG-07 | Confirm avionics Faraday enclosures rated for ≥ 100g shock (required by 65.3g peak) | PCB fab |
