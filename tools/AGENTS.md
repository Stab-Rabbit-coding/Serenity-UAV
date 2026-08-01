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

### Hull-Frame Bake Tool

**File:** `tools/bake_hull_frame.py`  
**Purpose:** Bake validated coordinate transforms into STL binary header data

The R1 workflow stores all primary fuselage and component STLs **directly in hull-frame coordinates** with transforms baked into the binary STL vertex data. This eliminates the need for per-part placement transforms in FreeCAD; all primary components import with identity placement.

**Usage:**
```sh
python3 tools/bake_hull_frame.py            # bake all components (idempotent)
python3 tools/bake_hull_frame.py --check    # report baked state only
```

**Output:**
- All STLs in `airframe/stls/` receive the binary header marker: `SerenityUAV HULL-FRAME R1`
- Transform data is baked into vertex coordinates
- Tool refuses to bake an already-marked file (idempotent — cannot double-apply)

**Important:** Never bake a mesh *derived from* an already-baked file (e.g., a Blender repair of a baked STL loses the header marker and should not be re-baked).

**Historical transforms:** The bake transforms (position + quaternion per component) are defined in `tools/bake_hull_frame.py` `COMPONENTS` dictionary — do not duplicate them elsewhere in the codebase.

### SCAD and STL Generation

Generator scripts may model parts in convenient part-local frames, but any **regenerated primary-component STL must be re-baked before publishing**.

**General workflow:**
1. Edit source SCAD file
2. Run SCAD to generate STL (or use Blender pipeline)
3. Validate mesh for watertight surface and no voids
4. Verify bore diameter and Z-range match specification (console output from SCAD)
5. Run bake tool: `python3 tools/bake_hull_frame.py`
6. Commit the updated STL and baked header marker

### Blender Hollowing Pipeline

**Directory:** `airframe/blender-scripts/files-hollowed-24in/`  
**Purpose:** Generate canonical fuselage shells (authoritative source for all fuselage geometry)

The Blender hollowing pipeline is the **authoritative canonical source** for all fuselage geometry. Any future changes must start from the corresponding Blender source file in `files-hollowed-24in/`.

**Usage:**
```sh
blender --background --python <script>.py
```

**Pipeline steps:**
1. Update source in `airframe/blender-scripts/files-hollowed-24in/`
2. Copy updated file to `airframe/stls/fuselage/` (or `fuselage/cargo/` for cargo)
3. Run bake tool: `python3 tools/bake_hull_frame.py`
4. Verify Z-range and bore-diameter in console output before committing

**Output locations:**
- Fuselage shells: `airframe/stls/fuselage/`
- Nacelles: `airframe/stls/nacelles/`
- Wings: `airframe/stls/wings/`

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

### FreeCAD Assembly Script

**File:** `airframe/FreeCAD-scripts/serenity_assembly.py`  
**Purpose:** Headless assembly of all components with correct placement

Generates the canonical assembly `airframe/freecad/assembly/SerenityAssembly.FCStd` by:
- Loading all baked primary STLs
- Placing them at identity (no transforms needed)
- Setting up internal bonding networks and cable routing guides

**Usage:**
```sh
freecadcmd airframe/FreeCAD-scripts/serenity_assembly.py
```

### Project/Archive Index Agent

**File:** `tools/precommit_index.py`
**Purpose:** Keep `PROJECT_INDEX.md` and `ARCHIVE_INDEX.md` (root AGENTS.md §10) in sync with
the actual file tree, with cross-functional tags for low-token AI-agent lookup.

Wired into `.githooks/pre-commit` and the `index-check` CI job (`.github/workflows/ci.yml`); runs
on every commit and in CI. Fully regenerates both Markdown indexes and `tools/index_tags.json`
from scratch every run (never append-only patches) — this is deliberate: the earlier append-only
generator silently corrupted both files for months (renamed/archived paths dropped their entry's
first line but left wrapped description lines orphaned forever; see git history of this file and
`docs/DOCUMENTATION_RECONCILIATION_2026-07-28.md` item 2). A file is classified **archived** if
any path component is literally `archive` or `archives`; everything else tracked is **active**,
including `deferred/` (future work, not superseded work).

Each entry gets a one-line description mined from the file itself (Markdown H1, Python docstring,
OpenSCAD/C header comment, STL binary header marker, BOM row/item count) and a set of tags:

- **One domain tag** from its top-level directory (`structural`, `avionics-hardware`, `firmware`,
  `pcb-design` via extension, etc.)
- **Cross-functional capability tags** from a path-keyword table (`security`, `emi-hardening`,
  `redundancy-failover`, `comms-protocol`, `power`, `propulsion`, `sensors-vision`,
  `landing-gear`, `fabrication`, `licensing`, …). For the three AGENTS.md §1 non-negotiables
  (`security`, `emi-hardening`, `redundancy-failover`) that show up mostly in prose rather than
  filenames, the generator also scans a leading slice of Markdown/Python/C/SCAD/DTS file content
  for the same keywords — deliberately limited to just those three tags, so a broad WBS/TODO file
  doesn't get flooded with every topic it merely mentions.

Each Markdown index opens with a **Tag Index**: one line per tag listing every file carrying it,
so an agent can `grep` a single tag name and get the exact file list without reading the rest of
the (much smaller, post-rewrite) document. `tools/index_tags.json` holds the same
`path -> {description, tags, archived}` and `tag -> [paths]` data for programmatic lookup.

**Usage:**
```sh
python3 tools/precommit_index.py            # regenerate PROJECT_INDEX.md / ARCHIVE_INDEX.md /
                                             # tools/index_tags.json and write them
python3 tools/precommit_index.py --check    # exit 1 if the indexes would change (CI gate)
```

To change how entries look (a new tag, a new file-type description rule), edit the generator —
never hand-edit `PROJECT_INDEX.md` or `ARCHIVE_INDEX.md` directly; the next commit's pre-commit
hook overwrites hand edits.

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

## Output Locations

| Output Type | Directory | Format |
| --- | --- | --- |
| Fuselage STLs | `airframe/stls/fuselage/` | Binary STL (baked) |
| Nacelle STLs | `airframe/stls/nacelles/` | Binary STL (baked) |
| Wing STLs | `airframe/stls/wings/` | Binary STL (baked) |
| SCAD sources | `airframe/openscad/` | OpenSCAD `.scad` |
| Blender sources | `airframe/blender-scripts/files-hollowed-24in/` | Blender `.blend` |
| FreeCAD assembly | `airframe/freecad/assembly/` | FreeCAD `.FCStd` |
| PCB Gerbers | `avionics/gerbers/` | Gerber RS-274X format |
| Documentation | `docs/` | Markdown `.md` or PDF |

## Validation and Quality Checks

### Pre-Commit Checklist

Before committing any generated files:

**For STL files:**
- [ ] Mesh validation passed (watertight, no voids)
- [ ] Bake tool has been run and file carries header marker
- [ ] Z-range verified against specification
- [ ] Bore diameter verified against specification (if applicable)
- [ ] File size is reasonable (not excessively large or small)

**For SCAD files:**
- [ ] Syntax is correct (no parse errors)
- [ ] Generated STL validates cleanly
- [ ] Comments are verbose and follow OpenSCAD conventions
- [ ] 4-space indentation throughout

**For KiCad files:**
- [ ] Electrical Rules Checker (ERC) passes
- [ ] Design Rules Checker (DRC) passes (or violations are documented in TODO.md)
- [ ] Gerber files are production-ready
- [ ] Schematics and PCB are in sync

**For Blender scripts:**
- [ ] Script executes headless without errors
- [ ] Output STL is correct
- [ ] Hollowing parameters are correct (2.0 mm wall, watertight)

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
