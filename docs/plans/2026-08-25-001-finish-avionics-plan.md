---
title: "plan: Close out avionics — CAN-FD/RS-485 actuator bus, SG90/OSC finalize, Observer pitot airspeed"
date: 2026-08-25
plan_type: feature+fix
execution: hardware+firmware
deepened: 2026-08-25
---

# plan: Close out avionics subsystem

**Target repo:** Serenity-UAV (this repo)
**Scope:** `avionics/` (Pilot, XO, Commo, Observer, FlightEngineer, CAN-PERIPH-GW-1,
ENC-NACELLE-1, firmware) plus the three external companion repos this plan
assumes are backend-complete: `open-servo-core-secure`, `Open-Secure-ESC`,
`LibreServo_v4`.

---

## Summary

"Finish the avionics" is not one task — it is five separable work streams that
converge on the same six boards. This plan takes three backend assumptions as
**given** (per user direction, not re-derived here):

1. All SG90-class servos run **open-servo-core-secure**: TTL bus, CMAC-authenticated
   messages.
2. All nacelle ESCs are **Open-Secure-ESC 50A/6S `CAN_485_faraday`** builds:
   CAN-FD + RS-485, host **and** message authentication.
3. Both nacelle tilt servos run **LibreServo_v4**: CAN-FD + RS-485 + OPTIGA Trust M
   secure element.

Taking these as given exposes a real problem: **the avionics hardware and firmware
that are supposed to talk to these actuators were designed against an older, PWM-based
interface.** Pilot's own field-connector table (`avionics/kicad/Pilot/Pilot.md` §14)
still lists `J_ESC` as 4-channel PWM/BDSHOT and `J_SERVO` as 4-channel PWM; the
firmware WBS's EDF governor (`avionics/firmware/WBS.md` §4.2) is scoped around
BDSHOT600 telemetry decode and EHRPWM throttle output — none of that exists on a
CAN-FD/RS-485 actuator. `REFERENCES.md` REF-SENSOR-014 also still names "LibreServo
v2" and documents an **unresolved RS-485 transceiver gap** on `CAN-PERIPH-GW-1`'s
`J_FLEX` (bare UART pair, no local transceiver) — that citation predates the v4 fork
and the gap it flags is exactly what nacelle-servo integration needs closed. Finally,
Pilot's own purpose statement claims an "airspeed sensor" that **does not exist
anywhere in the design** — no pitot connector, no sensor, no REF-ID. The user's
direction to put airspeed on **Observer** instead of Pilot is a deliberate
architecture correction, not an addition to a design that already had it.

This plan is organized as nine implementation units (U1–U9) across four phases,
plus the pre-existing per-board ERC/DRC backlog that has to close before any board
ships gerbers.

## Assumptions Taken As Given (not re-litigated by this plan)

- Open-Secure-ESC, LibreServo_v4, and open-servo-core-secure firmware/hardware are
  functionally complete on their own repos. This plan only covers **integration**:
  bus wiring, message schemas, key provisioning, and the Serenity-side firmware that
  talks to them.
- `REFERENCES.md` REF-SENSOR-015 already flags OpenServoCore upstream as "in active
  development, nothing here is shippable yet" (verified only to hardware rev B) —
  that flag is **not cleared by this plan**. U4 below re-checks it as a gate, not a
  formality; if it's still true, flight-article SG90 procurement stays blocked
  regardless of how much integration work lands.

---

## Skills & Workflow Map

None of these nine units close on acceptance-criteria checkboxes alone — each has
a project skill that either produces the artifact the checkbox demands or is the
gate that must pass before the checkbox can be marked done. This table is the
quick-reference; each unit below repeats its own row inline so an implementer
never has to cross-reference back here.

| Unit | Producing skill(s) | Gating skill/workflow | What "gate passes" means |
|---|---|---|---|
| U1 | `pcb-designer` (bus-topology + connector rework guidance) | `kicad` | ERC/DRC on `Pilot.kicad_sch`/`.kicad_pcb` shows 0 new violations after the `J_ESC`/`J_SERVO` retarget |
| U2 | `pcb-designer` (RS-485 transceiver placement), `datasheets` (ADM2587E/ADM3055E extraction) | `kicad` | `CAN-PERIPH-GW-1` schematic ERC clean after the `J_FLEX` transceiver fix; datasheet extraction attached before REF-SENSOR-014 is renamed |
| U3 | `bom`/`datasheets` (Open-Secure-ESC `CAN_485_faraday` BOM/spec pull) | `secure-controller-assurance` | Host+message-auth message schema maps onto SCA's actuator-authentication controls with no unmapped 🔒 gate |
| U4 | — (protocol/firmware only) | `secure-controller-assurance` + explicit upstream-maturity re-check | CMAC framing maps onto an SCA control; REF-SENSOR-015 maturity flag is re-stated, not silently dropped |
| U5 | `datasheets` (sensor extraction), `bom` (sourcing), `pcb-designer` (I2C bus/pull-up sizing) | `kicad`, then `kidoc` | Datasheet extraction exists **before** any REFERENCES.md entry is written (hard order, not parallel); ERC clean on `J_PITOT`; Observer's `kidoc` HDD scaffold regenerates without a stale-data warning |
| U6 | — (architecture decision, no board edit) | `secure-controller-assurance` | Every new authenticated endpoint class (ESC, tilt servo, SG90) is mapped to an SCA control or overlay, not asserted informally |
| U7 | — (closeout only) | `kicad` (ERC/DRC/BOM/DFM), `emc` (pre-compliance) | Each board table row reaches `kicad` ERC=0/DRC=0-hard (or documented exception) **and** an `emc` pre-compliance pass/waiver, before gerbers are generated |
| U8 | `pcb-designer` (isolation/creepage reference), `emc` (shielding/radiated-emissions guidance) | `kicad` | DRC re-run shows the 13 `TMESH_P`/`TMESH_N` vs `GND2_*` violations resolved to ≥8mm creepage / ≥1.5mm clearance |
| U9 | `kidoc` (regenerate per-board status docs) | `project-overseer` | WBS/TODO federation check shows no stale checkbox and no orphaned open item across `avionics/TODO.md`, `avionics/WBS.md`, and root `TODO.md`/`WBS.md` |

**Why `kicad` (not ad-hoc `kicad-cli`) is the gate, not just a tool call:** the
`kicad` skill's ERC/DRC analyzer produces a confidence-labeled, evidence-sourced
report (`trust_summary` rollup) rather than a bare pass/fail — that's what
`avionics/AGENTS.md`'s DRC Workflow policy ("document anything that cannot be
resolved... with the specific DRC rule and reason") actually needs to be
satisfiable. A bare `kicad-cli` exit code doesn't carry the reason text the
policy requires.

**Why `secure-controller-assurance` gates U3/U4/U6 specifically:** those three
units are exactly where root `AGENTS.md`'s Zero Trust requirement stops being an
aspiration and becomes a wire-level claim (an ESC accepts a signed setpoint, an
SG90 accepts a CMAC frame). The skill's 96 controls + platform overlays are the
existing mechanism for turning "this is authenticated" into a checked control
rather than a sentence in a `.md` file.

**Why `datasheets` gates the *order of operations* in U2/U5, not just informs
them:** root CLAUDE.md's Authenticity policy ("No fabricated... reference...
will ever be fabricated") is a standing constraint this plan cannot waive for
convenience. U5 in particular is the unit most at risk of a fabricated citation
— it is picking a **new** sensor with no prior art in the repo — so the datasheet
pull is sequenced as a hard prerequisite to writing anything into
`REFERENCES.md`, not a parallel nice-to-have.

---

## Dependency Graph

```
U1 (Pilot ESC/servo interface: PWM → CAN-FD/RS-485)
 ├─→ U2 (LibreServo_v4 nacelle-tilt bus integration)
 ├─→ U3 (Open-Secure-ESC CAN-FD/RS-485 integration + governor rewrite)
 └─→ U6 (fleet key provisioning / host+message auth wiring)
U4 (OSC SG90 TTL+CMAC bus finalize)  ─────────────────→ U6
U5 (Observer pitot airspeed sensor)  ─────────────────→ U9
U6 ─→ U7 (per-board ERC/DRC/gerber closeout)
U8 (tamper-mesh EMI blocker + Faraday/shielding) ─────→ U7
U7 ─→ U9 (REFERENCES.md + WBS/TODO closeout, fab release gate)
```

U4 and U5 have no hardware dependency on U1–U3 and can run in parallel with them.
U8's tamper-mesh item is a **standing fab blocker on Pilot** (13 DRC violations,
0.125 mm measured vs 8 mm required creepage) independent of everything else here —
it must close before U7's Pilot pass regardless of schedule.

---

## Phase A — Actuator bus reconciliation (U1–U3)

### U1. Pilot ESC/servo interface: retire PWM, adopt CAN-FD/RS-485 trunk

**Description:** Open-Secure-ESC's 50A/6S build and LibreServo_v4 both speak
CAN-FD + RS-485, not PWM. Pilot's `J_ESC` (PWM/BDSHOT, 4 ch) and `J_SERVO` (PWM,
4 ch) connectors in `Pilot.md` §14 are dead headers against this hardware. Retarget
actuator command/telemetry onto Pilot's existing isolated CAN-FD trunk (`J_CAN`,
ISOW1044BDFMR) and RS-485 trunk (`J_485`, pending its own ISOW1412 footprint swap —
already tracked in `TODO.md` §1.2a). Each nacelle's ESC and tilt servo become
addressed nodes on that trunk instead of point-to-point PWM wires.

**Acceptance criteria:**
- [ ] `Pilot.md` §14 field-connector table updated: `J_ESC`/`J_SERVO` marked
  removed-or-repurposed, with the CAN-FD/RS-485 trunk documented as the actuator
  path; power-only conductors (if any survive, e.g. BEC 5V/6V feed) called out
  separately from the retired signal pins.
- [ ] Bus topology decision recorded: point-to-point CAN-FD per nacelle vs. shared
  trunk with node addressing (Open-Secure-ESC and LibreServo_v4 both support
  multi-drop CAN-FD; confirm addressing scheme against both repos' protocol docs
  before choosing).
- [ ] `avionics/firmware/WBS.md` §4.2 EDF governor item rewritten: BDSHOT600/PRU-ICSS
  telemetry decode and EHRPWM output are removed from scope; replaced with a
  CAN-FD message producer (throttle/tilt setpoint) and consumer (RPM/V/I/temp
  telemetry, now sourced from the ESC's own authenticated telemetry frame instead
  of PRU-decoded BDSHOT).
- [ ] `docs/POWER_DISTRIBUTION.md` and `FlightEngineer.md` power budget rows for
  ESC/servo current draw re-checked against 50A-rated (not 40A, current text) ESC
  capacity — confirm this is a rating headroom change, not an actual draw change.

**Verification:**
- [ ] `kicad-cli sch erc` and `kicad-cli pcb drc` on `Pilot.kicad_sch`/`.kicad_pcb`
  after the connector-table edit — no new violations introduced.
- [ ] Manual check: trace the retired `J_ESC`/`J_SERVO` nets end-to-end; confirm no
  firmware code path still assumes EHRPWM output exists.

**Skills / workflow gate:** Use `pcb-designer` (communication-interfaces.md, §CAN
reference) to work the point-to-point-vs-shared-trunk decision before touching the
schematic. The unit is not done until the `kicad` skill's ERC/DRC analyzer runs
against the edited `Pilot.kicad_sch`/`.kicad_pcb` and reports the confidence-labeled
`trust_summary` this doc's own DRC Workflow policy requires — a bare `kicad-cli`
exit code is not sufficient evidence for the "no new violations" acceptance
criterion above.

**Dependencies:** None (this is the gating decision for U2/U3/U6).

**Files likely touched:** `avionics/kicad/Pilot/Pilot.md`, `Pilot.kicad_sch`,
`avionics/firmware/WBS.md`, `docs/POWER_DISTRIBUTION.md`,
`avionics/kicad/FlightEngineer/FlightEngineer.md`.

**Estimated scope:** L — touches schematic, board doc, firmware WBS, and power
budget together; if it grows further, split the connector-table/schematic edit from
the firmware-WBS rewrite.

---

### U2. LibreServo_v4 nacelle-tilt bus integration

**Description:** Close the gap `REFERENCES.md` REF-SENSOR-014 already documents:
`CAN-PERIPH-GW-1`'s `J_FLEX` exposes only a bare `FLEX_UART_TX/RX` pair, with no
local RS-485 transceiver for LibreServo's genuine differential daisy-chain bus.
That citation still says "LibreServo v2" — rename to v4 throughout and re-verify
the fork's current interface (ADM2587E RS-485 + ADM3055E CAN-FD, per
`LibreServo_v4/README.md`) matches what's cited.

**Acceptance criteria:**
- [ ] Decide and document the gateway-side RS-485 transceiver approach: add one at
  the wiring harness, or extend `CAN-PERIPH-GW-1`'s schematic with a dedicated
  local-drop transceiver — do not leave `J_FLEX` as a bare UART pair feeding a
  differential bus.
- [ ] `REFERENCES.md` REF-SENSOR-014 renamed/updated to LibreServo_v4, with the
  ADM2587E/ADM3055E part numbers and CRC-16 framing cited from
  `LibreServo_v4/README.md` (validated URL, per REFERENCES.md discipline —
  no invented section numbers).
- [ ] Two nacelle tilt servos wired as addressed CAN-FD/RS-485 nodes per U1's bus
  topology decision; AK7455 tilt-angle encoder feedback (already bus-published per
  `project_fleet_trust_module` design) reconciled against the same trunk, not a
  separate path.
- [ ] OPTIGA Trust M provisioning on LibreServo_v4 boards cross-checked against
  `project_optiga_trust_m_firmware` constraints (default world-readable 0xE140
  requires mandatory pairing before flight-article use).

**Verification:**
- [ ] DRC/ERC clean on any touched `CAN-PERIPH-GW-1` schematic changes.
- [ ] Bench check (when hardware available): LibreServo_v4 unit responds to an
  addressed CAN-FD setpoint frame and returns authenticated position/current
  telemetry over the same trunk.

**Skills / workflow gate:** Run `datasheets` against the ADM2587E and ADM3055E
parts named in `LibreServo_v4/README.md` **before** editing REF-SENSOR-014 — the
rename to v4 must carry a pulled-and-cached extraction, not a copy of the README
prose, per root CLAUDE.md's citation-authenticity policy. Use `pcb-designer`'s
communication-interfaces.md RS-485 guidance (120Ω termination, fail-safe bias) to
size the new gateway-side transceiver. Gate: `kicad` ERC clean on the touched
`CAN-PERIPH-GW-1` schematic.

**Dependencies:** U1 (bus topology/addressing decision).

**Files likely touched:** `avionics/kicad/CAN-PERIPH-GW-1/*`, `REFERENCES.md`,
`avionics/kicad/FlightEngineer/FlightEngineer.md` (6V servo rail row still says
"LibreServo v2").

**Estimated scope:** M.

---

### U3. Open-Secure-ESC 50A/6S integration + PID governor rewrite

**Description:** Wire the `CAN_485_faraday` build variant onto Pilot's CAN-FD trunk
per U1's decision, define the message schema (throttle setpoint, arm/disarm,
telemetry readback), and rewrite the EDF PID governor firmware around it.

**Acceptance criteria:**
- [ ] Message schema defined: setpoint frame (throttle %, direction if applicable),
  telemetry frame (RPM, voltage, current, temperature, fault flags), arm/disarm/
  e-stop frame — each carrying the host+message authentication Open-Secure-ESC
  already implements (this plan does not re-derive that crypto, only wires to it).
- [ ] PID governor firmware ported from PRU-ICSS/EHRPWM to CAN-FD message I/O;
  existing targets preserved (settle <200ms, overshoot <5%, |RPM_FWD−RPM_AFT|
  <100 RPM, fault latch on overtemp/overcurrent with no auto-recovery).
- [ ] Fault-latch behavior re-verified: does Open-Secure-ESC's own fault reporting
  satisfy "GCS ack required, no auto-recovery," or does Pilot firmware need to
  enforce that on top of the ESC's authenticated fault frame?
- [ ] New `REFERENCES.md` entry for Open-Secure-ESC (repo URL, `CAN_485_faraday`
  build path, protocol doc) — do not cite it informally in code comments without
  a REF-ID per root CLAUDE.md citation policy.

**Verification:**
- [ ] `governor_cal.py` bench-test re-run against the new CAN-FD path once hardware
  is available; confirm settle/overshoot/equalization targets still hold.
- [ ] CAN-FD cross-node RPM sync (fwd/aft pairing across River/Simon stacks, per
  firmware WBS §4.2) re-verified over the new bus.

**Skills / workflow gate:** Pull the `CAN_485_faraday` build's own protocol doc
and BOM via `bom`/`datasheets` before freezing the message schema — do not derive
frame layout from the generic README description alone. The governing gate is
`secure-controller-assurance`: run it against the new setpoint/telemetry/arm-
disarm frame set and confirm each maps to an existing SCA actuator-authentication
control (or is flagged as a new 🔒 gate to add) before this unit is considered
closed — this is the unit where Zero Trust stops being a sentence in `AGENTS.md`
and becomes a wire-level claim.

**Dependencies:** U1.

**Files likely touched:** `avionics/firmware/` (governor source), `REFERENCES.md`,
`avionics/kicad/Pilot/Pilot.md`.

**Estimated scope:** L — firmware rewrite is the bulk of it; split the message-
schema definition from the governor port if it runs long.

---

## Phase B — SG90/OSC and Observer sensing (U4–U5, parallel to Phase A)

### U4. OpenServoCore (SG90) TTL+CMAC bus finalize

**Description:** `avionics/firmware/WBS.md` §"Cargo control" already scopes a
DRV8833/HX711/SG90 state machine (IDLE→DEPLOY→DELIVERED→RETRACT→LATCHED) but
predates the CMAC-authenticated open-servo-core-secure backend. Finalize which
node hosts the TTL bus master (FlightEngineer, per the existing 6V-servo-rail
co-location in `FlightEngineer.md`, is the natural host — confirm rather than
assume) and update the firmware state machine to speak the authenticated
osc-native protocol instead of raw PWM.

**Acceptance criteria:**
- [ ] Host node for the SG90 TTL bus confirmed and documented (FlightEngineer vs.
  Pilot vs. a dedicated node) — this is a real open decision, not implied by
  existing docs.
- [ ] Cargo door + release servo state machine rewritten against osc-native
  protocol framing (break-framed, CMAC-authenticated) instead of PWM duty cycle.
- [ ] Nozzle-actuation SG90s (RCS proportional valve servos, `POWER_DISTRIBUTION.md`
  line ~174) get the same bus/protocol treatment — confirm they share the host
  node or need a separate drop.
- [ ] **Gate check, not a formality:** re-verify `github.com/OpenServoCore/open-servo-core`
  (and the `-secure` fork) hardware-maturity status against REF-SENSOR-015's "not
  shippable yet, validated to rev B" flag before any flight-article SG90+OSC
  procurement. If still true, note it explicitly in this unit's closeout — do not
  silently drop the gate because integration work is done.
- [ ] New `REFERENCES.md` entry for the `-secure` (CMAC) fork specifically, since
  REF-SENSOR-015 currently cites only the upstream, non-secure OpenServoCore.

**Verification:**
- [ ] ERC clean on whichever node's schematic carries the TTL bus master pins.
- [ ] Firmware state machine unit-tested against a simulated CMAC-authenticated
  frame sequence (or bench-tested if hardware is available).

**Skills / workflow gate:** The upstream-maturity re-check is a literal step, not
a note — actually query `github.com/OpenServoCore/open-servo-core` and the
`-secure` fork's current state before closing this unit; do not reuse the
REF-SENSOR-015 text from a prior pass. Run `secure-controller-assurance` against
the CMAC framing to confirm it maps to an SG90/actuator-class control in the same
way U3/U6 map the ESC and fleet-auth wiring — a servo class exception here would
be a silent Zero Trust gap. No `kicad` gate is required unless the host-node
decision changes that board's schematic (see Files below).

**Dependencies:** None (parallel to Phase A).

**Files likely touched:** `avionics/firmware/WBS.md`, `REFERENCES.md`,
`docs/CARGO_WINCH_SPECIFICATION.md`, whichever board hosts the TTL bus.

**Estimated scope:** M.

---

### U5. Observer pitot-tube airspeed sensor

**Description:** No board in the current design has a pitot/airspeed sensor —
Pilot's purpose text claims one but no connector, IC, or REF-ID exists anywhere
(confirmed by repo-wide search). Add it to **Observer** per user direction, and
correct Pilot's stale claim.

**Acceptance criteria:**
- [ ] Sensor selection: a differential-pressure airspeed IC (I2C is the natural
  fit for Observer's MSPM0G3507, which already runs I2C for other peripherals)
  — candidate parts to evaluate via the `datasheets`/`bom` skills, not assumed:
  e.g. TE Connectivity MS4525DO or Sensirion SDP3x family. **Do not commit a part
  number to `REFERENCES.md` without pulling and citing its actual datasheet** —
  mark as "requires verification" per root CLAUDE.md policy until then.
- [ ] MSPM0G3507 peripheral allocation checked for conflicts: Observer already
  uses UART1 (TFmini-S ToF), SPI (KSZ9477 mgmt + TPM), and I2C for its own PMIC/
  regulator monitoring if any — confirm a free I2C or spare UART exists before
  committing to a bus.
- [ ] New `J_PITOT` connector added to Observer's field-connector set (JST-GH,
  matching the board's existing connector family), wired to the chosen bus, with
  pull-ups sized per the sensor's I2C spec if I2C is chosen.
- [ ] Firmware driver added to Observer's MSPM0G3507 firmware scope (or wherever
  Observer's application logic lives) publishing airspeed onto the same CAN-FD
  trunk Observer already uses, so Pilot's flight-control loop can consume it
  cross-node instead of hosting the sensor itself.
- [ ] `avionics/AGENTS.md` and `Pilot.md` purpose text corrected: remove the
  unbacked "airspeed sensor" claim from Pilot's sensor list, and add Observer as
  the airspeed source in the architecture description.
- [ ] Mechanical coordination flagged (not solved here): a pitot tube needs an
  external-airflow mounting point — check whether the bow sensor pod location
  (Observer's nose install) has room for a forward-facing pitot mast, or whether
  this needs a dedicated mount design task handed to the airframe subsystem.

**Verification:**
- [ ] ERC clean on the new `J_PITOT` connector and its bus wiring.
- [ ] Manual check: confirm the chosen bus doesn't collide with an existing
  Observer peripheral (cross-reference `OBSERVER_SOM_NETMAP.md`/pinmap CSV).

**Skills / workflow gate — strict order, not parallel steps:**

1. `datasheets` pulls and caches the candidate sensor's actual datasheet (MS4525DO
   or SDP3x family) — **this must complete before any `REFERENCES.md` edit**, per
   root CLAUDE.md's no-fabrication policy; U5 is the highest citation-risk unit in
   this plan because it introduces a part with zero prior art in the repo.
2. `bom` confirms sourcing/availability for the selected part.
3. `pcb-designer` (§6.3 I2C bus pattern, §3 pull-up sizing) informs the `J_PITOT`
   connector and bus design.
4. `kicad` ERC gate on the new connector and its wiring.
5. `kidoc` regenerates Observer's HDD scaffold once wired — if the scaffold's
   auto-run `kicad` analysis still shows the sensor as absent, the unit is not
   done, regardless of what the `.md` prose claims.

**Dependencies:** None (parallel to Phase A); feeds U9 documentation closeout.

**Files likely touched:** `avionics/kicad/Observer/Observer.md`,
`Observer.kicad_sch`/pinmap CSV, `REFERENCES.md`, `avionics/AGENTS.md`,
`avionics/kicad/Pilot/Pilot.md`.

**Estimated scope:** M — sensor selection + connector/bus wiring is S/M; if the
mechanical pitot-mast question turns into real geometry work, that's a separate
airframe-subsystem task, not part of this unit's scope.

---

## Phase C — Fleet security wiring (U6)

### U6. Host + message authentication wiring across ESC/servo/SG90 endpoints

**Description:** Root `AGENTS.md`'s Zero Trust requirement ("every message ...
authenticated ... every node state change") now has three new authenticated
endpoint classes (ESC, nacelle servo, SG90) that need key provisioning tied into
the existing TPM/OPTIGA fleet architecture (`project_fleet_trust_module`,
`project_optiga_trust_m_swap`, `project_optiga_trust_m_firmware` memory).

**Acceptance criteria:**
- [ ] Key provisioning path documented for each endpoint class: does Pilot's own
  TPM sign/verify CAN-FD frames to/from the ESC and tilt servo, or does each
  endpoint's own secure element (Open-Secure-ESC's, LibreServo_v4's OPTIGA Trust
  M, OSC's CMAC key) operate independently with Pilot only relaying?
  This is a real architecture decision — do not assume "it just works" because
  each repo independently implements auth.
- [ ] Pairing/provisioning step identified for LibreServo_v4's OPTIGA Trust M
  (mandatory pairing against default world-readable 0xE140, per
  `project_optiga_trust_m_firmware` memory) as a production/flight-article gate,
  not a dev-time skip.
- [ ] Failure-mode behavior specified: what happens on an authentication failure
  from an ESC or servo frame mid-flight (reject + fault-latch vs. fail-safe
  default) — ties into U3's fault-latch acceptance criterion.

**Verification:**
- [ ] Design review checklist item: every new bus frame type introduced by
  U1–U4 has an explicit auth field and a documented verification path.

**Skills / workflow gate:** `secure-controller-assurance` is the governing skill
for this entire unit, not an optional cross-check — its 96 controls across the
5 platform overlays are the mechanism for answering the "does Pilot's TPM relay
or does each endpoint self-authenticate" architecture question with a control
mapping instead of a guess. Run it once per endpoint class (ESC, nacelle tilt
servo, SG90) and record which overlay applies to each; an endpoint class with no
mapped control is an open gap, not a pass.

**Dependencies:** U1, U2, U3, U4.

**Files likely touched:** `avionics/AGENTS.md`, board `.md` files touched above,
possibly a new `docs/FLEET_AUTHENTICATION.md` if this doesn't fit cleanly
elsewhere.

**Estimated scope:** M.

---

## Phase D — Closeout (U7–U9)

### U7. Per-board ERC/DRC/gerber closeout

**Description:** Independent of the actuator-bus work above, every avionics board
already carries a known ERC/DRC backlog (from `avionics/TODO.md`, current as of
this plan's date):

| Board | Known backlog |
|---|---|
| Pilot | 48 ERC + 76 DRC hard; PB2-P2 header fully-unwired defect (unresolved root cause); tamper-mesh creepage violation (13 DRC, blocks fab — see U8) |
| XO | 219 ERC + 154 DRC hard; TPM footprint wrong land size (4×4/0.4mm → needs 5×5/0.5mm); Zigbee RF chain never added (scope gap) |
| Commo | TPM/R/C not yet routed to SPI1/TPM_IRQN/TPM_RSTN nets; FCC Part 15 §15.235 pre-compliance checklist open |
| Flight Engineer | 213 DRC hard; full resync to trust-module schematic needed |
| Observer | 124 DRC; RS-485/§H section never reached layout |
| CAN-PERIPH-GW-1 | 47/296 nets still unrouted; OPTIGA Trust M swap pending |

**Acceptance criteria:**
- [ ] Each board above reaches 0 ERC errors / 0 DRC hard violations, or every
  remaining violation is documented in `TODO.md` with the specific DRC rule and
  reason (per `avionics/AGENTS.md` DRC Workflow policy) — no silent skips.
- [ ] Gerbers generated for every board that reaches clean DRC, per root
  `AGENTS.md` §7 production-completeness bar.
- [ ] This unit runs **after** U1/U2/U3/U5's hardware edits land on the affected
  boards (Pilot, CAN-PERIPH-GW-1, Observer) — DRC-cleaning a connector table
  that's about to be re-edited is wasted effort.

**Verification:**
- [ ] `kicad-cli sch erc` / `kicad-cli pcb drc` output attached or referenced per
  board in that board's `.md` status file.

**Skills / workflow gate (per board):** Run the `kicad` skill's full analyzer
(ERC, DRC, DFM, BOM extraction) rather than raw `kicad-cli` — the analyzer's
confidence-labeled findings are what let a residual violation be "documented in
`TODO.md` with the specific DRC rule and reason" per `avionics/AGENTS.md`, versus
a bare pass/fail. Follow each board's `kicad` pass with an `emc` pre-compliance
check before generating gerbers — Pilot and Observer both carry explicit EMC
compliance targets (IEC 61000-4-2/4/5, MIL-STD-461G) in their own `.md` files that
a DRC-clean board does not automatically satisfy. A board is not ready for
gerbers on DRC-clean alone if its `.md` file states EMC targets and no `emc` pass
has been run against it.

**Dependencies:** U1, U2, U3, U5 (for the boards each touches); U8 (Pilot
specifically, tamper-mesh blocker).

**Files likely touched:** all `avionics/kicad/<board>/*.kicad_sch`/`.kicad_pcb`.

**Estimated scope:** XL overall — treat as one task per board (6 boards), each
S–M once the upstream hardware edits are stable.

---

### U8. Tamper-mesh EMI blocker + Faraday/shielding closeout

**Description:** Pilot's per-domain tamper-detect mesh currently routes through
the isolated `GND2_CAN`/`GND2_ETH` domains at measured spacing as low as 0.125 mm
— a hard fab blocker (needs ≥8 mm creepage per IEC 62368-1 Annex G, already cited
as REF-IEC-001 §5.5.2). This is pre-existing, tracked, and orthogonal to the
actuator-bus work, but must close before Pilot's U7 pass.

**Acceptance criteria:**
- [ ] Tamper mesh redesigned as a per-domain (not cross-domain) anti-tamper mesh
  per the existing TODO.md item ("Redesign the tamper mesh as a per-domain
  anti-tamper mesh (all bays)").
- [ ] Tamper signal carried over the link for TPM-less boards (existing open item).
- [ ] Faraday cage / box design for all PCBs, and the shielded/twisted-pair wiring
  spec for inter-bay harnesses — both currently unstarted per `TODO.md`.
- [ ] Per-footprint repositioning required by this fix is **referred to the user**
  per `avionics/AGENTS.md` footprint-placement policy — this unit should surface
  the specific moves needed, not silently execute them.

**Verification:**
- [ ] DRC re-run confirms the 13 cross-domain violations are resolved (0.125mm →
  ≥8mm creepage / ≥1.5mm clearance).

**Skills / workflow gate:** Use `pcb-designer`'s protection-reliability.md
isolation guidance to redesign the per-domain mesh, and `emc`'s shielding
guidance for the Faraday-cage/twisted-pair harness spec (both currently
unstarted per `TODO.md`). Gate: `kicad` DRC confirms the creepage/clearance fix
numerically — this unit's own acceptance criterion is a measured distance, not a
design intent, so the gate has to be the analyzer's measured output, not a
visual review of the new mesh geometry.

**Dependencies:** None — can start immediately, independent of Phase A–C.

**Files likely touched:** `avionics/kicad/Pilot/Pilot.kicad_pcb`, EMI hardening
docs under `avionics/emi-hardening/`.

**Estimated scope:** L.

---

### U9. Documentation, REFERENCES.md, and WBS/TODO closeout

**Description:** Propagate every closed item above into the federated WBS/TODO
structure per root CLAUDE.md instructions, and reconcile all new/changed
citations.

**Acceptance criteria:**
- [ ] `REFERENCES.md` updated: new entries for Open-Secure-ESC and the
  open-servo-core-secure fork; REF-SENSOR-014 renamed to LibreServo_v4 with
  current part numbers; pitot sensor entry added once selected (U5), marked
  "requires verification" if not yet datasheet-confirmed.
  Any citation that cannot be traced to a validated URL is marked
  "requires verification" with a TODO §0.x item — never invented.
- [ ] `avionics/TODO.md` and `avionics/WBS.md` updated: close every item this
  plan resolves, add any newly-discovered sub-items (e.g., U6's endpoint-auth
  architecture decision) as proper WBS entries.
- [ ] Root `TODO.md`/`WBS.md` cross-references updated where they index avionics
  items.
- [ ] `avionics/AGENTS.md` architecture summary corrected for the actuator-bus
  change (PWM references removed) and the Observer-airspeed correction.
- [ ] Final production-readiness sign-off: every board in U7's table either ships
  gerbers or has its residual gap explicitly documented as deferred, with a
  reason.

**Skills / workflow gate:** Regenerate each touched board's status doc with
`kidoc` (`kidoc_scaffold.py --type hdd` or `design_review`) rather than
hand-editing prose — the scaffold's auto-run `kicad`/`emc` analyses are the
mechanism that keeps the `.md` files from drifting out of sync with the boards
again, which is exactly the failure mode `avionics/kicad/Pilot/Pilot.md`'s own
"known divergence" note (schematic vs. as-placed PCB) already shows happened
once. The final gate is `project-overseer`: run its WBS/TODO consistency check
across `avionics/TODO.md`, `avionics/WBS.md`, and root `TODO.md`/`WBS.md` to
confirm no checkbox is left unchecked once its own text says resolved (the
project's standing rule) and no item this plan closes is orphaned in one file
but not the other.

**Dependencies:** U7 (and effectively everything else, since this is the closeout
pass).

**Files likely touched:** `REFERENCES.md`, `avionics/TODO.md`, `avionics/WBS.md`,
root `TODO.md`, root `WBS.md`, `avionics/AGENTS.md`.

**Estimated scope:** M.

---

## Checkpoint: After Phase A (U1–U3)

- [ ] Pilot's connector table and firmware WBS no longer reference PWM/BDSHOT for
  ESC or nacelle-servo control.
- [ ] Bus topology/addressing decision is written down somewhere durable (not just
  this plan) before U2/U3 implementation proceeds independently.

## Checkpoint: After Phase B (U4–U5)

- [ ] OSC hardware-maturity gate re-checked and its status stated plainly, whatever
  it is.
- [ ] Pitot sensor is either selected-and-cited or explicitly deferred with a
  reason; Pilot's stale airspeed claim is corrected either way.

## Checkpoint: After Phase C (U6)

- [ ] Every new authenticated bus frame type has a documented key-provisioning
  path and failure-mode behavior — no "trust me, the sub-repo handles it" gaps.

## Checkpoint: After Phase D (U7–U9)

- [ ] Every avionics board is at 0 ERC/0 DRC-hard or has documented exceptions,
  each backed by a `kicad` skill run (not raw `kicad-cli`) and, where the board
  states EMC targets, an `emc` pre-compliance pass.
- [ ] `REFERENCES.md` has no fabricated or stale citations touching this plan's
  scope — every new/changed entry traces to a `datasheets` extraction.
- [ ] WBS/TODO federation reflects reality — no checkbox left unchecked once its
  own text says resolved (standing project rule), verified by a `project-overseer`
  consistency pass, not by visual scan.

---

## Risks & Dependencies

| Risk | Impact | Mitigation |
|---|---|---|
| OpenServoCore upstream still not shippable (REF-SENSOR-015) | Blocks flight-article SG90 procurement even after integration work is done | U4 treats this as a live gate, re-checked at closeout, not assumed cleared |
| Bus topology decision (U1) made informally and not written down | U2/U3 diverge on addressing scheme, rework later | Checkpoint after Phase A explicitly requires a durable record |
| PB2-P2 unwired-header defect (Pilot, pre-existing) turns out to sit on the same net group as the new CAN-FD trunk wiring | Could compound with U1's connector-table rework | Investigate the PB2-P2 defect before or alongside U1, not after |
| Pitot sensor selection invents a part/spec to move fast | Violates root CLAUDE.md no-fabrication policy | U5 explicitly requires datasheet pull via `datasheets`/`bom` skills before REFERENCES.md entry |
| Tamper-mesh redesign (U8) requires footprint moves | `avionics/AGENTS.md` requires referring footprint repositioning to the user | U8 acceptance criterion calls this out explicitly |

## Definition of Done

- All nine units' acceptance criteria checked.
- All four phase checkpoints passed.
- Every board in the U7 table ships gerbers or has a documented, reasoned
  deferral.
- No PWM references remain in any document describing ESC or nacelle-tilt-servo
  control paths.
- Observer supports the pitot-tube airspeed sensor; Pilot's stale claim is gone.
- `REFERENCES.md`, `avionics/TODO.md`, `avionics/WBS.md`, and root `TODO.md`/`WBS.md`
  all reflect the closed state — no stale checkboxes.
- Every authenticated endpoint class introduced by this plan (ESC, nacelle tilt
  servo, SG90) has a `secure-controller-assurance` control mapping on record, not
  an assumed-authenticated note.
- Every board shipping gerbers has a `kicad`-skill analyzer report and, where
  the board states EMC targets, an `emc`-skill pre-compliance pass on record —
  see the Skills & Workflow Map above.

## Sources & Research

- `avionics/AGENTS.md`, `avionics/TODO.md`, `avionics/WBS.md` (current open-item state)
- `avionics/kicad/Pilot/Pilot.md` (connector table, EMC targets, PB2-P2 defect)
- `avionics/kicad/Observer/Observer.md` (architecture, MCU peripheral allocation, no pitot found)
- `avionics/firmware/WBS.md` §4.2, §"Cargo control" (current PWM/BDSHOT governor scope, SG90 state machine)
- `REFERENCES.md` REF-SENSOR-013/014/015 (servo fleet citations, LibreServo v2→v4 staleness, OSC maturity flag)
- `docs/POWER_DISTRIBUTION.md`, `avionics/kicad/FlightEngineer/FlightEngineer.md` (power budget rows for ESC/servo)
- `LibreServo_v4/README.md`, `Open-Secure-ESC/README.md`, `open-servo-core-secure/README.md` (backend protocol confirmation)
- Repo-wide grep confirming no existing pitot/airspeed/MS4525/SDP3 references anywhere in the codebase
