import { useState } from "react";

// ── OpenDyslexic font loader ─────────────────────────────────
function _ODFontLoader(){
  if(typeof document==="undefined") return null;
  if(document.getElementById("od-font-link")) return null;
  const l=document.createElement("link");
  l.id="od-font-link"; l.rel="stylesheet";
  l.href="https://fonts.cdnfonts.com/css/opendyslexic";
  document.head.appendChild(l);
  const s=document.createElement("style");
  s.id="od-font-style";
  s.textContent=`
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
  bg:"#060810", border:"rgba(0,229,255,0.11)", accent:"#00e5ff",
  orange:"#ff6b35", yellow:"#ffe600", purple:"#c084fc", green:"#4ade80",
  pink:"#f472b6", teal:"#2dd4bf", red:"#f87171", lime:"#a3e635",
  gold:"#fbbf24", dim:"rgba(255,255,255,0.92)", dimmer:"rgba(255,255,255,0.82)",
  text:"rgba(255,255,255,0.95)",
};
const M  = "'OpenDyslexic Mono','OpenDyslexicMono','Courier New',monospace";
const MB = "'OpenDyslexic Bold','OpenDyslexic',sans-serif";

// ── Unit helpers ──────────────────────────────────────────────
const mmToIn = mm => (mm*0.03937).toFixed(3);
const mmi    = mm => `${mm} mm (${mmToIn(mm)}")`;
const gToLb  = g  => (g/453.592).toFixed(2);
const gLb    = g  => `${g} g (${gToLb(g)} lb)`;

// ── Canonical Rev I dimensions (QMx 269ft×170ft×79ft @ 18") ──
const DIM = {
  L_MM:   457.2,  L_IN:  18.0,
  H_MM:   134.3,  H_IN:   5.286,
  W_MM:   288.9,  W_IN:  11.375,
  C2C_MM: 195.46, C2C_IN: 7.696,
  NAC_OD:  93.48, NAC_IN:  3.68,
  DATUM:   82.15,
  INNER:   50.99,
  OUTER:  144.47,
  ARM_STUB:10.4,
  PB_L:   101.6,  PB_W:  76.2, PB_H:  76.2,
  GONDOLA_DROP: 18,
  KEEL_L: 480.0,
  CG_MM:  190.0,  CG_IN:  7.48,
  BAT_TR:  28.0,
  TILT_FWD_STOP:  -5,
  TILT_FWD:        0,
  TILT_VTOL:      90,
  TILT_REV:      120,
  TILT_AFT_STOP: 140,
};

// ── Rev L weight budget (identical hardware to dual-EDF Rev K) ──
const W_ITEMS = [
  // Hull structure
  ["Hull shell 1.2mm PETG (6 sections)",     143],
  ["X-30 PU foam fill",                        42],
  ["CF keel + ring frames",                    28],
  ["PTFE conduit tubes ×6 (stay in hull)",     12],
  ["Access panel frames + lids (PETG)",        38],
  ["Access screws M2.5 ×16 + magnets ×8",       6],
  ["Gasket tape 3M 4016",                       8],
  // Propulsion — dual 80mm 6S series EDFs per nacelle
  ["XRP 3660-2700KV 80mm EDF ×4 (2 per nacelle, tandem series)", 1532],
  ["XFLY Galaxy X4 PRO 40mm 12-blade EDF (4S)",  40],
  ["120A ESC ×4 (nacelle, one per EDF, HW Platinum V4 120A)", 428],
  ["40A ESC ×1 (fuselage, 4S)",                15],
  ["6S→4S balance tap pigtail (cells 1–4)",     2],
  ["Nacelle pods 93.5mm OD ×2 (tandem 230mm pod)", 52],
  ["Nacelle tip caps ×2 + nav lights",         16],
  ["CF stub arms + tilt brackets ×2",          14],
  ["Nacelle tilt servos MG90S ×2",             18],
  ["Gear nozzle assemblies ×3",                12],
  ["Variable-nozzle servo SG90",                9],
  // Avionics — 8× PocketBeagle 2 + Cape-A/B (Rev K arch)
  ["PocketBeagle 2 ×8 (AM6232 + PRU-ICSS)",    80],
  ["Cape-A Sensor/Flight PCB ×4 (85×55mm 4L)", 112],
  ["Cape-B Comms/Payload PCB ×4 (90×60mm 4L)", 152],
  ["RCRS-49 sub-modules ×4",                    48],
  ["microSD ×12 (OS×8 + log×4)",                12],
  // Power + wiring
  ["PDB + BEC 5V/5A",                          30],
  ["ESC power wiring (12/16 AWG — 4 nacelle ESCs + fuselage)", 52],
  ["Servo + signal wiring",                    12],
  ["XT90 battery pigtail",                     15],
  ["Bus cables (CAN×7/RS-485×7/1553×7/ETH×8)", 25],
  ["GPS pigtails ×4 + ESC telem ×5 + misc",    22],
  // Payload + cargo system
  ["Payload servo + winch motor + driver",     20],
  ["Cargo gondola shell + clamshell door PETG",22],
  ["SG90 cargo door servo + bell-crank",        9],
  ["Cargo cradle + auto-latch assembly",        10],
  ["Dyneema SK75 winch line 1.5m",              1],
  ["TPU landing skids ×4",                      4],
  // Obstacle avoidance
  ["VL53L5CX ToF sensors ×6 Array-A + harness",15],
  ["TCA9548A mux-A + MCP23008 GPIO-A (PCB)",    4],
  ["Sensor PETG mounts ×6 Array-A + PMMA",      7],
  ["VL53L5CX ToF sensors ×6 Array-B + harness",15],
  ["TCA9548A mux-B + MCP23008 GPIO-B (PCB)",    4],
  ["Sensor PETG mounts ×6 Array-B + PMMA",      7],
  // Radios + sensors
  ["SiK 915MHz modules ×4 + antennas",         36],
  ["LoRa 915MHz RFM95W ×4 + antennas",         20],
  ["TI WL1837MOD WiFi ×4 + antennas",          12],
  ["RCRS-49 sub-modules ×4 — counted in avionics", 0],
  ["GPS u-blox M10Q ×4 + patch antennas",      48],
  ["WS2812C nav lights ×6",                     8],
  // Fasteners + misc
  ["Standoffs + screws + zip ties (8-node)",   24],
  ["Foam tape + cable clips",                   8],
];
const DRY_G   = W_ITEMS.reduce((s,[,g])=>s+g, 0);

// ── Power & thrust ────────────────────────────────────────────
const THRUST_NAC  = 5300;  // each nacelle — 2× 80mm 6S EDF tandem series, 91% of 2×2900g
const THRUST_FUSE =  650;  // XFLY Galaxy X4 PRO 5850KV 4S
const THRUST      = THRUST_NAC*2 + THRUST_FUSE;  // 11250g total

const BAT_EMPTY   =  410;  // 6S 4000mAh
const BAT_CARGO   =  295;  // 6S 2800mAh
const PAYLOAD     =  250;

const AUW_EMPTY = DRY_G + BAT_EMPTY;
const AUW_CARGO = DRY_G + BAT_CARGO + PAYLOAD;
const TW_EMPTY  = (THRUST / AUW_EMPTY).toFixed(2);
const TW_CARGO  = (THRUST / AUW_CARGO).toFixed(2);
const MAX_PAY   = Math.round(THRUST/2.0 - DRY_G - BAT_CARGO);

// ── Primitives ────────────────────────────────────────────────
const SH=({t,c=C.accent,mt=22})=>(
  <div style={{display:"flex",alignItems:"center",gap:10,marginBottom:14,marginTop:mt}}>
    <div style={{width:3,height:17,background:c}}/>
    <span style={{color:c,fontFamily:M,fontSize:13,letterSpacing:"0.1em",textTransform:"uppercase"}}>{t}</span>
  </div>
);
const KV=({k,v,vc=C.text})=>(
  <div style={{display:"flex",justifyContent:"space-between",padding:"5px 0",
    borderBottom:"1px solid rgba(0,229,255,0.07)",alignItems:"baseline"}}>
    <span style={{color:C.dim,fontFamily:M,fontSize:11}}>{k}</span>
    <span style={{color:vc,fontFamily:M,fontSize:11}}>{v}</span>
  </div>
);
const Note=({c=C.dim,ch})=>(
  <div style={{marginTop:8,marginBottom:6,color:c,fontFamily:M,fontSize:10,lineHeight:1.9,
    padding:"8px 12px",borderLeft:`2px solid ${c}55`,background:`${c}07`,borderRadius:3}}>{ch}</div>
);
const Good=({ch})=>(
  <div style={{marginTop:8,color:C.green,fontFamily:M,fontSize:10,lineHeight:1.8,
    padding:"7px 12px",borderLeft:`2px solid ${C.green}`,background:"rgba(74,222,128,0.05)",borderRadius:3}}>✓ {ch}</div>
);
const Warn=({ch})=>(
  <div style={{marginTop:8,color:C.yellow,fontFamily:M,fontSize:10,lineHeight:1.8,
    padding:"7px 12px",borderLeft:`2px solid ${C.yellow}`,background:"rgba(255,230,0,0.05)",borderRadius:3}}>⚠ {ch}</div>
);
const Crit=({ch})=>(
  <div style={{marginTop:8,color:C.red,fontFamily:M,fontSize:10,lineHeight:1.8,
    padding:"7px 12px",borderLeft:`2px solid ${C.red}`,background:"rgba(248,113,113,0.05)",borderRadius:3}}>✖ {ch}</div>
);
function TH({cols}){return(<thead><tr>{cols.map(h=>(
  <th key={h} style={{padding:"6px 9px",borderBottom:`1px solid ${C.border}`,color:C.accent,
    textAlign:"left",fontWeight:"normal",fontSize:10,letterSpacing:"0.06em",whiteSpace:"nowrap",opacity:.9}}>{h}</th>
))}</tr></thead>);}
function Grid(){return(
  <svg style={{position:"fixed",inset:0,width:"100%",height:"100%",pointerEvents:"none",zIndex:0}}>
    <defs>
      <pattern id="sg" width="20" height="20" patternUnits="userSpaceOnUse">
        <path d="M20 0L0 0 0 20" fill="none" stroke="rgba(0,229,255,0.035)" strokeWidth={0.5}/>
      </pattern>
      <pattern id="lg" width="100" height="100" patternUnits="userSpaceOnUse">
        <rect width="100" height="100" fill="url(#sg)"/>
        <path d="M100 0L0 0 0 100" fill="none" stroke="rgba(0,229,255,0.065)" strokeWidth={1}/>
      </pattern>
    </defs>
    <rect width="100%" height="100%" fill="url(#lg)"/>
  </svg>
);}

// ── Hull profile SVG (top view, 18" canonical) ────────────────
function HullProfileDiagram(){
  const VW=800, VH=320, CY=160;
  const SC = 457.2/508 * 0.82;
  const OX = 55;
  const HULL=[
    [0,0],[10,13],[28,22],[50,38],[73,45],[110,46],[150,52],[175,52],
    [207,50],[237,45],[275,36],[316,22],[325,20],[347,30],[381,36],
    [412,35],[457.2,28],
  ];
  const xp = mm => OX + mm*SC;
  const NAC_HALF = DIM.C2C_MM/2 * SC;
  const up = HULL.map(([x,y])=>`${xp(x).toFixed(1)},${(CY-y*SC*0.5).toFixed(1)}`);
  const lo = [...HULL].reverse().map(([x,y])=>`${xp(x).toFixed(1)},${(CY+y*SC*0.38).toFixed(1)}`);
  const pts = [...up,...lo].join(" ");
  const NAC_X = xp(457.2 * 0.37);
  const NAC_W = DIM.NAC_OD/2 * SC;
  const NAC_L = 170 * SC;  // 170mm — represents 230mm tandem pod length proportionally

  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      <polygon points={pts} fill={`${C.accent}0e`} stroke={C.accent} strokeWidth={2.5}/>
      <ellipse cx={xp(40).toFixed(1)} cy={CY.toFixed(1)}
        rx={(40*SC).toFixed(1)} ry={(22*SC).toFixed(1)}
        fill="rgba(0,229,255,0.09)" stroke={C.accent} strokeWidth={1.2}/>
      <circle cx={xp(381).toFixed(1)} cy={CY.toFixed(1)} r={(47*SC*0.5).toFixed(1)}
        fill="rgba(255,230,0,0.1)" stroke={C.yellow} strokeWidth={1.8}/>
      <text x={xp(381).toFixed(1)} y={(CY+4).toFixed(1)} textAnchor="middle"
        fill={C.yellow} fontSize={7.5} fontFamily={M}>40mm EDF</text>
      <line x1={xp(0).toFixed(1)} y1={CY} x2={xp(-22).toFixed(1)} y2={CY}
        stroke={C.teal} strokeWidth={3.5} strokeLinecap="round"/>
      {[-1,1].map(side=>{
        const ay = CY + side*NAC_HALF;
        const hullY = CY + side*52*SC*0.45;
        const nacCX = NAC_X;
        const nacRX = NAC_L*0.5; const nacRY = NAC_W;
        return(<g key={side}>
          <line x1={xp(150).toFixed(1)} y1={hullY.toFixed(1)} x2={nacCX.toFixed(1)} y2={ay.toFixed(1)}
            stroke={C.accent} strokeWidth={5} strokeLinecap="round"/>
          <ellipse cx={nacCX.toFixed(1)} cy={ay.toFixed(1)}
            rx={nacRX.toFixed(1)} ry={nacRY.toFixed(1)}
            fill={`${C.orange}15`} stroke={C.orange} strokeWidth={2.5}/>
          {/* FWD EDF */}
          <ellipse cx={(nacCX-nacRX*0.32).toFixed(1)} cy={ay.toFixed(1)}
            rx={(nacRX*0.22).toFixed(1)} ry={(nacRY*0.6).toFixed(1)}
            fill="none" stroke={C.orange} strokeWidth={1} strokeDasharray="3 2" opacity={0.7}/>
          {/* AFT EDF */}
          <ellipse cx={(nacCX+nacRX*0.25).toFixed(1)} cy={ay.toFixed(1)}
            rx={(nacRX*0.22).toFixed(1)} ry={(nacRY*0.6).toFixed(1)}
            fill="none" stroke={C.gold} strokeWidth={1} strokeDasharray="3 2" opacity={0.7}/>
          <text x={(nacCX-nacRX*0.32).toFixed(1)} y={(ay+side*NAC_W*0.9).toFixed(1)}
            textAnchor="middle" fill={C.orange} fontSize={7} fontFamily={M}>FWD</text>
          <text x={(nacCX+nacRX*0.25).toFixed(1)} y={(ay+side*NAC_W*0.9).toFixed(1)}
            textAnchor="middle" fill={C.gold} fontSize={7} fontFamily={M}>AFT</text>
          <circle cx={(nacCX-nacRX+8).toFixed(1)} cy={ay.toFixed(1)} r={7}
            fill={side===-1?"#cc2200":"#00aa00"} opacity={0.95}/>
          <text x={(nacCX-nacRX+8).toFixed(1)} y={(ay+side*17).toFixed(1)}
            textAnchor="middle" fill={side===-1?"#ff6060":"#60ff60"}
            fontSize={8} fontFamily={M} fontWeight="bold">
            {side===-1?"PORT":"STBD"}</text>
        </g>);
      })}
      <line x1={xp(DIM.CG_MM).toFixed(1)} y1={(CY-65).toFixed(1)}
        x2={xp(DIM.CG_MM).toFixed(1)} y2={(CY+65).toFixed(1)}
        stroke={C.green} strokeWidth={1.5} strokeDasharray="6 3"/>
      <text x={xp(DIM.CG_MM).toFixed(1)} y={(CY-72).toFixed(1)} textAnchor="middle"
        fill={C.green} fontSize={8.5} fontFamily={M} fontWeight="bold">CG {DIM.CG_MM}mm</text>
      <rect x={VW-230} y={8} width={222} height={72} rx={4}
        fill="rgba(0,0,0,0.55)" stroke="rgba(163,230,53,0.4)" strokeWidth={0.8}/>
      <text x={VW-119} y={24} textAnchor="middle" fill={C.lime} fontSize={8} fontFamily={M} letterSpacing="0.5">REV L — DUAL 80mm 6S SERIES</text>
      <text x={VW-119} y={38} textAnchor="middle" fill={C.lime} fontSize={9} fontFamily={M} fontWeight="bold">PID GOVERNOR ACTIVE</text>
      <text x={VW-119} y={52} textAnchor="middle" fill={C.orange} fontSize={7.5} fontFamily={M}>FWD+AFT EDF per nacelle · 230mm pod</text>
      <text x={VW-119} y={66} textAnchor="middle" fill={C.accent} fontSize={7.5} fontFamily={M}>11,250g thrust · T/W {TW_EMPTY}:1 empty</text>
      <text x={VW/2} y={14} textAnchor="middle"
        fill="rgba(163,230,53,0.85)" fontSize={8} fontFamily={M} letterSpacing="2">
        TOP VIEW — CANONICAL PROPORTIONS — REV L (DUAL-EDF + PID GOVERNOR)</text>
    </svg>
  );
}

// ── TAB: OVERVIEW ─────────────────────────────────────────────
function OverviewTab(){
  const ratio = (DIM.C2C_MM/DIM.L_MM).toFixed(3);
  return(<div>
    <div style={{background:"rgba(163,230,53,0.07)",border:"1px solid rgba(163,230,53,0.4)",
      borderRadius:6,padding:"16px 20px",marginBottom:20}}>
      <div style={{color:C.lime,fontFamily:M,fontSize:12,fontWeight:"bold",marginBottom:6,letterSpacing:"0.08em"}}>
        REV L — 18" CANONICAL · DUAL 80mm 6S SERIES EDFs PER NACELLE · PID GOVERNOR · 8× PocketBeagle 2
      </div>
      <div style={{color:C.gold,fontFamily:M,fontSize:10,marginBottom:12}}>
        Supersedes Rev K · Adds closed-loop RPM governor per EDF + cooperative nacelle equalization · Hardware unchanged
      </div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:20}}>
        <div>
          <KV k="Hull length"              v={mmi(DIM.L_MM)} vc={C.lime}/>
          <KV k="Nacelle centre-to-centre" v={mmi(DIM.C2C_MM)} vc={C.lime}/>
          <KV k="C2C / length ratio"       v={`${ratio}  (QMx 170/269 = 0.632)`} vc={C.teal}/>
          <KV k="Full outer span"          v={mmi(DIM.W_MM)}/>
          <KV k="Max height (hull+nac)"    v={mmi(DIM.H_MM)}/>
          <KV k="Nacelle pod OD"           v={`${DIM.NAC_OD} mm (93.5mm canonical)`}/>
          <KV k="Datum from CL"            v={`${DIM.DATUM} mm  →  outer ${DIM.OUTER} mm`} vc={C.purple}/>
        </div>
        <div>
          <KV k="Nacelle EDFs (FWD+AFT ×2)" v={`2× 80mm 6S series · ${THRUST_NAC}g/nacelle`} vc={C.orange}/>
          <KV k="Fuselage EDF"             v={`40mm 4S · ${THRUST_FUSE}g`}/>
          <KV k="Total hover thrust"       v={`${THRUST}g (${gToLb(THRUST)} lb)`} vc={C.green}/>
          <KV k="Airframe dry"             v={gLb(DRY_G)} vc={C.yellow}/>
          <KV k="AUW empty (6S 4000mAh)"  v={gLb(AUW_EMPTY)} vc={C.yellow}/>
          <KV k="T/W empty"               v={`${TW_EMPTY}:1`} vc={parseFloat(TW_EMPTY)>=2.0?C.green:C.red}/>
          <KV k="AUW cargo (2800mAh+250g)" v={gLb(AUW_CARGO)}/>
          <KV k="T/W cargo"               v={`${TW_CARGO}:1`} vc={parseFloat(TW_CARGO)>=2.0?C.green:C.yellow}/>
        </div>
      </div>
    </div>

    <HullProfileDiagram/>

    {/* Rev K → Rev L delta */}
    <SH t="Rev K → Rev L Changes"/>
    <div style={{overflowX:"auto",marginBottom:16}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["Change","Rev K","Rev L"]}/>
        <tbody>
          {[
            ["Nacelle governor","Open-loop throttle passthrough","PID closed-loop RPM per EDF + equalization"],
            ["Governor hardware","PRU-ICSS unused for governor","M4F coprocessor 500Hz PID · PRU DSHOT1200"],
            ["RPM feedback","BDSHOT available but unused","BDSHOT 1kHz → PID feedback loop"],
            ["Equalization","None — FWD/AFT run same cmd","Inter-EDF equalization PID + AFT +2% bias"],
            ["Fault detection","ESC telemetry logged only","Active fault latch + MAVLink alert + RTH"],
            ["Thermal derate","ESC internal (firmware only)","Governor-level proportional derate 85–110°C"],
            ["Current limiting","ESC internal hard cutoff","Governor soft 80A + hard 105A with latch"],
            ["EDF options","XRP 3660-2700KV only","Budget / Standard (XRP) / High-perf documented"],
            ["Nacelle pod STL","nacelle_pod_dual_80mm.stl","Unchanged — same 230mm tandem pod"],
            ["Hardware BOM","Identical to dual-EDF Rev K","No new hardware — firmware only update"],
          ].map(([c,k,l])=>(
            <tr key={c}>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:C.dim}}>{c}</td>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:C.dimmer,opacity:0.7}}>{k}</td>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:C.green}}>{l}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>

    <SH t="Architecture"/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:16}}>
      <div>
        <KV k="FC attitude loop" v="50 Hz — ArduPilot" vc={C.accent}/>
        <KV k="Nacelle governor (M4F)" v="500 Hz — equalization PID" vc={C.orange}/>
        <KV k="Per-EDF PID (M4F)" v="500 Hz — Kp=3e-4 Ki=1e-5 Kd=8e-5" vc={C.green}/>
        <KV k="DSHOT command rate" v="1 kHz — PRU-ICSS" vc={C.teal}/>
        <KV k="BDSHOT RPM feedback" v="1 kHz — embedded in DSHOT response" vc={C.teal}/>
        <KV k="BLHeli32 serial telem" v="10 Hz — RPM, I, temp, V, mAh" vc={C.purple}/>
      </div>
      <div>
        <KV k="MCU" v="PocketBeagle 2 AM6232" vc={C.text}/>
        <KV k="PRU-ICSS" v="250 MHz — DSHOT timing (4ns precision)" vc={C.text}/>
        <KV k="M4F coprocessor" v="400 MHz — governor (no OS latency)" vc={C.text}/>
        <KV k="ESC mux" v="74HC4051 8:1 (MCP23017 SEL A/B/C)" vc={C.text}/>
        <KV k="Nav lights" v="PCA9685 I²C PWM (frees GP29 for DSHOT3)" vc={C.text}/>
        <KV k="Avionics nodes" v="8× PocketBeagle 2 — Rev K arch" vc={C.text}/>
      </div>
    </div>

    <Good ch={`T/W empty: ${TW_EMPTY}:1 — 11,250g thrust ÷ ${AUW_EMPTY}g AUW. Comfortable margin above 2.0 minimum.`}/>
    <Good ch={`T/W cargo: ${TW_CARGO}:1 — 6S 2800mAh + 250g payload. Meets ≥2.0 spec.`}/>
    <Good ch={`Max payload at T/W=2.0: ${MAX_PAY}g (${gToLb(MAX_PAY)} lb) with 6S 2800mAh battery.`}/>
    <Note ch="Rev L adds no new hardware. The PID governor runs as firmware on the existing AM6232 M4F coprocessor. Update governor_firmware.bin on each of the 4 FC nodes (FC1–FC4, Cape-A) via Cape-B CN1–CN4 secure update channel."/>
  </div>);
}

// ── TAB: WEIGHT & THRUST ─────────────────────────────────────
function WeightTab(){
  const total = W_ITEMS.reduce((s,[,g])=>s+g,0);
  const BATTERIES = [
    {label:"6S 4000mAh (standard empty)",mass:410},
    {label:"6S 2800mAh (cargo config)",  mass:295},
    {label:"6S 2200mAh (lightweight)",   mass:220},
    {label:"6S 5000mAh (extended range)",mass:510},
  ];
  return(<div>
    <SH t="Weight Budget"/>
    <KV k="Airframe dry (no battery)"  v={gLb(DRY_G)} vc={C.yellow}/>
    <KV k="AUW empty (6S 4000mAh)"    v={gLb(AUW_EMPTY)} vc={C.yellow}/>
    <KV k="AUW cargo (2800mAh+250g)"  v={gLb(AUW_CARGO)}/>
    <KV k="Nacelle thrust (×2)"        v={`2 × ${THRUST_NAC}g = ${THRUST_NAC*2}g`} vc={C.green}/>
    <KV k="Fuselage thrust"            v={`${THRUST_FUSE}g`} vc={C.green}/>
    <KV k="Total thrust"               v={`${THRUST}g (${gToLb(THRUST)} lb)`} vc={C.green}/>
    <KV k="T/W empty"                 v={`${TW_EMPTY}:1`} vc={parseFloat(TW_EMPTY)>=2.0?C.green:C.red}/>
    <KV k="T/W cargo"                 v={`${TW_CARGO}:1`} vc={parseFloat(TW_CARGO)>=2.0?C.green:C.yellow}/>
    <KV k="Max payload at T/W=2.0"    v={`${MAX_PAY > 0 ? MAX_PAY+"g" : "0g"} (${gToLb(MAX_PAY)} lb)`} vc={C.lime}/>
    <KV k="BOM total (sum of items)"  v={`${total}g`} vc={total===DRY_G?C.green:C.yellow}/>

    <SH t="Battery Options"/>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["Battery","Mass","AUW empty","T/W empty","AUW +250g cargo","T/W cargo"]}/>
        <tbody>
          {BATTERIES.map(b=>{
            const auw=DRY_G+b.mass;
            const tw=(THRUST/auw).toFixed(2);
            const auwC=DRY_G+b.mass+PAYLOAD;
            const twC=(THRUST/auwC).toFixed(2);
            return(
              <tr key={b.label}>
                <td style={{padding:"5px 9px",color:C.dim,borderBottom:`1px solid ${C.border}`}}>{b.label}</td>
                <td style={{padding:"5px 9px",color:C.dimmer,borderBottom:`1px solid ${C.border}`}}>{b.mass}g</td>
                <td style={{padding:"5px 9px",color:C.dimmer,borderBottom:`1px solid ${C.border}`}}>{auw}g</td>
                <td style={{padding:"5px 9px",color:parseFloat(tw)>=2.0?C.green:C.red,borderBottom:`1px solid ${C.border}`}}>{tw}:1</td>
                <td style={{padding:"5px 9px",color:C.dimmer,borderBottom:`1px solid ${C.border}`}}>{auwC}g</td>
                <td style={{padding:"5px 9px",color:parseFloat(twC)>=2.0?C.green:C.yellow,borderBottom:`1px solid ${C.border}`}}>{twC}:1</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>

    <SH t="Fault Tolerance T/W"/>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["Condition","Thrust","T/W (AUW empty)","PID Governor Action"]}/>
        <tbody>
          {[
            ["NOMINAL — all 4 nacelle EDFs",`${THRUST}g`,TW_EMPTY,"Normal equalization — FWD/AFT matched"],
            ["FWD or AFT EDF failed (×1)",`${THRUST_NAC+2900+THRUST_FUSE}g`,(THRUST_NAC+2900+THRUST_FUSE)/AUW_EMPTY,"FAULT_LATCH + AFT or FWD continues solo"],
            ["Both EDFs in one nacelle failed",`${THRUST_NAC+THRUST_FUSE}g`,(THRUST_NAC+THRUST_FUSE)/AUW_EMPTY,"FAULT_BOTH — FC commands RTH"],
            ["One full nacelle failed",`${THRUST_NAC+THRUST_FUSE}g`,(THRUST_NAC+THRUST_FUSE)/AUW_EMPTY,"FC mixer compensates yaw"],
          ].map(([cond,thrust,tw,action])=>(
            <tr key={cond}>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:C.dim}}>{cond}</td>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:C.teal}}>{thrust}</td>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:parseFloat(tw)>=2.0?C.green:parseFloat(tw)>=1.5?C.yellow:C.red}}>{parseFloat(tw).toFixed(2)}:1</td>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:C.dimmer}}>{action}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>

    <SH t="BOM Detail"/>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:9}}>
        <TH cols={["Item","Mass (g)"]}/>
        <tbody>
          {W_ITEMS.filter(([,g])=>g>0).map(([item,g])=>(
            <tr key={item}>
              <td style={{padding:"3px 9px",color:C.dimmer,borderBottom:`1px solid ${C.border}20`}}>{item}</td>
              <td style={{padding:"3px 9px",color:C.teal,textAlign:"right",borderBottom:`1px solid ${C.border}20`}}>{g}</td>
            </tr>
          ))}
          <tr>
            <td style={{padding:"5px 9px",color:C.lime,fontWeight:"bold",borderTop:`1px solid ${C.border}`}}>TOTAL DRY</td>
            <td style={{padding:"5px 9px",color:total===DRY_G?C.green:C.red,fontWeight:"bold",textAlign:"right",borderTop:`1px solid ${C.border}`}}>{total}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>);
}

// ── TAB: DUAL-EDF NACELLE ────────────────────────────────────
function DualEDFNacelleTab(){
  return(<div>
    {/* Rev L governor note */}
    <div style={{background:"rgba(163,230,53,0.08)",border:"1px solid rgba(163,230,53,0.4)",
      borderRadius:6,padding:"12px 16px",marginBottom:16}}>
      <div style={{color:C.lime,fontFamily:M,fontSize:11,fontWeight:"bold",marginBottom:6}}>
        REV L: PID GOVERNOR ACTIVE — see "EDF Governor" tab for full spec
      </div>
      <div style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.8}}>
        Each EDF runs a 500Hz closed-loop RPM governor (M4F coprocessor). BDSHOT 1kHz is the primary feedback.
        The nacelle equalization PID commands AFT ~2% higher RPM to compensate for inlet velocity deficit.
        Faults are latched per-ESC; the partner EDF continues. See serenity-nacelle-pid-governor.jsx.
      </div>
    </div>

    <SH t="Nacelle Configuration"/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:16}}>
      <div>
        <KV k="Pod length" v="230 mm (tandem — FWD+AFT EDF)" vc={C.orange}/>
        <KV k="Pod OD" v={`${DIM.NAC_OD} mm (93.5mm canonical)`}/>
        <KV k="Pod ID" v="83 mm (XRP 3660-2700KV housing OD)"/>
        <KV k="Inter-EDF gap" v="20 mm — flow-straightener vanes"/>
        <KV k="EDF-FWD position" v="55 mm from pod inlet"/>
        <KV k="EDF-AFT position" v="155 mm from pod inlet"/>
        <KV k="FWD stage thrust" v="~2,650g (inlet efficiency ~91%)"/>
        <KV k="AFT stage thrust" v="~2,650g (velocity deficit compensated by PID +2% RPM)"/>
        <KV k="Combined nacelle thrust" v={`${THRUST_NAC}g (91% of 2×2900g)`} vc={C.green}/>
      </div>
      <div>
        <KV k="ESC per EDF" v="Hobbywing Platinum PRO V4 120A" vc={C.orange}/>
        <KV k="ESC-NAC-L-FWD" v="DSHOT0 / GP26 / mux ch000"/>
        <KV k="ESC-NAC-L-AFT" v="DSHOT1 / GP27 / mux ch001"/>
        <KV k="ESC-NAC-R-FWD" v="DSHOT2 / GP28 / mux ch010"/>
        <KV k="ESC-NAC-R-AFT" v="DSHOT3 / GP29 / mux ch011"/>
        <KV k="ESC-FUSE" v="DSHOT4 / GP0 / mux ch100"/>
        <KV k="Max ESC current each" v="84A (XRP 3660 @ 22.2V)"/>
        <KV k="Combined nacelle current" v="168A (2× 84A)"/>
        <KV k="Power bus" v="4 AWG main · 350A peak" vc={C.red}/>
      </div>
    </div>

    {/* Tandem pod cross-section SVG */}
    <SH t="Tandem Pod Cross-Section (230mm)"/>
    <svg viewBox="0 0 700 160" width="100%" style={{maxWidth:"100%",display:"block",marginBottom:12}}>
      {/* Pod outline */}
      <rect x={30} y={30} width={560} height={100} rx={20}
        fill={`${C.orange}12`} stroke={C.orange} strokeWidth={2}/>
      {/* inlet */}
      <ellipse cx={30} cy={80} rx={18} ry={50}
        fill={`${C.teal}15`} stroke={C.teal} strokeWidth={1.5}/>
      <text x={30} y={85} textAnchor="middle" fill={C.teal} fontSize={8} fontFamily={M}>INLET</text>
      {/* FWD EDF */}
      <ellipse cx={165} cy={80} rx={20} ry={48}
        fill={`${C.orange}25`} stroke={C.orange} strokeWidth={2}/>
      <text x={165} y={76} textAnchor="middle" fill={C.orange} fontSize={9} fontFamily={M} fontWeight="bold">FWD</text>
      <text x={165} y={89} textAnchor="middle" fill={C.orange} fontSize={8} fontFamily={M}>EDF</text>
      {/* inter-EDF gap + flow straightener */}
      <rect x={185} y={32} width={60} height={96} rx={2}
        fill="rgba(192,132,252,0.12)" stroke={C.purple} strokeWidth={1} strokeDasharray="4 3"/>
      {[0,1,2,3,4].map(i=>(
        <line key={i} x1={185} y1={45+i*19} x2={245} y2={45+i*19}
          stroke={C.purple} strokeWidth={0.8} opacity={0.6}/>
      ))}
      <text x={215} y={77} textAnchor="middle" fill={C.purple} fontSize={7} fontFamily={M}>FLOW</text>
      <text x={215} y={87} textAnchor="middle" fill={C.purple} fontSize={7} fontFamily={M}>VANES</text>
      <text x={215} y={97} textAnchor="middle" fill={C.purple} fontSize={7} fontFamily={M}>20mm</text>
      {/* AFT EDF */}
      <ellipse cx={370} cy={80} rx={20} ry={48}
        fill={`${C.gold}25`} stroke={C.gold} strokeWidth={2}/>
      <text x={370} y={76} textAnchor="middle" fill={C.gold} fontSize={9} fontFamily={M} fontWeight="bold">AFT</text>
      <text x={370} y={89} textAnchor="middle" fill={C.gold} fontSize={8} fontFamily={M}>EDF</text>
      {/* nozzle */}
      <path d={`M580,32 L640,50 L640,110 L580,128 Z`}
        fill={`${C.teal}15`} stroke={C.teal} strokeWidth={1.5}/>
      <text x={620} y={85} textAnchor="middle" fill={C.teal} fontSize={8} fontFamily={M}>NOZZ</text>
      {/* dimension annotations */}
      <line x1={30} y1={145} x2={590} y2={145} stroke={C.dimmer} strokeWidth={0.5} opacity={0.4}/>
      <text x={310} y={158} textAnchor="middle" fill={C.dimmer} fontSize={8} fontFamily={M}>230mm pod length</text>
      <line x1={30} y1={148} x2={30} y2={142} stroke={C.dimmer} strokeWidth={0.8} opacity={0.4}/>
      <line x1={590} y1={148} x2={590} y2={142} stroke={C.dimmer} strokeWidth={0.8} opacity={0.4}/>
      <text x={165} y={18} textAnchor="middle" fill={C.orange} fontSize={8} fontFamily={M}>@55mm</text>
      <text x={370} y={18} textAnchor="middle" fill={C.gold} fontSize={8} fontFamily={M}>@155mm</text>
      <text x={215} y={18} textAnchor="middle" fill={C.purple} fontSize={8} fontFamily={M}>+20mm gap</text>
    </svg>

    <SH t="Fault State Matrix"/>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["State","FWD ESC","AFT ESC","Nacelle Thrust","Governor Action"]}/>
        <tbody>
          {[
            ["NOMINAL",       "✓ ACTIVE",     "✓ ACTIVE",     `${THRUST_NAC}g`,   "Equalization PID running — matched RPM"],
            ["FWD FAULT",     "✗ LATCHED",    "✓ CONTINUES",  "~2,650g",           "AFT runs at full cmd · MAVLink WARN"],
            ["AFT FAULT",     "✓ CONTINUES",  "✗ LATCHED",    "~2,650g",           "FWD runs at full cmd · MAVLink WARN"],
            ["BOTH FAULT",    "✗ LATCHED",    "✗ LATCHED",    "0g",                "FC: NACELLE_LOST → RTH mandatory"],
          ].map(([state,fwd,aft,thrust,action])=>(
            <tr key={state}>
              <td style={{padding:"5px 9px",borderBottom:`1px solid ${C.border}`,color:
                state==="NOMINAL"?C.green:state==="BOTH FAULT"?C.red:C.yellow,fontWeight:"bold"}}>{state}</td>
              <td style={{padding:"5px 9px",borderBottom:`1px solid ${C.border}`,color:
                fwd.startsWith("✓")?C.green:C.red}}>{fwd}</td>
              <td style={{padding:"5px 9px",borderBottom:`1px solid ${C.border}`,color:
                aft.startsWith("✓")?C.green:C.red}}>{aft}</td>
              <td style={{padding:"5px 9px",borderBottom:`1px solid ${C.border}`,color:C.teal}}>{thrust}</td>
              <td style={{padding:"5px 9px",borderBottom:`1px solid ${C.border}`,color:C.dimmer}}>{action}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>

    <SH t="ESC Wiring (Independent Power Rails)"/>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["ESC","Power input","Fuse","Wire","DSHOT signal","Telem mux"]}/>
        <tbody>
          {[
            ["ESC-NAC-L-FWD","PDB rail A — XT30","100A poly","12 AWG","GP26 PRU DSHOT0","MCP23017 000"],
            ["ESC-NAC-L-AFT","PDB rail B — XT30","100A poly","12 AWG","GP27 PRU DSHOT1","MCP23017 001"],
            ["ESC-NAC-R-FWD","PDB rail C — XT30","100A poly","12 AWG","GP28 PRU DSHOT2","MCP23017 010"],
            ["ESC-NAC-R-AFT","PDB rail D — XT30","100A poly","12 AWG","GP29 PRU DSHOT3","MCP23017 011"],
            ["ESC-FUSE","PDB tap 4S balance","30A blade","16 AWG","GP0 PRU DSHOT4","MCP23017 100"],
          ].map(([esc,pwr,fuse,wire,dshot,mux])=>(
            <tr key={esc}>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:C.orange,fontWeight:"bold"}}>{esc}</td>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:C.dim}}>{pwr}</td>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:C.red}}>{fuse}</td>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:C.dimmer}}>{wire}</td>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:C.teal}}>{dshot}</td>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:C.purple}}>{mux}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>

    <Good ch="Independent power rails per ESC — a fuse blow or ESC failure cannot shut down its partner EDF."/>
    <Warn ch="4 AWG main power bus required — peak current 350A (4×84A nacelle + 30A fuselage). Never substitute smaller gauge."/>
    <Note ch="1000µF electrolytic bulk capacitor per ESC at PDB — damps inrush during rapid throttle-up of the equalization PID correction."/>
  </div>);
}

// ── TAB: EDF GOVERNOR ────────────────────────────────────────
function EDFGovernorTab(){
  return(<div>
    <div style={{background:"rgba(74,222,128,0.07)",border:"1px solid rgba(74,222,128,0.35)",
      borderRadius:6,padding:"12px 16px",marginBottom:16}}>
      <div style={{color:C.green,fontFamily:M,fontSize:11,fontWeight:"bold",marginBottom:4}}>
        Rev L — Per-EDF PID Closed-Loop RPM Governor
      </div>
      <div style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.8}}>
        Full specification: serenity-nacelle-pid-governor.jsx (5 tabs — Overview, Per-EDF PID, Cooperative Control, Fault Response, Commissioning).
        This tab is a Rev L summary for quick reference.
      </div>
    </div>

    <SH t="Control Hierarchy"/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:16}}>
      <div>
        <KV k="Loop 1 — FC attitude" v="50 Hz · ArduPilot" vc={C.accent}/>
        <KV k="Loop 2 — Nacelle governor" v="500 Hz · M4F · equalization PID" vc={C.orange}/>
        <KV k="Loop 3 — Per-EDF PID" v="500 Hz · M4F · RPM tracking" vc={C.green}/>
        <KV k="DSHOT output" v="1 kHz · PRU-ICSS 250MHz" vc={C.teal}/>
        <KV k="BDSHOT RPM feedback" v="1 kHz · embedded in DSHOT frame" vc={C.teal}/>
        <KV k="BLHeli32 serial feedback" v="10 Hz · I/temp/V via 74HC4051 mux" vc={C.purple}/>
      </div>
      <div>
        <KV k="Kp_rpm" v="3.0×10⁻⁴" vc={C.cyan}/>
        <KV k="Ki_rpm" v="1.0×10⁻⁵" vc={C.cyan}/>
        <KV k="Kd_rpm" v="8.0×10⁻⁵" vc={C.cyan}/>
        <KV k="Kp_equalization" v="1.0×10⁻⁴" vc={C.purple}/>
        <KV k="Ki_equalization" v="3.0×10⁻⁶" vc={C.purple}/>
        <KV k="AFT bias" v="+2.0% RPM (inlet velocity deficit)" vc={C.gold}/>
      </div>
    </div>

    <SH t="Limiter Stack"/>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["Limiter","Threshold","Action","State"]}/>
        <tbody>
          {[
            ["Thermal derate","85°C → 110°C","Linear throttle cap 100%→0%","DERATE → FAULT_LATCH"],
            ["Current soft limit","80A","Proportional throttle reduction","DERATE"],
            ["Current hard limit","105A","throttle=0 + fault latch","FAULT_LATCH"],
            ["RPM stall","<5000 RPM @ cmd>20%","throttle=0 + fault latch","FAULT_LATCH"],
            ["RPM runaway",">56,000 RPM","throttle=0 + fault latch","FAULT_LATCH"],
            ["BDSHOT loss",">100ms no response","throttle=0 + fault latch","FAULT_LATCH"],
          ].map(([lim,thresh,action,state])=>(
            <tr key={lim}>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:C.dim}}>{lim}</td>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:C.yellow}}>{thresh}</td>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:C.dimmer}}>{action}</td>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:C.red}}>{state}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>

    <SH t="Fault State Machine"/>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["State","Trigger","FWD throttle","AFT throttle","FC action"]}/>
        <tbody>
          {[
            ["NORMAL","Nominal operation","PID tracking","PID tracking + +2% bias","Normal flight"],
            ["DERATE_FWD","ESC-FWD temp>85°C or I>80A","Proportionally reduced","Equalization adjusts","Log WARN"],
            ["DERATE_AFT","ESC-AFT temp>85°C or I>80A","Equalization adjusts","Proportionally reduced","Log WARN"],
            ["FAULT_FWD","ESC-FWD temp>110°C or I>105A","0 (latched)","Full commanded","MAVLink WARN + RTH option"],
            ["FAULT_AFT","ESC-AFT temp>110°C or I>105A","Full commanded","0 (latched)","MAVLink WARN + RTH option"],
            ["FAULT_BOTH","Both ESCs latched","0 (latched)","0 (latched)","NACELLE_LOST → RTH mandatory"],
          ].map(([state,trigger,fwd,aft,fc])=>(
            <tr key={state}>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:
                state==="NORMAL"?C.green:state.includes("DERATE")?C.yellow:C.red,fontWeight:"bold"}}>{state}</td>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:C.dimmer,fontSize:9}}>{trigger}</td>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:C.orange,fontSize:9}}>{fwd}</td>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:C.gold,fontSize:9}}>{aft}</td>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:C.dim,fontSize:9}}>{fc}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>

    <SH t="Commissioning Overview"/>
    <ol style={{fontFamily:M,fontSize:10,lineHeight:2.1,color:C.dim,paddingLeft:20,marginTop:8}}>
      <li>Flash M4F governor firmware: <span style={{color:C.teal}}>governor_firmware_revL.bin</span> to FC1–FC4 via CN1–CN4</li>
      <li>Enable BDSHOT on all 4 nacelle ESCs in BLHeli32/AM32 Configurator. Set telem baud 115200.</li>
      <li>Bench calibration: run <span style={{color:C.teal}}>governor_cal.py --mode bench</span> — logs RPM vs thrust curve, fits k coefficient</li>
      <li>Update <span style={{color:C.teal}}>EDF_THRUST_K</span> in governor_config.h from bench measurement (expect k ≈ 1.07×10⁻⁶ g/RPM²)</li>
      <li>Step-response PID tuning: 10% step → observe settle time &lt;200ms, overshoot &lt;5%</li>
      <li>Verify equalization: |RPM_FWD − RPM_AFT| &lt; 100 RPM at steady state</li>
      <li>Fault injection: confirm FAULT_LATCH, partner continues, MAVLink alert, no auto-recovery</li>
      <li>Flight acceptance: two full hover cycles — monitor temp, current, RPM balance</li>
    </ol>

    <Good ch="PID governor operates on existing M4F silicon — no new hardware required. Binary update only."/>
    <Warn ch="Re-run bench calibration after any EDF replacement — thrust k coefficient varies ±5% unit-to-unit."/>
    <Note ch="See serenity-nacelle-pid-governor.jsx for full pseudocode, SVG block diagrams, commissioning checklist, and governor_config.h reference."/>
  </div>);
}

// ── TAB: EDF OPTIONS ─────────────────────────────────────────
function EDFOptionsTab(){
  const EDF_TIERS = [
    {
      tier:"BUDGET", color:C.teal, phase:"Phases 2–6",
      edfs:[
        {name:"FlyFox 80mm 6S 2900KV 12-blade",price:35,thrust:1400,current:45,rpm:40000,esc:"50A BLHeli32",pair:2550},
        {name:"Generic 80mm 6S 3000KV 12-blade",price:38,thrust:1450,current:45,rpm:40000,esc:"50A BLHeli32",pair:2640},
        {name:"Freewing 80mm 2836-2150KV 6S",   price:55,thrust:1700,current:50,rpm:35000,esc:"60A BLHeli32",pair:3094},
      ]
    },
    {
      tier:"STANDARD ★ SELECTED", color:C.orange, phase:"Phase 7 (baseline)",
      edfs:[
        {name:"Changesun XRP 3660-2700KV 80mm 6S",price:170,thrust:2900,current:84,rpm:52000,esc:"120A BLHeli32",pair:5278,selected:true},
      ]
    },
    {
      tier:"HIGH PERFORMANCE", color:C.purple, phase:"Phase 7+ premium",
      edfs:[
        {name:"Freewing 80mm 12-blade 3500KV 6S", price:180,thrust:3100,current:88,rpm:54000,esc:"120A BLHeli32",pair:5642},
        {name:"Jetfan 80mm Pro 3300KV 6S",        price:240,thrust:3200,current:90,rpm:54000,esc:"120A BLHeli32",pair:5824},
        {name:"Schübeler DS-51-AXI HST 80mm 6S",  price:320,thrust:3800,current:95,rpm:58000,esc:"120A BLHeli32+",pair:6916},
      ]
    },
  ];

  const maxPairThrust = Math.max(...EDF_TIERS.flatMap(t=>t.edfs.map(e=>e.pair)));

  return(<div>
    <div style={{background:"rgba(255,107,53,0.07)",border:"1px solid rgba(255,107,53,0.35)",
      borderRadius:6,padding:"12px 16px",marginBottom:16}}>
      <div style={{color:C.orange,fontFamily:M,fontSize:11,fontWeight:"bold",marginBottom:4}}>
        EDF Selection Guide — Rev L
      </div>
      <div style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.8}}>
        Full specification: serenity-edf-options.jsx (4 tabs — EDF Comparison, Tandem Series Performance, ESC Pairing, Build Phase Guide).
        The PID governor (Rev L) auto-tunes to any EDF via bench calibration — no code changes needed when swapping tiers.
      </div>
    </div>

    {EDF_TIERS.map(tier=>(
      <div key={tier.tier}>
        <SH t={`${tier.tier} — ${tier.phase}`} c={tier.color}/>
        <div style={{overflowX:"auto",marginBottom:8}}>
          <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
            <TH cols={["EDF","$/each","Thrust/EDF","Peak A","Max RPM","ESC req.","Nacelle pair (×0.91)"]}/>
            <tbody>
              {tier.edfs.map(e=>(
                <tr key={e.name} style={{background:e.selected?`${tier.color}12`:"transparent"}}>
                  <td style={{padding:"5px 9px",borderBottom:`1px solid ${C.border}`,color:e.selected?tier.color:C.dim}}>
                    {e.selected?"★ ":""}{e.name}</td>
                  <td style={{padding:"5px 9px",borderBottom:`1px solid ${C.border}`,color:C.teal}}>${e.price}</td>
                  <td style={{padding:"5px 9px",borderBottom:`1px solid ${C.border}`,color:C.green}}>{e.thrust}g</td>
                  <td style={{padding:"5px 9px",borderBottom:`1px solid ${C.border}`,color:C.yellow}}>{e.current}A</td>
                  <td style={{padding:"5px 9px",borderBottom:`1px solid ${C.border}`,color:C.dimmer}}>{e.rpm.toLocaleString()}</td>
                  <td style={{padding:"5px 9px",borderBottom:`1px solid ${C.border}`,color:C.red}}>{e.esc}</td>
                  <td style={{padding:"5px 9px",borderBottom:`1px solid ${C.border}`,color:e.selected?C.lime:C.dimmer,fontWeight:e.selected?"bold":"normal"}}>{e.pair}g</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {/* Mini bar chart */}
        <div style={{marginBottom:12}}>
          {tier.edfs.map(e=>(
            <div key={e.name} style={{display:"flex",alignItems:"center",gap:8,marginBottom:4}}>
              <div style={{fontFamily:M,fontSize:8,color:C.dimmer,minWidth:260,textAlign:"right",overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{e.name.split(" ").slice(-3).join(" ")}</div>
              <div style={{flex:1,background:`${tier.color}22`,borderRadius:3,height:14,position:"relative"}}>
                <div style={{width:`${(e.pair/maxPairThrust*100).toFixed(1)}%`,background:e.selected?tier.color:`${tier.color}88`,height:"100%",borderRadius:3}}/>
              </div>
              <div style={{fontFamily:M,fontSize:9,color:tier.color,minWidth:55}}>{e.pair}g</div>
            </div>
          ))}
        </div>
      </div>
    ))}

    <SH t="Tandem Aircraft Performance Comparison"/>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["EDF Option","Nacelle pair","×2 nacelles","+ Fuse","Aircraft total","T/W (AUW 3607g)"]}/>
        <tbody>
          {[
            ["FlyFox 80mm (budget)",    2550, 5100,  650, 5750,  (5750/AUW_EMPTY).toFixed(2)],
            ["Freewing 2150KV (budget)",3094, 6188,  650, 6838,  (6838/AUW_EMPTY).toFixed(2)],
            ["XRP 2700KV ★ SELECTED",  5278,10556,  650,11206,  (11206/AUW_EMPTY).toFixed(2)],
            ["Jetfan 80mm Pro",         5824,11648,  650,12298,  (12298/AUW_EMPTY).toFixed(2)],
            ["Schübeler DS-51-AXI",     6916,13832,  650,14482,  (14482/AUW_EMPTY).toFixed(2)],
          ].map(([name,pair,x2,fuse,total,tw])=>(
            <tr key={name}>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:name.includes("SELECTED")?C.orange:C.dim,fontWeight:name.includes("SELECTED")?"bold":"normal"}}>{name}</td>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:C.teal}}>{pair}g</td>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:C.teal}}>{x2}g</td>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:C.dimmer}}>{fuse}g</td>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:C.green}}>{total.toLocaleString()}g</td>
              <td style={{padding:"4px 9px",borderBottom:`1px solid ${C.border}`,color:parseFloat(tw)>=2.5?C.green:parseFloat(tw)>=2.0?C.yellow:C.red,fontWeight:"bold"}}>{tw}:1</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>

    <SH t="Fuselage EDF — Fixed Spec"/>
    <Crit ch="XFLY Galaxy X4 PRO 40mm 12-blade 4S 5850KV is the ONLY approved fuselage EDF. It is sized for the 40mm nozzle assembly. Do NOT substitute."/>
    <KV k="Fuselage EDF" v="XFLY Galaxy X4 PRO 40mm 12-blade 4S 5850KV"/>
    <KV k="Thrust" v="650g @ 4S 14.8V · 30A peak"/>
    <KV k="ESC" v="40A BLHeli32 — 6S→4S balance tap pigtail (cells 1–4)"/>
    <KV k="Governor" v="Same 500Hz PID loop · DSHOT4 / GP0 / mux ch100"/>

    <SH t="Phase Upgrade Path"/>
    <Note ch="Phases 2–6: Use budget EDFs (FlyFox or generic 80mm 6S). Prove airframe + avionics cheaply. Governor calibrates automatically via bench script."/>
    <Note ch="Phase 7: Swap to XRP 3660-2700KV + Hobbywing 120A ESCs. This is the Rev L baseline spec. Re-run governor_cal.py after swap."/>
    <Note ch="Phase 7+ premium: Schübeler or Jetfan if T/W >3.5 is desired. Same pod, same ESC mount — swap EDF only. 120A ESC is already installed."/>
    <Warn ch="Budget EDFs (≤50A) cannot share the same ESC as the XRP or premium tiers. When upgrading from Phase 6 to 7, replace ESCs alongside EDFs."/>
    <Good ch="The PID governor auto-tunes to any EDF. Only EDF_THRUST_K in governor_config.h needs updating after a bench run. No PID gain re-tuning required for same-class EDFs."/>
    <Note ch="See serenity-edf-options.jsx for ESC pairing guide, detailed per-phase cost breakdowns, and BDSHOT/BLHeli32 firmware requirements."/>
  </div>);
}

// ── TAB: AVIONICS ─────────────────────────────────────────────
function AvionicsTab(){
  return(<div>
    <SH t="8-Node PocketBeagle 2 Architecture (Rev K arch — Rev L firmware)"/>
    <Note c={C.dim} ch="Rev L avionics hardware is identical to Rev K. All 8 PocketBeagle 2 nodes run AM6232 SoC. The 4 FC nodes (Cape-A, FC1–FC4) run the Rev L PID governor firmware on the M4F coprocessor. The 4 CN nodes (Cape-B, CN1–CN4) distribute firmware updates and relay MAVLink fault messages."/>

    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:16,marginTop:12}}>
      <div>
        <KV k="FC nodes" v="FC1–FC4 · Cape-A · 85×55mm 4L PCB" vc={C.orange}/>
        <KV k="CN nodes" v="CN1–CN4 · Cape-B · 90×60mm 4L PCB" vc={C.teal}/>
        <KV k="Bay assignments" v="A: CN1+FC1 · B: CN2+FC2 · D: CN3+FC3 · E: CN4+FC4"/>
        <KV k="M4F governor (new Rev L)" v="500Hz PID per EDF — all FC nodes" vc={C.green}/>
        <KV k="PRU-ICSS DSHOT" v="DSHOT0–3 per FC node (250MHz, 4ns)" vc={C.teal}/>
        <KV k="GPS" v="u-blox M10Q ×4 — Cape-A FC1–FC4"/>
        <KV k="IMU" v="ICM-42688-P — Cape-A each"/>
        <KV k="Baro" v="BMP388 — Cape-A each"/>
      </div>
      <div>
        <KV k="SiK 915MHz" v="×4 — Cape-B CN1–CN4"/>
        <KV k="LoRa RFM95W" v="×4 backup MAVLink — Cape-B"/>
        <KV k="WL1837MOD WiFi" v="×4 — Cape-B GCS"/>
        <KV k="RCRS-49MHz" v="×4 RC sub-modules"/>
        <KV k="TPM 2.0" v="SLB9670 — all 8 nodes" vc={C.green}/>
        <KV k="CPLD write-blocker" v="ATF16V8BQL — all Cape-B nodes" vc={C.green}/>
        <KV k="MIL-STD-1553B" v="PRU Manchester II — FC1=BC, FC2=standby"/>
        <KV k="CAN FD" v="CN1→FC1→…→FC4 linear chain · 1Mbps/8Mbps data"/>
        <KV k="RS-485" v="Multi-drop · 1Mbps"/>
        <KV k="Ethernet" v="RSTP ring · 100Mbps self-healing"/>
      </div>
    </div>

    <SH t="Rev L Firmware Update Procedure"/>
    <ol style={{fontFamily:M,fontSize:10,lineHeight:2.1,color:C.dim,paddingLeft:20,marginTop:8}}>
      <li>Connect GCS via SiK 915MHz or WiFi to any CN node.</li>
      <li>Upload <span style={{color:C.teal}}>governor_firmware_revL.bin</span> via MAVLink file transfer to CN1.</li>
      <li>CN1 distributes to FC1–FC4 via Ethernet ring (RSTP secure channel).</li>
      <li>Each FC node validates binary signature against TPM 2.0 endorsement key.</li>
      <li>FC1 flashes M4F partition; confirms via CAN FD heartbeat. FC2–FC4 follow.</li>
      <li>Reboot all 4 FC nodes. Confirm governor active via MAVLink: <span style={{color:C.teal}}>GOV_STATE = NORMAL</span> on all 4 ESCs.</li>
    </ol>

    <Good ch="TPM 2.0 signature check prevents rogue firmware installation. CPLD write-blocker protects flight logs."/>
    <Warn ch="M4F governor update and A53 OS update are independent partitions — do not flash OS update as M4F firmware."/>
  </div>);
}

// ── TAB: QUICK REF ────────────────────────────────────────────
function QuickRefTab(){
  return(<div>
    <SH t="Rev L Quick Reference"/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:16}}>
      <div>
        <SH t="Physical" c={C.teal} mt={4}/>
        <KV k="Hull length" v={mmi(DIM.L_MM)} vc={C.lime}/>
        <KV k="Nacelle C-to-C" v={mmi(DIM.C2C_MM)}/>
        <KV k="Full outer span" v={mmi(DIM.W_MM)}/>
        <KV k="Max height" v={mmi(DIM.H_MM)}/>
        <KV k="Nacelle pod OD" v={`${DIM.NAC_OD} mm`}/>
        <KV k="Nacelle pod length" v="230 mm (tandem)"/>
        <KV k="CG target" v={`${DIM.CG_MM} mm (${DIM.CG_IN}") from nose`} vc={C.green}/>
        <KV k="Canon basis" v="QMx 269ft×170ft×79ft · 18in scale"/>

        <SH t="Propulsion" c={C.orange} mt={16}/>
        <KV k="Nacelle EDF (each)" v="2× XRP 3660-2700KV 80mm 6S" vc={C.orange}/>
        <KV k="Nacelle thrust (each)" v={`${THRUST_NAC}g (2900+2900 × 91%)`} vc={C.green}/>
        <KV k="Total thrust" v={`${THRUST}g (${gToLb(THRUST)} lb)`} vc={C.green}/>
        <KV k="Nacelle ESC" v="Hobbywing Platinum V4 120A ×4"/>
        <KV k="Fuselage EDF" v="XFLY X4 PRO 40mm 4S · 650g"/>
        <KV k="Fuselage ESC" v="BLHeli32 40A ×1"/>
        <KV k="Power bus" v="4 AWG · 350A peak"/>
      </div>
      <div>
        <SH t="Performance" c={C.green} mt={4}/>
        <KV k="Dry mass" v={gLb(DRY_G)} vc={C.yellow}/>
        <KV k="AUW empty" v={gLb(AUW_EMPTY)} vc={C.yellow}/>
        <KV k="T/W empty" v={`${TW_EMPTY}:1`} vc={parseFloat(TW_EMPTY)>=2.0?C.green:C.red}/>
        <KV k="AUW cargo" v={gLb(AUW_CARGO)}/>
        <KV k="T/W cargo" v={`${TW_CARGO}:1`} vc={parseFloat(TW_CARGO)>=2.0?C.green:C.yellow}/>
        <KV k="Max payload (T/W=2.0)" v={`${MAX_PAY}g (${gToLb(MAX_PAY)} lb)`} vc={C.lime}/>
        <KV k="T/W one nacelle lost" v="1.65:1 — controlled descent" vc={C.yellow}/>

        <SH t="Governor (Rev L New)" c={C.green} mt={16}/>
        <KV k="Loop rate" v="500 Hz (M4F coprocessor)" vc={C.green}/>
        <KV k="Feedback" v="BDSHOT 1kHz + serial telem 10Hz" vc={C.teal}/>
        <KV k="Kp / Ki / Kd RPM" v="3e-4 / 1e-5 / 8e-5" vc={C.cyan}/>
        <KV k="Equalization Kp / Ki" v="1e-4 / 3e-6" vc={C.purple}/>
        <KV k="AFT bias" v="+2% RPM (inlet deficit)" vc={C.gold}/>
        <KV k="Thermal derate start" v="85°C → proportional" vc={C.yellow}/>
        <KV k="Hard cutoff" v="110°C / 105A → latch" vc={C.red}/>
      </div>
    </div>

    <SH t="Sensor Stations"/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:16}}>
      <div>
        <KV k="GPS patch" v="59.4 mm from nose"/>
        <KV k="SiK 915MHz belly" v="253.7 mm from nose"/>
        <KV k="49MHz RCRS dorsal" v="365.8 mm from nose"/>
        <KV k="ToF Array-A" v="FC3 Bay D — 6× VL53L5CX 8×8"/>
        <KV k="ToF Array-B" v="FC1 Bay A — 6× VL53L5CX 8×8"/>
      </div>
      <div>
        <KV k="Navigation lights" v="ICAO Annex 2 · 14 CFR 91.209"/>
        <KV k="Nav light driver" v="PCA9685 I²C PWM (0x40) — Rev L"/>
        <KV k="FAA registration" v="N00000 PLACEHOLDER — replace before flight" vc={C.red}/>
        <KV k="License" v="CC BY 4.0 · Steve Griffing PE(CSE) CISSP"/>
      </div>
    </div>

    <SH t="Rev History"/>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["Rev","Key change","Thrust","T/W"]}/>
        <tbody>
          {[
            ["J","XRP 3660-2700KV 80mm · Hobbywing 120A","6,450g","2.81"],
            ["K","Dual 80mm 6S series per nacelle · 4× ESC","11,250g","3.12"],
            ["L ★","PID governor per EDF · nacelle equalization · EDF options","11,250g","3.12"],
          ].map(([rev,change,thrust,tw])=>(
            <tr key={rev}>
              <td style={{padding:"5px 9px",borderBottom:`1px solid ${C.border}`,color:rev.includes("★")?C.lime:C.dimmer,fontWeight:"bold"}}>{rev}</td>
              <td style={{padding:"5px 9px",borderBottom:`1px solid ${C.border}`,color:C.dim}}>{change}</td>
              <td style={{padding:"5px 9px",borderBottom:`1px solid ${C.border}`,color:C.green}}>{thrust}</td>
              <td style={{padding:"5px 9px",borderBottom:`1px solid ${C.border}`,color:parseFloat(tw)>=2.5?C.green:C.yellow}}>{tw}:1</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>);
}

// ── TABS CONFIG ───────────────────────────────────────────────
const TABS = [
  {label:"Overview",        value:"overview"},
  {label:"Weight & Thrust", value:"weight"},
  {label:"Dual-EDF Nacelle",value:"dual_edf"},
  {label:"EDF Governor",    value:"governor"},
  {label:"EDF Options",     value:"edf_options"},
  {label:"Avionics",        value:"avionics"},
  {label:"Quick Ref",       value:"quickref"},
];

// ── APP ───────────────────────────────────────────────────────
export default function App(){
  _ODFontLoader();
  const [tab,setTab]=useState("overview");
  return(
    <div style={{background:C.bg,minHeight:"100vh",padding:"14px 18px",position:"relative",overflowX:"hidden"}}>
      <Grid/>
      <div style={{position:"relative",zIndex:1}}>
        {/* Header */}
        <div style={{marginBottom:18}}>
          <div style={{color:C.lime,fontFamily:MB,fontSize:22,fontWeight:"bold",letterSpacing:"0.05em",lineHeight:1.2}}>
            Serenity-Class Tiltrotor UAV
          </div>
          <div style={{color:C.orange,fontFamily:M,fontSize:13,marginTop:4}}>
            Rev L — 18" Canonical · Dual 80mm 6S Series EDFs per Nacelle · PID Governor · 8× PocketBeagle 2
          </div>
          <div style={{color:C.dimmer,fontFamily:M,fontSize:10,marginTop:4}}>
            CC BY 4.0 · Steve Griffing, PE(CSE) CISSP-ISSEP CPP · 2026 ·{" "}
            Fan engineering · Firefly/Serenity © Joss Whedon / Mutant Enemy / Universal (not affiliated)
          </div>
          <div style={{display:"flex",gap:20,marginTop:8,flexWrap:"wrap"}}>
            <span style={{fontFamily:M,fontSize:10,color:C.green}}>Thrust: {THRUST.toLocaleString()}g</span>
            <span style={{fontFamily:M,fontSize:10,color:C.yellow}}>Dry: {DRY_G}g</span>
            <span style={{fontFamily:M,fontSize:10,color:C.teal}}>T/W empty: {TW_EMPTY}:1</span>
            <span style={{fontFamily:M,fontSize:10,color:C.teal}}>T/W cargo: {TW_CARGO}:1</span>
            <span style={{fontFamily:M,fontSize:10,color:C.lime}}>Max payload: {MAX_PAY}g</span>
            <span style={{fontFamily:M,fontSize:10,color:C.purple}}>2× 80mm FWD+AFT per nacelle</span>
            <span style={{fontFamily:M,fontSize:10,color:C.orange}}>PID governor 500Hz</span>
          </div>
        </div>

        {/* Tab bar */}
        <div style={{display:"flex",flexWrap:"wrap",gap:6,marginBottom:18}}>
          {TABS.map(t=>(
            <button key={t.value} onClick={()=>setTab(t.value)} style={{
              background:tab===t.value?"rgba(0,229,255,0.09)":"transparent",
              border:`1px solid ${tab===t.value?C.accent:"rgba(0,229,255,0.12)"}`,
              color:tab===t.value?C.accent:C.dimmer,padding:"4px 11px",fontFamily:M,fontSize:9,
              borderRadius:4,cursor:"pointer",letterSpacing:"0.06em",
              textTransform:"uppercase",transition:"all 0.15s",
            }}>{t.label}</button>
          ))}
        </div>

        {/* Tab content */}
        {tab==="overview"    && <OverviewTab/>}
        {tab==="weight"      && <WeightTab/>}
        {tab==="dual_edf"    && <DualEDFNacelleTab/>}
        {tab==="governor"    && <EDFGovernorTab/>}
        {tab==="edf_options" && <EDFOptionsTab/>}
        {tab==="avionics"    && <AvionicsTab/>}
        {tab==="quickref"    && <QuickRefTab/>}

        <div style={{marginTop:32,paddingTop:12,borderTop:`1px solid ${C.border}`,
          fontFamily:M,fontSize:9,color:`${C.dim}60`,textAlign:"center"}}>
          Serenity-Class Tiltrotor UAV · Rev L · CC BY 4.0 · Steve Griffing 2026
        </div>
      </div>
    </div>
  );
}
