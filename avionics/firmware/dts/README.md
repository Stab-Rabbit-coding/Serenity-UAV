# Serenity UAV — Device Tree Overlays

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Status:** Phase 6 — Minimum Viable Firmware for First Flight

---

## Overview

This directory contains the AM62X device tree overlays that configure the
PocketBeagle 2 Industrial (AM6254) peripherals for the Serenity UAV Cape-A
and Cape-B expansion boards.

| Overlay | Cape | Node | Peripherals |
|---------|------|------|-------------|
| `cape-a/k3-am6254-pocketbeagle2-serenity-cape-a.dtbo` | Cape-A | FC nodes (4×) | IMU, barometer, TPM, ToF, GNSS, RS-485, CAN FD, Ethernet, EHRPWM, MIL-STD-1553 |
| `cape-b/k3-am6254-pocketbeagle2-serenity-cape-b.dtbo` | Cape-B | CN nodes (4×) | TPM, LoRa, NOR flash, logging SD, SiK radio, RS-485, RCRS 49 MHz, CAN FD, Ethernet, WiFi, cargo servo, MIL-STD-1553 |

## Prerequisites

```bash
# On the PocketBeagle 2 (Debian Trixie) or cross-compilation host:
sudo apt install device-tree-compiler    # provides dtc 1.7.x
```

`dtc` version 1.7 or later is required for the `-@` flag (generates
`__symbols__` section enabling runtime overlay application).

## Build

```bash
cd serenity/firmware/dts
make
```

This produces `cape-a/*.dtbo` and `cape-b/*.dtbo`.

## Install

```bash
# Copy compiled overlays to the PocketBeagle 2 boot partition.
# Must be run as root on the target board.
sudo make install
```

Then edit `/boot/firmware/extlinux/extlinux.conf` and add the appropriate
`fdtoverlays` line under your `LABEL` stanza:

```
# FC nodes (Cape-A):
fdtoverlays /overlays/k3-am6254-pocketbeagle2-serenity-cape-a.dtbo

# CN nodes (Cape-B):
fdtoverlays /overlays/k3-am6254-pocketbeagle2-serenity-cape-b.dtbo
```

Each node loads only one overlay (the one matching its installed cape).

## Pad Offset Verification

All `AM62X_IOPAD` offsets tagged `[ESTIMATE]` in the DTS source files
**must be verified** before production use by cross-referencing:

1. **TI AM6254 TRM, SPRUJ40**, Table 7-1 "MAIN Domain Pad Control Registers"
2. **PocketBeagle 2 Industrial schematic** (BeagleBoard.org hardware repo),
   which maps AM6254 ball numbers to P1/P2 expansion header pins.

Offsets tagged `[CONFIRMED]` are sourced from `k3-am625-sk.dtsi` in the
Linux 6.x kernel tree and have been validated against production hardware.

GPIO line numbers are logical (relative to `main_gpio0`) and must also
be verified against the PocketBeagle 2 expansion header pin map.

## Cape-A Peripheral Details

| Peripheral | Interface | Linux Driver | Notes |
|------------|-----------|--------------|-------|
| ICM-42688-P IMU | SPI0 CS0 | `invensense,icm42688p` | SPI mode 3, 24 MHz |
| BMP388 barometer | SPI0 CS1 | `bosch,bmp388` | SPI mode 0, 10 MHz |
| SLB9670 TPM 2.0 | SPI0 CS2 | `infineon,slb9670` | 33 MHz, IRQ + RST GPIO |
| TCA9548A I²C mux | I2C2 0x70 | `nxp,pca9548` | 8-ch, 400 kHz |
| VL53L5CX ToF ×2 | I2C2 mux ch0/1 | `st,vl53l5cx` | 0x29, share addr |
| MS4525DO airspeed | I2C2 mux ch2 | `ms4525do` | FC1 only |
| Debug console | UART0 | n/a | 115200 8N1 |
| ESC telemetry | UART1 | n/a | BLHeli32 / Hobbywing |
| u-blox M10Q GNSS | UART3 | gpsd | 38400 baud default |
| RS-485 MAX3485E | UART4 | n/a | DE/RE# GPIO direction |
| CAN FD ATA6561 | MCAN0 | `m_can` | 1/8 Mbps |
| Ethernet DP83825I ×2 | CPSW3G | `dp83825i` | 100BASE-TX RSTP ring |
| EHRPWM 0-2 | — | `pwm` | 6ch servo/ESC PWM |
| MIL-STD-1553B | PRU-ICSS0 PRU0 | n/a | Manchester II 1 Mbps |
| Extra PWM ch 6-7 | PRU-ICSS0 PRU1 | n/a | 1 µs resolution |

## Cape-B Peripheral Details

| Peripheral | Interface | Linux Driver | Notes |
|------------|-----------|--------------|-------|
| SLB9670 TPM 2.0 | SPI1 CS0 | `infineon,slb9670` | HMAC keys for radio frames |
| RFM95W LoRa 915 | SPI1 CS1 | `semtech,sx1276` | 47 CFR Part 15 Subpart C |
| W25Q128JV NOR flash | SPI1 CS2 | `jedec,spi-nor` | 16 MiB, 3 partitions |
| Logging microSD | SPI1 CS3 | `mmc-spi-slot` | ext4, noexec, CPLD WP |
| RFD900x SiK 915 MHz | UART2 | n/a | MAVLink, HW CTS/RTS |
| RS-485 MAX3485E | UART4 | n/a | DE/RE# GPIO direction |
| XCVR-49MHZ-1 RCRS | UART5 | n/a | AX.25, 57600 8N1, PTT_N GPIO |
| CAN FD ATA6561 | MCAN0 | `m_can` | 1/8 Mbps |
| Ethernet DP83825I ×2 | CPSW3G | `dp83825i` | 100BASE-TX RSTP ring |
| WL1837MOD WiFi | MMC1 / SDIO | `ti,wl1837` | 5 GHz 802.11ac, 4-bit |
| EHRPWM0 | — | `pwm` | 2ch cargo servo/gimbal |
| MIL-STD-1553B | PRU-ICSS0 PRU0 | n/a | RT mode only on CN nodes |
| Cargo PWM + TDDS | PRU-ICSS0 PRU1 | n/a | 2ch servo + Si5351 sync |

## PRU Firmware

PRU firmware binaries must be installed to `/lib/firmware/serenity/` on
the target before loading the overlays:

```bash
sudo mkdir -p /lib/firmware/serenity/
sudo cp pru0-mil1553.out   /lib/firmware/serenity/
sudo cp pru1-servo-pwm.out /lib/firmware/serenity/    # Cape-A PRU1
sudo cp pru1-cargo-servo.out /lib/firmware/serenity/  # Cape-B PRU1
```

PRU firmware source is in `serenity/firmware/pru/` (Phase 7).

## References

- TI AM6254 Technical Reference Manual, SPRUJ40
- TI AM62x SK EVM device tree, `k3-am625-sk.dtsi`, Linux 6.x kernel
- PocketBeagle 2 Industrial schematic — BeagleBoard.org hardware repository
- BeagleBone Debian Trixie `extlinux.conf` overlay documentation
- MIL-STD-1553B, DoD Interface Standard, 21 Sep 1978
- 47 CFR Part 95 Subpart D (RCRS 49 MHz channel plan)
- 47 CFR Part 15 Subpart C (unlicensed 915 MHz LoRa)
