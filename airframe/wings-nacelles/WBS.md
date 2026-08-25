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
    - **[x]** Verify cargo-section wing-root mortise dimensions against new root chord 129 mm (was 161 mm); `cargo_sect_shell24.scad` mortise slot (currently 30.8×20.8×15 mm) may need resizing and re-centering
    - **[x]** Re-check root-tab center position: with 129 mm chord the tab centers at hull Y ≈ +57.5 mm (was +73.5 mm); confirm mortise center in cargo SCAD matches
    - **[x]** Verify wing TE position (hull Y≈+122 mm port, +117 mm stbd) clears cargo-section aft interior features; cargo aft boundary is hull Y≈+132 mm — 10 mm clearance

- [ ] **SPAR-01 — spars do NOT carry through the fuselage; adopt the two-bearing
    overhung shaft + CF thwart pair.** *(owner direction 2026-08-23: the 8 mm steel
    spars rotate **independently**, driven by the nacelle servos, on a wingtip
    bearing and a fuselage-side bearing.  Verified by
    `tools/wing_spar_carrythrough.py`.)*  **Resolves CARGO-01.**

    Relationship to `docs/TILT_SPAR_ANALYSIS.md` §1: the drive servo stays **inside
    the fuselage** as §1 has it — what changes is that there are now **two
    independent servos, one per side, mounted on the port and starboard bulkheads**
    (owner, 2026-08-23), and that the root bearing moves from "inside the cargo bay"
    to **in the fuselage side wall**.  §1's single spar running "cargo bay → wing →
    nacelle" and its single cargo-bay root bearing are superseded; its servo
    *location* is not.  Servo mount deconfliction is **SPAR-02** below.

    **1. Carry-through is not required, and independent rotation forbids it.**
    Two coaxial shafts cannot be one rigid beam and still rotate independently, so
    a continuous carry-through spar is ruled out by the mechanism before any
    structural argument.  It is also not needed.  Per side the spar is a
    determinate **overhung shaft** — fuselage-side bearing and wingtip bearing,
    with the nacelle on the overhang — so its statics never reach the far side.
    Measured from the baked STLs (hull frame, port; X positive = port):

    | Station | X |
    | --- | --- |
    | fuselage wall skin at the spar station | −81.33 |
    | spar bearing seat (existing boss mid-span) | −80.00 |
    | spar inboard end if it stops at the boss | −100.00 |
    | wing tip face (wingtip bearing) | +6.70 |
    | nacelle duct axis (load line) | +45.00 |

    → span **L = 86.7 mm**, overhang **a = 38.3 mm**, wall-to-load arm
    **d = 126.3 mm**.  Loads per side from AUW 3.911 kg (8.62 lbm, `README.md`
    Phase 5–10) over 2 nacelles, at the `docs/structural_analysis.md` §3 factors
    (4 g limit = 3 g gust + 1 g maneuver, ×1.5 ultimate).  Spar section 8 mm OD ×
    1.5 mm wall 4130, **I = 170 mm⁴, Z = 42.6 mm³**:

    | Case | Load | R_tip | R_fus | M_spar | σ | FOS on yield |
    | --- | --- | --- | --- | --- | --- | --- |
    | 1 g | 19.2 N (4.31 lbf) | 27.6 N | −8.5 N | 0.73 N·m | 17.2 MPa | 26.7 |
    | limit (4 g) | 76.7 N (17.24 lbf) | 110.6 N | −33.9 N | 2.94 N·m | 69.0 MPa | 6.7 |
    | ultimate | 115.1 N (25.87 lbf) | 165.9 N | −50.8 N | 4.41 N·m | 103.5 MPa | **4.4** |

    The fuselage-side bearing sees only **50.8 N (11.4 lbf)** at ultimate, and it
    acts *downward* (the nacelle overhang levers the inboard end down).  Note the
    4130 yield used is the 460 MPa "typical" figure — MMPDS verification is still
    open as root `TODO.md` §0.8.

    **2. What DOES have to cross the ship is the couple, not the spar.** Each side
    hands its wall **V = 115.1 N with M = 14.54 N·m (128.7 lbf·in)** at ultimate,
    and in symmetric flight the port and starboard couples are equal and opposite.
    A carry-through spar would short-circuit that pair through a straight member;
    with the spar stopping at the wall the **section** must close it instead.

    **3. The stiffener the design already assumes is not closed.** The
    `CF-PLATE-2MM` ring at cargo Y +30 is specified as a "full closed ring —
    anti-ovalisation at spar pin load introduction" (`docs/structural_analysis.md`
    §5), but its **bottom chord (Z +1.5…+3.0, X −256.1…−82.6) is cut away by the
    clamshell aperture**; only the top and two side chords survive.  It is a
    three-sided frame, not a ring, and a three-sided frame is exactly the wrong
    shape for a spreading couple.  It is also now **8.15 mm forward of the Rev S1b
    spar station** and its DXF is still flagged PROVISIONAL in `bom_revS.csv`.
    **No closed ring is possible anywhere between Y +2 and +108** — that is the
    door.

    **4. Therefore: CF thwarts fore and aft of the bay, as the owner proposed.**
    Sited on measured-intact structure (belly and both flanks present; the fore
    gear bays open the flanks ≈ Y −26…+18 and the aft bays ≈ Y +86…+106, so the
    only clear bands are **Y −66…−32**, **Y +56…+86** and **Y +110…+125**).
    Recommend **Y −40 fore** and **Y +118 aft**, which straddle the spar station
    almost evenly:

    | Thwart | Share of the couple | M | σ | FOS |
    | --- | --- | --- | --- | --- |
    | fore, Y −40 | 0.51 | 7.35 N·m | 35.3 MPa | **8.5** |
    | aft, Y +118 | 0.49 | 7.19 N·m | 34.5 MPa | **8.7** |

    Section: **2 mm × 25 mm CF plate** (existing `CF-PLATE-2MM` stock, Z = 208 mm³).
    The FOS column above uses a deliberately conservative **300 MPa** cross-ply
    bending stand-in — a factor of 5 below the only CF figure this repository
    carries (`docs/structural_analysis.md` §1, ≈1 500 MPa **unidirectional**
    pultruded, itself marked as needing supplier certificates).  Against that
    unidirectional figure the FOS would be 42.5.  **Neither is a verified allowable
    for a plate in bending**; logged in `REFERENCES.md` "requires verification" with
    an ASTM D3039/D695 action before the thwarts are cut (root `TODO.md` §0.8).
    Even at the conservative end the margin is 8.5, so the *sizing conclusion* does
    not hinge on which figure is right — only the final certification does.
    Mass ≈ 2 × 25 × 175 mm ×
    1.6 g/cm³ ≈ **14 g (0.031 lbm) each, 28 g (0.062 lbm) the pair** — against the
    ≈78 g the provisional Y +30 ring would have cost, so this is a **net saving of
    ≈50 g (0.11 lbm)** as well as a stiffer load path.

    **5. Consequences to carry.**
    - **CARGO-01 is resolved by this.** With the spar terminating at the boss
      (X −100 port, −240 starboard) the bay clear span is **X −240…−100 = 140 mm**
      and the full bay height is available — the 4 × 3 × 3 in payload fits.
      Re-run `tools/cargo_bay_envelope.py` once the shell is re-cut; it will still
      fail until then, which is the intended behaviour.
    - **CARGO-02** (shell bores Ø12.3 for the retired 12 mm tube) must be closed in
      the same shell edit: the bore becomes a **bearing seat**, not a clearance
      hole, and it no longer runs the full lateral span.
    - `docs/TILT_SPAR_ANALYSIS.md` §1 still describes a **cargo-bay servo** driving
      the spar and a **root bearing inside the cargo bay**; both are superseded by
      the nacelle-servo drive and the in-wall bearing.  Update it, and re-check §3.2
      torsion — the torque path is now short (nacelle servo to nacelle) instead of
      running the length of the spar, which can only reduce wind-up.
    - Retire or re-scope the Y +30 cargo ring in `bom_revS.csv` and
      `docs/structural_analysis.md` §5 rather than finalising its PROVISIONAL DXF.

    **Open sub-steps:**
    - [ ] Owner confirms the thwart stations (Y −40 / +118) before geometry work.
    - [ ] Re-cut the shell: spar bore → bearing seat, terminate at the wall.
    - [ ] Author the two thwarts + their landing pads; re-run the cargo merge.
    - [ ] Re-verify with `cargo_bay_envelope.py` and `wing_spar_carrythrough.py`.
    - [ ] Update `TILT_SPAR_ANALYSIS.md` §1/§3.2 and `structural_analysis.md` §5.

- [ ] **SPAR-02 — bulkhead servo mounts: deconflicted, but the pad is undersized.**
    **2026-08-25 status: torque re-derivation and current-rail resizing sub-items
    are CLOSED (see item 1/2 below) — DS3225 stands, no part change; remaining
    open work is the mounting bolt-pattern verification (item further below),
    unrelated to load/power sizing.**
    *(owner direction 2026-08-23: 25 kgf·cm+ servos inside the fuselage, against the
    port and starboard bulkheads, each driving one spar and its nacelle.  Checked by
    `tools/nacelle_servo_deconflict.py`, which pulls every neighbour live from
    `merge_cargo_interior.py` so it cannot drift from the shell it checks.)*

    **Deconfliction result — all four named conflicts CLEAR.**  Servo body envelope
    (SPT5425LV 40.5 × 20 × 40.5 mm, 57 g, 26 kgf·cm @ 6 V, [REF-SENSOR-013], plus a
    6 mm/end ear allowance) seated on the pad's inboard face at
    X −100 (port) / −220 (starboard), spanning Y +25.20…+77.70, Z +78.67…+119.17;
    horn swing taken as R22 for the −5°…140° throw:

    | Neighbour | Body gap | Horn gap |
    | --- | --- | --- |
    | spar bearing seat | flush at the mounting plane (0 mm³ overlap) | 20.00 mm |
    | wing root mortise | 5.77 mm | 20.40 mm |
    | LG bay fore (port / stbd) | 4.55 / 4.36 mm | 27.20 / 27.02 mm |
    | LG bay aft (port / stbd) | 8.06 / 7.89 mm | 30.49 / 30.31 mm |
    | avionics bay Inara / River | 25.83 mm | 24.87 mm |

    The zero gap to the spar bearing seat is a **coplanar face-touch, not a
    collision** — the pad and the spar boss are both placed off the same
    `PORT_INB`/`STBD_INB` datum, so meeting exactly at that plane is by
    construction, and the boolean overlap is 0.0 mm³.  The tool distinguishes the
    two cases explicitly so this is not re-raised as a defect later.

    **RESOLVED 2026-08-23 (Rev S1d, owner): pads rebuilt for LibreServo_v4.**  The
    tilt servos are now **DS3218MG bodies fitted with the LibreServo_v4 PCB**.
    That fork does not change the envelope — its README states no bottom-cover
    change is needed, and its only mechanical part (`3D/LS_body.stl`,
    13 × 13 × 8.45 mm) replaces the potentiometer *inside* the case — so the pad
    sizes to the bare servo body, and Findings 1 and 2 below are what had to change.

    Rebuilt in `merge_cargo_interior.py`:

    | Constant | Was | Now | Why |
    | --- | --- | --- | --- |
    | `NSVMT_PAD_W` (Y) | 52.0 | **61.5** | 40.5 body + 2 × 7.0 ear allowance + 2 × 3.5 relief |
    | `NSVMT_PAD_H` (Z) | 30.0 | **47.5** | 40.5 body + 2 × 3.5 relief |
    | `NSVMT_DZ` | 30.5 | **40.72** | floor datumed off the gear-bay tops — see below |
    | `NSVMT_Z` | +98.92 | **+109.14** | derived |
    | `NSVMT_HOLES_ENABLED` | (always cut) | **False** | ear pattern still unverified |

    **The floor datum was wrong, and not in the way Finding 1 assumed.**  My first
    pass said to grow upward off the spar boss crown (Z +79.42).  Measured, the
    **Rev R6 landing-gear bay seats top out at Z +82.39 — 2.97 mm above the boss**
    — and the pad overlaps both bays in Y (pad Y +20.70…+82.20 against the fore bay
    to +25.87 and the aft bay from +68.89), so Z separation is the entire margin.
    Datuming off the boss left only **1.53 mm** over the bays.  The floor is now set
    from the bay tops plus the 3.0 mm budget: floor Z +85.39, crown Z +132.89.

    Result — every clearance now passes, and most improved:

    | Neighbour | Servo body | Servo **pad** |
    | --- | --- | --- |
    | spar bearing seat | 9.47 mm (was flush) | 5.97 mm |
    | wing root mortise | 15.99 mm | 12.49 mm |
    | wing root tenon | 20.88 mm | 17.38 mm |
    | LG bay fore | 8.45 mm (was 4.55) | **3.00 mm** |
    | LG bay aft | 11.09 mm | **3.00 mm** |
    | avionics bay | 15.61 mm | 12.11 mm |

    Pad fit is now **+9.0 mm in Y and +7.0 mm in Z** (was −0.5 and −10.5).  The
    gate's servo-pad findings are gone; what remains in its output is all
    shell-side (CARGO-03/03b/04).

    `tools/wing_root_deconflict.py` gained a **`servo PAD`** probe in the same
    edit — it previously checked only the servo body and its horn, which would have
    missed this entirely, since the pad is wider than the servo by design and it is
    the pad, not the servo, that reaches toward the gear bays.

    **UPDATE 2026-08-23 — the datasheet arrived, and it corrected the mounting
    orientation as well as the numbers.**  Sized on
    `avionics/datasheets/DS3218 datasheet.pdf`, then confirmed unchanged against
    `DS3225 datasheet.pdf` when the part moved for torque (same drawing, same
    size).  Authoritative figures: **40 × 20 × 40.5 mm, 60 g, 54.5 mm flange span,
    49.5 × 10 mm bolt pattern**, flange 27.7 mm above the body base.

    The correction that mattered: a standard servo's four screws run **parallel to
    the output shaft**, through a flange perpendicular to it.  The tilt drive needs
    the shaft along hull X, so the **flange** lies in the Y-Z plane on the bulkhead
    and the **40.5 mm height is the inboard depth, not the footprint**.  The pad
    footprint is therefore **54.5 (Y) × 20 (Z)**, not 54.5 × 40.5 — my
    standard-size-class estimate had the wrong face on the wall and oversized the
    pad in Z by 20.5 mm.  Rebuilt again:

    | Constant | Class estimate | Datasheet |
    | --- | --- | --- |
    | `NSVMT_PAD_H` (Z) | 47.5 | **27.0** |
    | `NSVMT_DZ` | 40.72 | **30.47** |
    | `NSVMT_Z` | +109.14 | **+98.89** |
    | bolt pattern | 35 × 16 (unverified) | **49.5 × 10** |
    | `NSVMT_HOLES_ENABLED` | False | **True** |

    Pad fit is **+7.0 mm on both axes**; the floor still holds the 3.00 mm budget
    over the landing-gear bay tops.  The bores are now live, because the pattern is
    sourced.

    **Two things the datasheet exposed that are NOT geometry:**

    1. **Torque — part changed to DS3225 the same day; still marginal.**  The
       owner supplied the 25 kg variant's datasheet after the DS3218 shortfall was
       raised.  **DS3225 is dimensionally identical** (same drawing, same §2-1
       size), so **the pads above are unchanged by the swap** — a useful property:
       the pad is common to this whole body family.  Torque against the
       **≥ 25 kgf·cm (2.45 N·m)** requirement (`docs/TILT_SPAR_ANALYSIS.md` §2,
       from `serenity-rev-r.jsx` L383):

       | Rail | DS3218 | DS3225 | % of requirement |
       | --- | --- | --- | --- |
       | 5.0 V | 18.0 kgf·cm | 21.0 kgf·cm | 84 % |
       | 6.0 V (interp.) | ~19.7 | ~22.9 | 92 % |
       | 6.8 V | 21.5 | **24.5** | **98 %** |

       The "25kg" in the product name is the marketing figure; the spec table maxes
       at 24.5.  So DS3225 nearly clears it and DS3218 did not, but neither clears
       it on datasheet figures alone.  LibreServo_v4 re-drives from 4.5–18 V and
       may close the last 2 %, though no converted-unit figure exists.

       **Before buying a larger servo, re-derive the requirement.**  ≥ 25 kgf·cm is
       cited to `serenity-rev-r.jsx` L383 as a spec pick, not a derivation, and
       §2 of the same analysis records the pivot as being **at the nacelle CG** —
       which nulls the gravity moment by design and leaves only aero and inertia.
       A 2 % gap against a possibly-stale requirement is not worth a part change.

       **Re-derived 2026-08-25 (`docs/TILT_SPAR_ANALYSIS.md` §2.1) — DONE, DS3225
       STANDS.**  Gravity is nulled to within a 0.00185 N·m (0.019 kgf·cm) bound
       on the two asymmetric off-axis parts (spar crank + pushrod; the axial CG
       coordinate is exact by construction, `PIVOT_Z` was set equal to the
       computed CG_Z).  Inertia, from the mass table's own 11-item moment of
       inertia about the pivot (I = 7.189e-4 kg·m²) and the repo's *only* cited
       tilt-transition figure (stale Phase-3 145°/500 ms slew test, triangular-
       profile bound, ×6 for the 4 g/1.5× ultimate convention) is ≈ 0.175 N·m
       (1.78 kgf·cm).  **Grounded total ≈ 1.80 kgf·cm — 7.3 % of DS3225's cited
       24.5 kgf·cm at 6.8 V**, a wide margin.  Aero moment about the tilt axis
       could not be grounded (no nacelle Cd/frontal-area/dynamic-pressure figure
       exists anywhere in the repo) and is left an explicit open item, not
       assumed zero — but it would need to be roughly an order of magnitude
       larger than the wing's own cited lift/thrust figures to threaten this
       margin.  **DS3225 clears the actual (aero+inertia) requirement by a wide
       margin; the old ≥25 kgf·cm figure was itself the stale artifact.  No
       servo change on load grounds.**
    2. **Stall current is now cited, and it is higher than the budget — but not
       RAIL-2's budget.**  1.9 A @ 5 V / **2.3 A @ 6.8 V** (DS3225).  **Correction,
       2026-08-25:** the "1.2 A placeholder RAIL-2 was sized on" language here and
       in `REFERENCES.md`/`current-specification/bom_revS.csv` was a citation
       error — `RAIL-2` (`5V_OBS`, `docs/POWER_DISTRIBUTION.md` §3.2.1/§11.1) is
       the Flight Engineer payload rail feeding the **Observer vision boards and
       the cargo-winch servo** (`docs/CARGO_WINCH_SPECIFICATION.md` §5.4); its
       1.2 A figure is the STS3215/SPT5425LV-era **winch-servo** placeholder, not
       a tilt-servo budget.  The nacelle tilt servos are powered from the
       separate **6 V servo bus** (`docs/POWER_DISTRIBUTION.md` §3.3, "PDB 6 V
       BEC output" in §4) which carried forward a DS3218MG-era 1.5 A stall
       figure per servo.  That 6 V rail — not RAIL-2 — is the one resized here
       to DS3225's cited 2.3 A stall (see `docs/POWER_DISTRIBUTION.md` §3.3/§3.4
       for the corrected figures).  RAIL-2 itself is unaffected by the DS3225
       swap and is left at its existing winch-servo-driven 1.2 A placeholder.

    Original open item, now partly closed:

    **Still open — the bolt pattern, and now the body dimensions too.**  DS3218MG
    has *no* cited dimensional source in this repository (the BOM recorded it as
    "(uncited)" when it was superseded on 2026-08-02).  The pad is therefore sized
    to the **standard-size servo class** off REF-SENSOR-013's 40.5 × 20 × 40.5 mm,
    which the BOM itself says is interchangeable, and the four M3 bores are
    **gated off** (`NSVMT_HOLES_ENABLED = False`, the same gate pattern as
    `LG_BAY_ENABLED`).  A pad that is 9 mm oversized is harmless; four bores on a
    guessed pattern are not, and a wrong hole cannot be un-drilled.  Logged in
    `REFERENCES.md` "requires verification".

    Original findings, retained for the record:

    **Finding 1 — the pad does not fit the servo.**  `NSVMT_PAD_W` × `NSVMT_PAD_H`
    is 52 × 30 mm against a servo footprint of 52.5 × 40.5 mm:

    | Axis | Servo needs | Pad has | Margin |
    | --- | --- | --- | --- |
    | Y | 52.5 mm | 52.0 mm | **−0.5 mm** |
    | Z | 40.5 mm | 30.0 mm | **−10.5 mm** |

    A servo overhanging its pad lands on raw 2 mm skin, which is not a mounting
    surface for a 2.55 N·m actuator.  **Grow the pad upward, not downward:** the
    spar boss crown is at Z +79.42 and the pad floor is at +83.92 (the documented
    4.5 mm boss clearance), so downward growth eats that gap, while upward growth
    is unobstructed to Inara/River at Z +145 — 20.6 mm of room after a 40.5 mm pad.
    That means `NSVMT_PAD_H` 30 → ≈46 and `NSVMT_Z` +98.92 → ≈+104.17
    (`NSVMT_DZ` 30.5 → 35.75).  **Consequence to carry:** raising the servo 5.25 mm
    changes the horn/pushrod geometry, so it re-opens the open §1.1.3 item "Tune
    servo→spar horn/pushrod linkage throw (−5°…140°)" — settle the pad first, then
    the linkage, not the other way round.

    In Y the shortfall is 0.5 mm and rests entirely on the 6 mm/end **ear
    allowance**, which is this tool's own conservative number, not a datasheet
    figure — see Finding 2.  Do not grow the pad in Y on the strength of it: the
    fore landing-gear bay is only 4.4 mm away, and that is the tightest real
    clearance on the whole mount.

    **Finding 2 — the bolt pattern is unvalidated.**  The shell drills
    `2 × NSVMT_HOLE_S_Y` × `2 × NSVMT_HOLE_S_Z` = **35 × 16 mm**.  [REF-SENSOR-013]
    publishes the SPT5425LV body as 40.5 × 20 × 40.5 mm but **does not publish the
    ear span or the hole spacing**, and root `AGENTS.md` §4 forbids guessing one.
    The 35 × 16 pattern predates this servo — it was drawn for the uncited DS3218MG
    the BOM replaced on 2026-08-02 — so it is very unlikely to be right and must not
    be cut on faith.  Logged in `REFERENCES.md` "requires verification".

    **Finding 3 — the cableways are clear of the servo, but not of everything.**
    Owner requirement: the nacelle ESC and nav-light cableways must not be blocked.
    Against the servo they are — the EDF ESC conduit, the Hall/encoder conduit and
    the spar bore all clear the servo body and its horn swing entirely.  Two are
    blocked by *other* things, tracked in `airframe/fuselage-mid/WBS.md` §1.1.1.2
    as **CARGO-03** (the wing root mortise never penetrates the bulkhead, so the
    aft ESC conduit has no path) and **CARGO-04** (the Hall conduit at 0.33 c lies
    inside the rotating spar at 0.35 c — a Rev S1b regression).  The nav light is
    satisfied as the owner expected: it rides the spar's ~5 mm ID and that bore is
    verified THROUGH.

    **Finding 4 — the wing root tenon is on a different datum from its mortise,
    and it is 0.23 mm from the spar bearing seat.**  `fuselage_root_tab()` centres
    the tenon on the wing **chord line** (hull Z +58.01); the shell centres the
    mortise on **`WING_ROOT_Z`** (hull Z +62.50).  4.49 mm apart against a 0.4 mm
    design clearance, so the tenon's lower 4.09 mm lands on solid wall — the sizes
    are right (30.0 × 20.0 in 30.8 × 20.8), only the datum is wrong.  Separately,
    the tenon's forward face (49.5 mm chordwise) now sits **0.226 mm** from the
    Rev S1b spar bore and 0.376 mm from the spar tube; before S1b that gap was
    ~23 mm.  Both are tracked with the fix in `airframe/fuselage-mid/WBS.md`
    §1.1.1.2 **CARGO-03b**, because the mortise and the tenon are one joint and
    must be re-datumed in a single coordinated edit across the two files.

    **Correction to the first pass:** the tenon depth is *not* simply "fine".  It
    clears geometrically — 12 mm insertion into a ~16 mm wall, 10.66 mm from the
    servo — but the owner has since established (2026-08-23) that the mortise/tenon
    joint **carries structural load**, because the wings do not rotate with the
    nacelles and, under SPAR-01, spanwise load now terminates at the wall.  The
    tenon therefore takes **165.9 N shear and 14.60 N·m at ultimate**, developing
    10.14 MPa bearing on its mortise faces, and it has never been sized against
    any of that.  `fuselage_root_tab()`'s comment ("The tab provides radial
    restraint; the CF spar carries spanwise load") is now wrong and must be
    corrected with the datum fix.  Full sizing, and the missing CF-PETG bearing
    allowable that blocks it, are **CARGO-03c**.

    **Open sub-steps:**
    - [ ] Measure ear span + hole spacing on a real SPT5425LV, or obtain a
        dimensioned drawing; add it to [REF-SENSOR-013].
    - [ ] Resize the pad (Z first) and re-site `NSVMT_Z`; re-run
        `tools/nacelle_servo_deconflict.py` — it must reach CLEAR.
    - [ ] Re-tune the horn/pushrod throw against the new servo height (§1.1.3).
    - [ ] Confirm the 4.4 mm fore-gear-bay gap survives the final pad outline.

- [x] **SPAR-04 — the Hall cable's wingtip jog runs straight through the spar
    bore. CLOSED 2026-08-23 by the Rev S1c merge — see the closure note below.** *(found 2026-08-23 while applying the Rev S1c Hall station; measured
    from the SCAD constants.)*  **BLOCKS the tilt-encoder harness.**

    `hall_sensor_cableway()` ends with a chordwise jog at the tip, from the
    spanwise conduit across to the sensor pocket at `SPAR_BORE_STATION +
    HALL_SENS_R`.  The sensor reads a diametric magnet **off-axis**, 11 mm aft of
    the spar axis, so the pocket is at chordwise **56.15 mm** — and the spar bore
    spans **41.00…49.30 mm**.  The jog therefore crosses the bore:

    | Hall station | Tip conduit x | Sensor pocket x | Jog length | Crosses the spar bore? |
    | --- | --- | --- | --- | --- |
    | 0.33 c (before Rev S1c) | 30.69 mm | 56.15 mm | 25.46 mm | **yes** |
    | 0.23256 c (Rev S1c) | 21.63 mm | 56.15 mm | 34.52 mm | **yes** |

    **This is pre-existing, not caused by the Rev S1c move** — the jog crossed the
    bore at the old station too.  What the move changes is its length, 25.46 →
    34.52 mm, so it crosses over a longer run.  Both the jog and the bore are cut
    as voids, which is why no boolean ever complained: two voids simply merge.  The
    physical consequence is what matters — at that station the **rotating spar
    occupies the bore**, and a cable cannot pass through a turning shaft.

    Note this is the same defect class as CARGO-04's: a route checked against
    *material* looks fine, because the thing blocking it is another moving part
    rather than plastic.  `tools/wing_root_deconflict.py` catches that at the root
    (it carries an explicit `rotating spar tube` obstruction); it does **not** yet
    model the tip jog.  Extend it before this is called closed.

    **CLOSED 2026-08-23 — fixed as a side effect of the Rev S1c reroute.**  None of
    the three options below was needed.  `feat/wing-spar-s1c-cableway-reroute`
    converted the Hall conduit from a chord FRACTION to a **constant 54.0 mm
    station**, so its tip end no longer walks forward as the chord tapers: it stays
    at 54.0 mm, against a sensor pocket at 56.15 mm.  The jog is now **2.15 mm**
    (was 34.52), and it **does not reach the spar bore at all** (41.00…49.30 mm) —
    the conduit already emerges aft of it.

    Worth keeping as a lesson: the jog was long only because the conduit's law
    (chord fraction) differed from the spar's (constant mm), so the two diverged
    outboard.  Putting both on the same law removed the divergence and the jog with
    it.  The same mismatch is what caused the original conduit-in-spar collisions.

    Fix options as originally tabled, retained for the record:
    1. Route the jog **around** the spar in thickness, over or under the bore.  The
        tip section is thin (t/c 19.47 % of a 93 mm chord after Rev S1b), so check
        the skin wall before assuming there is room.
    2. Move the sensor pocket so the jog no longer has to cross — but
        `HALL_SENS_R` = 11 mm is set by the magnet ring's mean radius, so this
        means re-siting the magnet, not just the pocket.
    3. Take the lead out through the **nacelle** side instead of back down the
        wing, if the encoder can be read from a harness that stays outboard.

- [ ] **★ WING-01 — the tabulated S1223 section is not a valid airfoil: the
    surfaces cross at x/c 0.742 and the outline self-intersects.**
    *(owner asked 2026-08-23: "verify that the airfoil doesn't create a zero
    thickness point that would cause a gap partway toward the trailing edge, as
    some of the drawings show."  It does.  Gated by
    `tools/wing_airfoil_integrity.py`, which fails closed.)*
    **BLOCKS wing fabrication, the mass budget, and any aero claim.**

    `S1223_UPPER` falls below `S1223_LOWER` over the aft quarter of the chord, so
    section thickness goes **negative from x/c ≈ 0.742**, bottoming at
    **t/c −0.0152 (−1.96 mm root / −2.05 mm tip) at x/c 0.90**, before both
    surfaces return to zero at the TE.  Shapely reports the outline invalid with a
    self-intersection at (0.7417, 0.0235).  A drawing that renders the outline
    shows exactly what the owner saw: the surfaces pinch to zero partway back and
    cross into a bowtie.

    **Why nothing caught it.**  Two independent reasons, and both are worth
    fixing as process:

    1. `wing_spar_station_fit.py` and `wing_internal_clearance.py` both ask "does
        a **bore** fit inside this section?".  Neither asks whether the section is
        a valid simple polygon to begin with.
    2. `wing_solid()` lofts with OpenSCAD **`hull()`**, which takes the CONVEX
        HULL of each section.  The convex hull of a self-intersecting outline is
        still a clean convex region, so the exported STL is watertight, single-
        bodied, and passes `tools/validate_stls.py`.  **The exported STL is not
        evidence here** — measured on the built wing, thickness runs a healthy
        12.7 mm at 0.60 c down to 1.5 mm at 0.975 c with no gap at all.

    **The masking is not free.**  Convex hull area is **1.647×** the tabulated
    outline's — it fills the airfoil's concavity *and* swallows the bowtie — so
    **39.3 % of the built section's area is material the section does not call
    for**.  The built wing is therefore materially not an S1223, which propagates
    into wing mass, into every aero figure, and into the Rev S1b camber-
    preservation work (thickness-only scaling preserves a camber line that
    `hull()` then discards).

    **What is NOT affected.**  Internal-clearance results are *conservative*, not
    wrong: the hull is strictly larger than the outline, so a bore that clears
    inside the tabulated section has at least as much material around it in the
    built part.  `wing_internal_clearance.py`'s PASS and the Rev S1c conduit
    stations stand as lower bounds.

    **Comparison against published Selig S1223** — the aft upper surface is the
    part that is wrong, by a roughly constant offset that grows from x/c 0.8:

    | x/c | repo `S1223_UPPER` | Selig S1223 | delta |
    | --- | --- | --- | --- |
    | 0.80 | +0.0082 | +0.0431 | −0.0349 |
    | 0.85 | −0.0020 | +0.0318 | −0.0338 |
    | 0.90 | −0.0089 | +0.0210 | −0.0299 |
    | 0.95 | −0.0109 | +0.0109 | −0.0218 |
    | 1.00 | 0.0000 | 0.0000 | 0.0000 |

    **This item is NOT closed by a fix, deliberately.**  Correcting it means
    replacing the coordinate table, and root `AGENTS.md` §4 forbids sourcing that
    from memory — the Selig column above is a comparison, not a transcription to
    paste in.  The table must come from a validated source (UIUC Airfoil
    Coordinates Database), be added to `REFERENCES.md` with a validated URL, and
    only then replace `S1223_UPPER`/`S1223_LOWER`.

    **Open sub-steps:**
    - [ ] Obtain S1223 coordinates from the UIUC database; add a `REF-CAD-*`
        entry with a validated URL and the retrieval date.
    - [ ] Replace both tables; `tools/wing_airfoil_integrity.py` must reach PASS.
    - [ ] Decide `hull()` vs a true loft.  Even with a correct table, `hull()`
        convexifies away S1223's concavity — check the ratio the gate reports and
        move to a swept/lofted solid if it stays above tolerance.
    - [ ] Re-render and re-bake both wings; re-run `wing_internal_clearance.py`
        and `wing_root_deconflict.py` against the corrected section.
    - [ ] Re-derive wing mass and re-check the §1.1.2 aero figures.

##### 1.1.2.1 *Rev R1a — spar straightened + camber-centered + EDF cableway (2026-07-07)*

- [x] **Spar bore de-skewed** — `wings_s1223_revo.scad`: replaced the constant-30%-
    chord-fraction bore (which walked 10.8 mm / 7.2° forward over span under the
    straight LE — the "swept" cutout) with a bore at a **constant chordwise station
    (`SPAR_BORE_STATION` = 22 mm)** → parallel to the LE. Bore center height now
    reads the **actual S1223 camber midline at each station** (`midline_frac()`),
    fixing the Rev R1 chord-line centering that broke out the lower surface AND the
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

- [x] **Re-merge the cargo shell.** **CLOSED 2026-08-23 — the re-merge has already
    happened; this item was stale.**  `merge_cargo_interior.py` carries the new spar
    station/height **and** the LG-10.4 wing keep-outs, and the published
    `cargo_sect_shell24_2mm_repaired.stl` now carries both.  Verified three ways
    against the published STL, not against the script:
    - **Spar station.** A Ø10 probe rod placed on each candidate axis and
        intersected with the shell: the **Rev S1b axis (Y +38.15, Z +68.42) is
        clear — 0.0 mm³**, i.e. the bore is cut there; the **pre-S1b axis
        (Y +31.70, Z +66.53) is solid — 1 500.3 mm³** of wall, i.e. the old bore is
        gone.  Controls through undisturbed 2 mm wall read 333–369 mm³, which is
        the expected 2 × π × 25 × 2 ≈ 314 mm³, so the probe is calibrated.
    - **LG-10.4 wing keep-outs.** `tools/landing_gear_wing_clearance.py` → **CLEAR**
        on all four checks (aperture/rebate vs wing material, bay material vs wing
        voids, 64 bolt-bore pairs, 128 bolt-vs-servo-pilot pairs — no intersection
        anywhere).
    - **Mesh health.** `tools/validate_stls.py` passes **62/62**; the shell is
        watertight, 0 boundary, 0 non-manifold, 1 body, 908 106 faces,
        295 931 mm³.  `tools/landing_gear_bay_seat_fit.py` also reports **CLEAR**
        (datum drift 0.00 mm both stations, 0.000 mm³ interference at all four
        corners, worst shim 1.14 mm against a 1.5 mm budget).

    **Carried forward, not closed by this:** the shell's spar bore **diameter** is
    still the retired 12.3 mm, not the wing's 8.3 mm — tracked separately as
    **CARGO-02** in `airframe/fuselage-mid/WBS.md` §1.1.1.2.

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
    (`tools/wing_airfoil_variants.py`). Consequential fix: the bore-center
    expressions (`spar_tip_y()`, `spar_bore()`, cableway, Hall-cable) no longer
    multiply `midline_frac()` by the thickness scale — doing so would now lift
    each bore off the camber line it is meant to be centered on.

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
    - [x] **Housing aft taper** (Stage 2) toward the cowl mold line; binding
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
    - [ ] **[OPEN — VERIFY] Full housing ovalization** to the cowl mold line +
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
    Crown Pinion at the fixed 28.1 mm center distance; Idler-Out (15T,
    R=7.5mm) meshes the new full-circle ring gear (72T, R=36mm) at a
    43.6 mm center distance. A valid idler-shaft position exists per the
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
    2026-06-22)* — solved the two simultaneous center-distance constraints
    (28.1 mm from Crown Pinion at local (X=0, Y=PINION_A_Y=28); 43.6 mm
    from the nozzle/ring axis (0,0)): shaft position (X=+27.485, Y=33.846),
    i.e. 50.92° from the local +X axis (rounded to 50.9°). The other valid
    mirror solution is 129.08° at X=-27.485 — +X chosen arbitrarily (nothing
    else occupies that sector at this Z station). `IDLER_SLOT_ANG` in
    `nacelle_nozzle_iris.scad` updated to match; idler + bracket placed in
    `serenity_assembly.py` at this (X, Y).
- [x] **idler axial mesh-band mismatch — RESOLVED 2026-07-04** (user decision:
    offset the Crown Pinion, accounting for CG).  The idler's two gear sections
    are 10 mm apart axially (Idler-In band center at local Z=6, Idler-Out at
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
    `spar_bearing_block()`, `nacelle_servo_mount_block()`) had been modeled
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
    canonical mold line.

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
    (reuses the EDF cableway). Never breaks the exterior mold line.
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
- [x] **Wing (fixed sensor) mount modeled + relocated** *(Rev R2d)* — added
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
- [x] **Nacelle (rotating magnet) hub modeled** *(Rev R2d)* — `nacelle_hall_ring_hub()`
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

