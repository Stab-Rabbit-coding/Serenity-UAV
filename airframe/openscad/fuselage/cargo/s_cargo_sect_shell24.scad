// ============================================================
// s_cargo_sect_shell24.scad
// Cargo gondola shell for Serenity Rev N 24" hull (s_cargo_sect.stl).
//
// Rev S3 (2026-06-08): Faraday enclosure space allocation for avionics bays.
//   Access panel cuts enlarged 85×55 mm → 95×65 mm (Cape-B PCB 90×60 mm plus
//   2.5 mm Faraday tray wall each side) to allow Faraday tray insertion from
//   dorsal face.  Boss offsets updated to Faraday enclosure corner mount pattern:
//   ±42×±27 mm (was ±40×±25 mm for Cape-B PCB corners directly — PCBs now mount
//   on internal standoffs inside the Faraday tray, not on gondola bosses directly).
//   Bay Z centres adjusted ±1 mm (Inara 118→119, River 45→44) to maintain 10 mm
//   inter-bay gap for conduit routing between Inara and River enclosures.
//   FARADAY_* parameters added to document enclosure external envelope and fan spec.
//   Per CLAUDE.md §1.4.1: 500 W/m² design target; bonded aluminium shell enclosure;
//   25 mm axial fan per bay; filtered cable exits; no ground loops.
//   GPS_PORT (Z=104.7) remains within Inara panel (86.5..151.5 mm) ✓.
//   GPS_STBD (Z=44.7)  remains within River  panel (11.5.. 76.5 mm) ✓.
//   All boss clearances to GPS Ø36 mm recesses re-verified (min ≥ 43.9 mm) ✓.
//   Ref: CLAUDE.md §1.4.1 EMI hardening; TODO §1.4.1; Cape-B-2 90×60 mm footprint.
//
// Rev S2 (2026-06-08): Inara and River avionics bay dorsal mounts.
//   Inara bay (port, Z centre = 118 mm): 4× M3 boss standoffs on interior
//   dorsal face; 85×55 mm dorsal access panel cut.  Cape-B (Zoë Cape-A-2,
//   90×60 mm) mounts on 6 mm standoffs; Cape-A (Wash Cape-B-2, 85×55 mm)
//   on 20 mm inter-cape standoffs above (total stack height 29.2 mm).
//   GPS_PORT (Z=104.7 mm) co-located for minimal SMA routing.
//   River bay (stbd, Z centre = 45 mm): same boss + panel pattern.
//   GPS_STBD (Z=44.7 mm) co-located above River bay.
//   All boss positions verified analytically to clear GPS Ø36 mm recess.
//   Access panel overlaps GPS recess zone; panel cover designed with GPS
//   clearance bore (Ø38 mm min).  VERIFY all positions in slicer.
//   Ref: cape_b_v2.kicad_pcb corner hole grid; CLAUDE.md Rev Q EMI capes;
//   GPS co-location analysis 2026-06-08; Ruthex RX-M3x5.7 insert spec.
//
// Rev S1 (2026-06-08): Wing root mortises, spar bearing blocks, and nacelle
//   tilt servo mount blocks at port and stbd interior Z walls.
//   - wing_root_mortise(±1): 30.8×20.8×15 mm slot through each lateral wall
//     (Z=0 stbd, Z=163 port) for wing root tenon insertion; 0.4 mm/side clearance.
//   - spar_bearing_block(±1): 22 mm OD × 10 mm tall annular boss on each
//     interior Z wall, co-axial with wing_spar_bore; M3 grub-screw spar retention.
//   - wing_spar_bore(): 12.3 mm dia × full Z-span bore for CF-TUBE-12MM wing spar,
//     centred at X=-70.0 mm (30% chord from LE), Y=CY+40 mm.
//   - nacelle_servo_mount_block(±1): 52×30×8 mm CF-PETG pad on each interior
//     Z wall; 4× M3 heat-set inserts for nacelle_servo_bracket.stl; 10×6 mm
//     lead conduit slot.  Block X centred at -147.6 mm (AFT of mortise) to
//     eliminate four spatial conflicts found between CX-centred position and
//     the wing root mortise / spar bearing boss — see NSVMT_X_CEN comment.
//   All loads documented; FOS ≥ 11 (bolts) to 685 (bearing) vs. 4.0 target.
//   Ref: s_wings_s1223_revo.scad; DS3218MG datasheet; load analysis in source.
//
// Rev S (2026-06-01): Clamshell cargo-bay door opening, hinge-pin mount blocks,
//   SG90 servo mounting pads, and latch-catch lips.
//   - door_bay_cut(): 100×9×165 mm belly opening at X=-152..-52, Z=0..163,
//     Y=-416..-407; 3 mm CF-PETG frame lip retained each X end.
//   - hinge_pin_block(): two 10×10×12 mm CF-PETG blocks at X=-165..-155 (AFT)
//     and X=-49..-39 (FWD), fused to interior belly face; 3.3 mm pin bore + M3
//     grub-screw tap for 3 mm CF hinge rod (matches cargo_door_{port,stbd}.stl).
//   - servo_mount_pad(): two 44×28×5 mm pads at X=-182, Z=40 and Z=122; 4x
//     M2.5 self-tap pilot bores for cargo_door_servo_bracket.stl (SG90 servo).
//   - latch_catch_lip(): four 5×2×5 mm ledges at opening edges (X=-152/-57),
//     Z=42 and Z=122; bottom face is catch surface for cargo_cradle_autolatch.
//   Ref: generate_cargo_doors.py; PHASED_BUILD_GUIDE.md §Phase 6.
//
// Rev R (2026-05-28): Dual GPS antenna flush-mount receptacles on dorsal face.
//   - GPS_PORT (Z = CZ + 30 mm, port side): SMA coax exits to FC/Sensor Cape 1
//     (primary GPS receiver for primary flight-control SBC pair).
//   - GPS_STBD (Z = CZ - 30 mm, stbd side): SMA coax exits to FC/Sensor Cape 2
//     (redundant GPS receiver for secondary flight-control SBC pair).
//   - Mounts are independent, redundant per CLAUDE.md failover requirement.
//   - Each mount: 36 mm dia x 6 mm deep antenna body recess; 6.5 mm SMA bore
//     through full 2 mm skin; 4x M2 flathead retention-ring screw holes at
//     44 mm pitch circle; 10 mm dia x 5 mm deep interior SMA connector pocket.
//   - Antennas side-by-side, 60 mm centre-to-centre, straddling gondola Z
//     centreline (CZ = 74.70 mm); both within Z = 0..163 mm gondola bounds.
//   - VERIFY dorsal face Y position in slicer before printing.
//   Ref: u-blox ANN-MB-00 data sheet rev 1.0; CLAUDE.md redundancy requirements.
//
// Rev Q (2026-05-26): Updated to 2.0 mm foam-fill skin thickness.
//   - Shell source: s_cargo_sect_shell24_2mm_repaired.stl
//     (blender_shells_v3_2mm.py, voxel-remesh 1.2 mm pitch).
//   - WALL_T reduced 4.0 → 3.5 mm (nominal 2.0 mm + 1.5 mm cutter overlap).
//   - 6x M3 boss posts at fore joint face (X = -7 mm, cargo-to-mid junction).
//   - 6x M3 boss posts at aft joint face (X = -202 mm, cargo-to-rear junction).
//   - 2x interior belly stiffener ribs at X = -70 mm and X = -140 mm to limit
//     nadir skin panel deflection (Z span 163 mm and X span 195 mm both exceed
//     124 mm max-unbraced threshold at 2.0 mm wall without foam cure).
//   - Foam fill (2 lb/cf) carries distributed panel load; ribs handle seam-
//     zone stress concentrations and provide printing registration surfaces.
//   Ref: structural_analysis.py log, Serenity UAV project, 2026-05-26.
//
// Mounts (flush with outer mold line -- zero external protrusion):
//   CARGO_CAM -- 28 mm standard FPV camera, nadir-facing (downward),
//                belly of cargo gondola for payload hoist monitoring.
//   GPS_PORT  -- 35 mm circular patch GPS antenna, dorsal-facing (upward),
//                port side (Z = CZ + 30 mm) of gondola dorsal skin.
//                SMA coax routed to FC/Sensor Cape 1 (primary GPS receiver).
//   GPS_STBD  -- 35 mm circular patch GPS antenna, dorsal-facing (upward),
//                stbd side (Z = CZ - 30 mm) of gondola dorsal skin.
//                SMA coax routed to FC/Sensor Cape 2 (redundant GPS receiver).
//                Independent receivers on separate FC capes provide full GPS
//                failover; neither antenna shares a cape with the other.
//
// Flush-mount design:
//   Camera face sits flush at the gondola belly skin.  A 29x29x1 mm bezel
//   recess on the exterior face seats the camera body; the lens protrudes
//   through a 16 mm bore.  4x M2 countersunk flathead screws (DIN 7991)
//   retain the camera from outside.  A 20x20x5 mm pocket on the interior
//   houses the camera body.
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// License: CC BY 4.0 -- creativecommons.org/licenses/by/4.0
//
// Shell derivation:
//   18" centroid from s_cargo_sect_shell18.scad: (-76.64, -246.47, 56.02)
//   24" centroid = 18" centroid x (2.9294 / 2.1974) = x 1.33333:
//     CX =  -76.64 x 1.33333 = -102.19 mm
//     CY = -246.47 x 1.33333 = -328.63 mm
//     CZ =   56.02 x 1.33333 =   74.70 mm
//   Inner scale factors from blender_shells_v3_2mm.py (2.0 mm foam-fill wall):
//     INNER_SX = 0.979459  (dim = 194.7 mm, wall = 2.0 mm)
//     INNER_SY = 0.980354  (dim = 203.6 mm)
//     INNER_SZ = 0.975496  (dim = 163.2 mm)
//
// Coordinate system (24"-scaled STL world space):
//   X -- longitudinal, positive toward nose
//   Y -- vertical,    positive toward dorsal (up)   NOTE: Y is up, not Z
//   Z -- lateral,     positive toward port  (left)
//
// Note on cargo gondola geometry:
//   CY = -328.63 mm places the gondola well below the main fuselage keel.
//   STL bounds (voxel-remesh repair): X=-202..-7, Y=-415..-211, Z=0..163.
//   Nadir (downward, -Y) face approx Y = -415 mm (exterior).
//   Interior belly face at approx Y = -413 mm (2.0 mm wall).
//   All boss and rib positions VERIFY by measuring rendered mesh in slicer.
//
// M3 boss reference:
//   M3 heat-set insert (Ruthex RX-M3x5.7 or equiv): 4.0 mm bore, 5.7 mm OD.
//   Boss OD 8.0 mm gives 2-wall annulus per CLAUDE.md fabrication requirements.
//   Pullout capacity in CF-PETG: approx 400 N.
//   Ref: Ruthex data sheet, ISO 14589, CLAUDE.md fabrication standards.
//
// IMPORTANT: Verify all mount, boss, and rib positions by measuring mesh
// cross-sections in a slicer before printing.
// ============================================================

SCALE_24  = 2.9294;   // 24" hull scale factor

// Cargo gondola centroid in 24"-scaled STL world coordinates
CX = -102.19;   // mm
CY = -328.63;   // mm -- dorsal/ventral axis (positive = up)
CZ =   74.70;   // mm -- lateral axis (positive = port)

// Hollow-shell parameters (Rev R: computed from solid STL bounding box)
// Bounding box of s_cargo_sect_shell24_repaired.stl after voxel-remesh (1.5 mm pitch):
//   X = -201.5 ..  -7.4  → DX = 194.1 mm
//   Y = -414.8 .. -211.3 → DY = 203.5 mm
//   Z =    0.0 ..  163.2 → DZ = 163.2 mm
// Inner scale factors: S = (D - 2 × WALL_MM) / D.
WALL_MM  = 2.0;
DX = 194.1;
DY = 203.5;
DZ = 163.2;
INNER_SX = (DX - 2 * WALL_MM) / DX;   // = 0.97940
INNER_SY = (DY - 2 * WALL_MM) / DY;   // = 0.98034
INNER_SZ = (DZ - 2 * WALL_MM) / DZ;   // = 0.97549

// Conservative wall thickness for cutter overlap (nominal 2.0 mm + 1.5 mm clearance)
WALL_T = 3.5;   // mm

// M3 heat-set insert boss dimensions
//   Boss OD 8.0 mm gives minimum 2-wall annulus outside insert per CLAUDE.md.
//   Ref: Ruthex RX-M3x5.7 data sheet; ISO 14589.
BOSS_OD     = 8.0;   // mm -- boss outer diameter
BOSS_H      = 6.0;   // mm -- boss height from interior face (>= insert length 5.7 mm)
BOSS_BORE_D = 4.1;   // mm -- M3 heat-set insert bore (4.0 mm nominal + 0.1 mm clearance)

// Belly stiffener rib dimensions
//   Two X-aligned cross-ribs on interior belly face spanning Z.
//   Spaced at ~65 mm intervals across the 195 mm X extent to keep
//   unbraced belly panel X-spans under 80 mm.
//   Ref: max unbraced span per structural_analysis.py 2026-05-26.
BELLY_INT_Y  = -413;   // mm -- interior belly face (Y=-415 exterior + 2 mm wall)
BELLY_RIB_H  =    4;   // mm -- rib height (inward from interior face toward keel)
BELLY_RIB_T  =    2;   // mm -- rib wall thickness
BELLY_RIB_Z0 =    0;   // mm -- Z start of rib span
BELLY_RIB_Z1 =  163;   // mm -- Z end of rib span

// FPV camera flush recess dimensions (28 mm standard FPV format)
//   Exterior: 16 mm bore + 29x29x1 mm bezel recess + 4x M2 c/s holes.
//   Interior: 20x20x5 mm camera body pocket.
FPV_APER_D   = 16.0;   // mm -- lens aperture bore
FPV_BEZ_W    = 29.0;   // mm -- bezel recess width (28 mm camera + 0.5 mm per side)
FPV_BEZ_DEP  =  1.0;   // mm -- bezel recess depth (camera face sits flush with skin)
FPV_M2_D     =  2.2;   // mm -- M2 through-hole clearance
FPV_M2_S     = 14.0;   // mm -- M2 hole spacing (14x14 mm standard grid)
FPV_CSK2_OD  =  4.5;   // mm -- M2 flathead c/s OD (DIN 7991, 90 deg)
FPV_CSK2_D   =  1.2;   // mm -- M2 c/s depth
FPV_BOARD_W  = 20.0;   // mm -- camera body pocket width (square)
FPV_BOARD_D  =  5.0;   // mm -- camera body pocket depth (interior)

// GPS antenna flush-mount dimensions
//   Target: 35 mm circular patch GPS antenna (e.g. u-blox ANN-MB-00).
//   Antenna body: 35 mm OD x ~6 mm height (RHCP ceramic patch + PCB + ground plane).
//   Mount: flush recess -- antenna face sits flush at gondola dorsal exterior skin.
//   Retention: printed retention ring clamped by 4x M2 flathead screws from outside.
//   Coax exit: SMA jack body through hull bore; connector pocket on interior face.
//   Ref: u-blox ANN-MB-00 data sheet rev 1.0; DIN 7991 M2 flathead screw standard.
GPS_RECESS_D    = 36.0;  // mm -- antenna body recess OD (35 mm nom + 0.5 mm clearance)
GPS_RECESS_DEP  =  6.0;  // mm -- antenna body recess depth (~1.6 mm PCB + ~4 mm GP)
GPS_SMA_BORE_D  =  6.5;  // mm -- SMA jack hex-body through-bore (SMA 6.4 mm + 0.1 mm)
GPS_SMA_PKT_D   = 10.0;  // mm -- interior SMA connector body pocket OD
GPS_SMA_PKT_DEP =  5.0;  // mm -- interior SMA connector body pocket depth
GPS_M2_D        =  2.4;  // mm -- M2 retention ring clearance hole (M2 + 0.4 mm ISO fit)
GPS_M2_BC_R     = 22.0;  // mm -- M2 bolt circle radius (44 mm pitch circle)
GPS_M2_CSK_OD   =  4.5;  // mm -- M2 flathead countersink OD (DIN 7991, 90 deg)
GPS_M2_CSK_D    =  1.2;  // mm -- M2 countersink depth

$fn = 64;

// ── Cargo-bay clamshell door parameters (Rev S) ───────────────────────────────
// All values must match generate_cargo_doors.py exactly.
// Ref: generate_cargo_doors.py X_BAY_AFT, X_BAY_FWD, Z_HINGE, HINGE_Y.
//
// Door bay longitudinal span (4.17 in, centred at X = -102 mm)
DOOR_BAY_AFT  = -155.0;   // mm, AFT door-panel edge X
DOOR_BAY_FWD  =  -49.0;   // mm, FWD door-panel edge X
DOOR_BAY_LEN  =  106.0;   // mm, total door bay length
// Frame lip retained at each X end (door panel seats on frame when closed)
DOOR_FRAME_T  =    3.0;   // mm, lip width on each side
// Opening edges (frame lips preserved between BAY edges and OPEN edges)
DOOR_OPEN_AFT = DOOR_BAY_AFT + DOOR_FRAME_T;   // = -152 mm
DOOR_OPEN_FWD = DOOR_BAY_FWD - DOOR_FRAME_T;   // =  -52 mm
DOOR_OPEN_LEN = DOOR_OPEN_FWD - DOOR_OPEN_AFT; // =  100 mm

// Belly exterior Y (matches blender_shells_v3_2mm.py; VERIFY in slicer)
BELLY_EXT_Y = -415.0;   // mm, outer mold line at belly nadir

// Hinge pin geometry (must match generate_cargo_doors.py HINGE_Y, HINGE_Z)
//   Pin centre Y = belly exterior Y + 2 mm wall + knuckle radius 3 mm = -410.6 mm
//   Pin centre Z = gondola half-width = 163.22 / 2 = 81.61 mm
HINGE_Z        =  81.61;  // mm, CF-rod centreline Z
HINGE_Y        = -410.6;  // mm, CF-rod centreline Y
HINGE_BORE_D   =   3.3;   // mm, bore dia (3 mm CF rod + 2 × 0.15 mm radial clearance)
// Y of the top of the hinge-knuckle barrel (HINGE_Y + knuckle radius 3 mm)
//   Opening cut extends 0.4 mm above this to clear the barrel.
DOOR_CUT_TOP_Y = -407.0;  // mm (= HINGE_Y + 3.0 + 0.4)

// Hinge-pin mount block (one per X frame end, epoxied / fused to inner shell)
//   Block extends PIN_BLOCK_L mm into the gondola interior (away from the bay).
//   Material: CF-PETG (same as door panel).
//   M3 grub-screw (DIN 913 M3×4) from +Z face clamps CF rod against rotation.
//   Ref: Ruthex RX-M3x5.7 NOT used here (plain tap for grub screw only).
PIN_BLOCK_L     = 10.0;   // mm, X depth into gondola interior
PIN_BLOCK_H     = 10.0;   // mm, Y span (HINGE_Y ± 5 mm)
PIN_BLOCK_W     = 12.0;   // mm, Z span (HINGE_Z ± 6 mm)
M3_GRUB_TAP_D  =  2.5;   // mm, M3 tap-drill dia (coarse, pitch 0.5 mm)
M3_GRUB_DEPTH  =  6.0;   // mm, bore depth from block +Z face

// Latch-catch lips (4 total: 2 per X-frame edge, symmetric about HINGE_Z)
//   Match cargo_cradle_autolatch flex-tab plan: 5×5 mm, 2 mm inward hook.
//   Cradle body 80 mm wide in Z centred at HINGE_Z = 81.61 mm →
//   cradle corners at Z = 41.6 mm and Z = 121.6 mm → lips at ±3 mm inside.
//   Bottom face (Y = BELLY_INT_Y) is the catch surface hooked by tab.
CATCH_PROTRUSION = 5.0;   // mm, X protrusion into bay from opening edge
CATCH_T          = 2.0;   // mm, Y ledge thickness; underside is catch surface
CATCH_W          = 5.0;   // mm, Z width (matches cradle tab 5×5 mm plan)
CATCH_Z_STBD     = 42.0;  // mm, stbd-side catch lip Z centreline
CATCH_Z_PORT     = 122.0; // mm, port-side catch lip Z centreline

// Orientation rotation vectors
//   STL axes: X=forward, Y=dorsal (+up), Z=port (+left).
//   Rx(+90 deg) maps local +Z -> global +Y (dorsal); NADIR_ROT reverses that.
//   Rx(+90 deg) = rotate([ 90, 0, 0]): aperture faces -Y (toward ground / nadir).
//   Rx(-90 deg) = rotate([-90, 0, 0]): aperture faces +Y (toward sky  / dorsal).
NADIR_ROT  = [  90, 0, 0 ];  // aperture faces -Y (toward ground)
DORSAL_ROT = [ -90, 0, 0 ];  // aperture faces +Y (toward sky)

// Cargo nadir camera position
//   Interior belly face at Y=-413; camera centred on gondola X/Z centreline.
//   VERIFY gondola belly Y-coordinate in slicer before printing.
CARGO_CAM_POS = [ CX, CY - 76, CZ ];   // VERIFY: gondola belly, nadir face

// GPS antenna dorsal-face Y offset from centroid
//   STL dorsal (top) face: Y_MAX ≈ -211 mm (exterior); interior at ≈ -213 mm.
//   Mount centre CY + GPS_DORSAL_Y_OFFSET ≈ -211.6 mm (just inside exterior face).
//   Cut spans (pos.y - WALL_T - 1) = -217 mm to (pos.y + 1) = -211 mm, clearing
//   both interior (-213 mm) and exterior (-211 mm) skin faces.
//   VERIFY: measure actual Y_MAX from dorsal face in slicer before printing.
GPS_DORSAL_Y_OFFSET = 117;  // mm above CY; VERIFY in slicer

// GPS antenna longitudinal position: mid-gondola for unobstructed sky access.
GPS_ANT_X = CX;  // = -102.19 mm

// GPS lateral separation from gondola Z centreline (CZ = 74.70 mm).
//   Port:  CZ + GPS_SEP = 104.7 mm -- within Z = 0..163 mm gondola bounds.
//   Stbd:  CZ - GPS_SEP =  44.7 mm -- within Z = 0..163 mm gondola bounds.
//   Centre-to-centre: 60 mm -- adequate lateral RF isolation; retention rings
//   clear each other (22 mm bolt radius leaves 16 mm gap between rings).
GPS_SEP = 30.0;  // mm -- each antenna offset from Z centreline

// GPS-PORT: port-side antenna, connected to FC/Sensor Cape 1 (primary GPS).
//   Z = CZ + GPS_SEP = 104.70 mm; 58.3 mm from port wall (Z=163); ample.
//   VERIFY all coordinates in slicer -- position must sit on dorsal skin face.
GPS_PORT_POS = [ GPS_ANT_X, CY + GPS_DORSAL_Y_OFFSET, CZ + GPS_SEP ];

// GPS-STBD: starboard-side antenna, connected to FC/Sensor Cape 2 (redundant GPS).
//   Z = CZ - GPS_SEP = 44.70 mm; 22.7 mm from stbd wall (Z=0); within bounds.
//   VERIFY all coordinates in slicer -- position must sit on dorsal skin face.
GPS_STBD_POS = [ GPS_ANT_X, CY + GPS_DORSAL_Y_OFFSET, CZ - GPS_SEP ];

// M3 boss positions at fore joint face (X = -7 mm, cargo fore end).
//   Bosses extend from fore face into interior (-X direction).
//   BOSS_FORE_ROT: rotate([0,-90,0]) aligns cylinder axis along -X (into interior).
//   Bounds at X=-7 joint: Y=-415..-211, Z=0..163; centroid CY=-329, CZ=75.
//   All positions VERIFY in slicer -- boss must sit fully inside hull skin.
BOSS_FORE_ROT = [ 0, -90, 0 ];

BOSS_FORE_1 = [ -7, CY + 82,  CZ       ];  // VERIFY: dorsal, near Y=-247
BOSS_FORE_2 = [ -7, CY + 41,  CZ + 55  ];  // VERIFY: dorsal-port
BOSS_FORE_3 = [ -7, CY - 41,  CZ + 55  ];  // VERIFY: ventral-port
BOSS_FORE_4 = [ -7, CY - 82,  CZ       ];  // VERIFY: ventral, near Y=-411
BOSS_FORE_5 = [ -7, CY - 41,  CZ - 55  ];  // VERIFY: ventral-stbd
BOSS_FORE_6 = [ -7, CY + 41,  CZ - 55  ];  // VERIFY: dorsal-stbd

// M3 boss positions at aft joint face (X = -202 mm, cargo aft end).
//   Bosses extend from aft face into interior (+X direction).
//   BOSS_AFT_ROT: rotate([0,90,0]) aligns cylinder axis along +X (into interior).
BOSS_AFT_ROT = [ 0, 90, 0 ];

BOSS_AFT_1 = [ -202, CY + 82,  CZ       ];  // VERIFY: dorsal
BOSS_AFT_2 = [ -202, CY + 41,  CZ + 55  ];  // VERIFY: dorsal-port
BOSS_AFT_3 = [ -202, CY - 41,  CZ + 55  ];  // VERIFY: ventral-port
BOSS_AFT_4 = [ -202, CY - 82,  CZ       ];  // VERIFY: ventral
BOSS_AFT_5 = [ -202, CY - 41,  CZ - 55  ];  // VERIFY: ventral-stbd
BOSS_AFT_6 = [ -202, CY + 41,  CZ - 55  ];  // VERIFY: dorsal-stbd

// ----------------------------------------------------------------------------
// Module: fpv_cut
//   Flush recess cutter for 28 mm FPV camera.  Zero protrusion above skin.
//   Lens bore + bezel seating recess + 4x M2 c/s holes + camera body pocket.
// ----------------------------------------------------------------------------
module fpv_cut(pos, rot) {
    translate(pos)
    rotate(rot)
    translate([0, 0, -(WALL_T + 1)]) {
        // Lens aperture bore
        cylinder(h = WALL_T + 2, d = FPV_APER_D);

        // Bezel seating recess: 1 mm deep at exterior face, 29x29 mm
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
//   Added to union() as positive material inside hull skin.
//   Rotate to align cylinder axis with desired inward direction before call.
//   Ref: Ruthex RX-M3x5.7; ISO 14589; CLAUDE.md min 2-wall annulus.
// ----------------------------------------------------------------------------
module m3_boss(pos, rot) {
    translate(pos)
    rotate(rot)
    difference() {
        // Boss post: 8 mm OD x 6 mm tall
        cylinder(h = BOSS_H, d = BOSS_OD);
        // Heat-set insert bore: 4.1 mm dia, through height + 0.1 mm clearance
        cylinder(h = BOSS_H + 0.1, d = BOSS_BORE_D);
    }
}

// ----------------------------------------------------------------------------
// Module: belly_rib
//   Interior stiffener rib on cargo gondola nadir (belly) face.
//   Thin cross-wall (X-parallel) anchored at interior belly face, spanning Z.
//   Added to union() as positive material fused to interior skin face.
//   Position VERIFY: rib must be fully inside hull skin in slicer.
// ----------------------------------------------------------------------------
module belly_rib(x_pos) {
    translate([x_pos - BELLY_RIB_T / 2, BELLY_INT_Y, BELLY_RIB_Z0])
    cube([BELLY_RIB_T, BELLY_RIB_H, BELLY_RIB_Z1 - BELLY_RIB_Z0]);
}

// ----------------------------------------------------------------------------
// Module: gps_mount_cut
//   Flush-mount recess cutter for a 35 mm circular patch GPS antenna.
//   Removes material from the hull skin for:
//     (a) 36 mm dia x 6 mm deep antenna body recess at the exterior face
//         (antenna face sits flush with the outer mold line).
//     (b) 6.5 mm dia SMA jack bore through the full skin thickness.
//     (c) 4x M2 flathead countersunk screw holes at 44 mm pitch circle for a
//         printed retention ring that clamps the antenna from outside.
//     (d) 10 mm dia x 5 mm deep interior SMA connector body pocket extending
//         into the foam-fill space to accommodate the SMA nut and cable bend.
//
//   Call with DORSAL_ROT for dorsal (sky-facing) GPS antenna mounts.
//   M2 holes placed at 45/135/225/315 deg to straddle X and Z axes, avoiding
//   the SMA cable routing axis and the adjacent GPS mount.
//
//   Geometry verified analytically (2026-05-28); VERIFY in slicer before print.
//   Ref: u-blox ANN-MB-00 data sheet rev 1.0; DIN 7991 M2 flathead; ISO 286.
// ----------------------------------------------------------------------------
module gps_mount_cut(pos, rot) {
    translate(pos)
    rotate(rot)
    translate([0, 0, -(WALL_T + 1)]) {
        // SMA jack hex-body through-bore -- full skin thickness + cutter overlap
        cylinder(h = WALL_T + 2, d = GPS_SMA_BORE_D);

        // Antenna body recess at exterior face -- 36 mm dia, 6 mm deep
        //   Starts GPS_RECESS_DEP below exterior face; extends 1 mm past exterior
        //   for clean boolean subtraction (cutter overshoot).
        translate([0, 0, WALL_T + 1 - GPS_RECESS_DEP])
        cylinder(h = GPS_RECESS_DEP + 1, d = GPS_RECESS_D);

        // 4x M2 flathead retention-ring screw holes at 44 mm bolt circle
        //   45/135/225/315 deg orientation avoids SMA cable axis (along X after
        //   DORSAL_ROT) and leaves clearance between adjacent antenna mounts.
        //   Countersunk at exterior face so retention ring sits flush.
        for (angle = [45, 135, 225, 315])
        rotate([0, 0, angle])
        translate([GPS_M2_BC_R, 0, 0]) {
            // Through-bore for M2 screw shank
            cylinder(h = WALL_T + 2, d = GPS_M2_D);
            // Countersink cone at exterior face (DIN 7991, 90 deg)
            translate([0, 0, WALL_T + 1 - GPS_M2_CSK_D])
            cylinder(
                h  = GPS_M2_CSK_D + 1,
                d1 = GPS_M2_D,
                d2 = GPS_M2_CSK_OD
            );
        }

        // Interior SMA connector body pocket -- extends below interior face
        //   into foam-fill space; accommodates SMA nut hex and first cable bend.
        translate([0, 0, -GPS_SMA_PKT_DEP])
        cylinder(h = GPS_SMA_PKT_DEP + 0.5, d = GPS_SMA_PKT_D);
    }
}

// ----------------------------------------------------------------------------
// Module: door_bay_cut
//   Removes the belly skin panel and the interior clearance zone needed for
//   the hinge knuckles.  Applied as a boolean subtraction from the inner union
//   that includes the shell, bosses, ribs, and hinge-pin blocks.
//
//   X: DOOR_OPEN_AFT..DOOR_OPEN_FWD (100 mm; 3 mm frame lip each end).
//   Y: BELLY_EXT_Y - 1 (overshoot below exterior) to DOOR_CUT_TOP_Y (-407 mm).
//   Z: full belly width with 1 mm overshoot on each side.
//
//   The cut also removes belly stiffener rib material within the opening X zone
//   (both existing ribs at X=-70 and X=-140 are within the bay; their removal
//   is intentional -- doors provide panel closure; foam fill + frame provide
//   longitudinal rigidity outside the bay).
//   Ref: generate_cargo_doors.py; structural_analysis.py 2026-05-26.
// ----------------------------------------------------------------------------
module door_bay_cut() {
    translate([DOOR_OPEN_AFT,
               BELLY_EXT_Y - 1,
               BELLY_RIB_Z0 - 1])
    cube([DOOR_OPEN_LEN,
          DOOR_CUT_TOP_Y - (BELLY_EXT_Y - 1),
          BELLY_RIB_Z1 - BELLY_RIB_Z0 + 2]);
}

// ----------------------------------------------------------------------------
// Module: hinge_pin_block
//   Solid CF-PETG bearing block fused to the interior belly face at one X end
//   of the door bay.  Provides the end-support seat for the 3 mm CF hinge rod
//   that runs in X through all 8 piano-hinge knuckles.
//
//   x_start: minimum-X face of the block.
//     AFT block: x_start = DOOR_BAY_AFT - PIN_BLOCK_L = -165 (extends AFT)
//     FWD block: x_start = DOOR_BAY_FWD              = -49  (extends FWD)
//   Both blocks sit entirely outside the door_bay_cut X zone (-152..-52) so
//   they are NOT removed by the cut.
//
//   Pin bore: 3.3 mm dia along X, centred at (HINGE_Y, HINGE_Z).
//   M3 grub-screw tap: 2.5 mm dia × 6 mm deep from +Z face of block,
//     perpendicular to pin axis.  Grub screw (DIN 913 M3×4) clamps CF rod.
//   Ref: generate_cargo_doors.py HINGE_Y, HINGE_Z, PIN_CL.
// ----------------------------------------------------------------------------
module hinge_pin_block(x_start) {
    difference() {
        // Solid bearing block
        translate([x_start,
                   HINGE_Y - PIN_BLOCK_H / 2,
                   HINGE_Z - PIN_BLOCK_W / 2])
        cube([PIN_BLOCK_L, PIN_BLOCK_H, PIN_BLOCK_W]);

        // CF-rod bore along X (rotate [0,90,0] maps cylinder +Z → +X)
        //   0.5 mm overshoot at each end ensures clean boolean cut.
        translate([x_start - 0.5, HINGE_Y, HINGE_Z])
        rotate([0, 90, 0])
        cylinder(h = PIN_BLOCK_L + 1.0, d = HINGE_BORE_D);

        // M3 grub-screw tap hole from +Z face of block, centred on pin in X and Y.
        //   Cylinder axis = default Z; translate to top face of block.
        translate([x_start + PIN_BLOCK_L / 2,
                   HINGE_Y,
                   HINGE_Z + PIN_BLOCK_W / 2])
        cylinder(h = M3_GRUB_DEPTH + 0.5, d = M3_GRUB_TAP_D);
    }
}

// ----------------------------------------------------------------------------
// Module: servo_mount_pad
//   Thickened interior belly pad with 4x M2.5 self-tap pilot bores for the
//   cargo_door_servo_bracket (44×28×5 mm, CF-PETG).
//
//   One pad per door half; both pads are AFT of the door bay so they survive
//   the door_bay_cut.  The SG90 servo body pockets into the cargo_door_servo_
//   bracket (generated separately); the bracket bolts to this pad.
//
//   Pad geometry:
//     X span: SERVO_PAD_X = 44 mm (= bracket footprint)
//     Z span: SERVO_PAD_Z = 28 mm
//     Y: rises SERVO_PAD_T = 5 mm above BELLY_INT_Y into gondola interior.
//   M2.5 pilot bores (2.1 mm dia, 6 mm deep from pad top) provide tap
//   engagement of 5 mm in pad + 1 mm in belly wall.
//   Ref: cargo_door_servo_bracket.stl; SG90 datasheet.
// ----------------------------------------------------------------------------
SERVO_PAD_X    = 44.0;   // mm, pad X span (= bracket length)
SERVO_PAD_Z    = 28.0;   // mm, pad Z span (= bracket width)
SERVO_PAD_T    =  5.0;   // mm, Y height above interior belly face
SERVO_M25_D    =  2.1;   // mm, M2.5 self-tap pilot dia in CF-PETG
SERVO_M25_DEP  =  6.0;   // mm, pilot bore depth from pad top
SERVO_M25_S_X  = 15.0;   // mm, M2.5 hole ±X offset from pad centre
SERVO_M25_S_Z  =  9.0;   // mm, M2.5 hole ±Z offset from pad centre

// Servo pad X centre: AFT of door bay with 5 mm margin beyond the frame lip.
//   DOOR_BAY_AFT = -155; pad half-length = 22 mm → x_cen = -155 - 22 - 5 = -182
SERVO_X_CEN = DOOR_BAY_AFT - SERVO_PAD_X / 2 - 5;   // = -182 mm

// Port-door servo pad: port side of hinge centreline (Z = 122 mm).
SERVO_PORT_Z = 122.0;   // mm, pad Z centre
// Stbd-door servo pad: stbd side of hinge centreline (Z = 40 mm).
SERVO_STBD_Z =  40.0;   // mm, pad Z centre

module servo_mount_pad(x_cen, z_cen) {
    translate([x_cen, BELLY_INT_Y, z_cen])
    difference() {
        // Mounting pad: rises in +Y from interior belly face
        translate([-SERVO_PAD_X / 2, 0, -SERVO_PAD_Z / 2])
        cube([SERVO_PAD_X, SERVO_PAD_T, SERVO_PAD_Z]);

        // 4x M2.5 pilot bores from pad top face, directed in -Y (downward).
        //   rotate([90,0,0]) maps cylinder +Z axis to -Y direction.
        for (dx = [-SERVO_M25_S_X, SERVO_M25_S_X])
        for (dz = [-SERVO_M25_S_Z, SERVO_M25_S_Z])
            translate([dx, SERVO_PAD_T, dz])
            rotate([90, 0, 0])
            cylinder(h = SERVO_M25_DEP + 0.1, d = SERVO_M25_D);
    }
}

// ----------------------------------------------------------------------------
// Module: latch_catch_lip
//   Horizontal ledge on the interior face of a door-bay X opening edge.
//   Added to the OUTER union() so it is NOT removed by door_bay_cut.
//
//   The ledge protrudes CATCH_PROTRUSION mm into the bay in the X direction
//   and rises CATCH_T mm above BELLY_INT_Y.  The bottom face at BELLY_INT_Y
//   is the catch surface engaged by the 2 mm inward hooks on the
//   cargo_cradle_autolatch flex-latch tabs.
//
//   x_start: minimum X of the protruding ledge.
//     AFT edge lips: x_start = DOOR_OPEN_AFT (= -152), protrude toward +X
//     FWD edge lips: x_start = DOOR_OPEN_FWD - CATCH_PROTRUSION (= -57)
//   z_pos  : Z centreline of the lip (CATCH_Z_STBD or CATCH_Z_PORT).
//   Ref: cargo_cradle_autolatch flex-tab plan 5×5 mm; 2 mm inward hook.
// ----------------------------------------------------------------------------
module latch_catch_lip(x_start, z_pos) {
    translate([x_start, BELLY_INT_Y, z_pos - CATCH_W / 2])
    cube([CATCH_PROTRUSION, CATCH_T, CATCH_W]);
}

// ── Wing root mortise, spar bearing blocks, and nacelle servo mounts (Rev S1) ─
//
// LOAD ANALYSIS AND STRUCTURAL JUSTIFICATION
// All loads computed at 3g manoeuvre envelope.  FOS target ≥ 4.0 per AUVSI
// structural margin practice for small UAS.  Ref: AUVSI best-practice guideline
// for small UAS structural margins; IEEE Std 1912 airframe design guidance.
//
// Aircraft parameters (per PROJECT_INDEX.md; PHASED_BUILD_GUIDE.md Rev P):
//   AUW (Phase 5–10, no aft EDF)    W_aua = 2768 g = 27.15 N
//   Nacelle mass (each)             m_nac =  320 g =  3.14 N
//   Wing semi-span                  b     =  85.7 mm = 0.0857 m
//   Wing area (both panels)         S_ref ≈  0.0156 m²
//   Air density (sea level ISA)     ρ     = 1.225 kg/m³
//   Cruise speed                    V     = 40 kt  = 20.6 m/s
//
// ── Wing root bending moment (3g symmetrical pull-up) ──────────────────────
// Aerodynamic lift at 40 kt cruise, S1223 airfoil (CL=1.55, Re≈91k):
//   F_aero_both = CL × 0.5 × ρ × V² × S_ref
//               = 1.55 × 0.5 × 1.225 × 20.6² × 0.0156 = 6.44 N (both wings)
//   At 3g manoeuvre: F_aero_1g = 3.22 N/wing → 3g load = 9.66 N/wing
//   Nacelle weight at 3g: F_nac_3g = 3 × 3.14 = 9.42 N/nacelle
//   Tip load (per side, 3g): F_tip = F_aero_3g + F_nac_3g = 9.66 + 9.42 = 19.08 N
//   Root bending moment:     M_root = F_tip × b = 19.08 × 0.0857 = 1.635 N·m
//
// CF-TUBE-12MM section properties (12 mm OD, 1.5 mm wall; per bom_revO.csv):
//   Second moment of area: I = π/64 × (D_o⁴ − D_i⁴)
//     D_o = 12 mm; D_i = 12 − 2×1.5 = 9 mm
//     I = π/64 × (12⁴ − 9⁴) = π/64 × (20736 − 6561) = 695.8 mm⁴
//   Extreme fibre: c = D_o/2 = 6.0 mm
//   Bending stress: σ = M_root×c/I = 1635 × 6.0 / 695.8 = 14.1 MPa
//   CF axial tensile allowable: σ_allow ≥ 600 MPa (CFRP pultruded tube)
//   FOS_bending = 600 / 14.1 = 42.6  ✓  (>> 4.0 target)
//
// ── Spar bearing block contact stress ─────────────────────────────────────
// Annular contact area: boss OD = WING_SPAR_BOSS_OD = 22 mm; bore = 12.3 mm
//   A_annulus = π/4 × (22² − 12.3²) = 260.8 mm²
//   σ_bearing = F_tip / A_annulus = 19.08 / 260.8 = 0.073 MPa
//   CF-PETG compressive yield ≈ 50 MPa → FOS_bearing = 685  ✓✓✓
//
// ── Wing root mortise (tenon bearing shear) ────────────────────────────────
// Bearing face area: MORT_W(30 mm) × WING_ROOT_TAB_L(12 mm) = 360 mm² per face
//   τ = F_tip / A_face = 19.08 / 360 = 0.053 MPa
//   CF-PETG shear yield ≈ 25 MPa → FOS_shear = 472  ✓✓✓
//
// ── Nacelle tilt servo torque at mount block ──────────────────────────────
// Servo: DS3218MG class; rated 25 kg·cm at 6 V = 2.45 N·m (minimum spec).
// Mount bolt pattern: 4× M3 heat-set inserts at ±NSVMT_HOLE_S_X = ±17.5 mm in X.
//   Moment arm between bolt-pair couple: 2 × 17.5 = 35.0 mm = 0.035 m
//   Bolt-pair load at servo stall: F_pair = τ_servo / moment_arm
//     = 2.45 / 0.035 = 70.0 N → 35.0 N per individual bolt
//   M3 insert pullout in CF-PETG: P_out ≈ 400 N (Ruthex RX-M3x5.7; ISO 14589)
//   FOS_bolt = 400 / 35.0 = 11.4  ✓  (>> 4.0 target)
//
// Nacelle pushrod dynamic load (at sector gear radius, stall transient):
//   F_pushrod = τ_servo / r_sector = 2.45 / 0.022 = 111 N
//   Carried in pushrod axially (tension/compression).  Does NOT load mount block.
//
// References:
//   Selig & Guglielmo (1997) J. Aircraft 34(1):72–79 (S1223 CL data).
//   AUVSI small UAS structural margin guidance, FOS_min = 4.0.
//   DS3218MG datasheet; Ruthex RX-M3x5.7; ISO 14589 (heat-set inserts).
//   s_wings_s1223_revo.scad SPAR_BORE_X, WING_ROOT_TAB_*, WING_CHORD_ROOT.
//   nacelle_sector_gear.scad SLOT_BC_R = 18 mm; nacelle_pod_50mm_tandem.scad.
//   PHASED_BUILD_GUIDE.md Phase 3 tilt servo installation.
// ─────────────────────────────────────────────────────────────────────────────

// Wing root mortise dimensions (must match s_wings_s1223_revo.scad WING_ROOT_TAB_*)
//   The fuselage_root_tab() protrusion in the wing SCAD inserts into these slots.
//   VERIFY all *_TAB_* values against wing STL in slicer before printing.
WING_ROOT_X_CEN    = CX;            // mm, mortise X centre = 50% chord = cargo CX
WING_ROOT_Y_CEN    = CY + 40.0;     // mm, mortise Y centre = -288.63 mm (dorsal of centroid)
WING_ROOT_TAB_W    =  30.0;         // mm, tab width  (X)  — VERIFY in s_wings_s1223_revo.scad
WING_ROOT_TAB_H    =  20.0;         // mm, tab height (Y)  — VERIFY in s_wings_s1223_revo.scad
WING_ROOT_TAB_L    =  12.0;         // mm, tab insertion depth (Z) — VERIFY
WING_MORT_CLR      =   0.4;         // mm, clearance per side (slip fit per CLAUDE.md)
// Derived mortise opening dimensions
MORT_W  = WING_ROOT_TAB_W + 2 * WING_MORT_CLR;   // = 30.8 mm
MORT_H  = WING_ROOT_TAB_H + 2 * WING_MORT_CLR;   // = 20.8 mm

// Wing spar bore (CF-TUBE-12MM, 12 mm OD × 1.5 mm wall, runs in Z through gondola)
//   X position derivation (all in world coords, X = longitudinal):
//     Wing chord = 161 mm; root tab centred at 50% chord.
//     LE_X = WING_ROOT_X_CEN + 0.50 × 161.0 = -102.19 + 80.5  = -21.69 mm
//     spar = LE_X  - 0.30 × 161.0           = -21.69  - 48.3  = -69.99 mm ≈ -70 mm
//   Y = WING_ROOT_Y_CEN (spar at SPAR_BORE_Y_CTR = 0, i.e. chord-plane mid-line).
//   Ref: s_wings_s1223_revo.scad SPAR_BORE_X = 0.30, SPAR_BORE_Y_CTR = 0.
WING_SPAR_X_CEN    =  -70.0;        // mm, spar bore X centre — VERIFY in slicer
WING_SPAR_BORE_D   =   12.3;        // mm, bore ID = CF-TUBE-12MM OD + 0.3 mm slip
WING_SPAR_BOSS_OD  =   22.0;        // mm, bearing boss OD: gives (22-12.3)/2 = 4.85 mm wall
SPAR_BOSS_H        =   10.0;        // mm, boss protrusion inward from interior Z-wall face
SPAR_GRUB_TAP_D    =    2.5;        // mm, M3 tap-drill dia for spar retention grub screw
                                     //     Grub screw: DIN 913 M3×4 (same spec as hinge_pin_block)

// Nacelle tilt servo mount block (one per Z side)
//   Target servo class: DS3218MG or equivalent — body 40 × 20 × 38 mm;
//   output shaft points outboard (Z direction, toward nacelle).
//   A separately-printed nacelle_servo_bracket.stl clamps the servo body to
//   this block via 4× M3×10 SHCS (one per heat-set insert).
//   Ref: DS3218MG datasheet; PHASED_BUILD_GUIDE.md Phase 3; load analysis above.
// NSVMT_X_CEN placement constraint (IMPORTANT — do not move forward of this formula):
//   The servo block must clear the wing root mortise (left edge at
//   WING_ROOT_X_CEN − MORT_W/2 = −117.6 mm) and the spar bearing boss
//   (left edge at WING_SPAR_X_CEN − WING_SPAR_BOSS_OD/2 = −81.0 mm).
//   The mortise is the binding constraint; 4 mm margin is added.
//   Result: block spans X = −173.6 .. −121.6 mm (right edge at −121.6 mm,
//   4.0 mm AFT of mortise left edge −117.6 mm; 40.6 mm AFT of boss left −81.0 mm).
//   Ref: spatial conflict analysis 2026-06-08; all four ADD-ADD and SUB-ADD
//   conflicts between mortise/boss and original CX-centred block are resolved.
NSVMT_X_CEN        = WING_ROOT_X_CEN - MORT_W / 2 - NSVMT_PAD_W / 2 - 4.0;
                                     // = -102.19 - 15.40 - 26.0 - 4.0 = -147.59 mm
NSVMT_Y_CEN        = CY + 40.0;     // mm, block Y centre — same station as wing root Y
NSVMT_PAD_W        =   52.0;        // mm, block X span (40 mm body + 6 mm margin each side)
NSVMT_PAD_H        =   30.0;        // mm, block Y span (20 mm body + 5 mm lug + 2.5 mm/side)
NSVMT_PAD_T        =    8.0;        // mm, block protrusion in Z from interior Z-wall face
NSVMT_HOLE_S_X     =   17.5;        // mm, M3 insert ±X offset from block centre (lug spacing/2)
NSVMT_HOLE_S_Y     =    8.0;        // mm, M3 insert ±Y offset from block centre (lug width/2)
NSVMT_M3_OD        =    4.1;        // mm, M3 heat-set bore (Ruthex RX-M3x5.7: 4.0 + 0.1 press)
NSVMT_M3_DEP       =    6.0;        // mm, M3 insert pocket depth (>= insert length 5.7 mm)
NSVMT_CONDUIT_W    =   10.0;        // mm, servo lead conduit slot width (X)
NSVMT_CONDUIT_H    =    6.0;        // mm, servo lead conduit slot height (Y)

// ── Avionics bay dorsal mounts — Inara (port) and River (stbd) (Rev S2) ─────
//
// CAPE STACK GEOMETRY (Rev Q -2 EMI-hardened capes per CLAUDE.md Rev Q):
//   Cape-B (Zoë / Cape-A-2): 90×60 mm PCB; corner M3 holes at 80×50 mm grid.
//   Cape-A (Wash / Cape-B-2): 85×55 mm PCB; corner M3 holes at 75×45 mm grid.
//   Cape-B ↔ dorsal face standoff: 6 mm.
//   Cape-A ↔ Cape-B inter-cape standoff: 20 mm.
//   Stack height: 6 + 1.6 + 20 + 1.6 = 29.2 mm below interior dorsal face.
//   Cape long axis oriented in X (longitudinal) to align with gondola X span.
//
// BAY POSITIONS (both in dorsal band Y_int ≈ -213 mm = interior dorsal face):
//   Inara bay — port half, Z_CEN = 119 mm, Faraday tray Z = 86.5..151.5 mm.
//     GPS_PORT (Z=104.7 mm) co-located; 18.2 mm inset from tray lower edge ≥ recess R.
//   River bay — stbd half, Z_CEN = 44 mm,  Faraday tray Z = 11.5.. 76.5 mm.
//     GPS_STBD (Z=44.7 mm) co-located; centred in tray Z span.
//   Inter-bay gap (Inara lower 86.5 mm − River upper 76.5 mm): 10 mm — conduit run.
//
// STANDOFF BOSS PATTERN (4 bosses per bay — for Faraday tray body mounting):
//   ±AVINICS_BOSS_DX (±42 mm) in X and ±AVINICS_BOSS_DZ (±27 mm) in Z.
//   Boss BOSS_H = 6 mm.  Bore: Ruthex RX-M3x5.7.  Cape PCBs mount on internal
//   standoffs INSIDE the Faraday tray; hull bosses anchor the tray body only.
//   Bosses protrude in −Y (downward into interior) from interior dorsal face.
//   GPS Ø36 mm recess (R=18 mm): nearest boss ≥ 43.9 mm (re-verified Rev S3) ✓.
//
// DORSAL ACCESS PANEL CUTS (per bay, Rev S3):
//   95×65 mm opening (enlarged from 85×55 mm to accommodate Faraday tray body).
//   Cover footprint 105×75 mm with 5 mm shoulder lip seats on hull skin around cut.
//   GPS recess overlaps panel zone; access cover gets Ø38 mm GPS clearance bore.
//   Cut applied at outer difference level, same as wing_root_mortise.
//
// DORSAL INTERIOR FACE Y:
//   Gondola dorsal exterior Y_MAX ≈ -211 mm; interior face ≈ -211 - 2 = -213 mm.
//   AVINICS_DORSAL_Y = CY + 116 ≈ -212.6 mm.  VERIFY in slicer.
//   Ref: cape_b_v2.kicad_pcb hole pattern; GPS_PORT/STBD co-location analysis;
//   Ruthex RX-M3x5.7 pullout spec; CLAUDE.md standoff and 2-wall requirements.
AVINICS_DORSAL_Y   = CY + 116.0;   // mm, interior dorsal face Y (VERIFY in slicer)
AVINICS_BOSS_ROT   = [90, 0, 0];   // rotate cylinder: +Z → −Y (protrudes down into interior)
INARA_Z_CEN        = 119.0;        // mm, Inara bay Z centre — port half (Rev S3: was 118)
RIVER_Z_CEN        =  44.0;        // mm, River bay Z centre — stbd half (Rev S3: was 45)
AVINICS_X_CEN      = CX;           // mm, both bays share gondola X centreline
AVINICS_BOSS_DX    =  42.0;        // mm, ±X Faraday tray corner boss offset (Rev S3: was 40)
AVINICS_BOSS_DZ    =  27.0;        // mm, ±Z Faraday tray corner boss offset (Rev S3: was 25)
AVINICS_PANEL_X    =  95.0;        // mm, dorsal access panel opening X (Rev S3: was 85)
AVINICS_PANEL_Z    =  65.0;        // mm, dorsal access panel opening Z (Rev S3: was 55)

// Faraday enclosure external envelope and fan specification (Rev S3).
//   Each avionics bay (Inara port, River stbd) is enclosed in a 5-walled
//   aluminium-sheet Faraday tray.  The hull dorsal skin IS the 6th wall.
//   The access panel cover (105×75 mm, copper-foil-lined PETG or 0.5 mm Al)
//   completes the EMI shield when installed.
//   Tray body inserts through AVINICS_PANEL_X × AVINICS_PANEL_Z dorsal opening.
//   Cape-B (Zoë) and Cape-A (Wash) PCBs mount on INTERNAL standoffs inside tray.
//   One 25 mm axial fan per tray on +X face; filtered PTFE-sleeved cable exits.
//   Ref: CLAUDE.md §1.4.1 (500 W/m² design target; bonding; fan; log μSD); TODO §1.4.1.
FARADAY_ENC_X   = 95.0;   // mm, tray external X (= AVINICS_PANEL_X, fits panel opening)
FARADAY_ENC_Z   = 65.0;   // mm, tray external Z (= AVINICS_PANEL_Z, fits panel opening)
FARADAY_ENC_Y   = 65.0;   // mm, tray depth below dorsal face (stack 29.2 mm + fan 25 mm + margin)
FARADAY_WALL    =  1.5;   // mm, tray wall thickness (0.5 mm Al sheet + PETG shell = ≤ 1.5 mm)
FARADAY_FAN_D   = 25.0;   // mm, axial fan diameter (25 mm × 10 mm, mounted on tray +X wall)
FARADAY_MOUNT_DX = AVINICS_BOSS_DX;  // mm, ±X tray corner M3 boss offset (= 42.0 mm)
FARADAY_MOUNT_DZ = AVINICS_BOSS_DZ;  // mm, ±Z tray corner M3 boss offset (= 27.0 mm)

// ----------------------------------------------------------------------------
// Module: wing_root_mortise
//   Rectangular slot cut through one Z-face wall to receive the wing root tenon.
//   z_sign = +1: port wall (Z = DZ = 163 mm); z_sign = −1: stbd wall (Z = 0).
//   Cut depth = WALL_MM + WING_ROOT_TAB_L + 1 mm cutter overshoot.
//   WING_MORT_CLR = 0.4 mm/side added per CLAUDE.md positive-stop slip-fit req.
//   VERIFY mortise position vs slicer cross-section before printing.
//   Ref: s_wings_s1223_revo.scad fuselage_root_tab(); CLAUDE.md §Fabrication.
// ----------------------------------------------------------------------------
module wing_root_mortise(z_sign) {
    cut_depth = WALL_MM + WING_ROOT_TAB_L + 1.0;
    z_lo = (z_sign > 0) ? (DZ - cut_depth) : 0.0;

    translate([WING_ROOT_X_CEN - MORT_W / 2,
               WING_ROOT_Y_CEN - MORT_H / 2,
               z_lo])
    cube([MORT_W, MORT_H, cut_depth]);
}

// ----------------------------------------------------------------------------
// Module: wing_spar_bore
//   Full-Z through-bore for the CF-TUBE-12MM wing spar (12 mm OD × 1.5 mm wall).
//   Runs the entire gondola Z span (DZ = 163 mm) with 1 mm overshoot each end.
//   X = WING_SPAR_X_CEN (30% chord from LE);  Y = WING_ROOT_Y_CEN (chord line).
//   Applied at the outer difference level to cut through hull walls AND
//   both spar_bearing_block solids in a single boolean operation.
//   Ref: s_wings_s1223_revo.scad spar_bore(); CF-TUBE-12MM per bom_revO.csv.
// ----------------------------------------------------------------------------
module wing_spar_bore() {
    translate([WING_SPAR_X_CEN, WING_ROOT_Y_CEN, -1.0])
    cylinder(h = DZ + 2.0, d = WING_SPAR_BORE_D);
}

// ----------------------------------------------------------------------------
// Module: spar_bearing_block
//   Solid annular boss on the interior Z-face wall, co-axial with the wing spar.
//   Provides the load-transfer annulus between the CF spar and the gondola hull.
//   Boss OD = 22 mm; the spar bore is removed by wing_spar_bore() at the outer
//   difference level (not inside this module) to guarantee a single clean cut.
//   A single M3 grub-screw tap hole from the +Y face retains the spar against
//   axial (Z-direction) walking; matches hinge_pin_block retention pattern.
//
//   z_sign = +1: port wall (boss protrudes in −Z from interior face at Z = DZ−WALL_MM)
//   z_sign = −1: stbd wall (boss protrudes in +Z from interior face at Z = WALL_MM)
//
//   Annular contact area = π/4×(22²−12.3²) = 260.8 mm² → σ = 0.073 MPa at 3g tip load.
//   FOS_bearing = 685 (CF-PETG compressive yield ≈ 50 MPa).  See analysis above.
//   Ref: load analysis above; CLAUDE.md min 2-wall contact annulus (4.85 mm >> 2×0.6 mm).
// ----------------------------------------------------------------------------
module spar_bearing_block(z_sign) {
    z_int_face = (z_sign > 0) ? (DZ - WALL_MM) : WALL_MM;
    z_blk_lo   = (z_sign > 0) ? (z_int_face - SPAR_BOSS_H) : z_int_face;
    z_blk_cen  = z_blk_lo + SPAR_BOSS_H / 2;

    difference() {
        // Boss cylinder: 22 mm OD × 10 mm tall; spar bore removed externally.
        translate([WING_SPAR_X_CEN, WING_ROOT_Y_CEN, z_blk_lo])
        cylinder(h = SPAR_BOSS_H, d = WING_SPAR_BOSS_OD);

        // M3 grub-screw tap bore from +Y face, centred on spar axis.
        //   Retains CF-TUBE-12MM against Z walking.
        //   Grub screw: DIN 913 M3×4 (tightened after spar insertion).
        translate([WING_SPAR_X_CEN,
                   WING_ROOT_Y_CEN + WING_SPAR_BOSS_OD / 2,
                   z_blk_cen])
        rotate([-90, 0, 0])   // bore axis toward spar centre from +Y exterior
        cylinder(h = SPAR_BOSS_H / 2 + 0.5, d = SPAR_GRUB_TAP_D);
    }
}

// ----------------------------------------------------------------------------
// Module: nacelle_servo_mount_block
//   Solid rectangular mounting pad on the interior Z-face wall for the nacelle
//   tilt servo (DS3218MG class: 40 × 20 × 38 mm body, ±17.5 mm lug spacing).
//   Provides:
//     • Flat inboard face for servo body seating (normal to Z axis)
//     • 4× M3 heat-set insert pockets (±17.5 mm × ±8 mm pattern)
//     • 10 × 6 mm lead conduit slot through inboard face for servo wiring
//   Servo output shaft points outboard (toward nacelle in Z direction).
//   A separately-printed nacelle_servo_bracket.stl (to be generated) clamps
//   the servo body to this pad via 4× M3×10 SHCS.
//
//   z_sign = +1: port wall  (pad protrudes in −Z, shaft toward port nacelle)
//   z_sign = −1: stbd wall  (pad protrudes in +Z, shaft toward stbd nacelle)
//
//   Servo stall torque reaction: 4× M3 inserts at 35 mm couple arm → 35 N/bolt.
//   FOS_bolt = 400 / 35 = 11.4.  See load analysis above.
//   Ref: DS3218MG datasheet; PHASED_BUILD_GUIDE.md Phase 3 tilt servo install.
// ----------------------------------------------------------------------------
module nacelle_servo_mount_block(z_sign) {
    // z_int_face: interior face of lateral Z wall (inset WALL_MM from exterior)
    z_int_face = (z_sign > 0) ? (DZ - WALL_MM) : WALL_MM;
    // Block origin in Z: port protrudes inward (-Z), stbd protrudes inward (+Z)
    z_blk_lo   = (z_sign > 0) ? (z_int_face - NSVMT_PAD_T) : z_int_face;
    // M3 bores drilled from the inboard (interior-facing) face of the pad.
    //   Port: inboard face is at z_blk_lo  → bores start there, go in +Z.
    //   Stbd: inboard face is at z_blk_lo+NSVMT_PAD_T → bores start NSVMT_M3_DEP below.
    z_bore_lo  = (z_sign > 0)
        ? z_blk_lo
        : (z_blk_lo + NSVMT_PAD_T - NSVMT_M3_DEP);

    difference() {
        // Mounting pad solid
        translate([NSVMT_X_CEN - NSVMT_PAD_W / 2,
                   NSVMT_Y_CEN - NSVMT_PAD_H / 2,
                   z_blk_lo])
        cube([NSVMT_PAD_W, NSVMT_PAD_H, NSVMT_PAD_T]);

        // 4× M3 heat-set insert pockets bored from inboard face into pad.
        //   ±NSVMT_HOLE_S_X (±17.5 mm) in X: matches DS3218MG lug-hole spacing.
        //   ±NSVMT_HOLE_S_Y (±8.0 mm)  in Y: matches DS3218MG lug width / 2.
        for (dx = [-NSVMT_HOLE_S_X, NSVMT_HOLE_S_X])
        for (dy = [-NSVMT_HOLE_S_Y, NSVMT_HOLE_S_Y])
            translate([NSVMT_X_CEN + dx, NSVMT_Y_CEN + dy, z_bore_lo])
            cylinder(h = NSVMT_M3_DEP + 0.1, d = NSVMT_M3_OD);

        // Servo lead conduit slot: 10 × 6 mm through inboard half of pad.
        //   Routes servo signal + power leads from the mount face to interior.
        translate([NSVMT_X_CEN - NSVMT_CONDUIT_W / 2,
                   NSVMT_Y_CEN - NSVMT_CONDUIT_H / 2,
                   z_bore_lo])
        cube([NSVMT_CONDUIT_W, NSVMT_CONDUIT_H, NSVMT_PAD_T / 2 + 0.1]);
    }
}

// ----------------------------------------------------------------------------
// Module: avinics_dorsal_boss
//   Single M3 heat-set insert boss post on the interior dorsal face, protruding
//   in −Y (downward into gondola interior).  Provides one corner standoff anchor
//   for Cape-B avionics PCB (one call per corner of each bay, 4 per bay).
//   Reuses m3_boss() with AVINICS_BOSS_ROT = [90,0,0] (maps +Z → −Y).
//   Boss geometry: BOSS_OD = 8 mm, BOSS_H = 6 mm, bore BOSS_BORE_D = 4.1 mm.
//   Boss base fused to interior dorsal face at AVINICS_DORSAL_Y; extends to
//   AVINICS_DORSAL_Y − BOSS_H (= −218.6 mm approx) into gondola interior.
//   VERIFY each boss clears GPS recess (Ø36 mm, R=18 mm) and GPS M2 holes in slicer.
//   Ref: Ruthex RX-M3x5.7; Cape-B-2 90×60 mm PCB corner hole pattern; CLAUDE.md.
// ----------------------------------------------------------------------------
module avinics_dorsal_boss(x_pos, z_pos) {
    m3_boss([x_pos, AVINICS_DORSAL_Y, z_pos], AVINICS_BOSS_ROT);
}

// ----------------------------------------------------------------------------
// Module: avinics_dorsal_panel_cut
//   Rectangular through-cut (95×65 mm, Rev S3) in the dorsal skin for avionics
//   bay access and Faraday tray insertion.
//   Faraday tray body (FARADAY_ENC_X × FARADAY_ENC_Z = 95×65 mm) inserts
//   through this opening from outside; tray screws to AVINICS_BOSS_* posts below.
//   Cover (105×75 mm) overlaps the cut perimeter by 5 mm on all sides for a
//   positive-stop EMI-seal shoulder; secured by 4× M2 screws or spring clips.
//
//   Cut Y span: AVINICS_DORSAL_Y − 1.0 to AVINICS_DORSAL_Y + WALL_MM + 1.0
//     = through interior skin (−1 mm overshoot) to past exterior face (+1 mm).
//
//   x_cen, z_cen: panel centre in X and Z (AVINICS_X_CEN and bay Z centre).
//
//   GPS recess (Ø36 mm) overlaps both panels; GPS antenna installed from outside
//   before Faraday tray and cover; access cover designed with Ø38 mm clearance bore.
//   Applied at outer difference level alongside wing_root_mortise and spar bore.
//   VERIFY opening bounds and GPS overlap in slicer before printing.
//   Ref: FARADAY_ENC_* parameters (Rev S3); GPS co-location analysis 2026-06-08;
//   CLAUDE.md positive-stop shoulder requirement for flight-critical joints.
// ----------------------------------------------------------------------------
module avinics_dorsal_panel_cut(x_cen, z_cen) {
    translate([x_cen - AVINICS_PANEL_X / 2,
               AVINICS_DORSAL_Y - 1.0,
               z_cen - AVINICS_PANEL_Z / 2])
    cube([AVINICS_PANEL_X, WALL_MM + 2.0, AVINICS_PANEL_Z]);
}

// ============================================================
// Main geometry
// ============================================================
//
// Shell source note (Rev Q):
//   2.0 mm foam-fill skin shell generated by blender_shells_v3_2mm.py
//   (WALL_MM=2.0, SCALE=2.9294x, centroid-inset hollowing) from Thingiverse
//   source s_cargo_sect.stl.  Repaired to manifold (0 NM edges) by
//   repair_shells_for_scad.py using voxel remesh at 1.2 mm pitch.
//   STL bounds: X=-202..-7, Y=-415..-211, Z=0..163 mm.
//   Inner scale used: sx=0.979459, sy=0.980354, sz=0.975496.
//
// ── CSG tree overview (Rev S3) ────────────────────────────────────────────────
//
//   outer_union
//   ├─ difference              ← bay cut + wing mortises + spar bore + avionics panels
//   │  ├─ inner_union
//   │  │  ├─ difference        ← per-skin cuts (camera, GPS)
//   │  │  │  ├─ import(shell_stl)
//   │  │  │  ├─ fpv_cut
//   │  │  │  └─ gps_mount_cut ×2
//   │  │  ├─ m3_boss ×12           ← joint-face bosses (outside bay zone)
//   │  │  ├─ belly_rib ×2          ← ribs CUT by door_bay_cut within bay zone
//   │  │  ├─ hinge_pin_block ×2    ← outside bay zone; survive door_bay_cut
//   │  │  ├─ servo_mount_pad ×2    ← cargo door servos, AFT of bay
//   │  │  ├─ spar_bearing_block ×2 ← port + stbd Z-wall bosses (Rev S1)
//   │  │  ├─ nacelle_servo_mount_block ×2 ← port + stbd tilt-servo pads (S1)
//   │  │  ├─ avinics_dorsal_boss ×8 ← Inara (port) + River (stbd) Faraday tray mounts (S2/S3)
//   │  │  └─   (4 bosses per bay, ±42 mm X × ±27 mm Z from bay Z centre)
//   │  ├─ door_bay_cut              ← removes belly skin + hinge clearance
//   │  ├─ wing_root_mortise ×2      ← port + stbd tenon slots (S1)
//   │  ├─ wing_spar_bore            ← 12.3 mm full-Z spar bore (S1)
//   │  ├─ avinics_dorsal_panel_cut  ← Inara bay 95×65 mm dorsal opening (S3)
//   │  └─ avinics_dorsal_panel_cut  ← River bay 95×65 mm dorsal opening (S3)
//   └─ latch_catch_lip ×4          ← added AFTER cut; protrude into bay opening

union() {

    // ── A. Inner structure minus door opening ─────────────────────────────────
    difference() {

        union() {
            // A1. Shell with existing sensor/GPS aperture cuts.
            difference() {
                // 2.0 mm foam-fill cargo gondola shell (manifold for CGAL ops)
                import("../../thingverse-serenity/files-hollowed-18in/s_cargo_sect_shell24_2mm_repaired.stl");

                // Nadir FPV camera aperture
                fpv_cut(CARGO_CAM_POS, NADIR_ROT);

                // Dual GPS flush-mount receptacles on dorsal face.
                //   GPS_PORT (Z=CZ+30): SMA coax to FC/Sensor Cape 1 (primary).
                //   GPS_STBD (Z=CZ-30): SMA coax to FC/Sensor Cape 2 (redundant).
                //   Independent capes satisfy CLAUDE.md failover requirement.
                //   VERIFY both positions on dorsal skin in slicer before print.
                gps_mount_cut(GPS_PORT_POS, DORSAL_ROT);
                gps_mount_cut(GPS_STBD_POS, DORSAL_ROT);
            }

            // A2. M3 heat-set boss posts at fore joint face (X = -7 mm).
            //     Bosses extend into interior (-X).  All outside door bay zone.
            //     VERIFY each boss is inside the hull skin in slicer.
            m3_boss(BOSS_FORE_1, BOSS_FORE_ROT);
            m3_boss(BOSS_FORE_2, BOSS_FORE_ROT);
            m3_boss(BOSS_FORE_3, BOSS_FORE_ROT);
            m3_boss(BOSS_FORE_4, BOSS_FORE_ROT);
            m3_boss(BOSS_FORE_5, BOSS_FORE_ROT);
            m3_boss(BOSS_FORE_6, BOSS_FORE_ROT);

            // A3. M3 boss posts at aft joint face (X = -202 mm).
            //     Bosses extend into interior (+X).  All outside door bay zone.
            m3_boss(BOSS_AFT_1, BOSS_AFT_ROT);
            m3_boss(BOSS_AFT_2, BOSS_AFT_ROT);
            m3_boss(BOSS_AFT_3, BOSS_AFT_ROT);
            m3_boss(BOSS_AFT_4, BOSS_AFT_ROT);
            m3_boss(BOSS_AFT_5, BOSS_AFT_ROT);
            m3_boss(BOSS_AFT_6, BOSS_AFT_ROT);

            // A4. Belly stiffener ribs on interior nadir face.
            //     Ribs at X=-70 and X=-140 both fall within the door bay zone
            //     (DOOR_OPEN_AFT=-152 to DOOR_OPEN_FWD=-52); door_bay_cut will
            //     remove them within that X range.  Sections outside the bay
            //     (X=-7..-49 fore zone; X=-155..-202 aft zone) are unaffected
            //     and continue to brace the belly skin for foam pour.
            //     VERIFY rib positions inside hull skin in slicer.
            belly_rib(-70);
            belly_rib(-140);

            // A5. Hinge-pin mount blocks at each door-bay X end.
            //     Both blocks sit OUTSIDE the door_bay_cut X zone and survive.
            //     AFT block: x_start = DOOR_BAY_AFT - PIN_BLOCK_L = -165
            //     FWD block: x_start = DOOR_BAY_FWD               = -49
            //     VERIFY blocks are fused to interior belly face in slicer.
            hinge_pin_block(DOOR_BAY_AFT - PIN_BLOCK_L);   // AFT: X = -165..-155
            hinge_pin_block(DOOR_BAY_FWD);                  // FWD: X =  -49..-39

            // A6. Servo mounting pads for door-actuator SG90 servos.
            //     Both pads AFT of door bay (X_CEN = -182 mm); outside cut zone.
            //     Port-door servo: pad centred at (SERVO_X_CEN, SERVO_PORT_Z).
            //     Stbd-door servo: pad centred at (SERVO_X_CEN, SERVO_STBD_Z).
            //     cargo_door_servo_bracket.stl bolts to each pad via 4x M2.5.
            //     VERIFY pad footprint clears interior ribs and foam-fill zone.
            servo_mount_pad(SERVO_X_CEN, SERVO_PORT_Z);   // port-door servo
            servo_mount_pad(SERVO_X_CEN, SERVO_STBD_Z);   // stbd-door servo

            // A7. Wing spar bearing blocks at port and stbd interior Z-walls.
            //     Each block: 22 mm OD boss × 10 mm tall, with M3 grub-screw tap.
            //     Boss OD = 22 mm; wall annulus = 4.85 mm (>> 2-perimeter min).
            //     Spar bore (wing_spar_bore) is applied at the outer difference
            //     level so it cuts cleanly through both bosses and hull walls.
            //     Port boss: protrudes −Z from interior face at Z ≈ 161 mm.
            //     Stbd boss: protrudes +Z from interior face at Z ≈ 2 mm.
            //     VERIFY boss Z-range and Y-position in slicer before printing.
            //     Ref: load analysis above; CF-TUBE-12MM per bom_revO.csv.
            spar_bearing_block(+1);    // port: Z = 151..161 mm
            spar_bearing_block(-1);    // stbd: Z =   2..12  mm

            // A8. Nacelle tilt servo mount blocks at port and stbd interior Z-walls.
            //     Each block: 52×30 mm face × 8 mm deep; 4× M3 heat-set inserts;
            //     10×6 mm lead conduit slot.  DS3218MG-class servo (≥25 kg·cm)
            //     mounts via separately-printed nacelle_servo_bracket.stl using
            //     4× M3×10 SHCS through the bracket into these inserts.
            //     Block Y range: NSVMT_Y_CEN ± 15 mm = −303 .. −273 mm (above Y=−407
            //     door cut top — not affected by door_bay_cut).
            //     Port block: protrudes −Z from interior face (Z ≈ 153..161 mm).
            //     Stbd block: protrudes +Z from interior face (Z ≈   2..10  mm).
            //     VERIFY block footprint clears conduits in slicer before printing.
            //     Ref: DS3218MG datasheet; PHASED_BUILD_GUIDE.md Phase 3.
            nacelle_servo_mount_block(+1);  // port: Z = 153..161 mm
            nacelle_servo_mount_block(-1);  // stbd: Z =   2..10  mm

            // A9. Inara's avionics bay — port half, Z centre = 119 mm (Rev S3).
            //     4× M3 Faraday tray anchor bosses on interior dorsal face (Y≈−213 mm).
            //     Boss pattern: ±42 mm (X) × ±27 mm (Z) from bay centre.
            //     Boss positions (X, Z): (−144.2,92), (−60.2,92), (−144.2,146), (−60.2,146).
            //     GPS_PORT (Z=104.7 mm) co-located; nearest boss ≥ 43.9 mm from GPS centre ✓.
            //     Cape PCBs mount on internal standoffs inside Faraday tray, not on hull bosses.
            //     VERIFY boss positions and clearance in slicer before printing.
            //     Ref: Rev S3 boss analysis; GPS_PORT recess R=18 mm; FARADAY_* parameters.
            for (dx = [-AVINICS_BOSS_DX, AVINICS_BOSS_DX])
            for (dz = [-AVINICS_BOSS_DZ, AVINICS_BOSS_DZ])
                avinics_dorsal_boss(AVINICS_X_CEN + dx, INARA_Z_CEN + dz);

            // A10. River's avionics bay — stbd half, Z centre = 44 mm (Rev S3).
            //      4× M3 Faraday tray anchor bosses on interior dorsal face (Y≈−213 mm).
            //      Boss positions (X, Z): (−144.2,17), (−60.2,17), (−144.2,71), (−60.2,71).
            //      GPS_STBD (Z=44.7 mm) co-located; nearest boss ≥ 49.6 mm from GPS centre ✓.
            //      Cape PCBs mount on internal standoffs inside Faraday tray, not on hull bosses.
            //      10 mm inter-bay gap (Z = 76.5..86.5 mm) available for conduit routing.
            //      VERIFY boss positions and clearance in slicer before printing.
            //      Ref: Rev S3 boss analysis; GPS_STBD recess R=18 mm; FARADAY_* parameters.
            for (dx = [-AVINICS_BOSS_DX, AVINICS_BOSS_DX])
            for (dz = [-AVINICS_BOSS_DZ, AVINICS_BOSS_DZ])
                avinics_dorsal_boss(AVINICS_X_CEN + dx, RIVER_Z_CEN + dz);
        }

        // ── Cargo-bay door opening ────────────────────────────────────────────
        //   Subtracts from ALL inner-union geometry including ribs.
        //   Removes belly skin (X=-152..-52, full Z, Y=-416..-407).
        //   3 mm shell frame lips remain at X=-155..-152 and X=-52..-49.
        door_bay_cut();

        // ── Wing root mortises (tenon slots through lateral Z walls) ─────────
        //   Each slot: MORT_W × MORT_H opening (30.8 × 20.8 mm) through wall.
        //   Depth = WALL_MM + WING_ROOT_TAB_L + 1 mm overshoot = 15 mm.
        //   Port slot: Z = 148..163 mm (through port wall at DZ=163).
        //   Stbd slot: Z =   0.. 15 mm (through stbd wall at Z=0).
        //   VERIFY mortise position vs wing STL in slicer before printing.
        //   Ref: s_wings_s1223_revo.scad fuselage_root_tab() geometry.
        wing_root_mortise(+1);   // port wall
        wing_root_mortise(-1);   // stbd wall

        // ── Wing spar through-bore (full Z span) ─────────────────────────────
        //   12.3 mm dia bore at (WING_SPAR_X_CEN, WING_ROOT_Y_CEN) = (-70, -288.6).
        //   Passes through both Z walls AND both spar_bearing_block solids.
        //   CF-TUBE-12MM (12 mm OD) slides through with 0.15 mm radial clearance.
        //   Spar retained by M3 grub screw in each bearing block after final fit.
        //   VERIFY bore X and Y in slicer cross-section before printing.
        //   Ref: CF-TUBE-12MM (bom_revO.csv); s_wings_s1223_revo.scad spar_bore().
        wing_spar_bore();

        // ── Inara avionics dorsal access panel (port, Z≈86.5..151.5 mm, Rev S3) ──
        //   95×65 mm cut through dorsal skin at Inara bay Z centre = 119 mm.
        //   Faraday tray body (FARADAY_ENC_X × FARADAY_ENC_Z = 95×65 mm) inserts
        //   through this opening from outside with ~1 mm assembly clearance.
        //   Cover (105×75 mm, 5 mm shoulder) forms EMI-sealed lid when installed.
        //   GPS_PORT recess (Ø36 mm at Z=104.7 mm) overlaps panel: GPS installed
        //   from outside before Faraday tray; cover has Ø38 mm clearance bore.
        //   VERIFY opening bounds and GPS overlap in slicer.
        avinics_dorsal_panel_cut(AVINICS_X_CEN, INARA_Z_CEN);

        // ── River avionics dorsal access panel (stbd, Z≈11.5..76.5 mm, Rev S3) ─
        //   95×65 mm cut through dorsal skin at River bay Z centre = 44 mm.
        //   Same Faraday tray geometry and GPS co-location note as Inara panel.
        //   GPS_STBD recess (Ø36 mm at Z=44.7 mm) centred in panel zone.
        //   10 mm gap from Inara lower edge (86.5 mm) for inter-bay conduit run.
        //   VERIFY opening bounds and GPS overlap in slicer.
        avinics_dorsal_panel_cut(AVINICS_X_CEN, RIVER_Z_CEN);
    }

    // ── B. Latch-catch lips (added after door_bay_cut; not affected by it) ────
    //   4 lips total: 2 at AFT opening edge, 2 at FWD opening edge.
    //   Each protrudes CATCH_PROTRUSION mm into the bay opening and rises
    //   CATCH_T mm above BELLY_INT_Y.  Bottom face (Y=BELLY_INT_Y) is the
    //   catch surface for cargo_cradle_autolatch 2 mm flex-tab hooks.
    //   VERIFY lips are accessible through the open door in slicer.
    //
    //   AFT-edge lips (x_start = DOOR_OPEN_AFT = -152, protrude toward +X)
    latch_catch_lip(DOOR_OPEN_AFT, CATCH_Z_STBD);
    latch_catch_lip(DOOR_OPEN_AFT, CATCH_Z_PORT);
    //   FWD-edge lips (x_start = DOOR_OPEN_FWD - CATCH_PROTRUSION = -57)
    latch_catch_lip(DOOR_OPEN_FWD - CATCH_PROTRUSION, CATCH_Z_STBD);
    latch_catch_lip(DOOR_OPEN_FWD - CATCH_PROTRUSION, CATCH_Z_PORT);
}
