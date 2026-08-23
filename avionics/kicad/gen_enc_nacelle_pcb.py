#!/usr/bin/env python3
"""Generate ENC-NACELLE-1.kicad_pcb — AK7455 off-axis nacelle tilt-encoder board.

Serenity UAV — SKIPPER-TILT-ENC-PCB (see ENC-NACELLE-1.md for the design record).

Board summary (all dimensions mm; KiCad canvas coordinates, Y grows downward):
    * Outline: 7.0 x 14.0 rounded-rect (r = 1.0), X 20..27, Y 20..34.
      7.0 mm is the hard chordwise (flange<->EDF) width from the wing pocket
      (``HALL_PCB_W`` in ``wings_s1223_revo.scad``); the length grows from the
      SCAD's legacy 7 mm to 14 mm because a 4x4 mm QFN24 + 2x M2 holes + a
      7-wire pigtail cannot coexist on 7 x 7 (the pocket was sized for the old
      3x3 MT6701 and is already flagged for re-bake — WBS 1.1.3.6).
    * U1 AK7455 QFN24 at (23.5, 27.9) rot 270 — SPI pins face the pigtail.
    * C1 100 nF 0402 beside VDD pin 11 (left edge); C2 1 uF 0402 right side.
    * P1 7x direct-solder wire lands at the top edge (Serenity-Custom lib).
    * MH1/MH2 M2 self-tap clearance holes (2.2 NPTH, compact courtyard).
    * 2-layer, GND pour on BOTH layers; signals on F.Cu; +3V3 spine and the
      ERROR return run on B.Cu; 6 vias total (0.6/0.3).

Pipeline (per PCBNEW_SWIG_BUG.md — the pcbnew 9.0.2 PAD wrapper is broken):
    1. text-author the base board (header/nets/outline/tracks/vias/zones);
    2. pcbnew: FootprintLoad + place (no pad access, no Remove);
    3. text post-pass: inject per-pad nets keyed by (reference, pad number),
       qualify footprint lib nicknames for schematic parity;
    4. pcbnew: ZONE_FILLER fill + save.

References (see repo REFERENCES.md and ENC-NACELLE-1.md):
    * AKM AK7455 datasheet 200800064-E-00 (avionics/datasheets/).
    * KiCad footprint library (Package_DFN_QFN, Capacitor_SMD) — CC-BY-SA 4.0
      with exception; QFN/0402 footprints used verbatim from the system lib.

Authored by Claude Fable 5 (Anthropic) for Steve Griffing, 2026-07-21.
License: CC BY 4.0.
"""

import re
import subprocess
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOARD = HERE / "ENC-NACELLE-1.kicad_pcb"
SCH = HERE / "ENC-NACELLE-1.kicad_sch"
NETLIST = HERE / "ENC-NACELLE-1.net"
SYS_FP = "/usr/share/kicad/footprints"

# ---------------------------------------------------------------------------
# Net table.  Codes are stable and sorted (code 0 = the unconnected net).
# ---------------------------------------------------------------------------
NETS = ["+3V3", "ENC_CSN", "ENC_ERROR", "ENC_MISO", "ENC_MOSI", "ENC_SCLK", "GND"]
CODE = {name: idx for idx, name in enumerate(NETS, start=1)}

# ---------------------------------------------------------------------------
# Placement plan: ref -> (library dir, footprint, (x, y), rotation degrees)
# ---------------------------------------------------------------------------
PLACE = {
    "U1": (
        f"{SYS_FP}/Package_DFN_QFN.pretty",
        "QFN-24-1EP_4x4mm_P0.5mm_EP2.6x2.6mm",
        (23.5, 27.9),
        270,
    ),
    # Both 0402s live in the top strip (canvas y < 25.3): U1's courtyard is
    # +/-2.6 mm (x 20.9..26.1), so no passives fit beside the QFN.  C_SMD
    # schematic pin 1 is the GND end, pin 2 the +3V3 end (symbol Y-inversion
    # verified against the netlist), hence the rotations below.
    "C1": (f"{SYS_FP}/Capacitor_SMD.pretty", "C_0402_1005Metric", (20.65, 24.3), 270),
    "C2": (f"{SYS_FP}/Capacitor_SMD.pretty", "C_0402_1005Metric", (25.55, 24.35), 90),
    "P1": (
        str(HERE / "Serenity-Custom.pretty"),
        "Pigtail_7W_DirectSolder",
        (23.5, 21.6),
        0,
    ),
    "MH1": (
        str(HERE / "Serenity-Custom.pretty"),
        "MountingHole_2.2mm_M2_SelfTap_Compact",
        (21.4, 32.2),
        0,
    ),
    "MH2": (
        str(HERE / "Serenity-Custom.pretty"),
        "MountingHole_2.2mm_M2_SelfTap_Compact",
        (25.6, 32.2),
        0,
    ),
}
VALUES = {
    "U1": "AK7455",
    "C1": "100nF",
    "C2": "1uF",
    "P1": "PIGTAIL_7W",
    "MH1": "M2_SELF_TAP",
    "MH2": "M2_SELF_TAP",
}

# ---------------------------------------------------------------------------
# Routing plan.  Each entry: (net, layer, width, [(x1, y1), (x2, y2), ...]).
# Polyline points become individual (segment) records.
# ---------------------------------------------------------------------------
TRACKS = [
    # SPI fan-out, F.Cu, QFN top edge (pins 6/5/4 after the 270 rotation)
    # straight down-canvas to the pigtail lands.
    ("ENC_SCLK", "F.Cu", 0.15,
     [(22.25, 25.9625), (22.25, 25.35), (22.4, 24.8), (22.55, 23.2), (22.55, 22.6)]),
    ("ENC_MOSI", "F.Cu", 0.15,
     [(22.75, 25.9625), (22.75, 25.4), (23.1, 24.8), (23.5, 23.9), (23.5, 22.6)]),
    ("ENC_MISO", "F.Cu", 0.15,
     [(23.25, 25.9625), (23.25, 25.45), (23.6, 24.9), (24.1, 24.2), (24.45, 23.4),
      (24.45, 22.6)]),
    # CSN: pin 7 stub -> via -> B.Cu left-edge run -> in-pad via at the land
    # (the F.Cu left channel is occupied by C1, so CSN dives to B.Cu).
    ("ENC_CSN", "F.Cu", 0.15, [(21.4, 26.65), (20.85, 26.5), (20.6, 26.4)]),
    ("ENC_CSN", "B.Cu", 0.2,
     [(20.6, 26.4), (20.4, 26.0), (20.4, 22.2), (21.6, 21.3)]),
    # VDD (pin 11, left edge) stub to the B.Cu +3V3 spine entry via.
    ("+3V3", "F.Cu", 0.15,
     [(21.4, 28.65), (21.1, 28.65), (20.75, 28.9), (20.75, 29.75)]),
    # C1 (+3V3 end, pad 2) stub to the spine via beside it.
    ("+3V3", "F.Cu", 0.15, [(20.65, 24.9), (21.0, 25.6)]),
    # +3V3 pigtail land stub up into C2's pad-2 in-pad via.
    ("+3V3", "F.Cu", 0.15, [(25.4, 22.6), (25.5, 23.4), (25.55, 23.87)]),
    # ERROR (pin 15, bottom edge) stub to its via, and the pigtail-end stub.
    ("ENC_ERROR", "F.Cu", 0.15, [(23.25, 29.8375), (23.25, 30.35), (23.95, 30.85)]),
    ("ENC_ERROR", "F.Cu", 0.15, [(26.35, 22.7), (26.35, 23.35)]),
    # VSS pad 14 tie to a GND via (avoids a starved 1-spoke thermal).
    ("GND", "F.Cu", 0.15, [(22.75, 29.8375), (22.75, 31.0)]),
    # B.Cu runs (B.Cu has no pads, so it is the uncongested layer).
    ("+3V3", "B.Cu", 0.2,
     [(25.55, 23.87), (21.35, 23.87), (21.0, 24.2), (21.0, 25.6), (21.2, 26.0),
      (21.2, 29.2), (20.75, 29.75)]),
    ("ENC_ERROR", "B.Cu", 0.2,
     [(23.95, 30.85), (26.25, 29.1), (26.25, 23.6), (26.35, 23.35)]),
]

# (net, (x, y)) — all vias are 0.6 mm pad / 0.3 mm drill.
VIAS = [
    ("+3V3", (20.75, 29.75)),    # VDD entry from the B.Cu spine
    ("+3V3", (21.0, 25.6)),      # C1 decoupler tap on the spine
    ("+3V3", (25.55, 23.87)),    # in-pad via in C2 pad 2 (spine start)
    ("ENC_CSN", (20.6, 26.4)),   # pin-7 stub down to B.Cu
    ("ENC_CSN", (21.6, 21.3)),   # in-pad via in the P1 CSN land
    ("ENC_ERROR", (23.95, 30.85)),
    ("ENC_ERROR", (26.35, 23.35)),
    ("GND", (20.65, 21.3)),      # in-pad tie inside the P1 GND land
    ("GND", (21.6, 24.55)),      # left F.Cu pour-pocket stitch (beside C1)
    ("GND", (22.75, 31.0)),      # VSS pad-14 tie
    ("GND", (23.5, 33.3)),       # bottom-centre pour stitch
]

# Board outline: rounded rectangle X0..X1 / Y0..Y1, corner radius R.
X0, Y0, X1, Y1, R = 20.0, 20.0, 27.0, 34.0, 1.0


def u():
    """Fresh UUID string for board items."""
    return str(uuid.uuid4())


def fmt(v):
    """Trim trailing zeros so coordinates stay tidy in the file."""
    return f"{v:.6f}".rstrip("0").rstrip(".")


def outline_records():
    """Rounded-rect Edge.Cuts: 4 straight edges + 4 quarter-arc corners."""
    k = 0.29289321881  # 1 - cos(45 deg): arc mid-point inset factor
    lines = [
        ((X0 + R, Y0), (X1 - R, Y0)),
        ((X1, Y0 + R), (X1, Y1 - R)),
        ((X1 - R, Y1), (X0 + R, Y1)),
        ((X0, Y1 - R), (X0, Y0 + R)),
    ]
    arcs = [
        # (start, mid, end) — counter-clockwise in canvas terms
        ((X1 - R, Y0), (X1 - R * k, Y0 + R * k), (X1, Y0 + R)),
        ((X1, Y1 - R), (X1 - R * k, Y1 - R * k), (X1 - R, Y1)),
        ((X0 + R, Y1), (X0 + R * k, Y1 - R * k), (X0, Y1 - R)),
        ((X0, Y0 + R), (X0 + R * k, Y0 + R * k), (X0 + R, Y0)),
    ]
    out = []
    for (sx, sy), (ex, ey) in lines:
        out.append(
            f"\t(gr_line\n\t\t(start {fmt(sx)} {fmt(sy)})\n\t\t(end {fmt(ex)} {fmt(ey)})\n"
            f'\t\t(stroke\n\t\t\t(width 0.1)\n\t\t\t(type solid)\n\t\t)\n'
            f'\t\t(layer "Edge.Cuts")\n\t\t(uuid "{u()}")\n\t)'
        )
    for (sx, sy), (mx, my), (ex, ey) in arcs:
        out.append(
            f"\t(gr_arc\n\t\t(start {fmt(sx)} {fmt(sy)})\n\t\t(mid {fmt(mx)} {fmt(my)})\n"
            f"\t\t(end {fmt(ex)} {fmt(ey)})\n"
            f'\t\t(stroke\n\t\t\t(width 0.1)\n\t\t\t(type solid)\n\t\t)\n'
            f'\t\t(layer "Edge.Cuts")\n\t\t(uuid "{u()}")\n\t)'
        )
    return out


def track_records():
    """Segments + vias with their net codes."""
    out = []
    for net, layer, width, pts in TRACKS:
        for (sx, sy), (ex, ey) in zip(pts, pts[1:]):
            out.append(
                f"\t(segment\n\t\t(start {fmt(sx)} {fmt(sy)})\n\t\t(end {fmt(ex)} {fmt(ey)})\n"
                f'\t\t(width {width})\n\t\t(layer "{layer}")\n'
                f'\t\t(net {CODE[net]})\n\t\t(uuid "{u()}")\n\t)'
            )
    for net, (x, y) in VIAS:
        out.append(
            f"\t(via\n\t\t(at {fmt(x)} {fmt(y)})\n\t\t(size 0.6)\n\t\t(drill 0.3)\n"
            f'\t\t(layers "F.Cu" "B.Cu")\n\t\t(net {CODE[net]})\n\t\t(uuid "{u()}")\n\t)'
        )
    return out


def zone_records():
    """Full-board GND pours on F.Cu and B.Cu (thermal-relief pad connect)."""
    out = []
    for layer in ("F.Cu", "B.Cu"):
        pts = f"(xy {X0} {Y0}) (xy {X1} {Y0}) (xy {X1} {Y1}) (xy {X0} {Y1})"
        out.append(
            f'\t(zone\n\t\t(net {CODE["GND"]})\n\t\t(net_name "GND")\n'
            f'\t\t(layer "{layer}")\n\t\t(uuid "{u()}")\n'
            f"\t\t(hatch edge 0.5)\n"
            f"\t\t(connect_pads\n\t\t\t(clearance 0.15)\n\t\t)\n"
            f"\t\t(min_thickness 0.15)\n\t\t(filled_areas_thickness no)\n"
            f"\t\t(fill yes\n\t\t\t(thermal_gap 0.3)\n\t\t\t(thermal_bridge_width 0.4)\n\t\t)\n"
            f"\t\t(polygon\n\t\t\t(pts\n\t\t\t\t{pts}\n\t\t\t)\n\t\t)\n\t)"
        )
    return out


def text_records():
    """Board name on the (component-free) back silk, mirrored so it reads
    correctly when viewed from the back."""
    return [
        '\t(gr_text "ENC-NAC-1 S"\n'
        "\t\t(at 23.9 27.6 0)\n"
        '\t\t(layer "B.SilkS")\n'
        f'\t\t(uuid "{u()}")\n'
        "\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 0.5 0.5)\n\t\t\t\t(thickness 0.1)\n\t\t\t)\n"
        "\t\t\t(justify mirror)\n\t\t)\n\t)"
    ]


def base_board_text():
    """The complete text-authored board minus footprints (added by pcbnew)."""
    nets = "\n".join([f'\t(net 0 "")'] + [f'\t(net {CODE[n]} "{n}")' for n in NETS])
    body = "\n".join(
        outline_records() + track_records() + zone_records() + text_records()
    )
    return f"""(kicad_pcb
\t(version 20241229)
\t(generator "pcbnew")
\t(generator_version "9.0")
\t(general
\t\t(thickness 0.8)
\t\t(legacy_teardrops no)
\t)
\t(paper "A4")
\t(title_block
\t\t(title "ENC-NACELLE-1 / SKIPPER-TILT-ENC-PCB")
\t\t(date "2026-07-21")
\t\t(rev "S")
\t\t(comment 1 "Serenity UAV — nacelle tilt-angle encoder (AKM AK7455, off-axis)")
\t\t(comment 2 "CC BY 4.0 — creativecommons.org/licenses/by/4.0")
\t\t(comment 3 "7 x 14 mm 2-layer 0.8 mm FR4; GND pours both sides; ERC/DRC per ENC-NACELLE-1.md")
\t\t(comment 4 "PCB drafted by Claude Fable 5 (Anthropic) via gen_enc_nacelle_pcb.py")
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
    """Export the schematic netlist so pad nets always match the schematic."""
    subprocess.run(
        ["kicad-cli", "sch", "export", "netlist", "-o", str(NETLIST), str(SCH)],
        check=True,
        capture_output=True,
    )


def parse_padnet():
    """(ref, pad) -> net name, from the exported KiCad netlist."""
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
    """pcbnew phase: load + place every footprint (no pad access, no Remove)."""
    import pcbnew

    board = pcbnew.LoadBoard(str(BOARD))
    for name in NETS:
        board.Add(pcbnew.NETINFO_ITEM(board, name))
    for ref, (lib, fpname, (x, y), rot) in PLACE.items():
        fp = pcbnew.FootprintLoad(lib, fpname)
        if fp is None:
            raise RuntimeError(f"cannot load {lib}:{fpname}")
        fp.SetReference(ref)
        fp.SetValue(VALUES[ref])
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
        board.Add(fp)
        if rot:
            fp.SetOrientationDegrees(rot)
    pcbnew.SaveBoard(str(BOARD), board)
    print(f"  placed {len(board.GetFootprints())} footprints")


def inject_pad_nets(padnet):
    """Text post-pass: net table + per-pad nets + parity-friendly lib IDs.

    SaveBoard prunes zero-pad nets, so the net table is re-injected here, and
    the footprint ids are re-qualified with their library nickname (Load-by-
    path drops it) so `kicad-cli pcb drc --schematic-parity` can match.
    """
    nick = {
        "U1": "Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.6x2.6mm",
        "C1": "Capacitor_SMD:C_0402_1005Metric",
        "C2": "Capacitor_SMD:C_0402_1005Metric",
        "P1": "Serenity-Custom:Pigtail_7W_DirectSolder",
        "MH1": "Serenity-Custom:MountingHole_2.2mm_M2_SelfTap_Compact",
        "MH2": "Serenity-Custom:MountingHole_2.2mm_M2_SelfTap_Compact",
    }
    src = BOARD.read_text()

    # Re-insert the net declaration block before the first footprint.
    decl = "\n".join(
        [f'\t(net 0 "")'] + [f'\t(net {CODE[n]} "{n}")' for n in NETS]
    )
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
        if ref in nick:
            block = re.sub(
                r'\(footprint "[^"]*"', f'(footprint "{nick[ref]}"', block, count=1
            )
        # The board has no free silk area for reference designators (7 x 14 mm,
        # dense top side) — move them to F.Fab so they stay on the fab drawing
        # without silk-over-pad / silk-off-board DRC noise.
        pr = block.find('(property "Reference"')
        if pr != -1:
            pv = block.find("(property", pr + 1)
            head = block[:pr]
            mid = block[pr: pv if pv != -1 else len(block)]
            tail = block[pv:] if pv != -1 else ""
            mid = mid.replace('(layer "F.SilkS")', '(layer "F.Fab")')
            block = head + mid + tail
        assign = {p: n for (r, p), n in padnet.items() if r == ref}

        def rewrite_pad(padtxt):
            num = re.match(r'\(pad "([^"]*)"', padtxt).group(1)
            net = assign.get(num)
            padtxt = re.sub(r'\s*\(net \d+ "[^"]*"\)', "", padtxt)
            if net is None or net not in CODE:
                return padtxt
            netexpr = f'\n\t\t\t(net {CODE[net]} "{net}")'
            lm = re.search(r'\(layers[^)]*\)', padtxt)
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
    """pcbnew phase 2: fill the GND pours and save."""
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
    print(f"  base board written ({len(TRACKS)} track runs, {len(VIAS)} vias)")
    place_footprints()
    inject_pad_nets(padnet)
    fill_zones()
    return 0


if __name__ == "__main__":
    sys.exit(main())
