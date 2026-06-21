# Serenity UAV — Landing Gear Structural Analysis

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Revision:** R4 (2026-06-20) — Strong-Leg + per-arm ductile wire-loop fuse (final hybrid)

> "She's tore up plenty, but she'll fly true." — Mal, on a ship that's seen worse landings than this one's rated for.

> **Rev R3** (Strong-Leg + elastic spring-steel leaf) **superseded 2026-06-20.** The
> spring-steel leaf was replaced by a much lighter **per-arm ductile wire-loop crash
> fuse** (one per arm, 8 total) — see §0 for why. The widened-trunk geometric fix from
> R3 §4.5 is **retained as a backstop**. Rev R2 / R1.4 / R1.3 / R1.2 / R1.1 / R1 remain
> superseded. Energy numbers (§3) still carry forward unchanged.

---

## 0. What Changed in Rev R4, and Why

Rev R3 added a 163 g elastic spring-steel leaf to fix a real problem found by rigorous
re-verification: the bare CF-PETG Strong-Leg's trunk is a geometrically fixed single
point of failure, and the system is far stiffer than earlier revisions assumed. That
fix worked, but elastic energy storage is fundamentally limited (σ²/2E) — absorbing
14 J elastically and recoverably needs a genuinely large amount of spring-steel volume,
and even the carefully-sized R3 leaf left an unresolved "what if the spring fractures
instead of bending" force-spike risk (§4.4 of Rev R3).

**Plastic (ductile) deformation stores energy far more densely than elastic deformation**
— typically 15–60× more energy per unit volume, because it isn't limited to staying
below yield. Rev R4 exploits this directly: a small **ductile wire ring**, installed
between each arm tip and its hull boss (replacing the rigid spigot), is designed to
plastically flatten under overload — a well-characterized, four-plastic-hinge ring
collapse mechanism — absorbing the full worst-case per-leg energy in **~73 g total
for 8 fuses**, versus 163 g for one spring leaf, **while also restoring the original
two-independent-arms redundancy story that motivated the Strong-Leg's geometry in the
first place**: one fuse can fire while the other arm's fuse and the rest of the
structure stay intact and load-bearing.

The trade is reusability: the wire ring takes a permanent set once it fires (it doesn't
spring back), so it's a single-use, field-replaceable item — exactly like the existing
M3/M4 nylon fuse bolts already specified elsewhere in this design, and consistent with
Requirement 3's "defined, observable, field-repairable" sacrificial-element intent. A
flattened ring is also a far more obvious, unambiguous "this needs replacing" indicator
than an internal CF-PETG crack would have been.

The widened CF-PETG trunk (Rev R3 §4.5) is kept as a secondary backstop in case both of
one leg's wire fuses are somehow exhausted on a single severe, asymmetric landing — at
negligible extra mass (~4 g/leg).

---

## 1. Purpose and Requirements

This document provides the structural analysis and design rationale for the
Serenity UAV main landing gear.  The landing gear system must:

1. **Survive a 6 ft (1.829 m) vertical drop** onto hard level ground at
   design all-up weight (AUW) without cracking the hull shell.
2. **Absorb lateral loads** from not-quite-vertical landings (design case ±15°
   from vertical).
3. **Fail internally under overload, progressively rather than catastrophically** — if a
   leg assembly is overstressed, the failure mode must be a defined, observable, partial
   degradation that still leaves the aircraft supported, not a single catastrophic event
   that drops the aircraft or cracks the cargo shell or hull boss.
4. **Be field-replaceable** using only common hand tools.
5. **Provide 3-D lateral stability** — legs must resist tipping loads in
   both the hull-X (lateral) and hull-Y (fore-aft) directions.

The landing gear does NOT need to be reusable after a 6 ft drop.

---

## 2. Aircraft Data and Strong-Leg Geometry

### 2.1 All-Up Weight

| Configuration | AUW |
|---|---|
| Phase 5–10 (no aft EDF) | **6.10 lbm (2,768 g)** |
| Phase 11 (full system, design case) | **6.90 lbm (3,130 g)** |

The **Phase 11 AUW of 6.90 lbm (3,130 g) is the design case**.

### 2.2 Landing Gear Configuration (Rev R4)

- **4 × Strong-Leg assemblies** — one per cargo belly corner; each assembly: 1
  single-piece CF-PETG Strong-Leg (foot point + 2 hull-attachment arms, trunk widened
  per §4.5) + 2 ductile wire-loop fuses (one per arm, between arm tip and hull boss) +
  1 canonical TPU 95A foot pad + 2 hull boss sockets (integral to cargo shell) + fuse
  bolts per boss.
- **8 ductile wire-loop fuses total** (2 per leg × 4 legs) — see §4.3.
- **8 hull boss sockets total** (2 per leg × 4 legs), CF-PETG, integral to the cargo shell.
- **4 × TPU 95A canonical foot pads** — existing Thingiverse-derived geometry, unmodified
  outer form; friction and surface compliance.
- **2 × rear skids** — integral to the horseshoe ring of the middle section; unrelated
  subsystem, unchanged by this revision (see §10).

### 2.3 Strong-Leg Geometry (measured from `strong-leg.stl`)

The Strong-Leg is built by FreeCAD boolean operation directly on the existing,
already-validated single-blade canonical leg (`leg_1_scaled24.stl`…`leg_4_scaled24.stl`,
misubisu Thingiverse hull, CC BY 4.0): the leg is stood up vertical, **duplicated**, the
duplicate **rotated 30° about the leg's own vertical centreline**, and the two **unioned**
into one watertight CF-PETG part. All dimensions below were measured directly from the
exported mesh (3,301 vertices, 6,598 faces, single body, volume 9,612 mm³) using
`trimesh` cross-sectioning, not assumed from nominal CAD intent — consistent with the
project's "actual physical build" philosophy (`CLAUDE.md`).

**Overall envelope:** 36.1 × 36.8 × 79.8 mm — the 79.8 mm vertical extent matches the
original single-blade leg's 79.84 mm strut length.

| Feature | Description |
|---|---|
| Foot point | Single point at the bottom; both source legs' feet coincide here |
| Trunk (foot → fork) | Single combined load path, local height ≈ 0–20 mm above foot |
| Fork transition | Complex multi-lobe cross-section, local height ≈ 20–44 mm above foot |
| Arm 1 | Fully separate prong, local height ≈ 44–80 mm above foot; tip carries wire fuse 1 → hull boss 1 |
| Arm 2 | Fully separate prong, same height range; tip carries wire fuse 2 → hull boss 2 |

**Foot-to-arm-tip vectors** (measured, one corner instance — also the basis for the
demonstration STLs in §16):

| | Vector (local frame) | Length | Angle from vertical |
|---|---|---|---|
| Foot point | (−114.72, −142.65, −13.00) | — | — |
| Arm 1 tip | (−96.30, −111.35, 66.17) | 87.1 mm | 24.6° |
| Arm 2 tip | (−84.86, −124.32, 66.17) | 86.6 mm | 23.9° |

Angle between the two arm vectors (azimuthal spread): **≈28°** measured (30° design
rotation; the difference is centroid-measurement noise on the tapered tip).

**Cross-sectional areas** (horizontal slices, perpendicular to the vertical working axis):

| Location | Local height above foot | Area (mm²) | Approx. rectangle |
|---|---|---|---|
| Foot-adjacent trunk (as-printed; widened target in §4.5) | ~3 mm | **52.5** (→ widened to ≈117) | 7.41 × 8.77 mm (→ ≈9.9 × 11.8) |
| Trunk, growing toward fork | ~15 mm | 183.3 | 16.6 × 18.1 mm |
| Each arm, steady mid-span | 44–58 mm | **58.5** | 8.13 × 9.55 mm |
| Each arm tip (now carries a wire fuse instead of plugging directly into the boss) | 60–67 mm | 2–40 (taper) | — |

**FreeCAD assembly status (2026-06-20):** four corner copies exist in
`airframe/freecad/assembly/SerenityAssembly.FCStd` as Boolean-result objects `Union`,
`Union001`, `Union002`, `Union003` (90°-stepped rotation: 0°/90°/180°/270°), all four
confirmed in their correct corner locations. **Z-leveling rule:** if the 4 feet deviate
in Z once placed, all 4 are aligned to the **most negative (lowest) Z** of the four.

> **TODO LG-10:** Bake the 4 placed Strong-Leg corner copies to hull frame and export 4
> placed STLs for printing. **BLOCKS hull boss integration (LG-02) and leg printing (LG-05).**

---

## 3. Impact Velocity and Kinetic Energy

Unchanged from Rev R1 — AUW and drop height are unaffected by the fuse-design change.

### 3.1 Free-Fall Velocity

```text
v = √(2 g h) = √(2 × 386.09 in/s² × 72.0 in) = 235.8 in/s  (19.65 ft/s, 5.99 m/s)
```

### 3.2 Total Kinetic Energy at Impact

```text
KE_total = ½ m v² = 496.8 in·lbf  (56.1 J)
```

### 3.3 Energy per Leg Assembly

```text
KE_per_assy (6 ft, full AUW)   = 56.1 / 4 = 14.04 J  (124.2 in·lbf)
KE_per_assy (1.5 ft, full AUW) =  3.51 J  (elastic-check energy, TODO.md LG-06)
```

---

## 4. Rigorous Force, Stiffness, and Fuse-Collapse Analysis (Rev R4)

### 4.1 System Stiffness (No Spring — Foot + Leg Only)

Without a spring in the load path, the relevant elastic stiffness prior to any fuse
activating is the same one identified as too-stiff in the Rev R3 re-verification:

```text
k_leg (trunk + arms in series, axial)      ≈ 6,700 N/mm
k_foot (TPU 95A, 43.94×43.94×9.04 mm pad)  ≈ 1,870 N/mm
k_system (foot + leg in series)            ≈ 1,460 N/mm
```

This stiffness governs the small elastic deflection **before** the wire fuses begin to
collapse (§4.3) — it is not the mechanism that absorbs the bulk of the 14.04 J, the
fuses are.

### 4.2 The Trunk Is Still a Geometrically Fixed Weak Point (Unchanged Finding)

```text
Max achievable trunk yield force (as-printed, 52.5 mm² nominal, 100% infill) ≈ 2,740 N
Combined-arm yield force (vertical, even split, 58.5 mm² nominal arms, 40% infill) ≈ 4,105 N
Trunk effective area needed to exceed the arms' combined capacity ≈ 74.6 mm²
```

This finding from Rev R3 is unchanged by the fuse swap — infill alone cannot fix it,
which is why the trunk is still widened geometrically (§4.5).

### 4.3 Per-Arm Wire-Loop Fuse — Sizing

**Geometry:** a closed ductile-wire ring (mean radius `RING_R` = 12 mm, wire diameter
`WIRE_D` = 4.0 mm, solid round cross-section), oriented with its plane containing the
arm's load axis, with a short straight mounting tab at each end (into the hull boss
bore and into the CF-PETG arm tip respectively) — replacing the rigid spigot that
previously plugged the arm directly into the boss. SCAD source:
`airframe/openscad/fuselage/wire_loop_fuse.scad`. Under axial overload the ring
progressively flattens via a classic four-plastic-hinge ring-collapse mechanism (two
hinges at the load points, two at 90° from them).

```text
Material: ductile spring-steel wire, tempered for plastic ductility (NOT full-hard) — flow stress ≈ 550 MPa
M_p (plastic moment, solid round wire) = σ_flow × WIRE_D³ / 6 ≈ 5,867 N·mm
P_collapse (per fuse, axial along the arm) = 4 × M_p / RING_R ≈ 1,956 N
Usable crush stroke ≈ RING_R = 12 mm
Energy capacity per fuse over that stroke ≈ 23.5 J  (1.7× the full 14.04 J per-leg worst case,
                                                       sized independently per arm — NOT a 50/50 split —
                                                       as a margin against uneven/asymmetric landings)
Mass per fuse ≈ 9.1 g  →  8 fuses (2/leg × 4 legs) ≈ 73 g total
```

### 4.4 Worst-Case 6 ft Drop — Full Force/Energy Sequence (Symmetric Nominal Case)

```text
Total leg (vertical) force at which BOTH arm fuses begin to collapse simultaneously
  = 2 × P_collapse × cos(24.3°) ≈ 3,565 N

Elastic energy absorbed before collapse begins (at k_system ≈ 1,460 N/mm) ≈ 4.35 J
Remaining energy absorbed by both fuses crushing at the ≈3,565 N plateau ≈ 9.69 J
  → vertical stroke needed ≈ 2.7 mm → axial stroke per fuse ≈ 3.0 mm (of 12 mm available — 4× reserve)
```

**Margins at the fuse plateau force (3,565 N):**

```text
vs combined-arm yield (4,105 N)         : 1.15×
vs widened-trunk yield (4,926 N, §4.5)  : 1.38×
vs hull boss bearing capacity (10,020 N): 2.81×
```

**This is the key result of Rev R4: in the nominal symmetric 6 ft full-AUW drop, the
wire fuses absorb essentially all of the energy beyond the small initial elastic phase,
at a force comfortably below both the arms' and the widened trunk's yield capacity. The
CF-PETG structure is never expected to yield at the design case — only the
field-replaceable wire fuses do, using only ~3 mm of their 12 mm available stroke.**

**Asymmetric / single-arm-worst-case check:** because each fuse is independently sized
for the *full* 14.04 J (not half), a severely uneven landing that dumps the entire
per-leg energy through one arm alone still uses only 7.2 mm of that fuse's 12 mm
stroke (§4.3) — comfortable margin, and the other arm's structure is never engaged at
all in that scenario.

### 4.5 Widened Trunk — Retained as a Secondary Backstop

Unchanged from Rev R3: the trunk's local cross-section is widened geometrically (not
just infill) so that if both of one leg's fuses are ever exhausted, the arms still fail
before the trunk:

```text
New trunk cross-section (100% infill): ≈9.9 × 11.8 mm (nominal ≈117 mm², up from 7.41 × 8.77 mm / 52.5 mm²)
New trunk yield force ≈ 4,926 N  vs combined-arm yield ≈ 4,105 N  →  arms fail first, 1.20× margin
Mass cost: ≈1 g per leg, ≈4 g for the aircraft
```

> **TODO LG-12:** widen the trunk's local cross-section to ≈9.9 × 11.8 mm (local Z =
> 0–20 mm above the foot) in the FreeCAD/Blender source, print that zone at 100%
> infill. **BLOCKS first flight.**

### 4.6 Hull Boss Bearing Check

```text
Boss bore ≈ 9.7 × 8.7 mm, Boss OD ≈ 13 × 12 mm (2-wall annulus per CLAUDE.md)
A_bearing per boss = 71.6 mm², A_bearing per leg (2 bosses) = 143.2 mm²
F_bearing_capacity ≈ 70 MPa × 143.2 mm² ≈ 10,020 N per leg

Margin vs fuse-collapse plateau force (3,565 N) = 2.81×
Margin vs widened-trunk yield (4,926 N, last-resort backstop) = 2.03×
```

**The hull boss — and by extension the cargo shell — is well protected at every stage
of this analysis**, with no thin-margin force-spike scenario remaining (contrast with
the Rev R3 spring's 1.16× spike-case margin, which this revision eliminates).

### 4.7 Euler Column Buckling Check (Arm)

```text
Post-fork arm length ≈ 25.1 mm, I_weak ≈ 428 mm⁴
P_crit = π² E I / L² ≈ 36,990 N  →  margin ≥ 8.0× even at the highest force considered (4,926 N)
```

No buckling risk.

---

## 5. Lateral Load Analysis (±15° Off-Vertical)

Using the fuse-collapse plateau force (§4.4) as the governing total leg force, since the
fuses cap how much force the structure ever sees:

```text
F_vert_component    = 3,565 × cos(15°) ≈ 3,444 N
F_lateral_component = 3,565 × sin(15°) ≈    923 N
F_shear_per_bolt (2 bosses, 2 bolts per boss = 4 bolts) = 923 / 4 ≈ 231 N
```

```text
Fuse capacity (1× M3 PA6 nylon, 40 MPa shear) = 283 N per bolt
Margin: 283 / 231 = 1.22×
```

This is workable with the standard M3 nylon bolt at the fuse-capped force level (unlike
the Rev R3 pre-spring-collapse reference force, which exceeded it). **Recommendation:**
keep 2× M3 PA6 nylon bolts per boss (4 per leg, 16 total) for a comfortable margin; the
M4 upsizing proposed in Rev R3 is no longer necessary now that the wire fuses cap the
peak force the structure can transmit.

> **TODO LG-13 (revised):** retain 2× M3 × 16 mm PA6 nylon SHCS per boss (16 total);
> Rev R3's M4 upsizing recommendation is superseded now that the wire fuses cap peak
> force at the §4.4 plateau.

---

## 6. Progressive Failure / Fuse Strategy (Rev R4)

| Level | Element | Activates at | Behavior |
|---|---|---|---|
| 1 (elastic, no damage) | TPU foot + rigid CF-PETG leg | up to ≈3,565 N total leg force | Fully elastic, fully recoverable — ordinary hard landings cause no damage anywhere |
| 2 (primary sacrificial fuse, per arm) | Ductile wire-loop fuse (one per arm, 8 total) | ≈1,956 N axial per fuse (≈3,565 N total leg, both arms, symmetric case) | Ring progressively flattens via a 4-hinge plastic mechanism; absorbs the bulk of the 6 ft worst-case energy at a near-constant, predictable force; visibly deformed afterward — unambiguous field-inspection indicator |
| 3 (lateral fuse) | M3 PA6 nylon bolts, 2 per boss | ≈283 N shear per bolt | Retention bolts shear before the hull boss is overloaded laterally |
| 4 (backstop, arm-first hierarchy) | One arm of the Strong-Leg | only if a fuse's 12 mm stroke is fully exhausted | Arm cracks before the (widened) trunk, 1.20× margin (§4.5) |
| 5 (last-resort, not expected to be reached) | Widened trunk | only if both arms have already failed | Single load path; kept above the arms' combined capacity by design |
| 6 (protected at all credible loads) | Hull boss / cargo shell | > 70 MPa bearing (§4.6) | ≥2.0× margin at every force level considered in this analysis — the hull is never expected to see damaging load |

This satisfies Requirement 3 (§1) with a clean, hand-calculable margin at every stage:
the wire fuses are the **intended, designed, predictable** sacrificial element (Level 2),
genuinely redundant per arm, and the CF-PETG structure (Levels 4–5) and hull (Level 6)
are not expected to be engaged at all in the nominal 6 ft full-AUW design case — they
remain as backstops for asymmetric or beyond-design overload only.

---

## 7. Foot Interface (Canonical TPU Foot Pad)

Unchanged from Rev R2: 43.94 × 43.94 × 9.04 mm TPU 95A, canonical Thingiverse-derived
geometry, unmodified outer form. No spring root to accommodate (Rev R3's spring leaf is
removed) — the foot socket reverts to the Rev R2 sizing, fitted to the leg's own foot
cross-section:

| Parameter | Value |
|---|---|
| Socket location | Top face (Z_max = 9.04 mm local), centred |
| Socket bore | 7.6 × 9.0 mm (leg foot cross-section 7.41 × 8.77 mm + 0.2 mm clearance) |
| Socket depth | 5.0 mm (leaves 4.0 mm TPU floor) |
| Retention | 1× M2.5 × 12 mm SS through-bolt + thin CA at socket walls |

---

## 8–9. (Reserved — merged into §4.6 and §6)

---

## 10. Rear Skids

Unchanged from Rev R1 — unrelated subsystem.

The two rear skids are built into the horseshoe ring of the middle section
(see `airframe/openscad/fuselage/middle_canonical_shell24.scad`).  They
must be reinforced with a CF rod (3 mm diameter, pultruded carbon fibre)
before first flight.

- CF rod OD: 3 mm; modulus: ~130 GPa
- Length per skid: approximately 140 mm
- Adhesive: thin cyanoacrylate

---

## 11. Materials Specification

### 11.1 Ductile Wire-Loop Fuse (8 per aircraft, 2 per leg — new in Rev R4)

| Parameter | Value |
|---|---|
| Material | Ductile spring-steel wire, tempered for plastic ductility (flow stress ≈550 MPa) — NOT full-hard temper |
| Geometry | Closed ring, mean radius 12 mm, wire diameter 4.0 mm, with two straight mounting tabs (8 mm long, 6×3 mm, Ø2.5 mm pin hole) |
| Source | `airframe/openscad/fuselage/wire_loop_fuse.scad` (PART="nominal" / PART="deformed") |
| Mounting | Pinned: one tab into the hull boss bore, one tab into the CF-PETG arm tip socket |
| Estimated mass | ≈9.1 g each × 8 = **≈73 g total** |

### 11.2 Strong-Leg (4 per aircraft, one per corner; trunk widened per §4.5)

| Parameter | Value |
|---|---|
| Material | CF-PETG |
| Source | `airframe/stls/fuselage/landing-gear/strong-leg.stl`, trunk zone re-modeled wider per §4.5 |
| Overall envelope | 36.1 × 36.8 × 79.8 mm (foot to arm tips) |
| Layer height | 0.15 mm |
| Perimeters | 4 |
| Trunk zone (local Z 0–20 mm above foot) | Widened cross-section ≈9.9 × 11.8 mm, **100% infill** |
| Arms and fork | Unchanged geometry, 40% gyroid (CLAUDE.md minimum) |
| Print orientation | Upright, foot down |
| Estimated mass | ≈23 g each × 4 = ≈92 g total |

### 11.3 Hull Boss Sockets (8 per aircraft, 2 per corner)

| Parameter | Value |
|---|---|
| Material | CF-PETG |
| Geometry | OD ≈ 13 × 12 mm, bore 9.7 × 8.7 mm, depth ≥ 12 mm + fuse tab clearance |
| Integration | Union with `cargo_sect_shell24.scad` belly/side wall; 2 per corner |
| Fuse bolts | 2× M3 × 16 mm PA6 nylon SHCS per boss (§5) |

### 11.4 TPU Foot Pads (4 per aircraft, unchanged canonical geometry)

| Parameter | Value |
|---|---|
| Material | TPU 95A |
| Dimensions | 43.94 × 43.94 × 9.04 mm (unmodified outer form) |
| New feature | Top-face socket, 7.6 × 9.0 mm bore × 5.0 mm deep (§7) |
| Layer height | 0.20 mm |
| Infill | 25 % gyroid |
| Fasteners | 1× M2.5 × 12 mm SS through-bolt per foot |

### 11.5 Safety Cord

| Parameter | Value |
|---|---|
| Material | Dyneema SK75, 2 mm diameter |
| Break strength | ≥ 750 N (168 lbf) |
| Length per assembly | ≈ 400 mm (foot → leg bore → boss → anchor post inside hull) |
| Anchor (hull end) | Loop on printed anchor post stub (ANCHOR_POST_OD = 5 mm) |
| Anchor (leg end) | Loop through a tether hole near the foot, overhand knot |

---

## 12. Bill of Materials (per aircraft, 4 assemblies)

| Item | Qty | Description |
|---|---|---|
| Ductile wire-loop fuse | 8 | Spring-steel wire ring, 2 per leg (one per arm) — **new in Rev R4**, replaces Rev R3's spring leaf |
| Strong-Leg | 4 | CF-PETG, single-piece print, widened trunk per §4.5 |
| Hull boss socket | 8 | CF-PETG, integral to cargo shell; 2 per corner |
| TPU foot pad | 4 | TPU 95A, canonical Thingiverse geometry + top socket |
| M3 × 16 nylon SHCS | 16 | Boss retention / lateral fuse (2 per boss, 4 per corner) |
| M2.5 × 12 SS bolt | 4 | Foot retention (1 per foot) |
| Fuse mounting pin, Ø2.5 mm | 16 | 2 per fuse (boss-side + arm-side tab), 8 fuses |
| Dyneema SK75, 2 mm | 1.6 m | Safety cord (4 × 400 mm) |
| 3 mm CF rod | 280 mm | Rear skid reinforcement (2 × 140 mm, unrelated subsystem, §10) |
| CA thin | — | Leg-to-foot socket bonding, CF rod adhesive |
| Spare nylon bolt set | 16 | Replacement M3 × 16 nylon (one full set) |
| Spare wire-loop fuse set | 8 | One full replacement set — the fuse is the primary sacrificial item and is expected to be consumed on any genuine hard/worst-case landing |

---

## 13. Assembly Procedure

1. **Hull boss integration:** Add 8 boss socket positions (2 per corner) to
   `cargo_sect_shell24.scad` belly/side wall.  Print cargo section with bosses integral.

2. **Leg print:** Print 4 Strong-Legs (CF-PETG, upright, foot down; widened trunk zone
   at 100% infill per §4.5 print-profile modifier).

3. **Fuse fabrication:** Form 8 wire-loop fuses to the §4.3 profile from ductile
   spring-steel wire stock; temper for plastic ductility per §4.3/§6.

4. **Foot print:** Print 4 canonical TPU 95A feet with the top-face socket (§7).

5. **Fuse installation:** Pin one tab of each wire-loop fuse into its arm tip socket,
   the other tab into the corresponding hull boss bore.

6. **Leg-to-foot assembly:** Insert leg foot tip into foot top-face socket; apply thin
   CA at socket walls; install M2.5 × 12 mm SS through-bolt.

7. **Safety cord:** Route Dyneema through the leg's foot-end tether hole.  Tie loop.
   Thread free end up through one arm and the corresponding boss tether hole.  Tie loop
   around the boss anchor post stub inside the hull.

8. **Boss insertion:** Slide each fuse's boss-side tab into its hull boss bore.  Install
   2× M3 × 16 mm nylon SHCS per boss — finger-tight + 1/4 turn only.

---

## 14. Field Replacement Procedure

After a fuse fires (visibly flattened ring) or other overload (§6):

1. Locate leg assembly on safety cord.
2. Remove all 4 M3 nylon retention bolts (2 bosses × 2 bolts) (drill out remnants if sheared).
3. Pull the Strong-Leg downward from both hull bosses.
4. Inspect boss bores; clean; check for cracks.
5. Remove the fuse mounting pins; replace any visibly flattened wire-loop fuse(s); a
   fuse that has fired is a single-use item and must not be reinstalled.
6. Install replacement fuse(s) and Strong-Leg (steps 5–8 of assembly procedure above);
   reuse the foot pad if undamaged.

**Required tools:** 2.5 mm hex key (M3), 2 mm hex key (M2.5), small punch/pin tool
(fuse mounting pins), 3.3 mm drill (bolt removal), CA adhesive.

---

## 15. Open Items and Verification Requirements

| ID | Item | Blocks |
|---|---|---|
| LG-01 | Shear-test 10 samples of M3 × 16 PA6 nylon in representative boss fixture; confirm lateral fuse ≥ 283 N per bolt | First flight |
| LG-02 | Integrate 8 hull boss sockets into `cargo_sect_shell24.scad`; run DRC mesh check | Hull print |
| LG-03 | Add CF rod channel to `middle_canonical_shell24.scad` rear skid section (unrelated subsystem) | Hull print |
| LG-05 | Bake and render final placed Strong-Leg STLs (4 corners) with the widened trunk, after LG-10 placement is finalized | Leg printing |
| LG-06 | Drop test prototype leg assembly at 1.5 ft (elastic check — confirm zero permanent set on the leg/fuses) | Pre-flight |
| LG-07 | Confirm avionics enclosure shock rating against the fuse-mediated deceleration profile (re-derive peak-g once LG-14 data exists) | PCB fab |
| LG-10 | Bake the 4 placed Strong-Leg corner copies to hull frame and export 4 placed STLs | Hull boss integration, leg printing |
| LG-11 | Coupon-test CF-PETG at 4 perimeters / 40% gyroid infill to replace the 0.70 effective-area assumption (§4.2) | First flight |
| LG-12 | Widen the trunk cross-section geometrically (≈9.9 × 11.8 mm, 100% infill) per §4.5 | First flight |
| LG-13 | Confirm 2× M3 × 16 mm PA6 nylon per boss is adequate at the fuse-capped force level (§5) | First flight |
| LG-14 | Instrumented drop test (load cell + high-speed video) at 6 ft full-AUW: confirm the wire fuses collapse at the predicted ≈1,956 N/fuse, confirm the ring-collapse mechanics (§4.3) match the idealized 4-hinge model, confirm the CF-PETG structure stays elastic per §4.4. This is the test that certifies the Rev R4 design. | First flight |
| LG-15 | Select and procure ductile spring-steel wire stock/temper for the fuse (§4.3); confirm achievable flow stress and ductility by coupon bend test; finalize fuse mounting-pin detail | Leg fabrication |
| LG-16 | **New.** Select and procure the ductile spring-steel wire grade/temper specifically for plastic-bend ductility (not elastic spring performance) — coordinate with LG-15; confirm chosen temper survives forming into the §4.3 ring shape without premature cracking | Leg fabrication |

---

## 16. Generated Demonstration Models (Rev R4)

Schematic STLs illustrating this design were generated to support visual review. These
use a simple placeholder cylinder for the hull boss (LG-02 integration is still open)
and the standalone exported Strong-Leg (not yet baked to a final corner placement,
LG-10) — they are illustrative, not final-production geometry:

| File | Description |
|---|---|
| `airframe/stls/fuselage/landing-gear/wire_loop_fuse_nominal.stl` | One wire-loop fuse, undeformed |
| `airframe/stls/fuselage/landing-gear/wire_loop_fuse_deformed.stl` | One wire-loop fuse, crushed/flattened to the §4.3 minor-axis collapse state — the field-inspection "this needs replacing" reference shape |
| `airframe/stls/fuselage/landing-gear/landing_gear_assembled.stl` | Leg + foot + 2 fuses (nominal) + 2 boss placeholders, in correct relative position |
| `airframe/stls/fuselage/landing-gear/landing_gear_exploded.stl` | Same parts, separated along each part's local insertion axis for visual clarity |
| `airframe/stls/fuselage/landing-gear/landing_gear_deformed.stl` | Same as assembled, but arm 1's fuse is swapped for the deformed variant and its boss is pulled in against the shortened fuse — shows the post-overload state with one arm fired and one arm still intact, the Level 2/4 progressive-failure behavior from §6 |

Generated by `tools/build_landing_gear_views.py` (Python/`trimesh`) and
`airframe/openscad/fuselage/wire_loop_fuse.scad` (OpenSCAD). Re-run both after any
change to the fuse dimensions, the Strong-Leg foot/tip geometry, or the boss placeholder.
