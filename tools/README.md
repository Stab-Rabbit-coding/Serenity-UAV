# Serenity UAV — Build Tools & Validation Scripts

**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0  
**Current design revision:** Rev S (2026-07-04)

> Python and shell scripts for design validation, mesh integrity checking, KiCad PCB/ERC/DRC
> verification, STL export, and repository linting. All tools support the design-to-fabrication
> pipeline.

## Quick Reference

| Tool | Language | Purpose | Input | Output |
|------|----------|---------|-------|--------|
| `validate_stls.py` | Python 3 | Mesh watertightness, manifold topology, normal orientation | STL files | Console report, TODO.md items |
| `validate_kicad.py` | Python 3 | KiCad schematic ERC + PCB DRC for all boards | `avionics/kicad/*/` | ERC/DRC pass/fail, violation report |
| `bake_hull_frame.py` | Python 3 | Embed hull-frame coordinate standard into STL vertex data | Hull/component STLs | Baked STLs (header marker added) |
| `ci.yml` (GitHub Actions) | YAML | CI pipeline: lint, validate, test | Git commits | CI status checks, PR feedback |
| `.super-lintignore` | Text | Exclusion list for super-linter | — | Config (managed by maintainers) |
| `precommit_sanitize.py` | Python 3 | Pre-commit hook to scrub sensitive data from commits | Staged files | Clean commits (no PII, credentials) |

## Core Validation Tools

### `validate_stls.py`

**Purpose:** Verify all STL meshes for watertightness, manifold topology, and correct normals.

**Usage:**

```bash
python3 tools/validate_stls.py --dir airframe/stls/ --report TODO.md
```

**Checks:**

- Mesh is closed (watertight) — no gaps, no internal cavities
- Topology is manifold — each edge shared by exactly 2 triangles
- Normals point outward (checked via cross-products)
- No degenerate triangles (zero-area, self-intersecting)
- Z-range is within expected bounds for each component (prevents accidental scaling)
- STL header comments include design revision and coordinate frame marker

**Output:**

Each failure is logged as a `TODO.md` item (e.g., `MESH-01` for non-watertight fuselage shell).
Passing STLs are reported with their Z-range and vertex count (for tracking physical sizing).

### `validate_kicad.py`

**Purpose:** Run KiCad schematic ERC (electrical rule check) and PCB DRC (design rule check) on all boards.

**Usage:**

```bash
python3 tools/validate_kicad.py --boards "Pilot,XO,FlightEngineer,Observer" --output report.json
```

**Requires:** KiCad ≥9.0 (`kicad-cli` available on PATH)

**Checks:**

- **ERC (Schematic):**
  - No unconnected pins (except labeled NC)
  - No floating nets or duplicate net names
  - Power rails properly terminated
  - No signal conflicts (e.g., driven pins on same node)

- **DRC (PCB Layout):**
  - Trace/via spacing meets design rules (10 mil minimum unless specified)
  - Creepage/clearance distances per IEC 62368-1 (high voltage sections)
  - Via/pad footprints match schematic net assignments
  - No copper-to-edge violations (10 mil setback from board boundary)
  - Impedance-controlled traces (CAN FD, Ethernet) routed per specification

**Output:** JSON report with violations catalogued by board and severity (error / warning).
Violations can be marked as "accepted" in `TODO.md` if justified (e.g., board-level design
tradeoff).

### `bake_hull_frame.py`

**Purpose:** Embed the hull-frame coordinate standard into every primary component STL.

**Usage:**

```bash
python3 tools/bake_hull_frame.py --input airframe/stls/fuselage/ --output airframe/stls/fuselage-baked/
```

**What it does:**

1. Loads each STL and checks its current coordinate system
2. Applies the validated hull-frame transform (if needed)
3. Embeds a header comment in the STL file:
   ```
   SerenityUAV HULL-FRAME R1, origin at SerenityAssembly.FCStd world origin
   ```
4. Writes the baked STL to the output directory

**Why it matters:** FreeCAD and Blender apply their own transforms during import. By baking the
frame directly into vertex data, every tool sees identical coordinates regardless of load order.

**Re-run triggers:**
- After regenerating any primary STL (hull sections, wings, nacelles) from SCAD/CAD
- After moving component placement in the FreeCAD assembly
- Before committing STL updates to ensure consistency

## Build Automation

### GitHub Actions CI (`.github/workflows/ci.yml`)

**Trigger:** Every push to any branch or pull request

**Jobs:**

1. **Lint (super-linter)** — code style, formatting, documentation
   - `PYTHON_BLACK`, `PYTHON_ISORT`, `CLANG_FORMAT`, `MARKDOWN`, etc.
   - Configuration: `.super-lintignore`, `super-linter.yml`

2. **KiCad Validation**
   - Runs `validate_kicad.py` on all `avionics/kicad/*/` boards
   - Uploads ERC/DRC report as artifact

3. **STL Validation**
   - Runs `validate_stls.py` on all `airframe/stls/` meshes
   - Validates coordinate system markers

4. **Python Tests** (if present in `tests/`)
   - pytest with coverage reporting

5. **C/C++ Compile Check**
   - GCC syntax check on firmware files (`avionics/firmware/*/src/`)

**Status:** CI must pass (all checks green) before PR merge. Maintainers can override
documented violations (recorded in `.github/workflows/ci.yml`).

### Pre-Commit Hook (`.githooks/pre-commit`)

**Purpose:** Prevent accidental commits of secrets, large files, or malformed data.

**Checks:**

- No commit messages with "WIP" or "DEBUG" (catches incomplete work)
- No `.env`, `secrets.json`, or API key files
- No STL files >50 MB (likely corrupted or accidentally committed twice)
- No `.o`, `.pyc`, `__pycache__` build artifacts
- Runs `precommit_sanitize.py` to scrub any stray credentials or PII

**Bypass** (with caution):

```bash
git commit --no-verify
```

## Design Scripts (Non-Validation)

Located in subsystem directories:

### Airframe Scripts

- **`airframe/FreeCAD-scripts/serenity_assembly.py`** — FreeCAD Python macro to regenerate the
  master assembly from component STLs
- **`airframe/blender-scripts/serenity_render_views.py`** — Blender headless renderer for
  isometric/cardinal silhouettes (used in build-guide SVG generation)
- **`airframe/stls/fuselage/generate_*.py`** — Per-component generators (head shell, cargo
  doors, access panels)
- **`landing_gear_*.py`** (`_r6_sizing`, `_bay_pad_fit`, `_bay_seat_fit`, `_bay_station_fit`,
  `_cowl_clearance`, `_foot_stance`, `_opening_fit`, `_wing_clearance`) — landing-gear geometry
  fit/clearance checks against the current CAD, one script per constraint
- **`wing_airfoil_variants.py`**, **`wing_cfd_openfoam.py`**, **`wing_spar_station_fit.py`** —
  wing airfoil/CFD/spar-fit tooling
- **`add_landing_gear_bosses.py`**, **`build_head_shell.py`**, **`build_landing_gear_views.py`**,
  **`export_landing_gear_stls.py`**, **`open_mating_faces.py`**,
  **`purge_stale_fcstd_objects.py`**, **`verify_bow_pod.py`** — additional airframe CAD
  generation/maintenance scripts; see each script's own docstring for usage

### Avionics Scripts

- **`avionics/kicad/<Board>/scripts/gen_<board>_sch.py`** — Parametric KiCad schematic
  generator, one per board (e.g. `avionics/kicad/Commo/scripts/gen_commo_sch.py`)
- **`avionics/kicad/<Board>/scripts/mod_<board>_pcb*.py`** — PCB layout modification scripts
  (footprint placement, net routing templates), e.g.
  `avionics/kicad/Commo/scripts/mod_commo_pcb.py`,
  `avionics/kicad/Pilot/scripts/mod_pilot_pcb_reconcile.py`,
  `avionics/kicad/FlightEngineer/scripts/mod_flight_engineer_pcb_revs1.py`
- **`avionics/kicad/export-specctra-dsn.py`** / **`import-specctra-ses.py`** — Specctra DSN/SES
  export/import for external autorouters
- **`avionics/kicad/precommit_kicad_load.py`** — pre-commit KiCad file load/sanity check

### GCS Scripts

- **`gcs/skipper/software/tracking/src/telemetry_feed.py`** — Telemetry decoder for
  QGroundControl
- **`gcs/skipper/software/tracking/src/gimbal_ctrl.py`** — Antenna gimbal servo control
- **`gcs/skipper/software/tracking/src/tracker.py`** — Visual tracking algorithm
  (bearing/elevation from aircraft position)

### Other Maintenance Scripts

- **`compact_bom_entries.py`** — re-compacts `docs/bom_*.json` files
- **`export-specctra-dsn.py`**, **`import-specctra-ses.py`** — see Avionics Scripts above
- **`mirror_claude_memory.py`** — mirrors the AI assistant's memory directory to
  `CLAUDE-MEMORY.md`
- **`precommit_index.py`** — regenerates `PROJECT_INDEX.md`/`ARCHIVE_INDEX.md` (see
  `tools/TOOL_REFERENCE.md`)

## Documentation & References

- **`REFERENCES.md`** — Master catalog of all standards, regulatory citations, supplier links,
  and datasheets
- **`bom_revS.json`**, **`bom_revS.csv`** — Bill of materials with cross-references to
  datasheets and supplier pages

## Development Setup

### Local Tool Installation

```bash
# Clone repo and enter directory
git clone https://github.com/stab-rabbit-coding/serenity-uav.git
cd serenity-uav

# Install Python dependencies
pip install -r requirements-dev.txt

# Install git pre-commit hook
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit

# Verify tools
python3 tools/validate_stls.py --help
python3 tools/validate_kicad.py --help
```

### KiCad Setup (for local ERC/DRC)

```bash
# Install KiCad 9.0 or later
# Ubuntu/Debian: sudo apt install kicad
# macOS: brew install --cask kicad
# Windows: download from https://kicad.org

# Verify CLI availability
kicad-cli version
```

### Blender / FreeCAD (for design rendering)

```bash
# Blender (for silhouettes in build guide)
blender --background --python airframe/blender-scripts/serenity_render_views.py

# FreeCAD (for assembly and component placement)
freecadcmd airframe/FreeCAD-scripts/serenity_assembly.py
```

## Common Tasks

### Generate New STL from SCAD

```bash
# Edit the SCAD source
nano airframe/stls/fuselage/head_shell24.scad

# Render to STL (via OpenSCAD or Blender)
openscad -o airframe/stls/fuselage/head_shell24.stl airframe/stls/fuselage/head_shell24.scad

# Validate the new mesh
python3 tools/validate_stls.py --file airframe/stls/fuselage/head_shell24.stl

# Bake hull-frame coordinate marker if not present
python3 tools/bake_hull_frame.py --input airframe/stls/fuselage/ --output airframe/stls/fuselage-baked/

# Commit
git add airframe/stls/fuselage/head_shell24.stl
git commit -m "Update head shell: [reason]"
```

### Run All Validation Before Committing

```bash
# Full validation pass
python3 tools/validate_stls.py --dir airframe/stls/
python3 tools/validate_kicad.py --boards "*"
python3 -m pytest tests/  # if tests exist

# Check lint (local super-linter equivalent)
black airframe/stls/*.py
isort airframe/stls/*.py
clang-format -i avionics/firmware/cn/src/*.c
```

### Update Bill of Materials

```bash
# Edit the JSON source
nano current-specification/bom_revS.json

# Sync to CSV -- no automated sync script exists yet (tools/update_bom.py is
# not implemented); edit current-specification/bom_revS.csv by hand to match,
# field-for-field, until one is written.

# Commit both
git add current-specification/bom_revS.*
git commit -m "Update BOM: [change reason]"
```

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `validate_stls.py` reports non-manifold | Mesh has T-junction or duplicate vertices | Re-slice in Blender Mesh > Clean Up > Merge by Distance |
| KiCad DRC fails on via size | Via pad < trace width per design rule | Edit via footprint in KiCad PCB Editor; document if intentional |
| Bake hull-frame fails on existing marker | STL already baked to a different origin | Verify origin in FreeCAD; re-export from canonical assembly |
| CI times out on large STL list | Too many meshes to validate in one pass | Split validation into phases (fuselage, nacelles, landing-gear) |
| Pre-commit hook blocks commit | Stray `.pyc` or large file detected | Run `git clean -fd` to remove build artifacts; stage only source files |

## License

All tools and scripts are **CC BY 4.0**.

See root [`LICENSE`](../LICENSE) for details.

---

*"We should go to the cryo-lab. Stare at a lot of ice." — Hoban "Wash" Washburne*
