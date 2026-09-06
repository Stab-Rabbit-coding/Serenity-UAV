// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Nacelle-local print frame: duct axis = local +Z, intake at Z = 0, azimuth
//   measured from local +X.  Consumed by nacelle_pod_50mm_tandem.scad and by
//   nacelle_esc_cover.scad, which must agree on every number in this file or
//   the cover will not fit the hole it covers.
// ===========================================================================
// =============================================================================
// nacelle_esc_bay.scad — the hinged-ESC bay interface, defined once
// =============================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Analysis and code by Claude (Claude Opus 5, Anthropic) under the author's
//           direction, per AGENTS.md §3 "Attribution and Licensing"
// License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date    : 2026-09-01  (Rev T4c)
//
// THE BOARD — owner direction, 2026-09-01
// ---------------------------------------
// Each of the two ESCs in a nacelle is TWO PCBs joined by a hinge:
//     power panel   23.0 mm
//     signal panel  10.0 mm
//     total         33.0 mm across the fold
//
// The hinge exists because the board cannot narrow.  32 mm is the floor set by
// Open-Secure-ESC's own `isolation_envelope.py` — 12.90 mm widest non-isolated
// part + 2 × (7.5 mm creepage + 1.43 mm inset) + 2 × 0.55 mm = 31.86 mm, off the
// ADM2582E/ADM2587E Table 6 clearance — and this pod's annulus is about 7 mm
// deep.  Folding does not make the board smaller; it makes its DEVIATION FROM
// THE ARC smaller, and that is the dimension the pod is short of.  Sagitta of a
// chord of width w on a circle of radius R is R − sqrt(R² − (w/2)²); at R 33:
//
//     one flat 33.0 mm board   4.42 mm   — 63 % of the annulus, gone
//     23.0 mm power panel      2.07 mm
//     10.0 mm signal panel     0.38 mm
//
// MEASURED FIT — tools/nacelle_esc_bay_fit.py.  That tool tests the OUTER
// CORNERS of each panel against the ray-cast skin, at radius
// sqrt(d_out² + (w/2)²) and azimuth φ ± atan((w/2)/d_out).  The corners are
// always the binding points, never the panel centre, which is why an earlier
// model that sized the bay as an annular SECTOR concluded the board should be
// wide and short — the exact opposite of the truth.
//
//     stack   length   Z span     area    vs as-built 32.0 × 66.1 = 2115 mm²
//     3.0 mm   74 mm   74–146   2442 mm²   115 %
//     3.5 mm   68 mm   74–140   2244 mm²   106 %
//     4.0 mm   62 mm   74–134   2046 mm²    97 %   <- BUILT
//     4.5 mm   58 mm   74–130   1914 mm²    91 %
//     5.0 mm   50 mm   74–122   1650 mm²    78 %
//     6.0 mm   16 mm   74– 88    528 mm²    25 %
//
// 4.0 mm is built: 1.6 mm of PCB leaves 2.4 mm for components across both faces
// plus mounting, and it recovers 97 % of the as-built board's area.  The fold
// also softens the cliff a flat board had — 4.0 → 5.0 mm of stack now costs
// 12 mm of length instead of all of it.
// =============================================================================

ESC_BAY_AZ      = [69, 249];  // [deg] hinge azimuth of each bay.  NOT free: 105
                              //   and 285 are the pod's two DEEP LOBES (annulus
                              //   alive aft to Z 163 at 6.2–6.4 mm, against
                              //   Z 135–147 elsewhere) and are where the EDF
                              //   spider arms are clocked, so each bay sits
                              //   directly over its own phase-lead crossing with
                              //   no circumferential run.  Also clear of the nav
                              //   cableway (az 0) and of the trunnion and
                              //   disconnect bay (az 180).
ESC_W_POWER     =  23.0;  // [mm] power panel width   (owner direction)
ESC_W_SIGNAL    =  10.0;  // [mm] signal panel width  (owner direction)
ESC_PCB_T       =   1.6;  // [mm] PCB thickness
ESC_STACK       =   4.0;  // [mm] radial envelope: PCB + parts both faces + mount
ESC_MOUNT_R     =  30.2;  // [mm] board inner face — equals the pod's
                          //   SLEEVE_BORE_R + CAVITY_DUCT_WALL, asserted there
ESC_BAY_Z0      =  74.0;  // [mm] bay forward end
ESC_BAY_Z1      = 134.0;  // [mm] bay aft end (62 mm of board + end clearance)
ESC_FIT         =   0.6;  // [mm] clearance per side around the board

// ── Access ───────────────────────────────────────────────────────────────────
// A board 33 mm across the fold cannot be threaded into a sealed annulus, so
// each bay is cut RADIALLY THROUGH THE SKIN and closed by a printed cover that
// drops into a rebate and finishes flush with the mould line.  The window is the
// union of the two panel footprints, so it is chevron-shaped and follows the
// fold — a rectangular window would either foul the fold or waste skin.
ESC_COVER_T     =   3.0;  // [mm] cover thickness — 3.0 rather than the 2.5 mm
                          //   minimum wall so an M3 counterbore still leaves
                          //   1.2 mm of material under the screw head
ESC_LEDGE_W     =   8.0;  // [mm] cover landing band around the window
ESC_LEDGE_T     =   2.5;  // [mm] material under the cover, radially
ESC_COVER_FIT   =   0.25; // [mm] clearance per side, cover into its rebate
ESC_BOSS_OD     =   7.0;  // [mm] insert boss OD
ESC_BOSS_INSET  =   4.0;  // [mm] boss centre inset from the window edge
ESC_SCREW_D     =   3.4;  // [mm] M3 clearance through the cover
ESC_CBORE_D     =   6.2;  // [mm] counterbore for an M3 BUTTON head (Ø5.7×1.65)
ESC_CBORE_DEPTH =   1.8;  // [mm] counterbore depth — head finishes flush
ESC_INSERT_D    =   3.5;  // [mm] M3 × 6 heat-set insert bore (pod M3_INSERT_D)
ESC_INSERT_L    =   6.0;  // [mm] insert depth              (pod M3_INSERT_L)
ESC_BOSS_DEPTH  = ESC_INSERT_L + 1.0;  // [mm] 6.0 of insert plus 1.0 of material
                          //   behind it, so a slightly over-driven insert does
                          //   not burst through into the cavity

// ── Cooling ──────────────────────────────────────────────────────────────────
// A 50 A ESC in a sealed CF-PETG annulus has no heat path at all, and CF-PETG
// conducts at ~0.25 W/mK — 2.5 mm of it over a 460 mm² footprint is 21.7 K/W,
// so conduction through the duct wall into the fan stream is not a path either.
// The cover therefore carries louvres at both ends, venting the bay to ambient.
//
// ** SIZED 2026-09-06 — and the earlier decision not to bleed was wrong. **
// This block used to say a duct bleed "would cost thrust, and stealing it
// without analysis is not a trade this file is entitled to make."  The analysis
// has now been done (`tools/nacelle_esc_thermal.py`) and the cost is small while
// every alternative fails:
//
//   path                                          R (K/W)   Tch at 28 A / 50 A
//   sealed bay, conduct through CF-PETG to stator   19.63     215 C / 632 C
//   same path in 6061 aluminium with a thermal pad   1.86      94 C / 246 C
//   BLEED AIR, 30 m/s through the bay                2.74      64 C / 148 C
//
// The stator sleeve is an EXCELLENT sink — 188 cm² of wetted area at 71 m/s
// gives 0.27 K/W — but it cannot be reached.  The 0.2 mm running fit between
// the sleeve OD and the pod bore is 5.33 K/W of still air ON ITS OWN, more than
// the pod wall, the sleeve wall and the stator sink combined even at a generous
// k = 1.2 W/m·K.  Filling it is not available: the sleeve slides in and out on
// its keys, and a thermal pad across a sliding joint shears on every service.
//
// So the heat leaves in the air, not through the walls.  The bay is a duct, fed
// from the inter-stage region where the static pressure is ~3.1 kPa above
// ambient, and vented through the louvres below.  At a 30 m/s bay velocity that
// is 4.85 g/s — **2.8 % of EDF1's mass flow, so roughly 1.4 % of the nacelle's
// thrust** — for a 61 K improvement over the sealed bay at hover.
//
// STILL OPEN, and it is the flow and not the geometry: the ACTUAL bay velocity
// depends on the loss coefficient of a circuit nobody has modelled.  The inlet
// is sized for the target flow at Cd 0.62; whether the bay delivers it needs
// CFD or a bench flow test.  See airframe/wings-nacelles/WBS.md §1.1.3.8.
ESC_LOUVRE_N    =   5;    // [count] slots per end
ESC_LOUVRE_W    =   1.2;  // [mm] slot width (Z) — 2 extrusions at a 0.6 nozzle
ESC_LOUVRE_L    =  12.0;  // [mm] slot length (circumferential)
ESC_LOUVRE_P    =   3.0;  // [mm] slot pitch

// ── Bleed inlet (Rev T4d, 2026-09-06) ────────────────────────────────────────
// Where the cooling air comes from.  It has to be Z 74–90: that is the only part
// of the bay where the POD's own bore is the flow boundary.  Aft of Z 90 the
// stator and aft-spider sleeves line the duct, so a hole in the pod wall there
// would open into the sleeve clearance, not into the airflow — and drilling
// both would put a bleed path across a sliding joint.
//
// Teardrop profile, not round: the hole axis is radial, so it is a HORIZONTAL
// hole in the print, and the top of a horizontal circle is an unsupported arc.
// A 45° apex removes it (3d-print-design FDM rules, "Horizontal holes").  It
// also adds a little area, which is free.
ESC_BLEED_N     =    4;   // [count] inlets per bay
ESC_BLEED_D     =  5.5;   // [mm] inlet diameter — 4 x Ø5.5 = 95 mm2, sized for
                          //   4.85 g/s at Cd 0.62 against a 3.1 kPa static rise
ESC_BLEED_Z     = [76.0, 80.0, 84.0, 88.0];  // [mm] stations, all inside 74–90


// ── Derived fold geometry ────────────────────────────────────────────────────
// Each panel is tangent to the same inner cylinder, so its half-angle is
// atan((w/2) / ESC_MOUNT_R) and the fold angle is the sum of the two.  At
// R 30.2 that is 20.85° + 9.40° = 30.25°, so the panels sit at 149.75° to each
// other — a shallow fold, well inside what a flex hinge will take.
function esc_a_pow() = atan((ESC_W_POWER  / 2) / ESC_MOUNT_R);
function esc_a_sig() = atan((ESC_W_SIGNAL / 2) / ESC_MOUNT_R);


// ── Module: esc_bay_footprint ────────────────────────────────────────────────
// The two panel envelopes, optionally grown by `pad` on every side.  `r_out`
// lets one footprint serve as the board pocket, the access window, and the
// cover's own outline — which is the point: three features that must match
// cannot be drawn three times.
module esc_bay_footprint(az_hinge, r_out, pad = 0) {
    union() {
        esc_panel_slab(ESC_W_POWER + 2 * (ESC_FIT + pad),
                       az_hinge + esc_a_pow(),
                       ESC_MOUNT_R - pad, r_out,
                       ESC_BAY_Z0 - pad, ESC_BAY_Z1 + pad);
        esc_panel_slab(ESC_W_SIGNAL + 2 * (ESC_FIT + pad),
                       az_hinge - esc_a_sig(),
                       ESC_MOUNT_R - pad, r_out,
                       ESC_BAY_Z0 - pad, ESC_BAY_Z1 + pad);
    }
}


// ── Module: esc_boss_cylinders ───────────────────────────────────────────────
// Six fastener positions per bay as long radial cylinders, to be clipped against
// the skin by the caller.  Three down each long side of the WIDE panel's window
// — the narrow panel's sides sit too close to the fold to carry a Ø7 boss.
module esc_boss_cylinders(az_hinge, dia) {
    off = ESC_W_POWER / 2 + ESC_FIT + ESC_BOSS_INSET;
    for (dy = [-off, off],
         z  = [ESC_BAY_Z0 + 6, (ESC_BAY_Z0 + ESC_BAY_Z1) / 2, ESC_BAY_Z1 - 6])
        rotate([0, 0, az_hinge + esc_a_pow()])
            translate([0, dy, z])
                rotate([0, 90, 0])
                    cylinder(d = dia, h = 60, center = false);
}
