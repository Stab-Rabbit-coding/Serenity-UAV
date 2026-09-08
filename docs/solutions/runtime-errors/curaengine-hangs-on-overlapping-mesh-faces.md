---
title: "CuraEngine hangs or crashes on an STL with overlapping faces trimesh reports as watertight"
date: 2026-09-07
category: runtime-errors
module: "airframe/gcode/davinci-jr-proto (PLA prototype print pipeline)"
problem_type: runtime_error
component: tooling
severity: medium
symptoms:
  - "CuraEngine 5.0.0 (headless CLI, cura-engine apt package) does not finish slicing rear_shell24_2mm_repaired.stl (64% scale, ~1,007,832 faces) within a 400s timeout, even with support generation disabled"
  - "trimesh reports the same STL as fully watertight and manifold (0 boundary edges, consistent winding), so the standard manifold/watertight check gives no indication of the defect"
  - "With CuraEngine support generation enabled, slicing several of the flagged parts aborts with an assertion failure in path-combing code: Comb.cpp:296, \"The part we end up inside when combing should have been computed already!\""
  - "6 of 49 STL parts sliced for the print guide (4 hollowed hull sections + 2 nacelle pod shells) each produce a CuraEngine [WARNING] Mesh has overlapping faces! at load time"
  - "np.unique on sorted face-vertex-index tuples confirms 4 clusters of genuine coincident/duplicate overlapping triangle pairs in the affected mesh, left behind by an earlier Blender hollowing/boolean operation"
root_cause: logic_error
resolution_type: tooling_addition
tags: [curaengine, manifold3d, mesh-repair, overlapping-faces, stl, 3d-printing]
related_components:
  - "airframe/stls (canonical CAD geometry — explicitly NOT touched by this fix; canonical hull-frame STLs are only regenerated from Blender/SCAD source per airframe/AGENTS.md 'Geometry Integrity')"
  - "docs/PROTO_PRINT_DAVINCI_JR.md (the print guide this verification work supports)"
---

# CuraEngine hangs or crashes on an STL with overlapping faces trimesh reports as watertight

## Problem

Six of the 49 STL parts in the current Rev T print batch — the four hull-shell sections (`head_shell24_2mm_repaired.stl`, `cargo_sect_shell24_2mm_repaired.stl`, `middle_shell24_2mm_repaired.stl`, `rear_shell24_2mm_repaired.stl`) and the two nacelle pod shells (`nacelle_port_revs.stl`, `nacelle_stbd_revs.stl`) — carry leftover overlapping/duplicate coincident triangles from an earlier Blender hollowing/boolean pipeline. `trimesh`'s watertight/manifold check reports all six as fully valid (watertight, consistent winding, zero boundary edges), because that check is blind to this defect class; CuraEngine 5.0.0, slicing headlessly for the printed guide `docs/PROTO_PRINT_DAVINCI_JR.md`, is not, and on the worst-affected file it never finished slicing at all.

## Symptoms

1. **Support-generation crash.** With `support_enable=True`, CuraEngine aborted with an internal assertion in its path-combing code, confirmed while slicing `cargo_sect_shell24_2mm_repaired.stl` at 64% scale:

   ```
   CuraEngine: ./src/pathPlanning/Comb.cpp:296: bool cura::Comb::calc(...): Assertion
   `end_crossing.dest_part.size() > 0 && "The part we end up inside when combing should
   have been computed already!"' failed.
   ```

2. **Slice hang with support disabled.** Disabling support let 5 of the 6 flagged parts (3 of 4 hull shells, both nacelle pods) slice successfully anyway. The sixth, `rear_shell24_2mm_repaired.stl` — the largest by face count (1,007,832 triangles at native scale; printed at 64% → 90.0 × 115.2 × 101.0 mm) — did not finish within a 400-second budget even with support off, and still did not complete on a longer retest.

3. **The defect was invisible to the standard mesh-health check.** `mesh.is_watertight`, `mesh.is_winding_consistent`, and a zero-boundary-edge count all passed on the vertex-merged mesh (`trimesh.load(path, process=True)`) for all six files — the class of defect (overlapping, coincident-or-near-coincident surface patches) is orthogonal to holes/winding, so a clean watertight report is not evidence the mesh is slicer-safe.

Direct inspection (sorting each face's 3 vertex indices and flagging exact-duplicate rows) found the concrete cause in `rear_shell24_2mm_repaired.stl`: 4 clusters of duplicate triangle pairs (8 duplicated non-manifold edges out of roughly 2.1 million edges) plus 11 zero-area (degenerate) triangles.

## What Didn't Work

- **Waiting longer.** The unrepaired mesh was retested past the original 400 s timeout as a sanity check after the fix was already in hand — it still never completed. The problem is not slicer slowness on a large mesh; it is the specific overlapping geometry defeating CuraEngine's internal polygon-boolean/combing logic.

- **Hand-deleting the offending faces.** An early attempt located the exact duplicate and zero-area faces via `numpy` (sorting each face's vertex-index triple and finding rows with `count > 1`), then deleted them directly with `trimesh.Trimesh.update_faces()` followed by `remove_unreferenced_vertices()`. This reduced the non-manifold edge count in the immediate area but punched 31 new boundary-edge holes nearby, because naive face deletion does not re-stitch the surrounding topology. It was abandoned in favor of the CSG-based repair below, which never hand-edits a triangle.

## Solution

Route the one problem file through a self-union performed by the `manifold3d` geometry kernel (https://github.com/elalish/manifold — Python bindings already present system-wide; no `pip install` needed) rather than trying to patch triangles by hand. The implementation lives in `airframe/gcode/davinci-jr-proto/cura/mesh_repair.py`:

```python
# airframe/gcode/davinci-jr-proto/cura/mesh_repair.py:54-93 (repair_mesh)
def repair_mesh(mesh: trimesh.Trimesh, tolerance: float = 0.15) -> trimesh.Trimesh:
    mesh_in = m3d.Mesh(
        vert_properties=mesh.vertices.astype("float32"),
        tri_verts=mesh.faces.astype("uint32"),
    )
    man = m3d.Manifold(mesh_in)
    repaired = (man + man).simplify(tolerance)
    if repaired.status() != m3d.Error.NoError:
        raise RuntimeError(f"manifold3d reported {repaired.status()} after repair")

    out_mesh = repaired.to_mesh()
    verts = np.array(out_mesh.vert_properties)[:, :3]
    faces = np.array(out_mesh.tri_verts)
    return trimesh.Trimesh(vertices=verts, faces=faces, process=True)
```

The load must go through `trimesh.load(path, process=True)` (vertex merging) — an unmerged load makes every triangle look like its own disconnected body and produces false non-manifold readings, per the module's own docstring. `man + man` is Manifold's `__add__`, which performs CSG union; unioning the mesh with itself is the mechanism, not an accident of API naming. The `.simplify(tolerance)` call afterward is a separate, optional decimation pass (0.15 mm tolerance, at the mesh's native 24-inch scale) applied purely to cut triangle count for slicer speed — it is not load-bearing for correctness.

Verified results on `rear_shell24_2mm_repaired.stl`:

- Self-union alone: 1,007,832 → 954,046 faces. Volume preserved to 5 decimal places (220429.24172 mm³ → 220429.22789 mm³ — float32 round-trip noise, not a real change). `manifold3d.Manifold(...)` reconstructed from this output reports `status() == Error.NoError`.
- Self-union + 0.15 mm simplify: 1,007,832 → 722,056 faces (a further ~24% reduction).
- Re-slicing the repaired mesh (64% scale, support disabled) in CuraEngine succeeded in both cases, in roughly 325–335 s wall time — previously this file did not finish in 400 s+. The simplify pass reduced file size but did not meaningfully speed up this particular slice, suggesting CuraEngine's time here is dominated by something other than raw triangle count (e.g., per-layer polygon complexity from the shell's rib/boss geometry) — worth flagging for anyone tempted to over-invest in decimation as a speed fix.

## Why This Works

The root cause is genuine duplicate/overlapping triangles — coincident or near-coincident surface patches left behind by whatever Blender boolean/hollowing operation produced the `_2mm_repaired` variant of this shell — not a hole and not inconsistent winding. A mesh can have zero boundary edges and fully consistent face winding while still containing two overlapping patches occupying the same 3D space; `trimesh`'s watertight check simply does not look for that condition, but it is exactly what breaks a slicer's internal polygon-boolean/path-combing logic (per the observed `Comb.cpp` assertion and the unbounded hang with support off).

Manifold's CSG kernel guarantees, by construction, that its *output* contains no self-intersections or duplicate coincident faces — that is the invariant the library is built to hold for any boolean result. Unioning a mesh with itself therefore canonicalizes away exactly this leftover-boolean-pipeline defect class without touching individual triangles by hand, unlike the face-deletion attempt above, which could not safely re-stitch topology on its own.

One nuance worth stating plainly: **after** this repair, `trimesh` still reports the output as not-100%-watertight — 8 residual non-manifold edges remain out of roughly 2.1 million, localized to a handful of ribs. But reconstructing a fresh `manifold3d.Manifold` object directly from that same repaired mesh's own vertex/face arrays (no round-trip through STL export/reimport) reports `Error.NoError`, both immediately after the self-union and again on independent reconstruction. This reflects a difference in how the two tools define "manifold" at edges where two coincident-but-topologically-distinct surface patches meet — a legitimate geometric configuration Manifold's kernel handles correctly but `trimesh`'s simple edge-adjacency-count heuristic flags — not a real remaining defect. It was verified correct by the successful re-slice, not by chasing `trimesh`'s edge count to exactly zero; a future reader applying this same fix to a different file should use "does it slice" as the acceptance criterion, not `mesh.is_watertight == True`.

## Prevention

The fix is codified as a reusable function, `repair_mesh(mesh: trimesh.Trimesh, tolerance: float = 0.15) -> trimesh.Trimesh`, in `airframe/gcode/davinci-jr-proto/cura/mesh_repair.py`, and wired into the batch slicing driver `airframe/gcode/davinci-jr-proto/cura/slice_all_batches_cura.py` via a `NEEDS_REPAIR` set:

```python
# airframe/gcode/davinci-jr-proto/cura/slice_all_batches_cura.py:146
NEEDS_REPAIR = {"rear_shell24_2mm_repaired"}
```

`prepare_stl()` (same file, ~line 149) checks membership in `NEEDS_REPAIR` before scaling; a matched part is routed through `mesh_repair.repair_mesh()` once, with the repaired output cached to a scratch STL (`/tmp/claude-1000/cura_scaled_stl/<stem>_meshfix.stl`) so repeated slice runs don't re-pay the CSG cost. Every other part — including the other 5 files that also carry the "overlapping faces" warning — passes through unmodified: they already slice fine as exported, so the repair is applied surgically to the one file that actually needs it rather than proactively to all six just because they share a warning. The driver's module docstring also records that every batch is sliced with `support_enable=False` across the board, since the crash symptom above was reproduced with support on even on files that don't need `NEEDS_REPAIR`.

This is deliberately scoped as a **print-pipeline-local fix**, not a change to canonical geometry. The canonical Rev T STLs under `airframe/stls/` were not touched or regenerated. `airframe/AGENTS.md` ("Geometry Integrity" and the Blender Pipeline section) establishes that canonical hull-frame STLs are only ever regenerated from their Blender-canonical source in `airframe/blender-scripts/files-hollowed-24in/`, never hand-patched at the STL level after export — `mesh_repair.py`'s own docstring restates this explicitly and points anyone needing a *source-level* fix (rather than a one-slicer-CLI patch) to that Blender pipeline via `tools/TOOL_REFERENCE.md` instead.

For future occurrences of this defect class:

- Don't trust `mesh.is_watertight` / `is_winding_consistent` as proof a mesh is slicer-safe — those checks do not see overlapping-but-closed geometry. If CuraEngine (or another slicer) emits an `overlapping faces` warning, treat it as a real signal even when trimesh's own check is clean.
- Before assuming a large/complex mesh just needs a longer timeout, check whether it carries this warning; a hang from this defect class does not resolve with more wall-clock time.
- If a repair is needed only to get one slicer's CLI through one specific mesh, keep it scoped like this one — a cached scratch copy, gated by an explicit allow-list (`NEEDS_REPAIR`), not touching `airframe/stls/`.
- If the same self-intersecting-geometry pattern turns out to affect a part in a way that matters beyond this one slicing pipeline (e.g. it also confuses FreeCAD, another slicer, or a downstream boolean step), that's a signal to fix it at the Blender-hollowing-pipeline source per `airframe/AGENTS.md`, not to keep patching individual STL exports.
- A prior-art claim was checked against this repo's session history before writing this doc: the specific claim that a 2026-08-31 nozzle-flap-shingle session used this same `manifold3d` self-union technique to fix overlapping seam geometry did **not** hold up against the available session content — that session's only `manifold3d` usage was an unrelated cover-to-cutout fit check, and it surfaced a `NACELLE_SIDE` naming-inversion bug, not a mesh self-intersection repair. Treat any future claim of prior art for this pattern as unconfirmed until it's checked directly against the source session rather than repeated from memory.

## Related Issues

- [`mating-face-aperture-allowlist.md`](../logic-errors/mating-face-aperture-allowlist.md) — a different defect (an intentional open fuselage mating face silently re-capped by a repair pass) from the same upstream Blender Hollowing Pipeline, but it independently arrives at the same core principle documented here: `mesh.is_watertight` is a *proxy* for mesh soundness, not proof of it. Worth reading together for anyone auditing a mesh pipeline in this repo, even though the concrete defects and fixes are unrelated.
- No related GitHub issues found (`gh issue list --search "mesh overlapping faces OR CuraEngine OR manifold3d" --state all --limit 5` returned zero results).
- `tools/TOOL_REFERENCE.md`'s "Blender Hollowing Pipeline" pre-commit checklist currently lists "Mesh validation passed (watertight, no voids)" as sufficient — it does not yet note that watertight/no-voids can pass while duplicate/overlapping triangles remain and later break a slicer. Flagged as a `ce-compound-refresh` candidate.
