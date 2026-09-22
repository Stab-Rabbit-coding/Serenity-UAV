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

- [ ] Clamshell door halves — `cargo_door_port.stl` +…
- [ ] `cargo_sect_shell24.scad` — shuttle exterior fairing profiles on Z…
- [ ] Update REVN_BUILD_GUIDE_24IN.md bay layout table to reflect revised…
- [ ] Add DRV8833-tray boss locations to `cargo_sect_shell24.scad`…
- [ ] Add SG90 bell-crank boss to inner face of each door panel for…

###### 1.1.1.2.2 *Cargo Section Rev T5 / T5b / T5e Layout (2026-09-15 / 2026-09-16)*
→ full detail: `WBS.md` §1.1.1.2.2

- [ ] WINCH-D — `CARGO_WINCH_SPECIFICATION.md` Rev D
- [ ] OBS-CARGO — cargo Observer tray SCAD in hull frame (envelope PLACED…
- [ ] NODE-SADDLE — author `node_saddle.scad` for N2/N4 (2 off)
- [ ] HARN-CLIP — encoder-harness turn-down clip on the tilt bracket (the…
- [ ] GPS-ANT — Ø36 patch antenna part for the dorsal cups (legacy…
- [ ] TC-BOARD — Open-Secure-ESC tilt controller fit on the T5e rails…
- [ ] ENC-DAUGHTER — AEAT-8800-Q24 sensor daughter for the brake-guide…
- [ ] 20D VERIFY — mounting-hole spacing (15 mm assumed) and Ø7 boss…
- [ ] CHIN-STRAPS — add 4 × BATT-STRAP-CAM to the order for the chin node…
- [ ] Cargo door re-fit (U1) still open — see 1.1.1.2.1 "Clamshell door…
- [ ] SERVO-PLACE — hull-frame placement of the three SG90s (port door…
- [ ] DOOR-LATCH-1..6 (`docs/CARGO_DOOR_LATCH_SPEC.md` §6)
- [ ] DOOR-SEAM-1 — tongue-and-groove interlock at the door-to-door mating…
- [ ] PRINT-GW-DOOR-TRAY hardware at order: 4 × RX-M3x5.7 inserts, 4 ×…

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
- [ ] MA-7 — The BOM mass column mixes installed mass, consumable stock…
- [ ] WA-R17 — Split-collar pinch clamp (WA-R3) is still not a part

---
