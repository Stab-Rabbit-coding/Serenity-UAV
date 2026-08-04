# Skipper GCS — Antenna Specification and FCC EIRP Compliance

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0
**Revision:** R (2026-06-11)

---

## Purpose

This document specifies the ground station antenna system for Skipper GCS and demonstrates
FCC EIRP compliance for each radio link.  Skipper operates at a safe distance from any
high-power RF sources; the link budget is sized to maintain reliable communications with
an aircraft whose onboard receivers may be desensed by proximity to commercial RF emitters.

---

## FCC Regulatory Baseline

> **Standards citations:** All regulations in this document are from the current
> Electronic Code of Federal Regulations (eCFR) at ecfr.gov.  See `REFERENCES.md`
> for full catalog entries with URLs and section-level detail.
>
> **Correction (2026-06-20):** The 49 MHz Commo link was previously cited against
> 47 CFR Part 95 (Radio Control Radio Service, RCRS).  Part 95 Subpart C RCRS covers
> only the 26–28 MHz, 72 MHz, and 75 MHz bands — it does not include 49 MHz.  The
> 49.82–49.90 MHz band is governed instead by **47 CFR Part 15 §15.235**, an
> unlicensed intentional-radiator rule with a **field-strength** limit (not an
> EIRP/ERP limit).  See Link 4 below for the corrected compliance analysis.

| Link              | Regulation                                        | REF-ID          | EIRP Limit (outdoor)    |
|-------------------|---------------------------------------------------|-----------------|-------------------------|
| SiK 915 MHz ISM   | 47 CFR §15.247(b)(3)(i) and §15.247(b)(3)(ii)    | REF-FCC-001     | 30 dBm; with directional antenna >6 dBi, reduce Tx 1 dB per 3 dB above 6 dBi |
| LoRa 915 MHz ISM  | 47 CFR §15.247(b)(3)(i) and §15.247(b)(3)(ii)    | REF-FCC-001     | Same as SiK             |
| WiFi 5 GHz UNII-3 | 47 CFR §15.407(a)(3)                              | REF-FCC-002     | 30 dBm EIRP (5.725–5.850 GHz)|
| 49 MHz Part 15    | 47 CFR §15.235 — field strength ≤ 10,000 µV/m at 3 m | REF-FCC-003 | ≈ −15.2 dBm (≈ 30 µW) EIRP-equivalent — see Link 4 |
| Zigbee 2.4 GHz    | 47 CFR §15.247(b)(3)(i)                           | REF-FCC-001     | 30 dBm                  |

> **Part 15.247 directional antenna rule** [REF-FCC-001 §15.247(b)(3)(ii)]: for intentional
> radiators using directional antennas with gain > 6 dBi, the conducted transmitter output
> power must be reduced 1 dB for every 3 dB that the antenna gain exceeds 6 dBi, such that
> total EIRP does not exceed 30 dBm.

---

## Link 1 — SiK 915 MHz (MAVLink primary)

| Parameter               | Value                                 |
|-------------------------|---------------------------------------|
| Module                  | RFD900x (or SiK-compatible 915 MHz)   |
| Tx output power         | +20 dBm (100 mW) — module maximum     |
| Short-range antenna     | 5 dBi rubber duck omni, RP-SMA        |
| Directional antenna     | 9 dBi Yagi, RP-SMA, gimbal-mounted    |
| Coax loss (LMR-195 1 m) | −0.5 dB                               |
| **Omni EIRP**           | 20 + 5 − 0.5 = **24.5 dBm** ✓ (≤30)  |
| **Yagi EIRP**           | 20 + 9 − 0.5 = **28.5 dBm** ✓ (≤30) |
| Yagi compliance check   | Gain 9 dBi > 6 dBi; excess = 3 dBi; required Tx reduction = 1 dB; 20 − 1 + 9 − 0.5 = 27.5 dBm ✓ |
| PA assessment           | No PA needed or FCC-permitted with directional antenna while staying compliant |

---

## Link 2 — LoRa 915 MHz (MAVLink alternate)

| Parameter               | Value                                 |
|-------------------------|---------------------------------------|
| Module                  | RFM95W on Cape-B-2                    |
| Tx output power         | +20 dBm (firmware configurable 2–20 dBm)|
| Short-range antenna     | 5 dBi rubber duck omni, RP-SMA        |
| Directional antenna     | 9 dBi Yagi, RP-SMA, gimbal-shared with SiK via RF splitter |
| Coax + splitter loss    | −0.5 dB coax + −3.5 dB splitter = −4 dB |
| **Omni EIRP**           | 20 + 5 − 4 = **21 dBm** ✓            |
| **Yagi EIRP (shared)**  | 20 + 9 − 4 = **25 dBm** ✓            |
| PA assessment           | No PA needed.  Splitter loss provides additional compliance margin. |

> **Note on SiK/LoRa shared Yagi:** An RF splitter/combiner (−3.5 dB insertion loss) allows
> a single Yagi to serve both SiK and LoRa.  Only one link transmits at a time.  The splitter
> must have adequate isolation (≥20 dB) between ports to prevent cross-modulation.

---

## Link 3 — WiFi 5 GHz (high-bandwidth data / telemetry)

| Parameter               | Value                                 |
|-------------------------|---------------------------------------|
| Module                  | TI WL1837MOD on Cape-B-2              |
| Tx output power (max)   | +18 dBm (UNII-3, firmware limit)      |
| Directional antenna     | 14 dBi flat panel, RP-SMA, gimbal-mounted |
| Coax loss (LMR-195 1 m) | −1.0 dB (higher loss at 5 GHz)       |
| **Panel EIRP (raw)**    | 18 + 14 − 1 = 31 dBm — EXCEEDS 30 dBm limit |
| **Required Tx power**   | 30 − 14 + 1 = **17 dBm** (reduce by 1 dB from max) |
| **Panel EIRP (adj.)**   | 17 + 14 − 1 = **30 dBm** ✓ (at limit)|
| PA assessment           | No PA permitted.  Tx power must be set to ≤17 dBm in firmware when 14 dBi panel is connected. |

> **Action item:** Configure WL1837MOD Tx power to 17 dBm (vs. default 18 dBm) when the
> 14 dBi panel is in use.  This adjustment must be applied in `skipper_config.yaml`.

---

## Link 4 — 49 MHz Part 15 §15.235 (AX.25, emergency backup)

> **Regulatory correction (2026-06-20):** This link was previously documented under
> 47 CFR Part 95 RCRS with an assumed 100 mW (+20 dBm) ERP ceiling.  Part 95 RCRS does
> not cover 49 MHz; the governing rule is **47 CFR §15.235**, which limits the
> *field strength* of the fundamental emission to ≤ 10,000 µV/m at 3 m — not an
> EIRP/ERP power figure directly.  Converting that field-strength limit to an
> equivalent EIRP via the standard far-field relation EIRP = E²·4πd²/Z₀ (Z₀ = 377 Ω
> free-space impedance) gives:
>
> EIRP_max = (0.01 V/m)² × 4π × (3 m)² / 377 Ω ≈ **30 µW ≈ −15.2 dBm**
>
> This is **≈ 35 dB lower** than the 100 mW previously assumed for this link.

| Parameter               | Value                                 |
|-------------------------|---------------------------------------|
| Module                  | Commo (via Cape-B-2 UART5)    |
| PA output power, as-designed | +20 dBm (100 mW) — **non-compliant with §15.235**, see below |
| Antenna                 | 1/4-wave base-loaded whip, ~0.94 m physical with loading coil; omnidirectional, ~0 dBi assumed |
| Ground radials          | 4× 1/4-wave radials (star pattern, flat on mast base) |
| Coax loss (RG-58 2 m)   | −1.0 dB at 49 MHz                    |
| Antenna efficiency      | ~80% (loading coil insertion loss ~−1 dB) |
| **EIRP at PA = +20 dBm** | 20 + 0 − 1 − 1 = **18 dBm (≈ 63 mW)** — exceeds the §15.235 limit by ≈ 33 dB |
| §15.235 EIRP ceiling     | **≈ −15.2 dBm (≈ 30 µW)** |
| **PA output required for compliance** | −15.2 − 0 + 1 + 1 = **≈ −13.2 dBm (≈ 48 µW)** conducted |
| PA assessment           | Commo's PA must be firmware-limited to ≈ −13 dBm (≈ 48 µW) conducted, not +20 dBm, to meet §15.235.  No external PA is permitted on this link in any configuration. |

> **§15.235 field strength limit** [REF-FCC-003 §15.235(a)]: fundamental emission field
> strength ≤ 10,000 µV/m at 3 m (average detector); peak limits of §15.35 also apply.
> Band-edge attenuation and out-of-band emission limits per §15.235(b)/§15.209.  Antenna
> restriction per §15.203 — text: *"the use of a standard antenna jack or electrical
> connector is prohibited."*  **§15.203 violation resolved in design (2026-06-20):**
> Commo's RF port previously used a generic SMA edge connector (Amphenol 132289), a standard
> jack.  §15.203 binds the manufacturer/responsible party directly — being the manufacturer
> does not exempt this design, and the section's narrow exceptions (carrier-current devices;
> professionally installed radiators measured at the install site) do not apply here.  J2 is
> now specified as Amphenol **132289RP** (RP-SMA, reverse-polarity counterpart of 132289 with
> identical PCB footprint), satisfying §15.203's "unique coupling" provision —
> `skipper_wiring.md` line 86 updated accordingly.  See `REFERENCES.md` "Open Standards
> Verification Items" for status; physical board re-spin to populate 132289RP is pending.
>
> **Design impact — open item:** At the compliant ≈ 48 µW conducted power level, this
> link's realistic range drops from the "miles" implied by the original 100 mW RCRS
> assumption to likely well under a quarter mile (exact figure depends on receiver
> sensitivity and ground-wave propagation at 49 MHz; not yet analyzed).  This
> contradicts the link's design role as River's resilient long-range backup comms path
> (see `avionics/AGENTS.md` "Node Workload Balancing and PACE Failover").  Re-architecting this link — e.g. a
> different frequency or a licensed service that permits higher power near 49 MHz — is
> tracked as an open item in `TODO.md` §0.1 and is **not resolved by this revision**;
> the PA power ceiling above reflects what §15.235 actually permits today, not a
> redesign of the link.

---

## Link 5 — Zigbee 2.4 GHz (mesh backup, optional)

| Parameter               | Value                                 |
|-------------------------|---------------------------------------|
| Module                  | CC2652R7 (optional, via Cape-B-2)     |
| Tx output power         | +20 dBm (module maximum)              |
| Antenna                 | 3 dBi rubber duck dipole, RP-SMA      |
| Coax loss               | −0.5 dB                               |
| **EIRP**                | 20 + 3 − 0.5 = **22.5 dBm** ✓ (≤30) |
| PA assessment           | No PA needed.                         |

---

## Summary EIRP Table

| Link          | EIRP (worst case) | FCC Limit | Status |
|---------------|-------------------|-----------|--------|
| SiK 915 MHz   | 27.5 dBm (Yagi)   | 30 dBm    | ✓ PASS |
| LoRa 915 MHz  | 25.0 dBm (Yagi)   | 30 dBm    | ✓ PASS |
| WiFi 5 GHz    | 30.0 dBm (panel, adjusted) | 30 dBm | ✓ PASS (Tx reduced to 17 dBm) |
| 49 MHz Part 15| ≈ −13.2 dBm PA req'd (≈ 48 µW), vs. ≈ 18 dBm EIRP at as-designed +20 dBm PA | ≈ −15.2 dBm (≈ 30 µW) EIRP | ✗ NON-COMPLIANT as designed — PA must be firmware-limited to ≈ −13 dBm; see Link 4 |
| Zigbee 2.4 GHz| 22.5 dBm          | 30 dBm    | ✓ PASS |

**Conclusion:** No external power amplifiers are FCC-compliant for any Skipper GCS link
in the standard configuration while maintaining compliance with directional antennas.
The link budget relies on directional antenna gain (not increased Tx power) to compensate
for aircraft-side receiver desense in hostile RF environments.  **Exception:** the 49 MHz
Commo link is not compliant as currently designed — Commo's PA must be firmware-limited from
+20 dBm to ≈ −13 dBm to satisfy §15.235, which severely curtails this link's usable range
versus its intended role as a resilient long-range backup; see Link 4 and TODO.md §0.1.

---

## Antenna Hardware Specifications

| Ref         | Description                           | Connector | Notes                       |
|-------------|---------------------------------------|-----------|-----------------------------|
| ANT-915-OMNI| 5 dBi 915 MHz omnidirectional rubber duck | RP-SMA | One for SiK, one for LoRa; short-range / stationary operations |
| ANT-915-YAGI| 9 dBi 915 MHz Yagi directional        | RP-SMA    | Gimbal-mounted; shared SiK+LoRa via splitter |
| ANT-WIFI-PNL| 14 dBi 5 GHz flat panel               | RP-SMA    | Gimbal-mounted; WiFi only   |
| ANT-49MHZ   | 49 MHz 1/4-wave loaded whip ~0.94 m  | PL-259    | Fixed on mast base; omnidirectional |
| ANT-ZIGBEE  | 3 dBi 2.4 GHz rubber duck dipole      | RP-SMA    | Fixed; optional             |
| ANT-GNSS    | u-blox ANN-MB-00 active GNSS patch    | SMA       | GCS position fix for tracker.py |

---

## Coax and Adapter Specifications

| Run                  | Cable     | Length | Connector A  | Connector B | Loss  |
|----------------------|-----------|--------|--------------|-------------|-------|
| SiK to gimbal Yagi   | LMR-195   | 1 m    | SMA-male     | SMA-female  | −0.5 dB |
| LoRa to splitter     | LMR-195   | 0.5 m  | SMA-male     | SMA-female  | −0.3 dB |
| Splitter to gimbal   | LMR-195   | 0.5 m  | SMA-male     | SMA-female  | −0.3 dB |
| WiFi to gimbal panel | LMR-195   | 1 m    | RP-SMA-male  | RP-SMA-female | −1.0 dB |
| 49 MHz whip          | RG-58     | 2 m    | RP-SMA-male  | PL-259      | −1.0 dB |
| GNSS to PB2-I        | RG-316    | 0.3 m  | SMA-male     | SMA-male    | −0.2 dB |

All shield connections must be bonded to chassis ground at both ends to minimise
ground loop-induced interference.  Apply ferrite choke (Würth 742792512 or equivalent)
on coax shields at enclosure penetration points.
