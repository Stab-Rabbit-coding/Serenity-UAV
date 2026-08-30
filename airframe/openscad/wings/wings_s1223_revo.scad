// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Hull frame (canonical for ALL design artifacts): X = +port (left),
//   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
//   world origin.  Primary-component STLs published to airframe/stls/
//   are stored directly in hull frame, baked by tools/bake_hull_frame.py
//   (marker 'SerenityUAV HULL-FRAME R1' in the binary STL header).
//   NEVER re-bake a mesh derived from an already-baked file.
//   This file:
//     Wing axes are parallel to hull axes (identity rotation); the
//     published wing STLs are baked to hull frame by translation only
//     (COMPONENTS['Wing_Port'] / COMPONENTS['Wing_Stbd']).  Baked
//     hull-frame bounds (Rev R1, chord 129/93 mm, zero sweep):
//       port  X -93.0..+4.7,  stbd X -347.7..-250.0;
//       both  Y  -7..+122,    Z +48..+77 mm.  After regeneration, re-run:
//         python3 tools/bake_hull_frame.py Wing_Port Wing_Stbd
// ===========================================================================
// =============================================================================
// wings_s1223_revo.scad
// Serenity UAV — Rev R1 — Wing Pair with Selig S1223 Airfoil Profile
// =============================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Project : Serenity-class Tilt-Rotor UAV (24-inch scale, Firefly TV ship)
// License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date    : 2026-05-24
// Revision: Rev R1 (2026-06-14)
//   - WING_CHORD_ROOT reduced 161 → 129 mm to match canonical desktop model
//     (s_wings_both_shell24.stl, scale 2.929× from Thingiverse s_wings_both.stl)
//   - WING_CHORD_TIP reduced 104 → 93 mm, preserving original taper ratio 0.718
//   - WING_SWEEP_LE zeroed (12 → 0 mm): leading edge is now straight root-to-tip,
//     matching the canonical Serenity straight-LE planform
//   - Span (WING_SEMI_SPAN = 85.7 mm) unchanged
//   Aerodynamic note: wing area reduced from 22 717 mm² to 19 025 mm² (both wings).
//   At 40 kt cruise: L ≈ 7.6 N vs. 9.1 N previously; still ~22 % AUW contribution.
//     ^ SUPERSEDED AT REV T1 — this figure is for the true S1223 section and
//       does NOT describe the built wing.  See "SECTION DESIGNATION AND DATA".
//   Re at root (40 kt, 129 mm chord) ≈ 182 000 (ISA SL, ν = 1.46e-5 m²/s);
//     the chord is unchanged at Rev T1, so Re is unchanged.  The older "177 000"
//     figure here corresponds to ν ≈ 1.51e-5 (≈ 20 °C) and is not wrong, just
//     stated at a different air temperature — both are LOW-Re (< 5e5).
//   Carried forward from Rev R (2026-06-11).
//
// Description
// -----------
// Replaces s_wings_both_shell24.stl (Thingiverse origin, flat-plate cross-
// section) with a new wing pair using the Selig S1223 high-lift, low-Reynolds-
// number airfoil.  Planform matches the canonical 24-inch Thingiverse desktop
// model (root 129 mm, tip 93 mm, straight leading edge, taper ratio 0.718).
// The wing is longer in span than the original panel (85.7 mm vs. 56 mm panel
// from the desktop STL) giving a less stubby planform while preserving chord
// proportions and the straight canonical LE.
//
// Why S1223
// ---------
// HISTORICAL — WHY S1223 WAS CHOSEN IN REV R1.  At cruise (40 kts, Re ≈ 1.8e5
// at root) the true S1223 delivers CL ≈ 1.55 at 3° AoA versus CL ≈ 0.32 for the
// original flat-plate wing, so wing lift rose from ~3 % to ~22 % AUW — nearly a
// 7× improvement with no change to the outward planform silhouette.
//
// ⚠ THIS NO LONGER DESCRIBES THE BUILT WING.  Rev T1 scales the thickness
// envelope ×1.46 (root) and ×2.20 (tip) to swallow the Ø20.4 spar, so the built
// sections are S1223/t17.7 and S1223/t26.7, not S1223.  The camber line — the
// source of the high-lift behaviour — IS preserved, which is the reason to
// expect the change to be less severe than the thickness numbers suggest, but
// no performance figure above transfers.  See "SECTION DESIGNATION AND DATA".
// Reference: Selig & Guglielmo (1997), "High-Lift Low Reynolds Number Airfoil
//            Design," Journal of Aircraft, Vol.34, No.1, pp.72–79.
//            UIUC Airfoil Database: https://m-selig.ae.illinois.edu/ads/afplots/s1223.gif
//
// Canon Fidelity
// --------------
// Changes vs. original Thingiverse flat-plate wing:
//   1. Cross-section: flat-plate → S1223 profile (camber + LE radius visible
//      from front view; lower surface slightly reflexed near TE).
//   2. Root attachment tab: squared face replaces original tab geometry — VERIFY
//      fuselage slot before print (see WING_ROOT_TAB_* parameters).
//   3. Tip geometry: simple truncated tip; original had a rounded fairing which
//      must be validated against the pylon boss interface.
// Unchanged from canonical desktop planform: root/tip chord ratio (0.718),
// straight leading edge (zero sweep), wing-to-pylon mount pocket (WING_SLOT_W /
// WING_SLOT_H), all structural hardware interface dimensions.
//
// SECTION DESIGNATION AND DATA — Rev T1 (re-derived 2026-08-29)
// ------------------------------------------------------------
// ⚠ THE BUILT SECTION IS NOT A SELIG S1223.  It shares S1223's CAMBER LINE and
// nothing else.  Naming it "S1223" in analysis, in the BOM, or in a
// performance claim is the single most misleading thing this file could do, so
// the built sections carry their own designations:
//
//     root   S1223/t17.7    S1223 camber line, thickness envelope x1.46
//     tip    S1223/t26.7    S1223 camber line, thickness envelope x2.20
//
// (The filename keeps "s1223" for continuity of the git/STL/BOM trail.  The
// SECTION does not.)
//
// GEOMETRY, DERIVED FROM THE TABULATED COORDINATES BELOW, NOT QUOTED
// ------------------------------------------------------------------
// Computed by sampling S1223_UPPER/S1223_LOWER at 1/20000 chord.  The camber
// line is NOT scaled (see s1223_section()), so camber is identical in all three
// columns and only the thickness envelope moves:
//
//                          baseline      root built     tip built
//   thickness scale          1.000          1.460          2.200
//   max t/c                 12.14 %        17.72 %        26.71 %
//     at x/c                 0.198          0.198          0.198
//   max camber               8.67 %         8.67 %         8.67 %
//     at x/c                 0.490          0.490          0.490
//   LE radius r/c           0.02502        0.05333        0.12110
//   LE radius, abs           3.23 mm        6.88 mm       11.26 mm
//                          (at c=129)     (at c=129)     (at c=93)
//
// CORRECTION TO THE PREVIOUS HEADER.  It claimed "Maximum thickness : 12.14%
// chord at 22.6% chord" and "Maximum camber : 8.65% chord at 39.4% chord".
// Both MAGNITUDES were about right; both CHORDWISE LOCATIONS were wrong.  The
// re-derivation above returns 19.8 % and 49.0 %, which is exactly the published
// characterisation of S1223 (max thickness 12.1 % at 19.8 %, max camber 8.7 %
// at 49.0 % — UIUC / airfoiltools, REF-CAD-006).  The old figures were never
// traceable to the coordinate table this file actually builds from.
//
// LE radius scales as t_scale² — a consequence of scaling the thickness
// envelope of a fixed shape, verified numerically above (0.02502 × 1.46² =
// 0.05333; × 2.20² = 0.12110).  The tip's leading edge is therefore 3.5× the
// baseline radius and 12 % of its own chord: geometrically it is closer to a
// strut fairing nose than to a low-Reynolds high-lift section.
//
// WHAT PUBLISHED S1223 DATA STILL APPLIES — AND WHAT DOES NOT
// -----------------------------------------------------------
// Flow regime, stated first because it governs which methods are even legal:
//   Re = V·c/ν at 40 kt (20.58 m/s), ν = 1.46e-5 m²/s (ISA SL, 15 °C):
//     root  (c 129 mm)  Re ≈ 182,000
//     MAC   (c 111 mm)  Re ≈ 156,000
//     tip   (c  93 mm)  Re ≈ 131,000
//   All below Re = 5e5, i.e. the LOW-REYNOLDS regime where laminar separation
//   bubbles dominate and published polars do not transfer between Reynolds
//   numbers, let alone between sections.
//
//   SURVIVES — the geometric camber figures.  Camber is unscaled by
//   construction, so max camber 8.67 % at 49.0 % chord is exact for the built
//   sections, not an approximation.
//
//   PARTIALLY SURVIVES, ROOT ONLY — zero-lift angle and lift-curve slope.
//   Thin-airfoil theory makes dc_l/dα = 2π and α_(L=0) functions of the CAMBER
//   LINE alone, independent of thickness, so preserving the camber line is the
//   reason to expect the linear range to be broadly retained.  But that theory
//   is valid for THIN sections; at 17.7 % t/c the root is already outside its
//   comfortable range and at 26.7 % the tip is emphatically outside it.  Treat
//   this as a reason for optimism at the root and as nothing at all at the tip.
//
//   DOES NOT SURVIVE — every performance number.  c_l,max, the L/D figure, the
//   drag polar, and the stall behaviour all depend on the thickness
//   distribution, the LE radius, and the separation bubble, and all three have
//   changed substantially.  c_l,max in particular comes only from measurement
//   or computation at the actual Re; it cannot be carried over from a different
//   section and it cannot be derived from theory.
//
//   NOT CHARACTERISED AT ALL — the printed surface.  FDM layer lines act as a
//   de-facto trip strip whose effect at these Reynolds numbers is real and
//   uncharacterised for this part.
//
// The Rev R1 claims below (CL ≈ 1.55 at 3° AoA, CL_max ≈ 2.0, L/D 30–35, and
// the 7.6 N cruise-lift figure derived from them) are RETAINED AS HISTORY ONLY
// and are marked at each use.  They describe the true S1223 and MUST NOT be
// applied to the built wing.  Establishing real numbers needs XFOIL or a
// transition-sensitive RANS run at Re 1.3e5–1.8e5, or a bench/tunnel result —
// tracked in TODO §0.8 and docs/flight_envelope.md.
//
// Reference: Selig, M.S. & Guglielmo, J.J. (1997), "High-Lift Low Reynolds
// Number Airfoil Design," Journal of Aircraft 34(1), 72–79; coordinates from
// the UIUC Airfoil Coordinates Database s1223.dat (REFERENCES.md REF-CAD-006).
//
// Coordinate System (internal / module geometry)
// -----------------------------------------------
//   X: chordwise    (X=0 = leading edge, X=CHORD = trailing edge)
//   Y: thickness    (Y>0 = upper surface)
//   Z: spanwise     (Z=0 = wing root, Z=SEMI_SPAN = wing tip)
//
// Assembly output orientation (after wings() reorientation transform)
// -------------------------------------------------------------------
//   X: spanwise     (X=0 = root / fuselage face, X=SEMI_SPAN = tip)
//   Y: chordwise    (Y=0 = leading edge, Y=CHORD = trailing edge)
//   Z: thickness    (Z>0 = upper surface = toward sky in level flight)
//
//   This matches the canonical Serenity hull orientation measured from
//   s_wings_both_shell24_50mm.stl: full-span X=171mm, chord Y=161mm,
//   thickness Z=24mm.  The wings() module applies a coordinate permutation
//   (X←Z, Y←X, Z←Y) to convert internal geometry to assembly orientation.
//
//   3° incidence is applied by wing_nacelle_pylon_revo.scad at the
//   pylon attachment face — not baked into this geometry.
//
// Render Commands
// ---------------
//   Port wing (left):
//     openscad -o wing_port_s1223_revo.stl \
//              wings_s1223_revo.scad -D RENDER_SIDE=1
//   Starboard wing (right):
//     openscad -o wing_stbd_s1223_revo.stl \
//              wings_s1223_revo.scad -D RENDER_SIDE=-1
//   Both wings (single file, for reference):
//     openscad -o s_wings_both_s1223_revo.stl wings_s1223_revo.scad
//
// References
// ----------
//   [1] Selig, M.S. & Guglielmo, J.J. (1997). "High-Lift Low Reynolds Number
//       Airfoil Design." Journal of Aircraft, 34(1), 72–79.
//   [2] UIUC Airfoil Database — S1223: m-selig.ae.illinois.edu/ads.html
//   [3] wing_nacelle_pylon_revo.scad — pylon mount pocket dimensions.
//   [4] CLAUDE.md — fabrication standards (4-perimeter CF-PETG, 3 mm wall).
//   [5] bom_revO.csv — CF-TUBE-12MM (12 mm OD × 1.5 mm wall) wing spar spec.
//
// =============================================================================


// =============================================================================
// ── Parameter Block ───────────────────────────────────────────────────────────
// =============================================================================

// ── Wing planform — derived from canonical s_wings_both_shell24.stl ──────────
// Canonical source: archives/stl/s_wings_both_shell24.stl (Thingiverse
// s_wings_both.stl × 2.929 scale factor).  One-panel measurements:
//   root face Y chord = 128.8 mm; tip face Y chord ≈ 92.5 mm (taper 0.718).
//   Panel span (root face to tip face) = 56.3 mm; full span per half = 85.7 mm
//   (includes central fuselage half-width in the desktop model).
//   LE sweep in desktop model: 14.2 mm — zeroed here to give a straight LE
//   that is more faithful to the canonical Serenity silhouette.
// WING_CHORD_ROOT rounded up from 128.8 mm to even 129 mm.
// WING_CHORD_TIP  = round(92.5) = 93 mm  (Thingiverse: 31.6 × 2.929 = 92.6 mm).
WING_CHORD_ROOT = 129.0;  // [mm] root chord (at fuselage face) — from canonical STL
WING_CHORD_TIP  =  93.0;  // [mm] tip chord  (at pylon face)    — from canonical STL
WING_SEMI_SPAN  =  85.7;  // [mm] root face to tip face          — maintained from Rev R
WING_SWEEP_LE   =   0.0;  // [mm] LE sweep: 0 = straight LE (matches Serenity canon)
WING_DIHEDRAL   =   0.0;  // [mm] tip rise vs. root (+Z in output); Serenity ≈ 0

// ── Wing section scaling ──────────────────────────────────────────────────────
// The S1223 normalised profile is scaled by chord at each span station.
// THICKNESS_SCALE=1.0 → full S1223 t/c (12.14%); reduce to thin down profile.
// Reducing below 1.0 preserves camber ratio but reduces absolute thickness.
// Set to 0.90 to lower max thickness from 7.9mm to 7.1mm at the root (subtle).
// REV T1 (2026-08-29, plan 003 KTD2): 1.00 → 1.46.  THE ROOT OML NOW MOVES.
// Through every prior revision this stayed at 1.00 and only the TIP was
// thickened — the root had 15.60 mm of section against a Ø8.3 bore and was
// never the binding station.  The unified Ø20.4 spar breaks that: at the
// 28.0 mm station the root section is 15.60 mm deep against a bore that needs
// 20.4 + 2 × 1.16 = 22.72 mm, so at 1.00 the bore BREAKS OUT of the root skin
// by 2.40 mm top and bottom.
//
// 1.456 is the exact solved figure (tools/wing_spar_station_fit.py --bore 20.4
// --station 28, which now solves the ROOT as well as the tip for exactly this
// reason); 1.46 is used so the wall is not sitting on its own limit — the same
// convention Rev S1b (1.447 → 1.45) and U6 (1.5505 → 1.56) applied at the tip.
// It gives 1.19 mm over the bore against the 1.16 mm floor.
//
// AERO CONSEQUENCE — READ THIS BEFORE CITING ANY LIFT FIGURE FROM THIS FILE.
// Root t/c goes 12.14 % → 17.7 %.  S1223 is a high-lift low-Reynolds section
// CHARACTERISED at 12.14 % t/c; scaling its thickness ~1.5× changes its
// behaviour qualitatively, not by a correction factor.  The 7.6 N cruise-lift
// figure in this file's header, and everything derived from it, is therefore
// UNVERIFIED for the built section (plan 003 RISK-1).  Do not present the
// re-lofted wing as an S1223 performance match until a CFD or bench result
// exists (tools/wing_cfd_openfoam.py is still blocked on mesh generation).
THICKNESS_SCALE =  1.46;  // [1.0 = full S1223 t/c; ROOT-station thickness scale]
                           // Camber line is NOT affected — only thickness offset.
                           // Below 0.75: separation bubble risk at Re < 100k.
                           // The tip uses THICKNESS_SCALE_TIP (below); the loft
                           // tapers linearly between the two.

// ── Tip-station thickness (Rev R1a) ──────────────────────────────────────────
// The tip chord (93 mm) at full S1223 t/c gives only ≈ 11.3 mm perpendicular
// max thickness (12.14% × 93) — LESS than the 12.3 mm spar bore, so a straight
// full-span 12 mm spar cannot be skinned at the tip without local thickening.
// THICKNESS_SCALE_TIP fattens ONLY the tip station (root OML unchanged); the
// loft tapers linearly between root and tip.
//
// REV S1b (2026-08-16): 1.25 → 1.447, forced by the SPAR_BORE_STATION move to
// 45.15 mm.  That station is 48.5 % of the tip chord, where the baseline
// section is only 7.34 mm deep — at 1.25 the Ø8.3 bore would carry just
// 0.44 mm of skin, below the 1.16 mm the root already runs at.  1.447 is the
// exact figure; 1.45 is used so the wall is not sitting on its own limit
// (gives 1.17 mm).  Measured by tools/wing_spar_station_fit.py; do not
// hand-tune it.
//
// U6 (2026-08-25): 1.45 → 1.56.  The 1.447 figure above was measured against
// the PRE-U1 S1223 table (a hand-approximated set of coordinates).  U1
// replaced that table with the validated UIUC S1223 points, which are a
// genuinely different shape at 48.5 % tip chord — deeper near mid-chord,
// shallower aft, where this bore sits.  Re-measuring wall-over-spar with
// tools/wing_internal_clearance.py against the corrected table found the tip
// wall had dropped to 0.82 mm (below the 1.16 mm floor) at the old 1.45
// scale.  1.5505 is the new exact figure (verified: `Section(chord_tip,
// t_scale).depth(SPAR_BORE_STATION)/2 - SPAR_BORE_OD/2 == 1.16` at that
// scale); 1.56 is used for the same "not sitting on its own limit" margin
// (gives 1.19 mm).  Root is unaffected (unchanged THICKNESS_SCALE, 2.46 mm
// wall there) -- this is purely a tip-airfoil-correction consequence.
//
// This is now a THICKNESS-only multiplier in fact as well as in name — see
// s1223_section() below.  It no longer stretches the camber line, so the tip
// keeps S1223's canonical camber instead of being driven up.
// Tip t/c is now ≈ 11.5 % at 1.56 (thickness only) -- see U6 note above;
// the "13.45 % → 19.47 %" figure below predates the U1 airfoil correction and
// is stale (kept in the historical record, not restated as current).
//
// CANON NOTE: this is an outer-mold-line change local to the wingtip; verify
// against the canonical Serenity wing silhouette before committing to print
// (see TODO.md §1.1.2, U8 canon-check). Lower the value only if the bore
// stays skinned per tools/wing_internal_clearance.py.
// UNVERIFIED BY CFD: the OpenFOAM study intended to quantify the drag penalty
// of the thicker tip at Re ≈ 2.1e5 is blocked on mesh generation
// (tools/wing_cfd_openfoam.py, WIP).  The camber-preservation argument does
// not depend on it, but the absolute penalty of the thicker tip is not yet
// quantified.
// REV T1 (2026-08-29, plan 003 KTD2): 1.56 → 2.20, forced by the same Ø20.4
// unified spar that moved the root.  2.190 is the exact solved figure
// (tools/wing_spar_station_fit.py --bore 20.4 --station 28); 2.20 keeps the
// wall off its own limit per the convention above, giving 1.21 mm.
// Tip t/c goes 18.93 % → 26.7 %.  See the RISK-1 note under THICKNESS_SCALE —
// it applies MORE strongly here, and this scale is also well outside the
// 0.85–1.0 range s1223_section()'s decomposition was written for, which is why
// tools/wing_airfoil_integrity.py now validates the sections at their ACTUAL
// scales rather than only validating the t_scale = 1.0 table (plan 003 RISK-2).
THICKNESS_SCALE_TIP = 2.20;  // [tip thickness multiplier; root stays THICKNESS_SCALE]

// ── Structural spar bore (Rev T1 — unified 20 mm FIXED CF spar) ─────────────
// UNIFIED FIXED SPAR (2026-08-29, plan 003 KTD1/KTD4).  The spar stops being a
// rotating drive shaft and becomes a BONDED STRUCTURAL MEMBER OF THE WING:
//
//   • It is a 20 × 16.3 mm roll-wrapped CARBON FIBRE tube, FIXED — it does not
//     rotate.  The nacelle now pivots on a trunnion ring carried at its own
//     inboard face (plan 003 KTD3), so nothing about the tilt motion is
//     transmitted through this tube.
//   • Because it is fixed and bonded over its full span, it is the wing's
//     PRIMARY BENDING MEMBER, not a shaft the wing merely rides on.  That is
//     the whole structural point of the change and it re-routes the root load
//     path — see the WING ROOT LOAD PATH block below.
//   • Its 16.3 mm bore carries the FOUR 10 AWG ESC feeds, coaxially with the
//     tilt axis.  This is why the tube is 20 mm and not 8 mm: it is sized by
//     WIRE VOLUME, not by torque.  4 × Ø5.5 conductors circumscribe a 13.28 mm
//     circle (exact 4-circle packing ratio 1 + √2, tools/spar_bundle_fit.py),
//     so the 11.0 mm bore proposed in docs/plans/2026-08-27-nacelle-wiring-plan.md
//     does not fit at all, and a 16 mm tube fits only as 16 × 14 with 0.36 mm
//     radial — no room for the bundle to twist.
//
// WHY THE WIRES HAD TO COME ON-AXIS.  The old double-D conduit sat 17.65 mm
// FORWARD of the tilt axis, so every nacelle transition dragged the harness
// through a ~45 mm arc (plan 003 Problem Frame; logged unclosed as U6 in
// docs/plans/2026-08-26-001-nacelle-esc-intake-integration-plan.md).  On the
// axis, that sweep becomes distributed TORSION spread along the captive span
// instead of a swept arc at a fixed port.
//
// The bore stays a SINGLE STRAIGHT cylinder at a fixed chordwise station
// (parallel to the straight LE → no plan-view skew) centred on the airfoil
// CAMBER MIDLINE so it stays skin-enclosed as the section tapers.
//
// CLEARANCE, NOT PRESS FIT — and deliberately so.  0.2 mm/side is a BONDING
// gap, not a rotating gap: the tube is epoxy-bonded into the wing (West System
// 105/206, the same system §6/§7 of docs/structural_analysis.md already
// specifies for CF stock in this airframe).  A press fit into a printed
// CF-PETG bore would rely on interference against a part whose bore is the
// least dimensionally repeatable feature on it, and would put a hoop tension
// on the skin exactly where it is thinnest (1.19 mm).  An adhesive-filled
// clearance loads the joint in shear over the full 85.7 mm span instead.
SPAR_BORE_OD      =  20.4;  // [mm] bonded-spar bore = 20 mm OD + 0.2 mm/side epoxy gap
// REV S1b (2026-08-16): station moved 22.0 → 45.15 mm = 35 % ROOT chord, by
// owner decision, to bring the nacelle tilt axis back toward its canonical
// station.  The 2026-07-19 reconciliation had slid the NACELLE forward to
// hull Y = +15 to reach a spar that sat too far forward; this moves the spar
// aft instead, so the pod sits where canon puts it.  It also closes the
// §1.1.2 spar-interface blocker — wing (22.0) and cargo shell (38.7) had
// disagreed — by putting BOTH on one station, and it lifts the wing-spar
// bearing boss clear of the Rev R6 landing-gear bay flange (LG-10.4: at
// ≥ 32.5 % root chord the boss/flange conflict disappears entirely;
// tools/landing_gear_wing_clearance.py --spar-station).
//
// Constant in MILLIMETRES, not chord fraction: the LE is straight
// (WING_SWEEP_LE = 0), so a constant-mm station is simultaneously parallel to
// the LE and perpendicular to the aircraft centreline, which is what the
// rotating spar requires.  A chord-fraction bore rakes and was already
// rejected once (the "swept" cutout).
//
// Cost, and why THICKNESS_SCALE_TIP moves with it: 45.15 mm is 35.0 % of root
// chord but 48.5 % of TIP chord, well aft of S1223's ~20 % max-thickness
// point.  Verify any change with tools/wing_spar_station_fit.py.
//
// REV T1 (2026-08-29, plan 003 KTD2): station moved 45.15 → 28.0 mm.  This
// RE-OPENS the Rev S1b decision above, and does so on the record rather than
// quietly: S1b moved the spar aft partly to stop dragging the nacelle forward
// off its canonical station.  THAT MOTIVE NO LONGER APPLIES — the nacelle now
// keeps its station because the pivot moves inside it (plan 003 KTD7/KTD8),
// so only the wing-INTERNAL station moves, and it moves back toward a line
// this wing was already built on before S1b.
//
// The station is forced by the airfoil.  A Ø20.4 bore needs 22.72 mm of
// section depth, and S1223 loses depth fast aft of its ~20 % max-thickness
// point, so holding 45.15 mm would need a 40 % t/c tip — not an airfoil.
// Station 28.0 was selected over the thinner 22.0 because the station also
// moves HOVER GROUND CLEARANCE (the bore rides the camber midline, which sits
// lower forward): 28.0 buys +7.2 mm of clearance for 1.8 points of tip t/c,
// at constant canonical nacelle offset when paired with the ESC1 relocation
// (plan 003 KTD2/KTD8 three-way trade table).
//
// Bore inventory at this station, ALL constant-mm and therefore parallel
// (checked by tools/wing_internal_clearance.py, which is fail-closed on
// bore-to-bore convergence — the fault class Rev S1c was written for):
//      8.0  Ø3.2   nav-light 3-core conduit         (web to spar  8.20 mm)
//     28.0  Ø20.4  THIS BORE                        spans 17.80 .. 38.20
//     44.5  Ø6.5   AK7455 SPI + power conduit       (web to spar  3.05 mm)
//     53.6  Ø4.4   nacelle tilt drive shaft         (web to SPI   3.65 mm)
//   No root-only bores remain: the tie-rod couple is retired on the default
//   path (see the WING ROOT LOAD PATH block).
SPAR_BORE_STATION =  28.00; // [mm] chordwise station aft of LE — CONSTANT over the
                            //      span (21.7 % root / 30.1 % tip chord).
                            //      Constant ⇒ bore ∥ leading edge ⊥ centreline.
                            // The bore-centre thickness height is taken from the
                            // ACTUAL S1223 camber midline at each station's own
                            // chord fraction (midline_frac(), below) — NOT a single
                            // constant — so it stays centred (root breakout fixed).

// ── Nav-light / auxiliary signal conduit (Rev T1 — replaces the double-D) ────
// THE 2 × Ø7 "DOUBLE-D" EDF POWER CONDUIT IS RETIRED (2026-08-29, plan 003 U2).
// Two independent reasons, either of which alone would end it:
//
//   1. It never actually carried the wiring it was named for.  Two 10 AWG
//      silicone conductors need ≥ 2 × 5.5 = 11.0 mm side by side; each bore
//      was Ø7.0, so one bore held ONE conductor and the pair capped out at two
//      of the four required.  This was sized without ever checking wire OD
//      against bore area (verified in plan 002 §A.1) — the conduit was a
//      40 A-labelled cavity that could not take the load it was labelled for.
//   2. Its 27.5 mm station is now INSIDE the Ø20.4 spar bore (17.80 .. 38.20).
//      Even had it fitted the wire, it could not stay where it was.
//
// The ESC feeds now run inside the spar, on the tilt axis (see SPAR_BORE_OD).
// What is left needing a wing conduit is the WS2812C nav-light 3-core, and it
// gets its own bore rather than sharing the spar's:
//
//   • The nav light is on the nacelle OUTBOARD face and rotates WITH the
//     nacelle [REF-FAA-003 §91.209(a)], so its 3-core must cross the tilt
//     joint.  It crosses at the trunnion, not through the spar.
//   • Under a FIXED spar the old plan-001 reasoning — "route the nav wire in
//     the spar bore" — is VOID.  That depended on the spar rotating WITH the
//     nacelle so the wire twisted with it.  The spar no longer rotates; the
//     light still does.  Putting the nav 3-core in the spar bore would now
//     bond it to the non-rotating side AND sit it in the middle of four 40 A
//     conductors, which is the exact co-location the whole routing decision
//     exists to avoid (plan 003 R7).
//
// FORWARD of the spar deliberately: this is where the section is near its
// max-thickness point at BOTH ends (10.5 mm = 8.1 % root / 11.3 % tip chord),
// so the walls are ~7–9 mm rather than the ~1.2 mm they would be aft, and it
// puts the spar's grounded CF wall physically between this conduit and the
// power bundle inside it.
//
// CONSTANT MILLIMETRES, matching the spar's own law: with a straight LE
// (WING_SWEEP_LE = 0) a constant-mm bore holds the same chordwise separation
// at every span station, so the web cannot be eroded by taper.  A chord-
// fraction conduit re-creates the convergence Rev S1c existed to remove.
NAV_BORE_D       =   3.2;  // [mm] conduit for the WS2812C 3-core (bundle Ø ≈ 2.5)
// STATION 8.0.  The nav conduit must EXIT the tip face into the nacelle (the
// light rotates with the nacelle), so it must clear the tip pad — the exact
// failure Rev S1c found when a Ø29.5 disc capped the EDF double-D, which is a
// blocked harness, not a cosmetic overlap.  The Rev T1 pad's forward edge is
// at X = 28 - TIP_PAD_R = 14.0; this conduit's aft edge is 9.6, clearing it by
// 4.40 mm.  Forward is also the only side with room: the whole region aft of
// the spar is taken by the AK7455 conduit, the tilt drive shaft, and the root
// tenon.
NAV_BORE_STATION =   8.0;  // [mm] chordwise station aft of LE — CONSTANT over span.
                           //      Walls (tools/wing_spar_station_fit.py, at the
                           //      Rev T1 thickness scales): root ±6.88, tip ±8.76.
                           //      Web to the spar bore's forward edge: 8.20 mm.
                           //      Gap to the tip pad's forward edge:   4.40 mm.

// ── Nacelle tilt drive shaft bore (Rev T1) ──────────────────────────────────
// Plan 004 KTD1/KTD4.  With the spar fixed, tilt torque can no longer travel
// down the spar, so a separate Ø4 mm steel shaft runs spanwise from the
// bulkhead servo to a spur pinion at the wingtip.  It is a SHAFT and not a
// belt because the tilt axis IS the spanwise axis: a belt's pulley axes are
// perpendicular to its run, so a spanwise belt would need a bevel or worm
// stage at the tip purely to turn the axis 90°, in the most congested region
// on the airframe.  A shaft lying parallel to the tilt axis needs no such
// stage — a plain spur pair transfers the motion directly (plan 004 trade
// study, Options A–D).
//
// STATION 53.6 — FIXED BY THE GEAR MESH, NOT A PACKAGING CHOICE.
//
// THE DRIVE IS A REDUCTION, NOT A STEP-UP (owner direction, 2026-08-29): the
// shaft turns MORE THAN ONE REVOLUTION to sweep the nacelle through 140°.  That
// inverts the whole stage.  An earlier pass here assumed a limited-rotation
// hobby servo (180°/270°), which forces a step-UP — the ring smaller than the
// pinion — and that is what produced an impossible geometry:
//
//   The tilt ring gear is CONCENTRIC WITH THE SPAR, so its ROOT diameter must
//   clear Ø20 plus a hub wall (≥ 26 mm).  Under a step-up at plan 004 KTD4's
//   C = 15 mm the algebra returns PD_ring = 10.5 mm — a ring gear SMALLER THAN
//   THE SPAR IT ENCIRCLES.  No tooth count fixes that.
//
// As a REDUCTION the ring is the LARGER member and the geometry closes easily.
// With i = N_ring/N_pinion, the shaft turns 140° × i:
//
//   module 0.8, 14T pinion (PD 11.2 — 14T is the no-undercut floor at 20° PA)
//     N_ring   PD    i      shaft rev   C      station   ring OD   root Ø
//        36   28.8  2.571     1.000   20.00     48.00      30.4     26.8
//        45   36.0  3.214     1.250   23.60     51.60      37.6     34.0
//     >> 50   40.0  3.571     1.389   25.60     53.60      41.6     38.0  <<
//        54   43.2  3.857     1.500   27.20     55.20      44.8     41.2
//
// **50T is selected.** 36T turns exactly one revolution, not "more than"; 54T
// pushes this bore to 55.2, leaving only 1.1 mm to the root tenon at 58.5 —
// under the 1.16 mm floor.  50T lands the shaft at 53.6 with 2.7 mm to the
// tenon and, more importantly, leaves the AK7455 pocket a 10.2 mm chordwise
// window between the spar bore's aft edge (38.2) and the shaft's forward edge
// (51.4).  Ring OD 41.6 fits the 53.4 mm trunnion envelope (plan 003 OQ2) and
// its 38.0 mm root diameter clears the spar with 9 mm of hub wall each side.
//
// CONSEQUENCE FOR THE ACTUATOR — this is a real change, not a detail.  A
// multi-turn output means the drive is NO LONGER a limited-rotation servo.  It
// is a continuous-rotation gearmotor or a stepper, closed on the AK7455's
// absolute nacelle angle rather than on the actuator's own travel.  That
// removes the 145°-of-travel constraint which plan 004 KTD5 found was the
// BINDING one (torque never was — the reduction now delivers 3.571 × whatever
// the actuator gives, against a 0.177 N·m grounded requirement), and it retires
// the 180°-vs-270° question entirely.  Shaft torque is 0.050 N·m; wind-up over
// the installed length is 0.27° (Ø4 steel, G 79 GPa).
SHAFT_BORE_D       =   4.4;  // [mm] Ø4 shaft + 0.2 mm/side running clearance
SHAFT_BORE_STATION =  53.6;  // [mm] chordwise station aft of LE — CONSTANT over span.
                             //      = spar station 28.0 + centre distance 25.6.
                             //      Walls: root ±6.1, tip ±3.5.
                             //      Web to the AK7455 conduit: 3.65 mm.
                             //      Gap to the root tenon (58.5): 2.70 mm.

// ── Pylon mount pocket (must match wing_nacelle_pylon_revo.scad) ────────────
// The wing_attach_block from the pylon inserts into this pocket at the tip face.
WING_SLOT_W     =  50.0;  // [mm] VERIFY — pocket width in X (chordwise) direction
WING_SLOT_H     =  40.0;  // [mm] VERIFY — pocket height in Y (thickness) direction
WING_SLOT_DEPTH =  14.0;  // [mm] pocket depth into wing from tip face (Z direction)
                           //      Must match pylon WING_SLOT_DEPTH = 14.0 mm
WING_BOLT_R     =  16.0;  // [mm] M3 bolt pitch circle radius (from pocket centre)
WING_BOLT_D     =   3.4;  // [mm] M3 clearance bore (nominal 3.0 mm + 0.4 clearance)
WING_BOLT_N     =   4;    // [count] bolt holes (45°/135°/225°/315°)
WING_SLOT_X_CTR =   0.50; // [chord fraction] pocket centre chordwise at tip — VERIFY

// ── Wing-tip FIXED-spar trunnion interface (Rev T1, 2026-08-29) ──────────────
// THE WINGTIP'S JOB CHANGES COMPLETELY AT THIS REVISION.
//
// Rev R2 wingtip: a BEARING SEAT.  The spar rotated inside the wing, so the
// wing had to journal it, and the nacelle was keyed to the spar's far end.
// Rev T1 wingtip: a CLAMP.  The spar is fixed, so the wing's job is to GRIP it
// and the bearing moves to the NACELLE side of the joint, inside the trunnion
// ring (plan 003 KTD3 / plan 004 U2).  A bearing here would now be actively
// wrong — it would let the spar spin under the drive-shaft's gear reaction,
// which is precisely what must not happen.
//
// This is also the structural termination of the wing's primary bending
// member, so the clamp is a load path, not a locating feature.  See the WING
// ROOT LOAD PATH block for the beam model both ends belong to.
//
// Fixed structural spar (20 × 16.3 mm roll-wrapped CF — plan 003 KTD4):
TILT_SPAR_OD          =  20.0;   // [mm] fixed CF spar outer diameter
TILT_SPAR_BORE_CLEAR  =  20.4;   // [mm] bonded clearance bore through wing (0.2 mm/side)

// ── HOW THE SPAR IS RETAINED — and why the clamp is at the ROOT, not here ────
// Plan 003 U3 specified a split-collar pinch clamp at the WINGTIP.  Two
// findings during implementation moved it to the root instead.  Recording both
// rather than silently relocating it:
//
// 1. IT DOES NOT FIT.  A collar that grips a Ø20 CF tube without crushing it
//    needs ~5 mm of wall, i.e. Ø30 outside.  The re-lofted TIP section is
//    22.83 mm deep at the spar station — its deepest point anywhere.  A Ø30
//    collar cannot exist inside it at any thickness scale that is still an
//    airfoil.  (Same class of finding as Rev R2d's F688ZZ → MF128ZZ downsize,
//    which was forced by exactly this section limit.)
//
// 2. IT WOULD HAVE NOTHING TO DO.  The spar is EPOXY-BONDED into the wing over
//    the full 85.7 mm span — bond area π × 20.4 × 85.7 = 5,492 mm².  At the
//    repo's 5 MPa figure that is ~27 kN of axial retention.  A clamp cannot add
//    to that, and a bonded spar cannot be withdrawn, so a clamp at this end
//    could not make the joint serviceable either.  A clamp is only meaningful
//    at a joint that is meant to come apart.
//
// So: WING + BONDED SPAR ARE ONE SERVICEABLE ASSEMBLY.  It separates from the
// aircraft at the FUSELAGE socket, by releasing the root clamp and withdrawing
// the spar outboard — which is how a light aircraft's spar-stub-into-socket
// wing attach works, and it satisfies plan 003 R10's intent at the joint that
// is actually designed to open.  The clamp hardware therefore belongs with the
// fuselage-side socket; this file publishes the requirement
// (ROOT_SOCKET_REACH_MIN, above) and the fuselage owns building it.
//
// SPAR PROTRUSION PAST THE TIP FACE — BOUNDED BY THE THRUST DUCT, NOT CHOSEN.
// Owner requirement (2026-08-29): **the spar must not penetrate the nacelle
// thrust tube.**  That is a hard geometric bound, and it is tighter than the
// bearing stack would like.
//
// The duct is a cylinder of r = 25 mm about the nacelle's local Z axis.  The
// spar runs along local X at Y = 0, so every point of it at station X sits
// sqrt(X² + Y²) ≥ |X| from the duct axis.  The spar therefore clears the duct
// **iff it TERMINATES at |X| ≥ 26** (25 + the 1 mm margin plan 003 R4 states).
//
//     wing tip face   |X| = 37.7 (NACELLE_OD_X/2) + 4.0 (joint gap) = 41.7
//     spar must stop  |X| = 26.0
//     => MAXIMUM STUB       15.7 mm
//
// The 32.0 mm previously specified here would have reached |X| = 9.7 — fifteen
// millimetres INSIDE the duct wall, straight through the thrust column between
// the two EDFs.  It was budgeted from the bearing stack outward and never
// checked against the duct, which is the same class of error as the Rev R2
// through-duct spar this whole revision exists to remove.
//
// 15.0 is used, keeping 0.7 mm in hand.  THE BEARING STACK MUST FIT INSIDE IT:
// 15 mm between |X| 41.7 and 26.7 carries a pair of thin-section bearings —
// 2 × 6804 (20 × 32 × 7) = 14.0 mm fits, and 6804 is already a BOM item
// (SKIPPER-BRG-6804).  A deeper stack does not fit and must not be assumed.
SPAR_TIP_PROTRUSION   =  15.0;   // [mm] spar stub proud of the wing tip face —
                                 //      DUCT-BOUNDED (max 15.7).  PUBLISHED
                                 //      JOINT REQUIREMENT; the nacelle must fit
                                 //      its trunnion bearing pair within it.

// ── Wingtip service access (Rev T1) ──────────────────────────────────────────
// Plan 003 U3 also specified a wingtip "maintenance garage" housing the
// high-current bullet disconnects.  MOVED TO THE NACELLE, with cause:
//
// The four 10 AWG feeds need ~6 mm of clear height for any disconnect
// (ring-terminal studs, bullets, or blade tabs).  Aft of the spar the TIP
// section falls away fast — measured depths at THICKNESS_SCALE_TIP = 2.20:
// station 40 → 17.50, 54 → 11.20, 66 → 6.78, 78 → 3.43 mm.  Subtracting
// 2 × WALL_T of skin leaves 12.5 mm at station 40 and 1.8 mm by station 66,
// over a chordwise run too short to lay four disconnects out in.  There is no
// wingtip volume for this.
//
// The nacelle HAS that volume: plan 003's own wire-routing diagram already
// lands the power bundle in "the annular space between the duct wall (r = 25)
// and the outer skin" before it reaches ESC1/ESC2.  That annulus is the right
// home for the disconnect, and putting it there also keeps the 40 A break out
// of the same pocket as the AK7455 plug — which is what
// docs/TILT_ENCODER_WIRING_EMI_SPEC.md §2.3 asks for and what a shared wingtip
// garage would have violated.  Published to the nacelle plan this revision.
//
// What the wingtip keeps is access, and it needs no hatch to get it: sliding
// the nacelle off the spar exposes the whole tip face — the AK7455 board and
// its plug, the drive-shaft pinion, and the nav-light crossing.  THE NACELLE IS
// THE COVER.  That is the nacelle-off-spar service model this repo already
// adopted in docs/plans/2026-08-26-001-nacelle-esc-intake-integration-plan.md,
// and it is why plan 001 rejected a wingtip hatch.  The only part of that
// rejection which does NOT survive Rev T1 is its reasoning about disturbing
// bearing seats — there is no longer a bearing here to disturb.

// SUPERSEDED Rev T1 — the MF128ZZ wingtip bearing and its seat.  Retained as
// named constants (NOT deleted) so the Rev R2d downsize record stays legible:
// F688ZZ (Ø16) was cut to MF128ZZ (Ø12) because the Ø16 seat radius exceeded
// the S1223 tip half-thickness and breached both skins.  Under Rev T1 the
// question is moot — there is no wingtip bearing at all — but a future revert
// to a rotating spar would need this history, not a rediscovery of it.
// NOT REFERENCED by any module below.
TIP_BRG_OD            =  12.0;   // [mm] SUPERSEDED — MF128ZZ outer diameter
TIP_BRG_SEAT_D        =  11.95;  // [mm] SUPERSEDED — press-fit seat bore
TIP_BRG_W             =   3.5;   // [mm] SUPERSEDED — bearing width
TIP_BRG_FLANGE_OD     =  13.5;   // [mm] SUPERSEDED — flange OD
TIP_BRG_FLANGE_T      =   1.0;   // [mm] SUPERSEDED — flange counterbore depth

// SUPERSEDED Rev R2b — fixed R22 sector-gear mount.  The tilt→nozzle gear
// train was archived when the nozzle drive became a pushrod/bellcrank; plan
// 004 KTD3 now re-datums the nozzle sync gear onto the FIXED TRUNNION on the
// nacelle side, so no gear mounts on the wing tip under Rev T1 either.
// NOT REFERENCED by any module below.
FIX_GEAR_BC_R         =  11.0;   // [mm] SUPERSEDED — M2.5 insert bolt circle
FIX_GEAR_N_BOLTS      =   3;     // [count] SUPERSEDED — 120° spacing
FIX_GEAR_INSERT_OD    =   3.7;   // [mm] SUPERSEDED — M2.5 heat-set insert bore
FIX_GEAR_INSERT_L     =   5.5;   // [mm] SUPERSEDED — insert pocket depth
FIX_GEAR_PLATE_H      =   3.0;   // [mm] SUPERSEDED — sector plate thickness

// ── Wingtip mount pad ────────────────────────────────────────────────────────
// Low boss around the spar at the tip face, proud by TIP_PAD_PROUD only, that
// carries the split collar and the AK7455 pocket and butts against the nacelle
// inboard face.
//
// REV T1: the pad grows from the Rev S1c teardrop to a plain disc, and the
// reason the teardrop existed has gone away.  S1c needed a teardrop because a
// Ø29.5 disc capped BOTH relocated Ø7 EDF conduits where they exited the tip
// face — a blocked harness, not a cosmetic overlap.  Those conduits no longer
// exist (see the nav-conduit block), so nothing forward of the spar has to be
// kept clear, and the pad can simply be concentric with the collar it carries.
// The nav conduit at station 10.5 is 17.5 mm forward of the spar axis, outside
// the pad radius.
TIP_PAD_R             =  14.0;   // [mm] pad radius at the spar — Ø20.4 bore +
                                 //      3.8 mm rim, enough to seat the nacelle
                                 //      trunnion register against a flat face.
                                 //      Forward edge X = 14.0, clearing the nav
                                 //      conduit's exit (aft edge 9.6) by 4.40.
TIP_PAD_SENS_R        =   7.5;   // [mm] pad radius at the AK7455 pocket centre.
                                 //      Covers the 10 × 8 board: half-diagonal
                                 //      sqrt(5² + 4²) = 6.40, + 1.1 rim.
TIP_PAD_SHAFT_R       =   5.0;   // [mm] pad radius at the drive-shaft exit.
                                 //      The shaft leaves the tip face at station
                                 //      53.6, where the section is ~11.4 mm deep
                                 //      and the skin alone is no bushing seat.
                                 //      This lobe gives it a supported boss.
                                 //      Pad aft reach = 53.6 + 5 = 58.6 mm.
TIP_PAD_PROUD         =   2.0;   // [mm] proud height beyond wing tip face (minimal)

// ── Wing/nacelle tilt-angle encoder — AKM AK7455 (Rev T1, 2026-08-29) ────────
// TRUE-NACELLE-TILT FEEDBACK.  A magnetic angle encoder at the wing/nacelle
// joint closes the tilt-servo loop on the ACTUAL nacelle angle (output side),
// so the loop is independent of drive-train compliance — shaft wind-up and
// spur backlash show up as hysteresis the encoder sees through, not as tilt
// error (plan 004 RISK-2).  This is the FIXED (sensor) half; the rotating
// diametric RING magnet is carried on the nacelle trunnion.
//
// OFF-AXIS read, and it STAYS off-axis under Rev T1 for a NEW reason.  Under
// Rev R2 the spar was a through-shaft into a keyed nacelle hub, so there was
// no free shaft end for an on-axis encoder.  Under Rev T1 the spar is fixed
// and its bore is FULL OF THE FOUR 10 AWG POWER CONDUCTORS, so there is still
// no free end — and now there is 40 A of switching current where an on-axis
// sensor would have to sit.  AS5600 and MT6701 remain rejected: both are
// on-axis-only parts (WBS §1.1.3.6, REF-SENSOR-008).  AK7455 (SPI,
// off-axis-capable) remains correct — plan 003 KTD6.
//
// WHAT CHANGED AT REV T1, AND WHY EACH FIGURE MOVED
//
// 1. THE SPAR IS NO LONGER FERROMAGNETIC.  Rev R2's whole magnetic-siting
//    problem was a 4130/17-4 PH steel shaft running through the ring centre
//    and distorting the bias field (docs/TILT_ENCODER_WIRING_EMI_SPEC.md §6.1;
//    docs/TILT_SPAR_ANALYSIS.md §3.5).  The Rev T1 spar is roll-wrapped CARBON
//    FIBRE (plan 003 KTD4), which is not ferromagnetic, so that distortion
//    source is REMOVED — not mitigated, removed.  The non-ferrous keep-out
//    below is RETAINED anyway, because it also governs the fasteners and the
//    nacelle-side collar, which are still free to be steel if nobody says
//    otherwise.  The in-situ zero-calibration stays required: it now absorbs
//    the drive-shaft and pinion (which ARE steel and ARE nearby), not the spar.
//    NOTE this INVALIDATES §6.1's stated premise; that spec needs the same
//    correction — flagged, not silently diverged from.
//
// 2. THE RING MAGNET HAS TO GROW.  It rides a non-ferrous collar on the spar,
//    and the spar went Ø8 → Ø20.  A ring of ID 10 physically cannot pass over
//    a Ø20 tube.  ID 22 / OD 34 clears the spar plus a 1 mm collar wall, and
//    fits inside the trunnion ring's measured 53.4 mm envelope (plan 003 OQ2).
//    Mean radius 14.0 → HALL_SENS_R moves 11.0 → 14.0 so the IC still reads
//    MID-ANNULUS.  Reading off the mean radius is not a nicety: a diametric
//    ring's field is only clean over the annulus, and an IC left at R = 11
//    would be reading 3 mm inboard of the magnet's inner edge, i.e. off it.
//
// 3. THE PCB SEAT WAS STILL SIZED FOR THE PART THAT WAS REJECTED.  HALL_PCB_W/H
//    were 7.0 × 7.0, dimensioned around the MT6701's 3 × 3 mm QFN — a part
//    rejected on 2026-07-19, over a year of revisions ago.  AK7455 is a QFN24
//    4 × 4 mm package; with its decoupling passives and a 7-way direct-solder
//    pigtail landing with strain relief, the real board is 12 × 10 mm.  This
//    closes the open item at airframe/wings-nacelles/WBS.md §1.1.3.6.
//
// 4. THE CONDUIT WAS SIZED FOR 4-WIRE I2C.  AK7455 is SPI: CS, CLK, MOSI, MISO
//    plus +3V3/GND plus ERROR = 7 conductors, and TILT_ENCODER_WIRING_EMI_SPEC
//    §2.1 specifies them as TWO separately-shielded cables — a 28 AWG shielded
//    quad and a 24 AWG shielded pair.  Ø3.5 carries neither pair of cables.
//    Ø6.5 carries both side by side with pull-through clearance.
//
//    DOCUMENTED DEVIATION: §2.3 asks for ≥ 15 mm between the signal group and
//    the power group.  Inside a single printed wing conduit that is not
//    achievable at any bore this section can hold, and splitting it into two
//    15-mm-separated conduits would need a second bore in the shallow aft
//    section where the Ø7 EDF conduits already could not hold wall.  Both
//    groups are 100 % braid-shielded per §2.1, which is the actual mitigation;
//    the 15 mm rule guards UNSHIELDED proximity.  Separation from the 40 A
//    feeds — the clearance that matters — is now far BETTER than Rev S1c's,
//    because those conductors are inside the spar's own grounded CF wall,
//    26 mm forward, instead of in an open conduit 9 mm away.
HALL_RING_OD    =  41.2;  // [mm] diametric ring-magnet OD (matches nacelle trunnion seat)
HALL_RING_ID    =  26.0;  // [mm] ring-magnet ID (clears Ø20 spar + 3.0 mm non-ferrous collar)
HALL_SENS_R     =  16.8;  // [mm] IC offset from spar axis = ring MEAN radius
                          //      (26 + 41.2) / 4 = 16.8 — the IC reads mid-annulus
HALL_AIR_GAP    =   1.5;  // [mm] axial magnet-face → IC-face gap (set by nacelle standoff)
HALL_PCB_W      =   9.0;  // [mm] sensor PCB seat width (chordwise, X) — AK7455 QFN24
                          //      4×4 + decoupling + 7-way pigtail landing.
                          //      Spans X 40.3..49.3: 2.10 mm clear of the spar
                          //      bore (aft edge 38.2) and 2.10 mm clear of the
                          //      drive-shaft bore (fwd edge 51.4).  Those two
                          //      gaps are what set HALL_SENS_R and the gear's
                          //      centre distance; none of the three is free.
                          //      The whole aft-of-spar window is 10.2 mm wide.
HALL_PCB_H      =   8.0;  // [mm] sensor PCB seat height (thickness, Y)
HALL_PCB_SEAT_T =   2.0;  // [mm] PCB + solder recess depth into the pad face
HALL_PCB_SCR_D  =   1.7;  // [mm] M2 self-tap pilot (2×, chordwise ±HALL_PCB_SCR_S)
HALL_PCB_SCR_S  =   3.0;  // [mm] screw pilot half-spacing (chordwise) — within W/2 span
HALL_KEEPOUT_R  =  10.0;  // [mm] NON-FERROUS keep-out radius around the IC
HALL_CABLE_D    =   6.5;  // [mm] AK7455 conduit: shielded 28 AWG SPI quad +
                          //      shielded 24 AWG power pair (EMI spec §2.1)
// REV S1c (2026-08-18): 0.33c → a CONSTANT 54.0 mm station, AFT of the spar.
// REV T1 (2026-08-29): 54.0 → 44.0.  Still aft of the spar, but now BETWEEN
// the spar and the tilt drive shaft rather than outboard of everything, and
// the move is forced rather than chosen: the drive shaft's gear-mesh centre
// distance puts IT at station 53.6 (see SHAFT_BORE_STATION), and two bores
// cannot share a station.  44.5 balances the surviving window — 3.05 mm of web
// to the spar bore and 3.65 mm to the shaft, both above the 2.5 mm WALL_T
// minimum, with walls root ±6.5 / tip ±4.5, comfortably above the 1.16 mm
// floor.  44.0 also passes but leaves only 0.05 mm of margin on the spar-side
// web, and there is no reason to spend it.
//
// The EMI reason for staying aft is UNCHANGED IN INTENT but has a different
// mechanism now.  Under Rev S1c the barrier between this shielded low-level
// pair and the 40 A feeds was the ferromagnetic steel spar sitting between
// them.  Under Rev T1 the feeds are INSIDE the spar, so the barrier is the
// spar's own grounded CF wall wrapped all the way around them — a closed
// shield rather than an interposed obstacle, and a strictly stronger one.
HALL_CABLE_STATION = 44.5; // [mm] chordwise station aft of LE — CONSTANT over the
                          //      span, like SPAR_BORE_STATION and SHAFT_BORE_STATION

// Spar-axis thickness (internal Y) height at the TIP station — the spar exits on
// the camber midline, NOT the chord line, so all wingtip spar features (pad,
// bearing seat, gear inserts) must share this Y to stay concentric with the
// spar_bore().  Defined as a FUNCTION (not a top-level variable) so it is
// evaluated at module-instantiation time, after the S1223_UPPER/LOWER point
// lists exist — same expression spar_bore() uses for its tip disc.
// REV S1b: no THICKNESS_SCALE_TIP factor.  s1223_section() now scales the
// thickness envelope about the camber line and leaves the camber unscaled, so
// multiplying the midline by the thickness scale would put the bore ABOVE the
// section it is supposed to be centred in.
function spar_tip_y() = midline_frac(SPAR_BORE_STATION / WING_CHORD_TIP)
                        * WING_CHORD_TIP;

// ── WING ROOT LOAD PATH (Rev T1, 2026-08-29) ────────────────────────────────
// THIS IS THE STRUCTURAL CONSEQUENCE OF THE SPAR BECOMING A WING MEMBER.
//
// Under Rev R2 the spar was a ROTATING drive shaft riding bearings at both
// ends.  A bearing transmits shear, not moment, so the spar was structurally
// incapable of reacting the wing-root moment — and every root-joint design in
// this file's history existed to work AROUND that:
//
//   CARGO-03c   enlarged tenon alone reacts the couple      FOS 0.49  FAILED
//   U5 / KTD1   two bonded CF tie rods react it as a couple FOS 4.14  passed
//
// Rev T1 removes the constraint at its source.  The spar is FIXED and bonded
// over its full span, so it carries moment, and the load path is simply:
//
//     nacelle → wingtip trunnion → SPAR → fuselage socket
//
// The wing skin carries only its own local air load into the spar.  The tenon
// and the tie rods are no longer in the path at all.  This is not a stronger
// version of the old joint — it is a different joint, and it is why the couple
// arm improves from 48 mm (chordwise rod spacing) to the full 86.7 mm span.
//
// LOADS (tools/wing_spar_carrythrough.py, measured from the baked STLs):
//   ultimate root moment      14.60 N.m   (4 g gust+maneuver × 1.5)
//   ultimate root shear      115.1  N
//   spar bending, cantilever bound   33.28 MPa → FOS 9.0 vs the 300 MPa
//                                     cross-ply stand-in (UNVERIFIED — DEP-1)
//   spar bending, two-support bound  10.04 MPa → FOS 29.9
//   The CANTILEVER bound is the quoted one: it does not depend on the printed
//   skin sharing load, which is not characterised.
//
// WHY THE TIE RODS RETIRE RATHER THAN STAYING AS BACKUP:
//   1. The forward rod is geometrically impossible.  It sat at station 14.0 at
//      Ø8.2 (9.9..18.1); the Ø20.4 spar bore spans 17.80..38.20.  They
//      overlap.  There is no clearance version of the old joint.
//   2. The aft rod fits but has no remaining job.  Its only candidate duty
//      would be wing TORSION about the spar axis, and that is 0.41 N.m at
//      ultimate — bond shear 0.016 MPa, FOS 306.  Thrust adds none: the duct
//      axis passes through the pivot, which is on the spar axis.
//   3. An unnecessary bonded rod is not free — it is a second bonded interface
//      competing for root volume with the spar socket and a stress riser in
//      the skin at the station where the section is thinnest.
//
// REQUIREMENT PUBLISHED TO THE FUSELAGE — REVISED 2026-08-29 (owner direction:
// **the centre of the cargo bay must remain clear**).
//
// An earlier pass here asked the fuselage for a 55 mm-deep bonded socket.  That
// is now ruled out: the bay's clear span begins at hull X −100 and the wall
// skin is at −81.33, so only **18.67 mm** of socket depth exists before the
// spar enters the bay.  A 55 mm socket would have reached X −136.
//
// 18.67 mm is not enough for the moment, and not close:
//     F = 3M/(2L) + V/2 = 1,231 N over D·L/3 = 124 mm²  →  9.89 MPa, FOS 0.51
// The stress goes as 1/L², so depth is the only lever a socket has, and the
// bay has taken it away.  **The socket therefore stops being the moment path.**
//
// THE JOINT SPLITS IN TWO, each part carrying what it is actually good at:
//
//   1. SHEAR — the Ø20.4 socket, 18.5 mm deep, entirely inside the sidewall.
//      σ = 115.1 / (20 × 18.5) = 0.31 MPa → **FOS 16**.  Shear was never the
//      problem; it does not need depth.
//
//   2. MOMENT — a bonded ROOT FLANGE on the INNER FACE of the sidewall.  The
//      moment is reacted over wall AREA instead of socket DEPTH, so it needs
//      no inboard reach at all: the flange lies flat against the wall and
//      protrudes only its own thickness (~5 mm, to X ≈ −86).  Triangular
//      pressure over the flange height h, arm 2h/3:
//          h  60 × w 50 →  365 N over 1,000 mm²  → 0.37 MPa, FOS 13.7
//          h  80 × w 60 →  274 N over 1,600 mm²  → 0.17 MPa, **FOS 29.2**
//      **80 × 60 mm is specified.**  The cargo section is ~150 mm tall inside
//      at this station, so 80 mm of height is available without crowding.
//
// This is strictly better than the 55 mm socket it replaces — FOS 29 instead
// of 4.0 — because a flange trades an unfavourable 1/L² depth term for a linear
// area term.  The bay is untouched: nothing goes inboard of X ≈ −86, against a
// bay edge at −100.
//
// The tube-to-flange transfer is the wing's own 85.7 mm bond, not a fitting:
// the spar is bonded through the wing root, and the flange is clamped to the
// spar at the wall by the same split collar that makes the joint releasable.
//
// TENON_LOAD_PATH selects which joint reacts the wing-root couple:
//   "spar_carrythrough" (DEFAULT, Rev T1) — the fixed bonded spar reacts the
//                     couple into a fuselage socket; the tenon is a locating
//                     feature and no tie rods are cut.
//   "two_rod"       (SUPERSEDED, Rev S1d) — two bonded CF tie rods react the
//                     couple.  Retained and still renderable, but note the
//                     forward rod now INTERSECTS the Ø20.4 spar bore, so this
//                     path is geometrically invalid at the Rev T1 spar and is
//                     kept only as the design record.
//   "enlarged_tenon" (SUPERSEDED, CARGO-03c) — the tenon alone reacts the
//                     couple at the measured maximum envelope.  Requires a
//                     CF-PETG fusion/bearing coupon clearing >= 15 MPa
//                     (root TODO.md §1.1.4 LG-11) — not available.
TENON_LOAD_PATH = "spar_carrythrough";  // ["spar_carrythrough" | "two_rod" | "enlarged_tenon"]

// Fuselage-side figures this wing requires (published interface — the wing does
// not build them; see the REQUIREMENT block above).
ROOT_SOCKET_REACH     = 18.5;  // [mm] spanwise, inboard of the wall.  BOUNDED by
                               //      the cargo bay (clear span starts at hull
                               //      X −100; wall skin −81.33), not chosen.
                               //      Carries SHEAR only, at FOS 16.
ROOT_FLANGE_H         = 80.0;  // [mm] bonded root-flange height (hull Z extent)
ROOT_FLANGE_W         = 60.0;  // [mm] bonded root-flange width  (hull Y extent)
                               //      Together these carry the MOMENT at FOS 29.2
                               //      against the 5 MPa bond-limited figure.

// ── Wing root fuselage tab (locating/index feature under "spar_carrythrough"
//    and "two_rod"; full structural tenon under "enlarged_tenon") ────────────
// The root face (Z=0) must interface with the fuselage wing slot.
// VERIFY slot dimensions in fuselage hull STL before printing.
//
// "spar_carrythrough" (DEFAULT, Rev T1): the tab's job is UNCHANGED from the
// "two_rod" case below and for the same reason — something else reacts the
// couple, so the tab locates and does not carry moment.  Only the "something
// else" changed, from two bonded rods to the spar itself.  The sizing is
// therefore identical and is shared rather than duplicated.
//
// "two_rod" (superseded): the two CF rods below react the entire wing-root
// couple, so the tab reverts to ITS OWN documented job — radial restraint
// and rotational location, not moment reaction.  Only W and L shrink: those
// are the two dimensions that actually appear in the bearing-stress formula
// (sigma = F / (W . L/2), tools/wing_spar_carrythrough.py report_root_joint())
// — H never did, it only sets the tab's vertical reach.  W/L are sized like
// this repo's other non-structural locating dowels/bosses
// (docs/structural_analysis.md §7.1 boss-pin convention: 8 mm depth is the
// established "positive stop / 3-point kinematic location" figure for a
// joint that "carries no structural flight load").
//
// H is DELIBERATELY left at its enlarged-tenon value, not shrunk: the S1223
// section at this chordwise band is centred well ABOVE the chord line (the
// tab is centred ON the chord line, Y=0, per CARGO-03b's fixed datum) — real
// wing material at x=64.5 spans only Y +6.6..+15.7 mm
// (tools/wing_spar_station_fit.py), so a tab shorter than ~H=13 mm never
// reaches material at all and unions as a disconnected floating solid (found
// by trimesh body-count during verification: bodies=2, not 1).  H=20 keeps
// the ~3.4 mm structural-era overlap into that material band that already
// made this connect cleanly; shrinking it would break the union, not the
// bearing stress (H was already not part of that calculation).
WING_ROOT_TAB_W_LOCATING =  12.0;  // [mm] locating-tab width in X
WING_ROOT_TAB_H_LOCATING =  20.0;  // [mm] locating-tab height in Y — see note above
WING_ROOT_TAB_L_LOCATING =   8.0;  // [mm] insertion depth (§7.1 boss-pin depth)

// "enlarged_tenon" (documented, gated off): the AS-BUILT structural sizing
// from CARGO-03c's first pass — 30 x 20 x 12 mm, FOS 0.49 against the 5 MPa
// bond-limited figure at that size.  Retained verbatim (not the 39.2 x 20.1
// mm envelope maximum, which needs the >=15 MPa fusion-strength coupon
// before it can be built) so the alternate branch still renders a real,
// previously-verified solid if selected.
WING_ROOT_TAB_W_ENLARGED = 30.0;  // [mm] VERIFY — fuselage slot width in X
WING_ROOT_TAB_H_ENLARGED = 20.0;  // [mm] VERIFY — fuselage slot height in Y
WING_ROOT_TAB_L_ENLARGED = 12.0;  // [mm] VERIFY — insertion depth into slot

// The tab is a LOCATING feature on every path except "enlarged_tenon", which
// is the only one where the tenon itself is the moment path.  Written as
// "not enlarged_tenon" rather than an explicit list so a future fourth path
// inherits the safe (locating) sizing by default instead of silently picking
// up the structural tenon.
TAB_IS_LOCATING = (TENON_LOAD_PATH != "enlarged_tenon");
WING_ROOT_TAB_W = TAB_IS_LOCATING ?
                   WING_ROOT_TAB_W_LOCATING : WING_ROOT_TAB_W_ENLARGED;
WING_ROOT_TAB_H = TAB_IS_LOCATING ?
                   WING_ROOT_TAB_H_LOCATING : WING_ROOT_TAB_H_ENLARGED;
WING_ROOT_TAB_L = TAB_IS_LOCATING ?
                   WING_ROOT_TAB_L_LOCATING : WING_ROOT_TAB_L_ENLARGED;

// ── Wing root tie-rod couple (U5, "two_rod" path) ─────────────────────────────
// Two bonded CF rods react the ultimate root moment (14.60 N.m,
// airframe/fuselage-mid/WBS.md §1.1.1.2 CARGO-03c) as a couple.  Each rod is a
// simple bonded pin (shear only, no moment restraint credited — the
// conservative idealisation, since the bond's rotational stiffness is not
// characterised) — see the couple-force derivation in that WBS.md section and
// tools/wing_spar_carrythrough.py report_root_joint().  Clearance bore = rod
// OD + 0.1 mm/side, matching the CF-ROD bonding convention already
// established for CF-ROD-4MM (docs/structural_analysis.md §6/§7: same
// pultruded-CF-rod-stock citation, West System 105/206 epoxy, cure 24 h
// before foam pour).
//
// Both rods are ROOT-ONLY embeds, not full-span like the main spar: the main
// spar must run full-span because it is ALSO the rotating tilt axis reaching
// the wingtip bearing — these tie rods only react the ROOT joint, so running
// them to the tip would add mass and risk fouling the tip bearing/gear/Hall
// pocket for no structural benefit.  Same reasoning applied to both rods for
// consistency.
//
// FWD rod: Ø8.2 mm (8 mm CF rod + 0.1 mm/side), station 14 mm from LE
// (largest separation from the main spar on a healthy bore wall — measured
// 2.92 mm at Ø8.2, tools/wing_spar_station_fit.py).  40 mm wing-side embed.
ROD_FWD_D       =  8.2;   // [mm] fwd tie-rod clearance bore
ROD_FWD_STATION = 14.0;   // [mm] chordwise station aft of LE
ROD_FWD_EMBED   = 40.0;   // [mm] wing-side embed depth (root face inward)

// AFT rod: Ø6.2 mm (6 mm CF rod + 0.1 mm/side).  A matching Ø8.2 mm aft rod
// does not fit at ANY aft station (main spar bore aft edge 49.30 mm and the
// Hall conduit's fixed 52.25..55.75 mm span leave no room); Ø6.2 mm fits aft
// of the Hall conduit.  Station 62.0 mm from LE is the pick WITHIN the
// feasible 60..62 mm band: it maximises clearance margin to the Hall
// conduit's trailing edge (3.15 mm vs 1.15 mm at 60 mm) while the spar-bore
// margin stays ample throughout that band (7.6..9.6 mm) and root wall stays
// well above the repo's 1.16 mm floor (measured 1.72 mm at 62 mm,
// tools/wing_spar_station_fit.py --station 62 --bore 6.2).  40 mm embed
// alone gives FOS 3.945 against the 5 MPa allowable (just under the §3 FOS
// 4.0 target — see the couple-force derivation) so the embed is bumped to
// 42 mm, which clears at FOS 4.14.
ROD_AFT_D       =  6.2;   // [mm] aft tie-rod clearance bore
ROD_AFT_STATION = 62.0;   // [mm] chordwise station aft of LE
ROD_AFT_EMBED   = 42.0;   // [mm] wing-side embed depth (root face inward)

// ── Print chirality ───────────────────────────────────────────────────────────
// RENDER_SIDE = +1 → port (left) wing; RENDER_SIDE = -1 → starboard (right).
// The SCAD mirrors geometry for starboard.
RENDER_SIDE     =   0;    // [0 = both wings; +1 = port only; -1 = stbd only]

// ── Wall / structural ─────────────────────────────────────────────────────────
WALL_T          =   2.5;  // [mm] minimum solid shell wall (4 perimeters at 0.6mm)

// ── Global facet resolution ───────────────────────────────────────────────────
$fn = 72;


// =============================================================================
// ── S1223 Airfoil Coordinate Data ─────────────────────────────────────────────
// =============================================================================
// Coordinates fetched live from the UIUC Airfoil Coordinates Database,
// `s1223.dat` (Selig), 2026-08-24 — REFERENCES.md REF-CAD-006.  This is a
// VERBATIM re-split of the published 81-point Selig-format loop (one closed
// list, upper TE->LE then lower LE->TE) into the two ordered lists this
// file's s1223_section()/midline_frac() decomposition expects (upper LE->TE,
// lower TE->LE).  No coordinate value, interpolation, or invented point was
// introduced — every (x, y) pair below appears verbatim in the fetched file.
// x in [0,1], y = local thickness ratio (positive = upper surface toward sky).
//
// This table REPLACES the Rev R1 placeholder table, which was never traced to
// an actual fetch and crossed to negative thickness at x/c ~= 0.742
// (WING-01, tools/wing_airfoil_integrity.py) -- a fabricated/reconstructed
// table, prohibited by root AGENTS.md SS4.
//
// Format: closed polygon, upper surface LE->TE then lower surface TE->LE.
// OpenSCAD polygon() uses counterclockwise winding (positive fill).
// The two surfaces do not share an exact (0,0) leading-edge point -- neither
// does the source data, which is normal for a discretely sampled finite-
// radius leading edge (upper's LE-most point is [0.00005, 0.00178]; lower's
// is [0.00044, -0.00561]).  tools/wing_airfoil_integrity.py excludes a
// LE_EXCLUDE = 0.005 band from the thickness check for exactly this reason.
// =============================================================================

// ── Upper surface points (LE x=0 -> TE x=1) ──────────────────────────────────
// REF-CAD-006, s1223.dat rows 46 down to 1 (reversed to LE->TE order).
S1223_UPPER = [
    [ 0.00005,  0.00178 ],   // leading-edge-most upper sample (source data; see note above)
    [ 0.00155,  0.01033 ],
    [ 0.00495,  0.01969 ],
    [ 0.01028,  0.02954 ],
    [ 0.01755,  0.03961 ],
    [ 0.02694,  0.04966 ],
    [ 0.03855,  0.05968 ],
    [ 0.05223,  0.06965 ],
    [ 0.06789,  0.07940 ],
    [ 0.08545,  0.08879 ],
    [ 0.10482,  0.09770 ],
    [ 0.12591,  0.10598 ],
    [ 0.14863,  0.11355 ],
    [ 0.17286,  0.12026 ],
    [ 0.19846,  0.12594 ],
    [ 0.22541,  0.13037 ],
    [ 0.25370,  0.13346 ],
    [ 0.28347,  0.13505 ],
    [ 0.31488,  0.13526 ],   // <- max thickness station (source data)
    [ 0.34777,  0.13447 ],
    [ 0.38193,  0.13271 ],
    [ 0.41721,  0.13011 ],
    [ 0.45340,  0.12683 ],
    [ 0.49025,  0.12303 ],
    [ 0.52744,  0.11881 ],
    [ 0.56465,  0.11425 ],
    [ 0.60158,  0.10935 ],
    [ 0.63798,  0.10412 ],
    [ 0.67360,  0.09859 ],
    [ 0.70823,  0.09277 ],
    [ 0.74166,  0.08671 ],
    [ 0.77369,  0.08044 ],
    [ 0.80412,  0.07402 ],
    [ 0.83277,  0.06749 ],
    [ 0.85947,  0.06089 ],
    [ 0.88406,  0.05427 ],
    [ 0.90641,  0.04768 ],
    [ 0.92639,  0.04116 ],
    [ 0.94389,  0.03476 ],
    [ 0.95884,  0.02853 ],
    [ 0.97111,  0.02250 ],
    [ 0.98075,  0.01646 ],
    [ 0.98825,  0.01037 ],
    [ 0.99417,  0.00494 ],
    [ 0.99838,  0.00126 ],
    [ 1.00000,  0.00000 ],   // trailing edge
];

// ── Lower surface points (TE x=1 -> LE x=0) ──────────────────────────────────
// REF-CAD-006, s1223.dat rows 81 down to 47 (reversed to TE->LE order).
S1223_LOWER = [
    [ 1.00000,  0.00000 ],   // trailing edge
    [ 0.99825,  0.00115 ],
    [ 0.99268,  0.00468 ],
    [ 0.98255,  0.01060 ],
    [ 0.96693,  0.01822 ],
    [ 0.94573,  0.02624 ],
    [ 0.91966,  0.03387 ],
    [ 0.88928,  0.04088 ],
    [ 0.85500,  0.04706 ],
    [ 0.81729,  0.05219 ],
    [ 0.77660,  0.05612 ],
    [ 0.73344,  0.05872 ],
    [ 0.68832,  0.05994 ],
    [ 0.64176,  0.05976 ],
    [ 0.59428,  0.05820 ],
    [ 0.54639,  0.05534 ],
    [ 0.49860,  0.05129 ],
    [ 0.45139,  0.04618 ],
    [ 0.40519,  0.04021 ],
    [ 0.36044,  0.03358 ],
    [ 0.31750,  0.02652 ],
    [ 0.27673,  0.01928 ],
    [ 0.23840,  0.01213 ],
    [ 0.20278,  0.00535 ],
    [ 0.17006, -0.00075 ],
    [ 0.14020, -0.00563 ],
    [ 0.11282, -0.00925 ],
    [ 0.08787, -0.01202 ],
    [ 0.06561, -0.01404 ],
    [ 0.04627, -0.01532 ],
    [ 0.03006, -0.01584 ],
    [ 0.01718, -0.01550 ],
    [ 0.00789, -0.01427 ],
    [ 0.00264, -0.01120 ],
    [ 0.00044, -0.00561 ],   // leading-edge-most lower sample (source data; see note above)
];

// ── Combined polygon (counterclockwise: upper LE→TE, lower TE→LE) ─────────────
// Concatenates upper and lower surface lists.  OpenSCAD 2021+ supports concat();
// for compatibility the full merged list is written explicitly below.
S1223_POLY = concat(S1223_UPPER, S1223_LOWER);


// =============================================================================
// ── Surface / camber-midline interpolation helpers (Rev R1a) ─────────────────
// =============================================================================
// surf_y(pts, xq): linear-interpolate the surface y (t/c) at chord fraction xq
//   from a surface point list (handles both ascending S1223_UPPER and
//   descending S1223_LOWER x-ordering by testing each segment either way).
// midline_frac(xq): camber-midline height (t/c) at chord fraction xq =
//   mean of upper and lower surface y.  Used to keep bores centred in the
//   (strongly cambered) section at each span station rather than on the
//   chord line — the S1223 lower surface sits ABOVE the chord line aft of
//   ~8% chord, so a chord-line-centred bore would break out the lower skin,
//   and a midline estimated at the wrong chord fraction rides into the upper
//   skin at the root (fixed here by evaluating at each station's own fraction).
function surf_y(pts, xq) =
    let (seg = [ for (k = [0 : len(pts) - 2])
                 let (a = pts[k], b = pts[k + 1])
                 if ((xq >= a[0] && xq <= b[0]) || (xq <= a[0] && xq >= b[0]))
                     [a, b] ])
    len(seg) == 0 ? 0
        : let (a = seg[0][0], b = seg[0][1])
          a[1] + (xq - a[0]) / (b[0] - a[0]) * (b[1] - a[1]);

function midline_frac(xq) =
    (surf_y(S1223_UPPER, xq) + surf_y(S1223_LOWER, xq)) / 2;


// =============================================================================
// ── Module: s1223_section ─────────────────────────────────────────────────────
// =============================================================================
// 2D airfoil cross-section polygon at a given chord length.
// The section is centred with LE at [0,0] and TE at [chord,0].
// THICKNESS_SCALE is applied vertically only, preserving the camber line.
//
// Parameters:
//   chord          [mm] chord length for this span station
//   t_scale        [1.0] vertical scale factor for thickness (see THICKNESS_SCALE)
// REV S1b (2026-08-16): this now scales THICKNESS ONLY, about the camber line.
//
// It previously did `scale([chord, chord * t_scale])`, which multiplies camber
// and thickness by the same factor, and conceded as much: "scaling y uniformly
// scales both camber and thickness ... a minor approximation acceptable for
// t_scale in [0.85,1.0]".  THICKNESS_SCALE_TIP left that range long ago (1.25),
// and the Rev S1b spar move needs 1.447 — where the approximation is not minor.
// Uniform scaling at 1.447 drives S1223's camber from 8.12 % to 11.75 %, i.e. a
// factor picked purely to fit a spar would silently re-camber the aerofoil, and
// S1223 is a high-lift section that earns its Cl from exactly that camber.
//
// Decomposing into camber + thickness and scaling only the thickness gives the
// IDENTICAL section depth at the spar station (so the same +1.16 mm of skin
// over the bore) while leaving the camber line exactly where Selig put it.
// The two are compared in tools/wing_airfoil_variants.py.
//
// The parameter block above already claimed "Camber line is NOT affected — only
// thickness offset"; this makes the code true to that.
function s1223_half_thk(p) = p[1] - midline_frac(p[0]);

function s1223_scaled_pts(t_scale) = [
    for (p = S1223_UPPER)
        [p[0], midline_frac(p[0]) + s1223_half_thk(p) * t_scale],
    for (p = S1223_LOWER)
        [p[0], midline_frac(p[0]) + s1223_half_thk(p) * t_scale]
];

module s1223_section(chord = 65.0, t_scale = THICKNESS_SCALE) {
    // x → x × chord (chordwise, unmodified); y → y × chord with the thickness
    // envelope opened by t_scale about the unscaled camber line.
    scale([chord, chord])
        polygon(s1223_scaled_pts(t_scale));
}


// =============================================================================
// ── Module: wing_solid ────────────────────────────────────────────────────────
// =============================================================================
// REV S1d (2026-08-24, KTD4): true vertex-matched loft, NOT hull().
//
// Why hull() was replaced: hull() takes the CONVEX HULL of the root and tip
// cross-section point clouds.  With the corrected UIUC S1223 table
// (REF-CAD-006, see S1223_UPPER/S1223_LOWER above) the real section has a
// genuinely reflexed/concave lower surface aft of ~65% chord -- that is real
// S1223 geometry, not a table defect.  `tools/wing_airfoil_integrity.py`
// reports the convex hull of the tabulated outline is 1.612x the true
// outline's area, over its 1.10x tolerance -- so a hull()-lofted solid would
// be measurably not the S1223 section the aero/mass analysis assumes (the
// reflex is filled in solid, changing wetted area, internal clearance, and
// mass).
//
// Replacement: a manual polyhedron() built from the two end-station point
// lists returned by s1223_scaled_pts() (the same list `s1223_section()`
// polygon()s).  s1223_scaled_pts() always returns the SAME point count in
// the SAME order (46 upper + 35 lower = 81 pts, upper LE->TE then lower
// TE->LE) regardless of chord or t_scale -- only the scaled coordinate
// values differ between root and tip -- so root and tip are vertex-matched
// by construction and a straight quad-strip side wall between them is a
// faithful ruled loft of the TRUE (non-convex) outline, not its hull.
// Span-wise the loft is still linear between just the two stations (root,
// tip), same as the old hull() version -- only the per-station CHORDWISE
// cross-section fidelity changes, from convex-hull-approximated to exact.
//
// Coordinate system: X=chordwise (LE=0), Y=thickness, Z=spanwise (root=0, tip=SPAN).
// The LE sweeps in +X by WING_SWEEP_LE over the span (aft sweep).
// The tip rises by WING_DIHEDRAL in +Y (positive dihedral).
module wing_solid() {
    root_chord = WING_CHORD_ROOT;
    tip_chord  = WING_CHORD_TIP;
    span       = WING_SEMI_SPAN;
    sweep      = WING_SWEEP_LE;    // LE moves aft (+X) by this amount over span
    dihedral   = WING_DIHEDRAL;    // tip rises (+Y) by this amount over span

    // Normalized (chord-fraction) section point lists -- SAME topology
    // (point count + winding order) at root and tip; only t_scale differs
    // (THICKNESS_SCALE at root, THICKNESS_SCALE_TIP at tip, per the Rev S1b
    // camber-preserving decomposition above).
    root_pts2d = s1223_scaled_pts(THICKNESS_SCALE);
    tip_pts2d  = s1223_scaled_pts(THICKNESS_SCALE_TIP);
    n = len(root_pts2d);   // == len(tip_pts2d) by construction; asserted below

    assert(n == len(tip_pts2d),
        "wing_solid(): root/tip section point counts diverged -- vertex-matched loft requires identical topology");

    // Scale each normalized point to its station's chord and place it in 3D.
    root_pts3d = [ for (p = root_pts2d) [ p[0] * root_chord, p[1] * root_chord, 0 ] ];
    tip_pts3d  = [ for (p = tip_pts2d)
                     [ p[0] * tip_chord + sweep, p[1] * tip_chord + dihedral, span ] ];

    pts = concat(root_pts3d, tip_pts3d);

    // Root cap (Z=0): reversed winding so its outward normal points -Z (away
    // from the solid, toward the fuselage).  Tip cap (Z=span): original CCW
    // winding so its outward normal points +Z (toward the wingtip).  This is
    // the standard prism-cap convention for a manually-built polyhedron().
    root_cap = [ for (i = [n - 1 : -1 : 0]) i ];
    tip_cap  = [ for (i = [0 : n - 1]) n + i ];

    // Side wall: two triangles per matched root/tip vertex pair, wound
    // outward.  Explicit triangulation (not a quad) because the root and
    // tip outlines differ (taper + the S1223 reflex), so the quad
    // [i, i2, n+i2, n+i] is not guaranteed planar -- OpenSCAD's own
    // nonplanar-quad fallback triangulator was found to produce a
    // non-watertight mesh (Volumes: 3, trimesh is_watertight: False) on
    // this section, so the diagonal split is done here explicitly instead.
    side_faces = [ for (i = [0 : n - 1])
        let (i2 = (i + 1) % n)
        each [
            [ i, i2, n + i ],
            [ i2, n + i2, n + i ],
        ]
    ];

    polyhedron(points = pts, faces = concat([root_cap], [tip_cap], side_faces), convexity = 6);
}


// =============================================================================
// ── Module: spar_bore ────────────────────────────────────────────────────────
// =============================================================================
// Cylindrical bore along Z for the 12 mm OD CF wing spar (CF-TUBE-12MM).
// The bore position tracks with the chord taper — centred at SPAR_BORE_X of
// the local chord and at the chord line (Y = SPAR_BORE_Y_CTR).
//
// Implementation (Rev R1a): the bore is a STRAIGHT cylinder at a constant
// chordwise station (SPAR_BORE_STATION, parallel to the straight LE — no plan-
// view skew).  Its centre tracks the camber midline in the thickness (internal
// Y) direction so it stays enclosed by the skin as the section tapers; because
// the tip is locally thickened (THICKNESS_SCALE_TIP) the midline height differs
// root-to-tip, so the two end discs sit at slightly different internal Y — this
// is a straight tube tilted a few degrees within the thickness plane only, which
// does NOT reintroduce plan-view (spanwise) sweep.
module spar_bore() {
    // Camber-midline bore-centre height (internal Y) at each end station.
    // The spar station is a FIXED chord distance, so it is a DIFFERENT chord
    // fraction at root (22/129 = 17.1%) vs tip (22/93 = 23.7%); the midline
    // height is evaluated at each station's own fraction so the bore stays
    // centred in both sections (root-camber breakout of the single-constant
    // version fixed).  y = midline(t/c) × local chord.
    // REV S1b: the local thickness-scale factor is GONE from these — camber is
    // no longer scaled by s1223_section(), so re-applying the thickness scale
    // here would lift the bore off the camber line it is centred on.
    root_y_ctr = midline_frac(SPAR_BORE_STATION / WING_CHORD_ROOT)
                 * WING_CHORD_ROOT;
    tip_y_ctr  = midline_frac(SPAR_BORE_STATION / WING_CHORD_TIP)
                 * WING_CHORD_TIP;

    hull() {
        translate([SPAR_BORE_STATION, root_y_ctr, -1.0])       // root disc (1 mm below root face)
            cylinder(r = SPAR_BORE_OD / 2, h = 0.01);

        translate([SPAR_BORE_STATION, tip_y_ctr + WING_DIHEDRAL, WING_SEMI_SPAN + 1.0])
            cylinder(r = SPAR_BORE_OD / 2, h = 0.01);          // tip disc (1 mm past tip)
    }
}


// =============================================================================
// ── Module: nav_bore — nav-light / auxiliary signal conduit ──────────────────
// =============================================================================
// Single spanwise conduit FORWARD of the spar, carrying the WS2812C nav-light
// 3-core from the fuselage to the wing tip, where it crosses the tilt joint at
// the trunnion (the light rotates with the nacelle; the spar does not).
//
// REPLACES cableway_bore(), the 2 × Ø7 EDF "double-D" — retired Rev T1.  See
// the NAV_BORE_* parameter block for why: it could not carry two 10 AWG
// conductors at any realistic wire OD, and its 27.5 mm station now falls
// inside the Ø20.4 spar bore.
//
// Camber-centred at each end station via midline_frac(), so it follows the
// camber line as the section changes.  No thickness-scale factor:
// s1223_section() opens the thickness envelope about an UNSCALED camber line
// (Rev S1b), so re-applying the scale here would lift the bore off it.
module nav_bore() {
    xc = NAV_BORE_STATION;
    root_yc = midline_frac(xc / WING_CHORD_ROOT) * WING_CHORD_ROOT;
    tip_yc  = midline_frac(xc / WING_CHORD_TIP)  * WING_CHORD_TIP;

    // Root face (−1 mm) → 1 mm past the wing tip, so it breaks cleanly out of
    // the tip face clear of the pad (pad forward edge X = 12.0; this bore's
    // aft edge X = 10.0).
    hull() {
        translate([xc, root_yc, -1.0])
            cylinder(r = NAV_BORE_D / 2, h = 0.01);
        translate([xc, tip_yc + WING_DIHEDRAL, WING_SEMI_SPAN + 1.0])
            cylinder(r = NAV_BORE_D / 2, h = 0.01);
    }
}


// =============================================================================
// ── Module: tilt_shaft_bore — nacelle tilt drive shaft ──────────────────────
// =============================================================================
// Spanwise running-clearance bore for the Ø4 mm steel tilt drive shaft (plan
// 004 KTD1/KTD4).  Runs the full span: bulkhead servo → wingtip pinion.
//
// It exits the tip face UNDER the mount pad (pad spans X 12.0..50.5; this bore
// is at 43.0), which is deliberate — the pad gives the shaft's outboard bushing
// a thick, supported boss to run in instead of a 1.2 mm skin.
//
// Same constant-mm law as every other bore in this wing, so it stays parallel
// to the spar over the whole span and the webs cannot be eroded by taper.
module tilt_shaft_bore() {
    xc = SHAFT_BORE_STATION;
    root_yc = midline_frac(xc / WING_CHORD_ROOT) * WING_CHORD_ROOT;
    tip_yc  = midline_frac(xc / WING_CHORD_TIP)  * WING_CHORD_TIP;

    hull() {
        translate([xc, root_yc, -1.0])
            cylinder(r = SHAFT_BORE_D / 2, h = 0.01);
        translate([xc, tip_yc + WING_DIHEDRAL,
                   WING_SEMI_SPAN + TIP_PAD_PROUD + 1.0])
            cylinder(r = SHAFT_BORE_D / 2, h = 0.01);
    }
}


// =============================================================================
// ── Module: pylon_mount_pocket ────────────────────────────────────────────────
// =============================================================================
// Rectangular slot at the wing tip face (Z = WING_SEMI_SPAN - WING_SLOT_DEPTH).
// Receives the wing_attach_block from wing_nacelle_pylon_revo.scad.
// The pocket centre is at WING_SLOT_X_CTR of the TIP chord, Y = 0 (chord line).
//
// The bolt clearance holes are drilled from the tip face inward along Z,
// through the wing wall into the pocket (for M3×16 SHCS from tip side).
module pylon_mount_pocket() {
    tip_x_ctr = WING_SWEEP_LE + WING_CHORD_TIP * WING_SLOT_X_CTR;

    // ── Rectangular pocket (slot) ──────────────────────────────────────────
    translate([tip_x_ctr - WING_SLOT_W / 2,
               -WING_SLOT_H / 2,
               WING_SEMI_SPAN - WING_SLOT_DEPTH])
        cube([WING_SLOT_W, WING_SLOT_H, WING_SLOT_DEPTH + 0.1]);

    // ── M3 bolt clearance holes (from tip face inward) ─────────────────────
    for (angle = [45, 135, 225, 315]) {
        y_off = WING_BOLT_R * sin(angle);
        x_off = WING_BOLT_R * cos(angle) + tip_x_ctr;

        translate([x_off, y_off, WING_SEMI_SPAN - WING_SLOT_DEPTH - 2.0])
            cylinder(r = WING_BOLT_D / 2, h = WING_SLOT_DEPTH + 3.0);
    }
}


// =============================================================================
// ── Module: wing_tip_nacelle_mount_pad ────────────────────────────────────────
// =============================================================================
// Low boss at the wing tip face, centred on the spar, that provides:
//   • a flat register face for the nacelle trunnion to butt against,
//   • the seat for the AK7455 encoder board (aft lobe), and
//   • a thick, supported boss for the tilt drive shaft's outboard bushing,
//     which passes through the pad at station 43 rather than through 1.2 mm
//     of skin.
// Kept LOW (TIP_PAD_PROUD) — it sits in the nacelle inboard-face footprint and
// does not touch the exposed outer mould line.
//
// REV T1: a THREE-lobe hull, not Rev S1c's two.  S1c's teardrop existed to
// keep the pad's forward sweep off the two Ø7 EDF conduits that exited this
// face; those conduits are gone, but the shape survives — and gains a lobe —
// because everything the pad hosts now lies AFT of the spar in a line:
//     lobe A  X 28.0  r 14.0  trunnion register, concentric with the spar
//     lobe B  X 44.8  r  7.5  AK7455 board seat (HALL_SENS_R = 16.8)
//     lobe C  X 53.6  r  5.0  drive-shaft bushing boss
// Hulling them gives a tapering fin that reaches X 59 aft while its FORWARD
// edge stays at X 14.0 — which is the constraint that matters, because the nav
// conduit exits this same face at X 6.4..9.6 and a pad that reached it would
// be a blocked harness.  A plain disc large enough to cover lobe C would have
// a forward edge at X = -3 and cap the nav conduit outright.
// Additive only; the spar bore, shaft bore and sensor pocket are cut separately.
module wing_tip_nacelle_mount_pad() {
    spar_x = WING_SWEEP_LE + SPAR_BORE_STATION;  // spar chordwise position
    spar_y = spar_tip_y();                       // spar on the camber midline
    spar_z = WING_SEMI_SPAN;                     // wing tip spanwise station

    hull() {
        translate([spar_x, spar_y, spar_z])
            cylinder(r = TIP_PAD_R, h = TIP_PAD_PROUD, $fn = 64);
        translate([spar_x + HALL_SENS_R, spar_y, spar_z])
            cylinder(r = TIP_PAD_SENS_R, h = TIP_PAD_PROUD, $fn = 48);
        translate([SHAFT_BORE_STATION, spar_y, spar_z])
            cylinder(r = TIP_PAD_SHAFT_R, h = TIP_PAD_PROUD, $fn = 48);
    }
}


// =============================================================================
// ── Module: wing_tip_spar_through_bore ────────────────────────────────────────
// =============================================================================
// Continues the spar bore through the mount pad so the Ø20 spar can pass out of
// the tip face and carry the nacelle trunnion (SPAR_TIP_PROTRUSION).
//
// FIXES A LATENT AXIS BUG.  The Rev R2 version of this module wrapped its
// cylinder in `rotate([0, 90, 0])`, which maps +Z to +X — so it cut a
// CHORDWISE hole through the wingtip, not a spanwise continuation of the spar
// bore.  It went unnoticed because at Ø8.3 the stray hole was small and
// spar_bore() already ran the full span, so the module's real job (reaching
// through the 2 mm pad) was simply never done and nothing looked wrong.  At
// Ø20.4 the same code would cut a 20 mm chordwise gash through the tip.  The
// sibling module wing_tip_bearing_seat() had the correct convention all along
// and even documented it: "Spanwise axis is Z, so plain Z-axis cylinders are
// already correct."  Corrected to match.
module wing_tip_spar_through_bore() {
    spar_x = WING_SWEEP_LE + SPAR_BORE_STATION;
    spar_y = spar_tip_y();
    z0 = WING_SEMI_SPAN - 5.0;                       // overlap into the wing
    z1 = WING_SEMI_SPAN + TIP_PAD_PROUD + 1.0;       // clear through the pad

    translate([spar_x, spar_y, z0])
        cylinder(r = TILT_SPAR_BORE_CLEAR / 2, h = z1 - z0, $fn = 64);
}


// =============================================================================
// ── Module: wing_tip_bearing_seat — SUPERSEDED (Rev T1, 2026-08-29) ───────────
// =============================================================================
// SUPERSEDED and NO LONGER CALLED.  The MF128ZZ wingtip bearing existed because
// the Rev R2 spar ROTATED inside the wing.  Under Rev T1 the spar is fixed and
// bonded, and the tilt bearing has moved to the NACELLE's trunnion ring (plan
// 003 KTD3).  A bearing here would now be actively harmful: it would let the
// spar spin under the drive pinion's gear reaction, which is the one thing the
// fixed spar must not do.
// Body emptied; retained as a marker for traceability, matching the convention
// wing_tip_fixed_gear_inserts() already set in this file.
module wing_tip_bearing_seat() { }


// =============================================================================
// ── Module: wing_tip_hall_sensor_pocket — tilt-feedback encoder seat ─────────
// =============================================================================
// FIXED half of the wing/nacelle tilt-angle Hall sensor (Rev R2c).  Cuts a
// shallow PCB recess + 2× M2 pilots into the tip pad face, with the sensor IC
// seated OFF-AXIS at radius HALL_SENS_R from the spar (under the ring-magnet
// annulus carried on the nacelle — _export_pivot_slab.scad).  The IC face sits
// flush with / just below the pad face so the axial gap to the ring is
// HALL_AIR_GAP once the nacelle butts up.  Offset is CHORDWISE (X) so the pocket
// stays in the wide part of the section (Y half-thickness is limited at the tip;
// see HALL_PCB_H VERIFY note).  Fasteners here MUST be non-ferrous (steel screws
// inside HALL_KEEPOUT_R corrupt the read — docs §3.5 / EMI WBS §1.4.6).
module wing_tip_hall_sensor_pocket() {
    spar_x = WING_SWEEP_LE + SPAR_BORE_STATION;
    spar_y = spar_tip_y();
    face_z = WING_SEMI_SPAN + TIP_PAD_PROUD;   // pad outer (nacelle) face
    ic_x   = spar_x + HALL_SENS_R;             // IC sits chordwise-offset under the ring

    // PCB + solder recess (cut inward −Z from the pad face).
    translate([ic_x - HALL_PCB_W / 2, spar_y - HALL_PCB_H / 2, face_z - HALL_PCB_SEAT_T])
        cube([HALL_PCB_W, HALL_PCB_H, HALL_PCB_SEAT_T + 0.1]);

    // 2× M2 self-tap pilots, chordwise either side of the IC.
    for (dx = [-HALL_PCB_SCR_S, HALL_PCB_SCR_S])
        translate([ic_x + dx, spar_y, face_z - 4.0])
            cylinder(r = HALL_PCB_SCR_D / 2, h = 4.0 + 0.1, $fn = 24);
}


// =============================================================================
// ── Module: hall_sensor_cableway — fixed sensor-lead conduit to the root ─────
// =============================================================================
// Dedicated spanwise conduit for the AK7455 tilt encoder's shielded lead.
// Because the SENSOR is on the FIXED wing (only the ring magnet rotates), this
// lead does NOT twist with tilt — no slip ring.
//
// REV S1c (2026-08-18): a CONSTANT chordwise station (HALL_CABLE_STATION),
// AFT of the spar.  The old 0.33c fraction put it INSIDE the spar bore at the
// root once Rev S1b moved the spar to 45.15 mm.  Aft placement is deliberate:
// the spar then sits physically between this shielded low-level pair and the
// 40 A EDF double-D, which is now forward of the spar (EMI-hardening WBS
// §1.4.4/§1.4.6).  A Ø3.5 bore is small enough to hold wall in the shallower
// aft section where the Ø7 EDF conduits could not.
//
// A short chordwise jog links the tip end of the conduit to the sensor pocket.
module hall_sensor_cableway() {
    xc = HALL_CABLE_STATION;
    // Camber-centred at each end; no thickness-scale factor (see Rev S1b note
    // in spar_bore()).
    root_yc = midline_frac(xc / WING_CHORD_ROOT) * WING_CHORD_ROOT;
    tip_yc  = midline_frac(xc / WING_CHORD_TIP)  * WING_CHORD_TIP;

    // Spanwise run: root face (into fuselage) → wing tip.
    hull() {
        translate([xc, root_yc, -1.0])
            cylinder(r = HALL_CABLE_D / 2, h = 0.01);
        translate([xc, tip_yc + WING_DIHEDRAL, WING_SEMI_SPAN])
            cylinder(r = HALL_CABLE_D / 2, h = 0.01);
    }

    // ROOT-TENON PASS-THROUGH: NO LONGER REQUIRED (Rev T1).
    // Rev S1c had to drill this conduit down through the root tenon because
    // the tenon then spanned X 49.5..79.5 and the 54.0 mm station landed
    // inside it, dead-ending the wire in solid material.  Under Rev T1 the
    // tenon is a LOCATING feature at its 12 mm width (WING_ROOT_TAB_W), so it
    // spans X 58.5..70.5 and this conduit spans 50.75..57.25 — clear by
    // 1.25 mm.  The wire exits the root face in open air and the tenon crown
    // stays intact, which is strictly better than grooving it.
    // If TENON_LOAD_PATH is ever set to "enlarged_tenon" (W = 30 → X
    // 49.5..79.5) the collision RETURNS and this pass-through must come back.

    // Chordwise jog at the tip linking the conduit to the sensor pocket.
    spar_x = WING_SWEEP_LE + SPAR_BORE_STATION;
    ic_x   = spar_x + HALL_SENS_R;
    hull() {
        translate([xc, tip_yc + WING_DIHEDRAL, WING_SEMI_SPAN - 2.0])
            cylinder(r = HALL_CABLE_D / 2, h = 0.01);
        translate([ic_x, spar_tip_y(), WING_SEMI_SPAN - 2.0])
            cylinder(r = HALL_CABLE_D / 2, h = 0.01);
    }
}


// =============================================================================
// ── Module: wing_tip_fixed_gear_inserts — SUPERSEDED (Rev R2b, 2026-07-19) ─────
// =============================================================================
// SUPERSEDED and NO LONGER CALLED.  The tilt→nozzle GEAR train (fixed sector +
// nacelle Pinion A) was archived when the nozzle drive became Option B pushrod /
// bellcrank (nacelle_nozzle_pushrod.scad, pod Rev T/T2): the nozzle is now
// stroked by a crank on the ROTATING spar inside the nacelle, so there is no
// fixed gear on the wing tip.  The wing tip keeps only the bearing seat (the
// spar rotates in it).  Body emptied; retained as a marker for traceability.
module wing_tip_fixed_gear_inserts() { }


// =============================================================================
// ── Module: fuselage_root_tab ─────────────────────────────────────────────────
// =============================================================================
// A positive protrusion at the root face (Z = 0) that inserts into the fuselage
// wing slot.  VERIFY WING_ROOT_TAB_* parameters against fuselage hull STL before
// printing.
//
// CORRECTED 2026-08-24 (U5/KTD1): under TENON_LOAD_PATH = "two_rod" (default)
// the tab is RESTORED to its originally-intended, correct role — radial
// restraint and rotational location only.  It does NOT react the wing-root
// couple; the two CF tie rods (wing_root_tie_rod_fwd_bore() /
// wing_root_tie_rod_aft_bore(), cut in wing_one_side()) do that.  This
// corrects the stale comment that used to read "The tab provides radial
// restraint; the CF spar carries spanwise load" — that was written when the
// spar carried through the fuselage; under SPAR-01 it terminates at the wall
// on its own bearing and never touched this joint anyway, and CARGO-03c then
// (temporarily, before this fix) made the tab itself react the moment. Under
// TENON_LOAD_PATH = "enlarged_tenon" the tab reverts to that structural role
// at its documented AS-BUILT size — see the WING_ROOT_TAB_* selection above.
//
// The tab is centred chordwise at 50% root chord, at Y = 0 (chord line).
module fuselage_root_tab() {
    tab_x_ctr = WING_CHORD_ROOT * 0.50;

    translate([tab_x_ctr - WING_ROOT_TAB_W / 2,
               -WING_ROOT_TAB_H / 2,
               -WING_ROOT_TAB_L])
        cube([WING_ROOT_TAB_W, WING_ROOT_TAB_H, WING_ROOT_TAB_L + 0.1]);
}


// =============================================================================
// ── Module: wing_root_tie_rod_fwd_bore / wing_root_tie_rod_aft_bore ──────────
// =============================================================================
// U5 (KTD1 "two_rod" path): bonded CF tie-rod clearance bores that react the
// wing-root couple as a two-point system, replacing the tenon's former
// structural role.  Each is a straight, ROOT-ONLY bore (does NOT run to the
// tip — see the rationale in the ROD_FWD_*/ROD_AFT_* parameter block above),
// centred on the S1223 camber midline at its own chordwise station exactly
// like spar_bore()/cableway_bore(), running from just outboard of the root
// face inward (+Z) by the rod's own embed depth.
//
// Matching bosses/bores on the fuselage side live in
// airframe/blender-scripts/merge_cargo_interior.py (ROD_FWD_*/ROD_AFT_*),
// mirroring the PORT_INB/PORT_OUTB main-spar-boss embed pattern.
module wing_root_tie_rod_fwd_bore() {
    xc = ROD_FWD_STATION;
    yc = midline_frac(xc / WING_CHORD_ROOT) * WING_CHORD_ROOT;
    translate([xc, yc, -1.0])
        cylinder(r = ROD_FWD_D / 2, h = ROD_FWD_EMBED + 1.0, $fn = 32);
}

module wing_root_tie_rod_aft_bore() {
    xc = ROD_AFT_STATION;
    yc = midline_frac(xc / WING_CHORD_ROOT) * WING_CHORD_ROOT;
    translate([xc, yc, -1.0])
        cylinder(r = ROD_AFT_D / 2, h = ROD_AFT_EMBED + 1.0, $fn = 32);
}


// =============================================================================
// ── Module: wing_one_side ─────────────────────────────────────────────────────
// =============================================================================
// One wing panel (port or starboard before mirror).
//
// REV T1 (2026-08-29) — THE SPAR IS NOW A MEMBER OF THIS PART, NOT A SHAFT
// PASSING THROUGH IT.  The Ø20 CF tube is epoxy-bonded into spar_bore() over
// the full span and is the wing's primary bending member; the wing skin is a
// stressed fairing bonded to it.  Everything else in this module follows from
// that:
//   • the wing tip carries a REGISTER PAD, not a bearing seat — the tilt
//     bearing is on the nacelle's trunnion ring (plan 003 KTD3);
//   • the root tenon LOCATES and does not react moment — the spar does, into
//     a fuselage socket (see the WING ROOT LOAD PATH block);
//   • the tie-rod couple is not cut at all on the default path.
//
// Spanwise bore inventory, all at CONSTANT chordwise stations so they stay
// mutually parallel over the taper (fail-closed check:
// tools/wing_internal_clearance.py):
//     8.0  Ø3.2   nav_bore()             nav-light 3-core
//    28.0  Ø20.4  spar_bore()            bonded CF structural spar
//    44.5  Ø6.5   hall_sensor_cableway() AK7455 SPI quad + power pair
//    53.6  Ø4.4   tilt_shaft_bore()      nacelle tilt drive shaft
module wing_one_side() {
    difference() {
        union() {
            // ── Lofted wing solid ──────────────────────────────────────────
            wing_solid();

            // ── Fuselage root insertion tab (locating) ─────────────────────
            fuselage_root_tab();

            // ── Wing-tip nacelle register pad ──────────────────────────────
            wing_tip_nacelle_mount_pad();
        }

        // ── Bonded structural spar bore (Ø20.4, full span) ────────────────
        spar_bore();

        // ── Spar continuation through the tip pad, so the stub can reach
        //    the nacelle trunnion (SPAR_TIP_PROTRUSION) ───────────────────
        wing_tip_spar_through_bore();

        // ── Nav-light 3-core conduit, forward of the spar ─────────────────
        nav_bore();

        // ── Nacelle tilt drive shaft, aft of the spar ─────────────────────
        tilt_shaft_bore();

        // ── AK7455 encoder seat + its dedicated shielded cableway ─────────
        wing_tip_hall_sensor_pocket();
        hall_sensor_cableway();

        // ── Wing-root tie-rod couple — SUPERSEDED path only ────────────────
        // Not cut under the Rev T1 default.  Under "two_rod" the forward rod
        // (station 14.0, Ø8.2 → 9.9..18.1) INTERSECTS the Ø20.4 spar bore
        // (17.80..38.20); that path is retained as the design record and is
        // geometrically invalid at the Rev T1 spar.  See TENON_LOAD_PATH.
        if (TENON_LOAD_PATH == "two_rod") {
            wing_root_tie_rod_fwd_bore();
            wing_root_tie_rod_aft_bore();
        }
    }
}


// =============================================================================
// ── Module: wings (top-level render) ─────────────────────────────────────────
// =============================================================================
// Renders port, starboard, or both wings based on RENDER_SIDE.
//
// Coordinate permutation applied here converts internal geometry
//   (chord=X, thickness=Y, span=Z)  →  assembly output (span=X, chord=Y, thickness=Z)
// using the cyclic permutation matrix [X←Z, Y←X, Z←Y].
// This matches the canonical Serenity hull: span in X, chord in Y, thickness in Z.
//
// Port  wing: span extends in +X.
// Stbd  wing: internal mirror([0,0,1]) flips span to −Z, then permutation → −X.
module wings(render_side = RENDER_SIDE) {
    reorient = [[0, 0, 1, 0],
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, 0, 1]];
    if (render_side >= 0) {
        multmatrix(reorient) wing_one_side();
    }
    if (render_side <= 0) {
        multmatrix(reorient) mirror([0, 0, 1]) wing_one_side();
    }
}


// =============================================================================
// ── Render call ───────────────────────────────────────────────────────────────
// =============================================================================
wings(render_side = RENDER_SIDE);


// =============================================================================
// ── Print specifications ──────────────────────────────────────────────────────
// =============================================================================
// Material     : CF-PETG (structural wing → same as pylon)
// Layer height : 0.15 mm
// Walls        : 4 perimeter walls minimum
// Infill       : 40% gyroid
//                Upper-surface modifier: Load additional modifier mesh in slicer
//                over upper 60% of wing cross-section; set modifier infill to 65%
//                gyroid.  Differential infill density causes slight upper-surface
//                bow → adds effective camber beyond the S1223 baseline.
//                (Optional; omit if S1223 geometry alone is sufficient.)
// Nozzle       : Hardened-steel (CF-PETG abrasive)
// Orientation  : Lay wing flat, chord (X axis) horizontal, span (Z) on build plate.
//                Upper surface faces UP on the build plate.
//                Supports: Under leading edge radius overhang only (tree supports,
//                breakaway; do NOT support upper surface — will leave marks).
// Quantity     : 2 per aircraft (port + starboard — export separately).
//
// Post-print verification:
//   1. Spar bore: 12.3 ± 0.1 mm ID (CF-TUBE-12MM should slide with light force).
//   2. Pylon pocket: WING_SLOT_W × WING_SLOT_H slot accepts pylon block cleanly.
//   3. Root tab: insert into fuselage slot; must seat flush with no rocking.
//   4. Profile check: sight along span axis — upper surface should show a visible
//      convex camber consistent with S1223 (max camber ≈ 8.65% of chord, at
//      ~39% chord aft of leading edge).
//   5. Aerodynamic orientation: leading edge (rounded, x=0) faces forward.
//      Trailing edge (sharp/blunt, x=1) faces aft.  DO NOT install reversed.
//
// CRITICAL — Before printing:
//   Chord dimensions (WING_CHORD_ROOT=129, WING_CHORD_TIP=93) are derived from
//   archives/stl/s_wings_both_shell24.stl (2.929× Thingiverse scale).  VERIFY
//   WING_SLOT_W, WING_SLOT_H, WING_ROOT_TAB_W, WING_ROOT_TAB_H against the
//   fuselage cargo-section wing slot before cutting or printing.
//   NOTE: Wing TE at root now sits at hull Y ≈ +122 mm (within cargo section
//   aft boundary Y ≈ +132 mm) — consistent with fuselage geometry.
//   VERIFY pylon bolt circle (WING_BOLT_R=16mm) fits within the 93mm tip chord;
//   bolt Y-offsets reach ±11.3 mm from chord line (≈ S1223 upper-surface limit
//   at 50% chord) — reduce WING_BOLT_R if the pylon block geometry requires it.
//
// Render commands (one wing at a time for slicer import):
//   openscad -o wing_port_s1223_revo.stl \
//            wings_s1223_revo.scad -D RENDER_SIDE=1
//   openscad -o wing_stbd_s1223_revo.stl \
//            wings_s1223_revo.scad -D RENDER_SIDE=-1
// =============================================================================
