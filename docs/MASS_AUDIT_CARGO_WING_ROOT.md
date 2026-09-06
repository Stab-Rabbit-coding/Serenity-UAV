# Mass Audit — Cargo Section and Wing Roots (Rev S1g)

**Revision:** 1 (2026-08-30)
**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**Analysis and drafting:** Claude (Claude Opus 5, Anthropic) under the author's
direction, per `AGENTS.md` §3 "Attribution and Licensing"
**License:** CC BY-SA 4.0 — <https://creativecommons.org/licenses/by-sa/4.0/>

> ⚠️ **ENGINEERING REVIEW REQUIRED — this output is not a substitute for a
> qualified engineer.** Every result, calculation, and recommendation produced
> with this skill **must be independently reviewed and accepted by a properly
> qualified individual** — a licensed Professional Engineer or an equivalently
> qualified authority for the jurisdiction and discipline — **before it is
> applied to any system carrying risk to life or safety.** This skill informs
> engineering judgment; it does not replace it, and it carries no professional
> liability.

---

## 0. Headline

**The largest mass problem in the cargo section is not geometry, it is
bookkeeping.** Twenty-three printed-part rows in `bom_revS.csv` were checked
against the STL they name. They understate the printed mass by **+521.6 g** in
total — **13.3 % of the 3,911 g (8.62 lbm) AUW** — and the single worst row is
the cargo section itself, at **+207 g**.

No amount of ribbing recovers 522 g. The BOM has to be reconciled to the meshes
before any lightening decision can be trusted, because the design is currently
being weighed against a number that is not the aircraft.

Separately, **`FOAM-PU-2LB` carried 900 g in the mass column — the *kit* mass,
not the installed foam.** Installed foam is **22 g**.

Those two corrections move in opposite directions and do not cancel.

---

## 1. Basis and conventions

| Quantity | Value | Source |
|---|---|---|
| CF-PETG as-printed bulk density `RHO_PRINT` | 1.05 × 10⁻³ g/mm³ | `merge_cargo_interior.py` (4 perimeters + ≥ 40 % infill) |
| CF-PETG solid density `RHO_SOLID` | 1.28 × 10⁻³ g/mm³ | same |
| PU foam | 2 lb/ft³ = **32.04 × 10⁻⁶ g/mm³** | `FOAM-PU-2LB`, `bom_revS.csv` |
| CF-PETG flexural modulus | 6.67 GPa | REF-MAT-002 (20 % chopped CF, ASTM D790) |
| AUW, Phase 5–10 | 3,911 g (8.62 lbm) | `docs/structural_analysis.md` §3 — a **design-margin back-calculation, not a BOM sum** |

> **`RHO_PRINT` is a bulk figure and must not be re-derived as
> `RHO_SOLID × infill`.** For anything thinner than about 6 mm the part is
> almost entirely perimeter: a 5 mm plate at 4 × 0.6 mm perimeters is 4.8 mm of
> wall and 0.2 mm of infill, so infill percentage barely moves it. Applying
> `1.30e-3 × 0.40` gives roughly **half** the true mass. That error was made in
> this repository on `PRINT-WING-ROOT-FLANGE` at Rev S1g and is corrected in §5.

All masses below are `RHO_PRINT` unless stated. Thin-walled proposals in §6 are
quoted at `RHO_SOLID`, which is the honest density for a pure-perimeter section
and makes the saving estimate conservative.

---

## 2. Cargo section — where the mass actually is

Measured against the published
`airframe/stls/fuselage/cargo/cargo_sect_shell24_2mm_repaired.stl`.

| Item | Volume (mm³) | Mass |
|---|---:|---:|
| Base shell before any feature (hollow, 2 mm wall) | 370,509 | 389.0 g |
| **Published shell, all features, as built** | **354,486** | **372.2 g** |

The net is *negative* — the duct removal, the clamshell aperture and the two
mating-face cuts take out more than the bosses and pads put in. That is why the
feature-by-feature table below matters more than the total: it is where the
recoverable mass lives.

### 2.1 Added features (envelope-clipped, as they land on the hull)

| Feature | Volume (mm³) | Mass | Note |
|---|---:|---:|---|
| **Actuator pad, port** | 52,673 | **55.3 g** | 24.1 g legacy embed + 31.4 g Rev S1g standoff |
| **Actuator pad, starboard** | 51,599 | **54.2 g** | 23.3 g + 31.4 g |
| Spar socket boss, port | 12,227 | 12.8 g | Ø30.1 (was Ø27.7 / 10.9 g) |
| Spar socket boss, starboard | 10,656 | 11.2 g | Ø30.1 (was Ø27.7 / 9.5 g) |
| Landing-gear bay features (raw, pre-trim) | 119,985 | 126.0 g | Rev R6, pre-existing |
| Root flanges | — | **0 g** | reserved keep-out only; separate bonded parts |

**The two actuator pads are 109.5 g — the heaviest discretionary feature on the
cargo section, and 29 % of the whole shell.** Before the Rev S1g standoff they
were 47.4 g. They are the obvious target and §6 quantifies them.

### 2.2 Already recovered at Rev S1g

Retiring the wing-root tie-rod couple removed four bosses from the shell:

| | Volume (mm³) | Mass |
|---|---:|---:|
| rod fwd boss, port / starboard | 3,559 / 3,783 | 3.7 / 4.0 g |
| rod aft boss, port / starboard | 1,661 / 2,179 | 1.7 / 2.3 g |
| **shell subtotal** | **11,182** | **11.7 g** |
| plus `CF-ROD-8MM` + `CF-ROD-6MM` stock | — | **22.0 g** |
| **total already banked** | | **33.7 g** |

---

## 3. Wing roots — there is almost nothing to take

| | Volume (mm³) | Mass |
|---|---:|---:|
| `wing_port_s1223_revo.stl` | 90,992 | 95.5 g |
| `wing_stbd_s1223_revo.stl` | 90,992 | 95.5 g |

Spanwise distribution, port, 8 slices across the 95.7 mm baked extent
(X −89 = root, X +6.7 = tip):

| X band | Mass |
|---|---:|
| −89.00 … −77.04 | 6.97 g ← tenon only; the root face is at ≈ −77 |
| −77.04 … −65.07 | **14.54 g** ← root section, the heaviest slice |
| −65.07 … −53.11 | 13.98 g |
| −53.11 … −41.15 | 13.40 g |
| −41.15 … −29.19 | 12.81 g |
| −29.19 … −17.22 | 12.20 g |
| −17.22 … −5.26 | 11.57 g |
| −5.26 … +6.70 | 10.07 g |

The distribution is a clean taper with no local pile-up, which is the signature
of a wing that is skin-limited rather than feature-limited. **The two dimensions
that set it are both already at their floors:**

* `WALL_T = 2.5 mm` is **four perimeters at 0.6 mm** — the repo's minimum wall.
  Taking it to 2.0 mm is 3.3 perimeters, which is not a wall, it is a
  suggestion. **Do not.**
* `THICKNESS_SCALE = 1.46` at the root is **solved, not chosen** — it is the
  exact figure that leaves 1.19 mm of skin over the Ø20.4 spar bore against the
  1.16 mm floor (`tools/wing_spar_station_fit.py`). Thinning the section breaks
  the bore out of the skin.

**Recommendation: take nothing from the wing.** The 33.7 g the tie rods gave
back is the whole of what this structure had to give, and it has been taken.

---

## 4. Foam fill and voids

### 4.1 Cargo section volume budget

| | Volume (mm³) | Litres |
|---|---:|---:|
| Outer envelope (filled hull) | 3,537,697 | 3.538 |
| less printed shell | −354,486 | −0.354 |
| **enclosed cavity** | **3,183,211** | **3.183** |
| less cargo bay — **explicitly not foamed** (`FOAM-PU-2LB`: *"do NOT foam nacelle or open cargo bay"*) | −2,135,476 | −2.135 |
| **foamable, upper bound** | **1,047,735** | **1.048** |

At 2 lb/ft³ that is **33.6 g of foam in the cargo section** — and it is an upper
bound, because the EPS void formers (avionics bays ×4, wiring trunk, power bus,
ventilation, Faraday cage pockets — `airframe/placeholders/foam/`) displace part
of it and are removed after cure.

### 4.2 The 900 g error

`FOAM-PU-2LB` carried **900 g** in `Unit_Mass_g`. That is the mass of the A + B
kit as purchased. The row's own note says **"~0.7 L mixed fill"**, and 0.7 L at
2 lb/ft³ is **22.4 g**. The measurement above independently supports that order:
the cargo section alone can accept at most 1.048 L.

**Corrected to 22 g.** Procurement quantity is unchanged — one kit is still one
kit. Only the mass column moves.

> **This is a pattern, not an isolated row.** The same kit-vs-installed
> confusion sits in `FIL-CF-PETG` (2,000 g of *spool stock*, of which the
> printed parts are the real mass and are already counted on their own rows),
> the West System epoxy row, and the EPS board row. Summing
> `bom_revS.csv` `Total_Mass_g` returns 12.7 kg, which is not the mass of
> anything — it mixes installed hardware, consumable stock, and ground-support
> equipment. **The BOM needs an `Installed` flag before its mass column can be
> used for a weight statement.** Logged as an open item.

---

## 5. BOM-vs-mesh reconciliation

Every `PRINT-*` row with `Qty > 0` whose description names an STL that exists
was measured. Twenty-three matched.

| Row | Qty | BOM g/ea | Measured g/ea | Δ |
|---|---:|---:|---:|---:|
| **PRINT-CARGO-SECT** | 1 | 165.0 | **372.2** | **+207.2** |
| **PRINT-BATT-TRAY** | 1 | 22.0 | **140.2** | **+118.2** |
| **PRINT-HEAD-SHELL** | 1 | 83.0 | **177.6** | **+94.6** |
| **PRINT-CARGO-CRADLE** | 1 | 18.0 | **80.6** | **+62.6** |
| **PRINT-MIDDLE-CANONICAL** | 1 | 135.0 | **190.9** | **+55.9** |
| PRINT-REAR-NECK-INTAKE | 1 | 200.0 | 243.2 | +43.2 |
| PRINT-BELLY-PANEL | 2 | 6.0 | 24.5 | +18.5 |
| PRINT-WING-ROOT-FLANGE | 2 | 12.7 | 25.6 | +12.9 |
| PRINT-CARGO-DOOR-PORT | 1 | 45.0 | 14.7 | −30.3 |
| PRINT-CARGO-DOOR-STBD | 1 | 45.0 | 14.8 | −30.2 |
| PRINT-NACELLE-RING | 2 | 18.0 | 6.7 | −11.3 |
| *(12 further rows, each within ±7 g)* | | | | |
| **TOTAL, matched rows** | | **975.2** | **1,496.8** | **+521.6** |

### 5.1 Corrected in this pass

* **`PRINT-CARGO-SECT` 165 → 372 g.** Not a Rev S1g regression: the *pre*-Rev-S1g
  shell already measured 316 g against the same 165 g row. The row predates the
  Rev R6 landing-gear bay features, the actuator pads, the Ø30.1 sockets and the
  CF thwart pockets.
* **`PRINT-WING-ROOT-FLANGE` 12.7 → 25.6 g/ea.** This one was our own error,
  introduced at Rev S1g: `RHO_SOLID × 0.40` instead of `RHO_PRINT`. See the
  warning in §1.
* **`FOAM-PU-2LB` 900 → 22 g.** §4.2.

### 5.2 Not corrected here, and why

`PRINT-BATT-TRAY` (+118 g), `PRINT-CARGO-CRADLE` (+63 g), `PRINT-HEAD-SHELL`
(+95 g), `PRINT-MIDDLE-CANONICAL` (+56 g) and `PRINT-REAR-NECK-INTAKE` (+43 g)
belong to other WBS branches. They are reported here with measurements so the
owning branch can act, rather than being edited across a governance boundary.

**`PRINT-BATT-TRAY` deserves a second look on its own merits**, not just as a
bookkeeping fix: 140 g for a battery tray is 3.6 % of AUW, it sits in the cargo
section, and it is 30 % of its own bounding box — which is a lot of solid for a
part whose job is to locate a LiPo and react 4 g × 1.5 through straps.

---

## 6. Lightening the actuator pads — the one real opportunity

### 6.1 Loads

| Term | Value | Basis |
|---|---:|---|
| Gear tangential force | 3.26 N (0.73 lbf) | `T / r` = 0.0496 N·m / 15.2 mm |
| Gear radial force | 1.19 N (0.27 lbf) | `F_t · tan 20°` |
| Gear separation resultant | 3.47 N (0.78 lbf) | `F_t / cos 20°` |
| Actuator inertial load | 3.53 N (0.79 lbf) | 60 g × 9.81 × 4 g × 1.5 |
| **Design load used below** | **5.0 N (1.12 lbf)** | worst-case combined, deliberately conservative |

### 6.2 The governing failure mode is not strength — it is mesh opening

A spur pair fails functionally long before it fails structurally: if the mount
deflects, the centre distance changes and the mesh opens. So the check is
**deflection**, not stress. Cantilever, `δ = F L³ / (3 E I)`, `L` = 18 mm,
`E` = 6.67 GPa:

| Standoff form | `I` (mm⁴) | Deflection at 5 N |
|---|---:|---:|
| Solid slab, as built | 100,875 | 1.44 × 10⁻⁵ mm |
| Hollow box, 3.0 mm wall | 58,043 | 2.51 × 10⁻⁵ mm |
| 4 × Ø12 posts | 15,381 | 9.47 × 10⁻⁵ mm |

A 0.05 mm centre-distance change is about 6 % of one module and would be
tolerable. **Every option is three or more orders of magnitude inside that.**
The solid pad is not carrying anything; it is there because a box was the easy
primitive.

*Modes checked and found non-governing:* bearing at the M3 heat-set inserts
(4 inserts sharing 5 N), tear-out at the flange, buckling of the standoff
(L/r ≈ 2, nowhere near slender), and bond shear where the pad fuses to the wall.
Fatigue is not assessed — tilt is a low-cycle duty, but the cycle count is not
established.

### 6.3 Options

| Option | Volume/side | Mass/side | **Saving, pair** | Risk |
|---|---:|---:|---:|---|
| As built — solid | 29,889 mm³ | 31.4 g | — | — |
| **Hollow box, 2.5 mm wall + 2.5 mm face** | 11,666 mm³ | 14.9 g | **−32.9 g** | low |
| Hollow box, 3.0 mm wall + 2.5 mm face | 13,061 mm³ | 16.7 g | −29.3 g | lowest |
| 4 × Ø12 posts, no skirt | 8,143 mm³ | 10.4 g | **−41.9 g** | print-orientation risk |

**Recommended: the 2.5 mm hollow box, −32.9 g.** It is four perimeters — the
same wall the rest of the airframe uses — it prints as part of the shell without
free-standing features, and it keeps a continuous face for the actuator flange.
The post variant saves 9 g more but puts four unsupported 18 mm columns inside
the hull, and their print orientation is set by the cargo shell's, not by what
suits them.

Masses for the hollow options are quoted at `RHO_SOLID`, not `RHO_PRINT`,
because a thin wall is all perimeter. That makes these savings conservative.

### 6.4 What NOT to do

* **Do not shrink `NSVMT_STANDOFF` below 18 mm.** It is
  `11 (gear plane) + 6 (gear face) + 1 (hub clearance)`, and the 11 is
  `8 (tenon insertion) + 3 (the repo's own GAP_BUDGET to a moving part)`.
  Recovering 3 mm buys 10.5 g and spends a stated clearance budget against a
  rotating gear.
* **Do not drop the gear face width below 6 mm.** 6 mm is 7.5 × module, already
  at the low end of the conventional 6–12 × module band. The load would allow
  less; the convention should not be broken for 5 g.
* **Do not thin the legacy 40 mm pad embed without an FEA or a coupon.** It is
  worth ~24 g/pair, but it also fuses the pad to a curved wall 3.6 mm from the
  landing-gear bay seats, and that interaction has not been characterised.

---

## 7. Revised Rev S1g mass delta

Correcting the flange density error changes the figure previously recorded:

| | Δ mass |
|---|---:|
| Cargo shell (Ø30.1 sockets, 18 mm standoffs, less the retired tie-rod bosses) | +56.0 g |
| `SPAR-CF-20X16` 58.2, `SHAFT-TILT-4MM` 49.4, `GEAR-TILT-FUS-38T` 16.0, `BUSH-TILT-4MM` 6.0, `PRINT-WING-ROOT-FLANGE` **51.2** | +180.8 g |
| Retired: `SPAR-TILT-4130` 96, `BRG-F688ZZ` 10, `PRINT-PUSHROD-CRANK` 6, `CF-ROD-8MM` 14, `CF-ROD-6MM` 8 | −134.0 g |
| **Rev S1g net** | **+102.8 g (+0.227 lbm), +2.63 % of AUW** |

Previously recorded as +77.0 g / +1.97 %. **The earlier figure was low because
the flange was under-massed by 25.6 g.** Corrected here and in
`airframe/fuselage-mid/WBS.md` WA-R18.

With the §6.3 recommendation applied, Rev S1g lands at **+69.9 g (+1.79 %)** —
below where it was first reported, on a corrected basis.

---

## 8. Findings and actions

| # | Finding | Action | Owner |
|---|---|---|---|
| **MA-1** | BOM printed-part masses understate by **+521.6 g** across 23 matched rows | Reconcile every `PRINT-*` row to its STL; add a CI check | root `TODO.md` §0.8 |
| **MA-2** | `PRINT-CARGO-SECT` 165 → **372 g** | **CORRECTED** | fuselage-mid |
| **MA-3** | `FOAM-PU-2LB` carried the 900 g **kit** mass, not the 22 g installed | **CORRECTED** | fuselage-mid |
| **MA-4** | `PRINT-WING-ROOT-FLANGE` used `RHO_SOLID × infill`; 12.7 → **25.6 g** | **CORRECTED** | fuselage-mid |
| **MA-5** | Actuator pads are 109.5 g of solid block carrying 5 N | Hollow to 2.5 mm wall: **−32.9 g** | fuselage-mid |
| **MA-6** | `PRINT-BATT-TRAY` measures **140.2 g** vs 22 g, in the cargo section | Re-measure, then lighten on its merits | fuselage-mid |
| **MA-7** | BOM mass column mixes installed mass, consumable stock and GCS | Add an `Installed` flag before any weight statement uses it | specification |
| **MA-8** | Wing roots have **no** recoverable mass — wall at 4-perimeter floor, thickness solved by the bore | None. Record so it is not re-litigated | wings-nacelles |
| **MA-9** | Rev S1g net is **+102.8 g**, not +77.0 g | **CORRECTED** in WA-R18 | fuselage-mid |

---

## 9. Sources

- `airframe/blender-scripts/merge_cargo_interior.py` — `RHO_PRINT`/`RHO_SOLID`,
  feature geometry, `wing_keepout_positives()`, `NSVMT_*`, `TILT_STAGE_*`.
- `airframe/openscad/wings/wings_s1223_revo.scad` — `WALL_T`,
  `THICKNESS_SCALE`, `SPAR_BORE_OD`.
- `tools/cargo_bay_envelope.py` — the 140 × 106 × 143.9 mm bay envelope used in §4.1.
- `tools/wing_spar_station_fit.py` — the 1.19 mm skin-over-bore figure that
  fixes `THICKNESS_SCALE`.
- `docs/structural_analysis.md` §3 (load factors, AUW basis), §6.4/§7.3
  (CF-PETG allowables).
- `docs/WING_ATTACH_INTERFACE.md` §4.3c — the drive stage the pads carry.
- `REFERENCES.md` REF-MAT-002 (20 % CF-PETG, 77 MPa flexural / 6.67 GPa).
- `current-specification/bom_revS.csv` — rows audited 2026-08-30.
- All volumes measured 2026-08-30 with `trimesh`/`manifold3d` against the
  published STLs under `/usr/bin/python3`.
