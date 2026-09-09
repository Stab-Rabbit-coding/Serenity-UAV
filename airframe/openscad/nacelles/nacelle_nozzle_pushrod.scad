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
//     1. spar_crank()  — the drive crank carrying a ball stud at radius
//        CRANK_R.  ADOPTED (2026-07-19 amendment): it seats on the nacelle
//        sync PINION, not on the tilt spar — see "ADOPTED ARCHITECTURE" below.
//        The pinion turns 1:1 with tilt RELATIVE TO THE NACELLE, so the crank
//        sweeps 0..90 deg in the nacelle frame.  (The module's geometry is
//        still drawn as the old Ø8 spar clamp — see its TODO/VERIFY.)
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
// ── ADOPTED ARCHITECTURE — crank on the PINION, linkage SOLVED ──────────────
//   Governing decision: `docs/NOZZLE_DRIVE_TRADE.md`, "DECISION AMENDMENT --
//   hybrid A+B adopted (2026-07-19)".  The drive crank does NOT clamp the tilt
//   spar.  It seats on a nacelle-mounted sync PINION that meshes a WING-FIXED
//   sun gear coaxial with the spar at the wing tip.  As the nacelle tilts
//   theta about the spar, the fixed-sun / planet-pinion pair spins the pinion
//   by theta * (N_sun / N_pinion) RELATIVE TO THE NACELLE; at the adopted 1:1
//   mesh the pinion tracks tilt 1:1 relative to the nacelle.  Crank, pushrod
//   and unison ring are then ALL nacelle-body-fixed, so the tilt rotation drops
//   out of the linkage math entirely and the problem is a plain planar-input /
//   spatial-RSSR solve in the nacelle frame.
//
//   SOLVED GEOMETRY (nacelle-local frame: duct axis = local Z, spar/tilt axis
//   = local X at local Z = PIVOT_Z; source of truth in brackets):
//     PIVOT_Z       = 107.5 mm   [nacelle_pod_50mm_tandem.scad:437]
//     SYNC_R        = 13.0 mm    1:1 sun and pinion pitch radius (pitch Ø26)
//     SYNC_CD       = 26.0 mm    centre distance = 2*SYNC_R; the pinion sits
//                                this far AFT of the spar axis, clearing the
//                                on-axis Hall/bearing stack in the joint gap
//     SUN_XLOC      = -38.0 mm   nacelle-local X of the mesh plane (the
//                                wing-tip <-> nacelle joint gap)
//     pinion axis   parallel to local X through
//                   (x = -38.0, y = 0, z = PIVOT_Z + SYNC_CD = 133.5)
//     CRANK_R       = 8.5 mm     (UNCHANGED)
//     CRANK_PHASE   = 206.0 deg  crank clocking about the pinion axis at zero
//                                tilt (see the parameter block below)
//     PUSHROD_LEN   = 48.0 mm    (was 45.0 — a spec change on a COTS
//                                turnbuckle-adjustable ball-link rod, not new
//                                hardware)
//     RING_LEVER_R  = 32.0 mm    [nacelle_nozzle_iris.scad]
//     RING_LEVER_AZ = 157.5 deg  [nacelle_nozzle_iris.scad] — RELOCATED from
//                                22.5 to the INBOARD flap gap so the pushrod
//                                hugs the inboard cheek instead of crossing
//                                the duct (8 flaps -> gaps at 22.5 + k*45)
//     ring ball at  (RING_LEVER_R*cos(AZ+psi), RING_LEVER_R*sin(AZ+psi),
//                    NOZZLE_RING_Z + 4.0)  with NOZZLE_RING_Z = 166.25
//
//   VERIFIED PERFORMANCE (`tools/nozzle_linkage_check.py`, default run — the
//   adopted nacelle-frame model; tilt swept 0->90 deg at 1 deg steps,
//   root-finding the ring angle psi that holds the rod length constant):
//     • ring stroke span 23.816 deg against the 23.75 deg design target
//       (THETA_RING_REF_OPEN, nacelle_nozzle_iris.scad) — 0.3 % error
//     • psi(0) = -0.36 deg, i.e. essentially zero — the ring cam needs NO
//       re-clocking relative to the lever ear
//     • psi MONOTONIC across the whole sweep (no toggle / dead point),
//       running 0 -> -24.18 deg (negative azimuth direction)
//     • transmission angle 88.1..103.8 deg; worst-case min(TA, 180-TA) =
//       76.2 deg, far above the >= 40-45 deg linkage rule of thumb
//   The check tool PASSES on this geometry.  The earlier "do NOT print until
//   the synthesis closes" VERIFY is therefore CLOSED for the linkage numbers.
//
//   RESOLVED HISTORY — why the spar crank failed (keep this on record):
//   the original Option-B implementation clamped the crank to the tilt spar.
//   **The tilt spar is KEYED TO THE NACELLE**, so that crank shared the
//   nacelle's rotating frame with the unison ring: the two swing together
//   through the whole 0..90 deg tilt with ZERO RELATIVE MOTION and the pushrod
//   never strokes the ring.  An exhaustive 2026-09-09 sweep (CRANK_R 8.5-28 mm
//   x PUSHROD_LEN 58-90 mm x 24 mounting phases x 8 spar stations, 336
//   combinations) returned ZERO reachable-and-monotonic candidates, confirming
//   that no choice of dimensions can create relative motion the frame geometry
//   does not have.  That empty result is retained as the regression/historical
//   record behind `tools/nozzle_linkage_check.py --model spar-crank-superseded`.
//   A passive, tilt-driven nozzle MUST take its datum from the NON-TILTING
//   WING — which is exactly what the adopted pinion architecture above does.
//
//   REMAINING WORK (WBS §1.1.3): spar_crank() below is still drawn as a Ø8
//   SPAR clamp.  It must be re-hubbed onto the pinion — see the TODO/VERIFY
//   comment on that module.  Module and tooth counts for the 1:1 sun/pinion
//   mesh (pitch radius 13.0 mm is fixed) are also still open.
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
//          T1 (2026-09-09): retargeted to the ADOPTED hybrid A+B architecture
//          (crank on the wing-geared PINION, not the spar).  PUSHROD_LEN
//          45.0 → 48.0, CRANK_PHASE = 206.0 added, header NO-GO replaced with
//          the solved/verified linkage; spar_crank() part geometry NOT yet
//          re-hubbed (see its TODO/VERIFY).  AI contribution: Claude (Opus 5,
//          Anthropic), directed by Steve Griffing.

// ── Resolution ──────────────────────────────────────────────────────────────
$fn = 64;

// ── Spar / interface dimensions (from nacelle_pod_50mm_tandem.scad) ──────────
SPAR_OD        =  8.0;    // [mm] rotating tilt spar OD (AISI 4130) — MUST match
                          //   pod SPAR_OD; the crank clamps this.
SPAR_BORE_D    =  8.2;    // [mm] clamp bore (0.1 mm/side slip fit on the spar)

// ── Crank geometry (SOLVED — see "ADOPTED ARCHITECTURE" above) ──────────────
CRANK_R        =  8.5;    // [mm] ball-stud radius on the crank (moment arm) —
                          //   UNCHANGED by the 2026-07-19 amendment; the solved
                          //   linkage keeps it.
CRANK_PHASE    = 206.0;   // [deg] crank clocking about the PINION axis at zero
                          //   tilt.  The crank ball sits, in nacelle-local
                          //   coordinates, at
                          //     x = SUN_XLOC                       = -38.0
                          //     y = CRANK_R * sin(theta + CRANK_PHASE)
                          //     z = PIVOT_Z + SYNC_CD
                          //         + CRANK_R * cos(theta + CRANK_PHASE)
                          //   with PIVOT_Z + SYNC_CD = 133.5 (pinion axis).
                          //   206 deg is the value solved by
                          //   tools/nozzle_linkage_check.py: it is what makes
                          //   psi(0 deg tilt) ~= 0 (so the ring cam needs no
                          //   re-clocking) while holding the 0->90 deg sweep
                          //   monotonic with a 23.816 deg ring stroke against
                          //   the 23.75 deg target.  Do not re-clock without
                          //   re-running that check.
CRANK_HUB_OD   = 16.0;    // [mm] clamp hub OD around the Ø8 spar
CRANK_W        =  8.0;    // [mm] crank axial width (along the spar, local X)
CRANK_ARM_W    =  6.0;    // [mm] crank arm tangential width
CRANK_BALL_STUD_D = 3.0;  // [mm] ball diameter of the COTS ball stud (M3 shank)
CRANK_BALL_BORE_D = 2.5;  // [mm] pilot bore for the M3 ball-stud shank (tap M3)

// ── Pushrod (COTS ball-link rod — assembly/clearance representation) ────────
PUSHROD_LEN    = 48.0;    // [mm] nominal rod length between ball centres.
                          //   SOLVED value (was 45.0 first-pass).  The rod is a
                          //   COTS turnbuckle-adjustable ball-link rod, so this
                          //   is a SPEC change, not new hardware.  48.0 is the
                          //   length at which tools/nozzle_linkage_check.py
                          //   reports a reachable, monotonic 0->90 deg sweep
                          //   with a 23.816 deg ring stroke (target 23.75) and
                          //   a worst-case transmission angle of 76.2 deg.
PUSHROD_ROD_D  =  3.0;    // [mm] M3 threaded rod
PUSHROD_CUP_D  =  7.0;    // [mm] ball-cup OD at each end
PUSHROD_CUP_L  =  6.0;    // [mm] ball-cup length

// ── Clamp split screws ──────────────────────────────────────────────────────
CLAMP_SCREW_D  =  2.2;    // [mm] clearance for 2x M2 SHCS
CLAMP_SCREW_SPACING = 11.0; // [mm] screw centres straddling the clamp split

// ── Module: spar_crank() ─────────────────────────────────────────────────────
//   Local frame: clamp bore axis = local X (parallel to the spar/tilt axis);
//   the crank arm and ball stud project in local +Z.  Origin at the bore axis,
//   mid-width.
//
//   TODO / VERIFY (WBS §1.1.3) — THIS PART IS NOT YET RETARGETED.  The geometry
//   below is the SUPERSEDED spar-clamp version: it still bores SPAR_BORE_D =
//   8.2 mm to clamp the Ø8 tilt spar, and it still places the arm at a fixed
//   local +Z with no clocking.  Under the adopted architecture the crank seats
//   on the nacelle sync PINION, not the spar, so this module MUST change in
//   two specific ways before it is printed:
//     1. BORE / HUB — replace the Ø8.2 spar clamp bore and CRANK_HUB_OD = 16
//        clamp hub with a hub sized to the PINION shaft (or integrated into the
//        pinion blank as one part).  The pinion axis is parallel to local X at
//        nacelle-local (x = SUN_XLOC = -38.0, y = 0, z = PIVOT_Z + SYNC_CD =
//        133.5); the shaft diameter and its retention (clamp split vs. keyed
//        vs. co-printed with the pinion) are not yet chosen, and neither is the
//        pinion module/tooth count for the 1:1 pitch-radius-13.0 mesh.  Hub OD
//        must also clear the sun gear's pitch Ø26 at the SYNC_CD = 26 mm centre
//        distance.
//     2. ARM CLOCKING — the arm must be clocked to CRANK_PHASE = 206.0 deg
//        about that pinion axis at zero tilt (measured as the solver measures
//        it: ball at y = CRANK_R*sin(theta+CRANK_PHASE),
//        z = 133.5 + CRANK_R*cos(theta+CRANK_PHASE)).  As drawn the arm is at
//        an unclocked local +Z, which is NOT that pose.
//   Deliberately NOT bodged here: a half-correct hub would be a printable but
//   wrong part.  The linkage NUMBERS are solved and closed; this PART is not.
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
