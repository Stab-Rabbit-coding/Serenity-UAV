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
// diaphragm.  Rev S1 (2026-07-07) replaces the Rev R1 gear train's idler
// stage with a direct INTERNAL-ring mesh (Nozzle Drive Pinion 14T M0.5 ->
// internal 136T ring gear — see docs/NOZZLE_DRIVE_TRADE.md); the ring's
// spiral-cam coupling to the flaps is unchanged.
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
//   FLAP_LENGTH = 40 mm, hinge to trailing edge.  Trailing-edge exit radius
//   as a function of flap swing angle phi (phi = 0 -> flap parallel to duct
//   axis, flush extension of the throat tube; phi > 0 -> flap swings
//   inward/downstream, converging):
//     exit_r(phi) = R_HINGE - FLAP_LENGTH * sin(phi)
//   Solving for the two bore-percentage targets (CLAUDE.md: 75 % of the
//   25 mm bore radius at 0 deg/cruise tilt, 105 % at 90 deg/hover tilt):
//     phi_closed = asin((R_HINGE - NOZZLE_CLOSED_R) / FLAP_LENGTH)
//                = asin((27.5 - 18.75) / 40) = asin(0.21875) = 12.64 deg
//     phi_open   = asin((R_HINGE - NOZZLE_OPEN_R)   / FLAP_LENGTH)
//                = asin((27.5 - 26.25) / 40) = asin(0.03125) =  1.79 deg
//   Both angles are POSITIVE (always at least slightly converging from the
//   throat) — there is no sign change to handle, unlike an earlier draft of
//   this derivation that put the hinge at the bore radius itself.  Both
//   angles are gentle (< 13 deg with the Rev T2 40 mm flap) — the flap is
//   never more than ~13 deg off the local flow direction, the actual
//   "smooth, low-turbulence" goal (halved from the old 20 mm flap's ~26 deg).
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
//   theta_ring derived from the Rev S1 chain: Stage 1 sector/Pinion-A
//   epicyclic x3.5882, Stage 2 bevel x10/14, Stage 3 drive-pinion-to-
//   internal-ring x3.5/34 — see the Ring Rotation mapping block) linearly
//   to pin_r:
//     pin_r(theta_ring) = PIN_R_REF_CLOSED
//                        + (PIN_R_REF_OPEN - PIN_R_REF_CLOSED)
//                          * theta_ring / THETA_RING_REF_OPEN
//   calibrated at the two REFERENCE points (theta_ring = 0 at 0 deg/cruise
//   tilt -> closed; theta_ring = 23.75 deg at 90 deg/hover tilt -> open —
//   Rev S1 chain, within 0.5 % of the Rev R1 figure).  The slot is cut
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
//   1. nozzle_throat_and_housing() — fixed: throat tube (flow liner, with
//      the Rev S1 drive-pinion relief patch) + outer shell + 8 tangential
//      hinge bosses + connecting ribs.
//   2. unison_ring()               — rotating: Rev S1 INTERNAL 136T M=0.5
//      ring gear (meshed from inside by the Nozzle Drive Pinion), plus
//      8 spiral cam slots on its downstream face.
//   3. nozzle_flap()                — one flap (print x 8): tangential
//      hinge knuckle (clevis) + compound lever tab + follower pin.
//
// Mating interfaces (pushrod drive, Rev T — Option B):
//   Pushrod: a ball-ended rod from a fixed crank on the nacelle pivot spar
//   strokes the unison ring's single lever ear (RING_LEVER_*), rotating it
//   0..23.75 deg over 0..90 deg tilt (linkage authored in the Stage-3 pushrod
//   SCAD).  The Rev S1 internal ring gear + Nozzle Drive Pinion + entire aft
//   gear train (sector, Pinion A, bevel pair) are DELETED — see header Rev T
//   and docs/NOZZLE_DRIVE_TRADE.md Option B.
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
//     verify they clear the drive-pinion sweep and all 8 flap hinge/cam
//     paths in the slicer.
//
// Upstream attribution (REFERENCES.md REF-CAD-001):
//   The variable-area duct-exit nozzle concept is informed by BamJr's
//   "Variable-area EDF nozzle" (Thingiverse Thing 2991269, CC BY 4.0,
//   <https://www.thingiverse.com/thing:2991269>).  Used as a mechanism /
//   kinematics reference ONLY — all geometry in this file (throat liner,
//   tangential-hinge overlapping conical flaps, unison ring gear, spiral
//   cam actuation) is original work authored for this project; no BamJr
//   geometry, mesh, or source is copied.  See REFERENCES.md [REF-CAD-001].
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
// Rev:     S1 (2026-07-07): INTERNAL ring gear conversion — flipped the
//          ring's teeth from the outer rim (72T M1.0 external) to the bore
//          (136T M0.5 internal, L-shaped section w/ separate gear band and
//          cam flange), deleting the compound idler + its housing slot
//          (the idler's teeth protruded ~10 mm past the nacelle OD — trade
//          study: docs/NOZZLE_DRIVE_TRADE.md; user decision 2026-07-07).
//          Added the drive-pinion throat relief patch (wall 2.5 -> 1.1 mm
//          over a 30 deg sector, gear-band heights only).  theta_ring
//          sweep 23.86 -> 23.75 deg (Rev S1 chain).  Flap/cam kinematics
//          unchanged.  AI contribution: Claude (Fable 5, Anthropic),
//          directed by Steve Griffing.
// Rev:     S2 (2026-07-18): follower-pin offset SIGN-BUG fix — TAB_X/TAB_Z had
//          the wrong sign, parking all 8 flap follower pins in the exhaust jet
//          (pin_r 20-24, aft of the throat) where they also could not reach the
//          ring cam, so the nozzle could not actuate.  Corrected to pin_r
//          31->35; bore restored smooth.  See the TAB_X/TAB_Z derivation block.
// Rev:     T  (2026-07-18): DRIVE ARCHITECTURE change — adopted Option B
//          (docs/NOZZLE_DRIVE_TRADE.md, user decision 2026-07-18): the internal
//          ring gear and the ENTIRE aft gear train (sector, Pinion A, bevel
//          pair, Nozzle Drive Pinion) are DELETED; the unison ring is now a
//          plain CAM-ONLY disc stroked by a PUSHROD/BELLCRANK from the pivot
//          (single lever ear, RING_LEVER_*).  Freed from the pinion mesh, the
//          ring shrinks Ø74 -> Ø66 and the housing Ø82 -> Ø71, seating inside
//          the canonical nozzle pocket instead of standing proud of the aft
//          cowl.  Follower band pulled inboard to pin_r 29->31; drive-pinion
//          throat relief removed (full 2.5 mm liner wall restored).  Staged
//          work — Stage 2 (housing outer profile to the cowl mould line),
//          Stage 3 (pushrod/bellcrank SCAD + stroke derivation), Stage 4
//          (archive the gear-train parts), Stage 5 (pod pocket, assembly,
//          docs) — tracked in the WBS.  AI contribution: Claude (Opus 4.8,
//          Anthropic), directed by Steve Griffing.

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
FLAP_LENGTH  = 40.0;             // [mm] hinge to trailing edge, axial-ish length
                                 //   Rev T2 (2026-07-18): doubled 20 -> 40 per
                                 //   user direction — a longer flap sweeps the
                                 //   same exit-radius range over HALF the swing
                                 //   arc (PHI 1.79..12.64 deg vs the old
                                 //   3.58..25.94), a gentler cone / lower
                                 //   turbulence and less follower travel demand.
HINGE_Z      = THROAT_LEN;       // [mm] = 15.0, hinge line Z station

// phi(exit_r) = asin((R_HINGE - exit_r) / FLAP_LENGTH) — see header derivation.
PHI_CLOSED = asin((R_HINGE - NOZZLE_CLOSED_R) / FLAP_LENGTH);   // = 12.64 deg (L=40)
PHI_OPEN   = asin((R_HINGE - NOZZLE_OPEN_R)   / FLAP_LENGTH);   // =  1.79 deg (L=40)

// ── Lever Tab / Follower Pin (drives the flap from the ring's spiral cam) ────
//
// TAB_X (radial outward offset) and TAB_Z (axial upstream offset) of the
// follower-pin tip from the hinge, solved so the follower pin's radius
// pin_r(phi) stays >= PIN_R_REF_CLOSED across the full operating range
// (clearing THROAT_OUTER_R with margin, so the ring's bore can clear the
// throat tube while the spiral slot still reaches the pin) while spanning
// a PIN_R_REF_OPEN - PIN_R_REF_CLOSED range usable by the cam:
//   pin_r(phi) = R_HINGE + TAB_X*cos(phi) - TAB_Z*sin(phi)
// Solved for pin_r(PHI_OPEN) = PIN_R_REF_OPEN, pin_r(PHI_CLOSED) = PIN_R_REF_CLOSED.
// Rearranging pin_r(phi) = R_HINGE + TAB_X*cos(phi) - TAB_Z*sin(phi) gives, at
// each reference angle,  TAB_X*cos - TAB_Z*sin = (PIN_R_REF - R_HINGE)  — the
// RHS is (target radius MINUS hinge radius), a POSITIVE number here (the pin
// sits OUTBOARD of the hinge, at the ring).  The two-equation solution below
// carries that (PIN_R_REF - R_HINGE) sign.
//
// SIGN-BUG FIX (Rev S2, 2026-07-18): the prior form wrote the RHS as
// (R_HINGE - PIN_R_REF), i.e. negated — which flipped TAB_X/TAB_Z to ≈ −8,
// driving the follower pin INWARD to R≈20–24 mm and AFT to Z≈20–26 mm: into
// the core exhaust jet (bore R25) and 12–18 mm downstream of the ring, so it
// both disrupted the airflow AND never reached the ring's spiral cam slots
// (which are cut at pin_r 30–38 mm — see pin_r_at_theta / SPIRAL_R_LO/HI).
// The nozzle therefore could not actuate as drawn.  Correcting the RHS sign
// restores the header/trade-doc intent: follower at pin_r 31→35 mm, upstream
// in the housing wall, fully clear of the smooth inner bore.  (Found while
// investigating a user report of "a hook in the middle of the airflow" on
// each flap's interior face, 2026-07-18.)  AI contribution: Claude (Opus 4.8,
// Anthropic), directed by Steve Griffing.
// Rev T (2026-07-18, Option B pushrod drive): PIN_R_REF pulled INBOARD from
// 31/35 to 29/31.  With the internal ring gear deleted (see header Rev T), the
// ring no longer needs to reach the drive pinion at R30.5 — the cam is free to
// hug the throat OD (27.5).  A follower band of 29→31 mm keeps the pin just
// clear of the throat (29 − pin_r 1.0 − 0.2 clr = 27.8 > 27.5) while dropping
// the cam ring OD to ≈Ø66 (was Ø74), so it seats inside the canonical Ø65-class
// nozzle pocket (nacelle_pod_50mm_tandem.scad NOZZLE_RING_OD) instead of
// standing Ø82 proud of the aft cowl.  The lever tab lengthens slightly to map
// this shorter 2 mm follower travel onto the same PHI_OPEN..PHI_CLOSED swing.
PIN_R_REF_CLOSED = 29.0;   // [mm] follower-pin radius at theta_ring = 0 (closed)
PIN_R_REF_OPEN   = 31.0;   // [mm] follower-pin radius at theta_ring = full stroke (open)

TAB_Z = ((PIN_R_REF_OPEN - R_HINGE) - (PIN_R_REF_CLOSED - R_HINGE) * cos(PHI_OPEN) / cos(PHI_CLOSED))
        / (sin(PHI_CLOSED) * cos(PHI_OPEN) / cos(PHI_CLOSED) - sin(PHI_OPEN));
                            // [mm] =~ +8.5, axial (upstream) component of the lever tab
TAB_X = ((PIN_R_REF_CLOSED - R_HINGE) + TAB_Z * sin(PHI_CLOSED)) / cos(PHI_CLOSED);
                            // [mm] =~ +8.1, radial (outward) component of the lever tab

FOLLOWER_PIN_D   = 2.0;    // [mm] follower pin OD (SS dowel)
FOLLOWER_PIN_L   = 4.0;    // [mm] follower pin length (engages the ring's slot pocket)

// pin position as a function of swing angle phi (used for BOTH the flap's
// own pin placement and, via the theta_ring mapping below, the ring's
// spiral slot — single source of truth, see header).
function flap_pin_r(phi) = R_HINGE + TAB_X * cos(phi) - TAB_Z * sin(phi);
function flap_pin_z(phi) = HINGE_Z - TAB_X * sin(phi) - TAB_Z * cos(phi);

// ── Ring Rotation <-> Pin Radius Mapping ──────────────────────────────────────
//
// Rev T (2026-07-18): the ring is now stroked by a PUSHROD / BELLCRANK from the
// nacelle pivot (docs/NOZZLE_DRIVE_TRADE.md Option B), NOT a gear train — the
// entire aft gear chain (sector, Pinion A, bevel pair, Nozzle Drive Pinion,
// internal ring gear) is deleted.  The pushrod linkage is sized (Stage 3, in
// the pushrod SCAD) so that nacelle tilt 0 → 90° rotates this ring through the
// SAME theta_ring = 0 → 23.75° stroke the cam spiral was cut for — so the cam
// geometry below is unchanged in principle, only the drive upstream of the ring
// differs.  Because the linkage carries its own mechanical stops, the cam no
// longer needs the wide over-travel the gear chain's −5°/140° tilt stops
// implied; the spiral is trimmed to the operating stroke plus a small margin.
//   0 deg nacelle tilt (cruise)  -> theta_ring =  0.00 deg -> closed
//   90 deg nacelle tilt (hover)  -> theta_ring = 23.75 deg -> open
THETA_RING_REF_OPEN = 23.75;   // [deg] ring stroke over 0→90° tilt (linkage-set)
SPIRAL_MARGIN_DEG   =  2.0;    // [deg] extra arc past each operating end
SPIRAL_ANG_LO =  0.00 - SPIRAL_MARGIN_DEG;              // [deg] = -2.00
SPIRAL_ANG_HI = THETA_RING_REF_OPEN + SPIRAL_MARGIN_DEG; // [deg] = 25.75
                            //   (27.75° total slot arc; adjacent 45°-spaced
                            //   slots clear each other easily at this reduced
                            //   radial band)

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

// ── Ring (Unison Disc) Dimensions — Rev T CAM-ONLY ring (pushrod drive) ───────
//
// Rev T (2026-07-18): Option B (docs/NOZZLE_DRIVE_TRADE.md, user decision
// 2026-07-18).  The internal ring GEAR (Rev S1 136T M0.5) and the entire aft
// gear train are DELETED — the ring is now a plain cam disc rotated by a
// PUSHROD/BELLCRANK from the nacelle pivot (linkage authored in the Stage-3
// pushrod SCAD).  Freed from meshing the drive pinion at R30.5, the ring drops
// from Ø74 to ≈Ø66, seating inside the canonical Ø65-class nozzle pocket rather
// than standing Ø82 proud of the aft cowl (the whole point of the switch).
//
// The ring is now a simple FLAT annular disc (no L-section gear band):
//   • Cam flange (full height Z 0..RING_H): annulus from CAM_FLANGE_INNER_R out
//     to RING_OUTER_R, carrying the 8 spiral cam slots on its outboard face
//     (pin_r spans 29..31 — see PIN_R_REF_* above).
//   • Rim pilots in the housing bore (0.5 mm running clearance), as before.
//   • Pushrod lever: one radial ear on the rim (RING_LEVER_*) with a ball-end
//     socket for the pushrod — the single drive input (replaces 136 teeth).

RING_H        =  8.0;        // [mm] total axial height (unchanged)

// Cam-slot radial envelope (drives the ring OD).  slot_out ≈ SPIRAL_R_HI +
// half-width; rim adds a thin pilot land.  slot_in stays > THROAT_OUTER_R.
RING_OUTER_R  = 33.1;        // [mm] rim OD ≈ Ø66.2 (was 37.0/Ø74); seats in the
                             //   Ø≈68 nozzle pocket (pod NOZZLE_RING_OD, Stage 5)
CAM_FLANGE_INNER_R = 28.5;   // [mm] cam-flange inner radius (clears throat OD
                             //   27.5 by 1.0; slot_in = 29 − 1.2 = 27.8 > 27.5)

// ── Pushrod lever (single drive input; replaces the internal ring gear) ──────
RING_LEVER_AZ   = 22.5;   // [deg] azimuth of the lever ear (in a flap gap,
                          //   between slots at 0°/45°)
RING_LEVER_R    = 32.0;   // [mm] radial reach of the ball-socket centre on the
                          //   lever (effective moment arm for the pushrod)
RING_LEVER_W    =  5.0;   // [mm] lever ear tangential width
RING_BALL_D     =  3.0;   // [mm] pushrod ball-end nominal (socket = +clearance)

// ── Outer Housing Dimensions ──────────────────────────────────────────────────
// Rev T: bore shrinks to clear the Ø66 cam ring; outer wall 2.0 mm (piloting
// shell, non-primary) → Ø≈70, recessed into the Ø72 pocket.  Stage 2 will
// taper/ovalise the outer wall to follow the canonical cowl mould line.
HOUSING_INNER_R =  33.6;   // [mm] bore radius (ring Ø66.2 + 0.5 mm/side clr)
HOUSING_OUTER_R =  35.6;   // [mm] outer radius (OD ≈ 71.2 mm; was 41.0/Ø82) —
                            //   set by the hinge-boss envelope (≈R34.7), the
                            //   binding hard point (see module note)
HOUSING_AFT_R   =  33.5;   // [mm] outer radius at the aft face (Z=THROAT_LEN):
                            //   the shell tapers HOUSING_OUTER_R→HOUSING_AFT_R
                            //   aft of the ring to follow the cowl's aft
                            //   narrowing; hinge bosses may stand slightly proud
                            //   of this at the exit lip (they carry the flaps)
HOUSING_LIP_H   =   3.0;   // [mm] forward bonding lip depth (bonds to nacelle
                            //   exit face; lip OD matches EDF duct exit OD)

// (Rev T: the Rev S1 drive-pinion relief pocket is DELETED with the gear train —
// no pinion sweeps the throat wall any more, so the liner is full 2.5 mm wall.)

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
//   - Outer shell (Rev T): OD = 2*HOUSING_OUTER_R ≈ 71 mm, bore =
//     2*HOUSING_INNER_R ≈ 67 mm (cam-only unison ring rides inside),
//     Z = 0..THROAT_LEN, bonding lip at the inboard face.  Aft of the ring
//     (Z > RING_H) the outer wall tapers to HOUSING_AFT_R to follow the
//     canonical cowl's aft narrowing (Stage 2, Rev T).
//   - RIB_N ribs bridging throat-tube OD to outer-shell bore at a single
//     axial station, offset from the flap centrelines.
//
//   BINDING ENVELOPE (Rev T): the tangential hinge bosses reach ≈R34.7
//     (Ø69.4) at the hinge station Z=HINGE_Z — wider than the cam ring
//     (Ø66) or the shell bore, so they, not the ring, now set the minimum
//     nozzle OD.  Fully ovalising the housing to the cowl mould line (and
//     resolving the hinge-boss vs aft-cowl clearance) needs the assembly
//     part-local→hull transform — deferred VERIFY (serenity_assembly.py).
//
//   Origin: centre of inboard (nacelle-side) face, Z = 0.
module nozzle_throat_and_housing() {
    union() {
        difference() {
            union() {
                // ── Outer shell main body (Rev T: ring-region cylinder + aft
                //    taper toward the cowl mould line) ─────────────────────────
                cylinder(h = RING_H, r = HOUSING_OUTER_R);
                translate([0, 0, RING_H])
                    cylinder(h = THROAT_LEN - RING_H,
                             r1 = HOUSING_OUTER_R, r2 = HOUSING_AFT_R);

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
                // Built OUTWARD ONLY from the throat tube's OD (boss centre
                // offset to BOSS_OD/2 - 1.0 mm beyond R_HINGE, i.e. only
                // 1 mm of overlap into the existing tube wall for fusion) —
                // a boss simply CENTRED on R_HINGE (as in an earlier draft)
                // dips to R_HINGE - BOSS_OD/2 = 23.4 mm, INSIDE the
                // THROAT_INNER_R = 25 mm bore, and the throat-bore cut below
                // then slices off that inward dip, severing the boss from
                // the tube entirely (found 2026-06-22 via mesh verification
                // — the boss came out as a disconnected floating body).
                // The hinge pin axis itself stays exactly at R_HINGE
                // (unchanged — required by the flap kinematics derivation
                // above); only the boss's OWN material is shifted outward —
                // the existing tube wall (solid from THROAT_INNER_R=25 to
                // THROAT_OUTER_R=27.5) already provides the bore's inner
                // bearing surface "for free."
                HINGE_BOSS_OD = HINGE_BORE_D + 5.0;
                HINGE_BOSS_X_CEN = R_HINGE + HINGE_BOSS_OD / 2 - 1.0;
                for (i = [0 : N_FLAPS - 1]) {
                    rotate([0, 0, i * 360 / N_FLAPS]) {
                        translate([HINGE_BOSS_X_CEN, 0, HINGE_Z])
                            rotate([90, 0, 0])
                                cylinder(h = HINGE_KNUCKLE_W, d = HINGE_BOSS_OD, center = true);
                    }
                }
            }

            // ── Throat bore — full length, flush with EDF bore ─────────────────
            translate([0, 0, -0.1])
                cylinder(h = THROAT_LEN + 0.2, r = THROAT_INNER_R);

            // ── Unison ring bore — clears RING_OUTER_R inside the outer shell ──
            // Stops at RING_CAVITY_Z_HI, NOT at THROAT_LEN: the ring itself
            // only occupies Z = 0..RING_H = 8 mm, so hollowing the shell out
            // to HOUSING_INNER_R = 37.5 mm any further than necessary would
            // reach into the hinge-boss region (Z ~10.9..19.1, radius up to
            // ~34.7 mm, both INSIDE 37.5 mm) and scoop the bosses out from
            // under the tube — found 2026-06-22 via mesh verification (the
            // bosses came out as disconnected floating bodies, severed at
            // exactly this cut's Z end).  1 mm margin past the ring height.
            RING_CAVITY_Z_HI = RING_H + 1.0;   // [mm] = 9.0
            // Rev S1 BUG FIX: this cut used to be a FULL cylinder of radius
            // HOUSING_INNER_R — which also swallowed the throat tube (r
            // 25..27.5) over the whole cavity height, deleting the flow
            // liner's first 9 mm in every previously published throat STL
            // (verified by cross-section: no material at r < 37.5, Z 0..9).
            // The cavity is now ANNULAR: from just outside the throat tube
            // OD out to the housing bore, so the liner survives and the
            // unison ring (cam-flange inner R 29.0) rides around it.
            translate([0, 0, -HOUSING_LIP_H - 0.1])
                linear_extrude(height = RING_CAVITY_Z_HI + HOUSING_LIP_H + 0.1)
                    difference() {
                        circle(r = HOUSING_INNER_R);
                        circle(r = THROAT_OUTER_R);
                    }

            // (Rev T: the Rev S1 drive-pinion throat relief pocket is DELETED
            // with the gear train — no pinion sweeps the throat wall now, so the
            // liner keeps its full 2.5 mm wall all the way round.)

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
// Rotating unison disc — Rev T CAM-ONLY ring (no gear teeth).  A flat annular
// disc carrying N_FLAPS spiral cam slots on its outboard face plus ONE radial
// pushrod lever ear on the rim.  The pushrod (Stage-3 SCAD) strokes the ear,
// rotating the ring through theta_ring = 0..23.75° as the nacelle tilts 0..90°;
// each flap's follower pin rides one slot, so ring rotation sweeps the slot's
// local radius under the pin and (via the flap's lever tab) rotates the flap
// about its tangential hinge — see header for the kinematic derivation.
//
//   Flat section (see Ring Dimensions block):
//     annulus CAM_FLANGE_INNER_R..RING_OUTER_R, full height Z 0..RING_H;
//     8 spiral cam slots pocketed into the outboard face (Z RING_H, depth
//     SPIRAL_SLOT_DEPTH); one lever ear standing off the rim at RING_LEVER_AZ.
//
//   Origin: centre of inboard face, Z = 0; outboard (slotted) face at
//   Z = RING_H.
module unison_ring() {
    difference() {
        union() {
            // ── Base ring body (flat annular blank at rim OD) ───────────────
            cylinder(h = RING_H, r = RING_OUTER_R);

            // ── Pushrod lever ear (single drive input) ──────────────────────
            // A radial tab off the rim carrying the pushrod ball socket at
            // RING_LEVER_R.  Sits in a flap gap (RING_LEVER_AZ) so it clears
            // all 8 cam slots and the flap sweep.
            rotate([0, 0, RING_LEVER_AZ])
                translate([0, -RING_LEVER_W / 2, 0])
                    cube([RING_LEVER_R + RING_BALL_D, RING_LEVER_W, RING_H]);
        }

        // Cam-flange through-bore — clears the throat tube full height
        translate([0, 0, -0.1])
            cylinder(h = RING_H + 0.2, r = CAM_FLANGE_INNER_R);

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

        // ── Pushrod ball socket (blind, in the lever ear) ────────────────────
        rotate([0, 0, RING_LEVER_AZ])
            translate([RING_LEVER_R, 0, RING_H / 2])
                sphere(d = RING_BALL_D + 0.4);   // 0.2 mm/side clearance ball seat
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

// ── Fit Confirmation (Rev T cam-only / pushrod drive) ───────────────────────────
//
//   Interface                  Mating part                   Clearance / fit
//   ─────────────────────────  ────────────────────────────  ──────────────────
//   RING_OUTER_R 33.1 mm OD    Housing HOUSING_INNER_R 33.6  0.5 mm radial clr
//   (cam-only unison ring)     (outer shell bore)             (ring rotates freely)
//   CAM_FLANGE_INNER_R 28.5    Throat tube OD 27.5 mm        1.0 mm radial clr
//   Ring lever ear (RING_      Pushrod ball end (RING_BALL_   ball-in-socket,
//     LEVER_R 32, socket)        D 3.0), Stage-3 pushrod SCAD  0.2 mm/side seat
//   HINGE_BORE_D 3.2 mm        3 mm SS hinge pin             0.2 mm diametral clr
//   (×8 tangential hinges)     (×8, 3 mm × 18 mm dowels)      (flaps pivot freely)
//   Follower pin 2.0 mm        Spiral slot width 2.4 mm      0.2 mm/side clr
//   (×8, on flap lever tab)    (unison_ring(), ×8 slots)      (slides along spiral)
//   Housing bonding lip        Nacelle exit face duct         epoxy bond,
//   OD = HOUSING_OUTER_R 35.6  (nozzle pocket, Ø≈72)          positive shoulder stop
//
//   phi range achieved: PHI_OPEN..PHI_CLOSED =~ 1.79..12.64 deg (Rev T2 40 mm
//   flap reference points; half the old 20 mm flap's 3.58..25.94 range).  The
//   ring lever stroke and its mechanical stops are set by the Stage-3 pushrod
//   linkage — VERIFY follower travel, ring-bore clearance, and the lever-ear
//   housing exit slot against a printed prototype before final tolerancing
//   (first-pass concept, see header).

// ── Render Instructions ───────────────────────────────────────────────────────
//
// Part selection is via the RENDER_PART -D string parameter (matching the
// nacelle_nozzle_idler.scad / wings RENDER_SIDE convention), so the Makefile
// can pull each print-ready part from this one file:
//   RENDER_PART = "throat"  -> nozzle_throat_and_housing()  (fixed liner+shell)
//   RENDER_PART = "ring"    -> unison_ring()                (136T int. gear + cam)
//   RENDER_PART = "flap"    -> nozzle_flap()                (print × 8)
//   RENDER_PART = "asm"     -> full assembly preview        (DEFAULT; the
//        combined body serenity_assembly.py imports as nacelle_nozzle_iris.stl
//        for spatial/clearance checks, not as a print-ready single part).
//
// Assembly-per-flap (applied right-to-left): rotate by PHI_CLOSED about the
// hinge's own tangential (local Y) axis, THEN translate the tilted flap so its
// hinge lands at (R_HINGE, 0, HINGE_Z), THEN sweep around Z by the flap index.
RENDER_PART = "asm";   // "throat" | "ring" | "flap" | "asm"

if (RENDER_PART == "throat") {
    nozzle_throat_and_housing();
} else if (RENDER_PART == "ring") {
    unison_ring();
} else if (RENDER_PART == "flap") {
    nozzle_flap();
} else {
    // asm — full closed-position assembly preview
    nozzle_throat_and_housing();
    unison_ring();
    for (i = [0 : N_FLAPS - 1]) {
        rotate([0, 0, i * 360 / N_FLAPS])
            translate([R_HINGE, 0, HINGE_Z])
                // −PHI_CLOSED: the flap body extrudes +Z just inside R_HINGE, so a
                // POSITIVE tilt throws the tips radially OUTWARD (diverging).  The
                // closed nozzle must CONVERGE (exit_r = R_HINGE − FLAP_LENGTH·sin φ
                // = 18.75 < 27.5), so the assembly tilt is −PHI_CLOSED.  (Sign-bug
                // fix 2026-07-20; preview only — print parts are unaffected.)
                rotate([0, -PHI_CLOSED, 0])
                    nozzle_flap();
    }
}
