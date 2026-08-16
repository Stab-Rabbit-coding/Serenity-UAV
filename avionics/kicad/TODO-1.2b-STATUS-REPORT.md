# Todo Item 1.2b — PCB Redesigns Status Report

**Date:** 2026-07-18  
**Branch:** `claude/todo-item-1-2b-e89qrb`  
**Status:** BLOCKED — Awaiting KiCad tools and user interaction

---

## Executive Summary

Todo item 1.2b requires completing PCB redesigns for three boards:
1. **Emma Rev S1** — Add LoRa, replace JST with P1+P2 socket rails
2. **TACCO Rev S1** — Remove LoRa, add P1+P2 passthrough rails  
3. **FlightEngineer Rev S1** — Remove 6 V BEC, add 5 V servo output

Most of the technical work has been started and partially completed, but **all three boards are blocked from completion** due to:
- Missing KiCad tools (kicad-cli, pcbnew Python module)
- User interaction required (TACCO reference-designator mapping, Emma RSSI routing)
- Design decisions needing sign-off (firmware pinmux approvals)

---

## Detailed Status by Board

### 1. Emma Rev S1 — Add LoRa, Replace JST with P1+P2 Socket Rails

**Last Updated:** 2026-07-05 (13 days old)  
**Completion Status:** ~70% (schematic complete, PCB 90% routed, blocking items prevent gerber export)

#### Completed ✓
- [x] Schematic authored from as-placed PCB (`gen_emma_sch.py`, 2026-07-04)
  - ERC: 0 errors, 120 benign warnings
  - 74 reference designators match, 104 nets exact parity
- [x] PCB rework applied (`mod_emma_pcb.py`, 2026-07-04)
  - J1 (JST-GH-6P) removed; UART moved to PB2-P1 rails
  - RSSI_CMP comparator + dividers added
  - DRC hard violations cleared: 0 errors
- [x] RSSI parts placed by user (2026-07-05) — parked on back of board in RF section
- [x] RSSI sub-circuit routed (2026-07-05, `route_emma_rssi.py`)
  - GND, RSSI_REF, +3V3, +3V3-link, RSSI_ANA all routed
  - Unconnected pad count: 104 → 95

#### Blocking — Cannot Complete Without KiCad
- [ ] **RSSI_DCD routing** — 1 net remaining (~28 mm cross-board run)
  - Attempted in `route_emma_rssi.py dcd` but naively routes; needs GUI push-shove or real autorouter
  - **TOOL REQUIRED:** kicad-cli/pcbnew for interactive or advanced autorouting
  - **Impact:** RSSI carrier-detect feature incomplete; output line to host PB2-P2 pad 2 unconnected
  
- [ ] **13 nets still unrouted** (from prior sessions)
  - RF_TX, RF_FILT, RF_LPF_N2, RX_LNA, TCXO_OUT, AFSK_IN, AFSK_OUT, DDS_CLK, DDS_DAT, SBUS_OUT, RF_RX, RSSI_RAW, UART_RX_MUX
  - Trapped in tight pockets; need thinner traces, B.Cu fallback, or manual GUI routing
  - **TOOL REQUIRED:** kicad-cli for DRC; pcbnew for advanced routing
  
- [ ] **Ethernet differential pairs deferred** (RMII1_*, MDIO, MDC, PHY2_*, EMMA_ETH_*)
  - Need length/impedance-matched routing
  - **TOOL REQUIRED:** kicad-cli/pcbnew + impedance calculator
  
- [ ] **LoRa SPI bus deferred** (LORA_RESETN, SPI1_MISO/MOSI/CLK/CS_LORA)
  - Same reasoning as Ethernet pairs
  - **TOOL REQUIRED:** kicad-cli/pcbnew
  
- [ ] **GND2_ETH / VCC2_ETH isolated domain routing**
  - Needs isolated copper island, not stitched to main GND plane
  - **TOOL REQUIRED:** kicad-cli/pcbnew for zone management
  
- [ ] **RSSI_CMP part/pinout vetting** — PROVISIONAL placeholder "LMV331-class"
  - Real part number + SOT-23-5 pin order MUST be confirmed
  - Comparator datasheet required to verify push-pull vs open-drain (pull-up needed if open-drain)
  - **ACTION REQUIRED:** User to research + document part selection in REFERENCES.md
  - **IMPACT:** Medium — affects firmware driver implementation
  
- [ ] **3 pre-existing in-circuit stubs** — identified by new schematic
  - RF_ANT_SW (T/R-switch antenna common, unconnected)
  - PA_EMIT (PA emitter-degeneration return)
  - DDS_FSYNC (MCP4921 ~LDAC/CS)
  - **ACTION REQUIRED:** User to route on PCB
  - **TOOL REQUIRED:** kicad-cli for DRC; pcbnew for routing
  - **IMPACT:** High — missing RF circuit connections
  
- [ ] **Silk overlap/over-copper cleanup**
  - 174 pre-existing warnings (119 silk_over_copper + 53 silk_overlap + 2 silk_edge_clearance)
  - Not caused by recent work; deferred to dedicated session
  - **TOOL REQUIRED:** kicad-cli DRC for verification
  - **IMPACT:** Low — cosmetic/manufacturing readability only
  
- [ ] **LoRa connectivity issues** (RFM95W footprint)
  - Pad 9 (ANT) and pad 13 (3.3V) carry no net — module has no antenna or power path
  - **ACTION REQUIRED:** User design decision: route antenna + supply, or remove LoRa entirely?
  - **IMPACT:** CRITICAL — LoRa module cannot function as currently wired
  
- [ ] **Gerber generation** BLOCKED
  - `generate_gerbers.py` requires `kicad-cli` not available
  - Output directory: `avionics/kicad/gerbers/Emma-S1/`
  - **REQUIRES:** kicad-cli + completion of above routing/part-selection work

#### Summary
Emma is ~90% complete on schematic/PCB design, but **cannot be fabricated** until:
1. All 13 unrouted nets completed (requires KiCad routing tools)
2. Differential pair impedance routing (Ethernet, LoRa SPI) completed (requires KiCad)
3. RSSI_CMP part/pinout confirmed (requires user research + datasheet)
4. Firmware sign-off on PTT_N/RSSI_DCD pinmux (requires firmware review)
5. LoRa connectivity resolved (antenna + supply path to pads 9/13)
6. 3 pre-existing stubs routed (requires KiCad)
7. DRC to zero errors (requires kicad-cli)
8. Gerbers generated (requires kicad-cli)

---

### 2. TACCO (Cape-B-2) Rev S1 — Remove LoRa, Add P1+P2 Passthrough Rails

**Last Updated:** 2026-07-04  
**Completion Status:** ~65% (PCB finished, schematic needs major reconciliation)

#### Completed ✓
- [x] Schematic file load bug fixed (2026-07-04)
  - Stray `(comment)` elements at top-level converted to valid `(text)` annotation
  - File now loads in kicad-cli 9.0.2
  - ERC: 564 pre-existing violations (not caused by recent work)

- [x] PCB already at intended end-state (verified 2026-07-04)
  - LoRa (RFM95W) removed — footprint **gone**, traces cleaned
  - P1+P2 socket rails placed: `2x18_P1_Socket` + `2x18_P2_Socket` on upper face
  - `PB2-P1/P2-TOP` passthrough headers placed
  - Lower pins pass through to Cape-A-2 / PB2-I stack

#### Blocking — Requires User Interaction + KiCad
- [ ] **CRITICAL: Full sch↔pcb reference-designator remap**
  - **PROBLEM:** Schematic uses different naming convention than PCB (~10 of ~50 refs match)
    - Schematic: `CMC_CAN`, PCB: `CMC-CAN`
    - Schematic: `X2Y_RS485`, PCB: `X2Y-RS485`
    - Schematic: `WINCH-DRV`, PCB: `WINCH DRV`
    - Schematic: `RS485`, PCB: `RS-485`
    - Schematic: `WIFI-BT`, PCB: `WIFI & BT`
    - … and 45 more mismatches
  - **ACTION REQUIRED:** User to confirm sch↔pcb footprint mapping (flight-hardware risk — guessing could mis-associate critical components)
  - **RECOMMENDED APPROACH:** Interactive confirmation in KiCad GUI or user-supplied name-map CSV
  - **TOOL REQUIRED:** kicad-cli for back-annotation + ERC validation after remapping
  - **IMPACT:** CRITICAL — cannot proceed without resolving this; risk of electrical errors

- [ ] **Schematic cleanup** (after reference-designator remap)
  - Remove LoRa block: LORA, RFM95W, FL_LORA, D_ANT_LORA, J_SMA_LORA, BPF_915×2
  - Remove obsolete J_XCVR (JST-GH Emma-cable connector — Emma now stacks via P1/P2)
  - Remove SBUS block: U_SBUS_B, R_SBUS_RX, SW1
  - Add P1/P2 passthrough sockets to schematic (already placed on PCB)
  - Re-run ERC after cleanup
  - **TOOL REQUIRED:** kicad-cli for ERC validation
  - **IMPACT:** High — schematic will match PCB only after these deletions

- [ ] **Verify P1/P2 socket nets** — Confirm already-placed sockets carry correct signals
  - Lower P1/P2 pins → upper P1/P2 sockets should pass through all PB2 signals
  - Confirm proper passthrough 0Ω jumper placement on signals consumed by TACCO (Wi-Fi, SiK, I²C, UART)
  - **ACTION REQUIRED:** User to inspect `TACCO.kicad_pcb` P1/P2 socket net assignments
  - **TOOL REQUIRED:** kicad-cli for net connectivity check
  - **IMPACT:** Medium — if nets are wrong, Emma stack will not function

- [ ] **Nets and vias** — Finalize interconnections post-reference-remap
  - **TOOL REQUIRED:** kicad-cli DRC for validation

- [ ] **DRC to zero hard errors**
  - Currently pre-existing 564 ERC violations (not from recent work)
  - After schematic cleanup + remap, re-run ERC
  - **TOOL REQUIRED:** kicad-cli `sch erc`

- [ ] **Gerbers export** BLOCKED
  - Requires completion of above work + kicad-cli
  - Output directory: `avionics/kicad/gerbers/CAPE-B-2-S1/`

#### Summary
TACCO PCB is **complete and ready**, but schematic is **30 days behind** and cannot be used without:
1. **User confirmation of reference-designator mapping** (no guessing — flight-critical board)
2. Removal of LoRa, J_XCVR, SBUS blocks from schematic
3. Addition of P1/P2 passthrough sockets to schematic
4. Verification of P1/P2 socket net assignments on PCB
5. ERC cleanup and DRC validation (kicad-cli required)
6. Gerber generation (kicad-cli required)

---

### 3. FlightEngineer Rev S1 — Remove 6 V BEC, Add 5 V Servo Output

**Last Updated:** 2026-07-18 (no recent work)  
**Completion Status:** 0% (design not started; current board is Rev R, not S1)

#### Current State
- Schematic exists: `avionics/kicad/FlightEngineer/kicads/FlightEngineer.kicad_sch` (Rev R)
  - TPS54540DDAR 6V/5A BEC defined at U_BEC_6V (lines 3552–3580)
  - Dual TPS54620 5V BECs already present (U_BEC_5V_1, U_BEC_5V_2)
  - Board status: "Schematic complete — PCB layout pending DRC sign-off"

#### Required Changes
- [ ] **Remove 6 V BEC circuit**
  - Delete TPS54540DDAR symbol (U_BEC_6V)
  - Delete associated inductors, capacitors, feedback dividers
  - Delete Molex Nano-Fit 6 V output connector
  - Delete Wurth 742792612 ferrite bead (FB_6V)
  - Delete related net labels/global labels (BOOT6V, FB6V_*, SW6V, COMP6V, SS6V)
  - **Schematic refs to delete:** U_BEC_6V, FB_6V, L3, C_BEC_SV_IN, and 8 global labels

- [ ] **Add third TPS54620 for 5 V servo rail**
  - Duplicate second 5V BEC (U_BEC_5V_2) instance
  - Rename to U_BEC_SERVO_5V (or similar)
  - Change output connector label from "6V_SERVO" to "SERVO-5V"
  - Verify 5 V servo current budget: 2× DS3218MG = 2× 500 mA stall = 1.0 A peak
    - TPS54620 3 A rated output provides 3× headroom ✓ (adequate)
  - Add to fabric layer: "FlightEngineer Rev S1"

#### Design Approach
```
SECTION E (OLD): 6V Servo BEC (TPS54540)
→ 
SECTION E (NEW): 5V Servo BEC (TPS54620)
  - Duplicate Section D (5V BEC) instance
  - Change output connector and labels to indicate 5V servo use
  - Keep feedback reference tied to other 5V BECs
  - Separate output capacitor bank per existing pattern
```

#### Blocking Work
- [ ] **Schematic modification**
  - Edit `FlightEngineer.kicad_sch` to remove TPS54540 circuit, add third TPS54620
  - Update title block to "Rev S1"
  - **RISK:** Editing S-expression KiCad files without interactive tool is error-prone
  - **RECOMMENDED:** Use KiCad GUI to make these changes safely
  - **TOOL REQUIRED:** KiCad interactive editor for schematic edits (or careful manual S-expression editing + validation)

- [ ] **PCB rework** (after schematic finalized)
  - Remove TPS54540 footprint + inductor/capacitor/connector footprints
  - Add third TPS54620 instance footprint (copy from U_BEC_5V_2)
  - Route power/feedback nets
  - **TOOL REQUIRED:** kicad-cli for DRC; pcbnew for layout
  - **IMPACT:** Medium — PCB impact is moderate (same footprints as existing 5V BECs)

- [ ] **DRC to zero hard errors**
  - Run `kicad-cli sch erc` and `kicad-cli pcb drc`
  - **TOOL REQUIRED:** kicad-cli

- [ ] **Gerber generation**
  - Output directory: `avionics/kicad/gerbers/FlightEngineer-S1/`
  - **TOOL REQUIRED:** kicad-cli + `generate_gerbers.py`

#### Summary
FlightEngineer design changes are **straightforward** (6V → 5V servo rail conversion) but **not yet started**.
- Schematic is easy to plan (delete one BEC section, duplicate another)
- PCB footprints are straightforward (same TPS54620 size/pinout as existing)
- **Main risk:** Safe editing of S-expression schematic files without KiCad validation tools

---

## Dependency Chain

```
Emma Rev S1:
  → Schematic complete (DONE)
  → PCB 90% routed (NEEDS: 13 nets + differential pair routing, kicad-cli DRC)
  → RSSI_CMP part selection (NEEDS: user research + datasheet)
  → Firmware sign-off (NEEDS: firmware team review)
  → Gerber export (NEEDS: kicad-cli, all above complete)

TACCO Rev S1:
  → PCB complete (DONE)
  → Schematic remap (BLOCKED: NEEDS user sch↔pcb confirmation, kicad-cli ERC)
  → Gerber export (NEEDS: kicad-cli, schematic complete)

FlightEngineer Rev S1:
  → Schematic edit (NEEDS: schematic mods + careful S-expression work or KiCad GUI)
  → PCB layout (NEEDS: footprint placement, routing, kicad-cli DRC)
  → Gerber export (NEEDS: kicad-cli, all above complete)

CRITICAL PATH: TACCO sch↔pcb remap (user decision) + Emma part selection (user research)
```

---

## Recommendations for Completion

### Immediate (No Tools Required)
1. **TACCO reference-designator mapping**
   - User to create name-map CSV or JSON mapping schematic refs → PCB refs
   - Example: `{ "CMC_CAN": "CMC-CAN", "X2Y_RS485": "X2Y-RS485", … }`
   - **Effort:** ~30 min (tedious but straightforward)

2. **Emma RSSI_CMP part selection**
   - User research: LM393, LMV331, LM741, or similar?
   - Confirm SOT-23-5 pin order against real datasheet
   - Verify push-pull vs open-drain (pull-up topology)
   - Add REFERENCES.md entry with part number + datasheet link
   - **Effort:** ~1 hour (research + datasheet verification)

3. **FlightEngineer design review**
   - Confirm 5V servo rail (2× DS3218MG) vs 6V conversion is acceptable for firmware/mechanics
   - **Effort:** 15 min (cross-team sync)

### With KiCad Tools Available (kicad-cli + pcbnew Python)
1. **Emma routing completion** (~4–6 hours)
   - 13 unrouted nets + differential pairs + stubs routing
   - Use `route_emma_rssi.py dcd` as starting point for RSSI_DCD
   - Run DRC iteratively
   - Generate gerbers

2. **TACCO schematic reconciliation** (~2–3 hours)
   - Apply name-map to remap refs
   - Delete LoRa/SBUS/J_XCVR blocks
   - Add P1/P2 sockets to schematic
   - Run ERC to zero
   - Generate gerbers

3. **FlightEngineer S1 conversion** (~2–3 hours)
   - Remove TPS54540 circuit from schematic
   - Add third TPS54620 instance
   - PCB footprint rework (copy TPS54620 instance)
   - Route nets, run DRC
   - Generate gerbers

### Total Effort Required
- **User input (no tools):** ~2 hours (remap + part research)
- **KiCad work (with tools):** ~8–12 hours (routing + schematic reconciliation)
- **Total estimated:** ~10–14 hours to fabrication-ready gerbers

---

## Files Involved

### Emma
- Schematic: `avionics/kicad/Emma/kicads/Emma.kicad_sch` (generated, DONE)
- PCB: `avionics/kicad/Emma/kicads/Emma.kicad_pcb` (90% routed, NEEDS work)
- Scripts:
  - `gen_emma_sch.py` (schematic generation, DONE)
  - `mod_emma_pcb.py` (PCB rework, DONE)
  - `route_emma_rssi.py` (RSSI routing, partial)
  - `cleanup_emma_drc.py` (DRC cleanup, DONE)
- Documentation: `avionics/kicad/Emma/Emma.md` (up-to-date)

### TACCO
- Schematic: `avionics/kicad/TACCO/kicads/TACCO.kicad_sch` (NEEDS reconciliation)
- PCB: `avionics/kicad/TACCO/kicads/TACCO.kicad_pcb` (DONE)
- Documentation: `avionics/kicad/TACCO/TACCO.md` (notes remap is needed)

### FlightEngineer
- Schematic: `avionics/kicad/FlightEngineer/kicads/FlightEngineer.kicad_sch` (NEEDS Rev S1 edits)
- PCB: `avionics/kicad/FlightEngineer/kicads/FlightEngineer.kicad_pcb` (NEEDS S1 layout)
- Documentation: `avionics/kicad/FlightEngineer/FlightEngineer.md` (notes Rev R status)

### Work Tracking
- Root TODO: `TODO.md` §1.2b (high-level, 3 items unchecked)
- Detailed WBS: `avionics/rev-s1/WBS.md` §1.2b (100+ line items, many checked, many open)

---

## Conclusion

**All three boards are blocked from completion.** While Emma and TACCO have substantial prior work, they cannot reach fabrication-ready state without:
1. KiCad tools (kicad-cli, pcbnew Python)
2. User decisions (TACCO remap, Emma part selection, FlightEngineer 5V confirmation)
3. Firmware team sign-off (PTT_N/RSSI_DCD pinmux)

**FlightEngineer design is straightforward** but has not been started — design decisions are clear and low-risk.

**Recommended next steps:**
1. Provide KiCad tools (install kicad-cli + python-pcbnew, or use interactive KiCad GUI)
2. User supplies TACCO reference-designator mapping
3. User researches Emma RSSI_CMP part + datasheet
4. Firmware team reviews PTT_N/RSSI_DCD pinmux constraints
5. Execute routing / schematic edits with KiCad

---

*Report generated: 2026-07-18 | Session: `claude/todo-item-1-2b-e89qrb`*
