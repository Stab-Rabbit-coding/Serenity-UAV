// gear_box_canonical_concept.scad -- CONCEPT envelope of the canonical
// landing-gear box (cargo-flank "gear sponson") and its leg-support pillars.
//
// STATUS: CONCEPT / appearance study only (2026-11-01).  NOT integrated:
// no keep-outs, no bolt pattern, no wall/shell, no mass.  It exists so the
// owner can approve the LOOK before the integration work in
// docs/plans/2026-11-01-001-feat-canonical-gear-box-plan.md.
//
// Problem it answers (owner, 2026-11-01): the Rev R6/A1B bays are open bolt
// frames on the 25 deg sponson panel; the thigh hub hangs in free air below
// them, so there is a visible gap between the bottom of each leg support and
// the hull, and the bay reads as a box added onto a different design.
//
// Canonical form, read from Nick Henning's model [REF-CAD-HENNING]:
//   * nick-henning-uvdisplay-wing.jpg -- the stub wing IS the top plate; the
//     gear box hangs under it as a faceted block whose outboard face leans in
//     toward a bevelled lower chine, with recessed panels and an angled hatch.
//   * nick-henning-close-gear-combine.jpg -- each thigh is SLEEVED in a square
//     leg-support pillar that lands on the box; the thigh emerges from the
//     pillar mouth, so support and hull read as one structure.
//   * nick-henning-uvdisplay-gear.jpg -- the upper-leg housing is a square
//     tube coaxial with the thigh.
//
// Frame: aircraft datum R2 (tools/hull_datums.py): X lateral (port = +X),
// Y aft, Z up, mm.  Built for PORT and mirrored about X_CL for starboard.
// Corner poses are COPIED from merge_cargo_interior.py LG_CORNERS /
// canonical_leg_r6_3_0in.scad CORNERS (R2) -- the integration step shall
// read them from one source instead (plan U2).
//
// Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
// Stab-Rabbit-coding, per AGENTS.md AI attribution.
// License: CERN-OHL-P-2.0 (hardware source) -- see repo LICENSE files.

PART = "both";          // "port" | "stbd" | "both"
include <../hull_datums.scad>   // X_CL etc. (GENERATED from tools/hull_datums.py)

// [hip_x, hip_y, hip_z, swing_azimuth_deg] -- port rows, R2
FORE = [54.95, 289.70, 118.0, -22.4];
AFT  = [77.61, 405.66, 118.0,  28.0];

KNEE_L   = [59, 0, -66];  // leg-local knee centre (canonical_leg_r6_3_0in KNEE)
FLEX_MAX = 26;            // deg, gear stroke swept by the bay check

// --- box section (X, Z) at the full-depth stations --------------------------
BOX_Z_BOT   = 80.0;       // belly plane
BOX_Z_TOP   = 133.0;      // wing-root underside (wing is the canonical top plate)
// Owner 2026-11-01: no shelf in front of the wing root -- the box top is a
// face sloping up-inboard from the outboard face edge at TOP_SLOPE, so it
// runs INTO the hull skin (a clean skin joint) wherever the wing is not
// above it.  Under the wing the top is then trimmed to the wing's own
// underside contour by tools/gear_box_concept_fit.py.
TOP_SLOPE   = 45;         // deg above horizontal
BOX_X_IN    = 56.0;       // inboard edge -- outboard of the door aperture (X 52.25)
BOX_X_FACE_T = 96.0;      // outboard face, top
BOX_X_FACE_B = 92.0;      // outboard face, bottom (face leans in, as canon)
BOX_Z_CHINE = 100.0;      // top of the bevelled lower chine
BOX_X_CHINE_B = 72.0;     // chine meets the bottom

Y_FWD_TIP = 262.0;        // fore face toe (sloped front face)
Y_FWD     = 280.0;        // full section begins
Y_AFT     = 424.0;        // full section ends
Y_AFT_TIP = 433.0;        // aft face, stops short of the cargo/middle collar (434.7)

// --- leg-support pillar (square sleeve coaxial with the static thigh) -------
PIL_W_SWING = 40.0;       // across the thigh, in the swing plane
PIL_W_PIN   = 30.0;       // along the hip pin
PIL_UP      = 30.0;       // run up/inboard of the hip (buried in the box)
PIL_DOWN    = 90.0;       // run down the thigh from the hip (clipped to the box)
SLOT_SWING  = 34.0;       // thigh cluster clearance (2 x O14 @ 18 + 2 mm)
SLOT_PIN    = 22.0;       // lug 14 + 2 x 4 mm, at the hip (narrow end)
// Owner 2026-11-01: the bay opening is TRAPEZOIDAL, as canon, and stays an
// OPEN slot.  It flares along the pin axis from SLOT_PIN at the hip to
// SLOT_PIN_MOUTH where the thigh leaves the box, so on the box face it reads as
// a trapezoid wide at the bottom (Henning close-gear: the leg recesses widen
// toward the chine).  34 = the Rev R6 aperture head width (BAY_APER_W_TOP).
SLOT_PIN_MOUTH = 34.0;
SLOT_FLARE_L   = 70.0;    // mm down the thigh over which the flare runs

function unit(v) = v / norm(v);
THIGH_ANG = atan2(-KNEE_L[2], KNEE_L[0]);   // 48.2 deg below local +x

module section(xs, xin = BOX_X_IN) {
    // xs scales the section outboard of BOX_X_IN (end tapers); xin is the
    // inboard edge (BOX_X_IN where the doors are, BOX_X_IN_FWD ahead of them)
    function sx(x) = BOX_X_IN + (x - BOX_X_IN) * xs;
    polygon([[xin, BOX_Z_BOT], [sx(BOX_X_CHINE_B), BOX_Z_BOT],
             [sx(BOX_X_FACE_B), BOX_Z_CHINE], [sx(BOX_X_FACE_T), BOX_Z_TOP],
             [xin, BOX_Z_TOP + (sx(BOX_X_FACE_T) - xin) * tan(TOP_SLOPE)]]);
}

module slab(y, xs, zlift = 0, xin = BOX_X_IN) {
    // a 0.01 mm slab of the section at station y; zlift raises the bottom
    translate([0, y, 0]) rotate([90, 0, 0])
        linear_extrude(0.01, center = true)
            intersection() { section(xs, xin);
                             translate([0, BOX_Z_BOT + zlift]) square([200, 200]); }
}

// Forward fairing (2026-11-01, owner: CF plates FLUSH; where canon cannot be
// exact, match the ship's character).  The fore hip sits at the box's
// inboard edge, in the concave notch behind the bridge neck (hull open
// between Z ~100 and ~150 at Y 280-300, X 41-56).  No strut azimuth packages
// the 55 mm A1B members there flush (sweep 2026-11-01, plan U3).  Ahead of
// the door aperture (Y 304.7) the box no longer has to clear the doors, so
// its inboard edge comes in to BOX_X_IN_FWD and its 45 deg top runs on into
// the upper hull skin -- the notch becomes a faceted cheek block, the same
// chamfered vocabulary as the Henning gear box, instead of an open pocket.
BOX_X_IN_FWD = 36.0;      // mm, meets the lower-flank wall (X 36-54 at Y 280-300)
Y_FAIR_AFT   = 302.0;     // mm, 2.7 mm ahead of the door aperture (304.7)

module fore_fairing() {
    hull() {
        slab(Y_FWD_TIP, 0.55, 18, BOX_X_IN_FWD);
        slab(Y_FAIR_AFT, 1.0, 0, BOX_X_IN_FWD);
    }
}

module box_envelope() {
    hull() {
        slab(Y_FWD_TIP, 0.55, 18);
        slab(Y_FWD, 1.0);
        slab(Y_AFT, 1.0);
        slab(Y_AFT_TIP, 0.75, 8);
    }
}

// Corner local frame: hip origin, +x outboard swing direction, +y pin axis.
module at_corner(c) {
    translate([c[0], c[1], c[2]]) rotate([0, 0, c[3]]) children();
}

PIL_PROUD = 3.0;          // pillar stands proud of the box faces by this much

module pillar(c) {
    // square sleeve along the static thigh, from PIL_UP above the hip to
    // PIL_DOWN down the thigh, CLIPPED to the box grown PIL_PROUD: the pillar
    // is a proud band on the box faces and its mouth lands ON the box (canon:
    // the thigh emerges from the support where it meets the hull -- no gap).
    intersection() {
        minkowski() { box_envelope(); cube(2 * PIL_PROUD, center = true); }
        pillar_raw(c);
    }
}

module pillar_raw(c) {
    at_corner(c) rotate([0, THIGH_ANG, 0])
        translate([-PIL_UP, -PIL_W_PIN / 2, -PIL_W_SWING / 2])
            cube([PIL_UP + PIL_DOWN, PIL_W_PIN, PIL_W_SWING]);
}

module swing_slot(c) {
    // thigh envelope swept 0..FLEX_MAX about the hip pin (flex splays the
    // knee outboard/up: a1b_rot in canonical_leg_r6_3_0in.scad)
    at_corner(c)
        for (f = [0 : FLEX_MAX / 4 : FLEX_MAX - 0.01])
            hull() for (g = [f, f + FLEX_MAX / 4])
                rotate([0, THIGH_ANG - g, 0]) slot_trapezoid();
}

module slot_trapezoid() {
    // slot section along the thigh: SLOT_PIN wide at the hip, flaring to
    // SLOT_PIN_MOUTH at SLOT_FLARE_L, then straight out past the box
    hull() {
        translate([-12, -SLOT_PIN / 2, -SLOT_SWING / 2])
            cube([0.01, SLOT_PIN, SLOT_SWING]);
        translate([SLOT_FLARE_L, -SLOT_PIN_MOUTH / 2, -SLOT_SWING / 2])
            cube([90, SLOT_PIN_MOUTH, SLOT_SWING]);
    }
}

module recess_panel(y0, y1) {
    // shallow canonical panel recess in the outboard face
    translate([BOX_X_FACE_T - 1.2, y0, BOX_Z_CHINE + 4])
        multmatrix([[1, 0, -(BOX_X_FACE_T - BOX_X_FACE_B) / (BOX_Z_TOP - BOX_Z_CHINE), 0],
                    [0, 1, 0, 0], [0, 0, 1, 0]])
            cube([6, y1 - y0, BOX_Z_TOP - BOX_Z_CHINE - 10]);
}

module gear_box_port() {
    difference() {
        union() {
            box_envelope();
            fore_fairing();
            pillar(FORE);
            pillar(AFT);
        }
        swing_slot(FORE);
        swing_slot(AFT);
        recess_panel(318, 352);     // between the bays, canonical inspection panel
        recess_panel(356, 388);
        // keep everything above the belly plane
        translate([-500, 0, BOX_Z_BOT - 100]) cube([1000, 1000, 100]);
    }
}

module mirror_cl() {
    translate([X_CL, 0, 0]) mirror([1, 0, 0]) translate([-X_CL, 0, 0]) children();
}

if (PART == "port" || PART == "both") gear_box_port();
if (PART == "stbd" || PART == "both") mirror_cl() gear_box_port();
