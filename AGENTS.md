# Serenity UAV — Agent Instructions

Applies to every AI agent working in this repository — Claude, GPT, Gemini, Grok,
local/llama.cpp models, or any other. **This file is the single authoritative source of
project-wide policy.** `CLAUDE.md` (root) is a one-line pointer to this file, kept only for
tooling that looks for that filename specifically.

## 1. Project

Build a fully functional EDF tilt-rotor UAV replica of the Firefly-class ship "Serenity"
(Joss Whedon). All work targets an **actual physical build** — every component will be
fabricated or procured. Never leave a spec as "TBD"; quote real masses, CG, and loads. See
`README.md` for the mission profile.

Non-negotiable, project-wide requirements:
- **Redundancy/failover** in every system where feasible (dual ESCs, independent battery
  rails, manual override).
- **Security**: every message, internal and external, is digitally signed, authenticated, and
  logged; every Cape carries a TPM; logs write to hardware-enforced non-executable microSD.
  Comply with NIST SP 800-207 Zero Trust [REF-NIST-001 §2.1, §2.2, §3.3].
- **EMI hardening**: design objective is correct operation in a 500 W/m² RF field (e.g. near a
  radiating broadcast/cellular antenna).
- Avionics, comms, and software are designed for reuse on other UAV/UGV/USV/robot platforms,
  not just this airframe.

**Propulsion baseline** (use for all thrust calculations):
- Nacelle EDF: 50 mm 6S, x-fly 2627-3200kv, 12-fin rotor / 11-fin stator, 1240 g thrust each;
  2 EDFs in series per nacelle, 90% stator efficiency → **2232 g per nacelle**.
- Fuselage EDF (Phase 11, optional/deferred): 55 mm 6S, feeds the **fixed** canonical
  elliptical tail nozzle — 2.06 in (52.3 mm) × 1.76 in (44.7 mm) — **never** an iris — plus 4
  RCS bleed-air thrusters (~15% mass flow) for pitch/yaw. Remainder is longitudinal forward
  thrust only, excluded from hover T/W. Details: `deferred/AGENTS.md`,
  `deferred/aft-edf/README.md`.

**Avionics architecture** (8-node, PACE failover — stable facts only; for current
implementation/PCB status see `avionics/AGENTS.md` and each board's own `.md` under
`avionics/kicad/<board>/`, which is updated more often than this file and is authoritative for
as-built state):
- 8× PocketBeagle2 Industrial SBC nodes, each carrying **Pilot** (flight control/sensor cape) +
  **TACCO** (comms/logging/payload cape), 5 kV galvanic isolation on CAN FD/RS-485/Ethernet.
- **COMMO** (49 MHz + LoRa transceiver cape) is installed only in River's Room and Simon's
  Medbay.
- Onboard bus: CAN FD, MIL-STD 1553, RS-485, Ethernet — all 8 nodes interconnected.
- External C2, all 4 usable for command and control: Wi-Fi 5 GHz, Zigbee 2.4 GHz, MAVLink/SiK
  915 MHz, AX.25 49 MHz (47 CFR Part 15 §15.235 — unlicensed, **not** Part 95 RCRS
  [REF-FCC-003]). S-Bus is supported by the capes but unused.
- Each nacelle has 2 EDFs in series, independently PID-controlled by two different SBCs. Any
  of the 4 flight-control nodes can take over any EDF.

## 2. Subsystem Files

Read this file plus the one matching your task's scope:

| File | Scope |
|---|---|
| `airframe/AGENTS.md` | Structural/CAD/3D design, hull-frame coordinates, fabrication, STL/SCAD, FreeCAD |
| `avionics/AGENTS.md` | KiCad PCB design, capes, security/crypto, comms protocols |
| `docs/AGENTS.md` | Documentation standards, standards vetting, references |
| `gcs/AGENTS.md` | Ground Control Station (Malcolm) |
| `tools/AGENTS.md` | Build automation, bake tool, Blender pipeline |
| `current-specification/AGENTS.md` | Active specs, revision numbering, traceability |
| `graphical-build-guide/AGENTS.md` | Build guide, fabrication checklists |
| `deferred/AGENTS.md` | Phase 11+ work, planned upgrades, rejected-design history |

A subsystem file is authoritative within its own scope. If it contradicts this file, do not
pick one silently — see §11.

## 3. Attribution and Licensing

All work is published under **CC BY 4.0**. Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
(personal copyright retained; avionics boards are marked with his personally owned LLC name).

- **Never fabricate a reference, citation, standard, or other resource.**
- Cite every resource used, whether or not the license requires it.
- Distinguish AI-generated work from human work; credit human contributors by GitHub username
  unless a governing project document says otherwise.
- Cite each AI system/model separately for its own contribution — e.g. Opus 4.8, Sonnet,
  Haiku 4.5, Gemini, and Grok are never lumped together.
- Every design decision, algorithm, or geometry technique drawn from an external reference
  **must** be cited in the source file's docstring/comment block and in the commit message.
- Derivative files carry the **full attribution chain** back to upstream sources.
- **Before committing any model, image, KiCad symbol, SCAD file, STL, or code snippet**,
  confirm its license is compatible with CC BY 4.0. Only license-compatible items are
  integrated.

## 4. Standards Vetting

Every design decision with any effect beyond cosmetic appearance must be vetted against
applicable standards/regulations before implementation.

- Catalog every citation in `REFERENCES.md`: designation + full title, a validated URL,
  the exact chapter/section/paragraph applied, and every file that cites it.
- Cite in code and docs as `[REF-ID §section.subsection.paragraph]`.
- **Never guess or invent a section number.** If a citation can't be verified, mark it
  "requires verification" in `REFERENCES.md` and add a `TODO.md §0.x` item.
- Applicable bodies: FAA, FCC, NIST, DoD/DLA, ISO, IEC, VDE, IEEE, ISA/IEC 62443,
  AUVSI/ASTM F38, ICAO. All legal/regulatory matters are US jurisdiction.

## 5. Engineering Requirements

- Account for real weight, balance, power, space, and component capability on every change;
  quote actual masses/CG shifts — never leave them "TBD."
- **Units — imperial-primary, metric in parentheses**: `10 in (254 mm)`, `2.5 lbm (1.13 kg)`,
  `4.8 lbf (21.4 N)`. Use **lbm** for mass, **lbf** for force — never bare "lb." Thrust/lift/
  aerodynamic loads are forces (lbf/N); component weight and payload capacity are masses
  (lbm/kg). Airspeed and wind speed are always **kt** (never mph/km/h).
- Failover: every system needs a fallback or redundant path where feasible.
- EDF housings are structural, printed as part of the build — specify wall thickness, infill,
  and material for each.
- PCBs are packed tight; final footprint positions are placed manually by the user after
  script-driven population and net-building. If a DRC violation requires moving a footprint,
  **refer it to the user**; other DRC fixes may be made directly.

### Airframe geometry

Serenity's hull is complex — bounding-box/centroid math is inadequate for part placement. Use
the validated hull-frame positions in `airframe/AGENTS.md`, or request manual FreeCAD
placement from the user when uncertain. Keep the canonical outer mold line intact; interior
modifications must blend into it and never alter the exterior unless structurally required. The
`docs/references/` library is the ground truth for what "canonical" shape means — authority order
QMx 2007 blueprints (most authoritative) → Nick Henning renders → misubisu Thingiverse model
(the `s_*.stl` origin; verify against the two above). See `airframe/AGENTS.md` "Canonical Accuracy
References" and `REFERENCES.md` REF-CAD-002/003/004.
Four fuselage sections (head, cargo, middle-neck/horseshoe ring, rear) plus wings and tilting
nacelles — see `airframe/AGENTS.md` for the qualitative layout, the hull-frame coordinate
standard, and the validated extents table (do not duplicate that table here).

Landing-gear and nacelle-nozzle-drive implementation details change as the design matures —
do not restate their specifics in this file. Canonical sources: `docs/LANDING_GEAR_ANALYSIS.md`
(landing gear, current revision) and `docs/NOZZLE_DRIVE_TRADE.md` (nozzle drive mechanism,
current revision); see `airframe/AGENTS.md` for both. Each nacelle nozzle is variable-diameter,
driven by nacelle tilt, sized 75% of bore at 0° (forward) to 105% of bore at ≥90° (vertical/
backing) — that ratio is a fixed functional requirement; the drive mechanism that achieves it
is under active trade study and must not be assumed.

## 6. Coding Standards

- Clean, syntactically correct, secure code — avoid OWASP Top 10 classes (injection, XSS,
  etc.). Pass all linting.
- **4-space indent, every language, always.**
- Verbose comments in each language's native style. If a format has no comment syntax (e.g.
  KiCad), put comments in an accompanying Markdown file instead. **KiCad files: never use `;`
  or `#`** — use `( comment 1 "text" )` blocks only.
- Security engineering complies with NIST SP 800-82 Rev 3 [REF-NIST-002 §5.3, §5.4, §6.2.5],
  SP 800-160 Vol 1 Rev 1 [REF-NIST-003 Ch.3], SP 800-207 [REF-NIST-001 §2.1].
- **On an exploitable failure** (race condition, memory corruption, buffer overflow,
  use-after-free, privilege escalation, etc.): stop, immediately generate a sanitized bug
  report (generalized failure type, affected subsystem, repro steps, observed-vs-expected —
  no filenames/paths/PII), and do not commit the failure pattern until it's been discussed.
  See `.githooks/pre-commit` / `tools/precommit_sanitize.py`.

## 7. Fabrication Standards

- **Material: CF-PETG** — 0.15 mm layer height, ≥4 perimeters, ≥40% infill load-bearing /
  25% non-structural. Replace any stray "PETG" reference with CF-PETG when found; verify any
  other material mentioned in the repo. (The DaVinci Jr prototype is exempt — not expected to
  meet full-build spec.)
- Exterior shell: hollow to 2.0 mm, watertight, no voids; fill with 2 lb/ft³ low-density foam;
  inter-section mating faces stay open for build access.
- Integrate mounting brackets/bosses/ribs into the shell print wherever feasible.
- Load-bearing mating joints require a minimum 2-wall contact annulus **and** a positive-stop
  shoulder — friction fit alone is never acceptable for a flight-critical joint.
- Design every field-serviceable part for **common hand-tool disassembly**.
- **Mesh validation is mandatory after every 3D-model edit** — watertight, no
  self-intersection, correct normals, manifold topology. Report findings to `TODO.md`; resolve
  before commit.
- **Every schematic/PCB edit requires a KiCad ERC + DRC pass.** Resolve violations, or
  document them (rule + reason) in `TODO.md`. Production requires a complete schematic + PCB +
  copper traces + correct IC footprints + production-ready Gerbers.

## 8. Revisions

- **Letter revision** (Rev R, Rev S, …): a comprehensive checkpoint. Every component is
  current, integrated, tested, and documented as of that letter — whether or not it changed
  since an earlier letter.
- **Numbered modification** after a letter (R1, R2, … — resets at each new letter): an
  incremental change. Components carried forward unchanged are part of the next letter's
  baseline.
- An archived item keeps the revision label it held at archival and drops out of future
  revisions.

## 9. Naming and Roles

| Name | Role | Firefly line |
|---|---|---|
| Malcolm | Ground control station | "I aim to misbehave." |
| Pilot | Flight Control + Sensor cape | "I'm a leaf on the wind." |
| TACCO | Comms/Logging/Payload cape | "Big Damn Heroes, sir." |
| FlightEngineer | Power Distribution Board | "Everything is shiny." |
| COMMO | 49 MHz + LoRa transceiver cape | — |
| Observer | Cargo-handling + nose/cargo-bay vision/ToF/laser board | "She's a good gun." |
| Shepherd's Room | Bay A — forward avionics | "I have heathens enough right here." |
| Inara's Shuttle | Bay B — port avionics | "Mal, I will never understand you." |
| River's Room | Bay C — starboard avionics | "I can kill you with my mind." |
| Simon's Medbay | Bay D — aft avionics | "What did they do to you?" |

FlightEngineer's room sits in the middle-section inner neck (open ventral face of the horseshoe ring),
minimizing power-run length to all four nacelles/stacks/battery. Observer is a standalone board
(not a PB2-I cape) installed at two locations — bow sensor pod and cargo nadir FPV mount —
connected only via the shielded Ethernet ring + CAN-FD trunk. **Observer's laser-indicator specs
(class, spread angle, per-site optics) change as the design matures — do not restate them
here; canonical source is `docs/JAYNE_LASER_ANALYSIS.md` (current revision) and
`avionics/kicad/Observerver/Observer.md`.**

**PACE per stack** (Primary / Alternative / Contingency / Emergency):

| Stack | Watchdog | Comms | Flight Control | Payload |
|---|---|---|---|---|
| Shepherd | P | A | C | E |
| Inara | A | P | E | C |
| River | C | E | P | A |
| Simon | A | C | A | P |

Shepherd: watchdog/fault-detect/failover/auth; SiK primary, Wi-Fi secondary.
Inara: camera/external sensors/high-bandwidth ground link; Wi-Fi primary, SiK-MAVLink
secondary.
River: forward EDF + nacelle tilt sync + most resilient comms; 49 MHz primary, LoRa secondary,
both via COMMO.
Simon: aft EDF + alternate watchdog + Jayne/cargo oversight; 49 MHz primary, SiK secondary,
both via COMMO.

## 10. Workflow

- Read this file and the matching subsystem `AGENTS.md` before starting a task; check
  `TODO.md` and recent git history for context; verify any citation you use against
  `REFERENCES.md`.
- New standards citation: look it up by REF-ID first; if absent, add it to `REFERENCES.md`
  with a validated URL and exact section, then cite the REF-ID. Never guess a section number.
- Keep `PROJECT_INDEX.md` current for active files; when a file is archived, move its entry to
  `ARCHIVE_INDEX.md`.

### WBS.md / TODO.md Federation (Rev S2)

Every subsystem that owns WBS branches keeps **two files, not one**:

- **`WBS.md`** — the full historical record: every task ever defined, done or open, with full
  notes/rationale/nested sub-steps for project-progression tracking. Root `WBS.md` is itself a
  compact index (headings, subheadings, single-line ≤70-char items, done + open) that points
  into each subsystem's own `WBS.md` for the real narrative detail.
- **`TODO.md`** — a lean, generated-from-`WBS.md` list of **only currently-open (unchecked)
  top-level items**, one line each (≤70 chars), each pointing back to its entry in the local
  `WBS.md`. This is the "what's actually left" view. Close an item in `WBS.md` first;
  `TODO.md` is regenerated/pruned from there, never edited as the source of truth.

Governance stays with the `AGENTS.md` files listed in §2; several subsystems keep `WBS.md`
detail split across more than one file so none exceeds ~500 lines (the threshold at which a
subsystem gets a new detail file rather than an ever-growing one):

- **avionics/** — `avionics/{TODO,WBS}.md` (Pilot/TACCO/COMMO cape hardware, names, workload),
  `avionics/rev-s1/{TODO,WBS}.md` (COMMO/TACCO/FlightEngineer Rev S1 redesign),
  `avionics/emi-hardening/{TODO,WBS}.md` (§0.6, §1.4 EMI hardening beyond the PCBs),
  `avionics/jayne/{TODO,WBS}.md` (Observer board + firmware), `avionics/firmware/{TODO,WBS}.md`
  (Pilot/TACCO node firmware)
- **airframe/** — `airframe/{TODO,WBS}.md` (hull-frame standard, non-printable placeholders,
  procurement), `airframe/fuselage-joints/{TODO,WBS}.md`, `airframe/fuselage-covers/{TODO,WBS}.md`,
  `airframe/fuselage-mid/{TODO,WBS}.md` (fuselage §1.1.1, split 3 ways),
  `airframe/wings-nacelles/{TODO,WBS}.md`, `airframe/landing-gear/{TODO,WBS}.md`
- **graphical-build-guide/** — `graphical-build-guide/{TODO,WBS}.md` (Phases 0-4 + SVG rebuild
  pipeline), `graphical-build-guide/flight-phases/{TODO,WBS}.md` (Phases 5-10)
- **docs/**, **gcs/**, **deferred/** — a single `{TODO,WBS}.md` pair each (well under the cap)
- **tools/**, **current-specification/** — reference-index `TODO.md` files only, no `WBS.md`
  (own no WBS branch and no checkboxes of their own; pointer views into the owning
  subsystem's `WBS.md`/`TODO.md`)

Split detail files are governed by their parent folder's `AGENTS.md` (no separate federated
`AGENTS.md` per split — e.g. `avionics/jayne/` follows `avionics/AGENTS.md`).

New work: close it in the owning `WBS.md` first (full notes there), then prune/regenerate the
matching `TODO.md` line from it. Sync root and subsystem `WBS.md`/`TODO.md` before committing.
- Prefer editing existing files. No speculative abstractions, feature flags, or unused
  scaffolding — build only what the task needs.
- Blender: run headless — `blender --background --python <script>.py`. FreeCAD:
  `freecadcmd <script>.py`. STL output goes to `airframe/stls/{fuselage,nacelles,wings}/`;
  verify Z-range/bore-diameter in console output before committing.
- File naming: the legacy `s_` prefix is dropped (Rev R1). Fix a stale `s_`-prefixed
  reference opportunistically when you touch that code/doc — not as a dedicated sweep.
- Git: create new commits, don't amend (unless asked); never skip hooks or bypass signing;
  never force-push `main`. Use a HEREDOC for multi-line commit messages, and credit the
  authoring model, e.g. `Co-Authored-By: <Model Name> <noreply@anthropic.com>`.
- Occasionally add a sparse, on-topic Firefly/Serenity quote to documentation (style:
  `docs/PHASED_BUILD_GUIDE.md`, `TODO.md` footer) — never in place of required technical
  content.

## 11. Conflicts and Unknowns

1. This file (project-wide) vs. a subsystem `AGENTS.md` (scope-specific): the subsystem file
   governs within its own scope unless this file explicitly excludes that topic.
2. Any conflict between this file and a subsystem file: **stop and get user adjudication
   before proceeding** — do not guess, do not pick a side unilaterally.
3. `REFERENCES.md` (verified standards) outranks comments or assumptions.
4. Actual code/model state outranks stale documentation — if they diverge, fix the doc to
   match reality and note why they diverged.
5. Task unclear, or information you need is missing: **ask the user.** Never guess or invent
   details.

---
**Authoritative file.** `CLAUDE.md` (root) points here for tooling that expects that
filename.
