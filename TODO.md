# Serenity UAV — Rev N TODO

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0  
Last updated: 2026-05-23

---

## Blocking / Pre-Fabrication

- [ ] **Regenerate CAPE-A-1 gerbers** — `.kicad_pcb` modified 2026-05-23 (tamper-mesh
  commit); gerbers in `serenity/kicad/gerbers/CAPE-A-1/` are from 2026-05-22.
  Open in KiCad → Plot → Gerbers; overwrite existing files; re-export drill files.

- [ ] **Regenerate CAPE-B-1 gerbers** — same timestamp problem as CAPE-A-1.
  `serenity/kicad/gerbers/CAPE-B-1/` files are from 2026-05-22.

- [ ] **Export STLs from Rev N SCAD files** — five SCADs have no rendered STL output:
  - `serenity/stl/s_edf_120_motor_mount.scad`
  - `serenity/stl/s_edf_120_thrust_tube.scad`
  - `serenity/stl/s_aft_edf_plenum.scad`
  - `serenity/stl/s_neck_intake_frame.scad`
  - `serenity/stl/s_rear_neck_intake_shell24.scad`
  Run: `blender --background --python <script>.py` per CLAUDE.md workflow.
  Verify Z-range and bore diameter in console before committing.

- [x] **Nacelle pod for Rev N (50 mm tandem EDFs)** — `nacelle_pod_50mm_tandem.scad` created
  2026-05-24 with: dual-bore centerline (EDF1 Z=22..72mm, EDF2 Z=98..143mm), 11-fin
  twisted stator, M=1.0 gear boss / conduit hard points, MF104ZZ clevis pivot boss at Z=83mm
  (nacelle CG).  Rev O: pivot relocated to Z=83mm from Z=74mm (v1); blender_nacelle_revo.py
  generates s_eng_left/right_stator_shell24_revo.stl.
  **Note:** blender and openscad not installed in this build environment; run
  `blender --background --python thingverse-serenity/blender_nacelle_revo.py` on host
  machine to verify Z-range and bore-diameter before committing STLs. *(done 2026-05-24)*

- [ ] create Cargo handling equipment mounts.  create bridge fpv camera mount.  export stls

- [ ] do a comprehensive update on the graphical build guides to the current design specs.
- [ ] integrated the build plan into the todo

---

## PCB / KiCad

- [ ] **Verify bom_revN.csv ↔ bom_revN.json sync** — CSV was updated 2026-05-23;
  JSON was last written 2026-05-22.  Confirm both reflect the same component list
  and quantities.

---

## XCVR-49MHZ-1 (49 MHz AX.25 RCRS Transceiver) — Full Development

Stub KiCad project created at `serenity/kicad/XCVR-49MHZ-1.*`.
Design notes and BOM candidates are in `serenity/kicad/XCVR-49MHZ-1.md`.

### Phase 1 — IC Selection and Architecture Lock

- [ ] **Resolve DDS choice** — Si5351A-B-GT (I²C, direct to 49 MHz, simpler) vs.
  AD9833BRMZ + external ×4 PLL.  Evaluate Si5351A phase noise vs. Part 95
  frequency stability spec (±0.005%).  Decision gates all downstream work.

- [ ] **Evaluate PA options for 49 MHz at 100 mW** — RA07H4047M (30–512 MHz)
  or discrete 2N3866 BJT PA.  Check gain, efficiency, and thermal at 100 mW
  continuous.  Must maintain ≥ 40 dBc harmonic suppression after LPF.

- [ ] **Confirm TCM3105 availability** — TI discontinued; verify stock at Mouser/Digi-Key
  or identify drop-in substitute for Bell 202 AFSK modem function.  Alternatives:
  MC14412 (Onsemi) or DSP implementation in firmware on CAPE-B MCU.

### Phase 2 — Schematic

- [ ] **Draw U1 DDS sub-circuit** — power decoupling, SPI/I²C to J1, frequency
  configuration load sequence; note that channel select (49.830–49.890) is
  software-configurable at runtime.

- [ ] **Draw U2 AFSK modem sub-circuit** — TCM3105 or equivalent; UART interface
  to J1 pins 3/4; CD (carrier detect) output to CAPE-B GPIO (add to J1 if needed).

- [ ] **Draw U3 PA + modulator sub-circuit** — DDS carrier in, AFSK audio in,
  RF out to FL1; PTT_N gate; include bias network and output matching to 50 Ω.

- [ ] **Draw FL1 5-element Chebyshev LPF** — calculate component values for
  fc = 75 MHz, 50 Ω in/out; verify −40 dBc at 98 MHz (2nd harmonic of 49 MHz).
  Use QUCS-S or similar to simulate before committing values.

- [ ] **Draw U4 LNA + envelope detector RX chain** — MGA-82563 input, gain/NF budget,
  RSSI voltage divider to J1 pin 6.

- [ ] **Draw U5 TX/RX switch** — PE4259-63 SPDT; PTT_N control; isolation spec
  must protect LNA during TX (PE4259 provides ~35 dB TX→RX isolation).

- [ ] **Draw U6 3.3 V LDO and power tree** — AMS1117-3.3 from +5V; bulk decoupling;
  ferrite bead between digital and RF sections on +5V.

- [ ] **Draw J1 and J2 connectors with pin labels**

- [ ] **Run ERC; resolve all errors**

### Phase 3 — PCB Layout

- [ ] **Set up layer stack in KiCad** — 4L: F.Cu signal / In1.Cu GND / In2.Cu +3V3
  power / B.Cu signal; confirm 1.6 mm total thickness (JLCPCB standard).

- [ ] **Place components** — RF section (right 25 mm): U1, U3, U4, U5, FL1, J2;
  digital section (left 30 mm): U2, U6, J1.

- [ ] **Route RF path** — 50 Ω microstrip, 2.75 mm wide on F.Cu; continuous
  ground stitching vias along both edges of microstrip; no 90° bends (use 45° or
  curved).

- [ ] **Route digital signals** — UART traces ≥ 5 mm from RF section boundary;
  ferrite bead (BLM18PG221SN1D or equivalent) on +5V at section boundary.

- [ ] **Place LPF shield keep-out** — mark Coilcraft SER inductor cans on F.Fab;
  orient inductors perpendicular to each other; verify no mutual coupling path.

- [ ] **Thermal vias under U3 PA** — exposed pad to In1.Cu GND plane; minimum
  9× 0.3 mm vias; confirm <85 °C case temperature at 100 mW continuous TX.

- [ ] **SMA J2 edge placement** — flush to right board edge; 3 mm copper keep-out
  on both sides of feed line from edge to U5.

- [ ] **Run DRC; resolve all errors**

### Phase 4 — Verification and Compliance

- [ ] **SPICE/QUCS simulation of LPF** — verify harmonic suppression meets
  47 CFR 95.655 before board spin.

- [ ] **50 Ω trace impedance check** — use KiCad impedance calculator or Saturn PCB
  toolkit to confirm 2.75 mm / 1.6 mm FR4 / εr=4.5 gives 50 ± 5 Ω.

- [ ] **FCC Part 95 pre-compliance checklist** — document: center frequency
  accuracy, ERP calculation, harmonic levels, labeling requirements
  (47 CFR 95.603 FCC ID block on silkscreen).

### Phase 5 — Production Files

- [ ] **Export gerbers** to `serenity/kicad/gerbers/XCVR-49MHZ-1/`

- [ ] **Export BOM** — add XCVR-49MHZ-1 line items to `serenity/docs/bom_revN.csv`
  and `bom_revN.json`.

- [ ] **Update `PROJECT_INDEX.md`** to list XCVR-49MHZ-1 under PCB section.

---

## Firmware (Phase 6 dependency)

- [ ] **Create `serenity/firmware/` directory structure** — minimum viable for
  Phase 6 first flight: CN node (CAPE-B AM6254) + FC node (CAPE-A AM6254).

- [ ] **KISS/AX.25 UART driver for XCVR-49MHZ-1** — runs on CN node; framing,
  channel select via I²C to Si5351A, PTT sequencing (≥ 5 ms key-up before TX).

---

## Documentation

- [x] **Update `PROJECT_INDEX.md`** — add XCVR-49MHZ-1 row to PCB table. *(done 2026-05-24)*

- [x] **Sync bom_revN.csv ↔ bom_revN.json** — resolve 2026-05-23 vs 2026-05-22
  timestamp discrepancy. *(done 2026-05-24 — added WIRE-49MHZ, POST-FWD-49, POST-AFT-49 as
  structured `avionics.antenna_system` entries in bom_revN.json; updated JSON date to 2026-05-23)*
