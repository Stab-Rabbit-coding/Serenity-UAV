---
title: Fuse canonical styling as skin over functional hardware, then re-check what it moved
date: 2026-11-02
category: design-patterns
module: airframe hull / landing gear
problem_type: design_pattern
component: tooling
severity: high
applies_when:
  - "Adding a canonical (Henning/QMx) styling element over existing functional hardware on the SLS hull"
  - "Fusing a new outer-mold-line feature into a published one-piece hull"
  - "Moving a mechanism to make it fit a canonical envelope"
tags: [canon, hull, gear-box, sls, boolean, keep-out, symmetry, landing-gear]
---

# Fuse canonical styling as skin over functional hardware, then re-check what it moved

## Context

PR #276 replaced open landing-gear bay frames with Henning's canonical gear box, fused into the one-piece SLS forward hull.  The plan is `docs/plans/2026-11-01-001-feat-canonical-gear-box-plan.md`.  The box looked right as a concept solid within an hour.  Making it functional without breaking the functional hardware took most of the work: wing root, spar and harness penetrations, flanges, bolted bays, CF backbone, the moving gear, and SLS printability.

## Guidance

1. **Fuse styling as skin, never as a solid.**  Build the box's outer and inner (INSET = wall) solids from one SCAD.  Keep the skin only outside the old hull's outer operand, and clear of the moving gear: `skin = (Bo − Bi) − O − gear`.  Open the old flank skin inside the box (`((Bi ∩ O) − I) − protect`) so the cavity drains SLS powder.  Protect the flanges, every penetration and every bolted seat from that opening.  See `tools/gear_box_hull_merge.py`.
2. **Reuse the hull's own keep-outs; never re-type them.**  The box clears the wing-root penetrations by calling `merge_cargo_interior.wing_keepout_negatives()`.  Before that call the concept box blocked the mortise (9,131 mm³), the spar socket (4,009 mm³) and every harness port.
3. **Derive starboard from port about `X_CL`, in every source.**  The LG corner rows were typed literals mirrored about the old R1 centreline, 0.1 mm off a true mirror.  That 0.1 mm was the root of about 7,000 starboard-only non-manifold edges in an earlier merge.  `tools/lg_corners.py` is now the one parser.  Wrap azimuths the same way everywhere (−157.6°, not 202.4°).
4. **Measure every boolean step with an mm³ gate.**  The gear keep-out first used the "leg (thigh+shin+foot)" feature, which omits the hip hub, lug and crank horns.  It missed 86 cm³ of gear, and 3,354 mm³ of new skin landed in the legs until the exported `hull_legs` was added.  Census the bodies a weld/clean step drops: 254 were dropped, all ≤ 0.5 mm³ residue — check that, don't assume it.
5. **Where canon cannot be exact, keep the ship's character.**  This is now a root `AGENTS.md` rule ("Airframe geometry").  Rejected in review: a round-topped housing (foreign to the faceted box) and a 64° fairing top (read as a tower).  Kept: a slim octagonal leg-support housing, the box's own chamfered vocabulary.
6. **A canonical change moves functional constraints elsewhere — re-check them.**
   - Seating the fore CF plates flush forced the fore legs from −22.4° to −65°.
   - That raised the out-of-plane share of the 308 N lateral case from 0.38 to 0.91.
   - It also exposed that `landing_gear_r6_sizing.py` never combines in-plane and out-of-plane thigh bending.
   - Fusing the box also trapped the bolted bay plate in every extraction direction, which forced a field-swap cartridge design (`docs/plans/2026-11-02-001-feat-gear-cartridge-field-swap-plan.md`).
7. **Know the storage limits of generated meshes.**  The fused hull grew to 115 MB, past GitHub's 100 MB file limit.  Planar decimation broke watertightness (2,910 bad edges) and still left 100.8 MB.  The build now writes a gzip tarball (51 MB) and the raw `.stl` is gitignored.  Convert manifold output to trimesh without `merge_vertices()`: welding folded 6 loft-cap edges.

## Why This Matters

A styling element that is visually right can still:

- block a spar socket;
- seal a powder pocket;
- trap the parts it covers;
- move a load path out of its sized plane.

Each of those is found only by measuring against the real parts and the real motion.  On an aircraft that has to be built and repaired, a hull that looks canonical but cannot be printed, assembled or field-serviced is not done.

## When to Apply

- Any new outer-mold-line feature fused into a published hull section.
- Any mechanism move made to fit a canonical envelope (re-run structural and maintenance checks, not only the clearance checks).
- Any generated artifact headed for git.

## Examples

```text
pre-trim box  x mortise 9,131 / spar socket 4,009 / 10 AWG exit 2,882 mm^3
post-trim     worst penetration overlap 0.0000 mm^3
first fuse    box-added overlap with gear 3,354 mm^3  (feature set missed the hip hub)
final fuse    box-added overlap with gear 0.0 mm^3; integrity check PASS, 0 openings
```

Related: `docs/solutions/design-patterns/build-every-joint-in-context-through-its-full-motion.md`, `docs/solutions/design-patterns/envelope-gates-pass-while-real-parts-clash.md`.
