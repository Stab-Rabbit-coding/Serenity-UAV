# Serenity UAV — Airframe Fuselage — Head/Cargo/Middle Shells TODO (Open Work Only)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0

> **This file lists only currently-open (unchecked) top-level tasks for
> this subsystem — one line each, <=70 chars, no prose.** Full detail
> (notes, rationale, nested sub-steps, done items) lives in
> [`WBS.md`](WBS.md), the full historical record for project-progression
> tracking. Close an item in `WBS.md` first, then delete its line here.

*"A special hell. — Shepherd Book"*

---

## §1.1.1 — Fuselage: Shell Regeneration, Middle-Section Bays (part 3/3)
→ full detail: `WBS.md` §1.1.1

- [ ] ★ CARGO-01 payload won't fit past the wing spar (BLOCKER)
- [ ] CARGO-02 shell bores Ø12.3 for a spar the wing retired (8.3)
- [ ] ★ CARGO-03 wing root mortise does not penetrate the bulkhead
- [ ] ★ CARGO-03b tenon on chord line, mortise on WING_ROOT_Z (4.5mm)
- [ ] ★ CARGO-03c coupon-test CF-PETG: >=15MPa tenon, else 2nd spar
- [ ] CARGO-04 aft ESC conduit blocked by the uncut bulkhead wall
- [ ] head_shell24.stl
- [ ] cargo_sect_shell24.stl
- [ ] Cargo gondola shell
- [ ] Clamshell door halves
- [ ] `cargo_sect_shell24.scad` — shuttle exterior fairing profiles on Z walls
- [ ] Avionics dorsal access covers / Faraday tray lids (Inara & River)
- [ ] Update REVN_BUILD_GUIDE_24IN.md bay layout table
- [ ] Regenerate `cargo_sect_shell24.stl`
- [ ] Add DRV8833-tray boss locations to `cargo_sect_shell24.scad`
- [ ] Add SG90 bell-crank boss to inner face of each door panel
- [ ] ★ Bench-verify SPT5425LV stall current + pin-removal (BLOCKER)
- [ ] ★ Winch containment: 5 positive fixes (spool must stay in bay)
- [ ] Verify Part 107 dropped-object section number
- [ ] Containment checks on assembly + pre-flight cards
- [ ] ★ Shed threshold vs maneuver envelope (2.0g = 0.98x)
- [ ] Calibrate T_slip 0.060 N·m at the spool hub collar
- [ ] Set servo torque ceiling below T_slip (wear protection)
- [ ] Servo mode: encoded continuous rotation (not stepper)
- [ ] Mark winch spool a consumable (wear item + spare)
- [ ] AK7455 spool encoder on gateway J_ENC (spec §3.7.3)
- [ ] Implement the six Rev S winch STLs
- [ ] Winch pedestal M3 boss stations in cargo_sect_shell24.scad
- [ ] Half-duplex TTL bus wiring on FLEX_TTL_GPIO
- [ ] Catch solenoid drive (AO3400 + pull-down + SS34)
- [ ] Bench-calibrate ratchet slip to 8.0 N ± 1.0 N
- [ ] Line-shed test (inboard end must NOT be anchored)
- [ ] Winch state machine firmware (Simon + gateway)
- [ ] Re-run winch mass/CG once SPT5425LV+LibreServo v2 is weighed
- [ ] Slicer verification
- [ ] Flight Engineer's room — PDB mounting in inner neck
- [ ] CF skid rod channels
- [ ] Simon bay — define avionics bay in MIDDLE section (Phase 11 move)
- [ ] Flight Engineer room — PDB + battery bay, middle VENTRAL (2026-06-13).
- [ ] Avionics-bay interior name marks (DEFERRED, 2026-06-13).
- [ ] Phase 11 — aft EDF intake scoop cuts
- [ ] neck_intake_frame.stl (Phase 11)
- [ ] aft_edf_plenum.stl
- [ ] Mount ant-collision strobe on belly of middle section (FAA 91.209)
- [ ] Mount ant-collision steady white tail light on upper pod of rear

---
