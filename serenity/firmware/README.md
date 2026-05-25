# Serenity UAV — Firmware

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Status:** Phase 6 — Minimum Viable Firmware for First Flight

---

## Overview

This directory contains the userspace firmware daemons that run on the eight
PocketBeagle 2 Industrial (AM6254) single-board computers in the Serenity UAV.

The AM6254 runs a standard Linux image from onboard eMMC; these daemons are
standard Linux processes that use POSIX APIs, i2c-dev, libgpiod, and pthreads.

## Node Groups

| Group | Count | Cape | Responsibilities |
|-------|-------|------|-----------------|
| FC nodes | 4 | Cape-A | Flight control, navigation, obstacle avoidance, ESC/actuator drive |
| CN nodes | 4 | Cape-B | Radio links, system logging, payload/cargo management |

## Directory Layout

```
firmware/
├── common/
│   └── include/         # Shared headers used by both FC and CN daemons
│       ├── kiss_types.h # KISS protocol constants (RFC 1055 / Chepponis & Karn 1987)
│       └── ax25_types.h # AX.25 v2.2 frame type definitions
├── cn/                  # CN node daemon (runs on all 4 Cape-B / AM6254 nodes)
│   ├── CMakeLists.txt
│   └── src/
│       ├── main.c       # Daemon entry point, argument parsing, signal handling
│       ├── si5351.h     # Si5351A DDS I²C driver API
│       ├── si5351.c     # Si5351A frequency programming (RCRS 49 MHz channels)
│       ├── xcvr_kiss.h  # XCVR-49MHZ-1 KISS/AX.25 driver API
│       └── xcvr_kiss.c  # KISS framing, PTT sequencing, UART I/O
├── fc/                  # FC node daemon (stub — Phase 7)
│   ├── CMakeLists.txt
│   └── src/
│       └── main.c       # FC node entry point stub
└── CMakeLists.txt       # Top-level build
```

## Build

### Prerequisites

```bash
# On the development host (cross-compilation for AM6254 / aarch64)
sudo apt install cmake gcc-aarch64-linux-gnu libc6-dev-arm64-cross
sudo apt install libgpiod-dev:arm64  # PTT GPIO control
```

### Cross-compile for AM6254 (aarch64)

```bash
mkdir build && cd build
cmake .. -DCMAKE_TOOLCHAIN_FILE=../cmake/aarch64-linux-gnu.cmake
cmake --build .
```

### Native build (for unit testing on x86 host)

```bash
mkdir build-native && cd build-native
cmake .. -DNATIVE_BUILD=ON
cmake --build .
```

## Deployment

Copy binaries to the target via scp and install as systemd services:

```bash
scp build/cn/serenity-cn debian@cn-node-1:/usr/local/bin/
scp build/fc/serenity-fc debian@fc-node-1:/usr/local/bin/
```

Systemd unit files are in `cn/serenity-cn.service` and `fc/serenity-fc.service`.

## Security

All inter-node messages are digitally signed using the node's TPM 2.0 (SLB9670).
The signing key is bound to the TPM's PCR state at boot (measured boot).
The AX.25 payload carries a SHA-256 HMAC before KISS framing; the CN node
verifies the HMAC on received frames before forwarding to the AX.25 stack.
Key management uses the Linux TPM2 PKCS#11 provider (`pkcs11-provider`).

## References

- AX.25 Link Access Protocol v2.2, ARRL, 1998
- KISS TNC Protocol: Chepponis & Karn, ARRL 6th Computer Networking Conference, 1987
- Si5351A/B/C-B Datasheet, Skyworks (formerly Silicon Labs), Rev 1.4
- 47 CFR Part 95 Subpart D — Remote Control Radio Service
- libgpiod API documentation — kernel.org
- Linux i2c-dev interface — kernel.org/doc/Documentation/i2c/dev-interface.rst
