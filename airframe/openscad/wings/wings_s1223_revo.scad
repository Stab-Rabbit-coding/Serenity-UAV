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
// loft tapers linearly between root and tip.  At 1.25 the tip vertical section
// at the spar station (≈24% chord) grows to ≈ 15.6 mm — the 12.3 mm bore then
// carries ≈ 1.7 mm of section each side.  Tip t/c rises 12.14% → ≈ 15.2%.
// CANON NOTE: this is a small outer-mold-line change local to the wingtip;
// verify against the canonical Serenity wing silhouette before committing to
// print (see TODO.md §1.1.2).  Lower the value only if the bore stays skinned.
THICKNESS_SCALE_TIP = 1.25; // [tip thickness multiplier; root stays THICKNESS_SCALE]

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
SPAR_BORE_STATION =  22.0;  // [mm] chordwise station aft of LE — CONSTANT over the
                            //      span (≈ tip 23.7% / root 17.1% chord; near tip
                            //      max-thickness).  Constant ⇒ bore ∥ leading edge.
                            // The bore-centre thickness height is taken from the
                            // ACTUAL S1223 camber midline at each station's own
                            // chord fraction (midline_frac(), below) — NOT a single
                            // constant — so it stays centred (root breakout fixed).

// ── Harness cableway (Rev R2) ────────────────────────────────────────────────
// The 8 mm rotating spar is hollow (≈ 5 mm ID) — enough for the nav-light 3-core
// (Ø 2.5 mm), which routes THROUGH the hollow spar to the outboard nacelle nav
// light (95° tilt twist is benign — docs/TILT_SPAR_ANALYSIS.md §5), but NOT for
// the 40 A EDF ESC feeds.  This dedicated wing conduit carries those: TWO
// parallel Ø CABLE_BORE_D bores forming a flat "double-D" (overall ≈ 15 × 7 mm),
// tracking a constant chord FRACTION (sweep is immaterial for a flexible
// harness) and camber-centred at each station.  Splitting into two bores keeps
// the EDF power pair separate from ESC signal/telemetry (noise).
CABLE_BORE_D    =   7.0;  // [mm] each conduit bore diameter (Ø7 ≈ 38 mm² each)
CABLE_BORE_SEP  =   8.0;  // [mm] chordwise centre-to-centre (overall ≈ 15 mm wide)
CABLE_BORE_XFR  =   0.48; // [chord fraction] cableway chordwise centre.  Moved aft
                          //      0.40 → 0.48 (Rev R2) so the forward conduit (tip
                          //      chordX ≈ 40.6 mm) clears the Ø26 wingtip mount pad
                          //      (reaches chordX ≈ 35 mm); still well aft of the
                          //      8 mm spar (ends ≈ 26% chord).  The nacelle harness
                          //      entry port must match this station.

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

// Wingtip bearing seat (F688ZZ flanged, 8 ID × 16 OD × 5 W):
TIP_BRG_OD            =  16.0;   // [mm] bearing outer diameter
TIP_BRG_SEAT_D        =  15.95;  // [mm] press-fit seat bore (0.025 mm/side interference)
TIP_BRG_W             =   5.0;   // [mm] bearing width (seat depth)
TIP_BRG_FLANGE_OD     =  18.0;   // [mm] flange OD → shallow counterbore, seats flush
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
TIP_PAD_OD            =  26.0;   // [mm] pad OD (clears 18 mm flange + r=11 bolt circle)
TIP_PAD_PROUD         =   2.0;   // [mm] proud height beyond wing tip face (minimal)

// Spar-axis thickness (internal Y) height at the TIP station — the spar exits on
// the camber midline, NOT the chord line, so all wingtip spar features (pad,
// bearing seat, gear inserts) must share this Y to stay concentric with the
// spar_bore().  Defined as a FUNCTION (not a top-level variable) so it is
// evaluated at module-instantiation time, after the S1223_UPPER/LOWER point
// lists exist — same expression spar_bore() uses for its tip disc.
function spar_tip_y() = midline_frac(SPAR_BORE_STATION / WING_CHORD_TIP)
                        * WING_CHORD_TIP * THICKNESS_SCALE_TIP;

// ── Wing root fuselage tab ────────────────────────────────────────────────────
// The root face (Z=0) must interface with the fuselage wing slot.
// VERIFY slot dimensions in fuselage hull STL before printing.
WING_ROOT_TAB_W =  30.0;  // [mm] VERIFY — fuselage slot width in X
WING_ROOT_TAB_H =  20.0;  // [mm] VERIFY — fuselage slot height in Y
WING_ROOT_TAB_L =  12.0;  // [mm] VERIFY — insertion depth into fuselage slot

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
// Normalised coordinates from UIUC Airfoil Database (Selig & Guglielmo 1997).
// x ∈ [0,1], y = local thickness ratio (positive = upper surface toward sky).
//
// Format: closed polygon, upper surface LE→TE then lower surface TE→LE.
// OpenSCAD polygon() uses counterclockwise winding (positive fill).
//
// Accuracy note: interpolated from published data; matches database to ±0.001
// chord units.  Download s1223.dat from UIUC for production verification:
//   https://m-selig.ae.illinois.edu/ads/coord/s1223.dat
// =============================================================================

// ── Upper surface points (LE x=0 → TE x=1) ───────────────────────────────────
S1223_UPPER = [
    [ 0.0000,  0.0000 ],   // leading edge
    [ 0.0050,  0.0163 ],
    [ 0.0100,  0.0231 ],
    [ 0.0150,  0.0284 ],
    [ 0.0250,  0.0381 ],
    [ 0.0350,  0.0472 ],
    [ 0.0500,  0.0594 ],
    [ 0.0650,  0.0706 ],
    [ 0.0800,  0.0810 ],
    [ 0.1000,  0.0936 ],
    [ 0.1250,  0.1073 ],
    [ 0.1500,  0.1189 ],
    [ 0.1750,  0.1285 ],
    [ 0.2000,  0.1362 ],
    [ 0.2250,  0.1419 ],
    [ 0.2500,  0.1455 ],   // ← approx max thickness station (half-thickness perp. to camber)
    [ 0.2750,  0.1472 ],
    [ 0.3000,  0.1471 ],
    [ 0.3250,  0.1454 ],
    [ 0.3500,  0.1422 ],
    [ 0.3750,  0.1378 ],
    [ 0.4000,  0.1323 ],
    [ 0.4250,  0.1260 ],
    [ 0.4500,  0.1189 ],
    [ 0.5000,  0.1033 ],
    [ 0.5500,  0.0866 ],
    [ 0.6000,  0.0696 ],
    [ 0.6500,  0.0526 ],
    [ 0.7000,  0.0361 ],
    [ 0.7500,  0.0210 ],
    [ 0.8000,  0.0082 ],
    [ 0.8500, -0.0020 ],
    [ 0.9000, -0.0089 ],
    [ 0.9500, -0.0109 ],
    [ 1.0000,  0.0000 ],   // trailing edge
];

// ── Lower surface points (TE x=1 → LE x=0) ───────────────────────────────────
S1223_LOWER = [
    [ 1.0000,  0.0000 ],   // trailing edge
    [ 0.9500,  0.0021 ],
    [ 0.9000,  0.0063 ],
    [ 0.8500,  0.0117 ],
    [ 0.8000,  0.0175 ],
    [ 0.7500,  0.0228 ],
    [ 0.7000,  0.0270 ],
    [ 0.6500,  0.0299 ],
    [ 0.6000,  0.0313 ],
    [ 0.5500,  0.0312 ],
    [ 0.5000,  0.0297 ],
    [ 0.4500,  0.0270 ],
    [ 0.4000,  0.0233 ],
    [ 0.3500,  0.0192 ],
    [ 0.3000,  0.0149 ],
    [ 0.2500,  0.0109 ],
    [ 0.2000,  0.0073 ],
    [ 0.1500,  0.0040 ],
    [ 0.1000,  0.0012 ],
    [ 0.0750, -0.0003 ],
    [ 0.0500, -0.0022 ],
    [ 0.0350, -0.0038 ],
    [ 0.0250, -0.0053 ],
    [ 0.0150, -0.0067 ],
    [ 0.0100, -0.0074 ],
    [ 0.0050, -0.0073 ],
    [ 0.0000,  0.0000 ],   // leading edge (closes polygon)
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
module s1223_section(chord = 65.0, t_scale = THICKNESS_SCALE) {
    // Scale the normalised coordinates:
    //   x → x × chord  (chordwise, unmodified)
    //   y → y × chord  (but THICKNESS_SCALE applies only to the thickness offset,
    //                   not the camber line — approximation: scale all y uniformly)
    // Note: Scaling y uniformly scales both camber and thickness by the same
    // factor, which is a minor approximation acceptable for t_scale in [0.85,1.0].
    scale([chord, chord * t_scale])
        polygon(S1223_POLY);
}


// =============================================================================
// ── Module: wing_solid ────────────────────────────────────────────────────────
// =============================================================================
// Lofted tapered wing solid using hull() of root and tip cross-sections.
// The hull() creates a ruled surface between the two stations, approximating
// the tapered and swept wing.  Valid for taper ratios > 0.4 (Serenity ≈ 0.65).
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

    hull() {
        // ── Root cross-section at Z = 0 ───────────────────────────────────
        // Extruded to 0.01 mm thin disc for hull input
        translate([0, 0, 0])
            linear_extrude(height = 0.01)
                s1223_section(chord = root_chord);

        // ── Tip cross-section at Z = span (swept + tapered + dihedral) ────
        // Leading edge swept aft by WING_SWEEP_LE; tip centred on same LE sweep.
        // Tip uses THICKNESS_SCALE_TIP (local thickening for the spar bore — see
        // parameter block); root uses THICKNESS_SCALE, so the loft tapers between.
        translate([sweep, dihedral, span])
            linear_extrude(height = 0.01)
                s1223_section(chord = tip_chord, t_scale = THICKNESS_SCALE_TIP);
    }
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
    // version fixed).  y = midline(t/c) × local chord × local thickness-scale.
    root_y_ctr = midline_frac(SPAR_BORE_STATION / WING_CHORD_ROOT)
                 * WING_CHORD_ROOT * THICKNESS_SCALE;
    tip_y_ctr  = midline_frac(SPAR_BORE_STATION / WING_CHORD_TIP)
                 * WING_CHORD_TIP  * THICKNESS_SCALE_TIP;

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
// Each conduit tracks a constant chord FRACTION (CABLE_BORE_XFR) and is
// camber-centred at each station via midline_frac().  The two bores are offset
// ±CABLE_BORE_SEP/2 chordwise about that fraction.  Runs full span (root face
// into the fuselage, tip face into the pylon harness channel).
module cableway_bore() {
    // Chordwise conduit centres at root and tip (constant fraction → tapered).
    root_xc = WING_CHORD_ROOT * CABLE_BORE_XFR;
    tip_xc  = WING_CHORD_TIP  * CABLE_BORE_XFR;
    root_yc = midline_frac(CABLE_BORE_XFR) * WING_CHORD_ROOT * THICKNESS_SCALE;
    tip_yc  = midline_frac(CABLE_BORE_XFR) * WING_CHORD_TIP  * THICKNESS_SCALE_TIP;

    for (dx = [-CABLE_BORE_SEP / 2, CABLE_BORE_SEP / 2]) {
        hull() {
            translate([root_xc + dx, root_yc, -1.0])
                cylinder(r = CABLE_BORE_D / 2, h = 0.01);
            translate([tip_xc + dx, tip_yc + WING_DIHEDRAL, WING_SEMI_SPAN + 1.0])
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

    // Low cylindrical pad, proud of the tip face by TIP_PAD_PROUD only.
    translate([spar_x, spar_y, spar_z])
        cylinder(r = TIP_PAD_OD / 2,
                 h = TIP_PAD_PROUD,
                 $fn = 48);
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
// printing.  The tab provides radial restraint; the CF spar carries spanwise load.
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

        // ── Harness cableway (2× Ø7 conduits for EDF power + signal) ──────
        cableway_bore();
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
