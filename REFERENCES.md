# REFERENCES.md — Serenity UAV Standards and Regulatory Reference Catalog

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0
**Revision:** S
**Last updated:** 2026-08-22
**Revision history:** Rev R (2026-06-10) → Rev R1 (2026-06-11, hull-frame bake) → Rev S
(2026-07-04, comprehensive checkpoint — integrates all Rev R1/R1c/R1d/R2 modifications;
see TODO.md "Rev S Checkpoint" for the full consolidated changelog) → 2026-07-20 (added the
Creative-Universe Attribution section and the `docs/references/` canonical-reference library:
REF-CAD-003 QMx 2007 Blueprints pack, REF-CAD-004 misubisu Thingiverse origin model; expanded
REF-CAD-002 Nick Henning after consolidation) → 2026-08-01 (TODO.md §0.9 licensing audit: added
Part XV REF-LIC-001/002, corrected REF-CAD-004 license to CC BY-SA 4.0, documented the
CERN-OHL-W 2.0 / CC BY-SA 4.0 dual-license split) → Rev T (2026-09-06, project-wide
comprehensive checkpoint — `docs/WBS.md` §6.4; no new citations added by this checkpoint
itself, the CF spar tube and 4130/17-4 PH/7075 allowables verification remains open per
`TODO.md` §0.8)

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
    - [REF-FCC-004: 47 CFR Part 95 Subpart C — Radio Control Radio Service (RCRS) — Evaluated and Rejected for Commo's 49 MHz Link](#ref-fcc-004-47-cfr-part-95-subpart-c--radio-control-radio-service-rcrs--evaluated-and-rejected-for-commos-49-mhz-link)
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
    - [REF-SENSOR-004: TI MSPM0G3507 — Mixed-Signal MCU with CAN-FD Interface (SUPERSEDED)](#ref-sensor-004-ti-mspm0g3507--mixed-signal-mcu-with-can-fd-interface-superseded)
    - [REF-SENSOR-017: TI MSPM0G351x-Q1 — Automotive Mixed-Signal MCU with CAN-FD](#ref-sensor-017-ti-mspm0g351x-q1--automotive-mixed-signal-mcu-with-can-fd)
    - [REF-SENSOR-018: TI MSPM0 G-Series Design and Support Literature](#ref-sensor-018-ti-mspm0-g-series-design-and-support-literature)
    - [REF-SEC-002: Infineon OPTIGA TPM SLB 9672 — SPI TPM 2.0](#ref-sec-002-infineon-optiga-tpm-slb-9672--spi-tpm-20)
    - [REF-SENSOR-005: Microchip KSZ9477 — Ethernet Switch with HSR/PRP Hardware Redundancy](#ref-sensor-005-microchip-ksz9477--ethernet-switch-with-hsrprp-hardware-redundancy)
    - [REF-SENSOR-006: TI TCAN1042HG-Q1 — CAN-FD Transceiver](#ref-sensor-006-ti-tcan1042hg-q1--can-fd-transceiver)
    - [REF-SENSOR-008: AKM AK7455 — 14-bit Off-Axis Magnetic Rotation Angle Sensor](#ref-sensor-008-akm-ak7455--14-bit-off-axis-magnetic-rotation-angle-sensor)
    - [REF-SENSOR-009: TI ISOW1044BDFMR — 5 kVrms Isolated CAN-FD Transceiver with Integrated Isolated DC-DC](#ref-sensor-009-ti-isow1044bdfmr--5-kvrms-isolated-can-fd-transceiver-with-integrated-isolated-dc-dc)
    - [REF-SENSOR-010: TI ISOW1412 — 5 kVrms Isolated RS-485/RS-422 Transceiver with Integrated Isolated DC-DC](#ref-sensor-010-ti-isow1412--5-kvrms-isolated-rs-485rs-422-transceiver-with-integrated-isolated-dc-dc)
    - [REF-SENSOR-011: Infineon OPTIGA™ SLB 9672 — SPI TPM 2.0](#ref-sensor-011-infineon-optiga-slb-9672--spi-tpm-20)
    - [REF-SENSOR-012: STS3215 Digital Servo Motor — Cargo Winch Control (SUPERSEDED)](#ref-sensor-012-sts3215-serial-bus-servo--cargo-winch-drive-superseded)
    - [REF-SENSOR-013: SPT Servo SPT5425LV — 25 kgf·cm Analog/Digital PWM Servo (fleet-standard high-torque body)](#ref-sensor-013-spt-servo-spt5425lv--25-kgfcm-analogdigital-pwm-servo-fleet-standard-high-torque-body)
    - [REF-SENSOR-014: LibreServo v2 (stab-rabbit-coding fork) — Open-Source Smart-Servo Control Board](#ref-sensor-014-libreservo-v2-stab-rabbit-coding-fork--open-source-smart-servo-control-board)
    - [REF-SENSOR-015: OpenServoCore — Open-Source SG90/MG90-Class Smart-Servo Control Board](#ref-sensor-015-openservocore--open-source-sg90mg90-class-smart-servo-control-board)
    - [REF-SENSOR-016: Infineon OPTIGA™ Trust M — I2C Secure Element (planned, CAN-PERIPH-GW-1 + Flight Engineer only)](#ref-sensor-016-infineon-optiga-trust-m--i2c-secure-element-planned-can-periph-gw-1--flight-engineer-only)
    - [REF-SENSOR-019: SMB Bearings F688ZZ — 8x16x5 mm Flanged Miniature Radial Ball Bearing (wing-root tilt-spar bearing)](#ref-sensor-019-smb-bearings-f688zz--8x16x5-mm-flanged-miniature-radial-ball-bearing-wing-root-tilt-spar-bearing)
- [Part XIII — Telecommunications Standards](#part-xiii--telecommunications-standards)
    - [REF-TIA-001: ANSI/TIA-485-A — Electrical Characteristics of Generators and Receivers for Use in Balanced Digital Multipoint Systems (RS-485)](#ref-tia-001-ansitia-485-a--electrical-characteristics-of-generators-and-receivers-for-use-in-balanced-digital-multipoint-systems-rs-485)
- [Part XIV — Upstream CAD / Derivative-Source Attributions](#part-xiv--upstream-cad--derivative-source-attributions)
- [Part XV — Open Hardware / Software Licensing Standards](#part-xv--open-hardware--software-licensing-standards)
    - [REF-LIC-001: CERN Open Hardware Licence Version 2 — Weakly Reciprocal (CERN-OHL-W 2.0)](#ref-lic-001-cern-open-hardware-licence-version-2--weakly-reciprocal-cern-ohl-w-20)
    - [REF-LIC-002: OSHWA Open Source Hardware Certification](#ref-lic-002-oshwa-open-source-hardware-certification)
- [Removed / Superseded Citations](#removed--superseded-citations)
- [Open Standards Verification Items](#open-standards-verification-items)

---

## Creative-Universe Attribution and Fan-Engineering Terms

This catalog is the standards/regulatory index; it is **not** the project's licensing document.
The authoritative, full attribution chain — original creators, cast/crew, upstream CAD authors,
and third-party software licenses — is
[`current-specification/LICENSE_AND_ATTRIBUTION.md`](current-specification/LICENSE_AND_ATTRIBUTION.md);
the project's dual-license policy and subsystem federation map is
[`docs/attribution_and_licensing.md`](docs/attribution_and_licensing.md). This section is a
**summary with cross-references**, recorded here so that the creative-universe rights holders — never
previously named in this file — are acknowledged wherever this catalog is read.

### Project license (this work)

All original work in this repository is © 2025 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP,
**dual-licensed** (corrected 2026-08-01 — see "Removed / Superseded Citations"):

- **Hardware/CAD/PCB design** (airframe SCAD/STL/FCStd, KiCad schematics/PCB/Gerbers, mechanical
  drawings) — **CERN Open Hardware Licence Version 2 — Weakly Reciprocal (CERN-OHL-W 2.0)**
  [REF-LIC-001]. Full terms: root [`LICENSE`](LICENSE).
- **Documentation, code, scripts, and non-hardware drawings** — **Creative Commons
  Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)** —
  <https://creativecommons.org/licenses/by-sa/4.0/>. Full terms: `LICENSES/CC-BY-SA 4.0`.

You may share and adapt either under its own terms, including commercially, with appropriate
credit, a link to the license, and an indication of changes; attribution must not imply
endorsement by the licensor or by any rights holder named below. See
[`docs/attribution_and_licensing.md`](docs/attribution_and_licensing.md) for the full split and
the per-subsystem `LICENSE` federation.

### *Firefly* / *Serenity* creative universe (underlying IP)

The hull form and visual identity of this UAV draw **visual inspiration** from the Firefly-class
transport ship *Serenity*. The eight-node avionics bay names (Shepherd's Room, Inara's Shuttle,
River's Room, Simon's Medbay) are drawn from the same characters. The six board role names
(Skipper, Pilot, XO, Flight Engineer, Commo, Observer) were originally drawn from the same
characters too, but were renamed 2026-08-01 to generic role names — see `AGENTS.md` §9 "Naming
history" — specifically to avoid using character names as commercial hardware identifiers; the
bay names were not part of that rename. The ship design, characters, and all associated
intellectual property remain the trademarks and copyrights of their respective rights holders:

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
Serenity's silhouette and reuses character names for the four avionics bay identifiers only
(the six board names were moved off character names 2026-08-01). It does **not**:

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
aft white); controlled by FC4 node (Simon's medbay, Bay D).

**Used in:** `graphical-build-guide/build_guide_13_nav_lights.svg`, `docs/REVN_BUILD_GUIDE_24IN.md`,
`README.md`, `TODO.md`, `AGENTS.md`

---

### REF-FAA-004: 14 CFR Part 23 — Airworthiness Standards: Normal Category Airplanes

| Field | Value |
|---|---|
| **Issuing authority** | U.S. Federal Aviation Administration (FAA), Department of Transportation |
| **Current edition** | Part 23 as restructured by Amdt. 23-64 (effective 2017-08-30), performance-based; as amended through the 2024 annual CFR edition |
| **Official URL** | <https://www.ecfr.gov/current/title-14/chapter-I/subchapter-C/part-23> |
| **Verified source** | Section text quoted below was retrieved and verified verbatim 2026-08-29 from GovInfo's authoritative CFR XML — <https://www.govinfo.gov/content/pkg/CFR-2024-title14-vol1/xml/CFR-2024-title14-vol1-sec23-2230.xml> and <https://www.govinfo.gov/content/pkg/CFR-2024-title14-vol1/xml/CFR-2024-title14-vol1-sec23-2265.xml>. (eCFR's HTML endpoint bot-blocks automated retrieval; GovInfo serves the same authority.) |
| **Applicability caveat** | Part 23 governs **manned** normal-category airplanes. Serenity is an sUAS operated under Part 107 [REF-FAA-002], which imposes **no** structural certification basis. Part 23 is cited here as an **adopted engineering baseline**, exactly as `docs/structural_analysis.md` §3 already frames it — **NOT as a compliance claim.** |

**Sections applied in this project:**

| Section | Title | Applied where |
|---|---|---|
| **§ 23.2230** | *Limit and ultimate loads* | The 1.5× ultimate/limit factor used throughout `docs/structural_analysis.md` §3 and `tools/wing_spar_carrythrough.py` |
| **§ 23.2265** | *Special factors of safety* | Justifies an additional factor on FDM-printed structure — see below |

**§ 23.2230 (verbatim, GovInfo 2024 CFR):** the applicant must determine —
(a) *"The limit loads, which are equal to the structural design loads unless
otherwise specified elsewhere in this part"*; and (b) *"The ultimate loads,
which are equal to the limit loads multiplied by a 1.5 factor of safety unless
otherwise specified elsewhere in this part."*

**§ 23.2265 (verbatim, GovInfo 2024 CFR):** (a) *"The applicant must determine a
special factor of safety for each critical design value for each part, article,
or assembly for which that critical design value is uncertain, and for each
part, article, or assembly that is —"* … (a)(2) *"Subject to appreciable
variability because of uncertainties in manufacturing processes or inspection
methods."* (c) *"The applicant must multiply the highest pertinent special
factor of safety in the design for each part of the structure by each limit and
ultimate load…"*

**Why §23.2265 matters here.** Serenity's primary structure is FDM-printed
CF-PETG. Layer adhesion, raster orientation, moisture uptake, and
machine-to-machine variation are precisely the *"appreciable variability because
of uncertainties in manufacturing processes"* that (a)(2) contemplates. This is
the regulatory hook for the FOS 4.0 joint target that `docs/structural_analysis.md`
§3 currently describes only as *"a design-team judgment value"* — the judgment
is sound and now has a citable basis, though the specific numeric value remains
the project's own choice rather than anything Part 23 prescribes.

**CORRECTION THIS ENTRY MAKES — stale section number.**
`docs/structural_analysis.md` cited **"14 CFR Part 23.303"** in two places. That
section belonged to the **pre-2017** Part 23 and does not exist in the current
rule; the 2017 restructure moved the limit/ultimate relationship to **§23.2230**.
This is the same class of defect this file already recorded for §23.1401 (see
"Removed / Superseded Citations"). Both occurrences corrected 2026-08-29.

**Also worth recording, to prevent a future fabrication:** the load factors
**+3.8 / −1.52**, widely quoted as "the Part 23 load factors," appear **nowhere
in the current rule** — they belong to the pre-2017 §23.337. Current §23.2200(b)
requires only *"design maneuvering load factors not less than those, which
service history shows, may occur within the structural design envelope."* This
project's 4 g limit factor is an adopted figure under that framing, not a
regulatory quotation. Do not cite +3.8/−1.52 to current Part 23.

**Used in:** `docs/structural_analysis.md` §2, §3;
`docs/WING_ATTACH_INTERFACE.md` §2.1; `tools/wing_spar_carrythrough.py`

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

**Used in:** `gcs/skipper/hardware/docs/skipper_antenna_spec.md`, `TODO.md`, `AGENTS.md`,
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

**Used in:** `gcs/skipper/hardware/docs/skipper_antenna_spec.md`, `TODO.md`, `AGENTS.md`

---

### REF-FCC-003: 47 CFR Part 15 §15.235 — Operation Within the Band 49.82–49.90 MHz

| Field | Value |
|---|---|
| **Issuing authority** | FCC |
| **Official URL** | <https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-C/section-15.235> |

> **Correction (2026-06-20):** Earlier project revisions cited the Commo 49 MHz link against
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

**Applied to:** Commo (XCVR-49MHZ-2) 49 MHz AX.25 link; River's Room and Simon's Medbay nodes only.
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
systems, field disturbance sensors) — Commo is neither, so no exemption applies. Per
`gcs/skipper/hardware/docs/skipper_wiring.md`, Commo's RF port previously used a standard SMA
connector (Amphenol 132289) on both the aircraft and Skipper GCS sub-modules — **this was a
confirmed §15.203 violation**. **Resolution (2026-06-20):** J2 is now specified as Amphenol
**132289RP**, the reverse-polarity (RP-SMA) counterpart of 132289 — same PCB footprint, reversed
mating-pin gender, mechanically incompatible with generic commercial SMA antennas/cables, which
satisfies §15.203's "unique coupling" provision. Updated in `avionics/kicad/Commo.kicad_sch`,
`avionics/kicad/Commo.kicad_pcb`, `avionics/kicad/Commo.md`,
`gcs/skipper/hardware/docs/skipper_wiring.md`, and
`gcs/skipper/hardware/docs/skipper_antenna_spec.md`. See TODO.md §0.1 — remaining step is the
physical board re-spin/fabrication run to populate 132289RP in place of 132289; the design-level
fix is complete.

**Used in:** `gcs/skipper/hardware/docs/skipper_antenna_spec.md`,
`avionics/firmware/dts/cape-b/k3-am6254-pocketbeagle2-serenity-cape-b2.dts`,
`README.md`, `TODO.md`, `AGENTS.md`, `docs/AVIONICS_PB2_REDESIGN.md`

---

### REF-FCC-004: 47 CFR Part 95 Subpart C — Radio Control Radio Service (RCRS) — Evaluated and Rejected for Commo's 49 MHz Link

| Field | Value |
|---|---|
| **Issuing authority** | FCC |
| **Official URL** | <https://www.ecfr.gov/current/title-47/chapter-I/subchapter-D/part-95/subpart-C> |
| **Status** | **Not used in design.** Researched 2026-06-20 as a candidate replacement band/service for Commo's 49 MHz link (to recover the power/range budget §15.235 does not permit — see REF-FCC-003 and TODO.md §0.1) and rejected. Retained here per the Standards Vetting Policy so the rejection is auditable and is not re-investigated from scratch in a future session. |

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
| Licensing | Operated without an individual license ("licensed by rule"), but the equipment itself requires Part 95-specific FCC certification, separate from the Part 15 §2.803/§15.19 process REF-FCC-003 already requires for Commo | §95.305 |

**Findings — why RCRS does not apply to Commo:**

1. **No 78 MHz allocation exists.** §95.763 defines only the 26–28 MHz, 72 MHz, and 75 MHz channel plans; there is no 78 MHz RCRS band in 47 CFR Part 95 at any subpart.
2. **Aircraft/surface split forecloses 75 MHz.** Serenity is an aircraft. §95.763(c) restricts 75 MHz channels to model *surface* craft by rule; only the 72 MHz band (§95.763(b)) is available to an aircraft under RCRS.
3. **§95.731 is disqualifying regardless of band or power.** Commo's payload is bidirectional
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
| §3.3 | Device Agent/Gateway-Based Deployment | TPM 2.0 attestation per node (SLB9672) as the device agent |
| §4 (entire) | Deployment Scenarios | Applied to the 8-node cooperative architecture with per-node key storage |

**Applied to:** Every message (internal CAN FD/RS-485/1553/Ethernet and external SiK/LoRa/WiFi/49 MHz)
carries a TPM-bound SHA-256 HMAC; TPM 2.0 (SLB9672) on all 8 nodes provides boot measurement
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

**Applied to:** 5 kV galvanic isolation on all inter-node buses; Faraday enclosure for Flight Engineer PDB;
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
| §4.4.2 | Protecting Log Data | Recommends measures preventing unauthorized modification, deletion, or access to logs; the ATF16V8BQL CPLD hardware write-block on each XO node implements this principle at the hardware layer |
| §4.1 | Log Generation | Every sensor reading, message, and camera frame logged to hardware-enforced non-executable microSD |

**Applied to:** ATF16V8BQL CPLD hardware write-block (SET at power-on, CLEAR only on hard power
cycle); hardware-enforced append-only non-executable log microSD on every XO node.

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
PE-68515 coupling transformer (1:1.41, 78 Ω); 78 Ω termination at CN1 (Bay A) and FC4 (Bay D).

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
| RE102 | Radiated Emissions, Electric Field | Limit C applies to all avionics subsystems; 100BASE-TX EMI suppressed via HX1188NL magnetics, CMCs, and TVS arrays on Pilot and XO |
| RS103 | Radiated Susceptibility, Electric Field | 200 V/m, 10 kHz–18 GHz; isolated buses + chassis-grounded Flight Engineer enclosure provide margin |
| CS101 | Conducted Susceptibility, Power Leads | 50 V, 30 Hz – 150 kHz; π-filter bulk caps on Flight Engineer BECs |
| CS114 | Conducted Susceptibility, Bulk Cable Injection | Curve 05; two-stage CM filter (CM1+CM2, > 80 dB at 10 MHz) + Y-caps to chassis |
| CE102 | Conducted Emissions, Power Leads | Limit B; CM1+CM2 input chokes + π-filter on each BEC |

**Applied to:** Pilot (Cape-A-2), XO (Cape-B-2), and Flight Engineer EMC compliance targets.  The
design environment (500 W/m², E ≈ 434 V/m) [REF-NIST-002 §6.2.5] exceeds all MIL-STD-461G
RS103 limits; compliance with 200 V/m RS103 is a design floor, not the design ceiling.  Full
MIL-STD-461G qualification testing is deferred pending airframe integration.

**Used in:** `avionics/kicad/Pilot.md`, `avionics/kicad/XO.md`, `avionics/kicad/FlightEngineer.md`,
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
ATA6561 CAN FD transceivers; 120 Ω bus termination at CN1 (Bay A) and FC4 (Bay D).

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
Observer board); required fan angle for a 3"×3" (76×76 mm) crosshair at 5 ft (1.5 m) is only
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

**Applied to:** bow sensor pod (nose, Observer board) crosshair laser. A 2"×2" (51×51 mm) crosshair
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

**Applied to:** TVS arrays (PRTR5V0U2X) at all JST-GH field connectors on Pilot and XO;
shielded Flight Engineer enclosure provides ESD isolation for PDB connectors.

**Used in:** `avionics/kicad/Pilot.md`, `avionics/kicad/XO.md`, `avionics/kicad/FlightEngineer.md`

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
(ISOW1044BDFMR, ADM2795EBRWZ) on Pilot and XO signal buses.

**Used in:** `avionics/kicad/Pilot.md`, `avionics/kicad/XO.md`

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
Level 3 ±2 kV CM surge on bus); SMBJ33CA TVS (D1) on Flight Engineer VBAT line; PRTR5V0U2X TVS
arrays at field connectors on Pilot and XO.

**Used in:** `avionics/kicad/Pilot.md`, `avionics/kicad/XO.md`, `avionics/kicad/FlightEngineer.md`

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

**Applied to:** All PCB designs (Pilot, XO, Flight Engineer, Commo, Observer, CAN-PERIPH-GW-1, ENC-NACELLE-1).

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

**Applied to:** PCB manufacturing accept/reject criteria during fabrication quality verification. All boards (Pilot, XO, Flight Engineer, Commo, Observer, CAN-PERIPH-GW-1, ENC-NACELLE-1) are fabricated by JLCPCB and inspected against IPC-A-600 standards prior to assembly.

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
| SR 4.2 | Use of Cryptography | TPM 2.0 (SLB9672) per node for key storage, attestation, and HMAC computation |
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

**Applied to:** The PACE-prioritized failover architecture across Pilot/XO avionics stacks
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

## Part X-A — Material Allowables and Property Data (Academic / Test Sources)

### REF-MAT-001: Batista, Lagomazzini, Ramirez-Peña & Vazquez-Martinez — "Mechanical and Tribological Performance of Carbon Fiber-Reinforced PETG for FFF Applications"

| Field | Value |
|---|---|
| **Authors** | Moises Batista, Jose Miguel Lagomazzini, Magdalena Ramirez-Peña (Univ. of Cadiz), Juan Manuel Vazquez-Martinez (Polytechnic School of Engineering of Algeciras) |
| **Publication** | *Applied Sciences* **2023**, 13(23), 12701 |
| **DOI / Official URL** | <https://doi.org/10.3390/app132312701> — MDPI open access, CC BY 4.0 (<https://creativecommons.org/licenses/by/4.0/>) |
| **Retrieved** | 2026-08-25, user-supplied PDF (`applsci-13-12701-v3.pdf`), cross-checked against the DOI landing page's abstract/citation |
| **Test method** | ASTM D638 (tensile, "bone-type" specimens) and ASTM D695 (compression, Ø12.70 × 25.40 mm cylinders); FFF-printed, 100% concentric infill, 0.15/0.25/0.35 mm layer height, 220/230/240 °C extrusion, 60 mm/s |
| **Material tested** | PETG-CF: **20% short (chopped) carbon fiber**-reinforced PETG filament (MÁSTONER, 1.75 mm), vs. unreinforced PETG baseline, both FFF/FDM printed |

**Measured properties (as published, this project's use):**

| Property | PETG-CF (20% short CF) | PETG (unreinforced) | Notes |
|---|---|---|---|
| Tensile strength | **39.23 N/mm² (MPa)** | 48.41 N/mm² (MPa) | Text Conclusions §4 — exact, not figure-read. CF **reduces** tensile strength (short-fiber pull-out/poor cohesion observed by SOM microscopy, Fig. 13b) |
| Tensile force at break | 834.052 N | 956.6 N | dog-bone cross-section per Fig. 2a |
| Elongation at break | 2.13% | 2.9% | |
| Compressive strength (max, ASTM D695) | **≈47–60 N/mm² (MPa)**, print-parameter dependent | ≈47–53 N/mm² (MPa) | Read from Fig. 16 bar chart (approximate — the paper states the qualitative result "reinforced material outperforming the non-reinforced material" in compression, `mid text §4, ¶3`, without restating an exact single MPa figure in prose; the range above is the visual envelope across the nine print-parameter combinations tested, not a single certified value) |

**What this study does NOT provide** (important for how it is used below): no bearing test (e.g., ASTM D953 pin-bearing-in-hole) and no interlaminar/interlayer shear or "fusion strength" test — only bulk tensile and bulk compressive coupons. It does not, by itself, satisfy the CF-PETG **bearing** allowable this repository has flagged as "requires verification" (`airframe/fuselage-mid/WBS.md` CARGO-03c) — bearing failure at a loaded hole is a distinct, generally more severe mode than bulk unnotched compressive strength, and no literature bearing-knockdown factor is asserted here (inventing one would violate root `AGENTS.md` §4). **Confirmed 2026-08-25 (full re-read, all 16 pages): the paper reports NO flexural test (no ASTM D790 or equivalent) and no orientation-specific data of its own** — its Introduction cites a THIRD-PARTY source (ref. [13] within the paper, not this paper's own data) for the general claim that "printing orientation significantly affects... elastic modulus and tensile strength" and that "longitudinal orientation results in greater stiffness," but Batista et al. themselves tested only ASTM D638 dog-bone tensile coupons (concentric 100% infill, load axis in-plane/XY, the FDM-strong direction) and ASTM D695 compression cylinders — do not cite this source for a flexural allowable or for a specific interlayer/Z-axis strength figure; neither exists in it. What it *does* provide: the first real, peer-reviewed, ASTM D695 bulk compressive figure for 20%-CF-reinforced PETG this repository has ever cited, replacing pure conjecture with a measured baseline an order of magnitude above the previous ≈5 MPa bond-limited placeholder (`docs/structural_analysis.md` §7.3), and (new use, `docs/structural_analysis.md` §6.2) the only citable bulk tensile figure for **unreinforced** PETG (48.41 MPa) this repo has, used there as a conservative bending-stress proxy for the rear skid arm — pending an actual flexural coupon and a stated print orientation, since a bending fiber-stress check is not the same test as bulk axial tension.

**Applied to:** `docs/structural_analysis.md` §7.3 (CF-PETG allowables) and the CARGO-03c CF-PETG bearing-allowable "requires verification" row below — as *context and a materially better bulk-compressive baseline*, not as a substitute for the bearing-specific coupon test that item still calls for.

**Used in:** `docs/structural_analysis.md` §7.3, `airframe/fuselage-mid/WBS.md` §1.1.1.2 CARGO-03c, this file's Open Standards Verification Items table (CF-PETG bearing allowable row)

### REF-SEMI-001: Toshiba — TPHR8504PL 40 V N-channel Power MOSFET datasheet

| Field | Value |
|---|---|
| **Manufacturer** | Toshiba Electronic Devices & Storage Corporation |
| **Document** | *TPHR8504PL — MOSFET Silicon N-channel MOS (U-MOS IX-H)*, datasheet, 2019-10-24 |
| **Local copy** | `Open-Secure-ESC/docs/datasheets/TPHR8504PL_datasheet_en_20191024.pdf` |
| **Official URL** | <https://toshiba.semicon-storage.com/ap-en/semiconductor/product/mosfets/detail.TPHR8504PL.html> — **REQUIRES VERIFICATION**: the local PDF is authoritative and was read directly; the product-page URL follows Toshiba's standard pattern but has not been fetched from the issuing body |
| **Retrieved** | 2026-09-06, from the local PDF via `pdftotext` |
| **Scope applied** | §5 Thermal Characteristics and the electrical characteristics table |

**Values used (read from the PDF, not quoted from memory):**

| Parameter | Symbol | Value | Where used |
|---|---|---|---|
| Channel-to-case thermal resistance (max, Tc = 25 °C) | `Rth(ch-c)` | **0.88 °C/W** | `tools/nacelle_esc_thermal.py` |
| Channel-to-ambient, glass-epoxy board (a) | `Rth(ch-a)` | **50 °C/W** | board-to-local-air term |
| Channel-to-ambient, glass-epoxy board (b) | `Rth(ch-a)` | 142 °C/W | bounding case, not used |
| Channel temperature, absolute maximum | `Tch` | **175 °C** | design limit derives from this |
| Drain-source on-resistance, typ / max (VGS = 10 V, ID = 50 A) | `RDS(on)` | **0.7 / 0.85 mΩ** | confirms the 1.75 W/FET figure |

The 0.7 mΩ typical reproduces Open-Secure-ESC's 6 × 1.75 W conduction figure
exactly at 50 A (`I²R` = 2500 × 0.0007). **The `max` 0.85 mΩ gives 2.13 W/FET,
and `RDS(on)` roughly doubles by 125 °C** — a positive feedback the steady-state
network in `nacelle_esc_thermal.py` does not model and which is stated there.

**Used in:** `tools/nacelle_esc_thermal.py`, `airframe/wings-nacelles/WBS.md`
§1.1.3.8

---

### REF-MAT-004: CF-PETG THERMAL CONDUCTIVITY — NO SOURCE EXISTS. DO NOT CITE A NUMBER.

**This entry exists to record an absence, and to stop the absence being filled
by a plausible-looking figure.**

| Field | Value |
|---|---|
| **Quantity** | Thermal conductivity `k` of 20 % chopped-carbon-fibre PETG, as printed by FFF |
| **Status** | **UNVERIFIED — no primary source in this repository or cited by it** |
| **What REF-MAT-002 does NOT contain** | It is a mechanical-properties study (ASTM D790 flexural, D695 compressive, E384 hardness, D1525 Vicat, D648 HDT). It publishes **no thermal conductivity**, and it is the only CF-PETG characterisation this project cites. |

**A figure of 0.25 W/m·K appeared in `airframe/wings-nacelles/WBS.md` on
2026-09-06 and was written as though established.** It was not: it was an
unsourced engineering estimate. It is retracted here and corrected in that file.

**What can honestly be said, pending a measurement:**

| | plausible band | reasoning |
|---|---|---|
| neat PETG | ~0.20 W/m·K | typical amorphous thermoplastic |
| 20 % CF, **through-plane** | ~0.25–0.45 W/m·K | short fibres align **in**-plane during extrusion, so the through-thickness gain over neat resin is small |
| 20 % CF, **in-plane** | ~0.5–1.0 W/m·K | along the fibre axis |
| FFF porosity | reduces both | inter-bead voids are series air gaps |

These are bounds for reasoning, **not a citation**, and no design decision may
rest on a single value from this table.

**How the open question was worked around rather than guessed.**
`tools/nacelle_esc_thermal.py` **sweeps** k from 0.15 to 1.20 W/m·K and shows the
conduction path to the stator sleeve fails at every point in the band — 28.98
K/W at the bottom, 8.52 K/W at the top, against a budget of about 4.6 K/W. The
decision is therefore insensitive to the missing datum. A measured value would
sharpen the numbers; it would not change the answer.

**To close this item:** either obtain a manufacturer datasheet for the specific
filament (3D Maker Engineering PETG-CF Pro Series — the product REF-MAT-002's
notes identify as the commercial 20 % CF material) that publishes thermal
conductivity, or measure a printed coupon per ASTM D5470 (through-plane, the
orientation that governs here) or ASTM E1225. Record the print orientation with
the value; without it the number is not usable.

**Tracked in:** `airframe/wings-nacelles/WBS.md` §1.1.3.8 open items

---

### REF-MAT-002: Ramachandran, Pandian, Ramamoorthi & Britto John — "Influence of Process Parameters on the Mechanical Properties of Carbon Fibre Reinforced PETG"

| Field | Value |
|---|---|
| **Authors** | Prabhakaran Ramachandran, Venkatesh Ramamoorthi, Jerold John Britto John (Ramco Institute of Technology, Rajapalayam, India); Pitchipoo Pandian (P.S.R. Engineering College, Sivakasi, India) |
| **Publication** | *Mechanics of Advanced Composite Structures* **2026**, 13(1) [Serial No. 27], 171–184, Semnan University Press |
| **DOI / Official URL** | <https://doi.org/10.22075/MACS.2025.36494.1791> — open access, CC BY 4.0 (<https://creativecommons.org/licenses/by/4.0/>) |
| **Retrieved** | 2026-08-25, user-supplied PDF, cross-checked against the DOI landing page |
| **Test method** | ASTM D695 (compression, cylindrical specimens), **ASTM D790 (three-point flexural)**, ASTM E384 (Shore D hardness), ASTM D1525 (Vicat softening), ASTM D648 (heat deflection); FFF-printed on a URU 3.0 printer, 0.1 mm layer height, 100% infill, 240°C nozzle / 85°C bed, 80 mm/s, ±45° raster |
| **Material tested** | Pure PETG vs. 10%/20%/30% short chopped-carbon-fiber PETG (M/s. Medsby Health Care Solutions & FlashForge filament), five specimens per composition |

**Measured properties, unreinforced PETG (this project's use — Table 4 of the paper):**

| Property | Value | Notes |
|---|---|---|
| **Flexural strength (ASTM D790)** | **54 N/mm² (MPa)** | Table 4, exact — this is a genuine three-point-bend test, not a tensile-strength proxy |
| **Flexural modulus (ASTM D790)** | **2.76 GPa** | Table 4, exact |
| Compressive strength (ASTM D695) | 53 MPa | Table 3 |
| Shore Hardness D | 71 | Table 5 |
| Heat deflection temperature | 67 °C | Table 7 |

**Measured properties, chopped-carbon-fiber PETG by fiber fraction (Table 4 of the
paper, ASTM D790 three-point flexural test — exact, not figure-read):**

| Material | Flexural strength (MPa) | Flexural modulus (GPa) | Notes |
|---|---|---|---|
| PETG (0% CF) | 54 | 2.76 | baseline, same row as above |
| **10% CF-PETG** | **43** | **5.15** | **Strength DROPS below plain PETG** at this fraction — the paper attributes this to poor fiber-matrix cohesion/wetting at low loading (short-fiber pull-out), consistent with the tensile-test finding in REF-MAT-001. Modulus still rises. **Do not treat "CF-PETG" as inherently stronger than plain PETG in flexure without a stated fiber fraction — 10% is a strength regression.** |
| **20% CF-PETG** | **77** | **6.67** | Strength recovers well above plain PETG; this is the fraction specified for Serenity's structural airframe skins (owner-directed 2026-08-25, see below) |
| 30% CF-PETG | 80 | 7.01 | Highest strength/modulus tested, but this exact fraction is a custom lab blend (Medsby Health Care Solutions & FlashForge filament, this paper's own test material) — not confirmed as an available commercial retail product; superseded as the airframe target by 20% CF-PETG once a real, explicitly-labeled 20%-CF commercial filament ("3D Maker Engineering" PETG-CF Pro Series) was verified to exist |

FEA cross-check (ANSYS Workbench, linear-elastic model, Table 11): simulated flexural yield strength for pure PETG = 50 MPa vs. the 54 MPa experimental figure above (7.4% error) — the paper's own validation, not independently re-verified here, but consistent enough to support citing the experimental figure with confidence.

**What this study does NOT provide:** no print-orientation-specific data (loading axis vs. layer-stack axis) — the paper's own conclusions section notes "anisotropic fibre orientation" as a source of nonlinearity in its compressive/flexural results but gives no interlayer (Z-axis) strength figure or orientation-dependent allowable. It also does not test any geometry resembling a thin-walled tube (only solid dog-bone/bar/cylinder coupons) — this figure is a bulk material property, not a structural-member allowable.

**Applied to:** `docs/structural_analysis.md` §6.4 (rear CF skid-rod nose-high re-derivation) — **replaces** the REF-MAT-001 tensile-strength-as-bending-proxy (48.41 MPa) used there initially with this source's direct ASTM D790 flexural strength (54 MPa), the correct test type for a bending failure mode. The print-orientation caveat from that section's original derivation stands unchanged — this source does not resolve it.

**Used in:** `docs/structural_analysis.md` §6.4

**Used in:** `airframe/README.md` §5.1

### REF-EDF-001: XFly-Model — Galaxy X5 50 mm 12-blade EDF, 6S, motor 2627-KV3200

| Field | Value |
|---|---|
| **Manufacturer** | XFly-Model |
| **Product** | EDF Ducted Fan XFly Galaxy X5, 50 mm, 12 blades, 6S, motor 2627-KV3200 |
| **Official URL** | <https://www.xfly-model.eu/en/edf-units/4833-edf-ducted-fan-xfly-galaxy-x5-xfly-model-50mm-12-blades-6s-motor-3200kv.html> |
| **Local archive** | `docs/references/EDF Ducted Fan XFly Galaxy X5 XFLY-Model 50mm 12 blades + 6S Motor 3200KV - Xfly-Model.html` (saved 2026-08-18) plus a page screenshot |
| **Retrieved** | 2026-08-18 (archived), re-read 2026-08-31 |

**Values used, as published:**

| quantity | value |
|---|---|
| motor | Brushless **2627-3200KV** outrunner |
| shaft diameter | **3 mm** |
| blades | **12** |
| internal (shroud) diameter | **50 mm** |
| static thrust | **1240 gf** @ 6S 22.2 V |
| max current / power | **38 A / 843 W** @ 6S |
| weight | **75 g** — combo EDF + lip + motor |
| connectors | **PK 3.5 mm** bullets |
| external diameter | published as "nc" — **not communicated** |
| max rotation speed | published as "nc" — **not communicated** |

**NOT published, and each is load-bearing somewhere in this repo:** the motor
mounting bolt circle, the motor's length, the motor-alone weight, and the wire
gauge. See REF-EDF-002 for what a vendor listing adds, and the open items in
`docs/plans/2026-08-26-001-nacelle-esc-intake-integration-plan.md`.

**Where it is applied:** the thrust budget throughout (`docs/structural_analysis.md`,
`AGENTS.md`), `airframe/openscad/nacelles/nacelle_pod_50mm_tandem.scad`
(`EDF_BORE_R`, EDF stations), `edf_stator_sleeve.scad`, `edf_aft_spider_sleeve.scad`,
`current-specification/bom_revS.csv` `EDF-50-6S`, and
`tools/nacelle_mass_cg.py`.

> The KV was confirmed by the repository owner on 2026-08-31 against this page:
> the motor is a **2627-KV3200**. One SCAD header had carried 2700KV.

---

### REF-EDF-002: Vendor listing image — XFly Galaxy X5 50 mm EDF dimensions and packing list

| Field | Value |
|---|---|
| **Type** | Vendor product-listing infographic (AliExpress marketplace listing) |
| **Image URL** | <https://ae-pic-a1.aliexpress-media.com/kf/Sbcaa665cfd9c4bbfbaabb2ceb99e0cc52.png> |
| **Listing URL** | <https://www.aliexpress.us/item/3256811751635162.html> — **cookie-gated; the listing page itself could not be retrieved.** The image above is directly fetchable and is what was read. |
| **Retrieved** | 2026-08-31 (image, 750 × 11 846 px) |
| **Provenance caveat** | A **marketplace listing, not a manufacturer datasheet.** It is used only where the manufacturer publishes nothing, and each value below records which panel it came from. The listing mixes the 3S / 4S / 6S variants of the same X5 airframe — the motor photographed in its Packing List panel is labelled **2627-KV4600**, which is the **4S** motor. The repository owner's assessment is that the dimensions and screw layout are common across the variants; that is recorded as an **owner assessment, not a manufacturer statement.** |

**Values used:**

| quantity | value | panel |
|---|---|---|
| fan / rotor diameter | **Ø50 mm** | "Product Size" drawing |
| shroud (housing) length | **38.6 mm** | "Product Size" drawing |
| overall length, incl. motor | **76 mm** | "Product Size" drawing |
| blade-tip to shell clearance | **0.4 mm** | body text |
| motor mounting screws | **4** identical, plus 1 longer spinner screw | "Packing List" photo |
| shroud motor hub | disc with 4 round holes alternating with 4 slots | "composite materials" photo |

**Where it is applied:**

- `edf_aft_spider_sleeve.scad` — the **4-screw** count is what shows the sleeve's
  three 120° arms cannot match the motor, flagged there as print-blocking.
- `edf_aft_spider_sleeve.scad` and `nacelle_pod_50mm_tandem.scad` post-print
  checks — the **0.4 mm** tip clearance against a 50 mm shroud ID is what sets
  the Ø50.0 +0.4/−0.0 bore tolerance now that the build discards the shroud and
  runs the rotor against printed plastic.

> **Still not published anywhere:** the **bolt-circle diameter** and the screw
> **thread size**. Both must be measured off a physical motor before the aft
> spider sleeve is printed for flight.

---

### REF-STD-GEAR-001: ISO 53:1998 — Cylindrical gears for general and heavy engineering — Standard basic rack tooth profile

| Field | Value |
|---|---|
| **Designation** | ISO 53:1998 |
| **Full title** | *Cylindrical gears for general and heavy engineering — Standard basic rack tooth profile* |
| **Issuing body** | International Organization for Standardization (ISO), Technical Committee ISO/TC 60 (Gears) |
| **Official access** | ISO catalogue, <https://www.iso.org/standards.html> — **DIRECT CATALOGUE URL REQUIRES VERIFICATION** (see below) |
| **Retrieved** | not retrieved — cited by designation only |
| **Scope applied** | The standard basic rack proportions used to generate the nacelle tilt ring gear: pressure angle α = 20°, addendum h_a = 1.00 × m, dedendum h_f = 1.25 × m. |

**Where it is applied**

- `airframe/openscad/nacelles/nacelle_trunnion.scad` — `GEAR_PA = 20.0`,
  tip radius `GEAR_RA = PD/2 + m`, root radius `GEAR_RF = PD/2 − 1.25·m`, and the
  involute flank generated from `inv(α) = tan α − α`.
- `tools/nacelle_trunnion_fit.py` — gate T5, which checks the resulting pitch
  diameter, ratio and centre distance against `docs/WING_ATTACH_INTERFACE.md`
  WA-R8.
- `airframe/blender-scripts/merge_cargo_interior.py` — the fuselage-end 38T/38T
  stage uses the same module and the same proportions.

> **REQUIRES VERIFICATION (`docs/WBS.md` §0.8).** The designation, title, issuing body and
> the three numeric proportions above are the well-established profile-A basic
> rack and are used as such throughout the mechanical-design literature. What is
> **not** verified here is the direct ISO catalogue URL and the specific clause
> number within ISO 53:1998 that states them. Neither has been fetched from the
> issuing body, so neither is asserted. Per `CLAUDE.md` Standards Vetting Policy,
> a guessed catalogue number or clause reference would be a fabricated citation;
> the entry is therefore recorded at the level that *is* verifiable and flagged
> at the level that is not. Resolve before the gear is released for fabrication.

---

### REF-MATH-001: Melissen, J.B.M. — "Packing and Covering with Circles"

| Field | Value |
|---|---|
| **Author** | Johannes Bernardus Marinus Melissen, Utrecht University |
| **Publication** | PhD thesis, Universiteit Utrecht, 1997 |
| **Official URL** | <https://dspace.library.uu.nl/handle/1874/25091> — Utrecht University Repository, open access |
| **Retrieved** | 2026-08-29 |
| **Scope applied** | The proven-optimal ratios for packing *n* equal circles inside the smallest enclosing circle, for *n* ≤ 7. Only these small-*n* cases are used; they are proven optimal in this source and are reproduced throughout the standard circle-packing literature. |

**Values used (enclosing diameter ÷ single-circle diameter):**

| *n* | Ratio K(*n*) | Closed form |
|---|---|---|
| 1 | 1.00000 | 1 |
| 2 | 2.00000 | 2 |
| 3 | 2.15470 | 1 + 2/√3 |
| 4 | **2.41421** | **1 + √2** |
| 5 | 2.70130 | 1 + √(2(1 + 1/√5)) |
| 6 | 3.00000 | 3 |
| 7 | 3.00000 | 3 (hexagonal + centre) |

**Why this is catalogued rather than treated as common knowledge:** the *n* = 4
case decided a load-bearing geometry change. Two independent sources — the
owner's `docs/plans/2026-08-27-nacelle-wiring-plan.md` and the external Gemini
conversation it derived from — both specified an 11.0 mm spar bore for four
10 AWG conductors. Four Ø5.5 mm circles circumscribe **13.28 mm** at zero
clearance, so 11.0 mm does not fit at all, and the error propagated because the
constant was carried in prose rather than computed. It is now computed, from
this table, in `tools/spar_bundle_fit.py`, which refuses to interpolate for any
*n* outside the tabulated set.

**Caveat on the input, not the ratio:** the ratio is exact; the 5.5 mm wire OD
it is applied to is **not** a verified figure. `current-specification/bom_revS.csv`
records no outside diameter for `WIRE-10AWG`. See `tools/spar_bundle_fit.py`,
which prints that caveat on every run.

**Used in:** `tools/spar_bundle_fit.py`;
`airframe/openscad/wings/wings_s1223_revo.scad` (`SPAR_BORE_OD` derivation);
`docs/WING_ATTACH_INTERFACE.md` §2

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

**Status: SUPERSEDED 2026-07-03.** Replaced by the Observer board's TI AM62Ax digital vision SoC
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
| Mount hole pattern | 4× M2 on 14×14 mm pitch (±7 mm from lens center) | Industry-standard 19 mm Nano mount |
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

**Applied to:** `avionics/kicad/Commo.kicad_pcb` footprint "LoRa" (HOPERF_RFM9XW_SMD,
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

**Used in:** `avionics/kicad/Commo.kicad_pcb`, `avionics/kicad/Commo.md`, `TODO.md`

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
Pilot (Cape-A-2) UART2 port; I2C available as fallback per Zero Trust data-path
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

**Applied to:** Observer board vision half (nose bow sensor pod and cargo bay nadir FPV mount) —
see `avionics/AGENTS.md` "Observer — Cargo-Handling System and Nose/Cargo-Bay Vision, ToF & Laser Board". **Open item:** the
484-ball FCBGA package is a substantial escalation in assembly difficulty versus the discrete
components elsewhere in this design; PCB fabrication/assembly house capability for this
package must be confirmed before board layout (tracked in TODO.md §1.2c).

**Used in:** `avionics/AGENTS.md`, `TODO.md`

---

### REF-SENSOR-004: TI MSPM0G3507 — Mixed-Signal MCU with CAN-FD Interface (SUPERSEDED)

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

> **Superseded 2026-08-03 by REF-SENSOR-017 (MSPM0G351x-Q1)** on all three trust-module
> boards. Retained here because the clean-room RGZ-48 symbol geometry used by the
> MSPM0G3519-Q1 symbol was originally derived from this part's datasheet (SLASEX6C).

**Applied to:** Observer board control half — reads Benewake TFmini-S (REF-SENSOR-002) over UART,
drives the location-specific crosshair laser GPIO, and republishes signed sensor data over
both the Ethernet ring (via REF-SENSOR-005) and the CAN-FD trunk (via REF-SENSOR-006).
Selected specifically for its native MCAN peripheral and shared TI toolchain with the
PocketBeagle 2 Industrial's AM6254 real-time domain — avoids the software-PIO CAN-FD
synthesis that a non-TI MCU (e.g. RP2350) would require.

**Used in:** `avionics/AGENTS.md`, `TODO.md`

---

### REF-SENSOR-017: TI MSPM0G351x-Q1 — Automotive Mixed-Signal MCU with CAN-FD

| Field | Value |
|---|---|
| **Manufacturer** | Texas Instruments |
| **Product** | MSPM0G3519-Q1 / MSPM0G3518-Q1 (MSPM0G351x-Q1 family) |
| **Official product page** | <https://www.ti.com/product/MSPM0G3519-Q1>, <https://www.ti.com/product/MSPM0G3518-Q1> |
| **Datasheet** | SLASFA6B, *MSPM0G351x-Q1 Automotive Mixed-Signal Microcontrollers With CAN-FD Interface*, Nov 2024, rev. Oct 2025 |
| **Datasheet URL** | <https://www.ti.com/lit/ds/symlink/mspm0g3519-q1.pdf> |
| **Local copy** | `avionics/datasheets/mspm0g3518-q1.pdf` |
| **Lifecycle status** | ACTIVE / PRODUCTION DATA |

**Specifications applied in this design:**

| Parameter | Value | Source |
|---|---|---|
| Core | Arm Cortex-M0+ @ 80 MHz | SLASFA6B §1 Features |
| Qualification | AEC-Q100 Grade 1, −40 °C to +125 °C | SLASFA6B §1 Features |
| Flash / SRAM | MSPM0G3519-Q1 512 KB / 128 KB; MSPM0G3518-Q1 256 KB / 128 KB | SLASFA6B ordering table |
| CAN-FD instances | 1 in the 48-pin and 32-pin packages (2 in 64/80/100-pin) | SLASFA6B ordering table |
| Orderable, 48-pin RGZ VQFN 7×7 mm | `M0G3519QRGZRQ1` | SLASFA6B ordering table + §10.2 nomenclature |
| Orderable, 32-pin RHB VQFN 5×5 mm | `M0G3518QRHBRQ1` | SLASFA6B ordering table + §10.2 nomenclature |
| RGZ-48 pin map | Verified identical, pad for pad, to the MSPM0G350x/-Q1 RGZ-48 | SLASFA6B Fig 6-5 vs SLASEX6C/SLASF88C Fig 6-4 |
| RHB-32 bonded ports | PA0–PA27 only, plus NRST/VDD/VSS/VCORE and the exposed pad; **no PBx port is available** | SLASFA6B Fig 6-6 |
| CAN pins | `CAN0_TX` PA12, `CAN0_RX` PA13, **IOMUX PF12** | SLASFA6B Table 6-2 |
| SPI1 chip select on PA15 | `SPI1_CS2` (PF3); this family does not offer `SPI1_CS0` on PA15 | SLASFA6B Table 6-2 |
| UART on PB15/PB16 | `UART7_TX`/`UART7_RX` (PF2); this family does not offer UART2 there | SLASFA6B Table 6-2 |
| C(VDD) / C(VCORE) | 10 µF / 470 nF, ±20 % or better, low-ESR, close to the pins | SLASFA6B recommended operating conditions |
| Package outline, RGZ-48 | RGZ0048F, exposed thermal pad **4.1 mm × 4.1 mm** | SLASFA6B land pattern 4229427/A |
| Package outline, RHB-32 | RHB0032T, exposed thermal pad **3.45 mm × 3.45 mm** | SLASFA6B land pattern 4224744/A |

**Applied to:** the trust-module MCU on all three trust-module boards, superseding
REF-SENSOR-004 (MSPM0G3507) at the 2026-08-03 retarget — `MSPM0G3519-Q1` in RGZ-48 on Jayne,
`MSPM0G3518-Q1` in RHB-32 on `CAN-PERIPH-GW-1` and Kaylee.

**Used in:** `avionics/kicad/symbols/MSPM0G3519_Q1_RGZ.kicad_sym`,
`avionics/kicad/symbols/MSPM0G3518_Q1_RHB.kicad_sym`,
`avionics/kicad/retarget_mspm0g351x_slb9672.py`, `avionics/kicad/Observer/Observer.md`,
`avionics/kicad/FlightEngineer/FlightEngineer.md`, `avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md`, `TODO.md`

---

### REF-SENSOR-018: TI MSPM0 G-Series Design and Support Literature

| Field | Value |
|---|---|
| **Manufacturer** | Texas Instruments |
| **Documents** | SLAAE76E, SLAAET8A, SLAAE29A, SLAU846E, SLAZ742G |
| **Local copies** | `avionics/datasheets/slaae76e.pdf`, `slaaet8a.pdf`, `slaae29a.pdf`, `slau846e.pdf`, `slaz742g.pdf` |

| Designation | Title | URL | Sections applied |
|---|---|---|---|
| SLAAE76E | *MSPM0 G-Series MCUs Hardware Development Guide* (rev. E, Apr 2026) | <https://www.ti.com/lit/an/slaae76e/slaae76e.pdf> | §1 Table 1-1 hardware design check list; §2.4 decoupling; §3 reset; §8.5 open-drain I/O; §9 layout |
| SLAAET8A | *EMC Improvement Guide for MSPM0* (rev. A) | <https://www.ti.com/lit/an/slaaet8a/slaaet8a.pdf> | EMC design practice for the nacelle-bay EMI environment |
| SLAAE29A | *Cybersecurity Enablers in MSPM0 MCUs* (rev. A) | <https://www.ti.com/lit/an/slaae29a/slaae29a.pdf> | Secure boot and secure storage, paired with the SLB 9672 TPM |
| SLAU846E | *MSPM0 G-Series 80-MHz Microcontrollers Technical Reference Manual* (rev. E, Jul 2026) | <https://www.ti.com/lit/ug/slau846e/slau846e.pdf> | Peripheral programming model for §4.6 firmware |
| SLAZ742G | *MSPM0G3x0x, MSPM0G1x0x, MSPM0G3x0x-Q1 Microcontrollers Errata* (rev. G, Jul 2026) | <https://www.ti.com/lit/er/slaz742g/slaz742g.pdf> | Silicon advisories |

**Requires verification:** SLAZ742G covers the MSPM0G3x0x/G1x0x families and their -Q1
variants. It does **not** enumerate the MSPM0G351x-Q1 parts adopted on 2026-08-03, and the
TRM SLAU846E contains no occurrence of "MSPM0G3518"/"MSPM0G3519". The MSPM0G351x-Q1 errata
and TRM applicability must be confirmed against TI before firmware sign-off — see TODO.md
§1.2d.

**Applied to:** MCU support-circuit design review for all three trust-module boards.

**Used in:** `avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md`, `TODO.md`

---

### REF-SEC-002: Infineon OPTIGA TPM SLB 9672 — SPI TPM 2.0

| Field | Value |
|---|---|
| **Manufacturer** | Infineon Technologies |
| **Product** | SLB 9672AU2.0 FW16.xx (OPTIGA TPM 2.0) |
| **Datasheet** | *OPTIGA TPM SLB9672 TPM 2.0 FW16.xx Datasheet*, rev. 1.3, 2024-11-18 |
| **Datasheet URL** | <https://www.infineon.com/assets/row/public/documents/30/49/infineon-slb9672-tpm20-spi-fw16.xx-ds-rev1-3-2024-11-18-datasheet-en.pdf> |
| **Local copy** | `avionics/datasheets/slb9672.pdf` |

**Specifications applied in this design:**

| Parameter | Value | Source |
|---|---|---|
| Interface | SPI, mode 0 only, up to 33 MHz | Rev 1.3 §3.1.1, Table 11 |
| Package | PG-UQFN-32-1,-2, 5 × 5 mm | Rev 1.3 §2.1 |
| Temperature range | SLB 9672AU2.0 extended, −40 °C to +105 °C (XU2.0 is −40 to +85 °C) | Rev 1.3 ordering information |
| SPI pins | CS# 20, SCLK 19, MOSI 21, MISO 24, PIRQ# 18, RST# 17 | Rev 1.3 Table 11 |
| Supply pins | VDD 1, 14, 22; GND 2, 9, 23, 32 | Rev 1.3 Table 12 |
| TCG-compatibility pins | Pin 8 NCI/VDD and pin 16 NCI/GND — connect to VDD/GND respectively | Rev 1.3 Table 13 |
| Exposed pad | Internally connected to GND; **must also be connected to GND externally** | Rev 1.3 §2.1.2 |
| Recommended land | 4.1 mm outline, exposed pad **3.6 mm × 3.6 mm** | Rev 1.3 Figure 3 |

**Compatibility with the superseded SLB9670VQ2.0:** every pin the Serenity boards connect —
the SPI group (17–24), VDD (1/8/14/22) and GND (2/9/16/23/32) — is identical between the two
parts. The differences are confined to pins 3, 4, 6 and 7 (GPIO_00/GPIO_01/NC/GPIO_02 on the
SLB 9672), all of which are left unconnected on all three Serenity boards.

**Applied to:** the trust-module TPM on Jayne, Kaylee and `CAN-PERIPH-GW-1`, superseding the
SLB9670VQ2.0 at the 2026-08-03 retarget. Not yet applied to Commo, Pilot or XO, which still
carry the SLB9670.

**Used in:** `avionics/kicad/symbols/Jayne_SLB9672_TPM.kicad_sym`,
`avionics/kicad/retarget_mspm0g351x_slb9672.py`, `TODO.md`

---

### REF-SENSOR-005: Microchip KSZ9477 — Ethernet Switch with HSR/PRP Hardware Redundancy

| Field | Value |
|---|---|
| **Manufacturer** | Microchip Technology Inc. |
| **Product** | KSZ9477 7-Port Gigabit Ethernet Switch |
| **Official product page** | <https://www.microchip.com/en-us/product/ksz9477> |
| **Application note** | AN3474 — "KSZ9477 High-Availability Seamless Redundancy" |
| **Note** | Selected specifically because it is confirmed (per AN3474) to hardware-offload HSR (High-availability Seamless Redundancy) and PRP (Parallel Redundancy Protocol) per IEC 62439-3 — HSR tag insertion, TX frame duplication, RX duplicate-frame discard. Two other Microchip switch parts (LAN9355, KSZ9563) were considered and **rejected** for this role: neither datasheet documents HSR/PRP/MRP hardware support; substituting either would leave the Ethernet ring without hardware-level redundancy and is not permitted for the ring-node role. |

**Applied to:** Observer board control half — Ethernet ring pass-through node (in/out via shielded
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

**Applied to:** Observer board control half — CAN-FD trunk transceiver, MSPM0G3507 MCAN peripheral
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
| **Note** | Selected for the wing/nacelle tilt-angle encoder (`SKIPPER-TILT-ENC-PCB`) because it explicitly supports the **Off-Axis (side-of-shaft)** configuration required by the through-shaft tilt-spar, and adds anomaly-magnetic-field detection + dynamic error reduction + EEPROM INL calibration — suited to the ferromagnetic (4130/17-4 PH) spar. Supersedes the on-axis MT6701 (rejected) and AS5600 (Rev Q). |

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

**Applied to:** wing-tip tilt-angle encoder board `SKIPPER-TILT-ENC-PCB` — off-axis read of the
rotating ring magnet (`HALL-RING-MAG`) on the tilt-spar hub. Off-axis flux (10–70 mT) at
the IC and the EEPROM INL calibration are **bench-verification** items (AKM app support);
ERROR-pin push-pull-vs-open-drain and the QFN24 EP dimensions are layout-verification items.

**Used in:** `avionics/kicad/ENC-NACELLE-1.kicad_sch`, `avionics/kicad/ENC-NACELLE-1.md`,
`current-specification/bom_revS.csv` (`SKIPPER-TILT-ENC-PCB`),
`airframe/wings-nacelles/WBS.md` §1.1.3.6, `avionics/WBS.md` §1.9.1

---

### REF-SENSOR-009: TI ISOW1044BDFMR — 5 kVrms Isolated CAN-FD Transceiver with Integrated Isolated DC-DC

| Field | Value |
|---|---|
| **Manufacturer** | Texas Instruments |
| **Product** | ISOW1044BDFMR |
| **Datasheet** | SLLSFF7A, archived at `avionics/datasheets/isow1044.pdf` |
| **Package** | 20-pin DFM (SOIC-20W compatible), `Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm` |
| **Note** | Combines galvanic signal isolation + an integrated isolated DC-DC converter in one part (no external isolated supply needed for the bus side) — used for every isolated CAN-FD node this project builds. Clean-room symbol `Observer_MSPM0G3507_RGZ`/`Observer_ISOW1044BDFMR` built directly from datasheet Table 7-1, first on Observer, then reused verbatim on `CAN-PERIPH-GW-1` and FlightEngineer. |

**Used in:** `avionics/kicad/Observer/kicads/Observer.kicad_sch` (U4), `avionics/kicad/CAN-PERIPH-GW-1/` (U3 per stack), `avionics/kicad/FlightEngineer/kicads/FlightEngineer.kicad_sch` (U_ISOCAN), `avionics/kicad/Pilot/kicads/Pilot.kicad_sch`, `avionics/kicad/XO/kicads/XO.kicad_sch` (both fixed 2026-07-26, see Removed/Superseded Citations).

---

### REF-SENSOR-010: TI ISOW1412 — 5 kVrms Isolated RS-485/RS-422 Transceiver with Integrated Isolated DC-DC

| Field | Value |
|---|---|
| **Manufacturer** | Texas Instruments |
| **Product** | ISOW1412 (500 kbps variant; ISOW1432 is the pin-compatible 12 Mbps variant, not used) |
| **Datasheet** | SLLSF86C, archived at `avionics/datasheets/isow1412.pdf` |
| **Package** | 20-pin DFM (SOIC-20W compatible), `Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm` |
| **Note** | Full-duplex part (separate Y/Z driver-out and A/B receiver-in pins); run in half-duplex mode on this project's 2-wire RS485_A/RS485_B multi-drop bus by shorting Y-to-A and Z-to-B, matching the standard technique for using a full-duplex transceiver as half-duplex. Selected 2026-07-26 to replace ADI ADM2795E fleet-wide (see Removed/Superseded Citations) because it integrates its own isolated DC-DC for the bus-side supply — ADM2795E is signal-only and needs a separate external isolated supply. Clean-room symbol built directly from datasheet Table 7-1 ("Pin Functions"). |

**Used in:** `avionics/kicad/CAN-PERIPH-GW-1/` (U4 per stack, `GW_ISOW1412`), `avionics/kicad/Observer/kicads/Observer.kicad_sch` (U6), `avionics/kicad/FlightEngineer/kicads/FlightEngineer.kicad_sch` (U_RS485), `avionics/kicad/Pilot/kicads/Pilot.kicad_sch`, `avionics/kicad/XO/kicads/XO.kicad_sch` (both fixed 2026-07-26, renamed from the broken inline "ADM2795EBRWZ" symbol).

---

### REF-SENSOR-011: Infineon OPTIGA™ SLB 9672 — SPI TPM 2.0

| Field | Value |
|---|---|
| **Manufacturer** | Infineon Technologies |
| **Product** | OPTIGA™ TPM SLB 9672 TPM 2.0 FW16.xx (SLB9672XU2.0 / SLB9672AU2.0) |
| **Datasheet** | Revision 1.3, 2024-11-18, archived at `avionics/datasheets/SLB_9672XU20_Infineon.pdf`, <https://www.infineon.com/assets/row/public/documents/30/49/infineon-slb9672-tpm20-spi-fw16.xx-ds-rev1-3-2024-11-18-datasheet-en.pdf> |
| **Product page** | <https://www.infineon.com/OPTIGA-TPM-SLB9672> |
| **Package** | PG-UQFN-32-1,-2, `Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm` |
| **Note** | Fleet-standard TPM (root `AGENTS.md` §Security: "every Cape carries a TPM"). **Migrated from SLB9670 to SLB9672 (2026-08-01)** — same 5x5mm/0.5mm-pitch/32-pin QFN land pattern (both datasheets: 5x5mm body, 3.6x3.6mm exposed pad), so the existing `Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm` footprint was reused as-is; the GPIO/PP pin functions and which VDD/GND pins are mandatory vs optional differ (SLB9672 pins 1/14/22 are the three mandatory VDD pins, vs 8/22 on SLB9670; pin 6 is a true no-connect instead of a GPIO; pins 3/4/7 are GPIO_00/01/02 instead of NCI/NCI/PP) — see Removed/Superseded Citations for the old SLB9670VQ2.0/XQ2.0 entry. Clean-room symbol `SLB9672_TPM` built directly from datasheet Tables 11/12/13, first on Observer, reused verbatim on `CAN-PERIPH-GW-1`, Flight Engineer, and Commo. **Not** the same as the inline "SLB9672" symbol already embedded in Pilot.kicad_sch/XO.kicad_sch (renamed from "SLB9670" in the same migration, pin numbers unchanged), which was found (2026-07-26, not yet corrected) to have incorrect pin numbers relative to the datasheet — see Removed/Superseded Citations. |

**Used in:** `avionics/kicad/Observer/kicads/Observer.kicad_sch` (U5), `avionics/kicad/CAN-PERIPH-GW-1/` (U2 per stack), `avionics/kicad/FlightEngineer/kicads/FlightEngineer.kicad_sch` (U_TPM), `avionics/kicad/Commo/kicads/Commo.kicad_sch` (TPM), `avionics/kicad/Pilot/kicads/Pilot.kicad_sch`/`Pilot_rebuild.kicad_sch` (TPM), `avionics/kicad/XO/kicads/XO.kicad_sch` (TPM).

**Planned partial supersession (2026-08-06, not yet implemented — see REF-SENSOR-016).**
`CAN-PERIPH-GW-1` and Flight Engineer are slated to move from this SPI TPM to the
Infineon OPTIGA™ Trust M I2C secure element, at the user's direction, citing SLB9672's
comparatively slow TPM-2.0 startup/self-test sequence as a boot-latency concern for
those two boards specifically. **Neither board's `.kicad_sch`/`.kicad_pcb` has been
edited yet** — see REF-SENSOR-016 for why (datasheet/tooling access gate) and
`avionics/WBS.md` §1.9.2 for the open item. This entry (REF-SENSOR-011) remains
authoritative and unchanged for Observer, Commo, Pilot, and XO, which are **not** in
scope for this change and keep the SLB9672 (root `AGENTS.md` §1 "every Cape carries a
TPM" — Pilot/XO are the fleet's actual Capes; `CAN-PERIPH-GW-1` and Flight Engineer are
standalone boards, not Capes, so this substitution does not conflict with that
requirement).

---

### REF-SENSOR-012: STS3215 Serial-Bus Servo — Cargo Winch Drive (SUPERSEDED)

**Status: SUPERSEDED 2026-08-02.** Replaced fleet-wide by the SPT5425LV (REF-SENSOR-013)
running the LibreServo v2 control board (REF-SENSOR-014) — see "Servo Fleet Standardisation,
2026-08-02" below. The STS3215's own datasheet-verification gate (below) is now moot: it is
retained here per project revision policy (components are referenced as of their last active
revision even after superseding) and because it explains *why* the winch briefly specified a
TTL bus servo before the fleet-wide standardisation. Do not delete; do not cite as active.

> **⚠ REQUIRES VERIFICATION — MOOT (superseded, not pursued further).** The archived
> datasheet is a **scanned/CID-encoded PDF**, and no OCR toolchain is available in the current build
> environment (`pdftotext`, `tesseract`, `mutool`, `poppler-utils` absent; `pypdf` fails on a
> broken `cryptography` build). **No performance figure below is quoted from that datasheet.**
> Nothing in this entry may be cited as a verified value until the gaps are read off the
> document and this table is updated. Tracked in "Open Standards Verification Items" and in
> `docs/TODO.md` §0.x. **Moot as of the 2026-08-02 supersession — left unresolved
> deliberately; do not spend further effort clearing this gate.**

| Field | Value |
|---|---|
| **Part Number** | STS3215 (repo SKU 108090023, variant C001) |
| **Manufacturer** | ⚠ Not yet confirmed from the datasheet |
| **Datasheet** | `docs/references/108090023_STS3215-C001_Datasheet.pdf` — revision/date ⚠ not extracted |
| **Control Interface** | **TTL half-duplex serial bus, ID-addressable** — **not** 1000–2000 µs PWM. Lands on `CAN-PERIPH-GW-1` `J_FLEX` → `FLEX_TTL_GPIO`, documented there as covering "a TTL-level digital servo protocol (e.g. a serial-bus servo)". |
| **Operating Voltage** | Driven at 5.4 V nominal from Flight Engineer RAIL-2 `5V_OBS` (project-side decision, not a datasheet limit) |
| **Torque** | ⚠ Not verified. **Design requirement is ≥ 3.2 kgf·cm (0.31 N·m)** at the coupler — derived in `docs/CARGO_WINCH_SPECIFICATION.md` §4.2, must be checked against the real rating. |
| **Stall current** | ⚠ Not verified for SPT5425LV (the cargo-winch servo on RAIL-2, `docs/CARGO_WINCH_SPECIFICATION.md` §5.4). Budgeted at 1.2 A for the RAIL-2 sizing; if actual stall exceeds ~2.5 A, RAIL-2 must be resized. **Note (2026-08-23):** the *nacelle-tilt* servos (a separate load, on the 6 V servo bus, `docs/POWER_DISTRIBUTION.md` §3.3 — not RAIL-2) moved to DS3225, whose datasheet DOES publish stall current — **1.9 A @ 5 V, 2.3 A @ 6.8 V**. **Correction (2026-08-25, SPAR-02 re-derivation):** the "RAIL-2 sizing must be re-checked" language here previously conflated the tilt servo with the RAIL-2 winch servo; RAIL-2 itself carries only the winch servo and Observer boards and is unaffected by the DS3225 swap. The 6 V servo bus (§3.3) has been resized to 2.3 A/servo instead — see `docs/POWER_DISTRIBUTION.md` §3.3/§4. |
| **Mass** | ⚠ Not verified. **60 g assumed** in the mass/CG table (spec §6); this term dominates the +98.6 g net delta and the resulting T/W 1.613 → 1.557. |
| **Case envelope / boss pattern** | ⚠ Not verified. Blocks `make_winch_pedestal_port()` in `airframe/stls/fuselage/cargo/generate_cargo_mounts.py`. |
| **Application** | Cargo winch drive. Transmits **torque only** through a lost-motion dog coupler; the spool is carried on two MR84ZZ bearings on a fixed Ø4 mm axle clamped at both pedestals, so no radial load reaches the servo output. Paired with a normally-engaged one-way safety ratchet whose catch is retracted by a solenoid on the same gateway. Signed CAN-FD telemetry per [REF-NIST-001 §2.1]. |

**Supersedes:** the Rev P/Q/R `N20-WINCH` (N20 300RPM 6V gearmotor) and its cantilever mount
`cargo_winch_motor_mount.stl` + N20-bored `cargo_winch_spool.stl`.

**Used in:** `docs/CARGO_WINCH_SPECIFICATION.md` (Rev B, historical), `docs/bom_revR.json`
(`STS3215-WINCH`, historical), `airframe/stls/fuselage/cargo/generate_cargo_mounts.py`
(historical comment only).

**Status:** SUPERSEDED. Not cleared for procurement or STL generation under this REF-ID;
current work uses REF-SENSOR-013/014 instead.

---

### Servo Fleet Standardisation, 2026-08-02

The three high-torque servos on the airframe — 2× nacelle tilt (previously DS3218MG, no
REF-ID; standard COTS analog/digital PWM servo, uncited) and 1× cargo winch (previously
STS3215, REF-SENSOR-012 above) — are unified onto **one physical servo model
(SPT5425LV, REF-SENSOR-013) running one open-source control board (LibreServo v2,
REF-SENSOR-014)**, each with the servo's internal mechanical rotation-limiting pin
removed. This gives the fleet a single spare part across three previously-different
servo/board combinations, and gives every one of them the signed-serial-bus telemetry the
STS3215 winch conversion was chasing in the first place — without the STS3215's own
never-resolved datasheet-verification gate (REF-SENSOR-012 above), since the SPT5425LV's
envelope, torque and mass are all published COTS figures (REF-SENSOR-013). Separately, the
SG90 micro servos (cargo door, payload release; RCS bleed-valve servos are Phase 11
deferred) are standardised on **OpenServoCore** (REF-SENSOR-015), an SG90/MG90-class
open-source swap board — not LibreServo, whose smallest documented target is a
standard-size (40 mm class) servo, not the 23 mm SG90 body.

Per-application operating mode differs even though the hardware is now identical:

| Application | Qty | Mode | Range |
|---|---|---|---|
| Cargo winch | 1 | Continuous rotation, gateway closes position on the AK7455 spool encoder (REF-SENSOR-008) | Multi-turn, unbounded by the servo itself |
| Nacelle tilt | 2 | **CORRECTED Rev T1c (2026-08-30):** continuous rotation, Pilot closes position on the AK7455 nacelle encoder (REF-SENSOR-008) — the same pattern as the winch above | **Multi-turn** (1.438 rev of actuator per 145° of nacelle), unbounded by the servo itself. Soft-limited to −5°…140° *at the nacelle*, backstopped by CF-PETG hard stops in the external gear train |

> **The row above changed at Rev T1c and the change is structural, not editorial.**
> The tilt stage became a REDUCTION (tip 14T/50T, `i` = 3.571), so the drive shaft must
> turn **1.438 revolutions** over the 145° sweep and no limited-rotation servo can drive
> it at any horn radius. Removing the rotation pin is therefore **required** on the tilt
> servos now, not merely convenient — and the AK7455 became **load-bearing for control**
> rather than telemetry, because a multi-turn drive without absolute feedback does not
> know where the nacelle is. See `docs/WING_ATTACH_INTERFACE.md` §4.3b/§4.3c and
> `docs/TILT_DRIVE_CONTROL_SPEC.md`.

Removing the pin on the winch is a deliberate commonality choice; on the tilt servos it
is now a requirement (see the note above). It is not a requirement of the
position-mode applications generally: LibreServo replaces the servo's potentiometer with a 360°
absolute magnetic encoder (AEAT-8800, 16-bit), so position feedback and soft-limit
enforcement no longer depend on the mechanical stop the pin used to provide. See
REF-SENSOR-013/014/015 below for the individual part records, and
`docs/CARGO_WINCH_SPECIFICATION.md` §3.1/§3.9 (Rev C) for the winch-specific analysis.

---

### REF-SENSOR-013: SPT Servo SPT5425LV — 25 kgf·cm Analog/Digital PWM Servo (fleet-standard high-torque body)

| Field | Value |
|---|---|
| **Manufacturer** | Shantou SiPaiTe Electronic Technology Co., Ltd. ("SPT Servo") |
| **Product** | SPT5425LV (waterproof variant SPT5425LV-W also available; both share the servo-database listing's mechanical/electrical figures below) |
| **Manufacturer product page** | <http://www.spt-servo.com/Product/1027594540.html> |
| **Independent spec listing** | <https://servodatabase.com/servo/sptservo/spt5425lv> |
| **Stall torque** | 24 kgf·cm (2.35 N·m) @ 4.8 V; 26 kgf·cm (2.55 N·m) @ 6.0 V |
| **Operating speed** | 0.22 s/60° @ 4.8 V; 0.18 s/60° @ 6.0 V |
| **Operating voltage** | 4.8–6.0 V (native PWM servo rating; LibreServo v2 re-drives the motor from its own 4.5–18 V input, REF-SENSOR-014, so the servo's native voltage window is a motor-only figure once converted) |
| **Dimensions** | 40.5 × 20 × 40.5 mm |
| **Mass** | ~57 g |
| **Construction** | Metal gear train, 2× ball bearings |
| **⚠ Not yet independently verified** | Stall current draw (needed for the RAIL-2 budget, `docs/POWER_DISTRIBUTION.md` §3.2.1) is not published in either source above; carried forward as "requires verification" rather than assumed. |

**Why this part, not a bus servo:** SPT5425LV is a standard hobby PWM/analog servo body,
not a native serial-bus servo like the STS3215 it replaces. The serial-bus behavior comes
entirely from swapping its internal control PCB for LibreServo v2 (REF-SENSOR-014), which
is explicitly designed to convert "any standard servo motor" without modifying the
mechanical body or bottom cover. Selecting a standard-body servo (rather than staying on a
factory bus servo like the STS3215) is what makes a single physical part usable identically
for the nacelle-tilt position application (where DS3218MG-class bodies were already
qualified, §"Servo Fleet Standardisation" above) and the winch's continuous-rotation
application.

**Mechanical note — rotation-limiting pin.** Like most analog/digital hobby servos of this
class, the SPT5425LV output gear/potentiometer assembly includes a small internal
mechanical stop (a plastic pin/tab molded into the output gear and case) that limits shaft
travel to roughly one physical turn, matching the servo's stock potentiometer. This is the
"rotation blocking pin" removed during LibreServo conversion (REF-SENSOR-014): with the
stock potentiometer removed and replaced by LibreServo's 360° magnetic encoder, the pin's
sole function — protecting the potentiometer wiper from over-travel — no longer applies, and
removing it lets the output shaft rotate continuously. **⚠ Exact pin location/removal
procedure is not yet documented for this specific part number** — verify by teardown before
committing to the build guide (`graphical-build-guide/`); do not assume it matches a
different manufacturer's servo internals.

**Applied to:** cargo winch drive (replacing STS3215, REF-SENSOR-012), 2× nacelle tilt servo
(replacing uncited DS3218MG). See `docs/CARGO_WINCH_SPECIFICATION.md` §3.1 (Rev C),
`current-specification/bom_revS.json`/`.csv`, `airframe/openscad/nacelles/nacelle_servo_bracket.scad`.

**Used in:** `docs/CARGO_WINCH_SPECIFICATION.md`, `current-specification/bom_revS.json`,
`current-specification/bom_revS.csv`, `airframe/openscad/nacelles/nacelle_servo_bracket.scad`,
`airframe/stls/fuselage/cargo/generate_cargo_mounts.py`

---

### REF-SENSOR-014: LibreServo v2 (stab-rabbit-coding fork) — Open-Source Smart-Servo Control Board

| Field | Value |
|---|---|
| **Project** | LibreServo — "An Open source controller to convert any servo motor to the best smart servo" |
| **Fork used by this project** | <https://github.com/Stab-Rabbit-coding/LibreServo_v2> (adds isolated RS-485 + isolated CAN-FD + a TPM to the upstream design) |
| **Upstream project** | <https://www.libreservo.com/en> |
| **Hardware license** | CC BY-SA 4.0 — <https://creativecommons.org/licenses/by-sa/4.0/> |
| **Board revision (this fork)** | v2.3.1 (`PCB/LibreServo-v2.3.1.sch`/`.brd`) |
| **MCU (as-built v2.3.1)** | STM32F302K8U6, Cortex-M4 @ 72 MHz, 64 KB flash (the fork's own BOM lists it as "STM32F301K8U6" — a naming discrepancy the fork's own `PCB/RS485-CANFD-TPM-upgrade.md` flags and does not resolve; treat as F302 per the `.ioc` project config) |
| **Communications (as-built)** | RS-485 half-duplex, up to 9 Mbps, daisy-chained, CRC-16 |
| **Motor driver** | Up to 16 A continuous (WSD3069DN56 N+P MOSFET pair, v2.3+) |
| **Position sensor** | AEAT-8800 16-bit (65,536 count) magnetic encoder, 360°, replaces the servo's stock potentiometer — this is what makes continuous rotation and true absolute position both available on the same converted servo |
| **Current sensor** | ACS711, ±15 A |
| **Input voltage** | 4.5–18 V (recommended 5–14 V) |
| **Mechanical fit** | Explicitly "compatible with standard servo motors (no need to change the bottom cover of them!)" — a same-footprint swap for the servo's factory control PCB |
| **⚠ Fork upgrade status (isolated RS-485 / isolated CAN-FD / TPM)** | `PCB/RS485-CANFD-TPM-upgrade.md` in the fork records this as an **in-progress, schematic-only** change: MCU swap to STM32G431 (native FDCAN) + isolated RS-485 (ADM2587E) + isolated CAN-FD (ADM3055E) are wired in the EAGLE schematic netlist, but have **no footprints, no PCB placement, and no firmware port yet**; the TPM (Infineon SLB9672) is **explicitly out of scope of that pass** — "not part of this pass — only the MCU/RS-485/CAN-FD work requested." **Do not assume TPM-signed servo-bus messages are available from the servo itself** until this upgrade lands; message signing for servo commands/telemetry on this airframe continues to rely on the CAN-PERIPH-GW gateway's own TPM (SLB9672) signing the bus frame the servo command rides in, per [REF-NIST-001 §2.1], not on a TPM inside the servo. |
| **⚠ Bus electrical integration open item** | LibreServo's daisy-chain bus is genuine differential RS-485 (A/B pair via an onboard transceiver), not the STS3215's single-wire half-duplex TTL scheme that `CAN-PERIPH-GW-1`'s `J_FLEX.FLEX_TTL_GPIO` was built for. `J_FLEX` exposes a bare `FLEX_UART_TX/RX` pair but no RS-485 transceiver of its own for this local servo drop (the gateway's onboard ISOW1412 is dedicated to its own board-to-board uplink trunk, not intended as a shared local servo sub-bus without further isolation/topology review). **Not resolved here** — filed as an open item in `avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md` and `airframe/fuselage-mid/WBS.md`. |
| **⚠ Intended end state, confirmed with the fork maintainer (2026-08-02)** | Once the fork's isolated-RS-485/isolated-CAN-FD/SLB9672-TPM upgrade ships, a converted servo is intended to **drop directly onto the airframe's isolated CAN-FD and RS-485 trunks as its own self-signing bus node — no `CAN-PERIPH-GW-1` bridge required for this application.** This would make the bus-electrical-integration open item above moot rather than resolved-as-planned; the interim gateway-bridge options remain the near-term path until the fork ships. **Not yet true** — as of this writing the RS-485/CAN-FD work is schematic-only (no footprints, no board, no firmware port) and the TPM work has not started. |

**Applied to:** cargo winch drive (1×) and 2× nacelle tilt servo — all three high-torque
servos, standardised per "Servo Fleet Standardisation, 2026-08-02" above.

**Used in:** `docs/CARGO_WINCH_SPECIFICATION.md`, `current-specification/bom_revS.json`,
`current-specification/bom_revS.csv`, `avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md`

---

### REF-SENSOR-015: OpenServoCore — Open-Source SG90/MG90-Class Smart-Servo Control Board

| Field | Value |
|---|---|
| **Project** | OpenServoCore — "the goal of this project is to create an open servo controller board and firmware," targeting SG90/MG90-class servos specifically |
| **Repository** | <https://github.com/OpenServoCore/open-servo-core> |
| **Swap board (SG90 target)** | "OSC SG90 M007" — "a swap board that physically replaces the SG90 factory PCB," 10×12.5 mm, double-sided |
| **MCU** | CH32V006, RISC-V, 48 MHz, 62 KB flash, 8 KB RAM ("no multi-chip roadmap; one chip, done well") |
| **Communication protocol** | osc-native — a custom break-framed wire protocol inspired by Dynamixel Protocol 2.0; 0.5–3 Mbaud, ~30 µs ping turnaround at 1 Mbaud, multi-servo status chains, hardware CRC both directions |
| **Firmware license** | MIT OR Apache-2.0 |
| **Hardware license** | CERN-OHL-P v2.0 |
| **⚠ Project maturity** | Explicitly **"in active development. Nothing here is shippable yet."** Firmware v2 is underway; hardware validated only to revision B (as of May 2026 per project status). **Treat as a pre-production part — do not commit to procurement quantities until the project reaches a shippable release**; tracked as an open item, not silently assumed production-ready. |

**Why this part, not LibreServo:** LibreServo v2 (REF-SENSOR-014) targets standard-size
(≥40 mm class) servo bodies; OpenServoCore is purpose-built for the SG90/MG90 body size
(23 mm class) used by the cargo door and payload-release servos, so the two boards are
applied to different servo classes on this airframe rather than one board covering both.

**Applied to:** `SERVO-CARGO` (cargo door actuation ×1, payload release ×1); RCS bleed-jet
proportional valve servos (`SERVO-RCS-VALVE`, ×4, Phase 11 deferred) are the same SG90 class
and inherit this note when that phase is implemented, but are not otherwise touched here.

**Used in:** `current-specification/bom_revS.json`, `current-specification/bom_revS.csv`,
`airframe/stls/fuselage/cargo/generate_cargo_mounts.py`

---

### REF-SENSOR-016: Infineon OPTIGA™ Trust M — I2C Secure Element (planned, CAN-PERIPH-GW-1 + Flight Engineer only)

> **⚠ REQUIRES VERIFICATION (root `AGENTS.md` §4).** The primary datasheet
> (`infineon-optiga-trust-m-datasheet-en.pdf`, Infineon document reference
> `Z8F80311641-D`) could **not** be fetched in this session — `infineon.com`,
> `mouser.com`, `digikey.com`, and `device.report` are all blocked by this
> environment's network egress policy. Everything below is sourced from
> Infineon's own public GitHub overview
> (<https://github.com/Infineon/optiga-trust-m-overview>, fetched successfully)
> plus WebSearch-aggregated snippets of the primary datasheet, **not** a direct
> read of the datasheet PDF itself. **The pin-to-pad table in particular is
> not verified** and must not be used for a footprint or schematic pin
> binding until read directly off the primary datasheet. No KiCad symbol,
> footprint, or schematic net has been created against these figures — see
> "Status" below.

| Field | Value |
|---|---|
| **Manufacturer** | Infineon Technologies |
| **Product family** | OPTIGA™ Trust M, SLS32AIA — industrial variant (`SLS32AIA010MK` cited as the PSA Level 3-certified SKU in the sourced overview) |
| **Source consulted** | <https://github.com/Infineon/optiga-trust-m-overview> (official Infineon GitHub, fetched successfully) |
| **Datasheet (not fetched this session)** | Z8F80311641-D — <https://www.infineon.com/dgdl/Infineon-OPTIGA%20TRUST%20M%20SLS32AIA-DataSheet-v03_00-EN.pdf?fileId=5546d4626c1f3dc3016c853c271a7e4a> |
| **Package** | PG-USON-10, 3×3 mm |
| **Interface** | I²C, with an optional "I²C Shielded Connection" encrypted/authenticated channel over the same bus |
| **Supply voltage** | 3.3 V nominal; 5.5 V absolute maximum |
| **Temperature range** | −40°C to +105°C (matches this project's other automotive/industrial-grade parts) |
| **Asymmetric crypto** | ECC up to NIST P-521; Brainpool up to 512-bit |
| **Symmetric crypto** | RSA up to 2048; AES up to 256; HMAC up to SHA-512 |
| **Hash** | SHA-256 |
| **Key/cert storage** | Up to 10 kB user memory, multiple key/certificate slots |
| **Anti-replay** | 4 monotonic up-counters |
| **Power modes** | Hibernate (application context saved/restored across power-off, per the overview text) |
| **Certification** | Common Criteria EAL6+ (hardware); PSA Level 3 (cited SKU) |
| **⚠ Pin-to-pad table** | Not verified this session. WebSearch-aggregated snippets suggest VDD/GND/SDA/SCL on a 10-pin USON with several NC pins, but this is **not** cited to a page/table in the primary datasheet and must be independently confirmed before use. |
| **⚠ Boot/power-up latency figure** | **Not found in any source reachable this session.** The user's stated rationale for this swap is SLB9672's TPM-2.0 startup/self-test sequence being slow relative to a lighter-weight secure element; this is architecturally plausible (OPTIGA Trust M implements a vendor-specific command set, not the full TCG TPM 2.0 command interpreter/self-test suite a TPM 2.0 part like the SLB9672 runs), but no numeric figure for either part's actual power-on-ready time was verified in this session. Do not cite a specific millisecond figure until one is read off a primary datasheet. |

**Why this part, not another TPM:** the request was specifically to move away from
a TPM-class part on these two boards for latency reasons, not to swap TPM vendors.
OPTIGA Trust M supports ECDSA signing (asymmetric), AES/HMAC (symmetric), and
monotonic counters (anti-replay) — the primitives this project's message-signing
architecture actually uses on these two boards — without implementing the TCG
TPM 2.0 command protocol, PCR/attestation model, or the associated startup
self-test sequence a TPM 2.0 part runs. Since `CAN-PERIPH-GW-1` and Flight
Engineer are bare-metal MCU boards signing/verifying discrete CAN-FD/RS-485
frames (not doing OS-level measured boot or PCR attestation), the TPM's
attestation machinery was not being used by this project's own architecture on
these two boards in the first place — see `avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md`
and `avionics/kicad/FlightEngineer/FlightEngineer.md` for the specific open-item
write-ups.

**Status: decision recorded, NOT implemented.** No `.kicad_sch`, `.kicad_pcb`,
clean-room symbol, or footprint has been created or edited for this part. Two
independent gates block that work, per root `AGENTS.md` §4 and §7:

1. **Datasheet access** — the pin-to-pad table above is unverified (see the
   gate note at the top of this entry).
2. **`kicad-cli` availability** — this project's standard for a schematic/PCB
   edit is an ERC/DRC pass (root `AGENTS.md` §7); `kicad-cli` is not installed
   in this session's environment, so even a pin-verified edit could not be
   checked before being committed. Flight Engineer's own trust-module section
   was already added via a narrow text-injection script rather than a full
   regeneration specifically because a bad regeneration silently reintroduced
   drift undetectable without ERC (`inject_flight_engineer_trust_module.py`
   docstring) — the same risk applies here, more acutely, for a part with an
   unverified pinout.

**Applied to (planned):** `CAN-PERIPH-GW-1` (replacing U2, SLB9672, per stack)
and Flight Engineer (replacing `U_TPM`, SLB9672, in "Section H: Trust Module").
**Not applied to:** Observer, Commo, Pilot, XO — out of scope for this request;
those boards keep the SLB9672 (REF-SENSOR-011).

**Used in:** `avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md` (open item),
`avionics/kicad/FlightEngineer/FlightEngineer.md` (open item), `avionics/WBS.md` §1.9.2

---

### REF-SENSOR-019: SMB Bearings F688ZZ — 8x16x5 mm Flanged Miniature Radial Ball Bearing (wing-root tilt-spar bearing)

| Field | Value |
|---|---|
| **Manufacturer** | SMB Bearings |
| **Product** | F688ZZ — flanged, double-metal-shielded miniature radial ball bearing |
| **Datasheet (fetched and read this session)** | <https://www.smbbearings.com/firebrick/ckeditor/plugins/upload/Uploads/Documents/bearingpdfs/F688ZZ-flanged-miniature-bearing-8x16x5mm.pdf> |
| **Bore (ID)** | 8 mm (0.3150 in) |
| **Outside diameter (OD)** | 16 mm (0.6299 in) |
| **Width** | 5 mm |
| **Flange OD** | 18 mm |
| **Flange width** | 1.1 mm |
| **Flange step height** | 0.2 mm (min.) |
| **Rings/balls material** | SAE 52100 chrome steel |
| **Cage material** | Pressed steel |
| **Closures** | Metal shields (ZZ) |
| **Static load rating** | 59 kgf (579 N) |
| **Dynamic load rating** | 125 kgf (1,226 N) |
| **Speed limit** | 36,000 rpm (with adequate lubrication) |
| **Standard lubrication** | Kyodo Yushi Multemp SRL grease |
| **Bore/OD tolerance (P0, as-supplied grade)** | +0 / −0.008 mm each |
| **Compliance** | EU RoHS and REACH |

**Applied to:** the wing-root (fuselage-wall) end of each 8 mm OD AISI 4130 rotating
tilt-spar, per `airframe/wings-nacelles/WBS.md` §1.1.2 **SPAR-01** ("Root bearing
stays F688ZZ" — the tip end uses the downsized MF128ZZ, not this part; see the
2026-07-19 Rev R2d note in the same section). The bearing seat cut into the cargo
shell (`airframe/fuselage-mid/WBS.md` CARGO-02) is sized from this datasheet's OD —
**16 mm nominal, +0/−0.008 mm** — plus a light interference allowance for a
printed-plastic seat (outer race stationary in the shell; inner race rotates with
the spar), not from the retired Ø22 mm press-fit figure that sized the old fixed
12 mm CF tube boss. The 8 mm bore matches the spar's 8 mm OD directly (line-to-line
on the rotating inner race, per the manufacturer's P0 bore tolerance above; no
added clearance is applied on the *bearing* bore itself — the 8.3 mm figure in
`WING_SPAR_BORE_D` is a separate, non-bearing rotating clearance elsewhere along
the spar's run, not this seat).

**Used in:** `airframe/blender-scripts/merge_cargo_interior.py`
(`WING_SPAR_BOSS_OD`), `airframe/wings-nacelles/WBS.md` §1.1.2,
`airframe/fuselage-mid/WBS.md` §1.1.1.2 CARGO-02, `current-specification/bom_revS.csv`

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
transceivers on Pilot (Cape-A-2) and XO (Cape-B-2); 120 Ω termination resistors at CN1
(Shepherd's Room / Bay A) and FC4 (Simon's Medbay / Bay D).

**Used in:** `docs/AVIONICS_PB2_REDESIGN.md`, `docs/REVN_BUILD_GUIDE_24IN.md`,
`avionics/kicad/Pilot.md`, `avionics/kicad/XO.md`,
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
| **License** | Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) — <https://creativecommons.org/licenses/by-sa/4.0/> (corrected 2026-08-01 from an earlier "CC BY 4.0" mis-citation in this catalog and in `current-specification/LICENSE_AND_ATTRIBUTION.md`/`README.md` — the upstream Thingiverse license page states CC BY-SA 4.0, not plain CC BY) |
| **Repository copy** | `docs/references/thingverse-serenity/` (source STLs in `files/`, renders in `images/`, upstream `LICENSE.txt` + `README.txt`) |
| **CERN-OHL-W integration** | Incorporated into the project's CERN-OHL-W 2.0-licensed airframe Covered Source as an **Available Component** [REF-LIC-001 §1.6] — the upstream geometry keeps its own CC BY-SA 4.0 terms (share-alike applies to redistributions of the upstream model itself; the project's original adaptation work is separately licensed CERN-OHL-W 2.0 per `airframe/LICENSE`). See `docs/attribution_and_licensing.md` "Available Component Boundary." |
| **Note** | This is the **origin of the project's `s_*.stl` geometry** — every hull/nacelle/wing/gear STL in the build traces back to this model (adapted: scaled to 24 in (609 mm), hollowed to 2.0 mm CF-PETG, CF skeleton + foam fill added). It is the **lowest** of the three canonical references in authority: **verify its detail against REF-CAD-003 (QMx) and REF-CAD-002 (Nick Henning) before treating any feature as canonical** — but it remains a usable, license-clean geometry starting point. Do not confuse Thing 7330462 with the separate low-poly orientation guide Thing 4677565 (`current-specification/LICENSE_AND_ATTRIBUTION.md` §2b). |

**Applied to:** base hull/section geometry for the entire fuselage and nacelle build; the four
canonical sections and the swivel-engine/tilt concept originate here.

**Used in:** `airframe/stls/` (all `s_`-lineage fuselage/nacelle/wing/landing-gear STLs, `s_` prefix
dropped Rev R1); full remix attribution in
[`current-specification/LICENSE_AND_ATTRIBUTION.md`](current-specification/LICENSE_AND_ATTRIBUTION.md) §2.

### REF-CAD-005: Ryan and Israel (General Electric) — "Exhaust nozzle flap seal arrangement" (US 4,128,208)

| Field | Value |
|---|---|
| **Inventors** | Edward W. Ryan; George H. Israel, Jr. |
| **Assignee** | General Electric Company |
| **Work** | Exhaust nozzle flap seal arrangement — variable-area exhaust nozzle carrying seals **between adjacent flaps** to minimise flow loss as the flaps modulate between minimum and maximum area positions |
| **Designation** | United States Patent US 4,128,208 |
| **Official URL** | <https://patents.google.com/patent/US4128208A/en> |
| **Filed / Granted** | Filed 1977-07-11; granted 1978-12-05 |
| **Legal status** | **Expired — lifetime.** Verified 2026-08-09 via the Google Patents record above. The disclosure is in the public domain; nothing in this project practises a live claim. |
| **License** | Not applicable — an expired US patent is public-domain technical disclosure, cited here as prior-art/technique literature. No text, figure, or geometry from the patent is copied or redistributed. |
| **Note** | Cited for the **master-flap / seal-flap principle only**: in a variable-area nozzle whose flaps overlap circumferentially, the overlap is only realisable if alternate members sit at different radii, so one set laps over its neighbours and closes the inter-flap gap from outside rather than occupying the same material. Serenity-UAV's implementation (tangential-hinge conical flaps, `FLAP_SHINGLE_GAP` running clearance, spiral-cam unison ring) is original work; the patent's own bellcrank-centered seal linkage is **not** used — this design carries the seal on its own hinge, identical to the master flap. |

**Concept applied in this project:** Rev T3 (2026-08-09) of the nacelle variable nozzle.  All eight
flaps had been carved from one radial band, so the deliberate 5° circumferential overlap
(`FLAP_SPAN_DEG` 50° × 8 = 400° of arc on a 360° circle) was a solid interpenetration — physically
unbuildable, and it exported assembly STLs with coincident cylindrical surfaces that failed the
repository's watertight check.  Alternate flaps are now **seal flaps** lapped
`FLAP_SHINGLE_GAP` = 0.2 mm (0.008 in) outboard of the **master flaps**, which keeps the masters'
inner surface as the flow-facing boundary.  The master flaps are geometrically unchanged, so
`exit_r(φ) = R_HINGE − FLAP_LENGTH·sin φ` and the 75 %/105 % bore-percentage targets are unaffected.

**Applied to:** the nacelle variable-area nozzle flap ring (8 flaps per nozzle = 4 master + 4 seal;
2 nozzles per aircraft).

**Used in:** `airframe/openscad/nacelles/nacelle_nozzle_iris.scad` (header Rev T3 and the
`FLAP_SHINGLE_GAP` derivation block), `airframe/wings-nacelles/WBS.md` §1.1.3,
`docs/PHASED_BUILD_GUIDE.md` (nozzle flap print quantities), `current-specification/bom_revS.json`
(`PRINT-NACELLE-FLAP-MASTER` / `PRINT-NACELLE-FLAP-SEAL`), `TODO.md` §1.1.3.

### REF-CAD-006: Selig, M.S. — S1223 airfoil coordinates (UIUC Airfoil Coordinates Database)

| Field | Value |
|---|---|
| **Author** | Michael S. Selig (University of Illinois at Urbana-Champaign, Department of Aerospace Engineering) |
| **Work** | S1223 airfoil — tabulated (x, y) surface coordinates, normalised to unit chord, Selig convention (single closed loop starting/ending at the trailing edge, upper surface TE→LE followed by lower surface LE→TE) |
| **Designation** | UIUC Airfoil Coordinates Database, entry `s1223.dat` |
| **Official URL** | <https://m-selig.ae.illinois.edu/ads/coord_database.html> (database index); direct file <https://m-selig.ae.illinois.edu/ads/coord/s1223.dat> |
| **Retrieved** | 2026-08-24, fetched live via HTTP GET against the direct file URL above; content verified against the published S1223 plots at <https://m-selig.ae.illinois.edu/ads/afplots/s1223.gif> (same database) |
| **License** | UIUC Applied Aerodynamics Group airfoil data is published for open engineering/research use; cited here per this project's citation policy (root `AGENTS.md` §4) regardless of whether a formal license notice accompanies the file. No coordinate value is altered — the table below is a verbatim re-split of the published 81-point loop into the two ordered surface lists (`S1223_UPPER` LE→TE, `S1223_LOWER` TE→LE) that `wings_s1223_revo.scad`'s existing `s1223_section()`/`midline_frac()` decomposition expects; no interpolation, smoothing, or invented points were introduced. |
| **Note** | Supersedes the placeholder table that shipped with `wings_s1223_revo.scad` since Rev R1 — that table was a hand-typed approximation that crossed to negative thickness at x/c ≈ 0.742 (WING-01, `tools/wing_airfoil_integrity.py`). This entry is the actual source data; the placeholder's origin was never traceable to a fetch and is not cited as a source. |

**Applied to:** `S1223_UPPER` / `S1223_LOWER` coordinate tables — the wing outer-mold-line section
used by `s1223_section()`, `wing_solid()`, and every bore/pad module in
`wings_s1223_revo.scad` that reads `midline_frac()`.

**Used in:** `airframe/openscad/wings/wings_s1223_revo.scad` (`S1223_UPPER`, `S1223_LOWER`),
`tools/wing_airfoil_integrity.py` (validates this table), `airframe/wings-nacelles/WBS.md` §1.1.2
(WING-01).

---

## Part XV — Open Hardware / Software Licensing Standards

### REF-LIC-001: CERN Open Hardware Licence Version 2 — Weakly Reciprocal (CERN-OHL-W 2.0)

| Field | Value |
|---|---|
| **Publisher** | CERN (European Organization for Nuclear Research) |
| **Designation** | CERN-OHL-W-2.0 |
| **Official URL** | <https://ohwr.org/licences/> (license text + user guide), SPDX record <https://spdx.org/licenses/CERN-OHL-W-2.0.html> |
| **Applied sections** | §1.6 "Available Component" (upstream hardware not itself licensed under CERN-OHL but legitimately referenced/incorporated without relicensing); §4 (distribution obligations); §5 ("weakly reciprocal" scope — modifications to Covered Source must stay CERN-OHL, but a design that merely *uses* Covered Source without modifying it is not itself pulled under the license) |
| **Note** | Selected 2026-08-01 (TODO.md §0.9 licensing audit) as the license for this project's original hardware/CAD/PCB design work — airframe (wings, nacelles, landing gear, cargo system, fuselage) and avionics (Pilot/XO/FlightEngineer/Commo/Observer PCB schematics, layouts, Gerbers). Documentation, code, scripts, and non-hardware drawings remain CC BY-SA 4.0 — see `docs/attribution_and_licensing.md`. |

**Applied to:** `LICENSE` (root), `avionics/LICENSE`, `airframe/LICENSE`; the CERN-OHL-W
"Available Component" concept is used to define the IP boundary around the three canonical
airframe reference sources (REF-CAD-002/003/004) — see `docs/attribution_and_licensing.md`
"Available Component Boundary."

**Used in:** all KiCad/SCAD/STL/FCStd original design files in `airframe/` and `avionics/`.

### REF-LIC-002: OSHWA Open Source Hardware Certification

| Field | Value |
|---|---|
| **Publisher** | Open Source Hardware Association (OSHWA) |
| **Designation** | OSHWA Certification Program / Open Source Hardware Definition |
| **Official URL** | <https://certification.oshwa.org/requirements.html> (requirements), <https://certification.oshwa.org/process.html> (self-certification process), <https://certification.oshwa.org/basics.html> (definition basics) — verified 2026-08-01 |
| **Applied requirements** | (1) all of the creator's own contributions to a certified product must be shared as open source; (2) all parts within the creator's control must be open source, third-party proprietary components clearly distinguished, and third-party chips must have fully accessible/shareable datasheets; (3) all software necessary for hardware operation must be licensed under an OSI-approved license; self-certification is completed via an online license form + Certification Mark License Agreement, valid one year with annual reaffirmation |
| **Note** | Program is **self-certification**, not a numbered legal standard — no §-citation exists to verify beyond the requirements page above. UUID assignment and the Certification Mark License Agreement require the human maintainer (Steve Griffing) to submit the actual application; this repository can only prepare the supporting documentation. See `docs/OSHW_CERTIFICATION.md` for the readiness checklist (TODO.md §0.9 item 7, still open — submission not yet made). |

**Applied to:** `docs/OSHW_CERTIFICATION.md` readiness checklist; not yet applied to an actual
OSHWA certification submission (open item).

**Used in:** `docs/OSHW_CERTIFICATION.md`, `TODO.md` §0.9.

## Removed / Superseded Citations

The following references appeared in earlier versions of project files but have been removed
because they were incorrectly attributed, unverifiable, or inapplicable.

| Old Citation | Where Found | Reason Removed | Replacement |
|---|---|---|---|
| "NIST SP 800-72 principles" (write-blocker design) | `README.md` §Patent Notice, line 382 | **Incorrect attribution.** NIST SP 800-72 (2004) is "Guidelines on PDA Forensics" — unrelated to write-blocker design. The closest applicable standard is NIST SP 800-92 §4.4.2 (log data protection principles). | REF-NIST-004 (NIST SP 800-92 §4.4.2) |
| 47 CFR Part 95 RCRS (§95.635/§95.655/§95.639, "TDDS"/"LERS"/"27 channels") | REF-FCC-003, `skipper_antenna_spec.md`, `AGENTS.md`, `README.md`, `TODO.md`, `AVIONICS_PB2_REDESIGN.md` | **Wrong band.** RCRS covers only 26–28/72/75 MHz, not 49 MHz; "TDDS"/"LERS"/27-channel terms untraceable. Commo's 49.82–49.90 MHz band is Part 15 §15.235, unlicensed. | REF-FCC-003 (Part 15 §15.235) |
| "ASTM F3322 — sUAS Battery Safety" | TODO.md §0.4 (candidate list, not yet cited in active docs) | **Incorrect attribution.** F3322 is the *Standard Specification for Small Unmanned Aircraft System (sUAS) Parachutes* — unrelated to batteries, and not applicable to Serenity (no deployable recovery parachute). | REF-ASTM-002 (ASTM F3005-22, sUAS battery specification) |
| "ASTM F3003 — Quality Assurance of a Small Unmanned Aircraft System" | TODO.md §0.4 (candidate list, not yet cited in active docs) | **Withdrawn standard.** F3003-14 was withdrawn by ASTM in January 2023 with no replacement. | None — see REF-ASTM-001 (F2910) for design/construction/test coverage |
| RunCam Nano 4 analog camera (REF-SENSOR-001) at bow sensor pod | `avionics/AGENTS.md`, `TODO.md` §1.1.1.1a | **Superseded by design decision (2026-07-03), not an error.** Replaced by the Observer board's TI AM62Ax digital vision SoC (REF-SENSOR-003) at both the nose and cargo bay locations. | REF-SENSOR-003 (TI AM62Ax) |
| "TI DM38x + remixed OpenIPC firmware" (early Observer design concept from an external AI-assisted brainstorm, never committed) | Not committed to any file — caught during REFERENCES.md drafting 2026-07-03 | **Infeasible as proposed.** TI DM385/DM388 (DaVinci DM38x) are NRND; OpenIPC's supported-hardware list contains no TI part, not even at R&D stage — porting would mean a from-scratch ISP/encoder bring-up on a chip TI is discontinuing, not a firmware port. Also: the same source proposed LAN9355/KSZ9563 for "MRP" ring redundancy (neither chip implements it) and an "ST33GTPMISPI" TPM part number that does not exist. | REF-SENSOR-003 (TI AM62Ax, in-production, TI's own open BSP), REF-SENSOR-005 (KSZ9477, real HSR/PRP support), Infineon SLB9672 (fleet-standard TPM, REFERENCES.md §3.3/§4.2) |
| ADI ADM2795EBRWZ (isolated RS-485, signal-only) — `Observer`, `CAN-PERIPH-GW-1`, `Flight Engineer`, `Pilot`, `XO` RS-485 transceivers | `avionics/kicad/Observer/kicads/Observer.kicad_sch`, `avionics/kicad/CAN-PERIPH-GW-1/`, `avionics/kicad/FlightEngineer/kicads/FlightEngineer.kicad_sch`, `avionics/kicad/Pilot/kicads/Pilot.kicad_sch`, `avionics/kicad/XO/kicads/XO.kicad_sch` | **Superseded by design decision, 2026-07-26.** ADM2795E provides signal isolation only and requires a separate external isolated DC-DC supply for its bus-side VDD2. TI ISOW1412 integrates its own isolated DC-DC, eliminating the extra supply and simplifying every "trust module" node fleet-wide. Fleet-wide swap performed 2026-07-26. Separately, while performing this swap on Pilot and XO, found their pre-existing ADM2795EBRWZ symbols had incorrectly numbered pins (and their ISOW1044BDFMR symbols had the wrong footprint, `SOIC-16W` instead of the correct `SOIC-20W` for a 20-pin part) — both defects predate this session and were corrected as part of the same fix (`kicad-cli sch erc` violation counts unchanged before/after: Pilot 48, XO 234 — confirming the fix corrected the target defects with zero regression against these boards' large, pre-existing, out-of-scope ERC backlog). | REF-SENSOR-010 (TI ISOW1412) |

---

## Open Standards Verification Items

The following citations in the codebase require verification before first flight.
Add verified section numbers to the relevant files and update this table.

| Citation | File | Issue | Action Required |
|---|---|---|---|
| §15.203 antenna restriction (Commo RF connector) | Commo board files, `skipper_wiring.md` | **Confirmed, resolved 2026-06-20.** §15.203 binds the manufacturer directly. J2 used a generic SMA edge connector (Amphenol 132289), a standard jack; no exception applies. | **Resolved:** J2 changed to 132289RP (RP-SMA, same footprint), satisfying §15.203. Board re-spin tracked in TODO.md §0.1 |
| 14 CFR Part 47 (aircraft registration marks) | `ax25_types.h` | **Resolved 2026-06-21.** README/build guide had no erroneous citation; the miscitation was in `ax25_types.h`, which stated Part 47 governs registration and AX.25 needs an amateur license (Part 97) | Corrected to cite Part 48 §48.205 [REF-FAA-001]; link is license-exempt under Part 15 §15.235 [REF-FCC-003], per REF-PROTO-001 |
| AUVSI "standards" (unnamed) | `AGENTS.md`, `README.md` | **Resolved 2026-06-22.** No specific numbered AUVSI standard exists (AUVSI publishes frameworks, not numbered design standards). Identified and verified three applicable ASTM F38 standards. | Added REF-ASTM-001 (F2910-22, design/construction/test), REF-ASTM-002 (F3005-22, batteries), REF-ASTM-003 (F3269-21, runtime assurance/failover). `AGENTS.md`/`README.md` AUVSI text is accurate as-is (AUVSI frameworks, not numbered standards) — no doc text change needed there. |
| IEC 62368-1 clause numbers | PCB layout (not yet complete) | PCB layout must verify creepage/clearance distances meet IEC 62368-1 Clause 5.5.2 requirements for 5 kV reinforced insulation; this cannot be verified until PCB layout is complete | Verify during Pilot and XO PCB layout review (see TODO.md §1.4) |
| REF-IEC-003 (IEC 61000-4-2) exact product URL | `REFERENCES.md` REF-IEC-003 | Exact webstore.iec.ch product-page URL not confirmed during catalog entry (WebFetch redirected to homepage during verification attempt 2026-06-29); standard designation and content are correct | Confirm product page URL via <https://webstore.iec.ch/> search for "IEC 61000-4-2" and update REF-IEC-003 |
| REF-IEC-004 (IEC 61000-4-4) exact product URL | `REFERENCES.md` REF-IEC-004 | Same as REF-IEC-003 — webstore URL not confirmed 2026-06-29 | Confirm via <https://webstore.iec.ch/> search "IEC 61000-4-4" |
| REF-IEC-005 (IEC 61000-4-5) exact product URL | `REFERENCES.md` REF-IEC-005 | Same as REF-IEC-003 — webstore URL not confirmed 2026-06-29 | Confirm via <https://webstore.iec.ch/> search "IEC 61000-4-5" |
| REF-TIA-001 (ANSI/TIA-485-A) exact product URL | `REFERENCES.md` REF-TIA-001 | TIA standards portal URL not confirmed via WebFetch 2026-06-29 (domain blocked by permission hook) | Confirm product page via <https://www.tiaonline.org/standards/> or <https://webstore.ansi.org/> search "TIA-485-A" |
| Anti-collision flash rate "60 FPM" | `build_guide_13_nav_lights.svg`, `decal_sheet.svg` | **Resolved 2026-06-29.** Researched 14 CFR Part 107 §107.29(b) (anti-collision light visible 3 statute miles — no flash rate specified), old Part 23 §23.1401 (reorganized 2017, prescriptive flash-rate text no longer exists in current eCFR), and Part 25 §25.1401(f) (transport category, 40–100 FPM — not directly applicable to this sUAS). No currently-enforceable regulatory standard applicable to Part 107 UAS mandates a specific flash rate. "60 FPM" in the build guide is a design convention within the conventional aviation anti-collision light range (40–100 FPM). No regulatory citation is required or appropriate; the figure is a design target, not a compliance claim. | No citation required — design convention documented here. |
| REF-SENSOR-005 (KSZ9477 HSR/PRP) IEC 62439-3 clause numbers | `REFERENCES.md` REF-SENSOR-005 | AN3474 confirms HSR/PRP hardware support but exact IEC 62439-3 Clause 4 (HSR)/Clause 5 (PRP) sub-clause numbers applied have not been cross-checked against the standard text itself | Obtain IEC 62439-3 and confirm clause numbers before final PCB layout citation (TODO.md §1.2c) |
| Observer laser — single 520 nm green source, **Class 2 both sites**, part/optic ratings | `REFERENCES.md` REF-IEC-002, `avionics/kicad/Observer/Observer.md`, `docs/OBSERVER_LASER_ANALYSIS.md` | Per `docs/OBSERVER_LASER_ANALYSIS.md` Rev A1 (2026-07-05) both installs share ONE 520 nm green diode + driver and are **both Class 2 (≤1 mW)** — the nose is a concentrated dot detected by Observer's camera (strobe + frame-difference), ~0.45 mW, NOT the inherently Class 3B module of Rev A. Differ only by per-location terminal optic (spread) + hardware current limit. No real, sourced part exists yet. | Source a real datasheet with manufacturer-stated mW output and IEC 60825-1 class for the green diode + both optics before procurement; update REF-IEC-002 with the verified citation (TODO.md §1.2c.4). Do not fabricate or procure against the placeholder. Both Class 2 caps must be hardware-enforced; no Class 3B interlock/shutter required unless a human-at-target-in-full-sun requirement is later added. |
| Commo `RSSI_CMP` carrier-detect comparator part number and pinout | `avionics/kicad/Commo.kicad_sch` / `Commo.kicad_pcb`, `avionics/kicad/mod_commo_pcb.py` | The RSSI→`RSSI_DCD` conversion (2026-07-04 reconciliation) adds an on-board comparator, value placeholder "LMV331-class". No specific part is vetted; the PCB pad→net map is by function only and the SOT-23-5 pin order is unconfirmed. | Select a real comparator, confirm its SOT-23-5 datasheet pinout (and push-pull vs open-drain — add a `RSSI_DCD` pull-up if open-drain), add a `REF-*` catalog entry with a validated URL, and correct the footprint pad map before layout is final (TODO.md §1.2b). Do not fabricate or procure against the placeholder. |
| VL53L5CX obstacle-avoidance ToF sensor — no REF-ID | `docs/failsafe_thresholds.md`, `avionics/firmware/common/include/failsafe_config.h`, `docs/PHASED_BUILD_GUIDE.md` | Found 2026-07-12 while writing the Failsafe Threshold Document: the 12× VL53L5CX obstacle-avoidance array is cited throughout the repository (4 m range noted informally inside the REF-SENSOR-002 entry above) but has no `REFERENCES.md` catalog entry of its own, unlike the project's other core sensor ICs (REF-SENSOR-002 through -006). | Add a `REF-SENSOR-007` entry for ST Microelectronics VL53L5CX (validated datasheet URL, ranging accuracy, and the 4 m operating range cited in `docs/failsafe_thresholds.md` §3) before final PCB layout citation sign-off (TODO.md §3.0 Phase 0). |
| Tilt-spar material allowables (4130 + trade-study alternates) | `docs/TILT_SPAR_ANALYSIS.md` §3.1–3.2/§3.5, `current-specification/bom_revS.csv` SPAR-TILT-4130 | The §3.5 material trade study uses **typical handbook allowables** for AISI 4130 (~460 MPa yield), 17-4 PH H1075 (~860 MPa), 7075-T6 (~503 MPa), 6061-T6 (~276 MPa), 316 SS, and Ti-6Al-4V (~880 MPa); none are yet tied to a validated MMPDS/AMS product page. Moduli/densities are nominal. | Confirm the **selected** material's design allowable and the two carried alternates (17-4 PH, 7075-T6) vs MMPDS-2023 / AMS (or mill cert) and add `REF-MAT-*` catalog entries with validated URLs before spar procurement (TODO §0.8). |
| CF plate bending allowable for the SPAR-01 thwarts | `airframe/wings-nacelles/WBS.md` §1.1.2 SPAR-01, `tools/wing_spar_carrythrough.py`, `docs/structural_analysis.md` §1 | The two CF thwarts that replace the wing-spar carry-through (2026-08-23) are sized against a **300 MPa** cross-ply bending stand-in, chosen a factor of 5 below the only CF figure the repository carries — `docs/structural_analysis.md` §1's ~1 500 MPa for **unidirectional pultruded** stock, which is itself marked as requiring supplier certificates. A thwart is loaded in bending across the ship, which is not that layup, so neither number is a verified allowable for this part. The tool prints FOS against both (8.5 and 42.5 at the governing station). | Obtain ASTM D3039 (tensile) and ASTM D695 (compressive) certificates for the actual CF plate stock, add a `REF-MAT-*` catalog entry with a validated URL and the certified flexural allowable, and re-run `tools/wing_spar_carrythrough.py` before cutting the thwarts. Do not fabricate the figure. (root `TODO.md` §0.8) |
| S1223 airfoil coordinates — the tabulated section is not a valid airfoil | `airframe/openscad/wings/wings_s1223_revo.scad` `S1223_UPPER`/`S1223_LOWER`, `airframe/wings-nacelles/WBS.md` §1.1.2 WING-01, `tools/wing_airfoil_integrity.py` | The tabulated upper surface falls below the lower surface over the aft quarter: section thickness goes **negative from x/c ≈ 0.742**, reaching t/c −0.0152 at x/c 0.90, and the outline self-intersects at (0.7417, 0.0235). The aft upper points sit ~0.03 t/c below published Selig S1223. **No source is recorded for the tables** — they carry no citation, retrieval date, or URL anywhere in the repository, which is how a corrupted aft section went unnoticed. `wing_solid()` lofts with `hull()`, whose convex hull is 1.647× the outline's area, so the defect never reaches the STL and `validate_stls.py` passes. | Retrieve S1223 coordinates from the **UIUC Airfoil Coordinates Database** (<https://m-selig.ae.illinois.edu/ads/coord_database.html>) — URL not yet validated against the issuing site by this repository, so verify before citing — record the retrieval date, add a `REF-CAD-*` entry, and only then replace both tables. `tools/wing_airfoil_integrity.py` must reach PASS. Do **not** transcribe coordinates from memory or from the comparison column in WING-01. (root `TODO.md` §1.1.2) |
| DS3225 nacelle-tilt servo — residual torque margin vs the tilt requirement | `avionics/datasheets/DS3225 datasheet.pdf`, `docs/TILT_SPAR_ANALYSIS.md` §2/§2.1, `current-specification/bom_revS.csv` SERVO-TILT | **Dimensions RESOLVED and stable across the swap.** DS3225 (added 2026-08-23) is **dimensionally identical** to the DS3218 it replaces — 40 × 20 × 40.5 mm, 60 g, 54.5 mm flange span, 49.5 × 10 mm bolt pattern, flange 27.7 mm above base — so the Rev S1d cargo-shell pads are unaffected. Datasheet stall is **21 kgf·cm @ 5 V / 24.5 kgf·cm @ 6.8 V**; the "25kg" in the product name is the marketing figure and the spec table maxes at 24.5. Against the uncorrected **≥ 25 kgf·cm (2.45 N·m)** spec-pick that was **98 % at 6.8 V**. **RESOLVED 2026-08-25** (`docs/TILT_SPAR_ANALYSIS.md` §2.1): the ≥25 kgf·cm figure was itself the stale artifact — it is a spec pick (`archives/serenity-rev-r.jsx` L383), not a load derivation. Re-derived from aero+inertia only (pivot at CG nulls gravity to within a 0.019 kgf·cm bound on two off-axis parts): grounded requirement ≈ 1.80 kgf·cm, **7.3 % of DS3225's 24.5 kgf·cm** — wide margin. Aero moment could not be grounded (no nacelle Cd/frontal-area data exists in the repo) and remains an open item, not assumed zero. **DS3225 stands; no part change.** Stall current is cited at **1.9 A / 2.3 A** — this is the **6 V servo bus** current (`docs/POWER_DISTRIBUTION.md` §3.3), now resized there to 2.3 A/servo; it is **not** RAIL-2 (RAIL-2/`5V_OBS` is the separate Observer/winch-servo rail, `docs/POWER_DISTRIBUTION.md` §3.2.1/§11.1 — the earlier "1.2 A placeholder RAIL-2 was sized on" language in this row and elsewhere was a citation error, corrected 2026-08-25). | Bench-measure stall torque of a DS3225 + LibreServo_v4 unit at the rail voltage actually chosen, to confirm the datasheet figures translate to the built hardware — the load-side conclusion (DS3225 stands) does not depend on this, but it remains an open verification item per Scope Boundaries. (root `TODO.md` §0.8) |
| SPT5425LV mounting-ear span and bolt-hole spacing (REF-SENSOR-013) | `REFERENCES.md` REF-SENSOR-013, `airframe/blender-scripts/merge_cargo_interior.py` `NSVMT_HOLE_S_Y`/`NSVMT_HOLE_S_Z`, `airframe/wings-nacelles/WBS.md` §1.1.2 SPAR-02 | REF-SENSOR-013 publishes the SPT5425LV body as 40.5 × 20 × 40.5 mm but **neither source lists the mounting-ear span or the bolt-hole spacing**. The cargo shell drills a 35 × 16 mm pattern into both nacelle-servo pads; that pattern predates this servo (drawn for the uncited DS3218MG the BOM replaced 2026-08-02) and is therefore unlikely to match. `tools/nacelle_servo_deconflict.py` carries a 6 mm/end ear allowance as an explicitly conservative stand-in, not a datasheet figure, and the 0.5 mm Y pad shortfall it reports rests entirely on that allowance. | Measure the ear span and hole spacing on a real SPT5425LV (or obtain a dimensioned manufacturer drawing), add them to REF-SENSOR-013, then correct `NSVMT_HOLE_S_Y`/`NSVMT_HOLE_S_Z` and re-run `tools/nacelle_servo_deconflict.py` before the cargo shell is cut. Do not fabricate the spacing. (root `TODO.md` §0.8) |
| CF-PETG **bearing** allowable for the wing-root tenon | `airframe/fuselage-mid/WBS.md` §1.1.1.2 CARGO-03c, `tools/wing_spar_carrythrough.py`, `docs/structural_analysis.md` §7.3, **REF-MAT-001** | **RESOLVED (built) 2026-08-25 under the default `two_rod` path — this row now describes the coupon-gated alternative, not a blocker.** The wing-root couple is now reacted by two bonded CF tie rods (`wings_s1223_revo.scad` `TENON_LOAD_PATH = "two_rod"`), sized against the repo's existing ≈5 MPa bond-limited CF-PETG figure at FOS 5.26 (fwd)/4.14 (aft) — no new allowable needed to close this. The tenon itself is traded out of the load path and reverted to a locating-only feature. The **`enlarged_tenon`** path (tenon alone reacting the full 14.60 N·m ultimate moment, needing ≥40.6 MPa bearing at 12 mm insertion or ≥11.1 MPa at the airframe's 39.2×20.1 mm maximum envelope) stays documented/buildable but is not default and remains gated on a real bearing coupon. **REF-MAT-001** (2026-08-25) adds the first peer-reviewed data point — ASTM D695 *bulk* compressive strength for 20%-CF-PETG, ≈47–60 MPa — an order of magnitude above the 5 MPa placeholder, but it is bulk unnotched compression, not a bearing-in-a-hole test, so it does not by itself clear the ≥11.1–40.6 MPa bar this row's `enlarged_tenon` alternative needs; it does make that alternative look plausibly viable pending an actual bearing coupon, where before this row had no positive evidence at all. | For the built `two_rod` path: no action required, already closed. To *reopen* `enlarged_tenon` as a real option: run a genuine bearing coupon (ASTM D953 or equivalent pin-in-hole test, printed in the tenon's own orientation/layer direction) rather than inferring a bearing allowable from REF-MAT-001's bulk-compression figure via an unstated knockdown factor — add the LG-11 coupon-test schedule item (root `TODO.md` §1.1.4) if pursued. Do not fabricate a bearing/bulk-compression knockdown factor. |
| 14 CFR Part 107 dropped-object provision — section number **not yet verified** | `REFERENCES.md` REF-FAA-002 applied-sections table, `docs/CARGO_WINCH_SPECIFICATION.md` §3.10.2 | Part 107 contains a provision prohibiting dropping an object from a small UA in a manner that creates an undue hazard to persons or property. REF-FAA-002's applied-sections table currently lists only §107.3, §107.29, §107.31 and §107.51(a)–(d) — the dropped-object section is **absent**, so no section number is asserted in the winch spec (root `AGENTS.md` §4: never guess a section number). This matters because the cargo winch **intentionally** releases a payload (requirement R5, overload line-shed) while an uncommanded structural release of the spool itself (19.1 J, or 31.8 J for the full assembly, from the §107.51(b) 400 ft ceiling) is precisely the hazard the provision addresses. | Look up the section in the eCFR Part 107 text, add it to REF-FAA-002's applied-sections table with the exact title and a validated URL, then cite it in `docs/CARGO_WINCH_SPECIFICATION.md` §3.10.2 and state explicitly how a commanded shed differs from an uncommanded release under that text. Do not fabricate the number. (`docs/TODO.md` §0.x) |
| STS3215 cargo winch servo — envelope, torque, mass, stall current (REF-SENSOR-012) | `REFERENCES.md` REF-SENSOR-012 | **MOOT — servo superseded 2026-08-02.** The STS3215 datasheet-verification gate below is retained only as a historical record; the winch (and nacelle tilt) servos have moved to SPT5425LV/LibreServo v2 (REF-SENSOR-013/014), whose envelope/torque/mass are published COTS figures — see the row below. Do not spend further effort clearing this gate. | None — superseded. |
| SPT5425LV servo — stall current; rotation-pin removal procedure (REF-SENSOR-013) | `REFERENCES.md` REF-SENSOR-013, `docs/CARGO_WINCH_SPECIFICATION.md` §3.1/§3.9 (Rev C), `current-specification/bom_revS.json`/`.csv`, `airframe/openscad/nacelles/nacelle_servo_bracket.scad` | Stall/running current is not published on either sourced listing (manufacturer product page or servodatabase.com), so RAIL-2 and the nacelle-tilt servo rail budgets carry the prior STS3215-era 1.2 A figure forward as a **placeholder, not a verified SPT5425LV number**. Separately, the exact internal location and removal procedure for the rotation-limiting pin has not been confirmed by teardown — the "remove the pin for continuous rotation" mod is a well-known technique on hobby servos generally, but part-specific verification is outstanding. | Bench-measure SPT5425LV stall current at 5–6 V before finalizing RAIL-2 / nacelle-tilt servo-rail sizing; photograph/document the pin-removal procedure on a teardown unit before committing steps to the build guide. Do not fabricate either figure. (`docs/TODO.md` §0.x) |
| LibreServo v2 fork — RS-485 differential bus electrical integration onto `CAN-PERIPH-GW-1` (REF-SENSOR-014) | `avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md`, `docs/CARGO_WINCH_SPECIFICATION.md` §5.1 (Rev C) | LibreServo's daisy-chain is genuine differential RS-485 (onboard transceiver on the servo side); `J_FLEX` on the gateway exposes only a bare `FLEX_UART_TX/RX` pair, not a local RS-485 transceiver for this specific servo drop. Also, the fork's own isolated-RS-485/CAN-FD/TPM upgrade (`PCB/RS485-CANFD-TPM-upgrade.md`) is schematic-only with no footprints, PCB placement, or firmware port yet, and the TPM addition has not been started at all. | Decide and document the gateway-side RS-485 transceiver approach (add one at the harness, or extend the gateway schematic) before winch/nacelle-tilt firmware bring-up; do not assume TPM-signed servo-native messages until the fork's TPM work lands — rely on the gateway's own TPM signing the CAN-FD/RS-485 frame instead. (`airframe/fuselage-mid/WBS.md`) |
| OpenServoCore hardware maturity for SG90 cargo servos (REF-SENSOR-015) | `REFERENCES.md` REF-SENSOR-015, `current-specification/bom_revS.json`/`.csv` `SERVO-CARGO` | Upstream project status is explicitly "in active development, nothing here is shippable yet," hardware validated only to revision B as of the source consulted. | Re-check `github.com/OpenServoCore/open-servo-core` project status before procurement; do not order SG90+OpenServoCore boards in flight-article quantity until upstream reaches a tagged/shippable hardware release. (`docs/TODO.md` §0.x) |
| OPTIGA™ Trust M pin-to-pad table + boot-latency figure, and `CAN-PERIPH-GW-1`/Flight Engineer schematic edits (REF-SENSOR-016) | `REFERENCES.md` REF-SENSOR-016, `avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md`, `avionics/kicad/FlightEngineer/FlightEngineer.md`, `avionics/WBS.md` §1.9.2 | Primary datasheet unreachable this session (`infineon.com`/`mouser.com`/`digikey.com`/`device.report` all blocked by network egress policy) — pin-to-pad table and any specific boot/power-up latency figure are unverified. `kicad-cli` is also not installed in this session, so even a verified schematic edit could not be ERC/DRC-checked. **No `.kicad_sch`/`.kicad_pcb` file has been touched for this change.** | Read the pin-to-pad table and any startup-timing figures off the primary datasheet (or a reachable mirror) from an environment with `infineon.com` access; build a clean-room KiCad symbol the same way `Observer_SLB9672_TPM` was built (datasheet tables, not vendor convention); confirm `kicad-cli` availability before editing `CAN-PERIPH-GW-1.kicad_sch`/`FlightEngineer.kicad_sch`, then run ERC. Do not fabricate pin numbers or a latency figure. (`avionics/WBS.md` §1.9.2) |
| Wing/nacelle Hall tilt encoder — sensor selection | `current-specification/bom_revS.csv` SKIPPER-TILT-ENC-PCB, `avionics/kicad/ENC-NACELLE-1.*`, `docs/TILT_SPAR_ANALYSIS.md` §1/§3.5/§8.1, `avionics/WBS.md` §1.9.1 | **RESOLVED 2026-07-19 (datasheets in repo).** MT6701 (Rev 1.9) was **rejected** — its datasheet §6 confirms it is **on-axis only** (Ø6 mm cyl magnet, off-axis misalignment ≤ 0.3 mm), so it cannot read the through-shaft off-axis; AS5600 has the same limit. Part selected = **AKM AK7455** (REF-SENSOR-008), which explicitly supports the Off-Axis (side-of-shaft) configuration; pinout/interface **verified** vs datasheet 200800064-E-00 and the schematic rebuilt (`kicad-cli` ERC 0-error). Interface is **SPI** (no off-axis absolute IC offers I²C). | **Electrical spec resolved.** Remaining, now scoped as bench/layout items (not "unverified part"): (1) off-axis flux 10–70 mT at the IC with the chosen ring/gap; (2) EEPROM INL calibration over −5..90° (AKM app support); (3) ERROR-pin push-pull vs open-drain; (4) QFN24 4×4 EP dims (EP left floating) + wing-pocket resize 3×3→4×4 (`HALL_*` in `wings_s1223_revo.scad`); (5) confirm the AKM product URL if the datasheet is re-hosted. TODO §0.8 / `airframe/wings-nacelles/WBS.md` §1.1.3.6. |
| Pilot's own inline "SLB9672" TPM symbol pin numbers | `avionics/kicad/Pilot/kicads/Pilot.kicad_sch` | Found 2026-07-26 while building Commo's TPM addition (which deliberately reused the separately-verified `Observer_SLB9670_TPM` clean-room symbol instead, precisely to avoid this defect): Pilot's own, independently-authored inline "SLB9670" symbol had pin numbers that did not match datasheet Revision 1.4 Tables 3–5. Not fixed at the time — out of scope for the CAN-FD/RS-485 trust-module task. **2026-08-01 SLB9670→SLB9672 migration:** the symbol/lib_id/value text was renamed to "SLB9672" (its pin *numbers* were left exactly as they were — this defect predates and is independent of the chip migration) so it now carries the same wrong-pin-number defect under the new chip's name (REF-SENSOR-011). Still not fixed — still out of scope. | Rebuild Pilot's TPM symbol from REF-SENSOR-011 using the same clean-room `parse_real_symbol`/pin-table method as `SLB9672_TPM`, or replace the instance with that verified symbol outright; re-run `kicad-cli sch erc` to confirm no regression against Pilot's existing 48-violation baseline. |
| VimDrones `ap_periph_pico` / ESC S50 concept-only inspiration, `CAN-PERIPH-GW-1` and CAN-PERIPH-GW-1's ESC-gateway deployment mode | `avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md` | **Not a citation defect — documented here for license-boundary auditability.** `CAN-PERIPH-GW-1` was built as a fleet-integrated remix of the *publicly documented product concept* at <https://dev.vimdrones.com/products/vimdrones_can_periph_pico/> and <https://dev.vimdrones.com/products/vimdrones_esc_s50/> (peripheral-bus CAN/servo gateway; per-ESC CAN telemetry). VimDrones' own KiCad source (`VimDrones/AM32_esc_development_board` on GitHub) is licensed GPL-3.0, which is incompatible with this project's CC-BY-4.0-or-better attribution baseline for derivative files — no VimDrones schematic, footprint, or geometry was copied; only the public product specification was used as design inspiration, and the entire trust-module implementation (MCU, TPM, isolators, netlist) is original clean-room work against TI/Infineon datasheets. | N/A — informational; see `CAN-PERIPH-GW-1.md` "Why VimDrones' concept but not VimDrones' hardware" |
| REF-CAD-004 misubisu hull model license stated as "CC BY 4.0" | REFERENCES.md REF-CAD-004, `current-specification/LICENSE_AND_ATTRIBUTION.md` §2, `README.md` Component License Map + Attribution quote, `docs/references/thingverse-serenity/LICENSE.txt` | **Incorrect attribution, found during TODO.md §0.9 licensing audit (2026-08-01).** The Thingiverse listing for Thing 7330462 is licensed **CC BY-SA 4.0** (ShareAlike), not plain CC BY 4.0 — the two earlier docs that had it right (`current-specification/LICENSE_AND_ATTRIBUTION.md` §2 "CC BY 4.0 SA", `docs/references/thingverse-serenity/LICENSE.txt`) used a garbled/non-standard label that also needed correcting. All four locations corrected to read "CC BY-SA 4.0". | REF-CAD-004 (corrected), REF-LIC-001 (CERN-OHL-W 2.0 Available Component treatment) |
| REF-AMS-001 (AMS 2301 electroplating standard) — cited, no catalog entry | `airframe/README.md` §Printing Specifications (hardened-steel nozzle plating context) | Found 2026-08-22 during TODO.md §0.10.2 documentation audit: `[REF-AMS-001]` is cited but `REFERENCES.md` has no matching entry — never guess a section/spec number (root `AGENTS.md` §4). | Look up SAE AMS2301 (or confirm the intended AMS spec number) via a validated URL and add a full `REF-AMS-001` catalog entry before citing it further. (`TODO.md` §0.x) |
| REF-WGS84-001 (WGS84 geodetic datum) — cited, no catalog entry | `gcs/README.md` §References (GPS navigation) | Found 2026-08-22, same audit pass. | Add a `REF-WGS84-001` entry citing NGA's WGS 84 standard (NGA.STND.0036) with a validated URL. (`TODO.md` §0.x) |
| REF-HAVERSINE-001 (Haversine great-circle distance formula) — cited, no catalog entry | `gcs/README.md` §References (`gcs/skipper/software/tracking/src/tracker.py` bearing/range calculation) | Found 2026-08-22, same audit pass. | Add a `REF-HAVERSINE-001` entry citing the formula's standard reference (e.g. Sinnott 1984, "Virtues of the Haversine," Sky & Telescope) with a validated URL. (`TODO.md` §0.x) |
| XO's own local TPM footprint (`QFN-32-1EP_4x4mm_P0.4mm_EP2.65x2.65mm`) | `avionics/kicad/XO/kicads/XO.kicad_pcb` (TPM footprint, renamed SLB9670→SLB9672 in the 2026-08-01 migration) | Found 2026-08-01 while migrating SLB9670→SLB9672: XO's placed TPM footprint uses a generic Renesas-sourced KiCad standard-library QFN-32 land pattern (4x4mm body, 0.4mm pitch, 2.65x2.65mm EP) that does not match either TPM's real package (both SLB9670 and SLB9672 are 5x5mm body, 0.5mm pitch, per their respective datasheets' Fig 6/Fig 3 recommended footprints) — i.e. `Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm`, the footprint used everywhere else this part appears (Observer, Commo, Flight Engineer, CAN-PERIPH-GW-1, Pilot). A separate, pre-existing defect from the wrong-pin-number one already tracked above; not fixed this session — out of scope for the chip-migration task (renamed text only; root `AGENTS.md` §5 requires footprint-position/DRC-driven moves to be referred to the user). | Replace XO's TPM footprint with `Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm` (refer the footprint swap to the user per `avionics/AGENTS.md` "Footprint and Component Placement"); re-run `kicad-cli pcb drc` to confirm no regression against XO's existing DRC baseline. |
