// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Hull frame (canonical for ALL design artifacts): X = +port (left),
//   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
//   world origin.  Primary-component STLs published to airframe/stls/
//   are stored directly in hull frame, baked by tools/bake_hull_frame.py.
//   This file:
//     Part-local print frame.  The spar crank's clamp bore axis is local X
//     (the tilt/spar axis); the ball-stud boss projects in local +Z.  Hull
//     placement derives from the nacelle pivot pose (spar axis = hull X at
//     duct PIVOT_Z; nacelle_pod_50mm_tandem.scad).  Assembly placement
//     VERIFY pending (serenity_assembly.py).
// ===========================================================================
// nacelle_nozzle_pushrod.scad
// Serenity UAV Rev T — Nozzle Pushrod Drive (Option B), Spar Crank + Pushrod
//
// PURPOSE
//   Rev T (2026-07-18) replaces the entire tilt-to-nozzle GEAR train (fixed
//   sector gear, Drive Pinion A, bevel pair, Nozzle Drive Pinion, internal
//   ring gear) with a PUSHROD / BELLCRANK linkage — trade-study Option B
//   (docs/NOZZLE_DRIVE_TRADE.md; user decision 2026-07-18).  The nozzle
//   remains PASSIVELY driven by nacelle tilt (canonical requirement,
//   airframe/AGENTS.md "Nacelle Nozzle Drive"): as the nacelle tilts 0 -> 90 deg
//   the unison ring (nacelle_nozzle_iris.scad, Rev T cam-only) is rotated
//   0 -> 23.75 deg, opening the nozzle exit 75 % -> 105 % of bore.
//
//   This file provides the two printed/procured drive parts; the ring lever
//   ear + ball socket are already part of unison_ring() in the iris file:
//     1. spar_crank()  — clamps the rotating tilt spar (Ø8 AISI 4130,
//        nacelle_pod_50mm_tandem.scad SPAR_OD) and carries a ball stud at
//        radius CRANK_R.  Because the current pod spar ROTATES with the
//        nacelle tilt (it superseded the old fixed-rod pivot — pod line ~363),
//        this crank is a DIRECT tilt-angle input: crank sweeps 0..90 deg with
//        tilt.  (This is a simplification over the trade-doc's original
//        "fixed crank on a NON-rotating spar" assumption, which would have
//        required reading tilt as relative motion; the rotating-spar pod makes
//        the crank a plain driven link.)
//     2. pushrod()     — assembly/clearance representation of the COTS link:
//        an M3 threaded rod (steel) with a ball-cup end at each end that snaps
//        over the crank ball stud and the ring-lever ball stud (standard RC
//        "ball link", e.g. 3 mm ball / M3 cup).  The rod length is set at
//        assembly (turnbuckle-style adjustable ends) — see PUSHROD_LEN.
//
//   Ball studs (x2, COTS): 3 mm ball on an M3 threaded shank (steel), one
//   into the crank boss (CRANK_BALL_*), one into the ring lever ear
//   (RING_BALL_D in the iris file).  Cited as generic RC hardware — no
//   proprietary source.
//
// ── SPATIAL LINKAGE — SYNTHESIS IS *VERIFY* (first-pass geometry) ────────────
//   The tilt (spar) axis is hull X (transverse); the ring axis is the duct
//   local Z (longitudinal) — the two rotation axes are PERPENDICULAR, so this
//   is a spatial RSSR-class linkage (revolute-spherical-spherical-revolute),
//   exactly the risk the trade study flagged for Option B.  The parameters
//   below (CRANK_R, ball offsets, PUSHROD_LEN) are a FIRST-PASS starting point
//   sized for the right order of magnitude:
//     ring ball travel  = RING_LEVER_R * radians(23.75) ~= 32 * 0.4145
//                       ~= 13.3 mm along the ring-lever arc, and
//     crank ball travel  = CRANK_R * radians(90) — so CRANK_R ~= 13.3 / 1.571
//                       ~= 8.5 mm gives ~1:1 arc-length transfer as a start.
//   The EXACT crank radius, ball 3-D positions, and rod length that give a
//   MONOTONIC, non-locking 0..90 deg tilt -> 0..23.75 deg ring map (and clear
//   the nacelle skin over the whole sweep) MUST be solved with a kinematic
//   study / motion sim before this geometry is relied upon.  Tracked as a WBS
//   VERIFY item (§1.1.3).  Do NOT print for flight hardware until closed.
//
// Print / procurement specification:
//   spar_crank : CF-PETG, 0.15 mm layers, 4 perimeters, 60 % infill (carries
//                the full nozzle actuation load through a small ball stud —
//                print solid-ish).  Clamp closed with 2x M2 SHCS.
//   pushrod    : COTS — M3 steel threaded rod + 2x M3 ball-cup links + 2x
//                3 mm/M3 ball studs.  Not printed (shown here for clearance).
//
// Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// License: CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date:    2026-07-18
// Rev:     T (2026-07-18): initial release — Option B pushrod drive replacing
//          the Rev S1 gear train.  AI contribution: Claude (Opus 4.8,
//          Anthropic), directed by Steve Griffing.

// ── Resolution ──────────────────────────────────────────────────────────────
$fn = 64;

// ── Spar / interface dimensions (from nacelle_pod_50mm_tandem.scad) ──────────
SPAR_OD        =  8.0;    // [mm] rotating tilt spar OD (AISI 4130) — MUST match
                          //   pod SPAR_OD; the crank clamps this.
SPAR_BORE_D    =  8.2;    // [mm] clamp bore (0.1 mm/side slip fit on the spar)

// ── Crank geometry (FIRST-PASS — see synthesis VERIFY above) ────────────────
CRANK_R        =  8.5;    // [mm] ball-stud radius on the crank (moment arm)
CRANK_HUB_OD   = 16.0;    // [mm] clamp hub OD around the Ø8 spar
CRANK_W        =  8.0;    // [mm] crank axial width (along the spar, local X)
CRANK_ARM_W    =  6.0;    // [mm] crank arm tangential width
CRANK_BALL_STUD_D = 3.0;  // [mm] ball diameter of the COTS ball stud (M3 shank)
CRANK_BALL_BORE_D = 2.5;  // [mm] pilot bore for the M3 ball-stud shank (tap M3)

// ── Pushrod (COTS ball-link rod — assembly/clearance representation) ────────
PUSHROD_LEN    = 45.0;    // [mm] nominal rod length between ball centres —
                          //   ADJUSTABLE at assembly (turnbuckle ends); final
                          //   value set with CRANK_R by the linkage synthesis.
PUSHROD_ROD_D  =  3.0;    // [mm] M3 threaded rod
PUSHROD_CUP_D  =  7.0;    // [mm] ball-cup OD at each end
PUSHROD_CUP_L  =  6.0;    // [mm] ball-cup length

// ── Clamp split screws ──────────────────────────────────────────────────────
CLAMP_SCREW_D  =  2.2;    // [mm] clearance for 2x M2 SHCS
CLAMP_SCREW_SPACING = 11.0; // [mm] screw centres straddling the clamp split

// ── Module: spar_crank() ─────────────────────────────────────────────────────
//   Clamps the rotating tilt spar and carries a ball stud at CRANK_R.
//   Local frame: clamp bore axis = local X (the spar/tilt axis); the crank
//   arm and ball stud project in local +Z.  Origin at the spar axis, mid-width.
module spar_crank() {
    difference() {
        union() {
            // Clamp hub around the spar (bore axis = local X)
            rotate([0, 90, 0])
                cylinder(h = CRANK_W, d = CRANK_HUB_OD, center = true);
            // Crank arm reaching out to the ball-stud boss (+Z)
            translate([-CRANK_ARM_W / 2, -CRANK_W / 2, 0])
                cube([CRANK_ARM_W, CRANK_W, CRANK_R + CRANK_BALL_STUD_D]);
        }
        // Spar clamp bore (through, local X)
        rotate([0, 90, 0])
            cylinder(h = CRANK_W + 0.2, d = SPAR_BORE_D, center = true);
        // Clamp split slot (thin gap from +Z into the bore so the 2 screws
        // close it onto the spar)
        translate([-0.4, -CRANK_W / 2 - 0.1, 0])
            cube([0.8, CRANK_W + 0.2, CRANK_HUB_OD / 2 + 0.1]);
        // 2x M2 clamp screws straddling the split (bores along local Y)
        for (s = [-1, 1])
            translate([s * CLAMP_SCREW_SPACING / 2, 0, CRANK_HUB_OD / 2 - 1.5])
                rotate([90, 0, 0])
                    cylinder(h = CRANK_W + 0.2, d = CLAMP_SCREW_D, center = true);
        // Ball-stud pilot bore at the crank tip (M3 shank, tap)
        translate([0, 0, CRANK_R])
            rotate([0, 0, 0])
                cylinder(h = CRANK_BALL_STUD_D + 4, d = CRANK_BALL_BORE_D, center = true);
    }
}

// ── Module: pushrod() ────────────────────────────────────────────────────────
//   COTS ball-link rod — shown for assembly/clearance only (not printed).
//   Local frame: rod along local Z, ball centres at Z = 0 and Z = PUSHROD_LEN.
module pushrod() {
    // threaded rod
    translate([0, 0, PUSHROD_CUP_L / 2])
        cylinder(h = PUSHROD_LEN - PUSHROD_CUP_L, d = PUSHROD_ROD_D);
    // ball cups at each end
    for (z = [0, PUSHROD_LEN])
        translate([0, 0, z])
            sphere(d = PUSHROD_CUP_D);
}

// ── Render selection ─────────────────────────────────────────────────────────
//   RENDER_PART = "crank"   -> spar_crank()   (printed CF-PETG)
//   RENDER_PART = "pushrod" -> pushrod()      (COTS — clearance viz only)
//   RENDER_PART = "asm"     -> both, roughly posed (DEFAULT)
RENDER_PART = "asm";

if (RENDER_PART == "crank") {
    spar_crank();
} else if (RENDER_PART == "pushrod") {
    pushrod();
} else {
    spar_crank();
    // rough pose: rod leaving the crank ball toward the ring lever (VERIFY)
    translate([0, 0, CRANK_R])
        rotate([90, 0, 0])
            pushrod();
}
