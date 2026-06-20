# REFERENCES.md — Serenity UAV Standards and Regulatory Reference Catalog

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Revision:** R1
**Last updated:** 2026-06-16

---

## Standards Vetting Policy

Every design specification that has any effect beyond cosmetic appearance **must** be vetted
against applicable industry standards and/or regulations before implementation.  This file
catalogs every standard and regulation that governs any aspect of this project.  It is the
authoritative index of:

1. The standard's designation and full title
2. A validated URL for official access (verified against the issuing body's website)
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

```
[REF-ID §section.subsection] — Short description of what is applied
```

Examples:
- `[REF-MIL-001 §4.1] Manchester II encoding at 1 Mbps, 78 Ω characteristic impedance`
- `[REF-FCC-001 §15.247(b)(3)(ii)] directional antenna gain > 6 dBi: reduce Tx 1 dB per 3 dB above 6 dBi`
- `[REF-NIST-001 §2.1] all messages digitally signed and authenticated`

When a standard has multiple applicable clauses, list them all:
```
[REF-IEC-001 Cl.5.5.2] and [REF-VDE-001 Cl.4.3] — 5 kV reinforced insulation barrier
```

---

## Part I — United States Federal Aviation Regulations

### REF-FAA-001: 14 CFR Part 48 — Registration and Marking Requirements for Small Unmanned Aircraft Systems

| Field | Value |
|---|---|
| **Issuing authority** | Federal Aviation Administration (FAA), U.S. Dept. of Transportation |
| **Current edition** | As amended through 2024 |
| **Official URL** | https://www.ecfr.gov/current/title-14/chapter-I/subchapter-F/part-48 |

**Sections applied in this project:**

| Section | Title | Application |
|---|---|---|
| §48.25 | Eligibility for registration | All UAS > 0.55 lbs (250 g) must be registered |
| §48.205(a) | Display of unique identifier | Registration number on exterior |
| §48.205(b)(1) | Legibility of identifier | Minimum 3-inch (76 mm) characters clearly visible |

**Used in:** `docs/REVN_BUILD_GUIDE_24IN.md`, `graphical-build-guide/decal_sheet.svg`,
`README.md`, `TODO.md`, `CLAUDE.md`

---

### REF-FAA-002: 14 CFR Part 107 — Small Unmanned Aircraft Systems

| Field | Value |
|---|---|
| **Issuing authority** | FAA, U.S. Dept. of Transportation |
| **Current edition** | As amended through 2024 |
| **Official URL** | https://www.ecfr.gov/current/title-14/chapter-I/subchapter-F/part-107 |

**Sections applied in this project:**

| Section | Title | Application |
|---|---|---|
| §107.3 | Definitions | "Small unmanned aircraft" definition applicable |
| §107.29 | Daylight operation | Must operate in daylight or civil twilight with anti-collision lighting |
| §107.51(a) | Maximum groundspeed | ≤ 87 kt (100 mph) |
| §107.51(b) | Maximum altitude | ≤ 400 ft AGL (unless within 400 ft of a structure) |
| §107.51(c) | Minimum visibility | ≥ 3 statute miles from pilot's control station |
| §107.51(d) | Minimum distance from clouds | 500 ft below, 2,000 ft horizontal |

**Used in:** `docs/REVN_BUILD_GUIDE_24IN.md`, `graphical-build-guide/build_guide_18_first_flight.svg`,
`README.md`, `TODO.md`, `CLAUDE.md`, `airframe/openscad/fuselage/bow_sensor_pod.scad`

---

### REF-FAA-003: 14 CFR §91.209 — Aircraft Lights

| Field | Value |
|---|---|
| **Issuing authority** | FAA |
| **Official URL** | https://www.ecfr.gov/current/title-14/chapter-I/subchapter-F/part-91/subpart-C/section-91.209 |
| **Companion guidance** | FAA Advisory Circular AC 107-2B (UAS operations under Part 107) — https://www.faa.gov/regulations_policies/advisory_circulars/ |

**Sections applied in this project:**

| Section | Title | Application |
|---|---|---|
| §91.209(a) | Position lights | Aircraft must display lighted red (port), green (starboard), and white (aft) position lights during night operations |
| §91.209(b) | Anti-collision light | Required for aircraft with a standard airworthiness certificate; applicable to UAS by AC 107-2B guidance |

**Applied to:** Navigation light subsystem — 6× WS2812C-2020 RGB LEDs (port red, starboard green,
aft white); controlled by FC4 node (Simon's medbay, Bay E).

**Used in:** `graphical-build-guide/build_guide_13_nav_lights.svg`, `docs/REVN_BUILD_GUIDE_24IN.md`,
`README.md`, `TODO.md`, `CLAUDE.md`

---

## Part II — United States Federal Communications Commission Regulations

> "Can't stop the signal." — Mr. Universe. We can, however, stay inside Part 15/95 limits while we transmit it.

### REF-FCC-001: 47 CFR §15.247 — Operation within the bands 902–928 MHz, 2400–2483.5 MHz, and 5725–5850 MHz

| Field | Value |
|---|---|
| **Issuing authority** | Federal Communications Commission (FCC) |
| **Official URL** | https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-C/section-15.247 |
| **Parent part** | 47 CFR Part 15 — https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15 |

**Sections applied in this project:**

| Section | Title | Application |
|---|---|---|
| §15.247(a)(1) | Frequency band | Operation in 902–928 MHz ISM band |
| §15.247(a)(2) | Frequency band | Operation in 2400–2483.5 MHz ISM band |
| §15.247(b)(3)(i) | Power limit | Max 1 W (30 dBm) conducted output for frequency-hopping and direct-sequence systems |
| §15.247(b)(3)(ii) | Directional antenna rule | For antennas > 6 dBi, reduce conducted Tx power 1 dB per 3 dB above 6 dBi, such that total EIRP ≤ 30 dBm |

**Applied to:** SiK 915 MHz MAVLink (RFD900x), LoRa 915 MHz (RFM95W), Zigbee 2.4 GHz (CC2652R7)

**Used in:** `gcs/malcolm/hardware/docs/malcolm_antenna_spec.md`, `TODO.md`, `CLAUDE.md`,
`avionics/firmware/dts/cape-b/k3-am6254-pocketbeagle2-serenity-cape-b2.dts`

---

### REF-FCC-002: 47 CFR Part 15 Subpart E — Unlicensed National Information Infrastructure Devices (UNII)

| Field | Value |
|---|---|
| **Issuing authority** | FCC |
| **Official URL** | https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-E |

**Sections applied in this project:**

| Section | Title | Application |
|---|---|---|
| §15.407(a)(3) | Power limits — UNII-3 | Maximum EIRP 30 dBm in the 5725–5850 MHz band |
| §15.407(c) | Spurious emissions | Applied to WL1837MOD 5 GHz output |

**Applied to:** TI WL1837MOD WiFi 5 GHz link (UNII-3 band); Tx power must be reduced to
17 dBm conducted when a 14 dBi directional antenna is connected to maintain EIRP ≤ 30 dBm.

**Used in:** `gcs/malcolm/hardware/docs/malcolm_antenna_spec.md`, `TODO.md`, `CLAUDE.md`

---

### REF-FCC-003: 47 CFR Part 15 §15.235 — Operation Within the Band 49.82–49.90 MHz

| Field | Value |
|---|---|
| **Issuing authority** | FCC |
| **Official URL** | https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-C/section-15.235 |

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
| Antenna restriction | Intentional radiator shall be designed so that no antenna other than that furnished by the responsible party (manufacturer) is used with it; a permanently attached antenna or a unique (non-standard) coupling satisfies this; **"the use of a standard antenna jack or electrical connector is prohibited"** even where the manufacturer permits user replacement of a broken antenna | §15.203 |
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
prohibited."* (47 CFR §15.203, https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-C/section-15.203).
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
`README.md`, `TODO.md`, `CLAUDE.md`, `docs/AVIONICS_PB2_REDESIGN.md`

---

## Part III — NIST Security Standards

### REF-NIST-001: NIST SP 800-207 — Zero Trust Architecture

| Field | Value |
|---|---|
| **Issuing authority** | National Institute of Standards and Technology (NIST), U.S. Dept. of Commerce |
| **Edition** | Final (August 2020) |
| **Official URL** | https://csrc.nist.gov/publications/detail/sp/800-207/final |
| **Direct PDF** | https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf |

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

**Used in:** `CLAUDE.md`, `README.md`, `docs/AVIONICS_PB2_REDESIGN.md`, `TODO.md`,
`airframe/openscad/fuselage/bow_sensor_pod.scad`

---

### REF-NIST-002: NIST SP 800-82 Rev 3 — Guide to Operational Technology (OT) Security

| Field | Value |
|---|---|
| **Issuing authority** | NIST |
| **Edition** | Revision 3 (September 2023) |
| **Official URL** | https://csrc.nist.gov/publications/detail/sp/800-82/3/final |
| **Direct PDF** | https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-82r3.pdf |

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

**Used in:** `CLAUDE.md`, `README.md`, `docs/AVIONICS_PB2_REDESIGN.md`

---

### REF-NIST-003: NIST SP 800-160 Vol 1 Rev 1 — Engineering Trustworthy Secure Systems

| Field | Value |
|---|---|
| **Issuing authority** | NIST |
| **Edition** | Volume 1 Revision 1 (November 2022) |
| **Official URL** | https://csrc.nist.gov/publications/detail/sp/800-160/vol-1-rev-1/final |
| **Direct PDF** | https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-160v1r1.pdf |

**Sections applied in this project:**

| Section | Title | Application |
|---|---|---|
| Chapter 3 | Systems Security Engineering Framework | Security-by-design applied throughout PCB layout, firmware architecture, and bus protocol selection |
| §3.3 | Stakeholder Needs and Requirements | Security requirements derived from mission profile (§ Mission profile items 1–3: rogue command detection, unsafe node detection, failover) |
| Appendix C | System Life Cycle Processes | Security considerations applied at every design phase |

**Used in:** `CLAUDE.md`

---

### REF-NIST-004: NIST SP 800-92 — Guide to Computer Security Log Management

| Field | Value |
|---|---|
| **Issuing authority** | NIST |
| **Edition** | Final (September 2006); Revision 1 in draft as of 2024 |
| **Official URL** | https://csrc.nist.gov/publications/detail/sp/800-92/final |

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
| **Official access** | DLA ASSIST QuickSearch: https://assist.dla.mil/ (search "MIL-STD-1553") |
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

## Part V — International Standards (ISO, IEC)

### REF-ISO-001: ISO 11898-1:2015 — Road Vehicles — Controller Area Network (CAN) — Part 1: Data Link Layer and Physical Signalling

| Field | Value |
|---|---|
| **Issuing authority** | International Organization for Standardization (ISO) |
| **Edition** | 2015, with Amendment 1:2020 (CAN FD) |
| **Catalog URL** | https://www.iso.org/standard/63648.html |
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
`avionics/firmware/dts/cape-a/k3-am6254-pocketbeagle2-serenity-cape-a2.dts`, `CLAUDE.md`

---

### REF-IEC-001: IEC 62368-1 Ed. 3.0 — Audio/Video, Information and Communication Technology Equipment — Part 1: Safety Requirements

| Field | Value |
|---|---|
| **Issuing authority** | International Electrotechnical Commission (IEC) |
| **Edition** | Third edition (2018-12) |
| **Official URL (purchase)** | https://webstore.iec.ch/en/publication/25285 |
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
`TODO.md`, `CLAUDE.md`, `airframe/openscad/fuselage/bow_sensor_pod.scad`

---

### REF-IEC-002: IEC 60825-1:2014+AMD1:2021 — Safety of Laser Products — Part 1: Equipment Classification and Requirements

| Field | Value |
|---|---|
| **Issuing authority** | International Electrotechnical Commission (IEC) |
| **Edition** | Second edition 2014-05, consolidated with Amendment 1 (2021-11) |
| **Official URL (purchase)** | https://webstore.iec.ch/en/publication/5587 |
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

**Applied to:** 12 mm OD crosshair-pattern laser module (5 mW, 650 nm) installed in the bow
sensor pod (bow_sensor_pod.scad, BOW-LASER mount, dome B ventral position); bore-sighted
at 30° below horizon on aircraft CL.

**Used in:** `airframe/openscad/fuselage/bow_sensor_pod.scad`,
`airframe/openscad/fuselage/head_shell24.scad`

---

### REF-VDE-001: VDE V 0884-11:2017-01 — Optocouplers for Use in Electrical Equipment — Test and Measurement Methods

| Field | Value |
|---|---|
| **Issuing authority** | Verband der Elektrotechnik Elektronik Informationstechnik e.V. (VDE), Germany |
| **Edition** | 2017-01 |
| **Official URL (search)** | https://www.vde-verlag.de/ (search "VDE V 0884-11") |
| **Alternative catalog** | https://www.beuth.de/ (DIN/VDE standards via Beuth Verlag) |
| **Note** | VDE V 0884-11 specifies test methodology for galvanic isolators (digital isolators, optocouplers). This standard defines the certification framework under which ISOW1044BDFMR and ADM2795EBRWZ are certified. |

**Clauses applied in this project:**

| Clause | Title | Application |
|---|---|---|
| Clause 4.3 | Reinforced Insulation (RI) | The insulation class applied on all inter-node transceivers in this design |
| Clause 5.2 | Partial discharge test (Vpd) | Confirms no partial discharge at rated working voltage |
| Clause 5.3 | Dielectric withstand test (Viso) | 5000 Vrms (7071 Vpk) hipot test for RI class — basis for the "5 kV" rating |

**Applied to:** Same isolation devices as REF-IEC-001.  VDE V 0884-11 compliance is verified
per individual component certifications in the ISOW1044BDFMR and ADM2795EBRWZ datasheets.

**Used in:** `README.md`, `docs/AVIONICS_PB2_REDESIGN.md`, `CLAUDE.md`,
`avionics/firmware/dts/cape-a/k3-am6254-pocketbeagle2-serenity-cape-a2.dts`,
`avionics/firmware/dts/cape-b/k3-am6254-pocketbeagle2-serenity-cape-b2.dts`

---

## Part VI — IEEE Standards

### REF-IEEE-001: IEEE 802.3-2022 — Ethernet (CSMA/CD Access Method and Physical Layer Specifications)

| Field | Value |
|---|---|
| **Issuing authority** | Institute of Electrical and Electronics Engineers (IEEE) |
| **Edition** | 2022 |
| **Official URL (purchase)** | https://ieeexplore.ieee.org/document/9844436 |

**Clauses applied in this project:**

| Clause | Title | Application |
|---|---|---|
| Clause 22 | Media Independent Interface (MII/RMII) | RMII interface between AM6254 CPSW3G and ADIN1300BCPZ / DP83825I PHYs |
| Clause 24 | 100BASE-TX PHY | 100 Mbps operation on all ring links |
| Clause 38 | Isolation transformer requirements | 1500 Vrms isolation per Ethernet port (Würth 749010012A meets this requirement) |

**Applied to:** Ethernet RSTP ring connecting all 8 nodes; CPSW3G hardware switch mode in AM6254.

**Used in:** `docs/AVIONICS_PB2_REDESIGN.md`, `CLAUDE.md`,
`avionics/firmware/dts/cape-a/k3-am6254-pocketbeagle2-serenity-cape-a2.dts`,
`avionics/firmware/dts/cape-b/k3-am6254-pocketbeagle2-serenity-cape-b2.dts`

---

### REF-IEEE-002: IEEE 802.11-2020 — Wireless LAN Medium Access Control (MAC) and Physical Layer (PHY) Specifications

| Field | Value |
|---|---|
| **Issuing authority** | IEEE |
| **Edition** | 2020 |
| **Official URL (purchase)** | https://ieeexplore.ieee.org/document/9363693 |

**Clauses applied in this project:**

| Clause | Title | Application |
|---|---|---|
| Clause 17 | OFDM PHY (802.11a/n/ac) | 5 GHz UNII-3 band operation for WL1837MOD |
| Clause 19 | 802.11n High Throughput PHY | 2.4 GHz and 5 GHz dual-band capability |

**Applied to:** TI WL1837MOD 802.11 a/b/g/n via SDIO interface; 5 GHz primary, 2.4 GHz fallback.

**Used in:** `docs/AVIONICS_PB2_REDESIGN.md`, `CLAUDE.md`

---

### REF-IEEE-003: IEEE 802.15.4-2020 — Low-Rate Wireless Networks

| Field | Value |
|---|---|
| **Issuing authority** | IEEE |
| **Edition** | 2020 |
| **Official URL (purchase)** | https://ieeexplore.ieee.org/document/9144691 |

**Clauses applied in this project:**

| Clause | Title | Application |
|---|---|---|
| Clause 10 | 2.4 GHz O-QPSK PHY | Zigbee radio layer (CC2652R7 optional backup mesh) |

**Used in:** `docs/AVIONICS_PB2_REDESIGN.md`, `README.md`, `CLAUDE.md`

---

## Part VII — ISA/IEC Industrial Cybersecurity Standards

### REF-ISA-001: ISA/IEC 62443-3-3:2013 — Industrial Automation and Control Systems Security — System Security Requirements and Security Levels

| Field | Value |
|---|---|
| **Issuing authority** | International Society of Automation (ISA) / International Electrotechnical Commission (IEC) |
| **Edition** | 2013 |
| **Official URL (ISA)** | https://www.isa.org/products/isa-iec-62443-3-3-2013-industrial-automation-and-c |
| **Official URL (IEC)** | https://webstore.iec.ch/en/publication/7032 |

**Security Requirements (SR) applied in this project:**

| SR | Title | Application |
|---|---|---|
| SR 3.1 | Communications Integrity | All messages (internal + external) carry TPM-bound HMAC; basis for authentication requirement |
| SR 3.2 | Malicious Code Protection | Firmware in eMMC; hardware write-blocked logs; TPM-measured boot |
| SR 4.2 | Use of Cryptography | TPM 2.0 (SLB9670) per node for key storage, attestation, and HMAC computation |
| SR 7.6 | Network and Security Configuration Settings | 5 kV galvanic isolation as physical network security hardening against EMI/RF injection |

**Used in:** `CLAUDE.md`, `docs/AVIONICS_PB2_REDESIGN.md`

---

## Part VIII — ICAO Standards

### REF-ICAO-001: ICAO Annex 2 — Rules of the Air

| Field | Value |
|---|---|
| **Issuing authority** | International Civil Aviation Organization (ICAO) |
| **Edition** | 10th edition (July 2005) with amendments |
| **Official URL (purchase)** | https://store.icao.int/en/annex-2-rules-of-the-air |
| **ICAO main site** | https://www.icao.int/ |
| **Note** | For US domestic operations, **14 CFR §91.209 (REF-FAA-003) is the directly enforceable regulation.** ICAO Annex 2 is cited for international context only and as the basis from which §91.209 derives. |

**Sections applied in this project:**

| Section | Title | Application |
|---|---|---|
| Chapter 3, §3.1.9 | Lights to be displayed by unmanned aircraft | Port red, starboard green, aft white position lights |

**Used in:** `graphical-build-guide/build_guide_13_nav_lights.svg`,
`graphical-build-guide/decal_sheet.svg`, `CLAUDE.md`, `docs/REVN_BUILD_GUIDE_24IN.md`

---

## Part IX — Protocol References

### REF-PROTO-001: AX.25 Link Access Protocol for Amateur Packet Radio

| Field | Value |
|---|---|
| **Authority** | Tucson Amateur Packet Radio (TAPR) / American Radio Relay League (ARRL) |
| **Edition** | Version 2.2 (July 1998) |
| **Official URL** | https://www.ax25.net/AX25.2.2-Jul%2098-2.pdf |
| **Note** | AX.25 is used as the frame format on the 49 MHz link. The RF portion of this link is governed by 47 CFR Part 15 §15.235 (REF-FCC-003), NOT the Amateur Radio Service and NOT Part 95 RCRS. AX.25 is a protocol choice; its use here does not require an amateur radio license because the 49.82–49.90 MHz band is a license-exempt, unlicensed Part 15 band. |

**Sections applied in this project:**

| Section | Title | Application |
|---|---|---|
| §6.2 | I Frame (Information Frame) | Data packet format for command uplink and telemetry downlink |
| §6.3 | S Frames | Flow control and error recovery on the 49 MHz link |

**Used in:** `avionics/firmware/dts/cape-b/k3-am6254-pocketbeagle2-serenity-cape-b2.dts`, `README.md`,
`docs/AVIONICS_PB2_REDESIGN.md`

---

### REF-PROTO-002: MAVLink v2 Protocol Specification

| Field | Value |
|---|---|
| **Authority** | ArduPilot / QGroundControl / MAVLink community (open standard) |
| **Edition** | v2.0 (current as of 2026) |
| **Official URL** | https://mavlink.io/en/ |
| **Note** | MAVLink is the application-layer protocol carried over the SiK 915 MHz link. It is an open, packet-framed protocol with CRC-16/MCRF4XX integrity check and optional signing (MAVLink v2 message signing uses HMAC-SHA256). |

**Applied to:** SiK MAVLink telemetry link (primary ground-to-air C2 channel).

**Used in:** `docs/AVIONICS_PB2_REDESIGN.md`, `TODO.md`

---

## Part X — AUVSI and Industry Frameworks

### REF-AUVSI-001: AUVSI Trusted Operator Program (TOP) and XCELLENCE Safety Standards

| Field | Value |
|---|---|
| **Issuing authority** | Association for Unmanned Vehicle Systems International (AUVSI) |
| **Official URL** | https://www.auvsi.org/trusted-operator-program |
| **Note** | AUVSI does not publish numbered engineering design standards (e.g., "AUVSI-XYZ"). The references to "AUVSI standards" in `CLAUDE.md` and `README.md` refer to AUVSI's published safety frameworks and guidelines for UAS design and operations. For numbered airframe engineering standards, applicable ASTM International standards from Committee F38 (Unmanned Aircraft Systems) should be identified. See TODO item for specific ASTM F38 standard identification. |

**ASTM F38 Committee UAS standards (identify applicable documents):**

| Standard | Title | Status |
|---|---|---|
| ASTM F3322 | Small Unmanned Aircraft System (sUAS) Battery Safety | Verify applicability to LiPo 6S pack |
| ASTM F3269 | Standard Practice for Methods to Safely Bound Flight Behavior of Unmanned Aircraft Systems | Verify applicability to failover design |
| ASTM F3003 | Standard Specification for Quality Assurance of a Small Unmanned Aircraft System | May apply to flight testing |

**Used in:** `CLAUDE.md`, `README.md`

---

## Part XI — FDA / CDRH Laser Product Regulations

### REF-FDA-001: 21 CFR Part 1040 — Performance Standards for Light-Emitting Products

| Field | Value |
|---|---|
| **Issuing authority** | U.S. Food and Drug Administration (FDA), Center for Devices and Radiological Health (CDRH) |
| **Current edition** | As amended through 2024 |
| **Official URL** | https://www.ecfr.gov/current/title-21/chapter-I/subchapter-J/part-1040 |
| **Parent subchapter** | 21 CFR Subchapter J — Radiological Health (https://www.ecfr.gov/current/title-21/chapter-I/subchapter-J) |
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
`airframe/openscad/fuselage/head_shell24.scad`, `TODO.md`

---

## Part XII — Sensor and Component Specifications

### REF-SENSOR-001: RunCam Nano 4 — 19 mm Nano Format FPV Camera Specification

| Field | Value |
|---|---|
| **Manufacturer** | RunCam Technology Co., Ltd. |
| **Product** | RunCam Nano 4 (or equivalent 19 mm Nano format camera) |
| **Official product page** | https://www.runcam.com/nano4 |
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
format compatibility (CAM_APER_D = 12 mm, CAM_BEZ_W = 21 mm, CAM_M2_PITCH = 14 mm).

**Used in:** `airframe/openscad/fuselage/bow_sensor_pod.scad`,
`airframe/openscad/fuselage/head_shell24.scad`

---

### REF-RFMOD-001: HopeRF RFM95W/96W/98W — Low Power Long Range Transceiver Module, Pin Description

| Field | Value |
|---|---|
| **Manufacturer** | Shenzhen Hope Microelectronics Co., Ltd. (HOPERF) |
| **Product** | RFM95W/96W/98W LoRa transceiver module, version 2.0 datasheet |
| **Official product page** | https://www.hoperf.com/modules/lora/RFM95W.html |
| **Datasheet URL** | https://www.hoperf.com/uploads/RFM96W-V2.0_1695351477.pdf (123 pp.) |
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
| **Official product page** | https://www.benewake.com/product/TFminiS.html |
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
`airframe/openscad/fuselage/head_shell24.scad`, `TODO.md`

---

## Removed / Superseded Citations

The following references appeared in earlier versions of project files but have been removed
because they were incorrectly attributed, unverifiable, or inapplicable.

| Old Citation | Where Found | Reason Removed | Replacement |
|---|---|---|---|
| "NIST SP 800-72 principles" (write-blocker design) | `README.md` §Patent Notice, line 382 | **Incorrect attribution.** NIST SP 800-72 (2004) is titled "Guidelines on PDA Forensics" — a forensic analysis guideline for personal digital assistants. It has no relation to hardware write-blocker design. No single NIST SP covers CPLD write-blocker design; the closest applicable standard is NIST SP 800-92 §4.4.2 (log data protection principles). | REF-NIST-004 (NIST SP 800-92 §4.4.2) |
| 47 CFR Part 95 RCRS (§95.635 ERP limit, §95.655 frequency accuracy, §95.639 PTT sequencing, "TDDS"/"LERS"/"27 channels" terminology) | `REFERENCES.md` REF-FCC-003, `gcs/malcolm/hardware/docs/malcolm_antenna_spec.md`, `CLAUDE.md`, `README.md`, `TODO.md`, `docs/AVIONICS_PB2_REDESIGN.md` | **Incorrect band classification.** Part 95 Subpart C (Radio Control Radio Service) covers only the 26–28 MHz, 72 MHz, and 75 MHz bands — it has no provisions for 49 MHz. The "TDDS"/"LERS"/27-channel terminology could not be traced to any verifiable Part 95 text. The 49.82–49.90 MHz band actually used by Emma is governed by 47 CFR Part 15 §15.235, an unlicensed intentional-radiator band, not a licensed/license-exempt personal radio service. | REF-FCC-003 (47 CFR Part 15 §15.235) |

---

## Open Standards Verification Items

The following citations in the codebase require verification before first flight.
Add verified section numbers to the relevant files and update this table.

| Citation | File | Issue | Action Required |
|---|---|---|---|
| §15.203 antenna restriction (Emma 49 MHz RF connector) | Emma (XCVR-49MHZ-2) hardware design, `avionics/kicad/Emma.md`, `avionics/kicad/Emma.kicad_sch`, `avionics/kicad/Emma.kicad_pcb`, `gcs/malcolm/hardware/docs/malcolm_wiring.md` | **Confirmed violation, resolved in design 2026-06-20.** §15.203 text ("...the use of a standard antenna jack or electrical connector is prohibited") binds the manufacturer/responsible party directly; being the manufacturer (rather than a third-party modifier) does not exempt this design. Emma's J2 previously used a generic SMA edge connector (Amphenol 132289), a standard jack; the carrier-current and professional-installation/on-site-measurement exceptions in §15.203 do not apply to Emma | **Resolved:** J2 changed to Amphenol 132289RP (RP-SMA, reverse-polarity counterpart of 132289, identical PCB footprint) across schematic, PCB footprint/silkscreen, and documentation, satisfying §15.203's "unique coupling" provision. Remaining step is the physical board re-spin/fabrication run to populate the new part — tracked in TODO.md §0.1 |
| 14 CFR Part 47 (aircraft registration marks) | `README.md`, `docs/REVN_BUILD_GUIDE_24IN.md` | 14 CFR Part 47 applies to manned aircraft registration; for UAS the applicable regulation is 14 CFR Part 48 §48.205 (display requirements) | Replace all Part 47 references with REF-FAA-001 (Part 48 §48.205) where the citation concerns UAS mark display |
| AUVSI "standards" (unnamed) | `CLAUDE.md`, `README.md` | No specific numbered AUVSI or ASTM standard cited | Identify applicable ASTM F38 committee standards for UAS airframe engineering and add to this catalog |
| IEC 62368-1 clause numbers | PCB layout (not yet complete) | PCB layout must verify creepage/clearance distances meet IEC 62368-1 Clause 5.5.2 requirements for 5 kV reinforced insulation; this cannot be verified until PCB layout is complete | Verify during Wash and Zoë PCB layout review (see TODO.md §1.4) |
