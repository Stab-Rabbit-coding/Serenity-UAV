/**
 * serenity-rev-o.jsx — Serenity-Class Tiltrotor UAV Rev O Specification
 *
 * Revision O: CG-Pivot Nacelle + Fully-Specified Gear / Nozzle Iris Linkage
 *
 * Key changes from Rev N:
 *   1. Nacelle tilt pivot relocated to nacelle CG (Z=83mm from intake, was 74mm).
 *      Eliminates gravity-induced torque on nacelle servo in all flight attitudes.
 *   2. Pivot bearing changed to MF104ZZ (4×10×4mm) — smaller and lighter than 686ZZ.
 *   3. Gear train fully specified: M=1.0mm module throughout.
 *      Sector R=22mm → Pinion A N=12T → Bevel pair N=14T (45° cone) → Crown N=12T
 *      → Nozzle ring rack R_eff=28mm. Ratio: 90°×3.667×0.214 = 70.7° ring travel.
 *   4. nacelle_pod_50mm_tandem.scad: parametric SCAD source for port + starboard nacelle.
 *   5. Complete iris nozzle redesign in nacelle_nozzle_iris.scad (M=1.0 rack).
 *   6. Longitudinal gear shaft conduit moulded into nacelle exterior.
 *   7. blender_nacelle_revo.py: updated generation script → *_revo.stl output.
 *
 * Author:  Steve Griffing, PE(CSE) [Control Systems Engineering], CISSP-ISSEP, CPP
 * License: CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/
 * Year:    2026
 */

import { useState } from "react";

// ── OpenDyslexic font loader ─────────────────────────────────────────────────
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
            * { color: #111111 !important; background: transparent !important; border-color: #333333 !important; }
            a { color: #003366 !important; }
        }
    `;
    document.head.appendChild(s);
    return null;
}

// ── Design tokens ────────────────────────────────────────────────────────────
const C = {
    bg:      "#060810",
    border:  "rgba(0,229,255,0.13)",
    accent:  "#00e5ff",
    orange:  "#ff6b35",
    yellow:  "#ffe600",
    purple:  "#c084fc",
    green:   "#4ade80",
    pink:    "#f472b6",
    teal:    "#2dd4bf",
    red:     "#f87171",
    lime:    "#a3e635",
    gold:    "#fbbf24",
    text:    "rgba(255,255,255,0.95)",
    dim:     "rgba(255,255,255,0.82)",
    dimmer:  "rgba(255,255,255,0.70)",
};
const M  = "'OpenDyslexic Mono','OpenDyslexicMono','Courier New',monospace";
const MB = "'OpenDyslexic Bold','OpenDyslexic',sans-serif";

// ── Nacelle geometry constants (1× reference, Z=0=intake) ───────────────────
const NACELLE_L      = 148.3;   // mm total nacelle length
const EDF1_ENTRY     =  22.0;
const EDF1_EXIT      =  72.0;
const STATOR_BOT     =  75.0;
const STATOR_TOP     =  95.0;
const EDF2_ENTRY     =  98.0;
const EDF2_EXIT      = 143.0;
const PIVOT_OLD      =  74.0;   // Rev N pivot Z
const PIVOT_NEW      =  83.0;   // Rev O pivot Z (at CG)
const CROWN_Z        = 133.0;   // crown pinion Z
const NOZZLE_Z       = 133.0;   // nozzle ring bottom Z

// CG mass breakdown
const CG_ROWS = [
    { part: "Shell  CF-PETG",               mass: 130, z_cg: 74.2  },
    { part: "Thrust tube sleeve",            mass:  18, z_cg: 75.0  },
    { part: "EDF1  upstream  (Z=22..72)",    mass:  68, z_cg: 47.0  },
    { part: "ESC1  (co-located EDF1)",       mass:  25, z_cg: 47.0  },
    { part: "EDF2  downstream (Z=98..143)",  mass:  68, z_cg: 120.5 },
    { part: "ESC2  (co-located EDF2)",       mass:  25, z_cg: 120.5 },
    { part: "Stator hub+fins  (Z=75..95)",   mass:   8, z_cg: 85.0  },
    { part: "Nozzle iris + hardware",         mass:  22, z_cg: 140.0 },
    { part: "Gear train  (M1.0 all gears)",  mass:  18, z_cg: 90.0  },
    { part: "LED ring",                       mass:   8, z_cg: 143.0 },
    { part: "Inlet bell",                     mass:  10, z_cg: 11.0  },
    { part: "Wiring (motor + ESC leads)",    mass:  12, z_cg: 80.0  },
    { part: "Motor mount struts (×2 sets)",  mass:   6, z_cg: 82.5  },
    { part: "Clevis / pivot boss",            mass:   8, z_cg: 74.0  },
    { part: "Fasteners / misc",              mass:   8, z_cg: 100.0 },
];
const TOTAL_MASS   = CG_ROWS.reduce((s, r) => s + r.mass, 0);
const TOTAL_MOMENT = CG_ROWS.reduce((s, r) => s + r.mass * r.z_cg, 0);
const CG_Z         = TOTAL_MOMENT / TOTAL_MASS;

// Gear train
const GEAR_TRAIN = [
    { label: "Sector gear",    R: 22, N: 88,  mod: 1.0, type: "M=1.0 sector R=22mm,  38T arc (155°) — FIXED to tilt bracket" },
    { label: "Drive pinion A", R:  6, N: 12,  mod: 1.0, type: "M=1.0 spur  N=12T,  R=6mm — on nacelle at pivot Z" },
    { label: "Bevel A (trans.)",R: 7, N: 14,  mod: 1.0, type: "M=1.0 bevel N=14T,  45° cone — transverse shaft" },
    { label: "Bevel B (long.)", R:  7, N: 14,  mod: 1.0, type: "M=1.0 bevel N=14T,  45° cone — longitudinal shaft" },
    { label: "Crown pinion",   R:  6, N: 12,  mod: 1.0, type: "M=1.0 spur  N=12T,  R=6mm — drives nozzle ring rack" },
    { label: "Nozzle ring rack",R:28, N: null, mod: 1.0, type: "M=1.0 rack on inner ring ID,  R_eff=28mm" },
];

// ── SVG nacelle profile diagram ──────────────────────────────────────────────
function NacelleDiagram() {
    const W = 520;
    const H = 140;
    const PAD_L = 20;
    const PAD_R = 20;
    const scale = (W - PAD_L - PAD_R) / NACELLE_L;   // px per mm
    const cx = (z) => PAD_L + z * scale;
    const mid = H / 2;
    const BORE_R   = 25 * scale * 0.55;   // visual bore half-height
    const NACELLE_R= 33 * scale * 0.55;   // nacelle outer half-height (visual)

    // Regions
    const regions = [
        { z0: 0,         z1: EDF1_ENTRY, fill: "rgba(0,229,255,0.08)",  label: "Bell"   },
        { z0: EDF1_ENTRY,z1: EDF1_EXIT,  fill: "rgba(74,222,128,0.12)", label: "EDF1"   },
        { z0: STATOR_BOT,z1: STATOR_TOP, fill: "rgba(196,132,252,0.22)",label: "Stator" },
        { z0: EDF2_ENTRY,z1: EDF2_EXIT,  fill: "rgba(255,107,53,0.12)", label: "EDF2"   },
        { z0: NOZZLE_Z,  z1: NACELLE_L,  fill: "rgba(251,191,36,0.12)", label: "Nozzle" },
    ];

    // Markers
    const markers = [
        { z: PIVOT_OLD, color: C.red,    dash: "4,4", label: "Pivot N\n74mm"  },
        { z: PIVOT_NEW, color: C.green,  dash: "0",   label: "Pivot O\n83mm (CG)" },
        { z: CROWN_Z,   color: C.gold,   dash: "4,4", label: "Crown\n133mm"   },
    ];

    return (
        <svg viewBox={`0 0 ${W} ${H}`} style={{ width: "100%", maxWidth: W, display: "block" }}>
            {/* Nacelle outer shell */}
            <rect x={PAD_L} y={mid - NACELLE_R} width={(NACELLE_L) * scale}
                  height={NACELLE_R * 2} rx={8}
                  fill="rgba(0,229,255,0.04)" stroke={C.accent} strokeWidth={1.2} />
            {/* Bore */}
            <rect x={PAD_L + EDF1_ENTRY * scale} y={mid - BORE_R}
                  width={(NACELLE_L - EDF1_ENTRY) * scale} height={BORE_R * 2}
                  fill="rgba(0,0,0,0.35)" stroke="rgba(0,229,255,0.25)" strokeWidth={0.8} />
            {/* Region highlights */}
            {regions.map((r, i) => (
                <rect key={i}
                      x={cx(r.z0)} y={mid - NACELLE_R}
                      width={(r.z1 - r.z0) * scale} height={NACELLE_R * 2}
                      fill={r.fill} />
            ))}
            {/* Region labels */}
            {regions.map((r, i) => (
                <text key={i}
                      x={cx((r.z0 + r.z1) / 2)} y={mid - NACELLE_R - 5}
                      textAnchor="middle" fontSize={7.5} fill={C.dimmer}
                      fontFamily={M}>{r.label}</text>
            ))}
            {/* Z-axis markers */}
            {markers.map((m, i) => {
                const x = cx(m.z);
                return (
                    <g key={i}>
                        <line x1={x} y1={mid - NACELLE_R - 2} x2={x} y2={mid + NACELLE_R + 2}
                              stroke={m.color} strokeWidth={1.8} strokeDasharray={m.dash} />
                        <text x={x} y={mid + NACELLE_R + 16 + (i % 2) * 10}
                              textAnchor="middle" fontSize={7.5} fill={m.color}
                              fontFamily={M}>{m.label.split("\n")[0]}</text>
                        <text x={x} y={mid + NACELLE_R + 26 + (i % 2) * 10}
                              textAnchor="middle" fontSize={7.0} fill={m.color}
                              fontFamily={M}>{m.label.split("\n")[1]}</text>
                    </g>
                );
            })}
            {/* Intake / exhaust labels */}
            <text x={PAD_L + 2} y={mid + 3} fontSize={8} fill={C.accent} fontFamily={M}>←Intake</text>
            <text x={cx(NACELLE_L) - 2} y={mid + 3} fontSize={8} fill={C.accent}
                  fontFamily={M} textAnchor="end">Exhaust→</text>
            {/* Scale bar */}
            <line x1={PAD_L} y1={H - 6} x2={cx(50)} y2={H - 6}
                  stroke={C.dim} strokeWidth={0.8} />
            <text x={(PAD_L + cx(50)) / 2} y={H - 1} textAnchor="middle"
                  fontSize={7} fill={C.dim} fontFamily={M}>50 mm</text>
        </svg>
    );
}

// ── Gear ratio diagram ───────────────────────────────────────────────────────
function GearRatioDiagram() {
    const steps = [
        { label: "Nacelle tilt", val: "90°",   note: "Input" },
        { label: "Sector→Pinion", val: "×3.667", note: "22÷6" },
        { label: "Pinion A",     val: "330°",  note: "Output" },
        { label: "Bevel pair",   val: "×1.0",  note: "1:1, 90°" },
        { label: "Long. shaft",  val: "330°",  note: "redirected" },
        { label: "Crown→Ring",   val: "×0.214", note: "6÷28" },
        { label: "Nozzle ring",  val: "70.7°", note: "OPEN" },
    ];
    return (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 4, alignItems: "center" }}>
            {steps.map((s, i) => (
                <span key={i} style={{ display: "flex", alignItems: "center", gap: 4 }}>
                    <span style={{
                        background: "rgba(0,229,255,0.08)", border: `1px solid ${C.border}`,
                        borderRadius: 6, padding: "4px 8px", fontSize: 12,
                        fontFamily: M, color: C.text,
                    }}>
                        <span style={{ color: C.accent }}>{s.val}</span>
                        <span style={{ color: C.dimmer, marginLeft: 4 }}>{s.label}</span>
                        <br />
                        <span style={{ color: C.dimmer, fontSize: 10 }}>{s.note}</span>
                    </span>
                    {i < steps.length - 1 && (
                        <span style={{ color: C.accent, fontSize: 16 }}>→</span>
                    )}
                </span>
            ))}
        </div>
    );
}

// ── Section card component ───────────────────────────────────────────────────
function Card({ title, accent, children }) {
    return (
        <div style={{
            border: `1px solid ${accent || C.border}`,
            borderRadius: 10,
            padding: "16px 20px",
            marginBottom: 18,
            background: "rgba(255,255,255,0.025)",
        }}>
            <div style={{
                color: accent || C.accent,
                fontFamily: MB, fontSize: 15, fontWeight: 700,
                marginBottom: 12, letterSpacing: 0.5,
                textTransform: "uppercase",
            }}>{title}</div>
            {children}
        </div>
    );
}

function Row({ label, value, note }) {
    return (
        <tr>
            <td style={{ padding: "3px 12px 3px 0", color: C.dim,  fontFamily: M, fontSize: 12.5 }}>{label}</td>
            <td style={{ padding: "3px 12px 3px 0", color: C.text, fontFamily: M, fontSize: 12.5 }}>{value}</td>
            {note && <td style={{ padding: "3px 0", color: C.dimmer, fontFamily: M, fontSize: 11 }}>{note}</td>}
        </tr>
    );
}

// ── Main component ───────────────────────────────────────────────────────────
export default function RevOSpec() {
    const [activeTab, setActiveTab] = useState("overview");

    const tabs = [
        { id: "overview",  label: "Overview"      },
        { id: "cg",        label: "CG Analysis"   },
        { id: "gears",     label: "Gear Train"    },
        { id: "nozzle",    label: "Iris Nozzle"   },
        { id: "bom",       label: "Rev O Changes" },
        { id: "files",     label: "Files"         },
        { id: "winglift",  label: "Wing Lift"     },
        { id: "pylon",     label: "Pylon"         },
    ];

    return (
        <div style={{
            background: C.bg, color: C.text, minHeight: "100vh",
            padding: "24px 20px", fontFamily: M,
        }}>
            <_ODFontLoader />

            {/* Header */}
            <div style={{ marginBottom: 24 }}>
                <div style={{
                    fontFamily: MB, fontSize: 22, color: C.accent,
                    letterSpacing: 1, marginBottom: 4,
                }}>
                    SERENITY-CLASS TILTROTOR UAV — REV O
                </div>
                <div style={{ color: C.dimmer, fontSize: 12 }}>
                    CG-Pivot Nacelles · M=1.0 Gear Train · Iris Nozzle Linkage · 24-inch Scale
                </div>
                <div style={{ color: C.dimmer, fontSize: 11, marginTop: 4 }}>
                    Author: Steve Griffing PE(CSE) [Control Systems Engineering] CISSP-ISSEP CPP ·
                    CC BY 4.0 · 2026-05-24
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

            {/* ── Overview ─────────────────────────────────────────────────── */}
            {activeTab === "overview" && (
                <div>
                    <Card title="Nacelle Profile — Rev O" accent={C.accent}>
                        <NacelleDiagram />
                        <div style={{ marginTop: 12, fontSize: 11, color: C.dimmer }}>
                            Green line = Rev O CG pivot (Z=83mm). Red dashed = Rev N pivot (Z=74mm).
                            Gold dashed = Crown pinion / nozzle ring bottom (Z=133mm).
                        </div>
                    </Card>

                    <Card title="Rev O vs Rev N — Key Changes" accent={C.orange}>
                        <table style={{ borderCollapse: "collapse", width: "100%" }}>
                            <thead>
                                <tr>
                                    {["Parameter", "Rev N", "Rev O", "Reason"].map(h => (
                                        <th key={h} style={{
                                            color: C.orange, fontFamily: MB, fontSize: 11,
                                            padding: "4px 10px 4px 0", textAlign: "left",
                                            borderBottom: `1px solid ${C.border}`,
                                        }}>{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {[
                                    ["Pivot Z (1× ref)","74 mm","83 mm","CG-derived — zero gravity moment on servo"],
                                    ["Pivot bearing","686ZZ  6×13×3.5 mm","MF104ZZ  4×10×4 mm","Smaller, lighter; matches BOM spec"],
                                    ["Gear module","M=0.5 (planned)","M=1.0  throughout","Printable in FDM; M0.5 required SLA only"],
                                    ["Sector arc","22T / 90°","38T / 155°","Covers −5°..140° hard-stop range"],
                                    ["Pinion A","12T / R=3mm (M0.5)","12T / R=6mm (M=1.0)","Consistent with M=1.0"],
                                    ["Bevel pair","14T / R=3.5mm (M0.5)","14T / R=7mm (M=1.0)","Printable face width ≥ 4mm"],
                                    ["Shaft conduit","Not present","Moulded into nacelle skin","Routes 3mm CF shaft Z=83→133mm"],
                                    ["SCAD source","blender script only","nacelle_pod_50mm_tandem.scad","Fully parametric, no STL import needed"],
                                    ["Nozzle iris SCAD","nacelle_nozzle_iris.scad (M0.5)","nacelle_nozzle_iris.scad  (M=1.0 rack)","Module upgrade"],
                                    ["Blender script","blender_nacelle_integrated_v2.py","blender_nacelle_revo.py","CG pivot + gear mount bosses"],
                                ].map((row, i) => (
                                    <tr key={i} style={{ background: i % 2 ? "rgba(255,255,255,0.02)" : "transparent" }}>
                                        {row.map((cell, j) => (
                                            <td key={j} style={{
                                                padding: "4px 10px 4px 0",
                                                color: j === 0 ? C.dim : j === 2 ? C.green : C.text,
                                                fontFamily: M, fontSize: 11.5,
                                            }}>{cell}</td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </Card>
                </div>
            )}

            {/* ── CG Analysis ──────────────────────────────────────────────── */}
            {activeTab === "cg" && (
                <div>
                    <Card title="Nacelle CG Mass Breakdown" accent={C.green}>
                        <table style={{ borderCollapse: "collapse", width: "100%" }}>
                            <thead>
                                <tr>
                                    {["Component","Mass (g)","Z_cg (mm)","Moment (g·mm)"].map(h => (
                                        <th key={h} style={{
                                            color: C.green, fontFamily: MB, fontSize: 11,
                                            padding: "4px 12px 4px 0", textAlign: "left",
                                            borderBottom: `1px solid ${C.border}`,
                                        }}>{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {CG_ROWS.map((r, i) => (
                                    <tr key={i} style={{ background: i % 2 ? "rgba(74,222,128,0.03)" : "transparent" }}>
                                        <td style={{ padding: "3px 12px 3px 0", color: C.dim,  fontFamily: M, fontSize: 11.5 }}>{r.part}</td>
                                        <td style={{ padding: "3px 12px 3px 0", color: C.text, fontFamily: M, fontSize: 11.5, textAlign: "right" }}>{r.mass}</td>
                                        <td style={{ padding: "3px 12px 3px 0", color: C.text, fontFamily: M, fontSize: 11.5, textAlign: "right" }}>{r.z_cg.toFixed(1)}</td>
                                        <td style={{ padding: "3px 0",          color: C.text, fontFamily: M, fontSize: 11.5, textAlign: "right" }}>{(r.mass * r.z_cg).toFixed(0)}</td>
                                    </tr>
                                ))}
                                <tr style={{ borderTop: `1px solid ${C.green}` }}>
                                    <td style={{ padding: "4px 12px 4px 0", color: C.green, fontFamily: MB, fontSize: 12 }}>TOTAL</td>
                                    <td style={{ padding: "4px 12px 4px 0", color: C.green, fontFamily: MB, fontSize: 12, textAlign: "right" }}>{TOTAL_MASS}</td>
                                    <td style={{ padding: "4px 12px 4px 0", color: C.green, fontFamily: MB, fontSize: 12, textAlign: "right" }}>—</td>
                                    <td style={{ padding: "4px 0",          color: C.green, fontFamily: MB, fontSize: 12, textAlign: "right" }}>{TOTAL_MOMENT.toFixed(0)}</td>
                                </tr>
                            </tbody>
                        </table>
                        <div style={{
                            marginTop: 16, padding: "12px 16px",
                            background: "rgba(74,222,128,0.08)",
                            border: `1px solid rgba(74,222,128,0.3)`,
                            borderRadius: 8, fontFamily: M, fontSize: 13,
                        }}>
                            <span style={{ color: C.green, fontFamily: MB }}>CG_Z = </span>
                            <span style={{ color: C.text }}>{TOTAL_MOMENT.toFixed(0)} ÷ {TOTAL_MASS} = </span>
                            <span style={{ color: C.green, fontFamily: MB }}>{CG_Z.toFixed(1)} mm from intake</span>
                            <span style={{ color: C.dimmer }}> → pivot set to 83.0 mm</span>
                        </div>
                        <div style={{ marginTop: 10, color: C.dimmer, fontSize: 11 }}>
                            Note: All masses are per nacelle (one side). CG is 56% from intake toward exhaust —
                            the two EDFs at Z=120.5mm contribute more moment than EDF1 at Z=47mm.
                            Pivot at CG eliminates the servo from fighting gravity in any nacelle orientation.
                        </div>
                    </Card>

                    <Card title="Pivot Comparison: Rev N vs Rev O" accent={C.purple}>
                        <table style={{ borderCollapse: "collapse" }}>
                            <tbody>
                                <Row label="Rev N pivot Z"         value="74.0 mm" note="Between EDF1 exit (72mm) and stator (75mm)" />
                                <Row label="Rev O pivot Z (CG)"    value="83.0 mm" note="Mid-stator region; boss on exterior, no fin interference" />
                                <Row label="Delta"                  value="+9.0 mm" note="Pivot moved 9mm toward exhaust" />
                                <Row label="Bearing (Rev N v1)"    value="686ZZ 6×13×3.5mm" />
                                <Row label="Bearing (Rev O)"       value="MF104ZZ 4×10×4mm" note="Flanged; 2 per nacelle, press-fit" />
                                <Row label="Pivot rod"             value="4mm OD CF, cut to length" />
                                <Row label="Max servo torque improvement" value="~12% reduction" note="From removing gravity moment of EDF2 rear mass" />
                            </tbody>
                        </table>
                    </Card>
                </div>
            )}

            {/* ── Gear Train ───────────────────────────────────────────────── */}
            {activeTab === "gears" && (
                <div>
                    <Card title="Passive Nozzle Gear Train — Rev O (M=1.0)" accent={C.yellow}>
                        <GearRatioDiagram />
                        <div style={{ marginTop: 16, color: C.dimmer, fontSize: 11 }}>
                            The sector gear is fixed to the fuselage tilt bracket. As the nacelle tilts,
                            Drive Pinion A rolls along the sector arc, rotating the bevel pair, which routes
                            torque 90° through a longitudinal CF shaft to the Crown Pinion at the nozzle end.
                            The Crown Pinion drives rack teeth on the inner ring of the iris nozzle.
                        </div>
                    </Card>

                    <Card title="Gear Specifications — M=1.0 Throughout" accent={C.gold}>
                        <table style={{ borderCollapse: "collapse", width: "100%" }}>
                            <thead>
                                <tr>
                                    {["Gear","Module","Teeth","Pitch R","Notes"].map(h => (
                                        <th key={h} style={{
                                            color: C.gold, fontFamily: MB, fontSize: 11,
                                            padding: "4px 12px 4px 0", textAlign: "left",
                                            borderBottom: `1px solid ${C.border}`,
                                        }}>{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {[
                                    ["Sector gear",     "M=1.0","38T arc","22 mm","Fixed to tilt bracket; 155° arc covers −5°..140° range"],
                                    ["Drive Pinion A",  "M=1.0","12T","6 mm","On nacelle at pivot Z; rolls along sector; MR63ZZ shafts"],
                                    ["Bevel A (trans.)","M=1.0","14T","7 mm","45° pitch cone; keyed to Pinion A shaft (transverse)"],
                                    ["Bevel B (long.)", "M=1.0","14T","7 mm","45° pitch cone; keyed to longitudinal CF shaft"],
                                    ["Crown pinion",    "M=1.0","12T","6 mm","At Z=133mm; drives nozzle ring inner rack teeth"],
                                    ["Nozzle ring rack","M=1.0","22T arc","28 mm (eff.)","On inner diameter of rotating iris ring; 71° travel"],
                                ].map((row, i) => (
                                    <tr key={i} style={{ background: i % 2 ? "rgba(251,191,36,0.04)" : "transparent" }}>
                                        {row.map((cell, j) => (
                                            <td key={j} style={{
                                                padding: "4px 12px 4px 0",
                                                color: j === 0 ? C.gold : C.text,
                                                fontFamily: M, fontSize: 11.5,
                                            }}>{cell}</td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>

                        <div style={{ marginTop: 16 }}>
                            <div style={{ color: C.gold, fontFamily: MB, fontSize: 12, marginBottom: 6 }}>
                                Ratio Verification
                            </div>
                            {[
                                ["Step 1: Sector → Pinion A", "22 ÷ 6 = 3.667:1", "90° nacelle → 330° Pinion A"],
                                ["Step 2: Bevel pair 1:1",    "1.000:1",           "330° → 330° longitudinal shaft"],
                                ["Step 3: Crown → Ring rack", "6 ÷ 28 = 0.2143",  "330° → 70.7° nozzle ring"],
                                ["Total at 90° nacelle",      "3.667 × 0.2143",    "= 0.786 → 70.7° ring ✓"],
                            ].map((r, i) => (
                                <div key={i} style={{ display: "flex", gap: 16, marginBottom: 3, fontSize: 12 }}>
                                    <span style={{ color: C.dim, width: 200 }}>{r[0]}</span>
                                    <span style={{ color: C.gold, width: 100, fontFamily: M }}>{r[1]}</span>
                                    <span style={{ color: C.dimmer }}>{r[2]}</span>
                                </div>
                            ))}
                        </div>
                    </Card>

                    <Card title="Shaft Routing" accent={C.teal}>
                        <table style={{ borderCollapse: "collapse" }}>
                            <tbody>
                                <Row label="Transverse shaft (Pinion A ↔ Bevel A)"
                                     value="3mm CF rod, 22mm long"
                                     note="Through MR63ZZ bearings in Pinion A boss; co-planar with pivot axis" />
                                <Row label="Longitudinal shaft (Bevel B → Crown)"
                                     value="3mm CF rod, 52mm long"
                                     note="Inside 4mm OD PTFE sleeve in nacelle conduit; Z=83→133mm" />
                                <Row label="Conduit position"
                                     value="R=31mm from bore axis, inboard face"
                                     note="Clears thrust tube OD (27.5mm) and nacelle outer skin" />
                                <Row label="Conduit feature"
                                     value="OD=5.5mm, ID=3.5mm, moulded into nacelle"
                                     note="Generated by blender_nacelle_revo.py and nacelle_pod_50mm_tandem.scad" />
                                <Row label="Bevel housing"
                                     value="24×14×20mm CF-PETG block"
                                     note="Mounts to two M2.5 boss posts on inboard nacelle face; contains both bevels" />
                            </tbody>
                        </table>
                    </Card>
                </div>
            )}

            {/* ── Iris Nozzle ──────────────────────────────────────────────── */}
            {activeTab === "nozzle" && (
                <div>
                    <Card title="Iris Nozzle Assembly — Rev O" accent={C.pink}>
                        <table style={{ borderCollapse: "collapse" }}>
                            <tbody>
                                <Row label="Bore diameter"      value="50 mm (flush with EDF bore)" />
                                <Row label="Nozzle CLOSED exit" value="36 mm (cruise)"              note="0° nacelle → ring at 0° → petals closed" />
                                <Row label="Nozzle OPEN exit"   value="42 mm (hover)"               note="90° nacelle → ring at 70.7° → petals open" />
                                <Row label="Petals"             value="8 per nacelle × 2 = 16 total" />
                                <Row label="Hinge pins"         value="3mm OD × 5mm stainless steel, 1 per petal" />
                                <Row label="Link ring"          value="0.8mm piano wire bent ring, links petals to inner ring" />
                                <Row label="Inner ring"         value="OD=62mm ID=50mm H=8mm CF-PETG" note="Rotating; M=1.0 rack teeth on inner bore face" />
                                <Row label="Outer housing"      value="OD=70mm ID=63mm H=10mm CF-PETG" note="Fixed to nacelle exit face; hinge bore × 8" />
                                <Row label="Crown pinion seat"  value="Z=133mm on nacelle, MR63ZZ × 2" />
                                <Row label="Hard stop"          value="Internal tab limits ring to 71° max" note="Prevents over-drive at nacelle >90°" />
                                <Row label="Rack module"        value="M=1.0" note="Matches crown pinion" />
                                <Row label="Rack teeth on arc"  value="22T (covers 71° + margin)" />
                                <Row label="Petal material"     value="PETG body + translucent-blue inner face" note="LED backlight through inner petal face" />
                                <Row label="LED ring"           value="WS2812B, 1 per nacelle nozzle + 1 rear" />
                                <Row label="SCAD source"        value="nacelle_nozzle_iris.scad" />
                            </tbody>
                        </table>
                    </Card>

                    <Card title="Nozzle Area Analysis" accent={C.lime}>
                        <table style={{ borderCollapse: "collapse" }}>
                            <tbody>
                                <Row label="EDF bore area"    value="π × 25² = 1,963 mm²" note="50mm ID" />
                                <Row label="Nozzle CLOSED area" value="π × 18² = 1,018 mm²" note="36mm exit dia; velocity ×1.93 vs bore" />
                                <Row label="Nozzle OPEN area"   value="π × 21² = 1,385 mm²" note="42mm exit dia; velocity ×1.42 vs bore" />
                                <Row label="Area ratio closed/open" value="0.735" note="Nozzle acts as a variable-area thrust nozzle" />
                                <Row label="Cruise benefit"     value="Higher jet velocity → better propulsive efficiency at speed" />
                                <Row label="Hover benefit"      value="Lower backpressure → more static thrust for same power" />
                            </tbody>
                        </table>
                    </Card>
                </div>
            )}

            {/* ── BOM Changes ──────────────────────────────────────────────── */}
            {activeTab === "bom" && (
                <div>
                    <Card title="Rev O New / Changed BOM Items" accent={C.orange}>
                        <table style={{ borderCollapse: "collapse", width: "100%" }}>
                            <thead>
                                <tr>
                                    {["Ref","Description","Qty","Change"].map(h => (
                                        <th key={h} style={{
                                            color: C.orange, fontFamily: MB, fontSize: 11,
                                            padding: "4px 12px 4px 0", textAlign: "left",
                                            borderBottom: `1px solid ${C.border}`,
                                        }}>{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {[
                                    ["MF104ZZ",         "Flanged bearing 4×10×4mm — nacelle pivot",     "4",  "Was 686ZZ in v1; BOM already spec'd MF104ZZ ✓"],
                                    ["SECTOR-M1-R22",   "M=1.0 sector gear R=22mm, 38T arc",           "2",  "New — replaces unspecified M0.5 sector"],
                                    ["PINION-A-M1-12T", "M=1.0 drive pinion N=12T R=6mm",             "2",  "New — drive pinion A for each nacelle"],
                                    ["BEVEL-M1-14T",    "M=1.0 bevel pair N=14T 45° cone",            "4",  "New — 2 gears × 2 nacelles"],
                                    ["CROWN-M1-12T",    "M=1.0 crown pinion N=12T R=6mm",             "2",  "New — crown pinion for each nacelle"],
                                    ["BEVEL-HOUSING",   "CF-PETG bevel gear housing 24×14×20mm",       "2",  "New — mounts to nacelle inboard boss posts"],
                                    ["SHAFT-CF-3MM",    "3mm CF rod — gear shafts cut to length",      "1",  "New — 300mm per nacelle pair"],
                                    ["BRG-MR63ZZ",      "MR63ZZ bearing 3×6×2.5mm — gear shafts",      "8",  "New — 2 per pinion × 4 pinions/crowns"],
                                    ["PTFE-SLEEVE-4MM", "PTFE tube 4×3mm — longitudinal shaft sleeve", "1",  "New — 52mm per nacelle, prevents CF shaft seizing"],
                                ].map((row, i) => (
                                    <tr key={i} style={{ background: i % 2 ? "rgba(255,107,53,0.04)" : "transparent" }}>
                                        {row.map((cell, j) => (
                                            <td key={j} style={{
                                                padding: "4px 12px 4px 0",
                                                color: j === 0 ? C.orange : j === 3 ? C.dimmer : C.text,
                                                fontFamily: M, fontSize: 11.5,
                                            }}>{cell}</td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        <div style={{ marginTop: 10, color: C.dimmer, fontSize: 11 }}>
                            All other Rev N items unchanged. Full BOM in bom_revO.json / bom_revO.csv.
                        </div>
                    </Card>
                </div>
            )}

            {/* ── Files ────────────────────────────────────────────────────── */}
            {activeTab === "files" && (
                <div>
                    <Card title="Rev O New / Modified Files" accent={C.teal}>
                        <table style={{ borderCollapse: "collapse", width: "100%" }}>
                            <thead>
                                <tr>
                                    {["File","Type","Description"].map(h => (
                                        <th key={h} style={{
                                            color: C.teal, fontFamily: MB, fontSize: 11,
                                            padding: "4px 14px 4px 0", textAlign: "left",
                                            borderBottom: `1px solid ${C.border}`,
                                        }}>{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {[
                                    ["thingverse-serenity/blender_nacelle_revo.py",          "Blender/Python","Updated nacelle generation script: CG pivot Z=83mm + gear mount bosses + shaft conduit"],
                                    ["serenity/stl/nacelle_pod_50mm_tandem.scad",            "OpenSCAD","Parametric nacelle pod SCAD — complete from-scratch design, no STL import"],
                                    ["serenity/stl/nacelle_sector_gear.scad",                "OpenSCAD","M=1.0 sector gear R=22mm, 38T, 155° arc — print resin SLA"],
                                    ["serenity/stl/nacelle_pinion.scad",                    "OpenSCAD","M=1.0 drive pinion A (12T) and crown pinion (12T) — both same spec"],
                                    ["serenity/stl/nacelle_bevel_pair.scad",                "OpenSCAD","M=1.0 bevel pair N=14T 45° pitch cone — 1:1, 90° redirect"],
                                    ["serenity/stl/nacelle_bevel_housing.scad",             "OpenSCAD","CF-PETG bevel housing block with MR63ZZ bearing seats"],
                                    ["serenity/stl/nacelle_nozzle_iris.scad",               "OpenSCAD","Complete iris nozzle: rotating ring (M=1.0 rack) + outer housing + petal"],
                                    ["serenity/docs/bom_revO.json",                         "JSON","Rev O bill of materials — adds gear train section"],
                                    ["serenity/docs/bom_revO.csv",                          "CSV","Rev O BOM in spreadsheet format"],
                                    ["serenity/artifacts/serenity-rev-o.jsx",               "JSX","This specification document"],
                                ].map((row, i) => (
                                    <tr key={i} style={{ background: i % 2 ? "rgba(45,212,191,0.03)" : "transparent" }}>
                                        {row.map((cell, j) => (
                                            <td key={j} style={{
                                                padding: "4px 14px 4px 0",
                                                color: j === 0 ? C.teal : j === 1 ? C.purple : C.dim,
                                                fontFamily: M, fontSize: 11,
                                            }}>{cell}</td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </Card>

                    <Card title="Build Commands" accent={C.purple}>
                        <div style={{ fontFamily: M, fontSize: 12, lineHeight: 2 }}>
                            {[
                                ["# Generate nacelle STLs via Blender (requires nacelle shell STL inputs):"],
                                ["blender --background --python thingverse-serenity/blender_nacelle_revo.py"],
                                [""],
                                ["# Generate nacelle pod from SCAD (self-contained, no input STL):"],
                                ["openscad -o s_nacelle_port_revo.stl serenity/stl/nacelle_pod_50mm_tandem.scad -D SWIRL_DIR=1"],
                                ["openscad -o s_nacelle_stbd_revo.stl serenity/stl/nacelle_pod_50mm_tandem.scad -D SWIRL_DIR=-1"],
                                [""],
                                ["# Generate gear components:"],
                                ["openscad -o nacelle_sector_gear.stl   serenity/stl/nacelle_sector_gear.scad"],
                                ["openscad -o nacelle_pinion.stl        serenity/stl/nacelle_pinion.scad"],
                                ["openscad -o nacelle_bevel_pair.stl    serenity/stl/nacelle_bevel_pair.scad"],
                                ["openscad -o nacelle_bevel_housing.stl serenity/stl/nacelle_bevel_housing.scad"],
                                [""],
                                ["# Generate nozzle iris components:"],
                                ["openscad -o nozzle_inner_ring_revo.stl  serenity/stl/nacelle_nozzle_iris.scad -D RENDER_PART=1"],
                                ["openscad -o nozzle_outer_housing_revo.stl serenity/stl/nacelle_nozzle_iris.scad -D RENDER_PART=2"],
                                ["openscad -o nozzle_petal_revo.stl       serenity/stl/nacelle_nozzle_iris.scad -D RENDER_PART=3"],
                            ].map((line, i) => (
                                <div key={i} style={{ color: line[0].startsWith("#") ? C.dimmer : C.green }}>
                                    {line[0] || " "}
                                </div>
                            ))}
                        </div>
                    </Card>
                </div>
            )}

            {/* ── Wing Lift Analysis ───────────────────────────────────────── */}
            {activeTab === "winglift" && (
                <div>
                    {/* ── Section header ── */}
                    <div style={{ marginBottom: 20 }}>
                        <div style={{ fontFamily: MB, fontSize: 18, color: C.accent, letterSpacing: 1 }}>
                            WING LIFT ANALYSIS — FORWARD FLIGHT
                        </div>
                        <div style={{ color: C.dimmer, fontSize: 12, marginTop: 4 }}>
                            Lift contribution at cruise speed; airfoil improvement recommendation
                        </div>
                    </div>

                    {/* ── Given / constants ── */}
                    <Card title="Given — Flight Conditions &amp; Geometry" accent={C.accent}>
                        <table style={{ borderCollapse: "collapse", width: "100%" }}>
                            <tbody>
                                {/* AUW */}
                                <tr>
                                    <td style={{ padding: "4px 14px 4px 0", color: C.dim,  fontFamily: M, fontSize: 12, whiteSpace: "nowrap" }}>AUW</td>
                                    <td style={{ padding: "4px 14px 4px 0", color: C.text, fontFamily: M, fontSize: 12 }}>3 550 g = 3.55 kg</td>
                                    <td style={{ padding: "4px 0", color: C.dimmer, fontFamily: M, fontSize: 11 }}>Weight W = 3.55 × 9.81 = 34.8 N</td>
                                </tr>
                                {/* Cruise speed */}
                                <tr style={{ background: "rgba(0,229,255,0.03)" }}>
                                    <td style={{ padding: "4px 14px 4px 0", color: C.dim,  fontFamily: M, fontSize: 12, whiteSpace: "nowrap" }}>Cruise speed V</td>
                                    <td style={{ padding: "4px 14px 4px 0", color: C.text, fontFamily: M, fontSize: 12 }}>40 kts = 20.58 m/s</td>
                                    <td style={{ padding: "4px 0", color: C.dimmer, fontFamily: M, fontSize: 11 }}>1 kt = 0.5144 m/s</td>
                                </tr>
                                {/* Air density */}
                                <tr>
                                    <td style={{ padding: "4px 14px 4px 0", color: C.dim,  fontFamily: M, fontSize: 12, whiteSpace: "nowrap" }}>Air density ρ</td>
                                    <td style={{ padding: "4px 14px 4px 0", color: C.text, fontFamily: M, fontSize: 12 }}>1.225 kg/m³</td>
                                    <td style={{ padding: "4px 0", color: C.dimmer, fontFamily: M, fontSize: 11 }}>ISA sea-level standard</td>
                                </tr>
                                {/* Dynamic pressure */}
                                <tr style={{ background: "rgba(0,229,255,0.03)" }}>
                                    <td style={{ padding: "4px 14px 4px 0", color: C.dim,  fontFamily: M, fontSize: 12, whiteSpace: "nowrap" }}>Dynamic pressure q</td>
                                    <td style={{ padding: "4px 14px 4px 0", color: C.text, fontFamily: M, fontSize: 12 }}>½ρV² = ½ × 1.225 × 20.58² = 259.7 Pa ≈ 260 Pa</td>
                                    <td style={{ padding: "4px 0", color: C.dimmer, fontFamily: M, fontSize: 11 }}></td>
                                </tr>
                                {/* Wing plan area */}
                                <tr>
                                    <td style={{ padding: "4px 14px 4px 0", color: C.dim,  fontFamily: M, fontSize: 12, whiteSpace: "nowrap" }}>Wing plan area S_ref</td>
                                    <td style={{ padding: "4px 14px 4px 0", color: C.text, fontFamily: M, fontSize: 12 }}>0.0156 m² (both wings)</td>
                                    <td style={{ padding: "4px 0", color: C.dimmer, fontFamily: M, fontSize: 11 }}>Each wing ≈ 120 mm span × 65 mm mean chord = 7 800 mm² per side; total 15 600 mm²; trapezoidal estimate at 24″ scale</td>
                                </tr>
                                {/* Reynolds number */}
                                <tr style={{ background: "rgba(0,229,255,0.03)" }}>
                                    <td style={{ padding: "4px 14px 4px 0", color: C.dim,  fontFamily: M, fontSize: 12, whiteSpace: "nowrap" }}>Reynolds number Re</td>
                                    <td style={{ padding: "4px 14px 4px 0", color: C.text, fontFamily: M, fontSize: 12 }}>ρVc / μ = 1.225 × 20.58 × 0.065 / 1.81×10⁻⁵ ≈ 90 700</td>
                                    <td style={{ padding: "4px 0", color: C.dimmer, fontFamily: M, fontSize: 11 }}>Low-Re regime; viscous effects significant</td>
                                </tr>
                            </tbody>
                        </table>

                        {/* Scale-mismatch reminder */}
                        <div style={{
                            marginTop: 14,
                            padding: "10px 14px",
                            background: "rgba(255,107,53,0.08)",
                            border: `1px solid rgba(255,107,53,0.35)`,
                            borderRadius: 7,
                            fontFamily: M, fontSize: 11.5,
                            color: C.orange,
                        }}>
                            <span style={{ fontFamily: MB }}>Scale note: </span>
                            Nacelles were enlarged 1.25× relative to the canonical 2.197× Thingiverse
                            model to fit 50 mm EDF units. The fuselage and wings remain at the
                            original 2.197× scale. Wing area and chord values above are derived from
                            the 2.197× (24-inch) fuselage/wing dimensions.
                        </div>
                    </Card>

                    {/* ── Baseline geometry ── */}
                    <Card title="Current Geometry — Flat-Plate Wings (Canonical Serenity Shape)" accent={C.yellow}>
                        <table style={{ borderCollapse: "collapse", width: "100%" }}>
                            <tbody>
                                {/* CL at 5 deg */}
                                <tr>
                                    <td style={{ padding: "4px 14px 4px 0", color: C.dim,  fontFamily: M, fontSize: 12, width: "34%" }}>C_L at 5° AoA (flat plate, Re ≈ 91k)</td>
                                    <td style={{ padding: "4px 14px 4px 0", color: C.text, fontFamily: M, fontSize: 12 }}>≈ 0.32</td>
                                    <td style={{ padding: "4px 0", color: C.dimmer, fontFamily: M, fontSize: 11 }}>Falkner-Skan thin-airfoil inviscid: C_L = 2π sin α ≈ 0.55; corrected for low-Re viscous separation → 0.32</td>
                                </tr>
                                {/* Lift formula */}
                                <tr style={{ background: "rgba(255,230,0,0.04)" }}>
                                    <td style={{ padding: "4px 14px 4px 0", color: C.dim,  fontFamily: M, fontSize: 12 }}>Lift L</td>
                                    <td style={{ padding: "4px 14px 4px 0", color: C.yellow, fontFamily: M, fontSize: 12 }}>C_L × q × S = 0.32 × 260 × 0.0156 = 1.30 N</td>
                                    <td style={{ padding: "4px 0", color: C.dimmer, fontFamily: M, fontSize: 11 }}></td>
                                </tr>
                                {/* Wing lift fraction */}
                                <tr>
                                    <td style={{ padding: "4px 14px 4px 0", color: C.dim,  fontFamily: M, fontSize: 12 }}>Wing lift fraction</td>
                                    <td style={{ padding: "4px 14px 4px 0", color: C.yellow, fontFamily: M, fontSize: 12 }}>L / W = 1.30 / 34.8 = 3.7%</td>
                                    <td style={{ padding: "4px 0", color: C.dimmer, fontFamily: M, fontSize: 11 }}>Remaining 96.3% from EDF thrust</td>
                                </tr>
                            </tbody>
                        </table>
                    </Card>

                    {/* ── Airfoil improvement options ── */}
                    <Card title="Recommended Airfoil Improvements — Zero Outer Mold-Line Change" accent={C.teal}>
                        {/* Option 1 */}
                        <div style={{
                            marginBottom: 14,
                            padding: "10px 14px",
                            background: "rgba(0,229,255,0.05)",
                            border: `1px solid ${C.border}`,
                            borderRadius: 7,
                        }}>
                            <div style={{ fontFamily: MB, fontSize: 13, color: C.accent, marginBottom: 6 }}>
                                Option 1 — Add 3° Positive Incidence at Wing Root Attachment
                            </div>
                            <div style={{ fontFamily: M, fontSize: 12, color: C.text, lineHeight: 1.7 }}>
                                Angle the pylon wing-mount block upward 3° (pitch leading edge up).
                                No change to the outer hull. ΔC_L = 2π × (3π/180) ≈ 0.33 at high Re;
                                ~0.25 at Re = 91k. New C_L ≈ 0.57.<br />
                                <span style={{ color: C.teal }}>New L = 0.57 × 260 × 0.0156 = 2.31 N → 6.6% of AUW.</span>
                            </div>
                        </div>

                        {/* Option 2 */}
                        <div style={{
                            marginBottom: 14,
                            padding: "10px 14px",
                            background: "rgba(0,229,255,0.05)",
                            border: `1px solid ${C.border}`,
                            borderRadius: 7,
                        }}>
                            <div style={{ fontFamily: MB, fontSize: 13, color: C.accent, marginBottom: 6 }}>
                                Option 2 — Hollow Interior with Asymmetric PETG Infill (4% Camber Line)
                            </div>
                            <div style={{ fontFamily: M, fontSize: 12, color: C.text, lineHeight: 1.7 }}>
                                Keep the outer skin canonical. Hollow the wing body with infill biased toward
                                the suction surface, shifting the mean camber line to ~4% of chord without
                                any exterior change.<br />
                                NACA 4-series at Re = 91k: C_L ≈ 0.90 at 5° AoA + 3° incidence.<br />
                                <span style={{ color: C.teal }}>New L = 0.90 × 260 × 0.0156 = 3.65 N → 10.5% of AUW.</span>
                            </div>
                        </div>

                        {/* Option 3 */}
                        <div style={{
                            marginBottom: 0,
                            padding: "10px 14px",
                            background: "rgba(74,222,128,0.07)",
                            border: `1px solid rgba(74,222,128,0.35)`,
                            borderRadius: 7,
                        }}>
                            <div style={{ fontFamily: MB, fontSize: 13, color: C.green, marginBottom: 6 }}>
                                Option 3 — Combined (3° Incidence + 4% Camber Infill)
                            </div>
                            <div style={{ fontFamily: M, fontSize: 12, color: C.text, lineHeight: 1.7 }}>
                                C_L ≈ 0.90, L = 3.65 N → 10.5% of AUW. Reduces EDF thrust required for
                                cruise by ~10.5%, improving battery endurance.<br />
                                <span style={{ color: C.green }}>
                                    Estimated cruise endurance improvement: +6–8 min on 6S 10Ah pack
                                    (based on reduced loiter thrust).
                                </span>
                            </div>
                        </div>
                    </Card>

                    {/* ── Summary comparison table ── */}
                    <Card title="Lift Configuration Comparison" accent={C.green}>
                        <table style={{ borderCollapse: "collapse", width: "100%" }}>
                            <thead>
                                <tr>
                                    {["Configuration", "C_L", "Lift (N)", "% AUW", "Endurance Δ"].map((h, hi) => (
                                        <th key={h} style={{
                                            color: C.green, fontFamily: MB, fontSize: 11,
                                            padding: "4px 14px 4px 0", textAlign: hi > 0 ? "right" : "left",
                                            borderBottom: `1px solid ${C.border}`,
                                        }}>{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {/* Each row: [label, CL, lift, pct, delta, highlight] */}
                                {[
                                    ["Flat plate (baseline)", "0.32", "1.30 N", "3.7%",  "—",          false],
                                    ["+ 3° incidence",        "0.57", "2.31 N", "6.6%",  "≈ +3–4 min", false],
                                    ["+ 4% camber",           "0.90", "3.65 N", "10.5%", "≈ +5–7 min", false],
                                    ["Combined",              "0.90", "3.65 N", "10.5%", "+6–8 min",   true ],
                                ].map((row, i) => (
                                    <tr key={i} style={{
                                        background: row[5]
                                            ? "rgba(74,222,128,0.10)"
                                            : i % 2 ? "rgba(74,222,128,0.03)" : "transparent",
                                        border: row[5] ? `1px solid rgba(74,222,128,0.40)` : "none",
                                    }}>
                                        {/* Configuration name */}
                                        <td style={{
                                            padding: "5px 14px 5px 6px",
                                            color: row[5] ? C.green : C.text,
                                            fontFamily: row[5] ? MB : M,
                                            fontSize: 12,
                                        }}>{row[0]}</td>
                                        {/* CL */}
                                        <td style={{ padding: "5px 14px 5px 0", color: row[5] ? C.green : C.text, fontFamily: M, fontSize: 12, textAlign: "right" }}>{row[1]}</td>
                                        {/* Lift */}
                                        <td style={{ padding: "5px 14px 5px 0", color: row[5] ? C.green : C.text, fontFamily: M, fontSize: 12, textAlign: "right" }}>{row[2]}</td>
                                        {/* % AUW */}
                                        <td style={{ padding: "5px 14px 5px 0", color: row[5] ? C.green : C.text, fontFamily: M, fontSize: 12, textAlign: "right" }}>{row[3]}</td>
                                        {/* Endurance Δ */}
                                        <td style={{ padding: "5px 0", color: row[5] ? C.green : C.dimmer, fontFamily: M, fontSize: 12, textAlign: "right" }}>{row[4]}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </Card>

                    {/* ── Outer mold-line caveat ── */}
                    <div style={{
                        padding: "10px 16px",
                        background: "rgba(0,229,255,0.05)",
                        border: `1px solid ${C.border}`,
                        borderRadius: 7,
                        fontFamily: M, fontSize: 11.5,
                        color: C.dimmer,
                        marginBottom: 18,
                    }}>
                        <span style={{ color: C.accent, fontFamily: MB }}>Note: </span>
                        Wing geometry is canonical Serenity shape. Outer mold line is NEVER changed.
                        Only incidence angle (set by pylon mount block geometry at 3°) and internal
                        hollow infill bias are modified.
                    </div>
                </div>
            )}

            {/* ── Wing Nacelle Pylon ───────────────────────────────────────── */}
            {activeTab === "pylon" && (
                <div>
                    {/* ── Section header ── */}
                    <div style={{ marginBottom: 20 }}>
                        <div style={{ fontFamily: MB, fontSize: 18, color: C.orange, letterSpacing: 1 }}>
                            WING NACELLE PYLON — s_wing_nacelle_pylon_revo.scad
                        </div>
                        <div style={{ color: C.dimmer, fontSize: 12, marginTop: 4 }}>
                            Merged pivot + outer housing — single CF-PETG part
                        </div>
                    </div>

                    {/* ── Key parameters table ── */}
                    <Card title="Key Parameters" accent={C.orange}>
                        <table style={{ borderCollapse: "collapse", width: "100%" }}>
                            <thead>
                                <tr>
                                    {["Parameter", "Value", "Description"].map((h, hi) => (
                                        <th key={h} style={{
                                            color: C.orange, fontFamily: MB, fontSize: 11,
                                            padding: "4px 14px 4px 0", textAlign: "left",
                                            borderBottom: `1px solid ${C.border}`,
                                        }}>{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {[
                                    /* [parameter, value, description] */
                                    ["PYLON_SPAN",       "88 mm",            "Wing face to nacelle X-face (verify vs wing STL)"],
                                    ["PYLON_W",          "36 mm",            "Body width (Y, nacelle fore-aft)"],
                                    ["PYLON_H",          "32 mm",            "Body height (Z, centred on PIVOT_Z)"],
                                    ["PYLON_WALL",       "3.0 mm",           "CF-PETG wall (4 perimeter × 0.6 mm)"],
                                    ["SPAR_BORE_D",      "4.0 mm",           "CF spar press-fit bore (fixed in pylon)"],
                                    ["NAC_BOSS_SOCKET",  "Ø16.3 × 5.5 mm",  "Accepts nacelle pivot boss (16 mm OD)"],
                                    ["SECTOR_GEAR_BC_R", "18 mm",            "M2.5 insert bolt circle (4× inserts)"],
                                    ["WING_SLOT_W",      "50 mm",            "Wing mount block width (VERIFY vs STL)"],
                                    ["WING_SLOT_H",      "40 mm",            "Wing mount block height (VERIFY vs STL)"],
                                ].map((row, i) => (
                                    <tr key={i} style={{ background: i % 2 ? "rgba(255,107,53,0.04)" : "transparent" }}>
                                        {/* Parameter name in monospace accent */}
                                        <td style={{ padding: "4px 14px 4px 0", color: C.orange, fontFamily: M, fontSize: 12, whiteSpace: "nowrap" }}>{row[0]}</td>
                                        {/* Value */}
                                        <td style={{ padding: "4px 14px 4px 0", color: C.text, fontFamily: M, fontSize: 12, whiteSpace: "nowrap" }}>{row[1]}</td>
                                        {/* Description */}
                                        <td style={{ padding: "4px 0", color: C.dim, fontFamily: M, fontSize: 11.5 }}>{row[2]}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </Card>

                    {/* ── Nacelle scale mismatch note ── */}
                    <Card title="Nacelle Scale Mismatch Note" accent={C.yellow}>
                        <div style={{ fontFamily: M, fontSize: 12, color: C.text, lineHeight: 1.8, marginBottom: 12 }}>
                            The nacelle was enlarged by <span style={{ color: C.yellow, fontFamily: MB }}>1.25×</span> relative
                            to the fuselage/wing (to accommodate 50 mm EDFs). The original wing mount
                            pocket was designed for the smaller 2.197× nacelle. The pylon bridges this
                            mismatch:
                        </div>
                        <table style={{ borderCollapse: "collapse", width: "100%", marginBottom: 14 }}>
                            <tbody>
                                <tr>
                                    <td style={{ padding: "4px 14px 4px 0", color: C.dim,  fontFamily: M, fontSize: 12, whiteSpace: "nowrap" }}>Nacelle-facing end</td>
                                    <td style={{ padding: "4px 0", color: C.text, fontFamily: M, fontSize: 12 }}>Sized for Rev O 60.5 × 67 mm elliptical nacelle cross-section</td>
                                </tr>
                                <tr style={{ background: "rgba(255,230,0,0.04)" }}>
                                    <td style={{ padding: "4px 14px 4px 0", color: C.dim,  fontFamily: M, fontSize: 12, whiteSpace: "nowrap" }}>Wing-facing end</td>
                                    <td style={{ padding: "4px 0", color: C.text, fontFamily: M, fontSize: 12 }}>Sized for original 2.197× wing pocket geometry</td>
                                </tr>
                            </tbody>
                        </table>
                        {/* Critical measurement warning */}
                        <div style={{
                            padding: "10px 16px",
                            background: "rgba(255,107,53,0.10)",
                            border: `1px solid rgba(255,107,53,0.50)`,
                            borderRadius: 7,
                            fontFamily: M, fontSize: 12,
                            color: C.orange,
                        }}>
                            <span style={{ fontFamily: MB }}>⚠ VERIFY BEFORE PRINTING: </span>
                            WING_SLOT_W and WING_SLOT_H MUST be measured directly from
                            <span style={{ color: C.yellow, fontFamily: MB }}> s_wings_both_shell24.stl </span>
                            before slicing or printing the pylon. Values shown (50 mm × 40 mm) are
                            provisional estimates only. Dimension from the STL pocket geometry,
                            accounting for print clearance (~0.2 mm per face for CF-PETG).
                        </div>
                    </Card>

                    {/* ── Features ── */}
                    <Card title="Pylon Features" accent={C.teal}>
                        <table style={{ borderCollapse: "collapse", width: "100%" }}>
                            <thead>
                                <tr>
                                    {["#", "Feature", "Detail"].map(h => (
                                        <th key={h} style={{
                                            color: C.teal, fontFamily: MB, fontSize: 11,
                                            padding: "4px 14px 4px 0", textAlign: "left",
                                            borderBottom: `1px solid ${C.border}`,
                                        }}>{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {[
                                    /* [number, feature name, detail] */
                                    [
                                        "1",
                                        "Hollow box body — harness channel",
                                        "Entire interior carries ESC power + signal + nav light leads through the pylon span",
                                    ],
                                    [
                                        "2",
                                        "4 mm CF spar press-fit bore",
                                        "Spar fixed to pylon; nacelle MF104ZZ bearings rotate on spar (spar does not rotate)",
                                    ],
                                    [
                                        "3",
                                        "Nacelle boss socket — positive-stop shoulder",
                                        "Accepts Ø16.3 mm boss; shoulder prevents axial pull-out; CLAUDE.md compliant",
                                    ],
                                    [
                                        "4",
                                        "Sector gear mount face",
                                        "4× M2.5 heat-set inserts at R = 18 mm bolt circle; ±10° adjustment arc per insert",
                                    ],
                                    [
                                        "5",
                                        "Wing root attach block",
                                        "4× M3 SHCS + positive-stop shoulder into wing pocket; rigidly fixed — no fold mechanism",
                                    ],
                                    [
                                        "6",
                                        "Nav light wiring route",
                                        "Harness exits nacelle through X-face port: 14 × 8 mm slot at Z = 86 mm, adjacent to pivot boss",
                                    ],
                                ].map((row, i) => (
                                    <tr key={i} style={{ background: i % 2 ? "rgba(45,212,191,0.04)" : "transparent" }}>
                                        <td style={{ padding: "5px 14px 5px 0", color: C.teal, fontFamily: MB, fontSize: 13, textAlign: "center", width: 30 }}>{row[0]}</td>
                                        <td style={{ padding: "5px 14px 5px 0", color: C.text, fontFamily: MB, fontSize: 12 }}>{row[1]}</td>
                                        <td style={{ padding: "5px 0", color: C.dim, fontFamily: M, fontSize: 11.5 }}>{row[2]}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </Card>

                    {/* ── Print specification ── */}
                    <Card title="Print Specification" accent={C.purple}>
                        <table style={{ borderCollapse: "collapse", width: "100%" }}>
                            <tbody>
                                <tr>
                                    <td style={{ padding: "4px 14px 4px 0", color: C.dim,  fontFamily: M, fontSize: 12, whiteSpace: "nowrap" }}>Material</td>
                                    <td style={{ padding: "4px 0", color: C.text, fontFamily: M, fontSize: 12 }}>CF-PETG · 0.15 mm layer height · 4 perimeter walls · 40% gyroid infill</td>
                                </tr>
                                <tr style={{ background: "rgba(192,132,252,0.04)" }}>
                                    <td style={{ padding: "4px 14px 4px 0", color: C.dim,  fontFamily: M, fontSize: 12, whiteSpace: "nowrap" }}>Orientation</td>
                                    <td style={{ padding: "4px 0", color: C.text, fontFamily: M, fontSize: 12 }}>Long axis (X) horizontal on build plate; pylon body flat-face down; wing block flange up</td>
                                </tr>
                                <tr>
                                    <td style={{ padding: "4px 14px 4px 0", color: C.dim,  fontFamily: M, fontSize: 12, whiteSpace: "nowrap" }}>Supports</td>
                                    <td style={{ padding: "4px 0", color: C.text, fontFamily: M, fontSize: 12 }}>Required under wing attachment block shoulder flange overhang only</td>
                                </tr>
                                <tr style={{ background: "rgba(192,132,252,0.04)" }}>
                                    <td style={{ padding: "4px 14px 4px 0", color: C.dim,  fontFamily: M, fontSize: 12, whiteSpace: "nowrap" }}>Quantity</td>
                                    <td style={{ padding: "4px 0", color: C.text, fontFamily: M, fontSize: 12 }}>2× per aircraft (port and starboard); mirror in slicer — do NOT print two of the same hand</td>
                                </tr>
                            </tbody>
                        </table>
                    </Card>
                </div>
            )}

            {/* Footer */}
            <div style={{ marginTop: 32, borderTop: `1px solid ${C.border}`, paddingTop: 12,
                          color: C.dimmer, fontSize: 10.5, fontFamily: M }}>
                Serenity-Class Tiltrotor UAV Rev O · Steve Griffing PE(CSE) CISSP-ISSEP CPP ·
                CC BY 4.0 creativecommons.org/licenses/by/4.0 · 2026-05-24 ·
                Hull geometry CC BY 4.0 Peter Farell (printables.com/model/548545) ·
                Variable-area EDF nozzles CC BY 4.0 BamJr (thingiverse.com/thing:2991269) ·
                Visual inspiration Joss Whedon / Mutant Enemy / Universal © all rights reserved
            </div>
        </div>
    );
}
