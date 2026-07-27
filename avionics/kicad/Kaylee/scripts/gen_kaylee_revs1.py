#!/usr/bin/env python3
"""Kaylee Rev S1 schematic conversion: 6 V servo BEC -> 5 V servo BEC.

1. Section E replaced: TPS54540 6 V BEC (U_BEC_6V, FB_6V, L3, C_BEC_SV_IN,
   R_FB6_*, C_BEC_SV_OUT, J_6V, J_SHLD_6V and the 6V_SERVO/SW6V/BOOT6V/...
   nets) is deleted; a TPS54620 5 V servo BEC (U_BEC_SERVO_5V, FB_SERVO,
   L4, R_FBSV_*, C_BEC_SV_*, J_SERVO_5V, J_SHLD_SV; rail net ``5V_SERVO``)
   is generated from the Section D pattern, INCLUDING the boot / soft-start
   / compensation passives the original generator never drew.
   DS3218MG budget: 2 x 500 mA stall = 1.0 A peak << TPS54620 6 A.
2. Section D completion: the same BOOT/SS/COMP support passives are added
   for U_BEC_5V_1 / U_BEC_5V_2 (their BOOT5Vx/SS5Vx/COMP5Vx nets dangled).
3. Section D topology fix: L1/L2 were drawn from the filtered INPUT to the
   SW node, leaving the buck output floating.  They now connect
   SW5Vx -> BEC5Vx_RAW as a buck output inductor must.
4. One-off label repairs: CM2_OUT_N return tied to PGND at the fuse;
   PDB_SDA_RAW / PDB_SCL_RAW / PDB_SCL Section-G labels snapped onto their
   series-resistor pins.

Component values marked "verify per TPS54620 DS" are first-pass pending
per-datasheet verification (same convention as the Jayne carrier rails).

Authored by Claude Fable 5 (Anthropic), 2026-07-21.  License: CC BY 4.0.
"""

import re
import sys
import uuid
from pathlib import Path

SCH = Path(__file__).resolve().parents[1] / "kicads" / "Kaylee.kicad_sch"


def u():
    return str(uuid.uuid4())


def glabel(net, x, y, rot):
    return (
        f'  (global_label "{net}" (shape bidirectional) (at {x:.2f} {y:.2f} {rot})\n'
        f"    (effects (font (size 1.016 1.016)))\n"
        f'    (uuid "{u()}")\n'
        f'    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {x:.2f} {y:.2f} 0)\n'
        f"      (effects (font (size 1.016 1.016)) (hide yes))))\n"
    )


def sym(lib_id, ref, value, x, y, rot=0, hidden_ref=False):
    ref_hide = " (hide yes)" if hidden_ref else ""
    return (
        f'  (symbol (lib_id "{lib_id}") (at {x:.2f} {y:.2f} {rot})\n'
        f"    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)\n"
        f'    (uuid "{u()}")\n'
        f'    (property "Reference" "{ref}" (at {x:.2f} {y - 3.81:.2f} 0)\n'
        f"      (effects (font (size 1.27 1.27)){ref_hide}))\n"
        f'    (property "Value" "{value}" (at {x:.2f} {y + 3.81:.2f} 0)\n'
        f"      (effects (font (size 1.27 1.27))))\n"
        f'    (property "Footprint" "" (at 0 0 0)\n'
        f"      (effects (font (size 1.27 1.27)) (hide yes)))\n"
        f'    (property "Datasheet" "" (at 0 0 0)\n'
        f"      (effects (font (size 1.27 1.27)) (hide yes)))\n"
        f"  )\n"
    )


def pgnd(x_pin, y_pin, rot=180):
    """PGND power symbol placed so its pin (lib (0,-1.27)) lands on (x,y)."""
    if rot == 180:
        ix, iy = x_pin, y_pin + 1.27
    elif rot == 0:
        ix, iy = x_pin, y_pin - 1.27
    elif rot == 270:
        ix, iy = x_pin + 1.27, y_pin
    else:  # 90
        ix, iy = x_pin - 1.27, y_pin
    return sym("PGND", "#PWR", "PGND", ix, iy, rot, hidden_ref=True)


def vdis(x_pin, y_pin):
    """VDIS power symbol, pin at (x,y), rot 0 (pin renders 1.27 below)."""
    return sym("VDIS", "#PWR", "VDIS", x_pin, y_pin - 1.27, 0, hidden_ref=True)


def passive(lib, ref, value, x, y, lnet, rnet):
    """Horizontal 2-pin part at (x,y): left net label, right net label."""
    return (
        sym(lib, ref, value, x, y)
        + glabel(lnet, x - 2.54, y, 180)
        + glabel(rnet, x + 2.54, y, 0)
    )


def passive_pg(lib, ref, value, x, y, lnet):
    """Horizontal 2-pin part: left net label, right pin to PGND."""
    return (
        sym(lib, ref, value, x, y)
        + glabel(lnet, x - 2.54, y, 180)
        + pgnd(x + 2.54, y, 180)
    )


def section_e():
    out = []
    out.append(
        '  (text "=== Section E: 5V Servo BEC (Rev S1 - 6V BEC retired) ===" (at 248.00 120.00 0)\n'
        "    (effects (font (size 1.27 1.27)))\n"
        f'    (uuid "{u()}"))\n'
    )
    # Input filter: VDIS -> FB_SERVO -> FBSV_OUT, bulk cap to PGND.
    out.append(sym("FB_Generic", "FB_SERVO", "Wurth 742792612 600R@100MHz 2A", 250, 130))
    out.append(vdis(247.46, 130.00))
    out.append(glabel("FBSV_OUT", 252.54, 130.00, 0))
    out.append(passive_pg("C_Generic", "C_BEC_SV_IN", "100uF/50V electrolytic", 250, 140, "FBSV_OUT"))
    # Buck output inductor: SW_SV -> 5V_SERVO (correct buck branch).
    out.append(passive("L_Generic", "L4", "Wurth 744314100 10uH >=6A Isat", 265, 130, "SW_SV", "5V_SERVO"))
    # The regulator.  Pin attach points for instance (280,135):
    # VIN 142.62 / EN 140.08 / SS 137.54 / COMP 135.00 / FB 132.46 /
    # GND 129.92 (all x 267.30); BOOT 140.08 / SW 135.00 / PGND 129.92
    # (all x 292.70).  EN ties to VIN (always-on), matching Section D.
    out.append(sym("TPS54620RGYT", "U_BEC_SERVO_5V", "TPS54620RGYT 6A/28V sync buck 5.0V servo rail", 280, 135))
    out.append(glabel("FBSV_OUT", 267.30, 142.62, 180))
    out.append(glabel("FBSV_OUT", 267.30, 140.08, 180))
    out.append(glabel("SS_SV", 267.30, 137.54, 180))
    out.append(glabel("COMP_SV", 267.30, 135.00, 180))
    out.append(glabel("FBSV_FBK", 267.30, 132.46, 180))
    out.append(pgnd(267.30, 129.92, 180))
    out.append(glabel("BOOT_SV", 292.70, 140.08, 0))
    out.append(glabel("SW_SV", 292.70, 135.00, 0))
    out.append(pgnd(292.70, 129.92, 180))
    # Support passives (first-pass values; verify per TPS54620 datasheet).
    out.append(passive("C_Generic", "C_BOOT_SV", "100nF X7R (BOOT-SW)", 280, 150, "BOOT_SV", "SW_SV"))
    out.append(passive_pg("C_Generic", "C_SS_SV", "10nF soft-start (verify per TPS54620 DS)", 280, 157, "SS_SV"))
    out.append(passive("R_Generic", "R_COMP_SV", "R comp (verify per TPS54620 DS)", 265, 150, "COMP_SV", "COMPRC_SV"))
    out.append(passive_pg("C_Generic", "C_COMP_SV", "C comp (verify per TPS54620 DS)", 265, 157, "COMPRC_SV"))
    out.append(passive_pg("C_Generic", "C_COMP2_SV", "C comp2 hi-f pole (verify per TPS54620 DS)", 265, 164, "COMP_SV"))
    # Feedback divider (5.0 V servo rail — direct, no diode-OR).
    out.append(passive("R_Generic", "R_FBSV_1", "R for Vout=5.0V (top)", 300, 150, "5V_SERVO", "FBSV_FBK"))
    out.append(passive_pg("R_Generic", "R_FBSV_2", "R for Vout=5.0V (bot)", 300, 157, "FBSV_FBK"))
    out.append(passive_pg("C_Generic", "C_BEC_SV_OUT", "220uF 10V electrolytic + 100nF X7R", 300, 140, "5V_SERVO"))
    # Output connector + shield pad.
    out.append(sym("Nano_Fit_4P", "J_SERVO_5V", "Molex Nano-Fit 4P 2.5mm SERVO-5V bus", 315, 135))
    out.append(glabel("5V_SERVO", 317.54, 131.19, 0))
    out.append(glabel("5V_SERVO", 317.54, 133.73, 0))
    out.append(pgnd(317.54, 136.27, 180))
    out.append(pgnd(317.54, 138.81, 180))
    out.append(sym("M3_ChassisPad", "J_SHLD_SV", "PGND via-pad for SERVO-5V cable shield", 315, 150))
    out.append(pgnd(312.46, 150.00, 0))
    return "".join(out)


def section_d_support():
    out = []
    for n, ybase in (("1", 0.0), ("2", 45.0)):
        out.append(passive("C_Generic", f"C_BOOT{n}", "100nF X7R (BOOT-SW)", 285, 55 + ybase, f"BOOT5V{n}", f"SW5V{n}"))
        out.append(passive_pg("C_Generic", f"C_SS{n}", "10nF soft-start (verify per TPS54620 DS)", 285, 62 + ybase, f"SS5V{n}"))
        out.append(passive("R_Generic", f"R_COMP{n}", "R comp (verify per TPS54620 DS)", 293, 55 + ybase, f"COMP5V{n}", f"COMPRC5V{n}"))
        out.append(passive_pg("C_Generic", f"C_COMPA{n}", "C comp (verify per TPS54620 DS)", 293, 62 + ybase, f"COMPRC5V{n}"))
        out.append(passive_pg("C_Generic", f"C_COMPB{n}", "C comp2 hi-f pole (verify per TPS54620 DS)", 301, 55 + ybase, f"COMP5V{n}"))
    return "".join(out)


def main():
    src = SCH.read_text()

    # --- 1. Replace Section E ------------------------------------------------
    start = src.find('  (text "=== Section E:')
    end = src.find('  (text "=== Section F:')
    if start == -1 or end == -1:
        print("Section E/F markers not found — aborting")
        return 1
    src = src[:start] + section_e() + section_d_support() + src[end:]

    # --- 2. Section D L1/L2 branch fix --------------------------------------
    fixes = [
        ('(global_label "FB5V1_OUT" (shape bidirectional) (at 262.46 30.00 180)',
         '(global_label "SW5V1" (shape bidirectional) (at 262.46 30.00 180)'),
        ('(global_label "SW5V1" (shape bidirectional) (at 267.54 30.00 0)',
         '(global_label "BEC5V1_RAW" (shape bidirectional) (at 267.54 30.00 0)'),
        ('(global_label "FB5V2_OUT" (shape bidirectional) (at 262.46 75.00 180)',
         '(global_label "SW5V2" (shape bidirectional) (at 262.46 75.00 180)'),
        ('(global_label "SW5V2" (shape bidirectional) (at 267.54 75.00 0)',
         '(global_label "BEC5V2_RAW" (shape bidirectional) (at 267.54 75.00 0)'),
        # --- 4. one-off label / power repairs -------------------------------
        # CM2_OUT_N return bonds to PGND at the fuse input (move the floating
        # PGND@270 so its pin (instance + (-1.27, 0)) lands on the label).
        ('(symbol (lib_id "PGND") (at 90.46 38.89 270)',
         '(symbol (lib_id "PGND") (at 91.73 37.62 270)'),
        ('(global_label "PDB_SDA_RAW" (shape bidirectional) (at 547.38 35.00 0)',
         '(global_label "PDB_SDA_RAW" (shape bidirectional) (at 547.46 35.00 0)'),
        ('(global_label "PDB_SCL_RAW" (shape bidirectional) (at 548.00 45.00 0)',
         '(global_label "PDB_SCL_RAW" (shape bidirectional) (at 547.46 45.00 0)'),
        ('(global_label "PDB_SCL" (shape bidirectional) (at 552.00 45.00 0)',
         '(global_label "PDB_SCL" (shape bidirectional) (at 552.54 45.00 0)'),
    ]
    missed = 0
    for old, new in fixes:
        if old in src:
            src = src.replace(old, new, 1)
        else:
            missed += 1
            print(f"  WARN: pattern not found: {old[:70]}")

    SCH.write_text(src)
    n6v = len(re.findall(r"6V_SERVO|U_BEC_6V|SW6V|BOOT6V|FB6V", src))
    print(f"Section E rewritten; label fixes missed: {missed}; residual 6V refs: {n6v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
