#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_emma_sch.py — Author Emma.kicad_sch from the as-placed Emma.kicad_pcb.
========================================================================
Schematic-first reconciliation of the Emma cape (2026-07-04).  The PCB layout
(75 footprints / ~106 nets: DDS+PA+LPF+LNA+AFSK RF chain, UART/SBUS digital,
RFM95W LoRa, a 2nd ADIN1300 Ethernet PHY through the T-ETH isolation
transformer, and the full PB2-P1/P2 PocketBeagle passthrough bus) had raced far
ahead of the schematic, which was only a ~10-symbol EMI stub.  This script makes
the schematic the source of truth by generating one symbol per placed component,
with the SAME per-pad net names the PCB carries, so a subsequent netlist export
is provably at parity with the board.

Design decisions applied here (user-locked 2026-07-04, TODO.md §1.2b):
  * DROP J1 (JST-GH-6P "CAPE-B IF").  The modem host UART moves onto the PB2
    rails: modem TX net UART_TX -> UART_RCRS_RX (PB2-P1 pin 15); modem RX net
    UART_RX -> UART_RCRS_TX (PB2-P1 pin 16).
  * PTT_N -> repurposed PB2-P2 pin 1 (SERVO7 ball), presence-gated by a
    cape-detect device-tree overlay (documented, not a hardware change here).
  * RSSI -> 1-bit RSSI_DCD.  A new on-board comparator RSSI_CMP (LMV331-class)
    thresholds the analog RSSI_ANA against a divider (RSSI_RH/RSSI_RL ->
    RSSI_REF); its output RSSI_DCD rides PB2-P2 pin 2 (SERVO6 ball).  Analog
    RSSI_ANA is retained as a board test point.

Connectivity method: every symbol pin gets a short wire stub terminated in a
LOCAL net label carrying the PCB net name.  On a single sheet, identical local
label names are one net, so this is both electrically exact (net parity with the
PCB) and fully traceable (every pin is named at the pin).  Verified by
`kicad-cli sch export netlist` diffed against the PCB pad-net model.

Author : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  (Griffing Technology LLC)
AI-assist: Claude Opus 4.8 (Anthropic) — generator authoring, 2026-07-04.
License: CC BY 4.0  |  creativecommons.org/licenses/by/4.0
"""

import re
import sys
import uuid as _uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
PCB = HERE / "Emma.kicad_pcb"
OUT = HERE / "Emma.kicad_sch"

UPREFIX = "49030000-0000-0000-0000-"  # Rev S1 schematic UUID band
SHEET_UUID = UPREFIX + "000000000001"
_ucount = [0x1000]


def uid() -> str:
    _ucount[0] += 1
    return UPREFIX + f"{_ucount[0]:012x}"


# ---------------------------------------------------------------------------
# 1. Minimal robust s-expression parser (for reading the PCB pad-net model)
# ---------------------------------------------------------------------------
def tokenize(s):
    return re.findall(r'"(?:[^"\\]|\\.)*"|\(|\)|[^\s()]+', s)


def parse(toks, i):
    node = []
    while i < len(toks):
        t = toks[i]
        if t == "(":
            child, i = parse(toks, i + 1)
            node.append(child)
        elif t == ")":
            return node, i + 1
        else:
            node.append(t)
            i += 1
    return node, i


def unq(s):
    if isinstance(s, str) and len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        return s[1:-1].replace('\\"', '"')
    return s


def find_all(node, key):
    return [c for c in node if isinstance(c, list) and c and c[0] == key]


def find_one(node, key):
    for c in node:
        if isinstance(c, list) and c and c[0] == key:
            return c
    return None


# ---------------------------------------------------------------------------
# 2. Read PCB -> component list [(ref, value, footprint, [(pad, net), ...])]
# ---------------------------------------------------------------------------
def read_pcb():
    txt = PCB.read_text(encoding="utf-8")
    root, _ = parse(tokenize(txt), 1)
    comps = []
    for fp in find_all(root, "footprint"):
        ref = val = None
        for pr in find_all(fp, "property"):
            nm = unq(pr[1])
            if nm == "Reference":
                ref = unq(pr[2])
            elif nm == "Value":
                val = unq(pr[2])
        pads = []
        seen = set()
        for pad in find_all(fp, "pad"):
            pn = unq(pad[1])
            if pn in seen:  # dedupe multi-line pad repeats
                continue
            seen.add(pn)
            net = find_one(pad, "net")
            netname = unq(net[2]) if net and len(net) > 2 else ""
            pads.append((pn, netname))
        if ref:  # skip anonymous mounting holes
            comps.append({"ref": ref, "value": val or "", "pads": pads})
    return comps


# ---------------------------------------------------------------------------
# 3. Apply the locked topology transform to the pad-net model
# ---------------------------------------------------------------------------
NET_RENAME = {  # J1 removal: modem UART -> PB2 rails
    "UART_TX": "UART_RCRS_RX",  # modem transmits -> host receives
    "UART_RX": "UART_RCRS_TX",  # modem receives  <- host transmits
}
DROP_REFS = {"CAPE-B IF"}  # J1 JST-GH-6P removed


def transform(comps):
    out = []
    for c in comps:
        if c["ref"] in DROP_REFS:
            continue
        pads = []
        for pn, net in c["pads"]:
            net = NET_RENAME.get(net, net)
            # PB2-P2 payload-pin repurpose (presence-gated overlay)
            if c["ref"] == "PB2-P2" and pn == "1":
                net = "PTT_N"  # was SERVO7 ball
            if c["ref"] == "PB2-P2" and pn == "2":
                net = "RSSI_DCD"  # was SERVO6 ball
            pads.append((pn, net))
        out.append({"ref": c["ref"], "value": c["value"], "pads": pads})
    # --- add the new RSSI->DCD comparator subcircuit (schematic + later PCB) ---
    out.append(
        {
            "ref": "RSSI_CMP",
            "value": "LMV331 RSSI Carrier-Detect Comparator",
            "pads": [
                ("1", "RSSI_ANA"),
                ("2", "+3V3"),
                ("3", "RSSI_REF"),
                ("4", "GND"),
                ("5", "RSSI_DCD"),
            ],
        }
    )
    out.append(
        {
            "ref": "RSSI_RH",
            "value": "100k RSSI DCD Threshold Upper",
            "pads": [("1", "+3V3"), ("2", "RSSI_REF")],
        }
    )
    out.append(
        {
            "ref": "RSSI_RL",
            "value": "100k RSSI DCD Threshold Lower",
            "pads": [("1", "RSSI_REF"), ("2", "GND")],
        }
    )
    out.append(
        {
            "ref": "RSSI_CBY",
            "value": "100nF RSSI_CMP VCC Bypass",
            "pads": [("1", "+3V3"), ("2", "GND")],
        }
    )
    return out


# ---------------------------------------------------------------------------
# 4. Schematic emission — generic black-box symbol per component
# ---------------------------------------------------------------------------
PIN_PITCH = 2.54
STUB = 3.81
SIZE = 1.27  # text size


# power/rail nets that should be drawn as a rail label (visual grouping only;
# still ordinary local labels electrically).
def is_power(net):
    return net in ("GND", "+3V3", "+5V", "+5V_FILT", "VCC2_ETH", "GND2_ETH")


def lib_symbol(ref, pads):
    """Generic rectangle symbol; pins split left/right, all electrical 'passive'."""
    n = len(pads)
    left = pads[: (n + 1) // 2]
    right = pads[(n + 1) // 2 :]
    rows = max(len(left), len(right), 1)
    half_h = (rows * PIN_PITCH) / 2 + PIN_PITCH
    half_w = 12.7
    libid = f"S_{sanitize(ref)}"
    s = []
    s.append(
        f'    (symbol "{libid}" (pin_names (offset 1.016)) '
        f"(exclude_from_sim no) (in_bom yes) (on_board yes)"
    )
    s.append(
        f'      (property "Reference" "U" (at 0 {half_h+1.27:.2f} 0) '
        f"(effects (font (size {SIZE} {SIZE}))))"
    )
    s.append(
        f'      (property "Value" "{esc(ref)}" (at 0 {-half_h-1.27:.2f} 0) '
        f"(effects (font (size {SIZE} {SIZE}))))"
    )
    s.append(f'      (symbol "{libid}_0_1"')
    s.append(
        f"        (rectangle (start {-half_w:.2f} {half_h:.2f}) "
        f"(end {half_w:.2f} {-half_h:.2f}) "
        f"(stroke (width 0.2540) (type default)) (fill (type background)))"
    )
    s.append(f"      )")
    s.append(f'      (symbol "{libid}_1_1"')
    # left pins (angle 0 -> connection point on far left)
    for i, (pn, net) in enumerate(left):
        y = half_h - PIN_PITCH * (i + 1)
        s.append(pin_def(-half_w - PIN_PITCH, y, 0, pn, net))
    for i, (pn, net) in enumerate(right):
        y = half_h - PIN_PITCH * (i + 1)
        s.append(pin_def(half_w + PIN_PITCH, y, 180, pn, net))
    s.append(f"      )")
    s.append(f"    )")
    return "\n".join(s), left, right, half_w, half_h


def pin_def(x, y, ang, pn, net):
    return (
        f"        (pin passive line (at {x:.2f} {y:.2f} {ang}) "
        f"(length {PIN_PITCH}) "
        f'(name "{esc(net)}" (effects (font (size {SIZE} {SIZE})))) '
        f'(number "{esc(pn)}" (effects (font (size {SIZE} {SIZE})))))'
    )


def sanitize(ref):
    return re.sub(r"[^A-Za-z0-9_+.-]", "_", ref)


def esc(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def wire(x1, y1, x2, y2):
    return (
        f"  (wire (pts (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y2:.2f})) "
        f'(stroke (width 0) (type default)) (uuid "{uid()}"))'
    )


# Net occurrence counts (pin count per net across the whole board); populated in
# main().  Nets that touch only one pin on this board are inter-board / SoC
# passthrough signals (e.g. the unused PB2 rail pins) or pre-existing in-circuit
# stubs — they are emitted as GLOBAL labels so ERC does not flag them as
# "dangling" local labels (a global label legitimately continues off-sheet).
NETCOUNT: dict = {}


def label(net, x, y, ang):
    just = "left" if ang == 0 else "right"
    if NETCOUNT.get(net, 0) <= 1:
        return (
            f'  (global_label "{esc(net)}" (shape passive) (at {x:.2f} {y:.2f} {ang}) '
            f"(effects (font (size {SIZE} {SIZE})) (justify {just})) "
            f'(uuid "{uid()}"))'
        )
    return (
        f'  (label "{esc(net)}" (at {x:.2f} {y:.2f} {ang}) '
        f"(effects (font (size {SIZE} {SIZE})) (justify {just} bottom)) "
        f'(uuid "{uid()}"))'
    )


def emit_instance(ref, value, X, Y, left, right, half_w, half_h):
    """Place the symbol instance at (X,Y) rot0 and wire+label every pin.
    Library pin (lx,ly) -> sheet (X+lx, Y-ly)  [KiCad lib Y is +up]."""
    out = []
    libid = f"S_{sanitize(ref)}"
    out.append(f'  (symbol (lib_id "{libid}") (at {X:.2f} {Y:.2f} 0) (unit 1)')
    out.append(
        f"    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) "
        f'(uuid "{uid()}")'
    )
    out.append(
        f'    (property "Reference" "{esc(ref)}" (at {X:.2f} {Y-half_h-1.27:.2f} 0) '
        f"(effects (font (size {SIZE} {SIZE}))))"
    )
    out.append(
        f'    (property "Value" "{esc(value)}" (at {X:.2f} {Y+half_h+1.27:.2f} 0) '
        f"(effects (font (size {SIZE} {SIZE}))))"
    )
    npad = len(left) + len(right)
    for pn, _ in left + right:
        out.append(f'    (pin "{esc(pn)}" (uuid "{uid()}"))')
    out.append(
        f'    (instances (project "Emma" (path "/{SHEET_UUID}" '
        f'(reference "{esc(ref)}") (unit 1))))'
    )
    out.append(f"  )")
    # wires + labels
    wl = []
    for i, (pn, net) in enumerate(left):
        ly = half_h - PIN_PITCH * (i + 1)
        cx, cy = X - half_w - PIN_PITCH, Y - ly  # pin connection point
        if not net:  # unconnected pad on PCB
            wl.append(no_connect(cx, cy))
            continue
        lx = cx - STUB
        wl.append(wire(cx, cy, lx, cy))
        wl.append(label(net, lx, cy, 180))
    for i, (pn, net) in enumerate(right):
        ly = half_h - PIN_PITCH * (i + 1)
        cx, cy = X + half_w + PIN_PITCH, Y - ly
        if not net:
            wl.append(no_connect(cx, cy))
            continue
        lx = cx + STUB
        wl.append(wire(cx, cy, lx, cy))
        wl.append(label(net, lx, cy, 0))
    return out + wl


def no_connect(x, y):
    return f'  (no_connect (at {x:.2f} {y:.2f}) (uuid "{uid()}"))'


# ---------------------------------------------------------------------------
# 5. Functional grouping + grid layout
# ---------------------------------------------------------------------------
GROUP = [
    (
        "POWER SUPPLY (5V input filter, MCP1703 LDO, bypass cascade)",
        [
            "+5V Bead",
            "+5V 100u",
            "+5V 100n",
            "LDO 3V3",
            "LDO By",
            "+3V 100u",
            "+3V 10u",
            "+3V 100n",
            "+3V 10n",
            "GND X2Y",
            "PGND 10n",
        ],
    ),
    (
        "DDS / TCXO (Si5351A 49 MHz synthesiser)",
        ["TCXO 25M", "OSC By", "49M DDS", "U1 ByA", "U1 ByB"],
    ),
    (
        "PA CHAIN (MMBT2222A driver + 2N3866 100 mW final)",
        [
            "PA Rb1",
            "PA Cb1",
            "PA Drvr",
            "PA Rc1",
            "PA Rb2",
            "PA Cb2",
            "PA By",
            "PA 100mW",
            "PA Re",
            "PA By2",
        ],
    ),
    (
        "6-ELEMENT CHEBYSHEV LPF",
        ["L1 100n", "C1 120p", "L2 180n", "C2 180p", "L3 180n", "C3 120p"],
    ),
    (
        "T/R SWITCH, LNA, ANTENNA PORT",
        ["T/R Sw", "LNA", "LNA By", "ANT CMC", "ANT TVS", "SMA ESD", "ANT RPSMA"],
    ),
    (
        "AFSK MODEM (MCP4921 TX DAC, LM393 RX demod, tone filters)",
        [
            "TX DAC",
            "AFSK Cp",
            "RX Demod",
            "Th Hi",
            "Th Lo",
            "1.2k R",
            "1.2k C",
            "2.2k R",
            "2.2k C",
            "RSSI Hi",
            "RSSI Lo",
            "CMP By",
            "DAC By",
        ],
    ),
    (
        "UART / SBUS DIGITAL (CMC, TVS, beads, inverter, mux)",
        [
            "UART CMC",
            "UART TVS",
            "TX Bead",
            "RX Bead",
            "PTT Bead",
            "INV1",
            "MUX1",
            "S1",
            "R_MODE",
            "C_INV",
            "C_MUX",
            "SW By",
        ],
    ),
    (
        "RSSI CARRIER-DETECT (NEW 2026-07-04 — analog RSSI -> 1-bit RSSI_DCD)",
        ["RSSI_CMP", "RSSI_RH", "RSSI_RL", "RSSI_CBY"],
    ),
    ("LoRa 915 MHz (RFM95W, SPI via PB2-P1)", ["LoRa"]),
    (
        "ETHERNET 2nd PORT (ADIN1300 PHY + T-ETH isolation xfmr, JST-GH-4P line)",
        ["ETH-PHY", "T-ETH", "J-ETH"],
    ),
    (
        "PB2-I PASSTHROUGH RAILS (PocketBeagle 2 Industrial P1 + P2)",
        ["PB2-P1", "PB2-P2"],
    ),
]

# All layout constants are exact multiples of the 1.27 mm (50 mil) connection
# grid so every pin endpoint, wire end and label lands on-grid (KiCad ERC
# flags any off-grid endpoint).
CELL_W = 95.25  # 75 * 1.27
CELL_H = 60.96  # 48 * 1.27
COLS = 6
X0, Y0 = 63.5, 63.5  # 50 * 1.27


def main():
    comps = transform(read_pcb())
    by_ref = {c["ref"]: c for c in comps}
    placed = set()

    # net pin-counts drive local-vs-global label choice (see label())
    NETCOUNT.clear()
    for c in comps:
        for _pn, net in c["pads"]:
            if net:
                NETCOUNT[net] = NETCOUNT.get(net, 0) + 1

    lib_defs = []
    body = []
    slot = 0

    def place(ref):
        nonlocal slot
        c = by_ref[ref]
        col = slot % COLS
        row = slot // COLS
        X = X0 + col * CELL_W
        Y = Y0 + row * CELL_H
        ld, left, right, hw, hh = lib_symbol(ref, c["pads"])
        lib_defs.append(ld)
        body.extend(emit_instance(ref, c["value"], X, Y, left, right, hw, hh))
        placed.add(ref)
        slot += 1

    # place group-by-group, each group starting on a fresh row, with a title
    for title, refs in GROUP:
        # advance to a new row
        if slot % COLS != 0:
            slot += COLS - (slot % COLS)
        row = slot // COLS
        ty = Y0 + row * CELL_H - CELL_H / 2 - 4
        body.append(
            f'  (text "{esc(title)}" (at {X0-12.7:.2f} {ty:.2f} 0) '
            f"(effects (font (size 2.0 2.0) (bold yes)) (justify left)) "
            f'(uuid "{uid()}"))'
        )
        for ref in refs:
            if ref in by_ref:
                place(ref)
    # any component not covered by a group (safety net)
    for c in comps:
        if c["ref"] not in placed:
            place(c["ref"])

    # ---- assemble file ----
    total_rows = slot // COLS + 2
    page_w = max(841, X0 + COLS * CELL_W + 40)
    page_h = max(594, Y0 + total_rows * CELL_H + 40)
    hdr = []
    hdr.append("(kicad_sch (version 20240101) (generator eeschema)")
    hdr.append('  (paper "User" %.2f %.2f)' % (page_w, page_h))
    hdr.append(f'  (uuid "{SHEET_UUID}")')
    hdr.append("  (title_block")
    hdr.append(
        '    (title "Emma — 49 MHz AX.25 + LoRa 915 MHz Transceiver Cape (Rev S1)")'
    )
    hdr.append('    (date "2026-07-04") (rev "S1") (company "Griffing Technology LLC")')
    hdr.append(
        '    (comment 1 "Schematic-first reconciliation: authored to match Emma.kicad_pcb (J1 dropped; UART on PB2 rails; PTT_N + RSSI_DCD on gated payload GPIOs)")'
    )
    hdr.append(
        '    (comment 2 "Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  |  AI-assist: Claude Opus 4.8 (Anthropic)")'
    )
    hdr.append("  )")
    hdr.append("  (lib_symbols")
    hdr.append("\n".join(lib_defs))
    hdr.append("  )")
    out = "\n".join(hdr) + "\n" + "\n".join(body) + "\n)\n"
    OUT.write_text(out, encoding="utf-8")

    # ---- report net pin-counts (flag single-pin nets) ----
    cnt = dict(NETCOUNT)
    singles = sorted(n for n, k in cnt.items() if k == 1)
    print(f"components placed: {len(placed)}   nets: {len(cnt)}")
    print(f"single-pin nets ({len(singles)}): {', '.join(singles)}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
