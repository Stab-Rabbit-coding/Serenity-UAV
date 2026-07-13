# Vera — Manufacturing-Readiness Gap Analysis

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**AI-assist:** Claude Opus 4.8 (Anthropic) — gap analysis, 2026-07-06
**License:** CC BY 4.0
**Revision:** Rev B (2026-07-06)
**Status:** Analysis + recommended resolution — the raw-SoC gap, and the SoM-carrier path
that closes most of it.

**Changelog:**

- **Rev C (2026-07-11):** Module + form factor **locked** (user): **PHYTEC phyCORE-AM62A**
  (40×40 mm, 270-pin 0.8 mm direct-solder) on a **trapezoidal carrier** — narrow end (≤ 1.0 in)
  toward the sensor pod, widening aft to seat the 40 mm module, conforming to the nose cone.
  Added the verified module spec, the carrier interface/net map (§3B, the schematic plan), and
  the pinout datasheet gate. See §1.1, §3A, §3B.
- **Rev B (2026-07-06):** Added the recommended resolution — mount the AM62A on a vendor
  **system-on-module (SoM)** and rebuild Vera as a **carrier board**, which eliminates the
  LPDDR4/boot-flash/power-sequencing/DDR-BGA gaps (G1/G2/G4 and most of G6). Re-scoped the
  staged plan around the SoM-carrier path with the raw-SoC design retained as the alternative.
- **Rev A (2026-07-06):** Initial gap analysis (raw-SoC design).

---

## 1. Bottom line

Vera is a **partial architectural sketch, not a fabricable board.** The peripheral/glue
circuitry (connectors, Ethernet magnetics, EMI, isolated CAN, crystal, laser driver, passives)
uses **real, verifiable footprints**, but the design cannot be brought to manufacturing by an
automated placeholder-swap because:

1. **All five main ICs are placeholder footprints** with **placeholder pin/ball numbering** — a
   real board needs datasheet-verified land patterns *and* pin↔net maps. Per the project
   no-fabrication rule (`CLAUDE.md`), these **cannot be invented**; they must come from the
   vendor datasheets.
2. **The entire memory subsystem is missing.** The **TI AM62A7 has no usable internal RAM for
   Linux — it requires external LPDDR4** — and the schematic contains **no LPDDR4 and no boot
   flash/eMMC.** Without them the SoC cannot boot. This is a *subsystem* to design, not a detail.
3. **AM62A7 + LPDDR4 is impedance-controlled BGA/DDR layout** — expert manual routing (length/
   impedance-matched byte lanes, BGA escape, reference planes), not something a script can
   generate correctly.

So "get it ready for manufacturing" is a **multi-stage hardware effort gated on the SoC+memory
subsystem**, not a one-shot automation. What *can* be automated (the pre-commit corruption
guard, `tools/precommit_kicad_load.py`) is done.

## 1.1 Recommended resolution — put the AM62A on a SoM; make Vera a carrier

The root of every blocker is that Vera tries to host a **raw Linux applications SoC** (AM62A7)
and therefore *owns* the LPDDR4, boot flash, power sequencing, and impedance-controlled DDR/BGA
routing. **The simplest, most reliable fix is not to own any of that:** mount the AM62A on a
vendor **system-on-module (SoM)** where the SoC + LPDDR4 + boot flash + PMIC are already
integrated **and validated by the vendor**, and rebuild Vera as a **carrier board** carrying
only the parts it already has as real footprints (KSZ9477 switch, ISOW1044 CAN, SLB9670 TPM,
Ethernet magnetics/EMI, laser driver, camera/ToF connectors) plus the SoM's board-to-board
connector.

This **eliminates G1, G2, G4 and most of G6** — they move onto the module — and drops Vera from
a 6-layer impedance-controlled DDR/BGA design to an **ordinary ~4-layer carrier**. It also
matches the project's existing pattern: the whole fleet already runs on **PocketBeagle 2
Industrial** compute modules on capes; raw-SoC Vera was the outlier.

**Verified this session (2026-07-06):** TI's own SK-AM62A-LP EVM confirms the AM62A7 (AM62A74,
quad-A53) pairs with **external 4 GB LPDDR4** and provides **4-lane MIPI CSI-2** + **dual
gigabit Ethernet** — i.e. the memory really is external (the gap is real) and the camera/Ethernet
Vera needs are native to the part. **Module + form factor LOCKED (2026-07-11, user):** no AM62A SoM fits a 1.0 in-wide board
(narrowest ~30 mm OSM; mainstream 40 mm), so Vera becomes a **trapezoidal carrier** conforming
to the nose cone — **narrow end ≤ 1.0 in toward the sensor pod** (camera/ToF/laser), **widening
aft to seat the module**. Selected module: **PHYTEC phyCORE-AM62A** (see §3A for verified spec).

**The one remaining datasheet gate is the module PIN MAP:** the phyCORE-AM62A 270-pad
assignment lives only in the PHYTEC Hardware Manual PDF, which is **blocked in this build
environment** (phytec.com + snapeda.com denied by a PermissionRequest hook; phytec.eu exposes
the interface list but not the pad table). The SoM schematic **symbol cannot be authored without
it** — fabricating 270 pad numbers is barred by the no-fabrication rule. Unblock path in §3B.

The raw-SoC gap analysis (§2–§6) is retained below because it defines what the SoM buys us and
remains the fallback if the phyCORE-AM62A is disqualified on fit.

---

## 2. Current footprint state

| Class | Refs | Footprint status |
|---|---|---|
| **Real / verifiable** | T1/T2 (749010012A), J_ETH_IN/OUT, J_CANFD, J_PWR, J_TOF, J_CAM1/2, J_LASER, U4 (ISOW1044 SOIC-16W), CMC1-5, D1-5, Q1, Y1, R1/R2, C_MCU1, H1-4 | OK (see §5 for two minor fixes) |
| **Placeholder — needs datasheet** | **U1 AM62A7** (BGA-484), **U2 KSZ9477** (QFN-128), **U3 MSPM0G3507** (VSSOP-28), **U5 SLB9670** (VQFN-32), **U_PMIC TPS65219** (VQFN-32) | Land pattern *and* pin map both placeholder |
| **MISSING entirely** | LPDDR4 DRAM, boot flash (eMMC/OSPI NOR), DDR termination, full PMIC power-sequencing net, SoC PLL/loop-filter passives | Not in schematic |

---

## 3. Critical gaps (in priority order) — under the raw-SoC path

*(G1, G2, G4 and most of G6 are **eliminated** by the §1.1 / §3A SoM-carrier path — they move
onto the module. They are documented here as what the SoM buys us, and as the fallback scope if
no AM62A SoM qualifies.)*

**G1 — LPDDR4 memory (blocker).** AM62A7 needs external LPDDR4. Add a **1–2 GB LPDDR4** device
(single x16/x32 package, ~200-ball FBGA — e.g. a Micron/Nanya part *to be selected against a
datasheet*), its decoupling, and **impedance/length-matched DDR routing** to the AM62A7 DDR
pins. This is the single largest piece of work and drives the layer stack-up and board area.

**G2 — Boot media (blocker).** Add **eMMC** (a BGA-153, e.g. Kingston/Micron) *or* **OSPI NOR
flash** (a small SOIC/USON) as boot media, per the AM62A7 boot-mode strapping. (An SD-card slot
is an alternative but is bulkier and less reliable for flight.)

**G3 — Datasheet-verified footprints + pin maps** for U1/U2/U3/U5/U_PMIC. The land patterns for
the *standard* packages (VSSOP-28, VQFN-32, QFN-128) exist in KiCad's `Package_*` libraries, but
swapping them is pointless until the **pin↔net map** is corrected from each datasheet (the
current maps are placeholder sequences). The AM62A7 484-ball map is a datasheet transcription
job on its own.

**G4 — Power sequencing.** TPS65219 → AM62A7 rail order/timing per TI SLVAFD0; add the
enable/PGOOD nets and sequencing so the rails come up in the required order.

**G5 — Full MIPI CSI-2.** Only 1 of 4 CSI data lanes is modeled; a real camera needs all 4
(plus CLK) as length-matched differential pairs.

**G6 — Routing.** After G1–G5: BGA escape, DDR byte-lane matching, RGMII/MDIO to KSZ9477,
CSI-2 pairs, Ethernet magnetics pairs — all impedance-controlled on a defined stack-up, then
gerbers + fab notes. **Expert manual layout; not auto-routable to fab quality.**

---

## 3A. SoM-carrier architecture (recommended)

Vera becomes a **carrier** for an AM62A SoM. What lives where:

**On the module (bought, pre-validated — deletes G1/G2/G4 + DDR/BGA routing):**

- AM62A7 (AM62A74) SoC, LPDDR4 (target ≥ 2 GB; TI EVM ships 4 GB), boot flash (eMMC/OSPI),
  PMIC + full power sequencing, SoC decoupling, main oscillator.

**On the Vera carrier (mostly parts already footprinted — ordinary ~4-layer routing):**

- **SoM board-to-board connector(s)** — the one new footprint; its exact P/N + pitch + pin count
  come from the selected module's carrier-design guide (datasheet-gated, §3A selection below).
- **KSZ9477** Ethernet switch (HSR/PRP ring) — RGMII/MDIO from the SoM.
- **ISOW1044** isolated CAN-FD, **SLB9670** TPM (SPI from SoM), **MSPM0G3507** CAN-FD
  coprocessor (as today).
- Ethernet magnetics + SRF2012 CMC + PRTR5V0U2X TVS (EMI, as today).
- Camera **MIPI CSI-2** route from the SoM to the camera connector / direct-solder land (§4);
  ToF UART; laser driver (Q1 + current limit).
- 5 V input; the SoM's own rails feed the SoC — the carrier only supplies what the module's
  design guide requires (typically a single 5 V or 3.3 V in).

**§3A selection criteria (the one datasheet-gated decision):**

1. **AM62A** vision variant (VPAC/ISP + H.264/H.265 encode) — *not* plain AM62/AM62P.
2. Breaks out **≥ 1 MIPI CSI-2 (4-lane)**, **RGMII** (for KSZ9477), and enough **SPI/UART/CAN**.
3. **Connector stack height + module footprint** fit the nose pod's Z-budget and Vera's
   1.0 in width (verify against `airframe/openscad/fuselage/bow_sensor_pod.scad`).
4. Documented **carrier design guide + reference schematic** and current production status.

**Selected module (2026-07-11): PHYTEC phyCORE-AM62A.** Verified spec (TI partner page +
phytec.eu, 2026-07-11):

- **SoC:** AM62A7 (AM62A74, quad-A53) + 2 TOPS C7x DSP; H.264/H.265 encode/decode to 4K30.
- **On-module memory:** 4 GB LPDDR4, 128 GB eMMC, 256 MB OSPI NOR, 4 KB EEPROM — **boot media
  is on the module (G2 closed).**
- **Interconnect:** 270-pad, 0.8 mm-pitch **direct-solder** edge (half-hole) — **no connector,
  no added Z-height** (ideal for the pod), solders flat to the carrier.
- **Interfaces to carrier:** 2× GbE (1× via on-module DP83867IR PHY, 1× RGMII pins to
  carrier), up to 9 UART, 3× CAN-FD, 6 I²C, 4 SPI, 1× 4-lane MIPI CSI-2 v1.3.
- **Size:** 40 × 40 mm (drives the trapezoid wide end).

**Chosen over** Variscite VAR-SOM-AM62 (67.8×33 mm, and plain AM62 = no ISP) and Critical Link
MitySOM-AM62A (~43×39 mm) on footprint + direct-solder (no connector height). The 38×28 mm
Beacon AM62**L** was rejected — the L variant has **no ISP/VPAC/encode**.

**Trade to accept:** a SoM adds some **Z-height** (module thickness + its tallest part; no
connector, since this module is direct-solder) and per-unit cost, in exchange for deleting the
LPDDR4/flash/sequencing design and the single largest fabrication risk. For a low-volume flight
build this trade strongly favors the SoM.

---

## 3B. Carrier interface / net map (the schematic plan)

This is the wiring the carrier schematic implements. Every carrier-side part below has a
**verified pinout already in this repo** (reused from `gen_cape_a2*.py` / existing Vera files) —
only the **SoM-side pad numbers** are datasheet-gated. The generator (a `gen_vera_sch.py`, in
the Emma pattern) can wire all of this the moment the phyCORE-AM62A pad map is available.

**Interface map (SoM function → carrier net → destination):**

| SoM function | Carrier net(s) | Destination on carrier |
| --- | --- | --- |
| RGMII (1×, to-connector) + MDIO | RGMII_TXD[0:3]/RXD[0:3]/TXC/RXC/TXCTL/RXCTL, MDC/MDIO | KSZ9477 switch (HSR/PRP ring) |
| MIPI CSI-2 (4-lane + CLK) | CSI_D[0:3]±, CSI_CLK± | Camera connector / direct-solder land (§4) |
| SPI (1×) | SPI_TPM_SCLK/MOSI/MISO/CS_N | SLB9670 TPM |
| CAN-FD (1×) | MCU_CANL/CANH domain | MSPM0G3507 → ISOW1044 isolated CAN → J_CANFD |
| UART (1–2×) | ToF_UART_TX/RX; console UART | MSPM0G3507 / TFmini-S ToF; debug header |
| GPIO/PWM | LASER_EN, LASER_PWM, LASER_KEY (opt.) | Laser driver (Q1 + hardware current limit) |
| Reset / boot-mode | POR_N, BOOTMODE straps | pull-net resistors per HW manual |
| Power in | +5V, GND, PGND | 5 V feed (POWER_DISTRIBUTION.md §3.2.1); SoM makes its own rails |

**Power tree:** 5 V in → phyCORE-AM62A VIN (module hosts its own PMIC/sequencing). Carrier-only
loads (KSZ9477, SLB9670, MSPM0G3507, magnetics) draw from either the SoM's exposed 3V3/1V8 rails
*or* a small carrier LDO — **which, is datasheet-gated** on what rails the module brings out to
the 270 pads (HW manual). Ethernet EMI chain unchanged: Wurth 749010012A + 2× SRF2012 CMC + 2×
PRTR5V0U2X TVS per port; same CMC+TVS on the CAN bus after ISOW1044.

**Trapezoidal outline spec (KiCad Edge.Cuts):** narrow end **≤ 25.4 mm (1.0 in)** at the pod;
wide end **≈ 42 mm** (40 mm module + 1 mm/side); length set by nose interior aft of the pod
(FreeCAD check against `airframe/openscad/fuselage/bow_sensor_pod.scad` — **refer final length
to user**, per the placement rule). Narrow end carries the camera + ToF + laser (toward the
pod); wide end carries the SoM + KSZ9477. Sidewalls follow the cone half-angle.

**Unblock path (the one gate to a real symbol):** obtain the phyCORE-AM62A **270-pad pin map**,
by either — (a) downloading the **SnapMagic "PHYCORE-AM62AX-DSC" KiCad symbol + footprint**
(snapeda.com) and dropping it in `avionics/kicad/`, or (b) attaching the **PHYTEC phyCORE-AM62A
Hardware Manual** PDF (pad-assignment table) to the repo. Both hosts are blocked by this
environment's PermissionRequest hook, so this is a **user action** (allowlist the domain, or
download + commit the file). Then `gen_vera_sch.py` wires §3B and ERC-checks it.

---

## 4. Dual camera / ToF / laser interface — connector OR direct-solder (design spec)

Requirement (user, 2026-07-06): the camera, ToF, and laser must be **either** cabled via
connectors (cargo install) **or** soldered directly to the board (nose install, to sit flush in
the pod). Recommended implementation — **co-located dual footprint, populate one per build:**

- For each of the three interfaces (camera CSI, ToF UART, laser drive), place **two footprints
  on the same nets, side by side:**
  1. the existing **JST-GH/JST-SH connector** (cargo build — populated), and
  2. a **direct-solder land** — a castellated / SMD pad row (e.g. a 1.27 mm or 1.0 mm pad array,
     or a 0.5 in-edge castellated strip) matching the camera/ToF/laser flex or module pinout —
     onto which the module solders directly (nose build).
- **Populate exactly one per install** (the other is DNP). Both share identical nets, so the
  schematic carries them as alternate-footprint options; DRC treats the unpopulated one as a
  no-load.
- This keeps **one board design** for both installs (per the standing Vera principle) and needs
  no schematic net change — only added footprints. It is a clean, verifiable task that does
  **not** depend on the SoC datasheets, so it can be done independently of G1–G6 — **but** do it
  *after* the real SoC/DDR placement so the direct-solder lands don't collide with BGA escape.

---

## 5. Minor footprint fixes (verifiable now)

- **CMC1–5 (SRF2012-100Y)** currently use `Inductor_SMD:L_Taiyo-Yuden_NR-20xx` — a 2-pin power
  inductor land, **not** the 4-pin 2012-metric common-mode-choke land the SRF2012 needs. Swap to
  the `Bourns_SRF2012` (4-pad) footprint used on Wash/Zoë/Vera elsewhere.
- **C_ISO (100 nF / 500 V)** is on an `R_0402` land — a 500 V cap will not fit an 0402. Use a
  proper HV MLCC footprint (≥ 1206/1210 for 500 V) or drop the voltage rating to what the
  isolation actually needs.

(These are noted, not yet applied — the board is not fabricable until §3, and PCB edits carry the
recurring GUI-corruption risk now guarded by `tools/precommit_kicad_load.py`.)

---

## 6. Staged plan to fabricable

### 6.1 Recommended — SoM-carrier path

1. **Select the AM62A SoM** against §3A criteria; obtain its datasheet, carrier design guide,
   reference schematic, and **board-to-board connector P/N** *(datasheet gate — refer the final
   pick to the user; requires reaching PHYTEC/Variscite datasheets, blocked this session)*.
2. **Confirm Z/width fit** of the module + connector against the nose pod
   (`bow_sensor_pod.scad`) and the 1.0 in carrier width.
3. **Schematic-first (carrier):** replace the raw AM62A + placeholder DRAM/flash/PMIC nets with
   the SoM connector symbol; wire SoM↔KSZ9477 (RGMII/MDIO), SoM↔camera (CSI-2), SoM↔TPM (SPI),
   SoM↔MSPM0G3507, power-in per the design guide. Keep KSZ9477/ISOW1044/SLB9670/MSPM0G3507
   pin maps datasheet-correct (still §G3 for *these* parts — but no 484-ball SoC map needed).
4. **Footprints:** SoM connector land + real land patterns for the remaining ICs; apply §5 fixes.
5. **Place + route (ordinary ~4-layer):** SoM connector, KSZ9477 RGMII pairs, CSI-2 pairs,
   Ethernet magnetics pairs, CAN; add the §4 dual camera/ToF/laser interface.
6. **Verify:** ERC + DRC to 0 hard (CI validator), then gerbers + fab notes.

**Why this is tractable:** no LPDDR4 fly-by routing, no 484-ball BGA escape, no power
sequencing — those ship on the module. Steps 3–6 are ordinary carrier work I can do
schematic-first (as with Emma) once the module + connector P/N are chosen.

### 6.2 Fallback — raw-SoC path (only if no AM62A SoM qualifies)

1. **Select + datasheet** the LPDDR4 (G1), boot media (G2), AM62A7 ball map, and the other ICs
   (G3). 2. **Schematic-first:** add LPDDR4 + boot-flash + power-sequencing; correct all pin
   maps. 3. **Footprints:** real land patterns + §5 fixes. 4. **Stack-up:** 6-layer for DDR +
   BGA escape. 5. **Place + route:** BGA escape, DDR byte-lane match, CSI-2/RGMII/Ethernet pairs,
   plus the §4 interface. 6. **Verify:** ERC/DRC, impedance/length reports, gerbers.

**Honest scope note:** in 6.2, steps 4–5 (impedance-controlled DDR/BGA layout) realistically
need interactive layout with a length-tuning tool and hand review of the critical nets — not
blind scripting. That risk is precisely what 6.1 eliminates. This document is the checklist so
nothing above is forgotten.

---

*© 2026 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP — CC BY 4.0*
