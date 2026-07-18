# Serenity UAV — Airframe Wings and Nacelles Work Breakdown Structure (Detail)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Current design revision:** Rev S (2026-07-04)

> **Detail-holder for the root WBS.** The repository-root [`TODO.md`](../../TODO.md)
> is a compact index — headings, subheadings, and short (<=70-char) checkbox items
> only, per root `CLAUDE.md`. This file carries the full task detail for the WBS
> branches the root indexes below. Close an item here first, then check it off in
> the root index as a commit prerequisite (root `CLAUDE.md` "Revisions and Version
> Control").

*"Curse your sudden but inevitable betrayal."*

---

## §1.1.2 — Wings
*(root `WBS.md` §1.1.2)*


**Wing pylon (OpenSCAD — Rev S integrated design; carried fwd from Rev O):**

- [ ] **wing_nacelle_pylon_revo.stl** — `openscad -o ... serenity/stl/wing_nacelle_pylon_revo.scad`
    - Verify WING_SLOT_W and WING_SLOT_H against tip chord 93 mm (Rev R1 planform) before printing — pocket 50×40 mm uses 54 % of tip chord; confirm pylon block clears airfoil walls
    - Verify WING_BOLT_R (16 mm) does not exceed S1223 half-thickness at 50 % tip chord (≈ 9.6 mm above chord line at 93 mm chord); reduce to ≤ 12 mm if pylon block geometry requires it
- [ ] **wings_s1223_revo.stl** — Rev R1 planform (2026-06-14): root 129 mm, tip 93 mm, zero LE sweep; STLs regenerated and baked ✓
    - **[OPEN]** Verify cargo-section wing-root mortise dimensions against new root chord 129 mm (was 161 mm); `cargo_sect_shell24.scad` mortise slot (currently 30.8×20.8×15 mm) may need resizing and re-centring
    - **[OPEN]** Re-check root-tab centre position: with 129 mm chord the tab centres at hull Y ≈ +57.5 mm (was +73.5 mm); confirm mortise centre in cargo SCAD matches
    - **[OPEN]** Verify wing TE position (hull Y≈+122 mm port, +117 mm stbd) clears cargo-section aft interior features; cargo aft boundary is hull Y≈+132 mm — 10 mm clearance

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
- [ ] **[OPEN — BLOCKER] Fuselage spar-interface now mismatched.** §1.1.1.3 cuts the
    cargo-shell mating Ø12.3 spar bore + Ø22 bearing bosses at the **old** 30 %-chord
    line (hull **Y ≈ +31.7, Z ≈ 62.5**). The Rev R1a wing spar now sits at the 22 mm
    station on the camber midline → root ≈ hull **Y ≈ +15, Z ≈ +71** (~16 mm fwd,
    ~8 mm up). The spar can no longer pass through both parts. **User decision
    required:** (a) relocate the cargo-shell bore + bosses to the new spar line
    (cargo-shell / Blender-canonical change + re-merge + re-bake), or (b) keep the
    fuselage bore and instead thicken the tip further (~1.6×) so a straight spar at
    the 38.7 mm station fits — fatter wingtip OML. **Do not print either wing or
    cargo shell until reconciled.** Consider whether `THICKNESS_SCALE_TIP` /
    `SPAR_BORE_STATION` should be canon-checked against the Serenity wing silhouette.


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

