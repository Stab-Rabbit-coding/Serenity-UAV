// ============================================================
// cargo_sect_shell24.scad
// Cargo gondola shell for Serenity Rev N 24" hull (s_cargo_sect.stl).
//
// Rev R1 (2026-06-22): Fixed port/stbd mirroring axis for the wing-root
//   subsystem — wing_root_mortise(), wing_spar_bore(), spar_bearing_block(),
//   and nacelle_servo_mount_block() previously mirrored "port wall" vs
//   "stbd wall" across Z (vertical/dorsal), contradicting this file's own
//   header (CZ = vertical) and CLAUDE.md's hull-frame standard (X = lateral/
//   port).  Root cause: the subsystem had been modelled using the WING's
//   own internal pre-permutation convention (wings_s1223_revo.scad:
//   "X: chordwise, Y: thickness, Z: spanwise") without applying that file's
//   own X<-Z, Y<-X, Z<-Y permutation before use here.  Added CARGO_X_WALL_
//   PORT/STBD (measured lateral wall positions, mapped through this file's
//   own bake transform) and WING_ROOT_Z_CEN (fixed root height for both
//   sides, from CLAUDE.md's validated baked wing Z-extent); re-derived all
//   four modules' geometry to mirror across X with this fixed Z.  Also
//   fixed wing_spar_bore() to run the full lateral span through BOTH walls
//   (a real continuous tip-to-tip spar passage — previously it was a short
//   Z-axis bore that never reached the far wall at all).
//   KNOWN OPEN ISSUES from this fix (see inline VERIFY/note comments):
//     - The spar/mortise chordwise (Y) offset still uses the pre-existing
//       WING_ROOT_Y_CEN value pending the separately-tracked stale-161mm-
//       chord re-derivation (TODO.md §1.1.2).
//     - WING_ROOT_Z_CEN = 62.5 mm overlaps River's avionics bay Z range
//       (24..64 mm) — a real packaging conflict, NOT resolved here; see
//       NSVMT_Z_OFFSET comment and TODO.md §1.1.3.3.
//
// Rev R (2026-06-11): Rev R baseline — consolidated from Rev S4 (2026-06-08); no geometry changes.
//
// Rev S4 (2026-06-08): Correct Cape-B-2/Cape-A-2 PCB dimensions — was CAPE-B-1 legacy.
//   VERIFIED from CAPE-B-2.kicad_pcb Edge.Cuts (X=121..176, Y=87.5..122.5 mm):
//   Both Cape-B-2 (XO) and Cape-A-2 (Pilot) are 55×35 mm, not the 90×60 mm / 85×55 mm
//   values used in Rev S2/S3.  Those came from CAPE-B-1's archived footprint referenced
//   in CAPE-B-2.md; CAPE-B-2 was redesigned to match the 55×35 mm PB2-I footprint.
//   All AVINICS_BOSS_* and FARADAY_ENC_* parameters corrected accordingly:
//     AVINICS_BOSS_DX: 42 → 25 mm  (tray ±24.5 mm PCB hole + 0.5 mm wall inset)
//     AVINICS_BOSS_DZ: 27 → 15 mm  (tray ±14.5 mm PCB hole + 0.5 mm wall inset)
//     AVINICS_PANEL_X: 95 → 62 mm  (Faraday tray 60 mm + 1 mm insertion clearance each side)
//     AVINICS_PANEL_Z: 65 → 42 mm  (Faraday tray 40 mm + 1 mm insertion clearance each side)
//     FARADAY_ENC_X:   95 → 60 mm  (Cape-B-2 55 mm + 1.5 mm Al wall each side)
//     FARADAY_ENC_Z:   65 → 40 mm  (Cape-B-2 35 mm + 1.5 mm Al wall each side)
//     FARADAY_ENC_Y:   65 → 55 mm  (39.2 mm stack + 5 mm clearance + 7 mm fan + 1.5 mm floor)
//   Access cover now 72×52 mm (panel 62×42 + 5 mm shoulder each side).
//   Inara tray Z = 99..139 mm; River tray Z = 24..64 mm; inter-bay gap = 35 mm.
//   GPS clearances re-verified at new boss positions: nearest boss ≥ 25.0 mm to GPS ✓.
//   CAPE_PCB_* and CAPE_HOLE_* constants added for cape/tray SCAD cross-referencing.
//   Ref: CAPE-B-2.kicad_pcb pad MH1–MH4 (2.7 mm drill at ±24.5×±14.5 mm from board ctr).
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
//   dorsal face; 85×55 mm dorsal access panel cut.  Cape-B (XO Cape-A-2,
//   90×60 mm) mounts on 6 mm standoffs; Cape-A (Pilot Cape-B-2, 85×55 mm)
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
//   Ref: wings_s1223_revo.scad; DS3218MG datasheet; load analysis in source.
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
//   - Shell source: cargo_sect_shell24_2mm_repaired.stl
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
// Coordinate system (24"-scaled STL world space = hull frame per CLAUDE.md):
//   X — lateral,      positive toward port  (left)
//   Y — longitudinal, positive aft (back)   NOTE: Y is aft; Z is dorsal/up
//   Z — vertical,     positive dorsal (up)
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
//
// HULL-FRAME COORDINATE STANDARD — Rev R1 (2026-06-11).  See CLAUDE.md.
//   Hull frame (canonical for ALL design artifacts): X = +port (left),
//   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
//   world origin.  This SCAD models the cargo section in its historical
//   part-local frame; the PUBLISHED STL
//   (airframe/stls/fuselage/cargo/s_cargo_sect_shell24_2mm_repaired.stl)
//   is BAKED into hull frame by tools/bake_hull_frame.py using the
//   placement validated in SerenityAssembly.FCStd (2026-06-10):
//     Base: Px = −274.400 mm (−10.80 in), Py = −282.800 mm (−11.13 in), Pz = 0
//     Rotation: 180° about Z  (local +X → hull −X;  local +Y → hull −Y)
//   Forward transform: hull_X = −local_X − 274.4   (port axis)
//                      hull_Y = −local_Y − 282.8   (aft axis)
//                      hull_Z = local_Z             (dorsal axis — unchanged)
//   Inverse transform: local_X = −hull_X − 274.4
//                      local_Y = −hull_Y − 282.8
//                      local_Z = hull_Z
//   Baked hull-frame bounds: X −267.0..−72.9, Y −71.5..+132.0, Z 0..163.2 mm.
//   After ANY regeneration from this source, re-run:
//       python3 tools/bake_hull_frame.py Cargo_Shell Cargo_Shell_Repair2
//   R1 AUDIT NOTE: in the validated hull frame the LONGITUDINAL axis is Y
//   (head and cargo sections mate at hull_Y ≈ −71 mm; X is lateral/port).
//   The 2026-06-10 head-cargo joint analysis below uses hull_X as the
//   mating axis — re-verify BOSS_FORE/BOSS_AFT positions against the
//   baked meshes before printing (TODO.md §1.1.1.1).
//
//   NOTE: the 180° rotation REVERSES both the port and aft axes.  What is
//   the "fore" face in STL local space (local_X = −7) becomes the AFT face
//   in the hull-frame assembly, and vice-versa.
//
//   Key hull-frame positions:
//     STL fore face (local_X = −7):   hull_X = −(−7) − 274.4 = −267.4 mm (−10.53 in)
//       → This is the AFT face of the cargo section in the assembled aircraft.
//     STL aft face  (local_X = −202): hull_X = −(−202) − 274.4 = −72.4 mm (−2.85 in)
//       → This is the FORE (nose-ward) face of the cargo section in the assembly.
//     Centroid (CX = −102.19 mm): hull_X = −(−102.19) − 274.4 = −172.2 mm (−6.78 in)
//     Centroid (CY = −328.63 mm): hull_Y = −(−328.63) − 282.8 = +45.8 mm (+1.80 in)
//     Centroid (CZ =   74.70 mm): hull_Z = 74.70 mm (2.94 in)  [unchanged]
//
//   Head-to-cargo joint (2026-06-10 analysis):
//     Head_Shell aft face at head local_X = 99 →
//       hull_X = 99 + (−332) = −233 mm (−9.17 in)
//     Matching cargo local_X for hull_X = −233:
//       local_X = −(−233) − 274.4 = −41.4 mm
//     BOSS_FORE positions corrected: X = −7 → X = −41.4 mm to place mating
//     bosses at the correct joint station in hull space.
//     All Y/Z offsets remain estimated; VERIFY in slicer.
//
// ============================================================

SCALE_24  = 2.9294;   // 24" hull scale factor

// Cargo gondola centroid in 24"-scaled STL world coordinates
CX = -102.19;   // mm -- lateral axis (positive = port)
CY = -328.63;   // mm -- longitudinal axis (positive = aft)
CZ =   74.70;   // mm -- vertical axis (positive = dorsal/up)

// Hollow-shell parameters (Rev R: computed from solid STL bounding box)
// Bounding box of cargo_sect_shell24_repaired.stl after voxel-remesh (1.5 mm pitch):
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
//   Rev R2 (2026-07-03) — CORRECTED.  The "STL axes: X=forward, Y=dorsal,
//   Z=port" comment this replaced was itself the bug: same class of legacy-
//   permutation error already fixed for the wing subsystem in Rev R1 (see
//   header note).  Empirically confirmed against the real canonical mesh
//   (airframe/blender-scripts/files-hollowed-24in/cargo_sect_shell24_2mm_repaired.stl):
//   local Z range 0..163.2 mm matches the documented bake-invariant hull Z
//   range exactly (CLAUDE.md "hull_Z = local_Z, unchanged") -- Z IS dorsal.
//   X range -201.7..-7.4 mm matches CARGO_X_WALL_PORT/STBD (fixed Rev R1) --
//   X IS lateral.  Y is longitudinal, as this file's own header (line ~171)
//   always correctly stated.  The GPS/avionics-bay/nadir-camera modules below
//   were the only ones still using the old (Y=dorsal) mental model; fixed
//   here.  Cutter cylinders are built along local +Z by default (see
//   gps_mount_cut/fpv_cut bodies) so a DORSAL cut (exterior face at high Z,
//   cutting toward lower Z into the interior) needs NO rotation, and a NADIR
//   cut (exterior face at Z=0, cutting toward higher Z into the interior)
//   needs a 180 deg flip.
DORSAL_ROT = [   0, 0, 0 ];  // no rotation -- cutter's native -Z cut direction
                              //   already points from a high-Z exterior face
                              //   inward, matching the dorsal skin.
NADIR_ROT  = [ 180, 0, 0 ];  // flips cutter to cut toward +Z, matching a
                              //   Z=0 (belly) exterior face cutting inward.

// Dorsal / nadir exterior skin Z -- measured directly from the canonical
// mesh bounds above (not reused from any of the legacy Y-based numbers).
DORSAL_Z_EXT = 163.2;   // mm, exterior dorsal (top) skin
NADIR_Z_EXT  =   0.0;   // mm, exterior nadir (belly) skin

// Cargo nadir camera position -- lateral + longitudinal centreline, belly
// exterior face.  (Previously offset CY-76 in the Y slot under the legacy
// Y=dorsal model; that offset served no purpose once Z correctly carries
// the nadir/dorsal distinction, so it is dropped, not reused.)
CARGO_CAM_POS = [ CX, CY, NADIR_Z_EXT ];   // VERIFY in slicer before printing

// GPS antennas -- dorsal-facing, mounted on the actual dorsal (Z-max) skin.
// Confirmed Rev R2 (2026-07-03, user decision): Inara/River bays are a
// port/stbd PAIR at a shared longitudinal station (not fore/aft sequential).
GPS_STATION_Y = CY;   // mm, shared longitudinal (Y) station -- mid-gondola,
                       //   clear of the ring-frame pocket (hull Y=+30 <->
                       //   local Y=-312.8) and the joint-boss zones.
                       //   VERIFY in slicer before printing.

// GPS lateral (X) separation from the gondola centreline (CX = -102.19 mm).
//   Port:  CX - GPS_SEP  (more-negative local X, toward CARGO_X_WALL_PORT).
//   Stbd:  CX + GPS_SEP  (less-negative local X, toward CARGO_X_WALL_STBD).
//   MOVED OUTBOARD 2026-07-06 (user directive): GPS_SEP 30 -> 37.5 mm so each
//   antenna is CO-LOCATED with its Inara/River bay centre (= BAY_SEP_X/2, defined
//   below).  Rationale: the dorsal access cover is only ~46 mm wide after OML
//   trimming, so the Ø38 mm GPS clearance bore in the cover
//   (access_panels_24in.scad) only stays fully ENCLOSED if the antenna is within
//   ~±4 mm of the cover/bay centre.  At the old 30 mm the antenna sat 7.5 mm
//   inboard of the bay centre and the Ø38 bore broke the cover's inboard edge
//   (opened to a scallop).  Co-locating on the bay centre gives 26 mm to each
//   cover edge (7 mm bore margin).  Centre-to-centre now 75 mm (= BAY_SEP_X);
//   retention rings (Ø44 bolt circle) still clear (31 mm gap).  MUST equal
//   BAY_SEP_X / 2 — keep in sync if BAY_SEP_X changes.
GPS_SEP = 37.5;  // mm -- each antenna's X offset from centreline (= BAY_SEP_X/2, bay-centred)

// GPS-PORT: port-side antenna, connected to FC/Sensor Cape 1 (primary GPS).
//   VERIFY all coordinates in slicer -- position must sit on dorsal skin face.
GPS_PORT_POS = [ CX - GPS_SEP, GPS_STATION_Y, DORSAL_Z_EXT ];

// GPS-STBD: starboard-side antenna, connected to FC/Sensor Cape 2 (redundant GPS).
//   VERIFY all coordinates in slicer -- position must sit on dorsal skin face.
GPS_STBD_POS = [ CX + GPS_SEP, GPS_STATION_Y, DORSAL_Z_EXT ];

// M3 boss positions at the head-to-cargo joint face.
//   Joint hull_X = −233 mm → cargo local_X = −41.4 mm (see hull-frame block above).
//   Bosses extend inboard from joint face in the −X direction (into cargo interior).
//   BOSS_FORE_ROT: rotate([0,-90,0]) aligns cylinder axis along −X (into interior).
//   STL bounds at X ≈ −41 station: Y = −415..−211, Z = 0..163; centroid CY=−329, CZ=75.
//   All positions VERIFY in slicer after correction; boss must sit fully inside hull skin.
//   Ref: head-to-cargo joint analysis in hull-frame block above; head_shell24.scad BOSS_AFT.
BOSS_FORE_ROT = [ 0, -90, 0 ];

BOSS_FORE_1 = [ -41.4, CY + 82,  CZ       ];  // VERIFY: dorsal (hull_X = −233 mm joint)
BOSS_FORE_2 = [ -41.4, CY + 41,  CZ + 55  ];  // VERIFY: dorsal-port
BOSS_FORE_3 = [ -41.4, CY - 41,  CZ + 55  ];  // VERIFY: ventral-port
BOSS_FORE_4 = [ -41.4, CY - 82,  CZ       ];  // VERIFY: ventral
BOSS_FORE_5 = [ -41.4, CY - 41,  CZ - 55  ];  // VERIFY: ventral-stbd
BOSS_FORE_6 = [ -41.4, CY + 41,  CZ - 55  ];  // VERIFY: dorsal-stbd

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
// Module: jayne_board_bosses (added Rev R2, 2026-07-03)
//   4x M3 heat-set insert boss posts for the Observer vision/ToF/laser PCB
//   (avionics/kicad/Observer.kicad_pcb, 1.0 × 2.75 in (25.4 × 69.85 mm) double-sided board, mounting
//   holes at board-local (4,4)/(42,4)/(4,44)/(42,44) -- i.e. +/-19 mm x
//   +/-20 mm from board centre).  Mounted on the belly interior floor,
//   standing up (+Z) from just above the nadir exterior skin, centred on
//   CARGO_CAM_POS's (X,Y) station so the board sits directly above/behind
//   the camera aperture -- short local harness runs to J_CAM1/J_CAM2/
//   J_TOF/J_LASER (see Observer.md "Mechanical Mounting and Wiring").
//   Boss base at Z = WALL_MM (interior nadir face); extends to
//   Z = WALL_MM + BOSS_H (= 8 mm) -- an 8 mm standoff starting allowance,
//   pending real (non-placeholder) component-height verification per
//   Observer.md.  PROPOSED placement -- verify in FreeCAD before printing
//   (this hull's geometry is too complex for bounding-box placement per
//   CLAUDE.md "Assembly and Placement").
//   Ref: avionics/kicad/Observer.md; TODO.md §1.2c.3.
// ----------------------------------------------------------------------------
OBSERVER_HOLE_DX = 19.0;   // mm, +/-X half-spacing of Observer's mounting-hole pattern
OBSERVER_HOLE_DY = 20.0;   // mm, +/-Y half-spacing of Observer's mounting-hole pattern
OBSERVER_STATION_X = CX;         // mm, lateral centreline, same as CARGO_CAM_POS
OBSERVER_STATION_Y = CY;         // mm, longitudinal station, same as CARGO_CAM_POS
module jayne_board_bosses() {
    for (dx = [-OBSERVER_HOLE_DX, OBSERVER_HOLE_DX])
    for (dy = [-OBSERVER_HOLE_DY, OBSERVER_HOLE_DY])
        m3_boss([OBSERVER_STATION_X + dx, OBSERVER_STATION_Y + dy, WALL_MM], [0, 0, 0]);
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
// Module: hinge_pin_block   *** SUPERSEDED — Rev R1c (2026-06-29) ***
//
//   This module and its HINGE_Y / HINGE_Z / PIN_BLOCK_* parameters describe a
//   SINGLE shared hinge running along the legacy part-local LATERAL axis, in
//   the PRE-BAKE frame (Y = vertical, Z = lateral).  That is backwards from the
//   Rev R1b door design, where each door is its OWN independent piano hinge
//   pinned at the OUTBOARD belly edge with its axis along hull Y (see
//   generate_cargo_doors.py).  The correct, hull-frame shell-side retention
//   blocks are now produced by
//       airframe/stls/fuselage/cargo/generate_cargo_hinge_retention.py
//   (Rev R1c) → cargo_hinge_retention.stl, which is boolean-unioned into the
//   Blender-canonical cargo shell during the interior-feature merge
//   (TODO.md §1.1.1.0a).  Port rod axis hull (X=-117.6, Z=5.11); stbd rod axis
//   hull (X=-222.5, Z=5.22); rod span hull Y +2..+108.  This legacy module is
//   retained only so the legacy SCAD still renders until the full door-bay
//   subsystem (door_bay_cut / servo pads / latch lips) is reframed to hull
//   frame and merged; it is NO LONGER the source of the as-built retention
//   blocks.  Do not re-derive retention geometry from HINGE_Y/HINGE_Z.
//
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
// All loads computed at 3g manoeuvre envelope.  FOS target ≥ 4.0: design-team
// judgment value for FDM composite joints with non-linear failure modes.  Design
// reference: ASTM F2910-14 [ASTM F38] sUAS design specification.
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
// Servo: SPT5425LV class (was DS3218MG); rated 26 kgf·cm at 6 V = 2.55 N·m
//   (REFERENCES.md REF-SENSOR-013, 2026-08-02 servo fleet standardisation —
//   up slightly from DS3218MG's 2.45 N·m minimum-spec figure, re-checked below).
// Mount bolt pattern: 4× M3 heat-set inserts at ±NSVMT_HOLE_S_X = ±17.5 mm in Y
//   (was "in X" — re-labelled 2026-06-22 when the mount block's mirror axis
//   moved from Z to X; the moment-arm distance itself is unchanged).
//   Moment arm between bolt-pair couple: 2 × 17.5 = 35.0 mm = 0.035 m
//   Bolt-pair load at servo stall: F_pair = τ_servo / moment_arm
//     = 2.55 / 0.035 = 72.9 N → 36.4 N per individual bolt
//   M3 insert pullout in CF-PETG: P_out ≈ 400 N (Ruthex RX-M3x5.7; ISO 14589)
//   FOS_bolt = 400 / 36.4 = 11.0  ✓  (>> 4.0 target)
//
// Nacelle pushrod dynamic load (at sector gear radius, stall transient):
//   F_pushrod = τ_servo / r_sector = 2.55 / 0.022 = 115.9 N
//   Carried in pushrod axially (tension/compression).  Does NOT load mount block.
//
// References:
//   Selig & Guglielmo (1997) J. Aircraft 34(1):72–79 (S1223 CL data).
  //   ASTM F2910-14 [ASTM F38]; FOS_min = 4.0 design judgment for FDM composite joints.
//   REFERENCES.md REF-SENSOR-013 (SPT5425LV); Ruthex RX-M3x5.7; ISO 14589 (heat-set inserts).
//   wings_s1223_revo.scad SPAR_BORE_X, WING_ROOT_TAB_*, WING_CHORD_ROOT.
//   nacelle_sector_gear.scad SLOT_BC_R = 18 mm; nacelle_pod_50mm_tandem.scad.
//   PHASED_BUILD_GUIDE.md Phase 3 tilt servo installation.
// ─────────────────────────────────────────────────────────────────────────────

// Wing root mortise dimensions (must match wings_s1223_revo.scad WING_ROOT_TAB_*)
//   The fuselage_root_tab() protrusion in the wing SCAD inserts into these slots.
//   VERIFY all *_TAB_* values against wing STL in slicer before printing.
WING_ROOT_X_CEN    = CX;            // mm, mortise X centre = 50% chord = cargo CX
WING_ROOT_Y_CEN    = CY + 40.0;     // mm, mortise Y centre = -288.63 mm (dorsal of centroid)
WING_ROOT_TAB_W    =  30.0;         // mm, tab width  (X)  — VERIFY in wings_s1223_revo.scad
WING_ROOT_TAB_H    =  20.0;         // mm, tab height (Y)  — VERIFY in wings_s1223_revo.scad
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
//   Ref: wings_s1223_revo.scad SPAR_BORE_X = 0.30, SPAR_BORE_Y_CTR = 0.
// SUPERSEDED 2026-06-22 (see CARGO_X_WALL_*/WING_ROOT_Z_CEN below): this was
// the chordwise position of the spar (30% chord from LE, via a 161 mm-chord
// calc above) plugged into the X slot of a Z-extruded cut — i.e. it carried
// the wing's own internal "X = chordwise" convention (wings_s1223_revo.scad
// line 85) straight into this file without applying that file's own
// X<-Z, Y<-X, Z<-Y permutation to hull-aligned axes before use.  The
// corrected geometry below uses WING_ROOT_Y_CEN (chordwise -> hull Y) as an
// interim stand-in for the spar's chordwise offset from the mortise centre;
// re-deriving the true offset against the current 129 mm Rev R1 root chord
// is tracked separately (TODO.md §1.1.2 wing-root-mortise items) and this
// constant is kept only for that future derivation's reference history.
WING_SPAR_X_CEN    =  -70.0;        // mm, NOT USED below — see note above
WING_SPAR_BORE_D   =   12.3;        // mm, bore ID = CF-TUBE-12MM OD + 0.3 mm slip
WING_SPAR_BOSS_OD  =   22.0;        // mm, bearing boss OD: gives (22-12.3)/2 = 4.85 mm wall
SPAR_BOSS_H        =   10.0;        // mm, boss protrusion inward from interior lateral (X) wall face
SPAR_GRUB_TAP_D    =    2.5;        // mm, M3 tap-drill dia for spar retention grub screw

// ── Lateral (X) wall positions + fixed root height for wing attachment ───────
// FIXED 2026-06-22 (TODO.md §1.1.3.3 cargo-shell port/stbd mirroring bug):
// wing_root_mortise()/wing_spar_bore()/spar_bearing_block()/
// nacelle_servo_mount_block() used to mirror "port wall" vs "stbd wall"
// across Z (DZ=163.2 vs 0) — but this file's own header (CZ comment above,
// and the validated Rev R1 bake transform: hull_Z = local_Z) establishes Z
// as the VERTICAL/dorsal axis throughout.  Port/stbd is a LATERAL
// distinction per CLAUDE.md hull frame (X = +port) and per CLAUDE.md's own
// note that wings "span outboard in +-X from [their] root at the cargo
// section's lateral walls."  Root cause: this subsystem was modelled using
// the WING's own internal pre-permutation convention (wings_s1223_revo.scad:
// "X: chordwise, Y: thickness, Z: spanwise") without ever applying that
// file's own X<-Z, Y<-X, Z<-Y permutation step before use here — i.e. an
// un-translated foreign coordinate system, exactly the case CLAUDE.md's
// hull-frame standard exists to prevent.
//
// Wall positions: this file's measured STL bounding box local X = -7.4 ..
// -201.5 (line ~225 above).  Mapped through this file's own validated bake
// transform (hull_X = -local_X - 274.4, Rev R1 header above):
//   local_X =   -7.4  -> hull_X = -267.0  (most-negative  -> STBD)
//   local_X = -201.5  -> hull_X =  -72.9  (least-negative -> PORT)
CARGO_X_WALL_STBD = -7.4;     // mm, local-X exterior face mapping to hull STBD
CARGO_X_WALL_PORT = -201.5;   // mm, local-X exterior face mapping to hull PORT

// Fixed vertical (Z) height for ALL wing-root features — identical for both
// sides (left-right mirror symmetry means height does not change with
// side).  Derived from CLAUDE.md's validated baked Wing_Port/Wing_Stbd
// hull-frame Z extent (+48.0..+77.0 mm — both wings, same range, since
// hull_Z = local_Z for this file too, no remap needed) at the span midpoint.
WING_ROOT_Z_CEN = 62.5;   // mm, VERIFY against final wing thickness profile at root

// Nacelle tilt servo mount block (one per Z side)
//   Target servo: SPT5425LV + LibreServo v2 (was DS3218MG) — body
//   40.5 × 20 × 40.5 mm (REFERENCES.md REF-SENSOR-013);
//   output shaft points outboard (Z direction, toward nacelle).
//   A separately-printed nacelle_servo_bracket.stl clamps the servo body to
//   this block via 4× M3×10 SHCS (one per heat-set insert).  The pad's own
//   bolt pattern (below) is independent of servo body size, so the
//   2026-08-02 servo migration required no change to this block itself.
//   Ref: REFERENCES.md REF-SENSOR-013 (SPT5425LV); PHASED_BUILD_GUIDE.md
//   Phase 3; load analysis above.
// NSVMT_Z_OFFSET placement constraint — RE-DERIVED 2026-06-22 (was
// NSVMT_X_CEN; see CARGO_X_WALL_*/WING_ROOT_Z_CEN comment above for why X is
// no longer a free placement axis for this pad).  Old logic offset the pad
// along the (mislabeled) chordwise axis to clear the wing mortise and spar
// boss; the analogous corrected axis is Z (vertical), since the mortise and
// spar boss are now both centred at WING_ROOT_Z_CEN.
//
// *** NEW CONFLICT FOUND, NOT RESOLVED (flag for user review, TODO.md
// §1.1.3.3): WING_ROOT_Z_CEN = 62.5 mm sits INSIDE River's avionics bay Z
// range (24..64 mm, see INARA_Z_CEN/RIVER_Z_CEN below) — the wing spar boss
// alone (Z 51.5..73.5) already overlaps River's upper 51.5..64 mm band.
// This conflict is independent of the axis-mirroring bug fixed here; it is
// surfaced BY the fix (the old, wrong Z-mirrored code happened to place the
// wing hardware at the Z extremes, nowhere near River's bay, so the
// conflict was masked).  The placement below clears the wing mortise/spar
// boss by the same 4 mm margin the original code used, but does NOT yet
// check or resolve the River-bay overlap — needs a structural/packaging
// decision (move River's bay? confirm the wing spar's actual swept volume
// doesn't reach the Faraday tray?) before this pad position is final.
NSVMT_Z_OFFSET     =   30.5;        // mm, +Z offset from WING_ROOT_Z_CEN (spar boss
                                     //   half-OD 11.0 + 4.0 mm margin + pad half-span 15.0)
NSVMT_Y_CEN        = CY + 40.0;     // mm, block Y centre — same station as wing root Y
NSVMT_PAD_W        =   52.0;        // mm, block Y span (40 mm body + 6 mm margin each side)
NSVMT_PAD_H        =   30.0;        // mm, block Z span (20 mm body + 5 mm lug + 2.5 mm/side)
NSVMT_PAD_T        =    8.0;        // mm, block protrusion in X from interior lateral wall face
NSVMT_HOLE_S_X     =   17.5;        // mm, M3 insert ±Y offset from block centre (lug spacing/2)
NSVMT_HOLE_S_Y     =    8.0;        // mm, M3 insert ±Z offset from block centre (lug width/2)
NSVMT_M3_OD        =    4.1;        // mm, M3 heat-set bore (Ruthex RX-M3x5.7: 4.0 + 0.1 press)
NSVMT_M3_DEP       =    6.0;        // mm, M3 insert pocket depth (>= insert length 5.7 mm)
NSVMT_CONDUIT_W    =   10.0;        // mm, servo lead conduit slot width (X)
NSVMT_CONDUIT_H    =    6.0;        // mm, servo lead conduit slot height (Y)

// ── Cape PCB dimensions (Rev S4 — verified from CAPE-B-2.kicad_pcb Edge.Cuts) ──
//   Both Cape-B-2 (XO) and Cape-A-2 (Pilot) share the 55×35 mm PB2-I footprint.
//   Ref: CAPE-B-2.kicad_pcb X=121..176 mm (55 mm), Y=87.5..122.5 mm (35 mm).
//   MH1–MH4: 2.7 mm drill (M2.5 nylon standoffs inside tray) at ±24.5×±14.5 mm
//   from board centre.  Title block: "55x35mm 4L JLCPCB assembled".
CAPE_PCB_X     =  55.0;   // mm, Cape-B-2 / Cape-A-2 PCB X extent
CAPE_PCB_Z     =  35.0;   // mm, Cape-B-2 / Cape-A-2 PCB Z extent
CAPE_HOLE_DX   =  24.5;   // mm, ±X M2.5 corner hole offset from board centre
CAPE_HOLE_DZ   =  14.5;   // mm, ±Z M2.5 corner hole offset from board centre

// ── Avionics bay dorsal mounts — Inara (port) and River (stbd) (Rev S4) ──────
//
// CAPE STACK GEOMETRY (Rev Q -2 EMI-hardened capes per CLAUDE.md Rev Q):
//   Cape-B-2 (XO):  55×35 mm PCB; M2.5 corner holes at ±24.5×±14.5 mm.
//   Cape-A-2 (Pilot): 55×35 mm PCB; M2.5 corner holes at ±24.5×±14.5 mm.
//   Architecture: hull M3 bosses → Faraday tray body.
//                 M2.5 nylon standoffs inside tray → PCB corners.
//   Cape-B-2 ↔ dorsal tray floor: 6 mm standoff + 1.6 mm PCB.
//   PocketBeagle 2 Industrial SOM: 5 mm height above PCB surface.
//   Inter-cape standoff: 20 mm.  Cape-A-2 + PB2-I: 1.6 + 5 mm.
//   Stack height: 6 + 1.6 + 5 + 20 + 1.6 + 5 = 39.2 mm total.
//   Cape long axis oriented in X (longitudinal) to align with gondola X span.
//
// BAY POSITIONS (both in dorsal band Y_int ≈ -213 mm = interior dorsal face):
//   Inara bay — port half, Z_CEN = 119 mm, Faraday tray Z = 99..139 mm.
//     GPS_PORT (Z=104.7 mm) co-located; 5.7 mm inset from tray lower edge ✓.
//   River bay — stbd half, Z_CEN = 44 mm,  Faraday tray Z = 24..64 mm.
//     GPS_STBD (Z=44.7 mm) co-located; 0.7 mm from tray Z centre ✓.
//   Inter-bay gap (Inara lower 99 mm − River upper 64 mm): 35 mm — conduit run.
//
// STANDOFF BOSS PATTERN (4 bosses per bay — for Faraday tray body mounting):
//   ±AVINICS_BOSS_DX (±25 mm) in X and ±AVINICS_BOSS_DZ (±15 mm) in Z.
//   Boss BOSS_H = 6 mm.  Bore: Ruthex RX-M3x5.7.  Cape PCBs mount on M2.5
//   internal standoffs INSIDE the Faraday tray; hull bosses anchor tray body only.
//   Bosses protrude in −Y (downward into interior) from interior dorsal face.
//   GPS Ø36 mm recess (R=18 mm): nearest boss ≥ 25.0 mm (re-verified Rev S4) ✓.
//
// DORSAL ACCESS PANEL CUTS (per bay, Rev S4):
//   62×42 mm opening (tray 60×40 mm + 1 mm insertion clearance each side).
//   Cover footprint 72×52 mm with 5 mm shoulder lip seats on hull skin around cut.
//   GPS recess overlaps panel zone; access cover gets Ø38 mm GPS clearance bore.
//   Cut applied at outer difference level, same as wing_root_mortise.
//
// DORSAL FACE Z (Rev R2, 2026-07-03 — CORRECTED, see NADIR_ROT/DORSAL_ROT
//   header note above for the root-cause of the fix):
//   Gondola dorsal exterior skin at DORSAL_Z_EXT = 163.2 mm (measured from
//   the canonical mesh, see above) -- this replaces the legacy
//   "AVINICS_DORSAL_Y = CY + 116" value, which placed the tray/boss features
//   in the wrong (longitudinal) axis entirely.
//   Bay separation is now lateral (X), confirmed by user decision 2026-07-03:
//   Inara (port) / River (stbd) are a port/stbd PAIR at a shared
//   longitudinal station, matching their names and the GPS_PORT/GPS_STBD
//   antenna-diversity co-location.  Original numeric intent (35 mm inter-bay
//   gap, tray 60x40 mm footprint, 25/15 mm corner boss offsets) is preserved
//   -- only the axis each number is APPLIED to has changed:
//     legacy "X"-named quantities (the tray's declared "long axis... in X")
//       -> now the real longitudinal (Y) footprint dimension
//     legacy "Z"-named quantities (used to differentiate Inara/River bays)
//       -> now the real lateral (X) separation-axis dimension
//   Ref: CAPE-B-2.kicad_pcb pad MH1–MH4; GPS_PORT/STBD co-location analysis;
//   Ruthex RX-M3x5.7 pullout spec; CLAUDE.md standoff and 2-wall requirements.
AVIONICS_BOSS_ROT  = [0, 0, 0];    // no rotation -- see DORSAL_ROT note above
BAY_GAP            =  35.0;        // mm, edge-to-edge gap between Inara/River trays (unchanged intent)

// Faraday enclosure external envelope, fan, and ductwork specification (Rev S4;
// axis roles corrected Rev R2 -- see header note above.  Original "X"/"Z" tray
// dimension names are kept as-is below but their real-world roles are now
// longitudinal (Y) / lateral (X) respectively, matching how the Rev S4 numbers
// were actually derived (60 mm = "long axis... in X" = the real longitudinal
// footprint; 40 mm = the bay-separation-axis footprint = real lateral X).
//   Each avionics bay (Inara port, River stbd) is enclosed in a 5-walled
//   aluminium-sheet Faraday tray.  The hull dorsal skin IS the 6th wall.
//   The access panel cover (72×52 mm, copper-foil-lined PETG or 0.5 mm Al sheet)
//   completes the EMI shield when installed.
//   Tray body inserts through AVINICS_PANEL_X × AVINICS_PANEL_Y dorsal opening.
//   Cape-B-2 (XO) and Cape-A-2 (Pilot) PCBs mount on M2.5 internal standoffs.
//   One 25×25×7 mm axial fan per tray on one tray wall; air exhausts into
//   gondola interior (no hull skin penetrations required).  Intake covered by
//   6 mm-thick waveguide-below-cutoff honeycomb panel (6 mm cell, attenuation
//   >> 100 dB at 10 GHz).  Fan/intake wall assignment is an internal Faraday-
//   tray detail, not a hull-cut feature -- not re-derived here.
//   Ref: CLAUDE.md §1.4.1 (500 W/m² design target); EMC waveguide cutoff theory.
FARADAY_ENC_X      =  40.0;   // mm, tray external footprint, lateral (X, bay-separation) axis (Rev S4: was 95, mislabelled "Z")
FARADAY_ENC_Z      =  60.0;   // mm, tray external footprint, longitudinal (Y) axis (Rev S4: was 65, mislabelled "X"; name kept for cross-reference continuity)
FARADAY_ENC_Y      =  55.0;   // mm, tray depth below dorsal face (Rev S4: was 65)
                               //   = 39.2 mm stack + 5 mm clearance + 7 mm fan + 1.5 mm floor
FARADAY_WALL       =   1.5;   // mm, tray wall (0.5 mm Al + PETG liner ≤ 1.5 mm)
FARADAY_FAN_D      =  25.0;   // mm, axial fan diameter (25×25×7 mm)
BAY_SEP_X          = FARADAY_ENC_X + BAY_GAP;   // = 75 mm centre-to-centre (same as legacy 119-44=75)
INARA_X_CEN        = CX - BAY_SEP_X / 2;   // mm, Inara bay X centre -- port half (more-negative local X)
RIVER_X_CEN        = CX + BAY_SEP_X / 2;   // mm, River bay X centre -- stbd half (less-negative local X)
AVIONICS_STATION_Y = GPS_STATION_Y;         // mm, shared longitudinal station, co-located with GPS
AVINICS_BOSS_DY    =  25.0;        // mm, ±Y (longitudinal) Faraday tray corner boss offset (Rev S4: was 42, mislabelled "X")
AVINICS_BOSS_DX    =  15.0;        // mm, ±X (lateral) Faraday tray corner boss offset (Rev S4: was 27, mislabelled "Z")
AVINICS_PANEL_Y    =  62.0;        // mm, dorsal access panel opening, longitudinal (Rev S4: was 95, mislabelled "X")
AVINICS_PANEL_X    =  42.0;        // mm, dorsal access panel opening, lateral (Rev S4: was 65, mislabelled "Z")
FARADAY_MOUNT_DX   = AVINICS_BOSS_DX;   // mm, ±X tray corner M3 boss offset (= 15.0 mm)
FARADAY_MOUNT_DY   = AVINICS_BOSS_DY;   // mm, ±Y tray corner M3 boss offset (= 25.0 mm)

// Ductwork parameters — Faraday tray ventilation (Rev S4, all bays).  Internal
// circulation only; no hull skin penetrations required.  Fan/intake wall
// assignment is an internal tray-hardware detail, unaffected by the hull-axis
// fix above.
//   Attenuation ≈ 27×(DUCT_EMC_T/DUCT_CELL_D) dB — at 6/6 mm: ≥ 27 dB per panel.
DUCT_INTAKE_W   =  22.0;   // mm, intake slot width (≤ fan 25 mm)
DUCT_INTAKE_H   =  22.0;   // mm, intake slot height
DUCT_EXHAUST_W  =  24.0;   // mm, exhaust slot width (behind fan)
DUCT_EXHAUST_H  =  24.0;   // mm, exhaust slot height
DUCT_EMC_T      =   6.0;   // mm, honeycomb waveguide panel thickness
DUCT_CELL_D     =   6.0;   // mm, honeycomb cell diameter (λ/2 cutoff > 25 GHz)
DUCT_GROOVE_W   =  26.0;   // mm, conduit relief groove width (Y) in interior dorsal face
DUCT_GROOVE_D   =   5.0;   // mm, conduit relief groove depth (−Z from interior face)
DUCT_GROOVE_X   = INARA_X_CEN + AVINICS_BOSS_DX + 4.0; // mm, groove X start (just outboard of Inara boss)

// ----------------------------------------------------------------------------
// Module: wing_root_mortise
//   Rectangular slot cut through one LATERAL (X) wall to receive the wing
//   root tenon.  side = +1: port wall (CARGO_X_WALL_PORT); side = -1: stbd
//   wall (CARGO_X_WALL_STBD).  FIXED 2026-06-22 — was mirrored across Z
//   (vertical); see CARGO_X_WALL_*/WING_ROOT_Z_CEN comment above for why.
//   Cut depth = WALL_MM + WING_ROOT_TAB_L + 1 mm cutter overshoot, now along X.
//   WING_MORT_CLR = 0.4 mm/side added per CLAUDE.md positive-stop slip-fit req.
//   VERIFY mortise position vs slicer cross-section before printing.
//   Ref: wings_s1223_revo.scad fuselage_root_tab(); CLAUDE.md §Fabrication.
// ----------------------------------------------------------------------------
module wing_root_mortise(side) {
    cut_depth = WALL_MM + WING_ROOT_TAB_L + 1.0;
    x_lo = (side > 0) ? CARGO_X_WALL_PORT : (CARGO_X_WALL_STBD - cut_depth);

    translate([x_lo,
               WING_ROOT_Y_CEN - MORT_W / 2,
               WING_ROOT_Z_CEN - MORT_H / 2])
    cube([cut_depth, MORT_W, MORT_H]);
}

// ----------------------------------------------------------------------------
// Module: wing_spar_bore
//   Full-X through-bore for the CF-TUBE-12MM wing spar (12 mm OD × 1.5 mm wall).
//   FIXED 2026-06-22 — was modelled as a Z-axis bore reaching only one wall
//   at a time (so it never actually connected the two wing roots); now runs
//   the entire gondola lateral (X) span, through BOTH walls, with 1 mm
//   overshoot each end — a single continuous spar connecting port and stbd
//   wing roots, matching how a real tip-to-tip wing spar works.
//   Y = WING_ROOT_Y_CEN (interim chordwise stand-in — see WING_SPAR_X_CEN
//   note above); Z = WING_ROOT_Z_CEN (fixed root height, both sides).
//   Applied at the outer difference level to cut through hull walls AND
//   both spar_bearing_block solids in a single boolean operation.
//   Ref: wings_s1223_revo.scad spar_bore(); CF-TUBE-12MM per bom_revO.csv.
// ----------------------------------------------------------------------------
module wing_spar_bore() {
    x_lo = CARGO_X_WALL_PORT - 1.0;   // 1 mm overshoot past port exterior face
    x_hi = CARGO_X_WALL_STBD + 1.0;   // 1 mm overshoot past stbd exterior face

    translate([x_lo, WING_ROOT_Y_CEN, WING_ROOT_Z_CEN])
    rotate([0, 90, 0])
    cylinder(h = x_hi - x_lo, d = WING_SPAR_BORE_D);
}

// ----------------------------------------------------------------------------
// Module: spar_bearing_block
//   Solid annular boss on the interior LATERAL (X) wall, co-axial with the
//   wing spar.  Provides the load-transfer annulus between the CF spar and
//   the gondola hull.  Boss OD = 22 mm; the spar bore is removed by
//   wing_spar_bore() at the outer difference level (not inside this module)
//   to guarantee a single clean cut.  A single M3 grub-screw tap hole from
//   the +Y face retains the spar against axial (X-direction) walking;
//   matches hinge_pin_block retention pattern.
//
//   FIXED 2026-06-22 — was mirrored across Z; see CARGO_X_WALL_*/
//   WING_ROOT_Z_CEN comment above.
//   side = +1: port wall (boss protrudes inward (+X) from interior face at
//               CARGO_X_WALL_PORT + WALL_MM)
//   side = -1: stbd wall (boss protrudes inward (-X) from interior face at
//               CARGO_X_WALL_STBD - WALL_MM)
//
//   Annular contact area = π/4×(22²−12.3²) = 260.8 mm² → σ = 0.073 MPa at 3g tip load.
//   FOS_bearing = 685 (CF-PETG compressive yield ≈ 50 MPa).  See analysis above.
//   Ref: load analysis above; CLAUDE.md min 2-wall contact annulus (4.85 mm >> 2×0.6 mm).
// ----------------------------------------------------------------------------
module spar_bearing_block(side) {
    x_int_face = (side > 0) ? (CARGO_X_WALL_PORT + WALL_MM) : (CARGO_X_WALL_STBD - WALL_MM);
    x_blk_lo   = (side > 0) ? x_int_face : (x_int_face - SPAR_BOSS_H);
    x_blk_cen  = x_blk_lo + SPAR_BOSS_H / 2;

    difference() {
        // Boss cylinder: 22 mm OD × 10 mm tall, axis along X; spar bore
        // removed externally.
        translate([x_blk_lo, WING_ROOT_Y_CEN, WING_ROOT_Z_CEN])
        rotate([0, 90, 0])
        cylinder(h = SPAR_BOSS_H, d = WING_SPAR_BOSS_OD);

        // M3 grub-screw tap bore from +Y face, centred on spar axis.
        //   Retains CF-TUBE-12MM against X (lateral) walking.
        //   Grub screw: DIN 913 M3×4 (tightened after spar insertion).
        translate([x_blk_cen,
                   WING_ROOT_Y_CEN + WING_SPAR_BOSS_OD / 2,
                   WING_ROOT_Z_CEN])
        rotate([-90, 0, 0])   // bore axis toward spar centre from +Y exterior
        cylinder(h = SPAR_BOSS_H / 2 + 0.5, d = SPAR_GRUB_TAP_D);
    }
}

// ----------------------------------------------------------------------------
// Module: nacelle_servo_mount_block
//   Solid rectangular mounting pad on the interior LATERAL (X) wall for the
//   nacelle tilt servo (SPT5425LV + LibreServo v2, was DS3218MG:
//   40.5 × 20 × 40.5 mm body, ±17.5 mm lug spacing — REFERENCES.md
//   REF-SENSOR-013).  Bolt pattern is independent of body size, so this pad's
//   own geometry is unchanged by the 2026-08-02 servo migration.  Provides:
//     • Flat inboard face for servo body seating (normal to X axis)
//     • 4× M3 heat-set insert pockets (±17.5 mm × ±8 mm pattern)
//     • 10 × 6 mm lead conduit slot through inboard face for servo wiring
//   Servo output shaft points outboard (toward nacelle in X/lateral direction).
//   A separately-printed nacelle_servo_bracket.stl (to be generated) clamps
//   the servo body to this pad via 4× M3×10 SHCS.
//
//   FIXED 2026-06-22 — was mirrored across Z; see CARGO_X_WALL_*/
//   WING_ROOT_Z_CEN comment above.  The pad's old X-span (W=52 mm, with the
//   ±17.5 mm lug-hole spacing) carried the wing subsystem's un-permuted
//   "X=chordwise" convention and is now the Z-span instead (no chord
//   relationship for a servo pad — it is simply the pad's other in-plane
//   dimension); the old Y-span (H=30 mm, ±8 mm spacing) is unchanged, since
//   NSVMT_Y_CEN was always a legitimate hull-Y (longitudinal station) value.
//
//   side = +1: port wall  (pad protrudes inward +X, shaft toward port nacelle)
//   side = -1: stbd wall  (pad protrudes inward -X, shaft toward stbd nacelle)
//
//   Servo stall torque reaction: 4× M3 inserts at 35 mm couple arm → 36.4 N/bolt.
//   FOS_bolt = 400 / 36.4 = 11.0.  See load analysis above.
//   Ref: REFERENCES.md REF-SENSOR-013 (SPT5425LV); PHASED_BUILD_GUIDE.md Phase 3 tilt servo install.
// ----------------------------------------------------------------------------
module nacelle_servo_mount_block(side) {
    z_cen = WING_ROOT_Z_CEN + NSVMT_Z_OFFSET;   // see NSVMT_Z_OFFSET note above —
                                                  // UNRESOLVED River-bay overlap risk

    // x_int_face: interior face of lateral X wall (inset WALL_MM from exterior)
    x_int_face = (side > 0) ? (CARGO_X_WALL_PORT + WALL_MM) : (CARGO_X_WALL_STBD - WALL_MM);
    // Block origin in X: port protrudes inward (+X), stbd protrudes inward (-X)
    x_blk_lo   = (side > 0) ? x_int_face : (x_int_face - NSVMT_PAD_T);
    // M3 bores drilled from the inboard (interior-facing) face of the pad.
    //   Port: inboard face is at x_blk_lo+NSVMT_PAD_T → bores start NSVMT_M3_DEP before it.
    //   Stbd: inboard face is at x_blk_lo  → bores start there, go in +X.
    x_bore_lo  = (side > 0)
        ? (x_blk_lo + NSVMT_PAD_T - NSVMT_M3_DEP)
        : x_blk_lo;

    difference() {
        // Mounting pad solid — footprint now in the Y-Z plane, depth along X.
        translate([x_blk_lo,
                   NSVMT_Y_CEN - NSVMT_PAD_W / 2,
                   z_cen - NSVMT_PAD_H / 2])
        cube([NSVMT_PAD_T, NSVMT_PAD_W, NSVMT_PAD_H]);

        // 4× M3 heat-set insert pockets bored from inboard face into pad,
        // bore axis along X.
        //   ±NSVMT_HOLE_S_X (±17.5 mm) in Y: matches the servo bracket's lug-hole spacing.
        //   ±NSVMT_HOLE_S_Y (±8.0 mm)  in Z: matches the servo bracket's lug width / 2.
        for (dy = [-NSVMT_HOLE_S_X, NSVMT_HOLE_S_X])
        for (dz = [-NSVMT_HOLE_S_Y, NSVMT_HOLE_S_Y])
            translate([x_bore_lo, NSVMT_Y_CEN + dy, z_cen + dz])
            rotate([0, 90, 0])
            cylinder(h = NSVMT_M3_DEP + 0.1, d = NSVMT_M3_OD);

        // Servo lead conduit slot: 10 × 6 mm through inboard half of pad.
        //   Routes servo signal + power leads from the mount face to interior.
        translate([x_bore_lo,
                   NSVMT_Y_CEN - NSVMT_CONDUIT_W / 2,
                   z_cen - NSVMT_CONDUIT_H / 2])
        cube([NSVMT_PAD_T / 2 + 0.1, NSVMT_CONDUIT_W, NSVMT_CONDUIT_H]);
    }
}

// ----------------------------------------------------------------------------
// Module: avinics_dorsal_boss
//   Single M3 heat-set insert boss post on the interior dorsal face, protruding
//   in −Z (downward into gondola interior).  Provides one corner standoff anchor
//   for Cape-B avionics PCB (one call per corner of each bay, 4 per bay).
//   Rev R2 (2026-07-03): corrected to use the real dorsal (Z) axis for depth
//   and the real (X,Y) plane for in-panel position -- see header note above.
//   Reuses m3_boss() with AVIONICS_BOSS_ROT = [0,0,0] (no rotation needed).
//   Boss geometry: BOSS_OD = 8 mm, BOSS_H = 6 mm, bore BOSS_BORE_D = 4.1 mm.
//   Boss base fused to interior dorsal face at DORSAL_Z_EXT; extends to
//   DORSAL_Z_EXT − BOSS_H into gondola interior.
//   VERIFY each boss clears GPS recess (Ø36 mm, R=18 mm) and GPS M2 holes in slicer.
//   Ref: Ruthex RX-M3x5.7; Cape-B-2 90×60 mm PCB corner hole pattern; CLAUDE.md.
// ----------------------------------------------------------------------------
module avinics_dorsal_boss(x_pos, y_pos) {
    m3_boss([x_pos, y_pos, DORSAL_Z_EXT], AVIONICS_BOSS_ROT);
}

// ----------------------------------------------------------------------------
// Module: avinics_dorsal_panel_cut
//   Rectangular through-cut (62×42 mm, Rev S4) in the dorsal skin for avionics
//   bay access and Faraday tray insertion.
//   Rev R2 (2026-07-03): corrected to real (X,Y) in-panel plane / Z depth --
//   see header note above.
//   Faraday tray body (FARADAY_ENC_X × FARADAY_ENC_Z = 40×60 mm, lateral x
//   longitudinal) inserts through this opening from outside with 1 mm assembly
//   clearance each side; tray screws to AVINICS_BOSS_* posts below.
//   Cover (72×52 mm) overlaps the cut perimeter by 5 mm on all sides for a
//   positive-stop EMI-seal shoulder; secured by 4× M2 screws or spring clips.
//
//   Cut Z span: DORSAL_Z_EXT − WALL_MM − 1.0 to DORSAL_Z_EXT + 1.0
//     = through interior skin (−1 mm overshoot) to past exterior face (+1 mm).
//
//   x_cen, y_cen: panel centre in X (lateral) and Y (longitudinal).
//
//   GPS recess (Ø36 mm) overlaps both panels; GPS antenna installed from outside
//   before Faraday tray and cover; access cover designed with Ø38 mm clearance bore.
//   Applied at outer difference level alongside wing_root_mortise and spar bore.
//   VERIFY opening bounds and GPS overlap in slicer before printing.
//   Ref: FARADAY_ENC_* parameters (Rev S3); GPS co-location analysis 2026-06-08;
//   CLAUDE.md positive-stop shoulder requirement for flight-critical joints.
// ----------------------------------------------------------------------------
module avinics_dorsal_panel_cut(x_cen, y_cen) {
    translate([x_cen - AVINICS_PANEL_X / 2,
               y_cen - AVINICS_PANEL_Y / 2,
               DORSAL_Z_EXT - WALL_MM - 1.0])
    cube([AVINICS_PANEL_X, AVINICS_PANEL_Y, WALL_MM + 2.0]);
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
// ── CSG tree overview (Rev S4) ────────────────────────────────────────────────
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
//   │  │  ├─ avinics_dorsal_boss ×8 ← Inara (port) + River (stbd) Faraday tray mounts (S4)
//   │  │  └─   (4 bosses per bay, ±25 mm X × ±15 mm Z from bay Z centre)
//   │  ├─ door_bay_cut              ← removes belly skin + hinge clearance
//   │  ├─ wing_root_mortise ×2      ← port + stbd tenon slots (S1)
//   │  ├─ wing_spar_bore            ← 12.3 mm full-Z spar bore (S1)
//   │  ├─ avinics_dorsal_panel_cut  ← Inara bay 62×42 mm dorsal opening (S4)
//   │  └─ avinics_dorsal_panel_cut  ← River bay 62×42 mm dorsal opening (S4)
//   └─ latch_catch_lip ×4          ← added AFTER cut; protrude into bay opening

union() {

    // ── A. Inner structure minus door opening ─────────────────────────────────
    difference() {

        union() {
            // A1. Shell with existing sensor/GPS aperture cuts.
            difference() {
                // 2.0 mm foam-fill cargo gondola shell (manifold for CGAL ops)
                import("../../../stls/fuselage/cargo/cargo_sect_shell24_repaired.stl");

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

            // A5. Hinge-pin mount blocks  *** SUPERSEDED — Rev R1c ***
            //     These legacy-frame blocks (single lateral hinge) are NOT the
            //     as-built retention geometry.  The correct hull-frame blocks
            //     are generated by generate_cargo_hinge_retention.py
            //     (cargo_hinge_retention.stl) and merged into the Blender
            //     canonical shell.  Calls retained only so the legacy SCAD
            //     still renders until the door-bay subsystem is reframed.
            //     See hinge_pin_block() header and TODO.md §1.1.0 / §1.1.1.0a.
            hinge_pin_block(DOOR_BAY_AFT - PIN_BLOCK_L);   // legacy: X = -165..-155
            hinge_pin_block(DOOR_BAY_FWD);                  // legacy: X =  -49..-39

            // A6. Servo mounting pads for door-actuator SG90 servos.
            //     Both pads AFT of door bay (X_CEN = -182 mm); outside cut zone.
            //     Port-door servo: pad centred at (SERVO_X_CEN, SERVO_PORT_Z).
            //     Stbd-door servo: pad centred at (SERVO_X_CEN, SERVO_STBD_Z).
            //     cargo_door_servo_bracket.stl bolts to each pad via 4x M2.5.
            //     VERIFY pad footprint clears interior ribs and foam-fill zone.
            servo_mount_pad(SERVO_X_CEN, SERVO_PORT_Z);   // port-door servo
            servo_mount_pad(SERVO_X_CEN, SERVO_STBD_Z);   // stbd-door servo

            // A7. Wing spar bearing blocks at port and stbd interior LATERAL
            //     (X) walls.  FIXED 2026-06-22 — was mirrored across Z; see
            //     CARGO_X_WALL_*/WING_ROOT_Z_CEN comment above.
            //     Each block: 22 mm OD boss × 10 mm tall, with M3 grub-screw tap.
            //     Boss OD = 22 mm; wall annulus = 4.85 mm (>> 2-perimeter min).
            //     Spar bore (wing_spar_bore) is applied at the outer difference
            //     level so it cuts cleanly through both bosses and hull walls.
            //     Port boss: protrudes inward (+X) from interior face at
            //       CARGO_X_WALL_PORT + WALL_MM, fixed Z = WING_ROOT_Z_CEN.
            //     Stbd boss: protrudes inward (−X) from interior face at
            //       CARGO_X_WALL_STBD − WALL_MM, fixed Z = WING_ROOT_Z_CEN.
            //     VERIFY boss X-range and Y/Z position in slicer before printing.
            //     Ref: load analysis above; CF-TUBE-12MM per bom_revO.csv.
            spar_bearing_block(+1);    // port wall
            spar_bearing_block(-1);    // stbd wall

            // A8. Nacelle tilt servo mount blocks at port and stbd interior
            //     LATERAL (X) walls.  FIXED 2026-06-22 — was mirrored across
            //     Z; see CARGO_X_WALL_*/WING_ROOT_Z_CEN comment above.
            //     Each block: 52(Y)×30(Z) mm face × 8 mm deep (X); 4× M3
            //     heat-set inserts; 10×6 mm lead conduit slot.  SPT5425LV +
            //     LibreServo v2 (was DS3218MG-class; ≥25 kgf·cm) servo mounts
            //     via separately-printed
            //     nacelle_servo_bracket.stl using 4× M3×10 SHCS through the
            //     bracket into these inserts.
            //     Block Y range: NSVMT_Y_CEN ± 26 mm = −314.6 .. −262.6 mm
            //     (above Y=−407 door cut top — not affected by door_bay_cut).
            //     Block Z range: WING_ROOT_Z_CEN + NSVMT_Z_OFFSET ± 15 mm —
            //     *** UNRESOLVED: overlaps River avionics bay, see
            //     NSVMT_Z_OFFSET note above — VERIFY/resolve before printing. ***
            //     Port block: protrudes inward (+X) from interior face.
            //     Stbd block: protrudes inward (−X) from interior face.
            //     VERIFY block footprint clears conduits in slicer before printing.
            //     Ref: DS3218MG datasheet; PHASED_BUILD_GUIDE.md Phase 3.
            nacelle_servo_mount_block(+1);  // port wall
            nacelle_servo_mount_block(-1);  // stbd wall

            // A8b. Observer vision/ToF/laser PCB mounting bosses (Rev R2, 2026-07-03).
            //      4x M3 bosses on the belly interior floor, centred on
            //      CARGO_CAM_POS's (X,Y) station.  See jayne_board_bosses() header.
            jayne_board_bosses();

            // A9. Inara's avionics bay — port half (Rev R2: X centre = CX-37.5 mm,
            //     shared longitudinal station with River and GPS).
            //     4× M3 Faraday tray anchor bosses on interior dorsal face (Z≈DORSAL_Z_EXT).
            //     Boss pattern: ±15 mm (X) × ±25 mm (Y) from bay centre.
            //     GPS_PORT co-located (same X); nearest boss ≥ 5 mm from GPS centre.
            //     Cape-B-2 (XO) / Cape-A-2 (Pilot) PCBs mount on M2.5 internal standoffs
            //     inside Faraday tray; hull bosses anchor tray body only.
            //     VERIFY boss positions and clearance in slicer before printing.
            //     Ref: Rev S4 dimension correction (Rev R2 axis fix); GPS_PORT recess
            //     R=18 mm; FARADAY_* params.
            for (dx = [-AVINICS_BOSS_DX, AVINICS_BOSS_DX])
            for (dy = [-AVINICS_BOSS_DY, AVINICS_BOSS_DY])
                avinics_dorsal_boss(INARA_X_CEN + dx, AVIONICS_STATION_Y + dy);

            // A10. River's avionics bay — stbd half (Rev R2: X centre = CX+37.5 mm,
            //      shared longitudinal station with Inara and GPS).
            //      4× M3 Faraday tray anchor bosses on interior dorsal face (Z≈DORSAL_Z_EXT).
            //      Boss pattern: ±15 mm (X) × ±25 mm (Y) from bay centre.
            //      GPS_STBD co-located (same X); nearest boss ≥ 5 mm from GPS centre.
            //      Cape-B-2 (XO) / Cape-A-2 (Pilot) PCBs mount on M2.5 internal standoffs.
            //      35 mm inter-bay gap (X) available for conduit and wiring routing.
            //      VERIFY boss positions and clearance in slicer before printing.
            //      Ref: Rev S4 dimension correction (Rev R2 axis fix); GPS_STBD recess
            //      R=18 mm; FARADAY_* params.
            for (dx = [-AVINICS_BOSS_DX, AVINICS_BOSS_DX])
            for (dy = [-AVINICS_BOSS_DY, AVINICS_BOSS_DY])
                avinics_dorsal_boss(RIVER_X_CEN + dx, AVIONICS_STATION_Y + dy);
        }

        // ── Cargo-bay door opening ────────────────────────────────────────────
        //   Subtracts from ALL inner-union geometry including ribs.
        //   Removes belly skin (X=-152..-52, full Z, Y=-416..-407).
        //   3 mm shell frame lips remain at X=-155..-152 and X=-52..-49.
        door_bay_cut();

        // ── Wing root mortises (tenon slots through LATERAL (X) walls) ───────
        //   FIXED 2026-06-22 — was cut through Z (vertical) walls at the
        //   gondola's dorsal/ventral extremes; see CARGO_X_WALL_*/
        //   WING_ROOT_Z_CEN comment above for the root cause (un-permuted
        //   wing-internal "X=chordwise" convention) and CLAUDE.md's own
        //   "wings... attach at the cargo section's lateral walls."
        //   Each slot: MORT_W(Y) × MORT_H(Z) opening (30.8 × 20.8 mm) through wall.
        //   Depth = WALL_MM + WING_ROOT_TAB_L + 1 mm overshoot = 15 mm, along X.
        //   Port slot: X = CARGO_X_WALL_PORT .. +15 mm (through port wall).
        //   Stbd slot: X = CARGO_X_WALL_STBD − 15 mm .. CARGO_X_WALL_STBD.
        //   Both centred at fixed Y = WING_ROOT_Y_CEN, Z = WING_ROOT_Z_CEN.
        //   VERIFY mortise position vs wing STL in slicer before printing.
        //   Ref: wings_s1223_revo.scad fuselage_root_tab() geometry.
        wing_root_mortise(+1);   // port wall
        wing_root_mortise(-1);   // stbd wall

        // ── Wing spar through-bore (full lateral X span) ──────────────────────
        //   FIXED 2026-06-22 — was a short Z-axis bore that never actually
        //   connected the two wing roots; now a single continuous lateral
        //   bore at (Y, Z) = (WING_ROOT_Y_CEN, WING_ROOT_Z_CEN) = (-288.6, 62.5),
        //   passing through BOTH lateral walls AND both spar_bearing_block
        //   solids — a real tip-to-tip spar passage.
        //   12.3 mm dia.  CF-TUBE-12MM (12 mm OD) slides through with
        //   0.15 mm radial clearance.  Spar retained by M3 grub screw in each
        //   bearing block after final fit.
        //   VERIFY bore Y and Z in slicer cross-section before printing; the Y
        //   value is an interim stand-in pending the chordwise-offset
        //   re-derivation tracked in TODO.md §1.1.2 (see WING_SPAR_X_CEN note
        //   above).
        //   Ref: CF-TUBE-12MM (bom_revO.csv); wings_s1223_revo.scad spar_bore().
        wing_spar_bore();

        // ── Inara avionics dorsal access panel (port, Rev R2 axis fix) ──────
        //   42×62 mm cut (lateral X × longitudinal Y) through dorsal skin at
        //   Inara bay X centre = CX-37.5 mm, shared Y station with GPS/River.
        //   Faraday tray body (FARADAY_ENC_X × FARADAY_ENC_Z = 40×60 mm) inserts
        //   through this opening from outside with 1 mm assembly clearance each side.
        //   Cover (72×52 mm, 5 mm shoulder) forms EMI-sealed lid when installed.
        //   GPS_PORT recess overlaps panel: GPS installed from outside before
        //   Faraday tray; cover has Ø38 mm clearance bore.
        //   VERIFY opening bounds and GPS overlap in slicer.
        avinics_dorsal_panel_cut(INARA_X_CEN, AVIONICS_STATION_Y);

        // ── River avionics dorsal access panel (stbd, Rev R2 axis fix) ──────
        //   42×62 mm cut through dorsal skin at River bay X centre = CX+37.5 mm,
        //   shared Y station with Inara/GPS.
        //   Same Faraday tray geometry and GPS co-location note as Inara panel.
        //   35 mm inter-bay gap (X) from Inara for conduit run.
        //   VERIFY opening bounds and GPS overlap in slicer.
        avinics_dorsal_panel_cut(RIVER_X_CEN, AVIONICS_STATION_Y);
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
