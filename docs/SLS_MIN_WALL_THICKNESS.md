# SLS minimum wall thickness, DuraForm PA CF (replaces the 0.079 in FDM rule)

**Revision:** Rev U, 2026-11-11. **Status:** proposed; owner decision required (OD-19 below).
**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (owner) — analysis by Claude (Anthropic,
Claude Opus 5.5) under the author's direction, with the `mechanical-engineering` skill.
**License:** CC BY-SA 4.0 — see LICENSES/CC-BY-SA-4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Tool:** `tools/sls_min_wall.py` (re-runs every number below; change its declared inputs there).

> [!WARNING]
> **ENGINEERING REVIEW REQUIRED — this output is not a substitute for a qualified engineer.** Every
> result, calculation, and recommendation produced with this skill **must be independently reviewed
> and accepted by a properly qualified individual** — a licensed Professional Engineer or an
> equivalently qualified authority for the jurisdiction and discipline — **before it is applied to
> any system carrying risk to life or safety.**

> [!CAUTION]
> **This skill informs engineering judgment; it does not replace it.** Applying unreviewed results
> to real equipment or hardware — even where no life-safety risk exists — carries a risk of
> equipment damage or property loss. It is reference material provided AS-IS (see LICENSE §5), is
> not an engineering service, and does not constitute a sealed, certified, or reviewed work product
> for any specific project.

## Why the old rule does not carry over

`AGENTS.md` §7's 0.079 in (2.0 mm) exterior-shell wall was set for FDM CF-PETG (flexural modulus
6,670 MPa, REF-MAT-002). The flight article is SLS DuraForm PA CF (REF-MAT-015), which has a
different modulus, a 0.039 in (1.0 mm) process minimum (REF-MFG-001 p. 15), and an unknown
build-axis (Z) strength that the repo knocks down by 0.5 (ASSUMED, `sls_materials.py`). The right
minimum therefore depends on whether the part carries load, what backs the skin, and whether the
drawing fixes the build orientation.

## Result

A **minimum gauge**: the floor before any part-specific load analysis. A load-bearing part is still
sized by its own loads; this gives where that analysis starts. "Any orientation" applies the Z
knockdown and is the default; "XY fixed" applies only when the drawing fixes the print orientation
so the skin bends in the build plane.

| Part | Backing | Any orientation (default) | XY fixed on the drawing | Governing mode |
|---|---|---|---|---|
| **Non-load-bearing** | **Foam-backed** (2 lb/ft³ PU) | **0.051 in (1.3 mm)** | 0.039-0.043 in (1.0-1.1 mm) | foam crush under the handling load (ESTIMATE, foam strength unverified) |
| | **Free-standing** | **0.040 in (1.0 mm)** to 1 in span; 0.064 in (1.6 mm) at 2 in; 0.084 in (2.1 mm) at 3 in; 0.101 in (2.6 mm) at 4 in | 0.039 in (1.0 mm) to 1 in; 0.051 in (1.3 mm) at 2 in; 0.066 in (1.7 mm) at 3 in; 0.080 in (2.0 mm) at 4 in | oil-canning (deflection) beyond about 1 in span; process floor below |
| | **Lattice-supported** (node pitch to 1 in) | **0.039 in (1.0 mm)** | 0.039 in (1.0 mm) | process floor |
| **Load-bearing** | **Foam-backed** | **0.052 in (1.3 mm)** handling floor; in-plane compression limited by face wrinkling (see below) | 0.039 in (1.0 mm) floor; same wrinkling limit | handling rupture; wrinkling for in-plane load |
| | **Free-standing** | **0.098 in (2.5 mm)**; 0.101 in (2.6 mm) at 4 in span | **0.077 in (2.0 mm)**; 0.080 in (2.0 mm) at 4 in | stiffness parity with the 2.0 mm CF-PETG design basis |
| | **Lattice-supported** | **0.039 in (1.0 mm)** at node or rib pitch up to 0.81 in (20.5 mm); 0.051 in (1.3 mm) to 1.05 in; 0.059 in (1.5 mm) to 1.21 in; 0.079 in (2.0 mm) to 1.62 in | same pitches | skin buckling between nodes at the full design compressive stress |

Every value is an ESTIMATE from declared inputs (next section). The SLS DFM audit
(`tools/sls_dfm_audit.py`) flags any wall reading below 0.037 in (0.95 mm).

## Method, loads and inputs

**Failure modes.** Process floor; flexural rupture of the skin under a handling point load; oil-
canning (deflection); for load-bearing skins also stiffness parity with the old FDM basis, panel
buckling between supports, and face wrinkling over foam. Thin-plate central-load formulas (Roark,
circular plates: simply supported for free-standing panels, clamped for lattice cells, a foundation-
equivalent plate for foam-backed skins), Winkler foundation characteristic length (Timoshenko and
Woinowsky-Krieger), the simply supported plate buckling coefficient k = 4, and the Hoff-Mautner face-
wrinkling stress 0.5 (Ef Ec Gc)^(1/3). These textbooks are not yet catalogued in `REFERENCES.md`:
**edition and table numbers require verification** before this is cited as a design basis.

| Input | Value | Status |
|---|---|---|
| PA CF flexural modulus / strength, XY | 1,015 ksi (7,000 MPa) / 20.3 ksi (140 MPa) | typical, REF-MAT-015 (not a design allowable) |
| Z knockdown (orientation not fixed) | 0.5 on modulus and strength | ASSUMED (`sls_materials.Z_KNOCKDOWN_PA_CF`) |
| Poisson ratio | 0.35 | ASSUMED |
| Handling load | 10 lbf (44.5 N) on a 0.25 in (6.35 mm) radius (a firm thumb press) | ASSUMED; no standard sets it |
| Deflection limit under handling | 0.040 in (1.0 mm) | ASSUMED |
| Factor of safety | non-load-bearing 1.5; load-bearing 1.5 basic x 1.5 special = 2.25 | ASSUMED; special factor after the 14 CFR §23.2265 model for process variability |
| Foam core (2 lb/ft³ PU) | Ec 145 psi (1.0 MPa), Gc 58 psi (0.4 MPa), depth 0.5 in (12.7 mm) | ASSUMED low-end; the FOAM-PU-2LB kit has no datasheet in the repo |
| Old basis | 2.0 mm CF-PETG, flexural modulus 6,670 MPa | REF-MAT-002 via `MASS_AUDIT_CARGO_WING_ROOT.md` §1 |

## Findings the table depends on

1. **Foam-backed skins are limited by the foam, not the skin.** Under the 10 lbf handling load a
   1.0 mm skin spreads the load over about a 0.32-0.38 in (8-10 mm) characteristic radius, so the
   foam sees about 22-32 psi (150-220 kPa). That is about what 2 lb/ft³ rigid PU typically withstands,
   so the skin is thickened to 1.3 mm (any orientation) to bring the foam pressure to about 21 psi.
   **Get the foam's compressive strength from its datasheet**; it can move this row either way.
2. **2 lb/ft³ foam barely stabilizes a load-bearing skin.** Face wrinkling limits in-plane
   compressive skin stress to about 811 psi (5.6 MPa) any orientation, 1,022 psi (7.0 MPa) XY, before
   the 2.25 factor: about 360 psi (2.5 MPa) allowable. A 1.3 mm foam-backed skin then carries only
   about 19 lbf/in (3.3 N/mm) of compression. **Load-bearing skins that see compression should be
   rib- or lattice-supported, not foam-backed**, or use a stiffer core.
3. **Free-standing load-bearing walls are set by stiffness parity, not strength.** Every existing
   analysis assumed a 2.0 mm CF-PETG skin. A PA CF skin matches its bending stiffness at 1.97 mm when
   the skin bends in the build plane, but needs 2.48 mm if the orientation is not fixed (Z knockdown).
   **A 2.0 mm PA CF skin of unfixed orientation has about 52 % of the bending stiffness the old
   analyses assumed** (E t³ ratio).
4. **Lattice support makes the process floor govern**, provided the node or rib pitch stays within
   the buckling limit for skins that carry compression.

## OD-19 — Owner Decision Brief: adopt an SLS minimum-wall rule

| Check | Finding |
|---|---|
| **Statics and dynamics** | Governing loads: a 10 lbf (44.5 N) handling point load (ASSUMED), in-plane compression for load-bearing skins. Allowables are typical datasheet values with a 0.5 Z knockdown and a 2.25 factor for load-bearing parts. |
| **Function** | Thinner non-structural skins (fairings, covers, cosmetic shells) still hold shape and survive handling; foam-backed parts need a vent and fill hole as before. |
| **Structural integrity** | Load-bearing free-standing walls stay at 2.0-2.5 mm; load-bearing thin skins need ribs or lattice at the stated pitch. Joints, bosses and insert walls are not covered here and keep their own rules (§7 two-wall annulus and positive stop; insert wall ≥ 0.079 in (2.0 mm) to a bore, as used in NAC-64-ASM-03). |
| **Mechanism and component interactions** | None directly; thinner skins free internal volume. |
| **Weight and balance** | Non-load-bearing foam-backed skins drop from 2.0 to 1.3 mm (about −35 % shell mass) or 1.0 mm XY-fixed (−50 %). Example: the OD-17 wing-tip fairing at 1.3 mm instead of 2.0 mm saves roughly 0.006-0.008 lbm (3-4 g) per side (ESTIMATE; rebuild with `nacelle64_wing_fairing.py --skin 1.3` to get the mesh mass). |
| **Canonical shape** | Internal only; the outer mould line is unchanged. |

**Options.**
- **A (recommended):** adopt the table above as the SLS rule in `AGENTS.md` §7 (owner edit), keeping
  2.0 mm as the default where a part's category or orientation is not stated, and requiring the print
  orientation on the drawing to use the XY column.
- **B:** keep 2.0 mm everywhere. Simple, but it over-builds non-structural skins and, for load-bearing
  skins of unfixed orientation, still falls about 20 % short of stiffness parity (2.48 mm needed).
- **C:** adopt A for non-load-bearing parts only; leave load-bearing parts at 2.0 mm pending Z-axis
  coupon data.

**Recommendation: A**, because it is the only option that is both lighter where it can be and stiff
enough where it must be, and it ties the XY values to a stated print orientation as REF-FAA-002's
process-control model expects.

**Still unverified:** PA CF Z-axis strength and modulus (the 0.5 knockdown); the 2 lb/ft³ foam's
compressive strength, modulus and shear modulus; the handling load (consider a press test on a
printed coupon panel); textbook citations (Roark, Timoshenko, Allen/Hoff-Mautner) not yet in
`REFERENCES.md`; SLS dimensional tolerance on thin walls (design nominal at or above the floor plus
the vendor's tolerance).

**Open consequence:** hull shells and other load-bearing 2.0 mm SLS parts whose print orientation is
not fixed fall short of the stiffness parity in finding 3; logged in `airframe/WBS.md` for review.
