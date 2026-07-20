// =============================================================================
// port_tilt_spar_assembly.scad — ILLUSTRATIVE integration view (2026-07-19)
// =============================================================================
// Author  : Steve Griffing (assembled by Claude Opus 4.8)
// License : CC BY 4.0
//
// Shows how the PORT tilt-spar chain fits together, in the canonical HULL FRAME
// (X = +port, Y = +aft, Z = +dorsal; origin = SerenityAssembly.FCStd world):
//   • Port cargo-bay wing ROOT (baked cargo shell, clipped to the root region)
//     + its spar-drive ACCESSORIES (root bearing boss, servo cradle, wing-root
//     receiver/mortise, cableway ends) from cargo_spar_drive.scad.
//   • Port WING (baked hull-frame STL).
//   • Port NACELLE (baked hull-frame STL) shifted onto the spar line (see below).
//   • The NACELLE-INTERNAL parts that tilt with the pod: EDF inter-stage stator
//     sleeve, aft spider sleeve (EDF2 motor mount) + EDF2 motor, and the closed
//     iris nozzle assembly — placed via the nacelle pose (in_nacelle()).
//   • The NOZZLE PUSHROD DRIVE (Option B): spar crank + COTS pushrod to the
//     unison-ring lever ear (nacelle_nozzle_pushrod.scad).
//   • PLACEHOLDER 8 mm spar + the two bearings (F688ZZ root / MF128ZZ wingtip),
//     the Ø22 tilt-feedback ring magnet + non-ferrous hub, and the MT6701
//     sensor PCB — the Rev R2e tilt-feedback hardware.
//
// NACELLE ALIGNMENT (2026-07-19):
//   The baked nacelle pose (tools/bake_hull_frame.py Nacelle_Port) predates the
//   Rev R2 tilt-spar.  Its CG pivot boss — measured in nacelle_port_revs.stl at
//   hull Y=40.5, Z=63.2 — sits ~25 mm AFT of and ~3 mm below the spar line
//   (Y=15, Z=66), which read as "nacelle too far aft, spar not through the
//   mounting hole, and a proud gap at the wing tip".  A corrective shift
//   NAC_D[] brings the nacelle CG pivot onto the spar (TILT_SPAR_ANALYSIS.md §1:
//   a single straight spar runs cargo → wing → nacelle CG pivot at duct
//   Z=111.5) and closes the wing-tip↔nacelle interface.  The proper fix is to
//   re-derive the nacelle bake translation; this overlay applies NAC_D[] so the
//   INTENDED fit is shown without re-baking a mesh.
//
//   REV T CG RE-DERIVE (2026-07-19): PIVOT_ZLOC moved 104.5 → 111.5 mm (new 40 mm
//   nozzle fins).  NAC_D[] is now DERIVED from PIVOT_ZLOC (below), so the slide-
//   forward keeps ONE straight spar through the CURRENT CG pivot automatically.
//   Chosen reconciliation (user 2026-07-19): "slide the nacelle forward to Y=15"
//   — the wing/cargo spar stays at 22 % chord; the pod translates fwd so its CG
//   pivot reaches the spar.  CAVEAT: the baked STL's OLD pivot boss is at hull
//   Y≈40.5 (duct Z 104.5); at PIVOT_ZLOC=111.5 the spar sits ~7 mm AFT of that
//   stale boss — the nacelle STL still needs re-baking to the Rev T CG (WBS §1.1.3).
//
// NOTE: the baked wing/nacelle STLs predate the Rev R2e wingtip changes (MF128
// bearing, MT6701 pocket, straight tenon drill); the placeholder spar/bearings/
// sensor here reflect the CURRENT design and show intended fit.  This file is a
// VISUAL OVERLAY, not a build artifact.
//
// Render: openscad -o port_tilt_spar_assembly.png port_tilt_spar_assembly.scad
// =============================================================================

$fn = 48;

use <fuselage/cargo/cargo_spar_drive.scad>   // root_bearing_seat/servo_mount/…

// ── Spar axis (hull frame) ───────────────────────────────────────────────────
SPAR_Y   = 15;    // hull Y (chord-station 22 → camber)   [cargo_spar_drive PORT]
SPAR_Z   = 66;    // hull Z (camber midline + 58)
SPAR_X0  = -96;   // cargo (root-bearing) end
SPAR_X1  =  88;   // nacelle outboard end (through the outboard pivot boss)
SPAR_OD  = 8.0;

// Feature X-stations along the spar (hull X):
X_ROOT_BRG = -90;   // F688ZZ root bearing (cargo)          [x_root −81 + inb·9]
X_TIP_BRG  =   4;   // MF128ZZ wingtip bearing (wing tip pad)
X_RING     =   9;   // Ø22 ring magnet at nacelle inboard face
X_SENSOR   =   3;   // MT6701 PCB on the wing pad, chord-aft of the spar

// ── Nacelle pose (bake) + spar-alignment shift ───────────────────────────────
// Baked pose (tools/bake_hull_frame.py Nacelle_Port): 270° about +X then
// translate, so nacelle-LOCAL (x,y,z) → hull (x+47, z−64, −y+63).  The pod is
// modelled with the duct axis on local +Z, intake at local Z=0; the CG pivot /
// spar axis is at local Z = PIVOT_ZLOC.
NAC_BAKE   = [47, -64, 63];   // baked translation (rotation = 270° about +X)
PIVOT_ZLOC = 111.5;           // nacelle-local duct Z of the CG pivot / spar axis
                              //   (Rev T CG re-derive 2026-07-19; was 104.5)
// Corrective shift, DERIVED from PIVOT_ZLOC so it re-solves with the CG:
//   • Y: slide fwd so the CG pivot (baked hull Y = PIVOT_ZLOC + NAC_BAKE.y)
//        reaches the spar line SPAR_Y.
//   • Z: drop onto the spar height (bore-centre baked hull Z ≈ 63.2 → SPAR_Z).
//   • X: 3 mm inboard nudge that closes the wing-tip↔nacelle shell gap.
PIVOT_Y_BAKED = PIVOT_ZLOC + NAC_BAKE[1];             // pre-shift pivot hull Y (= 47.5)
NAC_D = [-3, SPAR_Y - PIVOT_Y_BAKED, SPAR_Z - 63.2];  // = [-3, -32.5, +2.8]

// ── Small helpers ─────────────────────────────────────────────────────────────
module x_cyl(d, len)  { rotate([0, 90, 0]) cylinder(d = d, h = len); }      // +X axis
module bearing(od, w, id) {                                                 // race ring
    rotate([0, 90, 0]) difference() {
        cylinder(d = od, h = w);
        translate([0, 0, -0.1]) cylinder(d = id, h = w + 0.2);
    }
}
module ring(od, id, t) {
    rotate([0, 90, 0]) difference() {
        cylinder(d = od, h = t);
        translate([0, 0, -0.1]) cylinder(d = id, h = t + 0.2);
    }
}
// Place a bore-coaxial nacelle-LOCAL part (local +Z = duct axis, intake at 0)
// into the hull frame at the spar-aligned nacelle pose.  zseat = the nacelle-
// local Z at which the part's local Z origin seats.
module in_nacelle(zseat = 0) {
    translate([NAC_BAKE[0] + NAC_D[0], NAC_BAKE[1] + NAC_D[1], NAC_BAKE[2] + NAC_D[2]])
        rotate([-90, 0, 0])
            translate([0, 0, zseat])
                children();
}
// Straight rod of diameter d between two points (used for the COTS pushrod).
module rod(p1, p2, d) {
    v = p2 - p1;
    L = norm(v);
    if (L > 1e-3)
        translate(p1) rotate(acos(v[2] / L), [-v[1], v[0], 0]) cylinder(d = d, h = L);
}

// =============================================================================
// 1) PORT CARGO-BAY WING ROOT (baked cargo shell, clipped to the root region)
// =============================================================================
color([0.82, 0.72, 0.55, 0.30])                          // translucent tan
intersection() {
    import("../stls/fuselage/cargo/cargo_sect_shell24_2mm_repaired.stl", convexity = 6);
    translate([-115, -15, 18]) cube([80, 120, 90]);      // port root region only
}

// ── Cargo spar-drive ACCESSORIES (port), each a distinct colour ──────────────
//   PORT args: spar_y=15, spar_z=66, x_root=-81, inb=-1, tenon_y=57.5,
//   tenon_z=58, cable_y=55, wall_x=-86  (matches cargo_spar_drive.scad PORT[]).
color([0.90, 0.55, 0.25, 0.85]) wing_root_receiver(15, 66, -81, -1, 57.5, 58); // orange
color([0.95, 0.80, 0.20])       root_bearing_seat(15, 66, -81, -1);            // gold boss
color([0.65, 0.35, 0.80, 0.9])  servo_mount(15, 66, -81, -1, -86);             // purple
color([0.20, 0.70, 0.75])       cableway_ends(55, 66, -1, -86);                // teal tubes

// =============================================================================
// 2) PORT WING (baked hull-frame STL)
// =============================================================================
color([0.45, 0.78, 0.45, 0.45])                          // translucent green
    import("../stls/wings/wing_port_s1223_revo.stl", convexity = 6);

// =============================================================================
// 3) PORT NACELLE (baked hull-frame STL) — shifted onto the spar line
// =============================================================================
color([0.45, 0.58, 0.88, 0.35])                          // translucent blue
    translate(NAC_D)
        import("../stls/nacelles/nacelle_port_revs.stl", convexity = 6);

// =============================================================================
// 4) PLACEHOLDER SPAR + BEARINGS + TILT-FEEDBACK HARDWARE (Rev R2e)
// =============================================================================
// 8 mm rotating tilt-spar (steel)
color([0.62, 0.62, 0.66])
    translate([SPAR_X0, SPAR_Y, SPAR_Z]) x_cyl(SPAR_OD, SPAR_X1 - SPAR_X0);

// Root bearing — F688ZZ 8×16×5 (cargo)
color([0.95, 0.75, 0.10])
    translate([X_ROOT_BRG, SPAR_Y, SPAR_Z]) bearing(16, 5, SPAR_OD + 0.3);

// Wingtip bearing — MF128ZZ 8×12×3.5 (wing tip)
color([0.95, 0.75, 0.10])
    translate([X_TIP_BRG, SPAR_Y, SPAR_Z]) bearing(12, 3.5, SPAR_OD + 0.3);

// Ø22 diametric ring magnet (rotor) — red
color([0.88, 0.20, 0.20])
    translate([X_RING, SPAR_Y, SPAR_Z]) ring(22, 10, 2.5);

// Non-ferrous ring-carrier hub (Ø24) — dark grey
color([0.30, 0.30, 0.34, 0.9])
    translate([X_RING - 3, SPAR_Y, SPAR_Z]) ring(24, SPAR_OD + 2, 8);

// MT6701 sensor PCB (7×7) on the wing pad, chord-aft (+Y) of the spar — dark green
color([0.10, 0.38, 0.16])
    translate([X_SENSOR - 1.6, SPAR_Y + 11 - 3.5, SPAR_Z - 3.5]) cube([1.6, 7, 7]);

// =============================================================================
// 5) NACELLE-INTERNAL PARTS THAT TILT WITH THE POD
// =============================================================================
// Nacelle-local seat stations (duct Z) from the part sources:
//   stator sleeve   90 … 122.5  (edf_stator_sleeve.scad)     — spar tunnel at 111.5
//   aft spider slv  122.5 … 166.25 (edf_aft_spider_sleeve.scad) — EDF2 motor mount
//   nozzle ring     166.25+      (nacelle_pod_50mm_tandem.scad NOZZLE_RING_Z)
STATOR_ZSEAT   = 90.0;
AFT_SLV_ZSEAT  = 122.5;
NOZZLE_RING_Z  = 166.25;

// EDF inter-stage stator sleeve (hub + 11 twisted fins + spar tunnel) — olive
color([0.72, 0.72, 0.32, 0.95])
    in_nacelle(STATOR_ZSEAT)
        import("../stls/nacelles/edf_stator_sleeve.stl", convexity = 6);

// Aft spider sleeve = the EDF2 (aft) MOTOR MOUNT — tan
color([0.60, 0.48, 0.30, 0.95])
    in_nacelle(AFT_SLV_ZSEAT)
        import("../stls/nacelles/edf_aft_spider_sleeve.stl", convexity = 6);

// EDF2 motor (placeholder Ø28×28): seats on the spider aft face, body protrudes
// aft toward the nozzle throat — dark grey
color([0.22, 0.22, 0.25])
    in_nacelle(150) cylinder(d = 28, h = 28);

// Iris nozzle assembly (throat + housing + cam ring + 8 tangential-hinge flaps),
// CURRENT Rev T output (nacelle_nozzle_iris.scad, RENDER_PART="asm").  Its local
// frame: bonding lip at local −Z mates the nacelle exit face, throat at Z≈0,
// flaps extend to +Z — so local +Z = aft.  Seated with the throat/ring forward
// face at NOZZLE_RING_Z, in_nacelle() sends +Z → hull +Y (aft): throat forward,
// exit aft.  (Was the stale 2026-06-09 nacelle_nozzle_closed_asm.stl — the OLD
// Rev R1 axial-hinge nozzle, which also came out reversed.) — rose
color([0.85, 0.42, 0.52, 0.85])
    in_nacelle(NOZZLE_RING_Z)
        import("../stls/nacelles/nozzles/nacelle_nozzle_iris.stl", convexity = 6);

// The 8 tangential-hinge nozzle flaps, CLOSED position (0° tilt / cruise: exit
// = 75 % of bore = R 18.75, CONVERGING).  The on-disk iris.stl above is throat +
// housing + cam ring only; the 40 mm petals are a separate print part
// (nacelle_nozzle_flap.stl, ×8).  This replicates the per-flap transform from
// nacelle_nozzle_iris.scad "asm" — sweep around Z, seat the hinge at
// (R_HINGE, 0, HINGE_Z), tilt about the tangential axis — BUT with the tilt sign
// CORRECTED to −PHI_CLOSED.  The flap body sits just inside R_HINGE and extrudes
// +Z, so the source asm's +PHI_CLOSED throws the tips OUTWARD (diverging), which
// contradicts exit_r = R_HINGE − FLAP_LENGTH·sin φ (tips should move inward).
// The asm loop in nacelle_nozzle_iris.scad has the sign flipped — preview-only
// bug (print parts unaffected); flagged for a source fix.
NZ_N_FLAPS = 8;                              // N_FLAPS         [iris scad]
NZ_R_HINGE = 27.5;                           // THROAT_OUTER_R  [iris scad]
NZ_HINGE_Z = 15.0;                           // = THROAT_LEN    [iris scad]
NZ_PHI_CL  = asin((27.5 - 18.75) / 40.0);    // PHI_CLOSED ≈ 12.64° (L=40)
color([0.95, 0.55, 0.45, 0.90])              // coral petals
    in_nacelle(NOZZLE_RING_Z)
        for (i = [0 : NZ_N_FLAPS - 1])
            rotate([0, 0, i * 360 / NZ_N_FLAPS])
                translate([NZ_R_HINGE, 0, NZ_HINGE_Z])
                    rotate([0, -NZ_PHI_CL, 0])
                        import("../stls/nacelles/nozzles/nacelle_nozzle_flap.stl",
                               convexity = 4);

// =============================================================================
// 6) NOZZLE PUSHROD DRIVE (Option B — nacelle_nozzle_pushrod.scad, Rev T)
// =============================================================================
// spar_crank clamps the ROTATING spar at the pivot station (nacelle Z=111.5);
// its arm reaches aft (local +Z) to a ball stud at CRANK_R.  A COTS M3 ball-link
// pushrod ties that ball to the unison-ring lever ear (RING_LEVER_R at
// RING_LEVER_AZ, on the nozzle ring).
//
// NOTE — the exact crank radius, ball 3-D positions and rod length that give a
// monotonic 0..90°-tilt → 0..23.75°-ring map are the RSSR spatial-linkage
// SYNTHESIS, flagged *VERIFY* in nacelle_nozzle_pushrod.scad (WBS §1.1.3).  This
// overlay shows the drive TOPOLOGY (crank on the spar, straight rod to the ring
// lever), NOT solved kinematics — the drawn rod length is not the final value.
CRANK_R       = 8.5;                       // crank ball-stud radius   [pushrod scad]
RING_LEVER_R  = 32.0;                       // ring lever-ear ball reach [iris scad]
RING_LEVER_AZ = 22.5;                       // ring lever-ear azimuth    [iris scad]
CRANK_XLOC    = RING_LEVER_R * cos(RING_LEVER_AZ);   // clamp X aligns rod under ear

crank_ball = [CRANK_XLOC, 0, PIVOT_ZLOC + CRANK_R];                 // nacelle-local
ring_ball  = [RING_LEVER_R * cos(RING_LEVER_AZ),
              RING_LEVER_R * sin(RING_LEVER_AZ), NOZZLE_RING_Z + 4]; // nacelle-local

// spar crank (clamped on the spar, arm aft) — cyan
color([0.25, 0.75, 0.85])
    in_nacelle() translate([CRANK_XLOC, 0, PIVOT_ZLOC])
        import("../stls/nacelles/nacelle_pushrod_crank.stl", convexity = 4);

// COTS pushrod (M3 ball-link rod), straight crank-ball → ring-lever ball — yellow
color([0.85, 0.82, 0.20])
    in_nacelle() rod(crank_ball, ring_ball, 3.0);
