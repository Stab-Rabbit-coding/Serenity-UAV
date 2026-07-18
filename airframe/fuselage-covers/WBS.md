# Serenity UAV — Airframe Fuselage — Access Covers, Antenna Mounts, Nacelle Bracket Work Breakdown Structure (Detail)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Current design revision:** Rev S (2026-07-04)

> **Detail-holder for the root WBS.** The repository-root [`TODO.md`](../../TODO.md)
> is a compact index — headings, subheadings, and short (<=70-char) checkbox items
> only, per root `CLAUDE.md`. This file carries the full task detail for the WBS
> branches the root indexes below. Close an item here first, then check it off in
> the root index as a commit prerequisite (root `CLAUDE.md` "Revisions and Version
> Control").

*"Love keeps her in the air. — Capt. Malcolm Reynolds"*

---

## §1.1.1 — Fuselage: Access Covers, Antenna Mounts, Nacelle Bracket (part 2/3)
*(root `WBS.md` §1.1.1)*

    = 2-loop tube). Watertight, single body, 0 boundary (vol 336 k mm³ — up from the old 273 k
    because the old cutter was OVER-removing via the bite plus a deep −55 notch). Assembly
    re-runs 0 WARN/MISSING/error. **Head/middle already used `_bore_open_cutter`** (their joints
    use the clean method too); **rear is now clean too** — regenerated 2026-07-06 via
    `regen_rear_interior.py` with the same lofted bore-open cutter (MESH-01 rear RESOLVED). *The original finding, for the record:* A starboard-side
    silhouette of the published cargo fab mesh shows **uneven fwd (Y=−71.5) and aft (Y=+132)
    joint rims** and a **notched "cutout" in the dorsal skin just aft of the fwd joint
    (Y≈−60..−50, Z≈140..160)**. Confirmed these are **cutter artifacts, NOT intentional**, by
    ray-cast silhouette comparison against the clean baked Blender source (which has smooth,
    clean joint edges and no dorsal notch). Root cause: `merge_cargo_interior.py`
    `open_face_plug()` opens each mating face by extruding a SINGLE inner-cavity cross-section
    (8 mm inboard, `OPEN_STATION_OFF`) over a 27 mm Y span (`OPEN_PAST`=3 → `OPEN_DEPTH`=16)
    with a +0.5 mm outset — the constant section does not track the tapering/curving fwd hull,
    so it leaves ragged wall fragments at the rim and clips through the dorsal skin at the fwd
    end (the "top cutout"). The mesh stays watertight (the boolean re-closes around the
    over-cut), so it passed the watertight gate. **The OPENING is intended** (CLAUDE.md: mating
    faces left open for assembly + cable routing; splice collars bond across them) — only the
    ragged EXECUTION is wrong. **Intentional features in the same view (do NOT touch):** wing
    spar bore (Ø12.3 @ Y≈+32,Z≈62), wing root mortise (Y≈42..73,Z≈52..73), belly clamshell
    aperture (Z≈0..9). **FIX (needs design input):** replace the constant-section extrude with
    a clean planar cut at each mating station (flat-rimmed open tube); requires confirming the
    exact mating-plane Y per joint given the source shells' rounded end-closures (fwd section
    near-closes by Y≈−71.5; a clean full-perimeter rim wants the cut ~Y=−64 ≈ 7 mm shorter, OR
    an accepted tapered rim at −71.5). Same fix applies to `add_structural_features.py`
    `_bore_open_cutter` (head/middle/rear). **Refer mating-plane choice to user before rework.**
- [ ] **MESH-01 `add_structural_features.py` boolean cuts left non-watertight / fragmented
    shells on cargo, middle, and rear** *(found 2026-06-16, reviewing 03_top.png render)* —
    **ROOT CAUSE FIXED IN CODE. RESOLVED FOR CARGO 2026-06-30. RESOLVED FOR MIDDLE
    2026-07-03. REAR RESOLVED 2026-07-06 (new `regen_rear_interior.py`; see the
    "Rear" note below — its root cause was the bake's float32 STL round-trip
    damaging the delicate 3-body rear source, not a source-mesh defect).**
    - **2026-07-06 REGEN + HULL AUDIT (this session).** Head, cargo, and middle
        regenerated from the clean Blender sources with the joint boss-pins REMOVED
        (splice collars supersede — see §1.1.0 note above) and independently
        re-verified with trimesh: **HEAD** watertight, 0 boundary, 0 non-manifold, 1
        body, vol 186 757 mm³; **MIDDLE** watertight, 0 boundary, 0 non-manifold, 2
        bodies (outer horseshoe + inner neck, both closed — expected), vol 232 327
        mm³; **CARGO** in-memory PASS (watertight, 0 boundary, 0 non-manifold, 1 body,
        vol 273 170 mm³) — on reload the exported STL shows ~57 non-manifold edges but
        **0 boundary edges** (closed surface; benign float32-quantization artifact that
        slicers weld; a nondegenerate-strip was tried and REVERTED because it opens ~120
        real holes on cargo's shared T-junction slivers). **Hull-breach audit: 0 boundary
        edges on all four shells** (no unintended skin openings). **Hollow audit: ≥2
        concentric wall loops at every mid-station** (outer + inner 2 mm wall present).
        All three carry the HULL-FRAME R1 marker; `serenity_assembly.py` re-run clean
        (0 WARN/MISSING/error) with all 3 splice collars present. **REAR now also
        regenerated + clean (2026-07-06, `regen_rear_interior.py`): watertight, single
        body, 0 boundary, 246 769 mm³, clean fwd mating rim — see the Rear note below.**
    Original root cause was NOT (only) the cutter-vs-wall
    epsilon grazing but the fragile `_subtract_all` loop: it subtracted cutters one at a
    time via `trimesh.boolean.difference(engine="manifold")` with a per-step repair on a
    1.4 M-face shell, compounding degenerate slivers into 10⁴+ disconnected bodies.
    `_subtract_all` now unions ALL cutters into one Manifold and does a SINGLE
    `shell − union` (boolean of closed manifolds is closed by construction → guaranteed
    watertight out), plus a post-boolean `nondegenerate_faces()` / unreferenced-vertex
    cleanup pass added 2026-07-03 to strip the 1-2 zero-area triangles the manifold3d→
    float32-STL round trip was otherwise leaving behind. **Cargo** is fully resolved by
    `merge_cargo_interior.py` using this approach (watertight=True, single body,
    vol 323 188 mm³ — see §1.1.1.0a).

    **Middle — RESOLVED 2026-07-03.**  Regenerated from the clean Blender source
    (`airframe/blender-scripts/files-hollowed-24in/middle_shell24_2mm_repaired.stl`),
    baked to hull frame with `tools/bake_hull_frame.py`, then run through the fixed
    `add_structural_features.py`.  Independently re-verified with trimesh directly
    (not just the script's own `verify()` gate): `airframe/stls/fuselage/
    middle_shell24_2mm_repaired.stl` is `is_watertight=True`, 0 boundary edges, 0
    non-manifold edges, **1 body**, vol = 232 230.71 mm³ (vs. 232 437 mm³ pre-cut —
    a 206 mm³ reduction from the 15 boss-pin/skid-rod/bore-open cutters, consistent with
    their small bore sizes).  `bake_hull_frame.py --check` confirms the file still carries
    the `HULL-FRAME R1` marker (the export path stamps it directly; no re-bake needed
    since only booleans, not a placement transform, were applied).

    **Rear — RESOLVED 2026-07-06 (`airframe/blender-scripts/regen_rear_interior.py`).**
    The 2026-07-03 diagnosis below (a "pre-damaged source" with 380 slivers / 550
    non-manifold edges / volume-inflating internal lobes) was itself an artifact:
    the canonical rear source, loaded `process=False` then `merge_vertices()`, is
    actually **watertight at the correct 247 239 mm³** — three connected bodies
    (main wall shell +302 k, plus two symmetric inside-out internal cavity shells
    −27.5 k each, netting to 247 k). manifold3d handles that merged mesh correctly
    (volume 247 239). The real culprit was the **bake step's float32 STL write at
    the rear's large hull-frame Y (≈+203..+384)**: it splits coincident vertices
    just enough that the reloaded published STL no longer welds watertight, and
    manifold3d then mis-resolves it to ~357 k — so every subsequent cut was built
    on a wrong base. `regen_rear_interior.py` (rear analogue of
    `merge_cargo_interior.py`) fixes it by baking the clean source **in memory
    (float64)** and cutting before any float32 round-trip, then doing a single
    manifold3d boolean of the rear features (lofted bore-open fwd joint, keel
    channel, Y=+290 ring pocket, 2× skid-rod bores). Result: **watertight (0
    boundary edges), single body, 246 769 mm³ (~259 g)**, HULL-FRAME R1 marker,
    clean fwd mating rim (JOINT-01 lofted cutter — verified by starboard
    silhouette `scratchpad/rear_side.png`), assembly re-runs 0 WARN/MISSING/error.
    (~3 non-manifold edges remain on reload — a benign float32 artifact, 0
    boundary, same accepted state as cargo; slicers weld them.) *Superseded
    2026-07-03 diagnosis retained below for the record:*
    Different root cause than originally diagnosed, found
    2026-07-03: **the canonical Blender-source rear shell itself
    (`airframe/blender-scripts/files-hollowed-24in/rear_shell24_2mm_repaired.stl`) is
    pre-damaged, independent of any cutting.** Splitting the raw, un-cut, freshly-baked
    rear mesh into connected components gives 383 bodies: the real outer skin
    (999 938 faces), 2 real cavity/lobe surfaces (47 702 and 47 572 faces), and **380
    two-face zero-area degenerate slivers (760 faces total) that carry 550 non-manifold
    edges** — a defect baked into the Blender hollowing/export pipeline output, not
    introduced by `add_structural_features.py`. trimesh's divergence-theorem volume
    integral is robust to this and correctly reports 247 238.9 mm³ (matches the
    mass-budget figure) for the untouched source, but feeding the same mesh through
    `manifold3d`'s `Manifold` constructor (required by the fixed `_subtract_all`) silently
    mis-resolves the non-manifold edges and returns a `Manifold` whose own `.volume()` is
    357 242.6 mm³ — **before any cutter is even applied.** Every subsequent boolean
    subtraction is therefore built on an already-wrong 357 k mm³ base, which is why the
    exported result after cutting reads `vol=356 071 mm³, watertight(gate)=True` from the
    script's own in-memory check yet **fails independent re-verification**: reloading the
    exported STL with trimesh shows `boundary=3, bodies=2, watertight=False` (a small
    STL-roundtrip artifact on top of the larger volume-inflation defect).  A quick
    `nondegenerate_faces()` cleanup on the raw source removes the 380 slivers but then
    manifold3d returns **volume 0.0** for the whole mesh — i.e. cleanup alone does not fix
    it, it just changes failure mode.  **The rear published STL has been left at git HEAD
    (the pre-existing baked-but-unfeatured file, `is_watertight=False`/383 bodies, same as
    before this session) rather than overwritten with the new, more-broken cut result —
    no fabricated "PASS" is recorded.**  **REMAINING:** the rear Blender source mesh needs
    actual repair (removing/re-stitching the 380 degenerate slivers and their 550
    non-manifold edges) in Blender itself — a mesh-cleanup task upstream of
    `add_structural_features.py`, not a boolean-logic fix — before the feature-cutting
    pass can be re-attempted. Historical diagnosis below retained for the record.
    what looks like "huge cutouts / air where there should be hull" in the rendered build-guide
    images is **not** the intended bore-open joint design; it is a meshing defect from the
    boss-pin/keel-channel/ring-pocket boolean subtractions in `add_structural_features.py`.
    - `python3 airframe/blender-scripts/verify_shells.py --published` reports "ALL PASS" but
        its own per-shell output shows `watertight(strict)=False` for cargo, middle, and rear,
        and `large_shells=3` for rear (i.e. the rear shell is split into 3 disconnected solid
        islands, not one continuous hull) — the gate's pass criteria (`open_edges==0` and
        `large_shells<=3`) do not actually require `is_watertight`, so this slipped through.
    - Non-manifold edges (shared by 4–6 faces instead of 2) and hundreds of zero-area sliver
        fragments cluster exactly at the boss-pin/keel-channel/ring-pocket cut sites: cargo at
        Y ≈ −68..−58 mm (Joint 1) and Y ≈ 121–122 mm (Joint 2); rear at Y ≈ 217–233 mm
        (Joint 3 / skid-rod bore zone).  Head (boss-pin bores only, no keel/ring cuts) is fully
        clean — pointing at the keel-locating-channel and ring-frame-pocket box cutters
        (`KEEL_CHANNEL`, `RING_POCKETS` in `add_structural_features.py`) as the likely root
        cause: their cut surfaces sit within float-epsilon of the shell's existing 2 mm wall,
        producing degenerate/non-manifold triangulation in the `manifold3d` boolean difference.
    - Cargo's computed volume (6,234,838 mm³) is ~17× the §2 mass-budget figure
        (370,509 mm³) — a strong independent signal of broken topology, not just cosmetic noise.
    - **Fix path:** add finite clearance/overlap to the keel-channel and ring-pocket cutters
        so they fully traverse the wall instead of grazing it; re-run
        `add_structural_features.py`; tighten `verify_shells.py`'s gate to hard-fail on
        `is_watertight=False` and on `large_shells>1` (a clean single-piece shell should split
        into exactly 1 surface body, not be allowed up to 3).  Re-run `bake_hull_frame.py --check`
        after re-export.  **BLOCKS cargo/middle/rear printing and any FEA based on current STLs.**

- [x] **CF ring plate (CF-PLATE-2MM) — complete first-principles re-evaluation *(Rev R1)*** *(done 2026-06-14)*
    Full analysis in `docs/structural_analysis.md`.  2 rings selected (down from prior 5):
    cargo Y=+30 mm (wing-spar load zone) and rear Y=+290 mm (landing anti-ovalisation zone).
    Inner-profile CSVs exported to `airframe/diagrams/ring_frames/` for DXF cut file generation.
    See structural_analysis.md §3 for load case inventory and §5 for ring pocket dimensions.
    Ring-frame pockets cut into cargo and rear shells by `add_structural_features.py`.
    **SUB-TASKS:**
    - [x] **DONE 2026-07-03.** FreeCAD's headless interpreter (`freecadcmd`) was blocked by
        this session's sandbox permission hook and could not be invoked; an equivalent
        geometry pipeline (Shapely polygon offset/boolean + a hand-written DXF R12 writer)
        was used instead. Built the ring plate outer profile from each inner-skin CSV, added
        a 3 mm outward clearance offset, and cut the keel-bar notch. **Notch corrected to
        3.5 mm wide (X) × 6 mm deep (Z)**, centred at hull X = −170 mm — the "6 mm wide ×
        3 mm deep" figure previously here transposed the keel bar's own 3 mm(X) × 6 mm(Z)
        cross-section (structural_analysis.md §4.3/§4.5/§5.4 already specifies 3.5×6 mm;
        that figure is authoritative). Exported:
        - `airframe/diagrams/ring_frames/ring_rear_Y290_plate.dxf` — **FINAL.** Rear
          Y=+290mm cross-section is two clean concentric closed loops (outer + inner wall,
          2 mm apart); used the inner-wall loop. Net area 113.2 cm², bounds X[−236.3..−115.3]
          Z[24.5..146.2] mm. Verified by re-parsing the DXF's own vertex data and confirming
          the bounding box matches the pre-export polygon (round-trip OK).
        - `airframe/diagrams/ring_frames/ring_cargo_Y30_plate_PROVISIONAL.dxf` —
          **PROVISIONAL, NOT for fabrication.** The cargo Y=+30mm cross-section is
          fragmented into 4 disjoint closed loops (quadrant-like, not one/two continuous
          rings), consistent with the open `large_shells>1` / MESH-01 cargo-mesh defect
          tracked above. Rather than fabricate a smoothed single contour, this DXF uses the
          convex hull of the 4 main loops as a conservative placeholder envelope (net area
          242.9 cm², bounds X[−257.6..−81.1] Z[0.0..159.1] mm). **Must be re-extracted and
          re-cut once the cargo shell mesh is repaired — do not cut CF stock from this file.**
    - [x] **DONE 2026-07-03.** Updated `current-specification/bom_revR.csv` CF-PLATE-2MM
        Notes: 2 rings (cargo Y=+30mm, rear Y=+290mm); mass computed from actual DXF
        enclosed area × 2 mm × **1.6 g/cm³** (not the 1.54 g/cm³ previously cited here —
        1.54 has no other citation anywhere in this repository, while 1.6 g/cm³ is already the
        CF-plate density used in structural_analysis.md §5.6; superseding 1.54 with the
        repository-verified 1.6 figure). Rear (final): 36.2 g. Cargo (provisional): 77.7 g.
        Combined 113.9 g — supersedes the ~300 g bounding-rectangle/fill-factor estimate in
        structural_analysis.md §5.6. Revised prior count from 5 to 2.
    - [x] **DONE 2026-07-03.** Updated `REVN_BUILD_GUIDE_24IN.md` keel/ring-frame table and
        installation steps 1–2 with hull-Y ring stations (+30 mm, +290 mm), replacing the
        stale 91/165/251/320/388 mm values.

    All prior design data for CF ring plates (station count, hull-Y positions, 2D profiles,
    and structural function) were based on the **pre-Rev N non-canonical hull model** and
    are entirely invalid for the current baked canonical Serenity geometry.  This is a
    clean-sheet structural design task, not a re-derivation of old numbers.

    **Step 1 — Structural load case inventory.**
    Identify every load introduction point inside the hull that a ring frame could react:
    - Wing spar pin loads (X-axis spar through cargo section; derive spar-bore Y stations
        from `cargo_sect_shell24.scad` SPAR_BORE_Y / bearing block parameters).
    - Nacelle tilt servo reaction (NSVMT blocks in cargo section; derive Y from SCAD
        `NSVMT_X_CEN` or equivalent — note SCAD uses part-local frame; convert to hull Y).
    - Skid landing-impact loads (aft section; CF rod reinforcement already handles skid-arm
        bending; determine if tail-cone ovalisation under landing shock still warrants a ring).
    - Fuselage bending under 2g manoeuvre (keel bar + foam carry primary moment; rings
        provide shear-web anti-ovalisation — evaluate whether skin thickness + foam elastic
        foundation make rings unnecessary in lightly-loaded sections).

    **Step 2 — Hull cross-section survey at load stations.**
    For each load station identified in Step 1, slice the baked canonical STL at that
    hull-Y plane (FreeCAD Cross-Section on the baked mesh, or `python tools/bake_hull_frame.py`
    cross-section output).  Characterise the inner-skin boundary:
    - Is it a closed loop (full ring possible) or open (e.g., middle horseshoe open at −Z)?
    - What is the enclosed area and minimum inscribed rectangle?
    - Does the Serenity exterior geometry at that station allow a flat CF plate to seat
        flush against the inner skin, or is the section too curved / tapered?

    **Step 3 — Decide ring type, station count, and positions.**
    Based on Steps 1–2, determine for each candidate station whether to use:
    - Full closed ring (cargo or rear sections where skin forms a closed perimeter)
    - Partial arch (middle horseshoe upper arch only; bottom open)
    - No frame (head section is non-structural per Rev R1; foam + keel adequate)
    - Integrated boss rib (if load is highly localised, a rib printed into the shell SCAD
        may be lighter than a separate CF plate — evaluate for servo and spar stations)
    Record chosen station count (≥1; ≤5), hull-Y for each, and ring type.

    **Step 4 — Profile extraction and DXF generation.**
    For each chosen station: export 2D inner-skin boundary as DXF (FreeCAD TechDraw or
    `Draft.dxf` export of cross-section wire).  Add keel-bar notch (6×3 mm slot at hull
    −Z centroid).  Add 3 mm clearance all-round from skin so ring can be inserted and
    epoxy-bonded without force-fitting.  Save to `airframe/diagrams/ring_frames/`.

    **Step 5 — Update BOM and build guide.**
    - Update CF-PLATE-2MM Notes: confirmed station count, hull-Y values, ring types, mass.
    - Update `REVN_BUILD_GUIDE_24IN.md` keel datum mark table with new hull-Y stations.
    - If any station is replaced by an integrated shell rib, add SCAD sub-task under the
        relevant shell file (§1.1.1.1–§1.1.1.4).
    **BLOCKS keel bar + ring plate fabrication; BLOCKS foam pour.**

- [x] **Hull keel (CF-BAR-6X3) — complete first-principles re-evaluation *(Rev R1)*** *(done 2026-06-14)*
    Full analysis in `docs/structural_analysis.md` §2.  Decisions:
    - Keel spans cargo-to-rear (hull Y −71..+384 mm ≈ 455 mm), two lap-spliced segments.
    - Cargo segment: Z ≈ +1..+2 mm (belly, just above skin floor). Rear segment: Z ≈ +4.7..+5.7 mm.
    - CF-BAR-6X3 retained; oriented 6 mm vertical (strong axis), 3 mm horizontal. FOS ≥ 24.8 at 2g.
    - Head section excluded (incompatible Z floor at Z=+61 mm, non-structural, short section).
    - Middle section: keel passes through unsupported in foam; no hard attachment.
    - RF counterpoise: separate AWG 22 copper stranded wire alongside keel (CF bar inadequate at 49 MHz).
        BOM item WIRE-COUNTERPOISE-49MHZ added.
    - Keel locating channels cut into cargo and rear shells by `add_structural_features.py`.
    **SUB-TASKS OPEN:**
    - [x] Add WIRE-COUNTERPOISE-49MHZ to BOM: AWG 22 stranded tinned copper, 460 mm,
        2 g, routed alongside keel inside foam from cargo to rear, terminated at Emma
        antenna feed on River's Room stack. *(done 2026-06-22 — was referenced here since
        Rev R1 but never actually added; backfilled as part of §1.4.2 antenna work, which
        also added a second counterpoise wire, WIRE-COUNTERPOISE-49MHZ-2, for Simon's
        independent 49 MHz antenna.)*
    - [x] **DONE 2026-07-03.** `battery_tray.scad` keel-rail slot corrected to match the
        Rev R1 keel bar orientation (3 mm lateral(X) × 6 mm vertical(Z), strong axis
        vertical — structural_analysis.md §4.3): RAIL_W/RAIL_D swapped from 6.5/3.5 mm to
        3.5/6.5 mm. This required increasing FLOOR from 4.0 to 8.5 mm so the deeper rail
        slot does not breach the battery cavity (2.0 mm solid margin retained). Re-rendered
        via `openscad` and re-exported to `airframe/stls/fuselage/battery_tray.stl`
        (watertight, single body, verified with `trimesh`; solid CAD volume 133 519 mm³ →
        ~169.5 g at CF-PETG ρ=1.27 g/cm³, a 100%-solid upper bound that supersedes the
        stale, apparently-uncalculated "~22 g" placeholder — confirm the actual
        infill-derated mass in the slicer before finalizing the AUW budget). Keel Z
        position itself (cargo belly Z≈+1..+2 mm, §4.2) is set by the assembly transform,
        not this part file, so no additional change was needed there.
        **OPEN ITEM, not resolved by this edit:** the header's stated tray placement
        ("stations 60–130mm inside head/bridge section") conflicts with (a) the Rev R1
        keel decision, which is headless in that section, and (b) other TODO.md entries
        ("battery tray in cargo section") — while a separate, older note (~line 2818–2830,
        2026-06-08 Kaylee placement decision) instead places a battery boss pattern in the
        MIDDLE section keel face, which itself conflicts with the Rev R1 finding that the
        middle-section keel span is unsupported (foam only, no hard attachment). This
        three-way placement conflict (head / cargo / middle) needs a user decision before
        the tray's final hull-Y station and `serenity_assembly.py` placement can be set.
    - [x] **DONE 2026-07-03.** Updated `REVN_BUILD_GUIDE_24IN.md` keel installation section
        (steps 1–2) and CF-cuts table: span hull Y −71..+384 mm (455 mm), lap-splice at the
        middle/rear joint (hull Y ≈ +203 mm, 100 mm / 3.9 in total overlap — i.e. each
        segment extends 50 mm past the joint, per structural_analysis.md §4.3), ring-notch
        positions at hull Y = +30 mm and +290 mm.

    A continuous bow-to-stern backbone is structurally justified (primary fuselage bending
    moment arm; inter-section tie-rod spanning all fabrication splits).  However, the
    canonical Serenity hull geometry makes the current straight 6×3 mm flat bar
    infeasible as specified.  This is a clean-sheet keel design task.

    **Known geometry constraints (from baked hull-frame extents):**
    - **Head/Cargo Z step**: Head_Shell Z_min = +61.2 mm; Cargo_Shell Z_min = 0.0 mm.
        A straight keel at the cargo belly cannot enter the head section without a ≈ 61 mm
        vertical bend at hull Y ≈ −71 mm.
    - **Middle section open belly**: Middle_Shell (Y = +130.4..+203.6 mm) is open at −Z
        (horseshoe ring with no belly floor).  A belly keel has no skin to bond to for
        ~73 mm of hull length here.  Foam fill provides distributed elastic support but no
        hard attachment.
    - **Head section structural role**: Head_Shell is non-structural per Rev R1 (foam + 2 mm
        CF-PETG skin adequate; avionics bays relocated to cargo + rear sections).  A keel that
        terminates at the head/cargo joint face (hull Y ≈ −71 mm) may be fully adequate.
    - **Datum marks**: the 91/165/251/320/388 mm station marks are tied to the stale pre-Rev N
        ring plate positions and must be replaced by the new ring station outputs (see ring
        plate re-evaluation task above).

    **Step 1 — Decide keel span.**
    Determine whether the keel must enter the head section or whether cargo-to-rear
    (hull Y ≈ −71 mm → +384 mm, ≈ 455 mm) is structurally sufficient.  The head section
    contributes little to global fuselage bending (short, tapered, non-structural) and has
    an incompatible Z floor.  Cargo-to-rear span is preferred unless a specific head-section
    load case (e.g., FPV/GPS nose mount inertia) justifies the extension.

    **Step 2 — Determine Z routing through each section.**
    At each hull section, identify the highest Z level that provides:
    - Continuous bonding surface against inner skin or foam (closed loop or foam contact)
    - Clearance from avionics bays, battery tray, servo mounts, spar bores, and wiring trunk
    Candidate Z levels to survey (from section Z extents):
    - Cargo belly: Z ≈ +5..+15 mm (below battery tray floor, above hull skin)
    - Middle horseshoe: keel passes through the interior unsupported — foam alone provides
        lateral stability; check that Z routing clears the wiring trunk PTFE conduit.
    - Rear cone belly: Z ≈ +5..+15 mm (consistent with cargo level)
    Target: a monotonically constant or gently varying Z route from cargo to rear that
    requires no bends exceeding the material's minimum bend radius.

    **Step 3 — Choose keel form and cross-section.**
