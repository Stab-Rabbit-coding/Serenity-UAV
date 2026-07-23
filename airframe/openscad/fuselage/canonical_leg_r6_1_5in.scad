// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   This part is modeled in a LEG-LOCAL frame (hip pin at origin, pin axis
//   = local Y, swing plane = local XZ, +X outboard in the swing direction,
//   +Z dorsal/up).  NOT a primary-component STL; do NOT bake with
//   bake_hull_frame.py.  Corner placement transforms live in the
//   "hull_stance" PART below and in docs/LANDING_GEAR_ANALYSIS.md Rev R6.
// ===========================================================================
// ===========================================================================
// canonical_leg_r6.scad
// Serenity UAV -- Rev R6 -- Canonical Articulated Landing Leg (hip-pivot)
// ===========================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// AI note : Authored by Claude (model: Claude Fable 5, Anthropic) under the
//           author's direction, 2026-07-21.  Per AGENTS.md AI attribution.
// Project : Serenity-class Tilt-Rotor UAV (24-inch scale, Firefly TV ship)
// License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date    : 2026-07-21
// Revision: Rev R6 (supersedes Rev R5 wire_brace_leg.scad -- retained for
//           reference with a retirement note, per the SS1.1.4.5 pattern)
//
// Canonical references (see REFERENCES.md):
//   REF-CAD-003  QMx "Official Serenity Blueprints Reference Pack" (2007),
//                Sheet 5 "Ventral Surface Plan View" -- bay stations (fore
//                feet 39.2% / aft feet 63.9% of hull length, ~1.45x hull
//                half-width off centreline), "Detail of Landing Gear"
//                (tri-pad foot, "Feet Pivot 90 deg") and leg side view
//                (cylinder-cluster thigh ~50 deg, disc knee/ankle joints).
//   REF-CAD-002  Nick Henning reference renders -- close-up leg mechanical
//                detail: telescoping piston cluster, 4-satellite-hole disc
//                joints, slotted shin, wedge tri-pad foot.
//   Canonical universe: Firefly / Serenity (TV/film), created by Joss
//                Whedon; ship design Tim Earls / Geoffrey Mandel (QMx pack).
//
// Deliberate deviations from canon (functional build, documented):
//   1. Leg length -- canonical proportions give only ~11 mm belly clearance
//      at 24-in scale; the length is extended to 1.5 in belly clearance to
//      provide functional landing protection.
//   2. Knee/ankle articulate on-screen; here the leg frame is ONE printed
//      piece (thigh+shin) and all articulation is at the HIP -- the knee
//      and ankle discs are canonical styling.  ("Feet Pivot 90 deg" is
//      realized as a square spigot indexing the foot at 90-deg steps.)
//   3. Gear is fixed-down (no retraction); the bay plate provides the
//      canonical recessed-bay look on the hull flank.
//
// Structural basis: tools/landing_gear_r6_sizing.py (all numbers below
// trace to its output) and docs/LANDING_GEAR_ANALYSIS.md Rev R6.
// Mechanism summary: the whole leg pivots about an M3 stainless hip pin in
// a hull-flank bay.  Two SPRING bowed wires (elastic, recoverable) and two
// DUCTILE bowed wires (plastic, sacrificial fuse) span the hip at a 6 mm
// bellcrank radius: leg flexion (foot swinging up-outboard) compresses the
// wire chords so their pre-formed bows deepen -- identical mechanics to
// Rev R5, but the 65:6 lever turns millimetres of wire stroke into tens of
// millimetres of hull settle (peak decel ~52 g at 6 ft tail-down, vs
// ~1,000 g for the Rev R5 rigid post).  An M3 extension-stop cross-pin
// through the clevis ears carries the opposite (hanging / in-flight)
// rotation via a tab on the thigh root; landing loads never touch it.
//
// Usage -- set PART to render:
//   PART = "leg_frame"    One-piece thigh+shin leg frame (CF-PETG, print
//                         lying on its -Y side: bending loads stay in the
//                         layer plane -- strongest orientation)
//   PART = "foot"         Canonical tri-pad arrowhead foot (TPU 95A)
//   PART = "bay"          Hull-flank bay plate: clevis, wire bosses, stop (CF-PETG)
//   PART = "spring_wire_nominal"   / "spring_wire_deformed"
//   PART = "ductile_wire_nominal"  / "ductile_wire_deformed"
//   PART = "leg_assembled"  One complete leg + bay + wires, leg-local frame
//   PART = "leg_deformed"   Same, flexed to full ductile stroke (post-overload)
//   PART = "hull_stance"    All 4 corners at hull-frame stations + ground plane
//
// STL export (from repo root; output names lg_r6_<part>.stl):
//   openscad -o airframe/stls/fuselage/landing-gear/lg_r6_leg_frame.stl \
//     -D 'PART="leg_frame"' airframe/openscad/fuselage/canonical_leg_r6.scad
//   ... (same pattern for every PART above)
// ===========================================================================

PART = "leg_assembled";      // override with -D on the CLI
$fn = 48;

// ---------------------------------------------------------------------------
// Leg-local skeleton (mm) -- hip pin at origin, +X outboard, +Z up.
// Hip sits 118 mm above ground; belly clearance 80 mm (hip is at hull-frame
// Z +38 on the cargo-flank bay).  See sizing script for the lever numbers.
// ---------------------------------------------------------------------------
KNEE   = [32.2, 0, -42.6];      // knee disc centre (thigh 82.8 mm @ 53 deg from horiz)
ANKLE  = [41.9, 0, -64.5];     // ankle disc centre (shin 37.2 mm @ 23.8 deg lean)
GROUND_Z = -76.1;            // foot sole plane (leg-local)
R_H    = 41.9;                // horizontal hip->foot moment arm (documentation)

// Hip pivot / clevis
PIN_D        = 3.2;         // M3 stainless pin clearance bore
HUB_D        = 9.0;         // thigh hip-hub core OD (keeps wire chords clear)
LUG_W        = 14.0;        // thigh root lug width along pin (Y)
EAR_T        = 3.0;         // bay clevis ear thickness
EAR_CLR      = 0.5;         // lug-to-ear side clearance each side

// Extension stop: M3 SS cross-pin through both clevis ears; a tab on the
// thigh root rests on it at nominal extension.  Flexion lifts the tab off.
STOP_PIN_AZ  = 118;         // pin centre azimuth in XZ (deg from +X)
STOP_PIN_R   = 8.0;         // pin centre radius from hip axis
STOP_TAB_AZ1 = 131;         // thigh tab sector start (contact face)
STOP_TAB_AZ2 = 146;         // thigh tab sector end

// Bellcrank wire sockets (in the thigh root, around the pin)
CRANK_R      = 6.0;         // socket centre radius from pin axis
CRANK_AZ     = -22;         // socket azimuth in XZ (deg from +X; down-outboard)
CHORD_AZ     = 68;          // wire chord direction (deg from +X; up the bay wall)
WIRE_STAGGER = 3.5;         // socket pitch along pin axis Y
                            // ductile pair at Y +/-1.75, spring pair at Y +/-5.25

// Wire schedule -- tools/landing_gear_r6_sizing.py output.  Each wire is
// straight stock with ONE shallow mid-span bow; the ENDS STAY STRAIGHT
// (socket seat depth + 2 mm run-in per end) so they can seat in straight
// bores -- the bow occupies only the exposed span between socket mouths.
// DUCTILE diameter is the 6 ft drop-test schedule (Rev R6 default); the
// 4 ft alternative is d=3.81 mm, SAME lengths -- only stock diameter changes.
SPRING_D     = 3.35;        // mm, spring wire diameter
SPRING_L     = 37.0;        // mm, spring stock length (bow span 23)
SPRING_SEAT  = 5.0;         // mm, spring socket seat depth per end
DUCTILE_D    = 4.36;        // mm, ductile wire diameter (6 ft schedule)
DUCTILE_D4   = 3.81;        // mm, ductile alternative (4 ft schedule, ref only)
DUCTILE_L    = 75.0;        // mm, ductile stock length (bow span 55)
DUCTILE_SEAT = 8.0;         // mm, ductile socket seat depth per end
END_RUN_IN   = 2.0;         // mm, straight run-in beyond each socket mouth
H_NOM        = 3.5;         // mm, pre-bend bow rise (both types)
H_DEF_SPRING = 7.4;         // mm, bow at spring elastic-limit stroke (0.93 mm)
H_DEF_DUCT   = 19.2;        // mm, fired ductile bow (full 3.24 mm stroke)
SOCK_CLR     = 0.65;        // socket bore diametral clearance over wire d

// Thigh cylinder cluster (structural section: sizing script "2x14 @ 18")
THIGH_CYL_D  = 14.0;        // main cylinder OD
THIGH_CYL_C  = 18.0;        // main cylinder centre spacing (in swing plane)
THIGH_PISTON_D = 5.0;       // cosmetic telescoping piston rod OD
THIGH_COLLAR_D = 16.0;      // cosmetic telescope collar OD, lower third

// Knee / ankle disc joints -- canonical 4-satellite-hole wheel styling.
// COSMETIC on Rev R6 (leg frame is one piece; articulation is at the hip).
KNEE_DISC_D  = 26.0;
KNEE_DISC_T  = 3.0;         // proud styling disc, both Y faces
KNEE_BCD     = 15.0;        // satellite-hole circle diameter
KNEE_SAT_D   = 3.0;         // satellite recess diameter (1.6 mm deep)
KNEE_CTR_D   = 5.0;         // centre recess
ANKLE_DISC_D = 16.0;
ANKLE_DISC_T = 14.0;        // spans the shin thickness + proud both faces

// Shin blade (canonical slotted flat member)
SHIN_W       = 20.0;        // width in swing plane
SHIN_T       = 10.0;        // thickness along pin axis
SHIN_SLOT_L  = 14.0;        // cosmetic vent slot length
SHIN_SLOT_W  = 3.5;
SHIN_SLOT_DEEP = 2.0;       // pocket depth per face (NOT through -- keeps section)

// Foot (canonical tri-pad arrowhead, TPU 95A) -- print frame: sole on Z=0
FOOT_HUB_D   = 24.0;        // central hub OD
FOOT_HUB_H   = 10.0;        // hub height; top face meets the ankle disc rim
FOOT_PAD_T   = 8.0;         // pad thickness at hub, wedges taper to 4
FOOT_TOE_L   = 34.0;        // fore (toe) pad length from hub centre
FOOT_TOE_W   = 20.0;        // toe pad root width
FOOT_HEEL_L  = 26.0;        // rear pad length from hub centre
FOOT_HEEL_W  = 18.0;        // rear pad root width
FOOT_HEEL_AZ = 130;         // rear pads at +/-130 deg from toe
FOOT_SPIG    = 8.0;         // square ankle spigot side ("Feet Pivot 90 deg":
                            // square socket indexes the foot at 90-deg steps)
FOOT_SPIG_H  = 6.0;         // socket depth in the hub top face
FOOT_M25_D   = 2.8;         // M2.5 cross-bolt clearance
TREAD_N      = 3;           // tread ribs per pad (canonical ribbed sole)
TREAD_D      = 1.5;         // tread rib depth

// Bay plate (surface-mounts to the cargo-shell flank; conforming spacer /
// recess integration is LG-02.  Local frame: plate back face at X = -8 at
// pivot height, canted BAY_CANT to follow the flank slope.)
BAY_BACK_X   = -8.0;        // plate back plane X at Z=0 (pivot height)
BAY_CANT     = 22;          // deg from vertical -- cargo flank slope
BAY_PLATE_W  = 40.0;        // along pin axis Y
BAY_PLATE_L  = 82.0;        // up the flank (in the canted plane)
BAY_PLATE_T  = 5.0;
BAY_SURR_T   = 3.0;         // raised canonical bay-recess surround rim
BAY_M3_D     = 3.4;         // 4x M3 shell through-bolts (+ internal backing)
BOSS_OD      = 11.0;        // wire boss OD (bearing margin: see sizing script)
BOSS_L       = 10.0;        // wire boss length along chord

// Flexion at full ductile stroke (sizing script: 30.9 deg hip rotation)
FLEX_DEG     = 30.9;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

// Unit vector in the XZ swing plane at azimuth az (deg from +X toward +Z)
function azv(az) = [cos(az), 0, sin(az)];

// Thigh-side socket MOUTH centre for a wire at stagger y
function crank_socket(y) = CRANK_R * azv(CRANK_AZ) + [0, y, 0];

// Bay boss bore MOUTH centre for a wire of stock length l seated `seat`
// deep at both ends: exposed span between mouths = l - 2*seat
function boss_mouth(l, seat, y) = crank_socket(y) + (l - 2 * seat) * azv(CHORD_AZ);

// Solid rod between two points
module rod_between(a, b, d) {
    v = b - a;
    l = norm(v);
    polar = atan2(norm([v[0], v[1]]), v[2]);
    az = atan2(v[1], v[0]);
    translate(a) rotate([0, 0, az]) rotate([0, polar, 0])
        cylinder(h = l, d = d);
}

// Y-axis cylinder centred at point p, total width w, diameter d
module ycyl(p, w, d) {
    translate(p + [0, -w / 2, 0]) rotate([-90, 0, 0]) cylinder(h = w, d = d);
}

// ---------------------------------------------------------------------------
// Bowed wire strut (Rev R5 polyhedron sweep, carried forward with the face
// winding corrected -- Rev R5's winding yielded inward normals / negative
// volume): round wire, stock length L along local Z centred at the origin.
// The ends stay STRAIGHT for a length e each (socket seat + run-in); only
// the mid-span of length B = L - 2e carries the parabolic bow of rise h
// toward local +X (formable on a simple bending jig with straight grips).
// ---------------------------------------------------------------------------
module bowed_wire(d, L, h, e = 0) {
    n = 24;
    sides = 12;
    r = d / 2;
    b = L - 2 * e;                      // bow span between straight ends
    path = [for (i = [0 : n]) let (
        t = i / n,
        z = (t - 0.5) * L,
        zb = z + L / 2 - e,             // position within the bow span
        u = zb / b,
        x = (zb <= 0 || zb >= b) ? 0 : h * (1 - pow(2 * u - 1, 2))
    ) [x, 0, z]];
    tangents = [for (i = [0 : n]) let (
        i0 = max(i - 1, 0), i1 = min(i + 1, n),
        dv = path[i1] - path[i0]
    ) dv / norm(dv)];
    rings = [for (i = [0 : n]) let (
        t = tangents[i],
        arb = (abs(t[1]) < 0.9) ? [0, 1, 0] : [1, 0, 0],
        u = cross(t, arb) / norm(cross(t, arb)),
        v = cross(t, u)
    ) [for (j = [0 : sides - 1]) let (ang = 360 * j / sides)
        path[i] + r * (u * cos(ang) + v * sin(ang))]];
    points = [for (i = [0 : n]) for (j = [0 : sides - 1]) rings[i][j]];
    side_faces = [for (i = [0 : n - 1]) for (j = [0 : sides - 1]) let (
        a = i * sides + j,
        b = i * sides + (j + 1) % sides,
        c = (i + 1) * sides + (j + 1) % sides,
        d2 = (i + 1) * sides + j
    ) each [[a, c, b], [a, d2, c]]];
    faces = concat(side_faces,
                   [[for (j = [0 : sides - 1]) j]],
                   [[for (j = [sides - 1 : -1 : 0]) n * sides + j]]);
    polyhedron(points = points, faces = faces, convexity = 4);
}

// A wire posed in the leg-local frame, SEATED: the stock runs from `seat`
// deep inside the thigh socket, along the chord (azimuth CHORD_AZ in XZ),
// to `seat` deep inside its bay boss bore.  Bow bulges in-plane.
module posed_wire(l, seat, y, d, h) {
    a = crank_socket(y);
    translate(a + (l / 2 - seat) * azv(CHORD_AZ))
        rotate([0, 90 - CHORD_AZ, 0])       // local +Z -> chord direction
            rotate([0, 0, 90])              // bow bulge into the swing plane
                bowed_wire(d, l, h, seat + END_RUN_IN);
}

// Wedge sector in the XZ plane: azimuth az1..az2, radius r1..r2, width w
// along Y, centred on the hip axis.  Used for the extension-stop tab.
module xz_sector(az1, az2, r1, r2, w) {
    steps = 6;
    pts_outer = [for (i = [0 : steps]) let (a = az1 + (az2 - az1) * i / steps)
        [r2 * cos(a), r2 * sin(a)]];
    pts_inner = [for (i = [steps : -1 : 0]) let (a = az1 + (az2 - az1) * i / steps)
        [r1 * cos(a), r1 * sin(a)]];
    translate([0, w / 2, 0]) rotate([90, 0, 0])
        linear_extrude(height = w) polygon(concat(pts_outer, pts_inner));
}

// ---------------------------------------------------------------------------
// MODULE: knee_disc_cosmetic(y_face)
// Canonical knee "wheel" styling disc, proud on one Y face of the leg at
// the knee: 4 satellite recesses on KNEE_BCD + centre recess (QMx Sheet 5
// side view / Henning renders).  y_face = +1 or -1.
// ---------------------------------------------------------------------------
module knee_disc_cosmetic(y_face) {
    y0 = y_face * SHIN_T / 2;               // flush at the blade face
    difference() {
        ycyl(KNEE + [0, y0 + y_face * KNEE_DISC_T / 2, 0],
             KNEE_DISC_T, KNEE_DISC_D);
        for (a = [45, 135, 225, 315])
            translate(KNEE + [KNEE_BCD / 2 * cos(a),
                              y0 + y_face * (KNEE_DISC_T + 0.1),
                              KNEE_BCD / 2 * sin(a)])
                rotate([90 * y_face, 0, 0])
                    cylinder(h = 1.6, d = KNEE_SAT_D);
        translate(KNEE + [0, y0 + y_face * (KNEE_DISC_T + 0.1), 0])
            rotate([90 * y_face, 0, 0])
                cylinder(h = 1.6, d = KNEE_CTR_D);
    }
}

// ---------------------------------------------------------------------------
// MODULE: leg_frame()
// One-piece structural leg in leg-local assembly position:
//   hip hub + bellcrank wire sockets + extension-stop tab at the root,
//   twin-cylinder thigh cluster with web down to the knee,
//   cosmetic telescope collars + piston rods (canonical telescoping look),
//   canonical knee styling discs both faces,
//   slotted shin blade, ankle disc, square foot spigot.
// Print lying on the -Y face: swing-plane bending stays in the layer plane.
// ---------------------------------------------------------------------------
module leg_frame() {
    axis = KNEE / norm(KNEE);               // unit vector hip -> knee
    perp = [-axis[2], 0, axis[0]];          // in-plane perpendicular
    difference() {
        union() {
            // Hip hub core (kept slim so wire chords clear it -- see header)
            ycyl([0, 0, 0], LUG_W, HUB_D);
            // Extension-stop tab (rests on the bay's stop cross-pin)
            xz_sector(STOP_TAB_AZ1, STOP_TAB_AZ2, 3.0, 10.0, LUG_W);
            // Root lug: blend hub into the cluster.  The hull() stays in
            // the down-outboard quadrant, out of the wire-chord corridor.
            hull() {
                ycyl([0, 0, 0], LUG_W, HUB_D);
                for (s = [-1, 1])
                    translate(14 * axis + s * THIGH_CYL_C / 2 * perp)
                        sphere(d = THIGH_CYL_D);
            }
            // Twin main cylinders, hip to knee
            for (s = [-1, 1])
                rod_between(10 * axis + s * THIGH_CYL_C / 2 * perp,
                            KNEE + s * THIGH_CYL_C / 2 * perp - 6 * axis,
                            THIGH_CYL_D);
            // Web between the cylinders (hulled sphere chain)
            hull()
                for (s = [-1, 1]) {
                    translate(12 * axis + s * THIGH_CYL_C / 2 * perp)
                        sphere(d = THIGH_CYL_D * 0.72);
                    translate(KNEE - 8 * axis + s * THIGH_CYL_C / 2 * perp)
                        sphere(d = THIGH_CYL_D * 0.72);
                }
            // Cosmetic telescope collars (lower third of the cluster)
            for (s = [-1, 1])
                rod_between(KNEE - 28 * axis + s * THIGH_CYL_C / 2 * perp,
                            KNEE - 8 * axis + s * THIGH_CYL_C / 2 * perp,
                            THIGH_COLLAR_D);
            // Cosmetic piston rods on the outboard shoulder
            for (yo = [-4, 4])
                translate([0, yo, 0])
                    rod_between(12 * axis + 10 * perp,
                                KNEE - 24 * axis + 10 * perp,
                                THIGH_PISTON_D);
            // Knee styling discs, both faces (canonical wheel pattern)
            knee_disc_cosmetic(1);
            knee_disc_cosmetic(-1);
            // Shin blade: stadium section swept knee -> ankle
            hull() {
                ycyl(KNEE, SHIN_T, SHIN_W);
                ycyl(ANKLE, SHIN_T, SHIN_W * 0.8);
            }
            // Ankle disc (canonical joint styling, proud both faces)
            ycyl(ANKLE, ANKLE_DISC_T, ANKLE_DISC_D);
            // Square foot spigot: ankle disc rim down into the foot socket
            translate([ANKLE[0], ANKLE[1], ANKLE[2] - 9.75])
                cube([FOOT_SPIG, FOOT_SPIG, 9.5], center = true);
        }
        // Hip pin bore
        ycyl([0, 0, 0], LUG_W + 0.2, PIN_D);
        // 4 bellcrank wire sockets: bore along the chord, into the root
        for (i = [0 : 3]) {
            y = (i - 1.5) * WIRE_STAGGER;
            spring = (abs(y) > 3);                      // outer=spring
            wd = spring ? SPRING_D : DUCTILE_D;
            seat = spring ? SPRING_SEAT : DUCTILE_SEAT;
            a = crank_socket(y);
            translate(a + 0.1 * azv(CHORD_AZ))
                rotate([0, 90 - CHORD_AZ, 0])
                    translate([0, 0, -seat - 0.1])
                        cylinder(h = seat + 0.2, d = wd + SOCK_CLR);
        }
        // Wire-chord relief scallop across the root's up-outboard shoulder
        // (guarantees the chords' first 14 mm clear the lug blend)
        for (i = [0 : 3]) {
            y = (i - 1.5) * WIRE_STAGGER;
            a = crank_socket(y);
            translate(a) rotate([0, 90 - CHORD_AZ, 0])
                cylinder(h = 14, d = DUCTILE_D + 2.5);
        }
        // Canonical vent-slot pockets, both shin faces
        mid = (KNEE + ANKLE) / 2;
        for (sy = [-1, 1]) for (xo = [-4.5, 4.5])
            translate(mid + [xo, sy * (SHIN_T / 2 - SHIN_SLOT_DEEP / 2), 0])
                cube([SHIN_SLOT_W, SHIN_SLOT_DEEP + 0.2, SHIN_SLOT_L],
                     center = true);
        // Ankle cosmetic satellite recesses, both faces
        for (yf = [-1, 1]) for (a = [45, 135, 225, 315])
            translate(ANKLE + [ANKLE_DISC_D * 0.28 * cos(a),
                               yf * (ANKLE_DISC_T / 2 + 0.1),
                               ANKLE_DISC_D * 0.28 * sin(a)])
                rotate([90 * yf, 0, 0]) cylinder(h = 1.6, d = 2.6);
        // M2.5 foot retention cross-bolt through the spigot
        translate([ANKLE[0], ANKLE[1], ANKLE[2] - 11])
            rotate([0, 90, 0])
                cylinder(h = FOOT_SPIG + 8, d = FOOT_M25_D, center = true);
    }
}

// ---------------------------------------------------------------------------
// MODULE: foot()
// Canonical tri-pad arrowhead foot (TPU 95A), sole-down at the origin in
// PRINT orientation: central hub, pointed toe wedge (+X), two swept heel
// wedges, ribbed treads (QMx Sheet 5 "Detail of Landing Gear" bottom
// view), square top-face socket ("Feet Pivot 90 deg" -> 90-deg indexing)
// + M2.5 cross-bolt.
// ---------------------------------------------------------------------------
module foot_pad_wedge(l, w) {
    hull() {
        cylinder(h = FOOT_PAD_T, d = w);
        translate([l, 0, 0]) cylinder(h = 4.0, d = w * 0.45);
    }
}

module foot() {
    difference() {
        union() {
            cylinder(h = FOOT_HUB_H, d = FOOT_HUB_D);            // hub
            foot_pad_wedge(FOOT_TOE_L, FOOT_TOE_W);              // toe
            for (s = [-1, 1])
                rotate([0, 0, s * FOOT_HEEL_AZ])
                    foot_pad_wedge(FOOT_HEEL_L, FOOT_HEEL_W);    // heels
        }
        // Square ankle-spigot socket, top face (90-deg indexable)
        translate([0, 0, FOOT_HUB_H - FOOT_SPIG_H / 2 + 0.1])
            cube([FOOT_SPIG + 0.4, FOOT_SPIG + 0.4, FOOT_SPIG_H],
                 center = true);
        // M2.5 cross-bolt through hub and spigot
        translate([0, 0, FOOT_HUB_H - 3])
            rotate([0, 90, 0])
                cylinder(h = FOOT_HUB_D + 2, d = FOOT_M25_D, center = true);
        // Ribbed treads across each pad sole (canonical ribbed bottom)
        for (az = [0, FOOT_HEEL_AZ, -FOOT_HEEL_AZ])
            rotate([0, 0, az])
                for (i = [1 : TREAD_N])
                    translate([6 + i * 7, 0, -0.1])
                        cube([2.5, 60, TREAD_D + 0.1], center = true);
    }
}

// ---------------------------------------------------------------------------
// MODULE: bay()
// Hull-flank bay plate in leg-local position: canted mounting plate with
// raised canonical-recess surround, clevis ears (M3 hip pin + M3 stop
// cross-pin), 4 wire bosses on riser wedges at each wire's far chord end,
// 4x M3 shell through-bolt holes.  LG-02 owns final flank conforming.
// ---------------------------------------------------------------------------
module bay() {
    difference() {
        union() {
            // Canted plate: back face follows the flank slope
            translate([BAY_BACK_X, 0, 12])
                rotate([0, -BAY_CANT, 0])
                    translate([0, -BAY_PLATE_W / 2, -34])
                        difference() {
                            cube([BAY_PLATE_T, BAY_PLATE_W, BAY_PLATE_L]);
                            // recess pocket inside the raised surround
                            translate([BAY_PLATE_T - BAY_SURR_T + 3, 7, 9])
                                cube([BAY_SURR_T + 3.1, BAY_PLATE_W - 14,
                                      BAY_PLATE_L - 18]);
                        }
            // Clevis ears astride the thigh lug (carry both pins)
            for (s = [-1, 1])
                translate([0, s * (LUG_W / 2 + EAR_CLR + EAR_T / 2), 0])
                    hull() {
                        ycyl([0, 0, 0], EAR_T, HUB_D + 5);
                        ycyl(STOP_PIN_R * azv(STOP_PIN_AZ), EAR_T,
                             PIN_D + 4);
                        translate([BAY_BACK_X + 1, -EAR_T / 2, -9])
                            cube([2, EAR_T, 24]);
                    }
            // Wire bosses on riser wedges at each chord's far end
            for (i = [0 : 3]) {
                y = (i - 1.5) * WIRE_STAGGER;
                spring = (abs(y) > 3);
                l = spring ? SPRING_L : DUCTILE_L;
                st = spring ? SPRING_SEAT : DUCTILE_SEAT;
                m = boss_mouth(l, st, y);
                hull() {
                    translate(m) rotate([0, 90 - CHORD_AZ, 0])
                        cylinder(h = st + 3, d = BOSS_OD);
                    // riser root on the canted plate plane
                    translate([BAY_BACK_X + tan(BAY_CANT) * max(m[2], 0),
                              y - BOSS_OD / 2, m[2] - 5])
                        cube([2, BOSS_OD, 10]);
                }
            }
        }
        // Hip pin bore through both ears
        ycyl([0, 0, 0], LUG_W + 2 * (EAR_CLR + EAR_T) + 0.2, PIN_D);
        // Extension-stop cross-pin bore through both ears
        ycyl(STOP_PIN_R * azv(STOP_PIN_AZ),
             LUG_W + 2 * (EAR_CLR + EAR_T) + 0.2, PIN_D);
        // Wire seats: blind bores into each boss along the chord
        for (i = [0 : 3]) {
            y = (i - 1.5) * WIRE_STAGGER;
            spring = (abs(y) > 3);
            l = spring ? SPRING_L : DUCTILE_L;
            wd = spring ? SPRING_D : DUCTILE_D;
            st = spring ? SPRING_SEAT : DUCTILE_SEAT;
            translate(boss_mouth(l, st, y) - 0.1 * azv(CHORD_AZ))
                rotate([0, 90 - CHORD_AZ, 0])
                    cylinder(h = st + 0.2, d = wd + SOCK_CLR);
        }
        // 4x M3 shell mounting through-bolts (internal backing plate: LG-02)
        translate([BAY_BACK_X, 0, 12]) rotate([0, -BAY_CANT, 0])
            for (yb = [-BAY_PLATE_W / 2 + 5, BAY_PLATE_W / 2 - 5])
                for (zb = [-28, 42])
                    translate([-4.1, yb, zb])
                        rotate([0, 90, 0])
                            cylinder(h = BAY_PLATE_T + 8.2, d = BAY_M3_D);
    }
}

// ---------------------------------------------------------------------------
// MODULE: leg_moving(flex) -- leg frame + foot as one rigid group, rotated
// flex deg into flexion about the hip pin (foot swings up-outboard).
// ---------------------------------------------------------------------------
module leg_moving(flex) {
    rotate([0, -flex, 0]) {
        color("DimGray", 0.95) leg_frame();
        // foot: print frame -> assembly (sole at GROUND_Z, toe +X outboard)
        color([0.15, 0.15, 0.15], 0.95)
            translate([ANKLE[0], ANKLE[1], GROUND_Z]) foot();
    }
}

// ---------------------------------------------------------------------------
// MODULE: leg_assembly(flex, h_duct, h_spring)
// Complete corner: bay + leg at flexion angle + all 4 wires.
// ---------------------------------------------------------------------------
module leg_assembly(flex = 0, h_duct = H_NOM, h_spring = H_NOM) {
    color("OliveDrab", 0.8) bay();
    leg_moving(flex);
    for (i = [0 : 3]) {
        y = (i - 1.5) * WIRE_STAGGER;
        spring = (abs(y) > 3);
        color(spring ? "Goldenrod" : "FireBrick")
            posed_wire(spring ? SPRING_L : DUCTILE_L,
                       spring ? SPRING_SEAT : DUCTILE_SEAT, y,
                       spring ? SPRING_D : DUCTILE_D,
                       spring ? h_spring : h_duct);
    }
}

// ---------------------------------------------------------------------------
// Hull-frame corner placement (verification view only -- final placements
// are LG-10).  Hull frame: X=+port, Y=+aft, Z=+dorsal; centreline
// X=-169.9; cargo belly Z=0; ground plane Z=-80.
// Corner format: [hip_x, hip_y, hip_z, swing_azimuth_deg]
//   swing azimuth: direction of foot from hip in plan, deg from hull +X
//   (port-outboard); fore legs swing fore-of-outboard, aft legs aft-of-
//   outboard, feet landing within 5 mm of the canonical QMx stations.
// ---------------------------------------------------------------------------
X_CL = -169.9;
CORNERS = [
    [ -90.0,  -7.0, 38,  -22.4 ],   // fore-port  (foot ~[-30.4, -31.8])
    [-249.8,  -7.0, 38, -157.6 ],   // fore-stbd  (mirror)
    [ -79.0, 107.0, 38,   28.0 ],   // aft-port   (foot ~[-21.6, +137.5])
    [-260.8, 107.0, 38,  152.0 ],   // aft-stbd   (mirror)
];

// All 4 corners, gear only (no ground/ghost slabs) -- consumed by
// airframe/FreeCAD-scripts/serenity_assembly.py as the landing-gear
// component until the LG-10 FreeCAD bake finalizes placements.
module hull_legs() {
    for (c = CORNERS)
        translate([c[0], c[1], c[2]])
            rotate([0, 0, c[3]])
                leg_assembly(0);
}

module hull_stance() {
    // ground plane
    color("Tan", 0.25) translate([-360, -120, -39.1]) cube([380, 380, 1]);
    // cargo-belly footprint ghost
    color("SaddleBrown", 0.12) translate([-267, -69.5, 0])
        cube([194.3, 198.5, 2]);
    hull_legs();
}

// ---------------------------------------------------------------------------
// PART selector (print orientations noted per part)
// ---------------------------------------------------------------------------
if (PART == "leg_frame") {
    // Print lying on the -Y face (swing-plane bending in the layer plane)
    translate([0, 0, SHIN_T / 2]) rotate([-90, 0, 0]) leg_frame();
} else if (PART == "foot") {
    foot();                              // already sole-down print frame
} else if (PART == "bay") {
    // Print: canted plate back face down
    rotate([0, BAY_CANT, 0]) translate([-BAY_BACK_X + 1, 0, 0]) bay();
} else if (PART == "spring_wire_nominal") {
    bowed_wire(SPRING_D, SPRING_L, H_NOM);
} else if (PART == "spring_wire_deformed") {
    bowed_wire(SPRING_D, SPRING_L, H_DEF_SPRING);
} else if (PART == "ductile_wire_nominal") {
    bowed_wire(DUCTILE_D, DUCTILE_L, H_NOM);
} else if (PART == "ductile_wire_deformed") {
    bowed_wire(DUCTILE_D, DUCTILE_L, H_DEF_DUCT);
} else if (PART == "leg_assembled") {
    leg_assembly(0);
} else if (PART == "leg_deformed") {
    leg_assembly(FLEX_DEG, H_DEF_DUCT, H_DEF_SPRING);
} else if (PART == "hull_legs") {
    hull_legs();
} else if (PART == "hull_stance") {
    hull_stance();
} else {
    assert(false, str("Unknown PART: ", PART));
}
