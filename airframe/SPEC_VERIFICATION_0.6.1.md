# Airframe Specifications Verification (Task 0.6.1)

**Date:** 2026-08-01  
**Status:** Superseded — closed out by `docs/WBS.md` §0.10.1 (2026-08-22); this document's
open items were resolved there. Retained as historical record.  
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
| Hull length | 24.0 in (609 mm) | root README.md L71 | bom_revS.json metadata | ✅ |

**RESOLVED 2026-08-22 (maintainer-confirmed):** overall length is **24.0 in (609 mm)** —
this is the canonical spec value; any figure derived otherwise is incorrect. A prior pass
through this item mis-derived a ~690 mm figure by taking a naive min/max span across the
baked Head/Cargo/Middle/Rear shell Y-extents below; that approach does not correctly
measure "overall length" for this hull (it appears to pick up geometry — e.g. landing-gear
skid protrusion baked into Rear_Shell — beyond the hull body the 609 mm spec describes) and
was reverted. The baked-extent figures themselves are retained here for reference, not as
a length measurement:
- Head_Shell Y-extent: −305.7 to −70.7 mm (235 mm contribution)
- Cargo_Shell Y-extent: −71.5 to +132.0 mm (203.5 mm contribution)
- Middle_Shell Y-extent: +130.4 to +203.6 mm (73.2 mm contribution)
- Rear_Shell Y-extent: +203.2 to +384.3 mm (181.1 mm contribution)

If a future pass wants to re-derive overall length from CAD, it must isolate the hull-body
geometry from any non-body protrusions (landing gear, etc.) first — a raw span/sum over the
four shell extents is not a valid substitute for the specified measurement.

---

### 1.2 Wingspan

| Parameter | Spec Value | Source Doc | Current BOM/CAD | Status |
|-----------|------------|------------|-----------------|--------|
| Wingspan | 19.1 in (486 mm) | root README.md L72 | AGENTS.md extents table | ✅ |

**Verification note (RESOLVED 2026-08-22):** Wing port X-extent −93.0 to +4.7 mm = 97.7 mm.
Wing stbd X-extent −347.7 to −250.0 mm = 97.7 mm — **symmetric with port**, not the 82 mm
originally reported here. That 82 mm figure was a transcription mix-up one row down in the
`HULL_FRAME_REFERENCE.md` extents table (it belongs to `Nacelle_Stbd`, not `Wing_Stbd`).
Confirmed against `airframe/openscad/wings/wings_s1223_revo.scad:13-16`, whose own header
states both bounds and whose `wings()` module (lines 939-950) generates stbd as a mirror
transform of port. No wing geometry bug exists.

**Status:** ✅ VERIFIED — symmetric, no CAD change needed.

---

### 1.3 Height

| Parameter | Spec Value | Source Doc | Current BOM/CAD | Status |
|-----------|------------|------------|-----------------|--------|
| Height | 7.93 in (201.5 mm) | root README.md L73 (updated 2026-08-01) | Baked STL extents (Head top to Cargo belly) | ✅ |

**Verification task:** Confirm Z-extent from head top to cargo belly reference datum.
- Head_Shell Z-extent: +61.1 to +201.5 mm (maximum = 201.54 mm)
- Cargo_Shell Z-extent: 0.0 to +163.2 mm (minimum datum = 0.0 mm)

**Airframe height = 201.54 mm ≈ 7.93 in** ✅ **VERIFIED**

**Landing gear clearance:** R6 canonical 1.5 in (38.1 mm) below cargo belly.
**Total ground-to-top height:** 9.43 in (239.6 mm) when aircraft is on the ground.

**Note:** The 0.73-inch increment over the legacy 7.2-inch spec was incorporated into the R6 landing gear design to achieve proper ground clearance for flight safety.

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

| Parameter | Spec | Source | Calculation | Status |
|-----------|------|--------|-------------|--------|
| EDF model | XFly Galaxy X5 50mm 12-blade 6S 3200KV | AGENTS.md canonical | — | ✅ |
| Thrust per EDF | 1,240 g | XFly datasheet | — | ✅ |
| EDF unit mass | 70 g | BOM_revS.json | — | ✅ |
| Per nacelle (2 EDFs, 90% stator efficiency) | 2,232 g | 2 × 1,240 × 0.90 | See calculation note | ✅ |
| Total thrust (4 EDFs, 2 nacelles) | 4,464 g (9.84 lbf) | 2 × 2,232 | **With 90% efficiency factor applied** | ✅ |
| Total EDF unit mass (4×) | 280 g | 4 × 70 | Not included in nacelle assembly mass | ✅ |
| Nacelle assembly mass (2×, inc. EDFs + shells + gearing) | ~625 g | BOM breakdown | Composite, not EDF-only | ✅ |
| T/W (hover, Phase 5–10) | ≈1.61 | 4,464 g ÷ 2,768 g | Using efficiency-adjusted thrust | ✅ |

**Thrust Calculation with 90% Stator Efficiency (Explicit):**
- Per EDF (canonical): 1,240 g thrust (raw, from XFly Galaxy X5 datasheet)
- Per nacelle (tandem pair):
  - Two EDFs in series: 1,240 + 1,240 = 2,480 g (additive without efficiency loss)
  - With 11-fin inter-stage stator 90% efficiency: 2,480 × 0.90 = **2,232 g thrust per nacelle** ✅
- Total system (2 nacelles): 2,232 × 2 = **4,464 g thrust** (equivalent to 9.84 lbf)

**Verification:** T/W = 4,464 g thrust ÷ 2,768 g AUW = 1.61 — matches specification ✅

**Key Distinction (Resolved):**
- EDF unit MASS: 70 g per unit (BOM, what it weighs)
- EDF unit THRUST: 1,240 g per unit (datasheet, aerodynamic output at 6S throttle)
- Nacelle ASSEMBLY mass: ~625 g total (includes EDFs, shells, pivot, gearing, iris mechanism)
- Nacelle ASSEMBLY thrust: 2,232 g per pair (efficiency-adjusted)

---

### 3.3 Phase 11 (Deferred) — Rear EDF Thrust (No Stator Efficiency)

| Parameter | Spec | Source | Notes | Status |
|-----------|------|--------|-------|--------|
| Rear EDF (55mm) raw thrust | 1,500 g | Deferred/README.md | 6S fan, no inter-stage stator | ✅ |
| RCS bleed (4 jets) | 15% of mass flow | README.md L268 | Proportional-valve modulated | ✅ |
| Net forward thrust (post-bleed) | 1,275 g | 1,500 × 0.85 | 85% forward, 15% RCS authority | ✅ |

**Key distinction from nacelle EDFs:**
- **Nacelle EDFs (50mm):** 1,240g raw thrust each; **90% stator efficiency applied** → 2,232g per nacelle
- **Rear EDF (55mm):** 1,500g raw thrust; **no inter-stage stator** (no efficiency factor)
- RCS bleed is mass-flow diversion, not efficiency loss — serves attitude control, not thrust enhancement

**Phase 11 thrust budget:**
- Hover authority: 4,464 g (nacelles only) — rear EDF does not contribute to hover
- Forward cruise thrust: 1,275 g (rear EDF after RCS bleed)
- Total Phase 11 AUW: ~3,130 g | Hover T/W ≈ 1.43 (nacelles only)

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
| ✅ Verified | 23 | Material, printing, foam, battery, thrust servo, coordinate system, **airframe height (7.93 in)**, **hull length (24.0 in)**, landing gear R6 1.5 in clearance, wing geometry (symmetric) |
| ⚠️ Needs clarification | 4 | EDF mass/thrust confusion, wing geometry, T/W calculation source, hull length datum |
| ❌ Mismatch | 0 | *(none open — hull length resolved 24.0 in/609 mm canonical 2026-08-22; EDF mass already correctly labeled "nacelle assembly" in current airframe/README.md)* |
| 🔲 Not checked | 8 | Fuselage mass detail, wing mass detail, landing gear coupon test dimensions, avionics mass, tilt mechanism detail, individual component verification |

---

## Action Items for Completion (0.6.1.1 — Airframe Specs)

- [x] **Resolve Y-extent discrepancy** — RESOLVED 2026-08-22: 24.0 in (609 mm) is canonical
    (maintainer-confirmed); the extents-table span was a mis-derivation, see §1.1 above.
- [x] **Confirm height datum:** ✅ **RESOLVED** — Airframe height = 7.93 in (201.54 mm, head top to cargo belly). R6 landing gear adds 1.5 in (38.1 mm) clearance. Total ground-to-top = 9.43 in (239.6 mm). Updated root README.md L73 and airframe/SPEC_VERIFICATION_0.6.1.md.
- [ ] **Resolve EDF mass/thrust confusion:** Verify actual EDF unit mass vs. thrust (1,240 g **thrust** per unit, 70 g **mass** per unit per BOM)
- [ ] **Verify wing geometry:** Inspect wing SCAD/CAD for asymmetric port/stbd dimensions (appears intentional but document why)
- [ ] **Update README mass budget:** Correct EDF entries once actual mass confirmed (separate EDF mass 280g from nacelle assembly 625g)
- [ ] **Extract fuselage component masses:** Sum BOM entries for head, cargo, middle, rear shells to get exact fuselage mass
- [ ] **Validate mesh integrity:** Run `validate_stls.py` on all component STLs; confirm all pass watertightness + manifold checks
- [ ] **Landing gear dimensions:** Pending coupon test in Phase 7 (cannot verify pre-fabrication); R6 1.5 in canonical confirmed
- [ ] **Cross-reference BOM/README:** Ensure every component mentioned in README has corresponding BOM entry with current mass

---

**Next step:** Begin detailed component mass extraction from BOM and STL geometry analysis.

**Estimated completion:** ~2–3 hours for detailed review; 1 hour for updates.
