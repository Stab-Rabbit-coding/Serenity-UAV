// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Hull frame (canonical for ALL design artifacts): X = +port (left),
//   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
//   world origin.  Primary-component STLs published to airframe/stls/
//   are stored directly in hull frame, baked by tools/bake_hull_frame.py
//   (marker 'SerenityUAV HULL-FRAME R1' in the binary STL header).
//   NEVER re-bake a mesh derived from an already-baked file.
//   This file:
//     Skipper ground-support equipment - part-local print frame.  The
//     aircraft hull-frame standard does not apply to GCS hardware
//     (documented exception, like the avionics KiCad files).
// ===========================================================================
/*
 * skipper_gimbal_tilt.scad
 * Tilt (elevation) stage for Skipper GCS directional antenna gimbal
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 * Revision: R (2026-06-11)
 *
 * Description:
 *   The tilt stage rotates the antenna mounting plate about the horizontal
 *   (Y) axis.  It consists of:
 *     - Yoke frame that bolts to the pan turret top boss
 *     - Antenna mount plate (from skipper_gimbal_mount.scad) pivots on a
 *       4 mm CF pivot rod through two MF104ZZ bearings in the yoke ears
 *     - DS3218MG servo mounted in the yoke body, driving the mount plate
 *       via a pushrod / sector gear
 *     - AS5600 magnetic encoder in the yoke, reading a disc magnet on the
 *       pivot rod for elevation position feedback
 *     - Travel limits: −10° (10° below horizontal) to +90° (vertical up)
 *       Hard stops at −15° and +95° (printed into yoke walls)
 *
 * Material: CF-PETG, 0.15 mm layers, 40% infill, 4 perimeters
 *
 * Mesh verification: run after every geometry change.
 *   openscad -o skipper_gimbal_tilt.stl skipper_gimbal_tilt.scad
 *   python3 tools/validate_stls.py
 */

/* ---------------------------------------------------------------------------
 * Render mode: 0 = yoke, 1 = pivot arm stub (attach to mount plate), 2 = exploded
 * ---------------------------------------------------------------------------*/
RENDER_MODE = 0;

/* ---------------------------------------------------------------------------
 * Pivot rod and bearings (same MF104ZZ as nacelle pivot — M1 reuse)
 * ---------------------------------------------------------------------------*/
PIVOT_D     = 4.0;  /* CF pivot rod OD mm                                  */
BRG_OD      = 10.0; /* MF104ZZ bearing OD mm                               */
BRG_ID      = 4.0;  /* MF104ZZ bearing ID mm                               */
BRG_W       = 4.0;  /* MF104ZZ bearing width mm                            */
BRG_PRESS_TOL = 0.02;

/* ---------------------------------------------------------------------------
 * Yoke geometry
 * ---------------------------------------------------------------------------*/
YOKE_W      = 100.0; /* Yoke total width (ear tip to ear tip) mm           */
YOKE_D      = 50.0;  /* Yoke depth (fore-aft) mm                           */
YOKE_BASE_H = 18.0;  /* Yoke base height (below pivot axis) mm             */
EAR_W       = 12.0;  /* Ear plate thickness mm                             */
EAR_H       = 40.0;  /* Ear plate height above base mm                     */
PIVOT_Z     = YOKE_BASE_H + EAR_H / 2; /* Pivot axis height from yoke base mm */

/* ---------------------------------------------------------------------------
 * Servo pocket (DS3218MG, same as aircraft nacelle servos)
 * ---------------------------------------------------------------------------*/
SERVO_W     = 42.0;
SERVO_D     = 22.0;
SERVO_H     = 36.0;  /* Depth pocket below yoke top face                   */

/* ---------------------------------------------------------------------------
 * Base attachment (bolts to pan turret TILT_MOUNT boss from skipper_gimbal_pan.scad)
 * ---------------------------------------------------------------------------*/
BASE_BOSS_W = 60.0;  /* Must match TILT_MOUNT_W in pan SCAD               */
BASE_BOSS_D = 40.0;  /* Must match TILT_MOUNT_D in pan SCAD               */
BASE_BOSS_H = 6.0;   /* Matching socket depth mm                           */

/* ===========================================================================
 * Modules
 * ===========================================================================*/

module bearing_pocket(x, y, z) {
    /*
     * MF104ZZ press-fit pocket in ear wall.
     * Centred at (x, y, z) with bore along Y axis.
     */
    translate([x, y, z]) {
        rotate([90, 0, 0]) {
            cylinder(d = BRG_OD + BRG_PRESS_TOL, h = BRG_W + 0.1, center = true, $fn = 32);
        }
    }
}

module yoke() {
    /*
     * Yoke frame: U-shaped with flat base and two ears.  Servo mounts in the
     * base body.  Pivot rod runs through both ears along the Y axis.
     */
    difference() {
        union() {
            /* Base body */
            translate([0, 0, YOKE_BASE_H / 2]) {
                cube([YOKE_W, YOKE_D, YOKE_BASE_H], center = true);
            }

            /* Left ear */
            translate([-YOKE_W / 2 + EAR_W / 2, 0, YOKE_BASE_H + EAR_H / 2]) {
                cube([EAR_W, YOKE_D, EAR_H], center = true);
            }

            /* Right ear */
            translate([YOKE_W / 2 - EAR_W / 2, 0, YOKE_BASE_H + EAR_H / 2]) {
                cube([EAR_W, YOKE_D, EAR_H], center = true);
            }
        }

        /* Bearing pockets in ears */
        bearing_pocket(-YOKE_W / 2 + EAR_W / 2, 0, PIVOT_Z);
        bearing_pocket( YOKE_W / 2 - EAR_W / 2, 0, PIVOT_Z);

        /* Servo pocket in base body */
        translate([15, 0, YOKE_BASE_H - SERVO_H / 2]) {
            cube([SERVO_W, SERVO_D, SERVO_H + 0.1], center = true);
        }

        /* Base attachment socket (receives pan turret TILT_MOUNT boss) */
        translate([0, 0, -0.1]) {
            cube([BASE_BOSS_W + 0.2, BASE_BOSS_D + 0.2, BASE_BOSS_H + 0.1], center = true);
        }

        /* M3 bolt holes through base for turret attachment (4×) */
        for (xi = [-1, 1]) {
            for (yi = [-1, 1]) {
                translate([xi * (BASE_BOSS_W / 2 - 5), yi * (BASE_BOSS_D / 2 - 5), -0.1]) {
                    cylinder(d = 3.2, h = BASE_BOSS_H + YOKE_BASE_H + 0.2, $fn = 12);
                }
            }
        }

        /* Wire relief from servo pocket to yoke exterior */
        translate([15 + SERVO_W / 2, 0, YOKE_BASE_H / 2]) {
            cube([YOKE_W - 30 - SERVO_W / 2 + 1, 8, YOKE_BASE_H + 0.2], center = true);
        }
    }
}

/* ===========================================================================
 * Render dispatch
 * ===========================================================================*/
if (RENDER_MODE == 0) {
    yoke();
} else {
    /* Exploded — tilt yoke only for now; antenna mount plate in separate SCAD */
    yoke();
}
