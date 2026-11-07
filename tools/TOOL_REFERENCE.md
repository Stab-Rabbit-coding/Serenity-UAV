# Build Tool Reference — Usage, Output Locations, and Pre-Commit Checklists

Governing file: `tools/AGENTS.md` — this document holds the per-tool usage reference, the
output-location table, and the pre-commit validation checklists that `tools/AGENTS.md` points
to. For project-wide standards see the root `AGENTS.md`.

## Hull-Frame Bake Tool

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

**CAUTION:** A mesh *derived from* an already-baked file shall not be baked (e.g., a Blender repair of a baked STL loses the header marker).

**Historical transforms:** The bake transforms (position + quaternion per component) are defined in `tools/bake_hull_frame.py` `COMPONENTS` dictionary — do not duplicate them elsewhere in the codebase.

## SCAD and STL Generation

Generator scripts may model parts in convenient part-local frames, but any **regenerated primary-component STL shall be re-baked before publishing**.

**General workflow:**

1. Edit source SCAD file
2. Run SCAD to generate STL (or use Blender pipeline)
3. Validate mesh for watertight surface and no voids
4. Verify bore diameter and Z-range match specification (console output from SCAD)
5. Run bake tool: `python3 tools/bake_hull_frame.py`
6. Commit the updated STL and baked header marker

## Blender Hollowing Pipeline

**Directory:** `airframe/blender-scripts/files-hollowed-24in/`
**Purpose:** Generate canonical fuselage shells (authoritative source for all fuselage geometry)

The Blender hollowing pipeline is the **authoritative canonical source** for all fuselage geometry. Any future changes shall start from the corresponding Blender source file in `files-hollowed-24in/`.

**Usage:**

```sh
blender --background --python <script>.py
```

**Pipeline steps:**

1. Update source in `airframe/blender-scripts/files-hollowed-24in/`
2. Copy updated file to `airframe/stls/fuselage/` (or `fuselage/cargo/` for cargo)
3. Run bake tool: `python3 tools/bake_hull_frame.py`
4. Verify Z-range and bore-diameter in console output before committing

## FreeCAD Assembly Script

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

## Project/Archive Index Agent

**File:** `tools/precommit_index.py`
**Purpose:** Keep `PROJECT_INDEX.md` and `ARCHIVE_INDEX.md` (root AGENTS.md §10) in sync with
the actual file tree, with cross-functional tags for low-token AI-agent lookup.

Wired into `.githooks/pre-commit` and the `index-check` CI job (`.github/workflows/ci.yml`); runs
on every commit and in CI. Fully regenerates both Markdown indexes and `tools/index_tags.json`
from scratch every run (never append-only patches) — this is deliberate: the earlier append-only
generator silently corrupted both files for months (renamed/archived paths dropped their entry's
first line but left wrapped description lines orphaned forever; see git history of this file and
`archives/docs-superseded/DOCUMENTATION_RECONCILIATION_2026-07-28.md` item 2). A file is classified **archived** if
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

## WBS → TODO Generator

**File:** `tools/gen_todo_from_wbs.py`
**Purpose:** Implement the root `AGENTS.md` §10 rule that every `TODO.md` is *generated* from
its owning `WBS.md` — one line per currently-open top-level item, ≤70 characters, headings only
where open work remains, each section pointing back at its `WBS.md` entry. Added 2026-09-15
after two months of hand-patched `TODO.md` files had inverted the federation in places (see
`docs/solutions/workflow-issues/generate-open-item-views-never-hand-patch-them.md`).

Covers all 17 `{WBS,TODO}.md` pairs listed in `docs/WBS_FEDERATION.md` (`PAIRS` in the
script). Rules: an open `- [ ]` under a *closed* parent is promoted to its own line, under an
*open* parent it folds into the parent; item text is the first sentence/clause that fits, cut at
a word boundary with an ellipsis; the existing `TODO.md` preamble (through the first `---`) and
footer (after the last `---`) are preserved, so headers, licence stamps and quotes survive.

**Usage:**

```sh
/usr/bin/python3 tools/gen_todo_from_wbs.py                 # regenerate every TODO.md
/usr/bin/python3 tools/gen_todo_from_wbs.py --check         # unified diff + exit 1 on drift
/usr/bin/python3 tools/gen_todo_from_wbs.py docs/WBS.md     # one pair
```

Never hand-edit a `TODO.md`. A `TODO.md` line with no `WBS.md` home is a defect in the record:
move its content into the owning `WBS.md`, then regenerate. Wiring `--check` into
`.githooks/pre-commit` / CI beside `precommit_index.py --check` is tracked in root `WBS.md`
§0.10.2.

## Operator's Manual Sync

`tools/sync_operators_manual.py` keeps `docs/OPERATORS_MANUAL.md` current (WBS §0.10.3, OM-9). It
runs in `.githooks/pre-commit` (rewrites and stages the manual) and in CI (`--check`).

- **Single source:** `current-specification/flight_limits.json` (tilt range, EDF thrust/current/ESC,
  regulatory and failsafe thresholds). Edit there first.
- **Poll:** hashes the watched sources and reports which changed since the last sync.
- **Verify:** refuses the commit if the tools/docs that restate a limit disagree with the JSON.
- **Render:** recomputes T/W, θ_hover, V_min, density altitude, hover current/endurance and rewrites
  every `<!-- AUTO:name -->` block and `<!--V:key-->` value; prose outside markers is untouched.
- **Run:** `/usr/bin/python3 tools/sync_operators_manual.py [--check|--stage]`

## Rev U Consistency Gates

Three stdlib-only checks run in CI beside the index and joint-register gates:

- **`tools/check_bom_mesh_sync.py`** — the BOM is the procurement output, so a printed part's
  `Unit_Mass_g` must equal its mesh mass (STL volume × the SLS datasheet density from
  `tools/sls_materials.py`), as priced in `current-specification/auw_ledger.json`. `--write`
  re-syncs `bom_revU.csv/.json` after the ledger is regenerated. Printed rows with no ledger mesh are
  listed as NOT COVERED, never passed silently.
- **`tools/wbs_burndown.py`** — open and closed items per federation `WBS.md` (the `gen_todo_from_wbs.py` PAIRS list and open-item rule), the root `WBS.md` on its own row, and with `--baseline` the change since a snapshot (`d_open`, `closed+`). Sprints are measured by `closed+`, so recording a new finding never counts against them. The burndown measure of `docs/plans/2026-11-07-001-feat-rev-u-completion-execution-plan.md`. Exit 0 (2 on a bad baseline file).
- **`tools/nacelle64_assembly_check.py`** — assembles the 64 mm nacelle (pod, stage-2 cartridge, nozzle, trunnion, motor cans, spar stub, wing, wing pinion) in the nacelle-local frame; exact boolean overlap and clearance at 0 deg, a -5..+135 deg tilt sweep, the pinion-sweep pocket, and a voxel clearance search for the 4 x 10 AWG bundle from the spar-bore mouth to the ESC disconnect bay. Needs freshly rendered pod and trunnion STLs (`--pod`, `--trunnion`; the published pod is stale). Results: `docs/NACELLE_64MM_VERIFICATION.md` §5d. Exit 0 always (a report, not a gate).
- **`tools/check_nacelle_deps.py`** — the 64 mm nacelle's OpenSCAD closure (17 files) and `import()`s
  all exist and none is a 50 mm design or an archived file; required printed parts with no published STL
  are listed (`--strict-parts` makes them fail).
- **`tools/check_joint_register.py`** — every fastener-class BOM row is in a joint or exempted.

Supporting tools: `tools/scad_flatten.py` (applies OpenSCAD's last-assignment override rules once, how
the 64 mm sources were made independent of the 50 mm base) and `tools/winch_packaging_fit.py` (tests
whether the Rev C1 winch stack fits the one-piece forward hull; needs the hull and `shapely`).

## Output Locations

| Output Type | Directory | Format |
| --- | --- | --- |
| Fuselage STLs | `airframe/stls/fuselage/` | Binary STL (baked) |
| Nacelle STLs | `airframe/stls/nacelles/` | Binary STL (baked) |
| Wing STLs | `airframe/stls/wings/` | Binary STL (baked) |
| SCAD sources | `airframe/openscad/` | OpenSCAD `.scad` |
| Blender sources | `airframe/blender-scripts/files-hollowed-24in/` | Blender `.blend` |
| FreeCAD assembly | `airframe/freecad/assembly/` | FreeCAD `.FCStd` |
| PCB Gerbers | `avionics/kicad/<board>/gerbers/` | Gerber RS-274X format |
| Documentation | `docs/` | Markdown `.md` or PDF |

## Pre-Commit Checklist

Before committing any generated files:

**For STL files:**

- [ ] Mesh validation passed (watertight, no voids) — note this does not rule out
      duplicate/overlapping coincident triangles left by a boolean/hollowing step; that
      defect class passes a watertight check but can crash or hang a downstream slicer
      (see `docs/solutions/runtime-errors/curaengine-hangs-on-overlapping-mesh-faces.md`)
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
