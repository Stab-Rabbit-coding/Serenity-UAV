# Serenity UAV — Deferred Work & Future Phases

**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0  
**Current design revision:** Rev T (2026-09-06, see `docs/WBS.md` §6.4 for changelog)

> Phase 11+ design work, aft propulsion system, RCS attitude thrusters, cargo-bay range-extender
> battery module, and other deferred upgrades planned for post-Phase-10 operations.

## Overview

This directory contains design specifications and work planning for system upgrades and
enhancements that are **deferred beyond Phase 10** (Advanced Autonomy and Long-Range Operations).
These features are **not required** for first flight (Phase 5) or initial autonomous operations
(Phases 6–10), but enable extended-mission capabilities once the baseline platform is flight-proven.

## Deferred Phases & Features

### Phase 11 — Aft EDF Integration (Forward Thrust + RCS)

**Purpose:** Add rear-fuselage EDF for forward/cruise thrust and four RCS (reaction-control system)
bleed-jet thrusters for pitch/yaw attitude authority in forward flight.

**Key specs:**
- **Rear EDF:** 55 mm 6S ducted fan, ~1,500 g thrust (forward only; not counted in hover T/W)
- **Intake:** Neck-section scoop windows, flexible plenum, intake frame
- **Nozzle:** Fixed canonical elliptical nozzle (2.06" × 1.76", 52.3 × 44.7 mm)
- **RCS system:** 4× SG90 proportional valves, rcs_distribution_manifold, ~15% EDF mass flow diverted
- **Mass impact:** +362 g (55mm EDF, RCS servos, manifold, nozzle housing)
- **Phase 11 AUW:** ~3,130 g (~110.4 oz) including rear EDF (but rear EDF thrust is **not** in hover budget)

**Design documents:**
- `docs/DEFERRED_PHASE_11_AFT_EDF.md` (if created; currently in `deferred/AGENTS.md`)
- `deferred/WBS.md` §Phase11
- `deferred/TODO.md` — open Phase 11 tasks

**Status:** Design complete; implementation deferred pending Phase 5–10 baseline flight validation.

---

### Phase 12 — Cargo-Bay Range-Extender Battery Module (RBM)

**Purpose:** Add a secondary battery pack in the cargo bay to extend endurance on autonomous
missions or support higher-altitude operations.

**Concept:**
- **Secondary 6S LiPo:** 2,000–4,000 mAh, ~400–600 g (tunable; mission-dependent)
- **Placement:** Cargo gondola interior, side bays (non-structural)
- **Integration:** Kaylee power distribution system (dual-rail failover model; RBM is third rail)
- **Current sharing:** Load-sharing across primary + secondary with reverse-polarity diodes
  (no active balancing; passive parallel connection like main battery rail)
- **Field swappability:** Quick-disconnect XT90-S connector in gondola nose
- **Firmware:** `pwr_fault` node monitors voltage/current across all three rails

**Phase 12 impact:**
- Endurance extension: +2–4 minutes typical hover time (TBD via flight testing)
- No structural changes (cargo bay already open)
- No additional avionics (uses existing Kaylee + PB2-I monitoring)
- Cost: ~$30–50 for secondary battery pack

**Design documents:**
- `deferred/WBS.md` §Phase12
- Kaylee PDB schematic (shows third-rail header for RBM connector)

**Status:** Concept-phase only; deferred pending Phase 5–6 endurance baseline characterization.

---

### Phase 13+ — Future Expansion (Speculative)

Possible additions beyond Phase 12 (not yet formally scoped):

- **Advanced gimbal tracking** — motorized antenna platform on ground station (partially
  designed; gimbal mechanics in `gcs/hardware/`)
- **Vision-based landing** — TI AM62A7 (Jayne) could implement automated visual-servoing landing
- **Cooperative multi-UAV** — mesh networking via Ethernet + CAN; one aircraft could relay
  telemetry from others (requires flight test data + new firmware architecture)
- **Search-and-rescue sensor suite** — thermal imaging, acoustic locator (external payload bay
  integration; requires payload interface spec)

**Status:** Speculative; not actively designed. Mentioned for completeness and context.

---

## Directory Structure

| File / Folder | Purpose |
|---------------|---------|
| `AGENTS.md` | Deferred-subsystem policy (Phase 11+ specifications, design authority) |
| `README.md` | This file (feature overview and navigation) |
| `WBS.md` | Work breakdown structure for Phases 11–13 (full task narrative) |
| `TODO.md` | Open items for deferred work (checked items stay for history) |
| `aft-edf/` | Phase 11 aft-EDF design documents and CAD source files |
| `rcs-thrusters/` | RCS system design, valve selection, bleed-air manifold |
| `cargo-rbm/` | Phase 12 range-extender battery module schematics |
| `archive/` | Older design iterations, rejected concepts, obsolete components |

---

## Phase 11 — Detailed Feature Breakdown

### Aft EDF Selection & Integration

**Current baseline:** 55 mm 6S EDF (HobbyKing / AliExpress), **~1,500 g raw fan thrust** (no inter-stage stator).

**Key difference from nacelle EDFs:** Rear EDF has no stator efficiency factor (unlike 50mm nacelle EDFs with 90% efficiency); 1,500g is raw thrust. The 4 RCS jets bleed ~15% of mass flow (not an efficiency factor, but a flow diversion).

**Design constraints:**
1. **Fixed nozzle** — Unlike nacelle iris (variable), the aft nozzle is canonical and fixed shape
   (2.06" × 1.76" elliptical)
2. **Forward thrust only** — Does not contribute to hover T/W (decoupled from VTOL authority)
3. **RCS bleed integration:** ~15% of EDF mass flow diverted to 4 RCS jets → 1,275 g net forward thrust (1,500 × 0.85)

**SCAD sources (Phase 11):**
- `aft_edf_plenum.stl` — EDF inlet plenum, 55 mm bore, 4× RCS bleed taps
- `rcs_distribution_manifold.stl` — Bleed-flow splitting (TBD split ratio, likely 85% forward / 15% RCS)
- `rcs_thruster_nozzle.stl` (×4) — Small convergent nozzles for RCS jets
- `middle_neck_intake_frame.stl` — Intake scoop window frame (Phase 11 variant with larger windows)

**Mass budget addition:**
- 55 mm EDF unit: ~95 g
- RCS servos (4× SG90): 4 × 9 g = 36 g
- RCS manifold + nozzles: ~50 g
- Wiring + mounts: ~20 g
- **Subtotal phase 11 additions: ~201 g**
- But rear nozzle housing replaces cowl tail (no net mass change there); **net Phase 11 Δ ≈ +362 g total**

### RCS System Architecture

**4× proportional-valve RCS thrusters** provide pitch and yaw control during forward flight:

| Axis | Thruster Pair | Control | Authority | Fail-Safe |
|------|---------------|---------|-----------|-----------|
| **Pitch** | Top (dorsal) + bottom (ventral) | Collective bleed-flow rate | ~15% of rear EDF mass flow → ~225 g-force equivalent at full deflection | Spring-return to closed (no RCS = neutral pitch) |
| **Yaw** | Port + starboard | Differential bleed flow | One side closed, other full open | Closed both (no yaw authority without thrust differential) |

**Firmware (Phase 11):**
- 4× proportional-valve PWM outputs on Inara (FC2, the aft node assigned by PACE)
- Attitude controller blends VTOL hover authority (nacelle tilt) with RCS bleed for forward-flight
  yaw/pitch (cross-fade as nacelle tilt reduces toward 0°)
- Fail-safe: loss of Inara → River (FC3) takes over RCS channels

**Bench testing:** RCS authority verified via thrust vector measurement before first forward-flight
(Phase 11 Phase 5.1 in the local Phase 11 WBS).

---

### Phase 11 Build Sequence (Conceptual)

*Estimated Phase 11 integration: 30–40 flight-test hours post-Phase-10.*

1. **Print phase 11 STLs** — neck intake frame, plenum, RCS nozzles, rear pod fairing
2. **Modify middle neck** — Remove temporary intake scoop covers; install permanent frame
3. **Bond plenum + manifold** — Structural epoxy at intake/manifold flanges; pressure-test
4. **Install EDF retaining ring** — Bracket at station ~430 mm inside rear pod
5. **Wire 50A ESC** (ESC5) to rear EDF; route signal to FC2 PRU Ch.2
6. **Install RCS servos & valves** — Bracket assembly on rear pod; servo arms → valve linkages
7. **Calibrate RCS valves** — Verify 0% closed and 100% full-bleed before first flight
8. **Flight test 1:** Hover-only, all RCS proportional-valves disabled (safety)
9. **Flight test 2:** Gradual forward transition (0° → 90° tilt) with RCS authority increasing
10. **Flight test 3:** Full envelope (cruise altitude, cross-wind, RCS failover)

---

### Phase 11 — Risk Mitigation

| Risk | Mitigation |
|------|------------|
| EDF over-thrust damages rear fuselage | Load-test STL with weights before flight; bond plenum with structural epoxy |
| Bleed-air backpressure damages intake | Design intake frame with pressure-relief divert (or over-size manifold for low loss) |
| RCS valve stiction or blockage | Use proportional servos (not on-off); test bleed-air pressure with manometer before flight |
| Loss of rear-EDF power during flight | Graceful degradation; aircraft can VTOL-return on nacelle EDFs alone (T/W ≈1.61) |
| Nacelle/RCS cross-control confusion | Separate PWM channels; firmware explicitly cross-fade between modes (test on bench) |

---

## Phase 12 — Range-Extender Battery Module (RBM)

### Secondary Battery Integration

**Concept:** Parallel a second 6S LiPo in the cargo gondola to extend endurance.

**Parallel connection strategy:**
1. Main battery → Kaylee main input (40A fuse, dual-rail failover, primary)
2. RBM battery → Kaylee RBM input (separate 40A fuse, tertiary power rail)
3. **No active balancing** — passive parallel with reverse-polarity diodes (like main dual-rail)
4. **Voltage monitoring:** PB2-I reads both battery voltages via Kaylee GPIO (ADC)
5. **Load sharing:** Diode-OR'd outputs; main battery supplies first ~100%, then RBM kicks in
   as main voltage droops under load

**Advantage:** Simple, no added complexity (Kaylee already has current-sharing diodes for dual rails).

**Field operation:**
- Nominal endurance: 8 minutes hover (Phase 5 baseline with 4000 mAh primary)
- With RBM (4000 mAh secondary): 12–13 minute hover (rough estimate; verify via flight test)
- Cargo capacity trade-off: RBM occupies one cargo-bay side bin; full 226 g payload ← cargo bay, not RBM space

### Phase 12 Hardware BOM

| Item | Qty | Mass | Specs | Status |
|------|-----|------|-------|--------|
| 6S LiPo battery (RBM) | 1 | ~500 g | 2000–4000 mAh, 100C, XT90-S | Procure per endurance testing |
| XT90-S quick-disconnect | 1 pair | ~10 g | Shielded connector | TBD part number |
| Reverse-polarity diode (SBM60/60A) | 2 | ~5 g | One per battery leg | SBM60 or equivalent 60A Schottky |
| Gondola battery tray | 1 | ~30 g | 3D-printed CF-PETG, fold-down | Design pending (Phase 12 SCAD) |

**Total RBM system mass:** ~545 g (battery dominating)

### Phase 12 Firmware (pwr_fault node)

Minimal changes to `pwr_fault` watchdog node:

```c
// Pseudo-code: monitor RBM + primary battery voltages
if (battery_main < 5.5V && battery_rbm > 5.5V) {
    // Main battery low; RBM is healthy
    log("RBM failover active");
    // No special action; Kaylee's diode-OR handling voltage automatically
}
if (battery_main < 5.5V && battery_rbm < 5.5V) {
    // Both batteries low; RTL immediately
    rtl_mode = true;
    log("Low battery RTL");
}
```

---

## Deferred Work Status & WBS

### Phase 11 Work Items (WBS Tracking)

| Item | Description | Status | Est. Hours |
|------|-------------|--------|------------|
| Phase 11 CAD | Aft EDF, plenum, RCS manifold, nozzles | ~70% complete | 10–15 |
| Intake frame geometry | Scoop window size (5mm²), frame structure | 50% complete | 5–8 |
| RCS valve selection | Datasheet verification, sizing | 50% complete | 3–5 |
| Bleed-air manifold design | Pressure drop analysis, split-ratio tuning | 30% complete | 8–12 |
| ESC5 firmware integration | PWM output, failover, cross-drive logic | 20% complete | 5–8 |
| Structural analysis | EDF mounting loads, bleed-air backpressure | 10% complete | 5–8 |
| Bench testing plan | Pressure-relief test, valve calibration procedure | 0% (draft only) | 3–5 |
| Flight test plan | Gradual envelope expansion, abort criteria | 0% (draft only) | 5–10 |

**Estimated Phase 11 completion (design phase):** 40–60 hours (1–2 person-weeks)  
**Estimated Phase 11 build/test:** 30–50 hours (3–5 days on-site with aircraft)

### Phase 12 Work Items

| Item | Description | Status | Est. Hours |
|------|-------------|--------|------------|
| RBM battery procure spec | Capacity, C-rating, vendor lock-in | 10% | 2–3 |
| Gondola battery tray CAD | Fold-down mount, strain relief | 0% | 3–5 |
| Diode-OR circuit verification | Kaylee schematic review, loss analysis | 30% | 2–3 |
| ADC firmware (voltage read) | GPIO input, telemetry logging | 0% | 2–3 |
| Endurance modeling | Flight-test data required; deferred | 0% | 4–6 |
| Bench discharge test | Verify parallel load-sharing, no crosstalk | 0% | 2–3 |

**Estimated Phase 12 completion (design):** 15–25 hours  
**Estimated Phase 12 build/test:** 8–12 hours (bench only; no flight)

---

## Work Planning & Triggers

### When to Start Phase 11?

**Prerequisite:** Phase 5–10 baseline flight testing complete and documented.

**Go/no-go criteria:**
1. ✅ Phase 5 first hover achieved; vehicle stable at ±15° tilt
2. ✅ Phase 6 all 8 nodes operating; OA working
3. ✅ Phase 7 cargo door + winch fully functional
4. ✅ Phase 9 performance envelope documented (thrust stand calibrated, T/W measured, endurance logged)
5. ✅ Phase 10 BVLOS mission successful; node failover proven

**Expected Phase 11 start:** 2026-Q4 (after summer field testing, assuming baseline is flight-proven)

### When to Start Phase 12?

**Prerequisite:** Phase 11 forward-flight envelope validated; RCS attitude authority proven.

**Trigger:** If Phase 9–10 endurance is <10 min and missions need >12 min loiter time.

**Expected Phase 12 start:** 2027-Q1 (conditional; may defer indefinitely if Phase 5–10
endurance meets mission needs)

---

## Documentation & References

| Document | Location | Purpose |
|----------|----------|---------|
| AGENTS.md | deferred/ | Policy for Phase 11+ design |
| WBS.md | deferred/ | Full task breakdown + narrative |
| TODO.md | deferred/ | Open Phase 11 + 12 items |
| NOZZLE_DRIVE_TRADE.md | docs/ | Aft nozzle design rationale (fixed vs. variable) |
| TILT_SPAR_ANALYSIS.md | docs/ | Structural analysis (applicable to rear pod) |
| aft-edf/README.md | deferred/aft-edf/ | Phase 11 design details (if created) |

---

## License

All deferred-phase documentation is **CC BY 4.0**.

See root [`LICENSE`](../LICENSE) and [`docs/attribution_and_licensing.md`](../docs/attribution_and_licensing.md)
for details.

---

*"I don't give a hump if you're green, blue, or purple. You fly the ship right, we get along." — Hoban Washburne*
