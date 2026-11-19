---
title: "A CFD body must be built from the real printed parts, and a named cause must be tested by an isolating run before it is written down as the cause"
date: 2026-11-19
category: logic-errors
module: "tools/od17_junction_cfd/geom.py, geom_asbuilt.py; docs/NACELLE_64MM_POWER_CROSSING_BRIEF.md"
problem_type: logic_error
component: analysis_tooling
severity: high
applies_when:
  - "building a CFD (or FEA) body to stand for a printed part"
  - "a result differs from a baseline and a single picture suggests why"
  - "a geometry script applies a placement shift that an upstream builder may already apply"
related_components:
  - tools/od17_junction_cfd/geom_asbuilt.py
  - tools/nacelle64_wing_fairing.py
  - airframe/wings-nacelles/WBS.md (OD17-FAIR-CFD, OD17-FAIR-BORE)
tags: [cfd, openfoam, as-built, isolating-run, hypothesis, double-shift]
---

# A CFD body must come from the real parts, and a cause must be tested

## What went wrong (OD17-FAIR-CFD, 2026-11-12 to 11-19)

1. **Wrong body.** The first as-built body was the fairing's outer loft with no bore. The real part
   (`Builder.part()`) has a 2.20 in (56 mm) bore through its whole length. The solid, flat-faced block
   gave 0.243 lbf, about 66 % over the baseline, and that figure was withdrawn.
2. **Double shift.** `geom.py` added the 0.91 in (23 mm) joint shift on top of parts that were already
   placed at the shifted joint. The fix was `SHIFT = 0`.
3. **Cause asserted from one picture.** The corrected run gave +23 %. One velocity section showed an
   open pocket in the bore, and "mainly from the open bore" went into the brief and the WBS. The
   isolating run (bore capped, nothing else changed) then gave **more** drag (+15 %), not less. The
   recorded cause was wrong, and the fix it pointed to (a nose cap) would have made drag worse.

## Rules

- **Build the CFD body from the part's own builder** (`Builder.part()` and the assembly-check
  placement), not from a loft or an idealised shape. Print the bounds and occupancy of every cavity
  (bores, pockets, gaps) and check them against the part before meshing.
- **Never re-apply a placement** that the upstream builder already applies. Assert one known
  coordinate (for example the collar end face at X 74.8 mm) after placement.
- **A cause is a hypothesis until an isolating run changes only that feature.** Write "hypothesis"
  in the brief and the WBS, and do not offer a fix built on it, until the run is in.
- Report the sign of the isolating difference as the robust result. Its size, from one pair of runs
  on different meshes without a grid study, is not robust.
