---
title: "Ubuntu OpenFOAM v1912: function objects crash (sha1 IOstream), scotch is missing, two MPI jobs thrash 4 cores, and steady RANS in a separated wake never settles"
date: 2026-11-11
category: runtime-errors
module: "tools/od17_junction_cfd/ (mkcase.py, run.sh, post.py)"
problem_type: runtime_error
component: tooling
severity: medium
applies_when:
  - "running OpenFOAM from the Ubuntu `openfoam` apt package (v1912) in the cloud container"
  - "a simpleFoam case with massive separation (bluff or thick bodies at Re ~1e5)"
related_components:
  - tools/od17_junction_cfd/mkcase.py
  - tools/od17_junction_cfd/post.py
tags: [openfoam, simpleFoam, function-objects, scotch, mpirun, averaging, y-plus]
root_cause: "The Ubuntu v1912 build fails any controlDict function object with a 'sha1' IOstream error; it ships no scotch decomposition; and the steady solution of a separated flow oscillates by several percent from iteration to iteration"
---

# OpenFOAM v1912 (Ubuntu) pitfalls found in the OD-17 junction CFD

## What happened and what to do

| Symptom | Cause | Fix used |
|---|---|---|
| `forces`, `wallShearStress`, `yPlus` function objects abort with a `sha1` IOstream error | broken function-object I/O in the Ubuntu build | `functions { }` in controlDict; compute forces, wall shear and y+ in `post.py` from the near-wall cells (tau = (nu + nut_face)·U_t/d, pressure force = rho·sum p·n·A) |
| `decomposePar` fails with method `scotch` | scotch not built in | `method hierarchical; n (2 2 1)` |
| Two 4-way `mpirun` jobs at once ran far slower than one after the other | 4 cores | run cases one after the other, `--oversubscribe` only for one job |
| Drag moved about 7 % between written times | steady RANS in a separated wake does not converge to a point | run 2000 iterations, write every 50, average iterations 1500–2000, report the standard deviation, and decide only on differences several standard deviations wide (the end plate vs glove drag gap was about 5; the reversed-area gap about 1.2, so it was reported as weak) |
| Container restart mid-run | ephemeral container | `writeInterval 50` and `purgeWrite 0` so a run can resume with `startFrom latestTime` |

## Check before trusting a result

Median y+ was 4–5 (95th percentile 13–14), inside the range the Spalding wall function accepts; report it
every time. A single mesh with no grid study means absolute drag is uncertain; use it for A-versus-B only,
and say so.
