Repository Enforcement Checklist

This repository follows the authoritative instructions in `AGENTS.md`.
Use this checklist to validate commits, code generation, and design artifacts.

- Project authority: AGENTS.md is the canonical policy and must be referenced in all major changes.
- Licensing: All outputs are dual-licensed by content type — CERN-OHL-W 2.0 for hardware/CAD/PCB, CC BY-SA 4.0 for documentation/code/scripts/drawings (see `docs/attribution_and_licencing.md`). Include attribution in derivative files and commit messages.
- Coding style: 4-space indentation for all code files. Use `.editorconfig` and linters to enforce.
- Fabrication specs: CF-PETG primary structural material; 0.15 mm layer height; 4 perimeters; 40%+ infill for load-bearing parts; shell hollowed to 2.0 mm where required.
- 3D outputs: Output STLs to `airframe/stls/` subdirectories. Verify Z-range and bore-diameter after generation.
- Coordinate standard (Rev R1): all design artifacts use the hull frame (X = +port, Y = +aft, Z = +dorsal; origin = SerenityAssembly.FCStd world origin). Primary-component STLs must be baked to hull frame with `tools/bake_hull_frame.py` after regeneration (header marker `SerenityUAV HULL-FRAME R1`); never re-bake a derivative of an already-baked mesh. Assembly placements are identity — no per-part transforms. Exceptions: avionics KiCad files, Skipper GCS hardware, G-code.
- Blender scripts: Run headless with `blender --background --python <script>.py` per AGENTS.md workflow notes.
- PCB and Gerbers: Provide complete KiCad schematics, PCB files, footprints, and production-ready Gerber exports.
- Attribution: Cite external references in file docstrings or commit messages.
- Safety: Validate weight/balance/power for any hardware changes; quote masses and CG shifts where applicable.

For automation: CI jobs and bots should validate these items where practical (linters, `.editorconfig`, 3D file checks, BOM presence).
