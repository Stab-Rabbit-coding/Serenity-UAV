# Stale File Archive — 2026-06-01

**Archived by:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**Archive date:** 2026-06-01
**Reason:** Documentation scrub for Rev P baseline. Files below were stale, duplicated,
or superseded as of the Rev P documentation pass. Retained here for provenance and
traceability; not part of the active build.

---

## Archived Files

### `antenna-layout.jsx`

- **Original location:** `airframe/antenna-layout.jsx`
- **Why archived:** Duplicate of `serenity/artifacts/antenna-layout.jsx`. Root-level
  `airframe/` directory was a legacy staging area from early project iterations; the
  canonical artifact lives under `serenity/artifacts/`.

### `cm4-carrier-update.jsx`

- **Original location:** `controllers/cm4-carrier-update.jsx`
- **Why archived:** CM4 carrier board era (Rev E–J). Superseded when avionics were
  redesigned to PocketBeagle 2 Industrial (AM6254) nodes in Rev K. All CM4-era
  controller design files are obsolete.

### `pico2-hat.jsx`

- **Original location:** `controllers/hats/pico2-hat.jsx`
- **Why archived:** TRIHAT-1 / RP2040 Pico 2 hat era (Rev A–D). Superseded first by
  CM4 carrier (Rev E), then by PB2-I nodes (Rev K). Retained for design history.

### `comms-hat.jst`

- **Original location:** `controllers/hats/comms-hat.jst`
- **Why archived:** CM4-era comms hat specification stub (note: `.jst` extension, not
  `.jsx` — likely a typo or draft artifact). Superseded by Cape-B design in Rev K.
  Retained for provenance.

### `overview_side.svg`

- **Original location:** `overview_side.svg` (repository root)
- **Why archived:** Duplicate of `serenity/diagrams/overview_side.svg`. The canonical
  SVG diagrams directory is `serenity/diagrams/`. Root-level copy was stale.

### `airframe-stls/`

- **Original location:** `airframe/STLs/fuselage.md` (and the `airframe/STLs/`
  directory stub)
- **Why archived:** Early-project documentation stub with no substantive content.
  All current STL documentation is in `serenity/docs/bom_revP.json`,
  `serenity/docs/bom_revP.csv`, and `serenity/docs/PROJECT_INDEX.md`.

### `files-revF/`

- **Original location:** `files/` (repository root — entire directory)
- **Why archived:** Rev F era file collection (2025). Contains CM4-CARRIER-1, TRIHAT-1,
  COMMS-HAT-1 KiCad files, early STLs (nacelle_pod_70mm, sector_gear_22mm, hull sections),
  Rev F SVG diagrams, and the `serenity-drone-revF.zip` archive. All superseded by:
  - KiCad: `serenity/kicad/` (Cape-A, Cape-B, XCVR-49MHZ-1 — Rev K/O design)
  - STLs: `thingverse-serenity/files-hollowed-18in/` (24-inch Rev P design)
  - Diagrams: `serenity/diagrams/` (current)
  The `serenity-drone-revF.zip` file in `files-revF/` is a complete snapshot of the
  Rev F project state and is retained here as a historical archive artifact.

---

## Removed Empty Directories

The following directories were emptied by archiving and then removed from the tree:

- `airframe/` — contained only `antenna-layout.jsx` (archived above) and the `STLs/`
  stub directory
- `controllers/hats/` — contained only `pico2-hat.jsx` and `comms-hat.jst` (both archived)
- `controllers/` — contained only `cm4-carrier-update.jsx` (archived) and the `hats/`
  subdirectory
- `files/` — entire Rev F directory archived to `files-revF/`

---

## Active Canonical Locations (Post-Archive)

| Resource | Canonical Location |
|----------|--------------------|
| JSX specification artifacts | `serenity/artifacts/` |
| SVG engineering diagrams | `serenity/diagrams/` |
| KiCad PCB source files | `serenity/kicad/` |
| STL 3D print files | `thingverse-serenity/files-hollowed-18in/` |
| SCAD parametric sources | `serenity/stl/` |
| Bill of materials | `serenity/docs/bom_revP.json`, `bom_revP.csv` |
| Build documentation | `serenity/docs/REVN_BUILD_GUIDE_24IN.md`, `TODO.md` |
| Current specification | `serenity/artifacts/serenity-rev-p.jsx` |

---

*© 2026 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP — CC BY 4.0*
