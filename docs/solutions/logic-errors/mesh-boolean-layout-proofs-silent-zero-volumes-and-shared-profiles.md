---
title: "Mesh-boolean layout proofs: an unmerged STL makes manifold3d return 0 mm³ for everything, and grooves cut from a separately sampled surface go straight through the skin"
date: 2026-09-15
category: logic-errors
module: "tools/cargo_layout_fit.py, airframe/blender-scripts/merge_cargo_interior.py (_flank_profile/_ruled_slab), tools/gen_cargo_void_formers.py"
problem_type: logic_error
component: tooling
severity: high
symptoms:
  - "every intersection volume in a layout check reads 0 — including bosses that visibly cross the wall"
  - "Manifold(...).status() == Error.NotManifold and .volume() == 0 on a shell trimesh reports watertight only after process=True"
  - "a 0.8 mm decorative groove rendered as a through-slot: rays pass with no hit along one row"
  - "a 'cavity' former comes out the size of its design box, spanning outside the hull"
root_cause: "trimesh.load(process=False) leaves binary-STL per-face vertices unmerged, so manifold3d rejects the mesh and every boolean silently yields an empty solid; groove cutters built from their own coarse/fine Z sampling disagree with the skin slab's surface by mm at a curved lip; (box − shell) components connect interior to exterior wherever the design box crosses an open rim"
resolution_type: code_fix
related_components:
  - tools/cargo_layout_fit.py
  - airframe/blender-scripts/merge_cargo_interior.py
  - tools/gen_cargo_void_formers.py
  - tools/cargo_bay_envelope.py
tags: [trimesh, manifold3d, boolean, watertight, ray-cast, ruled-surface, void-former, layout-proof, silent-failure]
---

# Mesh-boolean layout proofs: three silent failure modes

## Problem

Building the Rev T5 cargo layout proof (`tools/cargo_layout_fit.py`), the ramp
fairing (`merge_cargo_interior.py`) and the chin void formers
(`tools/gen_cargo_void_formers.py`) hit three failures that all produced
*plausible-looking* output with no error.

## Symptoms

1. First run of the fit tool: every envelope, including six wall bosses, reported
   `hit 0 mm³, <gap 0 mm³` — a clean PASS on a layout that was later shown to
   foul the wall by up to 8,000 mm³.
2. Ray map of the ramp fairing: the hinge-line row (Z 14) had **no hit** across
   most of its width — the 0.8 mm groove had cut through the 2 mm skin.
3. A second ray map showed scattered "holes" all over the fairing — which turned
   out not to be holes at all.
4. The collar-rim void former came out spanning X −260..−80: the full design box,
   i.e. it included the outside of the hull.

## What Didn't Work

- Trusting a green first run. The layout tool was written, ran, and passed; only
  a sanity question ("why is a boss that must cross the skin reading 0?") exposed it.
- Fitting a single plane to the flank (rms 2.2 mm, max 5.4 mm) for the fairing:
  the canted face has a raised frame lip that a plane cannot follow.
- Eroding the cavity by intersecting six translated copies (Minkowski-free
  shrink): it fragmented the station-slab cavity into hundreds of bodies.
- Building the cavity from 1 mm extruded section slabs: T-junction seams became
  non-manifold edges after the binary-STL round trip.

## Solution

1. **Load the shell with `process=True`** so trimesh merges the STL's duplicated
   vertices; assert `is_watertight` before any boolean, and check
   `Manifold.status()`:

   ```python
   shell_tm = trimesh.load(SHELL, process=True)
   assert shell_tm.is_watertight, "published cargo shell is not watertight"
   ```

2. **Sample the flank profile once, share it.** `_flank_profile()` ray-probes
   the flank Y(z) on both sides of the opening at 0.5 mm; every slab (skin, lip,
   each groove) interpolates that one table. A groove is then exactly 0.8 mm deep
   from the same surface the skin was built on.
3. **Probe off-grid.** Rays at integer Z lie on the ruled mesh's row edges and
   miss; offset the ray grid (Z + 0.27) and check hit *parity* with
   `multiple_hits=True` — even parity everywhere is the closure test.
4. **Void former = (design box − shell), decomposed, component picked by a seed
   point.** No cavity solid is ever built. Start the box where the rim ring is
   actually closed (here Y ≥ −66; the open mating face is at −69.5 and the wall
   is not a ring until ~−67), or the interior component leaks to the exterior
   through the box's own face. Shrink each former about its own centroid for
   the wax allowance; export with `process=False` (manifold3d's output already
   shares vertices — trimesh's weld turns seam T-junctions into 4-face edges).

## Why This Works

manifold3d requires a true 2-manifold index structure; an unmerged STL is a
triangle soup, so `Manifold()` returns an empty solid and every `^`/`-`/`+`
inherits the emptiness — there is no exception path. Ruled-surface consistency
is purely a sampling question: two independent samplings of a curved edge
differ by their discretisation error, and at a lip that error exceeds the groove
depth. Component picking by seed sidesteps the need for a closed cavity, which a
hull with open mating rims and a belly aperture never has.

## Prevention

- Every mesh-boolean tool in this repo asserts watertightness after
  `process=True` and prints the shell volume; a shell volume of 0 is a hard stop.
- Any "hit 0 everywhere" result on a check that *includes* deliberate contacts
  (bosses, feet) is a tool bug until proven otherwise — include a known-contact
  envelope as a positive control.
- Closure of a fused feature is verified by an off-grid ray-parity map, not by
  `is_watertight` alone (a through-slot keeps the mesh closed).
- Formers, fairings and any other "conforms to the skin" feature derive their
  surface from one shared probe table; never sample twice.
