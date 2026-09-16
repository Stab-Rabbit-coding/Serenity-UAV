# Superseded Design Documents

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0

---

## POWER_SYSTEM_Q.md — Archived 2026-06-09

**Superseded by:** `docs/POWER_DISTRIBUTION.md` (authoritative) + `avionics/kicad/Kaylee.md`

**Reason for archival:**

- Phase numbering was inconsistent with the project build guide (used Phases 2–6 /
  Phase 7 labels that do not match the TODO.md WBS, which uses Phases 5–10 / Phase 11).
- EDF specification used a placeholder "budget 50 mm" EDF at 228 g thrust (incorrect),
  leading to T/W = 0.48 and an erroneous "cannot achieve VTOL" conclusion. The
  authoritative spec (XFly Galaxy X5 50 mm 3200 KV, 1,240 g per EDF) yields T/W = 1.61
  at Phase 5–10 AUW (2,768 g) — VTOL is achievable from Phase 5.
- Battery capacity recommendations (10,000 mAh / 8,000 mAh) were sized for the
  incorrect high-current budget EDF. The authoritative Kaylee board uses XT60 input
  (correct for XFly EDF peak ~165 A) with 6S 4,000 mAh (hover) or 2,800 mAh (cargo).
- Kaylee / PDB mass was listed as 80 g; the correct installed mass is 278 g
  (PCB assembly 158 g + shielded enclosure 120 g).
- Fuselage EDF listed as 40 mm 4S tap (incorrect); correct spec is 120 mm 6S, Phase 11 DNP.

The VTOL thrust analysis, ESC selection, and weight-and-balance content from this
document has been migrated (with corrected numbers) into `docs/POWER_DISTRIBUTION.md`
§§ 12–14.

---

## Documentation-process snapshots — Archived 2026-09-15

Four point-in-time documentation reports/hand-offs, all superseded by the living record in
`docs/WBS.md` §0.10 (the "Update and correct documentation" audit) and the Rev T checkpoint
(`docs/WBS.md` §6.4). Archived, not deleted, because each records what was true and what was
believed on its date; none should be read as current status. Archival pass performed by
Claude Opus 5 (Anthropic) under the author's direction; see `docs/WBS.md` §0.10.2 item 6.

### DOC_VERIFICATION_0.6.2.md — 2026-08-01, Claude Haiku 4.5

**Superseded by:** `docs/WBS.md` §0.10.2 (2026-08-22 pass and later).

Left "In Progress" with an action-item list; every item was either closed by the §0.10.2
pass (attribution doc, subsystem READMEs, licence split, JSX viewer, BOM sync, REFERENCES.md
duplicate IDs) or is tracked there as a named residual. The task number it uses ("0.6.2") was
itself renumbered to §0.10.2 on 2026-08-01.

### DOCUMENTATION_RECONCILIATION_2026-07-28.md — 2026-07-28, Claude Haiku 4.5

**Superseded by:** `docs/WBS.md` §0.10 and §6.4 (Rev T checkpoint, 2026-09-06).

A Rev S reconciliation report. Its own closing line — "Next audit: recommended after next
major revision (Rev T milestone)" — has fired. Its "Recommendations for Future Maintenance"
item 4 (regenerate `TODO.md` from `WBS.md`) was implemented 2026-09-15 as
`tools/gen_todo_from_wbs.py`.

### TODO_1_1_0_COMPLETION_SUMMARY.md — 2026-07-18

**Superseded by:** root `WBS.md` §1.1.0 and `airframe/WBS.md` §1.1.0.

A hand-off note asking the maintainer to tick two §1.1.0 checkboxes. Both are ticked; the
one item it left open ("Hull-frame placements for VERIFY parts") is still open in the owner.

### PYLON_INTEGRATION_2026-07-18.md — 2026-07-18

**Superseded by:** `docs/TILT_SPAR_ANALYSIS.md`, `docs/NOZZLE_DRIVE_TRADE.md`,
`docs/WING_ATTACH_INTERFACE.md` (the fixed 20 × 16.3 mm CF spar and trunnion pivot of
Rev S1g/S4).

Described a fixed 4 mm CF press-fit spar with a sector gear on a wing bracket; replaced
within a day of being written (its own banner said so from 2026-08-22). Retained as the
record of the geometry that `wings_s1223_revo.scad` Rev R1a was integrated against.
