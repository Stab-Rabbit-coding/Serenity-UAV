# Serenity UAV — Airframe Fuselage — Joints, Bow Pod, Interior Bosses Work Breakdown Structure (Detail)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0
**Current design revision:** Rev S (2026-07-04)

> **Detail-holder for the root WBS.** The repository-root [`TODO.md`](../../TODO.md)
> is a compact index — headings, subheadings, and short (<=70-char) checkbox items
> only, per root `AGENTS.md`. This file carries the full task detail for the WBS
> branches the root indexes below. Close an item here first, then check it off in
> the root index as a commit prerequisite (root `AGENTS.md` "Revisions and Version
> Control").

*"The Earth got used up. — opening narration"*

---

## §1.1.1 — Fuselage: Joints, Bow Sensor Pod, Interior Bosses (part 1/3)
*(root `WBS.md` §1.1.1)*


##### 1.1.1.1a *Bow Sensor Pod — Head Section (Rev R1c, 2026-06-30)*

Forward-facing sensor assembly on the canonical **40°-tilted bow mounting flat**
(~26.4 × 15 mm, outward normal 39.8° about +X), replacing the modeller's two convex
camera bumps.  **Rev R1c redesign (2026-06-30):** geometric verification against the
baked canonical head shell showed the Rev R1 dorsal/ventral dome estimates were off
(dorsal camera floated ~10 mm proud of the rounded nose).  Per user direction the three
apertures are now CLUSTERED on the 40° flat and distributed HORIZONTALLY — **camera on
the PORT camera-bump, ToF on the STARBOARD camera-bump, crosshair laser on CL between
them** — all bores normal to the flat, carried by ONE combined faceplate.
SCAD: `airframe/openscad/fuselage/bow_sensor_pod.scad` (cuts) +
`airframe/openscad/fuselage/bow_sensor_faceplate.scad` (faceplate); verifier:
`tools/verify_bow_pod.py`.

###### Geometric Verification — DONE 2026-06-30 (replaces manual slicer cross-sections)

- [x] **Built `tools/verify_bow_pod.py`** — ray-casts each bore against the baked
    `head_shell24_2mm_repaired.stl` and reports skin-landing, wall thickness, interior-pocket
    clearance, and aperture-row fit.  Reproducible; supersedes the eyeball-in-slicer checks.
- [x] **Located the canonical bow mounting flat** — centre hull (−167, −301, 120), normal
    (0, −0.766, −0.643) = 39.8° about X, ~26.4 × 15 mm (matches the 1.04 × 0.59 in spec).
- [x] **Placed + skin-verified all three apertures on the flat (3/3 PASS):** camera hull
    (−161.2, −300.7, 116.0) Ø10; ToF hull (−177.7, −301.0, 116.6) Ø8; laser hull
    (−170.7, −299.9, 117.1) Ø6 exit.  All land on skin (offset ≤ 0.01 mm), walls ≥ 2.2 mm,
    interior bores clear ≥ 103 mm into the nose (no pocket breach).
- [x] **Confirmed fit:** aperture row spans 25.5 mm in the 26.4 mm flat; ToF over-runs the
    starboard roll-off ~1.3 mm (bridged by the faceplate).
- [ ] **User FreeCAD fine-tune (fractional mm):** confirm the ToF 1.3 mm over-run and the
    camera↔laser↔ToF body-pocket packing behind the flat in `SerenityAssembly.FCStd`;
    re-run `tools/verify_bow_pod.py`.  *(rough fit verified; final alignment per CLAUDE.md
    complex-geometry policy)*
- [x] **Merge `bow_pod_cuts()` into the canonical Blender head shell — DONE 2026-07-03.**
    New `airframe/blender-scripts/merge_head_interior.py` (Rev R1d), mirroring
    `merge_cargo_interior.py`'s robust single-union/single-boolean pattern: loads the
    already-published, already-baked, already boss/aft-face-featured
    `head_shell24_2mm_repaired.stl` (deliberately does NOT redo the joint-boss work already
    done by `add_structural_features.py`'s `process_head()`), builds the camera/ToF/laser/
    faceplate-seat cutters exactly as `bow_sensor_pod.scad` defines them (same positions,
    same `rotate([130,0,0])`, same wall-overshoot), unions them into one cutter solid, and
    does ONE `shell − cutters` manifold3d boolean. Found and fixed a real bug along the way:
    the published STL loads with `process=False` (skips vertex welding — each STL triangle
    stores its own unwelded vertex copies), which made `trimesh` report
    `is_watertight=False` and made manifold3d reject the mesh outright
    (`Error.NotManifold`, producing an empty result) until `mesh.merge_vertices()` was added
    (matching the call `merge_cargo_interior.py` already makes — I'd missed it on the first
    pass). Also found one real disconnected 158-face/3.16 mm³ boolean-artifact sliver where
    two cutters graze each other; added a `keep_largest_body()` cleanup (analogous to
    `merge_cargo_interior.py`'s `drop_slivers()`) to discard it.
    **Verified (not just claimed):** `is_watertight=True`, `is_winding_consistent=True`,
    **1 body**, 0 boundary/0 non-manifold edges, volume 183,192 mm³ (down from 186,709 mm³
    pre-cut — a sane ~3,500 mm³ reduction from the 3 bore/pocket cutters + bump-shave).
    `tools/bake_hull_frame.py --check` confirms the `HULL-FRAME R1` marker survived (no
    re-bake needed — only booleans were applied, matching the identity-rotation head bake).
    `python3 tools/validate_stls.py` — **all 69 STL files pass watertight, including this
    one.**
    Observer's nose-mount bosses (`jayne_board_bosses()`, added earlier this session) and
    Shepherd's Book-bay bosses (`book_dorsal_boss()`, known unfixed legacy-axis bug) were
    DELIBERATELY EXCLUDED from this merge — both remain SCAD-only proposals, not baked into
    the fabrication mesh, per their own open-item flags (merging an unverified/buggy
    placement would falsely certify it).
    - **2026-07-12 (Rev S1):** `cargo_sect_shell24.scad` `vera_board_bosses()` was updated to the
        NEW Vera trapezoid outline's 4 corner **M2.5** holes (cargo JST-jumper variant), and a
        `cargo/cargo_vera_faraday.scad` EMI enclosure was added (renders watertight). These stay
        **SCAD-only / excluded from the baked mesh** for the same reason — pending a full
        cargo-shell render + watertight mesh check + re-bake, and a FreeCAD fit check. The Vera
        SoM is now the connectorized PHYTEC PCM-071 (240-pin, 2× Samtec BTH-060) — see avionics
        §1.2c; the nose install still needs head-shell rail slots + a foam void form (airframe
        §1.1).
- [x] **Re-run mesh validation after head shell regen — DONE 2026-07-03** (see above,
    `validate_stls.py` all-pass). Also re-ran `tools/verify_bow_pod.py` post-cut and found
    (and fixed) the SAME unwelded-STL loading bug there (`mesh.merge_vertices()` was missing
    — one-line fix). **Note on interpreting that tool post-cut:** `verify_bow_pod.py`
    ray-casts to find "first skin hit" along each bore axis — that check is only meaningful
    *before* cutting (confirming a proposed position lands on real skin, which it already
    did: 3/3 PASS, 2026-06-30). Run *after* the cut, the intended spot is now a hole, so the
    ray correctly sails through and reports hitting the *far* wall instead — an expected
    consequence of the tool's pre-cut design, not a regression. The actually meaningful
    post-cut check — `mesh.contains()` at each of the three aperture-centre hull points —
    confirms all three are void (outside the solid), i.e. the cuts landed exactly where
    intended: camera (−161.20,−300.68,+116.01), ToF (−177.67,−300.98,+116.61), laser
    (−170.67,−299.94,+117.14) — all `contains=False` ✓.

###### Combined Faceplate — DONE 2026-06-30 (supersedes the two separate bezels)

- [x] **Designed `bow_sensor_faceplate.scad`** — single 28 × 16 × 2.5 mm CF-PETG plate on the
    40° flat carrying camera (Ø10 lens), laser (Ø6 exit) and ToF (Ø8 + rear 8.4 mm PMMA disc
    counterbore); 4× M2 flathead from exterior into seat heat-set inserts.  Rendered + mesh-
    validated (watertight, manifold; ~0.83 g).  The shell-side seat (`bow_face_seat()` in
    bow_sensor_pod.scad) shaves the two camera bumps flat and drills the 4 inserts.
- [x] **Superseded `bow_camera_bezel.scad` + `bow_tof_laser_bezel.scad`** — three 15–21 mm
    bezel flanges cannot coexist on the 26.4 mm flat; consolidated into the one faceplate
    (separate files removed before commit).
- [ ] **PMMA window spec finalised** (sourcing remains a procurement action):
    - [x] Camera: open Ø10 lens bore (no window; faceplate shades the lens)
    - [x] ToF: 8 mm dia × 2 mm PMMA disc (uncoated; transmits 905 nm IR) — rear counterbore
    - [ ] Laser: 3 mm dia × 2 mm PMMA exit window (optional; sealed modules may omit)
- [ ] **Procure PMMA discs** (ToF 8 mm, laser 2 mm) — physical purchase. *(external)*
- [x] **Laser down-angle review** — **APPROVED 2026-06-30 (user).** The laser is mounted normal
    to the 40° bow flat (40° below horizon, vs the Rev R1 30°); this is the accepted final
    orientation, no re-aim required.

###### Avionics Integration *(physical wiring + firmware — external to this CAD task)*

- [x] **Superseded 2026-07-03 — see §1.2c "Observer" below.** ~~Create RP2350 (or similar) based
    Camera/TOF/laser mcu board~~ Scope expanded during design exploration (imported AI-assisted
    brainstorm, fact-checked and corrected against real datasheets — see REFERENCES.md
    "Removed / Superseded Citations" for what was fabricated in the original brainstorm) into
    the **Observer** standalone board (not a PB2-I cape — its own board, peer network node via
    Ethernet ring/CAN-FD only): TI MSPM0G3507 (native CAN-FD) + Infineon SLB9670 TPM
    (fleet-standard part, not a new one) + Microchip KSZ9477 Ethernet switch, plus a TI AM62Ax
    digital vision SoC replacing the RunCam Nano 4 analog camera. One board design, installed
    at both the bow sensor pod (nose) and the cargo bay nadir FPV mount.

- [x] **Wire TFmini-S UART to bow sensor MCU.** — **SUPERSEDED by Observer (2026-07-06).**
    The pre-Observer plan ran a 28 AWG loom from the bow pod all the way to Shepherd's Room and
    read the TFmini-S on the Shepherd (Pilot) node. Observer is now the board *at* the bow pod, so
    the TFmini-S is a short local run (<75 mm) on Observer's dedicated `J_TOF`/UART1, read by Observer's
    MSPM0G3507 — no head-section loom to Shepherd's, no Shepherd `serenity-fc` UART driver.
    Replaced by the Observer local sensor harness (§1.2c) and Observer node firmware (§4.6).
- [x] **Wire bow camera video output to bow sensor MCU** — **SUPERSEDED by Observer (2026-07-06).**
    The RG178 analog-coax run was for the RunCam Nano 4 analog camera, which Observer supersedes
    (REF-SENSOR-001, superseded). Observer's camera is a digital MIPI CSI-2 module on `J_CAM1/J_CAM2`
    (flex/FPC, ~20–30 mm), encoded on-board by the AM62A7 and published over the Ethernet ring —
    no analog coax to a separate MCU. Tracked as the Observer local sensor harness (§1.2c).
- [x] **Wire laser GPIO enable bow sensor MCU** — **SUPERSEDED by Observer (2026-07-06).**
    This discrete 2N7002-from-Pilot-GPIO driver plus a Class-3B-style physical key-switch
    ([REF-FDA-001 §1040.10(f)(1)]) is replaced by Observer's own on-board laser driver (Q1 AO3400
    logic-level N-FET, R1 100 Ω gate, R2 10 kΩ pulldown-default-off, `J_LASER`), enabled by
    Observer's MSPM0G3507 — not a Pilot GPIO. Per `docs/OBSERVER_LASER_ANALYSIS.md` Rev A2 the nose is
    **Class 2 (≤ 1 mW green), NOT Class 3B**, so the mandatory key-interlock/shutter is dropped
    and the ≤ 1 mW cap is hardware-enforced (fixed current limit). Tracked at §1.2c (driver) and
    §4.6 (GPIO firmware + interlock).
- [x] **Add laser enable command to MAVLink C2 interface** [REF-PROTO-002] — **SUPERSEDED /
    RELOCATED to Observer (2026-07-06).** The laser is now Observer-owned (commanded by Observer's
    MSPM0G3507, published/gated over the CAN-FD + Ethernet ring), not the Pilot MAVLink path. The
    surviving C2-enable requirement is folded into the Observer "Laser GPIO driver" firmware task
    (§4.6). Because the nose is now Class 2 (`docs/OBSERVER_LASER_ANALYSIS.md` Rev A2), the previously
    **mandatory** operator acknowledgement is downgraded to **optional** defense-in-depth rather
    than a Class-3B requirement.
- [ ] **Add standards REF-IDs to bow_sensor_pod.scad firmware integration notes** once driver
    code is in place.  Ref: [REF-SENSOR-002] TFmini-S UART protocol, [REF-NIST-001 §2.1] ZTA.

###### Mass Budget Entry — DONE 2026-06-30 (in `docs/bom_revR.json` → `bow_sensor_pod`)

- [x] **BOM updated** — `bow_sensor_faceplate.stl` added to `print_schedule`; dedicated
    `bow_sensor_pod` mass block added (imperial-primary).  Net AUW change vs the two convex
    bumps is ≈ nil (bumps removed, ~0.8 g faceplate added).
- Bow camera (RunCam Nano 4 or equiv.): 0.13 oz (3.6 g) [REF-SENSOR-001]
- TFmini-S ToF sensor: 0.18 oz (5.0 g) [REF-SENSOR-002]
- Crosshair laser module: ≈ 0.28 oz (8 g) (estimate; varies by COTS supplier)
- Printed faceplate (CF-PETG, measured solid vol 0.65 cm³): ≈ 0.03 oz (0.8 g)
- PMMA windows (2×): ≈ 0.2 g
- Wiring / connectors: ≈ 0.18 oz (5 g) (estimate)
- **Total bow pod mass addition: ≈ 0.80 oz (22.6 g)** *(was ~25.6 g with the twin-bezel placeholder)*
    Update master BOM `docs/bom_revR.json` once bezel masses confirmed in slicer.

---

##### 1.1.1.0a *Blender-Canonical Source Adoption (Rev R1, 2026-06-13)*

The four Blender-derived, 2 mm hollow, repaired fuselage shell STLs in
`airframe/blender-scripts/files-hollowed-24in/` are now the **authoritative canonical
sources** for all fuselage geometry.  They have been copied to `airframe/stls/fuselage/`
and baked to hull frame.  SCAD fuselage shell files are secondary references only.

**Baked on 2026-06-13 (all four verified OK, max error < 1.52e-05 mm):**
- [x] `head_shell24_2mm_repaired.stl` — 790 036 tri; X −232.9..−103.5 / Y −305.7..−70.7 / Z +61.1..+201.5 mm
- [x] `cargo_sect_shell24_2mm_repaired.stl` — 1 414 068 tri; X −267.0..−72.7 / Y −71.5..+132.0 / Z 0.0..+163.2 mm
- [x] `middle_shell24_2mm_repaired.stl` — 855 328 tri; X −258.5..−81.6 / Y +130.4..+203.6 / Z +1.3..+166.1 mm *(see §1.1.1.3 — includes horseshoe ring + inner neck as ONE piece)*
- [x] `rear_shell24_2mm_repaired.stl` — 1 095 972 tri; X −246.1..−105.5 / Y +203.2..+384.3 / Z +3.3..+161.1 mm

**Open tasks:**

- [x] **Cargo section interior boss features** — **DONE 2026-06-30** via new
    `airframe/blender-scripts/merge_cargo_interior.py` (Rev R1).  Starts from the clean
    Blender source, bakes to hull frame, and merges every cargo interior feature in ONE
    robust manifold3d pass (union all cutters / union all positives → single
    `(shell + positives) − negatives`).  Result: **watertight=True, single connected body,
    0 boundary/0 non-manifold edges, vol 323 188 mm³ (≈ 339 g as-printed .. 414 g solid
    CF-PETG)** — this simultaneously fixes MESH-01 for cargo (see MESH-01 item below).
    Merged this pass:
    - **Interior-wall removal** — the leftover cargo-bay floor "duct" the Blender hollowing
        left inside the cavity (a ~54×38 mm closed box blister on the belly floor, hull
        X −196..−142, Y −15..+102, Z 6..44), confirmed by cross-section + render before cut.
    - **Clamshell doors** — belly aperture cut hull X[−222.5..−117.6] × Y[+2..+108] between
        the two hinge lines, + the 4 Rev R1c hinge-pin retention blocks (imported verbatim
        from `generate_cargo_hinge_retention.py`), fused into the shell.
    - **Section-joint features** (head/cargo Joint 1 + cargo/middle Joint 2): bore-open
        fwd/aft faces, 6× Ø3.2 boss-pin bores, keel locating channel, Y=+30 ring-frame
        pocket — single-sourced from `add_structural_features.py`.
    - **Wing mortices** — Ø12.3 spar bore (full lateral span, both walls), 2 root mortises,
        and 2× Ø22 spar-bearing bosses, at the **re-derived** chordwise stations (129 mm Rev
        R1 root chord, LE root hull Y=−7: spar 30% → Y=+31.7; mortise 50% → Y=+57.5; Z=62.5).
        Supersedes the SCAD `WING_ROOT_Y_CEN=CY+40` (hull Y≈+6) stale-161mm-chord stand-in
        (§1.1.2).  All lateral-wall/dorsal features are seated against the wall position
        **sampled from the real baked mesh** at each feature's (Y,Z) — the walls curve
        inboard with Z, so a bbox-extremity pin would float off the wall.
    - **Interior support structures** — 2 nacelle-servo mount pads (Z=93, clears spar boss
        by ~4 mm) + M3 bores; **Inara** (port) avionics-bay standoff bosses (4, dorsal).
    - **SUB-TASKS OPEN (VERIFY / deferred — do not block MESH-01 or door/joint printing):**
        - [x] Verify wing spar/mortise fit in FreeCAD against the baked wing STL root/tab
            (2026-07-03, trimesh cross-section of `wing_port_s1223_revo.stl`, hull-frame,
            watertight): measured tab X[-93.0,-81.0] Y[42.5,72.5] (ctr 57.5) Z[48.0,68.0]
            (ctr 58.0) — matches `wings_s1223_revo.scad` WING_ROOT_TAB_W/H/L (30/20/12) mm
            exactly. **Y confirmed**: matches this section's re-derived mortise target
            Y=+57.5 mm above (supersedes stale `WING_ROOT_Y_CEN=CY+40`). **Z open**: planned
            mortise center Z=62.5 vs measured tab center Z=58.0 — 4.5 mm mismatch (~16/20 mm
            overlap only); adjust mortise Z_CEN to 58.0 mm or wing tab Z before cutting.
            **Mortise cavity not yet present** in `cargo_sect_shell24_2mm_repaired.stl` —
            solid material confirmed at the tab footprint by X-slice scan; cut/merge still
            TBD (blocks wing installation).
        - [x] **GPS×2, FPV nadir camera, and Inara/River avionics-bay dorsal mounts —
            axis bug FIXED at the SCAD reference-design level, Rev R2 (2026-07-03).**
            Root cause confirmed empirically (not guessed): the real canonical mesh's
            local Z range (0..163.2 mm) matches the documented bake-invariant hull Z
            range exactly, and local X range matches `CARGO_X_WALL_PORT/STBD` (fixed
            Rev R1) — confirming Z=dorsal, X=lateral, Y=longitudinal in this file, same
            as the rest of the project.  The GPS/avionics/nadir-camera modules were the
            only ones still using the legacy (Y=dorsal) mental model — same bug class as
            the Rev R1 wing-root fix.  **User decision (2026-07-03): Inara (port) and
            River (stbd) avionics bays are a lateral pair at a shared longitudinal
            station** (not fore/aft sequential) — matches their names and the
            GPS_PORT/GPS_STBD antenna-diversity co-location.  Fixed in
            `cargo_sect_shell24.scad`: `DORSAL_ROT`/`NADIR_ROT`, `DORSAL_Z_EXT`/
            `NADIR_Z_EXT` (measured, 163.2/0.0 mm), `GPS_PORT_POS`/`GPS_STBD_POS`,
            `CARGO_CAM_POS`, `avinics_dorsal_boss()`/`avinics_dorsal_panel_cut()`,
            `INARA_X_CEN`/`RIVER_X_CEN` (now real lateral positions, ±37.5 mm about CX).
            Original numeric intent preserved (GPS_SEP=30mm, 35mm inter-bay gap, 60×40mm
            tray footprint, 25/15mm boss offsets) — only the axis each number is applied
            to changed.  **River's avionics bay is restored** (previously dropped per the
            wing-spar Z conflict, §1.1.3.3 — that conflict was itself a symptom of the
            same Z-axis misuse; re-verify the wing-spar Z conflict note now that Z is
            correctly dorsal-only and no longer doubling as a lateral bay-selector).
            **NOT YET DONE:** these are SCAD reference-design fixes only — the actual
            fabrication-ready cargo mesh (produced by `merge_cargo_interior.py`) does
            NOT yet include GPS, FPV camera, or avionics-bay cuts at all (confirmed by
            reading that script — only Inara's boss/standoff geometry was merged, using
            its own independently-correct hardcoded hull-frame (X,Y)=(-135,90) values,
            unaffected by the SCAD bug).  Extending `merge_cargo_interior.py` to merge
            the now-fixed GPS/FPV/River-bay cuts (and the new Observer bosses below) into the
            real printed mesh is a follow-on task, not yet started.
        - [ ] **Door-servo pads, latch-catch lips, belly ribs, hinge-pin blocks — SAME
            axis bug found (2026-07-03), NOT yet fixed.**  `BELLY_INT_Y = -413` is used
            as the position's Y-component in `servo_mount_pad`/`belly_rib`/
            `latch_catch_lip` exactly like the now-fixed `AVINICS_DORSAL_Y` bug — i.e.
            these modules also treat Y as the nadir/vertical axis.  (Hinge-pin blocks are
            separately already marked superseded/legacy per Rev R1c — see
            `hinge_pin_block()` note — so lower priority.)  Needs the same fresh-design
            treatment as the GPS/avionics fix above (fix, don't guess-reinterpret) before
            these are merged into the fabrication mesh.
        - [ ] **Shepherd's "Book" Faraday-tray dorsal mount in `head_shell24.scad` — SAME
            axis bug found (2026-07-03) in the head section, NOT yet fixed.**
            `BOOK_DORSAL_Y = CY + 94` (`book_dorsal_boss`/`book_dorsal_panel_cut`) is the
            identical bug pattern, independently present in the head shell.  Confirmed
            the head shell's own local frame does NOT need any permutation fix otherwise
            (local X/Y/Z extents match the baked hull extents exactly, unlike cargo) —
            this is an isolated instance in the Book bay code only.
        - [ ] **Leg-mount clearance (§1.1.4):** the deferred Rev R5 wire-brace corner leg
            bosses must clear the **aft** door hinge retention blocks — those sit at the
            hinge X (−117.6 port / −222.5 stbd) over hull Y +109..+121, only ~9 mm aft of
            the aft leg-attach row (Y≈100). **Verified 2026-07-03** against
            `generate_cargo_hinge_retention.py` (real block geometry: aft blocks Y 109–121,
            X −126.6..−116.6 port / −213.5..−223.5 stbd, Z 0.5–9.26) and
            `docs/LANDING_GEAR_ANALYSIS.md` §11.4 (boss OD≈10 mm). With a ~10 mm boss
            centered on the Y≈100 row, true clear margin to the block face is **≈4 mm, not
            9 mm** — tight. **Cannot certify pass/fail**: LG-02/LG-10 (final corner boss
            X/Y placement) are still open in `LANDING_GEAR_ANALYSIS.md` §13/§14, so no
            authoritative boss X exists yet to check X-overlap against the block's X range.
            Recommend: finalize LG-10 boss X clear of block X ranges above, and hold the
            leg row at Y≤95 mm (≥14 mm clear of block face) rather than Y≈100.
        - [ ] Door latching: the aperture is a clean opening (no seating rabbet); the
            deferred latch-catch lips + `cargo_cradle_autolatch` hooks provide closure.
- [ ] **Middle section inner neck — Phase 5-10 print guidance** — the Blender middle mesh includes
    the inner neck (closed tube) and the outer horseshoe ring as one piece.  Confirm in slicer that
    both elements appear correctly and that there are no thin-wall violations in the neck-to-horseshoe
    web transitions.  The 4× EDF intake scoop openings in the inner neck are NOT cut in the current
    mesh — confirm before slicing.  See §1.1.1.3 for details.  **BLOCKS middle section printing.**
- [ ] **Deprecate SCAD fuselage shell files** — `s_head_shell24.scad`, `s_middle_canonical_shell24.scad`,
    `s_rear_neck_intake_shell24.scad` are now secondary references.  At next revision checkpoint,
    archive them to `airframe/archive/` and update PROJECT_INDEX.md / ARCHIVE_INDEX.md.
    `cargo_sect_shell24.scad` (Rev S3) remains active as the source for interior boss geometry
    until those features are merged into the Blender mesh (task above).
- [x] **Update `REVN_BUILD_GUIDE_24IN.md` fuselage shell source references** — **DONE 2026-06-30.**
    Added an authoritative "Fuselage shell source — Rev R1 canonical (Blender pipeline)" callout
    to the Blender Script Reference (copy from `airframe/blender-scripts/files-hollowed-24in/`
    → `airframe/stls/fuselage/` → `python3 tools/bake_hull_frame.py`), added the Blender-canonical
    row to the script table, and flagged the legacy `middle_canonical_shell24.scad` regen note.
    - [ ] *Remaining:* the legacy print-schedule table still lists pre-Rev-R1 PETG/8%-gyroid
        settings and old shell basenames; reconcile to CF-PETG 2 mm canonical at the next
        build-guide pass (out of scope for the source-reference fix).

##### 1.1.1.0b *Section Joint Boss / Alignment Design (Rev R1 — all four fuselage sections)*

All four fuselage section boundaries (head/cargo, cargo/middle, middle/rear) are
**fabrication splits** introduced for printability — they are not and were not structural
joints in the Thingiverse reference model (which was designed as a decorative display
piece with no structural engineering for any load case).

**Structural continuity is an open engineering task.**  The Thingiverse geometry —
wall thickness, cross-section shapes, and joint face geometry — was not designed to
carry UAV bending moments, torsion, shear, vibration, or landing-impact loads.
Candidate structural members (keel bar, CF ring plates, foam fill, CF skid rods) are
identified but have not yet been sized or verified.  The tasks below, and the keel bar
and ring plate re-evaluation tasks in §1.1.1, must all be completed before any structural
claim can be made about the assembled fuselage.

Each joint face must satisfy the **CLAUDE.md fabrication standard**: minimum 2-wall
contact annulus + positive-stop shoulder; friction fits are not acceptable for any joint.

Joint faces in hull-frame Y (confirmed from baked extents):
- **Head / Cargo** — hull Y ≈ −71 mm (Head_Shell Y-max = −70.7 mm; Cargo_Shell Y-min = −71.5 mm)
- **Cargo / Middle** — hull Y ≈ +131 mm (Cargo_Shell Y-max = +132.0 mm; Middle_Shell Y-min = +130.4 mm)
- **Middle / Rear** — hull Y ≈ +203 mm (Middle_Shell Y-max = +203.6 mm; Rear_Shell Y-min = +203.2 mm)

- [x] **Head/Cargo joint boss design (hull Y ≈ −71 mm)** *(done 2026-06-14)*
    - 3× Ø3.2 mm boss-pin bores (8 mm depth each side) at hull (X,Z):
        (−168.3, +143.9), (−138.0, +91.4), (−198.6, +91.4) mm; Y-range −79..−62 mm.
    - Face bore-open: Ø hull interior opened at Y −85..−68 mm (inner-face rectangle).
    - Positive-stop provided by pin depth; no separate shoulder lip needed (pin geometry
        self-registers both sections).
    - Implemented in `airframe/blender-scripts/add_structural_features.py` (BOSS_PIN_BORES
        joint1 + FACE_BORE_CUTTERS head_aft / cargo_fwd); all four shells verify PASS.
    - See `docs/structural_analysis.md` §4 for boss-pin sizing and load analysis.
    - Bond with West System 105/206; cure 24 h before foam pour.
    - **CORRECTION 2026-06-29 (verified against baked meshes — see §1.1.0 "Re-verify
        head↔cargo joint bosses in hull Y"):** the "8 mm depth each side" and
        "positive-stop by pin depth" claims above are **not achieved as-baked**.  Measured
        Y-engagement: dorsal pin A = HEAD 2.0 / CARGO 12.5 mm; flank pins B,C = HEAD 2.0 /
        CARGO 3.5–4.5 mm.  Straight Y pins through a tapering 2 mm wall give shallow
        engagement, and the broader cargo means the flank pins meet both walls only at the
        joint face.  Pins act as alignment dowels; the bonded West System lap is the
        primary load path.  Achieving true positive-stop depth needs boss pads or
        per-shell pin (X,Z) — structural decision flagged in §1.1.0.
    - **SUB-TASKS OPEN:** verify boss-pin bore positions in slicer cross-section at
        hull Y ≈ −71 mm before head/cargo printing. *(BLOCKS head + cargo printing)*

- [x] **Cargo/Middle joint boss design (hull Y ≈ +131 mm)** *(done 2026-06-14)*
    - 3× Ø3.2 mm boss-pin bores (8 mm depth each side) at hull (X,Z):
        (−170.1, +115.0), (−139.8, +62.5), (−200.4, +62.5) mm; Y-range +121..+141 mm.
    - Face bore-open: hull interior opened at Y +122..+134 mm and Y +128..+145 mm (aft
        cargo + fwd middle rectangles respectively).
    - Implemented in `add_structural_features.py` (BOSS_PIN_BORES joint2 + FACE_BORE_CUTTERS
        cargo_aft / middle_fwd); boss pins verified clear of keel channel (X −171.8..−168.2).
    - Bond with West System 105/206; cure 24 h before foam pour.
    - **SUB-TASKS OPEN:** verify in slicer at hull Y ≈ +131 mm. *(BLOCKS cargo + middle printing)*
    - [x] **Cargo/Middle splice analysis + design (mirror head/cargo §1.1.0).** DONE
        2026-07-03. Surveyed real cross-sections (trimesh, baked STLs): both cargo's aft
        face (Y=+122mm) and middle's fwd face (Y=+137mm) are CLOSED sections (middle's
        horseshoe doesn't open until Y>~175mm) — a full-perimeter collar is feasible.
        Load check: mass aft of joint (middle+rear shells + ~300g/section avionics
        allocation, §4.3 convention) = 1209g, arm 126.6mm; 9g-crash ultimate M=20,260
        N·mm vs a REAL computed section modulus S_x=31,984 mm³ (digitized profile, not
        an estimate) → 0.63 MPa peak, not strength-limited. Designed and generated
        `generate_cargo_middle_splice_collar.py` → `cargo_middle_splice_collar.stl`
        (hull frame, 2mm wall, L=16mm, ~17.0g, watertight single body, verified clearing
        the middle inner wall). Cargo-side fit checked only against the nearest clean
        cargo station (Y=+122mm) — the true cargo-side bonding span overlaps the
        pre-existing MESH-01 cargo defect (41 disconnected bodies); re-verify once that
        is resolved. Added to serenity_assembly.py, bom_revR.csv
        (PRINT-CARGO-MIDDLE-COLLAR), docs/structural_analysis.md §7.4, PROJECT_INDEX.md.

- [x] **Middle/Rear joint boss design (hull Y ≈ +203 mm)** *(done 2026-06-14)*
    - 3× Ø3.2 mm boss-pin bores (8 mm depth each side) at hull (X,Z):
        (−170.1, +109.6), (−139.8, +57.1), (−200.4, +57.1) mm; Y-range +193..+213 mm.
    - Face bore-open: hull interior opened at Y +193..+207 mm and Y +201..+217 mm (aft
        middle + fwd rear rectangles respectively).
    - CF skid-rod bores (Ø4.2 mm, 60 mm total, 30 mm per section) at (X=−202, Z=+18)
        and (X=−135, Z=+20); boss pins verified non-intersecting with skid-rod bores.
    - Implemented in `add_structural_features.py`; all shells verify PASS.
    - Bond with West System 105/206; cure 24 h before foam pour.
    - **SUB-TASKS OPEN:** verify in slicer at hull Y ≈ +203 mm. *(BLOCKS middle + rear printing)*
    - [x] **Middle/Rear splice structure analysis + design (mirror head/cargo §1.1.0).**
        DONE 2026-07-03. Surveyed real cross-sections: AT THE JOINT PLANE ITSELF the
        middle section is still a single closed tube (convex-hull-area ratio 0.96-1.00,
        Y=195-203mm) — resolves the open question above: a FULL RING collar is feasible,
        not just a partial inner-neck sleeve, because the horseshoe hasn't opened yet at
        this Y. Load check (shell-bending only; skid rods + inner neck remain the
        primary skid-impact load path, FOS 205 unchanged, §6.2): mass aft = rear shell +
        ~300g avionics = 614g, arm 90.5mm; 9g-crash ultimate M=7,362 N·mm vs REAL S_x=
        27,713 mm³ → 0.27 MPa peak, not strength-limited (even lower demand than
        Cargo/Middle). Designed and generated `generate_middle_rear_splice_collar.py` →
        `middle_rear_splice_collar.stl` (hull frame, 2mm wall, L=16mm, ~15.9g,
        watertight single body, verified clearing the middle inner wall and clear of the
        CF skid-rod bores). Rear-side fit checked only against the nearest clean rear
        station (Y=+233mm) — the true rear-side bonding span overlaps the pre-existing
        MESH-01 rear defect (36 disconnected bodies); re-verify once resolved. Added to
        serenity_assembly.py, bom_revR.csv (PRINT-MIDDLE-REAR-COLLAR),
        docs/structural_analysis.md §7.5, PROJECT_INDEX.md.

- [x] **JOINT-01 — cargo mating-face rims ragged + dorsal bite — RESOLVED 2026-07-06.**
    **FIX APPLIED:** `merge_cargo_interior.py` now opens the fwd + aft cargo joints with the
    SAME lofted per-station cavity cutter head/middle/rear already use
    (`asf._bore_open_cutter` with `asf.FACE_BORE_Y_RANGES["cargo_fwd"]`/`["cargo_aft"]`); the
    crude single-station `open_face_plug()` (and its `OPEN_*`/`FWD_FACE_Y`/`AFT_FACE_Y`
    constants) was deleted. The lofted cutter measures the inner cavity at several stations and
    lofts pairwise intersections, so it follows the tapering wall and never exceeds the local
    outer skin. Regenerated + verified by starboard-silhouette comparison: **the dorsal "top

### Observer (Vera) PCB mounting + Faraday enclosure (2026-07-12)
- [ ] **Vera PCB mounting + Faraday (2026-07-12, Rev S1).** DONE:
    `cargo/cargo_sect_shell24.scad` `vera_board_bosses()` updated to the NEW Vera trapezoid
    outline's 4 corner **M2.5** holes (was the old 46×48 / ±19×±20 M3 grid); CARGO variant —
    camera/ToF/laser are JST-jumpered so the board mounts FLAT (no sensor-aperture alignment),
    short harness to the JST connectors. New `cargo/cargo_vera_faraday.scad` EMI enclosure
    (73.85 × 62 × 17.6 mm internal tray + 4 M2.5 standoffs matching the board holes +
    waveguide-below-cutoff honeycomb vents + EMI-lip lid + JST harness slot; renders
    **watertight**, trimesh-verified; shield → PGND). PENDING: (a) **full cargo-shell render +
    watertight mesh check + re-bake** after the boss edit (bosses are SCAD-only, still EXCLUDED
    from the baked fabrication mesh — root TODO §1.1); (b) Faraday tray FreeCAD fit vs
    `door_bay_cut`/GPS/ribs; (c) **NOSE install** — add `head_shell24.scad` interior slots for
    the 1/16 in port/stbd install rails + a foam **void form** around the board, then
    render / mesh-validate / re-bake `Head_Shell`.
