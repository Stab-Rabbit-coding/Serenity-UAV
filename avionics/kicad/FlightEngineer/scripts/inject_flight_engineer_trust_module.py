#!/usr/bin/env python3
"""inject_flight_engineer_trust_module.py -- add the Section H trust module (MCU + TPM
+ isolated CAN-FD + isolated RS-485) into the EXISTING, working FlightEngineer.kicad_sch
via text injection, instead of a full gen_flight_engineer.py regeneration.

WHY injection, not regeneration: running gen_flight_engineer.py fresh from its own
current source (even with NONE of the Section H edits applied) does not
reproduce the checked-in FlightEngineer.kicad_sch -- it lands at 247 ERC errors
(all pre-existing, all in Sections A-G, none related to this change) where
the checked-in file has 0. That means gen_flight_engineer.py has drifted out of sync
with the working schematic at some point before this task (most likely the
schematic was hand-tuned in the KiCad GUI after its last real generation).
Regenerating from gen_flight_engineer.py's gen_sch() would silently reintroduce that
pre-existing drift. This script instead surgically inserts the new lib
symbols and Section H component/net content into the CURRENT working file,
leaving everything else byte-identical. gen_flight_engineer.py itself still carries
the Section H generator functions (for whenever the drift bug above gets
fixed and a real regeneration becomes safe again) -- this script reuses the
exact same helper functions, just targets the working file directly.

A distinct UUID prefix ("beef0000-...") is used for every object this script
adds, so injected UUIDs cannot collide with the existing file's "a3..."
sequence.

Usage: python3 inject_flight_engineer_trust_module.py
Output: overwrites avionics/kicad/FlightEngineer/kicads/FlightEngineer.kicad_sch in place.

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI-assist: Claude Fable 5 (Anthropic), 2026-07-26
License: CC BY 4.0
"""

# ---------------------------------------------------------------------------
# SUPERSEDED PART WARNING (2026-08-03)
#
# This generator still emits the MSPM0G3507 and/or SLB9670VQ2.0.  Both were
# retargeted on 2026-08-03:
#     MSPM0G3507  ->  MSPM0G3519-Q1 (M0G3519QRGZRQ1, RGZ-48)   on Jayne
#                 ->  MSPM0G3518-Q1 (M0G3518QRHBRQ1, RHB-32)   on the gateway and Kaylee
#     SLB9670VQ2.0 -> SLB 9672AU2.0 (PG-UQFN-32-1,-2)          on all three
# See REFERENCES.md REF-SENSOR-013 / REF-SEC-002 and TODO.md 1.2d.
#
# Do NOT re-run this script against the committed schematic: it has drifted
# from the as-placed design and regenerating would revert the retarget.  Apply
# changes with avionics/kicad/retarget_mspm0g351x_slb9672.py instead.
# ---------------------------------------------------------------------------

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
KICADS = HERE.parent / "kicads"
SCH = KICADS / "FlightEngineer.kicad_sch"

sys.path.insert(0, str(HERE))
import gen_flight_engineer as gk  # noqa: E402

# Distinct UUID stream so nothing collides with the existing file's "a3..." run.
_uid_i = [0]


def _next_uid():
    _uid_i[0] += 1
    val = _uid_i[0]
    h = f"{val:032x}"
    return f"beef0000-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


gk._next_uid = _next_uid  # monkey-patch: gk.sym_inst/glabel/pwr_sym/nc all call this


def build_lib_additions():
    lib = [
        gk.lib_symbol_conn_3p("Conn_JST_GH_03P"),
        gk.lib_symbol_2pin_h("SJ_Generic"),
        gk.lib_symbol_buck_sot23_6_trust("TLV62569_DBV_H"),
        gk.lib_symbol_generic_ic_trust(
            "GW_ISOW1412", gk.ADM_FOOTPRINT_T, gk.ADM_DATASHEET_T,
            left=gk.ADM_L_T, right=gk.ADM_R_T, size=gk.ADM_SIZE_T,
        ),
        gk.lib_symbol_pwr_flag_trust(),
    ]
    real_trust = {k: gk.parse_real_symbol_trust(v[0]) for k, v in gk.REAL_SYMS_TRUST.items()}
    for k in ("MCU", "TPM", "ISO"):
        lib.append(real_trust[k][0])
    return lib, real_trust


def two_pin_trust(lib_id, ref, value, cx, cy, net1, net2):
    """R_Generic/C_Generic/L_Generic/SJ_Generic (gk.lib_symbol_2pin_h) all
    share the SAME pin geometry: pin 1 at local x=-2.54, pin 2 at x=+2.54
    (Flight Engineer's OWN lib_symbol_2pin_h -- NOT the same offset as this project's
    other generators' 2pin_h helper, which uses 3.81; verified directly
    against gen_flight_engineer.py's own _pin_def calls). Computed, not hand-typed,
    after two rounds of hand-arithmetic offset bugs orphaned every 2-pin
    passive on the board."""
    return [
        gk.sym_inst(lib_id, ref, value, cx, cy),
        gk.glabel(net1, cx - 2.54, cy, rot=180),
        gk.glabel(net2, cx + 2.54, cy, rot=0),
    ]


def conn_glabel_trust(net, cx, cy, n, idx0):
    """Matches gk.lib_symbol_conn_3p/4p/7p's own pin geometry exactly: pin
    local x=+2.54 (rectangle sits at x in [-3.81, 0], pins stick out right),
    local y = -half + idx0*2.54, half=(n-1)*1.27. Sheet y = cy - local_y
    (KiCad negates local Y for a rot=0 instance)."""
    half = (n - 1) * 1.27
    local_y = -half + idx0 * 2.54
    return gk.glabel(net, cx + 2.54, cy - local_y, rot=0)


def build_section_h_body(real_trust):
    parts = []
    parts.append(
        gk.text_note("=== Section H: Trust Module (MCU+TPM+isolated CAN-FD+RS-485) ===", 700, 10)
    )
    parts.append(gk.sym_inst("TLV62569_DBV_H", "U_REG_3V3_H", "TLV62569DBVR -> +3V3", 710, 30))
    BL = [("EN", "1", "input"), ("GND", "2", "power_in"), ("VIN", "4", "power_in")]
    BR = [("SW", "3", "output"), ("FB", "5", "input"), ("PG", "6", "output")]
    BSZ = (7.62, 5.08)
    parts.append(gk.glabel_pin_bynum_trust("+5V", 710, 30, BL, BR, "1", BSZ))
    parts.append(gk.glabel_pin_bynum_trust("PGND", 710, 30, BL, BR, "2", BSZ))
    parts.append(gk.glabel_pin_bynum_trust("+5V", 710, 30, BL, BR, "4", BSZ))
    parts.append(gk.glabel_pin_bynum_trust("U_REG_H_SW", 710, 30, BL, BR, "3", BSZ))
    parts.append(gk.glabel_pin_bynum_trust("U_REG_H_FB", 710, 30, BL, BR, "5", BSZ))
    parts.append(gk.no_connect_pin_bynum_trust(710, 30, BL, BR, "6", BSZ))
    parts.extend(two_pin_trust("L_Generic", "L_H1", "2.2uH", 725, 30, "U_REG_H_SW", "+3V3"))
    parts.extend(two_pin_trust("R_Generic", "R_H_FBT", "10k", 725, 38, "+3V3", "U_REG_H_FB"))
    parts.extend(two_pin_trust("R_Generic", "R_H_FBB", "20k", 725, 44, "U_REG_H_FB", "PGND"))
    parts.extend(two_pin_trust("C_Generic", "C_H_IN", "10uF", 700, 40, "+5V", "PGND"))
    parts.extend(two_pin_trust("C_Generic", "C_H_OUT", "22uF", 740, 30, "+3V3", "PGND"))
    parts.extend(gk.pwr_flag_trust("+3V3", 750, 30))

    mcu_pins = real_trust["MCU"][1]
    # Pinmux VERIFIED against the real MSPM0G3507 datasheet (SLASEX6C
    # Table 6-2 "Pin Attributes"), read directly on request (2026-07-26) --
    # replaces an earlier draft that put CANFD_TX/RX on PA6/PA7 (pads 12/13)
    # and RS485_TX/RX on PB3/PA8 (pads 15/16), none of which offer CAN or
    # UART functions per the datasheet (PA12/PA13 are this device's ONLY
    # CAN pin pair; UART2 on PB15/PB16 was free and correct).
    #   CAN:   PA12 pad27 CAN_TX AF5 / PA13 pad28 CAN_RX AF6
    #   SPI0:  CS=PA2 pad8 / SCK=PA6 pad12 / MOSI=PA5 pad11 / MISO=PA4 pad10 (all AF3, TPM bus)
    #   I2C0:  SDA=PA0 pad1 AF3 / SCL=PA1 pad2 AF3 (existing PDB_SDA/PDB_SCL bus)
    #   UART2: TX=PB15 pad25 AF2 / RX=PB16 pad26 AF2 (RS-485)
    mcu_nm = {
        "1": "PDB_SDA", "2": "PDB_SCL", "4": "MCU_NRST", "6": "+3V3", "7": "PGND",
        "8": "TPM_SPI_CS", "9": "TPM_PIRQ", "10": "TPM_SPI_MISO",
        "11": "TPM_SPI_MOSI", "12": "TPM_SPI_SCK", "13": "TPM_RESET_N",
        "14": "RS485_DE", "15": "RS485_FLT_N", "16": "CANFD_FLT_N",
        "25": "RS485_TX", "26": "RS485_RX", "27": "CANFD_TX", "28": "CANFD_RX",
        "34": "MCU_SWDIO", "35": "MCU_SWCLK", "48": "MCU_VCORE", "49": "PGND",
    }
    parts.extend(gk.place_real_trust("MCU", "U_MCU", "TI MSPM0G3507", {1: (710, 90)}, mcu_nm, mcu_pins))
    parts.extend(two_pin_trust("R_Generic", "R_H_NRST", "10k", 690, 90, "+3V3", "MCU_NRST"))
    parts.extend(two_pin_trust("C_Generic", "C_H_VCORE", "1uF", 690, 96, "MCU_VCORE", "PGND"))
    parts.append(gk.sym_inst("Conn_JST_GH_04P", "J_SWD_H", "SWD: DIO/CLK/NRST/GND", 750, 90))
    parts.append(conn_glabel_trust("MCU_SWDIO", 750, 90, 4, 0))
    parts.append(conn_glabel_trust("MCU_SWCLK", 750, 90, 4, 1))
    parts.append(conn_glabel_trust("MCU_NRST", 750, 90, 4, 2))
    parts.append(conn_glabel_trust("PGND", 750, 90, 4, 3))

    tpm_pins = real_trust["TPM"][1]
    tpm_nm = {
        "1": "+3V3", "2": "PGND", "8": "+3V3", "9": "PGND", "14": "+3V3",
        "16": "PGND", "17": "TPM_RESET_N", "18": "TPM_PIRQ", "19": "TPM_SPI_SCK",
        "20": "TPM_SPI_CS", "21": "TPM_SPI_MOSI", "22": "+3V3", "23": "PGND",
        "24": "TPM_SPI_MISO", "32": "PGND",
    }
    parts.extend(gk.place_real_trust("TPM", "U_TPM", "Infineon SLB9672", {1: (710, 130)}, tpm_nm, tpm_pins))
    parts.extend(two_pin_trust("C_Generic", "C_H_TPM1", "100nF", 690, 125, "+3V3", "PGND"))
    parts.extend(two_pin_trust("R_Generic", "R_H_TPM_RST", "10k", 690, 131, "+3V3", "TPM_RESET_N"))

    iso_pins = real_trust["ISO"][1]
    iso_nm = {
        "1": "+3V3", "3": "CANFD_TX", "4": "PGND", "5": "CANFD_RX", "6": "PGND",
        "8": "CANFD_FLT_N", "9": "+3V3", "10": "PGND", "11": "ISO_GND_CAN",
        "12": "ISO_5V_CAN", "13": "ISO_5V_CAN", "15": "ISO_GND_CAN",
        "16": "ISO_GND_CAN", "17": "ISO_GND_CAN", "18": "CAN_L", "19": "CAN_H",
        "20": "ISO_5V_CAN",
    }
    parts.extend(gk.place_real_trust("ISO", "U_ISOCAN", "TI ISOW1044BDFMR", {1: (710, 170)}, iso_nm, iso_pins))
    parts.extend(two_pin_trust("C_Generic", "C_H_ISO1", "100nF", 690, 165, "+3V3", "PGND"))
    parts.extend(two_pin_trust("C_Generic", "C_H_ISO2", "1uF", 690, 171, "ISO_5V_CAN", "ISO_GND_CAN"))
    parts.extend(gk.pwr_flag_trust("ISO_GND_CAN", 750, 171))
    parts.append(gk.sym_inst("Conn_JST_GH_03P", "J_CAN_IN_H", "CAN-FD trunk IN (CANH/CANL/GND)", 790, 165))
    parts.append(conn_glabel_trust("CAN_H", 790, 165, 3, 0))
    parts.append(conn_glabel_trust("CAN_L", 790, 165, 3, 1))
    parts.append(conn_glabel_trust("ISO_GND_CAN", 790, 165, 3, 2))
    parts.append(gk.sym_inst("Conn_JST_GH_03P", "J_CAN_OUT_H", "CAN-FD trunk OUT (CANH/CANL/GND)", 820, 165))
    parts.append(conn_glabel_trust("CAN_H", 820, 165, 3, 0))
    parts.append(conn_glabel_trust("CAN_L", 820, 165, 3, 1))
    parts.append(conn_glabel_trust("ISO_GND_CAN", 820, 165, 3, 2))
    parts.extend(two_pin_trust("R_Generic", "R_H_CANTERM", "120R", 790, 185, "CAN_H", "CANTERM_MID_H"))
    parts.append(gk.sym_inst("SJ_Generic", "SJ_H_CAN", "open by default", 805, 185,
                              footprint="Jumper:SolderJumper-2_P1.3mm_Open_Pad1.0x1.5mm"))
    parts.append(gk.glabel("CANTERM_MID_H", 805 - 2.54, 185, rot=180))
    parts.append(gk.glabel("CAN_L", 805 + 2.54, 185, rot=0))

    adm_cx, adm_cy = 710, 210
    adm_nm = {
        "1": "+3V3", "2": "RS485_TX", "3": "RS485_DE", "4": "RS485_RX",
        "5": "RS485_DE", "6": "PGND", "8": "RS485_FLT_N", "9": "+3V3",
        "10": "PGND", "11": "ISO_GND_485", "12": "ISO_3V3_485",
        "13": "ISO_GND_485", "15": "ISO_GND_485", "16": "ISO_3V3_485",
        "17": "RS485_A", "18": "RS485_B", "19": "RS485_B", "20": "RS485_A",
    }
    parts.append(gk.sym_inst("GW_ISOW1412", "U_RS485", "TI ISOW1412", adm_cx, adm_cy,
                              footprint=gk.ADM_FOOTPRINT_T, datasheet=gk.ADM_DATASHEET_T))
    for pname, pnum, ptype in gk.ADM_L_T + gk.ADM_R_T:
        net = adm_nm.get(pnum)
        if net is None:
            parts.append(gk.no_connect_pin_bynum_trust(adm_cx, adm_cy, gk.ADM_L_T, gk.ADM_R_T, pnum, gk.ADM_SIZE_T))
        else:
            parts.append(gk.glabel_pin_bynum_trust(net, adm_cx, adm_cy, gk.ADM_L_T, gk.ADM_R_T, pnum, gk.ADM_SIZE_T))
    parts.extend(two_pin_trust("C_Generic", "C_H_ADM1", "100nF", 690, 205, "+3V3", "PGND"))
    parts.extend(two_pin_trust("C_Generic", "C_H_ADM2", "100nF", 690, 211, "ISO_3V3_485", "ISO_GND_485"))
    parts.extend(gk.pwr_flag_trust("ISO_GND_485", 750, 211))
    # No external isolated DC-DC needed -- ISOW1412 has its own integrated
    # isolated DC-DC (VISOOUT/VISOIN, pins 12/16), same as ISOW1044 above.
    parts.append(gk.sym_inst("Conn_JST_GH_03P", "J_RS485_IN_H", "RS-485 trunk IN (A/B/GND)", 790, 205))
    parts.append(conn_glabel_trust("RS485_A", 790, 205, 3, 0))
    parts.append(conn_glabel_trust("RS485_B", 790, 205, 3, 1))
    parts.append(conn_glabel_trust("ISO_GND_485", 790, 205, 3, 2))
    parts.append(gk.sym_inst("Conn_JST_GH_03P", "J_RS485_OUT_H", "RS-485 trunk OUT (A/B/GND)", 820, 205))
    parts.append(conn_glabel_trust("RS485_A", 820, 205, 3, 0))
    parts.append(conn_glabel_trust("RS485_B", 820, 205, 3, 1))
    parts.append(conn_glabel_trust("ISO_GND_485", 820, 205, 3, 2))
    parts.extend(two_pin_trust("R_Generic", "R_H_485TERM", "120R", 790, 225, "RS485_A", "TERM485_MID_H"))
    parts.append(gk.sym_inst("SJ_Generic", "SJ_H_485", "open by default", 805, 225,
                              footprint="Jumper:SolderJumper-2_P1.3mm_Open_Pad1.0x1.5mm"))
    parts.append(gk.glabel("TERM485_MID_H", 805 - 2.54, 225, rot=180))
    parts.append(gk.glabel("RS485_B", 805 + 2.54, 225, rot=0))
    return parts


def inject():
    src = SCH.read_text()
    lib_additions, real_trust = build_lib_additions()
    body_additions = build_section_h_body(real_trust)

    # Insert new lib symbols right before the FIRST top-level ")" that closes
    # the "(lib_symbols" block (the block's own closing paren, at 2-space
    # indent, immediately preceding the first "  (symbol (lib_id " placed
    # instance -- i.e. right before the first placed-instance line).
    first_instance = src.index('\n  (symbol (lib_id "')
    # Walk backward from there to the lib_symbols block's closing "  )" line.
    close_idx = src.rindex("\n  )\n", 0, first_instance) + 1  # start of "  )\n"
    lib_text = "\n".join(lib_additions) + "\n"
    src = src[:close_idx] + lib_text + src[close_idx:]

    # Append Section H body right before the file's final closing ")".
    assert src.rstrip().endswith(")")
    last_paren = src.rstrip().rindex(")")
    body_text = "\n".join(body_additions) + "\n"
    src = src[:last_paren] + body_text + src[last_paren:]

    SCH.write_text(src)
    print(f"  Injected {len(lib_additions)} lib symbols + {len(body_additions)} body items into {SCH}")


if __name__ == "__main__":
    inject()
