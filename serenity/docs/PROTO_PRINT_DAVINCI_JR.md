<!-- OpenDyslexic font for screen reading (CC BY 4.0) -->
<link rel="stylesheet" href="https://fonts.cdnfonts.com/css/opendyslexic">
<style>
body,p,li,td,th,code,pre{font-family:'OpenDyslexic','OpenDyslexicMono',sans-serif!important;line-height:1.8}
@media screen{body{background:#0d1117;color:#e6edf3}a{color:#58a6ff}
  h1,h2,h3,h4{color:#58a6ff;border-bottom:1px solid #30363d;padding-bottom:6px}
  code{background:#161b22;color:#e6edf3;padding:2px 6px;border-radius:4px}
  th{background:#21262d;color:#79c0ff}tr:nth-child(even)td{background:#161b22}
  blockquote{border-left:4px solid #388bfd;color:#8b949e;padding-left:12px}}
@media print{body{background:#fff!important;color:#111!important}a{color:#003399!important}}
</style>

# Serenity-Class Tiltrotor UAV — Prototype Print Guide
## XYZprinting da Vinci Jr. 1.0 w · PLA · Rev P Baseline

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Date:** 2026-06-01 | **Baseline:** Rev P

> Fan engineering work inspired by the Firefly-class transport ship *Serenity*
> from *Firefly* (Fox, 2002) and *Serenity* (Universal, 2005).
> © Joss Whedon / Mutant Enemy Productions — **Not an officially licensed product.**

---

## 1. Printer Reference

| Parameter | Value |
|-----------|-------|
| Printer | XYZprinting da Vinci Jr. 1.0 **w** (WiFi model) |
| Build volume | 150 × 150 × 150 mm |
| Nozzle | 0.4 mm (fixed, non-swappable) |
| Filament | 1.75 mm PLA — XYZ cartridge or compatible 3rd-party |
| Bed | Non-heated — apply glue stick before every plate |
| Slicer | XYZware 3.x (Windows / Mac) |
| Output format | `.3w` (WiFi print) or USB `.3w` file |

> **Note on XYZware settings:** XYZware exposes Quality (Draft/Normal/Fine),
> Fill %, Surface (shell count), Support (Off/Standard/Full), and Raft (On/Off).
> Temperature and speed are fixed per quality preset — 200 °C / ~40–50 mm/s for
> Normal PLA. All settings in this guide use those labels.

---

## 2. Global PLA Settings for All Prototype Prints

| Setting | Value | XYZware Control |
|---------|-------|-----------------|
| Quality | **Normal** (0.2 mm layers) | Quality → Normal |
| Nozzle temp | 200 °C (automatic for PLA) | — |
| Shell count | **2** | Surface → 2 |
| First layer | Automatic slow-down in firmware | — |
| Cooling | On after first layer (automatic) | — |
| Bed prep | Glue stick — light even coat | — |
| Raft | See per-batch table | Raft → On/Off |

> **Prototype vs. flight-spec:** Production prints use CF-PETG/PETG with 4 perimeters,
> 25–40% infill, and 0.15 mm layers. These PLA prototype settings prioritise speed and
> fit-checking, not structural performance. Do NOT fly any parts printed to this spec.

---

## 3. Part Inventory — Bounding Boxes and Scale Factors

All measurements are from actual STL bounding-box analysis (2026-06-01).
The da Vinci Jr. build volume is 150 × 150 × 150 mm.

### 3.1 Parts that Print at 1:1 (no scaling required)

| File | X mm | Y mm | Z mm | Notes |
|------|------|------|------|-------|
| `cargo_door_port.stl` | 108.0 | 33.7 | 87.0 | Rev P clamshell door |
| `cargo_door_stbd.stl` | 108.0 | 38.2 | 84.6 | Rev P clamshell door |
| `cargo_cradle_autolatch.stl` | 110.0 | 80.0 | 72.0 | Rev P auto-latch cradle |
| `cargo_door_servo_bracket.stl` | 44.0 | 28.0 | 5.0 | Rev P servo bracket |
| `cargo_release_servo_bracket.stl` | 44.0 | 28.0 | 5.0 | Rev P release bracket |
| `cargo_drv8833_tray.stl` | 36.0 | 33.0 | 6.0 | Rev P DRV8833 tray |
| `cargo_winch_motor_mount.stl` | 36.0 | 28.0 | 15.0 | Rev P winch mount |
| `cargo_winch_spool.stl` | 26.0 | 26.0 | 22.0 | Rev P winch spool |
| `cargo_gps_retention_ring.stl` | 50.0 | 50.0 | 2.5 | Rev P GPS ring |
| `cargo_fpv_bezel.stl` | 29.0 | 29.0 | 2.5 | Rev P FPV bezel |
| `nacelle_nozzle_petal.stl` | 31.0 | 22.8 | 19.5 | 50 mm EDF nozzle petal |
| `nacelle_nozzle_ring.stl` | 62.0 | 62.0 | 6.0 | 50 mm EDF iris ring |
| `rear_nozzle_frame.stl` | 131.0 | 131.0 | 20.0 | 120 mm EDF nozzle frame |
| `rear_nozzle_petal.stl` | 65.5 | 40.7 | 18.5 | 120 mm EDF petal |
| `s_eng_piv_outer_scaled24.stl` | 70.3 | 64.5 | 9.9 | Nacelle pivot housing |
| `s_eng_piv_pins_scaled24.stl` | 37.8 | 91.2 | 2.6 | Pivot pin holders |
| `s_pivot_arm_a_scaled24.stl` | 44.8 | 50.1 | 14.3 | Tilt pivot arm |
| `s_eng_pistons_scaled24.stl` | 32.8 | 58.9 | 13.2 | Piston fairings |
| `s_wings_both_shell24.stl` | 137.1 | 128.8 | 19.4 | Both wings — fits flat |
| `s_feet_x_4_scaled24.stl` | 78.2 | 98.4 | 9.0 | Landing feet ×4 |
| `s_edf_120_motor_mount.stl` | 126.0 | 126.0 | 53.0 | 120 mm EDF spider mount |
| `sector_gear_22mm.stl` | 28.5 | 28.5 | 4.0 | Sector gear (M0.5 era) |
| `bevel_gear_housing.stl` | 20.0 | 20.0 | 20.0 | Bevel gear housing |
| `pinion_a_bracket.stl` | 24.0 | 16.0 | 14.0 | Pinion A bearing bracket |

### 3.2 Parts that Require Scaling or Re-orientation

| File | Native size (mm) | Constraint | Scale | Scaled size (mm) |
|------|-----------------|------------|-------|-----------------|
| `s_eng_left_stator_shell24_50mm.stl` | 75.6 × 96.2 × 172.6 | Z=172.6 > 150 | **86%** | 65.0 × 82.7 × 148.4 |
| `s_eng_right_stator_shell24_50mm.stl` | 75.6 × 96.2 × 172.6 | Z=172.6 > 150 | **86%** | 65.0 × 82.7 × 148.4 |
| `s_head_shell24.stl` | 129.4 × 235.1 × 140.7 | Y=235.1 > 150 | **63%** | 81.5 × 148.1 × 88.6 |
| `s_middle_shell24.stl` | 177.1 × 164.8 × 73.2 | X=177.1 > 150 | **84%** | 148.8 × 138.4 × 61.5 |
| `s_cargo_sect_shell24.stl` | 194.7 × 203.6 × 163.2 | Y=203.6 > 150 | **73%** | 142.1 × 148.6 × 119.1 |
| `s_rear_shell24.stl` | 140.9 × 158.0 × 181.7 | Z=181.7 > 150 | **82%** | 115.5 × 129.6 × 149.0 |
| `s_legs_scaled24.stl` | 96.1 × 150.1 × 7.5 | Y=150.1 > 150 | **99%** | 95.1 × 148.6 × 7.4 |
| `s_edf_120_thrust_tube.stl` | 134.0 × 134.0 × 167.0 | Z=167.0 > 150 | **89%** | 119.3 × 119.3 × 148.6 |

> **Scale tip:** Enter the percentage in XYZware → Transform → Scale (uniform).
> Lock the aspect ratio checkbox. The fields accept a percentage value directly.

---

## 4. Print Schedule — 17 Batches

Parts are grouped to minimise machine time and maximise useful per-plate output.
Estimated times are for Normal quality (0.2 mm layers) at default XYZware speed (~45 mm/s).

### Batch A — Small Cargo Hardware (7 parts, 1 plate)

**Goal:** Verify all Rev P cargo hardware fits: servo pocket, DRV8833 tray, GPS ring,
FPV bezel, winch spool and mount geometry.

| Part | Qty | Orientation | Notes |
|------|-----|-------------|-------|
| `cargo_door_servo_bracket.stl` | 2 | Flat side down | Print 2× on same plate (separate 5 mm) |
| `cargo_release_servo_bracket.stl` | 1 | Flat side down | Identical footprint to door bracket |
| `cargo_drv8833_tray.stl` | 1 | Flat base down | No supports |
| `cargo_winch_motor_mount.stl` | 1 | Mounting face down | No supports |
| `cargo_winch_spool.stl` | 1 | Axis vertical | No supports |
| `cargo_gps_retention_ring.stl` | 1 | Flat (2.5 mm layer) | No supports — very flat, use raft |
| `cargo_fpv_bezel.stl` | 1 | Flat (2.5 mm layer) | No supports — print beside GPS ring |

| Setting | Value |
|---------|-------|
| Quality | Normal (0.2 mm) |
| Fill | **20%** |
| Surface | 2 shells |
| Support | **Off** |
| Raft | **On** (for thin flat parts) |
| Est. time | ~2.5 h total plate |

**Verify after print:**
- [ ] SG90 servo body drops into bracket pocket without force — pocket 23×12.5×22 mm
- [ ] DRV8833 breakout PCB (23×19 mm) snaps into tray — 4 snap tabs
- [ ] GPS ring 25 mm dia opening is round and clean
- [ ] N20 motor body (10×12 mm cross-section) fits winch mount saddle
- [ ] Spool bore (3 mm) fits a 3 mm rod cleanly

---

### Batch B — Port Cargo Door (1 plate)

**Goal:** Verify clamshell door hinge geometry, foam gasket channel, and door curvature
matches hull belly face (visual and caliper check against s_cargo_sect_shell24.stl from Batch I).

| Part | Qty | Orientation | Notes |
|------|-----|-------------|-------|
| `cargo_door_port.stl` | 1 | Outer hull face down (convex side down) | Supports on hinge tab only |

| Setting | Value |
|---------|-------|
| Quality | Normal (0.2 mm) |
| Fill | **20%** |
| Surface | 2 shells |
| Support | **Standard** (touching buildplate — hinge tab overhang) |
| Raft | **Off** (large flat footprint — good adhesion with glue stick) |
| Est. time | ~3 h |

**Verify after print:**
- [ ] Hinge tab bore (3.15 mm) fits a 3 mm CF or steel rod with slight clearance
- [ ] Inner mating flange has the 2×2 mm foam gasket channel visible
- [ ] Outer surface curvature matches hull section (lay against cargo_sect_shell24 print from Batch I)

---

### Batch C — Starboard Cargo Door (1 plate)

Mirror of Batch B. Settings and checks identical.

| Part | Qty | Orientation |
|------|-----|-------------|
| `cargo_door_stbd.stl` | 1 | Outer hull face down (convex side down) |

Settings: same as Batch B.

**Additional check:** Port and starboard doors should mate symmetrically along centre seam
with ≤1 mm gap when held together.

---

### Batch D — Cargo Auto-latch Cradle (1 plate)

**Goal:** Verify cradle footprint (≥50×50 mm payload area), latch tab geometry,
and pull-wire routing slot.

| Part | Qty | Orientation | Notes |
|------|-----|-------------|-------|
| `cargo_cradle_autolatch.stl` | 1 | Base down | Supports on latch tab overhang if present |

| Setting | Value |
|---------|-------|
| Quality | Normal (0.2 mm) |
| Fill | **25%** |
| Surface | 2 shells |
| Support | **Standard** (auto-detect latch tab) |
| Raft | **Off** |
| Est. time | ~2 h |

**Verify after print:**
- [ ] Internal 50×50 mm payload footprint is clear and flat
- [ ] Latch tab flexes without cracking (PLA is more brittle than PETG — note this)
- [ ] Pull-wire channel (1 mm groove) runs cleanly from latch tab to exit

---

### Batch E — Nozzle Iris Petals — 1 Nacelle Set (1 plate)

**Goal:** Verify 50 mm EDF nozzle petal geometry, hinge pin bore (3 mm), and
petal-to-petal clearance in the assembled ring.

| Part | Qty | Orientation | Notes |
|------|-----|-------------|-------|
| `nacelle_nozzle_petal.stl` | 8 | Flat (inner concave face up) | Arrange 4×2 grid on plate |

Plate footprint with 5 mm spacing: (31+5)×4 × (22.8+5)×2 = 144 × 55.6 mm — fits easily.

| Setting | Value |
|---------|-------|
| Quality | Normal (0.2 mm) |
| Fill | **15%** |
| Surface | 2 shells |
| Support | **Off** |
| Raft | **Off** |
| Est. time | ~1.5 h (8 petals together) |

**Verify after print:**
- [ ] 3 mm hinge pin bore is open and clean on all 8 petals
- [ ] Petals arranged in ring with nacelle_nozzle_ring (Batch F) and rotated — no binding

---

### Batch F — Nacelle Nozzle Ring (1 plate)

**Goal:** Verify 50 mm iris base ring size and inner rack tooth profile.

| Part | Qty | Orientation | Notes |
|------|-----|-------------|-------|
| `nacelle_nozzle_ring.stl` | 1 | Flat (tooth-side up) | No supports |
| `pinion_a_bracket.stl` | 2 | Any stable orientation | Batch with ring to fill plate |
| `bevel_gear_housing.stl` | 2 | Any | Batch with ring |
| `sector_gear_22mm.stl` | 2 | Flat | Batch with ring |

| Setting | Value |
|---------|-------|
| Quality | Normal (0.2 mm) |
| Fill | **20%** |
| Surface | 2 shells |
| Support | **Off** |
| Raft | **Off** |
| Est. time | ~1 h |

**Verify after print:**
- [ ] Nozzle ring OD fits flush inside nacelle nozzle petal assembly (from Batch E)
- [ ] Inner rack teeth are clean and visible (M=1.0 profile — 1 mm tooth pitch)
- [ ] Gear housing 20×20×20 mm — verify bevel bore size

---

### Batch G — Rear Nozzle Frame + Petals (1 plate, 2 prints)

**Goal:** Verify 120 mm EDF iris frame and petal count (8 moving + 8 fixed ribs).

> **Note:** rear_nozzle_frame (131×131×20 mm) is the largest single-plate item
> that fits at 1:1 with 19 mm of bed margin each side. Apply extra glue stick.

| Part | Qty | Orientation | Notes |
|------|-----|-------------|-------|
| `rear_nozzle_frame.stl` | 1 | Frame face down | Print alone — fills 131×131 footprint |

Then second print for petals:

| Part | Qty | Orientation | Notes |
|------|-----|-------------|-------|
| `rear_nozzle_petal.stl` | 4 | Flat (outer face down) | 4 per plate, 2 plates for full 8 |

| Setting (both prints) | Value |
|---------|-------|
| Quality | Normal (0.2 mm) |
| Fill | **20%** |
| Surface | 2 shells |
| Support | **Off** (frame ribs design for flat print) |
| Raft | **On** for frame (large footprint needs extra adhesion) |
| Est. time | ~3 h frame + ~1.5 h petals |

**Verify after print:**
- [ ] 8 fixed rib bases are solid — no delamination
- [ ] 120 mm EDF would seat inside frame ID (measure with calipers)
- [ ] Hinge pin bores (3 mm) open on all 8 petal slots in frame

---

### Batch H — Tilt Mechanism Parts (1 plate)

**Goal:** Verify nacelle pivot housing bore (accepts MF104ZZ bearing OD=10 mm),
pivot arm hole spacing, and piston fairing geometry.

| Part | Qty | Orientation | Notes |
|------|-----|-------------|-------|
| `s_eng_piv_outer_scaled24.stl` | 2 | Flat face down | Place 5 mm apart |
| `s_eng_piv_pins_scaled24.stl` | 2 | Flat (2.6 mm layer — print with Raft) | |
| `s_pivot_arm_a_scaled24.stl` | 2 | Flat face down | |
| `s_eng_pistons_scaled24.stl` | 2 | Flat face down | |

Plate footprint check: piv_outer (70.3×64.5)×2 side-by-side = 145.6×64.5 mm — fits.
Remaining space for pivot arms and pistons below.

| Setting | Value |
|---------|-------|
| Quality | Normal (0.2 mm) |
| Fill | **25%** |
| Surface | 2 shells |
| Support | **Off** |
| Raft | **On** for piv_pins (very thin flat part) |
| Est. time | ~2.5 h |

**Verify after print:**
- [ ] MF104ZZ bearing (OD=10 mm) presses into pivot housing bore — should be snug
- [ ] 4 mm CF rod passes through pivot housing centreline freely
- [ ] Pivot arm pushrod bore size correct (2 mm dia for steel pushrod)

---

### Batch I — 120 mm EDF Motor Mount (1 plate)

**Goal:** Verify spider arm geometry, hub bolt pattern (M3, 24 mm BC), and
forward spigot that registers in plenum bell.

| Part | Qty | Orientation | Notes |
|------|-----|-------------|-------|
| `s_edf_120_motor_mount.stl` | 1 | Motor face down (hub pointing up) | Supports on arms if needed |

| Setting | Value |
|---------|-------|
| Quality | Normal (0.2 mm) |
| Fill | **25%** |
| Surface | 2 shells |
| Support | **Standard** (spider arms may have small overhangs) |
| Raft | **Off** |
| Est. time | ~3.5 h |

**Verify after print:**
- [ ] 120 mm EDF motor outer can dimensions match hub bore
- [ ] M3 bolt holes on 24 mm BC are clear and aligned
- [ ] Forward spigot is round and concentric (calipers)

---

### Batch J — Port Nacelle Pod at 86% (1 plate)

**Goal:** Verify overall nacelle geometry, EDF bore clearance (scaled bore ≈47.3 mm —
NOTE: 50 mm EDF will NOT fit at 86%; this checks shape only), stator fin count,
and pivot boss locations.

> **Scale in XYZware:** Transform → Scale → 86% (uniform, all axes locked).

| Part | Qty | Orientation at 86% | Notes |
|------|-----|---------------------|-------|
| `s_eng_left_stator_shell24_50mm.stl` | 1 | Stand upright — intake face down | Scaled size: 65.0 × 82.7 × 148.4 mm height |

| Setting | Value |
|---------|-------|
| Quality | Normal (0.2 mm) |
| Fill | **15%** (shape check only) |
| Surface | 2 shells |
| Support | **Off** (tube prints well upright) |
| Raft | **On** (tall narrow print — raft improves base adhesion) |
| Est. time | ~8–10 h |

> **Tip:** Monitor first 30 layers. If there is any sign of layer shift,
> reduce the print speed to Slow in XYZware settings before continuing.

**Verify after print:**
- [ ] 11 stator fins visible in the Z=64..82 mm gap (at 86% of 75..95 mm = 64.5..81.7 mm)
- [ ] Pivot boss bump visible at Z≈71 mm (86% of 83 mm)
- [ ] Hub bore clear (~18 mm at 86% scale — EDF leads should pass)
- [ ] Overall shape matches reference images

---

### Batch K — Starboard Nacelle Pod at 86% (1 plate)

Identical to Batch J using `s_eng_right_stator_shell24_50mm.stl`.
Print with same settings. Verify CCW stator fins are mirrored vs. port pod.

---

### Batch L — Wings (1:1) + Landing Feet (1 plate)

**Goal:** Verify wing planform outline and landing foot flexibility.

| Part | Qty | Orientation | Notes |
|------|-----|-------------|-------|
| `s_wings_both_shell24.stl` | 1 | Flat (wing top-surface up) | Both wings in one file, fits flat |
| `s_feet_x_4_scaled24.stl` | 1 | Flat (bottom face down) | All 4 feet in one print |

Plate footprint: wings (137×128 mm) + feet (78×98 mm) — print separately, one per plate.

**Wings plate:**

| Setting | Value |
|---------|-------|
| Quality | Normal (0.2 mm) |
| Fill | **15%** |
| Surface | 2 shells |
| Support | **Off** |
| Raft | **Off** |
| Est. time | ~2.5 h |

> **Note:** The wing file contains both port and starboard wings joined. PLA is fine for
> visual check. The S1223 airfoil cross-section will be visible in the tip cross-section.

**Feet plate (separate print):**

| Setting | Value |
|---------|-------|
| Quality | Normal (0.2 mm) |
| Fill | **30%** (feet take landing impact — higher infill even for prototype) |
| Surface | 2 shells |
| Support | **Off** |
| Raft | **Off** |
| Est. time | ~1 h |

---

### Batch M — Landing Legs at 99% (1 plate)

> **Scale:** 99% uniform (reduces Y from 150.1 mm to 148.6 mm — just under 150 mm bed).

| Part | Qty | Orientation | Notes |
|------|-----|-------------|-------|
| `s_legs_scaled24.stl` | 1 | Flat (7.5 mm thickness vertical) | Long thin flat part |

| Setting | Value |
|---------|-------|
| Quality | Normal (0.2 mm) |
| Fill | **25%** |
| Surface | 2 shells |
| Support | **Off** |
| Raft | **On** (long narrow part — prevents warping lift at ends) |
| Est. time | ~1.5 h |

---

### Batch N — Head Shell at 63% (1 plate)

**Goal:** Hull silhouette and cockpit proportions check. Not for structural use.

> **Scale:** 63% uniform. Load `s_head_shell24.stl` → Transform → Scale → 63%.

| Part | Qty | Orientation at 63% | Scaled size |
|------|-----|---------------------|-------------|
| `s_head_shell24.stl` | 1 | Nose-up (cockpit facing down) | 81.5 × 148.1 × 88.6 mm |

| Setting | Value |
|---------|-------|
| Quality | Normal (0.2 mm) |
| Fill | **10%** (shape reference only) |
| Surface | 1 shell |
| Support | **Standard** (cockpit window overhangs) |
| Raft | **Off** |
| Est. time | ~4 h |

---

### Batch O — Mid Section at 84% (1 plate)

> **Scale:** 84% uniform. Load `s_middle_shell24.stl` → Transform → Scale → 84%.

| Part | Qty | Scaled size |
|------|-----|-------------|
| `s_middle_shell24.stl` | 1 | 148.8 × 138.4 × 61.5 mm |

Orient with the longest axis along X and the flat belly face down.

| Setting | Value |
|---------|-------|
| Quality | Normal (0.2 mm) |
| Fill | **10%** |
| Surface | 1 shell |
| Support | **Standard** |
| Raft | **Off** |
| Est. time | ~5 h |

---

### Batch P — Cargo Section at 73% (1 plate)

> **Scale:** 73% uniform. Load `s_cargo_sect_shell24.stl` → Transform → Scale → 73%.
> This is the pre-Rev-S shell — the Rev S SCAD with door cutout has not been exported
> to STL yet. Print this for hull shape reference; door opening geometry is verified
> separately via Batches B and C.

| Part | Qty | Scaled size |
|------|-----|-------------|
| `s_cargo_sect_shell24.stl` | 1 | 142.1 × 148.6 × 119.1 mm |

Orient with belly face down.

| Setting | Value |
|---------|-------|
| Quality | Normal (0.2 mm) |
| Fill | **10%** |
| Surface | 1 shell |
| Support | **Standard** |
| Raft | **Off** |
| Est. time | ~6 h |

---

### Batch Q — Rear Shell at 82% (1 plate)

> **Scale:** 82% uniform. Load `s_rear_shell24.stl` → Transform → Scale → 82%.

| Part | Qty | Scaled size |
|------|-----|-------------|
| `s_rear_shell24.stl` | 1 | 115.5 × 129.6 × 149.0 mm |

Orient with engine bell aft face down (largest circular opening on build plate).

| Setting | Value |
|---------|-------|
| Quality | Normal (0.2 mm) |
| Fill | **10%** |
| Surface | 1 shell |
| Support | **Standard** (engine bell undercut) |
| Raft | **Off** |
| Est. time | ~7 h |

---

## 5. Master Print Schedule and Time Estimate

| Batch | Key Parts | Scale | Prints/Plate | Est. Time | Priority |
|-------|-----------|-------|-------------|-----------|----------|
| A | Cargo small hardware (7 parts) | 1:1 | 1 | ~2.5 h | ★★★ |
| B | Cargo door port | 1:1 | 1 | ~3.0 h | ★★★ |
| C | Cargo door stbd | 1:1 | 1 | ~3.0 h | ★★★ |
| D | Cargo cradle autolatch | 1:1 | 1 | ~2.0 h | ★★★ |
| E | Nacelle nozzle petals ×8 | 1:1 | 1 | ~1.5 h | ★★ |
| F | Nacelle nozzle ring + gears | 1:1 | 1 | ~1.0 h | ★★ |
| G | Rear nozzle frame + petals ×8 | 1:1 | 2 | ~4.5 h | ★★ |
| H | Tilt mechanism parts | 1:1 | 1 | ~2.5 h | ★★ |
| I | 120 mm EDF motor mount | 1:1 | 1 | ~3.5 h | ★★ |
| J | Port nacelle pod | 86% | 1 | ~9.0 h | ★★ |
| K | Stbd nacelle pod | 86% | 1 | ~9.0 h | ★ |
| L | Wings + feet | 1:1 | 2 | ~3.5 h | ★ |
| M | Landing legs | 99% | 1 | ~1.5 h | ★ |
| N | Head shell | 63% | 1 | ~4.0 h | ★ |
| O | Mid shell | 84% | 1 | ~5.0 h | ★ |
| P | Cargo section shell | 73% | 1 | ~6.0 h | ★ |
| Q | Rear shell | 82% | 1 | ~7.0 h | ★ |
| **Total** | **17 batches · 19 prints** | | | **~72 h** | |

> **Priority key:** ★★★ = cargo system validation (Rev P focus); ★★ = propulsion /
> mechanism verification; ★ = hull visual check. Print ★★★ batches first — they can
> all be done in ~11 h of machine time.

---

## 6. Parts NOT Available as STL (require SCAD export first)

The following parts are in the Rev P design but do not yet have STL files in the
repository. Generate from SCAD before printing:

| Part | SCAD Source | Command |
|------|-------------|---------|
| Rev S cargo sect shell | `serenity/stl/s_cargo_sect_shell24.scad` | `openscad -o s_cargo_sect_shell24_revs.stl serenity/stl/s_cargo_sect_shell24.scad` |
| M=1.0 sector gear | `serenity/stl/nacelle_sector_gear.scad` | `openscad -o nacelle_sector_gear.stl serenity/stl/nacelle_sector_gear.scad` |
| M=1.0 drive pinions | `serenity/stl/nacelle_pinion.scad` | `openscad -o nacelle_pinion.stl serenity/stl/nacelle_pinion.scad` |
| M=1.0 bevel gear pair | `serenity/stl/nacelle_bevel_pair.scad` | `openscad -o nacelle_bevel_pair.stl serenity/stl/nacelle_bevel_pair.scad` |
| Rev O nacelle stator shells | `serenity/stl/nacelle_pod_50mm_tandem.scad` | `blender --background --python thingverse-serenity/blender_nacelle_revo.py` (requires Blender) |

> The sector_gear_22mm.stl, bevel_gear_housing.stl, and pinion_a_bracket.stl in
> `serenity/stl/` are from the Rev E M=0.5 era. Print them as shape references for
> the gear train concept, but note they are NOT the Rev O/P M=1.0 production geometry.

---

## 7. Bed Adhesion and PLA-Specific Notes

### 7.1 Glue Stick Application
Apply a thin, even coat of glue stick to the full bed surface before every plate.
Too much glue causes rough first layers; too little causes part detachment.
Allow glue to dry for 30 seconds before starting the print.

### 7.2 Raft vs. Brim
XYZware offers a raft option. Use raft for:
- Tall narrow prints (nacelle pods)
- Very thin flat parts (GPS ring, FPV bezel, piv_pins)
- First print on fresh glue stick layer

Skip raft for large flat parts with good bed contact (cargo doors, wing pair).

### 7.3 PLA vs. Production Materials
All production flight parts use CF-PETG (structural) or PETG (shells). PLA is
stiffer and more brittle. Expect:
- Snap-fit features (cargo cradle latch tab) to be more fragile than PETG versions
- Threaded bores to be tighter — chase with drill bit if needed
- PLA parts are NOT suitable for heat exposure (deforms above ~60 °C)
- Door hinge pins and pivot rods: use real CF rod / SS rod for these tests; do not
  attempt to print the rods in PLA

### 7.4 Support Removal
XYZware support material is the same PLA as the part. Remove with flush cutters
and hobby knife. Support contact surfaces will be rough — sand to 320 grit if
surface finish matters for the fit check.

---

## 8. Post-Print Verification Checklist

### Cargo System (Batches A–D)
- [ ] Both cargo doors fit against s_cargo_sect_shell24 belly curve (Batch P)
  — gap ≤2 mm along full door length
- [ ] Port and starboard door hinge tabs interdigitate (no interference)
- [ ] SG90 servo fits both servo brackets (no binding)
- [ ] DRV8833 PCB fits tray, connector cutout aligns with JST-PH connector
- [ ] Winch spool free-spins on 3 mm shaft; no wobble
- [ ] GPS retention ring lies flat against door inner face; 25 mm opening centred
- [ ] FPV bezel 28 mm dia opening centred and round

### Nozzle Iris — Nacelle (Batches E–F)
- [ ] 8 petals install onto ring base with 3 mm pins; all rotate freely
- [ ] Petal closed position: petals form a smooth disc with no gaps >1 mm
- [ ] Petal open: 75° total ring rotation clears all petals without binding
- [ ] Inner ring rack teeth engage a makeshift pinion (pencil, 6 mm dowel)

### Rear Nozzle (Batch G)
- [ ] 8 petals install in frame with 3 mm pins; rotate freely
- [ ] Frame inner diameter: calipers should read 120±2 mm for EDF seat

### Tilt Mechanism (Batch H)
- [ ] MF104ZZ bearing (OD=10 mm) presses into pivot housing — light tap with thumb
- [ ] Pivot arm: 4 mm shaft bore fits 4 mm CF rod; arm rotates smoothly
- [ ] Piston fairing snaps over pivot arm without binding

### EDF Mount (Batch I)
- [ ] 3-arm spider is rigid — no flex at arm mid-span with thumb pressure
- [ ] Forward spigot is round; OD matches plenum bell ID (measure from rear_shell24 throat)

### Nacelle Pods (Batches J–K)
- [ ] 11 stator fins visible and equally spaced in the inter-EDF gap zone
- [ ] Pivot boss bump palpable at correct axial location
- [ ] Hub bore clear (18 mm dia at 86% scale)

### Hull Assembly Mock-up
- [ ] Head + Mid + Cargo + Rear sections align at seam faces (scaled versions)
- [ ] Nacelle pods sit visually centred above wing attachment zones
- [ ] Wing planform matches canonical Serenity profile reference images

---

## 9. Known Limitations of This Prototype Set

1. **Nacelle pods at 86%:** bore ID is 47.3 mm — a 50 mm EDF will NOT fit. This
   prototype checks shape and stator geometry only. For EDF fit check, a 1:1 print
   is required; split the nacelle at the stator mid-point (Z≈83 mm) into two pieces
   to fit the 150 mm bed, then test-assemble.

2. **Rev S cargo sect shell not yet exported:** Batch P uses the pre-Rev S STL (no
   door cutout). Export `s_cargo_sect_shell24_revs.stl` from the updated SCAD and
   print at 73% once available.

3. **M=1.0 gear train parts not yet exported:** The Rev O M=1.0 sector gear, pinions,
   and bevel pair SCADs exist but have no STL in the repo. The serenity/stl/ gear STLs
   are M=0.5 era. Generate from SCAD (Section 6) for accurate gear mesh testing.

4. **Hull sections are at different scale factors:** Batches N–Q use different scales
   (63%–84%) to fit each section on the bed. A single assembly mock-up will NOT be to
   a consistent scale. For a consistent reduced-scale hull, scale all hull sections to
   the most restrictive common factor = 63% (head_shell24 constraint), then all sections
   will be at 63% of 24" = 15.1" hull.

5. **PLA is fragile at these thin walls:** Hull sections at 1 shell / 10% infill will
   be very fragile. Handle carefully; these are visual reference only.

---

*© 2026 Steve Griffing, PE(CSE) [Control Systems Engineering], CISSP-ISSEP, CPP — CC BY 4.0*
*Hull: Peter Farell CC BY 4.0 · Nozzles: BamJr CC BY 4.0 · Inspiration: Firefly/Serenity © Joss Whedon / Mutant Enemy / Universal*
