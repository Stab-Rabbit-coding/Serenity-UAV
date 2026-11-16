---
title: Fair a forced exterior deviation into the measured canonical skin, per azimuth, with G1 at the earliest feasible station
date: 2026-11-01
category: design-patterns
module: nacelle intake cowl (64 mm pod)
problem_type: design_pattern
component: tooling
severity: medium
applies_when:
  - "A functional part (intake, fairing, boss) must stand outside the canonical hull"
  - "Blending a lofted surface into an imported, non-axisymmetric mesh skin"
  - "A generator writes a SCAD table that hand-copies constants from the SCAD"
  - "Adding a variant to an existing CFD screening tool"
tags: [nacelle, intake, canon, loft, hermite, fritsch-carlson, g1, openscad, cfd]
---

# Fair a forced exterior deviation into the measured canonical skin, per azimuth, with G1 at the earliest feasible station

## Context

The owner rule in `airframe/AGENTS.md` ("Geometry Integrity", 2026-11-01) says
that deviations from the canonical exterior hull shall be minimized and shall keep
the Serenity style and character. A 64 mm EDF needs an intake highlight radius of
1.57 in (40 mm). The canonical engine dome is narrower than that ahead of about
Z 1.2 in (30 mm), so some deviation cannot be avoided. The first build held a
cylinder of r 1.77 in (45.05 mm) to Z 0.92 in (23.3 mm) and then dropped it
inside the skin. That made a plain can standing proud of the dome, which the
Henning engine model [REF-CAD-002] never shows: in canon, the cowl rolls straight
from the lip into the bulbous forward shell.

## Guidance

1. **Measure the skin and do not idealise it.** `tools/nacelle_cowl_fair.py`
   loads the source shell in the pod-local frame. The shell files and placement
   come from `tools/nacelle_hollow_profile.py`, and the scale from
   `tools/nacelle_64_scale.py`. The tool ray-casts the outer skin radius at 5°
   azimuth steps on every 1 mm station.
2. **Keep the functional part exactly as validated.** The CFD-selected lipE nose
   (shoulder r 42.5 mm, 4.0 mm nose radius) is unchanged. Only the surface aft of
   the shoulder is new.
3. **Join the skin with G1 continuity at the earliest feasible station.** Each
   azimuth gets a monotone cubic Hermite from the shoulder (slope 0) to the skin
   radius and slope at its junction. A monotone Hermite meets an end slope `m`
   exactly only if `0 <= m <= 3 * rise / L` (Fritsch-Carlson). The junction is
   therefore the **earliest** station in Z 28–50 mm where that holds, or the
   skin's crest if the crest comes first. Earliest gives the shortest departure
   from canon.
4. **Bury the end.** The loft ends 0.3 mm inside the skin, so the skin and not
   the loft is the surface aft of the junction. This avoids coincident faces.
5. **Generate the table, and make the consumer assert parity.** The generator
   writes the lip-shoulder and sink constants it used into
   `nacelle_cowl_fair_table.scad`. The pod SCAD asserts that its own `P64_*`
   values equal them, so drift fails at parse time and not in a print.
6. **Emit triangles, not quads.** Adjacent azimuths have different junction
   stations, so a quad between them is non-planar, and OpenSCAD warns
   "PolySet has nonplanar faces".

## Why This Matters

- **The first cut put the junction at the crest on Z 28–40 and said the join was
  G1.** That was false wherever the skin was still rising at Z 40. There the
  monotone clamp reduced the end slope (stbd az 315: 0.218 → 0.105), which left a
  kink of about 6°. The code review caught it, not the renders. If you write a
  continuity claim, have the generator enforce it.
- **Prove it with numbers.** Against the measured skin from Z 0 to Z 45 mm, the
  old ring stood out up to 19.6 mm, with an integrated mean excess of 243 mm². The
  new cowl, scored with the first-cut table, stood out up to 18.2 mm with 205 mm²,
  and the skin is exactly canon from Z 37 aft. The final table was not
  re-measured. Its loft solid is smaller than the first cut's (68.4 vs 92.8 cm³),
  so its excess should be lower. Most of the remaining excess is the intake
  mouth itself, which is the functional part.
- **Aero did not regress.** The hover OpenFOAM screen
  (`tools/nacelle_intake_cfd.py`, variants `lipE_cowl_*`) on the first-cut
  geometry gave 0% reversed flow on the lip and bell at both bounding azimuths,
  and lipE's 4.2% total-pressure loss at r/R 0.95 was unchanged. The old r 45.05
  ring was 2 points better (2.1%) because a fatter outer lip turns the hover
  inflow more gently. That gain was traded for canon. The bounding azimuths for
  the final table (az 310 and az 115) were re-run: 0% reversed flow, with
  4.2% and 4.0% loss at r/R 0.95.

## When to Apply

- Any exterior part that function forces outside the canonical hull: intakes,
  sensor bulges, gear fairings, access-hatch frames.
- Any loft that blends into an imported mesh whose section is not axisymmetric.

## Examples

**CFD regression trap.** To resolve the new Hermite, I changed the downstream
station count in `nacelle_intake_cfd.py` from 8 to 40 for every variant. That
silently re-meshed the previously validated variants as well. The efficiency
review caught it. Now only variants with a `fair` field use 40 stations:

```python
n_down = 40 if bell.fair is not None else 8
```

**Self-matching wait loop (cost about 20 minutes).** A wait loop of the form
`until ... ! pgrep -f _tmp_pod_head` never exits, because `pgrep -f` matches the
loop's own command line. Match on argv[0] (`pgrep -x openscad`) instead
(auto memory [claude]: "pkill self-match kills the shell").
