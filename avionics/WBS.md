# Serenity UAV — Avionics (Pilot / XO / Commo Cape Hardware) Work Breakdown Structure (Detail)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0
**Current design revision:** Rev S (2026-07-04)

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
    signal pin labelled); CAN-FD → CAN_H/CAN_L; RS-485 → RS485_A/B; PWR-IN → +5V/GND.
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
- [ ] **Generate Pilot gerbers** — `CAPE-A-2.kicad_pcb` complete; run DRC to zero errors in
    KiCad; export to `avionics/kicad/gerbers/CAPE-A-2/`; re-export drill files.
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

- [ ] **Pilot footprint-vs-datasheet verification — DONE 2026-07-13 (Claude Opus 4.8);
    7 footprints are NOT manufacturable, must be rebuilt before fab.** Full report:
    `avionics/kicad/Pilot/WASH_FOOTPRINT_VERIFICATION.md`. Fixing any of these remaps
    pin→net on flight hardware, so each needs the confirmed schematic pinout first (ERC
    is not clean — see below) and MUST NOT be guessed.
    - [ ] **CAN-TR (ISOW1044BDFMR): wrong land — has 16-pad `SOIC-16W`, part is a
        20-pin DFM (SOIC-20 land).** Datasheet `isow1044.pdf` §7 / Fig 7-1. (This is the
        fleet-wide ISOW1044 footprint error; confirmed present on Pilot.)
    - [ ] **TPM (SLB9670): wrong land — has `QFN-32 4×4 P0.4mm EP2.65`, part is VQFN-32
        0.5 mm pitch, ~5×5 body, EP 3.6×3.6.** Datasheet `SLB_9670VQ20_Infineon.pdf` p.15.
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
        **CAN-TR (ISOW1044, 20-pin), RS485 (ADM2795E, 16-pin RW-16), TPM (SLB9670, 32-pin
        correct 17–24 SPI map), GPS (SAM-M10Q, 16-pin).**
    - [ ] Author ETH section on **ADIN1300** (40-LFCSP) + Würth 749010012A magnetics +
        ISO6442 — redesign the RMII isolation (current scheme shorts the barrier / 50 MHz
        REF_CLK through a digital isolator is unworkable).
    - [ ] Add remaining ICs: 1553 (DS26LV31/32 + SM1553 xfmr), IMU (ICM-42688-P), baro
        (BMP388, 10-pin), compass (MMC5983MA/QMC5883L), INA226, PCA9555, 74LVC1G14.
    - [ ] Add PB2-P1/P2 (2×36) SoC headers + connectors + passives (TVS/CMC/X2Y-Syfer-0805/
        Nano-Fit); tie the off-sheet global labels; drive GND/power (PWR_FLAG) to clear ERC.
    - [ ] Associate corrected footprints (per WASH_FOOTPRINT_VERIFICATION.md) to each symbol;
        regenerate/re-sync the PCB; ERC + DRC --schematic-parity to zero.
    - [ ] Once approved, promote `Wash_rebuild.kicad_sch` → `Pilot.kicad_sch` (archive old).
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

- [x] The aft avionics bay is named "Simon's medbay" (Bay E) - "What did they do to you?" *(implemented 2026-06-07)*

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

- Inara has primarily camera, external sensors, and high bandwidth ground communication.  Her stack is connected to  Wi-Fi primarily and LoRa secondary.

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
    SLB9670 TPM) mounted in the nacelle, which publishes the angle as a
    signed message on both isolated CAN-FD and isolated RS-485 (ISOW1044BDFMR
    / ISOW1412, REF-SENSOR-009/010). River (primary) and Simon (failover)
    subscribe to the published bus message instead of owning a dedicated I²C
    bus per side — removes the two-encoders-one-bus-address collision problem
    entirely, and adds TPM-signed provenance to the tilt feedback. See
    `avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md` "Deployment" mode 1.
- [ ] **Firmware: zero-calibration over the −5..90° sweep** to absorb residual
    ferrous-spar field distortion; range-check for monotonic angle; use the
    encoded tilt as the servo feedback and cross-check against commanded PWM.
- [ ] **Wiring per EMI spec** — shielded encoder-to-gateway leads, routed
    clear of the 40 A EDF feeds; see `avionics/emi-hardening/WBS.md` §1.4.4
    and §1.4.6 (ferromagnetic spar / magnetic-sensor siting). Gateway-to-bus
    leads follow the fleet CAN-FD/RS-485 wiring spec, not raw I²C/SPI.

---

### §1.9.2 — Fleet Trust Module (MCU + TPM + isolated CAN-FD + isolated RS-485)

Added 2026-07-26: a reusable "trust module" block (TI MSPM0G3507 + Infineon
SLB9670 TPM + TI ISOW1044BDFMR isolated CAN-FD + TI ISOW1412 isolated RS-485,
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
- [x] **Commo** — TPM only (SLB9670); no separate CAN-FD/RS-485 needed, Commo
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
- [ ] **`gen_flight_engineer.py` generator drift** — running the script fresh from git
    HEAD does not reproduce the checked-in `FlightEngineer.kicad_sch` (247 ERC errors
    vs. 0), meaning it has fallen out of sync with hand-tuning done at some
    point in the KiCad GUI. Needs reconciliation before it can be trusted for
    future regeneration; until then, changes to Flight Engineer's schematic must use
    the injection pattern (see `inject_flight_engineer_trust_module.py`).
- [ ] **Pilot's own inline "SLB9670" TPM symbol** has incorrect pin numbers
    vs. datasheet Rev 1.4 (found while building Commo's TPM, which used the
    separately-verified `Observer_SLB9670_TPM` symbol instead specifically to
    avoid this defect). Not fixed — out of scope for this item. See
    REFERENCES.md Open Standards Verification Items.
- [ ] **`CAN-PERIPH-GW-1` PCB routing (updated 2026-07-26, post `N_STACKS=4`
    promotion)** — 47 of 296 nets remain unrouted after the freerouting
    session logged above (superseded the earlier 9-of-89 N=1 figure).
    `starved_thermal` class is now fixed board-wide (see above), not just
    "accepted" as it was for ENC-NACELLE-1. Footprint placement is the
    user's own manual packing (now captured as the real per-stack template
    in `gen_can_periph_gw_pcb.py`) and must not be touched by a full
    regeneration again without explicit permission. Further freerouting
    passes or manual GUI cleanup still possible for the remaining 47 nets.
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
- [ ] **XO full DRC/ERC clean-out — not started.** 219 ERC hard (206
    `pin_not_connected`, mirrors the CAN-TR/ISOW1044 VCC1/GND1/RXD/VCC2 pins
    genuinely unconnected in the schematic, plus LoRa/other pre-existing
    gaps) + 154 DRC hard. Same ADM2795E→ISOW1412 PCB footprint swap needed
    as Pilot. A stray `_autosave-XO.kicad_pcb` + `.lck` files are
    git-tracked in `avionics/kicad/XO/kicads/` — the autosave file appears
    to be an accidental commit of a KiCad crash-recovery artifact (578 hard
    DRC violations on its own, clearly not real design intent) and should
    be reviewed for removal. **Keep all legacy connectors** (user
    instruction).
- [ ] **Flight Engineer full PCB resync — not started.** 213 DRC hard, almost all
    `net_conflict` (PCB pad nets don't match the schematic at all — the
    injected trust module and other schematic changes never propagated to
    layout; compounds the pre-existing `gen_flight_engineer.py` drift above). No
    trust-module footprints exist on the PCB yet. Largest remaining board
    task — needs a real `Update PCB from Schematic` pass plus manual net
    cleanup, not just footprint addition.
- [ ] **Observer PCB resync — not started.** 124 DRC hard. PCB (`Observer.kicad_pcb`,
    dated 2026-07-14) predates the schematic's ISOW1412/Section H addition
    (2026-07-26) entirely — no RS-485 footprint on the board yet.

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
| Pilot (Pilot) PCB (JLCPCB assembled) | 2× | ~$110 | FC3/River's room (Bay D) + FC4/Simon's medbay (Bay E) (v2) |
| XO (XO) PCB (JLCPCB assembled) | 2× | ~$190 | CN3/River's room (Bay D) + CN4/Simon's medbay (Bay E) (v2) |
| Commo PCB (assembled) | 2× | ~$50 | CN3, CN4 (v2 EMI-hardened) |
| microSD 64GB (log) | 2× | ~$20 | CN3-LOG, CN4-LOG |
| VL53L5CX 8×8 ToF sensor | 12× | ~$84 | Dual OA arrays |
| TCA9548A 8-ch I²C multiplexer | 2× | ~$3 | One per array host |
| MCP23008 8-port I²C GPIO expander | 2× | ~$2.40 | XSHUT control |
| JST-SH1.0 4-wire sensor cable 300mm | 12× | ~$12 | ToF sensor leads |
| 5mm PMMA disc 0.5mm thick | 12× | ~$6 | ToF aperture covers |
| UV adhesive | 1× | ~$6 | ToF aperture seal |
| JST-GH cables (remaining bus segments) | assorted | ~$20 | Ring completion |
