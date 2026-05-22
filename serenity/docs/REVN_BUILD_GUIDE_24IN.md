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

# Serenity-Class Tiltrotor UAV — Build Guide Rev N (24-inch)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0  
**Year:** 2026 | **Status:** Public release

> Fan engineering work inspired by the Firefly-class transport ship *Serenity*  
> from *Firefly* (Fox, 2002) and *Serenity* (Universal, 2005).  
> © Joss Whedon / Mutant Enemy Productions — **Not an officially licensed product.**

---

## Attribution

| Work | Author | License | Source |
|------|--------|---------|--------|
| Hull geometry | misubisu / Peter Farell | CC BY 4.0 | printables.com/model/548545 |
| Iris nozzle concept | BamJr | CC BY 4.0 | thingiverse.com/thing:2991269 |
| Blueprint proportions | Mandel + Earls / QMx / Universal | © 2007 QMx | 269 ft × 170 ft × 79 ft ratios |
| All other design | Steve Griffing | CC BY 4.0 | This project |

---

## End-State Specifications (Rev N)

| Parameter | Value |
|-----------|-------|
| Hull length | 609.6 mm (24.00″) |
| Beam (nacelle tip-to-tip) | ~486 mm |
| Hull material | PETG (2.5 mm skin, 2 lb/ft³ closed-cell foam fill) |
| Propulsion | 2× (2× 50mm EDF @ 6S, tandem series) nacelles + 1× 120mm EDF @ 6S fuselage |
| Counter-rotation | Port nacelle EDFs: CW from intake | Starboard: CCW — zero net torque reaction |
| Inter-stage stators | 8-fin twisted stator, integrated into each nacelle print (CF-PETG) |
| Nacelle tilt | 0° (cruise) → 90° (hover) → 120° (backing); hard stops −5° / 140° |
| Tilt actuation | 1× digital servo per nacelle (≥25 kg·cm @ 6V), fuselage-mounted |
| Iris nozzles | 2× nacelle (gear-linked to tilt pivot, no dedicated servo) + 1× rear (SG90 servo) |
| Nozzle closed | 0° nacelle tilt → petals form hull-matched engine cone (Serenity skin) |
| Nozzle open | 90° nacelle tilt → petals hinge out, LED-backlit translucent-blue inner faces |
| Rear EDF | 120mm @ 6S, exhaust straight aft; intake via 4 radial scoops at neck station ~310mm (dorsal/port/ventral/stbd; CF-PETG frame + PETG plenum manifold) |
| Total thrust | ~5,322 g (1,822 g nacelles + 3,500 g rear) |
| Hover T/W | ~1.50 at 6S 4000mAh (~3,550 g AUW) |
| Avionics | 8× PocketBeagle 2 Industrial (AM6254): FC1–FC4 (Cape-A) + CN1–CN4 (Cape-B) |
| Cargo | 101.6 × 76.2 × 76.2 mm bay, clamshell doors, N20 winch |
| Build estimate | ~100–120 hours across all phases |

---

## Anti-Rework Rules — Read Before Phase 0

1. **Print everything before first epoxy joint.** Filament costs pennies compared to build time.
2. **Install every conduit, standoff, void former, and sensor mount before the foam pour.** Once foam cures these cannot be added.
3. **The foam pour is the point of no return.** Do a full dry-fit with all wiring and components before mixing.
4. **Do NOT foam the nacelle interior.** Nacelles are CF-PETG structural shells — foam in the bore traps EDF heat and ruins the press-fit.
5. **Verify EDF rotation direction before nacelle installation.** Port EDFs must rotate CW from the intake end; starboard CCW. Swap any two motor leads to reverse if wrong. Once nacelle is sealed and fiberglassed, this is a full disassembly.
6. **Gear-mesh the nozzle linkage before bonding the tilt bracket.** Check nozzle opens smoothly through the full 0°–90° sweep before epoxying the sector gear.
7. **FAA registration on airframe before first untethered flight.** Replace placeholder with your issued number.
8. **TPM 2.0 provisioning is non-reversible.** Provision all 8 nodes before first flight.

---

## Phase Overview

| Phase | Name | Milestone | Est. Cost |
|-------|------|-----------|-----------|
| 0 | Print All Parts + CF Cuts | All parts ready | ~$85 |
| 1 | Hull Structure + Provisions | Hull sealed, all conduits installed, foam-ready | ~$90 |
| 2 | Nacelle Assembly | Both nacelles complete with EDFs, stators, nozzle linkage | ~$190 |
| 3 | Tilt Mechanism | Nacelles mount, pivot, and tilt on fuselage | ~$80 |
| 4 | Rear EDF + Nozzle | Rear 120mm EDF mounted, nozzle frame and iris operational | ~$250 |
| 5 | Hull Foam Pour + Close-up | Structural foam cured, all access panels fitted | ~$30 |
| 6 | Minimum Viable Flyer (4 nodes) | ★ **FIRST FLIGHT** (CN1+FC1+CN2+FC2) | ~$640 |
| 7 | Full 8-Node Architecture | All 8 nodes, full ring redundancy | ~$480 |
| 8 | Cargo System | 250 g delivery operational | ~$30 |
| 9 | Finishing: Decals + FAA + Docs | Legal, complete, documented | ~$25 |

> Costs are USD estimates as of 2026. PCB assembly assumes JLCPCB pricing.

---

## Phase 0 — Print All Parts + CF Cuts

**Goal:** Every printed part complete and dry-fitted before Phase 1 begins.

### Printer Setup

| Setting | Value |
|---------|-------|
| Nozzle | Hardened steel (CF-PETG abrades brass — required for nacelles, brackets) |
| Bed | PEI spring steel, leveled |
| PETG profile | 230°C / 70°C bed |
| CF-PETG profile | 240–245°C / 80°C bed |
| TPU 95A profile | 220°C / 50°C bed, direct drive only |
| Dry time | 6 h at 65°C for all filament before printing |

### Print Schedule

| STL | Material | Layer | Infill | Qty | Notes |
|-----|----------|-------|--------|-----|-------|
| `s_head_shell24.stl` | PETG | 0.20 mm | 8% gyroid | 1 | Nose-down orientation |
| `s_middle_canonical_shell24.stl` | PETG | 0.20 mm | 8% gyroid | 1 | Canonical belly — NO belly scoop. Generate from `serenity/stl/s_middle_canonical_shell24.scad`. |
| `s_cargo_sect_shell24.stl` | PETG | 0.20 mm | 8% gyroid | 1 | |
| `s_rear_neck_intake_shell24.stl` | PETG | 0.20 mm | 8% gyroid | 1 | 4 radial scoop windows at neck station ~310mm. Generate from `serenity/stl/s_rear_neck_intake_shell24.scad`. Verify NECK_X alignment in slicer after generating. |
| `s_neck_intake_frame.stl` | **CF-PETG** | 0.15 mm | 40% gyroid, 4 walls | 1 | Structural intake frame ring — bonds into 4 scoop windows. Hardened-steel nozzle required. Generate from `serenity/stl/s_neck_intake_frame.scad`. |
| `s_aft_edf_plenum.stl` | PETG | 0.20 mm | 20% gyroid | 1 | Cross-shaped 4-to-1 plenum manifold. Generate from `serenity/stl/s_aft_edf_plenum.scad`. Pressure-test before hull close-up. |
| `s_wings_both_shell24.stl` | PETG | 0.20 mm | 8% gyroid | 1 | |
| `s_eng_left_stator_shell24.stl` | **CF-PETG** | 0.15 mm | 25% gyroid, 4 walls | 1 | Port nacelle — run `blender_nacelle_integrated_v1.py` first to generate |
| `s_eng_right_stator_shell24.stl` | **CF-PETG** | 0.15 mm | 25% gyroid, 4 walls | 1 | Starboard nacelle |
| `s_eng_piv_outer_scaled24.stl` | **CF-PETG** | 0.15 mm | 40%, 4 walls | 2 | Pivot housing; verify 4mm rod press-fit |
| `s_eng_piv_pins_scaled24.stl` | **CF-PETG** | 0.15 mm | 40% solid, 4 walls | 2 | |
| `s_eng_pistons_scaled24.stl` | PETG | 0.20 mm | 20% gyroid | 2 | Decorative fairings |
| `s_pivot_arm_a_scaled24.stl` | **CF-PETG** | 0.15 mm | 40%, 4 walls | 2 | Carries tilt servo pushrod |
| `nacelle_nozzle_petal.stl` | PETG (body) + translucent-blue PETG (inner face) | 0.20 mm | 20% gyroid | 16 | 8 per nacelle; print inner face swap if dual-material unavailable |
| `nacelle_nozzle_ring.stl` | **CF-PETG** | 0.15 mm | 40% | 2 | Base ring; seals to nacelle nozzle exit face |
| `rear_nozzle_petal.stl` | PETG + translucent-blue inner | 0.20 mm | 20% gyroid | 8 | 38° span; print flat |
| `rear_nozzle_frame.stl` | **CF-PETG** | 0.15 mm | 30% | 1 | One-piece ring + 8 fixed ribs |
| `s_feet_x_4_scaled24.stl` | **TPU 95A** | 0.25 mm | 40% | 1 | Direct-drive extruder required |
| `s_legs_scaled24.stl` | **CF-PETG** | 0.15 mm | 30% | 1 | |
| Tilt bracket w/ sector gear | **CF-PETG** | 0.12 mm | 40%, 4 walls | 2 | 0.12mm layer for M0.5 tooth accuracy |
| Drive pinion (R=6mm, M0.5) | PETG or resin | 0.12 mm | 40% | 4 | 2 per nacelle (one either end of bevel shaft); resin gives best tooth finish |
| Bevel gear pair (1:1, M0.5) | PETG or resin | 0.12 mm | 40% | 2 sets | 4 gears total; or source machined |
| Nozzle inner ring (rack R=28mm) | PETG | 0.12 mm | 40%, 3 walls | 2 | Print vertically for tooth accuracy |
| Access panel frames (A–F) + lids | PETG | 0.20 mm | 100% | 1 set | 6 frames + 6 lids; 2mm wall |

### CF Cuts

| Part | Material | Dimension | Notes |
|------|----------|-----------|-------|
| Keel | CF flat bar 6×3mm | 620 mm | Mark datums at 91, 165, 251, 320, 388mm from nose |
| Wing spars | CF tube 12mm OD / 1.5mm wall | 2× 380 mm | Sand spar ends to fit wing-root spar pockets |
| Pivot rods | CF solid rod 4mm OD | 2× cut to length per pivot housing drawing | Deburr ends; press-fit into MF104ZZ bearings |
| Ring frames | CF plate 2mm | 5 profiles per station drawing | Fit to keel slot-notches |

> ⚠ **CF dust hazard.** Wear N95 mask + safety glasses. Cut outdoors or with dust extraction.

### Phase 0 Checks

- [ ] Nacelle bore caliper check: 55.0–56.0 mm ID at Z=10 mm and Z=80 mm
- [ ] Stator fins visible inside nacelle bore at Z≈63 mm (between the two EDF seats)
- [ ] Hub bore clear at stator: 16 mm ID minimum (for EDF motor leads)
- [ ] Tilt bracket gear dry-mesh: sector ↔ pinion backlash 0.1–0.2 mm
- [ ] Nozzle ring fits flush on nacelle exit face; petals hinge freely on 3mm pins
- [ ] 4mm CF pivot rod slides through pivot housing with MF104ZZ bearings seated
- [ ] All access panel lids flush ±0.2 mm in frames

---

## Phase 1 — Hull Structure + All Future Provisions

**Goal:** Structurally complete hull with every conduit, standoff, void former, access panel, and cargo hard point installed — ready for foam pour.

### Buy List

| Item | Qty | Notes |
|------|-----|-------|
| West System 105/206 epoxy | 1 kit | Keel + spar bonding |
| 5-minute epoxy syringe 25mL | 3× | Access frames, sensor mounts, standoffs |
| X-30 polyurethane foam 2-part | ~600 mL kit | 2 lb/ft³, 4× expansion, 2-min pot life |
| EPS blue foam board 25mm | 500×250mm | Void formers A–E (bay + cargo cutouts); Owens Corning Foamular 150 |
| Johnson's Paste Wax | 1 tin | 2 coats on all EPS void surfaces (release agent) |
| 3M 4016 closed-cell gasket tape | 1 roll | Seal all access panel frame lips |
| PTFE tube 5mm OD × 3mm ID | 6 m | 8 conduits (CAN FD, RS-485, 1553, ETH×4, PWR) |
| M2.5 nylon hex standoffs 6mm | 16× | Cape-B floor mounts (4 per bay × 4 bays) |
| M2.5 nylon hex standoffs 20mm | 16× | Cape-A inter-cape spacing |
| M2.5 × 8mm SS button screws | 64× | Standoff attachment + panel B/E fasteners |
| M3 heat-set inserts | 4× | Cargo gondola belly hard points |
| N42 neodymium disc magnet 6×2mm | 8× | Panel D (4 in frame + 4 in lid) |
| SMA panel-mount bulkhead | 3× | 915MHz SiK (belly) + LoRa (belly) + WiFi (dorsal fwd). Note: 49MHz RCRS now uses a dorsal wire antenna — no belly SMA for that system |
| PETG wire post (49MHz fwd + aft) | 2× | Print from s_rcrs49_wire_post.scad: forward post (~120mm from nose, dorsal) + aft post (top of rear nozzle cone). Both ~10mm tall insulated hooks |
| 0.3mm stainless steel wire or 22AWG enamelled Cu | ~500mm | 49MHz RCRS top wire |
| Ceramic bead insulator (3mm ID) | 1× | Aft end of 49MHz wire (insulated/open) |
| Wing spar pocket inserts | 4× | CF spar sleeve inserts bonded into fuselage side walls at wing root |

### Installation Sequence

> **Critical:** Complete steps 1–12 before mixing any foam (step 13).

**1. Epoxy keel through all hull sections.** Datum marks at 91, 165, 251, 320, 388mm. Cure 2 h minimum.

**2. Bond ring frames to keel** at all 5 station notches. Cure 1 h.

**3. Bond access panel frames A–F into hull sections:**

| Panel | Station (mm) | Bay | Closure |
|-------|-------------|-----|---------|
| A — Nose | 0–91 | CN1+FC1 | Bayonet PETG frame |
| B — Dorsal Fwd | 91–165 | CN2+FC2 | 4× M2.5 screws |
| C — Cargo Belly | 160–251 | Cargo | Hinge + latch |
| D — Dorsal Aft | 251–320 | CN3+FC3 | 4× N42 magnets |
| E — Aft Service | 320–388 | CN4+FC4 | 4× M2.5 screws |
| F — Rear | 388–609 | EDF access | Bayonet PETG frame |

**4. Install M2.5 nylon standoffs in bays A, B, D, E.**
- Floor standoffs (6mm): Cape-B (90×60mm) hole pattern
- Inter-cape standoffs (20mm): Cape-A (85×55mm) hole pattern above Cape-B
- Verify 44mm total stack height clears bay void former

**5. Bond wing spar pocket inserts** at wing root stations, both sides. Spar must slide freely in/out for nacelle assembly access.

**6. Bond tilt servo mount brackets** into fuselage interior at wing root bays (one bracket per nacelle tilt servo). Servo arm must clear all wiring conduits.

**7. Install M3 heat-set inserts ×4** at belly cargo hard-point locations.

**8. Install antenna posts and SMA bulkhead pass-throughs:**
- Belly port, X≈**260mm**: SiK 915MHz SMA-RP bulkhead *(relocated forward from 310mm — station 310mm is now the neck intake ring; 260mm is in cargo bay belly, Panel C, clear of intake frame)*
- Belly stbd, X≈260mm: LoRa RFM95W 915MHz SMA-RP bulkhead
- Dorsal, X≈**120mm**: **49MHz RCRS-49 forward wire post** — PETG insulated mast (~10mm tall, 12×12mm foot), bonded to dorsal hull skin just aft of bridge/cockpit section; loading coil + LC pi-network at this post; RG-316 coax routed internally to Bay A RCRS-49 module *(replaces dorsal fin + vertical whip — wire now runs nose-to-tail along hull spine)*
- Rear nozzle cone top: **49MHz RCRS-49 aft wire post** — PETG hook post (~10mm tall) bonded to top of `rear_nozzle_frame.stl`; electrically open (insulated end)
- Dorsal fwd, X≈140mm: WiFi 2.4/5GHz antenna
- **49MHz top wire**: 0.3mm stainless steel wire or 22AWG enamelled copper, ~470mm, strung from forward post hook to aft post hook with light tension (~20g); CF keel bar connected to RCRS-49 GND as counterpoise
- **⚠ GPS clearance check**: forward wire post at ~120mm is ~43mm from GPS patch (both dorsal face). Bench-verify GPS HDOP ≤1.5 with RCRS-49 transmitting before flight. If GPS degrades, move GPS patch to ≥165mm from nose.

**9. Install 12× ToF sensor flush-mount PETG frames** (6.5mm hull cutouts):

| Sensor | X (mm) | Position | Array |
|--------|---------|----------|-------|
| S1A / S1B | 30, 50 | Nose ring | A / B |
| S3B / S4B | 180 | Port / Stbd hull sides | B |
| S3A / S4A | 240 | Port / Stbd hull sides | A |
| S6A / S6B | 195, 265 | Belly blisters | A / B |
| S5A / S5B | 215, 315 | Dorsal keel | A / B |
| S2B / S2A | 510, 525 | Rear bell rim | B / A |

**10. Feed 8× PTFE conduits nose-to-tail.** Thread pull strings immediately:

| Conduit | Route | Signal |
|---------|-------|--------|
| CAN-FD | Port keel rail | CAN FD ring — 120Ω term at CN1 and FC4 |
| RS-485 | Stbd keel rail | RS-485 multidrop — 120Ω at CN1 and FC4 |
| 1553-A | Port upper | MIL-STD-1553 bus A |
| 1553-B | Stbd upper | MIL-STD-1553 bus B |
| ETH-1 | Port lower | Ethernet ring segment |
| ETH-2 | Stbd lower | Ethernet ring segment |
| SERVO-PWR | Belly centerline | 6V servo bus + PWM signal harness |
| MAIN-PWR | Belly centerline | 10AWG main power from battery to PDB |

**11. Install EPS void formers** (waxed 2×) in all bays. Verify pull strings clear voids.

**12. Full dry-fit verification:**
- [ ] All 8 conduits routed and pull strings accessible at both ends
- [ ] All standoffs installed and fastener access clear through access panel opening
- [ ] EPS void formers seated without gaps at hull inner wall
- [ ] SMA bulkheads installed and dusted
- [ ] Cargo inserts flush with belly skin

**13. Foam pour.** Mix per manufacturer ratio. Pour in sections from aft forward. Do NOT pour into nacelle bays or pivot housing areas. Allow 24 h full cure before removing void formers.

**14. Remove EPS void formers.** Strip wax film with isopropyl alcohol. Install access panel lids; verify flush fit.

### Phase 1 Checks

- [ ] Hull rigid — no flex when held at nose and tail
- [ ] All 8 pull strings accessible
- [ ] All standoffs in place; screws start freely
- [ ] Foam not in nacelle mounting bay, pivot housing, or access panel bays

---

## Phase 2 — Nacelle Assembly

**Goal:** Both nacelles fully assembled — EDFs installed, stators integral, nozzle iris fitted, gear linkage dry-meshed and verified.

### Materials Needed

| Item | Qty | Notes |
|------|-----|-------|
| 50mm EDF @ 6S | 4 | 2 per nacelle |
| 40A 6S ESC (BDSHOT) | 4 | 1 per EDF |
| 3mm × 5mm SS hinge pins | 16 | 8 per nacelle nozzle |
| 0.8mm piano wire | ~600mm | Link rings for nozzle petals |
| M0.5 bevel gear pair (1:1) | 2 sets | One per nacelle |
| M0.5 drive pinion R=6mm | 4 | 2 per nacelle (one each end of bevel shaft) |
| Longitudinal nozzle shaft (steel 2mm OD) | 2× ~60mm | Links bevel output to crown pinion in nacelle |
| M0.5 crown pinion R=6mm | 2 | One per nacelle, drives nozzle inner ring |
| WS2812B LED ring (nozzle size) | 2 | One per nacelle duct exit |
| Structural epoxy (slow cure) | — | EDF casing bonding |
| 3-wire servo extension 150mm | 4 | ESC signal leads |
| Wire sleeve 8mm | ~500mm | Bundle ESC + motor leads in hub bore |

### 2A — EDF Installation

**For each nacelle** (port first, then starboard — VERIFY ROTATION DIRECTION DIFFERS):

1. **Test EDF rotation direction before installation.** Connect to bench ESC + power supply (safe prop/duct test only). 
   - Port EDF must spin **CW viewed from intake** (fore end).
   - Starboard EDF must spin **CCW viewed from intake**.
   - To reverse: swap any two motor phase wires at the ESC.

2. **Install EDF2 (downstream — aft EDF):**
   - Feed motor leads through hub bore (16mm ID) from aft end.
   - Slide EDF2 into nacelle from aft (nozzle) end, Z=0.
   - Seat EDF2 casing at Z=5mm shoulder. Casing OD should be snug in bore.
   - Apply 3 small dabs of slow-cure structural epoxy around EDF2 casing at the Z=50mm stator shoulder. Do not foul fin channels.
   - Route ESC1/ESC2 signal wire through hub bore alongside motor leads.

3. **Route EDF2 leads through hub bore** and bring them out the fore (intake) end alongside stator fins. Bundle with wire sleeve.

4. **Install EDF1 (upstream — fore EDF):**
   - Feed EDF1 leads through from fore end.
   - Slide EDF1 in from fore end, seat at Z=76mm.
   - Verify stator fins are visible and clear in Z=53–73mm gap between EDFs.
   - Apply 3 dabs epoxy at EDF1 casing at Z=76mm shoulder.

5. **Install ESC pair** against hub bore inner wall or in fuselage (route leads through spar conduit to fuselage bay). ESC heat must not be trapped inside nacelle bore — route ESCs to fuselage bay via spar conduit.

6. **Cure 2h minimum** before proceeding.

### 2B — Nozzle Iris Assembly

For each nacelle nozzle:

1. **Press nacelle_nozzle_ring.stl** onto the nacelle aft (nozzle) exit face (Z=0). Confirm flush seating.

2. **Install nozzle inner ring** (rack, R=28mm) inside the base ring — this is the driven element.

3. **Bend piano wire link ring** (0.8mm wire): one closed ring that passes through all 8 petal link holes and loops around the inner ring posts. The ring translates radial rotation of the inner ring into petal rotation.

4. **Install 8 petals** on 3mm hinge pins. Hinge pins press into base ring lugs. Each petal sits on one hinge pin; the piano wire link passes through the petal's bottom lug.

5. **Dry-test:** manually rotate the inner ring through its travel. Petals should open smoothly from closed (hull-matched position) to ~75° open. Check for binding.

6. **Install WS2812B LED ring** at duct exit lip inside the base ring. Three-wire lead routes through hub bore to fuselage LED driver (Cape-B).

### 2C — Gear Linkage Installation

The nozzle iris is driven passively from the tilt pivot — no dedicated servo.

**Gear train (per nacelle):**

```
Tilt pivot rotation
    ↓
Sector gear (R=22mm, fixed to tilt bracket — does NOT rotate with nacelle)
    ↓ meshes with ↓
Drive pinion (R=6mm, mounted on nacelle outer shell — rotates with nacelle body)
    Ratio: 22/6 ≈ 3.67:1 → 90° nacelle = 330° pinion rotation
    ↓ via ↓
1:1 Bevel gear pair (90° axis redirect — converts nacelle-axis rotation to longitudinal shaft)
    ↓ via ↓
Longitudinal shaft (2mm steel rod, ~60mm, runs forward inside nacelle wall)
    ↓ meshes with ↓
Crown pinion (R=6mm) → Nozzle inner ring rack (R=28mm)
    Final ratio: (6/28) × 330° ≈ 70.7° ring rotation for full 90° nacelle sweep
```

**Assembly steps:**

1. Mount sector gear to tilt bracket (fixed — does not move with nacelle).
2. Mount drive pinion on nacelle outer shell at pivot axis. Verify mesh with sector gear; set backlash 0.1–0.2mm.
3. Install bevel gear pair in nacelle body. Input shaft = nacelle-body-axis; output = longitudinal shaft toward nozzle.
4. Thread longitudinal 2mm steel shaft through nacelle wall channel toward nozzle end.
5. Mount crown pinion on longitudinal shaft at nozzle end. Verify mesh with nozzle inner ring rack; set backlash 0.1–0.2mm.
6. **Sweep test:** manually rotate nacelle from 0° to 90°. Nozzle inner ring should rotate ~71°; petals should open from fully closed to fully open.
7. Verify nozzle inner ring hard stop prevents over-drive at nacelle angles 90°–120°.
8. Confirm petal closed position matches nacelle hull profile at 0°.

### 2D — Nacelle Final Check

- [ ] EDF1 and EDF2 both bonded and leads routed
- [ ] Port nacelle EDF rotation: CW from intake
- [ ] Starboard nacelle EDF rotation: CCW from intake
- [ ] Stator fins visible in Z=53–73mm gap (clear of both EDF casings)
- [ ] Nozzle iris opens/closes smoothly through full nacelle sweep
- [ ] Petal closed position: hull-match profile flush at 0°
- [ ] Petal open position: all 8 petals visible and even at 90°
- [ ] LED ring installed and wired

---

## Phase 3 — Tilt Mechanism

**Goal:** Both nacelles mounted on fuselage, pivot freely on bearings, tilt driven by fuselage-mounted servos with correct hard stops.

### Materials Needed

| Item | Qty | Notes |
|------|-----|-------|
| Nacelle tilt servo ≥25 kg·cm @ 6V, metal gear, digital | 2 | e.g. DS3218MG class or equivalent |
| MF104ZZ flanged bearing 4×10×4mm | 4 | 2 per nacelle pivot (one each end of pivot rod) |
| 4mm OD CF solid rod | 2 | Cut to length per pivot housing drawing |
| Servo pushrod (steel 2mm, Z-bend ends) | 2 | Tilt servo arm → pivot arm |
| Clevis links M2 | 4 | Pushrod-to-servo-arm + pushrod-to-pivot-arm |
| Hard stop blocks (CF-PETG) | 4 | Two per nacelle: −5° stop + 140° stop |

### Installation

1. **Press MF104ZZ bearings** into pivot housing bores (both ends). Bearings are 10mm OD, press-fit into pivot housing.

2. **Insert 4mm CF pivot rod** through the wing spar pocket and through the pivot housing bearings. The pivot rod is fixed to the fuselage; the nacelle rotates around it on the bearings.

3. **Slide nacelle pivot housing** onto pivot rod. Verify nacelle rotates freely with <0.5 mm axial play. Add thrust washer (stainless 4×8×0.5mm) if axial play exceeds 1mm.

4. **Install tilt servo** in fuselage servo mount bracket at wing root bay. Servo arm must be accessible through access panel B or D.

5. **Connect pushrod** from servo arm to pivot arm (`s_pivot_arm_a_scaled24.stl`). Adjust pushrod length so that:
   - Servo 0° = nacelle 0° (horizontal / cruise)
   - Servo ~125° = nacelle 90° (hover / vertical)
   - Servo ~170° = nacelle 120° (backing)

6. **Install hard stop blocks.** Bond −5° stop and 140° stop blocks to fuselage / pivot housing. Verify servo stalls against stop at travel limits rather than stripping — set servo travel limits in FC firmware.

7. **Servo calibration (both nacelles):**
   - Set FC output channel travel ±100% = nacelle 0°–90° for normal flight.
   - Enable software travel limits at −5° and 140°.
   - Verify both nacelles reach 90° simultaneously on throttle-up command.

### Phase 3 Checks

- [ ] Both nacelles rotate freely on bearings — no grinding, no wobble
- [ ] Hard stops engage at −5° and 140° on both nacelles
- [ ] Nacelle nozzle opens/closes correctly across 0°–90° sweep (from Phase 2 gear linkage)
- [ ] Sector gear does NOT rotate with nacelle — fixed to bracket
- [ ] Servo arm midpoint approximately corresponds to 60° nacelle (nominal hover approach)
- [ ] Both nacelles synchronise to within 2° at 0° and 90° positions

---

## Phase 4 — Rear EDF + Radial Intake + Nozzle

**Goal:** CF-PETG intake frame and PETG plenum manifold installed; 120mm EDF mounted inside engine bell (Panel F); rear nozzle frame installed, iris operational, servo wired.

> **Design change from Rev M belly scoop:** The 120mm EDF no longer mounts in the fuselage belly. The belly of `s_middle_canonical_shell24.stl` is standard Serenity geometry. Air is delivered via 4 radial scoops at station ~310mm (the hull neck) through a CF-PETG frame ring and a cross-shaped PETG plenum manifold to the EDF fan face inside the engine bell at station ~430mm.

### 4A — Intake Frame Installation

The `s_neck_intake_frame.stl` (CF-PETG) is a one-piece ring that registers into all 4 scoop windows simultaneously.

1. **Dry-fit intake frame** into the 4 scoop windows of `s_rear_neck_intake_shell24.stl` before bonding. Registration tongues (5mm) should insert snugly into each window with ~0.2mm clearance. Adjust with sandpaper if tight.

2. **Verify aerodynamic orientation:** intake lips (6mm forward projection) face forward (+X toward nose). Duct arms extend inward toward fuselage centreline.

3. **Apply structural epoxy** (West System 105/206) to:
   - Registration tongue outer surfaces (tongue → hull window edges)
   - Bonding shoulders (flange pressing on hull exterior around each window)

4. **Press frame into position.** All 4 tongues must seat fully before epoxy sets. Clamp with tape across shoulder flanges. Cure 24 h before moving.

5. **Fill any gap between shoulder flange and hull exterior** with epoxy fillet. Smooth with gloved finger. Cure 2 h.

### 4B — Plenum Manifold Installation

The `s_aft_edf_plenum.stl` (PETG) connects the 4 intake frame duct arms to the 120mm EDF fan face. It is installed inside the engine bell section before closing Panel F.

1. **Dry-fit plenum** against intake frame duct arm exits and verify:
   - Each rectangular arm (65×60mm) aligns with the corresponding intake frame duct arm exit.
   - Aft circular outlet (120mm) is centred on fuselage centreline.

2. **Bond plenum forward arm ends to intake frame duct arm exits** with structural epoxy. Fillet all joints. Cure 2 h.

3. **Pressure-test plenum before bonding EDF:**
   - Seal EDF aft face with tape.
   - Cover 3 of the 4 scoop inlets temporarily.
   - Apply shop-vac suction at the 4th scoop — you should hear/feel a clear draft at the EDF outlet (leakage only around tape, not at joints).
   - If joints leak, apply additional epoxy fillet and re-test.

### 4C — 120mm EDF Installation

The EDF mounts axially inside the engine bell (Panel F), fan face at station ~430mm from nose.

1. **Test 120mm EDF** on bench ESC before installation (correct rotation, no vibration).

2. **Install EDF mounting ring** (circular PETG ring matching EDF OD + 3mm, printed from `s_aft_edf_plenum.scad` retaining lip) at station ~430mm inside Panel F. Bond with structural epoxy. Cure 1 h.

3. **Seat EDF in plenum outlet bell:**
   - Slide EDF aft into the plenum's 120mm circular outlet (inner bell diameter = EDF OD + 2×3mm = 126mm).
   - Press EDF forward until fan face aligns with the EDF retaining lip ring (station ~430mm).
   - Bond with 4 dabs slow-cure structural epoxy around EDF casing circumference at the retaining lip.

4. **Route 120mm EDF motor leads** through Panel F to 80A ESC in Panel F bay. Route signal lead forward through MAIN-PWR conduit to Bay B (FC2 PRU Ch.2).

5. **Install 80A ESC** in Panel F bay. Bond ESC to bay floor with double-sided foam tape + cable tie.

6. **Cure 2 h minimum before applying thrust.**

### 4D — Rear Nozzle Installation

1. **Press `rear_nozzle_frame.stl`** (base ring + 8 fixed ribs) onto the 120mm EDF duct exit face at Panel F aft end. Ribs are at 22.5° offsets from petal positions — they maintain the cone silhouette at all petal states.
2. **Install 8 rear nozzle petals** on 3mm hinge pins. Piano wire link ring passes through all petal bottom lugs.
3. **Install rear nozzle servo (SG90 class)** inside Panel F section. Piano wire pushrod connects servo arm to nozzle inner ring.
4. **Calibrate:** servo 0° = petals closed (hull-matched bell profile); servo 90° = petals fully open (full burn).
5. **Install WS2812B LED ring** at rear duct exit lip.

### Phase 4 Checks

- [ ] Intake frame tongues fully seated in all 4 scoop windows — no gaps
- [ ] Intake frame shoulder flanges bonded flush against hull exterior — no lifting
- [ ] Plenum pressure-test passed — no joint leakage
- [ ] EDF seated at station ~430mm, centreline ±2mm
- [ ] EDF rotation verified before sealing (correct direction: intake = forward face)
- [ ] Motor leads and ESC installed in Panel F; signal lead routed to FC2
- [ ] 80A ESC bonded in bay
- [ ] Nozzle frame ribs maintain cone profile with petals open AND closed
- [ ] 8 petals open and close evenly without binding
- [ ] Rear nozzle servo travel: closed at 0°, fully open at ~90°
- [ ] LED ring installed

---

## Phase 5 — Hull Foam Pour + Close-up

**Goal:** Structural foam cured throughout hull interior; all void formers removed; hull rigid.

### Pre-Pour Final Checklist

- [ ] All PTFE conduits routed — pull strings accessible at both ends
- [ ] All bay standoffs installed
- [ ] Cargo hard points installed
- [ ] SMA bulkhead pass-throughs installed
- [ ] EPS void formers waxed (2 coats) and seated
- [ ] Nacelle bays and pivot housings masked OFF — do not foam
- [ ] Servo mount brackets clear of foam path

### Pour Sequence

Mix and pour per X-30 datasheet (2:1 ratio by volume, 2-min pot life, 4× expansion).
Pour from aft forward in three shots to control expansion direction:
1. Rear bay (aft of Panel E)
2. Mid bays (D + C)
3. Forward bays (B + A)

**Allow 24 h full cure before opening or removing void formers.**

After cure:
- Remove EPS void formers
- Wipe bay walls with IPA to remove wax film
- Verify foam did not intrude into access panel bays, cargo bay, or conduit runs
- Test all 8 pull strings — should still move freely

---

## Phase 6 — Minimum Viable Flyer (CN1 + FC1 + CN2 + FC2)

**Goal:** ★ **FIRST FLIGHT** with 4-node avionics and all propulsion operational.

### Node Install Order

Install **CN1 + FC1** in Bay A (nose), **CN2 + FC2** in Bay B (dorsal fwd).

**For each bay:**
1. Seat Cape-B (CN node) on floor standoffs (M2.5 × 6mm). 4 screws.
2. Seat Cape-A (FC node) on 20mm inter-cape standoffs above Cape-B. 4 screws.
3. Plug 72-pin expansion connector between PB2-I and Cape.
4. Connect CAN FD, RS-485, 1553, ETH chain connectors per bus harness.
5. Connect ESC DSHOT signal leads to Cape-A PRU-ICSS header.
6. Connect servo signal leads (2× tilt servos + 1× rear nozzle servo) to Cape-A servo rail.
7. Connect GPS patch antenna coax to Cape-A GPS header. Mount GPS patch antenna on hull dorsal surface at nearest bay location.

### ESC Assignment — Cross-Nacelle Redundancy

ESCs are split across FC1 and FC2 so that each flight controller drives **one EDF per nacelle**.
If either FC fails, the surviving FC retains 50% thrust in both nacelles — the aircraft can still
hover rather than losing one nacelle entirely.

| ESC | EDF | Nacelle | Position | Controlled by |
| --- | --- | ------- | -------- | ------------- |
| ESC1 | EDF1 (upstream / fore) | Port | Z=76..126mm | **FC1** |
| ESC2 | EDF2 (downstream / aft) | Port | Z=5..50mm | **FC2** |
| ESC3 | EDF1 (upstream / fore) | Starboard | Z=76..126mm | **FC1** |
| ESC4 | EDF2 (downstream / aft) | Starboard | Z=5..50mm | **FC2** |
| ESC5 | 120mm rear EDF | Fuselage | — | **FC2** |

> **Failure mode:** FC1 loss → FC2 holds ESC2 (port aft) + ESC4 (stbd aft) + ESC5 (rear).
> FC2 loss → FC1 holds ESC1 (port fore) + ESC3 (stbd fore). Symmetric half-thrust in both nacelles either way.

### Wiring Connections for 4-Node Minimum Build

| Signal | From | To | Via |
|--------|------|----|-----|
| ESC1 DSHOT (port EDF1) | Cape-A FC1 PRU Ch.0 | ESC1 | Conduit Bay A → port wing root |
| ESC3 DSHOT (stbd EDF1) | Cape-A FC1 PRU Ch.1 | ESC3 | Conduit Bay A → stbd wing root |
| ESC2 DSHOT (port EDF2) | Cape-A FC2 PRU Ch.0 | ESC2 | Conduit Bay B → port wing root |
| ESC4 DSHOT (stbd EDF2) | Cape-A FC2 PRU Ch.1 | ESC4 | Conduit Bay B → stbd wing root |
| ESC5 DSHOT (rear EDF) | Cape-A FC2 PRU Ch.2 | ESC5 (80A) | Conduit Bay B → Bay F aft |
| Nacelle tilt servo 1 (port) | Cape-A FC1 servo rail | Servo-tilt-port | SERVO-PWR conduit |
| Nacelle tilt servo 2 (stbd) | Cape-A FC2 servo rail | Servo-tilt-stbd | SERVO-PWR conduit |
| Rear nozzle servo | Cape-A FC2 servo rail | Servo-rear-nozzle | SERVO-PWR conduit aft |
| LED strips | Cape-B CN1 GPIO | WS2812B ×3 | LED wiring harness |
| CAN FD bus | CN1→FC1→CN2→FC2 | Ring (open at FC2 end) | CAN conduit, 120Ω term at CN1 |

### Firmware Flash

1. Flash OS image (Debian/Ubuntu for AM6254) to each PB2-I via USB-C to eMMC.
2. Flash Rev N PID governor firmware binary to M4F coprocessor on each FC node.
3. Upload via CN1 MAVLink → ETH ring → TPM-verified flash on FC1, FC2.
4. Verify `GOV_STATE = NORMAL` on all active ESCs via MAVLink.

### Pre-Flight Checklist

- [ ] All 4 EDFs spin-tested on bench with correct rotation direction
- [ ] Rear EDF bench-tested
- [ ] Both tilt servos actuate smoothly through full 0°–120° range
- [ ] Rear nozzle servo actuates closed/open
- [ ] Nacelle nozzles open at 90° tilt, closed at 0° (verify via gear linkage)
- [ ] CAN FD bus: all 4 active nodes heartbeat visible in MAVLink
- [ ] GPS lock achieved on all 4 FC nodes (CN1/CN2 may relay for minimum flight)
- [ ] FAA registration applied
- [ ] Battery C-rating confirmed for peak draw

### First Flight Protocol

**Tethered hover test first.**

1. Secure tether lines to belly hard points. 5 kg breaking strength minimum, 3m length.
2. Bring up on throttle to 25% — verify hover, check all 5 EDF sounds.
3. Increase to 60% — verify stable hover and tilt response.
4. Verify nacelle nozzle state at commanded hover angle.
5. **Only after 3 successful tethered flights:** proceed to free hover.

---

## Phase 7 — Full 8-Node Architecture

**Goal:** All 8 nodes installed, full ring redundancy, obstacle avoidance operational.

Install **CN3 + FC3** in Bay D (dorsal aft), **CN4 + FC4** in Bay E (aft service). Same procedure as Phase 6 for each bay.

Connect remaining CAN FD / RS-485 / 1553 / ETH ring segments (CN3→FC3→CN4→FC4). Terminate CAN FD bus at FC4 (120Ω).

Install 12× ToF sensor array:
- Array A sensors on FC3 (Bay D): S1A, S3A, S4A, S5A, S6A, S2A
- Array B sensors on FC1 (Bay A): S1B, S3B, S4B, S5B, S6B, S2B

Verify full obstacle avoidance in firmware (dual-redundant arrays — A and B cover identical fields, any single FC failure leaves full coverage on the other).

---

## Phase 8 — Cargo System

Install clamshell cargo door hinges and latch. Bond cargo bay walls (per s_cargo_sect_shell24.stl interior). Install N20 winch motor in aft bay, drum, and auto-latch cradle. Wire HX711 load cell to Cape-B CN2. Test release and retrieval with 250 g dummy load.

---

## Phase 9 — Finishing

1. **Decals and paint.** Airbrush or hand-paint hull sections in Serenity's distinctive brown. Panel lines with thin wash.
2. **NAV lights.** ICAO Annex 2: port = red, stbd = green, aft/top = white strobe. Wire to Cape-B CN4 GPIO.
3. **FAA registration.** Display on hull exterior per 14 CFR 47 — replace N00000 on decal sheet with your issued number.
4. **Firmware security provisioning.** Program Cape-B CPLD write-blocker (ATF16V8BQL). Provision SLB9670 TPM 2.0 endorsement keys on all 8 nodes. Keys cannot be regenerated without physical node replacement.
5. **Weight and balance.** Measure actual AUW with battery. CG should be at 40–45% of hull length from nose. Adjust battery position in cargo bay for trim if needed.
6. **Documentation.** Log all configuration in `governor_config.h`. Archive MAVLink parameter file. Photograph completed build for insurance / forensic baseline.

---

## Structural Specifications Summary

| Component | Spec | Analysis |
|-----------|------|----------|
| Wing spar | CF tube 12mm OD / 1.5mm wall | Bending stress at full nacelle torque (~0.13 Nm) ≈ 18 MPa — allowable CF ≥600 MPa |
| Keel | CF flat bar 6×3mm | Carries fuselage bending; adequate for 24-inch hull at <5g manoeuvre |
| Pivot rod | 4mm OD solid CF | Shear stress at 340g nacelle weight ≈ 27 MPa — allowable CF ≥300 MPa shear |
| Pivot bearings | MF104ZZ 4×10×4mm × 2 per nacelle | Static capacity 490 N >> 3.3 N nacelle weight — fine |
| Foam fill | 2 lb/ft³ closed-cell PU | Provides hull rigidity, crash absorption; adds ~180 g to total AUW |
| Tilt servo | ≥25 kg·cm digital metal gear | Static torque req. ~13.6 kg·cm × 2 safety factor = 27 kg·cm min; 25 kg·cm rating marginal — prefer 30+ kg·cm |
| Nacelle shell | CF-PETG 25% gyroid, 4 walls | Adequate for EDF thrust loads and nacelle-tilt reaction forces |

---

## Blender Script Reference

| Script / File | Tool | Purpose | Output |
|---------------|------|---------|--------|
| `blender_shells_v3.py` | Blender | Hollow and scale all hull STLs to 24" | `*_shell24.stl` (all hull sections) |
| `blender_nacelle_integrated_v1.py` | Blender | Generate nacelle shells with integrated stators | `s_eng_left_stator_shell24.stl`, `s_eng_right_stator_shell24.stl` |
| ~~`blender_intake_cut.py`~~ | ~~Blender~~ | ~~Cut 120mm belly intake in s_middle~~ | **Superseded** — belly scoop removed in Rev N; use canonical middle shell instead |
| `blender_nozzle_gen.py` | Blender | Generate iris nozzle petals and rings | `nacelle_nozzle_petal.stl`, `nacelle_nozzle_ring.stl`, `rear_nozzle_petal.stl`, `rear_nozzle_frame.stl` |
| `serenity/stl/s_middle_canonical_shell24.scad` | OpenSCAD | Canonical middle fuselage shell (belly restored) | `s_middle_canonical_shell24.stl` |
| `serenity/stl/s_rear_neck_intake_shell24.scad` | OpenSCAD | Rear shell with 4 radial scoop windows | `s_rear_neck_intake_shell24.stl` |
| `serenity/stl/s_neck_intake_frame.scad` | OpenSCAD | CF-PETG structural intake frame ring | `s_neck_intake_frame.stl` |
| `serenity/stl/s_aft_edf_plenum.scad` | OpenSCAD | Cross-shaped 4-to-1 plenum manifold | `s_aft_edf_plenum.stl` |

Blender scripts run headless: `blender --background --python <script>.py`  
OpenSCAD STLs: `openscad -o <output>.stl <file>.scad`

---

*Rev N — first documented 24-inch Serenity-class build — May 2026*  
*Supersedes Rev M (18-inch, 80mm EDF, AM6254 upgrade)*
