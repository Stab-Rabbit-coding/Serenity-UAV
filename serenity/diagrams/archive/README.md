# Build Guide Archive

Pre-Rev-O versions of the build guide SVGs are preserved in git history.

To recover an original file:

```bash
git show <parent-commit-sha>:serenity/diagrams/<filename>.svg > archive/<filename>_pre-revo.svg
```

The 2026-05-25 Rev O update (commit on branch `claude/todo-implementation-8bRee`)
replaced all 34 SVG files with:

- Rev O component names, dimensions, and specs throughout
- STL-derived hull geometry silhouettes in overview_side/top/front/bottom
- Corrected CG (203 mm), GPS station (140 mm dorsal), step counts (X/26)

Generator scripts (in `serenity/diagrams/`):
- `probe_stl.py`           — reports STL bounding boxes (diagnostic)
- `gen_hull_outlines.py`   — generates standalone hull_*.svg reference files
- `update_overview_paths.py` — updates hull paths in the four overview SVGs

© 2026 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP — CC BY 4.0
