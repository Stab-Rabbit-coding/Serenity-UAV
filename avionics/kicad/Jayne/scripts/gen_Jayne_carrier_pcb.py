#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_Jayne_carrier_pcb.py -- rebuild Jayne.kicad_pcb in the SoM end-state.
=============================================================================
Drives the PCB from the schematic netlist (exported by kicad-cli from
Jayne.kicad_sch, authored by gen_Jayne_carrier_sch.py).  Removes the old
placeholder-footprint components and instantiates the REAL footprints for every
schematic component, assigns each pad's net from the netlist, and lays the parts
out inside the existing nose-carrier trapezoid outline (SoM on the back copper,
carrier ICs + regulators + connectors on the front).

Placement is an INITIAL, DRC-legal rough pass -- the user reserves final
positioning (avionics/CLAUDE.md: tightly-packed boards get manual final
placement).  The board outline, the four M2.5 corner mounting holes, the netclass
definitions, and the design rules are preserved from the loaded board.

Exposed-pad handling: U2 (KSZ) EP is pad 129 = GND in the clean-room symbol and
in the Jayne TQFP-128-1EP footprint; U3 (MSPM0) EP is pad 49 = VSS; U5 (TPM) EP
is footprint pad 33 with no symbol pin, so it is forced to GND here (SLB9670
thermal pad = GND).  Any footprint pad not named in the netlist and belonging to
one of these EP/thermal-via groups is tied to GND.

Author : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  (Griffing Technology LLC)
AI-assist: Claude Fable 5 (Anthropic) -- pcbnew rebuild, 2026-07-13.
License: CC BY 4.0
"""

import pickle
import re
import sys
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
BOARD = HERE.parent / "kicads" / "Jayne.kicad_pcb"
NET = HERE.parent / "kicads" / "Jayne.net"
PRETTY = str(HERE.parent / "Jayne.pretty")
SYS_FP = "/usr/share/kicad/footprints"

FROMMM = pcbnew.FromMM


# ref -> (library_path, footprint_name, layer)   layer: F or B
def fp(lib, name):
    return (lib, name)


SYS = {
    "SOT23-6": fp(f"{SYS_FP}/Package_TO_SOT_SMD.pretty", "SOT-23-6"),
    "SOT23-5": fp(f"{SYS_FP}/Package_TO_SOT_SMD.pretty", "SOT-23-5"),
    "SOT23": fp(f"{SYS_FP}/Package_TO_SOT_SMD.pretty", "SOT-23"),
    "SOT363": fp(f"{SYS_FP}/Package_TO_SOT_SMD.pretty", "SOT-363_SC-70-6"),
    "R0402": fp(f"{SYS_FP}/Resistor_SMD.pretty", "R_0402_1005Metric"),
    "C0402": fp(f"{SYS_FP}/Capacitor_SMD.pretty", "C_0402_1005Metric"),
    "IND": fp(f"{SYS_FP}/Inductor_SMD.pretty", "L_Taiyo-Yuden_NR-20xx"),
    "CMC": fp(f"{SYS_FP}/Inductor_SMD.pretty", "L_CommonModeChoke_Coilcraft_0805USB"),
    "XTAL": fp(f"{SYS_FP}/Crystal.pretty", "Crystal_SMD_2012-2Pin_2.0x1.2mm"),
    "XFMR": fp(f"{SYS_FP}/Transformer_SMD.pretty", "Wurth_749010012A_10-100BASE-TX"),
    "QFN48": fp(f"{SYS_FP}/Package_DFN_QFN.pretty",
                "QFN-48-1EP_7x7mm_P0.5mm_EP5.15x5.15mm"),
    "QFN32": fp(f"{SYS_FP}/Package_DFN_QFN.pretty",
                "QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm"),
    "SOIC20": fp(f"{SYS_FP}/Package_SO.pretty", "SOIC-20W_7.5x12.8mm_P1.27mm"),
    "JST_GH2": fp(f"{SYS_FP}/Connector_JST.pretty",
                  "JST_GH_BM02B-GHS-TBT_1x02-1MP_P1.25mm_Vertical"),
    "JST_GH4": fp(f"{SYS_FP}/Connector_JST.pretty",
                  "JST_GH_BM04B-GHS-TBT_1x04-1MP_P1.25mm_Vertical"),
    "JST_GH5": fp(f"{SYS_FP}/Connector_JST.pretty",
                  "JST_GH_SM05B-GHS-TB_1x05-1MP_P1.25mm_Horizontal"),
    "JST_SH2": fp(f"{SYS_FP}/Connector_JST.pretty",
                  "JST_SH_BM02B-SRSS-TB_1x02-1MP_P1.00mm_Vertical"),
}
JAYNE = {
    "SOM": fp(PRETTY, "phyCORE-AM62x_PCM071_2xBTH-060"),
    "KSZ": fp(PRETTY, "TQFP-128-1EP_KSZ9477_14x14mm_P0.4mm_EP10x10"),
    "XFMR": fp(PRETTY, "Wurth_749010012A_10-100BASE-TX"),
    "DS9": fp(PRETTY, "DS_Camera_9P"),
    "DS4": fp(PRETTY, "DS_ToF_4P"),
    "DS2": fp(PRETTY, "DS_Laser_2P"),
}

# ref -> (fp_key_dict, key, layer, (x, y), rot)
# layer 'B' = back (SoM); everything else front.  Positions are inside the
# trapezoid: wide/aft end low-X (~176), narrow/fore end high-X (~242).
PLACE = {
    "U_SOM":  (JAYNE, "SOM", "B", (200, 151), 90),
    "U2":     (JAYNE, "KSZ", "F", (198, 150), 0),
    "U3":     (SYS, "QFN48", "F", (216, 138), 0),
    "U5":     (SYS, "QFN32", "F", (216, 163), 0),
    "U4":     (SYS, "SOIC20", "F", (231, 150), 90),
    "U_REG_3V3": (SYS, "SOT23-6", "F", (182, 132), 0),
    "U_REG_1V2": (SYS, "SOT23-6", "F", (182, 140), 0),
    "U_REG_2V5": (SYS, "SOT23-5", "F", (182, 148), 0),
    "U_REG_3V3_L": (SYS, "IND", "F", (188, 132), 0),
    "U_REG_1V2_L": (SYS, "IND", "F", (188, 140), 0),
    "Y1":     (SYS, "XTAL", "F", (192, 163), 0),
    "Q1":     (SYS, "SOT23", "F", (236, 168), 0),
    "T1":     (JAYNE, "XFMR", "F", (180, 160), 0),
    "T2":     (JAYNE, "XFMR", "F", (180, 170), 0),
    "CMC5":   (SYS, "CMC", "F", (224, 138), 0),
    "D5":     (SYS, "SOT363", "F", (224, 143), 0),
    "T1_CMC1": (SYS, "CMC", "F", (188, 158), 0),
    "T1_CMC2": (SYS, "CMC", "F", (188, 162), 0),
    "T1_D1":  (SYS, "SOT363", "F", (192, 158), 0),
    "T1_D2":  (SYS, "SOT363", "F", (192, 172), 0),
    "T2_CMC1": (SYS, "CMC", "F", (188, 168), 0),
    "T2_CMC2": (SYS, "CMC", "F", (188, 172), 0),
    "T2_D1":  (SYS, "SOT363", "F", (192, 168), 0),
    "T2_D2":  (SYS, "SOT363", "F", (196, 172), 0),
    # connectors: ring/power/CAN at wide/aft (low X); sensors at fore (high X)
    "J_PWR":  (SYS, "JST_GH2", "F", (178, 130), 0),
    "J_CANFD": (SYS, "JST_GH4", "F", (178, 136), 0),
    "J_ETH_IN": (SYS, "JST_GH5", "F", (176, 150), 90),
    "J_ETH_OUT": (SYS, "JST_GH5", "F", (176, 165), 90),
    "J_SWD":  (SYS, "JST_GH4", "F", (206, 165), 0),
    "J_CAM1": (SYS, "JST_GH4", "F", (240, 145), 0),
    "J_CAM2": (SYS, "JST_GH4", "F", (240, 150), 0),
    "J_TOF":  (SYS, "JST_GH4", "F", (240, 156), 0),
    "J_LASER": (SYS, "JST_SH2", "F", (240, 161), 0),
    "J_CAM_DS": (JAYNE, "DS9", "F", (233, 138), 0),
    "J_TOF_DS": (JAYNE, "DS4", "F", (233, 162), 0),
    "J_LASER_DS": (JAYNE, "DS2", "F", (236, 165), 0),
    "J_CHASSIS_R": (SYS, "R0402", "F", (204, 172), 0),   # 0R GND/PGND bond
}

# Fallback footprint by reference prefix for passives (auto-placed in rows).
PREFIX_FP = [
    ("R_", SYS, "R0402"),
    ("R1", SYS, "R0402"),
    ("R2", SYS, "R0402"),
    ("C_", SYS, "C0402"),
]

# Approximate courtyard footprint size (w, h) in mm by footprint-name fragment,
# used by the shelf-packer to give every front part a non-overlapping cell.
# (Placement is an initial pass; the user reserves final positioning.)
SIZE_BY_FRAG = [
    ("TQFP-128", (18, 18)),
    ("SOIC-20", (9, 16)),
    ("QFN-48", (9, 9)),
    ("QFN-32", (7, 7)),
    ("Wurth_749010012A", (9, 11)),
    ("DS_Camera", (13, 6)),
    ("DS_ToF", (8, 6)),
    ("DS_Laser", (5, 6)),
    ("JST_GH_SM05B", (10, 7)),
    ("JST_GH_BM04B", (8, 6)),
    ("JST_GH_BM02B", (5, 5)),
    ("JST_SH_BM02B", (5, 5)),
    ("L_Taiyo-Yuden_NR", (5.5, 5.5)),
    ("CommonModeChoke", (4, 4)),
    ("Crystal_SMD_2012", (3, 2.5)),
    ("SOT-23-6", (3.5, 3.5)),
    ("SOT-23-5", (3.5, 3.5)),
    ("SOT-363", (2.6, 2.6)),
    ("SOT-23", (3.2, 3.2)),
    ("R_0402", (1.6, 1.6)),
    ("C_0402", (1.6, 1.6)),
]


def size_of(fpname):
    for frag, wh in SIZE_BY_FRAG:
        if frag in fpname:
            return wh
    return (3.0, 3.0)


def shelf_pack(items, x0=182.0, y0=135.0, x1=216.0, gap=1.4):
    """Assign non-overlapping centre positions (largest-first shelf packing)
    inside the usable front rectangle.  items = [(ref, fpname)] -> {ref:(x,y)}.
    Corner mounting holes sit outside [x0,x1]x[y0,..], so this band clears them."""
    order = sorted(items, key=lambda it: size_of(it[1])[1], reverse=True)
    pos = {}
    x, y, rowh = x0, y0, 0.0
    for ref, fpname in order:
        w, h = size_of(fpname)
        if x + w > x1:
            x = x0
            y += rowh + gap
            rowh = 0.0
        pos[ref] = (round((x + w / 2) / 1.27) * 1.27, round((y + h / 2) / 1.27) * 1.27)
        x += w + gap
        rowh = max(rowh, h)
    return pos


def parse_netlist():
    src = NET.read_text()
    comps = dict(re.findall(r'\(comp \(ref "([^"]+)"\)\s*\(value "([^"]*)"\)', src))
    padnet = {}
    for m in re.finditer(
        r'\(net \(code[^)]*\) \(name "([^"]*)"\)(.*?)(?=\(net \(code|\Z)', src, re.S
    ):
        for r, p in re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"', m.group(2)):
            padnet[(r, p)] = m.group(1)
    return comps, padnet


def main():
    comps, padnet = parse_netlist()
    board = pcbnew.LoadBoard(str(BOARD))

    # NOTE: in this pcbnew build, calling FootprintLoad AFTER board.Remove()
    # segfaults the plugin.  So resolve placement and load EVERY footprint
    # instance FIRST (before any board mutation), then remove + add.
    auto_x, auto_y = 206, 128
    placed_auto = 0
    plan = []   # (ref, fpobj, layer, x, y, rot)
    fpid_map = {}   # ref -> "nickname:footprint" for schematic-parity
    for ref in sorted(comps):
        if ref in PLACE:
            libd, key, layer, (x, y), rot = PLACE[ref]
            lib, fpname = libd[key]
        elif ref.endswith(("_CI", "_CO", "_CV")):
            lib, fpname = SYS["C0402"]          # regulator in/out decoupling caps
            layer, rot = "F", 0
            x, y = auto_x, auto_y
            auto_x += 4
            if auto_x > 240:
                auto_x, auto_y = 206, auto_y + 4
            placed_auto += 1
        else:
            match = next((p for p in PREFIX_FP if ref.startswith(p[0])), None)
            if match is None:
                print(f"  WARN: no footprint mapping for {ref}, skipping")
                continue
            lib, fpname = match[1][match[2]]
            layer, rot = "F", 0
            x, y = auto_x, auto_y
            auto_x += 4
            if auto_x > 240:
                auto_x, auto_y = 206, auto_y + 4
            placed_auto += 1
        fpobj = pcbnew.FootprintLoad(lib, fpname)
        if fpobj is None:
            print(f"  ERROR: could not load {lib}:{fpname} for {ref}")
            continue
        # library nickname = basename of the .pretty dir (or "Jayne" for PRETTY)
        nick = "Jayne" if lib == PRETTY else Path(lib).name[:-len(".pretty")]
        fpid_map[ref] = f"{nick}:{fpname}"
        plan.append((ref, fpobj, layer, x, y, rot, fpname))

    # Shelf-pack all FRONT parts so nothing overlaps (SoM stays on the back at
    # its hand-set position).  Rotation is normalised to 0 for the packed parts.
    front_pos = shelf_pack([(r, fn) for (r, _f, ly, _x, _y, _rt, fn) in plan
                            if ly != "B"])
    plan = [
        (r, f, ly, front_pos.get(r, (x, y))[0], front_pos.get(r, (x, y))[1],
         0 if ly != "B" else rt)
        for (r, f, ly, x, y, rt, fn) in plan
    ]

    # Remove every footprint except the four corner mounting holes.
    for f in list(board.GetFootprints()):
        if not f.GetReference().startswith("MH"):
            board.Remove(f)

    # Create nets.
    netmap = {}
    for name in sorted({n for n in padnet.values() if n}):
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        netmap[name] = ni

    # This pcbnew build's PAD wrapper is broken (Pads()/FindPadByNumber return
    # raw SwigPyObjects without SetNet), so pad nets are injected by the text
    # post-pass inject_pad_nets() below -- here we only place + flip footprints
    # and declare the nets.
    for ref, fpobj, layer, x, y, rot in plan:
        fpobj.SetReference(ref)
        fpobj.SetValue(comps.get(ref, ""))
        fpobj.SetPosition(pcbnew.VECTOR2I(FROMMM(x), FROMMM(y)))
        board.Add(fpobj)
        if layer == "B":
            fpobj.SetLayerAndFlip(pcbnew.B_Cu)
        if rot:
            fpobj.SetOrientationDegrees(rot)

    pcbnew.SaveBoard(str(BOARD), board)
    print(f"  Placed {len(board.GetFootprints())} footprints, "
          f"{board.GetNetCount()} nets, {placed_auto} auto-placed passives")
    inject_pad_nets(padnet, fpid_map)
    return 0


def inject_pad_nets(padnet, fpid_map):
    """Text post-pass: assign each pad its net (the pcbnew pad API is broken in
    this build, and SaveBoard prunes zero-pad nets).  Rebuilds the board's net
    table from the schematic netlist, then writes `(net <code> "<name>")` into
    every pad keyed by (reference, pad#).  Forces the KSZ/MSPM0/TPM thermal EP
    pads to GND."""
    EP_GND = {"U2": ["129"], "U3": ["49"], "U5": ["33"]}
    src = BOARD.read_text()

    # Full net-code table from the schematic netlist (code 0 = unconnected).
    names = sorted({n for n in padnet.values() if n})
    code = {"": 0}
    for idx, name in enumerate(names, start=1):
        code[name] = idx

    # Replace the board's top-level (net ...) declaration block.
    decl = "\n".join(f'\t(net {code[n]} "{n}")' for n in [""] + names)
    src = re.sub(r'(?m)^\t\(net \d+ "[^"]*"\)\n', "", src)      # drop old decls
    # re-insert the fresh block right before the first footprint
    fp0 = src.find("\t(footprint ")
    src = src[:fp0] + decl + "\n" + src[fp0:]

    # Split into footprint blocks by brace-balance; rewrite pads inside each.
    out = []
    i = 0
    while True:
        j = src.find("(footprint ", i)
        if j == -1:
            out.append(src[i:])
            break
        out.append(src[i:j])
        depth = 0
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
        # Qualify the footprint identity with its library nickname so
        # schematic-parity matches (FootprintLoad-by-path drops the nickname).
        if ref in fpid_map:
            block = re.sub(r'\(footprint "[^"]*"',
                           f'(footprint "{fpid_map[ref]}"', block, count=1)
        assign = {p: n for (r, p), n in padnet.items() if r == ref}
        for ep in EP_GND.get(ref, []):
            assign.setdefault(ep, "GND")

        # Insert (net ...) right after each pad's (layers ...) sub-list.
        def rewrite_pad(padtxt):
            num = re.match(r'\(pad "([^"]*)"', padtxt).group(1)
            net = assign.get(num)
            padtxt = re.sub(r'\s*\(net \d+ "[^"]*"\)', '', padtxt)  # clear old
            if net is None or net not in code:
                return padtxt
            netexpr = f'\n\t\t(net {code[net]} "{net}")'
            lm = re.search(r'\(layers[^)]*\)', padtxt)
            if lm:
                p = lm.end()
                return padtxt[:p] + netexpr + padtxt[p:]
            return padtxt
        # match a full pad (...) block by brace balance
        newblock = []
        p = 0
        while True:
            pj = block.find("(pad ", p)
            if pj == -1:
                newblock.append(block[p:])
                break
            newblock.append(block[p:pj])
            d = 0
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
    result = "".join(out)

    # Fix zone net-code references to match the rebuilt table (zones carry both
    # (net <code>) and (net_name "<name>"); renumbering nets invalidates the code).
    def fix_zone(m):
        zone = m.group(0)
        nm = re.search(r'\(net_name "([^"]*)"\)', zone)
        if nm and nm.group(1) in code:
            zone = re.sub(r'\(net \d+\)', f'(net {code[nm.group(1)]})', zone, count=1)
        return zone

    result = re.sub(r'\(zone.*?\(net_name "[^"]*"\)', fix_zone, result, flags=re.S)
    BOARD.write_text(result)
    print("  Injected pad nets + net table (text pass).")


if __name__ == "__main__":
    sys.exit(main())
