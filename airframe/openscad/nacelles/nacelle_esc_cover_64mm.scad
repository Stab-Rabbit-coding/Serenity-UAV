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
// RENDER — the same three side flags as the pod it closes, plus the bay index into the pod's
// ESC_BAYS table (G1, 2026-11-22).  Only the FLAT-cover bays have a cover here: ESC A power
// (RENDER_BAY = 0, with the louvre field) and ESC A logic (RENDER_BAY = 1, plain: logic bays have
// no discharge ports).  ESC B's two bays are closed by the H1 housings
// (tools/nacelle64_esc_housing.py, WBS NAC-64-ESC-BLISTER).
//   openscad -o nacelle_esc_cover_64mm_a_power.stl nacelle_esc_cover_64mm.scad -D RENDER_BAY=0
//   openscad -o nacelle_esc_cover_64mm_a_logic.stl nacelle_esc_cover_64mm.scad -D RENDER_BAY=1
// The other pod's covers are their X-mirror, as the pod is (tools/prep_nacelle_64_bake.py).
//
// G1 CHANGES (2026-11-22): cover 1.5 mm (SLS material study; pod ESC_COVER_T), no counterbore
// (button heads proud), louvres 11 x 1.2 x 18 mm, no mesh rebate (screen bonded flat), and the
// cover restores any dorsal-shroud material the bay rebate removed, so it finishes flush with
// the shroud where the shroud stands proud of the canonical skin (ESC A power, az 226-238).
// =============================================================================

include <nacelle_pod_64mm_tandem.scad>
P64_NO_RENDER  = true;    // the pod wrapper renders unless this is defined
RENDER_BAY     = 0;       // index into ESC_BAYS: 0 = ESC A power, 1 = ESC A logic

COVER_BAY = ESC_BAYS[RENDER_BAY];
COVER_AZ  = bay_az(COVER_BAY);
assert(!bay_is_housed(COVER_BAY), "this bay is closed by an H1 housing, not a flat cover");

// The material between the mould line and d_in inside it, on the pod's own scaled skin.
module cover64_shell(d_out, d_in) {
    difference() {
        grid_solid(offset_grid(ESC_SKIN, d_out), hollow_zs(), HOLLOW_N_AZ);
        grid_solid(offset_grid(ESC_SKIN, d_in), hollow_zs(), HOLLOW_N_AZ);
    }
}

// Louvre field: the aft-only inlet of the aspirated bay (nacelle_esc_bay.scad "Cooling").
function cover64_louvre_span() = (ESC_LOUVRE_N - 1) * ESC_LOUVRE_P + ESC_LOUVRE_W;
function cover64_louvre_z0()   = bay_z1(COVER_BAY) - ESC_LEDGE_W / 2 - cover64_louvre_span();

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
    assert(ESC_COVER_T >= ESC_CBORE_DEPTH + 1.5,
           "counterbore leaves under the 1.5 mm study floor beneath the screw head");
    assert(!bay_is_power(COVER_BAY) || cover64_louvre_z0() > bay_z0(COVER_BAY),
           "louvre field runs forward of the bay window");
    assert(ESC_LOUVRE_L <= ESC_W_POWER - 2.0, "louvre slots run past the power-panel window");
    difference() {
        // The cover drops into the pod's rebate (same footprint, less the fit clearance), and
        // its outer face is the pod's scaled mould line -- or the dorsal shroud where that
        // stands proud (the rebate cut it away too, see edf1_nacelle_spider()).
        intersection() {
            union() {
                cover64_shell(0.0, ESC_COVER_T);
                intersection() {
                    $nsv_side = PYLON_SIDE;
                    nsv_pod_adds();
                    difference() {
                        cylinder(r = 80, h = 400);
                        grid_solid(offset_grid(ESC_SKIN, ESC_COVER_T), hollow_zs(), HOLLOW_N_AZ);
                    }
                }
            }
            esc_bay_footprint(COVER_BAY, 60.0, ESC_LEDGE_W - ESC_COVER_FIT);
        }
        esc_boss_cylinders(COVER_BAY, ESC_SCREW_D);
        if (ESC_CBORE_DEPTH > 0) intersection() {
            cover64_shell(-0.5, ESC_CBORE_DEPTH);
            esc_boss_cylinders(COVER_BAY, ESC_CBORE_D);
        }
        if (bay_is_power(COVER_BAY)) cover64_louvres();
        if (bay_is_power(COVER_BAY) && ESC_MESH_REBATE > 0) intersection() {
            cover64_shell(ESC_COVER_T - ESC_MESH_REBATE, ESC_COVER_T + 1.0);
            cover64_mesh_rebate();
        }
    }
}

nacelle_esc_cover_64mm();
