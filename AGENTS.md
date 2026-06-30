# Instructions for AI Agents

> **You are Claude Code, or any other AI assistant working in the Serenity-UAV repository. Before proceeding with any task, read this file and the project instructions.**

## Authoritative Source

The **canonical project instructions and standards are in [`CLAUDE.md`](CLAUDE.md)** (root directory). You **must** follow all standards, conventions, and policies documented there.

**Every design specification, code change, commit message, and piece of documentation must comply with the standards in `CLAUDE.md`.**

## Authenticity

- **No Reference, citation, standard, or other resource will ever be fabricated.**
- Every resource will be properly cited, whether or not it's required by copyright or license
- All work done by AI will be distinguished from that done by a human user
- Human contributers will be referenced by their GitHub usernames, unless otherwise specified in a the project's governing documents.
- Each AI system and model will be cited for its own contribution (i.e. Gemini must be distinguished from Grok, from Claude, and Haiku 4.5 needs a separate citation from Opus 4.8)
- **Every design decision, algorithm, or geometry technique that draws on an external reference must be cited in the relevant source file docstring and commit message.**
- **Derivative files must carry the full attribution chain back to upstream sources.**

## Scope-Specific Guidance

For work within a specific subsystem, also consult the **federated `CLAUDE.md` file in that folder**. These provide additional detail and workflows tailored to that subsystem:

- **[`airframe/CLAUDE.md`](airframe/CLAUDE.md)** — Structural design, CAD/3D modeling, hull-frame coordinate system, fabrication standards, STL validation
- **[`avionics/CLAUDE.md`](avionics/CLAUDE.md)** — KiCad PCB design, capes, avionics stacks, security, communications protocols
- **[`docs/CLAUDE.md`](docs/CLAUDE.md)** — Documentation standards, standards vetting policy, references management
- **[`gcs/CLAUDE.md`](gcs/CLAUDE.md)** — Ground Control Station (Malcolm), command and control, telemetry
- **[`tools/CLAUDE.md`](tools/CLAUDE.md)** — Build automation, bake tool, Blender pipeline, SCAD generation
- **[`current-specification/CLAUDE.md`](current-specification/CLAUDE.md)** — Active design specifications, revision numbering, traceability
- **[`graphical-build-guide/CLAUDE.md`](graphical-build-guide/CLAUDE.md)** — Phased build instructions, fabrication checklists, troubleshooting
- **[`deferred/CLAUDE.md`](deferred/CLAUDE.md)** — Phase 11+ work, planned upgrades, design decision history

**Subordinate files are authoritative for their scope.** If a subordinate file contradicts the root file, follow the subordinate.

## Critical Standards You Must Follow

### Code and Commit Quality

- All code shall be clean and syntactically correct
- 4-space indenting throughout
- Verbose comments in strict conformity to each language
- Use secure coding practices — avoid command injection, XSS, SQL injection, OWASP top 10 vulnerabilities
- All code must pass strict linting rules

### Documentation

- Every design specification with any effect beyond cosmetic appearance must be vetted against applicable industry standards
- All standards citations use `[REF-ID §section.subsection.paragraph]` format from `REFERENCES.md`
- No fabricated, unverifiable, or incorrectly attributed references are permitted
- All measurements: **imperial-primary with metric in parentheses** (e.g., 10 in (254 mm))
    - Use **lbm** for mass, **lbf** for force, **kt** for airspeed

### Design Philosophy

- All designs are for **actual physical builds**, not hypothetical work
- Every component will be fabricated or procured
- Account for real weights, balance, power, space, and component capabilities
- Do not leave values as "TBD"
- Failover capability is a first-class requirement

### Fabrication Standards

- **Material:** CF-PETG (0.15 mm layer height, 4 perimeters, ≥40% infill for load-bearing)
- **Shell walls:** hollowed to 2.0 mm while maintaining a **watertight mesh** with no voids or holes
- All load-bearing mating surfaces: minimum 2-wall contact annulus + positive-stop shoulder
- **Mesh validation:** Run after every 3D model modification; report all findings to `TODO.md`

### PCB Design

- Every schematic and PCB must run through KiCad's DRC (Design Rules Checker)
- Resolve all DRC violations or document them in `TODO.md` with the reason
- Production-ready Gerber files required for fabrication
- If a DRC violation requires repositioning a component footprint, **refer the action to the user** — other modifications are allowed

### STL and SCAD

- All models must be clean and watertight; ready to slice for printing
- Any regenerated primary-component STL must be re-baked before publishing
- After SCAD changes, verify Z-range and bore-diameter in console output before committing

### File Management

- Prefer editing existing files over creating new ones
- Do not add features, refactor, or introduce abstractions beyond what the task requires
- Keep `PROJECT_INDEX.md` up to date when adding active files
- Move archived files to `archives/` and update `ARCHIVE_INDEX.md`
- When adding a standards citation, update `REFERENCES.md` with a validated URL and specific section/paragraph

### Git Commits

- **Create NEW commits** rather than amending existing ones (unless explicitly requested)
- Never skip hooks (`--no-verify`) or bypass signing (`--no-gpg-sign`)
- Never force-push to main/master
- Use HEREDOC syntax for commit messages with multi-line bodies:

  ```sh
  git commit -m "$(cat <<'EOF'
  Commit message here.

  Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
  EOF
  )"
  ```

### Coordinate System (Hull Frame)

**All design artifacts use the single validated hull frame:**

- **X** = positive port (left)
- **Y** = positive aft (back)  
- **Z** = positive dorsal (up)
- **Origin** = the SerenityAssembly.FCStd world origin

As of R1 (2026-06-11), placements are **baked into primary STL vertex data** via `tools/bake_hull_frame.py`. Primary components import with identity placement.

## Before You Act

1. **Read `CLAUDE.md`** in full before starting any task
2. **Check for subordinate CLAUDE.md** in the target folder
3. **Verify all standards citations** against `REFERENCES.md` before using them
4. **Check `TODO.md`** for context on ongoing work
5. **Review git history** for recent commits and patterns

## When Adding New Work

1. Add tracking items to `TODO.md` as subtasks in the appropriate section
2. Update `PROJECT_INDEX.md` when adding new active files
3. Update `REFERENCES.md` when adding standards citations
4. Cite applicable standards using REF-IDs
5. Include commit messages explaining the **why**, not just the **what**

## Conflict Resolution

**If you encounter conflicting guidance:**

1. Root CLAUDE.md (project-wide) > Subordinate CLAUDE.md (scope-specific)
1.1. The subordinate CLAUDE.md guidance is authoritative unless excluded by the root CLAUDE.md.
1.2 All conflicts between Root and Subordinate CLAUDE.md **shall** be immediately be brought to the user's attention for adjudication.  No work will procede until adjudication is received.  
2. REFERENCES.md (verified standards) > comments or assumptions
3. Actual code/model state > documentation (if they diverge, update the docs to match reality and investigate why they diverged)

## Questions?

If the task is unclear or you lack required information, **ask the user explicitly** before proceeding. Do not guess or invent details.

---

**Last updated:** 2026-06-30  
**Authoritative file:** [`CLAUDE.md`](CLAUDE.md)
