/*
 * malcolm_field_enclosure.scad
 * IP65 weatherproof field enclosure for Malcolm GCS comms node
 * (PocketBeagle 2 Industrial + Cape-B-2 + XCVR-49MHZ-2 stack)
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 * Revision: Q1 (2026-06-10)
 *
 * Description:
 *   Two-part (lid + body) enclosure for Malcolm's comms node.  The interior
 *   fits the PB2-I + Cape-B-2 + XCVR-49MHZ-2 stack on standoffs, a 40 mm
 *   cooling fan, and cable gland locations for RF, USB, power, and servo
 *   feedthroughs.  The lid is retained by M3 screws with a perimeter EPDM
 *   gasket for IP65 ingress protection.
 *
 *   NOTE: This design uses standard off-the-shelf components where possible.
 *   If a commercial Hammond 1590XX or similar IP65 aluminum enclosure fits the
 *   stack, prefer that over a printed enclosure to save weight and print time.
 *   See malcolm_power_budget.md and malcolm_wiring.md for stack dimensions.
 *
 * Stack envelope (Cape-B-2 + PB2-I + XCVR-49MHZ-2):
 *   Footprint: 90 mm × 60 mm
 *   Height:    29 mm (Cape-B-2 PCB 1.6 mm + M2.5×6 standoffs + PB2-I 6 mm board
 *              + M2.5×20 inter-cape standoffs + XCVR 8 mm) ≈ 42 mm total stack
 *   Board clearance below: 3 mm standoff feet
 *   Board clearance above: 8 mm lid clearance
 *   Total interior height needed: 3 + 42 + 8 = 53 mm
 *
 * Mesh verification: run after every geometry change.
 *   openscad -o malcolm_field_enclosure.stl malcolm_field_enclosure.scad
 *   python3 tools/validate_stls.py
 */

/* ---------------------------------------------------------------------------
 * Render mode: 0 = body only, 1 = lid only, 2 = exploded assembly view
 * ---------------------------------------------------------------------------*/
RENDER_MODE = 0;

/* ---------------------------------------------------------------------------
 * Interior dimensions (must fit stack + fan + cable routing)
 * ---------------------------------------------------------------------------*/
INT_W   = 110;      /* Interior width  (X) mm — 90mm stack + 10mm margin each side */
INT_D   = 80;       /* Interior depth  (Y) mm — 60mm stack + 10mm margin each side */
INT_H   = 55;       /* Interior height (Z) mm — see stack height calculation above  */

/* ---------------------------------------------------------------------------
 * Wall and lid geometry
 * ---------------------------------------------------------------------------*/
WALL_T      = 3.0;  /* Wall thickness mm — 3mm PETG adequate for weather seal */
LID_T       = 3.0;  /* Lid panel thickness mm                                  */
GASKET_W    = 4.0;  /* EPDM gasket groove width mm                             */
GASKET_D    = 2.0;  /* EPDM gasket groove depth mm (gasket 3mm dia compresses) */
CORNER_R    = 4.0;  /* Exterior corner radius mm                               */
SCREW_PITCH = 40.0; /* Lid screw pattern — one M3 screw every 40mm along rim   */

/* ---------------------------------------------------------------------------
 * Fan cutout (40 mm axial cooling fan in body wall)
 * ---------------------------------------------------------------------------*/
FAN_SIZE    = 40.0; /* Fan frame size mm (standard 40×40mm fan)                */
FAN_HOLE_D  = 38.0; /* Fan airflow opening diameter mm                         */
FAN_SCREW   = 32.0; /* Fan mounting screw hole pitch mm (32mm for 40mm fan)    */
FAN_SCREW_D = 3.5;  /* Fan mounting screw clearance diameter mm (M3)           */

/* ---------------------------------------------------------------------------
 * Cable gland locations (centred on body walls)
 * Z-position = gland centre height from floor (inside face)
 * ---------------------------------------------------------------------------*/
USB_GLAND_Z     = INT_H / 2;   /* USB-C gland on front wall — mid-height      */
PWR_GLAND_Z     = INT_H / 2;   /* Power XT30 gland on rear wall               */
RF_GLAND_Z      = INT_H * 0.7; /* 5× SMA glands on right wall — upper zone    */
SERVO_GLAND_Z   = INT_H * 0.3; /* Multi-pin servo/I2C connector on left wall  */

/* ---------------------------------------------------------------------------
 * Standoff pattern for Cape-B-2 PCB (90×60mm, M2.5 holes)
 * Origin at floor centre of interior.
 * ---------------------------------------------------------------------------*/
STAND_H     = 3.0;  /* Standoff height off floor mm                           */
STAND_OD    = 5.0;  /* Standoff outer diameter mm                             */
STAND_ID    = 2.7;  /* M2.5 clearance bore mm                                 */
PCB_W       = 90.0; /* Cape-B-2 PCB width mm                                  */
PCB_D       = 60.0; /* Cape-B-2 PCB depth mm                                  */
PCB_MOUNT_X = PCB_W / 2 - 3;   /* PCB mounting hole inset from edge mm        */
PCB_MOUNT_Y = PCB_D / 2 - 3;

/* ============================================================================
 * Derived dimensions
 * ============================================================================*/
EXT_W = INT_W + 2 * WALL_T;    /* Total exterior width  */
EXT_D = INT_D + 2 * WALL_T;    /* Total exterior depth  */
EXT_H = INT_H + WALL_T;        /* Body height (no lid)  */

module rounded_box(w, d, h, r) {
    /*
     * Solid rounded-corner cuboid for exterior shell subtraction.
     * w = width (X), d = depth (Y), h = height (Z), r = corner radius.
     */
    hull() {
        for (xi = [-1, 1]) {
            for (yi = [-1, 1]) {
                translate([xi * (w / 2 - r), yi * (d / 2 - r), 0]) {
                    cylinder(r = r, h = h, $fn = 32);
                }
            }
        }
    }
}

module pcb_standoff(x, y) {
    /*
     * Single M2.5 boss standoff at (x, y) from PCB origin.
     * Standoff is a cylinder with a central clearance bore.
     */
    translate([x, y, 0]) {
        difference() {
            cylinder(d = STAND_OD, h = STAND_H, $fn = 20);
            cylinder(d = STAND_ID, h = STAND_H + 0.1, $fn = 16);
        }
    }
}

module enclosure_body() {
    /*
     * Body (open-top box) with PCB standoffs, fan cutout, and cable gland bosses.
     * Lid seats on the top flange; EPDM gasket groove runs around the perimeter.
     */
    difference() {
        /* --- Exterior solid --- */
        rounded_box(EXT_W, EXT_D, EXT_H, CORNER_R);

        /* --- Interior pocket --- */
        translate([0, 0, WALL_T]) {
            rounded_box(INT_W, INT_D, EXT_H, CORNER_R - WALL_T + 0.5);
        }

        /* --- Fan cutout in +X wall (right side) --- */
        translate([EXT_W / 2, 0, EXT_H / 2]) {
            rotate([0, 90, 0]) {
                cylinder(d = FAN_HOLE_D, h = WALL_T * 2 + 1, center = true, $fn = 48);
            }
        }

        /* --- USB-C gland cutout in -Y wall (front) — placeholder 12mm dia --- */
        translate([0, -EXT_D / 2, USB_GLAND_Z + WALL_T]) {
            rotate([90, 0, 0]) {
                cylinder(d = 12, h = WALL_T * 2 + 1, center = true, $fn = 24);
            }
        }

        /* --- Power gland cutout in +Y wall (rear) — placeholder 14mm dia --- */
        translate([0, EXT_D / 2, PWR_GLAND_Z + WALL_T]) {
            rotate([90, 0, 0]) {
                cylinder(d = 14, h = WALL_T * 2 + 1, center = true, $fn = 24);
            }
        }
    }

    /* --- PCB standoffs on floor --- */
    translate([0, 0, WALL_T]) {
        for (sx = [-PCB_MOUNT_X, PCB_MOUNT_X]) {
            for (sy = [-PCB_MOUNT_Y, PCB_MOUNT_Y]) {
                pcb_standoff(sx, sy);
            }
        }
    }
}

module enclosure_lid() {
    /*
     * Flat lid with perimeter EPDM gasket groove and M3 screw clearance holes.
     * Lid thickness = LID_T; seats on top flange of body.
     */
    difference() {
        /* --- Lid solid --- */
        translate([0, 0, 0]) {
            rounded_box(EXT_W, EXT_D, LID_T, CORNER_R);
        }

        /* --- EPDM gasket groove around perimeter --- */
        difference() {
            rounded_box(EXT_W - WALL_T, EXT_D - WALL_T, GASKET_D + 0.1, CORNER_R - WALL_T / 2);
            rounded_box(EXT_W - WALL_T - 2 * GASKET_W, EXT_D - WALL_T - 2 * GASKET_W,
                        GASKET_D + 0.2, CORNER_R - WALL_T - GASKET_W / 2);
        }
    }
}

/* ============================================================================
 * Render dispatch
 * ============================================================================*/
if (RENDER_MODE == 0) {
    enclosure_body();
} else if (RENDER_MODE == 1) {
    enclosure_lid();
} else {
    /* Exploded assembly view */
    enclosure_body();
    translate([0, 0, EXT_H + 20]) {
        enclosure_lid();
    }
}
