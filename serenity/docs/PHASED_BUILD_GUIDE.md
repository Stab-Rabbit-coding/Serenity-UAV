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

# Serenity-Class Tiltrotor UAV — Phased Build Guide (Rev K)

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

## End State Specifications (Rev K)

| Parameter | Value |
|-----------|-------|
| Hull length | 457.2 mm (18.00″) — canonical 269 ft |
| Beam (nacelle tip-to-tip) | 288.9 mm (11.375″) — canonical 170 ft |
| Propulsion | 2× Changesun XRP 3660-2700KV 80mm 6S EDF + 1× XFLY X4 PRO 40mm 4S fuselage |
| Hover thrust | **6,450 g** (5,800 g nacelles + 650 g fuselage) |
| ESCs | 2× Hobbywing Platinum PRO V4 120A (nacelles) + 1× BLHeli32 40A (fuselage) |
| Avionics dry mass | **404 g** (8× PocketBeagle 2 + 4× Cape-A + 4× Cape-B + 4× RCRS-49 sub-modules + GPS ×4 + radios) |
| T/W empty | **2.49:1** (6S 4000mAh, 2,587 g AUW) |
| T/W with 250 g cargo | **2.37:1** (6S 2800mAh, 2,722 g AUW) |
| Max payload | **753 g (1.66 lb)** at T/W = 2.0 |
| Compute nodes | **8 nodes:** FC1–FC4 (Cape-A, sensor/flight) + CN1–CN4 (Cape-B, comms/payload) |
| FC node hardware | PocketBeagle 2 (AM6232) + Cape-A 85×55mm — ICM-42688-P IMU, BMP388 baro, u-blox M10Q GPS, MIL-STD-1553, CAN FD, RS-485, Ethernet; **SLB9670 TPM 2.0** |
| CN node hardware | PocketBeagle 2 (AM6232) + Cape-B 90×60mm — SiK 915MHz, LoRa RFM95W 915MHz, TI WL1837MOD WiFi/BT, RCRS-49 sub-module, MIL-STD-1553, CAN FD, RS-485, Ethernet; **SLB9670 TPM 2.0**; ATF16V8BQL CPLD write-blocker (log μSD) |
| Bay assignments | Bay A: FC1+FC2 · Bay B: FC3+FC4 · Bay D: CN1+CN2 · Bay E: CN3+CN4 |
| Node role election | CAN FD heartbeat priority arbitration at boot — all 8 nodes identical hardware; master elected dynamically with automatic failover |
| Radios | SiK 915MHz MAVLink + LoRa RFM95W 915MHz backup + TI WL1837MOD WiFi/BT GCS + 49MHz RCRS-49 RC; all 4 on every CN node; software-elected master per link |
| Obstacle avoidance | 12× VL53L5CX 8×8 ToF sensors, dual redundant arrays (A on FC3/FC4, B on FC1/FC2) |
| Cargo | 101.6 × 76.2 × 76.2 mm bay, clamshell doors, N20 winch + auto-latch cradle |
| Security | ATF16V8BQL CPLD write-blocker (log μSD, all Cape-B nodes) + **SLB9670 TPM 2.0 on all 8 nodes** (Cape-A and Cape-B) + W25Q128JV NOR flash circular log buffer |
| Navigation lights | ICAO Annex 2 / 14 CFR 91.209 (6-position) |
| Access panels | 6 removable panels A–F (bayonet/screw/hinge/magnet) |
| Build estimate | 100–130 hours across all phases |

---

## Design Principles — Anti-Rework Rules

These rules eliminate costly structural rework. Read before you start Phase 1.

1. **Print EVERYTHING in Phase 0.** Print both nacelle pod variants (80 mm and 83 mm ID). Resin-print or source all M0.5 gears. Filament costs pennies compared to build time.
2. **Install ALL conduits, voids, and mounts before the foam pour.** The six PTFE conduit tubes, all EPS void formers, all access-panel frames, all PCB standoffs, all SMA bulkhead pass-throughs, all ToF sensor flush-mounts, and all M3 cargo hard points must be in place before any foam is poured. **Once foam cures, these cannot be added.**
3. **The foam pour is the point of no return.** Verify every provision with a test fit BEFORE mixing foam.
4. **Install the final PTFE conduit tubes sized for the final cables.** The conduit tube ID is 3 mm; use pull strings from Phase 1. Route cables phase by phase as they're needed.
5. **Budget EDFs first, XRP EDFs last.** First flight uses affordable motors. Upgrade the nacelle pods and ESCs together in Phase 7 after the airframe and avionics are proven.
6. **Nacelle pod swaps are acceptable rework.** The pod attaches externally to the pivot bracket; swapping it requires only disconnecting motor leads, not cutting foam or hull.
7. **Security provisioning is non-reversible.** Program the Cape-B CPLD write-blocker (ATF16V8BQL) and provision all TPM 2.0 keys on every node before first untethered flight. The CPLD latch clears only on hard power cycle; TPM endorsement keys cannot be regenerated without physical node replacement.
8. **FAA registration on the airframe before first untethered flight.** Replace N00000 placeholder on decal sheet with your issued number.

---

## Phase Overview

| Phase | Name | Milestone | Incremental Cost | Cumulative Cost |
|-------|------|-----------|-----------------|-----------------|
| 0 | Print All Parts + Cut CF | All parts ready | ~$65 | ~$65 |
| 1 | Structure + All Future Provisions | Hull sealed, nothing left to install pre-foam | ~$80 | ~$145 |
| 2 | Nacelle Mechanics + Budget EDFs | Propulsion mechanically complete | ~$145 | ~$290 |
| 3 | Minimum Viable Flyer (FC1+FC2+CN1+CN2) | ★ **FIRST FLIGHT** | ~$740 | ~$1,030 |
| 4 | Full 8-Node Architecture (FC3+FC4+CN3+CN4) | All 8 nodes, full ring redundancy | ~$540 | ~$1,570 |
| 5 | Obstacle Avoidance: 12× VL53L5CX ToF | Autonomous flight + obstacle avoidance | ~$110 | ~$1,680 |
| 6 | Cargo System | 250 g delivery operational | ~$30 | ~$1,710 |
| 7 | Motor Upgrade: XRP + Hobbywing 120A | ★ **FULL PERFORMANCE** | ~$590 | ~$2,300 |
| 8 | Finishing: Decals + FAA + Docs | Legal, complete, documented | ~$20 | ~$2,320 |

> Cost estimates are in USD and reflect component retail pricing as of 2026.
> PCB fabrication costs assume JLCPCB assembled pricing.
> One-time tools (JTAG programmer, USB-UART adapter) are included only in Phase 3.

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
| PTFE tube 5mm OD × 3mm ID | 5m | 8 conduits (4× ETH ring + CAN + RS-485 + 1553 + PWR); label both ends |
| EPS blue foam board 25mm | 400×200mm | Void formers A–E (larger bays for 2-node stacks); Owens Corning Foamular 150 |
| Johnson's Paste Wax | 1 tin | 2 coats on all EPS void former surfaces |
| 3M 4016 closed-cell gasket tape | 1 roll | Seal all access panel frame lips |
| M2.5 nylon hex standoffs 6mm | 16× | 4 per bay (floor mount, lower Cape) × 4 bays |
| M2.5 nylon hex standoffs 20mm | 16× | 4 per bay (inter-cape spacing, upper Cape) × 4 bays |
| M2.5 × 8mm SS button screws | 64× | Panel B and E (4 each) + 8× per bay × 4 bays standoff attachment |
| M3 heat-set threaded inserts | 4× | Cargo gondola belly hard points |
| N42 neodymium disc magnet 6×2mm | 8× | Panel D (4 in frame + 4 in lid) |
| SMA panel-mount bulkhead | 4× | Belly: SiK 915MHz + LoRa 915MHz · Dorsal: RCRS-49MHz · Dorsal fwd: WiFi; 50Ω, RG174 pigtail |
| Pull strings | 8× ~600mm | Thread through each PTFE conduit immediately |
| Toothpicks | 20× | Temporary void former pins into hull ribs |

### Installation Sequence — Follow Exactly

> **Critical:** Steps 1–10 must all be complete before mixing any foam (Step 11).

**1. Epoxy ring frames to keel** at stations 91, 165, 251, 320, 388mm. Cure 2h minimum.

**2. Bond access-panel frames (A–F) into hull sections** with 5-minute epoxy — 30min cure:

| Panel | Station (mm) | Bay | Void size | Closure |
|-------|-------------|-----|-----------|---------|
| A — Nose | 0–91 | FC1+FC2 cockpit | 92×58×86mm EPS | Bayonet PETG frame |
| B — Dorsal Fwd | 91–165 | FC3+FC4 | 92×58×74mm EPS | 4× M2.5 screws |
| C — Cargo Belly | 160–251 | cargo | 70×48×91mm EPS | Hinge PETG frame |
| D — Dorsal Aft | 251–320 | CN1+CN2 | 97×63×69mm EPS | 4× N42 magnets |
| E — Aft Service | 320–388 | CN3+CN4 | 97×63×68mm EPS | 4× M2.5 screws |
| F — Engine Bell | 388–457 | EDF access | **NO FOAM** | Bayonet PETG frame |

**3. Install M2.5 nylon standoffs in all four node bays** before hulls are joined. Each bay holds two stacked Cape+PB2 units; install floor standoffs and inter-cape standoffs for both levels:

| Bay | Station | Nodes | Cape footprint | Floor standoffs | Inter-cape standoffs |
|-----|---------|-------|----------------|-----------------|----------------------|
| A (Nose, panel A) | 0–91mm | FC1+FC2 (Cape-A) | 85×55mm | 4× M2.5 nylon 6mm | 4× M2.5 nylon 20mm |
| B (Dorsal Fwd, panel B) | 91–165mm | FC3+FC4 (Cape-A) | 85×55mm | 4× M2.5 nylon 6mm | 4× M2.5 nylon 20mm |
| D (Dorsal Aft, panel D) | 251–320mm | CN1+CN2 (Cape-B) | 90×60mm | 4× M2.5 nylon 6mm | 4× M2.5 nylon 20mm |
| E (Aft Service, panel E) | 320–388mm | CN3+CN4 (Cape-B) | 90×60mm | 4× M2.5 nylon 6mm | 4× M2.5 nylon 20mm |

The lower Cape mounts on 6mm standoffs at the bay floor. The upper Cape mounts on 20mm standoffs threaded into the lower Cape's upper mounting holes — creating a two-board stack ~44mm tall, well within all bay void depths.

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
- Belly port at sta 253.7mm: SiK 915MHz antenna
- Belly stbd at sta 253.7mm: LoRa RFM95W 915MHz antenna
- Dorsal fin at sta 365.8mm: 49MHz RCRS-49 antenna
- Dorsal fwd at sta 120mm: TI WL1837MOD WiFi antenna (2.4/5GHz)

**7. Drill 3mm GPS coax routing holes ×4** at cockpit roof 59mm from nose (one per FC node GPS patch antenna). Insert PTFE sleeves, seal with silicone.

**8. Feed 8× PTFE conduits nose-to-tail through hull:**

| Conduit | Route | Signal |
|---------|-------|--------|
| CAN-FD | Port keel rail, full length | CAN FD differential pair — FC1→CN4 linear bus |
| RS-485 | Starboard keel rail, full length | RS-485 A/B — FC1→CN4 multidrop |
| MIL-1553 | Dorsal centre spine, full length | 1553B twisted shielded pair (78Ω) |
| ETH-AB | Port forward section: Bay A → Bay B | Ethernet — FC2↔FC3 ring link |
| ETH-BD | Port mid-section: Bay B → Bay D (skip Bay C) | Ethernet — FC4↔CN1 ring link |
| ETH-DE | Starboard aft: Bay D → Bay E | Ethernet — CN2↔CN3 ring link |
| ETH-EA | Starboard full length: Bay E → Bay A | Ethernet — CN4↔FC1 ring-close link |
| PWR | Belly centre: battery → BEC → nodes | 14AWG power + 20AWG servo bundle |

Label each conduit at BOTH ends with permanent marker. Immediately thread pull string through each tube and tie off at both ends.

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

**Goal:** Four nodes (FC1, FC2, CN1, CN2) installed and operational. Aircraft achieves safe, stable, RC-controlled hover and nacelle transition under cooperative PB2 flight control with automatic inter-node failover.

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
| PocketBeagle 2 (AM6232) | 4× | ~$50ea |
| Cape-A PCB 85×55mm 4L (JLCPCB assembled) — FC nodes | 2× | ~$42ea |
| Cape-B PCB 90×60mm 4L (JLCPCB assembled) — CN nodes | 2× | ~$80ea |
| RCRS-49 sub-module PCB (49MHz TDDS RC transceiver) | 2× | ~$20ea |
| SiK 915MHz ground station radio | 1× | ~$15 |
| microSD 8GB Class 10 A2 (OS boot — 1 per node) | 4× | ~$5ea |
| microSD 32GB (log — 1 per CN node) | 2× | ~$8ea |
| WS2812C nav light chain, diffusers, mounts | 6× | ~$8 |
| 6S 4000mAh LiPo battery | 1× | ~$60 |
| JST-GH cables: 4-pin CAN, 4-pin RS-485, 8-pin ETH, shielded 1553 pair | assorted | ~$15 |
| USB-UART adapter (CP2102 or CH340) | 1× | ~$8 (tool) |
| 3M double-sided foam tape | 1× | ~$5 |
| Zip ties 100mm + 200mm | 1 bag | ~$4 |

### Power System Installation

**1.** Mount XT90 PDB at sta 130mm on keel underside — 3M foam tape + M2.5 screw through mounting tab.

**2.** Solder 14AWG main leads: PDB to ESC-L (port, ~145mm run), ESC-R (stbd, ~155mm), ESC-Fwd (fuselage, ~290mm).

**3.** Mount 2× 80A BLHeli32 ESCs against hull interior sides in bay C — foam tape + M2.5 tabs. These will be replaced in Phase 7; mount accessibly.

**4.** Mount 1× BLHeli32 40A ESC in bay E for fuselage EDF.

**5.** Install 5V/5A BEC; output to avionics power rail. **Verify 5.00V ±0.05V under 1A bench load before connecting avionics.**

**6.** Pull 14AWG motor phase leads through PWR conduit to ESC terminals. Solder — check rotation marking before final solder order (swap any two leads to reverse direction).

**7.** Install 4S balance tap pigtail: JST-XH balance connector cells 1–4 of 6S pack → XT30 → fuselage ESC. 16AWG, 150mm.

**8.** CAN FD bus termination: FC1 end = 120Ω bridge **SOLDERED** to Cape-A termination pad at Bay A.  CN2 becomes the temporary far-end termination for Phase 3 (120Ω installed at CN2 Cape-B). Termination will shift to CN4 in Phase 4 when the full bus is populated.

### FC1 + FC2 Installation (Bay A — Nose)

> **Use NYLON standoffs throughout Bay A — metal standoffs degrade GPS and RF performance.**

**9.** Mount FC1 Cape-A PCB on Bay A floor standoffs (4× M2.5 nylon 6mm). Insert PocketBeagle 2 into Cape-A expansion connector. Secure with 2× M2.5 nylon screws through PB2 corner holes.

**10.** Thread FC2 inter-cape standoffs (4× M2.5 nylon 20mm) into FC1 Cape-A upper mounting holes. Mount FC2 Cape-A on inter-cape standoffs. Insert second PocketBeagle 2.

**11.** Install OS μSD (8GB) in each PB2 boot slot. Label: FC1, FC2. **These are OS cards only — no log card on Cape-A.**

**12.** Route GPS U.FL coax from FC1 Cape-A and FC2 Cape-A up through their respective PTFE-sleeved holes at the cockpit roof. Mount 2× GPS patch antennas flush on cockpit roof, antenna face UP, spaced ≥30mm apart.

**13.** Pull CAN-FD conduit to Bay A. Daisy-chain: termination resistor → FC1 JST-GH CAN port → 100mm stub → FC2 JST-GH CAN port.

**14.** Pull RS-485 conduit to Bay A. Daisy-chain FC1 → FC2 JST-GH RS-485 ports.

**15.** Pull MIL-1553 conduit to Bay A. Connect shielded twisted pair to FC1 DS26LV31/DS26LV32 header; stub to FC2.

**16.** Pull ETH-AB conduit (Bay A→Bay B end) to Bay A. Terminate at FC2 Cape-A ETH port (this is the FC2↔FC3 inter-bay link — cap the Bay B end until Phase 4).

**17.** Pull ETH-EA conduit (ring-close, Bay E→Bay A end) to Bay A. Terminate at FC1 Cape-A ETH port (ring-close cable — cap the Bay E end until Phase 4).

### CN1 + CN2 Installation (Bay D — Dorsal Aft)

**18.** Mount CN1 Cape-B PCB on Bay D floor standoffs (4× M2.5 nylon 6mm). Insert PocketBeagle 2. Install CN2 Cape-B on inter-cape standoffs above CN1. Insert second PocketBeagle 2.

**19.** Install OS μSD (8GB) in each PB2 boot slot. **Install log μSD (32GB) in each Cape-B log slot.** Label clearly: CN1-OS, CN1-LOG, CN2-OS, CN2-LOG. ⚠ Do not interchange OS and log cards.

**20.** Seat RCRS-49 sub-modules onto CN1 and CN2 Cape-B sub-module headers. Connect RCRS-49 coaxial lead through dorsal fin SMA bulkhead (installed Phase 1). Install 49MHz helical coil antenna in dorsal fin enclosure.

**21.** Connect SiK 915MHz RG174 pigtail to belly port SMA bulkhead. Attach 915MHz whip antenna outside hull. Connect LoRa RFM95W pigtail to belly stbd SMA bulkhead. Connect WL1837MOD WiFi antenna to dorsal fwd SMA bulkhead.

**22.** Pull CAN-FD conduit to Bay D. Daisy-chain from Bay A cable run: CN1 JST-GH CAN in → CN1 CAN out → CN2 CAN in → CN2 CAN out + 120Ω termination (temporary Phase 3 end termination).

**23.** Pull RS-485, MIL-1553, and ETH-BD conduits to Bay D. Connect CN1 and CN2 per same daisy-chain pattern. ETH-BD connects CN1 Cape-B ETH port (FC4↔CN1 link — cap the Bay B end until Phase 4).

**24.** Install nav light WS2812C chain: PORT nacelle (RED), STBD nacelle (GREEN), tail cone (WHITE steady), belly strobe (WHITE flash). Signal wire routes through PWR conduit; connect to CN1 Cape-B GPIO header.

### Security Provisioning (Do Before First Flight)

> ⚠ **TPM key provisioning is per-node and unique.** Provision each node separately with distinct key material. Do not copy key files between nodes.

**25.** Power each node via USB-C (3.3V/5V rail from Cape BEC) and boot from OS μSD. SSH in via USB-UART adapter (CP2102 on Cape-A/B debug UART header).

**26.** On each node, provision TPM 2.0 (SLB9670 on Cape-A and Cape-B):
```bash
tpm2_getcap properties-fixed | grep TPMFamilyIndicator   # verify TPM 2.0
tpm2_createprimary -C o -g sha256 -G ecc -c primary.ctx
tpm2_create -C primary.ctx -g sha256 -G aes -u key.pub -r key.priv
tpm2_load -C primary.ctx -u key.pub -r key.priv -c key.ctx
tpm2_evictcontrol -C o -c key.ctx 0x81000001
```
Run on **all 4 nodes** (FC1, FC2, CN1, CN2) — separate SSH sessions, separate key material per node.

**27.** Verify Cape-B CPLD write-blocker on CN1 and CN2. The ATF16V8BQL latch is SET automatically at power-on by the boot sequence — no JTAG required. Verify log μSD is write-blocked:
```bash
# On CN1 and CN2:
echo test > /mnt/flightlog/test.txt   # must return "Read-only file system"
ls -l /mnt/flightlog/                 # verify existing log files are present
```

**28.** Configure forensic log mount on CN1 and CN2:
```bash
# /etc/fstab entry for log partition:
# /dev/mmcblk1p1  /mnt/flightlog  ext4  noexec,nodev,nosuid,ro  0  2
systemctl daemon-reload && mount -a
```

### Software

**29.** OS image: BeagleBoard.org Debian 12 "Bookworm" for PocketBeagle 2 (AM6232 target). Flash to OS μSD using `dd` or Balena Etcher. Boot, SSH in, update:
```bash
apt update && apt upgrade -y
apt install can-utils iproute2 python3-pip
pip3 install pymavlink mavsdk
```

**30.** Enable CAN FD interfaces on each node:
```bash
ip link set can0 type can bitrate 1000000 dbitrate 8000000 fd on
ip link set can0 up
ip link set can1 type can bitrate 1000000 dbitrate 8000000 fd on
ip link set can1 up
```

**31.** Verify CAN FD heartbeat ring: with FC1+FC2+CN1+CN2 all powered, run `candump can0` on any node — all 4 node heartbeat frames (IDs 0x001–0x004) must appear within 100ms. Role election (FC master) occurs automatically via highest-priority CAN ID.

**32.** Configure MAVLink routing on elected FC master node:
```bash
apt install mavlink-router
# Configure mavlink-router.conf: serial FC→SiK 915MHz on CN master
```

**33.** Calibrate ESCs (no loads connected):
- Arm sequence per BLHeli32 (full throttle power-on → drop to zero)
- Verify all 3 ESCs calibrated and armed

**34.** Calibrate nacelle tilt servos: command 0° → verify nacelle vertical ±0.5°; command 90° → verify horizontal ±0.5°. Adjust servo horn if needed.

**35.** Calibrate fuselage nozzle servo endpoints:
- 1.0ms PWM → nozzle open (42mm exit) — lock clevis
- 2.0ms PWM → nozzle closed (36mm exit) — verify

### Ground Tests — Verify Before Any Flight

**36.** Static CG: target **190mm from nose**. Slide battery position on rail to achieve. Measure with wing tips level on known-flat surface.

**37.** Radio checks:
- MAVLink heartbeat visible in QGroundControl over SiK 915MHz link
- LoRa backup link: verify heartbeat in QGC when SiK is disabled
- RCRS-49 RC channels show correct direction and travel in QGC RC calibration screen
- WiFi GCS: connect QGC over WL1837MOD access point, verify telemetry

**38.** Motor spin test (5% throttle, 2 seconds): all 3 motors spin in correct directions:
- Port nacelle: CCW (tractor)
- Stbd nacelle: CW (tractor)
- Fuselage: CCW (tractor)

**39.** Tethered thrust test (tie-down hook rated ≥10kg on keel):
- 30% throttle: verify ≥870g per nacelle EDF (budget motors at 30%)
- 60% throttle, 10s: verify lift exceeds AUW → aircraft attempts to rise on tether
- ESC temps: ≤60°C after 30s at 50% throttle

**40.** Node failover test: with FC master node active, kill FC master power → verify standby FC node assumes authority within 100ms (CAN FD arbitration), altitude hold maintained on tether.

**41.** Nav lights: all 6 positions cycle through ICAO states — RED port, GREEN stbd, WHITE steady tail, WHITE strobe belly.

**42.** GPS lock: HDOP ≤1.5 with both nacelle EDFs running at 30%. FC1 and FC2 each report independent GPS fix — cross-check positions agree within 2m.

### First Flight

> ⚠ **FAA requirement:** Apply registration number (replacing N00000 on decal sheet) BEFORE any untethered flight. 14 CFR Part 48 — registration mark visible without moving any part.

**Pre-flight ABCD checklist:**
- **A**irframe: all fasteners torqued, no visible damage, CG at 190mm, battery secured on rail
- **B**attery: 6S 4000mAh at ≥80% charge, connectors clean, no puffing
- **C**omms: MAVLink heartbeat in QGC, RCRS-49 RC stick response verified, failsafe tested (link loss → Hover Hold), all 4 node CAN FD heartbeats visible
- **D**ocs: FAA Part 107 remote pilot certificate current, registration number on airframe, site NOTAM checked

**Flight sequence:**
1. Tethered hover 1m AGL: 30s, land, inspect — ESC and motor temps ≤70°C
2. Free hover 1m AGL: stability check, ±10° roll/pitch/yaw authority, altitude hold ±0.3m — ≤60s
3. Free hover 3m AGL: yaw 360° both directions
4. Nacelle transition: climb to ≥8m (26ft) AGL, command gradual nacelle sweep 90°→0° → verify altitude hold ±1.5m during transition
5. Forward flight circuit: one lap of flying area at ≤10m AGL, transition back to hover, land
6. Record telemetry log. Verify flight data written to CN1 and CN2 log μSDs (file size increases on both cards).

### Phase 3 Pass Criteria

- [ ] Stable hover at 1m AGL in ≤15° headwind
- [ ] Nacelle transition without altitude excursion >1.5m
- [ ] All 3 ESCs ≤70°C at full hover power
- [ ] MAVLink telemetry live to QGC during all flight segments
- [ ] All 4 node CAN FD heartbeats confirmed in QGC system status
- [ ] Node failover: FC standby assumes authority within 100ms of master power-kill
- [ ] Flight log written to both CN node log μSDs; CPLD write-block verified (write attempt returns read-only error)
- [ ] FC1 and FC2 GPS HDOP ≤1.5, positions agree within 2m

**Phase 3 cost estimate:** ESCs ~$68 + PDB/BEC/wiring ~$38 + 4× PB2 ~$200 + 2× Cape-A ~$84 + 2× Cape-B ~$160 + 2× RCRS-49 ~$40 + SiK GS radio ~$15 + μSD ×6 ~$36 + battery ~$60 + nav lights ~$8 + tools ~$8 + misc ~$23 = **~$740**

**Cumulative cost at first flight: ~$1,030**

---

## Phase 4 — Full 8-Node Architecture

**Goal:** Install the remaining four nodes (FC3, FC4, CN3, CN4) to complete the 8-node cooperative ring. With all nodes present, CAN FD priority arbitration runs at full topology, Ethernet RSTP ring heals on any single-link failure, and MIL-STD-1553 has primary and standby Bus Controllers.

### Buy List for Phase 4

| Item | Qty | Approx. Cost |
|------|-----|--------------|
| PocketBeagle 2 (AM6232) | 4× | ~$50ea |
| Cape-A PCB 85×55mm 4L (JLCPCB assembled) — FC3+FC4 | 2× | ~$42ea |
| Cape-B PCB 90×60mm 4L (JLCPCB assembled) — CN3+CN4 | 2× | ~$80ea |
| RCRS-49 sub-module PCB | 2× | ~$20ea |
| microSD 8GB OS boot | 4× | ~$5ea |
| microSD 32GB log (CN3+CN4 only) | 2× | ~$8ea |
| JST-GH CAN/RS-485/1553/ETH cables 150mm | assorted | ~$20 |

### FC3 + FC4 Installation (Bay B — Dorsal Forward)

**1.** Open bay B panel (dorsal forward, 4× M2.5 screws). Mount FC3 Cape-A on bay B floor standoffs (4× M2.5 nylon 6mm). Insert PocketBeagle 2. Mount FC4 Cape-A on inter-cape standoffs (4× M2.5 nylon 20mm) above FC3. Insert second PocketBeagle 2.

**2.** Install OS μSD in each PB2 boot slot. Label: FC3, FC4.

**3.** Uncap the Bay B end of the ETH-AB conduit (pulled in Phase 1, capped then). Terminate at FC3 Cape-A ETH port (FC2↔FC3 ring link). Pull ETH-BD conduit Bay B end to FC4 Cape-A ETH port (FC4↔CN1 ring link — uncap the Bay D end connected in Phase 3).

**4.** Daisy-chain CAN FD from Bay A run: FC3 JST-GH CAN in → FC3 CAN out → FC4 CAN in → FC4 CAN out → continue conduit toward Bay D. Connect to existing CN1 input already in Bay D.

**5.** Connect RS-485 and MIL-1553 conduit cables to FC3 and FC4 per same daisy-chain pattern.

**6.** Provision TPM 2.0 on FC3 and FC4 via same procedure as Phase 3 Step 26. Each node receives unique key material.

### CN3 + CN4 Installation (Bay E — Aft Service)

**7.** Open bay E panel (aft service, 4× M2.5 screws). Mount CN3 Cape-B on bay E floor standoffs. Insert PocketBeagle 2. Mount CN4 Cape-B on inter-cape standoffs. Insert second PocketBeagle 2.

**8.** Install OS μSD in each PB2 boot slot. **Install log μSD (32GB) in each Cape-B log slot.** Label: CN3-OS, CN3-LOG, CN4-OS, CN4-LOG.

**9.** Seat RCRS-49 sub-modules onto CN3 and CN4 Cape-B sub-module headers.

**10.** Uncap the Bay E end of the ETH-DE conduit and the ETH-EA conduit. Terminate ETH-DE at CN3 Cape-B ETH port (CN2↔CN3 ring link). Terminate ETH-EA at CN4 Cape-B ETH port (CN4↔FC1 ring-close link).

**11.** Daisy-chain CAN FD from Bay D run into Bay E: CN3 CAN in → CN3 CAN out → CN4 CAN in → CN4 CAN out + **120Ω termination** (final bus endpoint, replaces temporary Phase 3 CN2 termination — remove the Phase 3 termination resistor from CN2).

**12.** Connect RS-485 and MIL-1553 to CN3 and CN4. Remove Phase 3 temporary MIL-1553 and RS-485 stubs.

**13.** Provision TPM 2.0 on CN3 and CN4. Verify Cape-B CPLD write-blocker on both:
```bash
echo test > /mnt/flightlog/test.txt   # must return "Read-only file system"
```

### Full Ring Integration

**14.** With all 8 nodes powered, verify Ethernet ring via RSTP: run `bridge vlan show` on any node — all 8 switch ports should appear. Disconnect one inter-bay ETH cable and verify traffic re-routes within 1s (RSTP fast-failover).

**15.** Verify full CAN FD ring: `candump can0` on any node must show heartbeat frames 0x001–0x008 within 100ms. Role election produces one FC master, one FC standby, one CN master, one CN standby.

**16.** MIL-STD-1553 final configuration: FC1 = primary Bus Controller (BC), FC2 = standby BC. FC3, FC4, CN1–CN4 = Remote Terminals (RT). Verify all 8 RT addresses conflict-free and respond to BC poll within 9μs.

**17.** RS-485 multidrop: all 8 nodes active on bus. No additional termination changes (FC1 and CN4 ends are the permanent termination points).

### Phase 4 Pass Criteria

- [ ] All 8 CAN FD heartbeats (0x001–0x008) confirmed on QGC system status
- [ ] Ethernet RSTP ring heals on single-link disconnect within 1s
- [ ] MIL-STD-1553: all 8 RT addresses respond to BC poll within 9μs
- [ ] CN3 and CN4 log μSD write-block verified
- [ ] Full hover with all 8 nodes: no interference or command jitter
- [ ] Any single node power-kill: remaining nodes maintain flight control within 100ms

**Phase 4 cost estimate:** 4× PB2 ~$200 + 2× Cape-A ~$84 + 2× Cape-B ~$160 + 2× RCRS-49 ~$40 + μSD ×6 ~$36 + cables ~$20 = **~$540**

---

## Phase 5 — Obstacle Avoidance: 12× VL53L5CX ToF

**Goal:** Dual-redundant obstacle avoidance operational. All 12 sensors installed, wired to Bay A (Array B, hosted by FC1+FC2) and Bay B (Array A, hosted by FC3+FC4), and fused into autonomous navigation.

> Requires Phase 4 complete — FC3+FC4 must be installed before Array A can be wired.

### Buy List for Phase 5

| Item | Qty | Approx. Cost |
|------|-----|--------------|
| VL53L5CX 8×8 multizone ToF sensor | 12× | ~$7ea |
| TCA9548A 8-channel I2C multiplexer | 2× | ~$1.50ea |
| MCP23008 8-port I2C GPIO expander | 2× | ~$1.20ea |
| JST-SH1.0 4-wire sensor cable 300mm | 12× | ~$1ea |
| 5mm PMMA disc 0.5mm thick (ToF aperture covers) | 12× | ~$0.50ea |
| UV adhesive (ToF aperture seal) | 1× | ~$6 |

### Array B Installation (FC1+FC2, Bay A — Nose)

**1.** Install Array B sensors ×6 at flush-mount frames prepared in Phase 1. Cable routes to Bay A:

| Sensor | Position | Station |
|--------|----------|---------|
| S1B | Nose bayonet ring (aft of S1A) | 40mm |
| S2B | Engine bell rim (fwd of S2A) | 425mm |
| S3B | Port hull flush mount | 150mm |
| S4B | Stbd hull flush mount | 150mm |
| S5B | Dorsal keel (panel D area, aft of S5A) | 260mm |
| S6B | Belly blister (aft of S6A) | 220mm |

**2.** Connect each VL53L5CX via JST-SH1.0 4-wire (GND/VCC/SDA/SCL) to TCA9548A channels 0–5 in Bay A. Wire MCP23008 GP0–GP5 to XSHUT pins. I2C bus connects to FC1 Cape-A I2C header.

Boot sequence: assert all XSHUT LOW → enable one sensor → assign I2C address 0x54–0x59 → repeat for all 6.

### Array A Installation (FC3+FC4, Bay B — Dorsal Forward)

**3.** Install Array A sensors ×6. Cable routes to Bay B:

| Sensor | Position | Station |
|--------|----------|---------|
| S1A | Nose bayonet ring (fwd of S1B) | 25mm |
| S2A | Engine bell rim (aft of S2B) | 440mm |
| S3A | Port hull flush mount (aft of S3B) | 200mm |
| S4A | Stbd hull flush mount (aft of S4B) | 200mm |
| S5A | Dorsal keel (panel B area, fwd of S5B) | 180mm |
| S6A | Forward belly blister (fwd of S6B) | 160mm |

**4.** Connect to TCA9548A + MCP23008 in Bay B, wired to FC3 Cape-A I2C header. Array A I2C bus is **electrically isolated** from Array B — same addresses on separate buses is intentional.

### Navigation Configuration

**5.** Configure OA fusion across both arrays. GPS position is broadcast on CAN FD by the elected FC master; any FC node can run waypoint planning and OA fusion.

- OA halt threshold: stop all forward motion at 1.0m obstacle clearance; resume when clear
- Array B primary; Array A cross-check (or either array independent on single-node failure)
- Configure CN master node for payload control triggers (Phase 6 adds hardware)

### Phase 5 Pass Criteria

- [ ] All 12 ToF sensors return valid range data at ≤4m (QGC sensor page)
- [ ] Ground wall-approach test: aircraft moves toward wall at 0.5m/s, OA halts at 1.0m clearance
- [ ] 3-waypoint autonomous mission: GPS-guided flight, altitude hold, correct RTL on simulated link loss
- [ ] Array failure mode: kill FC1 (Array B host) → Array A on FC3 provides full OA coverage
- [ ] Array failure mode: kill FC3 (Array A host) → Array B on FC1 provides full OA coverage

**Phase 5 cost estimate:** 12× VL53L5CX $84 + 2× TCA9548A $3 + 2× MCP23008 $2.40 + cables/PMMA/UV $18 = **~$108** (rounded to **~$110**)

---

## Phase 6 — Cargo System

**Goal:** Full cargo handling operational: 250g payload delivered via autonomous winch deploy with auto-latch cradle.

The cargo gondola hard points (M3 inserts) and panel C hinge (belly) were installed in Phase 1. This phase installs the gondola shell, clamshell doors, winch mechanism, and cradle, then integrates cargo commands with the elected CN master node (CN1 or CN2, Bay D).

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

**6.** Route DRV8833 control leads and servo cables through PWR conduit to Bay D (CN1 Cape-B GPIO header — cargo control assigned to CN master node).

**7.** Seal gondola-to-hull perimeter joint with 3M foam gasket tape (dust and moisture seal).

**8.** Configure CN master node GPIO: door open/close command, winch deploy/retract, payload latch status (microswitched auto-latch). The Cape-B DRV8833 and HX711 load-cell interfaces are used directly for winch motor and payload weight sensing.

### Phase 6 Pass Criteria

- [ ] Door command: doors swing fully open (spring-assist) and close (servo pull) × 10, no binding
- [ ] Winch deploy: lower cradle 1.5m to ground — straight descent, line not fouled
- [ ] Winch retract: raise empty cradle — auto-latch corner clips click and hold at top, no droop
- [ ] Load test: 250g in cradle, winch deploy + retract × 5 — latch holds, no line slip
- [ ] Hover with 250g payload: altitude-hold performance degradation ≤10% vs. empty
- [ ] T/W with 250g + 6S 2800mAh battery: verify ≥2.30:1 (target 2.37:1)
- [ ] Autonomous delivery: 3-waypoint mission, deploy payload at waypoint 2 on command, retract empty cradle, complete mission

**Phase 6 cost estimate:** N20 winch $8 + DRV8833 $2 + 2× SG90 $6 + Dyneema $4 + misc $10 = **~$30**

---

## Phase 7 — Motor Upgrade: XRP 3660-2700KV + Hobbywing 120A ESCs

**Goal:** Full-performance propulsion installed. Aircraft achieves Rev K specified T/W ratios and max payload capacity. This phase swaps the budget nacelle pods and EDFs for the final XRP motors.

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
- Empty (6S 4000mAh, 2,587g AUW): measured thrust 6,450g → T/W = **2.49:1** ✓
- With 250g cargo (6S 2800mAh, 2,722g AUW): thrust 6,450g → T/W = **2.37:1** ✓

**13.** Max payload test (incremental, over multiple flights):
- 500g payload hover: stable, altitude hold within spec
- 750g payload hover: verify T/W ≥2.05:1 (753g theoretical max at T/W = 2.0)

**14.** Full performance flight: forward flight at 35–49 kts, nacelle transitions, cargo delivery, return to home.

### Phase 7 Pass Criteria

- [ ] Static bench thrust: ≥6,450g total at full throttle
- [ ] ESC temps ≤80°C at full sustained thrust
- [ ] T/W ≥2.49:1 empty (2,587g AUW), ≥2.37:1 with 250g cargo (2,722g AUW)
- [ ] Successfully hover-lifted ≥750g payload (753g theoretical max at T/W = 2.0)
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
- Store Cape-B CPLD bitstream and all node TPM endorsement key fingerprints with build record
- Record final AUW, CG position, and ESC settings for each configuration (empty, cargo)

**6.** FAA compliance final check:
- Registration number visible without moving any part
- Remote pilot certificate current
- Aircraft < 55 lbs AUW (it is — ~7.1 lbs max payload-loaded, ~5.7 lbs empty)
- Flies only in uncontrolled airspace or with LAANC authorization

**Phase 8 cost estimate:** Decal paper + printing ~$15 + misc ~$5 = **~$20**

---

## Phase Cost Summary

| Phase | Name | Incremental | Cumulative | Notes |
|-------|------|------------|------------|-------|
| 0 | Print All Parts + Cut CF | ~$65 | ~$65 | Filament + CF materials + resin gears |
| 1 | Structure + All Future Provisions | ~$80 | ~$145 | Foam, epoxy, conduits, hardware |
| 2 | Nacelle Mechanics + Budget EDFs | ~$145 | ~$290 | Includes XFLY PRO (final fuselage EDF) |
| **3** | **Minimum Viable Flyer ★ FIRST FLIGHT** | **~$740** | **~$1,030** | FC1+FC2+CN1+CN2, power, ESCs, radios, battery |
| 4 | Full 8-Node Architecture | ~$540 | ~$1,570 | FC3+FC4+CN3+CN4 — full ring redundancy |
| 5 | Obstacle Avoidance: 12× ToF | ~$110 | ~$1,680 | Dual-redundant OA arrays |
| 6 | Cargo System | ~$30 | ~$1,710 | Winch, gondola, auto-latch cradle |
| **7** | **Motor Upgrade: XRP + Hobbywing ★ FULL PERFORMANCE** | **~$590** | **~$2,300** | Pod swap + ESC swap |
| 8 | Finishing: Decals + FAA + Docs | ~$20 | **~$2,320** | |

> **Total build cost (end state): ~$2,320 USD**
> **First flight achieved at end of Phase 3: ~$1,030 invested**

### Savings vs. Buying Everything at Once

If all XRP EDFs and Hobbywing ESCs had been purchased in Phase 2/3:
- Additional Phase 2 cost: +$480 (2× XRP EDFs instead of budget EDFs)
- Additional Phase 3 cost: +$200 (2× Hobbywing 120A vs. 2× budget 80A)
- Total if buying premium up front: ~$1,030 + $480 + $200 = **~$1,710 to first flight**

The phased approach reaches first flight at **~$1,030** and defers the $590 motor upgrade until the airframe and avionics are proven, at the same total end-state cost.

---

## Reference: Conduit Cable Assignment

| Conduit | Route | Cable | Phases Using It |
|---------|-------|-------|-----------------|
| CAN-FD | Port keel rail, full length | 4-pin JST-GH (CANH/CANL/GND/VCC) — 120Ω at FC1 and CN4 | 3 (FC1+FC2), 4 (full ring) |
| RS-485 | Stbd keel rail, full length | 4-pin JST-GH (A/B/GND/VCC) — 120Ω at FC1 and CN4 | 3 (FC1+FC2), 4 (full ring) |
| MIL-1553 | Dorsal centre spine, full length | 4-pin shielded JST-GH, 78Ω — FC1=BC, FC2=standby BC | 3 (FC1+FC2), 4 (full ring) |
| ETH-AB | Port forward: Bay A → Bay B | 8-pin JST-GH Cat5e — FC2↔FC3 ring link | 4 (FC3+FC4 install) |
| ETH-BD | Port mid: Bay B → Bay D | 8-pin JST-GH Cat5e — FC4↔CN1 ring link | 3 (capped), 4 (connected) |
| ETH-DE | Stbd aft: Bay D → Bay E | 8-pin JST-GH Cat5e — CN2↔CN3 ring link | 4 (CN3+CN4 install) |
| ETH-EA | Stbd full: Bay E → Bay A | 8-pin JST-GH Cat5e — CN4↔FC1 ring-close link | 3 (capped), 4 (connected) |
| PWR | Belly centre | 14AWG power + 20AWG servo bundle | 3 (ESCs, BEC, nav lights) |

---

## Reference: Access Panel Quick-Reference

| Panel | Location | Station | Closure | What's Inside |
|-------|----------|---------|---------|---------------|
| A | Nose, top | 0–91mm | Bayonet | FC1+FC2 (Cape-A stack), 2× GPS coax, ETH-AB/ETH-EA conduit ends, Array B mux |
| B | Dorsal fwd | 91–165mm | 4× M2.5 | FC3+FC4 (Cape-A stack), ETH-AB/ETH-BD conduit ends, Array A mux |
| C | Cargo belly | 160–251mm | Hinge | Cargo gondola, clamshell doors, winch motor |
| D | Dorsal aft | 251–320mm | 4× N42 magnets | CN1+CN2 (Cape-B stack), RCRS-49 ×2, ETH-BD/ETH-DE conduit ends, log μSD ×2 |
| E | Aft service | 320–388mm | 4× M2.5 | CN3+CN4 (Cape-B stack), RCRS-49 ×2, ETH-DE/ETH-EA conduit ends, budget→Hobbywing ESCs |
| F | Engine bell | 388–457mm | Bayonet | XFLY 40mm fuselage EDF, fuselage nozzle servo |

---

## Reference: Node Architecture Summary (Rev K)

| Node | Bay | Hardware | Role (elected) | Security |
|------|-----|----------|----------------|----------|
| FC1 | A (nose, lower) | PocketBeagle 2 + Cape-A 85×55mm | FC master or standby; OA Array B host | SLB9670 TPM 2.0 |
| FC2 | A (nose, upper) | PocketBeagle 2 + Cape-A 85×55mm | FC master or standby | SLB9670 TPM 2.0 |
| FC3 | B (dorsal fwd, lower) | PocketBeagle 2 + Cape-A 85×55mm | FC node; OA Array A host | SLB9670 TPM 2.0 |
| FC4 | B (dorsal fwd, upper) | PocketBeagle 2 + Cape-A 85×55mm | FC node | SLB9670 TPM 2.0 |
| CN1 | D (dorsal aft, lower) | PocketBeagle 2 + Cape-B 90×60mm | CN master or standby; cargo control | SLB9670 TPM 2.0 + ATF16V8BQL CPLD write-blocker |
| CN2 | D (dorsal aft, upper) | PocketBeagle 2 + Cape-B 90×60mm | CN master or standby | SLB9670 TPM 2.0 + ATF16V8BQL CPLD write-blocker |
| CN3 | E (aft svc, lower) | PocketBeagle 2 + Cape-B 90×60mm | CN node | SLB9670 TPM 2.0 + ATF16V8BQL CPLD write-blocker |
| CN4 | E (aft svc, upper) | PocketBeagle 2 + Cape-B 90×60mm | CN node; CAN FD bus far-end termination | SLB9670 TPM 2.0 + ATF16V8BQL CPLD write-blocker |

**All FC nodes (Cape-A):** ICM-42688-P IMU · BMP388 baro · u-blox M10Q GPS · ATA6561 CAN FD · MAX3485E RS-485 · DS26LV31/32 + PE-68515 1553 · DP83825I ×2 Ethernet · SLB9670 TPM 2.0 · 8× servo PWM rail

**All CN nodes (Cape-B):** SiK 915MHz · LoRa RFM95W 915MHz · TI WL1837MOD WiFi/BT · RCRS-49 sub-module · ATA6561 CAN FD · MAX3485E RS-485 · DS26LV31/32 + PE-68515 1553 · DP83825I ×2 Ethernet · SLB9670 TPM 2.0 · ATF16V8BQL CPLD write-blocker · W25Q128JV NOR flash log · DRV8833 winch · HX711 load cell · 2× cargo servo PWM

---

*CC BY 4.0 · 2026 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP*
*Hull: Peter Farell CC BY 4.0 · Nozzles: BamJr CC BY 4.0 · Visual inspiration: Firefly/Serenity © Joss Whedon / Mutant Enemy / Universal*
