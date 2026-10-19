// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   This part is modeled in a LEG-LOCAL frame (hip pin at origin, pin axis
//   = local Y, swing plane = local XZ, +X outboard in the swing direction,
//   +Z dorsal/up).  NOT a primary-component STL; do NOT bake with
//   bake_hull_frame.py.  Corner placement transforms live in the
//   "hull_stance" PART below and in docs/LANDING_GEAR_ANALYSIS.md Rev R6.
// ===========================================================================
// ===========================================================================
// canonical_leg_r6_3_0in.scad
// Serenity UAV -- Rev R6 -- Canonical Articulated Landing Leg (hip-pivot)
// -- 3.0 in (80 mm) BELLY CLEARANCE VARIANT (THE FLIGHT ARTICLE, adopted
// 2026-09-06 -- see docs/LANDING_GEAR_ANALYSIS.md S4.8) --
// ===========================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// AI note : Authored by Claude (model: Claude Fable 5, Anthropic) under the
//           author's direction, 2026-07-21.  Per AGENTS.md AI attribution.
//           Split into the 1.5in / 3.0in named variants 2026-07-23 (same
//           attribution).
// Project : Serenity-class Tilt-Rotor UAV (24-inch scale, Firefly TV ship)
// License : CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
// Date    : 2026-07-21 (variant split 2026-07-23)
// Revision: Rev R6 (supersedes Rev R5 wire_brace_leg.scad -- retained for
//           reference with a retirement note, per the SS1.1.4.5 pattern)
//
// Canonical references (see REFERENCES.md):
//   REF-CAD-003  QMx "Official Serenity Blueprints Reference Pack" (2007),
//                Sheet 5 "Ventral Surface Plan View" -- bay stations (fore
//                feet 39.2% / aft feet 63.9% of hull length, ~1.45x hull
//                half-width off centreline), "Detail of Landing Gear"
//                (tri-pad foot, "Feet Pivot 90 deg") and leg side view
//                (cylinder-cluster thigh ~50 deg, disc knee/ankle joints).
//   REF-CAD-002  Nick Henning reference renders -- close-up leg mechanical
//                detail: telescoping piston cluster, 4-satellite-hole disc
//                joints, slotted shin, wedge tri-pad foot.
//   Canonical universe: Firefly / Serenity (TV/film), created by Joss
//                Whedon; ship design Tim Earls / Geoffrey Mandel (QMx pack).
//
// Deliberate deviations from canon (functional build, documented):
//   1. Leg length -- canonical proportions give only ~11 mm belly clearance
//      at 24-in scale.  Ground clearance is an AIRCRAFT SAFETY spec (avoid
//      a belly/tail strike and keep the hull clear of ground debris during
//      the landing/absorption stroke) -- it is NOT sized to pass a cargo
//      box underneath the parked aircraft.  THIS FILE is the 3.0 in
//      (80 mm) variant -- it is the original Rev R6 design point
//      (2026-07-21) and the reference the wire schedule is solved
//      against.  **Adopted as the flight article 2026-09-06**
//      (docs/LANDING_GEAR_ANALYSIS.md S4.8): the tilted-to-vertical
//      nozzle stack hangs 38-47 mm below the belly datum on every
//      takeoff/landing, and the compact 1.5 in leg is 27-40 mm below the
//      minimum safe clearance that drives -- not rescuable within this
//      leg family.  "The 3.0 in leg is the flight article" (S4.8
//      verbatim).  The compact 1.5 in variant, `canonical_leg_r6_1_5in.scad`,
//      is RETIRED to bench/ground-handling use only (props off, no
//      tilt-to-vertical, the nozzle-clearance driver does not apply).
//      Both share the identical bay/foot/wire BOM; only the printed
//      leg-frame length differs.  Cost of the decision: +67 g (0.148 lbm),
//      symmetric fore/aft (no X/Y CG shift), vertical CG and belly both
//      rise 41.9 mm (LG-29, open) -- see S4.8 for the full trade.
//   2. Knee/ankle articulate on-screen; here the leg frame is ONE printed
//      piece (thigh+shin) and all articulation is at the HIP -- the knee
//      and ankle discs are canonical styling.  ("Feet Pivot 90 deg" is
//      realized as a square spigot indexing the foot at 90-deg steps.)
//   3. Gear is fixed-down (no retraction); the bay plate provides the
//      canonical recessed-bay look on the hull flank.
//
// Structural basis: tools/landing_gear_r6_sizing.py (all numbers below
// trace to its output) and docs/LANDING_GEAR_ANALYSIS.md Rev R6 SS4.7 (the
// two-variant comparison).  Mechanism summary: the whole leg pivots about
// an M3 stainless hip pin in a hull-flank bay.  Two SPRING bowed wires
// (elastic, recoverable) and two DUCTILE bowed wires (plastic, sacrificial
// fuse) span the hip at a 6 mm bellcrank radius: leg flexion (foot
// swinging up-outboard) compresses the wire chords so their pre-formed
// bows deepen -- identical mechanics to Rev R5, but the 65:6 lever turns
// millimetres of wire stroke into tens of millimetres of hull settle
// (peak decel ~52 g tail-down / ~104 g level at the 6 ft schedule, vs
// ~1,000 g for the Rev R5 rigid post).  This is the gentler of the two
// variants -- the compact 1.5in leg reuses this same wire hardware over a
// shorter lever and runs hotter (~81 g / ~162 g).  An M3 extension-stop
// cross-pin through the clevis ears carries the opposite (hanging /
// in-flight) rotation via a tab on the thigh root; landing loads never
// touch it.
//
// Usage -- set PART to render:
//   PART = "leg_frame"    One-piece thigh+shin leg frame (CF-PETG, print
//                         lying on its -Y side: bending loads stay in the
//                         layer plane -- strongest orientation)
//   PART = "foot"         Canonical tri-pad arrowhead foot (TPU 95A)
//   PART = "bay"          Hull-flank bay plate: clevis, wire bosses, stop (CF-PETG)
//   PART = "spring_wire_nominal"   / "spring_wire_deformed"
//   PART = "ductile_wire_nominal"  / "ductile_wire_deformed"
//   PART = "leg_assembled"  One complete leg + bay + wires, leg-local frame
//   PART = "leg_deformed"   Same, flexed to full ductile stroke (post-overload)
//   PART = "hull_legs"      All 4 corners at hull-frame stations, gear only
//   PART = "hull_stance"    Same + ground plane + cargo-belly ghost (review)
//
// STL export (from repo root; output names lg_r6_3_0in_<part>.stl):
//   openscad -o airframe/stls/fuselage/landing-gear/lg_r6_3_0in_leg_frame.stl \
//     -D 'PART="leg_frame"' airframe/openscad/fuselage/canonical_leg_r6_3_0in.scad
//   ... (same pattern for every PART above)
// ===========================================================================

PART = "leg_assembled";      // override with -D on the CLI
BAY_STATION  = "aft";       // "fore" | "aft" -- selects the back-face datum, the
                            // wire-row azimuths and the stop-pin azimuth; MUST
                            // precede every assignment that reads it
$fn = 48;

// ---------------------------------------------------------------------------
// Leg-local skeleton (mm) -- hip pin at origin, +X outboard, +Z up.
// Hip sits 118 mm above ground; belly clearance 80 mm / 3.15 in (hip is at
// hull-frame Z +38 on the cargo-flank bay).  See the sizing script for the
// lever numbers.
// ---------------------------------------------------------------------------
// LG-10.2 HIP RECESS (2026-08-09, owner decision).  The pivot is translated
// 15 mm along leg-local -X (into the bay) so the pivot and the wire anchors sit
// inside the recess instead of hanging outside the skin -- see
// tools/landing_gear_bay_station_fit.py and LANDING_GEAR_ANALYSIS.md SS2.4a.
// Translating along the SWING axis (not the panel normal) is what keeps the
// FOOT exactly where it was: R_H grows by the same 15 mm, so hip + R_H is
// unchanged.  Measured against the panel normal the bay gains 11.8-12.6 mm of
// depth (the swing azimuth is not aligned with the panel normal).
// ACCEPTED TRADE: the longer lever makes the leg softer -- peak decel falls but
// the arrest settles further, and the compact variant pays for it out of the
// only clearance it has (residual 15.5 -> 7.4 mm).  Holding F_leg constant by
// growing the ductile wire to d 4.22 mm was offered and declined.
KNEE   = [59, 0, -66];      // knee disc centre (thigh 88.5 mm @ 48.2 deg from horiz).
                            // X was 50 pre-recess; 9 of the 15 mm recess is taken
                            // in the thigh and 6 in the shin, keeping the shin SHORT
                            // per [REF-CAD-002].
ANKLE  = [80, 0, -100];     // ankle disc centre (shin 40.0 mm @ 31.7 deg lean).
                            // X = R_H by construction: the foot spigot sits here.
GROUND_Z = -118;            // foot sole plane (leg-local)
R_H    = 80;                // horizontal hip->foot moment arm (was 65 pre-recess)

// Hip pivot / clevis
PIN_D        = 3.2;         // M3 stainless pin clearance bore
HUB_D        = 9.0;         // thigh hip-hub core OD (keeps wire chords clear)
LUG_W        = 14.0;        // thigh root lug width along pin (Y)
EAR_T        = 3.0;         // bay clevis ear thickness
EAR_CLR      = 0.5;         // lug-to-ear side clearance each side

// Extension stop: M3 SS cross-pin through both clevis ears; a tab on the
// thigh root rests on it at nominal extension.  Flexion lifts the tab off.
// 2026-10-11 (BHD-02g): the two-row wire layout needs the stop elsewhere --
// at 118 the rows' horns and seated wire ends cross it.  Pin and tab rotate
// TOGETHER about the hip (tab = pin + 13..28 deg), so the rest pose is
// unchanged.  Was 118 / 131..146 at both stations.
STOP_PIN_AZ  = (BAY_STATION == "aft") ? 210 : 195;  // pin centre azimuth (deg)
STOP_PIN_R   = 8.0;         // pin centre radius from hip axis
STOP_TAB_AZ1 = STOP_PIN_AZ + 13;   // thigh tab sector start (contact face)
STOP_TAB_AZ2 = STOP_PIN_AZ + 28;   // thigh tab sector end

// Bellcrank wire sockets (in the thigh root, around the pin)
CRANK_R      = 6.0;         // socket centre radius from pin axis
// BHD-02k / BHD-02g (2026-10-10, owner B "redesign the wire geometry"): the
// Rev R6 single row -- 4 sockets at 3.5 mm pitch, CRANK_AZ -22 -- could not
// be built: the wires (O4.26 / O3.59) are thicker than the pitch and four
// O4.9 bores need 19.6 mm across the 14 mm lug.  TWO ROWS of two: the ductile
// row and the spring row, each at its own crank azimuth, 6 mm in-row pitch
// (y +/-3), crank radius and 90 deg crank-to-chord transmission unchanged --
// so every wire's force, arm and stroke, and therefore the sizing, are as
// tools/landing_gear_r6_sizing.py solved them.  A row's chord points crank +
// 90 (flexion turns the thigh counter-clockwise in XZ, so the chord shortens
// and the wire bows in compression).  The azimuths come from the swing-plane
// screen tools/lg_wire_layout_study.py, then the 3-D census.
// PER STATION (2026-10-11): the fore and aft clusters must avoid different
// things (aft: the wing root above; fore: the hull belly and the doors below),
// so each station has its own thigh -- one leg part number per station, as
// the bays already are.  Values from the swing-plane screen, confirmed by
// the 3-D census (docs/BHD02_OPTION_STUDY.md SS12).
CRANK_AZ_D   = (BAY_STATION == "aft") ?  30 : -20;   // ductile row
CRANK_AZ_S   = (BAY_STATION == "aft") ? 120 :  70;   // spring row
ROW_PITCH    = 6.0;         // in-row socket pitch along Y (bore 4.91 + 1.1 wall)
HORN_WALL    = 1.5;         // crank-horn wall around a socket bore that leaves
                            // the root lug (the horn rides on the thigh)

// Wire schedule -- tools/landing_gear_r6_sizing.py output.  Each wire is
// straight stock with ONE shallow mid-span bow; the ENDS STAY STRAIGHT
// (socket seat depth + 2 mm run-in per end) so they can seat in straight
// bores -- the bow occupies only the exposed span between socket mouths.
// DUCTILE diameter is the 6 ft drop-test schedule (Rev R6 default); the
// 4 ft alternative is d=3.81 mm, SAME lengths -- only stock diameter changes.
SPRING_D     = 3.59;        // mm, spring wire diameter.  Was 3.35: the
                            // elastic-limit target is 350 N/leg, and the
                            // lever it acts over grew to R_H 80 mm, so the
                            // wire has to carry more to hit the same onset.
SPRING_L     = 34.0;        // mm, spring stock length (bow span 20)
                            // Was 37 (bow span 23).  The bow span comes
                            // from wire_stroke_available(), which was 4x
                            // low until 2026-08-09 (SS4.5a); the corrected
                            // solve floors on BOW_SPAN_MIN = 20 mm at a
                            // 3.97x stroke reserve.
SPRING_SEAT  = 5.0;         // mm, spring socket seat depth per end
DUCTILE_D    = 4.26;        // mm, ductile wire dia -- 4 ft schedule.
                            // Was 3.81.  Sized by the CLEARANCE-limited
                            // variant, not by a peak-decel target: at
                            // R_H 80 the 3.81 wire needs 43.2 mm of settle
                            // and the compact leg has 38.1 mm, so it would
                            // BOTTOM OUT -- 2.20 J (11.8%) of a 4 ft arrest
                            // arriving as a 1.68 m/s belly strike with the
                            // fuse only 88% fired.
                            // (LG-17 CLOSED 2026-08-09, owner decision:
                            //  4 ft crash height adopted).  The 6 ft
                            //  alternative was d = 4.36 mm, SAME lengths.
DUCTILE_D6   = 4.36;        // mm, 6 ft schedule (superseded, ref only)
DUCTILE_L    = 40.0;        // mm, ductile stock length (bow span 20)
                            // Was 75 (bow span 55) -- a consequence of the
                            // 4x-low stroke formula (SS4.5a), NOT of the
                            // energy balance.  The corrected solve needs
                            // only 24 mm of span to deliver the SAME
                            // 3.24 mm stroke at a 1.5x reserve.  d, P,
                            // F_leg, settle, hip rotation and peak decel
                            // are all UNCHANGED -- see the sizing script.
DUCTILE_SEAT = 8.0;         // mm, ductile socket seat depth per end
END_RUN_IN   = 2.0;         // mm, straight run-in beyond each socket mouth
H_NOM        = 3.5;         // mm, pre-bend bow rise (both types)
H_DEF_SPRING = 4.38;        // mm, bow at spring elastic-limit stroke
                            // (0.93 mm) on the corrected 20 mm span.
H_DEF_DUCT   = 5.70;        // mm, fired ductile bow at full stroke, on
                            // the corrected 24 mm bow span.  History: 19.2
                            // (4x-low stroke formula), then 9.9 (formula
                            // corrected but still read against the old 55 mm
                            // span).  The rise is only meaningful WITH its
                            // span -- 6.84 mm on 24 mm is rise/span 0.285 vs
                            // 0.146 nominal, i.e. still an unambiguous
                            // "visibly bent" field-inspection indicator.
SOCK_CLR     = 0.65;        // socket bore diametral clearance over wire d

// Thigh cylinder cluster (structural section: sizing script "2x14 @ 18")
// THIGH_VARIANT (LG-REMASS, 2026-10-19; owner evaluating, default unchanged):
//   "baseline" -- Rev R6 14 mm cylinders @ 18 mm, 6 mm bores from 20 mm out.
//   "grown"    -- 17 mm cylinders @ 22 mm: ~1.9x section modulus, all printed.
//   "cf_core"  -- baseline envelope; the bores run from the knee end through
//                 the root lug and a 6 mm pultruded CF rod is bonded in each,
//                 anchored by a 3 mm steel cross-pin through the lug so the
//                 hip moment reaches the rods by bearing, not by bond alone.
THIGH_VARIANT = "baseline";
THIGH_CYL_D  = (THIGH_VARIANT == "grown") ? 17.0 : 14.0;   // main cylinder OD
THIGH_CYL_C  = (THIGH_VARIANT == "grown") ? 22.0 : 18.0;   // centre spacing, swing plane
CF_ROD_D     = 6.0;         // cf_core: rod OD (bore = CF_ROD_D + 2 x 0.1 bond gap)
CF_ROD_START = 6.0;         // cf_core: rod root station along the hip->knee axis
CF_PIN_D     = 3.0;         // cf_core: steel cross-pin through lug + rod
CF_PIN_AT    = 11.0;        // cf_core: cross-pin station along the axis
THIGH_BORE_D = 6.0;         // LG-18: axial bore through each main cylinder.
                            // MUST equal THIGH_BORE_D in
                            // tools/landing_gear_r6_sizing.py, which
                            // regenerates the section margin from it:
                            //   bore 0  Z 2219 mm^3  margin 1.25x
                            //   bore 6  Z 1926 mm^3  margin 1.09x  <- here
                            //   bore 8  Z 1686 mm^3  margin 0.95x  FAILS
THIGH_PISTON_D = 5.0;       // cosmetic telescoping piston rod OD
THIGH_COLLAR_D = 15.0;      // cosmetic telescope collar OD, lower third.
                            // LG-19: 16 read as a swollen sleeve against
                            // the Ø14 tube; [REF-CAD-002] shows a slim
                            // collar barely proud of the tube it rides.

// Knee / ankle disc joints -- canonical 4-satellite-hole wheel styling.
// COSMETIC on Rev R6 (leg frame is one piece; articulation is at the hip).
THIGH_HOSE_D = 2.2;         // LG-19 #5: hose runs alongside the cluster,
                            // visible in every [REF-CAD-002] view and
                            // absent from Rev R6 entirely.
KNEE_DISC_D  = 26.0;
KNEE_DISC_T  = 3.0;         // proud styling disc, both Y faces
KNEE_BCD     = 15.0;        // satellite-hole circle diameter
KNEE_SAT_D   = 3.0;         // satellite recess diameter (1.6 mm deep)
KNEE_CTR_D   = 5.0;         // centre recess
ANKLE_DISC_D = 16.0;
ANKLE_DISC_T = 12.0;        // spans the shin thickness + proud both faces.
                            // LG-19 #4: was 14 (2 mm proud each side), which
                            // read as a flat plate.  12 gives 1 mm of rim
                            // and the hub cap below carries the joint look.
ANKLE_HUB_D  = 9.0;         // raised hub cap OD, both faces
ANKLE_HUB_H  = 2.0;         // hub cap height proud of the disc

// Shin blade (canonical slotted flat member)
SHIN_W       = 20.0;        // width in swing plane
SHIN_T       = 10.0;        // thickness along pin axis
SHIN_SLOT_L  = 14.0;        // cosmetic vent slot length
SHIN_SLOT_W  = 3.5;
SHIN_SLOT_DEEP = 2.0;       // pocket depth per face (NOT through -- keeps section)

// Foot (canonical tri-pad arrowhead, TPU 95A) -- print frame: sole on Z=0
FOOT_HUB_D   = 24.0;        // central hub OD
FOOT_HUB_H   = 10.0;        // hub height; top face meets the ankle disc rim
FOOT_PAD_T   = 5.0;         // pad thickness at hub.  LG-19 #3: Rev R6's 8 mm
                            // pads are stubby slabs; [REF-CAD-002] shows flat
                            // blade-like wedges, much longer and thinner, with
                            // a sharp taper to the tip.  This is also the
                            // single largest LG-18 saving on the foot.
FOOT_PAD_TIP_T = 2.5;       // pad thickness at the tip (was a hardcoded 4.0)
FOOT_TOE_L   = 40.0;        // fore (toe) pad length from hub centre (was 34)
FOOT_TOE_W   = 20.0;        // toe pad root width
FOOT_HEEL_L  = 31.0;        // rear pad length from hub centre (was 26)
FOOT_HEEL_W  = 18.0;        // rear pad root width
FOOT_HEEL_AZ = 130;         // rear pads at +/-130 deg from toe
FOOT_SPIG    = 8.0;         // square ankle spigot side ("Feet Pivot 90 deg":
                            // square socket indexes the foot at 90-deg steps)
FOOT_SPIG_H  = 6.0;         // socket depth in the hub top face
FOOT_M25_D   = 2.8;         // M2.5 cross-bolt clearance
TREAD_N      = 3;           // tread ribs per pad (canonical ribbed sole)
TREAD_D      = 1.5;         // tread rib depth

// Foot-joint stack-up, leg-local (LG-10.8, 2026-08-17).  The joint closes on
// the foot's HUB TOP FACE against the ankle disc rim -- the spigot only
// indexes the foot at 90 deg steps, it does not carry the stance load -- so
// the spigot must stop SHORT of the socket floor.  The old hardcoded cube
// (`ANKLE[2] - 9.75`, 9.5 tall) bottomed out on that floor instead: 0.6 mm on
// the 3.0in leg and 7.0 mm on the 1.5in one.  Verify with
// tools/landing_gear_foot_stance.py, which gates both rules below.
FOOT_SOCK_FLOOR = GROUND_Z + FOOT_HUB_H - FOOT_SPIG_H + 0.1;  // socket floor
SPIG_FLOOR_CLR  = 0.4;      // spigot tip clearance above that floor
SPIG_Z0         = FOOT_SOCK_FLOOR + SPIG_FLOOR_CLR;
// The disc rim must LAND on the hub top face, never inside it.
assert(abs((ANKLE[2] - ANKLE_DISC_D / 2) - (GROUND_Z + FOOT_HUB_H)) < 0.05,
       "ankle disc rim must meet the foot hub top face: set ANKLE[2] = GROUND_Z + ANKLE_DISC_D/2 + FOOT_HUB_H");

// Bay plate.  LG-10 (2026-08-09): the original surface-mount assumption was
// measured against the baked cargo skin and does NOT hold -- the back face
// floated 14-17 mm outboard of the hull at hip height, BAY_CANT leaned the
// plate the WRONG WAY (the real flank leans outboard going up, not inboard),
// and the flank is doubly curved with 15-42 mm of deviation across the
// footprint.  See tools/landing_gear_bay_pad_fit.py for the measurements.
//
// The back face is FLAT, and stays flat -- LG-10.6, 2026-08-17.  It was going
// to be CONFORMING (cut against a local hull-surface patch), which is the
// right answer for a plate bolted to a raw compound-curved flank; but since
// LG-10.3/LG-10.4 the hull no longer offers one.
// merge_cargo_interior.lg_bay_features() cuts a flange REBATE -- a flat
// trapezoidal pocket, BAY_PLATE_T deep and 12 mm into the skin -- with a seat
// collar under it, and that pocket is deep enough to shave the whole
// footprint (tools/landing_gear_wing_clearance.py --proud reports "none").
// The hull therefore presents a FLAT seat, normal to the bolt axis by
// construction.  Cutting the printed part to a curve it no longer meets would
// put the mismatch straight back, and would split the bay into four unshared
// geometries for nothing -- one part per station still fits, so the SS11.4
// shared-BOM claim holds.  BAY_CONFORM and its patch generator are retired;
// what the two files must now agree on is the DATUM, gated by
// tools/landing_gear_bay_seat_fit.py.
// BAY_STATION is assigned near the top of the file (before the stop-pin and
// wire-row parameters that also depend on it -- a forward reference to it
// would silently read undef and give every station the fore values).

BAY_PLATE_T  = 5.0;         // frame thickness -- MUST be assigned before
                            // BAY_BACK_X below, which reads it (OpenSCAD
                            // resolves top-level assignments in order;
                            // a forward reference silently yields undef
                            // and the whole part renders displaced).

// Back-face datum, PER STATION.  This is a CONTRACT with
// merge_cargo_interior.py, which cuts the hull pocket this frame drops into:
//     BAY_STANDOFF[s] = mci.BAY_STANDOFF[s] + mci.station_seat_data()[1][s]
// Gate it with tools/landing_gear_bay_seat_fit.py after ANY hull re-merge.
//
// The previous 12.6 / 5.4 came from tools/landing_gear_bay_station_fit.py,
// which measures the outboard skin along the SS2.4a panel NORMAL.  The plate's
// own e_x is 21-24 deg off that normal (the LG-10.3 yaw), so a standoff
// measured in one frame and applied in the other overshoots: it left the frame
// floating 3.5-7.7 mm outboard of the pocket floor the merge had actually cut,
// and every M3 would have clamped across an air gap.  Re-measured 2026-08-17
// in the frame that places the part (merge_cargo_interior.seat_offset), the
// station datums are x0 -7.69 fore / -3.55 aft, giving:
//   fore  +4.91 mm from the hip        aft  +1.85 mm from the hip
// ONE datum per station, taken at the deeper of that station's two corners --
// the printed bay is one part per station, so it can only seat on one floor.
// The shallower corner (fore-port, 1.14 mm) takes a feeler shim at assembly;
// aft is 0.02 mm, i.e. identical.  The frame's OUTER face lands on the seat
// and sits BAY_PLATE_T out from the datum, so datum = standoff - thickness.
// 2026-10-10 (BHD-02): fore re-measured at the moved station (hip Y -16):
// x0 -6.53 (fore-stbd, the deeper) -> 6.07; was 4.91 at Y -1.28.  Since the
// owner's conforming-seat decision the printed FLANGE and LINER follow the
// skin (tools/generate_lg_bays.py) and this datum only places the hip-relative
// body (ears, gussets, carrier) -- it is kept so the seat-fit gate still holds.
BAY_STANDOFF = (BAY_STATION == "fore") ? 6.07 : 1.85;
BAY_BACK_X   = BAY_STANDOFF - BAY_PLATE_T;
BAY_CANT     = -11.5;       // deg; NEGATIVE = leans outboard at the top, which
                            // is what the real cargo flank does (was +22)
// The bay APERTURE is the hull well opening (merge_cargo_interior.py
// LG_WELL_W_BOT / LG_WELL_W_TOP / LG_WELL_L).  These four numbers are a
// contract between the two files -- change one, change both.  Trapezoidal,
// narrow at the bottom: that is the mouth the leg swings out of (SS2.4a).
BAY_APER_W_BOT = 25.0;      // mm, along the pin axis, at the mouth
BAY_APER_W_TOP = 34.0;      // mm, along the pin axis, at the head
BAY_APER_L     = 58.0;      // mm, up the canted plane.  The verified-clear
                            // thigh corridor is 53 mm (see the cowl clearance
                            // tool); 58 keeps the 2.5 mm liner wall plus
                            // clearance without cutting more hull than needed.
BAY_APER_ZB0   = -38.0;     // aperture bottom edge, canted-plate frame.
                            // Was -32: the 3.0in thigh drops more steeply
                            // through the same mouth and fouled the rim by
                            // 11.9 mm^3 AT REST (flex 0) -- exactly the
                            // failure mode the closed rectangular rim hit.
                            // -35 cleared the rim but the thigh still clipped
                            // the FLANGE's lower lip at the outer face by
                            // 0.16 mm^3 (a 0.4 mm deep sliver at leg-local
                            // [5.3, 0, -23.4]) -- the flange wraps under the
                            // mouth to carry the two lower M3s, so opening
                            // the liner alone was not enough.  -38 is clear
                            // with margin; verified on both
                            // variants by boolean intersection over the full
                            // 0..22 deg sweep plus 26 deg of margin
                            // (tools/landing_gear_cowl_clearance.py).

// Bolt flange: the only solid material on the part, a band all round the
// aperture.  The Rev R6 solid plate had no room for its own bolts -- at the
// head the aperture was 36 mm wide inside a 40 mm plate, so the M3 centres at
// +/-15 fell INSIDE the opening.  That is why the merge tool's bosses ended up
// out on the bare flank.
BAY_FLANGE   = 10.0;        // mm, flange width all round the aperture
// Thigh exit notch.  The flange wraps UNDER the mouth to carry the two lower
// M3s, but that band sits directly in the thigh's exit path -- the 3.0in leg
// (steeper thigh, same aperture) cut 25.6 mm^3 out of it AT REST.  Chasing it
// by lowering BAY_APER_ZB0 only moves the collision down with the leg.  The
// canonical bay is a U, open at the low end (see the bay_cowl notes); the
// flange gets the same relief, notched only across the centre so the two lower
// bolts at |y| 17.5 keep their material and the couple lever is unchanged.
BAY_NOTCH_W  = 22.0;        // mm, notch width across the pin axis.  Thigh is
                            // LUG_W 14 wide (+/-7) with piston rods to +/-6.5,
                            // so this leaves 4 mm of clearance each side.
BAY_PLATE_W  = BAY_APER_W_TOP + 2 * BAY_FLANGE;   // 54, head (wide) end
BAY_PLATE_WB = BAY_APER_W_BOT + 2 * BAY_FLANGE;   // 45, mouth (narrow) end
BAY_PLATE_L  = BAY_APER_L + 2 * BAY_FLANGE;       // 78, up the canted plane
BAY_PLATE_ZB0 = BAY_APER_ZB0 - BAY_FLANGE;        // -42

// M3 centres run down the middle of the flange, so they follow the trapezoid.
BAY_BOLT_ZB  = [BAY_PLATE_ZB0 + BAY_FLANGE / 2,
                BAY_PLATE_ZB0 + BAY_PLATE_L - BAY_FLANGE / 2];   // -37, +31
BAY_BOLT_YB  = [(BAY_APER_W_BOT + BAY_FLANGE) / 2,
                (BAY_APER_W_TOP + BAY_FLANGE) / 2];              // 17.5, 22
                            // merge_cargo_interior.py LG_BOLT_ZB / LG_BOLT_YB
                            // MUST track these pairs.
BAY_M3_HEAD_CB = 0.0;       // (reserved) counterbore depth, frame outer face
BAY_M3_D     = 3.4;         // 4x M3 shell through-bolts (+ internal backing)
BOSS_OD      = 11.0;        // wire boss OD (bearing margin: see sizing script)
BOSS_L       = 10.0;        // wire boss length along chord

// --- Canonical retraction-bay cowl (LG-19 / LG-02) -------------------------
// On the canonical ship the leg retracts into a recessed flank bay; this build
// is fixed-down but must still READ as a leg emerging from that bay.  The
// recess cannot be sunk into the hull: the cargo wall measures 1.97-4.65 mm
// there, and the footprint's interior is already occupied by the wing spar
// boss (Y 20.7..42.7), the wing root mortise (Y 42..73 @ Z 52..73) and the
// nacelle-servo pad (Y 19..71 @ Z 78..108).  The bay depth is therefore
// carried on THIS printed part as a cowl standing proud of the plate, which
// is also how a real retraction-bay liner is built.
// The cowl is now the well LINER: it runs INBOARD from the frame, through the
// 2 mm skin and the 5 mm reinforcing collar the merge tool grows around each
// opening, so the leg reads as emerging from a real recess instead of from a
// rim stuck on the outside of the skin.  Before LG-10 cut the wells open there
// was no recess to line and the depth had to be faked by standing the rim
// PROUD of the plate; with the hull open that is now backwards, and at the aft
// stations it stood 4.5 mm out into the airstream.
COWL_H       = 7.0;         // liner depth INBOARD (2 mm skin + 5 mm collar)
COWL_T       = 2.5;         // liner wall thickness
COWL_W_TOP   = BAY_APER_W_TOP;   // liner outer face IS the aperture
COWL_W_BOT   = BAY_APER_W_BOT;
COWL_TAPER   = COWL_W_BOT / COWL_W_TOP;   // 0.735, retained for reference

// --- LG-10.3 bay internal structure ----------------------------------------
// With the wells cut OPEN, the bay is a recessed BOX and there is no longer a
// solid plate behind the clevis and the wire bosses for them to root on.  Left
// as Rev R6 built them they root at the old plate datum, which now falls inside
// the OPEN aperture -- the part renders as 3 disconnected bodies.  They are
// carried by the liner instead:
//   * a CARRIER slab normal to the wire chord ties all four bosses into both
//     liner side walls;
//   * a GUSSET each side flares the clevis ears out from |y| 10.5 to the wall
//     annulus (|y| 11.7..14.2 at the hip station).
// Both are checked by body_count == 1 on the rendered bay, not by eye.
BAY_CARRIER_T = 12.0;       // slab thickness along the chord -- spans the
                            // FULL boss length, because it is the only
                            // thing carrying the bosses now
BAY_CARRIER_W = 30.0;       // slab width along the pin axis (reaches the walls)
BAY_CARRIER_H = 16.0;       // slab extent in the swing plane
BAY_GUSSET_Y0 = 8.8;        // gusset inboard edge.  8.0 grazed the thigh
                            // lug blend by 0.16 mm^3 at rest.
BAY_GUSSET_Y1 = 14.0;       // gusset outboard edge (lands in the liner wall)
BAY_GUSSET_Z  = [-9.0, 15.0];   // gusset extent up the swing plane
BAY_GUSSET_X  = [-6.0, 3.0];    // gusset depth band, relative to BAY_BACK_X

// --- LG-13 wire-end retention ----------------------------------------------
// The wire ends MUST remain free to slide: the chord shortens by the stroke as
// the bow deepens, so each end travels ~1.62 mm DEEPER into its bore at full
// ductile stroke (stroke = U/P = 3.24 mm; see tools/landing_gear_r6_sizing.py
// and the sympy derivation recorded in docs/LANDING_GEAR_ANALYSIS.md SS4.5a).
// A set screw torqued onto the seat would clamp that motion and fight the
// fuse, so retention is a NYLON-TIPPED drag screw: enough friction to stop
// vibration walk-out (~5 N) and negligible against the 4,333 N chord force.
// Bay side only -- with the bay end captive the wire cannot leave the
// thigh-side blind bore either (it would have to translate along its axis).
RET_SCREW_D  = 2.0;         // M2 nylon-tipped cup-point set screw
RET_TAP_D    = 1.6;         // M2 tap drill (printed pilot, tapped after print)
RET_PAD_D    = 6.5;         // local thread pad OD on the boss
RET_PAD_H    = 3.5;         // pad height proud of the boss OD
RET_DEPTH_D  = 4.0;         // screw axis, mm from the boss mouth (ductile)
RET_DEPTH_S  = 2.5;         // screw axis, mm from the boss mouth (spring)

// Flexion at full ductile stroke (sizing script: 22.0 deg hip rotation).
// Was 30.9 deg: the stiffer ductile wire needs less stroke (2.30 mm, not
// 3.24 mm) to absorb the same energy, and rotation = stroke / CRANK_R.
FLEX_DEG     = 22.0;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

// Unit vector in the XZ swing plane at azimuth az (deg from +X toward +Z)
function azv(az) = [cos(az), 0, sin(az)];

// Wire table, i = 0..3: 0-1 the DUCTILE row, 2-3 the SPRING row, each pair at
// y -/+ ROW_PITCH/2.
function w_spring(i) = i >= 2;
function w_y(i)      = (i % 2 == 0 ? -1 : 1) * ROW_PITCH / 2;
function w_crank(i)  = w_spring(i) ? CRANK_AZ_S : CRANK_AZ_D;
function w_chord(i)  = w_crank(i) + 90;
function w_l(i)      = w_spring(i) ? SPRING_L : DUCTILE_L;
function w_seat(i)   = w_spring(i) ? SPRING_SEAT : DUCTILE_SEAT;
function w_d(i)      = w_spring(i) ? SPRING_D : DUCTILE_D;

// Thigh-side socket MOUTH centre of wire i
function crank_socket(i) = CRANK_R * azv(w_crank(i)) + [0, w_y(i), 0];

// Bay boss bore MOUTH centre of wire i: exposed span between mouths = l - 2 seat
function boss_mouth(i) = crank_socket(i) + (w_l(i) - 2 * w_seat(i)) * azv(w_chord(i));

// Solid rod between two points
module rod_between(a, b, d) {
    v = b - a;
    l = norm(v);
    polar = atan2(norm([v[0], v[1]]), v[2]);
    az = atan2(v[1], v[0]);
    translate(a) rotate([0, 0, az]) rotate([0, polar, 0])
        cylinder(h = l, d = d);
}

// Y-axis cylinder centred at point p, total width w, diameter d
module ycyl(p, w, d) {
    translate(p + [0, -w / 2, 0]) rotate([-90, 0, 0]) cylinder(h = w, d = d);
}

// ---------------------------------------------------------------------------
// Bowed wire strut (Rev R5 polyhedron sweep, carried forward with the face
// winding corrected -- Rev R5's winding yielded inward normals / negative
// volume): round wire, stock length L along local Z centred at the origin.
// The ends stay STRAIGHT for a length e each (socket seat + run-in); only
// the mid-span of length B = L - 2e carries the parabolic bow of rise h
// toward local +X (formable on a simple bending jig with straight grips).
// ---------------------------------------------------------------------------
module bowed_wire(d, L, h, e = 0) {
    n = 24;
    sides = 12;
    r = d / 2;
    b = L - 2 * e;                      // bow span between straight ends
    path = [for (i = [0 : n]) let (
        t = i / n,
        z = (t - 0.5) * L,
        zb = z + L / 2 - e,             // position within the bow span
        u = zb / b,
        x = (zb <= 0 || zb >= b) ? 0 : h * (1 - pow(2 * u - 1, 2))
    ) [x, 0, z]];
    tangents = [for (i = [0 : n]) let (
        i0 = max(i - 1, 0), i1 = min(i + 1, n),
        dv = path[i1] - path[i0]
    ) dv / norm(dv)];
    rings = [for (i = [0 : n]) let (
        t = tangents[i],
        arb = (abs(t[1]) < 0.9) ? [0, 1, 0] : [1, 0, 0],
        u = cross(t, arb) / norm(cross(t, arb)),
        v = cross(t, u)
    ) [for (j = [0 : sides - 1]) let (ang = 360 * j / sides)
        path[i] + r * (u * cos(ang) + v * sin(ang))]];
    points = [for (i = [0 : n]) for (j = [0 : sides - 1]) rings[i][j]];
    side_faces = [for (i = [0 : n - 1]) for (j = [0 : sides - 1]) let (
        a = i * sides + j,
        b = i * sides + (j + 1) % sides,
        c = (i + 1) * sides + (j + 1) % sides,
        d2 = (i + 1) * sides + j
    ) each [[a, c, b], [a, d2, c]]];
    faces = concat(side_faces,
                   [[for (j = [0 : sides - 1]) j]],
                   [[for (j = [sides - 1 : -1 : 0]) n * sides + j]]);
    polyhedron(points = points, faces = faces, convexity = 4);
}

// Wire i posed in the leg-local frame, SEATED: the stock runs from `seat` deep
// inside the thigh socket, along its row's chord, to `seat` deep inside its bay
// boss bore.  The bow bulges IN THE SWING PLANE, radially outward (toward the
// crank arm's own azimuth).  Rev R6 had an extra rotate([0, 0, 90]) here that
// its comment said put the bow "into the swing plane"; it put it along the
// PIN axis instead, into the neighbouring wire and the clevis ear (BHD-02k).
module posed_wire(i, h) {
    a = crank_socket(i);
    translate(a + (w_l(i) / 2 - w_seat(i)) * azv(w_chord(i)))
        rotate([0, 90 - w_chord(i), 0])     // local +Z -> chord; local +X -> crank azimuth
            bowed_wire(w_d(i), w_l(i), h, w_seat(i) + END_RUN_IN);
}

// Wedge sector in the XZ plane: azimuth az1..az2, radius r1..r2, width w
// along Y, centred on the hip axis.  Used for the extension-stop tab.
module xz_sector(az1, az2, r1, r2, w) {
    steps = 6;
    pts_outer = [for (i = [0 : steps]) let (a = az1 + (az2 - az1) * i / steps)
        [r2 * cos(a), r2 * sin(a)]];
    pts_inner = [for (i = [steps : -1 : 0]) let (a = az1 + (az2 - az1) * i / steps)
        [r1 * cos(a), r1 * sin(a)]];
    translate([0, w / 2, 0]) rotate([90, 0, 0])
        linear_extrude(height = w) polygon(concat(pts_outer, pts_inner));
}

// ---------------------------------------------------------------------------
// MODULE: knee_disc_cosmetic(y_face)
// Canonical knee "wheel" styling disc, proud on one Y face of the leg at
// the knee: 4 satellite recesses on KNEE_BCD + centre recess (QMx Sheet 5
// side view / Henning renders).  y_face = +1 or -1.
// ---------------------------------------------------------------------------
module knee_disc_cosmetic(y_face) {
    y0 = y_face * SHIN_T / 2;               // flush at the blade face
    difference() {
        ycyl(KNEE + [0, y0 + y_face * KNEE_DISC_T / 2, 0],
             KNEE_DISC_T, KNEE_DISC_D);
        for (a = [45, 135, 225, 315])
            translate(KNEE + [KNEE_BCD / 2 * cos(a),
                              y0 + y_face * (KNEE_DISC_T + 0.1),
                              KNEE_BCD / 2 * sin(a)])
                rotate([90 * y_face, 0, 0])
                    cylinder(h = 1.6, d = KNEE_SAT_D);
        translate(KNEE + [0, y0 + y_face * (KNEE_DISC_T + 0.1), 0])
            rotate([90 * y_face, 0, 0])
                cylinder(h = 1.6, d = KNEE_CTR_D);
    }
}

// ---------------------------------------------------------------------------
// MODULE: leg_frame()
// One-piece structural leg in leg-local assembly position:
//   hip hub + bellcrank wire sockets + extension-stop tab at the root,
//   twin-cylinder thigh cluster with web down to the knee,
//   cosmetic telescope collars + piston rods (canonical telescoping look),
//   canonical knee styling discs both faces,
//   slotted shin blade, ankle disc, square foot spigot.
// Print lying on the -Y face: swing-plane bending stays in the layer plane.
// ---------------------------------------------------------------------------
module leg_frame() {
    axis = KNEE / norm(KNEE);               // unit vector hip -> knee
    perp = [-axis[2], 0, axis[0]];          // in-plane perpendicular
    difference() {
        union() {
            // Hip hub core (kept slim so wire chords clear it -- see header)
            ycyl([0, 0, 0], LUG_W, HUB_D);
            // Extension-stop tab (rests on the bay's stop cross-pin)
            xz_sector(STOP_TAB_AZ1, STOP_TAB_AZ2, 3.0, 10.0, LUG_W);
            // Crank horns (BHD-02g): a local boss around each ROW's sockets,
            // hulled to the hub, so a row may sit outside the root lug.
            for (az = [CRANK_AZ_D, CRANK_AZ_S])
                hull() {
                    ycyl([0, 0, 0], LUG_W, HUB_D);
                    ycyl(CRANK_R * azv(az), LUG_W,
                         DUCTILE_D + SOCK_CLR + 2 * HORN_WALL);
                }
            // Root lug: blend hub into the cluster.  The hull() stays in
            // the down-outboard quadrant, out of the wire-chord corridor.
            hull() {
                ycyl([0, 0, 0], LUG_W, HUB_D);
                for (s = [-1, 1])
                    translate(14 * axis + s * THIGH_CYL_C / 2 * perp)
                        sphere(d = THIGH_CYL_D);
            }
            // Twin main cylinders, hip to knee
            for (s = [-1, 1])
                rod_between(10 * axis + s * THIGH_CYL_C / 2 * perp,
                            KNEE + s * THIGH_CYL_C / 2 * perp - 6 * axis,
                            THIGH_CYL_D);
            // Web between the cylinders (hulled sphere chain)
            hull()
                for (s = [-1, 1]) {
                    translate(12 * axis + s * THIGH_CYL_C / 2 * perp)
                        sphere(d = THIGH_CYL_D * 0.72);
                    translate(KNEE - 8 * axis + s * THIGH_CYL_C / 2 * perp)
                        sphere(d = THIGH_CYL_D * 0.72);
                }
            // Cosmetic telescope collars (lower third of the cluster)
            for (s = [-1, 1])
                rod_between(KNEE - 28 * axis + s * THIGH_CYL_C / 2 * perp,
                            KNEE - 8 * axis + s * THIGH_CYL_C / 2 * perp,
                            THIGH_COLLAR_D);
            // Cosmetic piston rods on the outboard shoulder.  LG-19 #5:
            // [REF-CAD-002] shows a large main tube plus TWO OR THREE smaller
            // parallel rods; Rev R6 had two.  The third sits inboard-low so
            // the cluster reads as a stack rather than a symmetric pair.
            for (yo = [-4, 4])
                translate([0, yo, 0])
                    rod_between(12 * axis + 10 * perp,
                                KNEE - 24 * axis + 10 * perp,
                                THIGH_PISTON_D);
            rod_between(14 * axis - 9 * perp, KNEE - 26 * axis - 9 * perp,
                        THIGH_PISTON_D * 0.8);
            // Hose runs alongside the cluster (LG-19 #5).  Two thin tubes
            // stood off the outboard shoulder, following the thigh line.
            for (yo = [-6.5, 6.5])
                translate([0, yo, 0])
                    rod_between(16 * axis + 12.5 * perp,
                                KNEE - 20 * axis + 12.5 * perp,
                                THIGH_HOSE_D);
            // Knee styling discs, both faces (canonical wheel pattern)
            knee_disc_cosmetic(1);
            knee_disc_cosmetic(-1);
            // Shin blade: stadium section swept knee -> ankle
            hull() {
                ycyl(KNEE, SHIN_T, SHIN_W);
                ycyl(ANKLE, SHIN_T, SHIN_W * 0.8);
            }
            // Ankle disc + raised hub caps (LG-19 #4: reads as a real hub
            // joint, not a flat styling plate)
            ycyl(ANKLE, ANKLE_DISC_T, ANKLE_DISC_D);
            for (yf = [-1, 1])
                ycyl(ANKLE + [0, yf * (ANKLE_DISC_T / 2 + ANKLE_HUB_H / 2), 0],
                     ANKLE_HUB_H, ANKLE_HUB_D);
            // Square foot spigot: ankle disc rim down into the foot socket,
            // stopping SPIG_FLOOR_CLR short of the socket floor (LG-10.8).
            translate([ANKLE[0], ANKLE[1], (SPIG_Z0 + ANKLE[2]) / 2])
                cube([FOOT_SPIG, FOOT_SPIG, ANKLE[2] - SPIG_Z0],
                     center = true);
        }
        // LG-18: axial bore through each main thigh cylinder.  Starts past the
        // root lug blend (which carries the hip moment into the cluster) and
        // stops short of the knee, so the loaded ends stay solid.  Printed
        // lying on the -Y face the bore axis is horizontal -- a Ø6 bridge.
        // It runs OUT through the knee end rather than stopping inside: ending
        // it flush with the cylinder's end cap left a sealed internal void
        // (watertight, CI-passing, and invisible -- it showed up only as two
        // NEGATIVE-volume bodies in the split), which traps air, cannot drain
        // and cannot be inspected.  Through-bored it also reads as the real
        // tube [REF-CAD-002] shows.
        //
        // NOTE the section check is conservative: the bore starts 20 mm out
        // along the thigh, so the CRITICAL section at the hip -- where the
        // bending moment is greatest -- stays SOLID.  The 1.09x margin from
        // the sizing script applies the bored section at the full hip moment.
        if (THIGH_VARIANT == "cf_core") {
            // Rod bores run through the root lug to CF_ROD_START (clear of the
            // hub: rod edge at perp 9 - 3.1 = 5.9 > HUB_D/2 4.5), out the knee.
            for (s = [-1, 1])
                rod_between(CF_ROD_START * axis + s * THIGH_CYL_C / 2 * perp,
                            KNEE + 4 * axis + s * THIGH_CYL_C / 2 * perp,
                            CF_ROD_D + 0.2);
            // Cross-pin bore through the lug and both rods, along the pin (Y).
            for (s = [-1, 1])
                ycyl(CF_PIN_AT * axis + s * THIGH_CYL_C / 2 * perp, LUG_W + 0.2,
                     CF_PIN_D + 0.1);
        } else if (THIGH_BORE_D > 0)
            for (s = [-1, 1])
                rod_between(20 * axis + s * THIGH_CYL_C / 2 * perp,
                            KNEE + 4 * axis + s * THIGH_CYL_C / 2 * perp,
                            THIGH_BORE_D);
        // Hip pin bore
        ycyl([0, 0, 0], LUG_W + 0.2, PIN_D);
        // 4 bellcrank wire sockets: bore along each row's chord, into the root
        for (i = [0 : 3]) {
            translate(crank_socket(i) + 0.1 * azv(w_chord(i)))
                rotate([0, 90 - w_chord(i), 0])
                    translate([0, 0, -w_seat(i) - 0.1])
                        cylinder(h = w_seat(i) + 0.2, d = w_d(i) + SOCK_CLR);
        }
        // Wire-chord relief scallop across the root shoulder (the chords'
        // first 14 mm clear the lug blend and the crank horn)
        for (i = [0 : 3])
            translate(crank_socket(i)) rotate([0, 90 - w_chord(i), 0])
                cylinder(h = 14, d = w_d(i) + 2.5);
        // Canonical vent-slot pockets, both shin faces
        mid = (KNEE + ANKLE) / 2;
        for (sy = [-1, 1]) for (xo = [-4.5, 4.5])
            translate(mid + [xo, sy * (SHIN_T / 2 - SHIN_SLOT_DEEP / 2), 0])
                cube([SHIN_SLOT_W, SHIN_SLOT_DEEP + 0.2, SHIN_SLOT_L],
                     center = true);
        // Ankle cosmetic satellite recesses, both faces
        for (yf = [-1, 1]) for (a = [45, 135, 225, 315])
            translate(ANKLE + [ANKLE_DISC_D * 0.28 * cos(a),
                               yf * (ANKLE_DISC_T / 2 + 0.1),
                               ANKLE_DISC_D * 0.28 * sin(a)])
                rotate([90 * yf, 0, 0]) cylinder(h = 1.6, d = 2.6);
        // M2.5 foot retention cross-bolt through the spigot
        translate([ANKLE[0], ANKLE[1], ANKLE[2] - 11])
            rotate([0, 90, 0])
                cylinder(h = FOOT_SPIG + 8, d = FOOT_M25_D, center = true);
    }
}

// ---------------------------------------------------------------------------
// MODULE: foot()
// Canonical tri-pad arrowhead foot (TPU 95A), sole-down at the origin in
// PRINT orientation: central hub, pointed toe wedge (+X), two swept heel
// wedges, ribbed treads (QMx Sheet 5 "Detail of Landing Gear" bottom
// view), square top-face socket ("Feet Pivot 90 deg" -> 90-deg indexing)
// + M2.5 cross-bolt.
// ---------------------------------------------------------------------------
module foot_pad_wedge(l, w) {
    hull() {
        cylinder(h = FOOT_PAD_T, d = w);
        translate([l, 0, 0]) cylinder(h = FOOT_PAD_TIP_T, d = w * 0.45);
    }
}

module foot() {
    difference() {
        union() {
            cylinder(h = FOOT_HUB_H, d = FOOT_HUB_D);            // hub
            foot_pad_wedge(FOOT_TOE_L, FOOT_TOE_W);              // toe
            for (s = [-1, 1])
                rotate([0, 0, s * FOOT_HEEL_AZ])
                    foot_pad_wedge(FOOT_HEEL_L, FOOT_HEEL_W);    // heels
        }
        // Square ankle-spigot socket, top face (90-deg indexable)
        translate([0, 0, FOOT_HUB_H - FOOT_SPIG_H / 2 + 0.1])
            cube([FOOT_SPIG + 0.4, FOOT_SPIG + 0.4, FOOT_SPIG_H],
                 center = true);
        // M2.5 cross-bolt through hub and spigot
        translate([0, 0, FOOT_HUB_H - 3])
            rotate([0, 90, 0])
                cylinder(h = FOOT_HUB_D + 2, d = FOOT_M25_D, center = true);
        // Ribbed treads across each pad sole (canonical ribbed bottom)
        for (az = [0, FOOT_HEEL_AZ, -FOOT_HEEL_AZ])
            rotate([0, 0, az])
                for (i = [1 : TREAD_N])
                    translate([6 + i * 7, 0, -0.1])
                        cube([2.5, 60, TREAD_D + 0.1], center = true);
    }
}

// ---------------------------------------------------------------------------
// MODULE: bay()
// Hull-flank bay plate in leg-local position: canted mounting plate with
// raised canonical-recess surround, clevis ears (M3 hip pin + M3 stop
// cross-pin), 4 wire bosses on riser wedges at each wire's far chord end,
// 4x M3 shell through-bolt holes.  LG-02 owns final flank conforming.
// ---------------------------------------------------------------------------
// Canonical retraction-bay cowl: a rim standing proud of the plate face so the
// leg reads as emerging from a recessed flank bay (see the COWL_* block).  The
// leg exits through the rim's hollow interior; the sector cut below is
// insurance against the thigh fouling the rim anywhere in its 0..FLEX_DEG
// sweep.
// The rim is a U, OPEN at the low end: that is the bay mouth the leg swings
// out of, and it is what the canonical retraction bay does.  A closed
// rectangular rim was tried first and fails a boolean interference check --
// the thigh fouls the lower wall by 188 mm^3 at rest (flex = 0), falling to
// ~0.8 mm^3 by 20 deg -- because the leg exits across that edge.  Verified
// clear with the same check after opening it; see the LG-13/LG-19 notes in
// docs/LANDING_GEAR_ANALYSIS.md.
// The aperture is TRAPEZOIDAL, not rectangular: narrower at the bottom (the
// mouth the leg swings out of) than at the top, per the canonical flank bays
// in [REF-CAD-003] Sheet 5 / [REF-CAD-002].  Ported here 2026-08-09 -- the
// LG-19 trapezoid originally landed in the 1.5in file ONLY, which silently
// broke the SS11.4 invariant that the bay is one part shared by both variants.

// Trapezoidal prism in the plate frame: width tapers w_bot -> w_top going up
// the plate (local z), centred on the plate's pin-axis centreline, spanning
// x0..x1 out from the plate face.  hull() of two thin end slabs gives the
// linear taper.
module trap_prism(w_bot, w_top, z0, z1, x0, x1) {
    e = 0.01;
    hull() {
        translate([x0, BAY_PLATE_W / 2 - w_bot / 2, z0])
            cube([x1 - x0, w_bot, e]);
        translate([x0, BAY_PLATE_W / 2 - w_top / 2, z1 - e])
            cube([x1 - x0, w_top, e]);
    }
}

module bay_cowl(flange = true) {
    z0 = BAY_APER_ZB0 - BAY_PLATE_ZB0;          // aperture, plate-local z
    z1 = z0 + BAY_APER_L;
    iw_bot = COWL_W_BOT - 2 * COWL_T;
    iw_top = COWL_W_TOP - 2 * COWL_T;
    // Built as ONE union-then-bore, deliberately.  Building the flange and the
    // liner as separate solids and unioning them puts their walls on the SAME
    // surface (the liner's outer face is the flange's aperture wall), which is
    // the coincident-face pattern that renders as a non-manifold shell -- see
    // the SCAD manifold notes in docs/.  Overlapping the two positives and
    // taking a single bore through both avoids any shared boundary.
    translate([BAY_BACK_X, 0, 12])
        rotate([0, -BAY_CANT, 0])
            translate([0, -BAY_PLATE_W / 2, BAY_PLATE_ZB0])
                difference() {
                    union() {
                        // bolt flange slab, full plate outline (omitted for
                        // the CONFORMING bay: tools/generate_lg_bays.py
                        // builds the flange as a skin-following layer and
                        // takes only the liner from here -- BHD-02, 2026-10-10)
                        if (flange)
                            trap_prism(BAY_PLATE_WB, BAY_PLATE_W,
                                       0, BAY_PLATE_L, 0, BAY_PLATE_T);
                        // liner block: aperture outline, running INBOARD
                        // through the skin and collar, up into the flange
                        trap_prism(COWL_W_BOT, COWL_W_TOP, z0, z1,
                                   -COWL_H, BAY_PLATE_T);
                    }
                    // single bore: the open aperture, all the way through
                    trap_prism(iw_bot, iw_top, z0 + COWL_T, z1 - COWL_T,
                               -COWL_H - 0.1, BAY_PLATE_T + 0.1);
                    // open the mouth: remove the narrow low-end wall
                    translate([-COWL_H - 0.1,
                               BAY_PLATE_W / 2 - iw_bot / 2,
                               z0 - 0.1])
                        cube([COWL_H + BAY_PLATE_T + 0.2, iw_bot,
                              COWL_T + 0.2]);
                    // thigh exit notch: carry the same U-shaped opening down
                    // through the lower flange band, so the leg swings out of
                    // the bay instead of through its bolt flange
                    translate([-COWL_H - 0.1,
                               BAY_PLATE_W / 2 - BAY_NOTCH_W / 2,
                               -0.1])
                        cube([COWL_H + BAY_PLATE_T + 0.2, BAY_NOTCH_W,
                              z0 + 0.1]);
                }
}

// LG-13 retention: local thread pad on one wire boss.  The Ø11 boss wall is
// only (11 - 5.65)/2 = 2.68 mm, too thin to tap M2 with any engagement, so the
// thread is carried on a raised pad.  Axis is radial to the wire (normal to
// the chord) and set back RET_DEPTH_* from the boss mouth so the screw always
// bears on the STRAIGHT seat, including after the 1.62 mm inward slide.
module retention_pad(i, cut) {
    dep  = w_spring(i) ? RET_DEPTH_S : RET_DEPTH_D;
    m    = boss_mouth(i);
    // step `dep` INTO the boss along the chord, then go radial (in the swing
    // plane, perpendicular to the chord, clear of the row neighbour).
    seat = m + dep * azv(w_chord(i));
    translate(seat) rotate([0, 90 - w_chord(i), 0]) rotate([0, 90, 0])
        if (cut) {
            // tap pilot: through the pad and the boss wall into the bore
            translate([0, 0, -0.1])
                cylinder(h = RET_PAD_H + BOSS_OD / 2 + 0.2, d = RET_TAP_D);
            // shallow counterbore so the screw sits below the pad face
            translate([0, 0, RET_PAD_H + BOSS_OD / 2 - 1.2])
                cylinder(h = 1.4, d = RET_SCREW_D + 0.6);
        } else {
            translate([0, 0, BOSS_OD / 2 - 1.0])
                cylinder(h = RET_PAD_H + 1.0, d = RET_PAD_D);
        }
}

// Carrier slab: normal to the wire chord, centred on the boss cluster, wide
// enough along the pin axis to bite into both liner walls.  Placed at the boss
// MID-LENGTH so it bonds the full 4-boss cluster rather than clipping its root.
module boss_carrier() {
    // one carrier per ROW (BHD-02g), centred between the row's two bosses
    for (i = [0, 2]) {
        m = (boss_mouth(i) + boss_mouth(i + 1)) / 2;
        translate(m + ((w_seat(i) + 3) / 2 - BAY_CARRIER_T / 4) * azv(w_chord(i)))
            rotate([0, 90 - w_chord(i), 0])
                cube([BAY_CARRIER_H, BAY_CARRIER_W, BAY_CARRIER_T], center = true);
    }
}

// Clevis root gussets: one per side, bridging the ear out to the liner wall.
module clevis_gussets() {
    for (s = [-1, 1])
        translate([BAY_BACK_X + BAY_GUSSET_X[0],
                   s > 0 ? BAY_GUSSET_Y0 : -BAY_GUSSET_Y1,
                   BAY_GUSSET_Z[0]])
            cube([BAY_GUSSET_X[1] - BAY_GUSSET_X[0],
                  BAY_GUSSET_Y1 - BAY_GUSSET_Y0,
                  BAY_GUSSET_Z[1] - BAY_GUSSET_Z[0]]);
}

// ---------------------------------------------------------------------------
// Bay feature modules.  Split out of bay() 2026-10-10 (BHD-02) so that
// tools/landing_gear_bay_function.py can render each feature ALONE and report
// its clash with the wing, spar and root flange per feature.  bay() unions /
// subtracts exactly these, so the printed part is unchanged by the split
// (gated: rendered volume identical before and after).
// ---------------------------------------------------------------------------

// Clevis ears astride the thigh lug (carry both pins)
module bay_clevis_ears() {
    for (s = [-1, 1])
        translate([0, s * (LUG_W / 2 + EAR_CLR + EAR_T / 2), 0])
            hull() {
                ycyl([0, 0, 0], EAR_T, HUB_D + 5);
                ycyl(STOP_PIN_R * azv(STOP_PIN_AZ), EAR_T,
                     PIN_D + 4);
                translate([BAY_BACK_X + 1, -EAR_T / 2, -9])
                    cube([2, EAR_T, 24]);
            }
}

// Wire bosses on riser wedges at each chord's far end
module bay_wire_bosses() {
    for (i = [0 : 3]) {
        st = w_seat(i);
        m = boss_mouth(i);
        // Plain boss along the chord.  Rev R6 hulled each boss down to
        // a "riser root on the canted plate plane" -- a 2 mm cube
        // parked at BAY_BACK_X.  That plane was solid plate then; since
        // LG-10.3 cut the wells open it is the middle of the OPEN
        // aperture, so the riser rooted in nothing and the bosses came
        // out as free-floating bodies.  The load path is now real: the
        // carrier slab crosses every boss over its full length and
        // lands in both liner side walls, which are continuous with
        // the bolt flange.  Nothing is hulled to a datum any more.
        translate(m - BAY_CARRIER_T / 2 * azv(w_chord(i)))
            rotate([0, 90 - w_chord(i), 0])
                cylinder(h = st + 3 + BAY_CARRIER_T / 2, d = BOSS_OD);
    }
}

// Wire seats: blind bores into each boss along the chord.  These are the
// FUNCTIONAL surfaces of the spring/ductile energy absorber -- a relief may
// never cut them (BHD-02).
module bay_wire_seats() {
    for (i = [0 : 3]) {
        wd = w_d(i);
        st = w_seat(i);
        translate(boss_mouth(i) - 0.1 * azv(w_chord(i)))
            rotate([0, 90 - w_chord(i), 0])
                cylinder(h = st + 0.2, d = wd + SOCK_CLR);
        // FREE-SPAN RELIEF (found 2026-10-10, tools/landing_gear_bay_function.py
        // wires x bay = 277 mm^3 at every corner): the boss is centred on the
        // carrier slab, so its root starts BAY_CARRIER_T/2 = 6 mm BEFORE the
        // seat mouth -- inside the wire's free span.  ~4.8 mm of each wire ran
        // through solid boss + carrier, a quarter of the 20 mm bow span the
        // absorber flexes over.  Counterbore the root back to the carrier's
        // near face, 1.5 mm over the seat bore; the seat itself (st beyond the
        // mouth) is untouched, so the boss bearing margin is unchanged.
        translate(boss_mouth(i) - (BAY_CARRIER_T / 2 + 0.5) * azv(w_chord(i)))
            rotate([0, 90 - w_chord(i), 0])
                cylinder(h = BAY_CARRIER_T / 2 + 0.5, d = wd + SOCK_CLR + 1.5);
    }
}

// BOW RELIEF (2026-10-11): the wire's bow sweeps sideways in the swing plane;
// 4.5-7 mm before the boss mouth it is already 2.4 mm (rest) to 4.0 mm (full
// stroke) off the chord -- more than the straight free-span counterbore allows
// (wires x bay 20 / 57 mm^3 in the census).  Cut the envelope of the wire at
// full-stroke bow + 0.5 mm, O d + 1.0, but ONLY between the two socket mouths:
// the seats beyond each mouth keep their tight bore.
module bay_bow_relief() {
    for (i = [0 : 3]) {
        h = (w_spring(i) ? H_DEF_SPRING : H_DEF_DUCT) + 0.5;
        span = w_l(i) - 2 * w_seat(i);               // mouth to mouth
        intersection() {
            translate(crank_socket(i) + (w_l(i) / 2 - w_seat(i)) * azv(w_chord(i)))
                rotate([0, 90 - w_chord(i), 0])
                    bowed_wire(w_d(i) + 1.0, w_l(i), h, w_seat(i) + END_RUN_IN);
            // the free span only, mouth + 0.1 .. mouth - 0.1, as a fat slab
            translate(crank_socket(i) + 0.1 * azv(w_chord(i)))
                rotate([0, 90 - w_chord(i), 0])
                    translate([-30, -30, 0]) cube([60, 60, span - 0.2]);
        }
    }
}

// 4x M3 shell mounting through-bolts.  d = BAY_M3_D for the clearance hole;
// a larger d gives a fastener keep-out (head / nut / tool access).
module bay_bolts(d) {
    translate([BAY_BACK_X, 0, 12]) rotate([0, -BAY_CANT, 0])
        for (i = [0 : 1])
            for (s = [-1, 1])
                translate([-4.1, s * BAY_BOLT_YB[i], BAY_BOLT_ZB[i]])
                    rotate([0, 90, 0])
                        cylinder(h = BAY_PLATE_T + 8.2, d = d);
}

// Every positive of the bay except the cowl (flange + liner): clevis ears,
// gussets, boss carrier, wire bosses, retention pads.  Split out 2026-10-10
// so the conforming-bay generator can union them with its own flange.
module bay_body() {
    boss_carrier();
    clevis_gussets();
    for (i = [0 : 3])
        retention_pad(i, false);
    // Clevis ears astride the thigh lug (carry both pins)
    bay_clevis_ears();
    // Wire bosses along each chord (see bay_wire_bosses)
    bay_wire_bosses();
}

// Every cut of the bay except the 4 M3 bolts (which the generator places per
// corner, because a corner may relocate one -- BHD-02 / TACCO chin pouch).
module bay_cuts() {
    // Hip pin bore through both ears
    ycyl([0, 0, 0], LUG_W + 2 * (EAR_CLR + EAR_T) + 0.2, PIN_D);
    // Extension-stop cross-pin bore through both ears
    ycyl(STOP_PIN_R * azv(STOP_PIN_AZ),
         LUG_W + 2 * (EAR_CLR + EAR_T) + 0.2, PIN_D);
    // Wire seats: blind bores into each boss along the chord
    bay_wire_seats();
    // Bow sweep relief through the carrier / boss roots (free span only)
    bay_bow_relief();
    // LG-13 retention tap pilots + counterbores
    for (i = [0 : 3])
        retention_pad(i, true);
}

// Flange OUTLINE as a prism x0..x1 (plate frame, measured out from the back
// face): the plate trapezoid minus the aperture bore, the open mouth and the
// thigh notch -- i.e. exactly where bay_cowl() puts flange material, but
// extruded through any depth.  The conforming generator intersects this with
// the skin layer to get the flange.
module bay_flange_outline(x0, x1) {
    z0 = BAY_APER_ZB0 - BAY_PLATE_ZB0;
    z1 = z0 + BAY_APER_L;
    iw_bot = COWL_W_BOT - 2 * COWL_T;
    iw_top = COWL_W_TOP - 2 * COWL_T;
    translate([BAY_BACK_X, 0, 12])
        rotate([0, -BAY_CANT, 0])
            translate([0, -BAY_PLATE_W / 2, BAY_PLATE_ZB0])
                difference() {
                    trap_prism(BAY_PLATE_WB, BAY_PLATE_W, 0, BAY_PLATE_L, x0, x1);
                    trap_prism(iw_bot, iw_top, z0 + COWL_T, z1 - COWL_T,
                               x0 - 0.1, x1 + 0.1);
                    translate([x0 - 0.1, BAY_PLATE_W / 2 - iw_bot / 2, z0 - 0.1])
                        cube([x1 - x0 + 0.2, iw_bot, COWL_T + 0.2]);
                    translate([x0 - 0.1, BAY_PLATE_W / 2 - BAY_NOTCH_W / 2, -0.1])
                        cube([x1 - x0 + 0.2, BAY_NOTCH_W, z0 + 0.1]);
                }
}

// Liner OUTLINE as a prism x0..x1 (plate frame): the aperture-wall ring the
// liner occupies (outer face = aperture, bore = aperture - 2 COWL_T, open at
// the mouth).  The conforming generator intersects it with a skin-following
// layer BAY_PLATE_T + COWL_H deep, so the liner runs from the skin inboard
// through the collar whatever the local curvature.
module bay_liner_outline(x0, x1) {
    z0 = BAY_APER_ZB0 - BAY_PLATE_ZB0;
    z1 = z0 + BAY_APER_L;
    iw_bot = COWL_W_BOT - 2 * COWL_T;
    iw_top = COWL_W_TOP - 2 * COWL_T;
    translate([BAY_BACK_X, 0, 12])
        rotate([0, -BAY_CANT, 0])
            translate([0, -BAY_PLATE_W / 2, BAY_PLATE_ZB0])
                difference() {
                    trap_prism(COWL_W_BOT, COWL_W_TOP, z0, z1, x0, x1);
                    trap_prism(iw_bot, iw_top, z0 + COWL_T, z1 - COWL_T,
                               x0 - 0.1, x1 + 0.1);
                    translate([x0 - 0.1, BAY_PLATE_W / 2 - iw_bot / 2, z0 - 0.1])
                        cube([x1 - x0 + 0.2, iw_bot, COWL_T + 0.2]);
                }
}

module bay() {
    difference() {
        union() {
            bay_cowl();
            bay_body();
        }
        bay_cuts();
        // 4x M3 shell mounting through-bolts (internal backing plate: LG-02)
        bay_bolts(BAY_M3_D);
        // NOTE: no thigh-sweep sector cut here -- rim-vs-thigh clearance is
        // verified numerically (tools/landing_gear_cowl_clearance.py,
        // tools/landing_gear_bay_function.py).
        // NOTE: this flat-backed bay is the DESIGN SOURCE.  The printed bay
        // is the CONFORMING part built from it per corner by
        // tools/generate_lg_bays.py (owner decision 2026-10-10, BHD-02): the
        // flange follows the skin, so the flat seat datum below no longer
        // places the printed flange.
    }
}

// ---------------------------------------------------------------------------
// MODULE: leg_moving(flex) -- leg frame + foot as one rigid group, rotated
// flex deg into flexion about the hip pin (foot swings up-outboard).
// ---------------------------------------------------------------------------
// cf_core inserts (procured, not printed): CF rods + steel cross-pins.
module thigh_cf_inserts() {
    axis = KNEE / norm(KNEE);
    perp = [-axis[2], 0, axis[0]];
    for (s = [-1, 1]) {
        color([0.05, 0.05, 0.05])
            rod_between(CF_ROD_START * axis + s * THIGH_CYL_C / 2 * perp,
                        KNEE + 2 * axis + s * THIGH_CYL_C / 2 * perp, CF_ROD_D);
        color("Silver")
            ycyl(CF_PIN_AT * axis + s * THIGH_CYL_C / 2 * perp, LUG_W, CF_PIN_D);
    }
}

LEG_ALPHA = 0.95;           // render-only: <1 shows the CF core through the frame

module leg_moving(flex) {
    rotate([0, -flex, 0]) {
        color("DimGray", LEG_ALPHA) leg_frame();
        if (THIGH_VARIANT == "cf_core") thigh_cf_inserts();
        // foot: print frame -> assembly (sole at GROUND_Z, toe +X outboard)
        color([0.15, 0.15, 0.15], 0.95)
            translate([ANKLE[0], ANKLE[1], GROUND_Z]) foot();
    }
}

// ---------------------------------------------------------------------------
// MODULE: leg_assembly(flex, h_duct, h_spring)
// Complete corner: bay + leg at flexion angle + all 4 wires.
// ---------------------------------------------------------------------------
module leg_assembly(flex = 0, h_duct = H_NOM, h_spring = H_NOM) {
    color("OliveDrab", 0.8) bay();
    leg_moving(flex);
    for (i = [0 : 3])
        color(w_spring(i) ? "Goldenrod" : "FireBrick")
            posed_wire(i, w_spring(i) ? h_spring : h_duct);
}

// ---------------------------------------------------------------------------
// Hull-frame corner placement (verification view only -- final placements
// are LG-10).  Hull frame: X=+port, Y=+aft, Z=+dorsal; centreline
// X=-169.9; cargo belly Z=0; ground plane Z=-80.
// Corner format: [hip_x, hip_y, hip_z, swing_azimuth_deg, hand]
//   swing azimuth: direction of foot from hip in plan, deg from hull +X
//   (port-outboard); fore legs swing fore-of-outboard, aft legs aft-of-
//   outboard.  The AFT feet land within 5 mm of the canonical QMx stations;
//   the FORE feet no longer do -- the 2026-10-10 station move (BHD-02) put
//   them at Y -46.5, 129 mm off the centreline (were -31.8 / 140).
// ---------------------------------------------------------------------------
X_CL = -169.9;
CORNERS = [
    // [hip_x, hip_y, hip_z, swing_azimuth_deg, hand] -- hand +1 = port part,
    // -1 = starboard part, the MIRROR image of port (owner 2026-10-10,
    // BHD-02: distinct mirrored port/starboard bays, not one part rotated).
    // A starboard row is the port row mirrored about X_CL: x -> 2 X_CL - x,
    // az -> 180 - az, and the part itself mirrored in leg-local y.
    //
    // FORE station moved 2026-10-10 (BHD-02; owner chose the "hybrid", study
    // SS10-11): hip Y -16, X re-solved so the seat lands at the old depth (seat
    // median -0.14 mm, plate frame).  Was [-103.87, -1.28] / [-235.93, -1.28]:
    // there the fore bays sat inside the bonded wing-root flange and on the CF
    // spar.  At Y -16 the bay is off the spar, the wing and the TACCO chin
    // pouch, 92 % of its footprint is on the hull, and the remaining 511 mm^3
    // into the flange is cleared by a notch in the flange (FOS 16.1).  Y -38
    // was rejected: a third of the footprint is off the hull there.
    // AFT rows: hip stations RECESSED 15 mm along each corner's own swing
    // axis (LG-10.2); pre-recess [-79, 107], [-260.8, 107].
    [-114.90, -16.00, 38,  -22.4,  1 ],   // fore-port
    [-224.90, -16.00, 38, -157.6, -1 ],   // fore-stbd  (mirror of fore-port)
    [ -92.24,  99.96, 38,   28.0,  1 ],   // aft-port
    [-247.56,  99.96, 38,  152.0, -1 ],   // aft-stbd   (mirror of aft-port)
];

// All 4 corners, gear only (no ground/ghost slabs) -- consumed by
// airframe/FreeCAD-scripts/serenity_assembly.py as the landing-gear
// component until the LG-10 FreeCAD bake finalizes placements.
module hull_legs() {
    for (c = CORNERS)
        translate([c[0], c[1], c[2]])
            rotate([0, 0, c[3]])
                mirror([0, c[4] < 0 ? 1 : 0, 0])
                    leg_assembly(0);
}

module hull_stance() {
    // ground plane
    color("Tan", 0.25) translate([-360, -120, -81]) cube([380, 380, 1]);
    // cargo-belly footprint ghost
    color("SaddleBrown", 0.12) translate([-267, -69.5, 0])
        cube([194.3, 198.5, 2]);
    hull_legs();
}

// ---------------------------------------------------------------------------
// PART selector (print orientations noted per part)
// ---------------------------------------------------------------------------
if (PART == "leg_frame") {
    // Print lying on the -Y face (swing-plane bending in the layer plane)
    translate([0, 0, SHIN_T / 2]) rotate([-90, 0, 0]) leg_frame();
} else if (PART == "foot") {
    foot();                              // already sole-down print frame
} else if (PART == "bay") {
    // Print: canted plate back face down
    rotate([0, BAY_CANT, 0]) translate([-BAY_BACK_X + 1, 0, 0]) bay();
} else if (PART == "spring_wire_nominal") {
    bowed_wire(SPRING_D, SPRING_L, H_NOM);
} else if (PART == "spring_wire_deformed") {
    bowed_wire(SPRING_D, SPRING_L, H_DEF_SPRING);
} else if (PART == "ductile_wire_nominal") {
    bowed_wire(DUCTILE_D, DUCTILE_L, H_NOM);
} else if (PART == "ductile_wire_deformed") {
    bowed_wire(DUCTILE_D, DUCTILE_L, H_DEF_DUCT);
} else if (PART == "leg_assembled") {
    leg_assembly(0);
} else if (PART == "leg_deformed") {
    leg_assembly(FLEX_DEG, H_DEF_DUCT, H_DEF_SPRING);
} else if (PART == "hull_legs") {
    hull_legs();
} else if (PART == "hull_stance") {
    hull_stance();
} else if (PART == "none") {
    // library mode: emit nothing, so a context file can include this one and
    // pose bay() / leg_moving() itself (tools/landing_gear_bay_function.py)
} else {
    assert(false, str("Unknown PART: ", PART));
}
