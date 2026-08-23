# Serenity UAV — Avionics EMI Hardening (500 W/m^2 environment) Work Breakdown Structure (Detail)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0
**Current design revision:** Rev S (2026-07-04)

> **Detail-holder for the root WBS.** The repository-root [`TODO.md`](../../TODO.md)
> is a compact index — headings, subheadings, and short (<=70-char) checkbox items
> only, per root `AGENTS.md`. This file carries the full task detail for the WBS
> branches the root indexes below. Close an item here first, then check it off in
> the root index as a commit prerequisite (root `AGENTS.md` "Revisions and Version
> Control").

*"Everything is shiny, Cap'n. Not to fret. — Flight Engineer"*

---

## §0.6 — IEC 62368-1 PCB Layout Isolation Verification
*(root `WBS.md` §0.6)*


- [x] **Verify creepage and clearance distances in Pilot PCB layout** [REF-IEC-001 §5.5.2]
    — **verified 2026-06-22 via `kicad-cli pcb drc` (KiCad 9.0.2) against `Pilot.kicad_pcb`.
    Result: NOT MET — still BLOCKS PCB fab.** DRC found 47 violations of the 0.5 mm
    `ISOLATION` netclass rule; after excluding 34 same-package pin-to-pin false positives
    (adjacent pins on the secondary side of the same isolator IC), **13 are genuine
    cross-domain clearance violations** — the `TMESH_P`/`TMESH_N` tamper-detect mesh
    routed too close to (in some cases inside the netclass minimum of) the isolated
    `GND2_CAN`/`GND2_ETH` domains, actual spacing as low as 0.125 mm against the 0.5 mm
    netclass minimum and the ≥ 8 mm physical creepage target documented in `Pilot.md`.
    This confirms and quantifies the tamper-mesh routing problem already tracked in
    `TODO.md` §1.2a. Verification performed; **layout rework not performed** — per
    `CLAUDE.md`, repositioning footprints/routes to close this gap is referred to the
    user, not done automatically.
- [x] **Verify creepage and clearance distances in XO PCB layout** [REF-IEC-001 §5.5.2]
    — **verified 2026-06-22 via `kicad-cli pcb drc` against `XO.kicad_pcb`. Result: NOT
    MET — still BLOCKS PCB fab.** Same root cause as Pilot: 40 `ISOLATION`-netclass
    violations, 31 same-package false positives excluded, **9 genuine cross-domain
    violations** between `TMESH_P`/`TMESH_N` (and, in one case, a primary-side Ethernet
    PHY ground pad) and the isolated `GND2_CAN`/`GND2_RS485` domains, actual spacing as
    low as **0.0 mm (direct contact)**. Not fixed here, same reason as Pilot.
- [x] **Document verified creepage/clearance values** in `avionics/kicad/Pilot.md` and
    `avionics/kicad/XO.md` — added a "Verification status" block to each file's
    "Isolation creepage" PCB layout constraint with the measured DRC findings above,
    dated and tool-versioned, distinguishing the design target (≥ 8 mm creepage /
    ≥ 1.5 mm clearance, IEC 62368-1 Annex G) from the as-laid-out current state (not met).


## §1.4 — EMI Hardening Beyond the PCBs (500 W/m^2 design objective)
*(root `WBS.md` §1.4)*


#### 1.4.1 Faraday Enclosures

**Design constraints (apply to every enclosure below):**

- Must have proper bonding/grounding without loops.

- Must have a fan and appropriate cooling

- Must minimize weight, size, and cost

- Must account for all sensor inputs and flight control and comms outputs.

- Must account for RF routing from external antennas to internal transceivers

- Must protect the log uSD

- [ ] **PB2-I + Pilot Enclosure** (Shepherd's Room / Inara's Shuttle — no Commo board):
    - [ ] Confirm internal clearance for PB2-Industrial + Cape-A-2 stack height against
        the FAR-CAGE-AV placeholder envelope (76×56×88 mm, §1.1.5).
    - [ ] Cut-outs for GPS/IMU/barometer sensor leads, ToF array cabling, servo/ESC
        connectors, and the microSD log slot — each cut-out gets its own FAR-FT-PANEL
        feedthrough or grommet, not an open hole.
    - [ ] Mount FAR-FAN-40 + FAR-EMI-VENT-40 on the low-pressure side of the enclosure;
        verify intake/exhaust path does not create a direct RF leakage slot.
    - [ ] Bond enclosure to chassis ground via FAR-BOND-STRAP (single point, no loop).
- [ ] **PB2-I + XO Enclosure** (all 4 bays — Cape-B-2, plus Commo in River's Room /
    Simon's Medbay only):
    - [ ] Confirm internal clearance for PB2-Industrial + Cape-B-2 (+ Commo where fitted)
        stack height against the FAR-CAGE-AV placeholder envelope.
    - [ ] Cut-outs for CAN FD/RS-485/Ethernet/MIL-1553 connectors, SMA antenna feeds
        (WiFi/SiK/LoRa per §1.4.2), and the microSD log slot — feedthrough or grommet
        per cut-out.
    - [ ] River's Room / Simon's Medbay variant: add the LoRa + 49 MHz SMA feedthrough
        pair for Commo; Shepherd's Room / Inara's Shuttle variant omits these.
    - [ ] Mount FAR-FAN-40 + FAR-EMI-VENT-40; bond via FAR-BOND-STRAP.

#### 1.4.2. Antenna Placement and feedlines

- [x] **Resolve total antenna count per stack against the PACE radio table** *(done
    2026-06-22)* — the prior "2 antennas per comm link × 4 links + 2 GPS = 10" count basis
    was wrong on two counts: (a) no stack actually mounts an antenna for all 4 external
    links — each of the 4 bays carries exactly 2 external-link antennas (its PACE
    primary + secondary, per `CLAUDE.md`), not one-per-link-globally; (b) GPS/GNSS is
    one patch **per FC node (Pilot, Cape-A-2)**, and there are 4 FC nodes (one per bay),
    not 2. Resolved count, reconciled against current (pre-Rev-R1) hardware fit:

    | Bay | Radios fitted | External antennas | GPS |
    | --- | --- | --- | --- |
    | Shepherd's Room (Bay A) | XO: Wi-Fi, SiK, LoRa chain present on PCB | SiK whip (primary) + Wi-Fi patch (secondary) = 2 | 1 |
    | Inara's Shuttle (Bay B) | XO: Wi-Fi, SiK, LoRa chain present on PCB | Wi-Fi patch (primary) + SiK whip (secondary) = 2 | 1 |
    | River's Room (Bay D) | XO + Commo (49 MHz) | 49 MHz whip (primary) + LoRa whip (secondary, fed from XO's `J_SMA_LORA`) = 2 | 1 |
    | Simon's Medbay (Bay D) | XO + Commo (49 MHz) | 49 MHz whip (primary, **independent antenna — see new sub-task below**) + SiK whip (secondary) = 2 | 1 |

    **Total: 8 external C2/payload-link antennas + 4 GPS patches = 12 physical antennas.**
    Every XO (Cape-B-2) carries identical Wi-Fi/SiK/LoRa RF frontends per board (all
    4 XO boards are the same PCB), but only the antenna feeding that bay's PACE-assigned
    primary/secondary link is populated — the unused chain's SMA pad is left unpopulated
    (no antenna, no feedline) rather than wasting mass/hull penetrations on a link that
    bay never uses. **Zigbee 2.4 GHz has no antenna mount** — see flagged gap below; it is
    excluded from the 12-antenna count until the hardware gap is resolved.

- [x] **Antenna mounts** *(types and stations resolved 2026-06-22; physical hull
    placement still needs FreeCAD/slicer verification — see sub-tasks)*:
    - [x] **Shepherd's Room** (Bay A, nose, sta ≈ 59 mm) — SiK 915 MHz ¼-wave RP-SMA whip
        (primary) + Wi-Fi 5 GHz RP-SMA whip (secondary). Mount both on the dorsal hull
        skin near the bay, ≥ 30 mm apart (reduce 915/5800 MHz frontend desense).
    - [x] **Inara's Shuttle** (Bay B, dorsal fwd, sta ≈ 130 mm) — Wi-Fi 5 GHz RP-SMA whip
        (primary) + SiK 915 MHz RP-SMA whip (secondary). Same dorsal mount style and
        spacing as Shepherd's.
    - [x] **River's Room** (Bay D, dorsal aft, sta ≈ 275 mm) — 49 MHz top-wire antenna
        (existing `WIRE-49MHZ`/`POST-FWD-49`/`POST-AFT-49`, §1.1.1.0b; primary) + LoRa
        915 MHz RP-SMA whip (secondary, fed from XO `J_SMA_LORA`). **Relocated
        2026-06-22 (with user): the 49 MHz top wire moves from the dorsal centerline to
        the PORT flank, shoulder height** — see the port/starboard sub-task below;
        LoRa whip stays dorsal.
    - [x] **Simon's Medbay** (Bay D, aft service, sta ≈ 350 mm) — **independent** 49 MHz
        top-wire antenna, new, on the **STARBOARD flank, shoulder height** (primary; see
        dedicated sub-task below — do not share River's antenna) + SiK 915 MHz RP-SMA
        whip (secondary, stays dorsal).
    - [x] **4× GPS/GNSS patch antenna mounts** — one per FC node (Pilot, Cape-A-2), all
        dorsal hull, face up, per existing routing tasks (Phase 5/6 install steps,
        TODO.md lines ~2645/2666/2773/2794): FC1 sta ≈ 59 mm, FC2 sta ≈ 130 mm,
        FC3 sta ≈ 275 mm, FC4 sta ≈ 350 mm. ≥ 3 mm clearance from the 49 MHz wire posts
        (already a documented constraint on `POST-FWD-49`) — now a flank-to-dorsal
        clearance check rather than a same-surface one, since the 49 MHz posts moved
        off the dorsal centerline (below); re-verify the 3 mm figure still applies once
        the shoulder-height mount line is fixed.
    - [ ] **Zigbee 2.4 GHz antenna mount — BLOCKED, hardware gap confirmed; antenna
        strategy decided 2026-06-22 (with user).** XO (Cape-B-2) Rev S has no Zigbee
        transceiver, antenna filter chain, or SMA pad (the CC2652R7 Zigbee radio exists
        only in the archived COMMS-HAT-1 design, not in the current Rev S Cape-B-2
        schematic) — **no antenna can be mounted for hardware that does not exist on
        the board**, so this remains a genuine PCB scope gap, not just a placement
        question. **Decision:** rather than a time-shared coexistence switch, split
        the existing dual-band Wi-Fi antenna by frequency instead of by time —
        **restrict WL1837MOD Wi-Fi to 5 GHz only** (already the spec for the Wi-Fi
        whip mounts above) and feed the freed 2.4 GHz path to the future CC2652R7
        Zigbee module through a passive **2.4/5 GHz diplexer** ahead of one shared
        broadband antenna. Because Wi-Fi and Zigbee no longer overlap in frequency,
        this needs no `RF_NCOEX` coexistence arbitration and no switching — both
        radios can transmit/receive simultaneously through the diplexer, unlike a
        switched-antenna approach. The diplexer (and the antenna it feeds) remains a
        single passive point of failure shared between the two radios, but a passive
        component is materially more reliable than an active coexistence switch, and
        Wi-Fi/Zigbee are not PACE failover partners of each other (unlike River/Simon's
        49 MHz link, sharing here doesn't undermine the redundancy mandate).
        Still open: which bay carries the Zigbee module once added, diplexer part
        selection, and Cape-B-2 schematic work to add the CC2652R7 RF chain.
        **Cross-reference added to §1.2a as a tracked PCB scope gap.**
    - [ ] **Verify the 6 dorsal mount stations (Shepherd ×2, Inara ×2, River's LoRa whip,
        Simon's SiK whip) in FreeCAD against the baked hull** — confirm ≥ 30 mm
        antenna-to-antenna spacing is actually achievable on the as-built dorsal skin at
        each bay's station, and that no mount collides with an access-panel cover
        (§1.1.1.0a), the bow sensor pod (§1.1.1.1a), or the dorsal antenna fin
        (`dorsal_antenna_fin.stl`). **BLOCKS dorsal antenna mount printing.**
    - [ ] **Verify the 2 flank mount lines (River's 49 MHz, port; Simon's 49 MHz,
        starboard) in FreeCAD against the cargo clamshell door swing envelope** — see
        the dedicated sub-task under "Second 49 MHz antenna" below.
        **BLOCKS flank antenna mount printing.**

- [x] **Feedlines** *(cable spec and run-length budget resolved 2026-06-22)*:
    - Cable: **RG-316** (50 Ω, PTFE dielectric, silver-plated copper braid) for every
        aircraft-side antenna-to-SMA-bulkhead run. RG-316 is already the spec used for
        Commo's own 49 MHz feed (`Commo.md` lines 553–554); standardizing on one cable type
        for all 8 runs simplifies stock and crimping tooling.
    - Run-length budget: **≤ 300 mm per run** for Wi-Fi/SiK/LoRa whip-to-bulkhead runs
        (antenna is mounted directly over its bay); **≤ 500 mm** for the 49 MHz runs
        (River's existing run and Simon's new run both route from the bay's Commo J2 to
        the forward wire-post loading coil, matching the existing 500 mm ceiling already
        set in `Commo.md`). RG-316 loss at 915 MHz/2.4 GHz over these lengths is
        ≈ 0.3–0.5 dB — negligible against the link budgets in `skipper_antenna_spec.md`.
    - Routing: each run exits its bay's Faraday enclosure through an SMA bulkhead
        feedthrough in the FAR-FT-PANEL (§1.1.5, still in design) and is dressed along
        the hull skin to its mount, kept ≥ 5 mm clear of the digital-section keep-out
        zones (CAN FD/RS-485/Ethernet/1553 trunk, per §1.4.4 wiring keep-outs).
        **BLOCKS final feedline length confirmation until FAR-FT-PANEL mechanical
        design (§1.1.5) is complete.**

- [x] **Chokes** *(part and placement resolved 2026-06-22)* — one **Würth 74271222**
    snap-on ferrite clamp per antenna feedline, placed within 25 mm of the Faraday
    enclosure boundary crossing on the *inside* (cage) end of the run. This mirrors the
    treatment Commo already applies to its own 49 MHz feedline (`Commo.md` lines 553–557)
    and is consistent with the 500 W/m² EMI design objective (`CLAUDE.md`). 8 feedlines
    (Shepherd ×2, Inara ×2, River's LoRa run, Simon's SiK run, plus River's and Simon's
    49 MHz runs) → **8× Würth 74271222 required**, added to BOM.

- [x] **Second 49 MHz antenna for Simon's Medbay** *(decision made 2026-06-22, with
    user; routing corrected 2026-06-22, with user)* — Simon's Commo board currently has
    no antenna feed at all; only River's J2 is wired to the single existing
    `WIRE-49MHZ` top-wire antenna. **Decision: build a second, fully independent 49 MHz
    antenna for Simon rather than sharing River's antenna through a mux/switch or
    passive splitter.** A shared antenna (switched or split) makes the antenna/switch a
    single point of failure for *both* stacks' 49 MHz link, which directly contradicts
    the first-class redundancy requirement in `CLAUDE.md` — and the mass cost of a
    second antenna is trivial (≈ 9–11 g, see BOM) against that benefit. *(Moved here
    from former §1.1.1.0.1, 2026-06-22.)*
    - [x] **Design mirrors the existing River system, full length**: PETG forward wire
        post + 38 µH base-loading coil, ~470 mm stainless-steel top wire (same length as
        `WIRE-49MHZ`, not shortened), aft wire post with ceramic insulator, AWG 22
        stranded copper counterpoise (routed inside the foam alongside the structural
        keel — the keel itself is interior/embedded and not affected by the exterior
        clamshell door swing discussed below, so this counterpoise routing is unchanged),
        RG-316 feed to Simon's Commo J2 (≤ 500 mm), Würth 74271222 choke at the Faraday
        crossing — same component set as `POST-FWD-49`/`WIRE-49MHZ`/`POST-AFT-49`/
        `WIRE-COUNTERPOISE-49MHZ`, new reference IDs (see BOM).
    - [x] **Route on the STARBOARD flank, shoulder height — not ventral, not dorsal
        centerline** *(corrected 2026-06-22, with user)* — two routings were rejected:
        (1) a second full-length wire parallel to River's on the same dorsal ridge would
        sit well under one wavelength (λ = 6.12 m at 49 MHz) from the first, risking
        mutual coupling/detuning of both antennas; (2) a ventral/keel-line run (the
        original proposal here) was rejected outright once `generate_cargo_doors.py`
        was checked — the cargo bay clamshell doors hinge at the **outboard flank/belly
        edge** and swing up to **180°**, sweeping the lower flank and belly through the
        door's full Y-span; any exterior wire post mounted there is in the door's path.
        **Resolution: both antennas move off the dorsal centerline entirely.** River's
        existing antenna relocates to the **port** flank, shoulder height; Simon's new
        antenna goes on the **starboard** flank, shoulder height, same sta ≈ 120–580 mm
        span and full ~470 mm length as River's. Shoulder height is chosen specifically
        because it is above the door's swing reach (door hinges at the bottom-outboard
        edge) and laterally separated from its mirror-image counterpart by the full
        fuselage width (port vs. starboard), solving both the coupling and the door
        problems at once — see updated `rcrs49_wire_post.scad` header and §1.1.1.0b.
        **SUB-TASKS OPEN:**
    - [ ] **Verify the exact shoulder-height Z offset in FreeCAD against the cargo
        door's 180°-open envelope** (door panel width from the hinge line) at every
        station along sta 120–580 mm, not just within the door bay's own Y-span —
        confirm port and starboard mount lines clear the door on both sides.
        **BLOCKS bonding either antenna's posts.**
    - [ ] **Confirm the port/starboard mount line also clears the wing roots** (wings
        attach at the cargo section's lateral walls, `CLAUDE.md`) — the flank line
        passes close to this area within the cargo section.
        **BLOCKS Simon's 49 MHz antenna fabrication; BLOCKS River's antenna relocation.**
    - [ ] **Bench-verify isolation between the two 49 MHz antennas** (River's port,
        Simon's starboard) before first flight — confirm neither antenna's feedpoint
        impedance shifts unacceptably with the other antenna present, and that
        simultaneous Commo TX on one does not desense the other's receiver beyond an
        acceptable margin. Use the same HDOP-with-TX-active bench test already specified
        for `POST-FWD-49` as a model.

- [x] **Ensure all transceivers have antenna placement and wiring from XO and/or Commo
    boards to mounted antennas** *(moved here from former §1.1.1.0.1, 2026-06-22)* —
    satisfied by the mount/feedline/choke specs above for all populated radio chains;
    remaining open items are the Zigbee hardware gap (flagged above) and the FreeCAD/
    bench verification sub-tasks, which are tracked individually rather than left as one
    generic catch-all.

**Mass/cost added to `docs/bom_revR.json` `avionics.antenna_system` (2026-06-22, updated
after the port/starboard routing correction):** 11 new line items — ANT-WIFI-5G ×2,
ANT-SIK-915 ×3, ANT-LORA-915 ×1, ANT-GPS-PATCH ×4, WIRE-COUNTERPOISE-49MHZ ×1
(backfilled, was referenced but never added), WIRE-49MHZ-2/POST-FWD-49-2/POST-AFT-49-2/
WIRE-COUNTERPOISE-49MHZ-2 (Simon's independent 49 MHz antenna, full-length starboard
design, not the earlier shortened ventral proposal), COAX-RG316-AIRFRAME ×1,
CHOKE-FERRITE-ANT ×8 — **+96 g / +$93** beyond the pre-existing 3-item 49 MHz antenna
entry (9 g / $16, itself relocated port-flank, mass unchanged). New `antenna_system`
total: **105 g / $109.** This is a small fraction of the ~3,590 g AUW noted in
`totals.note`; no AUW/T-W recheck needed at this magnitude.

#### 1.4.3 internode communication wiring

Per-bus signal wiring specification for the 4 internode buses (CAN FD, MIL-STD-1553B, RS-485,
Ethernet) connecting all 8 nodes — see CLAUDE.md "Onboard Communications."

- [ ] **CAN FD** — specify bus topology (linear trunk vs. star), termination (120 Ω at each
    physical end), node tap spacing, and connector pinout per node; cross-reference the
    CAN_H/CAN_L footprint pinout already fixed on Pilot (§1.2).
- [ ] **RS-485** — specify daisy-chain topology, termination, and connector pinout per node;
    cross-reference the RS485_A/B footprint pinout already fixed on Pilot (§1.2).
- [ ] **MIL-STD-1553B** — specify bus controller / remote terminal wiring per node role
    (§4.2 "MIL-STD-1553B RT implementation," §4.3 "MIL-STD-1553B BC/RT tasks"); stub length
    and transformer-coupling placement per node, matching the 1553-XFM coupling already
    partially netted on Pilot (§1.2).
- [ ] **Ethernet** — specify CPSW3G ring topology (node-to-node order), cable category, and
    connector pinout; cross-reference the 100 Ω ±10% MDI impedance-controlled traces already
    specified on Pilot/XO (§1.2) and the RSTP ring management firmware task (§4.3).

#### 1.4.4 flight control signal wiring

Per-signal-type wiring specification for sensor/actuator signals local to each FC node.

- [ ] **UART** — specify wiring for GPS (u-blox M10Q NMEA/UBX, §4.2), SBUS-equivalent
    (§1.2 "Add SBUS/UART DIP switch to Pilot"), and any inter-cape UART links.
- [ ] **I2C** — specify wiring for IMU/barometer (ICM-42688-P, BMP388/390 — note these are
    SPI per §4.2, verify bus assignment), ToF array mux (TCA9548A) and XSHUT GPIO expander
    (MCP23008), and the `U-GPIO` PCA9555DB expander already added to Pilot (§1.2).
- [ ] **BDSHOT/DSHOT (ESC telemetry)** — specify wiring for the ESC-PWM connector (DSHOT0–3,
    JST-GH 5-pin, already defined on Pilot §1.2) and BDSHOT600 telemetry return path on PRU-ICSS
    (§4.2 "EDF ESC PID governor").
- [ ] **PWM** — specify wiring for nacelle tilt servo control (EHRPWM/PRU, §4.2 "Nacelle tilt
    servo PWM generation") and the SERVO-PWM 1×8 connector pinout already defined on Pilot
    (§1.2).

#### 1.4.5 power distribution — Flight Engineer (PDB) and battery

**Battery placement decision (2026-06-08):**
The 6S 4000 mAh LiPo (~450–520 g, ~155×52×36 mm) must be located near the aircraft CG.
Phase 5 ground-test requirement: static CG at 190 mm from nose (REVN_BUILD_GUIDE_24IN.md §Phase 5).
The keel datum at 190 mm from nose falls within the **middle ring section** (between keel stations
165 mm and 251 mm), which is the main fuselage body above the cargo gondola.
Battery is placed on the keel floor of the middle section, oriented longitudinally, secured by:
- Two M3 boss standoffs at X≈−190 mm (CG station) on the keel face
- Velcro retention strap through keel slot (safety tether, not sole retention)
- Slide-in rail guides on keel face prevent lateral shift at 3g maneuver

**Flight Engineer (PDB) placement decision (2026-06-08):**
Flight Engineer (XT90 PDB, 4× XT30 outputs, ~80×60 mm) mounts adjacent to the battery in the middle
section keel area (X≈−165..−245 mm station range) to minimise high-current 14 AWG wire length
to the four nacelle ESC feeds (fed through PTFE conduits in the wing spar channel and to the
cargo gondola lateral walls).
Battery swap access via a **ventral hatch** in the middle section belly skin (hatch centered at
X≈−190 mm, ~120×60 mm opening; 2 mm shoulder lip; 4× M2 captive screws).

**Open items — BLOCKS Phase 1 foam pour:**
- [ ] **Add FlightEngineer/battery boss pattern to `middle_canonical_shell24.scad`.**
    Boss posts: 4× M3 at (±55 mm X) × (±25 mm Z) from X=−190 mm keel center for battery tray.
    Flight Engineer PDB: 4× M3 boss posts at X≈−205 mm, Z=CZ±25 mm. Both on keel interior face (+Y rail).
    Verify boss positions clear keel CF flat bar (6×3 mm) and ring frame station notches in slicer.

- [ ] **Add ventral battery-swap hatch cut to `middle_canonical_shell24.scad`.**
    120×60 mm belly cut centered at X=−190 mm; 2 mm shoulder lip; same pattern as avionics panels.
    **BLOCKS Phase 1 foam pour** (void former must clear hatch zone before foam pour).

- [ ] **Create `flight_engineer_battery_tray.scad`.**
    CF-PETG slide-in rail guide tray for 6S LiPo 155×52×36 mm; M3 attachment to boss posts;
    two captive Velcro strap slots; XT90 connector exit cutout on AFT face.
    **Add to Phase 0 print schedule.**

- [ ] **Create `flight_engineer_pdb_tray.scad`.**
    CF-PETG mounting tray for Flight Engineer PDB (80×60 mm footprint); M3 boss attachment;
    XT90 input pigtail route-through; 4× XT30 output ports facing AFT (toward ESC conduits).
    **Add to Phase 0 print schedule.**

- [x] **Flight Engineer PCB KiCad files generated (Rev A, 2026-06-10):**

    - [x] `avionics/kicad/FlightEngineer.kicad_pro` — project file; net classes VBAT/PGND/POWER_5V/Default; DRC rules

    - [x] `avionics/kicad/FlightEngineer.kicad_sch` — full schematic; 90×65 mm 4-layer; BQ76930 6S cell monitor;
                dual TPS54620 5V BEC; TPS54540 6V BEC; 5× INA226 monitors; 4× ESC branches with 40A fuses +
                470µF caps + CMC + 1 mΩ shunts; SMBJ33CA TVS; AON6556 discharge FET; dual Würth 7440640500 CM filter

    - [x] `avionics/kicad/FlightEngineer.kicad_pcb` — PCB outline + 4-layer stackup (F.Cu signal, In1.Cu GND,
                In2.Cu VBAT 4oz, B.Cu signal); 4× M3 NPTH mounting holes; all 19 nets declared
    - [x] `avionics/kicad/gen_flight_engineer.py` — Python generator producing all three KiCad files
- [x] **Flight Engineer PCB — DRC run and gerbers generated (Rev A, 2026-06-10):**
    - [x] Run KiCad DRC; resolved all shorting and 0.0 mm clearance violations
    - [x] Generate gerbers to `avionics/kicad/gerbers/FlightEngineer/` (17 Gerber layers + FlightEngineer.drl)
    - [ ] **DRC accepted violations (document only — not fixable without PCB re-architecture):**
        - [ ] 16 clearance violations at 0.15 mm: INA226 MSOP-10 adjacent pads (pins 3/4) at 0.5 mm pitch
        inherently violate 0.2 mm PGND/POWER_5V class rule; IPC-2221B allows ≥ 0.1 mm for ≤ 31 V
        - [ ] 77 courtyard overlaps: dense 90×65 mm layout; 3D bodies do not conflict; no manufacturing impact
        - [ ] 59 lib_footprint_mismatch: all footprints are inline in .kicad_pcb (not library copies); expected
        - [ ] 33 silk_over_copper / 26 silk_overlap / 2 silk_edge_clearance: cosmetic; board is fab-ready
        - [ ] 8 lib_footprint_issues: inline footprints; not KiCad library-linked; expected
        - [ ] 181 unconnected_items: traces not yet routed (power planes on In1/In2.Cu are correct)
    - [ ] **Flight Engineer PCB — remaining layout tasks (BLOCKS fabrication):**
        - [ ] Manually place in KiCad: CM_ESC1–4 (INA226 shunt caps), C_DEC1–4 (ESC decoupling), Section F
                    (BQ76930, J_BAL, R_BAL1–6, C_CAP, J_NTC, C_NTC) — area x=62–88, y=50–65 recommended
        - [ ] Manually place: J_SHLD_5V, J_SHLD_6V, J_SHLD_I2C, J_SHLD_ALERT chassis shield lugs

        - [ ] Route all traces; verify 4 oz Cu pour on VBAT/PGND power planes (In2.Cu / In1.Cu)
        - [ ] Add BQ76930 thermal pad (TSSOP-30 PowerPAD) to footprint — currently missing from gen_flight_engineer_pcb.py
        - [ ] Verify XT30 connectors (J_ESC1–4) courtyard clears board edge on left side
        - [ ] Verify size and weight: PCB target ≤ 90×65 mm, ≤ 0.110 lbm (≤ 50 g)

- [ ] **Update REVN_BUILD_GUIDE_24IN.md Phase 1** to include Flight Engineer + battery tray installation
    in the pre-foam-pour checklist. Battery tray and hatch must be installed and hatch zone
    masked before the foam pour step.

#### 1.4.6 ferromagnetic structural elements — magnetic-sensor siting

The rotating tilt-spar (`SPAR-TILT-4130`, and its `17-4 PH` alternative) is
**ferromagnetic steel** — a departure from the otherwise non-ferrous airframe
(CF-PETG / PETG / carbon-fiber / aluminum). Two magnetic-interference concerns
follow from putting a magnetic material into a rotating, servo-driven joint, plus
the servo's own motor and the F688ZZ steel bearings. Captured here so it is not
re-discovered at bring-up. Material selection rationale: docs/TILT_SPAR_ANALYSIS.md
§3.5 (a non-magnetic **Ti-6Al-4V** or **316** spar would remove this entirely but
loses on keyability/fatigue — see the trade study).

- [ ] **Hall tilt-encoder ↔ ferrous spar (`HALL-TILT-ENC`).** The joint angle
    encoder's bias magnet (`HALL-RING-MAG`) is a diametric ring **around the steel
    spar**, which distorts/short-circuits its field. Mitigations already in the
    geometry (docs §3.5; airframe §1.1.3.6): (a) ring ID stood ≥1 mm off the steel
    on the non-ferrous `PRINT-HALL-HUB`; (b) **non-ferrous fasteners only**
    (`HALL-SCR-M2-BRASS`, brass/316/nylon) within the ~10 mm IC keep-out — **NOT**
    the steel bearing screws; (c) keep the ring ≥3 mm clear of the F688ZZ shield.
    **VERIFY by bench-cal** with the real steel spar + bearing installed:
    monotonic, repeatable angle over the −5..90° sweep after firmware zero-cal.
- [ ] **Flight magnetometer / compass siting.** A rotating ferromagnetic shaft +
    its tilt-servo motor is a **variable hard/soft-iron disturbance** whose signature
    changes with tilt angle — the worst case for a compass. **Site the flight
    magnetometer as far as practical from both nacelle joints and the cargo-bay
    tilt servo/root bearing**, and record the tilt-dependent offset for
    compensation if a magnetometer is in the nav solution. (Confirm whether the
    Rev S1 IMU stack even includes a magnetometer — if heading is GPS/RTK-derived,
    this reduces to the encoder concern above only.)
- [ ] **Add the ferrous-spar note to the build guide** so the non-ferrous-fastener
    keep-out and magnetometer-siting rules survive into assembly.

---

