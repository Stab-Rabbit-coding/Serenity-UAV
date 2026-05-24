// ============================================================
// s_cargo_sect_shell24.scad
// Cargo gondola shell for Serenity Rev N 24" hull (s_cargo_sect.stl).
//
// Mounts:
//   CARGO_CAM – 28 mm standard FPV camera, nadir-facing (downward),
//               belly of cargo gondola for payload hoist monitoring.
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// License: CC BY 4.0 – creativecommons.org/licenses/by/4.0
//
// Shell derivation:
//   18" centroid from s_cargo_sect_shell18.scad: (-76.64, -246.47, 56.02)
//   24" centroid = 18" centroid × (2.9294 / 2.1974) = × 1.33333:
//     CX =  -76.64 × 1.33333 = -102.19 mm
//     CY = -246.47 × 1.33333 = -328.63 mm
//     CZ =   56.02 × 1.33333 =   74.70 mm
//   Inner scale factors from s_cargo_sect_shell18.scad (2.5 mm absolute wall):
//     INNER_SX = 0.965771
//     INNER_SY = 0.967263
//     INNER_SZ = 0.959167
//
// Coordinate system (24"-scaled STL world space):
//   X – longitudinal, positive toward nose
//   Y – lateral, positive toward starboard (right)
//   Z – vertical, positive toward dorsal (up)
//
// Note on cargo gondola geometry:
//   The cargo section STL is the below-fuselage cargo gondola.  Its centroid
//   at CY = -328.63 mm places it well below / to the side of the main keel in
//   the original Thingiverse model's coordinate frame.  All mount positions
//   below are in that same 24"-scaled STL world space.
//
// IMPORTANT: All mount positions are estimated.  Verify by rendering in
// OpenSCAD and measuring the gondola belly cross-section before printing.
// ============================================================

SCALE_24  = 2.9294;   // 24" hull scale factor

// ── Cargo shell centroid in 24"-scaled STL world coordinates ─────────────────
CX = -102.19;   // mm
CY = -328.63;   // mm
CZ =   74.70;   // mm

// ── Inner-shell scale factors (preserve 2.5 mm absolute wall thickness) ──────
INNER_SX = 0.965771;
INNER_SY = 0.967263;
INNER_SZ = 0.959167;

// ── Nominal wall thickness (used for aperture depth calculations) ─────────────
WALL_T = 4.0;   // mm (conservative; nominal 2.5 mm + tolerance)

// ── Cargo nadir camera mount dimensions (28 mm standard FPV format) ───────────
//    Camera faces downward (-Z) to monitor payload hoist beneath gondola.
//    28 mm FPV mount: 4× M2 screws on 14×14 mm grid; 16 mm lens aperture.
FPV_BOSS_W  = 28.0;   // mm – square boss footprint
FPV_BOSS_H  =  2.0;   // mm – boss protrusion below gondola belly (into airstream)
FPV_APER_D  = 16.0;   // mm – lens aperture bore
FPV_M2_D    =  2.2;   // mm – M2 screw clearance
FPV_M2_S    = 14.0;   // mm – M2 hole spacing (14×14 mm grid)
FPV_BOARD_W = 20.0;   // mm – camera PCB pocket width (square, interior)
FPV_BOARD_D =  5.0;   // mm – camera PCB pocket depth

$fn = 64;

// ── Orientation rotation vectors ──────────────────────────────────────────────
//    Default cylinder axis = +Z.  Rotate to redirect boss toward target axis.
NADIR_ROT = [ 180, 0, 0 ];   // boss points in -Z (downward / ventral)

// ── Cargo nadir camera position ───────────────────────────────────────────────
//    Position is in 24"-scaled STL world space (same frame as CX/CY/CZ above).
//    Gondola belly is approximately CZ − gondola_half_height.
//    VERIFY: measure gondola belly Z-coordinate in slicer after rendering.
CARGO_CAM_POS = [ -102, -329, 35 ];   // VERIFY; Z=35 mm estimated gondola belly

// ── Module: fpv_boss ─────────────────────────────────────────────────────────
//    Square raised boss for 28 mm FPV camera; union into outer shell.
// ────────────────────────────────────────────────────────────────────────────
module fpv_boss(pos, rot) {
    translate(pos)
    rotate(rot)
    translate([-FPV_BOSS_W / 2, -FPV_BOSS_W / 2, 0])
    cube([FPV_BOSS_W, FPV_BOSS_W, FPV_BOSS_H]);
}

// ── Module: fpv_cut ──────────────────────────────────────────────────────────
//    Lens aperture bore + 4× M2 through-holes + PCB pocket; subtract from union.
// ────────────────────────────────────────────────────────────────────────────
module fpv_cut(pos, rot) {
    translate(pos)
    rotate(rot)
    translate([0, 0, -(WALL_T + 1)]) {
        // Lens aperture bore
        cylinder(h = WALL_T + FPV_BOSS_H + 2, d = FPV_APER_D);
        // 4× M2 through-holes at 14×14 mm grid
        for (dx = [-FPV_M2_S / 2, FPV_M2_S / 2])
        for (dy = [-FPV_M2_S / 2, FPV_M2_S / 2])
            translate([dx, dy, 0])
            cylinder(h = WALL_T + FPV_BOSS_H + 2, d = FPV_M2_D);
        // Camera PCB pocket on interior face (gondola interior)
        translate([-FPV_BOARD_W / 2, -FPV_BOARD_W / 2, 0])
        cube([FPV_BOARD_W, FPV_BOARD_W, FPV_BOARD_D + 1]);
    }
}

// ══════════════════════════════════════════════════════════════════════════════
// Main geometry
// ══════════════════════════════════════════════════════════════════════════════
difference() {
    union() {
        // ── Canonical 24" cargo gondola shell ─────────────────────────────
        difference() {
            scale([SCALE_24, SCALE_24, SCALE_24])
                import("../../thingverse-serenity/files/s_cargo_sect.stl");

            translate([CX, CY, CZ])
            scale([INNER_SX, INNER_SY, INNER_SZ])
            translate([-CX, -CY, -CZ])
            scale([SCALE_24, SCALE_24, SCALE_24])
                import("../../thingverse-serenity/files/s_cargo_sect.stl");
        }

        // ── Nadir camera boss (protrudes downward from gondola belly) ──────
        fpv_boss(CARGO_CAM_POS, NADIR_ROT);
    }

    // ── Camera aperture and through-holes ─────────────────────────────────
    fpv_cut(CARGO_CAM_POS, NADIR_ROT);
}
