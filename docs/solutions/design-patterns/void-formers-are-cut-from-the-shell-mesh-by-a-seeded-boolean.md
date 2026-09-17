---
title: "Void formers for a foam pour are (design box − shell) picked by a seed point, exported without re-processing — never hand-drawn and never stacked slabs"
date: 2026-09-16
category: design-patterns
module: "cargo section foam — tools/gen_cargo_void_formers.py"
problem_type: design_pattern
component: tooling
severity: medium
applies_when:
  - "a printed former, plug or insert must fit a compound-curved cavity of a published shell mesh"
  - "a cavity solid is being assembled from stacked boxes or slabs and the result reports non-manifold seams"
  - "a manifold3d result is being exported through trimesh and comes back fragmented or with flipped normals"
  - "a former's design box reaches a region where the shell is not a closed ring (an open mating face)"
related_components:
  - tools/gen_cargo_void_formers.py
  - tools/cargo_layout_fit.py
  - docs/CARGO_SECTION_LAYOUT.md
tags: [void-former, foam, manifold3d, trimesh, boolean, decompose, cargo-section, printed-fixture]
---

# Void formers for a foam pour are (design box − shell) picked by a seed point, exported without re-processing — never hand-drawn and never stacked slabs

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP. **AI note:** drafted by
Claude (model: Claude Opus 5, Anthropic) under the author's direction,
2026-09-16, per `AGENTS.md` §3. **License:** CC BY-SA 4.0.

## Context

The cargo section's chin may optionally be foamed, and the collar seat, the
battery drop path, the harness ways and (Rev T5e) the chin node bay must stay
foam-free. The first attempt built each former as a stack of slabs hugging
the cavity and subtracted the shell: the result had non-manifold seams
between slabs and fragmented erosion where slab edges met the skin. Hand-drawn
boxes were either too big to insert past the skin's curvature or left a foam
fillet exactly where the equipment later goes.

## Guidance

1. **Build the former as one boolean:** `(design box) − shell`, then
   `decompose()` and keep the component that contains a seed point known to
   be inside the cavity (`gen_cargo_void_formers.py:103-115`,
   `former_in_box`). The cavity never has to be modelled; the shell defines it.
2. **Keep the design box inside the closed part of the shell.** The cargo
   rim ring is not closed forward of Y ≈ −67 (open mating face at −69.5), so
   a box starting at −71.5 leaks out of the section and the "cavity" component
   becomes the outside world. The formers start at Y −66.
3. **Shrink for the wax film and print tolerance** by scaling about the
   former's own centroid (`SHRINK_MM = 0.4`), not by offsetting faces.
4. **Export the manifold3d result with `process=False`.** manifold3d's output
   is already a proper 2-manifold; letting trimesh re-process (merge/weld) it
   on export fragments thin regions and flips normals. Load *inputs* with
   `process=True` (or manifold3d silently returns zero volumes — see the
   mesh-boolean doc), export *outputs* untouched.
5. **Re-derive after every shell merge.** The formers are cut from the
   published STL; a new boss (Rev T5e added eight) changes the cavity.
   Regenerating is one command; a stale former will not insert.
6. **Keep formers from overlapping each other.** When equipment moves into a
   former's box (the chin nodes moved under the battery chimney), split the
   boxes so each former owns a disjoint volume — the chimney now starts at the
   battery underside and a `node_bay` former takes the floor.

## Why This Matters

A foam pour is irreversible; a former that does not fit, or that lets foam
into a bonding seat, costs the printed section. Deriving formers from the
mesh makes fit a property of the boolean rather than of a modeller's eye,
and makes the set regenerable whenever the shell changes.

## When to Apply

Any removable fixture that must match a published shell cavity: void formers,
alignment plugs for splice collars, potting dams, bonding jigs.

## Examples

Rev T5e set (`/usr/bin/python3 tools/gen_cargo_void_formers.py`): collar_rim
57.8 cm³, batt_chimney 79.9 (Z 90..131), harness_trunk_port/stbd 27.3/27.5,
node_bay 128.1 (X −214..−126, Z 44..90); chin cavity 955 cm³, foamable
634 cm³ ≈ 20 g of 2 lb/ft³ PU. All five STLs pass `tools/validate_stls.py`.
