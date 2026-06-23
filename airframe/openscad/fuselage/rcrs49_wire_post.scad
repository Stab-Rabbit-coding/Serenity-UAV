// rcrs49_wire_post.scad
// Serenity UAV Rev R — 49 MHz RCRS Top-Wire Antenna Post (24" build)
//
// Purpose:
//   Simple insulated PETG mast posts for the top-wire element of the AX.25 /
//   49 MHz RCRS antenna(s).  TWO independent antennas are built from this
//   same post (River's Room and Simon's Medbay each need their own — see
//   TODO.md §1.4.2, 2026-06-22) — print FOUR posts total, two per antenna:
//
//   River's antenna — PORT flank, shoulder height (between the dorsal ridge
//     and the cargo clamshell door's ventral hinge/swing zone — see below).
//     Forward post at station ≈ 4.72 in (120 mm) from nose (head section).
//     Aft post at station ≈ 22.8 in (580 mm) from nose (rear section,
//     temporary; replaced by integrated mount in Phase 11).
//
//   Simon's antenna — STARBOARD flank, mirrored station and shoulder height.
//
//   Rev R moved both antennas off the dorsal centreline and off any ventral
//   routing (2026-06-22): a single shared dorsal run put both elements too
//   close together (mutual coupling/detuning risk at 49 MHz on this small
//   an airframe); a ventral/keel run was rejected outright because the cargo
//   bay clamshell doors (`generate_cargo_doors.py`) hinge at the outboard
//   flank/belly edge and swing up to 180°, sweeping the lower flank and
//   belly through the door's Y-span — any exterior post mounted there would
//   be in the door's path. Port/starboard at shoulder height (well above
//   the door's reach, well separated from each other) clears both problems.
//   Exact shoulder-height Z offset still needs a FreeCAD cross-section check
//   against the door swing envelope before bonding any post — see TODO.md.
//
// Geometry:
//   Base:  0.47 × 0.47 × 0.079 in (12 × 12 × 2 mm) flat foot — bonded or
//          screwed (M2 flat-head) to hull dorsal skin.
//   Mast:  0.31 × 0.31 × 0.28 in (8 × 8 × 7 mm) upright column on base.
//   Notch: 0.059 in (1.5 mm) diameter bore running athwartships (Z-axis)
//          through the mast, 0.079 in (2 mm) from the mast top.
//          Wire passes through the bore and is retained by a loop or crimp.
//   Total height: 0.35 in (9 mm) — within REVN_BUILD_GUIDE_24IN.md "~10 mm".
//
// Material:  PETG (non-structural / EMI-transparent insulator, no CF filler).
// Print spec: 0.15 mm layer height, 4 perimeters, 40% gyroid infill.
// Orientation: print upright (base on build plate, mast faces up) for best
//   bore roundness.
//
// Installation:
//   Bond base to hull skin (port flank for River's antenna, starboard flank
//   for Simon's — NOT dorsal centreline, NOT ventral/keel line) at shoulder
//   height with West System 105/206 structural epoxy.  Thread 49 MHz antenna
//   wire through bore; dress wire aft to aft post.  For each forward post,
//   feed wire to that bay's own Emma (XCVR-49MHZ-2) J2: River's Room for the
//   port antenna, Simon's Medbay for the starboard antenna — the two Emma
//   boards do not share an antenna (TODO.md §1.4.2, redundancy mandate).
//
// References:
//   docs/REVN_BUILD_GUIDE_24IN.md, Phase 1, Step 8 (superseded by §1.4.2
//     port/starboard relocation, 2026-06-22 — update build guide to match):
//     "Print from rcrs49_wire_post.scad: forward post (~120 mm from nose) +
//      aft post (~580 mm from nose)" — now ×2 sets (port + starboard).
//   CLAUDE.md §Component Naming: River = 49 MHz RCRS primary antenna;
//     Simon also carries 49 MHz primary (independent antenna, starboard).
//   TODO.md §1.4.2 (2026-06-22): port/starboard relocation rationale.
//
// Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// License: CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date:    2026-06-11
// Rev:     R (2026-06-11): Initial release.

// ── Resolution ────────────────────────────────────────────────────────────────

$fn = 32;   // adequate for 1.5 mm bore; keeps render fast for this simple part

// ── Parameters ────────────────────────────────────────────────────────────────

// Base (foot) dimensions
BASE_X = 12.0;   // [mm] base fore-aft length (0.47 in)
BASE_Z = 12.0;   // [mm] base athwartships width (0.47 in)
BASE_Y =  2.0;   // [mm] base thickness, sits flat on hull skin (0.079 in)

// Mast (column) dimensions
MAST_X =  8.0;   // [mm] mast fore-aft width (0.31 in) — centred on base
MAST_Z =  8.0;   // [mm] mast athwartships depth (0.31 in) — centred on base
MAST_Y =  7.0;   // [mm] mast height above base top face (0.28 in)

// Wire retention bore
WIRE_D      =  1.5;   // [mm] wire bore diameter — accepts up to 20 AWG antenna wire
WIRE_Y_FROM_TOP = 2.0;   // [mm] bore centre height below mast top face

// Derived heights
TOTAL_Y = BASE_Y + MAST_Y;   // [mm] total post height = 9.0 mm (0.35 in)
WIRE_Y  = BASE_Y + MAST_Y - WIRE_Y_FROM_TOP;   // [mm] bore centre from base bottom

// ── Module: wire_post ─────────────────────────────────────────────────────────
//
// Single antenna wire post.  Origin at base bottom-face centroid.
// +X = fore, +Z = port (athwartships), +Y = up (away from hull surface).
//
module wire_post() {
    difference() {
        union() {
            // ── Base foot ─────────────────────────────────────────────────
            // Flat plate centred at origin, sitting flush on hull skin.
            translate([-BASE_X/2, 0, -BASE_Z/2])
                cube([BASE_X, BASE_Y, BASE_Z]);

            // ── Mast column ───────────────────────────────────────────────
            // Upright column, centred on base, rising from base top face.
            translate([-MAST_X/2, BASE_Y, -MAST_Z/2])
                cube([MAST_X, MAST_Y, MAST_Z]);
        }

        // ── Wire retention bore ───────────────────────────────────────────
        // Athwartships (Z-axis) bore through mast, WIRE_Y_FROM_TOP below top.
        // Extends 0.1 mm proud of each face for clean manifold cut.
        translate([0, WIRE_Y, -MAST_Z/2 - 0.1])
            cylinder(h = MAST_Z + 0.2, d = WIRE_D);
    }
}

// ── Render ────────────────────────────────────────────────────────────────────
//
// Renders one post.  The module is generic (no port/starboard parameter —
// orientation comes from how the printed post is bonded to the hull
// surface).  Print FOUR total: River's antenna (port flank) forward
// (sta ~120 mm) + aft (sta ~580 mm), and Simon's antenna (starboard flank)
// forward (sta ~120 mm) + aft (sta ~580 mm).  See TODO.md §1.4.2.

wire_post();
