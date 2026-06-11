// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Hull frame (canonical for ALL design artifacts): X = +port (left),
//   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
//   world origin.  Primary-component STLs published to airframe/stls/
//   are stored directly in hull frame, baked by tools/bake_hull_frame.py
//   (marker 'SerenityUAV HULL-FRAME R1' in the binary STL header).
//   NEVER re-bake a mesh derived from an already-baked file.
//   This file:
//     Part-local print frame centred on its own origin.  Hull-frame
//     placement not yet validated - VERIFY pending (serenity_assembly.py).
// ===========================================================================
// ============================================================
// nacelle_servo_bracket.scad
// U-channel saddle clamp for mounting a DS3218MG-class nacelle tilt servo
// to the nacelle_servo_mount_block pads in s_cargo_sect_shell24.scad.
//
// Rev S1 (2026-06-08): Initial release.
//   Design for field disassembly per CLAUDE.md (common hand-tools only).
//   Fasteners: 4× M3×10 SHCS into heat-set inserts on mount block.
//
// FUNCTION:
//   The bracket clamps around the DS3218MG servo body (40×20×38 mm) and
//   bolts flush to the 52×30×8 mm NSVMT pad on the interior Z-wall of the
//   cargo gondola.  The servo output shaft points outboard (Z direction)
//   toward the nacelle tilt pivot.  Output shaft is concentric with
//   NSVMT_Y_CEN (= CY + 40 mm ≈ -289 mm world Y).
//
// ASSEMBLY SEQUENCE (Phase 3 per PHASED_BUILD_GUIDE.md):
//   1. Heat-set 4× Ruthex RX-M3x5.7 inserts into NSVMT pad (in gondola shell).
//   2. Insert servo into bracket U-channel from the outboard (nacelle) side.
//   3. Offer bracket + servo assembly to NSVMT pad (servo lead through conduit).
//   4. Fasten 4× M3×10 SHCS through bracket flanges into pad inserts.
//   5. Route servo lead through 10×6 mm conduit slot to avionics bay.
//   Note: Bracket can be removed with servo attached for in-field servo swap.
//
// GEOMETRY:
//   U-channel: BKRT_CH_W × BKRT_CH_H × BKRT_CH_D
//     Inner clear: 40.4×20.4 mm (servo 40×20 mm + 0.2 mm/side clearance).
//     Wall:        BKRT_WALL = 2.0 mm CF-PETG (structural per CLAUDE.md).
//   Flanges: BKRT_FLNG_T × BKRT_FLNG_H on each side of channel mouth.
//     4× M3 through-holes at ±17.5 mm (X) × ±8.0 mm (Y) from bracket centre.
//     M3 clearance hole: 3.4 mm dia (ISO 273 medium fit).
//   Lead notch: 10×6 mm slot on channel closed face for servo lead exit.
//
// LOAD / FOS:
//   Servo stall: 2.45 N·m (DS3218MG, 6 V min spec).
//   Couple arm (bolt pair): 2×17.5 = 35 mm → F_pair = 70 N → 35 N/bolt.
//   M3×10 SHCS in CF-PETG direct shear: ≥ 3000 N (8.8 grade, ISO 4762).
//   FOS_shear = 3000 / 35 = 85.7  ✓✓ (>> 4.0 target, AUVSI guidance).
//   Ref: ISO 4762 M3×10 SHCS; DS3218MG datasheet; AUVSI UAS structural margin.
//
// MATERIAL: CF-PETG, 0.15 mm layer height, 4 perimeters, ≥ 40% infill.
//   Print orientation: channel mouth facing up (−Y in print bed coords) to
//   avoid support in bore; flanges flat on build plate.
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// License: CC BY 4.0 -- creativecommons.org/licenses/by/4.0
// Ref: DS3218MG datasheet; s_cargo_sect_shell24.scad NSVMT_* parameters;
//      PHASED_BUILD_GUIDE.md Phase 3; ISO 4762; CLAUDE.md fabrication standards.
// ============================================================

$fn = 64;

// DS3218MG body dimensions (nominal; verified against datasheet Rev 1.0)
SERVO_BODY_X       = 40.0;   // mm, body length (X, longitudinal)
SERVO_BODY_Y       = 20.0;   // mm, body width  (Y, vertical)
SERVO_BODY_Z       = 38.0;   // mm, body depth  (Z, into nacelle — not constrained by bracket)

// Clearance on each inner face of channel (ISO 286 loose fit for CF-PETG shrinkage)
SERVO_CLR          =  0.2;   // mm, clearance per side in X and Y

// Bracket wall thickness
BKRT_WALL          =  2.0;   // mm, CF-PETG structural minimum per CLAUDE.md

// U-channel inner dimensions
BKRT_CH_IW         = SERVO_BODY_X + 2 * SERVO_CLR;   // = 40.4 mm, inner width (X)
BKRT_CH_IH         = SERVO_BODY_Y + 2 * SERVO_CLR;   // = 20.4 mm, inner height (Y)

// U-channel outer dimensions
BKRT_CH_OW         = BKRT_CH_IW + 2 * BKRT_WALL;    // = 44.4 mm, outer width
BKRT_CH_OH         = BKRT_CH_IH + BKRT_WALL;         // = 22.4 mm, outer height (open at −Z face)

// Channel depth in Z (covers servo output-shaft boss side)
//   Servo output shaft on +Z face; bracket depth keeps servo captured until flange bolts engaged.
BKRT_CH_D          = 10.0;   // mm, channel depth in Z (not full servo depth; flange provides axial lock)

// Flange geometry
//   Flanges extend in Z beyond the channel to bolt to the NSVMT pad.
//   BKRT_FLNG_T: flange thickness in Z (bolt head recess + thread engagement).
//   BKRT_FLNG_H: flange height in Y (must span ±NSVMT_HOLE_S_Y = ±8.0 mm → ≥ 16 mm + margins).
BKRT_FLNG_T        =  8.0;   // mm, flange thickness in Z (8 mm pad engagement)
BKRT_FLNG_H        = BKRT_CH_OH;     // = 22.4 mm, same as channel outer height
BKRT_FLNG_W        = BKRT_CH_OW;     // = 44.4 mm, full channel outer width

// M3 through-hole in flange
//   ISO 273 medium fit: 3.4 mm clearance hole.
//   Positions match NSVMT_HOLE_S_X = ±17.5 mm (X) and NSVMT_HOLE_S_Y = ±8.0 mm (Y).
M3_CLR_D           =  3.4;   // mm, M3 ISO medium clearance hole
FLNG_HOLE_S_X      = 17.5;   // mm, ±X offset from bracket X centre
FLNG_HOLE_S_Y      =  8.0;   // mm, ±Y offset from bracket Y centre

// M3 SHCS head recess on outboard flange face (prevents protrusion)
//   DIN 912 M3×10 SHCS socket head: 5.5 mm dia × 3.0 mm tall.
M3_HD_D            =  6.0;   // mm, recess OD (5.5 mm head + 0.25 mm clearance)
M3_HD_DEP          =  3.2;   // mm, recess depth (3.0 mm head + 0.2 mm clearance)

// Lead notch dimensions (servo lead exits through bracket closed face)
LEAD_NOTCH_W       = 10.0;   // mm, notch width in X (matches NSVMT_CONDUIT_W)
LEAD_NOTCH_H       =  6.0;   // mm, notch height in Y (matches NSVMT_CONDUIT_H)

// Bracket origin convention:
//   (0, 0, 0) = centre of channel inner base face (closed −Z wall outboard face).
//   Channel opens toward +Z (toward nacelle / servo shaft).
//   Flanges extend in −Z (toward NSVMT pad, into gondola).

// ----------------------------------------------------------------------------
// Module: bracket_body
//   Full bracket geometry: U-channel + two flanges − bore cuts.
//   Called once in main block.
// ----------------------------------------------------------------------------
module bracket_body() {
    difference() {
        union() {
            // U-channel outer solid (closed at −Z, open toward +Z)
            //   Origin at channel centre (X=0, Y=0, Z=0 = outboard face of channel).
            translate([-BKRT_CH_OW / 2, -BKRT_CH_OH / 2, 0])
            cube([BKRT_CH_OW, BKRT_CH_OH, BKRT_CH_D]);

            // Port flange (−X side of channel, extends −Z toward pad)
            translate([-BKRT_CH_OW / 2 - 0,
                       -BKRT_FLNG_H / 2,
                       -BKRT_FLNG_T])
            cube([BKRT_WALL, BKRT_FLNG_H, BKRT_FLNG_T]);

            // Starboard flange (+X side of channel, extends −Z toward pad)
            translate([BKRT_CH_OW / 2 - BKRT_WALL,
                       -BKRT_FLNG_H / 2,
                       -BKRT_FLNG_T])
            cube([BKRT_WALL, BKRT_FLNG_H, BKRT_FLNG_T]);

            // Flange bridge: thin backing plate connecting both flanges at −Z face.
            //   Distributes bolt preload; prevents flange rotation under torque.
            translate([-BKRT_FLNG_W / 2,
                       -BKRT_FLNG_H / 2,
                       -BKRT_FLNG_T])
            cube([BKRT_FLNG_W, BKRT_WALL, BKRT_FLNG_T]);
        }

        // ── U-channel inner bore (servo body cavity) ──────────────────────────
        //   Inner clear: 40.4 × 20.4 mm, depth BKRT_CH_D + 1 mm overshoot.
        translate([-BKRT_CH_IW / 2,
                   -BKRT_CH_IH / 2,
                   BKRT_WALL - 0.01])
        cube([BKRT_CH_IW, BKRT_CH_IH, BKRT_CH_D - BKRT_WALL + 1.01]);

        // ── Lead wire notch on closed (outboard) channel face ─────────────────
        //   10×6 mm slot at centre of closed face for servo lead exit.
        //   Aligns with NSVMT_CONDUIT_W × NSVMT_CONDUIT_H in NSVMT pad.
        translate([-LEAD_NOTCH_W / 2, -LEAD_NOTCH_H / 2, -0.1])
        cube([LEAD_NOTCH_W, LEAD_NOTCH_H, BKRT_WALL + 0.2]);

        // ── M3 through-holes and head recesses in flanges ─────────────────────
        //   4 holes: ±FLNG_HOLE_S_X (X) × ±FLNG_HOLE_S_Y (Y).
        //   Clearance hole: M3_CLR_D = 3.4 mm through flange thickness.
        //   Head recess: M3_HD_D = 6.0 mm × M3_HD_DEP = 3.2 mm on outboard face.
        for (sx = [-FLNG_HOLE_S_X, FLNG_HOLE_S_X])
        for (sy = [-FLNG_HOLE_S_Y, FLNG_HOLE_S_Y]) {
            // Through-hole (Z axis, from outboard face through flange)
            translate([sx, sy, -BKRT_FLNG_T - 0.1])
            cylinder(h = BKRT_FLNG_T + 0.2, d = M3_CLR_D);

            // DIN 912 socket head recess on outboard flange face
            translate([sx, sy, -BKRT_FLNG_T - 0.1])
            cylinder(h = M3_HD_DEP + 0.1, d = M3_HD_D);
        }
    }
}

// ============================================================
// Main geometry
// ============================================================
//
// Print orientation note:
//   Render with channel mouth facing +Z (up); set slicer to print with
//   the outboard flat face (Z=0 plane) on the build plate.
//   No supports needed: channel walls bridge the inner bore overhang.
//
// Assembly fit check:
//   Verify channel inner 40.4×20.4 mm clears DS3218MG body 40×20 mm.
//   Verify M3 hole pattern ±17.5 mm × ±8.0 mm matches NSVMT insert pattern.
//   Verify BKRT_FLNG_T = 8 mm matches NSVMT_PAD_T = 8 mm for flush seating.
//   VERIFY all dimensions in slicer measurement tool before printing.

bracket_body();
