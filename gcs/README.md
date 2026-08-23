# Serenity UAV — Ground Control Station (Skipper)

**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0
**Current design revision:** Rev S (2026-07-04)

> Ground control station (GCS) hardware and software for Serenity UAV: multi-radio comms
> node (Wi-Fi, Zigbee, SiK 915 MHz, 49 MHz, LoRa), antenna gimbal tracking, and
> QGroundControl integration for autonomous mission planning and flight telemetry.

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
- **Comms:** [REF-IEEE-001] IEEE 802.15.4 (ZigBee), [REF-IEEE-002] IEEE 802.11 (Wi-Fi)
- **Navigation:** [REF-WGS84-001] WGS84 geodetic datum (GPS), [REF-HAVERSINE-001] Haversine
  formula (great-circle distance)

See root [`REFERENCES.md`](../REFERENCES.md) for the complete reference catalog.

## License

**Hardware (CAD, schematics, Gerbers, 3D-printed parts):** CERN-OHL-W 2.0
**Firmware (C source, Python scripts, device-tree overlays):** CC BY-SA 4.0
**Documentation:** CC BY-SA 4.0

See root [`LICENSE`](../LICENSE) and [`docs/attribution_and_licensing.md`](../docs/attribution_and_licensing.md)
for full licensing details.

---

*"I aim to misbehave." — Skipper Reynolds*
