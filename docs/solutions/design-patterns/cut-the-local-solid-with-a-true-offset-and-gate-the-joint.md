---
title: "When a printed part must pass through hull material, cut the small local solid with a true offset and gate the joint's integrity"
date: 2026-10-12
category: design-patterns
module: "cargo hull merge / landing-gear bays (any hull feature that must give way to a mating part)"
problem_type: design_pattern
component: tooling
severity: high
applies_when:
  - "a generated part (bay, bracket, liner) overlaps hull material the merge adds or keeps"
  - "a fit clearance is needed between the part and the hull it sits in"
  - "the hull feature being cut carries load (a bolt seat, a bonded collar, a splice joint)"
related_components:
  - airframe/blender-scripts/merge_cargo_interior.py
  - tools/lg_collar_integrity.py
  - tools/generate_lg_bays.py
tags: [hull-merge, boolean, minkowski, offset, seat-collar, splice-collar, landing-gear, manifold3d]
---

## Context

In BHD-02g (2026-10-11), the two-row landing-gear wire layout ran a boss
cluster through hull material at the aft gear corners: carrier ∩ shell
620 / 526 mm³. The hull merge had to give way to the printed bay, with
a fit clearance. Three attempts failed before one worked.

1. **The whole bay dilated by 15 shifted copies, cut from the whole
   shell.** The near-coincident faces left the merged shell non-manifold,
   and `open_mating_faces.ensure_open` crashed in the export repair. Not
   published.
2. **Convex hulls of each overlap piece.** On the source hull the overlap
   joins the liner, the seat collar and the cluster. The hulls became blobs
   of 3,200–4,500 mm³ that would have taken the seat collar's bolt
   bearing. Not published.
3. **A true offset (Minkowski sum) of each bay, cut from the whole shell.**
   The main boolean passed, but the result had 1,195 non-manifold edges
   and the export repair failed again. Not published.
4. **A true offset of each bay, cut from the bay's own seat-collar
   positive only, keeping the bearing band under the flange.** Clean:
   watertight, one body, CI-valid.

The overlap was in the merge's **seat collar positive**, a small local
solid, not in the source hull. The source-hull overlap pieces were
14–89 mm³.

## Guidance

1. **Find which solid the part actually overlaps before cutting.**
   Intersect with each merge positive and with the source hull separately.
   Here it was positive #14, the bay's own collar.
2. **Cut that small local solid, not the whole shell.** A boolean between
   a 50k-face part and a 1M-face shell, near coincident surfaces, is the
   case that fails. A boolean against a 30k mm³ collar does not.
3. **Use a true offset for the clearance:**
   `manifold.simplify(0.05).minkowski_sum(Manifold.sphere(clr, 8))`. This
   took about 30 s per bay and gave one valid body. Shifted copies and
   convex hulls are not offsets.
4. **Exclude the load-bearing face from the cut.** Here that is the skin
   layer from −1 to T + 0.5 inside the flange outline, which the M3s clamp
   onto.
5. **Gate the joint's integrity, not just its volume.** `tools/lg_collar_integrity.py`
   checks three things and reports a fourth:
   - every seat collar is still ONE piece, ignoring sub-1 mm³ boolean
     slivers;
   - each collar's surviving volume against the uncut layer is reported
     (not gated — the wall-bond comparison in the 2026-10-12 result was a
     one-off measurement);
   - there is bearing material under every M3 (≥ 150 mm³);
   - the neighbouring splice-collar joints are untouched, judged against
     each collar mesh grown 2 mm and not against a crude Y band, since the
     band also contains the bay pockets.

## Why This Matters

A hull that merges "PASS" can still have cut away the material a joint
depends on. A volume check would not have caught the convex-hull blobs:
they were legal solids. A body-count check on the collar first reported
a false split, which turned out to be a 0.0 mm³ sliver. Only the
per-fastener bearing check and the wall-bond comparison say whether the
joint still works.

## When to Apply

- Any time a generated part must pass through material the merge creates.
- Any cut near a fastener seat or a bonded or splice joint.

## Examples

**Result (2026-10-12).**

- Seat-collar volume against the previous shell: fore −3.5 %, aft
  −9.8 / −8.6 %.
- Every collar is one piece, and its wall bond is unchanged (fore 513.9 /
  328.0 mm³).
- M3 bearing is 172–368 mm³.
- Both splice-collar joints show 0.00 mm³ of change at the collar or its
  bond face.

AI attribution: drafted by Claude (Claude Opus 5.5, Anthropic) from the
2026-10-11/12 session, under the direction of Stab-Rabbit-coding.
