---
title: "Ray-probe the published hull at the station before placing anything — and when a placement misses by fractions of a millimetre three times, change its class, not its margins"
date: 2026-09-16
category: design-patterns
module: "cargo section layout — tools/cargo_layout_fit.py, airframe/blender-scripts/merge_cargo_interior.py"
problem_type: design_pattern
component: tooling
severity: high
applies_when:
  - "placing equipment against the canonical hull from a comment, a legacy constant or a section plot instead of a measurement"
  - "a placement fails the clearance budget by 0.2-1 mm and the next idea is a smaller gap, a bonded liner or a 1.5 mm shift"
  - "a candidate pocket looks big in gross volume (cm3) but has not been measured as a usable window (mm x mm at a given depth)"
  - "an owner constraint ('any orientation', 'pouch not tray') has not been checked for the freedom it actually gives"
related_components:
  - tools/cargo_layout_fit.py
  - airframe/blender-scripts/merge_cargo_interior.py
  - airframe/openscad/fuselage/cargo/chin_node_shelf.scad
  - docs/CARGO_SECTION_LAYOUT.md
tags: [hull-frame, ray-probe, clearance, placement, cargo-section, avionics, asymmetry, measurement]
---

# Ray-probe the published hull at the station before placing anything — and when a placement misses by fractions of a millimetre three times, change its class, not its margins

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP. **AI note:** drafted by
Claude (model: Claude Opus 5, Anthropic) under the author's direction,
2026-09-16, per `AGENTS.md` §3. **License:** CC BY-SA 4.0.

## Context

The cargo-section build-out (Rev T5 → T5e, 2026-09-15/16) re-learned the same
lesson at least five times, each time paid for in a failed placement:

* The retired DS3225 pad comments put the lower sidewall at X −86 at the drive
  shaft station. A ray probe (`tools/cargo_layout_fit.py`, comment at the
  `GEAR_X_OUT` block) found it at **−115**, with the bonded root flange face at
  −120 — the whole gear plane moved 38 mm.
* The canonical hull is **not symmetric about X_CL**: at Y −45 / Z 80 the port
  wall is at X −112 and the starboard at −225 (2.7 mm difference), so a
  placement that passes on port fails on starboard.
* The "shuttle-profile" shoulder pockets outboard of the tilt brackets are
  ~300 cm³ each; the largest usable *window* at 20 mm depth is 55 × 31 mm, and
  the board is 35 mm tall. Gross volume said yes; the window said no.
* The two chin-flank avionics nodes were tried standing on edge three times
  (encoder removed from the motor, worm offset, cradle shifted 1.5 mm, foil
  liner bonded to the wall) and missed by 0.2–1 mm every time.
* The same two nodes **lying flat on the chin floor** under the battery nose
  (`N_CHIN_*`, `chin_node_shelf.scad`) were clear on both sides at the full
  2 mm budget on the first probe — because the owner had said "any
  orientation" and nobody had used that freedom.

## Guidance

1. **Measure the station, then design.** Before placing anything against the
   hull, fire rays from inside the section at the exact (Y, Z) or (X, Z) you
   care about and read the surfaces back (`shell_tm.ray.intersects_location`,
   `process=True` on load). Legacy constants in comments, the nominal loft,
   and section plots at other stations are hypotheses, not data. Record the
   probed numbers next to the constant they justify, as `cargo_layout_fit.py`
   now does for `GEAR_X_OUT`, `N_AFT_Z0` and the chin nodes.
2. **Never assume port/starboard symmetry** on a Blender-canonical hull. Check
   both sides of every mirrored envelope (`mirror=True` in `layout_t5()` does
   this) and expect the tighter side to govern.
3. **Measure windows, not volumes.** A pocket is usable only if a rectangle of
   the part's footprint fits at the part's depth with the gap on all sides. Cast
   a grid of rays across the candidate and read the *minimum* clear width;
   gross cavity volume is irrelevant.
4. **Three near-misses means the wrong class of placement.** When a fit keeps
   failing by fractions of a millimetre, the honest fixes (thinner gap, bonded
   liner, "shift it 1.5 mm") are hopes, not designs. Step back to the owner's
   actual constraints — orientation, pouch vs tray, which items must be in this
   section — and try a different class: a different orientation, a different
   floor, a different section. The flat chin-floor placement took one probe.
5. **Every boss you add goes through every gate.** Bracket foot 2 moved twice
   because it landed on the aft landing-gear bay's bolt bores, found only by
   `tools/landing_gear_wing_clearance.py --proud`. Adding a boss to the shell
   re-opens the gates that were green.

## Why This Matters

Each of the failed placements above consumed hours of layout iteration and,
in the case of the chin flanks, produced design changes (encoder removed from
the gearmotor, worm offset) that were later undone or made moot. The hull is
the one thing in the project that cannot be changed to suit a part; every
number about it must be measured from the published mesh at the station in
question, and the cheapest measurement is a ray.

## When to Apply

* Any new equipment station in any fuselage section, before the first SCAD
  line is written.
* Any placement whose margin is being negotiated below the repo budget
  (3 mm moving, 2 mm static).
* Any pocket proposed on the strength of a section view or a cm³ figure.
* Any time an owner has stated a freedom (orientation, mounting style) that
  the current attempt is not using.

## Examples

* Sidewall −86 → −115 measured; gear plane `GEAR_X_OUT` −122.75 (T5e), wheel
  clear of the payload box by 4 mm and of the flange by 2.75 mm.
* Chin flanks: port node 1.5–4 mm to the wall, starboard 21–28 mm available
  against 26 needed (2026-09-15); after the worm offset + cradle shift both
  sides ~0.5 mm short (2026-09-16). Chin floor: 0 mm³ hit, 0 mm³ within 2 mm,
  both sides, first run (`docs/CARGO_SECTION_LAYOUT.md` §3a).
* Aft nodes: the outboard-top pouch corner met the shoulder's curve-in 1.5 mm
  short — a 5 mm chamfer on the pouch fold (the PCB corner is 2 mm inboard of
  it) closed it without moving the node.
