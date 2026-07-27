#!/usr/bin/env python3
"""gen_can_periph_gw_pcb.py -- generate CAN-PERIPH-GW-1.kicad_pcb.

First-pass footprint population for the CAN-PERIPH-GW-1 trust-module gateway
board (see CAN-PERIPH-GW-1.md and gen_can_periph_gw_sch.py). Follows the same
pipeline this project already uses for ENC-NACELLE-1
(gen_enc_nacelle_pcb.py): export the schematic netlist, place every real
system-library footprint via pcbnew at a grid position, inject per-pad nets
by (reference, pad) from the netlist, pour a two-layer GND zone, fill.

SCOPE NOTE (documented per avionics/AGENTS.md "final footprint positions are
placed manually by the user after script-driven population"): this pass
places every footprint with correct nets and a generous non-overlapping grid
-- it does NOT hand-route signal traces (30+ nets). DRC will report
unconnected-ratsnest items for the un-routed nets; that is expected at this
stage and is tracked as an open item in CAN-PERIPH-GW-1.md / TODO.md, the
same documented-residual-DRC pattern already used for Kaylee's own PCB
generator (gen_kaylee_pcb.py docstring).

RS-485 isolation is ISOW1412 (own integrated isolated DC-DC per stack, no
external DC-DC placeholder needed -- see schematic docstring).

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI-assist: Claude Fable 5 (Anthropic), 2026-07-26
License: CC BY 4.0
"""

import re
import subprocess
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_can_periph_gw_sch import N_STACKS  # single source of truth (see that module's header)

HERE = Path(__file__).resolve().parent
KICADS = HERE.parent / "kicads"
BOARD = KICADS / "CAN-PERIPH-GW-1.kicad_pcb"
SCH = KICADS / "CAN-PERIPH-GW-1.kicad_sch"
NETLIST = KICADS / "CAN-PERIPH-GW-1.net"
SYS_FP = "/usr/share/kicad/footprints"
CUSTOM_FP = str(HERE.parent.parent / "Serenity-Custom.pretty")

# Per-stack nets (suffixed "_i" in the schematic, i=1..N_STACKS) plus the
# board-shared bus/power nets (unsuffixed) -- see gen_can_periph_gw_sch.py.
_PER_STACK_NETS = [
    "MCU_NRST", "MCU_VCORE", "MCU_SWDIO", "MCU_SWCLK",
    "TPM_SPI_CS", "TPM_SPI_SCK", "TPM_SPI_MOSI", "TPM_SPI_MISO",
    "TPM_PIRQ", "TPM_RESET_N",
    "ENC_SPI_CS", "ENC_SPI_SCK", "ENC_SPI_MOSI", "ENC_SPI_MISO", "ENC_ERROR",
    "CANFD_TX", "CANFD_RX", "CANFD_FLT_N",
    "RS485_TX", "RS485_RX", "RS485_DE", "RS485_FLT_N",
    "ISO_5V_CAN", "ISO_3V3_485",
    "FLEX_UART_TX", "FLEX_UART_RX", "FLEX_TTL_GPIO", "FLEX_PWM_IO", "FLEX_BSHOT_IO",
]
_SHARED_NETS = [
    "+3V3", "+5V", "GND",
    "ISO_GND_CAN", "ISO_GND_485",
    "CAN_H", "CAN_L", "CANTERM_MID",
    "RS485_A", "RS485_B", "TERM485_MID",
    "U_REG_SW", "U_REG_FB",
]
NETS = list(_SHARED_NETS)
for i in range(1, N_STACKS + 1):
    NETS += [f"{n}_{i}" for n in _PER_STACK_NETS]
CODE = {name: idx for idx, name in enumerate(NETS, start=1)}

# ---------------------------------------------------------------------------
# Placement: ref -> (lib dir, footprint name, (x, y), rotation deg)
# Simple non-overlapping grid, grouped loosely by schematic section --
# final compaction/routing is a manual follow-on pass (see module docstring).
# Per-stack footprints are duplicated N_STACKS times (own MCU/TPM/CAN-FD/
# RS-485/encoder/flex per stack); the power section and both shared buses
# (CAN-FD, RS-485) + termination + isolated DC-DC are placed ONCE regardless
# of N_STACKS, matching the schematic's shared-bus wiring.
# ---------------------------------------------------------------------------
QFN = f"{SYS_FP}/Package_DFN_QFN.pretty"
SO = f"{SYS_FP}/Package_SO.pretty"
SOT = f"{SYS_FP}/Package_TO_SOT_SMD.pretty"
RSMD = f"{SYS_FP}/Resistor_SMD.pretty"
CSMD = f"{SYS_FP}/Capacitor_SMD.pretty"
LSMD = f"{SYS_FP}/Inductor_SMD.pretty"
JST = f"{SYS_FP}/Connector_JST.pretty"
PINHDR = f"{SYS_FP}/Connector_PinHeader_2.54mm.pretty"
JUMPER = f"{SYS_FP}/Jumper.pretty"

# Real, manually-packed placement captured from the user's built
# CAN-PERIPH-GW-1.kicad_pcb (Rev 2026-07-26, N_STACKS=1 at capture time) --
# NOT an invented grid. Per-stack parts carry an explicit layer ("F"/"B";
# 4 of them -- the MCU/TPM/CAN-FD-iso/RS-485-iso ICs -- are hand-placed on
# the BACK). For stacks 2..N_STACKS this same per-stack template is
# replayed shifted by LANE_DX along X (past the shared bus/power section,
# which is placed once and never duplicated) -- a first-pass mechanical
# repeat of the user's single-stack layout, same "final compaction is a
# manual follow-on pass" convention already used by every generator in
# this project (see module docstring). LANE_DX is sized from the real
# per-stack footprint cluster's own bounding-box span (~34 mm center-to-
# center) plus each edge footprint's own body half-width, so adjacent
# lanes don't collide -- verified via DRC (0 courtyards_overlap/clearance
# from placement) at N_STACKS=4 in a sandboxed dry run, see commit notes.
LANE_DX = 50.0

# ref-without-suffix -> (lib dir, footprint name, (x, y), rotation deg, layer)
_PER_STACK_REAL: dict[str, tuple[str, str, tuple[float, float], float, str]] = {
    "R_NRST": (RSMD, "R_0402_1005Metric", (143.98, 106.0), 0, "F"),
    "C_VCORE": (CSMD, "C_0402_1005Metric", (150.48, 107.0), 0, "F"),
    "C_MCU1": (CSMD, "C_0402_1005Metric", (143.48, 105.0), 0, "F"),
    "J_SWD": (JST, "JST_GH_BM04B-GHS-TBT_1x04-1MP_P1.25mm_Vertical", (174.46, 113.9), 0, "F"),
    "C_TPM1": (CSMD, "C_0402_1005Metric", (167.46, 106.48), 90, "F"),
    "C_TPM2": (CSMD, "C_0402_1005Metric", (168.96, 106.48), 90, "F"),
    "R_TPM_RST": (RSMD, "R_0402_1005Metric", (170.46, 106.51), 90, "F"),
    "C_ISO1": (CSMD, "C_0402_1005Metric", (143.96, 110.0), 0, "F"),
    "C_ISO2": (CSMD, "C_0402_1005Metric", (160.46, 105.0), 0, "F"),
    "C_RS1": (CSMD, "C_0402_1005Metric", (149.48, 110.5), 0, "F"),
    "C_RS2": (CSMD, "C_0402_1005Metric", (163.94, 106.0), 0, "F"),
    "J_ENC": (CUSTOM_FP, "Pigtail_7W_DirectSolder", (140.41, 114.0), 0, "F"),
    "J_FLEX": (PINHDR, "PinHeader_1x08_P2.54mm_Vertical", (166.54, 114.0), -90, "F"),
    "U1": (QFN, "QFN-48-1EP_7x7mm_P0.5mm_EP5.15x5.15mm", (154.75, 106.5625), 180, "B"),
    "U2": (QFN, "QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm", (155.25, 97.5625), 180, "B"),
    "U3": (SO, "SOIC-20W_7.5x12.8mm_P1.27mm", (140.5, 107.0), 90, "B"),
    "U4": (SO, "SOIC-20W_7.5x12.8mm_P1.27mm", (171.0, 106.5), -90, "B"),
}

PLACE: dict[str, tuple[str, str, tuple[float, float], float, str]] = {}
for _base, (_lib, _fpname, (_rx, _ry), _rot, _lyr) in _PER_STACK_REAL.items():
    for _i in range(1, N_STACKS + 1):
        _dx = (_i - 1) * LANE_DX
        PLACE[f"{_base}_{_i}"] = (_lib, _fpname, (_rx + _dx, _ry), _rot, _lyr)

VALUES = {}
for _i in range(1, N_STACKS + 1):
    VALUES.update({
        f"U1_{_i}": "MSPM0G3507", f"R_NRST_{_i}": "10k", f"C_VCORE_{_i}": "1uF",
        f"C_MCU1_{_i}": "100nF", f"J_SWD_{_i}": "SWD", f"U2_{_i}": "SLB9670",
        f"C_TPM1_{_i}": "100nF", f"C_TPM2_{_i}": "1uF", f"R_TPM_RST_{_i}": "10k",
        f"U3_{_i}": "ISOW1044BDFMR", f"C_ISO1_{_i}": "100nF", f"C_ISO2_{_i}": "1uF",
        f"U4_{_i}": "ISOW1412", f"C_RS1_{_i}": "100nF", f"C_RS2_{_i}": "100nF",
        f"J_ENC_{_i}": "AK7455 pigtail", f"J_FLEX_{_i}": "UART/TTL/PWM/BSHOT",
    })

NICK: dict[str, str] = {}
for _i in range(1, N_STACKS + 1):
    NICK.update({
        f"U1_{_i}": "Package_DFN_QFN:QFN-48-1EP_7x7mm_P0.5mm_EP5.15x5.15mm",
        f"R_NRST_{_i}": "Resistor_SMD:R_0402_1005Metric",
        f"C_VCORE_{_i}": "Capacitor_SMD:C_0402_1005Metric",
        f"C_MCU1_{_i}": "Capacitor_SMD:C_0402_1005Metric",
        f"J_SWD_{_i}": "Connector_JST:JST_GH_BM04B-GHS-TBT_1x04-1MP_P1.25mm_Vertical",
        f"U2_{_i}": "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm",
        f"C_TPM1_{_i}": "Capacitor_SMD:C_0402_1005Metric",
        f"C_TPM2_{_i}": "Capacitor_SMD:C_0402_1005Metric",
        f"R_TPM_RST_{_i}": "Resistor_SMD:R_0402_1005Metric",
        f"U3_{_i}": "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm",
        f"C_ISO1_{_i}": "Capacitor_SMD:C_0402_1005Metric",
        f"C_ISO2_{_i}": "Capacitor_SMD:C_0402_1005Metric",
        f"U4_{_i}": "Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm",
        f"C_RS1_{_i}": "Capacitor_SMD:C_0402_1005Metric",
        f"C_RS2_{_i}": "Capacitor_SMD:C_0402_1005Metric",
        f"J_ENC_{_i}": "Serenity-Custom:Pigtail_7W_DirectSolder",
        f"J_FLEX_{_i}": "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical",
    })

# Shared Section A: power (once, feeds every stack) -- real absolute
# positions, placed once regardless of N_STACKS.
PLACE.update({
    "J_PWR": (JST, "JST_GH_BM02B-GHS-TBT_1x02-1MP_P1.25mm_Vertical", (135.435, 99.4), 0, "F"),
    "U_REG_3V3": (SOT, "SOT-23-6", (136.3225, 107.0), 0, "F"),
    "L1": (LSMD, "L_Taiyo-Yuden_NR-20xx", (140.285, 109.5), 0, "F"),
    "R_FBT": (RSMD, "R_0402_1005Metric", (140.95, 105.5), 0, "F"),
    "R_FBB": (RSMD, "R_0402_1005Metric", (147.49, 107.5), 0, "F"),
    "C_IN": (CSMD, "C_0402_1005Metric", (136.98, 110.5), 0, "F"),
    "C_OUT": (CSMD, "C_0402_1005Metric", (133.96, 110.0), 0, "F"),
})
VALUES.update({
    "J_PWR": "+5V/GND", "U_REG_3V3": "TLV62569DBVR", "L1": "2.2uH",
    "R_FBT": "10k", "R_FBB": "20k", "C_IN": "10uF", "C_OUT": "22uF",
})
NICK.update({
    "J_PWR": "Connector_JST:JST_GH_BM02B-GHS-TBT_1x02-1MP_P1.25mm_Vertical",
    "U_REG_3V3": "Package_TO_SOT_SMD:SOT-23-6",
    "L1": "Inductor_SMD:L_Taiyo-Yuden_NR-20xx",
    "R_FBT": "Resistor_SMD:R_0402_1005Metric",
    "R_FBB": "Resistor_SMD:R_0402_1005Metric",
    "C_IN": "Capacitor_SMD:C_0402_1005Metric",
    "C_OUT": "Capacitor_SMD:C_0402_1005Metric",
})

# Shared Sections D/E: the ONE physical CAN-FD bus + ONE physical RS-485 bus
# (true multi-drop topology -- every stack's xcvr taps the same two wires).
# Real absolute positions, placed once regardless of N_STACKS. No shared
# isolated DC-DC is needed -- each stack's own ISOW1412 (U4_i) has an
# integrated isolated DC-DC, same as ISOW1044 (U3_i) already does for CAN-FD.
PLACE.update({
    "J_CAN_IN": (JST, "JST_GH_BM03B-GHS-TBT_1x03-1MP_P1.25mm_Vertical", (144.96, 100.0), 0, "F"),
    "J_CAN_OUT": (JST, "JST_GH_BM03B-GHS-TBT_1x03-1MP_P1.25mm_Vertical", (154.56, 100.0), 0, "F"),
    "R_CANTERM": (RSMD, "R_0402_1005Metric", (153.96, 106.99), 90, "F"),
    "SJ1": (JUMPER, "SolderJumper-2_P1.3mm_Open_Pad1.0x1.5mm", (157.11, 107.0), 0, "F"),
    "J_RS485_IN": (JST, "JST_GH_BM03B-GHS-TBT_1x03-1MP_P1.25mm_Vertical", (165.46, 100.5), 0, "F"),
    "J_RS485_OUT": (JST, "JST_GH_BM03B-GHS-TBT_1x03-1MP_P1.25mm_Vertical", (175.21, 100.0), 0, "F"),
    "R_485TERM": (RSMD, "R_0402_1005Metric", (172.95, 105.5), 0, "F"),
    "SJ2": (JUMPER, "SolderJumper-2_P1.3mm_Open_Pad1.0x1.5mm", (176.46, 106.0), 0, "F"),
})
VALUES.update({
    "J_CAN_IN": "CAN-FD IN", "J_CAN_OUT": "CAN-FD OUT", "R_CANTERM": "120R", "SJ1": "open",
    "J_RS485_IN": "RS485 IN", "J_RS485_OUT": "RS485 OUT", "R_485TERM": "120R", "SJ2": "open",
})
NICK.update({
    "J_CAN_IN": "Connector_JST:JST_GH_BM03B-GHS-TBT_1x03-1MP_P1.25mm_Vertical",
    "J_CAN_OUT": "Connector_JST:JST_GH_BM03B-GHS-TBT_1x03-1MP_P1.25mm_Vertical",
    "R_CANTERM": "Resistor_SMD:R_0402_1005Metric",
    "SJ1": "Jumper:SolderJumper-2_P1.3mm_Open_Pad1.0x1.5mm",
    "J_RS485_IN": "Connector_JST:JST_GH_BM03B-GHS-TBT_1x03-1MP_P1.25mm_Vertical",
    "J_RS485_OUT": "Connector_JST:JST_GH_BM03B-GHS-TBT_1x03-1MP_P1.25mm_Vertical",
    "R_485TERM": "Resistor_SMD:R_0402_1005Metric",
    "SJ2": "Jumper:SolderJumper-2_P1.3mm_Open_Pad1.0x1.5mm",
})

# Real board outline is 130.91,92.45 - 180.01,118.05 for N_STACKS=1; each
# additional stack's lane extends the board by LANE_DX to the right.
X0, Y0 = 130.0, 91.0
X1 = 180.5 + max(0, N_STACKS - 1) * LANE_DX
Y1 = 119.0

# Back-silkscreen attribution block (mirrors the block already on Wash.md /
# Zoe.md boards) -- placed in the open band below the back-side ICs, left
# of the per-stack cluster so it doesn't move as N_STACKS grows.
ATTRIBUTION_TEXT = (
    "TPM-Secured CAN-FD/RS-485 Gateway\n"
    "For the PocketBeagle2 fleet\n"
    "CC BY 4.0 — July 2026\n"
    "Steve Griffing\n"
    "PE(CSE), CISSP-ISSEP, CPP\n"
    "Griffing Technology LLC\n"
    "github.com/Stab-Rabbit-Coding\n"
)
ATTRIBUTION_POS = (135.0, 115.5)


def u():
    return str(uuid.uuid4())


def fmt(v):
    return f"{v:.6f}".rstrip("0").rstrip(".")


def outline_records():
    pts = [(X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1)]
    out = []
    for (sx, sy), (ex, ey) in zip(pts, pts[1:] + pts[:1]):
        out.append(
            f"\t(gr_line\n\t\t(start {fmt(sx)} {fmt(sy)})\n\t\t(end {fmt(ex)} {fmt(ey)})\n"
            f'\t\t(stroke\n\t\t\t(width 0.1)\n\t\t\t(type solid)\n\t\t)\n'
            f'\t\t(layer "Edge.Cuts")\n\t\t(uuid "{u()}")\n\t)'
        )
    return out


def zone_records():
    out = []
    for layer in ("F.Cu", "B.Cu"):
        pts = f"(xy {X0+2} {Y0+2}) (xy {X1-2} {Y0+2}) (xy {X1-2} {Y1-2}) (xy {X0+2} {Y1-2})"
        out.append(
            f'\t(zone\n\t\t(net {CODE["GND"]})\n\t\t(net_name "GND")\n'
            f'\t\t(layer "{layer}")\n\t\t(uuid "{u()}")\n'
            f"\t\t(hatch edge 0.5)\n"
            f"\t\t(connect_pads\n\t\t\t(clearance 0.2)\n\t\t)\n"
            f"\t\t(min_thickness 0.2)\n\t\t(filled_areas_thickness no)\n"
            f"\t\t(fill yes\n\t\t\t(thermal_gap 0.3)\n\t\t\t(thermal_bridge_width 0.4)\n\t\t)\n"
            f"\t\t(polygon\n\t\t\t(pts\n\t\t\t\t{pts}\n\t\t\t)\n\t\t)\n\t)"
        )
    return out


def base_board_text():
    nets = "\n".join([f'\t(net 0 "")'] + [f'\t(net {CODE[n]} "{n}")' for n in NETS])
    body = "\n".join(outline_records() + zone_records())
    return f"""(kicad_pcb
\t(version 20241229)
\t(generator "pcbnew")
\t(generator_version "9.0")
\t(general
\t\t(thickness 1.6)
\t\t(legacy_teardrops no)
\t)
\t(paper "A4")
\t(title_block
\t\t(title "CAN-PERIPH-GW-1 / MAL-CAN-PERIPH-GW-PCB")
\t\t(date "2026-07-26")
\t\t(rev "1")
\t\t(comment 1 "Serenity UAV -- TPM-secured dual-isolated-bus (CAN-FD+RS-485) peripheral gateway")
\t\t(comment 2 "CC BY 4.0 -- creativecommons.org/licenses/by/4.0")
\t\t(comment 3 "First-pass footprint population; signal routing is an open manual follow-on -- see CAN-PERIPH-GW-1.md")
\t\t(comment 4 "PCB drafted by Claude Fable 5 (Anthropic) via gen_can_periph_gw_pcb.py")
\t)
\t(layers
\t\t(0 "F.Cu" signal)
\t\t(2 "B.Cu" signal)
\t\t(9 "F.Adhes" user "F.Adhesive")
\t\t(11 "B.Adhes" user "B.Adhesive")
\t\t(13 "F.Paste" user)
\t\t(15 "B.Paste" user)
\t\t(5 "F.SilkS" user "F.Silkscreen")
\t\t(7 "B.SilkS" user "B.Silkscreen")
\t\t(1 "F.Mask" user)
\t\t(3 "B.Mask" user)
\t\t(25 "Edge.Cuts" user)
\t\t(27 "Margin" user)
\t\t(31 "F.CrtYd" user "F.Courtyard")
\t\t(29 "B.CrtYd" user "B.Courtyard")
\t\t(35 "F.Fab" user)
\t\t(33 "B.Fab" user)
\t)
\t(setup
\t\t(pad_to_mask_clearance 0)
\t\t(allow_soldermask_bridges_in_footprints no)
\t\t(tenting front back)
\t)
{nets}
{body}
)
"""


def export_netlist():
    subprocess.run(
        ["kicad-cli", "sch", "export", "netlist", "-o", str(NETLIST), str(SCH)],
        check=True,
        capture_output=True,
    )


def parse_padnet():
    src = NETLIST.read_text()
    padnet = {}
    for m in re.finditer(
        r'\(net \(code "[^"]*"\) \(name "([^"]*)"\)(.*?)(?=\(net \(code|\Z)', src, re.S
    ):
        name = m.group(1)
        for r, p in re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"', m.group(2)):
            padnet[(r, p)] = name
    return padnet


def place_footprints():
    import pcbnew

    board = pcbnew.LoadBoard(str(BOARD))
    for name in NETS:
        board.Add(pcbnew.NETINFO_ITEM(board, name))
    for ref, (lib, fpname, (x, y), rot, layer) in PLACE.items():
        fp = pcbnew.FootprintLoad(lib, fpname)
        if fp is None:
            raise RuntimeError(f"cannot load {lib}:{fpname} (ref {ref})")
        fp.SetReference(ref)
        fp.SetValue(VALUES[ref])
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
        board.Add(fp)
        if layer == "B":
            # Real board hand-places the MCU/TPM/CAN-FD-iso/RS-485-iso ICs
            # on the back -- flip (mirrors footprint + moves to B.Cu), then
            # set the recorded absolute rotation (Flip alone doesn't match
            # the captured orientation).
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        if rot:
            fp.SetOrientationDegrees(rot)
    pcbnew.SaveBoard(str(BOARD), board)
    print(f"  placed {len(board.GetFootprints())} footprints")


def add_attribution():
    import pcbnew

    board = pcbnew.LoadBoard(str(BOARD))
    text = pcbnew.PCB_TEXT(board)
    text.SetText(ATTRIBUTION_TEXT)
    text.SetLayer(pcbnew.B_SilkS)
    text.SetPosition(
        pcbnew.VECTOR2I(pcbnew.FromMM(ATTRIBUTION_POS[0]), pcbnew.FromMM(ATTRIBUTION_POS[1]))
    )
    text.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.5), pcbnew.FromMM(0.5)))
    text.SetTextThickness(pcbnew.FromMM(0.08))
    text.SetMirrored(True)
    board.Add(text)
    pcbnew.SaveBoard(str(BOARD), board)
    print("  attribution block added (B.Silkscreen)")


def inject_pad_nets(padnet):
    src = BOARD.read_text()
    decl = "\n".join([f'\t(net 0 "")'] + [f'\t(net {CODE[n]} "{n}")' for n in NETS])
    src = re.sub(r'(?m)^\t\(net \d+ "[^"]*"\)\n', "", src)
    fp0 = src.find("\t(footprint ")
    src = src[:fp0] + decl + "\n" + src[fp0:]

    out = []
    i = 0
    while True:
        j = src.find("\t(footprint ", i)
        if j == -1:
            out.append(src[i:])
            break
        out.append(src[i:j])
        depth = 0
        end = len(src)
        for k in range(j, len(src)):
            if src[k] == "(":
                depth += 1
            elif src[k] == ")":
                depth -= 1
                if depth == 0:
                    end = k + 1
                    break
        block = src[j:end]
        rm = re.search(r'\(property "Reference" "([^"]+)"', block)
        ref = rm.group(1) if rm else None
        if ref in NICK:
            block = re.sub(
                r'\(footprint "[^"]*"', f'(footprint "{NICK[ref]}"', block, count=1
            )
        assign = {p: n for (r, p), n in padnet.items() if r == ref}

        def rewrite_pad(padtxt):
            num = re.match(r'\(pad "([^"]*)"', padtxt).group(1)
            net = assign.get(num)
            padtxt = re.sub(r'\s*\(net \d+ "[^"]*"\)', "", padtxt)
            if net is None or net not in CODE:
                return padtxt
            netexpr = f'\n\t\t\t(net {CODE[net]} "{net}")'
            lm = re.search(r"\(layers[^)]*\)", padtxt)
            if lm:
                p = lm.end()
                return padtxt[:p] + netexpr + padtxt[p:]
            return padtxt

        newblock = []
        p = 0
        while True:
            pj = block.find("(pad ", p)
            if pj == -1:
                newblock.append(block[p:])
                break
            newblock.append(block[p:pj])
            d = 0
            pend = len(block)
            for k in range(pj, len(block)):
                if block[k] == "(":
                    d += 1
                elif block[k] == ")":
                    d -= 1
                    if d == 0:
                        pend = k + 1
                        break
            newblock.append(rewrite_pad(block[pj:pend]))
            p = pend
        out.append("".join(newblock))
        i = end
    BOARD.write_text("".join(out))
    print("  pad nets injected")


def fill_zones():
    import pcbnew

    board = pcbnew.LoadBoard(str(BOARD))
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    pcbnew.SaveBoard(str(BOARD), board)
    print("  zones filled")


def main():
    export_netlist()
    padnet = parse_padnet()
    BOARD.write_text(base_board_text())
    print("  base board written")
    place_footprints()
    inject_pad_nets(padnet)
    add_attribution()
    fill_zones()
    return 0


if __name__ == "__main__":
    sys.exit(main())
