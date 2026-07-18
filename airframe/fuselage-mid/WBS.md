# Serenity UAV — Airframe Fuselage — Head/Cargo/Middle Shells, Kaylee/Simon Bays Work Breakdown Structure (Detail)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Current design revision:** Rev S (2026-07-04)

> **Detail-holder for the root WBS.** The repository-root [`TODO.md`](../../TODO.md)
> is a compact index — headings, subheadings, and short (<=70-char) checkbox items
> only, per root `CLAUDE.md`. This file carries the full task detail for the WBS
> branches the root indexes below. Close an item here first, then check it off in
> the root index as a commit prerequisite (root `CLAUDE.md` "Revisions and Version
> Control").

*"A special hell. — Shepherd Book"*

---

## §1.1.1 — Fuselage: Shell Regeneration, Middle-Section Bays (part 3/3)
*(root `WBS.md` §1.1.1)*

    - **Straight flat bar (CF-BAR-6X3)**: viable only if Z routing is constant.  6 mm wide
        face ideally oriented horizontally (resist vertical bending = primary fuselage mode).
        Minimum bend radius for 6×3 CF bar ≈ 200–300 mm; tighter bends require separate spans.
    - **Pre-bent flat bar**: single bar bent in the weak axis (3 mm thickness) to follow a
        gentle Z curve.  Requires heat + jig; feasible if total Z variation over the keel span
        is < 30 mm and bends are gradual.  Confirm with material supplier.
    - **Segmented with lap splice**: two or three straight segments (e.g., cargo + rear);
        overlapping lap joint (≥ 50 mm) at each join, bonded with West System 105/206 + peel
        ply prep.  Maintains continuity without bending.  Adds ≤ 5 g mass at each splice.
    - **CF tube**: round tube (e.g., 6 mm OD × 1 mm wall) is isotropic in bending, easier
        to route curves, and can double as a wiring conduit.  Lower area moment of inertia
        than a 6×3 flat bar in the primary bending axis — check adequacy.
    - **CF tow/tape embedded in foam**: lays up along any geometry during foam pour; no
        discrete part to install; non-inspectable after pour.  Lowest mass option but least
        stiff and non-replaceable.

    **Step 4 — Assess RF counterpoise function.**
    CF-BAR-6X3 currently doubles as the 49 MHz (Part 15 §15.235) antenna counterpoise.  CF has anisotropic
    conductivity (longitudinal only, ≈ 5–10 kΩ/m vs copper ≈ 0.017 Ω/m); it is a poor RF
    conductor.  At 49 MHz, λ = 6.12 m; λ/4 = 1.53 m; a 455–620 mm bar is ≈ λ/10 — a
    dedicated copper counterpoise wire (AWG 22 stranded, < 2 g) bonded alongside the keel
    is more reliable than relying on CF conductivity.  Decide: (a) keep CF keel as structural
    only and add a separate copper counterpoise wire in the wiring trunk, or (b) embed a
    copper braid in the keel lap joint.  Update Emma/XCVR antenna design accordingly.

    **Step 5 — Update BOM, battery tray, and build guide.**
    - Update CF-BAR-6X3 Notes: confirmed form, span, Z routing, cross-section, mass.
    - Battery tray SCAD (`battery_tray.scad`): the "keel rail" interface must match the
        new keel Z position and cross-section; update SCAD and re-export STL.
    - Update `REVN_BUILD_GUIDE_24IN.md` keel installation section with new span, Z level,
        lap joint positions, and ring plate notch locations (from ring plate re-evaluation).
    - If separate copper counterpoise wire is chosen, add to BOM as WIRE-COUNTERPOISE-49MHZ.
    **BLOCKS ring plate notch design; BLOCKS keel fabrication; BLOCKS foam pour.**
    **Run concurrently with CF ring plate re-evaluation (ring plate notch geometry depends
    on keel cross-section and Z position).**

- [x] **Access panel frames + covers (24" Rev R)** — `airframe/openscad/fuselage/access_panels_24in.scad` created 2026-06-11. Geometries derived from authoritative shell SCADs (Rev R baseline):
    - 4× Faraday-bay covers (Shepherd/Inara/River/Simon): 72×52 mm, 4× M3 clearance bores, positive-stop shoulder; Inara + River covers include Ø42 mm GPS retention-ring recess.
    - 2× ventral hatch covers: battery 160×60 mm, Kaylee 115×100 mm; M2.5 pilots into bonded frames.
    - 2× ventral hatch frames: battery + Kaylee; 6 mm CF-PETG wall, West System 105/206 epoxy-bonded to hull.
    - **SUB-TASKS:**
        - [ ] Export individual STLs (set RENDER variable in SCAD): shepherd, inara, river, simon,
            battery, battery_f, kaylee, kaylee_f → `airframe/stls/fuselage/` — **NOT DONE
            2026-07-03**: `openscad -o` export could not be run this session (sandboxed sub-agent
            Bash permission hook blocks any command containing `-o`, and the main session hit a
            separate OpenSCAD-render permission block); must be run by the user or an unrestricted
            session.
        - [ ] Verify cover shoulder fit in slicer cross-section (confirm 1.5 mm step seats on hull
            face) — blocked on STL export above.
        - [x] **GPS clearance geometry re-derived to the dorsal frame — RESOLVED 2026-07-06.**
            `access_panels_24in.scad` Rev R2: Inara/River covers rebuilt with a new
            `av_cover_dorsalZ()` module in the corrected DORSAL (+Z-normal) frame, sourcing
            every constant from `cargo_sect_shell24.scad` (INARA_X/RIVER_X = CX∓37.5,
            AVIONICS_STATION_Y = CY, dorsal face Z=163.2, GPS_PORT/STBD_X = CX∓30 at the
            shared Y station). **GPS clearance bore corrected 42 → Ø38 mm** to match the
            shell's own `avinics_dorsal_panel_cut` note ("access cover designed with Ø38 mm
            clearance bore"; clears the Ø36 GPS body). Rendered + verified watertight, single
            body. **ANTENNAS MOVED OUTBOARD 2026-07-06 (user directive):** `GPS_SEP` 30 → 37.5
            mm in both `cargo_sect_shell24.scad` and `access_panels_24in.scad`, co-locating
            each GPS with its bay/cover centre (= `BAY_SEP_X`/2). The ~46 mm-wide (OML-trimmed)
            cover only keeps a Ø38 bore fully enclosed if the antenna is within ~±4 mm of the
            cover centre; at the old 30 mm it sat 7.5 mm inboard and the bore broke the cover's
            inboard edge (scallop). Re-rendered + verified: GPS bore is now a **fully-enclosed
            interior hole** (6 section loops = outer + 4 M3 + 1 GPS; single watertight body;
            `inara_access_cover.stl` 4604 mm³, `river_access_cover.stl` 4456 mm³; 26 mm to each
            cover edge, 7 mm bore margin). New GPS centre-to-centre = 75 mm; Ø44 retention rings
            still clear (31 mm gap). VERIFY-in-slicer: confirm each antenna still lands on flat
            enough dorsal skin at the outboard station and the SMA pocket clears the Faraday
            tray below.
        - [x] **M3 bore positions now match the shell boss pattern — RESOLVED 2026-07-06.**
            The dorsal-Z covers cut their 4× M3 bores at ±`AVZ_SCREW_DX`(15, X) ×
            `AVZ_SCREW_DY`(25, Y) = `cargo_sect_shell24.scad` `AVINICS_BOSS_DX/DY` exactly
            (was mismatched 25/15 in the wrong X-Z axes). Verified geometrically from the
            rendered STL: bore centres at (±15, ±25) mm, Ø3.3 M3 clearance. (Shepherd/Simon
            covers stay on the legacy Y-normal `av_cover_dorsal` until the head/middle
            avionics bays get the same dorsal-axis fix — the still-open head/middle
            axis-bug items in this section.)

- [x] **49 MHz (Part 15 §15.235) wire posts** — `airframe/openscad/fuselage/rcrs49_wire_post.scad` created 2026-06-11.
    Single `wire_post()` module: 12×12×2 mm PETG base, 8×8×7 mm mast, Ø1.5 mm athwartships wire-retention bore at 2 mm from top.
    **Relocated 2026-06-22 (§1.4.2):** dorsal-centreline mount superseded — print FOUR posts (two antennas, two posts each):
    River's antenna forward (sta ≈ 120 mm) + aft (sta ≈ 580 mm) on the **port flank**, Simon's antenna forward + aft (same
    stations) on the **starboard flank**, both at shoulder height.
    Reasons: (a) a single shared dorsal run put River's and Simon's independent 49 MHz antennas (§1.4.2) too close together;
    (b) the cargo bay clamshell doors hinge at the outboard flank/belly edge and swing up to 180° (`generate_cargo_doors.py`),
    so any ventral or low-flank exterior post in the cargo bay's Y-span is in the door's path — shoulder height, port/starboard, clears both.

    - **BLOCKS Phase 1 (antenna installation)**
    - **SUB-TASKS:**
        - [ ] Export STL → `airframe/stls/fuselage/rcrs49_wire_post.stl` (×4 instances, no geometry
            change needed — same module, different bond points) — **NOT DONE 2026-07-03**:
            `openscad -o` export could not be run in this sandboxed session (Bash permission hook
            blocks any `-o`-flagged command); rerun with an unrestricted session.
        - [ ] **Verify port/starboard shoulder-height mount line in FreeCAD against the cargo
            door's 180°-open swing envelope** — **partially verified 2026-07-03 (source-level
            only, no STL yet)**: confirmed the door bay's Y-span (hull Y 2–108, per
            `generate_cargo_doors.py`) converts to station-from-nose 307.6–413.6 mm (nose tip hull
            Y=−305.6), which sits entirely inside the post run (sta 120–580 mm) — the mid-run
            wire, not just the two discrete posts, crosses the door's swing zone and must clear
            it. Door swing envelope = a semicircle radius ≈52–55 mm (measured door width)
            centered at hinge (X=−117.6 port/−222.5 stbd, Z≈5.1–5.2), spanning only hull Y 2–108.
            `rcrs49_wire_post.scad` still has **no defined shoulder-height Z value** (flagged open
            in its own header) — cannot compute a real clearance margin until that Z is set;
            recommend Z ≥ 65 mm (hinge Z + envelope radius + margin) at any station falling within
            hull Y 2–108, then re-verify numerically. **Still BLOCKS bonding both antennas'
            posts.**
        - [ ] Bond River's forward post to the port flank at sta 120 mm; dress wire aft to River's Emma J2
        - [ ] Bond Simon's forward post to the starboard flank at sta 120 mm; dress wire aft to Simon's Emma J2
        - [ ] Install both temporary aft posts (port + starboard) at sta 580 mm; remove and replace with integrated mounts in Phase 11

##### 1.1.1.1 *Head*

**Geometry verification (hull-frame coordinate analysis, 2026-06-10):**

- [x] **Verify head-cargo mating boss positions in slicer — SUPERSEDED, see RESOLVED note below.**
    Hull-frame analysis (2026-06-10): `Head_Shell` Identity rotation, Base=[−332, −18, +61];
    head aft face (head local_X=99) maps to hull_X = 99−332 = **−233 mm**.
    `Cargo_Shell` 180°-Z rotation, Base=[−274.4, −282.8, 0]; matching cargo local_X =
    −(−233) − 274.4 = **−41.4 mm** — corrected in `cargo_sect_shell24.scad` BOSS_FORE
    (was X=−7, now X=−41.4). **VERIFY** both sections simultaneously in an assembly render
    or slicer that shows both STLs in hull-frame placement.  Confirm 6 head BOSS_AFT bosses
    (at head local_X=99) align with 6 cargo BOSS_FORE bosses (at cargo local_X=−41.4) in
    the assembled hull.  All Y/Z offsets remain estimated; also VERIFY those after X is confirmed.
    Ref: `head_shell24.scad` BOSS_AFT_* comments; `cargo_sect_shell24.scad` hull-frame block.
    **R1 AUDIT (2026-06-11): this analysis used hull X as the longitudinal mating axis, but
    in the validated hull frame X is LATERAL (+port) and the longitudinal axis is Y — the
    baked head and cargo meshes mate at hull Y ≈ −71 mm.  Redo the joint analysis in hull Y
    (see §1.1.0) before trusting BOSS_FORE = −41.4 mm.**
    **RESOLVED 2026-06-29 (see §1.1.0 "Re-verify head↔cargo joint bosses in hull Y"):**
    the hull-Y verification was done against the baked meshes.  `BOSS_FORE = −41.4 mm`
    (and the whole SCAD `BOSS_FORE`/`BOSS_AFT` scheme) is **obsolete** — the canonical
    joint-1 bosses are `add_structural_features.py` `BOSS_PIN_BORES["joint1"]` in hull
    frame.  Faces mate at hull Y ≈ −71 ✓; measured pin engagement is shallow on the two
    flank pins (the "8 mm each side" target is not met as-baked) — flagged for a
    structural decision in §1.1.0.

**Rev R shell updates (sensor/antenna mounts; carried fwd from Rev O, 2026-05-24):**

- [ ] **head_shell24.stl** — regenerate from `airframe/openscad/fuselage/head_shell24.scad` Rev S2.
    - Rev S2 (2026-06-16) corrected FWD_ROT and all three nose-face aperture positions;
        see Rev S2 note at top of SCAD for root-cause detail.
    - [ ] **Verify S1A, S1B, FPV positions at nose surface in slicer** — load generated STL
        and cross-section at Y ≈ −268 to −280 mm (pre-bake frame); confirm apertures cut
        cleanly through the nose-face hull skin, not the port lateral skin.
        Adjust S1A_POS / S1B_POS / FPV_POS Y values if nose face is at a different Y
        at the sensor's (X, Z) coordinates.
    - [ ] **Specify laser pointer mount** — laser pointer is currently documented as
        colocated with S1A/S1B (green highlight, port side nose face), but no separate
        aperture is cut.  Once laser pointer hardware is selected, add a laser_cut()
        module with the appropriate bore size adjacent to or integrated with S1A aperture.
    - [ ] **Correct BOSS_AFT positions** — BOSS_AFT_* in `head_shell24.scad` use X=99 as
        the aft face (legacy X=longitudinal convention, same root cause as Rev S2 sensor
        correction).  Hull-frame aft joint face is at Y ≈ −53 mm; BOSS_AFT_ROT should be
        [0,90,0] only if facing into the joint (−Y direction → [−90,0,0]).  See §1.1.0
        open item and §1.1.1 for the full correction plan — this is a pre-existing blocker.
    - [ ] create mounting bracket for camera/tof/laser control pcb
    - Verify Faraday tray cutout and all other non-boss geometry unchanged after SCAD re-render.

##### 1.1.1.2 *Cargo*

**Rev R shell updates (sensor/antenna mounts; carried fwd from Rev O, 2026-05-24):**

- [ ] **cargo_sect_shell24.stl** — regenerate from `serenity/stl/cargo_sect_shell24.scad` (cargo nadir FPV mount added)
    - Both outputs go to `thingverse-serenity/files-hollowed-18in/`

###### 1.1.1.2.1 *Cargo Handling*

**Cargo handling equipment:**

- [x] **Mounting hardware — 8 STLs** generated by `serenity/stl/generate_cargo_mounts.py` (Python/trimesh/manifold3d). Output: `thingverse-serenity/files-hollowed-18in/cargo_*.stl` *(done 2026-05-30, PR #21)*
    - [x] cargo_winch_motor_mount (CF-PETG), cargo_winch_spool (PETG), cargo_door_servo_bracket (CF-PETG), cargo_release_servo_bracket (CF-PETG), cargo_drv8833_tray (PETG), cargo_cradle_autolatch (PETG), cargo_gps_retention_ring (PETG), cargo_fpv_bezel (PETG)

- [ ] **Cargo gondola shell** — create `serenity/stl/s_cargo_gondola_shell.scad`: 112×85×22 mm belly pod, 4× M3 hard point pattern, 18 mm protrusion below hull line
- [ ] **Clamshell door halves** — `cargo_door_port.stl` + `cargo_door_stbd.stl` generated by
    `serenity/stl/generate_cargo_doors.py` Doors hinge on port and starboard sides and meet at the centerline.  Doors open out to 180 deg, allowing landing over and loading 4"x3"x3" cargo payload, or raising/lowering it in flight via the internal winch. (trimesh/scipy bilinear interpolation from Rev-O shell belly faces). 8-barrel piano hinge, 3 mm CF rod, 3.15 mm bore.
- [x] **`cargo_sect_shell24.scad` Rev S** — belly opening (100×9×165 mm), 2× hinge-pin blocks
    (3.3 mm bore + M3 grub-screw tap), 2× SG90 servo mounting pads (4× M2.5 pilots each), 4×
    latch-catch lips (Z=42/122 mm at each X frame edge). *(done 2026-06-01)*
- [x] **`cargo_sect_shell24.scad` Rev S1** — wing root mortises (30.8×20.8×15 mm), spar bearing
    blocks (22 mm OD × 10 mm boss, M3 grub-screw), full-Z spar bore (Ø12.3 mm), and nacelle tilt
    servo mount blocks (52×30×8 mm, 4× RX-M3×5.7 inserts) at port + stbd interior Z walls.
    All 4 spatial conflicts resolved (NSVMT_X_CEN moved AFT to −147.6 mm). Load FOS ≥ 11 vs 4.0
    AUVSI target. *(done 2026-06-08, PR #42)*
- [x] **`cargo_sect_shell24.scad` Rev S2** — Inara and River avionics bay dorsal standoffs
    (8× M3 boss posts, ±40×±25 mm pattern) + dorsal access panel cuts (62×42 mm each) for Cape-B
    (55×35 mm) at port half (Z_CEN=118 mm, Inara) and stbd half (Z_CEN=45 mm, River). GPS_PORT/STBD
    colocated for minimal SMA routing. *(done 2026-06-08, PR #42)*
- [x] **`cargo_sect_shell24.scad` Rev S3** — Faraday enclosure space allocation.
    Panel cuts enlarged 55×35 → 62×42 mm; boss offsets updated ±40×±25 → [TBD pending PCB layout — hole pattern must be derived from Wash.kicad_pcb / Zoë.kicad_pcb once layout is complete] to match
    Faraday tray corner mounts; bay Z centres adjusted ±1 mm (Inara 118→119, River 45→44) for 10 mm
    inter-bay gap; FARADAY_* envelope parameters (95×65×65 mm, 1.5 mm Al wall, 25 mm fan) added.
    *(done 2026-06-08, PR #42)*
- [x] **`nacelle_servo_bracket.scad`** — U-channel saddle clamp for DS3218MG nacelle tilt servo;
    4× M3×10 SHCS flanges at ±17.5×±8 mm; 10×6 mm lead notch; FOS_shear=85.7. *(done 2026-06-08)*
- [x] **`REVN_BUILD_GUIDE_24IN.md` Phase 3 anti-rework** — spar grub-screw torque sequence
    (0.5 N·m each, before foam pour) with consequence documentation. *(done 2026-06-08)*

- [ ] **`cargo_sect_shell24.scad` — shuttle exterior fairing profiles on Z walls.**
    Canonical Serenity shuttles (Shuttle 1 = Inara's, Shuttle 2) sit just above the wing roots on
    the exterior Z faces of the cargo section. Their outline profiles need to be added as raised
    exterior features at Y≈−273..−213 mm on both Z walls, matching the canonical hull geometry.
    Interior avionics zone (Inara + River dorsal band) coexists — shuttles are exterior, avionics
    interior. Reference the Thingiverse low-detail hull for shuttle fairing geometry.
    **BLOCKS canonical hull fidelity (CLAUDE.md requirement: keep skin geometry true to reference).**

- [ ] **Avionics dorsal access covers / Faraday tray lids for Inara and River bays (two parts).**
    Create `inara_access_cover.scad` and `river_access_cover.scad` (or a single parametric SCAD):
    Cover footprint 105×75 mm with 5 mm shoulder lip seating on hull skin around 95×65 mm opening.
    Copper-foil-lined PETG or 0.5 mm Al sheet; Ø38 mm GPS clearance bore at GPS offset from cover
    centre (Inara: offset −13.3 mm in Z from bay centre; River: offset +0.7 mm in Z from bay centre).
    4× M2 flathead captive screws at ±40 mm (X) × ±25 mm (Z) from cover centre for EMI-seal clamping.
    Must be removable with common hand tools per CLAUDE.md field disassembly requirement.
    Ref: FARADAY_* parameters in cargo_sect_shell24.scad Rev S3; CLAUDE.md §1.4.1.
    Add to Phase 0 print schedule.

- [ ] **Update REVN_BUILD_GUIDE_24IN.md bay layout table** to reflect revised avionics stack
    positions (Inara + River in cargo section dorsal band; Shepherd Book in head section forward;
    Simon in rear cone pre-Phase 11, middle ring post-Phase 11). Current guide Bays A–E are from an
    older layout that does not match the cargo-section dorsal placement in Rev S (formerly
    Rev R — the axis-bug fix in §1.1.1.0a doesn't change the bay positions this item refers to).

- [ ] **Regenerate `cargo_sect_shell24.stl`** from the current Rev S SCAD source (includes the
    Rev R2/Rev S GPS/avionics/nadir-camera axis-bug fix, §1.1.1.0a). Run:
    `openscad -o airframe/stls/fuselage/cargo_sect_shell24.stl
        airframe/openscad/fuselage/cargo/cargo_sect_shell24.scad`
    Verify in slicer: wing mortises at both Z walls; spar bore at X=−70 mm; 8 dorsal boss posts;
    two 62×42 mm dorsal panel openings. Z-range must be 0..163 mm; all features inside hull skin.
    **BLOCKS Phase 0 cargo section printing.**

- [ ] Add motor-mount and DRV8833-tray boss locations to `cargo_sect_shell24.scad` interior
    drawing notes (Phase 1 pre-pour checklist reference).
- [ ] Add SG90 bell-crank boss to inner face of each door panel for pushrod attachment.
    - Export gondola shell to `thingverse-serenity/files-hollowed-18in/`
    - **BLOCKS Phase 8**

###### 1.1.1.2.2 *Wing Root*

##### 1.1.1.3 *Middle Neck*

**Canonical geometry (Rev R1, 2026-06-13):**
The middle section is defined by `airframe/blender-scripts/files-hollowed-24in/middle_shell24_2mm_repaired.stl`
(canonical Blender source) → baked to `airframe/stls/fuselage/middle_shell24_2mm_repaired.stl`.

It is **ONE printed piece** comprising two distinct structural elements:
1. **Outer horseshoe ring** — the U-shaped exterior frame surrounding the middle section, open at −Z (ventral).
    The two lower arms of the horseshoe continue aft as the landing skids into the rear section.
2. **Inner neck** — a tube-like enclosed passage running through the centre of the horseshoe,
    connecting the cargo bay interior to the rear engine room interior within the hull skin.
    Canonically this is a pressurised passage within the ship; in the UAV context it provides
    structural continuity and a wiring/keel routing path through the narrowest hull section.

**Phase 5–10 print state:** inner neck is a closed, uncut tube.
Aft EDF intake scoops (reduced-area radial openings into the inner neck for the 55 mm EDF airflow)
are **DEFERRED to Phase 11** — do not cut or modify the inner neck before Phase 11.

- [x] **Blender canonical source baked** — `middle_shell24_2mm_repaired.stl` (855 328 tri) baked
    2026-06-13; extents X −258.5..−81.6 / Y +130.4..+203.6 / Z +1.3..+166.1 mm. *(done 2026-06-13)*

- [ ] **Slicer verification** — open baked `middle_shell24_2mm_repaired.stl` in slicer and confirm:
    - Both the outer horseshoe ring and inner neck are present as connected geometry
    - No thin-wall violations at neck-to-horseshoe web transitions (min 1.6 mm wall at all points)
    - Inner neck bore is closed (no EDF intake openings)
    - Skid arm geometry at the lower horseshoe legs correctly transitions into the rear section
    - Z-range +1.3..+166.1 mm in hull frame; total height ≈ 165 mm — fits build-volume vertical
    **BLOCKS middle section printing.**

- [ ] **Kaylee's room — PDB mounting in inner neck** — the Kaylee Power Distribution Board
    (Kaylee Rev A1; 75 g) is housed inside the inner neck of the middle section, accessible
    through the open ventral face of the horseshoe ring.  The inner neck central location
    minimises power run lengths to all four nacelles, all four avionics stacks, and the battery.
    Required additions to the Blender middle mesh (or as bonded inserts):
    - 4× M3 standoff boss posts for Kaylee PCB (55×35 mm board; ±20×±12.5 mm pattern from bore centre)
    - Power cable exit notches (6 AWG leads, 4× nacelle ESC runs + avionics BEC tap)
    - Ventilation opening or clearance to allow heat dissipation from TPS54620 regulators
    - Access clearance from horseshoe ventral opening (confirm Kaylee can be inserted and removed
        with hand tools — field disassembly requirement per CLAUDE.md)
    - Confirm inner neck bore dimensions from baked `middle_shell24_2mm_repaired.stl` cross-section
        at hull Y ≈ +165 mm (midpoint of middle section) before adding boss features.
    **BLOCKS middle section Blender mesh update; BLOCKS Kaylee installation.**

- [ ] **CF skid rod channels** — add 4.2 mm bore channel along each horseshoe-to-skid arm (lower
    legs of the horseshoe) in the Blender mesh, coaxial with the matching channels in the rear shell.
    Export updated STL, re-bake, verify watertight.  See §1.1.0a skid task.  **BLOCKS taxi test.**

- [ ] **Simon bay — define avionics bay in the MIDDLE section (moved here from §1.1.1.2, 2026-06-13).**
    Simon's stack (Cape-B-2 + Cape-A-2, 55×35 mm both, 39.2 mm stack height) + Faraday tray (60×40×55 mm)
    mounts in the **middle inner-neck dorsal** interior. Add boss standoffs + dorsal access panel to the
    middle Blender/SCAD source. Verify the inner-neck dorsal band has clearance (middle Z ≈ 1.3..166 mm,
    thin horseshoe section — confirm the inscribed cavity holds the 60×40×55 tray before placing bosses).
    Ref: CLAUDE.md PACE (Simon = alternate watchdog, aft EDF control); shuttle Faraday-fit method in
    `engrave_plaques.py`/cavity-profile check. **BLOCKS Phase 6 full 8-node installation.**

- [ ] **Kaylee room — PDB + battery bay, middle VENTRAL (2026-06-13).**
    The Kaylee power-distribution board and the main battery mount together in the middle section's
    ventral region (the open −Z side of the horseshoe). Define the mounting bay / strap points there;
    keep mass low and central for CG. Coordinate with §1.4.5 (power distribution).

- [ ] **Avionics-bay interior name marks (DEFERRED, 2026-06-13).** Engrave/emboss bay identifiers
    (INARA port shuttle, RIVER stbd shuttle, SHEPHERD head fwd, SIMON middle dorsal, KAYLEE middle
    ventral) on each bay interior. First attempt (flat recessed plaque via `engrave_plaques.py`) did
    not read cleanly on the morph-opened organic cavity walls; pending a method decision (raised letters
    on a flat boss pad, or smooth the bay wall first). Mechanism is watertight and stays inside the 2 mm
    skin. Scripts: `make_bay_text.py`, `engrave_plaques.py`.

- [ ] **Phase 11 — aft EDF intake scoop cuts** — at Phase 11, cut the reduced-area radial scoop
    openings (sized for the 55 mm EDF, ~3,090 mm² total capture at 1.3× duct match) into the inner
    neck to match the resized EDF plenum geometry (`deferred/aft-edf/openscad/neck_intake_frame.scad`).
    These cuts are Phase 11 ONLY — the Phase 5–10 mesh is the closed-neck version.  **Scoop geometry
    must be re-derived for the 55 mm fan — the old 4× scoops were sized for the 120 mm EDF.**

- [ ] **neck_intake_frame.stl (Phase 11)** — `openscad -o neck_intake_frame.stl deferred/aft-edf/openscad/neck_intake_frame.scad`
    - Verify: registration tongues 5 mm depth; intake lips project 6 mm forward
    - Material: CF-PETG; **DEFERRED — BLOCKS Phase 11 only.** STL at `deferred/aft-edf/stls/`.
    - **Requires regeneration for 55 mm intake area (Rev R1 rear-EDF redesign).**

    **Rear intake system (OpenSCAD):**

- [ ] **aft_edf_plenum.stl** — `openscad -o aft_edf_plenum.stl deferred/aft-edf/openscad/aft_edf_plenum.scad`
    - Verify: intake arms feed a 55 mm circular EDF inlet; **add 4 RCS bleed taps (~15% flow split)**
        on the discharge side to the RCS distribution manifold; no self-intersection
    - **DEFERRED — BLOCKS Phase 11 only.** **Requires regeneration: outlet 120 mm → 55 mm and RCS
        bleed taps added (Rev R1 rear-EDF redesign).** Old STL at `deferred/aft-edf/stls/aft_edf_plenum.stl` is superseded.

    **Canonical middle shell (OpenSCAD — belly restored, no belly scoop):**

- [x] **middle_canonical_shell24.stl** — `openscad -o ... serenity/stl/middle_canonical_shell24.scad`
    - Note: NOT the same as `middle_shell24.stl` (which has the obsolete belly intake cut). This is the Rev N canonical belly.

###### 1.1.1.3.1 *Anti-Collision Strobe*

- [ ] Mount ant-collision strobe on belly of middle section in accordance with [REF-FAA-003]

    - [ ] Create cableways from mount point to avionics bay

    - [ ] Wire strobe to led pwd output on Wash cape in Simon's medbay

##### 1.1.1.4 *Rear Engine Cone*

###### 1.1.1.4.1 *Anti-Collision Tail Light*

- [ ] Mount ant-collision steady white tail light on upper pod of rear section in accordance with [REF-FAA-003]

    - [ ] Create cableways from mount point to avionics bay

    - [ ] Wire strobe to led pwd output on Wash cape in Simon's medbay

