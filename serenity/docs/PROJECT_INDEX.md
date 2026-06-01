<!-- OpenDyslexic font for screen reading (CC BY 4.0) -->
<link rel="stylesheet" href="https://fonts.cdnfonts.com/css/opendyslexic">
<style>
body, p, li, td, th, code, pre {
  font-family: 'OpenDyslexic', 'OpenDyslexicMono', sans-serif !important;
  line-height: 1.8;
  letter-spacing: 0.03em;
}
/* Screen: dark background, high-contrast light text */
@media screen {
  body { background: #0d1117; color: #e6edf3; }
  a    { color: #58a6ff; }
  code { background: #161b22; color: #e6edf3; padding: 2px 6px; border-radius: 4px; }
  pre  { background: #161b22; padding: 12px; border-radius: 6px; }
  th   { background: #21262d; color: #79c0ff; }
  tr:nth-child(even) td { background: #161b22; }
  h1,h2,h3 { color: #58a6ff; border-bottom: 1px solid #30363d; padding-bottom: 6px; }
  blockquote { border-left: 4px solid #388bfd; color: #8b949e; padding-left: 12px; }
}
/* Print: light background, dark text, conserve ink */
@media print {
  body { background: #ffffff !important; color: #111111 !important; }
  a    { color: #003399 !important; }
  h1,h2,h3 { color: #000000 !important; }
  code,pre  { background: #f5f5f5 !important; color: #111111 !important; border: 1px solid #cccccc; }
  tr:nth-child(even) td { background: #f9f9f9 !important; }
}
</style>

# Serenity-Class Tiltrotor UAV — Public Project Index

**Author:** Steve Griffing, PE(CSE) [Control Systems Engineering], CISSP-ISSEP, CPP  
**License:** CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/  
**Year:** 2026  
**Status:** Public release — all artifacts published

---

## Attribution

| Work | Author | License | Source |
|------|--------|---------|--------|
| Hull geometry | Peter Farell | CC BY 4.0 | printables.com/model/548545 |
| Variable-area EDF nozzles | BamJr | CC BY 4.0 | thingiverse.com/thing:2991269 |
| Visual inspiration | Joss Whedon / Mutant Enemy / Universal | © all rights reserved | Firefly (2002) / Serenity (2005) — Fan engineering work |
| All other design work | Steve Griffing | CC BY 4.0 | This project |

---

## Complete File Manifest

### JSX Interactive Specification Artifacts (open in Claude.ai or offline viewer)

| File | Description | Revision |
|------|-------------|----------|
| `tiltrotor-drone.jsx` | Original Rev A design concept | Rev A |
| `pico2-hat.jsx` | TRIHAT-1 sensor hat specification | Rev A |
| `cm4-carrier-update.jsx` | CM4 carrier board update | Rev B |
| `antenna-layout.jsx` | Antenna layout specification | Rev B |
| `serenity-drone.jsx` | Full system spec Rev B | Rev B |
| `serenity-rev-b.jsx` | Rev B consolidated | Rev B |
| `serenity-rev-c.jsx` | Battery + nav lights + antenna + wiring + BOM/SBOM | Rev C |
| `serenity-rev-d.jsx` | 70mm EDFs + 40mm fwd + variable nozzle + build guide | Rev D |
| `serenity-rev-e.jsx` | CC BY 4.0 + write-blocker + HW NX + dual WiFi SMA + Zigbee/LoRa + nacelle gear nozzle | Rev E |
| `serenity-rev-f.jsx` | Author attribution + ft/kts/yd units + full license compliance | Rev F |
| `nacelle-nozzle-gear.jsx` | Variable-area nacelle nozzle gear coupling full design | Rev E |
| `serenity-connectivity-revF.jsx` | 4-bus architecture analysis (Ethernet + CAN FD + RS-485 + I²C) | Rev F connectivity |
| `serenity-connectivity-revG.jsx` | CAN daisy-chain (2nd connector) + RS-485 + I²C inter-board buses | Rev G connectivity |
| `serenity-connectivity-revH.jsx` | **MIL-STD-1553B replaces I²C as 4th active bus** | Rev H connectivity |
| `serenity-rev-i.jsx` | CM3+ Nodes 2&3 + CM3-CARRIER-1 + dual VL53L5CX ToF arrays + cargo gondola | Rev I |
| `serenity-rev-j.jsx` | XRP 3660-2700KV nacelle EDFs + Hobbywing 120A ESCs + 83mm pod ID | Rev J |
| `serenity-rev-k.jsx` | 8× PocketBeagle 2 (AM6232) cooperative nodes + Cape-A/B + TPM ×8 + CPLD write-blocker + LoRa + WL1837MOD WiFi + **Dual 80mm 6S series EDFs per nacelle** | Rev K (superseded by Rev L → Rev M) |
| `serenity-esc-telem-dual-edf.jsx` | Dual-EDF ESC telemetry spec — 4× nacelle ESCs, 74HC4051 8:1 mux, power wiring, fault tolerance | Rev K dual-EDF |
| `serenity-nacelle-pid-governor.jsx` | **Per-EDF PID closed-loop RPM governor** — 5-tab spec: overview, PID loops, cooperative control, fault response, commissioning | **Rev L new** |
| `serenity-edf-options.jsx` | **EDF selection guide** — budget / standard XRP / high-perf Schübeler comparison, tandem series performance, ESC pairing, phase build guide | **Rev L new** |
| `serenity-rev-l.jsx` | **Rev L — Dual 80mm 6S series EDFs + PID governor + EDF options** — supersedes Rev K; firmware-only update; hardware unchanged | Rev L (superseded by Rev M) |
| `serenity-rev-m.jsx` | **Rev M — PocketBeagle 2 Industrial (AM6254) hardware upgrade** — 8× AM6254 quad A53 1.4GHz · 1GB DDR4 · 64GB eMMC · −40°C to 85°C · OS microSD eliminated · propulsion + governor unchanged | Rev M (superseded by Rev N) |
| `serenity-rev-n.jsx` | **Rev N — 24-inch hull + 50mm tandem EDFs** — scaled hull to 609.6 mm · 2× 50mm 6S EDF per nacelle in tandem series · 4-radial-scoop intake for rear 120mm EDF · nacelle_pod_50mm_tandem design stub · bom_revN (5 propulsion + full avionics) | Rev N (superseded by Rev O) |
| `serenity-rev-o.jsx` | **Rev O — CG-pivot nacelle + full gear train** — tilt pivot relocated from Z=74mm to Z=83mm (nacelle CG, derived from 15-component mass breakdown) · M=1.0 gear train fully specified (sector R=22mm → drive pinion N=12T → bevel pair 45° N=14T → crown pinion N=12T → nozzle ring rack R_eff=28mm) · blender_nacelle_revo.py generates left/right stator shells · nacelle_pod_50mm_tandem.scad parametric SCAD · bom_revO (full 50mm-EDF build) | Rev O (superseded by Rev P) |
| `serenity-rev-p.jsx` | **Rev P — Cargo bay complete** — Rev S cargo section shell (100×90mm belly opening, hinge-pin blocks, SG90 servo pads, latch-catch lips) · port/stbd CF-PETG clamshell doors (piano hinge, 3mm CF rod, foam gasket seal) · 2× SG90 servo (door + release) via DRV8833 H-bridge · N20 winch + Dyneema SK75 0.5mm spool · auto-latch cargo cradle · GPS retention ring + FPV bezel · bom_revP.json/csv (14 new items, 5 total servos, ~$1,905 est.) · Comprehensive 11-tab standalone spec | **Rev P ← current master** |

### SVG Engineering Diagrams

| File | Description |
|------|-------------|
| `overview_top.svg` | Top / plan view with dimensions, antennas, CG, nav lights |
| `overview_side.svg` | Right side view with all subsystems annotated |
| `overview_front.svg` | Front (nose-on) view showing nacelle span |
| `overview_bottom.svg` | Bottom view showing payload bay, SiK antenna, battery rail |
| `components_overview.svg` | 32-component grid overview |
| `build_plan.svg` | 9-phase build plan summary |
| `decal_sheet.svg` | **Full decal sheet** — FAA reg blocks, Serenity markings, safety labels, Chinese 宁静, weathering guide |
| `build_guide_00_cover.svg` | LEGO-style build guide cover |
| `build_guide_01_print_prep.svg` | Step 1: Print preparation |
| `build_guide_02_print_hull.svg` | Step 2: Print hull sections |
| `build_guide_03_print_nacelle.svg` | Step 3: Print nacelles & nozzle parts |
| `build_guide_04_cut_cf.svg` | Step 4: Cut carbon fibre skeleton |
| `build_guide_05_cf_skeleton.svg` | Step 5: Assemble CF skeleton |
| `build_guide_06_nacelle_pivot.svg` | Step 6: Nacelle pivot & bearing installation |
| `build_guide_07_edf_install.svg` | Step 7: Install 70mm EDFs & LED tip caps |
| `build_guide_08_nozzle_gear.svg` | Step 8: Gear nozzle assembly (BamJr remix) |
| `build_guide_09_avionics.svg` | Step 9: Avionics installation |
| `build_guide_10_power_wiring.svg` | Step 10: Power wiring & ESC installation |
| `build_guide_11_inter_board.svg` | Step 11: Inter-board wiring (Ethernet + CAN FD) |
| `build_guide_12_security_hw.svg` | Step 12: Security hardware (CPLD write-blocker + STM32 NX) |
| `build_guide_13_nav_lights.svg` | Step 13: Navigation lights (ICAO / 14 CFR 91.209) |
| `build_guide_14_antennas.svg` | Step 14: Antenna installation |
| `build_guide_15_software.svg` | Step 15: Software flash & configure |
| `build_guide_16_calibration.svg` | Step 16: CG balance, servo, nozzle calibration |
| `build_guide_17_ground_test.svg` | Step 17: Ground test procedures |
| `build_guide_18_first_flight.svg` | Step 18: First flight |
| `build_guide_19_decal_placement.svg` | Step 19: Decal application & FAA registration placement |

### KiCad PCB Source Files (KiCad 7.x)

| File | Board | Size | Description |
|------|-------|------|-------------|
| `TRIHAT-1.kicad_pcb` | TRIHAT-1 | 65×48mm | Pico 2 sensor hat: IMU, Baro, GPS, CAN FD, Ethernet, TPM 2.0 |
| `TRIHAT-1.kicad_sch` | TRIHAT-1 | — | Schematic (open in KiCad 7.x) |
| `CM4-CARRIER-1.kicad_pcb` | CM4-CARRIER-1 Rev E | 65×52mm | CM4 carrier: write-blocker CPLD, dual-band WiFi SMA, μSD, USB hub |
| `CM4-CARRIER-1.kicad_sch` | CM4-CARRIER-1 Rev E | — | Schematic |
| `COMMS-HAT-1.kicad_pcb` | COMMS-HAT-1 Rev E | 65×48mm | CM4 hat: CAN FD, Ethernet, TPM, NX proxy, log μSD, SiK, RCRS, Zigbee/LoRa |
| `COMMS-HAT-1.kicad_sch` | COMMS-HAT-1 Rev E | — | Schematic |
| `XCVR-49MHZ-1.kicad_pcb` | XCVR-49MHZ-1 | 55×35mm | 49 MHz AX.25 RCRS transceiver: Si5351A DDS, TCM3105 AFSK modem, PA, 5-element Chebyshev LPF, MGA-82563 LNA, PE4259 TX/RX switch — connects to Cape-B J1 |
| `XCVR-49MHZ-1.kicad_sch` | XCVR-49MHZ-1 | — | Schematic stub (open in KiCad 7.x) — layout in progress; see `XCVR-49MHZ-1.md` for design notes |

### STL 3D Print Files (22 parts)

| File | Material | Notes |
|------|----------|-------|
| `hull_cockpit_cap.stl` | PETG | Nose section 0–22mm |
| `hull_cockpit_section.stl` | PETG | Cockpit bay 22–90mm |
| `hull_mid_body_left.stl` | PETG | Mid hull left half |
| `hull_mid_body_right.stl` | PETG | Mid hull right half |
| `hull_aft_neck.stl` | PETG | Aft transition 230–270mm |
| `hull_engine_bell.stl` | PETG | Engine bell 270–365mm |
| `nacelle_pod_70mm.stl` | CF-PETG | 70mm EDF nacelle pod, 80mm OD |
| `nacelle_tip_cap_port.stl` | Clear PETG | Port nacelle tip, LED recess (RED) |
| `nacelle_tip_cap_stbd.stl` | Clear PETG | Starboard nacelle tip, LED recess (GREEN) |
| `tilt_bracket_cf_petg.stl` | CF-PETG | Nacelle tilt pivot bracket |
| `sector_gear_22mm.stl` | PETG/Resin | R=22mm, 90° arc, M0.5 — drives nozzle via bevel/crown chain |
| `nozzle_inner_ring_70mm.stl` | CF-PETG | BamJr remix — nacelle nozzle, 70mm ID, rack teeth on OD |
| `nozzle_outer_housing_70mm.stl` | PETG | BamJr remix — nacelle nozzle outer, 70mm |
| `nozzle_flap_x8.stl` | PETG | BamJr remix — 8 nozzle flaps (print 16 total) |
| `nozzle_inner_ring_40mm.stl` | CF-PETG | BamJr remix — fuselage nozzle, 40mm ID |
| `nozzle_outer_housing_40mm.stl` | PETG | BamJr remix — fuselage nozzle outer |
| `bevel_gear_housing.stl` | CF-PETG | Bevel gear pair housing block |
| `pinion_a_bracket.stl` | CF-PETG | Pinion-A bearing bracket, external nacelle face |
| `dorsal_antenna_fin.stl` | PETG | 49MHz RCRS antenna fin, 35mm tall, coil cavity |
| `payload_bay_door.stl` | PETG | Belly payload door, 112×42mm, SG90 latch hinge |
| `landing_skid_foot.stl` | TPU 95A | Crash-absorbing skid pads (print ×4) |
| `cockpit_dome_clear.stl` | Clear PETG | Ellipsoidal cockpit dome, GPS window |

### OpenSCAD Parametric Source Files (Rev N / Rev O)

Generate STL from SCAD: `openscad -o <output.stl> <file.scad>` (OpenSCAD 2021.01+)
Nacelle shells use Blender script instead — see `thingverse-serenity/blender_nacelle_revo.py`.

| File | Output STL | Description |
|------|-----------|-------------|
| `serenity/stl/s_edf_120_motor_mount.scad` | `s_edf_120_motor_mount.stl` | 120mm rear EDF motor mount ring — CF-PETG structural |
| `serenity/stl/s_edf_120_thrust_tube.scad` | `s_edf_120_thrust_tube.stl` | 120mm rear EDF thrust tube / nozzle — PETG |
| `serenity/stl/s_aft_edf_plenum.scad` | `s_aft_edf_plenum.stl` | 4-to-1 cross-shaped plenum manifold for 4 radial scoops → 120mm EDF |
| `serenity/stl/s_neck_intake_frame.scad` | `s_neck_intake_frame.stl` | CF-PETG structural intake frame ring — bonds into 4 scoop windows at neck station |
| `serenity/stl/s_rear_neck_intake_shell24.scad` | `s_rear_neck_intake_shell24.stl` | Rear fuselage shell with 4 radial scoop windows |
| `serenity/stl/nacelle_pod_50mm_tandem.scad` | `s_eng_left/right_stator_shell24_revo.stl` | **Rev O** complete parametric nacelle pod — 50mm tandem EDFs, 11-fin stator, CG pivot boss (Z=83mm), M=1.0 gear bosses, iris nozzle pocket. Use `SWIRL_DIR=1` (port) / `-1` (stbd). |
| `serenity/stl/nacelle_sector_gear.scad` | `nacelle_sector_gear.stl` | **Rev O** M=1.0 sector gear R=22mm, 38T, 155° arc — fixed to tilt bracket |
| `serenity/stl/nacelle_pinion.scad` | `nacelle_pinion.stl` | **Rev O** M=1.0 spur pinions (drive pinion A + crown pinion), N=12T, D-bore shaft |
| `serenity/stl/nacelle_bevel_pair.scad` | `nacelle_bevel_pair.stl` | **Rev O** M=1.0 bevel gear pair N=14T, 45° pitch cone, 1:1, 90° axis redirect |
| `serenity/stl/nacelle_bevel_housing.scad` | `nacelle_bevel_housing.stl` | **Rev O** CF-PETG housing block 24×14×20mm for bevel gear pair |
| `serenity/stl/nacelle_nozzle_iris.scad` | `nacelle_nozzle_iris.stl` | **Rev O** 50mm iris nozzle — inner ring (M=1.0 rack), outer housing, 8-petal geometry |

### Documentation

| File | Description |
|------|-------------|
| `LICENSE_AND_ATTRIBUTION.md` | Full CC BY 4.0 license, author credentials, all upstream attributions |
| `README.md` | Project overview, quick specs, build guide index, file inventory |
| `MANIFEST.json` | SHA-256 checksums for all project files (integrity verification) |
| `PROJECT_INDEX.md` | This file |
| `AVIONICS_PB2_REDESIGN.md` | **Rev K** — 8-node PocketBeagle 2 cooperative avionics architecture; Cape-A and Cape-B design specs |
| `PHASED_BUILD_GUIDE.md` | **Rev M** — 8-phase phased build, procurement, and flight-test guide (PB2-I boards, eMMC boot, dual-EDF + PID governor) |
| `bom_revP.json` | **Rev P** bill of materials — Rev O baseline + cargo bay complete: 10 new printed cargo parts + SERVO-CARGO, DRV8833-CARGO, DYNEEMA-SK75, FOAM-GASKET-CARGO; cargo section fully detailed; 5 total servos; ~$1,905 est. |
| `bom_revP.csv` | **Rev P** bill of materials (CSV for spreadsheet use) — 91 line items including all Rev O rows + 14 new Rev P cargo rows |
| `bom_revO.json` | **Rev O** bill of materials — CG-pivot nacelle · M=1.0 gear train · 50mm tandem EDF · 24-inch hull · full avionics + antenna system |
| `bom_revO.csv` | **Rev O** bill of materials (CSV for spreadsheet use) — 77 line items including 8 new Rev O gear-train rows; superseded M=0.5 rows retained at Qty=0 for traceability |
| `bom_revN.json` | **Rev N** bill of materials — 50mm EDF upgrade + antenna system |
| `bom_revN.csv` | **Rev N** bill of materials (CSV for spreadsheet use) |
| `bom_revM.json` | Rev M bill of materials (superseded) — PB2-I hardware swap, DigiKey P/N, cost delta, eMMC notes |
| `bom_revL.json` | Rev L bill of materials (superseded) — firmware delta, EDF options, governor commissioning |
| `bom_revK.json` | Rev K bill of materials (superseded) — dual-EDF hardware |
| `bom_revK.csv` | Rev K bill of materials CSV (superseded) |
| `bom_revJ.json` | Rev J bill of materials (historical reference) |
| `bom_revJ.csv` | Rev J bill of materials CSV |
| `serenity-drone-revF.zip` | Complete Rev F project archive — legacy reference |

---

## Quick Specs

| Parameter | Value |
|-----------|-------|
| Hull | **609.6 mm (24.00") Serenity-class** · CC BY 4.0 Peter Farell (printables.com/model/548545) · scale factor 2.9294× |
| Canon basis | QMx Blueprints Mandel/Earls 2007 · 269ft × 170ft × 79ft |
| Canonical beam | 486 mm tip-to-tip · hull height 182 mm (landed) |
| Hull structure | PETG thin shell + 2 lb/ft³ closed-cell PU foam + CF skeleton (6×3mm keel + 12mm OD spar tubes) |
| Propulsion | **2× (2× 50mm EDF @ 6S, tandem series) per nacelle** · pod OD ~60.5 mm × 67 mm · pod length 148.3 mm · 1× 120mm EDF @ 6S rear · Rev O pivot at Z=83mm (nacelle CG) |
| Nozzle linkage | Passive gear train: M=1.0 sector R=22mm → pinion N=12T → bevel pair N=14T 45° → crown N=12T → ring rack R=28mm · ratio 70.7° nozzle per 90° tilt · no dedicated servo |
| Nacelle ESC | 4× 40A 6S BLHeli32 BDSHOT (one per 50mm EDF) · 1× 80A 6S BLHeli32 (120mm rear) |
| Total hover thrust | **~5,322 g** (~1,822 g nacelles + ~3,500 g rear EDF) · T/W ≈1.50 at 6S 4000mAh AUW |
| Governor | **PID closed-loop RPM per EDF** · BDSHOT600 feedback · nacelle equalization (Rev L governor — unchanged) |
| Avionics | **8× PocketBeagle 2 Industrial (AM6254)** · 4× Cape-A (FC nodes) · 4× Cape-B (CN nodes) · DK 2820-100003007-ND · $51.03 ea |
| Avionics dry | ~420 g (8× PB2-I + 4× Cape-A + 4× Cape-B + 4× RCRS-49 + GPS×4 + radios) |
| AUW (Rev O) | **~3,550 g · 6S 4000mAh · T/W ≈1.50** |
| Max payload at T/W=1.0 | **~1,772 g (3.91 lb)** |
| Cruise speed | 38–54 kts (scaled from 35-49kts at 365mm) |
| Transition altitude | ≥30 ft AGL |
| CG target | 190 mm (7.48") from nose |
| Data buses | Ethernet RSTP ring · CAN FD 1Mbps · RS-485 1Mbps · MIL-STD-1553B 1Mbps |
| Radios | SiK 915MHz MAVLink · LoRa RFM95W 915MHz backup · TI WL1837MOD WiFi/BT GCS · RCRS-49MHz RC |
| Security | ATF16V8BQL CPLD write-blocker (Cape-B log μSD) · **SLB9670 TPM 2.0 on all 8 nodes** · NOR flash circular log |
| Navigation lights | 6× WS2812C — ICAO Annex 2 · 14 CFR 91.209 compliant |
| FAA registration | **N00000 PLACEHOLDER — replace before first flight** |
---

## Connectivity Summary (Rev K/L — unchanged)

| Bus | Protocol | Speed | Topology | Notes |
|-----|----------|-------|----------|-------|
| 1 | Ethernet (CPSW3G + DP83825I) | 100 Mbps | **RSTP ring** (8-node, self-healing) | Added Rev E; ring topology Rev K |
| 2 | CAN FD ISO 11898-1 | 1 Mbps / 8 Mbps data | Linear daisy-chain CN1→FC1→CN2→FC2→CN3→FC3→CN4→FC4; 120Ω at CN1 (start) and FC4 (end) | Added Rev E |
| 3 | RS-485 / EIA-485 | 1 Mbps | Multi-drop CN1→…→FC4; 120Ω at CN1 and FC4 | Added Rev G |
| 4 | **MIL-STD-1553B** (PRU Manchester II) | 1 Mbps | BC/RT — FC1=BC, FC2=standby BC; all others RT | Added Rev H; PRU encoder Rev K |
| — | I²C (on-Cape) | 400 kHz | Local sensor bus via TCA9548A mux | Not inter-board |

---

*© 2026 Steve Griffing, PE(CSE) [Control Systems Engineering], CISSP-ISSEP, CPP*  
*CC BY 4.0 · creativecommons.org/licenses/by/4.0*
