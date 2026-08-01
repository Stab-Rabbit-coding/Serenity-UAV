/**
 * serenity-rev-s.jsx — Serenity-Class Tiltrotor UAV Rev S Specification
 *
 * Revision S (2026-07-04): Comprehensive Checkpoint & System Integration
 *
 * Key changes from Rev R:
 *   1. Integrates all Rev R1/R1c/R1d/R2 modifications (see docs/WBS.md §6.3 changelog).
 *   2. Pilot/XO PCB Rev S1 designs: EMI hardening applied; full isolation (5 kV);
 *      all 8 avionics stacks in identical EMI-hardened configuration.
 *   3. Commo Rev S1: Adds LoRa + RSSI detection; part of distributed comms strategy.
 *   4. Flight Engineer Rev S: PDB finalized; 5-rail power distribution; clean DRC.
 *   5. Observer board (vision/ToF/laser): Standalone CAN-FD + Ethernet node; two units
 *      (nose sensor pod forward view; cargo bay nadir 3D imaging).
 *   6. STS3215 digital servo winch: Replaces N20 motor train; 5 containment fixes;
 *      ratchet safety mechanism; Dyneema SK75 line.
 *   7. Tilt-spar material selection open (4130, 17-4 PH, 7075 candidates).
 *   8. Landing gear: Wire brace design finalized; elastic + ductile wire grades.
 *   9. Fuselage mid-section bays refined (Flight Engineer's room, Simon's medbay).
 *   10. Lint debt remediation complete (2026-07-18); CI pipeline green.
 *
 * This is a COMPLETE design specification — not a delta from Rev R.
 * Every subsystem is documented in full for standalone reference.
 *
 * Attribution:
 *   Hull geometry: misubisu (thingiverse.com/thing:7330462) — CC BY 4.0
 *   Iris nozzle concept (nacelle): BamJr (thingiverse.com/thing:2991269) — CC BY 4.0
 *   Visual inspiration: Firefly / Serenity © Joss Whedon / Mutant Enemy / Universal
 *     (Fan engineering work — not an officially licensed product)
 *
 * Author:  Steve Griffing, PE(CSE) [Control Systems Engineering], CISSP-ISSEP, CPP
 * License: CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/
 * Date:    2026-07-04
 */

import { useState } from "react";

/* ── OpenDyslexic font loader ───────────────────────────────────────────────── */
function _ODFontLoader() {
    if (typeof document === "undefined") return null;
    if (document.getElementById("od-font-link")) return null;
    const l = document.createElement("link");
    l.id = "od-font-link"; l.rel = "stylesheet";
    l.href = "https://fonts.cdnfonts.com/css/opendyslexic";
    document.head.appendChild(l);
    const s = document.createElement("style");
    s.id = "od-font-style";
    s.textContent = `
        *, *::before, *::after {
            font-family: 'OpenDyslexic','OpenDyslexic Bold','OpenDyslexicMono',sans-serif !important;
        }
        @media print {
            body { background: #ffffff !important; color: #111111 !important; }
            * { color: #111111 !important; background: transparent !important; }
            a { color: #003366 !important; }
        }
    `;
    document.head.appendChild(s);
    return null;
}

/* ── Design tokens ─────────────────────────────────────────────────────────── */
const C = {
    bg:     "#060810",
    border: "rgba(0,229,255,0.13)",
    accent: "#00e5ff",
    orange: "#ff6b35",
    yellow: "#ffe600",
    purple: "#c084fc",
    green:  "#4ade80",
    pink:   "#f472b6",
    teal:   "#2dd4bf",
    red:    "#f87171",
    lime:   "#a3e635",
    gold:   "#fbbf24",
    text:   "rgba(255,255,255,0.95)",
    dim:    "rgba(255,255,255,0.82)",
    dimmer: "rgba(255,255,255,0.70)",
};
const M  = "'OpenDyslexic Mono','OpenDyslexicMono','Courier New',monospace";
const MB = "'OpenDyslexic Bold','OpenDyslexic',sans-serif";

/* ── Reusable primitives ───────────────────────────────────────────────────── */
function Card({ title, accent, children }) {
    return (
        <div style={{
            border: `1px solid ${accent || C.border}`,
            borderRadius: 10, padding: "16px 20px",
            marginBottom: 18, background: "rgba(255,255,255,0.025)",
        }}>
            <div style={{
                color: accent || C.accent, fontFamily: MB,
                fontSize: 14, fontWeight: 700, marginBottom: 12,
                letterSpacing: 0.5, textTransform: "uppercase",
            }}>{title}</div>
            {children}
        </div>
    );
}

function TH({ cols, accent }) {
    return (
        <thead>
            <tr>
                {cols.map(c => (
                    <th key={c} style={{
                        color: accent || C.accent, fontFamily: MB,
                        fontSize: 11, padding: "4px 12px 4px 0", textAlign: "left",
                        borderBottom: `1px solid ${C.border}`,
                    }}>{c}</th>
                ))}
            </tr>
        </thead>
    );
}

function Table({ cols, rows, accent, rowAccent }) {
    return (
        <table style={{ borderCollapse: "collapse", width: "100%" }}>
            <TH cols={cols} accent={accent} />
            <tbody>
                {rows.map((row, i) => (
                    <tr key={i} style={{ background: i % 2 ? `rgba(255,255,255,0.02)` : "transparent" }}>
                        {row.map((cell, j) => (
                            <td key={j} style={{
                                padding: "4px 12px 4px 0", fontFamily: M, fontSize: 11.5,
                                color: j === 0 ? (rowAccent || C.dim) : C.text,
                            }}>{cell}</td>
                        ))}
                    </tr>
                ))}
            </tbody>
        </table>
    );
}

function Badge({ text, color }) {
    return (
        <span style={{
            display: "inline-block", padding: "1px 7px",
            background: `${color}22`, border: `1px solid ${color}55`,
            borderRadius: 4, fontSize: 10, fontFamily: MB,
            color: color, marginLeft: 6, verticalAlign: "middle",
        }}>{text}</span>
    );
}

/* ── Overview tab ──────────────────────────────────────────────────────────── */
function TabOverview() {
    return (
        <div>
            <Card title="Rev R — What's New" accent={C.green}>
                <Table
                    cols={["Subsystem", "Change", "Status", "Date"]}
                    accent={C.green}
                    rows={[
                        ["Avionics / Naming", "Cape-A-2 renamed to Pilot; Cape-B-2 renamed to XO. CAPE-A-2 and CAPE-B-2 KiCad files archived to avionics/kicad/archive/. Pilot.* and XO.* are now the sole active cape design files.", "✓ DONE", "2026-06-10"],
                        ["Avionics / Flight Engineer PDB", "Flight Engineer Power Distribution Board: KiCad pro/sch/pcb generated; DRC 0 shorts; gerbers generated to avionics/kicad/gerbers/. FlightEngineer.md design notes created.", "✓ DONE", "2026-06-10"],
                        ["Airframe / FreeCAD", "SerenityAssembly.FCStd validated: position + quaternion for Head, Cargo, Middle, Rear, Wing×2, Nacelle×2 documented in CLAUDE.md and serenity_assembly.py. Hull-frame axes defined (X = +port, Y = +aft, Z = +dorsal).", "✓ DONE", "2026-06-10"],
                        ["Airframe / Coordinates (R1)", "Hull-frame standardisation: validated placements baked into all 8 primary STLs (tools/bake_hull_frame.py, header marker 'SerenityUAV HULL-FRAME R1'); serenity_assembly.py imports at identity; 48 scripts stamped with the hull-frame standard header. Exceptions: avionics KiCad, Skipper GCS, G-code. Open: nacelle port/stbd label swap vs wings; head-cargo joint axis re-verify.", "✓ DONE", "2026-06-11"],
                        ["Mission Profile", "10-step cargo mission and 3-step cyber-resilience criteria added to README.md.", "✓ DONE", "2026-06-10"],
                        ["Standards / CLAUDE.md", "Imperial-primary units formalised (lbm vs lbf); airspeed in knots (kt); hull-frame coordinate system canonically defined with validated placements.", "✓ DONE", "2026-06-10"],
                        ["Code Quality", "All Python scripts brought to flake8 compliance: E201/E122/E501/E251/F401/E231 violations resolved.", "✓ DONE", "2026-06-10"],
                        ["Docs", "README, PROJECT_INDEX, AVIONICS_PB2_REDESIGN, ARCHIVE_INDEX updated to Rev R. bom_revR.json/csv created. serenity-rev-q.jsx remains in current-specification/ as Rev Q reference.", "✓ DONE", "2026-06-10"],
                    ]}
                />
            </Card>

            <Card title="Quick Specs — Rev R Baseline" accent={C.accent}>
                <Table
                    cols={["Parameter", "Value", "Notes"]}
                    rows={[
                        ["Hull length",         "609.6 mm (24.00 in)",      "Serenity-class, misubisu geometry × 2.9294"],
                        ["Beam (nacelle tips)", "~486 mm",                  "Tip-to-tip across tilt axis"],
                        ["Height (landed)",     "182 mm",                   "To top of dorsal hull"],
                        ["Hull material",       "PETG shell + PU foam + CF skeleton", "2.5 mm skin, 2 lb/ft³ closed-cell foam fill"],
                        ["Propulsion",         "2× (2× 50 mm EDF @ 6S) nacelles + 1× 55 mm EDF @ 6S fuselage (Phase 11, cruise + RCS)", "Counter-rotating nacelle pairs"],
                        ["Nacelle tilt",       "0° (cruise) → 90° (hover) → 120° (backing)", "Hard stops −5° / 140°"],
                        ["Nozzle actuation",   "Passive gear train per nacelle; rear nozzle is FIXED canonical (no servo)", "M=1.0 sector → pinion → bevel → crown → iris ring (nacelles only)"],
                        ["Hover thrust (nacelles)",  "~4,464 g",            "4× 1,240 g × 0.9 stator; rear EDF is forward-thrust only"],
                        ["AUW (6S 4000 mAh)",  "~3,130 g (Phase 11)",      "Hover T/W ≈ 1.43 (nacelles only)"],
                        ["Avionics",           "8× PocketBeagle 2 Industrial (AM6254)", "4× FC (Pilot) + 4× CN (XO) — ALL v2"],
                        ["Cape variant",       "EMI-hardened v2 at ALL 8 positions",   "v2·v2·v2·v2 (Rev R baseline — Pilot/XO naming finalised)"],
                        ["Data buses",         "Ethernet RSTP · CAN FD · RS-485 · MIL-STD-1553B", "All 4 on every node"],
                        ["Radio links",        "SiK 915 MHz + LoRa 915 MHz + WiFi + XCVR 49 MHz", "All 4 on every CN node"],
                        ["Security",           "SLB9670 TPM 2.0 on all 8 nodes + ATF16V8BQL CPLD write-blocker", "Message signing + forensic log"],
                        ["Cargo bay",          "101.6 × 76.2 × 76.2 mm",  "Clamshell doors + N20 winch + auto-latch cradle"],
                        ["EMI protection",     "5 kV isolated transceivers on ALL 8 nodes", "IEC 62368-1 / VDE 0884-11 at every position"],
                        ["FAA registration",   "N00000 PLACEHOLDER",       "Replace before first untethered flight (14 CFR Part 48)"],
                        ["License",            "CC BY 4.0",                "Steve Griffing PE(CSE) CISSP-ISSEP CPP · 2026"],
                    ]}
                />
            </Card>

            <Card title="Design Revision History" accent={C.purple}>
                <Table
                    cols={["Rev", "Date", "Key Milestone"]}
                    accent={C.purple}
                    rows={[
                        ["A", "2026-04",  "Initial tiltrotor concept"],
                        ["B", "2026-04",  "Full system spec — battery, nav lights, antenna, BOM"],
                        ["C", "2026-04",  "70 mm EDFs + variable nozzle + build guide"],
                        ["D", "2026-04",  "CC BY 4.0 + write-blocker + HW NX + dual WiFi SMA + Zigbee/LoRa"],
                        ["E", "2026-04",  "Attribution + ft/kts/yd units + full license compliance"],
                        ["F", "2026-04",  "Nacelle nozzle gear coupling"],
                        ["G–H","2026-04", "MIL-STD-1553B adds as 4th active bus"],
                        ["I", "2026-04",  "CM3+ Nodes + dual VL53L5CX ToF + cargo gondola"],
                        ["J", "2026-04",  "XRP 3660-2700KV nacelle EDFs + Hobbywing 120A ESCs"],
                        ["K", "2026-05",  "8× PocketBeagle 2 (AM6254) + Cape-A/B + TPM ×8 + dual 80 mm EDFs"],
                        ["L", "2026-05",  "Dual 80 mm EDFs + PID governor + EDF options"],
                        ["M", "2026-05",  "PB2-I (AM6254) hardware upgrade; propulsion unchanged"],
                        ["N", "2026-05",  "24-inch hull + 50 mm tandem EDFs + 4-radial-scoop intake"],
                        ["O", "2026-05",  "CG-pivot nacelle (Z=83 mm) + M=1.0 gear train + S1223 wings"],
                        ["P", "2026-06",  "Cargo bay complete (doors + mounts + Rev S shell)"],
                        ["Q", "2026-06",  "Hardened avionics baseline — EMI-hardened v2 capes at ALL positions; v1 archived; old design variants archived"],
                        ["R", "2026-06",  "Naming finalisation (Pilot/XO); Flight Engineer PDB DRC-clean + gerbers; FreeCAD hull-frame validated; mission profile; CLAUDE.md standards — this revision"],
                    ]}
                />
            </Card>
        </div>
    );
}

/* ── Airframe tab ──────────────────────────────────────────────────────────── */
function TabAirframe() {
    return (
        <div>
            <Card title="Hull Dimensions & Geometry" accent={C.accent}>
                <Table
                    cols={["Parameter", "Value", "Notes"]}
                    rows={[
                        ["Overall length",      "609.6 mm (24.00 in)",   "QMx canon basis: 269 ft × 2.9294 scale"],
                        ["Beam tip-to-tip",     "~486 mm",               "Canon 170 ft proportion at 2.9294×"],
                        ["Height (landed)",     "182 mm",                "Canon 79 ft proportion at 2.9294×"],
                        ["Hull scale factor",   "2.9294×",               "From Thingiverse model 7330462 (misubisu)"],
                        ["Shell wall",          "2.5 mm PETG",           "Uniform; generated by blender_shells_v3.py"],
                        ["Foam fill",           "2 lb/ft³ PU closed-cell", "X-30 two-part, 4× expansion; ~0.7 L total"],
                        ["Keel",                "CF flat bar 6×3 mm, 620 mm", "Backbone + 49 MHz counterpoise"],
                        ["Wing spars",          "CF tube 12 mm OD × 1.5 mm wall, 2× 350 mm", "Through wing root pockets"],
                        ["Ring frames",         "2 mm CF plate, 5 stations", "91, 165, 251, 320, 388 mm from nose"],
                        ["Hull sections",       "5 shell prints: head, middle, cargo, neck-intake, legs/feet", "All PETG 0.20 mm / 8% gyroid"],
                    ]}
                />
            </Card>

            <Card title="Access Panels" accent={C.teal}>
                <Table
                    cols={["Panel", "Bay", "Station (from nose)", "Access Type", "Contents"]}
                    accent={C.teal}
                    rows={[
                        ["A — Shepherd's room (nose)",   "Bay A", "~0–91 mm",   "Screw/bayonet", "CN1 (XO) + FC1 (Pilot); GPS coax; SiK/LoRa radios"],
                        ["B — Inara's shuttle (fwd dors)","Bay B", "~91–165 mm", "Screw/bayonet", "CN2 (XO) + FC2 (Pilot); GPS coax"],
                        ["C (wing root)",                 "Bay C", "~165–251 mm","Hinge+latch",   "ESC pairs, servo leads, wing spar access"],
                        ["D — River's room (aft dorsal)", "Bay D", "~251–320 mm","Screw/bayonet", "CN3 (XO) + FC3 (Pilot)"],
                        ["E — Simon's medbay (aft svc)",  "Bay E", "~320–388 mm","Screw/bayonet", "CN4 (XO) + FC4 (Pilot)"],
                        ["F (engine bell)","Bay F","~388–600 mm","Magnet+snap",   "55 mm EDF, 50A ESC, plenum, canonical nozzle, 4× RCS valves (Phase 11)"],
                    ]}
                />
                <div style={{ marginTop: 8, fontFamily: M, fontSize: 11, color: C.dimmer }}>
                    All bays: XO (CN lower) + Pilot (FC upper). Uniform v2 EMI hardening at all positions.
                    Panel lids: PETG 0.20 mm / 100% infill. Gasket: 3M 4016 closed-cell foam tape on frame lip.
                </div>
            </Card>

            <Card title="Canonical Print Schedule — Rev R" accent={C.yellow}>
                <Table
                    cols={["STL", "Material", "Layer / Infill", "Qty", "Est. Mass"]}
                    accent={C.yellow}
                    rows={[
                        ["head_shell24.stl",                "PETG",    "0.20 mm / 8% gyroid",    "1",  "95 g"],
                        ["middle_canonical_shell24.stl",    "PETG",    "0.20 mm / 8% gyroid",    "1",  "135 g"],
                        ["cargo_sect_shell24.stl (Rev S)",  "PETG",    "0.20 mm / 8% gyroid",    "1",  "165 g"],
                        ["rear_neck_intake_shell24.stl",    "PETG",    "0.20 mm / 8% gyroid",    "1",  "225 g"],
                        ["legs_scaled24.stl",               "CF-PETG", "0.15 mm / 30%",          "1",  "60 g"],
                        ["feet_x_4_scaled24.stl",           "TPU 95A", "0.25 mm / 40%",          "1",  "80 g"],
                        ["neck_intake_frame.stl",           "CF-PETG", "0.15 mm / 40% / 4 walls","1",  "85 g"],
                        ["aft_edf_plenum.stl",              "PETG",    "0.20 mm / 20% gyroid",   "1",  "75 g"],
                        ["edf_55_motor_mount.stl",          "CF-PETG", "0.15 mm / 40% / 4 walls","1",  "25 g"],
                        ["edf_55_thrust_tube.stl",          "PETG",    "0.20 mm / 20% gyroid",   "1",  "20 g"],
                        ["Access panel frames A–F + lids",    "PETG",    "0.20 mm / 100%",         "1 set","~90 g"],
                        ["s_eng_left_stator_shell24_revo.stl","CF-PETG", "0.15 mm / 25% / 4 walls","1",  "132 g"],
                        ["s_eng_right_stator_shell24_revo.stl","CF-PETG","0.15 mm / 25% / 4 walls","1",  "132 g"],
                        ["s_wing_nacelle_pylon_port/stbd.stl","CF-PETG", "0.15 mm / 40% / 4 walls","2",  "52 g ea"],
                        ["wings_s1223_revo.stl (port+stbd)","CF-PETG", "0.15 mm / 40% / 4 walls","2",  "118 g ea"],
                        ["nacelle_nozzle_petal.stl",          "PETG",    "0.20 mm / 20% gyroid",   "16", "2 g ea"],
                        ["nacelle_nozzle_ring.stl",           "CF-PETG", "0.15 mm / 40%",          "2",  "18 g ea"],
                        ["rear_nozzle_canonical.stl",         "CF-PETG", "0.15 mm / 30% / 4 walls","1",  "30 g"],
                        ["rcs_thruster_nozzle.stl",           "CF-PETG", "0.15 mm / 40% / 4 walls","4",  "8 g ea"],
                        ["rcs_distribution_manifold.stl",     "PETG",    "0.20 mm / 30%",          "1",  "25 g"],
                        ["rcs_valve_bracket.stl",             "CF-PETG", "0.15 mm / 40%",          "4",  "10 g ea"],
                        ["nacelle_sector_gear.stl",           "Resin SLA","0.05 mm / solid",       "2",  "8 g ea"],
                        ["nacelle_pinion.stl (drive + crown)","Resin SLA","0.05 mm / solid",       "4",  "3 g ea"],
                        ["nacelle_bevel_pair.stl",            "Resin SLA","0.05 mm / solid",       "4",  "4 g ea"],
                        ["nacelle_bevel_housing.stl",         "CF-PETG", "0.15 mm / 40%",          "2",  "12 g ea"],
                        ["cargo_door_port.stl",               "CF-PETG", "0.15 mm / 40% / 4 walls","1",  "45 g"],
                        ["cargo_door_stbd.stl",               "CF-PETG", "0.15 mm / 40% / 4 walls","1",  "45 g"],
                        ["cargo_winch_motor_mount.stl",       "CF-PETG", "0.15 mm / 40%",          "1",  "25 g"],
                        ["cargo_winch_spool.stl",             "PETG",    "0.20 mm / 40%",          "1",  "15 g"],
                        ["cargo_door_servo_bracket.stl",      "CF-PETG", "0.15 mm / 40%",          "1",  "10 g"],
                        ["cargo_release_servo_bracket.stl",   "CF-PETG", "0.15 mm / 40%",          "1",  "10 g"],
                        ["cargo_drv8833_tray.stl",            "PETG",    "0.20 mm / 30%",          "1",  "8 g"],
                        ["cargo_cradle_autolatch.stl",        "PETG",    "0.20 mm / 30%",          "1",  "18 g"],
                        ["cargo_gps_retention_ring.stl",      "PETG",    "0.20 mm / 40%",          "1",  "5 g"],
                        ["cargo_fpv_bezel.stl",               "PETG",    "0.20 mm / 40%",          "1",  "8 g"],
                    ]}
                />
            </Card>
        </div>
    );
}

/* ── Propulsion tab ────────────────────────────────────────────────────────── */
function TabPropulsion() {
    return (
        <div>
            <Card title="Nacelle EDFs — 50 mm Tandem Series" accent={C.orange}>
                <Table
                    cols={["Parameter", "Value", "Notes"]}
                    accent={C.orange}
                    rows={[
                        ["EDF size",            "50 mm",           "Verify OD fits 55–56 mm nacelle bore ID before ordering"],
                        ["Count",               "4 total (2 per nacelle)", "Tandem/series in shared bore"],
                        ["Voltage",             "6S (22.2 V nominal)", ""],
                        ["EDF1 position",       "Z=22..72 mm from intake", "Upstream; port CW / stbd CCW from intake"],
                        ["EDF2 position",       "Z=98..143 mm from intake", "Downstream"],
                        ["Inter-stage stator",  "11-fin twisted, Z=75..95 mm", "CF-PETG, integral to nacelle shell; 33° vane angle"],
                        ["Counter-rotation",    "Port CW, stbd CCW from intake", "Zero net torque reaction on fuselage"],
                        ["Thrust per EDF",      "~1,240 g",        "XFly Galaxy X5 50 mm 12-blade 6S 3200 KV"],
                        ["Thrust per nacelle",  "~2,232 g",        "2 EDFs in tandem × 0.9 stator efficiency"],
                        ["Total nacelle thrust","~4,464 g",        "Both nacelles combined (hover/vertical)"],
                        ["Canonical SCAD",      "nacelle_pod_50mm_tandem.scad", "Parametric; SWIRL_DIR=1 (port), -1 (stbd)"],
                    ]}
                />
            </Card>

            <Card title="Rear EDF — 55 mm (Phase 11 deferred)" accent={C.red}>
                <Table
                    cols={["Parameter", "Value", "Notes"]}
                    accent={C.red}
                    rows={[
                        ["EDF size",     "55 mm",          "Single unit, tail cone"],
                        ["Voltage",      "6S",             ""],
                        ["Fan thrust",   "~1,500 g",       "~1,275 g net forward after ~15% RCS bleed"],
                        ["Thrust axis",  "Horizontal (forward/cruise) only", "Canonical nozzle fires aft — NOT counted in hover T/W"],
                        ["Nozzle",       "Fixed canonical elliptical 2.06×1.76 in", "52.3×44.7 mm exit (~1,836 mm²); no iris, no servo"],
                        ["RCS",          "4× bleed-air jets (~15% flow)", "Pitch/yaw attitude authority; SG90-class proportional valves"],
                        ["Location",     "Station ~430 mm from nose", "Inside tail cone, Panel F"],
                        ["Intake",       "Reduced-area neck scoops at station ~310 mm", "neck_intake_frame + aft_edf_plenum (regen for 55 mm)"],
                        ["Fan area",     "~2,376 mm²",     "55 mm fan"],
                        ["Scoop capture area","~3,090 mm²","Ratio ~1.3× duct-match"],
                        ["Motor mount",  "edf_55_motor_mount.stl", "CF-PETG 3-arm spider"],
                        ["Thrust tube",  "edf_55_thrust_tube.stl", "PETG 55 mm ID duct"],
                        ["ESC",          "50A 6S BLHeli32","~65A burst; XT60; F_ESC5 = 60A MIDI"],
                    ]}
                />
            </Card>

            <Card title="Nacelle Tilt Mechanism" accent={C.teal}>
                <Table
                    cols={["Parameter", "Value", "Notes"]}
                    accent={C.teal}
                    rows={[
                        ["Travel",       "0° (cruise) → 90° (hover) → 120° (backing)", "Hard stops at −5° and 140°"],
                        ["Pivot Z",      "83 mm from intake (nacelle CG)", "Eliminates gravity torque on servo in all attitudes"],
                        ["Bearing",      "MF104ZZ 4×10×4 mm flanged, 2 per nacelle", "Press-fit; pivot rod = 4 mm CF rod (fixed)"],
                        ["Servo",        "≥25 kg·cm @ 6V digital metal-gear, 2×", "Fuselage-mounted, one per nacelle"],
                        ["Hard stops",   "CF-PETG blocks bonded at −5° and 140°", "Servo stalls at stop; does not strip"],
                    ]}
                />
            </Card>

            <Card title="Nozzle Gear Train — M=1.0 Passive" accent={C.gold}>
                <Table
                    cols={["Gear", "Module", "Teeth", "Pitch R", "Function"]}
                    accent={C.gold}
                    rows={[
                        ["Sector gear",      "M=1.0","38T arc","22 mm", "FIXED to tilt bracket; Pinion A rolls along arc"],
                        ["Drive Pinion A",   "M=1.0","12T",    "6 mm",  "On nacelle at pivot Z=83 mm; MR63ZZ shafts"],
                        ["Bevel A (transverse)","M=1.0","14T", "7 mm",  "45° cone; on Pinion A shaft"],
                        ["Bevel B (longitudinal)","M=1.0","14T","7 mm", "45° cone; keyed to 3 mm CF shaft, Z=83→133 mm"],
                        ["Crown Pinion",     "M=1.0","12T",    "6 mm",  "At Z=133 mm; drives nozzle ring rack teeth"],
                        ["Nozzle ring rack", "M=1.0","22T arc","28 mm (eff.)", "Inner face of rotating iris ring; 70.7° travel"],
                    ]}
                />
                <div style={{ marginTop: 10, fontFamily: M, fontSize: 12, color: C.text }}>
                    <span style={{ color: C.gold }}>Ratio: </span>
                    90° nacelle tilt × (22/6) = 330° Pinion A → ×1.0 bevel → 330° shaft → ×(6/28) = 70.7° iris ring.
                    Nozzle fully closed at 0° (hull-matched petal surface); fully open at 90° (hover aesthetic).
                </div>
            </Card>

            <Card title="Thrust & Weight Budget" accent={C.green}>
                <Table
                    cols={["Item", "Value", "Notes"]}
                    accent={C.green}
                    rows={[
                        ["Nacelle hover thrust","~4,464 g","2× (2× 50 mm EDF) = 4 × 1,240 g × 0.9 stator — VERTICAL (hover)"],
                        ["Rear EDF thrust",  "~1,275 g", "55 mm 6S, net forward after RCS bleed — HORIZONTAL (cruise), not summed into hover"],
                        ["Hull prints + foam","~1,150 g","All shell sections + access panels + foam"],
                        ["Nacelle assemblies","~440 g",  "2× nacelle shells + EDFs + ESCs + gear + nozzle"],
                        ["Avionics",         "~460 g",   "8× PB2-I + 4× Pilot + 4× XO + 4× Commo + GPS×4 + radios"],
                        ["Servos + linkage", "~155 g",   "2× tilt servo + pushrods (4× RCS valves are Phase 11)"],
                        ["Power (6S 4000mAh)","~750 g",  "Primary flight battery"],
                        ["Rear EDF system (Phase 11)","~360 g","55 mm EDF + 50A ESC + canonical nozzle + 4 RCS jets/valves + plenum/mount"],
                        ["Misc hardware",    "~230 g",   "CF stock, fasteners, wiring, ESCs, bearings"],
                        ["AUW Phases 5–10",  "~2,768 g", "Hover T/W ≈ 1.61 (4,464 ÷ 2,768)"],
                        ["AUW Phase 11",     "~3,130 g", "Hover T/W ≈ 1.43 (4,464 ÷ 3,130) — rear EDF not counted"],
                        ["Max hover payload at T/W=1.0","~1,696 g","Phases 5–10 (4,464 − 2,768)"],
                    ]}
                />
                <div style={{ marginTop: 8, fontFamily: M, fontSize: 11, color: C.dimmer }}>
                    Rev R1: rear EDF 120 mm → 55 mm with a fixed canonical elliptical nozzle + 4 RCS bleed jets.
                    It now provides forward-flight (cruise) thrust and pitch/yaw attitude authority — NOT hover lift —
                    so it is not summed into hover T/W. Hover remains nacelle-driven (T/W ≈ 1.61 Phases 5–10).
                </div>
            </Card>
        </div>
    );
}

/* ── Avionics tab ──────────────────────────────────────────────────────────── */
function TabAvionics() {
    return (
        <div>
            <Card title="8-Node Cooperative Architecture — Rev R: All v2 (Pilot / XO)" accent={C.accent}>
                <div style={{ fontFamily: M, fontSize: 12, color: C.text, marginBottom: 12, lineHeight: 1.8 }}>
                    Eight PocketBeagle 2 Industrial (AM6254) boards, split into two groups of four.
                    All nodes run the same base Linux image (from 64 GB eMMC — no OS microSD required).
                    Real-time tasks use the AM6254 PRU-ICSS cores. Role assignment is dynamic:
                    CAN FD heartbeat priority arbitration at boot elects FC master and CN master independently.
                    Any node can fail over for any role.
                    <br /><br />
                    <span style={{ color: C.green }}>Rev Q change:</span> All 8 positions use EMI-hardened v2 capes
                    (Pilot / XO + Commo). Placement is uniform v2·v2·v2·v2 nose to tail.
                    Cape-A-1, Cape-B-1, XCVR-49MHZ-1 designs are archived.
                    <br />
                    <span style={{ color: C.green }}>Rev R change:</span> Cape-A-2 / Cape-B-2 generic designators retired.
                    Pilot and XO are now the sole active cape names in all documentation, design files, and gerbers.
                </div>
                <Table
                    cols={["Group", "Count", "Cape", "Primary Responsibility"]}
                    rows={[
                        ["FC1–FC4", "4", "Pilot (EMI-hardened Sensor/Flight)", "Flight control, IMU/GPS/baro fusion, ESC PID governor, ToF OA, actuator PWM"],
                        ["CN1–CN4", "4", "XO (EMI-hardened Comms/Payload)", "Radio links (all 4), system logging, cargo/payload control, MAVLink routing"],
                    ]}
                />
            </Card>

            <Card title="PocketBeagle 2 Industrial (AM6254) Platform" accent={C.purple}>
                <Table
                    cols={["Parameter", "Specification"]}
                    accent={C.purple}
                    rows={[
                        ["Board",         "PocketBeagle 2 Industrial · MFR 100003007 · DigiKey 2820-100003007-ND · $51.03 ea"],
                        ["SoC",           "TI AM6254 (Sitara)"],
                        ["App cores",     "4× Cortex-A53 @ up to 1.4 GHz"],
                        ["RT co-proc",    "1× Cortex-M4F (bare-metal / FreeRTOS) — PID governor at 500 Hz"],
                        ["PRU-ICSS",      "2× PRU @ 250 MHz + 1× RTU — DSHOT1200 + MIL-STD-1553B encoder/decoder"],
                        ["RAM",           "1 GB DDR4"],
                        ["Storage",       "64 GB eMMC (OS + runtime) — no OS microSD needed"],
                        ["CAN",           "2× MCAN ISO 11898-1, CAN FD capable"],
                        ["Ethernet",      "CPSW3G — 2 external RGMII/RMII MAC ports for RSTP ring"],
                        ["Temperature",   "−40°C to +85°C industrial"],
                        ["Mass",          "12.7 g per board"],
                    ]}
                />
            </Card>

            <Card title="Pilot — FC Node (EMI-Hardened Flight Control / Sensor)" accent={C.green}>
                <div style={{ fontFamily: M, fontSize: 11, color: C.green, marginBottom: 8 }}>
                    Rev R: Active design. Cape-A-1 and CAPE-A-2 designators archived. All 4 FC positions use Pilot.
                </div>
                <Table
                    cols={["Feature", "Detail"]}
                    accent={C.green}
                    rows={[
                        ["Size",          "55×35 mm, 4-layer KiCad (Pilot gerbers — active)"],
                        ["CAN FD",        "ISOW1044BDFMR 5 kV isolated CAN FD transceiver (TI) — IEC 62368-1 / VDE 0884-11 certified"],
                        ["RS-485",        "ADM2795EBRWZ 5 kV isolated RS-485 (ADI) — half-duplex, 1 Mbps"],
                        ["Ethernet",      "ADIN1300BCPZ 1000BASE-T PHY + 2× ISO7642FDWRR 6-ch digital isolators + Würth 749010012A transformer; JST GH 4P (no RJ45)"],
                        ["IMU",           "ICM-42688-P (SPI) — 6-DOF; 32 kHz ODR"],
                        ["Barometer",     "BMP388 / BMP390 (SPI) — altitude hold PID"],
                        ["GPS",           "u-blox M10Q via UART — NMEA/UBX; HDOP gating ≤1.5"],
                        ["ESC PWM",       "EHRPWM / PRU-ICSS — BDSHOT600; 5 outputs (4× nacelle + 1× rear)"],
                        ["Servo PWM",     "2 channels active — 2× nacelle tilt (+4× RCS valves at Phase 11)"],
                        ["ToF array",     "TCA9548A 8-ch I²C mux + MCP23008 XSHUT expander → 6× VL53L5CX per node"],
                        ["TPM",           "SLB9670 TPM 2.0 (SPI) — attestation + HMAC signing"],
                        ["Tamper mesh",   "F.Cu / B.Cu TMESH_P/N nets routed to TPM GPIO — physical intrusion detect"],
                        ["MIL-STD-1553", "PRU Manchester II encoder/decoder; FC1=BC, FC2=standby BC"],
                        ["ADC (ESC telem)","74HC4051 8:1 mux — BDSHOT telemetry demux for 4 ESCs"],
                        ["DTS overlay",   "k3-am6254-pocketbeagle2-serenity-cape-a2.dts (avionics/firmware/dts/cape-a/)"],
                    ]}
                />
            </Card>

            <Card title="XO — CN Node (EMI-Hardened Comms / Logging / Payload)" accent={C.pink}>
                <div style={{ fontFamily: M, fontSize: 11, color: C.green, marginBottom: 8 }}>
                    Rev R: Active design. Cape-B-1 and CAPE-B-2 designators archived. All 4 CN positions use XO.
                </div>
                <Table
                    cols={["Feature", "Detail"]}
                    accent={C.pink}
                    rows={[
                        ["Size",           "55×35 mm, 4-layer KiCad (XO gerbers — active)"],
                        ["CAN FD",         "ISOW1044BDFMR 5 kV isolated (same as Pilot)"],
                        ["RS-485",         "ADM2795EBRWZ 5 kV isolated (same as Pilot)"],
                        ["Ethernet",       "ADIN1300BCPZ + ISO7642FDWRR × 2 + Würth transformer (same as Pilot)"],
                        ["SiK radio",      "SiK 915 MHz MAVLink — belly port SMA bulkhead"],
                        ["LoRa radio",     "RFM95W 915 MHz backup — belly stbd SMA bulkhead"],
                        ["WiFi/BT",        "TI WL1837MOD 2.4/5 GHz — dorsal fwd SMA bulkhead"],
                        ["XCVR-49MHZ",     "Commo sub-module — 49 MHz AX.25 RC (EMI-hardened)"],
                        ["Log μSD",        "XO microSD slot — hardware write-blocked via CPLD"],
                        ["CPLD",           "ATF16V8BQL — hardware-enforced non-executable log storage"],
                        ["NOR flash",      "W25Q128JV 128 Mb — circular log overflow buffer"],
                        ["TPM",            "SLB9670 TPM 2.0 — key material for log signing + HMAC on AX.25 payloads"],
                        ["Tamper mesh",    "Same as Pilot"],
                        ["Cargo GPIO",     "DRV8833 winch H-bridge + HX711 load cell ADC via XO GPIO"],
                        ["MIL-STD-1553",  "PRU Manchester II; CN1=RT 0x01, CN2–CN4 RT addresses"],
                        ["DTS overlay",   "k3-am6254-pocketbeagle2-serenity-cape-b2.dts (avionics/firmware/dts/cape-b/)"],
                    ]}
                />
            </Card>

            <Card title="Commo — EMI-Hardened 49 MHz AX.25 Transceiver" accent={C.orange}>
                <div style={{ fontFamily: M, fontSize: 11, color: C.green, marginBottom: 8 }}>
                    Rev R: Active design. XCVR-49MHZ-1 archived. All 4 CN positions use XCVR-49MHZ-2.
                </div>
                <Table
                    cols={["Feature", "Detail"]}
                    accent={C.orange}
                    rows={[
                        ["Size",         "55×35 mm, 4-layer PCB"],
                        ["CMC",          "SRF2012-100Y common-mode choke on antenna feed — radiated immunity"],
                        ["TVS",          "PRTR5V0U2X TVS on signal lines — transient suppression"],
                        ["X2Y cap",      "X2Y bridging capacitor on antenna feed — EMI filtering"],
                        ["Ferrite bead", "Würth 742792512 ferrite bead on +5V supply rail"],
                        ["Connector",    "JST GH 6P to XO J1 (replaces direct-coupled connection)"],
                        ["RF trace",     "Z₀ = 52.26 Ω — W=2.75 mm, H=1.6 mm, εr=4.5, T=35 µm — PASS [45–55 Ω]"],
                        ["Modem",        "TCM3105 AFSK modem — same as XCVR-49MHZ-1"],
                        ["PA / LNA",     "MGA-82563 LNA, PE4259 TX/RX switch — same as XCVR-49MHZ-1"],
                        ["DDS",          "Si5351A + TCXO reference — ±0.005% freq stability (FCC 47 CFR 95.655)"],
                    ]}
                />
            </Card>

            <Card title="Flight Engineer — Power Distribution Board (Rev A)" accent={C.lime}>
                <div style={{ fontFamily: M, fontSize: 11, color: C.green, marginBottom: 8 }}>
                    Rev R: Added. Flight Engineer PDB KiCad files generated; DRC clean (0 shorts); gerbers produced 2026-06-10.
                </div>
                <Table
                    cols={["Feature", "Detail"]}
                    accent={C.lime}
                    rows={[
                        ["Board name",     "Flight Engineer — Power Distribution Board"],
                        ["Callsign",       "\"Everything is shiny.\" — Flight Engineer Frye, Firefly-class vessel Serenity"],
                        ["KiCad files",    "avionics/kicad/FlightEngineer.kicad_{pro,sch,pcb}"],
                        ["Design notes",   "avionics/kicad/FlightEngineer.md"],
                        ["Gerbers",        "avionics/kicad/gerbers/ — generated 2026-06-10"],
                        ["DRC status",     "✓ 0 shorts, 0 unconnected (schematic level) — 2026-06-10"],
                        ["Function",       "Primary 6S battery power distribution; dual BEC outputs (5 V and 3.3 V); current sensing per rail; bus protection MOSFETs"],
                        ["Revision",       "Rev A — first hardware revision"],
                    ]}
                />
            </Card>

            <Card title="Bay Assignments — Rev R (All v2)" accent={C.yellow}>
                <Table
                    cols={["Bay / Room", "Station", "Lower CN (XO)", "Upper FC (Pilot)", "Notes"]}
                    accent={C.yellow}
                    rows={[
                        ["A — Shepherd's room (nose)",   "0–91 mm",   "CN1", "FC1", "5 kV CAN FD/RS-485/ETH isolation; GPS1; SiK + LoRa + WiFi + Commo; CAN FD bus start 120Ω"],
                        ["B — Inara's shuttle (fwd dors)","91–165 mm", "CN2", "FC2", "5 kV isolation; GPS2; Commo"],
                        ["D — River's room (aft dorsal)", "251–320 mm","CN3", "FC3", "5 kV isolation; GPS3; Commo"],
                        ["E — Simon's medbay (aft svc)",  "320–388 mm","CN4", "FC4", "5 kV CAN FD/RS-485/ETH isolation; GPS4; CAN FD bus end 120Ω permanent"],
                    ]}
                />
                <div style={{ marginTop: 8, fontFamily: M, fontSize: 11, color: C.dimmer }}>
                    Rev R uniform v2 placement provides 5 kV galvanic isolation at ALL 8 nodes.
                    Bus order: CN1→FC1→CN2→FC2→CN3→FC3→CN4→FC4.
                    Any single bay power failure leaves ≥2 FC + ≥2 CN on both sides of the break.
                    Bay C is the wing root bay (ESCs, servos, spar access — no PCB nodes).
                </div>
            </Card>
        </div>
    );
}

/* ── Comms tab ─────────────────────────────────────────────────────────────── */
function TabComms() {
    return (
        <div>
            <Card title="Wired Inter-Node Data Buses" accent={C.accent}>
                <Table
                    cols={["Bus", "Protocol", "Speed", "Topology", "Notes"]}
                    rows={[
                        ["Ethernet", "IEEE 802.3u · ADIN1300BCPZ 1000BASE-T PHY (via ISO7642FDWRR isolation)", "1 Gbps PHY / 100 Mbps effective", "RSTP ring (8 nodes, self-healing)", "Ring closes at FC4→CN1; single-link failure heals in <1 s; 5 kV isolated at all 8 nodes"],
                        ["CAN FD",   "ISO 11898-1:2015 · ISOW1044BDFMR 5 kV isolated", "1 Mbps arb / 8 Mbps data", "Linear daisy-chain; 120Ω at CN1 + FC4", "Heartbeat 0x001–0x008; cross-node RPM sync + OA halt broadcast; 5 kV isolated all nodes"],
                        ["RS-485",   "EIA-485 · ADM2795EBRWZ 5 kV isolated", "1 Mbps", "Multi-drop; 120Ω at CN1 + FC4", "Structured frame: header/payload/CRC; 5 kV isolated all nodes"],
                        ["MIL-STD-1553B","PRU Manchester II encoder/decoder", "1 Mbps", "BC/RT: FC1=BC, FC2=standby BC; all others RT", "All 8 RT addresses respond within 9 µs"],
                    ]}
                />
            </Card>

            <Card title="External Radio Links" accent={C.orange}>
                <Table
                    cols={["Link", "Technology", "Band", "Use Case", "Regulatory"]}
                    accent={C.orange}
                    rows={[
                        ["SiK 915 MHz",  "SiK v2 MAVLink",           "915 MHz ISM", "Primary GCS telemetry (MAVLink)", "FCC Part 15 / module FCC ID required"],
                        ["LoRa 915 MHz", "RFM95W / LoRa",             "915 MHz ISM", "Backup GCS telemetry + long-range", "FCC Part 15 / module FCC ID required"],
                        ["WiFi 2.4/5GHz","TI WL1837MOD 802.11b/g/n/ac","ISM", "GCS app link; firmware update; video stream", "FCC Part 15 / WL1837MOD certified"],
                        ["XCVR 49 MHz",  "Commo AX.25 AFSK",  "49.830–49.890 MHz", "RC command link (backup)", "FCC Part 15 §15.235 (not Part 95 RCRS — REF-FCC-003); FCC equipment authorization required before airborne TX"],
                    ]}
                />
            </Card>

            <Card title="XCVR-49MHZ Antenna System" accent={C.purple}>
                <Table
                    cols={["Element", "Spec", "Notes"]}
                    accent={C.purple}
                    rows={[
                        ["Top wire",       "0.3 mm SS wire, ~470 mm dorsal spine", "Forward post ~120 mm → aft post ~600 mm from nose"],
                        ["Forward post",   "PETG mast, base-loading coil 38 µH + LC pi-net", "Bonded at dorsal ~120 mm; 3 mm clearance from GPS patch"],
                        ["Aft post",       "PETG mast, ceramic bead insulator", "Top of rear nozzle cone; insulated (open-circuit) end"],
                        ["Counterpoise",   "CF keel bar 6×3 mm, 620 mm", "Connected to Commo GND on XO"],
                        ["XCVR Z₀",        "52.26 Ω for W=2.75 mm, H=1.6 mm, εr=4.5, T=35 µm", "PASS [45–55 Ω] — verified by check_impedance.py 2026-05-30"],
                    ]}
                />
            </Card>
        </div>
    );
}

/* ── Cargo tab ─────────────────────────────────────────────────────────────── */
function TabCargo() {
    return (
        <div>
            <Card title="Cargo System — Rev P Baseline (unchanged in Rev Q)" accent={C.green}>
                <Table
                    cols={["Item", "Status", "Notes"]}
                    accent={C.green}
                    rows={[
                        ["cargo_sect_shell24.stl (Rev S)", "✓ DONE", "Belly opening 100×165 mm; 2× hinge-pin blocks; 2× SG90 servo pads; 4× latch-catch lips"],
                        ["cargo_door_port.stl",   "✓ DONE", "CF-PETG; 8-barrel piano hinge; 3 mm CF rod; 3.15 mm bore"],
                        ["cargo_door_stbd.stl",   "✓ DONE", "Mirror of port door"],
                        ["cargo_winch_motor_mount.stl", "✓ DONE", "N20 motor press-fit; 4× M2.5 boss pattern"],
                        ["cargo_winch_spool.stl", "✓ DONE", "Dyneema SK75 0.5 mm winding groove"],
                        ["cargo_door_servo_bracket.stl", "✓ DONE", "SG90 4× M2.5 pilot holes; bell-crank pivot boss"],
                        ["cargo_release_servo_bracket.stl", "✓ DONE", "SG90 release arm socket"],
                        ["cargo_drv8833_tray.stl","✓ DONE", "DRV8833 snap-fit tray"],
                        ["cargo_cradle_autolatch.stl","✓ DONE","Spring-latch auto-lock; HX711 load-cell pocket"],
                        ["cargo_gps_retention_ring.stl","✓ DONE","GPS module retention ring"],
                        ["cargo_fpv_bezel.stl",   "✓ DONE", "FPV camera bezel; M2.5 mount"],
                        ["cargo_gondola_shell.stl","○ OPEN", "BLOCKS Phase 8 — s_cargo_gondola_shell.scad not yet created"],
                    ]}
                />
            </Card>

            <Card title="Cargo Bay Geometry" accent={C.teal}>
                <Table
                    cols={["Parameter", "Value", "Notes"]}
                    accent={C.teal}
                    rows={[
                        ["Bay internal dims",   "101.6 × 76.2 × 76.2 mm (4 × 3 × 3 in)", ""],
                        ["Door opening",        "100 × 165 mm belly opening", "Station 165..330 mm"],
                        ["Door hinge pin",      "3 mm CF rod", "8-barrel piano hinge; 3.15 mm bore (clearance)"],
                        ["Latch-catch lips",    "4× lips at Z=42/122 mm per X frame edge", ""],
                        ["Max payload",         "~400 g nominal / ~250 g Phase 8 target","Within hover T/W ≈ 1.61 (Phases 5–10)"],
                    ]}
                />
            </Card>
        </div>
    );
}

/* ── Security tab ──────────────────────────────────────────────────────────── */
function TabSecurity() {
    return (
        <div>
            <Card title="Security Architecture" accent={C.red}>
                <div style={{ fontFamily: M, fontSize: 12, color: C.text, lineHeight: 1.8, marginBottom: 12 }}>
                    Every message is authenticated. Everything is logged.
                    Hardware-enforced non-executable storage prevents post-flight log modification.
                    Rev R: uniform 5 kV galvanic isolation on all bus transceivers at all 8 nodes.
                </div>
                <Table
                    cols={["Layer", "Implementation", "Coverage"]}
                    accent={C.red}
                    rows={[
                        ["TPM 2.0",              "SLB9670 on every Pilot and XO (8 chips total)", "Unique key material per node; HMAC-SHA256 on all flight-critical CAN FD messages; PCR extend on each boot"],
                        ["CPLD write-blocker",   "ATF16V8BQL on every XO (4 chips total)", "Hardware-enforced read-only append to log μSD; NX enforcement; cannot be bypassed in firmware"],
                        ["Message signing",      "TPM-bound HMAC on all outbound inter-node CAN FD frames", "Unauthenticated messages discarded by all nodes"],
                        ["AX.25 HMAC",           "TPM-bound HMAC-SHA256 on every XCVR-49MHZ AX.25 packet", "Receiver nodes verify before acting on RC commands"],
                        ["5 kV isolation",       "ISOW1044BDFMR + ADM2795EBRWZ + ADIN1300BCPZ at all 8 nodes", "Galvanic isolation prevents conducted EMI/transient propagation across bus boundaries"],
                        ["NOR flash log",        "W25Q128JV 128 Mb circular log on XO", "Overflow buffer for log μSD; also write-blocked; NX enforced"],
                        ["Tamper mesh",          "F.Cu/B.Cu TMESH_P/N copper nets on Pilot + XO", "Physical intrusion detection routed to SLB9670 TPM GPIO"],
                        ["Boot measurement",     "TPM PCR extend on each boot stage", "Detected replay or firmware modification flagged to ground station"],
                        ["Log integrity",        "SHA-256 hash chain on all log records", "Forensically sound; record tampering detectable"],
                    ]}
                />
            </Card>

            <Card title="Forensic Logging Note" accent={C.orange}>
                <div style={{ fontFamily: M, fontSize: 12, color: C.dimmer, lineHeight: 1.8 }}>
                    The write-blocker and NX-enforcement hardware are intended to support forensic
                    data integrity in UAV operations contexts. They are <strong style={{ color: C.orange }}>NOT</strong> certified
                    forensic tools per NIST/SWGDE standards. Do not use this design as the sole
                    mechanism for evidence preservation in legal proceedings without independent
                    verification of the implementation against your jurisdiction's evidence handling requirements.
                </div>
            </Card>

            <Card title="TPM Provisioning Checklist" accent={C.purple}>
                <Table
                    cols={["Node", "Bay", "Cape", "TPM Action"]}
                    accent={C.purple}
                    rows={[
                        ["CN1", "A — Shepherd's room", "XO", "TPM clear → generate endorsement key → extend PCR0 on first boot"],
                        ["FC1", "A — Shepherd's room", "Pilot", "Same; also bind HMAC signing key to FC1 endorsement key"],
                        ["CN2", "B — Inara's shuttle", "XO", "Same as CN1"],
                        ["FC2", "B — Inara's shuttle", "Pilot", "Same as FC1"],
                        ["CN3", "D — River's room", "XO", "Phase 7 — provision after board installation"],
                        ["FC3", "D — River's room", "Pilot", "Phase 7"],
                        ["CN4", "E — Simon's medbay", "XO", "Phase 7"],
                        ["FC4", "E — Simon's medbay", "Pilot", "Phase 7"],
                    ]}
                />
                <div style={{ marginTop: 8, fontFamily: M, fontSize: 11, color: C.red }}>
                    ⚠ TPM 2.0 provisioning is non-reversible without a full board re-spin.
                    Provision each node before installation, verify CPLD write-blocker function,
                    then install. Do NOT provision after foam pour.
                </div>
            </Card>
        </div>
    );
}

/* ── Regulatory tab ────────────────────────────────────────────────────────── */
function TabRegulatory() {
    return (
        <div>
            <Card title="FAA Compliance (United States)" accent={C.accent}>
                <Table
                    cols={["Requirement", "Standard", "Status", "Action Required"]}
                    rows={[
                        ["sUAS Registration",  "14 CFR Part 48",            "○ OPEN", "Register at FAA DroneZone; replace N00000 placeholder in decal_sheet.svg before first untethered flight"],
                        ["Remote Pilot Cert",  "14 CFR Part 107",           "— (operator)", "Verify 24-month knowledge test recurrency"],
                        ["Registration markings","14 CFR 47",               "○ OPEN", "Mark FAA reg number on airframe; visible without moving any part"],
                        ["AUW limit",          "14 CFR Part 48 — < 55 lbs", "✓ PASS", "AUW ~3,590 g = ~7.9 lbs — well within limit"],
                        ["Navigation lights",  "14 CFR 91.209 / ICAO Annex 2","✓ DESIGN OK","6× WS2812C: port RED, stbd GREEN, tail WHITE steady, belly WHITE strobe; ≥3 SM visibility"],
                        ["sUAS data plate",    "14 CFR 47",                 "○ OPEN", "Attach to airframe: operator name, contact info, registration number"],
                        ["LAANC / airspace",   "14 CFR 91 / FAA",           "— (pre-flight)", "Check LAANC authorization before each flight in Class B/C/D/E"],
                    ]}
                />
            </Card>

            <Card title="FCC Compliance (United States)" accent={C.orange}>
                <Table
                    cols={["System", "Standard", "Status", "Notes"]}
                    accent={C.orange}
                    rows={[
                        ["SiK 915 MHz",         "FCC Part 15 ISM",     "✓ PASS", "Module must carry FCC ID marking; verify before installation"],
                        ["LoRa RFM95W 915 MHz", "FCC Part 15 ISM",     "✓ PASS", "Module FCC ID required; verify"],
                        ["WiFi WL1837MOD",       "FCC Part 15 ISM",     "✓ PASS", "TI WL1837MOD certified; verify FCC ID on module"],
                        ["Commo",         "47 CFR Part 15 §15.235 (REF-FCC-003)", "○ OPEN", "Equipment authorization (FCC ID grant) required before airborne TX; pre-compliance checklist in WBS §1.3 Phase 4"],
                        ["49 MHz channels",      "47 CFR §15.235",       "○ OPEN", "Channel selection (49.830–49.890 MHz) set in CN firmware; verify FCC channel table"],
                        ["49 MHz field strength", "47 CFR §15.235(a)",   "○ OPEN", "≤10,000 µV/m at 3 m (≈30 µW / −15.2 dBm EIRP-equivalent); firmware PA limit required — see REF-FCC-003"],
                    ]}
                />
            </Card>

            <Card title="Industry Standards Compliance" accent={C.teal}>
                <Table
                    cols={["Standard Body", "Standard / Best Practice", "Status"]}
                    accent={C.teal}
                    rows={[
                        ["AUVSI", "UAS best practices — structural redundancy, failsafe modes, pre-flight checklists", "Design compliant; validate at build"],
                        ["IEEE",  "IEEE 802.3 (Ethernet), ISO 11898 (CAN FD), NIST SP 800-72 (write-blocker)", "All wired bus protocols conformant"],
                        ["ISA",   "ISA-99/IEC 62443 — message authentication, secure boot, isolation barriers", "TPM + HMAC + 5 kV isolation architecture addresses core requirements"],
                        ["IEC",   "IEC 62368-1 / VDE 0884-11 — 5 kV isolation barrier certification", "All isolation barriers on Pilot / XO / Commo certified"],
                        ["FAA",   "AC 107-2 (remote pilot operations), FAA Part 107 waivers if above 400 ft AGL", "Operator responsibility"],
                        ["ICAO",  "Annex 2 — nav light colours/positions; Annex 13 — accident reporting", "Nav light design conformant"],
                    ]}
                />
            </Card>
        </div>
    );
}

/* ── BOM summary tab ───────────────────────────────────────────────────────── */
function TabBOM() {
    const categories = [
        { cat: "Propulsion (EDFs + ESCs)",    items: 4,  mass_g: 510,  cost: 239,  notes: "4× 50mm EDF + 4× 40A ESC + 1× 55mm EDF + 1× 50A ESC (rear pair Phase 11 deferred)" },
        { cat: "Tilt servos + linkage",        items: 2,  mass_g: 130,  cost: 26,   notes: "2× tilt servo + pushrods (rear nozzle servo deleted — canonical nozzle is fixed)" },
        { cat: "Cargo servos",                 items: 2,  mass_g: 18,   cost: 6,    notes: "2× SG90 — door actuator + payload release" },
        { cat: "Gear train (M=1.0)",           items: 8,  mass_g: 62,   cost: 62,   notes: "Sector, pinion ×2, bevel ×2, crown, housing ×2, shafts, bearings" },
        { cat: "Avionics (PB2-I + v2 capes)",  items: 6,  mass_g: 460,  cost: 1348, notes: "8× PB2-I + 4× Pilot + 4× XO + 4× Commo + 4× log μSD" },
        { cat: "PCB fabrication (JLCPCB)",     items: 3,  mass_g: 0,    cost: 680,  notes: "Pilot ×4 + XO ×4 + Commo ×4 (assembled, active)" },
        { cat: "Power (batteries + PDB)",      items: 3,  mass_g: 1540, cost: 120,  notes: "6S 4000 mAh + 6S 2800 mAh + dual BEC PDB" },
        { cat: "Printed parts (filament)",     items: 3,  mass_g: 2000, cost: 106,  notes: "PETG ~1,400 g + CF-PETG ~650 g + TPU ~100 g" },
        { cat: "Structural (CF stock + foam)", items: 5,  mass_g: 980,  cost: 77,   notes: "Keel + spars + ring frames + PU foam + epoxy" },
        { cat: "Wiring + conduit",             items: 4,  mass_g: 165,  cost: 48,   notes: "10/16/28 AWG silicone + PTFE conduit" },
        { cat: "Lighting",                     items: 1,  mass_g: 1,    cost: 1,    notes: "4× WS2812C nav lights (port RED / stbd GREEN); WS2812B nozzle rings removed" },
        { cat: "Cargo hardware",               items: 4,  mass_g: 16,   cost: 13,   notes: "N20 motor + HX711 + DRV8833 + Dyneema + gasket" },
        { cat: "Hardware / fasteners",         items: 10, mass_g: 80,   cost: 80,   notes: "Bearings, pins, inserts, antenna hardware, misc" },
    ];
    const totalCost = categories.reduce((s, c) => s + c.cost, 0);
    const totalMass = categories.reduce((s, c) => s + c.mass_g, 0);

    return (
        <div>
            <Card title="Rev R BOM — Category Summary" accent={C.gold}>
                <table style={{ borderCollapse: "collapse", width: "100%" }}>
                    <TH cols={["Category", "Items", "Mass (g)", "Est. Cost (USD)", "Notes"]} accent={C.gold} />
                    <tbody>
                        {categories.map((c, i) => (
                            <tr key={i} style={{ background: i % 2 ? "rgba(251,191,36,0.03)" : "transparent" }}>
                                <td style={{ padding: "4px 12px 4px 0", fontFamily: M, fontSize: 11.5, color: C.gold }}>{c.cat}</td>
                                <td style={{ padding: "4px 12px 4px 0", fontFamily: M, fontSize: 11.5, color: C.text, textAlign: "right" }}>{c.items}</td>
                                <td style={{ padding: "4px 12px 4px 0", fontFamily: M, fontSize: 11.5, color: C.text, textAlign: "right" }}>{c.mass_g.toLocaleString()}</td>
                                <td style={{ padding: "4px 12px 4px 0", fontFamily: M, fontSize: 11.5, color: C.text, textAlign: "right" }}>${c.cost}</td>
                                <td style={{ padding: "4px 0", fontFamily: M, fontSize: 11, color: C.dimmer }}>{c.notes}</td>
                            </tr>
                        ))}
                        <tr style={{ borderTop: `1px solid ${C.gold}` }}>
                            <td style={{ padding: "5px 12px 5px 0", fontFamily: MB, fontSize: 12, color: C.gold }}>TOTAL</td>
                            <td style={{ padding: "5px 12px 5px 0", fontFamily: MB, fontSize: 12, color: C.gold, textAlign: "right" }}>—</td>
                            <td style={{ padding: "5px 12px 5px 0", fontFamily: MB, fontSize: 12, color: C.gold, textAlign: "right" }}>{totalMass.toLocaleString()}</td>
                            <td style={{ padding: "5px 12px 5px 0", fontFamily: MB, fontSize: 12, color: C.gold, textAlign: "right" }}>~${totalCost.toLocaleString()}</td>
                            <td style={{ padding: "5px 0", fontFamily: M, fontSize: 11, color: C.dimmer }}>Excludes one-time tools; component prices as of 2026</td>
                        </tr>
                    </tbody>
                </table>
            </Card>

            <Card title="Rev R vs Rev Q Cost Delta" accent={C.green}>
                <Table
                    cols={["Item", "Rev Q", "Rev R", "Delta"]}
                    accent={C.green}
                    rows={[
                        ["Pilot ×4 (unchanged from Rev Q)",     "$272", "$272", "$0"],
                        ["XO ×4 (unchanged from Rev Q)",      "$420", "$420", "$0"],
                        ["Commo ×4 (unchanged)",        "$128", "$128", "$0"],
                        ["Flight Engineer PDB (new in Rev R)",           "—",    "~$45", "+$45"],
                        ["Total estimate",                      "~$2,137","~$2,182","~+$45"],
                    ]}
                />
                <div style={{ marginTop: 8, fontFamily: M, fontSize: 11, color: C.dimmer }}>
                    Rev R cost increase is minimal — only the Flight Engineer PDB is new.
                    All avionics cape costs carry forward from Rev Q unchanged. Hover T/W ≈ 1.61 (Phases 5–10) / 1.43 (Phase 11).
                </div>
            </Card>

            <Card title="Full BOM Reference" accent={C.teal}>
                <div style={{ fontFamily: M, fontSize: 12, color: C.text, lineHeight: 1.8 }}>
                    Complete line-item BOM with supplier P/Ns, unit prices, and build notes:
                </div>
                <div style={{ fontFamily: M, fontSize: 12, color: C.dimmer, marginTop: 6, lineHeight: 2 }}>
                    <div><span style={{ color: C.teal }}>docs/bom_revR.json</span> — machine-readable JSON with full part-level detail</div>
                    <div><span style={{ color: C.teal }}>current-specification/bom_revR.csv</span> — spreadsheet-compatible CSV</div>
                    <div><span style={{ color: C.dimmer }}>Historical: docs/bom_revQ.json · current-specification/bom_revQ.csv · bom_revP.json/csv (archives/) · bom_revO · bom_revN … bom_revI</span></div>
                </div>
            </Card>
        </div>
    );
}

/* ── Files tab ─────────────────────────────────────────────────────────────── */
function TabFiles() {
    return (
        <div>
            <Card title="JSX Interactive Specification Artifacts" accent={C.accent}>
                <Table
                    cols={["File", "Description", "Rev"]}
                    rows={[
                        ["serenity-rev-r.jsx",                "This document — complete Rev R specification (comprehensive, not a delta)", "Rev R ← CURRENT"],
                        ["serenity-rev-q.jsx",                "Rev Q — Hardened avionics baseline (EMI-hardened v2 capes at all nodes)", "Rev Q — in current-specification/"],
                        ["serenity-rev-p.jsx",                "Rev P — Cargo bay complete (doors + mounts + Rev S shell)", "Rev P — in archives/"],
                        ["serenity-rev-o.jsx",                "Rev O — CG-pivot nacelle, M=1.0 gear train, S1223 wings", "Rev O — in archives/"],
                        ["serenity-rev-n.jsx through rev-b.jsx","Rev N back to Rev B — archived", "Historical — in archives/"],
                        ["serenity-connectivity-revH.jsx",    "Rev H connectivity / MIL-STD-1553 architecture","Rev H — in archives/"],
                        ["nacelle-nozzle-gear.jsx",           "Nacelle nozzle gear coupling detail","Rev E — in archives/"],
                        ["antenna-layout.jsx",                "Antenna layout specification","Rev B — in archives/"],
                    ]}
                />
            </Card>

            <Card title="Active KiCad PCB Files (Rev R)" accent={C.green}>
                <Table
                    cols={["File", "Board", "Status"]}
                    accent={C.green}
                    rows={[
                        ["Pilot.kicad_pcb / .kicad_sch", "Pilot (55×35mm EMI-hardened FC)", "✓ ACTIVE — primary FC cape at all positions"],
                        ["XO.kicad_pcb / .kicad_sch", "XO (55×35mm EMI-hardened CN)", "✓ ACTIVE — primary CN cape at all positions"],
                        ["XCVR-49MHZ-2.kicad_pcb / .kicad_sch", "Commo (55×35mm EMI-hardened)", "✓ ACTIVE — primary 49 MHz sub-module"],
                        ["FlightEngineer.kicad_pcb / .kicad_sch", "Flight Engineer PDB Rev A", "✓ ACTIVE — Rev R addition; DRC clean; gerbers generated 2026-06-10"],
                        ["CAPE-A-2 / CAPE-B-2", "v2 generic cape designators", "ARCHIVED — avionics/kicad/archive/ (Rev R 2026-06-10; renamed Pilot/XO)"],
                        ["CAPE-A-1 / CAPE-B-1 / XCVR-49MHZ-1", "v1 standard capes", "ARCHIVED — avionics/kicad/archive/ (Rev Q 2026-06-05)"],
                    ]}
                />
            </Card>

            <Card title="Active Gerber Files (Rev R)" accent={C.yellow}>
                <Table
                    cols={["Directory", "Board", "Status"]}
                    accent={C.yellow}
                    rows={[
                        ["avionics/kicad/gerbers/FlightEngineer/", "Flight Engineer PDB",  "✓ GENERATED — DRC clean 2026-06-10; ready for fab review"],
                        ["avionics/kicad/gerbers/Pilot/",   "Pilot",        "○ PENDING — PCB layout and DRC sign-off required before fab submission"],
                        ["avionics/kicad/gerbers/XO/",   "XO",        "○ PENDING — PCB layout and DRC sign-off required before fab submission"],
                        ["avionics/kicad/gerbers/XCVR-49MHZ-2/","Commo","○ PENDING — DRC sign-off required before fab submission"],
                        ["avionics/kicad/archive/",        "Cape-A-1, Cape-B-1, CAPE-A-2, CAPE-B-2, XCVR-49MHZ-1", "ARCHIVED Rev Q/R"],
                    ]}
                />
                <div style={{ marginTop: 8, fontFamily: M, fontSize: 11, color: C.orange }}>
                    ⚠ Pilot, XO, and Commo gerbers still pending PCB layout completion.
                    Flight Engineer gerbers are the only fully generated set at Rev R.
                    Do not submit Pilot/XO/XCVR for fabrication until DRC passes with 0 errors / 0 unconnected.
                </div>
            </Card>

            <Card title="Active DTS Overlays (Rev R)" accent={C.teal}>
                <Table
                    cols={["File", "Cape", "Status"]}
                    accent={C.teal}
                    rows={[
                        ["avionics/firmware/dts/cape-a/k3-am6254-pocketbeagle2-serenity-cape-a2.dts", "Pilot", "✓ ACTIVE"],
                        ["avionics/firmware/dts/cape-b/k3-am6254-pocketbeagle2-serenity-cape-b2.dts", "XO", "✓ ACTIVE"],
                        ["avionics/firmware/dts/cape-a/archive/k3-am6254-pocketbeagle2-serenity-cape-a.dts", "Cape-A-1", "ARCHIVED Rev Q"],
                        ["avionics/firmware/dts/cape-b/archive/k3-am6254-pocketbeagle2-serenity-cape-b.dts", "Cape-B-1", "ARCHIVED Rev Q"],
                    ]}
                />
            </Card>

            <Card title="Canonical Airframe Design Files (Rev R)" accent={C.purple}>
                <Table
                    cols={["File", "Description", "Type"]}
                    accent={C.purple}
                    rows={[
                        ["airframe/blender-scripts/blender_nacelle_revo.py",    "Nacelle stator shell generator — CW/CCW variants", "Canonical (active)"],
                        ["airframe/blender-scripts/blender_shells_v3.py",       "Hull shell generator — 2.5 mm wall", "Canonical (active)"],
                        ["airframe/blender-scripts/blender_nozzle_gen.py",      "Iris nozzle petal generator", "Canonical (active)"],
                        ["airframe/blender-scripts/blender_stator_gen.py",      "Stator vane geometry generator", "Canonical (active)"],
                        ["airframe/openscad/nacelles/nacelle_pod_50mm_tandem.scad","Nacelle pod — 50mm tandem, stator, gear bosses", "Canonical (active)"],
                        ["airframe/openscad/fuselage/head_shell24.scad",      "Cockpit / nose section", "Canonical (active)"],
                        ["airframe/openscad/fuselage/middle_canonical_shell24.scad","Fuselage mid-section, no belly scoop", "Canonical (active)"],
                        ["airframe/archive/blender-scripts/",                   "blender_nacelle_integrated_v1/v2.py, *_2mm.py, *_50mm.py, generate_shells_v2.py, generate_hollow_shells.py", "ARCHIVED Rev Q"],
                        ["airframe/archive/stls/nacelles/",                     "s_nacelle_*_revt.stl, *_50mm_repaired.stl, stator_50mm.stl, sector_gear_22mm_fixed.*", "ARCHIVED Rev Q"],
                        ["airframe/archive/stls/fuselage/",                     "hull_engine_bell.stl, rear_shell24*.stl, middle_shell24*.stl, s_middle_intake_shell24.stl, all *_2mm.* and *_repaired.* variants", "ARCHIVED Rev Q"],
                    ]}
                />
            </Card>

            <Card title="Documentation Files" accent={C.gold}>
                <Table
                    cols={["File", "Description", "Rev / Status"]}
                    accent={C.gold}
                    rows={[
                        ["README.md",                               "Project overview, specs, mission profile, attribution", "Rev R ← CURRENT"],
                        ["CLAUDE.md",                               "Project engineering requirements; hull-frame coordinates; imperial-primary units", "Rev R ← CURRENT"],
                        ["TODO.md",                                 "Full phased WBS", "Rev R ← CURRENT"],
                        ["PROJECT_INDEX.md",                        "Complete file manifest, quick specs", "Rev R ← CURRENT"],
                        ["docs/AVIONICS_PB2_REDESIGN.md",           "8-node PB2-I architecture — Rev R baseline", "Rev R ← CURRENT"],
                        ["docs/REVN_BUILD_GUIDE_24IN.md",           "9-phase 24-inch build guide", "Rev R (carried forward)"],
                        ["docs/bom_revR.json",                      "Rev R BOM — machine-readable, all v2 capes + Flight Engineer PDB", "Rev R ← CURRENT"],
                        ["current-specification/bom_revR.csv",      "Rev R BOM CSV — Flight Engineer PDB added", "Rev R ← CURRENT"],
                        ["docs/bom_revQ.json",                      "Rev Q BOM — historical reference", "Rev Q"],
                        ["current-specification/bom_revQ.csv",      "Rev Q BOM CSV — historical reference", "Rev Q"],
                    ]}
                />
            </Card>
        </div>
    );
}

/* ── Build Status tab ──────────────────────────────────────────────────────── */
function TabBuildStatus() {
    const phases = [
        {
            phase: "Pre-Build: 3D Models", status: "IN PROGRESS",
            color: C.yellow,
            items: [
                ["Rev O nacelle stator shells (blender_nacelle_revo.py)", "○ OPEN — BLOCKS Phase 0"],
                ["aft_edf_plenum.stl (SCAD export)", "○ OPEN — BLOCKS Phase 4"],
                ["neck_intake_frame.stl (SCAD export)", "○ OPEN — BLOCKS Phase 1"],
                ["rear_neck_intake_shell24.stl (SCAD export)", "○ OPEN — BLOCKS Phase 0"],
                ["nacelle_sector_gear.stl + all 4 gear SCADs", "○ OPEN"],
                ["wing_nacelle_pylon_revo.stl + wings_s1223_revo.stl", "○ OPEN"],
                ["middle_canonical_shell24.stl", "○ OPEN"],
                ["head_shell24.stl (Rev S sensor/antenna mounts)", "○ OPEN"],
                ["s_rcrs49_wire_post.stl", "○ OPEN"],
                ["Access panel frames A–F + lids (24\" version)", "○ OPEN"],
                ["cargo_gondola_shell.stl", "○ OPEN — BLOCKS Phase 8"],
                ["Cargo door STLs (port + stbd)", "✓ DONE  PR #22"],
                ["Cargo equipment mount STLs (8 parts)", "✓ DONE  PR #21"],
            ],
        },
        {
            phase: "Pre-Build: PCBs (Rev R — v2 + Flight Engineer PDB)", status: "IN PROGRESS",
            color: C.yellow,
            items: [
                ["Flight Engineer PDB KiCad pro/sch/pcb generated", "✓ DONE  Rev R 2026-06-10"],
                ["Flight Engineer PDB DRC clean (0 shorts)", "✓ DONE  Rev R 2026-06-10"],
                ["Flight Engineer PDB gerbers generated", "✓ DONE  Rev R 2026-06-10"],
                ["Cape-A-2 / Cape-B-2 archived; Pilot/XO naming finalised", "✓ DONE  Rev R 2026-06-10"],
                ["Cape-A-1 / Cape-B-1 / XCVR-49MHZ-1 archived", "✓ DONE  Rev Q 2026-06-05"],
                ["Commo RF trace Z₀ = 52.26 Ω", "✓ DONE  PASS"],
                ["Pilot PCB layout complete (EMI-hardened)", "○ OPEN — BLOCKS Phase 6 fab"],
                ["XO PCB layout complete (EMI-hardened)", "○ OPEN — BLOCKS Phase 6 fab"],
                ["Commo PCB layout complete (EMI-hardened)", "○ OPEN — BLOCKS Phase 6 fab"],
                ["Pilot DRC pass + gerbers generated", "○ OPEN — BLOCKS Phase 6 fab"],
                ["XO DRC pass + gerbers generated", "○ OPEN — BLOCKS Phase 6 fab"],
                ["Commo DRC pass + gerbers generated", "○ OPEN"],
            ],
        },
        {
            phase: "Phase 0 — Print All Parts", status: "NOT STARTED",
            color: C.red,
            items: [
                ["All SCAD → STL exports complete", "○ BLOCKED by Pre-Build"],
                ["All filament ordered + dried (6 h @ 65°C)", "○ OPEN"],
                ["Hardened-steel nozzle installed", "○ OPEN"],
                ["Phase 0 dry-fit checks", "○ OPEN"],
            ],
        },
        {
            phase: "Phase 1 — Hull Structure", status: "NOT STARTED",
            color: C.red,
            items: [
                ["Keel + ring frames + access panel frames", "○ BLOCKED by Phase 0"],
                ["Standoffs, SMA bulkheads, PTFE conduits installed", "○ OPEN"],
                ["EPS void formers (waxed 2×)", "○ OPEN"],
                ["X-30 PU foam pour (3 shots, 24 h cure each)", "○ OPEN"],
            ],
        },
        {
            phase: "Phase 2 — Nacelle Assembly", status: "NOT STARTED",
            color: C.red,
            items: [
                ["EDF bench-test (rotation direction)", "○ BLOCKED by Phase 0"],
                ["EDF1 + EDF2 installation in nacelle bore", "○ OPEN"],
                ["Nozzle assembly (8 conical flaps + 72T unison ring + spiral cam)", "○ OPEN"],
                ["Gear linkage (sector → pinion → bevel → crown)", "○ OPEN"],
                ["Full sweep test: 0°→90°, nozzle open/close verified", "○ OPEN"],
            ],
        },
        {
            phase: "Phases 3–5 — Tilt / Rear EDF / Foam Close", status: "NOT STARTED",
            color: C.red,
            items: [
                ["Nacelle pivot + tilt servos installed", "○ BLOCKED by Phase 2"],
                ["Rear EDF + radial intake + plenum", "○ OPEN"],
                ["Final foam close-up + void former removal", "○ OPEN"],
            ],
        },
        {
            phase: "Phase 6 — Minimum Viable Flyer ★ (Rev Q: all v2 capes)", status: "NOT STARTED",
            color: C.red,
            items: [
                ["CN1+FC1 (Shepherd's room/Bay A) + CN2+FC2 (Inara's shuttle/Bay B) Pilot/XO installed", "○ BLOCKED by Phase 5 + PCB fab"],
                ["Pilot/XO PCBs received from JLCPCB", "○ BLOCKED by DRC + gerber regen"],
                ["Commo sub-modules received", "○ BLOCKED by gerber regen"],
                ["TPM provisioning (all 4 Shepherd's room + Inara's shuttle nodes)", "○ OPEN"],
                ["CPLD write-blocker verification (XO)", "○ OPEN"],
                ["Load k3-am6254-...-cape-a2.dts / cape-b2.dts overlays", "○ OPEN"],
                ["CAN FD heartbeat ring (0x001–0x004)", "○ OPEN"],
                ["serenity-cn Phase 6 + serenity-fc Phase 6 flashed", "✓ FIRMWARE DONE"],
                ["Ground tests (ESC cal, motor spin, CG, GPS lock)", "○ OPEN"],
                ["First tethered hover → first free hover → transition", "○ OPEN"],
                ["FAA registration applied to airframe", "○ OPEN  REQUIRED before free flight"],
            ],
        },
        {
            phase: "Phase 7 — Full 8-Node + OA (Rev Q: River's room/Bay D + Simon's medbay/Bay E use Pilot/XO)", status: "NOT STARTED",
            color: C.red,
            items: [
                ["CN3+FC3 (River's room/Bay D) + CN4+FC4 (Simon's medbay/Bay E) Pilot/XO installed", "○ BLOCKED by Phase 6"],
                ["12× VL53L5CX ToF sensors installed + configured", "○ OPEN"],
                ["Ethernet RSTP ring closed + verified (8 ADIN1300BCPZ nodes)", "○ OPEN"],
                ["3-waypoint autonomous mission", "○ OPEN"],
            ],
        },
        {
            phase: "Phase 8 — Cargo System", status: "PARTIALLY DONE",
            color: C.yellow,
            items: [
                ["Cargo gondola shell bonded into belly", "○ BLOCKED by cargo_gondola_shell.stl"],
                ["Clamshell door hinges + 3 mm CF rod installed", "○ OPEN  STLs done"],
                ["N20 winch + Dyneema + auto-latch cradle", "○ OPEN"],
                ["DRV8833 + SG90 door actuator + SG90 release servo", "○ OPEN"],
                ["CN master cargo state machine firmware", "○ OPEN"],
                ["250 g payload delivery test", "○ OPEN"],
            ],
        },
        {
            phase: "Phase 9 — Finishing / Regulatory", status: "NOT STARTED",
            color: C.red,
            items: [
                ["FAA registration decal (issued number)", "○ OPEN"],
                ["Waterslide decals applied per decal_sheet.svg", "○ OPEN"],
                ["Final airworthiness inspection", "○ OPEN"],
                ["Documentation archive (build log, TPM fingerprints, AUW/CG)", "○ OPEN"],
            ],
        },
        {
            phase: "Firmware Phase 7", status: "IN PROGRESS",
            color: C.yellow,
            items: [
                ["serenity-cn Phase 6 daemon (XCVR KISS + argparse)", "✓ DONE  2026-05-25"],
                ["serenity-fc Phase 6 stub (signal handling)", "✓ DONE  2026-05-25"],
                ["Si5351A I²C driver + AM6254 DTS overlays (cape-a2 / cape-b2)", "✓ DONE  2026-05-25"],
                ["EDF PID governor (FC) — BDSHOT + EHRPWM + CAN FD sync", "○ OPEN"],
                ["IMU / baro / GPS sensor fusion (FC)", "○ OPEN"],
                ["ToF OA array management (FC)", "○ OPEN"],
                ["MIL-STD-1553B RT (FC + CN)", "○ OPEN"],
                ["TPM attestation + boot measurement chain", "○ OPEN"],
                ["Node role election + failover protocol", "○ OPEN"],
                ["Cargo state machine (CN)", "○ OPEN"],
            ],
        },
    ];

    return (
        <div>
            {phases.map((p, pi) => (
                <Card key={pi} title={`${p.phase}`} accent={p.color}>
                    <div style={{ display: "flex", alignItems: "center", marginBottom: 10 }}>
                        <Badge text={p.status} color={p.color} />
                    </div>
                    <table style={{ borderCollapse: "collapse", width: "100%" }}>
                        <tbody>
                            {p.items.map((item, ii) => (
                                <tr key={ii} style={{ background: ii % 2 ? "rgba(255,255,255,0.02)" : "transparent" }}>
                                    <td style={{ padding: "3px 12px 3px 0", fontFamily: M, fontSize: 11.5, color: C.text, width: "70%" }}>{item[0]}</td>
                                    <td style={{ padding: "3px 0", fontFamily: M, fontSize: 11,
                                        color: item[1].startsWith("✓") ? C.green : item[1].includes("BLOCKED") ? C.red : C.dimmer,
                                    }}>{item[1]}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </Card>
            ))}
        </div>
    );
}

/* ── Main component ────────────────────────────────────────────────────────── */
export default function RevRSpec() {
    const [activeTab, setActiveTab] = useState("overview");

    const tabs = [
        { id: "overview",  label: "Overview"      },
        { id: "airframe",  label: "Airframe"       },
        { id: "propulsion",label: "Propulsion"     },
        { id: "avionics",  label: "Avionics"       },
        { id: "comms",     label: "Comms"          },
        { id: "cargo",     label: "Cargo"          },
        { id: "security",  label: "Security"       },
        { id: "regulatory",label: "Regulatory"     },
        { id: "bom",       label: "BOM"            },
        { id: "files",     label: "Files"          },
        { id: "status",    label: "Build Status"   },
    ];

    return (
        <div style={{
            background: C.bg, color: C.text,
            minHeight: "100vh", padding: "24px 20px",
            fontFamily: M,
        }}>
            <_ODFontLoader />

            {/* Header */}
            <div style={{ marginBottom: 24 }}>
                <div style={{
                    fontFamily: MB, fontSize: 22, color: C.accent,
                    letterSpacing: 1, marginBottom: 4,
                }}>
                    SERENITY-CLASS TILTROTOR UAV — REV R
                    <Badge text="NAMING FINALISATION + FLIGHT ENGINEER PDB" color={C.lime} />
                </div>
                <div style={{ color: C.dimmer, fontSize: 12 }}>
                    Pilot / XO Naming Finalised · Flight Engineer PDB DRC-Clean · Hull-Frame Validated · 24-inch Hull · M=1.0 Gear Train
                </div>
                <div style={{ color: C.dimmer, fontSize: 11, marginTop: 4 }}>
                    Author: Steve Griffing PE(CSE) [Control Systems Engineering] CISSP-ISSEP CPP ·
                    CC BY 4.0 · 2026-06-10
                </div>
            </div>

            {/* Tabs */}
            <div style={{ display: "flex", gap: 8, marginBottom: 20, flexWrap: "wrap" }}>
                {tabs.map(t => (
                    <button key={t.id} onClick={() => setActiveTab(t.id)} style={{
                        background: activeTab === t.id ? C.accent : "rgba(0,229,255,0.07)",
                        color:      activeTab === t.id ? C.bg     : C.accent,
                        border:     `1px solid ${C.border}`,
                        borderRadius: 6, padding: "6px 14px", cursor: "pointer",
                        fontFamily: MB, fontSize: 12, letterSpacing: 0.3,
                    }}>{t.label}</button>
                ))}
            </div>

            {/* Tab content */}
            {activeTab === "overview"   && <TabOverview />}
            {activeTab === "airframe"   && <TabAirframe />}
            {activeTab === "propulsion" && <TabPropulsion />}
            {activeTab === "avionics"   && <TabAvionics />}
            {activeTab === "comms"      && <TabComms />}
            {activeTab === "cargo"      && <TabCargo />}
            {activeTab === "security"   && <TabSecurity />}
            {activeTab === "regulatory" && <TabRegulatory />}
            {activeTab === "bom"        && <TabBOM />}
            {activeTab === "files"      && <TabFiles />}
            {activeTab === "status"     && <TabBuildStatus />}

            {/* Footer */}
            <div style={{
                marginTop: 32, borderTop: `1px solid ${C.border}`,
                paddingTop: 12, color: C.dimmer, fontSize: 10.5, fontFamily: M,
            }}>
                Serenity-Class Tiltrotor UAV Rev R · Steve Griffing PE(CSE) CISSP-ISSEP CPP ·
                CC BY 4.0 creativecommons.org/licenses/by/4.0 · 2026-06-10 ·
                Hull geometry CC BY 4.0 misubisu (thingiverse.com/thing:7330462) ·
                Iris nozzle concept (nacelle) CC BY 4.0 BamJr (thingiverse.com/thing:2991269) ·
                Visual inspiration Joss Whedon / Mutant Enemy / Universal © all rights reserved
            </div>
        </div>
    );
}
