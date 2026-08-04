# Serenity UAV — Ground Control Station (Skipper) Work Breakdown Structure

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0
**Current design revision:** Rev S (2026-07-04)

> **Detail-holder for the root WBS.** The repository-root [`TODO.md`](../TODO.md)
> is a compact index — headings, subheadings, and short (<=70-char) checkbox items
> only, per root `AGENTS.md`. This file carries the full task detail for the WBS
> branches root indexes below. Close an item here first, then check it off in the
> root index as a commit prerequisite (root `AGENTS.md` "Revisions and Version
> Control"). **&#9733; = the branch is on the critical path to first flight (Phase 5).**

*"I aim to misbehave. — Capt. Skipper Reynolds"*

---

## Owned WBS branches — open-item summary

| Master § | Branch | Open | First flight |
|----------|--------|-----:|:------------:|
| §4.5 | 4.5 — Ground Control (Skipper / CAPT Reynolds) | 34 | &#9733; |
| | **Total open (this subsystem)** | **34** | |

---


## §4.5 — Ground Control (Skipper / CAPT Reynolds) &#9733;

*(root `WBS.md` §4.5)*

- [ ] **Create Skipper host computer specification** (`gcs/skipper/hardware/docs/skipper_host_spec.md`):
    minimum x86\_64 Debian Linux, 8 GB RAM, 256 GB SSD, USB 3.0+; ruggedized laptop
    (IP54 or better) for field use.  Document recommended models and any BIOS/driver notes.
- [ ] **Skipper field enclosure — print and fit-check** `gcs/skipper/hardware/enclosure/openscad/skipper_field_enclosure.scad`:
    export STL (`openscad -o skipper_field_enclosure_body.stl ... -D RENDER_MODE=0`);
    verify PCB standoff spacing matches Cape-B-2 55×35 mm mounting hole pattern in slicer;
    run mesh validation; print body + lid in PETG (IP65 gasket groove accepts 3 mm EPDM cord).
    **Add to Phase Skipper-1 print schedule.**
- [ ] **Gimbal STL generation and mesh verification** — for each of the three SCAD files:
    - `skipper_gimbal_pan.scad` → `skipper_gimbal_pan_base.stl` + `skipper_gimbal_pan_turret.stl`
    - `skipper_gimbal_tilt.scad` → `skipper_gimbal_tilt_yoke.stl`
    - `skipper_gimbal_mount.scad` → `skipper_gimbal_mount.stl`
    Print in CF-PETG (0.15 mm, 40% infill, 4 walls).  Verify bearing pocket diameters
    (6804: 32 mm OD housing; MF104ZZ: 10 mm OD housing) against bearing datasheets before printing.
- [ ] **Gimbal servo wind-load torque check** — compute worst-case wind torque on a 9 dBi Yagi
    (~1.2 m boom, ~0.04 m² front area) at 30 kt crosswind.  Verify DS3218MG (25 kg·cm @ 6 V)
    provides ≥2× safety factor.  Document in `gcs/skipper/hardware/docs/skipper_power_budget.md`.
- [ ] **Procure Skipper comms node hardware:**
    - 1× PocketBeagle 2 Industrial (AM6254) — same DigiKey PN 2820-100003007-ND
    - 1× Cape-B-2 (XO) PCB — order 1 additional unit when placing aircraft PCB order at JLCPCB
    - 1× Commo sub-module — order 1 additional unit with aircraft Commo order
    - 1× 64 GB microSD (Samsung or equiv, same as aircraft CN nodes)
    - 1× 5 V / 5 A switching BEC (Pololu D24V50F5 or equiv)
    - 1× 6 V / 2 A servo BEC (Pololu D24V22F6 or equiv)
- [ ] **Procure antenna hardware** per `gcs/skipper/hardware/docs/skipper_antenna_spec.md`:
    - 2× 5 dBi 915 MHz omni rubber duck (RP-SMA) — one SiK, one LoRa
    - 1× 9 dBi 915 MHz Yagi directional (RP-SMA) — shared SiK+LoRa via RF splitter
    - 1× 14 dBi 5 GHz flat panel (RP-SMA) — Wi-Fi, gimbal-mounted
    - 1× 49 MHz base-loaded whip 1/4-wave (~0.94 m physical) with 4 ground radials
    - 1× 3 dBi 2.4 GHz rubber duck dipole (Zigbee, optional)
    - 1× u-blox ANN-MB-00 or equiv active GNSS patch (GCS position fix)
    - 1× 2-way 915 MHz RF splitter ≥20 dB isolation (Minicircuits ZFSC-2-1W-S+ or equiv)
    - Coax cables per `skipper_wiring.md` cable table (LMR-195, RG-58, RG-316)
- [ ] **Procure gimbal hardware:**
    - 2× DS3218MG digital servo (same as aircraft nacelle servos — reduces spare parts inventory)
    - 2× AS5600 magnetic encoder PCB breakout module (I²C, 0x36)
    - 2× N42 diametrically magnetised disc magnet 6×2 mm (encoder rotor)
    - 1× 6804 thin-section bearing (20×32×7 mm) — pan stage
    - 2× MF104ZZ flanged bearing (4×10×4 mm) — tilt pivot (same as nacelle pivot)
    - 1× TCA9548A I²C mux PCB breakout (encoder bus isolation)
    - 1× M6 camera tripod (heavy-duty) or 3 m telescoping mast for outdoor use
- [ ] **Flash Debian Linux to Skipper PB2-I eMMC** — same OS image as aircraft nodes.
    USB-C boot procedure per BeagleBone Debian documentation.
- [ ] **Apply Cape-B-2 device tree overlay for Skipper** — compile and install
    `gcs/skipper/firmware/pb2i/dts/k3-am6254-pocketbeagle2-skipper-cape-b2.dtbo`.
    Verify EHRPWM0 appears as `/sys/class/pwm/pwmchip0/` with 2 channels.
    Verify I²C2 appears as `/dev/i2c-2`.
- [ ] **Provision TPM 2.0 (SLB9672) on Skipper's PB2-I** — unique key material; persistent
    handle `SKIPPER_TPM_KEY_HANDLE` (0x81000001) per `skipper_config.h`.
    Follow the same provisioning procedure as aircraft nodes (PROVISIONING.md, TBD).
- [ ] **Verify CPLD write-blocker on Skipper's log μSD** (Cape-B-2 ATF16V8BQL):
    `echo test > /mnt/flightlog/test.txt` must return read-only error.
    Configure `/etc/fstab` noexec/nodev/nosuid/ro mount for log partition.
- [ ] **Build and install Skipper PB2-I firmware:**
- [ ] **Install and configure mavlink-router on Skipper's PB2-I** — same binary as for
    aircraft CN nodes; configure for GCS role (forward all radio links → USB CDC-ECM → host PC).
    Test: QGC on host PC should receive heartbeat on UDP :14550 with aircraft bench-powered.
- [ ] **Enable all 5 radio interfaces on Skipper's PB2-I** and verify each link at bench:
    - SiK UART2: `screen /dev/ttyS2 57600` — observe MAVLink framing bytes
    - LoRa SPI1: Python test: `python3 -c "import spidev; ..."` — read RFM95W version register (expected 0x12)
    - Wi-Fi wlan0: `iw dev wlan0 scan` — observe available networks
    - 49 MHz UART5: `screen /dev/ttyS5 1200` — verify Commo responds to KISS init
    - I²C2 (encoders): `i2cdetect -y 2` — verify TCA9548A at 0x70 and AS5600 at 0x36
- [ ] **Configure Wi-Fi transmit power** per FCC EIRP compliance:
    When 14 dBi panel is in use, set `iw dev wlan0 set txpower fixed 1700` (17 dBm = 1700 mBm).
    Create persistent udev hook or network config to apply on boot.
- [ ] **Install Debian Linux on GCS host PC** (bookworm or later).
- [ ] **Run installation scripts in order:**
- [ ] **Configure QGroundControl:**
    Application Settings → Comm Links → Add → UDP → localhost:14550 (mavlink-router output).
    Set vehicle type to ArduPilot.  Import parameter file from `gcs/skipper/software/config/qgc_params.params`
    (create this file in Phase Skipper-3 after first aircraft connection).
- [ ] **Configure Wi-Fi Tx power on host PC** — if host PC has Wi-Fi and 14 dBi panel connected,
    reduce to 17 dBm before use: `iw dev wlan0 set txpower fixed 1700`.
- [ ] **Run tracking software tests:**
- [ ] **Implement `gcs/skipper/firmware/pb2i/src/skipper_comms.c` and `skipper_comms.h`** — GCS-side
    comms daemon: USB CDC-ECM bridge, MAVLink authentication (TPM HMAC), 49 MHz (Part 15 §15.235) KISS relay,
    LoRa relay, Wi-Fi UDP relay, mavlink-router integration.  Structure parallel to aircraft
    `avionics/firmware/cn/src/main.c`.  Add `skipper_comms` target to `CMakeLists.txt`.
    **BLOCKS Phase Skipper-2 full multi-link operation.**
- [ ] **Bench test gimbal hardware** — connect two AS5600 encoders via TCA9548A to Skipper
    PB2-I I²C2 bus.  Run `i2cdetect` to confirm encoder presence.  Run skipper_gimbal daemon;
    verify it reads encoder angles and drives servo PWM on EHRPWM0.
- [ ] **Gimbal calibration:**
    - Home position: set `s_pan_zero_counts` and `s_tilt_zero_counts` to encoder readings when
        gimbal physically points North at 0° elevation (calibration step in skipper_gimbal.c init).
    - Travel limit verification: command pan to ±170°; verify hard stops engage at ±175°.
    - Tilt limit: command −10° and +90°; verify hard stops engage at −15° and +95°.
- [ ] **Run telemetry_feed.py bench test** — power aircraft (Phase 5 minimum: 2-node),
    run `python3 src/telemetry_feed.py`; verify GLOBAL\_POSITION\_INT JSON datagrams appear
    on UDP :14560 within 2 s of aircraft GPS lock (HDOP ≤1.5).
- [ ] **Run tracker.py bench test** — with telemetry_feed.py running and GCS GNSS connected,
    run `python3 src/tracker.py`; verify gimbal target JSON appears on UDP :14570 at ≥5 Hz.
    Confirm azimuth and elevation values change correctly as aircraft position is varied.
- [ ] **Run gimbal_ctrl.py bench test** — with tracker.py running, run `python3 src/gimbal_ctrl.py`;
    verify `GIMBAL_TARGET` commands appear on PB2-I UDP :14571; verify gimbal physically slews
    to commanded position and encoder confirms on-target within 3 s.
- [ ] **End-to-end tracking test (outdoor):**
    - GCS GNSS acquires fix (HDOP ≤1.5); operator records GCS position.
    - Walk aircraft (powered, GPS locked) 30–50 m in cardinal directions.
    - Verify gimbal pan tracks aircraft azimuth within 5°.
    - Verify gimbal tilt tracks aircraft elevation within 3° (at low aircraft altitude, elevation ≈ 0°).
- [ ] **Multi-link communication bench test:** connect aircraft (Phase 5 minimum) to Skipper;
    verify QGC heartbeat on each link independently (disable 3, test 1, rotate):
    SiK 915 MHz → LoRa 915 MHz → Wi-Fi 5 GHz → 49 MHz (Part 15 §15.235).
    All 4 links must deliver ≥1 MAVLink heartbeat per 5 s with aircraft at 1 m range.
- [ ] **915 MHz link margin test (open field, 1 km):**
    Aircraft powered (no flight) at 1 km. Observe QGC RSSI on SiK link.
    Required: RSSI ≥ −90 dBm (SiK sensitivity ≈ −112 dBm → ≥22 dB link margin;
    adequate to absorb ~20 dB receiver desense at aircraft in 500 W/m² environment).
- [ ] **Wi-Fi link margin test (open field, 200 m):**
    Aircraft at 200 m. Observe Wi-Fi telemetry rate in QGC.
    Required: ≥100 kbps sustained (adequate for video + MAVLink telemetry at 200 m).
- [ ] **49 MHz (Part 15 §15.235) link test (1 km):**
    Aircraft at 1 km. Verify AX.25 KISS frames received on the 49 MHz (Part 15 §15.235) link.
    Log RSSI from Commo STATUS register.
- [ ] **Gimbal pointing accuracy test (outdoor, aircraft at 200–500 m):**
    With aircraft carrying a known position-fix (GPS HDOP ≤1.0), compare gimbal-pointed
    azimuth to independently measured true bearing.  Required: pointing error ≤5°.
- [ ] **MAVLink authentication test:** verify aircraft nodes reject unsigned commands from
    Skipper if TPM provisioning is incomplete (remove TPM key, attempt arm command →
    should be rejected; re-provision TPM → arm command accepted).
- [ ] **Node loss with Skipper active:** kill one aircraft FC node during bench hover test;
    verify Skipper (QGC) shows failover in status panel within 200 ms; remaining nodes
    maintain MAVLink heartbeat to Skipper on all links.
