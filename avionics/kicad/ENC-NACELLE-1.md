# ENC-NACELLE-1 — Nacelle Tilt-Angle Encoder Board (MT6701, off-axis)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**Rev R2e reconciliation drafted by:** Claude Opus 4.8 (2026-07-19)
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**BOM designator:** `MAL-TILT-ENC-PCB` (`current-specification/bom_revS.csv`)
**Revision:** R2e (2026-07-19) — reconciled to the rotating 8 mm tilt-spar mechanism
**Status:** Design intent frozen; **schematic held at the verification gate** — MT6701
pinout / I²C address / off-axis magnet geometry REQUIRE datasheet verification
(REFERENCES.md pending-verification table; root `TODO.md` §0.8). **Do not fabricate
the PCB or procure the sensor against the placeholder.**

---

## Supersession Notice — AS5600 → MT6701 (why this board was re-architected)

The Rev Q design of this board used an **AMS AS5600** on-axis, end-of-shaft magnetic
encoder mounted on the wing-spar end cap, reading a small diametric magnet press-fit
into the pivot-shaft end cap. That topology is **no longer valid** under the Rev R2
tilt-spar mechanism (commit #144, `feat: rotating 8mm tilt-spar mechanism`):

- The single wing spar is now the **rotating 8 mm tilt-spar** (AISI 4130, hollow
  5 mm ID — `SPAR-TILT-4130`). It is *both* the wing structural spar *and* the
  nacelle tilt axis, servo-driven from the cargo bay and **keyed to the nacelle**
  (`airframe/openscad/fuselage/cargo/cargo_spar_drive.scad`;
  `airframe/openscad/wings/wings_s1223_revo.scad`; `docs/TILT_SPAR_ANALYSIS.md`).
- Because the spar continues **through** the wing tip into the nacelle, there is
  **no free shaft end** at the joint. An on-axis end-of-shaft encoder (AS5600)
  cannot be used — it needs the magnet on a shaft *tip* facing the IC on-axis.
- The tilt loop must close on the **true nacelle angle** (output side) so the
  controller is immune to tilt-spar torsional wind-up between the cargo-bay servo
  and the nacelle (`docs/TILT_SPAR_ANALYSIS.md` §1, §3.5). That mandates a sensor
  at the wing/nacelle joint, not at the servo end.

**Resolution:** an **off-axis** magnetic angle IC on the *fixed* wing-tip pad reads
a diametric **ring** magnet carried on the *rotating* nacelle spar hub. Selected IC:
**Magntek MT6701** (I²C/SSI, off-axis capable). Fallback: **Magntek MA732** (SPI).

> The **AS5600 is retained elsewhere** — the Malcolm GCS antenna gimbal
> (`MAL-GIMBAL-ENC`) still uses AS5600 on-axis with a TCA9548A mux; that design is
> valid because the gimbal shafts have free ends. This board is the only place the
> AS5600 was invalid, and it is the only board changed.

---

## Purpose

`MAL-TILT-ENC-PCB` is a compact in-house magnetic rotary-encoder board that measures
the **true tilt angle of each nacelle** at the wing/nacelle joint. One board is
installed per nacelle (port and starboard) in the **fixed wing-tip pad pocket**
(`wing_tip_hall_sensor_pocket()` in `wings_s1223_revo.scad`).

The board reports absolute angle data over I²C to the **nacelle-control node —
River (primary nacelle control/sync), Simon (alternate)** — so the tilt-servo PID
closes on the measured nacelle output angle rather than on commanded servo PWM.
Because the sensor sits on the fixed wing (only the magnet rotates), its lead does
**not** twist with tilt — **no slip ring** is required.

---

## Design Rationale — Off-Axis Topology & Sensor Selection

Optical encoders remain rejected (carbon-fibre dust, moisture, and EDF-stream debris
at the joint). A magnetic angle IC is contactless and sealed. The change from Rev Q
is the **read geometry**, forced by the through-shaft spar:

| Aspect | Rev Q (AS5600) — retired | Rev R2e (MT6701) — current |
| --- | --- | --- |
| Read geometry | On-axis, end-of-shaft | **Off-axis**, IC beside the shaft |
| Magnet | Ø6 × 2.5 mm cylinder, on shaft tip | **Ø22 × Ø10 × 2.5 mm diametric ring** around the spar |
| Sensor IC | AMS AS5600, SOIC-8 | **Magntek MT6701**, 3×3 QFN (MA732/SPI fallback) |
| Board | 15 × 15 mm, JST-GH connector | **7 × 7 mm**, direct-solder 4-wire pigtail (no connector) |
| Mount | 4× M2 corner standoffs on spar end cap | **2× M2 brass** self-tap into the wing-tip pad |
| Host | Wash flight-control cape | **River / Simon** nacelle-control nodes |

MT6701 selection drivers: off-axis (side-shaft) reading capability; I²C interface
(SSI alternate); 3×3 QFN fits the congested wing-tip; single fixed I²C address
(drives the two-bus / mux requirement below).

---

## Bill of Materials (cross-referenced to `bom_revS.csv`)

| Ref | BOM ID | Value / MPN | Description | Package |
| --- | --- | --- | --- | --- |
| U1 | `MAL-TILT-ENC-PCB` | Magntek **MT6701QT-STD** | Off-axis magnetic rotary encoder IC (I²C/SSI) | 3×3 QFN |
| C1, C2 | (on-board) | 2× decoupling (values per MT6701 datasheet — **verify**) | VDD decoupling | 0402 |
| P1 | (on-board) | 4-wire direct-solder pigtail | GND / +3V3 / SDA / SCL — **no connector** | wire pads |
| — | `HALL-RING-MAG` | Ø22 OD × Ø10 ID × 2.5 mm NdFeB, **diametric** | Rotating rotor ring (nacelle side) | ring magnet |
| — | `PRINT-HALL-HUB` | `nacelle_hall_ring_hub.stl`, CF-PETG, OD 24 mm | Non-ferrous ring carrier keyed to spar | printed |
| — | `HALL-SCR-M2-BRASS` | M2 × 6 mm **brass** pan-head (×2/board) | Non-ferrous PCB fasteners | hardware |

**Board:** 7 × 7 mm, 2-layer FR4. Contents per `bom_revS.csv` `MAL-TILT-ENC-PCB`:
MT6701 (3×3 QFN) + 2 decoupling caps + direct-solder 4-wire pigtail. No connector
and no separate ESD array — the 7 × 7 mm outline threads the ~8.4 mm chordwise gap
between the Ø13.5 bearing flange and the forward EDF double-D bore at the wing tip
(`wings_s1223_revo.scad` `HALL_*` block). The shielded pigtail + firmware zero-cal
carry the EMI budget in place of the retired connector-mounted ESD diode array.

---

## Magnet & Rotating Hub (nacelle side)

The rotor is a **diametrically magnetised NdFeB ring** (`HALL-RING-MAG`,
Ø22 OD × Ø10 ID × 2.5 mm) carried on a **non-ferrous CF-PETG hub**
(`PRINT-HALL-HUB` = `nacelle_hall_ring_hub()` in
`airframe/openscad/nacelles/_export_pivot_slab.scad`, OD 24 mm) keyed/bonded to the
rotating 8 mm spar at the nacelle inboard face. The ring face points at the wing-tip
sensor pocket across an axial air gap of **`HALL_AIR_GAP` = 1.5 mm**; the MT6701 sits
off-axis at **R = 11 mm** and reads mid-annulus (ring mean radius ≈ 11 mm).

- Magnetisation **must be diametric** (across the diameter), **not axial** — an axial
  ring gives no in-plane angle signal to the off-axis IC.
- Ring **ID 10 mm** over the **8 mm** spar keeps a ≥ 1 mm non-ferrous wall between the
  magnet and the ferromagnetic steel (see mitigation below).

---

## Ferromagnetic-Spar Mitigation (mandatory)

Unlike Rev Q (which *required* a non-magnetic pivot shaft), the current spar **is**
ferromagnetic — AISI 4130 (or the 17-4 PH H1075 alternate), running through the ring
centre and distorting the bias field. This is a supported commercial arrangement
**only with mitigation and in-situ calibration** (`docs/TILT_SPAR_ANALYSIS.md` §1,
§3.5; `avionics/emi-hardening/WBS.md` §1.4.6):

1. **Non-ferrous stand-off** — the CF-PETG hub holds the ring ID off the steel spar
   (≥ 1 mm wall) and stands the ring proud of the steel F688ZZ root bearing.
2. **Non-ferrous fasteners in the keep-out** — every fastener within
   `HALL_KEEPOUT_R` = 10 mm of the IC must be brass / 316 / aluminium / nylon
   (`HALL-SCR-M2-BRASS`), **never** the steel bearing screws.
3. **Firmware zero-calibration** over the full **−5°…+90°** tilt sweep absorbs
   residual distortion; range-check for a **monotonic** angle after cal.

---

## Mounting (fixed wing-tip pad)

The board seats in `wing_tip_hall_sensor_pocket()` on the wing-tip mount pad
(`wings_s1223_revo.scad`):

- **PCB recess** `HALL_PCB_SEAT_T` = 2.0 mm into the pad face; the IC face sits flush
  with / just below the pad face so the axial gap to the ring is `HALL_AIR_GAP` once
  the nacelle butts up.
- **2× M2 self-tap pilots** (`HALL_PCB_SCR_D` = 1.7 mm), chordwise ±2.5 mm either side
  of the IC — **brass screws only** (keep-out rule above).
- IC offset **chordwise-aft** of the spar at R = 11 mm, clear of the Ø13.5 wing-tip
  bearing-flange keep-out (the wing-tip bearing is **MF128ZZ** 8×12×3.5, Rev R2d
  downsize from F688ZZ; the root bearing stays **F688ZZ** in the cargo bay).

Wing-tip radial reaction at the joint ≈ **19 N (4.3 lbf)** dynamic — trivial for both
the bearing and the pad; the pocket is geometry-/clearance-limited, not load-limited.

---

## Interface & Host Assignment

| Pin (pigtail P1) | Signal | Description |
| --- | --- | --- |
| 1 | GND | Power / signal return |
| 2 | +3V3 | 3.3 V supply from the nacelle-control node |
| 3 | ENC_SDA | I²C SDA (to/from node) |
| 4 | ENC_SCL | I²C SCL (from node) |

- **Nodes:** port + stbd read by **River** (primary nacelle control/sync), with
  **Simon** (alternate nacelle control) as failover (`avionics/WBS.md` §1.9.1).
- **Fixed I²C address → two-bus rule:** MT6701 has a **fixed** I²C address, so the two
  nacelle encoders collide on one bus. Put port and stbd on **separate I²C buses**, or
  behind a **TCA9548A** mux (the antenna-gimbal AS5600 pattern). Confirm the actual
  address on datasheet verification.
- **No slip ring:** the sensor is on the fixed wing; only the magnet rotates.

> **Cross-subsystem reconciliation (avionics, out of scope here):**
> `avionics/kicad/Wash/Wash.md` §13 still lists `J_ENC` as *"AS5600 nacelle tilt angle
> encoder (I2C)"* on the **Wash** cape. The host moved to **River/Simon** and the
> sensor to **MT6701**; Wash's `J_ENC` row needs the same reconciliation on the
> avionics side (tracked in `avionics/WBS.md` §1.9.1). Not edited by this pass.

---

## EMI / Wiring

- **Shielded 4-wire** sensor lead (VCC/GND/SDA/SCL) routed through the dedicated
  fixed-wing conduit `hall_sensor_cableway()` (chord fraction ≈ 0.30–0.33c),
  **forward of** the 0.48c EDF double-D so the low-level I²C lines stay clear of the
  40 A EDF feeds (`avionics/emi-hardening/WBS.md` §1.4.4 (I²C) / §1.4.6 (ferromagnetic
  spar / magnetic-sensor siting)).
- On-board 2× VDD decoupling close to the MT6701 (values per datasheet — verify).
- The board is a clean signal ground; the shield drain is single-point-grounded at the
  node end only (no ground loop).

---

## ⚠ REQUIRES VERIFICATION — do not fabricate / do not procure

Per `REFERENCES.md` (pending-verification table, entry *"Wing/nacelle Hall tilt
encoder — MT6701 off-axis spec"*) and root `TODO.md` §0.8, the following are
**placeholders** and must be confirmed against the MT6701 datasheet before the
schematic pinout is finalised, a `REF-SENSOR-*` catalog entry (with validated URL) is
added, and any PCB/harness sign-off occurs:

- **MT6701 QFN pinout and I²C address** (the schematic IC placement is held at the
  gate for exactly this reason — see `ENC-NACELLE-1.kicad_sch`).
- **Off-axis air-gap** (assumed 1.5 mm), **ring OD/ID** (Ø22/Ø10), **IC radial offset**
  (R = 11 mm) vs the datasheet's off-axis operating window.
- **Ferrous-through-shaft behaviour** — bench-cal with the steel spar + F688ZZ bearing
  installed; confirm monotonic angle over −5…90° after zero-cal, or switch to **MA732**.

Decoupling-cap values are likewise datasheet-dependent (shown provisional).

---

## Related Files

- `airframe/openscad/wings/wings_s1223_revo.scad` — fixed sensor half:
  `wing_tip_hall_sensor_pocket()`, `hall_sensor_cableway()`, `HALL_*` parameters.
- `airframe/openscad/nacelles/_export_pivot_slab.scad` — rotating half:
  `nacelle_hall_ring_hub()` (ring + non-ferrous hub). `INBOARD_FACE_X` sign VERIFY.
- `airframe/openscad/fuselage/cargo/cargo_spar_drive.scad` — cargo-bay spar drive
  (DS3218MG servo + F688ZZ root bearing): the actuator whose wind-up this board's
  true-tilt feedback rejects.
- `docs/TILT_SPAR_ANALYSIS.md` §1 / §3.5 / §8 — tilt-feedback rationale, ferrous-spar
  mitigation, wingtip-bearing downsize.
- `avionics/WBS.md` §1.9.1 — node assignment, part selection, calibration, wiring.
- `avionics/emi-hardening/WBS.md` §1.4.4 / §1.4.6 — I²C EMI and ferromagnetic-spar
  siting.
- `airframe/wings-nacelles/WBS.md` §1.1.3.6 — airframe-side task detail.

---

## References

1. Magntek **MT6701** magnetic angle-sensor IC — datasheet **URL PENDING** (add as
   `REF-SENSOR-*` with a validated URL on verification; `REFERENCES.md` / `TODO.md`
   §0.8). Selected part; off-axis I²C/SSI.
2. Magntek **MA732** magnetic angle-sensor IC (SPI) — **fallback**; datasheet URL to
   be cataloged if adopted.
3. AISI 4130 / 17-4 PH tilt-spar material — `current-specification/bom_revS.csv`
   `SPAR-TILT-4130`; allowables require MMPDS/AMS verification (`TODO.md` §0.8).
4. IEC 61000-4-2:2008 — ESD immunity (retained EMI context).
5. MIL-STD-461G:2015 — EM emissions/susceptibility (retained EMI context).

> The AS5600, PRTR5V0U2X, JST GH, and Belden 9367 citations from the Rev Q design have
> been removed here — none of those parts appear on the Rev R2e MT6701 board. They
> remain valid for the boards that still use them (AS5600 on `MAL-GIMBAL-ENC`).
