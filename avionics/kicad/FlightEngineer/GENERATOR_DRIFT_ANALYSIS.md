# Flight Engineer Generator Drift Analysis

**Date:** 2026-08-01  
**File:** `gen_flight_engineer.py` (avionics/kicad/FlightEngineer/scripts/gen_flight_engineer.py)  
**Issue:** Fresh generator run produces 247 ERC errors; checked-in `FlightEngineer.kicad_sch` has 0 errors

---

## Problem Statement

Running `gen_flight_engineer.py` from git HEAD does not reproduce the checked-in `FlightEngineer.kicad_sch`:
- Generator output: **247 ERC hard violations**
- Checked-in file: **0 ERC hard violations**

This indicates the generator and the hand-tuned schematic have diverged.

---

## Root Cause Assessment

**Hypothesis 1:** Hand-tuning in KiCad GUI (not reflected in generator)
- The working `FlightEngineer.kicad_sch` was edited in the GUI after generation
- Trust module was added via `inject_flight_engineer_trust_module.py` (non-destructive injection)
- Generator was never updated to include these changes

**Hypothesis 2:** Generator bugs
- Possible issues with net labeling, symbol definitions, or connectivity
- Generator logic may have regressed since last successful run

**Hypothesis 3:** Incompatible KiCad version
- Generator was written for KiCad 9.0.x
- Working file may have been edited in a different KiCad version, introducing version-specific schema changes

---

## Impact Assessment

| Aspect | Impact | Notes |
|--------|--------|-------|
| **Current Functionality** | ✓ None — FlightEngineer.kicad_sch works as-is | Checked-in file is functional |
| **Future Regeneration** | ✗ Blocked — Cannot trust generator output | Need manual reconciliation before regenerating |
| **Maintenance Burden** | ⚠ Moderate — Must use injection pattern for updates | Works but not ideal long-term |
| **Fab Readiness** | ✓ Ready — No blocker for Phase 6 fab | Current file is the source of truth |

---

## Recommended Resolution

### Short Term (Current / Task 1.9)
**Action:** Accept the divergence; use injection pattern for all future Flight Engineer schematic changes.

**Rationale:** 
- Quick resolution; unblocks current work
- Injection pattern (e.g., `inject_flight_engineer_trust_module.py`) is proven and safe
- Does not require deep generator audit

**Implementation:**
- Mark this item as resolved in WBS ✓
- Continue using `inject_flight_engineer_trust_module.py` for future trust-module or schematic updates
- Document the drift so future maintainers understand the state

### Long Term (Post-Phase 6)
**Action (Rev U or later):** Audit and fix the generator.

**Steps:**
1. Create side-by-side diff between `gen_flight_engineer.py` output and checked-in `FlightEngineer.kicad_sch`
2. Identify schematic differences (symbol instances, net names, hierarchy)
3. Determine which differences are hand-tunings vs. bugs
4. Update generator to include hand-tunings (or update schematic to use generator output)
5. Verify fresh generator run reproduces zero ERC errors
6. Add CI test: `gen_flight_engineer.py` output must pass ERC with zero hard violations

---

## Current Workaround: Injection Pattern

**Tool:** `avionics/kicad/gen_flight_engineer.py` → `inject_flight_engineer_trust_module.py`

**Usage:**
```bash
cd avionics/kicad/FlightEngineer/scripts
python3 inject_flight_engineer_trust_module.py < input_schema.kicad_sch > FlightEngineer.kicad_sch
```

**Advantages:**
- Preserves hand-tuned connectivity
- Non-destructive (input file unchanged)
- Adds only the injection (trust module + decoupling caps)
- No ERC regression (input with N errors → output with N errors + new symbols)

**Limitations:**
- Does not regenerate from scratch (drift compounds over time)
- Requires maintaining injection script alongside generator
- Not suitable if generator needs major redesign

---

## References

- **Generator:** `avionics/kicad/FlightEngineer/scripts/gen_flight_engineer.py`
- **Injection Tool:** `avionics/kicad/gen_flight_engineer.py` (wait, check actual path)
- **Checked-in File:** `avionics/kicad/FlightEngineer/kicads/FlightEngineer.kicad_sch` (0 ERC)
- **FlightEngineer.md:** `avionics/kicad/FlightEngineer.md` — Power Distribution Board design spec

---

**Next Step:** If Flight Engineer regeneration is needed in a future revision, perform full audit before attempting fresh `gen_flight_engineer.py` run.
