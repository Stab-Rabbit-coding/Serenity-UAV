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

PART = "both";          // "port" | "stbd" | "both" | "envelope_port"
// INSET > 0 builds the INNER solid of the same box (every face moved in by
// INSET, slots and panel recesses grown by INSET so they keep their walls):
// box skin = (PART "port", INSET 0) - (PART "port", INSET = WALL).  Set with
// -D INSET=2 by tools/gear_box_hull_merge.py (2 mm = the hull skin).
INSET = 0;
include <../hull_datums.scad>   // X_CL etc. (GENERATED from tools/hull_datums.py)

// [hip_x, hip_y, hip_z, swing_azimuth_deg] -- port rows, R2
FORE = [54.95, 289.70, 118.0, -65.0];   // 2026-11-01, was -22.4
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

module section(xs, xin = BOX_X_IN, slope = TOP_SLOPE) {
    // xs scales the section outboard of BOX_X_IN (end tapers); xin is the
    // inboard edge (BOX_X_IN where the doors are, BOX_X_IN_FWD ahead of them)
    function sx(x) = BOX_X_IN + (x - BOX_X_IN) * xs;
    offset(delta = -INSET) polygon([[xin, BOX_Z_BOT], [sx(BOX_X_CHINE_B), BOX_Z_BOT],
             [sx(BOX_X_FACE_B), BOX_Z_CHINE], [sx(BOX_X_FACE_T), BOX_Z_TOP],
             [xin, BOX_Z_TOP + (sx(BOX_X_FACE_T) - xin) * tan(slope)]]);
}

module slab(y, xs, zlift = 0, xin = BOX_X_IN, slope = TOP_SLOPE) {
    // a 0.01 mm slab of the section at station y; zlift raises the bottom
    translate([0, y, 0]) rotate([90, 0, 0])
        linear_extrude(0.01, center = true)
            intersection() { section(xs, xin, slope);
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

// With the fore swing azimuth at -65 the CF cheeks stand nearly vertical and
// their tops reach Y ~265 at Z ~178, ahead of the box's full section, so the
// fairing's full section starts at Y_FAIR_FULL with its own sloped toe ahead.
Y_FAIR_TOE  = 256.0;      // mm
Y_FAIR_FULL = 268.0;      // mm
// The cheek tops stand ~60 mm above the hip (Z ~178); a 45 deg top only reaches
// Z ~159 there, so the fairing's top facet is steeper.  Still one sloped
// facet running into the upper skin, as the main box top.
FAIR_TOP_SLOPE = TOP_SLOPE;   // deg (64 read as a tower ahead of the wing; reverted)
FAIR_XS = 0.70;           // outboard scale: face at X ~84 -- the hull is X 41-74 here

module fore_fairing() {
    hull() {
        slab(Y_FAIR_TOE, 0.55, 18, BOX_X_IN_FWD, FAIR_TOP_SLOPE);
        slab(Y_FAIR_FULL, FAIR_XS, 0, BOX_X_IN_FWD, FAIR_TOP_SLOPE);
        slab(Y_FAIR_AFT, FAIR_XS, 0, BOX_X_IN_FWD, FAIR_TOP_SLOPE);
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
        minkowski() { box_envelope(); cube(2 * max(PIL_PROUD - INSET, 0.01), center = true); }
        pillar_raw(c);
    }
}

module pillar_raw(c) {
    at_corner(c) rotate([0, THIGH_ANG, 0])
        translate([-PIL_UP, -PIL_W_PIN / 2 + INSET, -PIL_W_SWING / 2 + INSET])
            cube([PIL_UP + PIL_DOWN, PIL_W_PIN - 2 * INSET, PIL_W_SWING - 2 * INSET]);
}

// Fore leg-support housing (2026-11-01).  With the fore swing azimuth at -65
// the A1B CF cheeks stand at strut az FORE_STRUT_AZ (80: zero contact with the
// TACCO CN2 chin pouch, whose keep-out is the raw pouch).  Their tops sit
// outside the slim fore fairing, so the fore leg gets what Henning's leg
// supports are: a slim faceted pillar rising from the box toward the deck,
// here the cheek outline grown HSG_CLR all round -- nothing wider.
// Cheek geometry from canonical_leg_r6_3_0in.scad a1b_backbone():
// hull of O(A1B_PIN_D + 10) bosses at the hip and at a1b_anchor(+/-1).
FORE_STRUT_AZ = 80;       // deg, = A1B_STRUT_AZ fore
A1B_REACH_C   = 55.0;     // = A1B_REACH
A1B_CRANK_C   = 10.0;     // = A1B_CRANK_R
A1B_BOSS_R    = (4.0 + 10) / 2;   // = (A1B_PIN_D + 10) / 2
A1B_CHEEK_OUT = 14 / 2 + 0.5 + 3.18;  // outer face of a cheek = CHEEK_Y + PLATE_T/2
HSG_CLR       = 3.0;      // mm, housing OUTER face to the plate: 2 mm wall + 1 mm clearance

function azv2(a) = [cos(a), sin(a)];

// Octagon CIRCUMSCRIBING the grown boss (r / cos 22.5), so the faceted
// housing still contains the plate: chamfered corners, the gear box's own
// vocabulary -- a round-topped housing read as foreign to the ship.
module hsg_facet() {
    rotate(22.5) circle(r = (A1B_BOSS_R + HSG_CLR - INSET) / cos(22.5), $fn = 8);
}

module strut_housing(c, saz) {
    u = azv2(saz); n = azv2(saz - 90);
    at_corner(c)
        rotate([90, 0, 0])
            linear_extrude(2 * (A1B_CHEEK_OUT + HSG_CLR - INSET), center = true)
                hull() {
                    hsg_facet();
                    for (sg = [-1, 1])
                        translate(sg * A1B_CRANK_C * n + A1B_REACH_C * u) hsg_facet();
                }
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
        translate([-12 - INSET, -SLOT_PIN / 2 - INSET, -SLOT_SWING / 2 - INSET])
            cube([0.01, SLOT_PIN + 2 * INSET, SLOT_SWING + 2 * INSET]);
        translate([SLOT_FLARE_L, -SLOT_PIN_MOUTH / 2 - INSET, -SLOT_SWING / 2 - INSET])
            cube([90, SLOT_PIN_MOUTH + 2 * INSET, SLOT_SWING + 2 * INSET]);
    }
}

module recess_panel(y0, y1) {
    // shallow canonical panel recess in the outboard face
    translate([BOX_X_FACE_T - 1.2 - INSET, y0 - INSET, BOX_Z_CHINE + 4 - INSET])
        multmatrix([[1, 0, -(BOX_X_FACE_T - BOX_X_FACE_B) / (BOX_Z_TOP - BOX_Z_CHINE), 0],
                    [0, 1, 0, 0], [0, 0, 1, 0]])
            cube([6, y1 - y0 + 2 * INSET, BOX_Z_TOP - BOX_Z_CHINE - 10 + 2 * INSET]);
}

module gear_box_port() {
    difference() {
        union() {
            box_envelope();
            fore_fairing();
            strut_housing(FORE, FORE_STRUT_AZ);
            pillar(FORE);
            pillar(AFT);
        }
        swing_slot(FORE);
        swing_slot(AFT);
        recess_panel(318, 352);     // between the bays, canonical inspection panel
        recess_panel(356, 388);
        // keep everything above the belly plane
        translate([-500, 0, BOX_Z_BOT + INSET - 100]) cube([1000, 1000, 100]);
    }
}

module mirror_cl() {
    translate([X_CL, 0, 0]) mirror([1, 0, 0]) translate([-X_CL, 0, 0]) children();
}

// "envelope_port": the outer mold line only (no slots / panel recesses) --
// the reference a part must sit inside to be FLUSH (plan U3 flush check).
if (PART == "envelope_port") union() { box_envelope(); fore_fairing(); strut_housing(FORE, FORE_STRUT_AZ); pillar(FORE); pillar(AFT); }
// "slots_port": the two swept leg paths alone -- the hull merge clears them
// through any OLD hull material the new swing planes cross.
if (PART == "slots_port") { swing_slot(FORE); swing_slot(AFT); }
if (PART == "port" || PART == "both") gear_box_port();
if (PART == "stbd" || PART == "both") mirror_cl() gear_box_port();
