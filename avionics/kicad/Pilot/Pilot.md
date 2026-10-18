# Pilot — Flight Control & Sensor Cape

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**Callsign:** Pilot
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Revision:** T (schematic-first rebuild, superseding Rev Q)
**Date:** 2026-10-06
**Status:** Schematic and PCB unified from one generator; ERC 0, DRC 0, fully placed on 6 layers on the corrected 4.80 mm SMT rails (2026-10-06). **Routing not yet complete** (see "Routing status" below).

**Update 2026-10-17 (PB2-I header re-map, Ethernet ring architecture, sourcing rules; S.
Griffing decisions, implemented by Claude Opus 5.5) — schematic ahead of the PCB.**

- **AM625 SoC capabilities re-checked against the data sheet** (SPRSP58C Table 5-1, TRM
  SPRUIV7C §1.4.12; REF-SENSOR-049/050): see
  [`../PB2I_AM625_HEADER_CAPABILITIES.md`](../PB2I_AM625_HEADER_CAPABILITIES.md). The SoC has
  two external Ethernet ports, but only port 2 (RMII2 or gigabit RGMII2) reaches the PB2-I
  header, so the two-NIC ring below stands. Three CAN-FD controllers reach the header (MCAN0
  in use; MCU_MCAN0 and MCU_MCAN1 share pins with the TPM and SPI0 chip-select nets) — open
  owner decision in `avionics/WBS.md`.
- **Header map rebuilt from official BeagleBoard sources** (REF-SENSOR-047, SRM §4.2):
    - The previous map put GND on P1-1, which is the PB2-I's VIN.
    - It put PHY resets on P2-13..16 (VSYS / VBAT / GND / BAT_TS).
    - It used RMII0/RMII1, which the headers do not carry.
    - The PB2-I and PB2 share one design repository and header map.
    - The rail footprints had pin 1 on the wrong row once flipped to B.Cu; the library is
      fixed, and TACCO is affected too (WBS).
- **Ethernet ring** (named by TI interface, owner 2026-10-17 — the ring's two legs are not
  "port 1/port 2", because TI numbers the AM625 CPSW3G ports and only its port 2 is used):
    - **CPSW3G port 2 / RMII2 leg:** DP83825I on RMII2 + MDIO0 (schematic `ETH1-PHY`). RMII2 is
      the only CPSW interface in use; the 12 RGMII2 balls also reach the header but are unused.
      CPSW3G port 1 (RGMII1/RMII1) does not reach the PB2-I header.
    - **USB1 leg:** a USB 10/100 controller on USB1 (P1-5 VBUS, P1-9 D-, P1-11 D+; schematic
      `ETH2-USB`). It is not a CPSW port. Linux bridges the two legs, so forwarding stops if
      this node's CPU is down (owner accepted).
    - The schematic reference designators `ETH1-*`/`ETH2-*`, `T-ETH`/`T-ETH2` and the nets
      `PHY1_*`, `ETH_*`, `ETH2_*` still carry the old 1/2 numbering; renaming them is an
      `avionics/WBS.md` item tied to the PCB re-sync.
- **Rejected candidates** (do not re-propose):
    - Microchip KSZ8863RLLI 3-port switch: no 10.5 mm courtyard site; the largest free square
      is ~6 mm.
    - Microchip LAN9303: also too large (8 x 8 QFN), and its RMII clock direction depends on
      register setup.
    - WCH CH397A: manufacturer domiciled in the PRC (AGENTS.md §5 sourcing rule).
    - Realtek RTL8152B-VB-CG: datasheet marked "CONFIDENTIAL: Development Partners Only"
      (fails the NDA-free rule).
    - Microchip LAN9500Ai: 8 x 8 QFN-56 does not fit.
    - ASIX AX88772E is selected (public datasheet, 4 x 4 QFN-32, 0-70 °C); it waits for ASIX's
      reference schematic.
- **Expansion:** the GNSS's place goes to one 6-pin JST-GH on the PB2-I SPI2 pins (SPI /
  UART1 / UART6 / PWM / GPIO) with fused 5 V and ESD. There is room for only one edge
  connector.

**Update 2026-10-17 (ISOW §13.1 re-floorplan applied to the PCB, keeping valid manual
routing; S. Griffing chose keep-copper; implemented by Claude Opus 5.5).** One script,
`scripts/refloorplan_keep_copper.sh`, rebuilds the board from the owner's routed board:

1. `refloorplan_pilot.py --keep-copper` syncs the PCB to the netlist (GNSS parts off, four
   §13.1 beads on), applies the hand poses and re-places displaced parts:
    - Both isolators are at rot 180, at (135.1, 107.1) and (150.5, 107.1) mm.
    - The §13.1 caps are within 1 mm of pins 11/12.
    - U-3V3 sits on B at (138.0, 100.6) with CIN on its south side and COUT on its east and
      north sides.
    - C-1553C sits at the HI-6138's VCCP pins.
    - 21 more parts were moved. Supply caps follow their parent, and no pad sits within
      2.75 mm of a mounting hole.
2. `iso_zones_pilot.py` redraws the isolation copper and adds the rules:
    - ISO_BAND, the GND2 islands, and the GND / +3V3 planes notched with the 0.5 mm moat.
    - The 4 mm `BUBBLE_CAN` / `BUBBLE_485` areas on every layer, with no pour.
    - The `bubble_*` DRC rules, and a courtyard exemption limited to the §13.1 part pairs.
3. `cleanup_pilot_copper.py` removes the 184 items on deleted GNSS nets.
4. `repair_pilot_routing.py` rips out copper that is now illegal or dangling.

Then `grid_route_pilot.py` (now aware of the bubbles and plane outlines), the rip-up rounds and
`fence_pgnd_pilot.py` ran. The PGND fence is partial: 20 vias in 8 runs tied to H1–H4, about
40 of the 180 mm perimeter.

- **Gates:**
    - DRC: 0 errors, 43 silkscreen warnings.
    - Schematic parity: 0.
    - 107 unconnected: 66 signal, 41 plane.
- **Before this pass,** the owner's board had 73 signal connections open; 66 are open now.
  The remaining core was already open before the re-floorplan:
    - RMII0/1, MDC/MDIO and PHY reset/interrupt lines;
    - SPI fan-in;
    - the RS485 logic lines.
- **Why it doesn't route:** the escapes around ETH1-PHY on B are fully used, and the P2-rail
  pads under the band can only escape on B.
- **Open owner decisions** (avionics/WBS.md): logic parts on B under the isolated domains
  (X-50M, BARO, HI-6138 west pads) have no logic plane or via, so they couple to GND2*. The
  PHY corridor needs interactive routing or a regional strip-and-reroute.
- **Backup:** the pre-change board is
  `kicads/Pilot-backups/Pilot.pre-refloorplan-2026-10-17.kicad_pcb`. That folder is gitignored.

**Update 2026-10-17 (3V3 supply → TPSM828224SILR module; S. Griffing decision, implemented by
Claude Opus 5.5).** The TPS62933 buck, its WE-MAPI 3015 inductor and six support parts (about
54 mm²) are replaced by TI's **TPSM828224SILR**. It is a fixed-3.3 V, 2 A MicroSiP module with
the inductor inside, 2.0 × 2.5 × 1.1 mm [REF-PWR-008]. The goal is to fit the 3V3 supply in
the B.Cu pocket between the §13.1 bubbles.

- **Load:** worst case about 875 mA (HI-6138 transmit 695 mA, 2 × DP83825I about 115 mA, TPM
    35 mA), so a 2 A part has about 2.3× margin. Input 2.4–5.5 V (abs. max 6 V); +5V is already
    held at 4.5–5.5 V by the ISOW VDD limit.
- **Schematic (ERC 0, 111 parts):**
    - FB (pin 8) ties to VOUT, as SLVSEP0F §9.2.1.2.1 requires for the fixed-output devices.
    - EN ties to VIN, and PG is left open.
    - Removed: `R-EN3`, `C-BST`, `C-SS`, `L-3V3`, `R-FB3H`, `R-FB3L`.
    - `C-3V3-IN` and `C-3V3-O1/O2` are all Taiyo Yuden MSASJ168BC6226MTNA01, 22 µF 6.3 V X6S
        0603 (TI's Table 9-1 output cap under its new part number) [REF-PWR-011].
    - DC bias checked against SLVSEP0F §9.2.2, worst case with −20 % tolerance and the
        temperature limit:
        - Input: 4.2 µF at 5.5 V, against a 3 µF minimum.
        - Output: 7.2 µF per cap at 3.333 V, against a 5 µF minimum.
    - The first input pick, Murata GRM188Z71A106MA73 10 µF, kept only 2.65 µF at 5.5 V and was
        rejected [REF-PWR-012].
- **Land:** `Serenity-Custom:TI_SIL0010D_uSiP-10_2.0x2.5mm_P0.5mm` (`gen_pilot_footprints.py`):
    - Taken from SLVSEP0F p. 48. The pads are solder-mask-defined, as §11.1 asks for pads tied to
        planes.
    - Cross-checked against the Ultra Librarian export.
    - The STEP body is in `../Serenity-Custom.3dshapes/`.
- **PCB:** swapped in place by `scripts/inject_tpsm828224.py`, which keeps the manual routing.
    It deleted the copper on the five dead nets and the old SOT-583 escapes under the new pads.
    - DRC with parity: 320 violations / 96 unconnected / 33 footprint errors, against 306 / 89 /
        33 before the swap.
    - Every new violation is in this area:
        - `U-3V3` courtyard overlaps `C-BARO1`;
        - 12 silk hits;
        - dangling +5V / +3V3 / GND copper waiting to be re-routed.
    - No shorts.
- **Open:**
    - Re-place the module and its caps into the pocket.
    - Thermal margin is thin only at the extreme: continuous 1553 transmit at 85 °C ambient
        reaches about 119 °C against 125 °C. That uses an estimated 85 % efficiency and TI's EVM
        θJA.

**Update 2026-10-12 (ISOW §13.1 made binding, GNSS moved off the cape; S. Griffing decisions,
analysis and implementation by Claude Opus 5.5).** The schematic is ahead of the PCB until the
re-floorplan below lands (branch `pilot-refloorplan`).

- **§13.1 is binding.** TI ISOW1044 SLLSFF7A §13.1 p. 36 [REF-SENSOR-009] and ISOW1412
  SLLSF86C §13.1 p. 41 [REF-SENSOR-010] require:
  - a 10 nF 0402 cap within 1 mm of VDD and of VISOOUT;
  - a ≥ 10 µF bulk cap after it, at 2–4 mm;
  - symmetric supply/ground traces up to those caps;
  - BLM15EX331SN1 beads from VISOOUT to VISOIN and from GND2 (pin 11) to GISOIN
    [REF-SENSOR-043];
  - "no metal traces or ground pour within 4 mm of" VISOOUT (pin 12) and GND2 (pin 11).

  This board reads the last item as covering every layer, measured from pad edge to metal
  edge.
- **Schematic (done, ERC 0).**
  - Four beads `FB-CAN-V/G` and `FB-485-V/G` added.
  - The converter side now has its own nets: `VCC2_*_DCDC` and `GND2_*_DCDC`.
  - `C-CAN4` and `C-485-4` move from 0201 to 0402.
  - ISOW1412 MODE (pin 13) is tied to GND2 per §13.1.
  - The MAX-M10S, its bias-T (`R-ANT`, `C-ANT`, `L-ANT`), `J-ANT` and `C-GPS1/2` are removed.
  - P1-31/32 (GPS UART) and P2-9/10 (GPS RESET_N / TIMEPULSE) are now NC.
  - Result: 117 parts.
- **Why GNSS left.** The 4 mm bubbles can only sit in the strip between the B.Cu PB2 rail pads
  (inner rows end at y 96.6 mm and 113.4 mm). Across that strip, PWR-IN's THT pads and T-ETH2
  leave about 0 mm to spare beside the two isolators. The bubbles displace the 3V3 buck,
  IMU/BARO, the GPS and the 1553 transceiver, and on 55 × 35 mm there was no room for all of
  them. The two dorsal GPS cups get **isolated CAN-FD GPS pucks** instead (owner choice;
  `avionics/WBS.md`). Each cup has room for a Ø28 mm × 8 mm board under the cup floor, which
  was measured against the T5 cargo shell.
- **PGND perimeter fence (owner request, 2026-10-12).** A PGND ring with stitching vias along
  the edge, gapped at the PB2 rail pads, the bubbles and the isolated band. To be added after
  placement and before routing.
- **PCB (in progress).** Both isolators go to rot 180, which puts the isolated column on the
  west with pins 11/12 at the top. CAN-TR sits at x 135.1 mm and RS485 at x 150.5 mm, both at
  y 107.1 mm. The displaced logic parts are being re-placed, and the band, islands and planes
  will be redrawn.

**Update 2026-10-11 (ISO_BAND GPS notch, S. Griffing decision after creepage review;
implemented by Claude Opus 5.5 with `scripts/notch_iso_band.py`):** the band's corner over
the GPS (MAX-M10S, B.Cu) is cut back. Its edge moves from y 105.5 to y 111.0 mm over
x 128.3–137.6 mm, so GPS pins 1–9 are no longer inside the band.
- **Outlines changed:** ISO_BAND, the In2/In3/In4 isolation keep-outs, the GND2_CAN island,
  and the GND and +3V3 plane cut-outs. No part moved.
- **Under the module:** In1 is now the logic GND plane and In4 the +3V3 plane. This follows
  u-blox UBX-20053088 R05 §4: "ground the area below the module, on the top and second layer".
- **Spacing:** the tightest new gap is 0.725 mm, from the notch edge to the CAN-TR isolated
  pins on F.Cu. The project rule is 0.5 mm, and the existing B.Cu gap from the GPS pins to
  CMC-CAN is also 0.725 mm. The isolation class is unchanged (functional, see "Isolation"
  below).
- **Cost:** the GND2_CAN island shrinks by 23 %, from 223.6 to 172.4 mm².
- **Gates:** DRC 0 errors, parity 0, 195 unconnected. GND/+3V3 pads inside the band drop
  from 9 to 5.
- **Not done:** the GPS caps found no closer legal site, because CAN-TR's body sits above
  the module and the band and CMC-CAN sit below its pin row. `gen_pilot_pcb.py` still carries
  the rectangular band, like the rest of the post-2026-10-09 placement.

**Update 2026-10-10 (TPM header pins, S. Griffing decision; implemented by Claude
Opus 5.5):** `TPM_RSTN` moved from PB2 P2-11 to **P1-28** (GPIO0_43, ball K22) and
`TPM_IRQN` from P2-12 to **P1-29** (GPIO0_62, ball Y20), per the PocketBeagle 2 SRM
§4.2 mux tables (`../../datasheets/pocketbeagle2_srm.pdf`).
- **Superseded 2026-10-17:** the PB2-I header re-map (top of this file) puts `TPM_IRQN` on
  P1-20 (ball Y24) and `DSHOT2` on P1-29; `gen_pilot_sch.py` `PB2_P1` is authoritative.
- **Why:** the TPM sits over the P1 rail, 6–7 mm from the new pins, whereas P2-11/12 were
  26–31 mm away and inside `ISO_BAND`, where no via is legal.
- **Rejected pins:** P1-27 is shared with AIN4, and P1-30 is UART0_TXD (the console).
- **Gates:** ERC 0, DRC 0 errors, parity 0. The PCB pad nets were edited in place, so the
  2026-10-09 hand placement is untouched.
- **Commo:** wires its own TPM to P2-11/12 and leaves P1-28/29 unconnected, so the two
  capes no longer share TPM reset/IRQ lines if they are ever stacked on one host.
- **Follow-up:** the host device-tree pin mux must move with the pins.

**Update 2026-10-06 (PB2 rail correction, avionics/WBS.md R2, S. Griffing decision;
implemented by Claude Opus 5.5):** the PB2 rails were 2.54 mm from the long edges
(29.92 mm apart). That spacing had no source, and the cape could not have mated.
- **Rails:** now at **4.80 mm** from each edge, 25.4 mm apart (PB2 SRM Fig. 3.45). They are
  Samtec **TSM-118-04-L-DV-LC** male SMT strips on the bottom face, the same as TACCO, because
  the PB2-I carries female receptacles. The -LC clip NPTHs are at ±20.32 mm on each rail.
- **Bottom-face height limit:** the stack gap is ~5.54 mm, which allows ≤ 5.04 mm parts on
  B.Cu, less over the PB2-I microSD (pin-1/2 end) and JST-SH (pin-35/36 end).
  - Both Ethernet transformers (8.9 mm) move to the top-right.
  - The 1553 transformer (4.70 mm) sits on B.Cu between the band and the JST-SH.
  - The GPS (2.5 mm) moves to B.Cu over the microSD.
- **Isolation band (TACCO scheme):**
  - CAN-TR / RS485 move to the top face at v 20.6, with their isolated rows facing the
    bottom edge.
  - CAN-FD / RS-485 / MIL-1553 sit at the bottom edge over the P2 rail.
  - `ISO_BAND` covers F.Cu and In1–In4 over u 7.3–34.9, v 18.0 to the edge. B.Cu under it
    carries only two-pad parts and the GPS / 1553-XFM, whose nets escape on B.Cu.
  - The X2Y bridges straddle the band edge on B.Cu.
- **Position-sensitive parts:** J-PWM moved 1.6 mm east so its pad-1 column clears the P1
  clip hole.
- **Gates:** ERC 0 errors (10 accepted `lib_symbol_issues`); DRC 0 violations with schematic
  parity 0; all 120 parts placed. Every bottom-face part was audited against the height and
  under-band rules (0 violations). Routing remains open (below).

**Update 2026-09-28 (MIL-STD-1553C fleet swap, S. Griffing decision; implemented by Claude
Opus 5.5):** `1553-XCVR` is now the **Holt HI-6138** BC/RT/MT protocol engine, a 48-pin
6 × 6 mm QFN on SPI0, replacing the HI-1573 and the AM6254 PRU Manchester codec.
- **Added parts:** a 50 MHz MCLK oscillator (`X-50M`, ECS-2520MV-500-BN-TR), `C-50M`,
  `R-1553IRQ`, and `C-1553D`.
- **PB2 P1 remap:** P1-7/8/9 become IRQ#/MR#/TXINHA GPIOs, P1-10 is freed, and P1-20 becomes
  the HI-6138 chip-select.
- **Placement:** the PCB was patched in place. The HI-6138 sits at the old site and no other
  part moved.
- **Gates:** ERC 0; DRC 0 with 0 schematic-parity issues.
- **References:** pin table and area budget in
  `../HI6138_FOOTPRINT_VERIFICATION.md`; plan in
  `docs/plans/2026-09-28-002-feat-fleet-1553c-hi6138-swap-plan.md`. MIL-STD-1553C is
  electrically identical to 1553B [REF-MIL-001].

> **Rev Q archived:** the prior revision's document, whose schematic and PCB
> had diverged into two different designs, is archived at
> `archives/avionics-archives/kicad-archives/Pilot-superseded-2026-09-19/Pilot-Rev-Q-doc.md`.
> `PILOT_FOOTPRINT_VERIFICATION.md` in this directory is kept in place — it is
> the per-footprint verification record that started the Rev T rebuild and is
> still an accurate account of what was wrong with Rev Q's land patterns.

---

## Purpose

Pilot is the flight-control and sensor cape for a PocketBeagle 2 Industrial
(AM6254) node. Per `docs/AVIONICS_PB2_REDESIGN.md` §3, every control node
(Pilot and XO capes alike) carries a point of presence on all four onboard
buses — MIL-STD-1553C, isolated CAN-FD, isolated RS-485, and Ethernet — so
any node can take over any role. Pilot additionally carries the node's
IMU, barometer and TPM. GNSS moved off the cape on 2026-10-12 to isolated CAN-FD GPS
pucks in the dorsal cups (see the update above).

## Board

55 × 35 mm (2.165 × 1.378 in), **6-layer** (F.Cu signal / In1.Cu GND with
isolated GND2 islands / In2.Cu signal / In3.Cu signal / In4.Cu +3V3 plane /
B.Cu signal), 1.6 mm (0.063 in), stacked on the PocketBeagle 2's two 2×18
0.1 in headers. Schematic, footprints, and PCB are produced by three
generators from one part table, gated by `kicad-cli`:

| File | Produces |
|---|---|
| `scripts/gen_pilot_sch.py` | `kicads/Pilot.kicad_sch` + `kicads/Pilot.kicad_sym` |
| `scripts/gen_pilot_footprints.py` | project-custom lands in `../Serenity-Custom.pretty/` |
| `scripts/gen_pilot_pcb.py` | `kicads/Pilot.kicad_pcb` + `kicads/Pilot.kicad_dru` + `kicads/Pilot.kicad_pro` netclass patch |
| `scripts/finish_pilot_pcb.py` | imports the freerouting session, adds outer GND pours, re-fills zones |
| `scripts/export_pilot_gerbers.sh` | production Gerbers + Excellon drill |

**Do not hand-edit `Pilot.kicad_sch` or `Pilot.kicad_pcb`.** A part or
placement change is a table edit in the generator; re-running it regenerates
every downstream artifact and the placer immediately reports any resulting
courtyard collision. See
`docs/solutions/conventions/pb2-cape-datasheet-verified-footprints-and-courtyard-budget-before-layout.md`
for the verification and area-budgeting discipline this rebuild established
(applies to XO, Observer, Flight Engineer, and CAN-PERIPH-GW-1 too).

Gates, run in this order after any generator change:

```bash
python3 scripts/gen_pilot_sch.py
kicad-cli sch erc --severity-all kicads/Pilot.kicad_sch          # shall be 0
kicad-cli sch export netlist --format kicadsexpr -o kicads/Pilot.net kicads/Pilot.kicad_sch
python3 scripts/gen_pilot_footprints.py
python3 scripts/gen_pilot_pcb.py
kicad-cli pcb drc --severity-all --schematic-parity kicads/Pilot.kicad_pcb   # shall be 0
# route (see "Routing" below), then:
python3 scripts/finish_pilot_pcb.py kicads/Pilot.kicad_pcb <routed.ses>
kicad-cli pcb drc --severity-all --schematic-parity kicads/Pilot.kicad_pcb   # shall still be 0
bash scripts/export_pilot_gerbers.sh
```

## Routing status (2026-10-11): 195 unconnected, DRC 0, parity 0 — interactive finish needed

Owner hand placement (2026-10-09) + 34 optimised bypass-cap moves
(`scripts/optimize/placement_moves.json`) + the ISO_BAND GPS notch (2026-10-11, below) +
the owner's freerouting run repaired to DRC 0 + 11 plane vias. Automated routing results
on this placement (Claude Opus 5.5):

| Strategy | Result |
|---|---|
| keep routing, plane fanout, repair (**committed**) | 196 unconnected |
| strip, plane fanout first, freerouting | hung in pass 1 (normalize loop); killed |
| strip, freerouting 15 passes, plane fanout after | 240 after phase 1, phase 2 hung; 222 after fanout |

freerouting 2.2.4 hangs whenever it starts from existing copper (phase 2, or pre-placed
fanout), so `scripts/route_pilot.sh` now caps each phase at 150 min and never lets a
worse/empty phase-2 session replace phase 1. The remainder is for KiCad's interactive
router: isolated-band nets (GND2/VCC2/CAN/RS-485), plane drops at the dense ICs (use
under-body via alleys, ideation idea 9), then the remaining logic nets.

## Routing history — earlier automated result tried and rejected

The board above is fully placed (0 courtyard collisions, 0 DRC errors) but
**0% routed** — all 388 connections are still ratsnest. Two freerouting runs
were made via the project's Specctra bridge (`tools/export-specctra-dsn.py` /
`tools/import-specctra-ses.py`, `pcbnew.ExportSpecctraDSN` /
`pcbnew.ImportSpecctraSES`, `java -jar
/usr/share/freerouting-2.2.4-linux-x64/lib/app/freerouting-executable.jar -de
<in.dsn> -do <out.ses> -mp <passes>`):

- First run, `-mp 40`: freerouting logs one pass every ~3-4 minutes and only
  writes the `.ses` at the very end of the whole run — after 8 passes
  (~24 minutes) and a plateau around 150-160 unrouted connections, it was
  killed with no output recoverable (consistent with the documented
  freerouting-headless caveat: it does not checkpoint between passes).
- Second run, bounded to `-mp 6` (~22 minutes): completed and wrote
  `Pilot.ses` — 161 of 389 connections still unrouted (58.6% routed) at exit.
  Importing it (`scripts/finish_pilot_pcb.py`) and running
  `kicad-cli pcb drc` on the result showed **9 genuine net-to-net shorts and
  118 hole-clearance violations**, concentrated around the dense 36-pad
  PocketBeagle 2 P1/P2 headers (e.g. a `MDC0` track routed directly across a
  `PTH pad [RMII1_TXD0]` on `PB2-P2`) — the Specctra round-trip does not carry
  this project's DRC/netclass configuration into freerouting, so its router
  does not treat a neighboring pad's copper as an obstacle the way KiCad's
  own interactive router would. **That result was rejected and the board was
  reverted to the clean, unrouted checkpoint above** rather than accepting a
  board with real shorts.

`gen_pilot_pcb.py` deliberately leaves the outer F.Cu/B.Cu pour-free (a
freerouting run treats a filled zone as fixed copper it shall route around);
`finish_pilot_pcb.py` adds the top/bottom GND pours back and re-fills all
zones after a routing pass is imported and accepted.

**Recommended next step:** finish routing interactively in the KiCad PCB
editor, whose push-and-shove router applies this project's live DRC rules
(including the `ISO_BAND` isolation-domain rule) as it routes, rather than
through the batch Specctra bridge. A from-scratch freerouting attempt with
tighter DSN-side clearance margins is a viable alternative but unproven at
this board's density (95%+ per-side prior to going to 6 layers) and header
pitch.

## Rev T changes from Rev Q

Rev Q's schematic and PCB had diverged into different designs (verified in
`PILOT_FOOTPRINT_VERIFICATION.md`: 7 of 46 footprints were not manufacturable
as drawn, and several net→pin maps were wrong). Rev T is a full rebuild, not
a patch, and changed several parts along the way:

| Area | Rev Q | Rev T | Why |
|---|---|---|---|
| Ethernet PHY | ADIN1300BCPZ (gigabit, LFCSP-40 6×6) drifted in during EMI-hardening | **DP83825I** (10/100 RMII, WQFN-24 3×3) | `docs/AVIONICS_PB2_REDESIGN.md` §3.1 specifies DP83825I; the ring is 100BASE-TX, never needed gigabit. Removes the 0.9 V core rail, 12 hardware straps, and one oscillator per PHY (RMII Leader mode sources 50MHzOut from a shared 25 MHz reference). |
| MIL-STD-1553B (→ 1553C, 2026-09-28: HI-1573 + PRU replaced by the **Holt HI-6138** protocol engine on SPI0; see the status update above) | DS26LV31/DS26LV32 (RS-422 line drivers) mislabeled as a 1553 transceiver | **Holt HI-1573** (3.3 V, MIL-STD-1553A/B compliant, QFN-44) + **Premier Magnetics PM-DB2791S** 1:2.5 direct-coupled-stub transformer + 2× 55 Ω isolation resistors + 2× SMAJ33CA | RS-422's ~2 V differential swing cannot meet MIL-STD-1553B §4.5.2 bus voltage levels. Bus A only is populated (bus B parked); Manchester II encode/decode stays in the AM6254 PRU per §94, unchanged. |
| GPS | u-blox SAM-M10Q (integrated patch antenna module) | **u-blox MAX-M10S** + U.FL to the airframe's dorsal-cup SMA bulkhead, with a bias-T (Table 52-54 of the integration manual) | Pilot flies inside a Faraday pouch (`docs/CARGO_SECTION_LAYOUT.md`) with the antenna in an external cup — an integrated-patch module could never see the sky. |
| Isolated CAN-FD | ATA6561 (non-isolated) | ISOW1044BDFMR, unchanged from the Rev Q *plan* (Rev Q's PCB never actually carried the right land) | 5 kV reinforced isolated CAN-FD with an integrated isolated DC-DC. |
| Isolated RS-485 | MAX3485E (non-isolated) / ADM2795EBRWZ (wrong land) | ISOW1412DFMR | Fleet-wide isolated-transceiver standardization (2026-07-26); ADM2795E needs a separate isolated supply ISOW1412 does not. |
| PWM / ESC servo header | 1×8 THT pin header | **Samtec TSM-108-01-L-DV**, 2×8 SMT 0.1 in, 4 channels × (SIG, +5V, GND, **PGND shield**) | Keeps the board usable on other platforms with PWM/DSHOT/BDSHOT ESCs (owner requirement, 2026-09-19) while an SMT header does not block the opposite copper layer the way the THT part did. SIG pins are the SoC's PRU-capable DSHOT0-3 balls. |
| Field connectors | J_ESC / J_SERVO PWM headers | **retired** — ESCs and tilt actuators live on the isolated CAN-FD/RS-485 trunk (WBS §1.10 U1) | The servo/ESC header above is a platform-portability port, not the flight actuation path. |
| Anti-tamper mesh | `TMESH_P`/`TMESH_N` routed through the isolated GND2 domains — the single largest DRC-blocking defect in Rev Q (13 genuine cross-domain violations, 0.125 mm measured spacing vs an 8 mm creepage target) | **not carried forward** | Open item — see "Known gaps" below. |
| Layer count | 4 | **6** | The 4-layer board had only F/B for signal routing and was ~95% full at real courtyard sizes — unroutable. See `docs/ideation/2026-09-19-pilot-cape-four-bus-area-ideation.html` idea #1. |
| Passives | 0402/0603 throughout | 0201 for straps, pull-ups, and HF bypass caps | See ideation idea #5. |

## Isolation — what the board actually delivers

The cape can offer roughly a 0.5 mm creepage gap between the isolated
(bus-side) domain of ISOW1044/ISOW1412 and everything else — not the 8 mm
IEC 62368-1 Annex G reinforced-insulation target Rev Q's document asserted.
This is enforced, not just documented: `gen_pilot_pcb.py` generates a named
rule area (`ISO_BAND`) covering the isolated pin rows and field connectors,
and `Pilot.kicad_dru` carries a custom DRC rule
(`iso_cross_domain_clearance`) requiring ≥ 0.5 mm between any ISOLATION-class
net and any non-ISOLATION net — DRC fails if a track, via, or the isolated
band's boundary is violated. The X2Y-CAN/X2Y-RS485 GND1↔GND2 RF bridging
capacitors (TI app note SLLA337A) are the one deliberate exception: their
whole function is a small, intentional high-frequency bridge across the
barrier, so they are explicitly excluded from the cross-domain rule rather
than silently failing DRC.

If the fleet needs true reinforced (5 kV, 8 mm creepage) isolation at the
cape rather than functional isolation, that is an architecture decision (see
`docs/ideation/2026-09-19-pilot-cape-four-bus-area-ideation.html` idea #3
and its rejected/harder alternatives), not a layout fix.

## Field Connectors

| Designator | Type | Pins | Function |
|---|---|---|---|
| PWR-IN | Molex Nano-Fit 4-pin (THT) | +5V_IN ×2, GND ×2 | Power entry |
| CAN-FD | JST SM04B-GHS-TB | GND2_CAN, CAN_H, CAN_L, VCC2_CAN | Isolated CAN-FD bus |
| RS-485 | JST SM04B-GHS-TB | GND2_RS485, A, B, VCC2_RS485 | Isolated RS-485 bus |
| MIL-1553 | JST SM04B-GHS-TB | BUS_P, BUS_N, GND, PGND (shield) | MIL-STD-1553C bus A |
| ETH1 / ETH2 | JST SM04B-GHS-TB | TXP, TXN, RXP, RXN | 10/100 Ethernet line pairs (isolated by the 749010012A magnetics) |
| J-PWM | Samtec TSM-108-01-L-DV, 2×8 SMT 0.1 in | 4 × (SIG, +5V, GND, PGND shield) | PWM/DSHOT/BDSHOT-capable servo/ESC port; SIG = PRU DSHOT0-3 balls |

## Known gaps (tracked in `avionics/WBS.md`)

- **Anti-tamper mesh not carried forward.** Rev Q's mesh was the single
  largest source of DRC failures and is not reproduced in Rev T. If tamper
  detection into the SLB9672 TPM is still required, it needs a per-domain
  redesign (one monitored mesh per isolation region, clear of the 0.5 mm
  ISOLATION moat) — an owner decision, not something to guess back in.
- **Single-bus 1553.** The HI-6138 has a dual-bus transceiver; only bus A is
  wired (TXINHB left on its internal pull-up, BUSB/BUSB* open). Dual-redundant 1553 would need a second PM-DB2791S
  transformer, TVS pair, and connector — real area cost, see the ideation
  doc's item #4.
- ~~U.FL antenna feed unverified against the physical cup mount~~ — moot since
  2026-10-12: GNSS is off the cape (GPS pucks in the dorsal cups, `avionics/WBS.md`).

## References

1. `docs/AVIONICS_PB2_REDESIGN.md` — fleet architecture, part list, power budgets.
2. `docs/CARGO_SECTION_LAYOUT.md` — node envelope (58×37×22 mm pouch), GPS antenna cups.
3. `docs/ideation/2026-09-19-pilot-cape-four-bus-area-ideation.html` — the
   ranked options that produced the Rev T design decisions, including the
   ideas that were tried and refuted (populating F.Cu between the PB2 rail
   pins; vertical GH4 connectors to save area; sharing one magnetic core
   between 1553 and Ethernet).
4. `docs/solutions/conventions/pb2-cape-datasheet-verified-footprints-and-courtyard-budget-before-layout.md`
   — the datasheet-verification and courtyard-budgeting convention this
   rebuild established for the fleet.
5. `PILOT_FOOTPRINT_VERIFICATION.md` — the Rev Q footprint audit that started
   the rebuild.
6. TI Application Note SLLA337A — isolation boundary layout guidelines for
   ISOW devices (X2Y bridge capacitor placement).
7. MIL-STD-1553C [REF-MIL-001] §4.5.1.5.2 / §4.5.2 — direct-coupled stub and bus
   electrical requirements (Holt HI-6138 DS6138 Rev S, Premier Magnetics PM-DB2791S).

## Usage notices

**Intended use:** the Serenity-UAV avionics, including this board, are intended
for use only on uncrewed aircraft.

**Würth Elektronik usage notice** — applies to the Würth parts on this board
(749010012A, 742792512, WE-MAPI 3015). Quoted verbatim from Würth Elektronik
eiSos, *749010012A data sheet* rev 004.000 (2024-04-11), p. 1 [REF-SENSOR-028];
the same notice appears on every Würth product data sheet. Owner decision
2026-09-26: the Würth parts are retained (avionics/WBS.md U7.1d).

> This electronic component has been designed and developed for usage in general
> electronic equipment only. This product is not authorized for use in equipment
> where a higher safety standard and reliability standard is especially required
> or where a failure of the product is reasonably expected to cause severe
> personal injury or death, unless the parties have executed an agreement
> specifically governing such use. Moreover Würth Elektronik eiSos GmbH & Co KG
> products are neither designed nor intended for use in areas such as military,
> aerospace, aviation, nuclear control, submarine, transportation,
> transportation signal, disaster prevention, medical, public information
> network etc.. Würth Elektronik eiSos GmbH & Co KG must be informed about the
> intent of such usage before the design-in stage. In addition, sufficient
> reliability evaluation checks for safety must be performed on every electronic
> component which is used in electrical circuits that require high safety and
> reliability functions or performance.

<!-- /USAGE-NOTICE-2026-09-26 -->
