---
title: "Commo as a standalone MCU bus node (vs. PB2-I cape) — requirements brainstorm"
date: 2026-09-29
status: draft — decision pending owner answers (see "Open Questions")
scope: avionics/kicad/Commo, avionics PACE/radio architecture
authors: S. Griffing (owner); analysis drafted by Claude (Claude Code)
---

# Commo as a Standalone MCU Bus Node — Requirements Brainstorm

## 1. Question

Should Commo stop being a PocketBeagle2-Industrial (PB2-I) cape and become a standalone,
MCU-driven PCB? It would keep its current radios (49 MHz AX.25 §15.235 transceiver + SiK
RFD900ux-SMT) and add isolated CAN-FD, RS-485, and MIL-STD-1553C. Any PB2-I stack could then
use its radios over the bus. The goals are to (a) save weight by fitting fewer radios and
(b) improve failover.

## 2. Current baseline (from the repo, 2026-09-29)

| Fact | Source |
| --- | --- |
| Commo is a PB2-I cape on P1/P2 socket rails, fitted only in River's Room (Bay C) and Simon's Medbay (Bay D) | `avionics/AGENTS.md`, root `AGENTS.md` §1 |
| Radios: 49 MHz AX.25 (Si5351A DDS, MCP4921 AFSK DAC, LM393 demod, 2N3866 PA) + SiK RFD900ux-SMT | `avionics/kicad/Commo/Commo.md` (2026-09-21 note) |
| The modem is **host-driven**: the DAC is on the PB2 SPI bus (`DDS_FSYNC`), PTT/RSSI_DCD are on PB2 GPIOs, and the SiK UART is on the PB2-P1 rails. The PB2 CPU runs the AFSK/AX.25/KISS software. | `Commo.md` status header |
| The TPM (SLB9672) binds to the host PB2 over SPI1. There is deliberately no local CAN-FD/RS-485. | `Commo.md` "Security Notes" |
| Open layout blocker: there is no contiguous free area for the 21 × 29 mm (0.83 × 1.14 in) SiK module without disturbing ETH-PHY/T-ETH. The cape outline is saturated, and F.Cu has no ≥ 6 × 6 mm free site. | `Commo.md` |
| PACE: River is Comms **E**, Simon is Comms **C**. Shepherd (Comms A) and Inara (Comms P) have **no** 49 MHz or SiK access. | root `AGENTS.md` §9 |
| The 1553 bus is "not extended to the resource-constrained nodes lacking an SBC" | `avionics/AGENTS.md` "Bus Topology" |
| Fleet 1553 PHY: Holt HI-1573 + Premier Magnetics PM-DB2791S (bus A only populated) | `Pilot.md`, `TACCO/reports/HDD.md` |
| Fleet standard standalone MCU: TI MSPM0G3507 (Observer, Bus-Gateway) | `Bus-Gateway/CAN-PERIPH-GW-1.md` |
| Commo mass: **0.044 lbm (20 g) each** (2× = 40 g) in `airframe/README.md`, but **0.115 lbm (52 g) each** in `docs/BATTERY_MOUNT.md`, which also counts **4×** Commo. **The two sources disagree and need reconciling.** | as cited |

## 3. Findings

### 3.1 Failover: this is the real win, but only if Commo becomes a bus peer

Today the 49 MHz and SiK links are **fate-shared with one PB2**. If River's SBC, cape stack, or
host software dies, River's radios die with it, even though the radio hardware is fine.
Shepherd and Inara, the stacks that hold Comms **P** and **A** in the PACE table, cannot reach
either long-range Commo link at all.

A standalone Commo on the isolated CAN-FD, RS-485, and optionally 1553 rings changes that:

- The radios survive the loss of any single SBC.
- Any of the 4 stacks can key either radio, so the Comms-P stack (Inara) could use 49 MHz/SiK
  directly instead of relaying through River or Simon.
- It matches the Observer and Bus-Gateway pattern the project already uses: a standalone PCB,
  an SE instead of a TPM, and authenticated bus traffic (NIST SP 800-207 micro-segment).

**Assessment: strong yes on failover grounds.**

### 3.2 Weight: going from two Commos to one does not pay

- A standalone board does **not** get lighter than the cape. It drops the PB2 2×18 sockets
  (≈ 0.007–0.009 lbm, 3–4 g, estimate). It adds an MCU, an isolated DC-DC and digital isolators
  for 2–3 bus domains, the 1553 protocol engine and its transformer (the transformer is the
  heaviest new item, ≈ 0.004–0.009 lbm, 2–4 g, estimate — verify against the PM-DB2791S
  datasheet), 3–4 more JST-GH connectors, its own power input stage, an SE, and a mounting
  provision. **Estimate: 0 to +0.022 lbm (0 to +10 g) per board versus the cape.** These are
  engineering estimates, not measured masses; they need a KiCad BOM mass roll-up before any
  decision is quoted.
- Consolidating to **one** Commo saves roughly one board, 0.044–0.115 lbm (20–52 g) depending on
  which source is right. Using the README figure of ≈ 0.95 lbm (432 g) of avionics at 15.2 %,
  the airframe is ≈ 6.3 lbm (2.84 kg), so the saving is **≈ 0.7–1.8 % of gross mass**.
- The price of that saving is a **single point of failure** for both 49 MHz and SiK. The
  design brief calls River "most resilient comms", and the 49 MHz link exists specifically for
  the 500 W/m² high-RF-field case. Losing it to one board fault defeats that purpose.

**Assessment: consolidate the *host dependency*, not the *radio count*.** Keep two standalone
Commos (Bays C and D) that every stack can reach over the bus. If weight really has to come
out, a better option is a **one-Commo + mLRS-backup** architecture, with that trade stated
explicitly in the PACE table. Do not present one Commo as a failover improvement: it is a
failover regression traded for about 1 % of mass.

### 3.3 Bus-by-bus feasibility

| Bus | Need on standalone Commo | Feasibility / part direction | Notes |
| --- | --- | --- | --- |
| CAN-FD (isolated) | Yes, primary control/data path | Straightforward: MCU MCAN + isolated transceiver (fleet ISO parts) | 5 Mbit/s data phase is far above the 1200-baud AFSK and SiK air-rate needs |
| RS-485 (isolated) | Yes, second independent lane | Straightforward: MCU UART + isolated RS-485 transceiver | Gives two dissimilar lanes without 1553 |
| MIL-STD-1553C | **Decision needed** | Much harder. HI-1573 is only a transceiver; an MCU cannot practically do 1 Mbit/s Manchester II framing with RT timing. It needs a protocol engine such as Holt's HI-613x BC/MT/RT family with SPI (**part number, 1553C conformance, and transceiver integration must be checked against the Holt datasheet before use**) plus the transformer. | This also **contradicts** the current rule that 1553 is not extended to non-SBC nodes. Adding it costs board area, ≈ 0.1–0.3 W, BOM cost, and a change to the architecture rule. Commo would be a 1553 **RT**, and the BC schedule on the SBCs has to include it. |
| Ethernet (current ETH-PHY) | Optional | MSPM0G3507 has no Ethernet MAC. Keeping Ethernet forces an MCU with a MAC and FD-CAN (for example an STM32H5-class part — verify). | Dropping ETH also frees the floorplan that currently blocks SiK placement |

### 3.4 What moves from the PB2 into the MCU

- **AFSK modem + AX.25/KISS.** 1200-baud Bell-202 DSP is well within an 80 MHz Cortex-M0+
  (MSPM0G3507) budget. Demodulation stays on the hardware LM393 path. The TX DAC and DDS
  control move onto the MCU's own SPI/I²C.
- **SiK.** The UART terminates on the MCU. MAVLink is bridged to CAN-FD/RS-485 frames as
  opaque, authenticated payloads.
- **Security.** Per `avionics/AGENTS.md`, a non-cape PCB carries an **SE**, not a TPM. Signing
  for radio TX/RX moves from the host-bound TPM to the local SE, and the node needs its own
  secure boot and key-provisioning story, the same as Observer. **Firmware and an assurance
  workload go with this change**: the node becomes a new zero-trust micro-segment that has to
  authenticate at startup and throughout the mission.
- **Arbitration.** This is a new requirement. Commo has to accept keying and TX requests from
  up to 4 stacks. That needs a PACE-aware ownership/lease protocol (which stack "owns" PTT)
  with watchdog takeover, or two stacks can collide on the air.

### 3.5 Side benefits

- It removes the SiK floorplan blocker, because the outline is no longer fixed by the PB2
  footprint.
- The board can mount near its antennas. That shortens RF coax (emi-hardening WBS run-length
  budget of ≤ 11.8 in, 300 mm) at the cost of a longer, shielded bus harness.
- It stays reusable on other UAV/UGV/USV platforms (root `AGENTS.md` §0) without requiring a
  PB2 host.

## 4a. Owner decisions (2026-09-29)

| # | Decision | Consequence carried into planning |
| --- | --- | --- |
| 1 | **One standalone Commo board** for the airframe | Accepted trade: 49 MHz and SiK become a single point of failure; mLRS (on every TACCO) is the fallback long-range link. The PACE table needs updating so that every stack reaches Commo over the bus. The install bay still has to be chosen (C or D, or a location closer to the antennas). |
| 2 | **MIL-STD-1553C included**, because Commo is an external RF link and has to be on every onboard bus lane | Amend the `avionics/AGENTS.md` "Bus Topology" rule to allow the 1553 exception for Commo. Commo is a 1553 **RT**, so the SBC bus-controller schedule has to include it. Needs a protocol engine + transformer, with the Holt part verified against its datasheet. |
| 3 | **No Ethernet**: ADIN1300 / T-ETH / J-ETH removed | The fleet-standard MSPM0G3507 is viable, provided its SPI, UART, and MCAN counts cover 1553 + RS-485 + SiK + DAC/DDS + SE. The pin budget is to be confirmed in the plan. |
| 3b | **Placement: co-located with its antennas** (49 MHz whip + SiK whip), not in an avionics bay | RF coax runs become minimal, and the bus harness (CAN-FD, RS-485, 1553 stubs, power) carries the length instead. The exact station and antenna sites are to be set in the plan against the hull model and the emi-hardening WBS antenna-separation checks. The 1553 stub length must stay within transformer-coupled stub limits. The board's mass moves the CG and needs a weight-and-balance update. |
| 4 | Mass source of truth: **derived from the PCB design itself** (bare-board mass from outline × stackup, plus per-part BOM masses from OEM datasheets), not from either hand-entered figure | `airframe/README.md` and `docs/BATTERY_MOUNT.md` are updated from the new board's roll-up once it is laid out | Reconcile `airframe/README.md` against `docs/BATTERY_MOUNT.md` before quoting the saving |

Resulting requirement set: a standalone, MCU-driven Commo with the 49 MHz AX.25 chain and SiK
RFD900ux-SMT unchanged, isolated CAN-FD, isolated RS-485, isolated MIL-STD-1553C RT, an SE, its
own power input, and no PB2 headers or Ethernet. One unit per airframe.

## 4. Recommendation (draft, superseded in part by §4a)

**Go standalone. Keep two units. Make 1553 an explicit owner decision, and default it to "no".**

1. Redefine Commo as a standalone bus node: MSPM0G3507 (fleet standard) if Ethernet is
   dropped, isolated CAN-FD + isolated RS-485, SE, and both existing radio chains unchanged.
2. Keep one unit each in Bays C and D, reachable by all 4 stacks. Update the PACE radio lines
   so that Shepherd and Inara gain 49 MHz/SiK access.
3. Leave 1553 **off** unless the owner wants Commo on the 1553 ring. That would reverse the
   "no 1553 on non-SBC nodes" rule and bring in a protocol engine + transformer per board.
4. Reconcile the Commo mass (20 g vs. 52 g, 2× vs. 4×) before quoting any weight delta.

## 5. Open Questions (owner decisions)

1. **Radio count:** keep 2 standalone Commos (failover gain), or consolidate to 1 (≈ 1 % mass
   saving, 49 MHz/SiK single point of failure)?
2. **1553C:** is it required on Commo? If yes, this reverses the current `avionics/AGENTS.md`
   rule that 1553 is not extended to non-SBC nodes.
3. **Ethernet:** keep the ADIN1300 port (forces a non-MSPM0 MCU) or drop it?
4. **Mounting:** co-locate the board with its antennas, or stay in the avionics bay?
5. **Mass source of truth:** which Commo mass and count is right, `airframe/README.md`
   (2 × 20 g) or `docs/BATTERY_MOUNT.md` (4 × 52 g)?

## 6. Next steps once answered

`/ce-plan`, then WBS/TODO entries under `avionics/WBS.md` §1.2a, then a schematic-first
redesign in `avionics/kicad/Commo/`. Preserve the current cape as an archived revision per
`avionics/AGENTS.md` "Work Tracking" item 5.
