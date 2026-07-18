// _export_pivot_slab.scad — one-shot cache export (work section, 2026-07-18).
// Full-radius Z-slab of the true (imported) port nacelle shell around the pivot
// station (Z = 104.5), so the rotating-spar features (keyed hub, duct-wall
// bosses, stator tunnel) can be developed against real canonical geometry
// without re-CSG-ing the whole nacelle each render.  NOT a build artifact.
BORE_CX_L = 42.72; BORE_CY = 190.79;
Z_LO = 85; Z_HI = 125;                         // ±~20 mm around pivot Z=104.5
intersection() {
    translate([-BORE_CX_L, BORE_CY, 0])
        import("../../stls/nacelles/eng_left_shell24_50mm_repaired.stl", convexity = 4);
    translate([-45, -45, Z_LO]) cube([90, 90, Z_HI - Z_LO]);   // FULL width (both X faces)
}
