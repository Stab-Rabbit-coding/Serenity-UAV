# Malcolm GCS — Antenna Specification and FCC EIRP Compliance

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Revision:** Q1 (2026-06-10)

---

## Purpose

This document specifies the ground station antenna system for Malcolm GCS and demonstrates
FCC EIRP compliance for each radio link.  Malcolm operates at a safe distance from any
high-power RF sources; the link budget is sized to maintain reliable communications with
an aircraft whose onboard receivers may be desensed by proximity to commercial RF emitters.

---

## FCC Regulatory Baseline

| Link              | Regulation           | EIRP Limit (outdoor)    |
|-------------------|----------------------|-------------------------|
| SiK 915 MHz ISM   | FCC Part 15.247      | 30 dBm (1 W) omnidirectional; with directional antenna >6 dBi, reduce Tx 1 dB per 3 dB above 6 dBi |
| LoRa 915 MHz ISM  | FCC Part 15.247      | Same as SiK             |
| WiFi 5 GHz UNII-3 | FCC Part 15 UNII     | 30 dBm (5.725–5.850 GHz)|
| 49 MHz RCRS       | FCC Part 95 Subpart D| 20 dBm (100 mW) ERP     |
| Zigbee 2.4 GHz    | FCC Part 15.247      | 30 dBm                  |

> **Note:** Part 15.247 directional antenna rule (47 CFR 15.247(b)(3)(ii)): for antennas
> with gain > 6 dBi, the transmitter output power must be reduced 1 dB for every 3 dB that
> the antenna gain exceeds 6 dBi, such that total EIRP does not exceed 30 dBm.

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
> 14 dBi panel is in use.  This adjustment must be applied in `malcolm_config.yaml`.

---

## Link 4 — 49 MHz RCRS (AX.25, emergency backup)

| Parameter               | Value                                 |
|-------------------------|---------------------------------------|
| Module                  | XCVR-49MHZ-2 (via Cape-B-2 UART5)    |
| PA output power (max)   | +20 dBm (100 mW) — Part 95 ceiling    |
| Antenna                 | 1/4-wave base-loaded whip, ~0.94 m physical with loading coil; omnidirectional |
| Ground radials          | 4× 1/4-wave radials (star pattern, flat on mast base) |
| Coax loss (RG-58 2 m)   | −1.0 dB at 49 MHz                    |
| Antenna efficiency      | ~80% (loading coil insertion loss ~−1 dB) |
| **ERP (isotropic)**     | 20 − 1 − 1 = **18 dBm ERP** ✓ (≤20) |
| PA assessment           | No external PA.  XCVR-49MHZ-2 PA is already at the Part 95 ERP ceiling. |

> **FCC Part 95.635:** RCRS station transmitter power shall not exceed 100 milliwatts (mW)
> ERP.  Frequency accuracy ±0.005% per 47 CFR 95.655.

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
| 49 MHz RCRS   | 18 dBm ERP        | 20 dBm    | ✓ PASS |
| Zigbee 2.4 GHz| 22.5 dBm          | 30 dBm    | ✓ PASS |

**Conclusion:** No external power amplifiers are FCC-compliant for any Malcolm GCS link
in the standard configuration while maintaining compliance with directional antennas.
The link budget relies on directional antenna gain (not increased Tx power) to compensate
for aircraft-side receiver desense in hostile RF environments.

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
| 49 MHz whip          | RG-58     | 2 m    | SMA-male     | PL-259      | −1.0 dB |
| GNSS to PB2-I        | RG-316    | 0.3 m  | SMA-male     | SMA-male    | −0.2 dB |

All shield connections must be bonded to chassis ground at both ends to minimise
ground loop-induced interference.  Apply ferrite choke (Würth 742792512 or equivalent)
on coax shields at enclosure penetration points.
