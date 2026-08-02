# Cargo Winch — Motor, Ratchet and Spool Support Specification

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**Drafted by:** Claude Haiku 4.5 (Anthropic), 2026-07-27
**Rev C drafted by:** Claude Sonnet 5 (Anthropic), 2026-08-02
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0
**Revision:** C (2026-08-02)
**Supersedes:** the Rev P/Q/R N20 winch train (see "Superseded Hardware" below); Rev C
additionally supersedes Rev B's servo selection (STS3215 → SPT5425LV + LibreServo v2)

> **Rev C replaces the winch's servo — STS3215 → SPT5425LV + LibreServo v2 —
> as part of a fleet-wide standardisation across all three high-torque servos on
> the airframe** (this winch, plus the 2× nacelle tilt servos, previously
> DS3218MG). See §3.1/§3.1.1/§3.9/§5.1/§6/§7 below for what changed and why;
> everything else in Rev B (spool support architecture, ratchet, line-shed,
> containment) is carried forward unchanged. See
> `REFERENCES.md` "Servo Fleet Standardisation, 2026-08-02" for the fleet-wide
> rationale and REF-SENSOR-013/014/015 for the individual part records.

> **Rev B corrects four substantive errors in Rev A** (same date, first pass):
> Rev A specified PWM servo control (the STS3215 is a **TTL serial-bus** servo);
> invented a 50 lbf design load and 0.25 in line against the airframe's real
> 3.92 N payload load and 0.5 mm Dyneema; described the ratchet as a
> **bidirectional** lock when the requirement is a **one-way** ratchet
> (retract-free, pay-out-locked); and specified the line as permanently anchored
> to the spool, which directly contradicts the line-shed requirement. Rev A
> should not be used.

---

## 1. Scope and Requirements

Ten requirements drive this revision:

| # | Requirement | Where satisfied |
|---|---|---|
| R1 | Cargo winch motor is a **SPT5425LV servo converted with LibreServo v2** (Rev C; was STS3215 under Rev B) | §3.1 |
| R2 | **Normally-engaged** safety ratchet on the spool | §3.4 |
| R3 | Spool supported at **both ends**, not cantilevered on the motor axle | §3.2 |
| R4 | No power → spool may **retract**; power required to retract the catch and permit **pay-out** | §3.4, §5.2 |
| R5 | Line force above max available lift → **slow unwind, line runs off the spool** so the UAV cannot be fouled | §3.6, §4.3 |
| R6 | One **CAN-PERIPH-GW** (`N_STACKS=1`) drives both the servo and the catch | §5 |
| R7 | **Spool position reported to the aircraft throughout pay-out and shed**, until the line departs | §3.7 |
| R8 | Overload sacrifices a **cheap printed part**, never the servo | §3.8 |
| R9 | Servo operating mode suits multi-turn travel **and** a slipping spool | §3.9 |
| R10 | **The spool can never leave the cargo bay.** No failure — including its own designed wear — may release it as a projectile | §3.10 |

*"Everything is shiny." — Flight Engineer Frye*

---

## 2. Superseded Hardware

The Rev P/Q/R cargo winch train is retired in full. Every item below is removed
from the active BOM and must not be carried into the next letter revision.

| Superseded item | Rev P/Q/R definition | Why it is retired |
|---|---|---|
| **N20 300RPM 6V gearmotor** (`N20-WINCH`) | Brushed gearmotor, 3 mm D-shaft | Replaced by STS3215 (R1). Open-loop brushed motor with no position feedback and no bus interface. |
| **`cargo_winch_motor_mount.stl`** | CF-PETG U-channel, 36 × 28 × 15 mm, 25 g; zip-tie motor retention; 4× M2 self-tap into gondola ceiling | **Cantilever mount** — its docstring states "spool on motor output shaft hangs into gondola interior below the bracket." Directly violates R3. |
| **`cargo_winch_spool.stl`** | PETG, core OD 20 mm, flange OD 26 mm, 22 mm wide, 15 g; **3.15 mm D-bore for the N20 shaft**; M2 set-screw; **tangential Dyneema anchor slot** | Bore and set-screw exist only to hang the spool off the N20 shaft (violates R3); the anchor slot permanently ties the line to the spool (violates R5). |
| **DRV8833 as winch driver** | Dual H-bridge, 1.5 A/ch | The STS3215 is a bus servo with an integrated driver — no external H-bridge. **See note below.** |

> **DRV8833 scope note.** `cargo_drv8833_tray.stl` and `DRV8833-CARGO` are **not**
> deleted by this change. The Rev R BOM assigns both DRV8833 channels to the
> **door** and **payload-release** SG90 servos (Ch-A / Ch-B), not to the winch.
> Only the winch's dependency on it is removed. Consolidating the door and
> release servos onto the same CAN-PERIPH-GW is plausible (its `J_FLEX` header
> exposes a spare `FLEX_PWM_IO`) but is **out of scope here** and is filed as an
> open item in `airframe/fuselage-mid/WBS.md`.

**Retained unchanged:** `DYNEEMA-SK75` (0.5 mm braid × 2 m, ~300 N break,
60 N WLL) and `HX711-LC` (24-bit tension ADC). Both are re-hosted onto the
gateway rather than Cape-B — see §5.

### 2.1 Why the cantilever fails, numerically

The retired mount hangs the 22 mm-wide spool off the N20's 3 mm output shaft,
placing the line load ~11 mm outboard of the gearbox bushing face:

```
M_bushing = F_line × 11 mm = 8.0 N × 0.011 m = 0.088 N·m
```

The 3 mm shaft itself survives this (σ = Mc/I = 88 × 1.5 / 3.976 = **33 MPa**),
but the load path terminates in the N20's sintered-bronze output bushing, which
is a locating bushing, not a load-bearing journal. Under the 2.5 g dynamic
factor this document uses for cargo events (`docs/structural_analysis.md` §6
landing-impact convention) the side load reaches **20 N at 11 mm**, and the
failure mode is bushing wear and output-shaft bind — a jammed winch with a
payload hanging under the aircraft. This is the concrete reason R3 exists.

---

## 3. Mechanical Design

### 3.1 Motor — SPT5425LV + LibreServo v2 (Rev C; supersedes the Rev B STS3215 selection)

**Rev C change.** The winch servo is now an **SPT5425LV** standard hobby servo body
with its factory control PCB replaced by **LibreServo v2** (the
`stab-rabbit-coding` fork), converting it into a serial-bus servo with a 360°
absolute magnetic position sensor. This is one of the three high-torque servos
on the airframe (the other two are the nacelle tilt servos, also converted —
`REFERENCES.md` "Servo Fleet Standardisation, 2026-08-02"), standardised onto
one physical servo/board combination. Unlike the STS3215 it replaces, the
SPT5425LV + LibreServo v2 combination has **published, sourced specifications**
(REF-SENSOR-013/014) — the STS3215's never-resolved scanned-PDF datasheet gate
does not carry forward.

| Parameter | Value | Provenance |
|---|---|---|
| Servo body | SPT5425LV (Shantou SiPaiTe / "SPT Servo") | REF-SENSOR-013 |
| Control board | LibreServo v2 (`stab-rabbit-coding` fork), <https://github.com/Stab-Rabbit-coding/LibreServo_v2> | REF-SENSOR-014 |
| Mechanical mod | Internal rotation-limiting pin **removed** — §3.1.2 | REF-SENSOR-013 |
| Interface | **RS-485 half-duplex serial bus**, daisy-chainable, CRC-16 | §3.1.1 |
| Supply | LibreServo v2 accepts 4.5–18 V (recommended 5–14 V); driven at 5.4 V nominal from Flight Engineer RAIL-2 `5V_JAYNE`, unchanged from Rev B | `docs/POWER_DISTRIBUTION.md` §3.2.1; REF-SENSOR-014 |
| Stall torque (servo body, native) | 24 kgf·cm (2.35 N·m) @ 4.8 V, 26 kgf·cm (2.55 N·m) @ 6.0 V | REF-SENSOR-013 — comfortably clears the §4.2 requirement below |
| Mass | ~57 g (servo body) + LibreServo v2 PCB (not separately published; treat as included in the ~57 g class figure pending a bench weigh-in) | REF-SENSOR-013 |
| Case envelope | 40.5 × 20 × 40.5 mm | REF-SENSOR-013 — resolves the §3.3 `PEDESTAL_PORT` case-envelope gate that blocked pedestal generation under Rev B |
| **Required** output torque | **≥ 3.2 kgf·cm (0.31 N·m)** at the coupler (unchanged) | Derived, §4.2 |
| **Required** side load on output | **0 N** — see §3.3 (unchanged) | Derived, R3 |
| **⚠ Not yet verified** | Stall/running current at 5.4 V (needed to finalize the §5.4 RAIL-2 budget) and the exact pin-removal procedure (§3.1.2) — neither figure is published by the sources above | REFERENCES.md "Open Standards Verification Items" |

> **Gate resolved, one gate remains.** Rev B's blocking issue was the STS3215's
> unreadable scanned datasheet — case envelope, torque, mass and stall current
> were all unverifiable. The SPT5425LV's envelope, stall torque and mass are
> published on the manufacturer's own product page and an independent servo
> database (REF-SENSOR-013), which **unblocks pedestal/mounting-hardware
> generation** (§3.3). Stall current is still not published anywhere sourced,
> so the RAIL-2 budget in §5.4 below carries the old STS3215-era 1.2 A figure
> forward as a placeholder — bench-measure before final sizing. Per root
> `AGENTS.md` §4, this is logged in `REFERENCES.md` REF-SENSOR-013 and the Open
> Standards Verification Items table. **Do not fabricate the current figure.**

#### 3.1.1 Interface — RS-485 differential serial bus, not single-wire TTL

LibreServo v2's daisy-chain bus is **genuine differential RS-485** (an A/B
pair driven by an onboard transceiver — SIT3485 on the shipped v2.3.1 board,
being upgraded upstream to an isolated ADM2587E), at up to 9 Mbps with CRC-16
framing. This is a materially different electrical scheme from the STS3215's
**single-wire half-duplex TTL** bus that Rev B designed around, and it changes
the electrical integration story in §5.1 below:

- Rev B's plan reused `CAN-PERIPH-GW-1`'s `J_FLEX.FLEX_TTL_GPIO` — a single
  bidirectional MCU GPIO pin — with an open item to add direction-steering
  hardware for the STS3215's single-wire half-duplex protocol (§5.1.1, now
  historical).
- Rev C's SPT5425LV/LibreServo v2 servo instead needs a true differential
  RS-485 link. `J_FLEX` exposes a bare `FLEX_UART_TX/RX` pair but **no RS-485
  transceiver of its own for this local servo drop** — the gateway's onboard
  ISOW1412 (`RS485_A`/`RS485_B`) is dedicated to the board's own isolated
  uplink trunk to Pilot/XO, not intended as a shared local servo sub-bus
  without further isolation/topology review.
- **This is an open item, not resolved here** — see §5.1 and
  `REFERENCES.md` "Open Standards Verification Items" ("LibreServo v2 fork —
  RS-485 differential bus electrical integration").

#### 3.1.2 Mechanical mod — rotation-limiting pin removed for continuous rotation

Like most analog/digital hobby servos, the SPT5425LV's output gear/potentiometer
assembly includes a small internal mechanical stop that limits the output shaft
to roughly one physical turn, matched to the servo's stock potentiometer. This
is the "rotation blocking pin" the migration removes. Two things make removal
safe here, where it would not be on an un-converted servo:

1. **LibreServo v2 replaces the potentiometer with a 360° absolute magnetic
   encoder** (AEAT-8800, 16-bit) — the pin's only job, protecting the
   potentiometer wiper from over-travel, no longer applies once the
   potentiometer itself is gone.
2. **Position feedback and range limiting move from mechanical to firmware.**
   With the pin removed the servo can rotate continuously; whether a given
   installation actually *uses* that continuous range is a firmware/mode
   choice, not a hardware one (§3.9 for the winch's own mode).

The same physical mod is applied to all three high-torque servos for
commonality (one spare part, one firmware image with per-application
configuration) — see `REFERENCES.md` "Servo Fleet Standardisation,
2026-08-02" for why this is safe for the nacelle-tilt application too (its
real range limit is the external CF-PETG hard-stop blocks in the gear train,
not the servo's own internal pin).

**⚠ Not yet verified:** the exact pin location and removal procedure for this
specific part number. "Remove the limit pin/tab for continuous rotation" is a
well-documented technique on hobby servos generally, but has not been
confirmed by teardown of an actual SPT5425LV unit. Document the verified
procedure (with photos) in `graphical-build-guide/` before it is added to the
build guide as a build step — do not assume it matches a different
manufacturer's servo internals.

### 3.2 Spool support architecture — supported at both ends (R3)

The load path no longer passes through the motor at all. The spool rotates on
**two bearings carried inside its own hub**, riding on a **fixed** axle that is
clamped at **both** pedestals:

```text
        PORT pedestal                                  STBD pedestal
   (bearing seat + SPT5425LV/LS2)                (bearing seat + pawl + solenoid)
              │                                            │
      ┌───────┴────────┐                          ┌────────┴────────┐
      │  axle clamp    │                          │   axle clamp    │
      │   ┌────────────┼──── Ø4 mm FIXED AXLE ────┼────────────┐    │
      │   │            │                          │            │    │
      │   │      ╔═════╧═══════════════════════════╧═════╗     │    │
      │   │      ║  MR84ZZ │      SPOOL      │  MR84ZZ  ║     │    │
      │   │      ╚═════╤═══════════════════════════╤═════╝     │    │
      │   │            │        ▲                  │  ▲        │    │
      └───┼────────────┘        │                  │  │        │    │
          │                  Dyneema            ratchet ring   │    │
 SPT5425LV/LS2 ─dog coupler──►  line             (24 sawtooth)  │    │
     (torque only,            pays out              ▲         pawl  │
      no radial load)                               └──────────┘    │
```

- **Axle:** Ø4 mm × 46 mm, A2/304 stainless, **stationary** (does not rotate).
  Clamped in a split-collar seat in each pedestal with one M3 pinch screw.
- **Bearings:** 2× MR84ZZ (4 × 8 × 3 mm), pressed into counterbores in the
  spool's two flange hubs — one at each end of the drum, so the line load is
  reacted symmetrically.
- **Drive:** the SPT5425LV (LibreServo v2-converted) transmits **torque only**
  through a lost-motion dog coupler (§3.3). No radial or moment load reaches
  the servo output spline.
  The coupler isolates the servo from *radial* load but **not** from spool
  *rotation* — see §3.7, which is the governing constraint on whether the
  powerless shed works at all.

Choosing a *fixed* axle with bearings inside the spool (rather than a rotating
axle in pedestal bearings) removes the rotating-shaft-to-pedestal interface
entirely, halves the bearing count, and lets the pedestals be simple clamped
seats.

### 3.3 New printed parts

All CF-PETG unless noted; 0.15 mm layers, 4 perimeters, 40 % gyroid infill
(root `AGENTS.md` §7). Load-bearing joints carry a 2-wall contact annulus and a
positive-stop shoulder — no friction-only fits.

| Part (new STL) | Material | Mass | Function |
|---|---|---|---|
| `cargo_winch_pedestal_port.stl` | CF-PETG | 18 g | Port axle clamp + bearing seat + **SPT5425LV case cradle**, 40.5×20×40.5 mm envelope (REF-SENSOR-013 — resolves the §3.1 case-envelope gate) |
| `cargo_winch_pedestal_stbd.stl` | CF-PETG | 20 g | Stbd axle clamp + bearing seat + pawl pivot boss + solenoid mount + spring seat |
| `cargo_winch_spool_r2.stl` | **CF-PETG** (was PETG) | 16 g | Drum + twin bearing counterbores + **integral ratchet ring**; **no anchor slot** |
| `cargo_winch_pawl.stl` | CF-PETG | 2 g | Sawtooth pawl lever |
| `cargo_winch_dog_coupler.stl` | CF-PETG | 3 g | Lost-motion servo→spool dog; isolates servo from radial load |
| `cargo_winch_fairlead.stl` | PETG | 3 g | Line exit guide, 10 mm throat radius; keeps a shed line clear of the flange |

**Spool geometry** (carried forward from the retired spool where still valid):
core OD 20 mm, usable drum width 18 mm, flanges OD 26 mm × 2 mm. Line capacity
is unchanged — 1500 mm at 0.55 mm pitch ≈ 24 turns ≈ 13.2 mm of the 18 mm
usable width. Changes: material PETG → **CF-PETG** (the hub now carries pressed
bearing races); D-bore + M2 set-screw **deleted**; twin Ø8 mm × 3 mm bearing
counterbores **added**; Ø30 mm × 3 mm ratchet ring **added** to the outboard
starboard flange face; tangential anchor slot **deleted** (R5, §3.6).

### 3.4 Safety ratchet — normally engaged, one-way (R2, R4)

The ratchet is a **one-way** device, not a lock. Its default state permits
retraction and blocks pay-out:

| State | Power | Retract (wind in) | Pay out (unwind) |
|---|---|---|---|
| **Engaged** (default) | none | **Permitted** — pawl ratchets over the ramp faces | **Blocked** — pawl seats on the locking faces |
| **Retracted** | solenoid energised | Permitted | Permitted |

This is exactly R4: *without power the spool can retract, but power is required
to retract the catch to allow the spool to unwind.*

**Ratchet ring** — integral with the starboard spool flange:

| Parameter | Value |
|---|---|
| Outside diameter | 30.0 mm (pitch radius 15.0 mm) |
| Teeth | 24 (15.0° pitch) |
| Face width | 3.0 mm |
| Tooth height | 2.0 mm |
| **Wind-in (ramp) face** | 30° from tangent — pawl rides over and clicks |
| **Pay-out (locking) face** | **8° undercut from radial** — locks below the slip threshold, cams the pawl out above it (§3.6) |

**Pawl** — CF-PETG lever on an M2 × 10 mm A2 stainless dowel in the starboard
pedestal; 18 mm from pivot to tooth contact; spring seat at 15 mm from pivot.

**Spring** — compression, **1.0 N ± 0.2 N at installed length**, stainless
(corrosion + the 500 W/m² RF environment of root `AGENTS.md` §1). Seated against
a **set-screw-adjustable** seat in the starboard pedestal so the slip threshold
can be trimmed on the bench, because printed-part friction cannot be predicted
closer than about ±30 %.

### 3.5 Catch actuator — fail-safe by construction

| Parameter | Value |
|---|---|
| Type | Pull-type linear solenoid |
| Supply | 5.4 V (RAIL-2), ~200 mA hold ⇒ ~1.1 W **only while paying out** |
| Stroke | ≥ 3.0 mm |
| **Required** pull | **≥ 2.5 N at 3 mm** (2.5× the 1.0 N spring) |
| De-energised | Spring drives the pawl **into** engagement |

A solenoid is chosen over a second servo because de-energised means *engaged*
with no firmware involvement — the failure state is the safe state. (A limp
servo back-driven by the pawl spring would also work, but depends on the servo
being genuinely free when unpowered, which is a weaker guarantee.)

### 3.6 Overload line-shed (R5)

Two independent mechanisms, per the redundancy requirement of root `AGENTS.md`
§1 — one mechanical and powerless, one sensed:

**(a) Mechanical slip — primary, works with no power.** The 8° undercut on the
locking face converts excess tangential tooth force into a radial component that
cams the pawl out against its spring. The spool then ratchets backwards under
load: it **pays out slowly**, one tooth click at a time, rather than releasing
in free-fall.

**(b) Sensed shed — secondary.** The retained HX711 load cell reports line
tension to the gateway; above threshold the gateway energises the solenoid and
commands a de-rated pay-out (§5.3). This is the graceful path and it produces
telemetry; (a) is what protects the aircraft when power or firmware is gone.

**Line runs off the spool.** The Dyneema anchor slot is **deleted**. The inboard
end is whipped and heat-sealed and laid in a shallow tangential relief, retained
by wrap friction alone. Capstan holding force on the last two turns:

```
F_hold = F_tail · e^(µθ),  µ ≈ 0.1 (Dyneema on PETG),  θ = 2 turns = 4π rad
F_hold ≈ 0.2 N × e^(0.1 × 12.57) = 0.2 × 3.51 ≈ 0.7 N
```

0.7 N is far below the 8.0 N slip threshold, so once the spool has paid out to
its last turns the line **pulls free of the drum entirely** and falls away. The
`cargo_winch_fairlead.stl` throat keeps the freed end from wedging between
flange and pedestal on its way out.

### 3.7 Spool position sensing, and the servo back-drive problem (R7)

**The question this section answers:** during an overload shed, does the servo
turn as the line pays out, and can its encoder keep reporting spool position?

**Under the Rev B coupling, yes — but that answer is load-bearing in a way Rev B
did not acknowledge, and it is conditional on something not yet verified.**
The dog coupler's lost motion is only a few degrees of dead band; once taken up,
the spool bears on the servo dog and back-drives it. Servo and spool are rigidly
coupled for all but that dead band, in both directions. So the spool cannot pay
out *unless* it can turn the servo's gear train.

#### 3.7.1 Back-drive is in series with the safety threshold

The shed threshold is not set by the pawl alone. The spool must overcome the
pawl cam-out **and** the servo's back-drive resistance:

```
F_shed = ( T_pawl + T_backdrive ) / r_line
```

`T_backdrive` is unknown, and the budget for it is brutally small. §3.6 sets the
threshold at 8.0 N with a bench-calibration tolerance of ±1.0 N. At
r_line = 10.3 mm that entire tolerance is:

```
±1.0 N × 0.0103 m = ±0.0103 N·m = ±0.105 kgf·cm
```

**0.105 kgf·cm is the whole error budget.** A high-ratio geared servo of the
SPT5425LV's 25 kgf·cm class will typically resist back-drive by *several*
kgf·cm — one to two orders of magnitude more. If that holds here, then:

- the ratchet cams out at 8.0 N exactly as designed, **and the spool still does
  not turn**, because the servo gearbox holds it;
- the powerless mechanical shed (§3.6a) — the path that exists precisely for
  when power and firmware are gone — **does not function at all**;
- worse, `T_backdrive` varies with temperature, wear and lubricant, so even if
  shed does occur the threshold is not repeatable, which is unacceptable for a
  safety function whose whole purpose is a predictable release point.

This was the top open item as written. **§3.8 supersedes it:** moving the torque
limiter into the printed spool hub lets the spool break free of the servo
entirely at overload, so `T_backdrive` drops out of `F_shed`. What remains is
the far weaker requirement `T_slip < T_backdrive` — and a *stiffer* servo makes
that easier to satisfy, not harder. `T_backdrive` should still be measured
(pawl held clear, tangential load at the spool, record the torque that turns the
unpowered servo), but to **confirm an inequality**, not to decide whether R5 can
be met at all.

#### 3.7.2 Three couplings, and why the servo encoder cannot be the answer

| Coupling | Normal lowering | Powerless shed | Servo encoder during shed |
|---|---|---|---|
| **(A) Rigid dog** (Rev B as written) | Servo controls descent ✓ | **Only if back-drivable** — threshold polluted by `T_backdrive` | Tracks ✓ |
| **(B) Torque-limiting slip clutch** above working torque, below overload | Servo controls descent ✓ | Clean — `T_backdrive` out of the equation ✓ | **Does not track** ✗ (servo stays put) |
| **(C) Overrunning one-way clutch** | **Broken** ✗ — servo could never pay out under control | Clean ✓ | Does not track ✗ |

(C) is rejected outright: it would make controlled lowering impossible.
**§3.8 selects (B)** and locates the clutch in the printed spool hub, which is
why the "does not track" column costs nothing — the AK7455 is on the spool
(§3.7.3) and reads true angle through any slip. The trade is closed; no
`T_backdrive` measurement is needed to decide it.

Two further defects apply to the servo encoder **even in case (A)**, where it
does rotate:

1. **It wraps.** Paying out 1500 mm at r = 10.3 mm is **23.2 spool turns**. A
   single-turn absolute servo encoder wraps ~23 times, so it reports angle, not
   position, without firmware turn-accumulation.
2. **It can be outrun.** If a snag releases, the payload approaches free fall:
   over 1.5 m that is 5.4 m/s, **527 rad/s ≈ 5,030 rpm** at the spool. Nyquist
   alone needs > 168 samples/s; reliable wrap-counting needs **≥ 840 Hz**
   (10 samples/rev). Above that the accumulated turn count is simply wrong.

And the case the mechanical shed exists for — **total power loss — has no
telemetry at all.** No power, no encoder, no gateway, no CAN frame. Encoder
coverage applies to the *powered* overload path (§3.6b) only. Nothing reports
spool position during a powerless shed, by construction.

#### 3.7.3 Resolution — sense the spool, not the servo

Spool position is measured **directly at the spool**, independent of the servo
and of whichever coupling §3.7.1 resolves to:

| Parameter | Value |
|---|---|
| Sensor | **AKM AK7455** off-axis magnetic angle sensor [REF-SENSOR-008] |
| Why this part | Already fleet-standard for nacelle tilt; clean-room symbol and footprint exist; **no new part number** |
| Interface | SPI → the gateway's **existing `J_ENC`** 7-pad header, on a dedicated SPI bus separate from the TPM's — **no board change** |
| Target | Diametric magnet in a pocket in the port spool flange hub, off-axis (the axle is fixed and occupies the centreline) |
| Sample rate | **≥ 1 kHz** (covers the 840 Hz wrap-tracking floor with margin) |
| Multi-turn | Accumulated in gateway firmware; `turns` invalidated, not guessed, if `|Δθ|` between samples exceeds half a revolution |

This satisfies R7 in every branch of the §3.7.2 trade: whether the coupler ends
up rigid (A) or slipping (B), the aircraft is told the true spool angle for as
long as it has power. The servo's own encoder becomes a cross-check — a
divergence between servo angle and AK7455 angle is a direct, and useful,
indication that a slip clutch has slipped or a dog has stripped.

*"Takes a mechanic to tell you the wheel's turning. Takes a good one to tell you
it isn't."*

### 3.8 The slip interface belongs in the printed spool (R8)

Two observations reshape §3.7's trade, and they compound:

> *"If the spool is slipping on the shaft, it's moot."*
> *"In a failure mode, it's easier to replace a printed spool than a digital servo."*

Both are correct, and together they say the torque limiter should not be a
separate component at all — **it should be the spool's own hub interface**, with
the printed spool as the deliberate sacrificial element.

#### 3.8.1 What this fixes

**It removes `T_backdrive` from the shed equation entirely.** §3.7.1 made
back-drive a go/no-go on R5 because the spool had to turn the servo gearbox to
pay out. With a slip interface in the hub, once the pawl cams out the spool
breaks its drive coupling and **spins free of the servo**, whatever the gearbox
does. The shed threshold becomes:

```
F_shed = T_pawl / r_line          (T_backdrive no longer appears)
```

provided only that `T_slip < T_backdrive`. **A stiff, non-back-drivable servo
stops being a hazard and becomes irrelevant** — arguably a benefit, since it
holds position without drawing current. This inverts §3.7.1 from a go/no-go into
a one-line inequality to confirm.

**It puts the wear where it is cheap.** The sacrificial element is a ~16 g
printed CF-PETG part on a shelf, not a bus servo with a gearbox and electronics.
A shed event, or a jam that would otherwise strip gear teeth or stall the motor,
consumes spool life instead. Replacement is a hand-tool operation per root
`AGENTS.md` §7.

**And it keeps position telemetry honest.** The AK7455 magnet is in the spool
flange (§3.7.3), so it reads **true spool angle through any amount of slip**.
Had the magnet been on the drive side, slip would have silently corrupted it.

#### 3.8.2 Design

| Parameter | Value |
|---|---|
| Type | Friction slipper — spool hub clamped to the drive plate by a Belleville washer on a threaded collar |
| Why friction, not shear-pin or detent | **Self-resetting** (a shed event must not ground the aircraft), continuously adjustable, and quiet — a ball-detent would ratchet audibly and pit the printed hub |
| **`T_slip`** | **0.060 N·m (0.61 kgf·cm)** — 1.49× static payload torque, 73 % of the shed torque |
| Adjustment | Threaded collar, torque-wrench set, then thread-locked and witness-marked |
| Required | **`T_slip` < `T_backdrive`** — the one inequality left from §3.7.1 |
| Wear surface | Printed CF-PETG hub against a steel drive plate; hub is the consumable |

The window is bounded on both sides and is not wide:

```
must NOT slip in normal lifting : T > 0.0404 N·m (0.41 kgf·cm) at 3.92 N payload
must     slip at the shed point : T < 0.0824 N·m (0.84 kgf·cm) at 8.0 N
chosen                          : T_slip = 0.060 N·m, mid-window
```

#### 3.8.3 Four-layer protection hierarchy

Each layer is cheaper to consume than the one below it:

| # | Layer | Set at | Protects |
|---|---|---|---|
| 1 | Servo torque limit (firmware) | below `T_slip` | the printed hub, from routine wear |
| 2 | **Slip interface (printed spool hub)** | **0.060 N·m** | the servo gearbox |
| 3 | Pawl cam-out (ratchet) | 0.0824 N·m ⇒ 8.0 N line | the aircraft — this is the shed |
| 4 | Line break (Dyneema SK75) | ~300 N | nothing; it is the last resort |

Layer 1 matters: with the servo's own torque ceiling set below `T_slip`, ordinary
operation never reaches the friction interface, so the sacrificial part is
consumed only by genuine overload events rather than by every lift.

### 3.9 Servo operating mode (R9) — Rev C: continuous rotation by construction, not by register

**Rev B context (historical).** The STS3215 exposed position/servo, stepper,
and encoded-continuous-rotation as **register-selected modes** on otherwise
identical hardware, and Rev B selected encoded continuous rotation.

**Rev C.** SPT5425LV + LibreServo v2 does not have a mode register in the same
sense — with the rotation-limiting pin physically removed (§3.1.2) and the
stock potentiometer replaced by the AEAT-8800 360° absolute magnetic encoder,
the servo is a continuous-rotation actuator **by construction**, not by a
selectable mode. The same three failure modes Rev B rejected the other two
STS3215 modes for still apply, so the winch's control architecture is
unchanged in substance — only the mechanism by which continuous rotation is
achieved has changed:

| Requirement | Why it still holds under LibreServo v2 |
|---|---|
| Must express 23.2 spool turns (§3.7.2) | The physical rotation limit is gone (§3.1.2); LibreServo's own position tracking is continuous relative to its own boot reference, not single-turn absolute — firmware still must not rely on the servo's own turn count as spool position |
| Must not go fictional after a hub slip (§3.8) | Unchanged reasoning: whatever the servo reports about its own shaft position, only the **AK7455 on the spool itself** reads true spool angle through a slip (§3.7.3) — the servo's own sensor is a cross-check, never authoritative, exactly as under Rev B |
| Needs closed-loop *speed* control + a settable torque ceiling (protection layer 1, §3.8.3) | LibreServo v2 "generates their own curves (sine ramps, trapezoidal ramps, hermitian curves...)" and has current sensing (ACS711, ±15 A) on-board — rate/torque commanding is a firmware-protocol question for the winch state machine (`avionics/firmware/WBS.md`), not resolved here |

The cascaded-loop architecture is unchanged: outer position on true spool
angle (AK7455), inner rate/torque in the servo. Degradation is unchanged too —
if the AK7455 fails, the winch still has commanded-rate control and the
ratchet still protects the aircraft; it simply loses payload-height readout
(`encoder_fail`, §5.3).

**⚠ Open item.** LibreServo v2's own wire protocol (`LibreServo Commands`,
linked from REF-SENSOR-014) has not yet been reviewed against the winch state
machine's requirements (rate command, torque-ceiling set, position readback).
This replaces Rev B's "confirm STS3215 mode indices/register" open item —
same category of gap, different part. Do not invent LibreServo command/register
values here; read them from the protocol documentation linked in REF-SENSOR-014
when the firmware task starts.

> **⚠ Mode semantics are part of the §3.1 datasheet gate.** The three modes are
> as described by the user; exact mode indices, the register that selects them,
> and whether the torque ceiling is settable per-mode are **not** verified here
> and must be read off the datasheet before firmware is written. No register
> number is invented in this document.

### 3.10 Containment — the sacrificial spool must never become a projectile (R10)

**§3.8 created this hazard and did not address it.** Designating the spool as the
sacrificial element means planning for it to degrade in service. A wear item
directly above clamshell doors that open 180° to free air must therefore be
*positively captive*, and Rev B's retention was not.

#### 3.10.1 The defect this exposes

§3.2 retains the axle with "a split-collar seat in each pedestal with one M3
pinch screw." **That is friction retention**, and root `AGENTS.md` §7 is explicit:

> *"Load-bearing mating joints require a minimum 2-wall contact annulus **and** a
> positive-stop shoulder — friction fit alone is never acceptable for a
> flight-critical joint."*

A pinch collar carrying the entire spool assembly over an open cargo bay is a
flight-critical joint by any reading. This is a self-inflicted violation, not an
inherited one, and it is corrected below.

#### 3.10.2 What is at stake

At the §107.51(b) ceiling of 400 ft AGL [REF-FAA-002], ignoring drag (an upper
bound — drag reduces it):

| Released | Mass | Impact speed | Kinetic energy |
|---|---|---|---|
| Spool alone | 16 g | 48.9 m/s | **19.1 J (14.1 ft·lbf)** |
| Full assembly (spool + bearings + axle + line) | 26.6 g | 48.9 m/s | **31.8 J (23.5 ft·lbf)** |

These are engineering magnitudes, not a compliance claim — see the verification
item in §8 for the dropped-object regulation, whose section number is **not**
asserted here because it is not yet verified in `REFERENCES.md`.

#### 3.10.3 Failure modes and positive fixes

| # | Release path | Rev B state | Fix |
|---|---|---|---|
| **FM1** | Axle slides out of a pedestal | **Friction only** (M3 pinch screw) | **Circlip groove + external circlip immediately outboard of each pedestal.** The axle cannot translate more than groove clearance even at zero clamp force. The pinch screw is demoted to locating/anti-rotation — it is no longer the retention. |
| **FM2** | Printed hub cracks; spool leaves the axle in pieces | Bearings pressed **into printed plastic** | **Continuous steel sleeve through the full hub bore**, bearings pressed into the *sleeve*. Total loss of the printed material still leaves sleeve + bearings captive on the axle. Also better practice regardless: printed press-fits creep. |
| **FM3** | Pedestal tears out of the hull | M3 heat-set inserts in printed shell | **Through-bolts with an aluminium backing plate** on the far side of the bay floor. Positive, and inspectable without disassembly. |
| **FM4** | Any single retention omitted at assembly, or a pedestal cracks | *(nothing)* | **Keeper bar** spanning both pedestals over the spool, bolted at both ends. Independent secondary capture — the assembly cannot fall clear even if FM1–FM3 all fail. |
| **FM5** | Slip-adjust collar backs off and departs | Thread-lock only | Collar **captive on the axle** — retained by the FM1 circlip, so a fully-backed-off collar still cannot leave. |

#### 3.10.4 The governing principle

**The sacrificial element must fail by *slipping*, never by *releasing*.**

Wear at the friction interface degrades torque transmission — the spool free-spins,
which is the safe direction and is exactly what §3.8 wants. Wear must never
degrade *retention*. Concretely: the hub's friction face and its bearing bores are
separate features on opposite sides of the steel sleeve, so consuming the former
cannot compromise the latter.

**Containment must hold with the cargo doors open**, since that is both the normal
operating state during a cargo evolution and the only geometry in which a released
spool has a path to free air. Every fix above is doors-open-independent.

---

## 4. Load Analysis

### 4.1 Design loads

| Quantity | Value | Source |
|---|---|---|
| Payload mass | 400 g → **3.92 N** | `docs/bom_revR.json` `cargo.winch.line` |
| Total nacelle thrust | 4,464 gf → **43.79 N** | root `AGENTS.md` §1 (2,232 gf × 2 nacelles) |
| AUW, Phase 5–10 | 2,768 g → **27.15 N** | `docs/flight_envelope.md` |
| **Max available lift (excess)** | 43.79 − 27.15 = **16.64 N (3.74 lbf)** | Derived |
| Dynamic factor, cargo events | 2.5 g | `docs/structural_analysis.md` §6 |
| Line, Dyneema SK75 0.5 mm | ~300 N break, 60 N WLL (5:1) | `DYNEEMA-SK75` |

### 4.2 Slip threshold

R5 sets the threshold by the **max available lift**. Shedding must begin while
the aircraft still holds usable lift authority, so the threshold is placed at
roughly half the excess:

```
F_slip = 8.0 N (1.80 lbf)
      = 2.04 × nominal payload load (3.92 N)
      = 48 %  of available excess lift (16.64 N)
      = 13 %  of line WLL (60 N)
      = 2.7 % of line break strength (300 N)
```

8.0 N is also exactly the tension the retired spool was already documented to
carry ("max line tension ~8 N well below PETG yield"), so the drum sizing
carries over unchanged.

Torque and the resulting servo requirement:

```
r_line   = 10.3 mm (first layer, core R 10 mm + ½ line Ø)
T_spool  = 8.0 N × 0.0103 m = 0.082 N·m = 0.84 kgf·cm
T_full   = 8.0 N × 0.0130 m = 0.104 N·m = 1.06 kgf·cm   (at flange radius)
T_req    = 3 × T_full = 0.31 N·m = 3.2 kgf·cm            → §3.1 requirement
F_tooth  = T_spool / 0.015 m = 5.5 N tangential at the ratchet ring
```

### 4.3 Structural margins

**Axle** — Ø4 mm A2 stainless, 40 mm clear span, simply supported, worst-case
central load 2.5 × 8.0 N = 20 N:

```
M = FL/4 = 20 × 40 / 4 = 200 N·mm
I = πd⁴/64 = 12.57 mm⁴ ;  c = 2.0 mm
σ = Mc/I = 200 × 2.0 / 12.57 = 31.8 MPa
FOS = 215 MPa (304 yield) / 31.8 = 6.8          ✓
δ = FL³/48EI = 20 × 40³ / (48 × 193 000 × 12.57) = 0.011 mm   ✓ negligible
```

**Bearings** — MR84ZZ, 10 N per bearing (symmetric): static C₀ ≈ 130 N →
**FOS ≈ 13** ✓

**Ratchet tooth** — cantilever, 3.0 mm face × 2.0 mm root, F_t = 5.5 N:

```
M = 5.5 N × 2.0 mm = 11.0 N·mm ;  Z = bh²/6 = 3.0 × 2.0² / 6 = 2.0 mm³
σ = 5.5 MPa   vs. CF-PETG flexural ≈ 70 MPa  →  FOS = 12.7   ✓
```

All exceed the AUVSI 4.0 target used elsewhere in this project.

### 4.4 ⚠ Unresolved: the shed threshold sits inside the maneuver envelope

Checking `F_slip` against manoeuvre loads on the suspended payload surfaces a
conflict this specification does **not** resolve:

| Condition | Line tension | vs. 8.0 N threshold |
|---|---|---|
| Static payload | 3.92 N | 0.49× — holds |
| 1.5 g | 5.88 N | 0.73× — holds |
| **2.0 g** | **7.84 N** | **0.98× — on the edge** |
| **2.5 g** | **9.80 N** | **1.23× — sheds** |

The 2.5 g factor is the cargo dynamic factor this document already uses for the
axle and bearings (§4.3, from `docs/structural_analysis.md` §6). Applied to the
*line*, it means **a 2.5 g manoeuvre with a slung load drops the payload**, and a
2 g manoeuvre is within 2 % of doing so.

That may well be the correct behaviour — hard manoeuvring with a slung load is
poor airmanship, and shedding beats losing the aircraft. But it is currently an
**accident of where the threshold landed**, not a stated decision, and it needs
one. Three options:

1. **Accept and document** — declare a manoeuvre limit (≈1.5 g) whenever a
   payload is slung, and put it in the flight envelope. Costs nothing mechanical.
2. **Raise the threshold to ~12 N** — 3.06× static payload, still only 72 % of
   the 16.64 N excess lift, leaving 4.6 N of margin at the moment of shed. Buys
   manoeuvre headroom; spends lift margin.
3. **Reduce slung payload mass** — moves both numbers, but 400 g is a
   requirement input, not a free variable.

The threshold cannot simply be raised without limit: it is bounded above by
available excess lift (§4.2), and the whole point of R5 is to shed *before* the
aircraft is dragged down. **Option 1 is recommended** — it is free, it is honest,
and it matches how slung-load limits are handled on crewed rotorcraft — but this
is a flight-envelope decision, not a winch decision, so it is referred rather
than taken. Cross-reference `docs/flight_envelope.md` when resolved.

---

## 5. Electrical Integration — one CAN-PERIPH-GW (R6)

One `SKIPPER-CAN-PERIPH-GW-PCB` at `N_STACKS=1`, mounted in the cargo bay, drives
**both** the servo and the catch. **No board respin is required** — every signal
lands on the existing `J_FLEX` header.

### 5.1 Signal assignment

**Rev C change.** The STS3215's single-wire half-duplex TTL bus (Rev B,
historical — see §5.1.1) is replaced by LibreServo v2's genuine differential
RS-485 bus (§3.1.1). `J_FLEX` was designed for the former, not the latter —
see the open item below.

| Gateway net (`J_FLEX`) | Direction | Connects to | Function |
|---|---|---|---|
| `FLEX_UART_TX/RX` | bidirectional | SPT5425LV/LS2 servo, via an RS-485 transceiver — **§5.1.1, open item** | Servo command/telemetry bus |
| `FLEX_PWM_IO` | output | AO3400 N-FET gate | Solenoid enable — high = catch retracted |
| `FLEX_TTL_GPIO` | — | HX711 (moved here from the now-vacated `FLEX_UART_TX/RX` role) | Line-tension ADC (clock/data), bit-banged on a plain GPIO pair |
| `ENC_SPI_*` (`J_ENC`) | input | **AK7455 on the spool** | Spool angle (§3.7.3) — existing header, dedicated SPI bus, no board change |
| `+5V`, `GND` | power | Servo, solenoid, HX711 | RAIL-2 `5V_JAYNE` |

**Solenoid drive** — AO3400 SOT-23 N-FET (already a project-standard part; see
`avionics/kicad/Observer/Observer.md` Q1), 100 Ω gate resistor, 10 kΩ gate pull-down
so an un-driven or resetting MCU leaves the catch **engaged**, and an SS34
flyback diode across the coil.

#### 5.1.1 RS-485 bus note — **open item** (supersedes the Rev B half-duplex-TTL open item)

Rev B's open item here was whether the MSPM0G3507 could drive a single-wire
half-duplex UART on `FLEX_TTL_GPIO` for the STS3215. That is moot under Rev C:
LibreServo v2 needs genuine **differential RS-485** (an A/B pair through a
transceiver), which `J_FLEX`'s bare `FLEX_UART_TX/RX` pins do not provide by
themselves. Two ways to close this, **neither selected here**:

1. **Add a local RS-485 transceiver at the gateway or in the servo harness**,
   fed from `FLEX_UART_TX/RX`, dedicated to this one servo drop.
2. **Reuse the gateway's own isolated RS-485 trunk** (`RS485_A`/`RS485_B` via
   ISOW1412) if it can be shared with a local servo sub-bus without
   compromising the isolation/topology that trunk exists for — this needs
   deliberate review, not an assumption.

Filed in `avionics/WBS.md` and `REFERENCES.md` "Open Standards Verification
Items" ("LibreServo v2 fork — RS-485 differential bus electrical
integration"). Do not wire either option silently; it changes the gateway's
BOM and possibly its schematic.

### 5.2 Failsafe state table

| Condition | Solenoid | Ratchet | Spool | Outcome |
|---|---|---|---|---|
| Normal, stowed | off | engaged | retract-only | Payload held |
| Commanded pay-out | **on** | retracted | free both ways | Controlled descent |
| Overload, powered | on | retracted | slow pay-out (servo de-rated) | Sensed shed (§3.6b) |
| **Overload, unpowered** | off | **cams out at 8.0 N** | slow pay-out | **Mechanical shed (§3.6a)** |
| Comms loss / watchdog | off | engaged | retract-only | Payload held, cannot pay out |
| Total power loss | off | engaged | retract-only | Payload held; ratchet still sheds above 8.0 N |

Watchdog ownership follows the PACE table in root `AGENTS.md` §9 — **Simon** is
payload-primary, **Shepherd** is the watchdog that cuts RAIL-2 on heartbeat
timeout. Cutting RAIL-2 de-energises the solenoid, which *engages* the catch.

### 5.3 CAN-FD messages

Every frame is TPM-signed by the gateway before republication on both isolated
buses, per NIST SP 800-207 [REF-NIST-001 §2.1].

```text
WINCH_STATUS   (10 Hz, gateway → bus)
  state        : 0 STOWED │ 1 UNLOCKING │ 2 PAYING_OUT │ 3 RETRACTING
                 4 OVERLOAD │ 5 LINE_SHED │ 6 FAULT
  servo_pos    : SPT5425LV/LS2 reported position
  servo_load   : SPT5425LV/LS2 reported load
  line_tension : HX711, mN
  spool_angle  : AK7455, 0-4095 (single-turn absolute)
  spool_turns  : accumulated in firmware; INVALID if |dtheta| > half a rev
                 between samples (see §3.7.2 outrun case)
  flags        : bit0 catch_engaged   bit1 slip_detected
                 bit2 servo_comm_fail bit3 loadcell_fail
                 bit4 encoder_fail    bit5 turns_invalid
                 bit6 servo_vs_spool_divergence (coupler slipped/stripped)
  signature    : TPM

WINCH_COMMAND  (event, Simon → gateway)
  cmd          : 0 HOLD │ 1 PAY_OUT │ 2 RETRACT │ 3 ABORT
  rate         : commanded pay-out rate
  signature    : TPM (rejected if unverified)
```

`ABORT` de-energises the solenoid and releases the servo; the catch springs
engaged. Message IDs are assigned in the firmware task, not here — this document
does not invent bus IDs.

### 5.4 Power budget — RAIL-2 `5V_JAYNE`

| Load | Current @ 5.4 V | Power |
|---|---|---|
| SPT5425LV/LS2, moving | **⚠ stall current not yet published — §3.1** — 1.2 A carried forward from the STS3215-era budget as a placeholder | 6.5 W |
| Solenoid, hold (pay-out only) | 0.20 A | 1.1 W |
| Gateway (MSPM0 + TPM + 2 isolators) | 0.10 A | 0.5 W |
| HX711 | 0.01 A | 0.1 W |
| AK7455 spool encoder | 0.02 A | 0.1 W |
| **Total, worst case** | **≈ 1.53 A** | **≈ 8.3 W** |

RAIL-2 is planned at ~2.4 A typical / ~4.2 A peak
(`docs/POWER_DISTRIBUTION.md` §3.2.1), so the winch fits with margin — **subject
to the SPT5425LV/LS2 stall current, still not published by either sourced
listing (REF-SENSOR-013).** If bench-measured stall exceeds ~2.5 A the RAIL-2
sizing must be revisited. LibreServo v2's own motor driver is rated for up to
16 A continuous (WSD3069DN56 MOSFETs, REF-SENSOR-014) — that is a board
capability ceiling, not a prediction of what this particular servo motor will
actually draw.

---

## 6. Mass and Balance

Per root `AGENTS.md` §5, real masses — no TBD.

| | Item | Mass |
|---|---|---|
| **−** | `cargo_winch_motor_mount.stl` | −25 g |
| **−** | `cargo_winch_spool.stl` | −15 g |
| **−** | N20 gearmotor *(≈10 g, typical N20 — confirm at teardown)* | −10 g |
| | **Removed** | **−50 g** |
| **+** | 6 new printed parts (§3.3) | +62 g |
| **+** | Ø4 × 46 mm stainless axle | +4.6 g |
| **+** | 2× MR84ZZ bearings | +3 g |
| **+** | Spring, M2 dowel, M3 screws/inserts | +4 g |
| **+** | AK7455 spool encoder + diametric magnet + pigtail | +4 g |
| **+** | Steel hub sleeve (Ø10 × Ø8 × 25 mm) — FM2 | +5.6 g |
| **+** | 2× external circlips — FM1 | +0.2 g |
| **+** | Keeper bar, 1 mm Al — FM4 | +5 g |
| **+** | 2× pedestal backing plates — FM3 | +4 g |
| **+** | Pull solenoid | +15 g |
| **+** | SPT5425LV + LibreServo v2 board *(~57 g servo body, REF-SENSOR-013; LibreServo v2 PCB mass not separately published — carried at the same ~60 g class total pending a bench weigh-in of the converted unit)* | +60 g |
| | **Added** | **+167.4 g** |
| | **NET** | **+117.4 g (+0.26 lbm)** |

Consequence at Phase 5–10:

```
AUW  : 2 768 g → 2 885 g  (+4.2 %)
T/W  : 43.79/27.15 = 1.613 → 43.79/28.31 = 1.547
Excess lift : 16.64 N → 15.48 N
Slip threshold as fraction of excess : 48 % → 52 %   (still conservative)
```

T/W stays above 1.5 and the winch remains a cargo-bay-centred mass, so the
longitudinal CG shift is small. **The converted servo's real mass dominates
this table** — the SPT5425LV body alone (~57 g) is close to the 60 g carried
here, but the LibreServo v2 PCB adds an unweighed increment; re-run this
section once a converted unit has been bench-weighed.

---

## 7. Bill of Materials — new items

### 7.1 Printed

See §3.3. All six are new STLs from
`airframe/stls/fuselage/cargo/generate_cargo_mounts.py`, which must be extended
(`make_motor_mount()` and `make_winch_spool()` are **deleted** and replaced).

### 7.2 Purchased

| Ref | Description | Qty | Notes |
|---|---|---|---|
| `SPT5425LV-WINCH-LS2` | SPT5425LV servo, converted with LibreServo v2 (rotation-limiting pin removed) | 1 | REF-SENSOR-013/014; ⚠ stall current not yet published — §3.1 |
| `SOL-CATCH-5V` | Pull solenoid, ≥ 2.5 N @ 3 mm, 5 V | 1 | De-energised = engaged |
| `BRG-MR84ZZ` | MR84ZZ bearing, 4 × 8 × 3 mm | 2 | Pressed into spool hubs |
| `SHAFT-SS-4MM` | Ø4 mm A2 stainless rod, 46 mm | 1 | **New stock item** (project stocks 3 mm CF; CF is unsuitable in a press-fit race) |
| `SPRING-PAWL` | Compression spring, 1.0 N ± 0.2 N installed, stainless | 1 | Set-screw adjustable seat |
| `DOWEL-M2-10` | M2 × 10 mm A2 dowel | 1 | Pawl pivot |
| `ENC-AK7455-SPOOL` | AKM AK7455 off-axis angle sensor + diametric magnet | 1 | [REF-SENSOR-008], fleet-standard; mates the gateway's existing `J_ENC` pigtail — **no new part number, no board change** (§3.7.3) |
| `SLEEVE-HUB-STEEL` | Steel sleeve, Ø10 OD × Ø8 ID × 25 mm | 1 | FM2 — bearings press into steel, not printed plastic; keeps fragments captive |
| `CLIP-EXT-4MM` | External circlip, 4 mm shaft | 2 | FM1 — **positive** axle retention outboard of each pedestal |
| `KEEPER-WINCH` | Keeper bar, 1 mm Al, pedestal-to-pedestal | 1 | FM4 — independent secondary capture |
| `PLATE-PEDESTAL` | Aluminium backing plate, pedestal through-bolt | 2 | FM3 — replaces heat-set-insert-only mounting |
| `FET-AO3400` | AO3400 N-FET, SOT-23 | 1 | Existing project part |
| `DIODE-SS34` | SS34 flyback diode | 1 | Across solenoid coil |
| — | M3 heat-set inserts + M3 × 8 SHCS | 8 + 8 | Pedestals → cargo frame |
| — | M3 × 10 SHCS | 2 | Axle split-collar pinch screws |

**Retained:** `DYNEEMA-SK75`, `HX711-LC`.
**Deleted:** `N20-WINCH`.

---

## 8. Open Items

1. **★ CONTAINMENT — implement all five FM fixes before any flight with a slung
   load (§3.10.3).** Circlip grooves + external circlips (FM1, replaces the
   friction-only pinch collar that violates root `AGENTS.md` §7), steel hub sleeve
   (FM2), pedestal through-bolts + backing plates (FM3), keeper bar (FM4), captive
   slip collar (FM5). A released spool carries **19.1 J** and the full assembly
   **31.8 J** from 400 ft. **This gates flight, not just fabrication.**
2. **Verify the dropped-object regulation.** 14 CFR Part 107 contains a provision
   on dropping objects from a small UA in a manner creating an undue hazard; the
   **exact section number is deliberately not asserted here** because it is not in
   `REFERENCES.md`. Look it up, add it to REF-FAA-002's applied-sections table with
   a validated URL, then cite it in §3.10.2. Per root `AGENTS.md` §4 — do not guess
   a section number. Note the winch *intentionally* releases a payload (R5), so the
   distinction between a commanded release and an uncommanded structural release
   needs to be stated explicitly against the real regulatory text.
3. **Add a containment check to the assembly and pre-flight cards** — circlips
   seated (visual), keeper bar fitted and torqued, backing plates present, slip
   collar witness-mark intact. Doors-open inspection, since that is the geometry
   in which a release escapes.
4. **★ FLIGHT-ENVELOPE DECISION — the shed threshold sits inside the manoeuvre
   envelope (§4.4).** At 8.0 N, a 2.0 g manoeuvre on the slung payload reaches
   0.98× the threshold and 2.5 g sheds the load. Choose: declare a ≈1.5 g
   slung-load manoeuvre limit (recommended, free), raise the threshold to ~12 N
   (spends lift margin), or reduce payload. **Referred to the flight envelope,
   not decided here.** Blocks the pawl-spring calibration target.
5. **Calibrate `T_slip` to 0.060 N·m (0.61 kgf·cm)** at the spool hub collar, and
   confirm the one remaining back-drive requirement **`T_slip < T_backdrive`**
   (§3.8.2). Measure `T_backdrive` with the pawl held clear — but note this now
   confirms an inequality rather than gating R5, since §3.8 removed
   `T_backdrive` from `F_shed` entirely.
6. **Set the servo torque ceiling below `T_slip`** (protection layer 1, §3.8.3)
   so routine lifting never reaches the friction interface and the sacrificial
   hub is consumed only by genuine overloads.
7. **⚠ SPT5425LV/LibreServo v2 stall-current + pin-removal verification (§3.1/§3.1.2).**
   Envelope, torque and mass are now published/sourced (REF-SENSOR-013) and no longer
   block STL generation or the §6 mass figures; stall current and the exact
   pin-removal procedure are still unverified. `TODO §0.x`. (Historical: this item
   was "STS3215 datasheet gate" under Rev B, superseded 2026-08-02.)
8. **RS-485 bus wiring (§5.1.1)** — decide and implement the gateway-side RS-485
   transceiver for LibreServo v2's differential bus (`J_FLEX.FLEX_UART_TX/RX` has
   no transceiver of its own for this drop). Historical: this item was "half-duplex
   TTL bus wiring on `FLEX_TTL_GPIO`" under the Rev B STS3215 selection.
9. **Pawl-spring calibration — distinct from item 5.** This sets `F_shed` (the
   ratchet cam-out, 8.0 N ± 1.0 N at the line); item 5 sets `T_slip` (the hub
   friction interface). Two independent thresholds, two separate adjustments.
   Verify over ≥ 100 lock/release cycles. Target pending item 4.
10. **Line-shed test** — confirm the line actually runs clear of the drum and
    fairlead under load; capstan estimate (§3.6) is analytic, not measured.
11. **Generator rewrite** — delete `make_motor_mount()` / `make_winch_spool()`,
    add the six parts in §3.3; mesh-validate per root `AGENTS.md` §7.
12. **Pedestal mounting stations** — the retired mount anchored to the *gondola
    ceiling* with M2 self-taps; the pedestals need real M3 boss stations in
    `cargo_sect_shell24.scad`, FreeCAD-verified against the door swing envelope.
13. **DRV8833 consolidation (optional)** — door/release servos could move to the
    gateway's spare `FLEX_PWM_IO`, retiring `DRV8833-CARGO` and its tray.
14. **AK7455 spool-encoder integration (§3.7.3)** — magnet pocket in the port
    flange hub, off-axis (the fixed axle occupies the centreline); confirm flux
    at the IC for the chosen magnet and gap, the same bench item already open for
    the nacelle encoders; ≥ 1 kHz sampling; firmware turn-accumulation with the
    `turns_invalid` guard rather than a guessed count.
15. **Spool is a consumable** (§3.8) — mark `cargo_winch_spool_r2.stl` as a wear
    item in the build guide, define an inspection interval and a slip-witness
    mark, and keep a spare in the field kit. Hand-tool replacement per
    `AGENTS.md` §7.
16. **Confirm LibreServo v2 wire-protocol commands** (§3.9) — rate command,
    torque-ceiling set, position/telemetry readback, against the protocol
    documentation linked in REF-SENSOR-014. Supersedes the Rev B "confirm
    STS3215 mode semantics" item (that register-based mode scheme does not
    apply to LibreServo v2); no command/register value is invented in this
    document.
18. **★ Bench-verify the SPT5425LV/LibreServo v2 conversion** (§3.1) — stall
    current at 5.4 V (for RAIL-2 sizing), converted-unit mass (for §6), and the
    rotation-limiting-pin removal procedure (photograph and document before it
    becomes a build-guide step). None of these three figures is published by
    the sources cited in REF-SENSOR-013/014.
19. **Nacelle-tilt servo migration (out of scope for this document)** — the 2×
    nacelle tilt servos are migrating from DS3218MG to the same SPT5425LV +
    LibreServo v2 combination as this winch, per `REFERENCES.md` "Servo Fleet
    Standardisation, 2026-08-02". That migration's own mounting-hardware and
    firmware items are tracked in `airframe/wings-nacelles/WBS.md` and
    `avionics/WBS.md`, not here — this document is the winch's own spec.
17. **Accept that a powerless shed is un-telemetered** (§3.7.2) — no power means
    no encoder and no CAN frame. If post-event knowledge of a shed is required,
    that needs a separate mechanism (e.g. a latching mechanical indicator), not
    the encoder.

---

## 9. References

- REF-SENSOR-013 (SPT5425LV), REF-SENSOR-014 (LibreServo v2) — §3.1, current servo spec
- `docs/references/108090023_STS3215-C001_Datasheet.pdf` — REF-SENSOR-012 (**superseded, historical**, §3.1)
- `avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md` — gateway, `J_FLEX`, `N_STACKS`
- `docs/POWER_DISTRIBUTION.md` §3.2.1, §11.1 — RAIL-2 `5V_JAYNE`
- `docs/flight_envelope.md` — AUW 2,768 g / 27.15 N
- `docs/structural_analysis.md` §6 — 2.5 g cargo dynamic factor
- `docs/bom_revR.json` — superseded winch entries (§2)
- `airframe/fuselage-mid/WBS.md` §1.1.1.2.1 — cargo-handling geometry
- [REF-NIST-001 §2.1] NIST SP 800-207 — signed telemetry
- root `AGENTS.md` §1 (redundancy, thrust baseline), §5 (units, mass), §7 (CF-PETG, joints)

---

*"Takes a man of honour to sit a winch that won't let go until you tell it to."*
