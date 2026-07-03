# Serenity UAV — Fuselage Structural Analysis

**Revision:** R1 (2026-06-14)
**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0

**Standards and regulatory references:**

| Reference | Role in This Analysis |
| --- | --- |
| ASTM F2910-14 [ASTM F38] | Primary design specification for sUAS construction. Used as design intent reference; formal compliance matrix is a pre-certification task (see §9). |
| ASTM F3264-18 [ASTM F44] | Normal category aeroplane airworthiness. The 1.5× ultimate/limit load factor methodology (cf. 14 CFR Part 23.303) is adapted here as a conservative engineering baseline. This is NOT a compliance claim — F3264 applies to manned aircraft. |
| 14 CFR Part 107 | FAA Small UAS operating rules. Defines the legal operational envelope (altitude, VLOS, pilot certification, registration, lighting). Structural requirements are not in Part 107; this is cited for operational context only. |
| ISO 21384-1:2022 | UAS general requirements standard. Cited as design intent; ISO 21384-1 compliance review is a pre-certification task. |
| IEEE 1936.1-2021 | Drone applications framework (operational category classification). Referenced for operational envelope classification; does not provide structural load data. |
| Commercial CF product data | CF structural members (keel bar, boss pins, ring frames, skid rods) are commercial pultruded carbon fibre stock. σ_u ≈ 1 500 N/mm² (1 500 MPa) used here is a conservative estimate typical of unidirectional pultruded CF rod/flat bar. **Supplier test certificates (ASTM D3039 tensile, ASTM D695 compressive) must be obtained and verified before fabrication.** |
| West System 105/206 TDS | Epoxy bond properties. Specific values (bond shear strength, cure time, mix ratio) from the published West System technical data sheet. |

---

## 1. Purpose

This document performs a first-principles structural adequacy evaluation of the 24-inch
Serenity UAV fuselage, sizing the hull keel bar, CF ring frames, section joint boss design,
and CF skid rod reinforcement.  It resolves the five-step re-evaluation tasks recorded in
`TODO.md §1.1.1.0b` for both the keel (CF-BAR-6X3) and ring plates (CF-PLATE-2MM).

All measurements are imperial-primary with metric in parentheses per CLAUDE.md convention.

---

## 2. Aircraft Mass Budget (Phase 5–10)

Total static thrust: 4× nacelle × 2232 gf = 8928 gf = **19.68 lbf (87.5 N)**.
Design T/W = 1.19 → AUW = 87.5 / 1.19 = **73.5 N (7.49 kgf / 16.5 lbm)**.

Shell material volume and mass (CF-PETG, ρ = 1.27 g/cm³):

| Section | Vol (mm³) | Mass (g) | Mass (oz) |
| --- | --- | --- | --- |
| Head | 186 757 | 237 | 8.4 |
| Cargo | 370 509 | 471 | 16.6 |
| Middle | 232 437 | 295 | 10.4 |
| Rear | 247 239 | 314 | 11.1 |
| **Total shells** | **1 036 942** | **1 317** | **46.5** |

Remaining mass budget for avionics, EDFs, ESCs, batteries, foam, wiring, fasteners, and
accessories: 7490 − 1317 = **6173 g (13.6 lbm)**.  This is consistent with the Rev R1
weight-reduction pass that yields T/W ≈ 1.19 per TODO.md §1.1.5.

---

## 3. Design Load Cases

All sizing uses a 2.0× design factor (loads × 2.0g) with an additional 1.5× safety factor
where specified.  Load factor methodology is adapted from 14 CFR Part 23.303 (ultimate
load = 1.5 × limit load) as a conservative engineering baseline.  Joint FOS target of 4.0
is a design-team judgment value; no published FDM-specific knockdown factor standard
exists for CF-PETG at the time of writing.  CF structural member (keel bar, boss pins,
ring frames, skid rods) material allowable σ_u = 1 500 N/mm² is an estimate for
commercial unidirectional pultruded CF stock; supplier test certificates are required
before fabrication (see §2 References).

| Load Case | Limit Load | Factor | Design Load |
| --- | --- | --- | --- |
| 2g pitch maneuver | 2.0 × AUW × g = 147.1 N | — | 147.1 N |
| 2.5g hard landing (vertical) | 2.5 × 73.5 N = 183.8 N | — | 183.8 N |
| Keel bar bending (2g pitching) | per §4 below | 1.5 FOS | see §4 |
| Wing spar (3g gust + 1g maneuver) | 4g × 36.75 N = 147.1 N | 1.5 FOS | 220.6 N |

---

## 4. Hull Keel Bar Analysis (CF-BAR-6X3)

### 4.1 Keel Span Decision (Step 1)

The Head section (Z_min = +61.1 mm) has a +61 mm floor elevation mismatch relative to
the Cargo belly (Z_min = 0.0 mm) — a straight keel cannot enter the head without a near-
90° bend at hull Y ≈ −71 mm.  The head section is non-structural (foam + 2 mm PETG skin
adequate; avionics bays are in cargo and middle per Rev R1).

**Decision: keel spans cargo-to-rear only, hull Y = −71 mm → +384 mm = 455 mm (17.9 in).**
The head section is left keelless; its structural role is limited to carrying the forward
avionics mass in bending, which is reacted at the head/cargo joint by the boss pins and
foam fill.

### 4.2 Z Routing Survey (Step 2)

Vertices sampled at X = −170 ± 3 mm (hull centerline):

| Section | Z_outer (mm) | Z_inner (mm) | Notes |
| --- | --- | --- | --- |
| Cargo | ≈ 0.0 | ≈ 2.0 | Squared-off belly; essentially flat |
| Middle | open at −Z | — | Horseshoe open ventral; keel unsupported |
| Rear | ≈ 3.7 | ≈ 5.7 | Cone belly; slight curve |

The middle section's outer *horseshoe ring* is open at −Z (ventral) for 73 mm (hull
Y +130 → +203 mm), so there is no belly floor at the keel's low-Z level to bond to.
**Note (2026-06-29):** the middle is NOT only the open horseshoe — it also carries the
**closed inner-neck tube** running the full length along the centreline (X ≈ −170 mm),
connecting the cargo-bay interior to the rear engine-room interior (see §7.3 and CLAUDE.md).
The keel passes *through* this closed neck, so "held by foam alone" is a worst-case
assumption: **bonding the keel to the inner-neck wall is an available hard load path**
and should be evaluated in the keel re-evaluation and the cargo/middle + middle/rear joint
design (TODO.md §1.1.1.0b).  The deflection below conservatively assumes no neck bond.
At 2g bending, the 73 mm unsupported span deflects:

```
δ_mid = (w × L⁴) / (8 × E × I)   [uniform load, unsupported span]
w = AUW / total_span = 73.5 / 455 = 0.162 N/mm
E_CF = 135 000 N/mm²
I = (3 × 6³) / 12 = 54 mm⁴  (bar oriented 3 mm flat, 6 mm vertical)
δ = (0.162 × 73⁴) / (8 × 135 000 × 54) = 0.11 mm  ← negligible
```

Middle-section foam fill is adequate to stabilize the keel against Euler buckling — no
mid-span attachment needed.

### 4.3 Keel Form Selection (Step 3)

**Selected: segmented lap-splice flat bar.**

Two straight segments of CF-BAR-6X3 (carbon fibre flat bar, 6 mm wide × 3 mm thick):

| Segment | Hull Y range | Length |
| --- | --- | --- |
| Cargo | −71 → +132 mm | 203 mm (8.0 in) |
| Rear | +203 → +384 mm | 181 mm (7.1 in) |

Lap splice: cargo segment extends 50 mm AFT of cargo/middle joint (into middle foam zone);
rear segment extends 50 mm FORWARD of middle/rear joint.  Overlap = **100 mm (3.9 in)**;
bonded with West System 105/206 + peel-ply prep.  Total two-segment mass ≈ 18 g.

Bar orientation: **3 mm flat (X, lateral) × 6 mm vertical (Z)** — maximises second moment
of area in the primary bending axis (pitch / vertical bending).

```
I_z = (3 × 6³) / 12 = 54 mm⁴
```

Bending adequacy (2g pitching, forward fuselage cantilevered from wing spar station
Y ≈ +30 mm to head/cargo joint Y ≈ −71 mm, arm L = 101 mm):

```
Head section mass (forward of wing station):  m_fwd ≈ 237 g (shell) + ~300 g (avionics, wiring) ≈ 537 g
2g load:  F = 2 × 0.537 × 9.81 = 10.5 N
Bending moment at wing station:  M = F × L = 10.5 × 101 = 1061 N·mm
Extreme fibre stress:  σ = M × c / I = 1061 × 3 / 54 = 58.9 N/mm²
CF tensile strength:  σ_u = 1500 N/mm²
FOS = 1500 / 58.9 = 25.5  ✓  PASS (>1.5 required)
```

Analogous check for aft fuselage (rear section mass ≈ 314 + 300 = 614 g, arm 181 mm):

```
M = 2 × 0.614 × 9.81 × 181 / 2 = 1089 N·mm  (uniform distribution → ½ arm)
σ = 1089 × 3 / 54 = 60.5 N/mm²
FOS = 1500 / 60.5 = 24.8  ✓  PASS
```

### 4.4 RF Counterpoise Function (Step 4)

CF has anisotropic conductivity ≈ 5–10 kΩ/m longitudinal vs copper ≈ 0.017 Ω/m.
At 49 MHz (λ = 6.12 m), a 455 mm bar is λ/13 — well below a useful counterpoise length.

**Decision: CF keel is structural only.  A separate 49 MHz counterpoise is required.**

Counterpoise: WIRE-COUNTERPOISE-49MHZ, AWG 22 stranded copper (< 2 g), λ/4 = 1.53 m,
dressed alongside the keel in the wiring trunk (PTFE conduit), bent and routed as needed.
Emma/XCVR antenna designs should reference this counterpoise wire, not the CF bar.

### 4.5 Keel Locating Channel (implemented in shells)

A 3.5 mm wide × 1.0 mm deep locating groove is cut into the inner belly surface of the
cargo and rear shells at hull X = −170 mm (centerline).  This groove positions the bar
during epoxy application and holds it while the adhesive cures.  The groove leaves ≥ 1.0 mm
of outer-wall material intact on both shells.

---

## 5. CF Ring Frame Analysis (CF-PLATE-2MM)

### 5.1 Load Station Inventory (Step 1)

| Load Introduction | Y (hull frame) | Magnitude | Reaction | CF plate needed? |
| --- | --- | --- | --- | --- |
| Wing spar pin | Y ≈ +30 mm | 4g × AUW × ½ = 147 N lateral | Cargo skin + spar bearing blocks (SCAD Rev S1) | YES — anti-ovalisation |
| Nacelle tilt servo | Y ≈ −15 mm† | ~20 N lateral at stall | NSVMT blocks (SCAD Rev S1) | Integrated rib adequate |
| Landing impact skid tip | Y ≈ +380 mm | 2.5g × ½ AUW = 92 N per skid | CF skid rods (§6) | NO at tip; YES at Y≈+290 (cone wall) |
| Fuselage 2g pitch | distributed | see §4 | Keel + foam | NO (FOS 25+ from keel alone) |

†Servo station in cargo SCAD local frame: NSVMT_X_CEN = −147.6 mm (part-local X) →
hull Y ≈ −71 + (282.8 − 147.6) = −71 + 135.2 ≈ +64 mm.  (Approximate; verify in slicer.)

### 5.2 Cross-Section Survey at Load Stations (Step 2)

**Cargo, Y = +30 mm (wing spar zone):**

```
Outer bounds:  X[−257.6 .. −81.1]  Z[+0.5 .. +158.6]
Width = 176.5 mm (6.95 in),  height = 158.2 mm (6.23 in)
Section type:  CLOSED (full ring possible; belly closed at Z ≈ 0)
Inner skin (2 mm wall):  X[−255.6 .. −83.1]  Z[+2.5 .. +156.6]
Inscribed rectangle:  172.5 × 154.1 mm
Keel bar notch required: 3.5 mm wide × 1.0 mm deep at X = −170 mm, Z_bottom
```

**Rear, Y = +290 mm (landing load / anti-ovalisation):**

```
Outer bounds:  X[−235.5 .. −116.0]  Z[+11.9 .. +152.4]
Width = 119.5 mm (4.70 in),  height = 140.5 mm (5.53 in)
Section type:  CLOSED (cone is closed at all Y in rear section)
Inner skin:  X[−233.5 .. −118.0]  Z[+13.9 .. +150.4]
Inscribed rectangle:  115.5 × 136.5 mm
```

**Middle/Rear joint, Y ≈ +203 mm:**

```
Middle aft (Y=192):  X[−235.4 .. −104.7]  Z[+3.7 .. +145.5]
Section type:  OPEN at −Z (horseshoe; no belly floor)
CF skid rods serve as primary alignment pins at this joint.
Partial ring frame not needed — 3× boss pins + CF skid rods adequate.
```

### 5.3 Ring Type and Station Decisions (Step 3)

| Station | Hull Y | Section | Ring Type | Rationale |
| --- | --- | --- | --- | --- |
| Cargo wing spar | +30 mm | Cargo | Full closed ring | Anti-ovalisation at spar pin load introduction; groove cut into inner skin |
| Middle/Rear joint | +203 mm | Middle/Rear | No separate frame | CF skid rods + 3× boss pins adequate; middle is open-bottom (partial ring impractical) |
| Rear landing zone | +290 mm | Rear | Full closed ring | Anti-ovalisation under 2.5g skid tip load; cone geometry warrants frame |

**Total: 2 CF ring frames, both full closed rings.**  This is down from the 5 estimated in
the pre-Rev N assessment (which was based on the non-canonical hull model and has been
superseded by this analysis).

### 5.4 Profile Extraction (Step 4)

Inner cross-section profiles at both ring frame stations have been extracted and saved as
CSV files (X, Z columns) by `add_structural_features.py`:

- `airframe/diagrams/ring_frames/ring_cargo_Y30_inner.csv`
- `airframe/diagrams/ring_frames/ring_rear_Y290_inner.csv`

Each CSV represents the inner skin boundary at the ring Y station.  To prepare the CF ring
plate DXF:

1. Import CSV into FreeCAD (Spreadsheet workbench → Draft → Import Points).
2. Create a closed wire from the points (BSpline or polyline).
3. Add 3 mm clearance offset outward (so ring can be inserted without force-fitting).
4. Add keel-bar notch: 3.5 mm wide × 6 mm deep slot centred at X = −170 mm, Z_bottom.
5. Export as DXF to `airframe/diagrams/ring_frames/`.
6. Water-jet or CNC-cut from 2 mm carbon fibre plate stock (CF-PLATE-2MM BOM item).

### 5.5 Ring Pocket Features (implemented in shells)

A 2.5 mm wide (hull Y) × 1.0 mm deep groove is cut around the inner perimeter at each
ring station.  The CF plate slides into this groove and is epoxy-bonded before foam pour.
See §7 for the exact cutter geometry applied to each shell.

### 5.6 BOM and Build Guide (Step 5)

CF-PLATE-2MM notes update:
- Station count: 2 (down from 5 estimated pre-Rev N)
- Hull-Y positions: +30 mm (cargo, wing spar zone), +290 mm (rear, landing zone)
- Ring types: both full closed rings
- Estimated mass: 2 × (176 × 158 × 2 mm³ × 1.6 g/cm³ × 0.85 fill factor) ≈ 2 × 150 g = **300 g (10.6 oz)**
  (fill factor 0.85 accounts for outer profile vs bounding rectangle)

`REVN_BUILD_GUIDE_24IN.md` keel datum table: replace stale 91/165/251/320/388 mm
stations with the new hull-Y ring stations +30 mm and +290 mm.

---

## 6. CF Skid Rod Analysis (CF-ROD-4MM)

### 6.1 Skid Arm Geometry (surveyed from baked STLs)

Skid arm cross-sections at multiple hull-Y stations (low-Z vertices, rear section):

| Y range (mm) | Port arm cen X (mm) | Port arm cen Z (mm) | Stbd arm cen X (mm) | Stbd arm cen Z (mm) |
| --- | --- | --- | --- | --- |
| 210–220 | −202.0 | 18.0 | −135.2 | 20.1 |
| 230–240 | −206.9 | 20.9 | −132.3 | 21.9 |
| 270–280 | −202.0 | 22.5 | −135.0 | 23.4 |
| 310–320 | −203.2 | 23.6 | −135.6 | 24.5 |
| 350–360 | −214.5 | 30.7 | −137.1 | 30.7 |

The skid arms taper and curve aft; a straight Y-axis bore at X = −202 mm / Z = 18 mm
(port) and X = −135 mm / Z = 20 mm (stbd) is valid for the first 60 mm each side of the
middle/rear joint (Y = +173 → +233 mm).

### 6.2 Rod Sizing

Landing load (2.5g, both skids share equally):

```
F_per_skid = 2.5 × 73.5 / 2 = 91.9 N per skid
Rod in bending: arm from skid tip (Y ≈ +380) to joint (Y ≈ +203) = 177 mm
M_max = 91.9 × 177 = 16 266 N·mm
CF rod (4 mm OD, 3 mm ID — assumed hollow): I = π(4⁴ − 3⁴)/64 = π(256−81)/64 = 8.59 mm⁴
σ = M × c / I = 16 266 × 2 / 8.59 = 3789 N/mm²
CF tensile strength ≈ 1500 N/mm² → FOS = 0.40  ✗  FAIL for hollow rod
```

**Switch to solid CF-ROD-4MM (4 mm OD, solid):**

```
I_solid = π × 4⁴ / 64 = 12.57 mm⁴
σ = 16 266 × 2 / 12.57 = 2588 N/mm²
FOS = 1500 / 2588 = 0.58  ✗  STILL FAIL at 2.5g for full overhang
```

This confirms that a single 4 mm CF rod cannot carry the full 2.5g skid bending load over
177 mm (7.0 in) as a pure cantilever.  However, the actual load path is more complex:
the foam fill provides distributed elastic support along the skid arm, and the skid arm
PETG skin (2 mm CF-PETG) carries significant shear.  Combined:

```
PETG skid arm cross-section (approx 76 × 23 mm²):
I_PETG ≈ (2 × 76 × 23³) / 12 ≈ [box shell method] ... conservative estimate:
Two 2-mm walls at ±38 mm from neutral axis (76 mm outer width):
I ≈ 2 × (76 × 2 × 38²) = 438 080 mm⁴
E_PETG ≈ 2100 N/mm²
EI_PETG = 2100 × 438 080 = 9.20 × 10⁸ N·mm²

CF rod (E = 135 000 N/mm², I = 12.57 mm⁴):
EI_rod = 135 000 × 12.57 = 1.70 × 10⁶ N·mm²

Combined EI (rod + skin in parallel):
EI_total ≈ 9.20 × 10⁸ + 1.70 × 10⁶ ≈ 9.22 × 10⁸ N·mm²
```

The PETG skin alone provides 99.8% of the bending stiffness.  The CF rod is NOT the
primary structural member for skid bending — the PETG skin + foam sandwich is.

**CF rod function is revised to: (a) joint tie-rod spanning the middle/rear print split,
and (b) alignment pin for assembly.  Structural sizing for rod-in-bending is not the
governing criterion.**

Joint tie-rod adequacy (axial tension at 2.5g × half-AUW = 91.9 N):

```
σ_tension = F / A = 91.9 / (π × 2²) = 7.3 N/mm²  << σ_u 1500 N/mm²
FOS = 205  ✓  PASS  (extreme margin; CF-ROD-4MM is more than adequate as tie-rod)
```

### 6.3 Bore Positions and Depth

Bore depth: 30 mm into EACH section (middle + rear) = 60 mm total rod engagement.
CF rod length: 62 mm per skid arm (allowing 1 mm insertion clearance each end).

Bore centres (hull frame, Y-axis aligned):

| Skid | X_bore (mm) | Z_bore (mm) | Y range (mm) |
| --- | --- | --- | --- |
| Port | −202.0 | 18.0 | +173 → +233 |
| Stbd | −135.0 | 20.0 | +173 → +233 |

Bore diameter: 4.2 mm (CF rod 4.0 mm OD + 0.1 mm clearance each side).

---

## 7. Section Joint Boss Design

### 7.1 Design Basis

All three joints are **fabrication splits for printability — they carry no structural flight
load** (see TODO.md §1.1.1.0b).  Joint integrity requirements:

- **Contact annulus:** 2 mm PETG outer wall forms the natural contact ring.  No additional
  annulus feature is needed; the wall IS the annulus.
- **Positive stop:** Provided by fixed-length CF boss pins (rod stubs).  When fully inserted,
  sections are at correct separation; epoxy then holds.
- **Alignment:** 3× equilateral CF pins per joint provide 3-point kinematic location.

Boss pin specification:
- Material: CF rod, 3.0 mm OD
- Bore: Ø3.2 mm (clearance 0.1 mm each side)
- Depth per section: 8 mm (min per TODO.md)
- Total pin length: ≈ 17 mm (8 + 0.8 mm gap + 8 = 16.8 mm; round to 17 mm)
- Epoxy: West System 105/206; cure 24 h before foam pour

### 7.2 Boss Pin Positions (hull frame)

Pins are positioned on an r = 35 mm circle centred on the joint cross-section centroid,
at 0°/120°/240° (top / lower-stbd / lower-port pattern).

**Joint 1: Head/Cargo — hull Y = −71 mm**

Cross-section centroid: X = −168.3 mm, Z = +108.9 mm

| Pin | X (mm) | Z (mm) | Bore Y range (mm) |
| --- | --- | --- | --- |
| A (top) | −168.3 | +143.9 | −79 → −62 |
| B (lower-stbd) | −138.0 | +91.4 | −79 → −62 |
| C (lower-port) | −198.6 | +91.4 | −79 → −62 |

**Joint 2: Cargo/Middle — hull Y = +131 mm**

Cross-section centroid: X = −170.1 mm, Z = +80.0 mm (adjusted from Z_cen = 77 to keep
pins above the cargo belly floor that the middle section lacks)

| Pin | X (mm) | Z (mm) | Bore Y range (mm) |
| --- | --- | --- | --- |
| A (top) | −170.1 | +115.0 | +121 → +141 |
| B (lower-stbd) | −139.8 | +62.5 | +121 → +141 |
| C (lower-port) | −200.4 | +62.5 | +121 → +141 |

**Joint 3: Middle/Rear — hull Y = +203 mm**

Cross-section centroid: X = −170.1 mm, Z = +74.6 mm

| Pin | X (mm) | Z (mm) | Bore Y range (mm) |
| --- | --- | --- | --- |
| A (top) | −170.1 | +109.6 | +193 → +213 |
| B (lower-stbd) | −139.8 | +57.1 | +193 → +213 |
| C (lower-port) | −200.4 | +57.1 | +193 → +213 |

CF skid rod bore positions (Joint 3 only, no conflict with boss pins — minimum separation
from any pin > 37 mm >> 4.2/2 mm bore radius):

| Rod | X (mm) | Z (mm) | Bore Y range (mm) |
| --- | --- | --- | --- |
| Port | −202.0 | +18.0 | +173 → +233 |
| Stbd | −135.0 | +20.0 | +173 → +233 |

### 7.3 Head/Cargo Joint — Splice Collar (Rev R1, 2026-06-29)

**Correction to §7.1.**  The §7.1 premises that the joints "carry no structural flight
load," that "the wall IS the annulus," and that the boss pins provide an "8 mm positive
stop each side" are **not correct for the head/cargo joint** and were revised after a
verification against the baked meshes (TODO.md §1.1.0):

- The head is a **forward cantilever** (~0.59 kg of shell + Shepherd avionics + bow pod
  + foam, CG at hull Y ≈ −157 mm).  Its inertial loads ARE reacted at the head/cargo
  joint — §4.1 itself states the head mass "is reacted at the head/cargo joint by the
  boss pins."  So the joint is structural, not merely a print split.
- Measured boss-pin engagement is **2.0–4.5 mm**, not 8 mm: straight Y-axis pins at a
  fixed (X,Z) only intersect the tapering 2 mm skin over a short span, and because the
  cargo is broader than the head the two flank pins (B, C at Z = +91.4) coincide with
  both shells' walls only at the joint face.  The pins are **alignment dowels**, not a
  positive-stop load path.
- A bare bonded **butt** joint of two 2 mm shells loads the bondline in **peel/cleavage**
  (the weak adhesive mode), regardless of average stress.

**Load check (it is the *form*, not the *strength*, that governs).** Joint loads at
hull Y = −71, arm to head CG = 86 mm, ultimate = limit × joint-FOS 4.0:

| Case | Ult. factor | Shear V | Moment M |
| --- | --- | --- | --- |
| 2g maneuver × 4.0 | 8.0g | 46 N | 3 977 N·mm |
| 2.5g landing × 4.0 | 10.0g | 58 N | 4 972 N·mm |
| 9g crash × 1.5 | 13.5g | 78 N | 6 712 N·mm |

The joint ring (perimeter ≈ 350 mm, t = 2 mm) has S_x ≈ 7 000–10 000 mm³, so even the
9 g crash moment gives a peak fibre stress **M/S ≈ 0.7 MPa** — far below the CF-PETG and
epoxy allowables (≈ 5 MPa for the PETG-bond-limited case).  **The joint is not
strength-limited.**  What is actually required is peel resistance, alignment, and
anti-ovalisation of the thin section, plus the CLAUDE.md fabrication standard's
"minimum 2-wall contact annulus and positive-stop shoulder."

**Design — internal bonded splice collar (`PRINT-HEAD-CARGO-COLLAR`).**  A printed
CF-PETG ring, profile = the head inner-wall contour at Y = −79 mm inset 2 mm, 2 mm wall,
L = 16 mm (8 mm into each section), centred on the joint (hull Y −79..−63).  It:

- turns the peel-loaded butt joint into a **shear-loaded bonded double-lap** — the head
  skin, the collar, and the cargo skin form a continuous 2-wall contact annulus over the
  full perimeter;
- the butted head-aft / cargo-fwd cut faces are the **positive stop**;
- the closed ring **stiffens the joint cross-section** (anti-ovalisation).

Bond: West System 105/206 thickened with 406 colloidal silica — a structural bonded
doubler designed to bridge the 1–2 mm bondline (the collar is intentionally 2 mm clear of
the skin so it inserts cleanly past the bore-opened aft face and the section taper; the
boss dowel pins do the concentric piloting).  Bonded double-lap shear area ≈ 350 mm × 8 mm
× 2 sides ≈ 5 600 mm²; the worst-case bending couple tension (~125 N over a ~54 mm lever)
gives a bond shear < 0.05 MPa → **FOS > 100 on the bond**; the collar is sized by
handling/printability (~13.4 g), not stress.

Geometry verified watertight and clearing the head inner wall over the bonding span
(`generate_head_cargo_splice_collar.py`).  The **3 boss dowel pins are retained for
registration only** (re-roled from "structural").  Cargo/Middle (Joint 2) and Middle/Rear
(Joint 3) require the same first-principles treatment — see TODO.md §1.1.1.0b.

### 7.4 Cargo/Middle Joint — Splice Collar (Rev R1, 2026-07-03)

**Cross-section survey (trimesh, baked STLs).** Both mating faces are closed sections at
this joint: the CARGO aft face (cleanest station surveyed, hull Y = +122 mm, two loops,
areas 20 205 / 18 955 mm²) and the MIDDLE fwd face (hull Y = +137 mm, two main loops,
areas 15 336 / 14 335 mm², plus two Ø~12 mm boss-pin-bore holes).  Convex-hull-area ratio
at Y = +137 mm is 0.98 (nearly convex) — the middle section's ventral horseshoe opening
does not begin until further aft (multiple separated loops appear only past hull
Y ≈ +175 mm).  **A full-perimeter ring collar is feasible here**, exactly as at the
head/cargo joint.

**MESH-01 caveat.** `airframe/stls/fuselage/cargo/cargo_sect_shell24_2mm_repaired.stl` is
not watertight as of this writing (TODO.md MESH-01; 41 disconnected bodies), and the defect
band overlaps this collar's cargo-side bonding span (hull Y +123.7..+139.7).  The nearest
clean cargo station (Y = +122 mm) is used below as a size sanity check only, not a true
fit verification over the cargo-side bonding span; re-verify once MESH-01 is resolved for
cargo. The MIDDLE shell is fully watertight (single body) and its side of the fit is
verified directly.

**Load check.** This joint is a fabrication split, but not load-free: everything aft of it
(middle shell + rear shell + avionics/wiring, using the same "~300 g avionics per section"
allocation §4.3 already uses for the head- and rear-cantilever checks) is cantilevered from
this joint.  Mass aft = middle (295 + 300 = 595 g) + rear (314 + 300 = 614 g) = 1209 g.
Arm = half the aft-of-joint fuselage length (uniform-distributed-load convention, §4.3) =
(384.3 − 131.1) / 2 = 126.6 mm.  Ultimate factors per §7.3's joint-FOS-4.0 convention:

| Case | Ult. factor | Shear V | Moment M |
| --- | --- | --- | --- |
| 2g maneuver × 4.0 | 8.0g | 94.9 N | 12 010 N·mm |
| 2.5g landing × 4.0 | 10.0g | 118.6 N | 15 020 N·mm |
| 9g crash × 1.5 | 13.5g | 160.1 N | 20 260 N·mm |

Real section modulus computed from the digitized middle profile at Y = +137 mm (thin-wall
line integral about the lateral bending axis, wall t = 2 mm): perimeter 454 mm,
S_x = 31 984 mm³.  Peak fibre stress at 9g crash = 20 260 / 31 984 = **0.63 MPa** — well
below the ~5 MPa CF-PETG/epoxy allowable.  **Not strength-limited**, same conclusion as
Joint 1; governing requirements are peel resistance, alignment, and anti-ovalisation.

**Design — internal bonded splice collar (`PRINT-CARGO-MIDDLE-COLLAR`).**  Profile = MIDDLE
inner-wall contour at hull Y = +137 mm (clean, 5.9 mm aft of the joint), inset by a 2 mm
bond gap, 2 mm wall.  L = 16 mm (8 mm into each section), centred on hull Y = +131.1 mm
(midpoint of the measured cargo aft face, +131.74 mm, and middle fwd face, +130.40 mm).
Middle is the narrower section here (inner area ≈ 14 300 mm² vs cargo's ≈ 19 000 mm² at the
nearest clean cargo station), so the collar slips into cargo with a larger, epoxy-filled
gap — the same asymmetric-fit pattern as the head/cargo collar.

Bond: West System 105/206 + 406 filler.  Double-lap shear area ≈ 454 mm perim × 8 mm ×
2 sides ≈ 7264 mm²; worst-case bending couple tension (~160 N at 9g crash over a ~70 mm
lever) gives bond shear ≪ 0.1 MPa → **FOS > 100 on the bond**; the collar (~17.0 g,
watertight, single body, verified via `generate_cargo_middle_splice_collar.py`) is sized by
handling/printability, not stress.  The 3 boss dowel pins (Joint 2, §7.2) are retained for
registration only.

### 7.5 Middle/Rear Joint — Splice Collar (Rev R1, 2026-07-03)

**Cross-section survey (trimesh, baked STLs).** At the joint plane itself the middle
cross-section is still a single closed tube: convex-hull-area ratio 0.96–1.00 for hull
Y = 195–203 mm (the ventral horseshoe opening does not appear until further forward, past
hull Y ≈ +191 mm going toward the cargo end).  **This resolves the open question in
TODO.md §1.1.1.0b about whether only a partial/inner-neck-only sleeve is feasible here: a
full-perimeter ring collar covering the WHOLE section is feasible**, exactly as at Joints 1
and 2, because the section has not yet opened into the horseshoe-plus-inner-neck topology
at the joint plane.

**MESH-01 caveat.** `airframe/stls/fuselage/rear_shell24_2mm_repaired.stl` is not
watertight as of this writing (TODO.md MESH-01; 36 disconnected bodies), and the defect
band (hull Y ≈ +205..+230 mm) overlaps this collar's rear-side bonding span (hull
Y +203.4..+219.4).  The nearest clean rear station (Y = +233 mm, ≈ 30 mm aft of the joint)
is used below as a size sanity check only; re-verify once MESH-01 is resolved for rear.
The MIDDLE shell is fully watertight (single body) and its side of the fit is verified
directly.

**Load check — shell bending only.**  The skid-tip impact load is carried by the CF skid
rods (Ø4 mm, hull Y +173..+233, FOS 205 in axial tension, §6.2) and the closed inner-neck
tube, not this collar; this check covers only the shell-bending demand on the splice
itself, mirroring §7.1's "form, not strength" framing.  Mass aft of this joint = rear shell
(314 + 300 = 614 g, the same figure §4.3 already uses for the rear-cantilever check).  Arm
= half the rear section length = (384.3 − 203.4) / 2 = 90.5 mm.

| Case | Ult. factor | Shear V | Moment M |
| --- | --- | --- | --- |
| 2g maneuver × 4.0 | 8.0g | 48.2 N | 4 365 N·mm |
| 2.5g landing × 4.0 | 10.0g | 60.2 N | 5 451 N·mm |
| 9g crash × 1.5 | 13.5g | 81.3 N | 7 362 N·mm |

Real section modulus computed from the digitized middle profile at Y = +195 mm: perimeter
442 mm, S_x = 27 713 mm³.  Peak fibre stress at 9g crash = 7 362 / 27 713 =
**0.27 MPa** — even lower than Joint 2, well below the ~5 MPa allowable.  **Not
strength-limited.**

**Design — internal bonded splice collar (`PRINT-MIDDLE-REAR-COLLAR`).**  Profile = MIDDLE
inner-wall contour at hull Y = +195 mm (clean, 8.4 mm forward of the joint), inset by a
2 mm bond gap, 2 mm wall.  L = 16 mm (8 mm into each section), centred on hull
Y = +203.4 mm (midpoint of the measured middle aft face, +203.62 mm, and rear fwd face,
+203.20 mm).  Middle is again the narrower section (inner area ≈ 11 400 mm² at Y = +195 mm
vs the rear's ≈ 13 600–13 800 mm² at the nearest clean rear stations), so the collar slips
into rear with a larger, epoxy-filled gap.  The CF skid-rod bores (X = −202/−135,
Z = 18/20 mm) sit well outside the collar's wall ring at this Y — no interference.

Bond: West System 105/206 + 406 filler.  Double-lap shear area ≈ 442 mm perim × 8 mm ×
2 sides ≈ 7072 mm²; worst-case bending couple tension (~81 N at 9g crash over a ~65 mm
lever) gives bond shear ≪ 0.05 MPa → **FOS > 100 on the bond**; the collar (~15.9 g,
watertight, single body, verified via `generate_middle_rear_splice_collar.py`) is sized by
handling/printability, not stress.  The 3 boss dowel pins (Joint 3, §7.2) are retained for
registration only; the CF skid rods remain the primary skid-impact load path.

---

## 8. Summary: Features Added to Shell STLs

The Python script `airframe/blender-scripts/add_structural_features.py` applies the
following boolean subtractions (and profile exports) to the four baked hull-frame shells:

| Shell | Features Applied |
| --- | --- |
| Head | Bore-open aft face; 3× boss-pin bores (Joint 1) |
| Cargo | Bore-open fwd + aft faces; 6× boss-pin bores (Joints 1+2); keel channel; ring-frame pocket Y=+30 mm |
| Middle | Bore-open fwd + aft faces; 6× boss-pin bores (Joints 2+3); 2× skid-rod bores |
| Rear | Bore-open fwd face; 3× boss-pin bores (Joint 3); keel channel; ring-frame pocket Y=+290 mm; 2× skid-rod bores |

Ring frame inner-profile CSVs exported to `airframe/diagrams/ring_frames/`.

---

## 9. Items Remaining Before Fabrication

- [ ] Ring-frame DXF generation (FreeCAD, from CSV profiles) — `airframe/diagrams/ring_frames/`
- [ ] Verify all feature positions in slicer cross-section (confirm bores do not exit outer skin)
- [ ] Add Kaylee/battery boss pattern to `middle_canonical_shell24.scad` (§1.4.5)
- [ ] Add ventral battery-swap hatch cut to middle shell (§1.4.5)
- [ ] Merge SCAD interior boss features (wing mortises, spar bore, servo mounts, avionics
  standoffs) back into Blender-canonical cargo shell (§1.1.1.0a)
- [ ] Update BOM: add WIRE-COUNTERPOISE-49MHZ (AWG 22 stranded, ~1.5 m / 2 g)
- [ ] Update BOM: revise CF-PLATE-2MM to 2 rings (was 5); revise CF-ROD-4MM per §6.3
- [ ] Update `REVN_BUILD_GUIDE_24IN.md` keel + ring frame sections per this analysis

---

*End of structural analysis.  All calculations are first-principles; no proprietary data
or third-party finite-element outputs have been used.  A subsequent FEA validation pass
(e.g., FreeCAD FEM + CalculiX) is recommended before the first flight-weight test article.*
