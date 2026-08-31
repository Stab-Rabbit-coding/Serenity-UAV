// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Hull frame (canonical for ALL design artifacts): X = +port (left),
//   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
//   world origin.  Primary-component STLs published to airframe/stls/
//   are stored directly in hull frame, baked by tools/bake_hull_frame.py
//   (marker 'SerenityUAV HULL-FRAME R1' in the binary STL header).
//   NEVER re-bake a mesh derived from an already-baked file.
//   This file:
//     Part-local print frame, coaxial with the nacelle duct (duct axis =
//     local +Z, intake at Z = 0).  Hull placement derives from the nacelle
//     pose (cruise = 270 deg about +X + translation; hover rotates about the
//     tilt pivot at duct Z = 83 mm).  Assembly placement VERIFY pending
//     (serenity_assembly.py).
// ===========================================================================
// =============================================================================
// edf_stator_sleeve.scad
// Serenity UAV — Rev R — EDF Inter-stage Stator Sleeve
// =============================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Project : Serenity-class Tilt-Rotor UAV (24-inch scale, Firefly TV ship)
// License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date    : 2026-05-29
// Revision: Rev T4 (2026-08-30) — through-duct spar strut + clearance bore DELETED
//           (Rev R 2026-06-11; Rev A 2026-05-29)
//
// Change from Rev T2 (Rev T4 — 2026-08-30)
// ----------------------------------------
//   The rotating 8 mm tilt-spar no longer crosses the duct (Rev T1 fixed CF
//   spar, terminated outside r = 25 mm — docs/WING_ATTACH_INTERFACE.md §4.3a),
//   so spar_fairing() and spar_bore_cut() are DELETED.  The sleeve is now a
//   clean 11-vane annulus, and the 0° anti-rotation key — which the Rev T2 spar
//   bore had to be drilled through, splitting it in two — is continuous again.
//   Analysis and edit by Claude (Claude Opus 5, Anthropic) under the author's
//   direction, per AGENTS.md §3 AI attribution.
//
// Description
// -----------
// Removable stator sleeve for the Serenity-UAV tandem-EDF nacelle
// (nacelle_pod_50mm_tandem.scad Rev T).
//
// Bore-interior axial order (nacelle coordinates):
//   intake → rotor1 → spider1 → motor1 → [stator sleeve] → rotor2 → spider2 → motor2 → nozzle
//
// This sleeve occupies Z = 90 … 122.5 mm (nacelle) and contains only the
// inter-stage stator hub and 11 twisted fins.  No motor mounts.
//
// Retention
// ---------
//   Forward stop: nacelle bore narrows from SLEEVE_BORE_R (27.7 mm) to
//   EDF_BORE_R (25 mm) at Z = 90 mm — sleeve OD 27.5 mm cannot advance past
//   this shoulder.
//   Aft retention: aft spider sleeve (edf_aft_spider_sleeve.scad) pushes
//   forward against this sleeve's aft face.  No own fasteners required.
//
// Anti-rotation: 3× longitudinal keys at 0°, 120°, 240° on sleeve OD engage
// matching slots in nacelle enlarged bore (bore_key_slots() in nacelle Zone B).
//
// Installation sequence
// ---------------------
//   1. Install EDF1 motor into nacelle (from nozzle, screws from intake).
//   2. Slide stator sleeve (nozzle end first) into nacelle until forward stop.
//   3. Install aft spider sleeve assembly (see edf_aft_spider_sleeve.scad).
//      Aft sleeve forward face pushes against this sleeve's aft face.
//   4. Secure aft sleeve with 3× M3 SHCS at nozzle ring pocket.
//
// References
// ----------
//   [1] nacelle_pod_50mm_tandem.scad Rev T — mating nacelle bore geometry.
//   [2] edf_aft_spider_sleeve.scad — aft sleeve that retains this sleeve.
//   [3] Serenity-UAV project CLAUDE.md — fabrication standards (2026).
//
// =============================================================================


// =============================================================================
// ── Parameter Block ───────────────────────────────────────────────────────────
// =============================================================================

// ── Sleeve tube dimensions ─────────────────────────────────────────────────────
// Must match nacelle_pod_50mm_tandem.scad Rev T bore parameters.
EDF_BORE_R      =  25.0;    // [mm] EDF bore inner radius (50 mm ID)
SLEEVE_OD       =  55.0;    // [mm] sleeve OD (= EDF_CASING_R × 2 = 27.5 mm × 2)
SLEEVE_WALL     =   2.5;    // [mm] wall thickness = (SLEEVE_OD − 50) / 2

// Nacelle-local Z boundaries of this sleeve (STATOR_SLV_Z_START / END in nacelle file).
SLEEVE_Z_START  =  90.0;    // [mm] sleeve forward face (nacelle coord)
SLEEVE_Z_END    = 122.5;    // [mm] sleeve aft face     (nacelle coord)
SLEEVE_L        = SLEEVE_Z_END - SLEEVE_Z_START;  // = 32.5 mm

// ── Anti-rotation keys ─────────────────────────────────────────────────────────
// Must match nacelle SLEEVE_KEY_W / SLEEVE_KEY_H and key-slot angles.
SLEEVE_KEY_W    =   3.0;    // [mm] key tangential width
SLEEVE_KEY_H    =   3.0;    // [mm] key radial height above sleeve OD
KEY_ROOT_OVERLAP =  0.5;    // [mm] key root sunk below the tube OD — CGAL
                            //      volumetric overlap, not a touching face

// ── Sleeve key CLOCKING (Rev T4b, 2026-08-31) ────────────────────────────────
// Moved 0/120/240 -> 30/150/270, and the reason is an interference, not tidiness.
//
// A key stands proud to r = 30.5 and runs the sleeve's full length, so a key at
// 0 deg lies along +X and a key at 180 deg along -X — which is exactly where the
// trunnion sits, on the starboard and port pods respectively.  Measured mesh
// against mesh, the 0 deg key drove 37.7 mm3 of solid overlap into the starboard
// trunnion (tools/nacelle_trunnion_fit.py gate T8b).
//
// With three keys at 120 deg spacing the only clockings that miss BOTH +X and -X
// are theta = 30 and 90 (and equivalents).  30/150/270 is used: it holds 30 deg
// of angular clearance from each trunnion, and at r 30.5 the keys reach only
// |X| = 26.4, inboard of the trunnion's 28.2 face by 1.8 mm.
//
// The aft sleeve's M3 retention screws pass THROUGH the key ribs, and the pod's
// retention bosses receive them, so all three feature sets move together.
SLEEVE_KEY_ANGLES = [30, 150, 270];

// ── Stator geometry (nacelle 1.25× scale values converted to sleeve-local Z) ──
// Sleeve-local Z = nacelle Z − SLEEVE_Z_START
STATOR_Z_BOT_L  =   3.75;  // [mm] stator bottom (nacelle 93.75 − 90.0)
STATOR_Z_TOP_L  =  28.75;  // [mm] stator top    (nacelle 118.75 − 90.0)
// N_FINS MUST stay COPRIME with the 12-blade EDF rotor (Xfly Galaxy X5) so the
// rotor↔stator interaction tones stay cut off (Tyler–Sofrin rotor-stator mode
// selection): use 11 (chosen — preserves the vetted thrust/solidity budget) or
// 13 ONLY.  NEVER 12 (1:1 resonance) and avoid even counts sharing factors with
// 12.  (Rev T4: the old note here about the spar needing its own streamlined
// strut is obsolete — nothing crosses the duct now.  See the SUPERSEDED block.)
N_FINS          =  11;     // [count] inter-stage stator fins (coprime w/ 12-blade rotor)
FIN_THICKNESS   =   2.0;   // [mm] fin tangential thickness
VANE_ANGLE_DEG  =  33.0;   // [deg] fin angle from axial (tuned to 50 mm 6S tip swirl)

// ── Hub dimensions ─────────────────────────────────────────────────────────────
// Hub bore routes EDF1 ESC wires through stator zone to inter-stage space.
S_HUB_R         =   8.0;   // [mm] hub outer radius (16 mm OD)
S_HUB_BORE_R    =   2.0;   // [mm] hub bore radius   ( 4 mm ID)

// ── SUPERSEDED Rev T4 (2026-08-30) — the through-duct spar and its fairing ───
// DELETED, not deferred.  Through Rev T2 a rotating O8 mm tilt spar crossed the
// duct spanwise at the CG pivot, right inside this sleeve, and had to be carried
// across the annulus on a streamlined teardrop strut (SPAR_FAIR_*) with a
// clearance bore drilled through strut, hub and the 0 deg anti-rotation key.
//
// Under Rev T1 the spar is a FIXED 20 x 16.3 mm carbon tube bonded into the wing
// and STOPPING at |X| >= 26 mm -- outside the r = 25 mm duct
// (docs/WING_ATTACH_INTERFACE.md S4.3a, wings_s1223_revo.scad
// SPAR_TIP_PROTRUSION).  Nothing crosses the duct any more: the nacelle hangs on
// a trunnion bearing pair at its inboard face (nacelle_trunnion.scad).
//
// So this sleeve reverts to what the aero always wanted -- a CLEAN 11-vane
// annulus with no bluff body upstream of EDF2.  What that buys, measured:
//   * the strut's blockage of the annulus is gone.  It was inherently bluff
//     (the O8.15 bore was ~= its own chord, noted in the Rev T2 comment) and it
//     sat 1 mm upstream of the vane trailing-edge plane, i.e. in the ONLY
//     straightening length EDF2 had.
//   * the 0 deg anti-rotation key is CONTINUOUS again.  Rev T2 had to drill the
//     spar bore out through it, leaving that key in two pieces -- a real
//     structural defect in the part that reacts EDF torque.
//   * the hub bore is once more a clean O4 wire route end to end.
//
// The 11-vane count is UNCHANGED and still coprime with the 12-blade Xfly rotor
// (Tyler-Sofrin); the note below about "no diametric fin pair on the spar axis"
// is now moot -- there is no spar axis to carry.
// Removed constants (recorded, not re-used): SPAR_TUNNEL_Z_L 21.5,
// SPAR_BORE_D_S 8.15, SPAR_FAIR_THK 13.0, SPAR_FAIR_TAIL 7.0.

// ── Swirl direction ─────────────────────────────────────────────────────────────
SWIRL_DIR       =  +1;     // [+1 / -1] port nacelle CW; override: -D SWIRL_DIR=-1

// ── Global facet resolution ─────────────────────────────────────────────────────
$fn = 72;


// =============================================================================
// ── Module: stator_sleeve_body ───────────────────────────────────────────────
// =============================================================================
// Hollow cylinder: OD = 55 mm, ID = 50 mm, length = 32.5 mm.
// Three longitudinal key ribs protrude radially from the OD at 0°/120°/240°.
module stator_sleeve_body() {
    union() {

        // ── Main tube ──────────────────────────────────────────────────────
        difference() {
            cylinder(r = SLEEVE_OD / 2, h = SLEEVE_L, center = false);
            translate([0, 0, -0.01])
                cylinder(r = EDF_BORE_R, h = SLEEVE_L + 0.02, center = false);
        }

        // ── Anti-rotation keys (3× at 120°) ──────────────────────────────
        // Rectangular rib on OD surface, spans full sleeve length.
        // Engages bore_key_slots() in nacelle enlarged bore.
        for (angle = SLEEVE_KEY_ANGLES) {
            rotate([0, 0, angle])
            // Rev T4 (2026-08-30): the key root is sunk KEY_ROOT_OVERLAP mm
            // BELOW the tube OD so the two solids INTERPENETRATE rather than
            // meet on a coincident cylindrical face.  A touching face is what
            // left the exported STL locally non-manifold (WBS §1.1.3 "MESH FIX
            // 2026-08-25"), which had been patched downstream with a manifold3d
            // re-union of the split bodies; fixing it in the source removes the
            // need for that pass.  Outer edge is unchanged at OD/2 + KEY_H.
            translate([SLEEVE_OD / 2 - KEY_ROOT_OVERLAP, -SLEEVE_KEY_W / 2, 0])
                cube([SLEEVE_KEY_H + KEY_ROOT_OVERLAP, SLEEVE_KEY_W, SLEEVE_L]);
        }

    }
}


// =============================================================================
// ── Module: stator_hub ───────────────────────────────────────────────────────
// =============================================================================
// Hollow hub ring at stator zone: OD = 16 mm, bore = 4 mm.
// Routes EDF1 ESC wires through the fin stack.
module stator_hub() {
    translate([0, 0, STATOR_Z_BOT_L])
        difference() {
            cylinder(r = S_HUB_R,
                     h = STATOR_Z_TOP_L - STATOR_Z_BOT_L,
                     center = false);
            translate([0, 0, -0.01])
                cylinder(r = S_HUB_BORE_R,
                         h = (STATOR_Z_TOP_L - STATOR_Z_BOT_L) + 0.02,
                         center = false);
        }
}


// =============================================================================
// ── Module: stator_fin ───────────────────────────────────────────────────────
// =============================================================================
// One twisted stator fin, sleeve-local Z coordinates.
// Radial span (S_HUB_R − 1) → (EDF_BORE_R + 1); ±1 mm CGAL volumetric overrun
// prevents touching-face errors at hub cylinder and sleeve bore-wall interfaces.
module stator_fin(phi_center, swirl_dir) {
    fin_h     = STATOR_Z_TOP_L - STATOR_Z_BOT_L;
    twist_deg = swirl_dir * VANE_ANGLE_DEG * 2;

    rotate([0, 0, phi_center])
        translate([0, 0, STATOR_Z_BOT_L])
            linear_extrude(
                height = fin_h,
                twist  = twist_deg,
                slices = 16,
                center = false
            )
                translate([S_HUB_R - 1, -FIN_THICKNESS / 2, 0])
                    square([EDF_BORE_R - S_HUB_R + 2, FIN_THICKNESS]);
}


// =============================================================================
// ── Module: edf_stator_sleeve (main assembly) ────────────────────────────────
// =============================================================================
// Union of sleeve body, stator hub, and 11 stator fins.
// Fin arms extend +1 mm past the bore wall (EDF_BORE_R + 1 = 26 mm) to overlap
// the sleeve tube inner wall, providing CGAL volumetric contact.
module edf_stator_sleeve(swirl_dir = SWIRL_DIR) {
    union() {

            // ── Sleeve tube + keys ────────────────────────────────────────────
            stator_sleeve_body();

            // ── Stator hub ring ───────────────────────────────────────────────
            stator_hub();

            // ── 11 twisted inter-stage stator fins ────────────────────────────
            for (i = [0 : N_FINS - 1]) {
                stator_fin(i * (360 / N_FINS), swirl_dir);
            }

    }
}


// =============================================================================
// ── Render call ───────────────────────────────────────────────────────────────
// =============================================================================
edf_stator_sleeve(swirl_dir = SWIRL_DIR);


// =============================================================================
// ── Print specifications ──────────────────────────────────────────────────────
// =============================================================================
// Material    : CF-PETG (CarbonX PETG+CF or equivalent)
// Layer height: 0.15 mm
// Walls       : 4 perimeter walls (minimum)
// Infill      : 40% gyroid
// Nozzle      : Hardened-steel required for CF-PETG
// Orientation : Forward face (Z=0 end) down; no supports required.
// Quantity    : 1 per nacelle (identical for port and starboard — SWIRL_DIR
//               is the only difference; re-render with -D SWIRL_DIR=-1 for stbd).
//
// Post-print checks
// -----------------
//   1. OD = 55.0 mm ± 0.2 mm at forward, mid, and aft stations.
//      Must slide into nacelle enlarged bore (≈55.4 mm) without binding.
//   2. Bore ID = 50.0 mm ± 0.2 mm.
//   3. Hub bore = 4.0 mm ± 0.1 mm (ESC wire routing).
//   4. Key width = 3.0 mm ± 0.1 mm; verify alignment with nacelle bore slots.
//   5. Stator fin edges: lightly sand if bridging creates rough surface.
//   6. Sleeve forward face must seat flush against nacelle bore shoulder at
//      Z = 90 mm (no gap visible when sleeve is fully inserted).
//
// Render commands
// ---------------
//   Port nacelle (CW stator from intake):
//     openscad -o edf_stator_sleeve_port.stl edf_stator_sleeve.scad -D SWIRL_DIR=1
//   Starboard nacelle (CCW stator):
//     openscad -o edf_stator_sleeve_stbd.stl edf_stator_sleeve.scad -D SWIRL_DIR=-1
