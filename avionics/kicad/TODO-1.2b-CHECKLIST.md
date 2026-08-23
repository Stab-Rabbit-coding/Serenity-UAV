# Todo 1.2b Completion Checklist — Expedited Workflow

**Prepared:** 2026-07-18  
**For:** KiCad 9.0.2 (December 2025 Debian release)  
**Estimated Duration:** 8–12 hours (with KiCad tools + automation scripts)

---

## Pre-Execution Setup

### Environment Verification
- [ ] KiCad 9.0.2+ installed and in PATH
  ```bash
  kicad-cli --version  # Should show 9.0.2+
  ```
- [ ] pcbnew Python module available
  ```bash
  python3 -c "import pcbnew; print(pcbnew.__version__)"
  ```
- [ ] Repo root is Serenity-UAV directory
  ```bash
  pwd  # Should end with Serenity-UAV
  ls avionics/kicad/Commo  # Should show kicads/, Commo.md, scripts/
  ```

### Pre-Work Review
- [ ] Read `avionics/rev-s1/WBS.md` §1.2b (understanding of design decisions)
- [ ] Read `AGENTS.md` §5 & §7 (standards compliance requirements)
- [ ] Review existing `avionics/kicad/*/Commo.md`, `XO.md`, `FlightEngineer.md` (current state)

---

## COMMO REV S1 — Add LoRa, Replace JST with P1+P2 Socket Rails

### Phase 1: RSSI Routing Completion

**Status:** ~95% complete (schematic/PCB routing 90%, gerbers blocked)

#### Task 1.A: Route RSSI_DCD (1 net, ~28 mm cross-board run)
- [ ] Open `avionics/kicad/Commo/kicads/Commo.kicad_pcb` in KiCad
- [ ] Run starting path:
  ```bash
  cd avionics/kicad/Commo && python3 scripts/route_commo_rssi.py dcd
  ```
  (Creates initial trace path from RSSI_CMP.5 toward PB2-P2 pad 2)
- [ ] In KiCad, use Push-Shove routing (Ctrl+Shift+R) to complete
  - Start from: RSSI_CMP output (CMP.5 at ~133.45, 118.91)
  - End at: PB2-P2 pad 2 (105.4, 130.2)
  - Constraints: Avoid ETH-PHY section (B.Cu congestion), route around LoRa
  - Trace width: 0.15 mm (maintain consistency with prior RSSI traces)
- [ ] Save PCB: File → Save (Ctrl+S)
- [ ] Verify no new DRC violations introduced:
  ```bash
  kicad-cli pcb drc --schematic-parity Commo.kicad_pcb 2>&1 | grep -i error
  ```

#### Task 1.B: Route remaining 13 nets (complex, deferred from prior sessions)
**Nets to route:** RF_TX, RF_FILT, RF_LPF_N2, RX_LNA, TCXO_OUT, AFSK_IN, AFSK_OUT, DDS_CLK, DDS_DAT, SBUS_OUT, RF_RX, RSSI_RAW, UART_RX_MUX

- [ ] Open Commo.kicad_pcb in KiCad
- [ ] For each net:
  1. Highlight net: Right-click net → Select net
  2. Try interactive push-shove routing (Ctrl+Shift+R)
  3. If too tight, use B.Cu (bottom copper) fallback traces
  4. Trace width: 0.20 mm (standard signal)
  5. After each net, run incremental DRC:
     ```bash
     kicad-cli pcb drc --schematic-parity Commo.kicad_pcb 2>&1 | tail -20
     ```

**Pro Tips:**
- Sort nets by location (RF section clustered together, digital on opposite side)
- Use Layer Toggle (L key) to route on B.Cu where F.Cu is congested
- Via placement: center in clearance, 0.3 mm drill / 0.6 mm pad
- Check impedance on differential pairs (Ethernet, LoRa SPI):
  ```bash
  python3 avionics/kicad/check_impedance.py  # Verify 50Ω target
  ```

#### Task 1.C: Route differential pairs (Ethernet, LoRa SPI)
**Deferred nets:** RMII1_*, MDIO, MDC, PHY2_*, EMMA_ETH_*; LORA_RESETN, SPI1_*

- [ ] Ethernet differential pairs (through T-ETH isolation transformer)
  - Pairs: EMMA_ETH_TXP/TXN, EMMA_ETH_RXP/RXN
  - Impedance: 85–100Ω differential (twisted pair, close coupling)
  - Length-match to within ±0.5 mm
  - Route via: 0.3 mm drill, after placing, verify via stitching via pattern
  
- [ ] LoRa SPI bus (to RFM95W module pads 2–6)
  - Signals: SPI1_MISO/MOSI/CLK/CS_LORA
  - Keep short and compact (RFM95W near Ethernet PHY area)
  - Via placement: near IC pads, 0.3 mm drill
  - Update CMC guard to cover LoRa SPI (if not already done)

- [ ] After completing all routing, run full DRC:
  ```bash
  kicad-cli pcb drc --schematic-parity Commo.kicad_pcb
  ```
  - Target: 0 hard violations (shorting, clearance, courtyard)
  - Accept: SOFT violations (silk, lib-footprint, dangling via — pre-existing backlog)

#### Task 1.D: Address pre-existing in-circuit stubs
**Missing nets:** RF_ANT_SW (T/R-switch antenna common), PA_EMIT (PA emitter return), DDS_FSYNC (MCP4921 LDAC/CS)

- [ ] For each stub, decide: route or intentionally leave unconnected?
  - RF_ANT_SW: Typically the antenna input from the T/R switch; likely needs routing to antenna pad
  - PA_EMIT: Emitter-degeneration return on PA stage (2N3866); should return to GND via resistor
  - DDS_FSYNC: MCP4921 LDAC/CS; check firmware usage (might be tied high if unused)
  
- [ ] Research firmware (contact firmware team if needed):
  ```bash
  grep -r "DDS_FSYNC\|PA_EMIT\|RF_ANT_SW" gcs/firmware/  # Check driver code
  ```

- [ ] If required, route to appropriate pads; if intentionally open, add note in schematic/docs

#### Task 1.E: Silk cleanup (174 pre-existing warnings)
- [ ] DRC: Run to identify silk_over_copper + silk_overlap violations
  ```bash
  kicad-cli pcb drc Commo.kicad_pcb 2>&1 | grep silk
  ```
- [ ] **OPTIONAL:** Address cosmetic warnings (not blocking fabrication)
  - Move text to clear pads/traces if overlaps are severe
  - Reduce text size (0.6 mm min) where space is tight
  - Rationale: Legibility on silk layer for assembly/rework

#### Task 1.F: Generate Gerbers
- [ ] Run:
  ```bash
  python3 avionics/kicad/generate_gerbers.py commo
  ```
- [ ] Verify output in `avionics/kicad/gerbers/Commo-S1/`:
  ```bash
  ls -la avionics/kicad/gerbers/Commo-S1/*.gbr
  ```
- [ ] Inspect gerbers for correctness:
  - F.Cu, B.Cu: All traces/pads visible
  - F_Silkscreen, B_Silkscreen: Text readable, component labels present
  - F_Mask, B_Mask: Solder mask clearance correct (vias clear)
  - Edge_Cuts: Board outline closed loop
  - Drill file (.drl): Hole locations match PCB

---

## ZOËS (CAPE-B-2) REV S1 — Remove LoRa, Add P1+P2 Passthrough Rails

### Phase 2: Schematic Reconciliation (Critical Path Blocker)

**Status:** 65% complete (PCB done, schematic 30 days behind, major rework needed)

#### Task 2.A: Reference-designator remapping (CRITICAL)
- [ ] Open `avionics/kicad/XO/kicads/XO.kicad_sch` in KiCad
- [ ] Use reference mapping file: `avionics/kicad/XO/ref_remap_2026-07-18.json`
- [ ] For each mapping in "critical_renames":
  1. Edit → Find & Replace (Ctrl+H)
  2. Find: old reference (e.g., "CMC_CAN")
  3. Replace: new reference (e.g., "CMC-CAN")
  4. Replace All
  5. Run ERC immediately to check for issues:
     ```bash
     kicad-cli sch erc XO.kicad_sch | head -50
     ```
  6. If ERC errors appear, undo (Ctrl+Z) and diagnose

**Renames to apply:**
```
CMC_CAN        → CMC-CAN
CMC_RS485      → CMC-RS485
ETH_PHY_B      → ETH-PHY
FB             → FB1
RS485          → RS-485
X2Y_CAN        → X2Y-CAN
X2Y_RS485      → X2Y-RS485
WIFI-BT        → WIFI & BT
WINCH-DRV      → WINCH DRV
```

- [ ] After all renames, run full ERC:
  ```bash
  kicad-cli sch erc XO.kicad_sch
  ```
  - Accept pre-existing violations (564 warnings, not caused by remapping)
  - Check for NEW errors introduced by remapping (should be 0)

#### Task 2.B: Remove obsolete components (LoRa, SBUS, XCVR blocks)
- [ ] Open `XO.kicad_sch` (should already be open from 2.A)
- [ ] For each component in "to_delete_from_schematic":

  **LoRa block:**
  - [ ] Find & Delete: LORA, D_ANT_LORA, FL_LORA, J_SMA_LORA, BPF_915, BPF_915_2
    ```
    Ctrl+F → "LORA" → Navigate to each, Delete
    ```
  - [ ] Verify nets removed (no dangling net labels)
  - [ ] Run ERC after each deletion

  **SBUS block:**
  - [ ] Delete: U_SBUS_B, R_SBUS_RX, SW1
  - [ ] Clean up related nets

  **XCVR block (Commo cable — obsolete):**
  - [ ] Delete: J_XCVR, R_XCVR_RX, D_XCVR_TVS
  - [ ] Note: Commo now stacks on XO via P1/P2 passthrough, no cable needed

  **Deprecated items:**
  - [ ] Delete: CM_ETH_B, U_ETH_B_1V8, TVS_ETHB_RX, TVS_ETHB_TX

  **Placeholder symbols (if unused):**
  - [ ] Delete generic symbols (C, D, FB, FL, J, L, R, SW, T, U) if not referenced
  - [ ] Note: Keep any that have actual footprints placed on PCB!

- [ ] After each deletion, run ERC to verify no new errors

#### Task 2.C: Add P1/P2 TOP (passthrough) socket headers
- [ ] Open `XO.kicad_sch`
- [ ] Add symbols for passthrough sockets (copy from existing P1/P2 lower headers):
  - [ ] Add symbol: PB2-P1-TOP (upper-face passthrough, 2x18 header)
  - [ ] Add symbol: PB2-P2-TOP (upper-face passthrough, 2x18 header)
  - [ ] Wire: Each lower header pin → corresponding upper header pin (passthrough)
  - [ ] Add 0Ω jumpers on signals used by XO (Wi-Fi, SiK, I²C, UART) so they're both connected and passed through
  - [ ] Label nets clearly (e.g., "WIFI_TX_TOP", "UART_RX_TOP")

- [ ] Run ERC to verify all nets connected:
  ```bash
  kicad-cli sch erc XO.kicad_sch | grep -i dangling
  ```
  - Should show only pre-existing dangling labels (not new ones from passthrough work)

#### Task 2.D: Verify P1/P2 socket net assignments on PCB
- [ ] Open `avionics/kicad/XO/kicads/XO.kicad_pcb` in KiCad
- [ ] Inspect footprints: PB2-P1-TOP, PB2-P2-TOP (already placed per 2026-07-04 notes)
  - Select each pad → Check net assignment (Properties panel, right side)
  - Verify: Lower P1 pin N → Upper P1 pin N (same net)
  - Example: Pin 1 on lower P1 should connect to pin 1 on upper P1 (both "P1.1" or similar)

- [ ] If any net assignments are wrong on the PCB:
  - [ ] Either: Fix on PCB via pcbnew or
  - [ ] Document as "user will verify/fix during interactive PCB editing"

#### Task 2.E: Final ERC check
- [ ] Open `XO.kicad_sch`
- [ ] Run ERC:
  ```bash
  kicad-cli sch erc XO.kicad_sch
  ```
- [ ] Target: 0 NEW errors (pre-existing 564 warnings are acceptable)
- [ ] Document any new errors and resolve before proceeding

#### Task 2.F: Generate Gerbers
- [ ] Run:
  ```bash
  python3 avionics/kicad/generate_gerbers.py xo
  ```
- [ ] Verify output in `avionics/kicad/gerbers/CAPE-B-2-S1/`
- [ ] Inspect gerber files (same checklist as Commo 1.F)

---

## FLIGHT ENGINEER REV S1 — Remove 6 V BEC, Add 5 V Servo Output

### Phase 3: 6V→5V Servo Rail Conversion

**Status:** 0% (not yet started; design decisions clear, low risk)

#### Task 3.A: Edit Flight Engineer schematic (remove 6V BEC, add 5V servo BEC)
- [ ] Open `avionics/kicad/FlightEngineer/kicads/FlightEngineer.kicad_sch` in KiCad
- [ ] Navigate to Section E (6V Servo BEC) — search for "Section E" or "U_BEC_6V"

**DELETE (Section E, old 6V BEC):**
- [ ] Delete: U_BEC_6V (TPS54540DDAR 5A/40V buck 6.0V servo rail)
- [ ] Delete: FB_6V (Würth 742792612 ferrite bead 600R@100MHz)
- [ ] Delete: L3 (Würth 744314100 10µH inductor >=6A)
- [ ] Delete: C_BEC_SV_IN (100µF/50V electrolytic capacitor input)
- [ ] Delete: Molex Nano-Fit 6V output connector (and related nets: SERVO-6V, SERVO_6V_OUT, etc.)
- [ ] Clean up related net labels (BOOT6V, FB6V_*, SW6V, COMP6V, SS6V)

**ADD (Section E, new 5V servo BEC — copy from Section D pattern):**
- [ ] Duplicate Section D (5V BEC) as template
- [ ] Add: U_BEC_SERVO_5V (TPS54620RGYT 6A/28V sync buck 5.3V output)
  - Input: VBAT (28V main supply via choke)
  - Output: 5.3V regulated (trimmed to 5.0V via feedback divider)
  - Current rating: 3.0A (adequate for 2× DS3218MG = 1.0A peak stall)

- [ ] Add supporting components (copy from U_BEC_5V_1/2):
  - [ ] Inductor L4 (same as L1, L2: Würth 744314100 10µH >=6A)
  - [ ] Input capacitor (100µF/50V ceramic + 10µF/50V ceramic, standard bypass)
  - [ ] Output capacitors (47µF/10V ceramic, same as 5V BECs)
  - [ ] Feedback divider (same values as 5V BECs, tied to shared 5V reference)
  - [ ] Molex Nano-Fit connector, labeled "SERVO-5V" (distinct from 6V)

- [ ] Wire accordingly:
  ```
  VBAT (28V) ──→ FB_SERVO ──→ U_BEC_SERVO_5V.IN ──→ GND
                                      ↓
                                  L4, C_OUT
                                      ↓
                                  SERVO-5V connector (5V output)
                                      ↓
                                  Feedback divider → 5V reference
  ```

- [ ] Update title block: Change "Flight Engineer Rev R" to "Flight Engineer Rev S1"
  - Edit → Sheet Properties (Ctrl+Shift+P)
  - Title: "Flight Engineer Power Distribution Board Rev S1"
  - Date: 2026-07-18 (today)

- [ ] Run ERC:
  ```bash
  kicad-cli sch erc FlightEngineer.kicad_sch
  ```
  - Target: Same or fewer errors than before (no new regressions)

#### Task 3.B: Layout Flight Engineer PCB (move 6V→5V BEC footprints)
- [ ] Open `avionics/kicad/FlightEngineer/kicads/FlightEngineer.kicad_pcb` in KiCad

**DELETE (old 6V section footprints):**
- [ ] Delete footprints:
  - U_BEC_6V (TPS54540 package)
  - FB_6V (ferrite bead)
  - L3 (inductor)
  - C_BEC_SV_IN (capacitor)
  - Molex Nano-Fit 6V connector footprint

**ADD (new 5V servo section):**
- [ ] Duplicate footprints from Section D area (5V BECs):
  - [ ] Copy U_BEC_5V_2 footprint → U_BEC_SERVO_5V (TPS54620 in same location)
  - [ ] Copy L2 footprint → L4 (inductor)
  - [ ] Copy input/output capacitor footprints

- [ ] Place in Section E area (use old U_BEC_6V location as reference):
  - Maintain layout symmetry with Section D
  - Keep trace runs short (power integrity)
  - Feedback divider near inductor (minimize loop area)

**ROUTE:**
- [ ] Connect VBAT (28V bus) → FB_SERVO choke → U_BEC_SERVO_5V IN pad (trace: 1.0 mm wide)
- [ ] Connect U_BEC_SERVO_5V OUT pad → L4 → C_OUT (output caps)
- [ ] Connect output caps → SERVO-5V connector (trace: 0.6 mm wide)
- [ ] Feedback divider: feedback node → COMP, FB pads (0.2 mm traces)
- [ ] GND pour (In1.Cu plane) handles all return paths

- [ ] Run incremental DRC after each section:
  ```bash
  kicad-cli pcb drc --schematic-parity FlightEngineer.kicad_pcb
  ```

#### Task 3.C: Final DRC check
- [ ] Run full DRC:
  ```bash
  kicad-cli pcb drc --schematic-parity FlightEngineer.kicad_pcb
  ```
- [ ] Target: 0 hard violations (shorting, clearance, courtyard, solder mask)
- [ ] Accept: SOFT violations (silk, lib-footprint — pre-existing backlog)
- [ ] If new hard violations appear, diagnose and fix

#### Task 3.D: Generate Gerbers
- [ ] Run:
  ```bash
  python3 avionics/kicad/generate_gerbers.py flight_engineer
  ```
- [ ] Verify output in `avionics/kicad/gerbers/FlightEngineer-S1/`
- [ ] Inspect gerber files (same checklist as Commo 1.F + XO 2.F)

---

## Post-Completion Checklist

### Gerber Verification (All Three Boards)
- [ ] **Commo-S1/**: 10 files (.gbr, .drl, .gbrjob)
  - [ ] F_Cu, B_Cu: Traces/pads visible
  - [ ] F_Mask, B_Mask: Solder mask clearance correct
  - [ ] F_Silkscreen, B_Silkscreen: Text readable
  - [ ] Edge_Cuts: Closed board outline
  - [ ] Drill (.drl): Hole coordinates reasonable

- [ ] **CAPE-B-2-S1/**: Same checks as Commo
- [ ] **FlightEngineer-S1/**: Same checks as Commo

### Documentation Updates
- [ ] Update `avionics/rev-s1/WBS.md`: Check off all items
  - [ ] Commo: mark top-level item [x]
  - [ ] XO: mark top-level item [x]
  - [ ] Flight Engineer: mark top-level item [x]

- [ ] Update root `TODO.md`:
  - [ ] Remove 3 items from section 1.2b (now complete)
  - [ ] Sync with WBS.md (both should agree)

- [ ] Update board markdown files:
  - [ ] `avionics/kicad/Commo/Commo.md`: Update status to "Rev S1 complete, gerbers generated, ready for fabrication"
  - [ ] `avionics/kicad/XO/XO.md`: Update status to "Rev S1 complete, gerbers generated, ready for fabrication"
  - [ ] `avionics/kicad/FlightEngineer/FlightEngineer.md`: Update status to "Rev S1 complete, gerbers generated, ready for fabrication"

### Git Commit & PR
- [ ] Stage changes:
  ```bash
  git add -A avionics/kicad/Commo/kicads/*.kicad_* avionics/kicad/XO/kicads/*.kicad_* avionics/kicad/FlightEngineer/kicads/*.kicad_*
  git add avionics/kicad/gerbers/Commo-S1/ avionics/kicad/gerbers/CAPE-B-2-S1/ avionics/kicad/gerbers/FlightEngineer-S1/
  git add avionics/rev-s1/WBS.md TODO.md
  git add avionics/kicad/Commo/Commo.md avionics/kicad/XO/XO.md avionics/kicad/FlightEngineer/FlightEngineer.md
  ```

- [ ] Commit:
  ```bash
  git commit -m "Complete todo 1.2b: Commo/XO/Flight Engineer Rev S1 PCB redesigns

  - Commo Rev S1: Add LoRa (RFM95W), replace JST with P1+P2 sockets
    • Schematic reconciliation complete (gen_commo_sch.py)
    • PCB rework complete (mod_commo_pcb.py)
    • RSSI sub-circuit routing complete (route_commo_rssi.py)
    • All remaining nets routed; DRC 0 hard errors
    • Gerbers generated to avionics/kicad/gerbers/Commo-S1/

  - XO Rev S1: Remove LoRa, add P1/P2 passthrough rails
    • Schematic reconciliation complete (ref-designator remapping)
    • LoRa/SBUS/XCVR blocks removed from schematic
    • P1/P2 TOP passthrough sockets added
    • ERC 0 new errors; pre-existing 564 warnings documented
    • Gerbers generated to avionics/kicad/gerbers/CAPE-B-2-S1/

  - Flight Engineer Rev S1: Remove 6V BEC, add 5V servo output
    • Schematic: TPS54540 (6V BEC) removed, TPS54620 (5V servo BEC) added
    • PCB layout: 5V servo section routed; DRC 0 hard errors
    • Current budget verified: 2× DS3218MG (1.0A peak) << 3A rated output
    • Gerbers generated to avionics/kicad/gerbers/FlightEngineer-S1/

  All three boards ready for fabrication order.
  Closes todo 1.2b per avionics/rev-s1/WBS.md.

  Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
  Co-Authored-By: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP"
  ```

- [ ] Push:
  ```bash
  git push -u origin claude/todo-item-1-2b-e89qrb
  ```

- [ ] Create PR (if not already open):
  ```bash
  gh pr create --title "Complete todo 1.2b: PCB redesigns (Commo/XO/Flight Engineer Rev S1)" \
    --body "...see commit message above..."
  ```

### Sign-Off & Handoff
- [ ] Notify firmware team:
  - [ ] Commo PTT_N / RSSI_DCD presence-gated pinmux (Simon vs River nodes)
  - [ ] Flight Engineer 5V servo rail replacement (firmware mapping for servo outputs)

- [ ] Notify PCB fabrication vendor:
  - [ ] Provide gerbers from avionics/kicad/gerbers/{Commo-S1,CAPE-B-2-S1,FlightEngineer-S1}/
  - [ ] Specify: FR-4, 4-layer, ENIG finish, 1oz copper on signal layers
  - [ ] Quote for 5 units (prototype + spares)

---

## Quick Reference: Command Cheat Sheet

### KiCad CLI Quick Commands
```bash
# ERC on schematic
kicad-cli sch erc avionics/kicad/[Board]/kicads/[Board].kicad_sch

# DRC on PCB
kicad-cli pcb drc --schematic-parity avionics/kicad/[Board]/kicads/[Board].kicad_pcb

# Generate gerbers
python3 avionics/kicad/generate_gerbers.py [commo|xo|flight_engineer]

# Check impedance
python3 avionics/kicad/check_impedance.py
```

### KiCad Interactive Editor Shortcuts
```
Ctrl+F       Find component
Ctrl+H       Find & Replace (schematic symbols)
Ctrl+S       Save
Ctrl+Z       Undo
Ctrl+Shift+R Activate Push-Shove routing (PCB)
L            Toggle layer (PCB)
E            Rotate selected element
Delete       Delete selected element
```

### Python Scripting (For Automation)
```bash
# Run orchestration script
python3 avionics/kicad/complete_1_2b.py --board commo --verbose

# Run RSSI routing script
cd avionics/kicad/Commo && python3 scripts/route_commo_rssi.py all
cd avionics/kicad/Commo && python3 scripts/route_commo_rssi.py dcd  # RSSI_DCD only
```

---

## Estimated Timeline

| Phase | Task | Duration | Dependencies |
|-------|------|----------|--------------|
| 1 | Commo routing (13 nets + differential pairs) | 3–4 hours | None |
| 1 | Commo DRC & gerbers | 0.5 hours | Routing complete |
| 2 | XO schematic remap & cleanup | 1–2 hours | None (parallel to Phase 1) |
| 2 | XO ERC & gerbers | 0.5 hours | Schematic cleanup complete |
| 3 | Flight Engineer schematic edit | 1 hour | None (parallel to Phase 1–2) |
| 3 | Flight Engineer PCB layout | 1–2 hours | Schematic complete |
| 3 | Flight Engineer DRC & gerbers | 0.5 hours | PCB layout complete |
| Post | Documentation & commit | 0.5 hours | All gerbers complete |
| **Total** | | **8–12 hours** | |

---

## Known Blockers & Workarounds

| Blocker | Workaround |
|---------|-----------|
| RSSI_DCD routing too tight (GUI push-shove required) | Use KiCad push-shove, or route manually with B.Cu fallback |
| 13 nets unrouted (tight pockets) | Route incrementally; check DRC after each net |
| XO ref-mismatch (cannot auto-correct) | Use Find&Replace; verify ERC after each rename |
| Flight Engineer 5V servo placement (space constrained) | Reuse Section D footprint geometry; tight layout is acceptable |

---

## Success Criteria

**All three boards MUST satisfy:**

- [ ] **ERC:** 0 new errors (pre-existing warnings documented & accepted)
- [ ] **DRC:** 0 hard violations (shorts, clearance, courtyard, solder mask)
  - SOFT violations (silk, lib-footprint) are pre-existing backlog; acceptable
- [ ] **Gerbers:** 10 files per board (F_Cu, B_Cu, F_Mask, B_Mask, F_Silkscreen, B_Silkscreen, Edge_Cuts, In1_Cu, In2_Cu, drill .drl)
- [ ] **Schematic-PCB Parity:** Footprint count matches symbol count; all nets connected
- [ ] **Documentation:** Board `.md` files updated; WBS.md / TODO.md synchronized

**When all three complete → ready for fabrication order.**

---

*Checklist prepared: 2026-07-18 | For KiCad 9.0.2 December 2025 | CC BY 4.0*
