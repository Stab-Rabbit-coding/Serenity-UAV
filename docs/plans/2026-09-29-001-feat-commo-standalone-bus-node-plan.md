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

### Phase 1 findings (2026-09-28, from on-file datasheets)

**MCU: TI MSPM0G351x-Q1, VQFN-48 RGZ.**
- Source: `avionics/datasheets/mspm0g3518-q1.pdf`, TI SLASFA6B, Table 5-1.
- The RGZ-48 package gives 1 CAN-FD, 6 UART, 3 I²C, 2 SPI, and 44 GPIO. The G351x also has an
  AES-256 accelerator, secure key storage, and a TRNG (§1).
- Estimated signal count: about 30 lines. That covers SWD, CAN-FD, RS-485 (TX/RX/DE), the SiK
  UART, SPI to the 1553 engine with IRQ and reset, SPI to the MCP4921, I²C to the Si5351A and
  SE, PTT, RSSI_DCD, the demod input, T/R switch control, and PA enable.
- **The RHB-32 package is ruled out.** It has 28 GPIO, which is too few for about 30 lines.
- SPI is exactly consumed: RGZ-48 has 2 SPI ports, and Commo needs 2 (1553 engine and DAC).
- **Recommend M0G3519QRGZRQ1** (512 KB flash) over the G3518 (256 KB). It is the same
  footprint and the same part as Observer, and dual-bank OTA halves the usable flash.
- The G3507 is dropped. The fleet retarget (§1.9.3) moved to G351x for key storage.

**1553: HI-1573 is a transceiver only.**
- Source: `avionics/datasheets/hi-1573.pdf`, Holt DS1573 Rev U.
- It takes Manchester II bi-phase data in and out (p. 2). A separate protocol engine is
  mandatory.
- The MCU's Manchester-capable UARTs cannot substitute. 1553 sync is an invalid-Manchester
  waveform, and RT response timing must be guaranteed in hardware.
- **Conformance gap:** HI-1573 claims only "MIL-STD-1553A and B" compliance (p. 1). It does
  not claim 1553C. 1553C conformance must be shown on the protocol engine's datasheet or
  justified in `REFERENCES.md`. This blocks final part selection.
- Coupling (p. 2): direct coupling uses a 1:2.5 transformer with 2 × 55 Ω resistors.
  Transformer coupling uses 1:1.79 plus a 1:1.4 coupler and 0.75·Zo resistors.
- The fleet's 55 Ω parts (`R-1553P/N`) match direct coupling, which is short-stub only. The
  antenna-site stub length decides which coupling Commo uses.
- The Holt protocol-engine datasheet is **not on file** and must be downloaded next.

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

### Owner decisions, 2026-09-28 (after Phase 1 findings)

- **MCU:** M0G3519QRGZRQ1 approved.
- **1553:** dedicated protocol engine (option 2). The candidate is Holt HI-6138: BC/RT/MT,
  SPI host, on-chip transceiver. Holt claims MIL-STD-1553B/C compliance on its product page.
  Datasheet verification is pending a manual download.
- **Fleet:** Pilot and TACCO also move to MIL-STD-1553C using the same part. This is tracked
  as its own work item in `avionics/WBS.md` §1.2a.3, outside this plan's scope.

### HI-6138 datasheet check (DS6138 Rev S, 2026-09-28)

- **Magnetics carry over.** Figure 28 (p. 255) specifies a 1:2.5 isolation transformer for
  both coupling modes, which matches the fleet's PM-DB2791S. Transformer coupling adds a
  1:1.4 stub coupler and 52.5 Ω resistors.
- **HI-1573 dropped.** The transceiver is on-chip.
- **Host interface:** SPI up to 40 MHz, modes 0 and 3. IRQ is active low; MR is an
  active-low reset.
- **Open:** the datasheet claims MIL-STD-1553B only. The 1553C claim exists only on Holt's
  product page, and written confirmation from Holt is required.
