# Tilt Bracket Integration into Wing — Summary (2026-07-18)

> **SUPERSEDED 2026-07-18/19** — see `docs/TILT_SPAR_ANALYSIS.md` and
> `docs/NOZZLE_DRIVE_TRADE.md` for the adopted mechanism (rotating 8 mm steel spar
> driven by a cargo-bay servo, wingtip-gear + pushrod nozzle drive). The fixed 4 mm
> CF press-fit spar and sector-gear-on-bracket design described below was replaced
> within roughly a day of this document being written; retained as historical record
> of the design this document's own integration work was built against.

**Status:** Integration complete; wing SCAD updated; pylon artifacts archived

---

## Changes Made

### 1. Wing SCAD Updated (wings_s1223_revo.scad Rev R1a)

Added integrated tilt bracket functionality to wing tip geometry:

**New parameters (lines 217–234):**
- `BRACKET_SPAN` = 88 mm (extension from wing tip to nacelle)
- `BRACKET_W_ROOT` = 36 mm, `BRACKET_H_ROOT` = 32 mm (cross-section)
- `BRACKET_WALL` = 3 mm (minimum wall thickness)
- `TILT_SPAR_BORE_D` = 3.98 mm (4mm CF spar press-fit)
- `NAC_BOSS_SOCKET_D` = 16.6 mm (nacelle pivot boss receiver)
- `SECTOR_BC_R_BRACKET` = 18 mm (sector gear mounting bolt circle)
- M2.5 insert pockets for sector gear (4×)

**New modules added:**
- `integrated_tilt_bracket_body()` — structural box from wing tip to nacelle
- `bracket_tilt_spar_bore()` — 4mm CF pivot spar bore
- `bracket_nacelle_boss_socket()` — nacelle pivot boss receiver
- `bracket_sector_gear_mounts()` — M2.5 insert pockets for sector gear

**Integration into wing_one_side():**
- Bracket added to union (additive geometry)
- Bracket bores subtracted in difference() block
- Replaces separate wing_nacelle_pylon_revo.scad component

**Documentation updated:**
- Line 639: Updated module comment to note integration
- Backup created: `wings_s1223_revo.scad.backup-2026-07-18`

---

### 2. Pylon Artifacts Archived

Superseded components moved to `airframe/archive/`:

| Item | Archive Location |
|------|------------------|
| `wing_nacelle_pylon_revo.scad` | `archive/openscad/wings/` |
| `wing_nacelle_pylon_revo.stl` | `archive/stls/wings/` |

Reason: Tilt bracket functionality now integrated into wing; separate component no longer needed.

---

### 3. Assembly Script Updated (serenity_assembly.py)

- Removed standalone pylon import lines (former Pylon_Port, Pylon_Stbd)
- Replaced with integration note and reference to updated wing geometry
- No separate `add_mesh()` calls for pylon
- Assembly now loads wings with integrated brackets; no separate pylon component

---

## Next Steps

### User Action Required

1. **Regenerate wing STLs** from the updated SCAD:
   ```bash
   cd airframe/openscad/wings/
   openscad -o wing_port_s1223_revo.stl wings_s1223_revo.scad -D RENDER_SIDE=1
   openscad -o wing_stbd_s1223_revo.stl wings_s1223_revo.scad -D RENDER_SIDE=-1
   ```

2. **Verify bracket geometry** in FreeCAD:
   - Bracket should extend from wing tip outboard ~88 mm
   - Cross-section should taper smoothly
   - Bracket should reach the nacelle cleanly with no gaps

3. **Test fit with nacelle** (visual inspection in assembly):
   - Nacelle pivot boss should seat into bracket socket
   - Sector gear mount face should align with gear
   - Confirm smooth transition wing → bracket → nacelle

### AI Next Steps

Once wings are regenerated:

1. Bake new wing STLs to hull frame (via `tools/bake_hull_frame.py`)
2. Regenerate assembly
3. Verify in FreeCAD that bracket-to-nacelle interface is clean
4. **OPEN ISSUE:** Servo bracket placement for nacelle tilt actuation
   - Former design: servo on cargo wall, pushrod to pylon
   - New design: bracket integrated into wing — servo actuation path TBD
   - Needs clarification on how servo will reach the bracket/nacelle

---

## Known Unknowns

### Servo Actuation Path (BLOCKER)

The separate servo bracket (Cargo_Door_Servo_Bracket / Cargo_Release_Servo_Bracket in the assembly) was designed to mount on the cargo wall and reach the pylon via pushrod. Now that the bracket is part of the wing:

**Question:** How should the servo-to-bracket connection work?

**Options:**
1. **Servo mounts on cargo wall, longer pushrod reaches wing-mounted bracket** (requires longer mechanical linkage)
2. **Servo mounts on wing pylon/bracket itself** (simplifies linkage, requires servo mounting boss on bracket)
3. **Different actuation mechanism entirely** (e.g., cable-driven, deferred to Phase 11)

**Required before proceeding:**
- Clarify servo mounting location
- Design/update bracket geometry to accommodate servo attachment if needed
- Update pushrod routing and length

---

## Documentation References

- Wing SCAD header: `wings_s1223_revo.scad` (updated 2026-07-18, Rev R1a)
- Archive manifest: Check `ARCHIVE_INDEX.md` for pylon files
- TODO.md §1.1.0 §1.1.2: Hull-frame standardisation + wing work
- VERIFY_PLACEMENT_CHECKLIST.md: Still references old pylon §3 (update pending user decision on servo actuation)

---

## Files Changed

| File | Change |
|------|--------|
| `airframe/openscad/wings/wings_s1223_revo.scad` | Added bracket modules + integration |
| `airframe/FreeCAD-scripts/serenity_assembly.py` | Removed pylon imports |
| `airframe/archive/openscad/wings/wing_nacelle_pylon_revo.scad` | Archived (moved from `openscad/wings/`) |
| `airframe/archive/stls/wings/wing_nacelle_pylon_revo.stl` | Archived (moved from `stls/wings/`) |

---

*"The only easy day was yesterday." — Navy SEAL saying*
