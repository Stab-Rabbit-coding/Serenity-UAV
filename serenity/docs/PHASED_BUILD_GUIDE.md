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

# Serenity-Class Tiltrotor UAV — Phased Build Guide (Rev L)

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

## End State Specifications (Rev L)

> Rev L supersedes Rev K. Hardware identical to Rev K dual-EDF. Adds PID closed-loop governor per EDF.

| Parameter | Value |
|-----------|-------|
| Hull length | 457.2 mm (18.00″) — canonical 269 ft |
| Beam (nacelle tip-to-tip) | 288.9 mm (11.375″) — canonical 170 ft |
| Propulsion | **2× (2× Changesun XRP 3660-2700KV 80mm 6S, tandem series) per nacelle** + 1× XFLY X4 PRO 40mm 4S fuselage |
| Nacelle pod | 93.5 mm OD × **230 mm** length (tandem dual-EDF) · ID 83 mm |
| Hover thrust | **11,250 g** (10,600 g nacelles + 650 g fuselage) |
| ESCs | **4× Hobbywing Platinum PRO V4 120A** (nacelles, one per EDF) + 1× BLHeli32 40A (fuselage) |
| Governor (Rev L new) | **PID closed-loop RPM per EDF · 500 Hz M4F · BDSHOT 1 kHz feedback** |
| Avionics dry mass | **404 g** (8× PocketBeagle 2 + 4× Cape-A + 4× Cape-B + 4× RCRS-49 sub-modules + GPS ×4 + radios) |
| Airframe dry mass | **3,197 g** |
| T/W empty | **3.12:1** (6S 4000mAh, 3,607 g AUW) |
| T/W with 250 g cargo | **3.01:1** (6S 2800mAh, 3,742 g AUW) |
| T/W one EDF failed | **2.29:1** — partner EDF continues, fault latched |
| T/W one nacelle lost | **1.65:1** — FC RTH |
| Max payload | **1,406 g (3.10 lb)** at T/W = 2.0 |
| Compute nodes | **8 nodes:** FC1–FC4 (Cape-A, sensor/flight) + CN1–CN4 (Cape-B, comms/payload) |
| FC node hardware | PocketBeagle 2 (AM6232) + Cape-A 85×55mm — ICM-42688-P IMU, BMP388 baro, u-blox M10Q GPS, MIL-STD-1553, CAN FD, RS-485, Ethernet; **SLB9670 TPM 2.0** |
| CN node hardware | PocketBeagle 2 (AM6232) + Cape-B 90×60mm — SiK 915MHz, LoRa RFM95W 915MHz, TI WL1837MOD WiFi/BT, RCRS-49 sub-module, MIL-STD-1553, CAN FD, RS-485, Ethernet; **SLB9670 TPM 2.0**; ATF16V8BQL CPLD write-blocker (log μSD) |
| Bay assignments | Bay A: CN1+FC1 · Bay B: CN2+FC2 · Bay D: CN3+FC3 · Bay E: CN4+FC4 (CN lower, FC upper per bay) |
| Bus order | CN1→FC1→CN2→FC2→CN3→FC3→CN4→FC4 — CN and FC interleaved on all data buses (CAN FD, RS-485, 1553) and power distribution; any single segment or bay power failure leaves ≥2 FC + ≥2 CN on both sides of the break |
| Node role election | CAN FD heartbeat priority arbitration at boot — all 8 nodes identical hardware; master elected dynamically with automatic failover |
| Radios | SiK 915MHz MAVLink + LoRa RFM95W 915MHz backup + TI WL1837MOD WiFi/BT GCS + 49MHz RCRS-49 RC; all 4 on every CN node; software-elected master per link |
| Obstacle avoidance | 12× VL53L5CX 8×8 ToF sensors, dual redundant arrays (A on FC3 Bay D, B on FC1 Bay A) |
| Cargo | 101.6 × 76.2 × 76.2 mm bay, clamshell doors, N20 winch + auto-latch cradle |
| Security | ATF16V8BQL CPLD write-blocker (log μSD, all Cape-B nodes) + **SLB9670 TPM 2.0 on all 8 nodes** (Cape-A and Cape-B) + W25Q128JV NOR flash circular log buffer |
| Navigation lights | ICAO Annex 2 / 14 CFR 91.209 (6-position) |
| Access panels | 6 removable panels A–F (bayonet/screw/hinge/magnet) |
| Build estimate | 100–130 hours across all phases |

---

## Design Principles — Anti-Rework Rules

These rules eliminate costly structural rework. Read before you start Phase 1.

1. **Print EVERYTHING in Phase 0.** Print both nacelle pod variants (80 mm and 83 mm ID). Resin-print or source all M0.5 gears. Filament costs pennies compared to build time.
2. **Install ALL conduits, voids, and mounts before the foam pour.** All 8 PTFE conduit tubes, all EPS void formers, all access-panel frames, all PCB standoffs, all SMA bulkhead pass-throughs, all ToF sensor flush-mounts, and all M3 cargo hard points must be in place before any foam is poured. **Once foam cures, these cannot be added.**
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
| 0 | Print All Parts + Cut CF | All parts ready (incl. dual-EDF pods) | ~$65 | ~$65 |
| 1 | Structure + All Future Provisions | Hull sealed, nothing left to install pre-foam | ~$80 | ~$145 |
| 2 | Nacelle Mechanics + **2× Budget EDFs/nacelle** | Dual-EDF propulsion mechanically complete | ~$215 | ~$360 |
| 3 | Minimum Viable Flyer (CN1+FC1+CN2+FC2) | ★ **FIRST FLIGHT** | ~$740 | ~$1,100 |
| 4 | Full 8-Node Architecture (CN3+FC3+CN4+FC4) | All 8 nodes, full ring redundancy | ~$540 | ~$1,640 |
| 5 | Obstacle Avoidance: 12× VL53L5CX ToF | Autonomous flight + obstacle avoidance | ~$110 | ~$1,750 |
| 6 | Cargo System | 250 g delivery operational | ~$30 | ~$1,780 |
| 7 | **Motor Upgrade: 4× XRP + 4× Hobbywing 120A + PID Governor** | ★ **FULL PERFORMANCE — Rev L** | ~$800 | ~$2,580 |
| 8 | Finishing: Decals + FAA + Docs | Legal, complete, documented | ~$20 | ~$2,600 |

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
| **`nacelle_pod_80mm.stl`** | CF-PETG | 0.15mm | 25% | 2 | **Phase 2 fit** — budget single-EDF housing (short, ~144mm) |
| **`nacelle_pod_dual_80mm.stl`** | CF-PETG | 0.15mm | 25% | 2 | **Phase 7 fit** — 230mm tandem dual-EDF pod, 83mm ID, 6-vane flow-straightener rib at 110mm |
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
| A — Nose | 0–91 | CN1+FC1 (CN lower, FC upper) | 97×63×86mm EPS | Bayonet PETG frame |
| B — Dorsal Fwd | 91–165 | CN2+FC2 (CN lower, FC upper) | 97×63×74mm EPS | 4× M2.5 screws |
| C — Cargo Belly | 160–251 | cargo | 70×48×91mm EPS | Hinge PETG frame |
| D — Dorsal Aft | 251–320 | CN3+FC3 (CN lower, FC upper) | 97×63×69mm EPS | 4× N42 magnets |
| E — Aft Service | 320–388 | CN4+FC4 (CN lower, FC upper) | 97×63×68mm EPS | 4× M2.5 screws |
| F — Engine Bell | 388–457 | EDF access | **NO FOAM** | Bayonet PETG frame |

All 4 node bays use a uniform 97×63mm footprint — sized for Cape-B (90×60mm) + 7mm clearance. This simplifies void former fabrication: bays A–E (except cargo C) share the same footprint jig template.

**3. Install M2.5 nylon standoffs in all four node bays** before hulls are joined. Each bay holds one CN node (Cape-B, lower) and one FC node (Cape-A, upper). Install floor standoffs at the Cape-B (90×60mm) hole pattern; install inter-cape standoffs at the Cape-A (85×55mm) hole pattern above:

| Bay | Station | Nodes (lower→upper) | Lower footprint | Floor standoffs | Inter-cape standoffs |
|-----|---------|---------------------|-----------------|-----------------|----------------------|
| A (Nose, panel A) | 0–91mm | CN1 Cape-B → FC1 Cape-A | 90×60mm | 4× M2.5 nylon 6mm | 4× M2.5 nylon 20mm |
| B (Dorsal Fwd, panel B) | 91–165mm | CN2 Cape-B → FC2 Cape-A | 90×60mm | 4× M2.5 nylon 6mm | 4× M2.5 nylon 20mm |
| D (Dorsal Aft, panel D) | 251–320mm | CN3 Cape-B → FC3 Cape-A | 90×60mm | 4× M2.5 nylon 6mm | 4× M2.5 nylon 20mm |
| E (Aft Service, panel E) | 320–388mm | CN4 Cape-B → FC4 Cape-A | 90×60mm | 4× M2.5 nylon 6mm | 4× M2.5 nylon 20mm |

Cape-B (CN) mounts on 6mm floor standoffs. Cape-A (FC) mounts on 20mm inter-cape standoffs threaded into the Cape-B upper holes — ~44mm total stack height. Because Cape-A (85×55mm) is smaller than Cape-B (90×60mm), the inter-cape standoffs use inboard hole positions; verify clearance on the PCB design before ordering standoffs.

**Bus interleave benefit:** Each bay contains one CN and one FC node, sharing the same power tap and data bus segment. A power short, connector failure, or flooded bay takes out exactly one of each type — never all of either.

**4. Install 12× ToF sensor flush-mount PETG frames** into hull cutouts (6.5mm holes):

| Sensor | Station (mm) | Position | Array | Host node |
|--------|-------------|----------|-------|-----------|
| S1A | 25 | Nose, fwd bayonet ring | A | FC3 (Bay D upper) |
| S1B | 40 | Nose ring, aft of S1A | B | FC1 (Bay A upper) |
| S3B | 150 | Port hull side | B | FC1 (Bay A upper) |
| S4B | 150 | Stbd hull side | B | FC1 (Bay A upper) |
| S3A | 200 | Port hull side | A | FC3 (Bay D upper) |
| S4A | 200 | Stbd hull side | A | FC3 (Bay D upper) |
| S6A | 160 | Forward belly blister | A | FC3 (Bay D upper) |
| S5A | 180 | Dorsal keel apex | A | FC3 (Bay D upper) |
| S6B | 220 | Belly, aft of S6A | B | FC1 (Bay A upper) |
| S5B | 260 | Dorsal keel, aft of S5A | B | FC1 (Bay A upper) |
| S2B | 425 | Engine bell rim, fwd | B | FC1 (Bay A upper) |
| S2A | 440 | Engine bell rim, aft | A | FC3 (Bay D upper) |

Bond each PETG flush-mount frame with 5-min epoxy — flush ±0.2mm. Apply 0.5mm PMMA disc over each aperture, UV-adhesive. Do not obstruct aperture.

**5. Install M3 heat-set threaded inserts ×4** in belly at cargo hard-point locations (per gondola drawing).

**6. Install SMA bulkhead pass-throughs** with dust caps:
- Belly port at sta 253.7mm: SiK 915MHz antenna
- Belly stbd at sta 253.7mm: LoRa RFM95W 915MHz antenna
- Dorsal fin at sta 365.8mm: 49MHz RCRS-49 antenna
- Dorsal fwd at sta 120mm: TI WL1837MOD WiFi antenna (2.4/5GHz)

**7. Drill 3mm GPS coax routing holes** — one per FC node, at the nearest dorsal hull surface to each bay:

| FC node | Bay | Hull position | Station |
|---------|-----|---------------|---------|
| FC1 | A (nose) | Cockpit roof | ~59mm |
| FC2 | B (dorsal fwd) | Dorsal hull | ~130mm |
| FC3 | D (dorsal aft) | Dorsal hull | ~275mm |
| FC4 | E (aft service) | Dorsal hull | ~350mm |

Insert PTFE sleeves in all 4 holes, seal each with silicone. Mount GPS patch antennas flush on the hull exterior, antenna face UP.

**8. Feed 8× PTFE conduits nose-to-tail through hull:**

| Conduit | Route | Signal |
|---------|-------|--------|
| CAN-FD | Port keel rail, full length | CAN FD — CN1→FC1→CN2→FC2→CN3→FC3→CN4→FC4; 120Ω at CN1 and FC4 |
| RS-485 | Starboard keel rail, full length | RS-485 — CN1→FC1→CN2→FC2→CN3→FC3→CN4→FC4 multidrop; 120Ω at CN1 and FC4 |
| MIL-1553 | Dorsal centre spine, full length | 1553B twisted shielded pair (78Ω) — FC1=BC, FC2=standby BC |
| ETH-AB | Port forward section: Bay A → Bay B | Ethernet — FC1↔CN2 ring link |
| ETH-BD | Port mid-section: Bay B → Bay D (skip Bay C) | Ethernet — FC2↔CN3 ring link |
| ETH-DE | Starboard aft: Bay D → Bay E | Ethernet — FC3↔CN4 ring link |
| ETH-EA | Starboard full length: Bay E → Bay A | Ethernet — FC4↔CN1 ring-close link |
| PWR | Belly centre: battery → BEC → bay taps | 14AWG power + 20AWG servo bundle; one power tap per bay — each tap feeds one CN + one FC |

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

- [ ] Pull string through all 8 PTFE conduits — no blockage, string exits cleanly at both ends
- [ ] All 6 access panels open and close flush (≤0.2mm gap, latches/magnets engage)
- [ ] 4× standoffs accessible in each of the 4 node bays (test with M2.5 screw)
- [ ] Push 5mm test plug through each of 12 ToF sensor flush-mounts
- [ ] CG of bare sealed hull: record for reference (target hull structure ~263g)
- [ ] SMA bulkhead connectors accessible at belly and dorsal positions

**Phase 1 cost estimate:** ~$30 epoxy + ~$25 foam + ~$12 PTFE conduits + ~$13 hardware = **~$80**

---

## Phase 2 — Nacelle Mechanics + Budget EDFs (2× per nacelle, tandem series)

**Goal:** All propulsion mechanics and both nacelle/fuselage EDFs installed and mechanically verified. No ESCs connected yet. **Rev L uses 2× budget EDFs in tandem series per nacelle from the start** — the tandem pod geometry is the final geometry. XRP EDF upgrade comes in Phase 7 with the same pod.

> Budget EDFs in tandem series deliver ~2,500–3,100g per nacelle depending on model — adequate for Phases 2–6 airframe and avionics validation. The PID governor is not commissioned until Phase 7 (requires BDSHOT-capable ESCs). Budget ESCs in Phases 2–6 do not need BDSHOT; open-loop throttle is sufficient.

### Buy List for Phase 2

| Item | Qty | Approx. Cost |
|------|-----|--------------|
| Budget 80mm 6S EDF (×4 — 2 per nacelle, tandem series) | **4×** | ~$30–55ea |
| XFLY Galaxy X4 PRO 40mm 12-blade 5850KV EDF | 1× | ~$48 |
| Budget 50–60A BLHeli32 ESC (×4 nacelle + 1 fuselage) | **5×** | ~$18–30ea |
| MG90S metal gear servo (nacelle tilt) | 2× | ~$5ea |
| SG90 micro servo (nacelle nozzle 2×; fuselage nozzle 1×) | 3× | ~$3ea |
| MR63ZZ radial bearing 3×6×2.5mm | 4× | ~$8 total |
| 8mm CF rod (pivot rods) | ~150mm | ~$5 |
| Loctite 243 medium threadlock | 1× | ~$8 |
| M3 set screws | 8× | ~$3 |
| M2.5 × 6mm stainless screws | 20× | ~$4 |
| WS2812C-2020 addressable RGB LED | 2× | ~$3 total |
| Kynar wire 28AWG for nav lights | ~300mm | ~$2 |
| 5-minute epoxy (LED sealing) | — | carry from Phase 1 |

> **Budget EDF housing OD note:** All 4 budget EDFs must fit in the **`nacelle_pod_dual_80mm.stl`** 230mm tandem pod. Measure OD with calipers. Typical generic 80mm 6S EDF housing OD = 80–82mm. The dual pod has 83mm ID — add a thin (0.5–1mm) PETG liner ring if needed. This is the only Phase 2 variable.
>
> **ESC note for Phases 2–6:** 50–60A BLHeli32 ESCs are adequate for budget EDFs (≤50A peak). You will replace these with 4× Hobbywing 120A in Phase 7. Do not spend on premium ESCs until Phase 7 — budget ESCs are a deliberate temporary choice.

### Nacelle Assembly Sequence

**1. Press 4× MR63ZZ bearings** into nacelle pivot sockets — must be flush ±0.2mm. Use a printed bearing-press jig or M5 bolt as press tool. Do not apply side load to bearing.

**2. Thread 8mm CF pivot rods** through wing spar → tilt bracket → nacelle bearing. Secure with M3 set screws and Loctite 243. Torque to finger-tight + 1/4 turn. Allow 2h cure before moving.

**3. Install MG90S tilt servos** (one per nacelle) in 140° bracket geometry:
- Connect servo horn at 18mm radius from pivot
- Travel: 0° = VTOL (nacelle up), 90° = forward flight, 115° = reverse/brake (FC soft limit)
- Hard stop at 140° via bracket — nacelle physically cannot rotate past this point
- ⚠ Do not force past 140° — bracket will crack

**4. Install 2× budget 80mm EDFs** in `nacelle_pod_dual_80mm.stl` (one nacelle at a time):
- **FWD EDF:** Slide from intake face into FWD position (55mm from inlet). Align motor mount ears with M2.5 captive inserts. Torque 4× M2.5 screws to 0.3 N·m.
- **Flow-straightener rib** at 110mm from inlet: verify the rib is oriented correctly (vanes tangential-opposing). This is molded into the pod.
- **AFT EDF:** Slide into AFT position (155mm from inlet). Same mounting. AFT motor leads route through separate slot (avoid FWD lead routing space).
- Route all 3-phase motor leads (14AWG each EDF) through the 4mm channels and hollow CF spar toward hull.
- Label leads FWD and AFT with heat-shrink before routing.
- Cap all leads at hull exit with electrical tape — do NOT connect to ESCs yet

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
- [ ] Motor shafts: rotate **all 4** budget EDFs by hand — free rotation, blade tips clear pod wall at all nacelle angles
- [ ] FWD and AFT leads correctly labeled, accessible at hull exit
- [ ] LED polarity bench test (3.3V bench supply): PORT = RED, STBD = GREEN
- [ ] Hard stop confirmed: nacelle cannot rotate past 140° aft

**Phase 2 cost estimate:** 4× budget EDF ~$120–160 + 5× budget ESC ~$90–150 + 1× XFLY PRO ~$48 + servos ~$21 + bearings/hardware ~$16 = **~$215–295** (use lower-cost options from serenity-edf-options.jsx budget tier)

---

## Phase 3 — Minimum Viable Flyer ★

**Goal:** Four nodes (CN1, FC1, CN2, FC2) installed and operational — one CN+FC pair in Bay A, one in Bay B. Aircraft achieves safe, stable, RC-controlled hover and nacelle transition under cooperative PB2 flight control with automatic inter-node failover. Even at minimum build, any bus segment failure leaves one FC and one CN reachable on both sides of the break.

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

**8.** CAN FD bus termination: CN1 end = 120Ω bridge **SOLDERED** to Cape-B termination pad at Bay A (CN1 is the bus start — first node on the chain). FC2 gets a temporary far-end termination resistor (120Ω at FC2 Cape-A, Bay B) for Phase 3. Termination will shift permanently to FC4 (Bay E, final node) in Phase 4 — remove the Phase 3 FC2 resistor at that time.

### CN1 + FC1 Installation (Bay A — Nose)

> **Use NYLON standoffs throughout Bay A — metal standoffs degrade GPS and RF performance.**

**9.** Mount CN1 Cape-B PCB on Bay A floor standoffs (4× M2.5 nylon 6mm, Cape-B hole pattern). Insert PocketBeagle 2 into CN1 Cape-B expansion connector. Secure with M2.5 nylon screws.

**10.** Thread FC1 inter-cape standoffs (4× M2.5 nylon 20mm, Cape-A hole pattern) into CN1 Cape-B upper mounting holes. Mount FC1 Cape-A on inter-cape standoffs. Insert second PocketBeagle 2.

**11.** Install OS μSD (8GB) in each PB2 boot slot. **Install log μSD (32GB) in CN1 Cape-B log slot.** Label: CN1-OS, CN1-LOG, FC1-OS. ⚠ Do not interchange OS and log cards.

**12.** Seat RCRS-49 sub-module onto CN1 Cape-B sub-module header. Connect RCRS-49 coaxial lead through dorsal fin SMA bulkhead. Install 49MHz helical coil antenna in dorsal fin enclosure.

**13.** Connect CN1 radio antenna pigtails:
- SiK 915MHz → belly port SMA bulkhead (sta 253.7mm)
- LoRa RFM95W → belly stbd SMA bulkhead (sta 253.7mm)
- WL1837MOD WiFi → dorsal fwd SMA bulkhead (sta 120mm)
- RCRS-49 → dorsal fin SMA (sta 365.8mm, connected above)

**14.** Route FC1 GPS U.FL coax through the PTFE-sleeved cockpit-roof hole (sta ~59mm). Mount GPS patch antenna flush on cockpit roof, antenna face UP.

**15.** Pull CAN-FD conduit to Bay A. Daisy-chain: **120Ω soldered termination** → CN1 CAN in → CN1 CAN out → FC1 CAN in → FC1 CAN out → exit Bay A toward Bay B via CAN conduit.

**16.** Pull RS-485 conduit to Bay A. Daisy-chain CN1 → FC1 JST-GH RS-485 ports; cable exits toward Bay B.

**17.** Pull MIL-1553 conduit to Bay A. Connect to CN1 and FC1 DS26LV31/DS26LV32 headers. FC1 is configured as MIL-STD-1553 Bus Controller (BC); CN1 as RT address 0x01.

**18.** Pull ETH-EA conduit (Bay E→Bay A ring-close end) to Bay A. Terminate at CN1 Cape-B ETH-2 port (ring-close link FC4↔CN1 — cap the Bay E end until Phase 4).

**19.** Install nav light WS2812C chain: PORT nacelle (RED), STBD nacelle (GREEN), tail cone (WHITE steady), belly strobe (WHITE flash). Signal wire routes through PWR conduit; connect to CN1 Cape-B GPIO header.

### CN2 + FC2 Installation (Bay B — Dorsal Forward)

**20.** Open Bay B panel (4× M2.5 screws). Mount CN2 Cape-B on Bay B floor standoffs (4× M2.5 nylon 6mm). Insert PocketBeagle 2. Mount FC2 Cape-A on inter-cape standoffs (4× M2.5 nylon 20mm). Insert second PocketBeagle 2.

**21.** Install OS μSD in each PB2 boot slot. **Install log μSD (32GB) in CN2 Cape-B log slot.** Label: CN2-OS, CN2-LOG, FC2-OS.

**22.** Seat RCRS-49 sub-module onto CN2 Cape-B header.

**23.** Route FC2 GPS U.FL coax through the PTFE-sleeved dorsal hole at sta ~130mm. Mount GPS patch antenna on dorsal hull exterior, antenna face UP.

**24.** Continue CAN-FD daisy-chain from Bay A into Bay B: CN2 CAN in → CN2 CAN out → FC2 CAN in → FC2 CAN out + **temporary 120Ω termination** (Phase 3 far-end — remove in Phase 4 when full bus is populated).

**25.** Continue RS-485 daisy-chain from Bay A into Bay B: CN2 → FC2 ports.

**26.** Continue MIL-1553 daisy-chain from Bay A to Bay B: CN2 and FC2 as RT nodes. FC2 is configured as standby Bus Controller.

**27.** Pull ETH-AB conduit (Bay A→Bay B): terminate Bay A end at FC1 Cape-A ETH-1 port. Terminate Bay B end at CN2 Cape-B ETH-2 port. This completes the FC1↔CN2 Ethernet ring link.

**28.** Pull ETH-BD conduit (Bay B→Bay D): terminate Bay B end at FC2 Cape-A ETH-1 port. Cap the Bay D end — will connect to CN3 in Phase 4.

**29.** Power tap: connect CN2 and FC2 power leads from PWR conduit Bay B branch. Verify 5V ±0.05V at each node power header.

### Security Provisioning (Do Before First Flight)

> ⚠ **TPM key provisioning is per-node and unique.** Provision each node separately with distinct key material. Do not copy key files between nodes.

**30.** Power each node via USB-C (3.3V/5V rail from Cape BEC) and boot from OS μSD. SSH in via USB-UART adapter (CP2102 on Cape-A/B debug UART header).

**31.** On each node, provision TPM 2.0 (SLB9670 on Cape-A and Cape-B):
```bash
tpm2_getcap properties-fixed | grep TPMFamilyIndicator   # verify TPM 2.0
tpm2_createprimary -C o -g sha256 -G ecc -c primary.ctx
tpm2_create -C primary.ctx -g sha256 -G aes -u key.pub -r key.priv
tpm2_load -C primary.ctx -u key.pub -r key.priv -c key.ctx
tpm2_evictcontrol -C o -c key.ctx 0x81000001
```
Run on **all 4 nodes** (CN1, FC1, CN2, FC2) — separate SSH sessions, separate key material per node.

**32.** Verify Cape-B CPLD write-blocker on CN1 and CN2. The ATF16V8BQL latch is SET automatically at power-on by the boot sequence — no JTAG required. Verify log μSD is write-blocked:
```bash
# On CN1 and CN2:
echo test > /mnt/flightlog/test.txt   # must return "Read-only file system"
ls -l /mnt/flightlog/                 # verify existing log files are present
```

**33.** Configure forensic log mount on CN1 and CN2:
```bash
# /etc/fstab entry for log partition:
# /dev/mmcblk1p1  /mnt/flightlog  ext4  noexec,nodev,nosuid,ro  0  2
systemctl daemon-reload && mount -a
```

### Software

**34.** OS image: BeagleBoard.org Debian 12 "Bookworm" for PocketBeagle 2 (AM6232 target). Flash to OS μSD using `dd` or Balena Etcher. Boot, SSH in, update:
```bash
apt update && apt upgrade -y
apt install can-utils iproute2 python3-pip
pip3 install pymavlink mavsdk
```

**35.** Enable CAN FD interfaces on each node:
```bash
ip link set can0 type can bitrate 1000000 dbitrate 8000000 fd on
ip link set can0 up
ip link set can1 type can bitrate 1000000 dbitrate 8000000 fd on
ip link set can1 up
```

**36.** Verify CAN FD heartbeat ring: with CN1+FC1+CN2+FC2 all powered, run `candump can0` on any node — all 4 node heartbeat frames (IDs 0x001–0x004) must appear within 100ms. Role election (FC master) occurs automatically via highest-priority CAN ID.

**37.** Configure MAVLink routing on elected FC master node:
```bash
apt install mavlink-router
# Configure mavlink-router.conf: serial FC→SiK 915MHz on CN master
```

**38.** Calibrate ESCs (no loads connected):
- Arm sequence per BLHeli32 (full throttle power-on → drop to zero)
- Verify all 3 ESCs calibrated and armed

**39.** Calibrate nacelle tilt servos: command 0° → verify nacelle vertical ±0.5°; command 90° → verify horizontal ±0.5°. Adjust servo horn if needed.

**40.** Calibrate fuselage nozzle servo endpoints:
- 1.0ms PWM → nozzle open (42mm exit) — lock clevis
- 2.0ms PWM → nozzle closed (36mm exit) — verify

### Ground Tests — Verify Before Any Flight

**41.** Static CG: target **190mm from nose**. Slide battery position on rail to achieve. Measure with wing tips level on known-flat surface.

**42.** Radio checks:
- MAVLink heartbeat visible in QGroundControl over SiK 915MHz link
- LoRa backup link: verify heartbeat in QGC when SiK is disabled
- RCRS-49 RC channels show correct direction and travel in QGC RC calibration screen
- WiFi GCS: connect QGC over WL1837MOD access point, verify telemetry

**43.** Motor spin test (5% throttle, 2 seconds): all 3 motors spin in correct directions:
- Port nacelle: CCW (tractor)
- Stbd nacelle: CW (tractor)
- Fuselage: CCW (tractor)

**44.** Tethered thrust test (tie-down hook rated ≥10kg on keel):
- 30% throttle: verify ≥870g per nacelle EDF (budget motors at 30%)
- 60% throttle, 10s: verify lift exceeds AUW → aircraft attempts to rise on tether
- ESC temps: ≤60°C after 30s at 50% throttle

**45.** Node failover test: with FC master node active, kill FC master power → verify standby FC node assumes authority within 100ms (CAN FD arbitration), altitude hold maintained on tether.

**46.** Nav lights: all 6 positions cycle through ICAO states — RED port, GREEN stbd, WHITE steady tail, WHITE strobe belly.

**47.** GPS lock: HDOP ≤1.5 with both nacelle EDFs running at 30%. FC1 and FC2 each report independent GPS fix — cross-check positions agree within 2m.

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

### CN3 + FC3 Installation (Bay D — Dorsal Aft)

> **Use NYLON standoffs throughout Bay D — metal standoffs degrade GPS performance.**

**1.** Open Bay D panel (dorsal aft, 4× N42 magnets). Mount CN3 Cape-B on Bay D floor standoffs (4× M2.5 nylon 6mm, Cape-B hole pattern). Insert PocketBeagle 2. Mount FC3 Cape-A on inter-cape standoffs (4× M2.5 nylon 20mm) above CN3. Insert second PocketBeagle 2.

**2.** Install OS μSD in each PB2 boot slot. **Install log μSD (32GB) in CN3 Cape-B log slot.** Label: CN3-OS, CN3-LOG, FC3-OS.

**3.** Seat RCRS-49 sub-module onto CN3 Cape-B sub-module header.

**4.** Route FC3 GPS U.FL coax through the PTFE-sleeved dorsal hole at sta ~275mm. Mount GPS patch antenna on dorsal hull exterior, antenna face UP.

**5.** Remove the temporary Phase 3 FC2 120Ω CAN termination resistor from FC2 Cape-A in Bay B. Continue CAN-FD daisy-chain from Bay B (FC2 CAN out) into Bay D: CN3 CAN in → CN3 CAN out → FC3 CAN in → FC3 CAN out → cable exits Bay D toward Bay E via CAN conduit.

**6.** Continue RS-485 daisy-chain from Bay B into Bay D: CN3 → FC3 ports. Cable exits toward Bay E.

**7.** Continue MIL-1553 from Bay B into Bay D: CN3 and FC3 as Remote Terminal nodes.

**8.** Pull ETH-BD conduit (Bay B→Bay D) — uncap the Bay D end. Terminate at CN3 Cape-B ETH-2 port (FC2↔CN3 Ethernet ring link).

**9.** Power tap: connect CN3 and FC3 power leads from PWR conduit Bay D branch. Verify 5V ±0.05V at each node power header.

### CN4 + FC4 Installation (Bay E — Aft Service)

**10.** Open Bay E panel (aft service, 4× M2.5 screws). Mount CN4 Cape-B on Bay E floor standoffs (4× M2.5 nylon 6mm, Cape-B hole pattern). Insert PocketBeagle 2. Mount FC4 Cape-A on inter-cape standoffs (4× M2.5 nylon 20mm) above CN4. Insert second PocketBeagle 2.

**11.** Install OS μSD in each PB2 boot slot. **Install log μSD (32GB) in CN4 Cape-B log slot.** Label: CN4-OS, CN4-LOG, FC4-OS.

**12.** Seat RCRS-49 sub-module onto CN4 Cape-B sub-module header.

**13.** Route FC4 GPS U.FL coax through the PTFE-sleeved dorsal hole at sta ~350mm. Mount GPS patch antenna on dorsal hull exterior, antenna face UP.

**14.** Terminate CAN FD bus end: CN4 CAN in → CN4 CAN out → FC4 CAN in → FC4 CAN out + **120Ω PERMANENT termination** soldered to FC4 Cape-A termination pad (FC4 is the far-end terminus of the CN1→FC1→CN2→FC2→CN3→FC3→CN4→FC4 chain).

**15.** Continue RS-485 daisy-chain from Bay D into Bay E: CN4 → FC4 ports. Bus termination is already at CN1 (start, Bay A) and FC4 (end, Bay E) — no additional resistors needed.

**16.** Connect MIL-1553 to CN4 and FC4. Both as Remote Terminal nodes.

**17.** Pull ETH-DE conduit (Bay D→Bay E): terminate Bay D end at FC3 Cape-A ETH-1 port. Terminate Bay E end at CN4 Cape-B ETH-2 port. This completes the FC3↔CN4 Ethernet ring link.

**18.** Terminate ETH-EA conduit ring-close (Bay E→Bay A): terminate Bay E end at FC4 Cape-A ETH-1 port. The Bay A end is already connected to CN1 Cape-B ETH-2 (connected in Phase 3, Step 18). This closes the FC4↔CN1 link and completes the 8-node RSTP ring.

**19.** Power tap: connect CN4 and FC4 power leads from PWR conduit Bay E branch. Verify 5V ±0.05V at each node power header.

### Security Provisioning — Phase 4 Nodes

**20.** Provision TPM 2.0 on CN3, FC3, CN4, FC4 via same procedure as Phase 3 Step 31. Each node receives unique key material.

**21.** Verify Cape-B CPLD write-blocker on CN3 and CN4:
```bash
echo test > /mnt/flightlog/test.txt   # must return "Read-only file system"
```

### Full Ring Integration

**22.** With all 8 nodes powered, verify Ethernet ring via RSTP: run `bridge vlan show` on any node — all 8 switch ports should appear. Disconnect one inter-bay ETH cable and verify traffic re-routes within 1s (RSTP fast-failover).

**23.** Verify full CAN FD ring: `candump can0` on any node must show heartbeat frames 0x001–0x008 within 100ms. Role election produces one FC master, one FC standby, one CN master, one CN standby.

**24.** MIL-STD-1553 final configuration: FC1 = primary Bus Controller (BC), FC2 = standby BC. FC3, FC4, CN1–CN4 = Remote Terminals (RT). Verify all 8 RT addresses conflict-free and respond to BC poll within 9μs.

**25.** RS-485 multidrop: all 8 nodes active on bus. Permanent termination at CN1 (Bay A, bus start) and FC4 (Bay E, bus end) — no additional termination changes needed.

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

**Goal:** Dual-redundant obstacle avoidance operational. All 12 sensors installed, wired to Bay A (Array B, hosted by FC1) and Bay D (Array A, hosted by FC3), and fused into autonomous navigation.

> Requires Phase 4 complete — FC3 (Bay D) must be installed before Array A can be wired.

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

### Array A Installation (FC3, Bay D — Dorsal Aft)

**3.** Install Array A sensors ×6. Cable routes to Bay D:

| Sensor | Position | Station |
|--------|----------|---------|
| S1A | Nose bayonet ring (fwd of S1B) | 25mm |
| S2A | Engine bell rim (aft of S2B) | 440mm |
| S3A | Port hull flush mount (aft of S3B) | 200mm |
| S4A | Stbd hull flush mount (aft of S4B) | 200mm |
| S5A | Dorsal keel (panel B area, fwd of S5B) | 180mm |
| S6A | Forward belly blister (fwd of S6B) | 160mm |

**4.** Connect to TCA9548A + MCP23008 in Bay D, wired to FC3 Cape-A I2C header. Array A I2C bus is **electrically isolated** from Array B — same addresses on separate buses is intentional.

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

The cargo gondola hard points (M3 inserts) and panel C hinge (belly) were installed in Phase 1. This phase installs the gondola shell, clamshell doors, winch mechanism, and cradle, then integrates cargo commands with the elected CN master node (CN1 in Bay A or CN2 in Bay B).

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

**6.** Route DRV8833 control leads and servo cables through PWR conduit belly tap to the elected CN master node Cape-B GPIO header (CN1 in Bay A or CN2 in Bay B — whichever won CN master election).

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

## Phase 7 — Motor Upgrade: 4× XRP 3660-2700KV + 4× Hobbywing 120A + PID Governor (Rev L)

**Goal:** Full-performance dual-EDF propulsion installed in both nacelles. 4× XRP 80mm EDFs replace budget EDFs. 4× Hobbywing 120A ESCs replace budget ESCs. Rev L PID governor commissioned. Aircraft achieves Rev L specified T/W 3.12:1 and max payload 1,406g.

> ★ **Milestone: FULL PERFORMANCE + PID GOVERNOR — Rev L achieved at end of this phase.**

### Why Defer to Phase 7

- Budget EDFs and ESCs (Phases 2–6) proved airframe, avionics, and tandem-series duct geometry at ~$800 lower cost
- Any structural or design defects are corrected before committing to premium motors
- The dual pod (`nacelle_pod_dual_80mm.stl`) is already installed — only the EDFs and ESCs swap out

### Buy List for Phase 7

| Item | Qty | Approx. Cost |
|------|-----|--------------|
| Changesun XRP 3660-2700KV 80mm 6S EDF — Port FWD (CCW) | 1× | ~$170 |
| Changesun XRP 3660-2700KV 80mm 6S EDF — Port AFT (CCW) | 1× | ~$170 |
| Changesun XRP 3660-2700KV 80mm 6S EDF — Stbd FWD (CW) | 1× | ~$170 |
| Changesun XRP 3660-2700KV 80mm 6S EDF — Stbd AFT (CW) | 1× | ~$170 |
| Hobbywing Platinum PRO V4 120A ESC (one per EDF) | **4×** | ~$125ea |
| 12AWG silicone motor phase wire 100mm × 3-phase × 4 (if needed) | — | ~$10 |
| XT30 pigtails (independent power rail per ESC) | 4× | ~$8 total |
| 100A automotive mini poly fuse (one per ESC rail) | 4× | ~$6 total |
| 1000µF 35V electrolytic capacitors (bulk cap per ESC at PDB) | 4× | ~$5 total |
| 4-AWG silicone main bus wire (if not already upgraded) | ~500mm | ~$8 |

> **Sourcing:** XRP 3660-2700KV available CCW and CW from Turbines-RC (EU) and RC-Castle (global). Order CCW for port nacelle (both FWD+AFT), CW for starboard nacelle (both FWD+AFT) to maintain tractor/pusher balance.

> ⚠ **ESC mandatory:** XRP 3660-2700KV draws **84A peak per EDF** on 6S. The Hobbywing 120A provides 43% headroom. Do NOT attempt to run XRP on budget 50–60A ESCs — they will overheat and fail. Replace all 4 nacelle ESCs.

> ⚠ **Power wiring upgrade:** With 4× 84A ESCs, peak nacelle current is 168A/side (336A total). Upgrade main bus to **4-AWG silicone** if not already installed. Each ESC needs an independent XT30 power pigtail with 100A poly fuse at PDB.

### EDF Swap Sequence (per nacelle — repeat for both)

**1.** Power off and disconnect battery. Remove nacelle tip cap.

**2.** Disconnect all 4 budget EDF motor leads at hull exit (FWD and AFT).

**3.** Unscrew 4× M2.5 from AFT EDF. Slide AFT EDF out of pod aft face.

**4.** Unscrew 4× M2.5 from FWD EDF. Slide FWD EDF out of pod intake.

**5.** The `nacelle_pod_dual_80mm.stl` pod remains on the pivot bracket — **do not remove the pod.**

**6.** Slide XRP FWD EDF into intake (housing OD 83mm → 83mm ID pod = slip fit). Torque 4× M2.5 to 0.3 N·m. Route 14AWG phase leads through FWD channel, label "FWD".

**7.** Slide XRP AFT EDF in from aft face. Mount as above. Route 14AWG leads through AFT channel, label "AFT".

**8.** Verify blade tips clear pod wall at 0°, 45°, 90°, 115° nacelle angles — rotate by hand.

**9.** Reinstall nacelle tip cap.

### ESC Replacement Sequence

**10.** Remove 4× budget ESCs from Bay C/D (one per nacelle EDF).

**11.** Mount 4× Hobbywing Platinum V4 120A ESCs:
- ESC-NAC-L-FWD in Bay C-L-FWD position
- ESC-NAC-L-AFT in Bay C-L-AFT position
- ESC-NAC-R-FWD in Bay C-R-FWD position
- ESC-NAC-R-AFT in Bay C-R-AFT position

**12.** For each Hobbywing ESC:
- Connect independent XT30 power pigtail with 100A poly fuse to PDB rail
- Solder 14AWG motor leads from XRP EDF
- Connect DSHOT signal lead to FC1 Cape-A (for ESC-NAC-L-FWD/AFT) or FC4 Cape-A (for ESC-NAC-R-FWD/AFT)
- Connect BLHeli32 serial telem JST-GH 3-pin to Cape-A telem port

**13.** In BLHeli32 Suite (via FC USB passthrough):
- Enable BDSHOT on all 4 nacelle ESCs
- Set telem baud 115200 on all 4 nacelle ESCs
- Verify BDSHOT RPM returns 0 at rest on all 4 channels
- Verify current limiting: set to 120A in BLHeli Suite

**14.** Update CG: XRP quad vs budget quad adds significant mass. Recheck CG at 190mm from nose with flight battery. Shift battery on rail as needed.

### Rev L PID Governor Commissioning

**15.** Flash Rev L governor firmware to FC1–FC4:
```
# From GCS via SiK or WiFi:
mavftp upload governor_firmware_revL.bin /fc/m4f/governor.bin
mavftp upload governor_config.h /fc/m4f/governor_config.h
```
Firmware distributes via Ethernet ring CN1→FC1→FC2→FC3→FC4 with TPM 2.0 signature verification.

**16.** Bench calibration (nacelle on thrust stand with load cell, bench power supply):
```
python3 governor_cal.py --mode bench --nacelle port
python3 governor_cal.py --mode bench --nacelle stbd
```
Each run sweeps 0%→100%→0% throttle, fits k coefficient (T = k × RPM²), outputs `EDF_THRUST_K`.

**17.** Update `governor_config.h` with measured k values. Re-flash to FC1–FC4.

**18.** PID step-response verification (bench, EDF in pod, tethered):
- Apply 10% throttle step → verify RPM settle in <200ms, overshoot <5%
- Verify equalization: |RPM_FWD − RPM_AFT| < 100 RPM at steady state
- Verify AFT runs ~2% higher RPM than FWD at same thrust command

**19.** Fault injection test (bench, tethered):
- Inject FAULT_INJECT_OVERTEMP to ESC-NAC-L-FWD via GCS
- Verify: FWD throttle → 0, AFT continues, MAVLink STATUSTEXT "EDF-L-FWD FAULT_OVERTEMP"
- Verify fault stays latched (does not recover when temp injection removed)
- Power cycle. Verify fault clears. Verify GCS acknowledgment required before arm.

### Full Performance Tests

**20.** Bench thrust test (tie-down, tethered, all 4 nacelle EDFs running):
- 100% throttle for 5s per nacelle: verify ≥5,300g per nacelle (thrust stand or suspended scale)
- Total nacelle thrust: ≥10,600g
- Fuselage EDF at 100% 4S: verify ≥650g
- **Total: ≥11,250g** (Rev L spec target)

**21.** ESC temperature: Hobbywing 120A ESC junction ≤80°C at sustained full throttle 10s on all 4 nacelle ESCs. Monitor with IR thermometer.

**22.** T/W verification:
- Empty (6S 4000mAh, 3,607g AUW): measured thrust 11,250g → T/W = **3.12:1** ✓
- With 250g cargo (6S 2800mAh, 3,742g AUW): thrust 11,250g → T/W = **3.01:1** ✓

**23.** Max payload test (incremental, tethered hover):
- 500g payload hover: stable, altitude hold
- 1,000g payload hover: T/W ≥2.22:1
- 1,400g payload: T/W ≥2.01:1 (theoretical max 1,406g at T/W = 2.0)

**24.** Full performance flight: forward flight at cruise speed, nacelle transitions, 1-EDF fault injection at altitude (governor maintains flight), cargo delivery, RTH.

### Phase 7 Pass Criteria

- [ ] Static bench thrust: ≥11,250g total at full throttle (all 4 nacelle EDFs + fuselage)
- [ ] ESC temps ≤80°C at full sustained thrust on all 4 nacelle ESCs
- [ ] T/W ≥3.12:1 empty (3,607g AUW), ≥3.01:1 with 250g cargo (3,742g AUW)
- [ ] Governor active: BDSHOT RPM feedback confirmed on all 4 ESCs
- [ ] Governor equalization: |RPM_FWD − RPM_AFT| < 100 RPM steady-state
- [ ] Fault latch test passed: single-EDF fault, partner continues, MAVLink alert issued
- [ ] Successfully hover-lifted ≥1,000g payload
- [ ] All Hobbywing ESC calibration LEDs show correct armed state
- [ ] CG at 190mm from nose with flight battery verified

**Phase 7 cost estimate:** 4× XRP EDF ~$680 + 4× Hobbywing 120A ~$500 + power hardware ~$37 = **~$800** (vs ~$590 for single-EDF Rev J Phase 7)

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
| **3** | **Minimum Viable Flyer ★ FIRST FLIGHT** | **~$740** | **~$1,030** | CN1+FC1+CN2+FC2, power, ESCs, radios, battery |
| 4 | Full 8-Node Architecture | ~$540 | ~$1,570 | CN3+FC3+CN4+FC4 — full ring redundancy |
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
| CAN-FD | Port keel rail, full length | 4-pin JST-GH (CANH/CANL/GND/VCC) — 120Ω at CN1 (start, Bay A) and FC4 (end, Bay E) | 3 (CN1+FC1+CN2+FC2), 4 (full ring) |
| RS-485 | Stbd keel rail, full length | 4-pin JST-GH (A/B/GND/VCC) — 120Ω at CN1 (start, Bay A) and FC4 (end, Bay E) | 3 (CN1+FC1+CN2+FC2), 4 (full ring) |
| MIL-1553 | Dorsal centre spine, full length | 4-pin shielded JST-GH, 78Ω — FC1=BC, FC2=standby BC | 3 (CN1+FC1+CN2+FC2), 4 (full ring) |
| ETH-AB | Port forward: Bay A → Bay B | 8-pin JST-GH Cat5e — FC1↔CN2 ring link | 3 (connected Phase 3 Step 27) |
| ETH-BD | Port mid: Bay B → Bay D | 8-pin JST-GH Cat5e — FC2↔CN3 ring link | 3 (Bay B end connected, Bay D capped), 4 (connected) |
| ETH-DE | Stbd aft: Bay D → Bay E | 8-pin JST-GH Cat5e — FC3↔CN4 ring link | 4 (CN3+FC3+CN4+FC4 install) |
| ETH-EA | Stbd full: Bay E → Bay A | 8-pin JST-GH Cat5e — FC4↔CN1 ring-close link | 3 (Bay A end connected, Bay E capped), 4 (connected) |
| PWR | Belly centre | 14AWG power + 20AWG servo bundle; one tap per bay, each tap feeds one CN + one FC | 3 (ESCs, BEC, nav lights) |

---

## Reference: Access Panel Quick-Reference

| Panel | Location | Station | Closure | What's Inside |
|-------|----------|---------|---------|---------------|
| A | Nose, top | 0–91mm | Bayonet | CN1 Cape-B (lower) + FC1 Cape-A (upper); CN1 radios (SiK/LoRa/WiFi/RCRS-49); FC1 GPS coax (~59mm); ETH-AB/ETH-EA conduit ends; CAN FD 120Ω at CN1; Array B mux |
| B | Dorsal fwd | 91–165mm | 4× M2.5 | CN2 Cape-B (lower) + FC2 Cape-A (upper); CN2 RCRS-49; FC2 GPS coax (~130mm); ETH-AB/ETH-BD conduit ends |
| C | Cargo belly | 160–251mm | Hinge | Cargo gondola, clamshell doors, winch motor |
| D | Dorsal aft | 251–320mm | 4× N42 magnets | CN3 Cape-B (lower) + FC3 Cape-A (upper); CN3 RCRS-49; FC3 GPS coax (~275mm); ETH-BD/ETH-DE conduit ends; CN3 log μSD; Array A mux |
| E | Aft service | 320–388mm | 4× M2.5 | CN4 Cape-B (lower) + FC4 Cape-A (upper); CN4 RCRS-49; FC4 GPS coax (~350mm); ETH-DE/ETH-EA conduit ends; CAN FD 120Ω at FC4; CN4 log μSD; budget→Hobbywing ESCs |
| F | Engine bell | 388–457mm | Bayonet | XFLY 40mm fuselage EDF, fuselage nozzle servo |

---

## Reference: Node Architecture Summary (Rev K)

Bus order: **CN1 → FC1 → CN2 → FC2 → CN3 → FC3 → CN4 → FC4** (interleaved CN+FC per bay — any single segment or bay power failure leaves ≥2 FC + ≥2 CN on both sides of the break)

| Node | Bay | Position | Hardware | Role (elected) | Security |
|------|-----|----------|----------|----------------|----------|
| CN1 | A — Nose | Lower (floor) | PocketBeagle 2 + Cape-B 90×60mm | CN master or standby; radios master; CAN FD bus start (120Ω soldered) | SLB9670 TPM 2.0 + ATF16V8BQL CPLD write-blocker |
| FC1 | A — Nose | Upper (inter-cape) | PocketBeagle 2 + Cape-A 85×55mm | FC master or standby; OA Array B host; 1553 primary BC | SLB9670 TPM 2.0 |
| CN2 | B — Dorsal Fwd | Lower (floor) | PocketBeagle 2 + Cape-B 90×60mm | CN master or standby | SLB9670 TPM 2.0 + ATF16V8BQL CPLD write-blocker |
| FC2 | B — Dorsal Fwd | Upper (inter-cape) | PocketBeagle 2 + Cape-A 85×55mm | FC master or standby; 1553 standby BC | SLB9670 TPM 2.0 |
| CN3 | D — Dorsal Aft | Lower (floor) | PocketBeagle 2 + Cape-B 90×60mm | CN node | SLB9670 TPM 2.0 + ATF16V8BQL CPLD write-blocker |
| FC3 | D — Dorsal Aft | Upper (inter-cape) | PocketBeagle 2 + Cape-A 85×55mm | FC node; OA Array A host | SLB9670 TPM 2.0 |
| CN4 | E — Aft Service | Lower (floor) | PocketBeagle 2 + Cape-B 90×60mm | CN node; cargo control | SLB9670 TPM 2.0 + ATF16V8BQL CPLD write-blocker |
| FC4 | E — Aft Service | Upper (inter-cape) | PocketBeagle 2 + Cape-A 85×55mm | FC node; CAN FD bus end (120Ω soldered) | SLB9670 TPM 2.0 |

**All FC nodes (Cape-A):** ICM-42688-P IMU · BMP388 baro · u-blox M10Q GPS · ATA6561 CAN FD · MAX3485E RS-485 · DS26LV31/32 + PE-68515 1553 · DP83825I ×2 Ethernet · SLB9670 TPM 2.0 · 8× servo PWM rail

**All CN nodes (Cape-B):** SiK 915MHz · LoRa RFM95W 915MHz · TI WL1837MOD WiFi/BT · RCRS-49 sub-module · ATA6561 CAN FD · MAX3485E RS-485 · DS26LV31/32 + PE-68515 1553 · DP83825I ×2 Ethernet · SLB9670 TPM 2.0 · ATF16V8BQL CPLD write-blocker · W25Q128JV NOR flash log · DRV8833 winch · HX711 load cell · 2× cargo servo PWM

---

*CC BY 4.0 · 2026 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP*
*Hull: Peter Farell CC BY 4.0 · Nozzles: BamJr CC BY 4.0 · Visual inspiration: Firefly/Serenity © Joss Whedon / Mutant Enemy / Universal*
