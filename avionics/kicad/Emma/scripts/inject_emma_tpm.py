#!/usr/bin/env python3
"""inject_emma_tpm.py -- add an SLB9670 TPM to Emma.kicad_sch via text
injection (same non-destructive pattern as Kaylee's
inject_kaylee_trust_module.py), rather than a full gen_emma_sch.py rerun.

Emma (49 MHz + LoRa transceiver cape) has no MCU of its own -- it connects
only via the P1+P2 header stack to its host PocketBeagle2 node, which
already carries Wash + Zoe (both of which already have their own TPM). Per
user direction: Emma does NOT need its own isolated CAN-FD/RS-485 (it rides
Zoe's), it only needs its own TPM so ITS OWN telemetry/config messages can
be signed with an Emma-specific key.

The TPM's SPI+control lines are exposed on a NEW dedicated 6-pin header
(J_TPM, see lib_symbol_j_tpm_emma()) rather than tapped into Emma's
existing P1/P2 PocketBeagle2 stack -- an earlier draft tried reusing Wash's
"SPI0_CLK" etc. net names directly, but global labels only merge within one
schematic FILE; reusing the same net-name string across Wash.kicad_sch and
Emma.kicad_sch does NOT actually connect them (two separate boards/files),
and produced 5 "input not driven" ERC errors on the TPM's own input pins
once actually checked. A dedicated header is unambiguous and ERC-correct
without needing to first verify which P1/P2 pins are free on the PB2 side.

Uses the ALREADY-VERIFIED Jayne_SLB9670_TPM clean-room symbol (real
Infineon datasheet pin numbers) -- NOT Wash's own inline "SLB9670" symbol,
which was found during this same pass to have incorrect pin numbers (e.g.
its pin 24 is labeled CS_N; the real datasheet's pin 24 is MISO). That is a
separate, pre-existing defect on Wash, out of scope for this change (not
requested), flagged in REFERENCES.md / TODO.md.

OPEN ITEM: SPI0_CS_TPM_EMMA / TPM_IRQN_EMMA / TPM_RSTN_EMMA are placeholder
net names for Emma's own chip-select/IRQ/reset -- which physical P1/P2
header pin these land on (a free PocketBeagle2 GPIO not already claimed by
Wash/Zoe on the same stack) has NOT been verified against the PB2 pinout
and needs confirmation before fab.

Usage: python3 inject_emma_tpm.py
Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI-assist: Claude Fable 5 (Anthropic), 2026-07-26
License: CC BY 4.0
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
KICADS = HERE.parent / "kicads"
SCH = KICADS / "Emma.kicad_sch"
SYMDIR = HERE.parent.parent / "symbols"

_uid_i = [0]


def _next_uid():
    _uid_i[0] += 1
    val = _uid_i[0]
    h = f"{val:032x}"
    return f"7ee00000-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


def parse_real_symbol(name):
    src = (SYMDIR / f"{name}.kicad_sym").read_text()
    start = src.index(f'(symbol "{name}"')
    depth = 0
    end = None
    for i in range(start, len(src)):
        if src[i] == "(":
            depth += 1
        elif src[i] == ")":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    lib_block = src[start:end]
    pins = []
    unit = None
    lines = src.splitlines()
    i = 0
    while i < len(lines):
        mu = re.search(r'\(symbol "[^"]+_(\d+)_\d+"', lines[i])
        if mu:
            unit = int(mu.group(1))
        mp = re.match(
            r"\s*\(pin\s+(\w+)\s+\w+\s+\(at\s+([-\d.]+)\s+([-\d.]+)\s+(\d+)\)", lines[i]
        )
        if mp:
            etype = mp.group(1)
            x, y, ang = float(mp.group(2)), float(mp.group(3)), int(mp.group(4))
            pname = re.search(r'\(name "([^"]+)"', lines[i + 1]).group(1)
            pnum = re.search(r'\(number "([^"]+)"', lines[i + 2]).group(1)
            pins.append((pnum, pname, x, y, ang, etype, unit))
            i += 3
            continue
        i += 1
    return lib_block, pins


def glabel(name, x, y, rot=0):
    return (
        f'  (global_label "{name}" (shape bidirectional) (at {x:.2f} {y:.2f} {rot})\n'
        f"    (effects (font (size 1.016 1.016)))\n"
        f'    (uuid "{_next_uid()}")\n'
        f'    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {x:.2f} {y:.2f} 0)\n'
        f"      (effects (font (size 1.016 1.016)) (hide yes))))"
    )


def no_connect(x, y):
    return f'  (no_connect (at {x:.2f} {y:.2f}) (uuid "{_next_uid()}"))'


def text_note(txt, x, y):
    return (
        f'  (text "{txt}" (at {x:.2f} {y:.2f} 0)\n'
        f"    (effects (font (size 1.27 1.27)))\n"
        f'    (uuid "{_next_uid()}"))'
    )


def sym_inst_unit(lib_id, ref, value, cx, cy, unit, footprint):
    return "\n".join(
        [
            f'  (symbol (lib_id "{lib_id}") (at {cx:.2f} {cy:.2f} 0)',
            f"    (unit {unit}) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)",
            f'    (uuid "{_next_uid()}")',
            f'    (property "Reference" "{ref}" (at {cx:.2f} {cy - 2.0:.2f} 0)',
            f"      (effects (font (size 1.27 1.27))))",
            f'    (property "Value" "{value}" (at {cx:.2f} {cy + 2.0:.2f} 0)',
            f"      (effects (font (size 1.27 1.27))))",
            f'    (property "Footprint" "{footprint}" (at 0 0 0)',
            f"      (effects (font (size 1.27 1.27)) (hide yes)))",
            "  )",
        ]
    )


def two_pin(lib_id, ref, value, cx, cy, net1, net2, footprint):
    # NOTE: matches _gen2pin()'s own pin geometry (+/-3.81), NOT the 2.54
    # offset used by this project's OTHER generators (different symbol,
    # different pin spacing) -- this exact mismatch caused a real bug here
    # on the first pass (every 2-pin part showed "pin not connected").
    return [
        sym_inst_unit(lib_id, ref, value, cx, cy, 1, footprint),
        glabel(net1, cx - 3.81, cy, rot=180),
        glabel(net2, cx + 3.81, cy, rot=0),
    ]


TPM_FOOTPRINT = "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm"


def lib_symbol_j_tpm_emma():
    # Dedicated 6-pin header for the TPM's SPI+control -- NOT tapped into
    # Emma's existing P1/P2 PocketBeagle2 stack (that header's exact free
    # pins were not verified against the PB2 pinout in the time available --
    # tracked as an open item). Pin ELECTRICAL TYPE is set from the HOST's
    # point of view (this connector is where the host's signal enters/exits
    # Emma): SCLK/MOSI/CS#/RST# are "output" (host drives them onto Emma),
    # MISO/IRQ# are "input" (Emma's TPM drives them back to the host) -- so
    # each of the TPM's own input pins gets a real ERC driver instead of a
    # dangling global label with nothing behind it.
    pins = [
        ("SCLK", "output"), ("MOSI", "output"), ("CS_N", "output"),
        ("RST_N", "output"), ("MISO", "input"), ("IRQ_N", "input"),
    ]
    half = (len(pins) - 1) * 1.27
    lines = [
        '  (symbol "J_TPM_EMMA" (in_bom yes) (on_board yes)',
        f'    (property "Reference" "J" (at 0 {-(half + 3.81):.2f} 0) (effects (font (size 1.27 1.27))))',
        f'    (property "Value" "J_TPM_EMMA" (at 0 {(half + 3.81):.2f} 0) (effects (font (size 1.27 1.27))))',
        '    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '    (symbol "J_TPM_EMMA_0_1"',
        f"      (rectangle (start -2.54 {-half - 1.27:.2f}) (end 2.54 {half + 1.27:.2f})))",
        '    (symbol "J_TPM_EMMA_1_1"',
    ]
    for i, (pname, ptype) in enumerate(pins):
        py = -half + i * 2.54
        lines.append(
            f'      (pin {ptype} line (at -5.08 {py:.2f} 0) (length 2.54)\n'
            f'        (name "{pname}" (effects (font (size 1.016 1.016))))\n'
            f'        (number "{i + 1}" (effects (font (size 1.016 1.016)))))'
        )
    lines.append("    )")
    lines.append("  )")
    return "\n".join(lines)


def lib_symbol_pwr_flag():
    return (
        '  (symbol "PWR_FLAG_TPM" (power) (in_bom no) (on_board no)\n'
        '    (property "Reference" "#FLG" (at 0 1.905 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
        '    (property "Value" "PWR_FLAG" (at 0 3.556 0) (effects (font (size 1.27 1.27))))\n'
        '    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
        '    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
        '    (symbol "PWR_FLAG_TPM_0_1"\n'
        "      (polyline (pts (xy 0 0) (xy 0 1.016) (xy -1.016 1.524) (xy 0 2.032) (xy 1.016 1.524) (xy 0 1.016))\n"
        "        (stroke (width 0) (type default)) (fill (type none))))\n"
        '    (symbol "PWR_FLAG_TPM_1_1"\n'
        '      (pin power_out line (at 0 0 90) (length 0)\n'
        '        (name "~" (effects (font (size 1.016 1.016))))\n'
        '        (number "1" (effects (font (size 1.016 1.016)))))\n'
        "    )\n"
        "  )"
    )


def pwr_flag(net, x, y):
    inst = "\n".join(
        [
            f'  (symbol (lib_id "PWR_FLAG_TPM") (at {x:.2f} {y:.2f} 0)',
            "    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)",
            f'    (uuid "{_next_uid()}")',
            f'    (property "Reference" "#FLG" (at {x:.2f} {y - 2.0:.2f} 0)',
            "      (effects (font (size 1.27 1.27)) (hide yes)))",
            f'    (property "Value" "PWR_FLAG" (at {x:.2f} {y + 2.0:.2f} 0)',
            "      (effects (font (size 1.27 1.27))))",
            f'    (pin "1" (uuid "{_next_uid()}"))',
            "  )",
        ]
    )
    return [inst, glabel(net, x, y, rot=90)]


def _gen2pin(name):
    # Emma's own lib_symbols has no generic R/C (only fixed-value/pre-wired
    # blocks like S_1.2k_R / S_+3V_100n with their own idiosyncratic pin
    # geometry) -- add small self-contained 2-pin generics instead of trying
    # to match a different symbol's offsets (source of earlier bugs today).
    return (
        f'  (symbol "{name}" (in_bom yes) (on_board yes)\n'
        f'    (property "Reference" "R" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))\n'
        f'    (property "Value" "{name}" (at 0 2.54 0) (effects (font (size 1.27 1.27))))\n'
        f'    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
        f'    (symbol "{name}_0_1"\n'
        "      (rectangle (start -2.54 -1.27) (end 2.54 1.27)))\n"
        f'    (symbol "{name}_1_1"\n'
        '      (pin passive line (at -3.81 0 0) (length 1.27)\n'
        '        (name "1" (effects (font (size 1.016 1.016))))\n'
        '        (number "1" (effects (font (size 1.016 1.016)))))\n'
        '      (pin passive line (at 3.81 0 180) (length 1.27)\n'
        '        (name "2" (effects (font (size 1.016 1.016))))\n'
        '        (number "2" (effects (font (size 1.016 1.016)))))\n'
        "    )\n"
        "  )"
    )


def build():
    tpm_lib_block, pins = parse_real_symbol("Jayne_SLB9670_TPM")
    lib_block = (
        tpm_lib_block + "\n"
        + _gen2pin("R_Generic_TPM") + "\n"
        + _gen2pin("C_Generic_TPM") + "\n"
        + lib_symbol_j_tpm_emma() + "\n"
        + lib_symbol_pwr_flag()
    )

    netmap = {
        "1": "+3V3", "2": "GND", "8": "+3V3", "9": "GND", "14": "+3V3", "16": "GND",
        "17": "TPM_RSTN_EMMA", "18": "TPM_IRQN_EMMA", "19": "TPM_SCLK_EMMA",
        "20": "TPM_CS_EMMA", "21": "TPM_MOSI_EMMA", "22": "+3V3", "23": "GND",
        "24": "TPM_MISO_EMMA", "32": "GND",
    }
    cx, cy = 250, 1100
    body = [text_note("=== Section: TPM (SLB9670, added 2026-07-26 -- own key/signing identity) ===", 200, 1080)]
    body.append(sym_inst_unit("Jayne_SLB9670_TPM", "TPM", "Infineon SLB9670 TPM2.0", cx, cy, 1, TPM_FOOTPRINT))
    for pnum, pname, x, y, ang, etype, unit in pins:
        sx, sy = cx + x, cy - y
        net = netmap.get(pnum)
        if net is None:
            body.append(no_connect(sx, sy))
        else:
            rot = 180 if ang == 0 else 0
            body.append(glabel(net, sx, sy, rot=rot))
    body.extend(two_pin("R_Generic_TPM", "R_TPM_RST_EMMA", "10k", 210, 1090, "+3V3", "TPM_RSTN_EMMA", "Resistor_SMD:R_0402_1005Metric"))
    body.extend(two_pin("C_Generic_TPM", "C_TPM_EMMA1", "100nF", 210, 1105, "+3V3", "GND", "Capacitor_SMD:C_0402_1005Metric"))
    body.extend(pwr_flag("+3V3", 230, 1090))
    body.extend(pwr_flag("GND", 230, 1105))

    # Dedicated SPI+control header (see lib_symbol_j_tpm_emma() docstring
    # for why this isn't tapped into the existing P1/P2 stack).
    jx, jy = 290, 1100
    j_nets = ["TPM_SCLK_EMMA", "TPM_MOSI_EMMA", "TPM_CS_EMMA", "TPM_RSTN_EMMA", "TPM_MISO_EMMA", "TPM_IRQN_EMMA"]
    body.append(sym_inst_unit("J_TPM_EMMA", "J_TPM", "TPM SPI+control (host PB2 side, open item -- see script docstring)", jx, jy, 1, "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical"))
    half = (len(j_nets) - 1) * 1.27
    for i, net in enumerate(j_nets):
        py = -half + i * 2.54
        body.append(glabel(net, jx - 5.08, jy - py, rot=180))
    return lib_block, body


def inject():
    src = SCH.read_text()
    lib_block, body = build()

    first_instance = src.index('\n  (symbol (lib_id "')
    close_idx = src.rindex("\n  )\n", 0, first_instance) + 1
    src = src[:close_idx] + lib_block + "\n" + src[close_idx:]

    assert src.rstrip().endswith(")")
    last_paren = src.rstrip().rindex(")")
    src = src[:last_paren] + "\n".join(body) + "\n" + src[last_paren:]

    SCH.write_text(src)
    print(f"  Injected TPM (1 lib symbol + {len(body)} body items) into {SCH}")


if __name__ == "__main__":
    inject()
