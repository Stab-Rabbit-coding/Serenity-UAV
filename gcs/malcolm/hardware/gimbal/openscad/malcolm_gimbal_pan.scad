/*
 * malcolm_gimbal_pan.scad
 * Pan (azimuth) stage for Malcolm GCS directional antenna gimbal
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 * Revision: Q1 (2026-06-10)
 *
 * Description:
 *   The pan stage rotates the tilt stage + antenna assembly about the vertical
 *   (Z) axis.  It consists of:
 *     - Base plate that mounts to the tripod or mast (M6 bolt pattern)
 *     - 6804 (20×32×7 mm) thin-section bearing pressed into base
 *     - Rotating turret that carries the tilt stage
 *     - DS3218MG servo mounted in the base, driving the turret via a printed
 *       sector gear attached to the turret underside
 *     - AS5600 magnetic encoder PCB pocket on the underside of the turret
 *       (reads the diametrically magnetised disc pressed onto the bearing shaft)
 *     - Travel limits: 0°–355° continuous (5° hard stop gap for wiring relief)
 *
 * Material: CF-PETG, 0.15 mm layers, 40% infill, 4 perimeters
 *
 * Mesh verification: run after every geometry change.
 *   openscad -o malcolm_gimbal_pan.stl malcolm_gimbal_pan.scad
 *   python3 tools/validate_stls.py
 */

/* ---------------------------------------------------------------------------
 * Render mode: 0 = base plate, 1 = rotating turret, 2 = exploded assembly
 * ---------------------------------------------------------------------------*/
RENDER_MODE = 0;

/* ---------------------------------------------------------------------------
 * Bearing (6804 thin-section: 20 mm ID, 32 mm OD, 7 mm width)
 * ---------------------------------------------------------------------------*/
BRG_ID   = 20.0;   /* Inner race bore mm                                  */
BRG_OD   = 32.0;   /* Outer race diameter mm                              */
BRG_W    = 7.0;    /* Bearing width mm                                    */
BRG_PRESS_TOL = 0.02; /* Press-fit interference on housing bore (+ = tighter) */

/* ---------------------------------------------------------------------------
 * Base plate geometry
 * ---------------------------------------------------------------------------*/
BASE_W   = 120.0;  /* Base plate width mm                                  */
BASE_D   = 100.0;  /* Base plate depth mm                                  */
BASE_H   = 12.0;   /* Base plate thickness mm (including bearing housing)  */
BASE_R   = 6.0;    /* Corner radius mm                                     */
MOUNT_HOLE_D = 6.5;/* M6 tripod mount hole diameter mm                    */
MOUNT_PITCH  = 88.0;/* M6 mounting hole pitch (centre-to-centre) mm       */

/* ---------------------------------------------------------------------------
 * Servo pocket (DS3218MG: 40×20×38 mm body; shaft centre at 20×10 mm from
 * mounting face)
 * ---------------------------------------------------------------------------*/
SERVO_W      = 42.0;   /* Pocket width mm (2 mm clearance each side)      */
SERVO_D      = 22.0;   /* Pocket depth mm                                  */
SERVO_H      = 40.0;   /* Pocket depth below base top face mm              */
SERVO_OFFSET_X = 30.0; /* Servo shaft centre offset from bearing centre X mm */

/* ---------------------------------------------------------------------------
 * Sector gear on turret (M=1.0, R=28 mm, 120° arc driven by servo arm pinion)
 * ---------------------------------------------------------------------------*/
SECTOR_R    = 28.0; /* Pitch radius mm                                     */
SECTOR_ARC  = 120;  /* Sweep angle deg — servo ±60° gives 120° pan range  */
SECTOR_W    = 8.0;  /* Gear face width mm                                  */

/* ---------------------------------------------------------------------------
 * Turret geometry
 * ---------------------------------------------------------------------------*/
TURRET_OD   = 80.0; /* Turret outer diameter mm                            */
TURRET_H    = 15.0; /* Turret body height mm                               */
TILT_MOUNT_W = 60.0;/* Width of tilt stage mounting boss on turret top mm  */
TILT_MOUNT_D = 40.0;/* Depth of tilt stage mounting boss mm                */
TILT_MOUNT_H = 6.0; /* Boss protrusion height mm                           */

/* ===========================================================================
 * Modules
 * ===========================================================================*/

module base_plate() {
    /*
     * Base plate with:
     *   - Central bearing housing (outer race press-fit bore)
     *   - Servo pocket
     *   - M6 tripod mounting holes at four corners
     *   - M3 mounting holes for AS5600 encoder PCB on underside
     */
    difference() {
        /* Exterior solid */
        hull() {
            for (xi = [-1, 1]) {
                for (yi = [-1, 1]) {
                    translate([xi * (BASE_W / 2 - BASE_R), yi * (BASE_D / 2 - BASE_R), 0]) {
                        cylinder(r = BASE_R, h = BASE_H, $fn = 32);
                    }
                }
            }
        }

        /* Central bearing housing bore (outer race press-fit) */
        translate([0, 0, -0.1]) {
            cylinder(d = BRG_OD + BRG_PRESS_TOL, h = BRG_W + 0.2, $fn = 48);
        }

        /* Servo pocket */
        translate([SERVO_OFFSET_X, 0, BASE_H - SERVO_H]) {
            cube([SERVO_W, SERVO_D, SERVO_H + 0.1], center = true);
        }

        /* M6 tripod mount holes */
        for (xi = [-1, 1]) {
            for (yi = [-1, 1]) {
                translate([xi * MOUNT_PITCH / 2, yi * MOUNT_PITCH / 2, -0.1]) {
                    cylinder(d = MOUNT_HOLE_D, h = BASE_H + 0.2, $fn = 16);
                }
            }
        }

        /* Wire relief slot from servo pocket to exterior */
        translate([SERVO_OFFSET_X + SERVO_W / 2, 0, BASE_H / 2]) {
            cube([BASE_W - SERVO_OFFSET_X - SERVO_W / 2, 8, BASE_H + 0.2], center = true);
        }
    }
}

module turret() {
    /*
     * Rotating turret: mounts to bearing inner race, carries tilt stage boss
     * on top face, and has sector gear on underside for pan drive.
     */
    difference() {
        union() {
            /* Main disc */
            cylinder(d = TURRET_OD, h = TURRET_H, $fn = 64);

            /* Tilt stage mounting boss on top */
            translate([0, 0, TURRET_H]) {
                cube([TILT_MOUNT_W, TILT_MOUNT_D, TILT_MOUNT_H], center = true);
            }
        }

        /* Bearing inner race bore — slip fit onto shaft */
        translate([0, 0, -0.1]) {
            cylinder(d = BRG_ID + 0.1, h = BRG_W + TURRET_H + 0.2, $fn = 32);
        }

        /* M3 holes for tilt stage attachment — 4× at tilt mount boss corners */
        for (xi = [-1, 1]) {
            for (yi = [-1, 1]) {
                translate([xi * (TILT_MOUNT_W / 2 - 5), yi * (TILT_MOUNT_D / 2 - 5),
                           TURRET_H - 0.1]) {
                    cylinder(d = 3.2, h = TILT_MOUNT_H + 0.2, $fn = 12);
                }
            }
        }
    }
}

/* ===========================================================================
 * Render dispatch
 * ===========================================================================*/
if (RENDER_MODE == 0) {
    base_plate();
} else if (RENDER_MODE == 1) {
    turret();
} else {
    /* Exploded view: base at origin, turret above */
    base_plate();
    translate([0, 0, BASE_H + 20]) {
        turret();
    }
}
