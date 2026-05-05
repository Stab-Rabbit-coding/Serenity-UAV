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
| `serenity-rev-f.jsx` | Author attribution + ft/kts/yd units + full license compliance | Rev F ← current master |
| `nacelle-nozzle-gear.jsx` | Variable-area nacelle nozzle gear coupling full design | Rev E |
| `serenity-connectivity-revF.jsx` | 4-bus architecture analysis (Ethernet + CAN FD + RS-485 + I²C) | Rev F connectivity |
| `serenity-connectivity-revG.jsx` | CAN daisy-chain (2nd connector) + RS-485 + I²C inter-board buses | Rev G connectivity |
| `serenity-connectivity-revH.jsx` | **MIL-STD-1553B replaces I²C as 4th active bus** | Rev H connectivity ← current |

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
| `COMPHAT-1.kicad_pcb` | COMPHAT-1 Rev E | 65×48mm | CM4 hat: CAN FD, Ethernet, TPM, NX proxy, log μSD, SiK, RCRS, Zigbee/LoRa |
| `COMPHAT-1.kicad_sch` | COMPHAT-1 Rev E | — | Schematic |

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

### Documentation

| File | Description |
|------|-------------|
| `LICENSE_AND_ATTRIBUTION.md` | Full CC BY 4.0 license, author credentials, all upstream attributions |
| `README.md` | Project overview, quick specs, build guide index, file inventory |
| `MANIFEST.json` | SHA-256 checksums for all 72 files (integrity verification) |
| `PROJECT_INDEX.md` | This file |
| `serenity-drone-revF.zip` | **Complete project archive** — all 72 files in one download (425 KB) |

---

## Quick Specs

| Parameter | Value |
|-----------|-------|
| Hull | 457.2 mm (18.00") Serenity-class · CC BY 4.0 Peter Farell |
| Canon basis | QMx Blueprints Mandel/Earls 2007 · 269ft × 170ft × 79ft |
| Canonical beam | 288.9 mm (11.375") tip-to-tip · **100% canonical** |
| Canonical height | 134.3 mm (5.286") landed |
| Hull structure | PETG thin shell + X-30 expanding foam + CF skeleton · 302g |
| Propulsion | 2× 80mm EDF nacelle (93mm OD · 1700g each @6S) · 1× 40mm fuselage |
| Nacelle span | 288.9 mm tip-to-tip (canonical beam) · C-C 195.9 mm (7.71") |
| Pylon datum | 82.5 mm from CL (1/3 from nacelle inner edge — outward expansion) |
| AUW (empty rec.) | 1,388g · 6S 4000mAh · T/W 2.45 · ~8min hover |
| AUW (cargo 250g rec.) | 1,488g · 6S 2200mAh · T/W 2.28 · ~5min hover |
| Max payload at T/W=2.0 | **462g (16.3oz)** |
| Cruise speed | 38–54 kts (scaled from 35-49kts at 365mm) |
| Transition altitude | ≥30 ft AGL |
| CG target | 152 mm (5.98") from nose |
| Data buses | Ethernet 100BASE-T · CAN FD 4Mbps · RS-485 1Mbps · MIL-STD-1553B 1Mbps |
| Security | CPLD write-blocker · STM32 NX proxy · TPM 2.0 · TrustZone · SELinux |
| Navigation lights | 6× WS2812C — ICAO Annex 2 · 14 CFR 91.209 compliant |
| FAA registration | **N00000 PLACEHOLDER — replace before first flight** |
---

## Connectivity Summary (Rev H)

| Bus | Protocol | Speed | Topology | Added |
|-----|----------|-------|----------|-------|
| 1 | Ethernet 100BASE-T | 100 Mbps | P2P / switch | Rev E |
| 2 | CAN FD ISO 11898-1 | 4 Mbps | Daisy-chain | Rev E (2nd connector Rev G) |
| 3 | RS-485 / EIA-485 | 1 Mbps | Multi-drop bus | Rev G |
| 4 | **MIL-STD-1553B** | 1 Mbps | BC/RT dual-redundant bus | **Rev H** |
| — | I²C (on-PCB) | 400 kHz | Local sensor bus | Rev G (not inter-board) |

---

*© 2026 Steve Griffing, PE(CSE) [Control Systems Engineering], CISSP-ISSEP, CPP*  
*CC BY 4.0 · creativecommons.org/licenses/by/4.0*
