---
artifact_contract: "ce-handoff/v1"
created_at: "2026-10-26T12:00:00Z"
title: "Split battery + head rail (plan 001) and FE multi-battery PDB (plan 002)"
summary: "Two implementation-ready, doc-reviewed plans for the split 6S main pack, head-section rail and audit, optional third cell, and the Flight Engineer three-input PDB and harnesses; nothing implemented or pushed yet."
keywords: ["split-battery", "head-rail", "third-cell", "flight-engineer", "pdb", "LTC4370", "LTC4359", "harness", "PWR-CONN-01", "BATT-02", "LG-LOADPATH", "fuselage-reconcile"]
cwd: ".claude/worktrees/fuselage-reconcile"
resume_focus: "Start plan 002 U1 (LTC4370/LTC4359 25.2 V gate + hover-current reconciliation) and plan 001 U1 (head-section R2 migration) after the owner answers the open questions."
repository: "Serenity-UAV"
repo_root_sha: "1411aee2adfe082e69ec11a5086cf60a281825c2"
branch: "worktree-fuselage-reconcile"
head: "74024c3714b1e5003a34c4ce8d20d92d5a1cfc76"
worktree_path: ".claude/worktrees/fuselage-reconcile"
---

# Handoff: split battery, head rail, and FE multi-battery PDB

**Author:** Claude (Claude Opus 5.5, Anthropic), under the direction of
Stab-Rabbit-coding, per `AGENTS.md` §3.
**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)

## 1. Objective

The owner directed, on 2026-10-26:

- Specify the split main pack as two cells, one in the cargo cradle and one in the head, with a rail through the head/cargo collar so the head cell swaps from the cargo bay. The head has no belly panel.
- Specify an optional third cell that takes the place of the payload box.
- Use this work to drive the detailed visual and mechanical audit and update of the head section.
- Plan the Flight Engineer PDB and power harnesses separately, as active work and no longer a deferred Phase 12 task.

## 2. Authoritative documents

| Document | What matters |
| --- | --- |
| `docs/plans/2026-10-26-001-feat-split-battery-head-rail-plan.md` | Units U1–U7. KTD5 was verified only for Y 200–328. R7's 5 g figure is marked "requires verification". The third cell stays non-jettisonable until plan 002 R12 is in place. Open Questions Q1–Q3 are at the end. |
| `docs/plans/2026-10-26-002-feat-fe-multi-battery-pdb-plan.md` | Units U1–U6. **U1 step 1 is a stop gate:** the LTC4370 and LTC4359 must be rated for 25.2 V plus margin. R4 sizes each input for its worst case. R5 is RTH-or-land. R12 is the breakaway connector plus isolate-before-release. |
| `docs/BATTERY_SPLIT_OPTIONS.md` | The verified pack listings, and the AUW / CG / C-rate table. Configuration S1 (2 × Tattu 6S 2200 95C) is the one chosen. §7 item 5 flags Tattu's PRC domicile as an owner sourcing decision. |
| `WBS.md` (SPLIT-BATT, FE-MULTIBATT, §0.8 HEAD-CELL-G and the LTC input-range item); `deferred/WBS.md` §Phase12 | Phase 12 is promoted to active. Plan 002 U6 retires the deferred entry formally. |
| `docs/LG_BELLCRANK_LOAD_PATH_STUDY.md`, `tools/lg_bellcrank_fbd.py`, `tools/lg_fuse_material.py` | The gear load-path study and the fuse material trade. |

## 3. Decisions already made (do not reopen)

- **Fuse:** 6061-T6 in axial tension, Ø4.60 mm, 33.9 mm gauge, 19.4 g for all eight wires. Spring steel was rejected because the fuse has to yield, not spring back. Annealed brass was rejected because it work-hardens (high Su/Sy).
- **Material preference order (owner):** composite before brass or aluminium, brass or aluminium before spring steel, and spring steel before stainless. Absorber wires stay metal, because ductility is their function.
- **Main pack:** 2 × Tattu 6S 2200 95C in parallel, matched set, plus the optional Tattu 6S 1600 160C in the payload box.
- **Combiner:** LTC4370-class current share for the matched pair and LTC4359-class ideal diode for the third input. Both are subject to the plan 002 U1 voltage gate.
- **Head cell access:** via a rail through the collar from the cargo bay. No head belly panel.
- **Cargo door rework** and the datum R2 migration of the cargo, gear and tools are done (see §5).

## 4. Open owner decisions

| ID | Question | Blocks |
| --- | --- | --- |
| LG-LOADPATH | Option A, balanced couple (+32.2 g, worst margin 1.07, recommended), or Option B, metal path (+128.8 g)? | Gear bellcrank rebuild. F2 waits on this. |
| Plan 001 Q1 | Third-cell jettison: required, or permanently non-jettisonable? | Plan 002 R12 scope |
| Plan 001 Q2 | Crash g for the head-cell retention (the 5 g figure is unverified)? | Plan 001 R7 sled and stop sizing |
| Plan 001 Q3 | Minimum mission time? | The endurance check and whether S1 alone is sufficient |
| BATT §7.5 | Tattu (PRC-domiciled cell maker) or a cell from another maker? | Procurement |

## 5. State of `worktree-fuselage-reconcile`

- **HEAD:** `74024c37`. The branch is 64 commits ahead of `origin/main`. **Nothing has been pushed.** Work in the worktree only; the shared checkout switches branches, see memory `feedback_shared_checkout_use_worktree`.
- **Done this session:**
  - Datum R2 migration of the cargo, gear and tools, with the drift gate wired in (commits from `3df5f82d` to `bae6a47d`).
  - Cargo symmetry fix (`97a1d290`).
  - Tilt bracket slots (`4eb7e435`).
  - Door rework Rev B (`0a6c491f`, `48d7d50d`).
  - Gear FBD study (`0a3fd936`, `3c92f018`).
  - Fuse trade (`e388195c` to `a72f07b1`).
  - Battery options (`7a29561c`).
  - Both plans (`ce266ead`), with the doc-review fixes folded in (`74024c37`).
- **Not started:** every implementation unit in both plans.
- **Known still pending:**
  - The head shell SCAD is still in the legacy frame (`TODO.md` §1.1.1). Plan 001 U1 owns the head R2 migration.
  - `tools/head_bulkhead_context.py` is named in plan 001 but does not exist yet.
  - The ASM-PLACE items are open.
  - PWR-CONN-01 is now owned by plan 002 U4.
- **Fragile:** the regression snapshot tool rewrites tracked STLs as a side effect. If it does, restore them with `git checkout -- <stl>`.

## 6. Traps a fresh agent is likely to hit

- **The head bay is not empty.** It holds:
  - the Observer board behind the bow faceplate, with camera, ToF and laser bores at about Y 0–70;
  - the pitot line;
  - the nose avionics trunk (Ethernet ring and CAN), which needs its own harness channel.
- **Hover current conflict.** 76 A (FE document) and about 150 A (WBS PWR-CONN-01) disagree. Plan 002 U1 reconciles them; do not size anything before that.
- **Edit the FE KiCad files by injection.** Do not regenerate them (`avionics/kicad/FlightEngineer/GENERATOR_DRIFT_ANALYSIS.md`). Use a `kicad-cli` at or above the files' generator version.
- **Line endings and generated files:**
  - The BOM CSV is CRLF; write it with `lineterminator="\r\n"` and keep the CSV and JSON in parity.
  - Never hand-edit a `TODO.md`; regenerate it with `tools/gen_todo_from_wbs.py`.
  - Resolve conflicts in the index files by regenerating them.
- **Sourcing rule.** Every new IC needs a non-PRC/RU/IR/DPRK manufacturer and an NDA-free datasheet catalogued in `REFERENCES.md` (`AGENTS.md` §5).

## 7. Plausible next steps

1. Get the owner's answers to §4. Q2 and Q3 most affect plan 001; Q1 affects plan 002.
2. Plan 002: run U1 (voltage gate, hover-current reconciliation, datasheet reads), then U2, then U3/U4/U5 in parallel, then U6.
3. Plan 001: run U1 (head R2 migration and audit context), then the rail, sled and stop units, and pass the lead routes to plan 002 U4.

Relevant skills: `ce-work` (execute the plans), `mechanical-engineering`, `statics-and-dynamics`, `openscad`, `3d-print-design` (head and rail), `kicad` and `datasheets` (FE board), `pcb-engineer`.

## Addendum (2026-10-26, later the same session)

Owner decisions since this handoff was written; these supersede §2–§4 where they conflict.

- **Combiner:** the LTC4370 fails the 6S gate (24 V absolute maximum) [REF-PWR-014]. Plan 002 KTD1 is now one LTC4359 with back-to-back FETs per input [REF-PWR-015]. The pair shares current passively.
- **Third cell first (plan 002 R13):** firmware holds the pair's SHDN low while the third cell runs, then hands over make-before-break and isolates the third cell. Undriven SHDN re-enables the pair (fail-safe). Q1 resolved: drain it first, then jettison it.
- **Head-cell catch (plan 001 R7, Q2 resolved):** 79.4 g in every direction, from the gear design's 4 ft level peak; re-check after LG-LOADPATH.
- **Still open:** LG-LOADPATH, Q3 (mission time), Tattu sourcing, the analog.com URL check and Analog Devices' domicile record.
