---
title: "One Python module holds every layout station, proves the layout, feeds the mesh merge and emits the SCAD include — numbers are never restated"
date: 2026-09-16
category: design-patterns
module: "cargo section — tools/cargo_layout_fit.py, cargo_layout_t5_params.scad, merge_cargo_interior.py"
problem_type: design_pattern
component: tooling
severity: medium
applies_when:
  - "a station or dimension is needed by a proof script, a mesh-merge script and one or more OpenSCAD parts"
  - "a SCAD file is about to restate a number that another file already owns"
  - "a layout is proved in one tool and built in another and the two have drifted"
related_components:
  - tools/cargo_layout_fit.py
  - airframe/openscad/fuselage/cargo/cargo_layout_t5_params.scad
  - airframe/blender-scripts/merge_cargo_interior.py
  - airframe/openscad/fuselage/cargo/tilt_actuator_bracket.scad
  - airframe/openscad/fuselage/cargo/battery_cradle.scad
tags: [single-source, layout, openscad, generated-include, merge-pipeline, cargo-section, stations]
---

# One Python module holds every layout station, proves the layout, feeds the mesh merge and emits the SCAD include — numbers are never restated

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP. **AI note:** drafted by
Claude (model: Claude Opus 5, Anthropic) under the author's direction,
2026-09-16, per `AGENTS.md` §3. **License:** CC BY-SA 4.0.

## Context

Before Rev T5 the cargo section's stations lived in three places: constants
in `merge_cargo_interior.py`, literals in each part's SCAD, and the numbers in
`docs/CARGO_SECTION_LAYOUT.md`. The legacy cargo SCAD modules were even in a
different (Y-as-dorsal) frame from the merge script. Every change was typed
two or three times and drifted. Rev T5 replaced that with one module,
`tools/cargo_layout_fit.py`, and Rev T5e changed ~40 stations in a day
through it without a single restated number.

## Guidance

* **The module owns the constants.** Every station, gap, boss position and
  part envelope is a named constant with the measurement or decision that
  justifies it in the adjacent comment (`GEAR_X_OUT`, `BOARD_*`,
  `N_CHIN_*`, `SHELF_BOSS`, `OBSERVER_BOSS`, `BRACKET_FEET`).
* **The same module is the proof.** `layout_t5()` builds every envelope from
  those constants; `report()` booleans them against the published shell and
  each other. Nothing is placed that is not also checked.
* **The merge script imports it.** `merge_cargo_interior.py` does
  `import cargo_layout_fit as clf` and builds bosses from `clf.BRACKET_FEET`,
  `clf.SHELF_BOSS`, `clf.OBSERVER_BOSS`, `clf.HOIST_XS` … — the shell's
  bosses are the layout's bosses by construction.
* **The SCAD parts include a generated file.** `--write-scad` emits
  `cargo_layout_t5_params.scad` (header: *GENERATED … do not edit*); every
  part (`tilt_actuator_bracket.scad`, `tilt_brake.scad`, `battery_cradle.scad`,
  `chin_node_shelf.scad`) `include`s it and derives its own geometry from the
  names. A part file may define *its own* wall thicknesses and fillets; it may
  not type a hull station.
* **Change order:** edit the constant → run the proof (`--write-scad`) → re-merge
  the shell if a boss moved → re-render the parts → boolean the parts against
  the proof → run the other gates. The layout doc is written last, from the
  tool's output.

## Why This Matters

A station typed twice is a station that will disagree. With the single
source, moving the tilt bracket's feet, the controller board and two avionics
nodes in Rev T5e touched one file's constants; the merge, the parts and the
proof followed. The failure modes that remain are the interesting ones —
missing envelopes, wrong measurements — not transcription.

## When to Apply

Any subsystem whose geometry is shared by a proof, a mesh pipeline and printed
parts: the other fuselage sections when their interiors are laid out, the
nacelle ESC bays, the wing root. Start the module before the first part.

## Examples

`cargo_layout_fit.py` → `write_scad()` → `cargo_layout_t5_params.scad`:

```scad
include <cargo_layout_t5_params.scad>
WEB_X1 = GEAR_X_OUT + 5.0;   // foot / web plane, from the gear plane, not typed
BOARD_X0 ...                 // board station straight from the params file
```

and in the merge script:

```python
for x, y in clf.SHELF_BOSS:
    pos.append(box(x - 5.0, x + 5.0, y - 5.0, y + 5.0, -5.0, clf.SHELF_Z0))
```
