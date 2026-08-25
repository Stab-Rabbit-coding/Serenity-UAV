# Serenity UAV — TODO (Open Work Only)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0  
**Last updated:** 2026-08-01

> **This file lists only currently-open (unchecked) tasks — one line each,
> <=70 chars, no prose — for a fast "what's actually left" view.** Every
> item here also appears in [`WBS.md`](WBS.md), which is the full historical
> record (done + open, for project-progression tracking) and the index into
> each subsystem's own `WBS.md` for full task detail. When an item is
> completed: check it off in the subsystem `WBS.md` first, then delete the
> line here (it stays checked, in context, over in `WBS.md`).

---

## 0.0 — Standards Vetting and Regulatory Compliance

### 0.1 — FCC Part 95 Section Number Verification

→ detail: `docs/WBS.md` §0.1

*(All items completed 2026-07-18)*

### 0.7 — CI Lint Scope and Repo-Wide Lint Debt

→ detail: `docs/WBS.md` §0.7

### 0.8 — Tilt-Spar Material Allowables + Hall Encoder Verification

→ detail: `docs/WBS.md` §0.8

- [ ] Verify 4130 / 17-4 PH / 7075 allowables vs MMPDS/AMS (REF-MAT-*)
- [ ] Add 4130 corrosion-finish spec (zinc/cad plate) to BOM/build guide
- [ ] Verify AK7455 off-axis geometry + pinout vs datasheet (REF-SENSOR-*)
- [ ] ASTM D3039/D695 coupon test: CF-PLATE-2MM bending allowable (thwarts
      built at FOS 8.5/8.7 vs the conservative 300 MPa stand-in only)

### 0.10 Update and correct documentation touching every non-archived file.

→ detail: `docs/WBS.md` §0.10

*(Renumbered 2026-08-01 from a colliding "0.6" — root `WBS.md` §0.6 was already the distinct,
completed "IEC 62368-1 PCB Layout Isolation Verification" item, so the old label here was not
a valid cross-reference. Renumbered in both files, and moved after §0.9 here for ascending
numeric order.)*

#### 0.10.1 Systems

→ detail: `docs/WBS.md` §0.10.1

- [ ] Verify and update airframe specifications vs as built for each component.
- [ ] Verify avionics specifications vs as- built.
- [ ] Verify and update all assessment and engineering documents.
- [ ] Verify and update all software, firmware, and scripts, along with their documentation.

#### 0.10.2 Documentation

→ detail: `docs/WBS.md` §0.10.2

- [ ] Verify and update the system specification files and BOM.
- [ ] Verify and update the WBS and TODO files.

#### 1.1.0 — Hull-Frame Coordinate Standardisation (R1)

→ detail: `airframe/WBS.md` §1.1.0

- [ ] Hull-frame placements for VERIFY parts

#### 1.1.1 — Fuselage

→ detail: `airframe/fuselage-joints/WBS.md` §1.1.1 (1/3)

- [ ] User FreeCAD fine-tune (fractional mm) for all component placements
- [ ] PMMA window spec finalised (optical & structural requirements)
- [ ] Procure PMMA discs per final specification
- [ ] Add standards REF-IDs to bow_sensor_pod.scad (firmware interface)
- [ ] Middle section inner neck — Phase 5-10 print guidance
- [ ] Deprecate SCAD fuselage shell files (post-Rev S archive)

#### 1.1.1 — Fuselage (continued)

→ detail: `airframe/fuselage-covers/WBS.md` §1.1.1 (2/3)

*No open items. MESH-01 closed 2026-08-23 — all four shells verify watertight.*

#### 1.1.1 — Fuselage (continued)

→ detail: `airframe/fuselage-mid/WBS.md` §1.1.1 (3/3)

- [ ] CARGO-03c follow-up: coupon-test CF-PETG fusion/bearing (>=15MPa unlocks
      the `enlarged_tenon` alternative) — the default two-rod tie-rod couple
      is BUILT and does not block on this (`airframe/fuselage-mid/WBS.md`
      §1.1.1.2 CARGO-03c, 2026-08-24)
- [ ] head_shell24.stl
- [ ] cargo_sect_shell24.stl
- [ ] Cargo gondola shell
- [ ] Clamshell door halves
- [ ] `cargo_sect_shell24.scad` — shuttle exterior fairing profiles on Z walls
- [ ] Avionics dorsal access covers / Faraday tray lids (Inara & River)
- [ ] Update REVN_BUILD_GUIDE_24IN.md bay layout table
- [ ] Regenerate cargo_sect_shell24.stl
- [ ] Add DRV8833-tray boss locations to cargo_sect_shell24.scad
- [ ] Add SG90 bell-crank boss to inner face of each door panel
- [ ] ★ Bench-verify SPT5425LV stall current + pin-removal procedure (was: STS3215 datasheet gate)
- [ ] ★ Winch containment: 5 positive fixes (spool = projectile)
- [ ] Verify Part 107 dropped-object section number
- [ ] Containment checks on assembly + pre-flight cards
- [ ] ★ Shed threshold vs maneuver envelope (2.0g = 0.98x)
- [ ] Calibrate T_slip 0.060 N·m at the spool hub collar
- [ ] Set servo torque ceiling below T_slip (wear protection)
- [ ] Servo mode: continuous rotation by construction (pin removed); confirm LibreServo v2 protocol commands
- [ ] Mark winch spool a consumable (wear item + spare)
- [ ] AK7455 spool encoder on gateway J_ENC (spec §3.7.3)
- [ ] Implement the six Rev S winch STLs
- [ ] Winch pedestal M3 boss stations in cargo_sect_shell24.scad
- [ ] RS-485 differential bus wiring for LibreServo v2 (was: half-duplex TTL on FLEX_TTL_GPIO)
- [ ] Catch solenoid drive (AO3400 + pull-down + SS34)
- [ ] Bench-calibrate ratchet slip to 8.0 N ± 1.0 N
- [ ] Line-shed test (inboard end must NOT be anchored)
- [ ] Winch state machine firmware (Simon + gateway)
- [ ] Re-run winch mass/CG once SPT5425LV+LibreServo v2 mass is bench-weighed
- [ ] Slicer verification
- [ ] Flight Engineer's room — PDB mounting in inner neck
- [ ] CF skid rod channels
- [ ] Simon bay — define avionics bay in the MIDDLE section (moved he…
- [ ] Flight Engineer room — PDB + battery bay, middle VENTRAL (2026-06-13).
- [ ] Avionics-bay interior name marks (DEFERRED, 2026-06-13).
- [ ] Phase 11 — aft EDF intake scoop cuts
- [ ] neck_intake_frame.stl (Phase 11)
- [ ] aft_edf_plenum.stl
- [ ] Mount ant-collision strobe on belly of middle section in accord…
- [ ] Mount ant-collision steady white tail light on upper pod of rea…

#### 1.1.2 — Wings

→ detail: `airframe/wings-nacelles/WBS.md` §1.1.2

#### 1.1.3 — Nacelles
→ detail: `airframe/wings-nacelles/WBS.md` §1.1.3

- [ ] Reconcile crazy-ivan/PR#141 as SUPERSEDED by fix/nozzle branch
- [ ] Merge cargo_spar_drive into cargo shell (bearing/servo/mortise…
- [ ] Verify stbd cargo-chunk placement of spar-drive features
- [ ] Tune servo→spar horn/pushrod linkage throw (−5°..140°)
- [ ] Repair pre-existing stator sleeve non-manifold (edf_stator_sleeve)
- [ ] VERIFY INBOARD_FACE_X sign in _export_pivot_slab.scad
- [ ] Migrate nacelle_hall_ring_hub → nacelle_pod_50mm_tandem.scad + re-bake
- [ ] Bench-cal AK7455 with steel spar/MF128 bearing (ferrous-field check)
    (2026-07-19).** CG_Z = 111.5 mm (was 104.5); `PIVOT_Z` propagated to all
    SCAD/assembly/docs; nacelle shells + stator sleeve re-rendered/re-baked (66
    STLs pass validate_stls). Drivers: 40 mm flaps + discrete Ø71 housing aft.
- [ ] VERIFY Rev T CG (first-pass, band ≈109–112 mm)
    printed densities (CF-PETG 1.05 / PETG 1.00 g/cm³) against printer-sliced
    masses, and the discrete-housing vs cowl-skin overlap. → pod header table.
- [ ] Re-solve single-straight-spar alignment for +7 mm pivot move
    In the hull-frame bake the spar line slides ~7 mm aft in Y; re-derive the
    nacelle bake translation (or the cargo/wing spar Y-station) so one straight
    spar still passes through the CG pivot. `port_tilt_spar_assembly.scad` NAC_D
    is now DERIVED from `PIVOT_ZLOC` (slide-fwd-to-Y15, user 2026-07-19) so the
    overlay stays consistent; the baked nacelle STL still needs re-baking to the
    Rev T CG pivot (its old boss is ~7 mm fwd of the new pivot).
- [ ] Nozzle drive: replace invalid spar-crank w/ wing-referenced sync…
    gear + geared bellcrank (2026-07-19).** The Rev T crank clamps the spar, which
    is KEYED to the nacelle → shares the ring's rotating frame → zero relative
    motion → no actuation. Adopted hybrid (user; docs/NOZZLE_DRIVE_TRADE.md
    "DECISION AMENDMENT"): wing-fixed sun gear coaxial with the spar + nacelle
    pinion (1:1) → geared bellcrank → Rev T cam-only-ring pushrod. Modelled in
    `port_tilt_spar_assembly.scad` §6. SUB-TASKS:
    - [ ] Reconcile the wing fixed R22 sector (`wings_s1223_revo.scad`) to the
        chosen 1:1 sun (module, teeth, pitch radius; keep bolt circle vs bearing).
    - [ ] Rework `nacelle_nozzle_pushrod.scad`: seat the crank on the pinion, add
        the pinion + bellcrank; delete the spar-crank clamp.
    - [ ] Relocate the iris unison-ring lever ear 22.5°→157.5° (inboard flap gap)
        so the pushrod hugs the inboard cheek instead of crossing the duct.
    - [ ] Motion study: 1:1-mesh + crank/pushrod transmission angle, monotonic
        0..90° tilt → 0..23.9° ring; verify joint-gap width vs. the coaxial
        bearing + sun-gear + Hall-magnet/AK7455 stack.
- [x] Fix iris asm flap sign (nacelle_nozzle_iris.scad) — 8-flap loop…
    used `rotate([0, PHI_CLOSED, 0])` → petals DIVERGE at "closed"; must be
    `−PHI_CLOSED` to converge to 75 % bore. Preview-only (print parts unaffected).
    **RESOLVED 2026-07-20** (sign-bug fix in the asm loop); the loop now reads
    `rotate([0, −FLAP_PHI, 0])` after the Rev T3 parameterisation.
- [x] Iris flap shingle (Rev T3, 2026-08-09) — the documented 5° inter-flap…
    overlap was a solid INTERPENETRATION: all 8 flaps sat in one radial band, so
    adjacent flaps shared coincident surfaces (17/12 non-manifold edges) and CI
    "STL Validation" failed. Alternate flaps are now SEAL flaps lapped
    `FLAP_SHINGLE_GAP` 0.2 mm (0.008 in) outboard of the MASTER flaps
    [REF-CAD-005]. Masters unchanged → `exit_r(φ)` and the 75 %/105 % bore
    targets unaffected. Print split 8 → 4 master + 4 seal per nozzle; the
    abandoned `-closed-5deg.stl` shingling attempt was discarded (user).
    → detail: `airframe/wings-nacelles/WBS.md` §1.1.3.1. SUB-TASKS:
    - [ ] VERIFY mass/CG: flap set 32.0 → 56.8 g (+24.8 g / +0.87 oz total,
        +12.4 g / +0.44 oz per nacelle), all aft/outboard of the tilt pivot —
        re-check the Rev T CG band (≈109–112 mm) and tilt-servo torque margin.
    - [ ] VERIFY the 0.2 mm seal step against the "smooth, low-turbulence exit"
        goal by bench/CFD; fall back to a scarfed seal if the step is material.
    - [ ] Rewrite `docs/PHASED_BUILD_GUIDE.md` §7 for Rev T — it still describes
        the deleted sector/bevel/crown gear chain and a third fuselage nozzle
        (current drive is a pushrod/bellcrank to one ring lever; 2 nozzles).
    - [x] Harden `tools/precommit_index.py`: `collect_files()` indexed every
        root-level loose FILE, and inside a git worktree `.git` IS a file, so a
        regeneration from a worktree re-injected a bare `.git` entry (the artifact
        removed in 48eae05; it recurred via the `.githooks` pre-commit hook on
        2026-08-08). **RESOLVED 2026-08-09** — `collect_files()` now filters the
        walk through `git_tracked_paths()` (`git ls-files`), so the index is a
        deterministic function of the COMMIT rather than the working directory.
        Kills both failure modes at once: the worktree `.git` entry (git never
        lists it in any checkout topology) and untracked local artifacts leaking
        in (154 of them — KiCad `*-backups/*.zip`, `~*.lck`, `fp-info-cache`,
        sliced gcode, `*.FCStd` — which CI's fresh clone never had, the actual
        cause of the "random" index-sync failures). Falls back to the plain walk
        when git cannot answer (source tarball). Verified output-neutral: a clean
        worktree regenerates byte-identically, and planted untracked strays are
        excluded. The pre-commit hook is now safe to run anywhere, so `--no-verify`
        is no longer needed when committing index changes from a worktree.
    - [x] DevSkim `DS176209` false positives on the generated indexes —
        **RESOLVED 2026-08-09**: excluded the three generated artifacts by PATH via
        `ignore-globs` in `.github/workflows/devskim.yml` rather than disabling the
        rule repo-wide, so leftover-TODO detection stays active in real source. The
        alerts flagged the substring "TODO" inside indexed *filenames*
        (`tools/TODO.md`) and document titles, which cannot be reworded because the
        files are generator output asserted byte-equal by CI (PR #180, alerts
        942/945).
    - [ ] **[OPEN — needs a credential decision]** Auto-commit a stale index from
        CI instead of failing. Drafted and deliberately NOT shipped: the push would
        use `GITHUB_TOKEN`, and GitHub does not trigger workflow runs for
        `GITHUB_TOKEN` pushes, so the corrected head commit would arrive without the
        ruleset's required checks ("Python lint", "STL Validation") and the PR would
        be unmergeable — worse than a clear failure. Needs a PAT or GitHub App token
        in repository secrets to do safely. Meanwhile the determinism fix above
        removes the failure class that actually kept firing, and the job now prints
        a one-command fix plus uploads the corrected files as an artifact.
- [ ] Stator spar crossing (Rev T2): 11 vanes, coprime w/ 12-blade rotor
    rotor — Tyler–Sofrin); spar carried in a streamlined teardrop strut (tail
    aft, TE ≈ vane TE) + 0° anti-rotation key drilled through. VERIFY strut
    chord/tail + residual swirl into EDF2 by CFD/bench before flight.
- [ ] Ø72 nozzle-pocket eats the aft cowl tail…
    end at duct Z≈172.2 mm (was 185.2) — the straight Ø72 pocket over-cuts the
    tapering dome tail (172–185), so the nozzle housing becomes the aft surface.
    Decide: taper/shorten the pocket to preserve the silhouette, or accept the
    housing as the aft OML. (`NOZZLE_RING_OD`; the long-standing "shell bake
    needs review" note.)

→ detail: `airframe/wings-nacelles/WBS.md` §1.1.3

- [ ] [OPEN — DESIGN] Nozzle drive protrudes ~10 mm past the nacelle…

#### 1.1.4 — Landing Gear

→ detail: `airframe/landing-gear/WBS.md` §1.1.4

- [ ] LG-15 Procure both wire grades/tempers; coupon test
- [ ] LG-16 Confirm ductile wire temper survives jig-forming
- [ ] LG-13 Define wire-end retention detail at bay bosses
- [ ] LG-02 Bay mounting integration: backing plates, flank conform…
- [ ] Assess foot grip on concrete/asphalt
- [ ] LG-03 CF rod channel in middle_canonical_shell24.scad rear skid…
- [ ] LG-06 Elastic bench check: quarter-AUW fixture, 1.5 ft drop
- [ ] LG-07 Confirm avionics enclosure shock rating
- [ ] LG-11 Coupon-test CF-PETG
- [ ] LG-14 Instrumented drop test (load cell + high-speed video) at…
- [ ] LG-18 Mass-reduction pass (leg frame / bay / thigh)
- [ ] LG-19 Styling refinement pass vs REF-CAD-002 (cosmetic)
- [ ] Reconcile the remaining-parts list
- [ ] Combine all airframe STLs
- [ ] Render overview SVGs using FreeCAD TechDraw
- [ ] Exploded view SVG — printed parts only
- [ ] Exploded view SVG — full build

#### 1.1.5 — Non-Printable Component Placeholders

→ detail: `airframe/WBS.md` §1.1.5

- [ ] Rear skid reinforcement — SCAD update (TWO files)
- [ ] Run FreeCAD catalog
- [ ] Hull-frame placement pass
- [ ] Add Phase-11 (deferred) items to catalog
- [ ] Mesh watertightness audit
- [ ] FAR-FT-PANEL PCB design
- [ ] Link placeholders to BOM entries

### 1.2b — PCB Redesigns: Commo Rev S1 / XO Rev S1 / Flight Engineer Rev S1

→ detail: `avionics/rev-s1/WBS.md` §1.2b

- [ ] Commo Rev S1 — add LoRa, replace JST with P1+P2 socket rails
- [ ] XO (Cape-B-2) Rev S1 — remove LoRa, add P1+P2 passthrough rails
- [ ] Flight Engineer Rev S1 — remove 6 V BEC, add 5 V servo output

### 1.2c — PCB Design: Observer (Nose/Cargo-Bay Vision, ToF & Laser)

→ detail: `avionics/observer/WBS.md` §1.2c

- [ ] Final component placement (user-reserved) + impedance-controlle…
- [ ] Generate production-ready Gerber files to avionics/kicad/Observer/…
- [ ] Flag stale laser bore dimensions:
- [ ] Add cargo_tof_cut() and cargo_laser_cut() cutter modules
- [ ] Local sensor harness (both sites):
- [ ] External ring harness — nose:
- [ ] External ring harness — cargo:
- [ ] Flight Engineer second 5 V rail — cross-tied, mutually fault-tolerant…
- [ ] Observer 5 V harness:
- [ ] Laser — unify to a single 520 nm green source, Class 2 both sit…
- [ ] Both Class 2 caps must be hardware-enforced
- [ ] Nose camera strobe + frame-difference detection
- [ ] Do not source

### 1.2d — Trust-Module MCU/TPM Retarget (MSPM0G351x-Q1 + SLB 9672)

Applied 2026-08-03 by `avionics/kicad/retarget_mspm0g351x_slb9672.py` (schematics) and
`avionics/kicad/retarget_pcb_footprints.py` (PCBs).  Parts per REF-SENSOR-017 and REF-SEC-002.

| Board | MCU | Package | TPM |
|---|---|---|---|
| Observer (observer) | `M0G3519QRGZRQ1` | 48-pin RGZ VQFN 7×7 | `SLB 9672AU2.0` |
| `CAN-PERIPH-GW-1` (gateway) | `M0G3518QRHBRQ1` | 32-pin RHB VQFN 5×5 | `SLB 9672AU2.0` |
| FlightEngineer (flight engineer) | `M0G3518QRHBRQ1` | 32-pin RHB VQFN 5×5 | `SLB 9672AU2.0` |

- [x] Verify the MSPM0G351x-Q1 RGZ-48 pin map against the MSPM0G350x it replaces —
      identical for all 48 pads plus the exposed pad (SLASFA6B Fig 6-5 vs SLASEX6C Fig 6-4).
- [x] Re-pinmux the gateway and FlightEngineer onto RHB-32, which bonds out PA0–PA27 only and has
      no PBx ports: RS485_TX→PA8 (UART1_TX PF2), RS485_RX→PA9 (UART1_RX PF2),
      RS485_DE→PA21, RS485_FLT_N→PA22, CANFD_FLT_N→PA23 (FlightEngineer),
      FLEX_PWM_IO→PA25 (TIMA0_C3 PF5), FLEX_BSHOT_IO→PA26 (TIMG8_C0 PF4).
- [x] Swap and re-anchor the PCB footprints on the gateway (U1_1/U1_2) and Observer (U3).
- [x] Tie the TPM exposed pad to GND on all three boards — the SLB9670 symbol omitted pad 33
      entirely, so it was floating (Infineon SLB9672 datasheet rev 1.3 §2.1.2 requires it).
- [x] Correct the MCU land pattern: the design used
      `QFN-48-1EP_7x7mm_P0.5mm_EP5.15x5.15mm`, which KiCad's own `descr` identifies as an
      **Analog Devices LTC legacy** outline. TI's RGZ0048F exposed pad is 4.1 mm square, so
      the old land overhung the package thermal pad by 0.525 mm per side.
- [x] Separate FlightEngineer's overlapping `U_MCU` / `U_TPM` symbols (17 pads shared a coordinate,
      shorting the SPI bus and tying MCU VCORE to TPM GND); `U_TPM` moved +34.29 mm.

**Open — blocks fabrication:**

- [ ] **Re-route the gateway MCU area.** U1_1/U1_2 went from 48 pads at 7×7 mm to 32 pads at
      5×5 mm, so every trace into them is dangling. Needs a manual placement/routing pass and
      a DRC sign-off before gerbers.
- [ ] **Confirm MSPM0G351x-Q1 errata and TRM applicability.** SLAZ742G covers MSPM0G3x0x /
      G1x0x / G3x0x-Q1 and does not enumerate MSPM0G3518/3519; SLAU846E contains no
      occurrence of either part number. Obtain the correct errata/TRM for MSPM0G351x-Q1
      before firmware sign-off (REF-SENSOR-018 "requires verification").
- [ ] **Update firmware pinmux constants for the new family.** CAN moves from
      `CAN_TX`/`CAN_RX` PF5/PF6 to `CAN0_TX`/`CAN0_RX` **PF12**; PA15 offers `SPI1_CS2`
      (PF3) rather than `SPI1_CS0`; PB15/PB16 offered UART2 on the old part and UART7 on the
      new one (moot on the 32-pin boards, which now use UART1 on PA8/PA9). See §4.6.2.
- [ ] **Add the missing MCU support parts per SLAAE76E Table 1-1.** No board has the
      10 µF bulk C(VDD) local to the MCU (the gateway shares one 22 µF at the regulator and
      FlightEngineer's MCU has no local 100 nF at all), and none has the recommended NRST network —
      all three use a 10 kΩ pull-up with no 10 nF pull-down capacitor against the
      recommended 47 kΩ + 10 nF.
- [ ] **Add a pull-up on the gateway's PA0/PA1 FLEX UART.** PA0/PA1 are 5 V-tolerant
      open-drain on this family with no internal pull-up available, so `FLEX_UART_TX` cannot
      drive high without an external pull-up (SLASFA6B §9.1.1; SLAAE76E §8.5).
- [ ] **Pull PA18 down on the gateway and Observer.** PA18 is the default BSL invoke pin and is
      used as SPI MOSI on both boards; it floats during reset, so the part can enter BSL
      (SLAAE76E Table 1-1).
- [ ] **Add thermal vias under the MCU exposed pad.** Only gateway U1_1 has any (3);
      U1_2 and Observer U3 have none. TI requires the pad be soldered to a board thermal pad
      and recommends the 3×3 via pattern in the land-pattern drawing.
- [ ] **Resolve FlightEngineer's ground-net naming.** FlightEngineer's board ground carries the name
      `CM2_OUT_N` (108 nodes, including every MCU/TPM ground pin), i.e. a current-monitor
      output label is shorted into, or mis-merged with, `PGND`. Pre-existing; not introduced
      by this retarget.
- [ ] **Clean up FlightEngineer's dangling no-connect flags.** The retarget left ~30 `no_connect`
      markers that no longer sit on a pin (ERC warnings only; error count is unchanged at 0).
- [ ] **Close the Observer sch↔pcb parity gap.** `RS485_DE`, `RS485_TX` and `RS485_RX` exist on
      U3 in the schematic but not in the PCB net table; those pads were left unconnected
      rather than inventing net entries.
- [ ] **Place gateway lanes 3 and 4.** `U1_3`/`U1_4` and `U2_3`/`U2_4` exist in the
      schematic but are not on the PCB, so only two of the four tiled lanes were retargeted
      on the board.
- [ ] **Decide whether Emma, Wash and Zoë follow to the SLB 9672.** They still carry the
      SLB9670; this retarget deliberately did not touch them.

### 1.2a — PCB Design: Pilot, XO, and Commo (EMI-Hardened Variants)

→ detail: `avionics/WBS.md` §1.2a

- [ ] Reconcile Pilot.md §14 field-connector table with the actual P…
- [ ] Wire the MIL-1553 connector + transformer.
- [ ] Redesign the tamper mesh as a per-domain anti-tamper mesh (all…
- [ ] Carry the tamper signal over the link for the TPM-less boards.
- [ ] Route the rearranged capes.
- [ ] Clear residual DRC after mesh + routing
- [ ] Finish Pilot PCB (CAPE-A-2) close-out pass:
- [ ] Add SBUS/UART DIP switch to Pilot
- [ ] Generate Pilot gerbers
- [ ] Generate XO gerbers
- [ ] Zigbee RF chain was never actually added to XO — PCB scope g…
- [ ] FCC Part 15 §15.235 pre-compliance checklist for Commo
- [ ] EMI isolation validation checklist
- [ ] Merge claude/cape-em-harsh-variants-9Yfr1 → master
- [ ] Design Faraday cages / boxes to protect all PCBs
- [ ] Specify / implement tightly twisted pair bonded shielded wiring…

→ Fleet trust module (2026-07-26), see `avionics/TODO.md` "Fleet Trust Module and Tilt Encoder": Pilot PB2-P2 unwired-header finding, Pilot/XO/FlightEngineer/Observer DRC clean-out, CAN-PERIPH-GW-1 N=4 routing all still open.

### 1.4 — EMI Hardening Beyond the PCBs (500 W/m^2 environment)

→ detail: `avionics/emi-hardening/WBS.md` §1.4

- [ ] PB2-I + Pilot Enclosure
- [ ] PB2-I + XO Enclosure
- [ ] CAN FD
- [ ] RS-485
- [ ] MIL-STD-1553B
- [ ] Ethernet
- [ ] UART
- [ ] I2C
- [ ] BDSHOT/DSHOT (ESC telemetry)
- [ ] PWM
- [ ] Add FlightEngineer/battery boss pattern to middle_canonical_shell24.sca…
- [ ] Add ventral battery-swap hatch cut to middle_canonical_shell24.…
- [ ] Create flight_engineer_battery_tray.scad.
- [ ] Create flight_engineer_pdb_tray.scad.
- [ ] Update REVN_BUILD_GUIDE_24IN.md Phase 1

### 1.5 — Documentation

→ detail: `docs/WBS.md` §1.5

- [ ] Update PHASED_BUILD_GUIDE.md
- [ ] 1.5.6 Rebuild Graphical Buiild Guide
- [ ] Sync bom_revO.json ↔ bom_revO.csv

### Phase0 — Print All Parts + CF Cuts

→ detail: `graphical-build-guide/WBS.md` §Phase0

- [ ] Install hardened-steel nozzle (CF-PETG abrades brass)
- [ ] Calibrate E-steps and Pressure Advance for each filament
- [ ] Dry all filament 6 h at 65°C before printing
- [ ] Nacelle bore caliper: 55.0–56.0 mm ID at Z=10 mm and Z=80 mm
- [ ] Stator fins visible in Z=53–95 mm gap (between the two EDF seat…
- [ ] Hub bore clear at stator: 16 mm ID minimum (motor leads)
- [ ] Sector gear ↔ pinion dry-mesh: 0.1–0.2 mm backlash
- [ ] Unison ring gear seats flush in the throat housing; the 8 flaps…
- [ ] 4mm CF pivot rod slides through pivot housing with MF104ZZ bear…
- [ ] All access panel lids flush ±0.2 mm in frames
- [ ] Keel dry-fits through all hull sections without force
- [ ] Rear neck shell scoop windows covered with removable 3mm PETG b…

### Phase1 — Hull Structure + All Future Provisions

→ detail: `graphical-build-guide/WBS.md` §Phase1

- [ ] Epoxy keel through all hull sections; cure 2h. Datum marks at 9…
- [ ] Bond ring frames at all 5 station notches; cure 1h.
- [ ] Bond access panel frames A–F into hull sections (5-min epoxy, 3…
- [ ] Install M2.5 nylon standoffs in bays A, B, C, D (floor 6mm + in…
- [ ] Bond wing spar pocket inserts at wing root stations, both sides.
- [ ] Bond tilt servo mount brackets at wing root bay interior (one p…
- [ ] Install M3 heat-set inserts ×4 at belly cargo hard-point locati…
- [ ] Install SMA bulkheads: belly port (SiK 915MHz, X≈260mm), belly…
- [ ] Install 49 MHz (Part 15 §15.235) forward wire post (dorsal, X≈1…
- [ ] temporary
- [ ] String 49MHz top wire (0.3mm SS wire or 22AWG enamelled Cu) fro…
- [ ] Install 12× VL53L5CX flush-mount PETG frames (6.5mm hull cutout…
- [ ] Feed 8× PTFE conduits nose-to-tail; thread pull strings through…
- [ ] Install EPS void formers (waxed 2×) in bays A–E; verify pull st…
- [ ] Full dry-fit: all 8 pull strings accessible, standoffs clear, v…
- [ ] Do NOT foam nacelle bays, pivot housing, or access panel bays.
- [ ] Remove EPS void formers; IPA wipe bay walls; verify foam not in…
- [ ] Bond cockpit cap (verify cockpit bay wires and GPS coax accessi…
- [ ] Hull rigid — no flex when held at nose and tail
- [ ] All 8 pull strings accessible at both ends
- [ ] All standoffs in place; screws start freely
- [ ] Foam not in nacelle mounting bay, pivot housing, or panel bays
- [ ] All 6 access panel lids flush ±0.2 mm; latches/magnets engage

### Phase2 — Nacelle Assembly

→ detail: `graphical-build-guide/WBS.md` §Phase2

- [ ] Test EDF rotation direction on bench before installation: port…
- [ ] Install EDF2 (aft/downstream) from nozzle end; seat at Z=5mm sh…
- [ ] Install EDF1 (fore/upstream) from intake end; seat at Z=76mm; v…
- [ ] ESC pair: route to fuselage bay via spar conduit (ESC heat must…
- [ ] Cure 2h before proceeding.
- [ ] Repeat for stbd nacelle (opposite rotation direction).
- [ ] Press nacelle_nozzle_ring.stl onto nozzle exit face; confirm fl…
- [ ] Install nozzle inner ring (rack, R=28mm) inside base ring.
- [ ] Press a 2mm×4mm follower pin (PIN-2X4) into each of the 8 flaps…
- [ ] Hinge the 8 flaps to the throat housing on 3mm×18mm tangential…
- [ ] Dry-test: manually rotate the unison ring — flaps sweep smoothl…
- [ ] Mount sector gear to tilt bracket (FIXED — does not rotate with…
- [ ] Mount drive pinion on nacelle outer shell at pivot axis; mesh w…
- [ ] Install bevel gear pair in nacelle body (nacelle-axis → longitu…
- [ ] Thread 2mm steel longitudinal shaft through nacelle wall channe…
- [ ] Mount crown pinion on shaft at nozzle end; mesh with Idler-In o…
- [ ] Mount idler gear on its bracket to the nozzle outer housing; me…
- [ ] Full sweep test (Rev R1, 2026-06-22):
- [ ] Confirm petal closed position matches nacelle hull profile at 0…
- [ ] Port nacelle EDF rotation: CW from intake; stbd: CCW from intake
- [ ] Stator fins visible and clear in Z=53–73mm gap on each nacelle
- [ ] Nozzle iris opens/closes smoothly through full nacelle sweep
- [ ] Petal closed: hull-match at 0°; petal open: all 8 even at 90°

### Phase3 — Tilt Mechanism

→ detail: `graphical-build-guide/WBS.md` §Phase3

- [ ] Press MF104ZZ bearings into pivot housing bores (both ends); fl…
- [ ] Insert 4mm CF pivot rod through wing spar pocket + pivot housin…
- [ ] Slide nacelle pivot housing onto pivot rod; verify <0.5mm axial…
- [ ] Install tilt servos in fuselage servo mount bracket at wing roo…
- [ ] Connect pushrods (servo arm → pivot arm): servo 0° = nacelle 0°…
- [ ] Install CF-PETG hard stop blocks; bond at −5° stop and 140° sto…
- [ ] Servo calibration: set FC software travel limits at −5° and 140…
- [ ] Both nacelles rotate freely on bearings — no grinding, no wobble
- [ ] Hard stops engage at −5° and 140° (servo stalls, does not strip)
- [ ] Nozzle opens/closes correctly via gear linkage through sweep (f…
- [ ] Sector gear does NOT rotate with nacelle
- [ ] Both nacelles synchronise to within 2° at 0° and 90°

### Phase4 — Hull Foam Pour + Close-up

→ detail: `graphical-build-guide/WBS.md` §Phase4

- [ ] All PTFE conduits routed — pull strings accessible at both ends
- [ ] All bay standoffs installed
- [ ] Cargo hard points installed
- [ ] SMA bulkheads installed and dusted
- [ ] EPS void formers waxed (2 coats) and seated
- [ ] Nacelle bays and pivot housings masked OFF
- [ ] Servo mount brackets clear of foam path
- [ ] Mix X-30 per manufacturer (2:1 ratio by volume, 2-min pot life,…
- [ ] After full cure: remove EPS void formers; IPA wipe bay walls; v…
- [ ] Pull all 8 pull strings — verify still move freely.
- [ ] Install all 6 access panel lids; verify flush fit.

### Phase5 — Minimum Viable Flyer ★ FIRST FLIGHT

→ detail: `graphical-build-guide/flight-phases/WBS.md` §Phase5

- [ ] Mount XT90 PDB at keel sta 130mm; solder 14AWG main leads to ES…
- [ ] Install 2× 40A BLHeli32 ESCs in bay C (port + stbd nacelle fore…
- [ ] Phase 11 only:
- [ ] Install 5V/5A BEC; verify 5.00V ±0.05V under 1A bench load.
- [ ] Pull motor phase leads through conduit to ESCs; solder (verify…
- [ ] CAN FD termination: 120Ω SOLDERED to CN1 Cape-B at Shepherd's r…
- [ ] Mount CN1 XO on Shepherd's room (Bay A) floor standoffs (M2.5…
- [ ] Mount FC1 Pilot on inter-cape standoffs (M2.5 nylon 20mm) above…
- [ ] Flash OS to eMMC on CN1 and FC1 via USB-C before installation.
- [ ] CN1-LOG
- [ ] Seat the 49 MHz (Part 15 §15.235) sub-module on CN1 Cape-B head…
- [ ] Connect CN1 radio pigtails: SiK 915MHz → belly port SMA; LoRa →…
- [ ] Route FC1 GPS U.FL coax through cockpit-roof PTFE sleeve (sta ~…
- [ ] Daisy-chain CAN FD: 120Ω (soldered) → CN1 → FC1 → exit Shepherd…
- [ ] Daisy-chain RS-485: CN1 → FC1 → exit toward Inara's shuttle (Ba…
- [ ] Connect MIL-STD-1553: FC1 = Bus Controller (primary); CN1 = RT…
- [ ] Cap Simon's medbay (Bay D) end of ETH-EA conduit (will connect…
- [ ] Mount CN2 XO on Inara's shuttle (Bay B) floor standoffs; inser…
- [ ] Flash OS to eMMC on CN2 and FC2 before installation.
- [ ] CN2-LOG
- [ ] Seat the 49 MHz (Part 15 §15.235) sub-module on CN2 XO J_XCVR…
- [ ] Route FC2 GPS coax through dorsal PTFE sleeve (sta ~130mm); mou…
- [ ] Continue CAN FD daisy-chain Shepherd's room→Inara's shuttle: CN…
- [ ] Continue RS-485 daisy-chain Shepherd's room (Bay A) → Inara's s…
- [ ] Connect ETH-AB (Shepherd's room → Inara's shuttle): FC1 Pilot ET…
- [ ] Cap River's room (Bay C) end of ETH-BD (will connect to CN3 in…
- [ ] Power taps: connect CN1, FC1, CN2, FC2 power leads from PWR con…
- [ ] Provision TPM 2.0 (SLB9672) on CN1, FC1, CN2, FC2 — unique key…
- [ ] Verify CPLD write-blocker on CN1 and CN2: echo test > /mnt/flig…
- [ ] Configure forensic log mount in /etc/fstab (noexec, nodev, nosu…
- [ ] Flash serenity-cn Phase 6 daemon to CN1 and CN2.
- [ ] Flash serenity-fc Phase 6 stub to FC1 and FC2.
- [ ] Enable CAN FD interfaces at 1 Mbps / 8 Mbps on all 4 nodes.
- [ ] Verify 4-node CAN FD heartbeat ring: candump can0 shows frames…
- [ ] Configure MAVLink routing (mavlink-router) on elected FC master…
- [ ] Install the 49 MHz (Part 15 §15.235) daemon on CN1 and CN2 (sel…
- [ ] ESC calibration (full throttle power-on → drop to zero).
- [ ] Motor spin test (5% throttle 2s): all 5 motors spin in correct…
- [ ] Tilt servo calibration: 0° = nacelle vertical ±0.5°, 90° = hori…
- [ ] Rear nozzle servo endpoints verified.
- [ ] 190mm from nose
- [ ] GPS lock: HDOP ≤1.5 on both FC nodes; positions agree within 2m.
- [ ] Radio checks: MAVLink heartbeat in QGC (SiK + LoRa backup); 49…
- [ ] Node failover: kill FC master power → standby assumes authority…
- [ ] Tethered thrust test: 60% throttle 10s → lift exceeds AUW; ESC…
- [ ] Nav lights: 6-position ICAO cycle (RED port, GREEN stbd, WHITE…
- [ ] Apply FAA registration number
- [ ] Pre-flight ABCD checklist (Airframe, Battery, Comms, Docs)
- [ ] Tethered hover 1m AGL × 3 successful passes before free flight…
- [ ] Free hover 1m AGL (stability, ±10° authority, altitude hold ±0.…
- [ ] Free hover 3m AGL (yaw 360° both directions)
- [ ] Nacelle transition: ≥8m AGL, gradual sweep 90°→0° — altitude ho…
- [ ] Forward flight circuit: one lap ≤10m AGL, transition back to ho…
- [ ] Verify flight log written to CN1-LOG and CN2-LOG
- [ ] Stable hover 1m AGL in ≤15° headwind
- [ ] Nacelle transition without altitude excursion >1.5m
- [ ] All 4 nacelle ESCs ≤70°C at full hover power
- [ ] MAVLink telemetry live to QGC during all segments
- [ ] All 4-node CAN FD heartbeats confirmed
- [ ] Node failover: standby assumes within 100ms of master power-kill
- [ ] Flight log on both CN μSDs; CPLD write-block verified

### Phase6 — Full 8-Node Architecture + ToF Obstacle Avoidance

→ detail: `graphical-build-guide/flight-phases/WBS.md` §Phase6

- [ ] Remove temporary Phase 6 CAN FD 120Ω from FC2 Pilot in Inara's s…
- [ ] Mount CN3 XO on River's room (Bay C) floor standoffs; insert P…
- [ ] CN3-LOG
- [ ] Seat the 49 MHz (Part 15 §15.235) sub-module on CN3 XO J_XCVR…
- [ ] Route FC3 GPS coax through dorsal PTFE sleeve (sta ~275mm); mou…
- [ ] Continue CAN FD chain: Inara's shuttle (Bay B) FC2 → River's ro…
- [ ] Continue RS-485 chain Inara's shuttle (Bay B) → River's room (B…
- [ ] Connect ETH-BD (Inara's shuttle → River's room): FC2 Pilot ETH-1…
- [ ] Power tap River's room (Bay C); verify 5V ±0.05V.
- [ ] Mount CN4 XO on Simon's medbay (Bay D) standoffs; insert PB2-I…
- [ ] CN4-LOG
- [ ] Seat the 49 MHz (Part 15 §15.235) sub-module on CN4 header.
- [ ] Route FC4 GPS coax through dorsal PTFE sleeve (sta ~350mm); mou…
- [ ] 120Ω PERMANENT
- [ ] Connect ETH-DE (River's room → Simon's medbay): FC3 Cape-A ETH-…
- [ ] Connect ETH-EA ring-close (Simon's medbay → Shepherd's room): F…
- [ ] Power tap Simon's medbay (Bay D); verify 5V ±0.05V.
- [ ] TPM 2.0 on CN3, FC3, CN4, FC4 — unique key material per node.
- [ ] CPLD write-blocker verification on CN3 and CN4.
- [ ] Verify RSTP ring: bridge vlan show; disconnect one ETH cable →…
- [ ] Verify full 8-node CAN FD ring: candump can0 shows frames 0x001…
- [ ] MIL-STD-1553 final config: FC1=BC, FC2=standby BC, FC3/FC4/CN1–…
- [ ] Install 6× VL53L5CX in Array B flush-mount frames; wire to TCA9…
- [ ] Install 6× VL53L5CX in Array A flush-mount frames; wire to TCA9…
- [ ] Apply 0.5mm PMMA disc over each sensor aperture with UV adhesiv…
- [ ] Configure OA fusion in firmware: halt at 1.0m obstacle clearanc…
- [ ] GPS clearance check for 49MHz wire post proximity: bench-verify…
- [ ] All 8 CAN FD heartbeats (0x001–0x008) confirmed
- [ ] Ethernet RSTP ring heals on single-link disconnect within 1s
- [ ] MIL-STD-1553: all 8 RTs respond within 9μs
- [ ] CN3 and CN4 log μSD write-block verified
- [ ] All 12 ToF sensors return valid range at ≤4m
- [ ] OA halt test: approach wall at 0.5m/s → stops at 1.0m clearance
- [ ] Array failure mode: either FC1 or FC3 loss → remaining array pr…
- [ ] 3-waypoint autonomous mission with GPS, altitude hold, RTL on s…

### Phase7 — Cargo System

→ detail: `graphical-build-guide/flight-phases/WBS.md` §Phase7

- [ ] Bond cargo gondola shell into belly void at 4× M3 hard points (…
- [ ] Install 3mm CF door hinge pins; attach clamshell door halves (s…
- [ ] Install SPT5425LV/LibreServo v2 winch + twin-pedestal spool + ratchet; wind Dy…
- [ ] Install SG90 door-actuator servo (spring-assist open, servo pul…
- [ ] Install SG90 payload-release servo; connect to DRV8833 IN1/IN2…
- [ ] Route control leads through PWR conduit belly tap to CN master…
- [ ] Seal gondola-hull perimeter with 3M foam gasket tape.
- [ ] Configure CN master GPIO: door open/close, winch deploy/retract…
- [ ] Door open/close × 10: no binding
- [ ] Winch deploy 1.5m: straight descent, line clear
- [ ] Winch retract: auto-latch clicks and holds at top
- [ ] 250g load test: winch deploy + retract × 5; latch holds
- [ ] Hover with 250g payload: altitude-hold degradation ≤10%
- [ ] Autonomous delivery: 3-waypoint mission, deploy at waypoint 2,…

### Phase8 — Finishing

→ detail: `graphical-build-guide/flight-phases/WBS.md` §Phase8

- [ ] Replace FAA N00000 placeholder in serenity/diagrams/decal_sheet…
- [ ] Print decal sheet on waterslide decal paper; seal with clear co…
- [ ] Apply decals per build_guide_19_decal_placement.svg: Serenity l…
- [ ] Final airworthiness inspection: all fasteners, propulsion, elec…
- [ ] Documentation archive: build log (photos + test results), Cape-…
- [ ] FAA compliance final check: registration visible without moving…

### Phase9 — Performance Tuning and Flight Envelope Expansion

→ detail: `graphical-build-guide/flight-phases/WBS.md` §Phase9

- [ ] Thrust stand calibration
- [ ] PID governor tuning
- [ ] Nacelle transition tuning
- [ ] Endurance test
- [ ] Cross-wind hover
- [ ] Extended autonomous mission
- [ ] T/W measured ≥1.10 (nacelles only) on thrust stand
- [ ] Hover altitude hold ±0.15 m for 60 s
- [ ] Nacelle transition altitude excursion ≤0.5 m
- [ ] Endurance ≥8 min at hover (6S 4000mAh baseline)
- [ ] Logs on all 4 CN nodes; write-block verified

### Phase10 — Advanced Autonomy and Long-Range Operations

→ detail: `graphical-build-guide/flight-phases/WBS.md` §Phase10

- [ ] BVLOS communication validation
- [ ] Extended waypoint missions
- [ ] Payload delivery mission
- [ ] Simulated node failure during flight
- [ ] Emergency RTL validation
- [ ] Regulatory readiness review
- [ ] Mission continues on any single surviving radio link
- [ ] 10-waypoint autonomous mission completed without intervention
- [ ] Autonomous cargo delivery within 2 m of target
- [ ] Node failure: remaining FCs maintain flight ≥30 s
- [ ] RTL on link loss: lands within 3 m of takeoff point
- [ ] All regulatory documentation current and on file

### Phase11 — Aft EDF Integration (Deferred)

→ detail: `deferred/WBS.md` §Phase11

- [ ] Scoop windows must be re-sized for the 55 mm EDF (reduced area).
- [ ] Remove temporary window covers from existing neck shell, or swa…
- [ ] Regenerate
- [ ] Regenerate
- [ ] Generate
- [ ] Generate
- [ ] Run mesh watertightness verification on all regenerated STLs; r…
- [ ] Dry-fit neck_intake_frame.stl into the resized scoop windows; r…
- [ ] Verify aerodynamic orientation: intake lips face forward (−Y /…
- [ ] Apply structural epoxy to tongues + shoulder flanges; press fra…
- [ ] Fillet all gaps between flange and hull; cure 2h.
- [ ] Dry-fit aft_edf_plenum.stl; verify intake arm alignment and 55m…
- [ ] Bond plenum forward arms to intake frame exits; fillet joints;…
- [ ] Bond rcs_distribution_manifold.stl to the 4 plenum bleed taps;…
- [ ] Pressure-test: seal EDF face with tape; cover all but one scoop…
- [ ] Bench-test 55mm EDF (correct rotation, no vibration).
- [ ] Install EDF retaining ring at station ~430mm inside Panel F; bo…
- [ ] Seat EDF in plenum 55mm inlet; press forward to retaining lip;…
- [ ] Route motor leads through Panel F to 50A ESC; route signal lead…
- [ ] Install 50A ESC in Panel F bay; foam tape + cable tie. Cure 2h…
- [ ] Fixed — no moving petals.
- [ ] Install 4× rcs_thruster_nozzle.stl at their RCS stations; conne…
- [ ] Install 4× SG90-class proportional valves on rcs_valve_bracket.…
- [ ] Calibrate RCS valves: 0% = closed (no bleed); 100% = full bleed…
- [ ] Bond permanent aft 49 MHz (Part 15 §15.235) wire post to top of…
- [ ] Remove temporary aft post from station ~580mm.
- [ ] Restring 49MHz top wire (~470mm) from forward post to nozzle af…
- [ ] Enable ESC5 in FC2 firmware (PRU Ch.2); configure BDSHOT govern…
- [ ] Add the 4 RCS proportional-valve channels to the attitude-contr…
- [ ] Add rear EDF to the forward-thrust (cruise) schedule — NOT the…
- [ ] Verify all 5 ESC heartbeats on CAN FD; confirm FC2 cross-drive…
- [ ] Bench-test RCS attitude authority; then forward-flight thrust t…
- [ ] All regenerated rear-EDF STLs pass mesh watertightness verifica…
- [ ] Intake frame tongues fully seated in the resized scoop windows
- [ ] Plenum + RCS manifold pressure-test passed (draft at EDF inlet…
- [ ] EDF seated at station ~430mm, centerline ±2mm; rotation verifie…
- [ ] 50A ESC installed; ESC5 signal routed to FC2 PRU Ch.2
- [ ] Canonical nozzle bonded flush to hull outer mold line; exit 2.0…
- [ ] All 4 RCS valves calibrated; pitch/yaw authority confirmed on b…
- [ ] 49MHz aft wire post on canonical nozzle; top wire re-strung at…
- [ ] Forward-thrust test passed; rear EDF NOT used for hover lift; E…
- [ ] All 5 ESC telemetry visible on CAN FD; ESC temps ≤70°C at cruis…

### Phase12 — Cargo-bay Range-Extender Battery Module (Deferred)

→ detail: `deferred/WBS.md` §Phase12

- [ ] RBM module:
- [ ] Flight Engineer input:
- [ ] Current sharing:
- [ ] Firmware (pwr_fault):
- [ ] W&B:
- [ ] CAD:

### 4.2 — FC Node (Pilot) - Phase 7 Firmware

→ detail: `avionics/firmware/WBS.md` §4.2

- [ ] EDF ESC PID governor
- [ ] Nacelle tilt servo command generation (RS-485/LibreServo v2, was PWM)
- [ ] IMU / barometer sensor fusion
- [ ] ToF sensor array management
- [ ] u-blox M10Q GNSS integration
- [ ] MIL-STD-1553B RT implementation
- [ ] TPM-bound attestation

### 4.3 — CN Node (XO) - Phase 7 Firmware

→ detail: `avionics/firmware/WBS.md` §4.3

- [ ] CAN FD heartbeat and telemetry forwarding
- [ ] MIL-STD-1553B BC/RT tasks
- [ ] RS-485 inter-board messaging
- [ ] Ethernet RSTP ring management
- [ ] Signed-log write via CPLD write-blocker
- [ ] TPM-bound HMAC on all outbound AX.25 payloads
- [ ] Cargo control
- [ ] MAVLink routing configuration

### 4.4 — Both Nodes

→ detail: `avionics/firmware/WBS.md` §4.4

- [ ] Node role election protocol
- [ ] Autonomous navigation
- [ ] OA integration
- [ ] GPS cross-check
- [ ] Security message signing

#### 4.5.1 — Skipper Hardware Design

→ detail: `gcs/WBS.md` §4.5

- [ ] Create Skipper host computer specification
- [ ] Skipper field enclosure — print and fit-check
- [ ] Gimbal STL generation and mesh verification
- [ ] Gimbal servo wind-load torque check
- [ ] Procure Skipper comms node hardware:
- [ ] Procure antenna hardware
- [ ] Procure gimbal hardware:

#### 4.5.2 — Skipper Comms Node Setup (Phase Skipper-2)

→ detail: `gcs/WBS.md` §4.5

- [ ] Flash Debian Linux to Skipper PB2-I eMMC
- [ ] Apply Cape-B-2 device tree overlay for Skipper
- [ ] Provision TPM 2.0 (SLB9672) on Skipper's PB2-I
- [ ] Verify CPLD write-blocker on Skipper's log μSD
- [ ] Build and install Skipper PB2-I firmware:
- [ ] Install and configure mavlink-router on Skipper's PB2-I
- [ ] Enable all 5 radio interfaces on Skipper's PB2-I
- [ ] Configure Wi-Fi transmit power

#### 4.5.3 — Skipper Host PC Software Setup (Phase Skipper-3)

→ detail: `gcs/WBS.md` §4.5

- [ ] Install Debian Linux on GCS host PC
- [ ] Run installation scripts in order:
- [ ] Configure QGroundControl:
- [ ] Configure Wi-Fi Tx power on host PC
- [ ] Run tracking software tests:
- [ ] Implement gcs/skipper/firmware/pb2i/src/skipper_comms.c and skipper_com…

#### 4.5.4 — Tracking and Gimbal Integration (Phase Skipper-3)

→ detail: `gcs/WBS.md` §4.5

- [ ] Bench test gimbal hardware
- [ ] Gimbal calibration:
- [ ] Run telemetry_feed.py bench test
- [ ] Run tracker.py bench test
- [ ] Run gimbal_ctrl.py bench test
- [ ] End-to-end tracking test (outdoor):

#### 4.5.5 — Skipper Integration Testing (Phase Skipper-4)

→ detail: `gcs/WBS.md` §4.5

- [ ] Multi-link communication bench test:
- [ ] 915 MHz link margin test (open field, 1 km):
- [ ] Wi-Fi link margin test (open field, 200 m):
- [ ] 49 MHz (Part 15 §15.235) link test (1 km):
- [ ] Gimbal pointing accuracy test (outdoor, aircraft at 200–500 m):
- [ ] MAVLink authentication test:
- [ ] Node loss with Skipper active:

#### 4.6.1 — TI AM62Ax Vision Pipeline Bring-Up

→ detail: `avionics/observer/WBS.md` §4.6.1

- [ ] MIPI CSI-2 camera sensor bring-up
- [ ] VPAC/ISP pipeline configuration
- [ ] H.264/H.265 hardware encoder pipeline
- [ ] Kernel/BSP integration
- [ ] Bench test:

#### 4.6.2 — TI MSPM0G3507 Control Firmware

→ detail: `avionics/observer/WBS.md` §4.6.2

- [ ] MCAN (CAN-FD) driver bring-up
- [ ] TFmini-S UART driver
- [ ] KSZ9477 Ethernet switch management driver
- [ ] Laser GPIO driver (both sites Class 2 — docs/OBSERVER_LASER_ANALYS…
- [ ] Laser strobe + crosshair-metrology routine (AM62A7 ISP):
- [ ] SPI driver to Infineon SLB9672 TPM
- [ ] Signed telemetry:

#### 4.6.3 — Integration Testing

→ detail: `avionics/observer/WBS.md` §4.6.3

- [ ] Bench test:
- [ ] Ring failure test:
- [ ] Laser safety interlock test (nose only):

### 5.1 — FCC (external radio systems)

→ detail: `docs/WBS.md` §5.1

- [ ] XCVR-49MHZ-1/2 FCC Part 15 §15.235 compliance

### 5.2 — FAA (airworthiness and operations)

→ detail: `docs/WBS.md` §5.2

- [ ] Aircraft registration
- [ ] Remote Pilot Certificate
- [ ] Navigation lights compliance
- [ ] sUAS data plate
- [ ] Pre-flight area check
- [ ] Airspace waiver (if applicable)

### 5.3 — Industry Standards Compliance

→ detail: `docs/WBS.md` §5.3

- [ ] Structural validation
- [ ] IEEE/ISA/AUVSI best practices
- [ ] Tamper-evident logging

### 5.4 - Open Source Hardware Certification

→ detail: `docs/WBS.md` §0.9

- [ ] Submit OSHW self-certification — requires the human maintainer to act

### 6.1 — Branch Reconciliation (2026-06-09)

→ detail: `docs/WBS.md` §6.1

- [ ] Delete stale feature branches

---

*"Get on with it, Pilot." — Capt. Skipper Reynolds*
