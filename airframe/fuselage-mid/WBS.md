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
            each GPS with its bay/cover center (= `BAY_SEP_X`/2). The ~46 mm-wide (OML-trimmed)
            cover only keeps a Ø38 bore fully enclosed if the antenna is within ~±4 mm of the
            cover center; at the old 30 mm it sat 7.5 mm inboard and the bore broke the cover's
            inboard edge (scallop). Re-rendered + verified: GPS bore is now a **fully-enclosed
            interior hole** (6 section loops = outer + 4 M3 + 1 GPS; single watertight body;
            `inara_access_cover.stl` 4604 mm³, `river_access_cover.stl` 4456 mm³; 26 mm to each
            cover edge, 7 mm bore margin). New GPS center-to-center = 75 mm; Ø44 retention rings
            still clear (31 mm gap). VERIFY-in-slicer: confirm each antenna still lands on flat
            enough dorsal skin at the outboard station and the SMA pocket clears the Faraday
            tray below.
        - [x] **M3 bore positions now match the shell boss pattern — RESOLVED 2026-07-06.**
            The dorsal-Z covers cut their 4× M3 bores at ±`AVZ_SCREW_DX`(15, X) ×
            `AVZ_SCREW_DY`(25, Y) = `cargo_sect_shell24.scad` `AVINICS_BOSS_DX/DY` exactly
            (was mismatched 25/15 in the wrong X-Z axes). Verified geometrically from the
            rendered STL: bore centers at (±15, ±25) mm, Ø3.3 M3 clearance. (Shepherd/Simon
            covers stay on the legacy Y-normal `av_cover_dorsal` until the head/middle
            avionics bays get the same dorsal-axis fix — the still-open head/middle
            axis-bug items in this section.)

- [x] **49 MHz (Part 15 §15.235) wire posts** — `airframe/openscad/fuselage/rcrs49_wire_post.scad` created 2026-06-11.
    Single `wire_post()` module: 12×12×2 mm PETG base, 8×8×7 mm mast, Ø1.5 mm athwartships wire-retention bore at 2 mm from top.
    **Relocated 2026-06-22 (§1.4.2):** dorsal-centerline mount superseded — print FOUR posts (two antennas, two posts each):
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

- [x] **★ CARGO-03 — the wing root mortise does not penetrate the bulkhead.**
    **CLOSED 2026-08-24.**
    *(found 2026-08-23 while checking that the nacelle ESC cableway is not blocked,
    owner direction; gated by `tools/wing_root_deconflict.py`)*  **BLOCKS wing
    attachment, the ESC cableway, and the cargo shell print.**

    `merge_cargo_interior.py` cuts the two wing root mortises as
    `box(PORT_INB + 1.0, PORT_OUTB - 10.0, …)` = hull **X −99…−70** port and
    **X −270…−241** starboard, described in the source as cutting "through each
    wall".  It does not.  At the mortise station (Y +57.5, Z +62.5) the port wall
    material actually lies at **X −115…−99** — the cut begins exactly where the
    wall *ends* and runs outboard into free air.  Swept corridor test, from well
    inboard of the wall to well outboard of it:

    | Penetration | Cut X span | Material left in the corridor | Verdict |
    | --- | --- | --- | --- |
    | wing root mortise, port | −99.0…−70.0 | **1 781.7 mm³** | **BLIND** |
    | wing root mortise, stbd | −270.0…−241.0 | **1 676.0 mm³** | **BLIND** |
    | spar bore, port | −270.0…−70.0 | 0.0 mm³ | THROUGH |
    | spar bore, stbd | −270.0…−70.0 | 0.0 mm³ | THROUGH |

    The spar bore is cut across the **full** lateral span, so it does pass through;
    the mortise is the only wing-root penetration sized to a local X band, and that
    band is wrong.  Note the trap this hid behind: probing *inside* the cut region
    reports 0 mm³ of material and looks correct — emptiness proves nothing when the
    cut is outboard of the wall.  Only the swept corridor exposes it, which is why
    the check now lives in a tool rather than a one-off probe.

    **Consequences.**  The wing root tenon cannot enter; the 40 A EDF ESC conduit
    has no path into the fuselage (CARGO-04); and any prior "mortise cut verified"
    claim rests on a region test, not a through test.  This predates Rev S1b —
    `WING_MORT_Y` (0.50 chord) and `WING_ROOT_Z` were untouched by that change, so
    the defect has been latent since the mortises were first cut.

    **FIXED 2026-08-24.**  Both mortise cutters now span the same inboard
    references the Rev S1c harness ports already derived for this wall
    (`WING_HARNESS_INB_PORT` −125.0 / `WING_HARNESS_INB_STBD` −213.0, "past the
    −115.2 encoder-line wall") out to `PORT_OUTB` / `STBD_OUTB`.  One measured
    fact now drives every wing-root penetration instead of three different
    guesses.  Re-merged and published; swept-corridor test on the published shell:

    | Penetration | Material left in the corridor | Verdict |
    | --- | --- | --- |
    | wing root mortise, port | **0.0 mm³** (was 1 682.8) | **THROUGH** |
    | wing root mortise, stbd | **0.0 mm³** (was 1 643.8) | **THROUGH** |

    `PORT_INB`/`PORT_OUTB` are deep-embed spans for **bosses** and were never the
    wall; treating them as the wall is what caused this, and the fix removes that
    conflation rather than patching the numbers.

    **CARGO-03b — and the tenon that enters it is on a different datum. CLOSED 2026-08-24.**
    *(owner direction 2026-08-23: the wing root tenon has to be accounted for
    alongside the bearing seat.)*  The mortise is only half the joint;
    `wings_s1223_revo.scad` `fuselage_root_tab()` is the other half.  It fits in Y
    and fouls in Z:

    | Axis | Tenon span | Mortise span | Clearance each side |
    | --- | --- | --- | --- |
    | Y (chordwise) | +42.50…+72.50 | +42.10…+72.90 | +0.40 / +0.40 — correct |
    | Z (thickness) | +48.01…+68.01 | +52.10…+72.90 | **−4.09** / +4.89 — **FOULS** |

    Root cause is a **datum disagreement, not a size error**: `fuselage_root_tab()`
    centres the tenon on the wing **chord line** (hull Z **+58.01**), while
    `merge_cargo_interior.py` centres the mortise on **`WING_ROOT_Z`** (hull Z
    **+62.50**).  The two are 4.49 mm apart, against a 0.4 mm design clearance, so
    the tenon's lower 4.09 mm lands on solid wall.  The sizes themselves are right
    — 30.0 × 20.0 tenon in a 30.8 × 20.8 mortise is a sensible 0.4 mm/side fit.
    All three `WING_ROOT_TAB_*` constants still carry their original `VERIFY`
    comments in the SCAD; they were flagged as unchecked when written and never
    were.  Pick **one** datum for the joint and drive both files from it.

    **FIXED 2026-08-24 — the chord line is now the single datum.**
    `WING_ROOT_Z` 62.5 → `WING_CHORD_LINE_Z` (58.01), so the mortise is centred
    where `fuselage_root_tab()` already centres the tenon.  The chord line won
    because the tenon is a *wing* feature and the chord line is the wing's own
    datum; `WING_ROOT_Z` was a fuselage-side number with no geometric claim on the
    joint.  Nothing else reads it — the spar bore and the servo pad are both
    spar-relative — so the move disturbs nothing.  Measured after the re-cut:

    | Axis | Tenon span | Mortise span | Clearance each side |
    | --- | --- | --- | --- |
    | Y | +42.50…+72.50 | +42.10…+72.90 | +0.40 / +0.40 |
    | Z | +48.01…+68.01 | +47.61…+68.41 | **+0.40 / +0.40** |

    The joint now has the symmetric 0.4 mm/side fit its sizes were always chosen
    for.

    **Tenon depth is fine.**  Measured wall face at the mortise station is hull
    X −99.0 (port); a 12 mm `WING_ROOT_TAB_L` reaches X −111.0, still inside the
    wall band (−115…−99), so the tenon does **not** protrude into the cargo bay and
    clears the servo body by 10.66 mm and its horn swing by 12.66 mm.

    **Tenon vs the spar bearing seat — 0.23 mm, and that is the real number.**
    The tenon's forward face sits at 49.5 mm chordwise; the Rev S1b spar bore's aft
    edge sits at 45.15 + 4.15 = 49.3 mm.  Measured gap **0.226 mm** to the bore and
    **0.376 mm** to the spar tube itself.  Before Rev S1b the spar was at 0.171 c
    and the gap was ~23 mm; moving it to 0.35 c closed it to nothing.  At that
    spacing there is no material between the rotating bearing seat and the tenon's
    load-bearing face — treat it as zero and resolve it with the datum fix, because
    any correction that moves the tenon aft or the seat forward consumes it.

    **The tenon is not a plain block** — `wing_one_side()` drills the EDF ESC
    conduits straight through it axially ("tenon pass-through"), grooving its crown
    while the lower ~30 × 15 mm stays solid.  With those modelled, both ESC conduits
    pass the tenon cleanly (0.0 mm³); the blockage in CARGO-04 is the wall, not the
    wing.

    **CARGO-03c — the tenon is a STRUCTURAL joint element, and it has never been
    sized as one.** *(owner, 2026-08-23: "that mortise/tenon joint provides part of
    the structural joint at the wing root, since the wings don't rotate with the
    nacelles.")*  This contradicts `fuselage_root_tab()`'s own comment — "The tab
    provides radial restraint; the CF spar carries spanwise load" — which was
    written when the spar carried through.  Under SPAR-01 it does not: spanwise
    load terminates at the wall, and the tenon is part of how it gets there.
    **Correct that comment when the tenon is re-datumed.**

    Quantified by `tools/wing_spar_carrythrough.py` (tip bearing to root face
    88.0 mm; the wing is supported at the tenon and at the wingtip bearing, so
    whatever the spar hands the wing at the tip, the tenon reacts at the root):

    | Case | R_tip | Tenon shear | Tenon moment | Bearing stress |
    | --- | --- | --- | --- | --- |
    | limit (4 g) | 110.6 N | 110.6 N (24.9 lbf) | 9.74 N·m | 6.76 MPa |
    | ultimate | 165.9 N | 165.9 N (37.3 lbf) | 14.60 N·m | **10.14 MPa** |

    Bearing stress assumes the moment is reacted as a couple on the tenon's top and
    bottom faces over the 12 mm insertion, effective arm ⅔ of depth, bearing area
    = width × half depth.

    **The problem is that no CF-PETG bearing allowable exists in this repository.**
    The only CF-PETG number it carries is ≈5 MPa, and that is **bond**-limited
    (`docs/structural_analysis.md` §7.3), not bearing — against it the tenon is
    under-strength at FOS 0.49.  Bearing on a printed tenon in a printed slot is a
    different mode and almost certainly a higher allowable, but inventing one is
    exactly what root `AGENTS.md` §4 forbids.  So the sizing is inverted instead:
    for the §3 joint FOS target of **4.0** at the present 12 mm insertion the
    bearing allowable must be **≥ 40.6 MPa**; otherwise the depth has to grow:

    Bearing stress falls as **1/(W · L²)** — insertion depth is a *quadratic*
    lever, width only a *linear* one.  Both are capped by what the airframe will
    physically accept, measured by bisection against real parts in
    `tools/wing_root_deconflict.py` `max_tenon_envelope()`:

    - **Max width 39.2 mm.**  The forward face cannot move at all — the spar bore's
      aft edge leaves **0.20 mm** — so every millimetre of width has to be taken
      aft, and aft runs out at hull Y +81.7 against the **aft landing-gear bay**.
    - **Max insertion 20.1 mm.**  Past the ~16 mm wall band the tenon protrudes
      into the bay; it stays clear of the servo, both gear bays and the avionics
      bay, and what finally stops it is the **CARGO-01 payload envelope** at
      X −119.1.  Staying buried in the wall instead caps it at 16.0 mm.

    | If the coupon test returns | Depth @ W = 30 (present) | Depth @ W = 39.2 (max) | Verdict |
    | --- | --- | --- | --- |
    | 5 MPa | 34.2 mm | 29.9 mm | **impossible** — over max depth even at max width |
    | 10 MPa | 24.2 mm | 21.1 mm | **impossible** — over max depth even at max width |
    | 15 MPa | 19.7 mm | 17.3 mm | fits, deeper tenon |
    | 20 MPa | 17.1 mm | 14.9 mm | fits, deeper tenon |
    | 30 MPa | 14.0 mm | 12.2 mm | fits, deeper tenon |
    | 40.6 MPa | 12.0 mm | 10.5 mm | fits as-built |
    | 60 MPa | 9.9 mm | 8.6 mm | fits as-built |

    **The maximum tenon this airframe accepts is 39.2 × 20.1 mm (width ×
    insertion).**  At that size the joint reaches FOS 4.0 only if the measured
    bearing allowable is **≥ 11.1 MPa** — that number is the hard floor the coupon
    test has to clear.  Below it the tenon cannot be grown into compliance at all
    and the joint needs a different answer: a bonded doubler, a second tenon
    forward of the spar, or a metal insert.

    Note how little the width buys: going from 30 → 39.2 mm, the entire aft room
    available, takes only **13 %** off the required depth, because width enters
    linearly while depth enters squared.  Width is the lever to reach for only when
    depth is already against the payload envelope — i.e. between roughly 11 and
    15 MPa, where it is the difference between feasible and not.

    **DECISION RULE (owner, 2026-08-23): if CF-PETG cannot be sourced at ≥ 15 MPa
    fusion strength, the joint gets a second spar instead of a bigger tenon.**
    "Fusion strength" is the right property to name — the tenon reacts its couple
    on faces loaded across the print layers, so interlayer fusion governs, not bulk
    compressive.  15 MPa is a sound threshold: it is the first row in the table
    above that fits (19.7 mm at the present width, 17.3 mm at maximum width, both
    inside the 20.1 mm cap), and it sits above the 11.1 mm-floor with enough room
    that the joint is not built on the last millimetre of envelope.

    **The fallback is feasible, and it must go FORWARD of the main spar.**  First
    pass, Ø6 assumed, ultimate root moment 14.60 N·m, couple force = M / separation:

    | Station (mm from LE) | Separation from main spar | Couple force | Min bore wall | Nearest feature |
    | --- | --- | --- | --- | --- |
    | **14.0** | 31.15 mm | **469 N** | **3.23 mm** | Hall conduit, +11.25 mm |
    | 18.0 | 27.15 mm | 538 N | 4.14 mm | Hall conduit, +7.25 mm |
    | 20.0 | 25.15 mm | 581 N | 4.51 mm | Hall conduit, +5.25 mm |
    | 24.0 | 21.15 mm | 690 N | 5.10 mm | Hall conduit, +1.25 mm |
    | 85.0 | 39.85 mm | 366 N | **−1.69 mm** | tenon, +2.50 mm |
    | 90.0 | 44.85 mm | 326 N | **−2.37 mm** | tenon, +7.50 mm |

    Aft stations are **not available at any separation** — the section is too thin
    behind the tenon and the bore breaks out of the skin (negative wall).  Forward
    works, and further forward is better because separation grows and the force
    falls; **14.0 mm** is the pick, giving the largest separation still on a healthy
    3.23 mm bore wall and 11 mm of room to the Hall conduit at its new 30 mm
    station.

    **Why this actually fixes the problem, where a bigger tenon does not.**  The
    tenon reacts a couple on shallow faces; a rod reacts shear along an embedded
    length, and the wall can give it the same deep boss the main spar already has
    (`PORT_INB` −100 to `PORT_OUTB` −60 = 40 mm of embed):

    | Rod | Embed | Bearing | vs the tenon's 10.14 MPa |
    | --- | --- | --- | --- |
    | Ø6 | 16 mm | 4.88 MPa | 2.1× better |
    | Ø6 | 40 mm | 1.95 MPa | 5.2× better |
    | Ø8 | 25 mm | 2.34 MPa | 4.3× better |
    | **Ø8** | **40 mm** | **1.46 MPa** | **6.9× better** |

    At Ø8 × 40 mm embed the FOS 4.0 target needs an allowable of only **≈5.9 MPa**,
    against 40.6 MPa for the present tenon — so the second spar takes the joint out
    of the fusion-strength question almost entirely, and would clear even the
    repository's pessimistic 5 MPa bond-limited figure at FOS 3.4.

    It also **restores the tenon to the job its own comment already claims** —
    radial restraint and location, not moment reaction — which means
    `fuselage_root_tab()`'s wording becomes correct again rather than needing the
    CARGO-03c correction.

    **Costs to carry if this branch is taken:** 2 × 4130 rod (~24 g each at 100 mm
    of Ø8 × 1.5, so ≈**48 g / 0.106 lbm** added), 2 more wall bosses, 2 more wing
    bores, and a second bore through the tenon region — and the rod length and
    embed both still need sizing, since the table above assumes 40 mm by analogy
    with the main spar rather than deriving it.

    **Open:** add CF-PETG **fusion/bearing** coupons to the LG-11 coupon-test
    schedule (root `TODO.md` §1.1.4 already carries "Coupon-test CF-PETG"),
    printed in the tenon's own layer orientation.  **≥ 15 MPa → grow the tenon per
    the table; < 15 MPa → second spar at 14 mm.**  Re-run
    `tools/wing_spar_carrythrough.py` either way.

    **BUILT 2026-08-24, U5/KTD1: two-rod system, not a single rod vs. the
    tenon.** A feasibility pass against the corrected S1223 geometry (WING-01
    fix) found a matching Ø8.2 mm AFT rod does not fit anywhere aft of the
    main spar (spar bore aft edge 49.30 mm and the Hall conduit's fixed
    52.25..55.75 mm span leave no room); a smaller **Ø6.2 mm aft rod** fits
    **root-only** at **62.0 mm from LE** (picked within the 60..62 mm feasible
    band for maximum clearance margin to the Hall conduit's trailing edge —
    `tools/wing_spar_station_fit.py`), with the forward Ø8.2 mm rod unchanged
    at 14.0 mm. Both rods are root-only embeds (not full-span like the main
    spar — a root-reacting tie rod has no structural reason to reach the
    tip).

    The couple-force split is **not** the single-rod `F = M / separation from
    spar` method above: with two dedicated rods and no third reaction (the
    main spar rides in a rotating CLEARANCE bore at the wing root and reacts
    no moment about this axis), pure statics for two pin reactions gives
    **equal-magnitude forces**, `F = M / (rod-to-rod separation)`, independent
    of the spar's position — `tools/wing_spar_carrythrough.py
    report_two_rod_couple()`:

    | Rod | Station | D (nominal) | Embed | F (ultimate) | Bearing | FOS vs 5 MPa |
    | --- | --- | --- | --- | --- | --- | --- |
    | fwd | 14.0 mm | 8 mm | 40 mm | 304.3 N | 0.951 MPa | **5.26** |
    | aft | 62.0 mm | 6 mm | 42 mm | 304.3 N | 1.207 MPa | **4.14** |

    (48.00 mm rod-to-rod separation; ultimate root moment 14.60 N·m unchanged
    from the table above.) Both clear the §3 FOS 4.0 target against the
    existing 5 MPa bond-limited CF-PETG allowable — the aft rod needed its
    embed bumped from the WBS-convention 40 mm to 42 mm to clear (at 40 mm,
    FOS is 3.945, just under target).  No new coupon data required.

    **REF-MAT-001 added 2026-08-25** (`REFERENCES.md`) — the first peer-
    reviewed data point for CF-PETG in this repository (Batista et al. 2023,
    *Appl. Sci.* 13(23), 12701, ASTM D695 bulk compressive strength on 20%
    short-CF-reinforced PETG, ≈47–60 MPa).  It does not change anything
    above — bulk unnotched compression is not the bearing-in-a-hole mode
    either the tenon or the tie rods actually see, so it is not substituted
    into the FOS figures here — but it is real evidence the `enlarged_tenon`
    alternative's ≥11.1–40.6 MPa bar is plausibly clearable, which the
    coupon-test decision is still the correct way to confirm.

    **The tenon is traded out of the load path entirely** (not merely
    "restored" pending a coupon result, as the single-rod branch above
    described) — `fuselage_root_tab()` is now a pure locating/index feature,
    gated behind `TENON_LOAD_PATH = "two_rod"` in
    `wings_s1223_revo.scad` (default); the enlarged-tenon sizing above stays
    documented and buildable under `TENON_LOAD_PATH = "enlarged_tenon"` if a
    future coupon clears ≥ 15 MPa. Geometry: `wings_s1223_revo.scad`
    (`ROD_FWD_*`/`ROD_AFT_*`, `wing_root_tie_rod_fwd_bore()`/
    `_aft_bore()`), `merge_cargo_interior.py` (`ROD_FWD_*`/`ROD_AFT_*`
    wall bosses, mirroring the `PORT_INB`/`PORT_OUTB` main-spar-boss embed
    pattern — the forward boss's fuselage-side embed is 41 mm, not 40, to
    avoid an exact end-cap coincidence with the main spar boss that produced
    a non-manifold seam in the merged shell). CARGO-03c is CLOSED under this
    branch; the coupon test remains open only to *enable* the
    `enlarged_tenon` alternative, not to close this one.

- [x] **CARGO-04 — the aft EDF ESC conduit is blocked, and the Hall conduit runs
    inside the rotating spar. CLOSED 2026-08-24.** *(found 2026-08-23 with CARGO-03; same tool)*
    **BLOCKS the nacelle ESC harness and the tilt-encoder harness.**

    Owner requirement: the nacelle ESC and nav-light cableways must stay open.  The
    nav light is satisfied — it routes through the spar's ~5 mm ID and the spar bore
    is verified THROUGH (above).  The other two are not:

    | Route | Station (hull) | Obstruction | Blocked |
    | --- | --- | --- | --- |
    | EDF ESC conduit #1 (fwd) | Y +50.92, Z +66.92, Ø7 | — | clear |
    | EDF ESC conduit #2 (aft) | Y +58.92, Z +66.92, Ø7 | published shell | **172.3 / 172.9 mm³** |
    | Hall/encoder conduit | Y +35.57, Z +68.47, Ø3.5 | **rotating spar tube** | **468.1 / 450.1 mm³** |
    | spar bore / nav-light | Y +38.15, Z +68.42, Ø8.3 | — | clear |

    **EDF #2** is blocked by the same uncut wall as CARGO-03 (the blockage sits at
    X −112…−99 port, inboard of where the mortise cut starts), so fixing CARGO-03
    should clear it — **re-verify, do not assume**.  Both conduits lie inside the
    mortise footprint in Y and Z, so a correctly-cut mortise is their intended path
    and no separate penetration is needed.

    **The Hall conduit is a genuine Rev S1b regression.**  `HALL_CABLE_XFR` = 0.33 c
    and the spar moved to `SPAR_BORE_STATION` = 45.15 mm = 0.35 c — 2.58 mm apart,
    against a 4.15 mm spar radius plus 1.75 mm conduit radius, so the conduit lies
    **entirely inside the spar bore** and the rotating spar occupies it.  Before
    Rev S1b the spar sat at 0.171 c and the two were well separated; the S1b note in
    `wings_s1223_revo.scad` lists its consequential fixes but the Hall conduit is not
    among them.  Its own comment still reads "HALL_CABLE_XFR = 0.30c", which also
    disagrees with the 0.33 in force — fix the comment with the station.

    **RESOLVED 2026-08-23 by merging `feat/wing-spar-s1c-cableway-reroute`.**
    The owner's instruction — route the Hall 4-core **aft of the spar**, because
    the steel spar then shields it from the power feeds — was correct, and my
    analysis of it was wrong.  I evaluated "aft of the spar" against the EDF pair
    where it *then* sat (0.48 c, aft of the spar) and concluded the shielding could
    only work forward.  That branch had already moved the EDF pair **forward**, and
    with both moves applied the ordering is:

    | Feature | Station (mm from LE) | Hull Y |
    | --- | --- | --- |
    | EDF #1 — 40 A POWER | 22.75 | +15.75 |
    | EDF #2 — signal | 32.25 | +25.25 |
    | **spar bore** | **41.00…49.30** | **+38.15** |
    | Hall/encoder | 54.00 | +47.00 |

    The ferromagnetic spar now sits **between** the power pair and the sensor line,
    exactly as intended, and the Hall conduit is aft of it exactly as instructed.
    My Rev S1c edit (`HALL_CABLE_XFR` → 0.23256, 30 mm **forward**) is superseded
    and was dropped in the merge.

    The branch's reasoning is also better than mine on a point I missed entirely:
    both conduits are now **constant-mm stations**, matching the spar's own law.
    As chord-fraction bores they converged on the constant-mm spar as the chord
    tapered 129 → 93 mm, so the EDF pair entered the spar bore from 29.6 % span
    outboard and merged with it at the tip — a defect invisible at the root, which
    is the only station I checked.  `tools/wing_internal_clearance.py` (from that
    branch) samples the whole span and reports **PASS** on the merged source.

    **Two consequences the merge creates, both open:**

    1. **The Hall conduit now needs a tenon pass-through.**  At 54.0 mm it lands
        inside the tenon's chordwise span (49.5…79.5), and `wing_one_side()` cuts
        pass-throughs only for the EDF pair — `tools/wing_root_deconflict.py`
        reports the tenon blocking it by **65.0 mm³**.  Cut it the same way the
        EDF bores are cut.  (This is the consequence flagged when the aft option
        was first tabled; it has now materialised.)
    2. **The EDF pair no longer rides the mortise.**  At 22.75/32.25 mm they sit
        **forward** of the mortise (hull Y +42.10…+72.90), so they need their own
        wall penetrations.

    **BOTH CLOSED 2026-08-24, and one of them was never a defect.**

    * The **wall penetrations already existed** — the Rev S1c branch added
      `wing_harness_ports()` (2 × Ø8.0 EDF + 1 × Ø4.5 encoder per side) and wires
      them into `build_negatives()` through `wing_keepout_negatives()`, so the
      same solids the gear bay is trimmed against are the ones the hull is cut
      with.  The 10.4 / 0.5 mm³ residuals reported here were **a bug in
      `tools/wing_root_deconflict.py`, not in the shell**: it evaluated one camber
      midline for both EDF bores, when each is camber-centred at its own station
      and the two differ by ~0.8 mm in Z.  Fixed; both now read 0.0 mm³.
    * The **Hall tenon pass-through already existed too** — `wing_one_side()`
      cuts it at the 54.0 mm station.  The same tool was hardcoded to subtract
      *EDF* pass-throughs from its tenon model, which was correct before Rev S1c
      and wrong after it: the reroute moved the EDF pair clear of the tenon and
      moved the sensor conduit into it.  The model is now **station-driven** — it
      cuts a pass-through for whichever conduit actually falls inside the tenon —
      so a future reroute cannot invert it again.

    Verified against the re-cut published shell: all four routes read **0.0 mm³**
    on both sides, and `tools/wing_root_deconflict.py` reports
    **"CLEAR — servo mounts deconflict and every cableway stays open"**.

##### 1.1.1.2 *Cargo*

- [x] **★ CARGO-01 — the mission payload does not fit past the wing spar. CLOSED 2026-08-25 (U3/U4).**
    *(found 2026-08-23 while placing the VERIFY-tier cargo accessories against the
    baked hull, root `WBS.md` §1.1.0; measured by `tools/cargo_bay_envelope.py`)*
    **BLOCKS the cargo mission, the cradle/winch placements, and the §1.1.1.2.1
    winch build.  Needs an owner decision — do not resolve unilaterally.**

    `README.md` mission steps 6 and 9 require a **4 in × 3 in × 3 in
    (101.6 × 76.2 × 76.2 mm)** payload to be winched up through the clamshell
    aperture and carried inside the bay.  The wing spar crosses the bay laterally
    at the Rev S1b station (`merge_cargo_interior.WING_SPAR_Y` = **+38.15 mm**,
    `WING_SPAR_Z` = **+68.42 mm**), and its bore is cut the **full lateral span**
    (hull X −270…−70), so it sits directly across the payload's vertical path.
    The spar is continuous through the fuselage by design — `wings_s1223_revo.scad`
    Rev R2 makes it the unified rotating tilt-spar serving *both* nacelles, with
    "the second bearing … in the cargo bay" — so it cannot simply be routed around.
    Clearances below use the **wing's Ø8.0 mm** spar (the generous case; see
    CARGO-02 — the cargo shell still bores Ø12.3, which is worse), measured against
    the published shell and the baked door STLs (bay floor = closed-door crown,
    hull Z **+8.72**; aperture `merge_cargo_interior.APERTURE` = Y +2…+108):

    | Path into the bay | Clear | Needed | Result |
    | --- | --- | --- | --- |
    | Under the spar (Z +8.72 → +64.42) | 55.7 mm (2.19 in) | 76.2 mm (3.00 in) | short 20.5 mm |
    | Forward of the spar (Y +2 → +34.2) | 32.1 mm (1.27 in) | 76.2 mm (3.00 in) | short 44.1 mm |
    | Aft of the spar (Y +42.2 → +108) | 65.8 mm (2.59 in) | 76.2 mm (3.00 in) | short 10.4 mm |

    Every orientation is blocked; the **best case is 10.4 mm short**.  Rotating the
    payload does not help — its two smaller dimensions are equal, so 76.2 mm is the
    smallest face it can ever present.  This is **not** a Rev S1b regression: the
    pre-S1b spar (Y +31.7, Z ≈ +66.5) also crossed the bay, so the conflict has been
    latent since the spar was first routed through the cargo section.

    **RESOLUTION SELECTED 2026-08-23 (owner) — resolution 1, in the stronger
    form.**  The spars now **terminate at the fuselage wall** on a bearing in the
    side, rotate independently, and are driven by the nacelle servos; the couple
    they used to carry across is closed by a **CF thwart fore and aft of the bay**
    instead.  Verified adequate in `airframe/wings-nacelles/WBS.md` §1.1.2
    **SPAR-01** (`tools/wing_spar_carrythrough.py`).  With the spar stopping at
    X −100 / −240 the bay clear span is **X −240…−100 = 140 mm** at full bay
    height, and the 4 × 3 × 3 in payload fits.

    **CLOSED 2026-08-25.** The shell was re-cut (U3, `7bfccd3`) and the two CF
    thwarts closing the couple were added (U4). `tools/cargo_bay_envelope.py`
    now PASSES against the published, re-merged STL: measured interior
    170.6 mm (X) x 150.7 mm (Z), aperture 106.0 mm (Y) — the
    101.6 x 76.2 x 76.2 mm payload fits with margin on every axis. Closed
    together with **CARGO-02** below, the same shell edit.

    Candidate resolutions as originally tabled, retained for the record (the owner
    took 1; each of the others trades against a requirement that is currently
    fixed):

    1. **Split the spar at the centreline** into two stub spars landing on a
        centre rib, clearing the bay volume.  Cost: the continuous through-member
        that today carries nacelle tilt loads across the fuselage is lost, so the
        rib must take the full spar bending moment; re-opens the
        `CF-PLATE-2MM` cargo Y +30 ring sizing and `docs/structural_analysis.md` §3.
    2. **Move the spar station** clear of the aperture (forward of Y +2 or aft of
        Y +108).  Cost: breaks the 35 %-root-chord station that Rev S1b just fixed
        to match `wings_s1223_revo.scad` `SPAR_BORE_STATION`; both parts move.
    3. **Raise the spar** above the payload.  Requires spar Z ≥ +8.72 + 76.2 + 6.0
        = **+90.9 mm**, i.e. +22.5 mm above today's axis — well off the S1223
        camber midline, so the wing structure changes, not just the fuselage.
    4. **Re-scope the payload** to ≤ 63.9 mm (2.51 in) in its two smaller
        dimensions, carried aft of the spar.  Cost: amends `README.md` mission
        steps 6 and 9 and the `docs/CARGO_WINCH_SPECIFICATION.md` envelope.
    5. **Carry the payload slung below the hull** rather than inside it.  Cost:
        contradicts README step 9 ("pull the payload into the cargo bay and close
        the clamshells") and re-opens the drag/CG case.

    Until this is settled the cargo cradle cannot be placed: `cargo_cradle_autolatch`
    (110 × 80 × 72 mm) is sized for the 4 × 3 × 3 in payload and inherits the same
    obstruction.

- [x] **CARGO-02 — the cargo shell bores for a spar the wing retired. CLOSED 2026-08-25 (U3).**
    *(found 2026-08-23 alongside CARGO-01; gated by `tools/cargo_bay_envelope.py`,
    which fails loudly on the mismatch)*  **BLOCKS cargo shell print.**

    `airframe/openscad/wings/wings_s1223_revo.scad` Rev R2 (2026-07-18) states
    plainly that **"the 12 mm fixed CF tube is retired"**: the wing's single spar
    is now an **8 mm rotating AISI 4130 tilt-spar** (hollow ≈5 mm ID, carrying the
    nav-light 3-core), which is simultaneously the wing structural spar and the
    nacelle tilt axis, and it declares `SPAR_BORE_OD = 8.3` (8.0 mm OD + 0.15
    mm/side rotating clearance).  Three places still carry the retired 12 mm part:

    | File | Constant | Carries | Should be |
    | --- | --- | --- | --- |
    | `airframe/blender-scripts/merge_cargo_interior.py` | `WING_SPAR_BORE_D` | 12.3 | 8.3 |
    | `airframe/blender-scripts/merge_cargo_interior.py` | `WING_SPAR_BOSS_OD` | 22.0 | re-derive for a bearing seat, not a press-fit |
    | `current-specification/bom_revS.csv` | `CF-TUBE-12MM` | 12 mm OD CF tube ×2 | 8 mm OD AISI 4130, hollow 5 mm ID |

    A 4.0 mm diametral over-bore on a **rotating** spar is not a slip fit, it is a
    missing bearing: the Rev R2 note is explicit that the cargo-bay end carries the
    **second bearing** of the tilt axis, so the shell needs a bearing seat sized to
    the chosen bearing, not a clearance hole.  Rev S1b reconciled the spar
    **station** across the wing and the cargo shell (that was the §1.1.2
    spar-interface blocker) but left the **diameter** unreconciled, so this is the
    same defect class re-appearing on the other dimension.

    Sequencing — **settled 2026-08-23.**  CARGO-01 took resolution 1 (spars stop
    at the wall, independently rotating, nacelle-servo driven; see
    `airframe/wings-nacelles/WBS.md` §1.1.2 **SPAR-01**), so the shell edit is now
    fully specified and CARGO-01/CARGO-02 close together in it.  The bore is no
    longer a full-span clearance hole at all: it becomes a **bearing seat in the
    lateral wall** sized to the chosen bearing for an 8 mm rotating spar, and it
    stops at the wall (inboard end X −100 port / −240 starboard) instead of
    crossing the bay.  `WING_SPAR_BOSS_OD` is re-derived from that bearing's OD
    rather than from the retired Ø12 press fit.

    **CLOSED 2026-08-25.** `WING_SPAR_BORE_D` is 8.3 mm (matching the wing's
    `SPAR_BORE_OD`); `WING_SPAR_BOSS_OD` is 27.7 mm, derived from the F688ZZ
    bearing seat, not the retired Ø22 press fit; `bom_revS.csv`'s
    `CF-TUBE-12MM` row is marked SUPERSEDED (qty 0), retained for
    traceability, citing `SPAR-TILT-4130` as the single active spar row.

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
    Faraday tray corner mounts; bay Z centers adjusted ±1 mm (Inara 118→119, River 45→44) for 10 mm
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
    center (Inara: offset −13.3 mm in Z from bay center; River: offset +0.7 mm in Z from bay center).
    4× M2 flathead captive screws at ±40 mm (X) × ±25 mm (Z) from cover center for EMI-seal clamping.
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
    - **FM3** pedestal through-bolts + aluminum backing plates, replacing
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
- [ ] **★ Flight-envelope decision — shed threshold vs maneuver envelope.** At
    `F_shed` = 8.0 N a **2.0 g** maneuver on the slung payload reaches **0.98×**
    the threshold and **2.5 g sheds the load**. Choose: declare a ≈1.5 g slung-load
    maneuver limit (recommended — free, and matches crewed-rotorcraft practice),
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
    the port flange hub, off-axis (the fixed axle occupies the centerline); mates the
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
- [ ] **RS-485 gateway integration (both winch and nacelle-tilt applications) — interim.**
    LibreServo v2's differential RS-485 bus has no local transceiver on `CAN-PERIPH-GW-1`'s
    `J_FLEX` header (which was sized for the STS3215's single-wire half-duplex TTL scheme).
    Decide: add a transceiver fed from `FLEX_UART_TX/RX`, or extend the gateway's own
    isolated RS-485 uplink trunk (ISOW1412) to this local servo drop. Cross-ref
    `avionics/WBS.md`, `avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md`.
    **Watch before committing:** the LibreServo v2 fork maintainer confirmed (2026-08-02)
    the fork's in-progress isolated-RS-485/CAN-FD/SLB9672-TPM upgrade is intended to let a
    converted servo attach directly to the airframe's isolated CAN-FD/RS-485 trunks as its
    own self-signing node, eliminating the gateway-bridge need for this application entirely
    — not shipped yet (schematic-only, TPM not started). If it lands before this item is
    implemented, re-scope to direct-attach instead of building an interim bridge.
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
2. **Inner neck** — a tube-like enclosed passage running through the center of the horseshoe,
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
    - 4× M3 standoff boss posts for Flight Engineer PCB (55×35 mm board; ±20×±12.5 mm pattern from bore center)
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


---

## §1.1.1.5 — Wing-Root Spar Socket (Rev T1 joint requirements)

**Owning specification:** [`docs/WING_ATTACH_INTERFACE.md`](../../docs/WING_ATTACH_INTERFACE.md)
**Owning plans:** `docs/plans/2026-08-29-003-...` U7; `airframe/wings-nacelles/WBS.md` §1.1.4 SPAR-20-7

**Why this section exists.** The wing side of the Rev T1 tilt-spar migration is
BUILT (2026-08-29); the fuselage side is not. The spar is no longer a rotating
drive shaft that the wing rides on — it is a **fixed 20 × 16.3 mm CF tube bonded
into the wing**, and it is now the wing's primary bending member. That makes the
fuselage socket the wing's structural root joint, replacing both the enlarged
tenon (FOS 0.49, CARGO-03c) and the two-rod couple (FOS 4.14, U5/KTD1) that
existed only because a spar on bearings could not react a moment.

**The gate is currently RED and will stay red until this section lands.**
`tools/wing_root_deconflict.py` exits 1 with three findings, all one cause — the
fuselage still carries `WING_SPAR_Y = +38.15` and `WING_SPAR_BORE_D = 8.3`:

| Finding | Blocked volume |
|---|---|
| rotating spar tube blocks Hall/encoder conduit | 1,720.6 mm³ |
| rotating spar tube blocks tilt drive-shaft bore | 637.7 mm³ |
| published cargo shell blocks spar bore / 4 × 10 AWG feeds | 2,048.6 mm³ |

- [ ] **WA-R1 — Spar socket.** Hull **Y +21.00**, **Z +66.85**, bore **Ø20.4**
    (20.0 OD + 0.2 mm/side epoxy gap), **≥ 55 mm spanwise reach** inboard of the
    wall. Both stations are DERIVED, not chosen: the wing LE root bakes to hull
    Y −7.0 and the spar is at chord station 28.0 → +21.0; the chord line bakes
    to Z +58.01 and the spar rides the **unscaled** camber midline (+8.84 mm at
    this station) → +66.85. **Do not apply `THICKNESS_SCALE` to the midline** —
    `s1223_section()` opens the thickness envelope *about* an unscaled camber
    line, so scaling it would lift the socket 4.07 mm above the spar.
    Update `WING_SPAR_Y` / `WING_SPAR_Z` / `WING_SPAR_BORE_D` in
    `airframe/blender-scripts/merge_cargo_interior.py`.

- [ ] **WA-R2 — Delete the F688ZZ root bearing.** A bearing here is no longer
    merely unnecessary, it is wrong: it would let the fixed spar spin under the
    tilt pinion's gear reaction. Replace with a bonded/clamped socket.

- [ ] **WA-R3 — Split-collar pinch clamp.** ≥ 5 mm wall over Ø20 (≈ Ø30 outside),
    M3 heat-set inserts, 2 screws. **No set screws** — CF tube splinters under a
    point load. The split must retain a **positive gap when clamped**; if the
    halves close on each other first, the collar grips itself and the spar is
    free. This is the joint that makes wing + bonded spar removable as one
    assembly (the spar is bonded in the wing, clamped in the fuselage).

- [ ] **WA-R4 — Re-size the mortise** 30.8 → **12.8 mm** wide. The tenon is now
    a locating feature at 12 × 20 × 8 mm (`TENON_LOAD_PATH = "spar_carrythrough"`),
    not a 30 mm structural tenon. The current mortise is oversize for it.

- [ ] **WA-R5 — Re-verify the cargo-bay envelope** against the intruded clear
    span, do not assume it. `tools/cargo_bay_envelope.py` currently passes the
    mission payload (101.6 × 76.2 × 76.2 mm) against a 170.6 mm measured
    interior width, but that is measured with the spar stopping at X −100.

- [ ] **WA-R6 — Fuselage-side conduits** to match the wing's new bore set:
    nav 3-core at hull Y +1.0 (Ø3.2), AK7455 shielded pair at Y +37.5 (Ø6.5),
    tilt drive shaft at Y +47.0 (Ø4.4). The retired Ø7 EDF double-D ports can go
    — the four 10 AWG feeds now enter the spar bore directly at the socket.

### OWNER DECISION REQUIRED — bay intrusion

55 mm of socket reach puts the spar's inboard end near hull **X −136** (wall at
−81.3), cutting the cargo-bay clear span **140 mm → ~104 mm** on that side.
`CARGO-01` removed a full-width spar carry-through *precisely* to free that
volume, so this is a real re-encroachment in the same direction, and it is not
the wing's call to make. Three options, unpriced:

1. **Accept it** — re-run WA-R5 against the intruded span and confirm the
   mission payload still fits.
2. **Land the LG-11 coupon** (root `TODO.md` §1.1.4). Socket bearing stress goes
   as 1/L², so the allowable moves the length hard: at the owner's own <15 MPa
   decision-rule threshold **31 mm** clears FOS 4.0; at REF-MAT-001's ASTM D695
   bulk-compressive figure for 20 % CF-PETG (47 MPa) **17 mm** would do — and
   bearing of a bonded tube against a socket wall *is* a compressive mode, not
   the bond/peel mode the standing 5 MPa figure was written to bound. This is
   very likely the conservative direction by a wide margin, but overturning a
   standing repo allowable is an owner decision, not a side effect of a geometry
   change.
3. **Two short collars** instead of one continuous socket — same 1/L² physics on
   the separation; two 12 mm collars 50 mm apart reach FOS 4.1 with less
   continuous material, though the same total reach.
