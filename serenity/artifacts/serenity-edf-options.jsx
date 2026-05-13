import { useState } from "react";

// ── OpenDyslexic font loader ───────────────────────────────────
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

// ── Tokens ─────────────────────────────────────────────────────
const C = {
  bg: "#060810", border: "rgba(0,229,255,0.11)", accent: "#00e5ff",
  orange: "#ff6b35", yellow: "#ffe600", purple: "#c084fc", green: "#4ade80",
  pink: "#f472b6", teal: "#2dd4bf", red: "#f87171", lime: "#a3e635",
  gold: "#fbbf24", dim: "rgba(255,255,255,0.92)", dimmer: "rgba(255,255,255,0.82)",
  text: "rgba(255,255,255,0.95)",
};
const M  = "'OpenDyslexic Mono','OpenDyslexicMono','Courier New',monospace";
const MB = "'OpenDyslexic Bold','OpenDyslexic',sans-serif";

// ── Shared primitives ──────────────────────────────────────────
const SH = ({ t, c = C.accent, mt = 22 }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14, marginTop: mt }}>
    <div style={{ width: 3, height: 17, background: c }} />
    <span style={{ color: c, fontFamily: M, fontSize: 13, letterSpacing: "0.13em", textTransform: "uppercase", fontWeight: "normal" }}>{t}</span>
  </div>
);
const KV = ({ k, v, vc = C.text, u = "" }) => (
  <div style={{ display: "flex", justifyContent: "space-between", padding: "5px 0", borderBottom: "1px solid rgba(0,229,255,0.07)", alignItems: "baseline" }}>
    <span style={{ color: C.dim, fontFamily: M, fontSize: 11 }}>{k}</span>
    <span style={{ color: vc, fontFamily: M, fontSize: 11 }}>{v}{u && <span style={{ color: C.accent, marginLeft: 4, fontSize: 10 }}>{u}</span>}</span>
  </div>
);
const Note = ({ c = C.dim, ch }) => (
  <div style={{ marginTop: 8, marginBottom: 6, color: c, fontFamily: M, fontSize: 10, lineHeight: 1.85, padding: "8px 12px", borderLeft: `2px solid ${c}55`, background: `${c}07`, borderRadius: 3 }}>{ch}</div>
);
const Warn = ({ ch }) => (
  <div style={{ marginTop: 8, color: C.yellow, fontFamily: M, fontSize: 10, lineHeight: 1.8, padding: "7px 12px", borderLeft: `2px solid ${C.yellow}`, background: "rgba(255,230,0,0.05)", borderRadius: 3 }}>⚠ {ch}</div>
);
const Good = ({ ch }) => (
  <div style={{ marginTop: 8, color: C.green, fontFamily: M, fontSize: 10, lineHeight: 1.8, padding: "7px 12px", borderLeft: `2px solid ${C.green}`, background: "rgba(74,222,128,0.05)", borderRadius: 3 }}>✓ {ch}</div>
);
const Crit = ({ ch }) => (
  <div style={{ marginTop: 8, color: C.red, fontFamily: M, fontSize: 10, lineHeight: 1.8, padding: "7px 12px", borderLeft: `2px solid ${C.red}`, background: "rgba(248,113,113,0.05)", borderRadius: 3 }}>✖ {ch}</div>
);
function TH({ cols }) {
  return (
    <thead>
      <tr>{cols.map(h => (
        <th key={h} style={{ padding: "6px 9px", borderBottom: `1px solid ${C.border}`, color: C.accent, textAlign: "left", fontWeight: "normal", fontSize: 10, letterSpacing: "0.06em", whiteSpace: "nowrap", opacity: 0.85 }}>{h}</th>
      ))}</tr>
    </thead>
  );
}
function Grid() {
  return (
    <svg style={{ position: "fixed", inset: 0, width: "100%", height: "100%", pointerEvents: "none", zIndex: 0 }}>
      <defs>
        <pattern id="sg" width="20" height="20" patternUnits="userSpaceOnUse">
          <path d="M20 0L0 0 0 20" fill="none" stroke="rgba(0,229,255,0.035)" strokeWidth={0.5} />
        </pattern>
        <pattern id="lg" width="100" height="100" patternUnits="userSpaceOnUse">
          <rect width="100" height="100" fill="url(#sg)" />
          <path d="M100 0L0 0 0 100" fill="none" stroke="rgba(0,229,255,0.065)" strokeWidth={1} />
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#lg)" />
    </svg>
  );
}

// ── EDF data ───────────────────────────────────────────────────
// tandem efficiency: 0.91 (pressure-rise fan-on-fan penalty)
// AUW for T/W: 3607g empty + 410g battery = 4017g
const AUW = 4017;
const FUSELAGE_THRUST = 650; // g, 40mm XFLY fixed
const EFF = 0.91;

const EDFS = [
  {
    id: "flyfox",
    tier: "Budget",
    name: "FlyFox 80mm 6S",
    model: "2900KV 12-blade",
    color: C.teal,
    cost: 35,
    thrustSingle: 1400,   // g per EDF
    peakA: 45,
    maxRPM: 40000,
    escRating: 50,
    voltage: "6S",
    blades: 12,
    motorSize: "—",
    phases: "2–6",
    housing: "Plastic",
    note: "Cheapest proof-of-airframe unit. Adequate for hover + transition testing.",
  },
  {
    id: "freewing-budget",
    tier: "Budget",
    name: "Freewing 80mm 6S",
    model: "2836-2150KV",
    color: C.teal,
    cost: 55,
    thrustSingle: 1700,
    peakA: 50,
    maxRPM: 35000,
    escRating: 60,
    voltage: "6S",
    blades: 12,
    motorSize: "2836",
    phases: "2–6",
    housing: "Plastic",
    note: "Better build quality for early phase iteration. Freewing has good spares availability.",
  },
  {
    id: "generic",
    tier: "Budget",
    name: "Generic 80mm 6S",
    model: "3000KV 12-blade",
    color: C.teal,
    cost: 38,
    thrustSingle: 1400,
    peakA: 43,
    maxRPM: 42000,
    escRating: 50,
    voltage: "6S",
    blades: 12,
    motorSize: "—",
    phases: "2–6",
    housing: "Plastic",
    note: "Various brands (BananaHobby, Readytosky). Quality varies — inspect before install.",
  },
  {
    id: "xrp",
    tier: "Standard",
    name: "Changesun XRP 3660",
    model: "2700KV 12-blade",
    color: C.orange,
    cost: 170,
    thrustSingle: 2900,
    peakA: 84,
    maxRPM: 52000,
    escRating: 120,
    voltage: "6S",
    blades: 12,
    motorSize: "3660",
    phases: "7+",
    housing: "Aluminum",
    note: "CURRENT SPEC — SELECTED. Best thrust-per-dollar in class. Phase 7 baseline.",
    current: true,
  },
  {
    id: "freewing-hp",
    tier: "High-Perf",
    name: "Freewing 80mm HP",
    model: "3500KV 12-blade",
    color: C.purple,
    cost: 180,
    thrustSingle: 3100,
    peakA: 88,
    maxRPM: 54000,
    escRating: 120,
    voltage: "6S",
    blades: 12,
    motorSize: "—",
    phases: "7+",
    housing: "Aluminum",
    note: "Moderate premium over XRP with marginal thrust gain. Good availability.",
  },
  {
    id: "jetfan",
    tier: "High-Perf",
    name: "Jetfan 80mm Pro",
    model: "3300KV 6S",
    color: C.purple,
    cost: 240,
    thrustSingle: 3200,
    peakA: 90,
    maxRPM: 56000,
    escRating: 120,
    voltage: "6S",
    blades: 12,
    motorSize: "—",
    phases: "7+",
    housing: "Aluminum",
    note: "Precision-balanced rotor, reduced vibration. Popular in scale jet community.",
  },
  {
    id: "schubeler",
    tier: "High-Perf",
    name: "Schübeler DS-51-AXI HST",
    model: "80mm 6S",
    color: C.pink,
    cost: 320,
    thrustSingle: 3800,
    peakA: 95,
    maxRPM: 60000,
    escRating: 120,
    voltage: "6S",
    blades: 12,
    motorSize: "AXI",
    phases: "7+",
    housing: "Aircraft-grade Al",
    note: "Extreme performance, aircraft-grade aluminum. Maximum efficiency at high speed.",
  },
];

// Fuselage EDF (fixed, not an upgrade path)
const FUSE_EDF = {
  name: "XFLY Galaxy X4 PRO 40mm",
  model: "12-blade 4S 5850KV",
  cost: 45,
  thrustSingle: 650,
  peakA: 30,
  escRating: 40,
  voltage: "4S",
  blades: 12,
  housing: "Plastic",
  note: "ONLY approved fuselage EDF — fits 40mm nozzle assembly. Not an upgrade path.",
};

function tandemThrust(single) {
  return Math.round(2 * single * EFF);
}
function aircraftThrust(single) {
  return tandemThrust(single) * 2 + FUSELAGE_THRUST;
}
function tw(single) {
  return (aircraftThrust(single) / AUW).toFixed(2);
}
function nacelleAircraft(single) {
  return tandemThrust(single) * 2;
}

// ────────────────────────────────────────────────────────────────
// TAB 1: EDF Comparison
// ────────────────────────────────────────────────────────────────
function TierBadge({ tier, color }) {
  return (
    <span style={{
      display: "inline-block", padding: "1px 7px", borderRadius: 3,
      background: `${color}18`, border: `1px solid ${color}55`,
      color: color, fontFamily: M, fontSize: 9, letterSpacing: "0.08em",
    }}>{tier}</span>
  );
}

function ThrustBarChart({ edfs }) {
  const maxThrust = Math.max(...edfs.map(e => tandemThrust(e.thrustSingle)));
  const BAR_MAX_W = 220;
  const ROW_H = 32;
  const LEFT = 155;
  const VW = 680;
  const VH = edfs.length * ROW_H + 50;

  return (
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{ display: "block", maxWidth: "100%" }}>
      <text x={LEFT + BAR_MAX_W / 2} y={14} textAnchor="middle" fill={C.accent} fontSize={8} fontFamily={M} opacity={0.7}>
        TANDEM NACELLE THRUST (g) — 2 × EDF × 0.91 series efficiency
      </text>
      {edfs.map((e, i) => {
        const nt = tandemThrust(e.thrustSingle);
        const bw = (nt / maxThrust) * BAR_MAX_W;
        const y = 26 + i * ROW_H;
        const isXRP = e.current;
        const barColor = isXRP ? C.orange : e.color;
        return (
          <g key={e.id}>
            <text x={LEFT - 6} y={y + ROW_H * 0.62} textAnchor="end" fill={isXRP ? C.orange : e.color} fontSize={8.5} fontFamily={M}>
              {e.name}{isXRP ? " ★" : ""}
            </text>
            <rect x={LEFT} y={y + 4} width={bw} height={ROW_H - 10} rx={3}
              fill={`${barColor}22`} stroke={barColor} strokeWidth={isXRP ? 2 : 1} />
            <text x={LEFT + bw + 7} y={y + ROW_H * 0.62} fill={barColor} fontSize={9} fontFamily={M}>
              {nt.toLocaleString()} g
            </text>
            <text x={LEFT + bw + 80} y={y + ROW_H * 0.62} fill={`${barColor}80`} fontSize={8} fontFamily={M}>
              (${e.cost * 2}/pair)
            </text>
          </g>
        );
      })}
      {/* Single EDF bars — second bar set offset */}
      {edfs.map((e, i) => {
        const bw = (e.thrustSingle / maxThrust) * BAR_MAX_W;
        const y = 26 + i * ROW_H;
        return (
          <rect key={e.id + "-s"} x={LEFT} y={y + ROW_H - 8} width={bw} height={2} rx={1}
            fill={`${e.color}55`} />
        );
      })}
      <text x={LEFT} y={VH - 6} fill={`${C.dim}50`} fontSize={7} fontFamily={M}>
        Thin underline = single EDF thrust · Full bar = tandem nacelle pair thrust
      </text>
    </svg>
  );
}

function Tab1EdfComparison({ filter }) {
  const vis = filter === "All" ? EDFS : EDFS.filter(e => e.tier === filter);

  const cols = ["EDF / Model", "Tier", "Thrust/EDF", "Peak A", "Max RPM", "ESC Req.", "Nacelle Pair Thrust", "Cost/EDF", "Cost/Pair", "Phases", "Housing"];

  return (
    <div>
      <SH t="EDF Option Comparison — All Tiers" mt={0} />
      <Note c={C.dim} ch={
        "Nacelle = 2 × EDF in tandem series · Pod OD 93.5mm · Pod length 230mm · Tandem efficiency factor 0.91 · All EDFs 80mm 6S (nacelle) · Fuselage EDF 40mm 4S (fixed, see Tab 4)"
      } />

      <div style={{ overflowX: "auto", marginTop: 14 }}>
        <table style={{ borderCollapse: "collapse", width: "100%", minWidth: 860 }}>
          <TH cols={cols} />
          <tbody>
            {vis.map(e => {
              const nt = tandemThrust(e.thrustSingle);
              const isXRP = e.current;
              return (
                <tr key={e.id} style={{
                  background: isXRP ? `${C.orange}12` : "transparent",
                  outline: isXRP ? `1px solid ${C.orange}55` : "none",
                }}>
                  <td style={{ padding: "7px 9px", fontFamily: M, fontSize: 10, color: isXRP ? C.orange : e.color, whiteSpace: "nowrap" }}>
                    {e.name}{isXRP ? " ★ CURRENT" : ""}<br />
                    <span style={{ opacity: 0.65, fontSize: 9 }}>{e.model}</span>
                  </td>
                  <td style={{ padding: "7px 9px" }}><TierBadge tier={e.tier} color={e.color} /></td>
                  <td style={{ padding: "7px 9px", fontFamily: M, fontSize: 10, color: C.text }}>{e.thrustSingle.toLocaleString()} g</td>
                  <td style={{ padding: "7px 9px", fontFamily: M, fontSize: 10, color: C.yellow }}>{e.peakA} A</td>
                  <td style={{ padding: "7px 9px", fontFamily: M, fontSize: 10, color: C.text }}>{e.maxRPM.toLocaleString()}</td>
                  <td style={{ padding: "7px 9px", fontFamily: M, fontSize: 10, color: C.yellow }}>{e.escRating} A</td>
                  <td style={{ padding: "7px 9px", fontFamily: M, fontSize: 10, color: isXRP ? C.orange : C.green, fontWeight: isXRP ? "bold" : "normal" }}>
                    {nt.toLocaleString()} g
                  </td>
                  <td style={{ padding: "7px 9px", fontFamily: M, fontSize: 10, color: C.gold }}>${e.cost}</td>
                  <td style={{ padding: "7px 9px", fontFamily: M, fontSize: 10, color: C.gold }}>${e.cost * 2}</td>
                  <td style={{ padding: "7px 9px", fontFamily: M, fontSize: 10, color: C.dim }}>{e.phases}</td>
                  <td style={{ padding: "7px 9px", fontFamily: M, fontSize: 10, color: C.dim }}>{e.housing}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <SH t="Thrust Bar Chart — Tandem Nacelle Pair" mt={28} />
      <ThrustBarChart edfs={vis} />

      <SH t="Fuselage EDF (Fixed — Not an Upgrade Path)" mt={28} />
      <div style={{ background: `${C.teal}08`, border: `1px solid ${C.teal}40`, borderRadius: 6, padding: "14px 18px", marginBottom: 8 }}>
        <KV k="Model" v={FUSE_EDF.name} vc={C.teal} />
        <KV k="Spec" v={FUSE_EDF.model} />
        <KV k="Thrust" v={`${FUSE_EDF.thrustSingle} g`} vc={C.green} />
        <KV k="Peak Current" v={`${FUSE_EDF.peakA} A`} vc={C.yellow} />
        <KV k="ESC Required" v={`${FUSE_EDF.escRating} A`} vc={C.yellow} />
        <KV k="Voltage" v={FUSE_EDF.voltage} />
        <KV k="Cost" v={`$${FUSE_EDF.cost}`} vc={C.gold} />
      </div>
      <Crit ch="Only the XFLY Galaxy X4 PRO 40mm is approved for the fuselage nozzle. No substitution — nozzle assembly is dimensioned for 40mm OD." />
      <Note c={C.dim} ch={FUSE_EDF.note} />
    </div>
  );
}

// ────────────────────────────────────────────────────────────────
// TAB 2: Tandem Series Performance
// ────────────────────────────────────────────────────────────────
const PHASE_MAP = {
  "Budget":     { phases: "2–6", label: "PROOF-OF-AIRFRAME" },
  "Standard":   { phases: "7+",  label: "PHASE 7 BASELINE" },
  "High-Perf":  { phases: "7+",  label: "PREMIUM UPGRADE" },
};

// Representative EDFs for perf table (one per tier, plus all HP)
const PERF_EDFS = [
  EDFS.find(e => e.id === "flyfox"),
  EDFS.find(e => e.id === "freewing-budget"),
  EDFS.find(e => e.id === "xrp"),
  EDFS.find(e => e.id === "freewing-hp"),
  EDFS.find(e => e.id === "jetfan"),
  EDFS.find(e => e.id === "schubeler"),
];

function Tab2Tandem({ filter }) {
  const vis = filter === "All" ? PERF_EDFS : PERF_EDFS.filter(e => e.tier === filter);

  return (
    <div>
      <SH t="Tandem Series Performance per Nacelle" mt={0} />
      <Note c={C.dim} ch={
        "Each nacelle = 2 × 80mm EDF in tandem (series airflow). Series efficiency = 0.91. Aircraft has 2 nacelles + 1 fuselage 40mm EDF. " +
        "AUW for T/W: 3607g empty + 410g battery = 4017g. Fuselage EDF adds 650g thrust (fixed, all phases)."
      } />

      <div style={{ overflowX: "auto", marginTop: 14 }}>
        <table style={{ borderCollapse: "collapse", width: "100%", minWidth: 800 }}>
          <TH cols={[
            "EDF Option", "Tier", "Single EDF", "Nacelle Pair (×0.91)",
            "2× Nacelles", "+ Fuselage", "Aircraft Total", "T/W (AUW 4017g)",
            "Phase", "Assessment",
          ]} />
          <tbody>
            {vis.map(e => {
              const nt = tandemThrust(e.thrustSingle);
              const nacX2 = nt * 2;
              const total = nacX2 + FUSELAGE_THRUST;
              const twRatio = (total / AUW).toFixed(2);
              const isXRP = e.current;
              const twColor = parseFloat(twRatio) >= 3.0 ? C.green : parseFloat(twRatio) >= 1.5 ? C.yellow : C.red;
              return (
                <tr key={e.id} style={{
                  background: isXRP ? `${C.orange}12` : "transparent",
                  outline: isXRP ? `1px solid ${C.orange}55` : "none",
                }}>
                  <td style={{ padding: "7px 9px", fontFamily: M, fontSize: 10, color: isXRP ? C.orange : e.color, whiteSpace: "nowrap" }}>
                    {e.name}{isXRP ? " ★" : ""}<br />
                    <span style={{ opacity: 0.65, fontSize: 9 }}>{e.model}</span>
                  </td>
                  <td style={{ padding: "7px 9px" }}><TierBadge tier={e.tier} color={e.color} /></td>
                  <td style={{ padding: "7px 9px", fontFamily: M, fontSize: 10, color: C.text }}>{e.thrustSingle.toLocaleString()} g</td>
                  <td style={{ padding: "7px 9px", fontFamily: M, fontSize: 10, color: isXRP ? C.orange : C.green }}>{nt.toLocaleString()} g</td>
                  <td style={{ padding: "7px 9px", fontFamily: M, fontSize: 10, color: C.text }}>{nacX2.toLocaleString()} g</td>
                  <td style={{ padding: "7px 9px", fontFamily: M, fontSize: 10, color: C.teal }}>+{FUSELAGE_THRUST} g</td>
                  <td style={{ padding: "7px 9px", fontFamily: M, fontSize: 10, color: C.accent, fontWeight: "bold" }}>{total.toLocaleString()} g</td>
                  <td style={{ padding: "7px 9px", fontFamily: M, fontSize: 10, color: twColor, fontWeight: "bold" }}>{twRatio}:1</td>
                  <td style={{ padding: "7px 9px", fontFamily: M, fontSize: 9, color: C.dim }}>{PHASE_MAP[e.tier].phases}</td>
                  <td style={{ padding: "7px 9px", fontFamily: M, fontSize: 9, color: isXRP ? C.orange : C.dim }}>{PHASE_MAP[e.tier].label}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <SH t="Key Performance Benchmarks" mt={28} />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(240px,1fr))", gap: 14 }}>
        {[
          { label: "Budget FlyFox (Phases 2–6)", thrust: "5,750 g total", tw: "1.43:1", color: C.teal, note: "Adequate for hover + transition testing. 2× nacelle = ~2,548g each." },
          { label: "Standard XRP (Phase 7) ★", thrust: "11,250 g total", tw: "2.80:1", color: C.orange, note: "CURRENT SPEC. 2× nacelle = ~5,278g each. Confident hover + cruise margins." },
          { label: "Schübeler DS-51 (Premium)", thrust: "14,486 g total", tw: "3.61:1", color: C.pink, note: "Extreme margin. 2× nacelle = ~6,916g each. Maximum performance envelope." },
        ].map(b => (
          <div key={b.label} style={{ background: `${b.color}08`, border: `1px solid ${b.color}40`, borderRadius: 6, padding: "14px 16px" }}>
            <div style={{ color: b.color, fontFamily: M, fontSize: 10, marginBottom: 8, fontWeight: "bold" }}>{b.label}</div>
            <KV k="Aircraft Thrust" v={b.thrust} vc={b.color} />
            <KV k="T/W at AUW 4017g" v={b.tw} vc={b.color} />
            <Note c={b.color} ch={b.note} />
          </div>
        ))}
      </div>

      <SH t="Phase Compatibility Matrix" mt={28} />
      <div style={{ overflowX: "auto" }}>
        <table style={{ borderCollapse: "collapse", width: "100%", minWidth: 600 }}>
          <TH cols={["Phase", "Description", "Nacelle EDF", "Fuselage EDF", "Hover T/W", "Risk"]} />
          <tbody>
            {[
              { phase: "2–3", desc: "Structural validation, static thrust test", edf: "FlyFox / Generic", fuseOk: true, tw: "~1.43:1", risk: "LOW", rc: C.green },
              { phase: "4–5", desc: "Tethered hover, autonomous hover, hover PID", edf: "FlyFox / Generic", fuseOk: true, tw: "~1.43:1", risk: "LOW", rc: C.green },
              { phase: "6",   desc: "Full-envelope transition flight", edf: "FlyFox / Generic", fuseOk: true, tw: "~1.43:1", risk: "MEDIUM — margin thin", rc: C.yellow },
              { phase: "7",   desc: "Full performance envelope (baseline)", edf: "Changesun XRP ★", fuseOk: true, tw: "~2.80:1", risk: "LOW", rc: C.green },
              { phase: "7+",  desc: "Performance extension, payload missions", edf: "Jetfan / Schübeler", fuseOk: true, tw: "~3.6:1", risk: "VERY LOW", rc: C.green },
            ].map(r => (
              <tr key={r.phase}>
                <td style={{ padding: "6px 9px", fontFamily: M, fontSize: 10, color: C.accent }}>{r.phase}</td>
                <td style={{ padding: "6px 9px", fontFamily: M, fontSize: 10, color: C.dim }}>{r.desc}</td>
                <td style={{ padding: "6px 9px", fontFamily: M, fontSize: 10, color: r.phase === "7" ? C.orange : C.teal }}>{r.edf}</td>
                <td style={{ padding: "6px 9px", fontFamily: M, fontSize: 10, color: C.teal }}>XFLY X4 PRO 40mm</td>
                <td style={{ padding: "6px 9px", fontFamily: M, fontSize: 10, color: C.text }}>{r.tw}</td>
                <td style={{ padding: "6px 9px", fontFamily: M, fontSize: 10, color: r.rc }}>{r.risk}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <Note c={C.dim} ch={
        "T/W shown at empty AUW (4017g). With payload or fuel headroom deduction, effective T/W will be lower. " +
        "Hover minimum recommended T/W = 1.3:1. Budget tier is sufficient for Phases 2–6 validation objectives."
      } />
    </div>
  );
}

// ────────────────────────────────────────────────────────────────
// TAB 3: ESC Pairing Guide
// ────────────────────────────────────────────────────────────────
const ESC_TIERS = [
  {
    tier: "Budget", color: C.teal,
    edf: "FlyFox / Generic 80mm 6S",
    peakA: 45, headroom: 1.2, escRating: 50,
    wire: "14 AWG silicone", fuse: "60A blade fuse per ESC",
    firmware: "BLHeli32 or AM32",
    kv: "2900–3000", poles: 14, demag: "Normal",
    bdshot: "Full BDSHOT600 supported — required for governor RPM feedback",
    rpmRange: "15,000–42,000 RPM",
    gov: "Rev L governor uses BDSHOT telemetry. Calibrate: spin-up to 50% throttle, log RPM, set KV_CAL in params.",
    example: "Hobbywing XRotor 50A, Flycolor X-Cross 50A, Aikon AK50A",
  },
  {
    tier: "Standard (XRP ★)", color: C.orange,
    edf: "Changesun XRP 3660-2700KV 80mm 6S",
    peakA: 84, headroom: 1.2, escRating: 120,
    wire: "12 AWG silicone (nacelle runs) / 10 AWG trunk", fuse: "100A ANL fuse per nacelle pair",
    firmware: "BLHeli32 32.9+ or AM32 2.x",
    kv: "2700", poles: 14, demag: "High (high RPM motor)",
    bdshot: "BDSHOT600 mandatory — governor cannot function without RPM telemetry",
    rpmRange: "20,000–52,000 RPM",
    gov: "Rev L: set MOTOR_KV=2700, POLES=14, RPM_MAX=52000, RPM_IDLE=22000. Run auto-tune sequence at 40% throttle.",
    example: "Hobbywing XRotor 120A, Flycolor 120A 6S, Aikon AK120A BLHeli32",
  },
  {
    tier: "High-Perf", color: C.purple,
    edf: "Jetfan Pro / Schübeler DS-51 / Freewing HP 80mm 6S",
    peakA: 95, headroom: 1.2, escRating: 120,
    wire: "12 AWG silicone (nacelle) / 10 AWG trunk", fuse: "100A ANL fuse per nacelle pair",
    firmware: "BLHeli32 32.9+ or AM32 2.x",
    kv: "3300–3500 (Jetfan/Freewing) / AXI-rated (Schübeler)", poles: 14, demag: "High",
    bdshot: "BDSHOT600 mandatory. Schübeler AXI motor variant: verify pole count before calibrating",
    rpmRange: "20,000–60,000 RPM",
    gov: "Rev L: MOTOR_KV per unit, POLES=14, RPM_MAX per unit. Re-run auto-tune after swap — different KV shifts RPM→thrust curve.",
    example: "Hobbywing XRotor 120A, Flycolor 120A, ZTW Shark 120A BLHeli32",
  },
  {
    tier: "Fuselage (40mm)", color: C.accent,
    edf: "XFLY Galaxy X4 PRO 40mm 12-blade 4S 5850KV",
    peakA: 30, headroom: 1.2, escRating: 40,
    wire: "16 AWG silicone", fuse: "40A blade fuse",
    firmware: "BLHeli32 or AM32",
    kv: "5850", poles: 12, demag: "Normal",
    bdshot: "BDSHOT supported — governor tracks RPM for forward-flight trim",
    rpmRange: "25,000–70,000 RPM",
    gov: "Rev L: MOTOR_KV=5850, POLES=12, RPM_MAX=70000. Fuselage EDF operates in coordinated throttle mode.",
    example: "Hobbywing XRotor 40A, Aikon AK40A, T-Motor F45A",
  },
];

const FW_PARAMS = [
  { param: "Motor KV", budget: "2900–3000", standard: "2700 ★", hp: "3300–5850", note: "Enter exact KV for governor math" },
  { param: "Motor Poles", budget: "14", standard: "14", hp: "14 (12 fuselage)", note: "Verify on motor label" },
  { param: "Demagnetization", budget: "Normal", standard: "High", hp: "High", note: "Reduces noise at high RPM" },
  { param: "BDSHOT", budget: "On", standard: "On (required)", hp: "On (required)", note: "Governor fails without RPM telem" },
  { param: "RPM Telemetry", budget: "On", standard: "On", hp: "On", note: "10Hz minimum; 50Hz preferred" },
  { param: "Current Telem", budget: "On", standard: "On", hp: "On", note: "Used for overcurrent detection" },
  { param: "Temperature Telem", budget: "On", standard: "On", hp: "On", note: "95°C derate, 110°C fault threshold" },
  { param: "PWM Frequency", budget: "24 kHz", standard: "32 kHz", hp: "32 kHz", note: "Higher = smoother at high RPM" },
  { param: "Low RPM Power Prot.", budget: "On", standard: "On", hp: "On", note: "Prevents desync at spool-up" },
];

function Tab3EscPairing({ filter }) {
  const vis = filter === "All" ? ESC_TIERS : ESC_TIERS.filter(t => {
    if (filter === "Budget") return t.tier === "Budget";
    if (filter === "Standard") return t.tier === "Standard (XRP ★)";
    if (filter === "High-Perf") return t.tier === "High-Perf" || t.tier === "Fuselage (40mm)";
    return true;
  });

  return (
    <div>
      <SH t="ESC Pairing Requirements by EDF Tier" mt={0} />
      <Note c={C.dim} ch={
        "ESC rating rule: Peak EDF current × 1.20 headroom = minimum ESC continuous rating. " +
        "Each EDF in a tandem nacelle has its own dedicated ESC. 4 nacelle ESCs + 1 fuselage ESC = 5 total ESCs per aircraft."
      } />

      {vis.map(t => (
        <div key={t.tier} style={{ background: `${t.color}08`, border: `1px solid ${t.color}40`, borderRadius: 6, padding: "14px 18px", marginBottom: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
            <div style={{ width: 3, height: 18, background: t.color }} />
            <span style={{ color: t.color, fontFamily: M, fontSize: 12, letterSpacing: "0.1em" }}>{t.tier}</span>
          </div>
          <KV k="EDF" v={t.edf} vc={t.color} />
          <KV k="Peak Current" v={`${t.peakA} A`} vc={C.yellow} />
          <KV k="With 1.20× headroom" v={`${Math.ceil(t.peakA * 1.2)} A minimum ESC`} vc={C.yellow} />
          <KV k="Recommended ESC Rating" v={`${t.escRating} A`} vc={C.orange} />
          <KV k="Wire Gauge" v={t.wire} />
          <KV k="Fuse Sizing" v={t.fuse} />
          <KV k="Firmware" v={t.firmware} />
          <KV k="Motor KV (for FW)" v={t.kv} />
          <KV k="Motor Poles" v={String(t.poles)} />
          <KV k="Demag Setting" v={t.demag} />
          <KV k="RPM Range" v={t.rpmRange} />
          <KV k="Example ESCs" v={t.example} vc={C.dim} />
          <Good ch={`BDSHOT: ${t.bdshot}`} />
          <Note c={C.accent} ch={`Governor (Rev L): ${t.gov}`} />
        </div>
      ))}

      <SH t="BLHeli32 / AM32 Parameter Reference" mt={28} />
      <div style={{ overflowX: "auto" }}>
        <table style={{ borderCollapse: "collapse", width: "100%", minWidth: 640 }}>
          <TH cols={["Parameter", "Budget Tier", "Standard (XRP ★)", "High-Perf / Fuselage", "Notes"]} />
          <tbody>
            {FW_PARAMS.map(r => (
              <tr key={r.param}>
                <td style={{ padding: "6px 9px", fontFamily: M, fontSize: 10, color: C.accent }}>{r.param}</td>
                <td style={{ padding: "6px 9px", fontFamily: M, fontSize: 10, color: C.teal }}>{r.budget}</td>
                <td style={{ padding: "6px 9px", fontFamily: M, fontSize: 10, color: C.orange }}>{r.standard}</td>
                <td style={{ padding: "6px 9px", fontFamily: M, fontSize: 10, color: C.purple }}>{r.hp}</td>
                <td style={{ padding: "6px 9px", fontFamily: M, fontSize: 9, color: C.dimmer }}>{r.note}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <SH t="Wiring Topology" mt={24} />
      <Note c={C.dim} ch={
        "Each nacelle: 10 AWG trunk from battery bus → 100A ANL fuse → T-junction → 2 × 12 AWG to ESC-NAC-x-FWD and ESC-NAC-x-AFT. " +
        "Fuselage: 16 AWG from 4S bus → 40A blade fuse → ESC-FUSE → XFLY 40mm. " +
        "All DSHOT signal wires: 26 AWG twisted pair with GND return. " +
        "Telemetry UART: shared bus through 8-to-1 MUX (74HC151), GP select lines from RP2040."
      } />
      <Warn ch="Never share ESC ground returns across nacelles on same conductor. Each nacelle pair must have independent GND to battery bus to avoid ground loop current imbalance in telemetry UART." />
      <Warn ch="120A ESC required for XRP and all High-Perf EDFs. A 50A ESC on an XRP will fail immediately at full throttle." />
    </div>
  );
}

// ────────────────────────────────────────────────────────────────
// TAB 4: Build Phase Guide
// ────────────────────────────────────────────────────────────────
const PHASE_GUIDE = [
  {
    phase: "2–3",
    title: "Structural Validation + Static Thrust Test",
    edf: "FlyFox 80mm 6S 2900KV  or  Generic 80mm 6S 3000KV",
    esc: "50A BLHeli32 (×4 nacelle + 1 fuselage 40A)",
    totalEdfCost: "$140 nacelle pairs + $45 fuselage = $185",
    nacellePairCost: "$140 (4× FlyFox at $35)",
    thrust: "~5,750 g total | T/W ~1.43:1",
    color: C.teal,
    commission: [
      "Install 4× FlyFox in nacelle pods, 1× XFLY 40mm in fuselage nozzle.",
      "Flash BLHeli32 to all ESCs. Set motor KV=2900, poles=14, demag=Normal, BDSHOT=On.",
      "Power on bench. Run BLHeli32 Suite motor direction test — verify all spin correct direction.",
      "Rev L governor: MOTOR_KV=2900, POLES=14, RPM_MAX=40000, RPM_IDLE=15000.",
      "Static thrust test on test stand: throttle to 50%, log RPM via BDSHOT telem, compare to spec.",
      "Verify current draw <45A per EDF at 50% throttle. Log temperature at 5 min run.",
      "Run governor auto-tune: spin to 50% throttle, trigger KV_CAL routine in params, save.",
    ],
    upgrade: "After Phase 3: no mandatory upgrade. Continue with budget EDFs through Phase 6.",
  },
  {
    phase: "4–5",
    title: "Tethered Hover + Autonomous Hover PID",
    edf: "FlyFox / Generic (same as Phase 2–3)",
    esc: "50A BLHeli32 (same)",
    totalEdfCost: "No additional cost — reuse Phase 2–3 hardware",
    nacellePairCost: "—",
    thrust: "~5,750 g total | T/W ~1.43:1",
    color: C.teal,
    commission: [
      "Verify governor calibration from Phase 3 is loaded into flight controller params.",
      "Tether aircraft. Arm and throttle to hover point (~65–70% throttle with budget EDFs).",
      "Log RPM FWD vs AFT per nacelle via BDSHOT. Delta should be <300 RPM at matched throttle.",
      "Tune hover PID. Budget EDFs have lower RPM response — increase D-term if oscillation observed.",
      "Monitor ESC temperature. Budget ESCs may reach 70°C at sustained hover — verify cooling airflow.",
      "Phase 5: engage autonomous hover. Verify governor holds RPM target ±200 RPM through gust input.",
    ],
    upgrade: "After Phase 5: inspect budget EDFs for bearing wear. Replace any noisy units before Phase 6.",
  },
  {
    phase: "6",
    title: "Full-Envelope Transition Flight",
    edf: "FlyFox / Generic (final budget phase)",
    esc: "50A BLHeli32 (same)",
    totalEdfCost: "No additional cost — reuse hardware",
    nacellePairCost: "—",
    thrust: "~5,750 g total | T/W ~1.43:1 (margin is thin for aggressive transitions)",
    color: C.yellow,
    commission: [
      "Pre-flight: inspect all EDF blade condition, verify no blade cracks or delamination.",
      "Set governor RPM ceiling to 85% of rated max (34,000 RPM) for budget EDF longevity.",
      "Transition testing: nacelle tilt from 90° (hover) to 0° (cruise) at 50% throttle.",
      "Monitor RPM drop during tilt — governor should compensate within 200ms.",
      "Log all EDF RPM, current, temperature during full transition envelope.",
      "If transition T/W feels marginal, do not increase throttle ceiling — plan Phase 7 upgrade instead.",
    ],
    upgrade: "Phase 6 complete: upgrade to Changesun XRP 3660-2700KV before Phase 7.",
  },
  {
    phase: "7",
    title: "Full Performance Baseline — CURRENT SPEC",
    edf: "Changesun XRP 3660-2700KV 80mm 6S  ★ SELECTED",
    esc: "120A BLHeli32 or AM32 (×4 nacelle) + 40A fuselage (unchanged)",
    totalEdfCost: "$680 nacelle EDFs (4× $170) + $45 fuselage = $725 total",
    nacellePairCost: "$340 (2× XRP at $170)",
    thrust: "~11,250 g total | T/W ~2.80:1",
    color: C.orange,
    commission: [
      "Install 4× Changesun XRP into nacelle pods. Torque motor mounting bolts to spec.",
      "Install 4× 120A BLHeli32/AM32 ESCs on nacelle bulkheads. Verify heat-sink orientation toward airflow.",
      "Flash firmware. Set motor KV=2700, poles=14, demag=High, BDSHOT=On, PWM=32kHz.",
      "Rev L governor: MOTOR_KV=2700, POLES=14, RPM_MAX=52000, RPM_IDLE=22000.",
      "Run KV_CAL auto-tune at 40% throttle. Verify RPM reading matches expected (2700 × 22.2V ÷ 1.5 load factor ≈ 39,960 RPM at 40%).",
      "Static thrust test: verify ≥2800g per EDF at full throttle. Log current — must be <84A at full throttle.",
      "Hover test: T/W ~2.80:1 — nacelles should only need ~50% throttle to hover. Verify governor holds tight.",
      "Transition and cruise test: full envelope. Log all telem. Update performance tables with actual RPM→thrust data.",
    ],
    upgrade: "Phase 7 baseline: XRP is the standard production configuration. Upgrade to high-perf only for payload or performance extension missions.",
  },
  {
    phase: "7+ Premium",
    title: "High-Performance Upgrade Path",
    edf: "Schübeler DS-51-AXI HST  or  Jetfan 80mm Pro  or  Freewing HP 3500KV",
    esc: "120A BLHeli32 or AM32 (same ESC hardware as XRP — no ESC change needed)",
    totalEdfCost: "$1,280 nacelle EDFs (4× $320 Schübeler) + $45 fuselage = $1,325 (Schübeler max)",
    nacellePairCost: "$640 Schübeler | $480 Jetfan | $360 Freewing HP",
    thrust: "Up to ~14,486 g total (Schübeler) | T/W ~3.61:1",
    color: C.purple,
    commission: [
      "Swap EDF units only — ESC hardware is unchanged (120A already sufficient).",
      "Update governor params: MOTOR_KV=per-unit, POLES=14 (verify on Schübeler AXI — may differ), RPM_MAX=per-unit.",
      "Re-run KV_CAL auto-tune sequence — new KV shifts RPM→thrust curve, old calibration is invalid.",
      "Static thrust test: verify thrust meets spec. Schübeler should produce ≥3700g per EDF.",
      "Verify current <95A at full throttle (Schübeler). 120A ESC has adequate headroom.",
      "Full flight test: increased T/W requires governor gains re-tuning — aircraft will feel more responsive.",
      "Update thrust_table.csv in flight controller with new RPM→thrust values from test data.",
    ],
    upgrade: "High-perf is the terminal upgrade. Schübeler + 120A ESC is the maximum configuration this airframe supports.",
  },
];

function DecisionTree() {
  return (
    <div style={{ background: `${C.accent}06`, border: `1px solid ${C.accent}30`, borderRadius: 6, padding: "16px 18px" }}>
      <div style={{ color: C.accent, fontFamily: M, fontSize: 11, marginBottom: 12, letterSpacing: "0.1em" }}>UPGRADE DECISION TREE</div>
      {[
        { q: "Is this Phase 2–6?", a: "→ Use budget EDFs (FlyFox / Generic). Prove airframe first.", c: C.teal },
        { q: "Did Phase 6 complete successfully?", a: "→ Yes: upgrade to Changesun XRP for Phase 7. No: fix airframe issues first.", c: C.yellow },
        { q: "Phase 7 underway. Is T/W sufficient for mission?", a: "→ XRP T/W ~2.80:1 is ample for all standard missions. No upgrade needed.", c: C.orange },
        { q: "Do you need >3.0:1 T/W or maximum performance envelope?", a: "→ Upgrade to Jetfan Pro ($240) or Schübeler DS-51 ($320). ESC unchanged.", c: C.purple },
        { q: "Budget-constrained for Phase 7?", a: "→ XRP at $170/unit is the best thrust/dollar. Do not use budget EDFs at Phase 7+ — they cannot sustain required RPM.", c: C.red },
      ].map((row, i) => (
        <div key={i} style={{ display: "flex", gap: 10, marginBottom: 10 }}>
          <div style={{ width: 3, minWidth: 3, background: row.c, borderRadius: 2, alignSelf: "stretch" }} />
          <div>
            <div style={{ color: row.c, fontFamily: M, fontSize: 10, marginBottom: 3 }}>{row.q}</div>
            <div style={{ color: C.dim, fontFamily: M, fontSize: 9, lineHeight: 1.7 }}>{row.a}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

function Tab4BuildPhase({ filter }) {
  const vis = PHASE_GUIDE;

  return (
    <div>
      <SH t="Build Phase EDF Selection Guide" mt={0} />
      <Note c={C.dim} ch={
        "Follow the phase sequence in order. Do not skip to XRP until Phase 7. Budget EDFs are intentional — they reduce cost and risk during airframe validation. " +
        "ESC and wiring must be upgraded when moving from budget to standard tier (50A → 120A)."
      } />

      {vis.map(p => (
        <div key={p.phase} style={{ background: `${p.color}08`, border: `1px solid ${p.color}40`, borderRadius: 6, padding: "16px 20px", marginBottom: 18 }}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 12, marginBottom: 14 }}>
            <span style={{ color: p.color, fontFamily: MB, fontSize: 15 }}>Phase {p.phase}</span>
            <span style={{ color: C.dim, fontFamily: M, fontSize: 11 }}>{p.title}</span>
          </div>
          <KV k="Nacelle EDF" v={p.edf} vc={p.color} />
          <KV k="ESC" v={p.esc} vc={C.yellow} />
          <KV k="EDF Cost" v={p.totalEdfCost} vc={C.gold} />
          {p.nacellePairCost !== "—" && <KV k="Nacelle Pair Cost" v={p.nacellePairCost} vc={C.gold} />}
          <KV k="Expected Thrust / T:W" v={p.thrust} vc={p.color} />
          <div style={{ marginTop: 12 }}>
            <div style={{ color: C.accent, fontFamily: M, fontSize: 9, letterSpacing: "0.12em", marginBottom: 6, opacity: 0.7 }}>COMMISSIONING STEPS</div>
            {p.commission.map((step, i) => (
              <div key={i} style={{ display: "flex", gap: 8, marginBottom: 5 }}>
                <span style={{ color: p.color, fontFamily: M, fontSize: 9, minWidth: 18 }}>{i + 1}.</span>
                <span style={{ color: C.dim, fontFamily: M, fontSize: 9, lineHeight: 1.7 }}>{step}</span>
              </div>
            ))}
          </div>
          {p.phase !== "7+ Premium" && (
            <Good ch={`Next phase upgrade note: ${p.upgrade}`} />
          )}
          {p.phase === "7+ Premium" && (
            <Note c={C.purple} ch={p.upgrade} />
          )}
        </div>
      ))}

      <SH t="Upgrade Decision Tree" mt={28} />
      <DecisionTree />

      <SH t="Cost Summary — Full Build Budget" mt={24} />
      <div style={{ overflowX: "auto" }}>
        <table style={{ borderCollapse: "collapse", width: "100%", minWidth: 560 }}>
          <TH cols={["Configuration", "4× Nacelle EDFs", "1× Fuselage EDF", "4× ESCs", "Total EDF+ESC", "T/W"]} />
          <tbody>
            {[
              {
                cfg: "Budget (Phases 2–6)", ne: "4× FlyFox $35 = $140", fe: "XFLY $45",
                escs: "4×50A + 1×40A ≈ $120", total: "~$305", tw: "~1.43:1", c: C.teal,
              },
              {
                cfg: "Standard Phase 7 ★", ne: "4× XRP $170 = $680", fe: "XFLY $45",
                escs: "4×120A + 1×40A ≈ $320", total: "~$1,045", tw: "~2.80:1", c: C.orange,
              },
              {
                cfg: "High-Perf Jetfan", ne: "4× Jetfan $240 = $960", fe: "XFLY $45",
                escs: "4×120A + 1×40A ≈ $320 (reuse)", total: "~$1,325", tw: "~3.21:1", c: C.purple,
              },
              {
                cfg: "High-Perf Schübeler", ne: "4× DS-51 $320 = $1,280", fe: "XFLY $45",
                escs: "4×120A + 1×40A ≈ $320 (reuse)", total: "~$1,645", tw: "~3.61:1", c: C.pink,
              },
            ].map(r => (
              <tr key={r.cfg} style={{ background: r.cfg.includes("★") ? `${C.orange}10` : "transparent" }}>
                <td style={{ padding: "7px 9px", fontFamily: M, fontSize: 10, color: r.c }}>{r.cfg}</td>
                <td style={{ padding: "7px 9px", fontFamily: M, fontSize: 10, color: C.gold }}>{r.ne}</td>
                <td style={{ padding: "7px 9px", fontFamily: M, fontSize: 10, color: C.teal }}>{r.fe}</td>
                <td style={{ padding: "7px 9px", fontFamily: M, fontSize: 10, color: C.yellow }}>{r.escs}</td>
                <td style={{ padding: "7px 9px", fontFamily: M, fontSize: 10, color: C.accent, fontWeight: "bold" }}>{r.total}</td>
                <td style={{ padding: "7px 9px", fontFamily: M, fontSize: 10, color: r.c }}>{r.tw}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <Note c={C.dim} ch="ESC costs are approximate retail. Budget ESC reuse not recommended when upgrading from Budget→Standard — 50A ESC cannot handle XRP peak current. Must upgrade to 120A ESCs at Phase 7." />
    </div>
  );
}

// ────────────────────────────────────────────────────────────────
// MAIN COMPONENT
// ────────────────────────────────────────────────────────────────
const TABS = [
  { id: "comparison",  label: "EDF Comparison" },
  { id: "tandem",      label: "Tandem Series Performance" },
  { id: "esc",         label: "ESC Pairing Guide" },
  { id: "phase",       label: "Build Phase Guide" },
];

const TIER_FILTERS = ["All", "Budget", "Standard", "High-Perf"];

export default function SerenityEdfOptions() {
  _ODFontLoader();
  const [tab, setTab] = useState("comparison");
  const [filter, setFilter] = useState("All");

  return (
    <div style={{ background: C.bg, minHeight: "100vh", color: C.text, fontFamily: M, position: "relative" }}>
      <Grid />
      <div style={{ position: "relative", zIndex: 1, maxWidth: 960, margin: "0 auto", padding: "32px 20px 60px" }}>

        {/* Header */}
        <div style={{ marginBottom: 28, borderBottom: `1px solid ${C.border}`, paddingBottom: 20 }}>
          <div style={{ color: C.accent, fontFamily: M, fontSize: 10, letterSpacing: "0.22em", opacity: 0.55, marginBottom: 6 }}>
            SERENITY TILTROTOR UAV · REV L
          </div>
          <div style={{ color: C.text, fontFamily: MB, fontSize: 22, letterSpacing: "0.04em", marginBottom: 6 }}>
            EDF Selection Options
          </div>
          <div style={{ color: C.dim, fontFamily: M, fontSize: 11, opacity: 0.75 }}>
            80mm 6S Nacelle EDFs (tandem pair per nacelle) · 40mm 4S Fuselage EDF (fixed) · Phases 2–7+
          </div>
          <div style={{ display: "flex", gap: 20, marginTop: 10, flexWrap: "wrap" }}>
            <span style={{ color: C.teal, fontFamily: M, fontSize: 10 }}>Budget: Phases 2–6</span>
            <span style={{ color: C.orange, fontFamily: M, fontSize: 10 }}>★ Standard XRP: Phase 7 CURRENT SPEC</span>
            <span style={{ color: C.purple, fontFamily: M, fontSize: 10 }}>High-Perf: Phase 7+ premium</span>
          </div>
        </div>

        {/* Tier Filter */}
        <div style={{ display: "flex", gap: 8, marginBottom: 20, flexWrap: "wrap" }}>
          <span style={{ color: C.dim, fontFamily: M, fontSize: 9, alignSelf: "center", marginRight: 4, opacity: 0.7 }}>FILTER:</span>
          {TIER_FILTERS.map(f => (
            <button key={f} onClick={() => setFilter(f)} style={{
              background: filter === f ? `${C.accent}20` : "transparent",
              border: `1px solid ${filter === f ? C.accent : C.border}`,
              color: filter === f ? C.accent : C.dimmer,
              fontFamily: M, fontSize: 10, padding: "4px 14px", borderRadius: 4, cursor: "pointer",
              letterSpacing: "0.06em",
            }}>{f}</button>
          ))}
        </div>

        {/* Tabs */}
        <div style={{ display: "flex", gap: 4, marginBottom: 24, borderBottom: `1px solid ${C.border}`, flexWrap: "wrap" }}>
          {TABS.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)} style={{
              background: tab === t.id ? `${C.accent}15` : "transparent",
              border: "none",
              borderBottom: tab === t.id ? `2px solid ${C.accent}` : "2px solid transparent",
              color: tab === t.id ? C.accent : C.dimmer,
              fontFamily: M, fontSize: 10, padding: "8px 18px", cursor: "pointer",
              letterSpacing: "0.07em", marginBottom: -1,
            }}>{t.label}</button>
          ))}
        </div>

        {/* Tab content */}
        {tab === "comparison" && <Tab1EdfComparison filter={filter} />}
        {tab === "tandem"     && <Tab2Tandem filter={filter} />}
        {tab === "esc"        && <Tab3EscPairing filter={filter} />}
        {tab === "phase"      && <Tab4BuildPhase filter={filter} />}

        {/* Footer */}
        <div style={{ marginTop: 48, paddingTop: 16, borderTop: `1px solid ${C.border}`, color: C.dim, fontFamily: M, fontSize: 9, opacity: 0.55, textAlign: "center" }}>
          © 2026 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP · CC BY 4.0 · Serenity fan engineering
        </div>
      </div>
    </div>
  );
}
