# Malcolm GCS — Wiring and Connector Specification

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Revision:** R (2026-06-11)

---

## Overview

Malcolm's comms node (PB2-I + Cape-B-2 + Emma) connects to the host PC via USB
(CDC-ECM Ethernet-over-USB or USB serial) and to the antenna system via SMA RF cables.
The gimbal servos and AS5600 encoders connect to Cape-B-2 servo and I²C outputs.

---

## Host Computer Interface

| Signal          | Connector (PB2-I)     | Connector (host PC)  | Cable          | Notes |
|-----------------|----------------------|----------------------|----------------|-------|
| USB CDC-ECM     | USB-C (PB2-I J_USB)  | USB-A or USB-C       | USB 3.x, 2 m   | Provides Ethernet-over-USB (usb0); mavlink-router binds to 192.168.7.1:14550 |
| Debug console   | USB-C (PB2-I J_USB)  | USB-A (CP2102 adapter) | USB, 1 m     | Secondary serial console; /dev/ttyACM0 115200 8N1 |

---

## Power Connections

| Rail             | Source                        | Destination            | Wire Gauge | Notes |
|------------------|-------------------------------|------------------------|------------|-------|
| +5 V (bench)     | 5 V 3 A USB-C supply          | PB2-I J_USB or J_PWR   | 22 AWG     | Bench use only |
| +5 V (field)     | Field battery → 5 V 5 A BEC  | PB2-I J_PWR (JST-GH 2P)| 22 AWG    | Field use; BEC from 3S–6S LiPo field pack |
| +5 V gimbal rail | Same 5 V BEC                  | Cape-B-2 J_SERVO VCC   | 22 AWG     | Powers both gimbal servos from Cape-B-2 servo rail |

---

## RF Connections (SMA)

| Cape-B-2 Connector | Signal         | Cable Type | Antenna / Device              |
|--------------------|----------------|------------|-------------------------------|
| J_SMA_SIK          | SiK 915 MHz    | LMR-195    | ANT-915-OMNI (stationary) or → RF splitter → ANT-915-YAGI (gimbal) |
| J_SMA_LORA         | LoRa 915 MHz   | LMR-195    | ANT-915-OMNI (stationary) or → same RF splitter port             |
| J_SMA_WIFI         | WiFi 5 GHz     | LMR-195    | ANT-WIFI-PNL (gimbal-mounted flat panel) |
| Emma J2 (RP-SMA edge) | 49 MHz Part 15 | RG-58    | ANT-49MHZ (fixed mast whip)   |
| GNSS antenna port  | GNSS           | RG-316     | ANT-GNSS (u-blox active patch, GCS position fix) |
| Zigbee SMA (opt.)  | Zigbee 2.4 GHz | LMR-195    | ANT-ZIGBEE (fixed dipole)     |

> **Note:** When using the 9 dBi Yagi for both SiK and LoRa, insert a 2-way RF splitter
> (Minicircuits ZFSC-2-1W-S+ or equivalent, ≥20 dB port isolation, 800–1000 MHz).
> Only one link transmits at a time; receiver operation on both ports is simultaneous.

---

## Gimbal Connections (Cape-B-2 Servo and I²C)

### Servo Outputs

| Cape-B-2 Pin / Connector | Signal         | Gimbal Connection  | Wire Gauge |
|--------------------------|----------------|--------------------|------------|
| J_SERVO Ch.0 (PWM)       | Pan servo PWM  | Pan DS3218MG signal | 26 AWG     |
| J_SERVO Ch.1 (PWM)       | Tilt servo PWM | Tilt DS3218MG signal| 26 AWG     |
| J_SERVO VCC (6 V rail)   | Servo power    | Both servo +V pins  | 22 AWG     |
| J_SERVO GND              | Ground         | Both servo GND pins | 22 AWG     |

> Cape-B-2 servo rail is 6 V (from TPS54540 BEC on Kaylee PDB for aircraft, or from a
> standalone 6 V BEC on the GCS field power supply).  DS3218MG rated 6 V, 25 kg·cm.

### Encoder I²C Bus

| Cape-B-2 Pin    | Signal    | AS5600 Connection            | Notes |
|-----------------|-----------|------------------------------|-------|
| J_EXT_I2C SDA   | I²C SDA   | Both AS5600 SDA (shared bus) | 3.3 V logic; 2.2 kΩ pull-up to VDD on breakout |
| J_EXT_I2C SCL   | I²C SCL   | Both AS5600 SCL (shared bus) | AS5600 uses fixed address 0x36; use MCP23008 GPIO to select active encoder via OTP_ADDRESS pin |
| J_EXT_I2C VCC   | 3.3 V     | AS5600 VDD                   | 3.3 V supply from Cape-B-2 |
| J_EXT_I2C GND   | Ground    | AS5600 GND                   |       |

> **Address conflict:** Both AS5600 encoders share I²C address 0x36.  Use an MCP23008
> (already available on Cape-B-2) GPIO expander output to toggle the AS5600_ADDRESS_SELECT
> pin on each encoder, or use an I²C multiplexer (TCA9548A at 0x70) to isolate them.
> The latter is preferred; add TCA9548A between PB2-I I²C bus and encoder breakouts.

---

## Emma Sub-Module

Emma seats on Cape-B-2 J_XCVR header (JST-GH 6P).  No separate wiring required
for signal lines.  The RF RP-SMA connector on Emma routes to ANT-49MHZ via RG-58.

---

## Enclosure Penetrations (Field Use)

For field operations in an IP65 weatherproof enclosure, all connections exit the enclosure
through gasketed feedthroughs:

| Signal          | Penetration Type          | Notes |
|-----------------|---------------------------|-------|
| USB to host PC  | IP67 USB-C panel feedthrough | Cable gland + overmold |
| SiK SMA         | IP67 SMA bulkhead         | N-type to SMA adapter acceptable |
| LoRa SMA        | IP67 SMA bulkhead         |       |
| WiFi SMA        | IP67 SMA bulkhead         |       |
| 49 MHz RF       | IP67 PL-259 / SO-239      |       |
| GNSS SMA        | IP67 SMA bulkhead         |       |
| Power input     | IP67 XT30 panel mount     | +5 V field BEC output |
| Servo / I²C     | IP67 multi-pin panel conn.| 6-pin Amphenol AT series or equiv |

All shield braid continuations through bulkheads must maintain 360° contact at the
penetration point.  Apply ferrite clamp choke on all cables at the exterior exit point.

---

## Harness Summary

| Harness | Wire Count | Length | Material | Routing |
|---------|------------|--------|----------|---------|
| USB host link | 4 (USB) | 2 m | Shielded USB 3.x | Inside enclosure to host PC |
| Servo harness | 6 (2× 3-wire) | 1 m | 22/26 AWG silicone | Inside field kit to gimbal |
| Encoder I²C | 4 (shared) | 1 m | 26 AWG twisted pair | Inside field kit to gimbal |
| RF patch cables | 6 (coax) | 0.3–2 m | LMR-195 / RG-58 / RG-316 | Per antenna spec table |
