// =============================================================================
// edf_stator_sleeve.scad
// Serenity UAV — Rev A — EDF Inter-stage Stator Sleeve
// =============================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Project : Serenity-class Tilt-Rotor UAV (24-inch scale, Firefly TV ship)
// License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date    : 2026-05-29
// Revision: Rev A
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

// ── Stator geometry (nacelle 1.25× scale values converted to sleeve-local Z) ──
// Sleeve-local Z = nacelle Z − SLEEVE_Z_START
STATOR_Z_BOT_L  =   3.75;  // [mm] stator bottom (nacelle 93.75 − 90.0)
STATOR_Z_TOP_L  =  28.75;  // [mm] stator top    (nacelle 118.75 − 90.0)
N_FINS          =  11;     // [count] inter-stage stator fins
FIN_THICKNESS   =   2.0;   // [mm] fin tangential thickness
VANE_ANGLE_DEG  =  33.0;   // [deg] fin angle from axial (tuned to 50 mm 6S tip swirl)

// ── Hub dimensions ─────────────────────────────────────────────────────────────
// Hub bore routes EDF1 ESC wires through stator zone to inter-stage space.
S_HUB_R         =   8.0;   // [mm] hub outer radius (16 mm OD)
S_HUB_BORE_R    =   2.0;   // [mm] hub bore radius   ( 4 mm ID)

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
        for (angle = [0, 120, 240]) {
            rotate([0, 0, angle])
            translate([SLEEVE_OD / 2, -SLEEVE_KEY_W / 2, 0])
                cube([SLEEVE_KEY_H, SLEEVE_KEY_W, SLEEVE_L]);
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
