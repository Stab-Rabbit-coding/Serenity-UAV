#!/usr/bin/env python3
"""swap_lora_for_sik.py — One-off transform: remove Commo's LoRa (RFM95W),
add RFD900ux-SMT SiK, per the 2026-09-21 owner-approved radio relocation
(avionics/WBS.md "APPROVED DIRECTION" entry).

Commo.kicad_sch has no reliable schematic-first generator (gen_commo_sch.py
runs PCB-first, and is itself confirmed drifted — see this session's own
history) so this is a direct, precise text-level transform of the existing
file, following the exact "prefix both the instance AND the embedded
lib_symbols cache key" discipline already proven this session on Commo's
lib_id-corruption fix, and the same wire+global_label connectivity
convention gen_commo_sch.py's own docstring documents ("every symbol pin
gets a short wire stub terminated in a ... label carrying the ... net
name").

Verified pre-conditions (checked against the live file before writing this):
  * Commo's own PB2 header ALREADY exposes UART_SIK_RX/UART_SIK_TX as real,
    wired net labels (fleet-wide PocketBeagle2 UART convention) — SiK's host
    UART needs no new PB2 wiring, just connecting the module to these
    existing nets.
  * LORA_RESETN/LORA_DIO0 (PB2-side) become orphaned once LoRa is removed —
    repurposed here as SIK_RTS/SIK_CTS (same physical PB2 pins, renamed net,
    matching XO's own RFD900ux-SMT RTS/CTS convention).
  * SPI1_CS_LORA (PB2-side) becomes orphaned (SPI1_MISO/MOSI/CLK stay — they
    are shared with TPM) — converted to an explicit no_connect rather than
    left as a dangling label.

Author: Claude Sonnet 5, 2026-09-21. Owner: sgriffing. License: CC BY 4.0.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCH = HERE.parent / "kicads" / "Commo.kicad_sch"
SYM = HERE.parent / "kicads" / "Commo.kicad_sym"

OLD_LORA_LIBSYM_SCH = '''    (symbol "Commo:S_LoRa" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)
      (property "Reference" "U" (at 0 13.97 0) (effects (font (size 1.27 1.27))))
      (property "Value" "LoRa" (at 0 -13.97 0) (effects (font (size 1.27 1.27))))
      (symbol "S_LoRa_0_1"
        (rectangle (start -12.70 12.70) (end 12.70 -12.70) (stroke (width 0.2540) (type default)) (fill (type background)))
      )
      (symbol "S_LoRa_1_1"
        (pin passive line (at -15.24 10.16 0) (length 2.54) (name "GND" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at -15.24 7.62 0) (length 2.54) (name "SPI1_MISO" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
        (pin passive line (at -15.24 5.08 0) (length 2.54) (name "SPI1_MOSI" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))
        (pin passive line (at -15.24 2.54 0) (length 2.54) (name "SPI1_CLK" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))
        (pin passive line (at -15.24 0.00 0) (length 2.54) (name "SPI1_CS_LORA" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))
        (pin passive line (at -15.24 -2.54 0) (length 2.54) (name "LORA_RESETN" (effects (font (size 1.27 1.27)))) (number "6" (effects (font (size 1.27 1.27)))))
        (pin passive line (at -15.24 -5.08 0) (length 2.54) (name "" (effects (font (size 1.27 1.27)))) (number "7" (effects (font (size 1.27 1.27)))))
        (pin passive line (at -15.24 -7.62 0) (length 2.54) (name "GND" (effects (font (size 1.27 1.27)))) (number "8" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 15.24 10.16 180) (length 2.54) (name "" (effects (font (size 1.27 1.27)))) (number "9" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 15.24 7.62 180) (length 2.54) (name "GND" (effects (font (size 1.27 1.27)))) (number "10" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 15.24 5.08 180) (length 2.54) (name "" (effects (font (size 1.27 1.27)))) (number "11" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 15.24 2.54 180) (length 2.54) (name "" (effects (font (size 1.27 1.27)))) (number "12" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 15.24 0.00 180) (length 2.54) (name "" (effects (font (size 1.27 1.27)))) (number "13" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 15.24 -2.54 180) (length 2.54) (name "" (effects (font (size 1.27 1.27)))) (number "14" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 15.24 -5.08 180) (length 2.54) (name "" (effects (font (size 1.27 1.27)))) (number "15" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 15.24 -7.62 180) (length 2.54) (name "" (effects (font (size 1.27 1.27)))) (number "16" (effects (font (size 1.27 1.27)))))
      )
    )'''

OLD_LORA_LIBSYM_SYM = OLD_LORA_LIBSYM_SCH.replace('"Commo:S_LoRa"', '"S_LoRa"')

# New SIK (RFD900ux-SMT) lib_symbol — 30 pins, matching XO's own SIK pin
# table EXACTLY (real datasheet part, identical module to XO's original —
# "RFD900ux DataSheet v1.2.pdf" S5.2 Fig 5-2, 28-pad RF pinout + 2 thermal
# pads = 30 numbered terminals). Net names transcribed verbatim from
# gen_xo_sch.py's own SIK ICS entry (before this session's XO swap removed
# it), only renaming the "_F" ferrite-filtered net suffixes to their
# unfiltered form (Commo's own house convention has no equivalent EMI
# ferrite stage on this class of signal — see gen_commo_sch.py's existing
# UART_49MHZ_XCVR_RX/TX for comparison, which are also unfiltered).
SIK_PINS_L = [  # (num, name) left side, top-to-bottom — pins 1-14
    ("1", ""), ("2", ""), ("3", ""), ("4", ""), ("5", ""), ("6", ""), ("7", ""),
    ("8", "GND"), ("9", "GND"), ("10", ""), ("11", "GND"), ("12", "GND"),
    ("13", "SIK_ANT_RF"), ("14", "GND"),
]
SIK_PINS_R = [  # (num, name) right side, top-to-bottom — pins 15-30
    ("15", "GND"), ("16", ""), ("17", "GND"), ("18", "GND"), ("19", "SIK_VCC"),
    ("20", "GND"), ("21", ""), ("22", ""), ("23", ""), ("24", ""),
    ("25", "UART_SIK_RX"), ("26", "UART_SIK_TX"), ("27", "SIK_RTS"), ("28", "SIK_CTS"),
    ("29", "GND"), ("30", "GND"),
]


PIN_PITCH = 2.54


def build_libsym(prefix: str) -> str:
    rows = max(len(SIK_PINS_L), len(SIK_PINS_R))
    half_h = (rows * PIN_PITCH) / 2 + PIN_PITCH
    lines = [
        f'    (symbol "{prefix}S_SIK" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)',
        f'      (property "Reference" "U" (at 0 {half_h + 1.27:.2f} 0) (effects (font (size 1.27 1.27))))',
        f'      (property "Value" "SIK" (at 0 {-half_h - 1.27:.2f} 0) (effects (font (size 1.27 1.27))))',
        '      (symbol "S_SIK_0_1"',
        f'        (rectangle (start -12.70 {half_h:.2f}) (end 12.70 {-half_h:.2f}) (stroke (width 0.2540) (type default)) (fill (type background)))',
        "      )",
        '      (symbol "S_SIK_1_1"',
    ]
    for i, (num, name) in enumerate(SIK_PINS_L):
        y = half_h - PIN_PITCH * (i + 1)
        lines.append(f'        (pin passive line (at -15.24 {y:.2f} 0) (length 2.54) (name "{name}" (effects (font (size 1.27 1.27)))) (number "{num}" (effects (font (size 1.27 1.27)))))')
    for i, (num, name) in enumerate(SIK_PINS_R):
        y = half_h - PIN_PITCH * (i + 1)
        lines.append(f'        (pin passive line (at 15.24 {y:.2f} 180) (length 2.54) (name "{name}" (effects (font (size 1.27 1.27)))) (number "{num}" (effects (font (size 1.27 1.27)))))')
    lines += ["      )", "    )"]
    return "\n".join(lines)


_ucount = [0x2000]


def uid() -> str:
    _ucount[0] += 1
    return f"49030000-0000-0000-0000-{_ucount[0]:012x}"


def wire(x1, y1, x2, y2) -> str:
    return f'  (wire (pts (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y2:.2f})) (stroke (width 0) (type default)) (uuid "{uid()}"))'


def glabel(net, x, y, ang) -> str:
    just = "left" if ang == 0 else "right"
    return f'  (global_label "{net}" (shape passive) (at {x:.2f} {y:.2f} {ang}) (effects (font (size 1.27 1.27)) (justify {just})) (uuid "{uid()}"))'


def no_connect(x, y) -> str:
    return f'  (no_connect (at {x:.2f} {y:.2f}) (uuid "{uid()}"))'


STUB = 3.81
X, Y = 63.50, 929.64  # grid-aligned (multiple of 1.27 and 2.54); same general area LoRa occupied; schematic canvas is
                       # not area-constrained the way the PCB is, so a modest
                       # visual overlap with the ETH-PHY block below is a
                       # cosmetic concern only, not an ERC one.


def build_instance() -> str:
    rows = max(len(SIK_PINS_L), len(SIK_PINS_R))
    half_h = (rows * PIN_PITCH) / 2 + PIN_PITCH
    out = [
        '  (text "SiK RFD900ux-SMT (915 MHz UHF telemetry -- relocated from XO 2026-09-21, '
        'see avionics/WBS.md)" (at 50.80 882.46 0) (effects (font (size 2.0 2.0) (bold yes)) '
        f'(justify left)) (uuid "{uid()}"))',
        f'  (symbol (lib_id "Commo:S_SIK") (at {X:.2f} {Y:.2f} 0) (unit 1)',
        f'    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid()}")',
        f'    (property "Reference" "SIK" (at {X:.2f} {Y - half_h - 1.27:.2f} 0) (effects (font (size 1.27 1.27))))',
        f'    (property "Value" "RFD900ux-SMT" (at {X:.2f} {Y + half_h + 1.27:.2f} 0) (effects (font (size 1.27 1.27))))',
    ]
    for num, _ in SIK_PINS_L + SIK_PINS_R:
        out.append(f'    (pin "{num}" (uuid "{uid()}"))')
    out.append(f'    (instances (project "Commo" (path "/49030000-0000-0000-0000-000000000001" (reference "SIK") (unit 1))))')
    out.append("  )")
    wl = []
    for i, (num, net) in enumerate(SIK_PINS_L):
        cx, cy = X - 15.24, Y - (half_h - PIN_PITCH * (i + 1))
        if not net:
            wl.append(no_connect(cx, cy))
            continue
        wl.append(wire(cx, cy, cx - STUB, cy))
        wl.append(glabel(net, cx - STUB, cy, 180))
    for i, (num, net) in enumerate(SIK_PINS_R):
        cx, cy = X + 15.24, Y - (half_h - PIN_PITCH * (i + 1))
        if not net:
            wl.append(no_connect(cx, cy))
            continue
        wl.append(wire(cx, cy, cx + STUB, cy))
        wl.append(glabel(net, cx + STUB, cy, 0))
    return "\n".join(out + wl)


# --- Supporting passives: power bypass + antenna matching/ESD/jack --------
# (SIK's own datasheet-verified pins feed these: pin19 SIK_VCC needs bulk/HF
# bypass same as every other regulator/module on this project's boards;
# pin13 SIK_ANT_RF needs a matching network + ESD + jack chain, same
# disclosed "DNP until bench VSWR tuning" pattern already used for
# WIFI-BT-ZB's and Wio-E5's antenna chains on XO this session.)
PASSIVES = [
    # (ref, value, pin1_name, pin1_net, pin2_name, pin2_net)
    ("C-SIK1", "10uF 10V X5R", "P", "SIK_VCC", "N", "GND"),
    ("C-SIK2", "100nF", "P", "SIK_VCC", "N", "GND"),
    ("C-SIK-SH1", "DNP", "A", "SIK_ANT_RF", "B", "GND"),
    ("L-SIK-SER", "0R link", "A", "SIK_ANT_RF", "B", "SIK_ANT_F"),
    ("C-SIK-SH2", "DNP", "A", "SIK_ANT_F", "B", "GND"),
    ("D-ANT-SIK", "RCLAMP0502B", "A", "SIK_ANT_F", "K", "GND"),
]


def build_passive_libsym(prefix: str, ref: str, p1n: str, p2n: str) -> str:
    safe = ref.replace("-", "_")
    return "\n".join([
        f'    (symbol "{prefix}S_{safe}" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)',
        '      (property "Reference" "U" (at 0 5.08 0) (effects (font (size 1.27 1.27))))',
        f'      (property "Value" "{safe}" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))',
        f'      (symbol "S_{safe}_0_1"',
        '        (rectangle (start -12.70 3.81) (end 12.70 -3.81) (stroke (width 0.2540) (type default)) (fill (type background)))',
        "      )",
        f'      (symbol "S_{safe}_1_1"',
        f'        (pin passive line (at -15.24 1.27 0) (length 2.54) (name "{p1n}" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))',
        f'        (pin passive line (at 15.24 1.27 180) (length 2.54) (name "{p2n}" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))',
        "      )",
        "    )",
    ])


def build_passive_instance(ref: str, value: str, x: float, y: float, net1: str, net2: str) -> str:
    safe = ref.replace("-", "_")
    out = [
        f'  (symbol (lib_id "Commo:S_{safe}") (at {x:.2f} {y:.2f} 0) (unit 1)',
        f'    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid()}")',
        f'    (property "Reference" "{ref}" (at {x:.2f} {y - 6.35:.2f} 0) (effects (font (size 1.27 1.27))))',
        f'    (property "Value" "{value}" (at {x:.2f} {y + 6.35:.2f} 0) (effects (font (size 1.27 1.27))))',
        f'    (pin "1" (uuid "{uid()}"))',
        f'    (pin "2" (uuid "{uid()}"))',
        f'    (instances (project "Commo" (path "/49030000-0000-0000-0000-000000000001" (reference "{ref}") (unit 1))))',
        "  )",
        # NOTE: schematic pin transform negates the local Y even at angle 0
        # (project convention: instance + (x, -y) — see feedback_kicad_hand_
        # authoring memory). Pin-local y=+1.27 in the lib_symbol -> absolute
        # y = y_instance - 1.27, not + 1.27.
        wire(x - 15.24, y - 1.27, x - 15.24 - STUB, y - 1.27),
        glabel(net1, x - 15.24 - STUB, y - 1.27, 180),
        wire(x + 15.24, y - 1.27, x + 15.24 + STUB, y - 1.27),
        glabel(net2, x + 15.24 + STUB, y - 1.27, 0),
    ]
    return "\n".join(out)


# J-ANT-SIK: MMCX antenna jack (2-pin), same board-area rationale as XO's
# other antenna jacks this session.
JACK_LIBSYM_TEMPLATE = '''    (symbol "{prefix}S_J_ANT_SIK" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)
      (property "Reference" "J" (at 0 5.08 0) (effects (font (size 1.27 1.27))))
      (property "Value" "MMCX vertical" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
      (symbol "S_J_ANT_SIK_0_1"
        (rectangle (start -12.70 3.81) (end 12.70 -3.81) (stroke (width 0.2540) (type default)) (fill (type background)))
      )
      (symbol "S_J_ANT_SIK_1_1"
        (pin passive line (at -15.24 1.27 0) (length 2.54) (name "RF" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
        (pin passive line (at 15.24 1.27 180) (length 2.54) (name "SHIELD" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))
      )
    )'''


def main() -> None:
    sch = SCH.read_text()
    sym = SYM.read_text()

    assert OLD_LORA_LIBSYM_SCH in sch, "S_LoRa lib_symbol (Commo: prefix) not found verbatim in Commo.kicad_sch"
    assert OLD_LORA_LIBSYM_SYM in sym, "S_LoRa lib_symbol (bare) not found verbatim in Commo.kicad_sym"

    sch = sch.replace(OLD_LORA_LIBSYM_SCH, build_libsym("Commo:"))
    sym = sym.replace(OLD_LORA_LIBSYM_SYM, build_libsym(""))

    # --- Append new lib_symbols (passives + jack) right after S_SIK -------
    new_libsyms_sch = [build_passive_libsym("Commo:", ref, p1n, p2n) for ref, _, p1n, _, p2n, _ in PASSIVES]
    new_libsyms_sch.append(JACK_LIBSYM_TEMPLATE.format(prefix="Commo:"))
    new_libsyms_sym = [build_passive_libsym("", ref, p1n, p2n) for ref, _, p1n, _, p2n, _ in PASSIVES]
    new_libsyms_sym.append(JACK_LIBSYM_TEMPLATE.format(prefix=""))

    anchor_sch = '    (symbol "Commo:S_ETH-PHY"'
    assert anchor_sch in sch
    sch = sch.replace(anchor_sch, "\n".join(new_libsyms_sch) + "\n" + anchor_sch, 1)

    anchor_sym = '    (symbol "S_ETH-PHY"'
    assert anchor_sym in sym
    sym = sym.replace(anchor_sym, "\n".join(new_libsyms_sym) + "\n" + anchor_sym, 1)

    # --- Replace the LoRa instance block (heading text + instance + all its
    # wires/labels/no_connects) with the new SIK instance block. Anchored by
    # the exact known heading text through the last no_connect before the
    # ETHERNET-2nd-PORT heading (verified against the live file beforehand).
    start_marker = '  (text "LoRa 915 MHz (RFM95W, SPI via PB2-P1)"'
    end_marker = '  (text "ETHERNET 2nd PORT'
    start = sch.index(start_marker)
    end = sch.index(end_marker)
    assert start < end
    passive_instances = []
    # Placed well clear of ALL existing sheet content (max Y used elsewhere
    # in the file is 1107.0) to avoid the coordinate-collision "multiple
    # net names" warning a closer placement produced during testing.
    px, py = X, 1149.35  # grid-aligned (905 * 1.27)
    for i, (ref, value, _, net1, _, net2) in enumerate(PASSIVES):
        passive_instances.append(build_passive_instance(ref, value, px, py + i * 12.70, net1, net2))
    jx, jy = X + 38.10, py + len(PASSIVES) * 12.70
    passive_instances.append(
        f'  (symbol (lib_id "Commo:S_J_ANT_SIK") (at {jx:.2f} {jy:.2f} 0) (unit 1)\n'
        f'    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid()}")\n'
        f'    (property "Reference" "J-ANT-SIK" (at {jx:.2f} {jy - 6.35:.2f} 0) (effects (font (size 1.27 1.27))))\n'
        f'    (property "Value" "MMCX vertical" (at {jx:.2f} {jy + 6.35:.2f} 0) (effects (font (size 1.27 1.27))))\n'
        f'    (pin "1" (uuid "{uid()}"))\n'
        f'    (pin "2" (uuid "{uid()}"))\n'
        f'    (instances (project "Commo" (path "/49030000-0000-0000-0000-000000000001" (reference "J-ANT-SIK") (unit 1))))\n'
        "  )\n"
        + wire(jx - 15.24, jy - 1.27, jx - 15.24 - STUB, jy - 1.27) + "\n"
        + glabel("SIK_ANT_F", jx - 15.24 - STUB, jy - 1.27, 180) + "\n"
        + wire(jx + 15.24, jy - 1.27, jx + 15.24 + STUB, jy - 1.27) + "\n"
        + glabel("GND", jx + 15.24 + STUB, jy - 1.27, 0)
    )

    sch = sch[:start] + build_instance() + "\n" + "\n".join(passive_instances) + "\n" + sch[end:]

    # --- Repurpose the two now-orphaned PB2-side control nets -----------
    # LORA_RESETN -> SIK_RTS, LORA_DIO0 -> SIK_CTS (same physical PB2 pins).
    sch = sch.replace('(global_label "LORA_RESETN"', '(global_label "SIK_RTS"')
    sch = sch.replace('(global_label "LORA_DIO0"', '(global_label "SIK_CTS"')

    # --- SPI1_CS_LORA (PB2-side) has no remaining consumer -> no_connect ---
    old_spi_cs = ('  (wire (pts (xy 78.74 1033.78) (xy 82.55 1033.78)) (stroke (width 0) (type default)) '
                  '(uuid "49030000-0000-0000-0000-0000000013af"))\n'
                  '  (global_label "SPI1_CS_LORA" (shape passive) (at 82.55 1033.78 0) '
                  '(effects (font (size 1.27 1.27)) (justify left)) (uuid "49030000-0000-0000-0000-0000000013b0"))')
    assert old_spi_cs in sch, "SPI1_CS_LORA (PB2-side) wire+label not found verbatim"
    sch = sch.replace(old_spi_cs, no_connect(78.74, 1033.78))

    SCH.write_text(sch)
    SYM.write_text(sym)
    print("LoRa -> SIK swap done: lib_symbol, instance, wiring, PB2 net repurposing.")


if __name__ == "__main__":
    main()
