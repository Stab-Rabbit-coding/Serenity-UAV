---
title: "fix: Reconcile nacelle nav-light wire routing with the hollow tilt-spar decision; finish AK7455 wing-side geometry"
date: 2026-08-29
plan_type: fix
execution: geometry
status: superseded
superseded_by: docs/plans/2026-08-29-002-feat-unified-20mm-spar-trunnion-belt-drive-plan.md
---

# fix: Nacelle nav-wire/spar reconciliation + AK7455 wing-side finish

> **SUPERSEDED 2026-08-29 by
> [`2026-08-29-002-feat-unified-20mm-spar-trunnion-belt-drive-plan.md`](2026-08-29-002-feat-unified-20mm-spar-trunnion-belt-drive-plan.md).**
> This plan scoped only the nav-wire routing bug and the AK7455 pocket, and it
> assumed the Ø8 mm **rotating** spar would survive. It did not: the four
> 10 AWG ESC feeds have no viable path at all (they do not fit the Ø7 mm
> conduits, and those conduits sit 17.65 mm off the tilt axis), which forces a
> larger fixed spar, a thicker airfoil, a trunnion pivot, and a belt drive.
>
> Two findings here remain valid and are **carried into 002 §U5**: the AK7455
> wing-pocket/cableway is still sized and commented for the rejected MT6701,
> and the nav-wire path still needs to be separated from the ESC harness.
> Part A's validation of the external proposal also stands, with 002 adding the
> measurements that show the 16 mm spar itself does not close.
>
> **§U1's specific fix — routing the nav wire into the spar bore — is void.**
> That reasoning depended on the spar rotating *with* the nacelle. Under a
> fixed spar the nav light still rotates but the spar does not, so the 3-core
> must cross the joint at the trunnion instead (002 §U5 step 2).

**Target repo:** Serenity-UAV (this repo)

**Origin:** an external (Gemini) conversation proposed a "16 mm Unified Spar"
carrying 4× 10 AWG ESC power leads through an 11 mm bore, a static AS5600 Hall
encoder on the wingtip, and a removable wingtip "garage" hatch. This plan
opens with the validation of that proposal against the repo's own analysis
and as-built geometry, then scopes the one real, substantiated gap the
validation surfaced — which is unrelated to the external proposal's specific
recommendations but sits in the same subsystem (nacelle/wingtip signal
routing across the tilt joint).

**Scope:** `airframe/openscad/nacelles/nacelle_pod_50mm_tandem.scad`,
`airframe/openscad/wings/wings_s1223_revo.scad`,
`docs/TILT_SPAR_ANALYSIS.md`, `airframe/wings-nacelles/WBS.md`.

---

## Part A — Validation of the external proposal

| # | External claim | Verdict | Evidence |
|---|---|---|---|
| 1 | "16 mm Unified Spar" with `SPAR_BORE_D = 11.0 mm` lumen for a 4× 10 AWG power bundle | **REJECTED** | `docs/TILT_SPAR_ANALYSIS.md` §3/§9 adopted **8 mm OD × 1.5 mm wall (5 mm ID)** AISI 4130 after a full bending/torsion/stiffness/material trade study (FOS ≈ 13 bending, ≈ 9 torsion; a **12 mm** "unified structural" candidate was already evaluated and rejected in §3.4 as "Overbuilt; heavier, bigger duct crossing" — 16 mm is further from adopted than that rejected candidate). §5 of the same doc states explicitly: *"EDF power/signal do NOT use the spar (6× 16 AWG @ Ø3 mm — too large). They keep the existing wing double-D cableway + nacelle harness port. The spar is nav-wire-only."* The 2026-08-26 nacelle/ESC plan (`docs/plans/2026-08-26-001-nacelle-esc-intake-integration-plan.md`) restates this as a confirmed input: *"Do not route high-current ESC conductors through the rotating spar."* |
| 2 | 4× 10 AWG power wires need a bigger bore to fit | **PREMISE WRONG — path already exists** | `docs/POWER_DISTRIBUTION.md` confirms PDB→ESC feeds are **10 AWG silicone, 55 A rated** (external claim's gauge is right), but they already have a dedicated route: `wings_s1223_revo.scad` `CABLE_BORE_D = 7.0 mm` × 2 ("double-D", `CABLE_BORE_SEP = 9.5 mm`), forward of the spar, sized for "40 A EDF ESC power + ESC signal split across the two" (`WBS.md` §1.1.2.1 Rev R1a). No spar change is needed to carry this wiring. |
| 3 | Enlarging the spar would keep the same bearings/gears/duct fit | **FALSE if actually attempted** | The wingtip bearing is `MF128ZZ` (12 mm bore, downsized *from* `F688ZZ`/16 mm specifically because 16 mm cut through both tip airfoil skins — `wings_s1223_revo.scad` L334-341, `TILT_SPAR_ANALYSIS.md` §8.1). A 16 mm spar cannot pass through a 12 mm-bore bearing at all, and would reopen the exact skin-breach problem that motivated the R2d downsize. It would also roughly double the naive duct-core blockage (§4: 8 mm strut ≈ 20% naive / 2–4% mitigated by fairing into the existing 16 mm stator hub — a 16 mm spar is comparable to the *whole current hub diameter* and would not fit the same mitigation) and invalidate the `PINION_A_Y`-derived fixed-gear geometry. |
| 4 | `PIVOT_Z = 111.5` | **Already current — no-op** | Matches `nacelle_pod_50mm_tandem.scad` L383 exactly (Rev T CG re-derive, 2026-07-19). Nothing to change. |
| 5 | Mount the HE tilt encoder (named "AS5600") statically on the fixed wingtip, reading a diametric magnet on the rotating nacelle hub | **Architecture already built this way — chip name is wrong and the specific part is disqualified, not just outdated** | The off-axis/fixed-wing-side topology is exactly what `wing_tip_hall_sensor_pocket()` implements today. But **AS5600 was the original Rev Q design and was explicitly rejected**, not merely superseded: `airframe/wings-nacelles/WBS.md` L1276-1281 — AS5600 is on-axis-only and the mechanism has no free shaft end (the spar is a through-shaft to a keyed nacelle hub), so an on-axis sensor **cannot read the off-axis Ø22 ring magnet** the way this mechanism is built. MT6701 (also on-axis) was rejected for the same reason. The selected part is **AKM AK7455** (off-axis/side-of-shaft, SPI, anomaly-field detection for the ferromagnetic 4130/17-4 through-shaft — REF-SENSOR-008), with a dedicated EMI wiring spec already written (`docs/TILT_ENCODER_WIRING_EMI_SPEC.md`, more detailed than the external proposal's separation/shielding rules). Re-adopting AS5600 would be a functional regression, not a simplification. |
| 6 | Wingtip "garage" access hatch exposing the spar end + bullet connectors for the 4× 10 AWG feeds + static HE encoder plug, secured by a split-collar pinch clamp | **REJECTED — conflicts with the adopted service architecture** | No such hatch exists in `wings_s1223_revo.scad` today (checked for "garage", "hatch", "bullet connector", "split-collar" — no matches). `docs/plans/2026-08-26-001-nacelle-esc-intake-integration-plan.md` already evaluated and selected **nacelle-off-spar** service (slide the nacelle off the rotating spar; wing, spar, bearings, servo indexing, and Hall calibration stay installed) specifically to avoid disturbing the bearing seats and encoder calibration — the alternative ("spar out of bearings") was explicitly relegated to a fallback. A wingtip hatch that exposes and disconnects the spar's outboard end is the rejected alternative's access pattern, not the adopted one. Wingtip serviceability, if wanted, needs to be re-scoped against the nacelle-off-spar model, not introduced as an independent hatch. |
| 7 | Underlying EMI concern — don't co-locate low-voltage signal wiring with 4× 10 AWG PWM/high-current leads in the same lumen | **Correct instinct; structurally already satisfied by the adopted (not the proposed) architecture — except for one real, pre-existing gap found during this validation (Part B)** | HE encoder wiring never enters the spar (`TILT_SPAR_ANALYSIS.md` §1: "its wiring stays entirely within the fixed wing harness... eliminating wire fatigue and keeping it physically isolated from the ... EMI"). ESC power uses the wing double-D, not the spar. The spar's hollow bore is nav-wire-only. The one place this isolation is **not** actually built as designed is documented in Part B below. |

**Conclusion:** none of the external proposal's concrete geometry changes
(16 mm spar, 11 mm power bore, AS5600, wingtip garage) should be implemented.
The underlying EMI-isolation concern is valid and already the repo's own
design intent — but auditing it surfaced a real, independently-verifiable gap
between that intent and what is actually built, which is the rest of this
plan.

---

## Part B — Real gap found during validation: nav-light wire routing

**The bore-isolation decision and the built geometry disagree with each
other on which path the nav-light wire actually takes across the tilt
joint.**

- `docs/TILT_SPAR_ANALYSIS.md` §5 (2026-07-18, Rev R2) and
  `airframe/wings-nacelles/WBS.md` §1.1.2.1 Rev R1a (2026-07-07) both specify
  — with a worked twist-flex feasibility check ("~0.5°/mm over a 95° sweep,
  well inside 28 AWG stranded flex life, no slip ring required") — that the
  WS2812C 3-core nav-light wire runs **through the hollow spar bore**, root
  to outboard nav light, and is kept there specifically so it never shares a
  path with the 40 A ESC feeds.
- `nacelle_pod_50mm_tandem.scad`'s actual `nav_wire_channel()` (module docstring
  L966-969, and `airframe/wings-nacelles/WBS.md` §1.1.3.5, dated **2026-07-04
  — a week before** the spar-bore decision existed) instead runs the wire down
  an outboard-skin channel to `harness_exit_port()`, where the docstring says
  it explicitly **"joins the existing ESC/harness bundle"** on the *inboard*
  (pylon) face and exits with the 40 A EDF leads.

That is the exact co-location the spar-bore decision (and the external
conversation's own instinct) was written to avoid, and it is what is
currently built. It also takes a longer, more awkward path than necessary:
the nav-light emitter and the spar's outboard support hub
(`pivot_x_face_boss()`) are **both on the outboard (far) face** — `nav_wire_channel()`
already stops at `NAV_CHAN_Z_HI = PIVOT_Z − PIVOT_BOSS_DEPTH − 1.0 ≈ 106.5 mm`,
only ~5 mm short of the pivot boss at `PIVOT_Z = 111.5 mm` on the same face —
so routing it the rest of the way into the spar never needs to cross to the
inboard harness port at all. The wing side of this path (`hollow spar (Ø9 mm
tube ID)` per the 2026-07-07 WBS note) also predates the 2026-07-18 8 mm/5 mm-ID
spar spec and needs its figure corrected to match.

This is a real, citable, currently-open inconsistency between an adopted
decision and the shipped geometry — independent of the external conversation,
but in the same subsystem, and it is the actual fix the EMI concern calls for.

### Separately-tracked, already-open gap in the same area (not newly found here)

`airframe/wings-nacelles/WBS.md` L1304-1306 already carries an open item:
`wing_tip_hall_sensor_pocket()` and the `HALL_*` block in
`wings_s1223_revo.scad` are still sized/commented for the rejected MT6701
(3×3 QFN, 4-wire I²C) rather than the selected AK7455 (QFN24 4×4, 7-wire
SPI + ERROR pigtail). Since this plan is already touching the same wingtip/nacelle
signal-routing geometry, it closes this out too rather than leaving a second
half-finished pass over the same files.

---

## Requirements

- **R1** — `nacelle_pod_50mm_tandem.scad`'s nav-light wire path physically
  terminates inside the hollow spar bore at the outboard `pivot_x_face_boss()`
  hub, not at `harness_exit_port()`. The wire never shares a bore, channel, or
  exit port with the ESC/EDF power leads at any point in the nacelle.
- **R2** — `nav_wire_channel()`'s module docstring and the `airframe/wings-nacelles/WBS.md`
  §1.1.3.5 entry are corrected to describe the actual (post-fix) path instead
  of "joins the existing ESC/harness bundle."
- **R3** — The wing-side hollow-spar ID figure in `WBS.md` §1.1.2.1 ("Ø9 mm
  tube ID") is corrected to match the adopted 5 mm ID (`TILT_SPAR_ANALYSIS.md`
  §3) or removed if redundant with the later, authoritative figure.
- **R4** — `wing_tip_hall_sensor_pocket()` in `wings_s1223_revo.scad` is resized
  for the AK7455 QFN24 4×4 mm package (plus passives/pigtail footprint), and
  `HALL_CABLE_D` (currently 3.5 mm / "4-wire I²C") is re-sized for the actual
  7-wire SPI + ERROR direct-solder pigtail per `docs/TILT_ENCODER_WIRING_EMI_SPEC.md`
  §2.1's cable table (shielded 28 AWG SPI quad + shielded 24 AWG power pair,
  ≥15 mm internal group separation, ≥10–20 mm clearance from the 40 A EDF
  feeds).
- **R5** — Every `HALL_*` name/comment in `wings_s1223_revo.scad` still naming
  MT6701 or describing I²C is corrected to AK7455/SPI, matching the header
  comment (L407-408) that already says MT6701/AS5600 are superseded/rejected.
- **R6** — No change is made to `SPAR_OD`, `SPAR_BORE_D`, `PIVOT_Z`, the
  wingtip bearing, or the fixed-gear geometry — this plan is a routing/
  documentation reconciliation within the already-adopted mechanism, not a
  mechanism change.

## Implementation units

### U1 — Route the nacelle nav-light wire into the hollow spar, not the ESC harness

In `nacelle_pod_50mm_tandem.scad`:

- Extend `nav_wire_channel()` (or add a short connecting bore) from its current
  end at `NAV_CHAN_Z_HI` to the spar's hollow lumen at the outboard
  `pivot_x_face_boss()` hub — a short jog from the channel's rib position
  (`chan_in`/`chan_out`, inset from the outer skin) to the hub's centerline
  (Y = 0, the duct/spar axis).
- Remove the nav-wire leg from `harness_exit_port()`; confirm that module's
  remaining traffic is ESC motor leads + ESC signal only.
- Verify NAV_WIRE_BORE (2.4 mm) clears through the spar wall boss annulus
  into the spar's 5 mm ID with the 3-core WS2812C bundle (~2.5 mm per
  `TILT_SPAR_ANALYSIS.md` §5) — same feasibility margin already established
  there, just confirming it still holds at the new entry geometry.
- Update the `nav_wire_channel()` docstring and header comments accordingly.

### U2 — Fix wing-side hollow-spar ID references

In `airframe/wings-nacelles/WBS.md` §1.1.2.1 (Rev R1a entry): correct "Ø9 mm
tube ID" to the adopted 5 mm ID, with a note that it was superseded by the
2026-07-18 Rev R2 spar spec (`TILT_SPAR_ANALYSIS.md` §3).

### U3 — Finish AK7455 wing-side geometry (close WBS §1.1.3.6 open item)

In `wings_s1223_revo.scad`:

- Resize `HALL_PCB_W`/`HALL_PCB_H` (currently 7.0 × 7.0 mm, dimensioned around
  the MT6701 3×3 QFN) for the AK7455 QFN24 4×4 mm package plus its passives
  and 7-wire pigtail strain relief; re-verify `wing_tip_hall_sensor_pocket()`
  clearance to the `Ø13.5` bearing flange and top skin (previous echo-verified
  margins: 0.75 mm flange / 3.79 mm top skin — re-check both after the resize).
- Resize `HALL_CABLE_D` (currently 3.5 mm / 4-wire I²C) for the AK7455's
  7-wire SPI + ERROR pigtail, applying `docs/TILT_ENCODER_WIRING_EMI_SPEC.md`
  §2.1's cable spec and §2.3's ≥15 mm/≥10–20 mm separation rules within
  `hall_sensor_cableway()`.
- Rename/re-comment `HALL_SENS_R`, `HALL_PCB_*`, `HALL_CABLE_D` and any other
  MT6701/I²C-worded constants to AK7455/SPI, matching the module header at
  L407-408 that already documents the supersession.
- Cross-check `HALL_KEEPOUT_R` (10 mm non-ferrous keep-out) and the ≥30 mm
  spar-centerline clearance rule (`docs/TILT_ENCODER_WIRING_EMI_SPEC.md` §6.2)
  still hold after any pocket resize.

### U4 — Regenerate and verify

- Re-render port/starboard nacelle and wing STLs through the existing
  Makefile pipeline.
- Re-run `python3 tools/bake_hull_frame.py` for any re-baked parts.
- Inspect in FreeCAD: nav-wire path clears the pivot boss/spar bore with no
  solid overlap, the AK7455 pocket clears the bearing flange and top skin,
  and the exterior mold line is unchanged (all changes are internal).

## Verification contract

1. `nav_wire_channel()` no longer references `harness_exit_port()` in code or
   comments; `harness_exit_port()`'s own docstring lists only ESC motor +
   signal traffic.
2. The nav-light wire's documented path (emitter → outboard channel → spar
   hollow bore → root) matches, word-for-word in outcome, `docs/TILT_SPAR_ANALYSIS.md`
   §5 and the corrected `WBS.md` §1.1.3.5 entry.
3. `wings_s1223_revo.scad` contains no remaining MT6701/AS5600/I²C references
   in the `HALL_*` block outside of the historical-rejection comment at
   L407-408.
4. `wing_tip_hall_sensor_pocket()` clears the `Ø13.5` bearing flange and top
   skin by a positive, echo-verified margin after resizing.
5. Run the changed-geometry gates:

   ```text
   python3 tools/validate_stls.py
   python3 tools/wing_root_deconflict.py
   python3 tools/wing_internal_clearance.py
   python3 tools/wing_spar_carrythrough.py
   python3 tools/landing_gear_wing_clearance.py --proud
   ```

6. No change to `SPAR_OD`, `SPAR_BORE_D`, `PIVOT_Z`, wingtip/root bearing
   part numbers, or fixed-gear geometry (R6) — diff review confirms this.
7. Headless OpenSCAD/FreeCAD renders inspected at cruise, intermediate, and
   hover tilt configurations; nav-wire and SPI-pigtail paths have positive
   clearance through the full −5°…90° sweep.

## Open gates

- Exact AK7455 QFN24 4×4 mm footprint + passives (pull from the KiCad
  `ENC-NACELLE-1` board, not re-estimated here) to size the resized pocket.
- Confirmed physical fit of the 7-wire SPI pigtail bend radius inside
  `HALL_CABLE_D` once resized — bench-verify, per `TILT_ENCODER_WIRING_EMI_SPEC.md`
  §7.1's continuity/shield checks.
- Whether the corrected nav-wire entry geometry at the outboard pivot boss
  needs its own small reinforcing feature (beyond `spar_duct_wall_bosses()`,
  which already exists for the bore breach) — resolve in FreeCAD once U1 is
  modeled.
