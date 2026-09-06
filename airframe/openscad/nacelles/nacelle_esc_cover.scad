// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Nacelle-local print frame: duct axis = local +Z, intake at Z = 0.  The
//   cover is authored IN PLACE — at the radius and azimuth it occupies on the
//   pod — so that its outer face is the pod's own measured mould line and not an
//   approximation of it.  Re-orient for printing at the slicer, not here; see
//   PRINT ORIENTATION below.
// ===========================================================================
// =============================================================================
// nacelle_esc_cover.scad — Rev T4c — hinged-ESC bay access cover
// =============================================================================
//
// Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// Analysis and code by Claude (Claude Opus 5, Anthropic) under the author's
//           direction, per AGENTS.md §3 "Attribution and Licensing"
// License : CC BY 4.0  <https://creativecommons.org/licenses/by/4.0/>
// Date    : 2026-09-01
//
// WHY THERE IS A COVER AT ALL
// ---------------------------
// Rev T4b hollowed the pod, which is what created the annulus the ESCs live in.
// But a hollow annulus is a SEALED annulus: a folded board 33 mm across cannot
// be threaded in through a vent hole, and there is no split line to open.  So
// each bay is cut radially through the skin and this part closes it.
//
// That is a real structural cost and it is not hidden: two 62 × ~35 mm windows,
// 180° apart, in the pod's principal bending section.  The cover buys most of it
// back the way an aircraft access panel does — it is a bolted doubler, landing
// on a band of added material and clamped by six M3 into heat-set inserts, so
// load crosses the joint in shear through the fasteners rather than round the
// hole.  `tools/nacelle_esc_bay_fit.py` reports the section modulus with and
// without the windows.
//
// WHY IT IS AUTHORED IN PLACE
// ---------------------------
// The outer face IS the canonical mould line, taken from the same ray-cast skin
// grid the pod's cavity and rebate are built from
// (`nacelle_hollow_profile.scad`).  Anything else — a cylinder, a lofted patch,
// a re-measured surface — would leave a step at the joint, at the widest station
// of the nacelle, in the boundary layer.  Building it from the pod's own
// measurement is the only way the two are guaranteed to agree.
//
// HANDING — there are FOUR of these, and they are four different shapes.
// The shell is not axisymmetric, so the bay at azimuth 69° and the bay at 249°
// sit on different surface, and port and starboard are mirror images rather than
// copies.  Render all four; do not print two and mirror them in the slicer.
//
// PRINT ORIENTATION — inner (concave) face DOWN.
// The cover is a shallow arc: about 51 mm across the fold with roughly 4.4 mm of
// sagitta.  Laid concave-side-down the two long edges touch the bed and the
// middle arches up 4.4 mm, which the printer bridges; the OUTER face is then
// uppermost and gets the best surface, which is the one that matters because it
// is the mould line.  Laid the other way up the part balances on a line contact
// and the first layers are unsupported.
//   Layer lines run ACROSS the cover's width.  Analogy: layer lines are the
//   grain in wood — strong along the layers, splittable between them.  Here the
//   load is the fastener clamp plus air pressure, both normal to the face, so
//   the grain direction is not critical; but do NOT stand the cover on edge to
//   avoid the bridge, because that puts the grain across the screw bosses.
//
// References
// ----------
//   [1] tools/nacelle_esc_bay_fit.py — the measured fit that sized the bay.
//   [2] nacelle_esc_bay.scad — the shared bay interface; every dimension the
//       cover and the pod must agree on lives there, once.
//   [3] Open-Secure-ESC isolation_envelope.py — why the board is 33 mm and
//       cannot be narrowed.
// =============================================================================

include <nacelle_hollow_profile.scad>
use <nacelle_shell_grid.scad>
include <nacelle_esc_bay.scad>

// ── Render selectors ─────────────────────────────────────────────────────────
// ** NACELLE_SIDE IS INVERTED RELATIVE TO THE FILENAME, and it will catch you. **
// The Rev R1 nacelle-swap (2026-06-11) renamed the pod outputs to match their
// PHYSICAL mounting side without changing the selector that picks the shell, so
//     nacelle_port_revs.stl  is rendered with NACELLE_SIDE = -1  (right shell)
//     nacelle_stbd_revs.stl  is rendered with NACELLE_SIDE = +1  (left shell)
// A cover MUST be rendered with the same NACELLE_SIDE as the pod it closes.
// Building it on the other shell is not a cosmetic error: the two canonical
// shells differ by a few tenths of a millimetre, and measured mesh-against-mesh
// that mismatch put 442 mm3 of cover INSIDE the pod, all of it round the
// perimeter where the cover lands.  See the render commands at the foot of this
// file, and gate T9 in tools/nacelle_esc_bay_fit.py, which now checks it.
NACELLE_SIDE = -1;   // -1 => PORT pod (right shell); +1 => STBD pod (left shell)
RENDER_BAY   =  0;   // 0 = bay at ESC_BAY_AZ[0], 1 = bay at ESC_BAY_AZ[1]

$fn = 72;

COVER_SKIN = (NACELLE_SIDE > 0) ? HOLLOW_SKIN_PORT : HOLLOW_SKIN_STBD;
COVER_AZ   = ESC_BAY_AZ[RENDER_BAY];


// ── Module: cover_shell ──────────────────────────────────────────────────────
// The material between the mould line and one cover thickness inside it.
module cover_shell(d_out, d_in) {
    difference() {
        grid_solid(offset_grid(COVER_SKIN, d_out), HOLLOW_Z, HOLLOW_N_AZ);
        grid_solid(offset_grid(COVER_SKIN, d_in), HOLLOW_Z, HOLLOW_N_AZ);
    }
}


// ── Module: cover_louvre_field ───────────────────────────────────────────────
// The circuit's INLET, and it is AFT-ONLY.
//
// This comment has been wrong twice, and it is worth saying why, because the
// geometry barely changed — only the understanding of which way air moves.
// First it was "a route and an area", with no flow sized at all.  Then it was
// the OUTLET of a duct bleed, on the belief that the inter-stage ran above
// ambient.  It does not: every station inside this duct is at or below ambient
// and the aft fan's inlet sits 2781 Pa below it, so the fan ASPIRATES the bay.
//
// Slots at BOTH ends, which is what the first version had, short-circuit the
// circuit: the forward field sat directly over the discharge ports at Z 76-88,
// so air would enter and leave again without ever crossing the board.  One field
// at the AFT end forces the full-length traverse.
//
// ESC_LOUVRE_W = 1.2 mm now answers to two criteria at once: two extrusions at a
// 0.6 mm nozzle, and the coarse FOD limit.  The fine limit is the bonded screen.
function cover_louvre_span() = (ESC_LOUVRE_N - 1) * ESC_LOUVRE_P + ESC_LOUVRE_W;
function cover_louvre_z0()   = ESC_BAY_Z1 - ESC_LEDGE_W / 2 - cover_louvre_span();

module cover_louvres() {
    for (i = [0 : ESC_LOUVRE_N - 1])
        rotate([0, 0, COVER_AZ + esc_a_pow()])
            translate([ESC_MOUNT_R,
                       -ESC_LOUVRE_L / 2,
                       cover_louvre_z0() + i * ESC_LOUVRE_P])
                cube([40, ESC_LOUVRE_L, ESC_LOUVRE_W]);
}


// ── Module: cover_mesh_rebate ────────────────────────────────────────────────
// A shallow pocket in the cover's INNER face for the bonded FOD screen.
//
// The screen is a consumable and the cover is a cheap printed part, so it is
// bonded rather than clamped: a clamped screen wants its own retainer and eight
// more fasteners, for a part that is replaced by reprinting the cover.
//
// Depth 0.6 mm against a ~0.3 mm woven mesh leaves room for an adhesive bead at
// the rim without the mesh standing proud of the inner face and fouling the
// board.
module cover_mesh_rebate() {
    rotate([0, 0, COVER_AZ + esc_a_pow()])
        translate([ESC_MOUNT_R,
                   -(ESC_LOUVRE_L / 2 + ESC_MESH_MARGIN),
                   cover_louvre_z0() - ESC_MESH_MARGIN])
            cube([40, ESC_LOUVRE_L + 2 * ESC_MESH_MARGIN,
                  cover_louvre_span() + 2 * ESC_MESH_MARGIN]);
}


// ── Module: nacelle_esc_cover (main) ─────────────────────────────────────────
module nacelle_esc_cover() {
    assert(ESC_COVER_T > ESC_CBORE_DEPTH + 1.0,
           "counterbore leaves under 1 mm of material beneath the screw head");
    assert(ESC_LOUVRE_W >= 1.2,
           "louvre narrower than two extrusions at a 0.6 mm nozzle");
    difference() {
        // Plate: the cover's thickness, clipped to the window-plus-band outline
        // less a running clearance so it drops into the rebate.
        intersection() {
            cover_shell(0.0, ESC_COVER_T);
            esc_bay_footprint(COVER_AZ, 60.0, ESC_LEDGE_W - ESC_COVER_FIT);
        }

        // Six M3 clearance holes, on the pod's own boss centres.
        esc_boss_cylinders(COVER_AZ, ESC_SCREW_D);

        // Counterbores for M3 button heads, flat-bottomed and following the
        // skin so every head finishes flush wherever the local radius is.
        intersection() {
            cover_shell(-0.5, ESC_CBORE_DEPTH);
            esc_boss_cylinders(COVER_AZ, ESC_CBORE_D);
        }

        // Cooling louvres — the circuit's inlet.
        cover_louvres();

        // Rebate for the bonded FOD screen, in the inner face only.
        intersection() {
            cover_shell(ESC_COVER_T - ESC_MESH_REBATE, ESC_COVER_T);
            cover_mesh_rebate();
        }
    }
}

nacelle_esc_cover();


// =============================================================================
// ── Print specifications ──────────────────────────────────────────────────────
// =============================================================================
// Material    : CF-PETG (20 % CF) — same as the pod, so the cover and its
//               landing expand together.  A cover in a different polymer would
//               change fit across the -10 to +40 C the airframe sees.
// Layer height: 0.15 mm
// Walls       : 4 perimeters (2.5 mm at a 0.6 mm nozzle); the plate is 3.0 mm,
//               so it is essentially all perimeter — which is what you want in a
//               panel loaded normal to its face.
// Infill      : 100 % (the part is 3 mm thick; infill patterns in a 3 mm plate
//               are just voids)
// Nozzle      : hardened steel, required for CF-PETG
// Orientation : INNER (concave) face DOWN — see the header.  No supports; the
//               4.4 mm arch bridges.
// Quantity    : FOUR distinct parts per aircraft — port bay A, port bay B,
//               stbd bay A, stbd bay B.  They are not interchangeable.
//
// Post-print checks
// -----------------
//   1. Drop the cover into its rebate dry, before any insert is fitted.  It must
//      sit flush or up to 0.2 mm proud — NEVER recessed.  A recessed cover means
//      the rebate printed deep and the skin under it is thinner than 2.5 mm.
//   2. All six holes must clear an M3 shank without forcing.  A cover that has
//      to be sprung into place is preloading the pod's skin.
//   3. Counterbore depth 1.8 mm ± 0.15; check one head sits flush.
//   4. Louvres open through the full thickness — hold it to the light.  A
//      bridged-over louvre is the difference between a vented bay and a sealed
//      one, and this bay has no other heat path.
//   5. FOD screen: cut no-see-um mesh (0.6 mm aperture) to the rebate, bond at
//      the rim only — adhesive across the weave blocks the free area the sizing
//      depends on.  It must not stand proud of the inner face; the board is
//      1.0 mm away.  Check with a straightedge before fitting the cover.
//   6. M3 button heads sit 0.65 mm PROUD by design, not flush.  A head that sits
//      BELOW the surface means the counterbore printed deep and the cover is
//      thinner than 1.5 mm under it — reject.
//
// Render commands
// ---------------
//   PORT pod (rendered NACELLE_SIDE=-1 — see the selector note above):
//     openscad -o nacelle_esc_cover_port_a.stl nacelle_esc_cover.scad \
//              -D NACELLE_SIDE=-1 -D RENDER_BAY=0
//     openscad -o nacelle_esc_cover_port_b.stl nacelle_esc_cover.scad \
//              -D NACELLE_SIDE=-1 -D RENDER_BAY=1
//   STBD pod (rendered NACELLE_SIDE=+1):
//     openscad -o nacelle_esc_cover_stbd_a.stl nacelle_esc_cover.scad \
//              -D NACELLE_SIDE=1  -D RENDER_BAY=0
//     openscad -o nacelle_esc_cover_stbd_b.stl nacelle_esc_cover.scad \
//              -D NACELLE_SIDE=1  -D RENDER_BAY=1
