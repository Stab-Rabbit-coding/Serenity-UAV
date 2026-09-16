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

- [ ] Export individual STLs (set RENDER variable in SCAD)
- [ ] Verify cover shoulder fit in slicer cross-section (confirm 1.5 mm…
- [ ] Export STL → `airframe/stls/fuselage/rcrs49_wire_post.stl` (×4…
- [ ] Verify port/starboard shoulder-height mount line in FreeCAD against…
- [ ] Bond River's forward post to the port flank at sta 120 mm
- [ ] Bond Simon's forward post to the starboard flank at sta 120 mm
- [ ] Install both temporary aft posts (port + starboard) at sta 580 mm

##### 1.1.1.1 *Head*
→ full detail: `WBS.md` §1.1.1.1

- [ ] head_shell24.stl — regenerate from `airframe/openscad/fuselage/head_s…

##### 1.1.1.2 *Cargo*
→ full detail: `WBS.md` §1.1.1.2

- [ ] cargo_sect_shell24.stl — regenerate from `serenity/stl/cargo_sect_she…

###### 1.1.1.2.1 *Cargo Handling*
→ full detail: `WBS.md` §1.1.1.2.1

- [ ] Cargo gondola shell — create `serenity/stl/s_cargo_gondola_shell.scad`
- [ ] Clamshell door halves — `cargo_door_port.stl` +…
- [ ] `cargo_sect_shell24.scad` — shuttle exterior fairing profiles on Z…
- [ ] Avionics dorsal access covers / Faraday tray lids for Inara and…
- [ ] Update REVN_BUILD_GUIDE_24IN.md bay layout table to reflect revised…
- [ ] Regenerate `cargo_sect_shell24.stl` from the current Rev S SCAD…
- [ ] Add DRV8833-tray boss locations to `cargo_sect_shell24.scad`…
- [ ] Add SG90 bell-crank boss to inner face of each door panel for…

###### 1.1.1.2.1a *Cargo Winch — STS3215 Conversion (Rev B, 2026-07-27)*
→ full detail: `WBS.md` §1.1.1.2.1a

- [ ] ★ CONTAINMENT — the spool must never leave the cargo bay (spec §3.10)
- [ ] Verify the Part 107 dropped-object section number
- [ ] Containment checks on the assembly and pre-flight cards
- [ ] ★ Flight-envelope decision — shed threshold vs maneuver envelope
- [ ] Calibrate `T_slip` = 0.060 N·m (0.61 kgf·cm) at the spool hub collar
- [ ] Set the servo torque ceiling below `T_slip`
- [ ] Servo mode: continuous rotation by construction (Rev C
- [ ] Mark the spool a consumable — wear item in the build guide…
- [ ] AK7455 spool encoder integration (spec §3.7.3)
- [ ] Implement the six winch STLs in `generate_cargo_mounts.py`…
- [ ] Pedestal mounting stations in `cargo_sect_shell24.scad`
- [ ] RS-485 differential bus wiring (Rev C — supersedes the Rev B…
- [ ] Catch solenoid drive circuit
- [ ] Bench-calibrate the ratchet slip threshold to 8.0 N ± 1.0 N measured…
- [ ] Line-shed test. Confirm the line actually runs clear of drum and…
- [ ] Firmware — winch state machine (Simon payload-primary, gateway-side…
- [ ] Re-run the §6 mass/CG table once the SPT5425LV+LibreServo v2 unit is…
- [ ] *(Optional, out of scope for this change)* Move the door/release…

###### 1.1.1.2.1b *Servo Fleet Standardisation — SPT5425LV + LibreServo v2 (Rev C, 2026-08-02)*
→ full detail: `WBS.md` §1.1.1.2.1b

- [ ] ★ Bench-verify the SPT5425LV/LibreServo v2 conversion
- [ ] RS-485 gateway integration (both winch and nacelle-tilt applications)
- [ ] Nacelle tilt firmware — command scheme change
- [ ] `current-specification/bom_revS.json`/`.csv` reconciliation
- [ ] OpenServoCore maturity re-check before SG90 procurement

##### 1.1.1.3 *Middle Neck*
→ full detail: `WBS.md` §1.1.1.3

- [ ] Slicer verification — open baked `middle_shell24_2mm_repaired.stl`…
- [ ] Flight Engineer's room — PDB mounting in inner neck
- [ ] CF skid rod channels — add 4.2 mm bore channel along each…
- [ ] Simon bay — define avionics bay in the MIDDLE section (moved here…
- [ ] Flight Engineer room — PDB + battery bay, middle VENTRAL (2026-06-13)
- [ ] Avionics-bay interior name marks (DEFERRED, 2026-06-13)
- [ ] Phase 11 — aft EDF intake scoop cuts — at Phase 11, cut the…
- [ ] neck_intake_frame.stl (Phase 11) — `openscad -o…
- [ ] aft_edf_plenum.stl — `openscad -o aft_edf_plenum.stl…

###### 1.1.1.3.1 *Anti-Collision Strobe*
→ full detail: `WBS.md` §1.1.1.3.1

- [ ] Mount ant-collision strobe on belly of middle section in accordance…

###### 1.1.1.4.1 *Anti-Collision Tail Light*
→ full detail: `WBS.md` §1.1.1.4.1

- [ ] Mount ant-collision steady white tail light on upper pod of rear…

## §1.1.1.5 — Wing-Root Spar Socket (Rev S1e joint requirements)
→ full detail: `WBS.md` §1.1.1.5

- [ ] WA-R3 — Split-collar pinch clamp
- [ ] WA-R18 — Mass/CG/T-W re-derivation after Rev S1g
- [ ] MA-1 — Reconcile every `PRINT-*` BOM row to its STL
- [ ] MA-5 — Hollow the actuator standoffs (−32.9 g)
- [ ] MA-6 — `PRINT-BATT-TRAY` measures 140.2 g against a 22 g BOM row
- [ ] MA-7 — The BOM mass column mixes installed mass, consumable stock…
- [ ] WA-R15a — Cargo-bay envelope re-measure after the actuator standoff
- [ ] WA-R16 — Tilt drive holding provision (TILT-CTL-01)
- [ ] WA-R17 — Split-collar pinch clamp (WA-R3) is still not a part

---
