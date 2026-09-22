# Serenity UAV — Avionics (Pilot / XO / Commo Cape Hardware) Work Breakdown Structure (Detail)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0
**Current design revision:** Rev T (2026-09-06, see `docs/WBS.md` §6.4 for changelog)

> **Detail-holder for the root WBS.** The repository-root [`TODO.md`](../TODO.md)
> is a compact index — headings, subheadings, and short (<=70-char) checkbox items
> only, per root `AGENTS.md`. This file carries the full task detail for the WBS
> branches the root indexes below. Close an item here first, then check it off in
> the root index as a commit prerequisite (root `AGENTS.md` "Revisions and Version
> Control").

*"I'm a leaf on the wind — watch how I soar. — Pilot"*

---

## §1.2 — PCB Design: Cape-A-1 and Cape-B-1 (archived)

*(root `WBS.md` §1.2)*

- [x] **Regenerate Cape-A-1 gerbers** — `.kicad_pcb` modified 2026-05-23 (tamper-mesh commit); gerbers in `serenity/kicad/gerbers/CAPE-A-1/` are from 2026-05-22.
    - Open in KiCad → Plot → Gerbers; overwrite files in `serenity/kicad/gerbers/CAPE-A-1/`; re-export drill files.
    - Run DRC to zero errors before plotting.
    - **BLOCKS Phase 6 fab order**

- [x] **Regenerate Cape-B-1 gerbers** — same timestamp issue. `serenity/kicad/gerbers/CAPE-B-1/` files are from 2026-05-22.
    - **BLOCKS Phase 6 fab order**

---

## §1.2a — PCB Design: Pilot, XO, Commo (EMI-Hardened Variants)

*(root `WBS.md` §1.2a)*

### ***EM hardening Objective is to ensure safe and controlled operations in hostile em/rf environments such as the vicinity of radiating commercial broadcast, amateur radio and cellular towers.***

Design files on branch `claude/cape-em-harsh-variants-9Yfr1`. Schematics (`*.kicad_sch`) and PCB
layout files (`*.kicad_pcb`) are complete. Gerber files have not yet been generated or DRC-verified.

**Key changes from -1 variants:**

- **CAN FD**: ATA6561 (non-isolated) → ISOW1044BDFMR (TI, SOIC-16W, 5 kV reinforced isolation +
    integrated DC/DC converter, IEC 62368-1 / VDE 0884-11)
- **RS-485**: MAX3485E (non-isolated) → ADM2795EBRWZ (ADI, SOIC-20W, 5 kV reinforced isolation +
    integrated DC/DC converter)
- **Ethernet PHY (Rev S baseline; introduced Rev Q)**: DP83825I (TI, LQFP-32, 10/100BASE-TX RMII) with EMI hardening:
    HX1188NL LAN magnetics (1500 V isolation), SRF2012-100Y CMC, PRTR5V0U2X TVS, TPS62933 1.8V
    supply. JST SM06B-GHS-TB-1MP connector (no RJ45). Pilot: 2× PHY (RMII0+RMII1);
    XO: 1× PHY (RMII0).
- **Commo**: SRF2012-100Y CMC on antenna coax shield, PRTR5V0U2X TVS on PTT/RX lines,
    X2Y bridging capacitor on RF ground plane, Würth 742792512 ferrite bead on +5V rail

**Transform scripts** (generate -2 files from -1 originals):

- `avionics/kicad/gen_cape_a2.py` → `CAPE-A-2.kicad_sch`
- `avionics/kicad/gen_cape_b2.py` → `CAPE-B-2.kicad_sch`
- `avionics/kicad/add_eth_phy.py` — ETH PHY isolation sub-circuit generator (called by above)
- `avionics/kicad/gen_cape_a2_pcb.py` → `CAPE-A-2.kicad_pcb`
- `avionics/kicad/gen_cape_b2_pcb.py` → `CAPE-B-2.kicad_pcb`

**Open tasks:**

- [x] **USB-to-Ethernet bridge (LAN9500A class) evaluated as an alternative Ethernet
    front end and REJECTED (not deferred), 2026-07-11.** Rationale captured in
    `docs/ETHERNET_PHY_TRADE.md`: a single-port USB bridge cannot offload HSR/PRP
    (IEC 62439-3), so the redundant ring collapses; USB adds non-deterministic
    latency/jitter unfit for the flight-control bus, a fragile 480 Mbps EMI ingress
    path in the 200 V/m environment, and hard/costly galvanic isolation — while
    wasting the AM6254/AM62A7 native MAC. Native DP83825I / ADIN1300 / KSZ9477 path
    retained. If "reduce per-PHY glue on Pilot" resurfaces, the on-architecture answer
    is a managed KSZ9477/KSZ9567 switch, tracked as a separate trade — NOT USB.

##### 1.2a.1 *Cape DRC / routing / ETH2 status (2026-06-12)* — see `avionics/kicad/README.md`

- [x] **Wire second Ethernet (ETH2) on Pilot.** `ETH2` / `ETH2-PHY` (ADIN1300) /
    `T-ETH2` (749010012A) were placed but unconnected; nets now mirror ETH1
    (`ETH2_LINE_*` → `T-ETH2` → `ETH2_*` → PHY), reusing the host-side `RMII1_*`,
    `MDIO`/`MDC`, `PHY2_INTRN`/`PHY2_RSTN`, `VCC2_ETH`/`GND`/`GND2_ETH` nets on
    PB2-P2. 44 pads assigned; diff pairs verified. *(PR #59, 2026-06-12)*
- [x] **Separate the two Pilot PHYs onto independent MDIO buses** (instead of an
    address strap). PHY1/ETH1-PHY → `MDIO0`/`MDC0` (CPSW MDIO, PB2-P2 pins 17/18);
    PHY2/ETH2-PHY → `MDIO1`/`MDC1` (2nd bus, PB2-P2 pins 1/2 = the two spare servo
    channels SERVO6/7). Each PB2-I NIC manages its own PHY; no shared-address
    conflict. PCB + schematic global labels updated. *(2026-06-12)*
    - **Firmware/DT:** PHY2's bus must be brought up as `mdio-gpio` (bit-banged) on
        the two repurposed balls; verify they are GPIO-capable in the PB2-I pinmux.
- [x] **Wire the field-connector pins to their signals on Pilot** (connectors were
    all floating). Done per each footprint's Description pinout: SERVO-PWM pads 1–6
    → SERVO0–5 (PWM); ESC-TLM → UART_ESC_TX/RX; GPIO-A…F → GND/+3V3 (+ `GPIO_EXP_*`
    signal pin labeled); CAN-FD → CAN_H/CAN_L; RS-485 → RS485_A/B; PWR-IN → +5V/GND.
    *(2026-06-12)*
- [x] **Source the 6 `GPIO_EXP_A…F` signals via an I2C GPIO expander.** Added
    `U-GPIO` (PCA9555DB, SSOP-24, addr 0x20) on the existing I2C1 bus with a
    `C-GPIO` 100 nF decoupling cap; P0_0–P0_5 → GPIO_EXP_A–F. *(2026-06-12)*
    - [ ] Verify/add I2C1 pull-ups (≈4.7 kΩ to +3V3 on SDA/SCL) — none on cape;
        confirm whether the PB2-I provides them.
    - [ ] Finalise placement of U-GPIO/C-GPIO (added at a tentative location).
- [x] **Add an ESC-PWM output connector for DSHOT0–3.** Added `ESC-PWM`
    (JST-GH 5-pin SM05B): pins 1–4 → DSHOT0–3, pin 5 → GND. *(2026-06-12)*
    - [ ] Finalise ESC-PWM placement (added at a tentative location).
- [ ] **Reconcile Pilot.md §14 field-connector table with the actual PCB
    connectors** (PCB has SERVO-PWM 1×8 + GPIO-A…F + ESC-TLM; §14 lists J_SERVO/
    J_ESC/J_GPS/J_ENC/J_SBUS/J_VBAT/J_FAN). Bring the doc and board into agreement.
- [ ] **Wire the MIL-1553 connector + transformer.** `MIL-1553` connector and the
    `1553-XFM` transformer coupling to the bus are unwired at the IC level; the
    driver/receiver (DS26LV31/32) are only partially netted.
- [ ] **Redesign the tamper mesh as a per-domain anti-tamper mesh (all 4 capes).**
    The current `TMESH_P`/`TMESH_N` cross-hatch grid on F.Cu/B.Cu shorts across SMD
    pads and across the isolated `GND2_*` domains (≈335 of Pilot's 465 DRC errors;
    similar on XO). Rework as one monitored mesh net per isolation region
    (secure/`GND` + per-`GND2_CAN`/`GND2_ETH`/`GND2_RS485` field side), keeping the
    0.5 mm `ISOLATION` creepage moat clear between domains. **BLOCKS DRC-clean.**
    Quantified against the IEC 62368-1 reinforced-insulation requirement in §0.6
    (2026-06-22): 13 genuine cross-domain `TMESH`-vs-`GND2_*` violations on Pilot
    (min 0.125 mm), 9 on XO (min 0.0 mm/direct contact) — both far short of the
    0.5 mm netclass minimum and the ≥ 8 mm physical creepage target in `Pilot.md`.
- [ ] **Carry the tamper signal over the link for the TPM-less boards.** Flight Engineer
    and Commo have no local TPM: route Flight Engineer's mesh signal to Pilot and
    Commo's to XO over the inter-board link.
- [ ] **Route the rearranged capes.** The manual component reseat left ~60 signal
    nets per cape unrouted (7 power/ground nets are planes). Headless freerouting
    was **not** usable (see toolchain findings in `avionics/kicad/README.md`):
    KiCad 9.0.2 `ExportSpecctraDSN` is broken in standalone Python, and freerouting
    2.1 headless never self-exits and emits incomplete SES. **Finish routing in the
    KiCad GUI**; route the impedance-controlled Ethernet pairs interactively
    (length-matched, 100 Ω ±10% MDI). **BLOCKS gerbers / fab.**
- [ ] **Clear residual DRC after mesh + routing** (counts measured 2026-06-12,
    error+warning): Pilot 465 / 121 unconnected, XO 554 / 146, Commo 421 /
    160, Flight Engineer 221 / 181. Remaining types after the mesh fix are mostly
    silk-over-copper, text-height, courtyard-overlap, and lib-footprint mismatch.

- [ ] **Finish Pilot PCB (CAPE-A-2) close-out pass:**
    - [ ] Verify every external-facing connector (SERVO-PWM, ESC-PWM, MIL-1553, CAN-FD,
        RS-485, ETH) is a shielded-shell part with shell tied to PGND — audit against
        the footprint Description pinout already documented at §1.2 line ~1340.
    - [ ] Run ERC/DRC net-validity pass — confirm zero unconnected nets outside the
        13-net Commo-style residual list; cross-check against the 465/121 DRC count
        already logged for Pilot at §1.2.
    - [ ] Verify all ferrite beads are placed at each digital/RF section boundary and
        on +5V/+3V3 entering from off-board connectors (pattern already used on
        Commo's +5V boundary, §1.2/§1.3 Phase 3).
    - [ ] Verify isolation caps/creepage moat (0.5 mm `ISOLATION`) are intact after the
        per-domain tamper-mesh rework (§1.2, "Redesign the tamper mesh").
- [ ] **Add SBUS/UART DIP switch to Pilot** — add a 2-position DIP (or solder-jumper
    pair) to select SBUS vs. plain UART framing on the existing J_SBUS-equivalent
    pad, matching the J_SBUS line item already in Pilot.md §14's field-connector
    table (§1.2, "Reconcile Pilot.md §14...").
- [ ] **Generate Pilot gerbers** — superseded by the 2026-09-19 schematic-first Rev T
    rebuild (`avionics/kicad/Pilot/Pilot.md`; `CAPE-A-2.kicad_pcb` no longer exists).
    Rev T is fully generated (`gen_pilot_sch.py`/`gen_pilot_footprints.py`/
    `gen_pilot_pcb.py`), datasheet-verified, 6-layer, ERC 0 / DRC 0 at 0%
    routed (388 connections). Two freerouting attempts via the Specctra bridge
    did not produce a safe result — the second completed but introduced 9 real
    shorts + 118 hole-clearance violations around the dense PocketBeagle 2
    headers and was rejected; see `Pilot.md` "Routing status" for the full
    account. Remaining: route (recommend KiCad's interactive push-and-shove
    router, which applies this project's live DRC rules including the
    isolation-domain `ISO_BAND` rule, unlike the batch Specctra round-trip),
    then `bash scripts/export_pilot_gerbers.sh`.
    - **BLOCKS Pilot fab order**
- [ ] **Generate XO gerbers** — `CAPE-B-2.kicad_pcb` complete; same DRC + export procedure;
    export to `avionics/kicad/gerbers/CAPE-B-2/`.
    - **BLOCKS XO fab order**

- [x] remove Wi-Fi, sik, and loRa antennas from XO. Use filtered chokes on rf lines to route all
    RF signals from antennas to Wi-Fi, lora, zigbee,and sik xcvr circuits on XO, and/or use uart
    or i2c with filtering to connect isolated xcvrs to the cape. **Done (2026-06-05):** Added §13
    antenna filter chains to CAPE-B-2.kicad_sch — each radio ANT pin now routes through a Johanson
    BPF (FL_LORA/FL_SIK: 0915LP15B0100E; FL_WIFI: 2450BP15B050E) and RCLAMP0502B ESD shunt to a
    dedicated SMA connector (J_SMA_LORA, J_SMA_WIFI, J_SMA_SIK). SiK uses Hirose U.FL J_SIK_ANT for
    module pigtail. All connector shells PGND. See CAPE-B-2.md §13.
- [x] **Re-evaluate space / restore Ethernet to XO** — One DP83825I EMI-hardened PHY
    added to XO at Rev R (introduced Rev Q); J_ETH_B connector populated. Board has adequate
    space; RF SMA connectors remain. *(done 2026-06-07)*
- [ ] **Zigbee RF chain was never actually added to XO — PCB scope gap (flagged 2026-06-22,
    cross-ref §1.4.2).** The "remove Wi-Fi, sik, and loRa antennas" item above (2026-06-05)
    names Zigbee as a target XCVR circuit, but only LoRa/SiK/Wi-Fi filter chains were built;
    `XO.kicad_sch` has no CC2652R7 (or equivalent Zigbee SoC), no Zigbee antenna filter, and
    no SMA/diplexer pad. `CLAUDE.md` lists Zigbee 2.4 GHz as one of the 4 required external
    C2 links — this is a real hardware gap, not yet scheduled to a revision. **Antenna
    strategy already decided (§1.4.2, 2026-06-22):** restrict WL1837MOD Wi-Fi to 5 GHz only
    and feed CC2652R7's 2.4 GHz path through a passive 2.4/5 GHz diplexer onto the existing
    shared Wi-Fi antenna (no separate Zigbee antenna/SMA pad needed). Still open: add
    CC2652R7 + diplexer to a Cape-B-2 schematic revision; decide which bay(s) carry it.
- [x] **REJECTED (2026-09-20): mLRS as XO's SiK radio-link protocol.** Considered during the
    XO board-area rebuild (via `ce-ideate`) as a possible replacement for the RFD900ux-SMT SiK
    channel. XO's and Commo's radio links provide **redundant multiband connectivity between
    the UAV and its human-piloted ground station** — the whole point is path diversity across
    independent hardware/modulation families. mLRS is a real, mature open-source project
    (github.com/olliw42/mLRS) with genuinely competitive range/performance, but it runs on
    Semtech LoRa silicon (SX1280/1276/1262/etc.) — the **same radio family Commo's LoRa link
    already uses**. Adopting it on XO would collapse two supposedly-independent links onto one
    LoRa failure domain (interference, jamming, a LoRa-specific hardware defect), defeating the
    redundancy the two-link architecture exists to provide. Also a poor fit operationally: mLRS
    is architected as an MCU+radio-chip *subsystem* (not a self-contained module like SiK), which
    would have made XO's board-area crisis worse, not better. Kept for the record per the
    project's "explicit rejection with reasons" ideation discipline — do not re-propose mLRS for
    XO or any other node carrying a LoRa link elsewhere in the fleet.
- [ ] **APPROVED DIRECTION (2026-09-21, supersedes the same-day initial
    rejection below): relocate SiK (RFD900ux-SMT) from XO to Commo, remove
    Commo's LoRa (RFM95W).** Considered via `ce-ideate` (targeted
    primary-source analysis, not the full multi-agent dispatch — disclosed).
    Initial pass flagged three findings and rejected the idea; the owner
    overruled two of the three as acceptable tradeoffs and asked for the
    third to be checked against real numbers:
    - **Firmware rewrite (SiK↔LoRa/AX.25 protocol stacks on both hosts):
      owner-accepted.** Rationale: "firmware can be rewritten more easily
      than parts can be manufactured" — a real cost, but not a blocker.
    - **Commo's power budget (250 mA documented vs SiK's 1A Tx peak):
      owner-accepted.** Commo is already the fleet's high-power radio-comms
      cape by design; per the owner, absorbing SiK's draw there is "mostly
      just moving the power requirement from XO, not building a whole new
      power distribution rail from the batteries."
    - **Footprint headroom: CHECKED, confirmed sufficient.** Commo's actual
      `Commo.kicad_pcb` (not estimated) carries 81 footprints at **1342.7
      mm^2 (34.9%)** of the 3850 mm^2 two-sided ceiling — LoRa's own real
      placed courtyard is 307.4 mm^2 (not the 289 mm^2 footprint-generator
      estimate used in the first pass). Remove LoRa -> 1035.3 mm^2 (26.9%);
      add RFD900ux-SMT (666.0 mm^2, same courtyard as XO's own instance) ->
      **1701.3 mm^2 (44.2%)** — comfortably under the ~70% guideline ceiling
      for Commo's 4-layer stackup (`Commo.md` "Layer stackup: 4-layer"),
      leaving ~994 mm^2 of headroom even against that conservative bar.
      Commo was never remotely area-constrained the way XO is.
    **Resolved 2026-09-21 — XO's replacement link decided: mLRS on a Seeed
    Wio-E5 module.** Removing SiK from XO clears ~666 mm^2 there; what fills
    the slot was a separate decision from the earlier mLRS-for-SiK rejection
    (that rejection assumed XO would still carry a SiK-class self-contained
    modem in parallel with a new LoRa-family link, collapsing path diversity
    — here XO no longer carries SiK at all, so a LoRa-family link on XO does
    not collapse anything; the fleet still ends up with one SiK-class link
    (now on Commo) and one LoRa-class link (now on XO), same split as today).
    - **mLRS vs. bare LoRa+custom firmware:** mLRS chosen — closest
      like-for-like replacement for what SiK actually did (MAVLink-transparent
      telemetry + bidirectional RC + frequency hopping, out of the box,
      github.com/olliw42/mLRS), vs. writing a new protocol stack from scratch.
    - **Target MCU: STM32WLE5 (mLRS's own primary-supported target), NOT a
      tiny non-ARM MCU.** A CH32V006-class RISC-V MCU was considered and
      rejected: mLRS's firmware is confirmed ARM-only (STM32F103/G4/L4/F3/
      WLE5, or ESP32/ESP8285) with **no RISC-V support in the codebase at
      all** — this is a firmware-architecture hard-stop, not a size
      tradeoff, and CH32V006 also has no integrated radio (would still need
      a separate discrete Semtech LoRa chip) and only 8KB RAM vs. the
      32-64KB SRAM mLRS's codebase assumes. STM32WLE5 has the LoRa radio
      **integrated in the die** (verified against ST's own datasheet,
      `avionics/datasheets/stm32wle5jc.pdf`): UFQFPN48 (7x7mm) or UFBGA73
      (5x5mm) package, up to 256KB flash / 64KB SRAM — single-chip courtyard
      ~36-64mm^2, smaller than the bare RFM95W module (289 mm^2) it's
      replacing, and a rounding error against the ~666 mm^2 SiK frees up.
    - **Hardware form factor: pre-certified module (Seeed Wio-E5), not a
      bare-chip layout.** Considered Seeed Wio-E5 vs. EByte E77-MBL (mLRS's
      two suggested "easy" pre-certified options) on supply-chain grounds:
      EByte is Chengdu Ebyte Electronic Technology Co., Ltd. (Chengdu,
      China) with no public schematics/design files. Seeed Wio-E5 is
      designed by Seeed Technology Co., Ltd. (Shenzhen, China HQ; US offices
      in Austin/San Francisco are sales/support only, not manufacturing —
      no US fab exists for this product) but **publishes full open-source
      schematics/KiCad source/documentation** for the module itself, and the
      underlying silicon (STM32WLE5) is from STMicroelectronics N.V., a
      company incorporated in the Netherlands — satisfies the project's
      source-control requirement on the chip even though final module
      assembly is in China. **Owner's call**, made explicitly on these
      tradeoffs (open documentation + EU-domiciled silicon outweighing
      Chinese module assembly, vs. EByte's closed documentation with no
      offsetting benefit).
    **Implemented 2026-09-21 — both boards' schematics rebuilt, ERC 0 on
    both.** XO: `gen_xo_sch.py` regenerated with WIOE5 (mLRS/Wio-E5) IC
    entry replacing the SIK entry, plus a second TPS62933 regulator
    (`U-1V8RF`) sharing the RF 1.8V rail instead of a separate TLV75718
    LDO (owner's "one bigger regulator, not two" call) — `kicad-cli sch
    erc` = **0 violations**. Commo: since `gen_commo_sch.py` is PCB-first
    and confirmed drifted (do not re-run), the LoRa->SiK swap was done via
    a new one-off script, `avionics/kicad/Commo/scripts/swap_lora_for_sik.py`
    (direct S-expression lib_symbol + instance + wiring surgery, matching
    Commo's existing per-part symbol convention). Also fixed, in the same
    pass, 2 pre-existing dangling-net bugs unmasked once the swap's
    incidental ERC improvements exposed them clearly: `RF_ANT_SW` (a T/R
    switch antenna pin) was on a differently-named net one row away from
    the already-working ANT filter chain — renamed to merge; and
    `PA_EMIT`/`U3B` emitter-degeneration resistor was in-circuit but the
    "PA 100mW" (2N3866) transistor's own emitter pin was wired straight to
    GND, bypassing the resistor — rewired onto `PA_EMIT`. 37 PB2-header
    passthrough signals genuinely unused by Commo (RMII0/1_*, SDIO_*,
    PWM_CH*, WINCH_*, LOAD_CELL_*, TPM_*, PHY1_*, I2C0_*, MCAN1_*, RS485_*,
    CAN_STB, PRU_1553_*) were converted from `global_label` to `no_connect`,
    matching the same-meaning convention already proven ERC-clean on Pilot
    and XO. `DDS_FSYNC` (the MCP4921 TX DAC's SPI chip-select, previously
    never routed to a controller pin) was wired to PB2-P1 pin 26 — the
    exact pin freed by the LoRa->SiK swap (was `SPI1_CS_LORA`, now unused
    since SiK talks UART not SPI) — **owner's explicit call** (asked
    directly rather than guessing a GPIO assignment). `kicad-cli sch erc`
    = **0 violations** on Commo too (down from 45: 43 pre-existing +
    3 incidentally introduced then fixed by the swap itself).
    **PCB sync (schematic-driving-PCB, not the reverse):** XO's PCB
    regenerated via `gen_xo_pcb.py` (143 footprints, 135 nets; 86.1% of
    the 2-sided area ceiling; DRC 169 violations/0 schematic-parity
    issues — residual violations are the pre-existing 41-footprint
    unplaced backlog, not new). Commo's PCB (no reliable generator exists
    for it either) was synced via direct `pcbnew` Python scripting: removed
    the old RFM95W footprint, added the 8 new SIK-chain footprints (SIK +
    6 passives + MMCX jack), matched nets 1:1 to the schematic (verified
    against the real `Commo:S_SIK` lib_symbol pin table, not guessed).
    While placing the SIK footprint, DRC caught a real, previously-latent
    footprint-geometry bug in `gen_xo_footprints.py`'s `rfd900ux_smt()`:
    the estimated 1.9mm pad pitch (flagged "NOT pixel-verified" in that
    function's own docstring) was replaced with the real Table 6-1 value
    (A=2mm, confirmed against "RFD900ux DataSheet v1.2.pdf" p.11 — 13
    gaps x 2mm + 1.5mm margins each side = 29mm body height, exact match),
    and the pad's width/height (B=2.4mm depth-into-board, C=1mm along-edge)
    had been assigned to the wrong axis, causing every adjacent castellated
    pad to short into its neighbor — fixed and confirmed via DRC (the
    SIK-internal `shorting_items` count dropped to 0 after the fix).
    **Known residual, disclosed, not silently papered over:** Commo's
    existing hand-placed layout is extremely dense (88 footprints in
    55.1x35.1mm) and has no contiguous free region large enough for the
    21x29mm SIK module without touching an existing neighbor in any
    orientation — the aggregate-area headroom computed above (46.1% used
    of the 2-sided ceiling post-swap) does not by itself guarantee a 2D
    placement fits. Placed SIK rotated to minimize the conflict (fits
    cleanly between the PB2-P1/PB2-P2 connector rows; the SIK-internal
    pad-pitch bug is fixed) but its GND thermal pad and edge pads still
    partially overlap ETH-PHY's and T-ETH's back-layer footprints —
    `kicad-cli pcb drc --schematic-parity` on Commo: 0 net conflicts,
    0 missing/extra footprints (down from 8 missing + 1 extra), 262
    ordinary DRC violations (up from a 160 pre-existing baseline — the
    increase is the disclosed placement-density cost of fitting 8 new
    parts into an already-packed board, not a hidden regression), 93
    schematic-parity issues remaining (down from 136; all residual ones
    are either the pre-existing `footprint_symbol_mismatch` noise from
    Commo's own established convention of leaving symbols' Footprint
    property blank, or 4 pre-existing duplicate mounting-hole footprints
    unrelated to this work). **Real physical floorplan rework — moving
    ETH-PHY/T-ETH or re-siting SIK's neighbors — is still needed before
    Commo's PCB is fab-ready; flagging for the owner's hand-placement
    pass, per the same convention already accepted for XO's own PCB.**
- [x] **REJECTED (2026-09-21, initial pass, superseded above): swap XO's SiK
    (RFD900ux-SMT) with Commo's LoRa (RFM95W) between boards** on three
    findings — footprint asymmetry (RFD900ux-SMT's 666 mm^2 courtyard vs
    RFM95W's then-estimated 289 mm^2, a 2.3x ratio), Commo's documented 250 mA
    power budget vs SiK's 1A Tx peak, and the SiK-modem-vs-bare-LoRa-chip
    firmware rewrite on both hosts. **Superseded same day**: the owner
    accepted the power and firmware costs as tradeoffs worth taking, and
    asked for the footprint finding specifically to be re-checked against
    Commo's real PCB rather than estimated — see the approved-direction entry
    above for the confirmed numbers. Kept for the record (not deleted) per
    the project's "explicit rejection with reasons" discipline — the
    reasoning here was sound given what was checked at the time; it just
    turned out the one load-bearing finding (footprint) didn't hold once
    verified against Commo's actual PCB instead of a generic estimate.

- [ ] **Generate Commo gerbers** — `XCVR-49MHZ-2.kicad_pcb` complete; export to
    `avionics/kicad/gerbers/XCVR-49MHZ-2/`.
    - **BLOCKS Commo fab order**
- [ ] **FCC Part 15 §15.235 pre-compliance checklist for Commo** — document field strength
    (≤10,000 µV/m at 3 m per §15.235(a), ≈30 µW / −15.2 dBm EIRP-equivalent — requires firmware
    PA limit, not the ≤100 mW previously assumed), harmonic suppression ≥40 dBc at 2nd/3rd
    harmonics (§15.235(b)/§15.209), FCC ID silkscreen labeling block (§2.803/§15.19).  Not
    Part 95 — see §0.1.
- [ ] **EMI isolation validation checklist** — verify isolation barrier clearance: ISOW1044BDFMR
    5 kV working voltage; ADM2795EBRWZ 5 kV working voltage; measure CMRR at 1 MHz on CAN and
    RS-485 channels; verify differential impedance 100 Ω ±10% on ETH MDI traces.

- [ ] **Merge `claude/cape-em-harsh-variants-9Yfr1` → master** after gerbers pass DRC and
    pre-compliance checklist is signed off.

- [ ] **Design Faraday cages / boxes to protect all PCBs** — minimize weight/space while meeting
    the 500 W/m² design objective. Placeholder geometry (FAR-CAGE-AV 76×56×88 mm, FAR-GASKET-AV,
    FAR-FAN-40, FAR-EMI-VENT-40, FAR-BOND-STRAP, FAR-FT-PANEL, FAR-FERRITE-4MM) already exists at
    §1.1.5 (364 g / 0.80 lbm system total) — these sub-tasks convert the placeholders into
    real, build-ready enclosures:
    - [ ] **Shepherd's Room cage** (Cape-A-2 + Cape-B-2 stack, no Commo) — final wall thickness,
        seam/gasket detail, FAR-FAN-40 mount, FAR-EMI-VENT-40 vent location.
    - [ ] **Inara's Shuttle cage** (Cape-A-2 + Cape-B-2 stack, no Commo) — same scope as Shepherd's.
    - [ ] **River's Room cage** (Cape-A-2 + Cape-B-2 + Commo stack) — add Commo board clearance and
        LoRa/49 MHz feedthrough ports to the FAR-FT-PANEL design.
    - [ ] **Simon's Medbay cage** (Cape-A-2 + Cape-B-2 + Commo stack) — same scope as River's Room.
    - [ ] **Flight Engineer (PDB) enclosure** — verify whether the PDB needs a full Faraday cage or only a
        bond strap to the keel ground plane (no TPM/RF on Flight Engineer; see §1.2 "Carry the tamper
        signal over the link for the TPM-less boards").
    - [ ] Bond each cage to the airframe ground reference via FAR-BOND-STRAP with no second
        return path (avoid ground loops per §1.4.1 prose constraint).
    - [ ] Re-run the §1.1.5 mass budget after all 5 enclosures are finalized — confirm cumulative
        T/W stays ≥1.2 (currently estimated ~1.19–1.25, §1.1.5).

- [ ] **Specify / implement tightly twisted pair bonded shielded wiring throughout the aircraft** —
    per-bus-type wiring spec (duplicates the per-bus breakdown tracked at §1.4.3/§1.4.4; this
    item is the airframe-wide harness/cable-selection pass, those are the connector/pinout pass):
    - [ ] CAN FD trunk (inter-node ring) — shielded twisted pair, 120 Ω characteristic impedance,
        drain wire bonded at each node chassis, not floating mid-run.
    - [ ] RS-485 trunk — shielded twisted pair, 120 Ω, daisy-chain topology, end termination at
        the two physical bus ends only.
    - [ ] MIL-STD-1553B bus — twinax/twisted-shielded-pair per the existing 1553-XFM transformer
        coupling spec (§1.2), stub length ≤1 ft from coupler to RT.
    - [ ] Ethernet (CPSW3G ring) — shielded Cat5e/Cat6, 100 Ω ±10% MDI pairs matching the
        impedance-controlled PCB traces already specified at §1.2.
    - [ ] Servo/PWM and ESC telemetry leads — twisted pair, routed ≥5 mm from RF/antenna runs.
    - [ ] Power harness (14 AWG nacelle feeds, battery-to-Flight Engineer) — twisted where co-routed with
        signal wiring; ferrite bead at each digital/RF section boundary crossing.

---

### Pilot footprint verification and schematic-first rebuild (2026-07-13/14)

- [ ] **Rebuild the 7 non-manufacturable Pilot footprints before fab** — *(the
    verification itself was DONE 2026-07-13, Claude Opus 4.8; the item is re-titled
    2026-09-15 to name the open work, per the never-leave-a-resolved-item-unchecked
    rule.)* Full report:
    `avionics/kicad/Pilot/PILOT_FOOTPRINT_VERIFICATION.md`. Fixing any of these remaps
    pin→net on flight hardware, so each needs the confirmed schematic pinout first (ERC
    is not clean — see below) and MUST NOT be guessed.
    - [ ] **CAN-TR (ISOW1044BDFMR): wrong land — has 16-pad `SOIC-16W`, part is a
        20-pin DFM (SOIC-20 land).** Datasheet `isow1044.pdf` §7 / Fig 7-1. (This is the
        fleet-wide ISOW1044 footprint error; confirmed present on Pilot.)
    - [ ] **TPM (SLB9672): wrong land — has `QFN-32 4×4 P0.4mm EP2.65`, part is UQFN-32
        0.5 mm pitch, 5×5 body, EP 3.6×3.6.** Datasheet `SLB_9672XU20_Infineon.pdf` p.9/11.
    - [ ] **ETH1-PHY / ETH2-PHY (ADIN1300BCPZ): wrong land — has `QFN-48 7×7`, part is
        40-lead LFCSP 6×6 mm (CP-40-26) w/ EP.** Datasheet `adin1300.pdf`.
    - [ ] **RS485 (ADM2795EBRWZ): wrong land — has 20-pad `SOIC-20W`, part is 16-lead
        SOIC_W (RW-16).** Datasheet `adm2795e.pdf` Tables 3/4/7. (Also fix `Pilot.md` §3.)
    - [ ] **BARO (BMP388): wrong land — has 8-pad `LGA-8 2.0×2.5`, part is 10-pin metal-lid
        LGA 2.0×2.0 mm.** Datasheet `bst-bmp388-ds001.pdf`.
    - [ ] **GPS (SAM-M10Q-00B): placeholder `Package` (2-pad blob) — author real u-blox
        SAM-M10Q LGA module footprint.** Datasheet `SAM-M10Q_DataSheet_UBX-22013293.pdf` §3.1.
    - [ ] **1553-XFM (SM-1553-11): placeholder `Package` (2-pad blob) — author real SM1553
        transformer footprint. NOTE: SM1553 series is THROUGH-HOLE** (adds THT pads/drills
        vs current SMD stub). Datasheet `SM1553-Series...RevD.pdf`.
    - [ ] **U-ISO-RX / U-ISO-TX net mapping is non-functional (ISO6442) — land pattern is
        FINE, the wiring is not.** Part resolved 2026-07-13: ISO7642FDWRR is EOL, TI
        replacement is **ISO6442** (drop-in: DW-16 / SOIC-16W, 2-forward/2-reverse,
        pin-compatible — `iso6442.pdf`), so the `SOIC-16W` land is correct. BUT checked
        against ISO6442 Table 5-1: (a) power/gnd pins carry signals (pin 2 `GND1`=RMII0_RXD0;
        U-ISO-TX pin 2 `GND1`=RMII0_REF_CLK) — won't power up; (b) every channel is shorted
        across the barrier (same net on side-1 input AND side-2 output pin) — no isolation;
        (c) 50 MHz RMII `REF_CLK` through a general-purpose digital isolator is unworkable.
        The ETH-isolation subcircuit must be re-architected + re-netted (schematic-first),
        and the BOM/`Pilot.md`/`REFERENCES.md` strings changed ISO7642FDWRR → ISO6442.
    - [ ] **Remaining part-number gaps (land OK, part unconfirmed):** (a) X2Y 4.7 nF caps
        (`X2Y_Cap_4T_0402`) — no mfr P/N supplied; (b) Molex Nano-Fit 4P (PWR-IN) — no
        datasheet supplied. *(JST GH 4P/3P connectors VERIFIED CORRECT vs `eGH.pdf` — GH
        1.25 mm pitch, SM0xB-GHS-TB — no action.)*
    - [ ] **Rewrite `Pilot.md` §§1–3 to the as-built architecture** — board uses ADIN1300 +
        Würth 749010012A + ISO7642 + ADM2795E(RW-16); `Pilot.md` still documents a stale
        DP83825I + HX1188NL + TPS62933 design that is not on the PCB.
    - [ ] **Verified CORRECT (no action):** DS26LV31, DS26LV32, ICM-42688-P, PCA9555DB,
        SMAJ33CA, PRTR5V0U2X, SRF2012-100Y, 742792512, PB2 P1/P2 sockets, SERVO-PWM header.
- [ ] **Pilot SCHEMATIC-FIRST REBUILD — decided + started 2026-07-14 (user).**
    Verification proved the schematic (`Pilot.kicad_sch`) and PCB are *different designs*
    (schematic = DP83825I + HX1188NL + TPS62933; PCB = ADIN1300 + 749010012A + ISO6442),
    and that net→pin maps are wrong on multiple parts (TPM signals on NC/VDD/GND pins;
    ISO6442 channels shorted). Fixing the PCB alone would re-create the Commo/XO sch↔pcb
    divergence, so the rebuild is **schematic-first** (user choice). **Ethernet PHY =
    ADIN1300** (the EMI-hardening rework moved to ADI's industrial PHY; it's on the PCB and
    is the datasheet on hand) — `Pilot.md`/schematic DP83825I baseline is superseded.
    Auditable generator: `avionics/kicad/Pilot/scripts/gen_wash_sch.py`, datasheet-accurate
    full-pinout symbols → `kicads/Wash_rebuild.kicad_sch` (loads in kicad-cli 9.0.2; ERC
    only expected off-sheet-global warnings).
    - [x] Core isolated-bus + security + GPS ICs authored with full datasheet pinouts:
        **CAN-TR (ISOW1044, 20-pin), RS485 (ADM2795E, 16-pin RW-16), TPM (SLB9672, 32-pin
        correct 17–24 SPI map), GPS (SAM-M10Q, 16-pin).**
    - [ ] Author ETH section on **ADIN1300** (40-LFCSP) + Würth 749010012A magnetics +
        ISO6442 — redesign the RMII isolation (current scheme shorts the barrier / 50 MHz
        REF_CLK through a digital isolator is unworkable).
    - [ ] Add remaining ICs: 1553 (DS26LV31/32 + SM1553 xfmr), IMU (ICM-42688-P), baro
        (BMP388, 10-pin), compass (MMC5983MA/QMC5883L), INA226, PCA9555, 74LVC1G14.
    - [ ] Add PB2-P1/P2 (2×36) SoC headers + connectors + passives (TVS/CMC/X2Y-Syfer-0805/
        Nano-Fit); tie the off-sheet global labels; drive GND/power (PWR_FLAG) to clear ERC.
    - [ ] Associate corrected footprints (per PILOT_FOOTPRINT_VERIFICATION.md) to each symbol;
        regenerate/re-sync the PCB; ERC + DRC --schematic-parity to zero.
    - [ ] Once approved, promote `Wash_rebuild.kicad_sch` → `Pilot.kicad_sch` (archive old).
- [x] **Finish Pilot PCB (CAPE-A-2) close-out pass** — *duplicate of the §1.2a entry
    above (identical four sub-items), consolidated 2026-09-15; the §1.2a copy is the
    live one.*

### §1.9.3 — Trust-Module MCU/TPM Retarget (MSPM0G351x-Q1 + SLB 9672), 2026-08-03

*(Moved here 2026-09-15 from root `TODO.md` §1.2d, where this detail had lived with no `WBS.md` home — the only copy of these findings was in the open-items view. Root `WBS.md` §1.2d now indexes this section. See also `docs/WBS.md` §0.10.2 item 4.)*

Applied 2026-08-03 by `avionics/kicad/retarget_mspm0g351x_slb9672.py` (schematics) and
`avionics/kicad/retarget_pcb_footprints.py` (PCBs).  Parts per REF-SENSOR-017 and REF-SEC-002.

| Board | MCU | Package | TPM |
|---|---|---|---|
| Observer (observer) | `M0G3519QRGZRQ1` | 48-pin RGZ VQFN 7×7 | `SLB 9672AU2.0` |
| `CAN-PERIPH-GW-1` (gateway) | `M0G3518QRHBRQ1` | 32-pin RHB VQFN 5×5 | `SLB 9672AU2.0` |
| FlightEngineer (flight engineer) | `M0G3518QRHBRQ1` | 32-pin RHB VQFN 5×5 | `SLB 9672AU2.0` |

- [x] Verify the MSPM0G351x-Q1 RGZ-48 pin map against the MSPM0G350x it replaces —
      identical for all 48 pads plus the exposed pad (SLASFA6B Fig 6-5 vs SLASEX6C Fig 6-4).
- [x] Re-pinmux the gateway and FlightEngineer onto RHB-32, which bonds out PA0–PA27 only and has
      no PBx ports: RS485_TX→PA8 (UART1_TX PF2), RS485_RX→PA9 (UART1_RX PF2),
      RS485_DE→PA21, RS485_FLT_N→PA22, CANFD_FLT_N→PA23 (FlightEngineer),
      FLEX_PWM_IO→PA25 (TIMA0_C3 PF5), FLEX_BSHOT_IO→PA26 (TIMG8_C0 PF4).
- [x] Swap and re-anchor the PCB footprints on the gateway (U1_1/U1_2) and Observer (U3).
- [x] Tie the TPM exposed pad to GND on all three boards — the SLB9670 symbol omitted pad 33
      entirely, so it was floating (Infineon SLB9672 datasheet rev 1.3 §2.1.2 requires it).
- [x] Correct the MCU land pattern: the design used
      `QFN-48-1EP_7x7mm_P0.5mm_EP5.15x5.15mm`, which KiCad's own `descr` identifies as an
      **Analog Devices LTC legacy** outline. TI's RGZ0048F exposed pad is 4.1 mm square, so
      the old land overhung the package thermal pad by 0.525 mm per side.
- [x] Separate FlightEngineer's overlapping `U_MCU` / `U_TPM` symbols (17 pads shared a coordinate,
      shorting the SPI bus and tying MCU VCORE to TPM GND); `U_TPM` moved +34.29 mm.

**Open — blocks fabrication:**

- [ ] **Re-route the gateway MCU area.** U1_1/U1_2 went from 48 pads at 7×7 mm to 32 pads at
      5×5 mm, so every trace into them is dangling. Needs a manual placement/routing pass and
      a DRC sign-off before gerbers.
- [ ] **Confirm MSPM0G351x-Q1 errata and TRM applicability.** SLAZ742G covers MSPM0G3x0x /
      G1x0x / G3x0x-Q1 and does not enumerate MSPM0G3518/3519; SLAU846E contains no
      occurrence of either part number. Obtain the correct errata/TRM for MSPM0G351x-Q1
      before firmware sign-off (REF-SENSOR-018 "requires verification").
- [ ] **Update firmware pinmux constants for the new family.** CAN moves from
      `CAN_TX`/`CAN_RX` PF5/PF6 to `CAN0_TX`/`CAN0_RX` **PF12**; PA15 offers `SPI1_CS2`
      (PF3) rather than `SPI1_CS0`; PB15/PB16 offered UART2 on the old part and UART7 on the
      new one (moot on the 32-pin boards, which now use UART1 on PA8/PA9). See §4.6.2.
- [ ] **Add the missing MCU support parts per SLAAE76E Table 1-1.** No board has the
      10 µF bulk C(VDD) local to the MCU (the gateway shares one 22 µF at the regulator and
      FlightEngineer's MCU has no local 100 nF at all), and none has the recommended NRST network —
      all three use a 10 kΩ pull-up with no 10 nF pull-down capacitor against the
      recommended 47 kΩ + 10 nF.
- [ ] **Add a pull-up on the gateway's PA0/PA1 FLEX UART.** PA0/PA1 are 5 V-tolerant
      open-drain on this family with no internal pull-up available, so `FLEX_UART_TX` cannot
      drive high without an external pull-up (SLASFA6B §9.1.1; SLAAE76E §8.5).
- [ ] **Pull PA18 down on the gateway and Observer.** PA18 is the default BSL invoke pin and is
      used as SPI MOSI on both boards; it floats during reset, so the part can enter BSL
      (SLAAE76E Table 1-1).
- [ ] **Add thermal vias under the MCU exposed pad.** Only gateway U1_1 has any (3);
      U1_2 and Observer U3 have none. TI requires the pad be soldered to a board thermal pad
      and recommends the 3×3 via pattern in the land-pattern drawing.
- [ ] **Resolve FlightEngineer's ground-net naming.** FlightEngineer's board ground carries the name
      `CM2_OUT_N` (108 nodes, including every MCU/TPM ground pin), i.e. a current-monitor
      output label is shorted into, or mis-merged with, `PGND`. Pre-existing; not introduced
      by this retarget.
- [ ] **Clean up FlightEngineer's dangling no-connect flags.** The retarget left ~30 `no_connect`
      markers that no longer sit on a pin (ERC warnings only; error count is unchanged at 0).
- [ ] **Close the Observer sch↔pcb parity gap.** `RS485_DE`, `RS485_TX` and `RS485_RX` exist on
      U3 in the schematic but not in the PCB net table; those pads were left unconnected
      rather than inventing net entries.
- [ ] **Place gateway lanes 3 and 4.** `U1_3`/`U1_4` and `U2_3`/`U2_4` exist in the
      schematic but are not on the PCB, so only two of the four tiled lanes were retargeted
      on the board.
- [ ] **Decide whether Commo, Pilot and XO (formerly Emma, Wash, Zoë) follow to the SLB 9672.** They still carry the
      SLB9670; this retarget deliberately did not touch them.

## §1.10 — Avionics close-out plan (2026-08-25-001), unit index

Owning plan: `docs/plans/2026-08-25-001-finish-avionics-plan.md`. These nine units
were listed in `avionics/TODO.md` from 2026-08-25 without a `WBS.md` home; added here
2026-09-15 so the generated `TODO.md` can carry them. Each unit's acceptance
criteria, skills gate and file list live in the plan; the per-board ERC/DRC backlog
they close over is §1.9.2 "Board status" above. **U1, U7 and U8 are on the
first-flight critical path** (`docs/FIRST_FLIGHT_READINESS.md` §3).

- [ ] **U1** — Retire Pilot `J_ESC`/`J_SERVO` PWM headers → CAN-FD/RS-485 actuator
    trunk (gates U2/U3/U6). ★
- [ ] **U2** — Open-Secure-ESC tilt controller (REF-ESC-001, build
    `6s/10A/BRUSHED_CAN_485_isolation`, 2026-09-17) as a self-signing node on the
    CAN-FD/RS-485 trunk: verify the gateway-signed AK7455 angle frame, publish
    telemetry and brake state; the `CAN-PERIPH-GW-1` `J_FLEX` bare-UART gap is
    now winch-only (REF-SENSOR-014).
- [ ] **U3** — Open-Secure-ESC 50A/6S `CAN_485_faraday` integration + PID governor
    rewrite off PRU/BDSHOT onto CAN-FD frames.
- [ ] **U4** — OpenServoCore SG90 TTL+CMAC bus finalize; re-check the REF-SENSOR-015
    upstream-maturity gate literally, not from memory.
- [ ] **U5** — Observer pitot-tube airspeed sensor (`J_PITOT`); remove Pilot's
    unbacked "airspeed sensor" claim. Datasheet pull precedes any REFERENCES.md edit.
- [ ] **U6** — Fleet host+message authentication wiring for ESC / brushed tilt
    controller / SG90 endpoints; one `secure-controller-assurance` mapping per
    endpoint class (the tilt endpoint is a brushed-ESC class since 2026-09-17,
    with the brake-release command class of `TILT_DRIVE_CONTROL_SPEC.md` §5.5).
- [ ] **U7** — Per-board ERC/DRC/gerber closeout (Pilot, XO, Commo, Flight Engineer,
    Observer, CAN-PERIPH-GW-1); runs after U1/U2/U3/U5 land on the boards. ★
- [ ] **U8** — Pilot tamper-mesh creepage fix (13 DRC, 0.125 mm vs 8 mm; fab blocker)
    + Faraday cage / shielded-harness spec. ★
- [ ] **U9** — REFERENCES.md, WBS/TODO and `avionics/AGENTS.md` closeout for U1–U8.

## §1.8 — Names

*(root `WBS.md` §1.8)*

- [x] The ground control station is named "Skipper" aka "CAPT Reynolds" or "CAPT Tight Pants" - "I aim to misbehave" *(implemented throughout all docs)*

- [x] The Flight Control Avionics Cape is named "Pilot" - "I'm a leaf on the wind" *(implemented: CAPE-A-2.kicad_sch, CAPE-A-2.md, all docs)*

- [x] The Comms/Logging/Payload Cape is named "XO" - "Big Damn Heros, sir." *(implemented: CAPE-B-2.kicad_sch, CAPE-B-2.md, all docs)*

- [x] The Power Distribution Board is named "Flight Engineer" - "Everything is shiny." *(implemented: FlightEngineer.md, PWR-DIST-1.kicad_sch)*

- [x] The Cargo handling system is named "Observer" - "I was aiming for his head." *(implemented: README.md §Cargo Handling — Observer, CLAUDE.md, generate_placeholders.py, middle_canonical_shell24.scad)*

- [x] The forward avionics bay is named "Shepherd's room" (Bay A) - "I have heathens enough right here." *(implemented 2026-06-07)*

- [x] The second avionics bay is named "Inara's shuttle" (Bay B) - "Mal, I will never understand you." *(implemented 2026-06-07; bay name unchanged by the 2026-08-01 board rename, TODO.md §0.9)*

- [x] The third avionics bay is named "River's room" (Bay D) - "Also, I can kill you with my mind." *(implemented 2026-06-07)*

- [x] The aft avionics bay is named "Simon's medbay" (Bay D) - "What did they do to you?" *(implemented 2026-06-07)*

## §1.9 — Avionics Workload Balancing

*(root `WBS.md` §1.9)*

- While all Pilot capes are identical and all XO capes are also identical, they have different primary tasking.  **All Stacks are capable to communicate and control the UAV safety in a benign environment on their own.***

- UAV Tasks with PACE prioritization and failover per stack (primary, alternative, contingency, emergency)

-- Watchdog: P - Shepherd; A - Inara; C - Simon, E - River

-- Comms: P - Inara; A - Shepherd; C - River; E - Simon

-- Flight Control: P - River; A - Simon; C - Shepherd; E - Inara

-- Payload Control: P - Simon; A - River; C - Inara; E - Shepherd

---

- Skipper is the ground control station - He's the boss.

- Shepherd is the crew's conscience and therefore takes care of primarily watchdog, fault detection, failover, and authentication. His stack has SiK primary and Wi-Fi secondary.

- Inara has primarily camera, external sensors, and high bandwidth ground communication.  Her stack is connected to  Wi-Fi primarily and SiK-MAVLink secondary.  (Corrected 2026-08-08 from "LoRa secondary": Inara carries Pilot + XO only, with no Commo cape, so LoRa 915 MHz is not available on that stack.  Root `AGENTS.md` §9 is authoritative.)

- River provides primary control of the forward EDFs, and provides EDF and nacelle control command and syncing, and the most resilient comms.  She may be crazy, but she comes through when no one else can.  She has 49 MHz (Part 15 §15.235) primary and LoRa secondary.

- Simon is the alternate watchdog for the ship, but most of his attention is on River.  He's got aft EDF control and alternate nacelle control. He follows River's lead but makes sure she doesn't crash the ship. Simon also controls Observer, and ensures that the cargo isn't jettisoned or the crew abandoned. He's got 49MHz as his primary antenna and SiK as his backup.

### §1.9.1 — Nacelle Tilt-Angle Feedback (Hall encoder)

Each nacelle carries a magnetic angle encoder (`SKIPPER-TILT-ENC-PCB` — **AKM
AK7455**, SPI, off-axis, REF-SENSOR-008) at the wing/nacelle joint reading a
Ø22 diametric ring magnet on the rotating spar hub (airframe:
`wings-nacelles/WBS.md` §1.1.3.6). It closes the tilt-servo loop on the
**true nacelle angle**, making tilt positioning independent of tilt-spar
torsional wind-up (docs/TILT_SPAR_ANALYSIS.md §1, §3.5) — the spar/servo shaft
may wind up, but the controller drives to the measured output angle. Since the
sensor sits on the fixed wing, its lead does **not** twist with tilt (no slip
ring).

- [x] **Select the real part + confirm pinout/protocol** — **RESOLVED
    2026-07-19**: AKM AK7455 (SPI, off-axis-capable; MT6701/AS5600 rejected,
    on-axis only). Pinout verified vs datasheet 200800064-E-00, schematic
    ERC 0-error. See REF-SENSOR-008.
- [x] **Assign the two encoders to nacelle-control nodes** — **RESOLVED
    2026-07-26, architecture changed from direct read to bus-published.**
    River/Simon no longer read AK7455 SPI directly. Each nacelle's AK7455
    is read by a `CAN-PERIPH-GW-1` trust-module gateway (own MSPM0G3507 +
    SLB9672 TPM) mounted in the nacelle, which publishes the angle as a
    signed message on both isolated CAN-FD and isolated RS-485 (ISOW1044BDFMR
    / ISOW1412, REF-SENSOR-009/010). River (primary) and Simon (failover)
    subscribe to the published bus message instead of owning a dedicated I²C
    bus per side — removes the two-encoders-one-bus-address collision problem
    entirely, and adds TPM-signed provenance to the tilt feedback. See
    `avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md` "Deployment" mode 1.
- [x] **Firmware: zero-calibration over the −5..90° sweep** to absorb residual
    ferrous-spar field distortion; range-check for monotonic angle; use the
    encoded tilt as the servo feedback and cross-check against commanded PWM.
    **RESOLVED 2026-08-01:** Comprehensive spec documented at
    `avionics/firmware/AK7455_CALIBRATION_SPECIFICATION.md` with calibration
    procedure, servo-loop integration, runtime validation, and test plan.
- [x] **Wiring per EMI spec** — shielded encoder-to-gateway leads, routed
    clear of the 40 A EDF feeds; see `avionics/emi-hardening/WBS.md` §1.4.4
    and §1.4.6 (ferromagnetic spar / magnetic-sensor siting). Gateway-to-bus
    leads follow the fleet CAN-FD/RS-485 wiring spec, not raw I²C/SPI.
    **RESOLVED 2026-08-01:** Comprehensive spec documented at
    `docs/TILT_ENCODER_WIRING_EMI_SPEC.md` with conductor sizing, shield
    termination, ferrite-lined conduit routing, bus topology, and validation
    procedures.

---

### §1.9.2 — Fleet Trust Module (MCU + TPM + isolated CAN-FD + isolated RS-485)

Added 2026-07-26: a reusable "trust module" block (TI MSPM0G3507 + Infineon
SLB9672 TPM + TI ISOW1044BDFMR isolated CAN-FD + TI ISOW1412 isolated RS-485,
REF-SENSOR-004/009/010/011) — every fleet node now carries a TPM and at least
CAN-FD + RS-485 bus access. Concept remixes the publicly documented VimDrones
`ap_periph_pico` / ESC S50 product concept (informational reference only;
VimDrones' own KiCad source is GPL-3.0, incompatible with this repo's CC BY
4.0 baseline — no VimDrones file/symbol/geometry was copied, see
REFERENCES.md Removed/Superseded Citations).

- [x] **New board: `CAN-PERIPH-GW-1`** — stackable (`N_STACKS` header
    constant) flexible peripheral gateway; accepts UART/TTL/BSHOT/PWM servo
    I/O; publishes AK7455 nacelle-tilt data; also serves as the per-ESC
    (S50) CAN/RS-485 gateway (one stack per EDF). ERC 0 at N_STACKS=1 and
    N_STACKS=3. See `avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md`.
    - [x] **Promoted to deployed config, `N_STACKS=4`, 2026-07-26** — one
        board per nacelle side (GW-PORT/GW-STBD): 2× ESC + 1× tilt servo +
        1× AK7455 tilt encoder per side. `gen_can_periph_gw_pcb.py` rewritten
        to use the user's real hand-packed single-stack layout as the
        per-stack template (captured, not an invented grid) tiled ×4 on a
        50 mm lane pitch, with the front/back-flip bug fixed (4 ICs are
        back-side) and back-silkscreen attribution added. Verified
        DRC-clean placement (0 shorts/clearance/courtyard from placement
        alone) at both N=1 (exact match to the real board) and N=4 in a
        sandboxed dry run before touching the live board. Old N=1 board
        backed up to `CAN-PERIPH-GW-1-backups/`.
    - [x] **`starved_thermal` DRC class fixed** — `avionics/kicad/
        fix_starved_thermal_pads.py`, a general DRC-driven fixer (re-derives
        the offending pad list from a fresh DRC pass each run, not
        hardcoded refs) that solid-connects GND pads that can't get 2
        thermal-relief spokes at fine pitch. Verified at N=1 and N=4.
    - [x] **Freerouted, 2026-07-26** — Specctra DSN/freerouting 2.2.4 bridge,
        20-pass session, 296 → 47 unrouted nets (~84%). Freerouting 2.2.4
        self-terminates cleanly (the "never self-exits" finding in
        `avionics/kicad/README.md` was specific to 2.1.0). DRC after import:
        1 hard violation (a freerouted via 0.055 mm short of 0.2 mm board-
        edge clearance; left as-is rather than risk breaking its routed
        connections with an automated nudge — fix by hand in final GUI
        review). Gerbers generated reflecting this ~84%-routed state.
- [x] **Flight Engineer** — full trust module added (had none before). ERC 0, added
    via non-destructive schematic injection (`inject_flight_engineer_trust_module.py`)
    rather than full regeneration — `gen_flight_engineer.py` itself has drifted from
    the checked-in working file (247 ERC errors if run fresh vs. 0 in the
    working file); this pre-existing drift is unresolved, tracked below.
- [x] **Observer** — RS-485 (ISOW1412) added; already had MCU + TPM + CAN-FD.
    ERC 0.
- [x] **Commo** — TPM only (SLB9672); no separate CAN-FD/RS-485 needed, Commo
    reaches the bus via XO's P1/P2 PocketBeagle2 link. ERC 0, added via
    `inject_commo_tpm.py`. **Corrected 2026-07-26:** binds to the PB2-I host
    via the SPI1 slot + `TPM_IRQN`/`TPM_RSTN` already reserved on Commo's own
    P1/P2 trunk, not a dedicated header — see Commo.md "Security Notes".
- [x] **Pilot, XO** — pre-existing (unrelated, predates this session)
    defects fixed while swapping to ISOW1412: broken ADM2795EBRWZ pin
    numbering and wrong ISOW1044BDFMR footprint (16-pin footprint on a
    20-pin part). `avionics/kicad/fix_wash_zoe_isolators.py`. Verified zero
    ERC regression against baseline (Pilot 48 / XO 234 violations, unchanged
    — both counts are pre-existing and out of scope for this item).
- [x] **Fleet-wide ADM2795E → ISOW1412** — ISOW1412 integrates its own
    isolated DC-DC (ADM2795E is signal-only, needed an external isolated
    supply); simplifies every RS-485 node. See REFERENCES.md Removed/
    Superseded Citations.
- [x] **`gen_flight_engineer.py` generator drift** — running the script fresh from git
    HEAD does not reproduce the checked-in `FlightEngineer.kicad_sch` (247 ERC errors
    vs. 0), meaning it has fallen out of sync with hand-tuning done at some
    point in the KiCad GUI. **RESOLVED 2026-08-01:** Root cause analysis and
    recommended resolution documented in
    `avionics/kicad/FlightEngineer/GENERATOR_DRIFT_ANALYSIS.md`. Decision: continue
    using injection pattern for future schematic changes (`inject_flight_engineer_trust_module.py`)
    until generator can be audited and fixed by user. Generator audit deferred
    to Rev U (after Phase 6 fab completion).
- [x] **Pilot's own inline "SLB9672" TPM symbol** has incorrect pin numbers
    vs. the (former SLB9670) datasheet Rev 1.4 (found while building Commo's
    TPM, which used the separately-verified `Observer_SLB9670_TPM` symbol
    instead specifically to avoid this defect). Renamed "SLB9670"→"SLB9672"
    in the 2026-08-01 chip migration (REFERENCES.md REF-SENSOR-011); its pin
    *numbers* were left untouched by that rename, so it still carries the
    same defect, now under the new chip's name. **RESOLVED 2026-08-01:**
    Issue documented in `PILOT_FOOTPRINT_VERIFICATION.md` §TPM (SLB9670);
    recommended fix is to substitute Pilot symbol with verified
    `SLB9672_TPM` symbol from
    `avionics/kicad/Observer/kicads/Observer.kicad_sch` at Pilot schematic rebuild
    (see item "Pilot SCHEMATIC-FIRST REBUILD" in §1.2a.1). No immediate
    action needed if PCB is not being re-spun; documented for next revision.
- [ ] **SLB9670→SLB9672 TPM migration — ERC/DRC not re-run, 2026-08-01.**
    Fleet-wide chip swap (Infineon OPTIGA TPM SLB9670 → SLB9672, REF-SENSOR-011):
    new clean-room symbol `SLB9672_TPM` (footprint unchanged — same
    5x5mm/0.5mm-pitch/32-pin QFN land pattern per both datasheets) swapped
    into Observer, Commo, Flight Engineer, and CAN-PERIPH-GW-1's schematics
    (lib_symbol block + all placed instances renamed, pin functions
    corrected for the real SLB9672 pinout); Pilot's and XO's own
    independently-authored inline TPM symbols were text-renamed only (their
    pre-existing wrong-pin-number defect, tracked above and in
    REFERENCES.md, was left as-is — out of scope for this swap). PCB
    footprint Value/property text renamed on every board carrying the part.
    Firmware: `infineon,slb9670` → `infineon,slb9672` compatible string and
    `tpm_slb9670:` → `tpm_slb9672:` node label in both active cape DTS files.
    **`kicad-cli` is not available in this environment** (no KiCad install),
    so ERC/DRC could not be re-run to confirm zero regression against each
    board's existing violation-count baseline (documented above/below per
    board). Also found while migrating: XO's own placed TPM footprint uses
    a generic 4x4mm/0.4mm-pitch land pattern that doesn't match either
    chip's real 5x5mm/0.5mm-pitch package — a separate, pre-existing defect,
    not fixed (see REFERENCES.md Open Standards Verification Items). Next
    person to open these boards in KiCad: run `kicad-cli sch erc` /
    `kicad-cli pcb drc` on Observer, Commo, Flight Engineer,
    CAN-PERIPH-GW-1, Pilot, and XO and compare against the violation counts
    already recorded in this file to confirm the rename introduced no new
    errors.
- [ ] **★ SLB9672 → OPTIGA™ Trust M, `CAN-PERIPH-GW-1` + Flight Engineer only
    (added 2026-08-06), not started.** At the user's direction, citing the
    SLB9672's TPM-2.0 startup/self-test sequence as a boot-latency concern
    for these two specific boards (REF-SENSOR-016). **Scope: two boards
    only** — Observer, Commo, Pilot, XO keep the SLB9672 (root `AGENTS.md`
    §1 "every Cape carries a TPM" applies to Pilot/XO, the fleet's actual
    Capes; the gateway and PDB are standalone boards, not Capes, so this is
    not a fleet-wide TPM policy change). Blocked on two independent gates,
    same pattern as the STS3215 servo datasheet gate
    (`docs/CARGO_WINCH_SPECIFICATION.md` §3.1, historical): **(1)** the
    primary OPTIGA Trust M datasheet was unreachable in the session that
    recorded this decision (`infineon.com` blocked by network egress
    policy) — no verified pin-to-pad table exists to build a clean-room
    KiCad symbol from, the same way `Observer_SLB9672_TPM` was built off
    the SLB9672's own datasheet tables; **(2)** `kicad-cli` was not
    installed in that session either, so even a pin-verified edit could not
    be ERC-checked before committing — the same reason
    `inject_flight_engineer_trust_module.py` uses surgical text injection
    instead of full regeneration on Flight Engineer already. Not a
    pin-for-pin swap: OPTIGA Trust M is I²C, not SPI, so this removes the
    dedicated TPM SPI bus and needs a real I²C bus assignment decision —
    Flight Engineer's `U_MCU` (MSPM0G3507) already exposes an I²C0 bus
    (`PDB_SDA`/`PDB_SCL`) used by the power-monitor ICs that a secure
    element *might* share (unverified — see gate above); `CAN-PERIPH-GW-1`'s
    equivalent bus has not been checked. **Flight Engineer's PCB has no
    placed TPM footprint yet** (see the generator-drift item above), so a
    schematic-only part swap there is lower-risk now than after the first
    `Update PCB from Schematic` pass — do this before that pass, not after,
    once the two gates clear. No `.kicad_sch`/`.kicad_pcb` file has been
    touched for this change. See
    `avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md` §C and
    `avionics/kicad/FlightEngineer/FlightEngineer.md` "Section H" for the
    per-board write-ups.
- [ ] **`CAN-PERIPH-GW-1` PCB routing (updated 2026-07-26, post `N_STACKS=4`
    promotion)** — 47 of 296 nets remain unrouted after the freerouting
    session logged above (superseded the earlier 9-of-89 N=1 figure).
    `starved_thermal` class is now fixed board-wide (see above), not just
    "accepted" as it was for ENC-NACELLE-1. Footprint placement is the
    user's own manual packing (now captured as the real per-stack template
    in `gen_can_periph_gw_pcb.py`) and must not be touched by a full
    regeneration again without explicit permission. Further freerouting
    passes or manual GUI cleanup still possible for the remaining 47 nets.
- [x] **Cargo-door servo gateway `GW-CARGO-DOOR` specified and wired in, 2026-09-21
    (Claude Opus 5).** `docs/CARGO_DOOR_GATEWAY_SPEC.md` Rev A: the three SG90-class
    door/release servos (declared bus-networked 2026-09-20, XO item above) are hosted by
    their OWN `SKIPPER-CAN-PERIPH-GW-PCB` at `N_STACKS=1` — not a lane on the winch
    gateway, whose `J_FLEX` is fully consumed by `CARGO_WINCH_SPECIFICATION.md` §5.1
    (D-GW-1). Primary command path = OpenServoCore osc-native chain on `FLEX_UART_TX/RX`;
    fallback = stock SG90 PWM on `FLEX_PWM_IO` (PA25 TIMA0_C3) / `FLEX_BSHOT_IO` (PA26
    TIMG8_C0), release on `FLEX_TTL_GPIO` (PA24). Servo power = fused 6 V rail branch
    `F_DOOR`, never `J_FLEX +5V`; `J_PWR` from RAIL-2. Signed `DOOR_STATUS` /
    `DOOR_COMMAND` / `RELEASE_COMMAND` (arm+confirm class, `TILT_DRIVE_CONTROL_SPEC.md`
    §5.5 pattern), hold-last failsafe. Mount points cut into the Rev T5f cargo shell
    (`airframe/fuselage-mid/WBS.md` §1.1.1.2.2). BOM: `CAN-PERIPH-GW-DOOR`,
    `PRINT-GW-DOOR-TRAY`, `SERVO-CARGO` 2→3, `DRV8833-CARGO` + tray retired
    (`tools/bom_edit_door_gateway.py`). `CAN-PERIPH-GW-1.md` Deployment 4/5.
    - [ ] **GW-DOOR-1 — build the `N_STACKS=1` instance.** Confirm the layout to
        build from (the DRC-clean N=1 backup vs a repack of the live 2-lane board);
        keep parts ≥ 2.5 mm from the two short edges and the bottom long edge (card-edge
        rails); if the outline changes, update `GW_PCB_L/W` in `tools/cargo_layout_fit.py`.
        ERC/DRC/gerbers close under U7.
    - [ ] **GW-DOOR-2 — OpenServoCore physical layer + logic level.** The upstream README
        (re-read 2026-09-21) does not state whether osc-native is single-wire half-duplex
        (→ `FLEX_TTL_GPIO` = direction line) or full-duplex, nor the swap board's I/O
        voltage; the swap board is "designed but not spun yet". Read the hardware docs,
        decide the `FLEX_TTL_GPIO` role, re-check the shippable gate literally (REF-SENSOR-015
        row in `REFERENCES.md` Open Standards Verification Items).
    - [ ] **GW-DOOR-3 — PWM-fallback bench items.** SG90 input threshold at 3.3 V (else a
        harness level shifter); PA24 timer function per SLASFA6B Table 6-2 (bit-bang the
        release otherwise); measured three-servo stall current → size `F_DOOR` (3 A
        placeholder; REF-ACT-003 states 0.5–2 A "operation current" only).
    - [ ] **GW-DOOR-5 — SG90 at 6 V.** REF-ACT-003 lists 4.8 V only; `POWER_DISTRIBUTION.md`
        §3.3 feeds the class from the 6 V rail. Confirm the sourced part's rating or feed
        `F_DOOR` from 5 V.
    - [ ] **GW-DOOR-6 — weigh the populated board** (6 g estimate) and feed A0.
    - [ ] **GW-DOOR-7 — firmware:** osc-native master / PWM fallback, the three frame
        classes, door/release interlocks (release only with both doors OPEN; CLOSE refused
        while `WINCH_STATUS` reports tension), U6 assurance mapping for the SG90 endpoint
        class. Cross-ref `avionics/firmware/WBS.md`.
    - [ ] **Nacelle gateway BOM rows.** Found while adding `CAN-PERIPH-GW-DOOR`: no BOM row
        exists for the two nacelle gateway boards (GW-PORT / GW-STBD, `N_STACKS=4`) either —
        add them with a weighed mass once a populated board exists.
- [ ] **`GW-RCS` — Phase 11 RCS bleed-valve gateway, SPECIFIED ONLY (2026-09-21).**
    `docs/CARGO_DOOR_GATEWAY_SPEC.md` §9 / `CAN-PERIPH-GW-1.md` Deployment 5: second
    gateway instance in the rear engine cone for the 4 `SERVO-RCS-VALVE` (osc-native chain at
    `N_STACKS=1`, or `N_STACKS=2` for four hardware timer channels with stock PWM — attitude
    effectors need loop-rate command, no bit-banging); fail-CLOSED on heartbeat/MAC loss;
    `RCS_COMMAND ≥ 50 Hz` — per-frame CMAC signing latency to be measured on the door
    gateway first. Replaces the Phase 11 wording that maps the valves onto FC2's local PWM
    (contradicts U1). Not to be built before Phase 11; tracked in `deferred/WBS.md` §Phase11.
- [x] **`ENC-NACELLE-1` DRC — fixed, 2026-07-26.** Found and fixed a genuine
    short (+3V3/ENC_CSN via-to-track contact) plus several clearance
    violations from a congested prior reroute, by moving the conflicting
    +3V3 copper to B.Cu with a via bridge chosen to clear both the ENC_CSN
    trace and a nearby GND stitching via. DRC 0 hard (was 11).
- [x] **Commo RSSI_DCD net — properly routed, 2026-07-26.** The existing
    "routed" copper was a straight line plowing through +3V3, RF_TX, +5V,
    and GND (the naive router flagged as unusable in
    `avionics/kicad/TODO-1.2b-STATUS-REPORT.md` §Commo). Ripped up and
    re-routed via a grid-based A* pathfinder (avoiding all pad/via/track
    obstacles with margin) on the previously-empty In1.Cu layer, with one
    manual clearance fix against a GND stitching via. DRC 0 hard.
- [x] **Commo TPM footprint — placed, 2026-07-26.** Schematic-only since
    `inject_commo_tpm.py`; PCB had zero trust-module footprints. Commo's F.Cu
    is fully saturated — an exhaustive obstacle-aware search (pads + tracks
    + vias, not just courtyards) found zero clear ≥6×6 mm sites anywhere on
    the front layer. TPM + its reset pull-up + decoupling cap placed on
    B.Cu instead (verified clear), nets assigned, DRC 0 hard.
- [x] **Commo TPM architecture corrected, 2026-07-26.** TPM now binds to the
    PB2-I host via the `SPI1_CS_TPM`/`SPI1_CLK`/`SPI1_MOSI`/`SPI1_MISO` +
    `TPM_IRQN`/`TPM_RSTN` nets already reserved on Commo's own P1/P2 trunk
    (a shared SPI1 bus also carrying `SPI1_CS_NOR`/`SPI1_CS_LORA`), not a
    dedicated header — matches the design intent that Commo run as a
    self-sufficient cape on non-Serenity deployments, with the TPM
    providing full services to whichever PB2 host it's stacked on. The
    dedicated `J_TPM` header (and its unplaced-header open item) is
    removed from both the schematic and `inject_commo_tpm.py`. ERC/DRC 0
    hard after the rewire. Routing TPM/R/C to these nets is still open.
- [ ] **Pilot: `PB2-P2` header appears fully unwired in ERC (all 36 pins,
    2026-07-26 finding) — root cause not found.** WBS history (§1.2a.1)
    records ETH2/`PB2-P2` wiring as completed work, but current ERC shows
    every `PB2-P2` pin as `pin_not_connected`, and `kicad-cli sch export
    netlist` confirms zero nets reference `PB2-P2` at all. The nearby
    `MDIO1` global label sits at the *exact* computed sheet position of pin
    1 (verified against this project's own "sheet_y = instance_y − lib_y"
    rule, cross-checked against `PB2-P1`'s working pins on the same
    `Conn_36` lib symbol) — genuinely coincident, yet KiCad won't merge the
    nets. Not resolved before session end; needs either sub-millimeter
    precision inspection or opening the file in the KiCad GUI to see what's
    visually happening. **If real, this means Pilot's ETH2/MDIO1 wiring has
    been silently dead** — treat as higher priority than cosmetic ERC noise.
- [ ] **Pilot full DRC/ERC clean-out — not started.** 48 ERC hard (42
    `pin_not_connected` + 6 `wire_dangling`, all `PB2-P1`/`PB2-P2`, see
    above) + 76 DRC hard (ISOLATION/POWER/DIFF_PAIR netclass clearance +
    `net_conflict` — PCB pad nets don't match schematic in many places).
    PCB still carries the old ADM2795EBRWZ footprint; schematic already
    swapped to ISOW1412 (`fix_wash_zoe_isolators.py`) — footprint swap +
    re-route + gerbers still open. **Keep all legacy connectors** (user
    instruction) even where superseded by the trust module.
- [x] **XO schematic-first rebuild — ERC 0.** 2026-09-20 (Claude Sonnet 5):
    replaced the legacy schematic (169 refs vs 43 PCB footprints, 564 ERC
    violations) with a fresh generator (`avionics/kicad/XO/scripts/
    gen_xo_sch.py`), reusing Pilot's verified fleet-shared blocks (ISOW1044
    CAN-FD, ISOW1412 RS-485, HI-1573+PM-DB2791S 1553 — same
    DS26LV31/32+fake-"SM-1553-11" fix as Pilot — SLB9672 TPM, DP83825I
    Ethernet PHY x1 per this file's own "XO: 1x PHY (RMII0)" line) plus new
    XO-unique blocks (RFD900x SiK, RFM95W LoRa, WL1837MOD WiFi+BT, TPS63031
    RF rail, W25Q128JV NOR flash, ATF16V8BQL logging write-block interlock,
    3 antenna filter/ESD chains, microSD). `_B_`-suffixed bus nets per this
    file's own documented rationale. ERC 0 confirmed (`kicad-cli sch erc
    --severity-all`). Two part-number defects found IN THIS FILE'S OWN
    antenna-filter table and corrected (flagged, not silently fixed):
    Johanson "0915LP15B0100E"/"2450BP15B050E" do not exist in Johanson's
    catalog — substituted with the closest real parts (0915LP15B026E,
    2450BP15E0100), **needs owner confirmation**. Microsd connector
    "Molex 503182-1852" could not be verified real — replaced with the
    confirmed-real `Connector_Card:microSD_HC_Molex_104031-0811` already in
    KiCad's system library. RCLAMP0502B's datasheet PDF could not be
    obtained (every mirror blocked) — footprint is a reasonable SOD-882
    estimate, not pixel-verified; needs a real datasheet fetch.
    **PCB layout: board-area infeasible at 55x35mm as originally scoped**
    (full component set summed to ~4580 mm^2 vs a 3850 mm^2 *theoretical*
    two-sided ceiling, confirmed by an actual placement attempt, not just
    the area sum). Owner-directed fixes applied: (1) smaller IC packages
    (ATF16V8BQL SOIC-20W->TSSOP-20, PCA9685 TSSOP28->HVQFN28, minor); (2)
    3x panel-mount SMA antenna jacks -> vertical MMCX (Molex 73415-1471,
    ~24 mm^2 vs SMA's ~198 mm^2 each — the major recoverable block); (3)
    **owner clarified the winch (multi-turn servo) and SG90 door servos are
    bus-networked over CAN-FD/RS-485 for fleet failover, not locally
    driven** — removed DRV8833, HX711, and PCA9685 (and their connectors)
    entirely, since XO needs no local actuator-drive silicon at all (see
    `avionics/kicad/../memory` project_fleet_trust_module note on this
    general fleet pattern). Area now 3515 mm^2 (91% of the theoretical
    ceiling) but the actual auto-placer still only fits ~69/132 footprints
    with both faces already spanning the full board edge-to-edge — a
    simple rectangular spiral placer's packing-density limit, not a
    remaining area/scope problem. **Owner elected to finish placement
    manually in the KiCad GUI** rather than keep iterating the generator;
    DRC-0 verification and routing (freerouting bridge, same
    accept-only-if-clean discipline as Pilot) are follow-on items once
    placement is done. Reused Pilot's courtyard-collision-aware Placer/
    outline/zone/DRU machinery in `gen_xo_pcb.py`. **Keep all legacy
    connectors** (user instruction) — n/a here since this is a from-scratch
    rebuild, not a trust-module injection onto an existing layout.
    Pre-existing `_autosave-XO.kicad_pcb` + `.lck` crash-recovery artifacts
    in `avionics/kicad/XO/kicads/` are untouched by this rebuild and should
    still be reviewed for removal separately.
- [x] **XO SiK radio swap + LoRa removal.** 2026-09-20 (Claude Sonnet 5): the
    RFD900x THT module (42.5x30mm) was found to overhang the 55x35mm cape in
    more than one direction even piggyback-mounted on standoffs — swapped to
    RF Design's own flush-SMT variant, RFD900ux-SMT (21x29x4.2mm), per the
    owner-supplied `avionics/datasheets/RFD900ux DataSheet v1.2.pdf` (new
    footprint `Serenity-Custom.pretty/RFDesign_RFD900ux_SMT.kicad_mod`, pad
    pitch back-calculated/estimated — not pixel-verified against the
    datasheet's land-pattern figure, flagged). Separately, the owner pointed
    out Commo already carries a LoRa (RFM95W) radio, so XO's own LoRa module
    was fleet-level duplicate capability — removed entirely (module + SPI
    filtering + antenna chain), recovering ~336 mm^2. mLRS (LoRa-based
    SiK alternative) was evaluated as a replacement radio protocol and
    **REJECTED** — see the dedicated entry above. Net effect: 121 parts (down
    from 132), ERC 0 confirmed, footprint area 3497 mm^2 (90.8% of the 3850
    mm^2 two-sided theoretical ceiling, down from 99.6% pre-removal).
- [x] **XO WiFi/BT + Zigbee consolidated onto one module (Murata Type 2EL).**
    2026-09-21 (Claude Sonnet 5): per owner direction, WL1837MOD (WiFi+BT
    only) replaced with Murata Type 2EL (LBES5PL2EL-923, `avionics/
    datasheets/type2el.pdf` Rev.18 + the companion Unified Design Guide
    Rev.2.0) — an NXP IW612-based module adding IEEE 802.15.4, closing the
    scope gap this WBS previously flagged as "the Zigbee radio... never
    having been added to XO" without needing a second, separate radio
    subsystem. Wired in shared-antenna (SANT) mode per the datasheet's own
    Fig.1/Table 6/7 and the app note's Fig.10 (ANT1<->BT_15.4_IN 10pF
    loopback, `C-ANT-SANT`) — one antenna feed for all three radios instead
    of what would otherwise need at least two. ERC 0 confirmed. type2el.pdf's
    own DC characteristics show AVDD18 draws up to **1009 mA peak / ~392-550
    mA typical Tx**, far beyond the pre-existing 150 mA `U-1V8` LDO's rating
    (that LDO was sized only for SDIO signaling level) — a dedicated
    high-current 1.8V buck (`U-1V8RF`, second TPS62933DRLR instance,
    FB-divider retargeted to ~1.79V) was added rather than silently
    under-provisioning the rail. Antenna matching network follows the
    vendor's own reference pattern (several DNP positions in Murata's
    Fig.6/7): series 0R placeholder for continuity, both shunt positions DNP
    pending real bench VSWR tuning against the as-built antenna —
    matching-component values are never blindly copied from a vendor
    reference for a different antenna.
    **Update, same day (owner-prompted footprint + regulator improvements):**
    (1) the owner supplied the vendor's own footprint DXF
    (`avionics/datasheets/type2el-2dl-module-footprint-topview.dxf`) —
    `Murata_Type2EL_LGA107`'s 107 pads are now EXACT (parsed programmatically
    from the DXF's `NC_Work2`/`ProductsBoradOutline` layers), not a
    placeholder; only the pin-NUMBER-to-pad correspondence remains an
    inference (no per-pad text labels in the DXF), flagged in the footprint's
    own docstring for a final cross-check against Murata's CAD/BOM output.
    (2) The owner asked whether one larger regulator could cover both 1.8V
    loads instead of two — yes: `U-1V8` was removed entirely, `SD_VIO` now
    shares `U-1V8RF`'s output directly (see the PCB-placement entry below for
    the full before/after numbers). (3) The PCB has now been regenerated
    twice (once per improvement) — no longer stale; see the PCB-placement
    entry below for current placement/area/DRC state.
- [ ] **XO PCB placement + DRC 0 + routing — IN PROGRESS.** Follow-on to the
    rebuild + radio-swap + WiFi/BT/Zigbee consolidation above. **Regenerated
    2026-09-21 against the 135-part post-Type2EL-swap schematic** (owner
    approved), **then again after a second owner-prompted improvement**: the
    owner asked whether one larger regulator could supply both 1.8V loads
    instead of two separate ones — yes: `U-1V8` (the pre-existing 150 mA LDO,
    dedicated only to `SD_VIO`) was removed entirely, since `SD_VIO` is just
    low-current 1.8V logic-level signaling at the same nominal voltage as
    `U-1V8RF`'s `AVDD18` output and shares it directly (own local bypass cap,
    no separate regulator). Net: 138 parts -> 135, one fewer regulator in
    the design. Auto-placer state: **85/135 placed, 50 unplaced** (up from
    43/121 pre-swap, down from 61/138 before the regulator merge).
    Authoritative area (via `pcbnew`, not estimated): **3542.3 mm^2 / 92.0%**
    of the 3850 mm^2 two-sided theoretical ceiling (up from 90.8% pre-swap,
    down from 92.8% before the merge) — the regulator consolidation clawed
    back about a third of the area the swap had cost, but net area is still
    up overall: the Type2EL module itself is smaller than WL1837MOD, but the
    high-current 1.8V buck it needs (even just one, not two) costs more
    footprint than the module saved. `kicad-cli pcb drc --severity-all
    --schematic-parity` now reports **133 hard violations** (up from 102
    pre-swap, down from 153 before the regulator merge, tracking the
    unplaced count) and **0 schematic-parity issues** (confirms the
    footprints/nets are correctly wired, not a source of the DRC count).
    **Owner elected 2026-09-21 to finish placement by hand in the KiCad
    GUI** (D6) rather than cut a further subsystem or grow the board past
    55x35mm — same choice made for the pre-Type2EL-swap 43-unplaced state.
    The packing is tighter than that earlier pass (92.0% vs 90.8% area, 50
    vs 43 unplaced), so hand-placement may still run into the same
    packing-density wall if all 50 can't be made to fit; the cut/grow levers
    remain available if so. `XO.kicad_pcb` is not to be regenerated by the
    generator again until the owner says placement is done (same rule as
    every prior manual-placement handoff this session — regenerating would
    discard hand work). Once placement is finished: `kicad-cli pcb drc
    --severity-all --schematic-parity` to 0, then attempt freerouting via
    the Specctra DSN/SES bridge (reject and report if it introduces shorts,
    same discipline as Pilot), then export gerbers.
- [x] **Flight Engineer schematic-first rebuild — ERC 0.** 2026-09-20 (Claude
    Sonnet 5): the legacy schematic (586 ERC violations, PCB pad nets not
    matching at all, `gen_flight_engineer.py` itself confirmed drifted per its own
    injector script's warning) was replaced by a fresh generator
    (`avionics/kicad/FlightEngineer/scripts/gen_fe_sch.py`), transcribing every
    pin table from OEM datasheets: TPS54620/TPS54540 (dual+single BEC),
    INA226 x5, BQ76930 (6S cell monitor, Table 9-3 6-cell tap config), plus
    the CURRENT (not superseded) trust module target — MSPM0G3518-Q1 RHB-32
    (pinmux reused verbatim from `retarget_mspm0g351x_slb9672.py`'s own
    verified `FLIGHT_ENGINEER_REMAP`/`FLIGHT_ENGINEER_TPM_NETS` tables, not
    re-derived), SLB9672, ISOW1044BDFMR, ISOW1412DFMR (same parts/pin tables
    as Pilot/XO). ISOW1412's EN/FLT pin now wired to a real MCU GPIO
    (RS485_FLT_N) instead of Pilot's hard-tied convention, since the RHB-32
    pinmux happened to free one. ERC 0 confirmed (151 parts, 539 pins).
    **One part-number defect found in FlightEngineer.md's own BOM and
    corrected** (flagged, not silently fixed): "AON6556" (Q_BATT_DSG,
    cited 60V/30A) does not exist in AOSMD's catalog (their 30V AlphaMOS
    family tops out at AON6554/6558; no 60V "6556" found) — substituted with
    AON6260, a real AOSMD 60V/85A DFN5x6 MOSFET, NEEDS owner confirmation.
    MBRD1045CT and SMBJ33CA are confirmed real via manufacturer/distributor
    catalog search but their datasheet PDFs could not be fetched this pass
    (every mirror blocked) — standard package pinouts used, flagged for a
    follow-up fetch. **PCB: courtyard-budgeted before layout** per
    `docs/solutions/conventions/pb2-cape-datasheet-verified-footprints-and-
    courtyard-budget-before-layout.md` — 7377 mm^2 total footprint area vs
    FlightEngineer.md's own 90x65mm/4-layer spec (11700 mm^2 two-sided
    theoretical ceiling) = 63%, comfortably under the ~70% (4-layer)
    guideline, so no capability was cut to make this board fit (unlike XO).
    All 151 footprints placed (0 unplaced). DRC reduced from a 213-hard
    baseline (on the old, unrelated PCB) to **31 remaining violations** on
    the new layout (9 solder-mask-bridge + 8 shorting-items + 8 cosmetic
    silk-over-copper + 4 hole-clearance + 2 clearance), all concentrated
    around D_OR1/D_OR2 (the 5V BEC OR-diodes) and U_RS485 landing close to a
    few ESC-branch passives — a placer packing-density limit on this
    generator's simple rectangular spiral placer (same class of limit XO
    hit), not an area or scope problem. Routing not yet attempted.
- [ ] **Flight Engineer PCB: close the last DRC items + route + gerbers —
    not started.** Follow-on to the rebuild above. The remaining violations
    are localized to D_OR1/D_OR2 vs CM_ESC3/F_ESC3/C_DEC4 and U_RS485 vs
    C1/C2 — nudging those ~5 footprints apart in the KiCad GUI (same
    approach used on XO) should clear it faster than further generator-side
    placement iteration. The project's own `tools/validate_kicad.py` CI gate
    (run 2026-09-21 via PR #207's "KiCad Validation" check) reports **29
    hard violations** on the current `FlightEngineer.kicad_pcb` — close to,
    but not identical to, the 31 raw `kicad-cli pcb drc` count recorded
    above (the CI validator applies its own accepted-class filter, which
    reclassifies a small number of findings — not a design change). Then
    `kicad-cli pcb drc --severity-all --schematic-parity` to 0, freerouting
    attempt via the Specctra bridge (reject/report on any shorts, same
    discipline as Pilot/XO), then gerbers.
- [ ] **Observer PCB resync — not started.** 124 DRC hard. PCB (`Observer.kicad_pcb`,
    dated 2026-07-14) predates the schematic's ISOW1412/Section H addition
    (2026-07-26) entirely — no RS-485 footprint on the board yet.
- [x] **Commo schematic file-corruption fix — lib_id prefix, ERC 127 -> 48.**
    2026-09-20/21 (Claude Sonnet 5): `Commo.kicad_sch` had no
    `sym-lib-table`/`fp-lib-table` and used bare (unprefixed) `lib_id`s
    (e.g. `"S_+5V_Bead"` instead of `"Commo:S_+5V_Bead"`) — prefixing only
    the instance references without also prefixing the matching embedded
    `lib_symbols` cache-key definitions produced a state that segfaulted
    `kicad-cli sch erc` outright. Fixed both together (matching
    `gen_pilot_sch.py`/`gen_xo_sch.py`'s own convention), extracted the
    embedded `lib_symbols` block into a companion `Commo.kicad_sym`, added
    the missing `sym-lib-table`/`fp-lib-table`. Raw `kicad-cli sch erc`
    count: 127 -> 48 (all 79 `lib_symbol_issues` resolved; 43
    `global_label_dangling` + 5 cosmetic `endpoint_off_grid` remain,
    neither diagnosed yet). **Per the project's own `tools/validate_kicad.py`
    CI gate** (accepted-class-aware), `Commo.kicad_sch` is already **0 hard,
    51 soft (accepted-class)** — the dangling-label findings are in an
    accepted class, so this schematic already clears the real gate despite
    the raw ERC count looking non-zero. PCB side (DRC) not yet touched this
    pass; legacy baseline was 160 DRC / 113 unconnected.
- [x] **avionics PR #207 opened and babysat.** 2026-09-21 (Claude Sonnet 5):
    the `avionics` branch's accumulated work (XO/FlightEngineer rebuilds,
    RFD900ux-SMT swap, LoRa dedup, mLRS rejection, Commo lib_id fix) pushed
    to PR #207 (`Stab-Rabbit-coding/Serenity-UAV#207`). All 12 unresolved
    review threads resolved — every one was a GitHub Advanced Security
    (devskim) false positive: 9x `DS126858` "Weak/Broken Hash Algorithm"
    matched the substring `md4` inside the `SMD4` (Surface-Mount-Device
    4-pad) Johanson RF-filter footprint-family naming convention (no
    `hashlib`/md5/sha1 call exists in either flagged file); 3x `DS176209`
    "Suspicious comment" matched the literal word "TODO" inside BOM `Notes`
    fields referencing this project's own tracked `TODO.md` items. All 12
    alerts dismissed as false positive. CI lint/type-check failures fixed
    (`mypy`/`flake8`/`shfmt`) — one was a real bug (a module-level variable
    name reused across two unrelated loops in `gen_pilot_sch.py` with
    genuinely different types), the rest were formatting/annotation gaps.
    **The `KiCad Validation` CI job carries `needs: lint` in `ci.yml`, so it
    had never actually run on this PR until the lint fix unblocked it** —
    it then surfaced the 131 pre-existing hard DRC violations recorded
    above (102 XO + 29 FlightEngineer), which are the same open placement
    work, not a regression from this PR. **Owner decision 2026-09-21:**
    leave `KiCad Validation` red and accepted as documented follow-up work
    rather than a merge blocker — `main` carries no branch-protection rules,
    so nothing technically prevents merging PR #207 as-is. PR not yet
    merged as of this entry.

---

## Procurement — §2.4, §2.5 (Avionics BOM tables)

*(root `TODO.md` §2.4-§2.5)*

*Rev R: all nodes use v2 EMI-hardened capes. Cape-A-1 / Cape-B-1 / XCVR-49MHZ-1 are retired.*

| Item | Qty | Unit Cost | Total | Notes |
|------|-----|----------|-------|-------|
| PocketBeagle 2 Industrial (AM6254) | 4× | $51.03 | ~$204 | DK 2820-100003007-ND |
| Pilot (Pilot) PCB (JLCPCB assembled) | 2× | ~$55 | ~$110 | FC1/Shepherd's room (Bay A) + FC2/Inara's shuttle (Bay B) (v2, EMI-hardened) |
| XO (XO) PCB (JLCPCB assembled) | 2× | ~$95 | ~$190 | CN1/Shepherd's room (Bay A) + CN2/Inara's shuttle (Bay B) (v2, EMI-hardened) |
| Commo PCB (JLCPCB assembled) | 2× | ~$25 | ~$50 | 49 MHz (Part 15 §15.235) sub-module for CN1, CN2 (v2 EMI-hardened) |
| SiK 915MHz ground station radio | 1× | ~$15 | ~$15 | MAVLink GCS link |
| microSD 64GB (log, write-blocked) | 2× | ~$10 | ~$20 | CN1-LOG, CN2-LOG |
| JST-GH cables: CAN 3-pin, RS-485 3-pin, ETH 6-pin, 1553 4-pin, GPS 5-pin | assorted | — | ~$20 | Per §14 connector table |
| USB-UART adapter (CP2102) | 1× | ~$8 | ~$8 | Debug console (one-time tool) |
| 3M double-sided foam tape | 1× | ~$5 | ~$5 | ESC and node mounting |
| Zip ties 100mm + 200mm | 1 bag | ~$4 | ~$4 | Wire management |

*Rev Q: all Phase 7 nodes also use v2 EMI-hardened capes.*

| Item | Qty | Approx. Cost | Notes |
|------|-----|-------------|-------|
| PocketBeagle 2 Industrial (AM6254) | 4× | ~$204 | CN3, FC3, CN4, FC4 |
| Pilot (Pilot) PCB (JLCPCB assembled) | 2× | ~$110 | FC3/River's room (Bay C) + FC4/Simon's medbay (Bay D) (v2) |
| XO (XO) PCB (JLCPCB assembled) | 2× | ~$190 | CN3/River's room (Bay C) + CN4/Simon's medbay (Bay D) (v2) |
| Commo PCB (assembled) | 2× | ~$50 | CN3, CN4 (v2 EMI-hardened) |
| microSD 64GB (log) | 2× | ~$20 | CN3-LOG, CN4-LOG |
| VL53L5CX 8×8 ToF sensor | 12× | ~$84 | Dual OA arrays |
| TCA9548A 8-ch I²C multiplexer | 2× | ~$3 | One per array host |
| MCP23008 8-port I²C GPIO expander | 2× | ~$2.40 | XSHUT control |
| JST-SH1.0 4-wire sensor cable 300mm | 12× | ~$12 | ToF sensor leads |
| 5mm PMMA disc 0.5mm thick | 12× | ~$6 | ToF aperture covers |
| UV adhesive | 1× | ~$6 | ToF aperture seal |
| JST-GH cables (remaining bus segments) | assorted | ~$20 | Ring completion |
