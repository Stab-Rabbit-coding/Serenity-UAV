/**
 * serenity-rev-p.jsx — Serenity-Class Tiltrotor UAV Rev P Specification
 *
 * Revision P: Cargo Bay Complete — Documentation Baseline
 *
 * Key changes from Rev O:
 *   1. Cargo clamshell door STLs complete: cargo_door_port.stl + cargo_door_stbd.stl
 *      CF-PETG, 8-barrel piano hinge, 3 mm CF rod, 3.15 mm bore. (2026-06-01, PR #22)
 *   2. Cargo equipment mounts: 8 STLs via generate_cargo_mounts.py. (2026-05-30, PR #21)
 *      cargo_winch_motor_mount, cargo_winch_spool, cargo_door_servo_bracket,
 *      cargo_release_servo_bracket, cargo_drv8833_tray, cargo_cradle_autolatch,
 *      cargo_gps_retention_ring, cargo_fpv_bezel
 *   3. s_cargo_sect_shell24.scad Rev S: belly opening 100×9×165 mm,
 *      2× hinge-pin blocks (3.3 mm bore + M3 grub-screw tap),
 *      2× SG90 servo pads (4× M2.5 pilots each),
 *      4× latch-catch lips at Z=42/122 mm per X frame edge. (2026-06-01)
 *   4. XCVR-49MHZ-1 RF trace impedance verification: Z₀ = 52.26 Ω — PASS (2026-05-30)
 *   5. TODO.md expanded into full phased Work Breakdown Structure
 *   6. Documentation scrub: stale files archived, all docs updated to Rev P baseline
 *
 * This is a COMPLETE design specification — not a delta from Rev O.
 * Every subsystem is documented in full for standalone reference.
 *
 * Attribution:
 *   Hull geometry: Peter Farell (printables.com/model/548545) — CC BY 4.0
 *   Iris nozzle concept: BamJr (thingiverse.com/thing:2991269) — CC BY 4.0
 *   Visual inspiration: Firefly / Serenity © Joss Whedon / Mutant Enemy / Universal
 *     (Fan engineering work — not an officially licensed product)
 *
 * Author:  Steve Griffing, PE(CSE) [Control Systems Engineering], CISSP-ISSEP, CPP
 * License: CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/
 * Date:    2026-06-01
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

function TD({ row, colors }) {
    return (
        <tr>
            {row.map((cell, j) => (
                <td key={j} style={{
                    padding: "4px 12px 4px 0", fontFamily: M, fontSize: 11.5,
                    color: (colors && colors[j]) ? colors[j] : (j === 0 ? C.dim : C.text),
                }}>{cell}</td>
            ))}
        </tr>
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
            <Card title="Rev P — What's New" accent={C.green}>
                <Table
                    cols={["Subsystem", "Change", "Status", "PR / Date"]}
                    accent={C.green}
                    rows={[
                        ["Cargo / Structure", "s_cargo_sect_shell24.scad Rev S — belly opening 100×9×165 mm, hinge-pin blocks, SG90 servo pads, latch-catch lips", "✓ DONE", "2026-06-01"],
                        ["Cargo / STLs", "cargo_door_port.stl + cargo_door_stbd.stl — CF-PETG clamshell doors, 8-barrel piano hinge, 3 mm CF rod, 3.15 mm bore", "✓ DONE", "PR #22  2026-06-01"],
                        ["Cargo / STLs", "8 equipment mount STLs — winch motor mount, spool, door servo bracket, release bracket, DRV8833 tray, cradle, GPS ring, FPV bezel", "✓ DONE", "PR #21  2026-05-30"],
                        ["PCB / RF", "XCVR-49MHZ-1 RF trace: Z₀ = 52.26 Ω — W=2.75 mm, H=1.6 mm, εr=4.5, T=35 µm — PASS [45–55 Ω]", "✓ DONE", "2026-05-30"],
                        ["Docs", "TODO.md expanded to full phased WBS with dependency chains and phase pass criteria", "✓ DONE", "2026-05-30"],
                        ["Docs", "Documentation scrub — README, PROJECT_INDEX, BUILD_GUIDE updated; stale files archived", "✓ DONE", "2026-06-01"],
                    ]}
                />
            </Card>

            <Card title="Quick Specs — Rev P Baseline" accent={C.accent}>
                <Table
                    cols={["Parameter", "Value", "Notes"]}
                    rows={[
                        ["Hull length",         "609.6 mm (24.00 in)",      "Serenity-class, Peter Farell geometry × 2.9294"],
                        ["Beam (nacelle tips)", "~486 mm",                  "Tip-to-tip across tilt axis"],
                        ["Height (landed)",     "182 mm",                   "To top of dorsal hull"],
                        ["Hull material",       "PETG shell + PU foam + CF skeleton", "2.5 mm skin, 2 lb/ft³ closed-cell foam fill"],
                        ["Propulsion",         "2× (2× 50 mm EDF @ 6S) nacelles + 1× 120 mm EDF @ 6S fuselage", "Counter-rotating nacelle pairs"],
                        ["Nacelle tilt",       "0° (cruise) → 90° (hover) → 120° (backing)", "Hard stops −5° / 140°"],
                        ["Nozzle actuation",   "Passive gear train per nacelle; SG90 for rear nozzle", "M=1.0 sector → pinion → bevel → crown → iris ring"],
                        ["Total hover thrust",  "~5,322 g",                 "1,822 g nacelles + 3,500 g rear EDF"],
                        ["AUW (6S 4000 mAh)",  "~3,550 g",                 "Estimated; T/W ≈ 1.50"],
                        ["Avionics",           "8× PocketBeagle 2 Industrial (AM6254)", "4× FC (Cape-A) + 4× CN (Cape-B)"],
                        ["Data buses",         "Ethernet RSTP · CAN FD · RS-485 · MIL-STD-1553B", "All 4 on every node"],
                        ["Radio links",        "SiK 915 MHz + LoRa 915 MHz + WiFi + RCRS 49 MHz", "All 4 on every CN node"],
                        ["Security",           "SLB9670 TPM 2.0 on all 8 nodes + ATF16V8BQL CPLD write-blocker", "Message signing + forensic log"],
                        ["Cargo bay",          "101.6 × 76.2 × 76.2 mm",  "Clamshell doors + N20 winch + auto-latch cradle"],
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
                        ["P", "2026-06",  "Cargo bay complete (doors + mounts + Rev S shell) — this revision"],
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
                        ["A (nose)",      "Bay A", "~0–91 mm",   "Screw/bayonet", "CN1 + FC1 PCBs, GPS coax, SiK/LoRa radios"],
                        ["B (fwd dorsal)","Bay B", "~91–165 mm", "Screw/bayonet", "CN2 + FC2 PCBs, GPS coax"],
                        ["C (wing root)", "Bay C", "~165–251 mm","Hinge+latch",   "ESC pairs, servo leads, wing spar access"],
                        ["D (aft dorsal)","Bay D", "~251–320 mm","Screw/bayonet", "CN3 + FC3 PCBs"],
                        ["E (aft svc)",   "Bay E", "~320–388 mm","Screw/bayonet", "CN4 + FC4 PCBs"],
                        ["F (engine bell)","Bay F","~388–600 mm","Magnet+snap",   "120 mm EDF, 80A ESC, plenum, rear nozzle servo"],
                    ]}
                />
                <div style={{ marginTop: 8, fontFamily: M, fontSize: 11, color: C.dimmer }}>
                    Panel lids: PETG 0.20 mm / 100% infill. Frame bonding: 5-min epoxy, 30 min cure.
                    Gasket: 3M 4016 closed-cell foam tape on frame lip. All lids flush ±0.2 mm when installed.
                </div>
            </Card>

            <Card title="Print Schedule Summary" accent={C.yellow}>
                <Table
                    cols={["STL", "Material", "Layer / Infill", "Qty", "Est. Mass"]}
                    accent={C.yellow}
                    rows={[
                        ["s_head_shell24.stl",                "PETG",    "0.20 mm / 8% gyroid",    "1",  "95 g"],
                        ["s_middle_canonical_shell24.stl",    "PETG",    "0.20 mm / 8% gyroid",    "1",  "135 g"],
                        ["s_cargo_sect_shell24.stl (Rev S)",  "PETG",    "0.20 mm / 8% gyroid",    "1",  "185 g"],
                        ["s_rear_neck_intake_shell24.stl",    "PETG",    "0.20 mm / 8% gyroid",    "1",  "225 g"],
                        ["s_legs_scaled24.stl",               "CF-PETG", "0.15 mm / 30%",          "1",  "60 g"],
                        ["s_feet_x_4_scaled24.stl",           "TPU 95A", "0.25 mm / 40%",          "1",  "80 g"],
                        ["s_neck_intake_frame.stl",           "CF-PETG", "0.15 mm / 40% / 4 walls","1",  "85 g"],
                        ["s_aft_edf_plenum.stl",              "PETG",    "0.20 mm / 20% gyroid",   "1",  "75 g"],
                        ["Access panel frames A–F + lids",    "PETG",    "0.20 mm / 100%",         "1 set","~90 g"],
                        ["s_eng_left_stator_shell24_revo.stl","CF-PETG", "0.15 mm / 25% / 4 walls","1",  "132 g"],
                        ["s_eng_right_stator_shell24_revo.stl","CF-PETG","0.15 mm / 25% / 4 walls","1",  "132 g"],
                        ["s_wing_nacelle_pylon_port/stbd.stl","CF-PETG", "0.15 mm / 40% / 4 walls","2",  "52 g ea"],
                        ["s_wings_s1223_revo.stl (port+stbd)","CF-PETG", "0.15 mm / 40% / 4 walls","2",  "118 g ea"],
                        ["nacelle_nozzle_petal.stl",          "PETG",    "0.20 mm / 20% gyroid",   "16", "2 g ea"],
                        ["nacelle_nozzle_ring.stl",           "CF-PETG", "0.15 mm / 40%",          "2",  "18 g ea"],
                        ["rear_nozzle_petal.stl",             "PETG",    "0.20 mm / 20% gyroid",   "8",  "4 g ea"],
                        ["rear_nozzle_frame.stl",             "CF-PETG", "0.15 mm / 30%",          "1",  "55 g"],
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
                        ["Thrust per EDF",      "~460 g",          "Budget 6S 50 mm tier"],
                        ["Thrust per nacelle",  "~911 g",          "Two EDFs in tandem"],
                        ["Total nacelle thrust","~1,822 g",        "Both nacelles combined"],
                    ]}
                />
            </Card>

            <Card title="Rear EDF — 120 mm" accent={C.red}>
                <Table
                    cols={["Parameter", "Value", "Notes"]}
                    accent={C.red}
                    rows={[
                        ["EDF size",     "120 mm",         "Single unit, engine bell"],
                        ["Voltage",      "6S",             ""],
                        ["Thrust",       "~3,500 g",       "Exhaust straight aft"],
                        ["Location",     "Station ~430 mm from nose", "Inside engine bell, Panel F"],
                        ["Intake",       "4 radial scoops at station ~310 mm", "s_neck_intake_frame + s_aft_edf_plenum"],
                        ["Fan annular area", "~10,683 mm²","120 mm bore"],
                        ["Scoop capture area","~15,600 mm²","Ratio 1.46× — exceeds 1.3× duct-match minimum"],
                        ["ESC",          "80A 6S BLHeli32","110A burst; mounted in Panel F bay"],
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
                        ["Servo torque", "~12% lower demand vs. Rev N", "Benefit of CG-pivot; only aero + inertia moments remain"],
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
                    Internal hard stop limits ring to 70.7° max, protecting against over-drive above 90°.
                </div>
            </Card>

            <Card title="Thrust & Weight Budget" accent={C.green}>
                <Table
                    cols={["Item", "Value", "Notes"]}
                    accent={C.green}
                    rows={[
                        ["Nacelle thrust",   "~1,822 g", "2× (2× 50 mm EDF) = 4 EDFs × ~460 g ea (approx)"],
                        ["Rear EDF thrust",  "~3,500 g", "120 mm 6S"],
                        ["Total thrust",     "~5,322 g", ""],
                        ["Hull prints + foam","~1,150 g","All shell sections + access panels + foam"],
                        ["Nacelle assemblies","~440 g",  "2× nacelle shells + EDFs + ESCs + gear + nozzle"],
                        ["Avionics",         "~420 g",   "8× PB2-I + 4× Cape-A + 4× Cape-B + RCRS-49×4 + GPS×4 + radios"],
                        ["Servos + linkage", "~160 g",   "2× tilt servo + 1× rear nozzle servo + pushrods"],
                        ["Power (6S 4000mAh)","~750 g",  "Primary flight battery"],
                        ["Misc hardware",    "~230 g",   "CF stock, fasteners, wiring, ESCs, bearings"],
                        ["AUW (estimated)",  "~3,550 g", "All of the above; T/W ≈ 1.50"],
                        ["T/W at AUW",       "~1.50",    "5,322 ÷ 3,550 = 1.499"],
                        ["Max payload at T/W=1.0","~1,772 g","Hover capability margin"],
                    ]}
                />
            </Card>
        </div>
    );
}

/* ── Avionics tab ──────────────────────────────────────────────────────────── */
function TabAvionics() {
    return (
        <div>
            <Card title="8-Node Cooperative Architecture" accent={C.accent}>
                <div style={{ fontFamily: M, fontSize: 12, color: C.text, marginBottom: 12, lineHeight: 1.8 }}>
                    Eight PocketBeagle 2 Industrial (AM6254) boards, split into two groups of four.
                    All nodes run the same base Linux image (from 64 GB eMMC — no OS microSD required).
                    Real-time tasks use the AM6254 PRU-ICSS cores. Role assignment is dynamic:
                    CAN FD heartbeat priority arbitration at boot elects FC master and CN master independently.
                    Any node can fail over for any role.
                </div>
                <Table
                    cols={["Group", "Count", "Cape", "Primary Responsibility"]}
                    rows={[
                        ["FC1–FC4", "4", "Cape-A (Sensor/Flight)", "Flight control, IMU/GPS/baro fusion, ESC PID governor, ToF OA, actuator PWM"],
                        ["CN1–CN4", "4", "Cape-B (Comms/Payload)", "Radio links (all 4), system logging, cargo/payload control, MAVLink routing"],
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

            <Card title="Cape-A — FC Node (Flight Control / Sensor)" accent={C.green}>
                <Table
                    cols={["Feature", "Detail"]}
                    accent={C.green}
                    rows={[
                        ["Size",          "85×55 mm, 4-layer KiCad (Cape-A-1 gerbers)"],
                        ["IMU",           "ICM-42688-P (SPI) — 6-DOF; 32 kHz ODR"],
                        ["Barometer",     "BMP388 / BMP390 (SPI) — altitude hold PID"],
                        ["GPS",           "u-blox M10Q via UART — NMEA/UBX; HDOP gating ≤1.5"],
                        ["ESC PWM",       "EHRPWM / PRU-ICSS — BDSHOT600; 5 outputs (4× nacelle + 1× rear)"],
                        ["Servo PWM",     "3 channels — 2× nacelle tilt + 1× rear nozzle"],
                        ["ToF array",     "TCA9548A 8-ch I²C mux + MCP23008 XSHUT expander → 6× VL53L5CX per node"],
                        ["TPM",           "SLB9670 TPM 2.0 (SPI) — attestation + HMAC signing"],
                        ["Tamper mesh",   "F.Cu / B.Cu TMESH_P/N nets routed to TPM GPIO — physical intrusion detect"],
                        ["MIL-STD-1553", "PRU Manchester II encoder/decoder; FC1=BC, FC2=standby BC"],
                        ["CAN FD",        "Via AM6254 MCAN — daisy-chain bus topology"],
                        ["RS-485",        "Half-duplex, 1 Mbps, multi-drop"],
                        ["Ethernet",      "DP83825I 100BASE-TX phy → RSTP ring"],
                        ["ADC (ESC telem)","74HC4051 8:1 mux — BDSHOT telemetry demux for 4 ESCs"],
                    ]}
                />
            </Card>

            <Card title="Cape-B — CN Node (Comms / Logging / Payload)" accent={C.pink}>
                <Table
                    cols={["Feature", "Detail"]}
                    accent={C.pink}
                    rows={[
                        ["Size",           "90×60 mm, 4-layer KiCad (Cape-B-1 gerbers)"],
                        ["SiK radio",      "SiK 915 MHz MAVLink — belly port SMA bulkhead"],
                        ["LoRa radio",     "RFM95W 915 MHz backup — belly stbd SMA bulkhead"],
                        ["WiFi/BT",        "TI WL1837MOD 2.4/5 GHz — dorsal fwd SMA bulkhead"],
                        ["RCRS-49",        "XCVR-49MHZ-1 sub-module — 49 MHz AX.25 RC"],
                        ["Log μSD",        "Cape-B microSD slot — hardware write-blocked via CPLD"],
                        ["CPLD",           "ATF16V8BQL — hardware-enforced non-executable log storage; write-blocker"],
                        ["NOR flash",      "W25Q128JV 128 Mb — circular log overflow buffer"],
                        ["TPM",            "SLB9670 TPM 2.0 — key material for log signing + HMAC on AX.25 payloads"],
                        ["Tamper mesh",    "Same as Cape-A"],
                        ["Cargo GPIO",     "DRV8833 winch H-bridge + HX711 load cell ADC via Cape-B GPIO"],
                        ["MIL-STD-1553",  "PRU Manchester II; CN1=RT 0x01, CN2–CN4 RT addresses"],
                        ["CAN FD",         "Via AM6254 MCAN — same daisy-chain as Cape-A nodes"],
                    ]}
                />
            </Card>

            <Card title="Bay Assignments" accent={C.yellow}>
                <Table
                    cols={["Bay", "Station", "Lower (Cape-B CN)", "Upper (Cape-A FC)", "Notes"]}
                    accent={C.yellow}
                    rows={[
                        ["A (nose)",    "0–91 mm",   "CN1", "FC1", "SiK + LoRa + WiFi + RCRS-49 on CN1; GPS1 on FC1; CAN FD bus start (120Ω)"],
                        ["B (fwd)",     "91–165 mm", "CN2", "FC2", "GPS2 on FC2; RCRS-49 on CN2"],
                        ["D (aft)",     "251–320 mm","CN3", "FC3", "GPS3 on FC3; RCRS-49 on CN3"],
                        ["E (svc)",     "320–388 mm","CN4", "FC4", "GPS4 on FC4; CAN FD bus end (120Ω permanent)"],
                    ]}
                />
                <div style={{ marginTop: 8, fontFamily: M, fontSize: 11, color: C.dimmer }}>
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
                        ["Ethernet", "IEEE 802.3u 100BASE-TX · CPSW3G + DP83825I", "100 Mbps", "RSTP ring (8 nodes, self-healing)", "Ring closes at FC4→CN1 ETH-EA link; single-link failure heals in <1 s"],
                        ["CAN FD",   "ISO 11898-1:2015 (CAN FD)", "1 Mbps arb / 8 Mbps data", "Linear daisy-chain; 120Ω at CN1 + FC4", "Heartbeat 0x001–0x008; cross-node RPM sync + OA halt broadcast"],
                        ["RS-485",   "EIA-485 half-duplex", "1 Mbps", "Multi-drop; 120Ω at CN1 + FC4", "Structured frame: header/payload/CRC; command + status relay"],
                        ["MIL-STD-1553B","PRU Manchester II encoder/decoder", "1 Mbps", "BC/RT: FC1=BC, FC2=standby BC; all others RT", "All 8 RT addresses respond within 9 µs; added Rev H"],
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
                        ["RCRS 49 MHz",  "XCVR-49MHZ-1 AX.25 AFSK",  "49.830–49.890 MHz RCRS", "RC command link (backup)", "FCC Part 95 (RCRS); FCC equipment authorization required before airborne TX"],
                    ]}
                />
            </Card>

            <Card title="RCRS-49 Antenna System" accent={C.purple}>
                <Table
                    cols={["Element", "Spec", "Notes"]}
                    accent={C.purple}
                    rows={[
                        ["Top wire",       "0.3 mm SS wire, ~470 mm dorsal spine", "Forward post ~120 mm → aft post ~600 mm from nose"],
                        ["Forward post",   "PETG mast, base-loading coil 38 µH + LC pi-net", "Bonded at dorsal ~120 mm; 3 mm clearance from GPS patch"],
                        ["Aft post",       "PETG mast, ceramic bead insulator", "Top of rear nozzle cone; insulated (open-circuit) end"],
                        ["Counterpoise",   "CF keel bar 6×3 mm, 620 mm", "Connected to RCRS-49 GND on Cape-B"],
                        ["Antenna type",   "End-fed shortened wire, horizontal polarisation", "~6–12 dB cross-pol loss at ≤300 m range — acceptable"],
                        ["GPS clearance",  "≥3 mm from forward post to GPS patch face", "Bench-verify HDOP ≤1.5 with RCRS-49 TX active before flight"],
                        ["XCVR Z₀",        "52.26 Ω for W=2.75 mm, H=1.6 mm, εr=4.5, T=35 µm", "PASS [45–55 Ω] — verified by check_impedance.py 2026-05-30"],
                    ]}
                />
            </Card>
        </div>
    );
}

/* ── Cargo tab (Rev P) ─────────────────────────────────────────────────────── */
function TabCargo() {
    return (
        <div>
            <Card title="Rev P — Cargo System Status" accent={C.green}>
                <Table
                    cols={["Item", "Status", "Date / PR", "Notes"]}
                    accent={C.green}
                    rows={[
                        ["s_cargo_sect_shell24.scad Rev S", "✓ DONE", "2026-06-01", "Belly opening 100×9×165 mm; 2× hinge-pin blocks (3.3 mm bore + M3 grub tap); 2× SG90 servo pads; 4× latch-catch lips"],
                        ["cargo_door_port.stl", "✓ DONE", "PR #22  2026-06-01", "CF-PETG; bilinear interpolation from Rev-O belly faces; 8-barrel piano hinge, 3 mm CF rod"],
                        ["cargo_door_stbd.stl", "✓ DONE", "PR #22  2026-06-01", "Mirror of port door; same hinge geometry; both watertight"],
                        ["cargo_winch_motor_mount.stl", "✓ DONE", "PR #21  2026-05-30", "CF-PETG; N20 motor press-fit; 4× M2.5 boss pattern"],
                        ["cargo_winch_spool.stl", "✓ DONE", "PR #21  2026-05-30", "PETG; Dyneema SK75 0.5 mm winding groove; press-fit to N20 shaft"],
                        ["cargo_door_servo_bracket.stl", "✓ DONE", "PR #21  2026-05-30", "CF-PETG; SG90 4× M2.5 pilot holes; bell-crank pivot boss"],
                        ["cargo_release_servo_bracket.stl", "✓ DONE", "PR #21  2026-05-30", "CF-PETG; SG90 4× M2.5 pilot holes; payload release arm socket"],
                        ["cargo_drv8833_tray.stl", "✓ DONE", "PR #21  2026-05-30", "PETG; DRV8833 breakout snap-fit tray; cable routing slot"],
                        ["cargo_cradle_autolatch.stl", "✓ DONE", "PR #21  2026-05-30", "PETG; spring-latch auto-lock on winch retract; HX711 load-cell pocket"],
                        ["cargo_gps_retention_ring.stl", "✓ DONE", "PR #21  2026-05-30", "PETG; retains cargo-nadir GPS module in bay floor"],
                        ["cargo_fpv_bezel.stl", "✓ DONE", "PR #21  2026-05-30", "PETG; cargo nadir FPV camera bezel; M2.5 mount"],
                        ["cargo_gondola_shell.stl", "○ OPEN", "—", "s_cargo_gondola_shell.scad not yet created; 112×85×22 mm belly pod; BLOCKS Phase 8"],
                        ["SG90 bell-crank boss on door panels", "○ OPEN", "—", "Add to inner face of each door panel for pushrod attachment"],
                        ["DRV8833-tray boss in cargo sect interior", "○ OPEN", "—", "Drawing note addition to s_cargo_sect_shell24.scad"],
                    ]}
                />
            </Card>

            <Card title="Cargo Bay Geometry" accent={C.teal}>
                <Table
                    cols={["Parameter", "Value", "Notes"]}
                    accent={C.teal}
                    rows={[
                        ["Bay internal dims",   "101.6 × 76.2 × 76.2 mm (4 × 3 × 3 in)", "Fits up to 250 g delivery package"],
                        ["Door opening (Rev S)","100 × 165 mm belly opening", "Cut into cargo sect shell; 9 mm wall clearance"],
                        ["Door hinge pin",      "3 mm CF rod",               "8-barrel piano hinge; 3.15 mm bore (clearance)"],
                        ["Door servo pads",     "2× SG90 pads, 4× M2.5 pilots each", "At X-frame edges on Rev S shell interior"],
                        ["Latch-catch lips",    "4× lips at Z=42/122 mm per X frame edge", "Engage cargo_cradle_autolatch spring tabs"],
                        ["Cargo hard points",   "4× M3 heat-set inserts, belly",  "For gondola shell bonding (Phase 1)"],
                        ["Gondola shell",       "112×85×22 mm, 18 mm protrusion below hull line", "s_cargo_gondola_shell.scad — not yet done"],
                        ["Max payload",         "~400 g nominal / ~250 g Phase 8 target","At T/W ≈ 1.50"],
                    ]}
                />
            </Card>

            <Card title="Cargo Winch System" accent={C.yellow}>
                <Table
                    cols={["Component", "Spec", "Notes"]}
                    accent={C.yellow}
                    rows={[
                        ["Winch motor",      "N20 300RPM 6V gear motor",          "Low-speed/high-torque; controlled via DRV8833 H-bridge"],
                        ["H-bridge driver",  "DRV8833 dual H-bridge",             "Cape-B GPIO IN1/IN2; PWM→resistor divider speed control"],
                        ["Load cell",        "HX711 24-bit ADC + load cell",      "Payload weight sensing; interfaces to Cape-B SPI/GPIO"],
                        ["Winch line",       "Dyneema SK75 0.5 mm, 1.5 m",       "500+ kg rated; ~3 g total"],
                        ["Auto-latch cradle","cargo_cradle_autolatch.stl",        "Spring-latch clicks on winch retract; HX711 pocket integral"],
                        ["Payload release",  "SG90 servo in cargo_release_servo_bracket.stl", "CN master GPIO via Cape-B; release arm pivots to drop payload"],
                        ["Door actuator",    "SG90 servo in cargo_door_servo_bracket.stl",    "Spring-assist open; servo pull-close via bell-crank"],
                        ["State machine",    "IDLE → DEPLOY → DELIVERED → RETRACT → LATCHED", "CN master firmware (Phase 8 item)"],
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
                </div>
                <Table
                    cols={["Layer", "Implementation", "Coverage"]}
                    accent={C.red}
                    rows={[
                        ["TPM 2.0",              "SLB9670 on every Cape-A and Cape-B (8 chips total)", "Unique key material per node; HMAC-SHA256 on all flight-critical CAN FD messages; PCR extend on each boot"],
                        ["CPLD write-blocker",   "ATF16V8BQL on every Cape-B (4 chips total)", "Hardware-enforced read-only append to log μSD; NX enforcement; cannot be bypassed in firmware"],
                        ["Message signing",      "TPM-bound HMAC on all outbound inter-node CAN FD frames", "Unauthenticated messages discarded by all nodes"],
                        ["AX.25 HMAC",           "TPM-bound HMAC-SHA256 on every RCRS-49 AX.25 packet", "Receiver nodes verify before acting on RC commands"],
                        ["NOR flash log",        "W25Q128JV 128 Mb circular log on Cape-B", "Overflow buffer for log μSD; also write-blocked; NX enforced"],
                        ["Tamper mesh",          "F.Cu/B.Cu TMESH_P/N copper nets on Cape-A + Cape-B", "Physical intrusion detection routed to SLB9670 TPM GPIO"],
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
                        ["CN1", "A", "Cape-B", "TPM clear → generate endorsement key → extend PCR0 on first boot"],
                        ["FC1", "A", "Cape-A", "Same; also bind HMAC signing key to FC1 endorsement key"],
                        ["CN2", "B", "Cape-B", "Same as CN1"],
                        ["FC2", "B", "Cape-A", "Same as FC1"],
                        ["CN3", "D", "Cape-B", "Phase 7 — provision after board installation"],
                        ["FC3", "D", "Cape-A", "Phase 7"],
                        ["CN4", "E", "Cape-B", "Phase 7"],
                        ["FC4", "E", "Cape-A", "Phase 7"],
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
                        ["AUW limit",          "14 CFR Part 48 — < 55 lbs", "✓ PASS", "AUW ~3,550 g = ~7.8 lbs — well within limit"],
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
                        ["XCVR-49MHZ-1",         "FCC Part 95 (RCRS)", "○ OPEN", "Equipment authorization (FCC ID grant) required before airborne TX; pre-compliance checklist items in WBS §1.3 Phase 4"],
                        ["49 MHz channels",      "47 CFR 95.623",       "○ OPEN", "Channel selection (49.830–49.890 MHz) set in CN firmware; verify FCC channel table"],
                        ["49 MHz ERP",           "47 CFR 95.655",       "○ OPEN", "≤100 mW ERP; harmonic suppression ≥40 dBc at 98 MHz; verify with QUCS-S simulation"],
                        ["49 MHz freq stability", "47 CFR 95.655",      "○ OPEN", "±0.005% max; Si5351A DDS + TCXO reference provides this"],
                    ]}
                />
            </Card>

            <Card title="Industry Standards Compliance" accent={C.teal}>
                <Table
                    cols={["Standard Body", "Standard / Best Practice", "Status"]}
                    accent={C.teal}
                    rows={[
                        ["AUVSI", "UAS best practices — structural redundancy, failsafe modes, pre-flight checklists", "Design compliant; validate at build"],
                        ["IEEE",  "IEEE 802.3u (Ethernet), ISO 11898 (CAN FD), NIST SP 800-72 (write-blocker)", "All wired bus protocols conformant"],
                        ["ISA",   "ISA-99/IEC 62443 (industrial cybersecurity) — message authentication, secure boot", "TPM + HMAC architecture addresses core requirements"],
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
        { cat: "Propulsion (EDFs + ESCs)",    items: 5,  mass_g: 865,  cost: 287,  notes: "4× 50mm EDF + 4× 40A ESC + 1× 120mm EDF + 1× 80A ESC" },
        { cat: "Tilt servos + linkage",        items: 3,  mass_g: 139,  cost: 32,   notes: "2× tilt servo + 1× rear nozzle SG90" },
        { cat: "Cargo servos",                 items: 2,  mass_g: 18,   cost: 6,    notes: "2× SG90 — door actuator + payload release" },
        { cat: "Gear train (M=1.0)",           items: 8,  mass_g: 62,   cost: 62,   notes: "Sector, pinion ×2, bevel ×2, crown, housing ×2, shafts, bearings" },
        { cat: "Avionics (PB2-I + capes)",     items: 6,  mass_g: 420,  cost: 896,  notes: "8× PB2-I + 4× Cape-A + 4× Cape-B + 4× RCRS-49 + 4× log μSD" },
        { cat: "PCB fabrication (JLCPCB)",     items: 3,  mass_g: 0,    cost: 490,  notes: "Cape-A ×4 + Cape-B ×4 + XCVR-49MHZ-1 ×4 (assembled)" },
        { cat: "Power (batteries + PDB)",      items: 3,  mass_g: 1540, cost: 120,  notes: "6S 4000 mAh + 6S 2800 mAh + dual BEC PDB" },
        { cat: "Printed parts (filament)",     items: 3,  mass_g: 2000, cost: 106,  notes: "PETG ~1,400 g + CF-PETG ~650 g + TPU ~100 g" },
        { cat: "Structural (CF stock + foam)", items: 5,  mass_g: 980,  cost: 77,   notes: "Keel + spars + ring frames + PU foam + epoxy" },
        { cat: "Wiring + conduit",             items: 4,  mass_g: 165,  cost: 48,   notes: "10/16/28 AWG silicone + PTFE conduit" },
        { cat: "Lighting",                     items: 2,  mass_g: 25,   cost: 30,   notes: "3× WS2812B nozzle rings + 4× WS2812C nav lights" },
        { cat: "Cargo hardware",               items: 4,  mass_g: 16,   cost: 13,   notes: "N20 motor + HX711 + DRV8833 + Dyneema + gasket" },
        { cat: "Hardware / fasteners",         items: 10, mass_g: 80,   cost: 80,   notes: "Bearings, pins, inserts, antenna hardware, misc" },
    ];
    const totalCost = categories.reduce((s, c) => s + c.cost, 0);
    const totalMass = categories.reduce((s, c) => s + c.mass_g, 0);

    return (
        <div>
            <Card title="Rev P BOM — Category Summary" accent={C.gold}>
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

            <Card title="Rev P vs Rev O Cost Delta" accent={C.green}>
                <Table
                    cols={["Item", "Rev O", "Rev P", "Delta"]}
                    accent={C.green}
                    rows={[
                        ["Cargo servos (2× SG90)",          "—",     "$6",    "+$6"],
                        ["DRV8833 H-bridge cargo",           "—",     "$2",    "+$2"],
                        ["Dyneema SK75 winch line",          "—",     "$4",    "+$4"],
                        ["Cargo foam gasket tape",           "—",     "$3",    "+$3"],
                        ["CF-PETG filament (+90 g for doors/mounts)","~$48","~$54","+$6"],
                        ["PETG filament (+50 g for cargo parts)","~$56","~$58", "+$2"],
                        ["Total estimate",                  "~$1,882","~$1,905","~+$23"],
                    ]}
                />
            </Card>

            <Card title="Full BOM Reference" accent={C.teal}>
                <div style={{ fontFamily: M, fontSize: 12, color: C.text, lineHeight: 1.8 }}>
                    Complete line-item BOM with supplier P/Ns, unit prices, and build notes:
                </div>
                <div style={{ fontFamily: M, fontSize: 12, color: C.dimmer, marginTop: 6, lineHeight: 2 }}>
                    <div><span style={{ color: C.teal }}>serenity/docs/bom_revP.json</span> — machine-readable JSON with full part-level detail</div>
                    <div><span style={{ color: C.teal }}>serenity/docs/bom_revP.csv</span>  — spreadsheet-compatible CSV, 80+ line items</div>
                    <div><span style={{ color: C.dimmer }}>Historical: bom_revO.json/csv · bom_revN.json/csv · bom_revM.json · bom_revL.json · bom_revK.json/csv · bom_revJ.json/csv · bom_revI.json/csv</span></div>
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
                        ["serenity-rev-p.jsx",                "This document — complete Rev P specification (comprehensive, not a delta)", "Rev P ← CURRENT"],
                        ["serenity-rev-o.jsx",                "Rev O — CG-pivot nacelle, M=1.0 gear train, S1223 wings (delta doc)", "Rev O (superseded)"],
                        ["serenity-rev-n.jsx",                "Rev N — 24-inch hull, 50mm tandem EDFs", "Rev N (superseded)"],
                        ["serenity-rev-m.jsx",                "Rev M — PB2-I AM6254 hardware upgrade", "Rev M (superseded)"],
                        ["serenity-rev-l.jsx",                "Rev L — PID governor + EDF options", "Rev L (superseded)"],
                        ["serenity-rev-k.jsx",                "Rev K — 8× PB2 nodes + Cape-A/B + TPM", "Rev K (superseded)"],
                        ["serenity-rev-i.jsx",                "Rev I through Rev J series",          "Rev I–J (superseded)"],
                        ["serenity-rev-b.jsx through rev-f.jsx","Rev B–F series (CM4 era)",          "Rev B–F (superseded)"],
                        ["serenity-nacelle-pid-governor.jsx", "Per-EDF PID governor spec (Rev L new)","Rev L sub-spec"],
                        ["serenity-edf-options.jsx",          "EDF selection guide (Rev L new)",     "Rev L sub-spec"],
                        ["serenity-esc-telem-dual-edf.jsx",   "Dual-EDF ESC telemetry spec",         "Rev K sub-spec"],
                        ["serenity-connectivity-revH.jsx",    "Rev H connectivity / MIL-STD-1553 architecture","Rev H sub-spec"],
                        ["nacelle-nozzle-gear.jsx",           "Nacelle nozzle gear coupling detail",  "Rev E sub-spec"],
                        ["antenna-layout.jsx",                "Antenna layout specification",         "Rev B sub-spec"],
                    ]}
                />
            </Card>

            <Card title="BOM Files" accent={C.yellow}>
                <Table
                    cols={["File", "Revision", "Status"]}
                    accent={C.yellow}
                    rows={[
                        ["serenity/docs/bom_revP.json", "Rev P", "✓ CURRENT"],
                        ["serenity/docs/bom_revP.csv",  "Rev P", "✓ CURRENT"],
                        ["serenity/docs/bom_revO.json", "Rev O", "Superseded — retained for traceability"],
                        ["serenity/docs/bom_revO.csv",  "Rev O", "Superseded — retained for traceability"],
                        ["serenity/docs/bom_revN.json", "Rev N", "Historical"],
                        ["serenity/docs/bom_revN.csv",  "Rev N", "Historical"],
                        ["serenity/docs/bom_revM.json", "Rev M", "Historical"],
                        ["serenity/docs/bom_revL.json", "Rev L", "Historical"],
                        ["serenity/docs/bom_revK.json/csv","Rev K","Historical"],
                        ["serenity/docs/bom_revJ.json/csv","Rev J","Historical"],
                        ["serenity/docs/bom_revI.json/csv","Rev I","Historical"],
                    ]}
                />
            </Card>

            <Card title="Documentation Files" accent={C.green}>
                <Table
                    cols={["File", "Description", "Rev / Status"]}
                    accent={C.green}
                    rows={[
                        ["README.md",                               "Project overview, specs, attribution", "Rev P ← CURRENT"],
                        ["TODO.md",                                 "Full phased WBS (9 phases + firmware + regulatory)", "Rev P ← CURRENT"],
                        ["serenity/docs/PROJECT_INDEX.md",         "Complete file manifest, quick specs, connectivity", "Rev P ← CURRENT"],
                        ["serenity/docs/REVN_BUILD_GUIDE_24IN.md", "9-phase 24-inch build guide (Rev N/O specs)", "Rev N/O (updated to Rev P baseline)"],
                        ["serenity/docs/PHASED_BUILD_GUIDE.md",    "Legacy phased guide (Rev M 18-inch specs)", "Rev M — superseded for 24-inch builds"],
                        ["serenity/docs/AVIONICS_PB2_REDESIGN.md", "8-node PB2-I architecture reference", "Rev M / Rev K"],
                        ["serenity/docs/MANIFEST.json",            "SHA-256 checksums for all project files", "Updated with Rev P files"],
                        ["serenity/docs/LICENSE_AND_ATTRIBUTION.md","Full CC BY 4.0 text + all upstream attributions","Current"],
                        ["serenity/kicad/XCVR-49MHZ-1.md",        "XCVR-49MHZ-1 design notes + impedance check result","Rev P — Z₀=52.26Ω PASS"],
                    ]}
                />
            </Card>

            <Card title="Key SCAD / Python Build Commands" accent={C.teal}>
                <div style={{ fontFamily: M, fontSize: 12, lineHeight: 2 }}>
                    {[
                        ["# Nacelle shells — Blender (requires input STL):"],
                        ["blender --background --python thingverse-serenity/blender_nacelle_revo.py"],
                        [""],
                        ["# Nacelle pod from SCAD (self-contained):"],
                        ["openscad -o s_nacelle_port_revo.stl serenity/stl/nacelle_pod_50mm_tandem.scad -D SWIRL_DIR=1"],
                        ["openscad -o s_nacelle_stbd_revo.stl serenity/stl/nacelle_pod_50mm_tandem.scad -D SWIRL_DIR=-1"],
                        [""],
                        ["# Gear train components:"],
                        ["openscad -o nacelle_sector_gear.stl   serenity/stl/nacelle_sector_gear.scad"],
                        ["openscad -o nacelle_pinion.stl        serenity/stl/nacelle_pinion.scad"],
                        ["openscad -o nacelle_bevel_pair.stl    serenity/stl/nacelle_bevel_pair.scad"],
                        ["openscad -o nacelle_bevel_housing.stl serenity/stl/nacelle_bevel_housing.scad"],
                        [""],
                        ["# Cargo STLs:"],
                        ["python3 serenity/stl/generate_cargo_mounts.py  # outputs 8 cargo mount STLs"],
                        ["python3 serenity/stl/generate_cargo_doors.py   # outputs cargo_door_port/stbd.stl"],
                        [""],
                        ["# XCVR-49MHZ-1 RF trace impedance check:"],
                        ["python3 serenity/kicad/check_impedance.py       # W=2.75mm H=1.6mm er=4.5 T=35um"],
                    ].map((line, i) => (
                        <div key={i} style={{ color: line[0].startsWith("#") ? C.dimmer : C.green }}>
                            {line[0] || " "}
                        </div>
                    ))}
                </div>
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
                ["s_aft_edf_plenum.stl (SCAD export)", "○ OPEN — BLOCKS Phase 4"],
                ["s_neck_intake_frame.stl (SCAD export)", "○ OPEN — BLOCKS Phase 1"],
                ["s_rear_neck_intake_shell24.stl (SCAD export)", "○ OPEN — BLOCKS Phase 0"],
                ["nacelle_sector_gear.stl + all 4 gear SCADs", "○ OPEN"],
                ["s_wing_nacelle_pylon_revo.stl + s_wings_s1223_revo.stl", "○ OPEN"],
                ["s_middle_canonical_shell24.stl", "○ OPEN"],
                ["s_head_shell24.stl (Rev S sensor/antenna mounts)", "○ OPEN"],
                ["s_rcrs49_wire_post.stl", "○ OPEN"],
                ["Access panel frames A–F + lids (24\" version)", "○ OPEN"],
                ["cargo_gondola_shell.stl", "○ OPEN — BLOCKS Phase 8"],
                ["Cargo door STLs (port + stbd)", "✓ DONE  PR #22"],
                ["Cargo equipment mount STLs (8 parts)", "✓ DONE  PR #21"],
            ],
        },
        {
            phase: "Pre-Build: PCBs", status: "IN PROGRESS",
            color: C.yellow,
            items: [
                ["Cape-A-1 gerbers — regenerate from updated .kicad_pcb", "○ OPEN — BLOCKS Phase 6 fab"],
                ["Cape-B-1 gerbers — regenerate", "○ OPEN — BLOCKS Phase 6 fab"],
                ["XCVR-49MHZ-1 full schematic (Phase 2–5)", "○ OPEN"],
                ["XCVR-49MHZ-1 RF trace Z₀ = 52.26 Ω", "✓ DONE  PASS"],
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
                ["Iris nozzle assembly (8 petals + link ring)", "○ OPEN"],
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
            phase: "Phase 6 — Minimum Viable Flyer ★", status: "NOT STARTED",
            color: C.red,
            items: [
                ["CN1+FC1 (Bay A) + CN2+FC2 (Bay B) installed", "○ BLOCKED by Phase 5"],
                ["Cape-A/B PCBs received from JLCPCB", "○ BLOCKED by gerber regen"],
                ["TPM provisioning (all 4 nodes)", "○ OPEN"],
                ["CPLD write-blocker verification", "○ OPEN"],
                ["CAN FD heartbeat ring (0x001–0x004)", "○ OPEN"],
                ["serenity-cn Phase 6 + serenity-fc Phase 6 flashed", "✓ FIRMWARE DONE"],
                ["Ground tests (ESC cal, motor spin, CG, GPS lock)", "○ OPEN"],
                ["First tethered hover → first free hover → transition", "○ OPEN"],
                ["FAA registration applied to airframe", "○ OPEN  REQUIRED before free flight"],
            ],
        },
        {
            phase: "Phase 7 — Full 8-Node + OA", status: "NOT STARTED",
            color: C.red,
            items: [
                ["CN3+FC3 (Bay D) + CN4+FC4 (Bay E) installed", "○ BLOCKED by Phase 6"],
                ["12× VL53L5CX ToF sensors installed + configured", "○ OPEN"],
                ["Ethernet RSTP ring closed + verified", "○ OPEN"],
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
                ["Si5351A I²C driver + AM6254 DTS overlays", "✓ DONE  2026-05-25"],
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
export default function RevPSpec() {
    const [activeTab, setActiveTab] = useState("overview");

    const tabs = [
        { id: "overview",  label: "Overview"      },
        { id: "airframe",  label: "Airframe"       },
        { id: "propulsion",label: "Propulsion"     },
        { id: "avionics",  label: "Avionics"       },
        { id: "comms",     label: "Comms"          },
        { id: "cargo",     label: "Cargo (Rev P)"  },
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
                    SERENITY-CLASS TILTROTOR UAV — REV P
                    <Badge text="COMPLETE SPECIFICATION" color={C.green} />
                </div>
                <div style={{ color: C.dimmer, fontSize: 12 }}>
                    Cargo Bay Complete · 24-inch Hull · 8-Node PB2-I Avionics · M=1.0 Gear Train · Documentation Baseline
                </div>
                <div style={{ color: C.dimmer, fontSize: 11, marginTop: 4 }}>
                    Author: Steve Griffing PE(CSE) [Control Systems Engineering] CISSP-ISSEP CPP ·
                    CC BY 4.0 · 2026-06-01
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
                Serenity-Class Tiltrotor UAV Rev P · Steve Griffing PE(CSE) CISSP-ISSEP CPP ·
                CC BY 4.0 creativecommons.org/licenses/by/4.0 · 2026-06-01 ·
                Hull geometry CC BY 4.0 Peter Farell (printables.com/model/548545) ·
                Iris nozzle concept CC BY 4.0 BamJr (thingiverse.com/thing:2991269) ·
                Visual inspiration Joss Whedon / Mutant Enemy / Universal © all rights reserved
            </div>
        </div>
    );
}
