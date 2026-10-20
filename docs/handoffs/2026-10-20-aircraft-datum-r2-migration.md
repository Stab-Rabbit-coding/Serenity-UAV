---
artifact_contract: "ce-handoff/v1"
created_at: "2026-10-20T12:55:00Z"
title: "Aircraft datum R2 migration, mid-flight"
summary: "R1 hull frame to R2 aircraft datum (centreline / nose / 3.0 in ground) migration; U1-U6 mostly done, U7-U11 partial; rebuild queue waiting behind it"
keywords: ["datum", "R2", "hull frame", "migration", "fuselage", "landing gear", "cargo", "symmetry"]
cwd: "$HOME/Documents/Vocation/Employers/Griffing.tech/designs/Serenity-UAV/.claude/worktrees/fuselage-reconcile"
resume_focus: "Finish plan 2026-10-19-001 units U6-U11, run the regression compare, then do the one-time R2 rebuild"
repository: "github.com/Stab-Rabbit-coding/Serenity-UAV"
repo_root_sha: "1411aee2adfe082e69ec11a5086cf60a281825c2"
branch: "worktree-fuselage-reconcile"
head: "5149b8ce8070bb768243e88972656d9dd4664669 (before the commit that carries this file)"
worktree_path: ".claude/worktrees/fuselage-reconcile"
---

# Handoff: aircraft datum R2 migration (2026-10-20)

## Objective

Owner direction from Stab-Rabbit-coding on 2026-10-19: the airframe has one
datum. The origin is the centreline, the nose tip and the ground plane, with
the aircraft resting on the 3.0 in (76.2 mm) gear. The axes are unchanged:
X is positive to port, Y is positive aft and Z is positive dorsal. Only the
nacelles carry their own translations. Only PCBs keep local coordinates, and
only inside KiCad. The STEP or STL of every PCB, and of every printed part, is
published at its installed position, one STL per installed instance. The order
is migrate first, then rebuild once in R2.

The governing plan is
`docs/plans/2026-10-19-001-aircraft-datum-migration-plan.md`. Section 4 lists
the units U1 to U11 and section 5 the rebuild queue.

## Frame facts

- R2 = R1 + `R1_TO_R2` = (169.85, 305.70, 80.00) mm. The single source is
  `tools/hull_datums.py`. SCAD files include the generated
  `airframe/openscad/hull_datums.scad`.
- R2 datums: X_CL 0, Y_NOSE 0, GROUND_Z_3IN 0, BELLY_Z 80, SPAR_Y 326.700,
  SPAR_Z 146.851. The nose tip sits at Y −0.004 mm.
- The STL header marker is `hd.FRAME_MARKER` (`SerenityUAV AIRCRAFT-FRAME R2`).
  `bake_hull_frame.is_baked` exits on a file that still carries the R1 marker.

## State by unit

| Unit | State |
| --- | --- |
| U1 datum module | Done. The header of `scad_text()` still says "Hull frame" and needs rewording. |
| U2 inventory | Done: `tools/frame_inventory.py` and `tools/datum_r2_stl_list.txt` (46 STLs). |
| U3 drift gate | `tools/check_datum_drift.py` (gates D1-D5) is written. It is **not** wired into `.githooks/pre-commit` or CI yet. |
| U4 STLs | 41 of 46 are translated and verified. Five fail verification (listed below). |
| U5 bake table + assembly | `bake_hull_frame.py` COMPONENTS are in R2. `serenity_assembly.py` is **not** migrated: it still has local T_BAKE copies, `CARGO_X_CL −170`, `T5_STBD_DX` and legacy accessory placements. |
| U6 layout tools | `cargo_layout_fit.py` and `middle_layout_fit.py` are migrated and lint-clean. The generated SCAD params (`cargo_layout_t5_params.scad`, `middle_layout_t6_params.scad`) have **not** been regenerated. |
| U7 merge pipelines | Migrated: `merge_cargo_interior.py` constants, `add_structural_features.py`, `open_mating_faces.py`, `merge_head_interior.py` (BAKE_T from `hd`), and `cargo_door_hinge_params.{py,scad}`. Still to migrate: `generate_cargo_doors`, `generate_conforming_collars`, `generate_wing_root_flange`, `gen_cargo_void_formers`, `regen_rear_interior`. No merge has been re-run in R2 yet. |
| U8 gates and studies | Migrated: `cargo_bay_envelope`, `cargo_bulkhead_context`, `landing_gear_bay_station_fit`, `landing_gear_bay_pad_fit`, `landing_gear_foot_stance`, `landing_gear_opening_fit`, `landing_gear_ground_clearance`, `landing_gear_r6_sizing`, `nacelle_mass_cg`, `auw_ledger`, `verify_bow_pod`. Still to migrate: `wing_root_deconflict`, `wing_spar_carrythrough`, `wing_internal_clearance`, `landing_gear_wing_clearance`, `nacelle_esc_bay_fit`, `nozzle_linkage_check`, `airframe_interface_census` (CENTRE_X), and the rest of the inventory. |
| U9 SCAD parts | Done for both canonical leg SCADs (CORNERS in R2, `include <../hull_datums.scad>`). Still to do: `port_tilt_spar_assembly.scad` and the other placed SCADs. |
| U10 docs | The AGENTS.md datum rule is done (root, airframe and avionics). `docs/HULL_FRAME_REFERENCE` has not been updated. |
| U11 installed instances | Not started (117 part-local and 35 envelope STLs). |

The tree is **deliberately inconsistent** in the middle of the migration.
Tools that are already migrated read meshes or modules that are not, so gate
failures right now are expected and do not show defects.

## STLs that failed R2 verification

These five are still in R1. Regenerate them in R2; do not translate them.

- `cargo_sect_shell24_2mm_repaired.stl` (regenerate through `merge_cargo_interior.py`)
- `lg_r6_3_0in_bay_aft-port.stl`, `lg_r6_3_0in_bay_aft-stbd.stl`
- `void_former_cargo_harness_trunk_port.stl`, `void_former_cargo_harness_trunk_stbd.stl`

Root cause: float32 STL export collapses near-coincident vertices (gaps below
about 3e-5 mm) at the larger R2 coordinates. `tools/migrate_stl_r2.py` welds
at 1e-4 mm before translating, which saved the middle shell, the rear shell
and the fore-port bay, but not these five. Do not retry a plain translation.

## Regression harness

`tools/datum_regression.py snapshot DIR` and `compare A B`. The R1 baseline of
19 tools is committed at `docs/plans/2026-10-19-001-baseline-r1/`. It was
copied out of the session scratchpad, which is wiped on resume. Some tools
already exited nonzero in R1: `status.json` gives cargo_layout 1,
bay_function 2, middle 1, wing_clearance 1 and thigh 2. In the compare,
positions may change only by the datum offsets. The compare has not been run.

## Rebuild queue (plan section 5, after the migration)

The owner decided all of these in this session; they are not open questions.

- **Cargo symmetry.** Rebuild cargo as a mirror of its port half about X = 0.
  Head and rear were already re-centred (commit `5149b8ce`). Starboard twins
  (gear corners, wall brackets) become exact mirrors. Re-measure the skid rods.
- **Thigh.** The grown printed thigh (17/22) becomes the default. The CF rod
  core was rejected because its anchor fails in the crash case. Wires: ductile
  Ø5.27, spring Ø4.06. ROW_PITCH ≈ 7.1. Bosses grow to at least 137 mm²
  bearing (about 14 × 14 mm); the present bosses fail before the fuse at
  0.82×. Use the two-row layout at both stations.
- **Failure hierarchy.** Owner rule: wire fuse < leg < bay/hull, with mount
  capacity at least 1.25× the leg's breaking moment. Any option that breaks the
  hull or the bay is an automatic failure. A nozzle petal strike may not break
  the nacelle or the wing (NAC-64-PETAL-FUSE).
- **F2 fore station.** Chamfer the payload fore edges 8 × 5.5 mm, add a door
  fore-corner relief, and amend the payload spec in the README.
- **Doors.** Port opens first and closes over starboard, held by a single
  latch.
- **Open fit defects.** The brake guide has no mount. The starboard tilt
  bracket protrudes through the skin. The battery cradle has to grow
  (BATT-01/02). The XT60 runs at about 150 A, a WARNING-level item, so move to
  XT90 or AS150 (PWR-CONN-01).
- **Mass.** Target 13.0 lbm (5.90 kg). The ledger currently reads about
  6,049 g (13.34 lbm), so about 0.34 lbm (154 g) remains to find, plus margin.
  Approved levers: the nacelle foam core (plan 2026-10-03-001 U1/U3/U4/U6) and
  the FE PDB forward re-route. NoNFO was **not** approved.
- **NAC-64-REBAKE.** The published 64 mm pods are not at the ×1.06 scale.
- **Close-out.** Re-run assembly sync and the placement audit
  (`tools/placement_audit.py`), then all gates, then the final AUW and T/W.

## Rules learned this session

- A `MARKER` or datum is never re-typed. Import `tools/hull_datums.py`, or
  include the generated SCAD.
- `tools/shift_baked_stl.py` now refuses R1 files, because the marker comes
  from `hd`.
- `tools/lg_corners.py` parses the CORNERS table from
  `canonical_leg_r6_3_0in.scad`. Python gear tools must use it, not a copy.

## Pointers

- Plan: `docs/plans/2026-10-19-001-aircraft-datum-migration-plan.md`
- Review artifact from earlier in the session (gear and thigh decisions):
  <https://claude.ai/artifact/MujAWSqpV8zzsoimaiTmmY>
- Machine-local session transcript:
  `$HOME/.claude/projects/-home-steve-Documents-Vocation-Employers-Griffing-tech-designs-Serenity-UAV--claude-worktrees-fuselage-reconcile/e55b1155-9e5b-4ae9-abcf-fba848d4996f.jsonl`

*Handoff written by Claude (Claude Opus 5.5, Anthropic) for
Stab-Rabbit-coding, 2026-10-20, per `AGENTS.md` §3 AI attribution.*
