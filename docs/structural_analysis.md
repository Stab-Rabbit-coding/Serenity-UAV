# Serenity UAV — Fuselage Structural Analysis

**Revision:** R1 (2026-06-14)
**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0

**Standards and regulatory references:**

| Reference | Role in This Analysis |
| --- | --- |
| ASTM F2910-14 [ASTM F38] | Primary design specification for sUAS construction. Used as design intent reference; formal compliance matrix is a pre-certification task (see §9). |
| ASTM F3264-18 [ASTM F44] | Normal category aeroplane airworthiness. The 1.5× ultimate/limit load factor methodology (**14 CFR §23.2230** [REF-FAA-004] — *corrected 2026-08-29 from "Part 23.303", which belonged to the pre-2017 Part 23 and does not exist in the current rule*) is adapted here as a conservative engineering baseline. This is NOT a compliance claim — F3264 applies to manned aircraft, and Part 23 is an adopted baseline, not Serenity's certification basis. |
| 14 CFR Part 107 | FAA Small UAS operating rules. Defines the legal operational envelope (altitude, VLOS, pilot certification, registration, lighting). Structural requirements are not in Part 107; this is cited for operational context only. |
| ISO 21384-1:2022 | UAS general requirements standard. Cited as design intent; ISO 21384-1 compliance review is a pre-certification task. |
| IEEE 1936.1-2021 | Drone applications framework (operational category classification). Referenced for operational envelope classification; does not provide structural load data. |
| Commercial CF product data | CF structural members (keel bar, boss pins, ring frames, skid rods) are commercial pultruded carbon fiber stock. σ_u ≈ 1 500 N/mm² (1 500 MPa) used here is a conservative estimate typical of unidirectional pultruded CF rod/flat bar. **Supplier test certificates (ASTM D3039 tensile, ASTM D695 compressive) must be obtained and verified before fabrication.** |
| West System 105/206 TDS | Epoxy bond properties. Specific values (bond shear strength, cure time, mix ratio) from the published West System technical data sheet. |

---

## 1. Purpose

This document performs a first-principles structural adequacy evaluation of the 24-inch
Serenity UAV fuselage, sizing the hull keel bar, CF ring frames, section joint boss design,
and CF skid rod reinforcement.  It resolves the five-step re-evaluation tasks recorded in
`TODO.md §1.1.1.0b` for both the keel (CF-BAR-6X3) and ring plates (CF-PLATE-2MM).

All measurements are imperial-primary with metric in parentheses per AGENTS.md convention.

---

## 2. Aircraft Mass Budget (Phase 5–10)

> **Correction (2026-08-22, TODO.md §0.10.1):** this section previously double-counted
> thrust — there are **2** nacelles (port + starboard), each already representing the
> 2232 gf tandem-EDF-pair figure, not 4. The corrected total below drops AUW from a
> fabricated 16.5 lbm to ≈8.27 lbm — closer to, but not identical to, the BOM-derived
> Phase 5–10 AUW of ~8.62 lbm (3,911 g) established in `README.md`/`airframe/README.md`
> (this section's AUW is a design-margin back-calculation, not a BOM sum — the two
> should agree within rounding once both are current). **Every load case, margin, and
> FOS number in §3 through §7 below was computed from the old, doubled mass budget and
> has not yet been re-derived from the corrected baseline — treat them as stale until
> re-verified.** Since the true mass is lower than what was analyzed, the existing
> numbers are likely conservative (understating margin), not unsafe, but they should
> not be cited as current until recomputed.

Total static thrust: 2× nacelle × 2232 gf = 4464 gf = **9.84 lbf (43.79 N)**.
Design T/W = 1.19 → AUW = 43.79 / 1.19 = **36.8 N (3.75 kgf / 8.27 lbm)**.

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
where specified.  Load factor methodology is adapted from **14 CFR §23.2230**
[REF-FAA-004] (ultimate load = 1.5 × limit load) as a conservative engineering baseline.
*(Corrected 2026-08-29: this previously cited "14 CFR Part 23.303", a pre-2017 section
number removed by the Amdt. 23-64 restructure — same class of stale citation as the
§23.1401 case already recorded in REFERENCES.md.)*

Joint FOS target of 4.0 remains a design-team judgment value, and no published
FDM-specific knockdown-factor standard exists for CF-PETG at the time of writing —
but it now has a citable regulatory basis rather than resting on judgment alone.
**14 CFR §23.2265** [REF-FAA-004] requires a *special* factor of safety beyond the
basic 1.5 for any part "subject to appreciable variability because of uncertainties in
manufacturing processes or inspection methods", and FDM-printed polymer structure —
layer adhesion, raster orientation, moisture uptake, machine-to-machine variation — sits
squarely in that clause.  The *requirement* for an extra factor is cited; its numeric
value (4.0) stays this project's own choice.  CF structural member (keel bar, boss pins,
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
**closed inner-neck tube** running the full length along the centerline (X ≈ −170 mm),
connecting the cargo-bay interior to the rear engine-room interior (see §7.3 and AGENTS.md).
The keel passes *through* this closed neck, so "held by foam alone" is a worst-case
assumption: **bonding the keel to the inner-neck wall is an available hard load path**
and should be evaluated in the keel re-evaluation and the cargo/middle + middle/rear joint
design (TODO.md §1.1.1.0b).  The deflection below conservatively assumes no neck bond.
At 2g bending, the 73 mm unsupported span deflects:

```text
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

Two straight segments of CF-BAR-6X3 (carbon fiber flat bar, 6 mm wide × 3 mm thick):

| Segment | Hull Y range | Length |
| --- | --- | --- |
| Cargo | −71 → +132 mm | 203 mm (8.0 in) |
| Rear | +203 → +384 mm | 181 mm (7.1 in) |

Lap splice: cargo segment extends 50 mm AFT of cargo/middle joint (into middle foam zone);
rear segment extends 50 mm FORWARD of middle/rear joint.  Overlap = **100 mm (3.9 in)**;
bonded with West System 105/206 + peel-ply prep.  Total two-segment mass ≈ 18 g.

Bar orientation: **3 mm flat (X, lateral) × 6 mm vertical (Z)** — maximises second moment
of area in the primary bending axis (pitch / vertical bending).

```text
I_z = (3 × 6³) / 12 = 54 mm⁴
```

Bending adequacy (2g pitching, forward fuselage cantilevered from wing spar station
Y ≈ +30 mm to head/cargo joint Y ≈ −71 mm, arm L = 101 mm):

```text
Head section mass (forward of wing station):  m_fwd ≈ 237 g (shell) + ~300 g (avionics, wiring) ≈ 537 g
2g load:  F = 2 × 0.537 × 9.81 = 10.5 N
Bending moment at wing station:  M = F × L = 10.5 × 101 = 1061 N·mm
Extreme fiber stress:  σ = M × c / I = 1061 × 3 / 54 = 58.9 N/mm²
CF tensile strength:  σ_u = 1500 N/mm²
FOS = 1500 / 58.9 = 25.5  ✓  PASS (>1.5 required)
```

Analogous check for aft fuselage (rear section mass ≈ 314 + 300 = 614 g, arm 181 mm):

```text
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
Commo/XCVR antenna designs should reference this counterpoise wire, not the CF bar.

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

```text
Outer bounds:  X[−257.6 .. −81.1]  Z[+0.5 .. +158.6]
Width = 176.5 mm (6.95 in),  height = 158.2 mm (6.23 in)
Section type:  CLOSED (full ring possible; belly closed at Z ≈ 0)
Inner skin (2 mm wall):  X[−255.6 .. −83.1]  Z[+2.5 .. +156.6]
Inscribed rectangle:  172.5 × 154.1 mm
Keel bar notch required: 3.5 mm wide × 1.0 mm deep at X = −170 mm, Z_bottom
```

**Rear, Y = +290 mm (landing load / anti-ovalisation):**

```text
Outer bounds:  X[−235.5 .. −116.0]  Z[+11.9 .. +152.4]
Width = 119.5 mm (4.70 in),  height = 140.5 mm (5.53 in)
Section type:  CLOSED (cone is closed at all Y in rear section)
Inner skin:  X[−233.5 .. −118.0]  Z[+13.9 .. +150.4]
Inscribed rectangle:  115.5 × 136.5 mm
```

**Middle/Rear joint, Y ≈ +203 mm:**

```text
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
4. Add keel-bar notch: 3.5 mm wide × 6 mm deep slot centered at X = −170 mm, Z_bottom.
5. Export as DXF to `airframe/diagrams/ring_frames/`.
6. Water-jet or CNC-cut from 2 mm carbon fiber plate stock (CF-PLATE-2MM BOM item).

### 5.5 Ring Pocket Features (implemented in shells)

A 2.5 mm wide (hull Y) × 1.0 mm deep groove is cut around the inner perimeter at each
ring station.  The CF plate slides into this groove and is epoxy-bonded before foam pour.
See §7 for the exact cutter geometry applied to each shell.

### 5.6 BOM and Build Guide (Step 5)

**SUPERSEDED 2026-08-25 (U4, SPAR-01) — the cargo Y=+30 ring is retired, not
finalized.** §1 and §5.1's own load-station table already anticipated this
station's job (anti-ovalisation at the spar pin), but the wing-root repair
plan (`docs/plans/2026-08-24-001-fix-wing-repair-root-joint-plan.md`) found
the load itself had changed: the spar no longer carries through the
fuselage (SPAR-01, `airframe/wings-nacelles/WBS.md` §1.1.2), and this
station's own bottom chord is cut away by the clamshell aperture (a
three-sided frame, not a ring — see that WBS.md's SPAR-01 finding 3), so it
never actually closed the couple it was sized for. Two new CF thwarts (fore
Y −40, aft Y +118, same 2 mm CF-PLATE-2MM stock and locating-groove pattern
as this section) replace it — sized and re-verified in
`tools/wing_spar_carrythrough.py`'s `report_thwart()` (FOS 8.5/8.7 against
the same conservative 300 MPa stand-in this section used) and cut in
`add_structural_features.py` `RING_POCKETS["cargo_Yn40"]`/`["cargo_Y118"]`.
The cargo_Y30 pocket is gated off in `merge_cargo_interior.py`
(`RING_Y30_ENABLED = False`), not deleted — its own DXF was already
PROVISIONAL (§5.4, blocked on the MESH-01 fragmented-mesh defect), so no
finalized part is lost by retiring it.

CF-PLATE-2MM notes update:

- Station count: 3 total tracked (2 active + 1 retired) — active: cargo
  Y −40 mm (fore thwart) and Y +118 mm (aft thwart); retired: cargo Y +30 mm
  (superseded above); unchanged: rear Y +290 mm (landing zone, still active)
- Ring types: rear Y +290 remains a full closed ring; the two thwarts are
  narrower bands (2 × 25 mm CF plate section, not a full-profile plate) —
  see `wing_spar_carrythrough.py` `report_thwart()`, not the §5.2/§5.3
  full-ring-profile method (that method still applies unchanged to Y +290)
- Estimated mass: thwart pair ≈ 28 g (0.062 lbm) combined (2 × 14 g,
  `wing_spar_carrythrough.py`), replacing the retired Y +30 ring's
  ~78 g estimate (§5.1/WBS.md SPAR-01) — a net saving of ≈50 g (0.11 lbm)
- Y +290 rear ring: unchanged from this section's original figures

`REVN_BUILD_GUIDE_24IN.md` keel datum table: replace stale 91/165/251/320/388 mm
stations with the new hull-Y ring/thwart stations −40 mm, +118 mm, and +290 mm.

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

```text
F_per_skid = 2.5 × 73.5 / 2 = 91.9 N per skid
Rod in bending: arm from skid tip (Y ≈ +380) to joint (Y ≈ +203) = 177 mm
M_max = 91.9 × 177 = 16 266 N·mm
CF rod (4 mm OD, 3 mm ID — assumed hollow): I = π(4⁴ − 3⁴)/64 = π(256−81)/64 = 8.59 mm⁴
σ = M × c / I = 16 266 × 2 / 8.59 = 3789 N/mm²
CF tensile strength ≈ 1500 N/mm² → FOS = 0.40  ✗  FAIL for hollow rod
```

**Switch to solid CF-ROD-4MM (4 mm OD, solid):**

```text
I_solid = π × 4⁴ / 64 = 12.57 mm⁴
σ = 16 266 × 2 / 12.57 = 2588 N/mm²
FOS = 1500 / 2588 = 0.58  ✗  STILL FAIL at 2.5g for full overhang
```

This confirms that a single 4 mm CF rod cannot carry the full 2.5g skid bending load over
177 mm (7.0 in) as a pure cantilever.  However, the actual load path is more complex:
the foam fill provides distributed elastic support along the skid arm, and the skid arm
PETG skin (2 mm CF-PETG) carries significant shear.  Combined:

```text
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

```text
σ_tension = F / A = 91.9 / (π × 2²) = 7.3 N/mm²  << σ_u 1500 N/mm²
FOS = 205  ✓  PASS  (extreme margin; CF-ROD-4MM is more than adequate as tie-rod)
```

### 6.3 Bore Positions and Depth

Bore depth: 30 mm into EACH section (middle + rear) = 60 mm total rod engagement.
CF rod length: 62 mm per skid arm (allowing 1 mm insertion clearance each end).

Bore centers (hull frame, Y-axis aligned):

| Skid | X_bore (mm) | Z_bore (mm) | Y range (mm) |
| --- | --- | --- | --- |
| Port | −202.0 | 18.0 | +173 → +233 |
| Stbd | −135.0 | 20.0 | +173 → +233 |

Bore diameter: 4.2 mm (CF rod 4.0 mm OD + 0.1 mm clearance each side).

### 6.4 Re-derivation against a nose-high/asymmetric strike (2026-08-25)

*(Owner-directed: "canonically [the skids are] part of the propulsion
system, not landing gear, but they'll be the first things hitting if the
aircraft lands nose high." §6.2's own case is symmetric-only — both skids
sharing the load, wings level — and never covered a single-skid-first
touchdown. This unit re-derives §6.2 with the corrected AUW first, since
§2's own 2026-08-22 note already flags every number in §3–§7 as computed
from a stale, doubled mass budget, then adds the case §6.2 never had.)*

**Mass basis:** the owner directed using the **Phase 11 (full system) AUW,
4,273 g (9.42 lbm, `README.md`)** for this re-derivation specifically, so it
does not need re-deriving again once the aircraft reaches its final,
heaviest configuration. Total weight W = 4.273 kg × 9.80665 m/s² = **41.90 N**.
This supersedes §2's own Phase 5–10 corrected figure (36.8 N) *for this
section only* — §2 stays as the Phase 5–10 basis for the rest of this
document; do not silently propagate the Phase 11 figure elsewhere.

**Geometry re-measured directly from the published STL, not assumed.** §6.1's
"low-Z vertices" survey and §6.2's "approx 76 × 23 mm²" box-shell estimate
both predate this re-derivation and are **superseded by direct measurement**
below — they were never geometrically verified against a specific cross-
section, and the direct measurement found meaningful discrepancies with
both.

Sectioning `rear_shell24_2mm_repaired.stl` at 8 mm Y-intervals from the
middle/rear joint (Y = 204) to the tip (Y = 384) and identifying the two
discrete inner/outer loop pairs (not the whole-hull cross-section, which
also spans this X range and can be mistaken for the skid at a glance):

- The skid arm is a genuinely separate, thin-walled cantilevered tube only
  from roughly **Y ≈ 250 onward** to the tip — consistent with §6.2's
  177 mm moment-arm assumption (tip-to-joint), which this re-derivation
  therefore keeps.
- Measured outer cross-section near the tip: **≈ 24 mm (X) × 23 mm (Z)**,
  wall thickness ≈ 2 mm, material (annulus) area ≈ 138 mm² — matching
  independently via both a direct polygon slice and a `trimesh.split()`
  body-area check. **This is roughly 3× narrower than §6.2's assumed
  76 mm width** (76 was never a measurement; the "approx" in §6.2's own
  text was accurate self-disclosure).
- Approximated as a thin rectangular tube (24 × 23 mm outer, 2 mm wall) for
  a bending second moment of area about the horizontal (X) axis:
  `I = (24×23³ - 20×19³)/12 ≈ 12,900 mm⁴` — this **replaces** §6.2's
  `I_PETG ≈ 438,080 mm⁴` box-shell estimate, which used the wrong width.

**Independent finding, FIXED 2026-08-25 — the CF rod did not run through the
measured skid tube.** Probing `X = -202, Z = 18` (the previously documented/
bored station, §6.3) against the sectioned loops at Y = 210 (inside the
bore's own Y-range, 173–233): the nearest material was the **main horseshoe
ring's own wall**, 2.09–3.46 mm away — the discrete skid tube (centered ≈
X = -224 at this Y) was 13.17 mm away, outside the bore's clearance
entirely. **Root cause found and corrected** (`LG-26`,
`airframe/landing-gear/WBS.md`): the tube's own hollow-cavity centerline was
re-measured continuously across its full span (`middle_shell24_2mm_
repaired.stl` Y=188–202, `rear_shell24_2mm_repaired.stl` Y=208–233 — it is
not yet a separate feature below Y≈188), and `SKID_ROD_BORES` in
`add_structural_features.py` re-sited to it: port moved to (-223.7, 18.5),
stbd to a deliberate compromise center (-122.0, 19.0) since stbd's measured
centerline has a genuine ~10 mm discontinuity at the print-split joint too
large for one straight rod to stay centered on both sides. Both shells
re-verified: `tools/validate_stls.py` 61/61 PASS, and the bore's nearest
material at 8 sampled stations per side is now 2.09–7.03 mm (was 13+ mm
everywhere) — the bore is inside the tube's cavity, not the ring wall, at
every checked station. The stbd compromise is a real improvement, not a
perfect fit; a slicer/test-fit check before fabrication is still warranted,
and building the rod as two independently-anchored segments (rather than one
straight rod) remains an option if the compromise proves inadequate — see
LG-26.

**Allowable:** **54 MPa (ASTM D790 three-point flexural strength, unreinforced
PETG, REF-MAT-002)** — superseding this section's initial use of REF-MAT-001's
48.41 MPa tensile strength as a bending proxy. REF-MAT-002 (added 2026-08-25,
`REFERENCES.md`) is a genuine flexural test (the correct test type for this
failure mode), not a proxy, and its 50 MPa ANSYS FEA cross-check for pure
PETG (7.4% error vs. the 54 MPa experimental figure) supports citing it with
confidence. **What it does not resolve:** no print-orientation-specific data
(loading axis vs. layer-stack axis) exists in this source either — its own
conclusions cite "anisotropic fibre orientation" as a source of nonlinearity
but give no interlayer/Z-axis strength figure, and this repo has no record of
the rear shell's actual print orientation. Treat the FOS figures below as
upper bounds pending (a) confirmation the skid tube's bending axis sees the
tested (in-plane) direction rather than the weaker interlayer direction, and
(b) a coupon test of the actual tube geometry, not a bulk bar/dog-bone.

**Load cases** (2.5 g factor per §3's existing "hard landing (vertical)"
convention — kept, not re-derived, since no bound on nose-high pitch angle
or sink rate exists anywhere in this repo's flight-envelope docs to justify
a different factor). With the rod now geometrically coupled to the tube (the
fix above), its stiffness share is credited via a simple parallel-EI split
(`EI_skin = E·I_skin`, `EI_rod = 135,000 MPa × 12.57 mm⁴` for the solid
4 mm CF rod) instead of assuming it carries zero load:

| Case | Skin material (flexural) | F | M = F × 177 mm | Skin share of M | σ = M·c/I (c = 11.5 mm) | FOS |
| --- | --- | --- | --- | --- | --- | --- |
| Symmetric flat landing | plain PETG, 54 MPa / 2.76 GPa | 52.4 N | 9,275 N·mm | 94.1% | 7.78 MPa | **6.94 — PASS** |
| Nose-high, single skid | plain PETG, 54 MPa / 2.76 GPa | 104.75 N | 18,541 N·mm | 94.1% | 15.55 MPa | **3.47 — still below the 4.0 target** |
| Nose-high, single skid | **20% CF-PETG, 77 MPa / 6.67 GPa (REF-MAT-002 Table 4)** | 104.75 N | 18,541 N·mm | 98.1% | 16.20 MPa | **4.75 — PASS** |
| Symmetric flat landing | 20% CF-PETG, 77 MPa / 6.67 GPa | 52.4 N | 9,275 N·mm | 98.1% | 8.11 MPa | **9.49 — PASS** |

**Conclusion.** The rod-siting fix alone is not enough to close the nose-high
gap: a solid 4 mm CF rod is too slender to meaningfully stiffen even this
thin shell (it carries only ~2–6% of the moment once actually coupled), so
correcting its position improves plain-PETG FOS only from 3.27 to 3.47 —
real, but short of the 4.0 target. **What closes it is the material switch**
(owner-directed, 2026-08-25): specifying 20% CF-PETG for the rear (and
middle) fuselage skin, per REF-MAT-002's measured 77 MPa flexural strength /
6.67 GPa flexural modulus at that fiber fraction, gets to FOS 4.75. This is
fiber-fraction-specific — REF-MAT-002's own data shows **10% CF-PETG is
*worse* than plain PETG** (43 MPa flexural, likely poor fiber-matrix cohesion
at low loading) and that a nominal 30% blend (80 MPa/7.01 GPa) was the
paper's own custom lab specimen, not a normal retail product — so the BOM
and every citation must say **20% CF**, not a bare "CF-PETG" that could be
read as any fraction. 20% was selected over the paper's stronger 30% figure
specifically because a genuine, explicitly-labeled 20%-CF filament is a real,
verifiable commercial product ("3D Maker Engineering" PETG-CF Pro Series,
confirmed via direct vendor-page quote), whereas a true 30%-CF retail
filament could not be verified to exist. See the BOM/material-spec update
this drove (`current-specification/bom_revS.csv`, `REFERENCES.md`
REF-MAT-002). The symmetric case was never actually a concern (FOS 6.94–9.49
across all variants checked here) — it's included for completeness, not
because it was ever in doubt.

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

Pins are positioned on an r = 35 mm circle centered on the joint cross-section centroid,
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

- The head is a **forward cantilever** (~0.59 kg of shell + Shepherd avionics + bow
  pod + foam, CG at hull Y ≈ −157 mm).  Its inertial loads ARE reacted at the head/cargo
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
9 g crash moment gives a peak fiber stress **M/S ≈ 0.7 MPa** — far below the CF-PETG and
epoxy allowables (≈ 5 MPa for the PETG-bond-limited case; this figure predates any cited
source and is carried here as the repository's conservative working placeholder for a
bonded/adhesive-limited joint — **REF-MAT-001** (`REFERENCES.md`) now provides a real,
peer-reviewed ASTM D695 *bulk compressive* figure for 20 %-CF-PETG, ≈47–60 MPa, an order
of magnitude above this placeholder, but bulk compression is not the bond/peel mode this
figure is meant to bound, so it does not replace it here — see REF-MAT-001's own entry for
what it does and does not cover).  **The joint is not strength-limited.**  What is actually required is peel resistance, alignment, and
anti-ovalisation of the thin section, plus the AGENTS.md fabrication standard's
"minimum 2-wall contact annulus and positive-stop shoulder."

**Design — internal bonded splice collar (`PRINT-HEAD-CARGO-COLLAR`).**  A printed
CF-PETG ring, profile = the head inner-wall contour at Y = −79 mm inset 2 mm, 2 mm wall,
L = 16 mm (8 mm into each section), centered on the joint (hull Y −79..−63).  It:

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
S_x = 31 984 mm³.  Peak fiber stress at 9g crash = 20 260 / 31 984 = **0.63 MPa** — well
below the ~5 MPa CF-PETG/epoxy allowable.  **Not strength-limited**, same conclusion as
Joint 1; governing requirements are peel resistance, alignment, and anti-ovalisation.

**Design — internal bonded splice collar (`PRINT-CARGO-MIDDLE-COLLAR`).**  Profile = MIDDLE
inner-wall contour at hull Y = +137 mm (clean, 5.9 mm aft of the joint), inset by a 2 mm
bond gap, 2 mm wall.  L = 16 mm (8 mm into each section), centered on hull Y = +131.1 mm
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
442 mm, S_x = 27 713 mm³.  Peak fiber stress at 9g crash = 7 362 / 27 713 =
**0.27 MPa** — even lower than Joint 2, well below the ~5 MPa allowable.  **Not
strength-limited.**

**Design — internal bonded splice collar (`PRINT-MIDDLE-REAR-COLLAR`).**  Profile = MIDDLE
inner-wall contour at hull Y = +195 mm (clean, 8.4 mm forward of the joint), inset by a
2 mm bond gap, 2 mm wall.  L = 16 mm (8 mm into each section), centered on hull
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
- [ ] Add FlightEngineer/battery boss pattern to `middle_canonical_shell24.scad` (§1.4.5)
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
