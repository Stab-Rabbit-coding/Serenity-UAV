#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mod_emma_pcb.py — Apply the schematic-first reconciliation transform to
                  Emma.kicad_pcb so the board matches Emma.kicad_sch.
========================================================================
Mirrors exactly the topology transform authored into Emma.kicad_sch by
gen_emma_sch.py:

  1. DROP J1 ("CAPE-B IF", JST-GH-6P).  Its host-UART role moves onto the PB2
     rails, so the two modem UART nets are MERGED into the existing rail nets:
        UART_TX -> UART_RCRS_RX   (modem TX  = host RX,  PB2-P1 pin 15)
        UART_RX -> UART_RCRS_TX   (modem RX  = host TX,  PB2-P1 pin 16)
  2. Repurpose two PB2-P2 payload pads (presence-gated by a cape-detect DT
     overlay — a firmware concern, documented, no copper change beyond the net):
        PB2-P2 pad 1 (SERVO7 ball) -> PTT_N
        PB2-P2 pad 2 (SERVO6 ball) -> RSSI_DCD
  3. Add the RSSI carrier-detect sub-circuit (analog RSSI_ANA -> 1-bit
     RSSI_DCD) to match the schematic: RSSI_CMP comparator + RSSI_RH/RSSI_RL
     threshold divider + RSSI_CBY bypass.

PROVISIONAL / PENDING (flagged, — not fabrication-ready):
  * RSSI_CMP part number + physical SOT-23-5 pinout are NOT yet vetted against a
    datasheet.  Pad->net here is by FUNCTION and matches the schematic symbol
    (pad 1=RSSI_ANA/IN+, 2=+3V3/V+, 3=RSSI_REF/IN-, 4=GND/V-, 5=RSSI_DCD/OUT);
    the real comparator's pin order MUST be confirmed and a REFERENCES.md entry
    added before layout is final (cf. the Class 3B laser discipline).
  * The 4 new footprints are placed at PROVISIONAL coordinates in the strip
    vacated by J1.  Final placement + routing of the new parts, and re-routing of
    the merged UART / PTT_N / RSSI nets, are MANUAL steps to be confirmed by the
    user (project rule: refer footprint positioning to the user).

Author : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  (Griffing Technology LLC)
AI-assist: Claude Opus 4.8 (Anthropic) — transform authoring, 2026-07-04.
License: CC BY 4.0
"""

import pcbnew

PCB_FILE = "Emma.kicad_pcb"
FPLIB = "/usr/share/kicad/footprints"

NET_MERGE = {"UART_TX": "UART_RCRS_RX", "UART_RX": "UART_RCRS_TX"}
PB2P2_REASSIGN = {"1": "PTT_N", "2": "RSSI_DCD"}  # SERVO7->PTT_N, SERVO6->RSSI_DCD


def mm(v):
    return pcbnew.FromMM(v)


def get_or_add_net(board, name):
    n = board.FindNet(name)
    if n is None:
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
    return n


def load_fp(board, lib, mod, ref, val, x, y, rot=0):
    fp = pcbnew.FootprintLoad(f"{FPLIB}/{lib}.pretty", mod)
    if fp is None:
        raise RuntimeError(f"cannot load {lib}:{mod}")
    fp.SetReference(ref)
    fp.SetValue(val)
    fp.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y)))
    if rot:
        fp.SetOrientation(pcbnew.EDA_ANGLE(rot, pcbnew.DEGREES_T))
    board.Add(fp)
    return fp


def assign(board, fp, pad_map):
    for pad in fp.Pads():
        nn = pad_map.get(pad.GetNumber())
        if nn:
            pad.SetNet(get_or_add_net(board, nn))


def main():
    board = pcbnew.LoadBoard(PCB_FILE)

    # capture the footprints we need up front — iterating GetFootprints() again
    # after board.Remove() calls can return raw SWIG handles.
    fp_by_ref = {fp.GetReference(): fp for fp in board.GetFootprints()}

    # ensure the two new nets exist
    for nn in ("RSSI_DCD", "RSSI_REF"):
        get_or_add_net(board, nn)

    # --- 1. merge modem UART nets into the PB2 rail nets -------------------
    merged = {}
    for old, new in NET_MERGE.items():
        tgt = get_or_add_net(board, new)
        merged[old] = (new, tgt)
    # reassign pads on all footprints
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            nm = pad.GetNetname()
            if nm in merged:
                pad.SetNet(merged[nm][1])
    # reassign tracks / vias
    for tr in board.GetTracks():
        nm = tr.GetNetname()
        if nm in merged:
            tr.SetNet(merged[nm][1])
    # reassign copper zones
    for zi in range(board.GetAreaCount()):
        z = board.GetArea(zi)
        if z.GetNetname() in merged:
            z.SetNet(merged[z.GetNetname()][1])

    # --- 2. reassign PB2-P2 payload pads (BEFORE any board.Remove, which
    #        invalidates every previously-fetched footprint handle) ---------
    pb2 = fp_by_ref.get("PB2-P2")
    if pb2 is not None:
        for pad in pb2.Pads():
            nn = PB2P2_REASSIGN.get(pad.GetNumber())
            if nn:
                old = pad.GetNetname()
                pad.SetNet(get_or_add_net(board, nn))
                print(f"PB2-P2 pad {pad.GetNumber()}: {old} -> {nn}")

    # --- 2b. give every net-less pad the KiCad-canonical
    #     "unconnected-(REF-PadN)" net that the schematic's no_connect flags
    #     generate, so `pcb drc --schematic-parity` sees identical net-name
    #     strings (otherwise each floating pad reports net_conflict "Pad missing
    #     net given by schematic").  Must run before any board.Remove().
    nc = 0
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if not ref:
            continue
        for pad in fp.Pads():
            num = pad.GetNumber()
            if num and pad.GetNetname() == "":
                pad.SetNet(get_or_add_net(board, f"unconnected-({ref}-Pad{num})"))
                nc += 1
    print(f"assigned unconnected-() nets to {nc} net-less pads")

    # --- 3. add RSSI carrier-detect sub-circuit (PROVISIONAL placement) ----
    # Load/add/assign the new footprints BEFORE any board.Remove(): a Remove()
    # invalidates the SWIG IO-plugin state that FootprintLoad relies on.
    # Placed in the strip vacated by J1 (left edge).  Final placement TBD.
    j1 = fp_by_ref.get("CAPE-B IF")
    jx, jy = (
        (pcbnew.ToMM(j1.GetPosition().x), pcbnew.ToMM(j1.GetPosition().y))
        if j1 is not None
        else (102.0, 117.5)
    )
    # The board is fully packed (55x35 mm), so any in-cluster provisional
    # placement shorts existing copper.  Park the 4 new parts in a HOLDING AREA
    # just off the right board edge (x > 155 mm); the user drags them into final
    # position (project rule: refer footprint positioning to the user).  Off-board
    # they create only unconnected ratsnest items (expected), not shorts.
    hx, hy = 161.0, 108.0
    cmp_ = load_fp(
        board,
        "Package_TO_SOT_SMD",
        "SOT-23-5",
        "RSSI_CMP",
        "LMV331 RSSI Carrier-Detect (part/pinout TBD)",
        hx,
        hy,
    )
    assign(
        board,
        cmp_,
        {"1": "RSSI_ANA", "2": "+3V3", "3": "RSSI_REF", "4": "GND", "5": "RSSI_DCD"},
    )
    rh = load_fp(
        board,
        "Resistor_SMD",
        "R_0402_1005Metric",
        "RSSI_RH",
        "100k RSSI DCD Threshold Upper",
        hx,
        hy + 4.0,
    )
    assign(board, rh, {"1": "+3V3", "2": "RSSI_REF"})
    rl = load_fp(
        board,
        "Resistor_SMD",
        "R_0402_1005Metric",
        "RSSI_RL",
        "100k RSSI DCD Threshold Lower",
        hx,
        hy + 6.0,
    )
    assign(board, rl, {"1": "RSSI_REF", "2": "GND"})
    cby = load_fp(
        board,
        "Capacitor_SMD",
        "C_0402_1005Metric",
        "RSSI_CBY",
        "100nF RSSI_CMP VCC Bypass",
        hx,
        hy + 8.0,
    )
    assign(board, cby, {"1": "+3V3", "2": "GND"})

    # --- 4. remove J1 (CAPE-B IF) + its now-dangling stub copper (LAST) ----
    j1_pads = []
    if j1 is not None:
        for pad in j1.Pads():
            p = pad.GetPosition()
            j1_pads.append((p.x, p.y))
        board.Remove(j1)
        print(f"removed J1 (CAPE-B IF) at ({jx:.1f}, {jy:.1f})")

    # delete track/via segments that terminated on a removed J1 pad (now
    # dangling stubs in the vacated strip).  Surviving nets (UART_RCRS_*,
    # PTT_N, RSSI_ANA, +3V3, GND) keep their other routing; only the J1-facing
    # stub is dropped, to be re-routed to the PB2 rail manually.
    TOL = pcbnew.FromMM(0.4)

    def near_j1(pt):
        return any(
            abs(pt.x - px) <= TOL and abs(pt.y - py) <= TOL for px, py in j1_pads
        )

    dropped = 0
    for tr in list(board.GetTracks()):
        if isinstance(tr, pcbnew.PCB_VIA):
            if near_j1(tr.GetPosition()):
                board.Remove(tr)
                dropped += 1
        elif near_j1(tr.GetStart()) or near_j1(tr.GetEnd()):
            board.Remove(tr)
            dropped += 1
    print(f"dropped {dropped} dangling J1-stub track/via segments")

    board.BuildListOfNets()
    pcbnew.SaveBoard(PCB_FILE, board)
    print("saved", PCB_FILE)


if __name__ == "__main__":
    main()
