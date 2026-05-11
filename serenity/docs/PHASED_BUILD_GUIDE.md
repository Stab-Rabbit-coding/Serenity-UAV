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

# Serenity-Class Tiltrotor UAV — Phased Build Guide (Rev J)

**Author:** Steve Griffing, PE(CSE) \[Control Systems Engineering\], CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Year:** 2026  |  **Status:** Public release

> Fan engineering work inspired by the Firefly-class transport ship *Serenity*
> from *Firefly* (Fox, 2002) and *Serenity* (Universal, 2005).
> © Joss Whedon / Mutant Enemy Productions / Universal Pictures — **Not an officially licensed product.**

---

## Attribution

| Work | Author | License | Source |
|------|--------|---------|--------|
| Hull geometry | Peter Farell | CC BY 4.0 | printables.com/model/548545 |
| EDF nozzles | BamJr | CC BY 4.0 | thingiverse.com/thing:2991269 |
| Blueprint proportions | Mandel + Earls / QMx / Universal | © 2007 QMx | 269 ft × 170 ft × 79 ft ratios |
| All other design | Steve Griffing | CC BY 4.0 | This project |

---

## End State Specifications (Rev J)

| Parameter | Value |
|-----------|-------|
| Hull length | 457.2 mm (18.00″) — canonical 269 ft |
| Beam (nacelle tip-to-tip) | 288.9 mm (11.375″) — canonical 170 ft |
| Propulsion | 2× Changesun XRP 3660-2700KV 80mm 6S EDF + 1× XFLY X4 PRO 40mm 4S fuselage |
| Hover thrust | **6,450 g** (5,800 g nacelles + 650 g fuselage) |
| ESCs | 2× Hobbywing Platinum PRO V4 120A (nacelles) + 1× BLHeli32 40A (fuselage) |
| T/W empty | **2.81:1** (6S 4000mAh, 2,294 g AUW) |
| T/W with 250 g cargo | **2.66:1** (6S 2800mAh, 2,429 g AUW) |
| Max payload | **1,046 g (2.31 lb)** at T/W = 2.0 |
| Compute nodes | 4 nodes: N1 (FC/comms), N2 (nav/OA), N3 (payload/OA), N4 (actuator) |
| Node 1 hardware | CM4 Lite + CM4-CARRIER-2 + SENSORHAT-1 (XIAO RP2350 RT co-proc) + COMMS-HAT-SWITCH |
| Nodes 2 & 3 hardware | CM3+ Lite + CM3-CARRIER-1 (integrated bus I/O) |
| Node 4 hardware | CM4 Lite + CM4-CARRIER-2 + SENSORHAT-1 + MICROHAT |
| Radios | SiK 915MHz MAVLink (belly SMA) + 49MHz RCRS backup RC (dorsal fin) |
| Obstacle avoidance | 12× VL53L5CX 8×8 ToF sensors, dual redundant arrays (A on N3, B on N2) |
| Cargo | 101.6 × 76.2 × 76.2 mm bay, clamshell doors, N20 winch + auto-latch cradle |
| Security | CPLD write-blocker (N1, N4) + TPM ×4 + forensic flight-log μSD |
| Navigation lights | ICAO Annex 2 / 14 CFR 91.209 (6-position) |
| Access panels | 6 removable panels A–F (bayonet/screw/hinge/magnet) |
| Build estimate | 90–120 hours across all phases |

---

## Design Principles — Anti-Rework Rules

These rules eliminate costly structural rework. Read before you start Phase 1.

1. **Print EVERYTHING in Phase 0.** Print both nacelle pod variants (80 mm and 83 mm ID). Resin-print or source all M0.5 gears. Filament costs pennies compared to build time.
2. **Install ALL conduits, voids, and mounts before the foam pour.** The six PTFE conduit tubes, all EPS void formers, all access-panel frames, all PCB standoffs, all SMA bulkhead pass-throughs, all ToF sensor flush-mounts, and all M3 cargo hard points must be in place before any foam is poured. **Once foam cures, these cannot be added.**
3. **The foam pour is the point of no return.** Verify every provision with a test fit BEFORE mixing foam.
4. **Install the final PTFE conduit tubes sized for the final cables.** The conduit tube ID is 3 mm; use pull strings from Phase 1. Route cables phase by phase as they're needed.
5. **Budget EDFs first, XRP EDFs last.** First flight uses affordable motors. Upgrade the nacelle pods and ESCs together in Phase 7 after the airframe and avionics are proven.
6. **Nacelle pod swaps are acceptable rework.** The pod attaches externally to the pivot bracket; swapping it requires only disconnecting motor leads, not cutting foam or hull.
7. **Security provisioning is non-reversible.** Flash CPLD and burn STM32 OTP fuses in Phase 3 before first untethered flight. These cannot be undone.
8. **FAA registration on the airframe before first untethered flight.** Replace N00000 placeholder on decal sheet with your issued number.

---

## Phase Overview

| Phase | Name | Milestone | Incremental Cost | Cumulative Cost |
|-------|------|-----------|-----------------|-----------------|
| 0 | Print All Parts + Cut CF | All parts ready | ~$65 | ~$65 |
| 1 | Structure + All Future Provisions | Hull sealed, nothing left to install pre-foam | ~$80 | ~$145 |
| 2 | Nacelle Mechanics + Budget EDFs | Propulsion mechanically complete | ~$145 | ~$290 |
| 3 | Minimum Viable Flyer | ★ **FIRST FLIGHT** | ~$380 | ~$670 |
| 4 | Node 4: Actuator Redundancy | Survives N1 compute fault | ~$85 | ~$755 |
| 5 | Nodes 2 & 3: Full Architecture + OA | Autonomous flight + obstacle avoidance | ~$175 | ~$930 |
| 6 | Cargo System | 250 g delivery operational | ~$30 | ~$960 |
| 7 | Motor Upgrade: XRP + Hobbywing 120A | ★ **FULL PERFORMANCE** | ~$590 | ~$1,550 |
| 8 | Finishing: Decals + FAA + Docs | Legal, complete, documented | ~$20 | ~$1,570 |

> Cost estimates are in USD and reflect component retail pricing as of 2026.
> PCB fabrication costs assume JLCPCB assembled pricing.
> One-time tools (JTAG programmer, ST-LINK V2) are included only in Phase 3.

---

## Phase 0 — Print All Parts + Cut CF

**Goal:** Every printed part and CF cut complete before the first epoxy joint. Print the end-state geometry now — changing pod IDs or gear sizes later is expensive in time, not filament.

### What to Buy First

| Item | Qty | Notes |
|------|-----|-------|
| PETG filament | ~1,200 g | Hull sections, access panels, nozzle parts, cargo gondola, ToF mounts |
| CF-PETG filament | ~500 g | Nacelle pods, tilt brackets, spar bracket — requires hardened steel nozzle |
| TPU 95A filament | ~200 g | Landing skid feet |
| Clear resin (or source) | — | M0.5 bevel gear pair + pinion + crown — resin-print or buy precision-machined |
| CF flat bar 6×3mm | ~600 mm | Keel: 457.2 mm + 100 mm for ring frames |
| CF tube 12mm OD 1.5mm wall | ~700 mm | Spars: 2× 300 mm + 50 mm scrap; pivot rods per drawing |
| CF plate 2mm | 200×100 mm | Ring frames (5 stations) |

### Printer Setup

- Harden-steel nozzle installed (CF-PETG abrades brass nozzles)
- Calibrate E-steps and Pressure Advance per filament profile
- Bed: PEI spring steel, leveled; temp: 230°C / 70°C PETG, 240°C / 80°C CF-PETG
- Dry all filament 6 h at 65°C before printing

### Print Schedule (ordered to minimize reprints)

| STL | Material | Layer | Infill | Qty | Notes |
|-----|----------|-------|--------|-----|-------|
| `landing_skid_foot.stl` | TPU 95A | 0.25mm | 40% | 4 | Print first — tests bed adhesion |
| `cockpit_cap.stl` | PETG | 0.20mm | 8% gyroid | 1 | Print nose-down |
| `cockpit_section.stl` | PETG | 0.20mm | 8% gyroid | 1 | |
| `mid_hull_left.stl` | PETG | 0.20mm | 8% gyroid | 1 | |
| `mid_hull_right.stl` | PETG | 0.20mm | 8% gyroid | 1 | |
| `aft_neck.stl` | PETG | 0.20mm | 8% gyroid | 1 | |
| `engine_bell.stl` | PETG | 0.20mm | 20% gyroid | 1 | 3 walls |
| **`nacelle_pod_80mm.stl`** | CF-PETG | 0.15mm | 25% | 2 | **Phase 2 fit** — budget EDF housing OD |
| **`nacelle_pod_83mm.stl`** | CF-PETG | 0.15mm | 25% | 2 | **Phase 7 fit** — XRP 2700KV housing OD = 83mm |
| `nacelle_tip_cap_port.stl` | PETG | 0.20mm | 20% | 1 | RED nav light recess |
| `nacelle_tip_cap_stbd.stl` | PETG | 0.20mm | 20% | 1 | GREEN nav light recess |
| `tilt_bracket_140deg.stl` | CF-PETG | 0.15mm | 40% | 2 | 4 walls — hard stop at 140° |
| `spar_bracket.stl` | CF-PETG | 0.15mm | 40% | 1 | 4 walls |
| `nozzle_outer_housing.stl` | PETG | 0.20mm | 20% gyroid | 3 | 2 nacelle + 1 fuselage |
| `nozzle_inner_ring.stl` | CF-PETG | 0.15mm | vertical | 3 | Print vertical for tooth accuracy |
| `nozzle_flap.stl` | PETG | 0.20mm | 20% | 48 | 8 per nozzle × 3 sets = 24; print flat |
| `sector_gear_22mm.stl` | PETG | 0.12mm | 40% | 2 | 0.12mm layer for tooth accuracy |
| `access_panel_frames.stl` | PETG | 0.20mm | 100% | 1 set | 6 frames + 6 lids; 2mm wall |
| `cargo_gondola_shell.stl` | PETG | 0.20mm | 15% gyroid | 1 | 112×85×22mm belly pod |
| `clamshell_door_half.stl` | PETG | 0.20mm | 20% | 2 | Mirrored halves |
| `cargo_cradle_autolatch.stl` | PETG | 0.20mm | 30% | 1 | Auto-latch corner clips |
| `tof_flush_mount_5mm.stl` | PETG | 0.20mm | 100% | 12 | Press-fit into 6.5mm hull cutouts |

### CF Cuts

| Cut | Tool | Dimension | Notes |
|-----|------|-----------|-------|
| Keel | Dremel cut-off disc | 6×3mm flat bar → 457.2mm | Mark datums at 91, 165, 251, 320, 388mm from nose |
| Spars | Pipe cutter / Dremel | 12mm OD tube → 2× 300mm | Sand inner (spar end) to 8mm dia × 25mm tenon |
| Ring frames | Dremel / scroll saw | 2mm CF plate, 5 profiles per drawing | Fit to keel notches |
| Pivot rods | Dremel | 8mm CF rod → 2× per drawing | Clean cuts, deburr |

> ⚠ **CF dust hazard.** Wear N95 mask and safety glasses. Cut outdoors or with dust extraction. Wipe down with damp cloth after cutting.

### Phase 0 Functional Tests

- [ ] Dry-fit keel through all 6 hull sections — slides freely, no force needed
- [ ] Test nacelle_pod_80mm.stl ID: measure with calipers, verify your budget EDF housing OD fits
- [ ] Test nacelle_pod_83mm.stl ID: 83.0 mm ±0.2 mm (for XRP 2700KV Phase 7)
- [ ] Dry-fit all 6 access panel lids in their frames — flush ±0.2mm, latches engage
- [ ] Nozzle gear dry-assembly: sector gear teeth mesh with ring gear, 0.1–0.2mm backlash

**Phase 0 cost estimate:** ~$35 filament + ~$15 CF materials + ~$15 resin/gears = **~$65**

---

## Phase 1 — Structure + All Future Provisions

**Goal:** Fully sealed structural hull with every conduit, void former, standoff, SMA pass-through, sensor mount, and cargo hard point installed. This is the **point of no return** — no internal structural access after the foam cures.

### Buy List for Phase 1

| Item | Qty | Notes |
|------|-----|-------|
| West System 105/206 epoxy | 1 kit | Keel + spar bonding; structural joints |
| 5-minute epoxy 25mL syringe | 2× | Access panel frame bonding, ToF mounts |
| X-30 polyurethane foam (2-part) | ~400mL kit | 2 lb/ft³, 4× expansion, 2-min pot life |
| PTFE tube 5mm OD × 3mm ID | 3m | 6 conduits × 500mm per conduit; label both ends |
| EPS blue foam board 25mm | 300×150mm | Void formers A–E; Owens Corning Foamular 150 |
| Johnson's Paste Wax | 1 tin | 2 coats on all EPS void former surfaces |
| 3M 4016 closed-cell gasket tape | 1 roll | Seal all access panel frame lips |
| M2.5 nylon hex standoffs 6mm | 24× | 6 per node bay × 4 bays = 24; one size fits all node PCBs |
| M2.5 × 8mm SS button screws | 40× | Panel B and E (4 each) + standoff attachment |
| M3 heat-set threaded inserts | 4× | Cargo gondola belly hard points |
| N42 neodymium disc magnet 6×2mm | 8× | Panel D (4 in frame + 4 in lid) |
| SMA panel-mount bulkhead × 2 | 2× | Belly (SiK) + dorsal (RCRS); 50Ω, RG174 pigtail |
| Pull strings | 6× ~600mm | Thread through each PTFE conduit immediately |
| Toothpicks | 20× | Temporary void former pins into hull ribs |

### Installation Sequence — Follow Exactly

> **Critical:** Steps 1–10 must all be complete before mixing any foam (Step 11).

**1. Epoxy ring frames to keel** at stations 91, 165, 251, 320, 388mm. Cure 2h minimum.

**2. Bond access-panel frames (A–F) into hull sections** with 5-minute epoxy — 30min cure:

| Panel | Station (mm) | Bay | Void size | Closure |
|-------|-------------|-----|-----------|---------|
| A — Nose | 0–91 | N1 cockpit | 50×30×86mm EPS | Bayonet PETG frame |
| B — Dorsal Fwd | 91–165 | N2 | 55×52×74mm EPS | 4× M2.5 screws |
| C — Cargo Belly | 160–251 | cargo | 70×48×91mm EPS | Hinge PETG frame |
| D — Dorsal Aft | 251–320 | N3 | 55×47×69mm EPS | 4× N42 magnets |
| E — Aft Service | 320–388 | N4 | 50×42×68mm EPS | 4× M2.5 screws |
| F — Engine Bell | 388–457 | EDF access | **NO FOAM** | Bayonet PETG frame |

**3. Install M2.5 nylon standoffs in all four node bays** before hulls are joined:

| Bay | Station | Node | PCB footprint | Standoffs |
|-----|---------|------|---------------|-----------|
| A (Nose, panel A) | 0–91mm | Node 1: CM4-CARRIER-2 | 57×44mm | 4× M2.5 nylon 6mm |
| B (Dorsal Fwd, panel B) | 91–165mm | Node 2: CM3-CARRIER-1 | 68×30mm | 4× M2.5 nylon 6mm |
| D (Dorsal Aft, panel D) | 251–320mm | Node 3: CM3-CARRIER-1 | 68×30mm | 4× M2.5 nylon 6mm |
| E (Aft Service, panel E) | 320–388mm | Node 4: CM4-CARRIER-2 | 57×44mm | 4× M2.5 nylon 6mm |

**4. Install 12× ToF sensor flush-mount PETG frames** into hull cutouts (6.5mm holes):

| Sensor | Station (mm) | Position | Array | Host node |
|--------|-------------|----------|-------|-----------|
| S1A | 25 | Nose, fwd bayonet ring | A | N3 (bay D) |
| S1B | 40 | Nose ring, aft of S1A | B | N2 (bay B) |
| S3B | 150 | Port hull side | B | N2 (bay B) |
| S4B | 150 | Stbd hull side | B | N2 (bay B) |
| S3A | 200 | Port hull side | A | N3 (bay D) |
| S4A | 200 | Stbd hull side | A | N3 (bay D) |
| S6A | 160 | Forward belly blister | A | N3 (bay D) |
| S5A | 180 | Dorsal keel apex | A | N3 (bay D) |
| S6B | 220 | Belly, aft of S6A | B | N2 (bay B) |
| S5B | 260 | Dorsal keel, aft of S5A | B | N2 (bay B) |
| S2B | 425 | Engine bell rim, fwd | B | N2 (bay B) |
| S2A | 440 | Engine bell rim, aft | A | N3 (bay D) |

Bond each PETG flush-mount frame with 5-min epoxy — flush ±0.2mm. Apply 0.5mm PMMA disc over each aperture, UV-adhesive. Do not obstruct aperture.

**5. Install M3 heat-set threaded inserts ×4** in belly at cargo hard-point locations (per gondola drawing).

**6. Install SMA bulkhead pass-throughs** with dust caps:
- Belly at sta 253.7mm: SiK 915MHz antenna
- Dorsal fin at sta 365.8mm: 49MHz RCRS antenna

**7. Drill 3mm GPS coax routing hole** at cockpit roof 59mm from nose. Insert PTFE sleeve, seal with silicone.

**8. Feed 6× PTFE conduits nose-to-tail through hull:**

| Conduit | Route | Signal |
|---------|-------|--------|
| CAN-FD | Port keel rail, full length | CAN FD differential pair |
| RS-485 | Starboard keel rail, full length | RS-485 A/B |
| MIL-1553 | Dorsal centre spine, full length | 1553B twisted shielded pair (78Ω) |
| ETH-A | Port side: N1 → COMMS-HAT-SWITCH | Ethernet SPI (W5500) |
| ETH-B | Starboard side: N2 → COMMS-HAT-SWITCH | Ethernet SPI (W5500) |
| PWR | Belly centre: battery → BEC → nodes | 14AWG power + servo bundle |

Label each conduit A/B at BOTH ends with permanent marker. Immediately thread pull string through each tube and tie off at both ends.

**9. Apply 3M 4016 gasket tape** around all access panel frame lips on the hull-facing surface.

**10. Prepare EPS void formers:**
- Cut formers A–E from 25mm EPS board using craft knife + printed jig templates
- Each former must clear its panel frame by ≥5mm on all sides
- Apply 2 coats Johnson's Paste Wax to ALL EPS surfaces; buff between coats; 15min dry
- Do NOT wax PTFE conduit tubes (foam bond to tube is fine)

**11. Insert void formers A–E** through open dorsal-forward hull seam. Secure each with 2 toothpick pins into hull ribs. Test-fit all 6 access panel lids — all must close flush (≤0.2mm gap).

**12. Hull section bonding:**
- Epoxy mid-hull L/R sections to keel — cure 12h — **do NOT bond cockpit cap or engine bell yet**
- Epoxy CF-PETG spar bracket at 130mm datum; verify 90° to keel with square; cure 4h
- Press-fit spar tenons (sanded to 8mm dia × 25mm); apply Loctite 638 retaining compound; cure 4h
- Verify symmetric span measurement at nacelle tips before Loctite cures

**13. Foam pour** (X-30 PU foam, 2-part, 2-min pot life, ≤60mL per batch):
- Work nose-to-tail in 60mL batches; allow 24h cure per section before next batch
- Foam fills around void formers and PTFE conduits, bonding everything in place
- Zone F (engine bell, sta 388–457mm): **NO FOAM** — leave engine bay open
- Do not overfill — foam expands 4×

**14. After 24h cure per zone: Remove EPS void formers** via access panels. Pull upward, do not twist. EPS separates cleanly from waxed surface.

**15. Bond cockpit cap** — verify all cockpit bay wires and GPS coax are accessible first.

**16. Bond engine bell** — verify aft servo and power leads are accessible.

**17. Drill M3 pilot holes** through keel at datums 95, 165, 235, 295, 360mm.

### Phase 1 Pass Criteria (Test Before Proceeding)

- [ ] Pull string through all 6 PTFE conduits — no blockage, string exits cleanly at both ends
- [ ] All 6 access panels open and close flush (≤0.2mm gap, latches/magnets engage)
- [ ] 4× standoffs accessible in each of the 4 node bays (test with M2.5 screw)
- [ ] Push 5mm test plug through each of 12 ToF sensor flush-mounts
- [ ] CG of bare sealed hull: record for reference (target hull structure ~263g)
- [ ] SMA bulkhead connectors accessible at belly and dorsal positions

**Phase 1 cost estimate:** ~$30 epoxy + ~$25 foam + ~$12 PTFE conduits + ~$13 hardware = **~$80**

---

## Phase 2 — Nacelle Mechanics + Budget EDFs

**Goal:** All propulsion mechanics and both nacelle/fuselage EDFs installed and mechanically verified. No ESCs connected yet. Budget EDFs enable affordable first-flight testing; XRP upgrade comes in Phase 7.

### Buy List for Phase 2

| Item | Qty | Approx. Cost |
|------|-----|--------------|
| Budget 80mm EDF (verify housing OD matches nacelle_pod_80mm.stl ID) | 2× | ~$25–35ea |
| XFLY Galaxy X4 PRO 40mm 12-blade 5850KV EDF | 1× | ~$48 |
| MG90S metal gear servo (120° bracket; nacelle tilt) | 2× | ~$5ea |
| SG90 micro servo (nacelle nozzle, 2×; fuselage nozzle, 1×) | 3× | ~$3ea |
| MR63ZZ radial bearing 3×6×2.5mm | 4× | ~$8 total |
| 8mm CF rod (pivot rods) | ~150mm | ~$5 |
| Loctite 243 medium threadlock | 1× | ~$8 |
| M3 set screws | 8× | ~$3 |
| M2.5 × 6mm stainless screws | 20× | ~$4 |
| WS2812C-2020 addressable RGB LED | 2× | ~$3 total |
| Kynar wire 28AWG for nav lights | ~300mm | ~$2 |
| 5-minute epoxy (LED sealing) | — | carry from Phase 1 |

> **Budget EDF housing OD note:** Measure your chosen budget EDF with calipers before printing or purchasing nacelle pods. If housing OD differs from the STL ID, adjust the STL in your slicer or add a thin PETG adapter ring (0.5mm wall, same print run). This is the only Phase 2 variable.

### Nacelle Assembly Sequence

**1. Press 4× MR63ZZ bearings** into nacelle pivot sockets — must be flush ±0.2mm. Use a printed bearing-press jig or M5 bolt as press tool. Do not apply side load to bearing.

**2. Thread 8mm CF pivot rods** through wing spar → tilt bracket → nacelle bearing. Secure with M3 set screws and Loctite 243. Torque to finger-tight + 1/4 turn. Allow 2h cure before moving.

**3. Install MG90S tilt servos** (one per nacelle) in 140° bracket geometry:
- Connect servo horn at 18mm radius from pivot
- Travel: 0° = VTOL (nacelle up), 90° = forward flight, 115° = reverse/brake (FC soft limit)
- Hard stop at 140° via bracket — nacelle physically cannot rotate past this point
- ⚠ Do not force past 140° — bracket will crack

**4. Install budget 80mm EDFs** in nacelle_pod_80mm.stl:
- Slide EDF from intake face; align motor mount ears with M2.5 captive nut inserts
- Torque 4× M2.5 screws to 0.3 N·m
- Route 3-phase motor leads (14AWG) through 4mm channel in nacelle wall, then through hollow CF spar toward hull
- Cap leads at hull exit with electrical tape — do NOT connect to ESCs yet

**5. Install XFLY X4 PRO 40mm EDF** in engine bell (Zone F):
- 4S operation (14.8–16.8V) via 6S balance tap from cells 1–4
- Route 16AWG phase leads through PWR conduit to Bay E
- Cap leads at bay E — do NOT connect yet
- Fuselage EDF is ALWAYS the XFLY PRO — this is the final motor, no budget substitute

**6. Solder WS2812C-2020 LEDs** into nacelle tip cap recesses:
- PORT nacelle → **RED** LED
- STBD nacelle → **GREEN** LED (ICAO Annex 2 — do not swap)
- Apply 5-min epoxy bead over LED for moisture seal; cure 30min
- Route 3-wire signal lead (GND / 5V / DATA) through hollow spar; cap at hull

**7. Assemble variable-area nozzle gear trains (×3: port nacelle, stbd nacelle, fuselage):**
- Bevel block → longitudinal shaft → crown pinion → ring gear
- Install sector gear on bracket; rotate by hand to verify mesh; adjust for 0.1–0.2mm backlash
- Install 8 nozzle flaps per set
- Install SG90 nozzle servos (2 nacelle + 1 fuselage); cap servo leads at hull/bay E

**8. Install nacelle tip caps** (with WS2812C LEDs embedded) — M2.5 screws or press-fit per drawing.

### Phase 2 Pass Criteria (Test Before Proceeding)

- [ ] Manual nacelle sweep 0°→115°→0° × 10 repetitions each side — smooth, no binding, no interference
- [ ] Tilt servo command (bench 5V supply to servo): both nacelles track, symmetric response ±1°
- [ ] Nozzle sweep × 10 per assembly: open = 42mm / closed = 36mm (verify with calipers)
- [ ] Motor shafts: rotate budget EDFs by hand — free rotation, blade tips clear pod wall at all nacelle angles
- [ ] LED polarity bench test (3.3V bench supply): PORT = RED, STBD = GREEN
- [ ] Hard stop confirmed: nacelle cannot rotate past 140° aft

**Phase 2 cost estimate:** 2× budget EDF ~$60 + 1× XFLY PRO ~$48 + servos ~$21 + bearings/hardware ~$16 = **~$145**

---

## Phase 3 — Minimum Viable Flyer ★

**Goal:** Aircraft achieves safe, stable, RC-controlled hover and nacelle transition. This is the first flight milestone. Node 1 (the complete primary flight controller, comms, and security stack) is installed and operational.

> ★ **Milestone: FIRST FLIGHT achieved at end of this phase.**

### Buy List for Phase 3

| Item | Qty | Approx. Cost |
|------|-----|--------------|
| Budget BLHeli32 80A ESC (6S rated; for budget EDFs) | 2× | ~$25ea |
| BLHeli32 40A ESC (4S; for XFLY fuselage) | 1× | ~$18 |
| XT90 PDB — 4× XT30 outputs | 1× | ~$12 |
| XT90 battery pigtail 100mm | 1× | ~$5 |
| 5V 5A switching BEC (DC-DC) | 1× | ~$8 |
| 14AWG silicone wire 1m | 1× | ~$6 |
| 16AWG silicone wire 0.5m | 1× | ~$4 |
| JST-XH 6S balance tap → XT30 (cells 1–4, 4S tap) | 1× | ~$3 |
| CM4 Lite (no eMMC) | 1× | ~$35 |
| CM4-CARRIER-2 PCB (JLCPCB assembled) | 1× | ~$8 |
| SENSORHAT-1 PCB with XIAO RP2350 (JLCPCB assembled) | 1× | ~$22 |
| COMMS-HAT-SWITCH PCB with SiK 915MHz (JLCPCB assembled) | 1× | ~$35 |
| u-blox M10Q GPS module + patch antenna | 1× | ~$12 |
| SiK 915MHz ground station radio (pairs with airborne unit) | 1× | ~$15 |
| 49MHz RCRS-49 board (or temporary RC receiver for initial test) | 1× | ~$20 |
| microSD 8GB Class 10 A2 (OS boot) | 1× | ~$5 |
| microSD 32GB (flight log) | 1× | ~$8 |
| WS2812C nav light chain, diffusers, mounts | 6× | ~$8 |
| 6S 4000mAh LiPo battery | 1× | ~$60 |
| JST-GH cables: 4-pin CAN, 6-pin ETH, 3-pin servo extensions | assorted | ~$8 |
| USB-Blaster or FT2232H JTAG programmer | 1× | ~$20 (tool) |
| ST-LINK V2 SWD programmer | 1× | ~$10 (tool) |
| 3M double-sided foam tape | 1× | ~$5 |
| Zip ties 100mm + 200mm | 1× bag | ~$4 |

### Power System Installation

**1.** Mount XT90 PDB at sta 130mm on keel underside — 3M foam tape + M2.5 screw through mounting tab.

**2.** Solder 14AWG main leads: PDB to ESC-L (port, ~145mm run), ESC-R (stbd, ~155mm), ESC-Fwd (fuselage, ~290mm).

**3.** Mount 2× 80A BLHeli32 ESCs against hull interior sides in bay C — foam tape + M2.5 tabs. These will be replaced in Phase 7; mount accessibly.

**4.** Mount 1× BLHeli32 40A ESC in bay E for fuselage EDF.

**5.** Install 5V/5A BEC; output to avionics power rail. **Verify 5.00V ±0.05V under 1A bench load before connecting avionics.**

**6.** Pull 14AWG motor phase leads through PWR conduit (installed Phase 1) to ESC terminals. Solder — check rotation marking before final solder order (motor can swap any two leads to reverse direction).

**7.** Install 4S balance tap pigtail: JST-XH balance connector cells 1–4 of 6S pack → XT30 → fuselage ESC. 16AWG, 150mm.

**8.** CAN FD bus termination: Node 1 end = 120Ω bridge **SOLDERED**; no other termination yet (N2/N3/N4 not installed).

### Node 1 Installation

**9.** Mount CM4-CARRIER-2 PCB on Bay A (cockpit) nylon standoffs — M2.5 nylon screws. **Use NYLON standoffs throughout cockpit bay — metal reduces GPS and RF performance.**

**10.** Snap CM4 Lite into CM4-CARRIER-2 DF40 board-to-board connectors (bottom side).

**11.** Stack SENSORHAT-1 PCB on CM4-CARRIER-2 via 40-pin GPIO header. SENSORHAT-1 carries:
- XIAO RP2350 (real-time co-processor for flight control)
- ICM-42688-P 6-axis IMU
- BMP388 barometer
- MCP2518FD CAN FD controller
- W5500 Ethernet controller
- HI-6130 MIL-STD-1553 interface
- MAX3485E RS-485 transceiver

**12.** Stack COMMS-HAT-SWITCH PCB on SENSORHAT-1 via 40-pin header. COMMS-HAT-SWITCH carries:
- KSZ8895 5-port Ethernet switch (star topology for all nodes)
- SiK 915MHz MAVLink radio
- HI-6130 1553 RT
- CAN FD interface
- TPM

**13.** Install OS μSD (8GB, Class 10 A2) in CM4-CARRIER-2 boot slot.  
**Install log μSD (32GB) in CM4-CARRIER-2 log slot.**  
⚠ **DO NOT mix up the two cards.** OS card → boot slot; log card → log slot.

**14.** Route GPS U.FL coax through 3mm PTFE-sleeved hole at cockpit roof (59mm from nose) to GPS patch antenna. Mount patch antenna flush on cockpit roof with double-sided foam tape — antenna face UP.

**15.** Connect SiK 915MHz RG174 pigtail to belly SMA bulkhead (installed Phase 1). Attach 915MHz whip antenna outside hull.

**16.** Connect RCRS-49 coaxial lead to dorsal SMA bulkhead (installed Phase 1). Install 49MHz helical coil antenna in dorsal fin enclosure.

**17.** Install nav light WS2812C chain: PORT nacelle (RED), STBD nacelle (GREEN), tail cone (WHITE steady), belly strobe (WHITE flash). GP26 signal wire routes through PWR conduit.

### Security Provisioning (Irreversible — Do Before First Flight)

> ⚠ **OTP fuse burning is permanent.** Verify firmware is correct BEFORE burning. These steps cannot be undone.

**18.** Connect USB-Blaster/FT2232H to JTAG header on CM4-CARRIER-2. Flash CPLD write-blocker bitstream: `write_blocker.bit`. Insert JP2 jumper → **verify LED1 (green) illuminates.** LED1 indicates write-blocker active.

**19.** Connect ST-LINK V2 to SWD header on CM4-CARRIER-2. Flash STM32 NX proxy: `nx_proxy.bin` via STM32CubeProgrammer.

**20.** In STM32CubeProgrammer: burn STM32 read-protect OTP fuses. **Verify NX_LATCH = HIGH at TP_NX test point before proceeding.**

**21.** Boot CM4 (USB-C 5V power to CM4-CARRIER-2). SSH in. Run:
```bash
tpm2_getcap handles-persistent    # verify both TPMs detected
tpm2_createprimary -C o -g sha256 -G ecc -c primary.ctx
tpm2_create -C primary.ctx -g sha256 -G aes -u key.pub -r key.priv
tpm2_load -C primary.ctx -u key.pub -r key.priv -c key.ctx
tpm2_evictcontrol -C o -c key.ctx 0x81000001
```

**22.** Configure SELinux and forensic logging:
```bash
apt install policycoreutils selinux-basics
semanage fcontext -a -t log_storage_t /mnt/flightlog
mount -o noexec,nodev,nosuid,ro /dev/mmcblk1 /mnt/flightlog
```

### Software

**23.** Flash XIAO RP2350 firmware (on SENSORHAT-1) via USB BOOTSEL mode — drag `.uf2` to drive. Verify 1Hz heartbeat LED after boot.

**24.** Boot CM4 Raspberry Pi OS. SSH in:
```bash
apt install mavlink-router mavsdk pymavlink
```
Configure `mavlink-router.conf` to bridge XIAO RP2350 serial → SiK 915MHz.

**25.** Calibrate ESCs (no fans/loads connected):
- Arm sequence per BLHeli32 (full throttle power-on → drop to zero)
- Verify all 3 ESCs calibrated and armed

**26.** Calibrate nacelle tilt servos: command 0° → verify nacelle vertical ±0.5°; command 90° → verify horizontal ±0.5°. Adjust servo horn if needed.

**27.** Calibrate fuselage nozzle servo endpoints:
- 1.0ms PWM → nozzle open (42mm exit) — lock clevis
- 2.0ms PWM → nozzle closed (36mm exit) — verify

### Ground Tests — Verify Before Any Flight

**28.** Static CG: target **190mm from nose** per Rev J spec. Slide battery position on rail to achieve. Measure with wing tips level on known-flat surface.

**29.** Radio checks:
- MAVLink heartbeat visible in QGroundControl over SiK 915MHz link
- RCRS RC channels show correct direction and travel in QGC RC calibration screen
- TDDS channel assignment acknowledged

**30.** Motor spin test (5% throttle, 2 seconds): all 3 motors spin in correct directions:
- Port nacelle: CCW (tractor)
- Stbd nacelle: CW (tractor)
- Fuselage: CCW (tractor)

**31.** Tethered thrust test (tie-down hook rated ≥10kg on keel):
- 30% throttle: verify ≥870g per nacelle EDF (budget motors at 30%)
- 60% throttle, 10s: verify lift exceeds AUW → aircraft attempts to rise on tether
- ESC temps: ≤60°C after 30s at 50% throttle

**32.** Nav lights: all 6 positions cycle through ICAO states — RED port, GREEN stbd, WHITE steady tail, WHITE strobe belly.

**33.** GPS lock: HDOP ≤1.5 with both nacelle EDFs running at 30%. If HDOP degrades with motors, verify antenna placement and nylon standoffs.

### First Flight

> ⚠ **FAA requirement:** Apply registration number (replacing N00000 on decal sheet) BEFORE any untethered flight. 14 CFR Part 48 — registration mark visible without moving any part.

**Pre-flight ABCD checklist:**
- **A**irframe: all fasteners torqued, no visible damage, CG at 190mm, battery secured on rail
- **B**attery: 6S 4000mAh at ≥80% charge, connectors clean, no puffing
- **C**omms: MAVLink heartbeat in QGC, RCRS RC stick response verified, failsafe tested (link loss → Hover Hold)
- **D**ocs: FAA Part 107 remote pilot certificate current, registration number on airframe, site NOTAM checked

**Flight sequence:**
1. Tethered hover 1m AGL: 30s, land, inspect — ESC and motor temps ≤70°C
2. Free hover 1m AGL: stability check, ±10° roll/pitch/yaw authority, altitude hold ±0.3m — ≤60s
3. Free hover 3m AGL: yaw 360° both directions
4. Nacelle transition: climb to ≥8m (26ft) AGL, command gradual nacelle sweep 90°→0° → verify altitude hold ±1.5m during transition
5. Forward flight circuit: one lap of flying area at ≤10m AGL, transition back to hover, land
6. Record telemetry log. Verify flight data written to log μSD (check file size increases).

### Phase 3 Pass Criteria

- [ ] Stable hover at 1m AGL in ≤15° headwind
- [ ] Nacelle transition without altitude excursion >1.5m
- [ ] All 3 ESCs ≤70°C at full hover power
- [ ] MAVLink telemetry live to QGC during all flight segments
- [ ] Flight log written to write-protected μSD; CPLD LED1 remains green throughout

**Phase 3 cost estimate:** ESCs ~$68 + PDB/BEC/wiring ~$38 + Node 1 boards ~$100 + GPS ~$12 + radios ~$35 + μSD ~$13 + battery ~$60 + nav lights ~$8 + tools (one-time) ~$30 + misc ~$16 = **~$380**

**Cumulative cost at first flight: ~$670**

---

## Phase 4 — Node 4: Actuator Redundancy

**Goal:** Dedicated actuator-control node (Node 4) operational. Aircraft survives a Node 1 compute fault without losing servo and ESC control.

Node 4 (bay E, sta 320–388mm) is a hot-standby actuator controller. It runs a XIAO RP2350 real-time co-processor (on SENSORHAT-1) that monitors Node 1's heartbeat via CAN FD and assumes servo/motor authority within 100ms of N1 timeout. It also provides an independent IMU cross-check.

### Buy List for Phase 4

| Item | Qty | Approx. Cost |
|------|-----|--------------|
| CM4 Lite (no eMMC) | 1× | ~$35 |
| CM4-CARRIER-2 PCB (JLCPCB) | 1× | ~$8 |
| SENSORHAT-1 PCB with XIAO RP2350 (JLCPCB) | 1× | ~$22 |
| MICROHAT PCB (Ethernet passthrough + bus connectors) | 1× | ~$8 |
| microSD 8GB OS boot | 1× | ~$5 |
| microSD 32GB log | 1× | ~$8 |
| JST-GH CAN/RS-485/1553/ETH cables 150mm | assorted | ~$5 |

### Installation Sequence

**1.** Open bay E panel (aft service panel, 4× M2.5 screws). Mount CM4-CARRIER-2 on bay E nylon standoffs.

**2.** Snap CM4 Lite into DF40 connectors. Stack SENSORHAT-1 → MICROHAT via GPIO header.

**3.** Install OS μSD (boot slot) and log μSD (log slot). **Same CPLD flash and OTP provisioning as Node 1:**
- Flash CPLD write-blocker via JTAG → verify LED1 green
- Flash STM32 NX proxy via SWD → burn OTP fuses → verify NX_LATCH = HIGH
- Provision Node 4 TPM separately from Node 1 TPM (different key material)

**4.** Pull CAN FD, RS-485, MIL-1553, and ETH-B cables from conduits to bay E. Terminate at SENSORHAT-1/MICROHAT JST-GH connectors. Daisy-chain CAN FD: add 120Ω termination resistor at Node 4 end (second network endpoint).

**5.** Flash XIAO RP2350 (Node 4) with actuator-control firmware. Boot CM4 (Node 4), configure as actuator redundancy node:
- Monitors N1 CAN FD heartbeat
- Holds last-known servo/ESC commands in shadow register
- On N1 timeout >100ms: assumes servo/motor command authority, transmits CAN FD takeover frame
- On N1 recovery: graceful handoff back

**6.** Configure Node 1 firmware to acknowledge N4 presence:
- N1 transmits heartbeat frame every 20ms on CAN FD
- N1 can explicitly delegate to N4 (e.g., on N1 reboot)

### Phase 4 Pass Criteria

- [ ] Node 4 heartbeat visible on CAN FD bus alongside Node 1
- [ ] Simulate N1 shutdown (kill CM4 power): N4 assumes servo authority within 100ms, aircraft holds hover
- [ ] Full hover with N1 active: no interference or servo jitter from N4 shadow-tracking
- [ ] Cross-check IMU: N1 SENSORHAT-1 vs N4 SENSORHAT-1 readings agree within ±2°/s on all axes

**Phase 4 cost estimate:** CM4 $35 + CARRIER-2 $8 + SENSORHAT-1 $22 + MICROHAT $8 + μSD ×2 $13 = **~$86**

---

## Phase 5 — Nodes 2 & 3: Full Architecture + Obstacle Avoidance

**Goal:** Complete 4-node architecture operational. Autonomous waypoint navigation, dual-redundant obstacle avoidance (12× ToF sensors), and all network buses fully populated.

### Buy List for Phase 5

| Item | Qty | Approx. Cost |
|------|-----|--------------|
| Raspberry Pi CM3+ Lite (no eMMC) | 2× | ~$25ea |
| CM3-CARRIER-1 PCB 68×30mm (JLCPCB assembled) | 2× | ~$12ea |
| VL53L5CX 8×8 multizone ToF sensor | 12× | ~$7ea |
| TCA9548A 8-channel I2C multiplexer | 2× | ~$1.50ea |
| MCP23008 8-port I2C GPIO expander | 2× | ~$1.20ea |
| JST-SH1.0 4-wire sensor cable 300mm | 12× | ~$1ea |
| microSD 8GB OS boot | 2× | ~$5ea |
| 5mm PMMA disc 0.5mm thick (ToF aperture covers) | 12× | ~$0.50ea |
| UV adhesive (ToF aperture seal) | 1× | ~$6 |

> **CM3-CARRIER-1 integrates** on a single 68×30mm PCB: MCP2518FD (CAN FD), ATA6561 transceiver, MAX3485E (RS-485), HI-6130 (MIL-STD-1553), W5500 (Ethernet SPI), CH340C USB-UART, microSD OS boot slot, and 40-pin RPi HAT header. It replaces the 3-board stack (CM4-CARRIER-2 + SENSORHAT-1 + MICROHAT) at reduced cost and 60g less mass for the non-flight-critical navigation and payload nodes.

### Node 2 Installation (Bay B — Navigation / Waypoints / OA Array B)

**1.** Open bay B (dorsal forward panel, 4× M2.5 screws). Mount CM3-CARRIER-1 on bay B nylon standoffs.

**2.** Press CM3+ Lite into 200-pin SODIMM socket on CM3-CARRIER-1.

**3.** Install OS μSD in J_SD slot on CM3-CARRIER-1. Pull CAN FD, RS-485, MIL-1553, ETH-A cables from conduits to bay B JST-GH connectors.

**4.** Flash CM3+ with Raspberry Pi OS Lite. SSH in; install: `apt install ros-humble-base mavros pymavlink`.

**5.** Install OA Array B sensors ×6 (Node 2 hosts) at positions already prepared in Phase 1:

| Sensor | Position | Station |
|--------|----------|---------|
| S1B | Nose bayonet ring (aft of S1A) | 40mm |
| S2B | Engine bell rim (fwd of S2A) | 425mm |
| S3B | Port hull flush mount | 150mm |
| S4B | Stbd hull flush mount | 150mm |
| S5B | Dorsal keel (panel D, aft of S5A) | 260mm |
| S6B | Belly blister (aft of S6A) | 220mm |

Connect each VL53L5CX via JST-SH1.0 4-wire (GND/VCC/SDA/SCL) to TCA9548A channels 0–5 in bay B. Wire MCP23008 GP0–GP5 to XSHUT pins. Boot sequence: assert all XSHUT LOW → enable one sensor → assign I2C address 0x54–0x59 → proceed; repeat for all 6.

### Node 3 Installation (Bay D — Payload / Sensor / OA Array A)

**6.** Open bay D (dorsal aft panel, 4× N42 magnets). Mount CM3-CARRIER-1 on bay D nylon standoffs.

**7.** Install CM3+ Lite, OS μSD. Pull conduit cables to bay D JST-GH connectors.

**8.** Install OA Array A sensors ×6 (Node 3 hosts):

| Sensor | Position | Station |
|--------|----------|---------|
| S1A | Nose bayonet ring (fwd of S1B) | 25mm |
| S2A | Engine bell rim (aft of S2B) | 440mm |
| S3A | Port hull flush mount (aft of S3B) | 200mm |
| S4A | Stbd hull flush mount (aft of S4B) | 200mm |
| S5A | Dorsal keel (panel D, fwd of S5B) | 180mm |
| S6A | Forward belly blister (fwd of S6B) | 160mm |

Connect to TCA9548A + MCP23008 in bay D. Array A bus is **electrically isolated** from Array B bus — same I2C addresses on separate buses is intentional and correct.

### Full Network Integration

**9.** CAN FD bus now terminates at N1 (Node 1, SOLDERED) and N4 (Node 4, SOLDERED). N2 and N3 are mid-chain (no termination). Verify bus topology: N1 ↔ N2 ↔ N3 ↔ N4 daisy-chain with 120Ω at both ends only.

**10.** RS-485 multidrop: all 4 nodes — no termination changes needed (N1 and N4 ends already terminated).

**11.** MIL-STD-1553: N1 as Bus Controller (BC), N2/N3/N4 as Remote Terminals (RT). Verify RT address assignments conflict-free.

**12.** Ethernet star: COMMS-HAT-SWITCH KSZ8895 switch (on N1) provides ports to N2, N3, N4 via ETH-A/ETH-B conduits + direct connections.

**13.** Configure autonomous navigation on Node 2:
- GPS coordinates from Node 1 GPS (M10Q) broadcast on CAN FD
- Node 2 runs waypoint planning, obstacle avoidance fusion (Array B primary, Array A secondary)
- OA halt threshold: stop all forward motion at 1.0m obstacle clearance; resume when clear

**14.** Configure Node 3 for payload control triggers (Phase 6 will add hardware; configure IO now).

### Phase 5 Pass Criteria

- [ ] All 4-node CAN FD heartbeats confirmed on QGC system status
- [ ] All 12 ToF sensors return valid range data at ≤4m (QGC sensor page)
- [ ] Ground wall-approach test: aircraft moves toward wall at 0.5m/s, OA halts at 1.0m clearance
- [ ] 3-waypoint autonomous mission: GPS-guided flight, altitude hold, correct RTL on simulated link loss
- [ ] Single-node failure mode: kill N2 → N3 Array A provides full OA coverage; kill N3 → N2 Array B covers
- [ ] MIL-STD-1553 bus: all RT nodes respond to BC poll within 9μs

**Phase 5 cost estimate:** 2× CM3+ $50 + 2× CM3-CARRIER-1 $24 + 12× VL53L5CX $84 + 2× TCA9548A $3 + 2× MCP23008 $2.40 + cables/hardware $14 = **~$177**

---

## Phase 6 — Cargo System

**Goal:** Full cargo handling operational: 250g payload delivered via autonomous winch deploy with auto-latch cradle.

The cargo gondola hard points (M3 inserts) and panel C hinge (belly) were installed in Phase 1. This phase installs the gondola shell, clamshell doors, winch mechanism, and cradle, then integrates cargo commands with Node 3.

### Buy List for Phase 6

| Item | Qty | Approx. Cost |
|------|-----|--------------|
| N20 DC motor 6V 300:1 gear ratio (winch) | 1× | ~$8 |
| DRV8833 dual H-bridge motor driver board | 1× | ~$2 |
| SG90 servo (clamshell door actuator) | 1× | ~$3 |
| SG90 servo (payload release / winch direction) | 1× | ~$3 |
| Dyneema SK75 0.5mm braid 2m | 1× | ~$4 |
| 3mm CF rod for clamshell door hinge pin | ~60mm | ~$2 |
| Closed-cell foam gasket tape (gondola-to-hull seal) | — | carry from Phase 1 |

> All gondola printed parts (shell, door halves, cradle) were printed in Phase 0.

### Installation Sequence

**1.** Epoxy cargo gondola shell into belly void at 4× M3 hard points (installed Phase 1). Shell protrudes 18mm below hull line — matches Serenity canonical cargo module profile. Cure 24h before proceeding.

**2.** Install 3mm CF door hinge pins at gondola centreline. Attach clamshell door halves (2× mirrored). Doors must open freely (spring-loaded to open) and close to flush fit.

**3.** Install DRV8833 board and N20 winch motor + drum in gondola top. Wind 1.5m Dyneema SK75 onto spool; reserve 0.5m slack. Attach cargo cradle (cargo_cradle_autolatch.stl) to Dyneema via double-bowline knot.

**4.** Install SG90 door-actuator servo (spring-assist open, servo pull-close via bell-crank linkage). Adjust pushrod so full servo travel = full door travel; lock clevis.

**5.** Install SG90 payload-release servo to control DRV8833 IN1/IN2 and nSLEEP via PWM → resistor divider → GPIO.

**6.** Route DRV8833 control leads and servo cables through PWR conduit to bay D (Node 3) GPIO header.

**7.** Seal gondola-to-hull perimeter joint with 3M foam gasket tape (dust and moisture seal).

**8.** Configure Node 3 GPIO: door open/close command, winch deploy/retract, payload latch status (microswitched auto-latch).

### Phase 6 Pass Criteria

- [ ] Door command: doors swing fully open (spring-assist) and close (servo pull) × 10, no binding
- [ ] Winch deploy: lower cradle 1.5m to ground — straight descent, line not fouled
- [ ] Winch retract: raise empty cradle — auto-latch corner clips click and hold at top, no droop
- [ ] Load test: 250g in cradle, winch deploy + retract × 5 — latch holds, no line slip
- [ ] Hover with 250g payload: altitude-hold performance degradation ≤10% vs. empty
- [ ] T/W with 250g + 6S 2800mAh battery: verify ≥2.60:1 (target 2.66:1)
- [ ] Autonomous delivery: 3-waypoint mission, deploy payload at waypoint 2 on command, retract empty cradle, complete mission

**Phase 6 cost estimate:** N20 winch $8 + DRV8833 $2 + 2× SG90 $6 + Dyneema $4 + misc $10 = **~$30**

---

## Phase 7 — Motor Upgrade: XRP 3660-2700KV + Hobbywing 120A ESCs

**Goal:** Full-performance propulsion installed. Aircraft achieves Rev J specified T/W ratios and max payload capacity. This phase swaps the budget nacelle pods and EDFs for the final XRP motors.

> ★ **Milestone: FULL PERFORMANCE achieved at end of this phase.**

### Why Defer to Phase 7

- Budget EDFs and ESCs proved airframe and avionics over Phases 2–6 at ~$590 lower cost
- Any structural or design defects discovered in early phases are corrected before committing to premium motors
- If airframe survives to Phase 7 intact, the expensive hardware investment is validated

### Buy List for Phase 7

| Item | Qty | Approx. Cost |
|------|-----|--------------|
| Changesun XRP 3660-2700KV 80mm 6S EDF — CCW (port nacelle) | 1× | ~$170 |
| Changesun XRP 3660-2700KV 80mm 6S EDF — CW (stbd nacelle) | 1× | ~$170 |
| Hobbywing Platinum PRO V4 120A ESC | 2× | ~$125ea |
| 14AWG silicone motor phase wire 200mm × 3-phase (if not already adequate) | — | ~$6 |

> **Sourcing:** XRP 3660-2700KV available CCW and CW from Turbines-RC (EU primary) and RC-Castle (global). Order CCW for port (tractor), CW for stbd (tractor). Verify before ordering — incorrect rotation requires swapping any two phase leads, but correct rotation from the factory is cleaner.

> ⚠ **ESC mandatory:** XRP 3660-2700KV draws **84A peak** on 6S. The Hobbywing 120A provides 43% headroom. Do NOT attempt to run XRP motors on the budget 80A ESCs — the ESCs will overheat and fail. Replace both nacelle ESCs.

### Nacelle Pod Swap Sequence

**1.** Power off and disconnect battery. Remove nacelle tip caps.

**2.** Disconnect budget EDF motor leads at hull exit (unplug from ESC side or cut at nacelle if not connectorized).

**3.** Unscrew 4× M2.5 screws holding budget EDF to nacelle_pod_80mm.stl. Remove budget EDF; set aside (reuse or recycle).

**4.** Unclip nacelle_pod_80mm.stl from pivot bracket (remove set screw, slide pod off CF pivot rod).

**5.** Slide nacelle_pod_83mm.stl (printed Phase 0) onto CF pivot rod. Reattach with set screw + Loctite 243.

**6.** Mount XRP EDF in nacelle_pod_83mm.stl — XRP housing OD 83mm → slip fit into 83mm ID pod:
- Torque 4× M2.5 screws to 0.3 N·m
- Route 14AWG phase leads through channel and hollow spar (same path as budget EDF)
- Verify blade tips clear pod wall at 0°, 45°, 90°, 115° nacelle angles

**7.** Replace budget 80A ESCs with Hobbywing Platinum PRO V4 120A ESCs:
- Desolder old ESC motor leads from ESC output
- Mount Hobbywing 120A ESCs in same bay C positions (verify clearance — 120A ESCs are larger)
- Solder XRP motor phase leads to Hobbywing ESC outputs
- Calibrate Hobbywing ESCs: full throttle arm → drop to zero per Hobbywing calibration procedure
- Verify current limiting set to 120A in BLHeli Suite

**8.** Reinstall nacelle tip caps.

**9.** Update CG: XRP EDF pair is +766g vs budget EDF pair (~+440g delta vs typical budget 80mm pair). Recheck CG at 190mm from nose. Likely need to shift battery forward on rail.

### Full Performance Tests

**10.** Bench thrust test (tie-down, tethered):
- 100% throttle for 5s: verify ≥2,900g per nacelle (scale below aircraft nose)
- Total nacelle thrust: ≥5,800g
- Fuselage EDF at 100% 4S: verify ≥650g
- **Total: ≥6,450g** (spec target)

**11.** ESC temperature: Hobbywing 120A ESC junction ≤80°C at sustained full throttle 10s. Monitor with IR thermometer on ESC case.

**12.** T/W verification:
- Empty (6S 4000mAh, 2,294g AUW): measured thrust 6,450g → T/W = **2.81:1** ✓
- With 250g cargo (6S 2800mAh, 2,429g AUW): thrust 6,450g → T/W = **2.66:1** ✓

**13.** Max payload test (incremental, over multiple flights):
- 500g payload hover: stable, altitude hold within spec
- 750g payload hover: verify T/W ≥2.20:1
- 1,000g payload hover: verify T/W ≥2.05:1 (1,046g theoretical max at T/W = 2.0)

**14.** Full performance flight: forward flight at 35–49 kts, nacelle transitions, cargo delivery, return to home.

### Phase 7 Pass Criteria

- [ ] Static bench thrust: ≥6,450g total at full throttle
- [ ] ESC temps ≤80°C at full sustained thrust
- [ ] T/W ≥2.81:1 empty, ≥2.66:1 with 250g cargo
- [ ] Successfully hover-lifted ≥750g payload
- [ ] All Hobbywing ESC calibration LEDs show correct armed state

**Phase 7 cost estimate:** 2× XRP EDF ~$340 + 2× Hobbywing 120A ~$250 = **~$590**

---

## Phase 8 — Finishing: Decals, FAA Registration + Documentation

**Goal:** Aircraft legally compliant, aesthetically complete per show-accurate Serenity markings, and fully documented.

### Steps

**1.** Replace FAA placeholder N00000 in `diagrams/decal_sheet.svg` with your issued FAA registration number (assigned via FAA DroneZone / 14 CFR Part 48).

**2.** Print decal sheet on white waterslide decal paper (inkjet or laser per paper type). Seal with clear coat after printing; allow 24h dry.

**3.** Apply decals per `diagrams/build_guide_19_decal_placement.svg`:
- **A** — SERENITY hull name lettering (port, starboard, nose, engine bell)
- **B** — FAA registration blocks (required — both sides or on a visible flat surface)
- **C** — Firefly-universe markings: Alliance registry, 宁静 Chinese name, hull numbers, Companion Guild
- **D** — Legally required safety labels: sUAS data plate, LiPo warning, operating limits, operator contact
- **E** — Weathering details, show-accurate stencils

**4.** Final airworthiness inspection:
- All fasteners checked (torque per drawing)
- Propulsion: motor shafts spin free, no blade FOD, nacelles sweep full range
- Electronics: all panels close, all covers in place, antenna connectors tight
- Battery: no puffing, XT90 connector clean, balance leads secure
- CG: verify at 190mm with flight battery installed

**5.** Documentation archive:
- File build log (photos, test results) in project archive
- Store CPLD bitstream, STM32 firmware, and XIAO RP2350 firmware checksums with build record
- Record final AUW, CG position, and ESC settings

**6.** FAA compliance final check:
- Registration number visible without moving any part
- Remote pilot certificate current
- Aircraft < 55 lbs AUW (it is — ~5.4 lbs max)
- Flies only in uncontrolled airspace or with LAANC authorization

**Phase 8 cost estimate:** Decal paper + printing ~$15 + misc ~$5 = **~$20**

---

## Phase Cost Summary

| Phase | Name | Incremental | Cumulative | Notes |
|-------|------|------------|------------|-------|
| 0 | Print All Parts + Cut CF | ~$65 | ~$65 | Filament + CF materials + resin gears |
| 1 | Structure + All Future Provisions | ~$80 | ~$145 | Foam, epoxy, conduits, hardware |
| 2 | Nacelle Mechanics + Budget EDFs | ~$145 | ~$290 | Includes XFLY PRO (final fuselage EDF) |
| **3** | **Minimum Viable Flyer ★ FIRST FLIGHT** | **~$380** | **~$670** | Node 1, power, ESCs, radios, battery |
| 4 | Node 4: Actuator Redundancy | ~$86 | ~$756 | |
| 5 | Nodes 2 & 3: Full Architecture + OA | ~$177 | ~$933 | 12× ToF obstacle avoidance |
| 6 | Cargo System | ~$30 | ~$963 | Winch, gondola, auto-latch cradle |
| **7** | **Motor Upgrade: XRP + Hobbywing ★ FULL PERFORMANCE** | **~$590** | **~$1,553** | Pod swap + ESC swap |
| 8 | Finishing: Decals + FAA + Docs | ~$20 | **~$1,573** | |

> **Total build cost (end state): ~$1,573 USD**
> **First flight achieved at end of Phase 3: ~$670 invested**

### Savings vs. Buying Everything at Once

If all XRP EDFs and Hobbywing ESCs had been purchased in Phase 2/3:
- Additional Phase 2 cost: +$480 (2× XRP EDFs instead of budget EDFs)
- Additional Phase 3 cost: +$200 (2× Hobbywing 120A vs. 2× budget 80A)
- Total if buying premium up front: ~$670 + $480 + $200 = **~$1,350 to first flight**

The phased approach reaches first flight at **~$670** and defers the $590 motor upgrade until the airframe and avionics are proven, at the same total end-state cost.

---

## Reference: Conduit Cable Assignment

| Conduit | Route | Cable | Phases Using It |
|---------|-------|-------|-----------------|
| CAN-FD | Port keel rail | 4-pin JST-GH (CANH/CANL/GND/VCC) | 3 (N1), 4 (N4), 5 (N2, N3) |
| RS-485 | Stbd keel rail | 4-pin JST-GH (A/B/GND/VCC) | 3 (N1), 4 (N4), 5 (N2, N3) |
| MIL-1553 | Dorsal centre spine | 4-pin shielded JST-GH, 78Ω | 3 (N1), 4 (N4), 5 (N2, N3) |
| ETH-A | Port side | 6-pin JST-GH W5500 SPI | 3 (N1→COMMS-HAT-SWITCH) |
| ETH-B | Stbd side | 6-pin JST-GH W5500 SPI | 5 (N2→COMMS-HAT-SWITCH) |
| PWR | Belly centre | 14AWG power + 20AWG servo bundle | 3 (ESCs, BEC, nav lights) |

---

## Reference: Access Panel Quick-Reference

| Panel | Location | Station | Closure | What's Inside |
|-------|----------|---------|---------|---------------|
| A | Nose, top | 0–91mm | Bayonet | Node 1 (CM4 stack), GPS coax, cockpit bay |
| B | Dorsal fwd | 91–165mm | 4× M2.5 | Node 2 (CM3+ nav), OA Array B mux, CAN/ETH cables |
| C | Cargo belly | 160–251mm | Hinge | Cargo gondola, clamshell doors, winch motor |
| D | Dorsal aft | 251–320mm | 4× N42 magnets | Node 3 (CM3+ payload), OA Array A mux |
| E | Aft service | 320–388mm | 4× M2.5 | Node 4 (CM4 actuator), budget→Hobbywing ESCs |
| F | Engine bell | 388–457mm | Bayonet | XFLY 40mm fuselage EDF, fuselage nozzle servo |

---

## Reference: Node Architecture Summary

| Node | Bay | PCB Stack | Role | RT Co-proc | Security |
|------|-----|-----------|------|-----------|----------|
| N1 | A (nose) | CM4 Lite + CM4-CARRIER-2 + SENSORHAT-1 + COMMS-HAT-SWITCH | Primary FC, comms, logging | XIAO RP2350 | CPLD write-blocker + TPM |
| N2 | B (dorsal fwd) | CM3+ Lite + CM3-CARRIER-1 | Navigation, waypoints, OA Array B | None (CM3+ A53) | TPM via CM3-CARRIER-1 |
| N3 | D (dorsal aft) | CM3+ Lite + CM3-CARRIER-1 | Payload control, OA Array A | None (CM3+ A53) | TPM via CM3-CARRIER-1 |
| N4 | E (aft svc) | CM4 Lite + CM4-CARRIER-2 + SENSORHAT-1 + MICROHAT | Actuator redundancy | XIAO RP2350 | CPLD write-blocker + TPM |

---

*CC BY 4.0 · 2026 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP*
*Hull: Peter Farell CC BY 4.0 · Nozzles: BamJr CC BY 4.0 · Visual inspiration: Firefly/Serenity © Joss Whedon / Mutant Enemy / Universal*
