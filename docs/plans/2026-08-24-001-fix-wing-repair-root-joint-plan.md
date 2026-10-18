---
title: "fix: Wing S1223 repair, root bearing-seat joint, and tenon fallback spar"
date: 2026-08-24
plan_type: fix
artifact_contract: ce-unified-plan/v1
artifact_readiness: implementation-ready
execution: code
product_contract_source: ce-plan-bootstrap
---

# fix: Wing S1223 repair, root bearing-seat joint, and tenon fallback spar

**Target repo:** Serenity-UAV (this repo)

---

## Summary

Closes the remaining open items under `airframe/wings-nacelles/TODO.md` §1.1.2
(Wings): the S1223 self-intersection blocker (WING-01), the spar-root
bearing-seat re-cut and CF thwart pair (SPAR-01), the DS3225 torque
re-derivation and RAIL-2 budget (SPAR-02), the tip-thickness/spar-station
canon check, and the two wing STL re-bakes. It also closes the paired
fuselage-side items that are the same joint: CARGO-01/CARGO-02 (bearing-seat
bore) and CARGO-03c (tenon structural sizing), per
`airframe/fuselage-mid/WBS.md` §1.1.1.2.

**Most of the hard architecture is already owner-decided and dated
2026-08-23/24** (two-bearing overhung spar, CF thwart couple closure, tenon
vs. second-spar branch rule) — this plan is the implementation of those
decisions, not a re-derivation of them. Two forks that were still open were
confirmed for this plan: the CF thwart stations (Y −40 fore / Y +118 aft) and
the CARGO-03c branch (build the second-spar fallback now, since no CF-PETG
coupon data exists and the owner's own rule routes <15 MPa to that branch).

## Problem Frame

The wing subsystem has one true blocker and three coupled structural
redesigns, all interacting through the same wing-root joint:

1. **WING-01 (blocker).** The tabulated `S1223_UPPER`/`S1223_LOWER` coordinate
   tables produce a self-intersecting outline (surfaces cross at x/c 0.742,
   thickness goes negative to −1.96/−2.05 mm before returning to zero at the
   TE). `wing_solid()`'s OpenSCAD `hull()` loft masks this — the exported STL
   is watertight because `hull()` takes the convex hull, which is 1.647× the
   true outline's area (39.3% phantom material). This blocks fabrication, the
   mass budget, and every aero claim.
2. **SPAR-01.** The 8 mm 4130 tilt spar cannot pass through the fuselage
   centerline (the nacelles occupy it), and independent per-side rotation
   rules out a rigid carry-through spar mechanically, not just structurally.
   The owner-directed fix: each spar is a determinate overhung shaft on a
   wingtip bearing (MF128ZZ) and a fuselage-wall bearing (F688ZZ), driven by
   its own nacelle-side servo; the couple each side hands the wall (115.1 N,
   14.54 N·m at ultimate) is closed by two CF thwarts (fore Y −40, aft
   Y +118) instead of a continuous member. The shell re-cut (bore → bearing
   seat, terminate at the wall) is unbuilt; so are the thwarts.
3. **CARGO-03c.** The wing-root tenon is now a structural joint (spanwise
   load terminates at the wall through it, not through a carry-through spar),
   developing 10.14 MPa bearing at ultimate. The repository has no CF-PETG
   bearing allowable — only a 5 MPa bond-limited figure, which fails. Per the
   owner's decision rule, <15 MPa fusion strength routes to a second,
   forward-of-main-spar rod (Ø8 mm at 14 mm from the LE) instead of growing
   the tenon. That rod is fully sized in `airframe/fuselage-mid/WBS.md`
   §1.1.1.2 but not yet geometried.
4. **SPAR-02.** The DS3225 tilt servo's own datasheet only clears the cited
   ≥25 kgf·cm requirement to 98% (24.5 kgf·cm at 6.8 V), and that requirement
   traces to a spec pick (`serenity-rev-r.jsx` L383), not a load derivation —
   while the pivot is *at the nacelle CG*, which nulls the gravity moment by
   design. RAIL-2's 1.2 A placeholder is also ~1.9× under the DS3225's cited
   2.3 A stall current. Needs an analytical re-derivation from the actual
   aero+inertia loads before any part change is considered.

Canon-checking tip thickness and spar station against the Serenity silhouette,
and re-baking both wing STLs, are the closing steps that depend on 1–3 above
being fixed first (the current bakes are stale against Rev S1b/S1c geometry
and, more fundamentally, against an invalid airfoil).

## Requirements

- **R1** — `S1223_UPPER`/`S1223_LOWER` are replaced with a validated
  (non-self-intersecting) S1223 coordinate table, sourced from the UIUC
  Airfoil Coordinates Database and cited in `REFERENCES.md` with a validated
  URL. `tools/wing_airfoil_integrity.py` reaches PASS.
- **R2** — The wing loft method (`hull()` vs. a true swept/lofted solid) is
  re-decided based on the corrected table's convexity ratio, per the existing
  gate's tolerance.
- **R3** — Both wing STLs (`wing_nacelle_pylon_revo.stl`,
  `wings_s1223_revo.stl`, port + starboard) are re-rendered and re-baked
  against the corrected airfoil and current Rev S1b/S1c constants
  (`THICKNESS_SCALE_TIP`, `SPAR_BORE_STATION`, Hall station).
- **R4** — The cargo shell's spar interface becomes a bearing seat (sized to
  F688ZZ) that terminates at the fuselage wall (X −100 port / −240 stbd)
  instead of a full-span Ø12.3 clearance bore. Closes CARGO-01 and CARGO-02
  together (same shell edit, per WBS.md sequencing).
- **R5** — Two CF thwarts (2 mm × 25 mm `CF-PLATE-2MM`, fore Y −40 / aft
  Y +118) are authored as OpenSCAD parts with landing pads and merged into
  the cargo shell, closing the couple SPAR-01 identifies.
- **R6** — The wing-root tenon's fallback second spar (Ø8 mm rod, 14 mm from
  LE, 40 mm embed into the existing wall boss geometry) is authored in both
  the wing SCAD (bore) and the cargo-shell SCAD (boss), parametrized so the
  enlarged-tenon path remains a documented, flagged alternative if a future
  coupon test clears ≥15 MPa.
- **R7** — The DS3225 torque requirement is re-derived analytically from the
  wing's actual aero + inertia loads at the CG pivot (not the L383 spec
  pick), and RAIL-2's current budget is resized to the DS3225's cited 2.3 A
  stall figure per servo with margin. Bench-verified stall current stays an
  explicit open item (cannot be fabricated) — see Scope Boundaries.
- **R8** — Tip thickness and spar station are canon-checked against the
  Serenity reference silhouette (the existing `REF-CAD-002`/`REF-CAD-003`
  hierarchy) using FreeCAD, and the result is recorded in WBS.md.
- **R9** — All re-verification gates re-run clean against the final geometry:
  `wing_airfoil_integrity.py`, `wing_internal_clearance.py`,
  `wing_root_deconflict.py`, `wing_spar_carrythrough.py`,
  `cargo_bay_envelope.py`, `nacelle_servo_deconflict.py`,
  `landing_gear_wing_clearance.py`, `validate_stls.py`.
- **R10** — `WBS.md` (root wings-nacelles and fuselage-mid), `TODO.md`
  (wings-nacelles), and `REFERENCES.md` are updated per repo convention:
  close resolved sub-items in WBS.md first, delete the corresponding TODO.md
  lines, add new `REF-CAD-*`/`REF-MAT-*` entries with validated URLs (or mark
  "requires verification" where a physical test is the only path).

## Key Technical Decisions

**KTD1 — Second-spar fallback is built now, as a bonded CF rod, not the
enlarged tenon.**
*(session-settled: user-directed — chosen over waiting for coupon data, and
refined 2026-08-24 from the WBS.md steel-press-fit-boss sizing to a bonded
CF rod: no CF-PETG bearing/fusion coupon test exists yet for the tenon's
mode, only a 5 MPa bond-limited figure (`docs/structural_analysis.md` §7.3)
that already fails the tenon at FOS 0.49; the owner's own 2026-08-23 decision
rule routes <15 MPa to the second-spar branch, and that branch is already
fully sized in `airframe/fuselage-mid/WBS.md` §1.1.1.2 CARGO-03c at 1.46 MPa
bearing — clearing the *existing* 5 MPa bond-limited figure at FOS 3.4
without needing new coupon data at all.)* Governs R6.

**Refinement (2026-08-24, user-directed):** build the rod as **CF, bonded**,
following the repo's own established pattern for CF-ROD tie-rods/boss pins
(`docs/structural_analysis.md` §6/§7: CF rod, 0.1 mm/side clearance bore,
West System 105/206 epoxy, cure 24 h before foam pour) rather than the
originally-sketched steel-in-a-press-fit-boss. This is a mass win (CF is
~1/5 the density of the 4130 the WBS.md table assumed — roughly 48 g/pair →
~10 g/pair) and reuses an already-precedented joint, not a new one. It is
**not** an escape from needing CF-PETG data: the socket wall the rod bears
against is still CF-PETG (the hull skin), so the governing allowable is
still the repo's existing cited 5 MPa bond-limited figure — the refinement's
value is that the load (1.46 MPa bearing at the sized station/embed) is low
enough to already clear that existing figure, not that it sidesteps needing
one. Do not re-derive this against a plain-PETG datasheet — that would be
citing the wrong material for the actual bore wall.

The enlarged-tenon geometry stays documented but unbuilt, gated behind a
named OpenSCAD constant so it can be swapped in if a future coupon test
clears ≥15 MPa — do not delete the sizing table that supports it.

**Further refinement (2026-08-24, user-directed): trade the tenon for a
second (aft) bonded CF rod — asymmetric diameter, not a mirror of the
forward rod.** A feasibility pass against the corrected S1223 geometry
found: (a) an aft rod matching the forward rod's Ø8.2 mm bore does not fit
anywhere — the main spar bore's aft edge (49.30 mm) and the Hall conduit's
fixed Rev S1c station (52.25–55.75 mm) leave no room, and any station past
that breaks the repo's 1.16 mm minimum wall standard by x≈60mm and breaks
through the skin entirely by x≈70mm; (b) a **smaller Ø6.2 mm bore** (6 mm CF
rod + 0.1 mm/side clearance) *does* clear, root-only (not full-span like the
main spar), at approximately **x = 60–62 mm from the LE** — 1.7–2.0 mm root
wall, some clearance margin to both the spar bore and the Hall conduit.
**User-directed 2026-08-24: build the Ø6.2 mm aft rod.** Its bearing stress
at Ø6×40mm embed is 1.95 MPa per the existing WBS.md CARGO-03c table,
clearing the cited 5 MPa bond-limited CF-PETG allowable at FOS ≈ 2.6 — lower
margin than the forward rod's FOS 3.4, but still a real pass against
existing cited data, no new coupon test required.

This makes U5 a **two-rod system, asymmetric diameter** (Ø8.2 mm forward at
14 mm, Ø6.2 mm aft at ~60–62 mm, both root-only embeds except the forward
rod may be full-span if that's what the initial forward-rod build already
did — reconcile at implementation time, don't assume), reacting the root
couple as a true two-point system. **The tenon (`fuselage_root_tab()`) is
traded out of the structural load path entirely** — reduce it to a small
locating/index feature only, or remove it if the two rods alone provide
adequate radial location, and correct its stale "carries spanwise load"
comment either way. Recompute the couple-force split for a two-rod system
(not the single-rod method WBS.md's table used) before finalizing embed
depths — the separation from the main spar differs for each rod, so each
reacts a different share of the 14.60 N·m ultimate root moment.

**KTD2 — CF thwart stations are Y −40 (fore) / Y +118 (aft).**
*(session-settled: user-directed — chosen over the alternative of holding
geometry work until a separate confirmation pass: these stations were already
the WBS.md recommendation, sited on measured-intact structure clear of both
landing-gear bays, splitting the couple 0.51/0.49.)* Governs R5.

**KTD3 — WING-01's coordinate source is UIUC, not a repository restatement.**
Root `AGENTS.md` §4 forbids sourcing a coordinate table from memory. The
implementer must fetch the actual UIUC Airfoil Coordinates Database S1223
entry (Selig), not approximate it from the comparison table already in
WBS.md (that table is explicitly a comparison, not a transcription source).

**KTD4 — `hull()` vs. true loft is decided from the corrected geometry, not
assumed.** The current `hull()` masking (1.647× area) is a defect *of the
old broken table*; a valid S1223 table may or may not still convexify badly
under `hull()`. Re-run `wing_airfoil_variants.py`/the airfoil integrity gate's
convexity-ratio report against the corrected table before deciding whether a
true loft (e.g. `BOSL2` skin/loft or a manual `polyhedron()` between stations)
is required. Do not pre-commit to a loft rewrite if the corrected section
turns out convex enough.

**KTD5 — SPAR-02 re-derives the requirement before any part change.**
Per the owner's direction: the pivot sits at the nacelle CG (nulling the
gravity moment by design), so ≥25 kgf·cm as cited is a spec pick, not a load
derivation. This plan re-derives the actual required torque from aero +
inertia loads only, using the same load factors as `docs/structural_analysis.md`
§3 and the geometry already measured in `tools/wing_spar_carrythrough.py`. If
the re-derived requirement is ≤24.5 kgf·cm, DS3225 stands and no part change
is needed.

## High-Level Technical Design

```mermaid
flowchart TD
    A[UIUC S1223 coordinates] -->|R1| B[Replace S1223_UPPER/LOWER]
    B -->|wing_airfoil_integrity.py| C{PASS?}
    C -->|convexity ratio| D[KTD4: hull vs true loft]
    D -->|R3| E[Re-render + re-bake both wing STLs]

    E --> F[wing_internal_clearance.py]
    E --> G[wing_root_deconflict.py]
    E --> H[wing_spar_carrythrough.py]

    subgraph Shell re-cut (R4/R5/R6)
        I[Bearing-seat bore, terminate at wall] --> J[CF thwarts fore/aft]
        I --> K[Second-spar rod boss, 14mm from LE]
    end

    E --> I
    F & G & H --> L[cargo_bay_envelope.py]
    J & K --> L
    L --> M[nacelle_servo_deconflict.py / landing_gear_wing_clearance.py]
    M --> N[FreeCAD mating check: bearings, tenon/mortise, rod bores]
    N --> O[Canon-check tip t/c + spar station vs silhouette]
    O --> P[WBS.md / TODO.md / REFERENCES.md updates]

    Q[SPAR-02: re-derive torque + RAIL-2] --> P
```

## Implementation Units

### U1. Source and validate a correct S1223 coordinate table

**Goal:** Replace the self-intersecting `S1223_UPPER`/`S1223_LOWER` tables
with a validated Selig S1223 table from the UIUC Airfoil Coordinates
Database, and get `wing_airfoil_integrity.py` to PASS.

**Requirements:** R1, R2 (KTD3, KTD4)

**Dependencies:** none — this is the blocker everything else re-bakes
against.

**Files:**
- `airframe/openscad/wings/wings_s1223_revo.scad` (or wherever
  `S1223_UPPER`/`S1223_LOWER` are currently defined — confirm exact path at
  implementation time, WBS.md references the file by function name only)
- `REFERENCES.md` (new `REF-CAD-*` entry: UIUC database URL, S1223 dataset,
  retrieval date)
- `tools/wing_airfoil_integrity.py` (should not need changes — it is the
  gate; only extend if it cannot report a convexity ratio for KTD4)
- `tools/wing_airfoil_variants.py` (reference for how camber/thickness
  decomposition is currently done — reuse its decomposition, don't
  reimplement it)

**Approach:**
1. Fetch the actual S1223 dataset from the UIUC Airfoil Coordinates
   Database (`https://m-selig.ae.illinois.edu/ads/coord_database.html`,
   confirm exact file name/URL at fetch time — do not guess it from memory).
2. Add the `REF-CAD-*` entry to `REFERENCES.md` before using the data, per
   root `AGENTS.md` workflow (look up by REF-ID first; this is new, so
   assign the next unused `REF-CAD-NNN`).
3. Replace `S1223_UPPER`/`S1223_LOWER` with the validated table, preserving
   the existing chordwise-station sampling convention the rest of the file
   depends on (`midline_frac()`, `s1223_section()` camber/thickness
   decomposition from the Rev S1b fix — do not reintroduce the pre-S1b bug
   of scaling camber and thickness together).
4. Run `tools/wing_airfoil_integrity.py` — must PASS with no
   self-intersection and non-negative thickness across the full chord.

**Execution note:** Fetch real, quotable source data before writing any
table row — this is a hard fail-closed gate per `AGENTS.md` §4. If the
dataset cannot be retrieved, stop and report the blocker rather than
approximating.

**Test scenarios:**
- `wing_airfoil_integrity.py` reports a valid simple polygon (no
  self-intersection) for the corrected table.
- Thickness is non-negative at every sampled x/c from 0 to 1.
- The corrected table's t/c at x/c 0.60 and 0.975 stays consistent with the
  built-wing measurements already on record in WBS.md (12.7 mm / 1.5 mm,
  scaled to the current root/tip chords) — large deviation is a red flag,
  not necessarily an error, but must be explained.

**Verification:** `tools/wing_airfoil_integrity.py` exits PASS.

---

### U2. Decide and (if needed) implement true loft vs. `hull()`

**Goal:** Resolve KTD4 — determine whether `wing_solid()`'s `hull()` loft is
acceptable against the corrected table, or whether a true swept/lofted solid
is required.

**Requirements:** R2 (KTD4)

**Dependencies:** U1

**Files:**
- `airframe/openscad/wings/wings_s1223_revo.scad` (`wing_solid()`)
- `tools/wing_airfoil_integrity.py` (read its convexity-ratio tolerance/report
  before deciding)

**Approach:**
1. Run the airfoil integrity gate's convexity-ratio check against the
   corrected U1 table (the gate is described in WBS.md as already reporting
   this ratio for the old table — 1.647×).
2. If the ratio is within tolerance, keep `hull()` and document why in a
   short comment plus a WBS.md note (do not silently keep it without
   checking).
3. If not, replace the per-station `hull()` loft with a true loft between
   sections — e.g. an OpenSCAD `polyhedron()` built from matched-vertex
   station outlines, or a BOSL2 `skin()`/`sweep()` if the module set already
   uses BOSL2 elsewhere in this repo (check before introducing a new
   dependency). Keep the existing bore/cableway boolean operations working
   against whichever solid results.

**Execution note:** This is a real branch point — do not implement the loft
rewrite speculatively before U1's corrected table proves it's needed.

**Test scenarios:**
- Convexity ratio report from the integrity gate, before/after, is recorded.
- If a true loft is built: the resulting solid is manifold
  (`tools/validate_stls.py` reports 0 boundary, 0 non-manifold, 1 body) and
  its cross-sectional area at 3+ stations matches the tabulated outline
  within the gate's tolerance (not the old convex-hull area).

**Verification:** `tools/wing_airfoil_integrity.py` convexity check passes
its tolerance; `tools/validate_stls.py` passes on the resulting STL.

---

### U3. Bearing-seat spar-root re-cut (cargo shell) — closes CARGO-01/CARGO-02

**Goal:** Replace the cargo shell's full-span Ø12.3 mm clearance bore with a
bearing seat sized to F688ZZ, terminating at the fuselage wall (X −100 port /
−240 stbd), per SPAR-01/CARGO-02.

**Requirements:** R4 (KTD1 does not apply here — this is the main spar, not
the fallback rod)

**Dependencies:** none (independent of U1/U2 — this is fuselage-side
geometry); should land before U4/U5 which build on the same shell region.

**Files:**
- `airframe/blender-scripts/merge_cargo_interior.py` (`WING_SPAR_BORE_D`
  12.3 → 8.3 is already-noted as wrong-diameter fix; `WING_SPAR_BOSS_OD`
  re-derived from F688ZZ OD, not the retired Ø22 press-fit figure)
- `airframe/openscad/fuselage/cargo/cargo_sect_shell24.scad` (or current
  canonical cargo shell source — confirm path; WBS.md references
  `cargo_sect_shell24.scad` Rev S1's spar bearing blocks as the feature to
  revise)
- `current-specification/bom_revS.csv` (`CF-TUBE-12MM` row → 8 mm OD AISI
  4130 hollow spar; already flagged as stale in WBS.md CARGO-02)
- `REFERENCES.md` (F688ZZ bearing spec — confirm it already has a REF entry
  from the wingtip/root bearing selection; add one if not, with a validated
  vendor/datasheet URL — do not fabricate bearing dimensions)

**Approach:**
1. Look up F688ZZ's actual OD/ID/width from a validated datasheet (the
   bearing choice itself is already owner-settled per WBS.md — "Root bearing
   stays F688ZZ" — this unit sources its dimensions, not its selection).
2. Re-derive `WING_SPAR_BOSS_OD` from the F688ZZ OD plus a press-fit/seat
   allowance (do not reuse the retired Ø22 figure without checking it still
   fits the new bearing).
3. Cut the bore as a bearing seat (not a through-bore) stopping at the wall
   station (X −100 port / −240 stbd, per SPAR-01's measured stations).
4. Update `WING_SPAR_BORE_D` 12.3 → 8.3 mm alongside the seat change (same
   shell edit, per WBS.md CARGO-02 sequencing note).
5. Update `bom_revS.csv` `CF-TUBE-12MM` row to the 8 mm OD AISI 4130 hollow
   spar already specified in `wings_s1223_revo.scad`.
6. Re-run `merge_cargo_interior.py` to produce the merged cargo shell.

**Patterns to follow:** the existing bearing-boss pattern already used for
the wingtip bearing (MF128ZZ) in the wing SCAD — mirror its
seat-sizing/clearance convention for consistency.

**Test scenarios:**
- `tools/cargo_bay_envelope.py` reaches PASS (bay clear span X −240…−100 =
  140 mm at full height; the 4×3×3 in payload fits) — this is CARGO-01's
  closing gate.
- The bearing seat bore diameter matches F688ZZ's actual OD (from the
  sourced datasheet), not a placeholder.
- `tools/validate_stls.py` passes on the re-merged shell (watertight, 0
  boundary, 0 non-manifold, 1 body).
- `tools/landing_gear_wing_clearance.py` still reports CLEAR on all 4 checks
  after the shell edit.

**Verification:** `cargo_bay_envelope.py` and `validate_stls.py` both PASS on
the re-merged, published shell.

---

### U4. CF thwart pair (fore/aft couple closure)

**Goal:** Author the two CF thwarts (2 mm × 25 mm `CF-PLATE-2MM`) at the
confirmed stations (Y −40 fore, Y +118 aft) with landing pads, merged into
the cargo shell.

**Requirements:** R5 (KTD2)

**Dependencies:** U3 (same shell region; land after the bearing-seat re-cut
so the thwart pads reference the final wall geometry, not the retired
through-bore version)

**Files:**
- new OpenSCAD source for the thwart parts (name per repo convention —
  check `airframe/openscad/fuselage/cargo/` for the existing module-per-file
  pattern before choosing a filename)
- `airframe/blender-scripts/merge_cargo_interior.py` (thwart pad
  integration into the merged shell)
- `current-specification/bom_revS.csv` (retire/re-scope the provisional
  `CF-PLATE-2MM` Y +30 ring line per WBS.md "Consequences to carry"; add the
  two thwart line items)

**Approach:**
1. Model each thwart as a flat CF plate spanning the belly-to-flank
   structure at its station, sized 2 mm × 25 mm per the existing stock
   (`CF-PLATE-2MM`), with landing pads sized to the intact structure bands
   already measured in WBS.md (fore Y −66…−32, aft Y +110…+125 — confirm the
   pad footprint stays inside those clear bands, clear of the gear bay
   apertures at Y −26…+18 and Y +86…+106).
2. Integrate into `merge_cargo_interior.py`'s merge sequence.
3. Retire the provisional `CF-PLATE-2MM` Y +30 ring geometry/BOM line per
   WBS.md's explicit instruction ("retire or re-scope... rather than
   finalising its PROVISIONAL DXF").

**Test scenarios:**
- `tools/wing_spar_carrythrough.py` re-run against the final geometry
  confirms both thwart FOS figures stay ≥ the target (WBS.md records 8.5/8.7
  against the conservative 300 MPa stand-in — re-verify these numbers hold
  once the thwarts are real geometry, not just the analysis).
- `tools/validate_stls.py` passes on the shell with thwarts merged.
- Mass delta matches or beats the WBS.md estimate (≈28 g / 0.062 lbm pair,
  net ≈50 g / 0.11 lbm saving vs. the retired ring) — record actual mass
  from the merged STL, not the estimate, in the WBS.md update (U8).

**Verification:** `wing_spar_carrythrough.py` and `validate_stls.py` both
PASS on the shell with both thwarts present.

---

### U5. Second-spar fallback: bonded CF rod (CARGO-03c)

**Goal:** Author the Ø8 mm fallback rod (14 mm from LE, 40 mm embed) as a
**bonded CF rod** — not a steel press-fit — as the default structural path
for the wing-root couple, per KTD1's 2026-08-24 refinement, with the
enlarged-tenon path left documented but flagged off.

**Requirements:** R6 (KTD1)

**Dependencies:** U3 (shares the wall boss region)

**Files:**
- `airframe/openscad/wings/wings_s1223_revo.scad` (new Ø8.2 mm bore — 8 mm
  CF rod + 0.1 mm/side clearance, per the `docs/structural_analysis.md`
  §6/§7 CF-ROD bonding convention — at 14 mm from LE, clear of the Hall
  conduit's 30 mm station per WBS.md's 11 mm margin figure)
- `airframe/openscad/fuselage/cargo/cargo_sect_shell24.scad` (matching
  Ø8.2 mm wall bore, 40 mm embed, mirroring `PORT_INB`/`PORT_OUTB` pattern
  already used for the main spar boss)
- `airframe/fuselage-mid/WBS.md` §1.1.1.2 (correct `fuselage_root_tab()`'s
  stale comment — "The tab provides radial restraint; the CF spar carries
  spanwise load" — per WBS.md's own note that this needs correcting once the
  tenon/second-spar design lands; record the bearing-stress check against
  the existing cited 5 MPa bond-limited CF-PETG figure, FOS 3.4, no new
  coupon data required to close this item)
- `current-specification/bom_revS.csv` (2× CF rod, ≈8 mm OD × ~50 mm,
  following the existing `CF-ROD-4MM` BOM line pattern — cite the same
  pultruded-CF supplier data already used there per
  `docs/structural_analysis.md` §1/§6; West System 105/206 epoxy per §7.1)
- A named OpenSCAD constant (e.g. `TENON_LOAD_PATH = "second_spar"` vs.
  `"enlarged_tenon"`) gating which structural path is active — KTD1 requires
  the enlarged-tenon geometry stay present but not default-active.

**Approach:**
1. Cut the Ø8.2 mm bore (8 mm CF rod + 0.1 mm/side clearance, matching the
   §6/§7 CF-ROD convention) through the wing at 14 mm from the LE (per
   WBS.md's sizing table — this station gives the largest separation from
   the main spar on a healthy 3.23 mm bore wall).
2. Cut the matching Ø8.2 mm, 40 mm-embed bore in the cargo shell wall,
   mirroring the main spar boss's embed pattern (`PORT_INB` −100 to
   `PORT_OUTB` −60).
3. Gate the enlarged-tenon geometry (from the existing `fuselage_root_tab()`
   sizing) behind the named constant, defaulted to the second-spar path.
4. Correct the stale structural-role comment in the tenon module.
5. Record in WBS.md that the bearing stress at this station/embed
   (1.46 MPa, from the existing WBS.md CARGO-03c table) already clears the
   repo's cited 5 MPa bond-limited CF-PETG figure (`docs/structural_analysis.md`
   §7.3) at FOS 3.4 — the socket wall is CF-PETG hull skin, not plain PETG,
   so this is the correct allowable to cite, and no new coupon test is
   required to close CARGO-03c under this branch (a coupon test still
   matters for tightening the margin or enabling the enlarged-tenon
   alternative, but is not a blocker here).

**Patterns to follow:** the CF-ROD-4MM tie-rod/boss-pin joints in
`docs/structural_analysis.md` §6–§7 — same bonding convention (0.1 mm/side
clearance, West System 105/206, cure before foam pour) and the main spar
boss's embed geometry (`PORT_INB`/`PORT_OUTB`) for the boss parametrization.

**Test scenarios:**
- `tools/wing_root_deconflict.py` reaches CLEAR with the second-spar bore
  present — confirm it stays clear of the Hall conduit (11 mm margin at the
  30 mm Hall station) and the tenon region (2.50 mm clearance at 85 mm
  station per WBS.md, not applicable at 14 mm but verify no other
  interference).
- Bearing stress at the rod, recomputed by `wing_spar_carrythrough.py`
  against the final 40 mm embed, matches or beats the WBS.md estimate
  (1.46 MPa at Ø8×40mm) — FOS 4.0 needs ≤5.9 MPa allowable, well under even
  the pessimistic 5 MPa bond-limited figure.
- The enlarged-tenon path, when the constant is flipped, still builds a
  manifold solid (regression-proof the alternate path even though it is not
  default-active).

**Verification:** `tools/wing_root_deconflict.py` and
`tools/wing_spar_carrythrough.py` both PASS against the second-spar
configuration.

---

### U6. Re-render and re-bake both wing STLs

**Goal:** Produce final port + starboard STLs for `wing_nacelle_pylon_revo`
and `wings_s1223_revo` against the corrected airfoil (U1/U2) and current Rev
S1b/S1c constants.

**Requirements:** R3

**Dependencies:** U1, U2 (must not bake against the still-broken airfoil or
an undecided loft method)

**Files:**
- `airframe/openscad/wings/wings_s1223_revo.scad`,
  `airframe/openscad/wings/wing_nacelle_pylon_revo.scad` (or current
  canonical paths — confirm at implementation time)
- `tools/bake_hull_frame.py` (existing bake tool — reuse, do not
  reimplement)
- STL outputs under the repo's existing STL output convention

**Approach:**
1. Render both wing SCAD sources (port + starboard) with `openscad`.
2. `python3 tools/bake_hull_frame.py Wing_Port Wing_Stbd` (per the exact
   invocation already recorded in WBS.md for the prior, now-stale bake).
3. Confirm the resulting envelope: Z max should still be set by the
   (unchanged) root section; only the corrected-airfoil tip geometry moves.

**Test scenarios:**
- `tools/validate_stls.py` passes on both baked wings (watertight, 0
  boundary, 0 non-manifold, 1 body).
- `tools/wing_internal_clearance.py` and `tools/wing_root_deconflict.py`
  both PASS against the newly baked geometry.
- `tools/wing_spar_carrythrough.py` re-run confirms the FOS figures in
  WBS.md still hold against the corrected-airfoil spar section (the spar is
  steel tube, unaffected by the airfoil fix, but bearing-seat clearances in
  the wing wall are section-dependent — re-verify, don't assume).

**Verification:** `validate_stls.py`, `wing_internal_clearance.py`,
`wing_root_deconflict.py` all PASS on the final baked STLs.

---

### U7. SPAR-02 torque re-derivation and RAIL-2 resizing

**Goal:** Analytically re-derive the tilt-servo torque requirement from
actual aero+inertia loads at the CG pivot (not the L383 spec pick), and
resize RAIL-2's current budget to the DS3225's cited stall current.

**Requirements:** R7 (KTD5)

**Dependencies:** U6 (uses final wing mass/geometry for the inertia term)

**Files:**
- `docs/TILT_SPAR_ANALYSIS.md` §2 (requirement derivation — supersede the
  L383 spec-pick citation with the re-derived figure and its own load-case
  table)
- `airframe/wings-nacelles/WBS.md` §1.1.2 SPAR-02 (record the re-derivation
  result)
- RAIL-2 sizing location (search for `RAIL-2` — likely in a power-budget doc
  or the avionics BOM; confirm exact file at implementation time)
- `REFERENCES.md` (the DS3225 stall-current figure is already cited; add a
  "requires verification" row for bench-measured stall current if one does
  not already exist under REF-SENSOR-013's entry — WBS.md notes this is
  still open)

**Approach:**
1. Using the same 4 g limit / 1.5× ultimate factor convention already
   applied in `docs/structural_analysis.md` §3, and the pivot-at-CG geometry
   already established in `docs/TILT_SPAR_ANALYSIS.md` §2, compute the
   required tilt torque from aero moment + inertia moment only (gravity term
   is nulled by the CG pivot, per the owner's stated reasoning — verify this
   nulling explicitly in the derivation rather than asserting it).
2. Compare the re-derived requirement against DS3225's 24.5 kgf·cm at 6.8 V.
   If the re-derived figure is ≤24.5 kgf·cm, DS3225 stands (no part change).
   If it exceeds 24.5 kgf·cm, flag as a genuine blocker requiring owner
   input on a servo change — do not silently pick a replacement part.
3. Resize RAIL-2's current budget to DS3225's cited 2.3 A stall current per
   servo (× number of tilt servos, × any repo-standard margin factor used
   elsewhere in the power budget), replacing the 1.2 A placeholder.
4. Record bench-verified stall current as still-open in `REFERENCES.md`
   (cannot be fabricated — physical test, see Scope Boundaries).

**Test scenarios:**
- The re-derivation's gravity-nulling claim is checked algebraically (pivot
  at CG ⇒ zero moment arm for the weight vector at all tilt angles), not
  just asserted.
- RAIL-2's resized budget is traced to a specific load case (2.3 A × N
  servos, stated explicitly) rather than a round number.

**Verification:** The re-derived torque requirement and its comparison
against DS3225 are recorded in both `TILT_SPAR_ANALYSIS.md` §2 and WBS.md
SPAR-02, with the pass/fail conclusion stated explicitly.

---

### U8. Canon-check, FreeCAD mating verification, and doc closeout

**Goal:** Canon-check tip thickness/spar station against the Serenity
silhouette, run a FreeCAD mating verification pass on the bearing seats and
rod bores, and close out WBS.md/TODO.md/REFERENCES.md.

**Requirements:** R8, R9, R10

**Dependencies:** U1–U7 (this is the closing unit — needs final geometry
from all prior units)

**Files:**
- FreeCAD verification script (new, under `tools/` following the existing
  `tools/wing_*.py` naming convention — e.g. a script that imports both
  final STLs plus bearing/rod stand-ins and reports interference/clearance,
  mirroring how `wing_root_deconflict.py` already does this for other
  features)
- `airframe/wings-nacelles/WBS.md` (close SPAR-01, SPAR-02, WING-01
  checkboxes and their open sub-steps; add the canon-check result)
- `airframe/wings-nacelles/TODO.md` (delete the now-closed lines per repo
  convention — close in WBS.md first)
- `airframe/fuselage-mid/WBS.md` (close CARGO-01, CARGO-02, CARGO-03c;
  correct the `fuselage_root_tab()` comment reference)
- root `TODO.md` §0.8 (add/update the CF-PETG bearing coupon and bench
  stall-current items if not already tracked at LG-11)
- `REFERENCES.md` (finalize all new/updated REF-ID entries)

**Approach:**
1. Canon-check: compare final tip thickness (t/c) and spar station against
   the Serenity reference silhouette hierarchy already established in
   `REFERENCES.md` (REF-CAD-002 Nick Henning renders, REF-CAD-003 QMx, in
   that authority order) using FreeCAD's measurement tools against the
   imported reference geometry (or existing profile PNGs if no reference
   mesh is available — confirm what's actually on file before assuming a
   3D reference exists).
2. FreeCAD mating check: import final wing + cargo shell STLs, place bearing
   stand-ins (F688ZZ, MF128ZZ) and the second-spar rod at their final
   positions, and confirm zero interference / correct seat clearance at each
   joint (spar bearing seats ×2, tenon/mortise, second-spar rod bore/boss).
3. Run the full re-verification gate list (R9) and record pass/fail for
   each in the WBS.md closeout.
4. Update WBS.md (close resolved items, correct stale comments), delete
   corresponding TODO.md lines, finalize REFERENCES.md entries.

**Test scenarios:**
- FreeCAD mating check reports zero interference at all bearing/rod/tenon
  joints, with clearance values recorded (not just pass/fail) — mirror the
  numeric-clearance-table convention already used throughout WBS.md.
- Canon-check records actual measured tip t/c and spar station against the
  reference, with the delta stated (even if the delta is zero/negligible —
  do not omit the number).
- Every gate in R9 is re-run against final geometry and its result recorded.

**Verification:** All R9 gates PASS; WBS.md/TODO.md/REFERENCES.md reflect
the final closed state with no stale checkboxes (per this repo's own
standing rule — every `[ ]` whose text says resolved gets closed
immediately).

## Scope Boundaries

**In scope:** all OpenSCAD/geometry, FreeCAD verification, gate-script
re-runs, and documentation closure listed in U1–U8.

**Deferred to Follow-Up Work (not this plan):**
- CF-PETG bearing/fusion coupon testing (ASTM D695) for CARGO-03c — physical
  test, tracked at root `TODO.md` §1.1.4 LG-11. This plan builds the
  second-spar fallback so it does not block on the coupon result (KTD1); if
  a future coupon clears ≥15 MPa, swapping to the enlarged-tenon path is a
  follow-up unit, not part of this plan.
- CF plate bending allowable certification (ASTM D3039/D695) for the
  thwarts — tracked at root `TODO.md` §0.8. The thwarts are built now against
  the existing conservative 300 MPa stand-in (FOS 8.5/8.7); re-verification
  against certified figures is follow-up.
- Bench-measured SPT5425LV/DS3225 stall current and MMPDS/AMS allowable
  verification for 4130 — both explicitly "requires verification" physical
  tests per `REFERENCES.md`, tracked at root `TODO.md` §0.8.
- OpenFOAM aerodynamic re-verification of the corrected S1223 section is
  **not required** for this plan — `tools/wing_cfd_openfoam.py` is
  independently blocked on mesh generation (committed WIP per WBS.md) and
  the corrected-airfoil aero claim is a geometry-validity fix, not a new
  aero regime. If mesh generation becomes unblocked separately, re-running
  it is follow-up work, not a dependency of this plan.
- The `s1223_section()` camber/thickness decomposition itself (Rev S1b) is
  already correct and out of scope — only the coordinate *table* is wrong.

**Out of scope / not this plan's decision:**
- Any change to bearing part numbers already selected (F688ZZ, MF128ZZ) —
  those are settled; this plan only sources their dimensions for the seat
  cut.
- Payload/mission envelope changes (README.md steps 6/9) — CARGO-01's
  resolution already avoided needing these per the owner-selected
  resolution 1.

## Risks & Dependencies

- **UIUC dataset availability/format.** If the UIUC database's S1223 file
  cannot be fetched or parsed cleanly, U1 blocks the entire plan (everything
  downstream depends on a corrected airfoil). Mitigate by confirming fetch
  access early, before starting other units in parallel.
- **`hull()` replacement risk (KTD4).** If a true loft is required, this is
  the highest-uncertainty unit in the plan — OpenSCAD lofting between
  dissimilar station outlines is nontrivial. Budget it as its own
  checkpoint; do not assume it is a drop-in replacement for `hull()`.
- **SPAR-02 re-derivation could invalidate DS3225.** If the re-derived
  torque exceeds 24.5 kgf·cm, this surfaces as a genuine blocker requiring
  owner input (per KTD5) — do not silently substitute a larger servo, which
  would cascade into the already-settled servo-pad geometry (SPT5425LV/
  DS3225 pad family).
- **Second-spar rod clearance is tight in places.** WBS.md's own table shows
  aft stations going negative wall thickness — U5 must stay at the
  identified 14 mm station and not drift aft during implementation.

## Verification Contract

- `tools/wing_airfoil_integrity.py` — PASS (U1, U2)
- `tools/wing_internal_clearance.py` — PASS (U6)
- `tools/wing_root_deconflict.py` — CLEAR (U5, U6)
- `tools/wing_spar_carrythrough.py` — FOS targets met, all cases (U4, U5, U6)
- `tools/cargo_bay_envelope.py` — PASS, 4×3×3 in payload fits (U3)
- `tools/nacelle_servo_deconflict.py` — CLEAR (U3, U4)
- `tools/landing_gear_wing_clearance.py --proud` — CLEAR, all 4 checks (U3, U4)
- `tools/validate_stls.py` — watertight, 0 boundary, 0 non-manifold, 1 body,
  on every re-baked/re-merged STL (U3, U4, U5, U6)
- FreeCAD mating check (new script, U8) — zero interference at every
  bearing/rod/tenon joint

## Definition of Done

- WING-01 is closed: corrected S1223 table cited in `REFERENCES.md`, gate
  PASSES, both wings re-baked against it.
- SPAR-01 is closed: bearing-seat re-cut, CF thwarts built and verified,
  `TILT_SPAR_ANALYSIS.md` and `structural_analysis.md` §5 updated per the
  WBS.md instruction.
- SPAR-02's requirement is re-derived and recorded; RAIL-2 is resized; the
  bench-verification gap is explicitly logged, not silently closed.
- CARGO-01/CARGO-02/CARGO-03c are closed in `airframe/fuselage-mid/WBS.md`.
- Tip thickness/spar station canon check is recorded with measured deltas.
- Every Verification Contract gate above PASSes against final, published
  geometry (not against source scripts alone).
- `WBS.md` (both files), `TODO.md` (wings-nacelles), and `REFERENCES.md` are
  updated per repo convention with no stale `[ ]` items whose own text
  already says resolved.

## Sources & Research

- `airframe/wings-nacelles/TODO.md` §1.1.2/§1.1.3 (open-items index)
- `airframe/wings-nacelles/WBS.md` §1.1.2 (SPAR-01, SPAR-02, WING-01 full
  detail, all owner-dated 2026-08-23/24)
- `airframe/fuselage-mid/WBS.md` §1.1.1.2 (CARGO-01, CARGO-02, CARGO-03,
  CARGO-03b, CARGO-04 — the paired fuselage-side items)
- `REFERENCES.md` "requires verification" table (CF-PETG bearing/bond
  allowables, 4130 MMPDS verification, SPT5425LV stall current — all
  physical-test-gated items carried into Scope Boundaries)
- PR #189 (merged into `main`) — closed CARGO-03/03b/04 (mortise
  penetration, tenon/mortise datum fix), gated (not fixed) WING-01
- `tools/wing_spar_carrythrough.py`, `tools/wing_root_deconflict.py`,
  `tools/wing_airfoil_integrity.py` (existing gates this plan re-runs, not
  reimplements)
- External research was not run for this plan: the architecture
  (bearing-seat termination, thwart couple closure, tenon-vs-second-spar
  branch rule) is already owner-decided in-repo with load figures already
  computed against repo-standard factors; the one external fact this plan
  needs (validated S1223 coordinates) is sourced live during U1 from the
  UIUC Airfoil Coordinates Database, not researched here.
