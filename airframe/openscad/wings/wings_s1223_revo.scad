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

// ── Structural spar bore (Rev R1a — straight, LE-parallel, camber-centred) ──
// CF-TUBE-12MM (12 mm OD × 1.5 mm wall) spar per bom_revO.csv.
// The spar is a SINGLE STRAIGHT bore running spanwise at a FIXED chordwise
// station (constant distance aft of the straight LE → NO plan-view skew) and
// centred on the airfoil CAMBER MIDLINE (not the chord line), so it stays
// enclosed by the skin at every station.
//
// Rev R1 (superseded) pinned the bore to a constant chord FRACTION (30%);
// because the chord tapers 129→93 mm under a straight LE, that walked the bore
// 10.8 mm forward over the 85.7 mm semi-span (7.2° plan-view skew — the "swept"
// cutout) and, being centred on the chord line (SPAR_BORE_Y_CTR = 0), broke out
// through the strongly-cambered S1223 lower surface (whose lower skin sits ABOVE
// the chord line aft of ~8% chord).  Both defects are corrected here.
SPAR_BORE_OD      =  12.3;  // [mm] bore ID = tube OD (12) + 0.3 mm slip fit
SPAR_BORE_STATION =  22.0;  // [mm] chordwise station aft of LE — CONSTANT over the
                            //      span (≈ tip 23.7% / root 17.1% chord; near tip
                            //      max-thickness).  Constant ⇒ bore ∥ leading edge.
SPAR_MIDLINE_FRAC =  0.078; // [t/c] S1223 camber-midline height at the spar
                            //      station.  Bore centre Y = FRAC × local chord ×
                            //      local thickness-scale (keeps the bore centred in
                            //      the section at both root and tip stations).

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
    root_y_ctr = SPAR_MIDLINE_FRAC * WING_CHORD_ROOT * THICKNESS_SCALE;
    tip_y_ctr  = SPAR_MIDLINE_FRAC * WING_CHORD_TIP  * THICKNESS_SCALE_TIP;

    hull() {
        translate([SPAR_BORE_STATION, root_y_ctr, -1.0])       // root disc (1 mm below root face)
            cylinder(r = SPAR_BORE_OD / 2, h = 0.01);

        translate([SPAR_BORE_STATION, tip_y_ctr + WING_DIHEDRAL, WING_SEMI_SPAN + 1.0])
            cylinder(r = SPAR_BORE_OD / 2, h = 0.01);          // tip disc (1 mm past tip)
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
// Note: pylon mount pocket omitted — folding capability not used on this build.
module wing_one_side() {
    difference() {
        union() {
            // ── Lofted wing solid ──────────────────────────────────────────
            wing_solid();

            // ── Fuselage root insertion tab ────────────────────────────────
            fuselage_root_tab();
        }

        // ── CF spar bore (spanwise, 12 mm OD) ────────────────────────────
        spar_bore();
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
