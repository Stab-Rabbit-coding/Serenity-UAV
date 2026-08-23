# Serenity UAV — Current Specification (Rev S Baseline)

**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0  
**Current design revision:** Rev S (2026-07-04)

> Bill of Materials, component specifications, and system-level design parameters for
> Serenity UAV in JSON and CSV formats. **This is the authoritative baseline for Phase 5
> assembly and beyond.**

## Files

| File | Format | Purpose | Coverage |
|------|--------|---------|----------|
| `bom_revS.json` | JSON | **Canonical** structured BOM: part numbering, supplier links, mass, CG, cost | All components (procured + printed + machined) |
| `bom_revS.csv` | CSV | Flat-file BOM for spreadsheet import; derived from `bom_revS.json` | Import into build-tracking sheets, inventory management |
| `serenity-rev-s.jsx` | JSX (React) | **Current** interactive BOM viewer + system schematic (web/desktop app) | Same part list, visual links to subsystems, CAD references |
| `serenity-rev-r.jsx` | JSX (React) | **Archived** Rev R viewer (legacy; maintained for reference only) | Use `serenity-rev-s.jsx` for current Rev S baseline |
| `parts/` | CSV per subsystem | Breakdown by domain: airframe, avionics, power, cargo | Detail-level procurement checklists |

## BOM Structure (JSON Schema)

```json
{
  "metadata": {
    "revision": "Rev S",
    "date": "2026-07-04",
    "hull_length": "609.6 mm (24 in)",
    "auw": "3911 g (Phase 5-10, nacelles only)",
    "design_phase": 5
  },
  "bom": [
    {
      "id": "SYS-001",
      "category": "Airframe",
      "subcategory": "Fuselage",
      "description": "Head shell (printed CF-PETG)",
      "qty": 1,
      "unit": "ea",
      "print_or_procure": "printed",
      "material": "CF-PETG",
      "specs": {
        "wall_thickness": "2.0 mm",
        "infill": "40%",
        "mass": "~ 45 g",
        "layer_height": "0.15 mm"
      },
      "supplier": "print in-house",
      "part_number": "head_shell24.stl",
      "cost_usd": 0,
      "status": "ready",
      "notes": "Includes bow sensor pod mounting flat"
    },
    {
      "id": "PWR-001",
      "category": "Power",
      "subcategory": "Battery",
      "description": "6S LiPo battery (4000 mAh)",
      "qty": 2,
      "unit": "ea",
      "print_or_procure": "procured",
      "specs": {
        "chemistry": "LiPo",
        "voltage": "22.2 V nominal",
        "capacity": "4000 mAh",
        "c_rating": "100 C",
        "mass": "~590 g each",
        "dimensions": "155 × 43 × 56 mm"
      },
      "supplier": "Turnigy",
      "part_number": "turnigy-4000-6s-100c",
      "cost_usd": 45.00,
      "qty_cost": 90.00,
      "status": "procured",
      "notes": "Dual-rail failover per AGENTS.md §1 Redundancy"
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
- **Capes:** 8× Wash/Cape-A-2, 8× Zoë/Cape-B-2, 2× Emma/Cape-X-1, 1× Kaylee/PDB
- **Standalone:** 1× Jayne (vision/ToF/laser board, PCM-071 SoM)
- **Sensors:** GPS, IMU, barometer, 2× Hall encoders (AK7455), 12× ToF (VL53L5CX), 2× laser
- **Security:** 8× TPM 2.0 (SLB9672), 4× CPLD write-blocker (ATF16V8BQL)
- **Connectors & cabling:** USB-C, XT90 PDB, RP-SMA antenna bulkheads, shielded Ethernet/CAN

### Power Distribution

- **Kaylee PDB:** 2× 40A fuses, 5V/5A BEC, main bus connectors
- **ESCs:** 4× 40A BLHeli32 (nacelle EDF control)
- **Wiring:** 14 AWG main leads (XT90 → Kaylee), 22 AWG signal/logic

### Propulsion

- **EDFs:** 4× XFly Galaxy X5 50 mm (6S, 3200 KV, 12-blade rotor, 11-fin stator)
- **Servos:**
  - 2× SPT5425LV + LibreServo v2 (nacelle tilt, was DS3218MG)
  - 1× SPT5425LV + LibreServo v2 (winch motor, continuous rotation + encoder feedback, was STS3215)
  - SG90 + OpenServoCore (door actuator, payload release)

### Cargo System

- **Gondola shell** (printed CF-PETG, with clamshell door halves)
- **Winch mechanism:**
  - SPT5425LV + LibreServo v2 servo (continuous rotation, was STS3215)
  - Twin pedestal spool (magnetic brake ratchet)
  - Dyneema line (2 mm, 3 m length, 100 lb break strength)
  - Auto-latch and payload release solenoid
- **Door actuator:** SG90 servo, spring-assist open

### Comms & Sensors

- **Radios:**
  - SiK RFD900x (915 MHz MAVLink)
  - XCVR-49MHZ-1/2 (SI5351-based, 49 MHz Part 15 §15.235)
  - LoRa SX1262 (optional, Phase 10+)
  - Wi-Fi 5 GHz (via host PC or PB2-I USB dongle)
  - ZigBee 2.4 GHz (via PHY expansion, not yet integrated)

- **Antennas:**
  - 49 MHz wire posts (forward + aft, Part 15 §15.235 compliance)
  - SMA bulkhead connectors (SiK + XCVR + LoRa)
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
| 2 | Nacelle assembly | EDFs, nozzles, iris mechanism | — | CAD complete |
| 3 | Tilt mechanism | Servo mounts, pivot rod, linkages | — | CAD complete |
| 4 | Hull foam & close | Foam pour, panel lids | — | Ready |
| 5 | Avionics (4 nodes, minimal) | Wash/Zoë on Shepherd + Inara, ESCs | — | PCBs in rev S1 |
| 6 | Full 8-node architecture | All 8 nodes + Emma + Kaylee + Jayne | — | PCBs in rev S1 |
| 7 | Cargo system | Gondola, winch, servo, solenoid | — | CAD complete |
| 8 | Finishing | Decals, documentation | — | Awaiting first flight |
| 9–10 | Flight tuning & extended range | Optional LoRa, gimbal tracking | — | Deferred |
| 11+ | Aft EDF + RCS | 55 mm EDF, valve manifold, nozzle | — | Deferred |

## Revision History

- **Rev S** (2026-07-04): Baseline for Phase 5; 24-inch hull, 8-node PACE, Kaylee/Jayne, Wash/Zoë/Emma/Kaylee/Jayne Rev S1 PCBs
- **Rev R1** (2026-06-11): 24-inch hull final, hull-frame coordinate std baked into STLs, Nacelle CG tuning (PIVOT_Z = 111.5 mm)
- **Rev R** (2026-04-XX): First 24-inch hull iteration, pre-PIVOT_Z tuning
- **Rev Q** (2026-02-XX): Last 18-inch baseline; 8-node architecture finalized
- **Rev P & earlier:** Historical prototypes (DaVinci Jr, 18-inch predecessor)

See `docs/WBS.md` §6.3 for full Rev S changelog and component-level deltas from Rev R1.

## Part Cross-References

Every part in the BOM has a cross-reference to:

- **Schematic net / PCB footprint** (avionics parts) — link to `avionics/kicad/<board>/<board>.kicad_sch`
- **SCAD/CAD model** (printed parts) — link to `.scad` generator or STL file path
- **Datasheet** (ICs, sensors, mechanical parts) — link to PDF via REFERENCES.md `[REF-*]` ID
- **Supplier page** (procured items) — direct URL to part listing (Digi-Key, Mouser, Amazon, etc.)

## Usage

### For Bill of Materials

1. Export `bom_revS.csv` to spreadsheet (LibreOffice Calc, Excel, Google Sheets)
2. Add columns for:
   - Order date, delivery date, received qty, unit cost verified
   - Bin location (for inventory tracking)
   - Subcategory total cost (sum by subsystem)
3. Cross-reference against `serenity-rev-r.jsx` for linked supplier pages

### For Assembly / Build Guide

1. Use `bom_revS.json` as the source of truth for mass budget, CG, and part naming
2. Build-guide phase checkpoints reference part ID (e.g., "Install SYS-001 (head shell) using
   structural epoxy per Phase 1 procedures")
3. Every assembly step links back to a specific part or assembly in the BOM

### For Design Changes

1. Update the affected part's specs in `bom_revS.json` (mass, dimensions, supplier link)
2. Re-run `tools/update_bom.py` to sync `bom_revS.csv` and re-calculate total mass/cost
3. Update revision marker (`date` field) and commit with message referencing the design change

## Tools

- **`tools/update_bom.py`** — Python script to sync JSON ↔ CSV and calculate totals
- **`serenity-rev-r.jsx`** — React component (Webpack build) to render interactive BOM viewer
- **`REFERENCES.md`** — Catalog of all supplier links, datasheets, and regulatory citations

## License

All BOM files are **CC BY 4.0**.

See root [`LICENSE`](../LICENSE) and [`docs/attribution_and_licensing.md`](../docs/attribution_and_licensing.md)
for full details.

---

*"Everything is shiny." — Kaylee Frye*
