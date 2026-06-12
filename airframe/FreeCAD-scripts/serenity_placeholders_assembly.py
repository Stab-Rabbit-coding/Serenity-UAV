"""
serenity_placeholders_assembly.py — Serenity UAV non-printable component placeholder catalog.

Imports all placeholder STLs from airframe/placeholders/ into a single FreeCAD document
and arranges them in a grid layout (8 columns) for reference during assembly planning,
exploded-view preparation, and build-guide creation.

Run headlessly:
    freecadcmd airframe/FreeCAD-scripts/serenity_placeholders_assembly.py

Or from FreeCAD GUI: File → Open → run as macro.

Output: airframe/Serenity-Placeholders.FCStd

Each component is:
  • Imported as a Mesh::Feature at its grid position.
  • Labelled with the BOM reference (e.g. "EDF-50-6S").
  • Positioned in a 200 mm × 200 mm grid (column × row, 0-indexed, 8 per row).

IMPORTANT: These are standalone reference objects, NOT positioned in the hull frame.
           They carry no HULL-FRAME R1 bake marker and must not be included in the
           hull-frame assembly (serenity_assembly.py).

Coordinate standard exception (CLAUDE.md): placeholders use part-local display
frames (centred at origin per object); only the hull-frame STLs in airframe/stls/
use the canonical hull coordinate system.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0 — creativecommons.org/licenses/by/4.0

References:
    [1] airframe/placeholders/generate_placeholders.py — STL source
    [2] current-specification/bom_revR.csv — Rev R BOM
    [3] CLAUDE.md — project coordinate system and fabrication standards
"""

import os
import sys

import FreeCAD as App
import Mesh

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AIRFRAME   = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
PH_DIR     = os.path.join(AIRFRAME, "placeholders")
OUTPUT     = os.path.join(AIRFRAME, "Serenity-Placeholders.FCStd")

# Grid layout parameters (mm)
_GRID_COL_STEP = 200.0      # X step per column
_GRID_ROW_STEP = 200.0      # Y step per row
_GRID_COLS     = 8          # components per row


# ---------------------------------------------------------------------------
# All placeholder STLs: (bom_ref, subdir/filename, label)
# Must match the _COMPONENTS table in generate_placeholders.py.
# ---------------------------------------------------------------------------
_PLACEHOLDERS = [
    # Propulsion
    ("EDF-50-6S",          "propulsion/EDF_50mm_6S.stl",                     "EDF_50mm_6S"),
    ("EDF-120-6S",         "propulsion/EDF_120mm_6S_deferred.stl",           "EDF_120mm_6S"),
    ("ESC-40A-6S",         "propulsion/ESC_40A_6S_BLHeli32.stl",            "ESC_40A_6S"),
    ("ESC-80A-6S",         "propulsion/ESC_80A_6S_BLHeli32_deferred.stl",   "ESC_80A_6S"),
    # Servos
    ("SERVO-TILT",         "servos/DS3218MG_25kgcm.stl",                    "DS3218MG_25kgcm"),
    ("SERVO-SG90",         "servos/SG90_micro.stl",                         "SG90_micro"),
    # Bearings
    ("BRG-MF104ZZ",        "bearings/MF104ZZ_4x10x4mm.stl",                 "MF104ZZ_4x10x4"),
    ("BRG-MR63ZZ",         "bearings/MR63ZZ_3x6x2p5mm.stl",                 "MR63ZZ_3x6x2p5"),
    ("MAL-BRG-6804",       "bearings/B6804_20x32x7mm_GCS.stl",              "B6804_GCS"),
    # Structural
    ("CF-ROD-4MM",         "structural/CF_rod_4mm_300mm_stock.stl",          "CF_rod_4mm"),
    ("SHAFT-CF-3MM",       "structural/CF_rod_3mm_300mm_stock.stl",          "CF_rod_3mm"),
    ("CF-TUBE-12MM",       "structural/CF_tube_12mm_OD_1p5w_350mm_spar.stl","CF_tube_spar_12mm"),
    ("CF-BAR-6X3",         "structural/CF_bar_6x3mm_620mm_keel.stl",         "CF_bar_6x3_keel"),
    ("CF-PLATE-2MM",       "structural/CF_plate_2mm_200x300mm.stl",          "CF_plate_2mm"),
    ("PTFE-SLEEVE-4MM",    "structural/PTFE_sleeve_4mm_OD_3mm_ID_52mm.stl", "PTFE_sleeve_4mm"),
    # Avionics
    ("PB2-I",              "avionics/PocketBeagle2_Industrial_56x35mm.stl",  "PocketBeagle2_Industrial"),
    ("CAPE-A-2",           "avionics/Cape_A2_PCB_55x35mm.stl",              "Cape_A2"),
    ("CAPE-B-2",           "avionics/Cape_B2_PCB_55x35mm.stl",              "Cape_B2"),
    ("XCVR-49MHZ-2",       "avionics/XCVR_49MHZ2_PCB_55x35mm.stl",         "XCVR_49MHZ2"),
    ("Kaylee",             "avionics/Kaylee_PDB_90x65mm.stl",               "Kaylee_PDB"),
    ("MICROSD-LOG",        "avionics/microSD_64GB.stl",                     "microSD_64GB"),
    # Power
    ("BATT-6S-4000",       "power/LiPo_6S_4000mAh_138x44x36mm.stl",        "LiPo_6S_4000mAh"),
    ("BATT-6S-2800",       "power/LiPo_6S_2800mAh_115x35x35mm.stl",        "LiPo_6S_2800mAh"),
    ("MAL-FIELD-BATTERY",  "power/LiPo_4S_10000mAh_175x64x38mm_GCS.stl",   "LiPo_4S_GCS"),
    ("FUSE-MAIN-150A",     "power/Fuse_MAXI_150A.stl",                      "Fuse_MAXI_150A"),
    ("FUSE-ESC-40A",       "power/Fuse_mini_40A.stl",                       "Fuse_mini_40A"),
    ("SHUNT-1MOHM",        "power/Shunt_CSS2H_2512K_1mohm.stl",             "Shunt_1mohm"),
    # Cargo
    ("N20-WINCH",          "cargo/N20_motor_300RPM_6V.stl",                 "N20_motor_winch"),
    ("HX711-LC",           "cargo/HX711_loadcell_ADC_breakout.stl",         "HX711_ADC"),
    ("DRV8833-CARGO",      "cargo/DRV8833_Hbridge_breakout.stl",            "DRV8833_Hbridge"),
    ("DYNEEMA-SK75",       "cargo/Dyneema_SK75_0p5mm_coil.stl",             "Dyneema_SK75"),
    # Gears
    ("SECTOR-M1-R22",      "gears/Sector_gear_M1_R22mm.stl",               "Sector_M1_R22"),
    ("PINION-A-M1-12T",    "gears/Pinion_M1_12T_R6mm.stl",                 "Pinion_M1_12T"),
    ("BEVEL-M1-14T",       "gears/Bevel_M1_14T_pair.stl",                  "Bevel_M1_14T_pair"),
    ("BEVEL-HOUSING",      "gears/Bevel_housing_CF_PETG.stl",               "Bevel_housing"),
    # Hardware
    ("PIN-3X5",            "hardware/Pin_SS_3x5mm_hinge.stl",               "Pin_3x5_SS"),
    ("INSERT-M25-BRASS",   "hardware/Insert_M25_brass_L5.stl",              "Insert_M25_brass"),
    ("INSERT-M3-WING",     "hardware/Insert_M3_brass_L5.stl",               "Insert_M3_brass"),
    ("SCREW-M3-8-BTN",     "hardware/Screw_M3x8mm_button_ISO7380.stl",      "Screw_M3x8_btn"),
    ("PIANO-WIRE-0.8",     "hardware/Piano_wire_0p8mm_iris_ring.stl",       "Piano_wire_ring"),
    ("BATT-STRAP-CAM",     "hardware/Batt_strap_silicone_16mm_CAM.stl",     "Batt_strap_16mm"),
    # Lighting
    ("LED-WS2812B",        "lighting/WS2812B_ring_50mm.stl",               "WS2812B_ring_50mm"),
    ("LED-WS2812C-NAC",    "lighting/WS2812C_2020_SMD.stl",                "WS2812C_2020"),
    # Wiring
    ("CONDUIT-PTFE",       "wiring/PTFE_conduit_4mm_OD_3mm_ID_700mm.stl",  "PTFE_conduit_700mm"),
    ("WIRE-4AWG",          "wiring/Wire_4AWG_silicone_200mm_pair.stl",      "Wire_4AWG_pair"),
    ("WIRE-10AWG",         "wiring/Wire_10AWG_silicone_400mm.stl",          "Wire_10AWG"),
    ("WIRE-28AWG-STP",     "wiring/Wire_28AWG_STP_bundle_500mm.stl",        "Wire_28AWG_STP"),
    ("WIRE-49MHZ",         "wiring/Wire_49MHz_antenna_0p3mm_470mm.stl",     "Wire_49MHz_ant"),
    ("POST-FWD/AFT-49",    "wiring/Post_49MHz_base_load_coil.stl",          "Post_49MHz_coil"),
    # GCS
    ("MAL-ENCLOSURE",      "gcs/Malcolm_enclosure_IP65_145x90x65mm.stl",   "Malcolm_enclosure"),
    ("MAL-PWR-5V-BEC",     "gcs/Pololu_D24V50F5_5V5A_BEC.stl",             "Pololu_5V5A_BEC"),
    ("MAL-PWR-6V-BEC",     "gcs/Pololu_D24V22F6_6V2A_BEC.stl",             "Pololu_6V2A_BEC"),
    ("MAL-ANT-915-OMNI",   "gcs/Antenna_915MHz_omni_5dBi.stl",             "Ant_915_omni"),
    ("MAL-ANT-915-YAGI",   "gcs/Antenna_915MHz_Yagi_9dBi.stl",             "Ant_915_Yagi"),
    ("MAL-ANT-WIFI-PNL",   "gcs/Antenna_5GHz_panel_14dBi.stl",             "Ant_5GHz_panel"),
    ("MAL-ANT-49MHZ",      "gcs/Antenna_49MHz_whip_940mm.stl",             "Ant_49MHz_whip"),
    ("MAL-ANT-ZIGBEE",     "gcs/Antenna_2p4GHz_zigbee_rubber_duck.stl",    "Ant_2p4GHz_duck"),
    ("MAL-ANT-GPS",        "gcs/Antenna_GNSS_patch_ANN_MB00.stl",          "Ant_GNSS_patch"),
    ("MAL-GPS-MODULE",     "gcs/GPS_module_M10Q_SparkFun.stl",             "GPS_M10Q"),
    ("MAL-RF-SPLITTER",    "gcs/RF_splitter_915MHz_2way_ZFSC.stl",         "RF_splitter_915"),
    ("MAL-GIMBAL-ENC",     "gcs/AS5600_encoder_breakout_15x15mm.stl",      "AS5600_encoder"),
    ("MAL-GIMBAL-MAG",     "gcs/N42_disc_magnet_6x2mm.stl",                "N42_magnet"),
    ("MAL-TCA9548A",       "gcs/TCA9548A_I2C_mux_breakout.stl",            "TCA9548A_mux"),
    ("MAL-BRG-6804",       "gcs/B6804_20x32x7mm_gimbal_pan.stl",           "B6804_gimbal"),
    ("MAL-TRIPOD",         "gcs/Malcolm_tripod_antenna_mast.stl",           "Malcolm_tripod"),
]


# ---------------------------------------------------------------------------
# Assembly helpers
# ---------------------------------------------------------------------------

def _stl(rel):
    """Absolute path to a placeholder STL."""
    return os.path.join(PH_DIR, rel)


def _add(doc, stl_path, label, col, row):
    """
    Import an STL as Mesh::Feature and place it at grid position (col, row).

    The grid origin is (0, 0, 0); each cell is _GRID_COL_STEP × _GRID_ROW_STEP mm.
    Components at the same row are placed side-by-side along X.
    Returns the new doc object, or None if the file is missing.
    """
    if not os.path.exists(stl_path):
        print(f"[WARN] missing STL, skipping: {stl_path}", flush=True)
        return None

    mesh_data = Mesh.Mesh(stl_path)
    obj = doc.addObject("Mesh::Feature", label)
    obj.Mesh = mesh_data
    obj.Label = label

    px = col * _GRID_COL_STEP
    py = row * _GRID_ROW_STEP
    obj.Placement = App.Placement(
        App.Vector(px, py, 0.0),
        App.Rotation(0.0, 0.0, 0.0, 1.0),
    )
    return obj


# ---------------------------------------------------------------------------
# Main assembly
# ---------------------------------------------------------------------------

def assemble():
    """Build the placeholder catalog FreeCAD document."""
    print("[placeholders] Creating FreeCAD document ...", flush=True)
    doc = App.newDocument("SerenityPlaceholders")

    missing = []
    idx = 0
    for (bom_ref, rel_path, label) in _PLACEHOLDERS:
        col = idx % _GRID_COLS
        row = idx // _GRID_COLS
        full_path = _stl(rel_path)
        obj = _add(doc, full_path, label, col, row)
        if obj is None:
            missing.append(rel_path)
        else:
            print(f"  [{idx+1:02d}]  {label:<40s}  col={col} row={row}  [{bom_ref}]",
                  flush=True)
        idx += 1

    print(f"\n[placeholders] Loaded {idx - len(missing)}/{idx} components.", flush=True)
    if missing:
        print(f"[placeholders] MISSING ({len(missing)}):", flush=True)
        for m in missing:
            print(f"  {m}", flush=True)
        print("[placeholders] Run generate_placeholders.py to regenerate missing STLs.",
              flush=True)

    print("[placeholders] Recomputing ...", flush=True)
    doc.recompute()

    print(f"[placeholders] Saving → {OUTPUT}", flush=True)
    doc.saveAs(OUTPUT)
    print("[placeholders] Complete.", flush=True)


if __name__ in ("__main__", "serenity_placeholders_assembly"):
    assemble()
