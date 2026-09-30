// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Hull frame (canonical for ALL design artifacts): X = +port (left),
//   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
//   world origin.  Primary-component STLs published to airframe/stls/
//   are stored directly in hull frame, baked by tools/bake_hull_frame.py.
//   This file:
//     Part-local print frame, coaxial with the nacelle duct (duct axis =
//     local +Z, flow runs +Z), IDENTICAL to nacelle_nozzle_iris.scad's
//     frame so the part drops into the same seat: local Z = 0 is the
//     nacelle exit face, which sits at nacelle-local Z = NOZZLE_RING_Z
//     166.25 mm (serenity_assembly.py).  Hull placement follows the nacelle
//     pose exactly as the iris did (VERIFY with the assembly).
// ===========================================================================
// nacelle_nozzle_fixed.scad
// Serenity UAV Rev T6 — Nacelle FIXED OPEN nozzle (50 mm EDF bore)
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP.
// Written by Claude (Claude Opus 5.5, Anthropic) under the author's
// direction, 2026-09-29, per AGENTS.md §3 "Attribution and Licensing".
// License: CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0
//
// ── Why this part exists ──────────────────────────────────────────────────
//   Owner decision 2026-09-29 (docs/plans/2026-09-29-001-tw-recovery-stem-
//   to-stern-plan.md, D-TW-3): for Phases 5-10 the variable-area nozzle is
//   replaced by this one-piece fixed nozzle held at the HOVER (open) exit.
//   The servo-scheduled iris (nacelle_nozzle_iris.scad + plan
//   docs/plans/2026-09-28-001-feat-nacelle-nozzle-servo-drive-plan.md) is
//   DEFERRED to Phase 11b (deferred/WBS.md), not deleted.
//
//   Rationale, all from the T/W recovery plan §6.1:
//     - hover is the T/W-critical case, and the iris was already scheduled
//       to hold its open position from 90 deg to 145 deg tilt and to fail
//       open, so hover flow is unchanged by fixing the nozzle open;
//     - deletes 8 flaps, unison ring, 32 pins and the servo drive:
//       ≈ −85 g (0.19 lbm) per aircraft against the V1 servo iris;
//     - takes an entire open mechanism (servo, spring cord, gateway choice
//       D-NZ-1, bench load check U8) off the first-flight critical path;
//     - COST: the 75 % convergent cruise setting is lost, so cruise
//       efficiency / top speed drop by an amount not quantified in this repo
//       (no drag polar — docs/flight_envelope.md §2.2).
//
// ── Exit radius: built to the REQUIREMENT, not to the iris mesh ─────────
//   airframe/AGENTS.md sets the hover exit at 105 % of the 25 mm bore RADIUS:
//   NOZZLE_OPEN_R = 26.25 mm [REF-CAD-005 for the variable-nozzle principle].
//   Measured 2026-09-29 with trimesh on the committed
//   airframe/stls/nacelles/nozzles/nacelle_nozzle_iris-open.stl, the iris's
//   actual FLOW radius at its trailing edge is 23.77 mm (95 % radius, 90 %
//   area): NOZZLE_OPEN_R tracks the flap HINGE LINE (outer surface), and the
//   2.5 mm flap wall sits inboard of it.  The modelled iris therefore never
//   reached its own open requirement.  This part puts the 26.25 mm on the
//   FLOW surface, i.e. it meets the requirement.
//
//   Ideal ducted-fan momentum theory at fixed shaft power gives
//   T^3 = 2·rho·A_exit·P^2, so T ∝ A_exit^(1/3) (a diffusing exit raises
//   static thrust per watt).  Against the as-modelled iris that is
//   (26.25^2 / 23.77^2)^(1/3) = 1.068, i.e. up to +6.8 % static thrust at
//   equal power — an IDEAL UPPER BOUND, not a prediction: the real fan
//   unloads, draws different current and may separate in the diffuser.
//   FIXED_EXIT_R is a parameter so the thrust stand (T/W plan TW-1 / T3)
//   can sweep printed variants (e.g. 23.75 / 25.00 / 26.25 mm) and pick the
//   measured optimum.  The 2.39 deg diffuser half-angle at 26.25 mm is well
//   under the ~7 deg conical-diffuser separation guideline (engineering
//   rule of thumb, NOT a cited standard — VERIFY on the stand).
//
// ── Geometry (part-local, mm; profile revolved about local Z) ───────────
//   Interface zone, UNCHANGED from nacelle_nozzle_iris.scad Rev T so the
//   pod's Ø72 exit pocket and bond joint need no edit:
//     - bonding lip Z −3..0, annulus r 27.5..35.6 (spigots over the duct
//       tube, shoulders on the exit face — same positive stop);
//     - outer skin r 35.6 over Z 0..8, tapering to 33.5 at Z 15 (the cowl's
//       aft narrowing, as the iris housing had it).
//   Flow path:
//     - throat liner r 25.0 (flush with the EDF bore) over Z 0..15;
//     - conical diffuser r 25.0 → FIXED_EXIT_R over Z 15..EXIT_Z.
//   Overall length EXIT_Z = 15 + 30·cos(PHI_OPEN) = 44.97 mm: identical to
//   the iris with its 30 mm flaps at PHI_OPEN, so the hover ground-clearance
//   reach (tools/nacelle_mass_cg.py ROT_ASSY_TIP_Z) is unchanged.
//
//   Layout is the iris's own external silhouette minus flaps and bosses:
//   a housing with a SEALED internal void between liner and skin, closed aft
//   by a 2 mm web at Z 13..15, stiffened by RIB_N radial ribs; the housing's
//   aft face steps down onto a single-wall 2.5 mm diffuser cone exactly
//   where the iris's aft face stepped down onto its flap row.  A faired
//   boat-tail variant was built and measured first (42.7 g per nozzle — the
//   converging skin and cone merge into a thick solid wedge) and rejected.
//   A sealed void keeps the mesh globally watertight
//   (tools/validate_stls.py rule 1) and prints as-is; lip-down needs no
//   support (every surface leans ≤ 9 deg from vertical).
//
//   Walls: 2.5 mm = 4 × 0.6 mm perimeters + margin, the repo's CF-PETG
//   minimum wall (docs/MASS_AUDIT_CARGO_WING_ROOT.md §3); 2.0 mm skin is
//   the iris housing's own skin thickness (non-primary, piloting shell).
//
// ── Mass (measured 2026-09-29) ───────────────────────────────────────────
//   32,150 mm³ × RHO_PRINT 1.05e-3 g/mm³ = 33.8 g (0.074 lbm) per nozzle;
//   CG local Z 15.34 → nacelle Z 181.6.
//
// ── Material / print ──────────────────────────────────────────────────────
//   20 % CF-PETG (REF-MAT-002), hardened nozzle.  Lip DOWN on the bed,
//   0.15 mm layers, 4 perimeters, 100 % infill (thin walls are all
//   perimeter anyway — MASS_AUDIT §1 RHO_PRINT note).  Exhaust is EDF
//   bypass air only (no combustion), so CF-PETG's thermal limit is not
//   engaged; ESC heat stays in the forward bays.
//
// ── Fits (mate, target, clearance) ───────────────────────────────────────
//   Bonding lip ID 55.0  | nacelle duct tube OD 55.0 | epoxy bond, as iris
//   Bonding lip OD 71.2  | pod exit pocket Ø≈72     | 0.4 mm/side, as iris
//
// Render:
//   make -C airframe/FreeCAD-scripts ../stls/nacelles/nozzles/nacelle_nozzle_fixed.stl
//   Stand-sweep variant: openscad -D FIXED_EXIT_R=25.0 -o <out> <this file>
// ===========================================================================

$fn = 180;                  // facet count for the revolved profile

// ── Interface constants (copied from nacelle_nozzle_iris.scad Rev T) ─────
// Duplicated rather than `include`d: that file executes its own RENDER_PART
// dispatch at top level and is now a DEFERRED (Phase 11b) source.  If the
// pod's exit pocket ever changes, change it in both files.
BORE_R          = 25.0;     // [mm] 50 mm EDF bore radius
THROAT_WALL     =  2.5;     // [mm] liner wall (CF-PETG minimum wall)
THROAT_OUTER_R  = BORE_R + THROAT_WALL;   // [mm] = 27.5, duct tube OD
THROAT_LEN      = 15.0;     // [mm] exit face (Z 0) to the old hinge line
HOUSING_OUTER_R = 35.6;     // [mm] outer skin radius in the pocket zone
HOUSING_AFT_R   = 33.5;     // [mm] outer skin radius at Z = THROAT_LEN
RING_H          =  8.0;     // [mm] Z where the skin starts its aft taper
HOUSING_LIP_H   =  3.0;     // [mm] forward bonding lip depth
FLAP_LENGTH     = 30.0;     // [mm] iris flap length (plan 005 R1 trim)
NOZZLE_OPEN_R   = 26.25;    // [mm] REQUIRED hover exit = 105 % of BORE_R

// Iris open swing angle, kept only to reproduce the iris's overall length.
PHI_OPEN = asin((THROAT_OUTER_R - NOZZLE_OPEN_R) / FLAP_LENGTH);  // 2.39 deg

// ── Fixed-nozzle parameters ──────────────────────────────────────────────
FIXED_EXIT_R = NOZZLE_OPEN_R;   // [mm] FLOW radius at the exit plane;
                                //   sweep on the thrust stand (TW-1/T3)
EXIT_Z       = THROAT_LEN + FLAP_LENGTH * cos(PHI_OPEN);  // [mm] = 44.97
SKIN_T       =  2.0;            // [mm] outer skin thickness (iris housing)
WEB_T        =  2.0;            // [mm] aft closing web of the housing void
RIB_N        =  3;              // [count] radial stiffening ribs in the void
RIB_W        =  2.0;            // [mm] rib tangential thickness
RIB_EMBED    =  0.5;            // [mm] rib overlap INTO the liner — keeps
                                //   rib faces off the void surfaces, so the
                                //   CGAL union has no coincident faces

// Exit-lip outer radius: the 2.5 mm cone wall carried to the exit plane.
EXIT_OUTER_R = FIXED_EXIT_R + THROAT_WALL;

// Housing void top (the aft web occupies VOID_TOP..THROAT_LEN).
VOID_TOP = THROAT_LEN - WEB_T;                            // [mm] = 13.0

// Skin outer radius vs Z, as the iris housing: flat to RING_H, then a
// linear taper to HOUSING_AFT_R at Z = THROAT_LEN.
function skin_outer_r(z) = z <= RING_H ? HOUSING_OUTER_R
    : HOUSING_OUTER_R - (HOUSING_OUTER_R - HOUSING_AFT_R)
                        * (z - RING_H) / (THROAT_LEN - RING_H);

assert(FIXED_EXIT_R >= 20 && FIXED_EXIT_R <= 27.5,
       "FIXED_EXIT_R outside the range the cone/OML step can carry");

// ONE (r, z) profile, revolved about Z, containing the sealed housing void
// as a HOLE, so the void needs no 3D boolean subtraction at all.
module nozzle_profile() {
    difference() {
        polygon([
            [THROAT_OUTER_R,  -HOUSING_LIP_H],  // lip ID, forward face
            [THROAT_OUTER_R,   0],              // lip ID at the exit face
            [BORE_R,           0],              // step in to the flow bore
            [BORE_R,           THROAT_LEN],     // end of the parallel throat
            [FIXED_EXIT_R,     EXIT_Z],         // diffuser flow exit
            [EXIT_OUTER_R,     EXIT_Z],         // exit lip, outer corner
            [THROAT_OUTER_R,   THROAT_LEN],     // cone outer, back at Z 15
            [HOUSING_AFT_R,    THROAT_LEN],     // housing aft face (step)
            [HOUSING_OUTER_R,  RING_H],         // skin taper starts at Z 8
            [HOUSING_OUTER_R, -HOUSING_LIP_H]   // lip OD, forward face
        ]);
        // Sealed void.  Inner edge sits 0.01 mm OUTSIDE the liner line and
        // the floor 0.01 mm above Z 0, so no void edge lies on a profile
        // edge (2D boolean stays clean; revolved solid stays 2-manifold).
        polygon([
            [THROAT_OUTER_R + 0.01,               0.01],
            [THROAT_OUTER_R + 0.01,               VOID_TOP],
            [skin_outer_r(VOID_TOP) - SKIN_T,     VOID_TOP],
            [HOUSING_OUTER_R - SKIN_T,            RING_H],
            [HOUSING_OUTER_R - SKIN_T,            0.01]
        ]);
    }
}

module nacelle_nozzle_fixed() {
    union() {
        rotate_extrude() nozzle_profile();
        // Radial ribs bridging liner to skin through the void, drawn as an
        // (r, z) plate so the outer edge can follow the skin taper:
        //   inner edge r 27.0     — RIB_EMBED inside the 25..27.5 liner;
        //   outer edge r 34.0 over Z 0.5..8 (skin 33.6..35.6), sloping to
        //     r 33.0 at Z 13.5 (inside the skin at Z 13: 32.1..34.1, and
        //     inside the solid aft web at Z 13.5, whose OML is r 33.95);
        //   bottom Z 0.5 — floats 0.5 mm above the void floor rather than
        //     dipping into the lip, because below Z 0 the lip bore (r 27.5)
        //     is the duct-tube spigot and must stay clear;
        //   top Z 13.5 — 0.5 mm into the aft web.
        // Every edge is either inside solid or inside the void, never on a
        // void surface, so the union has no coincident faces.
        for (i = [0 : RIB_N - 1])
            rotate([0, 0, i * 360 / RIB_N + 30])   // clear of seam at 0 deg
                rotate([90, 0, 0])
                    linear_extrude(height = RIB_W, center = true)
                        polygon([
                            [THROAT_OUTER_R - RIB_EMBED,            0.5],
                            [THROAT_OUTER_R - RIB_EMBED,            VOID_TOP + 0.5],
                            [skin_outer_r(VOID_TOP + 0.5) - 0.95,   VOID_TOP + 0.5],
                            [HOUSING_OUTER_R - SKIN_T + 0.4,        RING_H],
                            [HOUSING_OUTER_R - SKIN_T + 0.4,        0.5]
                        ]);
    }
}

nacelle_nozzle_fixed();
