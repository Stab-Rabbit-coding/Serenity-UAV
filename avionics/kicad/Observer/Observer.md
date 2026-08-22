# Observer — Nose/Cargo-Bay Vision, ToF & Laser Board

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**Callsign:** Observer (Observer's rifle — "she's a good gun.")
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0
**Revision:** S1 (SoM end-state — PCM-071 carrier, real symbols/footprints)
**Date:** 2026-07-13
**Status:** **SoM end-state built** by `scripts/gen_observer_carrier_sch.py` +
`gen_observer_carrier_pcb.py`. Schematic uses REAL clean-room symbols (PCM-071 SoM + KSZ9477 +
MSPM0G3507 + ISOW1044BDFMR + SLB9672) wired by signal name — **ERC = 0 errors**. PCB has REAL
footprints (240-pad 2×BTH-060 SoM on the back, TQFP-128-1EP switch, QFN/SOIC/SOT carrier),
**0 placeholder footprints**, all pad nets injected, sch↔pcb parity clean (bar 4 mounting-holes
+ the TPM thermal-EP GND tie). Placement is an initial shelf-pack (no shorts; user reserves
final positioning); **traces not yet routed → NOT fabrication-ready.** Trapezoid outline
(nose-carrier, ~70 mm long) preserved from the prior pass. See TODO.md §1.2c.1/.2 for open
items (regulator value verification, RGMII strap sign-off, MSPM0 pinmux, routing, gerbers) and
`PCBNEW_SWIG_BUG.md` for the pcbnew binding defect worked around during the rebuild.

> **Carrier power (user decision 2026-07-13):** the PCM-071 connector takes 5 V in only and
> exposes no rail to the carrier (PHYTEC HW manual §5.1), so Observer generates its own rails —
> `U_REG_3V3`/`U_REG_1V2` (TI TLV62569 bucks) + `U_REG_2V5` (TI TLV75725 LDO). TPM + KSZ
> management stay on the MSPM0 SPI. Feedback-divider/inductor/LDO-margin values are first-pass
> pending per-datasheet verification.

---

## Purpose

Observer is a **standalone PCB — not a PocketBeagle 2 Industrial cape.** Unlike Pilot/XO/Commo it
does not use the P1+P2 header stack and does not mount onto a PB2-I node. It is installed at
**two physical locations** using one shared board design:

- The **bow sensor pod** (nose, `airframe/openscad/fuselage/bow_sensor_pod.scad`) —
  2"×2" (51×51 mm) laser crosshair at 50 ft (15.2 m).
- The **cargo bay nadir FPV mount** (`cargo_fpv_bezel`) —
  3"×3" (76×76 mm) laser crosshair at 5 ft (1.5 m).

It supersedes the RunCam Nano 4 analog camera (REF-SENSOR-001, superseded) originally
specified for the bow sensor pod, and fulfils the "RP2350-based Camera/TOF/laser MCU board"
task originally tracked at TODO.md §1.1.1.1a.

Observer connects to the rest of the airframe **only** via three shielded JST-GH connectors —
Ethernet ring in, Ethernet ring out, CAN-FD trunk — plus its own 5V power input. It has no
other physical or electrical dependency on any other avionics board.

**Power (added 2026-07-05):** each Observer board draws ≈ **1.2 A typ / ~2.1–2.7 A peak at 5 V**
(AM62A7 SoC + KSZ9477 switch + camera + ToF + laser; full budget in
`docs/POWER_DISTRIBUTION.md §3.2.1`). The two boards (≈ 2.4 A typ / ~4.8 A peak combined) are
fed from a **dedicated Flight Engineer 5 V payload rail (U_BEC_OBS → J_OBS)** — NOT the shared 5 V
avionics bus, which is already near its dual-BEC capacity — keeping the switching video-SoC
load off the avionics rail and preserving its margin. Observer's own TPS65219 PMIC regulates this
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
- **"ST33GTPMISPI" TPM part** — does not exist. Replaced with **Infineon SLB9672**, the same
  SPI TPM 2.0 part already standardized fleet-wide on all 8 Pilot/XO nodes.

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
  (behind the bow sensor pod's 40° flat, per `bow_sensor_pod.scad`), connected to Observer via
  J_CAM1/J_CAM2 (CSI diff pair + I2C/power).

### Control half

- **U3 — TI MSPM0G3507** MCU. Native hardware MCAN (CAN-FD) peripheral — no software PIO
  synthesis needed (an RP2350-based design would have required this). Shares TI toolchain
  with the AM6254 real-time domain on Pilot/XO. Two independent UART instances: UART0 to
  U1 (AM62A7, crossed TX↔RX), UART1 dedicated to the TFmini-S ToF sensor (no net-sharing
  between the two links).
- **U5 — Infineon SLB9672** SPI TPM 2.0 — the exact part already used fleet-wide on all 8
  Pilot/XO nodes, reused here rather than introducing a new TPM part number.
- **U2 — Microchip KSZ9477** 7-port Ethernet switch. Port 1 (RGMII) to U1 for video egress;
  Ports 2/3 (integrated PHY, full TX+/TX-/RX+/RX- differential pairs each) feed the
  EMI-hardening chain below; SPI host interface to U3 for ToF/laser-state telemetry and
  control-plane access.
- **U4 — TI ISOW1044BDFMR** galvanically-isolated CAN-FD transceiver (**20-pin DFM package**,
  5 kV reinforced insulation — the part is 20-pin DFM per TI SLLSFF7A, NOT the "SOIC-16W" earlier
  docs claimed; the Observer U4 footprint must be 20-pad DFM) — replaces an earlier non-isolated
  TCAN1042HG-Q1 to match the
  Pilot/XO Rev R EMI-hardening standard (see below).
- **U6 — TI ISOW1412** galvanically-isolated RS-485 transceiver (20-pin DFM,
  `Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm`, REFERENCES.md REF-SENSOR-010), added 2026-07-26
  as part of the fleet-wide trust-module rollout (schematic "Section H: ISOW1412 Isolated
  RS-485 (U6)"). Integrates its own isolated DC-DC for the bus-side supply, run half-duplex
  on RS485_A/RS485_B by shorting Y-to-A and Z-to-B; RS485_DE drives both DE and RE_N.
  J_RS485_IN/J_RS485_OUT trunk connectors added alongside. **PCB layout not yet synced** —
  Observer.kicad_pcb predates this schematic addition (open work, root `TODO.md` §1.2a).
- **Y1** — 25 MHz crystal for U2's reference clock.

### EMI hardening (added 2026-07-03 — see "EMI Hardening Status" below)

Matches the Pilot/XO Rev R baseline (TODO.md §1.2a) using the SAME real, already-verified
parts and footprints from this project's own `gen_cape_a2.py`/`gen_cape_a2_pcb.py`:

- **Each Ethernet port** (ring in, ring out): KSZ9477 port → **Wurth 749010012A** SMD
  10/100BASE-TX transformer (T1/T2, real 8-pin footprint) → 2× **Bourns SRF2012-100Y**
  common-mode choke (CMC1-4, one per differential pair) → 2× **Nexperia PRTR5V0U2X** TVS
  array (D1-4, shunt to GND) → JST-GH 5-pin connector (J_ETH_IN/J_ETH_OUT — GND + 4 signal,
  matching Pilot's real `JST_GH_SM05B-GHS-TB` footprint, not a fabricated 6-pin).
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
pulldown, J_LASER JST-SH 2P) serves both install locations. **Per `docs/OBSERVER_LASER_ANALYSIS.md`
(Rev A, 2026-07-05), both installs now use ONE shared 520 nm green laser diode + driver**; the
two sites differ only in (1) a per-location terminal optic that sets the spread angle and (2) a
per-location hardware current limit that sets the optical power / IEC 60825-1 class. This
retires the previous split (green nose + separate 650 nm red cargo module) and unifies the
laser BOM to a single green diode family. Rationale in full: `docs/OBSERVER_LASER_ANALYSIS.md`.

- **Pattern is a thin-line CROSSHAIR (not a bare dot) — a projected metrology reference.** A
  PB2-I computes a detected object's **size and relative orientation** from ToF range + the
  crosshair's known projected angle + trigonometry (size = (obj_px/cross_px)·2R·tan(θ/2); tilt
  from arm foreshortening — `docs/OBSERVER_LASER_ANALYSIS.md §4.4`). The binding constraint is
  camera pixel coverage: the nominal 2" @ 50 ft crosshair is too small (≈6 px on a wide lens);
  size the fan angle for **N ≈ 24–48 px** (nose ≈ 4–8" at 50 ft, or a narrower FOV). Cargo's
  3" @ 5 ft is already ample.
- **Spread angle is set by the terminal optic, not the source:** nose near-collimated crosshair
  (fan angle sized for pixel coverage, above); cargo ≈ 2.86° stock DOE crosshair. Same
  collimated green source both places.
- **Both sites are Class 2 (≤ 1 mW green)** — the nose is **not** inherently Class 3B. A
  thin-line green crosshair detected by Observer's own *strobed camera + frame-difference* (not a
  naked eye) needs only **~0.2–0.8 mW → Class 2**; the earlier "nose = Class 3B" was the
  worst-case spread-crosshair + naked-eye-in-full-sun corner (~82 mW). Cargo is likewise
  Class 2 (green's 6.64× photopic advantage over the retired 650 nm red). Full derivation:
  `docs/OBSERVER_LASER_ANALYSIS.md`.
- **Class 2 at both sites drops the Class 3B key-interlock and mechanical shutter.** The
  `LASER_KEY_IN`/`LASER_IND` lines already on Observer become optional defense-in-depth. Keep each
  ≤ 1 mW cap **HARDWARE-enforced** (fixed current limit), not firmware-only.
- **Firmware dependency:** the nose Class 2 margin depends on strobe + frame-difference
  detection in the AM62A7 ISP (laser-sync GPIO/PWM) — budget it in the Observer firmware WBS
  (TODO.md §4.6). 3B would only return if a *human at the 50 ft target* must see a *spread
  reticle* in full sun (not Observer's requirement).
- **Do not source the green diode or either terminal optic** until a real datasheet with a
  verified mW rating and IEC 60825-1 class replaces the placeholder citation in REFERENCES.md
  (REF-IEC-002 pending item; tracked TODO.md §1.2c.4).
- **Laser Diode Selection**
  
    - ams-OSRAM USA INC. PLT5 520EB_P

- **Laser Driver IC Selection**

    - **iC-Haus iC-WKN**

- **Nose Laser DOE Selection**

    - holo/or laserland or thorlabs

---

## PCB

**1.0 × 2.75 in (25.4 × 69.85 mm), double-sided, 4-layer FR4, rounded corners (3 mm radius, matching Pilot/Flight Engineer
convention).** - **Changed 7-7-2026** updated Observer dimensions to 1.0 × 2.75 in (25.4 × 69.85 mm) to allow it to sit flush against the camera/ToF/laser faceplate within the nose. Camera, ToF, and laser connectors are moved to the board's forward end and Ethernet, power, and CAN-FD connectors are at the other end. Four mounting holes are still present. Design should work in both nose and cargo bay.
    - This allows for direct pcb soldering of sensors in nose or via jst connectors in cargo bay. (needs feasibilty review)

**Board coordinate frame (KiCad; user-confirmed 2026-07-12):** **+X = fore→aft, +Y =
starboard→port, +Z = ventral→dorsal.** On the as-built board the camera/ToF/laser JST
connectors **and** their direct-solder lands (`J_CAM_DS`/`J_TOF_DS`/`J_LASER_DS`) are at the
**high-X end (~62–67 mm)**; the Ethernet-ring, CAN-FD, and power connectors are at the
**low-X end (~6–11 mm)**. The three sensor apertures differ in the **port-starboard (Y)** axis
— **camera = port (high Y), ToF = starboard (low Y), laser = centreline** — so the DS lands are
spread along **Y** to match `airframe/openscad/fuselage/bow_sensor_pod.scad`
(`CAM_POS`/`TOF_POS`, ToF··laser 8.2 mm, ToF··camera 16.5 mm). Board and DS-land placement are
correct as-built; an earlier "fore/aft mismatch" note was a high-vs-low-X mix-up, now resolved.
Final XY/rotation of the lands to the sensor mounting plate is a manual mechanical fit.

Board-size history: the original single-sided draft was 110×190 mm — the two big placeholder
ICs (U1's BGA footprint, U2's TQFP footprint) forced that size using rough first-guess body
dimensions. Several things brought it down to the current 1.0 × 2.75 in (25.4 × 69.85 mm):

1. **Double-siding**: U1 (AM62A7) on the front; U_PMIC/U5/U3/U2 on the back of the *same*
   board area (legal — opposite copper faces don't collide).
2. **Real component body sizes** (2026-07-03 datasheet research pass) replaced rough
   estimates — most significantly MSPM0G3507 turned out to have a real VSSOP-28 package
   option (7.1×4.9mm) far smaller than the VQFN-48 (7×7mm) first assumed, and AM62A7/KSZ9477/
   SLB9672/TPS65219 all have smaller real bodies (18×18mm, 14×14mm, 5×5mm, 5×5mm
   respectively) than the placeholder generator's original guesses.
3. **Adding the full EMI-hardening chain** (12 new small parts: 2 magnetics, 4 CMC, 4 TVS,
   plus the isolated CAN transceiver and its own CMC/TVS) grew the script-generated layout
   from an intermediate 68.5×63.5mm to 78×80mm — expanding only as required for the
   hardening components.
4. **Further manual compaction in the KiCad GUI** (component repacking, tighter spacing)
   brought it down to the current **1.0 × 2.75 in (25.4 × 69.85 mm)** — the tightest pass yet, packing all parts
   (front + back) right up against the courtyard-clearance limit.

Two rounds of manual GUI editing each introduced the same class of file corruption, both
found and fixed by chunk-removal bisection against `kicad-cli`'s "Failed to load board"
error: (1) the layer table getting rewritten with wrong layer IDs/types for B.Cu (declared
as ID 2 / type "power" instead of the fixed KiCad enum value 31 / type "signal", with
`In2.Cu` missing entirely); (2) the Edge.Cuts outline geometry becoming a non-closed,
self-intersecting shape after corner-dragging in the GUI (one arc's start point even landed
outside the board, at negative Y). Both were corrected in place — the layer table restored to
the standard values, the outline rebuilt as a clean rounded-rectangle at the compacted
1.0 × 2.75 in (25.4 × 69.85 mm) size with squared, properly-closed corners — and mounting holes were re-symmetrized
to an exact 4mm margin (4,4)/(65.85,4)/(4,21.4)/(65.85,21.4). A handful of components (J_TOF, U4) also
needed small repositioning after the resize to clear new courtyard/pad collisions.

Component placement is net-correct and DRC-clean (0 shorting_items, 0 net_conflict, 0
courtyards_overlap, 0 clearance violations, 0 solder_mask_bridge, 0 invalid_outline as of
2026-07-03, post-compaction re-verification) but **no copper traces are routed yet** — only a
GND pour zone on In1.Cu (bounds updated to 44×46mm to match). This is intentional per this
project's established PCB workflow (`avionics/AGENTS.md`: "PCBs are tightly packed. All final
component footprint positions will be done manually, after PCBs are populated and nets are
built by script.") — the script (`gen_jayne_pcb.py`) placed footprints and built nets;
subsequent manual compaction in the KiCad GUI is the "final positions done manually" step
this project's workflow anticipates. **Note:** `gen_jayne_pcb.py` itself still generates the
pre-compaction 78×80mm layout — it has not been updated to match the hand-compacted 1.0 × 2.75 in (25.4 × 69.85 mm)
result, so re-running it will not reproduce the current file (see "Generator Scripts" below).

**Open DRC finding, REFERRED TO USER 2026-07-12:** CI (`kicad-cli` 9.0.9, not available in the
assistant sandbox — the KiCad PPA host is blocked by this environment's egress policy) reports
U4 (TI ISOW1044BDFMR, SOIC-16W) with 1 `clearance` + 1 `solder_mask_bridge` hard DRC violation
(`actual 0.0000 mm` — copper touching). A same-day fix attempt that dropped each U4 pad's
explicit 90° local `at` rotation (reasoning: it looked redundant against the footprint's own
90° placement rotation, and the unplaced upstream `Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm`
library footprint carries no per-pad rotation) was **reverted** after CI showed it made things
far worse — 32 hard violations, including genuine `shorting_items` between adjacent U4 pads
(GND/CANFD_TX, CANFD_TX/CANFD_STBY_N, CANFD_ISOGND/+5V, CANFD_ISO_L/CANFD_ISO_H, etc.). That
result shows the pad's stored `at` angle is *not* simply additive with the footprint's
placement rotation the way a naive rigid-body composition would suggest — the real semantics
kicad-cli applies here couldn't be confirmed without live DRC. **Do not re-attempt this fix
blind;** re-verify any candidate change against `kicad-cli pcb drc` (KiCad 9.0.x) before
committing. File is back at the pre-2026-07-12 state (1 clearance + 1 solder_mask_bridge on
U4, same as the rest of this section describes).

Mounting holes: 4× M3, symmetric 4 mm margin from each edge — (4,4), (65.85,4), (4,21.4), (65.85,21.4).

---

## Verified vs. Placeholder — Read Before Fabricating Anything

**Real, verified:**

- All net-level architecture/interconnect (which pin talks to which pin, UART crossing,
  CAN-FD, SPI buses, PGND/GND single-point isolation — verified via netlist export, only one
  bridge point between GND and PGND).
- TI ISOW1044BDFMR's SOIC-16W pinout (reused from Pilot's own verified `gen_cape_a2.py`).
- AO3400 SOT-23 N-FET pinout.
- TPS65219 as the correct PMIC family for AM62A power (per TI's own SLVAFD0 app note),
  VQFN-32/RSM 5×5mm real body size.
- Microchip KSZ9477 as the correct part for HSR/PRP hardware redundancy (per AN3474) — NOT
  LAN9355/KSZ9563, which do not implement it. Real body size 14×14mm (128-TQFP-EP).
- AM62A7 real body size 18×18mm (484-ball FCBGA/FCCSP, AMB/ANF package).
- MSPM0G3507 real VSSOP-28 (DGS) package option, body ~7.1×4.9mm — smaller than the VQFN-48
  first assumed.
- SLB9672 real PG-UQFN-32 package, body ~5×5mm.
- Wurth 749010012A magnetics, Bourns SRF2012-100Y CMC, Nexperia PRTR5V0U2X TVS — all reused
  verbatim (pinout + footprint reference) from this project's own working Pilot/XO generator.

**Placeholder / NOT real — must be replaced before fabrication:**

- *(Resolved)* Placeholder ICs have been removed. U1 (AM62A) and U_PMIC are now integrated onto the real `phyCORE-AM62x_PCM071` SoM footprint. U2, U3, U4, and U5 now utilize verified, datasheet-accurate TQFP, QFN, and SOIC footprints.
- The JST-GH 5-pin Ethernet connector footprint is an untuned approximation of Pilot's real
  `JST_GH_SM05B-GHS-TB_1x05-1MP_P1.25mm_Horizontal` part (pin count/pitch match; exact pad
  geometry not independently re-verified).
- Only 1 of 4 real MIPI CSI-2 data lanes is modeled on the camera interface.

---

## EMI Hardening Status: MATCHES PROJECT STANDARD (added 2026-07-03)

This project's EMI-hardening baseline (established on Pilot/XO Rev R, TODO.md §1.2a) for any
board with external Ethernet or CAN-FD connectors is now matched:

| Bus | Pilot/XO Rev R standard | Observer (this design) |
|---|---|---|
| Ethernet | LAN magnetics (isolation) + SRF2012-100Y CMC + PRTR5V0U2X TVS array, per port | **Wurth 749010012A magnetics + 2× SRF2012-100Y CMC + 2× PRTR5V0U2X TVS, per port** (both ring in and ring out) |
| CAN-FD | ISOW1044BDFMR — galvanically isolated transceiver, 5 kV reinforced insulation (IEC 62368-1 / VDE 0884-11) | **ISOW1044BDFMR** (same part) + SRF2012-100Y CMC + PRTR5V0U2X TVS |

Note: an earlier pass of this document cited "HX1188NL" as the Pilot/XO magnetics part per a
stale TODO.md reference — the actual working `gen_cape_a2.py`/`add_eth_phy.py` generator
uses **Wurth 749010012A**, confirmed by reading that file directly; Observer now cites and reuses
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
approximation of Pilot's real `JST_GH_SM05B-GHS-TB_1x05-1MP_P1.25mm_Horizontal` footprint —
pad geometry was not independently re-verified against the real part this session, only the
pin count/pitch. Verify before fabrication.

---

## Mechanical Mounting and Wiring — Nose and Cargo Installs (added 2026-07-03)

Observer is a single 1.0 × 2.75 in (25.4 × 69.85 mm) double-sided board design installed at two physical locations.
Both installs share the same mounting-hole pattern — 4× M3, (4,4)/(65.85,4)/(4,21.4)/(65.85,21.4) mm
from the board's own corner — and the same connector set (J_PWR, J_ETH_IN, J_ETH_OUT,
J_CANFD, J_CAM1/J_CAM2, J_TOF, J_LASER). Only the local sensor harness and the board's
orientation/standoff depth differ per site.

**Per this project's own stated placement policy** (`airframe/AGENTS.md` "Assembly and
Placement": *"Serenity's geometry is complex — bounding boxes and centroid calculations are
inadequate... if there is uncertainty about placement, request manual placement in FreeCAD"*),
the exact board pose below is a **proposed placement to verify in FreeCAD**, not a baked
position — no interior-pocket mesh exists yet at either site to check real clearance against.

### Nose install (bow sensor pod, `airframe/openscad/fuselage/bow_sensor_pod.scad`)

The sensor cluster sits on the bow's 40° flat, in `bow_sensor_pod.scad`'s own part-local
(head-shell) frame: `CAM_POS=[170.80,-282.68,55.01]`, `TOF_POS=[154.33,-282.98,55.61]`,
`LASER_POS=[161.33,-281.94,56.14]`, all normal to the flat via `BOW_ROT=[130,0,0]`, gathered
under one `FACEPLATE_CTR=[162.15,-282.53,55.59]` seat (29×17mm, 4× M2 heat-set inserts). The
apertures face −Y (forward/bow direction) in this local frame — i.e. Observer must sit **aft of**
the faceplate, back along the pod's own +Y (into the fuselage).

- **Proposed pose:** Observer mounted flat, board plane roughly parallel to the faceplate,
  standoff-offset ~20 mm aft (+Y, part-local) of `FACEPLATE_CTR`, centered on
  `BOW_CX = 161.33 mm` (aircraft centerline). Head-shell interior at this station is well
  clear of the tight nose tip (the apertures are only ~23 mm aft of the Y-min nose tip per the
  shell's own baked extent, Y −305.7 mm; head shell spans a further ~235 mm aft to the
  head/cargo joint at Y ≈ −70.7 mm) — there is no volume-tightness concern, only clearance
  against the printed pod cutter geometry and any future boss/rib work.
- **Standoff:** 4× M3 heat-set-insert bosses, printed into the interior shell wall at the
  Observer hole pattern, height sized to the taller of (a) J_ETH/J_CANFD/J_PWR connector stack on
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

**Nose local sensor harness** (short, all <75mm point-to-point, since Observer co-locates with
the sensor cluster — unlike the pre-Observer plan of running TFmini-S's UART all the way to
Shepherd's Room):

| Connector | Signal | Run | Notes |
|---|---|---|---|
| J_CAM1/J_CAM2 | MIPI CSI-2 (1 lane modeled) | Observer → camera module, ~20-30mm | Flex/FPC preferred over discrete wire for CSI-2 signal integrity; length budget generous at this range |
| J_TOF | UART_TOF_TX/RX (dedicated UART1) | Observer → TFmini-S, ~25-40mm | Twisted pair or 4-cond ribbon; TFmini-S is 3.3V/5V tolerant per its datasheet, confirm supply pin matches Observer's 5V rail |
| J_LASER | Laser MOSFET drive (Q1 gate net) + laser V+ | Observer → laser diode module, ~15-25mm | Keep short — this is a switched high-current path; twisted pair recommended |

**Nose external (ring) harness:** J_PWR/J_ETH_IN/J_ETH_OUT/J_CANFD route aft through the open
head/cargo mating face (per `airframe/AGENTS.md`: *"mating faces are left open between the
four fuselage sections to allow construction access and inter-compartment cable routing"*) to
**Shepherd's Room** (forward avionics bay, PACE-primary Watchdog stack) — the nearest bay to
the nose. Observer joins the Ethernet ring as a new node between Shepherd's stack and whichever
neighbor currently closes that ring segment; CAN-FD trunk taps in parallel at the same bay.
**Open — needs confirmation:** which existing ring segment Shepherd's stack currently closes
to, so Observer's insertion point (and the two new ring-cable lengths) can be fixed.

### Cargo install (`cargo_fpv_bezel`, generated by `generate_cargo_mounts.py` from `cargo_sect_shell24.scad`'s `fpv_cut` module)

The existing cargo shell geometry only cuts a **camera** aperture today: `fpv_cut` at
`CARGO_CAM_POS = [CX, CY-76, CZ]` (part-local), aperture facing **−Y in local frame via
`NADIR_ROT=[90,0,0]`, i.e. nadir/belly-facing** (looking straight down) — consistent with a
cargo-drop rangefinder/crosshair use case for the 3"×3"@5ft laser spec. `fpv_cut` provides a
29×29mm bezel recess (1mm deep, flush camera face), 16mm lens aperture, and a 14×14mm M2
mounting grid — sized for a "28mm standard FPV camera body," not Observer's own faceplate.
`cargo_sect_shell24.scad` explicitly flags its own coordinates with `// VERIFY` comments (the
gondola belly Y-coordinate and all positions are marked "verify in slicer before printing") —
this is pre-existing, inherited uncertainty in the shell file, not new uncertainty introduced
here.

- **Camera:** Observer's camera output (J_CAM1/J_CAM2) can reuse the existing `fpv_cut`
  aperture/bezel as-is — no new SCAD needed for the camera path.
- **Open — new SCAD required for ToF + laser:** unlike the nose, **no ToF or laser aperture
  exists in `cargo_sect_shell24.scad` today** — only the camera cut. To match the nose
  faceplate concept, this needs two new cutter modules (e.g. `cargo_tof_cut()`,
  `cargo_laser_cut()`) placed adjacent to `CARGO_CAM_POS`, nadir-facing via the same
  `NADIR_ROT`, with the laser spread angle re-derived for the 3"×3" (76×76mm) at 5 ft (1.5m)
  spec (a wider divergence angle than the nose's 2"×2" at 50 ft spec — do not reuse the nose's
  laser optics/bore assumption). **This is new CAD work, not yet started** — add to TODO.md
  as its own sub-task (see below) rather than fabricating placeholder positions here.
- **Proposed Observer pose (cargo):** mounted flat against the interior of the cargo gondola
  belly, standoff-offset upward (+Z, away from the nadir skin) from the camera/ToF/laser
  cluster, hole pattern centered under the bezel group. Cargo section has the largest cross-
  section of the four fuselage shells (`Cargo_Shell` baked extent Z 0.0..+163.2mm) — no
  tightness concern expected, but **must be verified against the cargo bay door mechanism and
  Observer (cargo handling) hardware clearances** once cargo interior boss work resumes (see
  memory: cargo SCAD modules are in a legacy Y-as-dorsal frame that needs reconciling with the
  hull-frame standard before adding new geometry there — do this reconciliation before, not
  during, the Observer boss placement, to avoid building on top of a known-wrong frame).
- **Standoff:** same 8mm-per-side starting allowance as the nose install, pending real
  component-height verification.

**Cargo local sensor harness:** same connector roles as the nose table above
(J_CAM1/J_CAM2/J_TOF/J_LASER), all short local runs once Observer co-locates at the bezel;
lengths TBD pending the new ToF/laser cutter geometry above (they sit adjacent to the camera
cut, so runs should be comparably short, <75mm).

**Cargo external (ring) harness:** J_PWR/J_ETH_IN/J_ETH_OUT/J_CANFD route to the nearest
avionics bay through the cargo section's own open mating faces (to the head section forward,
or the middle section's inner-neck aft) — **open item:** determine whether **River's Room**
or **Simon's Medbay** is the shorter/more appropriate ring-insertion point for the cargo
install (both carry Commo boards and sit along the cargo/middle boundary per the Node Variant
Placement table in the root `AGENTS.md`); this should be decided alongside the general
avionics-bay-to-bay ring cable run planning, not fabricated here.

---

## Generator Scripts

- `avionics/kicad/Observer/scripts/gen_observer_carrier_sch.py` — generates
  `Observer.kicad_pro` + `Observer.kicad_sch` (SoM end-state, current).
- `avionics/kicad/Observer/scripts/gen_observer_carrier_pcb.py` — generates `Observer.kicad_pcb`:
  footprint placement, nets, and the rounded-corner board outline, all built into the script
  (not a manual post-pass).

**Note on regeneration:** `gen_observer_carrier_pcb.py` generates a net-correct 78×80mm layout
(with `rounded_board_outline()` for the corner rounding/mounting holes) — this was the state as
of the EMI-hardening pass. `Observer.kicad_pcb` has since been **manually compacted further to
1.0 × 2.75 in (25.4 × 69.85 mm) in the KiCad GUI** (see "PCB" section above); the generator script was not updated to
match. **Re-running `gen_observer_carrier_pcb.py` will overwrite the 1.0 × 2.75 in (25.4 × 69.85 mm) hand-compaction
back to the 78×80mm script layout** — do not run it without confirming that's intended, per this
project's established FlightEngineer/Pilot script-then-manual-placement convention. If the
hand-compacted layout is to remain the baseline going forward, the positions in this section
should be back-ported into `gen_observer_carrier_pcb.py` so the script and file stay in sync.

---

## Bill of Materials Summary

| Ref | Part | Package | Side | Role |
|---|---|---|---|---|
| U1 | TI AM62A7 | 484-ball BGA, 18×18mm real body (placeholder footprint) | Front | Vision SoC |
| U_PMIC | TI TPS65219 | VQFN-32/RSM, 5×5mm real body (placeholder footprint) | Back | Power management |
| U5 | Infineon SLB9672 | PG-UQFN-32, 5×5mm real body (placeholder footprint) | Back | TPM 2.0 |
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
| J_ETH_IN/J_ETH_OUT | JST-GH 5P (shielded, real Pilot-style footprint approximated) | — | Front | Ethernet ring (GND + TX+/TX-/RX+/RX-) |
| J_TOF | JST-GH 4P | — | Front | TFmini-S ToF sensor |
| J_LASER | JST-SH 2P | — | Front | Laser module (location-specific population) |

---

For project-wide standards see the root `AGENTS.md`; for avionics-specific conventions see
`avionics/AGENTS.md` "Observer" section; for the full task breakdown see `TODO.md` §1.2c
(hardware) and §4.6 (firmware).

---

## 2026-08-03 — Trust-module MCU/TPM retarget

The trust module on this board now uses **TI MSPM0G3519-Q1 (`M0G3519QRGZRQ1`)** (48-pin RGZ VQFN, 512 KB flash / 128 KB SRAM) and the
**Infineon SLB 9672AU2.0** TPM (PG-UQFN-32-1,-2, extended −40 to +105 °C), superseding the
MSPM0G3507 and SLB9670VQ2.0.  Parts and the specifications applied are catalogued as
REF-SENSOR-013 and REF-SEC-002 in `REFERENCES.md`; the change was applied by
`avionics/kicad/retarget_mspm0g351x_slb9672.py` and `avionics/kicad/retarget_pcb_footprints.py`,
which also wrote `.pre-g351x` backups beside each edited file.

**No net or pin assignment changed.** The MSPM0G351x-Q1 RGZ-48 pin map was verified pad
for pad against the MSPM0G350x it replaces (SLASFA6B Fig 6-5 vs SLASEX6C Fig 6-4) and is
identical, so U3 keeps every one of its 29 connections exactly as they were.

Two corrections did land on the PCB:

- **U3 land pattern.** The footprint was `QFN-48-1EP_7x7mm_P0.5mm_EP5.15x5.15mm`, which
  KiCad's own `descr` field identifies as an *Analog Devices LTC legacy* QFN outline. TI's
  RGZ0048F exposed thermal pad is 4.1 mm square, so that land overhung the package's
  thermal pad by 0.525 mm on every side. Now `VQFN-48-1EP_7x7mm_P0.5mm_EP4.1x4.1mm`; the
  48 lead pads are identical between the two, so only pad 49 changed.
- **U5 exposed pad.** The SLB9670 symbol stopped at pin 32 and never netted the package's
  thermal pad. It is now pad 33 tied to GND, as Infineon requires.

Firmware note: the CAN pins do not move, but their IOMUX changes — `CAN0_TX`/`CAN0_RX` on
PA12/PA13 are **PF12** on this family, and PA15 offers `SPI1_CS2` rather than `SPI1_CS0`.

Open items from this pass are tracked in `TODO.md` §1.2d — read those before ordering
anything from this board.

### DRC status after the retarget

Measured in place (a `.kicad_pcb` copied away from its project directory loses the
sibling `.kicad_pro` custom rules and netclasses, and the counts become meaningless):

| Board | before | after |
|---|---|---|
| Observer | 289 | 289 — unchanged |
| CAN-PERIPH-GW-1 | 743 | 804 |

The gateway's +61 are `clearance` violations in the MCU area, where the 48-pin traces
still run to a footprint that is now 32 pads at 5 x 5 mm. They clear with the manual
re-route tracked in TODO.md 1.2d.

The exposed-pad corrections are applied as an in-place edit of the placed footprint
(library reference, Value and the thermal pad only). Rebuilding the footprint from the
library instead would discard whatever the board author tuned on that instance — mask
margins, pad clearance overrides, zone connections — which showed up as ~180 spurious
clearance / solder-mask-bridge / shorting violations on Observer before this was fixed.
