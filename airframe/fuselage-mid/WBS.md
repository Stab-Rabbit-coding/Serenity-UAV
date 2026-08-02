# Serenity UAV — Airframe Fuselage — Head/Cargo/Middle Shells, FlightEngineer/Simon Bays Work Breakdown Structure (Detail)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0
**Current design revision:** Rev S (2026-07-04)

> **Detail-holder for the root WBS.** The repository-root [`TODO.md`](../../TODO.md)
> is a compact index — headings, subheadings, and short (<=70-char) checkbox items
> only, per root `AGENTS.md`. This file carries the full task detail for the WBS
> branches the root indexes below. Close an item here first, then check it off in
> the root index as a commit prerequisite (root `AGENTS.md` "Revisions and Version
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
    copper braid in the keel lap joint.  Update Commo/XCVR antenna design accordingly.

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
    - 2× ventral hatch covers: battery 160×60 mm, Flight Engineer 115×100 mm; M2.5 pilots into bonded frames.
    - 2× ventral hatch frames: battery + Flight Engineer; 6 mm CF-PETG wall, West System 105/206 epoxy-bonded to hull.
    - **SUB-TASKS:**
        - [ ] Export individual STLs (set RENDER variable in SCAD): shepherd, inara, river, simon,
            battery, battery_f, flight_engineer, flight_engineer_f → `airframe/stls/fuselage/` — **NOT DONE
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
        - [ ] Bond River's forward post to the port flank at sta 120 mm; dress wire aft to River's Commo J2
        - [ ] Bond Simon's forward post to the starboard flank at sta 120 mm; dress wire aft to Simon's Commo J2
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
    Panel cuts enlarged 55×35 → 62×42 mm; boss offsets updated ±40×±25 → [TBD pending PCB layout — hole pattern must be derived from Pilot.kicad_pcb / XO.kicad_pcb once layout is complete] to match
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

- [ ] Add DRV8833-tray boss locations to `cargo_sect_shell24.scad` interior drawing notes
    (Phase 1 pre-pour checklist reference). **The N20 motor-mount boss is dropped** — the
    winch now mounts on two pedestals, tracked separately in §1.1.1.2.1a.
- [ ] Add SG90 bell-crank boss to inner face of each door panel for pushrod attachment.
    - Export gondola shell to `thingverse-serenity/files-hollowed-18in/`
    - **BLOCKS Phase 8**

###### 1.1.1.2.1a *Cargo Winch — STS3215 Conversion (Rev B, 2026-07-27)*

Retires the Rev P/Q/R N20 winch train and replaces it with an STS3215 serial-bus servo
driving a spool that is **supported at both ends**, behind a **normally-engaged one-way
safety ratchet** with a powerless overload line-shed. Canonical source:
[`docs/CARGO_WINCH_SPECIFICATION.md`](../../docs/CARGO_WINCH_SPECIFICATION.md) **Rev B** —
do not restate its dimensions here.

- [x] **`docs/CARGO_WINCH_SPECIFICATION.md` Rev B authored** *(2026-07-27)*. Rev A (same
    date, first pass) is **withdrawn** — it specified PWM control (the STS3215 is a TTL
    serial-bus servo), invented a 50 lbf design load and 0.25 in line against the airframe's
    real 3.92 N / 0.5 mm figures, described the ratchet as a bidirectional lock rather than
    one-way, and anchored the line to the spool, contradicting the shed requirement.
- [x] **Superseded hardware scrubbed from active files** *(2026-07-27)*:
    `N20-WINCH`, `cargo_winch_motor_mount.stl` (cantilever), `cargo_winch_spool.stl`
    (N20 D-bore + anchor slot) removed from `docs/bom_revR.json`; `make_motor_mount()` /
    `make_winch_spool()` in `generate_cargo_mounts.py` converted to documented
    `NotImplementedError` stubs and dropped from the build list; prose updated in
    `README.md`, root `WBS.md`/`TODO.md`, `airframe/WBS.md`,
    `airframe/VERIFY_PLACEMENT_CHECKLIST.md`, `avionics/observer/WBS.md`,
    `graphical-build-guide/` (REVN guide + flight-phases + SVG task),
    `docs/PHASED_BUILD_GUIDE.md`, `docs/PROTO_PRINT_DAVINCI_JR.md`,
    `docs/AVIONICS_PB2_REDESIGN.md`, `docs/POWER_DISTRIBUTION.md`, `PROJECT_INDEX.md`.
    **`DRV8833-CARGO` + `cargo_drv8833_tray.stl` deliberately RETAINED** — Rev R assigns both
    channels to the door and payload-release SG90s, not the winch.
- [x] **New hardware specified** *(2026-07-27)*: 6 printed parts (2 pedestals, spool r2,
    pawl, dog coupler, fairlead) + 7 purchased refs (`STS3215-WINCH`, `SOL-CATCH-5V`,
    `BRG-MR84ZZ` ×2, `SHAFT-SS-4MM`, `SPRING-PAWL`, `DOWEL-M2-10`, `SS34-CATCH`) added to
    `docs/bom_revR.json` with masses, notes and cost roll-up.

- [x] **BLOCKER RESOLVED via servo supersession, not datasheet recovery (2026-08-02).**
    The STS3215 datasheet remains unreadable, but the servo itself is superseded — see
    §1.1.1.2.1b below. Case envelope, mass, and torque are now published COTS figures for the
    replacement (SPT5425LV, REF-SENSOR-013); stall current remains unverified under the new
    part too (§1.1.1.2.1b).
- [ ] **★ CONTAINMENT — the spool must never leave the cargo bay (spec §3.10).**
    Designating the spool sacrificial (§3.8) made it a planned-degradation part
    sitting directly above clamshell doors that open 180° to free air. Rev B
    retained the axle with a split collar and one M3 pinch screw — **friction
    retention, which root `AGENTS.md` §7 forbids outright for a flight-critical
    joint.** Self-inflicted, and corrected by five positive fixes, all required
    before any flight with a slung load:
    - **FM1** circlip groove + external circlip immediately outboard of each
      pedestal; the pinch screw is demoted to locating/anti-rotation only.
    - **FM2** continuous steel sleeve through the hub bore, bearings pressed into
      the sleeve rather than into printed plastic — total loss of the printed
      material still leaves sleeve + bearings captive on the axle.
    - **FM3** pedestal through-bolts + aluminium backing plates, replacing
      heat-set inserts in printed shell.
    - **FM4** keeper bar spanning both pedestals — independent secondary capture
      that holds even if FM1–FM3 all fail or a retainer is omitted at assembly.
    - **FM5** slip-adjust collar retained captive by the FM1 circlip.
    Energy at stake, from the §107.51(b) 400 ft ceiling ignoring drag: spool alone
    **19.1 J (14.1 ft·lbf)**, full assembly **31.8 J (23.5 ft·lbf)**.
    **Principle: the sacrificial element must fail by *slipping*, never by
    *releasing*** — wear degrades torque transmission, never retention. Containment
    must hold **with the doors open**, which is both the normal cargo-evolution
    state and the only geometry in which a release reaches free air.
- [ ] **Verify the Part 107 dropped-object section number.** REF-FAA-002's
    applied-sections table does not currently include it, so the winch spec
    asserts **no** section number (root `AGENTS.md` §4). Look it up, add it to
    REF-FAA-002 with a validated URL, then state explicitly how a *commanded*
    shed (R5) differs from an *uncommanded* structural release under that text.
    Tracked in `REFERENCES.md` "Open Standards Verification Items".
- [ ] **Containment checks on the assembly and pre-flight cards** — circlips
    seated, keeper bar fitted and torqued, backing plates present, slip-collar
    witness-mark intact. Doors-open inspection.
- [ ] **★ Flight-envelope decision — shed threshold vs manoeuvre envelope.** At
    `F_shed` = 8.0 N a **2.0 g** manoeuvre on the slung payload reaches **0.98×**
    the threshold and **2.5 g sheds the load**. Choose: declare a ≈1.5 g slung-load
    manoeuvre limit (recommended — free, and matches crewed-rotorcraft practice),
    raise `F_shed` to ~12 N (3.06× static, still only 72 % of the 16.64 N excess
    lift), or reduce payload. **A flight-envelope call, not a winch call** — refer
    to `docs/flight_envelope.md`. Blocks the pawl-spring calibration target.
    Spec §4.4.
- [x] **Coupler trade CLOSED — slip clutch, located in the printed spool hub.**
    Rigid dog (A) was rejected (pollutes the threshold with `T_backdrive`), and
    the overrunning clutch (C) was rejected outright (no controlled lowering).
    Putting the friction interface in the **spool hub** rather than in a separate
    component removes `T_backdrive` from `F_shed` entirely — at overload the spool
    breaks free of the servo whatever the gearbox does — and makes the **printed
    spool the sacrificial element**, which is far cheaper to replace than a digital
    servo. A stiff, non-back-drivable servo is now a *benefit*, not a hazard.
    Spec §3.8.
- [ ] **Calibrate `T_slip` = 0.060 N·m (0.61 kgf·cm)** at the spool hub collar —
    1.49× static payload torque, 73 % of shed torque; window is 0.0404–0.0824 N·m.
    Belleville washer on a threaded collar, torque-wrench set, thread-locked and
    witness-marked. Confirm the one surviving back-drive requirement
    **`T_slip` < `T_backdrive`** (measure with the pawl held clear — an inequality
    check now, no longer a go/no-go on R5). Spec §3.8.2.
- [ ] **Set the servo torque ceiling below `T_slip`** — protection layer 1 of 4, so
    routine lifting never reaches the friction interface and the sacrificial hub is
    consumed only by genuine overload events. Spec §3.8.3.
- [ ] **Servo mode: continuous rotation by construction** (Rev C — the STS3215's
    register-selected mode scheme no longer applies; SPT5425LV + LibreServo v2 is
    continuous-rotation by construction once the limit pin is removed, §1.1.1.2.1b).
    Gateway closes position on the AK7455. Confirm LibreServo v2 wire-protocol
    commands (rate, torque-ceiling, readback) against its protocol docs — **no
    command/register value is invented in the spec**. Spec §3.9.
- [ ] **Mark the spool a consumable** — wear item in the build guide, inspection
    interval, slip witness-mark, spare in the field kit; hand-tool replacement per
    root `AGENTS.md` §7.
- [ ] **AK7455 spool encoder integration (spec §3.7.3).** Diametric-magnet pocket in
    the port flange hub, off-axis (the fixed axle occupies the centreline); mates the
    gateway's existing `J_ENC` pigtail on its dedicated SPI bus — no board change and
    no new part number [REF-SENSOR-008]. Confirm flux at the IC for the chosen
    magnet/gap (same bench item already open for the nacelle encoders). Firmware:
    ≥ 1 kHz sampling, turn-accumulation with a `turns_invalid` guard rather than a
    guessed count — a snag release reaches ~5,030 rpm at the spool and outruns
    wrap-tracking below ~840 Hz. The servo's own encoder is a cross-check only:
    servo-vs-spool divergence indicates a slipped clutch or a stripped dog.
- [ ] **Implement the six winch STLs** in `generate_cargo_mounts.py` (`WINCH_REV_S_PARTS`).
    They are dimensionally interdependent — axle span, bearing seats and ratchet clearance all
    key off the servo envelope — so implement together, then mesh-validate per root
    `AGENTS.md` §7. Blocked on the gate above.
- [ ] **Pedestal mounting stations in `cargo_sect_shell24.scad`.** The retired mount used 4× M2
    self-taps into the gondola *ceiling*; the two pedestals need real M3 heat-set boss stations
    on the bay floor, FreeCAD-verified against the cargo-door 180° swing envelope
    (`generate_cargo_doors.py`) and clear of `CARGO_CAM_POS` / the Observer nadir bosses.
- [ ] **RS-485 differential bus wiring (Rev C — supersedes the Rev B half-duplex TTL item).**
    LibreServo v2 needs a true differential RS-485 pair, not the STS3215's single-wire
    half-duplex TTL scheme `FLEX_TTL_GPIO` was sized for. Decide: add a local RS-485
    transceiver fed from `J_FLEX.FLEX_UART_TX/RX`, or extend the gateway's own isolated
    RS-485 trunk (ISOW1412) to this drop — not decided in the spec. Cross-ref
    `avionics/WBS.md`, `avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md`.
- [ ] **Catch solenoid drive circuit.** AO3400 N-FET + 100 Ω gate + **10 kΩ gate pull-down**
    (undriven/resetting MCU must leave the catch ENGAGED) + SS34 flyback across the coil.
- [ ] **Bench-calibrate the ratchet slip threshold to 8.0 N ± 1.0 N** measured at the line, via
    the set-screw spring seat; then verify over ≥ 100 lock/release cycles for wear. The 8.0 N
    figure is derived (48 % of the 16.64 N available excess lift), not measured.
- [ ] **Line-shed test.** Confirm the line actually runs clear of drum and fairlead under load.
    The ~0.7 N capstan retention on the last two turns is analytic, not measured. Verify the
    inboard end is **not** anchored.
- [ ] **Firmware — winch state machine** (Simon payload-primary, gateway-side control).
    `WINCH_STATUS` / `WINCH_COMMAND` frames, TPM-signed per [REF-NIST-001 §2.1]; STS3215 bus
    driver; HX711 re-hosted from Cape-B to the gateway; Shepherd watchdog cuts RAIL-2 on
    heartbeat timeout (which *engages* the catch). Bus IDs assigned in firmware, not in the
    spec. Cross-ref `avionics/firmware/WBS.md`.
- [ ] **Re-run the §6 mass/CG table** once the SPT5425LV+LibreServo v2 unit is bench-weighed;
    propagate to `docs/flight_envelope.md` if AUW moves materially.
- [ ] *(Optional, out of scope for this change)* Move the door/release SG90s onto the
    gateway's spare `FLEX_PWM_IO` and retire `DRV8833-CARGO` + `cargo_drv8833_tray.stl`.

**BLOCKS:** Phase 8 cargo winch assembly; `build_guide_23_winch_latch.svg` rebuild;
Flight Engineer RAIL-2 third BEC channel (`docs/POWER_DISTRIBUTION.md` §11.1).

###### 1.1.1.2.1b *Servo Fleet Standardisation — SPT5425LV + LibreServo v2 (Rev C, 2026-08-02)*

Supersedes §1.1.1.2.1a's STS3215 servo selection and extends the same treatment to the
2× nacelle tilt servos (previously DS3218MG, uncited). All three high-torque servos on the
airframe now share one physical part (SPT5425LV, REF-SENSOR-013) running one open-source
control board (LibreServo v2, REF-SENSOR-014), each with the servo's internal
rotation-limiting pin removed. Canonical source:
[`docs/CARGO_WINCH_SPECIFICATION.md`](../../docs/CARGO_WINCH_SPECIFICATION.md) **Rev C**
§3.1/§3.1.1/§3.1.2/§3.9/§5.1 (winch-specific) and `REFERENCES.md` "Servo Fleet
Standardisation, 2026-08-02" (fleet-wide rationale) — do not restate their content here.

- [x] **`docs/CARGO_WINCH_SPECIFICATION.md` Rev C authored** *(2026-08-02)* — servo section
    rewrite; STS3215-era open items (datasheet gate, half-duplex TTL wiring, mode-register
    semantics) closed or superseded by SPT5425LV/LibreServo v2-specific equivalents.
- [x] **`REFERENCES.md` updated** *(2026-08-02)* — REF-SENSOR-012 (STS3215) marked
    SUPERSEDED; REF-SENSOR-013 (SPT5425LV), REF-SENSOR-014 (LibreServo v2), REF-SENSOR-015
    (OpenServoCore, for the SG90 cargo servos — separate board, separate servo class) added
    with sourced specifications; four new rows added to "Open Standards Verification Items."
- [x] **Nacelle tilt bracket updated** *(2026-08-02)* — `nacelle_servo_bracket.scad`
    `SERVO_BODY_X`/`SERVO_BODY_Z` updated 40.0/38.0 → 40.5/40.5 mm (SPT5425LV envelope);
    `SERVO_BODY_Y` unchanged at 20.0 mm; stall-torque/FOS check re-run at 2.55 N·m
    (26 kgf·cm @ 6 V) — FOS 82.4, still far above the 4.0 design-judgment target.
- [x] **`generate_cargo_mounts.py` comments updated** *(2026-08-02)* — case-envelope gate
    that blocked `make_winch_pedestal_port()` under the STS3215 selection is resolved
    (SPT5425LV envelope is a published figure); SG90 bracket docstring notes the
    OpenServoCore control board and its pre-production status.
- [ ] **★ Bench-verify the SPT5425LV/LibreServo v2 conversion.** Neither sourced listing
    publishes stall current or the exact rotation-pin removal procedure. Blocks final RAIL-2
    sizing (`docs/POWER_DISTRIBUTION.md` §3.2.1) and the nacelle-tilt servo rail, and the
    build-guide step for pin removal. Do not fabricate either figure.
- [ ] **RS-485 gateway integration (both winch and nacelle-tilt applications).** LibreServo
    v2's differential RS-485 bus has no local transceiver on `CAN-PERIPH-GW-1`'s `J_FLEX`
    header (which was sized for the STS3215's single-wire half-duplex TTL scheme). Decide:
    add a transceiver fed from `FLEX_UART_TX/RX`, or extend the gateway's own isolated
    RS-485 uplink trunk (ISOW1412) to this local servo drop. Cross-ref `avionics/WBS.md`,
    `avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md`.
- [ ] **Nacelle tilt firmware — command scheme change.** Pilot's servo-PWM generation
    (`avionics/firmware/WBS.md` §4.2) moves to LibreServo v2's RS-485 protocol; the servo's
    real range limit stays the external CF-PETG hard-stop blocks in the gear train
    (`docs/NOZZLE_DRIVE_TRADE.md`), not the (now-removed) internal servo pin — firmware still
    needs its own soft-limit enforcement, not a hardware guarantee from the servo alone.
- [ ] **`current-specification/bom_revS.json`/`.csv` reconciliation.** These files still
    carried the retired N20 winch train (never updated to STS3215 under Rev B); reconciled
    directly to the Rev C SPT5425LV/LibreServo v2 state as part of this change rather than
    passing through an intermediate STS3215 BOM entry that was never accurate to begin with.
- [ ] **OpenServoCore maturity re-check before SG90 procurement.** Upstream project status
    at time of writing is "in active development, nothing here is shippable yet," hardware
    validated to rev B only. Re-check `github.com/OpenServoCore/open-servo-core` before
    ordering in flight-article quantity.

**BLOCKS:** Same as §1.1.1.2.1a above, plus Pilot's nacelle-tilt servo firmware
(`avionics/firmware/WBS.md` §4.2) and the RS-485 gateway decision.

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

- [ ] **Flight Engineer's room — PDB mounting in inner neck** — the Flight Engineer Power Distribution Board
    (Flight Engineer Rev A1; 75 g) is housed inside the inner neck of the middle section, accessible
    through the open ventral face of the horseshoe ring.  The inner neck central location
    minimises power run lengths to all four nacelles, all four avionics stacks, and the battery.
    Required additions to the Blender middle mesh (or as bonded inserts):
    - 4× M3 standoff boss posts for Flight Engineer PCB (55×35 mm board; ±20×±12.5 mm pattern from bore centre)
    - Power cable exit notches (6 AWG leads, 4× nacelle ESC runs + avionics BEC tap)
    - Ventilation opening or clearance to allow heat dissipation from TPS54620 regulators
    - Access clearance from horseshoe ventral opening (confirm Flight Engineer can be inserted and removed
        with hand tools — field disassembly requirement per CLAUDE.md)
    - Confirm inner neck bore dimensions from baked `middle_shell24_2mm_repaired.stl` cross-section
        at hull Y ≈ +165 mm (midpoint of middle section) before adding boss features.
    **BLOCKS middle section Blender mesh update; BLOCKS Flight Engineer installation.**

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

- [ ] **Flight Engineer room — PDB + battery bay, middle VENTRAL (2026-06-13).**
    The Flight Engineer power-distribution board and the main battery mount together in the middle section's
    ventral region (the open −Z side of the horseshoe). Define the mounting bay / strap points there;
    keep mass low and central for CG. Coordinate with §1.4.5 (power distribution).

- [ ] **Avionics-bay interior name marks (DEFERRED, 2026-06-13).** Engrave/emboss bay identifiers
    (INARA port shuttle, RIVER stbd shuttle, SHEPHERD head fwd, SIMON middle dorsal, FLIGHT ENGINEER middle
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

    - [ ] Wire strobe to led pwd output on Pilot cape in Simon's medbay

##### 1.1.1.4 *Rear Engine Cone*

###### 1.1.1.4.1 *Anti-Collision Tail Light*

- [ ] Mount ant-collision steady white tail light on upper pod of rear section in accordance with [REF-FAA-003]

    - [ ] Create cableways from mount point to avionics bay

    - [ ] Wire strobe to led pwd output on Pilot cape in Simon's medbay

