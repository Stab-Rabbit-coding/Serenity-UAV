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
//   • The NOZZLE DRIVE marker: servo-in-pod drive (2026-09-28); only
//     the unison-ring lever pull point is drawn until the servo mount exists
//     (see §6 for why the wing-referenced sun/pinion drive was retired).
//   • PLACEHOLDER 8 mm spar + the two bearings (F688ZZ root / MF128ZZ wingtip),
//     the Ø22 tilt-feedback ring magnet + non-ferrous hub, and the AK7455
//     off-axis SPI encoder PCB — the Rev R2e tilt-feedback hardware.
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
//   pivot reaches the spar.
//
//   PIVOT_ZLOC CORRECTION (2026-09-09): the 111.5 above is SUPERSEDED.  The pod's
//   authoritative pivot is PIVOT_Z = 107.5 mm (source of truth: airframe/openscad/
//   nacelles/nacelle_pod_50mm_tandem.scad:437 — Rev T4c, ESC-bay CG re-derive with
//   the 30 mm nozzle flaps).  This overlay had drifted and is corrected below.
//   CAVEAT (unchanged in kind): the baked STL's OLD pivot boss is at hull Y≈40.5
//   (duct Z 104.5); at PIVOT_ZLOC=107.5 the spar sits ~3 mm AFT of that stale
//   boss — the nacelle STL still needs re-baking to the Rev T CG (WBS §1.1.3).
//
// NOTE: the baked wing/nacelle STLs predate the Rev R2e wingtip changes (MF128
// bearing, AK7455 pocket, straight tenon drill); the placeholder spar/bearings/
// sensor here reflect the CURRENT design and show intended fit.  This file is a
// VISUAL OVERLAY, not a build artifact.
//
// Render: openscad -o port_tilt_spar_assembly.png port_tilt_spar_assembly.scad
// =============================================================================

$fn = 48;

use <fuselage/cargo/cargo_spar_drive.scad>   // root_bearing_seat/servo_mount/…

// ── Spar axis (hull frame) ───────────────────────────────────────────────────
// REV S1c (2026-08-18): these were still the pre-Rev-S1b values (the 22.0 mm
// chord station, and a Z rounded off the old midline).  Rev S1b moved the spar
// to the 45.15 mm station = 35 % root chord; this overlay never followed, so
// every derived pose below — including NAC_D, which slides the nacelle onto the
// spar line — was solving against a spar that no longer exists.
// Both values now match airframe/blender-scripts/merge_cargo_interior.py
// (WING_SPAR_Y / WING_SPAR_Z), which is the fuselage-side authority for the
// same physical rod.
SPAR_Y   = 38.15; // hull Y (chord-station 45.15 = 35 % root chord → camber midline)
SPAR_Z   = 68.42; // hull Z (camber midline 10.41 + chord line 58.01)
SPAR_X0  = -96;   // cargo (root-bearing) end
SPAR_X1  =  88;   // nacelle outboard end (through the outboard pivot boss)
SPAR_OD  = 8.0;

// Feature X-stations along the spar (hull X):
X_ROOT_BRG = -90;   // F688ZZ root bearing (cargo)          [x_root −81 + inb·9]
X_TIP_BRG  =   4;   // MF128ZZ wingtip bearing (wing tip pad)
X_RING     =   9;   // Ø22 ring magnet at nacelle inboard face
X_SENSOR   =   3;   // AK7455 PCB on the wing pad, chord-aft of the spar

// ── Nacelle pose (bake) + spar-alignment shift ───────────────────────────────
// Baked pose (tools/bake_hull_frame.py Nacelle_Port): 270° about +X then
// translate, so nacelle-LOCAL (x,y,z) → hull (x+47, z−64, −y+63).  The pod is
// modelled with the duct axis on local +Z, intake at local Z=0; the CG pivot /
// spar axis is at local Z = PIVOT_ZLOC.
NAC_BAKE   = [47, -64, 63];   // baked translation (rotation = 270° about +X)
PIVOT_ZLOC = 103.5;           // nacelle-local duct Z of the CG pivot / spar axis.
                              //   Rev T6 (2026-09-29): 107.5 -> 103.5 with the pod
                              //   (fixed open nozzle moved the CG forward, D-TW-5).
                              //   CORRECTED 2026-09-09: this file carried a
                              //   STALE 111.5 (Rev T CG re-derive 2026-07-19,
                              //   itself up from 104.5).  The AUTHORITATIVE
                              //   value is the pod's own PIVOT_Z = 107.5, set
                              //   by the Rev T4c ESC-bay CG re-derive —
                              //   source of truth:
                              //   airframe/openscad/nacelles/
                              //   nacelle_pod_50mm_tandem.scad:437.
                              //   NAC_D[] below is DERIVED from this, so the
                              //   overlay's slide-forward re-solves with it.
// Corrective shift, DERIVED from PIVOT_ZLOC so it re-solves with the CG:
//   • Y: slide fwd so the CG pivot (baked hull Y = PIVOT_ZLOC + NAC_BAKE.y)
//        reaches the spar line SPAR_Y.
//   • Z: drop onto the spar height (bore-centre baked hull Z ≈ 63.2 → SPAR_Z).
//   • X: +JOINT_GAP_X OUTBOARD sets the wing-tip↔nacelle clearance.  Now that the
//        nozzle drive is a servo inside the pod (2026-09-28; §6), nothing
//        of the nozzle drive crosses the joint, and the gap stays at ~4 mm — the
//        floor set by the Hall air gap (1.5 mm), the wing tip pad and a
//        tilt-rotation safety margin.  The nacelle rotates IN-PLANE about the spar, so tilting needs no
//        extra axial gap (the faces stay parallel through the sweep).
//   AERO (user-requested check): the gap is a spanwise slot between the wing tip
//   and the pod side; its only flow effect is a weak through-gap jet driven by the
//   wing's light 40-kt loading (≈3.8 lbf/side) + the wing-body horseshoe vortex.
//   SHRINKING the gap monotonically WEAKENS the through-flow and the gap vortex —
//   it removes an eddy source, it does not add one (no new sharp edge / slot / knife
//   edge is introduced; the junction vortex exists at any gap).  At ~4 mm on a
//   ~75 mm pod it is a few-percent clearance, well inside Serenity's existing
//   blocky-junction character.  Cannot go to 0: the nacelle must clear the fixed
//   wing through the full tilt, and the bearing/sensor/mesh live here.
JOINT_GAP_X   = 1;                                    // [mm] → ~4 mm joint gap (min)
PIVOT_Y_BAKED = PIVOT_ZLOC + NAC_BAKE[1];             // pre-shift pivot hull Y (= 43.5
                                                      //   at PIVOT_ZLOC 107.5; was 47.5)
NAC_D = [JOINT_GAP_X, SPAR_Y - PIVOT_Y_BAKED, SPAR_Z - 63.2];  // = [+1, -5.35, +5.22]
// Rev S1c: the trailing comment used to read [+5, -32.5, +2.8].  Two of the
// three were stale: the Y shift followed the spar from 15 to 38.15 (so the pod
// slides 23.15 mm LESS far forward — the point of moving the spar aft), and the
// X figure had never been updated after JOINT_GAP_X was minimised 5 -> 1.

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
// Torus arc (loop_r loop of tube_r cable) for the cableway service loop.
module torus(loop_r, tube_r, ang = 360) {
    rotate_extrude(angle = ang, $fn = 40)
        translate([loop_r, 0, 0]) circle(r = tube_r, $fn = 14);
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
color([0.20, 0.70, 0.75])       cableway_ends(5, 66, -1, -86);                 // teal tubes (fwd)

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

// AK7455 sensor PCB (7×7) on the wing pad, chord-aft (+Y) of the spar — dark green
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
// 6) NOZZLE DRIVE — per-nacelle SERVO scheduled on measured tilt (2026-09-28)
// =============================================================================
// SUPERSEDED 2026-09-28 (owner decision, docs/NOZZLE_DRIVE_TRADE.md "DECISION
// AMENDMENT — servo drive (2026-09-28)"): the wing-fixed sun + nacelle pinion + geared bellcrank
// drive drawn here until this revision is RETIRED and archived
// (archives/airframe-archives/archive/openscad/nacelles/nacelle_nozzle_sync_gears.scad,
// nacelle_nozzle_pushrod.scad).  It was unbuildable: the sun had 0.0 mm axial
// room in the Rev T4 trunnion, the pinion (26.4 mm aft of the pivot) collided
// with the Rev T1 tilt-drive shaft (wing station 53.6), and any continuous 1:1
// drive over-strokes the ring past 90 deg tilt (ring -40.7 deg at 140 deg vs a
// 23.75 deg stroke).
//
// The nozzle is now driven by a sub-micro servo inside the pod, FORWARD of the
// ring, pulling the unison-ring lever ear (RING_LEVER_AZ 157.5 deg, inboard flap
// gap) through a pull-only slotted link; a torsion spring drives the ring to its
// hard 105 % stop whenever the servo stops pulling.  The servo station is set by
// docs/plans/2026-09-28-001-feat-nacelle-nozzle-servo-drive-plan.md U4; only the
// ring-lever ball is marked here until that geometry exists.
//
// AI contribution: Claude (Claude Opus 5.5, Anthropic), directed by Steve Griffing.
RING_LEVER_R  = 32.0;                 // [mm] ring lever-ear reach  [iris scad]
RING_LEVER_AZ = 157.5;                // [deg] lever ear, inboard flap gap  [iris scad]
ring_ball  = [RING_LEVER_R * cos(RING_LEVER_AZ),
              RING_LEVER_R * sin(RING_LEVER_AZ), NOZZLE_RING_Z + 4];
// ring-lever ear pull point (inboard flap gap) — red marker
color([0.90, 0.20, 0.20])
    in_nacelle() translate(ring_ball) sphere(d = 4);

// =============================================================================
// 7) EDF CABLEWAY — routed FORWARD of the pivot + rotation-tolerant connection
// =============================================================================
// The double-D EDF power/signal cableway (2× Ø7, cargo → wing, drawn as the teal
// tubes in §1) is re-routed to cross the joint FORWARD of the pivot (hull Y≈5,
// ahead of the spar at Y=15) so it clears the tilt-drive shaft
// (which lives aft of the spar).  The wing→nacelle crossing is a SERVICE LOOP: the
// harness anchors on the FIXED wing (cableway exit) and on a nacelle grommet near
// the spar axis, with a slack coil that winds/unwinds over the −5..90° (≈95°)
// tilt.  Anchoring the nacelle end NEAR the spar (small radius) keeps the loop
// excursion small (arc ≈ r·1.66 rad ≈ 12 mm at r≈7) — no slip-ring needed; the
// EDF power is too thick for the Ø5 hollow-spar bore (that carries only the
// nav-light 3-core).  SOURCE follow-up: move wing CABLE_BORE_XFR 0.48c → ~0.10c
// with a forward channel through the Ø29.5 wingtip pad, keeping the off-axis
// AK7455 Hall pocket (chord-aft of the spar) clear.
CW_GROMMET = [10, 8, 66];   // nacelle harness grommet (hull), fwd of the pivot boss

// service-loop slack coil (Ø14 loop of Ø4 harness), axis ≈ spar so nacelle tilt
// winds/unwinds it — teal
color([0.20, 0.62, 0.68])
    translate([6, 2, 66]) rotate([0, 90, 0]) torus(7, 2, 300);
// nacelle harness grommet — cable pass-through boss on the inboard face — teal
color([0.15, 0.52, 0.58])
    translate(CW_GROMMET) rotate([0, 90, 0])
        difference() {
            cylinder(d = 9, h = 4, center = true);
            cylinder(d = 5, h = 4.2, center = true);
        }
