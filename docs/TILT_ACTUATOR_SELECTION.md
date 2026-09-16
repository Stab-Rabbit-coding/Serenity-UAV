# Nacelle-Tilt Actuator Selection — Rev T5e (decision record, D5; Rev T5b 2026-09-15 base)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**AI note:** Drafted by Claude (model: Claude Opus 5, Anthropic) under the author's
direction, 2026-09-15 / 2026-09-16, per `AGENTS.md` §3 AI attribution.
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0
**Status:** Decided (owner, 2026-09-15: multi-start worm + brake, Option 2);
**re-cut 2026-09-16 (Rev T5e, Option 4)** — same architecture, the Ø25 motor
replaced by the Pololu 20D and the worm by a six-start Ø26, because Option 2
cannot be built (§1a). Supersedes the Rev T4 "DS3225 multi-turn + 38T/38T spur"
baseline (`merge_cargo_interior.py` NSVMT_*, now gated off) and the Rev T5
single-start worm first cut.

> ⚠️ **ENGINEERING REVIEW REQUIRED** — the load and rate figures below derive from
> cited inputs listed in `tools/tilt_actuator_options.py`; the aero moment about
> the tilt axis is unquantified (TILT-CTL-06) and the nacelle inertia is the lumped
> pre-T4 figure.

---

## 1. Decision

**Built: Option 4 (Rev T5e)** — a **six-start m1 worm (Ø26, lead 13.0°) on a
Pololu 20D 25:1 CB 6 V gearmotor (#3712, no encoder, REF-ACT-001)** driving a **40T
m1 worm wheel on the Ø4 drive shaft** (6.67:1), followed by the existing 14T/50T tip
stage (3.571:1); **23.8:1 overall; 144 °/s at the nacelle no-load, 111 °/s at the
motor's max-efficiency point**. The unpowered hold is a **spring-applied,
solenoid-released pin brake on the worm shaft** (`tilt_brake.scad`), not the worm
geometry. Each actuator + brake has its **own fused feed from the main bus** (§5).

Trade record: `docs/TILT_ACTUATOR_OPTIONS.md` (generated) and
`airframe/openscad/fuselage/cargo/tilt_actuator_options.scad` (`OPTION = 1|2|3|4`).

| | Opt 1 single-start worm | Opt 2 four-start / 25D (2026-09-15 pick) | Opt 3 spur + DS3225 | **Opt 4 six-start / 20D (built)** |
|---|---|---|---|---|
| Nacelle rate, no-load / max-eff | 24 / 18 °/s | 168 / 136 °/s | 129 / 103 °/s | **144 / 111 °/s** |
| ±5° move / full 145° sweep | 0.24 s / 6.1 s | 0.06 s / 0.89 s | 0.07 s / 1.15 s | **0.06 s / 1.04 s** |
| Rate-limit bandwidth at ±5° | 0.8 Hz | 5.3 Hz | 4.1 Hz | **4.6 Hz** |
| Torque limit at the nacelle | 1.83 N·m (tooth) | 1.83 N·m (tooth) | 1.34 N·m (tooth) | **1.81 N·m (motor stall ≈ tooth)** |
| Unpowered hold | geometry | brake (BRK-1..3) | brake | **brake (BRK-1..3)** |
| Motor vs Ø42 wheel tip | clear | **−1.5 mm (T5d-1)** | n/a | **+2.0 mm** |
| Battery cradle (Rev T5) | clear | clear | fouls by 13.6 mm/side | **clear (3.2 mm)** |
| Mass, both sides incl. shell delta | +130 g | +242 g | +188 g | **+147 g** |
| Stall current, both motors | 5.8 A | 12.0 A | 4.6 A | **5.8 A** |

## 1a. Why Option 2 could not be built (2026-09-16)

For a motor coaxial with its worm, the motor body's clearance to the wheel's tip
circle is `WORM_PD/2 − MOTOR_D/2 − m` — it does not depend on the centre distance
and it does not change if the worm is swung round the wheel (the first fix
proposed, a ~25° tilted motor, was worked through in `tools/cargo_layout_fit.py`
and abandoned: it also lands the worm on the port hoist line at Y 55.5). The
worm's inboard tip is capped by the battery cradle at X −139.25, i.e.
`WORM_PD ≤ 26` at the gear plane. So a Ø25 body is 1.5 mm inside the wheel for
every worm that fits, and a Ø20 body clears it by 2.0 mm. The 20D's lower speed
(570 rpm) is recovered by a six-start worm: 6.67:1 instead of 10:1, lead 13.0°
(back-drivable — the brake was always the design basis). Its 1.6 kgf·cm stall
puts 0.53 N·m on the wheel, matching the wheel-tooth Lewis limit (0.51 N·m at
FOS 4): the train is now limited by motor and tooth together, which is where a
brake sized to BRK-1 wants it.

## 2. Why the rate matters (the requirement this creates)

On a lateral tandem pair the nacelle tilt is the **only** hover pitch actuator and,
differentially, the yaw actuator. That is control-surface duty, not a mode change:

* **TILT-CTL-07 (adopted, owner to confirm against flight dynamics):** nacelle slew
  ≥ 120 °/s and rate-limit bandwidth ≥ 4 Hz at ±5°. Opt 1 fails it (0.8 Hz); Opt 2,
  3 and 4 meet it — Opt 4 no-load (144 °/s, 4.6 Hz); at the motor's max-efficiency
  point it is 111 °/s, so the loaded figure is the one the owner must confirm.

Aircraft-level authority is thrust-limited and identical for every option:
collective tilt of 2/5/10° gives 0.34/0.85/1.70 m/s² horizontal at hover thrust =
weight; ±5° differential gives 0.72 N·m of yaw at 3,911 g; pitch moment is
0.34 N·m per mm of pivot–CG vertical offset (z_cg not recorded, LG-29).

## 3. Why a brake, and why it is flight-critical

A 6-start worm at lead angle 13.0° back-drives once the friction coefficient falls
below tan 13° = 0.23 (the 4-start of Opt 2: 0.17) — its self-locking is conditional
and is **not** the design basis. A shorted-winding "short-brake" is a
damper, not a hold (zero back-EMF at zero speed ⇒ zero static torque).

**Owner-stated architecture principle (2026-09-15, recorded here because it is
written nowhere else):** *each ESC has an independent electrical path, from its own
fuse to its EDF, so that a single EDF or ESC-path failure in either nacelle cannot
cascade and the aircraft can make a controlled descent on the remaining units
instead of an uncontrolled crash.* Under that principle the tilt hold cannot be
delegated to a shared rail (the rail is exactly what is not shared), and the design
case for the brake is "one EDF path dead, descending on three, and the tilt
actuator's own feed has also failed." Both nacelles must stay where the controller
last put them.

Requirements (added to `docs/TILT_DRIVE_CONTROL_SPEC.md` §5.2/§8):

* **BRK-1** — Each tilt train shall hold its last commanded angle against the full
  aero + thrust-asymmetry moment with the actuator unpowered, for the duration of a
  three-EDF controlled descent from any Phase 5 flight condition. Sized to the
  train's own limit (1.81 N·m at the nacelle, wheel-tooth Lewis FOS 4 ≈ motor stall
  → 0.51 N·m drive shaft → 0.077 N·m worm shaft at 6.67:1) so the brake is never
  the weakest link.
* **BRK-2** — The hold shall be independent of the actuator's electrical path and
  of the bus: spring-applied, held **off** only by the actuator's own powered feed.
* **BRK-3** — Engagement on power loss is automatic; release is commanded, after
  the loop has unloaded the pin; the sequence is bench-verified with the AK7455
  reading the nacelle, not the motor.

Brake design (`airframe/openscad/fuselage/cargo/tilt_brake.scad`): a 12-slot
face-castellated collar on the worm's aft end (Rev T5e: the 20D's 18 mm shaft runs
through it), a Ø2 steel pin in a printed guide block bolted through the bracket
web, a Ø12 × 24 mm pull solenoid behind it (Y 62–86, axis 1.5 mm inboard of the
worm's), ~2 N spring. Pin load at the train limit: 0.077 N·m / 5.5 mm = 14 N
(shear 4.5 MPa on a Ø2 pin); release effort ≈ spring + 0.2 × side load ≈ 5 N.
Resolution 30° at the worm = 4.5° at the drive shaft = **1.26° at the nacelle**
(±0.63° drift before the pin seats; was 0.84° at 10:1 — acceptable for a
hold-in-place brake, the loop re-trims on release). Placement verified by
`tools/cargo_layout_fit.py` (PASS 2026-09-16: clears the winch axle above at
Z 139–143, the payload crown below at Z 85, the battery inboard).

Limitation, stated: a brake on the worm shaft does not protect against a broken
worm, wheel or bracket — a mechanism failure frees the nacelle regardless. A
drive-shaft brake would, but no placement below Z 85 clears the hoisted payload.

## 4. Controller — this changes the LibreServo_v4 specification

LibreServo_v4 is a **servo** controller: discrete N+P MOSFET bridge with FAN3227
gate drivers, ACS711 current sense, an on-axis AEAT-8800 absolute encoder, an
MPM3610 +7 V buck from the servo bus, CAN-FD (ADM3055E) + RS-485 (ADM2587E),
OPTIGA Trust M. Driving a gearmotor breaks four of those assumptions:

| Item | LibreServo_v4 today | Tilt-controller requirement (Opt 2) |
|---|---|---|
| Motor | DS3225 internal motor, 2.3 A stall @ 6.8 V | **Rev T5e: Pololu 20D 25:1 CB 6 V: 2.9 A stall**, 150 mA free-run (REF-ACT-001) — within 30 % of the v4 bridge's design point; re-rate rather than redesign. (Opt 2's 25D wanted 6.0 A.) |
| Position sensing | AEAT-8800 on the output shaft, single-turn absolute | **T5c/T5e:** the AEAT-8800 stays — it reads a Ø6 magnet in the worm's brake collar (worm-shaft angle, single-turn absolute; firmware counts turns, the AK7455 gives the absolute nacelle angle). The gearmotor is the no-encoder **#3712 (20Dx41L)** |
| Brake | none | one **solenoid driver output** (~0.5 A continuous or PWM-held), fail-safe de-energised = engaged, with brake-state telemetry |
| Power input | +7 V from the 6 V servo bus via MPM3610 | **own fused feed from VBAT (22.2 V nominal, 25.2 V full)**; MPM3610 input rating vs 25.2 V **REQUIRES VERIFICATION** — if it is a 21 V part the front end must change |
| Firmware | servo position loop | cascade: quadrature velocity/position inner loop, AK7455 outer loop, brake sequencing (BRK-3), differential-tilt trip input |

The bus, the trust module and the board outline (36.5 × 42.9 mm, card-edge rails
on the bracket — Rev T5e: on the web's OUTBOARD face, component side toward the
web with a 4 mm standoff, bare back to the skin) are unchanged. This is filed as a change request in the
LibreServo_v4 repository (`docs/CR-2026-09-15-tilt-controller-variant.md`) —
"LibreServo_v4.1-TC" — rather than a change to the winch/door servos' v4.0.0.

## 5. Power — per-path feeds

Two new fused branches off the main bus, on the same per-path principle as
F_ESC1–4 (`docs/POWER_DISTRIBUTION.md` §1/§3.3/§5):

| Branch | Load | Stall / running from VBAT | Fuse |
|---|---|---|---|
| F_TILT_P | port tilt controller + gearmotor + brake solenoid | Rev T5e: 2.9 A × 6 V / 22.2 V / 0.9 = 0.9 A transient (Opt 2 was 1.8 A); 0.5 A running incl. the solenoid | 3 A mini blade (unchanged; could drop to 2 A) |
| F_TILT_S | starboard, identical | 0.9 A / 0.5 A | 3 A mini blade |

The 6 V servo bus loses the 2 × 2.3 A DS3225 stall load (its 8.8 A all-stall
finding drops to 4.2 A). The tilt actuators are no longer on that bus at all.

## 6. Geometry consequences (applied, Rev T5e 2026-09-16)

* `tools/cargo_layout_fit.py` baseline: Ø20 motor (41 + 6 mm), worm PD 26 six-start,
  C 33, gear plane X −122.75, motor face Y 39.1, 18 mm shaft, brake collar Y 52.1..56.1,
  solenoid Y 62.1..86.1 at X −126.75; bracket feet (10.6, 124.09) (40, 124.09) (64, 77);
  controller board envelope on the web's outboard face. Regenerated
  `cargo_layout_t5_params.scad`.
* `tilt_actuator_bracket.scad`: Ø20 cradle (top + outboard quadrants only — nothing
  below the motor underside over the wheel), 2.5 mm face plate flat-bottomed at the
  motor underside with the worm hub turning inside its bore, 2 × M2.5 on a 45°
  diagonal (hole spacing 15 mm — VERIFY on the Pololu dimension diagram), web
  Y 4..97.5 with a rounded worm/collar slot, board rails outboard. Six-start worm
  from a transverse tooth section. STLs: `tilt_actuator_bracket_{port,stbd}.stl`
  (16.3 g), `tilt_actuator_worm.stl` (6.0 g, RH, 2 off), `tilt_actuator_wheel.stl`
  (6.9 g, 2 off), `tilt_brake_guide.stl` (2.1 g, 2 off).
* Cargo shell re-merged (`merge_cargo_interior.py` Rev T5e: feet moved, chin-shelf and
  Observer bosses added); every gate PASS (`validate_stls` 79/79, `cargo_bay_envelope`,
  `cargo_layout_fit`, `landing_gear_wing_clearance --proud`, `wing_root_deconflict`,
  `wing_internal_clearance`, `wing_spar_carrythrough`).
* Worm thrust at motor stall ≈ 27 N along Y into the gearbox's output bearing —
  REF-ACT-001 gives no axial rating (VERIFY; thrust washer fallback).

## 7. Open items

| ID | Item |
|---|---|
| TILT-CTL-05/07 | Owner to confirm ≥ 120 °/s, ≥ 4 Hz against the flight-dynamics case |
| TILT-CTL-06 | Aero moment about the tilt axis — sizes the brake's real margin |
| BRK-4 | Solenoid part selection (Ø12 × 24, pull, ~3 N @ 3 mm, 6 V, continuous) — BOM `SOL-TILT-BRAKE`, REQUIRES VERIFICATION |
| BRK-5 | Bench: hold test (§7.3) with the pin engaged, release under load, drift ≤ 0.63° |
| LS-CR-1 | LibreServo_v4.1-TC change request (bridge re-rated to 2.9 A stall, brake driver, VBAT front end) |
| REF-ACT-001 | Pololu 20D: product page read 2026-09-16 (41 L, 18 mm shaft, M2.5 ≤ 3.5 deep); mounting-hole spacing (15 mm assumed) and Ø7 boss REQUIRE VERIFICATION on the dimension diagram; axial load rating not published |
| TC-BOARD | Rail standoff 4 mm assumes ≤ 4 mm component height on LibreServo_v4 — verify against the v4.0.0 layout |
