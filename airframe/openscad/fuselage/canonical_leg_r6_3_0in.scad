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
// -- 3.0 in (80 mm) BELLY CLEARANCE VARIANT (extended, rough-field option) --
// ===========================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// AI note : Authored by Claude (model: Claude Fable 5, Anthropic) under the
//           author's direction, 2026-07-21.  Per AGENTS.md AI attribution.
//           Split into the 1.5in / 3.0in named variants 2026-07-23 (same
//           attribution).
// Project : Serenity-class Tilt-Rotor UAV (24-inch scale, Firefly TV ship)
// License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
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
//      box underneath the parked aircraft.  THIS FILE is the extended
//      3.0 in (80 mm) variant, kept for rough-field / extra-margin
//      missions -- it is the original Rev R6 design point (2026-07-21)
//      and the reference the wire schedule is solved against.  The
//      compact 1.5 in (38.1 mm) default variant is
//      `canonical_leg_r6_1_5in.scad`.  Both share the identical
//      bay/foot/wire BOM; only the printed leg-frame length differs.
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
STOP_PIN_AZ  = 118;         // pin centre azimuth in XZ (deg from +X)
STOP_PIN_R   = 8.0;         // pin centre radius from hip axis
STOP_TAB_AZ1 = 131;         // thigh tab sector start (contact face)
STOP_TAB_AZ2 = 146;         // thigh tab sector end

// Bellcrank wire sockets (in the thigh root, around the pin)
CRANK_R      = 6.0;         // socket centre radius from pin axis
CRANK_AZ     = -22;         // socket azimuth in XZ (deg from +X; down-outboard)
CHORD_AZ     = 68;          // wire chord direction (deg from +X; up the bay wall)
WIRE_STAGGER = 3.5;         // socket pitch along pin axis Y
                            // ductile pair at Y +/-1.75, spring pair at Y +/-5.25

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
THIGH_CYL_D  = 14.0;        // main cylinder OD
THIGH_CYL_C  = 18.0;        // main cylinder centre spacing (in swing plane)
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

// Bay plate.  LG-10 (2026-08-09): the original surface-mount assumption was
// measured against the baked cargo skin and does NOT hold -- the back face
// floated 14-17 mm outboard of the hull at hip height, BAY_CANT leaned the
// plate the WRONG WAY (the real flank leans outboard going up, not inboard),
// and the flank is doubly curved with 15-42 mm of deviation across the
// footprint.  See tools/landing_gear_bay_pad_fit.py for the measurements.
//
// The back face is therefore CONFORMING: the plate is cut against a local
// hull-surface patch (BAY_STATION selects fore/aft), so it seats on the real
// skin.  Because the fore and aft flanks are different surfaces this makes the
// bay TWO geometries, each a mirrored pair -- not one shared part.
BAY_STATION  = "aft";       // "fore" | "aft" -- selects the hull patch AND
                            // the back-face datum (they differ by 8.7 mm)
BAY_CONFORM  = false;       // true once tools/build_bay_hull_patches.py has run
BAY_PATCH_DIR = "../../../stls/fuselage/landing-gear";

BAY_PLATE_T  = 5.0;         // frame thickness -- MUST be assigned before
                            // BAY_BACK_X below, which reads it (OpenSCAD
                            // resolves top-level assignments in order;
                            // a forward reference silently yields undef
                            // and the whole part renders displaced).

// Back-face datum, PER STATION.  tools/landing_gear_bay_station_fit.py measures
// the outboard skin along the SS2.4a panel normal at each canonical hip:
// (measured AFTER the LG-10.2 15 mm hip recess, which is what the frame has to
// seat against):
//   fore  +12.6 mm from the hip        aft  +5.4 mm from the hip
// (port/stbd mirror to 2.3 mm fore, 0.9 mm aft -- so the split is fore/aft, not
// left/right; each value is the mean of its two sides).  The frame's OUTER face
// must land on that skin, and the outer face sits BAY_PLATE_T out from the
// datum, so datum = standoff - thickness.  The old shared -8.0 seated at
// neither station.  Pre-recess the same measurement read +1.17 / -7.53 mm --
// i.e. the hips sat ON the skin, which is why the bay could not close.
BAY_STANDOFF = (BAY_STATION == "fore") ? 12.6 : 5.4;
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

// Thigh-side socket MOUTH centre for a wire at stagger y
function crank_socket(y) = CRANK_R * azv(CRANK_AZ) + [0, y, 0];

// Bay boss bore MOUTH centre for a wire of stock length l seated `seat`
// deep at both ends: exposed span between mouths = l - 2*seat
function boss_mouth(l, seat, y) = crank_socket(y) + (l - 2 * seat) * azv(CHORD_AZ);

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

// A wire posed in the leg-local frame, SEATED: the stock runs from `seat`
// deep inside the thigh socket, along the chord (azimuth CHORD_AZ in XZ),
// to `seat` deep inside its bay boss bore.  Bow bulges in-plane.
module posed_wire(l, seat, y, d, h) {
    a = crank_socket(y);
    translate(a + (l / 2 - seat) * azv(CHORD_AZ))
        rotate([0, 90 - CHORD_AZ, 0])       // local +Z -> chord direction
            rotate([0, 0, 90])              // bow bulge into the swing plane
                bowed_wire(d, l, h, seat + END_RUN_IN);
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
            // Square foot spigot: ankle disc rim down into the foot socket
            translate([ANKLE[0], ANKLE[1], ANKLE[2] - 9.75])
                cube([FOOT_SPIG, FOOT_SPIG, 9.5], center = true);
        }
        // LG-18: axial bore through each main thigh cylinder.  Starts past the
        // root lug blend (which carries the hip moment into the cluster) and
        // stops short of the knee, so the loaded ends stay solid.  Printed
        // lying on the -Y face the bore axis is horizontal -- a Ø6 bridge.
        if (THIGH_BORE_D > 0)
            for (s = [-1, 1])
                rod_between(20 * axis + s * THIGH_CYL_C / 2 * perp,
                            KNEE - 6 * axis + s * THIGH_CYL_C / 2 * perp,
                            THIGH_BORE_D);
        // Hip pin bore
        ycyl([0, 0, 0], LUG_W + 0.2, PIN_D);
        // 4 bellcrank wire sockets: bore along the chord, into the root
        for (i = [0 : 3]) {
            y = (i - 1.5) * WIRE_STAGGER;
            spring = (abs(y) > 3);                      // outer=spring
            wd = spring ? SPRING_D : DUCTILE_D;
            seat = spring ? SPRING_SEAT : DUCTILE_SEAT;
            a = crank_socket(y);
            translate(a + 0.1 * azv(CHORD_AZ))
                rotate([0, 90 - CHORD_AZ, 0])
                    translate([0, 0, -seat - 0.1])
                        cylinder(h = seat + 0.2, d = wd + SOCK_CLR);
        }
        // Wire-chord relief scallop across the root's up-outboard shoulder
        // (guarantees the chords' first 14 mm clear the lug blend)
        for (i = [0 : 3]) {
            y = (i - 1.5) * WIRE_STAGGER;
            a = crank_socket(y);
            translate(a) rotate([0, 90 - CHORD_AZ, 0])
                cylinder(h = 14, d = DUCTILE_D + 2.5);
        }
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

module bay_cowl() {
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
                        // bolt flange slab, full plate outline
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
module retention_pad(y, spring, cut) {
    l    = spring ? SPRING_L : DUCTILE_L;
    st   = spring ? SPRING_SEAT : DUCTILE_SEAT;
    dep  = spring ? RET_DEPTH_S : RET_DEPTH_D;
    m    = boss_mouth(l, st, y);
    // step `dep` INTO the boss along the chord, then go radial (+Z-ish in the
    // swing plane, i.e. perpendicular to the chord, clear of the neighbours).
    seat = m + dep * azv(CHORD_AZ);
    translate(seat) rotate([0, 90 - CHORD_AZ, 0]) rotate([0, 90, 0])
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
    m = boss_mouth(DUCTILE_L, DUCTILE_SEAT, 0);
    translate(m + ((DUCTILE_SEAT + 3) / 2 - BAY_CARRIER_T / 4)
                 * azv(CHORD_AZ))
        rotate([0, 90 - CHORD_AZ, 0])
            cube([BAY_CARRIER_H, BAY_CARRIER_W, BAY_CARRIER_T], center = true);
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

module bay() {
    difference() {
        union() {
            bay_cowl();
            boss_carrier();
            clevis_gussets();
            for (i = [0 : 3]) {
                y = (i - 1.5) * WIRE_STAGGER;
                retention_pad(y, abs(y) > 3, false);
            }
            // NOTE: the bolt flange is emitted by bay_cowl() above, together
            // with the liner, as one union-then-bore solid.  Rev R6 had a
            // separate solid plate here with a "recess pocket" that removed
            // ZERO material -- it was translated to plate-local
            // x = BAY_PLATE_T, i.e. entirely outside the 5 mm plate it
            // claimed to pocket.  See LG-18.
            // Clevis ears astride the thigh lug (carry both pins)
            for (s = [-1, 1])
                translate([0, s * (LUG_W / 2 + EAR_CLR + EAR_T / 2), 0])
                    hull() {
                        ycyl([0, 0, 0], EAR_T, HUB_D + 5);
                        ycyl(STOP_PIN_R * azv(STOP_PIN_AZ), EAR_T,
                             PIN_D + 4);
                        translate([BAY_BACK_X + 1, -EAR_T / 2, -9])
                            cube([2, EAR_T, 24]);
                    }
            // Wire bosses on riser wedges at each chord's far end
            for (i = [0 : 3]) {
                y = (i - 1.5) * WIRE_STAGGER;
                spring = (abs(y) > 3);
                l = spring ? SPRING_L : DUCTILE_L;
                st = spring ? SPRING_SEAT : DUCTILE_SEAT;
                m = boss_mouth(l, st, y);
                // Plain boss along the chord.  Rev R6 hulled each boss down to
                // a "riser root on the canted plate plane" -- a 2 mm cube
                // parked at BAY_BACK_X.  That plane was solid plate then; since
                // LG-10.3 cut the wells open it is the middle of the OPEN
                // aperture, so the riser rooted in nothing and the bosses came
                // out as free-floating bodies.  The load path is now real: the
                // carrier slab crosses every boss over its full length and
                // lands in both liner side walls, which are continuous with
                // the bolt flange.  Nothing is hulled to a datum any more.
                translate(m - BAY_CARRIER_T / 2 * azv(CHORD_AZ))
                    rotate([0, 90 - CHORD_AZ, 0])
                        cylinder(h = st + 3 + BAY_CARRIER_T / 2, d = BOSS_OD);
            }
        }
        // Hip pin bore through both ears
        ycyl([0, 0, 0], LUG_W + 2 * (EAR_CLR + EAR_T) + 0.2, PIN_D);
        // Extension-stop cross-pin bore through both ears
        ycyl(STOP_PIN_R * azv(STOP_PIN_AZ),
             LUG_W + 2 * (EAR_CLR + EAR_T) + 0.2, PIN_D);
        // Wire seats: blind bores into each boss along the chord
        for (i = [0 : 3]) {
            y = (i - 1.5) * WIRE_STAGGER;
            spring = (abs(y) > 3);
            l = spring ? SPRING_L : DUCTILE_L;
            wd = spring ? SPRING_D : DUCTILE_D;
            st = spring ? SPRING_SEAT : DUCTILE_SEAT;
            translate(boss_mouth(l, st, y) - 0.1 * azv(CHORD_AZ))
                rotate([0, 90 - CHORD_AZ, 0])
                    cylinder(h = st + 0.2, d = wd + SOCK_CLR);
        }
        // 4x M3 shell mounting through-bolts (internal backing plate: LG-02)
        translate([BAY_BACK_X, 0, 12]) rotate([0, -BAY_CANT, 0])
            for (i = [0 : 1])
                for (s = [-1, 1])
                    translate([-4.1, s * BAY_BOLT_YB[i], BAY_BOLT_ZB[i]])
                        rotate([0, 90, 0])
                            cylinder(h = BAY_PLATE_T + 8.2, d = BAY_M3_D);
        // LG-13 retention tap pilots + counterbores
        for (i = [0 : 3]) {
            y = (i - 1.5) * WIRE_STAGGER;
            retention_pad(y, abs(y) > 3, true);
        }
        // NOTE: no thigh-sweep sector cut here.  The leg already exits through
        // the cowl rim's hollow interior, and an xz_sector centred on the hip
        // reaches the plate itself at large radius (the plate spans s -34..+48,
        // i.e. radius ~50 across the very azimuths the thigh sweeps), so it
        // gouged the plate open rather than notching the rim.  Rim-vs-thigh
        // clearance is verified numerically instead -- see
        // tools/landing_gear_cowl_clearance.py.
        // Conforming back face (LG-10).  The plate is cut against a local
        // hull-surface patch so it seats on the real, doubly-curved flank.
        // Patches are generated by tools/build_bay_hull_patches.py; until they
        // exist the part still renders as the nominal flat-backed plate.
        if (BAY_CONFORM)
            import(str(BAY_PATCH_DIR, "/lg_r6_hull_patch_", BAY_STATION,
                       ".stl"), convexity = 6);
    }
}

// ---------------------------------------------------------------------------
// MODULE: leg_moving(flex) -- leg frame + foot as one rigid group, rotated
// flex deg into flexion about the hip pin (foot swings up-outboard).
// ---------------------------------------------------------------------------
module leg_moving(flex) {
    rotate([0, -flex, 0]) {
        color("DimGray", 0.95) leg_frame();
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
    for (i = [0 : 3]) {
        y = (i - 1.5) * WIRE_STAGGER;
        spring = (abs(y) > 3);
        color(spring ? "Goldenrod" : "FireBrick")
            posed_wire(spring ? SPRING_L : DUCTILE_L,
                       spring ? SPRING_SEAT : DUCTILE_SEAT, y,
                       spring ? SPRING_D : DUCTILE_D,
                       spring ? h_spring : h_duct);
    }
}

// ---------------------------------------------------------------------------
// Hull-frame corner placement (verification view only -- final placements
// are LG-10).  Hull frame: X=+port, Y=+aft, Z=+dorsal; centreline
// X=-169.9; cargo belly Z=0; ground plane Z=-80.
// Corner format: [hip_x, hip_y, hip_z, swing_azimuth_deg]
//   swing azimuth: direction of foot from hip in plan, deg from hull +X
//   (port-outboard); fore legs swing fore-of-outboard, aft legs aft-of-
//   outboard, feet landing within 5 mm of the canonical QMx stations.
// ---------------------------------------------------------------------------
X_CL = -169.9;
CORNERS = [
    // Hip stations RECESSED 15 mm along each corner's own swing axis (LG-10.2).
    // Pre-recess: [-90, -7], [-249.8, -7], [-79, 107], [-260.8, 107].
    // Feet are UNCHANGED by the recess -- that is the point of translating
    // along the swing axis rather than the panel normal.
    [-103.87,  -1.28, 38,  -22.4 ],   // fore-port
    [-235.93,  -1.28, 38, -157.6 ],   // fore-stbd  (mirror)
    [ -92.24,  99.96, 38,   28.0 ],   // aft-port
    [-247.56,  99.96, 38,  152.0 ],   // aft-stbd   (mirror)
];

// All 4 corners, gear only (no ground/ghost slabs) -- consumed by
// airframe/FreeCAD-scripts/serenity_assembly.py as the landing-gear
// component until the LG-10 FreeCAD bake finalizes placements.
module hull_legs() {
    for (c = CORNERS)
        translate([c[0], c[1], c[2]])
            rotate([0, 0, c[3]])
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
} else {
    assert(false, str("Unknown PART: ", PART));
}
