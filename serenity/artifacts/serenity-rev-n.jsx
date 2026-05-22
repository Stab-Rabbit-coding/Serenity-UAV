import { useState } from "react";

// ── OpenDyslexic font loader ─────────────────────────────────
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

// ── Tokens ───────────────────────────────────────────────────
const C = {
  bg: "#060810", border: "rgba(0,229,255,0.13)", accent: "#00e5ff",
  orange: "#ff6b35", yellow: "#ffe600", purple: "#c084fc", green: "#4ade80",
  pink: "#f472b6", teal: "#2dd4bf", red: "#f87171", lime: "#a3e635",
  gold: "#fbbf24", text: "rgba(255,255,255,0.95)", dim: "rgba(255,255,255,0.82)",
  dimmer: "rgba(255,255,255,0.70)",
};
const M = "'OpenDyslexic Mono','OpenDyslexicMono','Courier New',monospace";
const MB = "'OpenDyslexic Bold','OpenDyslexic',sans-serif";

// ── Rev N 24-inch dimensions ──────────────────────────────────
const HULL_L = 609.6;   // mm, 24"
const SCALE  = 609.6 / 457.2;  // 1.3333 relative to 18"

// Hull profile [station_mm, half_width_mm] at 24" scale
// (18" profile × SCALE)
const HULL_PTS = [
  [0,0],[13.3,17.3],[37.3,29.3],[66.7,50.7],[97.3,60.0],[146.7,61.3],
  [200.0,69.3],[233.3,69.3],[276.0,66.7],[316.0,60.0],[366.7,48.0],
  [421.3,29.3],[433.3,26.7],[462.7,40.0],[508.0,48.0],[549.3,46.7],
  [609.6,37.3],
];
// Convert to SVG coordinates: X = station, Y = centred at 0 (up = -Y)
// Scale for display: 1px per mm * displayScale
const DS = 0.72; // display scale: mm → px

function hullPath(pts, flip = false) {
  const topPts = pts.map(([x, hw]) => [x * DS, -hw * DS]);
  const botPts = pts.map(([x, hw]) => [x * DS, hw * DS]);
  const top = topPts.map(([x, y], i) => `${i === 0 ? "M" : "L"}${x},${y}`).join(" ");
  const bot = [...botPts].reverse().map(([x, y]) => `L${x},${y}`).join(" ");
  return `${top} ${bot} Z`;
}

// Panel boundaries [start_mm, end_mm]
const PANELS = [
  { id: "A", label: "A Nose",    s: 0,     e: 91,   fill: "rgba(0,229,255,0.07)" },
  { id: "B", label: "B Fwd",    s: 91,    e: 165,  fill: "rgba(255,107,53,0.07)" },
  { id: "C", label: "C Cargo",  s: 165,   e: 251,  fill: "rgba(196,132,252,0.07)" },
  { id: "D", label: "D Neck",   s: 251,   e: 320,  fill: "rgba(255,230,0,0.09)" },
  { id: "E", label: "E Svc",    s: 320,   e: 388,  fill: "rgba(45,212,191,0.07)" },
  { id: "F", label: "F Bell",   s: 388,   e: 609.6,fill: "rgba(248,113,113,0.08)" },
];

// Key stations
const SCOOP_STA   = 310;  // neck scoop centre station (mm)
const EDF_FACE    = 430;  // 120mm EDF fan face station (mm)
const SIK_STA     = 260;  // SiK antenna station (mm, relocated from 310→260)
const WING_STA    = 200;  // wing/nacelle pivot approximate station

// Interpolate hull half-width at a given station
function hullHW(sta) {
  for (let i = 0; i < HULL_PTS.length - 1; i++) {
    const [x0, hw0] = HULL_PTS[i];
    const [x1, hw1] = HULL_PTS[i + 1];
    if (sta >= x0 && sta <= x1) {
      const t = (sta - x0) / (x1 - x0);
      return hw0 + t * (hw1 - hw0);
    }
  }
  return 0;
}

// ── Colour legend items ───────────────────────────────────────
const LEGEND = [
  { col: C.accent,  label: "Hull shell (PETG)" },
  { col: C.yellow,  label: "Intake scoops (neck, ~310mm)" },
  { col: C.orange,  label: "CF-PETG intake frame" },
  { col: C.teal,    label: "Plenum manifold (PETG, inside hull)" },
  { col: C.red,     label: "120mm EDF (station ~430mm, Panel F)" },
  { col: C.purple,  label: "Nacelle EDFs (2× port, 2× stbd)" },
  { col: C.green,   label: "SiK antenna (relocated, ~260mm)" },
  { col: C.pink,    label: "Rear iris nozzle" },
];

// ── Print schedule ────────────────────────────────────────────
const PRINT_SCHEDULE = [
  { stl: "s_head_shell24",           mat: "PETG",     qty: 1, g: 95,  note: "Nose / cockpit" },
  { stl: "s_middle_canonical_shell24", mat: "PETG",   qty: 1, g: 135, note: "Mid — canonical belly (no scoop)" },
  { stl: "s_cargo_sect_shell24",     mat: "PETG",     qty: 1, g: 180, note: "Cargo bay" },
  { stl: "s_rear_neck_intake_shell24",mat:"PETG",     qty: 1, g: 225, note: "Rear — 4 scoop windows at neck" },
  { stl: "s_wings_both_shell24",     mat: "PETG",     qty: 1, g: 110, note: "Wing pair" },
  { stl: "s_neck_intake_frame",      mat: "CF-PETG",  qty: 1, g: 85,  note: "Structural intake ring — bonds to 4 scoops" },
  { stl: "s_aft_edf_plenum",         mat: "PETG",     qty: 1, g: 75,  note: "4→1 plenum manifold" },
  { stl: "s_eng_left/right_stator_shell24", mat:"CF-PETG", qty: 2, g: 130, note: "Nacelle shells w/ integrated stators" },
  { stl: "nacelle_nozzle_petal",     mat: "PETG",     qty: 16, g: 2,  note: "Nacelle iris petals (×8 per nacelle)" },
  { stl: "nacelle_nozzle_ring",      mat: "CF-PETG",  qty: 2, g: 18,  note: "Nacelle iris base rings" },
  { stl: "rear_nozzle_petal",        mat: "PETG",     qty: 8, g: 4,   note: "Rear nozzle iris petals" },
  { stl: "rear_nozzle_frame",        mat: "CF-PETG",  qty: 1, g: 55,  note: "Rear nozzle frame (8 fixed ribs)" },
  { stl: "s_pivot_arm_a_scaled24",   mat: "CF-PETG",  qty: 2, g: 20,  note: "Tilt servo pivot arms" },
  { stl: "s_legs_scaled24",          mat: "CF-PETG",  qty: 1, g: 60,  note: "Landing legs" },
  { stl: "s_feet_x_4_scaled24",      mat: "TPU 95A",  qty: 1, g: 80,  note: "Landing feet (shock absorbing)" },
];

// ── Intake aerodynamics data ──────────────────────────────────
const FAN_ANNULAR_MM2  = Math.round(Math.PI / 4 * (120**2 - 28**2));
const SCOOP_EACH_MM2   = 65 * 60;
const SCOOP_TOTAL_MM2  = 4 * SCOOP_EACH_MM2;
const CAPTURE_RATIO    = (SCOOP_TOTAL_MM2 / FAN_ANNULAR_MM2).toFixed(2);

// ── SVG side-profile diagram component ───────────────────────
function SideProfile() {
  const CY = 80; // centreline Y in SVG
  const W  = HULL_L * DS + 20;
  const H  = 180;

  const hullTopPts = HULL_PTS.map(([x, hw]) => [x * DS + 10, CY - hw * DS]);
  const hullBotPts = HULL_PTS.map(([x, hw]) => [x * DS + 10, CY + hw * DS]);

  const topPath = hullTopPts.map(([x, y], i) => `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`).join(" ");
  const botPath = [...hullBotPts].reverse().map(([x, y]) => `L${x.toFixed(1)},${y.toFixed(1)}`).join(" ");
  const fullHull = `${topPath} ${botPath} Z`;

  const scoopX  = SCOOP_STA * DS + 10;
  const edfX    = EDF_FACE * DS + 10;
  const sikX    = SIK_STA * DS + 10;
  const scoopHW = hullHW(SCOOP_STA) * DS;
  const scoopW  = 38 * DS; // axial width of scoop zone

  // Nacelle pods (simplified ellipses at wing station)
  const wingX = WING_STA * DS + 10;

  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" style={{ maxWidth: 900, display: "block", margin: "0 auto" }}>
      {/* Panel fills */}
      {PANELS.map(p => {
        const px = p.s * DS + 10;
        const pw = (p.e - p.s) * DS;
        return <rect key={p.id} x={px} y={CY - 75} width={pw} height={150} fill={p.fill} />;
      })}

      {/* Hull outline */}
      <path d={fullHull} fill="rgba(0,229,255,0.08)" stroke={C.accent} strokeWidth="1.5" />

      {/* Scoop zone highlight (both top and bottom) */}
      <rect x={scoopX - scoopW / 2} y={CY - scoopHW - 2} width={scoopW} height={12}
        fill={C.yellow} opacity={0.7} rx={2} />
      <rect x={scoopX - scoopW / 2} y={CY + scoopHW - 10} width={scoopW} height={12}
        fill={C.yellow} opacity={0.7} rx={2} />
      {/* Port / stbd scoops (shown as side rectangles — viewed from port) */}
      <rect x={scoopX - scoopW / 2} y={CY - 8} width={scoopW} height={16}
        fill={C.orange} opacity={0.5} rx={2} />

      {/* Intake frame collar */}
      <rect x={scoopX - 19 * DS} y={CY - scoopHW - 14 * DS}
        width={38 * DS} height={(scoopHW + 14 * DS) * 2}
        fill="none" stroke={C.orange} strokeWidth="2" strokeDasharray="4,2" rx={2} />

      {/* Plenum manifold (inside hull, shown as dashed region) */}
      <rect x={scoopX} y={CY - 30} width={(EDF_FACE - SCOOP_STA) * DS} height={60}
        fill={C.teal} opacity={0.12} stroke={C.teal} strokeWidth="1.5" strokeDasharray="5,3" rx={4} />
      <line x1={scoopX} y1={CY} x2={edfX} y2={CY} stroke={C.teal} strokeWidth="2" strokeDasharray="8,3" />
      {/* Arrow toward EDF */}
      <polygon points={`${edfX},${CY} ${edfX - 8},${CY - 5} ${edfX - 8},${CY + 5}`} fill={C.teal} />

      {/* 120mm EDF disk at station ~430mm */}
      <rect x={edfX - 2} y={CY - 60 * DS} width={8} height={120 * DS}
        fill={C.red} opacity={0.8} rx={1} />
      <line x1={edfX + 6} y1={CY} x2={HULL_L * DS + 10} y2={CY} stroke={C.red} strokeWidth="2" strokeDasharray="6,3" />
      <polygon points={`${HULL_L * DS + 9},${CY} ${HULL_L * DS - 6},${CY - 4} ${HULL_L * DS - 6},${CY + 4}`} fill={C.red} />

      {/* Nacelle pods */}
      {[-38, 38].map((offset, i) => (
        <ellipse key={i} cx={wingX} cy={CY + offset} rx={74 * DS} ry={7 * DS}
          fill="none" stroke={C.purple} strokeWidth="1.5" />
      ))}

      {/* Rear nozzle */}
      <polygon points={`${(HULL_L + 10) * DS},${CY - 20} ${(HULL_L + 10) * DS},${CY + 20} ${(HULL_L + 28) * DS},${CY}`}
        fill={C.pink} opacity={0.6} />

      {/* SiK antenna */}
      <line x1={sikX} y1={CY + scoopHW - 2} x2={sikX} y2={CY + scoopHW + 18}
        stroke={C.green} strokeWidth="2" />
      <circle cx={sikX} cy={CY + scoopHW + 20} r={4} fill={C.green} />

      {/* Panel labels */}
      {PANELS.map(p => {
        const lx = ((p.s + p.e) / 2) * DS + 10;
        return (
          <text key={p.id} x={lx} y={12} textAnchor="middle"
            fill={C.dimmer} fontSize={8} fontFamily={M}>{p.label}</text>
        );
      })}

      {/* Station labels */}
      {[
        [SCOOP_STA, C.yellow,  "⬆ Scoops\n~310mm"],
        [EDF_FACE,  C.red,     "EDF\n~430mm"],
        [SIK_STA,  C.green,   "SiK\n~260mm"],
      ].map(([sta, col, rawLabel]) => {
        const lines = rawLabel.split("\n");
        const sx = sta * DS + 10;
        return (
          <g key={sta}>
            <line x1={sx} y1={CY + 2} x2={sx} y2={H - 25}
              stroke={col} strokeWidth="1" strokeDasharray="3,2" opacity={0.5} />
            {lines.map((ln, i) => (
              <text key={i} x={sx} y={H - 22 + i * 10} textAnchor="middle"
                fill={col} fontSize={8} fontFamily={M}>{ln}</text>
            ))}
          </g>
        );
      })}

      {/* Centreline */}
      <line x1={10} y1={CY} x2={W - 5} y2={CY}
        stroke="rgba(255,255,255,0.12)" strokeWidth="1" strokeDasharray="8,4" />
    </svg>
  );
}

// ── Cross-section diagram at neck station ─────────────────────
function NeckCrossSection() {
  const CX = 120, CY = 120;
  const HW = 63 * 0.9, HH = 50 * 0.9; // hull half-extents in px (scaled)
  const SCOOP_W_PX = 65 * 0.9 / 2;
  const SCOOP_H_PX = 14 * 0.9;         // radial depth of scoop opening
  const DUCT_L_PX  = 22 * 0.9;         // internal duct arm length
  const EDF_R      = 60 * 0.9 / 2;     // 60mm radius in px (half of 120mm)
  const HUB_R      = 14 * 0.9 / 2;     // hub radius

  // Hull ellipse
  const ellCmd = `M ${CX + HW},${CY} A ${HW},${HH} 0 1,1 ${CX - HW - 0.01},${CY} A ${HW},${HH} 0 1,1 ${CX + HW},${CY}`;

  const scoops = [
    { angle: 0,   label: "↑ Dorsal" },
    { angle: 90,  label: "→ Stbd"   },
    { angle: 180, label: "↓ Ventral"},
    { angle: 270, label: "← Port"   },
  ];

  return (
    <svg viewBox="0 0 240 240" width="100%" style={{ maxWidth: 340, display: "block", margin: "0 auto" }}>
      {/* Hull ellipse */}
      <path d={ellCmd} fill="rgba(0,229,255,0.06)" stroke={C.accent} strokeWidth="2" />

      {/* CF-PETG intake frame ring */}
      <ellipse cx={CX} cy={CY} rx={HW + SCOOP_H_PX} ry={HH + SCOOP_H_PX}
        fill="none" stroke={C.orange} strokeWidth="1.5" strokeDasharray="4,2" />

      {/* Scoop cutouts and duct arms at 4 positions */}
      {scoops.map(({ angle, label }) => {
        const rad = (angle * Math.PI) / 180;
        // Point on hull ellipse at this angle (parametric ellipse)
        const ex = CX + HW * Math.cos(rad);
        const ey = CY - HH * Math.sin(rad);
        // Direction outward from centre
        const dx = Math.cos(rad), dy = -Math.sin(rad);
        // Scoop opening (yellow rectangle on hull surface)
        const nx = -dy, ny = -(-dx); // normal to radial direction = tangent
        const hw2 = SCOOP_W_PX;
        return (
          <g key={angle}>
            {/* Scoop window on hull */}
            <line x1={ex + nx * hw2} y1={ey + ny * hw2}
              x2={ex - nx * hw2} y2={ey - ny * hw2}
              stroke={C.yellow} strokeWidth={4} />
            {/* Frame outer wall */}
            <line x1={ex + dx * SCOOP_H_PX + nx * hw2} y1={ey + dy * SCOOP_H_PX + ny * hw2}
              x2={ex + dx * SCOOP_H_PX - nx * hw2} y2={ey + dy * SCOOP_H_PX - ny * hw2}
              stroke={C.orange} strokeWidth="2" />
            {/* Duct arm sides */}
            <line x1={ex + nx * hw2} y1={ey + ny * hw2}
              x2={ex - dx * DUCT_L_PX + nx * hw2} y2={ey - dy * DUCT_L_PX + ny * hw2}
              stroke={C.teal} strokeWidth="1.5" />
            <line x1={ex - nx * hw2} y1={ey - ny * hw2}
              x2={ex - dx * DUCT_L_PX - nx * hw2} y2={ey - dy * DUCT_L_PX - ny * hw2}
              stroke={C.teal} strokeWidth="1.5" />
            {/* Air flow arrow */}
            <line x1={ex + dx * SCOOP_H_PX * 0.5} y1={ey + dy * SCOOP_H_PX * 0.5}
              x2={CX + dx * (EDF_R + 6)} y2={CY - dy * (EDF_R + 6)}
              stroke={C.teal} strokeWidth="1" strokeDasharray="4,3" opacity={0.6} />
            {/* Label */}
            <text x={ex + dx * (SCOOP_H_PX + 12)} y={ey + dy * (SCOOP_H_PX + 12) + 3}
              textAnchor="middle" fill={C.orange} fontSize={7} fontFamily={M}>{label}</text>
          </g>
        );
      })}

      {/* EDF annular fan face */}
      <circle cx={CX} cy={CY} r={EDF_R} fill="rgba(248,113,113,0.12)" stroke={C.red} strokeWidth="2" />
      <circle cx={CX} cy={CY} r={HUB_R} fill={C.red} opacity={0.5} />
      <text x={CX} y={CY + 3} textAnchor="middle" fill={C.red} fontSize={7} fontFamily={M}>120mm EDF</text>

      {/* Centreline mark */}
      <circle cx={CX} cy={CY} r={2} fill={C.dim} opacity={0.4} />

      {/* Title */}
      <text x={CX} y={228} textAnchor="middle" fill={C.dim} fontSize={8} fontFamily={M}>
        Cross-section at neck station ~310mm (aft view)
      </text>
    </svg>
  );
}

// ── Airflow path diagram ──────────────────────────────────────
function AirflowDiagram() {
  const nodes = [
    { x: 60,  y: 80,  w: 90, h: 36, col: C.yellow, label: "4× Radial\nScoops", sub: "65×60mm each\n≈310mm station" },
    { x: 210, y: 80,  w: 90, h: 36, col: C.orange,  label: "CF-PETG\nIntake Frame", sub: "14mm radial depth\n38mm axial, 3mm wall" },
    { x: 360, y: 80,  w: 90, h: 36, col: C.teal,    label: "PETG\nPlenum", sub: "4-to-1 cross\n80mm transition" },
    { x: 510, y: 80,  w: 90, h: 36, col: C.red,     label: "120mm\nEDF", sub: "6S, 3500g thrust\n≈430mm station" },
    { x: 660, y: 80,  w: 90, h: 36, col: C.pink,    label: "Rear Iris\nNozzle", sub: "8 petals, SG90 servo\nLED backlit" },
  ];
  const W = 780, H = 160;

  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" style={{ maxWidth: 820, display: "block", margin: "0 auto" }}>
      {nodes.map((n, i) => {
        const cx = n.x + n.w / 2;
        const cy = n.y + n.h / 2;
        const lines = n.label.split("\n");
        const subLines = n.sub.split("\n");
        return (
          <g key={i}>
            <rect x={n.x} y={n.y} width={n.w} height={n.h}
              fill={`${n.col}22`} stroke={n.col} strokeWidth="1.5" rx={6} />
            {lines.map((ln, li) => (
              <text key={li} x={cx} y={cy - (lines.length - 1) * 5 + li * 11}
                textAnchor="middle" fill={n.col} fontSize={9} fontFamily={MB}>{ln}</text>
            ))}
            {subLines.map((sl, si) => (
              <text key={si} x={cx} y={n.y + n.h + 14 + si * 11}
                textAnchor="middle" fill={C.dimmer} fontSize={7} fontFamily={M}>{sl}</text>
            ))}
            {i < nodes.length - 1 && (
              <g>
                <line x1={n.x + n.w} y1={cy} x2={nodes[i + 1].x} y2={cy}
                  stroke="rgba(255,255,255,0.3)" strokeWidth="2" />
                <polygon points={`${nodes[i + 1].x},${cy} ${nodes[i + 1].x - 8},${cy - 4} ${nodes[i + 1].x - 8},${cy + 4}`}
                  fill="rgba(255,255,255,0.3)" />
              </g>
            )}
          </g>
        );
      })}
      {/* Capture area note */}
      <text x={105} y={155} textAnchor="middle" fill={C.yellow} fontSize={7.5} fontFamily={M}>
        {`Total: ${SCOOP_TOTAL_MM2} mm² (ratio ${CAPTURE_RATIO}× fan area)`}
      </text>
      <text x={555} y={155} textAnchor="middle" fill={C.red} fontSize={7.5} fontFamily={M}>
        {`Fan annular: ${FAN_ANNULAR_MM2} mm²`}
      </text>
    </svg>
  );
}

// ── Print schedule table ──────────────────────────────────────
function PrintSchedule() {
  const totalG = PRINT_SCHEDULE.reduce((s, r) => s + r.g * r.qty, 0);
  const matColors = { "PETG": C.accent, "CF-PETG": C.orange, "TPU 95A": C.purple };
  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ borderCollapse: "collapse", width: "100%", fontSize: 11 }}>
        <thead>
          <tr>
            {["STL / Part", "Material", "Qty", "Est. g ea.", "Notes"].map(h => (
              <th key={h} style={{ padding: "6px 10px", background: "#13192b", color: C.accent,
                borderBottom: `1px solid ${C.border}`, textAlign: "left", whiteSpace: "nowrap" }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {PRINT_SCHEDULE.map((r, i) => {
            const matCol = matColors[r.mat] || C.dim;
            const isNew  = r.stl.includes("canonical") || r.stl.includes("neck_intake") || r.stl.includes("plenum");
            return (
              <tr key={i} style={{ background: i % 2 === 0 ? "#0d1320" : "transparent" }}>
                <td style={{ padding: "5px 10px", color: isNew ? C.gold : C.dim, fontFamily: M,
                  borderBottom: `1px solid ${C.border}` }}>
                  {r.stl}{isNew ? " ✦" : ""}
                </td>
                <td style={{ padding: "5px 10px", color: matCol, borderBottom: `1px solid ${C.border}` }}>{r.mat}</td>
                <td style={{ padding: "5px 10px", color: C.dim, borderBottom: `1px solid ${C.border}`, textAlign: "center" }}>{r.qty}</td>
                <td style={{ padding: "5px 10px", color: C.dim, borderBottom: `1px solid ${C.border}`, textAlign: "center" }}>{r.g}</td>
                <td style={{ padding: "5px 10px", color: C.dimmer, fontSize: 10, borderBottom: `1px solid ${C.border}` }}>{r.note}</td>
              </tr>
            );
          })}
          <tr style={{ background: "#13192b" }}>
            <td colSpan={2} style={{ padding: "6px 10px", color: C.accent, fontFamily: MB,
              borderTop: `1px solid ${C.accent}` }}>TOTAL (all parts)</td>
            <td colSpan={3} style={{ padding: "6px 10px", color: C.accent, fontFamily: MB,
              borderTop: `1px solid ${C.accent}` }}>{totalG} g (excl. electronics)</td>
          </tr>
        </tbody>
      </table>
      <p style={{ fontSize: 10, color: C.dimmer, marginTop: 6 }}>
        ✦ New parts for Rev N 4-radial-intake design. Generate STLs from SCAD via OpenSCAD.
      </p>
    </div>
  );
}

// ── Specs table ───────────────────────────────────────────────
function SpecsTable() {
  const rows = [
    ["Hull length",          "609.6 mm (24.00\")", C.dim],
    ["Scale factor",         "2.9294 × original model", C.dim],
    ["Wall thickness",       "2.5 mm PETG / 3.0 mm CF-PETG", C.dim],
    ["Rear EDF intake",      "4× radial scoops, 90° spacing — REPLACED belly scoop", C.gold],
    ["Scoop station",        "~310 mm from nose (hull neck, Panel D)", C.yellow],
    ["Scoop dimensions",     "65 mm wide × 60 mm axial × 4 scoops", C.yellow],
    ["Total capture area",   `${SCOOP_TOTAL_MM2} mm² (${CAPTURE_RATIO}× fan annular area)`, C.teal],
    ["Fan annular area",     `${FAN_ANNULAR_MM2} mm² (120mm EDF, 28mm hub)`, C.dim],
    ["EDF fan face station", "~430 mm from nose (Panel F engine bell)", C.red],
    ["SiK antenna station",  "~260 mm (relocated forward — was 310mm, conflicts with intake)", C.green],
    ["Nacelle propulsion",   "2× (2× 50mm EDF @ 6S, tandem) — counter-rotating pair", C.purple],
    ["Total thrust",         "~5,322 g (1,822 g nacelles + 3,500 g rear EDF)", C.dim],
    ["Hover T/W",            "~1.50 at 6S 4000mAh (~3,550 g AUW)", C.dim],
    ["Avionics",             "8× PocketBeagle 2 Industrial AM6254 + Cape-A/B", C.dim],
  ];
  return (
    <table style={{ borderCollapse: "collapse", width: "100%", fontSize: 11 }}>
      <tbody>
        {rows.map(([k, v, col], i) => (
          <tr key={i} style={{ background: i % 2 === 0 ? "#0d1320" : "transparent" }}>
            <td style={{ padding: "5px 10px", color: C.dimmer, borderBottom: `1px solid ${C.border}`,
              whiteSpace: "nowrap", fontFamily: M }}>{k}</td>
            <td style={{ padding: "5px 10px", color: col, borderBottom: `1px solid ${C.border}` }}>{v}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// ── Tab views ─────────────────────────────────────────────────
const TABS = [
  { id: "profile",    label: "Side Profile" },
  { id: "xsection",  label: "Neck Cross-Section" },
  { id: "airflow",   label: "Air Path" },
  { id: "prints",    label: "Print Schedule" },
  { id: "specs",     label: "Specs" },
];

// ── Root component ────────────────────────────────────────────
export default function SerenityRevN() {
  _ODFontLoader();
  const [tab, setTab] = useState("profile");

  const card = {
    background: "#0d1320", border: `1px solid ${C.border}`, borderRadius: 12,
    padding: "18px 20px", marginBottom: 16,
  };

  return (
    <div style={{ background: C.bg, minHeight: "100vh", color: C.text, padding: "20px 16px", boxSizing: "border-box" }}>
      {/* Header */}
      <div style={card}>
        <h1 style={{ margin: 0, color: C.accent, fontSize: 20, fontFamily: MB }}>
          Serenity-Class UAV — Rev N (24-inch)
        </h1>
        <p style={{ margin: "6px 0 0", color: C.dimmer, fontSize: 12 }}>
          4-radial-intake 120mm EDF fuselage propulsion • Belly restored to canonical geometry •
          CF-PETG structural intake frame + PETG plenum manifold • SiK antenna relocated to station ~260mm
        </p>
      </div>

      {/* Colour legend */}
      <div style={{ ...card, display: "flex", flexWrap: "wrap", gap: 12 }}>
        {LEGEND.map(({ col, label }) => (
          <div key={label} style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <div style={{ width: 12, height: 12, borderRadius: 3, background: col, flexShrink: 0 }} />
            <span style={{ fontSize: 10, color: C.dimmer, fontFamily: M }}>{label}</span>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", gap: 8, marginBottom: 14, flexWrap: "wrap" }}>
        {TABS.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)} style={{
            padding: "6px 14px", borderRadius: 20, border: `1px solid ${tab === t.id ? C.accent : C.border}`,
            background: tab === t.id ? `${C.accent}18` : "transparent",
            color: tab === t.id ? C.accent : C.dimmer,
            cursor: "pointer", fontSize: 11, fontFamily: M,
          }}>{t.label}</button>
        ))}
      </div>

      {/* Tab content */}
      <div style={card}>
        {tab === "profile" && (
          <>
            <h3 style={{ margin: "0 0 12px", color: C.accent, fontSize: 13 }}>Side Profile — Rev N 24-inch hull</h3>
            <SideProfile />
            <p style={{ fontSize: 10, color: C.dimmer, margin: "10px 0 0" }}>
              Yellow bands = 4 radial scoop windows at station ~310mm. Orange dashes = CF-PETG intake frame collar.
              Teal dashes = internal plenum manifold. Red bar = 120mm EDF fan face (~430mm). Green dot = SiK antenna (~260mm).
            </p>
          </>
        )}
        {tab === "xsection" && (
          <>
            <h3 style={{ margin: "0 0 12px", color: C.accent, fontSize: 13 }}>Neck Cross-Section — station ~310mm (aft-looking-forward)</h3>
            <NeckCrossSection />
            <p style={{ fontSize: 10, color: C.dimmer, margin: "10px 0 0" }}>
              Hull ellipse (≈63mm half-width, ≈50mm half-height). Yellow = scoop windows.
              Orange = CF-PETG frame collar. Teal = duct arms routing air inward. Red circle = 120mm EDF fan annulus at this cross-section level.
            </p>
          </>
        )}
        {tab === "airflow" && (
          <>
            <h3 style={{ margin: "0 0 12px", color: C.accent, fontSize: 13 }}>Air Path — Scoops → Frame → Plenum → EDF → Nozzle</h3>
            <AirflowDiagram />
            <div style={{ marginTop: 16, fontSize: 11, color: C.dim, lineHeight: 1.7 }}>
              <p style={{ margin: "0 0 6px" }}>
                <span style={{ color: C.yellow }}>■ 4 scoops</span> capture 15,600 mm² total —
                <span style={{ color: C.teal }}> 1.46× the fan annular area</span> (min 1.3× required for velocity matching).
                Symmetric 90° spacing gives balanced inflow and cancels yaw moments from asymmetric airspeed.
              </p>
              <p style={{ margin: 0 }}>
                <span style={{ color: C.orange }}>CF-PETG frame</span> restores torsional stiffness at the neck
                (lost by cutting 4 hull openings). 3mm walls, 38mm axial extent, registration tongues bonded with West System epoxy.
                <span style={{ color: C.teal }}> PETG plenum</span> tapers 4× rectangular arms (65×60mm) to 120mm circular
                EDF outlet over 80mm transition — cross-shaped layout minimises length and flow path losses.
              </p>
            </div>
          </>
        )}
        {tab === "prints" && (
          <>
            <h3 style={{ margin: "0 0 12px", color: C.accent, fontSize: 13 }}>Print Schedule — Rev N (all hull sections + intake parts)</h3>
            <PrintSchedule />
          </>
        )}
        {tab === "specs" && (
          <>
            <h3 style={{ margin: "0 0 12px", color: C.accent, fontSize: 13 }}>Rev N Key Specifications</h3>
            <SpecsTable />
          </>
        )}
      </div>

      {/* Footer */}
      <div style={{ textAlign: "center", fontSize: 10, color: C.dimmer, marginTop: 8 }}>
        Serenity Rev N — 24-inch Firefly-class tiltrotor UAV — Steve Griffing PE(CSE) CISSP-ISSEP CPP — CC BY 4.0 — 2026 |
        Hull geometry © misubisu / Peter Farell (CC BY 4.0) | Not an officially licensed Firefly/Serenity product.
      </div>
    </div>
  );
}
