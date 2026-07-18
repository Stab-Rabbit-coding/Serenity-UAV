# VERIFY Parts Placement — Workflow & Action Plan

**Phase:** 1 of 3 (Initial Placement — CURRENT)  
**Date:** 2026-07-18  
**Status:** Awaiting user action

---

## What Was Done

✅ **Created detailed placement checklist** — `airframe/VERIFY_PLACEMENT_CHECKLIST.md`
- Organized by airframe section (cargo, battery, wings, pylons, servo brackets, antenna)
- Lists all 18 VERIFY parts (11 cargo bay, 2 pylons, 2 servo brackets, battery tray, belly panel, dorsal antenna fin)
- For each part: design intent, current state, placement estimate, verification needs, user action

✅ **Updated assembly script** — `airframe/FreeCAD-scripts/serenity_assembly.py` (Rev R1.2)
- Initial hull-frame placements added for all unpositioned VERIFY parts
- Cargo bay: 11 components now positioned with estimated transforms
- Pylons: positioned at wing roots (Y ≈ 15 mm, Z ≈ 65 mm)
- Servo brackets: positioned on cargo interior walls (Y ≈ −290 mm, Z ≈ 115 mm)
- Antenna fin: positioned on cargo roof (Z ≈ 160 mm)
- Battery tray & belly panel: estimates retained from previous session
- All placements include inline VERIFY comments indicating refinement is needed

---

## Your Next Steps (Phase 1 → 2)

### Step 1: Regenerate the Assembly Document

```bash
cd airframe/FreeCAD-scripts/
freecadcmd serenity_assembly.py
```

This produces: `airframe/Serenity-Assembled.FCStd`

**Expected output:**
```
[assembly] Creating FreeCAD document ...
[assembly] Fuselage sections ...
[assembly] Cargo bay interior mounts ...
[assembly] Battery tray and belly panel ...
[assembly] Wings ...
[assembly] Nacelle tilt pylons ...
[assembly] Nacelle pods ...
[assembly] Nacelle internal components ...
[assembly] Nacelle servo brackets ...
[assembly] Dorsal antenna fin ...
[assembly] Recomputing ...
[assembly] Saving → airframe/Serenity-Assembled.FCStd
[assembly] Complete.
```

### Step 2: Open & Inspect in FreeCAD

```bash
# Open the GUI
freecad airframe/Serenity-Assembled.FCStd
```

**Or:** drag the `.FCStd` file into FreeCAD manually.

### Step 3: Verify Each Section (Use the Checklist)

Work through `airframe/VERIFY_PLACEMENT_CHECKLIST.md` section by section:

1. **Cargo Bay (§1)** — Expand the tree; inspect all 11 interior parts:
   - Are doors aligned with belly cutout?
   - Do hinge retention blocks sit coaxially on door hinge axes?
   - Are cradle, FPV bezel, GPS ring on the correct interior faces (floor vs. roof)?
   - Do servo brackets reach their target locations?

2. **Battery Tray & Belly Panel (§2)** — Check fit on keel:
   - Does tray CG align with FCOG (forward CG)?
   - Is belly panel flush over tray opening?

3. **Wings & Pylons (§3)** — Verify pylon fit at wing roots:
   - Does each pylon extend outboard without interpenetrating hull/wing?
   - Are pivot axes aligned with nacelle pivot housings?

4. **Nacelle Servo Brackets (§4)** — Check cargo interior walls:
   - Is each bracket on the correct interior wall (port or stbd)?
   - Can the servo arm swing freely to the pylon pivot (≈ 60 mm pushrod reach)?

5. **Dorsal Antenna Fin (§5)** — Inspect cargo roof mount:
   - Does fin sit on cargo dorsal roof without fouling hull geometry?
   - Is it forward of the FPV bezel, clear of GPS ring?

### Step 4: Correct Gross Errors

If a part is obviously wrong (wrong side, inverted, far off), **fix it manually in the FreeCAD GUI**:

- Right-click part → Edit placement
- Adjust position (X, Y, Z) and rotation as needed
- Save the document

**Examples of gross errors:**
- Cargo door on the roof instead of belly
- Servo bracket pointing the wrong direction
- Pylon on the wrong wing side
- Battery tray at the wrong station

### Step 5: Report Back to Me

Send (or comment in this file) a simple table of corrections:

```markdown
| Part | Issue | Correction Made |
|------|-------|-----------------|
| Cargo_Door_Port | Hinge at X=−120, should be −117.6 | Moved to X=−117.6 |
| Pylon_Port | Too far back (Y=30), should be Y≈15 | Moved to Y=15 |
| Dorsal_Antenna_Fin | None observed | ✓ Looks good |
| ... | ... | ... |
```

**Or** just mark the checkboxes in `VERIFY_PLACEMENT_CHECKLIST.md` and describe any issues you found:
```markdown
- [x] §1.1 Cargo Door Port — visually verified, hinge alignment ✓
- [x] §1.2 Cargo Door Stbd — **needs adjustment: hinge X off by 3 mm**
- [ ] §1.3 Cargo Hinge Retention (4 blocks) — [describe issue]
...
```

---

## Phase 2: AI Precision Alignment (Next)

Once you've corrected gross errors and saved the FCStd file, I will:

1. **Extract final placement matrices** from the corrected `Serenity-Assembled.FCStd`
2. **Compute 4×4 transforms** for each part (rotation + translation in hull-frame coordinates)
3. **Apply ±0.01 in (0.254 mm) fine-tuning** to achieve design intent:
   - Coaxial bores: ≤ ±0.1 mm
   - Flush surfaces: ≤ ±0.2 mm
   - Clearances: ≥ 2 mm minimum (no interference)
4. **Update `serenity_assembly.py`** with validated transforms
5. **Regenerate and verify** the assembly
6. **Commit** all changes to the branch

---

## Phase 3: Final Sign-Off (After Phase 2)

Once placements are refined and verified, the items in TODO.md §1.1.0 will be checked off:

- [x] ~~Re-verify head↔cargo joint bosses in hull Y~~ (internally resolved; just needs checkbox)
- [x] Hull-frame placements for VERIFY parts (complete after Phase 2)

---

## Questions?

Refer to:
- **Full task details:** `airframe/VERIFY_PLACEMENT_CHECKLIST.md`
- **Assembly code:** `airframe/FreeCAD-scripts/serenity_assembly.py` (Rev R1.2)
- **Hull-frame coordinate system:** `CLAUDE.md` "Hull-Frame Coordinate Standard"

---

*"Keep flyin'." — Wash*
