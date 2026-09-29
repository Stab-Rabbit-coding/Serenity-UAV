# Commo Standalone Bus Node (Rev T) — Project Plan

Created: 2026-09-29
Origin: `docs/brainstorms/2026-09-29-commo-standalone-node-requirements.md` (§4a owner decisions)

## Goal

Replace the PB2-I Commo cape (River/Simon, 2 units) with **one standalone, MCU-driven Commo**
co-located with its antennas. It keeps the 49 MHz AX.25 chain and SiK RFD900ux-SMT unchanged,
adds isolated CAN-FD, RS-485, and MIL-STD-1553C RT, and is reachable by all four stacks. Mass
comes from the PCB roll-up.

## Settled inputs (owner, 2026-09-29) — do not re-open

| Decision | Value |
| --- | --- |
| Units per airframe | 1 (accepted single point of failure; mLRS is the fallback) |
| Buses | Isolated CAN-FD, isolated RS-485, MIL-STD-1553C RT |
| Ethernet | Dropped (ADIN1300 / T-ETH / J-ETH removed) |
| Placement | Co-located with the 49 MHz and SiK antennas |
| Mass source | PCB-derived roll-up (bare board + BOM part masses from OEM datasheets) |

## Phase 0 — Architecture paperwork (before any KiCad edit)

1. **ADR / rule change.**
   - Amend `avionics/AGENTS.md`: "Bus Topology" gets a named 1553 exception for Commo; "Cape
     Naming" re-classes Commo as a standalone PCB with an SE (like Observer).
   - Root `AGENTS.md` §1 and §9: one Commo; all stacks reach 49 MHz/SiK over the bus; update the
     PACE radio lines.
2. **WBS/TODO.**
   - Add a new `avionics/WBS.md` §1.2a sub-item "Commo Rev T standalone" and matching `TODO.md`
     §1.2b entries, per root `AGENTS.md` WBS-first rule.
3. **Archive.**
   - Move the current cape project to `archives/avionics-archives/kicad-archives/Commo-cape-RevS-superseded-2026-09-29/`
     and update `ARCHIVE_INDEX.md`.

## Phase 1 — Part selection (datasheet-verified; check `avionics/datasheets/` first)

| Function | Candidate | Verify |
| --- | --- | --- |
| MCU | TI MSPM0G3507 (fleet standard; datasheet on file) | Peripheral budget: ≥1 MCAN, ≥3 UART (SiK, RS-485, debug), ≥2 SPI (1553 engine, MCP4921 DAC), I²C (Si5351A, SE), plus GPIO for PTT/RSSI_DCD/1553 IRQ. If this is short, escalate to the owner. |
| 1553C RT | Holt protocol engine with SPI host interface (HI-613x family) + existing HI-1573 transceiver if not integrated + PM-DB2791S transformer | Exact P/N, 1553C conformance, and transceiver integration, against the Holt OEM datasheet. Download it to `avionics/datasheets/`. |
| Isolated RS-485 | ADM2795E (fleet part; datasheet on file) | Reuse the Bus-Gateway circuit |
| Isolated CAN-FD | Same isolated transceiver as Pilot/TACCO/Bus-Gateway | Reuse the fleet circuit; confirm the part in the Bus-Gateway schematic |
| Security element | Infineon OPTIGA Trust M (appears in fleet docs) | Confirm this is the fleet SE choice; I²C address conflict with Si5351A |
| Power | Local buck from the bus harness supply + isolated DC-DC per bus domain | Input rail and budget. The 49 MHz PA and SiK TX peaks set the sizing. |
| Radios | Existing 49 MHz chain and RFD900ux-SMT, unchanged | Keep the fixed shared `RFDesign_RFD900ux_SMT` footprint |

## Phase 2 — Schematic (schematic-first, script-generated per root `AGENTS.md` §5)

1. Create the new `avionics/kicad/Commo/` project (Rev T). Port the RF sheets (DDS, PA, 6-element
   LPF, T/R switch, LNA, AFSK DAC/demod, SiK, antenna protection) from the archived cape as-is.
2. Remove the PB2 P1/P2 rails, TPM (SLB9672), ETH-PHY/T-ETH/J-ETH, and J1 remnants.
3. Add the MCU, SWD header, SE, CAN-FD, RS-485, 1553 RT with transformer, bus connectors
   (shielded JST-GH, PGND drain), and the power input stage.
4. Run ERC and get it to 0 or documented. Update `Commo.md`.

## Phase 3 — Layout

1. Outline sized to the antenna-site envelope. The script populates footprints; **manual
   placement is the owner's** per `avionics/AGENTS.md`.
2. Keep the existing RF rules: split PGND/GND moat, shield can over the RF section, no power
   plane under RF.
3. Keep isolation barriers per bus domain. The 1553 stub runs to the ring must stay within the
   MIL-STD-1553 transformer-coupled stub limit. Measure it once the site is fixed.
4. DRC to 0 or documented, then Gerbers.

## Phase 4 — Integration and mass

1. **Mass roll-up** from the PCB:
   - bare board = area × stackup density;
   - add BOM part masses from OEM datasheets;
   - add connectors and shield can.
   Update `airframe/README.md`, `docs/BATTERY_MOUNT.md`, and W&B/CG in lbm (g).
2. **Placement.**
   - Fix the station against the hull model and the `avionics/emi-hardening/WBS.md` antenna
     separation checks.
   - Update the bus-harness routing: CAN-FD, RS-485, the 1553 stub, and power.
3. **Firmware work items** (logged to `avionics/firmware/WBS.md`; not executed here):
   - AFSK/AX.25/KISS on the MCU and a SiK↔bus bridge;
   - PACE-aware PTT ownership lease with watchdog takeover;
   - 1553 RT subaddress map, and an update to the SBC bus-controller schedule;
   - SE-based signing, secure boot, and key provisioning.

## Risks

- **Single point of failure** on 49 MHz/SiK. This is accepted. Document mLRS fallback behavior
  in the PACE table.
- **1553 protocol engine.** Part availability or 1553C conformance may not pan out. Fallback: go
  to the owner before substituting anything.
- **MCU peripheral shortfall.** If there are not enough UARTs or SPI ports, the part choice goes
  back to the owner.
- **EMI.** The board sits outside the avionics bay near the antennas. The 500 W/m² field target
  applies, and the bus-port filtering has to match Observer/Bus-Gateway.

## Done when

- ERC and DRC are clean or documented.
- Gerbers are generated.
- `Commo.md` is current.
- The rules in both AGENTS.md files and the PACE table are updated.
- The mass roll-up is propagated.
- The old cape is archived.
- The firmware items are logged.
