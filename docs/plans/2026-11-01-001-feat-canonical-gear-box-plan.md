# Canonical landing-gear box (cargo-flank rebuild) — plan

Status: **U1 done; U2 done; D1–D3 decided; U3 next.**  Started 2026-11-01.
Branch: `feat/canonical-gear-box` (off `feat/sls-migration` 57437edd).

## Problem

Owner, 2026-11-01: the Rev R6/A1B bays (`tools/generate_lg_bays.py`) are open
bolt frames on the 25° sponson panel.  The thigh hub hangs in free air below
each frame, which leaves a visible gap between the bottom of every leg support
and the hull.  The bays read as boxes added onto a different design
(build-guide card 08).

## Canonical form (Henning model, `docs/references/nick-henning/`)

- `nick-henning-uvdisplay-wing.jpg`: the stub wing is the top plate.  The gear
  box hangs under it as a faceted block: the outboard face leans in, the lower
  chine is bevelled, and the face carries recessed panels and an angled hatch.
- `nick-henning-close-gear-combine.jpg`: each thigh is sleeved in a square
  leg-support pillar that lands on the box, so the thigh emerges from the
  pillar mouth.
- `nick-henning-uvdisplay-gear.jpg`: the upper-leg housing is a square tube
  coaxial with the thigh.

## Measured envelope (R2, port; hull `head_cargo_shell24_2mm_merged.stl`)

| Item | Value |
|---|---|
| Belly plane | Z 80 |
| Lower flank half-width, Z < 95 | X 53–56 |
| Flank half-width, Z 95–150, Y 300–390 | X 84–89 |
| Wing root | Y 311.4–440.4, root Z about 135–160 (`SPAR_Z` 146.85) |
| Door aperture edge | X ±52.25–52.65 |
| Hips (`LG_CORNERS`) | fore (54.95, 289.70, 118), aft (77.61, 405.66, 118) |
| Cargo/middle collar | Y 434.7–436.7 |

## Units

- **U1 — concept envelope (DONE).**
  `airframe/openscad/fuselage/gear_box_canonical_concept.scad` defines the
  box at Z 80–133, X 56→96 at the top and 92 at the chine, over Y 262–433.
  Each pillar is a square sleeve coaxial with the static thigh, clipped to
  the box grown by 3 mm.  The swing slot is swept 0–26°.  Status:
  appearance only.
- **U2 — single source.**  Read the corner poses from `LG_CORNERS` /
  `CORNERS` (the concept copies them) and the datums from `hull_datums.py`.
- **U3 — hull rebuild from source.**  Per [[feedback_rebuild_from_source_builds]],
  fold the box into the cargo-shell build (`merge_cargo_interior.py`
  `lg_bay_features`), replacing the sponson rebate/collar instead of
  bolting a fairing onto the published STL.  The current bays become the
  internal structure inside the box (the pillar is the visible support).
- **U4 — enclose the A1B backbone.**  The CF backbone plates currently
  stand proud of the skin (visible in the renders).  The box shall contain
  them.
- **U5 — keep-outs and gates.**  Re-run the bay gates:
  `landing_gear_bay_function.py`, `landing_gear_wing_clearance.py`,
  `landing_gear_cowl_clearance.py`, `landing_gear_ground_clearance.py`, and
  the door swing, tilt bracket, TACCO pouch, chin shelf, hinge retention
  and collar checks.  Hold port/stbd exact-mirror symmetry
  [[feedback_local_informs_airframe_rules]].
- **U6 — structure and mass.**  Size the SLS PA12-CF wall
  (`/statics-and-dynamics` load path from the leg into the box, then the
  hull), roll the mass into the AUW ledger (14.19 lbm baseline), and check
  the CG effect against the thrust line Y 326.7.
- **U7 — docs and renders.**  Regenerate card 08 and the build guide, and
  add `REF-CAD-HENNING` usage to `REFERENCES.md`.  Regenerate WBS/TODO with
  `tools/gen_todo_from_wbs.py`.

## Owner decisions (2026-11-01)

- **D1 — size:** approved as drawn.
- **D2 — opening:** trapezoidal, as canon, and left as an OPEN slot.  The slot
  flares along the pin axis from 22 mm at the hip to 34 mm at 70 mm down the
  thigh (`SLOT_PIN_MOUTH`).
- **D3 — construction:** merged into the one-piece SLS forward hull.
- **Symmetry:** exact about the centreline.  Done in U2.
- **Structure:** if the CF insert plates don't fit by shape or by insertion,
  use PA12-CF with ribbing or lattice.  Manage weight and balance throughout.

## Findings (2026-11-01)

**U2 (done).** The starboard corner rows were literals mirrored about the
old R1 centreline, 0.1 mm off a true mirror.  They are now derived from the
port rows about `X_CL`:

- In the SCAD: `LG_FORE_PORT` / `LG_AFT_PORT` + `lg_mirror_row()`.
- In `merge_cargo_interior.py`: `_mirror_corner()`.
- `tools/lg_corners.py` is now the one parser, and
  `landing_gear_bay_function.parse_corners()` delegates to it.

`canonical_leg_r6_1_5in.scad` (retired bench gear) still carries -77.71.

**A1B CF backbone vs. the new box.**  `tools/lg_a1b_census.py` FAILS before
and after this branch:

| Corner | Hull clash (mm³) | Keep-out clash (mm³) |
|---|---|---|
| Fore cheeks | 252 | 0 |
| Fore members | 85–132 | 0 |
| Aft cheeks | 0 | 16.5 |

The fore cheeks rise to Z 179 and pierce the flank skin above the box.  So
the plates do not work in their current shape or position.

PA12-CF cannot replace them for the couple.  PA 602-CF publishes only XY
values: 85 MPa tensile, 7,900 MPa modulus, 1.10 g/cm³, and no Z or bearing
allowable (`airframe/datasheets/PA-602-CF-Data-Sheet-2021.pdf`).  The
anchor pin carries 4,593 N × 1.25 on Ø4 mm.  That needs ≥ 17 mm of bearing
wall at the full XY strength and ≥ 30 mm with any orientation knockdown.
This is the same verdict the CF-PETG option got (plan 2026-10-27-001).

**Recommended structure (U3/U6):**

- The couple stays in the CF (TC1225, 3.29 mm) / 6061-T6 backbone.
- The cheeks are re-shaped and re-sited to sit inside the pillar, which is
  canon's "rectangular housing on the hull flank" (plan 2026-10-27-001
  line 90).
- They slide up the pillar from its open mouth into printed guide slots.
  That is the insertion path a one-piece hull allows.
- The fore station (Y 290) is ahead of the wing LE (Y 311.4), so the fore
  pillar may rise above the box top to house the cheek.
- The PA12-CF pillar walls carry only the net foot load: 1,148 N crash ×
  1.25 through the hip pin, two walls, Ø8 mm 6061 spreaders.  That needs
  about 2.1 mm of wall at 0.5 × 85 MPa.  Use 4 mm walls plus ribs.
- The allowable is uncited for PA12-CF bearing, so it **requires
  verification** (coupon, as LG-11).

**Weight and balance (first pass, both sides, concept envelope):**

| Item | Value |
|---|---|
| Exposed box skin | 76,100 mm² |
| Skin mass, 1.5 / 2.0 mm SLS | 82 / 109 g |
| Plus 30 % ribs | 106 / 142 g |
| Replaced Rev R6 bays (4, solid) | 64 g |
| Net change | +42 to +78 g, before cutting away the hull skin buried inside the box |
| Box centroid | Y 353.1, 26 mm aft of the thrust line Y 326.7 |
| CG effect | ≈ +0.3 mm aft at 14.19 lbm AUW |

U6 shall replace this with the ledger (`--write`).

**Coordination hazard.**  Another session has uncommitted edits to
`merge_cargo_interior.py` on `claude/3d-print-material-scaling-66d85n`
(head+cargo shell regen held).  U3 edits the same file.  Sequence U3 after
that lands, or rebase onto it.

## Open owner decisions (superseded — see above)

1. **D1 — box depth.**  The concept puts the outboard face 3–7 mm proud of
   the flank, plus a 3 mm proud band on each pillar.  Is that more or less
   bulk than wanted?
2. **D2 — pillar slot.**  The swing slot leaves the pillar as an open
   U-channel on its outboard face.  Canon shows a closed sleeve, but a closed
   sleeve needs a flexible boot or a smaller stroke.
3. **D3 — box as hull vs. separate part.**  The box can be merged into the
   one-piece SLS forward hull (fewer joints, mass to be measured) or printed
   as a bolt-on per side (serviceable, adds a seam).

## Fore CF plates flush — packaging study (2026-11-01)

Owner: "Reshape the cf plates to be flush.  For the parts of the hull that
can't exactly be canon, try to match the character of the ship."  The
"character" requirement is now in root `AGENTS.md` ("Airframe geometry").

**Forward fairing (added).**  Ahead of the door aperture, the box's inboard
edge comes in to X 36 (`BOX_X_IN_FWD`, Y 262–302), and its 45° top runs on
into the upper skin.  The open notch behind the bridge neck becomes a
faceted cheek block in the gear box's own chamfered vocabulary.  It is
clear of the wing, the flange and every penetration.

**Strut sweep, fore-port.**  Reach 55 mm is fixed by the fuse gauge.  The
hip mask is r 18 mm, as the census masks the open well.  Scripts:
`2026-11-01-001-canonical-gear-box/tools/`.

| Strut az | Proud of OML (mm³) | Wall (mm³) | Keep-outs hit (mm³) |
|---|---|---|---|
| 65 (current) | 6,826 | 569 | none |
| 80 | 2,674 | 985 | none |
| 95 | 257 | 56 | TACCO CN2 port 1,370; chin shelf 98 |
| 110 | 164 | 101 | TACCO CN2 2,487; chin shelf 256; payload 295 |
| 125 | 32 | 69 | TACCO CN2 3,719; chin shelf 401; payload 2,471 |

No reach from 25 to 55 mm passes at any azimuth from −40° to 200°.  The
only flush direction, up and inboard (95–110°), is occupied by the TACCO
CN2 port chin pouch.  **Owner decision D4** (see the session report)
chooses among:

- moving the pouch;
- a shorter fuse;
- a faceted housing ahead of the wing LE.

## D4 resolved — fore legs toward the bow (owner 2026-11-01)

The owner chose to rotate the fore feet toward the bow, which narrows the
stance.  Changes:

- Fore swing azimuth is now −65° (was −22.4°).  Starboard is still derived
  (−115° wrapped).
- Fore A1B strut azimuth is now 80° (was 65°).
- Changed in the leg SCAD, `merge_cargo_interior.py`, and the
  packaging-tool parity table.
- `landing_gear_r6_sizing.Y_FOOT_FORE` is now derived from the corner
  source: 217.2, was a typed 259.2.

**Why 80°.**  The cheeks plus members were rendered for corner −60 to −75 ×
strut 80 to 100 (`tools/fore_cheek_sweep.py`).  At −65 only strut 80 has
zero contact with the raw TACCO CN2 pouch (which has no clearance built in)
and the chin shelf.  Strut 85 touches the pouch by 45 mm³ and strut 90 by
219 mm³.  The 90° overlap lies on the inboard cheek's hip-to-anchor load
line, so notching the plate is not acceptable.

**Flush.**  The plates sit 0 mm³ proud of the box OML, which is now
exported as `PART="envelope_port"`.  The slot interior is not counted as
proud, because the crank end lives in the open slot by design.  To get
there:

- The fore fairing is slimmed to `FAIR_XS` 0.70 (face at X ≈ 84; the hull
  is X 41–74 there) with a 45° top.  A 64° top made it read as a tower.
- The plate tops are housed by a slim faceted fore leg-support housing:
  `strut_housing()`, the cheek outline grown 2 mm, octagonal so it stays
  chamfered.  Henning's leg supports are slim pillars rising to the deck;
  a round-topped housing read as foreign to the ship.
- The housing adds 8,890 mm³ of new skin volume outside the old hull.  Its
  overlap with the pouch and chin shelf is entirely inside the existing
  cavity (0.0 mm³ outside), so it never becomes a wall.

**Stance** (heaviest ledger case: 6,253 g, CG Y 353.9, Z 157.3):

| Item | Before | After |
|---|---|---|
| Fore track | 258 mm | 178 mm |
| Wheelbase | 184 mm | 226 mm |
| Side tip angle | 41.2° | 37.4° |
| Nose-over tip angle | 31.0° | 41.0° |
| Tail-back tip angle (limiting) | 29.6° | 29.6° (unchanged) |

These feed LG-29, the formal tip-over re-derivation.

**Side load — OPEN, gates first flight.**  Sizing reports 308 N/leg in the
±15° lateral case.  `LANDING_GEAR_ANALYSIS.md` §4 still shows 163 N
(stale).  At −65 the out-of-swing-plane fraction is 0.906 (was 0.381):

| Item | At −22.4° | At −65° |
|---|---|---|
| Fore thigh out-of-plane bending | ≈ 26 MPa | ≈ 61 MPa |
| Clevis ear couple | — | ≈ 1.8 kN/ear |

At −65° the printed thigh (2 × Ø14 mm, S 539 mm³) has a factor of 1.4 on
PA 602-CF's 85 MPa XY tensile strength.  There is no Z, impact or fatigue
allowable.  `cf_core` is NOT a candidate: the 2026-10-19 thigh-variant study
(`docs/plans/2026-10-19-001-baseline-r1/lg_thigh_variants.py.txt`) rejected
it.  The rod net section at the cross-pin failed (0.25×), and so did
cross-pin bearing in the lug (0.77×).  Owner 2026-11-01: hold.

The variant that survived that study is "grown" (printed 17/22 mm, worst
margin 1.09×, +11.1 g/leg).  Its out-of-plane section is S ≈ 965 mm³, which
roughly halves the bending, to ≈ 34 MPa.  It is a candidate to evaluate,
not adopted.

**Gates run at −65 / strut 80:**

| Gate | Result |
|---|---|
| `landing_gear_ground_clearance.py` | PASS |
| `export_landing_gear_stls.py` | 3.0 in STLs regenerated.  Pre-existing "bay differs between variants": `lg_r6_common_bay.stl` is unchanged since f3b99128; the retired 1.5 in never got A1B. |
| `lg_a1b_census.py` | FAIL, expected until U3.  It measures against the published shell, whose old flank wall the box replaces.  Fore: 390 mm³ members / 311 mm³ backbone.  It needs a box-aware hull reference once U3 lands. |
| `landing_gear_wing_clearance.py` | CRASHES on its own: 6 seat collars for 4 corners (IndexError).  Same on `claude/3d-print-material-scaling-66d85n`, so it came in with that branch.  The box retires that bay hardware. |

**Pre-existing, found here.**  The AFT cheeks reach X 18.9 and overlap the
payload hoist keep-out by 2,312 mm³.  The census never counted it because
it treats the payload as removable.  A CF plate is not removable, so this
needs its own fix (aft strut azimuth or cheek outline).

Renders: `2026-11-01-001-canonical-gear-box/fore65_port_{bow,quarter,side}.png`.

## U3 — box merged into the one-piece forward hull (2026-11-02)

`tools/gear_box_hull_merge.py`, called by `tools/merge_head_cargo_shell.py`
after the flanges fuse.  The box goes in as 2 mm skin:

- **New skin:** (Bo − Bi) − O − gear.  Walls exist only outside the old
  hull, and they clear the real moving gear.
- **Opening:** ((Bi ∩ O) − I) − protect.  The old flank skin inside the box
  is opened so the cavity drains SLS powder into the hold.
- **Leg path:** (slots ∩ O) − protect.
- **Protect set:** the wing-root flanges, every wing-root penetration, and
  each bolted bay's seat (footprint + 6 mm).  The bays carry the hip pins.

**Result:**

| Item | Value |
|---|---|
| Watertight | yes, 0 bad edges, one body |
| `assembly_integrity_check.py` | PASS: spar bore and flanges on datum, 0 openings |
| Net mass | +105.0 cm³ (≈ 116 g / 0.26 lbm PA12-CF): new skin 111.0 cm³, old skin opened 4.6 cm³, leg path 0.26 cm³ |
| Box-added overlap with the gear | 0.0 mm³ |

The 254 bodies the weld dropped were all ≤ 0.5 mm³ (boolean residue,
checked).  The first build left 3,354 mm³ of skin in the gear.  The
"leg (thigh+shin+foot)" feature omits the hip hub, lug and crank horns, so
the exported `hull_legs` is now part of the gear keep-out.

**Blocker — bolted bays (next).**  Printed bays outside hull ∪ box, mm³:

| Bay | Outside | Into wing | Note |
|---|---|---|---|
| fore-port | 843 | 0 | still at the OLD −22.4° orientation |
| fore-stbd | 1,481 | 0 | still at the OLD −22.4° orientation |
| aft-port | 313 | 177 | wing clash is LG-AFT-BOLT-01 (wing shift) |
| aft-stbd | 627 | 177 | wing clash is LG-AFT-BOLT-01 (wing shift) |

The aft-stbd upper corner stands to Z 158, above the box and the wing
underside (owner, pq_wing.png).  Fix: regenerate with
`generate_lg_bays.py`, with the box as a keep-in and the fore pair at −65.
The `hull_legs` render also carries the generic SCAD `bay()` plate, which
is untrimmed and shows the same protrusion.

**Side load (review item).**  The sizing tool's printed-leg bending
allowable is 27.5 MPa (CF-PETG yield/2).  Out-of-plane thigh bending at
308 N/leg, fore −65°, against that allowable:

| Thigh | Bending | Margin |
|---|---|---|
| Baseline 2 × Ø14 | ≈ 61 MPa | 0.45× |
| "Grown" 2 × Ø17 | ≈ 34 MPa | 0.81× |

Both are before combining with the in-plane crash bending.
`landing_gear_r6_sizing.py` has no out-of-plane thigh check at all.
