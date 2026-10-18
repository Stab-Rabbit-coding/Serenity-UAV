# Serenity Avionics — KiCad Board Index and Status

**Last updated:** 2026-10-07
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)

This directory holds the KiCad projects, generator scripts, and status files for every Serenity
avionics board. **Each board's own `.md` file is the authoritative as-built status**
(`avionics/AGENTS.md`, "Cape Naming and Revision History"); the table below is a dated
snapshot, so confirm against the board file before relying on it for fabrication or integration.
KiCad files keep KiCad board coordinates (a documented exception to the hull-frame standard,
see root `AGENTS.md`).

## Boards

| Folder | Board | Role | Status file |
| --- | --- | --- | --- |
| `Pilot/` | **Pilot** | PB2-I cape: flight control and sensors | `Pilot/Pilot.md` |
| `TACCO/` | **TACCO** | PB2-I cape: comms, logging, payload | `TACCO/TACCO.md` |
| `FlightEngineer/` | **Flight Engineer** | Power Distribution Board (PDB) | `FlightEngineer/FlightEngineer.md` |
| `Commo/` | **Commo** | 49 MHz + SiK transceiver; Rev S was a PB2-I cape, Rev T is a standalone bus node | `Commo/Commo.md` |
| `Observer/` | **Observer** | Standalone nose/cargo-bay vision, ToF, and laser board | `Observer/Observer.md` |
| `Bus-Gateway/` | **CAN-PERIPH-GW-1** | Secure CAN-FD / RS-485 edge node | `Bus-Gateway/CAN-PERIPH-GW-1.md` |
| `Encoder/` | **ENC-NACELLE-1** | Nacelle tilt-angle encoder (AK7455) | `Encoder/ENC-NACELLE-1.md` |

The legacy working name "XO" for TACCO survives only in some script and file names.

## Status snapshot (2026-10-07)

| Board | ERC | DRC | Placement | Routing | Gerbers |
| --- | --- | --- | --- | --- | --- |
| Pilot | 0 errors | 0 errors, parity 0 | 120 of 120 placed | Not started (0% routed) | Open |
| TACCO | 0 errors | 0 errors, parity 0 (before routing) | 163 parts placed on a 60 × 35 mm outline | Not started (0 segments) | Open; the checked-in set predates the rebuild |
| Flight Engineer | 0 errors | 29–31 hard violations | 151 of 151 placed | Not started | Open |
| Commo | Rev S: 0 errors | Rev S closed, not worked further | Rev T in design | Rev T outline and placement open | Rev S Gerbers will not be built |
| Observer | 0 errors | 124 hard violations | Initial shelf-pack; PCB predates the schematic | Not started; PCB resync not started | Open |
| Bus-Gateway | 0 errors | 1 hard violation | Placed (`N_STACKS=4`) | About 84% routed | Generated at that state |
| Encoder | 0 errors | 0 hard violations | Complete | Complete | Open item: firmware and bench calibration |

Pilot and TACCO both use Samtec TSM-118-04-L-DV-LC male SMT rails at 4.80 mm from each long
board edge (PB2 System Reference Manual Fig. 3.45, REF-SENSOR-041). A fab blocker is open on
TACCO: the owner has yet to select the USB Wi-Fi module (`avionics/WBS.md` §1.2a). The open-item
list for every board is in `avionics/TODO.md`; the full record is `avionics/WBS.md`.

## Supporting files

| Path | Purpose |
| --- | --- |
| `PB2_HEADER_PINMAP.md` | Verified PocketBeagle 2 P1/P2 ball-by-ball map and the TACCO allocation |
| `HI6138_FOOTPRINT_VERIFICATION.md` | Holt HI-6138 (MIL-STD-1553C) pin table and area budget |
| `Serenity-Custom.pretty/`, `symbols/` | Project footprint and symbol libraries |
| `tools/swap_1553_hi6138.py` | The fleet 1553C swap script (this folder's `tools/`) |
| `gerbers/` | Legacy Rev S1 Gerber sets; per-board sets are under each board folder (check its status file for currency) |
| `TODO-1.2b-*.md` | **Superseded** 2026-07-18 task snapshots; the live record is `avionics/WBS.md` §1.2a |

## Design method

Pilot, TACCO, Flight Engineer, and the Bus-Gateway use a **schematic-first generator** workflow:
a Python generator under `<board>/scripts/` writes both the schematic and the PCB, so the two
stay in parity. Edit the generator, not the generated files, except where a board file says the
owner has taken manual control of placement. Final component placement is the owner's
(root `AGENTS.md` §5); refer any DRC violation that needs a footprint moved to the owner.
Every schematic or PCB edit needs a KiCad ERC and DRC pass (root `AGENTS.md` §7).

## Toolchain findings (headless KiCad 9 and freerouting)

Recorded so the next contributor does not re-derive them:

- **`pcbnew.ExportSpecctraDSN()` does not work in standalone Python** under KiCad 9.0.2: it
  returns `False` because there is no GUI context. The project uses a custom headless Specctra
  DSN exporter and SES importer (repo-root `tools/export-specctra-dsn.py`, `tools/import-specctra-ses.py`)
  that round-trip correctly.
- **freerouting 2.2.4** exits by itself after its passes and gave the Bus-Gateway its ~84%
  route. Run it without a display, with `-mt 1`. It writes the `.ses` only at the end of a run,
  and its passes take minutes each, so budget the full run. The earlier 2.1.0 build never
  self-exited and captured only a handful of nets; do not use it.
- **Pilot's two runs were rejected** (see "Routing status" in `Pilot/Pilot.md`): automated
  results that introduced shorts are reported, not accepted.
- Route the impedance-controlled Ethernet pairs interactively, length-matched, regardless of
  autorouter results.
- The tamper-mesh rework (per-domain meshes, tamper signals for TPM-less boards) is open
  work in `avionics/WBS.md` §1.2a.1.

---

*Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP · License: CC BY-SA 4.0*
