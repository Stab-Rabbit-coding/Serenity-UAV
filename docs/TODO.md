# Serenity UAV — Documentation, Standards & Regulatory TODO (Open Work Only)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0

> **This file lists only currently-open (unchecked) top-level tasks for
> this subsystem — one line each, <=70 chars, no prose.** Full detail
> (notes, rationale, nested sub-steps, done items) lives in
> [`WBS.md`](WBS.md), the full historical record for project-progression
> tracking. Close an item in `WBS.md` first, then delete its line here.

*"A special hell. — Shepherd Book"*

---

## §0.5 — Citation Completeness Audit (All Source Files)
→ full detail: `WBS.md` §0.5

- [ ] `build_guide_18_first_flight.svg`'s Part 107/VLOS warning callouts…
- [ ] Seven additional SVGs (`build_guide_09_avionics.svg`…
- [ ] The remaining ~30 non-priority SVGs were not individually swept for…

## §0.8 — Tilt-Spar Material Allowables + Hall Encoder Verification
→ full detail: `WBS.md` §0.8

- [ ] Verify `REF-STD-GEAR-001` (ISO 53:1998) to clause level
- [ ] Verify spar material allowables vs MMPDS-2023 / AMS
- [ ] Add the 4130 corrosion-finish spec
- [ ] Verify the AK7455 off-axis geometry on the bench

## §0.9 — Licensing Updates
→ full detail: `WBS.md` §0.9

- [ ] Submit OSHW self-certification (root `TODO.md` §5.4)

#### 4. WBS and TODO files
→ full detail: `WBS.md` 4. WBS and TODO files

- [ ] Renumber `airframe/wings-nacelles/WBS.md` §1.1.4/§1.1.5 →…
- [ ] Wire `tools/gen_todo_from_wbs.py --check` into the pre-commit hook /…

#### 6. Superseded documents archived (2026-09-15)
→ full detail: `WBS.md` 6. Superseded documents archived (2026-09-15)

- [ ] Rewrite `docs/AVIONICS_PB2_REDESIGN.md` as a Rev T architecture…

## §1.5 — Documentation
→ full detail: `WBS.md` §1.5

- [ ] Update PHASED_BUILD_GUIDE.md from Rev M 18-inch to Rev S 24-inch…
- [ ] Rebuild `graphical-build-guide/` (38 SVGs) from…
- [ ] Sync `bom_revO.json` ↔ `bom_revO.csv` — verify all XCVR-49MHZ-1 BOM…
- [ ] Rewrite build-guide Phase 2/3 steps for the Rev T mechanism (added…

## §5.1 — FCC (external radio systems)
→ full detail: `WBS.md` §5.1

- [ ] XCVR-49MHZ-1/2 FCC Part 15 §15.235 compliance

## §5.2 — FAA (airworthiness and operations) &#9733;
→ full detail: `WBS.md` §5.2

- [ ] Aircraft registration — register under 14 CFR Part 48 (sUAS, AUW <55…
- [ ] Remote Pilot Certificate — verify FAA Part 107 Remote Pilot…
- [ ] Navigation lights compliance — verify 6-position WS2812C nav light…
- [ ] sUAS data plate — attach to airframe: operator name, contact info…
- [ ] Pre-flight area check — LAANC authorization for any Class B/C/D/E…
- [ ] Airspace waiver (if applicable) — if operating above 400ft AGL or in…

## §5.3 — Industry Standards Compliance
→ full detail: `WBS.md` §5.3

- [ ] Structural validation — wing spar, keel, pivot rod, and tilt servo…
- [ ] IEEE/ISA/AUVSI best practices — validate all design decisions…
- [ ] Tamper-evident logging — verify CPLD write-blocker (ATF16V8BQL) on…

## §6.1 — Branch Reconciliation / Pre-Flight Compliance &#9733;
→ full detail: `WBS.md` §6.1

- [ ] Delete stale feature branches on GitHub after confirming this…

---
