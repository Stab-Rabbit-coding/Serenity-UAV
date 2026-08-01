# Documentation Verification (Task 0.6.2)

**Date:** 2026-08-01  
**Status:** In Progress  
**Reviewer:** Claude Haiku 4.5

---

## Overview

This document verifies documentation structure, consistency, and completeness across the
Serenity UAV project per task 0.6.2 (Documentation subsection of 0.6 — Update and correct
documentation touching every non-archived file).

**Task 0.6.2 items:**
- [ ] 0.6.2.1 Verify and update all compliance and licensing documents
- [ ] 0.6.2.2 Verify and update all README files (root + subsystem)
- [ ] 0.6.2.3 Verify and update system specification files and BOM
- [ ] 0.6.2.4 Verify and update WBS and TODO files
- [ ] 0.6.2.5 Verify and update REFERENCES.md file

---

## 0.6.2.1 Compliance & Licensing Documents

### 1.1 License Files Inventory

| File | Location | Type | Last Updated | Status |
|------|----------|------|--------------|--------|
| `LICENSE` | root | CC BY 4.0 text | 2026-08-01 | 🔲 |
| `current-specification/LICENSE_AND_ATTRIBUTION.md` | subsystem | Narrative + CC BY 4.0 | 2026-06-16 | ⚠️ |
| `docs/attribution_and_licensing.md` | docs/ | Referenced in AGENTS.md | **MISSING** | ❌ |
| `LICENSES/` directory | root | License variants | Exists | 🔲 |

### 1.2 Missing Compliance Documents (Per AGENTS.md §0.9)

Per root AGENTS.md §0.9 (licensing updates), the following are **not yet created**:
- [ ] Subsystem-level LICENSE files (one per folder: airframe/, avionics/, gcs/, tools/)
- [ ] docs/attribution_and_licensing.md (root comprehensive licensing document, referenced in multiple files)
- [ ] OSHW certification files (associated with §0.9 licensing task, separate from 0.6.2)

### 1.3 License Coverage Review

**Current state:** Project uses **CC BY 4.0** for all software/docs per root LICENSE file.

**Task 0.9 (Licensing Updates)** specifies split licensing model:
- **Hardware (PCBs, STLs, CAD):** CERN-OHL-W 2.0
- **Firmware/Scripts:** CC BY 4.0
- **Documentation:** CC BY 4.0

**Status:** ⚠️ **License split (0.9) not yet implemented in 0.6.2 scope — this is deferred to §0.9 but affects doc verification**

**Action for 0.6.2:**
- Create `docs/attribution_and_licensing.md` documenting the intended split (CERN-OHL-W vs. CC BY 4.0)
- Add subsystem-level LICENSE files as placeholders pointing to root LICENSE + attribution doc
- Update current-specification/LICENSE_AND_ATTRIBUTION.md timestamp and scope note

---

## 0.6.2.2 README Files — All Levels

### 2.1 Root & Top-Level READMEs

| File | Location | Created/Updated | Scope | Status |
|------|----------|-----------------|-------|--------|
| `README.md` | root | 2026-08-01 | Project overview, architecture, mission | ✅ |
| `docs/README.md` | docs/ | 2026-08-01 | Documentation index, design docs | ✅ |
| `AGENTS.md` | root | 2026-07-18 | Project policy (model-agnostic) | ✅ |

**Status:** Root documentation index updated and consistent.

### 2.2 Subsystem READMEs (Created in Task 0.6 Initial Phase)

| Subsystem | File | Created | Status | Coverage |
|-----------|------|---------|--------|----------|
| Airframe | `airframe/README.md` | 2026-08-01 | ✅ | Hull frame, printing specs, mass budget, assembly |
| Avionics | `avionics/README.md` | 2026-08-01 | ✅ | 8-node architecture, PCBs, firmware, comms |
| GCS | `gcs/README.md` | 2026-08-01 | ✅ | Malcolm hardware, 5-radio comms, gimbal |
| Current Spec | `current-specification/README.md` | 2026-08-01 | ✅ | BOM structure, parts organization, revision tracking |
| Tools | `tools/README.md` | 2026-08-01 | ✅ | Validation scripts, CI pipeline, design automation |
| Graphical Guide | `graphical-build-guide/README.md` | **MISSING** | ❌ | Build guide phases, SVG organization |
| Deferred | `deferred/README.md` | **MISSING** | ❌ | Phase 11+ work, aft EDF, RCS thrusters |

**Status:** ⚠️ **5 of 7 subsystem READMEs created; 2 missing (graphical-build-guide, deferred)**

### 2.3 Subsystem AGENTS.md Files (Policy Documents)

| Subsystem | File | Status | Last Updated |
|-----------|------|--------|--------------|
| Root | `AGENTS.md` | ✅ | 2026-07-18 |
| Airframe | `airframe/AGENTS.md` | ✅ | 2026-07-27 |
| Avionics | `avionics/AGENTS.md` | ✅ | 2026-07-27 |
| Current Spec | `current-specification/AGENTS.md` | ✅ | 2026-07-27 |
| Deferred | `deferred/AGENTS.md` | ✅ | 2026-07-27 |
| Docs | `docs/AGENTS.md` | ✅ | 2026-07-27 |
| GCS | `gcs/AGENTS.md` | ✅ | 2026-07-27 |
| Graphical Build | `graphical-build-guide/AGENTS.md` | ✅ | 2026-07-27 |
| Tools | `tools/AGENTS.md` | ✅ | 2026-07-27 |

**Status:** ✅ **All subsystem AGENTS.md files present and current (Rev S baseline)**

---

## 0.6.2.3 System Specification & BOM Files

### 3.1 BOM Files

| File | Format | Purpose | Status | Issues |
|------|--------|---------|--------|--------|
| `current-specification/bom_revS.json` | JSON | Structured BOM (primary source) | ✅ | EDF mass discrepancy (see airframe verification) |
| `current-specification/bom_revS.csv` | CSV | Flat-file BOM (spreadsheet import) | 🔲 | Needs sync with JSON (last touched 2026-07-27) |
| `current-specification/serenity-rev-r.jsx` | JSX | Interactive BOM viewer | ✅ | Filename says "rev-r" but should it be "rev-s"? |
| `current-specification/serenity-rev-s.jsx` | JSX | Rev S BOM viewer | ✅ | Newer version; check if both are needed |

**Issues:**
- ⚠️ Two JSX viewers (rev-r and rev-s) — clarify which is canonical
- 🔲 CSV may be out of sync with JSON (need to verify with `update_bom.py`)

### 3.2 Specification Documents (Cross-Referenced)

| Document | Location | Scope | Status | Last Updated |
|----------|----------|-------|--------|--------------|
| `PHASED_BUILD_GUIDE.md` | docs/ | **MISSING** | ❌ | Spec says Rev M 18" (obsolete) |
| `REVN_BUILD_GUIDE_24IN.md` | docs/ | **MISSING** | ❌ | Referenced in README, doesn't exist |
| `TILT_SPAR_ANALYSIS.md` | docs/ | Material trade study | ✅ | 2026-07-19 |
| `NOZZLE_DRIVE_TRADE.md` | docs/ | Nacelle nozzle mechanism | ✅ | 2026-07-19 |
| `LANDING_GEAR_ANALYSIS.md` | docs/ | Landing gear design | ✅ | 2026-06-XX (date unclear) |
| `JAYNE_LASER_ANALYSIS.md` | docs/ | Laser indicator specs | ✅ | Date unclear |

**Status:** ⚠️ **Two critical build guides missing (PHASED_BUILD_GUIDE.md, REVN_BUILD_GUIDE_24IN.md)**

---

## 0.6.2.4 WBS & TODO File Consistency

### 4.1 WBS File Structure

| File | Location | Type | Status | Items | Last Updated |
|------|----------|------|--------|-------|--------------|
| `WBS.md` | root | Master index + open-item checklist | ✅ | ~200 | 2026-08-01 |
| `TODO.md` | root | Open items only (≤70 chars each) | ✅ | ~100 | 2026-07-31 |
| `docs/WBS.md` | docs/ | Documentation WBS detail | ✅ | Full narrative | 2026-08-01 |
| `airframe/WBS.md` | airframe/ | Airframe WBS detail | ✅ | Full narrative | 2026-08-01 |
| `avionics/WBS.md` | avionics/ | Avionics WBS detail | ✅ | Full narrative | 2026-07-27 |

**Status:** ✅ **WBS/TODO structure consistent; sections 0.6 properly aligned after task 0.6 initial phase**

### 4.2 WBS/TODO Sync Verification

**Federation rule (AGENTS.md §10):** Every open item in TODO.md must have corresponding detail in `WBS.md`.

**Sample check — section 0.6:**
- ROOT `TODO.md` §0.6 references `docs/WBS.md` §0.6 ✅
- ROOT `WBS.md` §0.6 references `docs/WBS.md` §0.6 ✅
- ROOT `TODO.md` §0.6.1 references `docs/WBS.md` §0.6.1 ✅
- ROOT `WBS.md` §0.6.1 references `docs/WBS.md` §0.6.1 ✅

**Status:** ✅ **Section 0.6 fully aligned after corrections made in task 0.6 initial phase**

### 4.3 Subsystem TODO File Status

| Subsystem | TODO.md | Last Updated | Status |
|-----------|---------|--------------|--------|
| airframe | ✅ | 2026-07-27 | Current |
| avionics | ✅ | 2026-07-31 | Current |
| docs | ✅ | 2026-07-27 | Current |
| gcs | ✅ | 2026-07-27 | Current |
| tools | ❌ | N/A | Not applicable (reference-index only) |
| current-specification | ❌ | N/A | Not applicable (reference-index only) |
| graphical-build-guide | ✅ | 2026-07-27 | Current |
| deferred | ✅ | 2026-07-27 | Current |

**Status:** ✅ **Subsystem TODO files present and current (where applicable)**

---

## 0.6.2.5 REFERENCES.md Verification

### 5.1 REFERENCES.md Structure & Status

| Section | Count | Status | Issues |
|---------|-------|--------|--------|
| **Regulatory** | 15+ | ✅ | Current (FAA, FCC, NIST, DoD, etc.) |
| **Standards** | 20+ | ✅ | Current (ISO, IEC, IEEE, ISA, AUVSI, ASTM) |
| **Design & CAD** | 5 | ✅ | Current (QMx blueprints, Nick Henning, misubisu) |
| **Suppliers & Components** | 30+ | 🔲 | Needs verification (URLs may be stale) |
| **Removed / Superseded** | 3 | ✅ | NIST 800-72, Part 95 RCRS (superseded by Part 15) |
| **Open Standards Verification** | 5+ | 🔲 | Some marked "requires verification" |

**Total entries:** ~80+ citations

### 5.2 Citation Completeness Audit (Per §0.5 — Citation Completeness Audit)

**Status:** Partial. §0.5 ("Citation Completeness Audit") is marked complete in root WBS.md, but:

- ✅ **Code-identifier renames:** RCRS → XCVR-49MHZ completed (§0.1)
- ⚠️ **Build guide diagrams:** 7 SVGs still have stale Cape-A-1/B-1 hardware depictions (noted in §0.5)
- 🔲 **Supplier links:** ~30 non-priority SVGs unchecked for citation format
- 🔲 **Firmware docstrings:** Individual module citations not yet audited

### 5.3 "Requires Verification" Entries

Per root AGENTS.md §4, any citation that cannot be verified immediately is marked "requires verification" in REFERENCES.md and a `TODO.md §0.x` item is added.

**Current "requires verification" items:**
1. MMPDS-2023 material allowables (4130, 17-4 PH, 7075-T6) — **Task 0.8** (Tilt-Spar)
2. MT6701 encoder off-axis geometry + pinout — **Task 0.8** (Hall Encoder)
3. AK7455 magnetoresistive encoder specs — **Task 0.8**

**Status:** 🔲 **Items tracked in §0.8; will be resolved during material/sensor verification**

### 5.4 URL Validation Status

**Spot check (sample of 5 citations):**
- [REF-FAA-001] 14 CFR Part 48 ✅ (ecfr.gov link valid)
- [REF-FCC-003] 47 CFR §15.235 ✅ (ecfr.gov link valid)
- [REF-CAD-003] QMx Blueprints ✅ (physical ref, not URL)
- [REF-AUVSI-001] (URL pending verification)
- [REF-IEEE-001] IEEE 802.15.4 (vendor site, may rotate)

**Status:** 🔲 **Sample URLs spot-checked; full audit pending**

---

## Summary of Findings

| Category | Status | Count | Action |
|----------|--------|-------|--------|
| ✅ Verified & Current | 15 | AGENTS.md files, WBS/TODO structure, root/subsystem READMEs, design analyses |
| ⚠️ Needs Update | 8 | BOM CSV sync, current-specification/LICENSE_AND_ATTRIBUTION.md timestamp, missing build guides, JSX viewer naming |
| ❌ Missing | 4 | docs/attribution_and_licensing.md, graphical-build-guide/README.md, deferred/README.md, PHASED_BUILD_GUIDE.md |
| 🔲 Pending Detailed Review | 5 | URL validation (REFERENCES.md), supplier link verification, Rev M docs deprecation, BOM/README mass discrepancy fallout |

---

## Action Items for Task 0.6.2 Completion

### 0.6.2.1 — Compliance & Licensing

- [ ] Create `docs/attribution_and_licensing.md` (comprehensive root licensing document)
- [ ] Add subsystem LICENSE files (airframe/LICENSE, avionics/LICENSE, gcs/LICENSE, tools/LICENSE)
  - Each references root LICENSE + docs/attribution_and_licensing.md
  - Clarify hardware vs. software licensing split (defer CERN-OHL-W to task 0.9)
- [ ] Update `current-specification/LICENSE_AND_ATTRIBUTION.md` timestamp and scope note

### 0.6.2.2 — README Files

- [ ] Create `graphical-build-guide/README.md` (SVG build guide organization, phase overview)
- [ ] Create `deferred/README.md` (Phase 11+ work, aft EDF, RCS, future upgrades)
- [ ] Create `docs/PHASED_BUILD_GUIDE.md` (if legacy Rev M doc should be archived) OR
  - Update docs/README.md to clarify Phase 0–10 guidance lives in graphical-build-guide/ + WBS
- [ ] Verify root README.md references are current (spot-check 5+ links to subsystem docs)
- [ ] Verify all subsystem READMEs include:
  - ✅ Project scope statement
  - ✅ License declaration (CC BY 4.0 or CERN-OHL-W placeholder)
  - ✅ Attribution to Steve Griffing + AI contributors
  - ✅ Links to AGENTS.md, REFERENCES.md, relevant analysis docs

### 0.6.2.3 — System Specs & BOM

- [ ] Sync `bom_revS.csv` ← → `bom_revS.json` using `tools/update_bom.py`
- [ ] Clarify JSX viewers: retain `serenity-rev-s.jsx` (canonical), archive or deprecate `serenity-rev-r.jsx`
- [ ] Verify BOM component counts and mass totals match README.md specs (resolve EDF mass discrepancy from 0.6.1)
- [ ] Regenerate README.md §Specifications table if BOM totals change

### 0.6.2.4 — WBS & TODO File Sync

- [ ] Audit subsystem TODO files for stale items (spot-check airframe, avionics, docs)
- [ ] Verify root TODO.md item counts match subsystem TODO files (federation sanity check)
- [ ] Run TODo regeneration script (if exists) to ensure TODO.md is derived from WBS.md
- [ ] Mark completed items in subsystem WBS files (they should show [x] and stay in WBS for history)

### 0.6.2.5 — REFERENCES.md

- [ ] Full URL validation pass on all 80+ citations
  - Focus on supplier links (URLs rotate; validate before commit)
  - Check regulatory document links (ecfr.gov, FCC, FAA)
  - Verify archived design references (CAD, Nick Henning, misubisu)
- [ ] Audit docstring citations in firmware/SCAD files:
  - Run `grep -r "\[REF-" avionics/firmware/ airframe/stls/ gcs/firmware/`
  - Verify every `[REF-ID]` has corresponding REFERENCES.md entry
- [ ] Consolidate superseded citations section (Part 95 RCRS → Part 15 §15.235 cleanup done in §0.1)
- [ ] Update timestamp: `Last verified: 2026-08-01`

---

## Interdependencies & Ordering

**Recommended completion sequence:**

1. **Phase 1 (Docs structure):** Create missing README files + attribution doc (1–2 hours)
2. **Phase 2 (BOM/Specs):** Sync BOM files, resolve mass discrepancy from 0.6.1 airframe verification (1 hour)
3. **Phase 3 (WBS/TODO):** Audit subsystem files for staleness, regenerate TODO from WBS (1 hour)
4. **Phase 4 (References):** URL validation pass, docstring citation audit (2–3 hours)
5. **Phase 5 (Final sync):** Cross-verify all interconnections, commit batch (1 hour)

**Estimated total:** 6–8 hours for thorough completion.

---

**Next step:** Begin with missing README files (graphical-build-guide, deferred) and attribution document.
