# Serenity Avionics — KiCad Cape Status & Build Notes

This directory holds the KiCad projects for the four cape/board types:

| Project | Name | Role |
| --- | --- | --- |
| `Pilot.kicad_*` | **Pilot** | Flight-control & sensor cape (FC) |
| `XO.kicad_*` | **XO** | Comms / logging / payload cape (CN) |
| `FlightEngineer.kicad_*` | **Flight Engineer** | Power-distribution board (PDB) |
| `Commo.kicad_*` | **Commo** | 49 MHz (Part 15 §15.235) transceiver |
| `Observer.kicad_*` | **Observer** | Nose/Cargo vision, ToF, & laser board (standalone) |

Per-board net/pin documentation lives in the matching `*.md` files
(`Pilot.md`, `XO.md`, `FlightEngineer.md`, `XCVR-49MHZ-2.md`). KiCad files keep
KiCad board coordinates (documented exception to the hull-frame standard,
see root `AGENTS.md`).

---

## DRC / routing work — what was done and what was not (2026-06-12)

A pass was made to wire in a second Ethernet channel and to clear the
Design-Rule-Check (DRC) and ratsnest issues introduced by a manual
component rearrangement. This section records exactly what landed and
what is still open, so the thread can be picked up cleanly.

### ✅ Done

- **Second Ethernet (ETH2) wired on Pilot.** The newly placed `ETH2`
  (JST-GH-4P), `ETH2-PHY` (ADIN1300BCPZ), and `T-ETH2` (749010012A
  magnetics) footprints were present but unconnected. Their nets now
  mirror the ETH1 topology exactly:

  ```text
  ETH2 ──ETH2_LINE_{TX,RX}{P,N}──► T-ETH2 ──ETH2_{TX,RX}{P,N}──► ETH2-PHY
  ```

  The host side reuses the nets already broken out on the **PB2-P2**
  header: the `RMII1_*` bus, shared `MDIO`/`MDC`, `PHY2_INTRN`/
  `PHY2_RSTN`, and the `VCC2_ETH` / `GND` / `GND2_ETH` power and
  isolation domains. 44 pads assigned (ETH2-PHY 32, T-ETH2 8, ETH2 4);
  diff-pair chains verified end-to-end. *(Delivered in PR #59.)*

- **Split the two Pilot PHYs onto independent MDIO buses (2026-06-12).** Instead
  of an address strap on a shared bus, PHY1 now uses `MDIO0`/`MDC0` (the CPSW
  MDIO controller, PB2-P2 pins 17/18) and PHY2 uses `MDIO1`/`MDC1` (PB2-P2 pins
  1/2, the two spare servo channels SERVO6/7). Each PB2-I NIC manages its own
  PHY — no shared-address conflict. Both the PCB nets and the schematic global
  labels were updated. *Firmware note:* PHY2's bus is a second (bit-banged
  `mdio-gpio`) MDIO; confirm the two repurposed balls are GPIO-capable in the
  PB2-I pinmux.

- **Wired the floating field connectors to their signals (2026-06-12).** Every
  JST field connector was placed but had no nets. Using each footprint's
  Description pinout: SERVO-PWM pads 1–6 → `SERVO0–5` (servo PWM); ESC-TLM →
  `UART_ESC_TX`/`RX`; GPIO-A…F → `GND`/`+3V3` (+ labeled `GPIO_EXP_*` signal);
  CAN-FD → `CAN_H`/`CAN_L`; RS-485 → `RS485_A`/`B`; PWR-IN → `+5V`/`GND`. The
  new connector shorts that DRC now reports are all against `TMESH_*` (the
  pre-existing tamper-mesh overlap, resolved by the mesh rework below) — not the
  connector wiring itself.

- **Confirmed the design is PCB-driven.** Each cape's schematic
  (`*.kicad_sch`) defines only the PocketBeagle-2 header pin-mux (the
  PB2-P1/P2 connectors with the RMII0/RMII1/MDIO net labels); every other
  component lives as a PCB footprint with nets assigned directly on the
  board. "Update PCB from Schematic" therefore does **not** repopulate
  the component nets — net edits are made on the `.kicad_pcb`.

- **Verified the boards load** in `pcbnew` (Pilot 43, XO 42, Commo 69,
  Flight Engineer 67 footprints) and characterised the violation landscape (below).

### ❌ Not done — open follow-up

1. **Tamper mesh (`TMESH_P`/`TMESH_N`).** Drawn today as a raw
   cross-hatch grid on F.Cu/B.Cu that **shorts across SMD pads and across
   the isolated `GND2_*` domains** — this is the single largest source of
   DRC errors (≈335 of Pilot's 465; similar on XO). The agreed design is
   a **per-domain anti-tamper mesh**: a separate monitored mesh net per
   isolation region (secure/`GND` area plus one per `GND2_CAN` / `GND2_ETH`
   / `GND2_RS485` field side), with the 0.5 mm `ISOLATION` creepage moat
   kept clear between them. Pilot and XO tie their mesh to the local TPM;
   **Flight Engineer and Commo have no local TPM**, so their tamper signal must be
   carried over the inter-board link (Commo → XO, Flight Engineer → Pilot).

2. **Routing / ratsnest.** The manual rearrangement left signal nets
   unrouted (~60 multi-pin signal nets per cape; the 7 power/ground nets
   are intended as planes). This was **not** completed — see the toolchain
   findings below for why headless autorouting did not produce a
   trustworthy result. The impedance-controlled Ethernet pairs should be
   routed interactively (length-matched / controlled-impedance) regardless.

3. **Remaining DRC.** After the mesh and routing are fixed, the residual
   cosmetic/footprint items still need clearing (counts measured
   2026-06-12, error+warning):

   | Board | violations | unconnected | dominant types |
   | --- | --- | --- | --- |
   | Pilot | 465 | 121 | mesh shorts, solder-mask bridges, clearance |
   | XO | 554 | 146 | mesh shorts, solder-mask bridges, clearance |
   | Commo | 421 | 160 | silk-over-copper, text-height, mask bridges |
   | Flight Engineer | 221 | 181 | courtyard overlap, lib-footprint mismatch, silk |

4. **MDIO addressing.** Both Pilot PHYs (ETH1-PHY, ETH2-PHY) share the
   `MDIO`/`MDC` management bus but there are **no address-strap resistors
   on the board**, so both default to the same MDIO address. A strap
   (or a decision to manage each PHY only over its own RMII channel) is
   required before the second PHY is manageable. Not invented here because
   no strap-resistor footprints are placed.

---

## Toolchain findings (headless KiCad 9 + freerouting)

These are recorded so the next person does not re-derive them:

- **KiCad 9.0.2 `pcbnew.ExportSpecctraDSN()` is non-functional in
  standalone Python** — it returns `False` with no GUI/kiway context
  (`pcbnew.GetBoard()` is `None`). Loading a project, building
  connectivity, initialising a `wx.App`, and running under Xvfb all make
  no difference; it is a binding limitation, not a display issue.

- A custom headless **Specctra DSN exporter + SES importer** (driven
  entirely through the working board API) was written to bridge this. The
  round-trip is mechanically correct (valid DSN out, freerouting routes
  it, SES tracks/vias re-imported at the right coordinates).

- **freerouting 2.1.0 headless is unreliable for a complete route on this
  toolchain**: it must be run **without** a display (with Xvfb it opens
  the GUI and hangs); it never self-exits (must be killed after the SES is
  written); its multi-threaded optimiser is broken (use `-mt 1`); and the
  SES it emits captured only a handful of nets rather than the full
  ~60-net set. It was therefore **not** used to route the boards.

- **Recommended workflow:** finish routing in the **KiCad GUI** (where
  Specctra DSN export and the interactive/auto routers are reliable), with
  the Ethernet pairs routed by hand. The deterministic, non-routing work
  (per-domain tamper-mesh zones, cosmetic/footprint DRC, the Commo/Flight Engineer
  link tamper signaling) can still be scripted headless via the board API.

---

*Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP · License: CC BY-SA 4.0*
