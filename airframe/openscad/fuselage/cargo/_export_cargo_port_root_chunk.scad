// _export_cargo_port_root_chunk.scad — work-section cache (2026-07-18).
// Hull-frame chunk of the true cargo shell around the PORT wing-root / tilt-spar
// entry (spar axis hull Y≈+15, Z≈+66, entering the outboard edge near X≈−73),
// so the root bearing seat + servo-to-spar horn features can be developed
// against real canonical geometry without re-CSG-ing the 51 MB shell.  NOT a
// build artifact.  Cargo STL is already hull-frame baked → import directly.
intersection() {
    import("../../../stls/fuselage/cargo/cargo_sect_shell24_2mm_repaired.stl", convexity = 6);
    translate([-150, 0, 35]) cube([90, 100, 65]);   // X −150..−60, Y 0..100, Z 20..100
}
