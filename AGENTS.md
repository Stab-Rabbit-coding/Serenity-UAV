# Serenity UAV — Agent Instructions

Applies to every AI agent working in this repository (Claude, GPT, Gemini, Grok, local models,
or any other). **This file is the single authoritative source of project-wide policy.**
`CLAUDE.md` (root) is a one-line pointer here for tooling that expects that filename.

AGENTS.md files carry **standing rules and routing pointers only**; design status, decision
history, and measured figures live in the owning README, WBS, plan, or board `.md` (owner,
2026-11-17). Domain terms: `CONCEPTS.md`.

## 1. Project

Build a fully functional EDF tilt-rotor UAV replica of the Firefly-class ship "Serenity"
(Joss Whedon). All work targets an **actual physical build**; every component is fabricated or
procured. Mission profile: `README.md`.

Non-negotiable, project-wide requirements:

- **Redundancy/failover** in every system where feasible (dual ESCs, independent battery
  rails, manual override).
- **Security**: every message, internal and external, is digitally signed, authenticated, and
  logged; every cape carries a TPM and every other PCB an SE; logs write to hardware-enforced
  non-executable microSD. Comply with NIST SP 800-207 Zero Trust [REF-NIST-001 §2.1, §2.2, §3.3].
- **EMI hardening**: design objective is correct operation in a 500 W/m² RF field (e.g., near a
  radiating broadcast/cellular antenna).
- Avionics, comms, and software are designed for reuse on other UAV/UGV/USV/robot platforms.

**Propulsion (requirements only).** Each nacelle carries two EDFs in series, each
independently PID-controlled by a different node; any flight-control node can take over any
EDF. The tail EDF is part of the first build and flight-critical in hover: it draws all its air
through the fuselage interior to cool the avionics, feeds the **fixed** canonical elliptical
tail nozzle (**never** an iris) plus RCS bleed-air thrusters for pitch/yaw, is the only hover
pitch trim, and its remainder is forward thrust that shall not be counted toward hover lift.
Basis: `airframe/fuselage-mid/WBS.md` §1.1.1.4.0 and
`docs/plans/2026-11-15-002-feat-ramp-intake-edf-cooling-plan.md`. Values for calculations come
from `current-specification/bom_revU.json` and `airframe/README.md`, never from this file.

**Avionics (requirements only).** Seven PocketBeagle2 Industrial (PB2-I) compute nodes:
Shepherd, Inara and River are full stacks (Pilot cape + PB2-I and TACCO cape + PB2-I); Simon
is one PB2-I plus a trust-module MCU (`avionics/WBS.md` §1.11, OD-19 option B). Commo
(49 MHz + SiK) is one standalone MCU node at the antennas, reachable by every stack over
CAN FD / RS-485 / MIL-STD-1553C (no Ethernet). Onboard buses: CAN FD, MIL-STD-1553C, RS-485,
Ethernet, 5 kV galvanic isolation at every PB2-I node. External C2, all five usable for command
and control: Wi-Fi 5 GHz, ZigBee 2.4 GHz and mLRS on every TACCO cape; SiK 915 MHz and AX.25
49 MHz (47 CFR Part 15 §15.235, unlicensed, **not** Part 95 RCRS [REF-FCC-003]) via Commo.
S-Bus is not a C2 channel. As-built state: `avionics/README.md` and each board's `.md`.

## 2. Subsystem Files

Read this file plus the one matching your task's scope:

| File | Scope |
| --- | --- |
| `airframe/AGENTS.md` | Structural/CAD/3D design, aircraft datum, STL/SCAD, FreeCAD, Blender |
| `avionics/AGENTS.md` | KiCad PCB design, capes and nodes, security/crypto, FCC bands |
| `docs/AGENTS.md` | Documentation standards, citation procedure, references |
| `gcs/AGENTS.md` | Ground Control Station (Skipper) |
| `tools/AGENTS.md` | Build automation, validators, script standards |
| `current-specification/AGENTS.md` | Active specifications |
| `graphical-build-guide/AGENTS.md` | Build guide, phases, fabrication checklists |
| `deferred/AGENTS.md` | Deferred work, planned upgrades, rejected-design history |

A subsystem file only **adds** scope-specific detail. Where this file speaks, it wins; a
subsystem line that contradicts it is a defect — fix it (§11).

## 3. Attribution and Licensing

Work is licensed by **what the file produces** (owner rule, 2026-10-04; full policy and the
per-subsystem `LICENSE` map: `docs/attribution_and_licensing.md`):

- **Hardware, and code that defines, creates or renders hardware** (OpenSCAD, KiCad files and
  scripts, FreeCAD, Blender, G-code/slicer profiles, mesh/CAD/PCB writers): **CERN-OHL-W 2.0**.
- **Code whose end result is software or firmware** (firmware, device trees, ground software,
  analysis/verification/CI tools): **MIT**.
- **Documents and all images** (Markdown, text, specifications, build guides, SVG/PNG/JPG/WebP,
  renders): **CC BY-SA 4.0**. Raster images carry it in XMP, SVGs in a header comment;
  `REUSE.toml` covers the image folders.

Every new file's header carries one line: `License: <name> — see LICENSES/<file>
(SPDX-License-Identifier: <id>)`. Third-party material keeps its own licence; before committing
any model, image, symbol, SCAD, STL, or code snippet, confirm it is compatible with the licence
above for its file type. Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (personal copyright
retained; avionics boards carry his LLC name).

- **Never fabricate a reference, citation, standard, or other resource.** Cite every resource
  used, whether or not its licence requires it. Distinguish AI-generated from human work; credit
  humans by GitHub username and each AI system/model separately, never lumped together.
- Cite every design decision, algorithm, or geometry technique drawn from an external
  reference in the source file's comment block and in the commit message; derivative files
  carry the full attribution chain.

## 4. Standards Vetting

Vet every non-cosmetic design decision against applicable standards/regulations before
implementation. Catalog every citation in `REFERENCES.md` and
write it as `[REF-ID §section.subsection.paragraph]`. **Never guess or invent a section number.**
The catalog fields, the citation-audit and reference-lifecycle procedures, and the standards
bodies are in `docs/AGENTS.md`. United States regulatory and standards bodies take precedence;
all legal/regulatory matters are US jurisdiction.

## 5. Engineering Requirements

- Account for real weight, balance, power, space, and component capability on every change;
  quote actual masses, CG shifts, and loads. Never write "TBD".
- **Missing values:** where no datasheet or user-verified value exists yet, write
  `UNVERIFIED — <basis>, see <WBS id>`, giving the best documented estimate and its source,
  and open that WBS item to obtain the real value. Never present it as verified.
- **Component measurements** (mass, thrust, dimensions, ratings) come only from the
  manufacturer's datasheet or document, or a user-verified measurement, cited where recorded —
  never from a seller listing, memory, or an earlier estimate.
- **Units: imperial first, metric in parentheses**: `10 in (254 mm)`, `2.5 lbm (1.13 kg)`,
  `4.8 lbf (21.4 N)`, `25 kt (12.8 m/s)`, `25 lbf·in (2.8 N·m)`. Use **lbm** for mass and
  **lbf** for force, never bare "lb". Thrust, lift, and aerodynamic loads are forces; component
  weight and payload are masses. Airspeed and wind speed are always **kt**.
- **Part selection gate:** every IC, discrete semiconductor, and module shall pass
  `docs/SOURCING_POLICY.md` (no restricted-country silicon by manufacturer domicile/control;
  public, NDA-free datasheets) before it enters a schematic or BOM.
- EDF housings are structural printed parts: specify wall thickness, infill, and material.
- PCBs are packed tight: the user places final footprints after scripted population and
  net-building. Refer any DRC fix that moves a footprint to the user; make other fixes directly.

### Airframe geometry

- **One aircraft datum** (owner directive 2026-10-19): origin on the centreline, at the nose
  tip, on the static ground plane; only a PCB inside KiCad keeps its own coordinates. Axes,
  frames, and migration rules: `airframe/AGENTS.md`.
- Keep the canonical outer mold line intact: interior modifications blend into it, and the
  exterior changes only where structurally required. Minimize deviations from canon; every
  deviation shall keep the style and character of the Serenity ship and add nothing
  incongruent (owner directive 2026-11-01). Check exterior deviations against
  `docs/references/` (REF-CAD-002/003) in the authority order of `airframe/HULL_FRAME_REFERENCE.md`.
- Bounding-box/centroid math is inadequate for placement; use the validated extents in
  `airframe/HULL_FRAME_REFERENCE.md`, or request manual FreeCAD placement.
- Nacelle nozzle requirement: `airframe/AGENTS.md` "Nacelle Nozzle Drive". Landing-gear and
  nozzle-mechanism design: `docs/LANDING_GEAR_ANALYSIS.md`, `docs/NOZZLE_DRIVE_TRADE.md`.

## 6. Coding and Documentation Standards

- Clean, syntactically correct, secure code; avoid OWASP Top 10 classes; pass all linting.
  **4-space indent, every language.** Verbose comments in each language's native style; where a
  format has no comment syntax, use an accompanying Markdown file. **KiCad files: never `;` or
  `#`**; use `( comment 1 "text" )` blocks.
- Security engineering complies with NIST SP 800-82 Rev 3 [REF-NIST-002 §5.3, §5.4, §6.2.5],
  SP 800-160 Vol 1 Rev 1 [REF-NIST-003 Ch.3], and SP 800-207 [REF-NIST-001 §2.1].
- **On an exploitable failure** (race, memory corruption, overflow, use-after-free, privilege
  escalation, etc.): stop, write a sanitized bug report (failure type, subsystem, repro steps,
  observed vs. expected; no filenames, paths, or PII), and do not commit the failure pattern
  until it has been discussed. Enforced by `tools/precommit_sanitize.py`.

### WARNING, CAUTION, NOTE, and wording

This section applies to every document in the repository, human- or AI-authored. Callouts and
requirement verbs follow CNAF M-3710.7 §1.5–1.6 [REF-MIL-003 §1.5, §1.6]:

- **WARNING** — a procedure, practice, or condition that may result in injury to or death of
  people if not carefully observed or followed (e.g., a charged spring, a soldering iron, a
  live battery pack, a payload release or failure that can bring the aircraft down on people).
- **CAUTION** — a procedure, practice, or condition that may result in damage to or loss of
  equipment, with no risk to people. **Owner deviation from CNAF M-3710.7:** CNAF assigns loss
  of the aircraft to WARNING; here, loss of the aircraft with no risk to people is a CAUTION.
- **NOTE** — information that must be emphasized but carries no WARNING- or CAUTION-level risk.

Never downgrade a WARNING-level risk to a NOTE, never use WARNING/CAUTION for merely helpful
information, and never use an ad hoc label ("IMPORTANT:", "ATTENTION:").

- **Shall** — mandatory (not "must"). **Should** — recommended. **May** / **need not** — optional. **Will**
  — futurity only, never a requirement. **Could** (project) — only physical/performance limits.
- **Voice** (project convention): active voice for procedures, directions, and specifications,
  including procedural steps inside an as-built document; passive voice for as-built
  description. Passive is allowed where a shall/should/may requirement needs it ("The joint
  shall be inspected before final assembly").

## 7. Fabrication Standards

- **Print process and material (Rev U):** flight-article hull and nacelle printed parts are
  **SLS DuraForm PA CF** [3DS-30108A] from a service bureau; PA11 at impact points (gear feet).
  Every PA CF flight part shall meet MS-SLS-PACF (`docs/MATSPEC_SLS_PA_CF.md`). Selection
  basis: `docs/SLS_MATERIAL_SELECTION_3DSYSTEMS.md`.
- **Mass basis:** price printed parts at the datasheet solid density from the single source
  `tools/sls_materials.py`; convert any FDM-basis mass with `sls_materials.sls_from_fdm_mass`.
  Every printed part's BOM `Unit_Mass_g` shall equal its mesh mass (`tools/check_bom_mesh_sync.py`
  gates this in CI; `--write` re-syncs).
- **Hull:** two SLS parts joined by one internal splice collar; both ship as gzip tarballs.
- **SLS walls** (OD-25 option A): size from `docs/SLS_MIN_WALL_THICKNESS.md` by load category
  and backing. Where category or print orientation is not stated, the wall shall be
  0.079 in (2.0 mm). Load-bearing parts are still sized by their own loads.
- **FDM CF-PETG** remains the spec for prototype prints and parts not yet moved to SLS:
  0.006 in (0.15 mm) layers, ≥4 perimeters, ≥40% infill load-bearing / 25% non-structural.
  Replace any stray "PETG" with CF-PETG. The DaVinci Jr prototype is exempt.
- Exterior shell: hollow, watertight, no voids; fill with 2 lbm/ft³ (32 kg/m³) closed-cell foam;
  inter-section mating faces stay open for build access and cable routing.
- Integrate brackets, bosses, and ribs into the shell print wherever feasible; design every
  field-serviceable part for common hand-tool disassembly. Load-bearing mating joints need a
  2-wall contact annulus **and** a positive-stop shoulder, never friction fit alone.
- **Mesh gate:** after every 3D-model edit run `python3 tools/validate_stls.py` (watertight, no
  self-intersection, outward normals, manifold); verify Z-range and bore diameters in console
  output. Resolve every finding before commit.
- **ERC/DRC gate:** after every schematic/PCB edit run
  `python3 tools/validate_kicad.py --changed-since origin/main`. Resolve each violation, or
  record it (rule + reason) as an open item in the owning `WBS.md` and the board's `.md`.
  Production needs a complete schematic, PCB, copper, correct footprints, and Gerbers.

## 8. Revisions

- **One project-wide letter revision.** The current baseline is **Rev U** (in progress). A
  letter revision is a comprehensive checkpoint: every component is current, integrated,
  tested, and documented as of that letter, whether or not it changed.
- **Numbered modification** after a letter (U1, U2, …; resets at each letter) is an incremental
  change. Unchanged components carry forward into the next letter's baseline.
- Board-level letters already in use (e.g., Commo Rev T, avionics Rev S1/S2) are frozen
  historical labels; every component is stamped Rev U when Rev U closes (ADR
  `docs/adr/0001-single-project-revision-letter.md`). Do not start a new board-level letter.
- An archived item keeps its label and drops out of future revisions. Coordinate frames are
  not revisions: write "frame R1"/"frame R2", never "Rev R2".

## 9. Naming and Roles

| Name | Role |
| --- | --- |
| Skipper | Ground control station |
| Pilot | Flight Control + Sensor cape |
| TACCO | Comms/Logging/Payload cape |
| Flight Engineer | Power Distribution Board |
| Commo | 49 MHz + SiK standalone transceiver node |
| Observer | Cargo-handling + nose/cargo-bay vision/ToF/laser board |
| Shepherd's Room | Bay A — forward avionics |
| Inara's Shuttle | Bay B — port avionics |
| River's Room | Bay C — starboard avionics |
| Simon's Medbay | Bay D — aft avionics |

Board names are generic role names; never use a former (Firefly-character) board name in new
work (record: `docs/attribution_and_licensing.md` §6).

- **PACE:** any change to a node's role or failover level shall be checked against
  `avionics/PACE.md` and approved by the owner before implementation.

## 10. Workflow

- Before a task, read this file and the matching subsystem `AGENTS.md`; check the owning
  `TODO.md` and recent git history; search `docs/solutions/` for past solutions in the area.
- **Hooks:** enable once per clone (`git config core.hooksPath .githooks`); never skip hooks or
  bypass signing. Without hooks, run `python3 tools/precommit_index.py` and stage its output.
- **Never hand-edit generated files:** `PROJECT_INDEX.md`, `ARCHIVE_INDEX.md`, `tools/index_tags.json`
  (`tools/precommit_index.py`) and every `TODO.md` (`tools/gen_todo_from_wbs.py`).
- **AGENTS.md caps:** root ≤300 lines / 20 KB, subsystem ≤100 lines / 7 KB
  (`tools/check_agents_size.py`, hook and CI). State each rule once, in its owning file; link it.
- **Interpreter:** `/usr/bin/python3` for tools importing `trimesh` (the `.venv` hides it).

### WBS.md / TODO.md federation

Each subsystem keeps a **`WBS.md`** (the full record: every task, done or open, with notes and
rationale) and a generated **`TODO.md`** (open top-level items only, one ≤70-char line each,
pointing back to `WBS.md`). Root `WBS.md` is a compact index into the subsystem files. Large
subsystems split `WBS.md` detail across files (new file past ~500 lines); the inventory is in
`docs/WBS_FEDERATION.md`, and split files are governed by their parent folder's `AGENTS.md`.

- **Open an item:** find the owning file in `docs/WBS_FEDERATION.md`; take the next ID in that
  branch's existing scheme; add a `- [ ]` entry with full notes there and a ≤70-char line under
  the matching root `WBS.md` heading; then run `python3 tools/gen_todo_from_wbs.py`.
- **Finished work:** check the item off in the owning `WBS.md` first, then regenerate every
  `TODO.md` (`--check` reports drift and exits non-zero; it runs in the hook and CI). A
  `TODO.md` line with no `WBS.md` home is a defect: move it into `WBS.md`, then regenerate.

### Design-shift gate (mandatory, before implementation)

A **design shift** changes a subsystem's capability (moving a functional block between PCBs,
swapping a major part's make/model, changing how an assembly mounts or actuates), not a bug
fix, DRC/ERC cleanup, placement/routing, or documentation correction.

1. **Document the decision first** in the owning `WBS.md` (and root `WBS.md` if
   federation-visible), before any KiCad, OpenSCAD, Blender, or STL change: what changes, why,
   what was considered and rejected, and which boards/parts/files are affected. In the same
   pass, add at least a dated status note to the matching descriptive doc (board `.md`,
   `current-specification/README.md`, or airframe doc).
2. **Then write an implementation plan** at `docs/plans/YYYY-MM-DD-NNN-<type>-<slug>-plan.md`
   (e.g., the Claude Code `ce-plan` skill).
3. **Then implement** in the KiCad or STL/CAD sources.

If implementation came first, write the WBS entry next; a KiCad/STL change is never the first
place a decision appears.

### Other practice

- Prefer editing existing files; no speculative abstractions, feature flags, or scaffolding.
- Blender and FreeCAD run headless; invocations and output paths: `tools/TOOL_REFERENCE.md`.
- Drop the legacy `s_` file prefix (Rev R1) when you touch a reference that carries it.
- Git: create new commits, don't amend unless asked; never force-push `main`; use a HEREDOC for
  multi-line messages; credit the authoring AI system with its own vendor's trailer (e.g.,
  Claude: `Co-Authored-By: Claude <noreply@anthropic.com>`).
- A sparse, on-topic Firefly quote in docs is welcome, never in place of required content.

## 11. Conflicts and Unknowns

1. This file wins wherever it speaks; a contradicting subsystem line is a defect to fix.
2. A contradiction this file does not settle (between two subsystem files, or between a rule
   and the owning WBS/plan record): **stop and get the owner's decision** before proceeding.
3. `REFERENCES.md` (verified standards) outranks comments or assumptions.
4. Actual code/model state outranks stale documentation: fix the doc to match and note why.
5. Task unclear, or information missing: **ask the user.** Never guess or invent details.
