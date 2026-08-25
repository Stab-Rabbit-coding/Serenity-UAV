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
//   Re at root (40 kt, 129 mm chord) ≈ 177 000 — above S1223 operating floor.
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
// At cruise (40 kts, Re ≈ 177 000 at root), the S1223 delivers CL ≈ 1.55 at
// 3° AoA versus CL ≈ 0.32 for the original flat-plate wing.  Wing lift rises
// from ~3 % to ~22 % AUW at cruise — nearly a 7× improvement with no change to
// the outward planform silhouette.
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
// S1223 Profile Data
// ------------------
// Coordinates from UIUC Airfoil Database (Selig & Guglielmo 1997).
// Normalised: x ∈ [0,1] (LE=0, TE=1), y = t/c ratio (positive = upper surface).
// Characteristics at design Re ≈ 100 000–200 000:
//   Maximum thickness : 12.14% chord at 22.6% chord
//   Maximum camber    :  8.65% chord at 39.4% chord
//   CL_max            : ≈ 2.0  (Re=100k, from Selig & Guglielmo wind tunnel)
//   CL at 3° AoA      : ≈ 1.55 (Re=91k, interpolated)
//   L/D at CL=1.0     : ≈ 30–35
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
THICKNESS_SCALE =   1.0;  // [1.0 = full S1223 t/c; 0.85–1.0 recommended range]
                           // Camber line is NOT affected — only thickness offset.
                           // Below 0.75: separation bubble risk at Re < 100k.
                           // This is the ROOT-station thickness scale; the tip
                           // uses THICKNESS_SCALE_TIP (below) so the 12 mm spar
                           // stays fully skinned in the thin outboard section.

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
// This is now a THICKNESS-only multiplier in fact as well as in name — see
// s1223_section() below.  It no longer stretches the camber line, so the tip
// keeps S1223's canonical 8.12 % camber instead of being driven to 11.75 %.
// Tip t/c rises 13.45 % → 19.47 % (thickness only).
//
// CANON NOTE: this is an outer-mold-line change local to the wingtip; verify
// against the canonical Serenity wing silhouette before committing to print
// (see TODO.md §1.1.2).  Lower the value only if the bore stays skinned.
// UNVERIFIED BY CFD: the OpenFOAM study intended to quantify the drag penalty
// of a 19.5 % t/c tip at Re ≈ 2.1e5 is blocked on mesh generation
// (tools/wing_cfd_openfoam.py, WIP).  The camber-preservation argument does
// not depend on it, but the absolute penalty of the thicker tip is not yet
// quantified.
THICKNESS_SCALE_TIP = 1.45;  // [tip thickness multiplier; root stays THICKNESS_SCALE]

// ── Rotating tilt-spar bore (Rev R2 — unified 8 mm rotating spar) ────────────
// UNIFIED ROTATING SPAR (2026-07-18): the wing's single spar is now the 8 mm
// rotating tilt-spar (AISI 4130, hollow 5 mm ID) — it is BOTH the wing
// structural spar AND the nacelle tilt axis, and it ROTATES (servo-driven from
// the cargo bay, keyed to the nacelle).  The 12 mm fixed CF tube is retired.
// This bore is therefore a rotating CLEARANCE bore (not a press-fit): the wing
// is located by its fuselage root tab and rides on the spar at the wingtip
// bearing (§ wing_tip_bearing_seat); the second bearing lives in the cargo bay.
// The bore stays a SINGLE STRAIGHT cylinder at a fixed chordwise station
// (parallel to the straight LE → no plan-view skew) centred on the airfoil
// CAMBER MIDLINE so it stays skin-enclosed as the section tapers.  See
// docs/TILT_SPAR_ANALYSIS.md.  (The nav-light 3-core routes INSIDE the hollow
// spar's 5 mm ID; the EDF power/signal keep the separate double-D cableway.)
SPAR_BORE_OD      =   8.3;  // [mm] rotating-spar clearance bore = 8 mm OD + 0.15 mm/side
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
SPAR_BORE_STATION =  45.15; // [mm] chordwise station aft of LE — CONSTANT over the
                            //      span (35.0 % root / 48.5 % tip chord).
                            //      Constant ⇒ bore ∥ leading edge ⊥ centreline.
                            // The bore-centre thickness height is taken from the
                            // ACTUAL S1223 camber midline at each station's own
                            // chord fraction (midline_frac(), below) — NOT a single
                            // constant — so it stays centred (root breakout fixed).

// ── Harness cableway (Rev S1c — moved FORWARD of the spar) ───────────────────
// The 8 mm rotating spar is hollow (≈ 5 mm ID) — enough for the nav-light 3-core
// (Ø 2.5 mm), which routes THROUGH the hollow spar to the outboard nacelle nav
// light (95° tilt twist is benign — docs/TILT_SPAR_ANALYSIS.md §5), but NOT for
// the 40 A EDF ESC feeds.  This dedicated wing conduit carries those: TWO
// parallel Ø CABLE_BORE_D bores forming a flat "double-D", camber-centred at
// each station.  Splitting into two bores keeps the EDF power pair separate
// from ESC signal/telemetry (noise).
//
// REV S1c (2026-08-18) — WHY THIS MOVED, AND WHY IT IS NOW CONSTANT-mm:
// Rev S1b moved SPAR_BORE_STATION 22.0 → 45.15 mm but left this conduit on a
// constant chord FRACTION (0.48c).  A constant-mm bore and a constant-fraction
// bore CONVERGE as the chord tapers 129 → 93 mm, so the pair that cleared at
// the root did not stay clear: the forward Ø7 conduit entered the Ø8.3 spar
// bore from 29.6 % span outboard, and at the tip BOTH conduits were merged
// with the spar (0.48 × 93 = 44.6 mm vs a spar at 45.15 mm).  That is 40 A of
// EDF feed sharing a cavity with a rotating steel spar — a wiring fault, not a
// tolerance one.  It was invisible to tools/wing_spar_station_fit.py, which
// sizes ONE bore against its section and cannot see bore-to-bore convergence;
// tools/wing_internal_clearance.py was written for exactly this class of fault
// and is fail-closed.
//
// The conduit had to go FORWARD of the spar: every station AFT of it fails, and
// not marginally — S1223 loses depth fast, and at the 58 mm station the TIP
// section is only 4.17 mm deep, so a Ø7 bore has negative wall before any
// thickening.  Forward of the spar the section is near its max-thickness point
// at BOTH ends (27.5 mm = 21.3 % root / 29.6 % tip chord), which is why the
// walls there are ~4.5 mm instead of ~1.2 mm.
//
// CONSTANT MILLIMETRES, matching the spar's own law (see SPAR_BORE_STATION):
// with a straight LE (WING_SWEEP_LE = 0), two constant-mm bores hold the SAME
// chordwise separation at every span station, so the web cannot be eroded by
// taper.  A chord-fraction conduit re-creates the convergence this change
// exists to remove.
CABLE_BORE_D    =   7.0;  // [mm] each conduit bore diameter (Ø7 ≈ 38 mm² each)
// REV S1c: separation 8.0 → 9.5 mm.  At 8.0 the web between the two Ø7 bores
// was 1.0 mm — under two extrusions at the 0.6 mm nozzle WALL_T is specified
// for, so it would not have printed as a wall and the "double-D" would have
// fused into one cavity, defeating the power/signal split it exists for.
// 9.5 mm gives a 2.5 mm web = WALL_T.  The chord forward of the spar affords
// it; this was only ever tight because the pair was crowded aft.
CABLE_BORE_SEP  =   9.5;  // [mm] chordwise centre-to-centre (overall ≈ 16.5 mm)
CABLE_BORE_STATION = 27.5; // [mm] chordwise station aft of LE — CONSTANT over the
                          //      span, like SPAR_BORE_STATION.  Conduits land at
                          //      22.75 / 32.25 mm.  Clearances held over the whole
                          //      span (tools/wing_internal_clearance.py):
                          //        web to spar bore   +5.25 mm
                          //        skin, root / tip   +4.45 / +4.84 mm
                          //        gap to wingtip pad +1.40 mm
                          //      The nacelle harness entry port must match this
                          //      station — see HARNESS_PORT_Z in
                          //      airframe/openscad/nacelles/nacelle_pod_50mm_tandem.scad.

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

// ── Wing-tip rotating-spar interface (Rev R2, 2026-07-18) ─────────────────────
// ROTATING TILT-SPAR mechanism — see docs/TILT_SPAR_ANALYSIS.md.
//   • The 8 mm spar ROTATES (servo-driven from the cargo bay) and is FIXED to
//     the nacelle. The wing is fixed; the spar spins inside it on two bearings
//     (root bearing in the cargo bay + this wingtip bearing).
//   • The wing tip therefore provides: (a) a rotating-clearance through-bore for
//     the spar, (b) a wingtip BEARING SEAT (F688ZZ 8×16×5) that carries the
//     wing/nacelle loads and lets the spar rotate, and (c) a FIXED R22 sector
//     gear bolted coaxial with the spar (the SAME sector previously carried by
//     the retired pylon — relocated to the fixed wingtip; nacelle gear housing
//     unchanged).  The nacelle's Pinion A orbits this fixed sector as the
//     nacelle tilts → nozzle iris tracks tilt angle.  (Gear-size study
//     2026-07-18: R22 kept over an R14+idler shrink — docs/TILT_SPAR_ANALYSIS.md
//     §6; airframe/openscad/nacelles/gear_shell_compare.scad.)
//   • The fixed gear stands only minimally proud (TIP_PAD_PROUD) and butts
//     against the nacelle inboard face; the nacelle housing already clears
//     Pinion A, so no pylon/block is needed.
//   • NO nacelle boss socket (the nacelle is keyed to the spar, not pinned to a
//     socket) — that feature is deleted vs Rev R1b.
//
// Rotating tilt spar (8 mm OD × 1.5 mm wall, 5 mm ID, AISI 4130 — docs §3):
TILT_SPAR_OD          =   8.0;   // [mm] rotating spar outer diameter
TILT_SPAR_BORE_CLEAR  =   8.3;   // [mm] rotating clearance bore through wing (0.15 mm/side)

// Wingtip bearing seat (MF128ZZ flanged, 8 ID × 12 OD × 3.5 W):
// Rev R2d (2026-07-19): DOWNSIZED from F688ZZ (Ø16).  The Ø16 seat radius
// (7.975 mm) exceeded the S1223 tip half-thickness (7.80 mm at the spar station,
// even at THICKNESS_SCALE_TIP = 1.25) and cut through BOTH airfoil skins by
// ~0.21 mm along the seat depth.  MF128ZZ (Ø12, flange Ø13.5 → r6.75) seats with
// ~1.0 mm skin margin.  Wingtip radial reaction ≈ 19 N (dyn) ≪ MF128 dynamic
// capacity (~700 N), so the downsize is load-safe.  The ROOT (cargo-bay) bearing
// stays F688ZZ — no thin section there.  docs/TILT_SPAR_ANALYSIS.md §8.
TIP_BRG_OD            =  12.0;   // [mm] bearing outer diameter
TIP_BRG_SEAT_D        =  11.95;  // [mm] press-fit seat bore (0.025 mm/side interference)
TIP_BRG_W             =   3.5;   // [mm] bearing width (seat depth)
TIP_BRG_FLANGE_OD     =  13.5;   // [mm] flange OD → shallow counterbore, seats flush
TIP_BRG_FLANGE_T      =   1.0;   // [mm] flange counterbore depth

// Fixed R22 sector gear mount (coaxial with spar, on nacelle-facing tip face):
FIX_GEAR_BC_R         =  11.0;   // [mm] M2.5 insert bolt circle (outside 18 mm flange, inside 21 mm R22 gear root)
FIX_GEAR_N_BOLTS      =   3;     // [count] 120° spacing
FIX_GEAR_INSERT_OD    =   3.7;   // [mm] M2.5 heat-set insert bore
FIX_GEAR_INSERT_L     =   5.5;   // [mm] insert pocket depth
FIX_GEAR_PLATE_H      =   3.0;   // [mm] sector gear plate thickness (reference)

// Wingtip mount pad — minimal boss around the spar at the tip face that houses
// the bearing seat + gear-bolt inserts. Kept low (butts against the nacelle
// inboard face) rather than standing on a tall block.
// REV S1c (2026-08-18): the pad is a TEARDROP, not a disc.  As a Ø29.5 disc it
// spanned X 30.4..59.9 on the tip face and capped BOTH relocated EDF conduits —
// the conduits exit the tip face into the nacelle, so a pad over them is not a
// cosmetic overlap, it is a blocked harness.  The disc OD was sized when the
// EDF pair sat AFT at 0.48c; with the pair now forward at 27.5 mm the disc can
// no longer be both small enough to clear them and large enough to host the
// AK7455 pocket at R = 11.
//
// A teardrop resolves it because the two things the pad must host are on
// OPPOSITE sides of the spar: the Ø13.5 bearing flange is concentric (needs
// r ≥ 6.75 all round) and the sensor pocket is purely AFT (needs reach to
// R ≈ 14.5).  Hulling a small forward circle to a small aft one covers both
// without the forward sweep a disc would need.  Forward edge lands at
// X = 37.15, clearing the aft EDF conduit (aft edge 35.75) by 1.40 mm.
// Proud only (Z > tip face) — sits in the nacelle inboard-face footprint; does
// not touch the exposed OML.
TIP_PAD_FWD_R         =   8.0;   // [mm] pad radius at the spar — Ø13.5 flange (r6.75) + 1.25 rim
TIP_PAD_AFT_R         =   5.5;   // [mm] pad radius at the sensor pocket centre (spar + HALL_SENS_R);
                                //      reaches X 61.65, covering the 7 mm PCB seat (52.65..59.65)
TIP_PAD_PROUD         =   2.0;   // [mm] proud height beyond wing tip face (minimal)

// ── Wing/nacelle tilt-angle Hall sensor (Rev R2c, 2026-07-19) ─────────────────
// TRUE-NACELLE-TILT FEEDBACK.  A magnetic angle encoder at the wing/nacelle
// joint closes the tilt-servo loop on the ACTUAL nacelle angle (output side), so
// the loop is independent of tilt-spar torsional wind-up
// (docs/TILT_SPAR_ANALYSIS.md §1, §3.5).  This is the FIXED (sensor) half; the
// rotating diametric RING magnet is carried on the nacelle spar hub (see
// airframe/openscad/nacelles/_export_pivot_slab.scad).
//
// OFF-AXIS read: the spar is a THROUGH-shaft here (it continues into the nacelle
// — there is no free shaft end), so an on-axis end-of-shaft encoder cannot be
// used.  A diametric RING magnet rides the spar on the nacelle and the sensor IC
// sits OFF-AXIS on this pad, under the ring annulus, facing it across a small
// axial air gap.  Use an off-axis-capable IC (MPS MA732 / Magntek MT6701) — the
// on-axis AS5600 used on the antenna gimbal will NOT work through a shaft.
//
// STEEL-SPAR ISSUE (docs §3.5 / EMI-hardening WBS §1.4.6): the 4130/17-4 PH spar
// is ferromagnetic and runs through the ring centre, distorting the bias field.
// Geometry mitigations: (a) the ring is stood off the steel by a non-ferrous
// collar on the nacelle side (magnet ID 10 mm over the 8 mm spar); (b) the PCB
// seat and every fastener within HALL_KEEPOUT_R of the IC are NON-FERROUS
// (brass / 316 / Al / nylon — NOT the steel bearing screws); (c) a factory
// zero-cal over the full −5..90° sweep absorbs residual distortion (firmware —
// avionics).  A ferrous shaft through a ring magnet is a supported commercial
// arrangement, but MUST be calibrated in situ.
//
// PLACEMENT (Rev R2d 2026-07-19; sensor part and pad revised Rev S1c 2026-08-18):
// SENSOR = AKM AK7455 (SPI, off-axis capable) on a small in-house PCB
// (ENC-NACELLE-1 / MAL-TILT-ENC-PCB; REFERENCES.md REF-SENSOR-008).  It
// SUPERSEDES the Magntek MT6701 named in earlier revisions of this block —
// MT6701 and AS5600 were both rejected as on-axis parts, and the spar is a
// THROUGH-shaft here.
//
// The IC sits OFF-AXIS at HALL_SENS_R = 11 mm, CHORDWISE-aft of the spar, clear
// of the Ø13.5 bearing-flange keep-out (r6.75) on the pad face — the earlier
// R = 6 pocket collided with the flange/seat.  The diametric ring is OD 22
// (mean r ≈ 11) so the IC reads mid-annulus.  Aft offset (not +Y) keeps the
// pocket in the wide chord direction, well under the top skin (Y-thickness is
// limited at the tip).
//
// REV S1c: the pocket is no longer THREADED between the bearing flange and the
// EDF double-D.  That congestion existed only because the EDF pair sat aft at
// 0.48c; with the pair moved forward to the 27.5 mm station (see the harness
// cableway block) the whole region aft of the spar is free, and the pad's aft
// lobe (TIP_PAD_AFT_R) hosts the 7 × 7 board outright.  A compact in-house
// board (AK7455 QFN + 2 decoupling caps + a direct-solder pigtail, no
// connector) fits at R = 11.
//
// The off-axis air-gap / ring geometry remains a REQUIRES-VERIFICATION item vs
// the AK7455 datasheet (REFERENCES.md; TODO §0.8) and is gated on the bench-cal
// in wings-nacelles WBS §1.1.3.6.
HALL_RING_OD    =  22.0;  // [mm] diametric ring-magnet OD (matches nacelle seat)
HALL_RING_ID    =  10.0;  // [mm] ring-magnet ID (rides non-ferrous collar on spar)
HALL_SENS_R     =  11.0;  // [mm] MT6701 IC offset from spar axis ≈ ring mean radius
HALL_AIR_GAP    =   1.5;  // [mm] axial magnet-face → IC-face gap (set by nacelle standoff)
HALL_PCB_W      =   7.0;  // [mm] sensor PCB seat width (chordwise, X) — fits the flange↔EDF
                          //      gap; MT6701 3×3 QFN + caps + direct-solder pigtail
HALL_PCB_H      =   7.0;  // [mm] sensor PCB seat height (thickness, Y) — clears top skin
                          //      (pocket top Y≈12.4 vs ceiling ≈16.4 at this station)
HALL_PCB_SEAT_T =   2.0;  // [mm] PCB + solder recess depth into the pad face
HALL_PCB_SCR_D  =   1.7;  // [mm] M2 self-tap pilot (2×, chordwise ±HALL_PCB_SCR_S)
HALL_PCB_SCR_S  =   2.5;  // [mm] screw pilot half-spacing (chordwise) — within W/2 span
HALL_KEEPOUT_R  =  10.0;  // [mm] NON-FERROUS keep-out radius around the IC
HALL_CABLE_D    =   3.5;  // [mm] 4-wire I²C sensor conduit (VCC/GND/SDA/SCL, shielded)
// REV S1c (2026-08-18): 0.33c → a CONSTANT 54.0 mm station, AFT of the spar.
// The old fraction was sized against a spar at the 22.0 mm station and was left
// behind by Rev S1b: 0.33 × 129 = 42.57 mm put this Ø3.5 conduit INSIDE the
// Ø8.3 spar bore at the ROOT (conduit 40.82..44.32 vs spar 41.00..49.30) — the
// mirror image of the EDF failure above, converging inboard instead of outboard.
//
// It stays AFT of the spar deliberately, where the EDF double-D could not go.
// A Ø3.5 sensor bore needs far less depth than a Ø7 power conduit, and 54.0 mm
// is the station where BOTH constraints close: a 2.95 mm web to the spar bore
// (≥ WALL_T) and 1.28 mm of tip skin — thicker than the 1.16 mm the root spar
// already runs at and prints, which is the floor tools/wing_spar_station_fit.py
// enforces.  Keeping it aft preserves the original EMI intent in its strongest
// form: the ferromagnetic spar sits physically BETWEEN the shielded low-level
// sensor pair and the 40 A EDF feeds (EMI-hardening WBS §1.4.4/§1.4.6), rather
// than trading that barrier for a printed web, which is what any forward
// placement would have done.
//
// Its tip end (X = 54.0) also sits just aft of the Ø11.95 bearing seat
// (aft edge X ≈ 51.1), shortening the jog to the R = 11 sensor pocket (X ≈ 56.15)
// to ~2.2 mm.
HALL_CABLE_STATION = 54.0; // [mm] chordwise station aft of LE — CONSTANT over the
                          //      span, like SPAR_BORE_STATION and CABLE_BORE_STATION

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

// ── Wing root joint load path (KTD1/U5, 2026-08-24 refinement) ───────────────
// CARGO-03c found the tenon under-strength as a STRUCTURAL joint (10.14 MPa
// bearing at ultimate vs. the repo's only CF-PETG figure, 5 MPa bond-limited,
// docs/structural_analysis.md §7.3 — FOS 0.49) and, per the owner's
// <15 MPa-fusion-strength decision rule, routed the load to a bonded CF rod
// instead of growing the tenon.  A feasibility pass then found a SINGLE rod
// forward of the main spar works (Ø8.2 mm at 14 mm from LE) but a matching
// Ø8.2 mm AFT rod does not fit anywhere aft of the spar (the main spar bore's
// aft edge at 49.30 mm and the Hall/encoder conduit's fixed Rev S1c span
// 52.25..55.75 mm leave no room at any station without breaking the wall or
// the skin).  A smaller Ø6.2 mm aft rod DOES fit, aft of the Hall conduit —
// see ROD_AFT_* below.  So the tenon is now traded out of the load path
// entirely and replaced by a TWO-ROD couple (not a single rod vs. the tenon).
//
// TENON_LOAD_PATH selects which joint reacts the wing-root couple:
//   "two_rod"       (DEFAULT) — two bonded CF rods (below) react the couple;
//                     the tenon is reduced to a locating/index feature only.
//   "enlarged_tenon" — the tenon alone reacts the couple, grown to the
//                     airframe's measured maximum envelope (39.2 x 20.1 mm,
//                     tools/wing_root_deconflict.py max_tenon_envelope()).
//                     Requires a CF-PETG fusion/bearing coupon test clearing
//                     >= 15 MPa (root TODO.md §1.1.4 LG-11) — NOT yet
//                     available, so this path is documented but NOT default.
// Kept as a named constant, not deleted, per KTD1: a future coupon result
// >= 15 MPa can swap the joint back to the tenon without re-deriving the
// sizing table.
TENON_LOAD_PATH = "two_rod";  // ["two_rod" | "enlarged_tenon"]

// ── Wing root fuselage tab (locating/index feature under "two_rod"; full
//    structural tenon under "enlarged_tenon") ────────────────────────────────
// The root face (Z=0) must interface with the fuselage wing slot.
// VERIFY slot dimensions in fuselage hull STL before printing.
//
// "two_rod" (default): the two CF rods below react the entire wing-root
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

WING_ROOT_TAB_W = (TENON_LOAD_PATH == "two_rod") ?
                   WING_ROOT_TAB_W_LOCATING : WING_ROOT_TAB_W_ENLARGED;
WING_ROOT_TAB_H = (TENON_LOAD_PATH == "two_rod") ?
                   WING_ROOT_TAB_H_LOCATING : WING_ROOT_TAB_H_ENLARGED;
WING_ROOT_TAB_L = (TENON_LOAD_PATH == "two_rod") ?
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
// ── Module: cableway_bore ────────────────────────────────────────────────────
// =============================================================================
// Two parallel spanwise conduits (a flat "double-D") for the nacelle harness —
// the 40 A EDF power feeds cannot fit the spar-tube ID (see parameter block).
//
// REV S1c (2026-08-18): the pair sits at a CONSTANT chordwise station
// (CABLE_BORE_STATION), FORWARD of the spar, replacing the constant chord
// FRACTION that converged onto the spar bore after Rev S1b moved the spar aft.
// Because the station is now constant in millimetres — the same law the spar
// uses — root and tip share one X, so the conduits run truly parallel to the
// spar and the web between them cannot be eroded by chord taper.  Each is still
// camber-centred at its own end station via midline_frac(), so the pair follows
// the camber line as the section changes.  Runs full span (root face into the
// fuselage, tip face into the nacelle harness port).
module cableway_bore() {
    // Chordwise conduit centre — one constant station, root and tip alike.
    xc = CABLE_BORE_STATION;
    // Camber-centred at each end.  No thickness-scale factor: s1223_section()
    // scales thickness about the camber line, so the camber line is unscaled
    // (Rev S1b) and re-applying the scale here would lift the bore off it.
    root_yc = midline_frac(xc / WING_CHORD_ROOT) * WING_CHORD_ROOT;
    tip_yc  = midline_frac(xc / WING_CHORD_TIP)  * WING_CHORD_TIP;

    // NO ROOT-TENON PASS-THROUGH IS NEEDED ANY MORE (Rev S1c).  The Rev R2d/R2e
    // straight tenon drill existed because the double-D at 0.48c landed at
    // X ≈ 57.9 / 65.9, inside the fuselage_root_tab (X 49.5..79.5), and the
    // wires dead-ended in solid tenon.  At the 27.5 mm station the conduits are
    // at X 22.75 / 32.25 — entirely FORWARD of the tenon — so they exit the root
    // face in clear air and the tenon crown is left intact.  The sensor conduit
    // inherits the tenon problem instead; see hall_sensor_cableway().
    for (dx = [-CABLE_BORE_SEP / 2, CABLE_BORE_SEP / 2]) {
        // Spanwise conduit: root face (−1 mm) → 1 mm past the wing tip, so it
        // breaks cleanly out of the tip face into the nacelle harness port.
        hull() {
            translate([xc + dx, root_yc, -1.0])
                cylinder(r = CABLE_BORE_D / 2, h = 0.01);
            translate([xc + dx, tip_yc + WING_DIHEDRAL, WING_SEMI_SPAN + 1.0])
                cylinder(r = CABLE_BORE_D / 2, h = 0.01);
        }
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
// Minimal boss at the wing tip face, centered on the tilt spar, that houses the
// wingtip bearing seat and the fixed-gear bolt inserts. Kept LOW (TIP_PAD_PROUD)
// so the fixed R14 sector gear nests into the nacelle inboard recess rather than
// standing on a tall block — preserves the canonical nacelle silhouette.
// Additive only; the bearing seat / bore / insert pockets are cut separately.
module wing_tip_nacelle_mount_pad() {
    spar_x = WING_SWEEP_LE + SPAR_BORE_STATION;  // spar chordwise position
    spar_y = spar_tip_y();                          // spar on the camber midline (not chord line)
    spar_z = WING_SEMI_SPAN;                      // wing tip spanwise station

    // Low TEARDROP pad, proud of the tip face by TIP_PAD_PROUD only (Rev S1c).
    // Hull of a forward circle on the spar axis (hosts the bearing flange) and a
    // smaller aft circle on the sensor-pocket axis (hosts the AK7455 seat).  The
    // forward edge stops at spar_x − TIP_PAD_FWD_R so it clears the relocated
    // EDF double-D, which exits this same face.
    hull() {
        translate([spar_x, spar_y, spar_z])
            cylinder(r = TIP_PAD_FWD_R, h = TIP_PAD_PROUD, $fn = 48);
        translate([spar_x + HALL_SENS_R, spar_y, spar_z])
            cylinder(r = TIP_PAD_AFT_R, h = TIP_PAD_PROUD, $fn = 48);
    }
}


// =============================================================================
// ── Module: wing_tip_spar_through_bore ────────────────────────────────────────
// =============================================================================
// Rotating-clearance bore for the 8 mm spar, spanwise through the wing tip and
// pad. The spar ROTATES, so this is a clearance bore (TILT_SPAR_BORE_CLEAR),
// NOT a press-fit. Centered at SPAR_BORE_STATION chordwise, Y = 0.
module wing_tip_spar_through_bore() {
    spar_x = WING_SWEEP_LE + SPAR_BORE_STATION;
    spar_y = spar_tip_y();
    bore_z_start = WING_SEMI_SPAN - 20.0;                    // well inside the wing
    bore_z_end   = WING_SEMI_SPAN + TIP_PAD_PROUD + 2.0;     // through the pad

    translate([spar_x, spar_y, bore_z_start])
        rotate([0, 90, 0])
            cylinder(r = TILT_SPAR_BORE_CLEAR / 2,
                     h = bore_z_end - bore_z_start,
                     $fn = 32);
}


// =============================================================================
// ── Module: wing_tip_bearing_seat ─────────────────────────────────────────────
// =============================================================================
// Press-fit seat for the wingtip bearing (F688ZZ 8×16×5), bored into the pad
// face at the tip. Outer race fixed here; inner race rotates on the spar. A
// shallow counterbore seats the F688ZZ flange flush with the pad face.
// The seat opens toward the nacelle (+Z spanwise), the flange facing outboard.
module wing_tip_bearing_seat() {
    spar_x = WING_SWEEP_LE + SPAR_BORE_STATION;
    spar_y = spar_tip_y();
    face_z = WING_SEMI_SPAN + TIP_PAD_PROUD;  // pad outer face (nacelle side)

    // Spanwise axis is Z, so plain Z-axis cylinders are already correct.
    // Bearing bore (OD seat), cut inward (−Z) from the pad face.
    translate([spar_x, spar_y, face_z - TIP_BRG_W])
        cylinder(r = TIP_BRG_SEAT_D / 2, h = TIP_BRG_W + 0.1, $fn = 48);

    // Flange counterbore at the very face (flush seat for the F688ZZ flange).
    translate([spar_x, spar_y, face_z - TIP_BRG_FLANGE_T])
        cylinder(r = TIP_BRG_FLANGE_OD / 2, h = TIP_BRG_FLANGE_T + 0.1, $fn = 48);
}


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

    // ROOT-TENON PASS-THROUGH (inherited from the EDF pair at Rev S1c).  The
    // fuselage_root_tab spans X 49.5..79.5, and at the 54.0 mm station this
    // conduit (X 52.25..55.75) now lands inside it — the same dead-end the EDF
    // double-D used to hit at 0.48c.  A SEPARATE STRAIGHT, AXIAL (constant X,Y)
    // bore continues it down through the tenon and out the inboard face, so the
    // root-face opening and the tenon-exit opening stay perfectly coaxial and
    // the wire threads straight.  SOUNDNESS: at Ø3.5 on a 30 × 20 mm tenon this
    // only grooves the crown (root_yc ≈ +9.8, so the bore reaches ≈ +11.6 vs
    // the Y = +10 tenon top); the full-width lower ~15 mm of the tenon — the
    // load-bearing spine — is untouched.  This is a strictly SMALLER intrusion
    // than the Ø7 double-D it replaces there.
    translate([xc, root_yc, -(WING_ROOT_TAB_L + 1.0)])
        cylinder(r = HALL_CABLE_D / 2, h = WING_ROOT_TAB_L + 2.0, $fn = 32);

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
// Builds the solid, then subtracts the spar bore.
// The fuselage root tab is additive (−Z from root face, inboard direction).
// INTEGRATION (Rev R2, 2026-07-18): Rotating 8 mm tilt-spar mechanism. The wing
// tip carries a bearing seat + rotating through-bore + fixed R14 gear mount pad;
// the separate wing_nacelle_pylon_revo.scad component is superseded and archived.
// See docs/TILT_SPAR_ANALYSIS.md.
module wing_one_side() {
    difference() {
        union() {
            // ── Lofted wing solid ──────────────────────────────────────────
            wing_solid();

            // ── Fuselage root insertion tab ────────────────────────────────
            fuselage_root_tab();

            // ── Wing-tip nacelle mount pad (Rev R2) ─────────────────────────
            // Low boss at the tip housing the bearing seat + fixed-gear inserts.
            // Stays low so the fixed R14 gear nests into the nacelle recess.
            wing_tip_nacelle_mount_pad();
        }

        // ── CF spar bore (spanwise, 12 mm OD wing structural spar) ────────
        spar_bore();

        // ── Rotating tilt-spar clearance bore (8 mm spar, through wing tip)
        wing_tip_spar_through_bore();

        // ── Wingtip bearing seat (F688ZZ 8×16×5, press-fit) ──────────────
        wing_tip_bearing_seat();

        // (Fixed sector-gear inserts removed Rev R2b — gear train archived;
        //  nozzle now pushrod-driven from the rotating spar.  No wing gear.)

        // ── Tilt-feedback Hall sensor seat + its dedicated cableway (Rev R2c)
        wing_tip_hall_sensor_pocket();
        hall_sensor_cableway();

        // ── Harness cableway (2× Ø7 conduits for EDF power + signal) ──────
        cableway_bore();

        // ── Wing-root tie-rod couple (U5, "two_rod" path only) ─────────────
        // Replaces the tenon's former structural role; see the module docs
        // above and the couple-force derivation in
        // airframe/fuselage-mid/WBS.md §1.1.1.2 CARGO-03c.
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
