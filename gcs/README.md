# Serenity UAV — Ground Control Station (Skipper)

**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Current design revision:** Rev T (2026-09-06, see `docs/WBS.md` §6.4 for changelog)  
**Last updated:** 2026-10-07

> Ground control station (GCS) hardware and software for Serenity UAV: multi-radio comms
> node (Wi-Fi, Zigbee, SiK 915 MHz, 49 MHz, plus a long-range link whose ground-side
> hardware is under decision), antenna gimbal tracking, and
> QGroundControl integration for autonomous mission planning and flight telemetry.

## Current Status (2026-10-07)

Skipper is in design; no hardware is built or procured and the ground-side firmware is partly
planned (`skipper_comms.c` is not yet implemented). All 34 open items are in `WBS.md` §4.5.

- **Open design decision (opened 2026-10-07):** the aircraft's radio plan changed after
  Skipper's was written. The aircraft now carries mLRS (bare STM32WLE5JC), Wi-Fi on a USB
  module, and ZigBee on every TACCO, with SiK and 49 MHz on a standalone Commo node (Rev T).
  Skipper's documents (`skipper/README.md`, wiring, antenna, and power budget) still describe a
  TACCO with SiK, LoRa (RFM95W), and a WL1837MOD Wi-Fi module. The owner decides the ground
  loadout first; documents and firmware follow (`WBS.md` §4.5).
- **Field enclosure:** TACCO grew to 60 × 35 mm on 2026-10-06 (the stacking hole pattern is
  unchanged); re-check the enclosure fit before printing.
- **Reference corrections:** the IEEE citations in the list below now point to the right
  `REFERENCES.md` entries.

## This file is a pointer

This top-level `gcs/` folder's detailed design content has moved to `gcs/skipper/`, which is
kept current far more often than this file. Read there for anything beyond scope:

| For | See |
|-----|-----|
| System overview, architecture, comms links | [`gcs/skipper/README.md`](skipper/README.md) |
| Full hardware/firmware/software specification | [`gcs/SKIPPER_SPEC.md`](SKIPPER_SPEC.md) |
| Antenna, power budget, wiring detail | `gcs/skipper/hardware/docs/skipper_antenna_spec.md`, `skipper_power_budget.md`, `skipper_wiring.md` |
| GCS subsystem policy | [`gcs/AGENTS.md`](AGENTS.md) |
| Work breakdown | [`gcs/WBS.md`](WBS.md), [`gcs/TODO.md`](TODO.md) |

**Skipper** (formerly "Malcolm" — see the 2026-08-01 board rename, root `AGENTS.md` §9) is a
**PocketBeagle 2 Industrial** compute module running a multi-radio transceiver suite and
antenna tracking gimbal for command-and-control of the Serenity UAV across multiple RF links
and extended ranges. All external messages are **signed and authenticated** via TPM-bound
keys; every command is verified before ground-station relay to the aircraft.

## References

- **Regulatory:** [REF-FCC-001] 47 CFR Part 15, [REF-FCC-003] §15.235 (49 MHz unlicensed)
- **Comms:** [REF-IEEE-003] IEEE 802.15.4-2020 (ZigBee), [REF-IEEE-002] IEEE 802.11-2020 (Wi-Fi)
- **Navigation:** [REF-WGS84-001] WGS84 geodetic datum (GPS), [REF-HAVERSINE-001] Haversine
  formula (great-circle distance)

See root [`REFERENCES.md`](../REFERENCES.md) for the complete reference catalog.

## License

**Hardware (CAD, schematics, Gerbers, 3D-printed parts):** CERN-OHL-W 2.0
**Firmware, device-tree overlays, and tracking software:** MIT
**Documentation and images:** CC BY-SA 4.0

See root [`LICENSE`](../LICENSE) and [`docs/attribution_and_licensing.md`](../docs/attribution_and_licensing.md)
for full licensing details.

---

*"I aim to misbehave." — Skipper Reynolds*
