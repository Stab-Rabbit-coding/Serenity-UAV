# Cargo-Door Servo Gateway (GW-CARGO-DOOR) — Specification, Rev A (2026-09-21)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**AI note:** Drafted by Claude (model: Claude Opus 5, Anthropic) under the author's
direction, 2026-09-21, per `AGENTS.md` §3 AI attribution.
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0

> ⚠️ **ENGINEERING REVIEW REQUIRED.** Rev A is a design specification, not a
> validated build. Every figure marked VERIFY is an assumption to be replaced by a
> bench measurement or a primary-source read before flight-article procurement.

Single source of the mechanical stations in this document: `tools/cargo_layout_fit.py`
(`GW_*`; exported to `airframe/openscad/fuselage/cargo/cargo_layout_t5_params.scad`,
imported by `merge_cargo_interior.py`). Run `/usr/bin/python3 tools/cargo_layout_fit.py`
for the proof (PASS 2026-09-21, Rev T5f shell).

---

## 0. Scope

Two things, in one document:

| § | Item | Status |
|---|---|---|
| 1–8 | **GW-CARGO-DOOR** — one `SKIPPER-CAN-PERIPH-GW-PCB` (`N_STACKS=1`) that hosts the SG90-class cargo-bay **door** servos (port, starboard) and the payload **release** servo, mounted on a printed card-edge tray at the forward rim of the clamshell aperture | **Specified, wired in, mount points cut** (this revision) |
| 9 | **GW-RCS** — a second gateway for the four SG90-class RCS bleed-valve servos of the deferred aft EDF (Phase 11) | **Specified only** — not implemented; `deferred/WBS.md` §Phase11 |

What this closes: the SG90 cargo servos were declared bus-networked on 2026-09-20
(`avionics/WBS.md` §1.9.2, XO board-area fix: "the winch and SG90 door servos are
bus-networked over CAN-FD/RS-485 for fleet failover, not locally driven") and their
local driver silicon was deleted from XO — but nothing on the airframe was assigned to
drive them. `DRV8833-CARGO` + `cargo_drv8833_tray.stl` (Rev P, Cape-B GPIO) were still in
the BOM. This document assigns the servos to their own gateway and **retires the DRV8833
path** (§7).

---

## 1. Decisions

| ID | Decision | Why |
|---|---|---|
| **D-GW-1** | The door/release servos get their **own** gateway board (`GW-CARGO-DOOR`, `N_STACKS=1`) — not a lane on the winch gateway | `docs/CARGO_WINCH_SPECIFICATION.md` §5.1 already consumes every `J_FLEX` signal of the winch gateway (UART = servo bus, `FLEX_PWM_IO` = catch solenoid, `FLEX_TTL_GPIO` = HX711, `J_ENC` = spool encoder). Its item 13 ("door/release servos could move to the gateway's spare `FLEX_PWM_IO`") is contradicted by its own §5.1 table and is closed by this decision. A separate node also keeps door actuation independent of the winch's still-open RS-485 transceiver decision (§5.1.1 there) and of the Phase 7 winch schedule — the doors are needed from Phase 5. |
| **D-GW-2** | **Three** servo channels: port door, starboard door, payload release | The doors are two **independent** piano-hinged halves since Rev R1b (`airframe/WBS.md` §1.1.0: each door hinges at its own outboard belly edge, free edges meet at X_CL). One actuator cannot drive both without a linkage that crosses the aperture. The Rev P BOM (`SERVO-CARGO` qty 2 = 1 door + 1 release) predates the split. **Owner to confirm** the two-actuator reading; the alternative (one servo + cross-linkage) is not designed here. |
| **D-GW-3** | Primary command path = **OpenServoCore osc-native serial chain** on `FLEX_UART_TX/RX`; **fallback** = stock SG90 PWM on the two hardware timer pins | REF-SENSOR-015 standardised the SG90 class on OpenServoCore (2026-08-02), but the SG90 swap board is "designed but not spun yet" and the project says "nothing here is shippable yet" (re-read 2026-09-21). The fallback lets the doors work with stock SG90s until then. |
| **D-GW-4** | Servo power is a **fused branch of the 6 V servo rail**, not `J_FLEX`'s `+5V` pin | Three SG90s at the manufacturer's stated 0.5–2 A operating current (REF-ACT-003) can exceed 3 A stalled; the 2.54 mm header pin and the board's `+5V` trace are not rated for that, and the gateway's own supply is the avionics `RAIL-2`. Signal + GND only cross `J_FLEX`. |
| **D-GW-5** | Mount = printed **card-edge tray**, board standing transverse on the forward belly slab, component side aft | The board has no mounting holes (generator outline; `gen_can_periph_gw_pcb.py` places none). The tilt-controller board on the Rev T5e bracket uses the same rail pattern. Standing transverse is the only orientation that fits the pocket's 14 mm floor-level depth (§5). |
| **D-GW-6** | Termination solder jumpers **open** on this node | It sits mid-chain between the chin nodes and the cargo Observer (§6). Termination stays at the trunk ends per the Phase 5 build steps (`WBS.md` Phase 5: "120 Ω SOLDERED to CN1 Cape-B"). |

---

## 2. Hardware

| Ref (BOM) | Item | Qty | Mass | Notes |
|---|---|---|---|---|
| `CAN-PERIPH-GW-DOOR` | `SKIPPER-CAN-PERIPH-GW-PCB` built at `N_STACKS=1` (MSPM0G3518-Q1 RHB-32 + SLB9672 TPM + ISOW1044 CAN-FD + ISOW1412 RS-485 + TLV62569 buck), outline 49.0 × 25.5 × 1.6 mm (1.93 × 1.00 × 0.063 in) | 1 | ~6 g (0.013 lbm) **VERIFY** — FR4 3.7 g + parts estimate; weigh the populated board | `avionics/kicad/CAN-PERIPH-GW-1/` — the `N_STACKS=1` backup `CAN-PERIPH-GW-1_N1_2026-07-26.kicad_pcb` is the DRC-clean single-lane layout; the live `.kicad_pcb` is the user-packed 2-lane nacelle board. Build this instance from the N=1 layout (or repack — the tray is parametric, §5). U2 is an SLB9672 until the OPTIGA Trust M swap (REF-SENSOR-016) lands. |
| `SERVO-CARGO` | SG90 9 g micro servo (TowerPro SG90, REF-ACT-003: 23 × 12.2 × 29 mm, 1.8 kgf·cm at 4.8 V, 0.1 s/60°) with OpenServoCore "OSC SG90 M007" swap board (REF-SENSOR-015) when available | **3** (was 2) | 9 g each (0.020 lbm) | Port door, starboard door, payload release. Pre-production caveat on the swap board unchanged. |
| `PRINT-GW-DOOR-TRAY` | `gateway_door_tray.stl` — CF-PETG card-edge tray | 1 | 5.0 g (0.011 lbm) — exported volume 4 729 mm³ × 1.05 g/cm³ | `airframe/openscad/fuselage/cargo/gateway_door_tray.scad` |
| `INS-M3` / `SCR-M3X8` | RX-M3×5.7 heat-set inserts in the shell bosses; M3 × 8 SHCS | 4 + 4 | ~1.2 g + ~3.2 g | Same insert as the chin shelf / cradle hangers |
| harness | see §6 | — | ~8 g (0.018 lbm) est. | |

**Retired by this revision:** `DRV8833-CARGO` (3 g) and `PRINT-DRV8833-TRAY` (8 g) → qty 0,
rows kept for the record (§7).

**Net mass change:** +6 + 5 + 4.4 + 8 + 9 (third servo) − 11 = **≈ +21 g (0.047 lbm)** at
hull (X_CL, Y −10, Z 25). Taking the CG at the hover thrust line (Y 46.6) and the
cargo-delivery AUW of ~3 383 g (`docs/POWER_DISTRIBUTION.md` §2), the CG moves
21 × (−56.6) / 3 404 ≈ **−0.35 mm (forward)** — inside the ledger's noise; feed it to A0.

---

## 3. Signal assignment — `J_FLEX` (1×8, 2.54 mm)

Pin functions after the 2026-08-03 RHB-32 retarget (`avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md`
"Trust-module MCU/TPM retarget"; MCU symbol pad map in `CAN-PERIPH-GW-1.kicad_sch`):

| `J_FLEX` pin | Net | MCU pin | **Primary — OpenServoCore chain** (D-GW-3) | **Fallback — stock SG90 PWM** |
|---|---|---|---|---|
| 1 | `FLEX_UART_TX` | PA0 (UART0_TX) | osc-native bus, all three servos daisy-chained, IDs 1 (port door), 2 (stbd door), 3 (release) | — |
| 2 | `FLEX_UART_RX` | PA1 (UART0_RX) | osc-native bus return / status chain | — |
| 3 | `FLEX_TTL_GPIO` | PA24 (GPIO) | **reserved** as bus direction/enable **if** osc-native's physical layer is single-wire half-duplex (**VERIFY** — the upstream README does not state the physical layer; see Open items) | release servo, 50 Hz software-timed pulse (position changes are rare, one-shot events; a timer channel is not required — **VERIFY** PA24 has no usable timer function on the G351x before deciding to bit-bang) |
| 4 | `FLEX_PWM_IO` | PA25 (TIMA0_C3) | spare | **port door** servo PWM, 50 Hz / 1 000–2 000 µs |
| 5 | `FLEX_BSHOT_IO` | PA26 (TIMG8_C0) | spare | **starboard door** servo PWM |
| 6 | `+5V` | — | **not used for servo power** (D-GW-4) | same |
| 7 | `+3V3` | — | not used | same |
| 8 | `GND` | — | signal reference to the servo harness | same |

Logic level: the MCU is a 3.3 V device. A stock SG90's PWM input is commonly driven at
3.3 V but no SG90 datasheet guarantees it (REF-ACT-003 publishes no input threshold) —
**VERIFY on the bench** with the fallback path, and if marginal, add a single-transistor
level shifter in the harness rather than on the board.

The osc-native bus runs at 0.5–3 Mbaud with hardware CRC both directions
(REF-SENSOR-015) — the CRC is a link-integrity check only; message **authentication** is the
gateway's job (§4).

`J_ENC` is **unused** on this instance (no encoder). `J_SWD` faces aft and is reachable
with the doors open (§5).

---

## 4. Bus role, security, and behaviour

- **Bus position.** CAN-FD and RS-485 daisy-chain IN/OUT (JST-GH 3P ×4) between the chin
  nodes (CN2/CN3, `chin_node_shelf`) forward and the cargo Observer tray aft. Termination
  jumpers `SJ1`/`SJ2` open (D-GW-6).
- **Frames.** Every frame is TPM-signed by the gateway before republication on both
  isolated buses [REF-NIST-001 §2.1], the same pattern as the winch gateway
  (`CARGO_WINCH_SPECIFICATION.md` §5.3):

  | Frame | Rate / trigger | Direction | Payload |
  |---|---|---|---|
  | `DOOR_STATUS` | 5 Hz + on change | gateway → bus | per-servo commanded / reported position (osc-native reports; PWM fallback reports commanded only), servo bus health, release armed/fired flags, rail-present flag |
  | `DOOR_COMMAND` | event | commanding node → gateway | `{port, stbd} ∈ {OPEN, CLOSE, HOLD}`; signed, freshness counter |
  | `RELEASE_COMMAND` | event, **arm + confirm pair** within a window | commanding node → gateway | payload release — its **own** authenticated command class, like the tilt brake release (`TILT_DRIVE_CONTROL_SPEC.md` §5.5, TILT-CTL-09): a MAC failure on a door position frame → hold last valid state; a MAC failure on a release → **do not release** |

- **Interlocks (firmware, gateway-side).** Release is refused unless `DOOR_STATUS` shows
  both doors OPEN; door CLOSE is refused while `WINCH_STATUS` (when the winch gateway is
  present, Phase 7+) reports a line under tension or a payload in the aperture. Bus IDs
  are assigned in firmware, not here.
- **Failsafe.** Loss of bus heartbeat → hold the last commanded positions (never auto-open
  in flight). Loss of the 6 V servo branch → the SG90s are unpowered and the doors are held
  only by the servo gear trains' static friction — **there is no positive door latch in
  the current design** (open item DOOR-LATCH, §8). Loss of `RAIL-2` → the gateway drops
  off the bus; the servos hold whatever pulse they last saw only while the fallback PWM is
  driven, so the commanding node sees the missing heartbeat within one status period.
- **Assurance mapping.** The SG90 door/release endpoint class is already in
  `avionics/WBS.md` U6 ("Fleet host+message authentication wiring for ESC / brushed tilt
  controller / SG90 endpoints"); this document is the endpoint's hardware/behaviour input to
  that `secure-controller-assurance` mapping.
- **Firmware.** AP_Periph-derived image, same licensing note as `CAN-PERIPH-GW-1.md` open
  item 5 (GPLv3 firmware, CC-BY hardware). Adds: osc-native master (or the PWM fallback),
  the three frames above, the interlocks, and the `DOOR-LATCH` state once that exists.

---

## 5. Mechanical — station, tray, clearances

**Where it is (hull frame, mm; X = +port, Y = +aft, Z = +dorsal).** Standing transverse
on the solid 6.2 mm belly slab that the sealed ramp fairing leaves under the chin shelf,
at the forward rim of the clamshell aperture (Y +2):

| Item | X | Y | Z |
|---|---|---|---|
| PCB (49.0 × 25.5 × 1.6) | −194.35..−145.35 (centred X_CL) | −14.5..−12.9 (plane normal to Y) | 15.6..41.1 |
| front components (aft face, ≤ 9 mm — J_FLEX header) | within PCB | −12.9..−3.9 | ≥ 18.1 (2.5 mm bottom-edge exclusion) |
| back components (forward face, ≤ 3 mm — SOIC isolators) | within PCB | −17.5..−14.5 | ≥ 18.1 |
| tray base slab (5.4 mm) | −195.95..−143.75 | −17.25..−2.0 | 10.2..15.6 |
| side rails (1.6 wall + 2 mm lips) | ends | −16.0..−11.4 | 15.6..44.1 |
| 4 shell bosses 7 × 7 mm, M3 heat-set (merged, Rev T5f) | X_CL ± 19 | −13.0 (rear, counterbored under the board) and −6.0 (front, exposed) | 6.2..10.2 (4 mm proud of the slab; pilot 6 mm deep) |

**Measured clearances** (ray probes of the published shell + `cargo_layout_fit.py` boolean,
2026-09-21):

| To | Distance | Budget |
|---|---|---|
| ramp-fairing wall, floor level (Y −20 at Z 8–10) | 2.75 mm (base slab), 2.5 mm (back parts, which start at Z 18 where the wall is at Y −23..−28) | 2.0 static |
| clamshell aperture rim (Y +2) | 4.0 mm (base), 5.9 mm (front parts) | — |
| mission payload box forward face (Y +4.7, hoisted through the aperture) | 8.6 mm to the J_FLEX pins | 2.0 |
| chin node shelf underside (Z 63.6) | 19.5 mm above the rail tops | 2.0 |
| bay side walls at Z 10..40 | ≥ 45 mm half-width vs 26.1 mm tray half-width | 2.0 |
| fore landing-gear bay apertures (sponson, Y −16..20) | outboard of X ±45 — not reached | — |

`tools/cargo_layout_fit.py`: `door gateway tray base / rails / board+parts` = 0 mm³ hit,
0 mm³ inside the 2 mm gap; the four bosses seat on skin (276 mm³ each = the 7 × 7 × 6.2 slab
they stand in — the slab is solid); 0 pair overlaps. The rendered tray booleaned against
the shell and every layout envelope touches only its own board envelope (rail/slot lips) and
its bosses.

**Tray design** (`gateway_door_tray.scad`, Rev T5f): 5.4 mm CF-PETG base slab on the four
bosses; the rear screw row lies under the board's bottom edge so its heads are counterbored
Ø6.0 × 3.2 into the slab top and covered by the removable board (cut the keeper tie, lift
the board, screws exposed); the front row's heads are exposed forward of the rails. Two
side rails with 1.2 mm fore/aft lips over 2 mm of each short edge (slot 2.2 mm = 1.6 board
+ 2 × 0.3) take the board from above; block-top lips locate the bottom edge; a cable tie
through slots in both rail tops keeps the top edge; two more slots in the forward apron take
the servo pigtail bundle. **Host constraint carried to the board:** no part within 2.5 mm of
the two short edges and the bottom long edge, either face. Print: slab flat, rails up, 4
perimeters, 30 % gyroid, CF-PETG. Loads: 0.25 N at 2.5 g on 1.6 × 4.6 mm rails → 2 MPa,
FOS > 20 (header of the SCAD).

**Shell change (Rev T5f, `merge_cargo_interior.py`):** `t5_gw_door_bosses()` — four
7 × 7 mm columns envelope-clipped to the slab + four Ø4.1 pilots 6 mm deep (4 in the boss,
2 in the slab; 4.2 mm of slab left above the skin). The bosses are merged **unclipped** (the slab lies in the ramp void of the outer-skin envelope) and their footprints are carved out of `DUCT_CUT` (which otherwise truncates them at Z 8 — found and fixed 2026-09-21). Shell re-merged: 287.7 cm³ / 302.1 g as-printed (+0.5 g vs Rev T5e), watertight, 1 body; boss tops ray-verified at Z 10.2, pilot floors at Z 4.2.

---

## 6. Wiring

| Run | Cable | Length (est.) | Notes |
|---|---|---|---|
| `J_FLEX` → 3 servo pigtails | 26 AWG 3-core silicone (6 V / GND / SIG or bus) per servo, 1×3 2.54 mm servo plugs; 1×8 2.54 mm crimp housing at `J_FLEX` | 150–250 mm each **VERIFY** once the servos are placed | The door and release servo hull-frame stations are **not yet placed** (`airframe/WBS.md` §1.1.0 VERIFY parts; open item SERVO-PLACE, §8). The pocket beside the tray offers X ±(27..45) at Z ≤ 20, Y −20..0 on both sides. |
| 6 V servo branch | 22 AWG pair from the Flight Engineer 6 V servo rail via a fused tap (`F_DOOR`, 3 A **VERIFY** against the measured stall of three SG90s) | ~600 mm | Joins the pigtail 6 V/GND at a 3-way splice in the tray's apron tie; GND bonded to `J_FLEX` pin 8 at the same splice (single-point reference) |
| `J_PWR` (JST-GH 2P) | +5 V / GND from `RAIL-2 5V_OBS` (`J_OBS`), 0.10 A | ~400 mm | RAIL-2 already runs into the cargo bay for the Observer and the winch gateway (`POWER_DISTRIBUTION.md` §11.1) |
| `J_CAN_IN/OUT`, `J_RS485_IN/OUT` | JST-GH 3P, the trunk daisy chain (CAN FD and RS-485 conduits, `airframe/WBS.md` §2.3) | — | chin nodes → **GW-CARGO-DOOR** → cargo Observer |

All 26 AWG runs are strain-relieved at the apron tie slots; nothing crosses the aperture
plane (Z < 8.7) or the hoist lines.

---

## 7. What changes elsewhere (done in this revision)

| File | Change |
|---|---|
| `tools/cargo_layout_fit.py` | `GW_*` stations, three envelopes + four bosses, `shell_after_merge` subtraction, `--write-scad` export (Rev T5f) |
| `airframe/blender-scripts/merge_cargo_interior.py` | `t5_gw_door_bosses()`; shell re-merged |
| `airframe/openscad/fuselage/cargo/gateway_door_tray.scad` → `airframe/stls/fuselage/cargo/gateway_door_tray.stl` | new part |
| `current-specification/bom_revS.{csv,json}` | `CAN-PERIPH-GW-DOOR` + `PRINT-GW-DOOR-TRAY` added; `SERVO-CARGO` 2 → 3; `DRV8833-CARGO`, `PRINT-DRV8833-TRAY` retired (qty 0) — `tools/bom_edit_door_gateway.py` |
| `docs/POWER_DISTRIBUTION.md` §3.3 | door servo row 1 → 2; gateway 0.10 A on RAIL-2 noted |
| `docs/CARGO_SECTION_LAYOUT.md` §1, §8 | tray row; open items |
| `docs/CARGO_WINCH_SPECIFICATION.md` item 13 | closed by D-GW-1 |
| `avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md` | Deployment 4 (this) and 5 (GW-RCS, Phase 11) |
| `REFERENCES.md` | REF-ACT-003 (TowerPro SG90); REF-SENSOR-015 re-read note; verification rows |
| `airframe/fuselage-mid/WBS.md`, `avionics/WBS.md`, `deferred/WBS.md` → TODOs | items in §8 |

---

## 8. Open items (tracked in the WBS files above)

| ID | Item |
|---|---|
| **GW-DOOR-1** | Build the `N_STACKS=1` instance: confirm the layout to build from (the N=1 backup vs a repack of the live 2-lane board), then ERC/DRC/gerbers under `avionics/WBS.md` U7. |
| **GW-DOOR-2** | OpenServoCore physical layer: read the upstream hardware docs for the osc-native wire level (single-wire half-duplex TTL with a direction line, or full-duplex) and the swap board's logic level; decide whether `FLEX_TTL_GPIO` is the direction line. Re-check the shippable-release gate (REF-SENSOR-015) literally, not from memory. |
| **GW-DOOR-3** | PWM fallback bench test: SG90 input threshold at 3.3 V; PA24 timer capability per SLASFA6B Table 6-2 (bit-bang otherwise); measured stall current of three SG90s → size `F_DOOR`. |
| **GW-DOOR-4 (D-GW-2)** | Owner confirmation that the two independent doors get two actuators (`SERVO-CARGO` qty 3). |
| **SERVO-PLACE** | Hull-frame placement of the three SG90s and their brackets (`cargo_door_servo_bracket.stl`, `cargo_release_servo_bracket.stl` are legacy-frame and unplaced) plus the door bell-crank bosses (`fuselage-mid/WBS.md` §1.1.1.2.1 open item); run them through `cargo_layout_fit.py`. |
| **DOOR-LATCH** | The doors have no positive in-flight latch; retention is servo gear-train friction. Root `AGENTS.md` §7 forbids friction retention on flight-critical joints — decide over-centre linkage vs mechanical latch before first flight with the doors fitted. **Finding, not designed here.** |
| **GW-DOOR-5** | SG90 6 V tolerance: REF-ACT-003 lists 4.8 V only; the servo rail is 6 V (`POWER_DISTRIBUTION.md` §3.3 already assumes SG90s on it). Confirm with the sourced part or feed the branch from 5 V. |
| **GW-DOOR-6** | Weigh the populated gateway board and the tray; replace the 6 g / 5 g estimates and re-run the CG ledger (A0). |
| **GW-DOOR-7** | Firmware: osc-native master / PWM fallback, `DOOR_STATUS` / `DOOR_COMMAND` / `RELEASE_COMMAND`, interlocks, U6 assurance mapping. |

---

## 9. GW-RCS — Phase 11 RCS bleed-valve gateway (SPECIFIED, NOT IMPLEMENTED)

Per `deferred/DEFERRED_ITEM_TEMPLATE.md` fields:

- **Title / revision:** GW-RCS — RCS bleed-valve servo gateway, Rev A concept (2026-09-21).
- **Status:** Phase 11 (deferred with the aft EDF).
- **Scope.** Host the four SG90-class proportional bleed-valve servos (`SERVO-RCS-VALVE`,
  ×4, OpenServoCore per REF-SENSOR-015) that modulate the 4 RCS jets fed by the 55 mm aft
  EDF, as a TPM-signed node on the isolated CAN-FD/RS-485 trunks — replacing the Phase 11
  WBS wording that maps the valves onto FC2's local PWM/mixer, which contradicts
  `avionics/WBS.md` U1 (retire local PWM headers; every actuator is a trunk node).
- **Technical approach.**
  - **Board:** one `SKIPPER-CAN-PERIPH-GW-PCB`. Two configurations, decided by GW-DOOR-2's
    answer: (a) OpenServoCore shippable → `N_STACKS=1`, all four valves on one osc-native
    chain (`FLEX_UART_TX/RX`, IDs 1–4), status chain returns valve position; (b) stock PWM
    → `N_STACKS=2`, `END_TO_END` (≈ 99 × 25.5 mm) — each lane gives two hardware timer
    channels (`FLEX_PWM_IO` PA25 / `FLEX_BSHOT_IO` PA26), four channels total, both lanes
    sharing the bus connectors and buck. RCS valves are **attitude effectors**, so unlike the
    doors they are not one-shot: the command rate is the attitude loop's (≥ 50 Hz), which
    rules out bit-banged channels — hence (b) needs two lanes.
  - **Frames:** `RCS_COMMAND` (≥ 50 Hz, Pilot/FC → gateway, four 0–100 % openings, signed
    with freshness) and `RCS_STATUS` (20 Hz). Latency budget: one CAN-FD frame at 2 Mbit/s
    data phase + TPM-signed republication — **the per-frame signing cost on the MSPM0 hot
    path must be measured** (the OPTIGA Trust M protected-op budget rule in
    `TILT_DRIVE_CONTROL_SPEC.md` §5.5 applies: signing is CMAC on the MCU, never a
    secure-element private-key op per frame).
  - **Failsafe:** heartbeat loss or MAC failure → **all four valves CLOSED** (no bleed, the
    aft EDF's thrust stays axial) — the opposite polarity from the door gateway's hold-last;
    the attitude mixer must treat RCS authority as absent when `RCS_STATUS` stops.
  - **Location:** rear engine cone, Panel F bay, beside the 50 A ESC (`deferred/WBS.md`
    §Phase11 "Install 50A ESC in Panel F bay") — next to the four `rcs_valve_bracket.stl`
    stations so the four pigtails stay short. Tray: a Phase 11 re-parameterisation of
    `gateway_door_tray.scad` (`GW_PCB_L` → the N=2 length; the rail/slot design is unchanged)
    on bosses to be cut into the rear-cone shell when Phase 11 resumes (the rear section's
    Blender source still carries MESH-01 and cannot be regenerated yet — `airframe/WBS.md`
    §1.1.0).
  - **Power:** `J_PWR` from the aft 5 V avionics feed that reaches Simon's / the aft ESC
    bay; valve servos on a fused branch of the 6 V servo rail (4 × SG90, `POWER_DISTRIBUTION.md`
    §3.3 already budgets them at 700 mA stall each). Trunk extension: the CAN-FD and RS-485
    daisy chains continue aft through the middle inner neck (`airframe/WBS.md` §2.3 conduits).
- **Dependencies.** Phase 11 aft-EDF hardware (plenum bleed taps, `rcs_valve_bracket.stl`
  ×4, manifold); GW-DOOR-2 (OpenServoCore physical layer / maturity) to pick (a) or (b);
  rear-cone shell regeneration (MESH-01) for the tray bosses; `avionics/WBS.md` U1/U6.
- **Blockers / risks.** Per-frame signing latency vs attitude-loop rate (measure on the
  door gateway first — it is the same MCU/TPM); RCS valve dynamics unknown (SG90 0.1 s/60°
  at 4.8 V, REF-ACT-003) — the attitude loop's phase margin with a ~100 ms actuator is a
  control-systems question to answer before the mixer is written.
- **Estimated effort.** Board instance: reuse (0 new design, one generator run + tray
  re-parameterisation); firmware: `RCS_COMMAND/STATUS` + fail-closed — comparable to the
  door gateway's; integration: Phase 11 bench items already listed in `deferred/WBS.md`.
- **Integration date:** Phase 11.
- **Owner / next reviewer:** Steve Griffing, PE(CSE) — with the aft-EDF phase.
- **Mass (Phase 11 budget):** ~6 g (N=1) or ~10 g (N=2) board + ~7 g tray + ~10 g harness
  ≈ +23 g (0.051 lbm) at the rear cone — add to the Phase 11 "~127 g" rear-propulsion line
  in the root `WBS.md` overview table when the phase is re-baselined.

---

## 10. References

- `avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md` — board, `J_FLEX`, `N_STACKS`, retarget pin table
- `docs/CARGO_WINCH_SPECIFICATION.md` §5 — the winch gateway (why the doors need their own)
- `docs/CARGO_SECTION_LAYOUT.md` — Rev T5e/T5f cargo layout; `tools/cargo_layout_fit.py`
- `docs/TILT_DRIVE_CONTROL_SPEC.md` §5.5 — arm/confirm command-class pattern
- `docs/POWER_DISTRIBUTION.md` §3.3 (6 V servo rail), §11.1 (RAIL-2)
- `REFERENCES.md`: REF-ACT-003 (TowerPro SG90), REF-SENSOR-015 (OpenServoCore), REF-SENSOR-017
  (MSPM0G351x-Q1), REF-SENSOR-009/-010 (ISOW1044/ISOW1412), REF-SEC-002 (SLB9672),
  REF-NIST-001 §2.1 (signed messages), REF-ISA-001 (command authenticity as a design input),
  REF-TIA-001 (RS-485), REF-ISO-001 (CAN)
- `deferred/WBS.md` §Phase11, `deferred/DEFERRED_ITEM_TEMPLATE.md`
