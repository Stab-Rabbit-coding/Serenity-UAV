# Root README Deep-Dive Sections — Archived 2026-08-03

**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0
**Archive date:** 2026-08-03

## Why archived

The root `README.md` was redesigned 2026-08-03 (Rev S2) into a compact front-page summary — hero
image, license/status badges, a two-column mission profile / specifications layout, and a
subsystem card grid that links out to each subsystem's own README or the relevant canonical
design doc. The full engineering prose that used to live directly under `## Airframe`,
`## Powerplant`, `## Avionics`, and `## Cargo Handling — Observer` in the root README has been
superseded as the *primary* reference by those more specific, actively-maintained documents and
is preserved here verbatim for historical reference and traceability.

`deep_dive_sections.md` in this directory is the exact text of those four sections as they read in
`README.md` immediately before the redesign (commit `56eeb02`, the tip of `main` when the redesign
branch was cut). Nothing was reworded or corrected on the way in — this is a snapshot, not a
rewrite.

## Superseded by

| Original root README section | Canonical location now |
|---|---|
| Airframe — Coordinate Standard, Fuselage, Compartments and Bays, Wings | `airframe/README.md` |
| Airframe — Nacelles | `airframe/README.md`, `docs/NOZZLE_DRIVE_TRADE.md` (nozzle/tilt mechanism) |
| Airframe — Landing Gear | `docs/LANDING_GEAR_ANALYSIS.md` |
| Powerplant — Power Distribution, Battery, Propulsion, Servos and Motors | `docs/POWER_DISTRIBUTION.md`, `airframe/README.md` |
| Avionics — Ground Control (Skipper), Onboard 8-node architecture | `avionics/README.md`, `gcs/README.md` |
| Cargo Handling — Observer | `docs/CARGO_WINCH_SPECIFICATION.md`, `avionics/kicad/Observer/Observer.md` |

Root `README.md` now carries only a short 1–2 sentence summary and a link per subsystem; see it
for the current subsystem index.
