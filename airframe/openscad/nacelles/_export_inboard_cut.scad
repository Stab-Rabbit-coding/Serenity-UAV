// _export_inboard_cut.scad — one-shot cache export (decision aid, 2026-07-18).
// Renders ONLY the inboard-half nacelle shell in the gear-housing Z band, so
// gear_shell_compare.scad can import this small STL instead of re-CSG-ing the
// whole imported nacelle every render.  Not a build artifact.
BORE_CX_L = 42.72; BORE_CY = 190.79;
Z_LO = 79; Z_HI = 130;
intersection() {
    translate([-BORE_CX_L, BORE_CY, 0])
        import("../../stls/nacelles/eng_left_shell24_50mm_repaired.stl", convexity = 4);
    translate([-45, -45, Z_LO]) cube([45.5, 90, Z_HI - Z_LO]);
}
