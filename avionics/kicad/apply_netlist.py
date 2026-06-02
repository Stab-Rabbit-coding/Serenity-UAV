#!/usr/bin/env python3
"""Apply KiCad netlist (.net) to PCB file, assigning nets to footprint pads."""

import sys
import pcbnew

def parse_netlist(net_path):
    """Return dict: {(ref, pin): netname} from KiCad S-expression netlist."""
    import re
    with open(net_path, 'r') as f:
        content = f.read()

    pad_to_net = {}
    # Split into net blocks: everything from one (net ... to the next
    net_blocks = re.split(r'\n    \(net ', content)
    for block in net_blocks[1:]:  # skip header
        name_m = re.search(r'\(name "([^"]+)"\)', block)
        if not name_m:
            continue
        netname = name_m.group(1)
        for node_m in re.finditer(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', block):
            ref, pin = node_m.group(1), node_m.group(2)
            pad_to_net[(ref, pin)] = netname
    return pad_to_net

def apply_netlist(pcb_path, net_path, out_path=None):
    if out_path is None:
        out_path = pcb_path

    pad_to_net = parse_netlist(net_path)
    print(f"Parsed {len(pad_to_net)} pad-net assignments from {net_path}")

    board = pcbnew.LoadBoard(pcb_path)

    # Build lookup: netname -> NETINFO_ITEM (create if missing)
    def get_or_create_net(name):
        ni = board.FindNet(name)
        if ni is None:
            ni = pcbnew.NETINFO_ITEM(board, name)
            board.Add(ni)
        return ni

    # Pre-create all nets from the netlist
    all_netnames = set(pad_to_net.values())
    for name in all_netnames:
        get_or_create_net(name)
    # Refresh after additions
    pcbnew.Refresh()

    assigned = 0
    missed_fp = set()
    missed_pad = []

    footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}

    for (ref, pin), netname in pad_to_net.items():
        fp = footprints.get(ref)
        if fp is None:
            missed_fp.add(ref)
            continue
        pad = None
        for p in fp.Pads():
            if p.GetNumber() == pin:
                pad = p
                break
        if pad is None:
            missed_pad.append((ref, pin, netname))
            continue
        ni = board.FindNet(netname)
        pad.SetNet(ni)
        assigned += 1

    print(f"Assigned: {assigned}")
    if missed_fp:
        print(f"Missing footprints ({len(missed_fp)}): {sorted(missed_fp)}")
    if missed_pad:
        print(f"Missing pads ({len(missed_pad)}): {missed_pad[:20]}")

    board.Save(out_path)
    print(f"Saved: {out_path}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: apply_netlist.py <board.kicad_pcb> <board.net> [output.kicad_pcb]")
        sys.exit(1)
    apply_netlist(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
