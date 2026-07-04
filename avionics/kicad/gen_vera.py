#!/usr/bin/env python3
"""
gen_vera.py — Vera (nose/cargo-bay Vision, ToF & Laser board) KiCad generator

Outputs to avionics/kicad/:
    Vera.kicad_pro  (project + net classes)
    Vera.kicad_sch  (schematic, A2, v20240101)

Vera is a STANDALONE board, not a PocketBeagle 2 Industrial cape — it does not use the
P1+P2 header stack. It connects to the rest of the airframe only via shielded JST-GH
connectors (Ethernet ring in/out, CAN-FD trunk) and has its own 5V power input.

Reference: avionics/CLAUDE.md "Vera" section; REFERENCES.md Part XII
(REF-SENSOR-002 .. REF-SENSOR-006).

IMPORTANT — verification status (do not treat as fab-ready without addressing these):
    - U1 (TI AM62A7), U2 (KSZ9477), U3 (MSPM0G3507), U5 (SLB9670), U_PMIC (TPS65219) all
      use a SIMPLIFIED schematic symbol / "2-row placeholder" PCB footprint. Real BODY
      sizes are verified (18x18mm BGA, 14x14mm TQFP, VSSOP-28 7.1x4.9mm, VQFN-32 5x5mm x2
      respectively — see each SIZE constant's comment), but exact pin NUMBERS are still
      placeholder sequences, not cross-checked against real datasheets. Logical signal
      names on every net are correct; pin numbers are not. See TODO.md §1.2c.
    - EMI hardening chain (added 2026-07-03, matching Wash/Zoe Rev R baseline) uses REAL,
      already-verified parts and pinouts reused from this project's own working
      gen_cape_a2.py: Wurth 749010012A magnetics (8-pin, real footprint), Bourns
      SRF2012-100Y common-mode choke (4-pin, real footprint), Nexperia PRTR5V0U2X TVS
      (3-pin per instance, real footprint), TI ISOW1044BDFMR isolated CAN-FD transceiver (real
      SOIC-16W footprint, same part Wash/Zoe use). These are NOT placeholders.
    - Q1 (AO3400) pinout IS the real, standard datasheet pinout for that part.

Author: Steve Griffing PE(CSE) CISSP-ISSEP CPP  |  CC BY 4.0
Usage:  python3 gen_vera.py   (run from any dir)
"""

import uuid
from pathlib import Path

# ---------------------------------------------------------------------------
# Deterministic UUID helpers
# ---------------------------------------------------------------------------
_NS = uuid.UUID("7e5a0000-0000-0000-0000-000000000000")

_uid_i = [0]


def _next_uid() -> str:
    _uid_i[0] += 1
    val = _uid_i[0]
    h = f"{val:032x}"
    return f"7e5a{h[4:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


# ---------------------------------------------------------------------------
# kicad_pro  (adapted from gen_kaylee.py gen_pro(); Vera-specific net classes)
# ---------------------------------------------------------------------------
def gen_pro() -> str:
    import json

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
                        "units_format": 0,
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
                    "zones": {"min_clearance": 0.2},
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
                    "zones_intersect": "error",
                },
                "rules": {
                    "clearance": 0.127,
                    "max_error": 0.005,
                    "min_clearance": 0.0,
                    "min_connection": 0.0,
                    "min_copper_edge_clearance": 0.2,
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
                    "min_track_width": 0.127,
                    "min_via_annular_width": 0.1,
                    "min_via_diameter": 0.4,
                    "solder_mask_clearance": 0.0,
                    "solder_mask_min_width": 0.0,
                    "solder_mask_to_copper_clearance": 0.0,
                    "use_height_for_length_calcs": True,
                },
                "track_widths": [0.127, 0.15, 0.2, 0.25, 0.3, 0.5, 1.0],
                "via_dimensions": [
                    {"diameter": 0.6, "drill": 0.3},
                    {"diameter": 0.8, "drill": 0.4},
                ],
                "zones_allow_external_fillets": False,
                "zones_min_antigap_margin": 0.0,
            },
            "ipc2581": {
                "dist": "",
                "distpn": "",
                "internal_id": "",
                "mfg": "",
                "mpn": "",
            },
            "layer_pairs": [],
            "layer_presets": [],
            "viewports": [],
        },
        "boards": [],
        "cvpcb": {"equivalence_files": []},
        "erc": {
            "erc_exclusions": [],
            "meta": {"version": 0},
            "pin_map": [],
            "rule_severities": [],
        },
        "libraries": {"pinned_footprint_libs": [], "pinned_symbol_libs": []},
        "meta": {"filename": "Vera.kicad_pro", "version": 3},
        "net_settings": {
            "classes": [
                {
                    "bus_width": 12,
                    "clearance": 0.127,
                    "diff_pair_gap": 0.15,
                    "diff_pair_via_gap": 0.15,
                    "diff_pair_width": 0.2,
                    "line_style": 0,
                    "microvia_diameter": 0.3,
                    "microvia_drill": 0.1,
                    "name": "Default",
                    "pcb_color": "rgba(0, 0, 0, 0.000)",
                    "priority": 2147483647,
                    "schematic_color": "rgba(0, 0, 0, 0.000)",
                    "track_width": 0.2,
                    "via_diameter": 0.6,
                    "via_drill": 0.3,
                    "wire_width": 6,
                },
                {
                    "clearance": 0.2,
                    "name": "POWER_5V",
                    "pcb_color": "rgba(0, 0, 0, 0.000)",
                    "priority": 1,
                    "schematic_color": "rgba(0, 0, 0, 0.000)",
                    "track_width": 0.4,
                    "via_diameter": 0.8,
                    "via_drill": 0.4,
                },
                {
                    "clearance": 0.2,
                    "name": "PGND",
                    "pcb_color": "rgba(0, 0, 0, 0.000)",
                    "priority": 0,
                    "schematic_color": "rgba(0, 0, 0, 0.000)",
                    "track_width": 0.4,
                    "via_diameter": 0.8,
                    "via_drill": 0.4,
                },
                {
                    "clearance": 0.15,
                    "diff_pair_gap": 0.15,
                    "diff_pair_width": 0.15,
                    "name": "ETH_DIFF_100R",
                    "pcb_color": "rgba(0, 0, 0, 0.000)",
                    "priority": 2,
                    "schematic_color": "rgba(0, 0, 0, 0.000)",
                    "track_width": 0.15,
                    "via_diameter": 0.6,
                    "via_drill": 0.3,
                },
                {
                    "clearance": 0.15,
                    "diff_pair_gap": 0.2,
                    "diff_pair_width": 0.2,
                    "name": "CANFD_DIFF_120R",
                    "pcb_color": "rgba(0, 0, 0, 0.000)",
                    "priority": 2,
                    "schematic_color": "rgba(0, 0, 0, 0.000)",
                    "track_width": 0.2,
                    "via_diameter": 0.6,
                    "via_drill": 0.3,
                },
            ],
            "meta": {"version": 4},
            "net_colors": None,
            "netclass_assignments": None,
            "netclass_patterns": [
                {"netclass": "PGND", "pattern": "PGND"},
                {"netclass": "PGND", "pattern": "GND"},
                {"netclass": "POWER_5V", "pattern": "+5V*"},
                {"netclass": "POWER_5V", "pattern": "+3V3*"},
                {"netclass": "POWER_5V", "pattern": "VDD_CORE"},
                {"netclass": "ETH_DIFF_100R", "pattern": "ETH_IN_*"},
                {"netclass": "ETH_DIFF_100R", "pattern": "ETH_OUT_*"},
                {"netclass": "ETH_DIFF_100R", "pattern": "RGMII_*"},
                {"netclass": "CANFD_DIFF_120R", "pattern": "CANFD_*"},
            ],
        },
        "pcbnew": {
            "last_paths": {
                "gencad": "",
                "idf": "",
                "netlist": "",
                "plot": "",
                "pos_files": "",
                "specctra_dsn": "",
                "step": "",
                "svg": "",
                "vrml": "",
            },
            "page_layout_descr_file": "",
        },
        "schematic": {
            "annotate_start_num": 0,
            "bom_fmt_preset": "",
            "bom_fmt_settings": {
                "fields_ordered": [],
                "filter": "",
                "group_by": [],
                "sort_asc": True,
                "sort_field": "Reference",
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
                "text_offset_ratio": 0.08,
            },
            "legacy_lib_dir": "",
            "legacy_lib_list": [],
            "meta": {"version": 1},
            "net_format_name": "",
            "page_layout_descr_file": "",
            "plot_directory": "",
            "spice_current_sheet_as_root": False,
            "subpart_first_id": 65,
            "subpart_id_separator": 0,
        },
        "sheets": [["7e5a0000-0000-0000-0000-000000000001", ""]],
        "text_variables": {},
    }
    return json.dumps(pro, indent=2)


# ---------------------------------------------------------------------------
# kicad_sch low-level helpers (same conventions as gen_kaylee.py)
# ---------------------------------------------------------------------------


def _pin_def(ptype, shape, px, py, ang, length, name, number):
    return (
        f"      (pin {ptype} {shape} (at {px:.2f} {py:.2f} {ang}) (length {length:.2f})\n"
        f'        (name "{name}" (effects (font (size 1.016 1.016))))\n'
        f'        (number "{number}" (effects (font (size 1.016 1.016)))))'
    )


def _rect(x1, y1, x2, y2):
    return (
        f"      (rectangle (start {x1:.2f} {y1:.2f}) (end {x2:.2f} {y2:.2f})\n"
        f"        (stroke (width 0.254) (type default)) (fill (type background))))"
    )


def lib_symbol_2pin_h(name, in_bom="yes"):
    return (
        f"""  (symbol "{name}" (in_bom {in_bom}) (on_board yes)
    (property "Reference" "R" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{name}" (at 0 2.54 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "{name}_0_1"
      (rectangle (start -2.54 -1.27) (end 2.54 1.27)
        (stroke (width 0.254) (type default)) (fill (type background))))
    (symbol "{name}_1_1"
"""
        + _pin_def("passive", "line", -3.81, 0, 0, 1.27, "1", "1")
        + "\n"
        + _pin_def("passive", "line", 3.81, 0, 180, 1.27, "2", "2")
        + """
    )
  )"""
    )


def lib_symbol_nmos(name):
    """Generic 3-pin logic-level N-MOSFET SOT-23 symbol (G, D, S)."""
    return (
        f"""  (symbol "{name}" (in_bom yes) (on_board yes)
    (property "Reference" "Q" (at 0 -6.35 0) (effects (font (size 1.27 1.27))))
    (property "Value" "{name}" (at 0 6.35 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_TO_SOT_SMD:SOT-23" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "{name}_0_1"
      (rectangle (start -5.08 -5.08) (end 5.08 5.08)
        (stroke (width 0.254) (type default)) (fill (type background))))
    (symbol "{name}_1_1"
"""
        + _pin_def("input", "line", -7.62, 0, 0, 2.54, "G", "1")
        + "\n"
        + _pin_def("passive", "line", 2.54, 7.62, 270, 2.54, "D", "3")
        + "\n"
        + _pin_def("passive", "line", 2.54, -7.62, 90, 2.54, "S", "2")
        + """
    )
  )"""
    )


def lib_symbol_srf2012():
    """SRF2012-100Y — 100uH common-mode choke, 2-winding, 4-terminal.
    Reused verbatim (pin layout) from this project's own verified Wash/Zoë
    generator (gen_cape_a2.py lib_sym_srf2012) — real, already-working part."""
    return (
        """  (symbol "SRF2012-100Y" (in_bom yes) (on_board yes)
    (property "Reference" "CMC" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
    (property "Value" "SRF2012-100Y" (at 0 5.08 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Inductor_SMD:L_Taiyo-Yuden_NR-20xx" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://www.coilcraft.com/getmedia/3a436de1-46ad-49b9-b3a8-9a3faa3ecf61/srf2012.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "SRF2012-100Y_0_1"
      (rectangle (start -5.08 -3.81) (end 5.08 3.81)
        (stroke (width 0.254) (type default)) (fill (type background)))
      (polyline (pts (xy -1.27 -3.81) (xy -1.27 3.81))
        (stroke (width 0.127) (type dash)) (fill (type none)))
      (polyline (pts (xy 1.27 -3.81) (xy 1.27 3.81))
        (stroke (width 0.127) (type dash)) (fill (type none)))
    )
    (symbol "SRF2012-100Y_1_1"
"""
        + _pin_def("passive", "line", -7.62, -2.54, 0, 2.54, "L1A", "1")
        + "\n"
        + _pin_def("passive", "line", 7.62, -2.54, 180, 2.54, "L1B", "2")
        + "\n"
        + _pin_def("passive", "line", -7.62, 2.54, 0, 2.54, "L2A", "3")
        + "\n"
        + _pin_def("passive", "line", 7.62, 2.54, 180, 2.54, "L2B", "4")
        + """
    )
  )"""
    )


def lib_symbol_prtr5v0u2x():
    """PRTR5V0U2X — dual TVS/ESD array, SOT-363. Reused verbatim (pin layout)
    from this project's own verified Wash/Zoë generator (gen_cape_a2.py
    lib_sym_prtr5v0u2x). One instance protects one differential pair
    (A1/A2 = the two lines, K = common cathode to ground)."""
    return (
        """  (symbol "PRTR5V0U2X" (in_bom yes) (on_board yes)
    (property "Reference" "D" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))
    (property "Value" "PRTR5V0U2X" (at 0 5.08 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "Package_TO_SOT_SMD:SOT-363_SC-70-6" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "https://assets.nexperia.com/documents/data-sheet/PRTR5V0U2X.pdf" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "PRTR5V0U2X_0_1"
      (rectangle (start -5.08 -3.81) (end 5.08 3.81)
        (stroke (width 0.254) (type default)) (fill (type background))))
    (symbol "PRTR5V0U2X_1_1"
"""
        + _pin_def("passive", "line", -7.62, -2.54, 0, 2.54, "A1", "1")
        + "\n"
        + _pin_def("passive", "line", -7.62, 2.54, 0, 2.54, "A2", "2")
        + "\n"
        + _pin_def("passive", "line", 7.62, 0.0, 180, 2.54, "K", "3")
        + """
    )
  )"""
    )


def lib_symbol_conn_np(name, n, pin_names=None):
    """Generic N-pin single-row connector symbol (pins on left side)."""
    pin_names = pin_names or [str(i + 1) for i in range(n)]
    half = (n - 1) * 1.27
    lines = [
        f'  (symbol "{name}" (in_bom yes) (on_board yes)',
        f'    (property "Reference" "J" (at 0 {-(half + 3.81):.2f} 0) (effects (font (size 1.27 1.27))))',
        f'    (property "Value" "{name}" (at 0 {(half + 3.81):.2f} 0) (effects (font (size 1.27 1.27))))',
        f'    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        f'    (symbol "{name}_0_1"',
        f"      (rectangle (start -2.54 {-half - 1.27:.2f}) (end 2.54 {half + 1.27:.2f})",
        f"        (stroke (width 0.254) (type default)) (fill (type background))))",
        f'    (symbol "{name}_1_1"',
    ]
    for i in range(n):
        py = -half + i * 2.54
        lines.append(
            _pin_def("passive", "line", -5.08, py, 0, 2.54, pin_names[i], str(i + 1))
        )
    lines.append("    )")
    lines.append("  )")
    return "\n".join(lines)


def lib_symbol_generic_ic(name, footprint, datasheet, left, right, size=(15.24, 15.24)):
    """Generic multi-pin IC block: left=[(name,num,ptype)], right=[...]."""
    hx, hy = size
    n_l, n_r = len(left), len(right)
    top = max(n_l, n_r) * 1.27
    lines = [
        f'  (symbol "{name}" (in_bom yes) (on_board yes)',
        f'    (property "Reference" "U" (at 0 {-(top + 3.81):.2f} 0) (effects (font (size 1.27 1.27))))',
        f'    (property "Value" "{name}" (at 0 {(top + 3.81):.2f} 0) (effects (font (size 1.27 1.27))))',
        f'    (property "Footprint" "{footprint}" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        f'    (property "Datasheet" "{datasheet}" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        f'    (symbol "{name}_0_1"',
        f"      (rectangle (start {-hx:.2f} {-hy:.2f}) (end {hx:.2f} {hy:.2f})",
        f"        (stroke (width 0.254) (type default)) (fill (type background))))",
        f'    (symbol "{name}_1_1"',
    ]
    n = len(left)
    start_y = -((n - 1) * 2.54) / 2.0
    for i, (pname, pnum, ptype) in enumerate(left):
        py = start_y + i * 2.54
        lines.append(_pin_def(ptype, "line", -(hx + 2.54), py, 0, 2.54, pname, pnum))
    n = len(right)
    start_y = -((n - 1) * 2.54) / 2.0
    for i, (pname, pnum, ptype) in enumerate(right):
        py = start_y + i * 2.54
        lines.append(_pin_def(ptype, "line", hx + 2.54, py, 180, 2.54, pname, pnum))
    lines.append("    )")
    lines.append("  )")
    return "\n".join(lines)


def _ic_pin_xy(left, right, pin_name, size):
    """Compute the exact (dx, dy, side) offset of a named pin, using the
    identical placement math as lib_symbol_generic_ic — this is the single
    source of truth so glabels always land exactly on the pin they claim to
    wire, instead of a hand-guessed offset that may miss the real pin.

    NOTE: lib_symbols content uses a Y-up (Cartesian) coordinate convention
    internally, while the placed instance on the sheet uses Y-down — KiCad
    negates the local Y when mapping a rot=0 instance's pins onto the sheet.
    dy returned here is already sheet-space (i.e. pre-negated) so callers can
    just add it to the instance's placed cy directly."""
    hx, hy = size
    for lst, side in ((left, "L"), (right, "R")):
        n = len(lst)
        start_y = -((n - 1) * 2.54) / 2.0
        for i, (pname, pnum, ptype) in enumerate(lst):
            if pname == pin_name:
                local_py = start_y + i * 2.54
                dx = -(hx + 2.54) if side == "L" else (hx + 2.54)
                return (dx, -local_py, side)
    raise KeyError(f"pin {pin_name!r} not found in left={left!r} right={right!r}")


def glabel_pin(net_name, cx, cy, left, right, pin_name, size):
    """Place a glabel exactly on a named IC pin (see _ic_pin_xy)."""
    dx, dy, side = _ic_pin_xy(left, right, pin_name, size)
    rot = 180 if side == "L" else 0
    return glabel(net_name, cx + dx, cy + dy, rot=rot)


def pwr_pin(lib_id, cx, cy, left, right, pin_name, size):
    """Place a power symbol exactly on a named IC pin (rotation is cosmetic
    only — coincident (x, y) is what establishes the electrical connection)."""
    dx, dy, side = _ic_pin_xy(left, right, pin_name, size)
    return pwr_sym(lib_id, cx + dx, cy + dy, rot=0)


def _conn_pin_xy(n, idx0):
    """Exact (dx, dy) offset of pin index idx0 (0-based) on an n-pin
    lib_symbol_conn_np connector — matches that function's placement math.
    Same Y-up/Y-down sheet-mapping note as _ic_pin_xy applies; dy is
    pre-negated to sheet space."""
    half = (n - 1) * 1.27
    local_py = -half + idx0 * 2.54
    return (-5.08, -local_py)


def glabel_conn(net_name, cx, cy, n, idx0):
    """Place a glabel exactly on connector pin idx0 (0-based) of an n-pin
    lib_symbol_conn_np instance."""
    dx, dy = _conn_pin_xy(n, idx0)
    return glabel(net_name, cx + dx, cy + dy, rot=180)


def lib_sym_power(name, bar_top=True):
    ybox = -1.27 if bar_top else 1.27
    yend = 1.27 if bar_top else -1.27
    pin_angle = 270 if bar_top else 90
    pin_y = 1.27 if bar_top else -1.27
    return (
        f"""  (symbol "{name}" (power) (in_bom no) (on_board no)
    (property "Reference" "#PWR" (at 0 -3.81 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Value" "{name}" (at 0 {yend:.2f} 0) (effects (font (size 1.27 1.27))))
    (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))
    (symbol "{name}_0_1"
      (polyline (pts (xy -1.27 {ybox:.2f}) (xy 0 {yend:.2f}) (xy 1.27 {ybox:.2f}))
        (stroke (width 0) (type default)) (fill (type none))))
    (symbol "{name}_1_1"
"""
        + _pin_def("power_in", "line", 0.0, pin_y, pin_angle, 1.27, "~", "1")
        + """
  )
  )"""
    )


def sym_inst(lib_id, ref, value, cx, cy, rot=0, footprint="", datasheet=""):
    lines = [
        f'  (symbol (lib_id "{lib_id}") (at {cx:.2f} {cy:.2f} {rot})',
        f"    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)",
        f'    (uuid "{_next_uid()}")',
        f'    (property "Reference" "{ref}" (at {cx:.2f} {cy - 3.81:.2f} {rot})',
        f"      (effects (font (size 1.27 1.27))))",
        f'    (property "Value" "{value}" (at {cx:.2f} {cy + 3.81:.2f} {rot})',
        f"      (effects (font (size 1.27 1.27))))",
        f'    (property "Footprint" "{footprint}" (at 0 0 0)',
        f"      (effects (font (size 1.27 1.27)) (hide yes)))",
        f'    (property "Datasheet" "{datasheet}" (at 0 0 0)',
        f"      (effects (font (size 1.27 1.27)) (hide yes)))",
        "  )",
    ]
    return "\n".join(lines)


# bar_top-ness per power-flag lib_id — must match the lib_sym_power(...) calls
# in gen_sch()'s lib_symbols block. Needed to compensate pwr_sym's placement:
# the flag symbol's own pin sits at local offset (0, +-1.27), NOT at the symbol
# origin, so placing the origin at a target coordinate misses the real
# electrical connection point by 1.27mm unless compensated for here.
_PWR_BAR_TOP = {
    "+5V": True,
    "+3V3": True,
    "VDD_CORE": True,
    "VDDSHV": True,
    "VDDR": True,
    "GND": False,
    "PGND": False,
}


def pwr_sym(lib_id, tx, ty, rot=0):
    """Place a power symbol so its OWN PIN (not the symbol origin) lands
    exactly at the target connection point (tx, ty). Only rot in {0, 180} is
    supported (the only values used in this generator).

    NOTE: lib_symbols content is Y-up internally; KiCad negates local Y when
    placing a rot=0 instance on the (Y-down) sheet, and an ADDITIONAL 180
    degree instance rotation flips it back — see _ic_pin_xy for the same
    convention applied to IC pins."""
    bar_top = _PWR_BAR_TOP.get(lib_id, True)
    pin_y = 1.27 if bar_top else -1.27
    if rot == 180:
        cx, cy = tx, ty - pin_y
    else:
        cx, cy = tx, ty + pin_y
        rot = 0
    lines = [
        f'  (symbol (lib_id "{lib_id}") (at {cx:.2f} {cy:.2f} {rot})',
        f"    (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)",
        f'    (uuid "{_next_uid()}")',
        f'    (property "Reference" "#PWR" (at {cx:.2f} {cy:.2f} 0)',
        f"      (effects (font (size 1.27 1.27)) (hide yes)))",
        f'    (property "Value" "{lib_id}" (at {cx:.2f} {cy - 2.54:.2f} 0)',
        f"      (effects (font (size 1.27 1.27))))",
        f'    (property "Footprint" "" (at 0 0 0)',
        f"      (effects (font (size 1.27 1.27)) (hide yes)))",
        f'    (property "Datasheet" "" (at 0 0 0)',
        f"      (effects (font (size 1.27 1.27)) (hide yes)))",
        f'    (pin "1" (uuid "{_next_uid()}"))',
        "  )",
    ]
    return "\n".join(lines)


def glabel(name, x, y, rot=0, shape="bidirectional"):
    return (
        f'  (global_label "{name}" (shape {shape}) (at {x:.2f} {y:.2f} {rot})\n'
        f"    (effects (font (size 1.016 1.016)))\n"
        f'    (uuid "{_next_uid()}")\n'
        f'    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at {x:.2f} {y:.2f} 0)\n'
        f"      (effects (font (size 1.016 1.016)) (hide yes))))"
    )


def text_note(txt, x, y, size=1.27):
    # KiCad's S-expression string literals require the literal two-character
    # escape "\n", not an embedded raw newline — multi-line notes must be escaped.
    esc = txt.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return (
        f'  (text "{esc}" (at {x:.2f} {y:.2f} 0)\n'
        f"    (effects (font (size {size:.2f} {size:.2f})))\n"
        f'    (uuid "{_next_uid()}"))'
    )


# ---------------------------------------------------------------------------
# Component pin-list constants — single source of truth for BOTH the
# lib_symbol definitions and the exact glabel/pwr_sym wiring offsets
# (glabel_pin / pwr_pin above compute the real coordinate from these lists,
# instead of the schematic body guessing an offset that might miss the pin).
# ---------------------------------------------------------------------------

# Sizes below are REAL body half-extents (verified via TI/Microchip/Infineon/TI
# datasheets and product pages, 2026-07-03) even though the footprints
# themselves remain the deliberate "2-row placeholder" (see gen_vera_pcb.py
# docstring) — real pin NUMBERS are still not verified, only body size is.
AM62A_SIZE = (9.0, 9.0)  # AM62A7: 18x18mm 484-ball FCBGA/FCCSP (AMB/ANF package)
AM62A_L = [
    ("VDD_CORE", "A1", "power_in"),
    ("VDDSHV_MAIN", "A2", "power_in"),
    ("VDDR_CORE", "A3", "power_in"),
    ("GND", "A4", "power_in"),
    ("PORz", "B1", "input"),
    ("BOOT_MODE0", "B2", "input"),
    ("CAM_I2C_SDA", "C1", "bidirectional"),
    ("CAM_I2C_SCL", "C2", "input"),
    ("CAM_RESET_N", "C3", "output"),
    ("CAM_PWDN", "C4", "output"),
    ("CSI_CLK_P", "D1", "input"),
    ("CSI_CLK_N", "D2", "input"),
    ("CSI_D0_P", "D3", "input"),
    ("CSI_D0_N", "D4", "input"),
]
AM62A_R = [
    ("RGMII1_TXC", "P1", "output"),
    ("RGMII1_TXCTL", "P2", "output"),
    ("RGMII1_TXD0", "P3", "output"),
    ("RGMII1_RXC", "P4", "input"),
    ("RGMII1_RXCTL", "P5", "input"),
    ("RGMII1_RXD0", "P6", "input"),
    ("MDIO", "P7", "bidirectional"),
    ("MDC", "P8", "output"),
    ("MCU_UART_TX", "R1", "output"),
    ("MCU_UART_RX", "R2", "input"),
    ("SD_CARD", "R3", "bidirectional"),
]

MSPM0_SIZE = (3.55, 2.45)  # MSPM0G3507 VSSOP-28 (DGS): real body ~7.1x4.9mm
MSPM0_L = [
    ("+3V3", "1", "power_in"),
    ("GND", "2", "power_in"),
    ("NRST", "3", "input"),
    ("SWCLK", "4", "input"),
    ("SWDIO", "5", "bidirectional"),
    ("MCAN_TX", "6", "output"),
    ("MCAN_RX", "7", "input"),
    ("UART0_TX", "8", "output"),
    ("UART0_RX", "9", "input"),
    ("UART1_TX", "22", "output"),
    ("UART1_RX", "23", "input"),
]
MSPM0_R = [
    ("SPI0_CS_TPM", "10", "output"),
    ("SPI0_SCK", "11", "output"),
    ("SPI0_MOSI", "12", "output"),
    ("SPI0_MISO", "13", "input"),
    ("TPM_PIRQ", "14", "input"),
    ("SPI1_CS_SW", "15", "output"),
    ("SPI1_SCK", "16", "output"),
    ("SPI1_MOSI", "17", "output"),
    ("SPI1_MISO", "18", "input"),
    ("GPIO_LASER_EN", "19", "output"),
    ("GPIO_LASER_KEY", "20", "input"),
    ("GPIO_LASER_IND", "21", "output"),
]

KSZ_SIZE = (7.0, 7.0)  # KSZ9477STXI: 128-TQFP-EP, real body 14x14mm
KSZ_L = [
    ("+3V3", "1", "power_in"),
    ("+1V2", "2", "power_in"),
    ("GND", "3", "power_in"),
    ("RESET_N", "4", "input"),
    ("INT_N", "5", "output"),
    ("XTAL_25M", "6", "input"),
    ("SPI_CS_HOST", "7", "input"),
    ("SPI_SCK_HOST", "8", "input"),
    ("SPI_MOSI_HOST", "9", "input"),
    ("SPI_MISO_HOST", "10", "output"),
]
# Each integrated-PHY port needs a FULL differential pair set (TX+/-, RX+/-) —
# a single MDIP/MDIN pair (as an earlier pass of this file had) under-models a
# real 10/100BASE-TX port, which needs both pairs. Fixed 2026-07-03 alongside
# adding the magnetics/CMC/TVS EMI-hardening chain those pairs feed into.
KSZ_R = [
    ("P1_RGMII_TXC", "20", "input"),
    ("P1_RGMII_TXCTL", "21", "input"),
    ("P1_RGMII_TXD0", "22", "input"),
    ("P1_RGMII_RXC", "23", "output"),
    ("P1_RGMII_RXCTL", "24", "output"),
    ("P1_RGMII_RXD0", "25", "output"),
    ("P2_TXP", "26", "output"),
    ("P2_TXN", "27", "output"),
    ("P2_RXP", "28", "input"),
    ("P2_RXN", "29", "input"),
    ("P3_TXP", "30", "output"),
    ("P3_TXN", "31", "output"),
    ("P3_RXP", "32", "input"),
    ("P3_RXN", "33", "input"),
]

TPM_SIZE = (2.5, 2.5)  # Infineon SLB9670: PG-VQFN-32, real body ~5x5mm
TPM_L = [
    ("+3V3", "1", "power_in"),
    ("GND", "2", "power_in"),
    ("SPI_CS", "3", "input"),
    ("SPI_CLK", "4", "input"),
]
TPM_R = [
    ("SPI_MOSI", "5", "input"),
    ("SPI_MISO", "6", "output"),
    ("PIRQ", "7", "output"),
    ("RESET_N", "8", "input"),
]

PMIC_SIZE = (2.5, 2.5)  # TI TPS65219: VQFN-32 (RSM), real body 5x5mm
PMIC_L = [
    ("VIN", "1", "power_in"),
    ("GND", "2", "power_in"),
    ("EN", "3", "input"),
    ("I2C_SDA", "4", "bidirectional"),
    ("I2C_SCL", "5", "input"),
]
PMIC_R = [
    ("BUCK1_VDD_CORE", "10", "output"),
    ("BUCK2_VDDSHV", "11", "output"),
    ("BUCK3_VDDR", "12", "output"),
    ("LDO1_3V3_CTRL", "13", "output"),
]

# --- EMI-hardening chain parts — reusing this project's OWN already-verified
# symbols/footprints from gen_cape_a2.py (Wash) rather than re-deriving new
# ones, so Vera's hardening matches the project's real, working Rev R baseline
# (not the fabricated HX1188NL/generic-TVS claims from the original AI brainstorm).

# TI ISOW1044BDFMR — isolated CAN-FD transceiver, SOIC-16W, replaces the
# non-isolated TCAN1042HG-Q1 to match Wash/Zoë's CAN-FD isolation standard.
ISOW_SIZE = (3.75, 5.15)  # SOIC-16W_7.5x10.3mm — real, from Wash's own footprint
ISOW_L = [
    ("GND1", "1", "power_in"),
    ("TXD", "2", "input"),
    ("STB_N", "3", "input"),
    ("RXD", "4", "output"),
    ("VCC1", "6", "power_in"),
]
ISOW_R = [
    ("ISOGND", "10", "power_in"),
    ("CANL", "14", "bidirectional"),
    ("CANH", "15", "bidirectional"),
    ("VCC2", "11", "power_in"),
]

# Wurth 749010012A — 10/100BASE-TX SMD transformer w/ integrated CMC, real
# 8-pin part already used on Wash/Zoë (TODO.md's "HX1188NL" reference for this
# role was stale/incorrect — the actual working generator uses this part).
XFMR_SIZE = (5.5, 4.0)  # estimated typical low-profile 10/100 SMD transformer body
XFMR_L = [
    ("PHY_TXP", "1", "input"),
    ("PHY_TXN", "2", "input"),
    ("PHY_RXP", "3", "output"),
    ("PHY_RXN", "4", "output"),
]
XFMR_R = [
    ("LINE_TXP", "5", "output"),
    ("LINE_TXN", "6", "output"),
    ("LINE_RXP", "7", "input"),
    ("LINE_RXN", "8", "input"),
]

# SRF2012-100Y and PRTR5V0U2X modeled through the same lib_symbol_generic_ic
# + glabel_pin/pwr_pin mechanism as every other part in this file, specifically
# to avoid re-introducing the lib_symbol Y-up/Y-down flip bug that a hand-wired
# version of this exact chain hit once already in this session (glabels placed
# at un-flipped local pin coordinates landed on the WRONG physical pin).
CMC_SIZE = (
    1.0,
    0.6,
)  # Bourns SRF2012-100Y: real body ~2.0x1.2mm (2012 metric); half-extent
CMC_L = [("L1A", "1", "passive"), ("L2A", "3", "passive")]
CMC_R = [("L1B", "2", "passive"), ("L2B", "4", "passive")]

TVS_SIZE = (
    1.05,
    0.625,
)  # Nexperia PRTR5V0U2X: real body ~2.1x1.25mm (SOT-363/SC-70-6); half-extent
TVS_L = [("A1", "1", "passive"), ("A2", "2", "passive")]
TVS_R = [("K", "3", "passive")]


# ---------------------------------------------------------------------------
# kicad_sch body
# ---------------------------------------------------------------------------


def gen_sch() -> str:
    parts = []

    # -------------------------------------------------------------------
    # lib_symbols
    # -------------------------------------------------------------------
    lib = [
        "  (lib_symbols",
        lib_symbol_2pin_h("C_Generic"),
        lib_symbol_2pin_h("R_Generic"),
        lib_symbol_nmos("AO3400"),
        lib_symbol_conn_np("Conn_JST_GH_02P", 2, ["1", "2"]),
        lib_symbol_conn_np("Conn_JST_GH_04P", 4, ["1", "2", "3", "4"]),
        lib_symbol_conn_np("Conn_JST_GH_05P", 5, ["1", "2", "3", "4", "5"]),
        lib_symbol_conn_np("Conn_JST_SH_02P", 2, ["1", "2"]),
        lib_symbol_generic_ic(
            "TI_AM62A7",
            "Vera:BGA484_23x23mm_P1mm_PLACEHOLDER",
            "https://www.ti.com/lit/ds/symlink/am62a7.pdf",
            left=AM62A_L,
            right=AM62A_R,
            size=AM62A_SIZE,
        ),
        lib_symbol_generic_ic(
            "TI_MSPM0G3507",
            "Package_DFN_QFN:VQFN-48_PLACEHOLDER_7x7mm_P0.5mm",
            "https://www.ti.com/lit/ds/symlink/mspm0g3507.pdf",
            left=MSPM0_L,
            right=MSPM0_R,
            size=MSPM0_SIZE,
        ),
        lib_symbol_generic_ic(
            "MICROCHIP_KSZ9477",
            "Vera:QFN128_PLACEHOLDER_16x16mm_P0.4mm",
            "https://www.microchip.com/en-us/product/ksz9477",
            left=KSZ_L,
            right=KSZ_R,
            size=KSZ_SIZE,
        ),
        lib_symbol_generic_ic(
            "TI_ISOW1044BDFMR",
            "Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm",
            "https://www.ti.com/lit/ds/sllseo9/sllseo9.pdf",
            left=ISOW_L,
            right=ISOW_R,
            size=ISOW_SIZE,
        ),
        lib_symbol_generic_ic(
            "WURTH_ETH_XFMR",
            "Transformer_SMD:Wurth_749010012A_10-100BASE-TX",
            "https://www.we-online.com/catalog/datasheet/749010012A.pdf",
            left=XFMR_L,
            right=XFMR_R,
            size=XFMR_SIZE,
        ),
        lib_symbol_generic_ic(
            "BOURNS_SRF2012_100Y",
            "Inductor_SMD:L_Taiyo-Yuden_NR-20xx",
            "https://www.coilcraft.com/getmedia/3a436de1-46ad-49b9-b3a8-9a3faa3ecf61/srf2012.pdf",
            left=CMC_L,
            right=CMC_R,
            size=CMC_SIZE,
        ),
        lib_symbol_generic_ic(
            "NEXPERIA_PRTR5V0U2X",
            "Package_TO_SOT_SMD:SOT-363_SC-70-6",
            "https://assets.nexperia.com/documents/data-sheet/PRTR5V0U2X.pdf",
            left=TVS_L,
            right=TVS_R,
            size=TVS_SIZE,
        ),
        lib_symbol_generic_ic(
            "INFINEON_SLB9670",
            "Vera:TPM_SLB9670_PLACEHOLDER",
            "https://www.infineon.com/dgdl/Infineon-SLB9670-DataSheet.pdf",
            left=TPM_L,
            right=TPM_R,
            size=TPM_SIZE,
        ),
        lib_symbol_generic_ic(
            "TI_TPS65219",
            "Vera:PMIC_TPS65219_PLACEHOLDER_WQFN32",
            "https://www.ti.com/lit/ds/symlink/tps65219.pdf",
            left=PMIC_L,
            right=PMIC_R,
            size=PMIC_SIZE,
        ),
        lib_sym_power("+5V"),
        lib_sym_power("+3V3"),
        lib_sym_power("VDD_CORE"),
        lib_sym_power("VDDSHV"),
        lib_sym_power("VDDR"),
        lib_sym_power("GND", bar_top=False),
        lib_sym_power("PGND", bar_top=False),
        "  )",
    ]
    parts.extend(lib)

    parts.append(
        text_note(
            "VERA — Nose/Cargo-Bay Vision, ToF & Laser Board  |  STANDALONE PCB, NOT a PB2-I cape",
            10,
            8,
            2.0,
        )
    )
    parts.append(
        text_note(
            "Connects to airframe ONLY via J_ETH_IN / J_ETH_OUT (Ethernet ring) and J_CANFD "
            "(CAN-FD trunk). Own +5V power input at J_PWR.",
            10,
            12,
            1.0,
        )
    )
    parts.append(
        text_note(
            "SIMPLIFIED SCHEMATIC SYMBOLS: U1 (AM62A7), U2 (KSZ9477), U5 (SLB9670) show "
            "representative pins only; real pin numbers not yet verified against datasheets. "
            "See file docstring in gen_vera.py. Do not fabricate without completing TODO.md §1.2c.",
            10,
            15,
            1.0,
        )
    )

    # =====================================================================
    # Section A — Power input and regulation
    # =====================================================================
    parts.append(text_note("=== Section A: Power Input + PMIC ===", 10, 25))

    cx, cy = 20, 40
    parts.append(
        sym_inst("Conn_JST_GH_02P", "J_PWR", "JST-GH 2P (shielded) +5V/GND", cx, cy)
    )
    parts.append(glabel_conn("+5V", cx, cy, 2, 0))
    parts.append(glabel_conn("GND", cx, cy, 2, 1))

    # R_Generic/C_Generic (lib_symbol_2pin_h) pins are at exact local (+-3.81, 0).
    parts.append(
        sym_inst(
            "R_Generic",
            "J_CHASSIS_R",
            "0R chassis PGND-GND bond (single point)",
            20,
            55,
        )
    )
    parts.append(glabel("GND", 20 - 3.81, 55, rot=180))
    parts.append(glabel("PGND", 20 + 3.81, 55, rot=0))
    parts.append(
        sym_inst(
            "C_Generic",
            "C_ISO",
            "100nF/500V (parallel w/ R_CHASSIS, GND-PGND bridge)",
            20,
            60,
        )
    )
    parts.append(glabel("GND", 20 - 3.81, 60, rot=180))
    parts.append(glabel("PGND", 20 + 3.81, 60, rot=0))

    cx, cy = 55, 40
    parts.append(sym_inst("TI_TPS65219", "U_PMIC", "TPS65219 PMIC", cx, cy))
    parts.append(glabel_pin("+5V", cx, cy, PMIC_L, PMIC_R, "VIN", PMIC_SIZE))
    parts.append(glabel_pin("GND", cx, cy, PMIC_L, PMIC_R, "GND", PMIC_SIZE))
    parts.append(glabel_pin("PMIC_EN", cx, cy, PMIC_L, PMIC_R, "EN", PMIC_SIZE))
    parts.append(glabel_pin("PMIC_SDA", cx, cy, PMIC_L, PMIC_R, "I2C_SDA", PMIC_SIZE))
    parts.append(glabel_pin("PMIC_SCL", cx, cy, PMIC_L, PMIC_R, "I2C_SCL", PMIC_SIZE))
    parts.append(
        glabel_pin("VDD_CORE", cx, cy, PMIC_L, PMIC_R, "BUCK1_VDD_CORE", PMIC_SIZE)
    )
    parts.append(
        glabel_pin("VDDSHV", cx, cy, PMIC_L, PMIC_R, "BUCK2_VDDSHV", PMIC_SIZE)
    )
    parts.append(glabel_pin("VDDR", cx, cy, PMIC_L, PMIC_R, "BUCK3_VDDR", PMIC_SIZE))
    parts.append(glabel_pin("+3V3", cx, cy, PMIC_L, PMIC_R, "LDO1_3V3_CTRL", PMIC_SIZE))

    parts.append(
        text_note(
            "+3V3 = TPS65219 LDO1 output; shared logic rail for U2/U3/U5/U4 control-half parts.\n"
            "VDD_CORE/VDDSHV/VDDR feed U1 (AM62A) per TI SLVAFD0 app note power sequencing —\n"
            "sequencing/enable logic not modelled here; verify against SLVAFD0 before layout.",
            cx - 17,
            cy + 20,
            0.9,
        )
    )

    # =====================================================================
    # Section B — Vision half: AM62A7 + camera interface
    # =====================================================================
    parts.append(text_note("=== Section B: Vision Half — TI AM62A7 ===", 10, 90))

    cx, cy = 60, 110
    parts.append(sym_inst("TI_AM62A7", "U1", "TI AM62A7", cx, cy))
    parts.append(pwr_pin("VDD_CORE", cx, cy, AM62A_L, AM62A_R, "VDD_CORE", AM62A_SIZE))
    parts.append(pwr_pin("VDDSHV", cx, cy, AM62A_L, AM62A_R, "VDDSHV_MAIN", AM62A_SIZE))
    parts.append(pwr_pin("VDDR", cx, cy, AM62A_L, AM62A_R, "VDDR_CORE", AM62A_SIZE))
    parts.append(pwr_pin("GND", cx, cy, AM62A_L, AM62A_R, "GND", AM62A_SIZE))
    parts.append(glabel_pin("SOC_PORZ", cx, cy, AM62A_L, AM62A_R, "PORz", AM62A_SIZE))
    parts.append(
        glabel_pin("SOC_BOOT0", cx, cy, AM62A_L, AM62A_R, "BOOT_MODE0", AM62A_SIZE)
    )
    parts.append(
        glabel_pin("CAM_SDA", cx, cy, AM62A_L, AM62A_R, "CAM_I2C_SDA", AM62A_SIZE)
    )
    parts.append(
        glabel_pin("CAM_SCL", cx, cy, AM62A_L, AM62A_R, "CAM_I2C_SCL", AM62A_SIZE)
    )
    parts.append(
        glabel_pin("CAM_RESET_N", cx, cy, AM62A_L, AM62A_R, "CAM_RESET_N", AM62A_SIZE)
    )
    parts.append(
        glabel_pin("CAM_PWDN", cx, cy, AM62A_L, AM62A_R, "CAM_PWDN", AM62A_SIZE)
    )
    parts.append(
        glabel_pin("CSI_CLK_P", cx, cy, AM62A_L, AM62A_R, "CSI_CLK_P", AM62A_SIZE)
    )
    parts.append(
        glabel_pin("CSI_CLK_N", cx, cy, AM62A_L, AM62A_R, "CSI_CLK_N", AM62A_SIZE)
    )
    parts.append(
        glabel_pin("CSI_D0_P", cx, cy, AM62A_L, AM62A_R, "CSI_D0_P", AM62A_SIZE)
    )
    parts.append(
        glabel_pin("CSI_D0_N", cx, cy, AM62A_L, AM62A_R, "CSI_D0_N", AM62A_SIZE)
    )

    parts.append(
        glabel_pin("RGMII1_TXC", cx, cy, AM62A_L, AM62A_R, "RGMII1_TXC", AM62A_SIZE)
    )
    parts.append(
        glabel_pin("RGMII1_TXCTL", cx, cy, AM62A_L, AM62A_R, "RGMII1_TXCTL", AM62A_SIZE)
    )
    parts.append(
        glabel_pin("RGMII1_TXD0", cx, cy, AM62A_L, AM62A_R, "RGMII1_TXD0", AM62A_SIZE)
    )
    parts.append(
        glabel_pin("RGMII1_RXC", cx, cy, AM62A_L, AM62A_R, "RGMII1_RXC", AM62A_SIZE)
    )
    parts.append(
        glabel_pin("RGMII1_RXCTL", cx, cy, AM62A_L, AM62A_R, "RGMII1_RXCTL", AM62A_SIZE)
    )
    parts.append(
        glabel_pin("RGMII1_RXD0", cx, cy, AM62A_L, AM62A_R, "RGMII1_RXD0", AM62A_SIZE)
    )
    parts.append(glabel_pin("MDIO", cx, cy, AM62A_L, AM62A_R, "MDIO", AM62A_SIZE))
    parts.append(glabel_pin("MDC", cx, cy, AM62A_L, AM62A_R, "MDC", AM62A_SIZE))
    # UART link to U3 (MSPM0G3507): crossed TX->RX, not net-name-matched TX->TX.
    parts.append(
        glabel_pin("UART_A2M", cx, cy, AM62A_L, AM62A_R, "MCU_UART_TX", AM62A_SIZE)
    )
    parts.append(
        glabel_pin("UART_M2A", cx, cy, AM62A_L, AM62A_R, "MCU_UART_RX", AM62A_SIZE)
    )
    parts.append(
        glabel_pin(
            "SD_CARD_NC",
            cx,
            cy,
            AM62A_L,
            AM62A_R,
            "SD_CARD",
            AM62A_SIZE,
        )
    )

    # J_CAM — camera module connector (CSI + I2C + power)
    cx, cy = 140, 100
    parts.append(
        sym_inst(
            "Conn_JST_GH_04P", "J_CAM1", "JST-GH 4P — CSI_CLK_P/N, CSI_D0_P/N", cx, cy
        )
    )
    parts.append(glabel_conn("CSI_CLK_P", cx, cy, 4, 0))
    parts.append(glabel_conn("CSI_CLK_N", cx, cy, 4, 1))
    parts.append(glabel_conn("CSI_D0_P", cx, cy, 4, 2))
    parts.append(glabel_conn("CSI_D0_N", cx, cy, 4, 3))
    parts.append(
        sym_inst(
            "Conn_JST_GH_04P",
            "J_CAM2",
            "JST-GH 4P — CAM_SDA/SCL, CAM_RESET_N, +3V3",
            cx,
            cy + 20,
        )
    )
    parts.append(glabel_conn("CAM_SDA", cx, cy + 20, 4, 0))
    parts.append(glabel_conn("CAM_SCL", cx, cy + 20, 4, 1))
    parts.append(glabel_conn("CAM_RESET_N", cx, cy + 20, 4, 2))
    parts.append(glabel_conn("+3V3", cx, cy + 20, 4, 3))
    parts.append(
        text_note(
            "Camera sensor module is a separate board mounted at the bow/cargo aperture, not on\n"
            "Vera itself. Only 1 of 4 real MIPI CSI-2 data lanes shown for schematic clarity —\n"
            "see gen_vera.py docstring. SD_CARD_NC left unconnected — placeholder pin, no\n"
            "physical microSD on Vera (logging lives on Wash/Zoe per CLAUDE.md).",
            cx - 7,
            cy + 30,
            0.9,
        )
    )

    # =====================================================================
    # Section C — Control half: MSPM0G3507 + TPM + KSZ9477 + CAN-FD
    # =====================================================================
    parts.append(
        text_note(
            "=== Section C: Control Half — MSPM0G3507 + TPM + Switch + CAN-FD ===",
            10,
            150,
        )
    )

    cx, cy = 55, 175
    parts.append(sym_inst("TI_MSPM0G3507", "U3", "TI MSPM0G3507", cx, cy))
    parts.append(pwr_pin("+3V3", cx, cy, MSPM0_L, MSPM0_R, "+3V3", MSPM0_SIZE))
    parts.append(pwr_pin("GND", cx, cy, MSPM0_L, MSPM0_R, "GND", MSPM0_SIZE))
    parts.append(glabel_pin("MCU_NRST", cx, cy, MSPM0_L, MSPM0_R, "NRST", MSPM0_SIZE))
    parts.append(glabel_pin("MCU_SWCLK", cx, cy, MSPM0_L, MSPM0_R, "SWCLK", MSPM0_SIZE))
    parts.append(glabel_pin("MCU_SWDIO", cx, cy, MSPM0_L, MSPM0_R, "SWDIO", MSPM0_SIZE))
    parts.append(
        glabel_pin("CANFD_TX", cx, cy, MSPM0_L, MSPM0_R, "MCAN_TX", MSPM0_SIZE)
    )
    parts.append(
        glabel_pin("CANFD_RX", cx, cy, MSPM0_L, MSPM0_R, "MCAN_RX", MSPM0_SIZE)
    )
    # UART0: link to U1 (AM62A7), crossed TX->RX (see U1 placement above).
    parts.append(
        glabel_pin("UART_M2A", cx, cy, MSPM0_L, MSPM0_R, "UART0_TX", MSPM0_SIZE)
    )
    parts.append(
        glabel_pin("UART_A2M", cx, cy, MSPM0_L, MSPM0_R, "UART0_RX", MSPM0_SIZE)
    )
    # UART1: dedicated link to TFmini-S (J_TOF), separate from the AM62A link.
    parts.append(
        glabel_pin("UART_TOF_TX", cx, cy, MSPM0_L, MSPM0_R, "UART1_TX", MSPM0_SIZE)
    )
    parts.append(
        glabel_pin("UART_TOF_RX", cx, cy, MSPM0_L, MSPM0_R, "UART1_RX", MSPM0_SIZE)
    )

    parts.append(
        glabel_pin("TPM_SPI_CS", cx, cy, MSPM0_L, MSPM0_R, "SPI0_CS_TPM", MSPM0_SIZE)
    )
    parts.append(
        glabel_pin("TPM_SPI_SCK", cx, cy, MSPM0_L, MSPM0_R, "SPI0_SCK", MSPM0_SIZE)
    )
    parts.append(
        glabel_pin("TPM_SPI_MOSI", cx, cy, MSPM0_L, MSPM0_R, "SPI0_MOSI", MSPM0_SIZE)
    )
    parts.append(
        glabel_pin("TPM_SPI_MISO", cx, cy, MSPM0_L, MSPM0_R, "SPI0_MISO", MSPM0_SIZE)
    )
    parts.append(
        glabel_pin("TPM_PIRQ", cx, cy, MSPM0_L, MSPM0_R, "TPM_PIRQ", MSPM0_SIZE)
    )
    parts.append(
        glabel_pin("SW_SPI_CS", cx, cy, MSPM0_L, MSPM0_R, "SPI1_CS_SW", MSPM0_SIZE)
    )
    parts.append(
        glabel_pin("SW_SPI_SCK", cx, cy, MSPM0_L, MSPM0_R, "SPI1_SCK", MSPM0_SIZE)
    )
    parts.append(
        glabel_pin("SW_SPI_MOSI", cx, cy, MSPM0_L, MSPM0_R, "SPI1_MOSI", MSPM0_SIZE)
    )
    parts.append(
        glabel_pin("SW_SPI_MISO", cx, cy, MSPM0_L, MSPM0_R, "SPI1_MISO", MSPM0_SIZE)
    )
    parts.append(
        glabel_pin("LASER_EN", cx, cy, MSPM0_L, MSPM0_R, "GPIO_LASER_EN", MSPM0_SIZE)
    )
    parts.append(
        glabel_pin(
            "LASER_KEY_IN", cx, cy, MSPM0_L, MSPM0_R, "GPIO_LASER_KEY", MSPM0_SIZE
        )
    )
    parts.append(
        glabel_pin("LASER_IND", cx, cy, MSPM0_L, MSPM0_R, "GPIO_LASER_IND", MSPM0_SIZE)
    )

    parts.append(
        sym_inst("C_Generic", "C_MCU1", "100nF 0402 decoupling", cx - 5, cy + 30)
    )
    parts.append(pwr_sym("+3V3", cx - 5 - 3.81, cy + 30, rot=0))
    parts.append(pwr_sym("GND", cx - 5 + 3.81, cy + 30, rot=0))

    # TPM
    cx, cy = 115, 155
    parts.append(sym_inst("INFINEON_SLB9670", "U5", "Infineon SLB9670 TPM 2.0", cx, cy))
    parts.append(pwr_pin("+3V3", cx, cy, TPM_L, TPM_R, "+3V3", TPM_SIZE))
    parts.append(pwr_pin("GND", cx, cy, TPM_L, TPM_R, "GND", TPM_SIZE))
    parts.append(glabel_pin("TPM_SPI_CS", cx, cy, TPM_L, TPM_R, "SPI_CS", TPM_SIZE))
    parts.append(glabel_pin("TPM_SPI_SCK", cx, cy, TPM_L, TPM_R, "SPI_CLK", TPM_SIZE))
    parts.append(glabel_pin("TPM_SPI_MOSI", cx, cy, TPM_L, TPM_R, "SPI_MOSI", TPM_SIZE))
    parts.append(glabel_pin("TPM_SPI_MISO", cx, cy, TPM_L, TPM_R, "SPI_MISO", TPM_SIZE))
    parts.append(glabel_pin("TPM_PIRQ", cx, cy, TPM_L, TPM_R, "PIRQ", TPM_SIZE))
    parts.append(glabel_pin("TPM_RESET_N", cx, cy, TPM_L, TPM_R, "RESET_N", TPM_SIZE))

    # KSZ9477
    cx, cy = 115, 195
    parts.append(
        sym_inst("MICROCHIP_KSZ9477", "U2", "Microchip KSZ9477 7-port switch", cx, cy)
    )
    parts.append(pwr_pin("+3V3", cx, cy, KSZ_L, KSZ_R, "+3V3", KSZ_SIZE))
    parts.append(glabel_pin("SW_1V2", cx, cy, KSZ_L, KSZ_R, "+1V2", KSZ_SIZE))
    parts.append(pwr_pin("GND", cx, cy, KSZ_L, KSZ_R, "GND", KSZ_SIZE))
    parts.append(glabel_pin("SW_RESET_N", cx, cy, KSZ_L, KSZ_R, "RESET_N", KSZ_SIZE))
    parts.append(glabel_pin("SW_INT_N", cx, cy, KSZ_L, KSZ_R, "INT_N", KSZ_SIZE))
    parts.append(glabel_pin("SW_XTAL_25M", cx, cy, KSZ_L, KSZ_R, "XTAL_25M", KSZ_SIZE))
    parts.append(glabel_pin("SW_SPI_CS", cx, cy, KSZ_L, KSZ_R, "SPI_CS_HOST", KSZ_SIZE))
    parts.append(
        glabel_pin("SW_SPI_SCK", cx, cy, KSZ_L, KSZ_R, "SPI_SCK_HOST", KSZ_SIZE)
    )
    parts.append(
        glabel_pin("SW_SPI_MOSI", cx, cy, KSZ_L, KSZ_R, "SPI_MOSI_HOST", KSZ_SIZE)
    )
    parts.append(
        glabel_pin("SW_SPI_MISO", cx, cy, KSZ_L, KSZ_R, "SPI_MISO_HOST", KSZ_SIZE)
    )

    parts.append(
        glabel_pin("RGMII1_TXC", cx, cy, KSZ_L, KSZ_R, "P1_RGMII_TXC", KSZ_SIZE)
    )
    parts.append(
        glabel_pin("RGMII1_TXCTL", cx, cy, KSZ_L, KSZ_R, "P1_RGMII_TXCTL", KSZ_SIZE)
    )
    parts.append(
        glabel_pin("RGMII1_TXD0", cx, cy, KSZ_L, KSZ_R, "P1_RGMII_TXD0", KSZ_SIZE)
    )
    parts.append(
        glabel_pin("RGMII1_RXC", cx, cy, KSZ_L, KSZ_R, "P1_RGMII_RXC", KSZ_SIZE)
    )
    parts.append(
        glabel_pin("RGMII1_RXCTL", cx, cy, KSZ_L, KSZ_R, "P1_RGMII_RXCTL", KSZ_SIZE)
    )
    parts.append(
        glabel_pin("RGMII1_RXD0", cx, cy, KSZ_L, KSZ_R, "P1_RGMII_RXD0", KSZ_SIZE)
    )
    parts.append(glabel_pin("ETH_IN_KSZ_TXP", cx, cy, KSZ_L, KSZ_R, "P2_TXP", KSZ_SIZE))
    parts.append(glabel_pin("ETH_IN_KSZ_TXN", cx, cy, KSZ_L, KSZ_R, "P2_TXN", KSZ_SIZE))
    parts.append(glabel_pin("ETH_IN_KSZ_RXP", cx, cy, KSZ_L, KSZ_R, "P2_RXP", KSZ_SIZE))
    parts.append(glabel_pin("ETH_IN_KSZ_RXN", cx, cy, KSZ_L, KSZ_R, "P2_RXN", KSZ_SIZE))
    parts.append(
        glabel_pin("ETH_OUT_KSZ_TXP", cx, cy, KSZ_L, KSZ_R, "P3_TXP", KSZ_SIZE)
    )
    parts.append(
        glabel_pin("ETH_OUT_KSZ_TXN", cx, cy, KSZ_L, KSZ_R, "P3_TXN", KSZ_SIZE)
    )
    parts.append(
        glabel_pin("ETH_OUT_KSZ_RXP", cx, cy, KSZ_L, KSZ_R, "P3_RXP", KSZ_SIZE)
    )
    parts.append(
        glabel_pin("ETH_OUT_KSZ_RXN", cx, cy, KSZ_L, KSZ_R, "P3_RXN", KSZ_SIZE)
    )

    # Y1 crystal for KSZ9477 (25 MHz)
    parts.append(
        sym_inst(
            "C_Generic",
            "Y1",
            "25MHz crystal (2-pin symbol simplified)",
            cx - 40,
            cy + 25,
        )
    )
    parts.append(glabel("SW_XTAL_25M", cx - 40 - 3.81, cy + 25, rot=180))
    parts.append(pwr_sym("GND", cx - 40 + 3.81, cy + 25, rot=180))

    # =====================================================================
    # EMI hardening — Ethernet ports (matches Wash/Zoë Rev R baseline):
    # KSZ9477 port -> Wurth 749010012A magnetics -> SRF2012-100Y CMC (x2,
    # one per differential pair) -> PRTR5V0U2X TVS (x2, shunt) -> connector.
    # =====================================================================
    parts.append(
        text_note(
            "EMI hardening chain per Ethernet port (matches Wash/Zoe Rev R baseline):\n"
            "KSZ9477 -> Wurth 749010012A magnetics -> SRF2012-100Y common-mode choke x2 ->\n"
            "PRTR5V0U2X TVS x2 (shunt to GND) -> JST-GH 5P connector (GND,TXP,TXN,RXP,RXN).",
            220,
            150,
            0.9,
        )
    )

    def eth_port_chain(
        port_label,
        cx0,
        cy0,
        ksz_txp,
        ksz_txn,
        ksz_rxp,
        ksz_rxn,
        xfmr_ref,
        cmc_tx_ref,
        cmc_rx_ref,
        tvs_tx_ref,
        tvs_rx_ref,
        conn_ref,
    ):
        # Magnetics: KSZ side (PHY_TX/RX) <-> Line side (LINE_TX/RX)
        parts.append(sym_inst("WURTH_ETH_XFMR", xfmr_ref, "Wurth 749010012A", cx0, cy0))
        parts.append(
            glabel_pin(ksz_txp, cx0, cy0, XFMR_L, XFMR_R, "PHY_TXP", XFMR_SIZE)
        )
        parts.append(
            glabel_pin(ksz_txn, cx0, cy0, XFMR_L, XFMR_R, "PHY_TXN", XFMR_SIZE)
        )
        parts.append(
            glabel_pin(ksz_rxp, cx0, cy0, XFMR_L, XFMR_R, "PHY_RXP", XFMR_SIZE)
        )
        parts.append(
            glabel_pin(ksz_rxn, cx0, cy0, XFMR_L, XFMR_R, "PHY_RXN", XFMR_SIZE)
        )
        parts.append(
            glabel_pin(
                f"{port_label}_XFMR_TXP",
                cx0,
                cy0,
                XFMR_L,
                XFMR_R,
                "LINE_TXP",
                XFMR_SIZE,
            )
        )
        parts.append(
            glabel_pin(
                f"{port_label}_XFMR_TXN",
                cx0,
                cy0,
                XFMR_L,
                XFMR_R,
                "LINE_TXN",
                XFMR_SIZE,
            )
        )
        parts.append(
            glabel_pin(
                f"{port_label}_XFMR_RXP",
                cx0,
                cy0,
                XFMR_L,
                XFMR_R,
                "LINE_RXP",
                XFMR_SIZE,
            )
        )
        parts.append(
            glabel_pin(
                f"{port_label}_XFMR_RXN",
                cx0,
                cy0,
                XFMR_L,
                XFMR_R,
                "LINE_RXN",
                XFMR_SIZE,
            )
        )

        # CMC (belt-and-suspenders common-mode suppression), one per pair.
        cx1, cy1 = cx0 + 18, cy0 - 6
        parts.append(
            sym_inst(
                "BOURNS_SRF2012_100Y",
                cmc_tx_ref,
                "Bourns SRF2012-100Y (TX pair)",
                cx1,
                cy1,
            )
        )
        parts.append(
            glabel_pin(
                f"{port_label}_XFMR_TXP", cx1, cy1, CMC_L, CMC_R, "L1A", CMC_SIZE
            )
        )
        parts.append(
            glabel_pin(f"{port_label}_TXP", cx1, cy1, CMC_L, CMC_R, "L1B", CMC_SIZE)
        )
        parts.append(
            glabel_pin(
                f"{port_label}_XFMR_TXN", cx1, cy1, CMC_L, CMC_R, "L2A", CMC_SIZE
            )
        )
        parts.append(
            glabel_pin(f"{port_label}_TXN", cx1, cy1, CMC_L, CMC_R, "L2B", CMC_SIZE)
        )

        cx2, cy2 = cx0 + 18, cy0 + 6
        parts.append(
            sym_inst(
                "BOURNS_SRF2012_100Y",
                cmc_rx_ref,
                "Bourns SRF2012-100Y (RX pair)",
                cx2,
                cy2,
            )
        )
        parts.append(
            glabel_pin(
                f"{port_label}_XFMR_RXP", cx2, cy2, CMC_L, CMC_R, "L1A", CMC_SIZE
            )
        )
        parts.append(
            glabel_pin(f"{port_label}_RXP", cx2, cy2, CMC_L, CMC_R, "L1B", CMC_SIZE)
        )
        parts.append(
            glabel_pin(
                f"{port_label}_XFMR_RXN", cx2, cy2, CMC_L, CMC_R, "L2A", CMC_SIZE
            )
        )
        parts.append(
            glabel_pin(f"{port_label}_RXN", cx2, cy2, CMC_L, CMC_R, "L2B", CMC_SIZE)
        )

        # TVS (shunt to GND) on each pair — anode taps the line, doesn't break the net.
        cx3, cy3 = cx0 + 36, cy0 - 6
        parts.append(
            sym_inst(
                "NEXPERIA_PRTR5V0U2X",
                tvs_tx_ref,
                "Nexperia PRTR5V0U2X (TX pair)",
                cx3,
                cy3,
            )
        )
        parts.append(
            glabel_pin(f"{port_label}_TXP", cx3, cy3, TVS_L, TVS_R, "A1", TVS_SIZE)
        )
        parts.append(
            glabel_pin(f"{port_label}_TXN", cx3, cy3, TVS_L, TVS_R, "A2", TVS_SIZE)
        )
        parts.append(pwr_pin("GND", cx3, cy3, TVS_L, TVS_R, "K", TVS_SIZE))

        cx4, cy4 = cx0 + 36, cy0 + 6
        parts.append(
            sym_inst(
                "NEXPERIA_PRTR5V0U2X",
                tvs_rx_ref,
                "Nexperia PRTR5V0U2X (RX pair)",
                cx4,
                cy4,
            )
        )
        parts.append(
            glabel_pin(f"{port_label}_RXP", cx4, cy4, TVS_L, TVS_R, "A1", TVS_SIZE)
        )
        parts.append(
            glabel_pin(f"{port_label}_RXN", cx4, cy4, TVS_L, TVS_R, "A2", TVS_SIZE)
        )
        parts.append(pwr_pin("GND", cx4, cy4, TVS_L, TVS_R, "K", TVS_SIZE))

        # Connector: JST-GH 5P (GND, TX+, TX-, RX+, RX-) — matches Wash's real
        # verified footprint (JST_GH_SM05B-GHS-TB_1x05-1MP), not a fabricated 6P.
        cx5, cy5 = cx0 + 54, cy0
        parts.append(
            sym_inst(
                "Conn_JST_GH_05P",
                conn_ref,
                f"JST-GH 5P (shielded) — Ethernet ring {port_label.split('_')[-1].lower()}",
                cx5,
                cy5,
            )
        )
        parts.append(glabel_conn("PGND_SHIELD", cx5, cy5, 5, 0))
        parts.append(glabel_conn(f"{port_label}_TXP", cx5, cy5, 5, 1))
        parts.append(glabel_conn(f"{port_label}_TXN", cx5, cy5, 5, 2))
        parts.append(glabel_conn(f"{port_label}_RXP", cx5, cy5, 5, 3))
        parts.append(glabel_conn(f"{port_label}_RXN", cx5, cy5, 5, 4))

    eth_port_chain(
        "ETH_IN",
        175,
        160,
        "ETH_IN_KSZ_TXP",
        "ETH_IN_KSZ_TXN",
        "ETH_IN_KSZ_RXP",
        "ETH_IN_KSZ_RXN",
        "T1",
        "CMC1",
        "CMC2",
        "D1",
        "D2",
        "J_ETH_IN",
    )
    eth_port_chain(
        "ETH_OUT",
        175,
        210,
        "ETH_OUT_KSZ_TXP",
        "ETH_OUT_KSZ_TXN",
        "ETH_OUT_KSZ_RXP",
        "ETH_OUT_KSZ_RXN",
        "T2",
        "CMC3",
        "CMC4",
        "D3",
        "D4",
        "J_ETH_OUT",
    )

    parts.append(glabel("PGND", 300, 240, rot=0))
    parts.append(glabel("PGND_SHIELD", 300, 243, rot=0))

    # =====================================================================
    # CAN-FD — TI ISOW1044BDFMR (galvanically isolated, 5 kV reinforced
    # insulation) replaces the non-isolated TCAN1042HG-Q1 to match Wash/Zoe's
    # CAN-FD isolation standard [REF-IEC-001, REF-VDE-001]. + SRF2012-100Y CMC
    # + PRTR5V0U2X TVS on the bus side, matching Wash's real CAN chain.
    # =====================================================================
    cx, cy = 40, 235
    parts.append(
        sym_inst("TI_ISOW1044BDFMR", "U4", "TI ISOW1044BDFMR (isolated CAN-FD)", cx, cy)
    )
    parts.append(pwr_pin("GND", cx, cy, ISOW_L, ISOW_R, "GND1", ISOW_SIZE))
    parts.append(glabel_pin("CANFD_TX", cx, cy, ISOW_L, ISOW_R, "TXD", ISOW_SIZE))
    parts.append(glabel_pin("CANFD_STBY_N", cx, cy, ISOW_L, ISOW_R, "STB_N", ISOW_SIZE))
    parts.append(glabel_pin("CANFD_RX", cx, cy, ISOW_L, ISOW_R, "RXD", ISOW_SIZE))
    parts.append(pwr_pin("+3V3", cx, cy, ISOW_L, ISOW_R, "VCC1", ISOW_SIZE))
    parts.append(
        glabel_pin("CANFD_ISOGND", cx, cy, ISOW_L, ISOW_R, "ISOGND", ISOW_SIZE)
    )
    parts.append(glabel_pin("CANFD_ISO_L", cx, cy, ISOW_L, ISOW_R, "CANL", ISOW_SIZE))
    parts.append(glabel_pin("CANFD_ISO_H", cx, cy, ISOW_L, ISOW_R, "CANH", ISOW_SIZE))
    parts.append(glabel_pin("+5V", cx, cy, ISOW_L, ISOW_R, "VCC2", ISOW_SIZE))

    # CMC_CAN — SRF2012-100Y on the isolated bus side (belt-and-suspenders).
    cx1, cy1 = cx + 25, cy
    parts.append(
        sym_inst(
            "BOURNS_SRF2012_100Y", "CMC5", "Bourns SRF2012-100Y (CAN bus)", cx1, cy1
        )
    )
    parts.append(glabel_pin("CANFD_ISO_H", cx1, cy1, CMC_L, CMC_R, "L1A", CMC_SIZE))
    parts.append(glabel_pin("CANFD_H", cx1, cy1, CMC_L, CMC_R, "L1B", CMC_SIZE))
    parts.append(glabel_pin("CANFD_ISO_L", cx1, cy1, CMC_L, CMC_R, "L2A", CMC_SIZE))
    parts.append(glabel_pin("CANFD_L", cx1, cy1, CMC_L, CMC_R, "L2B", CMC_SIZE))

    # TVS_CAN — PRTR5V0U2X shunt on CANH/CANL, cathode to chassis PGND (bus-side
    # protection references chassis ground, not the isolated logic-side GND).
    cx2, cy2 = cx + 43, cy
    parts.append(
        sym_inst("NEXPERIA_PRTR5V0U2X", "D5", "Nexperia PRTR5V0U2X (CAN bus)", cx2, cy2)
    )
    parts.append(glabel_pin("CANFD_H", cx2, cy2, TVS_L, TVS_R, "A1", TVS_SIZE))
    parts.append(glabel_pin("CANFD_L", cx2, cy2, TVS_L, TVS_R, "A2", TVS_SIZE))
    parts.append(pwr_pin("PGND", cx2, cy2, TVS_L, TVS_R, "K", TVS_SIZE))

    # J_CANFD connector
    cx, cy = 100, 235
    parts.append(
        sym_inst(
            "Conn_JST_GH_04P",
            "J_CANFD",
            "JST-GH 4P (shielded) — 5V, CAN-H, CAN-L, GND",
            cx,
            cy,
        )
    )
    parts.append(glabel_conn("+5V", cx, cy, 4, 0))
    parts.append(glabel_conn("CANFD_H", cx, cy, 4, 1))
    parts.append(glabel_conn("CANFD_L", cx, cy, 4, 2))
    parts.append(glabel_conn("GND", cx, cy, 4, 3))
    parts.append(
        text_note(
            "PGND_SHIELD = JST-GH metal shroud, bonded to chassis/Faraday ground only —\n"
            "tied to digital GND at a single RC isolation point (see Section A), never directly.",
            cx - 20,
            cy + 40,
            0.9,
        )
    )

    # =====================================================================
    # Section D — ToF sensor + laser driver (location-specific population)
    # =====================================================================
    parts.append(text_note("=== Section D: ToF (TFmini-S) + Laser Driver ===", 10, 230))

    cx, cy = 40, 250
    parts.append(
        sym_inst(
            "Conn_JST_GH_04P",
            "J_TOF",
            "JST-GH 4P — TFmini-S (+5V, GND, TX, RX)",
            cx,
            cy,
        )
    )
    parts.append(glabel_conn("+5V", cx, cy, 4, 0))
    parts.append(glabel_conn("GND", cx, cy, 4, 1))
    # Net names are from TFmini-S's own TX/RX perspective (matches its datasheet
    # labeling and TODO.md's existing wiring note) — crossed to U3's UART1 RX/TX above.
    parts.append(glabel_conn("UART_TOF_TX", cx, cy, 4, 2))
    parts.append(glabel_conn("UART_TOF_RX", cx, cy, 4, 3))
    parts.append(
        text_note(
            "TFmini-S has its OWN dedicated MSPM0G3507 UART instance (UART1) — separate from\n"
            "the UART0 link to U1 (AM62A7). No net-sharing/contention between the two links.",
            cx - 5,
            cy + 10,
            0.9,
        )
    )

    # Laser driver — Q1 AO3400, R1 gate, R2 pulldown
    # AO3400 local pin offsets (from lib_symbol_nmos): G=(-7.62,0), D=(2.54,7.62), S=(2.54,-7.62).
    # Sheet position negates local Y (see _ic_pin_xy docstring), so on the sheet
    # D lands at (cx+2.54, cy-7.62) and S at (cx+2.54, cy+7.62) — NOT the other
    # way around; this bit us once already (D/S swap caught by PCB DRC parity).
    cx, cy = 95, 250
    parts.append(sym_inst("AO3400", "Q1", "AO3400 logic-level N-MOSFET", cx, cy))
    parts.append(glabel("LASER_GATE", cx - 7.62, cy, rot=180))
    parts.append(glabel("LASER_CATHODE", cx + 2.54, cy - 7.62, rot=90))
    parts.append(pwr_sym("GND", cx + 2.54, cy + 7.62, rot=0))

    parts.append(sym_inst("R_Generic", "R1", "100R 0402 gate resistor", cx - 25, cy))
    parts.append(glabel("LASER_EN", cx - 25 - 3.81, cy, rot=180))
    parts.append(glabel("LASER_GATE", cx - 25 + 3.81, cy, rot=0))

    parts.append(
        sym_inst("R_Generic", "R2", "10k 0402 pulldown (default-off)", cx - 25, cy + 10)
    )
    parts.append(glabel("LASER_GATE", cx - 25 - 3.81, cy + 10, rot=180))
    parts.append(pwr_sym("GND", cx - 25 + 3.81, cy + 10, rot=0))

    cx2, cy2 = cx + 35, cy
    parts.append(
        sym_inst(
            "Conn_JST_SH_02P",
            "J_LASER",
            "JST-SH 2P — laser module (+5V, cathode/drain)",
            cx2,
            cy2,
        )
    )
    parts.append(glabel_conn("+5V", cx2, cy2, 2, 0))
    parts.append(glabel_conn("LASER_CATHODE", cx2, cy2, 2, 1))

    parts.append(
        text_note(
            'LOCATION-SPECIFIC POPULATION — see avionics/CLAUDE.md "Vera" and REF-IEC-002:\n'
            '  Cargo bay (3"x3" @ 5ft): populate with existing 5mW 650nm Class 3R module\n'
            "    (reuses driver above as-is; GPIO-default-off pull-down is sufficient).\n"
            '  Nose (2"x2" @ 50ft): Class 3B 520nm module (part TBD, TODO.md §1.2c) requires\n'
            "    ADDITIONAL key-interlock (LASER_KEY_IN to MSPM0G3507, gates LASER_EN in\n"
            "    firmware) and emission-indicator LED (LASER_IND) shown wired to U3 above but\n"
            "    not yet populated with a physical LED/interlock switch on this sheet — add\n"
            "    before nose variant fabrication.",
            cx - 20,
            cy + 20,
            0.9,
        )
    )

    # -------------------------------------------------------------------
    # Compose
    # -------------------------------------------------------------------
    sch = [
        "(kicad_sch (version 20240101) (generator eeschema)",
        '  (paper "A2")',
        "  (title_block",
        '    (title "Vera — Nose/Cargo-Bay Vision, ToF & Laser Board")'
        ' (date "2026-07-03") (rev "-") (company "Griffing Technology LLC")',
        '    (comment 1 "Serenity UAV — STANDALONE board, NOT a PocketBeagle 2 Industrial cape")',
        '    (comment 2 "Copyright 2026 Steve Griffing PE(CSE) CISSP-ISSEP CPP |'
        ' Griffing Technology LLC")',
        '    (comment 3 "License: CC BY 4.0  |  creativecommons.org/licenses/by/4.0")',
        '    (comment 4 "DESIGN EXPLORATION — see gen_vera.py docstring for verification status")',
        "  )",
    ]
    sch.extend(parts)
    sch.append(")")
    return "\n".join(sch)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    out = {
        "Vera.kicad_pro": gen_pro(),
        "Vera.kicad_sch": gen_sch(),
    }
    for fname, content in out.items():
        path = here / fname
        path.write_text(content, encoding="utf-8")
        print(f"  Written: {path}  ({len(content):,} bytes)")
    print("Done.")
