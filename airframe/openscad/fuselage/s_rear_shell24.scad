// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Hull frame (canonical for ALL design artifacts): X = +port (left),
//   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
//   world origin.  Primary-component STLs published to airframe/stls/
//   are stored directly in hull frame, baked by tools/bake_hull_frame.py
//   (marker 'SerenityUAV HULL-FRAME R1' in the binary STL header).
//   NEVER re-bake a mesh derived from an already-baked file.
//   This file:
//     Rear (engine cone / pod / skids) section modelled in a part-local
//     frame with the section axial direction along local Z.  The
//     assembly's Rear_Shell mesh (s_rear_shell24_2mm_repaired.stl) is
//     baked to hull frame (90 deg about -X + translation;
//     COMPONENTS['Rear_Shell']).  Baked hull-frame bounds:
//     X -246.0..-105.6, Y +203.2..+383.9, Z +3.4..+160.9 mm.  After
//     regenerating the assembly mesh, re-run:
//         python3 tools/bake_hull_frame.py Rear_Shell
// ===========================================================================
// ============================================================
// s_rear_shell24.scad
// Aft fuselage section shell — Serenity UAV 24" hull.
//
// Rev Q (2026-06-07): Initial SCAD derivation from archived STL.
//   Shell source: archive/stls/fuselage/s_rear_shell24_repaired.stl
//   (solid manifold; pre-hollowed s_rear_shell24_2mm.stl exists in archive
//   but is not used here — hollow is generated via centroid-inset scaling
//   for consistency with head and cargo shell SCAD files.)
//
//   Covers the aft fuselage: engine room (cone), dorsal pod, and port/stbd
//   skid stanchion roots.  Fore joint face (X ≈ -105.6 mm) mates with the
//   middle section horseshoe ring.  Aft face (X ≈ -246 mm) is the tail.
//   The fuselage EDF iris nozzle is deferred; tail cone renders closed.
//
//   6× M3 heat-set insert bosses at fore joint face (X ≈ -105.6 mm),
//   protruding into the interior (toward -X).
//
//   Fill: 2 lb/cf closed-cell foam.  Structural skin: CF-PETG.
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
//
// Print spec:
//   Material: CF-PETG (hardened-steel nozzle required)
//   Layer:    0.15 mm
//   Walls:    4 perimeters
//   Infill:   40% gyroid for boss/rib zones; 25% elsewhere
//
// Coordinate system (24"-scaled STL world space = hull frame per CLAUDE.md):
//   X — lateral,      positive toward port  (left)
//   Y — longitudinal, positive aft (back)
//   Z — vertical,     positive dorsal (up)
//   Station mapping: X_stl = 284 - station_mm
//
// Shell derivation:
//   STL measured bounds of s_rear_shell24_repaired.stl:
//     X = -246.0 .. -105.6  → DX = 140.4 mm
//     Y = -192.9 ..  -35.4  → DY = 157.5 mm
//     Z =    0.0 ..  180.7  → DZ = 180.7 mm
//   Centroid (bounding-box mid-point):
//     CX = -175.80 mm
//     CY = -114.12 mm
//     CZ =   90.36 mm
//   Inner scale: S = (D - 2 × WALL_MM) / D
//     INNER_SX = (140.4 - 4.0) / 140.4 = 0.97150
//     INNER_SY = (157.5 - 4.0) / 157.5 = 0.97460
//     INNER_SZ = (180.7 - 4.0) / 180.7 = 0.97785
//
// M3 boss reference:
//   Ruthex RX-M3x5.7 heat-set insert: 4.0 mm bore, 5.7 mm OD, 5.7 mm installed
//   length.  Boss OD 8.0 mm gives minimum 2-wall annulus (CLAUDE.md).
//   Pullout capacity in CF-PETG: ≈400 N.  Ref: Ruthex datasheet; ISO 14589.
//
// IMPORTANT: All boss positions are estimated from bounding-box geometry.
//   Render in OpenSCAD and verify each boss is fully inside the hull skin
//   before slicing.  Boss positions marked VERIFY.
// ============================================================

$fn = 64;

// ============================================================
// STL source
// ============================================================
STL_PATH = "../../archive/stls/fuselage/s_rear_shell24_repaired.stl";

// ============================================================
// Hull scale factor (24" from 18" Thingiverse base)
// ============================================================
SCALE_24 = 2.9294;

// ============================================================
// Bounding-box centroid in 24"-scaled STL world coordinates
// ============================================================
CX = -175.80;   // mm -- lateral axis (positive = port)
CY = -114.12;   // mm -- longitudinal axis (positive = aft)
CZ =   90.36;   // mm -- vertical axis (positive = dorsal/up)

// ============================================================
// Hollow-shell parameters (2.0 mm foam-fill skin, centroid-inset method)
// ============================================================
WALL_MM  = 2.0;
DX       = 140.4;
DY       = 157.5;
DZ       = 180.7;
INNER_SX = (DX - 2 * WALL_MM) / DX;   // 0.97150
INNER_SY = (DY - 2 * WALL_MM) / DY;   // 0.97460
INNER_SZ = (DZ - 2 * WALL_MM) / DZ;   // 0.97785

// Conservative cutter wall thickness for boss modules
WALL_T = 3.5;   // mm (nominal 2.0 mm + 1.5 mm cutter clearance)

// ============================================================
// M3 heat-set insert boss dimensions
// ============================================================
BOSS_OD     = 8.0;   // mm — boss outer diameter (2-wall annulus per CLAUDE.md)
BOSS_H      = 6.0;   // mm — boss depth from joint face (≥ insert length 5.7 mm)
BOSS_BORE_D = 4.1;   // mm — M3 heat-set bore (4.0 mm nominal + 0.1 mm clearance)

// ============================================================
// Fore joint face boss geometry
// Bosses at X = -105.6 mm (fore face of rear section).
// Cylinder axis along -X (into rear section interior).
// BOSS_FORE_ROT: rotate([0,-90,0]) maps default +Z to -X.
// ============================================================
BOSS_FORE_ROT = [0, -90, 0];

// 6× bosses distributed around the hull cross-section ellipse.
// Radii estimated from DY=157.5, DZ=180.7 at the fore face.
// ALL POSITIONS REQUIRE VERIFICATION IN SLICER.
BOSS_FORE_1 = [ -105.6,  CY + 55,  CZ       ];  // VERIFY: dorsal centreline
BOSS_FORE_2 = [ -105.6,  CY + 27,  CZ + 65  ];  // VERIFY: dorsal-port
BOSS_FORE_3 = [ -105.6,  CY - 27,  CZ + 65  ];  // VERIFY: ventral-port
BOSS_FORE_4 = [ -105.6,  CY - 65,  CZ       ];  // VERIFY: ventral centreline
BOSS_FORE_5 = [ -105.6,  CY - 27,  CZ - 65  ];  // VERIFY: ventral-stbd
BOSS_FORE_6 = [ -105.6,  CY + 27,  CZ - 65  ];  // VERIFY: dorsal-stbd

// ============================================================
// Module: m3_boss
//   M3 heat-set insert boss post.  Solid annular post with bore.
//   Protrudes from the joint face into the section interior.
//   BOSS_FORE_ROT positions the cylinder axis along -X (into aft interior).
//   Ref: Ruthex RX-M3x5.7; ISO 14589; CLAUDE.md 2-wall annulus requirement.
// ============================================================
module m3_boss(pos, rot) {
    translate(pos)
    rotate(rot)
    difference() {
        cylinder(h = BOSS_H, d = BOSS_OD);
        cylinder(h = BOSS_H + 0.1, d = BOSS_BORE_D);
    }
}

// ============================================================
// Module: hollow_shell
//   Outer solid minus centroid-inset scaled copy = 2.0 mm skin.
//   Fore and aft joint faces are open (no cap) by virtue of the
//   STL geometry — the mating annuli are handled at assembly.
// ============================================================
module hollow_shell() {
    difference() {
        import(STL_PATH, convexity = 10);
        translate([CX, CY, CZ])
            scale([INNER_SX, INNER_SY, INNER_SZ])
            translate([-CX, -CY, -CZ])
                import(STL_PATH, convexity = 10);
    }
}

// ============================================================
// Main geometry
// ============================================================
union() {
    // --- 2.0 mm hollow skin ---
    hollow_shell();

    // --- 6× M3 boss posts at fore joint face ---
    // Boss cylinders protrude in -X (into the rear section interior).
    // Verify each boss is inside the hull wall before printing.
    m3_boss(BOSS_FORE_1, BOSS_FORE_ROT);
    m3_boss(BOSS_FORE_2, BOSS_FORE_ROT);
    m3_boss(BOSS_FORE_3, BOSS_FORE_ROT);
    m3_boss(BOSS_FORE_4, BOSS_FORE_ROT);
    m3_boss(BOSS_FORE_5, BOSS_FORE_ROT);
    m3_boss(BOSS_FORE_6, BOSS_FORE_ROT);
}
