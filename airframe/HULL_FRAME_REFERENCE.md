# Airframe Hull-Frame and Canonical-Accuracy Reference

Governing file: `airframe/AGENTS.md` — this document holds the reference data (bake workflow,
canonical-accuracy authority order, validated baked extents) that `airframe/AGENTS.md` points
to. For project-wide standards see the root `AGENTS.md`.

## Bake Workflow (if you regenerate primary STLs)

As of R1 (2026-06-11), validated component placements are **baked into the published STL vertex
data** by `tools/bake_hull_frame.py` (binary header marker: `SerenityUAV HULL-FRAME R1`). Every
primary STL in `airframe/stls/` is stored **directly in hull-frame coordinates** and imports
into FreeCAD with **identity placement**. Do not apply per-part transforms when positioning
these components.

```sh
python3 tools/bake_hull_frame.py            # all components (idempotent)
python3 tools/bake_hull_frame.py --check    # report baked state only
```

Never bake a mesh *derived from* an already-baked file (e.g. a Blender repair of a baked STL
loses the header marker).

## Canonical Accuracy References (Ground Truth)

When judging whether hull/exterior geometry is faithful to the real ship, treat the
`docs/references/` library as ground truth, in this authority order (highest first):

1. **QMx *Official Serenity Blueprints Reference Pack* (2007)** —
   `docs/references/The_Official_Serenity_Blueprints_Reference_Pack.pdf` (REFERENCES.md
   REF-CAD-003). **Most authoritative** — officially licensed, production-derived canon. Where it
   disagrees with any other reference on canonical shape/proportion, **it wins.** Drawn at line-art
   fidelity, so it lacks fine mechanical detail. Copyrighted commercial product — reference only;
   never redistribute or relicense it.
2. **Nick Henning render collection** — `docs/references/nick-henning/` (REF-CAD-002). Derived from
   the show/QMx canon; carries **more mechanical/surface detail** than the blueprints. Use it where
   the blueprints are ambiguous. Used by email permission (2026-07-06).
3. **misubisu Thingiverse model, Thing 7330462** — `docs/references/thingverse-serenity/`
   (REF-CAD-004, CC BY-SA 4.0 — Available Component under CERN-OHL-W 2.0, see
   `docs/attribution_and_licencing.md` §3). The **origin of the `s_*.stl` geometry** in
   `airframe/stls/`. It is the
   working starting point, but **verify any detail against the two sources above before treating it
   as canonical** — it is the lowest-authority of the three.

This ranking is mirrored in `REFERENCES.md` ("Creative-Universe Attribution and Fan-Engineering
Terms" → "Canonical-Accuracy Reference Hierarchy") and `docs/AGENTS.md`. These references are the
arbiter of what "canonical" means; keep the canonical outer mold line intact per "Geometry
Integrity" in `airframe/AGENTS.md`.

## Validated Baked Extents (hull frame, mm — updated 2026-06-13)

| Component | X min..max | Y min..max | Z min..max |
| --- | --- | --- | --- |
| Head_Shell | −232.9..−103.5 | −305.7..−70.7 | +61.1..+201.5 |
| Cargo_Shell | −267.0..−72.7 | −71.5..+132.0 | 0.0..+163.2 |
| Middle_Shell | −258.5..−81.6 | +130.4..+203.6 | +1.3..+166.1 |
| Rear_Shell | −246.1..−105.5 | +203.2..+384.3 | +3.3..+161.1 |
| Wing_Port | −93.0..+6.7 | −7.0..+122.0 | +48.0..+77.0 |
| Wing_Stbd | −345.2..−245.5 | −7.0..+122.0 | +48.0..+77.0 |
| Nacelle_Port | +4.0..+86.0 | −58.2..+108.3 | +21.4..+104.7 |
| Nacelle_Stbd | −428.1..−346.1 | −64.2..+102.3 | +23.3..+106.6 |

**Wings, Rev S1c (2026-08-18).** `Wing_Stbd` was re-baked as a true mirror of `Wing_Port`; it
had been 5.0 mm aft-of-mirror in Y and 4.5 mm outboard in X, which put the starboard spar out of
line with the single `WING_SPAR_Y` the cargo shell cuts both sides on. Both wings now share
Y −7.0..+122.0 and mirror about the hull symmetry plane measured at the spar station,
X = −169.241 (residual 0.0000 mm) — see the Wing entries in `tools/bake_hull_frame.py` for the
derivation. The `Wing_Port` X maximum also moves +4.7 → +6.7: the recorded figure predated the
wingtip mount pad, which stands `TIP_PAD_PROUD` = 2.0 mm past the tip face.

Use these validated orientations and positions to determine where parts fit in space; bounding
boxes and centroid calculations are inadequate for Serenity's geometry. If placement is
uncertain, request manual placement in FreeCAD by the user.
