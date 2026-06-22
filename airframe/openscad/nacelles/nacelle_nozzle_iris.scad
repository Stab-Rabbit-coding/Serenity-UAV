// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Hull frame (canonical for ALL design artifacts): X = +port (left),
//   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
//   world origin.  Primary-component STLs published to airframe/stls/
//   are stored directly in hull frame, baked by tools/bake_hull_frame.py
//   (marker 'SerenityUAV HULL-FRAME R1' in the binary STL header).
//   NEVER re-bake a mesh derived from an already-baked file.
//   This file:
//     Part-local print frame, coaxial with the nacelle duct (duct axis =
//     local +Z, intake at Z = 0).  Hull placement derives from the nacelle
//     pose (cruise = 270 deg about +X + translation; hover rotates about the
//     tilt pivot at duct Z = 83 mm).  Assembly placement VERIFY pending
//     (serenity_assembly.py).
// ===========================================================================
// nacelle_nozzle_iris.scad
// Serenity UAV Rev R2 — Nacelle Variable Nozzle, Overlapping Flap Design
// (50 mm EDF bore)
//
// REV R2 REDESIGN (2026-06-22): replaces the Rev R1 camera-iris mechanism
// (8 flat trapezoidal petals hinged on pins PARALLEL to the duct axis,
// rotating in a plane perpendicular to the flow — i.e. a true photographic
// iris diaphragm) per explicit user direction: "the nacelle nozzles need
// provide a smooth variable diameter conical exit for the thrust tube, that
// minimizes airstream turbulence, not an abrupt iris like a camera."
//
// Mechanism chosen (of three options presented to the user; this one
// selected): OVERLAPPING CURVED FLAPS, the same general topology real
// variable-area jet-engine nozzles use (e.g. convergent flap rings on
// afterburning turbofans) — each flap is hinged on a TANGENTIAL
// (circumferential) pin at the fixed throat, and extends AXIALLY downstream
// rather than sitting in a flat radial plane.  Pivoting the flap about its
// tangential hinge sweeps its trailing edge through a small range of cone
// half-angles, so the assembled ring of 8 flaps presents a continuous,
// gently-tapering CONICAL surface at every position — never a flat faceted
// diaphragm.  The existing Rev R1 gear train (Crown Pinion -> Idler ->
// Ring gear, nacelle_nozzle_idler.scad / nacelle_pinion.scad) is reused
// UNCHANGED — only how the ring's rotation couples to the flaps changes
// (a spiral cam slot replaces the old radial piano-wire drive posts).
//
// ── Why a tangential hinge, not the old axial hinge ──────────────────────
//   Old (Rev R1): hinge pins parallel to the duct axis (local Z) -> each
//   petal swings IN a plane perpendicular to flow -> the assembled ring is a
//   flat disc with a polygonal opening (classic camera iris).  Flow sees a
//   sharp 90 deg facet at the duct exit at every position except fully open.
//   New (Rev R2): hinge pins tangential (circumferential) at the throat rim
//   -> each flap pivots so its TRAILING edge moves both inward/outward
//   (radially) AND fore/aft (axially) together -> the flap surface stays
//   close to parallel with the local flow at every position.  This is
//   exactly the kinematic difference between a camera iris and a real
//   variable-area nozzle flap ring.
//
// ── Flap pivot kinematics ──────────────────────────────────────────────────
//   Flap hinge circle radius R_HINGE = THROAT_OUTER_R = 27.5 mm (right at
//   the throat tube's OD — see THROAT geometry below).  Flap axial length
//   FLAP_LENGTH = 20 mm, hinge to trailing edge.  Trailing-edge exit radius
//   as a function of flap swing angle phi (phi = 0 -> flap parallel to duct
//   axis, flush extension of the throat tube; phi > 0 -> flap swings
//   inward/downstream, converging):
//     exit_r(phi) = R_HINGE - FLAP_LENGTH * sin(phi)
//   Solving for the two bore-percentage targets (CLAUDE.md: 75 % of the
//   25 mm bore radius at 0 deg/cruise tilt, 105 % at 90 deg/hover tilt):
//     phi_closed = asin((R_HINGE - NOZZLE_CLOSED_R) / FLAP_LENGTH)
//                = asin((27.5 - 18.75) / 20) = asin(0.4375)  = 25.94 deg
//     phi_open   = asin((R_HINGE - NOZZLE_OPEN_R)   / FLAP_LENGTH)
//                = asin((27.5 - 26.25) / 20) = asin(0.0625)  =  3.58 deg
//   Both angles are POSITIVE (always at least slightly converging from the
//   throat) — there is no sign change to handle, unlike an earlier draft of
//   this derivation that put the hinge at the bore radius itself.  Both
//   angles are gentle (< 26 deg) — the flap is never more than ~26 deg off
//   the local flow direction, the actual "smooth, low-turbulence" goal.
//
// ── Actuation: spiral-cam unison disc (replaces piano-wire drive posts) ───
//   A tangential-hinge flap needs an AXIAL force at a RADIALLY-offset point
//   to produce torque about its hinge (d x F about the tangential axis t-hat
//   requires d along r-hat and F along z-hat, or vice versa) — a simple
//   in-plane wire pull (as Rev R1 used) cannot do this.  Two real options:
//   (a) an axially-translating unison ring (real turbofans use this, via a
//   screwjack/cam), or (b) keep the ring ROTATING ONLY (reuse the Rev R1
//   gear train exactly as-is) and convert rotation to flap motion via a
//   SPIRAL CAM SLOT cut into the ring's face, engaged by a follower pin on
//   each flap.  (b) is simpler — no new linear actuator, no helical thread
//   on the housing bore — and is what this file implements.
//
//   Each flap carries a compound lever tab from its hinge: tab tip offset
//   (TAB_X radially outward, TAB_Z axially upstream) from the hinge line.
//   Rotating the flap by phi about its tangential hinge moves the tab tip
//   (and the small follower pin at its end) to:
//     pin_r(phi) = R_HINGE + TAB_X * cos(phi) - TAB_Z * sin(phi)
//     pin_z(phi) = HINGE_Z - TAB_X * sin(phi) - TAB_Z * cos(phi)
//   TAB_X and TAB_Z are solved (see TAB_X/TAB_Z derivation below) so that
//   pin_r stays comfortably OUTSIDE the throat tube's OD across the full
//   phi range — this is what makes the unison ring's bore able to clear the
//   throat tube while its face-cam slot still reaches the follower pins.
//
//   The ring's spiral cam slot maps ring rotation angle theta_ring (the
//   SAME theta_ring already derived for the Rev R1 gear train: Stage 1
//   sector/Pinion-A epicyclic x4.667, Stage 2 Crown-Pinion-to-ring-gear
//   x0.056818 via the idler — see nacelle_nozzle_idler.scad) linearly to
//   pin_r:
//     pin_r(theta_ring) = PIN_R_REF_CLOSED
//                        + (PIN_R_REF_OPEN - PIN_R_REF_CLOSED)
//                          * theta_ring / THETA_RING_REF_OPEN
//   calibrated at the two REFERENCE points (theta_ring = 0 at 0 deg/cruise
//   tilt -> closed; theta_ring = 23.86 deg at 90 deg/hover tilt -> open —
//   both unchanged from the Rev R1 gear-ratio derivation).  The slot is cut
//   slightly beyond the full -5 deg/140 deg hard-stop range
//   (SPIRAL_ANG_LO/HI below) so the follower pin never rides off either end.
//
// ── Overlap (the "not an abrupt iris" requirement) ────────────────────────
//   FLAP_SPAN_DEG = 50 deg per flap x 8 flaps = 400 deg > 360 deg, i.e. each
//   flap overlaps its neighbour by 5 deg of arc at every swing position
//   (carried forward from the Rev R1 petal spacing — tangential-hinge
//   rotation barely changes a flap's angular width for these gentle angles,
//   so the same overlap margin still holds).  Flaps are shingled (alternate
//   flap printed/assembled on top at each seam) so the OUTER, flow-facing
//   surface stays continuous at every position — there is no facet gap to
//   open up, unlike the old iris where opening the petals opened gaps.
//
// Three separately-printable parts, each in its own module:
//   1. nozzle_throat_and_housing() — fixed: throat tube (flow liner) +
//      outer shell (carries the ring + idler-access slot) + 8 tangential
//      hinge bosses + connecting ribs.
//   2. unison_ring()               — rotating: same 72T M=1.0 gear as
//      Rev R1 (meshes nacelle_nozzle_idler.scad Idler-Out, UNCHANGED), plus
//      8 spiral cam slots on its downstream face.
//   3. nozzle_flap()                — one flap (print x 8): tangential
//      hinge knuckle (clevis) + compound lever tab + follower pin.
//
// Mating interfaces (gear train, unchanged from Rev R1):
//   Idler-Out gear (nacelle_nozzle_idler.scad): module M = 1.0, meshes this
//   ring's 72-tooth gear at pitch R = 36 mm, through IDLER_SLOT in the
//   outer housing wall.
//   Nacelle exit face (hull): housing lip bonds to EDF exit duct face.
//   Hinge pins: 3 mm x 18 mm stainless steel dowel pins (x8), TANGENTIAL
//     orientation (Rev R2 change from axial).
//   Follower pins: 2 mm x 4 mm stainless steel dowel pins (x8), riding in
//     the ring's spiral cam slots — NEW (replaces the Rev R1 piano-wire
//     link ring entirely; no wire/drive-post hardware in this revision).
//
// Print specification — Throat-and-Housing:
//   Material:    CF-PETG (structural, bonded to nacelle)
//   Layers:      0.15 mm, 4 perimeters, 40 % gyroid infill
//   Orient:      Print with bonding lip face down
//
// Print specification — Unison Ring:
//   Material:    CF-PETG (ring gear teeth + cam slot walls carry load)
//   Layers:      0.15 mm, 4 perimeters, 40 % gyroid infill
//   Orient:      Print flat (gear face down) for tooth quality
//   Nozzle:      Hardened steel
//
// Print specification — Flaps:
//   Material:    PETG (non-structural aerodynamic surface; slight flex OK)
//   Layers:      0.15 mm, 3 perimeters, 25 % gyroid infill
//   Orient:      Print flat (concave/flow face down)
//   Color note:  Flow-facing (concave) face marked "TRANSLUCENT-BLUE" — use
//                translucent blue PETG filament for visual airflow
//                reference.  Convex (outer) face matches nacelle hull
//                finish (titanium grey).
//
// VERIFY (first-pass mechanical concept, not yet prototyped):
//   - TAB_X/TAB_Z and the spiral-slot radii are derived analytically from
//     the stated kinematics; confirm follower-pin travel and ring-bore
//     clearance against printed parts before relying on this geometry.
//   - The 3 connecting ribs between throat tube and outer shell (in
//     nozzle_throat_and_housing()) are a first-pass structural bridge —
//     verify they clear the idler-access slot and all 8 flap hinge/cam
//     paths in the slicer.
//
// Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// License: CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date:    2026-05-24
// Rev:     R (2026-06-11): Rev R baseline — no geometry changes (carried forward from Rev O initial release).
// Rev:     R1 (2026-06-22): Resolved TODO.md §1.1.3.3 Crown-Pinion-to-rack
//          radius inconsistency by adding an idler gear
//          (nacelle_nozzle_idler.scad) between the Crown Pinion and this
//          ring.  Replaced the partial inner-face rack (RACK_TEETH = 22,
//          RACK_PITCH_R = 26 mm) with a full-circle external spur gear on
//          the ring's outer rim (72 T, R = 36 mm) meshed by the idler.
// Rev:     R2 (2026-06-22): Full mechanism redesign — replaced the camera-
//          iris flat-petal diaphragm with overlapping tangential-hinge
//          flaps forming a smooth conical exit, per explicit user direction
//          (see header above).  Gear train (72T ring gear, idler mesh)
//          carried forward UNCHANGED from Rev R1.

// ── Resolution ────────────────────────────────────────────────────────────────

$fn = 72;   // standard circle resolution (all rotational bodies)

// ── Polygon Helpers ───────────────────────────────────────────────────────────
//
// arc_pts(r, a1, a2, n) — n+1 points along an arc at radius r from a1 to a2.
//   Returns a list of [x, y] vectors usable in polygon().
//
function arc_pts(r, a1, a2, n) =
    [for (i = [0 : n]) let(a = a1 + i * (a2 - a1) / n) [r * cos(a), r * sin(a)]];

// annular_wedge(r_in, r_out, a1, a2, n) — closed annular-sector polygon.
//   Using polygon() for ring-gear tooth spaces avoids nested 2D CSG
//   (circle−circle−square²) which causes CGAL exponential blowup above
//   ~20 iterations (see nacelle_sector_gear.scad); the ring gear has 72.
//   n = arc-segment count per edge; inner/outer arcs wound for correct face normal.
//
function annular_wedge(r_in, r_out, a1, a2, n) =
    concat(arc_pts(r_in,  a1, a2, n),
            arc_pts(r_out, a2, a1, n));

// spiral_pts(r1, r2, a1, a2, half_w, n) — closed polygon tracing a thin
//   slot along a linear r-vs-angle spiral from (r1,a1) to (r2,a2), offset
//   by +-half_w in the RADIAL direction (a simplifying approximation —
//   exact for a constant-radius arc, slightly inexact for a spiral, but
//   negligible distortion for the gentle ~0.17 mm/deg lead used here).
//
function spiral_pts(r1, r2, a1, a2, half_w, n) =
    concat(
        [for (i = [0 : n]) let(t = i / n, r = r1 + (r2 - r1) * t - half_w, a = a1 + (a2 - a1) * t)
            [r * cos(a), r * sin(a)]],
        [for (i = [n : -1 : 0]) let(t = i / n, r = r1 + (r2 - r1) * t + half_w, a = a1 + (a2 - a1) * t)
            [r * cos(a), r * sin(a)]]
    );

// ── Core Bore / Bore-Percentage Targets ───────────────────────────────────────

BORE_R           = 25.0;   // [mm] 50 mm EDF bore radius (airflow passage centre) —
                            //   fixed by the 50 mm EDF spec (CLAUDE.md); unchanged.
NOZZLE_CLOSED_R  = 18.75;   // [mm] nozzle exit radius at 0 deg tilt  = 75 % of BORE_R
NOZZLE_OPEN_R    = 26.25;   // [mm] nozzle exit radius at 90 deg tilt = 105 % of BORE_R

// ── Throat Tube (fixed flow liner — carries the hinge ring) ──────────────────

THROAT_WALL      =  2.5;   // [mm] liner wall thickness (matches CF-PETG min wall)
THROAT_INNER_R   = BORE_R;             // [mm] = 25.0, flush continuation of the EDF bore
THROAT_OUTER_R   = BORE_R + THROAT_WALL; // [mm] = 27.5
THROAT_LEN       = 15.0;   // [mm] axial length, inboard face (Z=0) to hinge line

// ── Flap Pivot Geometry ────────────────────────────────────────────────────────

R_HINGE      = THROAT_OUTER_R;   // [mm] = 27.5, tangential hinge circle radius
FLAP_LENGTH  = 20.0;             // [mm] hinge to trailing edge, axial-ish length
HINGE_Z      = THROAT_LEN;       // [mm] = 15.0, hinge line Z station

// phi(exit_r) = asin((R_HINGE - exit_r) / FLAP_LENGTH) — see header derivation.
PHI_CLOSED = asin((R_HINGE - NOZZLE_CLOSED_R) / FLAP_LENGTH);   // = 25.94 deg
PHI_OPEN   = asin((R_HINGE - NOZZLE_OPEN_R)   / FLAP_LENGTH);   // =  3.58 deg

// ── Lever Tab / Follower Pin (drives the flap from the ring's spiral cam) ────
//
// TAB_X (radial outward offset) and TAB_Z (axial upstream offset) of the
// follower-pin tip from the hinge, solved so the follower pin's radius
// pin_r(phi) stays >= PIN_R_REF_CLOSED across the full operating range
// (clearing THROAT_OUTER_R with margin, so the ring's bore can clear the
// throat tube while the spiral slot still reaches the pin) while spanning
// a PIN_R_REF_OPEN - PIN_R_REF_CLOSED range usable by the cam:
//   pin_r(phi) = R_HINGE + TAB_X*cos(phi) - TAB_Z*sin(phi)
// Solved for pin_r(PHI_OPEN) = PIN_R_REF_OPEN, pin_r(PHI_CLOSED) = PIN_R_REF_CLOSED:
PIN_R_REF_CLOSED = 31.0;   // [mm] follower-pin radius at theta_ring = 0 (closed)
PIN_R_REF_OPEN   = 35.0;   // [mm] follower-pin radius at theta_ring = 23.86 deg (open)

TAB_Z = ((R_HINGE - PIN_R_REF_OPEN) - (R_HINGE - PIN_R_REF_CLOSED) * cos(PHI_OPEN) / cos(PHI_CLOSED))
        / (sin(PHI_CLOSED) * cos(PHI_OPEN) / cos(PHI_CLOSED) - sin(PHI_OPEN));
                            // [mm] =~ 8.5, axial (upstream) component of the lever tab
TAB_X = (R_HINGE - PIN_R_REF_CLOSED + TAB_Z * sin(PHI_CLOSED)) / cos(PHI_CLOSED);
                            // [mm] =~ 8.1, radial (outward) component of the lever tab

FOLLOWER_PIN_D   = 2.0;    // [mm] follower pin OD (SS dowel)
FOLLOWER_PIN_L   = 4.0;    // [mm] follower pin length (engages the ring's slot pocket)

// pin position as a function of swing angle phi (used for BOTH the flap's
// own pin placement and, via the theta_ring mapping below, the ring's
// spiral slot — single source of truth, see header).
function flap_pin_r(phi) = R_HINGE + TAB_X * cos(phi) - TAB_Z * sin(phi);
function flap_pin_z(phi) = HINGE_Z - TAB_X * sin(phi) - TAB_Z * cos(phi);

// ── Ring Rotation <-> Pin Radius Mapping ──────────────────────────────────────
//
// theta_ring reference points carried forward UNCHANGED from the Rev R1
// gear-train derivation (Stage 1 sector/Pinion-A epicyclic x4.667, Stage 2
// Crown-Pinion-to-idler-to-ring x0.056818 — see nacelle_nozzle_idler.scad):
//   0 deg nacelle tilt (cruise)  -> theta_ring =  0.00 deg -> closed
//   90 deg nacelle tilt (hover)  -> theta_ring = 23.86 deg -> open
//   -5 deg / 140 deg hard stops  -> theta_ring = -1.33 / 38.45 deg
THETA_RING_REF_OPEN = 23.86;   // [deg]
SPIRAL_MARGIN_DEG   =  5.0;    // [deg] extra arc past each hard stop, both ends
SPIRAL_ANG_LO = -1.33 - SPIRAL_MARGIN_DEG;   // [deg] =  -6.33
SPIRAL_ANG_HI = 38.45 + SPIRAL_MARGIN_DEG;   // [deg] =  43.45

function pin_r_at_theta(theta_ring) =
    PIN_R_REF_CLOSED + (PIN_R_REF_OPEN - PIN_R_REF_CLOSED) * theta_ring / THETA_RING_REF_OPEN;

SPIRAL_R_LO = pin_r_at_theta(SPIRAL_ANG_LO);   // [mm] follower-pin radius at the slot's closed end
SPIRAL_R_HI = pin_r_at_theta(SPIRAL_ANG_HI);   // [mm] follower-pin radius at the slot's open end
SPIRAL_SLOT_W = FOLLOWER_PIN_D + 0.4;          // [mm] slot width, 0.2 mm/side clearance
SPIRAL_SLOT_DEPTH = 3.0;                       // [mm] pocket depth cut into ring face

// ── Flap Geometry ──────────────────────────────────────────────────────────────

N_FLAPS         =  8;       // [count] number of nozzle flaps
FLAP_SPAN_DEG   = 50.0;     // [deg] angular span per flap (45 deg + 5 deg overlap)
FLAP_THICKNESS  =  2.5;     // [mm] flap shell thickness
HINGE_PIN_D     =  3.0;     // [mm] stainless steel hinge pin OD (tangential)
HINGE_BORE_D    =  3.2;     // [mm] clearance bore for 3 mm hinge pin (0.2 mm clr)
HINGE_KNUCKLE_W =  6.0;     // [mm] width (tangential) of each hinge knuckle half

// ── Ring (Unison Disc) Dimensions — gear spec UNCHANGED from Rev R1 ──────────

RING_INNER_R  = THROAT_OUTER_R + 1.0;   // [mm] = 28.5, clears the throat tube OD
RING_GEAR_PITCH_R = 36.0;   // [mm] pitch radius of the full-circle gear (UNCHANGED —
                            //   meshes Idler-Out R=7.5mm, nacelle_nozzle_idler.scad)
RING_H        =  8.0;       // [mm] axial height — matches GEAR_H_OUT in
                            //   nacelle_nozzle_idler.scad

RING_GEAR_MODULE   = 1.0;    // [mm] Module — matches Idler-Out and Crown Pinion (UNCHANGED)
RING_GEAR_ADDENDUM = RING_GEAR_MODULE;          // [mm] = 1.0
RING_GEAR_DEDENDUM = 1.25 * RING_GEAR_MODULE;   // [mm] = 1.25
RING_OUTER_R  = RING_GEAR_PITCH_R + RING_GEAR_ADDENDUM;     // [mm] = 37.0 (tip)
RING_GEAR_ROOT_R = RING_GEAR_PITCH_R - RING_GEAR_DEDENDUM;  // [mm] = 34.75

N_RING_TEETH = round(2 * RING_GEAR_PITCH_R / RING_GEAR_MODULE);  // [count] = 72
RING_GEAR_ANGULAR_PITCH = 360.0 / N_RING_TEETH;   // [deg] = 5.0 deg per tooth

// ── Outer Housing Dimensions ──────────────────────────────────────────────────

HOUSING_OUTER_R =  41.0;   // [mm] housing outer radius (OD = 82 mm) — UNCHANGED envelope
HOUSING_INNER_R =  37.5;   // [mm] housing inner bore radius (ring fits inside;
                            //   ring OD = 74 mm, bore = 75 mm -> 0.5 mm clr)
HOUSING_LIP_H   =   3.0;   // [mm] forward bonding lip depth (bonds to nacelle
                            //   exit face; lip OD matches EDF duct exit OD)

// Idler-access slot in housing wall (UNCHANGED position/sizing from Rev R1 —
// the idler still meshes this ring's gear exactly as before):
IDLER_SLOT_W    =  10.0;   // [mm] slot width (circumferential)
IDLER_SLOT_H    =   6.0;   // [mm] slot radial depth, added to wall thickness
IDLER_SLOT_ANG  =  50.9;   // [deg] angular position of slot, measured from this
                            //   part's local +X axis (TODO.md §1.1.3.3, resolved
                            //   2026-06-22).  Solved from the two simultaneous
                            //   centre-distance constraints in
                            //   nacelle_nozzle_idler.scad — Crown Pinion sits at
                            //   local (X=0, Y=28) (PINION_A_Y, nacelle_pod_50mm_
                            //   tandem.scad), and the idler shaft must be 28.1 mm
                            //   from that point AND 43.6 mm from this ring's axis
                            //   (0,0).  Solving the two circle equations gives
                            //   shaft position (X=+27.485, Y=33.846), i.e. 50.92°
                            //   from +X (rounded to 50.9°).  This is one of the
                            //   two valid mirror-image solutions (the other is
                            //   129.08° at X=-27.485); +X was chosen arbitrarily
                            //   — no other component occupies this angular sector
                            //   at this Z station.

// Connecting ribs (throat tube <-> outer shell, structural bridge — VERIFY,
// first-pass concept, see header):
RIB_W    =  4.0;    // [mm] tangential width of each rib
RIB_N    =  3;       // [count] number of ribs
RIB_ANG_OFFSET = 22.5;   // [deg] angular offset from flap centrelines (avoids
                          //   blocking any flap's hinge/cam path)

// ── Module: nozzle_throat_and_housing() ───────────────────────────────────────
//
// Fixed assembly, printed as one part:
//   - Throat tube: ID = 2*BORE_R = 50 mm (flush continuation of the EDF
//     bore), OD = 2*THROAT_OUTER_R = 55 mm, Z = 0..THROAT_LEN.
//   - 8 tangential hinge bosses at Z = HINGE_Z, radius R_HINGE, spaced
//     360/N_FLAPS apart — each a central lug with a tangential through-bore
//     for the 3 mm hinge pin (flap clevis straddles it, see nozzle_flap()).
//   - Outer shell: OD = 2*HOUSING_OUTER_R = 82 mm, bore = 2*HOUSING_INNER_R
//     = 75 mm (unison ring rides inside), Z = 0..THROAT_LEN, with the
//     Rev R1 bonding lip at the inboard face and the idler-access slot.
//   - RIB_N ribs bridging throat-tube OD to outer-shell bore at a single
//     axial station, offset from the flap centrelines.
//
//   Origin: centre of inboard (nacelle-side) face, Z = 0.
module nozzle_throat_and_housing() {
    union() {
        difference() {
            union() {
                // ── Outer shell main body ────────────────────────────────────────
                cylinder(h = THROAT_LEN, r = HOUSING_OUTER_R);

                // Inboard bonding lip: shoulder against nacelle exit face
                translate([0, 0, -HOUSING_LIP_H])
                    difference() {
                        cylinder(h = HOUSING_LIP_H, r = HOUSING_OUTER_R);
                        cylinder(h = HOUSING_LIP_H + 0.1, r = THROAT_OUTER_R);
                    }

                // ── Throat tube ────────────────────────────────────────────────
                cylinder(h = THROAT_LEN, r = THROAT_OUTER_R);

                // ── Connecting ribs ──────────────────────────────────────────────
                for (i = [0 : RIB_N - 1]) {
                    rotate([0, 0, i * 360 / RIB_N + RIB_ANG_OFFSET])
                        translate([THROAT_OUTER_R - 0.1, -RIB_W / 2, 0])
                            cube([HOUSING_INNER_R - THROAT_OUTER_R + 0.2, RIB_W, THROAT_LEN]);
                }

                // ── Tangential hinge bosses (central lug, ×8) ────────────────────
                for (i = [0 : N_FLAPS - 1]) {
                    rotate([0, 0, i * 360 / N_FLAPS]) {
                        translate([R_HINGE, 0, HINGE_Z])
                            rotate([90, 0, 0])
                                cylinder(h = HINGE_KNUCKLE_W, d = HINGE_BORE_D + 5.0, center = true);
                    }
                }
            }

            // ── Throat bore — full length, flush with EDF bore ─────────────────
            translate([0, 0, -0.1])
                cylinder(h = THROAT_LEN + 0.2, r = THROAT_INNER_R);

            // ── Unison ring bore — clears RING_OUTER_R inside the outer shell ──
            translate([0, 0, -HOUSING_LIP_H - 0.1])
                cylinder(h = THROAT_LEN + HOUSING_LIP_H + 0.2, r = HOUSING_INNER_R);

            // ── Idler-access slot ────────────────────────────────────────────────
            rotate([0, 0, IDLER_SLOT_ANG]) {
                translate([HOUSING_INNER_R, -IDLER_SLOT_W / 2, THROAT_LEN * 0.2])
                    cube([IDLER_SLOT_H + (HOUSING_OUTER_R - HOUSING_INNER_R) + 0.1,
                            IDLER_SLOT_W,
                            THROAT_LEN * 0.6]);
            }

            // ── Hinge pin through-bores (tangential, ×8) ─────────────────────────
            for (i = [0 : N_FLAPS - 1]) {
                rotate([0, 0, i * 360 / N_FLAPS]) {
                    translate([R_HINGE, 0, HINGE_Z])
                        rotate([90, 0, 0])
                            cylinder(h = HINGE_KNUCKLE_W + 0.2, d = HINGE_BORE_D, center = true);
                }
            }
        }
    }
}

// ── Module: unison_ring() ─────────────────────────────────────────────────────
//
// Rotating unison disc — SAME 72-tooth M=1.0 gear as Rev R1 (meshes
// Idler-Out, nacelle_nozzle_idler.scad, UNCHANGED ratio/positioning), plus
// N_FLAPS spiral cam slots cut into its downstream (outboard) face.  Each
// flap's follower pin rides in one slot; ring rotation (driven by the gear
// train exactly as Rev R1) sweeps the slot's local radius under the pin,
// which (via the flap's lever tab) rotates the flap about its tangential
// hinge — see header for the full kinematic derivation.
//
//   Origin: centre of inboard face, Z = 0; outboard (slotted) face at
//   Z = RING_H.
module unison_ring() {
    difference() {
        // ── Base ring body (gear blank, tip radius OD) ──────────────────────
        cylinder(h = RING_H, r = RING_OUTER_R);

        // Inner bore — clears the throat tube
        translate([0, 0, -0.1])
            cylinder(h = RING_H + 0.2, r = RING_INNER_R);

        // ── Ring gear tooth spaces, full circle (UNCHANGED from Rev R1) ──────
        for (i = [0 : N_RING_TEETH - 1]) {
            _ring_gear_tooth_space(i);
        }

        // ── Spiral cam slots (×N_FLAPS) ──────────────────────────────────────
        for (i = [0 : N_FLAPS - 1]) {
            rotate([0, 0, i * 360 / N_FLAPS]) {
                translate([0, 0, RING_H - SPIRAL_SLOT_DEPTH])
                    linear_extrude(height = SPIRAL_SLOT_DEPTH + 0.1)
                        polygon(spiral_pts(SPIRAL_R_LO, SPIRAL_R_HI,
                                            SPIRAL_ANG_LO, SPIRAL_ANG_HI,
                                            SPIRAL_SLOT_W / 2, 24));
            }
        }
    }
}

// _ring_gear_tooth_space(i) — one tooth-space void on the ring's outer rim.
//   Standard external spur gear tooth-space subtraction, full circle.
//   Built as a polygon (annular_wedge) — avoids nested 2D CSG that caused
//   CGAL to time out at high tooth counts (see header).  UNCHANGED from
//   Rev R1.
//
//   Arguments:
//     i — tooth-space index (0-based, 0 through N_RING_TEETH - 1)
module _ring_gear_tooth_space(i) {
    space_centre = i * RING_GEAR_ANGULAR_PITCH + RING_GEAR_ANGULAR_PITCH / 2;
    half_ang     = RING_GEAR_ANGULAR_PITCH / 4;   // quarter pitch = half tooth space

    linear_extrude(height = RING_H + 0.2) {
        polygon(annular_wedge(
            RING_GEAR_ROOT_R - 0.1, RING_OUTER_R + 0.1,
            space_centre - half_ang, space_centre + half_ang,
            2   // 2 segments per arc edge (5 deg pitch — arc =~ straight line)
        ));
    }
}

// ── Module: nozzle_flap() ──────────────────────────────────────────────────────
//
// One nozzle flap (print x 8):
//   Curved channel-section panel, constant cross-section along its length
//   (an annular-sector slice of the throat tube's own curvature — i.e. at
//   phi = 0 the flap is a seamless extension of the throat tube; tilting it
//   by phi sweeps a gentle cone, never a flat facet).
//   Tangential hinge clevis at the root (straddles the housing's central
//   hinge boss — see nozzle_throat_and_housing()).
//   Compound lever tab + follower pin at the root, engaging the ring's
//   spiral cam slot (see header derivation for TAB_X/TAB_Z).
//
//   Local frame (flap REST pose, phi = 0): origin at the hinge line
//   (local Y = tangential/hinge axis); local +Z = flap length direction
//   (matches global +Z at phi = 0); local +X = radially outward.  The
//   bore-axis reference point (for the curved cross-section) sits at local
//   (X, Y) = (-R_HINGE, 0).  Assembly applies rotate([0,0,i*360/N_FLAPS])
//   then rotate([0, phi, 0]) per flap (about local Y, the tangential hinge)
//   — see assembly preview below.
module nozzle_flap() {
    // ── Main flap body — curved channel, constant section, extruded along
    //    local Z by FLAP_LENGTH (see header: same curved-sector technique
    //    Rev R1 used, just extruded along the flap's length instead of its
    //    thickness).  The sector's own centre (the bore-axis reference
    //    point) sits at local (X,Y) = (-R_HINGE, 0), so its OUTER edge
    //    (radius R_HINGE) passes exactly through the local origin — that is
    //    where the hinge line sits.  Built with annular_wedge() (defined
    //    above) rather than a circle/square mask, for an unambiguous wedge.
    linear_extrude(height = FLAP_LENGTH) {
        translate([-R_HINGE, 0]) {
            polygon(annular_wedge(
                R_HINGE - FLAP_THICKNESS, R_HINGE,
                -FLAP_SPAN_DEG / 2, FLAP_SPAN_DEG / 2,
                12
            ));
        }
    }

    // ── Hinge clevis (two knuckle halves flanking the housing's central
    //    boss, 0.2 mm clearance each side — see nozzle_throat_and_housing()'s
    //    boss, which is HINGE_KNUCKLE_W wide and centred on Y = 0).  Bore
    //    axis is tangential (local Y, matching the housing boss's own
    //    rotate([90,0,0]) pattern) — NOT the cylinder default of Z. ────────
    CLEVIS_LOBE_T = HINGE_KNUCKLE_W / 2;
    for (s = [-1, 1]) {
        translate([0, s * (HINGE_KNUCKLE_W / 2 + 0.2 + CLEVIS_LOBE_T / 2), 0])
            rotate([90, 0, 0])
                difference() {
                    cylinder(h = CLEVIS_LOBE_T, d = HINGE_BORE_D + 4.0, center = true);
                    cylinder(h = CLEVIS_LOBE_T + 0.2, d = HINGE_BORE_D, center = true);
                }
    }

    // ── Compound lever tab + follower pin ───────────────────────────────────
    // Tab tip at local (TAB_X, 0, -TAB_Z) relative to the hinge (i.e. radially
    // outward and axially upstream) — matches flap_pin_r(0)/flap_pin_z(0)
    // measured from the hinge.  A short stub pin projects further upstream
    // (local -Z) from the tip to engage the ring's spiral slot pocket.
    hull() {
        translate([0, 0, 0])
            cylinder(h = 0.1, d = HINGE_KNUCKLE_W);
        translate([TAB_X, 0, -TAB_Z])
            cylinder(h = 0.1, d = HINGE_KNUCKLE_W * 0.6);
    }
    translate([TAB_X, 0, -TAB_Z])
        cylinder(h = FOLLOWER_PIN_L, d = FOLLOWER_PIN_D, center = false);
}

// ── Fit Confirmation ──────────────────────────────────────────────────────────
//
//   Interface                  Mating part                   Clearance / fit
//   ─────────────────────────  ────────────────────────────  ──────────────────
//   RING_OUTER_R 37 mm OD      Housing HOUSING_INNER_R 37.5  0.5 mm radial clr
//   (unison ring)              (outer shell bore)             (ring rotates freely)
//   RING_INNER_R 28.5 mm       Throat tube OD 27.5 mm        1.0 mm radial clr
//   Ring gear pitch R 36 mm    Idler-Out pitch R 7.5 mm      0.1 mm backlash
//   (full-circle, 72 T)        nacelle_nozzle_idler.scad      (centre dist 43.6 mm)
//   HINGE_BORE_D 3.2 mm        3 mm SS hinge pin             0.2 mm diametral clr
//   (×8 tangential hinges)     (×8, 3 mm × 18 mm dowels)      (flaps pivot freely)
//   Follower pin 2.0 mm        Spiral slot width 2.4 mm      0.2 mm/side clr
//   (×8, on flap lever tab)    (unison_ring(), ×8 slots)      (slides along spiral)
//   Housing bonding lip        Nacelle exit face duct         epoxy bond,
//   OD = HOUSING_OUTER_R 41mm  (hull exit aperture 82 mm ID)  positive shoulder stop
//
//   phi range achieved: PHI_OPEN..PHI_CLOSED =~ 3.58..25.94 deg (reference
//   points); hard stops extrapolate to roughly -14..+27 deg — VERIFY against
//   a printed prototype before final tolerancing (first-pass concept, see
//   header).

// ── Render Instructions ───────────────────────────────────────────────────────
//
// Export each part individually (uncomment one section at a time):
//
// Render throat-and-housing:
// nozzle_throat_and_housing();
//
// Render unison ring:
// unison_ring();
//
// Render one flap (print × 8):
// nozzle_flap();
//
// Assembly preview — all 8 flaps at the closed (cruise) reference position +
// throat/housing + ring.  This is the DEFAULT render: serenity_assembly.py
// imports nacelle_nozzle_iris.stl as the combined assembly for spatial/
// clearance purposes, not as a print-ready single part — the throat-and-
// housing/ring/flaps are still printed as three separate parts pulled from
// this same file (uncomment one block at a time above).
//
// Each flap's own local origin is its hinge point, already centred on its
// wedge's angular span (annular_wedge() built symmetric about local angle
// 0 — see nozzle_flap()).  Assembly per flap (applied right-to-left):
// rotate by PHI_CLOSED about the hinge's own tangential (local Y) axis,
// THEN translate the (now-tilted) flap so its hinge lands at hull position
// (R_HINGE, 0, HINGE_Z), THEN sweep that whole placement around Z by the
// flap's circumferential index.
nozzle_throat_and_housing();
unison_ring();
for (i = [0 : N_FLAPS - 1]) {
    rotate([0, 0, i * 360 / N_FLAPS])
        translate([R_HINGE, 0, HINGE_Z])
            rotate([0, PHI_CLOSED, 0])
                nozzle_flap();
}
