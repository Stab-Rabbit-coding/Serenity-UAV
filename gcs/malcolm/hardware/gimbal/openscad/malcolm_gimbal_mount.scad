// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Hull frame (canonical for ALL design artifacts): X = +port (left),
//   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
//   world origin.  Primary-component STLs published to airframe/stls/
//   are stored directly in hull frame, baked by tools/bake_hull_frame.py
//   (marker 'SerenityUAV HULL-FRAME R1' in the binary STL header).
//   NEVER re-bake a mesh derived from an already-baked file.
//   This file:
//     Malcolm ground-support equipment - part-local print frame.  The
//     aircraft hull-frame standard does not apply to GCS hardware
//     (documented exception, like the avionics KiCad files).
// ===========================================================================
/*
 * malcolm_gimbal_mount.scad
 * Antenna mounting plate for Malcolm GCS directional antenna gimbal
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 * Revision: R (2026-06-11)
 *
 * Description:
 *   CF-PETG mounting plate that carries the 9 dBi 915 MHz Yagi (for SiK+LoRa)
 *   and the 14 dBi 5 GHz WiFi flat panel antenna on the tilt stage pivot.
 *   The plate pivots on the 4 mm CF rod through the tilt yoke MF104ZZ bearings.
 *
 *   Antenna layout (looking aft along antenna bore-sight):
 *     - Yagi:  centre of plate, top half; M4 U-bolt clamps at two points
 *     - Panel: centre of plate, lower half; 4× M4 threads at panel corners
 *
 *   Pivot boss: 4 mm bore CF rod, flanged hub at each end of the plate
 *   that slides over the MF104ZZ inner races.
 *
 *   Diametrically-magnetised disc magnet (6×2 mm, N42) pressed into pivot
 *   hub end-face for AS5600 encoder reading.
 *
 * Material: CF-PETG, 0.15 mm layers, 40% infill, 4 perimeters
 *
 * Mesh verification: run after every geometry change.
 *   openscad -o malcolm_gimbal_mount.stl malcolm_gimbal_mount.scad
 *   python3 tools/validate_stls.py
 */

/* ---------------------------------------------------------------------------
 * Plate geometry
 * ---------------------------------------------------------------------------*/
PLATE_W     = 80.0;  /* Plate total width (pivot axis span) mm             */
PLATE_H     = 200.0; /* Plate height mm — tall enough for both antennas     */
PLATE_T     = 6.0;   /* Plate thickness mm (CF-PETG structural)             */
CORNER_R    = 4.0;   /* Corner radius mm                                    */

/* ---------------------------------------------------------------------------
 * Pivot boss (flanged hub, one each end of pivot axis)
 * ---------------------------------------------------------------------------*/
HUB_OD      = 12.0;  /* Hub outer diameter mm (press onto MF104ZZ inner race) */
HUB_ID      = 4.1;   /* CF rod slip-fit bore mm (4.0 mm rod + 0.1 clearance) */
HUB_L       = 8.0;   /* Hub axial length mm                                  */
MAGNET_D    = 6.1;   /* Encoder magnet pocket diameter mm (6 mm disc + 0.1)  */
MAGNET_H    = 2.2;   /* Encoder magnet pocket depth mm (2 mm disc + 0.2)     */

/* ---------------------------------------------------------------------------
 * Yagi antenna clamp positions (U-bolt pattern, two stations along plate)
 * Yagi boom diameter assumed 15 mm (adjust UBOLT_D if different)
 * ---------------------------------------------------------------------------*/
UBOLT_D         = 15.5; /* U-bolt inner span mm (boom OD + 0.5 clearance)   */
UBOLT_HOLE_D    = 4.5;  /* U-bolt threaded rod clearance hole mm (M4)       */
UBOLT_PITCH     = 18.0; /* U-bolt leg centre-to-centre mm (M4 U-bolt 15mm span) */
YAGI_STATION_1  = PLATE_H / 2 + 40; /* Upper clamp Y position from plate centre mm */
YAGI_STATION_2  = PLATE_H / 2 + 10; /* Lower clamp Y position from plate centre mm */

/* ---------------------------------------------------------------------------
 * WiFi panel mounting (4× M4 holes in 55×55 mm pattern — standard VESA-like)
 * ---------------------------------------------------------------------------*/
PANEL_MOUNT_PITCH = 55.0; /* Panel mounting hole pitch (square) mm         */
PANEL_HOLE_D      = 4.2;  /* M4 clearance mm                               */
PANEL_Y_OFFSET    = -40.0;/* Panel centre offset from plate centre Y mm    */

/* ===========================================================================
 * Modules
 * ===========================================================================*/

module pivot_hub(side) {
    /*
     * Flanged pivot hub at one end of the plate (side = +1 port, -1 stbd).
     * Hub extends beyond the plate face; magnet pocket in the outer face.
     */
    translate([side * PLATE_W / 2, 0, PLATE_T / 2]) {
        rotate([0, 90 * side, 0]) {
            difference() {
                cylinder(d = HUB_OD, h = HUB_L, $fn = 32);
                /* CF rod bore */
                translate([0, 0, -0.1]) {
                    cylinder(d = HUB_ID, h = HUB_L + 0.2, $fn = 16);
                }
                /* Encoder magnet pocket in outer face */
                translate([0, 0, HUB_L - MAGNET_H]) {
                    cylinder(d = MAGNET_D, h = MAGNET_H + 0.1, $fn = 16);
                }
            }
        }
    }
}

module ubolt_clamp_plate(y_pos) {
    /*
     * Reinforcing boss at each U-bolt clamp station.
     * Includes two M4 clearance holes for U-bolt legs.
     */
    translate([0, y_pos, PLATE_T]) {
        difference() {
            cube([UBOLT_PITCH + 12, 14, 8], center = true);
            for (xi = [-1, 1]) {
                translate([xi * UBOLT_PITCH / 2, 0, -4.1]) {
                    cylinder(d = UBOLT_HOLE_D, h = 9, $fn = 12);
                }
            }
        }
    }
}

module mount_plate() {
    /*
     * Complete antenna mounting plate with pivot hubs, clamp bosses, and
     * WiFi panel mounting holes.
     */
    difference() {
        union() {
            /* Main plate */
            hull() {
                for (xi = [-1, 1]) {
                    for (yi = [-1, 1]) {
                        translate([xi * (PLATE_W / 2 - CORNER_R),
                                   yi * (PLATE_H / 2 - CORNER_R), 0]) {
                            cube([CORNER_R * 2, CORNER_R * 2, PLATE_T], center = true);
                        }
                    }
                }
            }

            /* Pivot hubs at plate ends */
            pivot_hub(+1);
            pivot_hub(-1);

            /* U-bolt clamp bosses for Yagi */
            ubolt_clamp_plate(PLATE_H / 2 - (PLATE_H - YAGI_STATION_1));
            ubolt_clamp_plate(PLATE_H / 2 - (PLATE_H - YAGI_STATION_2));
        }

        /* WiFi panel M4 mounting holes — 4× at PANEL_MOUNT_PITCH square pattern */
        for (xi = [-1, 1]) {
            for (yi = [-1, 1]) {
                translate([xi * PANEL_MOUNT_PITCH / 2,
                           PANEL_Y_OFFSET + yi * PANEL_MOUNT_PITCH / 2,
                           -0.1]) {
                    cylinder(d = PANEL_HOLE_D, h = PLATE_T + 0.2, $fn = 12);
                }
            }
        }

        /* Weight-reduction lightening holes — 3× on upper half, 2× on lower */
        for (yi = [0.25, 0.5, 0.75]) {
            translate([0, PLATE_H * yi - PLATE_H / 2 + 40, -0.1]) {
                cylinder(d = 20, h = PLATE_T + 0.2, $fn = 24);
            }
        }
    }
}

mount_plate();
