# CAN-PERIPH-GW-1 — TPM-Secured Dual-Isolated-Bus (CAN-FD + RS-485) Peripheral Gateway

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**Drafted by:** Claude Fable 5 (Anthropic), 2026-07-25/26
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**BOM designator:** `MAL-CAN-PERIPH-GW-PCB`
**Revision:** 1 (2026-07-26) — new board
**Status:** Schematic complete, `kicad-cli` ERC **0 errors** (74 warnings, identical
classes/counts-per-part to this project's own Jayne baseline — see "Verification"
below). PCB first-pass footprint population complete (32/32 footprints placed,
nets injected, GND pour filled), DRC **2 documented exceptions** + 86 unrouted
nets (signal routing is an open manual follow-on — see "Open items"). **Stackable**
(`N_STACKS` in the generator header) — verified ERC-0/documented-DRC-only at
both `N_STACKS=1` (shipped default) and `N_STACKS=3`.

---

## Purpose

`MAL-CAN-PERIPH-GW-PCB` is a standalone, TPM-secured gateway node that bridges a
sensor or actuator onto **both** of this project's onboard digital buses — CAN-FD
and RS-485, both galvanically isolated — signing every republished message with
its on-board TPM. It is a clean-room remix of the *concept* behind VimDrones'
"AP_Periph Pico" (a small dedicated MCU + CAN transceiver running ArduPilot
AP_Periph firmware to bridge serial/I²C/PWM sensors onto DroneCAN), extended with
the three components requested for this task:

| Addition | Part | Datasheet in repo |
| --- | --- | --- |
| Trusted platform module | Infineon OPTIGA™ TPM SLB 9670 TPM2.0 | `avionics/datasheets/SLB_9670VQ20_Infineon.pdf` |
| Isolated CAN-FD transceiver | TI ISOW1044BDFMR | `avionics/datasheets/isow1044.pdf` |
| Isolated RS-485 transceiver | ADI ADM2795E | `avionics/datasheets/adm2795e.pdf` |

**Not a PocketBeagle 2 Industrial cape** — standalone board, own 5 V power input,
connects to the airframe only via its CAN-FD and RS-485 daisy-chain connectors
plus a local power connector, matching Jayne's own "standalone board" pattern.

## Why VimDrones' concept, but not VimDrones' hardware

The VimDrones "AP_Periph Pico" (<https://dev.vimdrones.com/products/vimdrones_can_periph_pico/>,
spec table read 2026-07-25) is: STM32L431 MCU, single **non-isolated** CAN port,
5 V supply, 120 Ω switchable termination (default off), 15×11 mm, running AP_Periph
firmware to convert Serial/I²C sensors (GPS, compass, baro, airspeed, telemetry,
ELRS) to DroneCAN. VimDrones' own published KiCad source
(<https://github.com/VimDrones/AM32_esc_development_board>, and the same MCU
family confirmed again on the ESC S50 spec page) is **GPL-3.0-licensed** —
incompatible with this project's CC BY 4.0 terms per root `AGENTS.md` §3
("confirm license compatibility before integrating; only license-compatible
items are integrated"). **No VimDrones file, symbol, footprint, or schematic
geometry is reused anywhere in this board.** Only the public spec facts (MCU
family choice, CAN-bridge concept, 5 V supply, switchable termination) informed
the design below; every symbol here is either this project's own
already-verified clean-room part or newly authored directly from the OEM
datasheet.

The MCU is **TI MSPM0G3507** (this project's fleet-standard part, REF-SENSOR-004
— already used on Jayne; native CAN 2.0/CAN-FD peripheral, 4× UART, 2× SPI, up to
60 GPIO, QEI-capable timer), not VimDrones' STM32L431 — so this gateway shares its
brain with the rest of the fleet instead of introducing a one-off part, and no
GPL-licensed VimDrones schematic content needs to be touched at all.

## Architecture

```text
                    +5V in ──► TLV62569 buck ──► +3V3
                                                    │
        AK7455 tilt encoder ──SPI──┐               │
        (ENC-NACELLE-1 pigtail)    │        ┌───────┴────────┐
                                   ├──────► │  U1 MSPM0G3507  │
        UART/TTL/PWM/BSHOT ────────┘        │  (MCU, native   │
        (ESC S50 / AM32, or any             │   CAN-FD periph)│
         other UART/TTL/PWM/                └───┬────────┬────┘
         bidirectional-DShot device)             │        │
                                          SPI0    │        │  UART0 + GPIO
                                     ┌────────────┘        └────────────┐
                                     ▼                                  ▼
                          U2 SLB9670 TPM                    U3 ISOW1044 ── U4 ADM2795E
                          (signs every                      (isolated      (isolated
                           republished                       CAN-FD)       RS-485)
                           message)                             │              │
                                                          CAN-FD trunk    RS-485 trunk
                                                        (daisy-chain,   (daisy-chain,
                                                         120R term)      120R term)
```

U1 reads the local sensor/actuator (AK7455 SPI, or ESC UART/TTL/PWM/BSHOT), has
the TPM sign the outgoing telemetry/command frame, and republishes it on **both**
isolated buses so every other node on the airframe (River, Simon, Wash/Zoë at
every stack, etc.) can see it without trusting an unsigned local link.

## Deployment (2 use cases, same board type)

### 1. Nacelle tilt-encoder gateway (ENC-PORT / ENC-STBD, 2×)

Reads the local **AK7455** off-axis tilt encoder (`ENC-NACELLE-1.md`,
`MAL-TILT-ENC-PCB`) over its **existing, unmodified** 7-wire SPI+ERROR pigtail —
`J_ENC` on this board uses the identical `Serenity-Custom:Pigtail_7W_DirectSolder`
footprint with the same pad 1–7 assignment as ENC-NACELLE-1's own P1
(GND, CSN, SCLK, MOSI, MISO, +3V3, ERROR), so the existing pigtail plugs in
unchanged.

**This resolves the open cross-subsystem item recorded in `ENC-NACELLE-1.md`
"Host assignment" and `airframe/wings-nacelles/WBS.md`**: previously, River
(primary) / Simon (alternate) were expected to read the AK7455 SPI bus directly
over a long wire run through the airframe, and `Wash.md` §13 still listed a
legacy AS5600 I²C `J_ENC`. With this gateway in place, **River/Simon no longer
read the encoder directly at all** — they receive the TPM-signed tilt angle over
CAN-FD/RS-485 like every other piece of telemetry on the airframe. `Wash.md` §13
still needs a documentation pass to drop the stale `J_ENC` I²C line (flagged in
TODO.md; not edited here since it is Wash's own file, out of this board's scope).

### 2. Per-EDF ESC gateway (ESC-{PORT,STBD}-{FWD,AFT}, 4×)

Bridges a **VimDrones ESC S50** (<https://dev.vimdrones.com/products/vimdrones_esc_s50/>,
spec table read 2026-07-25: STM32L431KCU6, TOSHIBA TPHR8504PL FETs, 50 A
continuous, 2S–6S, 120 Ω switchable CAN term, 40×17 mm — informational reference
only, same GPL-3.0/no-source-copied caveat as above) — run in AM32's
**"Standard" firmware** mode (DSHOT/PWM command in, **BDSHOT**/EDSHOT telemetry
out: RPM, voltage, current, temperature) rather than its DroneCAN firmware
variant. `J_FLEX` on this board carries the DSHOT/PWM command line out and the
BDSHOT (bidirectional DShot) telemetry line back — this is exactly why
`FLEX_BSHOT_IO` and `FLEX_PWM_IO` exist on the flexible header (the "bshot"
requirement in the original task). One gateway per EDF (4× total: 2 nacelles ×
2 EDFs each, per the propulsion baseline in root `AGENTS.md`); each republishes
that EDF's TPM-signed `uavcan.equipment.esc.Status`-equivalent telemetry
(RPM/voltage/current/temperature) on both isolated buses, and relays incoming
signed setpoint commands back down to the ESC as DShot.

### 3. Servo actuator gateway (nacelle tilt / nozzle-drive servos, reuses the same header)

`FLEX_PWM_IO` and `FLEX_TTL_GPIO` are wired to plain MSPM0G3507 GPIOs, which
are bidirectional/timer-capable in both directions — the same physical pin
that captures BDSHOT telemetry (input) can instead **generate** a standard
50 Hz / 1000–2000 µs servo PWM command (output), and `FLEX_TTL_GPIO` covers a
TTL-level digital servo protocol (e.g. a serial-bus servo) on the same header.
No extra circuitry is needed for this beyond the MCU's own GPIO — this is a
firmware-mode choice, not a hardware change — so this board type also serves
as a signed CAN-FD/RS-485-to-servo command bridge (e.g. nacelle tilt or
nozzle-drive actuators) using the identical `J_FLEX` header already described
above. Net renamed `FLEX_PWM_IN` → `FLEX_PWM_IO` to reflect this (bidirectional,
not capture-only).

Using one reusable gateway board type for all three roles (rather than bespoke
designs) matches root `AGENTS.md`'s explicit goal: *"Avionics, comms, and
software are designed for reuse on other UAV/UGV/USV/robot platforms, not just
this airframe."*

## Stackable: N complete trust modules on one PCB

Set `N_STACKS` at the top of `scripts/gen_can_periph_gw_sch.py` (and the PCB
generator reads the same value automatically — see below) to place multiple
**complete** trust modules on one board to conserve area/connector count when
several sensors or actuators live at the same physical location — the
motivating case is a single nacelle's two EDFs sharing one gateway PCB
(`N_STACKS=2`) instead of two separate boards.

Each stack keeps its **own, independent** MCU, TPM, isolated CAN-FD
transceiver, isolated RS-485 transceiver, and encoder/flex headers — every
stack signs its own messages with its own TPM identity. Only the truly shared
physical infrastructure is generated once for the whole board:

| Shared once per board | Per-stack (own copy each) |
| --- | --- |
| +5V input connector + TLV62569 3V3 buck | U1 MSPM0G3507 MCU |
| CAN-FD bus connectors (IN/OUT) + 120 Ω term | U2 SLB9670 TPM |
| RS-485 bus connectors (IN/OUT) + 120 Ω term | U3 ISOW1044BDFMR (+ its own integrated isolated DC-DC) |
| Isolated RS-485 DC-DC (feeds every stack's ADM2795E VDD2) | U4 GW_ADM2795E |
| `CAN_H` / `CAN_L` / `ISO_GND_CAN` nets | `J_ENC`, `J_FLEX` |
| `RS485_A` / `RS485_B` / `ISO_GND_485` / `ISO_3V3_485` nets | `J_SWD` (independent programming/debug per MCU) |

This matches real CAN-FD/RS-485 electrical behavior, not just a schematic
convenience: both buses are genuine **multi-drop** topologies — every node's
transceiver taps the *same two physical wires* — so N stacks' transceivers on
one board are electrically in parallel on that shared pair regardless of
`N_STACKS`, exactly as N separate boards on the same bus segment would be.
Two exceptions, both deliberate:

- **`ISO_5V_CAN` stays per-stack** (`ISO_5V_CAN_1`, `ISO_5V_CAN_2`, …) because
  each ISOW1044 generates it from its own *integrated* isolated DC-DC —
  paralleling two independently regulated outputs together is bad practice
  (and would trip ERC's "two power outputs connected" check, since VISOOUT is
  a real `power_out` pin per the datasheet).
- **`ISO_3V3_485` is shared** because ADM2795E has *no* integrated isolated
  DC-DC (see the ADM2795E section below) — its VDD2 is a power **input**, so
  one real external supply legitimately feeding N input pins is fine.

Verified: `N_STACKS=1` (shipped default) and `N_STACKS=3` both regenerate to
`kicad-cli sch erc` **0 errors** and `kicad-cli pcb drc` **0 errors beyond the
2 (or 2×N) documented `starved_thermal` exceptions already tracked below** —
the PCB generator (`gen_can_periph_gw_pcb.py`) imports `N_STACKS` directly from
the schematic generator so the two can never drift out of sync.

## Section-by-section design (see `scripts/gen_can_periph_gw_sch.py`)

- **A — Power:** JST-GH 2P +5V/GND in → TI TLV62569 buck → +3V3 (identical
  topology to Jayne's own Section A, reused verbatim — already-verified
  regulator circuit).
- **B — MCU (U1, TI MSPM0G3507):** `Jayne_MSPM0G3507_RGZ` clean-room symbol
  reused verbatim (QFN-48-1EP 7×7 mm, ERC-0-proven on Jayne). NRST 10 kΩ
  pull-up, VCORE 1 µF decouple, SWD 4-pin program header.
- **C — TPM (U2, Infineon SLB9670):** `Jayne_SLB9670_TPM` clean-room symbol
  reused verbatim (QFN-32-1EP 5×5 mm). RST# gets an explicit 10 kΩ pull-up
  (datasheet notes only a *weak* internal pull-up); pin 1 and pin 14 tied to
  VDD and pin 16 to GND per the datasheet's own TCG-compliance notes (Table 5).
- **D — Isolated CAN-FD (U3, TI ISOW1044BDFMR):** `Jayne_ISOW1044BDFMR`
  clean-room symbol reused verbatim. STB tied to GND (normal mode); EN/FLT
  routed to a spare MCU GPIO (`CANFD_FLT_N`) for fault visibility rather than
  left floating — a real, datasheet-supported feature of the part, not
  scope creep. VISOOUT/VSIN/VISOIN shorted together (`ISO_5V_CAN`) and
  GND2/GISOIN×3 shorted together (`ISO_GND_CAN`) per the datasheet's own
  application-circuit note. Two `Conn_JST_GH_03P` bus connectors (daisy-chain
  in/out) + a 120 Ω termination resistor in series with an **open-by-default**
  solder jumper, replicating VimDrones' own "120 Ω switchable, default OFF"
  feature.
- **E — Isolated RS-485 (U4, ADI ADM2795E) — NEW clean-room symbol:** see
  "ADM2795E clean-room symbol" below. Same daisy-chain-connector +
  switchable-termination pattern as Section D.
- **F — `J_ENC`:** AK7455 pigtail-compatible 7-pad direct-solder header, wired
  to a **second, dedicated** MCU SPI bus (`ENC_SPI_*`) separate from the TPM's
  own SPI bus — SPI naturally supports multiple devices via separate chip
  selects, so this needed no bus-sharing logic.
- **G — `J_FLEX`:** 1×8 2.54 mm header — `FLEX_UART_TX/RX`, `FLEX_TTL_GPIO`,
  `FLEX_PWM_IO`, `FLEX_BSHOT_IO`, `+5V`, `+3V3`, `GND`. Each signal is its own
  labeled pin (not a multiplexed/analog-switched shared pin) — the simplest,
  most robust hardware choice for a field-configurable header; firmware
  decides which lines are active per deployment. `FLEX_PWM_IO` and
  `FLEX_TTL_GPIO` are plain bidirectional/timer-capable MCU GPIOs, so the same
  pins serve equally as **servo PWM/TTL command outputs** (see deployment
  mode 3 above) or as sensor/telemetry inputs — direction is a firmware
  choice, not a hardware one.

## ADM2795E clean-room symbol (`GW_ADM2795E`)

**The `ADM2795EBRWZ` symbol already embedded in `Wash.kicad_sch` and
`Zoë.kicad_sch` has incorrect pin numbers** — found while researching this
board. Its pin list assigns a pin **17** to a 16-pin part and a duplicate pin
number **20** to two different pin names (`VCC1` and `GND2`), inconsistent with
the real ADM2795E datasheet (Analog Devices Rev D, 16-lead SOIC_W / RW-16
package). It was evidently cloned from the ISOW1044 (20-pin) symbol template and
never corrected. **This board does not reuse that symbol.** `GW_ADM2795E` was
authored fresh from Table 10 ("Pin Function Descriptions") of
`avionics/datasheets/adm2795e.pdf`, read directly for this task:

| Pin | Name | Pin | Name |
| --- | --- | --- | --- |
| 1 | VDD1 | 9 | GND2 |
| 2 | GND1 | 10 | GND2 |
| 3 | TxD | 11 | A |
| 4 | DE | 12 | GND2 |
| 5 | RE̅ | 13 | VDD2 |
| 6 | RxD | 14 | B |
| 7 | NIC | 15 | GND2 |
| 8 | GND1 | 16 | VDD2 |

Footprint: `Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm` (real KiCad system
footprint, matches the datasheet's RW-16 package body). **The Wash/Zoë defect
is flagged in `REFERENCES.md` and `TODO.md` for correction there — not fixed in
this task, since Wash/Zoë were not part of this board's scope.**

## Open items

1. **Signal routing not done.** The user did the component packing/resizing
   pass by hand in the KiCad GUI (2026-07-26) — `scripts/route_can_periph_gw_pcb.py`
   re-syncs pad nets to the current schematic and cleans up silkscreen
   overlaps *without* touching that placement, but does not route copper.
   An earlier attempt at automatic straight-line routing was tried and
   **reverted**: with no real autorouter available in this environment (no
   `freerouting` binary; `kicad-cli pcb export` has no `dsn` target), a naive
   minimum-spanning-tree route made DRC measurably worse (114 unconnected →
   266 errors, including 48 actual shorts between different nets) — leaving
   nets unrouted is safer than a collision-blind auto-route. Current state:
   0 unrelated errors, 89 unrouted nets, 2 documented `starved_thermal`
   exceptions (below). Routing (~40 nets, including the CAN_H/CAN_L and
   RS485_A/B differential pairs) is a manual KiCad pass. Tracked in
   `avionics/WBS.md`.
2. **2 documented DRC exceptions** — `starved_thermal` on U2 (SLB9670) GND pads
   2 and 23 (zone wants 2 thermal-relief spokes, QFN pad pitch only permits 1).
   Same class of finding already accepted on `ENC-NACELLE-1` (its own DRC notes
   set `min_resolved_spokes = 1` for exactly this reason). Fix path: either
   accept (as ENC-NACELLE-1 did) or switch the GND zone to solid-fill
   (`connect_pads` mode) for this board — user's call at final layout.
3. **U_ISO_DCDC MPN not selected.** ADM2795E is a *signal-only* isolator (unlike
   ISOW1044, it has no integrated isolated DC-DC) — datasheet Table 1 requires
   an externally supplied, isolated VDD2 (3.0–5.5 V) on the bus side. Placed in
   the schematic as a labeled generic 4-pin block (`ISO_DCDC_1W_GENERIC`), not a
   claimed real part, and **not placed on the PCB** — no footprint chosen yet.
   Candidates to evaluate against an OEM datasheet before fab: a small 1 W SIP4
   isolated DC-DC module (e.g. MORNSUN B0505S-1WR3 5V→5V, or an equivalent
   5V→3.3V part) — add the chosen datasheet to `avionics/datasheets/` and a
   `REFERENCES.md` entry before this gate closes. Tracked TODO §0.x.
4. **MSPM0 GPIO → peripheral pinmux** (SPI0/SPI1/UART0/UART1/CAN/GPIO
   assignments) is a defensible datasheet-capable assignment, not yet
   cross-checked against the MSPM0G3507 pinmux tables — the same caveat
   Jayne's own carrier schematic already carries for this same MCU.
5. **Firmware** is out of scope for this hardware task. The gateway needs an
   AP_Periph-derived (not stock) firmware image: DroneCAN publish/subscribe on
   CAN-FD, a mirrored publish on RS-485, TPM-backed message signing, plus
   (encoder role) an AK7455 SPI driver or (ESC role) a DShot/BDShot master.
   Firmware in ArduPilot's AP_Periph is GPLv3 — a separate licensing domain
   from this CC-BY-4.0 hardware design (same relationship every ArduPilot-based
   board in this project already has).
6. **`Wash.md` §13** still lists a legacy AS5600 I²C `J_ENC` — needs a
   documentation-only edit to note the encoder is now read via this gateway,
   not directly. Flagged, not edited here (Wash's own file).

## Verification

- `kicad-cli sch erc CAN-PERIPH-GW-1.kicad_sch --severity-all`: **0 errors**,
  74 warnings — all `lib_symbol_issues` (no project sym-lib-table entry for the
  embedded lib_symbols) and `endpoint_off_grid` (auto-placed label coordinates
  off the 50 mil grid). Confirmed identical warning classes appear on this
  project's own `Jayne.kicad_sch` (0 errors / 141 warnings) — a pre-existing,
  accepted characteristic of this project's generator-script workflow, not a
  defect introduced here.
- `kicad-cli pcb drc CAN-PERIPH-GW-1.kicad_pcb --severity-all`: 2 errors
  (documented above), 5 warnings (silk/copper edge-clearance and one isolated-
  copper sliver — cosmetic, first-pass placement), 86 unrouted nets (documented
  above).

## Bill of Materials (new parts introduced by this board)

| Ref | Part | Package | Datasheet |
| --- | --- | --- | --- |
| U1 | TI MSPM0G3507 | QFN-48-1EP 7×7 mm | REF-SENSOR-004 |
| U2 | Infineon SLB9670VQ2.0 | PG-VQFN-32-13 | `SLB_9670VQ20_Infineon.pdf` |
| U3 | TI ISOW1044BDFMR | SOIC-20W 7.5×12.8 mm | `isow1044.pdf` |
| U4 | ADI ADM2795EBRWZ | SOIC-16W 7.5×10.3 mm | `adm2795e.pdf` |
| U_REG_3V3 | TI TLV62569DBVR | SOT-23-6 | ti.com/lit/ds/symlink/tlv62569.pdf |
| U_ISO_DCDC | TBD — isolated 1 W DC-DC | TBD | open item |

## Related Files

- `avionics/kicad/ENC-NACELLE-1.md` — the AK7455 tilt-encoder board this
  gateway's `J_ENC` mates with.
- `avionics/kicad/Jayne/Jayne.md` — source of the MSPM0G3507/SLB9670/ISOW1044
  clean-room symbols reused here.
- `docs/references/vimdrones_can_periph_pico_v1.0.stl`,
  `docs/references/vimdrones_esc_s50_v1.0.step` — mechanical reference models
  already in the repo for the two VimDrones products this board's concept
  draws on (informational/fit reference only, not electrically reused).
- `REFERENCES.md` — REF-SENSOR entries for ISOW1044/ADM2795E/SLB9670, and the
  Wash/Zoë ADM2795E pin-numbering defect note.
