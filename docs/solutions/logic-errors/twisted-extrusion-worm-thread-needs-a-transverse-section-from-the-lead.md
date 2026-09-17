---
title: "A worm made by twisted extrusion needs its transverse tooth section derived from the axial thickness and the lead — a fixed tangential half-width is wrong for every lead"
date: 2026-09-16
category: logic-errors
module: "nacelle tilt drive — airframe/openscad/fuselage/cargo/tilt_actuator_bracket.scad worm()"
problem_type: logic_error
component: tooling
severity: medium
symptoms:
  - "printed-worm profile polygon used a constant +/-0.79 mm tangential half-width for the tooth (Rev T5b)"
  - "a single-start worm at 3.14 mm lead should occupy 180 deg of the transverse section per tooth; the profile gave ~15 deg"
  - "the six-start worm (Rev T5e) would have had six needle-thin threads with no mesh with the 40T wheel"
root_cause: logic_error
resolution_type: code_fix
related_components:
  - airframe/openscad/fuselage/cargo/tilt_actuator_bracket.scad
  - tools/cargo_layout_fit.py
  - docs/TILT_ACTUATOR_SELECTION.md
tags: [worm-gear, openscad, linear-extrude, twist, thread-profile, lead-angle, multi-start, printed-gear]
---

# A worm made by twisted extrusion needs its transverse tooth section derived from the axial thickness and the lead — a fixed tangential half-width is wrong for every lead

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP. **AI note:** drafted by
Claude (model: Claude Opus 5, Anthropic) under the author's direction,
2026-09-16, per `AGENTS.md` §3. **License:** CC BY-SA 4.0.

## Problem

OpenSCAD makes a worm by `linear_extrude(height, twist = −360·L/lead)` of a 2-D
profile. The Rev T5b profile drew the root circle plus one trapezoid whose
*tangential* half-width was a constant (`±π·m/4 ≈ ±0.79 mm`) — a spur-gear
tooth thickness pasted into a thread. That number has nothing to do with a
thread's transverse section, and the error is invisible in a render because
the twisted ribbon still looks like a worm.

## Symptoms

* For the single-start m1 worm (lead 3.14 mm) the axial tooth thickness at
  pitch is π·m/2 = 1.571 mm — half the lead — so one tooth should sweep 180° of
  the transverse section. The profile gave ≈ 15°.
* On the six-start Ø26 worm (lead 18.85 mm) six such teeth would have been
  needle-thin ribbons with essentially no flank in contact with the wheel.

## What Didn't Work

Nothing had been tried; the profile was never checked against the lead. The
defect surfaced only when the six-start worm was authored and the tooth
count made the geometry obviously wrong.

## Solution

Derive the transverse section from the axial thickness at each radius and the
lead (`tilt_actuator_bracket.scad:344-357`):

```scad
WORM_LEAD = PI * GEAR_MODULE * WORM_STARTS;                              // 18.85 mm, 6 starts
function worm_t(r)        = PI * GEAR_MODULE / 2 - 2 * (r - WORM_PD / 2) * tan(20); // axial thickness at r
function worm_half_ang(r) = worm_t(r) / WORM_LEAD * 180;                 // deg of transverse section
module worm_tooth_2d() {                                                 // polar polygon root -> tip
    rs = [for (i = [0 : n]) WORM_ROOT_R - 0.2 + (WORM_TIP_R - WORM_ROOT_R + 0.2) * i / n];
    polygon(concat([for (r = rs) [r * cos(-worm_half_ang(r)), r * sin(-worm_half_ang(r))]],
                   [for (i = [n : -1 : 0]) let (r = rs[i]) [r * cos(worm_half_ang(r)), r * sin(worm_half_ang(r))]]));
}
module worm_profile() { union() { circle(r = WORM_ROOT_R);
    for (k = [0 : WORM_STARTS - 1]) rotate(k * 360 / WORM_STARTS) worm_tooth_2d(); } }
```

The extrusion twist is unchanged (`−360 · WORM_LEN / WORM_LEAD`); the profile
is what carries the thread's shape.

## Why This Works

A helical thread's transverse section at radius *r* is the axial section
mapped through the helix: an axial thickness *t* becomes an angle
*t / lead × 360°*. The trapezoidal (20°) thread thins from root to tip in the
axial direction, so the angle shrinks with *r*; each start is that wedge,
repeated `starts` times around the axis. The lead — not the module — sets
how wide the tooth is around the circumference, which is why a fixed
tangential width can only be right by accident.

## Prevention

* Any twisted-extrusion thread: compute the angular width from `t / lead`,
  and sanity-check that `starts × half_ang(root) × 2 + starts × gap` ≈ 360°.
* Before exporting a printed gear, boolean it against its mate's envelope —
  the worm/wheel intersection should be a thin mesh zone (21 mm³ for the
  T5e pair, `docs/CARGO_SECTION_LAYOUT.md` §7), not zero and not the whole
  tooth band.
* Keep the worm a *translated* part for the starboard side — a mirror makes a
  left-hand thread (`tilt_actuator_bracket.scad` header, PARTS).
