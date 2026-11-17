# Tools and Build Automation — Agent Instructions

Adds tooling rules to root `AGENTS.md`, which wins wherever it speaks. Scope: build tools,
validators, generators, and utilities (STL/SCAD generation, hull-frame baking, mesh and KiCad
validation, Gerber preparation, assembly documentation, index and TODO generation).

## Authoritative Reference

**`tools/TOOL_REFERENCE.md`** is the usage reference for every build tool: the hull-frame bake,
SCAD/STL generation, the Blender hollowing pipeline, the FreeCAD assembly script, output
locations, and per-file-type pre-commit checklists. Read it before running or changing a tool.

Gates run by `.githooks/pre-commit` and CI (root `AGENTS.md` §7, §10): `validate_stls.py`
(mesh), `validate_kicad.py` (ERC/DRC), `check_datum_drift.py`, `check_bom_mesh_sync.py`,
`check_hull_tarballs.py`, `check_agents_size.py`, `gen_todo_from_wbs.py --check`, and
`precommit_index.py` (regenerates the indexes; never hand-edit them).

## Script Standards

Python build tools (new tools shall meet these; bring an existing tool up to them when you
change it):

- An `if __name__ == "__main__":` guard and `argparse` (or similar) arguments.
- `--help` prints usage with an example and does not run the tool.
- Progress to stdout; a non-zero exit code on error.
- Dependencies (Python packages, Blender or FreeCAD version) stated in the module docstring.
- A test under `tools/tests/` for any check that gates commits.

Blender and FreeCAD scripts run headless (invocations in `tools/TOOL_REFERENCE.md`; no X11
display needed). Blender scripts print progress and validation results to stdout and save STLs
to the documented location; FreeCAD scripts produce assembly documents ready for measurement.

## Work Tracking

Tools live flat in `tools/` (tests in `tools/tests/`). Record known limitations and open work in
the owning subsystem's `WBS.md` (this folder owns no WBS branch; `docs/WBS_FEDERATION.md`).
