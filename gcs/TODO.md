# Serenity UAV — Ground Control Station (Skipper) TODO (Open Work Only)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0

> **This file lists only currently-open (unchecked) top-level tasks for
> this subsystem — one line each, <=70 chars, no prose.** Full detail
> (notes, rationale, nested sub-steps, done items) lives in
> [`WBS.md`](WBS.md), the full historical record for project-progression
> tracking. Close an item in `WBS.md` first, then delete its line here.

*"I aim to misbehave. — Capt. Skipper Reynolds"*

---

## §4.5 — Ground Control (Skipper / CAPT Reynolds) &#9733;
→ full detail: `WBS.md` §4.5

- [ ] Create Skipper host computer specification
- [ ] Skipper field enclosure — print and fit-check
- [ ] Gimbal STL generation and mesh verification
- [ ] Gimbal servo wind-load torque check
- [ ] Procure Skipper comms node hardware:
- [ ] Procure antenna hardware
- [ ] Procure gimbal hardware:
- [ ] Flash Debian Linux to Skipper PB2-I eMMC
- [ ] Apply Cape-B-2 device tree overlay for Skipper
- [ ] Provision TPM 2.0 (SLB9672) on Skipper's PB2-I
- [ ] Verify CPLD write-blocker on Skipper's log μSD
- [ ] Build and install Skipper PB2-I firmware:
- [ ] Install and configure mavlink-router on Skipper's PB2-I
- [ ] Enable all 5 radio interfaces on Skipper's PB2-I
- [ ] Configure Wi-Fi transmit power
- [ ] Install Debian Linux on GCS host PC
- [ ] Run installation scripts in order:
- [ ] Configure QGroundControl:
- [ ] Configure Wi-Fi Tx power on host PC
- [ ] Run tracking software tests:
- [ ] Implement `gcs/skipper/firmware/pb2i/src/skipper_comms.c` and `skipper_…
- [ ] Bench test gimbal hardware
- [ ] Gimbal calibration:
- [ ] Run telemetry_feed.py bench test
- [ ] Run tracker.py bench test
- [ ] Run gimbal_ctrl.py bench test
- [ ] End-to-end tracking test (outdoor):
- [ ] Multi-link communication bench test:
- [ ] 915 MHz link margin test (open field, 1 km):
- [ ] Wi-Fi link margin test (open field, 200 m):
- [ ] 49 MHz (Part 15 §15.235) link test (1 km):
- [ ] Gimbal pointing accuracy test (outdoor, aircraft at 200–500 m):
- [ ] MAVLink authentication test:
- [ ] Node loss with Skipper active:

---