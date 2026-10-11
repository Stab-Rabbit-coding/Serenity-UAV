---
title: "When sweeping a part's station, re-solve its seat against the real mating surface at every step and score footprint coverage"
date: 2026-10-11
category: design-patterns
module: "cargo bulkhead / landing gear (BHD-02 fore gear-bay station move; any part slid along a curved host)"
problem_type: design_pattern
component: tooling
severity: high
applies_when:
  - "a study slides a part along one axis while holding its other coordinates and orientation fixed"
  - "the host or mating surface (hull shell, flange, liner) is excluded from the clash targets on the grounds that it will be re-cut"
  - "the host surface is curved or tapers along the sweep axis, so a fixed offset no longer seats the part"
  - "a sweep reports a station clear before any placement at that station has been built and checked"
  - "a bonded or bolted part needs material under every fastener and gusset, not only zero clash volume"
related_components:
  - tools/bhd02_option_study.py
  - airframe/blender-scripts/merge_cargo_interior.py
  - tools/generate_lg_bays.py
  - docs/BHD02_OPTION_STUDY.md
tags: [parameter-sweep, seat-solve, footprint-coverage, mating-surface, landing-gear, cargo-bulkhead, placement]
---

## Context

On 2026-10-10 the owner chose to move the fore landing-gear bay station off
the bonded wing-root flange (BHD-02, option A). The first station sweep was
`station_sweep` in `tools/bhd02_option_study.py:393`. It copies the corner,
sets only `c[1] = y`, and poses the bay there (`:403`-`:406`). Hip X, hip Z
and the swing azimuth stay fixed. The target lists are in `SWEEPS`
(`tools/bhd02_option_study.py:380`). The comment above them says it plainly
(`:378`-`:379`): "The hull shell is NOT a target: the bay pocket is re-cut
wherever the bay goes."

That sweep reported hip Y −36 mm as the first clear station. It showed
0 mm³ to the flange, spar, wing, collar, chin nodes, cradle, harnesses and
tilt drive (`docs/BHD02_OPTION_STUDY.md` §10, "Fore station sweep", line 268).

The hull did not hold still. Forward of Y −20 the cargo hull narrows and
the belly rises. Belly Z is 0 at Y −20, 0.75 in (19 mm) at −30 and
1.73 in (44 mm) at −40 (§10, "Fore station at the seat-solved hip X
(correction)", line 310). A bay at a fixed X floats off a hull that has
moved inboard and up.

The correction re-solved hip X per Y with `seat_offset`
(`airframe/blender-scripts/merge_cargo_interior.py:1386`), measured in the
bay's own plate frame from `_plate_frame` (`:1356`). At Y −38 the hip moved
to X −125.5, 0.85 in (21.6 mm) inboard. That exposed a TACCO CN2 chin pouch
clash of 237 + 64 mm³ and a seat curvature spread of 0.67 in (17.1 mm).

Building the bay at Y −38 then showed the real problem (§10, "No clean fore
station", line 340). The lower-forward third of the footprint was off the
hull. The skin there fell 0.63–1.97 in (16–50 mm) inboard of the seat plane,
or was absent. The lower-forward M3 had 0 mm³ of flange material. The
forward clevis ear and gusset came off as a loose 1,561 mm³ body.

## Guidance

1. **Re-solve the part's own placement at every station step.** Moving one
   coordinate is not moving the part. Solve the seat against the real
   mating surface at each step. Here that is `seat_offset` per Y, which
   gives a different hip X at every station.
2. **Score how much of the mating footprint lands on the host.** Clash
   volume alone cannot see missing material. The re-sweep scored coverage:
   the fraction of footprint cells with skin within ±0.47 in (±12 mm) of
   the seat.
3. **Score the attachment material, both sides.** Each bolt needs printed
   flange around it and host collar under it. A bolt over air passes every
   clash check.
4. **Never drop the host part from a placement sweep's targets.** "The
   pocket is re-cut wherever the part goes" is true for the pocket. It does
   not create hull where the hull is absent.
5. **Treat a clean sweep as a hypothesis.** Build the part at the chosen
   station and check it there before you report the station as clear.

## Why This Matters

The fixed-X sweep said Y −36 was clean. At the seat-solved X the same
station had coverage 0.72 and a TACCO overlap of 890 mm³ (curve-following
bay re-sweep; the first seat-solved check of the flat bay gave 357 mm³). The
answer
changed from "move to −36" to "no station is clean".

The re-sweep table (§10, line 340; all 7 rows, overlaps in mm³) shows the
trade:

- Y −36: X −125.0, coverage 0.72. Flange 0, TACCO 890.
- Y −32: X −123.0, coverage 0.79. Flange 117, TACCO 783.
- Y −28: X −121.5, coverage 0.80. Flange 601, TACCO 524.
- Y −24: X −119.5, coverage 0.87. Flange 688, TACCO 237.
- Y −20: X −117.5, coverage 0.89. Flange 739, TACCO 61, nav port 44.
- Y −16: X −115.0, coverage 0.92. Flange 511, TACCO 0, spar 0, wing 0,
  nav port 71 (that port moves anyway under BHD-03/04).
- Y −12: X −112.0, coverage 0.92. Flange 488, spar 1, nav port 36.

No Y both clears the flange and keeps the footprint on the hull. The owner
chose the hybrid: hip Y −16 plus a smaller flange notch. The notch removes
5,361 mm³ against 8,848 mm³ for option A at the old station. The governing
bond FOS is 16.1 against a target of 4.0.

Had the first sweep been taken as the result, the bay would have been drawn
at Y −36. It would have bolted a third of its flange to nothing.

## When to Apply

- Any sweep that slides a part along a host whose surface curves, narrows
  or rises along the sweep axis.
- Any placement whose seat was solved once and then reused at other
  stations.
- Any sweep whose target list leaves out the part it mounts to.
- Any fastener pattern that is checked for keep-out clearance but not for
  material on both sides of the joint.

## Examples

The chosen station is baked into both sources, and the gate keeps them in
sync:

- `airframe/blender-scripts/merge_cargo_interior.py:848`-`853`, `LG_CORNERS`:
  `("fore-port", -114.90, -16.00, 38.0, -22.4, "fore")` and its mirror at
  X −224.90. The comment at `:845`-`:847` records the move from Y −1.28.
- `airframe/openscad/fuselage/canonical_leg_r6_3_0in.scad:1137`, `CORNERS`:
  the same rows at `:1154`-`:1155`. The comment notes "Y -38 was rejected:
  a third of the footprint is off the hull there."

The attachment-material check now lives in the generator.
`tools/generate_lg_bays.py:115`-`:140` accepts a bolt only when its keep-out
is clear, the printed flange surrounds it, and the hull seat collar lies
under it (`BOLT_MIN_COLLAR = 150.0` mm³ at `:79`). A rejected bolt slides
along its side-flange centreline in 0.5 mm steps until all three hold, up
to `BOLT_SLIDE_MAX = 30.0` mm (`:75`); past that the generator fails rather
than place it. The comment records
why: at the lower-forward corner "the nominal bolt there clamped over air
(3.4 / 5.4 mm^3 of flange, measured 2026-10-10)."

The sweep code itself still holds X at whatever the canonical CORNERS give
(now −114.90, not the −103.87 the first sweep used) and still excludes the
hull (`tools/bhd02_option_study.py:378`-`:406`). Read its output as a first
filter, not as a placement.

Related: [build every joint in context through its full motion](build-every-joint-in-context-through-its-full-motion.md).

## Related

- [probe-the-published-hull-and-change-the-placement-class-not-the-margins.md](probe-the-published-hull-and-change-the-placement-class-not-the-margins.md)
  — measure the hull at the exact station before placing; this doc extends
  that to every step of a sweep.
- [envelope-gates-pass-while-real-parts-clash.md](envelope-gates-pass-while-real-parts-clash.md)
  — the same family: a check built on an idealisation stays green while the
  real parts fail.
- [gate-a-part-invariant-at-every-selector-value-it-is-published-at.md](gate-a-part-invariant-at-every-selector-value-it-is-published-at.md)
  — check every configuration a part is built in; here, every station it is
  swept through.

AI attribution: drafted by Claude (Claude Opus 5.5, Anthropic) from the
2026-10-10 session, under the direction of Stab-Rabbit-coding.
