---
title: "chore: Ranked weight-reduction targets — cargo section, wing root, and carried mass"
date: 2026-08-30
plan_type: mechanical+process
artifact_contract: ce-unified-plan/v1
artifact_readiness: implementation-ready
execution: geometry+hardware
product_contract_source: ce-plan-bootstrap
parent: docs/MASS_AUDIT_CARGO_WING_ROOT.md
---

# chore: Ranked weight-reduction targets

**Target repo:** Serenity-UAV (this repo)

*"She'll fly true. Just gotta stop putting rocks in her pockets."*

---

## Summary

Hover T/W was ~1.19 against a 1.2 minimum, and Rev T1c added +102.8 g. This plan
lists what can come back out, ranked by mass, with the check that has to clear
before each one is cut.

**REVISED 2026-08-31 — the ranking's uncomfortable shape has been fixed, and
RISK-3 was right.** The plan warned that if the canonical nacelle pod turned out
to weigh far more than its 132 g BOM row, "the pods become the dominant target
and this plan's ordering is wrong." That is what happened. W6 is closed: the
canonical pod is `nacelle_port_revs.stl` / `nacelle_stbd_revs.stl`, and rebuilt
from current source it measures **284.8 g each — 152.8 g over its BOM row, 305.6 g
over the pair.**

The reason is a single structural fact nobody had written down: **the nacelle
pods are SOLID.** The SCAD imports the canonical shell — which is a solid
1.25×-scaled mesh — and subtracts only the duct and a handful of pockets. The
four *fuselage* shells were put through this repo's own hollowing pipeline
(`blender_shells_2mm_solidify.py` → `hollow_manifold.py`, producing the
`*_2mm_repaired.stl` files). **The nacelle shells never were.** So each pod is a
185 mm block of CF-PETG with a 50 mm hole down the middle, and the "annular space
between the duct wall and the outer skin" that three separate planning documents
route wiring through does not exist.

That makes **W0 the largest structural lever in this plan by a factor of two**,
and unlike W1 it costs no capability.

The battery swap (`BATT-6S-4000` → `BATT-6S-2800`, **225 g**) remains the single
largest item, but it is an endurance trade. W0 is not.

**And nothing here should be cut until W2 lands.** The BOM understates printed
mass by **+521.6 g (13.3 % of AUW)**, so the aircraft is currently being weighed
against a number that is not the aircraft. Shaving 30 g off a part whose BOM row
is 118 g wrong is not weight reduction, it is decoration.

| # | Target | Measured now | Recoverable | Confidence | Gate |
|---|---|---:|---:|---|---|
| **W0** | ~~Hollow the two nacelle pods~~ **DONE 2026-08-31** | 570.5 g (pair) | **−178.8 g** | measured | **cut — see §W0** |
| **W1** | Battery down-select 4000 → 2800 mAh | 750 g | **−225 g** | high | endurance/mission, not structure |
| **W2** | **BOM ⇄ mesh reconciliation** | — | **0 g** | — | **gates every other item** |
| **W3** | Battery-tray floor pocket | 140.2 g | **−23.1 g** | high | rail-slot depth, not bending |
| **W4** | Actuator standoffs → hollow | 109.5 g | **−32.9 g** | high | mesh deflection (already cleared) |
| **W5** | Cargo cradle → windowed frame | 80.6 g | **−25 g (est.)** | medium | latch-tab flex, 250 g payload |
| **W6** | ~~Nacelle pod STL identity~~ **RESOLVED 2026-08-31** | 132 g BOM vs **284.8 g** measured | *(BOM error, not a cut)* | — | **closed — see §W6** |
| **W7** | Landing-gear bay bolt bosses | 126.0 g raw | unquantified | low | bolt bearing; needs its own study |
| | **Printed-part subtotal (W3–W5)** | | **≈ −81 g** | | |
| | **Printed-part subtotal with W0 (W0 measured, W3–W5 estimated)** | | **≈ −260 g** | | |
| | **With W1** | | **≈ −485 g** | | |

**Explicitly NOT a target: the wing roots.** §W8 records why, so it is not
re-litigated.

---

## Problem Frame

### Why this is worth doing at all

`docs/structural_analysis.md` §1.1.5 puts hover T/W at ~1.19 without a battery
swap and ~1.25 with one, against a stated 1.2 minimum. Rev T1c's +102.8 g
(`airframe/fuselage-mid/WBS.md` WA-R18) pushes the un-swapped case further under.
So the airframe is not comfortably above its own hover criterion, and the margin
has to come from somewhere.

### Why the BOM gates everything

`docs/MASS_AUDIT_CARGO_WING_ROOT.md` §5 measured all 23 `PRINT-*` rows whose
description names an STL that exists. The rows understate by **+521.6 g**:

| Row | BOM | Measured | Δ |
|---|---:|---:|---:|
| `PRINT-CARGO-SECT` | 165.0 | 372.2 | +207.2 |
| `PRINT-BATT-TRAY` | 22.0 | 140.2 | +118.2 |
| `PRINT-HEAD-SHELL` | 83.0 | 177.6 | +94.6 |
| `PRINT-CARGO-CRADLE` | 18.0 | 80.6 | +62.6 |
| `PRINT-MIDDLE-CANONICAL` | 135.0 | 190.9 | +55.9 |

Three were corrected in the audit. The rest were measured and left for their
owning branches. Until they are reconciled, no weight statement in this
repository means anything — and a plan that optimises against a wrong baseline
optimises the wrong parts.

### The efficiency signal worth reading

Bounding-box fill fraction is a crude but honest tell for an over-built part:

| Part | Mass | Envelope (mm) | Fill |
|---|---:|---|---:|
| `battery_tray.stl` | 140.2 g | 154 × 51.5 × 62 | **27.2 %** |
| `wing_port_s1223_revo.stl` | 95.5 g | 95.7 × 129 × 31.4 | 23.5 % |
| `cargo_cradle_autolatch.stl` | 80.6 g | 110 × 80 × 72 | 12.1 % |
| `cargo_sect_shell24_2mm_repaired.stl` | 372.2 g | 194 × 199 × 163 | 5.6 % |

The wing is at 23.5 % because it is a thick, highly-cambered section skinned at
the 4-perimeter floor — that is the *shape*, not slack. The tray is at 27.2 %
because it has an 8.5 mm floor. Those two look similar in the column and are
completely different findings, which is why the column is a *signal* and the
per-part analysis below is the *answer*.

---

## Requirements

- **R1** — No target is cut before its BOM row is reconciled to its mesh (W2).
- **R2** — Every cut carries a named failure mode, a computed margin against a
  cited allowable, and the deflection or fit consequence where that governs
  instead of stress.
- **R3** — No cut takes a wall below **2.5 mm** (4 perimeters at 0.6 mm), the
  repo's minimum-wall convention.
- **R4** — No cut erodes a clearance budget that is already stated and spent
  (`GAP_BUDGET` 3.0 mm to a moving part; 1.16 mm minimum skin over a bore).
- **R5** — Mass, CG and hover T/W are re-derived once, after all accepted cuts,
  not incrementally per part.
- **R6** — Each modified part re-passes `tools/validate_stls.py` as a watertight
  single body.

---

## Key Technical Decisions

**KTD1 — W2 is a prerequisite, not a parallel task.** *(session-settled: the
audit found the baseline wrong by 13.3 % of AUW.)* Governs R1.

**KTD2 — Structural cuts are justified against a *named* mode, and the mode is
usually not stress.** On the tray floor it is a rail-slot depth constraint; on
the actuator standoff it is gear-mesh deflection; on the cradle it is flex-tab
compliance. Each was mis-diagnosable as a strength problem and none of them is
one. Governs R2.

**KTD3 — The wing root is closed to further reduction.** Both of its dimensions
are already at a floor: `WALL_T` 2.5 mm is four perimeters, and
`THICKNESS_SCALE` 1.46 is the *solved* value leaving 1.19 mm of skin over the
Ø20.4 bore against a 1.16 mm minimum. Governs R3, R4.

**KTD4 — W1 is an operations decision, not an engineering one.** The 2800 mAh
pack is 225 g lighter and shorter-endurance. This plan sizes it and states the
trade; it does not make the call.

---

## Implementation Units

### W0. Hollow the two nacelle pods — **CUT 2026-08-31**

**Result: −178.8 g across the pair** (284.8 → 195.9 g port, 285.7 → 195.8 g stbd),
measured from the meshes. The largest single weight reduction on the aircraft,
and it came with a clearance dividend that was the reason the owner directed the
shape of it.

**The wall is deliberately not uniform.** Owner direction: *"take more from the
forward end instead of the aft end to adjust CG and nacelle ground clearance."*
The tilt pivot sits at the rotating assembly's CG, so mass removed forward of it
drags the pivot aft, which shortens the pivot-to-nozzle arm one for one and lifts
the nozzle in hover. Built schedule: **2.5 mm forward, ramping to 8.0 mm over
Z 100–140.**

| | pod mass | `PIVOT_Z` | hover clr, 1.5 in gear |
|---|---:|---:|---:|
| solid (as built) | 284.8 g | 105.9 | −10.47 mm |
| uniform 2.5 mm wall | ~171 g | ~113.2 | ~−3.2 mm |
| **built: 2.5 fwd → 8.0 aft** | **195.9 g** | **113.8** | **−2.55 mm** |
| built + plan 005's 30 mm flaps | 195.9 g | 112.8 | **+6.41 mm** |

Two things that table says and should not be softened: the forward bias is worth
about **0.6 mm of clearance for 24 g**, a poor exchange rate in isolation, and it
**cannot close the 10.5 mm deficit on its own**. What it does is carry 8 mm of it,
so that plan 005's already-settled flap trim finishes the job instead of falling
short. The residual after both is +6.41 mm against the +9.8 mm the owner
previously accepted.

**How it was done, and why not the obvious way.** The fuselage pipeline
(`blender_shells_2mm_solidify.py` → `hollow_manifold.py`) was *not* used: it
produces 40–66 MB voxel meshes and the pod is an OpenSCAD part whose booleans
already take minutes against a 3.3 MB import. Instead
`tools/nacelle_hollow_profile.py` **ray-casts** the canonical shell's outer skin
and emits the cavity as an explicit `polyhedron()` — 29 KB of generated,
diffable, regenerable SCAD. Ray-casting rather than section radii, because the
canonical mesh carries an internal forward intake pocket that makes a section's
minimum radius meaningless below Z ≈ 58; the first estimate built that way
under-reported the removable volume by roughly half.

**What the hollowing forced, all of it caught by gates rather than inspection:**
- three **vented** structural webs at Z 40/62/84 — the first render sealed a
  −17,227 mm³ compartment between the first two, which no slicer can drain;
- a monotonic cavity-closure rule, after four sub-mm inverted slivers appeared
  where the cavity grazed the duct wall at the end of the ramp;
- `nav_wire_channel()` moved to Zone C — it is a rib standing *into* the cavity,
  so it was a no-op while the pod was solid and would have been deleted once it
  was not.

**Acceptance:** all met. Both pods watertight, single-bodied, no negative-volume
bodies, no OpenSCAD warnings; `validate_stls`, `nacelle_trunnion_fit` (T1–T8,
S1–S3, M1) and the wing/cargo/landing-gear gates green; `nacelle_mass_cg.py`
reports the CG fixed point converged to 0.00 mm.

**What it unblocks:** `WA-R10`. There is now a real 5–17 mm annulus between the
duct wall and the skin, which is what plan 003 assumed all along.

---

#### W0 (original scope, for the record)

**Goal:** −192.7 g across the pair, and the annulus that WA-R10 needs.

**Dependencies:** W2 for the BOM row; nothing else. Note that W0 also *unblocks*
`WA-R10` (the 4 × 10 AWG disconnect), which is currently blocked ON it.

**Files:** `airframe/blender-scripts/blender_shells_2mm_solidify.py`,
`airframe/blender-scripts/hollow_manifold.py`,
`airframe/openscad/nacelles/nacelle_pod_50mm_tandem.scad`,
`current-specification/bom_revS.csv`

**Approach:** Put `eng_{left,right}_shell24_50mm_repaired.stl` through the same
two-stage pipeline the fuselage shells already use — Blender voxel-remesh to
clean outer/inner operands, then a `manifold3d` boolean difference — producing
`eng_{left,right}_shell24_50mm_hollow.stl`, and import those in the pod SCAD
instead of the solid.

**How much is actually recoverable, measured rather than assumed.** Integrating
the annulus between `duct_r + 2.5` and `skin_r − 2.5` over Z 28–166 at 1 mm
stations and 5° azimuth bins, taking the **tightest** skin radius in each bin
(so the figure is a floor, not a hope), and leaving the intake bell and the
nozzle pocket alone:

| | volume | mass |
|---|---:|---:|
| removable core, per pod | 91,777 mm³ | **96.4 g** |
| pod as built | 271,198 mm³ | 284.8 g |
| **pod hollowed** | | **188.4 g** |
| **pair** | | **−192.7 g** |

**The wall is not uniform and that is the whole point.** Measured usable depth
(skin radius − duct radius − 2 × 2.5 mm) on the inboard face runs 7.1 mm at
Z 75–88 and collapses to 1.1 mm by Z 110; in the fat lobes at azimuth 240–300 it
reaches 12 mm. A rotationally-symmetric cavity sized to the minimum would
recover almost nothing, which is why this needs a true inward offset — i.e. the
existing pipeline — and not a `cylinder()` subtraction in the SCAD.

**The real cost is architectural, and it should be stated before anyone starts.**
The pod is currently an *OpenSCAD* part that imports a 3.3 MB solid and takes
~4 minutes to render. A hollowed shell from the voxel pipeline is 40–66 MB (the
fuselage ones are), and OpenSCAD CGAL booleans against a mesh that size are not
practical. **Hollowing the pod therefore means moving it to the Blender /
manifold3d pipeline**, as the cargo section already did
(`merge_cargo_interior.py`). That is the work, not the boolean.

**Acceptance criteria:**
- [ ] `eng_{left,right}_shell24_50mm_hollow.stl` watertight, single body, 2.5 mm
      minimum wall verified by section sampling — not by trusting the modifier.
- [ ] Pod re-derived through whichever pipeline owns it; measured mass within
      ±10 % of 188.4 g per pod.
- [ ] No feature that currently relies on solid material is left cantilevered —
      specifically the trunnion collar, the sleeve retention bosses, the EDF1
      spider, and the nav wire channel each need a boss or rib into the new skin.
- [ ] `tools/validate_stls.py` and `tools/nacelle_trunnion_fit.py` green.
- [ ] WA-R10 re-opened and closed: route the 4 × 10 AWG from the trunnion to the
      disconnect bay in the new annulus.

**Verification:** `tools/validate_stls.py`, `tools/nacelle_trunnion_fit.py`,
`tools/nacelle_mass_cg.py` (the pivot moves — see R5).

**Scope:** L (5–8 files)

---

### W2. Reconcile the BOM to the meshes *(do this first)*

**Goal:** A mass column that describes the aircraft.

**Dependencies:** none — this gates everything else
**Files:** `current-specification/bom_revS.csv`, `tools/bom_mass_check.py` (new),
`docs/MASS_AUDIT_CARGO_WING_ROOT.md`

**Approach:** For every `PRINT-*` row with `Qty > 0`, resolve the STL its
description names, measure it at `RHO_PRINT` (1.05 × 10⁻³ g/mm³), and write the
measured figure into `Unit_Mass_g`. Then add the check to CI so a regenerated
mesh cannot silently diverge from its row again.

Two traps the audit already hit, both worth encoding in the tool:

- **`RHO_PRINT` is a bulk figure.** Do not re-derive it as
  `RHO_SOLID × infill`. Below ~6 mm thickness a part is nearly all perimeter and
  infill barely moves it; that error halved the `PRINT-WING-ROOT-FLANGE` row.
- **Consumable stock is not installed mass.** `FOAM-PU-2LB` carried the 900 g
  *kit*; installed foam is 22 g. `FIL-CF-PETG` carries 2,000 g of spool. Add an
  `Installed` flag rather than trying to fix these row by row — summing the
  current mass column returns 12.7 kg, which is the mass of nothing.

**Acceptance criteria:**
- [ ] Every `PRINT-*` row with a resolvable STL matches it within ±5 %.
- [ ] Rows whose named STL cannot be resolved are listed explicitly (W6 is one).
- [ ] `Installed` flag present; the installed-only sum is stated.
- [ ] CI fails on a row that drifts from its mesh.

**Verification:** `/usr/bin/python3 tools/bom_mass_check.py` exits 0.

**Scope:** M (3–5 files)

---

### W1. Battery down-select

**Goal:** Decide 4000 mAh vs 2800 mAh on stated numbers rather than inertia.

**Dependencies:** W2 (so T/W is computed against a real airframe mass)
**Files:** `current-specification/bom_revS.csv`, `docs/flight_envelope.md`,
`docs/POWER_DISTRIBUTION.md`

**Approach:** `BATT-6S-4000` is **750 g — 19 % of the 3,911 g AUW and the single
heaviest item on the aircraft.** `BATT-6S-2800` is 525 g. Present endurance at
each capacity against the hover and cruise power draws already in
`POWER_DISTRIBUTION.md`, with T/W at each mass, and let the owner choose per
mission profile rather than fixing one pack.

**This is a mission trade, not a structural one.** State it and stop; the
airframe does not care which pack is fitted, and the tray already accepts both
(cavity 148 × 56 × 41 mm).

**Acceptance criteria:**
- [ ] Endurance and T/W tabulated for both packs at the reconciled AUW.
- [ ] Owner decision recorded, either way, with its reason.

**Verification:** Not automatable — a recorded decision.

**Scope:** S (1–2 files)

---

### W3. Battery-tray floor pocket

**Goal:** −23.1 g from a floor that is thick for a geometric reason, in the
region where that reason does not apply.

**Dependencies:** W2
**Files:** `airframe/openscad/fuselage/battery_tray.scad`,
`airframe/stls/fuselage/battery_tray.stl`

**Approach:** `FLOOR = 8.5 mm`, and the SCAD is explicit that this is **not a
strength figure**: the rail slot (`RAIL_D = 6.5`) must not breach the cavity
floor, so 8.5 leaves 2.0 mm above it. That constraint only exists *at the rail
slots*. Everywhere else the floor is carrying a battery on a 56 mm span.

Retain full thickness in a band around each rail slot; pocket the central field
from below to 3.0 mm.

**Bending check, simply-supported strip, 20 % CF-PETG at 77 MPa flexural
(REF-MAT-002, ASTM D790), 750 g pack:**

| Floor `t` | σ, limit 4 g×1.5 | FOS | σ, crash 9 g×1.5 | FOS | δ, limit |
|---|---:|---:|---:|---:|---:|
| 8.5 mm (as built) | 0.173 MPa | 444 | 0.390 MPa | 197 | 0.002 mm |
| 4.0 mm | 0.783 MPa | 98 | 1.762 MPa | 44 | 0.019 mm |
| **3.0 mm** | **1.392 MPa** | **55** | **3.132 MPa** | **25** | **0.045 mm** |
| 2.5 mm | 2.004 MPa | 38 | 4.510 MPa | 17 | 0.079 mm |

3.0 mm clears the §3 FOS 4.0 target by **6× on the crash case**. 2.5 mm would
too, but 3.0 matches the tray's own `WALL` and keeps one thickness in the part.

Pocket 138 × 29 × 5.5 mm = 22,011 mm³ → **−23.1 g**, tray 140.2 → 117.1 g.

*Modes checked and non-governing:* rail-slot breach (retained band), bearing at
the M3 detent bores (in the rail band, untouched), strap-slot tear-out
(`STRAP_SLOT` is in the wall, not the floor).

**Acceptance criteria:**
- [ ] Rail slots retain ≥ 2.0 mm of material above them.
- [ ] Central floor ≥ 3.0 mm; FOS ≥ 4.0 at 9 g × 1.5 recorded.
- [ ] STL watertight, single body; BOM row updated to the measured mass.

**Verification:** `tools/validate_stls.py`; re-measure and compare to 117.1 g.

**Scope:** S (1–2 files)

---

### W4. Hollow the actuator standoffs

**Goal:** −32.9 g. Already analysed; this unit is the execution.

**Dependencies:** W2
**Files:** `airframe/blender-scripts/merge_cargo_interior.py`

**Approach:** The two nacelle-tilt actuator pads are **109.5 g — 29 % of the
cargo shell**, of which 62.8 g is the Rev T1c standoff, modelled as a solid
61.5 × 27 × 18 mm block. Replace with a 2.5 mm wall + 2.5 mm mounting face.

**The governing mode is mesh opening, not strength.** Worst-case combined load
5.0 N (3.47 N gear separation + 3.53 N actuator inertia at 4 g × 1.5);
cantilever `δ = FL³/3EI`:

| Form | `I` (mm⁴) | δ | vs a 0.05 mm centre-distance budget |
|---|---:|---:|---|
| Solid, as built | 100,875 | 1.44 × 10⁻⁵ mm | 3,500× inside |
| **Hollow, 2.5 mm** | ~58,000 | ~2.5 × 10⁻⁵ mm | 2,000× inside |
| 4 × Ø12 posts | 15,381 | 9.47 × 10⁻⁵ mm | 500× inside |

The post variant saves 9 g more and is **not** recommended: it puts four
unsupported 18 mm columns inside the hull at a print orientation set by the
cargo shell, not by them.

**Do not instead** shrink `NSVMT_STANDOFF` (18 = 11 gear plane + 6 face + 1 hub,
and 3 of the 11 is `GAP_BUDGET` to a rotating gear) or thin the 6 mm gear face
(already 7.5 × module, low end of the conventional 6–12× band). Together they
are 15 g for two stated budgets — R4 forbids it.

**Acceptance criteria:**
- [ ] Standoff wall ≥ 2.5 mm; mounting face continuous under the flange.
- [ ] M3 pilot bores still land in ≥ 6 mm of material.
- [ ] `wing_root_deconflict.py` still CLEAR; shell watertight single body.
- [ ] Measured saving ≥ 30 g on the pair.

**Verification:** `tools/wing_root_deconflict.py`, `tools/validate_stls.py`,
re-measure the shell.

**Scope:** S (1–2 files)

---

### W5. Cargo cradle — windowed frame

**Goal:** ≈ −25 g from a part that weighs 80.6 g to carry a 250 g payload.

**Dependencies:** W2, and **CARGO-01** (the cradle's bay placement is still
blocked; redesigning it before that settles risks doing the work twice)
**Files:** `airframe/stls/fuselage/cargo/generate_cargo_mounts.py`

**Approach:** The cradle is *not* over-thick — it is already a 2.5 mm-walled
shell. Its problem is that it is a **fully-closed 110 × 80 × 60 mm box** for a
2.45 N line tension and a 250 g payload. Walls are ~53,600 mm³ of the 76,793;
the base plate is ~22,000.

Replace the closed side walls with a windowed frame: retain full-height corner
posts, the top rim, the base perimeter, and the four flex-tab corners; window
the panels between. A 50 % window fraction on the side walls is ≈ −28 g.

**Two things must not be windowed**, and they are why this is medium confidence
rather than high:

1. **The four corner flex tabs and the rim they hinge from.** The auto-latch
   works by tab compliance; changing the rim's local stiffness changes the snap
   force, and that force is not characterised in this repo.
2. **The Dyneema tie-off boss and its load path to the rim.** The whole payload
   hangs from it.

Material is PETG here, not CF-PETG — use the PETG allowable, not REF-MAT-002.

**Acceptance criteria:**
- [ ] Base plate retains a continuous load path from the tie-off boss to all
      four corners.
- [ ] Flex-tab geometry and the rim within 10 mm of each tab **unchanged**.
- [ ] Payload bearing check at 250 g × 9 g × 1.5 against the PETG allowable.
- [ ] STL watertight single body; measured saving ≥ 20 g.

**Verification:** `tools/validate_stls.py`; bench snap-force comparison against
an unmodified cradle before flight use.

**Scope:** M (3–5 files)

---

### W6. Nacelle pod STL identity — **CLOSED 2026-08-31**

**Answer: `nacelle_port_revs.stl` / `nacelle_stbd_revs.stl` are canonical.**

`PRINT-NACELLE-PORT`/`-STBD` named `s_eng_left_stator_shell24_revo.stl` at 132 g
each. That file does not exist; the `s_` prefix was dropped project-wide. Of the
two candidates:

| candidate | mass | what it actually is |
|---|---:|---|
| `nacelle_port_revs.stl` (published) | 277.9 g | **the printed pod** — but STALE, predating Rev S1c |
| `nacelle_port_revs.stl` (rebuilt 2026-08-31) | **284.8 g** | the printed pod at Rev T4 |
| `eng_left_shell24_50mm_repaired.stl` | 658.5 g | **not a printed part** — the solid canonical mould-line INPUT the pod SCAD imports and bores |

It was resolved by reading the build command out of the render pipeline
(`openscad -o nacelle_port_revs.stl nacelle_pod_50mm_tandem.scad -D SWIRL_DIR=-1
-D PYLON_SIDE=-1 -D NACELLE_SIDE=-1`, then `tools/bake_hull_frame.py`) rather
than by comparing masses, which would have been a guess.

**BOM impact: +152.8 g per pod, +305.6 g for the pair** — on its own, 58 % of the
+521.6 g understatement W2 was chartered to chase, in two rows. The row is
corrected and `PRINT-NACELLE-TRUNNION` is added alongside it.

**This finding is what created W0**, and it realises RISK-3 exactly as written.

---

### W7. Landing-gear bay bolt bosses *(study)*

**Goal:** Establish whether any of the 126.0 g raw bay feature volume is
recoverable.

**Dependencies:** W2
**Files:** `airframe/blender-scripts/merge_cargo_interior.py`,
`airframe/landing-gear/WBS.md`

**Approach:** The Rev R6 bay features are 126.0 g of raw positive volume before
keep-out trimming. They are bolt bosses carrying real landing loads, and
`tools/landing_gear_wing_clearance.py` already reports the fore-stbd boss
standing 12.0 mm proud with a warning that a cut-back would cost upper-bolt
bearing. **Assume nothing is free here** until the bolt bearing check is redone.

**Acceptance criteria:**
- [ ] Per-boss mass and bolt bearing margin tabulated.
- [ ] A recoverable figure stated, or "none" stated with its reason.

**Scope:** M (3–5 files)

---

### W8. Wing root — CLOSED, recorded so it is not reopened

**No action. This unit exists to stop the question being asked again.**

- Spanwise mass distribution is a clean taper (14.54 g in the root slice down to
  10.07 g at the tip) with **no local pile-up** — the signature of a skin-limited
  structure, not a feature-limited one.
- `WALL_T = 2.5 mm` is **four perimeters at 0.6 mm**. 2.0 mm is 3.3 perimeters,
  which is not a wall.
- `THICKNESS_SCALE = 1.46` is **solved, not chosen**: it is the exact value
  leaving 1.19 mm of skin over the Ø20.4 spar bore against the repo's 1.16 mm
  floor (`tools/wing_spar_station_fit.py`). Thinning the section breaks the bore
  out of the skin.
- The **33.7 g** the retired tie rods returned (11.7 g of shell bosses + 22.0 g
  of CF rod stock) was the whole of what this structure had to give, and it has
  been taken.

---

### Checkpoint: after W2, W3, W4

- [ ] BOM reconciled; installed-only AUW stated.
- [ ] ≈ 56 g recovered from the tray and standoffs.
- [ ] Gate suite green.
- [ ] Owner review before W5 (the cradle touches a mechanism whose snap force is
      uncharacterised).

---

## Risks & Dependencies

- **RISK-1 (high) — optimising against a wrong baseline.** Mitigated by KTD1:
  W2 first, and nothing else starts until it lands.
- **RISK-2 (medium) — the cradle's latch is a compliance mechanism.** Snap force
  is uncharacterised, so any stiffness change near the tabs is a change to a
  function nobody has measured. Mitigated by the W5 exclusion zones and a bench
  comparison.
- **RISK-3 — REALISED 2026-08-31, and the ranking was duly inverted.** The
  canonical pod is 284.8 g, not 132 g. The pods are now the dominant structural
  target (W0, −192.7 g for the pair) and the original ordering *was* wrong. Kept
  here rather than deleted, because the lesson generalises: this plan's other
  rankings also rest on BOM rows, and W2 is the only thing standing between them
  and the same failure.
- **RISK-4 (low) — cumulative FOS erosion.** Individually each cut keeps a large
  margin; R5 requires one combined re-derivation rather than trusting the sum of
  per-part checks.
- **DEP-1** — W5 is behind **CARGO-01** (cradle bay placement unresolved).
- **DEP-2** — All T/W statements inherit the unverified CF allowable
  (`WING_ATTACH_INTERFACE.md` OI-2) and the unquantified aero terms.

---

## Open Questions

- **OQ1** — Which battery is the mission baseline (W1)? Owner call.
- **OQ2** — Is `RHO_PRINT = 1.05 × 10⁻³` right for *thick* parts? It is the
  bulk figure and is conservative for thin walls, but a 45 mm-tall tray at 40 %
  gyroid may genuinely be lighter than it predicts. A weighed printed sample
  would settle it and would sharpen every number in this plan.
- **OQ3** — Does the cargo cradle fly on every sortie, or only on delivery
  missions? If the latter, its 80.6 g is removable payload rather than airframe
  mass, and W5 drops down the ranking.
- **OQ4** — W7: is there any bay-boss mass that does not carry bolt bearing?

---

## Verification Contract

```text
/usr/bin/python3 tools/bom_mass_check.py            # new, W2
/usr/bin/python3 tools/validate_stls.py
/usr/bin/python3 tools/wing_root_deconflict.py
/usr/bin/python3 tools/landing_gear_wing_clearance.py --proud
/usr/bin/python3 tools/cargo_bay_envelope.py
/usr/bin/python3 tools/precommit_index.py --check
```

Not automatable: the W1 owner decision, the W5 bench snap-force comparison, and
the single combined mass/CG/T-W re-derivation required by R5.

---

## Definition of Done

1. Every `PRINT-*` BOM row matches its mesh within ±5 %, enforced in CI, with an
   `Installed` flag separating installed mass from consumable stock.
2. W3 and W4 cut, each with a recorded FOS or deflection margin against a cited
   allowable, and each part re-passing `validate_stls.py`.
3. W5 either cut with the bench comparison recorded, or explicitly deferred
   behind CARGO-01.
4. W6 resolved — the canonical nacelle pod named and measured.
5. The battery decision recorded either way, with its reason.
6. Mass, CG and hover T/W re-derived **once** on the final geometry, with the
   T/W margin against the 1.2 minimum stated explicitly.

---

## Sources & Research

- `docs/MASS_AUDIT_CARGO_WING_ROOT.md` — parent; all measured masses, the
  +521.6 g BOM finding, and the foam budget.
- `airframe/fuselage-mid/WBS.md` WA-R18, MA-1, MA-5, MA-6, MA-7.
- `airframe/openscad/fuselage/battery_tray.scad` — `FLOOR = 8.5` and its own
  note that the figure is set by `RAIL_D`, not by load.
- `airframe/stls/fuselage/cargo/generate_cargo_mounts.py` `make_autolatch_cradle()`
  — 2.5 mm walls, 250 g payload rating, flex-tab latch.
- `airframe/blender-scripts/merge_cargo_interior.py` — `NSVMT_*`,
  `TILT_STAGE_*`, `RHO_PRINT`/`RHO_SOLID`.
- `docs/structural_analysis.md` §3 (load factors, FOS 4.0 target), §6.4/§7.3
  (CF-PETG allowables), §1.1.5 (T/W and the mass notice).
- `REFERENCES.md` REF-MAT-002 (20 % CF-PETG, 77 MPa flexural / 6.67 GPa).
- Volumes and bounding-box fill fractions measured 2026-08-30 with
  `trimesh`/`manifold3d` against the published STLs under `/usr/bin/python3`.

---

*Analysis and plan drafted by Claude (Claude Opus 5, Anthropic) under the
author's direction, 2026-08-30, per `AGENTS.md` §3 AI attribution.*
