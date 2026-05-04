# Serenity-Class Tiltrotor UAV — License & Attribution

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**Project:** Serenity-Class Tri-Fan Tiltrotor Unmanned Aerial Vehicle  
**Revision:** F (current)  
**License:** Creative Commons Attribution 4.0 International (CC BY 4.0)

---

## License

```
Creative Commons Attribution 4.0 International

Copyright © 2025 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP

You are free to:
  Share  — copy and redistribute the material in any medium or format
  Adapt  — remix, transform, and build upon the material for any purpose,
            even commercially

Under the following terms:
  Attribution — You must give appropriate credit, provide a link to the
                license, and indicate if changes were made. You may do so
                in any reasonable manner, but not in any way that suggests
                the licensor endorses you or your use.

No additional restrictions — You may not apply legal terms or technological
measures that legally restrict others from doing anything the license permits.

Full license text: https://creativecommons.org/licenses/by/4.0/legalcode
```

---

## Author

| Field | Value |
|-------|-------|
| **Name** | Steve Griffing |
| **PE License** | PE(CSE) — Professional Engineer |
| **PE Discipline** | **Control Systems Engineering** |
| **Security Cert.** | CISSP-ISSEP — Information Systems Security Engineering Professional |
| **Physical Sec.** | CPP — Certified Protection Professional (ASIS International) |

---

## Original Creative Work Covered by This License

The following elements are original work by Steve Griffing, released under CC BY 4.0:

- All flight system PCB schematics and layouts (TRIHAT-1, CM4-CARRIER-1 Rev E, COMPHAT-1 Rev E)
- CPLD write-blocker Verilog RTL (`write_blocker.v`)
- STM32 NX-enforcement proxy firmware (`nx_proxy.c`)
- Variable-area nozzle gear-coupling design (sector gear · bevel pair · crown pinion · ring rack)
- Nacelle nozzle gear geometry and STL files
- All KiCad PCB source files in this repository
- Flight controller firmware architecture and algorithm specifications
- 49 MHz RCRS TDDS (Time-Division Dual-Simplex) protocol specification
- All SVG engineering diagrams in `diagrams/`
- All wiring diagrams, pin-out tables, and system integration specifications
- Build guide and assembly documentation
- This license and attribution document

---

## Attribution to Integrated and Adapted Works

### 1. *Firefly* / *Serenity* — Creative Universe

> The hull form and visual design of this UAV are inspired by the **Firefly-class
> transport ship *Serenity*** from the television series *Firefly* (2002) and
> the feature film *Serenity* (2005).

**Original Creators:**

| Role | Name |
|------|------|
| Creator / Executive Producer / Writer | **Joss Whedon** |
| Co-Executive Producer / Writer | Tim Minear |
| Producer / Director | David Solomon |
| Production Designer | Carey Meyer |
| Costume Designer | Shawna Trpcic |
| Visual Effects Supervisor | Loni Peristere |
| Production Company | Mutant Enemy Productions |
| Broadcast Network | Fox Broadcasting Company |
| Feature Film | *Serenity* (2005) — Universal Pictures |
| Film Producer | Barry Mendel |
| Principal Cast | Nathan Fillion · Gina Torres · Alan Tudyk · Morena Baccarin · Adam Baldwin · Jewel Staite · Sean Maher · Summer Glau · Ron Glass |

**Note on Rights:**

The *Firefly* and *Serenity* names, the Firefly-class ship design, and all
associated intellectual property are trademarks and copyrights of their
respective owners (Joss Whedon / Mutant Enemy Productions / Universal Pictures /
20th Century Fox / The Walt Disney Company). This UAV project is a
**non-commercial fan engineering work** that draws **visual inspiration** from
the Serenity's iconic silhouette.

**This project does NOT:**
- Reproduce, distribute, or commercially exploit any copyrighted *Firefly*/*Serenity* artwork, script, soundtrack, or character
- Claim any trademark rights to the name "Serenity"
- Imply endorsement by or affiliation with the rights holders

Commercial products based on this design must obtain appropriate licensing from
rights holders before using the Serenity name or likeness in trade.

---

### 2. Serenity Firefly-Class 3D Model (Hull Geometry Basis)

| Field | Detail |
|-------|--------|
| **Title** | Serenity, Firefly Class |
| **Author** | Peter Farell |
| **Source** | [printables.com/model/548545](https://www.printables.com/model/548545) |
| **License** | CC BY 4.0 |
| **Use** | Hull outer geometry adapted; scaled to 365 mm (14.4"); hollowed to 1.5 mm thin-wall shell; structurally redesigned with CF skeleton for UAV flight loads. |

**Remix attribution template:**
```
Hull: "Serenity, Firefly Class" by Peter Farell
printables.com/model/548545 · CC BY 4.0
Remixed by Steve Griffing: scaled 365mm (14.4"), hollowed thin-wall,
CF skeleton added. CC BY 4.0.
```

---

### 3. Variable-Area EDF Nozzle (Nozzle Mechanism Basis)

| Field | Detail |
|-------|--------|
| **Title** | Variable Area EDF Nozzles |
| **Author** | BamJr |
| **Source** | [thingiverse.com/thing:2991269](https://www.thingiverse.com/thing:2991269) |
| **License** | CC BY 4.0 |
| **Use (nacelle)** | Scaled to 70 mm (2.76") ID. Servo removed. M0.5 rack teeth added to inner ring OD. Outer housing integrated with Serenity bell geometry. Gear-coupled to nacelle tilt pivot via sector/bevel/crown chain — fully passive, no servo. |
| **Use (fuselage)** | Scaled to 40 mm (1.57") ID. SG90 servo actuation retained. Integrated with Serenity engine bell. |

**Remix attribution template:**
```
Nozzle: "Variable Area EDF Nozzles" by BamJr
thingiverse.com/thing:2991269 · CC BY 4.0
Remixed by Steve Griffing:
  Nacelle — 70mm (2.76") ID, servo removed, M0.5 rack teeth added,
  gear-coupled to nacelle tilt pivot (sector/bevel/crown chain).
  Fuselage — 40mm (1.57") ID, SG90 servo actuated, Serenity bell integrated.
CC BY 4.0.
```

---

## Third-Party Software and Firmware

| Component | Version | License | Notes |
|-----------|---------|---------|-------|
| Raspberry Pi Pico SDK | ≥2.0 | BSD-3-Clause | RP2350 HAL |
| Mahony AHRS (port) | custom | Apache-2.0 | Attitude filter |
| MAVLink 2.0 C library | 2.0 | MIT/LGPL | Protocol encoder |
| W5500 ioLibrary | 3.x | BSD-3-Clause | Ethernet driver |
| FreeRTOS-Kernel (opt.) | 10.6 | MIT | RTOS scheduler |
| Raspberry Pi OS Lite | bookworm | Mixed GPL | CM4 OS |
| mavlink-router | ≥3.0 | Apache-2.0 | MAVLink router |
| MAVSDK-Python | ≥2.0 | BSD-3-Clause | Drone API |
| python-can | ≥4.0 | LGPL-3.0 | CAN bus interface |
| dronecan (Python) | ≥1.0 | MIT | DroneCAN stack |
| pymavlink | ≥2.4 | LGPL | MAVLink serial. |
| tpm2-tools | ≥5.0 | BSD-2-Clause | TPM 2.0 CLI |
| tpm2-tss | ≥4.0 | BSD-2-Clause | TPM stack |
| SELinux (kernel) | kernel | GPL-2.0 | MAC enforcement |
| spi-bcm2835 (kernel) | kernel | GPL-2.0 | SPI driver |
| SiK radio firmware | 2.x | GPL-3.0 | 915 MHz radio FW |
| LoRaLib | ≥5.0 | MIT | SX1276 driver |
| TI CC2652P7 Z-Stack | TI SDK | TI TSPA | Zigbee 2.4 GHz |
| QGroundControl | ≥4.3 | GPL-3.0 | GCS application |
| Mission Planner | ≥1.3 | GPL-3.0 | Alt. GCS |

> **GPL notice:** GPL-2.0 and GPL-3.0 components must remain open-source
> if redistributed in modified form. Consult qualified legal counsel before
> building closed-source commercial products.
>
> **TI TSPA notice:** Z-Stack commercial distribution requires TI license
> review at ti.com/lit/pdf/snda022.

---

## Regulatory Notices

This UAV **exceeds 250 g AUW** in all configurations.

| Jurisdiction | Authority | Key Requirement |
|-------------|-----------|-----------------|
| United States | FAA | Registration + Part 107 RPIC for commercial ops |
| European Union | EASA | C1/C2 class registration |
| United Kingdom | CAA | A2 CofC for sub-400 ft BVLOS |
| Canada | Transport Canada | Advanced Operations cert may apply |
| Australia | CASA | ReOC may be required for commercial ops |

Navigation lights comply with **ICAO Annex 2** and **14 CFR 91.209**.
Verify local night-operations requirements before flight.

---

## File Inventory

```
serenity-drone/
├── docs/
│   └── LICENSE_AND_ATTRIBUTION.md   ← this file
├── diagrams/
│   ├── overview_top.svg
│   ├── overview_side.svg
│   ├── overview_front.svg
│   ├── overview_bottom.svg
│   ├── components_overview.svg
│   └── build_plan.svg
├── pcb/
│   ├── TRIHAT-1/
│   │   ├── TRIHAT-1.kicad_sch
│   │   └── TRIHAT-1.kicad_pcb
│   ├── CM4-CARRIER-1/
│   │   ├── CM4-CARRIER-1.kicad_sch
│   │   └── CM4-CARRIER-1.kicad_pcb
│   └── COMPHAT-1/
│       ├── COMPHAT-1.kicad_sch
│       └── COMPHAT-1.kicad_pcb
└── stl/
    ├── hull_cockpit_cap.stl
    ├── hull_cockpit_section.stl
    ├── hull_mid_body_left.stl
    ├── hull_mid_body_right.stl
    ├── hull_aft_neck.stl
    ├── hull_engine_bell.stl
    ├── nacelle_pod_70mm.stl
    ├── nacelle_tip_cap_port.stl
    ├── nacelle_tip_cap_stbd.stl
    ├── tilt_bracket_cf_petg.stl
    ├── sector_gear_22mm.stl
    ├── nozzle_inner_ring_70mm.stl
    ├── nozzle_outer_housing_70mm.stl
    ├── nozzle_flap_x8.stl
    ├── nozzle_inner_ring_40mm.stl
    ├── nozzle_outer_housing_40mm.stl
    ├── bevel_gear_housing.stl
    ├── pinion_a_bracket.stl
    ├── dorsal_antenna_fin.stl
    ├── payload_bay_door.stl
    ├── landing_skid_foot.stl
    └── cockpit_dome_clear.stl
```

---

## Suggested Full Attribution Block

```
Serenity-Class Tiltrotor UAV
© 2025 Steve Griffing, PE(CSE) [Control Systems Engineering],
CISSP-ISSEP, CPP. CC BY 4.0.

Incorporates:
• Hull: "Serenity, Firefly Class" by Peter Farell
  printables.com/model/548545 · CC BY 4.0
• Nozzle: "Variable Area EDF Nozzles" by BamJr
  thingiverse.com/thing:2991269 · CC BY 4.0
• Visual inspiration: Firefly (Fox/Mutant Enemy, 2002) /
  Serenity (Universal Pictures, 2005)
  © Joss Whedon · Non-commercial fan engineering work.
  Not an officially licensed product.
```

---

*This document is itself released under CC BY 4.0.*  
*Last updated: 2025*
