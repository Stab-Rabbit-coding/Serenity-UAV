#!/usr/bin/env python3
"""
gen_kaylee.py — Kaylee Power Distribution Board KiCad file generator

Outputs to avionics/kicad/:
    Kaylee.kicad_pro  (project + net classes)
    Kaylee.kicad_sch  (schematic, A1, v20240101)
    Kaylee.kicad_pcb  (90x65 mm 4-layer PCB outline + stackup)

Reference: avionics/kicad/Kaylee.md  Rev A  2026-06-07
Author: Steve Griffing PE(CSE) CISSP-ISSEP CPP  |  CC BY 4.0
Usage:  python3 gen_kaylee.py   (run from any dir)
"""

import json
import uuid
from pathlib import Path

# ---------------------------------------------------------------------------
# Deterministic UUID helpers
# ---------------------------------------------------------------------------
_NS = uuid.UUID("a3000000-0000-0000-0000-000000000000")
_cnt = [0]


def _uid(tag: str) -> str:
    return str(uuid.uuid5(_NS, f"Kaylee:{tag}"))


def _seq() -> str:
    _cnt[0] += 1
    return f"a3{_cnt[0]:014x}"[:8] + "-" + f"{_cnt[0]:016x}"[8:12] + "-" + \
           "0000-0000-" + f"{_cnt[0]:012x}"


# ---------------------------------------------------------------------------
# kicad_pro
# ---------------------------------------------------------------------------
def gen_pro() -> str:
    pro = {
        "board": {
            "design_settings": {
                "defaults": {
                    "apply_defaults_to_fp_fields": False,
                    "apply_defaults_to_fp_shapes": False,
                    "apply_defaults_to_fp_text": False,
                    "board_outline_line_width": 0.05,
                    "copper_line_width": 0.2,
                    "copper_text_italic": False,
                    "copper_text_size_h": 1.5,
                    "copper_text_size_v": 1.5,
                    "copper_text_thickness": 0.3,
                    "copper_text_upright": False,
                    "courtyard_line_width": 0.05,
                    "dimension_precision": 4,
                    "dimension_units": 3,
                    "dimensions": {
                        "arrow_length": 1270000,
                        "extension_offset": 500000,
                        "keep_text_aligned": True,
                        "suppress_zeroes": True,
                        "text_position": 0,
                        "units_format": 0
                    },
                    "fab_line_width": 0.1,
                    "fab_text_italic": False,
                    "fab_text_size_h": 1.0,
                    "fab_text_size_v": 1.0,
                    "fab_text_thickness": 0.15,
                    "fab_text_upright": False,
                    "other_line_width": 0.15,
                    "other_text_italic": False,
                    "other_text_size_h": 1.0,
                    "other_text_size_v": 1.0,
                    "other_text_thickness": 0.15,
                    "other_text_upright": False,
                    "pads": {"drill": 0.0, "height": 8.0, "width": 8.0},
                    "silk_line_width": 0.15,
                    "silk_text_italic": False,
                    "silk_text_size_h": 1.0,
                    "silk_text_size_v": 1.0,
                    "silk_text_thickness": 0.15,
                    "silk_text_upright": False,
                    "zones": {"min_clearance": 0.5}
                },
                "diff_pair_dimensions": [],
                "drc_exclusions": [],
                "meta": {"version": 2},
                "rule_severities": {
                    "annular_width": "error",
                    "clearance": "error",
                    "connection_width": "warning",
                    "copper_edge_clearance": "error",
                    "copper_sliver": "warning",
                    "courtyards_overlap": "error",
                    "creepage": "error",
                    "diff_pair_gap_out_of_range": "error",
                    "diff_pair_uncoupled_length_too_long": "error",
                    "drill_out_of_range": "error",
                    "duplicate_footprints": "warning",
                    "extra_footprint": "warning",
                    "footprint": "error",
                    "footprint_filters_mismatch": "ignore",
                    "footprint_symbol_mismatch": "warning",
                    "footprint_type_mismatch": "ignore",
                    "hole_clearance": "error",
                    "hole_to_hole": "warning",
                    "holes_co_located": "warning",
                    "invalid_outline": "error",
                    "isolated_copper": "warning",
                    "item_on_disabled_layer": "error",
                    "items_not_allowed": "error",
                    "length_out_of_range": "error",
                    "lib_footprint_issues": "warning",
                    "lib_footprint_mismatch": "warning",
                    "malformed_courtyard": "error",
                    "microvia_drill_out_of_range": "error",
                    "mirrored_text_on_front_layer": "warning",
                    "missing_courtyard": "ignore",
                    "missing_footprint": "warning",
                    "net_conflict": "warning",
                    "nonmirrored_text_on_back_layer": "warning",
                    "npth_inside_courtyard": "ignore",
                    "padstack": "warning",
                    "pth_inside_courtyard": "ignore",
                    "shorting_items": "error",
                    "silk_edge_clearance": "warning",
                    "silk_over_copper": "warning",
                    "silk_overlap": "warning",
                    "skew_out_of_range": "error",
                    "solder_mask_bridge": "error",
                    "starved_thermal": "error",
                    "text_height": "warning",
                    "text_on_edge_cuts": "error",
                    "text_thickness": "warning",
                    "through_hole_pad_without_hole": "error",
                    "too_many_vias": "error",
                    "track_angle": "error",
                    "track_dangling": "warning",
                    "track_segment_length": "error",
                    "track_width": "error",
                    "tracks_crossing": "error",
                    "unconnected_items": "error",
                    "unresolved_variable": "error",
                    "via_dangling": "warning",
                    "zones_intersect": "error"
                },
                "rules": {
                    "clearance": 0.15,
                    "max_error": 0.005,
                    "min_clearance": 0.0,
                    "min_connection": 0.0,
                    "min_copper_edge_clearance": 0.25,
                    "min_groove_width": 0.0,
                    "min_hole_clearance": 0.25,
                    "min_hole_to_hole": 0.25,
                    "min_microvia_diameter": 0.2,
                    "min_microvia_drill": 0.1,
                    "min_resolved_spokes": 2,
                    "min_silk_clearance": 0.0,
                    "min_text_height": 0.8,
                    "min_text_thickness": 0.08,
                    "min_through_hole_diameter": 0.3,
                    "min_track_width": 0.2,
                    "min_via_annular_width": 0.1,
                    "min_via_diameter": 0.4,
                    "solder_mask_clearance": 0.0,
                    "solder_mask_min_width": 0.0,
                    "solder_mask_to_copper_clearance": 0.0,
                    "use_height_for_length_calcs": True
                },
                "track_widths": [0.2, 0.3, 0.5, 1.0, 2.0, 6.0],
                "via_dimensions": [
                    {"diameter": 0.8, "drill": 0.4},
                    {"diameter": 1.0, "drill": 0.5},
                    {"diameter": 1.6, "drill": 0.8}
                ],
                "zones_allow_external_fillets": False,
                "zones_min_antigap_margin": 0.0
            },
            "ipc2581": {"dist": "", "distpn": "", "internal_id": "", "mfg": "", "mpn": ""},
            "layer_pairs": [],
            "layer_presets": [],
            "viewports": []
        },
        "boards": [],
        "cvpcb": {"equivalence_files": []},
        "erc": {"erc_exclusions": [], "meta": {"version": 0}, "pin_map": [], "rule_severities": []},
        "libraries": {"pinned_footprint_libs": [], "pinned_symbol_libs": []},
        "meta": {"filename": "Kaylee.kicad_pro", "version": 3},
        "net_settings": {
            "classes": [
                {
                    "bus_width": 12,
                    "clearance": 0.15,
                    "diff_pair_gap": 0.25,
                    "diff_pair_via_gap": 0.25,
                    "diff_pair_width": 0.15,
                    "line_style": 0,
                    "microvia_diameter": 0.3,
                    "microvia_drill": 0.1,
                    "name": "Default",
                    "pcb_color": "rgba(0, 0, 0, 0.000)",
                    "priority": 2147483647,
                    "schematic_color": "rgba(0, 0, 0, 0.000)",
                    "track_width": 0.3,
                    "via_diameter": 0.8,
                    "via_drill": 0.4,
                    "wire_width": 6
                },
                {
                    "clearance": 3.0,
                    "name": "VBAT",
                    "pcb_color": "rgba(0, 0, 0, 0.000)",
                    "priority": 0,
                    "schematic_color": "rgba(0, 0, 0, 0.000)",
                    "track_width": 6.0,
                    "via_diameter": 1.6,
                    "via_drill": 0.8
                },
                {
                    "clearance": 3.0,
                    "name": "PGND",
                    "pcb_color": "rgba(0, 0, 0, 0.000)",
                    "priority": 0,
                    "schematic_color": "rgba(0, 0, 0, 0.000)",
                    "track_width": 6.0,
                    "via_diameter": 1.6,
                    "via_drill": 0.8
                },
                {
                    "clearance": 0.2,
                    "name": "POWER_5V",
                    "pcb_color": "rgba(0, 0, 0, 0.000)",
                    "priority": 1,
                    "schematic_color": "rgba(0, 0, 0, 0.000)",
                    "track_width": 0.5,
                    "via_diameter": 0.8,
                    "via_drill": 0.4
                }
            ],
            "meta": {"version": 4},
            "net_colors": None,
            "netclass_assignments": None,
            "netclass_patterns": [
                {"netclass": "VBAT",     "pattern": "VBAT*"},
                {"netclass": "VBAT",     "pattern": "VDIS*"},
                {"netclass": "PGND",     "pattern": "PGND"},
                {"netclass": "PGND",     "pattern": "GND"},
                {"netclass": "POWER_5V", "pattern": "+5V*"},
                {"netclass": "POWER_5V", "pattern": "+6V*"},
                {"netclass": "POWER_5V", "pattern": "5V_AVIONICS"},
                {"netclass": "POWER_5V", "pattern": "6V_SERVO"}
            ]
        },
        "pcbnew": {
            "last_paths": {
                "gencad": "", "idf": "", "netlist": "", "plot": "",
                "pos_files": "", "specctra_dsn": "", "step": "", "svg": "", "vrml": ""
            },
            "page_layout_descr_file": ""
        },
        "schematic": {
            "annotate_start_num": 0,
            "bom_fmt_preset": "",
            "bom_fmt_settings": {
                "fields_ordered": [],
                "filter": "",
                "group_by": [],
                "sort_asc": True,
                "sort_field": "Reference"
            },
            "connection_grid_size": 50.0,
            "drawing": {
                "dashed_lines_dash_length_ratio": 12.0,
                "dashed_lines_gap_length_ratio": 3.0,
                "default_line_thickness": 6.0,
                "default_text_size": 50.0,
                "field_names": [],
                "intersheets_ref_own_page": False,
                "intersheets_ref_prefix": "",
                "intersheets_ref_short": False,
                "intersheets_ref_show": False,
                "intersheets_ref_suffix": "",
                "junction_size_choice": 3,
                "label_size_ratio": 0.25,
                "op_value_scale_factor": 1.0,
                "overbar_offset_ratio": 1.23,
                "pin_symbol_size": 25.0,
                "text_offset_ratio": 0.08
            },
            "legacy_lib_dir": "",
            "legacy_lib_list": [],
            "meta": {"version": 1},
            "net_format_name": "",
            "page_layout_descr_file": "",
            "plot_directory": "",
            "spice_current_sheet_as_root": False,
            "subpart_first_id": 65,
            "subpart_id_separator": 0
        },
        "sheets": [["a3000000-0000-0000-0000-000000000001", ""]],
        "text_variables": {}
    }
    return json.dumps(pro, indent=2)


# ---------------------------------------------------------------------------
# kicad_sch helpers
# ---------------------------------------------------------------------------

def _prop(name, val, x, y, rot=0, hide=False):
    h = ' (hide yes)' if hide else ''
    return (f'    (property "{name}" "{val}" (at {x:.2f} {y:.2f} {rot})'
            f'\n      (effects (font (size 1.27 1.27)){h}))')


def _pin_def(ptype, shape, px, py, ang, length, name, number):
    return (
        f'      (pin {ptype} {shape} (at {px:.2f} {py:.2f} {ang}) (length {length:.2f})\n'
        f'        (name "{name}" (effects (font (size 1.016 1.016))))\n'
        f'        (number "{number}" (effects (font (size 1.016 1.016)))))'
    )


def _rect(x1, y1, x2, y2):
    return (f'      (rectangle (start {x1:.2f} {y1:.2f}) (end {x2:.2f} {y2:.2f})\n'
            f'        (stroke (width 0.254) (type default)) (fill (type background)))')


def lib_symbol_2pin_h(name, in_bom="yes"):
    """Horizontal 2-pin component: pin1 left (0°), pin2 right (180°)."""
    return f"""  (symbol "{name}" (in_bom {in_bom}) (on_board yes)
    (property "Reference" "?" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{name}" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "{name}_0_1"
{_rect(-1.27, -0.635, 1.27, 0.635)})
    (symbol "{name}_1_1"
{_pin_def("passive", "line", -2.54, 0, 0, 1.27, "~", "1")}
{_pin_def("passive", "line",  2.54, 0, 180, 1.27, "~", "2")})
  )"""


def lib_symbol_fuse(name="Fuse_MAXI"):
    return f"""  (symbol "{name}" (in_bom yes) (on_board yes)
    (property "Reference" "F" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{name}" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "{name}_0_1"
      (circle (center 0 0) (radius 0.762)
        (stroke (width 0.254) (type default)) (fill (type none)))
      (polyline (pts (xy -1.27 0) (xy -0.762 0)) (stroke (width 0.254) (type default)) (fill (type none)))
      (polyline (pts (xy 0.762 0) (xy 1.27 0)) (stroke (width 0.254) (type default)) (fill (type none))))
    (symbol "{name}_1_1"
{_pin_def("passive", "line", -2.54, 0, 0, 1.27, "A", "1")}
{_pin_def("passive", "line",  2.54, 0, 180, 1.27, "K", "2")})
  )"""


def lib_symbol_tvs_bi(name="SMBJ33CA"):
    return f"""  (symbol "{name}" (in_bom yes) (on_board yes)
    (property "Reference" "D" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{name}" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Diode_SMD:D_SMB" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "{name}_0_1"
      (polyline (pts (xy -1.27 -1.27) (xy -1.27 1.27) (xy 1.27 0) (xy -1.27 -1.27))
        (stroke (width 0.254) (type default)) (fill (type none)))
      (polyline (pts (xy 1.27 -1.27) (xy 1.27 1.27))
        (stroke (width 0.254) (type default)) (fill (type none))))
    (symbol "{name}_1_1"
{_pin_def("passive", "line", -2.54, 0, 0, 1.27, "A", "1")}
{_pin_def("passive", "line",  2.54, 0, 180, 1.27, "K", "2")})
  )"""


def lib_symbol_schottky_dual(name="MBRD1045CT"):
    """Dual Schottky: A1(1), A2(2), K(3) common cathode."""
    return f"""  (symbol "{name}" (in_bom yes) (on_board yes)
    (property "Reference" "D" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{name}" (at 0 5.08 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_TO_SOT_SMD:TO-252-3_TabPin2" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "{name}_0_1"
{_rect(-3.81, -3.81, 3.81, 3.81)})
    (symbol "{name}_1_1"
{_pin_def("passive", "line", -6.35, -2.54, 0, 2.54, "A1", "1")}
{_pin_def("passive", "line", -6.35,  2.54, 0, 2.54, "A2", "2")}
{_pin_def("passive", "line",  6.35,  0.00, 180, 2.54, "K", "3")})
  )"""


def lib_symbol_nmos(name="AON6556"):
    """N-MOSFET: G(1), S(2), D(3)."""
    return f"""  (symbol "{name}" (in_bom yes) (on_board yes)
    (property "Reference" "Q" (at 0 -7.62 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{name}" (at 0 7.62 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_DFN_QFN:DFN-8-1EP_3x3mm_P0.65mm_EP1.65x2.38mm" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "{name}_0_1"
{_rect(-5.08, -5.08, 5.08, 5.08)})
    (symbol "{name}_1_1"
{_pin_def("input",    "line", -7.62, -2.54, 0, 2.54, "G", "1")}
{_pin_def("passive",  "line", -7.62,  2.54, 0, 2.54, "S", "2")}
{_pin_def("passive",  "line",  7.62,  0.00, 180, 2.54, "D", "3")})
  )"""


def lib_symbol_cmc4(name="CMC_7440640500"):
    """4-terminal common-mode choke: IN+(1), IN-(2), OUT+(3), OUT-(4)."""
    return f"""  (symbol "{name}" (in_bom yes) (on_board yes)
    (property "Reference" "CM" (at 0 -7.62 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{name}" (at 0 7.62 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Inductor_THT:L_Toroid_Vertical_D10.0mm_P5.0mm" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "{name}_0_1"
{_rect(-5.08, -5.08, 5.08, 5.08)})
    (symbol "{name}_1_1"
{_pin_def("passive", "line", -7.62, -2.54, 0, 2.54, "IN+", "1")}
{_pin_def("passive", "line", -7.62,  2.54, 0, 2.54, "IN-", "2")}
{_pin_def("passive", "line",  7.62, -2.54, 180, 2.54, "OUT+", "3")}
{_pin_def("passive", "line",  7.62,  2.54, 180, 2.54, "OUT-", "4")})
  )"""


def lib_symbol_shunt4t(name="CSS2H_2512K_1mOhm"):
    """4-terminal Kelvin shunt: F+(1), S+(2), S-(3), F-(4)."""
    return f"""  (symbol "{name}" (in_bom yes) (on_board yes)
    (property "Reference" "RS" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{name}" (at 0 5.08 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Resistor_SMD:R_2512_6332Metric" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "{name}_0_1"
{_rect(-3.81, -3.81, 3.81, 3.81)})
    (symbol "{name}_1_1"
{_pin_def("passive", "line", -6.35, -1.27, 0, 2.54, "F+", "1")}
{_pin_def("passive", "line", -6.35,  1.27, 0, 2.54, "S+", "2")}
{_pin_def("passive", "line",  6.35,  1.27, 180, 2.54, "S-", "3")}
{_pin_def("passive", "line",  6.35, -1.27, 180, 2.54, "F-", "4")})
  )"""


def lib_symbol_ina226():
    return """  (symbol "INA226AIDGSR" (in_bom yes) (on_board yes)
    (property "Reference" "U" (at 0 -7.62 0) (effects (font (size 1.27 1.27))))
    (property "Value" "INA226AIDGSR" (at 0 7.62 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_SO:VSSOP-10_3x3mm_P0.5mm" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.ti.com/lit/ds/symlink/ina226.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "INA226AIDGSR_0_1"
      (rectangle (start -7.62 -7.62) (end 7.62 7.62)
        (stroke (width 0.254) (type default)) (fill (type background))))
    (symbol "INA226AIDGSR_1_1"
      (pin input   line (at -10.16 -5.08 0) (length 2.54)
        (name "IN+" (effects (font (size 1.016 1.016))))
        (number "1"  (effects (font (size 1.016 1.016)))))
      (pin input   line (at -10.16 -2.54 0) (length 2.54)
        (name "IN-" (effects (font (size 1.016 1.016))))
        (number "2"  (effects (font (size 1.016 1.016)))))
      (pin power_in line (at -10.16  0.00 0) (length 2.54)
        (name "GND" (effects (font (size 1.016 1.016))))
        (number "3"  (effects (font (size 1.016 1.016)))))
      (pin power_in line (at -10.16  2.54 0) (length 2.54)
        (name "VS"  (effects (font (size 1.016 1.016))))
        (number "4"  (effects (font (size 1.016 1.016)))))
      (pin input   line (at -10.16  5.08 0) (length 2.54)
        (name "A0"  (effects (font (size 1.016 1.016))))
        (number "9"  (effects (font (size 1.016 1.016)))))
      (pin bidirectional line (at 10.16 -5.08 180) (length 2.54)
        (name "SDA"   (effects (font (size 1.016 1.016))))
        (number "5"    (effects (font (size 1.016 1.016)))))
      (pin input   line (at 10.16 -2.54 180) (length 2.54)
        (name "SCL"   (effects (font (size 1.016 1.016))))
        (number "6"    (effects (font (size 1.016 1.016)))))
      (pin open_collector line (at 10.16  0.00 180) (length 2.54)
        (name "ALERT" (effects (font (size 1.016 1.016))))
        (number "7"    (effects (font (size 1.016 1.016)))))
      (pin input   line (at 10.16  2.54 180) (length 2.54)
        (name "A1"    (effects (font (size 1.016 1.016))))
        (number "8"    (effects (font (size 1.016 1.016)))))
      (pin input   line (at 10.16  5.08 180) (length 2.54)
        (name "VBUS"  (effects (font (size 1.016 1.016))))
        (number "10"   (effects (font (size 1.016 1.016)))))
    )
  )"""


def lib_symbol_bq76930():
    """BQ76930 6S cell monitor — key pins only (simplified symbol)."""
    return """  (symbol "BQ76930PWRQ1" (in_bom yes) (on_board yes)
    (property "Reference" "U" (at 0 -20.32 0) (effects (font (size 1.27 1.27))))
    (property "Value" "BQ76930PWRQ1" (at 0 20.32 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_QFP:TQFP-64_10x10mm_P0.5mm" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.ti.com/lit/ds/symlink/bq76930.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "BQ76930PWRQ1_0_1"
      (rectangle (start -12.70 -17.78) (end 12.70 17.78)
        (stroke (width 0.254) (type default)) (fill (type background))))
    (symbol "BQ76930PWRQ1_1_1"
      (pin input   line (at -15.24 -15.24 0) (length 2.54)
        (name "VC0"    (effects (font (size 1.016 1.016))))
        (number "1"     (effects (font (size 1.016 1.016)))))
      (pin input   line (at -15.24 -12.70 0) (length 2.54)
        (name "VC1"    (effects (font (size 1.016 1.016))))
        (number "2"     (effects (font (size 1.016 1.016)))))
      (pin input   line (at -15.24 -10.16 0) (length 2.54)
        (name "VC2"    (effects (font (size 1.016 1.016))))
        (number "3"     (effects (font (size 1.016 1.016)))))
      (pin input   line (at -15.24  -7.62 0) (length 2.54)
        (name "VC3"    (effects (font (size 1.016 1.016))))
        (number "4"     (effects (font (size 1.016 1.016)))))
      (pin input   line (at -15.24  -5.08 0) (length 2.54)
        (name "VC4"    (effects (font (size 1.016 1.016))))
        (number "5"     (effects (font (size 1.016 1.016)))))
      (pin input   line (at -15.24  -2.54 0) (length 2.54)
        (name "VC5"    (effects (font (size 1.016 1.016))))
        (number "6"     (effects (font (size 1.016 1.016)))))
      (pin input   line (at -15.24   0.00 0) (length 2.54)
        (name "VC6"    (effects (font (size 1.016 1.016))))
        (number "7"     (effects (font (size 1.016 1.016)))))
      (pin input   line (at -15.24   2.54 0) (length 2.54)
        (name "BAL_GND" (effects (font (size 1.016 1.016))))
        (number "8"     (effects (font (size 1.016 1.016)))))
      (pin input   line (at -15.24   5.08 0) (length 2.54)
        (name "TS1"    (effects (font (size 1.016 1.016))))
        (number "9"     (effects (font (size 1.016 1.016)))))
      (pin power_in line (at -15.24   7.62 0) (length 2.54)
        (name "REGSRC" (effects (font (size 1.016 1.016))))
        (number "10"    (effects (font (size 1.016 1.016)))))
      (pin passive line (at -15.24  10.16 0) (length 2.54)
        (name "CAP"    (effects (font (size 1.016 1.016))))
        (number "11"    (effects (font (size 1.016 1.016)))))
      (pin power_in line (at -15.24  12.70 0) (length 2.54)
        (name "GND"    (effects (font (size 1.016 1.016))))
        (number "12"    (effects (font (size 1.016 1.016)))))
      (pin power_in line (at  15.24 -15.24 180) (length 2.54)
        (name "BAT+"   (effects (font (size 1.016 1.016))))
        (number "13"    (effects (font (size 1.016 1.016)))))
      (pin bidirectional line (at 15.24 -12.70 180) (length 2.54)
        (name "SDA"    (effects (font (size 1.016 1.016))))
        (number "14"    (effects (font (size 1.016 1.016)))))
      (pin input   line (at  15.24 -10.16 180) (length 2.54)
        (name "SCL"    (effects (font (size 1.016 1.016))))
        (number "15"    (effects (font (size 1.016 1.016)))))
      (pin open_collector line (at 15.24 -7.62 180) (length 2.54)
        (name "ALERT_N" (effects (font (size 1.016 1.016))))
        (number "16"    (effects (font (size 1.016 1.016)))))
      (pin output  line (at  15.24  -5.08 180) (length 2.54)
        (name "DSG"    (effects (font (size 1.016 1.016))))
        (number "17"    (effects (font (size 1.016 1.016)))))
      (pin output  line (at  15.24  -2.54 180) (length 2.54)
        (name "CHG"    (effects (font (size 1.016 1.016))))
        (number "18"    (effects (font (size 1.016 1.016)))))
    )
  )"""


def lib_symbol_tps54620():
    return """  (symbol "TPS54620RGYT" (in_bom yes) (on_board yes)
    (property "Reference" "U" (at 0 -12.70 0) (effects (font (size 1.27 1.27))))
    (property "Value" "TPS54620RGYT" (at 0 12.70 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_DFN_QFN:QFN-16-1EP_4x4mm_P0.65mm_EP2.1x2.1mm" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.ti.com/lit/ds/symlink/tps54620.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "TPS54620RGYT_0_1"
      (rectangle (start -10.16 -10.16) (end 10.16 10.16)
        (stroke (width 0.254) (type default)) (fill (type background))))
    (symbol "TPS54620RGYT_1_1"
      (pin power_in  line (at -12.70 -7.62 0) (length 2.54)
        (name "VIN"   (effects (font (size 1.016 1.016))))
        (number "1"    (effects (font (size 1.016 1.016)))))
      (pin input     line (at -12.70 -5.08 0) (length 2.54)
        (name "EN"    (effects (font (size 1.016 1.016))))
        (number "2"    (effects (font (size 1.016 1.016)))))
      (pin input     line (at -12.70 -2.54 0) (length 2.54)
        (name "SS"    (effects (font (size 1.016 1.016))))
        (number "3"    (effects (font (size 1.016 1.016)))))
      (pin input     line (at -12.70  0.00 0) (length 2.54)
        (name "COMP"  (effects (font (size 1.016 1.016))))
        (number "4"    (effects (font (size 1.016 1.016)))))
      (pin input     line (at -12.70  2.54 0) (length 2.54)
        (name "FB"    (effects (font (size 1.016 1.016))))
        (number "5"    (effects (font (size 1.016 1.016)))))
      (pin power_in  line (at -12.70  5.08 0) (length 2.54)
        (name "GND"   (effects (font (size 1.016 1.016))))
        (number "6"    (effects (font (size 1.016 1.016)))))
      (pin passive   line (at  12.70 -5.08 180) (length 2.54)
        (name "BOOT"  (effects (font (size 1.016 1.016))))
        (number "7"    (effects (font (size 1.016 1.016)))))
      (pin output    line (at  12.70  0.00 180) (length 2.54)
        (name "SW"    (effects (font (size 1.016 1.016))))
        (number "8"    (effects (font (size 1.016 1.016)))))
      (pin power_in  line (at  12.70  5.08 180) (length 2.54)
        (name "PGND"  (effects (font (size 1.016 1.016))))
        (number "9"    (effects (font (size 1.016 1.016)))))
    )
  )"""


def lib_symbol_tps54540():
    return """  (symbol "TPS54540DDAR" (in_bom yes) (on_board yes)
    (property "Reference" "U" (at 0 -10.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "TPS54540DDAR" (at 0 10.16 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.ti.com/lit/ds/symlink/tps54540.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "TPS54540DDAR_0_1"
      (rectangle (start -7.62 -7.62) (end 7.62 7.62)
        (stroke (width 0.254) (type default)) (fill (type background))))
    (symbol "TPS54540DDAR_1_1"
      (pin passive   line (at -10.16 -5.08 0) (length 2.54)
        (name "BOOT"  (effects (font (size 1.016 1.016))))
        (number "1"    (effects (font (size 1.016 1.016)))))
      (pin power_in  line (at -10.16 -2.54 0) (length 2.54)
        (name "VIN"   (effects (font (size 1.016 1.016))))
        (number "2"    (effects (font (size 1.016 1.016)))))
      (pin input     line (at -10.16  0.00 0) (length 2.54)
        (name "EN"    (effects (font (size 1.016 1.016))))
        (number "3"    (effects (font (size 1.016 1.016)))))
      (pin input     line (at -10.16  2.54 0) (length 2.54)
        (name "SS"    (effects (font (size 1.016 1.016))))
        (number "4"    (effects (font (size 1.016 1.016)))))
      (pin input     line (at  10.16 -5.08 180) (length 2.54)
        (name "COMP"  (effects (font (size 1.016 1.016))))
        (number "5"    (effects (font (size 1.016 1.016)))))
      (pin input     line (at  10.16 -2.54 180) (length 2.54)
        (name "FB"    (effects (font (size 1.016 1.016))))
        (number "6"    (effects (font (size 1.016 1.016)))))
      (pin power_in  line (at  10.16  0.00 180) (length 2.54)
        (name "GND"   (effects (font (size 1.016 1.016))))
        (number "7"    (effects (font (size 1.016 1.016)))))
      (pin output    line (at  10.16  2.54 180) (length 2.54)
        (name "SW"    (effects (font (size 1.016 1.016))))
        (number "8"    (effects (font (size 1.016 1.016)))))
    )
  )"""


def lib_symbol_prtr5v0u2x():
    """Dual TVS SOT-363: GND(1), IO1(2), D1A(3), VCC(4), D2A(5), IO2(6)."""
    return """  (symbol "PRTR5V0U2X" (in_bom yes) (on_board yes)
    (property "Reference" "D" (at 0 -7.62 0) (effects (font (size 1.27 1.27))))
    (property "Value" "PRTR5V0U2X" (at 0 7.62 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_TO_SOT_SMD:SOT-363_SC-70-6" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://assets.nexperia.com/documents/data-sheet/PRTR5V0U2X.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "PRTR5V0U2X_0_1"
      (rectangle (start -5.08 -5.08) (end 5.08 5.08)
        (stroke (width 0.254) (type default)) (fill (type background))))
    (symbol "PRTR5V0U2X_1_1"
      (pin power_in line (at -7.62 -2.54 0) (length 2.54)
        (name "GND" (effects (font (size 1.016 1.016))))
        (number "1"  (effects (font (size 1.016 1.016)))))
      (pin bidirectional line (at -7.62  0.00 0) (length 2.54)
        (name "IO1" (effects (font (size 1.016 1.016))))
        (number "2"  (effects (font (size 1.016 1.016)))))
      (pin passive    line (at -7.62  2.54 0) (length 2.54)
        (name "D1A" (effects (font (size 1.016 1.016))))
        (number "3"  (effects (font (size 1.016 1.016)))))
      (pin power_in   line (at  7.62 -2.54 180) (length 2.54)
        (name "VCC" (effects (font (size 1.016 1.016))))
        (number "4"  (effects (font (size 1.016 1.016)))))
      (pin passive    line (at  7.62  0.00 180) (length 2.54)
        (name "D2A" (effects (font (size 1.016 1.016))))
        (number "5"  (effects (font (size 1.016 1.016)))))
      (pin bidirectional line (at 7.62  2.54 180) (length 2.54)
        (name "IO2" (effects (font (size 1.016 1.016))))
        (number "6"  (effects (font (size 1.016 1.016)))))
    )
  )"""


def lib_symbol_conn_2p(name):
    return f"""  (symbol "{name}" (in_bom yes) (on_board yes)
    (property "Reference" "J" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{name}" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "{name}_0_1"
      (rectangle (start -3.81 -2.54) (end 0 2.54)
        (stroke (width 0.254) (type default)) (fill (type background))))
    (symbol "{name}_1_1"
{_pin_def("passive", "line", 2.54, -1.27, 180, 2.54, "1", "1")}
{_pin_def("passive", "line", 2.54,  1.27, 180, 2.54, "2", "2")})
  )"""


def lib_symbol_conn_4p(name):
    return f"""  (symbol "{name}" (in_bom yes) (on_board yes)
    (property "Reference" "J" (at 0 -6.35 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{name}" (at 0 6.35 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "{name}_0_1"
      (rectangle (start -3.81 -5.08) (end 0 5.08)
        (stroke (width 0.254) (type default)) (fill (type background))))
    (symbol "{name}_1_1"
{_pin_def("passive", "line", 2.54, -3.81, 180, 2.54, "1", "1")}
{_pin_def("passive", "line", 2.54, -1.27, 180, 2.54, "2", "2")}
{_pin_def("passive", "line", 2.54,  1.27, 180, 2.54, "3", "3")}
{_pin_def("passive", "line", 2.54,  3.81, 180, 2.54, "4", "4")})
  )"""


def lib_symbol_conn_7p(name):
    return f"""  (symbol "{name}" (in_bom yes) (on_board yes)
    (property "Reference" "J" (at 0 -10.16 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{name}" (at 0 10.16 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "{name}_0_1"
      (rectangle (start -3.81 -8.89) (end 0 8.89)
        (stroke (width 0.254) (type default)) (fill (type background))))
    (symbol "{name}_1_1"
{_pin_def("passive","line",2.54,-7.62,180,2.54,"1","1")}
{_pin_def("passive","line",2.54,-5.08,180,2.54,"2","2")}
{_pin_def("passive","line",2.54,-2.54,180,2.54,"3","3")}
{_pin_def("passive","line",2.54, 0.00,180,2.54,"4","4")}
{_pin_def("passive","line",2.54, 2.54,180,2.54,"5","5")}
{_pin_def("passive","line",2.54, 5.08,180,2.54,"6","6")}
{_pin_def("passive","line",2.54, 7.62,180,2.54,"7","7")})
  )"""


def lib_symbol_m3pad(name="M3_ChassisPad"):
    """Single-pin M3 chassis ground lug pad."""
    return f"""  (symbol "{name}" (in_bom yes) (on_board yes)
    (property "Reference" "TP" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{name}" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "{name}_0_1"
      (circle (center 0 0) (radius 1.0)
        (stroke (width 0.254) (type default)) (fill (type background))))
    (symbol "{name}_1_1"
{_pin_def("passive","line",-2.54,0,0,1.54,"PGND","1")})
  )"""


# ---------------------------------------------------------------------------
# Power symbols
# ---------------------------------------------------------------------------

def lib_sym_power(name, y_pin=0, bar_top=True):
    """Generic power flag symbol."""
    ybox = -1.27 if bar_top else 1.27
    yend = 1.27 if bar_top else -1.27
    pin_angle = 270 if bar_top else 90
    pin_x = 0.0
    pin_y = 1.27 if bar_top else -1.27
    return f"""  (symbol "{name}" (power) (in_bom no) (on_board no)
    (property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "{name}" (at 0 {yend:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "{name}_0_1"
      (polyline (pts (xy -1.27 {ybox:.2f}) (xy 0 {yend:.2f}) (xy 1.27 {ybox:.2f}))
        (stroke (width 0) (type default)) (fill (type none))))
    (symbol "{name}_1_1"
""" + _pin_def("power_in", "line", pin_x, pin_y, pin_angle, 1.27, "~", "1") + """
  )
  )"""


# ---------------------------------------------------------------------------
# Schematic instance helpers
# ---------------------------------------------------------------------------

_uid_i = [0]


def _next_uid() -> str:
    _uid_i[0] += 1
    val = _uid_i[0]
    h = f"{val:032x}"
    return f"a3{h[2:10]}-{h[10:14]}-{h[14:18]}-{h[18:22]}-{h[22:34]}"


def sym_inst(lib_id, ref, value, cx, cy, rot=0, dnp=False, footprint="", datasheet="",
             pin_uids=None, extra_props=None):
    """Generate a symbol placement S-expression."""
    dnp_str = "yes" if dnp else "no"
    lines = [
        f'  (symbol (lib_id "{lib_id}") (at {cx:.2f} {cy:.2f} {rot})',
        f'    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp {dnp_str})',
        f'    (uuid "{_next_uid()}")',
        f'    (property "Reference" "{ref}" (at {cx:.2f} {cy - 3.81:.2f} {rot})',
        f'      (effects (font (size 1.27 1.27))))',
        f'    (property "Value" "{value}" (at {cx:.2f} {cy + 3.81:.2f} {rot})',
        f'      (effects (font (size 1.27 1.27))))',
        f'    (property "Footprint" "{footprint}" (at 0 0 0)',
        f'      (effects (font (size 1.27 1.27)) (hide yes)))',
        f'    (property "Datasheet" "{datasheet}" (at 0 0 0)',
        f'      (effects (font (size 1.27 1.27)) (hide yes)))',
    ]
    if extra_props:
        lines.extend(extra_props)
    if pin_uids:
        for pin_num, puid in pin_uids.items():
            lines.append(f'    (pin "{pin_num}" (uuid "{puid}"))')
    lines.append('  )')
    return '\n'.join(lines)


def pwr_sym(lib_id, cx, cy, rot=270):
    """Place a power symbol (+5V, GND, VBAT, PGND etc.)."""
    lines = [
        f'  (symbol (lib_id "{lib_id}") (at {cx:.2f} {cy:.2f} {rot})',
        f'    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)',
        f'    (uuid "{_next_uid()}")',
        f'    (property "Reference" "#PWR" (at {cx:.2f} {cy:.2f} 0)',
        f'      (effects (font (size 1.27 1.27)) (hide yes)))',
        f'    (property "Value" "{lib_id}" (at {cx:.2f} {cy - 2.54:.2f} 0)',
        f'      (effects (font (size 1.27 1.27))))',
        f'    (property "Footprint" "" (at 0 0 0)',
        f'      (effects (font (size 1.27 1.27)) (hide yes)))',
        f'    (property "Datasheet" "" (at 0 0 0)',
        f'      (effects (font (size 1.27 1.27)) (hide yes)))',
        f'    (pin "1" (uuid "{_next_uid()}"))',
        f'  )',
    ]
    return '\n'.join(lines)


def wire(x1, y1, x2, y2):
    return (f'  (wire (pts (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y2:.2f}))\n'
            f'    (uuid "{_next_uid()}"))')


def glabel(name, x, y, rot=0, shape="bidirectional"):
    return (f'  (global_label "{name}" (shape {shape}) (at {x:.2f} {y:.2f} {rot})\n'
            f'    (effects (font (size 1.016 1.016)))\n'
            f'    (uuid "{_next_uid()}")\n'
            f'    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {x:.2f} {y:.2f} 0)\n'
            f'      (effects (font (size 1.016 1.016)) (hide yes))))')


def nc(x, y):
    return (f'  (no_connect (at {x:.2f} {y:.2f})\n'
            f'    (uuid "{_next_uid()}"))')


def junc(x, y):
    return (f'  (junction (at {x:.2f} {y:.2f}) (diameter 0) (color 0 0 0 0)\n'
            f'    (uuid "{_next_uid()}"))')


def text_note(txt, x, y):
    return (f'  (text "{txt}" (at {x:.2f} {y:.2f} 0)\n'
            f'    (effects (font (size 1.27 1.27)))\n'
            f'    (uuid "{_next_uid()}"))')


# ---------------------------------------------------------------------------
# kicad_sch body builder
# ---------------------------------------------------------------------------

def gen_sch() -> str:
    parts = []

    # -----------------------------------------------------------------------
    # lib_symbols
    # -----------------------------------------------------------------------
    lib = [
        '  (lib_symbols',
        lib_symbol_2pin_h("C_Generic"),
        lib_symbol_2pin_h("R_Generic"),
        lib_symbol_2pin_h("L_Generic"),
        lib_symbol_2pin_h("FB_Generic"),
        lib_symbol_fuse("Fuse_MAXI_150A"),
        lib_symbol_fuse("Fuse_Mini_40A"),
        lib_symbol_fuse("Fuse_MIDI_100A"),
        lib_symbol_tvs_bi("SMBJ33CA"),
        lib_symbol_schottky_dual("MBRD1045CT"),
        lib_symbol_nmos("AON6556"),
        lib_symbol_cmc4("CMC_7440640500"),
        lib_symbol_shunt4t("CSS2H_2512K_1mOhm"),
        lib_symbol_ina226(),
        lib_symbol_bq76930(),
        lib_symbol_tps54620(),
        lib_symbol_tps54540(),
        lib_symbol_prtr5v0u2x(),
        lib_symbol_conn_2p("XT60PW_F"),
        lib_symbol_conn_2p("XT30PW_F"),
        lib_symbol_conn_2p("Conn_JST_GH_02P"),
        lib_symbol_conn_4p("Conn_JST_GH_04P"),
        lib_symbol_conn_7p("JST_XH_7P"),
        lib_symbol_conn_4p("Nano_Fit_4P"),
        lib_symbol_m3pad("M3_ChassisPad"),
        lib_sym_power("VBAT",  bar_top=True),
        lib_sym_power("VDIS",  bar_top=True),
        lib_sym_power("PGND",  bar_top=False),
        lib_sym_power("+5V",   bar_top=True),
        lib_sym_power("+6V",   bar_top=True),
        lib_sym_power("5V_AVIONICS", bar_top=True),
        lib_sym_power("6V_SERVO",    bar_top=True),
        '  )',
    ]
    parts.extend(lib)

    # -----------------------------------------------------------------------
    # Section A: Battery input  (x=20..110, y=30)
    # -----------------------------------------------------------------------
    parts.append(text_note("=== Section A: Battery Input / Main Bus Filter ===", 10, 15))

    # J_BATT (XT60PW-F) — battery connector, pin1=+VBAT, pin2=PGND
    cx, cy = 20, 30
    parts.append(sym_inst("XT60PW_F", "J_BATT", "Amass XT60PW-F", cx, cy))
    parts.append(glabel("VBAT_IN_P", cx + 2.54, cy - 1.27, rot=0))
    parts.append(glabel("VBAT_IN_N", cx + 2.54, cy + 1.27, rot=0))

    # J_PGND_BATT (M3 lug near J_BATT)
    parts.append(sym_inst("M3_ChassisPad", "J_PGND_BATT", "M3 chassis lug", cx + 10, cy + 8))
    parts.append(pwr_sym("PGND", cx + 10 - 2.54, cy + 8, rot=270))

    # CM1 — first common-mode choke
    cx, cy = 45, 30
    parts.append(sym_inst("CMC_7440640500", "CM1", "Wurth 7440640500 10A 2x100uH", cx, cy))
    parts.append(glabel("VBAT_IN_P",  cx - 7.62, cy - 2.54, rot=180))
    parts.append(glabel("VBAT_IN_N",  cx - 7.62, cy + 2.54, rot=180))
    parts.append(glabel("CM1_OUT_P",  cx + 7.62, cy - 2.54, rot=0))
    parts.append(glabel("CM1_OUT_N",  cx + 7.62, cy + 2.54, rot=0))

    # CM2 — second common-mode choke
    cx, cy = 70, 30
    parts.append(sym_inst("CMC_7440640500", "CM2", "Wurth 7440640500 10A 2x100uH", cx, cy))
    parts.append(glabel("CM1_OUT_P",  cx - 7.62, cy - 2.54, rot=180))
    parts.append(glabel("CM1_OUT_N",  cx - 7.62, cy + 2.54, rot=180))
    parts.append(glabel("CM2_OUT_P",  cx + 7.62, cy - 2.54, rot=0))
    parts.append(glabel("CM2_OUT_N",  cx + 7.62, cy + 2.54, rot=0))

    # F1 — main 150A MAXI blade fuse
    cx, cy = 93, 30
    parts.append(sym_inst("Fuse_MAXI_150A", "F1", "Littelfuse 0297150.ZXNV 150A MAXI", cx, cy))
    parts.append(glabel("CM2_OUT_P",  cx - 2.54, cy, rot=180))
    parts.append(glabel("VBAT",       cx + 2.54, cy, rot=0))

    # PGND bus continuation from CM2_OUT_N
    parts.append(glabel("CM2_OUT_N",  cx - 2.54, cy + 7.62, rot=180))
    parts.append(pwr_sym("PGND", cx - 2.54, cy + 7.62 + 1.27, rot=270))

    # Decoupling cluster: C1, C2, C_DM1, C3 (bulk + HF bypass)
    for i, (ref, val, dx) in enumerate([
        ("C1",    "Panasonic EEF-CX1V221R 220uF/35V",   20),
        ("C2",    "Panasonic EEF-CX1V221R 220uF/35V",   27),
        ("C_DM1", "Wurth 885012207016 10uF/50V X7R 1210", 34),
        ("C3",    "100nF X7R 0805 50V",                  41),
    ]):
        cx2, cy2 = dx, 48
        parts.append(sym_inst("C_Generic", ref, val, cx2, cy2))
        parts.append(pwr_sym("VBAT",  cx2 - 2.54, cy2, rot=0))
        parts.append(pwr_sym("PGND",  cx2 + 2.54, cy2, rot=180))

    # D1 — TVS clamp
    parts.append(sym_inst("SMBJ33CA", "D1", "SMBJ33CA 33V/400W TVS", 50, 48))
    parts.append(pwr_sym("VBAT",  50 - 2.54, 48, rot=0))
    parts.append(pwr_sym("PGND",  50 + 2.54, 48, rot=180))

    # C_Y1, C_Y2 — Y-class CM bypass caps
    parts.append(sym_inst("C_Generic", "C_Y1", "Kemet SA305E472MAR 4.7nF/250V Y2", 58, 48))
    parts.append(pwr_sym("VBAT",  58 - 2.54, 48, rot=0))
    parts.append(glabel("CHASSIS", 58 + 2.54, 48, rot=0))

    parts.append(sym_inst("C_Generic", "C_Y2", "Kemet SA305E472MAR 4.7nF/250V Y2", 65, 48))
    parts.append(pwr_sym("PGND",  65 - 2.54, 48, rot=0))
    parts.append(glabel("CHASSIS", 65 + 2.54, 48, rot=0))

    # -----------------------------------------------------------------------
    # Section B: Disconnect FET + main shunt + main INA226  (x=105..200, y=30)
    # -----------------------------------------------------------------------
    parts.append(text_note("=== Section B: Battery Disconnect + Main Shunt ===", 100, 15))

    # Q_BATT_DSG (AON6556): G=DSG_GATE, S=PGND, D=VBAT→VDIS
    cx, cy = 120, 30
    parts.append(sym_inst("AON6556", "Q_BATT_DSG", "AON6556 60V/30A NMOS", cx, cy))
    parts.append(glabel("DSG_GATE", cx - 7.62, cy - 2.54, rot=180))
    parts.append(pwr_sym("PGND",    cx - 7.62, cy + 2.54, rot=0))
    parts.append(pwr_sym("VBAT",    cx + 7.62, cy,         rot=180))

    # R_DSG_G — gate resistor 10k
    parts.append(sym_inst("R_Generic", "R_DSG_G", "10k 0402", cx - 12, cy + 10))
    parts.append(glabel("BQ_DSG_OUT", cx - 12 - 2.54, cy + 10, rot=180))
    parts.append(glabel("DSG_GATE",   cx - 12 + 2.54, cy + 10, rot=0))

    # R_CHGND — 0 Ohm chassis-PGND bond (socketed)
    parts.append(sym_inst("R_Generic", "R_CHGND", "0R 0402 (chassis-PGND bond, configurable)", cx - 12, cy + 18))
    parts.append(glabel("CHASSIS",    cx - 12 - 2.54, cy + 18, rot=180))
    parts.append(pwr_sym("PGND",      cx - 12 + 2.54, cy + 18, rot=180))

    # J_CHASSIS — M3 standoff pads (chassis bond point)
    parts.append(sym_inst("M3_ChassisPad", "J_CHASSIS", "M3 x8 brass standoff (x4)", cx - 5, cy + 25))
    parts.append(glabel("CHASSIS",    cx - 5 - 2.54, cy + 25, rot=180))

    # RS_MAIN — 1mΩ 4-terminal shunt (after Q_BATT_DSG drain, before VDIS)
    cx, cy = 150, 30
    parts.append(sym_inst("CSS2H_2512K_1mOhm", "RS_MAIN", "Bourns CSS2H-2512K-1L00F 1mOhm 3W", cx, cy))
    parts.append(pwr_sym("VBAT",  cx - 6.35, cy - 1.27, rot=0))
    parts.append(pwr_sym("PGND",  cx - 6.35, cy + 1.27, rot=0))  # F- carried from PGND rail
    parts.append(pwr_sym("VDIS",  cx + 6.35, cy - 1.27, rot=180))
    parts.append(glabel("RS_MAIN_SP", cx - 6.35, cy + 1.27, rot=0))
    # Sense outputs
    parts.append(glabel("RS_MAIN_SN", cx + 6.35, cy + 1.27, rot=180))

    # U_IS_MAIN — INA226 main bus monitor (addr 0x44)
    cx, cy = 178, 30
    parts.append(sym_inst("INA226AIDGSR", "U_IS_MAIN", "INA226AIDGSR I2C addr=0x44", cx, cy))
    parts.append(glabel("RS_MAIN_SP",  cx - 10.16, cy - 5.08, rot=180))  # IN+
    parts.append(glabel("RS_MAIN_SN",  cx - 10.16, cy - 2.54, rot=180))  # IN-
    parts.append(pwr_sym("PGND",       cx - 10.16, cy,         rot=0))   # GND
    parts.append(pwr_sym("+5V",        cx - 10.16, cy + 2.54,  rot=0))   # VS
    # A0=GND (0x44: A0=GND, A1=VCC)
    parts.append(pwr_sym("PGND",       cx - 10.16, cy + 5.08,  rot=0))   # A0=GND
    parts.append(glabel("PDB_SDA",     cx + 10.16, cy - 5.08,  rot=0))   # SDA
    parts.append(glabel("PDB_SCL",     cx + 10.16, cy - 2.54,  rot=0))   # SCL
    parts.append(glabel("PDB_ALERT_N", cx + 10.16, cy,          rot=0))  # ALERT
    parts.append(pwr_sym("+5V",        cx + 10.16, cy + 2.54,  rot=180)) # A1=VCC (addr bit)
    parts.append(glabel("VDIS_SENSE",  cx + 10.16, cy + 5.08,  rot=0))  # VBUS

    # -----------------------------------------------------------------------
    # Section C: 4x ESC branches  (y=80..220)
    # -----------------------------------------------------------------------
    parts.append(text_note("=== Section C: ESC Power Branches (x4) ===", 10, 70))

    esc_info = [
        ("1", "F_ESC1", "C_DEC1", "CM_ESC1", "RS1", "U_IS1",  "J_ESC1",  "J_SHLD_ESC1",  "0x40", "PGND", "PGND"),
        ("2", "F_ESC2", "C_DEC2", "CM_ESC2", "RS2", "U_IS2",  "J_ESC2",  "J_SHLD_ESC2",  "0x41", "+5V",  "PGND"),
        ("3", "F_ESC3", "C_DEC3", "CM_ESC3", "RS3", "U_IS3",  "J_ESC3",  "J_SHLD_ESC3",  "0x42", "PDB_SDA", "PGND"),
        ("4", "F_ESC4", "C_DEC4", "CM_ESC4", "RS4", "U_IS4",  "J_ESC4",  "J_SHLD_ESC4",  "0x43", "PDB_SCL", "PGND"),
    ]
    # ESC5 DNP
    esc_dnp = ("5", "F_ESC5", "C_DEC5", "CM_ESC5", "RS5", "U_IS5", "J_ESC5", "J_SHLD_ESC5", "0x45", "PGND", "PGND")

    def esc_branch(n, f_ref, cdec_ref, cm_ref, rs_ref, uis_ref, j_ref, shld_ref,
                   addr, a0_net, a1_net, base_x, base_y, dnp=False):
        """Emit one complete ESC branch."""
        bx = base_x

        # F_ESCn — 40A mini blade fuse
        fx, fy = bx + 5, base_y
        parts.append(sym_inst("Fuse_Mini_40A", f_ref, "Littelfuse 0297040.WXNV 40A mini blade",
                              fx, fy, dnp=dnp))
        parts.append(pwr_sym("VDIS",       fx - 2.54, fy, rot=0))
        parts.append(glabel(f"ESC{n}_FUSED", fx + 2.54, fy, rot=0))

        # C_DECn — 470µF/35V low-ESR electrolytic
        cx2, cy2 = bx + 5, base_y + 15
        parts.append(sym_inst("C_Generic", cdec_ref,
                              "Panasonic EEUFC1V471 470uF/35V D10x20mm low-ESR",
                              cx2, cy2, dnp=dnp))
        parts.append(glabel(f"ESC{n}_FUSED", cx2 - 2.54, cy2, rot=180))
        parts.append(pwr_sym("PGND",         cx2 + 2.54, cy2, rot=180))

        # CM_ESCn — 4-terminal CMC
        cx2, cy2 = bx + 5, base_y + 30
        parts.append(sym_inst("CMC_7440640500", cm_ref,
                              "Wurth 7440640500 10A 2x100uH per-ESC CMC",
                              cx2, cy2, dnp=dnp))
        parts.append(glabel(f"ESC{n}_FUSED",  cx2 - 7.62, cy2 - 2.54, rot=180))
        parts.append(pwr_sym("PGND",           cx2 - 7.62, cy2 + 2.54, rot=0))
        parts.append(glabel(f"ESC{n}_CM_OUT",  cx2 + 7.62, cy2 - 2.54, rot=0))
        parts.append(pwr_sym("PGND",           cx2 + 7.62, cy2 + 2.54, rot=180))

        # RS_n — 1mΩ 4-terminal Kelvin shunt
        cx2, cy2 = bx + 5, base_y + 50
        parts.append(sym_inst("CSS2H_2512K_1mOhm", rs_ref,
                              "Bourns CSS2H-2512K-1L00F 1mOhm 3W", cx2, cy2, dnp=dnp))
        parts.append(glabel(f"ESC{n}_CM_OUT",  cx2 - 6.35, cy2 - 1.27, rot=180))
        parts.append(pwr_sym("PGND",            cx2 - 6.35, cy2 + 1.27, rot=0))
        parts.append(glabel(f"ESC{n}_RS_OUT",   cx2 + 6.35, cy2 - 1.27, rot=0))
        parts.append(glabel(f"ESC{n}_RS_SN",    cx2 + 6.35, cy2 + 1.27, rot=0))
        parts.append(glabel(f"ESC{n}_RS_SP",    cx2 - 6.35, cy2 + 1.27, rot=180))

        # U_ISn — INA226
        cx2, cy2 = bx + 5, base_y + 73
        parts.append(sym_inst("INA226AIDGSR", uis_ref,
                              f"INA226AIDGSR I2C addr={addr}", cx2, cy2, dnp=dnp))
        parts.append(glabel(f"ESC{n}_RS_SP",  cx2 - 10.16, cy2 - 5.08, rot=180))
        parts.append(glabel(f"ESC{n}_RS_SN",  cx2 - 10.16, cy2 - 2.54, rot=180))
        parts.append(pwr_sym("PGND",           cx2 - 10.16, cy2,         rot=0))
        parts.append(pwr_sym("+5V",            cx2 - 10.16, cy2 + 2.54,  rot=0))
        # A0 pin — per address table
        if a0_net in ("PGND", "+5V"):
            parts.append(pwr_sym(a0_net,       cx2 - 10.16, cy2 + 5.08,  rot=0))
        else:
            parts.append(glabel(a0_net,        cx2 - 10.16, cy2 + 5.08, rot=180))
        parts.append(glabel("PDB_SDA",         cx2 + 10.16, cy2 - 5.08, rot=0))
        parts.append(glabel("PDB_SCL",         cx2 + 10.16, cy2 - 2.54, rot=0))
        parts.append(glabel("PDB_ALERT_N",     cx2 + 10.16, cy2,         rot=0))
        # A1 pin
        if a1_net in ("PGND", "+5V"):
            parts.append(pwr_sym(a1_net,       cx2 + 10.16, cy2 + 2.54, rot=180))
        else:
            parts.append(glabel(a1_net,        cx2 + 10.16, cy2 + 2.54, rot=0))
        # VBUS — connect to ESC RS output side for bus voltage measurement
        parts.append(glabel(f"ESC{n}_RS_OUT",  cx2 + 10.16, cy2 + 5.08, rot=0))

        # J_ESCn — XT30PW-F connector
        cx2, cy2 = bx + 5, base_y + 97
        parts.append(sym_inst("XT30PW_F", j_ref,
                              "Amass XT30PW-F PCB-mount XT30 female", cx2, cy2, dnp=dnp))
        parts.append(glabel(f"ESC{n}_RS_OUT", cx2 + 2.54, cy2 - 1.27, rot=0))
        parts.append(pwr_sym("PGND",           cx2 + 2.54, cy2 + 1.27, rot=180))

        # J_SHLD_ESCn — M3 chassis lug
        parts.append(sym_inst("M3_ChassisPad", shld_ref,
                              "M3 chassis lug for ESC cable shield", bx + 18, base_y + 97, dnp=dnp))
        parts.append(pwr_sym("PGND", bx + 18 - 2.54, base_y + 97, rot=0))

    # Place 4 ESC branches at x=20,60,100,140
    for idx, info in enumerate(esc_info):
        n, f_ref, cdec_ref, cm_ref, rs_ref, uis_ref, j_ref, shld_ref, addr, a0, a1 = info
        esc_branch(n, f_ref, cdec_ref, cm_ref, rs_ref, uis_ref, j_ref, shld_ref,
                   addr, a0, a1, base_x=20 + idx * 45, base_y=80)

    # ESC5 DNP branch
    n, f_ref, cdec_ref, cm_ref, rs_ref, uis_ref, j_ref, shld_ref, addr, a0, a1 = esc_dnp
    esc_branch(n, f_ref, cdec_ref, cm_ref, rs_ref, uis_ref, j_ref, shld_ref,
               addr, a0, a1, base_x=200, base_y=80, dnp=True)
    parts.append(text_note("ESC5 branch: DNP — Phase 11 only", 200, 76))

    # -----------------------------------------------------------------------
    # Section D: 5V Dual BEC  (x=250..420, y=30..120)
    # -----------------------------------------------------------------------
    parts.append(text_note("=== Section D: Dual 5V BEC (diode-OR) ===", 248, 15))

    def bec5v_half(suffix, bx, by):
        """One half of the dual 5V BEC."""
        # FB_5Vn ferrite bead
        parts.append(sym_inst("FB_Generic", f"FB_5V{suffix}",
                              "Wurth 742792612 600R@100MHz 2A", bx, by))
        parts.append(pwr_sym("VDIS",   bx - 2.54, by, rot=0))
        parts.append(glabel(f"FB5V{suffix}_OUT", bx + 2.54, by, rot=0))

        # Input cap
        parts.append(sym_inst("C_Generic", f"C_BEC{suffix}_IN",
                              "100uF/50V electrolytic", bx, by + 10))
        parts.append(glabel(f"FB5V{suffix}_OUT", bx - 2.54, by + 10, rot=180))
        parts.append(pwr_sym("PGND",               bx + 2.54, by + 10, rot=180))

        # L
        parts.append(sym_inst("L_Generic", f"L{suffix}",
                              "Wurth 744314100 10uH >=6A Isat", bx + 15, by))
        parts.append(glabel(f"FB5V{suffix}_OUT", bx + 15 - 2.54, by, rot=180))
        parts.append(glabel(f"SW5V{suffix}",      bx + 15 + 2.54, by, rot=0))

        # U_BEC_5V_n TPS54620
        parts.append(sym_inst("TPS54620RGYT", f"U_BEC_5V_{suffix}",
                              "TPS54620RGYT 6A/28V sync buck 5.3Vout",
                              bx + 30, by + 5))
        cx2, cy2 = bx + 30, by + 5
        parts.append(glabel(f"FB5V{suffix}_OUT", cx2 - 12.70, cy2 - 7.62, rot=180))
        # EN — tie to VIN via resistor pullup; here tie to VIN directly (tie high)
        parts.append(glabel(f"FB5V{suffix}_OUT", cx2 - 12.70, cy2 - 5.08, rot=180))
        # SS — cap to GND
        parts.append(glabel(f"SS5V{suffix}",     cx2 - 12.70, cy2 - 2.54, rot=180))
        # COMP — RC network
        parts.append(glabel(f"COMP5V{suffix}",   cx2 - 12.70, cy2,         rot=180))
        # FB
        parts.append(glabel(f"FB5V{suffix}_FBK", cx2 - 12.70, cy2 + 2.54,  rot=180))
        parts.append(pwr_sym("PGND",              cx2 - 12.70, cy2 + 5.08,  rot=0))
        parts.append(glabel(f"BOOT5V{suffix}",    cx2 + 12.70, cy2 - 5.08,  rot=0))
        parts.append(glabel(f"SW5V{suffix}",      cx2 + 12.70, cy2,          rot=0))
        parts.append(pwr_sym("PGND",              cx2 + 12.70, cy2 + 5.08,  rot=180))

        # Feedback divider R_FBn_1/2
        parts.append(sym_inst("R_Generic", f"R_FB{suffix}_1",
                              "R for Vout=5.3V (top)", bx + 20, by + 20))
        parts.append(glabel(f"BEC5V{suffix}_RAW", bx + 20 - 2.54, by + 20, rot=180))
        parts.append(glabel(f"FB5V{suffix}_FBK",  bx + 20 + 2.54, by + 20, rot=0))

        parts.append(sym_inst("R_Generic", f"R_FB{suffix}_2",
                              "R for Vout=5.3V (bot)", bx + 20, by + 30))
        parts.append(glabel(f"FB5V{suffix}_FBK",  bx + 20 - 2.54, by + 30, rot=180))
        parts.append(pwr_sym("PGND",               bx + 20 + 2.54, by + 30, rot=180))

        # Output cap
        parts.append(sym_inst("C_Generic", f"C_BEC{suffix}_OUT",
                              "220uF 10V electrolytic + 100nF X7R", bx + 50, by + 10))
        parts.append(glabel(f"BEC5V{suffix}_RAW",  bx + 50 - 2.54, by + 10, rot=180))
        parts.append(pwr_sym("PGND",                bx + 50 + 2.54, by + 10, rot=180))

        # OR diode MBRD1045CT: A1/A2→BEC outputs, K→5V_AVIONICS
        parts.append(sym_inst("MBRD1045CT", f"D_OR{suffix}",
                              "MBRD1045CT Dual Schottky 10A/45V", bx + 60, by + 5))
        parts.append(glabel(f"BEC5V{suffix}_RAW",  bx + 60 - 6.35, by + 5 - 2.54, rot=180))
        # A2 no-connect (single-diode use per half)
        parts.append(nc(bx + 60 - 6.35, by + 5 + 2.54))
        parts.append(glabel("5V_AVIONICS",          bx + 60 + 6.35, by + 5,     rot=0))

    bec5v_half("1", bx=250, by=30)
    bec5v_half("2", bx=250, by=75)

    # 5V output decoupling and connector
    parts.append(sym_inst("C_Generic", "C_5V_OUT", "100nF X7R 0805", 340, 52))
    parts.append(glabel("5V_AVIONICS", 340 - 2.54, 52, rot=180))
    parts.append(pwr_sym("PGND",       340 + 2.54, 52, rot=180))

    parts.append(sym_inst("Nano_Fit_4P", "J_5V", "Molex Nano-Fit 4P 2.5mm avionics bus", 355, 52))
    parts.append(glabel("5V_AVIONICS",  355 + 2.54, 52 - 3.81, rot=0))
    parts.append(glabel("5V_AVIONICS",  355 + 2.54, 52 - 1.27, rot=0))
    parts.append(pwr_sym("PGND",        355 + 2.54, 52 + 1.27, rot=180))
    parts.append(pwr_sym("PGND",        355 + 2.54, 52 + 3.81, rot=180))

    parts.append(sym_inst("M3_ChassisPad", "J_SHLD_5V", "PGND via-pad 1.2mm for 5V cable shield", 355, 64))
    parts.append(pwr_sym("PGND", 355 - 2.54, 64, rot=0))

    # -----------------------------------------------------------------------
    # Section E: 6V BEC  (x=250..380, y=130)
    # -----------------------------------------------------------------------
    parts.append(text_note("=== Section E: 6V Servo BEC ===", 248, 120))

    bx, by = 250, 130
    parts.append(sym_inst("FB_Generic", "FB_6V", "Wurth 742792612 600R@100MHz 2A", bx, by))
    parts.append(pwr_sym("VDIS",   bx - 2.54, by, rot=0))
    parts.append(glabel("FB6V_OUT", bx + 2.54, by, rot=0))

    parts.append(sym_inst("C_Generic", "C_BEC_SV_IN", "100uF/50V electrolytic", bx, by + 10))
    parts.append(glabel("FB6V_OUT", bx - 2.54, by + 10, rot=180))
    parts.append(pwr_sym("PGND",    bx + 2.54, by + 10, rot=180))

    parts.append(sym_inst("L_Generic", "L3", "Wurth 744314100 10uH >=6A Isat", bx + 15, by))
    parts.append(glabel("FB6V_OUT", bx + 15 - 2.54, by, rot=180))
    parts.append(glabel("SW6V",      bx + 15 + 2.54, by, rot=0))

    cx2, cy2 = bx + 32, by + 5
    parts.append(sym_inst("TPS54540DDAR", "U_BEC_6V",
                          "TPS54540DDAR 5A/40V buck 6.0V servo rail", cx2, cy2))
    parts.append(glabel("BOOT6V",       cx2 - 10.16, cy2 - 5.08, rot=180))
    parts.append(glabel("FB6V_OUT",     cx2 - 10.16, cy2 - 2.54, rot=180))
    parts.append(glabel("FB6V_OUT",     cx2 - 10.16, cy2,         rot=180))  # EN tied high
    parts.append(glabel("SS6V",         cx2 - 10.16, cy2 + 2.54,  rot=180))
    parts.append(glabel("COMP6V",       cx2 + 10.16, cy2 - 5.08,  rot=0))
    parts.append(glabel("FB6V_FBK",     cx2 + 10.16, cy2 - 2.54,  rot=0))
    parts.append(pwr_sym("PGND",        cx2 + 10.16, cy2,          rot=180))
    parts.append(glabel("SW6V",         cx2 + 10.16, cy2 + 2.54,  rot=0))

    parts.append(sym_inst("R_Generic", "R_FB6_1", "R for Vout=6.0V (top)", bx + 20, by + 20))
    parts.append(glabel("6V_SERVO",  bx + 20 - 2.54, by + 20, rot=180))
    parts.append(glabel("FB6V_FBK",  bx + 20 + 2.54, by + 20, rot=0))

    parts.append(sym_inst("R_Generic", "R_FB6_2", "R for Vout=6.0V (bot)", bx + 20, by + 30))
    parts.append(glabel("FB6V_FBK",   bx + 20 - 2.54, by + 30, rot=180))
    parts.append(pwr_sym("PGND",      bx + 20 + 2.54, by + 30, rot=180))

    parts.append(sym_inst("C_Generic", "C_BEC_SV_OUT", "100uF + 100nF output cap", bx + 50, by + 10))
    parts.append(glabel("6V_SERVO",    bx + 50 - 2.54, by + 10, rot=180))
    parts.append(pwr_sym("PGND",       bx + 50 + 2.54, by + 10, rot=180))

    parts.append(sym_inst("Nano_Fit_4P", "J_6V", "Molex Nano-Fit 4P 2.5mm servo bus", bx + 65, by + 5))
    jcx = bx + 65
    parts.append(glabel("6V_SERVO",  jcx + 2.54, by + 5 - 3.81, rot=0))
    parts.append(glabel("6V_SERVO",  jcx + 2.54, by + 5 - 1.27, rot=0))
    parts.append(pwr_sym("PGND",     jcx + 2.54, by + 5 + 1.27, rot=180))
    parts.append(pwr_sym("PGND",     jcx + 2.54, by + 5 + 3.81, rot=180))

    parts.append(sym_inst("M3_ChassisPad", "J_SHLD_6V", "PGND via-pad for 6V cable shield", jcx, by + 20))
    parts.append(pwr_sym("PGND", jcx - 2.54, by + 20, rot=0))

    # -----------------------------------------------------------------------
    # Section F: BQ76930 Cell Monitor  (x=400..540, y=30..160)
    # -----------------------------------------------------------------------
    parts.append(text_note("=== Section F: BQ76930 6S Cell Monitor ===", 398, 15))

    # J_BAL — 7-pin JST-XH balance lead connector
    jbx, jby = 400, 30
    parts.append(sym_inst("JST_XH_7P", "J_BAL",
                          "JST XH-7P 2.54mm 6S balance lead", jbx, jby))
    # Pins: 1=BAL_GND, 2=B1, 3=B2, 4=B3, 5=B4, 6=B5, 7=B6
    bal_nets = ["BAL_GND_J", "B1", "B2", "B3", "B4", "B5", "B6"]
    pin_ys   = [-7.62, -5.08, -2.54, 0.00, 2.54, 5.08, 7.62]
    for i, (net, py) in enumerate(zip(bal_nets, pin_ys), start=1):
        parts.append(glabel(net, jbx + 2.54, jby + py, rot=0))

    # Balance series resistors 100Ω (R_BALn) between J_BAL pins and BQ76930
    for i in range(1, 7):
        net_in  = f"B{i}"
        net_out = f"VC{i}_R"
        rx, ry  = 420, jby + (-7.62 + 5.08 + (i - 1) * 2.54)
        parts.append(sym_inst("R_Generic", f"R_BAL{i}",
                              "100R 0402 balance lead protection resistor", rx, ry, dnp=False))
        parts.append(glabel(net_in,  rx - 2.54, ry, rot=180))
        parts.append(glabel(net_out, rx + 2.54, ry, rot=0))

    # U_CELL — BQ76930
    ucx, ucy = 480, 85
    parts.append(sym_inst("BQ76930PWRQ1", "U_CELL",
                          "BQ76930PWRQ1 6S cell monitor + HW protection", ucx, ucy))
    parts.append(glabel("BAL_GND_J",  ucx - 15.24, ucy - 15.24, rot=180))  # VC0
    for i in range(1, 7):
        py_off = -15.24 + i * 2.54
        parts.append(glabel(f"VC{i}_R",    ucx - 15.24, ucy + (-12.70 + (i - 1) * 2.54), rot=180))
    parts.append(pwr_sym("PGND",      ucx - 15.24, ucy + 2.54,   rot=0))   # BAL_GND (reg GND)
    # TS1 — thermistor
    parts.append(glabel("NTC_P",      ucx - 15.24, ucy + 5.08,   rot=180))
    # REGSRC
    parts.append(pwr_sym("VBAT",      ucx - 15.24, ucy + 7.62,   rot=0))
    # CAP — boot cap
    parts.append(glabel("BQ_CAP",     ucx - 15.24, ucy + 10.16,  rot=180))
    # GND
    parts.append(pwr_sym("PGND",      ucx - 15.24, ucy + 12.70,  rot=0))
    # BAT+ (pack reference)
    parts.append(pwr_sym("VBAT",      ucx + 15.24, ucy - 15.24,  rot=180))
    # SDA/SCL
    parts.append(glabel("PDB_SDA",    ucx + 15.24, ucy - 12.70,  rot=0))
    parts.append(glabel("PDB_SCL",    ucx + 15.24, ucy - 10.16,  rot=0))
    # ALERT_N
    parts.append(glabel("PDB_ALERT_N", ucx + 15.24, ucy - 7.62,  rot=0))
    # DSG gate
    parts.append(glabel("BQ_DSG_OUT", ucx + 15.24, ucy - 5.08,   rot=0))
    # CHG gate — no-connect (DNP charge FET path)
    parts.append(nc(ucx + 15.24, ucy - 2.54))

    # BQ76930 support passives
    # C_CAP — 4.7µF boot capacitor
    parts.append(sym_inst("C_Generic", "C_CAP", "4.7uF X7R 0603 BQ76930 boot cap", 455, 95))
    parts.append(glabel("BQ_CAP",  455 - 2.54, 95, rot=180))
    parts.append(pwr_sym("VBAT",   455 + 2.54, 95, rot=180))

    # J_NTC — JST-GH 2-pin thermistor connector
    parts.append(sym_inst("Conn_JST_GH_02P", "J_NTC",
                          "JST-GH 2P 1.25mm battery NTC thermistor input", 455, 115))
    parts.append(glabel("NTC_P",   455 + 2.54, 115 - 1.27, rot=0))
    parts.append(pwr_sym("PGND",   455 + 2.54, 115 + 1.27, rot=180))

    parts.append(sym_inst("M3_ChassisPad", "J_SHLD_NTC", "PGND via-pad NTC cable shield", 455, 128))
    parts.append(pwr_sym("PGND", 455 - 2.54, 128, rot=0))

    # C_NTC — 100nF TS1 filter
    parts.append(sym_inst("C_Generic", "C_NTC", "100nF X7R 0805 BQ76930 TS1 filter", 468, 115))
    parts.append(glabel("NTC_P",   468 - 2.54, 115, rot=180))
    parts.append(pwr_sym("PGND",   468 + 2.54, 115, rot=180))

    # -----------------------------------------------------------------------
    # Section G: Signal Interface  (x=540..610, y=30..120)
    # -----------------------------------------------------------------------
    parts.append(text_note("=== Section G: I2C Interface, TVS, Alert, Connectors ===", 538, 15))

    # D_I2C — PRTR5V0U2X dual TVS for I2C protection
    parts.append(sym_inst("PRTR5V0U2X", "D_I2C",
                          "NXP PRTR5V0U2X Dual TVS 5V clamp I2C RF protection", 555, 35))
    parts.append(pwr_sym("PGND",       555 - 7.62, 35 - 2.54, rot=0))
    parts.append(glabel("PDB_SDA_RAW", 555 - 7.62, 35,         rot=180))
    parts.append(glabel("PDB_SCL_RAW", 555 - 7.62, 35 + 2.54, rot=180))
    parts.append(pwr_sym("+5V",        555 + 7.62, 35 - 2.54, rot=180))
    parts.append(nc(555 + 7.62, 35))                             # D2A — unused second diode anode
    parts.append(glabel("PDB_SDA",     555 + 7.62, 35 + 2.54, rot=0))

    # Short wire: PDB_SDA_RAW == PDB_SDA at this device boundary
    # (The TVS routes PDB_SDA through D_I2C; both labels used at ports)
    # Tie SCL through similarly
    parts.append(glabel("PDB_SCL_RAW", 548, 45, rot=180))
    parts.append(glabel("PDB_SCL",     552, 45, rot=0))

    # R_ALERT — 2.2kΩ pull-up for ALERT_N bus
    parts.append(sym_inst("R_Generic", "R_ALERT", "2.2k 0402 ALERT pull-up to +5V", 570, 50))
    parts.append(pwr_sym("+5V",         570 - 2.54, 50, rot=0))
    parts.append(glabel("PDB_ALERT_N",  570 + 2.54, 50, rot=0))

    # J_I2C — JST-GH 4-pin to Wash/Shepherd Bay A
    parts.append(sym_inst("Conn_JST_GH_04P", "J_I2C",
                          "JST-GH SM04B-GHS-TB 4P 1.25mm PDB I2C to FC1", 590, 38))
    parts.append(pwr_sym("PGND",        590 + 2.54, 38 - 3.81, rot=180))
    parts.append(pwr_sym("+5V",         590 + 2.54, 38 - 1.27, rot=0))
    parts.append(glabel("PDB_SCL",      590 + 2.54, 38 + 1.27, rot=0))
    parts.append(glabel("PDB_SDA",      590 + 2.54, 38 + 3.81, rot=0))

    parts.append(sym_inst("M3_ChassisPad", "J_SHLD_I2C", "PGND via-pad I2C cable shield", 590, 52))
    parts.append(pwr_sym("PGND", 590 - 2.54, 52, rot=0))

    # J_ALERT — JST-GH 2-pin ALERT output to Wash GPIO
    parts.append(sym_inst("Conn_JST_GH_02P", "J_ALERT",
                          "JST-GH SM02B-GHS-TB 2P 1.25mm ALERT to Wash GPIO", 590, 65))
    parts.append(pwr_sym("PGND",        590 + 2.54, 65 - 1.27, rot=180))
    parts.append(glabel("PDB_ALERT_N",  590 + 2.54, 65 + 1.27, rot=0))

    parts.append(sym_inst("M3_ChassisPad", "J_SHLD_ALERT", "PGND via-pad ALERT cable shield", 590, 75))
    parts.append(pwr_sym("PGND", 590 - 2.54, 75, rot=0))

    # -----------------------------------------------------------------------
    # Compose schematic
    # -----------------------------------------------------------------------
    sch = ['(kicad_sch (version 20240101) (generator eeschema)',
           '  (paper "A1")',
           '  (title_block',
           '    (title "Kaylee — EMI-Hardened Power Distribution Board")'
           ' (date "2026-06-10") (rev "A") (company "Griffing Technology LLC")',
           '    (comment 1 "Serenity UAV Power Distribution Board — 90x65mm 4-layer FR4-TG170")',
           '    (comment 2 "Copyright 2026 Steve Griffing PE(CSE) CISSP-ISSEP CPP |'
           ' Griffing Technology LLC")',
           '    (comment 3 "License: CC BY 4.0  |  creativecommons.org/licenses/by/4.0")',
           '    (comment 4 "Approved:                               Checked:")',
           '  )',
           ]
    sch.extend(parts)
    sch.append(')')
    return '\n'.join(sch)


# ---------------------------------------------------------------------------
# kicad_pcb
# ---------------------------------------------------------------------------

def gen_pcb() -> str:
    """90x65mm 4-layer PCB stub with correct stackup, outline, and mounting holes."""

    W, H = 90.0, 65.0   # board dimensions mm
    MH_D = 3.2           # M3 mounting hole drill diameter mm
    MH_OD = 6.0          # annular ring OD mm
    MH_MARGIN = 4.0      # hole centre from board edge mm

    mh_coords = [
        (MH_MARGIN,     MH_MARGIN),
        (W - MH_MARGIN, MH_MARGIN),
        (MH_MARGIN,     H - MH_MARGIN),
        (W - MH_MARGIN, H - MH_MARGIN),
    ]

    lines = [
        '(kicad_pcb',
        '\t(version 20241229)',
        '\t(generator "pcbnew")',
        '\t(generator_version "9.0")',
        '\t(general',
        '\t\t(thickness 1.6)',
        '\t\t(legacy_teardrops no)',
        '\t)',
        '\t(paper "A4")',
        '\t(title_block',
        '\t\t(title "Kaylee")',
        '\t\t(date "2026-06-10")',
        '\t\t(rev "A")',
        '\t\t(comment 1 "Serenity-Class Tiltrotor UAV — Power Distribution Board")',
        '\t\t(comment 2 "CC BY 4.0 creativecommons.org/licenses/by/4.0")',
        '\t\t(comment 3 "90x65mm 4-layer FR4-TG170  4oz Cu on F.Cu/In2.Cu  1oz on In1.Cu/B.Cu")',
        '\t\t(comment 4 "JLCPCB / PCBWay: 4-oz copper inner planes; ENIG; no V-score")',
        '\t)',
        '\t(layers',
        '\t\t(0 "F.Cu" signal)',
        '\t\t(4 "In1.Cu" power)',       # GND plane (1 oz)
        '\t\t(6 "In2.Cu" power)',       # VBAT plane (4 oz)
        '\t\t(2 "B.Cu" signal)',
        '\t\t(13 "F.Paste" user)',
        '\t\t(15 "B.Paste" user)',
        '\t\t(5 "F.SilkS" user "F.Silkscreen")',
        '\t\t(7 "B.SilkS" user "B.Silkscreen")',
        '\t\t(1 "F.Mask" user)',
        '\t\t(3 "B.Mask" user)',
        '\t\t(25 "Edge.Cuts" user)',
        '\t\t(27 "Margin" user)',
        '\t\t(31 "F.CrtYd" user "F.Courtyard")',
        '\t\t(29 "B.CrtYd" user "B.Courtyard")',
        '\t\t(35 "F.Fab" user)',
        '\t\t(33 "B.Fab" user)',
        '\t)',
        '\t(setup',
        '\t\t(pad_to_mask_clearance 0)',
        '\t\t(allow_soldermask_bridges_in_footprints no)',
        '\t\t(tenting front back)',
        '\t)',
        # Board outline on Edge.Cuts
        f'\t(gr_rect (start 0 0) (end {W} {H})',
        f'\t\t(stroke (width 0.05) (type default)) (layer "Edge.Cuts")',
        f'\t\t(uuid "{_next_uid()}"))',
        # Fab-layer board reference text
        f'\t(gr_text "Kaylee Rev A" (at {W/2:.2f} {H + 2.5:.2f} 0) (layer "F.Fab")',
        f'\t\t(effects (font (size 1.5 1.5) (thickness 0.15)))',
        f'\t\t(uuid "{_next_uid()}"))',
        f'\t(gr_text "Griffing Technology LLC | CC BY 4.0" (at {W/2:.2f} {H + 5.0:.2f} 0)'
        ' (layer "F.Fab")',
        f'\t\t(effects (font (size 1.0 1.0) (thickness 0.1)))',
        f'\t\t(uuid "{_next_uid()}"))',
    ]

    # 4 M3 mounting holes (NPTH)
    for i, (mx, my) in enumerate(mh_coords):
        lines += [
            f'\t(footprint "MountingHole:MountingHole_3.2mm_M3_Pad_Via" (layer "F.Cu")',
            f'\t\t(at {mx} {my})',
            f'\t\t(property "Reference" "H{i+1}" (at {mx} {my - 3:.1f} 0)',
            f'\t\t\t(layer "F.Fab") (effects (font (size 1.0 1.0))))',
            f'\t\t(pad "" np_thru_hole circle (at 0 0) (size {MH_OD} {MH_OD})'
            f' (drill {MH_D}) (layers "*.Cu" "*.Mask"))',
            f'\t)',
        ]

    # Basic net declarations (key signal nets; full list populated by Pcbnew from SCH)
    key_nets = [
        "", "VBAT", "PGND", "VDIS", "+5V", "+6V", "5V_AVIONICS", "6V_SERVO",
        "PDB_SDA", "PDB_SCL", "PDB_ALERT_N", "DSG_GATE", "BQ_DSG_OUT",
        "ESC1_RS_OUT", "ESC2_RS_OUT", "ESC3_RS_OUT", "ESC4_RS_OUT", "ESC5_RS_OUT",
        "CHASSIS",
    ]
    for i, net in enumerate(key_nets):
        lines.append(f'\t(net {i} "{net}")')

    lines.append(')')
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    out = {
        "Kaylee.kicad_pro": gen_pro(),
        "Kaylee.kicad_sch": gen_sch(),
        "Kaylee.kicad_pcb": gen_pcb(),
    }
    for fname, content in out.items():
        path = here / fname
        path.write_text(content, encoding="utf-8")
        print(f"  Written: {path}  ({len(content):,} bytes)")
    print("Done.")
