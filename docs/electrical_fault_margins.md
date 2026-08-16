# Serenity UAV — Electrical Fault Margin Validation

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Revision:** Rev S (2026-07-12)

Resolves `TODO.md` Phase 0 pre-print documentation gate item "Electrical
Fault Margin Validation." This document is a **pointer, not a duplicate** —
the substantive analysis for three of the four required checks was already
performed and documented in `docs/POWER_DISTRIBUTION.md` §9 ("Electrical
Fault Margin Validation") and §11 ("Redundant Power Rail Strategy") before
this file existed. Per the DRY convention already used elsewhere in this
repository (e.g. `TACCO.md`'s creepage/clearance rule inheriting Wash's by explicit
reference rather than restating it), this document cites that analysis
instead of re-deriving it, and performs the one check that had no existing
home.

## 1. Maximum ESC Short-Circuit Current and Fuse Break Time

**See `docs/POWER_DISTRIBUTION.md` §9.1 "ESC Fuse Sizing Validation" and
§5 "Fuse Coordination."** Summary: 40 A mini-blade fuses (`FUSE-ESC-40A`)
are coordinated with 10 AWG silicone wire (55 A free-air rating, derated to
~48 A at 45°C nacelle ambient); at the fuse's derated 32 A continuous
rating, a sustained 40 A ESC fault operates the fuse at 125% of its derated
point, tripping in < 60 s per the Littelfuse time-current curve — well
before the 90°C wire insulation limit is approached. **Conclusion (already
established): correctly coordinated.**

The originating WBS item also named "XT30 + 100A poly fuse" — that
combination does not appear in the current FlightEngineer BOM (`current-specification/bom_revS.csv`
lists `FUSE-ESC-40A`, a 40 A mini-blade fuse per ESC, plus a 150 A MAXI main
fuse, `docs/POWER_DISTRIBUTION.md` §5). No 100 A poly (resettable PTC) fuse
is specified anywhere in this design. This is a stale component reference
in the original WBS item text, not a missing design element — the
mini-blade + MAXI fuse coordination above supersedes it. Flagged in
`TODO.md` rather than silently corrected in the WBS item text.

## 2. BEC Brown-Out Threshold

**See `docs/POWER_DISTRIBUTION.md` §9.2 "BEC Brown-Out Threshold."**
Summary: TPS54620 5 V BEC output tolerance is ±2%, giving a 4.90 V minimum
output — a 0.40 V margin above the PocketBeagle 2 Industrial's 4.75 V
absolute minimum VIN (AM6254 boot ROM requires ≥ 4.5 V; PB2-I board adds
margin to 4.75 V). The BEC's own minimum operational input (9.5 V) is well
below the 18.0 V battery EMERGENCY cutoff, so the BEC cannot brown out
before the battery protection state machine (`docs/failsafe_thresholds.md`
§1) has already acted. **Conclusion (already established): ≥ 4.90 V
maintained; matches this WBS item's target exactly.**

## 3. Main Bus Fuse Sizing

**See `docs/POWER_DISTRIBUTION.md` §9.4 "Main Bus Fuse Sizing Validation."**
Summary: at 90 A sustained hover current, the 150 A MAXI fuse operates at
60% of rating (no trip). At a worst-case simultaneous-burst peak of 165 A
(all four EDFs at absolute burst + all radios transmitting — a transient
condition, < 1 s duration), the fuse operates at 110% of rating, requiring
60–120 s to trip per the Littelfuse time-current curve — far longer than
the burst duration, so no nuisance trip occurs. **Conclusion (already
established): correctly sized**, with a peak-current figure (165 A) close
to, and slightly more conservative than, this WBS item's own "4× EDF ESCs
(4× 40A) = 160A nacelle peak" estimate (the 165 A figure additionally
accounts for simultaneous radio TX load, per §3.1 of `POWER_DISTRIBUTION.md`).

## 4. Balance of Plant — Single PWR Conduit/Rail Segment Loss

**Not previously covered as a standalone check — addressed here.**

The shared 5 V avionics bus is explicitly documented as a **single rail,
not hardware-redundant** (`docs/POWER_DISTRIBUTION.md` §11, opening
sentence). The mitigations already in place are:

- **SMPS-level redundancy:** two independent TPS54620 5 V regulators on
  FlightEngineer, Schottky diode-OR'd (`docs/POWER_DISTRIBUTION.md` §11). If one
  SMPS channel fails, the other alone carries up to 6 A — sufficient for
  the 5 V rail's ~10 A nominal load only if load shedding (§8.3) has
  already reduced demand; a full-load single-channel failure without
  shedding **will** brown out some nodes. This is the honest limit of the
  current mitigation, not glossed over here.
- **Node-level isolation:** each Wash bay's power connector (J-PWR, Molex
  Nano-Fit) is independently disconnectable; any one FC+CN node pair can be
  removed from service without affecting the other three bays'
  connectors (`docs/POWER_DISTRIBUTION.md` §11).
- **Faraday-bay isolation:** each avionics bay's copper-foil EMI shielding
  also functions as a physical fault boundary — a short-circuit fault
  local to one bay's Cape (BEC current-limiting) does not propagate to the
  bus feeding other bays (`docs/POWER_DISTRIBUTION.md` §11).

**Conclusion:** loss of a single SMPS *channel* is tolerated (diode-OR'd
redundancy, with a load-shedding-dependent capacity limit noted above).
Loss of a single **rail wiring segment/tap** downstream of the FlightEngineer PDB
(e.g., a severed or shorted conduit run to one bay) is *not* redundant at
the wiring level — it isolates that bay's power feed with no alternate
path, mitigated only by that bay's PACE tier having its watchdog/comms/
flight-control/payload role picked up by another bay per the PACE failover
table (root `AGENTS.md`), not by the electrical design itself. This is an
architectural choice (avionics-role redundancy substituting for power-wiring
redundancy) rather than an unaddressed gap, but it should be stated plainly
rather than implied — this document states it plainly.

---

## Summary Table

| Check | Result | Source |
|---|---|---|
| ESC short-circuit / fuse break time | Correctly coordinated (40 A mini-blade + 10 AWG) | `POWER_DISTRIBUTION.md` §9.1 |
| BEC brown-out threshold | ≥ 4.90 V, 0.40 V margin | `POWER_DISTRIBUTION.md` §9.2 |
| Main bus fuse sizing | Correctly sized (150 A MAXI, 165 A peak = 110%, > 60 s to trip) | `POWER_DISTRIBUTION.md` §9.4 |
| Single PWR rail segment loss | Node/bay-level isolation + SMPS diode-OR; wiring-level redundancy is NOT present, mitigated by PACE role failover instead | `POWER_DISTRIBUTION.md` §11 + this document §4 |

---

*"Everything is shiny, Cap'n. Not to fret." — FlightEngineer, whose engine room this
power budget ultimately answers to.*
