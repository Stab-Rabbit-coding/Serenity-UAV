// ===========================================================================
// HULL-FRAME COORDINATE STANDARD - Rev R1 (2026-06-11).  See CLAUDE.md.
//   Hull frame (canonical for ALL design artifacts): X = +port (left),
//   Y = +aft (back), Z = +dorsal (up); origin = SerenityAssembly.FCStd
//   world origin.  Primary-component STLs published to airframe/stls/
//   are stored directly in hull frame, baked by tools/bake_hull_frame.py
//   (marker 'SerenityUAV HULL-FRAME R1' in the binary STL header).
//   NEVER re-bake a mesh derived from an already-baked file.
//   This file:
//     Middle (neck / horseshoe ring) section modelled in a part-local
//     frame with the section axial direction along local Z.  The
//     assembly's Middle_Shell mesh (s_middle_shell24_2mm_repaired.stl)
//     is baked to hull frame (90 deg about -X + translation;
//     COMPONENTS['Middle_Shell']).  Baked hull-frame bounds:
//     X -258.5..-81.7, Y +130.4..+203.6, Z +1.4..+166.1 mm.  After
//     regenerating the assembly mesh, re-run:
//         python3 tools/bake_hull_frame.py Middle_Shell
// ===========================================================================
// ============================================================
// middle_canonical_shell24.scad
// Mid-fuselage shell for Serenity Rev N 24" hull (s_middle.stl).
// Belly restored to standard Serenity geometry -- NO belly scoop.
// Replaces s_middle_intake_shell24.stl for the 4-radial-intake Rev N build.
//
// Rev R (2026-06-11): Rev R baseline checkpoint — no geometry changes.
// Rev S1 (2026-06-09): Simon avionics bay (Faraday enclosure) on dorsal interior;
//   Kaylee power distribution board and 6S battery tray on ventral interior.
//   Simon is the aft avionics SBC stack (CLAUDE.md: aft EDF control, alternate
//   nacelle/watchdog, Jayne cargo control, 49 MHz primary, SiK backup).
//   Kaylee is the power distribution board (CLAUDE.md: "Everything is shiny.").
//   Simon bay: Cape-B-2 (Zoë) + PB2-I + Cape-A-2 (Wash) + PB2-I; 55×35 mm PCBs.
//   Faraday tray: 60×40×55 mm external, same spec as cargo Rev S4 and head Rev S1.
//   4× M3 dorsal boss anchors (±25×±15 mm); 62×42 mm dorsal access panel.
//   Fan (25×25×7 mm) exhausts into fuselage interior; 22×22 mm honeycomb intake.
//   Kaylee tray: 100×60 mm footprint, ventral keel at station 190 mm.
//     4× M3 boss anchors; 110×70 mm ventral access hatch.
//   Battery: 6S 4000 mAh LiPo ≈ 145×44×50 mm; ventral, station 190 mm, keel.
//     Battery tray boss pattern: ±60 mm (X) × ±20 mm (Z) from tray centre.
//   Ref: cargo_sect_shell24.scad Rev S4; CLAUDE.md Kaylee/Simon; CAPE-B-2.kicad_pcb.
//
// Mounts:
//   S3A  -- VL53L5CX port-side ToF,  Array A (FC3), sta 267 mm
//   S4A  -- VL53L5CX stbd-side ToF,  Array A (FC3), sta 267 mm
//   S3B  -- VL53L5CX port-side ToF,  Array B (FC2), sta 200 mm
//   S4B  -- VL53L5CX stbd-side ToF,  Array B (FC2), sta 200 mm
//   S5A  -- VL53L5CX zenith ToF,     Array A (FC3), sta 240 mm
//   S5B  -- VL53L5CX zenith ToF,     Array B (FC2), sta 347 mm
//   S6A  -- VL53L5CX nadir ToF,      Array A (FC3), sta 213 mm
//   S6B  -- VL53L5CX nadir ToF,      Array B (FC2), sta 293 mm
//   GPS  -- 25x25 mm GPS patch antenna, dorsal centreline, sta 209 mm
//   ANT  -- 49 MHz XCVR whip post boss (1.5 mm protrusion), dorsal, sta 234 mm
//   SiK  -- SMA bulkhead, 915 MHz SiK telemetry,  port side,  sta 224 mm
//   ZBE  -- SMA bulkhead, 2.4 GHz ZigBee,         stbd side,  sta 224 mm
//   WIFI -- SMA bulkhead, 5 GHz WiFi,              port side,  sta 264 mm
//
// Flush-mount design philosophy:
//   All VL53L5CX apertures are cut flush with no external protrusion.
//   PMMA window discs sit in a 0.5 mm x 14 mm OD registration ring recess
//   on the exterior face, retained by UV adhesive and 4x M1.6 countersunk
//   flathead screws (DIN 7991).  Carrier board pockets are on the interior.
//   SMA connectors sit flush; hex nut recess is on the interior only.
//   GPS patch is recessed 2 mm into the dorsal hull surface (flush with OML);
//   a separate printed PETG dome cover protects it from weather.
//   The 49 MHz post boss is the only external protrusion -- 1.5 mm minimum
//   to register the antenna base above the hull waterline.
//
// Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
// License: CC BY 4.0 -- creativecommons.org/licenses/by/4.0
//
// Scale factor 24" hull: SCALE_24 = 2.9294
// Centroid of s_middle.stl at 24" scale:
//   CX = 135.712 x (2.9294/2.1974) = 180.95 mm
//   CY = -50.459 x (2.9294/2.1974) = -67.28 mm
//   CZ =  27.348 x (2.9294/2.1974) =  36.47 mm
// Inner scale factors (from 18" scad -- same 2.5 mm absolute wall):
//   INNER_SX = 0.962373
//   INNER_SY = 0.959565
//   INNER_SZ = 0.908966
//
// Coordinate system (24"-scaled STL world space = hull frame per CLAUDE.md):
//   X — lateral,      positive toward port  (left)
//   Y — longitudinal, positive aft (back)   NOTE: Y is aft; Z is dorsal/up
//   Z — vertical,     positive dorsal (up)
//
// Hull surface estimates (wall = 2.5 mm):
//   half_ext_Y = 2.5 / (1 - 0.959565) = 61.8 mm
//     Dorsal surface:  CY + 62 = approx -5 mm
//     Ventral surface: CY - 62 = approx -129 mm
//   half_ext_Z = 2.5 / (1 - 0.908966) = 27.5 mm
//     Port surface:    CZ + 28 = approx 64 mm
//     Stbd surface:    CZ - 28 = approx  9 mm
//
// All mount positions are estimates. VERIFY by measuring rendered mesh in slicer.
//
// Sensor wiring (dual-redundant failover):
//   Array A (FC3 SBC primary): S3A, S4A, S5A, S6A on I2C-3 bus, mux 0x70.
//   Array B (FC2 SBC primary): S3B, S4B, S5B, S6B on I2C-2 bus, mux 0x71.
//   Ref: ST UM2884 DocID032910 Rev 1, 2021.
//
// Antenna references:
//   SiK 915 MHz: FCC 47 CFR Part 15 Section 15.247 (REF-FCC-001).
//   ZigBee 2.4 GHz: IEEE 802.15.4; FCC Part 15 Section 15.247 (REF-FCC-001).
//   WiFi 5 GHz: IEEE 802.11ac; FCC Part 15 Subpart E Section 15.407 (REF-FCC-002).
//   49 MHz: FCC 47 CFR Part 15 Section 15.235 (REF-FCC-003) -- not Part 95 RCRS,
//   which does not cover this band.
// ============================================================

SCALE_24  = 2.9294;   // 24" hull scale factor

// Mid-fuselage centroid in 24"-scaled STL world coordinates
CX =  180.95;   // mm -- lateral axis (positive = port)
CY =  -67.28;   // mm -- longitudinal axis (positive = aft)
CZ =   36.47;   // mm -- vertical axis (positive = dorsal/up)

// Inner-shell scale factors (2.5 mm absolute wall)
INNER_SX = 0.962373;
INNER_SY = 0.959565;
INNER_SZ = 0.908966;

// Conservative wall thickness for cutter overlap
WALL_T = 4.0;   // mm

// Derived hull surface coordinates (VERIFY after rendering)
DORSAL_Y  = CY + 62;    // approx -5 mm
VENTRAL_Y = CY - 62;    // approx -129 mm
PORT_Z    = CZ + 28;    // approx 64 mm
STBD_Z    = CZ - 28;    // approx 9 mm
MID_Y     = CY;         // approx -67 mm (hull cross-section mid-height)
MID_Z     = CZ;         // approx 36 mm (hull Z centreline)

// VL53L5CX flush mount dimensions
//   Exterior: 11 mm PMMA bore + 0.5 mm x 14 mm OD seat ring + 4x M1.6 c/s.
//   Interior: 14x14x3 mm carrier-board recess.
//   Ref: ST UM2884 DocID032910 Rev 1, 2021.
VAPER_D   = 11.0;   // mm -- PMMA window aperture bore
VRING_OD  = 14.0;   // mm -- seat ring OD (hull-flush registration)
VRING_DEP =  0.5;   // mm -- seat ring recess depth
VM16_D    =  1.7;   // mm -- M1.6 clearance hole
VM16_R    =  7.0;   // mm -- M1.6 bolt circle radius
VCSK16_OD =  3.5;   // mm -- M1.6 flathead c/s OD (DIN 7991, 90 deg)
VCSK16_D  =  1.0;   // mm -- M1.6 c/s depth
VRECESS_W = 14.0;   // mm -- carrier board pocket (square)
VRECESS_D =  3.0;   // mm -- carrier board pocket depth

// SMA RF bulkhead dimensions (flush exterior, interior hex nut recess only)
//   SMA panel mount: 6.35 mm through-hole; 7/16" hex nut (11.1 mm AF).
SMA_BORE_D  =  6.5;    // mm -- SMA body clearance bore
SMA_HEX_AF  = 11.5;    // mm -- SMA hex nut across-flats (7/16" + clearance)
SMA_HEX_DEP =  4.0;    // mm -- interior hex nut recess depth

// GPS patch antenna flush recess dimensions (25x25 mm ceramic patch)
//   Patch sits 2 mm below hull surface; separate PETG dome cover snaps on.
//   Ref: u-blox UBX-15015498-R8 (NEO-M9N integration manual), Fig 3-3.
GPS_PATCH_W  = 26.0;   // mm -- patch pocket width (25 mm + 0.5 mm per side)
GPS_RECESS_D =  2.0;   // mm -- patch recess depth (patch element flush with OML)
GPS_COAX_D   =  5.0;   // mm -- coax feed-through bore (centre)
GPS_M2_D     =  2.2;   // mm -- M2 dome-cover mount hole clearance
GPS_M2_S     = 24.0;   // mm -- M2 bolt spacing (4 corners)
GPS_CSK2_OD  =  4.5;   // mm -- M2 flathead c/s OD (DIN 7991, 90 deg)
GPS_CSK2_D   =  1.2;   // mm -- M2 c/s depth

// 49 MHz XCVR antenna post boss
//   Minimum 1.5 mm protrusion to register antenna base above hull waterline.
//   M4 threaded insert (pressed from interior) retains antenna base flange.
ANT49_BOSS_OD    = 12.0;   // mm -- post boss OD (reduced to minimum functional)
ANT49_BOSS_H     =  1.5;   // mm -- boss protrusion above hull surface
ANT49_BORE_D     =  4.3;   // mm -- M4 insert bore clearance
ANT49_FLANGE_D   = 10.0;   // mm -- antenna base flange recess OD (on boss top)
ANT49_FLANGE_DEP =  1.0;   // mm -- flange recess depth

$fn = 64;

// Orientation rotation vectors
//   STL axes: X=forward, Y=dorsal (+up), Z=port (+left).
//   Ry(+90):  +Z -> +X  (forward)   rotate([  0,  90, 0 ])
//   Rx(-90):  +Z -> +Y  (zenith)    rotate([ -90,  0, 0 ])
//   Rx(+90):  +Z -> -Y  (nadir)     rotate([  90,  0, 0 ])
//   no rot:   +Z -> +Z  (port)      rotate([   0,  0, 0 ])
//   Rx(180):  +Z -> -Z  (stbd)      rotate([ 180,  0, 0 ])
ZENITH_ROT = [ -90,   0, 0 ];
NADIR_ROT  = [  90,   0, 0 ];
PORT_ROT   = [   0,   0, 0 ];
STBD_ROT   = [ 180,   0, 0 ];

// Mount position constants -- 24"-scaled STL world coordinates
//   X_stl = 284 - station_mm.  All positions VERIFY in slicer.

// Array A lateral sensors (FC3 primary) -- station 267 mm (X_stl = 17)
S3A_POS = [  17, MID_Y, PORT_Z ];    // VERIFY: port hull, sta 267 mm
S4A_POS = [  17, MID_Y, STBD_Z ];    // VERIFY: stbd hull, sta 267 mm

// Array B lateral sensors (FC2 primary) -- station 200 mm (X_stl = 84)
S3B_POS = [  84, MID_Y, PORT_Z ];    // VERIFY: port hull, sta 200 mm
S4B_POS = [  84, MID_Y, STBD_Z ];    // VERIFY: stbd hull, sta 200 mm

// Array A zenith sensor (FC3) -- station 240 mm (X_stl = 44)
S5A_POS = [  44, DORSAL_Y, MID_Z ];  // VERIFY: dorsal hull, sta 240 mm

// Array B zenith sensor (FC2) -- station 347 mm (X_stl = -63)
S5B_POS = [ -63, DORSAL_Y, MID_Z ];  // VERIFY: dorsal hull, sta 347 mm

// Array A nadir sensor (FC3) -- station 213 mm (X_stl = 71)
S6A_POS = [  71, VENTRAL_Y, MID_Z ]; // VERIFY: ventral hull, sta 213 mm

// Array B nadir sensor (FC2) -- station 293 mm (X_stl = -9)
S6B_POS = [  -9, VENTRAL_Y, MID_Z ]; // VERIFY: ventral hull, sta 293 mm

// GPS patch -- dorsal centreline, station 209 mm (X_stl = 75)
//   Broad, flat dorsal surface provides optimal GPS ground plane and sky view.
GPS_POS  = [  75, DORSAL_Y, MID_Z ]; // VERIFY: dorsal centreline, sta 209 mm

// 49 MHz XCVR post -- dorsal centreline, station 234 mm (X_stl = 50), aft of GPS
ANT49_POS = [ 50, DORSAL_Y, MID_Z ]; // VERIFY: dorsal centreline, sta 234 mm

// SiK 915 MHz SMA -- port side, station 224 mm (X_stl = 60)
SIK_POS  = [  60, MID_Y + 20, PORT_Z ];  // VERIFY: port hull, 20 mm above mid

// ZigBee 2.4 GHz SMA -- stbd side, station 224 mm (X_stl = 60)
ZBE_POS  = [  60, MID_Y + 20, STBD_Z ];  // VERIFY: stbd hull, 20 mm above mid

// WiFi 5 GHz SMA -- port side, station 264 mm (X_stl = 20)
WIFI_POS = [  20, MID_Y + 20, PORT_Z ];  // VERIFY: port hull, 20 mm above mid

// ----------------------------------------------------------------------------
// Module: vlsensor_cut
//   Flush-mount cutter for VL53L5CX.  Zero protrusion above hull surface.
//   Aperture bore + 0.5 mm PMMA seat ring + 4x M1.6 c/s holes + board pocket.
// ----------------------------------------------------------------------------
module vlsensor_cut(pos, rot) {
    translate(pos)
    rotate(rot)
    translate([0, 0, -(WALL_T + 1)]) {
        // PMMA aperture bore
        cylinder(h = WALL_T + 2, d = VAPER_D);

        // PMMA disc seat ring (0.5 mm recess, 14 mm OD) at exterior face
        translate([0, 0, WALL_T + 1 - VRING_DEP])
        cylinder(h = VRING_DEP + 1, d = VRING_OD);

        // 4x M1.6 countersunk through-holes at 45 deg diagonal
        for (a = [45, 135, 225, 315])
            rotate([0, 0, a])
            translate([VM16_R, 0, 0]) {
                cylinder(h = WALL_T + 2, d = VM16_D);
                translate([0, 0, WALL_T + 1 - VCSK16_D])
                cylinder(h = VCSK16_D + 1, d1 = VM16_D, d2 = VCSK16_OD);
            }

        // Carrier board recess on interior face
        translate([-VRECESS_W / 2, -VRECESS_W / 2, 0])
        cube([VRECESS_W, VRECESS_W, VRECESS_D + 1]);
    }
}

// ----------------------------------------------------------------------------
// Module: sma_cut
//   Flush SMA bulkhead bore + interior hex-nut recess.  No exterior protrusion.
// ----------------------------------------------------------------------------
module sma_cut(pos, rot) {
    translate(pos)
    rotate(rot)
    translate([0, 0, -(WALL_T + 1)]) {
        // SMA body clearance bore (full wall)
        cylinder(h = WALL_T + 2, d = SMA_BORE_D);
        // Interior hex-nut recess (6-sided, first SMA_HEX_DEP mm from inside)
        cylinder(h = SMA_HEX_DEP + 1, d = SMA_HEX_AF, $fn = 6);
    }
}

// ----------------------------------------------------------------------------
// Module: gps_cut
//   Flush GPS patch recess + coax bore + 4x M2 dome-cover c/s holes.
//   Patch sits 2 mm below hull OML; dome cover (separate part) clips on.
// ----------------------------------------------------------------------------
module gps_cut(pos, rot) {
    translate(pos)
    rotate(rot)
    translate([0, 0, -(WALL_T + 1)]) {
        // Patch element pocket (square recess, 2 mm deep at exterior face)
        translate([-GPS_PATCH_W / 2, -GPS_PATCH_W / 2, WALL_T + 1 - GPS_RECESS_D])
        cube([GPS_PATCH_W, GPS_PATCH_W, GPS_RECESS_D + 1]);

        // Coax feed-through bore at patch centre (full wall depth)
        cylinder(h = WALL_T + 2, d = GPS_COAX_D);

        // 4x M2 dome-cover retention holes (countersunk, 4 corners)
        for (dx = [-GPS_M2_S / 2, GPS_M2_S / 2])
        for (dy = [-GPS_M2_S / 2, GPS_M2_S / 2])
            translate([dx, dy, 0]) {
                cylinder(h = WALL_T + 2, d = GPS_M2_D);
                translate([0, 0, WALL_T + 1 - GPS_CSK2_D])
                cylinder(h = GPS_CSK2_D + 1, d1 = GPS_M2_D, d2 = GPS_CSK2_OD);
            }
    }
}

// ----------------------------------------------------------------------------
// Module: ant49_boss
//   Minimal 1.5 mm post boss for 49 MHz XCVR antenna base registration.
//   This is the only external protrusion; required to keep the antenna base
//   above the hull waterline.
// ----------------------------------------------------------------------------
module ant49_boss(pos, rot) {
    translate(pos)
    rotate(rot)
    cylinder(h = ANT49_BOSS_H, d = ANT49_BOSS_OD);
}

// ----------------------------------------------------------------------------
// Module: ant49_cut
//   M4 insert bore through hull + boss + flange recess on boss top.
// ----------------------------------------------------------------------------
module ant49_cut(pos, rot) {
    translate(pos)
    rotate(rot) {
        // M4 bore through hull and boss
        translate([0, 0, -(WALL_T + 1)])
        cylinder(h = WALL_T + ANT49_BOSS_H + 2, d = ANT49_BORE_D);
        // Antenna base flange recess on top of boss
        translate([0, 0, ANT49_BOSS_H - ANT49_FLANGE_DEP])
        cylinder(h = ANT49_FLANGE_DEP + 1, d = ANT49_FLANGE_D);
    }
}

// ── Cape PCB dimensions (Rev S1 — same spec as cargo Rev S4, head Rev S1) ────
//   Verified from CAPE-B-2.kicad_pcb Edge.Cuts; title block: "55x35mm 4L JLCPCB".
CAPE_PCB_X     =  55.0;   // mm, Cape-B-2 / Cape-A-2 PCB X extent
CAPE_PCB_Z     =  35.0;   // mm, Cape-B-2 / Cape-A-2 PCB Z extent
CAPE_HOLE_DX   =  24.5;   // mm, ±X M2.5 corner hole offset from board centre
CAPE_HOLE_DZ   =  14.5;   // mm, ±Z M2.5 corner hole offset from board centre

// ── M3 boss dimensions (reused pattern from cargo/head SCADs) ────────────────
BOSS_OD        =   8.0;   // mm, boss outer diameter (2-wall annulus per CLAUDE.md)
BOSS_H         =   6.0;   // mm, boss height from interior face (≥ insert length 5.7 mm)
BOSS_BORE_D    =   4.1;   // mm, M3 heat-set insert bore (4.0 mm nom + 0.1 mm clearance)
WALL_MM        =   2.5;   // mm, shell wall thickness (matches INNER_S* factors above)

// ── Faraday enclosure dimensions (same spec as cargo Rev S4) ─────────────────
FARADAY_ENC_X  =  60.0;   // mm, tray external X (Cape 55 mm + 1.5 mm Al wall each side)
FARADAY_ENC_Z  =  40.0;   // mm, tray external Z (Cape 35 mm + 1.5 mm Al wall each side)
FARADAY_ENC_Y  =  55.0;   // mm, tray depth (39.2 mm stack + 5 mm clearance + 7 mm fan + 1.5 mm)
FARADAY_WALL   =   1.5;   // mm, tray wall (0.5 mm Al + PETG liner ≤ 1.5 mm)
FARADAY_FAN_D  =  25.0;   // mm, axial fan diameter (25×25×7 mm, on tray +X wall)

// ── Ductwork parameters (same spec as cargo Rev S4, head Rev S1) ─────────────
DUCT_INTAKE_W  =  22.0;   // mm, intake slot width on tray −X face (≤ fan 25 mm)
DUCT_INTAKE_H  =  22.0;   // mm, intake slot height
DUCT_EXHAUST_W =  24.0;   // mm, exhaust slot width on tray +X face (behind fan)
DUCT_EXHAUST_H =  24.0;   // mm, exhaust slot height
DUCT_EMC_T     =   6.0;   // mm, waveguide-below-cutoff honeycomb panel thickness
DUCT_CELL_D    =   6.0;   // mm, honeycomb cell diameter (λ/2 cutoff > 25 GHz)

// ── Simon avionics bay — dorsal interior, mid-fuselage (Rev S1) ──────────────
//
// Simon (CLAUDE.md: aft avionics bay) is the primary aft-EDF and alternate
// watchdog SBC.  Cape-B-2 (Zoë) + PB2-I + Cape-A-2 (Wash) + PB2-I stack.
//
// DORSAL INTERIOR FACE Y:
//   Dorsal exterior ≈ CY + 62 = -5 mm.  Interior face ≈ -5 - 2.5 = -7.5 mm.
//   SIMON_DORSAL_Y = DORSAL_Y - WALL_MM ≈ -7.5 mm.  VERIFY in slicer.
//   NOTE: verify flat dorsal region spans full 62×42 mm panel footprint.
//
// BAY POSITION:
//   X centre = CX = 180.95 mm.  Panel X span: 149.95..211.95 mm.
//   Z centre = MID_Z = CZ = 36.47 mm.  Panel Z span: 15.47..57.47 mm.
//   All well within GPS (X=75), ANT49 (X=50), sensor zone (X≤84) ✓.
//   Port Z wall at ≈64 mm; panel Z upper edge 57.47 mm < 64 mm ✓.
//   Stbd Z wall at ≈9 mm; panel Z lower edge 15.47 mm > 9 mm ✓.
//
// BOSS PATTERN (4× M3 bosses, ±25 mm X × ±15 mm Z from bay centre):
//   Boss X: CX ± 25 = 155.95 and 205.95 mm.
//   Boss Z: CZ ± 15 = 21.47 and 51.47 mm.
//   VERIFY bosses sit on flat interior dorsal face in slicer before printing.
//   Ref: FARADAY_* dims above; CAPE-B-2.kicad_pcb MH1–MH4; Ruthex RX-M3x5.7.
SIMON_BOSS_ROT    = [90, 0, 0];    // rotate cylinder: +Z → −Y (protrudes down into interior)
SIMON_X_CEN       = CX;            // mm, bay X centre = 180.95 mm
SIMON_Z_CEN       = MID_Z;         // mm, bay Z centre =  36.47 mm
SIMON_DORSAL_Y    = DORSAL_Y - WALL_MM;  // mm, interior dorsal face (≈ -7.5 mm; VERIFY)
SIMON_BOSS_DX     =  25.0;         // mm, ±X boss offset
SIMON_BOSS_DZ     =  15.0;         // mm, ±Z boss offset
SIMON_PANEL_X     =  62.0;         // mm, dorsal access panel opening X
SIMON_PANEL_Z     =  42.0;         // mm, dorsal access panel opening Z

// ── Kaylee power distribution board + battery — ventral keel (Rev S1) ────────
//
// Kaylee (CLAUDE.md: PDB, "Everything is shiny") and the main 6S 4000 mAh
// flight battery are mounted at the ventral keel of the mid-fuselage section.
//
// Battery: 6S 4000 mAh LiPo (e.g., Tattu R-Line 6S 4000 mAh):
//   Dimensions: 145 mm (X) × 44 mm (Z) × 50 mm (Y) — VERIFY with actual cell.
//   Station 190 mm from nose → X_stl = 284 - 190 = 94 mm.
//   Tray boss pattern: ±70 mm (X) × ±24 mm (Z) from tray centre.
//   Access hatch: 150×50 mm opening on ventral face.
//
// Kaylee PDB: 100×80 mm (estimate — verify against actual Kaylee layout).
//   Station 255 mm from nose → X_stl = 284 - 255 = 29 mm.
//   Place AFT (lower X) of battery; adjacent in X with 10 mm gap.
//   Tray boss pattern: ±45 mm (X) × ±35 mm (Z) from tray centre.
//   Access hatch: 105×90 mm opening on ventral face.
//
// VENTRAL INTERIOR FACE Y:
//   Ventral exterior ≈ CY - 62 = -129 mm.  Interior ≈ -129 + 2.5 = -126.5 mm.
//   KAYLEE_VENTRAL_Y = VENTRAL_Y + WALL_MM ≈ -126.5 mm.  VERIFY in slicer.
//   Ref: CLAUDE.md Kaylee / battery placement; TODO §1.4.5; bom_revO.csv 6S cell.
KAYLEE_VENTRAL_Y    = VENTRAL_Y + WALL_MM;  // mm, interior ventral face Y (VERIFY slicer)
KAYLEE_BOSS_ROT     = [-90, 0, 0];          // rotate cylinder: +Z → +Y (protrudes up into interior)

// Battery tray (6S 4000 mAh)
BATT_X_CEN          =  94.0;   // mm, battery tray X centre (sta 190 mm from nose)
BATT_Z_CEN          = MID_Z;   // mm, battery tray Z centre = CZ = 36.47 mm
BATT_BOSS_DX        =  70.0;   // mm, ±X boss offset (battery 145 mm / 2 + 2.5 mm inset)
BATT_BOSS_DZ        =  24.0;   // mm, ±Z boss offset (battery 44 mm / 2 + 2 mm inset)
BATT_HATCH_X        = 150.0;   // mm, ventral hatch opening X (battery 145 mm + 5 mm)
BATT_HATCH_Z        =  50.0;   // mm, ventral hatch opening Z (battery 44 mm + 6 mm)

// Kaylee PDB tray
KAYLEE_X_CEN        =  29.0;   // mm, Kaylee tray X centre (sta 255 mm from nose)
KAYLEE_Z_CEN        = MID_Z;   // mm, Kaylee tray Z centre = CZ = 36.47 mm
KAYLEE_BOSS_DX      =  45.0;   // mm, ±X boss offset (PDB 100 mm / 2 - 5 mm)
KAYLEE_BOSS_DZ      =  35.0;   // mm, ±Z boss offset (PDB 80 mm / 2 - 5 mm)
KAYLEE_HATCH_X      = 105.0;   // mm, ventral hatch opening X (PDB 100 mm + 5 mm)
KAYLEE_HATCH_Z      =  90.0;   // mm, ventral hatch opening Z (PDB 80 mm + 10 mm)

// ----------------------------------------------------------------------------
// Module: simon_dorsal_boss
//   Single M3 heat-set insert boss on interior dorsal face, protruding −Y
//   (downward into mid-fuselage interior).  One corner of Simon's Faraday tray.
// ----------------------------------------------------------------------------
module simon_dorsal_boss(x_pos, z_pos) {
    translate([x_pos, SIMON_DORSAL_Y, z_pos])
    rotate(SIMON_BOSS_ROT)
    difference() {
        cylinder(h = BOSS_H, d = BOSS_OD);
        cylinder(h = BOSS_H + 0.1, d = BOSS_BORE_D);
    }
}

// ----------------------------------------------------------------------------
// Module: simon_dorsal_panel_cut
//   62×42 mm through-cut in dorsal skin for Simon's Faraday tray insertion.
//   Y span: SIMON_DORSAL_Y − 1.0 through SIMON_DORSAL_Y + WALL_MM + 1.0.
// ----------------------------------------------------------------------------
module simon_dorsal_panel_cut() {
    translate([SIMON_X_CEN - SIMON_PANEL_X / 2,
               SIMON_DORSAL_Y - 1.0,
               SIMON_Z_CEN - SIMON_PANEL_Z / 2])
    cube([SIMON_PANEL_X, WALL_MM + 2.0, SIMON_PANEL_Z]);
}

// ----------------------------------------------------------------------------
// Module: ventral_boss
//   Single M3 heat-set insert boss on interior ventral face, protruding +Y
//   (upward into mid-fuselage interior).  Used for both Kaylee and battery trays.
// ----------------------------------------------------------------------------
module ventral_boss(x_pos, z_pos) {
    translate([x_pos, KAYLEE_VENTRAL_Y, z_pos])
    rotate([-90, 0, 0])   // +Z → +Y: boss protrudes upward into fuselage interior
    difference() {
        cylinder(h = BOSS_H, d = BOSS_OD);
        cylinder(h = BOSS_H + 0.1, d = BOSS_BORE_D);
    }
}

// ----------------------------------------------------------------------------
// Module: ventral_hatch_cut
//   Rectangular through-cut in ventral skin for battery/Kaylee tray access.
//   Y span: KAYLEE_VENTRAL_Y − WALL_MM − 1.0 through KAYLEE_VENTRAL_Y + 1.0.
//   Hatch cover is a separate PETG part with 5 mm shoulder lip.
// ----------------------------------------------------------------------------
module ventral_hatch_cut(x_cen, z_cen, hatch_x, hatch_z) {
    translate([x_cen - hatch_x / 2,
               KAYLEE_VENTRAL_Y - WALL_MM - 1.0,
               z_cen - hatch_z / 2])
    cube([hatch_x, WALL_MM + 2.0, hatch_z]);
}

// ============================================================
// Main geometry
// ============================================================
// ── CSG tree overview (Rev S1) ────────────────────────────────────────────────
//
//   difference
//   ├─ union
//   │  ├─ difference            ← shell (outer − scaled inner void)
//   │  ├─ ant49_boss            ← 49 MHz antenna post (only external protrusion)
//   │  ├─ simon_dorsal_boss ×4  ← Simon Faraday tray anchor bosses on dorsal face
//   │  ├─ ventral_boss ×4       ← battery tray anchors on ventral keel face
//   │  └─ ventral_boss ×4       ← Kaylee PDB tray anchors on ventral keel face
//   ├─ vlsensor_cut ×8          ← ToF sensor apertures
//   ├─ gps_cut                  ← GPS patch recess + dome-cover holes
//   ├─ ant49_cut                ← 49 MHz M4 bore + flange recess
//   ├─ sma_cut ×3               ← SiK, ZigBee, WiFi SMA bulkheads
//   ├─ simon_dorsal_panel_cut   ← 62×42 mm Simon Faraday tray access opening
//   ├─ ventral_hatch_cut        ← 150×50 mm battery tray access hatch
//   └─ ventral_hatch_cut        ← 105×90 mm Kaylee PDB access hatch
//
difference() {
    union() {
        // Canonical 24" mid-fuselage shell (outer minus inner void)
        difference() {
            scale([SCALE_24, SCALE_24, SCALE_24])
                import("../../thingverse-serenity/files/s_middle.stl");

            translate([CX, CY, CZ])
            scale([INNER_SX, INNER_SY, INNER_SZ])
            translate([-CX, -CY, -CZ])
            scale([SCALE_24, SCALE_24, SCALE_24])
                import("../../thingverse-serenity/files/s_middle.stl");
        }

        // 49 MHz antenna post boss -- only external protrusion on this section
        ant49_boss(ANT49_POS, ZENITH_ROT);

        // Simon's avionics bay — 4× M3 Faraday tray anchor bosses on dorsal face.
        //   Boss pattern: ±25 mm (X) × ±15 mm (Z) from bay centre (CX, CZ).
        //   Boss positions (X, Z): (155.95,21.47), (155.95,51.47),
        //                          (205.95,21.47), (205.95,51.47).
        //   Panel X=149.95..211.95 mm clears GPS (X=75) and ANT49 (X=50) ✓.
        //   Panel Z=15.47..57.47 mm within section Z bounds (9..64 mm) ✓.
        //   VERIFY boss positions on flat dorsal interior face in slicer.
        //   Ref: Rev S1; FARADAY_ENC_* dims; CLAUDE.md Simon bay role.
        for (dx = [-SIMON_BOSS_DX, SIMON_BOSS_DX])
        for (dz = [-SIMON_BOSS_DZ, SIMON_BOSS_DZ])
            simon_dorsal_boss(SIMON_X_CEN + dx, SIMON_Z_CEN + dz);

        // Battery tray anchor bosses — 4× M3 on ventral keel face.
        //   Station 190 mm: X_stl = 94 mm.  Boss X: 94 ± 70 = 24..164 mm.
        //   Boss Z: CZ ± 24 = 12.47..60.47 mm — within section Z bounds ✓.
        //   VERIFY bosses fused to interior ventral face in slicer.
        //   Ref: 6S 4000 mAh LiPo (145×44×50 mm nominal); TODO §1.4.5.
        for (dx = [-BATT_BOSS_DX, BATT_BOSS_DX])
        for (dz = [-BATT_BOSS_DZ, BATT_BOSS_DZ])
            ventral_boss(BATT_X_CEN + dx, BATT_Z_CEN + dz);

        // Kaylee PDB tray anchor bosses — 4× M3 on ventral keel face.
        //   Station 255 mm: X_stl = 29 mm.  Boss X: 29 ± 45 = -16..74 mm.
        //   NOTE: -16 mm is AFT of middle section fore edge; VERIFY in slicer.
        //   Boss Z: CZ ± 35 = 1.47..71.47 mm — verify within section Z bounds.
        //   VERIFY boss positions in slicer — PDB footprint TBD after Kaylee layout.
        //   Ref: CLAUDE.md Kaylee PDB; TODO §1.4.5.
        for (dx = [-KAYLEE_BOSS_DX, KAYLEE_BOSS_DX])
        for (dz = [-KAYLEE_BOSS_DZ, KAYLEE_BOSS_DZ])
            ventral_boss(KAYLEE_X_CEN + dx, KAYLEE_Z_CEN + dz);
    }

    // VL53L5CX flush apertures (8 sensors, 6 directions)
    vlsensor_cut(S3A_POS,  PORT_ROT);
    vlsensor_cut(S4A_POS,  STBD_ROT);
    vlsensor_cut(S3B_POS,  PORT_ROT);
    vlsensor_cut(S4B_POS,  STBD_ROT);
    vlsensor_cut(S5A_POS,  ZENITH_ROT);
    vlsensor_cut(S5B_POS,  ZENITH_ROT);
    vlsensor_cut(S6A_POS,  NADIR_ROT);
    vlsensor_cut(S6B_POS,  NADIR_ROT);

    // GPS patch recess and dome-cover holes
    gps_cut(GPS_POS, ZENITH_ROT);

    // 49 MHz post bore and flange recess
    ant49_cut(ANT49_POS, ZENITH_ROT);

    // SMA RF bulkhead bores (flush exterior, interior hex recess)
    sma_cut(SIK_POS,  PORT_ROT);
    sma_cut(ZBE_POS,  STBD_ROT);
    sma_cut(WIFI_POS, PORT_ROT);

    // Simon's avionics bay dorsal access panel (Rev S1).
    //   62×42 mm cut through dorsal skin at (SIMON_X_CEN, SIMON_Z_CEN).
    //   Simon Faraday tray (60×40 mm) inserts from outside; 1 mm clearance each side.
    //   Cover (72×52 mm, 5 mm shoulder) seals EMI enclosure when installed.
    //   Fan (25×25×7 mm) on tray +X wall exhausts into fuselage interior.
    //   Honeycomb intake (22×22 mm slot, 6 mm waveguide panel) on tray −X wall.
    //   VERIFY panel bounds and boss clearances in slicer before printing.
    simon_dorsal_panel_cut();

    // Battery tray ventral access hatch (Rev S1).
    //   150×50 mm hatch at (BATT_X_CEN, BATT_Z_CEN) on ventral skin.
    //   Allows battery pull-out for field swap without disassembly.
    //   Hatch cover: 160×60 mm PETG, 5 mm shoulder, 4× M2.5 flush-head screws.
    //   VERIFY hatch bounds and battery fit in slicer — 6S cell dims TBD.
    ventral_hatch_cut(BATT_X_CEN, BATT_Z_CEN, BATT_HATCH_X, BATT_HATCH_Z);

    // Kaylee PDB ventral access hatch (Rev S1).
    //   105×90 mm hatch at (KAYLEE_X_CEN, KAYLEE_Z_CEN) on ventral skin.
    //   Provides field access to PDB connectors, fuses, and current sensors.
    //   Hatch cover: 115×100 mm PETG, 5 mm shoulder, 4× M2.5 flush-head screws.
    //   VERIFY hatch bounds and PDB footprint in slicer — PDB layout TBD.
    ventral_hatch_cut(KAYLEE_X_CEN, KAYLEE_Z_CEN, KAYLEE_HATCH_X, KAYLEE_HATCH_Z);
}
