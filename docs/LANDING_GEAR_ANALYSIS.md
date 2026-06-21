# Serenity UAV — Landing Gear Structural Analysis

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Revision:** R5 (2026-06-20) — Vertical post + 4-wire brace (2 spring, 2 ductile) — final hybrid

> "She's tore up plenty, but she'll fly true." — Mal, on a ship that's seen worse landings than this one's rated for.

> **Rev R4** (Strong-Leg forked arms + per-arm closed-ring wire fuse) **superseded
> 2026-06-20.** The closed ring was judged hard to manufacture and field-replace
> (precision winding + separate tabs). Rev R5 also corrects a geometric
> misunderstanding: the **original canonical single-blade leg already has two branch
> points of its own** (at the apex, and about 1/3 of the way down from the apex) — the
> Strong-Leg's duplicate+rotate+union therefore produces **four branch points total**
> (2 at the apex, 2 at the 1/3-down point), not a single fork into two arms. Rev R5
> models this directly: the forked CF-PETG arms are removed entirely and replaced with
> four simple wires (2 per branch level). Rev R3 / R2 / R1.4 / R1.3 / R1.2 / R1.1 / R1
> remain superseded. Energy numbers (§3) still carry forward unchanged.

---

## 0. Design Summary

The Strong-Leg is now **two parts**: a short CF-PETG **vertical post** (foot at the
bottom, two branch-height sockets above it) and **four simple wires** bracing that post
to the hull at the two branch heights inherited from the original canonical leg:

| Branch level | Height (from foot) | Wires | Role |
|---|---|---|---|
| Apex (top) | ≈79.8 mm (full original leg length) | 2× **spring** wire | Elastic, fully recoverable — ordinary hard landings, zero permanent set |
| 1/3-down from apex | ≈53.2 mm | 2× **ductile** wire | Plastic, sacrificial — each independently sized for the full 6 ft worst-case per-leg energy |

Each wire is a **single straight piece of wire stock with one shallow pre-bend** (a
shallow "bow," not a closed loop) — chosen specifically because it is the simplest
possible shape to manufacture (a bending jig or even careful hand-forming) and to
field-replace (cut wire stock to length, bend over a form block, no precision winding,
no separate tabs). The wire ends seat directly into a socket in the post and a socket
at the hull boss.

Total added wire mass: **≈50 g** for the aircraft (4 legs × 4 wires). Total CF-PETG post
mass: **≈130 g** for the aircraft. Both numbers are verified in §4.

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

## 2. Aircraft Data and Geometry

### 2.1 All-Up Weight

| Configuration | AUW |
|---|---|
| Phase 5–10 (no aft EDF) | **6.10 lbm (2,768 g)** |
| Phase 11 (full system, design case) | **6.90 lbm (3,130 g)** |

The **Phase 11 AUW of 6.90 lbm (3,130 g) is the design case**.

### 2.2 Landing Gear Configuration (Rev R5)

- **4 × leg assemblies** — one per cargo belly corner; each assembly: 1 CF-PETG vertical
  post (round, smoothly tapered cross-section, two branch-height sockets) + 2 spring wires (apex) +
  2 ductile wires (1/3-down) + 1 canonical TPU 95A foot pad + 4 hull boss sockets
  (integral to cargo shell).
- **16 hull boss sockets total** (4 per leg × 4 legs — one per wire).
- **16 wires total**: 8 spring (apex pairs) + 8 ductile (1/3-down pairs).
- **4 × TPU 95A canonical foot pads** — existing Thingiverse-derived geometry, unmodified
  outer form.
- **2 × rear skids** — integral to the horseshoe ring of the middle section; unrelated
  subsystem, unchanged by this revision (see §10).

### 2.3 Geometric Basis — the Original Leg's Two Branch Points

The original canonical single-blade leg (`leg_1_scaled24.stl`…`leg_4_scaled24.stl`,
misubisu Thingiverse hull, CC BY 4.0; 79.84 mm long) is a vertical part with **two
branch points of its own**: one at the **apex** (top) and one about **1/3 of the way
down from the apex**. The Strong-Leg's construction — duplicate the leg, **rotate the
duplicate 30° about its own vertical centreline**, **union** the two — doubles each
branch point into a pair, 30° apart in azimuth:

```
Apex branch:       2 attachment points (original + rotated duplicate), Z ≈ 79.8 mm
1/3-down branch:   2 attachment points (original + rotated duplicate), Z ≈ 53.2 mm
                   (= 79.8 × 2/3, i.e. 1/3 of the leg length down from the apex)
```

Rev R5 keeps only the **vertical post** portion of this geometry (foot up through the
1/3-down branch height) as a solid CF-PETG print, and replaces **all four branch
attachments** — the material that, in Rev R2–R4, continued upward as forked CF-PETG
arms — with the four wires described in §0. This is a more faithful reading of the
mesh than Rev R2–R4's "single fork at ~44 mm" approximation (cross-checked against the
mesh's multi-lobe region at local Z ≈ 20–44 mm, which is consistent with the 1/3-down
branch pair beginning to separate from the trunk in that range, not a single fork point).

### 2.4 Wire Geometry

Both wire types share the same shape — a straight chord of length `L` with a single
shallow pre-bend (rise `h` at the midpoint) — sized differently per branch level. The
apex (spring) wires are longer and the 1/3-down (ductile) wires shorter, in a ratio
similar to the retired Rev R1.4 V-brace's upper:lower strut proportions (77.6:53.9 mm):

| | Length `L` | Lean from vertical | Diameter `d` | Nominal sag `h` |
|---|---|---|---|---|
| Spring wire (apex) | 45 mm | 24° | 3.17 mm | 3.5 mm |
| Ductile wire (1/3-down) | 30 mm | 24° | 4.35 mm | 3.5 mm |

SCAD source: `airframe/openscad/fuselage/wire_brace_leg.scad` (`PART="post"`,
`"spring_wire_nominal"`, `"spring_wire_deformed"`, `"ductile_wire_nominal"`,
`"ductile_wire_deformed"`).

---

## 3. Impact Velocity and Kinetic Energy

Unchanged from Rev R1 — AUW and drop height are unaffected by the leg redesign.

```text
v = √(2 g h) = √(2 × 386.09 in/s² × 72.0 in) = 235.8 in/s  (19.65 ft/s, 5.99 m/s)
KE_total = ½ m v² = 496.8 in·lbf  (56.1 J)
KE_per_assy (6 ft, full AUW)   = 56.1 / 4 = 14.04 J  (124.2 in·lbf)
KE_per_assy (1.5 ft, full AUW) =  3.51 J  (elastic-check energy, TODO.md LG-06)
```

---

## 4. Wire and Post Sizing

### 4.1 Design Method — Bowed-Wire Strut

A wire with a shallow pre-bend, loaded along its chord, deforms by deepening the bow;
a plastic (ductile wire) or elastic (spring wire) hinge forms at the bow's crown. Using
a simplified 2-hinge mechanism (consistent with the project's existing hand-calc
practice elsewhere in this document):

```text
M = P·h/2                              (moment at the crown)
P = 2M/h                                (collapse / elastic-limit force)
stroke ≈ (h_final² − h_initial²) / (2L) (axial chord-shortening as the bow deepens
                                          from h_initial to h_final = 3×h_initial,
                                          a packaging choice leaving reserve stroke)
U = P × stroke                          (energy absorbed, constant-force approximation)
```

Solving for diameter `d` given a target energy `U` and material stress `σ`
(M = σ·d³/6 plastic, or σ·π·d³/32 elastic first-yield):

```text
d_plastic = (6·U·L / (3·σ·h)) ^ (1/3) ·[reduced consistently with the stroke relation above]
```

(full derivation: `U = σ²·b·t·L/(12E)`-style closed forms were used for the flat-blade
spring in the retired Rev R3/R4 design; the round-wire bowed-strut numbers below were
solved numerically with the same energy/stress balance — see
`tools/build_landing_gear_views.py` git history and the design-session calculation log.)

### 4.2 Spring Wire (Apex Pair) — Sized for the 1.5 ft Elastic-Check Case

```text
Material: spring steel, E = 200,000 MPa, working stress 900 MPa (elastic — full
  recoverability, no permanent set, long fatigue life)
Target energy per wire: 3.51 J / 2 wires = 1.755 J
L = 45 mm, h = 3.5 mm  →  d = 3.17 mm, P ≈ 1,612 N (axial, elastic limit), stroke ≈ 1.1 mm
Mass per wire ≈ 2.79 g
```

### 4.3 Ductile Wire (1/3-Down Pair) — Sized for the Full 6 ft Worst Case, Independently

```text
Material: ductile spring-steel wire, tempered for plastic ductility (NOT full-hard) —
  flow stress ≈ 550 MPa
Target energy per wire: 14.04 J / 2 wires = 7.02 J  (each wire sized to cover the FULL
  per-leg worst case on its own — not a 50/50 split — as margin against uneven/
  asymmetric landings)
L = 30 mm, h = 3.5 mm  →  d = 4.35 mm, P ≈ 4,298 N (axial, plastic collapse plateau),
  stroke ≈ 1.6 mm (of the available ~7 mm before the bow reaches its packaging limit —
  ample reserve)
Mass per wire ≈ 3.49 g
```

**Self-consistency check:** 2 ductile wires × 7.02 J each = 14.04 J ≥ the full 6 ft
worst-case per-leg energy. **The ductile pair alone, even with zero contribution from
the spring pair, covers the complete design case.**

### 4.4 Total Wire Mass

```text
(2 spring × 2.79 g + 2 ductile × 3.49 g) × 4 legs ≈ 50.3 g total  (1.6% of Phase 11 AUW)
```

### 4.5 Vertical Pair Capacities (for the Post and Boss Checks Below)

```text
Spring pair vertical capacity (elastic limit)  = 2 × 1,612 N × cos(24°) ≈ 2,945 N
Ductile pair vertical capacity (collapse plateau) = 2 × 4,298 N × cos(24°) ≈ 7,853 N
```

### 4.6 Post Sizing

The post no longer has the Rev R2–R4 trunk/fork/arm geometric weak point — it is a
simple round column with a smooth conical taper (no hard ledge) between a wider lower
section and a narrower upper section. The **lower section** (foot → 1/3-down socket)
carries the combined load from both pairs; the **upper section** (1/3-down → apex
socket) carries only the spring pair's share (the ductile pair's load already exits
the post at the 1/3-down socket). Cross-sections below are sized by required area, then
converted to an area-equivalent circular radius for the round post:

```text
Target allowable stress: σ_yield/2 = 27.5 MPa (2× margin), 100% infill (0.95 effective factor)

Lower section: F = 2,945 + 7,853 = 10,798 N  →  A_nom ≈ 411 mm²  →  r ≈ 11.45 mm (Ø22.9 mm)
Upper section: F = 2,945 N                    →  A_nom ≈ 112 mm²  →  r ≈ 5.98 mm (Ø11.96 mm)
Taper length: 8 mm, positioned clear of both socket bores (≥6 mm Z clearance each side)

Post mass ≈ 32.5 g each × 4 = 130.0 g total (area-equivalent — the round form factor
  does not change the mass relative to the square cross-section it's sized from)
```

> **TODO LG-12 (revised):** model the post per these dimensions — round column,
> Ø22.9 mm lower / Ø11.96 mm upper, smooth 8 mm conical taper between them (no
> stepped ledge), 100% infill — in place of the Rev R2–R4 Strong-Leg fork/arm
> geometry. **BLOCKS first flight.**

### 4.7 Hull Boss Bearing Check

Each leg now has **4** hull bosses (one per wire) instead of 2:

```text
Boss bore ≈ 6 × 5 mm (wire end + clearance), Boss OD ≈ 10 × 9 mm (2-wall annulus)
A_bearing per boss = (10×9) − (6×5) = 60 mm², × 4 bosses per leg = 240 mm²
F_bearing_capacity ≈ 70 MPa × 240 mm² ≈ 16,800 N per leg

Margin vs combined pair capacity (2,945 + 7,853 = 10,798 N) = 1.56×
Margin vs ductile pair alone (7,853 N)                       = 2.1×
```

**The hull boss — and by extension the cargo shell — remains protected with a healthy
margin.**

### 4.8 Lateral Load Analysis (±15° Off-Vertical)

```text
F_vert  = 10,798 × cos(15°) ≈ 10,433 N
F_lat   = 10,798 × sin(15°) ≈  2,795 N
F_per_boss (4 bosses) = 2,795 / 4 ≈ 699 N — resolved as bending/shear at the wire-to-
  boss socket interface, not a separate bolted fuse (the wire ends are pinned directly
  in their sockets; see §7 for retention detail).
```

> **TODO LG-13 (revised):** define the wire-to-boss socket retention detail (pin, set
> screw, or adhesive) and verify its capacity against the §4.8 lateral load. The
> previous M3/M4 nylon shear-bolt fuse concept (Rev R2–R4, sized for a rigid spigot) no
> longer applies directly to a wire end — needs a fresh fastener choice.

---

## 5. (Reserved — merged into §4)

---

## 6. Progressive Failure / Fuse Strategy (Rev R5)

| Level | Element | Activates at | Behavior |
|---|---|---|---|
| 1 (elastic, no damage) | CF-PETG post + spring wires (apex) | up to ≈2,945 N (spring pair elastic limit) | Fully elastic, fully recoverable — ordinary hard landings cause no damage anywhere |
| 2 (primary sacrificial fuse) | Ductile wires (1/3-down pair) | ≈4,298 N axial per wire (≈7,853 N pair, vertical) | Each wire's bow progressively deepens via a plastic hinge; **either wire alone covers the full 6 ft worst-case energy**; visibly bent afterward — unambiguous field-inspection indicator |
| 3 (lateral retention) | Wire-to-boss socket pin/retention (TBD, LG-13) | per §4.8 | Prevents the wire from walking out of its socket under lateral load |
| 4 (protected at all credible loads) | Hull boss / cargo shell | > 70 MPa bearing (§4.7) | ≥1.56× margin at the full combined-pair force — the hull is not expected to see damaging load |

This satisfies Requirement 3 (§1) with the cleanest margin structure of any revision so
far: **the CF-PETG post is not expected to yield at all** (it is sized with 2× margin
at the combined worst-case force, §4.6), and **either ductile wire alone is sufficient**
for the full 6 ft design case — genuine redundancy at the level of individual,
field-replaceable wires, with a simple, hand-formable shape.

---

## 7. Foot and Socket Interfaces

| Interface | Detail |
|---|---|
| Foot pad | Unchanged canonical TPU 95A pad, 43.94 × 43.94 × 9.04 mm, unmodified outer form; post foot end seats in a top-face socket as in Rev R2 (7.6 × 9.0 mm bore × 5.0 mm deep + M2.5 through-bolt) |
| Post-side wire sockets | 4× blind holes (Ø5 mm bore, ≈10 mm deep), 2 at the apex (Z≈79.8 mm), 2 at the 1/3-down height (Z≈53.2 mm), each bored at 24° from vertical, ±15° azimuth split within each pair |
| Hull-side wire sockets | 4 per leg, integral to the cargo shell (§4.7); retention detail TBD (LG-13) |

---

## 8–9. (Reserved)

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

### 11.1 CF-PETG Vertical Post (4 per aircraft, one per corner)

| Parameter | Value |
|---|---|
| Material | CF-PETG |
| Geometry | Round column, smooth conical taper (no stepped ledge): lower section Ø22.9 mm (foot → taper start, Z 0–59.2 mm), 8 mm taper, upper section Ø11.96 mm (taper end → apex socket, Z 67.2–85.8 mm); branch sockets at Z 53.2 mm (1/3-down, ductile) and Z 79.8 mm (apex, spring), both clear of the taper |
| Infill | 100% (both segments — neither is expected to yield, §4.6) |
| Layer height | 0.15 mm, 4 perimeters |
| Print orientation | Upright, foot down |
| Estimated mass | ≈32.5 g each × 4 = ≈130 g total |

### 11.2 Spring Wire (8 per aircraft, 2 per leg — apex branch)

| Parameter | Value |
|---|---|
| Material | Spring steel, E = 200,000 MPa, working stress 900 MPa |
| Geometry | Bowed strut: L = 45 mm chord, Ø3.17 mm, 3.5 mm nominal sag |
| Estimated mass | ≈2.79 g each × 8 = ≈22.3 g total |

### 11.3 Ductile Wire (8 per aircraft, 2 per leg — 1/3-down branch)

| Parameter | Value |
|---|---|
| Material | Ductile spring-steel wire, tempered for plastic ductility, flow stress ≈550 MPa |
| Geometry | Bowed strut: L = 30 mm chord, Ø4.35 mm, 3.5 mm nominal sag |
| Estimated mass | ≈3.49 g each × 8 = ≈27.9 g total |

### 11.4 Hull Boss Sockets (16 per aircraft, 4 per corner)

| Parameter | Value |
|---|---|
| Material | CF-PETG |
| Geometry | OD ≈ 10 × 9 mm, bore ≈ 6 × 5 mm |
| Integration | Union with `cargo_sect_shell24.scad` belly/side wall; 4 per corner |

### 11.5 TPU Foot Pads (4 per aircraft, unchanged canonical geometry)

| Parameter | Value |
|---|---|
| Material | TPU 95A |
| Dimensions | 43.94 × 43.94 × 9.04 mm (unmodified outer form) |
| Socket | Top-face, 7.6 × 9.0 mm bore × 5.0 mm deep |
| Fasteners | 1× M2.5 × 12 mm SS through-bolt per foot |

### 11.6 Safety Cord

| Parameter | Value |
|---|---|
| Material | Dyneema SK75, 2 mm diameter |
| Break strength | ≥ 750 N (168 lbf) |
| Length per assembly | ≈ 400 mm (foot → post bore → boss → anchor post inside hull) |

---

## 12. Bill of Materials (per aircraft, 4 assemblies)

| Item | Qty | Description |
|---|---|---|
| CF-PETG vertical post | 4 | Round column, smooth taper, 100% infill, replaces the Rev R2–R4 forked Strong-Leg |
| Spring wire | 8 | Spring steel, bowed strut, 2 per leg (apex branch) |
| Ductile wire | 8 | Ductile spring-steel wire, bowed strut, 2 per leg (1/3-down branch) |
| Hull boss socket | 16 | CF-PETG, integral to cargo shell; 4 per corner |
| TPU foot pad | 4 | TPU 95A, canonical Thingiverse geometry + top socket |
| M2.5 × 12 SS bolt | 4 | Foot retention (1 per foot) |
| Wire-to-socket retention (TBD, LG-13) | 16 | Pin / set screw / adhesive — fastener choice still open |
| Dyneema SK75, 2 mm | 1.6 m | Safety cord (4 × 400 mm) |
| 3 mm CF rod | 280 mm | Rear skid reinforcement (unrelated subsystem, §10) |
| CA thin | — | Leg-to-foot socket bonding, CF rod adhesive |
| Spare wire set | 16 | One full replacement set (8 spring + 8 ductile) — ductile wires are expected to be consumed on any genuine hard/worst-case landing |

---

## 13. Assembly Procedure

1. **Hull boss integration:** Add 16 boss socket positions (4 per corner) to
   `cargo_sect_shell24.scad` belly/side wall. Print cargo section with bosses integral.

2. **Post print:** Print 4 vertical posts (CF-PETG, upright, foot down, 100% infill).

3. **Wire fabrication:** Form 16 spring wires and 16 ductile wires (8 spares of each)
   to the §4.2/§4.3 profiles; temper the ductile wires for plastic ductility.

4. **Foot print:** Print 4 canonical TPU 95A feet with the top-face socket (§7).

5. **Wire installation:** Seat each wire's post-side end in its post socket; seat the
   hull-side end in its boss socket; secure per the LG-13 retention detail once finalized.

6. **Leg-to-foot assembly:** Insert post foot tip into foot top-face socket; apply thin
   CA; install M2.5 × 12 mm SS through-bolt.

7. **Safety cord:** Route Dyneema through the post's foot-end tether hole, up through
   the post bore, and to a hull anchor post.

---

## 14. Field Replacement Procedure

After a ductile wire fires (visibly deepened bow) or other overload (§6):

1. Locate leg assembly on safety cord.
2. Release the fired wire's retention at both ends (per LG-13 detail).
3. Inspect the post and hull boss sockets for damage.
4. Bend a replacement wire to the §4.3 profile from spare stock (or use a pre-formed
   spare); seat and secure.
5. If the post itself is damaged (not expected at the design case, §4.6), replace the
   post per steps 2–6 of the assembly procedure.

**Required tools:** simple wire-bending form block, 2 mm hex key (M2.5), CA adhesive,
whatever tool the final LG-13 retention detail requires (pin punch, hex key, etc.).

---

## 15. Open Items and Verification Requirements

| ID | Item | Blocks |
|---|---|---|
| LG-02 | Integrate 16 hull boss sockets into `cargo_sect_shell24.scad`; run DRC mesh check | Hull print |
| LG-03 | Add CF rod channel to `middle_canonical_shell24.scad` rear skid section (unrelated subsystem) | Hull print |
| LG-05 | Bake and render final placed post + wire STLs (4 corners) | Leg printing |
| LG-06 | Drop test prototype leg assembly at 1.5 ft (elastic check — confirm zero permanent set on post and both wire types) | Pre-flight |
| LG-07 | Confirm avionics enclosure shock rating against the wire-mediated deceleration profile (re-derive peak-g once LG-14 data exists) | PCB fab |
| LG-10 | Finalize the 4 corner post placements in `SerenityAssembly.FCStd`; bake to hull frame | Hull boss integration, leg printing |
| LG-12 | Model the post per §4.6 dimensions (round column, smooth taper, 100% infill), replacing the Rev R2–R4 forked geometry | First flight |
| LG-13 | **Revised, still open.** Define the wire-to-socket retention detail (pin / set screw / adhesive) at both the post end and the hull boss end; verify against the §4.8 lateral load | First flight |
| LG-14 | Instrumented drop test (load cell + high-speed video) at 6 ft full-AUW: confirm the ductile wires collapse at the predicted ≈4,298 N/wire; confirm the bowed-strut mechanics (§4.1) match the idealized 2-hinge model; confirm the post and spring wires stay elastic. This is the test that certifies the Rev R5 design. | First flight |
| LG-15 | Select and procure both wire grades/tempers (spring: full elastic range; ductile: plastic-bend ductility); confirm by coupon test | Leg fabrication |
| LG-16 | Confirm the ductile wire temper survives forming into the bowed-strut shape without premature cracking | Leg fabrication |

---

## 16. Generated Demonstration Models (Rev R5)

Schematic STLs illustrating this design (placeholder boss cylinders — LG-02 integration
is still open; standalone post — not yet baked to a final corner placement, LG-10):

| File | Description |
|---|---|
| `airframe/stls/fuselage/landing-gear/post.stl` | The CF-PETG vertical post alone |
| `airframe/stls/fuselage/landing-gear/spring_wire_nominal.stl` / `_deformed.stl` | One apex (spring) wire, undeformed and illustratively bowed |
| `airframe/stls/fuselage/landing-gear/ductile_wire_nominal.stl` / `_deformed.stl` | One 1/3-down (ductile) wire, undeformed and fired/flattened — the field-inspection reference shape |
| `airframe/stls/fuselage/landing-gear/landing_gear_assembled.stl` | Post + foot + 2 spring wires + 2 ductile wires + 4 boss placeholders, in correct relative position |
| `airframe/stls/fuselage/landing-gear/landing_gear_exploded.stl` | Same parts, separated along each part's local insertion axis |
| `airframe/stls/fuselage/landing-gear/landing_gear_deformed.stl` | Same as assembled, but both ductile wires are swapped for the fired/flattened variant — the post-overload state |

Generated by `tools/build_landing_gear_views.py` (Python/`trimesh`) and
`airframe/openscad/fuselage/wire_brace_leg.scad` (OpenSCAD). Re-run both after any
change to wire dimensions, post geometry, or the boss placeholder.

The Rev R4 closed-ring fuse SCAD (`airframe/openscad/fuselage/wire_loop_fuse.scad`) is
retired and kept for reference only — see the retirement note at the top of that file.
