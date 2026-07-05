# Vera — Nose/Cargo-Bay Vision, ToF & Laser Board

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**Callsign:** Vera (Jayne's rifle — "she's a good gun.")
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Revision:** — (design exploration; EMI-hardened, user-compacted pass)
**Date:** 2026-07-03
**Status:** Schematic net-correct and EMI-hardened (ERC clean of shorts); PCB footprints
placed, double-sided, corners rounded, **46×48 mm** (manually compacted in the KiCad GUI,
re-verified DRC-clean after); **traces not yet routed; NOT fabrication-ready.**

---

## Purpose

Vera is a **standalone PCB — not a PocketBeagle 2 Industrial cape.** Unlike Wash/Zoë/Emma it
does not use the P1+P2 header stack and does not mount onto a PB2-I node. It is installed at
**two physical locations** using one shared board design:

- The **bow sensor pod** (nose, `airframe/openscad/fuselage/bow_sensor_pod.scad`) —
  2"×2" (51×51 mm) laser crosshair at 50 ft (15.2 m).
- The **cargo bay nadir FPV mount** (`cargo_fpv_bezel`) —
  3"×3" (76×76 mm) laser crosshair at 5 ft (1.5 m).

It supersedes the RunCam Nano 4 analog camera (REF-SENSOR-001, superseded) originally
specified for the bow sensor pod, and fulfils the "RP2350-based Camera/TOF/laser MCU board"
task originally tracked at TODO.md §1.1.1.1a.

Vera connects to the rest of the airframe **only** via three shielded JST-GH connectors —
Ethernet ring in, Ethernet ring out, CAN-FD trunk — plus its own 5V power input. It has no
other physical or electrical dependency on any other avionics board.

**Power (added 2026-07-05):** each Vera board draws ≈ **1.2 A typ / ~2.1–2.7 A peak at 5 V**
(AM62A7 SoC + KSZ9477 switch + camera + ToF + laser; full budget in
`docs/POWER_DISTRIBUTION.md §3.2.1`). The two boards (≈ 2.4 A typ / ~4.8 A peak combined) are
fed from a **dedicated Kaylee 5 V payload rail (U_BEC_VERA → J_VERA)** — NOT the shared 5 V
avionics bus, which is already near its dual-BEC capacity — keeping the switching video-SoC
load off the avionics rail and preserving its margin. Vera's own TPS65219 PMIC regulates this
5 V input to the SoC core rails. `J_PWR` is the board-side 5 V/GND entry.

---

## Design Origin and Fact-Check

This board's architecture began as an AI-assisted (Gemini) brainstorm conversation imported
into this project on 2026-07-03. Several of the brainstorm's specific claims were fabricated
or wrong and were caught before being committed to any citation-tracked file — see
`REFERENCES.md` "Removed / Superseded Citations" for the full list:

- **"TI DM38x + remixed OpenIPC firmware"** — infeasible. TI's DaVinci DM385/DM388 are NRND
  (Not Recommended for New Designs), and OpenIPC's supported-hardware list contains no TI
  part at all, not even at R&D stage. Replaced with **TI AM62A7** (real, in-production,
  MIPI CSI-2 + 7th-gen VPAC/ISP + H.264/H.265 encode) running **TI's own open-source Linux
  BSP** (V4L2/GStreamer) — genuinely open-source, but explicitly not OpenIPC.
- **"LAN9355 / KSZ9563 for MRP ring redundancy"** — neither chip implements HSR/PRP/MRP.
  Replaced with **Microchip KSZ9477**, confirmed via Microchip's own AN3474 application note
  to hardware-offload HSR/PRP per IEC 62439-3.
- **"ST33GTPMISPI" TPM part** — does not exist. Replaced with **Infineon SLB9670**, the same
  SPI TPM 2.0 part already standardized fleet-wide on all 8 Wash/Zoë nodes.

## Architecture

### Vision half

- **U1 — TI AM62A7** (Sitara, in production). MIPI CSI-2 v1.3 camera input (1 of 4 real
  lanes modeled in this schematic pass — see "Known Gaps" below), 7th-gen VPAC/ISP, H.264
  (Level 5.2) / H.265 (Level 5.1 High-tier) hardware encode up to 4K.
- **U_PMIC — TI TPS65219** PMIC, TI's own purpose-built power solution for AM62x/AM62A
  (per TI application note SLVAFD0, "Powering the AM62x with the TPS65219 PMIC"). Feeds
  VDD_CORE, VDDSHV, VDDR from a single +5V input; +3V3 LDO output shared with the control
  half.
- Camera sensor module itself is a **separate board** mounted at the bow/cargo aperture
  (behind the bow sensor pod's 40° flat, per `bow_sensor_pod.scad`), connected to Vera via
  J_CAM1/J_CAM2 (CSI diff pair + I2C/power).

### Control half

- **U3 — TI MSPM0G3507** MCU. Native hardware MCAN (CAN-FD) peripheral — no software PIO
  synthesis needed (an RP2350-based design would have required this). Shares TI toolchain
  with the AM6254 real-time domain on Wash/Zoë. Two independent UART instances: UART0 to
  U1 (AM62A7, crossed TX↔RX), UART1 dedicated to the TFmini-S ToF sensor (no net-sharing
  between the two links).
- **U5 — Infineon SLB9670** SPI TPM 2.0 — the exact part already used fleet-wide on all 8
  Wash/Zoë nodes, reused here rather than introducing a new TPM part number.
- **U2 — Microchip KSZ9477** 7-port Ethernet switch. Port 1 (RGMII) to U1 for video egress;
  Ports 2/3 (integrated PHY, full TX+/TX-/RX+/RX- differential pairs each) feed the
  EMI-hardening chain below; SPI host interface to U3 for ToF/laser-state telemetry and
  control-plane access.
- **U4 — TI ISOW1044BDFMR** galvanically-isolated CAN-FD transceiver (SOIC-16W, 5 kV
  reinforced insulation) — replaces an earlier non-isolated TCAN1042HG-Q1 to match the
  Wash/Zoë Rev R EMI-hardening standard (see below).
- **Y1** — 25 MHz crystal for U2's reference clock.

### EMI hardening (added 2026-07-03 — see "EMI Hardening Status" below)

Matches the Wash/Zoë Rev R baseline (TODO.md §1.2a) using the SAME real, already-verified
parts and footprints from this project's own `gen_cape_a2.py`/`gen_cape_a2_pcb.py`:

- **Each Ethernet port** (ring in, ring out): KSZ9477 port → **Wurth 749010012A** SMD
  10/100BASE-TX transformer (T1/T2, real 8-pin footprint) → 2× **Bourns SRF2012-100Y**
  common-mode choke (CMC1-4, one per differential pair) → 2× **Nexperia PRTR5V0U2X** TVS
  array (D1-4, shunt to GND) → JST-GH 5-pin connector (J_ETH_IN/J_ETH_OUT — GND + 4 signal,
  matching Wash's real `JST_GH_SM05B-GHS-TB` footprint, not a fabricated 6-pin).
- **CAN-FD bus**: U4 (ISOW1044BDFMR, isolated) → **SRF2012-100Y** CMC (CMC5) → **PRTR5V0U2X**
  TVS (D5, shunt to chassis PGND) → J_CANFD.
- Each Ethernet port previously modeled only ONE differential pair (a real bug — 10/100BASE-TX
  needs both TX and RX pairs); fixed alongside adding the hardening chain.

### ToF sensor

- Benewake **TFmini-S** (REF-SENSOR-002) — unchanged from the existing bow sensor pod
  design. Read by U3 over its dedicated UART1 instance; range data republished signed over
  both the Ethernet ring and CAN-FD.

### Laser driver — single green source, location-specific optic + current limit

One shared driver circuit (Q1 AO3400 logic-level N-MOSFET, R1 100Ω gate resistor, R2 10kΩ
pulldown, J_LASER JST-SH 2P) serves both install locations. **Per `docs/VERA_LASER_ANALYSIS.md`
(Rev A, 2026-07-05), both installs now use ONE shared 520 nm green laser diode + driver**; the
two sites differ only in (1) a per-location terminal optic that sets the spread angle and (2) a
per-location hardware current limit that sets the optical power / IEC 60825-1 class. This
retires the previous split (green nose + separate 650 nm red cargo module) and unifies the
laser BOM to a single green diode family. Rationale in full: `docs/VERA_LASER_ANALYSIS.md`.

- **Spread angle is set by the terminal optic, not the source** (15× difference between sites):
  nose ≈ 0.19° (3.3 mrad) custom near-collimated crosshair/dot; cargo ≈ 2.86° (50 mrad) stock
  DOE crosshair or diverging-lens dot. Same collimated green source both places.
- **Cargo bay** (3"×3" @ 5 ft): green at 520 nm is 6.64× more luminous-efficient than the
  retired 650 nm red, so the same 5 ft visibility needs ≤ 1 mW → **Class 2** (blink-reflex
  safe; *safer* than the old red). GPIO-default-off pull-down suffices, **but the Class 2 cap
  must be HARDWARE-enforced** (fixed current limit) so no firmware fault can drive the shared
  diode to Class 3B near ground crew.
- **Nose** (2"×2" @ 50 ft): daylight visibility at 50 ft still requires **IEC 60825-1 Class
  3B** (5–500 mW) radiant power even in green. Requires the key-controlled interlock
  (LASER_KEY_IN → U3), emission indicator (LASER_IND → U3), **and a mechanical beam-stop/shutter
  (still not on the board — electronics-only interlock so far)**.
- **Do not source the green diode or either terminal optic** until a real datasheet with a
  verified mW rating and IEC 60825-1 class replaces the placeholder citation in REFERENCES.md
  (REF-IEC-002 pending item; tracked TODO.md §1.2c).

---

## PCB

**46 × 48 mm, double-sided, 4-layer FR4, rounded corners (3 mm radius, matching Wash/Kaylee
convention).**

Board-size history: the original single-sided draft was 110×190 mm — the two big placeholder
ICs (U1's BGA footprint, U2's TQFP footprint) forced that size using rough first-guess body
dimensions. Several things brought it down to the current 46×48mm:

1. **Double-siding**: U1 (AM62A7) on the front; U_PMIC/U5/U3/U2 on the back of the *same*
   board area (legal — opposite copper faces don't collide).
2. **Real component body sizes** (2026-07-03 datasheet research pass) replaced rough
   estimates — most significantly MSPM0G3507 turned out to have a real VSSOP-28 package
   option (7.1×4.9mm) far smaller than the VQFN-48 (7×7mm) first assumed, and AM62A7/KSZ9477/
   SLB9670/TPS65219 all have smaller real bodies (18×18mm, 14×14mm, 5×5mm, 5×5mm
   respectively) than the placeholder generator's original guesses.
3. **Adding the full EMI-hardening chain** (12 new small parts: 2 magnetics, 4 CMC, 4 TVS,
   plus the isolated CAN transceiver and its own CMC/TVS) grew the script-generated layout
   from an intermediate 68.5×63.5mm to 78×80mm — expanding only as required for the
   hardening components.
4. **Further manual compaction in the KiCad GUI** (component repacking, tighter spacing)
   brought it down to the current **46×48mm** — the tightest pass yet, packing all parts
   (front + back) right up against the courtyard-clearance limit.

Two rounds of manual GUI editing each introduced the same class of file corruption, both
found and fixed by chunk-removal bisection against `kicad-cli`'s "Failed to load board"
error: (1) the layer table getting rewritten with wrong layer IDs/types for B.Cu (declared
as ID 2 / type "power" instead of the fixed KiCad enum value 31 / type "signal", with
`In2.Cu` missing entirely); (2) the Edge.Cuts outline geometry becoming a non-closed,
self-intersecting shape after corner-dragging in the GUI (one arc's start point even landed
outside the board, at negative Y). Both were corrected in place — the layer table restored to
the standard values, the outline rebuilt as a clean rounded-rectangle at the compacted
46×48mm size with squared, properly-closed corners — and mounting holes were re-symmetrized
to an exact 4mm margin (4,4)/(42,4)/(4,44)/(42,44). A handful of components (J_TOF, U4) also
needed small repositioning after the resize to clear new courtyard/pad collisions.

Component placement is net-correct and DRC-clean (0 shorting_items, 0 net_conflict, 0
courtyards_overlap, 0 clearance violations, 0 solder_mask_bridge, 0 invalid_outline as of
2026-07-03, post-compaction re-verification) but **no copper traces are routed yet** — only a
GND pour zone on In1.Cu (bounds updated to 44×46mm to match). This is intentional per this
project's established PCB workflow (`avionics/CLAUDE.md`: "PCBs are tightly packed. All final
component footprint positions will be done manually, after PCBs are populated and nets are
built by script.") — the script (`gen_vera_pcb.py`) placed footprints and built nets;
subsequent manual compaction in the KiCad GUI is the "final positions done manually" step
this project's workflow anticipates. **Note:** `gen_vera_pcb.py` itself still generates the
pre-compaction 78×80mm layout — it has not been updated to match the hand-compacted 46×48mm
result, so re-running it will not reproduce the current file (see "Generator Scripts" below).

Mounting holes: 4× M3, symmetric 4 mm margin from each edge — (4,4), (42,4), (4,44), (42,44).

---

## Verified vs. Placeholder — Read Before Fabricating Anything

**Real, verified:**

- All net-level architecture/interconnect (which pin talks to which pin, UART crossing,
  CAN-FD, SPI buses, PGND/GND single-point isolation — verified via netlist export, only one
  bridge point between GND and PGND).
- TI ISOW1044BDFMR's SOIC-16W pinout (reused from Wash's own verified `gen_cape_a2.py`).
- AO3400 SOT-23 N-FET pinout.
- TPS65219 as the correct PMIC family for AM62A power (per TI's own SLVAFD0 app note),
  VQFN-32/RSM 5×5mm real body size.
- Microchip KSZ9477 as the correct part for HSR/PRP hardware redundancy (per AN3474) — NOT
  LAN9355/KSZ9563, which do not implement it. Real body size 14×14mm (128-TQFP-EP).
- AM62A7 real body size 18×18mm (484-ball FCBGA/FCCSP, AMB/ANF package).
- MSPM0G3507 real VSSOP-28 (DGS) package option, body ~7.1×4.9mm — smaller than the VQFN-48
  first assumed.
- SLB9670 real PG-VQFN-32 package, body ~5×5mm.
- Wurth 749010012A magnetics, Bourns SRF2012-100Y CMC, Nexperia PRTR5V0U2X TVS — all reused
  verbatim (pinout + footprint reference) from this project's own working Wash/Zoë generator.

**Placeholder / NOT real — must be replaced before fabrication:**

- U1 (AM62A7, 484-ball BGA), U2 (KSZ9477), U3 (MSPM0G3507), U5 (SLB9670), and U_PMIC
  (TPS65219) all use a **deliberately obvious "2-row pad" placeholder footprint** — not a
  fabricated-to-look-real BGA/QFN ball-out. Inventing a plausible-looking one with no
  datasheet to back it up would be worse than an honest placeholder. Real pin **numbers**
  for these five parts are not yet cross-checked against actual datasheets — the *signal
  names* on each net are correct, the *pin numbers* are placeholder sequences. Pad *pitch* on
  these placeholders is now tuned per-component to roughly match real proportions (e.g.
  0.65mm for U3's VSSOP-28), rather than a flat 2.54mm that would make small real packages
  look many times larger than they really are.
- The JST-GH 5-pin Ethernet connector footprint is an untuned approximation of Wash's real
  `JST_GH_SM05B-GHS-TB_1x05-1MP_P1.25mm_Horizontal` part (pin count/pitch match; exact pad
  geometry not independently re-verified).
- Only 1 of 4 real MIPI CSI-2 data lanes is modeled on the camera interface.
- PMIC power-sequencing/enable logic (per TI's SLVAFD0 app note) is not modeled.
- Magnetics for the KSZ9477's two integrated-PHY Ethernet ports are now modeled with a real
  part (Wurth 749010012A) — this item from the previous revision of this document is
  resolved.

---

## EMI Hardening Status: MATCHES PROJECT STANDARD (added 2026-07-03)

This project's EMI-hardening baseline (established on Wash/Zoë Rev R, TODO.md §1.2a) for any
board with external Ethernet or CAN-FD connectors is now matched:

| Bus | Wash/Zoë Rev R standard | Vera (this design) |
|---|---|---|
| Ethernet | LAN magnetics (isolation) + SRF2012-100Y CMC + PRTR5V0U2X TVS array, per port | **Wurth 749010012A magnetics + 2× SRF2012-100Y CMC + 2× PRTR5V0U2X TVS, per port** (both ring in and ring out) |
| CAN-FD | ISOW1044BDFMR — galvanically isolated transceiver, 5 kV reinforced insulation (IEC 62368-1 / VDE 0884-11) | **ISOW1044BDFMR** (same part) + SRF2012-100Y CMC + PRTR5V0U2X TVS |

Note: an earlier pass of this document cited "HX1188NL" as the Wash/Zoë magnetics part per a
stale TODO.md reference — the actual working `gen_cape_a2.py`/`add_eth_phy.py` generator
uses **Wurth 749010012A**, confirmed by reading that file directly; Vera now cites and reuses
that same real part, not the stale one.

All EMI-hardening parts/footprints (magnetics, CMC, TVS, isolated CAN transceiver) are REAL —
reused directly from this project's own verified `gen_cape_a2.py`/`gen_cape_a2_pcb.py`
symbols/pinouts, not fabricated placeholders. Two real bugs were caught and fixed while
wiring this in: (1) each Ethernet port had only modeled ONE differential pair instead of the
two (TX+/TX-/RX+/RX-) a real 10/100BASE-TX port needs; (2) the CMC/TVS glabels were initially
hand-wired at un-flipped local pin coordinates, landing on the wrong physical pin (the same
class of KiCad lib_symbol Y-up/Y-down bug caught earlier in this session) — fixed by routing
all of them through the same `glabel_pin`/`pwr_pin` helpers used everywhere else in the file.

**Still open:** the JST-GH 5-pin Ethernet connector footprint (`comp_jst_gh_5p`) is an
approximation of Wash's real `JST_GH_SM05B-GHS-TB_1x05-1MP_P1.25mm_Horizontal` footprint —
pad geometry was not independently re-verified against the real part this session, only the
pin count/pitch. Verify before fabrication.

---

## Mechanical Mounting and Wiring — Nose and Cargo Installs (added 2026-07-03)

Vera is a single 46×48mm double-sided board design installed at two physical locations.
Both installs share the same mounting-hole pattern — 4× M3, (4,4)/(42,4)/(4,44)/(42,44) mm
from the board's own corner — and the same connector set (J_PWR, J_ETH_IN, J_ETH_OUT,
J_CANFD, J_CAM1/J_CAM2, J_TOF, J_LASER). Only the local sensor harness and the board's
orientation/standoff depth differ per site.

**Per this project's own stated placement policy** (`airframe/CLAUDE.md` "Assembly and
Placement": *"Serenity's geometry is complex — bounding boxes and centroid calculations are
inadequate... if there is uncertainty about placement, request manual placement in FreeCAD"*),
the exact board pose below is a **proposed placement to verify in FreeCAD**, not a baked
position — no interior-pocket mesh exists yet at either site to check real clearance against.

### Nose install (bow sensor pod, `airframe/openscad/fuselage/bow_sensor_pod.scad`)

The sensor cluster sits on the bow's 40° flat, in `bow_sensor_pod.scad`'s own part-local
(head-shell) frame: `CAM_POS=[170.80,-282.68,55.01]`, `TOF_POS=[154.33,-282.98,55.61]`,
`LASER_POS=[161.33,-281.94,56.14]`, all normal to the flat via `BOW_ROT=[130,0,0]`, gathered
under one `FACEPLATE_CTR=[162.15,-282.53,55.59]` seat (29×17mm, 4× M2 heat-set inserts). The
apertures face −Y (forward/bow direction) in this local frame — i.e. Vera must sit **aft of**
the faceplate, back along the pod's own +Y (into the fuselage).

- **Proposed pose:** Vera mounted flat, board plane roughly parallel to the faceplate,
  standoff-offset ~20 mm aft (+Y, part-local) of `FACEPLATE_CTR`, centered on
  `BOW_CX = 161.33 mm` (aircraft centerline). Head-shell interior at this station is well
  clear of the tight nose tip (the apertures are only ~23 mm aft of the Y-min nose tip per the
  shell's own baked extent, Y −305.7 mm; head shell spans a further ~235 mm aft to the
  head/cargo joint at Y ≈ −70.7 mm) — there is no volume-tightness concern, only clearance
  against the printed pod cutter geometry and any future boss/rib work.
- **Standoff:** 4× M3 heat-set-insert bosses, printed into the interior shell wall at the
  Vera hole pattern, height sized to the taller of (a) J_ETH/J_CANFD/J_PWR connector stack on
  the back side or (b) the front-side EMI-chain/U4 stack — **8 mm standoff clearance each
  side** (16 mm total working envelope) is a reasonable starting allowance per this project's
  existing avionics-stack boss convention; **verify against actual component heights once
  real (non-placeholder) U1/U2/U3/U5/U_PMIC footprints are sourced.**
- **Open — requires FreeCAD verification:** exact standoff X/Y/Z in hull frame (bow_sensor_pod
  uses a documented, non-hull-frame local coordinate exception per its own header — do not
  hand-derive the hull-frame transform; use the FreeCAD assembly). Also verify the boss bosses
  don't intrude into the camera/ToF pocket walls (`bow_camera_cut`/`bow_tof_cut` 20×20×21mm and
  36×20×22mm interior pockets) — add a TODO item if a collision is found.
- **Open — stale bore flag:** `LASER_BORE_D=12.5mm`/`LASER_BORE_L=38.0mm` in
  `bow_sensor_pod.scad` are sized for the old 12mm-OD Class 3R laser module. The new custom-
  collimated 520nm Class 3B module's real dimensions are undetermined — do not reuse these
  bore numbers for the new module without re-measuring/re-verifying against its actual
  datasheet/mechanical drawing.

**Nose local sensor harness** (short, all <75mm point-to-point, since Vera co-locates with
the sensor cluster — unlike the pre-Vera plan of running TFmini-S's UART all the way to
Shepherd's Room):

| Connector | Signal | Run | Notes |
|---|---|---|---|
| J_CAM1/J_CAM2 | MIPI CSI-2 (1 lane modeled) | Vera → camera module, ~20-30mm | Flex/FPC preferred over discrete wire for CSI-2 signal integrity; length budget generous at this range |
| J_TOF | UART_TOF_TX/RX (dedicated UART1) | Vera → TFmini-S, ~25-40mm | Twisted pair or 4-cond ribbon; TFmini-S is 3.3V/5V tolerant per its datasheet, confirm supply pin matches Vera's 5V rail |
| J_LASER | Laser MOSFET drive (Q1 gate net) + laser V+ | Vera → laser diode module, ~15-25mm | Keep short — this is a switched high-current path; twisted pair recommended |

**Nose external (ring) harness:** J_PWR/J_ETH_IN/J_ETH_OUT/J_CANFD route aft through the open
head/cargo mating face (per `airframe/CLAUDE.md`: *"mating faces are left open between the
four fuselage sections to allow construction access and inter-compartment cable routing"*) to
**Shepherd's Room** (forward avionics bay, PACE-primary Watchdog stack) — the nearest bay to
the nose. Vera joins the Ethernet ring as a new node between Shepherd's stack and whichever
neighbor currently closes that ring segment; CAN-FD trunk taps in parallel at the same bay.
**Open — needs confirmation:** which existing ring segment Shepherd's stack currently closes
to, so Vera's insertion point (and the two new ring-cable lengths) can be fixed.

### Cargo install (`cargo_fpv_bezel`, generated by `generate_cargo_mounts.py` from `cargo_sect_shell24.scad`'s `fpv_cut` module)

The existing cargo shell geometry only cuts a **camera** aperture today: `fpv_cut` at
`CARGO_CAM_POS = [CX, CY-76, CZ]` (part-local), aperture facing **−Y in local frame via
`NADIR_ROT=[90,0,0]`, i.e. nadir/belly-facing** (looking straight down) — consistent with a
cargo-drop rangefinder/crosshair use case for the 3"×3"@5ft laser spec. `fpv_cut` provides a
29×29mm bezel recess (1mm deep, flush camera face), 16mm lens aperture, and a 14×14mm M2
mounting grid — sized for a "28mm standard FPV camera body," not Vera's own faceplate.
`cargo_sect_shell24.scad` explicitly flags its own coordinates with `// VERIFY` comments (the
gondola belly Y-coordinate and all positions are marked "verify in slicer before printing") —
this is pre-existing, inherited uncertainty in the shell file, not new uncertainty introduced
here.

- **Camera:** Vera's camera output (J_CAM1/J_CAM2) can reuse the existing `fpv_cut`
  aperture/bezel as-is — no new SCAD needed for the camera path.
- **Open — new SCAD required for ToF + laser:** unlike the nose, **no ToF or laser aperture
  exists in `cargo_sect_shell24.scad` today** — only the camera cut. To match the nose
  faceplate concept, this needs two new cutter modules (e.g. `cargo_tof_cut()`,
  `cargo_laser_cut()`) placed adjacent to `CARGO_CAM_POS`, nadir-facing via the same
  `NADIR_ROT`, with the laser spread angle re-derived for the 3"×3" (76×76mm) at 5 ft (1.5m)
  spec (a wider divergence angle than the nose's 2"×2" at 50 ft spec — do not reuse the nose's
  laser optics/bore assumption). **This is new CAD work, not yet started** — add to TODO.md
  as its own sub-task (see below) rather than fabricating placeholder positions here.
- **Proposed Vera pose (cargo):** mounted flat against the interior of the cargo gondola
  belly, standoff-offset upward (+Z, away from the nadir skin) from the camera/ToF/laser
  cluster, hole pattern centered under the bezel group. Cargo section has the largest cross-
  section of the four fuselage shells (`Cargo_Shell` baked extent Z 0.0..+163.2mm) — no
  tightness concern expected, but **must be verified against the cargo bay door mechanism and
  Jayne (cargo handling) hardware clearances** once cargo interior boss work resumes (see
  memory: cargo SCAD modules are in a legacy Y-as-dorsal frame that needs reconciling with the
  hull-frame standard before adding new geometry there — do this reconciliation before, not
  during, the Vera boss placement, to avoid building on top of a known-wrong frame).
- **Standoff:** same 8mm-per-side starting allowance as the nose install, pending real
  component-height verification.

**Cargo local sensor harness:** same connector roles as the nose table above
(J_CAM1/J_CAM2/J_TOF/J_LASER), all short local runs once Vera co-locates at the bezel;
lengths TBD pending the new ToF/laser cutter geometry above (they sit adjacent to the camera
cut, so runs should be comparably short, <75mm).

**Cargo external (ring) harness:** J_PWR/J_ETH_IN/J_ETH_OUT/J_CANFD route to the nearest
avionics bay through the cargo section's own open mating faces (to the head section forward,
or the middle section's inner-neck aft) — **open item:** determine whether **River's Room**
or **Simon's Medbay** is the shorter/more appropriate ring-insertion point for the cargo
install (both carry Emma boards and sit along the cargo/middle boundary per the Node Variant
Placement table in the root `CLAUDE.md`); this should be decided alongside the general
avionics-bay-to-bay ring cable run planning, not fabricated here.

---

## Generator Scripts

- `avionics/kicad/gen_vera.py` — generates `Vera.kicad_pro` + `Vera.kicad_sch`.
- `avionics/kicad/gen_vera_pcb.py` — generates `Vera.kicad_pcb`: footprint placement, nets,
  and the rounded-corner board outline, all built into the script (not a manual post-pass).

**Note on regeneration:** `gen_vera_pcb.py` generates a net-correct 78×80mm layout (with
`rounded_board_outline()` for the corner rounding/mounting holes) — this was the state as of
the EMI-hardening pass. `Vera.kicad_pcb` has since been **manually compacted further to
46×48mm in the KiCad GUI** (see "PCB" section above); the generator script was not updated to
match. **Re-running `gen_vera_pcb.py` will overwrite the 46×48mm hand-compaction back to the
78×80mm script layout** — do not run it without confirming that's intended, per this
project's established Kaylee/Wash script-then-manual-placement convention. If the
hand-compacted layout is to remain the baseline going forward, the positions in this section
should be back-ported into `gen_vera_pcb.py` so the script and file stay in sync.

---

## Bill of Materials Summary

| Ref | Part | Package | Side | Role |
|---|---|---|---|---|
| U1 | TI AM62A7 | 484-ball BGA, 18×18mm real body (placeholder footprint) | Front | Vision SoC |
| U_PMIC | TI TPS65219 | VQFN-32/RSM, 5×5mm real body (placeholder footprint) | Back | Power management |
| U5 | Infineon SLB9670 | PG-VQFN-32, 5×5mm real body (placeholder footprint) | Back | TPM 2.0 |
| U3 | TI MSPM0G3507 | VSSOP-28/DGS, 7.1×4.9mm real body (placeholder footprint) | Back | Control MCU |
| U2 | Microchip KSZ9477 | 128-TQFP-EP, 14×14mm real body (placeholder footprint) | Back | Ethernet switch |
| U4 | TI ISOW1044BDFMR | SOIC-16W_7.5x10.3mm (real footprint) | Front | Isolated CAN-FD transceiver |
| T1/T2 | Wurth 749010012A | SMD transformer, 8-pin (real footprint) | Front | Ethernet ring in/out magnetics |
| CMC1-4 | Bourns SRF2012-100Y | 2012 metric CMC, 4-pin (real footprint) | Front | Ethernet TX/RX common-mode suppression |
| D1-4 | Nexperia PRTR5V0U2X | SOT-363/SC-70-6 TVS array (real footprint) | Front | Ethernet TX/RX ESD/surge protection |
| CMC5 | Bourns SRF2012-100Y | 2012 metric CMC, 4-pin (real footprint) | Front | CAN-FD common-mode suppression |
| D5 | Nexperia PRTR5V0U2X | SOT-363/SC-70-6 TVS array (real footprint) | Front | CAN-FD ESD/surge protection |
| Y1 | 25 MHz crystal | 2016-2Pin (real footprint) | Back | U2 reference clock |
| Q1 | AO3400 | SOT-23 (real footprint) | Front | Laser MOSFET driver |
| R1 | 100Ω 0402 | — | Front | Laser gate resistor |
| R2 | 10kΩ 0402 | — | Front | Laser gate pulldown |
| C_MCU1 | 100 nF 0402 | — | Back | U3 decoupling |
| J_CHASSIS_R | 0Ω 0402 | — | Front | GND–PGND single-point bond |
| C_ISO | 100 nF/500 V 0402 | — | Front | GND–PGND RC bridge (parallel w/ J_CHASSIS_R) |
| J_PWR | JST-GH 2P (shielded) | — | Front | +5V/GND power input |
| J_CAM1/J_CAM2 | JST-GH 4P (shielded) | — | Front | Camera module interface |
| J_CANFD | JST-GH 4P (shielded) | — | Front | CAN-FD trunk |
| J_ETH_IN/J_ETH_OUT | JST-GH 5P (shielded, real Wash-style footprint approximated) | — | Front | Ethernet ring (GND + TX+/TX-/RX+/RX-) |
| J_TOF | JST-GH 4P | — | Front | TFmini-S ToF sensor |
| J_LASER | JST-SH 2P | — | Front | Laser module (location-specific population) |

---

For project-wide standards see the root `CLAUDE.md`; for avionics-specific conventions see
`avionics/CLAUDE.md` "Vera" section; for the full task breakdown see `TODO.md` §1.2c
(hardware) and §4.6 (firmware).
