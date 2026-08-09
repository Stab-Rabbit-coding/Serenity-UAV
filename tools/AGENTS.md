# Tools and Build Automation — Agent Instructions

> *See the root `AGENTS.md` for project-wide policies. This file provides specific guidance for build scripts, automation tools, and code generation.*

## Scope

This folder contains all build tools, automation scripts, utilities, and code generators used to:

- Generate or regenerate STL and SCAD files from source models
- Bake coordinate transforms into STL header data
- Validate meshes and design artifacts
- Prepare PCB Gerber files for fabrication
- Generate assembly documentation

## Core Build Tools

**`tools/TOOL_REFERENCE.md`** is the authoritative usage reference for each tool — read it
before running or modifying any of them. It covers:

- **`tools/bake_hull_frame.py`** — hull-frame bake tool: usage (`--check`), the
  `SerenityUAV HULL-FRAME R1` header marker, idempotency, the `COMPONENTS` transform dictionary,
  and the rule that a mesh *derived from* an already-baked file is never re-baked
- **SCAD and STL generation** — the six-step edit → generate → validate → verify → bake → commit
  workflow; any regenerated primary-component STL must be re-baked before publishing
- **Blender hollowing pipeline** — `airframe/blender-scripts/files-hollowed-24in/` is the
  authoritative canonical source for all fuselage geometry; headless usage and pipeline steps
- **`airframe/FreeCAD-scripts/serenity_assembly.py`** — headless assembly of
  `airframe/freecad/assembly/SerenityAssembly.FCStd` at identity placement
- **`tools/precommit_index.py`** — regenerates `PROJECT_INDEX.md`, `ARCHIVE_INDEX.md`, and
  `tools/index_tags.json` from scratch on every commit and in CI; never hand-edit those indexes
- **Output locations** table and the per-file-type **pre-commit checklists** (STL, SCAD, KiCad,
  Blender)

### Mesh Validation

Every 3D model modification requires mesh verification:

1. Run mesh validation tools (Blender checker, SCAD diagnostics, or dedicated validation utility)
2. Report all findings to `TODO.md` with specific violations
3. Resolve all violations before committing

**Validation checks:**

- Watertight surface (no voids, no open edges)
- Consistent face normals (all pointing outward)
- No self-intersecting geometry
- Proper manifold topology

## Script Execution Standards

### Python Scripts

- All Python build tools shall have a `__main__` block for direct execution
- Use `if __name__ == '__main__':` guard
- Accept command-line arguments via `argparse` or similar
- Provide `--help` output with usage examples
- Log progress to stdout
- Return non-zero exit code on error

### Blender Scripts

- Execute headless: `blender --background --python <script>.py`
- Machine supports headless execution (no X11 display required)
- Print progress and validation results to stdout
- Save output STLs to the correct location

### FreeCAD Scripts

- Execute headless: `freecadcmd <script>.py`
- Generate assembly documents ready for visualization and measurement

## Work Tracking

When creating or modifying build tools:

1. Add the tool to a logical subdirectory (e.g., `tools/mesh_validation/`, `tools/pcb_prep/`)
2. Include a `README.md` in the subdirectory explaining purpose and usage
3. Ensure all scripts have `--help` output
4. Document any dependencies (Python packages, Blender version, FreeCAD version)
5. Add an entry to `PROJECT_INDEX.md`
6. If the tool is complex or has known limitations, add tracking items to `TODO.md`

---

For project-wide standards, see the root `AGENTS.md`.
