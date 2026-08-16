# Serenity UAV — Airframe Wings and Nacelles Work Breakdown Structure (Detail)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0
**Current design revision:** Rev S (2026-07-04)

> **Detail-holder for the root WBS.** The repository-root [`TODO.md`](../../TODO.md)
> is a compact index — headings, subheadings, and short (<=70-char) checkbox items
> only, per root `AGENTS.md`. This file carries the full task detail for the WBS
> branches the root indexes below. Close an item here first, then check it off in
> the root index as a commit prerequisite (root `AGENTS.md` "Revisions and Version
> Control").

*"Curse your sudden but inevitable betrayal."*

---

## §1.1.2 — Wings
*(root `WBS.md` §1.1.2)*


**Wing pylon (OpenSCAD — Rev S integrated design; carried fwd from Rev O):**

- [x] **wing_nacelle_pylon_revo.stl** — `openscad -o ... serenity/stl/wing_nacelle_pylon_revo.scad` [SUPERSEDED]
    - Verify WING_SLOT_W and WING_SLOT_H against tip chord 93 mm (Rev R1 planform) before printing — pocket 50×40 mm uses 54 % of tip chord; confirm pylon block clears airfoil walls
    - Verify WING_BOLT_R (16 mm) does not exceed S1223 half-thickness at 50 % tip chord (≈ 9.6 mm above chord line at 93 mm chord); reduce to ≤ 12 mm if pylon block geometry requires it
- [x] **wings_s1223_revo.stl** — Rev R1 planform (2026-06-14): root 129 mm, tip 93 mm, zero LE sweep; STLs regenerated and baked ✓
    - **[x]** Verify cargo-section wing-root mortise dimensions against new root chord 129 mm (was 161 mm); `cargo_sect_shell24.scad` mortise slot (currently 30.8×20.8×15 mm) may need resizing and re-centring
    - **[x]** Re-check root-tab centre position: with 129 mm chord the tab centres at hull Y ≈ +57.5 mm (was +73.5 mm); confirm mortise centre in cargo SCAD matches
    - **[x]** Verify wing TE position (hull Y≈+122 mm port, +117 mm stbd) clears cargo-section aft interior features; cargo aft boundary is hull Y≈+132 mm — 10 mm clearance

##### 1.1.2.1 *Rev R1a — spar straightened + camber-centred + EDF cableway (2026-07-07)*

- [x] **Spar bore de-skewed** — `wings_s1223_revo.scad`: replaced the constant-30%-
    chord-fraction bore (which walked 10.8 mm / 7.2° forward over span under the
    straight LE — the "swept" cutout) with a bore at a **constant chordwise station
    (`SPAR_BORE_STATION` = 22 mm)** → parallel to the LE. Bore centre height now
    reads the **actual S1223 camber midline at each station** (`midline_frac()`),
    fixing the Rev R1 chord-line centring that broke out the lower surface AND the
    single-constant estimate that clipped the upper surface at the root.
- [x] **Tip thickened for spar fit** — `THICKNESS_SCALE_TIP` = 1.25 (root unchanged);
    tip t/c 12.14 % → ≈ 15.2 %. Needed because the tip section (11.3 mm max) is
    thinner than the Ø12.3 bore. Both wings re-rendered, baked, watertight ✓
    (vol 103 096 mm³, Z max +76.99 mm — within documented envelope). Min walls
    (mesh-measured): spar **1.16 mm** (root) → 1.44 mm; cableway 1.7–4.3 mm.
- [x] **EDF cableway added** — two Ø7 mm spanwise conduits at 40 % chord
    (`cableway_bore()`): 40 A EDF ESC power + ESC signal split across the two;
    nav-light 3-core routes through the hollow spar (Ø9 mm tube ID). Section
    figure: `docs/img/wing_rev_r1a_sections.png`.
- [x] **Fuselage spar-interface mismatch — RESOLVED 2026-08-16 (Rev S1b), owner
    decision: move the spar aft to 35 % root chord.** §1.1.1.3 cut the cargo-shell
    Ø12.3 spar bore + Ø22 bearing bosses at the **old** 30 %-chord line while the
    Rev R1a wing spar sat at the 22 mm station, so the spar could not pass through
    both parts. Neither original option was taken: (a) relocating the fuselage bore
    to the 22 mm line would have left the nacelle slid forward to hull Y +15 to
    reach it, and (b) keeping the fuselage bore needed a ~1.6× tip. Instead **both**
    parts moved onto one station, **45.15 mm = 35.0 % root chord**, which also
    brings the nacelle tilt axis back toward its canonical station instead of
    dragging the pod forward to meet the spar (the 2026-07-19 "slide the nacelle
    forward to Y = 15" reconciliation is hereby superseded).

    Applied:
    - `wings_s1223_revo.scad`: `SPAR_BORE_STATION` 22.0 → **45.15**;
        `THICKNESS_SCALE_TIP` 1.25 → **1.45**.
    - `merge_cargo_interior.py`: `WING_SPAR_Y` 0.30 → **0.35** of root chord
        (hull Y +31.7 → **+38.15**), and the spar bore + both bearing bosses moved
        off the mortise height onto a new `WING_SPAR_Z` = **68.42**.

    **Corrections to the original text of this item** (`AGENTS.md` §11.4 — model
    state outranks stale documentation):
    - "root ≈ hull **Z ≈ +71** (~8 mm up)" was a prose estimate and is **wrong**.
        The wing chord line sits at hull Z **58.01** — confirmed two independent
        ways: `port_tilt_spar_assembly.scad` states `SPAR_Z` is the camber
        midline plus 58, and solving this file's own recorded baked bound
        (Z max +76.99) against the root section top (+18.99 above the chord
        line) gives 58.01.
        The spar at the **old** 22 mm station was therefore at Z **66.52**,
        not 71; at the new station it is **68.42**.
    - The fuselage previously cut the spar at `WING_ROOT_Z` = 62.5, i.e. on the
        **mortise** height rather than the camber midline. That conflation is why
        the bore never lined up; the two are now separate constants.

    Verified: `tools/wing_spar_station_fit.py` (root wall 3.78 mm, tip wall
    1.17 mm ≥ the 1.16 mm the root already runs at);
    `tools/landing_gear_wing_clearance.py --proud` (all 4 checks clear).

    **Still gated on the re-bake — do not print either wing or cargo shell yet.**
    See the two open items directly below.

- [ ] **[OPEN] Re-render and re-bake both wings (Rev S1b OML change).** The tip
    OML changed twice over: `THICKNESS_SCALE_TIP` 1.25 → 1.45, and
    `s1223_section()` now scales **thickness only** about the camber line instead
    of scaling all of y (see §1.1.2 note below). The baked wing STLs and
    `docs/img/wing_rev_r1a_sections.png` are therefore **stale**. Re-render port
    and stbd, then `python3 tools/bake_hull_frame.py Wing_Port Wing_Stbd`, then
    `tools/validate_stls.py`. Expected envelope: Z max stays **+76.99** (set
    by the root section, which is unchanged); the tip top drops to ≈ +74.51.

- [ ] **[OPEN] Re-merge the cargo shell.** `merge_cargo_interior.py` carries the
    new spar station/height **and** the LG-10.4 wing keep-outs, but the published
    `cargo_sect_shell24_2mm_repaired.stl` predates both. One re-merge covers both
    changes; re-run `tools/validate_stls.py` and
    `tools/landing_gear_wing_clearance.py` after.

- [x] **`s1223_section()` scales THICKNESS ONLY (Rev S1b, 2026-08-16).** It
    previously did `scale([chord, chord * t_scale])`, which multiplies camber and
    thickness together, and its own comment conceded this was "acceptable for
    t_scale in [0.85, 1.0]" — a range `THICKNESS_SCALE_TIP` left at 1.25 and would
    have left far behind at 1.45. Uniform scaling at that factor drives S1223's
    camber from **8.12 % to 11.75 %**, i.e. a number chosen purely to fit a spar
    would have silently re-cambered a section whose whole value is its camber.
    Decomposing into camber + thickness and scaling only the thickness gives the
    **identical** section depth and the **identical** +1.17 mm of skin over the
    bore, with the camber line left exactly where Selig put it
    (`tools/wing_airfoil_variants.py`). Consequential fix: the bore-centre
    expressions (`spar_tip_y()`, `spar_bore()`, cableway, Hall-cable) no longer
    multiply `midline_frac()` by the thickness scale — doing so would now lift
    each bore off the camber line it is meant to be centred on.

    **Not CFD-verified.** Tip t/c rises 13.45 % → 19.47 %, and the drag
    penalty of a 19.5 % t/c tip at Re ≈ 2.1 × 10⁵ is **not** quantified: the
    OpenFOAM study
    built for it (`tools/wing_cfd_openfoam.py`) is blocked on mesh generation and
    is committed WIP. The camber-preservation argument above does not depend on
    CFD; the absolute penalty of the thicker tip does.

- [ ] **[OPEN] Canon-check `THICKNESS_SCALE_TIP` / `SPAR_BORE_STATION` against the
    Serenity wing silhouette** before print — carried over from the resolved item
    above, and now more pointed, since the tip is thicker than when it was raised.


## §1.1.3 — Nacelles
*(root `WBS.md` §1.1.3)*


**Nacelle shells (Blender, Rev S geometry; carried fwd from Rev O — must run on host machine):**

- [x] **Rev R1 nacelle stator shells** — **investigated 2026-06-22: this item is
    STALE / superseded, not run.** `blender_nacelle_revo.py` (now at
    `airframe/blender-scripts/`, not `thingverse-serenity/` — that path is
    archived) targets Rev O 18 in-scale inputs
    (`files-hollowed-18in/s_eng_{left,right}_shell24_50mm.stl`) that no
    longer exist at that path (only archived copies remain, at
    `archives/stl/`). The current Rev R1 design integrates the 11-fin stator
    as its own separate printed sleeve, `edf_stator_sleeve.scad` →
    `edf_stator_sleeve.stl` (already in the Makefile's `NACELLE_STLS` list
    and already published in `airframe/stls/nacelles/`) — confirmed
    up to date by re-rendering and vertex-diffing against the published
    file (2592/2592 verts, identical). **Pre-existing finding, not caused by
    today's changes:** `edf_stator_sleeve.stl` is not 2-manifold (OpenSCAD
    itself warns "may not be a valid 2-manifold" on render) — logged here
    per CLAUDE.md's mesh-verification-finding requirement; not fixed in this
    pass (unrelated to the nozzle/gear-train work above).

##### 1.1.3.1 *Nozzle*

- **Rev T3 (2026-08-09) — flap SHINGLE implemented (master/seal)** (user decision
  2026-08-09; found by CI "STL Validation", not by inspection).
    - [x] **Root cause** — `N_FLAPS` 8 × `FLAP_SPAN_DEG` 50° = 400° of arc on a
        360° circle, i.e. the deliberate 5° inter-flap overlap documented since
        Rev R2. But every flap was carved from the SAME radial band
        (`R_HINGE−FLAP_THICKNESS`..`R_HINGE`) at the same radius, so that overlap
        was a solid INTERPENETRATION, not a lap joint — physically unbuildable.
        Adjacent flaps therefore shared exactly coincident cylindrical surfaces,
        which exported as edges belonging to four facets (17 on the closed asm,
        12 on the open). `trimesh` reported the mesh non-watertight AND
        `mesh.split()` returned **zero** bodies, so the multi-body fallback in
        `tools/validate_stls.py` could not rescue it either. Confirmed in source,
        not inferred: re-rendering the committed SCAD reproduced the published
        mesh face-for-face (25 716).
    - [x] **Fix** — alternate flaps are now SEAL flaps lapped
        `FLAP_SHINGLE_GAP` = 0.2 mm (0.008 in) radially OUTBOARD of the MASTER
        flaps, closing the gap between adjacent masters from outside. Principle
        per REFERENCES.md **[REF-CAD-005]** (US 4,128,208, GE, expired). Both
        types keep an identical clevis on the hinge line, so all 8 still pivot on
        the same `R_HINGE` circle and straddle the same UNMODIFIED hinge bosses —
        housing, throat, ring and cam untouched.
    - [x] **Kinematics preserved** — the master band is unchanged, so
        `exit_r(φ) = R_HINGE − FLAP_LENGTH·sin φ` and the 75 %/105 % bore targets
        are numerically unaffected. Verified against the mesh: flow-boundary min
        radius 16.311 mm (0.642 in) and overall max radius 35.600 mm (1.402 in)
        identical before and after; the print-ready master STL renders
        byte-identical geometry (1 702 facets, 2 636.5722 mm³).
    - [x] **`FLAP_PHI` exposed** so each published assembly STL is reproducible
        from source instead of by hand-editing the tilt.
    - [x] **5° variant DISCARDED** (user 2026-08-09) —
        `nacelle_nozzle_iris-closed-5deg.stl` was an earlier, abandoned attempt at
        shingling the petals, exported from a source revision no longer in the
        tree (rendering the current file at φ = 5° reproduced neither its facet
        count nor its volume). Superseded by this revision; file deleted.
    - [x] **BOM/print split** — `PRINT-NACELLE-FLAP` (16) →
        `PRINT-NACELLE-FLAP-MASTER` (8) + `PRINT-NACELLE-FLAP-SEAL` (8), i.e.
        4 + 4 per nozzle. New print part `nacelle_nozzle_flap_seal.stl`. Masses
        re-measured from the rendered solids (master 2.637 cm³ → 3.4 g, seal
        2.874 cm³ → 3.7 g at 1.27 g/cm³ PETG); at 2.5 mm wall with 3 × 0.4 mm
        perimeters the section is effectively solid, so the previous 2 g/flap
        figure was an under-estimate.
    - [ ] **[OPEN — VERIFY] Mass/CG impact of the shingle.** Flap-set mass rises
        32.0 g → 56.8 g (1.13 oz → 2.00 oz), i.e. **+24.8 g (+0.87 oz) total,
        +12.4 g (+0.44 oz) per nacelle**, all of it aft of and outboard of the
        tilt pivot. Re-check the Rev T CG band (≈109–112 mm) and the tilt-servo
        torque margin against this before flight — see §1.1.3 "VERIFY Rev T CG".
    - [ ] **[OPEN — VERIFY] Seal-flap aerodynamic step.** The seal sits 0.2 mm
        proud of the masters' outer surface, so the flow boundary is no longer a
        single continuous cone: masters bound it over 4 × 50° of arc, seals over
        the intervening gaps at +2.7 mm radius. Confirm the residual step is
        acceptable for the "smooth, low-turbulence exit" goal by bench/CFD before
        flight; if not, the alternative is a scarfed (tapering-thickness) seal.

- **Rev T (2026-07-18) — Option B pushrod drive adopted** (user decision;
  `docs/NOZZLE_DRIVE_TRADE.md`). Supersedes the Rev S1 internal-ring gear drive.
    - [x] **Rev S2 bug fix** — corrected the `TAB_X`/`TAB_Z` follower-offset SIGN
        error that parked all 8 flap follower pins in the exhaust jet (pin_r
        20–24, aft of the throat) where they also could not reach the ring cam;
        restored to pin_r 31→35, bore smooth *(committed 9513086)*.
    - [x] **Cam-only unison ring** — deleted the internal ring gear; ring is now
        a plain cam disc with one pushrod lever ear. Ring Ø74→Ø66, housing
        Ø82→Ø71; follower band pulled to pin_r 29→31; drive-pinion throat relief
        removed *(nacelle_nozzle_iris.scad Rev T)*.
    - [x] **Rev T2 — flaps doubled** 20→40 mm (user direction): swing arc halved
        (PHI 1.79→12.64° vs 3.58→25.94°); bore stays clean, exit continuous.
    - [x] **Housing aft taper** (Stage 2) toward the cowl mould line; binding
        envelope is now the hinge bosses (≈Ø69.4), not the ring.
    - [x] **Pushrod drive part** (Stage 3) — `nacelle_nozzle_pushrod.scad`
        (spar crank + COTS ball-link pushrod); Makefile target added.
    - [x] **Gear train archived** (Stage 4) — sector gear, Pinion A, bevel pair,
        bevel housing, drive pinion (+STLs) → `airframe/archive/`; Makefile,
        PROJECT_INDEX/ARCHIVE_INDEX, serenity_assembly.py updated.
    - [x] **Pod pocket** grown `NOZZLE_RING_OD` 65→72 to seat the Ø71 housing.
    - [ ] **[OPEN — VERIFY] Spatial RSSR linkage synthesis** — solve crank
        radius, ball 3-D positions, and rod length for a MONOTONIC, non-locking
        0→90° tilt → 0→23.75° ring map that clears the nacelle skin over the
        full sweep. Current pushrod geometry is first-pass placeholder. Do NOT
        print for flight until closed.
    - [ ] **[OPEN — VERIFY] Re-bake the pod shells** (`nacelle_port_revs.stl` /
        `nacelle_stbd_revs.stl`) for the grown Ø72 nozzle pocket; the canonical-
        shell bake needs review before regenerating.
    - [ ] **[OPEN — VERIFY] Full housing ovalisation** to the cowl mould line +
        hinge-boss vs aft-cowl clearance — needs the assembly part-local→hull
        transform (serenity_assembly.py).
    - [ ] **[OPEN] Spar-crank placement** in serenity_assembly.py is first-pass
        (Y=0, Z=PIVOT_Z, X-axis clamp); confirm clock angle + pushrod routing.
    - [ ] **[OPEN] User WIP** `gear_option_compare.scad` / `gear_shell_compare.scad`
        (untracked) `use<>` the now-archived gear SCADs — update or archive.

- [x] **nacelle_nozzle_iris.stl** — `openscad -o ... serenity/stl/nacelle_nozzle_iris.scad`
    *(rendered 2026-06-22)* — Rev R1 50 mm iris: full-circle M=1.0 ring gear
    (72T, R=36mm pitch, replaces the old partial rack), outer housing,
    8-petal geometry sized to hit 75%→105% of the 50 mm bore (18.75→26.25 mm
    tip radius) across the -5°/140° nacelle tilt range. The file's default
    render was switched from the ring-only single part to the assembly
    preview (housing + ring + 8 petals at closed position), matching what
    `serenity_assembly.py` already expected to import. Mesh-verified: 8 of
    9 split bodies fully watertight; 1 non-manifold edge (of 26,381 total)
    where adjacent petals' designed 5° angular overlap touches at the
    closed position — cosmetic/assembly-preview only (this file is not the
    print source for the ring/housing/petals, which print as separate parts
    pulled from the same SCAD modules or, for the petal, from
    `blender_nozzle_gen.py`'s `nacelle_nozzle_petal.stl`); not pursued
    further here. `IDLER_SLOT_ANG` updated 0° → 50.9° to match the resolved
    idler shaft position (see §1.1.3.3).
- [x] **nacelle_nozzle_idler.stl** + **nacelle_nozzle_idler_bracket.stl**
    *(NEW component, rendered 2026-06-22)* — compound idler gear (Idler-In
    44T/R=22mm meshes Crown Pinion; Idler-Out 15T/R=7.5mm meshes the nozzle
    ring gear) plus its two-boss mounting bracket, each now a separate STL.
    Resolves the Crown-Pinion-to-ring radius mismatch (§1.1.3.3). Both
    mesh-verified fully watertight. `nacelle_nozzle_idler.scad`'s render
    selector changed from comment-toggle to a `RENDER_PART` `-D` string
    param ("gear" | "bracket"), matching the wings' `RENDER_SIDE` convention,
    and wired into the Makefile.
- [x] **Rebuild petals using the BamJr variable nozzle [REF-CAD-001] as a guide,
    using the gear train already developed** *(done 2026-07-04)* — the Rev R2
    redesign in `nacelle_nozzle_iris.scad` already implements the smooth conical
    exit (8 overlapping tangential-hinge flaps driven by the 72T unison ring gear
    via a spiral face-cam, reusing the Crown-Pinion→idler→ring train unchanged).
    This pass: (1) cited the BamJr "Variable-area EDF nozzle" reference
    (Thingiverse Thing 2991269, CC BY 4.0) — added to `REFERENCES.md` as
    **REF-CAD-001** and cited in the iris SCAD header, replacing the placeholder
    `[REF xxx]`; (2) numerically verified the 75 %/105 % kinematics
    (exit_r = R_HINGE − FLAP_LENGTH·sin φ → φ_closed = 25.94° at 18.75 mm = 75 %
    bore, φ_open = 3.58° at 26.25 mm = 105 % bore); (3) added a `RENDER_PART`
    (`throat` | `ring` | `flap` | `asm`) selector and Makefile rules, and rendered
    the print-ready **`nacelle_nozzle_throat.stl`**, **`nacelle_nozzle_ring.stl`**,
    **`nacelle_nozzle_flap.stl`** — all mesh-verified fully watertight (1 body
    each); (4) archived the superseded flat blender petal
    `nacelle_nozzle_petal.stl`.  *(Piano-wire loose end RECONCILED to Rev S
    2026-07-04: removed the retired 0.8 mm iris link-ring everywhere active —
    `bom_revS.csv` `PIANO-WIRE-0.8` dropped and replaced by `PIN-3X18` (3×18 mm
    tangential hinge, ×16) + new `PIN-2X4` (2×4 mm spiral-cam follower, ×16);
    `PRINT-NACELLE-PETAL`→`PRINT-NACELLE-FLAP`, `PRINT-NACELLE-RING` updated to the
    72T unison ring gear, and `PRINT-NACELLE-THROAT` / `-IDLER` / `-IDLER-BKT` added;
    Crown-Pinion note updated; `gen_piano_wire_ring` + its placeholder STL +
    `serenity_placeholders_assembly.py` entry + `PROJECT_INDEX` line + the
    `components_overview.svg` / `build_guide_08_nozzle_gear.svg` / `serenity-rev-r.jsx`
    strings all updated to the Rev S spiral-cam drive.)*

##### 1.1.3.2 *Tilt Gear Train*

    **Rev S gear train (OpenSCAD — all 5 parts, M=1.0; carried fwd from Rev O):**

- [x] **nacelle_sector_gear.stl** — `openscad -o ... serenity/stl/nacelle_sector_gear.scad`
    *(rendered 2026-06-22)* — Rev R1.1: R=22mm, **58T, ≈151.3° arc** (was
    38T/≈99.1°, grown to cover the widened -5°/140° mechanical tilt range);
    fixed to tilt bracket. Mesh-verified fully watertight.
- [x] **nacelle_pinion.stl** — spec: N=12T, D-bore shaft (×4 total: drive
    pinion + crown pinion per nacelle, identical part). 2026-06-22 change
    was comment-only (Stage 3 ratio/mating-interface text); re-rendered to a
    scratch file and diffed vertex-for-vertex against the published STL —
    confirmed byte-identical geometry, so the published STL was left as-is.
- [x] **nacelle_bevel_pair.stl** — `openscad -o airframe/stls/nacelles/nozzles/nacelle_bevel_pair.stl airframe/openscad/nacelles/nacelle_bevel_pair.scad`
    *(re-rendered 2026-07-04)* — Spec: N=14T, 45° pitch cone, 1:1, 90° axis
    redirect. No spec change; the published STL (2026-06-09) predated the
    2026-06-11 SCAD edit, so it was re-rendered from current source. Mesh-verified
    fully watertight (1 body, winding-consistent).
- [x] **nacelle_bevel_housing.stl** — `openscad -o airframe/stls/nacelles/nozzles/nacelle_bevel_housing.stl airframe/openscad/nacelles/nacelle_bevel_housing.scad`
    *(re-rendered 2026-07-04)* — Spec: CF-PETG, 24×14×20 mm housing block. No spec
    change; re-rendered from current source (same stale-STL reason as the pair).
    Mesh-verified watertight (4 separate solids — housing block + bearing bosses —
    all winding-consistent).

##### 1.1.3.3 *FreeCAD Hull-Frame Placement (gear train, nozzle, sleeves)*

- [x] **Map all nacelle-internal mechanism components to hull frame for both port
    and stbd, in `airframe/FreeCAD-scripts/serenity_assembly.py`** *(done, 2026-06-21)*
    — added `R_BAKE` / `T_BAKE` / `PYLON_SIDE` constants and a `nacelle_rows()`
    composition helper (`T_hull = T_nacelle_bake ∘ T_subcomponent_local`, derived
    by hand-expanding the shared nacelle bake quaternion); placed via
    `transform_mesh()` (VERIFY tier, not `place_mesh()`) for both sides:
    Stator Sleeve, Aft Spider Sleeve, Drive Pinion A, Crown Pinion, Bevel
    Housing, Bevel Pair, Sector Gear, Nozzle Iris, and Tip Cap.
- [x] **Fix `crown_pinion_boss()` in `nacelle_pod_50mm_tandem.scad`** *(fixed
    2026-06-22)* — it copied `pinion_a_boss()`'s `rotate([0,90,0])` X-axis-bore
    pattern verbatim, but both `nacelle_pinion.scad` and
    `nacelle_bevel_housing.scad` independently document the Crown Pinion as
    Z-axis/longitudinal (no rotation). Removed the rotation; `cylinder()`'s
    default Z-axis extrusion is now the boss's bore axis, matching the
    FreeCAD placement (which already used the documented-correct identity
    rotation) and both other files' documentation.
- [x] **Resolve the unresolved Crown-Pinion-to-rack mesh radius in
    `nacelle_nozzle_iris.scad`** *(resolved 2026-06-22)* — an author
    scratch-pad had computed four candidate radii (28/37/31/38 mm) and ended
    mid-thought ("Wait —") with none ever chosen. Root cause: the Crown
    Pinion's hull-frame Y-offset is fixed at 28 mm (shaft-conduit continuity
    through the bevel pair, shared with Pinion A), but the nozzle ring's
    required pitch radius (36 mm, sized for the petal/hinge geometry) is
    incompatible with a direct mesh at that offset. **Fix: added a compound
    idler gear stage** (`nacelle_nozzle_idler.scad`, new file) between the
    Crown Pinion and the nozzle ring — Idler-In (44T, R=22mm) meshes the
    Crown Pinion at the fixed 28.1 mm centre distance; Idler-Out (15T,
    R=7.5mm) meshes the new full-circle ring gear (72T, R=36mm) at a
    43.6 mm centre distance. A valid idler-shaft position exists per the
    triangle inequality (|28.1-43.6|=15.5mm ≤ 28mm ≤ 28.1+43.6=71.7mm).
    Also replaced the old partial rack with a full-circle ring gear,
    eliminating the arc-coverage sizing problem entirely. Also fixed a
    latent bug found during the rework: `LINK_HOLE_R` (28 mm) exceeded
    `PETAL_LENGTH` (18 mm) — the piano-wire link hole was off the physical
    end of the petal; corrected to `LINK_HOLE_R=16mm`, `PETAL_LENGTH=20mm`.
    Updated `nacelle_pinion.scad`'s Stage 3 ratio derivation and mating
    tables to match.
- [x] **Render updated/new gear-train STLs** *(done 2026-06-22, openscad +
    trimesh now available)* — `nacelle_nozzle_iris.scad`, `nacelle_sector_gear.scad`,
    and the new `nacelle_nozzle_idler.scad` (both parts) all rendered; see
    §1.1.3.1/§1.1.3.2 above.
- [x] **Mesh-verify the regenerated nacelle gear-train STLs** *(done
    2026-06-22)* — `nacelle_nozzle_idler.stl`, `nacelle_nozzle_idler_bracket.stl`,
    and `nacelle_sector_gear.stl` are all fully watertight (single connected
    solid each). `nacelle_nozzle_iris.stl` (assembly-preview render) has one
    non-manifold edge out of 26,381 from the petals' designed overlap —
    see §1.1.3.1 finding above; not a print-file defect.
- [x] **Idler angular position about the nozzle axis** *(resolved
    2026-06-22)* — solved the two simultaneous centre-distance constraints
    (28.1 mm from Crown Pinion at local (X=0, Y=PINION_A_Y=28); 43.6 mm
    from the nozzle/ring axis (0,0)): shaft position (X=+27.485, Y=33.846),
    i.e. 50.92° from the local +X axis (rounded to 50.9°). The other valid
    mirror solution is 129.08° at X=-27.485 — +X chosen arbitrarily (nothing
    else occupies that sector at this Z station). `IDLER_SLOT_ANG` in
    `nacelle_nozzle_iris.scad` updated to match; idler + bracket placed in
    `serenity_assembly.py` at this (X, Y).
- [x] **idler axial mesh-band mismatch — RESOLVED 2026-07-04** (user decision:
    offset the Crown Pinion, accounting for CG).  The idler's two gear sections
    are 10 mm apart axially (Idler-In band centre at local Z=6, Idler-Out at
    Z=16), but Crown Pinion and the Nozzle Ring both sat at the same station
    (`CROWN_Z = NOZZLE_RING_Z = 166.25`), 0 mm apart — unmeshable by one idler
    shaft.  **Fix:** decoupled the two and moved the Crown Pinion 10 mm toward the
    intake — `CROWN_Z = NOZZLE_RING_Z − 10 = 156.25` (`nacelle_pod_50mm_tandem.scad`)
    — so the targets are now 10 mm apart, matching the idler band spacing.  The
    idler + bracket are placed in `serenity_assembly.py` at `Z = CROWN_Z − 6` (real
    Z, no longer a placeholder), so Idler-In meshes the Crown plane and Idler-Out
    the Ring plane; the nozzle placement now uses `NOZZLE_RING_Z` (unchanged).
    **CG re-derived** for the FULL rotating assembly (gear train + nozzle
    ring/petals/idler included, WS2812B LED rings removed, aft cowl not
    double-counted): CG_Z = 104.5 mm, so `PIVOT_Z` moved 103.75 → 104.5 mm (a
    negligible +0.75 mm) — the nacelle still pivots about its CG, per the user
    requirement.  See the pod header mass breakdown and `nacelle_nozzle_idler.scad`
    header.
- [x] **CG RE-DERIVED for Rev T (pushrod/cam drive + rotating 8 mm spar),
    2026-07-19 — SUPERSEDES the 104.5 mm figure above.** Deleting the gear train
    alone left the pivot ~unchanged, but the Rev T2 40 mm flaps (CG ~198 mm), the
    discrete Ø71 throat+housing (~175 mm), the cam-only ring, and the ~19 g steel
    spar (on the pivot) net-move the rotating CG to **CG_Z = 111.5 mm** (mass
    393.4 g / 0.867 lbm).  `PIVOT_Z` propagated 104.5 → 111.5 across the pod SCAD
    (header mass table + value), `edf_stator_sleeve.scad` (`SPAR_TUNNEL_Z_L`
    14.5 → 21.5), `serenity_assembly.py`, `_export_pivot_slab.scad`,
    `port_tilt_spar_assembly.scad`, `tools/bake_hull_frame.py`, and
    `docs/TILT_SPAR_ANALYSIS.md`.  Nacelle shells + stator sleeve re-rendered and
    re-baked (66 STLs pass `validate_stls.py`); spar hub/bore verified at Z=111.5.
    FIRST-PASS (band ≈109–112 mm) — see root `TODO.md` §1.1.3 for the open VERIFY
    items (sliced-mass density check, single-straight-spar re-solve for the +7 mm
    move, stator teardrop-strut aero, and the Ø72-pocket aft-cowl-tail decision).
- [x] **Stator spar-crossing rework (Rev T2, 2026-07-19).** Pivot at 111.5 lands
    mid-stator; kept **11 vanes** (coprime with the 12-blade EDF rotor — Tyler–
    Sofrin resonance cut-off; 12 would resonate, 13 changes thrust) and carried
    the spar across in a **streamlined teardrop strut** (round nose over the bore,
    boat-tail swept aft, TE ≈ vane-TE plane so the vanes keep the last straightening
    word into EDF2) replacing the blunt Ø13 tube.  Drilled the spar bore through
    the 0° anti-rotation key that was plugging the hole.  Aero is first-pass —
    VERIFY strut chord/tail + residual EDF2 swirl by CFD/bench.
- [x] **Confirm Sector Gear standoff distance from the nacelle face**
    *(resolved 2026-06-22)* — a tilt-bracket SCAD source DOES exist
    (`airframe/openscad/wings/wing_nacelle_pylon_revo.scad`, not found in
    the previous search), which bolts the sector gear to the pylon face at
    `PYLON_X0 = NACELLE_OD_X/2 = 30.25 mm` using that file's own simplified
    synthetic-ellipse `NACELLE_OD_X = 60.5 mm`. `serenity_assembly.py`'s
    `NACELLE_FACE_X_PYLON = 34.0 mm` instead matches
    `nacelle_pod_50mm_tandem.scad`'s own constant of the same name, which
    that file documents as "taken from the actual nacelle STL measurements
    rather than the synthetic-ellipse `NACELLE_OD_X`/2" — i.e. 34.0 mm is
    the validated, measured standoff already in use; it was not a guess.
    **Follow-up (new, not done here):** reconcile the pylon file's 30.25 mm
    ellipse approximation to the nacelle's measured 34.0 mm in a future
    pylon-model pass — out of scope for this nozzle/gear-train fix.
- [x] **`nacelle_tip_cap_port/stbd.stl` — ARCHIVED 2026-06-22**, per user
    instruction ("legacy part, no longer needed"). STLs moved to
    `airframe/archive/stls/nacelles/` (see `ARCHIVE_INDEX.md`); placement
    code and the now-unused `NACELLE_FACE_X_FAR` constant removed from
    `serenity_assembly.py`; references removed from
    `airframe/blender-scripts/serenity_render_views.py`,
    `docs/PHASED_BUILD_GUIDE.md`, and `PROJECT_INDEX.md`. Note for the
    record: `PHASED_BUILD_GUIDE.md`'s now-removed rows described this part
    as housing the RED/GREEN nav-light recess (port/stbd) — if nav-light
    mounting is still needed, it isn't currently assigned to any other
    component; flagging in case that function still needs a home.
    `current-specification/LICENSE_AND_ATTRIBUTION.md` also references this
    part in an already-stale (pre-Rev-R1 naming) file-tree snapshot — not
    touched here, pre-existing staleness unrelated to this archival.
- [x] **`cargo_sect_shell24.scad`'s port/stbd mirroring used the wrong axis
    — FIXED 2026-06-22** (adjudicated against CLAUDE.md's hull-frame
    standard, per explicit user direction). Rendered and mesh-verified after
    the fix: `openscad --hardwarnings cargo_sect_shell24.scad` compiles
    clean (no warnings), output fully watertight (14 connected solids, 0
    bad) — bounds X −204.0..−7.4, Y −415.6..−211.3, Z 0.0..163.2 mm, matching
    the file's own documented STL bounding box. Root cause confirmed: the wing
    subsystem (`wing_root_mortise()`, `wing_spar_bore()`,
    `spar_bearing_block()`, `nacelle_servo_mount_block()`) had been modelled
    using the WING's own internal pre-permutation convention
    (`wings_s1223_revo.scad`: "X: chordwise, Y: thickness, Z: spanwise")
    without ever applying that file's own `X<-Z, Y<-X, Z<-Y` permutation to
    hull-aligned axes before use here — i.e. an un-translated foreign
    coordinate system, exactly what CLAUDE.md's hull-frame standard exists
    to prevent. Added `CARGO_X_WALL_PORT`/`CARGO_X_WALL_STBD` (measured
    lateral wall positions, mapped through this file's own validated bake
    transform: `local_X=-201.5 -> hull_X=-72.9` PORT, `local_X=-7.4 ->
    hull_X=-267.0` STBD) and `WING_ROOT_Z_CEN=62.5` (fixed root height for
    both sides, from CLAUDE.md's validated baked Wing_Port/Wing_Stbd Z
    extent +48..+77 mm); re-derived all four modules to mirror across X
    with this fixed Z. Bonus fix: `wing_spar_bore()` now runs the full
    lateral span through BOTH walls (a real continuous tip-to-tip spar
    passage) — previously it was a short Z-axis bore that never reached the
    far wall at all, so the two wings were never actually structurally
    connected by a shared spar.
    **Two items deliberately left open by this fix, not resolved:**
    - The spar/mortise chordwise (Y) offset still uses the pre-existing
    `WING_ROOT_Y_CEN` value as an interim stand-in; the true offset needs
    re-deriving against the current 129 mm Rev R1 root chord (already
    tracked: TODO.md §1.1.2 "Verify cargo-section wing-root mortise
    dimensions against new root chord 129 mm").
    - **NEW, more serious — `WING_ROOT_Z_CEN`=62.5 mm overlaps River's
    avionics bay (Z 24..64 mm)**: the spar bearing boss alone (Z
    51.5..73.5) already overlaps River's upper 51.5..64 mm band. This is
    a real structural/packaging conflict, independent of the axis bug —
    it was masked before only because the old (wrong) code happened to
    place the wing hardware at the gondola's Z extremes, nowhere near
    Z=24..64. `nacelle_servo_mount_block()`'s own Z-placement
    (`NSVMT_Z_OFFSET`, +30.5 mm from `WING_ROOT_Z_CEN`) was chosen only to
    clear the wing mortise/spar boss with the same 4 mm margin the
    original code used, and was NOT checked against River's bay — it may
    also land inside or near it. **Needs a structural/packaging decision
    (move River's bay? reduce its footprint? confirm the wing spar's
    actual swept volume doesn't reach the Faraday tray?) before any of
    this geometry is considered final — not resolved here.**
    `nacelle_servo_bracket.stl` still does not exist in `airframe/stls/`
    (only the SCAD source has been authored); render it once the Z-conflict
    above is resolved.

- [ ] **[OPEN — DESIGN] Nozzle drive protrudes ~10 mm past the nacelle OD**
    *(flagged 2026-07-07, design review)* — the compound idler shaft sits at R43.6 mm
    and its Idler-Out teeth reach R≈51 mm, ~10 mm proud of the Ø82 nozzle housing /
    nacelle OD (the "steampunk accessory"). Root cause: the external 72T ring gear
    forces the idler *outside* it, and the 17.6:1 reduction is inflated because the
    front sector/pinion stage first multiplies tilt ×4.67 then divides ×17.6.
    **Trade study authored** (`docs/NOZZLE_DRIVE_TRADE.md`,
    `docs/img/nozzle_drive_trade.png`) comparing two zero-protrusion redesigns:
    - **A — internal ring gear, re-architected reduction**: teeth on the ring bore,
        single ~13T drive pinion inside Ø82, idler deleted, front stage re-ratioed
        ~1.5×. Keeps positive gears + linear tilt→dia map. ~6 parts.
    - **B — pushrod/bellcrank linkage**: deletes the entire aft train (sector, bevel,
        shaft, crown, idler, ring gear); fixed pivot crank → pushrod → ring lever.
        ~4 parts, nonlinear map, FDM-friendly; departs from the canonical "gear
        train" wording (would need a `CLAUDE.md` spec edit).
    **User chose (2026-07-07): prototype BOTH and compare** — kinematic prototypes +
    trade table done. **AWAITING production-CAD decision** (A or B) before rebuilding
    `nacelle_nozzle_iris.scad`, `nacelle_sector_gear.scad`, removing
    `nacelle_nozzle_idler*`, and updating `serenity_assembly.py` + the ratio/BOM.

##### 1.1.3.4 *Nacelle Intake*

- [x] **Trim the intake bell to the canonical leading nacelle dome** *(done
    2026-07-04)* — the additive `inlet_bell` protruded well past the slender
    canonical dome (bell outer r ≈ 30.5 mm at Z=0 vs the ogive nose r ≈ 21 mm at
    the tip). Because the imported nacelle shell is a SOLID body (54 % bbox fill,
    airflow carved by subtraction), it was replaced with a SUBTRACTIVE cosine
    `inlet_bellmouth()` carved into the dome: r_cut(z) flares from 25 mm (aft) to
    28 mm (front) and, since it decreases monotonically in z while the dome radius
    increases, crosses the dome exactly once — so the nose forward of that crossover
    (the thin tip, thinner than the 50 mm EDF anyway) is removed and the LEADING
    EDGE = the canonical dome ∩ cosine intake, exactly as specified. Re-rendered +
    baked both nacelles; the trimmed nose shifted the baked Y extent by ≈5.8 mm
    (Port −64→−58.2, Stbd −70→−64.2 — CLAUDE.md extent tables updated). Both
    watertight. **VERIFY the exact crossover station in FreeCAD** against the
    canonical mould line.

##### 1.1.3.5 *Nacelle Lighting*

- [x] **Move the port (red) / stbd (green) nav lights INWARD→OUTWARD face** *(done
    2026-07-04)* — a red (port) / green (starboard) position light must radiate to
    its own side [REF-FAA-003 §91.209(a)]; on the inboard face the pylon/fuselage
    occludes the required outboard arc. Added `nav_light_pocket()` — a flush
    WS2812C-2020 recess cut INTO the OUTBOARD nacelle face (interior modification,
    does not protrude) + a short through-wall wire bore. Header/usage comments and
    REF-FAA-003's citation index updated. Both nacelles re-rendered + baked,
    watertight. `NAV_LIGHT_Z = 70 mm` is a VERIFY/fine-tune-in-FreeCAD station.
- [x] **Route nav-light wires through an internal cableway (not protruding)** *(done
    2026-07-04)* — removed the old EXTERNAL protruding D-section `nav_wire_conduit`;
    added `nav_wire_channel()`, an INTERNAL rib bonded to the inside of the outboard
    skin with an OPEN snap-in U-groove (no trapped/enclosed void — prints cleanly and
    is field-serviceable), running from the emitter down to the existing
    `harness_exit_port()` where the wire joins the ESC/harness bundle to the pylon
    (reuses the EDF cableway). Never breaks the exterior mould line.
- [x] **Remove the exhaust WS2812B LED rings + harnesses from the design completely**
    *(done 2026-07-04)* — all 3 (2 nacelle + 1 rear) removed across every ACTIVE
    file: `current-specification/bom_revS.csv`, `README.md`, `docs/POWER_DISTRIBUTION.md`
    (5 V subtotal 13 650→13 410 mA nom / 27 310→26 710 peak; load-shed table
    renumbered), `serenity-rev-r.jsx`, the placeholder generator + assembly + the
    `WS2812B_ring_50mm.stl` asset (deleted), both blender generators, `PROJECT_INDEX.md`,
    `components_overview.svg`, `deferred/aft-edf/README.md`, and the TODO BOM/build
    rows above. Historical revision snapshots (`bom_revP/Q/R.json`, `REVN_BUILD_GUIDE`)
    left intact per the revision-snapshot policy. The WS2812C nav lights (distinct
    part) are retained.

##### 1.1.3.6 *Tilt-Angle Feedback — Hall Sensor at the Wing/Nacelle Joint*

Closes the tilt-servo loop on the **true nacelle angle** (output side) so it is
independent of tilt-spar torsional wind-up (docs/TILT_SPAR_ANALYSIS.md §1, §3.5).
Off-axis topology (the spar is a through-shaft — no free end): a Ø22 diametric
ring magnet on the rotating nacelle hub read by an off-axis IC (**Magntek MT6701**,
I²C; **MA732**/SPI fallback) on the fixed wing-tip pad. Avionics/firmware side is
tracked in `avionics/WBS.md` §1.9.1 and `avionics/emi-hardening/WBS.md` §1.4.6.

- [x] **Wingtip bearing downsized F688ZZ → MF128ZZ** *(Rev R2d, 2026-07-19)* — the
    Ø16 F688ZZ seat radius (7.975 mm) exceeded the S1223 tip half-thickness
    (7.80 mm) and cut ~0.21 mm through **both** airfoil skins. `TIP_BRG_*` now
    MF128ZZ (Ø12, flange Ø13.5): seat clears with **+1.79 mm** margin (echo-verified).
    Reaction ≈19 N (dyn) ≪ MF128 capacity. Root bearing stays F688ZZ. BOM split.
- [x] **Wing (fixed sensor) mount modelled + relocated** *(Rev R2d)* — added
    `wing_tip_hall_sensor_pocket()` (MT6701 9×7 PCB recess + 2× M2 non-ferrous
    pilots) with the IC **relocated to HALL_SENS_R = 12 mm** (chordwise-aft, clear
    of the Ø13.5 flange keep-out — the initial R = 6 mm pocket collided with the
    bearing seat/flange). Pad OD 26→**36** to host it. Echo: clears flange 0.75 mm,
    3.79 mm under top skin. Plus `hall_sensor_cableway()` (Ø3.5 I²C conduit at
    0.30c, forward of the EDF double-D; fixed lead — no slip ring). Wired into
    `wing_one_side()`; compiles clean.
- [x] **EDF double-D drilled through the root tenon** *(Rev R2d)* — `cableway_bore()`
    root end extended Z −1 → −13 so the Ø7 EDF feeds pass through the
    `fuselage_root_tab` (was dead-ended 1 mm in). Soundness echo-verified: bores
    groove only the tenon crown; solid **15.4 mm lower spine** retained.
- [x] **Nacelle (rotating magnet) hub modelled** *(Rev R2d)* — `nacelle_hall_ring_hub()`
    (non-ferrous CF-PETG carrier, OD 24 for the Ø22 ring — Rev R2e ring downsize, keyed
    to the spar, ring ID ≥1 mm off the ferrous spar) in `_export_pivot_slab.scad`
    (dev sandbox).
- [x] **Tilt-encoder sensor SELECTED (AKM AK7455) + ENC-NACELLE-1 KiCad rebuilt**
    *(Rev S, 2026-07-19; drafted by Claude Opus 4.8)* — `avionics/kicad/ENC-NACELLE-1.md`
    and `.kicad_sch` were the Rev Q **AS5600 on-axis** design (magnet on a shaft tip,
    15×15 mm, JST-GH), invalid under the through-shaft spar. Datasheet-driven sensor
    down-select (user-supplied datasheets): **MT6701 REJECTED** — its datasheet (Rev 1.9
    §6) confirms **on-axis only** (Ø6 mm cyl magnet, off-axis misalignment ≤ 0.3 mm), so
    it cannot read the off-axis ring at R ≈ 11 mm — the same failure as the AS5600;
    **AS5200L** (on-axis I²C) likewise rejected. **SELECTED = AKM AK7455**
    (REF-SENSOR-008): datasheet 200800064-E-00 explicitly supports the **Off-Axis
    (side-of-shaft)** configuration and adds **anomaly-magnetic-field detection + dynamic
    error reduction + EEPROM INL calibration** — purpose-built for the ferromagnetic
    (4130/17-4) through-shaft. Both KiCad files rebuilt around the AK7455
    (`SKIPPER-TILT-ENC-PCB`, **QFN24 4×4**, **SPI** 4-wire + ERROR on a **7-wire** direct-
    solder pigtail; both nacelles share the SPI bus via separate **CSN** → the I²C
    fixed-address problem is gone). Pinout **verified** vs the datasheet (TEST2→VSS,
    TEST1 open, NC pins + back-tab/EP open); `kicad-cli` (9.0.2) ERC **0 errors**.
    `bom_revS.csv` (`SKIPPER-TILT-ENC-PCB` + `HALL-RING-MAG`) and `REFERENCES.md`
    (REF-SENSOR-008 + pending row) updated. (A KiCad symbol Y-inversion wiring bug —
    library Y-up vs sheet Y-down — was found and fixed during the rebuild.)
- [ ] **[OPEN — cross-subsystem, rescoped 2026-07-26] `Pilot.md` §13 / `Pilot.kicad_sch` still
    have a `J_ENC` connector row (SM04B-GHS-TB, `ENC_SDA`/`ENC_SCL`, "AS5600 nacelle tilt angle
    encoder (I2C)")** — this is now **obsolete, not merely stale**: the architecture moved to
    AK7455 read locally in-nacelle by a `CAN-PERIPH-GW-1` trust-module gateway (own
    MSPM0G3507, SPI 4-wire + ERROR direct to the gateway MCU), published as a signed message on
    isolated CAN-FD + isolated RS-485. River (primary) and Simon (failover) subscribe to the
    bus message rather than Pilot owning a dedicated I²C/SPI bus to each nacelle. **Action:**
    remove the `J_ENC` connector + `ENC_SDA`/`ENC_SCL` net from `Pilot.kicad_sch` and the §13
    table row (not a SPI reconciliation — the connector's function no longer belongs on Pilot at
    all). See `avionics/WBS.md` §1.9.1/§1.9.2 and
    `avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md` deployment mode 1.
- [ ] **[OPEN — airframe] Resize the wing sensor pocket for the AK7455 QFN24 4×4**
    (was sized for the MT6701 3×3) and route the **7-wire SPI** pigtail — update the
    `HALL_*` block + comments in `wings_s1223_revo.scad` (they still name MT6701) and
    `_export_pivot_slab.scad`, then re-bake.
- [ ] **VERIFY `INBOARD_FACE_X` sign** in `_export_pivot_slab.scad` (which X face
    of the port nacelle is the wing side).
- [ ] **Migrate `nacelle_hall_ring_hub()` into `nacelle_pod_50mm_tandem.scad`** with
    the keyed spar hub (retire the sandbox preview); re-bake port/stbd shells.
- [ ] **AK7455 off-axis bench validation** — confirm the ring presents **10–70 mT** at
    the IC (magnetisation diametric vs radial + gap/offset), run the **EEPROM INL
    calibration** over −5..90° (AKM app support; monotonic angle), set the sense plane
    (`R_FIELDSEL`), and confirm the **ERROR** pin drive (push-pull vs open-drain, add a
    node pull-up if open-drain). REFERENCES.md REF-SENSOR-008 / TODO §0.8; EMI WBS §1.4.6.

