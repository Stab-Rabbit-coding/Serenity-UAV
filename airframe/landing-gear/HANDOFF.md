# Landing Gear — Session Handoff (2026-08-17)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**AI note:** Session record written by Claude (model: Claude Opus 5,
Anthropic) under the author's direction, per `AGENTS.md` AI-attribution policy.  
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0

> **LG-10 is closed.** All eight sub-items (LG-10.1 … LG-10.8) are done and
> gated by tools. Full detail is `WBS.md` §1.1.4.1; this file is the short
> version plus the traps worth carrying forward.

---

## 1. State

Bay integration is complete: the hull carries the four seats, the printed bay
seats on them, and the gear stands on its treads. Four tools gate it, and all
four pass:

| Tool | Gates | Result |
| --- | --- | --- |
| `tools/validate_stls.py` | every STL watertight | 62/62 pass |
| `tools/landing_gear_wing_clearance.py --proud` | LG-10.4 bay vs wing | clear, no proud material |
| `tools/landing_gear_bay_seat_fit.py` | LG-10.6 datum + seat | 0.00 mm drift, 0.000 mm³ interference |
| `tools/landing_gear_foot_stance.py` | LG-10.8 stance | both variants clear |

Published cargo shell: 908,106 faces, 1 body, watertight, 0 boundary / 0
non-manifold edges, 295,931 mm³ → 310.7 g as-printed … 378.8 g solid CF-PETG.

Run mesh/boolean tooling with **`/usr/bin/python3`** — see §4.

## 2. What the last session actually changed

Three of the four remaining items closed **differently from how they were
written**, and the reasons matter more than the diffs:

- **LG-10.6** — the conforming back face and `BAY_CONFORM` are **retired**, not
  built. The hull's flange rebate already presents a flat seat, so cutting the
  printed part to a curve would put the mismatch back. The real defect was the
  **datum**: `BAY_STANDOFF` was 12.6/5.4 (measured along the panel normal)
  against a hull pocket cut at −7.69/−3.55 in the plate frame — a **3.5–7.7 mm
  air gap** under every M3. Now 4.91 fore / 1.85 aft, one datum per station.
- **LG-10.8** — the four feet were always level (spread 0.0000 mm). The
  assembly's lowest point was not the sole: a hardcoded spigot cube drove
  **2.9 mm through the foot** on the 1.5in leg, with **743.9 mm³** of leg
  inside the foot. `ANKLE[2]` was 6.4 mm off the rule `FOOT_HUB_H`'s own
  comment states. Fixed, with an in-SCAD `assert()` so it cannot recur.
- **LG-10.7** — purged the whole superseded object set from the FCStd (16 → 6
  objects), not just the two the item named; purging literally would have left
  three legs beside four feet.

Two latent bugs surfaced on the way and are fixed:

- **`bowed_wire` in the 1.5in SCAD** built its side wall as a list of face
  PAIRS inside a no-op `concat()`. Every wire on the **default** leg had been
  exporting as 20 cap faces of zero volume; the shared wire STLs looked fine
  only because they came from the 3.0in file.
- **Zero-area collinear slits** on nearly-coplanar boolean seams failed the CI
  watertight gate, and `fill_holes` cannot close them (the fill triangle has no
  area). `merge_cargo_interior.close_zero_area_slits()` collapses them; real
  holes still fail loudly.

## 3. The one thing to understand before touching anything

**The mounting face is the sponson's 25° angled panel, NOT the cargo flank.**
Rev R6 assumed the flank throughout, and that assumption caused every defect
found in this work.

- Measured panel normal **(0.901, 0.015, −0.433)** port, mirrored starboard.
  **Use this constant directly** — a per-station frame search lands on
  door-frame/joint surfaces and returns junk normals. Since LG-10.3 it is used
  only to LOCATE the opening, never to orient the mount: the bolt axis and the
  panel normal disagree by a 21–24° yaw that no `BAY_CANT` can remove.
- **Y −7 is where the sponson meets the wall**, so the wells need **no**
  sponson extension. A convex-hull extension was tried and reverted: +61.7 g of
  bulge for nothing.
- **`BAY_STANDOFF` is a contract** with `merge_cargo_interior.py`
  (`station_seat_data()`). Re-run `landing_gear_bay_seat_fit.py` after ANY hull
  re-merge, and `landing_gear_wing_clearance.py` after any spar move.

## 4. Traps that cost real time

1. **A file edit can silently not apply** if the file changed on disk. It
   produced a byte-identical no-op merge that still printed `RESULT: PASS` and
   `CI_valid=True`. Assert replacements; confirm the volume actually moved.
2. **"Most outboard vertex" finds the hull's widest point (Z ≈ 78)**, not the
   bay station (Z 38). Constrain height as well as plan position.
3. **`nx > 0.7` for "port outward" also catches the starboard INNER wall**
   (its normal points toward +X). Always add an X-vs-centerline constraint.
4. Run mesh/boolean tooling with **`/usr/bin/python3`**; the repo `.venv` hides
   `manifold3d`, `sympy` and `matplotlib`. **pip is not permitted.** There is
   no `rtree`/`embree`, so `trimesh.ray` and `proximity.closest_point` are
   unavailable — use projection or sectioning.
5. **Measuring the seat on the PUBLISHED shell is circular** — the rebate has
   already been cut there, which moves the outboard skin inboard. Measure it on
   `BLENDER_SRC` (pre-cut), which is what `station_seat_data()` does.
6. **A sub-tolerance geometry nudge can break the mesh.** Moving one collar
   0.02 mm to share a station datum was enough to create a coplanar seam and a
   zero-area slit that failed CI.

## 5. Still open in this subsystem

Nothing in LG-10. What remains is procurement, physical test, and cosmetics —
see `TODO.md`. The two that most affect geometry:

- **`wire_stroke_available()` is 4× low** (§4.5a). `H_DEF_DUCT` should be 9.9
  not 19.2, and ductile stock could drop 75 → ~40 mm (~33 g, LG-18).
  Correcting it re-opens LG-15 and would shrink the bay.
- **LG-15 / LG-16** (wire procurement and temper) **block leg fabrication**;
  **LG-13** (wire-end retention) **blocks first flight**.

## 6. Known noise

`tools/precommit_sanitize.py` flags `BAKE_T` in `merge_cargo_interior.py` as a
"phone number" on every commit touching that file. False positive,
non-blocking.

`tools/landing_gear_cowl_clearance.py --variant 1_5in` reports 5.468 mm³ at
**26°**, which is 4° PAST the 22° mechanical stop the leg cannot reach; it is
clear at every angle through the real stroke, and this was true before the
LG-10 close-out (baselined 2026-08-17). The tool fails on any sampled angle, so
it exits non-zero — do not read that as a new regression. The 3.0in variant is
clear at every sampled angle.
