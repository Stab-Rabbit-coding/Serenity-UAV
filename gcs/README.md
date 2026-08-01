# Serenity UAV — Ground Control Station (Malcolm)

**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0  
**Current design revision:** Rev S (2026-07-04)

> Ground control station (GCS) hardware and software for Serenity UAV: five-radio comms node
> (Wi-Fi, Zigbee, SiK 915 MHz, 49 MHz, LoRa), antenna gimbal tracking, and QGroundControl
> integration for autonomous mission planning and flight telemetry.

## System Overview

**Malcolm** (named after Capt. Malcolm Reynolds) is a **PocketBeagle2 Industrial** compute module
running a **5-radio transceiver suite** and **antenna tracking gimbal** for command-and-control
of the Serenity UAV across multiple RF links and extended ranges.

### Hardware Architecture

| Component | Role | Specs |
|-----------|------|-------|
| **PocketBeagle2-I** | Comms SBC | Cortex-A53 dual-core, 1 GB RAM, eMMC (OS), μSD (logging) |
| **Zoë Cape-B-2** | Radio interface | Wi-Fi adapter, SiK 915 MHz RFD900x, 49 MHz transceiver (via UART), LoRa expansion header |
| **Emma Cape-X-1** | Extended 49 MHz/LoRa | Dual 49 MHz + LoRa (standby remote link for failsafe) |
| **Antenna gimbal** | RF tracking | 2-axis (az/el) servo-driven platform, encoder feedback, 3D-printed mount |
| **Enclosure** | Weatherproofing | 3D-printed case (CF-PETG), aluminum heat sink, IP54 dust/splash rating |

### Comms Paths (5 Independent Links)

**Primary/Secondary hierarchy per mission phase:**

- **Phase Malcolm-1:** PB2-I + Zoë only (Wi-Fi 5 GHz primary, SiK 915 MHz secondary)
  - Development flights, short-range command & telemetry
  - Range: Wi-Fi ~500 m, SiK ~5 km typical (line-of-sight)

- **Phase Malcolm-2:** Add Emma (49 MHz + LoRa)
  - Extended autonomous mission comms
  - 49 MHz: Part 15 §15.235 unlicensed, ~30 µW EIRP, range ~5 km (forward/aft link for aircraft)
  - LoRa: Sub-GHz backup, low-power (~10 dBm), range ~10+ km open field

- **Phase Malcolm-3 & 4:** Full gimbal tracking + multi-link coordination
  - Gimbal servo control via GPIO (azimuth/elevation from tracking software)
  - Automatic link-switching based on signal strength
  - Remote antenna orientation for optimal SNR across swaps

All external messages are **signed and authenticated** via TPM-bound keys; every command is
verified before ground-station relay to aircraft.

## Software Components

### **mal_comms** (PB2-I Firmware)

Located in `firmware/pb2i/src/`:

- **Radio initialization:** configure all 5 transceiver interfaces (Wi-Fi driver, SiK/UART,
  49 MHz module, LoRa SPI)
- **CAN FD interface:** bridge aircraft CAN to radio payloads (MAVLink, 49 MHz frames, telemetry)
- **Link arbitration:** rate-limit and prioritize messages across 5 concurrent paths; failover
  to backup link on primary loss
- **TPM attestation:** sign every outbound packet with PB2-I node key (SLB9670 TPM 2.0)
- **Log forwarding:** relay aircraft's signed flight logs (via CAN FD) to GCS μSD with
  timestamp and signature verification

### **Ground Host Software** (Phase Malcolm-3+)

Located in `firmware/host/`:

- **QGroundControl integration:** MAVLink endpoint via `mavlink-router` daemon
- **Telemetry feed:** `telemetry_feed.py` — parse aircraft CAN/MAVLink frames, format for QGC
- **Gimbal control:** `gimbal_ctrl.py` — servo PWM output (azimuth/elevation) based on aircraft
  bearing/elevation from autopilot
- **Target tracking:** `tracker.py` — visual tracking of aircraft via slant-range, elevation
  angle, heading cross-wind compensation
- **Link monitor:** `link_monitor.py` — RSSI/SNR telemetry per radio; automatic switchover on
  loss

### **Malcolm Configuration** (`malcolm_config.yaml`)

Runtime configuration for comms priorities:

```yaml
xcvr_49mhz:
  enabled: true
  uart_port: /dev/ttyS1
  baud_rate: 9600
  power_limit_dbm: -13  # Part 15 §15.235 compliance

wifi:
  enabled: true
  ssid: "serenity-gcs"
  frequency: 5200  # MHz

zigbee:
  enabled: true
  channel: 20
  pan_id: 0xabcd

sik_915mhz:
  enabled: true
  air_speed: 115200
  tx_power: 23  # dBm

lora:
  enabled: false  # Phase Malcolm-3+
  frequency: 915000000
  bandwidth: 125000
  sf: 12
```

## Antenna Gimbal

### Hardware Design

- **Actuators:** 2× SG90 servo motors (azimuth + elevation)
- **Sensor feedback:** dual-axis potentiometric encoders (5 kΩ) for position readback
- **Mechanical:** aluminum pivot bracket, ball bearings, flexures for smooth slew
- **Antenna mount:** dual RP-SMA connectors (49 MHz + 915 MHz co-located for diversity)
- **Control interface:** GPIO PWM (pin mapping in device-tree overlay)

### Tracking Algorithm (`tracker.py`)

- Input: aircraft (lat, lon, alt) + aircraft heading / GCS (lat, lon, alt)
- Compute: slant range (Haversine), elevation angle (atan2 altitude diff, horizontal dist),
  bearing (atan2 E/N components)
- Output: servo PWM commands (azimuth 0–180°, elevation 0–90°) + tracking error (degrees off-boresight)

## Hardware Specifications

| Parameter | Value |
|-----------|-------|
| **Dimensions (enclosure)** | 250 mm × 180 mm × 80 mm (printed CF-PETG) |
| **Mass (complete, no gimbal)** | ~600 g |
| **Mass (with gimbal)** | ~800 g |
| **Power input** | USB-C (5V, 2A) or LiPo 2S/3S connector |
| **RF range (typical, line-of-sight)** | Wi-Fi 500 m; SiK 5 km; 49 MHz 5+ km; LoRa 10+ km |
| **Antenna diversity** | Omnidirectional base (sealed bulkhead, quarter-wave), gimbal-tracked (RP-SMA, ±45° slew) |
| **Operating temperature** | 0–45°C (enclosure sealed, passive convection) |

## Assembly & Setup (Phase Malcolm-1)

1. **Hardware assembly:**
   - 3D-print enclosure halves, heat-sink plate, gimbal mount; validate tolerances
   - Solder PB2-I + Zoë-Cape + USB/power connectors
   - Install TPM 2.0 (SLB9670) via SPI header; test attestation

2. **Software provisioning:**
   - Flash Debian Linux to PB2-I eMMC (from buildroot or official PocketBeagle images)
   - Apply device-tree overlay (`malcolm_device_tree.dtso`) for Zoë cape support
   - Build and install `mal_comms` firmware (CMake, cross-compile for ARM)
   - Install Python dependencies (`mavlink`, `cryptography`, `gps`)

3. **Field commissioning:**
   - Ground test: verify all 5 radio links; check MAVLink heartbeat in QGC
   - Gimbal test: manual azimuth/elevation servo sweep; record encoder feedback
   - Link margin test: range walk (open field, 1 km radius) for each radio path
   - Failover test: simulate RF loss on primary link; confirm automatic switchover

## Testing & Validation

| Test | Success Criteria | Phase |
|------|------------------|-------|
| Multi-link comms bench | All 5 radios TX/RX heartbeats simultaneously | Malcolm-1 |
| QGC integration | MAVLink telemetry live in QGC, no dropouts >1s | Malcolm-1 |
| Range walk | Measured RSSI/SNR vs. distance for each radio | Malcolm-2 |
| Link arbitration | Switchover to secondary link <200 ms on primary loss | Malcolm-2 |
| Gimbal accuracy | Tracking error <5° at 1 km range | Malcolm-3 |
| Cold-start acquisition | Aircraft lock within 10 s of antenna slew start | Malcolm-3 |
| End-to-end mission | 10-waypoint autonomous flight, gimbal following, telemetry logged | Malcolm-4 |

## Documentation Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | GCS subsystem policy: hardware spec, firmware architecture, testing matrix |
| `WBS.md`, `TODO.md` | Work breakdown: hardware design, Malcolm PB2-I setup, host PC software, tracking integration |
| `firmware/pb2i/src/` | PocketBeagle2 + Zoë/Emma cape firmware (C/Linux) |
| `firmware/host/` | Ground host Python scripts (telemetry, gimbal control, tracking) |
| `hardware/` | 3D-printed enclosure SCAD, gimbal mount CAD, antenna connector design |
| `tests/` | Unit tests for tracking algorithm, link-arbitration logic |

## References

- **Regulatory:** [REF-FCC-001] 47 CFR Part 15, [REF-FCC-003] §15.235 (49 MHz unlicensed)
- **Comms:** [REF-IEEE-001] IEEE 802.15.4 (ZigBee), [REF-IEEE-002] IEEE 802.11 (Wi-Fi)
- **Navigation:** [REF-WGS84-001] WGS84 geodetic datum (GPS), [REF-HAVERSINE-001] Haversine
  formula (great-circle distance)

See root [`REFERENCES.md`](../REFERENCES.md) for complete reference catalog.

## License

**Hardware (CAD, schematics, Gerbers, 3D-printed parts):** CERN-OHL-W 2.0  
**Firmware (C source, Python scripts, device-tree overlays):** CC BY 4.0  
**Documentation:** CC BY 4.0

See root [`LICENSE`](../LICENSE) and [`docs/attribution_and_licensing.md`](../docs/attribution_and_licensing.md)
for full licensing details.

---

*"I aim to misbehave." — Capt. Malcolm Reynolds*
