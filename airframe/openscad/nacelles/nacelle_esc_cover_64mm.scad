// =============================================================================
// nacelle_esc_cover_64mm.scad — Rev U — 64 mm pod ESC bay access cover (four handed parts)
// =============================================================================
// License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
//
// Author : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (GitHub Stab-Rabbit-coding) — owner.
// Code   : Claude (Claude Opus 5.5, Anthropic) under the author's direction, 2026-11-21,
//          per AGENTS.md section 3.  Derivative of nacelle_esc_cover.scad (Rev T4c, Claude Opus 5),
//          which carries the design rationale (why a cover, why authored in place, handing,
//          print orientation) and is unchanged.
// WBS    : airframe/wings-nacelles/WBS.md NAC-64-GEOM-03 (Rev U plan S4).
//
// WHY THIS FILE
// -------------
// nacelle_esc_cover.scad builds the cover from the UNSCALED 50 mm skin grid (HOLLOW_SKIN_* at
// x1.00, HOLLOW_Z unstretched) and the 50 mm bay stations in nacelle_esc_bay.scad.  The 64 mm pod
// cuts its rebate from radial_k_grid() of that skin (RADIAL_K = P64_K, x1.06 uniform enlargement),
// at stretched stations (hollow_zs(), ESC_BAY_Z0 92.79) — so a 50 mm cover cannot land in a 64 mm
// rebate.  Rather than copy the 64 mm values a second time, this file INCLUDES the pod wrapper
// with POD_AUTORENDER = false and builds the cover from the pod's own ESC_SKIN, hollow_zs(),
// footprint, boss and louvre definitions.  The cover and the rebate it lands in therefore come
// from one source and cannot drift.
//
// FRAME: nacelle-local (duct axis +Z, intake Z = 0), authored IN PLACE on the pod, as the 50 mm
// cover is.  The hull-frame placement is the pod's own bake transform (tools/bake_hull_frame.py);
// print orientation is a slicer choice (inner face down, see the 50 mm file).
//
// RENDER — the same three side flags as the pod it closes, plus the bay index:
//   stbd A: openscad -o nacelle_esc_cover_64mm_stbd_a.stl nacelle_esc_cover_64mm.scad \
//           -D SWIRL_DIR=1 -D PYLON_SIDE=1 -D NACELLE_SIDE=1 -D RENDER_BAY=0
//   stbd B: ... -D RENDER_BAY=1
//   port A: ... -D SWIRL_DIR=-1 -D PYLON_SIDE=-1 -D NACELLE_SIDE=-1 -D RENDER_BAY=0
//   port B: ... -D RENDER_BAY=1
// Bay A = ESC_BAY_AZ[0], bay B = ESC_BAY_AZ[1].
// =============================================================================

include <nacelle_pod_64mm_tandem.scad>
P64_NO_RENDER  = true;    // the pod wrapper renders unless this is defined
RENDER_BAY     = 0;       // 0 = bay A (ESC_BAY_AZ[0]), 1 = bay B (ESC_BAY_AZ[1])

COVER_AZ = ESC_BAY_AZ[RENDER_BAY];

// The material between the mould line and d_in inside it, on the pod's own scaled skin.
module cover64_shell(d_out, d_in) {
    difference() {
        grid_solid(offset_grid(ESC_SKIN, d_out), hollow_zs(), HOLLOW_N_AZ);
        grid_solid(offset_grid(ESC_SKIN, d_in), hollow_zs(), HOLLOW_N_AZ);
    }
}

// Louvre field: the aft-only inlet of the aspirated bay (nacelle_esc_bay.scad "Cooling").
function cover64_louvre_span() = (ESC_LOUVRE_N - 1) * ESC_LOUVRE_P + ESC_LOUVRE_W;
function cover64_louvre_z0()   = ESC_BAY_Z1 - ESC_LEDGE_W / 2 - cover64_louvre_span();

module cover64_louvres() {
    for (i = [0 : ESC_LOUVRE_N - 1])
        rotate([0, 0, COVER_AZ + esc_a_pow()])
            translate([ESC_MOUNT_R, -ESC_LOUVRE_L / 2, cover64_louvre_z0() + i * ESC_LOUVRE_P])
                cube([40, ESC_LOUVRE_L, ESC_LOUVRE_W]);
}

module cover64_mesh_rebate() {
    rotate([0, 0, COVER_AZ + esc_a_pow()])
        translate([ESC_MOUNT_R, -(ESC_LOUVRE_L / 2 + ESC_MESH_MARGIN),
                   cover64_louvre_z0() - ESC_MESH_MARGIN])
            cube([40, ESC_LOUVRE_L + 2 * ESC_MESH_MARGIN,
                  cover64_louvre_span() + 2 * ESC_MESH_MARGIN]);
}

module nacelle_esc_cover_64mm() {
    assert(ESC_COVER_T > ESC_CBORE_DEPTH + 1.0,
           "counterbore leaves under 1 mm of material beneath the screw head");
    assert(cover64_louvre_z0() > ESC_BAY_Z0,
           "louvre field runs forward of the bay window");
    difference() {
        // The cover drops into the pod's rebate (same footprint, less the fit clearance), and
        // its outer face is the pod's scaled mould line.
        intersection() {
            cover64_shell(0.0, ESC_COVER_T);
            esc_bay_footprint(COVER_AZ, 60.0, ESC_LEDGE_W - ESC_COVER_FIT);
        }
        esc_boss_cylinders(COVER_AZ, ESC_SCREW_D);
        intersection() {
            cover64_shell(-0.5, ESC_CBORE_DEPTH);
            esc_boss_cylinders(COVER_AZ, ESC_CBORE_D);
        }
        cover64_louvres();
        intersection() {
            cover64_shell(ESC_COVER_T - ESC_MESH_REBATE, ESC_COVER_T + 1.0);
            cover64_mesh_rebate();
        }
    }
}

nacelle_esc_cover_64mm();
