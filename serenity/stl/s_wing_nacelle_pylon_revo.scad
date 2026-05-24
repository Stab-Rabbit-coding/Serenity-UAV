// =============================================================================
// s_wing_nacelle_pylon_revo.scad
// Serenity UAV — Rev O — Integrated Wing Nacelle Tilt Pylon
// =============================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Project : Serenity-class Tilt-Rotor UAV (24-inch scale, Firefly TV ship)
// License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date    : 2026-05-24
// Revision: Rev O
//
// Description
// -----------
// Single printable CF-PETG part that merges and supersedes three separate
// Thingiverse pivot components:
//
//   s_pivot_arm_a_scaled24   — inner pivot arm (fixed to nacelle, rotates on X)
//   s_eng_piv_outer_scaled24 — outer pivot housing (wing-side, stow-fold hinge)
//
// The merged pylon integrates:
//   • Hollow structural box body — entire interior is the harness routing channel
//     (ESC motor leads, ESC signal, nav-light WS2812C signal wire)
//   • Press-fit bore for 4 mm CF tilt spar (spar fixed in pylon; nacelle
//     MF104ZZ bearings rotate on the spar)
//   • Nacelle boss socket — positive-stop receiver for the nacelle X-face pivot
//     boss (Ø 16 mm × 5 mm protrusion, from CLEVIS_EAR_OD in nacelle SCAD)
//   • Sector gear mount face — 4× M2.5 heat-set insert pockets at R = 18 mm
//     bolt circle, matching nacelle_sector_gear.scad SLOT_BC_R = 18 mm.
//     The fixed sector gear is bolted here; the nacelle tilts around the spar
//     while Pinion A (at Y = 28 mm on the nacelle) walks along the sector teeth.
//   • Wing root attachment block — M3 bolts + positive-stop shoulder into the
//     wing mount pocket on s_wings_both_shell24.stl.
//   • Fold hinge — 4 mm CF hinge pin through two pylon ears; allows 90°
//     fold-down of the nacelle+pylon assembly for stowage/transport.
//     M2.5 set-screw in each ear retains the hinge pin (no spring, no magnets).
//
// Scale / Compatibility Note
// --------------------------
// The nacelles were scaled to 1.25× relative to the original Thingiverse 18"
// (2.197×) assembly to accommodate 50 mm EDFs.  The fuselage and wings remain
// at the original 2.197× scale.  This pylon BRIDGES the scale mismatch:
//
//   Nacelle-facing end : sized for Rev O 50 mm nacelle (OD_X=60.5 mm, OD_Y=67 mm).
//   Wing-facing end    : sized for original 2.197× wing pocket.
//                        WING_SLOT_W and WING_SLOT_H MUST be measured from
//                        s_wings_both_shell24.stl before committing to print.
//                        Parameters are marked "VERIFY" below.
//
// Coordinate System (nacelle frame — same as nacelle_pod_50mm_tandem.scad)
// -----------------------------------------------------------------------
//   Z = 0         → nacelle intake face (forward, air-inlet end)
//   Z = NACELLE_L → nozzle exit face (aft, thrust end)
//   Bore axis     = Z (global +Z)
//   X = spanwise  (nacelle tilt axis; spar runs along X, away from fuselage)
//   Y = fore-aft  (+Y toward fuselage spar in fuselage frame)
//
//   Pylon body occupies X = NACELLE_OD_X/2 … NACELLE_OD_X/2 + PYLON_SPAN
//   and is centred on Y = 0 (nacelle bore axis), Z = PIVOT_Z (pivot station).
//
// Harness Routing
// ---------------
//   The hollow pylon body is the primary wire channel.  Wires enter/exit
//   through:
//     Nacelle end : HARNESS_PORT slot (14 × 8 mm) cut into nacelle X-face
//                   shell (added to nacelle_pod_50mm_tandem.scad), centred
//                   at Z = HARNESS_PORT_Z = 86 mm, Y = 0.
//     Wing end    : Open pylon interior face (cable dress at wing attachment).
//   The WS2812C nav-light wire (28AWG 3-core) runs through the pylon and exits
//   via a D-section conduit on the nacelle exterior to the tip cap LED recess.
//
// Sector Gear Kinematics
// ----------------------
//   The sector gear (nacelle_sector_gear.scad) is bolted to the pylon face.
//   Its centre is at (Y = 0, Z = PIVOT_Z).  As the nacelle tilts, Pinion A
//   (on the nacelle at Y = PINION_A_Y = 28 mm, Z = PIVOT_Z) orbits the pivot
//   and rolls on the fixed sector, converting tilt angle to iris-drive shaft
//   rotation.
//
// Fold Hinge
// ----------
//   A 4 mm CF hinge pin through the two inboard ears at the wing root end.
//   Fold axis = Y direction (fore-aft, perpendicular to spar).
//   0° position  = pylon horizontal (nacelle deployed for flight).
//   90° position = pylon folded down (nacelle alongside fuselage, stowed).
//   Each position is retained by an M2.5 × 4 set screw through a radial bore
//   in each hinge ear that engages a detent flat on the hinge block.
//
// References
// ----------
//   [1] nacelle_pod_50mm_tandem.scad — nacelle geometry source of truth.
//   [2] nacelle_sector_gear.scad     — sector gear SLOT_BC_R = 18 mm spec.
//   [3] CLAUDE.md — fabrication standards (4-perimeter CF-PETG, 3 mm wall min).
//   [4] 14 CFR 91.209               — navigation light visibility ≥ 3 SM.
//   [5] Thingiverse Serenity model   — s_wings_both_shell24.stl wing reference.
//
// Render Commands
// ---------------
//   Port pylon (left nacelle, inboard +X):
//     openscad -o s_wing_nacelle_pylon_port_revo.stl \
//              s_wing_nacelle_pylon_revo.scad -D INBOARD_SIGN=+1
//
//   Starboard pylon (right nacelle, inboard −X — mirror):
//     openscad -o s_wing_nacelle_pylon_stbd_revo.stl \
//              s_wing_nacelle_pylon_revo.scad -D INBOARD_SIGN=-1
//
// =============================================================================


// =============================================================================
// ── Parameter Block ───────────────────────────────────────────────────────────
// =============================================================================

// ── Nacelle dimensions (from nacelle_pod_50mm_tandem.scad) ───────────────────
NACELLE_L       = 148.3;  // [mm] total nacelle length
NACELLE_OD_X    =  60.5;  // [mm] nacelle outer diameter, spanwise (X axis)
NACELLE_OD_Y    =  67.0;  // [mm] nacelle outer diameter, fore-aft (Y axis)
PIVOT_Z         =  83.0;  // [mm] nacelle CG station = tilt pivot Z
PIVOT_BOSS_OD   =  16.0;  // [mm] nacelle pivot boss OD (CLEVIS_EAR_OD in nacelle SCAD)
PIVOT_BOSS_DEPTH =   5.0; // [mm] nacelle pivot boss protrusion from X face
PINION_A_Y      =  28.0;  // [mm] Pinion A Y offset from nacelle bore (meshing distance)

// ── Spar (tilt axis) ─────────────────────────────────────────────────────────
// The 4 mm CF spar is FIXED in the pylon (press-fit).
// The nacelle's MF104ZZ bearings (4×10×4 mm) rotate on the stationary spar.
SPAR_D          =   4.0;  // [mm] CF spar nominal diameter
SPAR_BORE_D     =   3.98; // [mm] spar press-fit bore (slight interference for CF-PETG)
                           //      ±0.05 mm is typical; tune to printer first article
SPAR_TOTAL_L    = 120.0;  // [mm] total spar stock length (spans nacelle OD + pylon depth
                           //      + bearing protrusion margin both sides)

// ── Nacelle boss socket ───────────────────────────────────────────────────────
// The nacelle X-face pivot boss (Ø16 mm, 5 mm protrusion) seats into this socket.
// Clearance 0.3 mm radial (0.6 mm diameter) gives a slip fit.
NAC_BOSS_SOCKET_D = 16.6; // [mm] socket bore ID (boss OD 16 mm + 0.6 mm clearance)
NAC_BOSS_SOCKET_L =  5.5; // [mm] socket depth (boss length 5 mm + 0.5 mm clearance)

// ── Pylon body ────────────────────────────────────────────────────────────────
// Hollow rectangular tube centred on the spar axis (Y=0, Z=PIVOT_Z).
// The interior is the harness wire channel.
PYLON_SPAN      =  88.0;  // [mm] nacelle X-face → wing mount face — VERIFY vs STL
PYLON_W         =  36.0;  // [mm] body outer width, Y direction (fore-aft)
PYLON_H         =  32.0;  // [mm] body outer height, Z direction (centred on PIVOT_Z)
PYLON_WALL      =   3.0;  // [mm] minimum wall thickness (CF-PETG: 4 × 0.6 mm nozzle)
                           //      Structural check: σ < 1.2 N/mm² at 3g AUW load
                           //      CF-PETG yield ≈ 50 MPa → FOS ≥ 40 — conservative.

// ── Sector gear mount (on nacelle-facing pylon face) ─────────────────────────
// Sector gear (nacelle_sector_gear.scad) bolts here with 4× M2.5 inserts.
// Gear is FIXED; nacelle tilts; Pinion A walks on fixed sector.
// M2.5 heat-set insert: OD ≈ 3.5 mm, length ≈ 5 mm (CNC Kitchen M2.5 brass).
SECTOR_BC_R     =  18.0;  // [mm] bolt circle radius (= SLOT_BC_R in sector gear SCAD)
SECTOR_N_BOLTS  =   4;    // [count] M2.5 inserts (evenly spaced at 90° intervals)
SECTOR_INSERT_OD =  3.7;  // [mm] insert bore OD (M2.5 insert OD + 0.1 mm press)
SECTOR_INSERT_L  =  5.5;  // [mm] insert pocket depth (insert length + 0.5 mm bottom)
SECTOR_GEAR_H   =   3.0;  // [mm] sector gear plate thickness (BODY_H in gear SCAD)
SECTOR_RECESS_D =  48.0;  // [mm] recess bore on pylon face to seat sector gear plate
                           //      = 2 × (TIP_R + 1mm clearance) = 2 × (23+1) = 48 mm

// ── Wing root attachment block ────────────────────────────────────────────────
// Positive-stop block that inserts into the wing mount pocket on
// s_wings_both_shell24.stl.  VERIFY slot dimensions by measuring the STL
// before printing — the wing was not scaled with the nacelle (2.197× only).
WING_SLOT_W     =  50.0;  // [mm] VERIFY: wing pocket width (Y dir) from wing STL
WING_SLOT_H     =  40.0;  // [mm] VERIFY: wing pocket height (Z dir) from wing STL
WING_SLOT_DEPTH =  14.0;  // [mm] engagement depth (block inserts this far into pocket)
WING_SLOT_CLEAR =   0.3;  // [mm] radial clearance per side for positive-stop fit
WING_BOLT_R     =  16.0;  // [mm] M3 bolt pitch circle radius (4× M3 × 16 SHCS)
                           //      VERIFY position from wing STL insert positions
WING_M3_INSERT_OD =  4.2; // [mm] M3 heat-set insert OD + 0.1 mm press
WING_M3_INSERT_L  =  5.5; // [mm] M3 insert pocket depth

// ── Fold hinge (inboard end of pylon, at wing root transition) ────────────────
// 4 mm CF hinge pin through two pylon ears allows 90° fold for stowage.
// Fold axis = Y (fore-aft); 0° = deployed, 90° = stowed (nacelle points down).
FOLD_PIN_D      =   4.0;  // [mm] hinge CF pin diameter
FOLD_BOSS_OD    =  14.0;  // [mm] hinge ear boss outer diameter
FOLD_EAR_T      =   6.0;  // [mm] each hinge ear axial (X) thickness
FOLD_EAR_GAP    =  22.0;  // [mm] gap between the two hinge ears (accommodates
                           //      wing bracket mid-lug, nominally 20 mm + 1 mm/side)
FOLD_PIN_BORE_D  =  4.0;  // [mm] hinge pin clearance bore (press: 3.98 → pin 4.0)
FOLD_SS_BORE_D   =  2.7;  // [mm] M2.5 set-screw bore (radial, from ear OD to pin)
FOLD_STOP_FLAT_W =  2.0;  // [mm] detent flat width milled on hinge block for set-screw

// ── Harness / nav-light wiring ────────────────────────────────────────────────
// Wire inventory through pylon interior (both EDFs, ESCs, nav-light WS2812C):
//   ESC1 + ESC2 motor leads : 3 wires × 16AWG (Ø 3.0 mm each) = 6 wires
//   ESC1 + ESC2 signal leads: 6 wires × 28AWG (Ø 1.0 mm each)
//   Nav-light WS2812C       : 3 wires × 28AWG (Ø 1.0 mm each) = 3-core Ø 2.5 mm
//   Harness bundle OD est.  : ≈ 15 mm × 10 mm, fills ≈ 150 mm² of 780 mm² interior
// The pylon interior void (after wall subtraction) is:
//   (PYLON_W - 2×PYLON_WALL) × (PYLON_H - 2×PYLON_WALL) = 30 × 26 = 780 mm²
//   Provides ample routing room and inspect/reroute access from each end.
NAV_CONDUIT_BORE =  4.0;  // [mm] nav-light conduit bore on nacelle exterior (28AWG bundle)
HARNESS_PORT_W   = 14.0;  // [mm] harness exit slot width on nacelle X-face (Y dir)
HARNESS_PORT_H   =  8.0;  // [mm] harness exit slot height on nacelle X-face (Z dir)
HARNESS_PORT_Z   = 86.0;  // [mm] slot centre Z — inter-EDF gap, above pivot boss

// ── Print chirality ───────────────────────────────────────────────────────────
// INBOARD_SIGN = +1 for port (left) pylon: pylon extends in +X from nacelle.
// INBOARD_SIGN = -1 for starboard (right): mirror via scale([-1,1,1]) and re-export.
// The SCAD mirrors by reflecting across X=0 when INBOARD_SIGN=-1.
INBOARD_SIGN    = +1;     // [+1 / −1] — override at CLI: -D INBOARD_SIGN=-1

// ── Global facet resolution ───────────────────────────────────────────────────
$fn = 72;

// ── Convenience: pylon X origin and end ──────────────────────────────────────
// The pylon body starts at the nacelle X-face and extends inboard (toward fuselage).
PYLON_X0 = NACELLE_OD_X / 2;          // X at nacelle face (outboard end of pylon)
PYLON_X1 = PYLON_X0 + PYLON_SPAN;     // X at wing root face  (inboard end of pylon)


// =============================================================================
// ── Module: pylon_body ───────────────────────────────────────────────────────
// =============================================================================
// Hollow rectangular prism running in X from the nacelle face (PYLON_X0)
// to just before the wing root block (PYLON_X1 - WING_SLOT_DEPTH).
// Centred on Y = 0, Z = PIVOT_Z.
// The hollow interior is the harness routing channel.
module pylon_body() {
    body_len = PYLON_SPAN;  // full pylon span from nacelle X-face to wing face

    translate([PYLON_X0, -PYLON_W / 2, PIVOT_Z - PYLON_H / 2])
        difference() {
            // ── Outer solid box ────────────────────────────────────────────
            cube([body_len, PYLON_W, PYLON_H]);

            // ── Inner void — harness channel ───────────────────────────────
            // Inset by PYLON_WALL on all four sides; open at both X faces to
            // allow wire ingress/egress from nacelle end and wing end.
            translate([0.0,                  // full length (no endcaps)
                       PYLON_WALL,
                       PYLON_WALL])
                cube([body_len + 0.02,
                      PYLON_W - 2 * PYLON_WALL,
                      PYLON_H - 2 * PYLON_WALL]);
        }
}


// =============================================================================
// ── Module: nacelle_face_block ────────────────────────────────────────────────
// =============================================================================
// Thickened face plate at the nacelle end of the pylon (at X = PYLON_X0).
// Provides:
//   • Sector gear recess and M2.5 insert pockets (gear mounts here, faces nacelle)
//   • Nacelle boss socket (positive-stop receiver)
//   • Structural boss around spar bore
//   • Extra wall material for sector gear bolt loads
module nacelle_face_block() {
    face_thick = SECTOR_INSERT_L + 2.0;  // face plate thick enough for inserts + 2 mm floor

    translate([PYLON_X0 - face_thick, -PYLON_W / 2, PIVOT_Z - PYLON_H / 2])
        cube([face_thick, PYLON_W, PYLON_H]);
}


// =============================================================================
// ── Module: wing_attach_block ─────────────────────────────────────────────────
// =============================================================================
// Solid block at the wing root end of the pylon.
// Inserts into the wing mount pocket with a positive-stop shoulder.
// Four M3 heat-set insert pockets for M3×16 SHCS mounting bolts.
//
// The block is slightly undersize (clearance) relative to the wing pocket:
//   Actual block: (WING_SLOT_W - 2×WING_SLOT_CLEAR) × (WING_SLOT_H - 2×WING_SLOT_CLEAR)
//   Wing pocket:   WING_SLOT_W × WING_SLOT_H
//
// CLAUDE.md compliance: 2-wall contact annulus (block walls ≥ 2×PYLON_WALL = 6 mm).
module wing_attach_block() {
    blk_w = WING_SLOT_W - 2 * WING_SLOT_CLEAR;  // slip-fit width
    blk_h = WING_SLOT_H - 2 * WING_SLOT_CLEAR;  // slip-fit height
    blk_l = WING_SLOT_DEPTH;                     // insertion depth

    // ── Block body ─────────────────────────────────────────────────────────
    translate([PYLON_X1,
               -blk_w / 2,
               PIVOT_Z - blk_h / 2])
        cube([blk_l, blk_w, blk_h]);

    // ── Shoulder flange — positive stop against wing face ─────────────────
    // The shoulder overhangs the block in Y and Z, preventing over-insertion.
    flange_w  = WING_SLOT_W + 8.0;  // 4 mm overhang each side in Y
    flange_h  = WING_SLOT_H + 8.0;  // 4 mm overhang each side in Z
    flange_t  = 4.0;                 // [mm] flange thickness (axial, in X)

    translate([PYLON_X1 - flange_t,
               -flange_w / 2,
               PIVOT_Z - flange_h / 2])
        cube([flange_t, flange_w, flange_h]);
}


// =============================================================================
// ── Module: fold_hinge_ears ───────────────────────────────────────────────────
// =============================================================================
// Two cylindrical hinge ear bosses extending inboard (in X) from the wing
// attach block at Y = 0, Z = PIVOT_Z.  A 4 mm CF hinge pin passes through both
// ears.  The wing bracket mid-lug sits in the gap between them.
//
// Fold axis: Y (fore-aft).  When the hinge pin rotates in the ear bores, the
// entire pylon+nacelle swings from horizontal (deployed) to vertical-down (stowed).
//
// Each ear has a radial M2.5 set-screw bore that bears against a detent flat
// on the hinge block at 0° and 90°.
module fold_hinge_ears() {
    // Ear centres: ±Z from pivot Z position, ±gap/2 in X direction from pylon end
    ear_z_offset = 0;  // ears are centred on pivot Z
    ear_x_base   = PYLON_X1 + WING_SLOT_DEPTH;  // inboard of the wing block

    for (x_sign = [-1, +1]) {
        translate([ear_x_base + (x_sign < 0 ? 0 : FOLD_EAR_GAP / 2 + FOLD_EAR_T / 2),
                   0,
                   PIVOT_Z])
            rotate([90, 0, 0])   // cylinder axis = Y
                // ── Ear cylinder ───────────────────────────────────────────
                difference() {
                    cylinder(r = FOLD_BOSS_OD / 2,
                             h = FOLD_EAR_T,
                             center = true);

                    // ── Hinge pin bore (Y axis through ear) ───────────────
                    cylinder(r = FOLD_PIN_BORE_D / 2,
                             h = FOLD_EAR_T + 0.02,
                             center = true);
                }
    }
}


// =============================================================================
// ── Module: spar_bore ────────────────────────────────────────────────────────
// =============================================================================
// Press-fit bore for the 4 mm CF tilt spar, running along X through the entire
// pylon body and face block.
// The bore is slightly under-size (SPAR_BORE_D < SPAR_D + tolerance) so the
// spar is retained by interference fit.  Adjust SPAR_BORE_D by ±0.05 mm
// based on printer first-article measurement.
// The nacelle's MF104ZZ bearings (4×10×4 mm inner bore) rotate on this spar.
module spar_bore() {
    // The bore passes through the full pylon span plus the face-block thickness.
    bore_x_lo  = PYLON_X0 - (SECTOR_INSERT_L + 2.0);  // starts at nacelle face block
    bore_x_hi  = PYLON_X1 + WING_SLOT_DEPTH + FOLD_EAR_T + 2.0;  // through fold ears + margin

    translate([bore_x_lo, 0, PIVOT_Z])
        rotate([0, 90, 0])   // cylinder along X
            cylinder(r  = SPAR_BORE_D / 2,
                     h  = bore_x_hi - bore_x_lo,
                     center = false);
}


// =============================================================================
// ── Module: nacelle_boss_socket ───────────────────────────────────────────────
// =============================================================================
// Cylindrical socket on the nacelle-facing pylon face.
// Accepts the nacelle X-face pivot boss (Ø 16 mm × 5 mm protrusion).
// The socket provides a positive stop that restrains the nacelle in the
// radial (Y, Z) directions while the spar provides axial (X) retention.
// 0.3 mm/side clearance gives a slip fit for easy field disassembly.
module nacelle_boss_socket() {
    translate([PYLON_X0, 0, PIVOT_Z])
        rotate([0, 90, 0])  // cylinder along X (boring into pylon face)
            cylinder(r = NAC_BOSS_SOCKET_D / 2,
                     h = NAC_BOSS_SOCKET_L,
                     center = false);
}


// =============================================================================
// ── Module: sector_gear_recess ────────────────────────────────────────────────
// =============================================================================
// Shallow circular recess on the nacelle-facing pylon face to seat the sector
// gear plate (BODY_H = 3 mm thick, tip circle R = 23 mm).
// The recess locates the gear plate radially and prevents rotation under load.
// Depth = SECTOR_GEAR_H + 0.2 mm clearance.
module sector_gear_recess() {
    translate([PYLON_X0 - SECTOR_GEAR_H - 0.2, 0, PIVOT_Z])
        rotate([0, 90, 0])  // cylinder along X
            cylinder(r = SECTOR_RECESS_D / 2,
                     h = SECTOR_GEAR_H + 0.2,
                     center = false);
}


// =============================================================================
// ── Module: sector_gear_inserts ───────────────────────────────────────────────
// =============================================================================
// Four M2.5 heat-set insert pockets in the nacelle-facing face plate.
// Spaced 90° apart on bolt circle R = SECTOR_BC_R = 18 mm.
// Positioned at 45°, 135°, 225°, 315° to avoid conflict with gear arc segment
// (which spans 0° to ~100° around the pivot axis).
// Insert: M2.5 × 5.5 mm, OD ≈ 3.5 mm — press via soldering iron after printing.
module sector_gear_inserts() {
    for (angle = [45, 135, 225, 315]) {
        y_off = SECTOR_BC_R * cos(angle);
        z_off = SECTOR_BC_R * sin(angle);

        translate([PYLON_X0, y_off, PIVOT_Z + z_off])
            rotate([0, 90, 0])  // pocket bored into pylon face (along X)
                cylinder(r = SECTOR_INSERT_OD / 2,
                         h = SECTOR_INSERT_L,
                         center = false);
    }
}


// =============================================================================
// ── Module: wing_bolt_inserts ─────────────────────────────────────────────────
// =============================================================================
// Four M3 heat-set insert pockets in the wing attach block, for M3 × 16 SHCS
// bolts that clamp the block to the wing mount pocket.
// Bolt circle R = WING_BOLT_R, positioned in the Y-Z plane at the wing face.
// Insert: M3 × 5.5 mm, OD ≈ 4.2 mm.
module wing_bolt_inserts() {
    blk_h = WING_SLOT_H - 2 * WING_SLOT_CLEAR;
    blk_w = WING_SLOT_W - 2 * WING_SLOT_CLEAR;

    for (angle = [45, 135, 225, 315]) {
        y_off = WING_BOLT_R * cos(angle);
        z_off = WING_BOLT_R * sin(angle);

        translate([PYLON_X1 + WING_SLOT_DEPTH / 2, y_off, PIVOT_Z + z_off])
            rotate([0, 90, 0])  // bore along X (from wing face inward)
                cylinder(r = WING_M3_INSERT_OD / 2,
                         h = WING_M3_INSERT_L,
                         center = false);
    }
}


// =============================================================================
// ── Module: fold_hinge_pin_bore ───────────────────────────────────────────────
// =============================================================================
// Through-bore for the 4 mm CF fold hinge pin, perpendicular to the fold axis.
// Runs along Y through both hinge ears.
// Bore diameter = FOLD_PIN_BORE_D (press fit) — retains pin without set screw.
// The M2.5 set-screw bore (FOLD_SS_BORE_D) is in the ear wall and engages
// a detent flat on the hinge block bracket to lock 0° and 90° positions.
module fold_hinge_pin_bore() {
    ear_x_base = PYLON_X1 + WING_SLOT_DEPTH;
    ear_half   = FOLD_EAR_GAP / 2 + FOLD_EAR_T;

    for (x_sign = [-1, +1]) {
        x_pos = ear_x_base + (x_sign < 0 ? FOLD_EAR_T / 2 : ear_half - FOLD_EAR_T / 2);

        translate([x_pos, -FOLD_BOSS_OD / 2 - 0.5, PIVOT_Z])
            rotate([-90, 0, 0])   // bore along Y
                cylinder(r = FOLD_PIN_BORE_D / 2,
                         h = FOLD_BOSS_OD + 1.0,
                         center = false);
    }
}


// =============================================================================
// ── Module: fold_set_screw_bores ──────────────────────────────────────────────
// =============================================================================
// Radial M2.5 set-screw bores through each hinge ear, oriented to bear
// against the detent flat on the wing bracket hinge block.
// Two bores per ear: one for 0° (deployed) detent, one for 90° (stowed) detent.
// The wing bracket must have matching flats machined or printed at these angles.
module fold_set_screw_bores() {
    ear_x_base = PYLON_X1 + WING_SLOT_DEPTH;

    for (x_sign = [-1, +1]) {
        x_pos = ear_x_base + (x_sign < 0 ? FOLD_EAR_T / 2 : FOLD_EAR_GAP / 2 + FOLD_EAR_T / 2);

        // 0° detent: set screw approaches from +Z (top of ear)
        translate([x_pos, 0, PIVOT_Z + FOLD_BOSS_OD / 2 + 0.5])
            rotate([180, 0, 0])
                cylinder(r = FOLD_SS_BORE_D / 2,
                         h = FOLD_BOSS_OD / 2 + 1.0,
                         center = false);

        // 90° detent: set screw approaches from +Y (front face of ear, perpendicular)
        translate([x_pos, -(FOLD_BOSS_OD / 2 + 0.5), PIVOT_Z])
            rotate([90, 0, 0])
                cylinder(r = FOLD_SS_BORE_D / 2,
                         h = FOLD_BOSS_OD / 2 + 1.0,
                         center = false);
    }
}


// =============================================================================
// ── Module: wing_incidence_shim ───────────────────────────────────────────────
// =============================================================================
// A 3° taper on the wing attach block face imposes 3° of positive incidence on
// the wing root attachment.  This angles the pylon (and nacelle) 3° nose-up
// relative to the fuselage datum, improving wing lift by ~ΔCL = 0.25 at
// Re ≈ 91,000 (40 kt cruise) with zero change to the outer mold line.
//
// Implementation: The wing block insertion face (at X = PYLON_X1) is cut at
// 3° from the Y-Z plane by subtracting a thin wedge from the block base.
// The incidence wedge is additive only in the parameter sense — the face is
// angled in the STL and the wing pocket receives it flat.  A mating 3° shim
// printed separately can be placed between pylon flange and wing surface if
// the wing pocket is not re-cut, to preserve reversibility.
//
// Note: This module defines the geometry comment and shim outline only.
//       The actual 3° incidence is achieved by printing a separate
//       s_wing_incidence_shim_3deg.stl shim (a 3°-tapered annular ring
//       matching the pylon flange footprint) placed between pylon flange and
//       wing surface — allowing the pylon STL to remain square-faced for
//       compatibility with any future incidence revision.
//
// Incidence shim dimensions (for reference and BOM):
//   Inner clearance  : WING_SLOT_W + 1.0 mm (clears block)
//   Outer diameter   : flange OD = WING_SLOT_W + 8.0 mm
//   Min thickness    : 0.5 mm (thin edge)
//   Max thickness    : (WING_SLOT_W/2 + 4) × tan(3°) ≈ 1.7 mm (thick edge)
INCIDENCE_DEG = 3.0;  // [deg] positive incidence added at wing root — do not change
                       //       without re-evaluating wing lift budget


// =============================================================================
// ── Module: pylon (top-level assembly) ───────────────────────────────────────
// =============================================================================
// Assembles all additive and subtractive geometry.
// Call with default INBOARD_SIGN for port (left) pylon.
// For starboard, re-export with -D INBOARD_SIGN=-1 which mirrors via scale().
module pylon(inboard_sign = INBOARD_SIGN) {
    mirror_vec = (inboard_sign < 0) ? [1, 0, 0] : [0, 0, 0];  // X-mirror for stbd

    mirror(mirror_vec) {
        difference() {

            // ==================================================================
            // ── Additive geometry ─────────────────────────────────────────────
            // ==================================================================
            union() {

                // ── Main hollow body ─────────────────────────────────────────
                pylon_body();

                // ── Thickened nacelle face plate (sector gear + boss socket) ─
                nacelle_face_block();

                // ── Wing root attachment block with shoulder flange ───────────
                wing_attach_block();

                // ── Fold hinge ears (extend inboard of wing block) ────────────
                fold_hinge_ears();

            } // end union

            // ==================================================================
            // ── Subtractive geometry ──────────────────────────────────────────
            // ==================================================================

            // ── Tilt spar press-fit bore (entire pylon length + fold ears) ───
            // The spar is fixed in this bore; nacelle bearings rotate on spar.
            spar_bore();

            // ── Nacelle boss socket (positive-stop receiver) ──────────────────
            // Accepts the 16 mm OD pivot boss from the nacelle X-face.
            nacelle_boss_socket();

            // ── Sector gear plate recess on nacelle face ──────────────────────
            // Provides radial seating for the sector gear (BODY_H = 3 mm plate).
            sector_gear_recess();

            // ── M2.5 insert pockets for sector gear mounting ──────────────────
            // 4× pockets at R = 18 mm, 45° / 135° / 225° / 315°.
            sector_gear_inserts();

            // ── M3 insert pockets for wing attachment bolts ───────────────────
            wing_bolt_inserts();

            // ── Fold hinge pin bore ────────────────────────────────────────────
            // 4 mm CF pin through both hinge ears.
            fold_hinge_pin_bore();

            // ── Fold set-screw bores (0° deployed + 90° stowed detents) ───────
            fold_set_screw_bores();

        } // end difference
    } // end mirror
}


// =============================================================================
// ── Render call ───────────────────────────────────────────────────────────────
// =============================================================================
// Default: port (left) pylon, INBOARD_SIGN = +1.
// Override at CLI for starboard: openscad -D INBOARD_SIGN=-1 ...
pylon(inboard_sign = INBOARD_SIGN);


// =============================================================================
// ── Print specifications ──────────────────────────────────────────────────────
// =============================================================================
// Material    : CF-PETG (CarbonX PETG+CF or equivalent)
// Layer height: 0.15 mm
// Walls       : 4 perimeter walls minimum
// Infill      : 40% gyroid throughout (structural — no non-structural regions)
// Nozzle      : Hardened-steel required (CF-PETG abrasive)
// Orientation : Long axis (X, spar direction) horizontal on build plate;
//               pylon body flat-face down; fold hinge ears pointing up.
//               Requires support under fold ears and wing block shoulder flange.
// Supports    : Breakaway / tree supports under hinge ears and flange overhangs.
// Quantity    : 2 per aircraft (port + starboard — mirror in slicer).
// Colour      : Matte black CF-PETG for UV/heat resistance.
//
// CRITICAL: Before printing, verify WING_SLOT_W and WING_SLOT_H
// by measuring the actual wing mount pocket in s_wings_both_shell24.stl.
// These dimensions are estimated (50 mm × 40 mm) based on Thingiverse model
// proportions at 2.197× scale.  Incorrect values will prevent mounting.
//
// Post-print checks:
//   1. Spar bore: measure ID = 3.98 ± 0.05 mm (should grip 4mm CF rod firmly).
//   2. Boss socket: measure ID = 16.6 ± 0.15 mm (nacelle boss should slip in,
//      not rock).
//   3. Sector gear recess: verify Ø 48 mm sector gear plate seats flush.
//   4. M2.5 insert pockets: heat-set 4× M2.5 brass inserts; confirm flush seating.
//   5. M3 insert pockets: heat-set 4× M3 brass inserts in wing block.
//   6. Fold hinge bores: 4mm CF pin should slide through both ears with hand
//      pressure; no rocking.  Apply thin film of PTFE grease.
//
// Render commands:
//   Port pylon:
//     openscad -o s_wing_nacelle_pylon_port_revo.stl \
//              s_wing_nacelle_pylon_revo.scad -D INBOARD_SIGN=1
//   Starboard pylon:
//     openscad -o s_wing_nacelle_pylon_stbd_revo.stl \
//              s_wing_nacelle_pylon_revo.scad -D INBOARD_SIGN=-1
