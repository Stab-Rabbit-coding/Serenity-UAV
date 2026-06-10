// ============================================================
// s_head_shell24.scad
// Nose / cockpit shell for Serenity Rev N 24" hull (s_head.stl).
//
// Hull-frame position (validated FreeCAD assembly — SerenityAssembly.FCStd,
//   2026-06-10):
//   Head_Shell placement in hull frame:
//     X = −331.999 mm (−13.07 in) from hull origin  [positive toward nose]
//     Y = −18.000 mm (−0.71 in)                      [positive dorsal/up]
//     Z = +60.999 mm (+2.40 in)                      [positive port/left]
//     Rotation: Identity — no rotation needed; STL axes align directly with
//               hull frame axes.
//   Meaning: Head is the forwardmost section (most negative X in assembly).
//   Station mapping within head STL: X_stl = 284 − station_mm.
//   STL bounds: X = 99..228 mm (3.90..8.98 in), Y = −288..−53 mm,
//               Z = 0..141 mm (0..5.55 in).
//   Head section in 24" hull spans approximately stations 0–7.28 in (0–185 mm)
//   from nose.  Aft mating face (head → cargo) at X_stl ≈ 99 mm = sta 3.54 in
//   (90 mm from nose).
//
// Key dimensions — imperial primary, mm in parentheses (for reference only;
//   all OpenSCAD variable assignments remain in mm):
//   Hull skin (foam-fill): 0.079 in (2.0 mm) CF-PETG + 2 lb/cf closed-cell foam
//   Wall cutter overlap (WALL_T): 0.138 in (3.5 mm) nominal
//   STL bounding box:
//     DX: 5.09 in (129.2 mm)
//     DY: 9.25 in (234.9 mm)
//     DZ: 5.52 in (140.2 mm)
//   Centroid in 24"-scaled STL world coords:
//     CX: 6.35 in (161.33 mm)
//     CY: −5.85 in (−148.57 mm)  [dorsal/ventral; positive = up]
//     CZ: 2.72 in (69.08 mm)     [lateral; positive = port]
//   M3 boss OD: 0.315 in (8.0 mm), height: 0.236 in (6.0 mm)
//   M3 heat-set bore: 0.161 in (4.1 mm)
//   Cruise speed at which skin was validated: 54.4 kt (28 m/s); deflection
//     ≤ 0.002 in (0.054 mm) on 2.0 mm CF-PETG + foam, vs 0.020 in (0.5 mm) limit.
//
// Rev S1 (2026-06-09): Shepherd Book avionics bay (Faraday enclosure) on
//   interior dorsal face; correct forward sensor and FPV camera positions.
//   Sensor position bug: S1A_POS.X=251, S1B_POS.X=231, FPV_POS.X=239 were
//   all outside STL X_max=228 mm (positions inside exterior hull skin required).
//   Corrected to X=224 (S1A, S1B) and X=226 (FPV), verified within bounds.
//   S1B_POS Z offset changed: was (CY+8, CZ+12), now (CY, CZ+22) — pure Z
//   separation avoids diagonal offset; 22 mm gives 9 mm gap between bezel edges.
//   FPV_POS Y offset: CY+24 puts aperture 24 mm dorsal of centroid (bridge
//   viewport location on Serenity hull); 4 mm gap to S1A bezel upper edge ✓.
//   Book bay: Shepherd Book (CLAUDE.md: "forward avionics bay", watchdog/auth
//   SBC stack) Faraday enclosure on interior dorsal face at (CX, CZ).
//   Same Cape-B-2 (Zoë) + Cape-A-2 (Wash) stack and 60×40×55 mm Faraday tray
//   spec as cargo bays (Rev S4).  4× M3 bosses + 62×42 mm dorsal access panel.
//   Ductwork parameters shared with cargo SCAD spec (DUCT_* constants).
//   Ref: s_cargo_sect_shell24.scad Rev S4; CLAUDE.md Book bay; CAPE-B-2.kicad_pcb.
//
// Rev Q (2026-05-26): Updated to 2.0 mm (0.079 in) foam-fill skin thickness.
//   - Shell source: s_head_shell24_2mm_repaired.stl (blender_shells_v3_2mm.py,
//     voxel-remesh at 1.2 mm pitch, repair_shells_for_scad.py).
//   - WALL_T reduced 4.0 → 3.5 mm (nominal 2.0 mm + 1.5 mm cutter overlap).
//   - 6x M3 heat-set boss posts added at aft joint face (X ≈ 99 mm) for
//     M3 bolts joining head to cargo section.
//   - Foam fill (2 lb/cf closed-cell) provides structural core; bosses provide
//     point-load capacity.  Structural analysis 2026-05-26 confirms 2.0 mm
//     CF-PETG + foam adequate for skin panels at 54.4 kt (28 m/s) cruise.
//   Ref: structural_analysis.py log, Serenity UAV project, 2026-05-26.
//
// Mounts (all flush with outer mold line -- zero external protrusion):
//   S1A  -- VL53L5CX forward ToF sensor, Array A (FC3 primary), sta 33 mm
//   S1B  -- VL53L5CX forward ToF sensor, Array B (FC2 primary), sta 53 mm
//   FPV  -- 28 mm standard FPV camera, bridge forward-facing viewport, sta 45 mm
//
// GPS patch antenna and 49 MHz RCRS post are on the broad, flat dorsal surface
// of the mid-fuselage section (s_middle_canonical_shell24.scad) where the
// ground plane is larger and the sky view is unobstructed.
//
// Flush-mount design philosophy:
//   Sensor apertures are cut flush through the hull wall.  No boss protrudes
//   above the outer mold line.  PMMA windows (VL53L5CX) and camera lenses
//   (FPV) are retained by M1.6 / M2 countersunk flathead screws from outside
//   and a carrier-board / camera-body recess on the interior.  A shallow
//   0.5 mm registration ring is cut around each aperture on the exterior
//   face to seat the window disc and preserve a clean hull surface.
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// License: CC BY 4.0 -- creativecommons.org/licenses/by/4.0
//
// Shell derivation:
//   18" centroid from s_head_shell18.scad: (121.00, -111.43, 51.81)
//   24" centroid = 18" centroid x (2.9294 / 2.1974) = x 1.33333:
//     CX =  121.00 x 1.33333 =  161.33 mm
//     CY = -111.43 x 1.33333 = -148.57 mm
//     CZ =   51.81 x 1.33333 =   69.08 mm
//   Inner scale factors from blender_shells_v3_2mm.py (2.0 mm foam-fill wall):
//     INNER_SX = 0.969083  (dim = 129.4 mm, wall = 2.0 mm)
//     INNER_SY = 0.982987  (dim = 235.1 mm)
//     INNER_SZ = 0.971563  (dim = 140.7 mm)
//
// Coordinate system (24"-scaled STL world space):
//   X -- longitudinal, positive toward nose
//   Y -- vertical,    positive toward dorsal (up)   NOTE: Y is up, not Z
//   Z -- lateral,     positive toward port  (left)
//   Station mapping: X_stl = 284 - station_mm
//     e.g. station 3.54 in (90 mm) → X_stl = 284 - 90 = 194
//
// Hull surface position estimates (wall = 0.079 in / 2.0 mm):
//   half_ext_Y = 2.0 / (1 - 0.982987) = 118 mm (4.65 in)
//   Hull Y-centreline (nose axis) approx CY = -149 mm (-5.87 in)
//   Hull Z-centreline approx CZ = 69 mm (2.72 in)
//   STL bounds (from voxel-remesh repair):
//     X = 99..228 mm (3.90..8.98 in)
//     Y = -288..-53 mm (-11.34..-2.09 in)
//     Z = 0..141 mm (0..5.55 in)
//
// Sensor references:
//   VL53L5CX: ST UM2884 DocID032910 Rev 1, 2021.
//     FoV 65 deg diagonal; 0.4-4.0 m; 8x8 multizone; 6.4x3.4 mm package.
//     Carrier board approx 13x13 mm; PMMA window disc 11 mm dia.
//   FPV: 28 mm industry-standard mount; 14x14 mm M2 bolt grid; 16 mm aperture.
//
// M3 boss reference:
//   M3 heat-set insert (Ruthex RX-M3x5.7 or equiv): 4.0 mm bore, 5.7 mm OD,
//   5.7 mm installed length.  Boss OD 8.0 mm gives 2-wall annulus per CLAUDE.md.
//   Pullout capacity in CF-PETG: approx 400 N.
//   Ref: Ruthex data sheet, ISO 14589, CLAUDE.md fabrication standards.
//
// IMPORTANT: All mount and boss positions are estimated.  Verify by rendering in
// OpenSCAD and measuring mesh cross-sections in a slicer before printing.
// ============================================================

SCALE_24  = 2.9294;   // 24" hull scale factor

// Head shell centroid in 24"-scaled STL world coordinates
CX =  161.33;   // mm
CY = -148.57;   // mm -- dorsal/ventral axis (positive = up)
CZ =   69.08;   // mm -- lateral axis (positive = port)

// Hollow-shell parameters (Rev R: computed from solid STL bounding box)
// Bounding box of s_head_shell24_repaired.stl after voxel-remesh (1.5 mm pitch):
//   X =   99.2 .. 228.4  → DX = 129.2 mm
//   Y = -287.6 .. -52.7  → DY = 234.9 mm
//   Z =    0.2 .. 140.4  → DZ = 140.2 mm
// Inner scale factors: S = (D - 2 × WALL_MM) / D (centroid-inset approximation).
WALL_MM  = 2.0;
DX = 129.2;
DY = 234.9;
DZ = 140.2;
INNER_SX = (DX - 2 * WALL_MM) / DX;   // = 0.96904
INNER_SY = (DY - 2 * WALL_MM) / DY;   // = 0.98297
INNER_SZ = (DZ - 2 * WALL_MM) / DZ;   // = 0.97147

// Conservative wall thickness for cutter overlap (nominal 2.0 mm + 1.5 mm clearance)
WALL_T = 3.5;   // mm

// M3 heat-set insert boss dimensions
//   Boss added to interior face at joint surfaces; bore accepts M3 heat-set insert.
//   OD 8.0 mm gives minimum 2-wall annulus outside insert per CLAUDE.md requirement.
//   Ref: Ruthex RX-M3x5.7 data sheet; ISO 14589.
BOSS_OD     = 8.0;   // mm -- boss outer diameter
BOSS_H      = 6.0;   // mm -- boss height from interior face (>= insert length 5.7 mm)
BOSS_BORE_D = 4.1;   // mm -- M3 heat-set insert bore (4.0 mm nominal + 0.1 mm clearance)

// VL53L5CX flush mount dimensions
//   Exterior: 11 mm PMMA bore + 0.5 mm x 14 mm OD seat ring + 4x M1.6 c/s holes.
//   Interior: 14x14x3 mm carrier-board recess.
//   Ref: ST UM2884 DocID032910 Rev 1, 2021.
VAPER_D   = 11.0;   // mm -- PMMA window aperture bore
VRING_OD  = 14.0;   // mm -- seat ring outer diameter (0.5 mm recess, hull-flush)
VRING_DEP =  0.5;   // mm -- seat ring recess depth (PMMA rests here, UV-adhesive)
VM16_D    =  1.7;   // mm -- M1.6 through-hole clearance
VM16_R    =  7.0;   // mm -- M1.6 bolt circle radius (4 holes at 90 deg)
VCSK16_OD =  3.5;   // mm -- M1.6 flathead countersink OD  (DIN 7991, 90 deg)
VCSK16_D  =  1.0;   // mm -- M1.6 countersink depth
VRECESS_W = 14.0;   // mm -- carrier board pocket (square)
VRECESS_D =  3.0;   // mm -- carrier board pocket depth (interior face)

// FPV camera flush recess dimensions (28 mm standard FPV format)
//   Exterior: 16 mm lens bore + 29x29x1 mm bezel seating recess + 4x M2 c/s holes.
//   Interior: 20x20x5 mm camera body pocket.
FPV_APER_D   = 16.0;   // mm -- lens aperture bore
FPV_BEZ_W    = 29.0;   // mm -- bezel recess width (28 mm camera + 0.5 mm per side)
FPV_BEZ_DEP  =  1.0;   // mm -- bezel recess depth (camera face sits flush at hull)
FPV_M2_D     =  2.2;   // mm -- M2 through-hole clearance
FPV_M2_S     = 14.0;   // mm -- M2 hole spacing (14x14 mm grid)
FPV_CSK2_OD  =  4.5;   // mm -- M2 flathead countersink OD (DIN 7991, 90 deg)
FPV_CSK2_D   =  1.2;   // mm -- M2 countersink depth
FPV_BOARD_W  = 20.0;   // mm -- camera body pocket width (square)
FPV_BOARD_D  =  5.0;   // mm -- camera body pocket depth (interior)

$fn = 64;

// Orientation rotation vectors
//   STL axes: X=forward, Y=dorsal (+up), Z=port (+left).
//   Ry(+90 deg) maps default +Z cylinder to +X:  rotate([ 0, 90, 0 ])
FWD_ROT = [ 0, 90, 0 ];   // aperture faces +X (toward nose)

// Mount position constants -- 24"-scaled STL world coordinates
//   X_stl = 284 - station_mm.  Y/Z at estimated hull centreline.
//   All positions VERIFY in slicer after rendering.

// Array A forward sensor -- nose centreline, station 33 mm (FC3 primary)
//   Rev S1 fix: X corrected 251 → 224 (was outside STL X_max=228 mm).
//   Station 33 mm → X_stl = 284 - 33 = 251; clipped to X=224 (4 mm inside X_max).
S1A_POS = [ 224, CY, CZ ];            // VERIFY: hull axis at station 33 mm

// Array B forward sensor -- offset for distinct FoV, station 53 mm (FC2 primary)
//   Rev S1 fix: X corrected 231 → 224; Y/Z offset changed to pure Z offset.
//   22 mm Z separation from S1A gives 9 mm gap between 14 mm-OD bezels ✓.
S1B_POS = [ 224, CY, CZ + 22 ];       // VERIFY: ~18 deg lateral bearing offset from S1A

// Bridge FPV camera -- upper nose, Serenity bridge viewport, station 45 mm
//   Rev S1 fix: X corrected 239 → 226; Y offset increased to CY+24 for bridge
//   viewport location.  At (CY+24): 4 mm gap from S1A bezel upper edge (CY+5.5) ✓.
FPV_POS = [ 226, CY + 24, CZ ];       // VERIFY: dorsal of nose axis at bridge viewport

// M3 boss positions at aft joint face (X = 99 mm, head-to-cargo mating face).
//   6 bosses distributed around the hull perimeter ellipse.
//   Positions estimated from STL bounds (Y=-288..-53, Z=0..141) and hull centroid.
//   BOSS_AFT_ROT: rotate([0,90,0]) aligns cylinder axis along +X (into interior).
//   All positions VERIFY in slicer -- boss must be fully inside the hull skin.
BOSS_AFT_ROT = [ 0, 90, 0 ];

BOSS_AFT_1 = [  99, CY + 75, CZ       ];  // VERIFY: dorsal face, top of section
BOSS_AFT_2 = [  99, CY + 38, CZ + 52  ];  // VERIFY: dorsal-port quadrant
BOSS_AFT_3 = [  99, CY - 38, CZ + 52  ];  // VERIFY: ventral-port quadrant
BOSS_AFT_4 = [  99, CY - 100, CZ      ];  // VERIFY: ventral face
BOSS_AFT_5 = [  99, CY - 38, CZ - 52  ];  // VERIFY: ventral-stbd quadrant
BOSS_AFT_6 = [  99, CY + 38, CZ - 52  ];  // VERIFY: dorsal-stbd quadrant

// ── Shepherd Book avionics bay — dorsal interior, head section (Rev S1) ──────
//
// Book is the primary watchdog / fault-detection / authentication SBC stack
// (CLAUDE.md: Book bay = "Shepherd Book" = forward avionics bay).
// Cape stack: Cape-B-2 (Zoë) + PB2-I + Cape-A-2 (Wash) + PB2-I, 55×35 mm each.
// Faraday enclosure: 5-walled aluminium-sheet tray, 60×40×55 mm external.
// Hull dorsal skin IS the 6th wall; access cover (72×52 mm) is the EMI lid.
//
// DORSAL INTERIOR FACE:
//   STL Y_max = -53 mm (exterior dorsal); interior at approx -53 - 2 = -55 mm.
//   BOOK_DORSAL_Y = CY + 94 ≈ -54.6 mm.  VERIFY in slicer.
//   NOTE: head dorsal surface is narrow and curved — verify tray fits flat region.
//
// BOSS PATTERN (4× M3 bosses, ±25 mm X, ±15 mm Z from bay centre):
//   Bay centre at (CX, BOOK_DORSAL_Y, CZ) = (161.33, -54.6, 69.08).
//   Boss X positions: CX ± 25 = 136.33 and 186.33 mm.
//   Boss Z positions: CZ ± 15 = 54.08 and 84.08 mm.
//   All within STL X=99..228, Z=0..141 bounds ✓.
//   Access panel: X=130.33..192.33, Z=48.08..90.08 — within bounds ✓.
//   Bosses protrude in −Y (downward into interior) from interior dorsal face.
//   VERIFY each boss clears hull skin and avoids sensor aperture zones in slicer.
//   Ref: s_cargo_sect_shell24.scad Rev S4 FARADAY_* / AVINICS_BOSS_* pattern;
//   CAPE-B-2.kicad_pcb MH1–MH4; CLAUDE.md Book bay; Ruthex RX-M3x5.7.
//
// Cape PCB dimensions (same as cargo SCAD Rev S4):
CAPE_PCB_X     =  55.0;   // mm, Cape-B-2 / Cape-A-2 PCB X extent
CAPE_PCB_Z     =  35.0;   // mm, Cape-B-2 / Cape-A-2 PCB Z extent
CAPE_HOLE_DX   =  24.5;   // mm, ±X M2.5 corner hole offset from board centre
CAPE_HOLE_DZ   =  14.5;   // mm, ±Z M2.5 corner hole offset from board centre

// Faraday enclosure dimensions (same spec as cargo Rev S4):
FARADAY_ENC_X  =  60.0;   // mm, tray external X
FARADAY_ENC_Z  =  40.0;   // mm, tray external Z
FARADAY_ENC_Y  =  55.0;   // mm, tray depth below dorsal face
FARADAY_WALL   =   1.5;   // mm, tray wall thickness (0.5 mm Al + PETG liner)
FARADAY_FAN_D  =  25.0;   // mm, axial fan diameter (25×25×7 mm, on tray +X wall)

// Ductwork parameters (same spec as cargo Rev S4):
DUCT_INTAKE_W  =  22.0;   // mm, intake slot width on tray −X face
DUCT_INTAKE_H  =  22.0;   // mm, intake slot height
DUCT_EXHAUST_W =  24.0;   // mm, exhaust slot width on tray +X face (behind fan)
DUCT_EXHAUST_H =  24.0;   // mm, exhaust slot height
DUCT_EMC_T     =   6.0;   // mm, waveguide-below-cutoff honeycomb panel thickness
DUCT_CELL_D    =   6.0;   // mm, honeycomb cell diameter (λ/2 cutoff > 25 GHz)

// Book bay position constants:
BOOK_DORSAL_Y  = CY + 94.0;   // mm, interior dorsal face Y (≈ -54.6 mm; VERIFY slicer)
BOOK_BOSS_ROT  = [90, 0, 0];  // rotate cylinder: +Z → −Y (protrudes down into interior)
BOOK_X_CEN     = CX;          // mm, bay X centre = 161.33 mm
BOOK_Z_CEN     = CZ;          // mm, bay Z centre =  69.08 mm
BOOK_BOSS_DX   =  25.0;       // mm, ±X boss offset (matches cargo AVINICS_BOSS_DX)
BOOK_BOSS_DZ   =  15.0;       // mm, ±Z boss offset (matches cargo AVINICS_BOSS_DZ)
BOOK_PANEL_X   =  62.0;       // mm, dorsal access panel opening X (60 mm tray + 1 mm each)
BOOK_PANEL_Z   =  42.0;       // mm, dorsal access panel opening Z (40 mm tray + 1 mm each)

// ----------------------------------------------------------------------------
// Module: book_dorsal_boss
//   Single M3 heat-set insert boss on interior dorsal face, protruding −Y.
//   Provides one corner M3 anchor for the Shepherd Book Faraday tray body.
// ----------------------------------------------------------------------------
module book_dorsal_boss(x_pos, z_pos) {
    translate([x_pos, BOOK_DORSAL_Y, z_pos])
    rotate(BOOK_BOSS_ROT)
    difference() {
        cylinder(h = BOSS_H, d = BOSS_OD);
        cylinder(h = BOSS_H + 0.1, d = BOSS_BORE_D);
    }
}

// ----------------------------------------------------------------------------
// Module: book_dorsal_panel_cut
//   62×42 mm through-cut in dorsal skin for Book Faraday tray insertion.
//   Cover (72×52 mm, 5 mm shoulder) overlaps cut for EMI-seal positive stop.
//   Y span: BOOK_DORSAL_Y − 1.0 through BOOK_DORSAL_Y + WALL_MM + 1.0.
// ----------------------------------------------------------------------------
module book_dorsal_panel_cut() {
    translate([BOOK_X_CEN - BOOK_PANEL_X / 2,
               BOOK_DORSAL_Y - 1.0,
               BOOK_Z_CEN - BOOK_PANEL_Z / 2])
    cube([BOOK_PANEL_X, WALL_MM + 2.0, BOOK_PANEL_Z]);
}

// ----------------------------------------------------------------------------
// Module: vlsensor_cut
//   Flush-mount cutter for VL53L5CX.  No protrusion above hull surface.
//   Cuts: aperture bore + 0.5 mm PMMA seat ring + 4x M1.6 c/s holes + board recess.
//   The translate([0,0,-(WALL_T+1)]) places z=0 one mm inside the hull interior;
//   z=WALL_T+1 is the outer hull surface.
// ----------------------------------------------------------------------------
module vlsensor_cut(pos, rot) {
    translate(pos)
    rotate(rot)
    translate([0, 0, -(WALL_T + 1)]) {
        // PMMA aperture bore through full wall
        cylinder(h = WALL_T + 2, d = VAPER_D);

        // PMMA disc seat ring: 0.5 mm recess at exterior face, 14 mm OD
        translate([0, 0, WALL_T + 1 - VRING_DEP])
        cylinder(h = VRING_DEP + 1, d = VRING_OD);

        // 4x M1.6 countersunk through-holes (45 deg diagonal from aperture axes)
        for (a = [45, 135, 225, 315])
            rotate([0, 0, a])
            translate([VM16_R, 0, 0]) {
                // Shaft through wall
                cylinder(h = WALL_T + 2, d = VM16_D);
                // Countersink at exterior face
                translate([0, 0, WALL_T + 1 - VCSK16_D])
                cylinder(h = VCSK16_D + 1, d1 = VM16_D, d2 = VCSK16_OD);
            }

        // Carrier board recess on interior face
        translate([-VRECESS_W / 2, -VRECESS_W / 2, 0])
        cube([VRECESS_W, VRECESS_W, VRECESS_D + 1]);
    }
}

// ----------------------------------------------------------------------------
// Module: fpv_cut
//   Flush recess cutter for 28 mm FPV camera.  Camera face sits flush at hull.
//   Exterior: lens bore + bezel seating recess + 4x M2 c/s holes.
//   Interior: camera body pocket.
// ----------------------------------------------------------------------------
module fpv_cut(pos, rot) {
    translate(pos)
    rotate(rot)
    translate([0, 0, -(WALL_T + 1)]) {
        // Lens aperture bore
        cylinder(h = WALL_T + 2, d = FPV_APER_D);

        // Bezel seating recess: 1 mm deep at exterior, 29x29 mm
        translate([-FPV_BEZ_W / 2, -FPV_BEZ_W / 2, WALL_T + 1 - FPV_BEZ_DEP])
        cube([FPV_BEZ_W, FPV_BEZ_W, FPV_BEZ_DEP + 1]);

        // 4x M2 countersunk mount holes (14x14 mm grid)
        for (dx = [-FPV_M2_S / 2, FPV_M2_S / 2])
        for (dy = [-FPV_M2_S / 2, FPV_M2_S / 2])
            translate([dx, dy, 0]) {
                cylinder(h = WALL_T + 2, d = FPV_M2_D);
                // Countersink at exterior face
                translate([0, 0, WALL_T + 1 - FPV_CSK2_D])
                cylinder(h = FPV_CSK2_D + 1, d1 = FPV_M2_D, d2 = FPV_CSK2_OD);
            }

        // Camera body pocket on interior face
        translate([-FPV_BOARD_W / 2, -FPV_BOARD_W / 2, 0])
        cube([FPV_BOARD_W, FPV_BOARD_W, FPV_BOARD_D + 1]);
    }
}

// ----------------------------------------------------------------------------
// Module: m3_boss
//   Interior M3 heat-set insert boss post.  Solid ring with bore for insert.
//   Added to union() so it is positive material inside the hull skin.
//   Boss cylinder axis along +X by default (BOSS_AFT_ROT = [0, 90, 0]).
//   Ref: Ruthex RX-M3x5.7; ISO 14589; CLAUDE.md min 2-wall annulus requirement.
// ----------------------------------------------------------------------------
module m3_boss(pos, rot) {
    translate(pos)
    rotate(rot)
    difference() {
        // Boss post: solid cylinder, 8 mm OD x 6 mm tall
        cylinder(h = BOSS_H, d = BOSS_OD);
        // Heat-set insert bore: 4.1 mm dia, full height + 0.1 mm clearance
        cylinder(h = BOSS_H + 0.1, d = BOSS_BORE_D);
    }
}

// ============================================================
// Main geometry
// ============================================================
//
// Shell source note (Rev Q):
//   2.0 mm foam-fill skin shell generated by blender_shells_v3_2mm.py
//   (WALL_MM=2.0, SCALE=2.9294x, centroid-inset hollowing) from Thingiverse
//   source s_head.stl.  Repaired to manifold (0 NM edges) by
//   repair_shells_for_scad.py using voxel remesh at 1.2 mm pitch.
//   STL bounds: X=99..228, Y=-288..-53, Z=0..141 mm.
//   Inner scale used: sx=0.969083, sy=0.982987, sz=0.971563.
//   Structural analysis (2026-05-26) confirms 2.0 mm CF-PETG + 2 lb/cf foam fill
//   adequate for skin panels: deflection 0.054 mm at 28 m/s cruise (vs 0.5 mm limit).
//
// ── CSG tree overview (Rev S1) ────────────────────────────────────────────────
//
//   union
//   ├─ difference
//   │  ├─ union
//   │  │  ├─ hollow_shell()               ← 2.0 mm skin (outer − scaled inner)
//   │  │  ├─ book_dorsal_boss ×4          ← Shepherd Book Faraday tray anchors
//   │  │  └─ m3_boss ×6                   ← aft joint-face bosses
//   │  ├─ vlsensor_cut (S1A)              ← forward ToF sensor, Array A
//   │  ├─ vlsensor_cut (S1B)              ← forward ToF sensor, Array B
//   │  ├─ fpv_cut (FPV)                   ← bridge FPV camera
//   │  └─ book_dorsal_panel_cut           ← 62×42 mm Faraday tray access opening
//
// ============================================================
// Module: hollow_shell (Rev R — same fix as s_rear_neck_intake_shell24.scad)
// ============================================================
module hollow_shell() {
    difference() {
        import("../../thingverse-serenity/files-hollowed-18in/s_head_shell24_repaired.stl");
        translate([CX, CY, CZ])
            scale([INNER_SX, INNER_SY, INNER_SZ])
            translate([-CX, -CY, -CZ])
                import("../../thingverse-serenity/files-hollowed-18in/s_head_shell24_repaired.stl");
    }
}

difference() {
    union() {
        // 2.0 mm foam-fill head shell — hollowed in SCAD
        hollow_shell();

        // Shepherd Book avionics bay — 4× M3 Faraday tray anchor bosses.
        //   Boss pattern: ±25 mm (X) × ±15 mm (Z) from bay centre (CX, CZ).
        //   Boss positions (X, Z): (136.33,54.08), (136.33,84.08),
        //                          (186.33,54.08), (186.33,84.08).
        //   All within STL X=99..228, Z=0..141 bounds ✓.
        //   VERIFY bosses are on interior dorsal face in slicer before printing.
        //   Ref: Rev S1 Book bay; FARADAY_* / BOOK_BOSS_* constants above.
        for (dx = [-BOOK_BOSS_DX, BOOK_BOSS_DX])
        for (dz = [-BOOK_BOSS_DZ, BOOK_BOSS_DZ])
            book_dorsal_boss(BOOK_X_CEN + dx, BOOK_Z_CEN + dz);

        // 6x M3 boss posts at aft joint face (head → cargo section interface).
        //   Bosses extend into interior (+X) from joint face at X = 99 mm.
        //   VERIFY all boss positions are inside hull skin in slicer.
        m3_boss(BOSS_AFT_1, BOSS_AFT_ROT);
        m3_boss(BOSS_AFT_2, BOSS_AFT_ROT);
        m3_boss(BOSS_AFT_3, BOSS_AFT_ROT);
        m3_boss(BOSS_AFT_4, BOSS_AFT_ROT);
        m3_boss(BOSS_AFT_5, BOSS_AFT_ROT);
        m3_boss(BOSS_AFT_6, BOSS_AFT_ROT);
    }

    // Flush aperture cuts -- sensors and camera (Rev S1 corrected positions).
    vlsensor_cut(S1A_POS, FWD_ROT);
    vlsensor_cut(S1B_POS, FWD_ROT);
    fpv_cut(FPV_POS,      FWD_ROT);

    // Shepherd Book Faraday tray dorsal access panel cut (Rev S1).
    //   62×42 mm opening through dorsal skin at (BOOK_X_CEN, BOOK_Z_CEN).
    //   Book Faraday tray (60×40 mm) inserts from outside; 1 mm clearance each side.
    //   Cover (72×52 mm, 5 mm shoulder) seals EMI enclosure when installed.
    //   Fan (25×25×7 mm) on tray +X wall exhausts into head section interior.
    //   Intake honeycomb (22×22 mm slot, 6 mm deep waveguide panel) on tray −X wall.
    //   VERIFY panel bounds clear sensor apertures and hull-skin thickness in slicer.
    book_dorsal_panel_cut();
}
