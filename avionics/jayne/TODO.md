# Serenity UAV — Jayne (Cargo-Handling + Vision/ToF/Laser) TODO (Open Work Only)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0

> **This file lists only currently-open (unchecked) top-level tasks for
> this subsystem — one line each, <=70 chars, no prose.** Full detail
> (notes, rationale, nested sub-steps, done items) lives in
> [`WBS.md`](WBS.md), the full historical record for project-progression
> tracking. Close an item in `WBS.md` first, then delete its line here.

*"I was aiming for his head. — Jayne"*

---

#### 1.2c.1 — Schematic and Component Selection
→ full detail: `WBS.md` §1.2c

- [ ] FLEET-WIDE ISOW1044BDFMR footprint audit (flight-hardware error…

#### 1.2c.2 — Layout and Verification
→ full detail: `WBS.md` §1.2c

- [ ] Final component placement (user-reserved) + impedance-controlle…
- [ ] Generate production-ready Gerber files to `avionics/kicad/Jayne…

#### 1.2c.3 — Mechanical Integration
→ full detail: `WBS.md` §1.2c

- [ ] Flag stale laser bore dimensions:
- [ ] Add `cargo_tof_cut()` and `cargo_laser_cut()` cutter modules
- [ ] Local sensor harness (both sites):
- [ ] External ring harness — nose:
- [ ] External ring harness — cargo:

#### 1.2c.4 — Jayne Power Feed and Laser Unification (2026-07-05)
→ full detail: `WBS.md` §1.2c

- [ ] Kaylee second 5 V rail — cross-tied, mutually fault-tolerant (P…
- [ ] Jayne 5 V harness:
- [ ] Laser — unify to a single 520 nm green source, Class 2 both sit…
- [ ] Both Class 2 caps must be hardware-enforced
- [ ] Nose camera strobe + frame-difference detection
- [ ] Do not source
- [ ] Add pitot tube differential pressure transducer

#### 4.6.1 — TI AM62Ax Vision Pipeline Bring-Up
→ full detail: `WBS.md` §4.6

- [ ] MIPI CSI-2 camera sensor bring-up
- [ ] VPAC/ISP pipeline configuration
- [ ] H.264/H.265 hardware encoder pipeline
- [ ] Kernel/BSP integration
- [ ] Bench test:

#### 4.6.2 — TI MSPM0G3507 Control Firmware
→ full detail: `WBS.md` §4.6

- [ ] MCAN (CAN-FD) driver bring-up
- [ ] TFmini-S UART driver
- [ ] KSZ9477 Ethernet switch management driver
- [ ] Laser GPIO driver (both sites Class 2 — `docs/JAYNE_LASER_ANALY…
- [ ] Laser strobe + crosshair-metrology routine (AM62A7 ISP):
- [ ] SPI driver to Infineon SLB9670 TPM
- [ ] Signed telemetry:

#### 4.6.3 — Integration Testing
→ full detail: `WBS.md` §4.6

- [ ] Bench test:
- [ ] Ring failure test:
- [ ] Laser safety interlock test (nose only):

---