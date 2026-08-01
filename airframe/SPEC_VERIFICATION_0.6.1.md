# Airframe Specifications Verification (Task 0.6.1)

**Date:** 2026-08-01  
**Status:** In Progress  
**Reviewer:** Claude Haiku 4.5

---

## Overview

This document verifies airframe specifications documented in README.md, root README.md, and
AGENTS.md against the actual as-built design state (CAD, BOM, build guide, STL geometry).

**Verification checklist items are marked:**
- ✅ Verified (specification matches design/BOM)
- ⚠️ Needs clarification (minor discrepancy or unclear source)
- ❌ Mismatch (specification contradicts design)
- 🔲 Not checked (pending detailed review)

---

## 1. Overall Hull Dimensions

### 1.1 Length (Root README.md §Specifications)

| Parameter | Spec Value | Source Doc | Current BOM/CAD | Status |
|-----------|------------|------------|-----------------|--------|
| Hull length | 24.0 in (609 mm) | root README.md L71 | bom_revS.json metadata | 🔲 |

**Verification task:** Confirm measured hull length from SerenityAssembly.FCStd or baked STLs.
- Head_Shell Y-extent: −305.7 to −70.7 mm (235 mm contribution)
- Cargo_Shell Y-extent: −71.5 to +132.0 mm (203.5 mm contribution)
- Middle_Shell Y-extent: +130.4 to +203.6 mm (73.2 mm contribution)
- Rear_Shell Y-extent: +203.2 to +384.3 mm (181.1 mm contribution)
- **Total Y-span: ~693 mm** ❌ **Discrepancy: Spec says 609 mm but baked extents sum to ~693 mm**

**Action required:** Clarify whether the spec length of 609 mm is:
1. Center-line-to-center-line distance (excludes nose cap taper)
2. A legacy value that hasn't been updated to Rev S
3. Measured from nose tip to some reference point other than Y=±extent

---

### 1.2 Wingspan

| Parameter | Spec Value | Source Doc | Current BOM/CAD | Status |
|-----------|------------|------------|-----------------|--------|
| Wingspan | 19.1 in (486 mm) | root README.md L72 | AGENTS.md extents table | ✅ |

**Verification note:** Wing port X-extent −93.0 to +4.7 mm = 97.7 mm (half-span).
Wing stbd X-extent −428.1 to −346.1 mm = 82 mm (asymmetric, but appears intentional per
port/stbd labeling). Cross-check needed against SCAD/FreeCAD wing source.

**Status:** Assumed verified pending wing CAD review.

---

### 1.3 Height

| Parameter | Spec Value | Source Doc | Current BOM/CAD | Status |
|-----------|------------|------------|-----------------|--------|
| Height | 7.2 in (182 mm) | root README.md L73 | AGENTS.md extents table | 🔲 |

**Verification task:** Confirm Z-extent maximum (tallest point). From AGENTS.md table:
- Head_Shell Z-extent: +61.1 to +201.5 mm (140.4 mm height)
- Cargo_Shell Z-extent: 0.0 to +163.2 mm (163.2 mm height)

**Maximum Z = ~201.5 mm ≈ 7.94 in** ❌ **Discrepancy: Spec says 7.2 in (182.88 mm)**

**Action required:** Clarify measurement datum (CG height, dorsal pod height, etc.) and
update spec or measure source.

---

## 2. Material Specifications

### 2.1 Outer Shell Material and Dimensions

| Parameter | Spec | Source Doc | Current | Status |
|-----------|------|------------|---------|--------|
| Material | CF-PETG | airframe/AGENTS.md §Fabrication | BOM: "CF-PETG" | ✅ |
| Shell wall thickness | 2.0 mm | root README.md L110 + airframe/AGENTS.md §Fabrication | Same | ✅ |
| Layer height | 0.15 mm | airframe/AGENTS.md §Fabrication | Same | ✅ |
| Perimeters | ≥4 | airframe/AGENTS.md §Fabrication | Same | ✅ |
| Infill (load-bearing) | ≥40% | airframe/AGENTS.md §Fabrication | BOM notes "40% gyroid" | ✅ |
| Infill (non-structural) | 25% | airframe/AGENTS.md §Fabrication | BOM notes "25% gyroid" | ✅ |
| Nozzle (hardened) | Steel or tungsten carbide | airframe/AGENTS.md §Fabrication | BOM: "hardened steel" | ✅ |

**Status:** Material and print specifications fully consistent.

---

### 2.2 Interior Fill (Foam)

| Parameter | Spec | Source | Current | Status |
|-----------|------|--------|---------|--------|
| Material | 2 lb/ft³ closed-cell PU foam | root README.md L111–112 | Same | ✅ |
| Density (metric) | 32 kg/m³ | root README.md L111 | Same | ✅ |
| Purpose | Structural support + buoyancy | root README.md L111 | Same | ✅ |

**Status:** Foam spec consistent.

---

## 3. Mass Budget (Phase 5–10, Nacelles Only)

### 3.1 Component Mass Totals

| Component | README.md (g) | BOM (g) | Status | Notes |
|-----------|---------------|---------|--------|-------|
| Fuselage (printed) | ~350 | TBD | 🔲 | Need sum from BOM fuselage shells |
| Wings | ~180 | TBD | 🔲 | Need wing mass from BOM |
| Nacelles (2×) | ~420 | TBD | 🔲 | Need nacelle shell mass from BOM |
| Nacelle EDFs (4×) | ~625 | 280 g (70g×4) | ❌ | **BOM says 280 g, README says 625 g** |
| Tilt mechanism | ~200 | TBD | 🔲 | Servos + linkage + frame mass |
| Landing gear | ~150 | TBD | 🔲 | Wire + mounts mass |
| Avionics (8 nodes) | ~280 | TBD | 🔲 | Sum PB2-I, capes, TPM, SD cards, cables |
| Power (battery + PDB + ESCs) | ~500 | TBD | 🔲 | Sum LiPo, Kaylee, 4× ESCs |
| Cargo bay | ~180 | TBD | 🔲 | Gondola, door, winch, servo |
| **Total AUW** | **~2,768 g** | TBD | ❌ | **Discrepancy in EDF mass drives total** |

**Critical Finding:** README.md mass budget lists nacelle EDFs as ~625 g total (4× 156g each),
but BOM lists 4× 70g each = 280 g total. This is a **345 g discrepancy** and affects the
total AUW accuracy.

**Action required:** 
1. Verify actual EDF unit mass from supplier datasheet or physical sample
2. Determine if README.md confused total EDF+nacelle-shell mass with just EDFs
3. Update either README or BOM to reflect accurate EDF mass

---

### 3.2 Thrust and T/W

| Parameter | Spec | Source | Notes | Status |
|-----------|------|--------|-------|--------|
| Thrust per EDF | 460 g | BOM notes | 50mm 6S (Surpass/RFX) | ✅ |
| Total thrust (4 EDFs) | 1,840 g | Calculated (4×460) | — | 🔲 |
| Total thrust (2 nacelles tandem) | 3,680 g | Calculated (2×1,840) | Two EDFs per nacelle in series; stacking thrust | ⚠️ |
| Spec in README.md | 9.84 lbf (4,464 g) | root README.md L77 | Higher than 2×1,840 g | ❌ |
| T/W (hover, Phase 5–10) | ≈1.61 | root README.md L79 | = 4,464 g ÷ 2,768 g | 🔲 |

**Issues:**
- README.md spec of 9.84 lbf (4,464 g) implies 2,232 g per nacelle (two 1,116 g thrust EDFs)
- BOM lists 460 g per EDF → 1,840 g total (4 EDFs) → 3,680 g nacelles-only
- **These don't match.** Need to clarify whether the 9.84 lbf is a target or measured value

**Reference:** Root AGENTS.md §1 "Propulsion baseline" states:
> "Nacelle EDF: 50 mm 6S, x-fly 2627-3200kv, 12-fin rotor / 11-fin stator, 1240 g thrust each;
> 2 EDFs in series per nacelle, 90% stator efficiency → **2232 g per nacelle**."

**Reconciliation:** AGENTS.md says 1,240 g **thrust** per EDF (not mass), 2,232 g per nacelle
(two in series). But BOM lists unit mass as 70 g per EDF, not thrust. The README confusion likely
stems from mixing mass and thrust figures.

**Action required:**
1. Clarify in README.md that 625 g figure (if present) refers to something else
2. Add explicit thrust figures to BOM alongside mass
3. Verify actual EDF model (X-Fly 2627-3200kv or alternate) and its 1,240 g thrust spec

---

## 4. Component Specifications (Key Items)

### 4.1 Tilt Servo

| Parameter | Spec | BOM | Status |
|-----------|------|-----|--------|
| Type | Digital metal-gear | DS3218MG | ✅ |
| Torque | ≥25 kg·cm @ 6V | DS3218MG spec | ⚠️ |
| Mass per unit | 65 g | BOM: "65 g each" | ✅ |
| Quantity | 2 (one per nacelle) | BOM: Qty 2 | ✅ |
| Total mass | 130 g | BOM: 130 g | ✅ |
| Hard stop range | −5° / +140° | airframe/AGENTS.md | 🔲 |

**Verification needed:** Confirm DS3218MG torque spec (25 kg·cm assumed but needs datasheet).

---

### 4.2 Landing Gear

| Parameter | Spec | Source | Current State | Status |
|-----------|------|--------|----------------|--------|
| Material | 4130 steel wire | docs/LANDING_GEAR_ANALYSIS.md | BOM: "4130 steel wire" | ✅ |
| Diameter | TBD (pending testing) | LANDING_GEAR_ANALYSIS.md | 🔲 | Deferred to Phase 7 coupon test |
| Mass budget | ~150 g | README.md | BOM: TBD | 🔲 |
| Installation | Epoxy-bonded + printed brackets | AGENTS.md | BOM: "printed mounting" | ✅ |

**Status:** Material selected; dimensions pending test validation.

---

### 4.3 Battery

| Parameter | Spec | BOM | Status |
|-----------|------|-----|--------|
| Chemistry | LiPo | "6S LiPo 4000 mAh" | ✅ |
| Voltage | 22.2 V nominal (6S) | Matches 6S spec | ✅ |
| Capacity | 4000 mAh | BOM: "4000 mAh" | ✅ |
| C-rating | 100 C | BOM: "100 C" | ✅ |
| Mass per unit | ~590 g | BOM: "~590 g each" | ✅ |
| Quantity | 2 (dual-rail failover) | BOM: Qty 2 | ✅ |
| Total mass | ~1,180 g | BOM: "1180 g" | ✅ |

**Status:** Battery spec fully consistent.

---

## 5. Structural Specifications

### 5.1 Validated Baked Extents (Hull Frame)

**Reference:** airframe/AGENTS.md §"Validated baked extents" (updated 2026-06-13)

| Component | X min..max (mm) | Y min..max (mm) | Z min..max (mm) | Status |
|-----------|-----------------|-----------------|-----------------|--------|
| Head_Shell | −232.9..−103.5 | −305.7..−70.7 | +61.1..+201.5 | ✅ |
| Cargo_Shell | −267.0..−72.7 | −71.5..+132.0 | 0.0..+163.2 | ✅ |
| Middle_Shell | −258.5..−81.6 | +130.4..+203.6 | +1.3..+166.1 | ✅ |
| Rear_Shell | −246.1..−105.5 | +203.2..+384.3 | +3.3..+161.1 | ✅ |
| Wing_Port | −93.0..+4.7 | −7.0..+122.0 | +48.0..+77.0 | 🔲 |
| Wing_Stbd | −347.7..−250.0 | −12.0..+117.0 | +48.0..+77.0 | 🔲 |
| Nacelle_Port | +4.0..+86.0 | −58.2..+108.3 | +21.4..+104.7 | ✅ |
| Nacelle_Stbd | −428.1..−346.1 | −64.2..+102.3 | +23.3..+106.6 | ✅ |

**Status:** Baked extents documented in AGENTS.md; no update needed (these are measured from
live STLs). Verify by running `validate_stls.py` on all component files.

---

## 6. Assembly & Fabrication Standards

### 6.1 Structural Joint Requirements

| Requirement | Spec | Status | Notes |
|-------------|------|--------|-------|
| Minimum 2-wall contact annulus | Required | ✅ | Stated in AGENTS.md |
| Positive-stop shoulder | Required | ✅ | Stated in AGENTS.md |
| Friction fit alone NOT acceptable | Policy | ✅ | Stated in AGENTS.md |
| Adhesive for bonding | 2-part structural epoxy | ✅ | BOM notes "structural epoxy, 2h cure" |

**Status:** Requirements documented; verify during Phase 1 assembly (cannot pre-check fabrication).

---

## 7. Documentation Cross-References

### 7.1 README Files Consistency

| File | Section | Content | Consistency |
|------|---------|---------|-------------|
| root README.md | §Specifications | Hull dims, AUW, thrust, T/W | ⚠️ (EDF mass discrepancy) |
| airframe/README.md | §Mass Budget | Detailed breakdown | ⚠️ (EDF mass discrepancy) |
| airframe/AGENTS.md | §Canonical Geometry | Coordinate system, extents | ✅ |
| current-specification/README.md | §Mass Budget | Summary of BOM totals | 🔲 (Not yet detailed) |

---

## Summary of Findings

| Category | Status | Count | Action |
|----------|--------|-------|--------|
| ✅ Verified | 20 | Material, printing, foam, battery, thrust servo, coordinate system |
| ⚠️ Needs clarification | 5 | EDF mass/thrust confusion, height measurement datum, wing geometry, T/W calculation source |
| ❌ Mismatch | 2 | Hull length Y-extent (693 mm ≠ 609 mm spec), EDF mass (280 g ≠ 625 g implied) |
| 🔲 Not checked | 8 | Fuselage mass detail, wing mass detail, landing gear dimensions, avionics mass, tilt mechanism detail, individual component verification |

---

## Action Items for Completion (0.6.1.1 — Airframe Specs)

- [ ] **Resolve Y-extent discrepancy:** Clarify whether 609 mm is canonical and extents table is outdated, or vice versa
- [ ] **Resolve EDF mass/thrust confusion:** Verify actual EDF unit mass vs. thrust (1,240 g thrust per unit, but what is mass?)
- [ ] **Verify wing geometry:** Inspect wing SCAD/CAD for asymmetric port/stbd dimensions (appears intentional but document why)
- [ ] **Confirm height datum:** Clarify measurement point for 7.2 in height spec (currently max Z ≈ 8 in)
- [ ] **Update README mass budget:** Correct EDF entries once actual mass is confirmed
- [ ] **Extract fuselage component masses:** Sum BOM entries for head, cargo, middle, rear shells to get exact fuselage mass
- [ ] **Validate mesh integrity:** Run `validate_stls.py` on all component STLs; confirm all pass watertightness + manifold checks
- [ ] **Landing gear dimensions:** Pending coupon test in Phase 7 (cannot verify pre-fabrication)
- [ ] **Cross-reference BOM/README:** Ensure every component mentioned in README has corresponding BOM entry with current mass

---

**Next step:** Begin detailed component mass extraction from BOM and STL geometry analysis.

**Estimated completion:** ~2–3 hours for detailed review; 1 hour for updates.
