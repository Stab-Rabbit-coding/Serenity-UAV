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
RENDER_BAY     = 0;       // index into ESC_BAYS: 0 / 1 = ESC A power / logic (flat covers),
                          //   2 / 3 = ESC B power / logic (H1 housing-covers)

// ESC B: the generator's housing solid covers both B bays as one styled shell.  It is cut into
// TWO covers by a radial half-plane midway between the two boards (H1_SPLIT_AZ), because one
// cover over two boards 58 deg apart cannot be lifted off in any single direction (checked
// 2026-11-22: ~200 mm3 of board interference along every direction tried).  Each cover lifts
// along its own bay's panel bisector, which carries it AWAY from the split plane, so either can
// come off first.
H1_SOLID       = "../../stls/nacelles/esc/h1_esc_housing_64mm_solid.stl";  // reference input,
                          //   tools/nacelle64_esc_housing.py --out (regenerate, never hand-edit)
ESC_COVER_CLR  = 0.4;     // [mm] running clearance board -> cover (as the housing generator)
H1_BAYS        = [for (b = ESC_BAYS) if (bay_is_housed(b)) b];
H1_LIFT_T      = 15.0;    // [mm] removal stroke the hollow is swept along
// split: midway between the power bay's far panel edge and the logic bay's near one (seat radius)
H1_SPLIT_AZ    = (bay_az(H1_BAYS[0]) + 2 * esc_a_pow() + bay_az(H1_BAYS[1]) - 2 * esc_a_sig()) / 2;

COVER_BAY = ESC_BAYS[RENDER_BAY];
COVER_AZ  = bay_az(COVER_BAY);
// lift direction of a cover: the bisector of its two panels' normals
function cover_lift_az(b) = bay_az(b) + (esc_a_pow() - esc_a_sig()) / 2;

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

// ── Partition between neighbouring covers ────────────────────────────────────────────────────
// Adjacent G1 bays' landing bands overlap (the pod rebates simply merge), so each cover is cut
// to its own side of every neighbour (overlaps found 2026-11-22: 31-151 mm3): by a Z-plane
// midway between two axially separate bays, else by a radial half-plane midway between the
// facing panel edges.  The two H1 halves use the same rule (= H1_SPLIT_AZ).
function wrap180(a) = a - 360 * floor((a + 180) / 360);
module half_plane_az(lo) {             // the 180 deg wedge [lo, lo + 180]
    translate([0, 0, -1]) linear_extrude(260)
        polygon(concat([[0, 0]], [for (i = [0 : 36]) let(t = lo + 180 * i / 36)
                                     [90 * cos(t), 90 * sin(t)]]));
}
// Radial split when the two bays' panels do not overlap in azimuth (the usual case, and the
// one the H1 halves need: a Z-plane between ESC B's bays handed the logic housing's forward
// ramp to the power cover as a loose piece); a Z-plane only when they do.
function cover_split(b, o) =
    let(d = wrap180(bay_az(o) - bay_az(b)),
        edge_b = d > 0 ? bay_az(b) + 2 * esc_a_pow() : bay_az(b) - 2 * esc_a_sig(),
        edge_o = d > 0 ? bay_az(o) - 2 * esc_a_sig() : bay_az(o) + 2 * esc_a_pow(),
        gap = d > 0 ? wrap180(edge_o - edge_b) : wrap180(edge_b - edge_o))
    [d, gap, edge_b + wrap180(edge_o - edge_b) / 2];
module cover_side_of(b, o) {
    c = cover_split(b, o);
    if (c[1] > 0)
        half_plane_az(c[0] > 0 ? c[2] - 180 : c[2]);
    else if (bay_z1(b) < bay_z0(o))
        translate([-100, -100, -1]) cube([200, 200, 1 + (bay_z1(b) + bay_z0(o)) / 2]);
    else
        translate([-100, -100, (bay_z1(o) + bay_z0(b)) / 2]) cube([200, 200, 300]);
}
module cover_region(b) {
    intersection_for(o = [for (x = ESC_BAYS) if (x != b) x]) cover_side_of(b, o);
}

module nacelle_esc_cover_64mm() {
    assert(!bay_is_housed(COVER_BAY), "a housed bay takes the H1 housing-cover");
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
            cover_region(COVER_BAY);
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

// ── ESC B housing-cover (H1) ─────────────────────────────────────────────────────────────────
// The board envelope + running clearance, per housed bay (the cover's hollow).
module h1_board_clearance(b) {
    env = bay_env(b) + ESC_COVER_CLR;
    union() {
        esc_panel_slab(ESC_W_POWER + 2 * ESC_COVER_CLR, bay_az(b) + esc_a_pow(),
                       ESC_MOUNT_R - 1.0, ESC_MOUNT_R + env,
                       bay_z0(b) - ESC_COVER_CLR, bay_z1(b) + ESC_COVER_CLR);
        esc_panel_slab(ESC_W_SIGNAL + 2 * ESC_COVER_CLR, bay_az(b) - esc_a_sig(),
                       ESC_MOUNT_R - 1.0, ESC_MOUNT_R + env,
                       bay_z0(b) - ESC_COVER_CLR, bay_z1(b) + ESC_COVER_CLR);
        intersection() {
            esc_fold_sector(b, ESC_MOUNT_R + env, ESC_COVER_CLR);
            translate([0, 0, bay_z0(b) - ESC_COVER_CLR])
                cylinder(r = ESC_MOUNT_R + env, h = bay_z1(b) - bay_z0(b) + 2 * ESC_COVER_CLR,
                         $fn = 180);
        }
    }
}

// the board clearance swept back along the lift: what the cover must not contain as it lifts
module h1_hollow(b) {
    a = cover_lift_az(b);
    hull() {
        h1_board_clearance(b);
        translate(-H1_LIFT_T * [cos(a), sin(a), 0]) h1_board_clearance(b);
    }
}

module nacelle_esc_housing_cover_64mm(b) {
    assert(len(H1_BAYS) == 2, "ESC B should have exactly two housed bays");
    assert(bay_is_housed(b), "not a housed bay");
    intersection() { difference() {
        union() {
            // flange: the flat-cover plate in this bay's rebate
            intersection() {
                cover64_shell(0.0, ESC_COVER_T);
                esc_bay_footprint(b, 60.0, ESC_LEDGE_W - ESC_COVER_FIT);
            }
            // this bay's side of the canonical-styled housing, standing ESC_COVER_FIT off the skin
            // outside the rebate (seats on the flange, not face-to-face on the curved skin); its
            // forward feather edge starts at the doubler band, ahead of which the 0.25 mm
            // stand-off left loose slivers (Z 57-62, 2026-11-22)
            intersection() {
                import(H1_SOLID, convexity = 10);
                translate([0, 0, bay_z0(b) - ESC_LEDGE_W - 3.0]) cylinder(r = 90, h = 200);
            }
        }
        difference() {
            grid_solid(offset_grid(ESC_SKIN, -ESC_COVER_FIT), hollow_zs(), HOLLOW_N_AZ);
            esc_bay_footprint(b, 60.0, ESC_LEDGE_W - ESC_COVER_FIT);
        }
        h1_hollow(b);
        esc_boss_cylinders(b, ESC_SCREW_D);
        // spotfaces: every screw head bears on the flange, at the skin
        difference() {
            esc_boss_cylinders(b, ESC_CBORE_D);
            grid_solid(ESC_SKIN, hollow_zs(), HOLLOW_N_AZ);
        }
    }
    cover_region(b); }
}

if (bay_is_housed(COVER_BAY)) nacelle_esc_housing_cover_64mm(COVER_BAY);
else nacelle_esc_cover_64mm();
