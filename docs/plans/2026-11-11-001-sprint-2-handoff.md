# Sprint 2 handoff — draw the 4 × 10 AWG route (WA-R10), from the OD-17 decision

**Written 2026-11-11, end of the session that decided OD-17.** Branch `ccr-8ff05bfb-r6gena`, PR #281 (draft → ready;
merge state is the owner's). Read `AGENTS.md`, then the plan section "S2" in
`docs/plans/2026-11-07-001-feat-rev-u-completion-execution-plan.md`, then this file.

## Goal (one sentence)
Implement the decided OD-17 geometry so the bundle has a drawn, clearance-proven path from the spar bore to the
disconnect bay: `tools/nacelle64_assembly_check.py --stage cable` finds a route at r 0.32 in (8.14 mm) on both
sides, bend radius ≥ 3 × wire OD at every bend, both WA-R10 entries closed (plan target −3).

## Owner decisions in force (all recorded in the repo)
| Decision | Value |
|---|---|
| OD-17 power crossing | **Option D**: tilt joint moved **0.91 in (23 mm) outboard**. (18 mm was wrong: the 2 × 2 wire group bends at R 16.5/22 mm.) |
| Fairing | Wing-fixed aft fairing behind the rotating collar (Ø2.13 in (54 mm) collar is its nose), NACA-type tail to the wing trailing-edge line `z_te(x) = 176.0 + 0.42 (x − 84.3)` mm; `tools/nacelle64_optD_aft_fairing.py` |
| Junction | **Rounded end plate with fillets** (0.24 in (6 mm) convex rounding, 1 mm wall, 0.24 in (6 mm) concave fillet); not the 1.50 in glove. CFD: 14 % less drag |
| Wing taper | **22.8° kept** (tip chord 3.66 in (93 mm)); the 11.9° longer tail was rejected |
| OD-1 | Option A, cartridge 0.12 in (3 mm) shorter (done) |
| Bay stud insert | 0.138 in (3.5 mm) (done, NAC-64-ASM-03 closed) |
| Units | Imperial first, metric in parentheses, everywhere |
| Presentation | Every decision as an Owner Decision Brief (`docs/DOC_TEMPLATES.md`): statics/dynamics, function, structural integrity, mechanism/component interactions, weight & balance, canonical shape, each with a picture and vectors |

## What exists
- `docs/NACELLE_64MM_POWER_CROSSING_BRIEF.md` — the brief: options, option D model, fairing, junction CFD, longer-tail CFD, decisions.
- `tools/nacelle64_optD_concept.py` (wire routing and renders), `nacelle64_optD_aft_fairing.py`, `nacelle64_optD_glove.py`, `tools/od17_junction_cfd/` (OpenFOAM), `tools/nacelle64_assembly_check.py` (stages static, sweep, cable, bay), `tools/wbs_burndown.py`.
- CFD figures and options in `docs/figures/nacelle64_od17_*`.
- Baseline `docs/plans/2026-11-07-001-burndown-baseline.json`; at close of this session `wbs_burndown.py` reads 714 open / 559 closed (`closed+` +3 over baseline; the +2 open are the two findings logged below).

## What S2 does now (in this order)
1. Re-render the live pod and trunnion (the scratch renders used so far are not in the repo and the container is gone):
   the pod SCAD is `airframe/openscad/nacelles/nacelle_pod_64mm_tandem.scad` (OpenSCAD ≈ 11 min of CPU, run it in the
   background); the trunnion per `nacelle64_assembly_check.py`'s header. Sanity: `--stage static` shows no overlap.
2. Move the joint 0.91 in (23 mm) outboard in the SCAD/tools (`SHIFT` in `nacelle64_optD_concept.py` is 23.0), cut the wire channels in the
   pod, set harness lengths, record SPAR-20-WIREOD (assumed 0.217 in (5.5 mm); cite the datasheet/measurement).
3. Add the aft fairing and end plate as a published part (new BOM row and ledger mesh) with its mass (0.071 lbm (32.2 g) solid PA CF per
   side before the plate); update the CG ledger (`tools/auw_ledger.py`) and `bom_revU.csv`; run `tools/check_bom_mesh_sync.py`.
4. Re-run the sweeps (static, tilt −5…135°, cable) on the moved joint; the old "0 in³" results do not carry over (lesson:
   `docs/solutions/workflow-issues/a-recorded-route-or-clearance-goes-stale-when-its-part-changes.md`).
5. Close the WA-R10 entries in `airframe/wings-nacelles/WBS.md` with full notes, then `python3 tools/gen_todo_from_wbs.py`.
6. Present the result to the owner as an Owner Decision Brief where a decision is needed.

## Traps already paid for
- Tilt sign: hover = exhaust down; use `tilt_matrix(deg) = rot_x(−deg)` (a wrong sign once produced a false finding, ASM-02, retracted).
- CI: flake8 at 100 columns on **Python 3.11** (byte-compile with `/usr/bin/python3.11 -m py_compile`; autopep8 can split f-strings only 3.12 parses);
  mypy; shfmt/shellcheck on `*.sh`; `tools/precommit_index.py` must run **after** `git add`, then add its outputs;
  `gen_todo_from_wbs.py --check`; `sync_operators_manual.py --check`; WBS first line ≤ 70 chars for TODO.
- Licences: tools that write or render meshes/CAD are CERN-OHL-W-2.0 (headers corrected this session for the four geometry tools; `nacelle64_assembly_check.py` and `nacelle_mass_cg_64.py` still say MIT — review).
- OpenFOAM in this environment: see `docs/solutions/runtime-errors/openfoam-v1912-ubuntu-build-and-steady-rans-pitfalls.md`.

## Open items logged, not part of S2's target
`OD17-TOOLS-01` (one shared fairing module; TE floor 0.6 vs 1.0 mm) and `WBS-BURNDOWN-01` (count closures by item ID) in
`airframe/wings-nacelles/WBS.md`. Owner queue still open: OD-2 winch, OD-3 ESC rating, OD-4 re-bake, OD-5…OD-16 as in the plan §5.
Known repo alert: GitHub reports 4 Dependabot alerts on `main` (1 high, 1 moderate, 2 low); not investigated.

## Close-out ritual (plan §4, every sprint)
doc review + three `--check`s → `/code-review medium` → one `docs/solutions/` lesson → commit with trailers, push, update PR, subscribe → burndown vs baseline.
