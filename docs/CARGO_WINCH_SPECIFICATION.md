# Cargo Winch — Motor, Ratchet and Spool Support Specification

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**Drafted by:** Claude Haiku 4.5 (Anthropic), 2026-07-27
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Revision:** B (2026-07-27)
**Supersedes:** the Rev P/Q/R N20 winch train (see "Superseded Hardware" below)

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

Seven requirements drive this revision:

| # | Requirement | Where satisfied |
|---|---|---|
| R1 | Cargo winch motor is an **STS3215** | §3.1 |
| R2 | **Normally-engaged** safety ratchet on the spool | §3.4 |
| R3 | Spool supported at **both ends**, not cantilevered on the motor axle | §3.2 |
| R4 | No power → spool may **retract**; power required to retract the catch and permit **pay-out** | §3.4, §5.2 |
| R5 | Line force above max available lift → **slow unwind, line runs off the spool** so the UAV cannot be fouled | §3.6, §4.3 |
| R6 | One **CAN-PERIPH-GW** (`N_STACKS=1`) drives both the servo and the catch | §5 |
| R7 | **Spool position reported to the aircraft throughout pay-out and shed**, until the line departs | §3.7 |

*"Everything is shiny." — Kaylee Frye*

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

### 3.1 Motor — STS3215

| Parameter | Value | Provenance |
|---|---|---|
| Part | STS3215 serial-bus servo | User-directed (R1) |
| Datasheet | `docs/references/108090023_STS3215-C001_Datasheet.pdf` | In repo |
| Interface | **TTL half-duplex serial bus**, ID-addressable, daisy-chainable | §3.1.1 |
| Supply | 5.4 V nominal, from Kaylee RAIL-2 `5V_JAYNE` | `docs/POWER_DISTRIBUTION.md` §3.2.1 |
| **Required** output torque | **≥ 3.2 kgf·cm (0.31 N·m)** at the coupler | Derived, §4.2 |
| **Required** side load on output | **0 N** — see §3.3 | Derived, R3 |

> **⚠ VERIFICATION GATE — `TODO §0.x`.** The STS3215 datasheet in the repo is a
> **scanned/CID-encoded PDF**, and this environment has no OCR tooling
> (`pdftotext`, `tesseract`, `mutool`, `poppler-utils` all absent; `pypdf` fails
> on a broken `cryptography` build). **No performance figure in this document is
> quoted from that datasheet.** Three inputs must be read off it and confirmed
> before any STL is generated or any part is ordered:
> 1. **Case envelope + mounting-boss pattern** — `PEDESTAL_PORT` (§3.3) is
>    parameterised on these; the generator will not produce a correct bracket
>    without them.
> 2. **Stall/continuous torque** — must meet the ≥ 3.2 kgf·cm requirement above.
> 3. **Mass and stall current** — the mass drives the CG/T-W figures in §6, and
>    the stall current drives the RAIL-2 budget in §5.4.
>
> Per root `AGENTS.md` §4 ("if a citation can't be verified, mark it 'requires
> verification'") this is logged in `REFERENCES.md` REF-SENSOR-012 and in the
> Open Standards Verification Items table. **Do not fabricate these numbers.**

#### 3.1.1 Interface — serial bus, not PWM

The STS3215 is commanded over a **half-duplex TTL serial bus**, not a
1000–2000 µs PWM pulse train. This is architecturally load-bearing and is why
`CAN-PERIPH-GW-1` needs no new hardware: its `J_FLEX` header already carries
`FLEX_TTL_GPIO`, documented in `avionics/kicad/CAN-PERIPH-GW-1.md` §G as
covering *"a TTL-level digital servo protocol (e.g. a serial-bus servo)."*
A half-duplex bus needs the MCU's TX and RX tied through a direction-steering
resistor/buffer at the header — see §5.1.

### 3.2 Spool support architecture — supported at both ends (R3)

The load path no longer passes through the motor at all. The spool rotates on
**two bearings carried inside its own hub**, riding on a **fixed** axle that is
clamped at **both** pedestals:

```text
        PORT pedestal                                  STBD pedestal
     (bearing seat + STS3215)                   (bearing seat + pawl + solenoid)
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
     STS3215 ──dog coupler──►  line             (24 sawtooth)  │    │
     (torque only,            pays out              ▲         pawl  │
      no radial load)                               └──────────┘    │
```

- **Axle:** Ø4 mm × 46 mm, A2/304 stainless, **stationary** (does not rotate).
  Clamped in a split-collar seat in each pedestal with one M3 pinch screw.
- **Bearings:** 2× MR84ZZ (4 × 8 × 3 mm), pressed into counterbores in the
  spool's two flange hubs — one at each end of the drum, so the line load is
  reacted symmetrically.
- **Drive:** the STS3215 transmits **torque only** through a lost-motion dog
  coupler (§3.3). No radial or moment load reaches the servo output spline.
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
| `cargo_winch_pedestal_port.stl` | CF-PETG | 18 g | Port axle clamp + bearing seat + **STS3215 case cradle** (envelope parameterised — see gate in §3.1) |
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

**0.105 kgf·cm is the whole error budget.** A high-ratio geared serial-bus servo
of the STS3215's class will typically resist back-drive by *several* kgf·cm —
one to two orders of magnitude more. If that holds here, then:

- the ratchet cams out at 8.0 N exactly as designed, **and the spool still does
  not turn**, because the servo gearbox holds it;
- the powerless mechanical shed (§3.6a) — the path that exists precisely for
  when power and firmware are gone — **does not function at all**;
- worse, `T_backdrive` varies with temperature, wear and lubricant, so even if
  shed does occur the threshold is not repeatable, which is unacceptable for a
  safety function whose whole purpose is a predictable release point.

This is a **more serious finding than the sensing question**, and it is now the
top open item (§8). It must be measured, not assumed: with the ratchet pawl held
clear, apply a tangential load at the spool and record the torque at which the
spool turns the unpowered servo.

#### 3.7.2 Three couplings, and why the servo encoder cannot be the answer

| Coupling | Normal lowering | Powerless shed | Servo encoder during shed |
|---|---|---|---|
| **(A) Rigid dog** (Rev B as written) | Servo controls descent ✓ | **Only if back-drivable** — threshold polluted by `T_backdrive` | Tracks ✓ |
| **(B) Torque-limiting slip clutch** above working torque, below overload | Servo controls descent ✓ | Clean — `T_backdrive` out of the equation ✓ | **Does not track** ✗ (servo stays put) |
| **(C) Overrunning one-way clutch** | **Broken** ✗ — servo could never pay out under control | Clean ✓ | Does not track ✗ |

(C) is rejected outright: it would make controlled lowering impossible. The
choice is (A) or (B), and it cannot be made until `T_backdrive` is measured.

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

---

## 5. Electrical Integration — one CAN-PERIPH-GW (R6)

One `MAL-CAN-PERIPH-GW-PCB` at `N_STACKS=1`, mounted in the cargo bay, drives
**both** the servo and the catch. **No board respin is required** — every signal
lands on the existing `J_FLEX` header.

### 5.1 Signal assignment

| Gateway net (`J_FLEX`) | Direction | Connects to | Function |
|---|---|---|---|
| `FLEX_TTL_GPIO` | bidirectional | STS3215 signal | Half-duplex TTL servo bus (**§5.1.1**) |
| `FLEX_PWM_IO` | output | AO3400 N-FET gate | Solenoid enable — high = catch retracted |
| `FLEX_UART_TX/RX` | input | HX711 | Line-tension ADC (clock/data) |
| `ENC_SPI_*` (`J_ENC`) | input | **AK7455 on the spool** | Spool angle (§3.7.3) — existing header, dedicated SPI bus, no board change |
| `+5V`, `GND` | power | Servo, solenoid, HX711 | RAIL-2 `5V_JAYNE` |

**Solenoid drive** — AO3400 SOT-23 N-FET (already a project-standard part; see
`avionics/kicad/Jayne/Jayne.md` Q1), 100 Ω gate resistor, 10 kΩ gate pull-down
so an un-driven or resetting MCU leaves the catch **engaged**, and an SS34
flyback diode across the coil.

#### 5.1.1 Half-duplex bus note — **open item**

`FLEX_TTL_GPIO` is a single pin. A half-duplex TTL servo bus needs the MCU's
UART TX and RX joined with direction steering — typically a series resistor plus
a pull-up, or a small buffer. Whether the MSPM0G3507's UART can be configured
single-wire on this pin, or whether a resistor/buffer must be added at the
harness end, **must be confirmed against the MSPM0G3507 pinmux tables**. This is
the same pinmux caveat already open on that board
(`CAN-PERIPH-GW-1.md` open item 4). Filed in `avionics/WBS.md`.

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
  servo_pos    : STS3215 reported position
  servo_load   : STS3215 reported load
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
| STS3215, moving | **⚠ gate §3.1** — budget 1.2 A | 6.5 W |
| Solenoid, hold (pay-out only) | 0.20 A | 1.1 W |
| Gateway (MSPM0 + TPM + 2 isolators) | 0.10 A | 0.5 W |
| HX711 | 0.01 A | 0.1 W |
| AK7455 spool encoder | 0.02 A | 0.1 W |
| **Total, worst case** | **≈ 1.53 A** | **≈ 8.3 W** |

RAIL-2 is planned at ~2.4 A typical / ~4.2 A peak
(`docs/POWER_DISTRIBUTION.md` §3.2.1), so the winch fits with margin — **subject
to the STS3215 stall current in the §3.1 gate.** If stall exceeds ~2.5 A the
RAIL-2 sizing must be revisited.

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
| **+** | Pull solenoid | +15 g |
| **+** | STS3215 *(**⚠ gate §3.1** — 60 g assumed)* | +60 g |
| | **Added** | **+152.6 g** |
| | **NET** | **+102.6 g (+0.23 lbm)** |

Consequence at Phase 5–10:

```
AUW  : 2 768 g → 2 871 g  (+3.7 %)
T/W  : 43.79/27.15 = 1.613 → 43.79/28.16 = 1.555
Excess lift : 16.64 N → 15.63 N
Slip threshold as fraction of excess : 48 % → 51 %   (still conservative)
```

T/W stays above 1.5 and the winch remains a cargo-bay-centred mass, so the
longitudinal CG shift is small. **The STS3215's real mass dominates this table**
— if it differs materially from 60 g, re-run this section.

---

## 7. Bill of Materials — new items

### 7.1 Printed

See §3.3. All six are new STLs from
`airframe/stls/fuselage/cargo/generate_cargo_mounts.py`, which must be extended
(`make_motor_mount()` and `make_winch_spool()` are **deleted** and replaced).

### 7.2 Purchased

| Ref | Description | Qty | Notes |
|---|---|---|---|
| `STS3215-WINCH` | STS3215 serial-bus servo | 1 | ⚠ gate §3.1 |
| `SOL-CATCH-5V` | Pull solenoid, ≥ 2.5 N @ 3 mm, 5 V | 1 | De-energised = engaged |
| `BRG-MR84ZZ` | MR84ZZ bearing, 4 × 8 × 3 mm | 2 | Pressed into spool hubs |
| `SHAFT-SS-4MM` | Ø4 mm A2 stainless rod, 46 mm | 1 | **New stock item** (project stocks 3 mm CF; CF is unsuitable in a press-fit race) |
| `SPRING-PAWL` | Compression spring, 1.0 N ± 0.2 N installed, stainless | 1 | Set-screw adjustable seat |
| `DOWEL-M2-10` | M2 × 10 mm A2 dowel | 1 | Pawl pivot |
| `ENC-AK7455-SPOOL` | AKM AK7455 off-axis angle sensor + diametric magnet | 1 | [REF-SENSOR-008], fleet-standard; mates the gateway's existing `J_ENC` pigtail — **no new part number, no board change** (§3.7.3) |
| `FET-AO3400` | AO3400 N-FET, SOT-23 | 1 | Existing project part |
| `DIODE-SS34` | SS34 flyback diode | 1 | Across solenoid coil |
| — | M3 heat-set inserts + M3 × 8 SHCS | 8 + 8 | Pedestals → cargo frame |
| — | M3 × 10 SHCS | 2 | Axle split-collar pinch screws |

**Retained:** `DYNEEMA-SK75`, `HX711-LC`.
**Deleted:** `N20-WINCH`.

---

## 8. Open Items

1. **★ MEASURE `T_backdrive` (§3.7.1) — now the top open item.** With the pawl
   held clear, apply tangential load at the spool and record the torque at which
   the spool turns the **unpowered** servo. The entire shed-threshold error
   budget is **0.105 kgf·cm**; a geared bus servo may exceed that by 10–100×, in
   which case the powerless shed (§3.6a) does not function and the coupler must
   change from rigid (A) to slip-clutch (B) per §3.7.2. **This gates whether
   R5 is met at all** — it is not a refinement, it is a go/no-go on the safety
   function. Measure before committing the coupler geometry.
2. **Coupler decision (A) vs (B)** — blocked on item 1. (C) is rejected: an
   overrunning clutch would make controlled lowering impossible.
3. **⚠ STS3215 datasheet gate (§3.1)** — envelope, torque, mass, stall current.
   Blocks STL generation, BOM order, and the §6 mass figures. `TODO §0.x`.
4. **Half-duplex bus wiring (§5.1.1)** — confirm MSPM0G3507 single-wire UART on
   `FLEX_TTL_GPIO`, or add a steering resistor/buffer at the harness.
5. **Slip-threshold bench calibration** — set the spring seat to 8.0 N ± 1.0 N
   measured at the line, then verify over ≥ 100 lock/release cycles.
6. **Line-shed test** — confirm the line actually runs clear of the drum and
   fairlead under load; capstan estimate (§3.6) is analytic, not measured.
7. **Generator rewrite** — delete `make_motor_mount()` / `make_winch_spool()`,
   add the six parts in §3.3; mesh-validate per root `AGENTS.md` §7.
8. **Pedestal mounting stations** — the retired mount anchored to the *gondola
   ceiling* with M2 self-taps; the pedestals need real M3 boss stations in
   `cargo_sect_shell24.scad`, FreeCAD-verified against the door swing envelope.
9. **DRV8833 consolidation (optional)** — door/release servos could move to the
   gateway's spare `FLEX_PWM_IO`, retiring `DRV8833-CARGO` and its tray.
10. **AK7455 spool-encoder integration (§3.7.3)** — magnet pocket in the port
    flange hub, off-axis (the fixed axle occupies the centreline); confirm flux
    at the IC for the chosen magnet and gap, the same bench item already open for
    the nacelle encoders; ≥ 1 kHz sampling; firmware turn-accumulation with the
    `turns_invalid` guard rather than a guessed count.
11. **Accept that a powerless shed is un-telemetered** (§3.7.2) — no power means
    no encoder and no CAN frame. If post-event knowledge of a shed is required,
    that needs a separate mechanism (e.g. a latching mechanical indicator), not
    the encoder.

---

## 9. References

- `docs/references/108090023_STS3215-C001_Datasheet.pdf` — REF-SENSOR-012 (**requires verification**, §3.1)
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
