# Rotating Tilt-Spar Analysis — 8 mm Through-Spar Option

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (analysis drafted by Claude Opus 4.8)
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0
**Date:** 2026-07-18
**Status:** DECISION SUPPORT — pre-implementation. Presents loading + airflow +
nav-wire feasibility for the rotating 8 mm tilt-spar mechanism before the wing
SCAD is reworked.

> All figures imperial-primary, metric in parentheses (CLAUDE.md). Mass = lbm,
> force = lbf. Material allowables flagged "typical" require MMPDS verification
> (see §7 and TODO §0.x).

---

## 1. Mechanism (as specified by user, 2026-07-18)

> **SUPERSEDED 2026-08-25 (SPAR-01, `airframe/wings-nacelles/WBS.md` §1.1.2;
> `docs/plans/2026-08-24-001-fix-wing-repair-root-joint-plan.md`).** The
> single-spar/single-servo/cargo-bay-root-bearing model below is retired.
> Each side now has its **own independent spar and servo** — the "servo
> stays inside the fuselage" part of the mechanism is unchanged, but it is
> now **two servos, one per port/stbd bulkhead**, not one servo in the
> cargo bay driving a spar that crosses the whole ship. The **root bearing
> moves from "inside the cargo bay" to in the fuselage SIDE WALL** (F688ZZ
> seat, terminating at X −100 port / −240 stbd) — the spar no longer
> crosses the bay at all, which is what closes CARGO-01. §3.2's torsion
> path is correspondingly short (bulkhead servo → wingtip), not
> cargo-bay-servo → wingtip. The nacelle-CG pivot, wingtip bearing, nozzle
> drive, and Hall tilt feedback below are **unchanged** — only the spar's
> inboard end and its drive servo's per-side count moved.
>
> - The **wing is fixed** to the fuselage and does **not** tilt.
> - **Two independent rotating spars** (one per side) run: fuselage wall
>   bearing → wing → **nacelle CG pivot** (duct Z = 111.5 mm; Rev T CG
>   re-derive 2026-07-19, was 104.5 mm), each **fixed (keyed) to its own
>   nacelle**.
> - **One servo per side, mounted on the port/stbd bulkhead**, rotates its
>   own spar → tilts its own nacelle. The spar *is* the drive shaft (no
>   external pushrod/lever).
> - **Two bearings per side** carry wing/spar loads and allow rotation:
>     - **Root bearing** — **in the fuselage side wall** (F688ZZ, spar ↔
>       fuselage), not free-floating inside the cargo bay.
>     - **Wingtip bearing** — at the wingtip/nacelle joint (spar ↔ fixed wing).

The mechanism as originally specified (2026-07-18), retained for the
record:

- The **wing is fixed** to the fuselage and does **not** tilt.
- A **single rotating spar** runs: cargo bay → wing → **nacelle CG pivot**
  (duct Z = 111.5 mm; Rev T CG re-derive 2026-07-19, was 104.5 mm), and is
  **fixed (keyed) to the nacelle**.
- **Servo in the cargo bay** rotates the spar → tilts the nacelle. The spar *is*
  the drive shaft (no external pushrod/lever).
- **Two bearings** carry wing/spar loads and allow rotation:
    - **Root bearing** — inside the cargo bay (spar ↔ fuselage).
    - **Wingtip bearing** — at the wingtip/nacelle joint (spar ↔ fixed wing).
- **Nozzle drive** tracks tilt angle. *Two variants exist:* the fixed-wingtip
  **sync gear** (Pinion A orbits a gear fixed to the non-rotating wingtip — §6,
  kept at **R22**) and the now-adopted **Option B pushrod** (a crank clamped to
  the rotating spar strokes the nozzle unison ring — `nacelle_nozzle_pushrod.scad`,
  BOM Rev T). **Either way the nozzle datum is taken at the nacelle/tip** — the
  gear meshes the fixed wingtip; the crank shares the nacelle-keyed spar end — so
  nozzle position tracks *true nacelle tilt* and is **not** corrupted by spar
  torsional wind-up, which lives upstream between the cargo-bay servo and the tip.
- **Tilt feedback — Hall/magnetic angle sensor at the wing/nacelle joint**
  (added per user direction, 2026-07-19): a diametric magnet on the rotating
  nacelle stub, read by a magnetic encoder fixed to the wingtip, closes the tilt
  loop on **true nacelle angle at the output**. Servo positioning therefore does
  **not** depend on spar torsional stiffness (see §3.5). Because the spar is
  ferromagnetic (4130/17-4 PH), the bias magnet must sit on a **non-ferrous stub**
  clear of the steel spar's field — see §3.5 and EMI-hardening WBS §1.4.6.

---

## 2. Load Inputs (from repo, verified)

| Quantity | Value | Source |
|---|---|---|
| Thrust per nacelle (hover) | 2,232 gf = **21.9 N (4.92 lbf)** | `serenity-rev-r.jsx` L346 |
| Nacelle mass (rotating assy) | 393.4 g = **0.867 lbm** (Rev T) | `nacelle_pod_50mm_tandem.scad` header mass breakdown |
| Nacelle CG (duct axis) | Z = 111.5 mm (4.39 in) (Rev T; was 104.5) | ibid — pivot at CG |
| Wing lift per side (40 kt) | ≈ **3.8 N (0.85 lbf)** | `wings_s1223_revo.scad` L35 (7.6 N ÷ 2) |
| Servo torque (tilt drive) | ≥ 25 kg·cm = **2.45 N·m (21.7 lbf·in)** | `serenity-rev-r.jsx` L383 |
| EDF bore ID | 50 mm (1.97 in), r = 25 mm | `nacelle_pod…scad` L221 |
| Wing semi-span (root→tip face) | 85.7 mm (3.37 in) | `wings_s1223_revo.scad` L142 |

**Cantilever geometry (assumed — CONFIRM in FreeCAD):**
Nacelle spanwise half-width ≈ OD_X/2 = 30.25 mm; the duct axis (thrust resultant)
sits ≈ 30 mm outboard of the wingtip bearing. Add ~5 mm mount gap →
**cantilever arm a ≈ 35 mm (1.38 in)** from wingtip bearing to nacelle load line.
(Superseded for the exact figure by the measured `tools/wing_spar_carrythrough.py`
overhang `a` = 38.3 mm used in §2.1 below; kept here as the original hand estimate.)

---

## 2.1 Torque Requirement Re-Derivation (2026-08-25, SPAR-02, KTD5)

**Why re-derive.** The ≥ 25 kgf·cm figure in §2 above is cited only to
`serenity-rev-r.jsx` L383 (a spec-pick table: *"Servo, ≥25 kg·cm @ 6V digital
metal-gear, 2×, Fuselage-mounted, one per nacelle"*, `archives/serenity-rev-r.jsx`
line 383) — it carries no load derivation. Per the owner's direction
(`airframe/wings-nacelles/WBS.md` §1.1.2 SPAR-02), the tilt pivot is sited at the
nacelle CG specifically to null the gravity moment, so the true torque
requirement is aero + inertia only. This section re-derives it and compares
against DS3225's own cleared figure (24.5 kgf·cm at 6.8 V, `REFERENCES.md`
"Open Standards Verification Items" DS3225 row).

**Load-factor convention (reused, not invented):** `docs/structural_analysis.md`
§3 — 4 g limit factor (3 g gust + 1 g maneuver) × 1.5 ultimate factor, the same
convention `tools/wing_spar_carrythrough.py` already applies to this exact
nacelle/pivot geometry.

### 2.1.1 Gravity term — verify the nulling claim algebraically, not by assertion

The tilt pivot is the spar's own axis: a line through the nacelle at duct
station `PIVOT_Z = 111.5 mm`, transverse offset `Y ≈ 0`
(`nacelle_pod_50mm_tandem.scad` header + line 243), running spanwise (the
repo's hull-frame X). Gravity produces zero moment about a line L if and only
if the body's CG lies *on* L (the position vector from any point on L to the
CG is then the zero vector, so `τ = r × F = 0` for any F, at any orientation of
the body about L — this holds for **all** tilt angles, not just the neutral
position, since rotating a zero vector about any axis is still zero).

The nacelle assembly's own mass table (`nacelle_pod_50mm_tandem.scad` header,
Rev T, 11 components, 393.4 g) gives axial CG:

```text
CG_Z = Σ(m_i · Z_i) / Σm_i = 43,879 g·mm / 393.4 g = 111.5 mm = PIVOT_Z
```

— exact by construction: `PIVOT_Z` was *set* to this computed CG_Z (line 383's
comment: "pivot axial centre = full-assembly CG station"), so the axial
(duct-length) coordinate is nulled by definition, not approximation, provided
the underlying 11-item mass/CG table is accurate.

**Residual term — the transverse (Y) coordinate is not tabulated.** The mass
table only reports each component's axial (Z) position; it does not report a
transverse (Y) CG offset. Most components (both EDFs, ESC1/2, shell+stator,
nozzle throat/housing, unison ring, 8× flaps) are nominally axisymmetric about
the duct centerline, so their individual Y-contribution is ≈0 by geometry. Two
components are **not** axisymmetric — they exist at a single clock position to
drive the nozzle unison ring: the **spar crank (1.4 g)** and **pushrod
(3.6 g)**, both cited in the same mass table. Their exact transverse offset is
not measured in the repo. Bounding it conservatively at the full nacelle
half-width (`NACELLE_OD_X/2 = 37.7 mm`, `nacelle_pod_50mm_tandem.scad` line
~229) as a worst case:

```text
M_residual ≤ (1.4 + 3.6) g × 9.80665 m/s² × 0.0377 m ≈ 0.00185 N·m (0.016 lbf·in)
```

This is ≈ 0.08 % of the DS3225's 6.8 V stall torque (2.402 N·m) — negligible,
but it is a **bound on an unmeasured offset, not a verified-zero figure**. The
"pivot at CG nulls gravity" claim holds to within this bound; the exact
transverse CG position is an open item (flag, not a fabricated coincidence).

### 2.1.2 Inertia term — mass moment of inertia about the pivot, from the same table

Treating each of the 11 mass-table items as a point mass at its axial offset
`r_i = |Z_i − PIVOT_Z|` from the pivot line (a lumped/point-mass
approximation — it omits each part's own moment of inertia about its own
centroid, which understates I for extended parts like the rotating spar span
and the 8× flap ring; conservative in the sense that it is the minimum bound
consistent with the tabulated masses and positions, not a full rigid-body
tensor):

```text
I = Σ m_i · r_i²  = 718,861 g·mm² = 7.189 × 10⁻⁴ kg·m²
```

(component-by-component: EDF1 70 g @ r=52.1mm, EDF2 70 g @ r=39.1mm, ESC1
25 g @ r=52.1mm, ESC2 25 g @ r=39.1mm, shell/stator/cowl 130 g @ r=18.7mm,
nozzle throat/housing 21.4 g @ r=63.3mm, unison ring 6.7 g @ r=58.4mm, 8×
flaps 21.1 g @ r=86.7mm, spar crank 1.4 g @ r=0, pushrod 3.6 g @ r=29.3mm,
rotating spar span 19.2 g @ r=0 — spar crank and rotating spar span sit at the
pivot itself, r=0, contributing nothing to I about this axis).

**Angular acceleration — no cited design profile exists.** The repo has two
tilt-rate figures, neither a design acceleration spec: a bench **monitoring**
rate (`docs/TILT_ENCODER_WIRING_EMI_SPEC.md` §7.3, "Nacelle sweep at 10°/s"
during a tethered-hover CAN-message-rate test — an instrumentation check, not
a commanded transition profile) and a **stale** Phase-3 build-guide test step
(`docs/REVN_BUILD_GUIDE_24IN.md` "Test servo response time (<500 ms slew)"
over the −5°→140° = 145° range, written against the pre-Rev-T DS3218MG/Z=83mm
pivot). Using the 145°/500 ms figure with a triangular (accelerate-then-
decelerate, no cruise) velocity-profile assumption — a standard kinematic
model applied to the repo's own cited angle/time pair, not a fabricated
physical constant — bounds the worst-case (highest-α) case:

```text
θ = 145° = 2.531 rad,  t = 0.5 s
α = θ / (t/2)² = 40.49 rad/s²   (peak ω = 10.12 rad/s = 580°/s)
T_inertia = I·α = 7.189×10⁻⁴ kg·m² × 40.49 rad/s² = 0.0291 N·m (0.257 lbf·in)
```

At the repo's own 4 g / 1.5× ultimate convention applied as a margin multiplier
(×6): **T_inertia,ultimate ≈ 0.175 N·m (1.78 kgf·cm, 1.55 lbf·in)** — about
7 % of DS3225's 24.5 kgf·cm 6.8 V stall figure, and the α input itself is
already the *highest* cited tilt rate in the repo (the 10°/s bench-monitoring
rate would give an α roughly two orders of magnitude smaller). **This θ/t
figure is stale (pre-Rev-T geometry) and not a confirmed commanded design
profile — flag for owner confirmation of the actual intended transition
time**, but given the 14× margin already present, only a ~14× faster
transition would put inertia alone at risk of the requirement.

### 2.1.3 Aero term — cannot be grounded; explicitly out of scope, not fabricated

No nacelle drag coefficient, frontal area, or dynamic-pressure figure for the
tilting assembly exists anywhere in `docs/` or `airframe/` (searched for
`drag`, `Cd`, `dynamic pressure`, `frontal area` near "nacelle" — no hits
besides an unrelated wing-airfoil drag note). Per root `AGENTS.md` §4, this
term is **not fabricated**. It is left as an explicit open item: aero moment
about the tilt axis during a transition (cross-flow load on the duct's
frontal/side area, not the axial thrust component — thrust itself acts along
the duct centerline, which passes through the pivot point by the same
CG-pivot geometry, so it contributes ~zero moment about the tilt axis at the
static condition) requires real repo aero data (a wind-tunnel figure, a CFD
result once `tools/wing_cfd_openfoam.py` is unblocked, or a bench thrust-stand
measurement at an angled inflow) before it can be added to this derivation.
**This bounds the analysis to inertia + the residual gravity term only, per
the owner's Scope Boundaries direction** — it is not asserted that aero is
negligible, only that no repo data exists to quantify it.

### 2.1.4 Comparison against DS3225

| Term | Value (ultimate, ×6 margin where applicable) | Basis |
|---|---|---|
| Gravity | ≤ 0.00185 N·m (0.019 kgf·cm) | §2.1.1, unmeasured-transverse-CG bound |
| Inertia | ≈ 0.175 N·m (1.78 kgf·cm) | §2.1.2, triangular-profile bound on stale 145°/500ms figure |
| Aero | **not grounded — open item** | §2.1.3 |
| **Grounded total** | **≈ 0.177 N·m (1.80 kgf·cm)** | sum of the two grounded terms |
| DS3225 stall (6.8 V, cited) | 24.5 kgf·cm (2.402 N·m) | REFERENCES.md DS3225 row |

The grounded requirement (gravity + inertia) is **≈ 7.3 % of DS3225's cited
24.5 kgf·cm** — a wide margin, not the 98 % the uncorrected ≥25 kgf·cm spec
pick implied. **Conclusion: DS3225 stands.** The 2 % shortfall against the
old ≥25 kgf·cm figure that motivated the servo-swap conversation
(`airframe/wings-nacelles/WBS.md` §1.1.2) is not a real structural shortfall —
it was measured against an undermined requirement. No servo change is needed
on load grounds. The aero term remains an explicit, unquantified open item
(§2.1.3); if a future aero figure is obtained and is large enough to erode the
~14× margin above, this conclusion would need revisiting — but nothing in the
repo today supports assuming that.

**Author's note:** this re-derivation reuses `docs/structural_analysis.md` §3's
load-factor convention and `tools/wing_spar_carrythrough.py`'s measured pivot/
overhang geometry (run 2026-08-25: `L=86.7mm`, `a=38.3mm`, `d=126.3mm`) rather
than re-deriving them; those tools remain the source of record for the
underlying spar/overhang geometry.

---

## 3. Spar Candidate: 8 mm OD × 1.5 mm wall (5 mm ID), AISI 4130 steel

Rationale for **hollow steel**: the spar rotates *and* transmits servo torque
through a keyed joint — steel keys/pins reliably (CF pultrusion delaminates at a
keyway); the 5 mm bore carries the nav-light harness (§5).

**Section properties (8 mm OD, 5 mm ID):**

- I = π(D⁴−d⁴)/64 = π(8⁴−5⁴)/64 = **170 mm⁴**
- Bending modulus Z = I/c = 170/4 = **42.6 mm³**
- Polar J = 2I = 341 mm⁴; torsion modulus Zp = J/c = **85.2 mm³**
- Section area = π(4²−2.5²) = 30.6 mm²; mass ≈ 48 g (0.106 lbm) at ~200 mm length

### 3.1 Bending (nacelle cantilever)

- Steady (hover thrust): M = 21.9 N × 0.035 m = **0.77 N·m**
- Design (2× dynamic — gust/hard-landing limit): M = **1.53 N·m**
- σ = M/Z = 1,530 N·mm / 42.6 mm³ = **35.9 MPa (5.2 ksi)**
- 4130 steel yield (typical, normalized) ≈ 460 MPa (66.7 ksi)
  → **FOS ≈ 12.8** on yield at the 2× design load.

### 3.2 Torsion (servo drive)

**Re-checked 2026-08-25 (SPAR-01):** the torsion figures below are unaffected
by the root bearing's move from the cargo bay to the fuselage side wall — the
section (8 mm OD × 1.5 mm wall) and the applied torque are unchanged, and the
now-per-side bulkhead servo shortens the drive path (bulkhead → wingtip)
versus the original cargo-bay-servo → wingtip run, which can only reduce
wind-up, not increase it. This FOS stands.

- τ = T/Zp = 2,450 N·mm / 85.2 mm³ = **28.8 MPa (4.2 ksi)**
- Shear yield ≈ 0.577 × 460 = 265 MPa → **FOS ≈ 9.2**.

### 3.3 Stiffness (tip deflection at nacelle)

- δ = F·a³/(3EI), E = 200 GPa: δ = 21.9 × 35³ / (3 × 200e3 × 170)
  = **0.009 mm (0.0004 in)** — negligible; nacelle stays rigid.

**Verdict:** 8 mm × 1.5 mm 4130 comfortably covers bending (FOS ≈ 13), torsion
(FOS ≈ 9), and stiffness. A 6 mm-ID variant (1 mm wall) still gives FOS ≈ 10
bending but leaves a thin keyway wall — **5 mm ID (1.5 mm wall) recommended.**

### 3.4 Why not the alternatives

| Spar | Bending σ @ 1.53 N·m | Wire path | Torsion | Verdict |
|---|---|---|---|---|
| **4 mm solid CF** (original) | Z=6.3 mm³ → **243 MPa**, FOS ≈ 3, brittle | none | poor keying | **Inadequate** |
| **8 mm × 1.5 steel** (this) | 35.9 MPa, FOS ≈ 13 | 5 mm ID ✓ | FOS ≈ 9 | **Recommended** |
| 12 mm unified (structural) | ~9 MPa, FOS ≈ 50 | 9 mm ID ✓ | best | Overbuilt; heavier, bigger duct crossing |

### 3.5 Material Trade Study (8 mm OD × 1.5 mm wall, 5 mm ID)

The bore (nav wires, §5) and the keyway wall (§3, §8) are **functional
requirements**, so the *section* is held fixed and only the material is traded.
With geometry fixed, bending σ = 35.9 MPa and torsion τ = 28.8 MPa are identical
for every candidate (§3.1–3.2); only the allowables, moduli, and fatigue/joint
behavior move.

> Allowables below are **typical handbook values — require MMPDS-2023 / AMS /
> mill-cert verification before release** (REFERENCES.md requires-verification
> table; TODO §0.8). Bending FOS is on yield at the 1.53 N·m design moment;
> torsion FOS on shear yield (0.577·σ_y) at 2.45 N·m; wind-up θ is over the
> ~200 mm captive length at 2.45 N·m.

| Metric | 4 mm CF | 8×5 CF tube | 6061-T6 | 7075-T6 | **4130 (sel.)** | 17-4 PH H1075 | 316 SS | Ti-6Al-4V |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Density (g/cc) | 1.60 | 1.60 | 2.70 | 2.70 | **7.85** | 7.75 | 8.00 | 4.43 |
| Mass /pair (0.21 lbm ref) | ~8 g | 20 g | 33 g | 33 g | **96 g** | 95 g | 98 g | 54 g |
| Yield allow. (MPa) | — | ~600* | 276 | 503 | **460** | 860 | ~250 | 880 |
| Bending FOS @1.53 N·m | ~3 | ~8* | 7.7 | 14.0 | **12.8** | 24 | 7.0 | 24.5 |
| E (GPa) | ~120* | ~120* | 68.9 | 71.7 | **200** | 197 | 193 | 114 |
| Tip deflection (mm) | — | 0.015 | 0.026 | 0.025 | **0.009** | 0.009 | 0.009 | 0.016 |
| Torsion FOS @2.45 N·m | poor | poor | 5.5 | 10.1 | **9.2** | 17 | 5.0 | 17.6 |
| Drive wind-up θ | — | ~4.6° | 3.2° | 3.1° | **1.0°** | 1.05° | 1.05° | 1.9° |
| Endurance limit | tension | tension | **none** | **none** | **yes** | **yes** | **none** | **yes** |
| Keyed torque joint | delam. | delam. | galls | fair | **excellent** | good | poor | good |
| Bearing journal (F688ZZ) | abrades | abrades | soft | marginal | **ideal** | **ideal** | soft | good |
| Corrosion / finish | inert | inert | good | good | **rusts—plate** | good, bare | best, bare | best, bare |
| Magnetic | no | no | no | no | **yes** | yes | no | no |
| Rel. cost / 8×5 sourcing | low | med | low/good | low-med | **low/good** | med-hi/poor | low/good | high/poor |

\* CF is layup-dependent — a torsion-capable ±45° wrap trades away the axial
bending numbers, and none of it survives a keyway.

**Wind-up is de-rated by the joint Hall sensor (§1).** The magnetic angle sensor
at the wing/nacelle joint closes the tilt loop on true nacelle angle, so shaft
torsional compliance no longer appears as tilt error; and the nozzle drive is
referenced at the nacelle/tip, so wind-up is not a sync error either (§1). A
dynamic check confirms this is safe for **every** candidate: the torsional
spar+nacelle mode (nacelle inertia ≈ 0.0013 kg·m² about the spar axis, k = GJ/L)
is ≈ 52 Hz (steel/SS), ≈ 38 Hz (Ti), ≈ 29 Hz (Al) — all an order of magnitude
above servo bandwidth (~2–5 Hz) and gust content (<10 Hz). Wind-up therefore
drops out as a selection driver; **fatigue endurance limit and keyability become
the discriminators.**

**Findings:**

- **CF (either form)** — fails the functional gate: cannot take a keyed torque
  joint (delaminates) and abrades the bearing journals. Out regardless of its
  mass advantage. Confirms §3.4.
- **6061 / 7075 aluminum & 316 SS** — **no fatigue endurance limit** → a
  rotating, gust-cycled, keyed shaft in these is a finite-life, inspection-
  interval part. **7075-T6** is the honest lightweight fallback (−63 g/pair,
  static FOS 14/10) now that the Hall sensor removes the wind-up penalty; 6061
  and 316 are too soft at the keyway and bearing journal.
- **4130 (selected)** — best keyability, hardness-matches the F688ZZ steel races,
  true endurance limit, lowest wind-up, cheap and well-stocked in 8×5. Only real
  penalties: heaviest, and **it rusts — a corrosion finish (zinc/cadmium plate,
  journals ground) is mandatory** and must be carried on the BOM finish spec.
- **17-4 PH (H1075) stainless** — essentially "4130 that doesn't rust": same
  E / mass / keyability / bearing match, higher FOS (24 / 17), true endurance
  limit, and **no plating step**. The strongest alternative to plated 4130;
  penalties are higher cost and poor 8×5 seamless-tube stock (likely gun-drilled
  from bar). Ferromagnetic, like 4130 (§1, EMI §1.4.6).
- **Ti-6Al-4V** — superior on every axis except cost and machinability; −42 g/pair,
  non-magnetic, corrosion-immune, endurance limit. The premium pick if budget and
  keyway machining allow.

**Selection:** retain **4130 + corrosion finish** as the baseline; carry **17-4 PH
H1075** as the qualified plating-free alternative and **7075-T6** as the mass-
critical (life-limited) fallback. All allowables pending MMPDS/AMS verification
(§7, TODO §0.8).

---

## 4. Airflow — Spar Crossing the Thrust Duct

The spar crosses the 50 mm duct **spanwise (X), perpendicular to flow (Z)**, at
**Z = 111.5 mm — the inter-EDF stator station** (stator spans 90–122.5 mm; Rev T
CG re-derive, was 104.5 mm — still well inside the stator span). This is the key
finding: **the duct core is already obstructed there.**

- Existing blockage at that station: 16 mm-OD stator hub + 11 radial fins
  (r = 16–25 mm). The core is a structural spider, **not** a fan.
- Naïve added blockage of a bare 8 mm strut across the 50 mm duct:
  8 × 50 = 400 mm² of the 1,963 mm² annulus (≈ 20%).
- **Mitigated:** the central 16 mm is *already* hub; fairing the spar into the
  hub + **2 opposing stator fins aligned to the spar (X) axis** hides the strut
  behind blockage that already exists. **Net added blockage → ~2–4%**, at the
  lowest-velocity (post-EDF1, pre-EDF2) station.
- **No motor conflict:** EDF1 (Z=59.4) and EDF2 (Z=150.6) shafts run along Z; the
  pivot at Z=111.5 is in the *gap* between them. The spar owns the core only where
  the stator spider already does.

**Required stator change:** re-index the 11 fins so **2 opposing fins lie on the
spar axis** and thicken into a **spar tunnel** through the hub. This is a
`nacelle_pod_50mm_tandem.scad` stator edit, tracked as a dependency.

**Duct-wall crossings:** the spar pierces the **inboard** duct wall (from the
wing) and the **outboard** duct wall (to reach the outboard nav light, §5),
fixed to the nacelle at both. Two small reinforced bosses; both inside the
existing shell, no OML change.

---

## 5. Nav-Light Wires Through the Spar — FEASIBLE

- Nav light = WS2812C addressable, **3-core 28 AWG**, bundle Ø ≈ 2.5 mm.
- **5 mm ID** carries it with margin (bundle area 4.9 mm² vs bore 19.6 mm² = 25%).
- **Rotation twist:** spar sweeps −5°…90° ≈ **95°** over its ~200 mm captive
  length. A 3-core twisting 95° over 200 mm is a gentle helix (≈ 0.5°/mm), far
  inside 28 AWG stranded flex life — **no slip ring required**; anchor the wire
  at the cargo-bay (root) end so the twist distributes along the free length.
- **Routing:** wire enters the hollow spar at the cargo-bay end, travels the bore
  through wing + duct, and exits at the **outboard** nacelle wall boss to the
  outboard nav light. The spar thus spans the full nacelle width.
- **EDF power/signal do NOT use the spar** (6× 16 AWG @ Ø3 mm — too large). They
  keep the existing wing **double-D cableway** + nacelle harness port. The spar
  is nav-wire-only.

---

## 6. Fixed Wingtip Gear — DECISION: keep R22 (no shrink, no idler, no embed)

**FINAL (2026-07-18):** the fixed sector is kept at **R22** and the nacelle gear
housing is **unchanged**; the sector simply relocates from the retired pylon to
the fixed wingtip (coaxial with the spar), and Pinion A meshes it as before.
Reason: shrinking to R14 breaks the one-shaft nozzle drive (`PINION_A_Y = 30.5`
does double duty as the sector-mesh AND internal-ring-mesh center distance), so
it would need a reintroduced idler for marginal gain. The shell-overlay study
(`airframe/openscad/nacelles/gear_option_compare.scad`) confirmed R22's Pinion A
stays within the existing nacelle housing blister, while R14 only fits by adding
the idler. The wing tip therefore just carries the bearing seat + a bolt circle
for the R22 sector (`wings_s1223_revo.scad`).

> The R14-shrink/embed analysis below is **SUPERSEDED** by the decision above,
> retained as the design record for why it was not adopted.

### ~~6.x (SUPERSEDED) Shrink to R14 + Embed in Nacelle Inboard Face~~

**Intermediate direction (later reversed):** shrink the fixed gear to R ≈ 14 mm
**and embed the pinion/sector into the nacelle's inboard surface** to preserve
the canonical outboard silhouette.

### 6.1 Regear (Module 1.0, PA 20°)

| Part | Was | Now (R14) | Notes |
|---|---|---|---|
| Fixed sector | R22, 44T, OD 44 mm | **R14, 28T, OD 30 mm** | sector arc ≈ 110° (95° sweep + margin), 3 mm plate |
| Drive Pinion A | R8.5, 17T, OD 19 mm | **R5.5, 11T, OD 13 mm** | smaller → embeds easier |
| Center distance (`PINION_A_Y`) | 30.5 mm | **19.5 mm** | = 14 + 5.5 |
| Sync factor (1 + R_s/R_p) | 3.588 | **3.545** | nozzle travel 98.8% of prior |

The 1.2% sync loss over the 95° sweep is inside the iris end-stop margin;
absorb it there or trim one tooth at the ring stage. **Re-verify iris full-travel
after regear** (`nacelle_nozzle_iris.scad`).

### 6.2 Embedding — keeps gears OUT of the airflow

Both the fixed sector and Pinion A are thin (3 mm) plates in the **Y–Z plane at
the inboard X-face**, recessed into the inboard wall/pivot-boss between
**X = 30–34 mm** (local). Because the EDF bore is a cylinder of r = 25 mm about
the duct (Z) axis, **any feature at X ≥ 30 mm is wholly outside the bore** (needs
X < 25 mm to intrude) — so embedding the gears in the inboard face adds **zero
airflow blockage** and is independent of the §4 stator-crossing of the spar.

- **Recess in nacelle inboard face:** Ø ≈ 52 mm × **4 mm deep** (X 34→30),
  centered on the spar axis (Y = 0, Z = 111.5). Sized so Pinion A can orbit the
  fixed sector through the full 95° (orbit radius 19.5 + pinion tip 6.5 = 26 mm).
- The fixed sector (on the non-rotating wingtip) sits **inside** this recess; the
  recess + Pinion A rotate around it with the nacelle.
- The recess mouth is **hidden at the wing–nacelle butt joint** → the visible
  outboard nacelle OML is unchanged (canonical preserved).
- Downstream: Pinion A moving 30.5 → 19.5 mm shifts the bevel/longitudinal shaft
  path inboard 11 mm — a contained `nacelle_pod…scad` adjustment, no OML change.

**Clearance confirmed:** gears at X ≥ 30 mm clear the bore (max X = 25 mm) with
5 mm margin; no stator-fin or duct intrusion.

---

## 7. Mass / T-W Impact (CLAUDE.md)

- Two 8 mm steel spars ≈ **96 g (0.21 lbm)** total, near the centerline (minimal
  CG shift). Replaces the 4 mm CF concept (~8 g) → **net +≈ 88 g**.
- AUW 2,768 g → ~2,856 g; hover T/W 4,464/2,856 = **1.56** (was 1.61) — still far
  above the 1.2 floor. Acceptable.

**Material allowable caveat:** 4130 yield used here (460 MPa typical) must be
confirmed against MMPDS-2023 for the procured temper before final release.
Add REFERENCES.md entry + TODO §0.x (requires-verification) when adopted.

---

## 8. Geometry Rework Required (why the current wing SCAD "doesn't allow this")

Current `wings_s1223_revo.scad` wingtip block is wrong for this mechanism:

| Current feature | Problem | Replace with |
|---|---|---|
| `wing_tip_nacelle_boss_socket()` | No boss exists (nacelle fixed to spar) | **Wingtip bearing seat** (MF128ZZ, 8×12×3.5 — Rev R2d downsize; the F688ZZ Ø16 seat broke both tip skins, §8 note) coaxial with spar |
| `wing_tip_tilt_spar_bore()` 3.98 mm press-fit | Spar rotates; must clear | **8.1 mm rotating clearance** + bearing pockets |
| Protruding mount block for gear | Gear must be fixed & coaxial | **Fixed R14 gear boss** coaxial w/ spar, standing proud for pinion mesh |
| — | Spar must pass fully through | **Through-bore** wing→tip; spar continues into nacelle |
| Root end | Not modeled | **Root bearing seat** in cargo-bay wall + servo horn coupling |

Dependencies opened by adopting 8 mm:

1. `nacelle_pod_50mm_tandem.scad` — stator re-index (2 fins on spar axis + tunnel);
   inboard/outboard duct-wall spar bosses; nacelle keyed to spar at CG.
2. `nacelle_pod…scad` — Drive-Pinion-A regear to R14 sector; nozzle ratio re-verify.
3. Cargo bay — root bearing seat + servo-to-spar horn (servo stays in bay).
4. BOM — 8 mm 4130 tube ×2, **F688ZZ root bearings ×2 + MF128ZZ wingtip bearings
   ×2** (Rev R2d — see note), R14 fixed gears ×2; retire 4 mm CF pivot rod + MF104ZZ.

### 8.1 Rev R2d implementation notes (2026-07-19)

The wingtip interface has since been modeled in `wings_s1223_revo.scad`, and three
geometry issues were found and fixed **using the parametric numbers** (no STL guesswork):

- **Wingtip bearing downsized F688ZZ → MF128ZZ (Ø16 → Ø12).** The Ø16 seat radius
  (7.975 mm) exceeded the S1223 tip half-thickness (7.80 mm at the spar station,
  even at `THICKNESS_SCALE_TIP` = 1.25) and cut a ~0.21 mm crescent through **both**
  airfoil skins. MF128ZZ seats with **+1.79 mm** margin. Wingtip radial reaction
  ≈ 19 N (dyn) ≪ MF128 capacity (~700 N) — load-safe. Root bearing stays F688ZZ.
- **Tilt-feedback Hall sensor = AK7455** (SPI, magnetoresistive, off-axis/ferrous-through-shaft)
  — supersedes the Magntek MT6701 (I²C) originally considered here; MT6701 was rejected this
  same day in favor of AK7455 (see `avionics/kicad/ENC-NACELLE-1.md`, REF-SENSOR-008, and
  `docs/TILT_ENCODER_WIRING_EMI_SPEC.md` for the current wiring/EMI spec), on a compact
  **7×7 mm** in-house PCB, seated off-axis at **R = 11 mm**, reading a **Ø22**
  diametric ring on the nacelle hub. The tip is congested — the pocket threads the
  ~8.4 mm chordwise gap between the Ø13.5 bearing flange (X≈28.75) and the forward
  EDF double-D bore (X≈37.1): echo-verified clearances 0.75 mm (flange) / 0.64 mm
  (EDF) / **4.01 mm** (top skin); pad OD 26→**29.5** (kept clear of the EDF bore).
- **EDF double-D drilled through the root tenon — STRAIGHT.** The `fuselage_root_tab`
  blocked the Ø7 double-D 1 mm in. The pass-through is a **separate straight axial
  bore** (constant X,Y) continuing each conduit through the tenon's inboard face —
  *not* an extension of the slanted spanwise hull, which had skewed the root-face
  hole ~2.3 mm sideways (hard to thread). Root-face and tenon-exit openings are now
  coaxial. Solid **15.4 mm lower spine** retained (bores groove only the crown) — sound.

---

## 9. Recommendation

**Adopt 8 mm OD × 1.5 mm wall (5 mm ID) AISI 4130 rotating tilt-spar.**
It clears all three gates:

- **Loading:** FOS ≈ 13 bending, ≈ 9 torsion, deflection negligible.
- **Airflow:** crosses at the stator station where the core is already blocked;
  net added blockage ~2–4% after fin/hub fairing.
- **Nav wires:** 5 mm ID carries the 3-core with margin; 95° twist needs no slip
  ring; reaches the outboard nav light.

**Material (§3.5):** 4130 is the baseline but **requires a corrosion finish**
(zinc/cadmium plate, journals ground) — the bare tube rusts at the bearing
journals; add it to the BOM finish spec. **17-4 PH H1075 stainless is the
qualified plating-free alternative** (same section/mass/stiffness, higher FOS, no
plating; higher cost + make-from-bar). **7075-T6 aluminum** is the mass-critical
fallback (−63 g/pair) now that the joint Hall sensor (§1, §3.5) removes the
torsional-wind-up penalty — but with no fatigue endurance limit it is a
life-limited, inspected part. All allowables pending MMPDS/AMS verification (§7,
TODO §0.8).

**Open the go-ahead decision** on §8 rework + §6 regear before I edit geometry.

> Skipper: Pilot, you gotta give me an Ivan.
> Pilot: I'll see what I can do.
> (over the intercom)
> Pilot: Flight Engineer, how would you feel about pullin' a Crazy Ivan?
> Flight Engineer: (sounds weak but positive) Always wanted to try one.
  