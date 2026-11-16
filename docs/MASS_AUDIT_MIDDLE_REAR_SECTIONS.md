# Mass Audit — Middle and Rear Sections, and the Joined One-Piece Baseline

**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Date:** 2026-10-31
**Tool:** `tools/aft_section_mass_audit.py` (reproduces every figure below)
**Method:** the same as `docs/MASS_AUDIT_CARGO_WING_ROOT.md`: measured watertight mesh,
station bands, cavity budget, and BOM-vs-mesh reconciliation.
**Feeds:** `docs/plans/2026-10-31-001-feat-one-piece-aft-sls-hull-plan.md`. This document is
its "before" picture. **No geometry has been changed.**
**AI note:** Measured and written by Claude Opus 5.5 (Anthropic) under the direction of
Steve Griffing (Stab-Rabbit-coding).

> **ENGINEERING REVIEW REQUIRED.** Every figure here must be reviewed and accepted by a
> qualified engineer before it is applied to any system carrying risk to life or safety.

Labels: **[MESH]** measured from the published STL. **[SRC]** a supplied datasheet.
**[REPO]** repo document or tool. **[CALC]** my arithmetic. **[ASSUMED]** needs verification.

## 0. Headline

1. **As-is joined part:** 420.5 g (0.93 lbm) in CF-PETG at the ledger density, against
   429.0 g for the three parts it replaces (middle, rear, collar at Y 509). Joining
   saves only **8.5 g**: the collar, less a bridge across the 2 mm gap [MESH, CALC].
2. **The same geometry in SLS PA CF** weighs **444.5 g**, which is **+15.5 g** against the
   ledger and **−78.5 g** against solid CF-PETG. Which of those is the right comparison
   still depends on weighing one printed shell (plan 001 gate G1) [SRC, CALC].
3. **The walls are already thin.** The mean wall is 2.16 mm in the middle and 2.15 mm in
   the rear. No band runs thicker than 3 mm (§2). The mass is skin area, not local
   thickening. The plan's ×0.5 and ×0.7 targets therefore have to come from **thinner
   skin plus ribs**, not from trimming bosses.
4. **The joint does not line up.** The two outer surfaces miss by about 4 mm in width and
   3 mm in height. The wall cut areas differ by 2×: 3,818 mm² on the middle side and
   1,819 mm² on the rear side. A one-piece part needs a **blended transition** rebuilt in
   the source, not a boolean union of the two STLs (§4).

## 1. Basis

| Quantity | Value | Source |
| --- | --- | --- |
| CF-PETG as-printed bulk density | 1.05 g/cc | `tools/auw_ledger.py` `RHO_PRINT` [REPO] |
| CF-PETG solid density | 1.28 g/cc | REF-MAT-002 [REPO] |
| DuraForm PA CF solid density | 1.11 g/cc (0.040 lbm/in³), ASTM D792 | 3DS-30108A [SRC] |
| Tilt pivot | Y 326.7, Z 146.9 mm | `tools/cg_relocation_study.py`, ledger [REPO] |
| Frame | aircraft datum R2, Y aft-positive, Z up | `AGENTS.md` |

All four meshes are watertight single bodies. The band sums equal the mesh volumes exactly.

## 2. Where the mass is

| Part | Volume | CF-PETG 1.05 | CF-PETG 1.28 | PA CF 1.11 | Centroid Y | Mean wall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Middle shell | 174,394 mm³ | 183.1 g | 223.2 g | 193.6 g | 473.2 | 2.16 mm |
| Rear shell | 220,456 mm³ | 231.5 g | 282.2 g | 244.7 g | 586.7 | 2.15 mm |
| Collar Y 509 | 13,739 mm³ | 14.4 g | 17.6 g | 15.2 g | 509.0 | 1.55 mm |
| Collar Y 436 (stays) | 15,048 mm³ | 15.8 g | 19.3 g | 16.7 g | 435.7 | 1.55 mm |

Moment about the pivot at 1.05 g/cc is 26,824 g·mm for the middle and **60,176 g·mm**
for the rear. Pitch inertia about the pivot is 15.4 lbm·in² for the middle and
**57.3 lbm·in²** for the rear [MESH].

### 2.1 Station bands (10 mm, CF-PETG bulk)

The middle runs from Y 436.7 to 508.0. Its heaviest bands are:

- **480–490: 35.8 g.** The cut has 7 loops and is 176 × 160 mm.
- **460–470: 31.6 g.** 1 loop, the open horseshoe.
- **450–460: 28.8 g.**

Ventral (below Z 163.7): 97.8 g. Dorsal: 85.4 g.

The rear runs from Y 510.0 to 690.0. It is fairly uniform at 12–17 g per band. The local
peaks are:

- **510–520: 20.4 g**, the joint land.
- **610–630: 31.0 g** over the two bands. This is the skid stanchion zone [ASSUMED].
- **590–600: 16 loops**, the ring-frame pocket at Y 595.7 [REPO `add_structural_features.py`].

Ventral (below Z 162.2): 129.5 g. Dorsal: 102.0 g. More than one loop from Y 520 aft is
the inner-neck tube [REPO].

The full band table is printed by the tool. Attributing a band to a feature is inference
from the loop count and the station: that is **[ASSUMED]** until it is checked against the
source build.

## 3. Cavity budget

Envelope = the convex hull of each 1 mm cut, integrated along Y. That is an upper bound:
the middle's open ventral horseshoe has no closed outer loop.

| Section | Envelope | Shell | Enclosed |
| --- | ---: | ---: | ---: |
| Middle | 1.448 L | 0.174 L | 1.273 L |
| Rear | 2.331 L | 0.220 L | 2.110 L |

## 4. Joined one-piece baseline (as-is walls)

| | CF-PETG 1.05 | CF-PETG 1.28 | PA CF 1.11 |
| --- | ---: | ---: | ---: |
| Joined part | 420.5 g | 512.6 g | 444.5 g |
| Three parts replaced | 429.0 g | 523.0 g | 453.5 g |
| Δ | −8.5 g | −10.4 g | −9.0 g |

- **Joined part:** centroid Y 536.2. Moment about the pivot is 88,079 g·mm at 1.05 g/cc
  and 93,112 g·mm in PA CF.
- **Size:** 253.3 × 176.9 × 164.8 mm (9.97 × 6.96 × 6.49 in). Fit to a vendor's SLS build
  envelope is not yet checked.
- **Bridge:** about 5,637 mm³, estimated as the mean wall cut times the 2 mm gap [CALC].
- **Joint mismatch:**
  - Outer section: 123 × 145 mm on the middle side, 127 × 142 mm on the rear side.
  - Wall cut: 3,818 mm² on the middle side (perimeter 506 mm), 1,819 mm² on the rear side
    (perimeter 1,090 mm, including the inner-neck loop).
  - Rebuild the blend in the owner's Blender/OpenSCAD sources (`AGENTS.md` rebuild rule),
    not by subtractive patches on the STLs.

## 5. BOM vs mesh reconciliation

| Row | BOM Rev T | Mesh (1.05) | Δ |
| --- | ---: | ---: | ---: |
| PRINT-MIDDLE-CANONICAL | 190.9 g | 183.1 g | −7.8 g |
| PRINT-REAR-NECK-INTAKE | 243.2 g | 231.5 g | −11.7 g |
| PRINT-MIDDLE-REAR-COLLAR | 16.0 g | 14.4 g | −1.6 g |

The ledger already uses the mesh values. `bom_revT.csv` is 21.1 g heavier than the mesh
for these three rows. Reconcile it when the joined part replaces them.

## 6. What this baseline does not cover

- Skid rods, ring-frame CF plate and fasteners. These are BOM items and do not change
  when the shells are joined.
- Allowables, stiffness and the drop case (plan 001 gate G2).
- Z-direction (build-axis) properties of PA CF. The datasheet gives no orientation
  breakdown [SRC].
