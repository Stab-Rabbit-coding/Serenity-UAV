# Project sizing basis (coordinator notes, from the repository and the motor datasheet)

Written by the coordinator from the Serenity UAV repository, not web research. Every figure has
its source.

## Motor: QX-Motor QF2822-2300KV, 64 mm 12-blade EDF (REF-EDF-003)
Read directly from the manufacturer instruction-manual image
`docs/references/qx-motor 64mm edf/64_2822-2300KV_00.png`
(source: https://cdn.shopify.com/s/files/1/0713/6424/7837/files/64_2822-2300KV_00.png):
- 9N6P, shaft 3.0 mm, motor diameter 28 mm, weight 140 g, 3-6S LiPo.
- Max continuous power 1440 W / 10 s; **max continuous current 60 A / 10 s** (a 10-second rating).
- 24 V table: 50 % 10.0 A 240 W 750 g; 60 % 17.0 A 408 W 1050 g; 70 % 25.0 A 600 W 1380 g;
  80 % 35 A 840 W 1720 g; 90 % 47 A 1128 W 2080 g; **100 % 57.0 A 1368 W 2370 g**.
- **Recommended ESC: 80 A.**
- **Not published:** winding resistance, lead gauge, lead length, connector type (the wiring
  sketch shows three bullet connectors).

## Aircraft load case (repository AUW ledger, 2026-11-11)
- 4 fans (2 nacelles x 2 EDFs in series), one ESC per fan, each ESC fed by its own +/- pair.
- Hover AUW 6,500 g (14.33 lbm); heaviest configuration about 6,605 g.
- Per fan in hover: 1,625-1,651 gf. Interpolated in the 24 V table: **32.2-33.0 A at 24 V,
  about 77-78 % throttle, 773-791 W**. Same power on a sagged pack: about 35 A at 22.2 V and
  **37-38 A at 21.0 V (3.5 V/cell)**. VTOL hover is the sustained case for the whole mission.
- Full throttle: **57 A at 24 V**; the 60 A / 10 s datasheet rating is the peak case.
- The repository's older "28 A sustained hover" figure predates the weight growth and is superseded
  by the above.

## Conductor loss (copper at 68 F (20 C), resistivity 1.7241e-8 ohm m, standard AWG areas)
| AWG | mm2 | mohm/m | W/m at 37.9 A | W/m at 60 A |
|---|---|---|---|---|
| 8 | 8.37 | 2.061 | 3.0 | 7.4 |
| 10 | 5.26 | 3.277 | 4.7 | 11.8 |
| 12 | 3.31 | 5.211 | 7.5 | 18.8 |
| 14 | 2.08 | 8.285 | 11.9 | 29.8 |
| 16 | 1.31 | 13.17 | 18.9 | 47.4 |
Copper resistance rises about 31 % from 68 F (20 C) to 212 F (100 C).

## Phase-lead current (ESTIMATE, ideal six-step, continuous conduction)
I_phase_rms = sqrt(2/3) x I_dc / D (D = effective duty): hover about **35 A RMS**; full throttle
about **46.5 A RMS**. Phase-lead loss per lead at 35 A RMS: 16 AWG 16.5 W/m, 14 AWG 10.4 W/m,
12 AWG 6.5 W/m.

## Geometry and constraints from the repository
- Feed: four conductors run as a 2 x 2 group inside the Dia 0.787 in (20 mm) x 0.642 in (16.3 mm)
  ID roll-wrapped CF spar (about 6.8 in (173 mm) installed); the bundle takes 140 deg of twist per
  tilt cycle inside the spar bore; after the spar the wires fan out in individual channels of
  Dia 0.256 in (6.5 mm), bend radius 0.65 in (16.5 mm) and 0.87 in (22 mm), to M3 stud ring
  terminals in the nacelle disconnect bay. The 2 x 2 group of four wires of OD d circumscribes
  2.414 d; the bore needs 2.414 d + 2 x 0.059 in (1.5 mm) twist clearance <= 0.642 in (16.3 mm),
  so **d <= 0.217 in (5.5 mm)** for the current spar. Any wire with a larger OD does not fit.
- Feed one-way length from the Flight Engineer board to the bay: about 1.3-1.6 ft (0.4-0.5 m)
  (ESTIMATE; wing-side route not drawn).
- Branch protection today: Littelfuse 0297040.WXNV 40 A mini blade fuse per ESC (BOM
  FUSE-ESC-40A). **40 A is below the 57 A full-throttle draw and only just above the 37-38 A
  late-pack hover current.**
- Phase leads: motor stage-1 leads run back through a Dia 0.197 in (5.0 mm) conduit; stage-2 in a
  0.197 x 0.189 in (5.0 x 4.8 mm) slot (pod SCAD LEAD_CONDUIT_D, LEAD_SLOT_W2/D2). Thicker leads
  would need these enlarged.
- Bend rule cited in the repository: NASA-STD-8739.4A Table 7-1 (REF-NASA-001): minimum 3 x OD for
  an overall harness of AWG 10 or smaller.
- Sourcing rule (repository AGENTS.md): published, NDA-free manufacturer data required; the
  restricted-country rule applies to semiconductors, not to wire, but manufacturer domicile should
  still be recorded.
