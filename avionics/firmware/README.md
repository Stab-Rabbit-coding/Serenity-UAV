# Serenity UAV — Firmware

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0
**Status:** Phase 6 — Minimum Viable Firmware for First Flight

---

## Overview

This directory contains the userspace firmware daemons that run on the eight
PocketBeagle 2 Industrial (AM6254) single-board computers in the Serenity UAV.

The AM6254 runs **BeagleBone Debian Trixie** from onboard 64 GB eMMC; these daemons
are standard Linux processes that use POSIX APIs, i2c-dev, libgpiod 2.x, and pthreads.

## Node Groups

| Group | Count | Cape | Responsibilities |
| ------- | ------- | ------ | ----------------- |
| FC nodes | 4 | Cape-A | Flight control, navigation, obstacle avoidance, ESC/actuator drive |
| CN nodes | 4 | Cape-B | Radio links, system logging, payload/cargo management |

## Cape Variant Placement

The eight nodes use a **v2 · v2 · v2 · v2** (nose → tail) cape variant layout — Rev R all-EMI-hardened:

| Bay | Room name | Pair | FC cape | CN cape | Rationale |
|-----|-----------|------|---------|---------|-----------|
| A (nose) | Shepherd's room | FC1 / CN1 | Pilot | XO | Bus start termination; 5 kV isolated CAN FD / RS-485 / Ethernet at forward bus endpoint |
| B | Inara's shuttle | FC2 / CN2 | Pilot | XO | Rev R: uniform EMI hardening across all bays |
| C | River's room | FC3 / CN3 | Pilot | XO | Rev R: uniform EMI hardening across all bays |
| D (tail) | Simon's medbay | FC4 / CN4 | Pilot | XO | Bus end termination; 5 kV isolation closest to nacelle motor wiring / rear EDF |

Rev R places 5 kV galvanic isolation at every node. Cape-A-1 / Cape-B-1 are archived (Rev Q, 2026-06-05).

## Directory Layout

```text

firmware/
├── common/
│   └── include/         # Shared headers used by both FC and CN daemons
│       ├── kiss_types.h        # KISS protocol constants (RFC 1055 / Chepponis & Karn 1987)
│       ├── ax25_types.h        # AX.25 v2.2 frame type definitions
│       ├── failsafe_config.h   # Failsafe threshold constants (docs/failsafe_thresholds.md)
│       ├── sbus_input.h        # S-Bus input decoding API
│       └── sbus_input.c        # S-Bus frame parsing
├── cn/                  # CN node daemon (runs on all 4 Cape-B / AM6254 nodes)
│   ├── CMakeLists.txt
│   └── src/
│       ├── main.c       # Daemon entry point, argument parsing, signal handling
│       ├── si5351.h     # Si5351A DDS I²C driver API
│       ├── si5351.c     # Si5351A frequency programming (49 MHz Part 15 §15.235 channels)
│       ├── xcvr_kiss.h  # XCVR-49MHZ-1 KISS/AX.25 driver API
│       └── xcvr_kiss.c  # KISS framing, PTT sequencing, UART I/O
├── fc/                  # FC node daemon (Phase 6 sensor/monitor work done; PID governor Phase 7)
│   ├── CMakeLists.txt
│   ├── tools/
│   │   ├── governor_cal.py     # PID governor calibration tool
│   │   └── requirements.txt
│   └── src/
│       ├── main.c              # FC node entry point
│       ├── bmon_ina2xx.c/.h    # INA2xx bus-voltage/current monitor driver
│       ├── cell_mon_bq769x0.c/.h  # BQ769x0 per-cell battery monitor driver
│       ├── governor_config.h   # PID governor tuning constants
│       ├── mag_mmc5983ma.c/.h  # MMC5983MA magnetometer driver
│       └── mag_qmc5883l.c/.h   # QMC5883L magnetometer driver
└── CMakeLists.txt       # Top-level build

```

## Build

### Target Platform

| Item | Value |
| ------ | ------- |
| Board | PocketBeagle 2 Industrial (DigiKey 2820-100003007-ND) |
| SoC | TI AM6254 (quad Cortex-A53 @ 1.4 GHz, dual PRU-ICSS) |
| OS | BeagleBone Debian Trixie (libgpiod 2.2.1, Linux ≥ 6.1) |
| Storage | 64 GB eMMC (no OS microSD) |

### Prerequisites (cross-compilation host, Ubuntu 24.04+)

```bash

# Cross-compiler and CMake

sudo apt install cmake gcc-aarch64-linux-gnu libc6-dev-arm64-cross

# libgpiod 2.x headers and static lib for aarch64

# Debian Trixie sysroot required — or use multiarch on a Trixie host:

#   sudo dpkg --add-architecture arm64

#   sudo apt install libgpiod-dev:arm64

```

> **Note:**libgpiod**2.x** is required (Debian Trixie ships 2.2.1).
> The libgpiod 1.x API (Ubuntu 24.04) is **incompatible** with this code.
> Build directly on a PocketBeagle 2 or in a Trixie arm64 container if
> a full cross-compilation sysroot is not available.

### Build on the PocketBeagle 2 itself (simplest for Phase 6)

```bash

# On the PocketBeagle 2 running Debian Trixie:

sudo apt install cmake build-essential libgpiod-dev

git clone <repo> && cd Serenity-UAV/avionics/firmware
mkdir build && cd build
cmake ..
cmake --build .
sudo cmake --install .

```

### Cross-compile for AM6254 (aarch64) — advanced

```bash

mkdir build && cd build
cmake .. -DCMAKE_TOOLCHAIN_FILE=../cmake/aarch64-linux-gnu.cmake
cmake --build .

```

## Deployment

```bash

# Install via cmake on the target, or copy manually:

scp build/cn/serenity-cn debian@pocketbeagle2-cn1:/usr/local/bin/
scp build/fc/serenity-fc debian@pocketbeagle2-fc1:/usr/local/bin/

```

Systemd unit files are in `cn/serenity-cn.service` and `fc/serenity-fc.service` (Phase 7).

## Security

All inter-node messages are digitally signed using the node's TPM 2.0 (SLB9672).
The signing key is bound to the TPM's PCR state at boot (measured boot).
The AX.25 payload carries a SHA-256 HMAC before KISS framing; the CN node
verifies the HMAC on received frames before forwarding to the AX.25 stack.
Key management uses the Linux TPM2 PKCS#11 provider (`pkcs11-provider`).

## References

- AX.25 Link Access Protocol v2.2, ARRL, 1998
- KISS TNC Protocol: Chepponis & Karn, ARRL 6th Computer Networking Conference, 1987
- Si5351A/B/C-B Datasheet, Skyworks (formerly Silicon Labs), Rev 1.4
- 47 CFR Part 15 §15.235 — Operation within the band 49.82–49.90 MHz
- libgpiod API documentation — kernel.org
- Linux i2c-dev interface — kernel.org/doc/Documentation/i2c/dev-interface.rst
