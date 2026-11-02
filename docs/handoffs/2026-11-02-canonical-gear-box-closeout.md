---
artifact_contract: "ce-handoff/v1"
created_at: "2026-11-02T19:10:00Z"
title: "Canonical gear box close-out (PR #276 draft) with side-hit crash study"
summary: "Gear box fused into the forward hull; side-hit failure modes recorded; bays, cartridge hatch, thigh allowable and PA12-CF Z data still open."
keywords: ["gear-box", "pr-276", "side-hit", "pa12-cf", "3d-systems", "cartridge", "landing-gear", "crash"]
cwd: "/home/steve/Documents/Vocation/Employers/Griffing.tech/designs/Serenity-UAV/.worktrees/canonical-gear-box"
resume_focus: "Regenerate the bolted gear bays with the box as keep-in, then plan the corner cartridge and hatch"
repository: "Stab-Rabbit-coding/Serenity-UAV"
repo_root_sha: "1411aee2"
branch: "feat/canonical-gear-box"
head: "02bc9fff1f8d71fbcaee148f4a27bc18a7355554"
worktree_path: "/home/steve/Documents/Vocation/Employers/Griffing.tech/designs/Serenity-UAV/.worktrees/canonical-gear-box"
---

# Canonical gear box close-out

Supersedes the earlier managed-store handoff `canonical-gear-box.md` (same branch).  Draft PR #276 → `main`.  Everything is committed and pushed (HEAD `02bc9fff`); the tree is clean.

## Where things stand

| Piece | State |
|---|---|
| Gear box fused into the forward hull as 2 mm skin | **Done and gated.**  Watertight, 0 bad edges, integrity check PASS, box-added gear overlap 0.0 mm³, +106.7 cm³ (~117 g).  `tools/gear_box_hull_merge.py`, called from `tools/merge_head_cargo_shell.py`. |
| Fore legs −65°, fore strut 80°, CF plates flush | **Done.**  Fore track 258 → 178 mm; tail-back tip angle 29.6° unchanged. |
| Hull storage | Fused hull is committed as `airframe/stls/fuselage/head_cargo_shell24_2mm_merged.stl.tar.gz` (51 MB); raw `.stl` (115 MB) is gitignored. |
| Side-hit failure study | **Done.**  `docs/LG_SIDE_HIT_FAILURE_MODES.md`, reproducible with `tools/lg_side_hit_study.py`.  Gear unchanged (owner). |
| Bolted bays inside the box | **Not regenerated.**  Fore at the old −22.4°; plates stand 313–1,481 mm³ outside hull + box; aft clash the wing by 177 mm³ (LG-AFT-BOLT-01). |
| Corner-cartridge field swap | **Requirements only.**  `docs/plans/2026-11-02-001-feat-gear-cartridge-field-swap-plan.md`.  Next: `/ce-plan`. |
| Thigh side-load sizing | **Open.**  The "grown" thigh is rejected (see below). |
| PR | Draft.  `/ce-babysit-pr` deliberately not started. |

## Side-hit study: what it says

Framing (owner 2026-11-02): any nacelle strike is a **crash**, not normal operations.  The study predicts what to repair; it is not an operating envelope.

- The fore thigh is the weak link.  Its −65° swing plane takes 91 % of a side load out of plane (aft: 47 %).
- The leg force is capped by the ductile fuse plateau (1,218 N crash, 626 N spring limit), so failure depends on **bank angle, not drop height**.
- Crash energy: the fore thigh reaches UTS (85 MPa) at bank ≥ 10.4°, the aft thigh at ≥ 21.8°.
- Gear + nacelle co-strike: the bank is 35.5° at 0° tilt, 30.5° at 45°, 23.8° at 90° and 27.6° at 135°.  The fore thigh breaks at every tilt at crash energy (1.54–1.96 × UTS).  At 1.5 ft it is 0.79–1.01 × UTS.
- The nacelle takes 1–6.5 kN in a co-strike.  Hull, box and wing stay 75–84 mm clear.
- Hip pins never govern.

Assumptions that bound trust (details in the doc §5):
- UTS is the XY datasheet value; no Z value exists.
- Roll inertia is an estimate (k = 133 mm).
- Nacelle contact stiffness is swept 100–1,000 N/mm.
- No sideways friction (it would lower every critical bank).

## Open questions and blockers

1. **PA12-CF Z-direction strength.**  The owner asked for a question to send to 3D Systems; it is drafted in the session (not committed to the repo).  The ask covers:
   - Z tensile, modulus and elongation;
   - XY and Z flexural strength;
   - notched impact, fatigue, pin-bearing and heat-set-insert pull-out;
   - a build orientation for a ~20 mm cantilever under combined bending and torsion;
   - supplied test coupons.
2. **Sizing gate gap.**  `landing_gear_r6_sizing.py` has no combined in-plane + out-of-plane thigh check and still uses the CF-PETG allowable (27.5 MPa).  The "grown" thigh (2 × Ø17) fails it (0.57× fore −65°, 0.79× even at −22.4°) and does not fit the 34 mm slot (39 mm cluster; 429 / 215 mm³ swept clash).  `cf_core` stays rejected (2026-10-19 study).
3. **Nacelle strength.**  The nacelle shell, trunnion and tilt spar are unchecked against a 1–6.5 kN strike.
4. **Gates that fail on their own.**  `tools/lg_a1b_census.py` needs a box-aware hull reference.  `tools/landing_gear_wing_clearance.py` crashes (6 collars / 4 corners; it came in with the merged `claude/3d-print-material-scaling-66d85n` branch).
5. Pre-existing: the aft CF cheeks overlap the payload keep-out by 2,312 mm³.
6. The middle/rear hull STL is 99.2 MB and will hit the same GitHub limit.

## Lessons (also in `docs/solutions/design-patterns/fuse-canonical-styling-as-skin-over-functional-hardware.md`)

- Fuse styling as skin, not a solid; reuse the hull's own keep-outs; derive starboard by mirror about `X_CL`; gate every boolean step in mm³.
- A canonical change moves a functional constraint elsewhere: flush CF plates forced the fore legs to −65°, which raised the out-of-plane side load and exposed the sizing-gate gap.
- Frame analyses by how the owner will use them: nacelle strikes are crashes, so the study predicts repair, not acceptance.

## Wrong paths to avoid

Blender planar decimation (breaks watertightness); `merge_vertices()` after the manifold union (folds loft caps); `trimesh.contains` on the 94 MB hull (OOM); a 64° fairing top (reads as a tower); round housing caps (off-character); notching the CF cheek for the pouch (cuts the load line).

## Pointers

- Plan with all decisions and findings: `docs/plans/2026-11-01-001-feat-canonical-gear-box-plan.md`.
- Renders: `docs/plans/2026-11-01-001-canonical-gear-box/`.
- Merge tool: `tools/gear_box_hull_merge.py`.
- Study tool: `tools/lg_side_hit_study.py`.
- Machine-local: the raw hull `.stl` in this worktree; scratch scripts under `/tmp/claude-1000/...`.

## Likely next path

Regenerate the bays (`generate_lg_bays.py` with `PART="envelope_port"` as keep-in, fore at −65°), then plan the cartridge and hatch, then mark the PR ready and start `/ce-babysit-pr`.  The thigh allowable depends on the 3D Systems reply.
