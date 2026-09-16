---
title: "A motor coaxial with its worm clears the wheel by WORM_PD/2 − MOTOR_D/2 − m, whatever you do with C or the worm's angle — and every part a bracket carries is a layout envelope"
date: 2026-09-16
category: design-patterns
module: "nacelle tilt drive — tools/cargo_layout_fit.py, airframe/openscad/fuselage/cargo/tilt_actuator_bracket.scad"
problem_type: design_pattern
component: tooling
severity: high
applies_when:
  - "a gearmotor drives a worm directly (no coupling) and the motor body sits beside the wheel"
  - "a clash is proposed to be fixed by moving the worm round the wheel or by changing the centre distance"
  - "a bracket carries a PCB, a brake, or any secondary part that is drawn in the part's SCAD but not in the layout proof"
  - "an interior boss check reads FAIL and the shell already contains bosses from the previous revision"
symptoms:
  - "Rev T5b pair check: Pololu 25D motor body 1.5 mm inside the 40T wheel tip circle (T5d-1)"
  - "controller-board card-edge rails in tilt_actuator_bracket.scad pass straight through the worm (T5d-2)"
  - "bracket web has no cut where the worm reaches past it (T5d-3)"
  - "swinging the worm >= 5 deg aft lands the motor body on the port hoist line at Y 55.5"
root_cause: missing_validation
resolution_type: tooling_addition
related_components:
  - tools/cargo_layout_fit.py
  - airframe/openscad/fuselage/cargo/tilt_actuator_bracket.scad
  - airframe/openscad/fuselage/cargo/tilt_brake.scad
  - docs/CARGO_SECTION_LAYOUT.md
  - docs/TILT_ACTUATOR_SELECTION.md
tags: [worm-gear, gearmotor, clearance, layout-proof, envelope, bracket, boolean-check, cargo-section]
---

# A motor coaxial with its worm clears the wheel by WORM_PD/2 − MOTOR_D/2 − m, whatever you do with C or the worm's angle — and every part a bracket carries is a layout envelope

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP. **AI note:** drafted by
Claude (model: Claude Opus 5, Anthropic) under the author's direction,
2026-09-16, per `AGENTS.md` §3. **License:** CC BY-SA 4.0.

## Context

Rev T5b of the cargo-section nacelle-tilt actuator put a Pololu 25D gearmotor
coaxially on a four-start Ø24 worm above the 40T m1 wheel (C 32). On 2026-09-16
the pairwise check in `tools/cargo_layout_fit.py` reported the motor body
1.5 mm inside the wheel's tip circle (finding T5d-1,
`docs/CARGO_SECTION_LAYOUT.md` §4). The first fix proposed was to swing the worm
~25° aft round the wheel so the motor climbed away; it was worked through in the
fit tool and abandoned. Doing so exposed two more latent defects in
`airframe/openscad/fuselage/cargo/tilt_actuator_bracket.scad`: the controller-
board rails ran straight through the worm (T5d-2) and the web had no slot where
the worm reaches 6.5 mm past its plane (T5d-3). Neither the board nor the
bracket itself had ever been an envelope in the layout proof. All of this is
uncommitted as of this writing (the SCAD, fit tool and both docs are untracked).

## Guidance

**Rule 1 — do the algebra before moving geometry.** For a gearmotor whose axis
*is* the worm axis, the motor body's nearest approach to the wheel is along the
common perpendicular at the centre distance C. With wheel tip radius
`WHEEL_PD/2 + m` and `C = (WHEEL_PD + WORM_PD)/2`:

```text
gap = C − (WHEEL_PD/2 + m) − MOTOR_D/2 = WORM_PD/2 − MOTOR_D/2 − m
```

C cancels, and rotating the worm about the wheel axis moves the whole pair
rigidly, so the worm's angle cancels too. The only levers are `WORM_PD` and
`MOTOR_D`; `WORM_PD` is usually capped by something else — here the battery
cradle 3.2 mm inboard of the worm tip (`tools/cargo_layout_fit.py:129`,
`:143-148`). The tool now records the fact beside the constants it governs:

```python
# tools/cargo_layout_fit.py:124-131
# WHY THE 25D WENT (T5d-1, found 2026-09-16): for a motor coaxial with the
# worm, the motor-to-wheel-tip gap is (WORM_PD/2 - MOTOR_D/2 - m), independent
# of C and of the worm's angle on the wheel -- rotating the worm (the first
# T5e idea) does not change it, and a worm swung >= 5 deg aft lands on the
# port hoist line at Y 55.5.
WORM_PD = 26.0                                  # :139
STAGE_C = (WHEEL_PD + WORM_PD) / 2          # 33.0 mm centre distance   :140
MOTOR_D = 20.0                              # Pololu 20D (REF-ACT-001)  :152
```

**Rule 2 — everything the bracket carries is an envelope.** A board, brake
guide, solenoid or cable channel drawn only in the part's SCAD is invisible to
the proof. The T5e board entry (`tools/cargo_layout_fit.py:342-344`) is the
model, with its own `gap` where the repo's 3 mm budget does not apply:

```python
L["tilt controller board"] = dict(mirror=True, solid=box(
    BOARD_X0, BOARD_X0 + BOARD_T, BOARD_Y0, BOARD_Y0 + BOARD_L, BOARD_Z0, BOARD_Z0 + BOARD_W),
    gap=2.0)
```

with `BOARD_L, BOARD_W, BOARD_T = 42.9, 36.5, 7.4` (`:193`) and
`BOARD_X0 = GEAR_X_OUT + 5.0` (`:199`) — the web's outboard face, so the board
station is derived from the gear plane, not typed twice.

**Rule 3 — boolean every exported STL against the shell and every envelope.**
`report()` (`:557-603`) checks envelope-vs-shell (`hit`, `near` after dilating
by the gap) and envelope-vs-envelope pairs, skipping declared `mates`. After
export, intersect the rendered bracket/worm/wheel/guide STLs the same way; only
the intended contacts may remain (feet on bosses, rails round the board, the
mesh zone — 21 mm³ in T5e, `docs/CARGO_SECTION_LAYOUT.md` §7).

**Rule 4 — subtract last revision's bosses from the published shell first.**
The shell on disk still carries the previous feet and pads; a new foot or board
that overlaps an old boss reads as a hull hit. `shell_after_merge()`
(`:493-520`) removes `NSVMT_PAD_PORT` and every boss in `PUBLISHED_FEET`
(`:489`), the cradle hangers, shelf bosses and hoist pedestals before `report()`
runs (`:669-670`). Update `PUBLISHED_FEET` whenever the shell is re-merged.

## Why This Matters

The tilted-motor fix looked plausible and consumed a working session before the
two-line derivation showed it could not move the number it was meant to move.
Worse, the fit tool had been reporting PASS on a bracket whose rails intersected
the worm, because the proof only knew about the parts someone had typed into
`layout_t5()`. A layout proof is only as complete as its envelope list, and a
part SCAD is not a proof. The three defects were found in one pass only because
the rendered STLs were booleaned against the proof's own solids.

## When to Apply

* A gearmotor drives a worm directly (no coupling) and its body sits beside the
  wheel — check `WORM_PD/2 − MOTOR_D/2 − m` before anything else.
* A clash is proposed to be fixed by changing C or swinging a part round a
  common axis — first ask which variables cancel.
* A bracket carries a PCB, brake, solenoid or harness that appears in its SCAD
  but not in the layout tool — add it to the layout dict with its own gap.
* An interior check reads FAIL and the shell already contains bosses from the
  previous revision — subtract them before believing the failure.
* Any part is exported for a shell re-merge — boolean the STL against the shell
  and every envelope, not just the envelopes against each other.

## Examples

* **T5d-1, motor into wheel (Rev T5b → T5e).** Ø25 motor, Ø24 worm, m1:
  gap = 12 − 12.5 − 1 = **−1.5 mm** at C 32; the motor underside (Z 88.6) sat
  inside the Ø42 tip circle (Z 90.1). With `WORM_PD ≤ 26` (cradle cap) a Ø25
  body can never clear. Ø20 motor, Ø26 worm: gap = 13 − 10 − 1 = **+2.0 mm** at
  C 33 (`tools/cargo_layout_fit.py:338-341`). The rate lost to the slower 20D
  came back through a six-start worm (6.67:1, lead 13.0°, `:137-141`); the
  brake was always the hold (`docs/TILT_ACTUATOR_SELECTION.md` §1a, Option 4 in
  `tools/tilt_actuator_options.py:305-311`). The rejected tilt also moved the
  worm centre to Y 46.6 + 33 sin θ, straddling the port hoist line at Y 55.5
  for θ ≥ 5°, and the line cannot move (`docs/CARGO_SECTION_LAYOUT.md` §4).
* **T5d-2, board rails through the worm.** T5b rails on the web's inboard face
  (Y 38..81, Z 93..129.5) crossed both worm and motor; the board had never been
  in `layout_t5()`. Added as an envelope; a 2 mm grid search found no clear
  position forward of the worm (wall curves in above Z 108 at Y < 12); it now
  sits on the web's outboard face at Y 55..97.9, Z 83..119.5
  (`board_rails()`, `tilt_actuator_bracket.scad:305-323`), which pushed the aft
  avionics nodes 8.5 mm aft.
* **T5d-3, web with no worm slot.** Found only by booleaning the rendered
  bracket against the worm envelope: the Ø26 worm reaches 6.5 mm and the Ø14
  collar 1.5 mm past the web plane. the slot geometry is derived at
  `tilt_actuator_bracket.scad:164-169` and `web_plate()` cuts it at `:215-223`. The same boolean
  caught a round `face_plate()` reaching 1.5 mm into the wheel — it is now flat-
  bottomed at the motor underside (`:255-259`).

## See also

* `docs/solutions/design-patterns/self-locking-worm-and-vectoring-bandwidth-are-mutually-exclusive.md`
  — why the tilt drive is a multi-start worm plus brake at all, and why a bigger
  lead angle (six-start) costs nothing the brake was not already carrying.
* `docs/solutions/logic-errors/mesh-boolean-layout-proofs-silent-zero-volumes-and-shared-profiles.md`
  — the other way `tools/cargo_layout_fit.py` returns a false PASS (unmerged
  STL → 0 mm³ everywhere); its positive-control rule pairs with rules 3–4 here.
* `docs/solutions/design-patterns/passive-mechanism-check-frames-before-dimensions.md`
  — the kinematic twin of rule 1: an empty or futile search over placement
  means the model, not the numbers, is wrong.
* `docs/solutions/workflow-issues/read-the-decision-record-before-verifying-first-pass-geometry.md`
  — write the closed-form constraint into the decision record before building
  or extending tooling around it.
* `docs/TILT_ACTUATOR_SELECTION.md` §1a — decision-record home of the same
  clearance algebra and the Opt 2 → Opt 4 re-cut; `docs/CARGO_SECTION_LAYOUT.md`
  §0 — the placed geometry the rules produced.
