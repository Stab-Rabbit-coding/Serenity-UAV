# Skipper — Serenity UAV Ground Control Station

> *"I aim to misbehave."*
>
> Skipper Reynolds, Captain

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0
**Revision:** R (2026-06-11)

---

## Overview

Skipper ("CAPT Reynolds", "CAPT Tight Pants") is the ArduPilot-compatible Ground Control
Station for the Serenity UAV.  Skipper manages all command, control, and monitoring functions
for the aircraft during all phases of operations.

Skipper operates at a safe distance from the aircraft's 500 W/m² design environment.
The link budget and directional antenna system are sized to maintain reliable communications
with an aircraft whose onboard receivers may be desensed by proximity to high-power RF
sources (commercial antenna towers, broadcast facilities).

---

## Architecture

### Host Computer

Debian Linux PC (x86\_64).  Minimum specification to be documented in
`hardware/docs/skipper_host_spec.md` (planned, not yet created).  Runs QGroundControl and the
tracking software stack.

### Skipper Comms Node

One PocketBeagle 2 Industrial (AM6254) + Cape-B-2 (XO) stack, USB-tethered to the host
PC.  This is the same hardware and firmware base used in the aircraft, providing a
symmetric, tested ground-side interface for every radio link.

| Link          | Module on Cape-B-2              | GCS antenna              |
|---------------|---------------------------------|--------------------------|
| SiK 915 MHz   | RFD900x via UART2               | 5 dBi omni + 9 dBi Yagi  |
| LoRa 915 MHz  | RFM95W via SPI1                 | 5 dBi omni + 9 dBi Yagi  |
| WiFi 5 GHz    | TI WL1837MOD                    | 14 dBi flat panel        |
| 49 MHz Part 15| Commo via UART5          | 1/4-wave loaded whip     |
| Zigbee 2.4 GHz| CC2652R7 via UART3 (optional)   | 3 dBi dipole             |

### Directional Antenna Gimbal

A two-axis (pan + tilt) CF-PETG gimbal carries the 9 dBi 915 MHz Yagi and 14 dBi WiFi
panel antennas.  Two AS5600 magnetic encoders (I²C to Cape-B-2) provide position feedback.
Two DS3218MG (or equivalent) servos drive the axes, commanded by Skipper's PB2-I via the
same servo output lines used on the aircraft.  The tracking software automatically points
the gimbal at the aircraft using MAVLink GLOBAL\_POSITION\_INT and the GCS's own GNSS fix.

Omnidirectional antennas (49 MHz whip, Zigbee dipole, 915 MHz omni) are mounted on fixed
mast arms and do not require tracking.

### EIRP Compliance

All transmitted EIRP values comply with FCC regulations.  See
`hardware/docs/skipper_antenna_spec.md` for the per-link gain chain and compliance table.

---

## Directory Layout

```
skipper/
├── README.md                         — This file
├── hardware/
│   ├── docs/
│   │   ├── skipper_host_spec.md      — (planned — not yet created)
│   │   ├── skipper_wiring.md         — Wiring and connector diagram
│   │   ├── skipper_antenna_spec.md   — Antenna gain budget and FCC EIRP compliance
│   │   └── skipper_power_budget.md   — Field power consumption breakdown
│   ├── enclosure/
│   │   ├── openscad/
│   │   │   └── skipper_field_enclosure.scad  — IP65 weatherproof field enclosure
│   │   └── stls/                     — Compiled STLs (generate from SCAD)
│   └── gimbal/
│       ├── openscad/
│       │   ├── skipper_gimbal_pan.scad   — Pan stage
│       │   ├── skipper_gimbal_tilt.scad  — Tilt stage
│       │   └── skipper_gimbal_mount.scad — Antenna mounting plate
│       └── stls/                     — Compiled STLs (generate from SCAD)
├── firmware/
│   └── pb2i/
│       ├── CMakeLists.txt            — Firmware build
│       ├── dts/
│       │   └── k3-am6254-pocketbeagle2-skipper-cape-b2.dts
│       └── src/
│           ├── skipper_config.h          — Compile-time configuration
│           ├── skipper_comms.h/c         — (planned, Phase Skipper-2 — not yet implemented; see CMakeLists.txt) USB serial link to host PC + radio bridge
│           ├── skipper_gimbal.h/c        — Antenna tracking servo controller
│           └── skipper_telemetry.h/c     — MAVLink telemetry parser / forwarder
└── software/
    ├── install/
    │   ├── install_deps.sh           — Host PC dependency installation
    │   ├── install_qgc.sh            — QGroundControl installation
    │   └── install_mavlink_router.sh — mavlink-router build and install
    ├── config/
    │   ├── mavlink_router.conf       — mavlink-router multi-endpoint configuration
    │   └── skipper_config.yaml       — Skipper system configuration
    └── tracking/
        ├── requirements.txt
        ├── src/
        │   ├── telemetry_feed.py     — MAVLink position consumer
        │   ├── tracker.py            — Bearing/elevation calculator
        │   └── gimbal_ctrl.py        — Servo command output to PB2-I
        └── tests/
            └── test_tracker.py
```

---

## Build and Setup

1. **Hardware:** See `hardware/docs/skipper_wiring.md`.  Flash PB2-I, seat Cape-B-2, attach
   Commo, connect antennas and field enclosure per wiring doc.

2. **Firmware:** Build Skipper's PB2-I firmware:
   ```sh
   cd firmware/pb2i && mkdir build && cd build
   cmake .. && make -j$(nproc)
   sudo make install
   ```

3. **Host PC:** Run installation scripts in order:
   ```sh
   sudo bash software/install/install_deps.sh
   sudo bash software/install/install_mavlink_router.sh
   bash software/install/install_qgc.sh
   ```

4. **Tracking software:**
   ```sh
   cd software/tracking
   pip install -r requirements.txt
   python src/telemetry_feed.py &
   python src/tracker.py &
   python src/gimbal_ctrl.py
   ```

5. **QGroundControl:** Launch QGC; it auto-connects to mavlink-router on UDP 14550.

---

## Security

Skipper participates in the Serenity NIST SP 800-207 Zero Trust architecture.

- Every command message sent from Skipper is digitally signed with the TPM-bound key
  provisioned during setup.
- Skipper's PB2-I TPM 2.0 must be provisioned before first operational use.
- The MAVLink system ID for Skipper is **255** (GCS reserved).
- Unsigned or unauthenticated messages from Skipper are discarded by all aircraft nodes.

---

## License

Published under **Creative Commons Attribution-ShareAlike 4.0 International** by Steve Griffing,
PE(CSE), CISSP-ISSEP, CPP.
[creativecommons.org/licenses/by-sa/4.0](https://creativecommons.org/licenses/by-sa/4.0)
