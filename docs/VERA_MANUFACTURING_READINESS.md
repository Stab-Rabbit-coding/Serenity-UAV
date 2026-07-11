# Vera — Manufacturing-Readiness Gap Analysis

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**AI-assist:** Claude Opus 4.8 (Anthropic) — gap analysis, 2026-07-06
**License:** CC BY 4.0
**Revision:** Rev A (2026-07-06)
**Status:** Analysis — what stands between the current Vera design and a fabricable board.

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
guard, `tools/precommit_kicad_load.py`) is done. The rest is itemized below with a staged plan.

---

## 2. Current footprint state

| Class | Refs | Footprint status |
|---|---|---|
| **Real / verifiable** | T1/T2 (749010012A), J_ETH_IN/OUT, J_CANFD, J_PWR, J_TOF, J_CAM1/2, J_LASER, U4 (ISOW1044 SOIC-16W), CMC1-5, D1-5, Q1, Y1, R1/R2, C_MCU1, H1-4 | OK (see §5 for two minor fixes) |
| **Placeholder — needs datasheet** | **U1 AM62A7** (BGA-484), **U2 KSZ9477** (QFN-128), **U3 MSPM0G3507** (VSSOP-28), **U5 SLB9670** (VQFN-32), **U_PMIC TPS65219** (VQFN-32) | Land pattern *and* pin map both placeholder |
| **MISSING entirely** | LPDDR4 DRAM, boot flash (eMMC/OSPI NOR), DDR termination, full PMIC power-sequencing net, SoC PLL/loop-filter passives | Not in schematic |

---

## 3. Critical gaps (in priority order)

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

1. **Select + datasheet** the LPDDR4 (G1), boot media (G2), and confirm the AM62A7 package/ball
   map, KSZ9477, TPS65219, SLB9670, MSPM0G3507 (G3). *(Requires fetching/attaching real
   datasheets — the no-fabrication gate.)*
2. **Schematic-first:** add the LPDDR4 + boot-flash + power-sequencing subsystems; correct all
   pin maps (schematic is the source of truth — cf. the Emma reconciliation).
3. **Footprints:** real land patterns for all ICs + memory; apply the §5 fixes.
4. **Stack-up:** define the impedance-controlled layer stack (likely 6-layer for DDR + BGA
   escape, not the current 4).
5. **Place + route:** BGA escape, DDR byte-lane match, CSI-2/RGMII/Ethernet pairs; add the §4
   dual camera/ToF/laser interface.
6. **Verify:** ERC + DRC to 0 hard (CI validator), impedance/length reports, then gerbers + fab
   notes.

**Honest scope note:** steps 1–3 I can do incrementally *with verified datasheets* (one
subsystem at a time, schematic-first, as with Emma). Steps 4–5 (impedance-controlled DDR/BGA
layout) realistically need interactive layout with a length-tuning tool, not blind scripting —
I can set up the constraints and do the non-critical routing, but the DDR/BGA critical nets
should be laid out and reviewed by hand. This document is the checklist so nothing above is
forgotten.

---

*© 2026 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP — CC BY 4.0*
