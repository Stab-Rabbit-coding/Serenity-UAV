// _export_pivot_slab.scad — one-shot cache export (work section, 2026-07-18).
// Full-radius Z-slab of the true (imported) port nacelle shell around the pivot
// station (Z = 104.5), so the rotating-spar features (keyed hub, duct-wall
// bosses, stator tunnel) can be developed against real canonical geometry
// without re-CSG-ing the whole nacelle each render.  NOT a build artifact.
//
// In THIS slab frame the spar/tilt axis runs along X (spanwise) at Y = 0,
// Z = 104.5 (the pivot/CG), piercing both X duct walls.  The Z-slab imports at
// the duct-axis origin, so the spar axis is the local X-axis through (0, 0, 104.5).
BORE_CX_L = 42.72; BORE_CY = 190.79;
Z_LO = 85; Z_HI = 125;                         // ±~20 mm around pivot Z=104.5
intersection() {
    translate([-BORE_CX_L, BORE_CY, 0])
        import("../../stls/nacelles/eng_left_shell24_50mm_repaired.stl", convexity = 4);
    translate([-45, -45, Z_LO]) cube([90, 90, Z_HI - Z_LO]);   // FULL width (both X faces)
}

// ── ROTATING half of the wing/nacelle tilt-angle Hall sensor (Rev R2c) ────────
// docs/TILT_SPAR_ANALYSIS.md §1/§3.5 ; fixed (sensor) half is on the wing tip
// pad (airframe/openscad/wings/wings_s1223_revo.scad).  A diametric RING magnet,
// coaxial with the spar, is carried on a NON-FERROUS printed hub keyed to the
// rotating spar at the nacelle INBOARD face; it presents a rotating field to the
// off-axis wing-tip IC across HALL_AIR_GAP.
//
// STEEL-SPAR MITIGATION (the reason this hub exists): the 4130/17-4 PH spar is
// ferromagnetic and runs through the ring centre.  The printed hub (CF-PETG —
// carbon fibre is NON-ferromagnetic) stands the ring ID (10 mm) off the 8 mm
// steel with a ≥1 mm non-ferrous wall, and keeps the ring HALL_HUB_STANDOFF
// proud of the steel F688ZZ bearing.  All hub fasteners must be non-ferrous.
// Residual shaft-through distortion is removed by firmware zero-cal (avionics).
// PROVISIONAL — migrate into nacelle_pod_50mm_tandem.scad with the keyed hub.
SPAR_AX_Y       =   0.0;    // [mm] spar axis, slab frame
SPAR_AX_Z       = 104.5;    // [mm] spar axis = pivot/CG station
INBOARD_FACE_X  = -30.0;    // [mm] VERIFY SIGN — nacelle inboard (wing-side) X face
HALL_SPAR_OD    =   8.0;    // [mm] rotating spar OD (keyway hub bore)
HALL_COLLAR_ID  =   8.1;    // [mm] hub bore over spar (slip/bond, keyed)
HALL_RING_OD    =  13.0;    // [mm] diametric ring-magnet OD (matches wing HALL_RING_OD)
HALL_RING_ID    =  10.0;    // [mm] ring-magnet ID (≥1 mm non-ferrous wall over 8 mm spar)
HALL_RING_T     =   2.5;    // [mm] ring-magnet thickness
HALL_HUB_OD     =  16.0;    // [mm] non-ferrous printed hub OD (ring carrier)
HALL_HUB_LEN    =   8.0;    // [mm] hub length along spar (into nacelle from face)
HALL_AIR_GAP    =   1.5;    // [mm] ring-face → wing IC-face axial gap (matches wing)

// Ring-magnet hub (rotating).  Local +Z is built along the spar toward the wing
// (−X here via rotate), so the ring face points at the wing-tip sensor pocket.
module nacelle_hall_ring_hub() {
    // rotate([0,-90,0]) maps local +Z → global −X (toward the wing, inboard).
    translate([INBOARD_FACE_X, SPAR_AX_Y, SPAR_AX_Z]) rotate([0, -90, 0])
        difference() {
            union() {
                // Hub body, extending INTO the nacelle (away from the wing).
                translate([0, 0, -HALL_HUB_LEN])
                    cylinder(r = HALL_HUB_OD / 2, h = HALL_HUB_LEN, $fn = 48);
                // Ring-magnet carrier lip standing HALL_AIR_GAP proud toward wing.
                cylinder(r = HALL_HUB_OD / 2, h = HALL_AIR_GAP + HALL_RING_T, $fn = 48);
            }
            // Spar bore (keyed) through the hub.
            translate([0, 0, -HALL_HUB_LEN - 0.1])
                cylinder(r = HALL_COLLAR_ID / 2, h = HALL_HUB_LEN + HALL_AIR_GAP + HALL_RING_T + 0.2, $fn = 32);
            // Ring-magnet seat pocket, opening toward the wing (local +Z face).
            translate([0, 0, HALL_AIR_GAP])
                cylinder(r = HALL_RING_OD / 2 + 0.1, h = HALL_RING_T + 0.2, $fn = 48);
        }
}

// Preview: the rotating hub shown against the canonical slab (not booleaned in —
// keeps this sandbox light; final merge happens in nacelle_pod_50mm_tandem.scad).
color("SteelBlue") nacelle_hall_ring_hub();
