#!/usr/bin/env python3
"""FlightEngineer Rev S1 close-out fixes (run after gen_kaylee_revs1.py).

1. Delete the six stray PGND power symbols whose pins land on the shunt
   Kelvin S+ points (5x ESC branches + RS_MAIN).  All four pins of every
   CSS2H shunt already carry their proper labels; these strays would short
   the 25 V high-side Kelvin sense line straight to ground.
2. Fix the Section-E VDIS symbol position: unlike PGND (pin at (0,-1.27)),
   the VDIS/+5V symbols carry their pin at (0,+1.27), so the instance
   belongs BELOW the attach point at rotation 0.
3. Rewire the D_I2C PRTR5V0U2X: IO1 = PDB_SDA, IO2 = PDB_SCL, D1A/D2A
   no-connect.  The vestigial PDB_*_RAW labels (one dangling on IO1, one on
   D1A, two floating in empty space at ~(550, 45)) are removed.
4. Add a PWR_FLAG symbol + instances on the externally/FET-driven rails
   (VBAT, PGND, VDIS, +5V, FB5V1/2_OUT, FBSV_OUT) to clear the
   power_pin_not_driven false positives.
5. Give U_IS_MAIN's VBUS pin its missing source: R_VSNS 0R Kelvin tap from
   VDIS onto the existing VDIS_SENSE net.

Authored by Claude Fable 5 (Anthropic), 2026-07-21.  License: CC BY 4.0.
"""

import sys
import uuid
from pathlib import Path

SCH = Path(__file__).resolve().parents[1] / "kicads" / "FlightEngineer.kicad_sch"


def u():
    return str(uuid.uuid4())


def delete_symbol_block(src, header):
    """Remove one full symbol block starting with `header` (brace-balanced)."""
    j = src.find(header)
    if j == -1:
        print(f"  WARN: block not found: {header}")
        return src
    depth = 0
    for k in range(j, len(src)):
        if src[k] == "(":
            depth += 1
        elif src[k] == ")":
            depth -= 1
            if depth == 0:
                end = k + 1
                while end < len(src) and src[end] == "\n":
                    end += 1
                return src[:j] + src[j:end][:0] + src[end:]
    return src


def main():
    src = SCH.read_text()

    # --- 1. stray Kelvin-shorting PGNDs -------------------------------------
    for pos in (
        "(at 18.65 127.46 0)",
        "(at 63.65 127.46 0)",
        "(at 108.65 127.46 0)",
        "(at 153.65 127.46 0)",
        "(at 198.65 127.46 0)",
        "(at 143.65 27.46 0)",
    ):
        src = delete_symbol_block(src, f'  (symbol (lib_id "PGND") {pos}')

    # --- 2. Section-E VDIS pin offset ---------------------------------------
    src = src.replace(
        '(symbol (lib_id "VDIS") (at 247.46 128.73 0)',
        '(symbol (lib_id "VDIS") (at 247.46 131.27 0)',
        1,
    )

    # --- 3. D_I2C TVS rewire -------------------------------------------------
    src = src.replace(
        '(global_label "PDB_SDA_RAW" (shape bidirectional) (at 547.38 35.00 180)',
        '(global_label "PDB_SDA" (shape bidirectional) (at 547.38 35.00 180)',
        1,
    )
    # D1A stub label -> no-connect
    src = delete_symbol_block(
        src,
        '  (global_label "PDB_SCL_RAW" (shape bidirectional) (at 547.38 32.46 180)',
    )
    src = src.replace(
        '(global_label "PDB_SDA" (shape bidirectional) (at 562.62 32.46 0)',
        '(global_label "PDB_SCL" (shape bidirectional) (at 562.62 32.46 0)',
        1,
    )
    # the two labels floating in empty space near (550, 45)
    src = delete_symbol_block(
        src,
        '  (global_label "PDB_SCL_RAW" (shape bidirectional) (at 548.00 45.00 180)',
    )
    src = delete_symbol_block(
        src,
        '  (global_label "PDB_SCL" (shape bidirectional) (at 552.54 45.00 0)',
    )
    add = [f'  (no_connect (at 547.38 32.46)\n    (uuid "{u()}"))\n']

    # --- 4. PWR_FLAG def + instances ----------------------------------------
    if '(symbol "PWR_FLAG"' not in src:
        pwr_def = (
            '  (symbol "PWR_FLAG" (power) (pin_numbers hide) (pin_names (offset 0) hide) (in_bom no) (on_board no)\n'
            '    (property "Reference" "#FLG" (at 0 1.905 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
            '    (property "Value" "PWR_FLAG" (at 0 3.81 0) (effects (font (size 1.27 1.27))))\n'
            '    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
            '    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))\n'
            "    (symbol \"PWR_FLAG_0_0\"\n"
            "      (pin power_out line (at 0 0 90) (length 0)\n"
            '        (name "~" (effects (font (size 1.27 1.27))))\n'
            '        (number "1" (effects (font (size 1.27 1.27)))))\n'
            "    )\n"
            "    (symbol \"PWR_FLAG_0_1\"\n"
            "      (polyline\n"
            "        (pts (xy 0 0) (xy 0 1.016) (xy -1.016 1.524) (xy 0 2.032) (xy 1.016 1.524) (xy 0 1.016))\n"
            "        (stroke (width 0) (type default)) (fill (type none)))\n"
            "    )\n"
            "  )\n"
        )
        anchor = '  (symbol "PGND" (power)'
        j = src.find(anchor)
        src = src[:j] + pwr_def + src[j:]

    for x, y in (
        (17.46, 48.00),
        (22.54, 48.00),
        (22.46, 80.00),
        (14.84, 150.46),
        (267.30, 42.62),
        (267.30, 87.62),
        (267.30, 142.62),
    ):
        add.append(
            f'  (symbol (lib_id "PWR_FLAG") (at {x:.2f} {y:.2f} 0)\n'
            f"    (unit 1) (exclude_from_sim no) (in_bom no) (on_board yes) (dnp no)\n"
            f'    (uuid "{u()}")\n'
            f'    (property "Reference" "#FLG" (at {x:.2f} {y - 3.5:.2f} 0)\n'
            f"      (effects (font (size 1.27 1.27)) (hide yes)))\n"
            f'    (property "Value" "PWR_FLAG" (at {x:.2f} {y - 2.0:.2f} 0)\n'
            f"      (effects (font (size 1.27 1.27))))\n"
            f'    (pin "1" (uuid "{u()}")))\n'
        )

    # --- 5. VBUS Kelvin tap: VDIS -> R_VSNS -> VDIS_SENSE -------------------
    if "R_VSNS" not in src:
        add.append(
            f'  (symbol (lib_id "R_Generic") (at 183.00 12.00 0)\n'
            f"    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)\n"
            f'    (uuid "{u()}")\n'
            f'    (property "Reference" "R_VSNS" (at 183.00 8.19 0)\n'
            f"      (effects (font (size 1.27 1.27))))\n"
            f'    (property "Value" "0R Kelvin VBUS tap (VDIS)" (at 183.00 15.81 0)\n'
            f"      (effects (font (size 1.27 1.27))))\n"
            f'    (property "Footprint" "" (at 0 0 0)\n'
            f"      (effects (font (size 1.27 1.27)) (hide yes)))\n"
            f'    (property "Datasheet" "" (at 0 0 0)\n'
            f"      (effects (font (size 1.27 1.27)) (hide yes)))\n"
            f"  )\n"
        )
        add.append(
            f'  (symbol (lib_id "VDIS") (at 180.46 13.27 0)\n'
            f"    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)\n"
            f'    (uuid "{u()}")\n'
            f'    (property "Reference" "#PWR" (at 180.46 13.27 0)\n'
            f"      (effects (font (size 1.27 1.27)) (hide yes)))\n"
            f'    (property "Value" "VDIS" (at 180.46 10.73 0)\n'
            f"      (effects (font (size 1.27 1.27))))\n"
            f'    (property "Footprint" "" (at 0 0 0)\n'
            f"      (effects (font (size 1.27 1.27)) (hide yes)))\n"
            f'    (property "Datasheet" "" (at 0 0 0)\n'
            f"      (effects (font (size 1.27 1.27)) (hide yes)))\n"
            f'    (pin "1" (uuid "{u()}"))\n'
            f"  )\n"
        )
        add.append(
            f'  (global_label "VDIS_SENSE" (shape bidirectional) (at 185.54 12.00 0)\n'
            f"    (effects (font (size 1.016 1.016)))\n"
            f'    (uuid "{u()}")\n'
            f'    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at 185.54 12.00 0)\n'
            f"      (effects (font (size 1.016 1.016)) (hide yes))))\n"
        )

    # insert additions before the closing paren of the file
    tail = src.rstrip()
    assert tail.endswith(")")
    src = tail[:-1] + "".join(add) + ")\n"

    SCH.write_text(src)
    print("cleanup applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
