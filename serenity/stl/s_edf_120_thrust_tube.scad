// s_edf_120_thrust_tube.scad
// Thrust tube for Serenity Rev N 120mm rear EDF.
//
// Remixed from Thingiverse thing:2838324 (120mm fuselage EDF).
// This tube channels exhaust from the EDF exit face through the
// aft fuselage (station ~440mm) to the rear iris nozzle (station ~600mm).
//
// Coordinate system: +Z = aft (exhaust direction).
// Z=0 = forward face of thrust tube (mates to EDF casing aft lip / motor mount ring).
// Z=TUBE_L = aft bonding face (mates to rear_nozzle_frame.stl base ring).
//
// Integration interfaces:
//   Forward (Z=0):     forward spigot ID = EDF casing OD; locates tube on EDF exit.
//   Aft (Z=TUBE_L):    bonding flange ring bonds to rear_nozzle_frame.stl base.
//
// Station reference (from nose):
//   Station ~440mm: EDF exhaust face → Z=0 of this part
//   Station ~600mm: rear nozzle frame base → Z=TUBE_L
//   Total span: ~160mm → TUBE_L = 155mm (5mm overlap at each end)
//
// Print: PETG, 0.20mm layers, 20% gyroid infill.
// Note: orient with tube axis vertical on printer for best layer adhesion.
// No support required if printed tube-axis vertical.

// ── Geometry parameters ────────────────────────────────────────────────────

BORE_ID      = 120;   // [mm] internal bore (matches EDF fan bore)
WALL         =   3;   // [mm] tube wall thickness → OD = BORE_ID + 2×WALL
TUBE_L       = 155;   // [mm] total tube length (see station notes above)

// Forward spigot: thin sleeve that slips over the EDF casing aft OD
// The EDF casing outer diameter is nominally ~125mm (varies by brand);
// adjust SPIGOT_ID if your 120mm EDF casing OD differs.
EDF_CASING_OD = 125;  // [mm] EDF casing outer diameter — adjust to match actual unit
SPIGOT_ID     = EDF_CASING_OD + 0.4; // slip-fit clearance
SPIGOT_WALL   =   3;  // [mm] spigot sleeve wall
SPIGOT_L      =  12;  // [mm] spigot engagement length (overlaps EDF casing)

// Aft bonding flange: widens to grip against rear_nozzle_frame.stl base ring.
// rear_nozzle_frame base ring inner bore is assumed ~128mm — verify in slicer.
FLANGE_OD     = 134;  // [mm] bonding flange outer diameter
FLANGE_L      =   8;  // [mm] axial depth of bonding flange

// Lightening slots in tube wall (optional aero/mass reduction — set to 0 to disable)
SLOT_COUNT    =   0;  // number of axial slots in tube wall (0 = solid tube)
SLOT_W        =   8;  // [mm] slot width
SLOT_L        = 100;  // [mm] slot length (centred on tube)

$fn = 72;

// ── Derived values ─────────────────────────────────────────────────────────

TUBE_OD = BORE_ID + 2 * WALL;          // = 126mm
SPIGOT_OD = SPIGOT_ID + 2 * SPIGOT_WALL;

// ── Modules ────────────────────────────────────────────────────────────────

module main_tube() {
    difference() {
        cylinder(h = TUBE_L, r = TUBE_OD / 2);
        // bore
        translate([0, 0, -0.5])
            cylinder(h = TUBE_L + 1, r = BORE_ID / 2);
        // axial lightening slots
        if (SLOT_COUNT > 0)
            for (i = [0 : SLOT_COUNT - 1])
                rotate([0, 0, i * 360 / SLOT_COUNT])
                translate([TUBE_OD / 2 - WALL / 2, 0, TUBE_L / 2])
                    cube([WALL + 1, SLOT_W, SLOT_L], center = true);
    }
}

module forward_spigot() {
    // sleeve at Z=0 end that overlaps EDF casing aft lip
    difference() {
        cylinder(h = SPIGOT_L, r = SPIGOT_OD / 2);
        // inner bore clears EDF casing
        translate([0, 0, -0.5])
            cylinder(h = SPIGOT_L + 1, r = SPIGOT_ID / 2);
    }
}

module aft_bonding_flange() {
    // thickened ring at aft end for epoxy bond to rear_nozzle_frame base ring
    translate([0, 0, TUBE_L - FLANGE_L])
    difference() {
        cylinder(h = FLANGE_L, r = FLANGE_OD / 2);
        translate([0, 0, -0.5])
            cylinder(h = FLANGE_L + 1, r = BORE_ID / 2);
    }
}

// ── Assembly ───────────────────────────────────────────────────────────────

union() {
    main_tube();
    // forward spigot protrudes in the −Z direction (over EDF casing)
    translate([0, 0, -SPIGOT_L])
        forward_spigot();
    aft_bonding_flange();
}
