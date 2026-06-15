# Serenity UAV — Landing Gear Structural Analysis

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Revision:** R1.1 (2026-06-15) — Redesign to 4-strut pyramid geometry

> **Rev R1 (2026-06-14)** flat-plate cantilever design superseded.
> Key impact numbers (§3) carry forward unchanged.

---

## 1. Purpose and Requirements

This document provides the structural analysis and design rationale for the
Serenity UAV main landing gear.  The landing gear system must:

1. **Survive a 6 ft (1.829 m) vertical drop** onto hard level ground at
   design all-up weight (AUW) without cracking the hull shell.
2. **Absorb lateral loads** from not-quite-vertical landings (design case ±15°
   from vertical).
3. **Fail internally under overload** — if a leg assembly is overstressed the
   failure mode must be a defined sacrificial element inside the assembly, not
   cracking of the cargo shell or hull boss.
4. **Be field-replaceable** using only common hand tools.
5. **Provide 3-D lateral stability** — legs must resist tipping loads in
   both the hull-X (lateral) and hull-Y (fore-aft) directions.

The landing gear does NOT need to be reusable after a 6 ft drop.

---

## 2. Aircraft Data and Landing Geometry

### 2.1 All-Up Weight

| Configuration | AUW |
|---|---|
| Phase 5–10 (no aft EDF) | **6.10 lbm (2,768 g)** |
| Phase 11 (full system, design case) | **6.90 lbm (3,130 g)** |

The **Phase 11 AUW of 6.90 lbm (3,130 g) is the design case**.

### 2.2 Landing Gear Configuration (Rev R1.1)

- **4 × main leg assemblies** — 4-strut pyramid (CF-PETG arm struts + PETG
  junction hub + CF-PETG column), one at each cargo belly corner.
- **4 × hull boss cylinders per leg assembly** (16 total) — CF-PETG, integral
  to the cargo belly shell.
- **4 × TPU 95A foot pads** — one per assembly; friction and surface compliance.
- **2 × rear skids** — integral to the horseshoe ring of the middle section; NOT
  produced by `landing_leg_assy.scad`.

### 2.3 Pyramid Geometry

Each leg assembly comprises:
- 4 hull boss cylinders (BOSS_OD = 22 mm) arranged in a 2 × 2 grid at
  Z = 0 (cargo belly), spaced SPREAD_X = 40 mm laterally and SPREAD_Y = 60 mm
  fore-aft, centred on the corner position.
- 4 arm struts (STRUT_OD = 12 mm, wall = 2 mm, CF-PETG) radiating from the
  4 boss tops inward and downward to a junction hub at Z = −JUNCT_Z = −85 mm.
- 1 vertical column (COL_OD = 18 mm, wall = 2.5 mm, CF-PETG) from junction
  hub to foot pad top at Z = −(JUNCT_Z + COL_H) = −145 mm.
- 1 TPU 95A foot pad (FOOT_H = 12 mm) at ground contact, Z = −157 mm.

**Total ground clearance (cargo belly to sole):** 157 mm (6.2 in).

---

## 3. Impact Velocity and Kinetic Energy

*(Numbers unchanged from Rev R1 — carry forward.)*

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

### 3.3 Energy per Leg Assembly

Conservative assumption: 4 leg assemblies absorb all energy, rear skids 0%:

```
KE_per_assy = 496.8 / 4 = 124.2 in·lbf  (14.0 J) per assembly
```

---

## 4. Pyramid Strut Analysis

### 4.1 Strut Geometry

Each arm strut connects a hull boss at Z = 0 to the junction hub at Z = −85 mm.

Boss offsets from hub centre (local corner frame, outboard-fore example):

```
Δx = SPREAD_X / 2 = 20 mm (outboard in hull X)
Δy = SPREAD_Y / 2 = 30 mm (fore = hull −Y direction)
Δz = JUNCT_Z      = 85 mm (upward from hub to boss)
```

| Parameter | Value |
|---|---|
| Strut length (outboard-fore) | √(20² + 30² + 85²) = √8333 = **91.3 mm** |
| Strut angle from vertical | atan(√(20² + 30²) / 85) = atan(0.425) = **23.0°** |
| Vertical component of strut axis | cos(23.0°) = 0.920 |

### 4.2 Strut Cross-Section Properties

Strut: STRUT_OD = 12 mm, wall = 2 mm, ID = 8 mm (CF-PETG hollow tube).

```
A_strut = π(12² − 8²)/4 = π × 80 / 4 = 62.8 mm²
I_strut = π(12⁴ − 8⁴)/64 = π × 16,640 / 64 = 816 mm⁴
E_CF-PETG = 5,500 MPa (in-plane, printed; conservative)
σ_yield   = 55 MPa
```

### 4.3 Load Path — Vertical Impact

Under a vertical landing impact, the ground reaction force F_total acts upward
on the foot pad and is transmitted:

```
foot → column (compression) → hub → 4 arm struts (compression)
     → 4 hull bosses → cargo belly shell → airframe
```

Force per strut (4 struts share equally for a central, symmetric impact):

```
F_vertical per assy = F_total / 4 (4 assemblies)
F_vert per strut    = (F_total/4) / 4 = F_total / 16

At 6 ft drop (from energy method):
  ½ k_equiv × δ² = 14.0 J → requires spring rate / deflection estimate.
```

**Column spring rate (CF-PETG column in compression):**

```
k_col = E × A / L
      = 5,500 × (π(18²−13²)/4) / 60
      = 5,500 × 122.5 / 60
      = 11,230 N/mm  (extremely stiff)
```

The column is far stiffer than any equivalent cantilever leg.  Energy
absorption at the design drop is therefore dominated by **plastic
deformation of the junction hub** (PETG, 25 % gyroid, intentionally weaker)
and by the TPU foot viscoelastic damping.

To estimate the peak force experienced by the structure, use the impulse-
momentum approach (rigid body, no spring credit):

```
Δv = v_impact = 5.99 m/s
m  = 3.130 kg  (Phase 11 AUW)
δ  = assumed 10 mm deflection before hub crush initiates (hub + foot compliance)

F_peak ≈ m × v² / (2 × δ)
       = 3.130 × 5.99² / (2 × 0.010)
       = 3.130 × 35.88 / 0.020
       = 5,620 N  total (all 4 assemblies)
       = 1,405 N  per assembly
       = 351 N    per strut (vertical component)
```

### 4.4 Per-Strut Axial Force

```
F_axial per strut = 351 / cos(23.0°) = 351 / 0.920 = 381 N
```

### 4.5 Euler Column Buckling Check (Strut)

With pin-pin end conditions, effective length = strut length = 91.3 mm:

```
P_crit = π² E I / L²
       = π² × 5,500 × 816 / 91.3²
       = 44,200,000 / 8,336
       = 5,302 N per strut
```

**Buckling margin:** 5,302 / 381 = **13.9×** — no buckling risk.

### 4.6 Strut Axial Stress

```
σ_axial = F_axial / A = 381 / 62.8 = 6.1 MPa  (vs σ_yield 55 MPa)
```

**Margin of safety: 8.0×** — struts remain fully elastic at design drop.

### 4.7 Peak Deceleration

```
a_peak = F_total / m = 5,620 / 3.130 = 1,796 m/s² = 183 g
```

This assumes 10 mm deflection.  Hub crush compliance will be larger, reducing
peak g to an acceptable range.

> **TODO LG-08:** Measure hub crush compliance by quasi-static loading of a
> printed PETG hub at 25 % gyroid infill.  Calculate actual δ and refine peak-g
> estimate.  Confirm ≤ 100g shock rating of avionics enclosures is met, or
> increase JUNCT_Z to increase total system compliance.

---

## 5. Lateral Load Analysis (±15° Off-Vertical)

For a landing at 15° from vertical, with F_per_assy = 1,405 N total:

```
F_vert_component    = 1,405 × cos(15°) = 1,357 N
F_lateral_component = 1,405 × sin(15°) =   364 N  (in hull XZ or YZ plane)
```

### 5.1 Lateral Load Resolution in Pyramid

For lateral force in the hull-X direction:

- Outboard struts (on the side toward the lateral force) see increased
  compression; inboard struts see reduced compression.
- The differential force per strut (2 outboard, 2 inboard):

```
ΔF_strut_axial = F_lateral × (SPREAD_X/2) / (4 × JUNCT_Z × sin(angle_x))
               = 364 × 20 / (4 × 85 × sin(atan(20/85)))
               = 7,280 / (4 × 85 × 0.229)
               = 7,280 / 77.9
               = 93.5 N additional axial per outboard strut
```

Total worst-case strut axial force (vertical + lateral combined):

```
F_axial_max = 381 + 93.5 / cos(23.0°) = 381 + 102 = 483 N
σ_axial_max = 483 / 62.8 = 7.7 MPa  (<< 55 MPa yield) ✓
```

### 5.2 Lateral Load at Boss Fuse Bolt

The retention bolt at each boss is loaded in shear by the lateral component
distributed to that boss.  With 4 bolts:

```
F_shear_per_bolt = F_lateral / 4 = 364 / 4 = 91 N
Fuse capacity (1× M3 PA6 nylon, 40 MPa shear):
  F_fuse = 40 × π × 3² / 4 = 282.8 N per bolt
Margin: 282.8 / 91 = 3.1×  (fuse bolts do NOT activate at design lateral load) ✓
```

**Fuse bolts are retention / lateral overload devices, not the primary vertical
energy fuse.**  The primary overload protection under severe (>3× design)
vertical load is junction hub crush.

---

## 6. Junction Hub — Crush Zone

The junction hub is printed in **PETG at 25 % gyroid infill** (not CF-PETG).
PETG σ_yield ≈ 30 MPa.  The hub sphere (HUB_R = 11 mm) has effective cross-
sectional area reduced by infill:

```
A_hub_eff ≈ 0.25 × π × 22² / 4 = 0.25 × 380 = 95 mm²
F_crush ≈ σ_yield_PETG × A_hub_eff = 30 × 95 = 2,850 N  (rough estimate)
```

Hub crush activates at approximately 2,850 N total vertical, which is 2.0×
the 1,405 N design load per assembly.  Hub crush is progressive and absorbs
significant energy before the boss bearing faces see high stress.

> **TODO LG-08:** Quasi-static compression test on representative PETG hub
> sample to characterise crush force and energy absorption.

---

## 7. Foot Impact Cushioning

The TPU 95A foot pad (55 × 55 × 12 mm) provides initial compliance.
With 25 % gyroid infill, effective modulus ≈ 8.75 MPa (approximation).

```
k_foot = E_eff × A / t = 8.75 × (55 × 55) / 12 ≈ 22,135 N/mm  (stiff)
```

The foot provides viscoelastic damping (hysteresis) and surface compliance
over rough terrain.  **No credit is taken for foot energy absorption in the
primary drop analysis.**

---

## 8. Hull Boss Bearing Check

Under design vertical load, the strut end bears against the top face of the
boss bore (annular area of boss wall above bore):

```
Bore ID = STRUT_OD + 0.4 = 12.4 mm
BOSS_OD = 22 mm
A_bearing = π(22² − 12.4²) / 4 = π(484 − 153.76) / 4 = 259 mm²  per boss
4 bosses total bearing area per assembly = 1,036 mm²

F_per_assy = 1,405 N (design load)
σ_bearing = 1,405 / 1,036 = 1.36 MPa  (vs CF-PETG bearing strength ≈ 70 MPa)
Bearing margin of safety: 70 / 1.36 = 51×
```

**Hull boss bearing stress is negligible at design load — hull is protected.**

---

## 9. Fuse Mechanism Summary

| Level | Element | Material | Activates At |
|---|---|---|---|
| 1 (primary compliance) | TPU foot + PETG hub elastic | TPU 95A + PETG | Any load |
| 2 (crush fuse) | PETG junction hub 25 % infill | PETG | ≈ 2,850 N per assy |
| 3 (retention / lateral) | M3 PA6 nylon bolts (1 per boss) | PA6 nylon | ≈ 283 N lateral per bolt |
| 4 (never reached) | Hull boss bearing | CF-PETG | > 70 MPa bearing → > 72,000 N |

The cargo shell and hull bosses are never at risk under the design load.

---

## 10. Rear Skids

The two rear skids are built into the horseshoe ring of the middle section
(see `airframe/openscad/fuselage/middle_canonical_shell24.scad`).  They
must be reinforced with a CF rod (3 mm diameter, pultruded carbon fibre)
before first flight.

- CF rod OD: 3 mm; modulus: ~130 GPa
- Length per skid: approximately 140 mm
- Adhesive: thin cyanoacrylate

---

## 11. Materials Specification

### 11.1 Arm Struts (4 per assembly, 16 total)

| Parameter | Value |
|---|---|
| Material | CF-PETG |
| Cross-section | OD 12 mm, wall 2 mm, ID 8 mm |
| Length | 91.3 mm (max; outboard-fore strut) |
| Layer height | 0.15 mm |
| Perimeters | 4 |
| Infill | 40 % gyroid |
| Print orientation | Lying flat (long axis horizontal) |
| Estimated mass | ≈ 4 g each × 16 = 64 g total |

### 11.2 Junction Hub (4 per aircraft)

| Parameter | Value |
|---|---|
| Material | **PETG** (not CF-PETG — intentional crush zone) |
| Diameter | 22 mm sphere |
| Layer height | 0.15 mm |
| Infill | **25 % gyroid** |
| Print orientation | Upright |
| Estimated mass | ≈ 6 g each × 4 = 24 g total |

### 11.3 Column (4 per aircraft)

| Parameter | Value |
|---|---|
| Material | CF-PETG |
| Cross-section | OD 18 mm, wall 2.5 mm, ID 13 mm |
| Length | 60 mm |
| Layer height | 0.15 mm |
| Perimeters | 4 |
| Infill | 40 % gyroid |
| Print orientation | Upright |
| Estimated mass | ≈ 9 g each × 4 = 36 g total |

### 11.4 Hull Boss Cylinders (16 per aircraft, integral to cargo shell)

| Parameter | Value |
|---|---|
| Material | CF-PETG |
| Geometry | OD 22 mm, bore 12.4 mm, height 30 mm |
| Integration | Union with `cargo_sect_shell24.scad` belly; 4 per corner |
| Fuse bolt | 1× M3 × 20 mm PA6 nylon SHCS per boss |

### 11.5 TPU Foot Pads

| Parameter | Value |
|---|---|
| Material | TPU 95A |
| Dimensions | 55 × 55 × 12 mm |
| Layer height | 0.20 mm |
| Infill | 25 % gyroid |
| Fasteners | 2× M3 × 10 mm SS SHCS per foot |

### 11.6 Safety Cord

| Parameter | Value |
|---|---|
| Material | Dyneema SK75, 2 mm diameter |
| Break strength | ≥ 750 N (168 lbf) |
| Length per assembly | ≈ 500 mm (foot → hub → boss → anchor post inside hull) |
| Anchor (hull end) | Loop on printed anchor post stub (ANCHOR_POST_OD = 5 mm) |
| Anchor (leg end) | Loop through hub TETHER_D hole, overhand knot |

---

## 12. Bill of Materials (per aircraft, 4 assemblies)

| Item | Qty | Description |
|---|---|---|
| Arm strut | 16 | CF-PETG, OD 12 mm × 91.3 mm per SCAD PART="strut" |
| Junction hub | 4 | PETG 25 % gyroid per SCAD PART="hub" |
| Column | 4 | CF-PETG per SCAD PART="column" |
| Hull boss cylinder | 16 | CF-PETG, integral to cargo shell (PART="boss" reference) |
| TPU foot | 4 | TPU 95A, SCAD PART="foot" |
| M3 × 20 nylon SHCS | 16 | Retention / lateral fuse (1 per boss) |
| M3 × 10 SS SHCS | 8 | Foot retention (2 per foot) |
| Dyneema SK75, 2 mm | 2.0 m | Safety cord (4 × 500 mm) |
| 3 mm CF rod | 280 mm | Rear skid reinforcement (2 × 140 mm) |
| CA thin | — | CF rod adhesive, rear skids |
| Spare nylon bolt set | 16 | Replacement M3 × 20 nylon (one full set) |

---

## 13. Assembly Procedure

1. **Hull boss integration:** Merge 4 boss cylinder positions per corner into
   `cargo_sect_shell24.scad` belly.  Print cargo section with bosses integral.

2. **Strut print:** Print 4 × 4 = 16 arm struts (CF-PETG, lying flat).

3. **Hub print:** Print 4 junction hubs (PETG, upright, 25 % gyroid).

4. **Column print:** Print 4 columns (CF-PETG, upright).

5. **Hub assembly:** Insert 4 strut top ends into hub sockets; apply thin CA.
   Insert column top end into hub column socket; apply thin CA.  Allow cure.

6. **Safety cord:** Route Dyneema through hub tether hole and up through column
   bore.  Tie loop at hub end.  Thread free end up through boss tether hole.
   Tie loop around boss anchor post stub inside hull.

7. **Boss insertion:** Slide each strut top end into the corresponding hull boss
   bore from below.  Align M3 fuse bolt holes.  Install 1× M3 × 20 nylon SHCS
   per boss — finger-tight + 1/4 turn only.

8. **Foot installation:** Press TPU foot socket over column spigot.
   Install 2× M3 × 10 SS SHCS from foot sole.  Torque to 0.3 N·m.

---

## 14. Field Replacement Procedure

After hub crush or other overload:

1. Locate leg assembly on safety cord.
2. Remove all 4 M3 nylon retention bolts (drill out remnants if sheared).
3. Pull strut / hub / column assembly downward from hull bosses.
4. Inspect boss bores; clean; check for cracks.
5. Install replacement assembly (steps 5–8 of assembly procedure above).

**Required tools:** 2.5 mm hex key (M3), 3.3 mm drill (bolt removal), CA adhesive.

---

## 15. Open Items and Verification Requirements

| ID | Item | Blocks |
|---|---|---|
| LG-01 | Shear-test 10 samples of M3 × 20 PA6 nylon in representative boss fixture; confirm lateral fuse ≥ 282 N per bolt | First flight |
| LG-02 | Integrate 16 hull boss cylinders into `cargo_sect_shell24.scad`; run DRC mesh check | Hull print |
| LG-03 | Add CF rod channel to `middle_canonical_shell24.scad` rear skid section | Hull print |
| LG-04 | Verify HULL_ATTACH_POS[] in SCAD against cargo belly contour in FreeCAD assembly | Hull print |
| LG-05 | Render STLs (PART="strut", "hub", "column", "boss", "foot"); verify all watertight | STL export |
| LG-06 | Drop test prototype assembly at 1.5 ft (elastic check) and 6 ft (design); log peak g with shock logger | Pre-flight |
| LG-07 | Confirm avionics enclosure ≥ 100g shock rating (design deceleration estimated ≤ 183g peak at 10 mm deflection; hub compliance expected to reduce this — LG-08 required) | PCB fab |
| LG-08 | Quasi-static compression test on PETG hub (25 % gyroid) — measure crush force and compliance; refine peak-g estimate; confirm ≤ 100g at avionics | Pre-flight |
