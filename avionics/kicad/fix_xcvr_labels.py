#!/usr/bin/env python3
"""
fix_xcvr_labels.py

Two-pass label cleanup for XCVR-49MHZ-2.kicad_pcb:

  Pass 1 — Reference field (F.SilkS, printed on board):
    Update text to short functional descriptions so the PCB is self-
    documenting without a BOM.  Standardise text size to 0.65×0.65 mm,
    thickness 0.10 mm.

  Pass 2 — Value field (F.Fab, not printed):
    Move ALL value-field text off the board boundary to the nearest edge
    (left / right / top / bottom).  Labels on the same edge are sorted
    by their component position along that edge and spread with
    MIN_SPACING = 2.2 mm so no two value labels overlap.

Author : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
"""

import pcbnew

PCB_FILE = (
    "/home/steve/Documents/Vocation/Employers/Griffing.tech/"
    "designs/Serenity-UAV/avionics/kicad/XCVR-49MHZ-2.kicad_pcb"
)

BOARD_X1, BOARD_Y1 = 100.0, 100.0  # mm
BOARD_X2, BOARD_Y2 = 155.0, 135.0  # mm
VAL_MARGIN = 3.5  # mm outside the board edge for value labels
MIN_SPACING = 2.2  # mm minimum centre-to-centre on an edge
VAL_SIZE = 0.80  # mm  (value text height)
VAL_THICK = 0.12  # mm
REF_SIZE = 0.65  # mm  (silk reference text height)
REF_THICK = 0.10  # mm


# ---------------------------------------------------------------------------
# Short silk labels keyed on ORIGINAL reference designator.
# Values are printed on F.SilkS — each describes the component function so
# the PCB is readable without a BOM.
# ---------------------------------------------------------------------------
SILK = {
    # Connectors
    "J1": "CAPE-B IF",
    "J2": "ANT SMA",
    # EMI stage — original stub components
    "CMC_CAN": "ANT CMC",
    "D_TVS": "ANT TVS",
    "FB1": "+5V Bead",
    "C_X2Y": "GND X2Y",
    # EMI stage — added by -2 design
    "TVS6": "UART TVS",
    "CM5": "UART CMC",
    "FB_TX": "TX Bead",
    "FB_RX": "RX Bead",
    "FB_PT": "PTT Bead",
    "TVS_SMA": "SMA ESD",
    "FB2": "+5V Bead2",
    # Signal ICs
    "U1": "49M DDS",
    "X1": "TCXO 25M",
    "U2A": "TX DAC",
    "U2B": "RX Demod",
    "U3A": "PA Drvr",
    "U3B": "PA 100mW",
    "U4": "LNA",
    "U5": "T/R Sw",
    "U6": "LDO 3V3",
    # Low-pass filter
    "FL1_L1": "L1 100n",
    "FL1_C1": "C1 120p",
    "FL1_L2": "L2 180n",
    "FL1_C2": "C2 180p",
    "FL1_L3": "L3 180n",
    "FL1_C3": "C3 120p",
    # Supply bypass cascade
    "C21": "+5V 100u",
    "C22": "+5V 100n",
    "C23": "+3V 100u",
    "C24": "+3V 10u",
    "C25": "+3V 100n",
    "C26": "+3V 10n",
    "C27": "PGND 10n",
    # IC decoupling
    "C_U1A": "U1 ByA",
    "C_U1B": "U1 ByB",
    "C_U2A": "DAC By",
    "C_U2B": "CMP By",
    "C_U4": "LNA By",
    "C_U5": "SW By",
    "C_U6": "LDO By",
    "C_X1": "OSC By",
    "C_PA": "PA By",
    # PA bias / signal conditioning
    "R_B1": "PA Rb1",
    "C_B1": "PA Cb1",
    "R_C1": "PA Rc1",
    "R_B2": "PA Rb2",
    "C_B2": "PA Cb2",
    "R_E2": "PA Re",
    "C_U3B": "PA By2",
    "C_AF": "AFSK Cp",
    # RX demodulator filter / comparator threshold
    "R_RX1": "1.2k R",
    "C_RX1": "1.2k C",
    "R_RX2": "2.2k R",
    "C_RX2": "2.2k C",
    "R_TH1": "Th Hi",
    "R_TH2": "Th Lo",
    # RSSI scaling
    "R_RS1": "RSSI Hi",
    "R_RS2": "RSSI Lo",
}


def mm(v):
    return pcbnew.FromMM(v)


def to_mm(v):
    return float(v) / 1_000_000.0


def nearest_edge(x, y):
    """Return which board edge is nearest to the component at (x, y)."""
    dl = x - BOARD_X1
    dr = BOARD_X2 - x
    dt = y - BOARD_Y1
    db = BOARD_Y2 - y
    m = min(dl, dr, dt, db)
    if m == dl:
        return "left"
    if m == dr:
        return "right"
    if m == dt:
        return "top"
    return "bottom"


def spread(sorted_positions, spacing):
    """
    Given a sorted list of floats (component positions along an edge),
    return a list of label positions where each is at least `spacing`
    apart from the previous one, growing in the positive direction.
    """
    result = []
    last = None
    for pos in sorted_positions:
        if last is None or pos - last >= spacing:
            result.append(pos)
        else:
            result.append(last + spacing)
        last = result[-1]
    return result


def main():
    print(f"Loading {PCB_FILE}")
    board = pcbnew.LoadBoard(PCB_FILE)

    # -----------------------------------------------------------------------
    # Single pass: collect all footprint data, update Reference silk text,
    # and build Value-field edge groups — all from the same iterator so
    # SWIG proxy identity is consistent within the loop.
    # -----------------------------------------------------------------------
    ref_updated = 0
    groups = {"left": [], "right": [], "top": [], "bottom": []}

    for fp in board.GetFootprints():
        oref = fp.GetReference()  # original ref-des, read before any mutation

        # -- Reference (silk) update --
        if oref in SILK:
            rf = fp.GetFieldByName("Reference")
            if rf is not None:
                rf.SetText(SILK[oref])
                rf.SetLayer(pcbnew.F_SilkS)
                rf.SetVisible(True)
                rf.SetTextSize(pcbnew.VECTOR2I(mm(REF_SIZE), mm(REF_SIZE)))
                rf.SetTextThickness(mm(REF_THICK))
                ref_updated += 1

        # -- Value field: collect for off-board placement --
        if not oref:
            continue  # mounting holes have empty ref

        pos = fp.GetPosition()
        fx = to_mm(pos.x)
        fy = to_mm(pos.y)

        edge = nearest_edge(fx, fy)
        along = fy if edge in ("left", "right") else fx

        vf = fp.GetFieldByName("Value")
        if vf is None:
            continue

        groups[edge].append((along, fx, fy, vf, oref))

    print(f"  Reference (silk) labels updated: {ref_updated}")

    # For each edge: sort by along-edge position, spread, assign positions
    # -----------------------------------------------------------------------
    # Pass 2: spread and position collected Value fields
    # -----------------------------------------------------------------------
    val_moved = 0
    for edge, items in groups.items():
        if not items:
            continue

        items_sorted = sorted(items, key=lambda x: x[0])
        along_positions = [i[0] for i in items_sorted]
        new_positions = spread(along_positions, MIN_SPACING)

        for new_pos, (_, fx, fy, vf, oref) in zip(new_positions, items_sorted):
            if edge == "top":
                lx, ly = new_pos, BOARD_Y1 - VAL_MARGIN
            elif edge == "bottom":
                lx, ly = new_pos, BOARD_Y2 + VAL_MARGIN
            elif edge == "left":
                lx, ly = BOARD_X1 - VAL_MARGIN, new_pos
            else:  # right
                lx, ly = BOARD_X2 + VAL_MARGIN, new_pos

            vf.SetPosition(pcbnew.VECTOR2I(mm(lx), mm(ly)))
            vf.SetTextSize(pcbnew.VECTOR2I(mm(VAL_SIZE), mm(VAL_SIZE)))
            vf.SetTextThickness(mm(VAL_THICK))
            vf.SetLayer(pcbnew.F_Fab)
            vf.SetVisible(True)

            # Rotate 90° for left / right edges so text runs along the edge
            if edge in ("left", "right"):
                vf.SetTextAngle(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T))
            else:
                vf.SetTextAngle(pcbnew.EDA_ANGLE(0, pcbnew.DEGREES_T))

            val_moved += 1

    print(f"  Value labels repositioned: {val_moved}")
    print(
        f"    top={len(groups['top'])}  bottom={len(groups['bottom'])}"
        f"  left={len(groups['left'])}  right={len(groups['right'])}"
    )

    # -----------------------------------------------------------------------
    # Verify: count how many value labels are still inside the board
    # -----------------------------------------------------------------------
    still_in = 0
    for edge, items in groups.items():
        for _, fx, fy, vf, oref in items:
            vp = vf.GetPosition()
            vx, vy = to_mm(vp.x), to_mm(vp.y)
            if (BOARD_X1 <= vx <= BOARD_X2) and (BOARD_Y1 <= vy <= BOARD_Y2):
                still_in += 1
                print(f"    WARN: {oref} value still in board at ({vx:.2f},{vy:.2f})")

    if still_in == 0:
        print("  All value labels are off-board. ✓")

    board.Save(PCB_FILE)
    print("Saved.")


if __name__ == "__main__":
    main()
