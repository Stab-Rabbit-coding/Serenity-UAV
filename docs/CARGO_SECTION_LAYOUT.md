# Cargo Section Layout — Rev T5f (2026-09-21; Rev T5e 2026-09-16, Rev T5/T5b 2026-09-15 base)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**AI note:** Drafted by Claude (model: Claude Opus 5, Anthropic) under the author's
direction, 2026-09-15 / 2026-09-16, per `AGENTS.md` §3 AI attribution.
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by/4.0

Single source of every station in this document: `tools/cargo_layout_fit.py`
(imported by `merge_cargo_interior.py`; exported to
`airframe/openscad/fuselage/cargo/cargo_layout_t5_params.scad` for the SCAD parts).
Run `tools/cargo_layout_fit.py --plot` for the proof (`docs/img/cargo_layout_t5_sections.png`).

> ⚠️ **ENGINEERING REVIEW REQUIRED** — see the notice in `docs/TILT_ACTUATOR_SELECTION.md`.

## 0a. Rev T5f (2026-09-21) — what changed

One addition: the **cargo-door servo gateway** (GW-CARGO-DOOR, a
`SKIPPER-CAN-PERIPH-GW-PCB` at `N_STACKS=1` hosting the three SG90-class
door/release servos — `docs/CARGO_DOOR_GATEWAY_SPEC.md`) is placed standing
transverse on the solid 6.2 mm belly slab at the forward rim of the clamshell
aperture, Y −17.25..−2, Z 10.2..44.1, on a printed card-edge tray
(`gateway_door_tray.stl`, 5.0 g) bolted to four new 7 × 7 mm slab bosses
(X_CL ± 19, Y −13 / −6, M3 heat-set). `cargo_layout_fit.py` PASS (0 hit, 0 near,
0 pair overlap); the ray-probed pocket has 4 mm to the aperture rim, 2.75 mm to
the ramp-fairing wall at floor level, 19.5 mm to the chin shelf. Shell re-merged
(`merge_cargo_interior.py` Rev T5f: `t5_gw_door_bosses`, unclipped — the slab is
in the ramp void of the outer-skin envelope — and carved out of `DUCT_CUT`).
`DRV8833-CARGO` + `cargo_drv8833_tray.stl` are retired by it. Shell 287.7 cm³ / 302.1 g
(+0.5 g), watertight, one body; all §7 gates re-run PASS.

## 0. Rev T5e (2026-09-16) — what changed

The 2026-09-16 pass found three defects in the T5b bracket (§4: T5d-1 motor
into the wheel, T5d-2 controller-board rails through the worm, T5d-3 web not
cut for the worm) and left the two CN nodes and the cargo Observer unplaced.
The "tilted-motor" fix proposed at the end of that pass was tried first and
**does not work**: rotating a coaxial motor about the wheel does not change
its distance from the wheel tip, and any worm swung ≥ 5° aft lands on the port
hoist line at Y 55.5. What was built instead:

| Change | Was (T5b/T5d) | Now (T5e) |
|---|---|---|
| Gearmotor | Pololu 25D HP 9.7:1 (#1571), Ø25 × 48 | **Pololu 20D 25:1 CB 6 V (#3712)**, Ø20 × 41 + 6 mm rear shaft, REF-ACT-001 |
| Worm | 4-start m1 Ø24, 10:1, C 32 | **6-start m1 Ø26, 6.67:1, C 33**, lead 13.0°; motor body 2.0 mm above the wheel tip |
| Nacelle rate | 168 °/s | **144 °/s no-load, 111 °/s at max efficiency** (TILT-CTL-07 ≥ 120 met no-load) |
| Gear plane | X −123.75 | X −122.75 (worm tip stays at −139.25, 3.2 mm off the cradle) |
| Worm offset | +2.5 mm aft | 0 (worm aft end 3.9 mm forward of the hoist line, was 1.4) |
| Controller board | bracket web, inboard face, Y 38..81 / Z 93..129.5 — through the worm | **bracket web, OUTBOARD face**, Y 55..97.9 / Z 83..119.5, 7.4 mm envelope, in the shoulder pocket |
| Bracket feet | (10.6, 123.09) (68.6, 123.09) (62, 86) | **(10.6, 124.09) (40, 124.09) (64, 77)** |
| Aft nodes N2/N4 | Y 89.5..111.5 | **Y 99.5..121.5** (clear of the boards; 0.5 mm into the splice-collar ring zone, checked at 4.5 mm) |
| Chin nodes N1/N3 | unplaced (flanks 0.5 mm short) | **flat on the chin floor under the battery nose**, Y −58..0, Z 66..88, 37 mm wide each, shared 10 mm cable channel; `chin_node_shelf.stl` on 4 floor bosses |
| Cargo Observer | unplaced | **standing behind the payload box**, Y 108.5..128.5, Z 14.2..85, 76.8 wide; 4 belly bosses; camera looks forward-down through the aperture |
| Void formers | 4 | 5 (`node_bay` added; chimney now Z 90..131) |
| Shell | 287.8 cm³ / 302 g | 287.2 cm³ / 301.6 g, re-merged |

---

## 1. What the section now carries (hull frame, mm; X = +port, Y = +aft, Z = +dorsal)

| Item | Station | Part / feature | Mount |
|---|---|---|---|
| Nacelle-tilt actuator, port | motor axis (X −125.25, Z 102.09) along Y, face plate Y 39.1..41.6, body Y −7.9..39.1; worm Y 41.6..51.6; wheel on the drive shaft (Y 46.6, Z 69.09) at X −127.75..−122.75 | `tilt_actuator_bracket_port.stl`, `tilt_actuator_worm.stl`, `tilt_actuator_wheel.stl`, Pololu 20D 25:1 CB 6 V (#3712) | 3 × 12 mm foot bosses in the shell at (Y 10.6, Z 124.1), (Y 40.0, Z 124.1), (Y 64.0, Z 77.0), M3 heat-set |
| — starboard | mirror of the bracket about X_CL = −169.85; worm and wheel translated | `tilt_actuator_bracket_stbd.stl` | mirrored bosses |
| Tilt brake (per side) | collar Y 52.1..56.1 on the worm's 18 mm shaft (with a Ø6 magnet for the AEAT-8800 in the guide); guide block X −134.25..−119.75, Y 57.1..62.1 on the web's inboard face; solenoid Y 62.1..86.1, axis 1.5 mm inboard of the worm's | `tilt_brake_guide.stl`, `PIN-2X22`, `SOL-TILT-BRAKE` | 2 × M2.5 through the bracket web (Z ±11) |
| Aft avionics nodes N2 FC2 (port) / N4 FC3 (stbd) | X_CL + 30 / − 31, Y 99.5..121.5, Z 87..124, transverse, pouch-wrapped | PB2I + cape in foil pouch, saddle (SCAD not yet authored) | `PRINT-NODE-SADDLE` |
| Chin avionics nodes N1 CN2 (port) / N3 CN3 (stbd) | X_CL + 5..42 / − 5..−42, Y −58..0, Z 66..88, lying flat, connector edges inboard on a shared 10 mm cable channel | PB2I + cape in foil pouch on `chin_node_shelf.stl` (plate Y −52..1.6, Z 63.6..66; two cam straps each) | 4 × 10 mm floor bosses at (X_CL ± 30, Y −49) and (X_CL ± 20, Y −33, on the ramp fairing), M3 heat-set |
| Cargo Observer tray | X_CL ± 38.4, Y 108.5..128.5, Z 14.2..85, standing (board plane transverse); nadir camera on the top edge looking forward-down through the clamshell aperture | envelope of `cargo_vera_faraday.scad` Rev S1 (76.8 × 70.8 × 20) — tray SCAD to be re-authored in hull frame to these bosses (OBS-CARGO) | 4 × belly bosses (X_CL ± 30, Y 112.5 / 117) forward of the splice-collar ring, M2.5 heat-set |
| Tilt controller board (per side) | card-edge rails on the bracket web's **outboard** face, Y 55..97.9, Z 83..119.5, component side toward the web | Open-Secure-ESC tilt controller build `6s/10A/BRUSHED_CAN_485_isolation` (REF-ESC-001), ≤ 42.9 × 36.5 mm, ≤ 4 mm parts web-side | rails + cable tie |
| Cargo-door servo gateway (GW-CARGO-DOOR) | board X_CL ± 24.5, Y −14.5..−12.9 (standing transverse, component side aft), Z 15.6..41.1; parts to Y −3.9 aft / −17.5 fwd; tray X −196..−143.75, Y −17.25..−2, Z 10.2..44.1 | `gateway_door_tray.stl` (card-edge rails, keeper tie) + `CAN-PERIPH-GW-DOOR` (`N_STACKS=1`) — `docs/CARGO_DOOR_GATEWAY_SPEC.md` | 4 × 7 mm slab bosses at (X_CL ± 19, Y −13 / −6), M3 heat-set (Rev T5f) |
| Flight battery | X −194.85..−144.85, Y −58..+84, Z 90..128 (centred, longitudinal) | `battery_cradle.stl` (inverted U, roof-hung) | 4 × 10 mm roof hanger bosses at (X −179.85/−159.85, Y −50 / +80), M3 heat-set |
| Mission payload (README steps 6/9) | 76.2 (X) × 101.6 (Y) × 76.2 (Z) box at the door crown Z 8.72, centred Y 55.5 — long side along Y | keep-out | — |
| Hoist (Phase 7 reserve) | **twin-line bridle** at X −200.75 / −138.95, Y 55.5; drums Ø16 at Z 133.4..149.4 on a common X axle; two 10 mm roof pedestal bosses at X −211.75 / −127.95 | `CARGO_WINCH_SPECIFICATION.md` needs a Rev D (twin drum) | pedestal bosses, M3 |
| GPS antennas ×2 | dorsal cups Ø40 at (X −135, Y 92) and (X −205, Y 92): Ø36 × 6 flush recess, Ø6.5 SMA bore, 4 × M2 on Ø44 | shell feature (first time cut in hull frame) | — |
| Canonical forward cargo ramp | X −194..−142, Z 8..44 on the 25°-canted forward face — **sealed** by a fused 2 mm fairing + 6 mm frame lip, panel lines 0.8 deep, hinge line at Z 14 | shell feature (KTD1, plan 2026-08-25-002 U2) | — |
| Wing root (unchanged) | spar socket Y 21 / Z 66.85, bonded root flange Y −9..51 × Z 27..107, drive shaft Y 46.6 / Z 69.09, harness bores Y 1 / 37.5 / 46.6 | — | — |
| Landing-gear bays (unchanged) | sponson wells, fore Y −16..20 / aft Y 80..110 | — | — |

## 2. Decisions

| ID | Decision | Why |
|---|---|---|
| **D-T5-1** | Battery lives in the cargo roof band, on the centreline, Y −58..+84 | 18 % of AUW; the hover thrust line is the tilt axis (Y 46.6) and a lateral tandem pair has no other pitch trim — the pack must sit at that station. Nothing else in the airframe has 142 mm of clear length there. |
| **D-T5-2** | Hoist is a twin-line bridle straddling the battery; payload goes up long-side along Y | A single centred line passes through the battery; a single off-centre line puts the 76.2 mm box into the actuator wheels (clear span between wheels 82.2 mm). Two lines at ±30.9 mm clear both, and stop the box spinning. |
| **D-T5-3** | Inara and River avionics trays leave the cargo section (bosses gated off, constants kept) | With the battery centred and the actuator bodies on both walls there is no 40 × 60 × 55 mm dorsal pocket left that clears everything by 3 mm (`cargo_layout_fit.py` proved each candidate). The trays are ~250 g each and CG-insensitive; the battery is not. Relocation target: the head (Bay A already there) or the middle inner neck (Simon precedent). **Owner to confirm.** |
| **D-T5-4** | Cargo section is not foamed by default | Its panels are under the 124 mm unbraced limit that set the 2 mm foam-fill wall; the bay and roof band must stay serviceable (battery swap from below, tray/winch access). The chin may be poured optionally — void formers provided (§6). |
| **D-T5-5 (T5b → T5e)** | Tilt actuator = 6-start worm 6.67:1 on a Pololu 20D 25:1 gearmotor + pin brake, own fused feeds (T5b: 4-start / 25D — retired by T5d-1) | `docs/TILT_ACTUATOR_SELECTION.md` |
| **D-T5-6 (T5e)** | CN2/CN3 lie flat on the chin floor under the battery nose on a printed shelf; the cargo Observer stands behind the payload box | The chin flanks were measured short three times; the chin floor (Y < 4.7, Z < 88, 113 mm wide) was clear first try on both sides at the 2 mm static budget. The Observer's only other 20 mm slot was the belly aperture. D-T5-3 CLOSES: all four nodes are in the cargo section. |

## 3. Battery — cradle vs. straps (summary; full case in `battery_cradle.scad` header)

Straps or hook-and-loop alone locate the pack by friction only and give no
vibration control; a printed inverted-U cradle gives positive location in X, Y,
+Z, roll and yaw, leaves the two 50 N cam straps carrying only the hanging load
(FOS 5.4 at 2.5 g), and the 3 mm silicone-foam pad against the ceiling is the
isolator (f_n ≈ 180 Hz, ~83 % isolation at the 470 Hz EDF shaft rate; modulus
ASSUMED). The pack is exchanged **downward** through the open bay with the winch
not fitted (Phase 5) — no roof access. Mass 39 g vs the 140 g keel-rail tray it
retires (MA-6 closed). Battery station is fixed by the cradle; fore/aft CG trim
moves to the ledger (A0), not to a rail.

## 3a. Avionics nodes in the cargo section — measured (2026-09-15, owner direction)

Owner direction: all four control nodes (Inara = CN2 + FC2, River = CN3 + FC3)
stay in the cargo section, any orientation, in a Faraday **pouch** (foil, ~1 mm)
rather than the rigid tray, with cable room. Node envelope used: PB2I + cape
stack **58 × 37 × 22 mm** pouch-inclusive (stack height VERIFY at first article),
plus a 10 mm cable zone on the connector edge. Every candidate was proved by
`tools/cargo_layout_fit.py` against the shell and every other envelope.

| Candidate | Result |
|---|---|
| Shuttle-profile shoulder pockets outboard of the tilt brackets | **No.** ~300 cm³ gross each, but the largest window is 55 × 31 mm (Y 52..107, Z 81..112) vs the 35 mm board — 4 mm short; two nodes across need 47 mm vs 40–43. |
| **Aft strip behind the battery** — N2 FC2 port / N4 FC3 stbd, transverse, Y 89.5..111.5, Z 87..124, X centres X_CL + 30 / X_CL − 31 (0.5 mm stbd bias: the port shoulder curves in earlier), outboard-top pouch edge chamfered 5 mm | **Yes — PASS.** Mount: saddles bolted to the battery cradle's aft wall (8 × M3 holes added to `battery_cradle.scad`); the GPS cups (Z ≥ 139) are above, the payload crown (84.92) below, the aft thwart (Y 116.75) behind. |
| **Chin flanks beside the battery nose** — N1 CN2 port / N3 CN3 stbd, standing on edge, X = stack, Y −49..−12, Z 75..133, cable zone on the lower aft edge | **Port yes, starboard no — by 2.7 mm.** Two changes were needed even to get this far: (1) the tilt gearmotor loses its rear encoder (#1571, 25Dx48L instead of the #4802 25Dx63L) so its forward end moves from Y −23.9 to −8.7, and the LibreServo AEAT-8800 reads a magnet in the worm's brake collar instead; (2) the node is raised above the chin floor fillet. Then the port flank leaves 1.5–4 mm to the wall; the **starboard chin flank is 2.7 mm narrower than port** (hull asymmetry about X_CL: port wall X −112 vs stbd −225 at Y −45 / Z 80) and offers 21–28 mm against the 26 needed. |

Recovery for the starboard chin node, if wanted: shift the battery cradle 3 mm to
port (lateral CG effect 0.6 mm) **and** bond the pouch's outboard foil to the
wall as the liner (zero skin gap) — both flanks then have 0.5–1.5 mm. That is a
zero-margin fit and is **not** in the baseline; `CHIN_NODES` in
`cargo_layout_fit.py` is gated off with the numbers so it can be re-run.

**2026-09-16 — battery-shift trial (owner asked):** with the worm offset 2.5 mm
aft (motor forward end Y −6.2), the cradle 1.5 mm to port and the nodes at
Y −46.2..−9.2 / Z 66..124, the **port** node still touches the bay sidewall at
its aft-bottom corner (X −117 at Y −25..−17, Z 66..82) and the **starboard** node
interferes ~1 mm along its outboard face (wall X −221..−224 vs node −223.75).
Cutting the cradle gap to 2 mm and bonding the pouch foil to the wall gets both
to ~0.5 mm. **Does not fit.** The cradle is back on the centreline; the worm
offset is kept (harmless, and the T5e bracket wants it).

**Rev T5e (2026-09-16) — resolved.** The chin FLOOR, not the flanks: both nodes
lie flat under the battery nose (Y −58..0, Z 66..88, 37 mm wide each, 10 mm cable
channel between them) — zero hit, zero 2 mm-near volume on both sides, first try.
The aft pair moved to Y 99.5..121.5 to clear the relocated controller boards. The
"tilted-motor" bracket proposed above was tried and abandoned (§0). **All four nodes
are in the cargo section; D-T5-3 closes.**

## 4. Actuator packaging findings (measured, not assumed)

* The lower sidewall at the shaft station is at X −115 (ray-probed at Y 46.6 / Z 62
  and Y 55 / Z 70), not the −86 the retired pad comments assumed; the bonded root
  flange's inner face is therefore at −120 there. The wheel plane sits at −123.75.
* The hoisted payload box (Z ≤ 85) forbids any motor body beside it: the motor must
  sit **above** Z 88 → worm above the wheel, C = 33 (T5e).
* The DS3225 standoff pads (Rev T4, X −158.5 / −221.5, 53.5 g) are gone; six 12 mm
  foot bosses replace them (−53.5 + 23.4 g). WA-R15a and MA-5 close by removal.
* Bracket foot 2 was moved twice to clear the aft LG bay's upper bolt bores
  (`landing_gear_wing_clearance.py --proud` fouled at Y 74 and Y 66; clear at Y 62 / Z 86);
  in T5e it is at (Y 64, Z 77): over the mortise block, 2 mm above the harness bores,
  2.6 mm forward of bolt3, 2 mm under the controller board. Feet 0/1 are in the top row.
* **T5d-1 (CLOSED by T5e):** at C 32 the Ø25 motor body's underside (Z 88.6) sat
  1.5 mm inside the Ø42 wheel's tip circle (Z 90.1). The general fact: for a motor
  coaxial with its worm the gap is `WORM_PD/2 − MOTOR_D/2 − m` — independent of C and
  of the worm's angle on the wheel — and the worm's inboard reach against the battery
  cradle caps WORM_PD at 26. So the motor had to be Ø ≤ 20 (2 mm gap) — the 20D.
* **T5d-2 (CLOSED by T5e):** the T5b controller-board rails (web inboard face, Y 38..81,
  Z 93..129.5) ran straight through the worm and the motor; the board had never been an
  envelope in the fit tool. It is now (`tilt controller board`), on the web's outboard
  face in the shoulder pocket. A grid search found no 2 mm-clear position forward of
  the worm (the wall curves in above Z 108 at Y < 12); aft of the worm's reach (Y ≥ 54.6)
  it clears at Z 83..119.5 with a 7.4 mm envelope, which pushed the aft nodes 8.5 mm aft.
* **T5d-3 (CLOSED by T5e):** the T5b web had no cut where the worm (6.5 mm past the web
  plane) and the brake collar (1.5 mm) reach; the T5b brake guide straddled the web
  plane and the solenoid overlapped it by 0.5 mm. The web now has a rounded slot for
  both, the guide's outboard face is the web face (2 × M2.5 through the web), and the
  solenoid axis is 1.5 mm inboard of the worm's.
* **The tilted-motor idea (rejected):** rotating the worm θ aft of vertical moves the
  worm's centre to Y 46.6 + 33 sin θ; at θ ≥ 5° its Ø28 body straddles the port hoist
  line (X −138.95, Y 55.5), and the line cannot move (it is 3 mm off the cradle wall on
  one side and would need 3 mm off the worm tip on the other). Motor-to-wheel gap is
  unchanged by θ anyway.
* The worm's thread profile in T5b (fixed ±0.79 mm tangential half-width) was wrong for
  any lead; T5e derives the transverse section from the axial tooth thickness.
* The encoder-line harness bore (Y 37.5, Z 68.7) exits the wall inside the wheel's
  disc: the harness must turn down within 9 mm of the wall — a clip on the bracket
  is an open item.

## 5. Ramp fairing

The void was real: a 52 × 36 mm rectangular opening in the 25°-canted forward
face (ray map, 2026-09-15). The fairing follows the flank profile sampled at
0.5 mm in Z on both sides of the opening (a single plane fit missed the flanks by
up to 5 mm), 2 mm skin + 6 mm × 2 mm inner frame lip, fused unclipped (the outer
envelope has a hole there, so envelope-clipping would delete it). Panel lines and
the hinge line are read from REF-CAD-003 Sheet One "Detail of Cargo Ramp" at
thumbnail fidelity — proportions and location, not line-art detail. Verified:
every ray from ahead now hits the face, even hit parity through the fairing,
grooves 0.8 mm deep and closed (off-grid ray map).

## 6. Foam zones and void formers

| Zone | Foamed? | Formers |
|---|---|---|
| Payload bay + roof band (Y −22..132) | never | — |
| Chin (Y −66..−22) | optional (≈ 20 g of 2 lb/ft³ PU, and mostly slivers now) | `void_former_cargo_collar_rim` (collar seat Y −66..−58), `_node_bay` (chin shelf + both pouched nodes, X −214..−126, Z 44..90 — T5e), `_batt_chimney` (Z 90..131, the cradle nose), `_harness_trunk_{port,stbd}` (flank conduit ways outboard of the node bay) — `tools/gen_cargo_void_formers.py`, cut from the published shell, PLA, waxed, removed after cure |

## 7. Verification (all PASS, 2026-09-16, post Rev T5e re-merge)

```text
/usr/bin/python3 tools/cargo_layout_fit.py --plot        # PASS, 0 hit / 0 pair overlap
/usr/bin/python3 tools/validate_stls.py                  # 79/79
/usr/bin/python3 tools/cargo_bay_envelope.py             # PASS
/usr/bin/python3 tools/landing_gear_wing_clearance.py --proud   # CLEAR
/usr/bin/python3 tools/wing_root_deconflict.py           # CLEAR
/usr/bin/python3 tools/wing_internal_clearance.py        # PASS
/usr/bin/python3 tools/wing_spar_carrythrough.py         # PASS
```

Shell: 287.2 cm³, 301.6 g as-printed (T5b 287.8 / 302; T4 338.5 / 355), watertight, one body.
Rev T5f (2026-09-21) re-merge: see §0a; gates re-run — all PASS; `gateway_door_tray.stl` 4.73 cm³ / 5.0 g, watertight, touches only its own board envelope and bosses.
Parts (exported STL × 1.05 g/cm³): bracket 16.3 g ×2, worm 6.0 ×2, wheel 6.9 ×2,
brake guide 2.1 ×2, chin shelf 9.4, battery cradle 39.2. The rendered bracket, worm,
wheel, guide and shelf were each booleaned against the shell and every layout
envelope (only the intended contacts remain: feet on bosses, rails around the board,
worm/wheel mesh zone 21 mm³, shelf lips in the cable channel).

## 8. Open items created

| ID | Item |
|---|---|
| D-T5-3 | **CLOSED (T5e):** all four nodes placed — FC2/FC3 aft strip, CN2/CN3 chin floor |
| WINCH-D | `CARGO_WINCH_SPECIFICATION.md` Rev D for the twin-drum bridle at Y 55.5 |
| HARN-CLIP | Encoder-harness turn-down clip on the tilt bracket |
| NODE-SADDLE | `node_saddle.scad` for N2/N4 at Y 99.5..121.5 — the cradle aft wall is now 13 mm ahead of them; a floor- or thwart-mounted saddle is the likelier answer |
| TC-BOARD | Open-Secure-ESC tilt controller (REF-ESC-001): the build carries the T5e rail envelope as a hard host constraint (≤ 42.9 × 36.5 mm, ≤ 4 mm parts on the web-facing side, bare back, connectors aft/inboard); layout not started — its buck inductors are the height risk |
| GPS-ANT | Ø36 patch antenna part vs the legacy ANN-MB reference (82 × 60 mm — does not fit the cup) |
| OBS-CARGO | Envelope PLACED (T5e, §1) and bosses merged; `cargo_vera_faraday.scad` (legacy frame) must be re-authored in hull frame to the 4 belly bosses, with the camera on the top edge looking forward-down through the aperture |
| A0 | Battery station fixed at Y −58..84 — feed the CG ledger |
| GW-DOOR-1..7, SERVO-PLACE, DOOR-LATCH | `docs/CARGO_DOOR_GATEWAY_SPEC.md` §8 (Rev T5f): build the `N_STACKS=1` instance; OpenServoCore physical layer; PWM-fallback bench items; two-actuator confirmation; hull-frame placement of the three SG90s (the pocket beside the tray, X ±(27..45) at Z ≤ 20, is the candidate); **the doors have no positive in-flight latch** (finding) |
