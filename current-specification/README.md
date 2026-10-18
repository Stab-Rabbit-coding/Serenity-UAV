# Serenity UAV — Current Specification (Rev T BOM Baseline)

**License:** By output — CERN-OHL-W 2.0 (hardware and hardware-producing code) / MIT (software/firmware code) / CC BY-SA 4.0 (documents, BOM).
See `docs/attribution_and_licensing.md`.  
**Current design revision (project-wide):** Rev T (2026-09-06, see `docs/WBS.md` §6.4 for
changelog).  
**Last updated:** 2026-10-07

> Bill of Materials, component specifications, and system-level design parameters for
> Serenity UAV in JSON and CSV formats. **`bom_revT.json` / `bom_revT.csv` (2026-09-28) are the
> authoritative baseline for Phase 5 assembly and beyond.** The Rev S files are retained as the
> Rev S checkpoint snapshot.

## Current Status (2026-10-07)

- **Rev T BOM:** 211 rows. It folds in the tilt actuator (Pololu 20D 25:1, six-start worm, pin
  brake), the 3.0 in (76 mm) landing-gear flight article, the cargo chin node shelf and void
  former, measured-mass corrections from `docs/MASS_AUDIT_CARGO_WING_ROOT.md`, and the spider
  sleeve motor mount on the measured 90° pattern.
- **Not yet in the Rev T BOM** (the data lags the design; each is an open item, not a decision
  to defer):
  - **TACCO is 60 × 35 mm** since 2026-10-06; the BOM row still reads 55 × 35 mm.
  - **Commo is one standalone node** under Rev T (approved 2026-09-29); the BOM still carries
    two Rev S sub-module rows. Per `avionics/AGENTS.md`, its mass comes from the PCB roll-up,
    not a hand entry.
  - **PCB masses:** Pilot and TACCO are still placeholder masses until routing closes.
  - **64 mm nacelle:** the 50 mm EDF rows are current. The 64 mm tandem-EDF rows enter after
    the NAC-64 fit, power, and mass gates close (`airframe/wings-nacelles/WBS.md`).
  - **AUW and T/W:** the 3,911 g figure and the 1.14 hover T/W are provisional pending the
    bottom-up AUW ledger recompute (`docs/WBS.md` §0.10.1).
- **Known data defect:** a few rows in the JSON files have parse-shifted `Category` values
  (for example `0`) from unquoted commas in CSV notes; the CSV is the cleaner source until the
  JSON is rebuilt.
- **Interactive viewer:** `serenity-rev-s.jsx` still describes Rev S (STS3215 winch, XO naming);
  it has not been regenerated for Rev T.

> **Note:** "Rev S" appears in the BOM Structure, Quantity Tracking, and Usage sections below
> where those sections describe the file format or workflow; the Rev T files use the same
> schema and workflow.

## Files

| File | Format | Purpose | Coverage |
|------|--------|---------|----------|
| `bom_revT.json` | JSON | **Canonical** structured BOM (Rev T, 2026-09-28): part numbering, supplier links, mass, cost | All components (procured + printed + machined) |
| `bom_revT.csv` | CSV | Flat-file BOM for spreadsheet import; the Rev T mirror of the JSON | Build-tracking sheets, inventory management |
| `bom_revS.json`, `bom_revS.csv` | JSON, CSV | Rev S checkpoint snapshot (2026-07-04), retained for traceability | Superseded by Rev T |
| `serenity-rev-s.jsx` | JSX (React) | Interactive BOM viewer and system schematic (Rev S content; see status above) | Same part list, visual links to subsystems |
| `SPEC_TEMPLATE.md`, `LICENSE_AND_ATTRIBUTION.md` | Markdown | Specification template; creative-universe attribution and fan-engineering terms | — |

## BOM Structure (JSON Schema)

```json
{
  "revision": "T",
  "date": "2026-09-28",
  "description": "Serenity UAV Bill of Materials — Rev S (Comprehensive Checkpoint) | Rev T5b ... change log",
  "items": [
    {
      "Ref": "EDF-50-6S",
      "Description": "50mm EDF unit @ 6S (6- or 12-blade)",
      "Category": "Propulsion",
      "Qty": 4,
      "Unit_Mass_g": 70,
      "Total_Mass_g": 280,
      "Supplier": "AliExpress / Banggood",
      "Supplier_PN_or_Search": "XFly Galaxy X5 50mm 12-blade 6S 3200KV (canonical)",
      "Est_Unit_Price_USD": 28.00,
      "Est_Total_Price_USD": 112.00,
      "Notes": "1240g thrust each; 70g unit mass; verify CW vs CCW rotation before nacelle install"
    }
  ]
}
```

## Component Categories

### Airframe (Printed, Machined, Procured)

- **Fuselage shells** (head, cargo bay, middle, rear sections)
- **Wings & nacelle structures** (printed CF-PETG + carbon-fiber skin)
- **Access panels & hatches** (lids, latches, removable covers)
- **Internals** (cable clips, bosses, tray frames, battery bay)
- **Landing gear** (4130 steel wire, epoxy-bonded; printed mounting brackets)
- **Fasteners & adhesives** (M2.5/M3 nylon standoffs, structural epoxy, foam, gasket tape)

### Avionics (PCBs, Capes, Sensors)

- **SBCs:** 8× PocketBeagle2 Industrial
- **Capes:** 4× Pilot, 4× TACCO (Tactical Coordinator: Comms, Payload, Logs); **Commo** (915 MHz SiK and 49 MHz): 2× Rev S capes in the BOM, one standalone node under Rev T
- **Standalone:** 1× Observer (vision/ToF/laser board, PCM-071 SoM), 1x Flight Engineer (Power Distribution Board)
- **Sensors:** GPS, IMU, barometer, 2× Hall encoders (AK7455), 12× ToF (VL53L5CX), 2× laser
- **Security:** TPM 2.0 (SLB9672) on every Pilot and TACCO cape, an SE on non-SBC nodes (Commo Rev T), 4× CPLD write-blocker (ATF16V8BQL)
- **Connectors & cabling:** USB-C, XT90 PDB, RP-SMA antenna bulkheads, shielded Ethernet/CAN

### Power Distribution

- **Flight Engineer PDB:** 2× 40A fuses, 5V/5A BEC, main bus connectors
- **ESCs:** 4× 40A BLHeli32 (nacelle EDF control)
- **Wiring:** 14 AWG main leads (XT90 → Flight Engineer), 22 AWG signal/logic

### Propulsion

- **EDFs:** 4× XFly Galaxy X5 50 mm (6S, 3200 KV, 12-blade rotor, 11-fin stator)
- **Servos:**
  - 2× SPT5425LV + LibreServo v2 (nacelle tilt, was DS3218MG)
  - 1× SPT5425LV + LibreServo v2 (winch motor, continuous rotation + encoder feedback, was STS3215)
  - SG90 + OpenServoCore (door actuator, payload release)

### Cargo System

- **Cargo shell** (printed CF-PETG, with clamshell door halves; the separate gondola shell was superseded 2026-09-15)
- **Winch mechanism:**
  - SPT5425LV + LibreServo v2 servo (continuous rotation, was STS3215)
  - Twin pedestal spool (magnetic brake ratchet)
  - Dyneema line (2 mm, 3 m length, 100 lb break strength)
  - Auto-latch and payload release solenoid
- **Door actuator:** SG90 servo, spring-assist open

### Comms & Sensors

- **Radios:**
  - SiK RFD900ux-SMT (915 MHz MAVLink), on Commo
  - XCVR-49MHZ-1/2 (SI5351-based, 49 MHz Part 15 §15.235), on Commo
  - mLRS on a bare STM32WLE5JC, on every TACCO
  - Wi-Fi 5 GHz on every TACCO (USB module on the PB2's USB1; module selection open)
  - ZigBee 2.4 GHz on every TACCO (Murata Type 2EL; 802.15.4 on SPI0)

- **Antennas:**
  - 49 MHz wire posts (forward + aft, Part 15 §15.235 compliance)
  - SMA bulkhead connectors (SiK + XCVR) and U.FL jacks on TACCO (Wi-Fi/ZigBee radio, mLRS)
  - Omni WiFi antenna (2.4/5 GHz, 5 dBi gain)

### Support / Structure

- **Keel rod:** 4 mm carbon-fiber rod (structural spine, tilt pivot mount)
- **Ring frames:** Epoxy-bonded nylon, stations at 0, 150, 300, 450, 600 mm
- **Epoxy:** Structural (2-part, 2 h cure) for fuselage bonds, foam casting
- **Foam:** 2 lb/ft³ PU (density: 0.032 g/cm³), fills hull interior
- **Paint / protection:** Matte polyurethane clear coat (UV protection)

## Quantity Tracking

| Phase | Description | Key BOM Items | Qty Complete | Status |
|-------|-------------|----------------|--------------|--------|
| 0 | Print all parts | All fuselage/nacelle/wing STLs | ~66 STLs | Ready |
| 1 | Hull structure | Keel, ring frames, access panels, standoffs | — | Design complete |
| 2 | Nacelle assembly | EDFs, servo-driven nozzles | — | CAD complete (50 mm); 64 mm redesign in progress |
| 3 | Tilt mechanism | Servo mounts, pivot rod, linkages | — | CAD complete |
| 4 | Hull foam & close | Foam pour, panel lids | — | Ready |
| 5 | Avionics (4 nodes, minimal) | Pilot/TACCO on Shepherd + Inara, ESCs | — | Pilot and TACCO placed, DRC 0; routing open |
| 6 | Full 8-node architecture | All 8 nodes + Commo + Flight Engineer + Observer | — | Flight Engineer, Commo Rev T, and Observer PCBs open |
| 7 | Cargo system | Cargo shell, winch, servo, solenoid | — | CAD in progress (`airframe/fuselage-mid/WBS.md`) |
| 8 | Finishing | Decals, documentation | — | Awaiting first flight |
| 9–10 | Flight tuning & extended range | Gimbal tracking | — | Deferred |
| 11+ | Aft EDF + RCS | 55 mm EDF, valve manifold, nozzle | — | Deferred |

## Revision History

- **Rev T BOM** (2026-09-28): `bom_revT.json` / `.csv` published (see Current Status above).
- **Rev T** (2026-09-06): Wings Rev S1g (fixed CF spar, geared tilt drive) and nacelles Rev
  S4c (hollowed pods, hinged ESC bays, 4x90° motor pattern) integrated; avionics/BOM carried
  forward from Rev S **unrecomputed** — see the BOM-currency note at the top of this file.
- **Rev S** (2026-07-04): Baseline for Phase 5; 24-inch hull, 8-node PACE, Flight Engineer/Observer, Pilot/TACCO/Commo/Flight Engineer/Observer Rev S1 PCBs
- **Rev R1** (2026-06-11): 24-inch hull final, hull-frame coordinate std baked into STLs, Nacelle CG tuning (PIVOT_Z = 111.5 mm)
- **Rev R** (2026-04-XX): First 24-inch hull iteration, pre-PIVOT_Z tuning
- **Rev Q** (2026-02-XX): Last 18-inch baseline; 8-node architecture finalized
- **Rev P & earlier:** Historical prototypes (DaVinci Jr, 18-inch predecessor)

See `docs/WBS.md` §6.4 for the full Rev T changelog and §6.3 for the Rev S changelog and
component-level deltas from Rev R1.

## Part Cross-References

Every part in the BOM has a cross-reference to:

- **Schematic net / PCB footprint** (avionics parts) — link to `avionics/kicad/<board>/<board>.kicad_sch`
- **SCAD/CAD model** (printed parts) — link to `.scad` generator or STL file path
- **Datasheet** (ICs, sensors, mechanical parts) — link to PDF via REFERENCES.md `[REF-*]` ID
- **Supplier page** (procured items) — direct URL to part listing (Digi-Key, Mouser, Amazon, etc.)

## Usage

### For Bill of Materials

1. Export `bom_revT.csv` to spreadsheet (LibreOffice Calc, Excel, Google Sheets)
2. Add columns for:
   - Order date, delivery date, received qty, unit cost verified
   - Bin location (for inventory tracking)
   - Subcategory total cost (sum by subsystem)
3. Cross-reference against `serenity-rev-s.jsx` for linked supplier pages

### For Assembly / Build Guide

1. Use `bom_revT.json` as the source of truth for mass budget, CG, and part naming
2. Build-guide phase checkpoints reference part ID (e.g., "Install SYS-001 (head shell) using
   structural epoxy per Phase 1 procedures")
3. Every assembly step links back to a specific part or assembly in the BOM

### For Design Changes

1. Update the affected row in `bom_revT.json` (mass, dimensions, supplier link) and mirror it in `bom_revT.csv`
2. Use `tools/compact_bom_entries.py` or the `tools/bom_edit_*.py` helpers for scripted edits (there is no `tools/update_bom.py`)
3. Update the revision marker (`date` field) and commit with a message referencing the design change

## Tools

- **`tools/compact_bom_entries.py`, `tools/bom_edit_*.py`** — scripted BOM edit helpers
- **`serenity-rev-s.jsx`** — React component to render the interactive BOM viewer (Rev S content)
- **`REFERENCES.md`** — Catalog of all supplier links, datasheets, and regulatory citations

## License

All BOM files are **CC BY-SA 4.0**.

See root [`LICENSE`](../LICENSE) and [`docs/attribution_and_licensing.md`](../docs/attribution_and_licensing.md)
for full details.

---

*"Everything is shiny." — Kaylee Frye*
