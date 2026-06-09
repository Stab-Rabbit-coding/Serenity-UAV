# Superseded Design Documents

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0

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
