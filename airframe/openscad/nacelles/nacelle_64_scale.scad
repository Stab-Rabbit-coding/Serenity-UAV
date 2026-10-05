// =============================================================================
// nacelle_64_scale.scad — SINGLE SOURCE for the 64 mm nacelle's shell scale
// =============================================================================
// Every SCAD file and tool that places something on the 64 mm pod reads its
// shell scale and the stations derived from it HERE, so a resize is one edit.
// Python tools read these values with a plain regex (name = number;).
//
// History
//   2026-10-03  P64_K 1.21 (radial packaging minimum), P64_A 1.13 (canonical
//               axial stretch) — tools/nacelle_64_proportion_trade.py.
//   2026-10-05  UNIFORM ENLARGEMENT x1.06 (owner: "if you need to enlarge the
//               nacelle, do so as a uniform enlarging, using the canonical
//               blueprint").  Both 70 A ESCs (two hinged bays each) fit only
//               at s >= 1.06 once the dorsal nozzle servo took the spine —
//               tools/esc80_cooptimize.py, WBS NAC-64-ESC-80A.m.  Uniform
//               scaling keeps the canonical L/D [REF-CAD-003].  The 64 mm duct,
//               the CFD-selected internal lip and the motor/rotor stack are
//               NOT scaled; they belong to the fan, not the shell.
//
// Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
// Stab-Rabbit-coding.  License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0
// (SPDX-License-Identifier: CERN-OHL-W-2.0)
// =============================================================================

P64_SCALE      = 1.06;                  // [-] uniform enlargement (2026-10-05)
P64_K          = 1.21 * P64_SCALE;      // [-] radial shell scale  = 1.2826
P64_A          = 1.13 * P64_SCALE;      // [-] axial shell scale   = 1.1978
P64_Z_NOZ      = 166.25 * P64_A;        // [mm] nozzle-ring pocket station = 199.13
P64_AXIS_SHIFT_S = 34.0 * P64_K - 34.0; // [mm] pylon-face axis shift  = 9.61
