# Vera Nose PCB — Trapezoid Definition & Two-Sided Fit Analysis

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**AI-assist:** Claude Opus 4.8 (Anthropic) — geometry derivation, 2026-07-12
**License:** CC BY 4.0
**Revision:** Rev A (2026-07-12)

Derives the Vera nose-carrier trapezoid from the airframe SCAD geometry
(`airframe/openscad/fuselage/head_shell24.scad`, `bow_sensor_faceplate.scad`,
`bow_sensor_pod.scad`) and reports an initial two-sided component-fit check.

## 1. Anchor geometry (from SCAD, part-local/SCAD frame)

- **Bow mounting flat:** ~26.4 × 15 mm planar face on the 40° bow flat
  (`bow_sensor_pod.scad`); the three apertures fit in one row, span ~25.5 mm.
- **`FACEPLATE_CTR` = [162.15, −282.53, 55.59]** (aperture-row centroid);
  **`BOW_CX` = 161.33** (aircraft CL). Nose tip ≈ Y −287.7; head aft (cargo mate)
  ≈ Y −53; head lateral extent X 99..228 (129 mm at the widest, aft).
- **Vera mount** (`head_shell24.scad vera_board_bosses`): station ≈ `FACEPLATE_CTR
  + 20 mm` aft (into the hull), level with the sensor cluster. *(That module still
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
the SCAD bounding box (CLAUDE.md: bounding-box/centroid placement is inadequate for
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
direct-solder lands / JSTs at the forward/narrow end; back = KSZ9477 + MSPM0 + SLB9670
+ ISOW1044 + EMI + network connectors at the aft end. Every part except the SoM is
size-compatible with the taper; **the SoM is the sole fit driver** and gates the
wide-end width.

**Two footprints still block a real placement:** the SoM 270-pad DSC land (needs the
PHYTEC hardware-manual mechanical drawing — the SnapEDA `.kicad_mod` is gitignored/
not-republishable) and the ISOW1044 DFM-20 land (TI package drawing). Until those
exist, the fit is by keep-out only.

## 6. Recommendation

Resolve the **wide-end width vs. nose interior** first (FreeCAD cross-section of
`head_shell24` at the Vera aft station), because it decides whether the SoM lives on
the nose board at all (§4 options). The 25.4 mm narrow end is fixed regardless.

*© 2026 Steve Griffing — CC BY 4.0.*
