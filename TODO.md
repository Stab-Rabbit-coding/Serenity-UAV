# Serenity UAV — Work Breakdown Structure

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0  
**Last updated:** 2026-06-02  
**Current design revision:** Rev P (master) | **Build target:** 24-inch hull (REVN_BUILD_GUIDE_24IN.md)

---

## Quick-Reference: End State vs. Current State

| Domain | End State (Rev P) | Current Status |
|--------|-------------------|----------------|
| Hull | 609.6 mm PETG / PU foam / CF skeleton | SCAD sources complete; cargo section shell updated to Rev S (clamshell opening); 3 Rev-O-specific STLs not yet rendered |
| Nacelles | 2× 50mm tandem EDF, CG pivot Z=83mm, M=1.0 gear, iris nozzle | `nacelle_pod_50mm_tandem.scad` complete; Rev O stator shells (`_revo.stl`) NOT yet rendered |
| Rear propulsion | 120mm 6S EDF, 4-scoop radial intake, iris nozzle | `s_edf_120_motor_mount.stl` ✓, `s_edf_120_thrust_tube.stl` ✓; intake frame + plenum SCAD complete, STLs missing |
| Cargo bay | Clamshell doors + SG90 servos + DRV8833 + N20 winch + Dyneema + auto-latch + GPS ring + FPV bezel | ✓ All 13 cargo STLs generated (PR #21 + PR #22 2026-06-01); BOM updated bom_revP.json/csv; gondola shell open |
| PCBs | Cape-A-1, Cape-B-1 assembled; XCVR-49MHZ-1 fabricated | Cape-A/B KiCad files complete, gerbers stale; XCVR-49MHZ-1 Phase 1 complete (ICs selected 2026-05-31); Phase 2 schematic open |
| Firmware | 8-node cooperative flight, PID governor, OA, cargo, logging | serenity-cn Phase 6 ✓; serenity-fc Phase 6 stub only; all Phase 7 items open |
| Physical build | Airborne, autonomous, cargo-capable | Not started — awaiting STL exports, PCB fabrication |
| Regulatory | FAA Part 107, ICAO nav lights, FCC Part 95 | FAA registration placeholder; XCVR-49MHZ-1 pre-compliance pending |

---

## 1.0 — Design Artifacts (Pre-Fabrication)

Complete all items in this section before ordering PCBs or starting any physical build step.

### 1.1 — 3D Models: Rev O SCAD → STL Exports

All SCADs run on a host machine with OpenSCAD 2021.01+ or Blender 3.x+ (headless).
Output STLs go to `thingverse-serenity/files-hollowed-18in/`.

**Nacelle shells (Blender, Rev O geometry — must run on host machine):**

- [ ] **Rev O nacelle stator shells** — run `blender --background --python thingverse-serenity/blender_nacelle_revo.py` with `SWIRL_DIR=1` (port) and `SWIRL_DIR=-1` (stbd).
  - Output: `s_eng_left_stator_shell24_revo.stl`, `s_eng_right_stator_shell24_revo.stl`
  - Verify: Z-range 0–148.3 mm, bore ID 55.0–56.0 mm, 11 stator fins visible in Z=53–95 mm gap
  - **BLOCKS Phase 0 nacelle printing**

**Rear intake system (OpenSCAD):**

- [ ] **s_aft_edf_plenum.stl** — `openscad -o s_aft_edf_plenum.stl serenity/stl/s_aft_edf_plenum.scad`
  - Verify: 4 rectangular arms 65×60 mm, aft outlet 120 mm circular; no self-intersection
  - **BLOCKS Phase 4**

- [ ] **s_neck_intake_frame.stl** — `openscad -o s_neck_intake_frame.stl serenity/stl/s_neck_intake_frame.scad`
  - Verify: 4 registration tongues 5 mm depth; intake lips project 6 mm forward
  - Material: CF-PETG; **BLOCKS Phase 1 (intake frame installation)**

- [ ] **s_rear_neck_intake_shell24.stl** — `openscad -o ... serenity/stl/s_rear_neck_intake_shell24.scad`
  - Verify: 4 radial scoop windows present; NECK_X station ~310 mm; window alignment
  - **BLOCKS Phase 0 (print schedule)**

**Rev O gear train (OpenSCAD — all 5 parts, M=1.0):**

- [ ] **nacelle_sector_gear.stl** — `openscad -o ... serenity/stl/nacelle_sector_gear.scad`
  - Spec: R=22mm, 38T, 155° arc; fixed to tilt bracket
- [ ] **nacelle_pinion.stl** — `openscad -o ... serenity/stl/nacelle_pinion.scad`
  - Spec: N=12T, D-bore shaft (×4 total: drive pinion + crown pinion per nacelle)
- [ ] **nacelle_bevel_pair.stl** — `openscad -o ... serenity/stl/nacelle_bevel_pair.scad`
  - Spec: N=14T, 45° pitch cone, 1:1, 90° axis redirect
- [ ] **nacelle_bevel_housing.stl** — `openscad -o ... serenity/stl/nacelle_bevel_housing.scad`
  - Spec: CF-PETG, 24×14×20 mm housing block
- [ ] **nacelle_nozzle_iris.stl** — `openscad -o ... serenity/stl/nacelle_nozzle_iris.scad`
  - Spec: 50 mm iris — inner ring (M=1.0 rack), outer housing, 8-petal geometry

**Wing pylon (OpenSCAD — Rev O integrated design):**

- [ ] **s_wing_nacelle_pylon_revo.stl** — `openscad -o ... serenity/stl/s_wing_nacelle_pylon_revo.scad`
  - Verify WING_SLOT_W and WING_SLOT_H against `s_wings_both_shell24.stl` (caliper-measure from the mesh) before printing — estimated 50×40 mm at 2.197× Thingiverse scale
- [ ] **s_wings_s1223_revo.stl** — `openscad -o ... serenity/stl/s_wings_s1223_revo.scad`
  - Verify WING_CHORD_ROOT, WING_CHORD_TIP, WING_SEMI_SPAN, WING_SWEEP_LE against original STL before printing

**Canonical middle shell (OpenSCAD — belly restored, no belly scoop):**

- [ ] **s_middle_canonical_shell24.stl** — `openscad -o ... serenity/stl/s_middle_canonical_shell24.scad`
  - Note: NOT the same as `s_middle_shell24.stl` (which has the obsolete belly intake cut). This is the Rev N canonical belly.

**Rev O shell updates (sensor/antenna mounts from 2026-05-24):**

- [ ] **s_head_shell24.stl** — regenerate from `serenity/stl/s_head_shell24.scad` (dual VL53L5CX bosses, FPV mount, GPS dome, 49MHz post, SMA bulkheads added 2026-05-24). Verify all mount boss positions in slicer cross-section before printing.
- [ ] **s_cargo_sect_shell24.stl** — regenerate from `serenity/stl/s_cargo_sect_shell24.scad` (cargo nadir FPV mount added)
  - Both outputs go to `thingverse-serenity/files-hollowed-18in/`

**Remaining parts needing SCAD source creation then STL export:**

- [ ] **49MHz RCRS wire posts** — create `serenity/stl/s_rcrs49_wire_post.scad`: insulated PETG mast ~10 mm tall, 12×12 mm foot; generate both forward post (station ~120 mm, dorsal) and aft post (rear nozzle cone top)
  - **BLOCKS Phase 1 (antenna installation)**

- [ ] **Access panel frames A–F + lids (24" Rev N)** — verify `files-hollowed-18in/` frames are sized for the 24" hull (97×63 mm bay footprint per REVN_BUILD_GUIDE_24IN.md Phase 1). If no 24" version exists, create `serenity/stl/access_panels_24in.scad` with 6 frame + 6 lid profiles.
  - **BLOCKS Phase 1**

**Cargo handling equipment:**

- [x] **Mounting hardware — 8 STLs** generated by `serenity/stl/generate_cargo_mounts.py` (Python/trimesh/manifold3d). Output: `thingverse-serenity/files-hollowed-18in/cargo_*.stl` *(done 2026-05-30, PR #21)*
  - [x] cargo_winch_motor_mount (CF-PETG), cargo_winch_spool (PETG), cargo_door_servo_bracket (CF-PETG), cargo_release_servo_bracket (CF-PETG), cargo_drv8833_tray (PETG), cargo_cradle_autolatch (PETG), cargo_gps_retention_ring (PETG), cargo_fpv_bezel (PETG)

- [ ] **Cargo gondola shell** — create `serenity/stl/s_cargo_gondola_shell.scad`: 112×85×22 mm belly pod, 4× M3 hard point pattern, 18 mm protrusion below hull line
- [x] **Clamshell door halves** — `cargo_door_port.stl` + `cargo_door_stbd.stl` generated by
  `serenity/stl/generate_cargo_doors.py` (trimesh/scipy bilinear interpolation from Rev-O shell
  belly faces). Both watertight; 8-barrel piano hinge, 3 mm CF rod, 3.15 mm bore. *(done 2026-06-01)*
- [x] **`s_cargo_sect_shell24.scad` Rev S** — belly opening (100×9×165 mm), 2× hinge-pin blocks
  (3.3 mm bore + M3 grub-screw tap), 2× SG90 servo mounting pads (4× M2.5 pilots each), 4×
  latch-catch lips (Z=42/122 mm at each X frame edge). *(done 2026-06-01)*
- [ ] Add motor-mount and DRV8833-tray boss locations to `s_cargo_sect_shell24.scad` interior
  drawing notes (Phase 1 pre-pour checklist reference).
- [ ] Add SG90 bell-crank boss to inner face of each door panel for pushrod attachment.
  - Export gondola shell to `thingverse-serenity/files-hollowed-18in/`
  - **BLOCKS Phase 8**

**Combined airframe model (visual verification):**

- [ ] **Combine all airframe STLs** into a single assembly model including the 1.25× scaled nacelles, all EDF tubes, cargo bay clamshells, antenna bosses, sensor cutouts, access panels, landing legs, and feet. Render SVGs from all 6 cardinal directions (top, bottom, front, rear, port, stbd) and all 8 isometric views (8 corners). Save renders to `serenity/diagrams/`.
- [ ] **Exploded view SVG — printed parts only** (all printed components labelled and exploded from assembly position)
- [ ] **Exploded view SVG — full build** (all components: PCBs, SBCs, motors, ESCs, wires, sensors, antennas, hardware)

---

### 1.2 — PCB Design: Cape-A-1 and Cape-B-1

- [ ] **Regenerate Cape-A-1 gerbers** — `.kicad_pcb` modified 2026-05-23 (tamper-mesh commit); gerbers in `serenity/kicad/gerbers/CAPE-A-1/` are from 2026-05-22.
  - Open in KiCad → Plot → Gerbers; overwrite files in `serenity/kicad/gerbers/CAPE-A-1/`; re-export drill files.
  - Run DRC to zero errors before plotting.
  - **BLOCKS Phase 6 fab order**

- [ ] **Regenerate Cape-B-1 gerbers** — same timestamp issue. `serenity/kicad/gerbers/CAPE-B-1/` files are from 2026-05-22.
  - **BLOCKS Phase 6 fab order**

---

### 1.3 — PCB Design: XCVR-49MHZ-1 (49 MHz AX.25 RCRS Transceiver)

Stub KiCad project at `serenity/kicad/XCVR-49MHZ-1.*`. Design notes in `serenity/kicad/XCVR-49MHZ-1.md`.
All Phase 1–3 items must be sequentially complete. Phase 4 verification runs in parallel with Phase 3.

**Phase 1 — IC Selection (gates all downstream work):**

- [x] **Resolve DDS choice** — **Si5351A-B-GT selected** (Silicon Labs, MSOP-10) + EPSON TG2520SMN 25 MHz ±0.5 ppm TCXO. I²C direct to 49 MHz; firmware driver already written (`si5351.c`); < ±1 ppm system stability, meeting Part 95 ±0.005% with > 25× margin. AD9833 eliminated (max 12.5 MHz; required ×4 external PLL). *(decided 2026-05-31)*
- [x] **Evaluate PA options** — **Two-stage discrete BJT selected**: MMBT2222A (SOT-23, driver) + 2N3866 (SOT-39, final). Class-A/AB; +5 V supply direct; ≈ 100 mW ERP; ≈ $1.60 BOM; ≥ 40 dBc harmonic suppression via FL1 LPF (SPICE verify Phase 4). RA07H4047M eliminated (requires 7.2–13.6 V; needs boost converter). *(decided 2026-05-31)*
- [x] **Confirm TCM3105 availability** — TCM3105 confirmed discontinued (TI); no in-production drop-in. **Software Bell 202 AFSK selected**: AM6254 Cape-B MCU generates/decodes audio; TX via MCP4921 SPI 12-bit DAC; RX via LM393 comparator + passive RC bandpass filter. *(decided 2026-05-31)*

**Phase 2 — Schematic:**

- [ ] **U1 DDS sub-circuit** — power decoupling, SPI/I²C to J1, frequency configuration load sequence; channel select (49.830–49.890 MHz) software-configurable.
- [ ] **U2 AFSK modem sub-circuit** — software Bell 202 on Cape-B MCU; MCP4921 SPI 12-bit DAC (TX audio to U3 modulator); LM393 comparator + passive RC bandpass filter (RX demod); UART to J1 pins 3/4; LM393 output as CD (carrier detect) to Cape-B GPIO.
- [ ] **U3 PA + modulator sub-circuit** — DDS carrier in, AFSK audio in, RF out to FL1; PTT_N gate; bias network and 50 Ω output matching.
- [ ] **FL1 5-element Chebyshev LPF** — calculate values for fc=75 MHz, 50 Ω; verify −40 dBc at 98 MHz (2nd harmonic of 49 MHz). Simulate in QUCS-S before committing values.
- [ ] **U4 LNA + envelope detector RX chain** — MGA-82563 input, gain/NF budget, RSSI voltage divider to J1 pin 6.
- [ ] **U5 TX/RX switch** — PE4259-63 SPDT; PTT_N control; isolation must protect LNA during TX (PE4259 ≥35 dB TX→RX isolation).
- [ ] **U6 3.3 V LDO and power tree** — AMS1117-3.3 from +5V; bulk decoupling; ferrite bead between digital and RF sections on +5V.
- [ ] **J1 and J2 connectors** with all pin labels.
- [ ] **Run ERC; resolve all errors.**

**Phase 3 — PCB Layout:**

- [ ] **Set up layer stack** — 4L: F.Cu signal / In1.Cu GND / In2.Cu +3V3 / B.Cu signal; 1.6 mm total thickness (JLCPCB standard).
- [ ] **Place components** — RF section (right 25 mm): U1, U3, U4, U5, FL1, J2; digital section (left 30 mm): U2, U6, J1.
- [ ] **Route RF path** — 50 Ω microstrip, 2.75 mm wide on F.Cu (Z₀ = 52.26 Ω confirmed by `check_impedance.py` 2026-05-30); continuous GND stitching vias; no 90° bends.
- [ ] **Route digital signals** — UART traces ≥5 mm from RF section boundary; ferrite bead (BLM18PG221SN1D or equiv.) on +5V at boundary.
- [ ] **LPF shield keep-out** — mark Coilcraft SER inductor cans on F.Fab; orient perpendicular; verify no mutual coupling.
- [ ] **Thermal vias under U3 PA** — exposed pad to In1.Cu GND; minimum 9× 0.3 mm vias; verify <85°C case at 100 mW continuous TX.
- [ ] **SMA J2 edge placement** — flush to right board edge; 3 mm Cu keep-out either side of feed line from edge to U5.
- [ ] **Run DRC; resolve all errors.**

**Phase 4 — Verification and Compliance:**

- [ ] **SPICE/QUCS simulation of FL1 LPF** — verify harmonic suppression meets 47 CFR 95.655 before board spin.
- [x] **50 Ω trace impedance check** — Z₀ = 52.26 Ω for W=2.75 mm, H=1.6 mm, εr=4.5, T=35 µm → **PASS** [45–55 Ω]. *(done 2026-05-30 — serenity/kicad/check_impedance.py)*
- [ ] **FCC Part 95 pre-compliance checklist** — document: center frequency accuracy, ERP calculation, harmonic levels, labeling requirements (47 CFR 95.603 FCC ID block on silkscreen).

**Phase 5 — Production Files:**

- [ ] **Export gerbers** to `serenity/kicad/gerbers/XCVR-49MHZ-1/`
- [ ] **Export BOM** — add XCVR-49MHZ-1 line items to `serenity/docs/bom_revN.csv` and `bom_revN.json`
- [x] **Update `PROJECT_INDEX.md`** to list XCVR-49MHZ-1. *(done 2026-05-25)*

---

### 1.4 — Documentation

- [x] **`serenity-rev-p.jsx`** — comprehensive 11-tab standalone Rev P specification created: Overview, Airframe, Propulsion, Avionics, Comms, Cargo, Security, Regulatory, BOM, Files, Build Status. Supersedes serenity-rev-o.jsx as current spec. *(done 2026-06-01)*
- [x] **`bom_revP.json` + `bom_revP.csv`** — full Rev P BOM created: all Rev O items retained + 10 new cargo printed parts + SERVO-CARGO, DRV8833-CARGO, DYNEEMA-SK75, FOAM-GASKET-CARGO; cargo section expanded; totals updated (5 servos, ~$1,905 est.). *(done 2026-06-01)*
- [x] **`README.md`** — updated to Revision P, June 2026; propulsion section updated to Rev O/P baseline; avionics section updated to PB2-I description; cargo section updated to Rev P complete spec. *(done 2026-06-01)*
- [x] **`PROJECT_INDEX.md`** — updated to add serenity-rev-p.jsx and bom_revP entries; Rev P marked as current master. *(done 2026-06-01)*
- [ ] **Update PHASED_BUILD_GUIDE.md** from Rev M 18-inch to Rev P 24-inch specifications (hull 609.6 mm, 50mm EDFs, 4-scoop radial intake, M=1.0 gears, Rev O pivot Z=83mm, MF104ZZ bearings, Rev P cargo system).
- [ ] **Sync `bom_revO.json` ↔ `bom_revO.csv`** — verify all XCVR-49MHZ-1 BOM items (Phase 5 above) are reflected in both files once XCVR-49MHZ-1 Phase 5 is complete.

---

## 2.0 — Procurement (Before Physical Build)

Order components after all Phase 0 STLs are confirmed printable in slicer. Long-lead items should be ordered concurrently with PCB fabrication.

### 2.1 — Filament and CF Stock (needed for Phase 0)

| Item | Qty | Notes |
|------|-----|-------|
| PETG filament | ~1,200 g | Hull sections, access panels, nozzle parts, cargo gondola |
| CF-PETG filament | ~500 g | Nacelle pods, tilt brackets, pylon, intake frame — hardened-steel nozzle required |
| TPU 95A filament | ~200 g | Landing skid feet — direct-drive extruder required |
| CF flat bar 6×3mm | ~700 mm | Keel 620 mm + 80 mm ring frame offcuts |
| CF tube 12mm OD / 1.5mm wall | ~850 mm | Wing spars 2×380 mm + 90 mm scrap |
| CF solid rod 4mm OD | ~300 mm | Pivot rods (2× nacelle) per pivot housing drawing |
| CF plate 2mm | 250×150 mm | Ring frames (5 stations per drawing) |

### 2.2 — Structural Hardware (Phase 1)

| Item | Qty | Notes |
|------|-----|-------|
| West System 105/206 epoxy | 1 kit | Keel + spar bonding; structural joints |
| 5-minute epoxy syringe 25mL | 3× | Access frames, sensor mounts |
| X-30 PU foam 2-part | ~600 mL | 2 lb/ft³, 4× expansion, 2-min pot life |
| EPS blue foam board 25mm | 500×250 mm | Void formers A–E; Owens Corning Foamular 150 |
| Johnson's Paste Wax | 1 tin | Void former release agent (2 coats) |
| 3M 4016 closed-cell gasket tape | 1 roll | Access panel frame lips |
| PTFE tube 5mm OD × 3mm ID | 6 m | 8 conduits (CAN FD, RS-485, 1553A, 1553B, ETH×2, SERVO-PWR, MAIN-PWR) |
| M2.5 nylon hex standoff 6mm | 16× | Cape-B floor mounts (4 per bay × 4 bays) |
| M2.5 nylon hex standoff 20mm | 16× | Cape-A inter-cape spacing |
| M2.5 × 8mm SS button screws | 64× | Standoff attachment + panel B/E fasteners |
| M3 heat-set threaded inserts | 4× | Cargo gondola belly hard points |
| N42 neodymium disc magnet 6×2mm | 8× | Panel D (4 in frame + 4 in lid) |
| SMA panel-mount bulkhead | 3× | SiK 915MHz (belly) + LoRa 915MHz (belly) + WiFi (dorsal fwd) |
| 0.3mm stainless wire or 22AWG enamelled Cu | ~500 mm | 49MHz RCRS top wire |
| Ceramic bead insulator 3mm ID | 1× | Aft end of 49MHz wire (insulated/open end) |

### 2.3 — Propulsion System (Phases 2–4)

| Item | Qty | Approx. Cost | Notes |
|------|-----|-------------|-------|
| 50mm EDF @ 6S (budget tier) | 4× | ~$25–40ea | 2 per nacelle, tandem; verify OD fits 55–56mm ID bore |
| 40A 6S BLHeli32 BDSHOT ESC | 4× | ~$18–25ea | 1 per nacelle EDF |
| 120mm 6S EDF | 1× | ~$60–80 | Fuselage rear; single final motor |
| 80A 6S BLHeli32 ESC | 1× | ~$25–35 | Fuselage EDF |
| Digital tilt servo ≥25 kg·cm @ 6V, metal gear | 2× | ~$20–30ea | Nacelle tilt; prefer 30+ kg·cm |
| SG90 micro servo | 3× | ~$3ea | Nacelle nozzle ×2 (redundant) + rear nozzle ×1 |
| MF104ZZ flanged bearing 4×10×4mm | 4× | ~$8 total | 2 per nacelle pivot |
| 4mm OD CF rod (pivot) | 2× cut lengths | — | From 2.3 CF stock above |
| Steel pushrod 2mm OD × ~60mm | 2× | ~$3 total | Longitudinal nozzle shaft per nacelle |
| Steel pushrod 2mm, Z-bend ends | 2× | ~$4 total | Tilt servo pushrod |
| M2 clevis links | 4× | ~$3 total | Servo-to-pushrod |
| 0.8mm piano wire | ~600 mm | ~$3 | Nozzle iris petal link rings |
| 3mm SS hinge pins | 16× | ~$4 total | 8 per nacelle iris nozzle |
| WS2812B LED ring (50mm) | 2× | ~$6 total | Nacelle duct exit |
| WS2812C-2020 addressable LED | 6× | ~$6 total | Nav lights |
| XT90 PDB, 4× XT30 outputs | 1× | ~$12 | Power distribution |
| XT90 battery pigtail | 1× | ~$5 | Battery lead |
| 5V 5A switching BEC | 1× | ~$8 | Avionics power rail |
| 14AWG silicone wire | 1 m | ~$6 | Main bus |
| 16AWG silicone wire | 0.5 m | ~$4 | ESC signal + fuselage taps |
| 6S 4000mAh LiPo battery | 1× | ~$55–70 | Phase 6 first flight |

### 2.4 — Avionics (Phase 6 — 4-node minimum viable)

| Item | Qty | Unit Cost | Total | Notes |
|------|-----|----------|-------|-------|
| PocketBeagle 2 Industrial (AM6254) | 4× | $51.03 | ~$204 | DK 2820-100003007-ND |
| Cape-A PCB (JLCPCB assembled) | 2× | ~$42 | ~$84 | FC nodes (Cape-A-1 gerbers) |
| Cape-B PCB (JLCPCB assembled) | 2× | ~$80 | ~$160 | CN nodes (Cape-B-1 gerbers) |
| XCVR-49MHZ-1 PCB (JLCPCB assembled) | 2× | ~$20 | ~$40 | RCRS sub-module; requires completed design |
| SiK 915MHz ground station radio | 1× | ~$15 | ~$15 | MAVLink GCS link |
| microSD 64GB (log, write-blocked) | 2× | ~$10 | ~$20 | CN1-LOG, CN2-LOG |
| JST-GH cables: CAN 4-pin, RS-485 4-pin, ETH 8-pin, 1553 shielded pair | assorted | — | ~$15 | |
| USB-UART adapter (CP2102) | 1× | ~$8 | ~$8 | Debug console (one-time tool) |
| 3M double-sided foam tape | 1× | ~$5 | ~$5 | ESC and node mounting |
| Zip ties 100mm + 200mm | 1 bag | ~$4 | ~$4 | Wire management |

### 2.5 — Avionics (Phase 7 — remaining 4 nodes + ToF arrays)

| Item | Qty | Approx. Cost | Notes |
|------|-----|-------------|-------|
| PocketBeagle 2 Industrial (AM6254) | 4× | ~$204 | CN3, FC3, CN4, FC4 |
| Cape-A PCB (JLCPCB assembled) | 2× | ~$84 | FC3, FC4 |
| Cape-B PCB (JLCPCB assembled) | 2× | ~$160 | CN3, CN4 |
| XCVR-49MHZ-1 PCB (assembled) | 2× | ~$40 | CN3, CN4 |
| microSD 64GB (log) | 2× | ~$20 | CN3-LOG, CN4-LOG |
| VL53L5CX 8×8 ToF sensor | 12× | ~$84 | Dual OA arrays |
| TCA9548A 8-ch I²C multiplexer | 2× | ~$3 | One per array host |
| MCP23008 8-port I²C GPIO expander | 2× | ~$2.40 | XSHUT control |
| JST-SH1.0 4-wire sensor cable 300mm | 12× | ~$12 | ToF sensor leads |
| 5mm PMMA disc 0.5mm thick | 12× | ~$6 | ToF aperture covers |
| UV adhesive | 1× | ~$6 | ToF aperture seal |
| JST-GH cables (remaining bus segments) | assorted | ~$20 | Ring completion |

### 2.6 — Cargo System (Phase 8)

| Item | Qty | Approx. Cost | Notes |
|------|-----|-------------|-------|
| N20 DC motor 6V 300:1 | 1× | ~$8 | Winch drive |
| DRV8833 dual H-bridge driver | 1× | ~$2 | |
| SG90 servo | 2× | ~$6 | Door actuator + payload release |
| Dyneema SK75 0.5mm braid | 2 m | ~$4 | Winch line |
| 3mm CF rod | ~60 mm | — | Clamshell door hinge pin |
| Closed-cell foam gasket tape | — | — | Gondola-to-hull perimeter seal |

---

## 3.0 — Physical Build

**Dependency:** All items in Section 1.0 (STL exports) must be complete before Phase 0.  
**PCB fab lead time:** ~7–14 days for JLCPCB assembled boards — order after 1.2 gerber regen and 1.3 Phase 5 are complete; boards arrive during physical Phases 0–5.

### Phase 0 — Print All Parts + CF Cuts

**Goal:** Every printed part complete and dry-fitted before first epoxy joint.

**Printer setup:**
- [ ] Install hardened-steel nozzle (CF-PETG abrades brass)
- [ ] Calibrate E-steps and Pressure Advance for each filament
- [ ] Dry all filament 6 h at 65°C before printing

**Print schedule (ordered to minimize reprints):**

| Part | Material | Layer | Infill | Qty |
|------|----------|-------|--------|-----|
| s_feet_x_4_scaled24.stl | TPU 95A | 0.25mm | 40% | 1 set |
| s_legs_scaled24.stl | CF-PETG | 0.15mm | 30% | 1 |
| s_head_shell24.stl | PETG | 0.20mm | 8% gyroid | 1 |
| s_middle_canonical_shell24.stl | PETG | 0.20mm | 8% gyroid | 1 |
| s_cargo_sect_shell24.stl | PETG | 0.20mm | 8% gyroid | 1 |
| s_rear_neck_intake_shell24.stl | PETG | 0.20mm | 8% gyroid | 1 |
| s_neck_intake_frame.stl | CF-PETG | 0.15mm | 40% gyroid, 4 walls | 1 |
| s_aft_edf_plenum.stl | PETG | 0.20mm | 20% gyroid | 1 |
| s_wings_s1223_revo.stl | PETG | 0.20mm | 8% gyroid | 1 |
| s_eng_left_stator_shell24_revo.stl | CF-PETG | 0.15mm | 25% gyroid, 4 walls | 1 |
| s_eng_right_stator_shell24_revo.stl | CF-PETG | 0.15mm | 25% gyroid, 4 walls | 1 |
| s_eng_piv_outer_scaled24.stl | CF-PETG | 0.15mm | 40%, 4 walls | 2 |
| s_eng_piv_pins_scaled24.stl | CF-PETG | 0.15mm | 40% solid, 4 walls | 2 |
| s_pivot_arm_a_scaled24.stl | CF-PETG | 0.15mm | 40%, 4 walls | 2 |
| s_eng_pistons_scaled24.stl | PETG | 0.20mm | 20% gyroid | 2 |
| s_wing_nacelle_pylon_revo.stl | CF-PETG | 0.15mm | 40%, 4 walls | 2 |
| nacelle_nozzle_petal.stl | PETG + translucent-blue inner | 0.20mm | 20% gyroid | 16 |
| nacelle_nozzle_ring.stl | CF-PETG | 0.15mm | 40% | 2 |
| nacelle_nozzle_iris.stl | PETG | 0.12mm | 40% | 2 |
| rear_nozzle_petal.stl | PETG + translucent-blue | 0.20mm | 20% gyroid | 8 |
| rear_nozzle_frame.stl | CF-PETG | 0.15mm | 30% | 1 |
| nacelle_sector_gear.stl | CF-PETG | 0.12mm | 40%, 4 walls | 2 |
| nacelle_pinion.stl | PETG or resin | 0.12mm | 40% | 4 |
| nacelle_bevel_pair.stl | PETG or resin | 0.12mm | 40% | 2 sets |
| nacelle_bevel_housing.stl | CF-PETG | 0.15mm | 40% | 2 |
| s_rcrs49_wire_post.stl | PETG | 0.20mm | 100% | 2 |
| Access panel frames A–F + lids | PETG | 0.20mm | 100% | 1 set |
| s_cargo_gondola_shell.stl | PETG | 0.20mm | 15% gyroid | 1 |
| cargo_door_port.stl | CF-PETG | 0.15mm | 40%, 4 walls | 1 | Generated (PR #22) — reprint if hinge changes |
| cargo_door_stbd.stl | CF-PETG | 0.15mm | 40%, 4 walls | 1 | Generated (PR #22) — reprint if hinge changes |
| cargo_cradle_autolatch.stl | PETG | 0.20mm | 30% | 1 | Already generated (PR #21) — reprint if dimensions change |
| cargo_winch_spool.stl | PETG | 0.20mm | 40% | 1 | Already generated (PR #21) — reprint if dimensions change |

**CF cuts:**

| Part | Material | Dimension | Notes |
|------|----------|-----------|-------|
| Keel | CF flat bar 6×3mm | 620 mm | Mark datums at 91, 165, 251, 320, 388mm from nose |
| Wing spars | CF tube 12mm OD / 1.5mm wall | 2× 380 mm | Sand spar ends to fit wing-root pockets |
| Pivot rods | CF solid rod 4mm OD | 2× cut per pivot housing drawing | Deburr; press-fit into MF104ZZ bearings |
| Ring frames | CF plate 2mm | 5 profiles per station drawing | Fit to keel slot-notches |

**Phase 0 checks:**
- [ ] Nacelle bore caliper: 55.0–56.0 mm ID at Z=10 mm and Z=80 mm
- [ ] Stator fins visible in Z=53–95 mm gap (between the two EDF seats)
- [ ] Hub bore clear at stator: 16 mm ID minimum (motor leads)
- [ ] Sector gear ↔ pinion dry-mesh: 0.1–0.2 mm backlash
- [ ] Iris nozzle ring fits flush on nacelle exit; petals hinge freely on 3mm pins
- [ ] 4mm CF pivot rod slides through pivot housing with MF104ZZ bearings seated
- [ ] All access panel lids flush ±0.2 mm in frames
- [ ] Keel dry-fits through all hull sections without force

---

### Phase 1 — Hull Structure + All Future Provisions

**Goal:** Structurally complete hull, every conduit/standoff/void former/sensor mount installed — ready for foam pour.

> ⚠ **Point of no return.** Complete all sub-steps before mixing foam (Step 13). Nothing can be added after foam cures.

- [ ] Epoxy keel through all hull sections; cure 2h. Datum marks at 91, 165, 251, 320, 388mm.
- [ ] Bond ring frames at all 5 station notches; cure 1h.
- [ ] Bond access panel frames A–F into hull sections (5-min epoxy, 30 min cure per phase guide table).
- [ ] Install M2.5 nylon standoffs in bays A, B, D, E (floor 6mm + inter-cape 20mm per bay).
- [ ] Bond wing spar pocket inserts at wing root stations, both sides.
- [ ] Bond tilt servo mount brackets at wing root bay interior (one per nacelle tilt servo).
- [ ] Install M3 heat-set inserts ×4 at belly cargo hard-point locations.
- [ ] Install SMA bulkheads: belly port (SiK 915MHz, X≈260mm), belly stbd (LoRa, X≈260mm), dorsal (WiFi, X≈140mm).
- [ ] Install 49MHz RCRS wire posts: forward (dorsal, X≈120mm, bonded with 5-min epoxy) + aft (top of rear nozzle frame, bonded after Phase 4).
- [ ] String 49MHz top wire (0.3mm SS wire or 22AWG enamelled Cu, ~470mm) from forward post to aft post with ~20g tension; CF keel connected to RCRS-49 GND as counterpoise.
- [ ] Install 12× VL53L5CX flush-mount PETG frames (6.5mm hull cutouts); apply 0.5mm PMMA disc over each aperture with UV adhesive.
- [ ] Feed 8× PTFE conduits nose-to-tail; thread pull strings through each immediately; label both ends.
- [ ] Install EPS void formers (waxed 2×) in bays A–E; verify pull strings clear voids.
- [ ] Full dry-fit: all 8 pull strings accessible, standoffs clear, void formers sealed, SMA bulkheads installed.
- [ ] Foam pour: X-30 PU foam, 3 shots aft→fwd, ≤60 mL per batch; cure 24h per zone. **Do NOT foam nacelle bays, pivot housing, or access panel bays.**
- [ ] Remove EPS void formers; IPA wipe bay walls; verify foam not in conduit runs.
- [ ] Bond cockpit cap (verify cockpit bay wires and GPS coax accessible first).

**Phase 1 checks:**
- [ ] Hull rigid — no flex when held at nose and tail
- [ ] All 8 pull strings accessible at both ends
- [ ] All standoffs in place; screws start freely
- [ ] Foam not in nacelle mounting bay, pivot housing, or panel bays
- [ ] All 6 access panel lids flush ±0.2 mm; latches/magnets engage

---

### Phase 2 — Nacelle Assembly

**Goal:** Both nacelles fully assembled — EDFs installed, stator integral, iris nozzle fitted, gear linkage dry-meshed.

**2A — EDF installation (port first, then starboard):**
- [ ] Test EDF rotation direction on bench before installation: port = CW from intake; stbd = CCW from intake. Swap any two motor phase wires to reverse.
- [ ] Install EDF2 (aft/downstream) from nozzle end; seat at Z=5mm shoulder; epoxy 3 dabs at Z=50mm stator shoulder; route leads through hub bore.
- [ ] Install EDF1 (fore/upstream) from intake end; seat at Z=76mm; verify stator fins clear in Z=53–73mm gap; epoxy 3 dabs at Z=76mm shoulder.
- [ ] ESC pair: route to fuselage bay via spar conduit (ESC heat must NOT be trapped in nacelle bore).
- [ ] Cure 2h before proceeding.
- [ ] Repeat for stbd nacelle (opposite rotation direction).

**2B — Nozzle iris assembly (per nacelle):**
- [ ] Press nacelle_nozzle_ring.stl onto nozzle exit face; confirm flush.
- [ ] Install nozzle inner ring (rack, R=28mm) inside base ring.
- [ ] Bend 0.8mm piano wire link ring through all 8 petal link holes.
- [ ] Install 8 petals on 3mm hinge pins in base ring lugs.
- [ ] Dry-test: manually rotate inner ring — petals open smoothly 0°→75°, no binding.
- [ ] Install WS2812B LED ring at duct exit lip; route 3-wire lead through hub bore.

**2C — Gear linkage (per nacelle):**
- [ ] Mount sector gear to tilt bracket (FIXED — does not rotate with nacelle).
- [ ] Mount drive pinion on nacelle outer shell at pivot axis; mesh with sector gear; set backlash 0.1–0.2mm.
- [ ] Install bevel gear pair in nacelle body (nacelle-axis → longitudinal axis redirect).
- [ ] Thread 2mm steel longitudinal shaft through nacelle wall channel toward nozzle end.
- [ ] Mount crown pinion on shaft at nozzle end; mesh with nozzle inner ring rack; set backlash 0.1–0.2mm.
- [ ] **Full sweep test:** rotate nacelle 0°→90°; verify nozzle inner ring rotates ~71°; petals open fully. Verify nozzle inner ring hard stop prevents over-drive at >90°.
- [ ] Confirm petal closed position matches nacelle hull profile at 0°.

**Phase 2 checks:**
- [ ] Port nacelle EDF rotation: CW from intake; stbd: CCW from intake
- [ ] Stator fins visible and clear in Z=53–73mm gap on each nacelle
- [ ] Nozzle iris opens/closes smoothly through full nacelle sweep
- [ ] Petal closed: hull-match at 0°; petal open: all 8 even at 90°
- [ ] LED ring installed and wired

---

### Phase 3 — Tilt Mechanism

**Goal:** Both nacelles mounted on fuselage, pivot freely on MF104ZZ bearings, tilt driven by fuselage-mounted servos with hard stops.

- [ ] Press MF104ZZ bearings into pivot housing bores (both ends); flush ±0.2mm.
- [ ] Insert 4mm CF pivot rod through wing spar pocket + pivot housing bearings (rod is FIXED to fuselage; nacelle rotates on it).
- [ ] Slide nacelle pivot housing onto pivot rod; verify <0.5mm axial play.
- [ ] Install tilt servos in fuselage servo mount bracket at wing root bay.
- [ ] Connect pushrods (servo arm → pivot arm): servo 0° = nacelle 0° (cruise), servo ~125° = nacelle 90° (hover), servo ~170° = nacelle 120° (backing).
- [ ] Install CF-PETG hard stop blocks; bond at −5° stop and 140° stop positions.
- [ ] Servo calibration: set FC software travel limits at −5° and 140°; verify both nacelles reach 90° simultaneously.

**Phase 3 checks:**
- [ ] Both nacelles rotate freely on bearings — no grinding, no wobble
- [ ] Hard stops engage at −5° and 140° (servo stalls, does not strip)
- [ ] Nozzle opens/closes correctly via gear linkage through sweep (from Phase 2)
- [ ] Sector gear does NOT rotate with nacelle
- [ ] Both nacelles synchronise to within 2° at 0° and 90°

---

### Phase 4 — Rear EDF + Radial Intake + Nozzle

**Goal:** CF-PETG intake frame and PETG plenum installed; 120mm EDF mounted inside engine bell; rear nozzle operational.

**4A — Intake frame:**
- [ ] Dry-fit `s_neck_intake_frame.stl` into 4 scoop windows; registration tongues insert with ~0.2mm clearance (sand if tight).
- [ ] Verify aerodynamic orientation: intake lips face forward (+X).
- [ ] Apply structural epoxy to tongues + shoulder flanges; press frame into position; clamp; cure 24h.
- [ ] Fillet all gaps between flange and hull; cure 2h.

**4B — Plenum manifold:**
- [ ] Dry-fit `s_aft_edf_plenum.stl`; verify arm alignment and 120mm outlet centred.
- [ ] Bond plenum forward arms to intake frame exits; fillet joints; cure 2h.
- [ ] Pressure-test: seal EDF face with tape; cover 3 of 4 scoops; shop-vac at 4th — confirm draft at outlet, no joint leakage.

**4C — 120mm EDF:**
- [ ] Bench-test 120mm EDF (correct rotation, no vibration).
- [ ] Install EDF retaining ring at station ~430mm inside Panel F; bond; cure 1h.
- [ ] Seat EDF in plenum 120mm outlet; press forward to retaining lip; bond with 4 dabs slow-cure epoxy.
- [ ] Route motor leads through Panel F to 80A ESC; route signal lead forward via MAIN-PWR conduit to Bay B (FC2 PRU Ch.2).
- [ ] Install 80A ESC in Panel F bay; foam tape + cable tie.
- [ ] Cure 2h before applying thrust.
- [ ] Install aft 49MHz wire post on top of rear nozzle frame (bonded with 5-min epoxy); string 49MHz top wire.

**4D — Rear nozzle:**
- [ ] Press `rear_nozzle_frame.stl` onto 120mm EDF duct exit (Panel F aft end).
- [ ] Install 8 rear nozzle petals on 3mm hinge pins; install piano wire link ring.
- [ ] Install SG90 rear nozzle servo inside Panel F; pushrod to nozzle inner ring.
- [ ] Calibrate: servo 0° = petals closed (hull-matched bell); servo ~90° = petals fully open.
- [ ] Install WS2812B LED ring at rear duct exit lip.

**Phase 4 checks:**
- [ ] Intake frame tongues fully seated in all 4 scoop windows
- [ ] Plenum pressure-test passed
- [ ] EDF seated at station ~430mm, centreline ±2mm
- [ ] EDF rotation correct before sealing
- [ ] 80A ESC installed; signal routed to FC2
- [ ] Rear nozzle 8 petals open/close evenly without binding
- [ ] Rear nozzle servo calibrated

---

### Phase 5 — Hull Foam Pour + Close-up

**Goal:** Structural foam cured; all void formers removed; hull rigid.

**Pre-pour final checklist:**
- [ ] All PTFE conduits routed — pull strings accessible at both ends
- [ ] All bay standoffs installed
- [ ] Cargo hard points installed
- [ ] SMA bulkheads installed and dusted
- [ ] EPS void formers waxed (2 coats) and seated
- [ ] Nacelle bays and pivot housings masked OFF
- [ ] Servo mount brackets clear of foam path

**Pour sequence:**
- [ ] Mix X-30 per manufacturer (2:1 ratio by volume, 2-min pot life, 4× expansion). Pour in 3 shots: aft bay → mid bays (D+C) → forward bays (B+A). Allow 24h full cure before next shot.
- [ ] After full cure: remove EPS void formers; IPA wipe bay walls; verify foam did not intrude into panel bays, cargo bay, or conduit runs.
- [ ] Pull all 8 pull strings — verify still move freely.
- [ ] Install all 6 access panel lids; verify flush fit.

---

### Phase 6 — Minimum Viable Flyer ★ FIRST FLIGHT

**Goal:** CN1+FC1 (Bay A) and CN2+FC2 (Bay B) installed and operational — first flight achieved.

**Dependency:** Cape-A (×2) and Cape-B (×2) PCB assemblies received from JLCPCB.

**Power system:**
- [ ] Mount XT90 PDB at keel sta 130mm; solder 14AWG main leads to ESCs.
- [ ] Install 2× 40A BLHeli32 ESCs in bay C (port + stbd nacelle fore EDF = FC1; aft EDF = FC2).
- [ ] Install 80A ESC in Panel F for 120mm rear EDF (FC2 PRU Ch.2).
- [ ] Install 5V/5A BEC; verify 5.00V ±0.05V under 1A bench load.
- [ ] Pull motor phase leads through conduit to ESCs; solder (verify rotation marking first).
- [ ] CAN FD termination: 120Ω SOLDERED to CN1 Cape-B at Bay A (bus start); temporary 120Ω at FC2 Cape-A Bay B (Phase 3 far-end; remove in Phase 7).

**ESC assignment (cross-nacelle redundancy — any FC failure retains 50% thrust both nacelles):**

| ESC | EDF | Nacelle | Controlled by |
|-----|-----|---------|---------------|
| ESC1 | EDF1 (fore) | Port | FC1 Cape-A PRU Ch.0 |
| ESC2 | EDF2 (aft) | Port | FC2 Cape-A PRU Ch.0 |
| ESC3 | EDF1 (fore) | Stbd | FC1 Cape-A PRU Ch.1 |
| ESC4 | EDF2 (aft) | Stbd | FC2 Cape-A PRU Ch.1 |
| ESC5 | 120mm rear | Fuselage | FC2 Cape-A PRU Ch.2 |

**CN1+FC1 installation (Bay A — nose):**
- [ ] Mount CN1 Cape-B on Bay A floor standoffs (M2.5 nylon 6mm). Insert PB2-I. Secure.
- [ ] Mount FC1 Cape-A on inter-cape standoffs (M2.5 nylon 20mm) above CN1. Insert second PB2-I.
- [ ] Flash OS to eMMC on CN1 and FC1 via USB-C before installation.
- [ ] Install log μSD (64GB) in CN1 Cape-B log slot. Label: **CN1-LOG**.
- [ ] Seat RCRS-49 sub-module on CN1 Cape-B header; connect RCRS coax to forward 49MHz wire post.
- [ ] Connect CN1 radio pigtails: SiK 915MHz → belly port SMA; LoRa → belly stbd SMA; WiFi → dorsal fwd SMA.
- [ ] Route FC1 GPS U.FL coax through cockpit-roof PTFE sleeve (sta ~59mm); mount GPS patch on hull dorsal, face UP.
- [ ] Daisy-chain CAN FD: 120Ω (soldered) → CN1 → FC1 → exit Bay A toward Bay B.
- [ ] Daisy-chain RS-485: CN1 → FC1 → exit toward Bay B.
- [ ] Connect MIL-STD-1553: FC1 = Bus Controller (primary); CN1 = RT 0x01.
- [ ] Cap Bay E end of ETH-EA conduit (will connect to FC4 in Phase 7); connect Bay A end to CN1 Cape-B ETH-2.

**CN2+FC2 installation (Bay B — dorsal fwd):**
- [ ] Mount CN2 Cape-B on Bay B floor standoffs; insert PB2-I; mount FC2 Cape-A above; insert second PB2-I.
- [ ] Flash OS to eMMC on CN2 and FC2 before installation.
- [ ] Install log μSD (64GB) in CN2 Cape-B log slot. Label: **CN2-LOG**.
- [ ] Seat RCRS-49 sub-module on CN2 header.
- [ ] Route FC2 GPS coax through dorsal PTFE sleeve (sta ~130mm); mount GPS patch on dorsal hull, face UP.
- [ ] Continue CAN FD daisy-chain Bay A→Bay B: CN2 → FC2 + temporary 120Ω at FC2 (remove Phase 7).
- [ ] Continue RS-485 daisy-chain Bay A→Bay B.
- [ ] Connect ETH-AB (Bay A→Bay B): FC1 Cape-A ETH-1 → CN2 Cape-B ETH-2 (FC1↔CN2 Ethernet ring link).
- [ ] Cap Bay D end of ETH-BD (will connect to CN3 in Phase 7).
- [ ] Power taps: connect CN1, FC1, CN2, FC2 power leads from PWR conduit; verify 5V ±0.05V at each header.

**Security provisioning (before first flight):**
- [ ] Provision TPM 2.0 (SLB9670) on CN1, FC1, CN2, FC2 — unique key material per node.
- [ ] Verify CPLD write-blocker on CN1 and CN2: `echo test > /mnt/flightlog/test.txt` must return read-only error.
- [ ] Configure forensic log mount in `/etc/fstab` (noexec, nodev, nosuid, ro) on CN1 and CN2.

**Software configuration:**
- [ ] Flash serenity-cn Phase 6 daemon to CN1 and CN2.
- [ ] Flash serenity-fc Phase 6 stub to FC1 and FC2.
- [ ] Enable CAN FD interfaces at 1 Mbps / 8 Mbps on all 4 nodes.
- [ ] Verify 4-node CAN FD heartbeat ring: `candump can0` shows frames 0x001–0x004 within 100ms.
- [ ] Configure MAVLink routing (mavlink-router) on elected FC master → SiK 915MHz on CN master.
- [ ] Install RCRS-49 daemon on CN1 and CN2 (select channel per 47 CFR 95.623).

**Ground tests:**
- [ ] ESC calibration (full throttle power-on → drop to zero).
- [ ] Motor spin test (5% throttle 2s): all 5 motors spin in correct directions.
- [ ] Tilt servo calibration: 0° = nacelle vertical ±0.5°, 90° = horizontal ±0.5°.
- [ ] Rear nozzle servo endpoints verified.
- [ ] Static CG: **190mm from nose** (adjust battery position on rail).
- [ ] GPS lock: HDOP ≤1.5 on both FC nodes; positions agree within 2m.
- [ ] Radio checks: MAVLink heartbeat in QGC (SiK + LoRa backup); RCRS-49 RC channels correct; WiFi GCS telemetry.
- [ ] Node failover: kill FC master power → standby assumes authority within 100ms on tether.
- [ ] Tethered thrust test: 60% throttle 10s → lift exceeds AUW; ESC temps ≤60°C.
- [ ] Nav lights: 6-position ICAO cycle (RED port, GREEN stbd, WHITE tail, WHITE belly strobe).
- [ ] **Apply FAA registration number** (14 CFR Part 48 — replaces N00000 placeholder on airframe).

**First flight sequence (per REVN_BUILD_GUIDE_24IN.md §Phase 6):**
- [ ] Pre-flight ABCD checklist (Airframe, Battery, Comms, Docs)
- [ ] Tethered hover 1m AGL × 3 successful passes before free flight
- [ ] Free hover 1m AGL (stability, ±10° authority, altitude hold ±0.3m)
- [ ] Free hover 3m AGL (yaw 360° both directions)
- [ ] Nacelle transition: ≥8m AGL, gradual sweep 90°→0° — altitude hold ±1.5m during transition
- [ ] Forward flight circuit: one lap ≤10m AGL, transition back to hover, land
- [ ] Verify flight log written to CN1-LOG and CN2-LOG

**Phase 6 pass criteria:**
- [ ] Stable hover 1m AGL in ≤15° headwind
- [ ] Nacelle transition without altitude excursion >1.5m
- [ ] All ESCs ≤70°C at full hover power
- [ ] MAVLink telemetry live to QGC during all segments
- [ ] All 4-node CAN FD heartbeats confirmed
- [ ] Node failover: standby assumes within 100ms of master power-kill
- [ ] Flight log on both CN μSDs; CPLD write-block verified

---

### Phase 7 — Full 8-Node Architecture + ToF Obstacle Avoidance

**Goal:** All 8 nodes installed, full ring redundancy, 12× VL53L5CX dual-redundant obstacle avoidance operational.

**CN3+FC3 installation (Bay D — dorsal aft):**
- [ ] Remove temporary Phase 6 CAN FD 120Ω from FC2 Cape-A Bay B.
- [ ] Mount CN3 Cape-B on Bay D floor standoffs; insert PB2-I; mount FC3 Cape-A above.
- [ ] Flash OS to eMMC; install log μSD. Label: **CN3-LOG**.
- [ ] Seat RCRS-49 sub-module on CN3 header.
- [ ] Route FC3 GPS coax through dorsal PTFE sleeve (sta ~275mm); mount GPS patch, face UP.
- [ ] Continue CAN FD chain: Bay B FC2 → Bay D CN3 → FC3 → exit toward Bay E.
- [ ] Continue RS-485 chain Bay B→Bay D→Bay E.
- [ ] Connect ETH-BD (Bay B→Bay D): FC2 Cape-A ETH-1 → CN3 Cape-B ETH-2.
- [ ] Power tap Bay D; verify 5V ±0.05V.

**CN4+FC4 installation (Bay E — aft service):**
- [ ] Mount CN4 Cape-B on Bay E standoffs; insert PB2-I; mount FC4 Cape-A above.
- [ ] Flash OS to eMMC; install log μSD. Label: **CN4-LOG**.
- [ ] Seat RCRS-49 sub-module on CN4 header.
- [ ] Route FC4 GPS coax through dorsal PTFE sleeve (sta ~350mm); mount GPS patch, face UP.
- [ ] Terminate CAN FD bus end: CN4 → FC4 + **120Ω PERMANENT** soldered to FC4 Cape-A.
- [ ] Connect ETH-DE (Bay D→Bay E): FC3 Cape-A ETH-1 → CN4 Cape-B ETH-2.
- [ ] Connect ETH-EA ring-close (Bay E→Bay A): FC4 Cape-A ETH-1 → [Bay A CN1 Cape-B ETH-2 already connected]. Closes the 8-node RSTP ring.
- [ ] Power tap Bay E; verify 5V ±0.05V.

**Security provisioning — remaining 4 nodes:**
- [ ] TPM 2.0 on CN3, FC3, CN4, FC4 — unique key material per node.
- [ ] CPLD write-blocker verification on CN3 and CN4.

**Full ring integration:**
- [ ] Verify RSTP ring: `bridge vlan show`; disconnect one ETH cable → traffic re-routes within 1s.
- [ ] Verify full 8-node CAN FD ring: `candump can0` shows frames 0x001–0x008 within 100ms.
- [ ] MIL-STD-1553 final config: FC1=BC, FC2=standby BC, FC3/FC4/CN1–CN4=RT; all 8 RT addresses respond within 9μs.

**ToF sensor installation:**

Array B (hosted by FC1, Bay A):

| Sensor | Station | Position |
|--------|---------|----------|
| S1B | 50mm | Nose ring |
| S2B | 510mm | Rear bell rim |
| S3B | 180mm | Port hull |
| S4B | 180mm | Stbd hull |
| S5B | 315mm | Dorsal keel |
| S6B | 265mm | Belly blister |

- [ ] Install 6× VL53L5CX in Array B flush-mount frames; wire to TCA9548A ch.0–5 in Bay A; MCP23008 GP0–GP5 → XSHUT; I²C to FC1 Cape-A.

Array A (hosted by FC3, Bay D):

| Sensor | Station | Position |
|--------|---------|----------|
| S1A | 30mm | Nose ring |
| S2A | 525mm | Rear bell rim |
| S3A | 240mm | Port hull |
| S4A | 240mm | Stbd hull |
| S5A | 215mm | Dorsal keel |
| S6A | 195mm | Belly blister |

- [ ] Install 6× VL53L5CX in Array A flush-mount frames; wire to TCA9548A ch.0–5 in Bay D; separate I²C bus (electrically isolated from Array B).
- [ ] Apply 0.5mm PMMA disc over each sensor aperture with UV adhesive.
- [ ] Configure OA fusion in firmware: halt at 1.0m obstacle clearance; either array independent on single-FC failure.
- [ ] GPS clearance check for 49MHz wire post proximity: bench-verify HDOP ≤1.5 with RCRS-49 transmitting; if GPS degrades, move GPS patch to ≥165mm from forward post.

**Phase 7 pass criteria:**
- [ ] All 8 CAN FD heartbeats (0x001–0x008) confirmed
- [ ] Ethernet RSTP ring heals on single-link disconnect within 1s
- [ ] MIL-STD-1553: all 8 RTs respond within 9μs
- [ ] CN3 and CN4 log μSD write-block verified
- [ ] All 12 ToF sensors return valid range at ≤4m
- [ ] OA halt test: approach wall at 0.5m/s → stops at 1.0m clearance
- [ ] Array failure mode: either FC1 or FC3 loss → remaining array provides full OA coverage
- [ ] 3-waypoint autonomous mission with GPS, altitude hold, RTL on simulated link loss

---

### Phase 8 — Cargo System

**Goal:** 250g payload delivery via autonomous winch deploy with auto-latch cradle.

- [ ] Bond cargo gondola shell into belly void at 4× M3 hard points (installed Phase 1). Cure 24h.
- [ ] Install 3mm CF door hinge pins; attach clamshell door halves (spring-loaded to open).
- [ ] Install DRV8833 + N20 winch motor + drum; wind 1.5m Dyneema; attach auto-latch cradle via double-bowline.
- [ ] Install SG90 door-actuator servo (spring-assist open, servo pull-close via bell-crank).
- [ ] Install SG90 payload-release servo; connect to DRV8833 IN1/IN2 via PWM→resistor divider→GPIO.
- [ ] Route control leads through PWR conduit belly tap to CN master (CN1 or CN2 — winner of CN master election).
- [ ] Seal gondola-hull perimeter with 3M foam gasket tape.
- [ ] Configure CN master GPIO: door open/close, winch deploy/retract, payload latch status (microswitched).

**Phase 8 pass criteria:**
- [ ] Door open/close × 10: no binding
- [ ] Winch deploy 1.5m: straight descent, line clear
- [ ] Winch retract: auto-latch clicks and holds at top
- [ ] 250g load test: winch deploy + retract × 5; latch holds
- [ ] Hover with 250g payload: altitude-hold degradation ≤10%
- [ ] Autonomous delivery: 3-waypoint mission, deploy at waypoint 2, retract empty, complete mission

---

### Phase 9 — Finishing

**Goal:** Aircraft legally compliant, aesthetically complete, and fully documented.

- [ ] Replace FAA N00000 placeholder in `serenity/diagrams/decal_sheet.svg` with issued FAA registration number (via FAA DroneZone, 14 CFR Part 48).
- [ ] Print decal sheet on waterslide decal paper; seal with clear coat; dry 24h.
- [ ] Apply decals per `build_guide_19_decal_placement.svg`: Serenity lettering, FAA blocks, universe markings (宁静 Chinese name, Alliance registry), safety labels, weathering.
- [ ] Final airworthiness inspection: all fasteners, propulsion, electronics, battery, CG.
- [ ] Documentation archive: build log (photos + test results), Cape-B CPLD bitstream, TPM endorsement key fingerprints, final AUW + CG measurements.
- [ ] FAA compliance final check: registration visible without moving any part; remote pilot certificate current; AUW <55 lbs; LAANC authorization for any controlled airspace.

---

## 4.0 — Firmware and Software

**Dependency for Phase 6:** serenity-fc Phase 7 items can be developed concurrently with physical Phases 0–5 and must be integrated by Phase 6 first flight.

### 4.1 — Completed

- [x] Firmware directory structure (`serenity/firmware/`) *(done 2026-05-25)*
- [x] KISS/AX.25 UART driver for XCVR-49MHZ-1 — `serenity/firmware/cn/src/xcvr_kiss.c/.h` *(done 2026-05-25)*
- [x] Si5351A I²C driver — `serenity/firmware/cn/src/si5351.c/.h` *(done 2026-05-25)*
- [x] AM6254 device tree overlays — Cape-A and Cape-B DTSs *(done 2026-05-25)*
- [x] serenity-cn Phase 6 daemon (XCVR KISS driver + argparse + SIGTERM) *(done 2026-05-25)*
- [x] serenity-fc Phase 6 stub (signal handling, idle loop placeholder) *(done 2026-05-25)*

### 4.2 — FC Node (Cape-A) — Phase 7 Firmware

- [ ] **EDF ESC PID governor** — BDSHOT600 telemetry input on PRU-ICSS, EHRPWM output to ESCs, CAN FD cross-node synchronisation. Targets: settle <200ms, overshoot <5%; equalization |RPM_FWD − RPM_AFT| <100 RPM; fault latch on overtemp/overcurrent (no auto-recovery, GCS ack required).
- [ ] **Nacelle tilt servo PWM generation** — EHRPWM or PRU; travel limits −5°/140° enforced in firmware; symmetric 2° tracking both nacelles.
- [ ] **IMU / barometer sensor fusion** — ICM-42688-P (SPI), BMP388/BMP390 (SPI); complementary or Kalman filter for attitude; altitude hold PID using barometric altitude + GPS.
- [ ] **ToF sensor array management** — VL53L5CX ×6 per node via TCA9548A I²C mux; XSHUT sequencing via MCP23008; OA fusion (Array A + Array B cross-check); halt at 1.0m clearance.
- [ ] **u-blox M10Q GNSS integration** — UART NMEA/UBX parse; position fix broadcast on CAN FD; HDOP gating (≤1.5 for valid position); multi-node position cross-check (≤2m disagreement threshold).
- [ ] **MIL-STD-1553B RT implementation** — PRU-ICSS Manchester II encoder/decoder; RT address assignment per node role; BC arbitration on FC1 and FC2.
- [ ] **TPM-bound attestation** — SLB9670 TPM 2.0 HMAC on all outbound flight-critical CAN FD messages; pcrs extend on each boot; boot measurement chain.
- [ ] **governor_cal.py** — thrust stand calibration script: sweeps 0%→100%→0% throttle, fits k coefficient (T = k × RPM²), outputs `EDF_THRUST_K` for `governor_config.h`.
- [ ] **governor_config.h** — template with calibrated k values per EDF; compile-time constants.

### 4.3 — CN Node (Cape-B) — Phase 7 Firmware

- [ ] **CAN FD heartbeat and telemetry forwarding** — broadcast 0x001–0x008 node health frames; relay MAVLink telemetry from elected FC master to SiK GCS link.
- [ ] **MIL-STD-1553B BC/RT tasks** — BC on CN1 (standby), RT on CN2–CN4; mirror FC bus controller arbitration.
- [ ] **RS-485 inter-board messaging** — structured message format (header/payload/CRC); inter-node command and status relay.
- [ ] **Ethernet RSTP ring management** — CPSW3G bridge configuration; RSTP fast-failover (<1s) verification; ring segment health monitoring.
- [ ] **Signed-log write via CPLD write-blocker** — log records written as read-only-append through ATF16V8BQL latch interface; NOR flash (W25Q128JV) circular buffer for overflow.
- [ ] **TPM-bound HMAC on all outbound AX.25 payloads** — each RCRS-49 packet includes HMAC-SHA256 computed from SLB9670 stored key; receiver nodes verify before acting.
- [ ] **Cargo control** — DRV8833 winch H-bridge, HX711 load cell (payload weight sensing), SG90 door and release servos; state machine: IDLE → DEPLOY → DELIVERED → RETRACT → LATCHED.
- [ ] **MAVLink routing configuration** — mavlink-router config: elected CN master routes FC master telemetry to all 4 radio links (SiK, LoRa, WiFi, RCRS-49 backup).

### 4.4 — Both Nodes

- [ ] **Node role election protocol** — CAN FD priority arbitration at boot; lowest node-ID wins master role; automatic failover on heartbeat timeout (100ms); FC master and CN master elected independently.
- [ ] **Autonomous navigation** — 3-waypoint GPS mission execution; altitude hold ±0.3m; waypoint radius 2m; RTL on any link loss >5s.
- [ ] **OA integration** — ToF halt trigger feeds into navigation; velocity command zeroed within 1.0m of obstacle; resumes when clear.
- [ ] **GPS cross-check** — 4 GPS receivers (one per FC node); positions averaged; outlier >2m flagged and excluded from blend.
- [ ] **Security message signing** — every inter-node CAN FD message signed; unauthenticated messages discarded; signing key material bound to node TPM endorsement key.

---

## 5.0 — Regulatory Compliance

### 5.1 — FCC (external radio systems)

- [ ] **XCVR-49MHZ-1 FCC Part 95 compliance** — center frequency accuracy ±0.005%, ERP ≤100mW, harmonic suppression ≥40dBc (47 CFR 95.655). Document via pre-compliance checklist (1.3 Phase 4). Formal FCC equipment authorization (FCC ID grant) required before airborne transmission on 49MHz channels (47 CFR 95.603).
- [x] **SiK 915MHz** — operates under FCC Part 15 / ISM band (no license required for operation). Verify SiK radio module carries FCC ID marking.
- [x] **LoRa RFM95W 915MHz** — same Part 15 / ISM band. Verify module carries FCC ID.
- [x] **WiFi (WL1837MOD)** — Part 15 / ISM. Module must carry FCC ID; verify.
- [x] **ZigBee 2.4GHz (if used)** — Part 15 / ISM. Verify FCC ID on any ZigBee module installed.

### 5.2 — FAA (airworthiness and operations)

- [ ] **Aircraft registration** — register under 14 CFR Part 48 (sUAS, AUW <55 lbs) at FAA DroneZone. Replace N00000 placeholder in `decal_sheet.svg`. Mark on airframe per 14 CFR 47 — visible without moving any part. **Complete before first untethered flight.**
- [ ] **Remote Pilot Certificate** — verify FAA Part 107 Remote Pilot Certificate is current (24-month knowledge test recurrency).
- [ ] **Navigation lights compliance** — verify 6-position WS2812C nav light implementation: port RED (≥3 SM visibility), stbd GREEN, tail WHITE steady, belly WHITE strobe. Compliant with ICAO Annex 2 and 14 CFR 91.209.
- [ ] **sUAS data plate** — attach to airframe: operator name, contact info, registration number. See `decal_sheet.svg` "D — safety labels" zone.
- [ ] **Pre-flight area check** — LAANC authorization for any Class B/C/D/E airspace. Verify no TFRs, NOTAM conflicts. File NOTAM if operating in uncontrolled airspace with public nearby.
- [ ] **Airspace waiver (if applicable)** — if operating above 400ft AGL or in controlled airspace without LAANC, apply for FAA Part 107 waiver (approval time 90 days typical).

### 5.3 — Industry Standards Compliance

- [ ] **Structural validation** — wing spar, keel, pivot rod, and tilt servo torque analysis documented per REVN_BUILD_GUIDE_24IN.md structural summary. Verify at actual build dimensions (24" hull).
- [ ] **IEEE/ISA/AUVSI best practices** — validate all design decisions against AUVSI UAS best practices; document in build record.
- [ ] **Tamper-evident logging** — verify CPLD write-blocker (ATF16V8BQL) on all 4 CN nodes prevents post-flight log modification; function as hardware-enforced non-executable microSD per CLAUDE.md requirement.

---

*© 2026 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP — CC BY 4.0*  
*Hull: Peter Farell CC BY 4.0 · Nozzles: BamJr CC BY 4.0 · Inspiration: Firefly/Serenity © Joss Whedon / Mutant Enemy / Universal — Not an officially licensed product.*
