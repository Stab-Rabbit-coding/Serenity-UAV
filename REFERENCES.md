# REFERENCES.md — Serenity UAV Standards and Regulatory Reference Catalog

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Revision:** S
**Last updated:** 2026-07-20
**Revision history:** Rev R (2026-06-10) → Rev R1 (2026-06-11, hull-frame bake) → Rev S
(2026-07-04, comprehensive checkpoint — integrates all Rev R1/R1c/R1d/R2 modifications;
see TODO.md "Rev S Checkpoint" for the full consolidated changelog) → 2026-07-20 (added the
Creative-Universe Attribution section and the `docs/references/` canonical-reference library:
REF-CAD-003 QMx 2007 Blueprints pack, REF-CAD-004 misubisu Thingiverse origin model; expanded
REF-CAD-002 Nick Henning after consolidation)

---

## Table of Contents

- [Creative-Universe Attribution and Fan-Engineering Terms](#creative-universe-attribution-and-fan-engineering-terms)
- [Standards Vetting Policy](#standards-vetting-policy)
- [Citation Format](#citation-format)
- [Part I — United States Federal Aviation Regulations](#part-i--united-states-federal-aviation-regulations)
    - [REF-FAA-001: 14 CFR Part 48 — Registration and Marking Requirements for Small Unmanned Aircraft Systems](#ref-faa-001-14-cfr-part-48--registration-and-marking-requirements-for-small-unmanned-aircraft-systems)
    - [REF-FAA-002: 14 CFR Part 107 — Small Unmanned Aircraft Systems](#ref-faa-002-14-cfr-part-107--small-unmanned-aircraft-systems)
    - [REF-FAA-003: 14 CFR §91.209 — Aircraft Lights](#ref-faa-003-14-cfr-91209--aircraft-lights)
- [Part II — United States Federal Communications Commission Regulations](#part-ii--united-states-federal-communications-commission-regulations)
    - [REF-FCC-001: 47 CFR §15.247 — Operation within the bands 902–928 MHz, 2400–2483.5 MHz, and 5725–5850 MHz](#ref-fcc-001-47-cfr-15247--operation-within-the-bands-902928-mhz-240024835-mhz-and-57255850-mhz)
    - [REF-FCC-002: 47 CFR Part 15 Subpart E — Unlicensed National Information Infrastructure Devices (UNII)](#ref-fcc-002-47-cfr-part-15-subpart-e--unlicensed-national-information-infrastructure-devices-unii)
    - [REF-FCC-003: 47 CFR Part 15 §15.235 — Operation Within the Band 49.82–49.90 MHz](#ref-fcc-003-47-cfr-part-15-15235--operation-within-the-band-49824990-mhz)
    - [REF-FCC-004: 47 CFR Part 95 Subpart C — Radio Control Radio Service (RCRS) — Evaluated and Rejected for Emma's 49 MHz Link](#ref-fcc-004-47-cfr-part-95-subpart-c--radio-control-radio-service-rcrs--evaluated-and-rejected-for-emmas-49-mhz-link)
- [Part III — NIST Security Standards](#part-iii--nist-security-standards)
    - [REF-NIST-001: NIST SP 800-207 — Zero Trust Architecture](#ref-nist-001-nist-sp-800-207--zero-trust-architecture)
    - [REF-NIST-002: NIST SP 800-82 Rev 3 — Guide to Operational Technology (OT) Security](#ref-nist-002-nist-sp-800-82-rev-3--guide-to-operational-technology-ot-security)
    - [REF-NIST-003: NIST SP 800-160 Vol 1 Rev 1 — Engineering Trustworthy Secure Systems](#ref-nist-003-nist-sp-800-160-vol-1-rev-1--engineering-trustworthy-secure-systems)
    - [REF-NIST-004: NIST SP 800-92 — Guide to Computer Security Log Management](#ref-nist-004-nist-sp-800-92--guide-to-computer-security-log-management)
- [Part IV — Defense Standards](#part-iv--defense-standards)
    - [REF-MIL-001: MIL-STD-1553B — Aircraft Internal Time Division Command/Response Multiplex Data Bus](#ref-mil-001-mil-std-1553b--aircraft-internal-time-division-commandresponse-multiplex-data-bus)
    - [REF-MIL-002: MIL-STD-461G — Requirements for the Control of Electromagnetic Interference Characteristics of Subsystems and Equipment](#ref-mil-002-mil-std-461g--requirements-for-the-control-of-electromagnetic-interference-characteristics-of-subsystems-and-equipment)
- [Part V — International Standards (ISO, IEC)](#part-v--international-standards-iso-iec)
    - [REF-ISO-001: ISO 11898-1:2015 — Road Vehicles — Controller Area Network (CAN) — Part 1: Data Link Layer and Physical Signalling](#ref-iso-001-iso-11898-12015--road-vehicles--controller-area-network-can--part-1-data-link-layer-and-physical-signalling)
    - [REF-IEC-001: IEC 62368-1 Ed. 3.0 — Audio/Video, Information and Communication Technology Equipment — Part 1: Safety Requirements](#ref-iec-001-iec-62368-1-ed-30--audiovideo-information-and-communication-technology-equipment--part-1-safety-requirements)
    - [REF-IEC-002: IEC 60825-1:2014+AMD1:2021 — Safety of Laser Products — Part 1: Equipment Classification and Requirements](#ref-iec-002-iec-60825-12014amd12021--safety-of-laser-products--part-1-equipment-classification-and-requirements)
    - [REF-IEC-003: IEC 61000-4-2:2008 — Electromagnetic Compatibility (EMC) — Testing and Measurement Techniques — Electrostatic Discharge (ESD) Immunity Test](#ref-iec-003-iec-61000-4-22008--electromagnetic-compatibility-emc--testing-and-measurement-techniques--electrostatic-discharge-esd-immunity-test)
    - [REF-IEC-004: IEC 61000-4-4:2012 — Electromagnetic Compatibility (EMC) — Testing and Measurement Techniques — Electrical Fast Transient/Burst (EFT/Burst) Immunity Test](#ref-iec-004-iec-61000-4-42012--electromagnetic-compatibility-emc--testing-and-measurement-techniques--electrical-fast-transientburst-eftburst-immunity-test)
    - [REF-IEC-005: IEC 61000-4-5:2014+AMD1:2017 — Electromagnetic Compatibility (EMC) — Testing and Measurement Techniques — Surge Immunity Test](#ref-iec-005-iec-61000-4-52014amd12017--electromagnetic-compatibility-emc--testing-and-measurement-techniques--surge-immunity-test)
    - [REF-VDE-001: VDE V 0884-11:2017-01 — Optocouplers for Use in Electrical Equipment — Test and Measurement Methods](#ref-vde-001-vde-v-0884-112017-01--optocouplers-for-use-in-electrical-equipment--test-and-measurement-methods)
- [Part V-A — IPC PCB Design Standards](#part-va--ipc-pcb-design-standards)
    - [REF-IPC-001: IPC-2221 — Design Guidelines for Printed Board Layout (PCB Design Fundamentals)](#ref-ipc-001-ipc-2221--design-guidelines-for-printed-board-layout-pcb-design-fundamentals)
    - [REF-IPC-002: IPC-A-600 — Acceptability of Printed Boards](#ref-ipc-002-ipc-a-600--acceptability-of-printed-boards)
- [Part VI — IEEE Standards](#part-vi--ieee-standards)
    - [REF-IEEE-001: IEEE 802.3-2022 — Ethernet (CSMA/CD Access Method and Physical Layer Specifications)](#ref-ieee-001-ieee-8023-2022--ethernet-csmacd-access-method-and-physical-layer-specifications)
    - [REF-IEEE-002: IEEE 802.11-2020 — Wireless LAN Medium Access Control (MAC) and Physical Layer (PHY) Specifications](#ref-ieee-002-ieee-80211-2020--wireless-lan-medium-access-control-mac-and-physical-layer-phy-specifications)
    - [REF-IEEE-003: IEEE 802.15.4-2020 — Low-Rate Wireless Networks](#ref-ieee-003-ieee-802154-2020--low-rate-wireless-networks)
- [Part VII — ISA/IEC Industrial Cybersecurity Standards](#part-vii--isaiec-industrial-cybersecurity-standards)
    - [REF-ISA-001: ISA/IEC 62443-3-3:2013 — Industrial Automation and Control Systems Security — System Security Requirements and Security Levels](#ref-isa-001-isaiec-62443-3-32013--industrial-automation-and-control-systems-security--system-security-requirements-and-security-levels)
- [Part VIII — ICAO Standards](#part-viii--icao-standards)
    - [REF-ICAO-001: ICAO Annex 2 — Rules of the Air](#ref-icao-001-icao-annex-2--rules-of-the-air)
- [Part IX — Protocol References](#part-ix--protocol-references)
    - [REF-PROTO-001: AX.25 Link Access Protocol for Amateur Packet Radio](#ref-proto-001-ax25-link-access-protocol-for-amateur-packet-radio)
    - [REF-PROTO-002: MAVLink v2 Protocol Specification](#ref-proto-002-mavlink-v2-protocol-specification)
- [Part X — AUVSI, ASTM F38, and Industry Frameworks](#part-x--auvsi-astm-f38-and-industry-frameworks)
    - [REF-AUVSI-001: AUVSI Trusted Operator Program (TOP) and XCELLENCE Safety Standards](#ref-auvsi-001-auvsi-trusted-operator-program-top-and-xcellence-safety-standards)
    - [REF-ASTM-001: ASTM F2910-22 — Design and Construction of a Small Unmanned Aircraft System (sUAS)](#ref-astm-001-astm-f2910-22--design-and-construction-of-a-small-unmanned-aircraft-system-suas)
    - [REF-ASTM-002: ASTM F3005-22 — Batteries for Use in Small Unmanned Aircraft Systems (sUAS)](#ref-astm-002-astm-f3005-22--batteries-for-use-in-small-unmanned-aircraft-systems-suas)
    - [REF-ASTM-003: ASTM F3269-21 — Methods to Safely Bound Behavior of Aircraft Systems Containing Complex Functions Using runtime assurance](#ref-astm-003-astm-f3269-21--methods-to-safely-bound-behavior-of-aircraft-systems-containing-complex-functions-using-runtime-assurance)
- [Part XI — FDA / CDRH Laser Product Regulations](#part-xi--fda--cdrh-laser-product-regulations)
    - [REF-FDA-001: 21 CFR Part 1040 — Performance Standards for Light-Emitting Products](#ref-fda-001-21-cfr-part-1040--performance-standards-for-light-emitting-products)
- [Part XII — Sensor and Component Specifications](#part-xii--sensor-and-component-specifications)
    - [REF-SENSOR-001: RunCam Nano 4 — 19 mm Nano Format FPV Camera Specification (SUPERSEDED)](#ref-sensor-001-runcam-nano-4--19-mm-nano-format-fpv-camera-specification-superseded)
    - [REF-SENSOR-002: Benewake TFmini-S — Long-Range Time-of-Flight Ranging Module Specification](#ref-sensor-002-benewake-tfmini-s--long-range-time-of-flight-ranging-module-specification)
    - [REF-SENSOR-003: TI AM62Ax Sitara Processors — Vision SoC Datasheet](#ref-sensor-003-ti-am62ax-sitara-processors--vision-soc-datasheet)
    - [REF-SENSOR-004: TI MSPM0G3507 — Mixed-Signal MCU with CAN-FD Interface](#ref-sensor-004-ti-mspm0g3507--mixed-signal-mcu-with-can-fd-interface)
    - [REF-SENSOR-005: Microchip KSZ9477 — Ethernet Switch with HSR/PRP Hardware Redundancy](#ref-sensor-005-microchip-ksz9477--ethernet-switch-with-hsrprp-hardware-redundancy)
    - [REF-SENSOR-006: TI TCAN1042HG-Q1 — CAN-FD Transceiver](#ref-sensor-006-ti-tcan1042hg-q1--can-fd-transceiver)
    - [REF-SENSOR-008: AKM AK7455 — 14-bit Off-Axis Magnetic Rotation Angle Sensor](#ref-sensor-008-akm-ak7455--14-bit-off-axis-magnetic-rotation-angle-sensor)
    - [REF-SENSOR-009: TI ISOW1044BDFMR — 5 kVrms Isolated CAN-FD Transceiver with Integrated Isolated DC-DC](#ref-sensor-009-ti-isow1044bdfmr--5-kvrms-isolated-can-fd-transceiver-with-integrated-isolated-dc-dc)
    - [REF-SENSOR-010: TI ISOW1412 — 5 kVrms Isolated RS-485/RS-422 Transceiver with Integrated Isolated DC-DC](#ref-sensor-010-ti-isow1412--5-kvrms-isolated-rs-485rs-422-transceiver-with-integrated-isolated-dc-dc)
    - [REF-SENSOR-011: Infineon OPTIGA™ SLB 9670 — SPI TPM 2.0](#ref-sensor-011-infineon-optiga-slb-9670--spi-tpm-20)
    - [REF-SENSOR-012: STS3215 Digital Servo Motor — Cargo Winch Control](#ref-sensor-012-sts3215-digital-servo-motor--cargo-winch-control)
- [Part XIII — Telecommunications Standards](#part-xiii--telecommunications-standards)
    - [REF-TIA-001: ANSI/TIA-485-A — Electrical Characteristics of Generators and Receivers for Use in Balanced Digital Multipoint Systems (RS-485)](#ref-tia-001-ansitia-485-a--electrical-characteristics-of-generators-and-receivers-for-use-in-balanced-digital-multipoint-systems-rs-485)
- [Part XIV — Upstream CAD / Derivative-Source Attributions](#part-xiv--upstream-cad--derivative-source-attributions)
- [Removed / Superseded Citations](#removed--superseded-citations)
- [Open Standards Verification Items](#open-standards-verification-items)

---

## Creative-Universe Attribution and Fan-Engineering Terms

This catalog is the standards/regulatory index; it is **not** the project's licensing document.
The authoritative, full attribution chain — original creators, cast/crew, upstream CAD authors,
and third-party software licenses — is
[`current-specification/LICENSE_AND_ATTRIBUTION.md`](current-specification/LICENSE_AND_ATTRIBUTION.md),
and the project's own license text is the root [`LICENSE`](LICENSE) (CC BY 4.0). This section is a
**summary with cross-references**, recorded here so that the creative-universe rights holders — never
previously named in this file — are acknowledged wherever this catalog is read.

### Project license (this work)

All original work in this repository is © 2025 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP, released
under **Creative Commons Attribution 4.0 International (CC BY 4.0)** —
<https://creativecommons.org/licenses/by/4.0/>. You may share and adapt it, including commercially,
with appropriate credit, a link to the license, and an indication of changes; attribution must not
imply endorsement by the licensor or by any rights holder named below. Full terms: root
[`LICENSE`](LICENSE).

### *Firefly* / *Serenity* creative universe (underlying IP)

The hull form and visual identity of this UAV draw **visual inspiration** from the Firefly-class
transport ship *Serenity*, and the avionics/role naming scheme (Malcolm, Wash, Zoë, Kaylee, Jayne,
Emma, Shepherd's Room, Inara's Shuttle, River's Room, Simon's Medbay) is drawn from the same
characters. The names, ship design, characters, and all associated intellectual property are the
trademarks and copyrights of their respective rights holders:

| Role / Rights | Party |
|---|---|
| Creator / Executive Producer / Writer | Joss Whedon |
| Co-Executive Producer / Writer | Tim Minear |
| Production company (series) | Mutant Enemy Productions |
| *Firefly* TV series (2002) | 20th Century Fox Television; broadcast on Fox Broadcasting Company — Fox film/TV assets now held by **The Walt Disney Company** (20th Television) |
| *Serenity* feature film (2005) | **Universal Pictures**; producer Barry Mendel |
| Principal cast | Nathan Fillion · Gina Torres · Alan Tudyk · Morena Baccarin · Adam Baldwin · Jewel Staite · Sean Maher · Summer Glau · Ron Glass |
| Official licensed blueprints | Quantum Mechanix Inc. (QMx), under license — see [REF-CAD-003](#ref-cad-003-qmx--the-official-serenity-blueprints-reference-pack-2007) |

### Fan-engineering terms

This project is a **non-commercial fan-engineering work**. It draws visual inspiration from
Serenity's silhouette and reuses character names for subsystem identifiers only. It does **not**:

- reproduce, redistribute, or commercially exploit any copyrighted *Firefly* / *Serenity* artwork,
  script, footage, soundtrack, model mesh, or character likeness;
- claim any trademark right in the name "Serenity," "Firefly," or any character name;
- imply endorsement by, affiliation with, or official status granted by any rights holder
  (consistent with CC BY 4.0 §2(a)(6) "No endorsement").

Any commercial product derived from this design must obtain appropriate licensing from the rights
holders before using the Serenity/Firefly name or likeness in trade. Reference materials that are
themselves copyrighted commercial products (e.g. the QMx blueprint pack, REF-CAD-003) are retained
**for internal design reference only** and are **not** relicensed under CC BY 4.0.

### Canonical-accuracy reference hierarchy

For questions of shape/proportion fidelity to the canonical ship, consult the
`docs/references/` library in this authority order (highest first). This ranking is restated for
agents in `airframe/AGENTS.md` and `docs/AGENTS.md`:

1. **QMx *Official Serenity Blueprints Reference Pack* (2007)** — [REF-CAD-003](#ref-cad-003-qmx--the-official-serenity-blueprints-reference-pack-2007). Most authoritative; officially licensed canon, but line-art level — lacks fine mechanical detail.
2. **Nick Henning render collection** — [REF-CAD-002](#ref-cad-002-nick-henning--firefly-class-serenity-wing-and-landing-gear-reference-renders). Higher mesh/surface detail, derived from the show/QMx canon; used where the blueprints are ambiguous.
3. **misubisu Thingiverse model, Thing 7330462** — [REF-CAD-004](#ref-cad-004-misubisu--serenity-firefly-with-landing-gear-and-swivel-engines-thingiverse-thing-7330462). The origin of the project's `s_*.stl` geometry; still used, but **verify against the two more-authoritative sources above** before treating any detail as canonical.

---

## Standards Vetting Policy

Every design specification that has any effect beyond cosmetic appearance **must** be vetted
against applicable industry standards and/or regulations before implementation.  This file
catalogs every standard and regulation that governs any aspect of this project.  It is the
authoritative index of:

1. The standard's designation and full title
2. A validated URL for official access (verified against the issuing body's site)
3. The specific chapters, sections, and paragraphs applied
4. Every location in the repository where the standard is cited

**Citations in code and documentation** shall reference the standard's REF-ID from this
catalog, e.g. `[REF-FCC-001 §15.247(b)(3)(ii)]`, and shall include chapter, section, and
paragraph to the extent applicable, to facilitate independent audit.

**No fabricated or unverifiable references are permitted.**  Every entry in this catalog
has been verified against the issuing body's official publication list or the U.S. eCFR.
References that appeared in earlier project files but could not be verified, or that
were incorrectly attributed, are documented in the "Removed / Superseded Citations"
section at the end of this file.

---

## Citation Format

In source code comments, documentation, and schematics, cite standards as follows:

```text
[REF-ID §section.subsection] — Short description of what is applied
```

Examples:

- `[REF-MIL-001 §4.1] Manchester II encoding at 1 Mbps, 78 Ω characteristic impedance`
- `[REF-FCC-001 §15.247(b)(3)(ii)] directional antenna gain > 6 dBi: reduce Tx 1 dB per 3 dB above 6 dBi`
- `[REF-NIST-001 §2.1] all messages digitally signed and authenticated`

When a standard has multiple applicable clauses, list them all:

```text
[REF-IEC-001 Cl.5.5.2] and [REF-VDE-001 Cl.4.3] — 5 kV reinforced insulation barrier
```

---

## Part I — United States Federal Aviation Regulations

### REF-FAA-001: 14 CFR Part 48 — Registration and Marking Requirements for Small Unmanned Aircraft Systems

| Field | Value |
|---|---|
| **Issuing authority** | Federal Aviation Administration (FAA), U.S. Dept. of Transportation |
| **Current edition** | As amended through 2024 |
| **Official URL** | <https://www.ecfr.gov/current/title-14/chapter-I/subchapter-F/part-48> |

**Sections applied in this project:**

| Section | Title | Application |
|---|---|---|
| §48.25 | Eligibility for registration | All UAS > 0.55 lbs (250 g) must be registered |
| §48.205(a) | Display of unique identifier | Registration number on exterior |
| §48.205(b)(1) | Legibility of identifier | Minimum 3-inch (76 mm) characters clearly visible |

**Used in:** `docs/REVN_BUILD_GUIDE_24IN.md`, `graphical-build-guide/decal_sheet.svg`,
`README.md`, `TODO.md`, `AGENTS.md`, `avionics/firmware/common/include/ax25_types.h`

---

### REF-FAA-002: 14 CFR Part 107 — Small Unmanned Aircraft Systems

| Field | Value |
|---|---|
| **Issuing authority** | FAA, U.S. Dept. of Transportation |
| **Current edition** | As amended through 2024 |
| **Official URL** | <https://www.ecfr.gov/current/title-14/chapter-I/subchapter-F/part-107> |

**Sections applied in this project:**

| Section | Title | Application |
|---|---|---|
| §107.3 | Definitions | "Small unmanned aircraft" definition applicable |
| §107.29 | Daylight operation | Must operate in daylight or civil twilight with anti-collision lighting |
| §107.31 | Visual line of sight (VLOS) aircraft operation | Remote PIC/visual observer must maintain unaided VLOS with the aircraft throughout flight |
| §107.51(a) | Maximum groundspeed | ≤ 87 kt (100 mph) |
| §107.51(b) | Maximum altitude | ≤ 400 ft AGL (unless within 400 ft of a structure) |
| §107.51(c) | Minimum visibility | ≥ 3 statute miles from pilot's control station |
| §107.51(d) | Minimum distance from clouds | 500 ft below, 2,000 ft horizontal |

**Used in:** `docs/REVN_BUILD_GUIDE_24IN.md`, `graphical-build-guide/build_guide_18_first_flight.svg`,
`README.md`, `TODO.md`, `AGENTS.md`, `airframe/openscad/fuselage/bow_sensor_pod.scad`

---

### REF-FAA-003: 14 CFR §91.209 — Aircraft Lights

| Field | Value |
|---|---|
| **Issuing authority** | FAA |
| **Official URL** | <https://www.ecfr.gov/current/title-14/chapter-I/subchapter-F/part-91/subpart-C/section-91.209> |
| **Companion guidance** | FAA Advisory Circular AC 107-2B (UAS operations under Part 107) — <https://www.faa.gov/regulations_policies/advisory_circulars/> |

**Sections applied in this project:**

| Section | Title | Application |
|---|---|---|
| §91.209(a) | Position lights | Aircraft must display lighted red (port), green (starboard), and white (aft) position lights during night operations |
| §91.209(b) | Anti-collision light | Required for aircraft with a standard airworthiness certificate; applicable to UAS by AC 107-2B guidance |

**Applied to:** Navigation light subsystem — 6× WS2812C-2020 RGB LEDs (port red, starboard green,
aft white); controlled by FC4 node (Simon's medbay, Bay E).

**Used in:** `graphical-build-guide/build_guide_13_nav_lights.svg`, `docs/REVN_BUILD_GUIDE_24IN.md`,
`README.md`, `TODO.md`, `AGENTS.md`

---

## Part II — United States Federal Communications Commission Regulations

> "Can't stop the signal." — Mr. Universe. We can, however, stay inside Part 15/95 limits while we transmit it.

### REF-FCC-001: 47 CFR §15.247 — Operation within the bands 902–928 MHz, 2400–2483.5 MHz, and 5725–5850 MHz

| Field | Value |
|---|---|
| **Issuing authority** | Federal Communications Commission (FCC) |
| **Official URL** | <https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-C/section-15.247> |
| **Parent part** | 47 CFR Part 15 — <https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15> |

**Sections applied in this project:**

| Section | Title | Application |
|---|---|---|
| §15.247(a)(1) | Frequency band | Operation in 902–928 MHz ISM band |
| §15.247(a)(2) | Frequency band | Operation in 2400–2483.5 MHz ISM band |
| §15.247(b)(3)(i) | Power limit | Max 1 W (30 dBm) conducted output for frequency-hopping and direct-sequence systems |
| §15.247(b)(3)(ii) | Directional antenna rule | For antennas > 6 dBi, reduce conducted Tx power 1 dB per 3 dB above 6 dBi, such that total EIRP ≤ 30 dBm |

**Applied to:** SiK 915 MHz MAVLink (RFD900x), LoRa 915 MHz (RFM95W), Zigbee 2.4 GHz (CC2652R7)

**Used in:** `gcs/malcolm/hardware/docs/malcolm_antenna_spec.md`, `TODO.md`, `AGENTS.md`,
`avionics/firmware/dts/cape-b/k3-am6254-pocketbeagle2-serenity-cape-b2.dts`

---

### REF-FCC-002: 47 CFR Part 15 Subpart E — Unlicensed National Information Infrastructure Devices (UNII)

| Field | Value |
|---|---|
| **Issuing authority** | FCC |
| **Official URL** | <https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-E> |

**Sections applied in this project:**

| Section | Title | Application |
|---|---|---|
| §15.407(a)(3) | Power limits — UNII-3 | Maximum EIRP 30 dBm in the 5725–5850 MHz band |
| §15.407(c) | Spurious emissions | Applied to WL1837MOD 5 GHz output |

**Applied to:** TI WL1837MOD Wi-Fi 5 GHz link (UNII-3 band); Tx power must be reduced to
17 dBm conducted when a 14 dBi directional antenna is connected to maintain EIRP ≤ 30 dBm.

**Used in:** `gcs/malcolm/hardware/docs/malcolm_antenna_spec.md`, `TODO.md`, `AGENTS.md`

---

### REF-FCC-003: 47 CFR Part 15 §15.235 — Operation Within the Band 49.82–49.90 MHz

| Field | Value |
|---|---|
| **Issuing authority** | FCC |
| **Official URL** | <https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-C/section-15.235> |

> **Correction (2026-06-20):** Earlier project revisions cited the Emma 49 MHz link against
> 47 CFR **Part 95** (Radio Control Radio Service, RCRS).  Part 95 Subpart C RCRS covers only
> the 26–28 MHz, 72 MHz, and 75 MHz bands — it does **not** include 49 MHz.  The 49.82–49.90 MHz
> band is an unlicensed, license-exempt intentional-radiator band governed by **47 CFR Part 15
> Subpart C §15.235**, not Part 95.  The previous "RCRS"/"TDDS"/"LERS"/"27 channels" terminology
> could not be traced to any verifiable Part 95 text and has been removed; see "Removed /
> Superseded Citations" below.

**Regulatory provisions applied in this project:**

| Provision | Description | Citation |
|---|---|---|
| Field strength limit | Fundamental emission ≤ 10,000 µV/m at 3 m (average detector); peak limits of §15.35 also apply | §15.235(a) |
| Band-edge attenuation | Emissions within 10 kHz of the 49.82/49.90 MHz band edges attenuated ≥ 26 dB below the unmodulated carrier level, or to the general §15.209 limit, whichever is the lesser attenuation (more permissive) | §15.235(b) |
| Out-of-band emissions | Emissions removed more than 10 kHz from the band edge must meet the general radiated-emission limits of §15.209 | §15.209, §15.235(b) |
| Certification disclosure | Any emission exceeding 20 µV/m at 3 m must be disclosed in the equipment certification application | §15.235(c) |
| No-interference-protection | Device must accept interference from other sources and must not cause harmful interference; operates on an unprotected, license-exempt basis | §15.5 |
| Antenna restriction | No antenna other than that furnished by the manufacturer may be used; a permanently attached antenna or a unique (non-standard) coupling satisfies this; **"the use of a standard antenna jack or electrical connector is prohibited"**, even where the manufacturer permits user replacement of a broken antenna | §15.203 |
| Equipment authorization | Requires FCC Certification through a Telecommunication Certification Body (TCB) prior to marketing; device must bear an FCC ID and Part 15 compliance statement | §2.803, §15.19 |

**Applied to:** Emma (XCVR-49MHZ-2) 49 MHz AX.25 link; River's Room and Simon's Medbay nodes only.
No operator or station license is required — the band is license-exempt under Part 15, not
because it is an RCRS personal radio service.

**§15.203 finding — confirmed violation, resolved in design (verified/resolved
2026-06-20):** §15.203's design obligation is imposed directly on "the responsible
party" — i.e., the manufacturer/certificate holder — not on third parties who might later swap
an antenna. Self-manufacture creates no exception: the rule exists specifically to constrain what
the manufacturer is permitted to ship, and the manufacturer bears the equipment-authorization
burden under §2.803/§15.19 above. The rule text is unambiguous that a standard antenna
jack/connector is prohibited regardless of who installs or swaps the antenna: *"An intentional
radiator shall be designed to ensure that no antenna other than that furnished by the responsible
party shall be used with the device. The use of a permanently attached antenna or of an antenna
that uses a unique coupling to the intentional radiator shall be considered sufficient to comply
with the provisions of this section. The manufacturer may design the unit so that a broken antenna
can be replaced by the user, but the use of a standard antenna jack or electrical connector is
prohibited."* (47 CFR §15.203, <https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-C/section-15.20>3).
The section also exempts carrier-current devices and intentional radiators that must be
professionally installed and measured at the installation site (e.g., perimeter protection
systems, field disturbance sensors) — Emma is neither, so no exemption applies. Per
`gcs/malcolm/hardware/docs/malcolm_wiring.md`, Emma's RF port previously used a standard SMA
connector (Amphenol 132289) on both the aircraft and Malcolm GCS sub-modules — **this was a
confirmed §15.203 violation**. **Resolution (2026-06-20):** J2 is now specified as Amphenol
**132289RP**, the reverse-polarity (RP-SMA) counterpart of 132289 — same PCB footprint, reversed
mating-pin gender, mechanically incompatible with generic commercial SMA antennas/cables, which
satisfies §15.203's "unique coupling" provision. Updated in `avionics/kicad/Emma.kicad_sch`,
`avionics/kicad/Emma.kicad_pcb`, `avionics/kicad/Emma.md`,
`gcs/malcolm/hardware/docs/malcolm_wiring.md`, and
`gcs/malcolm/hardware/docs/malcolm_antenna_spec.md`. See TODO.md §0.1 — remaining step is the
physical board re-spin/fabrication run to populate 132289RP in place of 132289; the design-level
fix is complete.

**Used in:** `gcs/malcolm/hardware/docs/malcolm_antenna_spec.md`,
`avionics/firmware/dts/cape-b/k3-am6254-pocketbeagle2-serenity-cape-b2.dts`,
`README.md`, `TODO.md`, `AGENTS.md`, `docs/AVIONICS_PB2_REDESIGN.md`

---

### REF-FCC-004: 47 CFR Part 95 Subpart C — Radio Control Radio Service (RCRS) — Evaluated and Rejected for Emma's 49 MHz Link

| Field | Value |
|---|---|
| **Issuing authority** | FCC |
| **Official URL** | <https://www.ecfr.gov/current/title-47/chapter-I/subchapter-D/part-95/subpart-C> |
| **Status** | **Not used in design.** Researched 2026-06-20 as a candidate replacement band/service for Emma's 49 MHz link (to recover the power/range budget §15.235 does not permit — see REF-FCC-003 and TODO.md §0.1) and rejected. Retained here per the Standards Vetting Policy so the rejection is auditable and is not re-investigated from scratch in a future session. |

**Regulatory provisions reviewed:**

| Provision | Description | Citation |
|---|---|---|
| 72 MHz channel plan | 50 channels, 72.01–72.99 MHz, 20 kHz spacing; **usable only to control and operate model aircraft** | §95.763(b) |
| 75 MHz channel plan | 30 channels, 75.41–75.99 MHz, 20 kHz spacing; **usable only to control and operate model surface craft** | §95.763(c) |
| 26–28 MHz channel plan | 6 channels, 26.995–27.255 MHz | §95.763(a) |
| Frequency tolerance | ±20 ppm at 72/75 MHz; ±50 ppm (or ±100 ppm under the ≤2.5 W on/off-only exception) at 26–28 MHz | §95.765 |
| Transmitter power | Mean output power ≤ 0.75 W on 72/75 MHz | §95.767 |
| Permissible use | RCRS transmitters may be used **only for one-way communications** (telecommand, and on 26–28 MHz only, narrow on/off-indicator telemetry); **"No person shall use a RCRS transmitter to transmit data"** | §95.731 |
| Equipment certification | No certification exception exists for 72/75 MHz transmitters (the §95.735 non-certified-transmitter exception applies only to the 26–28 MHz band) | §95.735 |
| Licensing | Operated without an individual license ("licensed by rule"), but the equipment itself requires Part 95-specific FCC certification, separate from the Part 15 §2.803/§15.19 process REF-FCC-003 already requires for Emma | §95.305 |

**Findings — why RCRS does not apply to Emma:**

1. **No 78 MHz allocation exists.** §95.763 defines only the 26–28 MHz, 72 MHz, and 75 MHz channel plans; there is no 78 MHz RCRS band in 47 CFR Part 95 at any subpart.
2. **Aircraft/surface split forecloses 75 MHz.** Serenity is an aircraft. §95.763(c) restricts 75 MHz channels to model *surface* craft by rule; only the 72 MHz band (§95.763(b)) is available to an aircraft under RCRS.
3. **§95.731 is disqualifying regardless of band or power.** Emma's payload is bidirectional
    AX.25 KISS-framed packet data (signed/authenticated messages, telemetry, command — required
    by the Zero Trust policy, REF-NIST-001 §2.1) — squarely "data" under §95.731's prohibition.
    RCRS permits only one-way telecommand/indicator-telemetry traffic; it cannot legally carry
    this link's actual payload even though §95.767's 0.75 W power ceiling is ≈42 dB higher than
    the ≈30 µW EIRP REF-FCC-003 permits under §15.235.
4. **No certification or licensing simplification.** Moving to 72 MHz would still require a from-scratch Part 95 equipment certification (no §95.735 exception above 26–28 MHz); it does not reduce the certification burden already carried under Part 15.

**Conclusion:** RCRS is incompatible with this link's function (bidirectional signed data), not just its frequency, and is **not adopted**. See TODO.md §0.1 for the disposition of the underlying range/power-budget problem.

**Used in:** `TODO.md` §0.1

---

## Part III — NIST Security Standards

### REF-NIST-001: NIST SP 800-207 — Zero Trust Architecture

| Field | Value |
|---|---|
| **Issuing authority** | National Institute of Standards and Technology (NIST), U.S. Dept. of Commerce |
| **Edition** | Final (August 2020) |
| **Official URL** | <https://csrc.nist.gov/publications/detail/sp/800-207/final> |
| **Direct PDF** | <https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf> |

**Sections applied in this project:**

| Section | Title | Application |
|---|---|---|
| §2.1 | Zero Trust Basics | Every network resource must authenticate/authorize each connection; no implicit trust granted by network location |
| §2.2 | Zero Trust Network Architecture | Principle basis for digitally signing every message, internal and external |
| §3.3 | Device Agent/Gateway-Based Deployment | TPM 2.0 attestation per node (SLB9670) as the device agent |
| §4 (entire) | Deployment Scenarios | Applied to the 8-node cooperative architecture with per-node key storage |

**Applied to:** Every message (internal CAN FD/RS-485/1553/Ethernet and external SiK/LoRa/WiFi/49 MHz)
carries a TPM-bound SHA-256 HMAC; TPM 2.0 (SLB9670) on all 8 nodes provides boot measurement
and key storage.

**Used in:** `AGENTS.md`, `README.md`, `docs/AVIONICS_PB2_REDESIGN.md`, `TODO.md`,
`airframe/openscad/fuselage/bow_sensor_pod.scad`

---

### REF-NIST-002: NIST SP 800-82 Rev 3 — Guide to Operational Technology (OT) Security

| Field | Value |
|---|---|
| **Issuing authority** | NIST |
| **Edition** | Revision 3 (September 2023) |
| **Official URL** | <https://csrc.nist.gov/publications/detail/sp/800-82/3/final> |
| **Direct PDF** | <https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-82r3.pdf> |

**Note:** Revision 3 retitled the document from "Industrial Control Systems (ICS) Security"
to "Operational Technology (OT) Security."

**Sections applied in this project:**

| Section | Title | Application |
|---|---|---|
| §5.3 | Network Architecture for OT Systems | Basis for galvanic isolation on all bus transceivers; network segmentation between RF and wired buses |
| §5.4 | Network Segmentation and Defense in Depth | Multiple independent bus types (CAN FD, 1553, RS-485, Ethernet) as defense-in-depth |
| §5.5 | Remote Access | Hardened external comms links; no unauthenticated remote access |
| §6.2.5 | Electromagnetic Interference | Basis for EMI hardening design objective (500 W/m² RF environment) |

**Applied to:** 5 kV galvanic isolation on all inter-node buses; Faraday enclosure for Kaylee PDB;
PACE redundancy design; hostile RF environment design objective.

**Used in:** `AGENTS.md`, `README.md`, `docs/AVIONICS_PB2_REDESIGN.md`

---

### REF-NIST-003: NIST SP 800-160 Vol 1 Rev 1 — Engineering Trustworthy Secure Systems

| Field | Value |
|---|---|
| **Issuing authority** | NIST |
| **Edition** | Volume 1 Revision 1 (November 2022) |
| **Official URL** | <https://csrc.nist.gov/publications/detail/sp/800-160/vol-1-rev-1/final> |
| **Direct PDF** | <https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-160v1r1.pdf> |

**Sections applied in this project:**

| Section | Title | Application |
|---|---|---|
| Chapter 3 | Systems Security Engineering Framework | Security-by-design applied throughout PCB layout, firmware architecture, and bus protocol selection |
| §3.3 | Stakeholder Needs and Requirements | Security requirements derived from mission profile (§ Mission profile items 1–3: rogue command detection, unsafe node detection, failover) |
| Appendix C | System Lifecycle Processes | Security considerations applied at every design phase |

**Used in:** `AGENTS.md`

---

### REF-NIST-004: NIST SP 800-92 — Guide to Computer Security Log Management

| Field | Value |
|---|---|
| **Issuing authority** | NIST |
| **Edition** | Final (September 2006); Revision 1 in draft as of 2024 |
| **Official URL** | <https://csrc.nist.gov/publications/detail/sp/800-92/final> |

**Note:** NIST SP 800-92 Rev 1 (draft) will supersede this document upon final publication.
Verify section references against the final revision when it is published.

**Sections applied in this project:**

| Section | Title | Application |
|---|---|---|
| §4.4.2 | Protecting Log Data | Recommends measures preventing unauthorized modification, deletion, or access to logs; the ATF16V8BQL CPLD hardware write-block on each Zoë node implements this principle at the hardware layer |
| §4.1 | Log Generation | Every sensor reading, message, and camera frame logged to hardware-enforced non-executable microSD |

**Applied to:** ATF16V8BQL CPLD hardware write-block (SET at power-on, CLEAR only on hard power
cycle); hardware-enforced append-only non-executable log microSD on every Zoë node.

**Used in:** `README.md` (replaces incorrect NIST SP 800-72 citation — see "Removed Citations"),
`TODO.md`, `docs/AVIONICS_PB2_REDESIGN.md`

---

## Part IV — Defense Standards

### REF-MIL-001: MIL-STD-1553B — Aircraft Internal Time Division Command/Response Multiplex Data Bus

| Field | Value |
|---|---|
| **Issuing authority** | U.S. Department of Defense (DoD) |
| **Edition** | MIL-STD-1553B with Notice 2 (30 September 1996); original date 21 September 1978 |
| **Official access** | DLA ASSIST QuickSearch: <https://assist.dla.mil/> (search "MIL-STD-1553") |
| **Note** | Public domain per 10 U.S.C. §4252; no purchase required |

**Sections applied in this project:**

| Section/Table | Title | Application |
|---|---|---|
| §3.1 | Definitions | Bus Controller (BC), Remote Terminal (RT), Bus Monitor (BM) — FC1 is primary BC, FC2 is standby BC, all others are RT |
| §4.1 | Bus Characteristics | 78 Ω characteristic impedance; shielded twisted pair (MIL-C-17/131 or equivalent); Manchester II biphase-level encoding |
| §4.2 | Terminal Types | One BC per bus at any given time; up to 31 RT addresses |
| §4.3 | Word Formats | 20-bit Manchester II word: 3-bit sync + 16-bit data + 1-bit parity; 1.0 Mbps ± 1% |
| §4.4 | Message Formats | BC-to-RT, RT-to-BC, and RT-to-RT transfer formats |
| §4.6 | Coupling Methods | Transformer coupling required for stub length > 0.9 m (0.03 ft) from the bus; PE-68515 or equivalent 1:1.41 transformer |
| Table IV | Response Time | RT must begin Status Word response between 4 µs and 12 µs after last bit of last valid Command Word |

**Applied to:** 8-node linear bus (CN1–FC1–CN2–FC2–CN3–FC3–CN4–FC4); PRU-ICSS Manchester II
encoder/decoder at 250 MHz (250 cycles per 1 µs bit cell); DS26LV31 driver / DS26LV32 receiver;
PE-68515 coupling transformer (1:1.41, 78 Ω); 78 Ω termination at CN1 (Bay A) and FC4 (Bay E).

**Used in:** `docs/AVIONICS_PB2_REDESIGN.md`,
`avionics/firmware/dts/cape-a/k3-am6254-pocketbeagle2-serenity-cape-a2.dts`,
`avionics/firmware/dts/cape-b/k3-am6254-pocketbeagle2-serenity-cape-b2.dts`

---

### REF-MIL-002: MIL-STD-461G — Requirements for the Control of Electromagnetic Interference Characteristics of Subsystems and Equipment

| Field | Value |
|---|---|
| **Issuing authority** | U.S. Department of Defense (DoD), Assistant Secretary of Defense for Acquisition |
| **Edition** | Revision G (11 August 2015); Change Notice 1 (CN1) issued 9 December 2019 |
| **Official access** | DLA ASSIST QuickSearch: <https://assist.dla.mil/> (search "MIL-STD-461") |
| **Note** | Public domain per 10 U.S.C. §4252; no purchase required. Revision G supersedes MIL-STD-461F (2007). The CN1 addendum corrects test procedures; G+CN1 is the current applicable revision. |

**Requirements applied in this project:**

| Requirement | Title | Application |
|---|---|---|
| RE102 | Radiated Emissions, Electric Field | Limit C applies to all avionics subsystems; 100BASE-TX EMI suppressed via HX1188NL magnetics, CMCs, and TVS arrays on Wash and Zoë |
| RS103 | Radiated Susceptibility, Electric Field | 200 V/m, 10 kHz–18 GHz; isolated buses + chassis-grounded Kaylee enclosure provide margin |
| CS101 | Conducted Susceptibility, Power Leads | 50 V, 30 Hz – 150 kHz; π-filter bulk caps on Kaylee BECs |
| CS114 | Conducted Susceptibility, Bulk Cable Injection | Curve 05; two-stage CM filter (CM1+CM2, > 80 dB at 10 MHz) + Y-caps to chassis |
| CE102 | Conducted Emissions, Power Leads | Limit B; CM1+CM2 input chokes + π-filter on each BEC |

**Applied to:** Wash (Cape-A-2), Zoë (Cape-B-2), and Kaylee EMC compliance targets.  The
design environment (500 W/m², E ≈ 434 V/m) [REF-NIST-002 §6.2.5] exceeds all MIL-STD-461G
RS103 limits; compliance with 200 V/m RS103 is a design floor, not the design ceiling.  Full
MIL-STD-461G qualification testing is deferred pending airframe integration.

**Used in:** `avionics/kicad/Wash.md`, `avionics/kicad/Zoë.md`, `avionics/kicad/Kaylee.md`,
`docs/AVIONICS_PB2_REDESIGN.md`

---

## Part V — International Standards (ISO, IEC)

### REF-ISO-001: ISO 11898-1:2015 — Road Vehicles — Controller Area Network (CAN) — Part 1: Data Link Layer and Physical Signalling

| Field | Value |
|---|---|
| **Issuing authority** | International Organization for Standardization (ISO) |
| **Edition** | 2015, with Amendment 1:2020 (CAN FD) |
| **Catalog URL** | <https://www.iso.org/standard/63648.html> |
| **Note** | ISO 11898-1:2024 is the latest edition; verify clause numbering against current edition. Amendment 1:2020 added CAN FD to the 2015 base document. |

**Clauses applied in this project:**

| Clause | Title | Application |
|---|---|---|
| Clause 8 | CAN Data Frame | Base frame and extended frame format for standard CAN messages |
| Clause 10 (Amd.1) | CAN FD Frame | FDF, BRS, ESI bits; data phase up to 8 Mbps; separate arbitration and data phase bit rates |
| Clause 12 (Amd.1) | Bit Timing | CAN FD two-phase bit timing (arbitration at 1 Mbps, data at 5 Mbps per design) |

**Applied to:** AM6254 native MCAN controllers operating at 1 Mbps arbitration / 5 Mbps data;
ATA6561 CAN FD transceivers; 120 Ω bus termination at CN1 (Bay A) and FC4 (Bay E).

**Used in:** `docs/AVIONICS_PB2_REDESIGN.md`,
`avionics/firmware/dts/cape-a/k3-am6254-pocketbeagle2-serenity-cape-a2.dts`, `AGENTS.md`

---

### REF-IEC-001: IEC 62368-1 Ed. 3.0 — Audio/Video, Information and Communication Technology Equipment — Part 1: Safety Requirements

| Field | Value |
|---|---|
| **Issuing authority** | International Electrotechnical Commission (IEC) |
| **Edition** | Third edition (2018-12) |
| **Official URL (purchase)** | <https://webstore.iec.ch/en/publication/25285> |
| **US equivalent** | UL 62368-1 (Underwriters Laboratories adoption) |
| **Note** | Supersedes IEC 60950-1 (information technology equipment) and IEC 60065 (audio/video equipment). Component compliance verified per individual datasheet certifications. |

**Clauses applied in this project:**

| Clause | Title | Application |
|---|---|---|
| Clause 5.5 | Insulation | General insulation requirements |
| Clause 5.5.2 | Clearance and creepage distances | Creepage/clearance for reinforced insulation class at rated working voltage |
| Clause 6.4 | Energy source hazard mitigations | Isolation barrier mitigating hazardous voltage on signal interfaces |

**Applied to:** 5 kV reinforced insulation barriers on all inter-node signal buses.  Compliance
verified per component datasheet certifications:

- CAN FD: ISOW1044BDFMR (TI) — certified IEC 62368-1 reinforced insulation at 5000 Vrms
- RS-485: ADM2795EBRWZ (Analog Devices) — certified IEC 62368-1 reinforced insulation at 5000 Vrms
- Ethernet: ADIN1300BCPZ PHY + ISO7642FDWRR (TI) isolator + Würth 749010012A transformer

**Note:** Component-level IEC 62368-1 certification does not automatically confer system-level
compliance.  The PCB layout must maintain the component-rated creepage and clearance distances
between primary and secondary sides of each isolation barrier.  PCB layout verification is
required before fabrication (see TODO.md §1.4 PCB DRC and isolation verification).

**Used in:** `README.md`, `docs/AVIONICS_PB2_REDESIGN.md`,
`avionics/firmware/dts/cape-a/k3-am6254-pocketbeagle2-serenity-cape-a2.dts`,
`avionics/firmware/dts/cape-b/k3-am6254-pocketbeagle2-serenity-cape-b2.dts`,
`TODO.md`, `AGENTS.md`, `airframe/openscad/fuselage/bow_sensor_pod.scad`

---

### REF-IEC-002: IEC 60825-1:2014+AMD1:2021 — Safety of Laser Products — Part 1: Equipment Classification and Requirements

| Field | Value |
|---|---|
| **Issuing authority** | International Electrotechnical Commission (IEC) |
| **Edition** | Second edition 2014-05, consolidated with Amendment 1 (2021-11) |
| **Official URL (purchase)** | <https://webstore.iec.ch/en/publication/5587> |
| **US equivalent** | ANSI Z136.1-2022 (American National Standard for Safe Use of Lasers) |
| **FDA harmonization** | IEC 60825-1 is harmonized with FDA 21 CFR Part 1040 [REF-FDA-001]; devices meeting IEC 60825-1 classification satisfy FDA emission limits for the corresponding laser class |

**Clauses applied in this project:**

| Clause | Title | Application |
|---|---|---|
| §3.60 | Accessible emission limit (AEL) | AEL for Class 3R at 630–680 nm: ≤ 5 mW CW (≤ 1 mW × MPE ratio) |
| §4.3.3 | Class 3R definition | Class 3R: low-risk lasers where direct beam viewing is hazardous; beam from diffuse reflection generally safe |
| Table 3 | AEL values for continuous-wave lasers | 650 nm, Class 3R: AEL = 5 mW; confirms ≤ 5 mW crosshair laser is within Class 3R boundary |
| §5.1 | Classification requirements | Manufacturer must classify laser product and provide required labels |
| §5.4 | Engineering controls for Class 3R | Class 3R devices require interlocked protective housing; this design implements GPIO-controlled enable with pull-down default-off |

**Applied to (Class 3R, cargo bay only — 2026-07-03 update):** 12 mm OD crosshair-pattern
laser module (5 mW, 650 nm) installed in the cargo bay nadir FPV mount (`cargo_fpv_bezel`,
Jayne board); required fan angle for a 3"×3" (76×76 mm) crosshair at 5 ft (1.5 m) is only
≈2.86°, well within reach of an off-the-shelf 5 mW Class 3R module — no change from the
original bow pod laser spec, just relocated. This module is **no longer installed in the bow
sensor pod** — see the Class 3B entry below for the nose laser, which has a materially
different optical throw requirement.

**Class 3B application — nose laser (added 2026-07-03):**

| Clause | Title | Application |
|---|---|---|
| §4.3.4 | Class 3B definition | Class 3B: direct intrabeam viewing is always hazardous; diffuse reflection viewing is normally still safe. Applies to CW visible lasers with accessible emission >5 mW up to 500 mW. |
| Table 3 | AEL values for continuous-wave lasers | 520 nm falls in the visible band; Class 3B upper bound 500 mW CW |
| §5.4 | Engineering controls for Class 3B | Requires: key-controlled interlock, emission indicator (visible when armed), a beam-stop or shutter, and protective housing — beyond the GPIO-default-off pull-down alone used for the Class 3R module |
| §7 | Labeling | Class 3B warning label and aperture label required on the module housing |

**Applied to:** bow sensor pod (nose, Jayne board) crosshair laser. A 2"×2" (51×51 mm) crosshair
at 50 ft (15.2 m) requires ≈0.19° fan angle — no catalog 520 nm crosshair module publishes
this tight a divergence, so a custom-collimated module is required, and the optical power
needed for daylight camera visibility at that divergence places it in Class 3B rather than
Class 3R. **Open item — do not fabricate:** the specific part number, verified mW rating, and
manufacturer-stated (or independently computed) IEC 60825-1 class are not yet established;
this design step is not complete until a real datasheet is cited here in place of this
placeholder text. Tracked in TODO.md §1.2c.

**Used in:** `airframe/openscad/fuselage/bow_sensor_pod.scad`,
`airframe/openscad/fuselage/bow_sensor_faceplate.scad`,
`airframe/openscad/fuselage/head_shell24.scad`

---

### REF-VDE-001: VDE V 0884-11:2017-01 — Optocouplers for Use in Electrical Equipment — Test and Measurement Methods

| Field | Value |
|---|---|
| **Issuing authority** | Verband der Elektrotechnik Elektronik Informationstechnik e.V. (VDE), Germany |
| **Edition** | 2017-01 |
| **Official URL (search)** | <https://www.vde-verlag.de/> (search "VDE V 0884-11") |
| **Alternative catalog** | <https://www.beuth.de/> (DIN/VDE standards via Beuth Verlag) |
| **Note** | VDE V 0884-11 specifies test methodology for galvanic isolators (digital isolators, optocouplers). This standard defines the certification framework under which ISOW1044BDFMR and ADM2795EBRWZ are certified. |

**Clauses applied in this project:**

| Clause | Title | Application |
|---|---|---|
| Clause 4.3 | Reinforced Insulation (RI) | The insulation class applied on all inter-node transceivers in this design |
| Clause 5.2 | Partial discharge test (Vpd) | Confirms no partial discharge at rated working voltage |
| Clause 5.3 | Dielectric withstand test (Viso) | 5000 Vrms (7071 Vpk) hipot test for RI class — basis for the "5 kV" rating |

**Applied to:** Same isolation devices as REF-IEC-001.  VDE V 0884-11 compliance is verified
per individual component certifications in the ISOW1044BDFMR and ADM2795EBRWZ datasheets.

**Used in:** `README.md`, `docs/AVIONICS_PB2_REDESIGN.md`, `AGENTS.md`,
`avionics/firmware/dts/cape-a/k3-am6254-pocketbeagle2-serenity-cape-a2.dts`,
`avionics/firmware/dts/cape-b/k3-am6254-pocketbeagle2-serenity-cape-b2.dts`

---

### REF-IEC-003: IEC 61000-4-2:2008 — Electromagnetic Compatibility (EMC) — Testing and Measurement Techniques — Electrostatic Discharge (ESD) Immunity Test

| Field | Value |
|---|---|
| **Issuing authority** | International Electrotechnical Commission (IEC) |
| **Edition** | Second edition (2008-12) |
| **Official URL (purchase)** | <https://webstore.iec.ch/> — search "IEC 61000-4-2" |
| **Note** | Supersedes IEC 61000-4-2:1995+AMD1:1998+AMD2:2000. Exact webstore product-page URL not confirmed during catalog entry (see Open Standards Verification Items). |

**Clauses applied in this project:**

| Clause | Title | Application |
|---|---|---|
| §5 | Classification of ESD generators | Contact discharge ±8 kV (Level 4), air discharge ±15 kV (Level 4) at all field connectors |
| §8 | Test levels | Level 4 is the highest defined test level; selected as design target for the 500 W/m² hostile EMI environment [REF-NIST-002 §6.2.5] |

**Applied to:** TVS arrays (PRTR5V0U2X) at all JST-GH field connectors on Wash and Zoë;
shielded Kaylee enclosure provides ESD isolation for PDB connectors.

**Used in:** `avionics/kicad/Wash.md`, `avionics/kicad/Zoë.md`, `avionics/kicad/Kaylee.md`

---

### REF-IEC-004: IEC 61000-4-4:2012 — Electromagnetic Compatibility (EMC) — Testing and Measurement Techniques — Electrical Fast Transient/Burst (EFT/Burst) Immunity Test

| Field | Value |
|---|---|
| **Issuing authority** | IEC |
| **Edition** | Third edition (2012-04) |
| **Official URL (purchase)** | <https://webstore.iec.ch/> — search "IEC 61000-4-4" |
| **Note** | Supersedes IEC 61000-4-4:2004+AMD1:2010. Exact webstore product-page URL not confirmed during catalog entry (see Open Standards Verification Items). |

**Clauses applied in this project:**

| Clause | Title | Application |
|---|---|---|
| §5.2 | Test levels | Level 4 (4 kV peak, 5/50 ns) on all signal lines |

**Applied to:** Common-mode chokes (CM2: Bourns SRF2012-100Y) and isolated transceivers
(ISOW1044BDFMR, ADM2795EBRWZ) on Wash and Zoë signal buses.

**Used in:** `avionics/kicad/Wash.md`, `avionics/kicad/Zoë.md`

---

### REF-IEC-005: IEC 61000-4-5:2014+AMD1:2017 — Electromagnetic Compatibility (EMC) — Testing and Measurement Techniques — Surge Immunity Test

| Field | Value |
|---|---|
| **Issuing authority** | IEC |
| **Edition** | Third edition 2014-05, consolidated with Amendment 1 (2017-03) |
| **Official URL (purchase)** | <https://webstore.iec.ch/> — search "IEC 61000-4-5" |
| **Note** | Supersedes IEC 61000-4-5:2005. The 2017 Amendment 1 introduced clarifications to coupling/decoupling network parameters. Exact webstore product-page URL not confirmed during catalog entry (see Open Standards Verification Items). |

**Clauses applied in this project:**

| Clause | Title | Application |
|---|---|---|
| §5.2 | Test levels | Level 3 (2 kV CM, 1 kV DM) on CAN FD and RS-485 bus lines; Level 3 (±2 kV CM, ±1 kV DM) on VBAT |
| Annex A | Combination wave generator | Defines the 1.2/50 µs (voltage) / 8/20 µs (current) surge waveform |

**Applied to:** ADM2795EBRWZ RS-485 transceiver (rated ±42 V bus fault — exceeds IEC 61000-4-5
Level 3 ±2 kV CM surge on bus); SMBJ33CA TVS (D1) on Kaylee VBAT line; PRTR5V0U2X TVS
arrays at field connectors on Wash and Zoë.

**Used in:** `avionics/kicad/Wash.md`, `avionics/kicad/Zoë.md`, `avionics/kicad/Kaylee.md`

---

## Part V-A — IPC PCB Design Standards

### REF-IPC-001: IPC-2221 — Design Guidelines for Printed Board Layout (PCB Design Fundamentals)

| Field | Value |
|---|---|
| **Issuing authority** | IPC (Association Connecting Electronics Industries) |
| **Edition** | IPC-2221B (current; earlier editions 2221, 2221A also valid) |
| **Official URL** | <https://www.ipc.org/> (catalog: search "IPC-2221") |
| **Current status** | Active standard; reaffirmed by IPC in 2020 |

**Clauses applied in this project:**

| Section | Title | Application |
|---|---|---|
| Section 3 | Trace Routing and Spacing | Minimum trace width, trace-to-trace clearance, and trace-to-edge clearance for signal integrity and manufacturability |
| Section 4 | Design Rules for EMI/RFI Control | PCB layer stackup, ground plane integrity, and edge clearance rules for high-frequency and hostile RF environments |
| Section 4.2 | Copper-to-Edge Clearance (Creepage) | Minimum copper-to-board-edge distance to prevent arcing, field coupling, and manufacturing defects |
| Section 6 | Design for Assembly and Manufacturing | Keepout zones, via placement, pad sizing for component footprints |

**Harsh EMI Environment Guidance — Critical Finding:**

The 500 W/m² RF field design objective [REF-NIST-002 §6.2.5] places this project in a **high-stress electromagnetic environment**. IPC-2221B §4.2 and complementary guidance in IPC-A-600 (REF-IPC-002) specify that:

1. **Standard environments** (office/lab, < 10 V/m RF): copper-to-edge clearance ≥ 0.10–0.15 mm
2. **Harsh RF environments** (industrial RF, > 100 V/m; calculated ≈434 V/m for this project): copper-to-edge clearance ≥ 0.20–0.30 mm

The design environment of 500 W/m² (≈434 V/m, equivalent to RF proximity near a strong broadcast or cellular link) **exceeds even MIL-STD-461G RS103 susceptibility limits** (200 V/m). **Consequently, a minimum 0.20 mm copper-to-edge clearance is the design floor for this project, not a design maximum.** Reducing to 0.15 mm would increase risk of field coupling, arcing, and PCB manufacturing defects in the harsh RF environment.

**Applied to:** All PCB designs (Wash, Zoë, Kaylee, Emma, Jayne, CAN-PERIPH-GW-1, ENC-NACELLE-1).

**Design Decision (2026-07-27):** Copper-to-edge clearance (min_copper_edge_clearance in KiCad) is established at **0.20 mm minimum** per IPC-2221B §4.2 for harsh RF environments. This clearance must not be reduced below 0.20 mm without explicit re-evaluation against the 500 W/m² field-strength requirement and validation that manufacturing yield remains acceptable.

**Used in:** `avionics/kicad/*/kicads/*.kicad_pro` (all board project files), EMI hardening documentation

---

### REF-IPC-002: IPC-A-600 — Acceptability of Printed Boards

| Field | Value |
|---|---|
| **Issuing authority** | IPC (Association Connecting Electronics Industries) |
| **Edition** | IPC-A-600K (current; earlier editions J, H, G also valid) |
| **Official URL** | <https://www.ipc.org/> (catalog: search "IPC-A-600") |
| **Current status** | Active standard; latest edition K released 2020 |

**Clauses applied in this project:**

| Clause | Title | Application |
|---|---|---|
| Section 3 | Acceptability Criteria — Layers and Substrates | PCB material acceptance, layer thickness, copper thickness tolerance |
| Section 4 | Acceptability Criteria — Imaging and Plating | Trace definition, plating thickness, surface finish specification (ENIG, HASL, OSP) |
| Section 5 | Acceptability Criteria — Etching and Drilling | Hole size tolerance, plating coverage, clearance around drilled holes |
| Section 8 | Workmanship Standards — Copper Traces and Pads | Conductor spacing, edge clearance acceptance, solder mask coverage verification |

**Applied to:** PCB manufacturing accept/reject criteria during fabrication quality verification. All boards (Wash, Zoë, Kaylee, Emma, Jayne, CAN-PERIPH-GW-1, ENC-NACELLE-1) are fabricated by JLCPCB and inspected against IPC-A-600 standards prior to assembly.

**Used in:** Board-specific design markdown files, incoming inspection checklists, Gerber generation workflows

---

## Part VI — IEEE Standards

### REF-IEEE-001: IEEE 802.3-2022 — Ethernet (CSMA/CD Access Method and Physical Layer Specifications)

| Field | Value |
|---|---|
| **Issuing authority** | Institute of Electrical and Electronics Engineers (IEEE) |
| **Edition** | 2022 |
| **Official URL (purchase)** | <https://ieeexplore.ieee.org/document/9844436> |

**Clauses applied in this project:**

| Clause | Title | Application |
|---|---|---|
| Clause 22 | Media Independent Interface (MII/RMII) | RMII interface between AM6254 CPSW3G and ADIN1300BCPZ / DP83825I PHYs |
| Clause 24 | 100BASE-TX PHY | 100 Mbps operation on all ring links |
| Clause 38 | Isolation transformer requirements | 1500 Vrms isolation per Ethernet port (Würth 749010012A meets this requirement) |

**Applied to:** Ethernet RSTP ring connecting all 8 nodes; CPSW3G hardware switch mode in AM6254.

**Used in:** `docs/AVIONICS_PB2_REDESIGN.md`, `AGENTS.md`,
`avionics/firmware/dts/cape-a/k3-am6254-pocketbeagle2-serenity-cape-a2.dts`,
`avionics/firmware/dts/cape-b/k3-am6254-pocketbeagle2-serenity-cape-b2.dts`

---

### REF-IEEE-002: IEEE 802.11-2020 — Wireless LAN Medium Access Control (MAC) and Physical Layer (PHY) Specifications

| Field | Value |
|---|---|
| **Issuing authority** | IEEE |
| **Edition** | 2020 |
| **Official URL (purchase)** | <https://ieeexplore.ieee.org/document/9363693> |

**Clauses applied in this project:**

| Clause | Title | Application |
|---|---|---|
| Clause 17 | OFDM PHY (802.11a/n/ac) | 5 GHz UNII-3 band operation for WL1837MOD |
| Clause 19 | 802.11n High Throughput PHY | 2.4 GHz and 5 GHz dual-band capability |

**Applied to:** TI WL1837MOD 802.11 a/b/g/n via SDIO interface; 5 GHz primary, 2.4 GHz fallback.

**Used in:** `docs/AVIONICS_PB2_REDESIGN.md`, `AGENTS.md`

---

### REF-IEEE-003: IEEE 802.15.4-2020 — Low-Rate Wireless Networks

| Field | Value |
|---|---|
| **Issuing authority** | IEEE |
| **Edition** | 2020 |
| **Official URL (purchase)** | <https://ieeexplore.ieee.org/document/9144691> |

**Clauses applied in this project:**

| Clause | Title | Application |
|---|---|---|
| Clause 10 | 2.4 GHz O-QPSK PHY | Zigbee radio layer (CC2652R7 optional backup mesh) |

**Used in:** `docs/AVIONICS_PB2_REDESIGN.md`, `README.md`, `AGENTS.md`

---

## Part VII — ISA/IEC Industrial Cybersecurity Standards

### REF-ISA-001: ISA/IEC 62443-3-3:2013 — Industrial Automation and Control Systems Security — System Security Requirements and Security Levels

| Field | Value |
|---|---|
| **Issuing authority** | International Society of Automation (ISA) / International Electrotechnical Commission (IEC) |
| **Edition** | 2013 |
| **Official URL (ISA)** | <https://www.isa.org/products/isa-iec-62443-3-3-2013-industrial-automation-and-c> |
| **Official URL (IEC)** | <https://webstore.iec.ch/en/publication/7032> |

**Security Requirements (SR) applied in this project:**

| SR | Title | Application |
|---|---|---|
| SR 3.1 | Communications Integrity | All messages (internal + external) carry TPM-bound HMAC; basis for authentication requirement |
| SR 3.2 | Malicious Code Protection | Firmware in eMMC; hardware write-blocked logs; TPM-measured boot |
| SR 4.2 | Use of Cryptography | TPM 2.0 (SLB9670) per node for key storage, attestation, and HMAC computation |
| SR 7.6 | Network and Security Configuration Settings | 5 kV galvanic isolation as physical network security hardening against EMI/RF injection |

**Used in:** `AGENTS.md`, `docs/AVIONICS_PB2_REDESIGN.md`

---

## Part VIII — ICAO Standards

### REF-ICAO-001: ICAO Annex 2 — Rules of the Air

| Field | Value |
|---|---|
| **Issuing authority** | International Civil Aviation Organization (ICAO) |
| **Edition** | 10th edition (July 2005) with amendments |
| **Official URL (purchase)** | <https://store.icao.int/en/annex-2-rules-of-the-air> |
| **ICAO main site** | <https://www.icao.int/> |
| **Note** | For US domestic operations, **14 CFR §91.209 (REF-FAA-003) is the directly enforceable regulation.** ICAO Annex 2 is cited for international context only and as the basis from which §91.209 derives. |

**Sections applied in this project:**

| Section | Title | Application |
|---|---|---|
| Chapter 3, §3.1.9 | Lights to be displayed by unmanned aircraft | Port red, starboard green, aft white position lights |

**Used in:** `graphical-build-guide/build_guide_13_nav_lights.svg`,
`graphical-build-guide/decal_sheet.svg`, `AGENTS.md`, `docs/REVN_BUILD_GUIDE_24IN.md`

---

## Part IX — Protocol References

### REF-PROTO-001: AX.25 Link Access Protocol for Amateur Packet Radio

| Field | Value |
|---|---|
| **Authority** | Tucson Amateur Packet Radio (TAPR) / American Radio Relay League (ARRL) |
| **Edition** | Version 2.2 (July 1998) |
| **Official URL** | <https://www.ax25.net/AX25.2.2-Jul%2098-2.pdf> |
| **Note** | AX.25 is used as the frame format on the 49 MHz link. The RF portion of this link is governed by 47 CFR Part 15 §15.235 (REF-FCC-003), NOT the Amateur Radio Service and NOT Part 95 RCRS. AX.25 is a protocol choice; its use here does not require an amateur radio license because the 49.82–49.90 MHz band is a license-exempt, unlicensed Part 15 band. |

**Sections applied in this project:**

| Section | Title | Application |
|---|---|---|
| §6.2 | I Frame (Information Frame) | Data packet format for command uplink and telemetry downlink |
| §6.3 | S Frames | Flow control and error recovery on the 49 MHz link |

**Used in:** `avionics/firmware/dts/cape-b/k3-am6254-pocketbeagle2-serenity-cape-b2.dts`, `README.md`,
`docs/AVIONICS_PB2_REDESIGN.md`, `avionics/firmware/common/include/ax25_types.h`

---

### REF-PROTO-002: MAVLink v2 Protocol Specification

| Field | Value |
|---|---|
| **Authority** | ArduPilot / QGroundControl / MAVLink community (open standard) |
| **Edition** | v2.0 (current as of 2026) |
| **Official URL** | <https://mavlink.io/en/> |
| **Note** | MAVLink is the application-layer protocol carried over the SiK 915 MHz link. It is an open, packet-framed protocol with CRC-16/MCRF4XX integrity check and optional signing (MAVLink v2 message signing uses HMAC-SHA256). |

**Applied to:** SiK MAVLink telemetry link (primary ground-to-air C2 channel).

**Used in:** `docs/AVIONICS_PB2_REDESIGN.md`, `TODO.md`

---

## Part X — AUVSI, ASTM F38, and Industry Frameworks

### REF-AUVSI-001: AUVSI Trusted Operator Program (TOP) and XCELLENCE Safety Standards

| Field | Value |
|---|---|
| **Issuing authority** | Association for Unmanned Vehicle Systems International (AUVSI) |
| **Official URL** | <https://www.auvsi.org/trusted-operator-program> |
| **Note** | AUVSI does not publish numbered design standards (e.g., "AUVSI-XYZ"). References to "AUVSI standards" in `AGENTS.md`/`README.md` mean AUVSI's published safety frameworks and guidelines. For numbered airframe standards, see the verified ASTM F38 Committee entries below. |

**Used in:** `AGENTS.md`, `README.md`

---

### REF-ASTM-001: ASTM F2910-22 — Design and Construction of a Small Unmanned Aircraft System (sUAS)

| Field | Value |
|---|---|
| **Issuing authority** | ASTM International, Committee F38 (Unmanned Aircraft Systems), Subcommittee F38.01 (Airworthiness) |
| **Edition** | F2910-22 |
| **Official URL** | <https://store.astm.org/f2910-22.html> |
| **Scope** | Design, construction, and test requirements for a small unmanned aircraft system (sUAS), max takeoff gross weight ≤ 55 lbm (25 kg) — covers general requirements, structure, propulsion, propellers, fuel/oil systems (not applicable, all-electric), cooling, and documentation. |

**Applied to:** Serenity airframe structural design (skin hollowing, mating-surface annulus/shoulder
requirements, fastener/wall sizing per AGENTS.md Engineering Requirements) and EDF propulsion
system design (printed EDF housings as structural components).  AUW well under the 55 lbm
(25 kg) sUAS weight class (current estimate ≈ 8 lbm / 3.6 kg, see `docs/bom_revR.json`), so the
standard's scope applies without a GAA weight exemption.

**Used in:** `AGENTS.md`, `README.md`

---

### REF-ASTM-002: ASTM F3005-22 — Batteries for Use in Small Unmanned Aircraft Systems (sUAS)

| Field | Value |
|---|---|
| **Issuing authority** | ASTM International, Committee F38, Subcommittee F38.01 |
| **Edition** | F3005-22 |
| **Official URL** | <https://store.astm.org/f3005-22.html> |
| **Scope** | Requirements for sUAS batteries — terminology, cell specification, mechanical and electrical design, and pack maintenance/documentation. Subordinate to REF-ASTM-001 (F2910). Does not address the systems utilizing the battery or use-phase safety (lithium-chemistry packs cannot be exempted from this standard). |
| **Correction note (2026-06-22)** | TODO.md §0.4 originally listed "ASTM F3322" as the candidate battery-safety standard. **F3322 is incorrect** — it is the *Standard Specification for Small Unmanned Aircraft System (sUAS) Parachutes*, unrelated to batteries and not applicable to Serenity (no deployable recovery parachute in the design). The correct battery standard is F3005. See "Removed / Superseded Citations" below. |

**Applied to:** LiPo 6S 4000 mAh main battery pack (cell specification, mechanical mounting, pack
documentation).

**Used in:** `AGENTS.md`, `README.md`

---

### REF-ASTM-003: ASTM F3269-21 — Methods to Safely Bound Behavior of Aircraft Systems Containing Complex Functions Using runtime assurance

| Field | Value |
|---|---|
| **Issuing authority** | ASTM International, Committee F38, Subcommittee F38.01 |
| **Edition** | F3269-21 (supersedes F3269-17, "...Flight Behavior of Unmanned Aircraft Systems...") |
| **Official URL** | <https://store.astm.org/f3269-21.html> |
| **Scope** | Design/test practice providing a run-time-assurance (RTA) architectural framework so that flight behavior of a complex/unverifiable function is constrained to a safe envelope by an independent monitor, without requiring traditional design-time certification (e.g. DO-178C) of the complex function itself. |

**Applied to:** The PACE-prioritized failover architecture across Wash/Zoë avionics stacks
(Watchdog, Comms, Flight Control, Payload Control primary/alternate/contingency/emergency
assignments — see AGENTS.md "Avionics Workload Balancing"): each PACE tier acts as an
independent runtime monitor/take-over path bounding the behavior of the primary controller,
consistent with F3269's RTA framework.

**Used in:** `AGENTS.md`, `README.md`

---

### Evaluated and rejected — ASTM F3003 (withdrawn)

ASTM F3003-14, *Standard Specification for Quality Assurance of a Small Unmanned Aircraft
System (sUAS)*, was the third candidate originally listed in TODO.md §0.4 for "may apply to
flight testing."  **F3003 was withdrawn by ASTM in January 2023 with no replacement
standard** (confirmed via ASTM's official store listing).  It is not cited anywhere in this
project.  No other active F38 standard fills the withdrawn QA-program role as of this
verification (2026-06-22); REF-ASTM-001 (F2910) already covers design/construction/test
requirements for the airframe itself.

---

## Part XI — FDA / CDRH Laser Product Regulations

### REF-FDA-001: 21 CFR Part 1040 — Performance Standards for Light-Emitting Products

| Field | Value |
|---|---|
| **Issuing authority** | U.S. Food and Drug Administration (FDA), Center for Devices and Radiological Health (CDRH) |
| **Current edition** | As amended through 2024 |
| **Official URL** | <https://www.ecfr.gov/current/title-21/chapter-I/subchapter-J/part-1040> |
| **Parent subchapter** | 21 CFR Subchapter J — Radiological Health (<https://www.ecfr.gov/current/title-21/chapter-I/subchapter-J>) |
| **Note** | Harmonized with IEC 60825-1 [REF-IEC-002] for laser emission limits. Applies to any laser product manufactured or imported for sale in the United States. |

**Sections applied in this project:**

| Section | Title | Application |
|---|---|---|
| §1040.10(b) | Classification | Laser products must be classified into one of four classes based on accessible emission levels |
| §1040.10(d) | Performance requirements | Class 3R (21 CFR equivalent: Class IIIa): interlocks, emission indicator, beam attenuator required |
| §1040.10(f)(1) | Safety interlock | Protective housing must incorporate a safety interlock preventing access to the beam; administrative GPIO control satisfies software interlock; physical interlock required for product shipment / commercial sale |
| §1040.10(g) | Labels and warnings | Required laser radiation warning label on product housing; Class IIIa (3R) label text and symbol required |

**Applied to:** 12 mm OD crosshair-pattern laser module (≤ 5 mW, 650 nm) in bow sensor pod.
The laser module installed in this design is a commercial off-the-shelf (COTS) component;
operator is responsible for confirming the COTS module carries required FDA/CDRH certification
labels before installation.  The GPIO enable circuit (2N7002 MOSFET, default-off 10 kΩ
pull-down) satisfies the software interlock requirement.  A physical safety key switch
shall be wired in series with the enable GPIO line before this platform is operated in
an environment where persons may be present in the beam path.

**Used in:** `airframe/openscad/fuselage/bow_sensor_pod.scad`,
`airframe/openscad/fuselage/bow_sensor_faceplate.scad`,
`airframe/openscad/fuselage/head_shell24.scad`, `TODO.md`

---

## Part XII — Sensor and Component Specifications

### REF-SENSOR-001: RunCam Nano 4 — 19 mm Nano Format FPV Camera Specification (SUPERSEDED)

**Status: SUPERSEDED 2026-07-03.** Replaced by the Jayne board's TI AM62Ax digital vision SoC
(REF-SENSOR-003) at both the bow sensor pod (nose) and the cargo bay nadir FPV mount. This
entry is retained per project revision policy (components are referenced as of their last
active revision even after superseding) — do not delete.

| Field | Value |
|---|---|
| **Manufacturer** | RunCam Technology Co., Ltd. |
| **Product** | RunCam Nano 4 (or equivalent 19 mm Nano format camera) |
| **Official product page** | <https://www.runcam.com/nano4> |
| **Specification document** | RunCam Nano 4 product specification sheet (available at product page above) |
| **Note** | This REF-ID covers the 19 mm Nano camera format standard as implemented by the RunCam Nano 4. Any 19 mm Nano format camera (19×19 mm body, M7 lens thread, 12 mm clear aperture, 4× M2 mount holes on 14×14 mm pitch) may be substituted provided it meets equivalent video output and environmental specifications. |

**Specifications applied in this design:**

| Parameter | Value | Source |
|---|---|---|
| Body dimensions | 19×19×19 mm | RunCam Nano 4 data sheet |
| Lens aperture (clear) | 12 mm diameter | RunCam Nano 4 data sheet |
| Mount hole pattern | 4× M2 on 14×14 mm pitch (±7 mm from lens centre) | Industry-standard 19 mm Nano mount |
| Operating voltage | 5 V (nominal) | RunCam Nano 4 data sheet |
| Weight | 3.6 g | RunCam Nano 4 data sheet |

**Applied to:** Dome A (dorsal) bow camera socket in
`airframe/openscad/fuselage/bow_sensor_pod.scad`; socket dimensions designed for 19 mm Nano
format compatibility (Rev R1c: CAM_APER_D = 10 mm lens bore on the 40° bow flat; the
camera body pockets behind the flat and is retained by bow_sensor_faceplate.scad).

**Used in:** `airframe/openscad/fuselage/bow_sensor_pod.scad`,
`airframe/openscad/fuselage/bow_sensor_faceplate.scad`,
`airframe/openscad/fuselage/head_shell24.scad`

---

### REF-RFMOD-001: HopeRF RFM95W/96W/98W — Low Power Long Range Transceiver Module, Pin Description

| Field | Value |
|---|---|
| **Manufacturer** | Shenzhen Hope Microelectronics Co., Ltd. (HOPERF) |
| **Product** | RFM95W/96W/98W LoRa transceiver module, version 2.0 datasheet |
| **Official product page** | <https://www.hoperf.com/modules/lora/RFM95W.html> |
| **Datasheet URL** | <https://www.hoperf.com/uploads/RFM96W-V2.0_1695351477.pdf> (123 pp.) |
| **Section applied** | §1.3 Pin Diagram, §1.4 Pin Description, Table 2 (p. 10–11) |

**Pin assignment applied in this design (16-pin module, Table 2):**

| Pin | Name | Pin | Name | Pin | Name | Pin | Name |
|---|---|---|---|---|---|---|---|
| 1 | GND | 5 | NSS | 9 | ANT | 13 | 3.3V |
| 2 | MISO | 6 | RESET | 10 | GND | 14 | DIO0 |
| 3 | MOSI | 7 | DIO5 | 11 | DIO3 | 15 | DIO1 |
| 4 | SCK | 8 | GND | 12 | DIO4 | 16 | DIO2 |

**Applied to:** `avionics/kicad/Emma.kicad_pcb` footprint "LoRa" (HOPERF_RFM9XW_SMD,
RFM95W per `TODO.md` §1.2b). **Corrected 2026-06-20:** the as-placed footprint had
SPI1_MISO/MOSI/CLK/SPI1_CS_LORA wired to pads 10–13 (real pins GND/DIO3/DIO4/3.3V) and
LORA_RESETN wired to pad 2 (real pin MISO) — a wrong-pin-number error, not merely a
missing connection; left as-built, the SPI clock signal would have driven the module's
3.3V supply pin. Pads 2–6 now carry MISO/MOSI/SCK/NSS/RESET per the table above; pads
1/8/10 tied to GND. **Still open:** pad 9 (ANT) and pad 13 (3.3V) carry no net — this
module has no antenna or power connection yet — and DIO0–DIO5 (pads 7, 11, 12, 14–16)
are unassigned pending a GPIO budget decision on the P1 header. Footprint pad size
(2.95×1.27 mm per pad) is also oversized versus the module's real castellated-pad
dimensions and the footprint physically overlaps `CAPE-B IF`; both require a footprint
correction and reposition before fabrication. Tracked in `TODO.md` §1.2b.

**Used in:** `avionics/kicad/Emma.kicad_pcb`, `avionics/kicad/Emma.md`, `TODO.md`

---

### REF-SENSOR-002: Benewake TFmini-S — Long-Range Time-of-Flight Ranging Module Specification

| Field | Value |
|---|---|
| **Manufacturer** | Benewake (Beijing) Co., Ltd. |
| **Product** | TFmini-S Time-of-Flight Ranging Module |
| **Official product page** | <https://www.benewake.com/product/TFminiS.html> |
| **Technical manual** | TFmini-S Product Manual v1.0.x (available at product page above) |
| **Note** | Selected for forward-ranging at the bow because its 12 m indoor / 7 m outdoor range substantially exceeds the VL53L5CX obstacle-avoidance sensors (4 m) used elsewhere in the airframe. Compact form factor (35×18.5×21 mm) fits within the narrow bow tip cross-section. |

**Specifications applied in this design:**

| Parameter | Value | Source |
|---|---|---|
| Range (indoor) | 0.1–12 m (SNR > 3, Lambertian target reflectance ≥ 10%) | TFmini-S Product Manual |
| Range (outdoor) | 0.1–7 m (strong ambient light) | TFmini-S Product Manual |
| Field of view | 2.3° (full angle) | TFmini-S Product Manual |
| Update rate | 1–100 Hz (configurable) | TFmini-S Product Manual |
| Interface | UART 115200 baud or I2C 400 kHz (software-selectable) | TFmini-S Product Manual |
| Operating voltage | 4.5–6 V (5 V nominal) | TFmini-S Product Manual |
| Current | 140 mA average; 800 mA peak | TFmini-S Product Manual |
| Body dimensions | 35×18.5×21 mm (L × W × H) | TFmini-S Product Manual |
| Optical aperture | 8 mm diameter (single TX/RX PMMA lens) | TFmini-S Product Manual |
| Weight | 5 g | TFmini-S Product Manual |

**Applied to:** Dome B (ventral) ToF sensor socket in
`airframe/openscad/fuselage/bow_sensor_pod.scad`; pocket dimensions designed for
TFmini-S body with 0.5 mm clearance per dimension (TOF_BODY_X = 36 mm,
TOF_BODY_Y = 20 mm, TOF_BODY_D = 22 mm).  UART routed to Shepherd's room
Wash (Cape-A-2) UART2 port; I2C available as fallback per Zero Trust data-path
redundancy policy [REF-NIST-001 §2.1].

**Used in:** `airframe/openscad/fuselage/bow_sensor_pod.scad`,
`airframe/openscad/fuselage/bow_sensor_faceplate.scad`,
`airframe/openscad/fuselage/head_shell24.scad`, `TODO.md`

---

### REF-SENSOR-003: TI AM62Ax Sitara Processors — Vision SoC Datasheet

| Field | Value |
|---|---|
| **Manufacturer** | Texas Instruments |
| **Product** | AM62A3/AM62A7 Sitara Processor (AM62Ax family) |
| **Official product page** | <https://www.ti.com/product/AM62A7> |
| **Datasheet URL** | <https://www.ti.com/lit/ds/symlink/am62a7.pdf> (Rev. E) |
| **Lifecycle status** | PRODUCTION DATA (current, not NRND) |
| **Note** | Selected over TI's earlier DaVinci DM38x family (DM385/DM388, datasheet SPRS821D) because DM38x is **NRND** (Not Recommended for New Designs) per TI's own product page. AM62Ax is also selected over an OpenIPC-supported SigmaStar/GokeMicro/HiSilicon/Ingenic SoC for toolchain uniformity with the PocketBeagle 2 Industrial's TI Sitara AM6254; it runs TI's own open-source Linux BSP (V4L2/GStreamer), not OpenIPC — OpenIPC's supported-hardware list does not include any TI part. |

**Specifications applied in this design:**

| Parameter | Value | Source |
|---|---|---|
| Camera input | MIPI CSI-2 v1.3, MIPI D-PHY 1.2, 1–4 data lanes up to 1.5 Gbps/lane | AM62Ax datasheet Rev. E |
| ISP | 7th-generation VPAC (Vision Processing Accelerator) with integrated ISP | AM62Ax datasheet Rev. E |
| Video encode | H.264 Baseline/Main/High Profile up to Level 5.2; HEVC (H.265) Main Profile up to Level 5.1 High-tier; up to 4K UHD (3840×2160) | AM62Ax datasheet Rev. E |
| Package | 484-ball FCBGA/FCCSP | AM62Ax datasheet Rev. E |

**Applied to:** Jayne board vision half (nose bow sensor pod and cargo bay nadir FPV mount) —
see `avionics/AGENTS.md` "Jayne — Cargo-Handling System and Nose/Cargo-Bay Vision, ToF & Laser Board". **Open item:** the
484-ball FCBGA package is a substantial escalation in assembly difficulty versus the discrete
components elsewhere in this design; PCB fabrication/assembly house capability for this
package must be confirmed before board layout (tracked in TODO.md §1.2c).

**Used in:** `avionics/AGENTS.md`, `TODO.md`

---

### REF-SENSOR-004: TI MSPM0G3507 — Mixed-Signal MCU with CAN-FD Interface

| Field | Value |
|---|---|
| **Manufacturer** | Texas Instruments |
| **Product** | MSPM0G3507 (MSPM0G350x family) |
| **Official product page** | <https://www.ti.com/product/MSPM0G3507> |
| **Datasheet URL** | <https://www.ti.com/lit/ds/symlink/mspm0g3507.pdf> |
| **Lifecycle status** | PRODUCTION DATA |

**Specifications applied in this design:**

| Parameter | Value | Source |
|---|---|---|
| Core | Arm Cortex-M0+ @ 80 MHz | MSPM0G3507 datasheet |
| CAN interface | Native hardware MCAN peripheral (CAN-FD capable) | MSPM0G3507 datasheet title: "Mixed-Signal Microcontrollers With CAN-FD Interface" |
| Package options | 48-pin LQFP (PT), 48-pin VQFN (RGZ), 32-pin VQFN (RHB), 32-/28-pin VSSOP | MSPM0G3507 datasheet |

**Applied to:** Jayne board control half — reads Benewake TFmini-S (REF-SENSOR-002) over UART,
drives the location-specific crosshair laser GPIO, and republishes signed sensor data over
both the Ethernet ring (via REF-SENSOR-005) and the CAN-FD trunk (via REF-SENSOR-006).
Selected specifically for its native MCAN peripheral and shared TI toolchain with the
PocketBeagle 2 Industrial's AM6254 real-time domain — avoids the software-PIO CAN-FD
synthesis that a non-TI MCU (e.g. RP2350) would require.

**Used in:** `avionics/AGENTS.md`, `TODO.md`

---

### REF-SENSOR-005: Microchip KSZ9477 — Ethernet Switch with HSR/PRP Hardware Redundancy

| Field | Value |
|---|---|
| **Manufacturer** | Microchip Technology Inc. |
| **Product** | KSZ9477 7-Port Gigabit Ethernet Switch |
| **Official product page** | <https://www.microchip.com/en-us/product/ksz9477> |
| **Application note** | AN3474 — "KSZ9477 High-Availability Seamless Redundancy" |
| **Note** | Selected specifically because it is confirmed (per AN3474) to hardware-offload HSR (High-availability Seamless Redundancy) and PRP (Parallel Redundancy Protocol) per IEC 62439-3 — HSR tag insertion, TX frame duplication, RX duplicate-frame discard. Two other Microchip switch parts (LAN9355, KSZ9563) were considered and **rejected** for this role: neither datasheet documents HSR/PRP/MRP hardware support; substituting either would leave the Ethernet ring without hardware-level redundancy and is not permitted for the ring-node role. |

**Applied to:** Jayne board control half — Ethernet ring pass-through node (in/out via shielded
JST-GH connectors), with hardware-level HSR/PRP failover so a link break elsewhere in the ring
does not require software topology management on the PocketBeagle 2 nodes.

**Open item:** exact IEC 62439-3 clause numbers (Clause 4 HSR / Clause 5 PRP) applied to this
design require verification against the current IEC 62439-3 edition before final citation —
tracked in TODO.md §1.2c and in "Open Standards Verification Items" below.

**Used in:** `avionics/AGENTS.md`, `TODO.md`

---

### REF-SENSOR-006: TI TCAN1042HG-Q1 — CAN-FD Transceiver

| Field | Value |
|---|---|
| **Manufacturer** | Texas Instruments |
| **Product** | TCAN1042HG-Q1 |
| **Official product page** | <https://www.ti.com/product/TCAN1042-Q1> |
| **Datasheet URL** | <https://www.ti.com/lit/ds/symlink/tcan1042hg-q1.pdf> |
| **Qualification** | AEC-Q100 Grade 1 |
| **Note** | The "HG" suffix variant is required for full CAN-FD data-phase rate (5 Mbps); the plain TCAN1042-Q1 (no suffix) supports classic CAN and CAN-FD only up to 2 Mbps. Specify TCAN1042HG-Q1 explicitly in the BOM to avoid ordering the slower part. |

**Specifications applied in this design:**

| Parameter | Value | Source |
|---|---|---|
| Data rate | Up to 5 Mbps (CAN-FD data phase) | TCAN1042HG-Q1 datasheet |
| Package | SOIC-8 or VSON-8 (3×3 mm) | TCAN1042HG-Q1 datasheet |

**Applied to:** Jayne board control half — CAN-FD trunk transceiver, MSPM0G3507 MCAN peripheral
to shielded JST-GH CAN-FD connector.

**Used in:** `avionics/AGENTS.md`, `TODO.md`

---

### REF-SENSOR-008: AKM AK7455 — 14-bit Off-Axis Magnetic Rotation Angle Sensor

| Field | Value |
|---|---|
| **Manufacturer** | Asahi Kasei Microdevices (AKM) |
| **Product** | AK7455 Zero-Latency Angle Sensor IC |
| **Official product page** | <https://www.akm.com/global/en/products/rotation-angle-sensor/ak7455/> |
| **Announcement** | <https://www.akm.com/us/en/about-us/news/2022/20220509-ak7455/> ("14-bit magnetic rotation angle sensor … that supports off-axis configuration") |
| **Datasheet** | Doc **200800064-E-00** (2020/09), 68 pp — archived in repo at `avionics/datasheets/ak7455-en-datasheet-myakm.pdf` (AKM gates the web download behind a form) |
| **Note** | Selected for the wing/nacelle tilt-angle encoder (`MAL-TILT-ENC-PCB`) because it explicitly supports the **Off-Axis (side-of-shaft)** configuration required by the through-shaft tilt-spar, and adds anomaly-magnetic-field detection + dynamic error reduction + EEPROM INL calibration — suited to the ferromagnetic (4130/17-4 PH) spar. Supersedes the on-axis MT6701 (rejected) and AS5600 (Rev Q). |

**Specifications applied in this design:**

| Parameter | Value | Source (datasheet section) |
|---|---|---|
| Configuration | Shaft-End **and Off-Axis (side-of-shaft)** | §1, §3 |
| Angle resolution | 14-bit (0.022°/LSB) | §3, §10 |
| Angle INL | ±0.5° (shaft-end, no cal); ±0.1° after calibration | §3, §10 |
| Magnetic flux window | 30–70 mT (shaft-end); **10–70 mT (off-axis)**; low-flux alarm < ~15 mT | §10, §17 |
| Sense-plane select | X-Y / X-Z / Y-Z (`R_FIELDSEL`) | §1, §3 |
| Interface | 4-wire SPI (absolute + programming), ABZ, UVW, ERROR | §3, §6 |
| Supply / temp | 3.0–5.5 V ; −40 to +125 °C | §3 |
| Package | QFN24, 4.0 × 4.0 × 0.85 mm (EP/back-tab must be OPEN, Note5) | §3, §22 |
| Pin handling | TEST1 open (Note3); TEST2 → VSS (Note4); NC pins open (Note2) | §6 |

**Applied to:** wing-tip tilt-angle encoder board `MAL-TILT-ENC-PCB` — off-axis read of the
rotating ring magnet (`HALL-RING-MAG`) on the tilt-spar hub. Off-axis flux (10–70 mT) at
the IC and the EEPROM INL calibration are **bench-verification** items (AKM app support);
ERROR-pin push-pull-vs-open-drain and the QFN24 EP dimensions are layout-verification items.

**Used in:** `avionics/kicad/ENC-NACELLE-1.kicad_sch`, `avionics/kicad/ENC-NACELLE-1.md`,
`current-specification/bom_revS.csv` (`MAL-TILT-ENC-PCB`),
`airframe/wings-nacelles/WBS.md` §1.1.3.6, `avionics/WBS.md` §1.9.1

---

### REF-SENSOR-009: TI ISOW1044BDFMR — 5 kVrms Isolated CAN-FD Transceiver with Integrated Isolated DC-DC

| Field | Value |
|---|---|
| **Manufacturer** | Texas Instruments |
| **Product** | ISOW1044BDFMR |
| **Datasheet** | SLLSFF7A, archived at `avionics/datasheets/isow1044.pdf` |
| **Package** | 20-pin DFM (SOIC-20W compatible), `Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm` |
| **Note** | Combines galvanic signal isolation + an integrated isolated DC-DC converter in one part (no external isolated supply needed for the bus side) — used for every isolated CAN-FD node this project builds. Clean-room symbol `Jayne_MSPM0G3507_RGZ`/`Jayne_ISOW1044BDFMR` built directly from datasheet Table 7-1, first on Jayne, then reused verbatim on `CAN-PERIPH-GW-1` and Kaylee. |

**Used in:** `avionics/kicad/Jayne/kicads/Jayne.kicad_sch` (U4), `avionics/kicad/CAN-PERIPH-GW-1/` (U3 per stack), `avionics/kicad/Kaylee/kicads/Kaylee.kicad_sch` (U_ISOCAN), `avionics/kicad/Wash/kicads/Wash.kicad_sch`, `avionics/kicad/Zoë/kicads/Zoë.kicad_sch` (both fixed 2026-07-26, see Removed/Superseded Citations).

---

### REF-SENSOR-010: TI ISOW1412 — 5 kVrms Isolated RS-485/RS-422 Transceiver with Integrated Isolated DC-DC

| Field | Value |
|---|---|
| **Manufacturer** | Texas Instruments |
| **Product** | ISOW1412 (500 kbps variant; ISOW1432 is the pin-compatible 12 Mbps variant, not used) |
| **Datasheet** | SLLSF86C, archived at `avionics/datasheets/isow1412.pdf` |
| **Package** | 20-pin DFM (SOIC-20W compatible), `Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm` |
| **Note** | Full-duplex part (separate Y/Z driver-out and A/B receiver-in pins); run in half-duplex mode on this project's 2-wire RS485_A/RS485_B multi-drop bus by shorting Y-to-A and Z-to-B, matching the standard technique for using a full-duplex transceiver as half-duplex. Selected 2026-07-26 to replace ADI ADM2795E fleet-wide (see Removed/Superseded Citations) because it integrates its own isolated DC-DC for the bus-side supply — ADM2795E is signal-only and needs a separate external isolated supply. Clean-room symbol built directly from datasheet Table 7-1 ("Pin Functions"). |

**Used in:** `avionics/kicad/CAN-PERIPH-GW-1/` (U4 per stack, `GW_ISOW1412`), `avionics/kicad/Jayne/kicads/Jayne.kicad_sch` (U6), `avionics/kicad/Kaylee/kicads/Kaylee.kicad_sch` (U_RS485), `avionics/kicad/Wash/kicads/Wash.kicad_sch`, `avionics/kicad/Zoë/kicads/Zoë.kicad_sch` (both fixed 2026-07-26, renamed from the broken inline "ADM2795EBRWZ" symbol).

---

### REF-SENSOR-011: Infineon OPTIGA™ SLB 9670 — SPI TPM 2.0

| Field | Value |
|---|---|
| **Manufacturer** | Infineon Technologies |
| **Product** | OPTIGA™ TPM SLB 9670 TPM2.0 (SLB9670VQ2.0 / SLB9670XQ2.0) |
| **Datasheet** | Revision 1.4, 2018-12-07, archived at `avionics/datasheets/SLB_9670VQ20_Infineon.pdf` |
| **Package** | PG-VQFN-32-13, `Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm` |
| **Note** | Fleet-standard TPM (root `AGENTS.md` §Security: "every Cape carries a TPM"). Clean-room symbol `Jayne_SLB9670_TPM` built directly from datasheet Tables 3/4/5, first on Jayne, reused verbatim on `CAN-PERIPH-GW-1`, Kaylee, and Emma (2026-07-26). **Not** the same as the inline "SLB9670" symbol already embedded in Wash.kicad_sch/Zoë.kicad_sch, which was found (2026-07-26, not yet corrected) to have incorrect pin numbers relative to this same datasheet — see Removed/Superseded Citations. |

**Used in:** `avionics/kicad/Jayne/kicads/Jayne.kicad_sch` (U5), `avionics/kicad/CAN-PERIPH-GW-1/` (U2 per stack), `avionics/kicad/Kaylee/kicads/Kaylee.kicad_sch` (U_TPM), `avionics/kicad/Emma/kicads/Emma.kicad_sch` (TPM).

---

### REF-SENSOR-012: STS3215 Serial-Bus Servo — Cargo Winch Drive

> **⚠ REQUIRES VERIFICATION (root `AGENTS.md` §4).** The archived datasheet is a
> **scanned/CID-encoded PDF**, and no OCR toolchain is available in the current build
> environment (`pdftotext`, `tesseract`, `mutool`, `poppler-utils` absent; `pypdf` fails on a
> broken `cryptography` build). **No performance figure below is quoted from that datasheet.**
> Nothing in this entry may be cited as a verified value until the gaps are read off the
> document and this table is updated. Tracked in "Open Standards Verification Items" and in
> `docs/TODO.md` §0.x.

| Field | Value |
|---|---|
| **Part Number** | STS3215 (repo SKU 108090023, variant C001) |
| **Manufacturer** | ⚠ Not yet confirmed from the datasheet |
| **Datasheet** | `docs/references/108090023_STS3215-C001_Datasheet.pdf` — revision/date ⚠ not extracted |
| **Control Interface** | **TTL half-duplex serial bus, ID-addressable** — **not** 1000–2000 µs PWM. Lands on `CAN-PERIPH-GW-1` `J_FLEX` → `FLEX_TTL_GPIO`, documented there as covering "a TTL-level digital servo protocol (e.g. a serial-bus servo)". |
| **Operating Voltage** | Driven at 5.4 V nominal from Kaylee RAIL-2 `5V_JAYNE` (project-side decision, not a datasheet limit) |
| **Torque** | ⚠ Not verified. **Design requirement is ≥ 3.2 kgf·cm (0.31 N·m)** at the coupler — derived in `docs/CARGO_WINCH_SPECIFICATION.md` §4.2, must be checked against the real rating. |
| **Stall current** | ⚠ Not verified. Budgeted at 1.2 A for the RAIL-2 sizing (spec §5.4); if actual stall exceeds ~2.5 A, RAIL-2 must be resized. |
| **Mass** | ⚠ Not verified. **60 g assumed** in the mass/CG table (spec §6); this term dominates the +98.6 g net delta and the resulting T/W 1.613 → 1.557. |
| **Case envelope / boss pattern** | ⚠ Not verified. Blocks `make_winch_pedestal_port()` in `airframe/stls/fuselage/cargo/generate_cargo_mounts.py`. |
| **Application** | Cargo winch drive. Transmits **torque only** through a lost-motion dog coupler; the spool is carried on two MR84ZZ bearings on a fixed Ø4 mm axle clamped at both pedestals, so no radial load reaches the servo output. Paired with a normally-engaged one-way safety ratchet whose catch is retracted by a solenoid on the same gateway. Signed CAN-FD telemetry per [REF-NIST-001 §2.1]. |

**Supersedes:** the Rev P/Q/R `N20-WINCH` (N20 300RPM 6V gearmotor) and its cantilever mount
`cargo_winch_motor_mount.stl` + N20-bored `cargo_winch_spool.stl`.

**Used in:** `docs/CARGO_WINCH_SPECIFICATION.md` (Rev B), `docs/bom_revR.json`
(`STS3215-WINCH`), `airframe/stls/fuselage/cargo/generate_cargo_mounts.py`.

**Status:** ACTIVE specification, **NOT cleared for procurement or STL generation** until the
⚠ rows above are resolved.

---

## Part XIII — Telecommunications Standards

### REF-TIA-001: ANSI/TIA-485-A — Electrical Characteristics of Generators and Receivers for Use in Balanced Digital Multipoint Systems (RS-485)

| Field | Value |
|---|---|
| **Issuing authority** | Telecommunications Industry Association (TIA), formerly Electronic Industries Alliance (EIA) |
| **Designation** | ANSI/TIA-485-A:1998 (also known as EIA-485, TIA/EIA-485-A) |
| **Official URL** | <https://www.tiaonline.org/standards/> — search "TIA-485"; also available via ANSI webstore: <https://webstore.ansi.org/> |
| **Note** | Originally published as EIA-485 by the Electronic Industries Alliance; re-designated ANSI/TIA-485-A when EIA's telecommunications sector became TIA.  The "A" revision (1998) is the current active edition.  This is a purchased standard.  Exact product-page URL not confirmed during catalog entry; access through TIA standards portal or ANSI webstore (see Open Standards Verification Items). |

**Sections applied in this project:**

| Section | Title | Application |
|---|---|---|
| §5 | Driver output characteristics | ±1.5 V minimum differential; ±6 V maximum; source impedance constraints |
| §6 | Receiver input characteristics | 200 mV hysteresis; −7 V to +12 V common-mode range |
| §7 | Bus loading | Up to 32 unit loads (UL) per bus segment; each ADM2795EBRWZ loads ≤ 1 UL per node |
| §9 | Cable characteristics | 120 Ω characteristic impedance; matched by 120 Ω termination at CN1 and FC4 |

**Applied to:** 8-node RS-485 half-duplex multidrop bus; ADM2795EBRWZ isolated RS-485
transceivers on Wash (Cape-A-2) and Zoë (Cape-B-2); 120 Ω termination resistors at CN1
(Shepherd's Room / Bay A) and FC4 (Simon's Medbay / Bay E).

**Used in:** `docs/AVIONICS_PB2_REDESIGN.md`, `docs/REVN_BUILD_GUIDE_24IN.md`,
`avionics/kicad/Wash.md`, `avionics/kicad/Zoë.md`,
`avionics/firmware/dts/cape-a/k3-am6254-pocketbeagle2-serenity-cape-a2.dts`,
`avionics/firmware/dts/cape-b/k3-am6254-pocketbeagle2-serenity-cape-b2.dts`,
`graphical-build-guide/build_guide_11_inter_board.svg`

---

## Part XIV — Upstream CAD / Derivative-Source Attributions

References in this part are upstream works — 3D models, officially licensed blueprints, and
reference renders — that either (a) had a mechanism or geometry concept adapted into a derivative
design, or (b) serve as a **canonical-accuracy ground-truth** reference for shape/proportion
fidelity to the real ship.  Per AGENTS.md, derivative files must carry the full attribution chain
back to upstream sources, meeting or exceeding CC-BY-4.0 requirements; reference-only sources are
cataloged so their provenance and license status are auditable even though no asset is redistributed.

**Canonical-accuracy authority ranking** (see the "Canonical-Accuracy Reference Hierarchy" above,
and `airframe/AGENTS.md`): REF-CAD-003 (QMx 2007 blueprints, most authoritative) → REF-CAD-002
(Nick Henning renders, derived detail) → REF-CAD-004 (misubisu Thingiverse model, the `s_*.stl`
origin — verify against the two above).  These live in `docs/references/`.

### REF-CAD-001: BamJr — "Variable-area EDF nozzle" (Thingiverse Thing 2991269)

| Field | Value |
|---|---|
| **Author** | BamJr (Thingiverse user) |
| **Work** | Variable-area EDF nozzle (parametric iris / variable-area duct exit) |
| **Designation** | Thingiverse Thing 2991269 |
| **Official URL** | <https://www.thingiverse.com/thing:2991269> |
| **License** | Creative Commons Attribution 4.0 International (CC BY 4.0) — <https://creativecommons.org/licenses/by/4.0/> |
| **Note** | Used only as a *mechanism/kinematics reference* for a variable-area duct-exit nozzle.  Serenity-UAV's nozzle geometry (throat liner, tangential-hinge overlapping conical flaps, 72T unison ring gear, spiral cam actuation, and the entire tilt gear train) is original work authored for this project; no BamJr geometry, mesh, or source file is copied or redistributed.  Attribution recorded here to satisfy CC-BY-4.0 even though no BamJr asset is included in the repository. |

**Concept applied in this project:** the variable-area duct-exit nozzle (iris
family) concept informed the Rev R2 overlapping-flap conical variable nozzle,
which sweeps 75 %→105 % of the 50 mm EDF bore radius across the −5°/140° nacelle
tilt range.

**Applied to:** the passively gear-linked variable nozzle on each nacelle
(nozzle exit follows nacelle tilt: 75 % bore radius at 0°/cruise, 105 % at
≥90°/hover-and-back).

**Used in:** `airframe/openscad/nacelles/nacelle_nozzle_iris.scad`,
`README.md` (Iris mechanism concept), `TODO.md` §1.1.3.1

### REF-CAD-002: Nick Henning — Firefly Class Serenity wing and landing gear reference renders

| Field | Value |
|---|---|
| **Author** | Nick Henning |
| **Work** | Serenity / Firefly Class wing and landing gear reference renders |
| **Designation** | Public reference render collection |
| **Official URL** | <https://www.nickhenning3d.com/> |
| **License / Permission** | Public-space reference imagery; direct permission granted by email from Nick Henning (`nickhenning3d@gmail.com`) on 2026-07-06 (email export archived at `docs/references/nick-henning/`). Used only as design reference imagery and attribution is recorded here to satisfy CC BY-style attribution requirements. |
| **Note** | Used as high-fidelity visual reference for wing surface detail, landing gear arrangement, and UV-display styling. Per Nick Henning's email, this model was a school project **derived from the show/movie renders** — so it sits **below** the QMx blueprints (REF-CAD-003) in the canonical-accuracy ranking but carries **more mechanical/surface detail**; use it where the blueprints are ambiguous. The repository stores only derivative reference imagery; no original CAD model or proprietary 3D geometry from the author is redistributed. |

**Applied to:** wing and landing gear detail reference in the Serenity UAV hull design, including landing gear canopy/brace styling and wing surface treatment; canonical-accuracy cross-check for exterior detail.

**Consolidated 2026-07-20:** all Nick Henning material was moved from `airframe/diagrams/` into a
single `docs/references/nick-henning/` folder alongside the other canonical references.

**Used in:** `docs/references/nick-henning/` — 14 renders plus the permission email:

- `b1cf1d_*.jpg` (×5) — high-resolution site-export source renders
- `nick-henning-close-back-combine.jpg`, `nick-henning-close-bridge-combine.jpg`, `nick-henning-close-gear-combine.jpg` — close composite renders
- `nick-henning-final-backside-combine.jpg`, `nick-henning-final-front-combine.jpg`, `nick-henning-final-top-combine.jpg` — full-ship composite renders
- `nick-henning-uvdisplay-engine.jpg`, `nick-henning-uvdisplay-gear.jpg`, `nick-henning-uvdisplay-wing.jpg` — UV-display renders
- `Re: Contact got a new submission - Nick Henning <nickhenning3d@gmail.com> - 2026-07-06 1421.txt` — raw permission-grant email export (retains full mail-transport headers — flagged to the user, not scrubbed)

### REF-CAD-003: QMx — The Official Serenity Blueprints Reference Pack (2007)

| Field | Value |
|---|---|
| **Publisher** | Quantum Mechanix Inc. (QMx) — <https://www.quantummechanix.com/> (the pack styles the publisher in-universe as "Quantum Mechanix Inc., Earth That Was") |
| **Creators** | Geoffrey Mandel (Serenity graphic designer) and Timothy (Tim) Earls (Firefly illustrator / Serenity set designer) — both original *Serenity* production designers |
| **Work** | *The Official Serenity Blueprints Reference Pack* — 33 pages of full-color blueprints, systems, and layout documentation for the Firefly-class transport *Serenity* (sequel to the 2007 limited-edition *Serenity Blueprints* set) |
| **Repository copy** | `docs/references/The_Official_Serenity_Blueprints_Reference_Pack.pdf` (20-page reference tablet extract, 3.7 MB) |
| **License** | **Copyrighted, officially licensed commercial product — NOT CC BY.** © Quantum Mechanix Inc., produced under license from the *Firefly*/*Serenity* rights holders (Universal Pictures / Twentieth Century Fox, now The Walt Disney Company). Retained in-repo **for internal design reference only**; no page, image, or derivative is redistributed under CC BY 4.0. Used under the same non-commercial fan-engineering basis described in "Creative-Universe Attribution and Fan-Engineering Terms" above. |
| **Note** | **MOST AUTHORITATIVE canonical geometry reference in this project.** These blueprints are the officially licensed, production-derived documentation of Serenity's design; they define canonical proportion and layout but are drawn at line-art fidelity and lack fine mechanical/CAD detail. Where this pack and any other reference disagree on canonical shape, **this pack wins.** |

**Concept/reference applied in this project:** ground-truth for exterior mold-line proportion, section
layout (head/cargo/middle/rear), and canonical feature placement. No QMx geometry is copied; it is a
visual/dimensional accuracy check only.

**Used in:** canonical-accuracy reference for `airframe/` hull/exterior work (see
`airframe/AGENTS.md` "Canonical Accuracy References"); cross-referenced by REF-CAD-002 and
REF-CAD-004 and by `current-specification/LICENSE_AND_ATTRIBUTION.md`.

### REF-CAD-004: misubisu — "Serenity Firefly with landing gear and swivel engines" (Thingiverse Thing 7330462)

| Field | Value |
|---|---|
| **Author** | misubisu (Thingiverse user) |
| **Work** | Serenity Firefly with landing gear and swivel engines (multi-part printable model — head, cargo, middle, rear, wings, engines, landing gear) |
| **Designation** | Thingiverse Thing 7330462 |
| **Official URL** | <https://www.thingiverse.com/thing:7330462> |
| **License** | Creative Commons Attribution 4.0 International (CC BY 4.0) — <https://creativecommons.org/licenses/by/4.0/> |
| **Repository copy** | `docs/references/thingverse-serenity/` (source STLs in `files/`, renders in `images/`, upstream `LICENSE.txt` + `README.txt`) |
| **Note** | This is the **origin of the project's `s_*.stl` geometry** — every hull/nacelle/wing/gear STL in the build traces back to this model (adapted: scaled to 24 in (609 mm), hollowed to 2.0 mm CF-PETG, CF skeleton + foam fill added). It is the **lowest** of the three canonical references in authority: **verify its detail against REF-CAD-003 (QMx) and REF-CAD-002 (Nick Henning) before treating any feature as canonical** — but it remains a usable, license-clean geometry starting point. Do not confuse Thing 7330462 with the separate low-poly orientation guide Thing 4677565 (`current-specification/LICENSE_AND_ATTRIBUTION.md` §2b). |

**Applied to:** base hull/section geometry for the entire fuselage and nacelle build; the four
canonical sections and the swivel-engine/tilt concept originate here.

**Used in:** `airframe/stls/` (all `s_`-lineage fuselage/nacelle/wing/landing-gear STLs, `s_` prefix
dropped Rev R1); full remix attribution in
[`current-specification/LICENSE_AND_ATTRIBUTION.md`](current-specification/LICENSE_AND_ATTRIBUTION.md) §2.

---

## Removed / Superseded Citations

The following references appeared in earlier versions of project files but have been removed
because they were incorrectly attributed, unverifiable, or inapplicable.

| Old Citation | Where Found | Reason Removed | Replacement |
|---|---|---|---|
| "NIST SP 800-72 principles" (write-blocker design) | `README.md` §Patent Notice, line 382 | **Incorrect attribution.** NIST SP 800-72 (2004) is "Guidelines on PDA Forensics" — unrelated to write-blocker design. The closest applicable standard is NIST SP 800-92 §4.4.2 (log data protection principles). | REF-NIST-004 (NIST SP 800-92 §4.4.2) |
| 47 CFR Part 95 RCRS (§95.635/§95.655/§95.639, "TDDS"/"LERS"/"27 channels") | REF-FCC-003, `malcolm_antenna_spec.md`, `AGENTS.md`, `README.md`, `TODO.md`, `AVIONICS_PB2_REDESIGN.md` | **Wrong band.** RCRS covers only 26–28/72/75 MHz, not 49 MHz; "TDDS"/"LERS"/27-channel terms untraceable. Emma's 49.82–49.90 MHz band is Part 15 §15.235, unlicensed. | REF-FCC-003 (Part 15 §15.235) |
| "ASTM F3322 — sUAS Battery Safety" | TODO.md §0.4 (candidate list, not yet cited in active docs) | **Incorrect attribution.** F3322 is the *Standard Specification for Small Unmanned Aircraft System (sUAS) Parachutes* — unrelated to batteries, and not applicable to Serenity (no deployable recovery parachute). | REF-ASTM-002 (ASTM F3005-22, sUAS battery specification) |
| "ASTM F3003 — Quality Assurance of a Small Unmanned Aircraft System" | TODO.md §0.4 (candidate list, not yet cited in active docs) | **Withdrawn standard.** F3003-14 was withdrawn by ASTM in January 2023 with no replacement. | None — see REF-ASTM-001 (F2910) for design/construction/test coverage |
| RunCam Nano 4 analog camera (REF-SENSOR-001) at bow sensor pod | `avionics/AGENTS.md`, `TODO.md` §1.1.1.1a | **Superseded by design decision (2026-07-03), not an error.** Replaced by the Jayne board's TI AM62Ax digital vision SoC (REF-SENSOR-003) at both the nose and cargo bay locations. | REF-SENSOR-003 (TI AM62Ax) |
| "TI DM38x + remixed OpenIPC firmware" (early Jayne design concept from an external AI-assisted brainstorm, never committed) | Not committed to any file — caught during REFERENCES.md drafting 2026-07-03 | **Infeasible as proposed.** TI DM385/DM388 (DaVinci DM38x) are NRND; OpenIPC's supported-hardware list contains no TI part, not even at R&D stage — porting would mean a from-scratch ISP/encoder bring-up on a chip TI is discontinuing, not a firmware port. Also: the same source proposed LAN9355/KSZ9563 for "MRP" ring redundancy (neither chip implements it) and an "ST33GTPMISPI" TPM part number that does not exist. | REF-SENSOR-003 (TI AM62Ax, in-production, TI's own open BSP), REF-SENSOR-005 (KSZ9477, real HSR/PRP support), Infineon SLB9670 (fleet-standard TPM, REFERENCES.md §3.3/§4.2) |
| ADI ADM2795EBRWZ (isolated RS-485, signal-only) — `Jayne`, `CAN-PERIPH-GW-1`, `Kaylee`, `Wash`, `Zoë` RS-485 transceivers | `avionics/kicad/Jayne/kicads/Jayne.kicad_sch`, `avionics/kicad/CAN-PERIPH-GW-1/`, `avionics/kicad/Kaylee/kicads/Kaylee.kicad_sch`, `avionics/kicad/Wash/kicads/Wash.kicad_sch`, `avionics/kicad/Zoë/kicads/Zoë.kicad_sch` | **Superseded by design decision, 2026-07-26.** ADM2795E provides signal isolation only and requires a separate external isolated DC-DC supply for its bus-side VDD2. TI ISOW1412 integrates its own isolated DC-DC, eliminating the extra supply and simplifying every "trust module" node fleet-wide. Fleet-wide swap performed 2026-07-26. Separately, while performing this swap on Wash and Zoë, found their pre-existing ADM2795EBRWZ symbols had incorrectly numbered pins (and their ISOW1044BDFMR symbols had the wrong footprint, `SOIC-16W` instead of the correct `SOIC-20W` for a 20-pin part) — both defects predate this session and were corrected as part of the same fix (`kicad-cli sch erc` violation counts unchanged before/after: Wash 48, Zoë 234 — confirming the fix corrected the target defects with zero regression against these boards' large, pre-existing, out-of-scope ERC backlog). | REF-SENSOR-010 (TI ISOW1412) |

---

## Open Standards Verification Items

The following citations in the codebase require verification before first flight.
Add verified section numbers to the relevant files and update this table.

| Citation | File | Issue | Action Required |
|---|---|---|---|
| §15.203 antenna restriction (Emma RF connector) | Emma board files, `malcolm_wiring.md` | **Confirmed, resolved 2026-06-20.** §15.203 binds the manufacturer directly. J2 used a generic SMA edge connector (Amphenol 132289), a standard jack; no exception applies. | **Resolved:** J2 changed to 132289RP (RP-SMA, same footprint), satisfying §15.203. Board re-spin tracked in TODO.md §0.1 |
| 14 CFR Part 47 (aircraft registration marks) | `ax25_types.h` | **Resolved 2026-06-21.** README/build guide had no erroneous citation; the miscitation was in `ax25_types.h`, which stated Part 47 governs registration and AX.25 needs an amateur license (Part 97) | Corrected to cite Part 48 §48.205 [REF-FAA-001]; link is license-exempt under Part 15 §15.235 [REF-FCC-003], per REF-PROTO-001 |
| AUVSI "standards" (unnamed) | `AGENTS.md`, `README.md` | **Resolved 2026-06-22.** No specific numbered AUVSI standard exists (AUVSI publishes frameworks, not numbered design standards). Identified and verified three applicable ASTM F38 standards. | Added REF-ASTM-001 (F2910-22, design/construction/test), REF-ASTM-002 (F3005-22, batteries), REF-ASTM-003 (F3269-21, runtime assurance/failover). `AGENTS.md`/`README.md` AUVSI text is accurate as-is (AUVSI frameworks, not numbered standards) — no doc text change needed there. |
| IEC 62368-1 clause numbers | PCB layout (not yet complete) | PCB layout must verify creepage/clearance distances meet IEC 62368-1 Clause 5.5.2 requirements for 5 kV reinforced insulation; this cannot be verified until PCB layout is complete | Verify during Wash and Zoë PCB layout review (see TODO.md §1.4) |
| REF-IEC-003 (IEC 61000-4-2) exact product URL | `REFERENCES.md` REF-IEC-003 | Exact webstore.iec.ch product-page URL not confirmed during catalog entry (WebFetch redirected to homepage during verification attempt 2026-06-29); standard designation and content are correct | Confirm product page URL via <https://webstore.iec.ch/> search for "IEC 61000-4-2" and update REF-IEC-003 |
| REF-IEC-004 (IEC 61000-4-4) exact product URL | `REFERENCES.md` REF-IEC-004 | Same as REF-IEC-003 — webstore URL not confirmed 2026-06-29 | Confirm via <https://webstore.iec.ch/> search "IEC 61000-4-4" |
| REF-IEC-005 (IEC 61000-4-5) exact product URL | `REFERENCES.md` REF-IEC-005 | Same as REF-IEC-003 — webstore URL not confirmed 2026-06-29 | Confirm via <https://webstore.iec.ch/> search "IEC 61000-4-5" |
| REF-TIA-001 (ANSI/TIA-485-A) exact product URL | `REFERENCES.md` REF-TIA-001 | TIA standards portal URL not confirmed via WebFetch 2026-06-29 (domain blocked by permission hook) | Confirm product page via <https://www.tiaonline.org/standards/> or <https://webstore.ansi.org/> search "TIA-485-A" |
| Anti-collision flash rate "60 FPM" | `build_guide_13_nav_lights.svg`, `decal_sheet.svg` | **Resolved 2026-06-29.** Researched 14 CFR Part 107 §107.29(b) (anti-collision light visible 3 statute miles — no flash rate specified), old Part 23 §23.1401 (reorganized 2017, prescriptive flash-rate text no longer exists in current eCFR), and Part 25 §25.1401(f) (transport category, 40–100 FPM — not directly applicable to this sUAS). No currently-enforceable regulatory standard applicable to Part 107 UAS mandates a specific flash rate. "60 FPM" in the build guide is a design convention within the conventional aviation anti-collision light range (40–100 FPM). No regulatory citation is required or appropriate; the figure is a design target, not a compliance claim. | No citation required — design convention documented here. |
| REF-SENSOR-005 (KSZ9477 HSR/PRP) IEC 62439-3 clause numbers | `REFERENCES.md` REF-SENSOR-005 | AN3474 confirms HSR/PRP hardware support but exact IEC 62439-3 Clause 4 (HSR)/Clause 5 (PRP) sub-clause numbers applied have not been cross-checked against the standard text itself | Obtain IEC 62439-3 and confirm clause numbers before final PCB layout citation (TODO.md §1.2c) |
| Jayne laser — single 520 nm green source, **Class 2 both sites**, part/optic ratings | `REFERENCES.md` REF-IEC-002, `avionics/kicad/Jayne/Jayne.md`, `docs/JAYNE_LASER_ANALYSIS.md` | Per `docs/JAYNE_LASER_ANALYSIS.md` Rev A1 (2026-07-05) both installs share ONE 520 nm green diode + driver and are **both Class 2 (≤1 mW)** — the nose is a concentrated dot detected by Jayne's camera (strobe + frame-difference), ~0.45 mW, NOT the inherently Class 3B module of Rev A. Differ only by per-location terminal optic (spread) + hardware current limit. No real, sourced part exists yet. | Source a real datasheet with manufacturer-stated mW output and IEC 60825-1 class for the green diode + both optics before procurement; update REF-IEC-002 with the verified citation (TODO.md §1.2c.4). Do not fabricate or procure against the placeholder. Both Class 2 caps must be hardware-enforced; no Class 3B interlock/shutter required unless a human-at-target-in-full-sun requirement is later added. |
| Emma `RSSI_CMP` carrier-detect comparator part number and pinout | `avionics/kicad/Emma.kicad_sch` / `Emma.kicad_pcb`, `avionics/kicad/mod_emma_pcb.py` | The RSSI→`RSSI_DCD` conversion (2026-07-04 reconciliation) adds an on-board comparator, value placeholder "LMV331-class". No specific part is vetted; the PCB pad→net map is by function only and the SOT-23-5 pin order is unconfirmed. | Select a real comparator, confirm its SOT-23-5 datasheet pinout (and push-pull vs open-drain — add a `RSSI_DCD` pull-up if open-drain), add a `REF-*` catalog entry with a validated URL, and correct the footprint pad map before layout is final (TODO.md §1.2b). Do not fabricate or procure against the placeholder. |
| VL53L5CX obstacle-avoidance ToF sensor — no REF-ID | `docs/failsafe_thresholds.md`, `avionics/firmware/common/include/failsafe_config.h`, `docs/PHASED_BUILD_GUIDE.md` | Found 2026-07-12 while writing the Failsafe Threshold Document: the 12× VL53L5CX obstacle-avoidance array is cited throughout the repository (4 m range noted informally inside the REF-SENSOR-002 entry above) but has no `REFERENCES.md` catalog entry of its own, unlike the project's other core sensor ICs (REF-SENSOR-002 through -006). | Add a `REF-SENSOR-007` entry for ST Microelectronics VL53L5CX (validated datasheet URL, ranging accuracy, and the 4 m operating range cited in `docs/failsafe_thresholds.md` §3) before final PCB layout citation sign-off (TODO.md §3.0 Phase 0). |
| Tilt-spar material allowables (4130 + trade-study alternates) | `docs/TILT_SPAR_ANALYSIS.md` §3.1–3.2/§3.5, `current-specification/bom_revS.csv` SPAR-TILT-4130 | The §3.5 material trade study uses **typical handbook allowables** for AISI 4130 (~460 MPa yield), 17-4 PH H1075 (~860 MPa), 7075-T6 (~503 MPa), 6061-T6 (~276 MPa), 316 SS, and Ti-6Al-4V (~880 MPa); none are yet tied to a validated MMPDS/AMS product page. Moduli/densities are nominal. | Confirm the **selected** material's design allowable and the two carried alternates (17-4 PH, 7075-T6) vs MMPDS-2023 / AMS (or mill cert) and add `REF-MAT-*` catalog entries with validated URLs before spar procurement (TODO §0.8). |
| 14 CFR Part 107 dropped-object provision — section number **not yet verified** | `REFERENCES.md` REF-FAA-002 applied-sections table, `docs/CARGO_WINCH_SPECIFICATION.md` §3.10.2 | Part 107 contains a provision prohibiting dropping an object from a small UA in a manner that creates an undue hazard to persons or property. REF-FAA-002's applied-sections table currently lists only §107.3, §107.29, §107.31 and §107.51(a)–(d) — the dropped-object section is **absent**, so no section number is asserted in the winch spec (root `AGENTS.md` §4: never guess a section number). This matters because the cargo winch **intentionally** releases a payload (requirement R5, overload line-shed) while an uncommanded structural release of the spool itself (19.1 J, or 31.8 J for the full assembly, from the §107.51(b) 400 ft ceiling) is precisely the hazard the provision addresses. | Look up the section in the eCFR Part 107 text, add it to REF-FAA-002's applied-sections table with the exact title and a validated URL, then cite it in `docs/CARGO_WINCH_SPECIFICATION.md` §3.10.2 and state explicitly how a commanded shed differs from an uncommanded release under that text. Do not fabricate the number. (`docs/TODO.md` §0.x) |
| STS3215 cargo winch servo — envelope, torque, mass, stall current (REF-SENSOR-012) | `REFERENCES.md` REF-SENSOR-012, `docs/CARGO_WINCH_SPECIFICATION.md` §3.1, `docs/bom_revR.json` `STS3215-WINCH`, `airframe/stls/fuselage/cargo/generate_cargo_mounts.py` | The datasheet **is in the repo** (`docs/references/108090023_STS3215-C001_Datasheet.pdf`) but is a **scanned/CID-encoded PDF** and could not be text-extracted in the build environment (no `pdftotext`/`tesseract`/`mutool`/`poppler-utils`; `pypdf` fails on a broken `cryptography` build). Consequently **no** performance figure for this part is datasheet-verified. Four values are currently assumed or derived, not read: (a) **case envelope + mounting-boss pattern** — blocks `make_winch_pedestal_port()`; (b) **torque** — the design *requires* ≥ 3.2 kgf·cm (spec §4.2), unconfirmed against the real rating; (c) **mass** — 60 g assumed, and this term dominates the +98.6 g net mass delta and the T/W 1.613 → 1.557 result in spec §6; (d) **stall current** — budgeted 1.2 A for RAIL-2 sizing (spec §5.4). The interface is stated as **TTL half-duplex serial bus (not PWM)**, consistent with `CAN-PERIPH-GW-1.md` §G, but this too should be confirmed off the datasheet. | Read the four values off the datasheet (or the vendor's published spec page, cited with a validated URL) and update REF-SENSOR-012, spec §3.1/§4.2/§5.4/§6, and the BOM entry. **Do not order the part or generate the six winch STLs until (a) and (b) are resolved**; re-run the §6 mass/CG table if (c) differs from 60 g; resize RAIL-2 if (d) exceeds ~2.5 A. Do not fabricate these numbers. (`docs/TODO.md` §0.x) |
| Wing/nacelle Hall tilt encoder — sensor selection | `current-specification/bom_revS.csv` MAL-TILT-ENC-PCB, `avionics/kicad/ENC-NACELLE-1.*`, `docs/TILT_SPAR_ANALYSIS.md` §1/§3.5/§8.1, `avionics/WBS.md` §1.9.1 | **RESOLVED 2026-07-19 (datasheets in repo).** MT6701 (Rev 1.9) was **rejected** — its datasheet §6 confirms it is **on-axis only** (Ø6 mm cyl magnet, off-axis misalignment ≤ 0.3 mm), so it cannot read the through-shaft off-axis; AS5600 has the same limit. Part selected = **AKM AK7455** (REF-SENSOR-008), which explicitly supports the Off-Axis (side-of-shaft) configuration; pinout/interface **verified** vs datasheet 200800064-E-00 and the schematic rebuilt (`kicad-cli` ERC 0-error). Interface is **SPI** (no off-axis absolute IC offers I²C). | **Electrical spec resolved.** Remaining, now scoped as bench/layout items (not "unverified part"): (1) off-axis flux 10–70 mT at the IC with the chosen ring/gap; (2) EEPROM INL calibration over −5..90° (AKM app support); (3) ERROR-pin push-pull vs open-drain; (4) QFN24 4×4 EP dims (EP left floating) + wing-pocket resize 3×3→4×4 (`HALL_*` in `wings_s1223_revo.scad`); (5) confirm the AKM product URL if the datasheet is re-hosted. TODO §0.8 / `airframe/wings-nacelles/WBS.md` §1.1.3.6. |
| Wash's own inline "SLB9670" TPM symbol pin numbers | `avionics/kicad/Wash/kicads/Wash.kicad_sch` | Found 2026-07-26 while building Emma's TPM addition (which deliberately reused the separately-verified `Jayne_SLB9670_TPM` clean-room symbol instead, precisely to avoid this defect): Wash's own, independently-authored inline "SLB9670" symbol has pin numbers that do not match datasheet Revision 1.4 Tables 3–5 (REF-SENSOR-011). Not fixed this session — out of scope for the CAN-FD/RS-485 trust-module task. | Rebuild Wash's TPM symbol from REF-SENSOR-011 using the same clean-room `parse_real_symbol`/pin-table method as `Jayne_SLB9670_TPM`, or replace the instance with that verified symbol outright; re-run `kicad-cli sch erc` to confirm no regression against Wash's existing 48-violation baseline. |
| VimDrones `ap_periph_pico` / ESC S50 concept-only inspiration, `CAN-PERIPH-GW-1` and CAN-PERIPH-GW-1's ESC-gateway deployment mode | `avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md` | **Not a citation defect — documented here for license-boundary auditability.** `CAN-PERIPH-GW-1` was built as a fleet-integrated remix of the *publicly documented product concept* at <https://dev.vimdrones.com/products/vimdrones_can_periph_pico/> and <https://dev.vimdrones.com/products/vimdrones_esc_s50/> (peripheral-bus CAN/servo gateway; per-ESC CAN telemetry). VimDrones' own KiCad source (`VimDrones/AM32_esc_development_board` on GitHub) is licensed GPL-3.0, which is incompatible with this project's CC-BY-4.0-or-better attribution baseline for derivative files — no VimDrones schematic, footprint, or geometry was copied; only the public product specification was used as design inspiration, and the entire trust-module implementation (MCU, TPM, isolators, netlist) is original clean-room work against TI/Infineon datasheets. | N/A — informational; see `CAN-PERIPH-GW-1.md` "Why VimDrones' concept but not VimDrones' hardware" |
