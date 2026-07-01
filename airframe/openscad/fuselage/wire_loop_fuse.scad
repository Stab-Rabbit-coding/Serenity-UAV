// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   This part is modeled in a PART-LOCAL frame (load axis = local Z);
//   NOT a primary-component STL; do NOT bake with bake_hull_frame.py.
// ===========================================================================
// ===========================================================================
// wire_loop_fuse.scad
// Serenity UAV -- Rev R4 -- Strong-Leg per-arm ductile wire-loop crash fuse
// *** RETIRED 2026-06-20, superseded by Rev R5 (wire_brace_leg.scad) ***
// The closed-ring fuse below was judged hard to manufacture/field-replace
// (precision wire winding + separate tabs). Rev R5 replaces it with a much
// simpler single-bend "bowed wire" strut (see wire_brace_leg.scad) and also
// replaces the forked CF-PETG arms entirely with FOUR such wires (2 spring,
// 2 ductile) rather than fusing only the arm tips. Kept here for reference
// only -- see docs/LANDING_GEAR_ANALYSIS.md Rev R5 for the current design.
// ===========================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Project : Serenity-class Tilt-Rotor UAV (24-inch scale, Firefly TV ship)
// License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date    : 2026-06-20
// Revision: Rev R3
//
// Description
// -----------
// One ductile-wire crash fuse is installed in series between each Strong-Leg
// arm tip and its hull boss (2 per leg, 8 per aircraft), replacing the rigid
// CF-PETG spigot that previously plugged directly into the boss bore.  See
// docs/LANDING_GEAR_ANALYSIS.md Rev R3, section 4/6 for the structural
// derivation of every dimension below.
//
// Geometry: a closed wire ring (mean radius RING_R, wire diameter WIRE_D),
// oriented with its long axis along the arm's load direction, with a short
// straight mounting tab at the top (into the hull boss bore) and bottom
// (into the CF-PETG arm tip socket).  Under axial overload the ring
// progressively flattens -- four plastic hinges form (two at the load
// points, two at 90 degrees from them) -- absorbing energy as it deforms.
// The flattened shape is a visible, unambiguous "this fuse has fired,
// replace it" field-inspection indicator.
//
// Sizing (per docs/LANDING_GEAR_ANALYSIS.md Rev R3 SS4.4/4.6):
//   Target ductile-metal collapse force  ~= 2,000 N per fuse
//   Target absorbed energy at that force ~= 14 J per fuse (full per-leg
//     worst-case energy, sized independently per arm as a conservative
//     margin against uneven/asymmetric landings -- NOT a 50/50 split)
//   WIRE_D  = 4.0 mm    (solid round ductile spring-steel wire, tempered
//                         for plastic ductility, NOT full-hard)
//   RING_R  = 12.0 mm   (mean ring radius; ring OD ~= 28 mm)
//   Available crush stroke ~= RING_R = 12 mm; only ~7 mm is used to reach
//     the 14 J target, leaving reserve stroke before the ring bottoms out.
//
// This is a hand-calculated STARTING POINT for prototyping, not a certified
// design -- see TODO.md LG-14/LG-15 for the required coupon/drop testing.
//
// Render commands
// ----------------
//   openscad -D 'PART="nominal"'  -o wire_loop_fuse_nominal.stl  wire_loop_fuse.scad
//   openscad -D 'PART="deformed"' -o wire_loop_fuse_deformed.stl wire_loop_fuse.scad
// ===========================================================================

$fn = 64;

// ---------------------------------------------------------------------------
// Parameters (mm unless noted)
// ---------------------------------------------------------------------------
WIRE_D      = 4.0;      // ductile wire diameter
RING_R      = 12.0;     // mean ring radius, undeformed
RING_MINOR_FACTOR_DEFORMED = 0.30;  // deformed ring minor-axis shrink factor
                                     // (0.30 = ring has crushed to 30% of its
                                     //  original minor-axis height -- a
                                     //  clearly visible "fired" flat-oval shape)
TAB_LEN     = 8.0;      // straight mounting tab length, each end
TAB_W       = 6.0;      // mounting tab width (flat, for a through-pin)
TAB_T       = 3.0;      // mounting tab thickness
PIN_D       = 2.5;      // mounting pin through-hole diameter (each tab)

PART = "nominal";   // "nominal" | "deformed" -- override with -D on the CLI

// ---------------------------------------------------------------------------
// Mounting tab: a short flat tongue with a through-pin hole, at one end of
// the ring along the local Z (load) axis.
// ---------------------------------------------------------------------------
module mount_tab() {
    difference() {
        translate([-TAB_W/2, -TAB_T/2, 0])
            cube([TAB_W, TAB_T, TAB_LEN]);
        translate([0, 0, TAB_LEN/2])
            rotate([90, 0, 0])
                cylinder(h = TAB_T * 3, d = PIN_D, center = true);
    }
}

// ---------------------------------------------------------------------------
// Wire ring: a torus-like loop lying in the local X-Z plane (hole axis = Y),
// so the ring's plane contains local Z -- the arm's load direction runs
// through the ring along Z, in line with the mounting tabs.
// minor_factor scales the ring's Z extent (the load axis) to model
// post-crush flattening: 1.0 = nominal (circular ring), <1.0 = the ring has
// been crushed shorter along Z while its X extent (perpendicular to the
// load) is left at full size, matching how a ring flattens under a
// diametral load -- short along the load axis, bulging perpendicular to it.
// ---------------------------------------------------------------------------
module wire_ring(minor_factor) {
    scale([1, 1, minor_factor])
        rotate([90, 0, 0])
            rotate_extrude($fn = 96)
                translate([RING_R, 0, 0])
                    circle(d = WIRE_D, $fn = 24);
}

// ---------------------------------------------------------------------------
// Full fuse assembly: ring + top/bottom mounting tabs, oriented with the
// ring's major (load) axis along local Z, tabs centred on that axis.
// ---------------------------------------------------------------------------
module wire_loop_fuse(minor_factor) {
    ring_half_len = RING_R * minor_factor;   // deformed ring is shorter overall
    union() {
        wire_ring(minor_factor);
        translate([0, 0,  ring_half_len])
            mount_tab();
        translate([0, 0, -ring_half_len - TAB_LEN])
            mount_tab();
    }
}

// ---------------------------------------------------------------------------
// PART selector
// ---------------------------------------------------------------------------
if (PART == "nominal") {
    wire_loop_fuse(1.0);
} else if (PART == "deformed") {
    wire_loop_fuse(RING_MINOR_FACTOR_DEFORMED);
} else {
    assert(false, str("Unknown PART: ", PART, " -- expected \"nominal\" or \"deformed\""));
}
