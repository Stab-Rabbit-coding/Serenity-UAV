# Serenity UAV — Airframe (Hull-Frame Standard + Placeholders) Work Breakdown Structure (Detail)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Current design revision:** Rev S (2026-07-04)

> **Detail-holder for the root WBS.** The repository-root [`TODO.md`](../TODO.md)
> is a compact index — headings, subheadings, and short (<=70-char) checkbox items
> only, per root `AGENTS.md`. This file carries the full task detail for the WBS
> branches the root indexes below. Close an item here first, then check it off in
> the root index as a commit prerequisite (root `AGENTS.md` "Revisions and Version
> Control").

*"I don't care what you believe in, just believe in it. — Shepherd Book"*

---

**Cross-cutting system: Jayne (cargo handling)** — doors/winch/latch/gondola geometry is
in [fuselage-mid/TODO.md](fuselage-mid/TODO.md) §1.1.1; the full Jayne subsystem map
(vision/ToF/laser board, firmware, assembly, deferred range-extender battery) is in
[avionics/jayne/TODO.md](../avionics/jayne/TODO.md).

---

## §1.1.0 — Hull-Frame Coordinate Standardisation (R1)
*(root `WBS.md` §1.1.0)*


All design artifacts standardised on the validated hull frame (X = +port, Y = +aft,
Z = +dorsal; origin = SerenityAssembly.FCStd world origin). See CLAUDE.md
"Hull-Frame Coordinate Standard".

- [x] **`tools/bake_hull_frame.py` created** — idempotent STL bake tool; applies the
    validated 2026-06-10 placements to STL vertex data; stamps binary header marker
    `SerenityUAV HULL-FRAME R1`; refuses to double-transform. *(done 2026-06-11)*
- [x] **9 STLs baked to hull frame** — Head, Cargo (both repair copies), Middle, Rear,
    Wing×2, Nacelle×2. Watertight validation PASS before and after; facet counts
    unchanged; re-read verification ≤ 1.5e-5 mm. *(done 2026-06-11)*
- [x] **`serenity_assembly.py` Rev R1** — all 8 primary placements now identity;
    `doc.saveAs()` fix; `freecadcmd` entry-point fix; `airframe/Serenity-Assembled.FCStd`
    regenerated and world extents verified identical to the validated assembly.
    *(done 2026-06-11)*
- [x] **48 generator/analysis scripts stamped** with the hull-frame standard header
    (SCAD, Blender, FreeCAD, cargo generators, build-guide tools; GCS and deferred
    files annotated as documented exceptions). *(done 2026-06-11)*
- [x] **Docs updated** — CLAUDE.md (baked-extents table + pipeline rule), README.md,
    REPO_ENFORCEMENT.md, serenity-rev-r.jsx (R1 entry; axis typo fixed),
    PROJECT_INDEX.md. *(done 2026-06-11)*
- [x] **Resolve nacelle port/stbd label swap.** Confirmed by user FreeCAD layout
    inspection (2026-06-11): harness conduit exits inboard face; original SCAD naming
    was inverted. Fixed: STL files renamed (port↔stbd swap), binary 80-byte headers
    patched, `bake_hull_frame.py` COMPONENTS corrected, `serenity_assembly.py` audit
    comment updated, SCAD build commands corrected (port: SWIRL_DIR=−1/PYLON_SIDE=−1,
    stbd: SWIRL_DIR=+1/PYLON_SIDE=+1), CLAUDE.md extents table corrected.
    *(done 2026-06-11)*
- [ ] **Re-verify head↔cargo joint bosses in hull Y.** The 2026-06-10 joint analysis
    used hull X as the longitudinal mating axis; in the validated frame the longitudinal
    axis is Y (sections mate at hull Y ≈ −71 mm; X is lateral). Re-check
    BOSS_FORE/BOSS_AFT positions in `head_shell24.scad` / `cargo_sect_shell24.scad`
    against the baked meshes. **BLOCKS head/cargo printing.**
    - **Verification DONE 2026-06-29 (trimesh Y-cross-sections of the baked shells).**
        The SCAD `BOSS_FORE`/`BOSS_AFT` parameters are **obsolete** — the canonical joint
        bosses now come from `add_structural_features.py` `BOSS_PIN_BORES["joint1"]`
        (hull frame), the SCAD shells being secondary references (§1.1.1.0a).  Findings:
        - Joint faces mate correctly: HEAD aft Y-max = −70.73, CARGO fwd Y-min = −71.54
            → mate at hull Y ≈ −71. ✓
        - **The §1.1.1.0b "8 mm depth each side" claim is NOT met as-baked.** Measured
            Y-engagement of the three Ø3.2 boss pins (cut Y-range −79..−62):
            Pin A dorsal (−168.3,+143.9) HEAD 2.0 / CARGO 12.5 mm; Pin B (−138.0,+91.4)
            HEAD 2.0 / CARGO 3.5 mm; Pin C (−198.6,+91.4) HEAD 2.0 / CARGO 4.5 mm.
        - Root cause: straight Y-axis pins at a single (X,Z) engage a tapering 2 mm wall
            only over a short span — the head aft wall walks off within ~2 mm, and because
            the cargo is broader than the head the two **flank** pins (B,C at Z=+91.4)
            coincide with both shells' walls only right at the joint face.  Only the
            **dorsal** pin A (tops align) engages deeply.
        - **RESOLVED 2026-06-29 — internal splice collar designed (`PRINT-HEAD-CARGO-COLLAR`).**
            First-principles load check: the joint is **not strength-limited** (worst-case
            9 g crash → M ≈ 6.7 N·m on a ~350 mm-perimeter ring → < 1 MPa peak).  The real
            need is peel resistance + alignment + anti-ovalisation + the CLAUDE.md
            "2-wall annulus + positive stop."  Designed an internal bonded **splice collar**
            (`airframe/stls/fuselage/generate_head_cargo_splice_collar.py` →
            `head_cargo_splice_collar.stl`, hull frame, ~13.4 g, watertight, verified
            clearing the head inner wall): 2 mm wall, L = 16 mm (8 mm/side), profile = head
            inner contour @Y=−79 inset 2 mm, bonded across the joint with West System
            105/206 + 406 filler → shear-loaded double-lap, FOS > 100 on the bond.  The 3
            boss pins are **re-roled to alignment dowels only.**  Added to
            `serenity_assembly.py`, BOM (`bom_revR.csv`), `docs/structural_analysis.md` §7.3,
            `PROJECT_INDEX.md`.  ~~**Remaining:** boss-pin bores get re-cut by
            `add_structural_features.py`...~~ **SUPERSEDED 2026-07-06 (user directive):
            the joint boss-pins are now REMOVED entirely, not re-cut as dowels — the
            splice collar provides both securing and alignment.**  `add_structural_features.py`
            (head/middle/rear) and `merge_cargo_interior.py` (cargo) no longer cut ANY
            joint boss-pin bore; `BOSS_PIN_BORES` retired to a historical record.  Head,
            cargo, and middle regenerated 2026-07-06 from the clean Blender source and
            re-verified watertight (in-memory PASS, 0 boundary edges, single/expected body
            count) with the pins absent — confirmed geometrically (pin-axis bore-ring vertex
            count dropped ~80→~24 = plain wall).  The collar bonds to the printed shells at
            assembly.  (Rear pin removal is coded but rear cannot be regenerated until its
            Blender-source mesh is repaired — see MESH-01 below.)
- [x] **Regenerate cargo doors from the baked shell.** `cargo_door_port/stbd.stl`
    (2026-06-01) predate both the repaired-shell re-orientation and the bake; regenerate
    via `generate_cargo_doors.py` against the baked
    `s_cargo_sect_shell24_2mm_repaired.stl` and verify the belly faces hull −Z.
    **DONE 2026-06-16**: `generate_cargo_doors.py` rewritten for hull frame (Rev R1a).
    Belly faces detected by normal Z < −0.5.  Both doors watertight.
- [x] **Correct hinge location: outboard flank, not centreline.** Rev R1a (above)
    placed both doors' piano-hinge knuckles at the ship centreline X_CL (≈ −169.85 mm)
    with the free edges at the hull sides — backwards from the door behaviour already
    documented everywhere else in the repository (TODO.md §1.4.2, README.md, `rcrs49_wire_post.scad`),
    all of which describe the doors hinging at the **outboard flank/belly edge** and
    swinging **down and out from the aircraft, full 180° range of motion**, to open the
    bottom of the cargo bay. **DONE 2026-06-22 (Rev R1b, with user)**:
    `generate_cargo_doors.py` corrected so each door hinges independently at its own
    outboard belly edge with its free edge at X_CL — see corner-curvature note below
    for why the hinge X is NOT the cargo-section bounding box (X_SHELL_MIN/MAX). Removed
    the port/stbd knuckle Y-interleaving (no longer meaningful — each door is now its
    own independent piano hinge pinned to the fuselage, not a shared centreline hinge
    joining the two panels). Knuckle Z is now sampled from the belly interpolator at
    each hinge X rather than a bare literal.
    - [x] **Fix door-surface discontinuity found during verification.** First Rev R1b
        pass still produced doors with a visible crease: the door grid extended to the
        cargo-section bounding-box X (±72.7/−267 mm), but the real ventral belly mesh
        only exists out to X ≈ −114..−225 mm — beyond that the interpolator silently
        fell back to a flat plane, producing a sharp step roughly halfway across each
        door. **DONE 2026-06-22**: hinge lines are now derived at runtime from the
        actual detected belly-mesh edge (per-Y-row worst-case extent, so every sampled
        point has real data), AND a row/column despike pass (`despike_grid()`,
        max 1.0 mm/step) suppresses a second, smaller artifact at the aft-outboard
        corner where the belly curves toward vertical (into the side wall/aft
        bulkhead) faster than a single-valued height-field can represent — that corner
        also overlaps the documented landing-gear HULL_ATTACH_POS Y ≈ 100 mm boss
        region. The despike is a print-safety net, not a substitute for verifying
        the aft-outboard corner shape in FreeCAD — see sub-tasks below.
    - [x] **Fix disconnected knuckles / non-straight hinge axis found during
        verification.** The despiked-panel fix (above) sampled each knuckle's Z
        independently from the belly contour, so the 4 knuckles per door landed at
        4 different Z heights — physically wrong (a single CF rod is rigid and
        straight) and some knuckles ended up too far from the panel surface to union
        into the same solid (disconnected, floating geometry). **DONE 2026-06-22**:
        all 4 knuckles on a door now share one constant (X, Z) hinge axis (Z = mean
        of the panel's actual contour at the 4 knuckle positions + KNUCKLE_R); each
        knuckle is bonded to the contoured panel via a small per-knuckle gusset block
        (`make_knuckle_gusset()`) bridging whatever local Z gap exists between the
        straight axis and the panel surface at that knuckle's Y. Final doors: port
        55.2×106.0×9.1 mm (hinge X ≈ −117.6 mm, hinge Z ≈ 5.11 mm), stbd
        55.7×106.0×9.2 mm (hinge X ≈ −222.5 mm, hinge Z ≈ 5.22 mm); both verified as a
        single connected watertight body (`trimesh` `split()` → 1 body each).
    - [ ] **Verify cargo door fit in slicer** — open `cargo_door_port.stl` and
        `cargo_door_stbd.stl` in slicer; confirm hinge knuckles align at X ≈ −117.6 mm
        (port) and X ≈ −222.5 mm (stbd), free edges meet at X ≈ −169.85 mm, and panels
        cover Y = 2..108 mm at Z ≈ 0..5 mm. Pay particular attention to the aft-outboard
        corner of each door (Y → 108, near the hinge edge) — this is where the despike
        safety net (above) is masking real but algorithmically-unresolved hull
        curvature; confirm by eye it isn't flattened in a way that leaves a gap against
        the real hull. Verify no overlap with hull boss sockets (HULL_ATTACH_POS
        Y = 25, 100 mm). **BLOCKS cargo door printing.**
        - **Programmatic cross-check DONE 2026-06-29 (7/7 PASS, trimesh):** port door
            X −169.85..−114.60 (hinge X=−117.6), stbd X −225.51..−169.85 (hinge X=−222.5),
            free edges meet at CL X=−169.85, panels span Y 2..108 at Z≈0..8.7 (hinge
            Z≈5.1), doors do not interpenetrate at CL (Δ < 0.3 mm), both watertight single
            bodies, and the 4 Rev R1c retention blocks present/watertight with coaxial
            bores.  **Still open:** the visual aft-outboard-corner despike eyeball and the
            HULL_ATTACH_POS Y=25/100 boss-overlap check — the latter references the
            *retired* `landing_leg_assy.scad`; redo against the Rev R5 wire-brace hull
            bosses once those are finalized in the cargo shell (§1.1.4).
    - [ ] **Piano-hinge CF rod (×2, independent)** — verify 3 mm CF rod passes through
        each door's own 4 knuckle bores (3.15 mm bore) — port and stbd are now two
        separate pins/rods, not one shared centreline pin; test in printed prototype
        before final assembly.
        - **Geometry cross-check DONE 2026-06-29:** each door's 4 knuckle bores (Ø3.15)
            and the two Rev R1c shell-side retention-block bores (Ø3.3,
            `cargo_hinge_retention.stl`) are coaxial on the door's rod axis (port
            X=−117.6/Z=5.11, stbd X=−222.5/Z=5.22), rod span Y +2..+108.  Printed-prototype
            insertion test still required (physical).
    - [x] **Sync `cargo_sect_shell24.scad` hinge-pin blocks to the Rev R1b hinge lines.**
        **DONE 2026-06-29 (Rev R1c).**  The legacy `hinge_pin_block()` /
        `HINGE_Y`/`HINGE_Z` parameters describe a single shared hinge along the legacy
        part-local LATERAL axis in the pre-bake frame (Y = vertical, Z = lateral) —
        backwards from the Rev R1b design (two independent piano hinges pinned at the
        outboard belly edges, axes along hull Y).  Reframing that one module inside the
        legacy SCAD (whose `door_bay_cut`/servo/latch modules are still legacy-frame and
        interdependent) would leave the SCAD internally inconsistent, and the published
        cargo shell is now Blender-canonical (§1.1.1.0a), so the correct realization is a
        new self-contained hull-frame generator:
        **`airframe/stls/fuselage/cargo/generate_cargo_hinge_retention.py` (Rev R1c) →
        `cargo_hinge_retention.stl`** (4 blocks, 2 per door; to be boolean-unioned into
        the Blender cargo shell during the §1.1.1.0a interior-feature merge).  Verified
        against the baked door STLs: bore axes coincide with the door rod axes (port
        X=−117.6/Z=5.11, stbd X=−222.5/Z=5.22; bore Ø3.3 on rod span Y +2..+108), all 4
        blocks watertight, each bonds to intact belly skin outside the bay aperture
        (600–800 shell verts inside each block envelope), and all clear the Y 2..108
        aperture.  Legacy `hinge_pin_block()` marked **SUPERSEDED** in
        `cargo_sect_shell24.scad` (module header + A5 call site) but retained so the
        legacy SCAD still renders until the door-bay subsystem is reframed.  Added to
        `serenity_assembly.py` (identity placement, hull frame) and `PROJECT_INDEX.md`.
        flake8-clean.
- [x] **Consolidate duplicate cargo shell copies.** **DONE 2026-06-29.**  The
    `fuselage/`-level copy no longer exists on disk; a single canonical copy remains at
    `fuselage/cargo/cargo_sect_shell24_2mm_repaired.stl` (the `s_` prefix was dropped
    project-wide — see CLAUDE.md "File-naming").  It is baked (header marker
    `SerenityUAV HULL-FRAME R1 Cargo_Shell` present; extents X −267.0..−72.7,
    Y −71.5..132.0, Z 0..163.2 mm, matching the CLAUDE.md table).  All active references
    (`serenity_assembly.py`, `tools/bake_hull_frame.py`, `serenity_render_views.py`,
    `bom_revR.csv`) use the `fuselage/cargo/` path; the stale `s_cargo…` reference in
    `serenity_assembly.py` was corrected.  NOTE: the canonical copy still carries the
    **MESH-01 fragmentation defect** (71,131 disconnected bodies, `is_watertight=False`) —
    that is the separately-tracked MESH-01 blocker above, not a consolidation issue.
- [ ] **Hull-frame placements for VERIFY parts** (assembly-load blocker resolved; visual
    fit-validation remains). Cargo mounts (8), pylons, EDF sleeves,
    nozzles/gears, battery tray, belly panel, tip caps, dorsal antenna fin, landing
    legs/feet remain part-local; validate each in FreeCAD against the baked hull and
    either bake or record explicit placements in `serenity_assembly.py`.
    - **2026-06-29 — assembly now regenerates cleanly (was broken/stale since Jun 11).**
        Fixed a latent FreeCAD-1.0 bug in `transform_mesh()`: `obj.Mesh` returns an
        immutable reference, so the in-place `.transform()` raised "This object is
        immutable" and aborted every save (the first `transform_mesh` call hit it).
        Changed to copy → transform → reassign.  This unblocked the VERIFY-tier
        placements: battery tray, belly panel, and all nacelle-internal components
        (gears/sleeves/nozzle, §1.1.3.3) now apply their `transform_mesh()` placements,
        and `airframe/Serenity-Assembled.FCStd` rebuilds with 0 WARN/MISSING/error.
    - Also resolved all missing-STL refs that were WARN-skipping: stale `s_`-prefixed
        primary-shell/wing/cargo paths corrected; generated the two missing VERIFY STLs
        (battery_tray, belly_panel) and `nacelles/nacelle_servo_bracket.stl`; corrected
        the landing-gear feet/legs paths to the `landing-gear/` subdir (flagged RETIRED —
        Rev R5 wire-brace supersedes; hull placement is §1.1.4).
    - **REMAINING (FreeCAD-manual, user step per CLAUDE.md):** visual fit-validation of
        the part-local items still placed by estimate (cargo mounts ×8, pylons, tip caps,
        dorsal antenna fin, battery tray/belly panel transforms) against the baked hull,
        then bake or commit final placements.  The assembly loading cleanly is the
        prerequisite that was blocking this.
- [x] **Generate `battery_tray.stl` and `belly_panel.stl`** from their SCAD sources —
    **DONE 2026-06-29.**  Rendered from `airframe/openscad/fuselage/battery_tray.scad`
    and `belly_panel.scad` to `airframe/stls/fuselage/`.  Both watertight, single body
    (battery_tray 252 facets, local 154×47×62 mm; belly_panel 548 facets, 160×3.5×65 mm).
    Part-local / VERIFY-tier (NOT in `bake_hull_frame.py` COMPONENTS); placed via
    `transform_mesh()` in `serenity_assembly.py` — the two WARNs are now gone and the
    assembly regenerates cleanly (see VERIFY-parts item below).
- [x] **Archive deprecated FreeCAD prototypes** — **DONE 2026-06-29.**  `assembly1.py`,
    `Serenity-Assemble.py`, `Serenity-Subsystem-Assembly.py`,
    `serenity_subsystem_assembler.py`, and `serenity_fuselage_asm4.py` (the last from
    `airframe/freecad/assembly/`) `git mv`-ed to `airframe/archive/FreeCAD-scripts/`
    (history preserved).  No active references remained.  `PROJECT_INDEX.md` entries
    removed; `ARCHIVE_INDEX.md` section "airframe/archive/FreeCAD-scripts/" added.
    The canonical `SerenityAssembly.FCStd` was left in place in `airframe/freecad/assembly/`.


## §1.1.5 — Non-Printable Component Placeholders
*(root `WBS.md` §1.1.5)*


Dimensionally-accurate bounding-geometry STL placeholder files for all non-printable
Rev S BOM components, for use in FreeCAD exploded-view and build-guide assembly.

**Generator:** `airframe/placeholders/generate_placeholders.py`
(pure Python, no external dependencies; run with `python3 generate_placeholders.py`)

**FreeCAD catalog script:** `airframe/FreeCAD-scripts/serenity_placeholders_assembly.py`
(loads all 76 placeholder STLs into a grid-layout catalog document;
run with `freecadcmd airframe/FreeCAD-scripts/serenity_placeholders_assembly.py`)

**Output:** `airframe/Serenity-Placeholders.FCStd` (76 components, 8-column grid)

**Placeholder coverage (76 STLs, 6056 triangles total):**

| Category | Count | Files |
|---|---|---|
| Propulsion (EDFs, ESCs) | 4 | `airframe/placeholders/propulsion/` |
| Servos (DS3218MG, SG90) | 2 | `airframe/placeholders/servos/` |
| Bearings (MF104ZZ, MR63ZZ, 6804) | 3 | `airframe/placeholders/bearings/` |
| Structural CF (rods, tube, bar, plate, PTFE) | 6 | `airframe/placeholders/structural/` |
| Avionics PCBs (PB2-I, Cape-A-2/B-2, Emma, Kaylee, microSD) | 6 | `airframe/placeholders/avionics/` |
| Power (LiPos, fuses, shunt) | 7 | `airframe/placeholders/power/` |
| Cargo (N20, HX711, DRV8833, Dyneema) | 4 | `airframe/placeholders/cargo/` |
| Gears M=1.0 (sector, pinion, bevel, housing) | 4 | `airframe/placeholders/gears/` |
| Hardware (pins, inserts, screws, straps, wire ring) | 6 | `airframe/placeholders/hardware/` |
| Lighting (WS2812C SMD nav LED) | 1 | `airframe/placeholders/lighting/` |
| Wiring (conduit, harnesses, antenna wire, posts) | 6 | `airframe/placeholders/wiring/` |
| GCS / Malcolm (enclosure, BECs, antennas, tripod, encoders) | 15 | `airframe/placeholders/gcs/` |
| Foam fill + interior voids (head/cargo/middle/rear fill; avbay, cargo bay, wiring trunk, power bus, ventilation, pylon pockets; Faraday cage pockets + vent duct spurs) | 13 | `airframe/placeholders/foam/` |
| EMC / Faraday shielding (cage, gasket, fan, EMI vent, bond strap, feed-through panel, ferrite; Malcolm fan + gasket) | 9 (×2 STL files share gen_far_fan_40) | `airframe/placeholders/faraday/` |

**Completed (2026-06-12):**
- [x] **Generate all 65 component placeholder STLs** — `generate_placeholders.py` created;
    all files verified `OK`. STL header marker: `SerenityUAV PLACEHOLDER R1`. *(done 2026-06-12)*
- [x] **FreeCAD catalog assembly script** — `serenity_placeholders_assembly.py` created;
    component grid layout; run with `freecadcmd`. *(done 2026-06-12)*
- [x] **Faraday shielding hardware** — 9 new generators; 11 new STL files in `airframe/placeholders/faraday/`:
    FAR-CAGE-AV (cage), FAR-GASKET-AV, FAR-FAN-40, FAR-EMI-VENT-40, FAR-BOND-STRAP,
    FAR-FT-PANEL, FAR-FERRITE-4MM; MAL-FAR-FAN, MAL-FAR-GASKET (GCS).
    BOM entries added to `current-specification/bom_revR.csv`.
    **⚠ MASS NOTICE: Faraday aircraft system now 364 g (0.80 lbm) after
    ferrite reduction to 4/cage and 1 bond strap/cage. Full Rev R1 weight
    reduction pass (Phase 11 deferrals, wiring gauge, PCB consolidation,
    head infill, CF plates) brings cumulative T/W to ~1.19 without battery
    swap; T/W ~1.25 with BATT-6S-2800. See §1.1.5 mass budget.**
    *(done 2026-06-13)*
- [x] **Faraday cage foam voids** — VOID-FAR-CAGE (76×56×88 mm cage pocket) and
    VOID-FAR-FAN-SPUR (44×44×50 mm vent duct spur) added to `airframe/placeholders/foam/`.
    Use ×4 and ×8 copies respectively in FreeCAD to plan all 4 bays. *(done 2026-06-13)*
- [x] **Foam-fill and void visualization STLs** — 11 new STLs in `airframe/placeholders/foam/`:
    4× FOAM-FILL-\* (head/cargo/middle/rear hull sections) and 7× VOID-\* (avionics bays,
    cargo bay, wiring trunk, power bus, ventilation intake/exhaust, nacelle pylon pockets).
    Total 76 components, 6056 triangles. Use tan/ochre for FOAM-FILL, translucent cyan for
    VOID objects in FreeCAD. *(done 2026-06-12)*

**Open sub-tasks:**
- [ ] **Rear skid reinforcement — SCAD update (TWO files)**
    The skids are the aft extensions of the middle-section horseshoe ring; the
    middle/rear section cut was made purely for printability and carries no load.
    The CF rod must therefore span BOTH sections continuously to reinforce the
    full skid bending span and to tie the print joint together.
    Changes required:
    - `s_middle_canonical_shell24.scad`: add 4.2 mm bore channel along each
        horseshoe-bent-aft skid arm from the horseshoe origin to the aft face
        (middle/rear joint face at hull Y ≈ +203 mm).
    - `s_rear_neck_intake_shell24.scad`: add matching coaxial 4.2 mm bore
        channel through the skid extension from the joint face to the skid tip.
    - Channels must be coaxially aligned across the joint face to accept a
        single continuous rod. Nominal channel axis = hull Z-face centroid of
        each skid cross-section.
    - Rod: 4 mm OD solid CF from CF-ROD-4MM stock, ~250 mm per skid × 2
        skids = ~500 mm total; insert from aft, epoxy (West System 105/206).
    - Rod serves triple purpose: skid bending stiffness, middle/rear joint
        tie-together, assembly alignment pin.
    - Re-slice both parts after SCAD update; update masses in BOM.
    **BLOCKS first taxi/landing test.**
- [ ] **Run FreeCAD catalog** — execute `serenity_placeholders_assembly.py` once
    FreeCAD is available to verify grid layout and produce
    `airframe/Serenity-Placeholders.FCStd`. Commit the FCStd to the repository.
- [ ] **Hull-frame placement pass** — for the full-build exploded view (§1.1.4 task),
    derive the hull-frame position and orientation of each placeholder (e.g., EDF
    inside nacelle bore, battery tray in cargo section, avionics PCBs in bays)
    and add `place_mesh()` calls to `serenity_placeholders_assembly.py`.
- [ ] **Add Phase-11 (deferred) items to catalog** — regenerate placeholders for the
    Rev R1 rear-EDF redesign: `EDF_55mm_6S_deferred.stl`, `ESC_50A_6S_BLHeli32_deferred.stl`,
    `rear_nozzle_canonical_deferred.stl`, and `rcs_thruster_x4_deferred.stl`; confirm they
    appear in the `deferred/aft-edf/` sub-assembly once that phase resumes. (Old 120mm/80A
    placeholders are superseded.)
- [ ] **Mesh watertightness audit** — run `python tools/validate_stls.py` across
    `airframe/placeholders/**/*.stl` after first CI run; resolve any non-manifold
    findings (complex compound meshes: piano-wire torus ring, RF splitter ports, etc.).
    **Known finding:** `Foam_fill_middle_horseshoe_173x69x161mm.stl` has coplanar
    T-junction faces at Z=121 mm between left/right pillar tops and the arch bottom
    (all three pieces share a common plane but are separate box meshes joined via `_cat()`).
    Acceptable for visualisation; fix by replacing with a proper extruded U-shape when
    trimesh/CSG support is available.
- [ ] **FAR-FT-PANEL PCB design** — design the EMI-filtered feed-through panel
    KiCad schematic + layout (55×35 mm, LP π-filter + TVS on CAN FD ×2,
    RS-485, Ethernet RJ45, power JST-GH 2P). Run DRC; generate gerbers; add
    to `avionics/kicad/`. **BLOCKS Faraday cage final assembly.**
- [x] **Faraday mass budget review** — Faraday aircraft system 364 g (0.80 lbm)
    after Rev R1 ferrite (4/cage) + strap (1/cage) reduction. Full weight
    reduction pass (2026-06-13) brings estimated T/W to ~1.19; BATT-6S-2800
    swap yields ~1.25 — above the 1.2 minimum. *(resolved 2026-06-13)*
- [ ] **Link placeholders to BOM entries** — add `Placeholder_STL` field to
    `docs/bom_revR.json` for each non-printable row pointing to its STL path.

---


## Procurement — §2.1, §2.2, §2.3, §2.6 (BOM tables)
*(root `TODO.md` §2.1-§2.3, §2.6)*


| Item | Qty | Notes |
|------|-----|-------|
| PETG filament | ~1,200 g | Access panels, nozzle parts, cargo gondola — **TODO: recompute split, hull sections moved to CF-PETG row below per CLAUDE.md Fabrication Standards** |
| CF-PETG filament | ~500 g | Hull sections (head, middle, cargo, rear neck, wings), nacelle pods, tilt brackets, pylon, intake frame — hardened-steel nozzle required |
| TPU 95A filament | ~200 g | Landing skid feet — direct-drive extruder required |
| CF flat bar 6×3mm | ~700 mm | Keel 620 mm + 80 mm ring frame offcuts |
| CF tube 12mm OD / 1.5mm wall | ~850 mm | Wing spars 2×380 mm + 90 mm scrap |
| CF solid rod 4mm OD | ~300 mm | Pivot rods (2× nacelle) per pivot housing drawing |
| CF plate 2mm | 250×150 mm | Ring frames (5 stations per drawing) |



| Item | Qty | Notes |
|------|-----|-------|
| West System 105/206 epoxy | 1 kit | Keel + spar bonding; structural joints |
| 5-minute epoxy syringe 25mL | 3× | Access frames, sensor mounts |
| X-30 PU foam 2-part | ~600 mL | 2 lb/ft³, 4× expansion, 2-min pot life |
| EPS blue foam board 25mm | 500×250 mm | Void formers A–E; Owens Corning Foamular 150 |
| Johnson's Paste Wax | 1 tin | Void former release agent (2 coats) |
| 3M 4016 closed-cell gasket tape | 1 roll | Access panel frame lips |
| PTFE tube 5mm OD × 3mm ID | 6 m | 8 conduits (CAN FD, RS-485, 1553A, 1553B, ETH×2, SERVO-PWR, MAIN-PWR) |
| M2.5 nylon hex standoff 6mm | 16× | Cape-B floor mounts (4 per bay × 4 bays) |
| M2.5 nylon hex standoff 20mm | 16× | Cape-A inter-cape spacing |
| M2.5 × 8mm SS button screws | 64× | Standoff attachment + panel B/E fasteners |
| M3 heat-set threaded inserts | 4× | Cargo gondola belly hard points |
| N42 neodymium disc magnet 6×2mm | 8× | Panel D (4 in frame + 4 in lid) |
| SMA panel-mount bulkhead | 3× | SiK 915MHz (belly) + LoRa 915MHz (belly) + Wi-Fi (dorsal fwd) |
| 0.3mm stainless wire or 22AWG enamelled Cu | ~500 mm | 49 MHz (Part 15 §15.235) top wire |
| Ceramic bead insulator 3mm ID | 1× | Aft end of 49MHz wire (insulated/open end) |



| Item | Qty | Approx. Cost | Notes |
|------|-----|-------------|-------|
| 50mm EDF @ 6S (budget tier) | 4× | ~$25–40ea | 2 per nacelle, tandem; verify OD fits 55–56mm ID bore |
| 40A 6S BLHeli32 BDSHOT ESC | 4× | ~$18–25ea | 1 per nacelle EDF |
| 55mm 6S EDF (~1,500 gf) | 1× | ~$35–55 | Fuselage rear; canonical tail nozzle; **Phase 11 deferred** |
| 50A 6S BLHeli32 ESC | 1× | ~$18–28 | Fuselage EDF; **Phase 11 deferred** |
| Digital tilt servo ≥25 kg·cm @ 6V, metal gear | 2× | ~$20–30ea | Nacelle tilt; prefer 30+ kg·cm |
| SG90 micro servo | 2× | ~$3ea | Nacelle nozzle ×2 (redundant) |
| SG90-class proportional valve servo | 4× | ~$3ea | RCS bleed jets; **Phase 11 deferred** |
| MF104ZZ flanged bearing 4×10×4mm | 4× | ~$8 total | 2 per nacelle pivot |
| 4mm OD CF rod (pivot) | 2× cut lengths | — | From 2.3 CF stock above |
| Steel pushrod 2mm OD × ~60mm | 2× | ~$3 total | Longitudinal nozzle shaft per nacelle |
| Steel pushrod 2mm, Z-bend ends | 2× | ~$4 total | Tilt servo pushrod |
| M2 clevis links | 4× | ~$3 total | Servo-to-pushrod |
| 3mm×18mm SS dowel pins (PIN-3X18) | 16× | ~$10 total | 8 per nacelle; Rev S nozzle flap tangential hinges |
| 2mm×4mm SS dowel pins (PIN-2X4) | 16× | ~$6 total | 8 per nacelle; Rev S flap cam followers (replace the retired piano-wire link ring) |
| WS2812C-2020 addressable LED | 6× | ~$6 total | Nav lights |
| XT90 PDB, 4× XT30 outputs | 1× | ~$12 | Power distribution |
| XT90 battery pigtail | 1× | ~$5 | Battery lead |
| 5V 5A switching BEC | 1× | ~$8 | Avionics power rail |
| 14AWG silicone wire | 1 m | ~$6 | Main bus |
| 16AWG silicone wire | 0.5 m | ~$4 | ESC signal + fuselage taps |
| 6S 4000mAh LiPo battery | 1× | ~$55–70 | Phase 6 first flight |



| Item | Qty | Approx. Cost | Notes |
|------|-----|-------------|-------|
| N20 DC motor 6V 300:1 | 1× | ~$8 | Winch drive |
| DRV8833 dual H-bridge driver | 1× | ~$2 | |
| SG90 servo | 2× | ~$6 | Door actuator + payload release |
| Dyneema SK75 0.5mm braid | 2 m | ~$4 | Winch line |
| 3mm CF rod | ~60 mm | — | Clamshell door hinge pin |
| Closed-cell foam gasket tape | — | — | Gondola-to-hull perimeter seal |

---

