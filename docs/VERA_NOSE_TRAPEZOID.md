# Vera Nose PCB — Trapezoid Definition & Two-Sided Fit Analysis

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**AI-assist:** Claude Opus 4.8 (Anthropic) — geometry derivation, 2026-07-12
**License:** CC BY 4.0
**Revision:** Rev C (2026-07-12)

> **Rev C — SoM variant switched to connectorized PCM-071** (user, 2026-07-12). The
> module is now **32 × 43 mm** (was 40×40 DSC) via 2× Samtec BTH-060 board-to-board
> connectors, **+5 mm stacking Z-height** (the flush DSC advantage is gone). Two
> effects: (1) the **32 mm width fits the trapezoid comfortably** — the "SoM barely
> fits" tension of §4 is **gone** (a 32 mm part is within the board over the aft
> ~55 mm, and the wide end can shrink toward ~40 mm); (2) a new **nose-pod Z-budget
> check** for the 5 mm connector stack (head interior is ~140 mm tall so likely fine,
> but confirm the stack direction vs the skin). Sections 4/4.1 (40×40 fit) are
> retained as history; the width conclusion only relaxes.
>
> **Rev B update — measured, not estimated.** Slicing the baked head STL
> (`airframe/stls/fuselage/head_shell24_2mm_repaired.stl`, hull frame) at the board
> Z-band shows the **blunt** nose widens fast, so the §4 pessimism (based on a linear
> taper) is **resolved in the SoM's favour** — see §4.1. The SoM fits the nose.

Derives the Vera nose-carrier trapezoid from the airframe SCAD geometry
(`airframe/openscad/fuselage/head_shell24.scad`, `bow_sensor_faceplate.scad`,
`bow_sensor_pod.scad`) and reports an initial two-sided component-fit check.

## 1. Anchor geometry (from SCAD, part-local/SCAD frame)

- **Bow mounting flat:** ~26.4 × 15 mm planar face on the 40° bow flat
  (`bow_sensor_pod.scad`); the three apertures fit in one row, span ~25.5 mm.
- **`FACEPLATE_CTR` = [162.15, −282.53, 55.59]** (aperture-row centroid);
  **`BOW_CX` = 161.33** (aircraft CL). Nose tip ≈ Y −287.7; head aft (cargo mate)
  ≈ Y −53; head lateral extent X 99..228 (129 mm at the widest, aft).
- **Vera mount** (`head_shell24.scad vera_board_bosses`): station ≈ 20 mm aft of
  `FACEPLATE_CTR` (into the hull), level with the sensor cluster. *(That module still
  carries the stale 46×48 hole pattern — see §5.)*

## 2. Board frame ↔ hull mapping

Vera KiCad frame (user-confirmed): **+X fore→aft, +Y starboard→port, +Z
ventral→dorsal.** So the board's **long axis (X) = hull longitudinal (SCAD Y)** and
its **width (Y) = hull lateral (SCAD X)**. The sensor (narrow) end is at high board-X
(forward, at the flat); the board extends aft (low board-X) into the widening hull.

## 3. Narrow (sensor) end — SOLID

The forward end sits behind the 26.4 mm flat and must span the camera↔ToF apertures
(~25.5 mm). **Narrow-end width = 25.4 mm (1.0 in)** — matches the flat and the
current board width. This end is well-constrained.

## 4. Wide (aft) end — driven by the 40 × 40 mm SoM, and it is the binding problem

The `phyCORE-AM62A` SoM is **40 × 40 mm** and needs a **≥40 mm-wide region over its
full 40 mm length**. On a linear taper from the 25.4 mm narrow end over length L:

| Board length L | Wide end needed for the SoM to sit within the taper |
| --- | --- |
| 69.85 mm | **≥ 59.6 mm** (≥ 64 mm with 1 mm/side margin) |

**Making the board longer does NOT help** — with a modest wide end (e.g. 42 mm) the
≥40 mm-wide zone only spans ~8–16 mm regardless of length (8.4 mm at L=70, 15.7 mm at
L=130). The **taper angle**, not the length, is the constraint: to hold the SoM the
board must fan out to **≥60 mm** at the aft end (25.4→60 over 69.85 = ~14°/side).

**⇒ FINDING:** a nose trapezoid that is 1 in at the sensor end can only carry the
40 mm-square SoM if it fans to ~60 mm within ~70 mm — i.e. the **hull interior must be
≥60 mm wide (lateral) at the SoM station**, ~50 mm aft of the flat. Whether the (blunt)
nose provides that is a **FreeCAD cross-section question** — it CANNOT be derived from
the SCAD bounding box (AGENTS.md: bounding-box/centroid placement is inadequate for
this hull; a linear taper estimate is invalid near the blunt nose). **Referred to
FreeCAD/user.**

### Options if the nose is NOT ≥60 mm wide at the SoM station

1. **Fan to whatever the nose allows** and accept the SoM only if width permits.
2. **Split board** (the earlier sensor-head + aft-compute concept) — SoM on a wider
   board further aft, sensor head in the nose tip, linked by flex.
3. **SoM in the cargo install only**; nose Vera carries sensors + MSPM0 + connectors
   and streams to a compute node elsewhere (breaks "one board design" — needs a call).
4. **Rotate/relocate the SoM** — a 40 mm square cannot be made to fit a 25.4→42 taper
   by rotation; this does not resolve it.

## 4.1 Measured nose interior width (resolves §4)

Slicing the baked head STL at constant hull Y over the board's extent (board width axis
= hull X lateral; the bow tilt `BOW_ROT` is a rotation about X, so board width maps to
hull X), lateral outer width and the width within the board Z-band [95..125]:

| hull Y (mm) | board station | lateral X width (mm) | X width in Z[95..125] (mm) |
| --- | --- | --- | --- |
| −300 | fwd / faceplate (narrow) | 41.4 | 41.4 |
| −290 | +10 | 68.6 | 51.0 |
| −280 | +20 | 76.4 | 70.6 |
| −270 | SoM fwd edge (+30) | 72.7 | 59.1 |
| −260 | +40 | 78.5 | 62.6 |
| −250 | +50 | 91.6 | 61.0 |
| −240 | +60 | 97.1 | 57.8 |
| −230 | aft / SoM aft edge (+70) | 101.9 | 64.5 |

**Conclusion — the SoM fits the nose.** The nose is blunt: the Z-band lateral width is
already **59–64 mm over the entire SoM region (Y −270..−230)**. Minus 2×2 mm wall +
~1 mm/side clearance (~6 mm) that is **~53–58 mm of usable interior width** where the
SoM sits — enough for the 40 mm SoM plus routing. The forward/sensor end (Y −300) has
41 mm (≥ the 25.4 mm needed). So a carrier that **widens fast near the front** (matching
the blunt nose: 25.4 mm at the flat → ~48 mm by 20 mm aft → ~54–56 mm at the aft end)
holds the SoM. A *gentle linear* taper does not (§4); a **fast-widening** trapezoid,
roughly following the nose profile, does. Exact outline still wants a FreeCAD trace of
the inner wall on the tilted board plane, but feasibility is confirmed.

## 5. Initial two-sided fit (valid footprints)

Board area on a 25.4→60 mm × 69.85 mm trapezoid ≈ (25.4+60)/2 × 69.85 ≈ **2983 mm²
per side** — ample by area for a 2-sided layout. Fit by *shape*:

| Part | Footprint | Fits the taper? |
| --- | --- | --- |
| SoM phyCORE-AM62A | 40×40 (clean-room fp NOT yet authored — PHYTEC mech drawing) | only if wide end ≥60 mm (§4) |
| KSZ9477 | TQFP-128 14×14 | ✅ anywhere aft of the 14 mm-wide station |
| MSPM0G3507 | QFN-48 7×7 | ✅ |
| SLB9670 | QFN-32 5×5 | ✅ |
| ISOW1044 | DFM-20 (fp TBD — TI mech drawing) | ✅ by size (~10×7) |
| EMI (magnetics/CMC/TVS), JST conns, DS lands, passives | real KiCad fps | ✅ |

**Placement intent (2-sided):** front = SoM at the aft/wide end + the sensor
direct-solder lands / JSTs at the forward/narrow end; back = KSZ9477, MSPM0, SLB9670,
ISOW1044, EMI, and network connectors at the aft end. Every part except the SoM is
size-compatible with the taper; **the SoM is the sole fit driver** and gates the
wide-end width.

**Two footprints still block a real placement:** the SoM 270-pad DSC land (needs the
PHYTEC hardware-manual mechanical drawing — the SnapEDA `.kicad_mod` is gitignored/
not-republishable) and the ISOW1044 DFM-20 land (TI package drawing). Until those
exist, the fit is by keep-out only.

## 6. Recommendation

**Resolved (§4.1): the SoM lives on the nose board.** The concrete trapezoid:

- **Narrow (fwd/sensor) end: 25.4 mm** at hull Y −300 (fixed by the flat + aperture span).
- **Wide (aft) end: ~54 mm** at hull Y −230 (fits the ~58 mm usable interior with margin).
- **Widen fast near the front** to reach ~40 mm width by the SoM forward edge (Y −270),
  matching the blunt nose — a straight 25.4→54 taper leaves the SoM's forward corners
  ~1–3 mm proud, so either bump the aft end toward ~58 mm (interior allows it) or use a
  two-segment / nose-following edge that widens faster in the first ~20 mm.
- **Length: 69.85 mm** (unchanged) works; the board need not grow.

Remaining gates for a *physical* placement (not geometry): the **SoM 270-pad DSC
footprint** (PHYTEC mechanical drawing) and the **ISOW1044 DFM-20 footprint** (TI
drawing). With those, the two-sided layout in §5 is straightforward; the outline's exact
inner-wall follow is a FreeCAD refinement.

*© 2026 Steve Griffing — CC BY 4.0.*
