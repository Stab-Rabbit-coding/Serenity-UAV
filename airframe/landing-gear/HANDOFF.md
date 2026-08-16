# Landing Gear — Session Handoff (2026-08-09)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**AI note:** Session record written by Claude (model: Claude Opus 5,
Anthropic) under the author's direction, per `AGENTS.md` AI-attribution policy.  
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0

> Start here, then read `docs/LANDING_GEAR_ANALYSIS.md` §2.4a and §4.5a.
> The ordered task list is `WBS.md` §1.1.4.1 (LG-10.1 … LG-10.8).

---

## 1. State

Branch `feat/lg-r6-bay-integration` (worktree `.worktrees/lg-r6-bay-integration`).
Local `main` was fast-forwarded through `ae7ad5f`; later commits are on the
branch only. Nothing is pushed.

| Commit | What |
| --- | --- |
| `f6043ba` | bay pad fit tool; proved the flat-mount defect |
| `6a6b09a` | bay cowl + LG-13 retention; `BAY_CANT` sign fix |
| `d83c806` | hull-side bolt bosses (wrong placement — see §3) + LG-02 margins |
| `4a9df0e` | trapezoidal cowl; **LG-17 closed at 4 ft** |
| `fd383d4`, `6c464a0` | Henning geometry spec; sponson identification |
| `ae7ad5f` | gated the misplaced bosses off; recorded the finish plan |
| `abf88b5` | LG-10.1 planar-segmentation measurement tool |
| `f687c9b`, `1211cd6`, `cac91cf` | LG-10.2/10.3 wells cut open |

**The canonical `cargo_sect_shell24_2mm_repaired.stl` is UNTOUCHED.** Every
merge wrote to a scratch `CARGO_MERGE_OUT`. The accepted result is
`cargo_wells_only.stl` (regenerate it; the scratch dir is session-local).

## 2. Closed

- **LG-13** — nylon-tipped M2 drag screw on a raised thread pad, bay side only.
  The seat **slides 1.62 mm per stroke**, so a torqued clamp would fight the
  fuse. Derivation: `landing_gear_r6_sizing.py --derive-stroke`.
- **LG-17** — **4 ft** adopted. Ø4.36 → Ø3.81, wire 70.2 → 53.6 g,
  P_wire 4,333 → 2,889 N, F_leg 1,241 → 827 N, hip moment 52.0 → 34.7 N·m.
- **LG-19** — trapezoidal bay cowl on the bay plate (taper 0.72), open at the
  mouth, verified clear of the thigh at 0/8/16/24/30.9° by boolean
  intersection (`tools/landing_gear_cowl_clearance.py`).
- **LG-10.1/10.2/10.3** — wells measured, placed and cut (below).

## 3. The one thing to understand before touching anything

**The mounting face is the sponson's 25° angled panel, NOT the cargo flank.**
Rev R6 assumed the flank throughout, and that assumption caused every defect
found this session.

- Measured panel normal **(0.901, 0.015, −0.433)** port, mirrored starboard;
  tilt 25.1–26.0°, mirror-verified to 1.4 mm. **Use this constant directly.**
  A per-station frame search lands on door-frame/joint surfaces and returns
  junk normals (Y-dominated fore, −Z-dominated aft).
- The vertical walls squared to port/starboard are the hull sides **forward
  of** the sponson — not a mounting face.
- **Y −7 is where the sponson meets the wall**, so the wells need **no**
  sponson extension. Each cutter removes 6.0–6.7 cm³ of existing shell at the
  canonical stations. A convex-hull extension was tried and reverted: +61.7 g
  of bulge for nothing. Wells-only is **−26.6 g** (298,576 → 273,270 mm³), and
  that delta matching 4 × ~6.3 cm³ is the check that the cuts are correct.
- `d83c806`'s 16 bolt bosses are on the bare flank and are therefore
  mispositioned. `LG_BAY_ENABLED = False` keeps them out of the shell.

## 4. Traps that cost real time

1. **A file edit can silently not apply** if the file changed on disk. It
   produced a byte-identical no-op merge that still printed `RESULT: PASS` and
   `CI_valid=True`. Assert replacements; confirm the volume actually moved.
2. **"Most outboard vertex" finds the hull's widest point (Z ≈ 78)**, not the
   bay station (Z 38). Constrain height as well as plan position.
3. **`nx > 0.7` for "port outward" also catches the starboard INNER wall**
   (its normal points toward +X). Always add an X-vs-centreline constraint —
   without it a convex hull spanned the entire hull.
4. Run mesh/boolean tooling with **`/usr/bin/python3`**; the repo `.venv` hides
   `manifold3d`, `sympy` and `matplotlib`. **pip is not permitted.** There is
   no `rtree`/`embree`, so `trimesh.ray` and `proximity.closest_point` are
   unavailable — use projection or sectioning.

## 5. Next, in order

1. **Visually review the cut wells**, then publish the merged shell to the
   canonical STL and re-run `tools/validate_stls.py`.
2. Relocate the 16 bay bolt bosses onto the new well collars, aim them along
   the panel normal, set `LG_BAY_ENABLED = True`.
3. LG-10.6 hull patches + `BAY_CONFORM`; LG-10.7 FCStd purge of
   `leg_4_scaled24` and `nacelle_port_revq`; LG-10.8 foot Z-levelling.

**Carried analysis items** (both affect geometry, worth settling early):

- **`wire_stroke_available()` is 4× low** (§4.5a). `H_DEF_DUCT` should be 9.9
  not 19.2, and ductile stock could drop 75 → ~40 mm (~33 g, LG-18).
  Correcting it re-opens LG-15 and would shrink the bay.
- **§11.4 "shared BOM"** needs amending: a conforming back face makes the bay
  two mirrored geometries, not one shared part.

## 6. Known noise

`tools/precommit_sanitize.py` flags `BAKE_T` in `merge_cargo_interior.py:127`
as a "phone number" on every commit touching that file. False positive,
non-blocking.
