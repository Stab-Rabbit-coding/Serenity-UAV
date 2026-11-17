# Serenity UAV — Deferred Work (Phase 11+) Work Breakdown Structure

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Current design revision:** Rev U (2026-11-03, see `docs/WBS.md` §6.5 for changelog)

> **Status note, 2026-11-16 (design shift).** The tail EDF, its speed controller and the RCS are
> no longer deferred: they are part of the first build (owner, 2026-11-15). The tail EDF is the
> QX-Motor 64 mm nacelle unit, not a 55 mm unit. The neck-scoop, plenum and bleed-tap items below are closed as
> superseded (2026-11-16 document review); the remaining Phase 11 items stay as written until
> WBS item TEDF-01 rewrites them. Authority: `airframe/fuselage-mid/WBS.md` §1.1.1.4.0 and
> `docs/plans/2026-11-15-002-feat-ramp-intake-edf-cooling-plan.md`.

> **Detail-holder for the root WBS.** The repository-root [`TODO.md`](../TODO.md)
> is a compact index — headings, subheadings, and short (<=70-char) checkbox items
> only, per root `AGENTS.md`. This file carries the full task detail for the WBS
> branches root indexes below. Close an item here first, then check it off in the
> root index as a commit prerequisite (root `AGENTS.md` "Revisions and Version
> Control"). **&#9733; = the branch is on the critical path to first flight (Phase 5).**

*"We will rise again. — Mr. Universe"*

---

## Owned WBS branches — open-item summary

| Master § | Branch | Open | First flight |
|----------|--------|-----:|:------------:|
| §Phase11 | Phase 11 — Aft EDF Integration (dissolved 2026-11-17) | 0 | — |
| §Phase12 | Phase 12 — Cargo-bay Range-Extender Battery Module (promoted 2026-10-26) | 0 | — |
| | **Total open (this subsystem)** | **0** | |

---


> **Phase 12 (Range-Extender Battery Module)** rides in the cargo bay on the same Observer hooks/release and adds a `J_BATT2` input to Flight Engineer — a cruise-range, not hover, enhancement. See the Observer cross-cutting map in [avionics/kicad/Observer/observer/TODO.md](../avionics/kicad/Observer/observer/TODO.md).


## §Phase11 — Aft EDF Integration (Deferred)

*(root `WBS.md` §Phase11)*

> **Moved 2026-11-17 (owner):** the open steps and pass criteria of this section are first-build work and now live in `graphical-build-guide/flight-phases/WBS.md` §Phase5 (tail EDF, speed controller and RCS parts, installation, firmware, ground tests and pass criteria) and §Phase9 (forward-thrust schedule and test). Only the superseded pre-shift records remain below.

- [x] (superseded 2026-11-16 by TEDF-01: no neck scoops, plenum or bleed taps; the QX 64 mm tail EDF draws through the sealed cargo duct, plan 002) Print `rear_neck_intake_shell24.stl` from `deferred/aft-edf/openscad/rear_neck_intake_shell24.scad`. Verify NECK_X ≈ 310mm alignment in slicer. **Scoop windows must be re-sized for the 55 mm EDF (reduced area).**
- [x] (superseded 2026-11-16 by TEDF-01: no neck scoops, plenum or bleed taps; the QX 64 mm tail EDF draws through the sealed cargo duct, plan 002) Remove temporary window covers from existing neck shell, or swap in the new windowed shell if a plain shell was used for Phases 0–10.
- [x] (superseded 2026-11-16 by TEDF-01: no neck scoops, plenum or bleed taps; the QX 64 mm tail EDF draws through the sealed cargo duct, plan 002) **Regenerate** `neck_intake_frame.scad` for the 55 mm intake area; print `neck_intake_frame.stl` (CF-PETG, 0.15mm, 40% gyroid, 4 walls).
- [x] (superseded 2026-11-16 by TEDF-01: no neck scoops, plenum or bleed taps; the QX 64 mm tail EDF draws through the sealed cargo duct and the RCS jets are apertures in the thrust tube, plan 002) **Regenerate** `aft_edf_plenum.scad`: 55 mm circular EDF inlet + 4 RCS bleed taps (~15% flow); print `aft_edf_plenum.stl` (CF-PETG, 0.20mm, 20% gyroid) — EDF housing, treated as structural per CLAUDE.md Fabrication Standards.
- [x] (superseded 2026-11-16 by TEDF-01: no neck scoops, plenum or bleed taps; the QX 64 mm tail EDF draws through the sealed cargo duct and the RCS jets are apertures in the thrust tube, plan 002) Dry-fit `neck_intake_frame.stl` into the resized scoop windows; registration tongues insert with ~0.2mm clearance (sand if tight).
- [x] (superseded 2026-11-16 by TEDF-01: no neck scoops, plenum or bleed taps; the QX 64 mm tail EDF draws through the sealed cargo duct, plan 002) Verify aerodynamic orientation: intake lips face forward (−Y / nose-ward).
- [x] (superseded 2026-11-16 by TEDF-01: no neck scoops, plenum or bleed taps; the QX 64 mm tail EDF draws through the sealed cargo duct, plan 002) Apply structural epoxy to tongues + shoulder flanges; press frame into position; clamp; cure 24h.
- [x] (superseded 2026-11-16 by TEDF-01: no neck scoops, plenum or bleed taps; the QX 64 mm tail EDF draws through the sealed cargo duct, plan 002) Fillet all gaps between flange and hull; cure 2h.
- [x] (superseded 2026-11-16 by TEDF-01: no neck scoops, plenum or bleed taps; the QX 64 mm tail EDF draws through the sealed cargo duct and the RCS jets are apertures in the thrust tube, plan 002) Dry-fit `aft_edf_plenum.stl`; verify intake arm alignment and 55mm EDF inlet centered.
- [x] (superseded 2026-11-16 by TEDF-01: no neck scoops, plenum or bleed taps; the QX 64 mm tail EDF draws through the sealed cargo duct and the RCS jets are apertures in the thrust tube, plan 002) Bond plenum forward arms to intake frame exits; fillet joints; cure 2h.
- [x] (superseded 2026-11-16 by TEDF-01: no neck scoops, plenum or bleed taps; the QX 64 mm tail EDF draws through the sealed cargo duct and the RCS jets are apertures in the thrust tube, plan 002) Bond `rcs_distribution_manifold.stl` to the 4 plenum bleed taps; route 4 bleed ducts to the RCS jet locations.
- [x] (superseded 2026-11-16 by TEDF-01: no neck scoops, plenum or bleed taps; the QX 64 mm tail EDF draws through the sealed cargo duct and the RCS jets are apertures in the thrust tube, plan 002) Pressure-test: seal EDF face with tape; cover all but one scoop; shop-vac — confirm draft at EDF inlet and at all 4 RCS jets, no joint leakage.
- [x] (superseded 2026-11-16 by TEDF-01: no neck scoops, plenum or bleed taps; the QX 64 mm tail EDF draws through the sealed cargo duct and the RCS jets are apertures in the thrust tube, plan 002) Seat EDF in plenum 55mm inlet; press forward to retaining lip; bond with 4 dabs slow-cure epoxy.
- [x] (superseded 2026-11-16 by TEDF-01: no neck scoops, plenum or bleed taps; the QX 64 mm tail EDF draws through the sealed cargo duct and the RCS jets are apertures in the thrust tube, plan 002) Intake frame tongues fully seated in the resized scoop windows


## §Phase12 — Cargo-bay Range-Extender Battery Module (PROMOTED 2026-10-26)

*(root `WBS.md` §Phase12)*

> **Superseded 2026-10-26 (owner):** no longer deferred. The work moved into the active build as
> `docs/plans/2026-10-26-001-feat-split-battery-head-rail-plan.md` and
> `docs/plans/2026-10-26-002-feat-fe-multi-battery-pdb-plan.md`. The items below are kept as
> the original concept record only.

- [x] (superseded 2026-10-26 by plans 001/002) **RBM module:** 6S LiPo (matched 4000 mAh recommended) + BQ76930-class BMS + ideal-diode
    ORing output, in a tray retained by the same Observer cargo hooks/release (jettisonable),
    with a keyed XT60 pigtail.
- [x] (superseded 2026-10-26 by plans 001/002) **Flight Engineer input:** add `J_BATT2` (XT60) + `F_BATT2` + an ideal-diode / current-share
    combiner (LTC4359- or LTC4370-class — a NEW part family) OR-combining `J_BATT`/`J_BATT2`
    into VBAT: hot-swap-safe across SoC mismatch, reverse-blocking so a faulted/absent RBM
    can't drain or back-feed the main pack. (Flight Engineer board revision — not yet in KiCad.)
- [x] (superseded 2026-10-26 by plans 001/002) **Current sharing:** same pack model + matched-SoC at takeoff (or LTC4370 to force
    balanced sharing); simple diode-ORing alone lets the higher-SoC pack hog.
- [x] (superseded 2026-10-26 by plans 001/002) **Firmware (`pwr_fault`):** add a second-pack context (V/I/SoC over the existing
    telemetry) + combiner PGOOD/fault logging; on RBM fault, isolate and continue on the main
    pack (RTH).
- [x] (superseded 2026-10-26 by plans 001/002) **W&B:** add the RBM to the §14 moment table; re-balance on the keel rail and verify on
    the physical CG rig before flight (a second ~750 g mass in the cargo bay shifts CG).
- [x] (superseded 2026-10-26 by plans 001/002) **CAD:** RBM tray + retention on the cargo-bay payload envelope; verify cargo-door and
    Observer clearances.
