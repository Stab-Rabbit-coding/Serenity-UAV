import { useState } from "react";

// ── OpenDyslexic font loader ───────────────────────────────────
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

const C = {
  bg:"#060810", border:"rgba(0,229,255,0.11)", accent:"#00e5ff",
  orange:"#ff6b35", yellow:"#ffe600", purple:"#c084fc", green:"#4ade80",
  pink:"#f472b6", teal:"#2dd4bf", red:"#f87171", lime:"#a3e635",
  gold:"#fbbf24", dim:"rgba(255,255,255,0.90)", dimmer:"rgba(255,255,255,0.80)",
  text:"rgba(255,255,255,0.95)",
};
const M = "'OpenDyslexic Mono','OpenDyslexicMono','Courier New',monospace";
const MB = "'OpenDyslexic Bold','OpenDyslexic',sans-serif";

const SH=({t,c=C.accent,mt=22})=>(<div style={{display:"flex",alignItems:"center",gap:10,marginBottom:14,marginTop:mt}}><div style={{width:3,height:17,background:c}}/><span style={{color:c,fontFamily:M,fontSize:13,letterSpacing:"0.13em",textTransform:"uppercase",fontWeight:"normal"}}>{t}</span></div>);
const KV=({k,v,vc=C.text,u=""})=>(<div style={{display:"flex",justifyContent:"space-between",padding:"5px 0",borderBottom:"1px solid rgba(0,229,255,0.07)",alignItems:"baseline"}}><span style={{color:C.dim,fontFamily:M,fontSize:11}}>{k}</span><span style={{color:vc,fontFamily:M,fontSize:11}}>{v}{u&&<span style={{color:C.accent,marginLeft:4,fontSize:10}}>{u}</span>}</span></div>);
const Note=({c=C.dim,ch})=>(<div style={{marginTop:8,marginBottom:6,color:c,fontFamily:M,fontSize:10,lineHeight:1.85,padding:"8px 12px",borderLeft:`2px solid ${c}55`,background:`${c}07`,borderRadius:3}}>{ch}</div>);
const Warn=({ch})=>(<div style={{marginTop:8,color:C.yellow,fontFamily:M,fontSize:10,lineHeight:1.8,padding:"7px 12px",borderLeft:`2px solid ${C.yellow}`,background:"rgba(255,230,0,0.05)",borderRadius:3}}>⚠ {ch}</div>);
const Good=({ch})=>(<div style={{marginTop:8,color:C.green,fontFamily:M,fontSize:10,lineHeight:1.8,padding:"7px 12px",borderLeft:`2px solid ${C.green}`,background:"rgba(74,222,128,0.05)",borderRadius:3}}>✓ {ch}</div>);
const Crit=({ch})=>(<div style={{marginTop:8,color:C.red,fontFamily:M,fontSize:10,lineHeight:1.8,padding:"7px 12px",borderLeft:`2px solid ${C.red}`,background:"rgba(248,113,113,0.05)",borderRadius:3}}>✖ {ch}</div>);
function TH({cols}){return(<thead><tr>{cols.map(h=>(<th key={h} style={{padding:"6px 9px",borderBottom:`1px solid ${C.border}`,color:C.accent,textAlign:"left",fontWeight:"normal",fontSize:10,letterSpacing:"0.06em",whiteSpace:"nowrap",opacity:.85}}>{h}</th>))}</tr></thead>);}
function Grid(){return(<svg style={{position:"fixed",inset:0,width:"100%",height:"100%",pointerEvents:"none",zIndex:0}}><defs><pattern id="sg" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0L0 0 0 20" fill="none" stroke="rgba(0,229,255,0.035)" strokeWidth={0.5}/></pattern><pattern id="lg" width="100" height="100" patternUnits="userSpaceOnUse"><rect width="100" height="100" fill="url(#sg)"/><path d="M100 0L0 0 0 100" fill="none" stroke="rgba(0,229,255,0.065)" strokeWidth={1}/></pattern></defs><rect width="100%" height="100%" fill="url(#lg)"/></svg>);}

// ════════════════════════════════════════════════════════════════
//  CONSTANTS
// ════════════════════════════════════════════════════════════════
const THRUST_SINGLE  = 2900;   // g — single XRP 3660-2700KV at 6S
const THRUST_NACELLE = 5300;   // g — tandem series pair (~91% of 2×2900)
const THRUST_TOTAL   = 11250;  // g — 2 nacelles + fuselage
const DRY_G          = 3197;   // g — airframe dry (dual-EDF Rev K)
const BAT_EMPTY_G    = 410;    // g — 6S 4000mAh
const AUW_EMPTY      = DRY_G + BAT_EMPTY_G;

// ════════════════════════════════════════════════════════════════
//  ESC ASSIGNMENT TABLE
// ════════════════════════════════════════════════════════════════
const ESC_ASSIGN = [
  {id:"ESC-NAC-L-FWD", nac:"Port (L)",   pos:"Forward",  dshot:"PRU DSHOT0 / GP26", mux:"000", telem:"BLHeli32/AM32 UART", role:"Low-pressure stage — first fan in duct"},
  {id:"ESC-NAC-L-AFT", nac:"Port (L)",   pos:"Aft",      dshot:"PRU DSHOT1 / GP27", mux:"001", telem:"BLHeli32/AM32 UART", role:"High-pressure booster — second fan in duct"},
  {id:"ESC-NAC-R-FWD", nac:"Stbd (R)",   pos:"Forward",  dshot:"PRU DSHOT2 / GP28", mux:"010", telem:"BLHeli32/AM32 UART", role:"Low-pressure stage — first fan in duct"},
  {id:"ESC-NAC-R-AFT", nac:"Stbd (R)",   pos:"Aft",      dshot:"PRU DSHOT3 / GP29", mux:"011", telem:"BLHeli32/AM32 UART", role:"High-pressure booster — second fan in duct"},
  {id:"ESC-FUSE",      nac:"Fuselage",   pos:"Aft bay",  dshot:"PRU DSHOT4",        mux:"100", telem:"BLHeli32/AM32 UART", role:"Forward-flight assist / transition EDF"},
];

// ════════════════════════════════════════════════════════════════
//  FAULT TREE
// ════════════════════════════════════════════════════════════════
const FAULT_TREE = [
  {
    fault:"Single EDF failure (FWD or AFT)", sev:"DEGRADED", c:C.yellow,
    detect:"BDSHOT zero-RPM response within 3 frames (300ms) · BLHeli32 fault flag in telem frame",
    action:"DSHOT DISARM on failed ESC · surviving EDF throttle held by governor · opposite nacelle trimmed −10% throttle for yaw balance",
    thrust:`~${THRUST_SINGLE}g nacelle (${Math.round(THRUST_SINGLE/THRUST_NACELLE*100)}% of nominal)`,
    tw:`${((THRUST_SINGLE + THRUST_NACELLE + 650) / AUW_EMPTY).toFixed(2)}:1`,
    recovery:"Controlled flight maintained. Return and land. No forced emergency landing.",
  },
  {
    fault:"Single ESC overtemp (>110°C)", sev:"DERATE", c:C.orange,
    detect:"BLHeli32 serial telem temperature byte · 10Hz update · threshold ladder: 95°C→derate 20%, 110°C→single-EDF mode",
    action:"Throttle capped at 50% on hot ESC · paired EDF compensates via governor · alert to GCS",
    thrust:"Reduced nacelle output — above hover threshold",
    tw:">2.0:1 depending on derate level",
    recovery:"Reduce throttle, increase altitude to improve cooling. Return if sustained.",
  },
  {
    fault:"Both EDFs failed — single nacelle dead", sev:"EMERGENCY", c:C.red,
    detect:"Both BDSHOT channels zero-RPM + both ESC telem fault flags simultaneously",
    action:"Remaining nacelle full throttle · fuselage EDF full · nacelle tilt trimmed to balance asymmetric thrust · controlled descent initiated",
    thrust:`${THRUST_NACELLE + 650}g = 5950g`,
    tw:`${((THRUST_NACELLE + 650) / AUW_EMPTY).toFixed(2)}:1`,
    recovery:"T/W 1.64:1 — descend at controlled rate. Land at nearest safe point. GCS MAYDAY alert.",
  },
  {
    fault:"RPM delta FWD/AFT >500 RPM (matched throttle)", sev:"ALERT", c:C.purple,
    detect:"BDSHOT RPM comparison per nacelle governor · continuous",
    action:"Alert to GCS · log event · no thrust change · schedule inspection",
    thrust:"Unaffected",
    tw:`${(THRUST_TOTAL / AUW_EMPTY).toFixed(2)}:1`,
    recovery:"Inspect fan blade pitch balance and bearing condition at next service.",
  },
  {
    fault:"Current imbalance FWD/AFT >15A (matched throttle)", sev:"ALERT", c:C.teal,
    detect:"BLHeli32 serial telem current byte comparison · 10Hz",
    action:"Log event · alert GCS · flag coil inspection",
    thrust:"Unaffected unless associated RPM delta",
    tw:`${(THRUST_TOTAL / AUW_EMPTY).toFixed(2)}:1`,
    recovery:"Inspect motor windings at next service.",
  },
];

// ════════════════════════════════════════════════════════════════
//  GOVERNOR LOGIC
// ════════════════════════════════════════════════════════════════
const GOV_STATES = [
  {state:"NORMAL",      c:C.green,  fwd:"FC_THROTTLE × 1.00", aft:"FC_THROTTLE × 1.00", note:"Both EDFs at matched command. Governor PID tracks RPM_FWD ≈ RPM_AFT."},
  {state:"DERATE_FWD",  c:C.orange, fwd:"min(FC_THR, 0.5)",   aft:"FC_THROTTLE × 1.05", note:"FWD ESC overtemp. AFT ESC picks up 5% extra to maintain nacelle output."},
  {state:"DERATE_AFT",  c:C.orange, fwd:"FC_THROTTLE × 1.05", aft:"min(FC_THR, 0.5)",   note:"AFT ESC overtemp. FWD ESC compensates."},
  {state:"FAULT_FWD",   c:C.yellow, fwd:"DISARMED (0)",        aft:"FC_THROTTLE × 1.20", note:"FWD ESC/EDF failed. AFT ESC runs at 120% to recover nacelle thrust. Hard cap at ESC rating."},
  {state:"FAULT_AFT",   c:C.yellow, fwd:"FC_THROTTLE × 1.20", aft:"DISARMED (0)",        note:"AFT ESC/EDF failed. FWD ESC at 120%."},
  {state:"FAULT_BOTH",  c:C.red,    fwd:"DISARMED (0)",        aft:"DISARMED (0)",        note:"Both failed. FC switches to single-nacelle emergency mode. Opposite nacelle + fuselage carry load."},
];

// ════════════════════════════════════════════════════════════════
//  NACELLE POD DIAGRAM
// ════════════════════════════════════════════════════════════════
function NacellePodDiagram(){
  const VW=720, VH=200, OD=93.5, SC=1.85;
  const podH = OD * SC;
  const podW = 230 * SC;
  const y0 = (VH - podH) / 2;
  const x0 = 20;
  // EDF positions: FWD at 30mm in, AFT at 130mm in (each 80mm housing + 20mm gap)
  const fwdX = x0 + 30 * SC;
  const aftX = x0 + 130 * SC;
  const edfW = 80 * SC;
  const edfH = podH * 0.88;
  const edfY = y0 + podH * 0.06;
  const gapX = fwdX + edfW;
  const gapW = 20 * SC;

  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* Pod outline */}
      <rect x={x0} y={y0} width={podW} height={podH} rx={6}
        fill={`${C.orange}10`} stroke={C.orange} strokeWidth={2}/>
      <text x={x0 + podW/2} y={y0 - 8} textAnchor="middle" fill={C.orange} fontSize={8} fontFamily={M}>
        nacelle_pod_dual_80mm.stl  ·  93.5mm OD  ·  230mm length
      </text>

      {/* FWD EDF */}
      <rect x={fwdX} y={edfY} width={edfW} height={edfH} rx={4}
        fill={`${C.teal}18`} stroke={C.teal} strokeWidth={1.8}/>
      <text x={fwdX + edfW/2} y={edfY + edfH*0.42} textAnchor="middle" fill={C.teal} fontSize={8.5} fontFamily={M} fontWeight="bold">FWD EDF</text>
      <text x={fwdX + edfW/2} y={edfY + edfH*0.58} textAnchor="middle" fill={`${C.teal}80`} fontSize={7} fontFamily={M}>XRP 3660-2700KV</text>
      <text x={fwdX + edfW/2} y={edfY + edfH*0.72} textAnchor="middle" fill={`${C.teal}70`} fontSize={7} fontFamily={M}>80mm · 84A · 6S</text>

      {/* AFT EDF */}
      <rect x={aftX} y={edfY} width={edfW} height={edfH} rx={4}
        fill={`${C.purple}18`} stroke={C.purple} strokeWidth={1.8}/>
      <text x={aftX + edfW/2} y={edfY + edfH*0.42} textAnchor="middle" fill={C.purple} fontSize={8.5} fontFamily={M} fontWeight="bold">AFT EDF</text>
      <text x={aftX + edfW/2} y={edfY + edfH*0.58} textAnchor="middle" fill={`${C.purple}80`} fontSize={7} fontFamily={M}>XRP 3660-2700KV</text>
      <text x={aftX + edfW/2} y={edfY + edfH*0.72} textAnchor="middle" fill={`${C.purple}70`} fontSize={7} fontFamily={M}>80mm · 84A · 6S</text>

      {/* Flow-straightener gap */}
      <rect x={gapX} y={edfY} width={gapW} height={edfH} rx={2}
        fill={`${C.lime}10`} stroke={`${C.lime}50`} strokeWidth={1} strokeDasharray="3 2"/>
      <text x={gapX + gapW/2} y={edfY + edfH*0.45} textAnchor="middle" fill={C.lime} fontSize={6.5} fontFamily={M}>VANES</text>
      <text x={gapX + gapW/2} y={edfY + edfH*0.62} textAnchor="middle" fill={`${C.lime}70`} fontSize={6} fontFamily={M}>20mm</text>

      {/* FWD ESC label */}
      <text x={fwdX + edfW/2} y={VH - 14} textAnchor="middle" fill={C.teal} fontSize={7.5} fontFamily={M}>ESC-NAC-x-FWD · 107g</text>
      <text x={fwdX + edfW/2} y={VH - 4} textAnchor="middle" fill={`${C.teal}70`} fontSize={6.5} fontFamily={M}>on FWD bulkhead face</text>

      {/* AFT ESC label */}
      <text x={aftX + edfW/2} y={VH - 14} textAnchor="middle" fill={C.purple} fontSize={7.5} fontFamily={M}>ESC-NAC-x-AFT · 107g</text>
      <text x={aftX + edfW/2} y={VH - 4} textAnchor="middle" fill={`${C.purple}70`} fontSize={6.5} fontFamily={M}>on AFT bulkhead face</text>

      {/* Airflow arrow */}
      <defs>
        <marker id="arr" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
          <path d="M0,0 L6,3 L0,6 Z" fill={C.yellow}/>
        </marker>
      </defs>
      <line x1={x0 + 6} y1={VH/2} x2={x0 + 25*SC} y2={VH/2} stroke={C.yellow} strokeWidth={1.5} markerEnd="url(#arr)"/>
      <text x={x0 + 6} y={VH/2 - 6} fill={C.yellow} fontSize={6.5} fontFamily={M}>AIR IN</text>
      <line x1={x0 + podW - 10} y1={VH/2} x2={x0 + podW + 20} y2={VH/2} stroke={C.yellow} strokeWidth={2} markerEnd="url(#arr)"/>
      <text x={x0 + podW + 5} y={VH/2 - 6} fill={C.yellow} fontSize={6.5} fontFamily={M}>THRUST</text>

      {/* Dimension bars */}
      <line x1={x0} y1={y0 - 20} x2={x0 + podW} y2={y0 - 20} stroke={`${C.orange}50`} strokeWidth={0.7}/>
      <text x={x0 + podW/2} y={y0 - 24} textAnchor="middle" fill={`${C.orange}80`} fontSize={7} fontFamily={M}>230 mm total pod length</text>

      {/* Stage labels */}
      <text x={fwdX + edfW*0.5} y={y0 + 12} textAnchor="middle" fill={C.teal} fontSize={7} fontFamily={M} opacity={0.7}>STAGE 1 — low-pressure</text>
      <text x={aftX + edfW*0.5} y={y0 + 12} textAnchor="middle" fill={C.purple} fontSize={7} fontFamily={M} opacity={0.7}>STAGE 2 — booster</text>

      <text x={VW/2} y={14} textAnchor="middle" fill="rgba(0,229,255,0.3)" fontSize={8.5} fontFamily={M} letterSpacing="0.12em">
        DUAL 80mm EDF TANDEM SERIES — NACELLE POD CROSS-SECTION
      </text>
    </svg>
  );
}

// ════════════════════════════════════════════════════════════════
//  TELEM MUX DIAGRAM
// ════════════════════════════════════════════════════════════════
function MuxDiagram(){
  const VW=680, VH=280;
  const escColors = [C.teal, `${C.teal}b0`, C.purple, `${C.purple}b0`, C.gold];
  const escLabels = ["ESC-NAC-L-FWD","ESC-NAC-L-AFT","ESC-NAC-R-FWD","ESC-NAC-R-AFT","ESC-FUSE"];
  const muxStates = ["000","001","010","011","100"];
  const muxX = 280, muxW = 110, muxH = 220, muxY = 30;
  const uartX = 450;

  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* ESC blocks */}
      {escLabels.map((lbl,i)=>{
        const ey = 42 + i * 44;
        return(<g key={i}>
          <rect x={10} y={ey - 14} width={120} height={28} rx={3}
            fill={`${escColors[i]}22`} stroke={escColors[i]} strokeWidth={1.5}/>
          <text x={70} y={ey + 2} textAnchor="middle" fill={escColors[i]} fontSize={8} fontFamily={M} fontWeight="bold">{lbl}</text>
          <text x={70} y={ey + 12} textAnchor="middle" fill={`${escColors[i]}90`} fontSize={6.5} fontFamily={M}>TELEM TX</text>
          {/* Wire to mux */}
          <line x1={130} y1={ey} x2={muxX} y2={muxY + (i+0.5)*(muxH/5)}
            stroke={escColors[i]} strokeWidth={1.8} opacity={0.8}/>
          {/* State label */}
          <text x={210} y={ey - 3} fill={escColors[i]} fontSize={7} fontFamily={M}>{muxStates[i]}</text>
        </g>);
      })}

      {/* 74HC4051 mux block */}
      <rect x={muxX} y={muxY} width={muxW} height={muxH} rx={5}
        fill="rgba(163,230,53,0.07)" stroke={C.lime} strokeWidth={2}/>
      <text x={muxX + muxW/2} y={muxY + 18} textAnchor="middle" fill={C.lime} fontSize={9} fontFamily={M} fontWeight="bold">74HC4051</text>
      <text x={muxX + muxW/2} y={muxY + 30} textAnchor="middle" fill={`${C.lime}80`} fontSize={7} fontFamily={M}>8:1 analog mux</text>
      <text x={muxX + muxW/2} y={muxY + 41} textAnchor="middle" fill={`${C.lime}60`} fontSize={6.5} fontFamily={M}>SOIC-16 · $0.50</text>
      {/* Select lines */}
      {["S0 ← GPA6","S1 ← GPA7","S2 ← GPB1"].map((s,i)=>(
        <text key={i} x={muxX + 6} y={muxY + 60 + i * 13} fill={C.gold} fontSize={6.5} fontFamily={M}>{s}</text>
      ))}
      {/* "state 111 = RS485" at bottom */}
      <text x={muxX + muxW/2} y={muxY + muxH - 10} textAnchor="middle" fill={C.dimmer} fontSize={7} fontFamily={M}>111 → RS-485</text>

      {/* Wire from mux to UART1 RX */}
      <line x1={muxX + muxW} y1={muxY + muxH/2} x2={uartX} y2={muxY + muxH/2}
        stroke={C.accent} strokeWidth={2.5}/>

      {/* UART1 block */}
      <rect x={uartX} y={muxY + muxH/2 - 28} width={100} height={56} rx={4}
        fill={`${C.accent}10`} stroke={C.accent} strokeWidth={1.8}/>
      <text x={uartX + 50} y={muxY + muxH/2 - 10} textAnchor="middle" fill={C.accent} fontSize={9} fontFamily={M} fontWeight="bold">UART1 RX</text>
      <text x={uartX + 50} y={muxY + muxH/2 + 4} textAnchor="middle" fill={`${C.accent}80`} fontSize={7} fontFamily={M}>MCU (PB2-I AM6254)</text>
      <text x={uartX + 50} y={muxY + muxH/2 + 16} textAnchor="middle" fill={`${C.accent}60`} fontSize={6.5} fontFamily={M}>115200 8N1</text>

      {/* RS-485 bus */}
      <rect x={uartX} y={muxY + muxH/2 + 40} width={100} height={30} rx={3}
        fill="rgba(45,212,191,0.08)" stroke={C.teal} strokeWidth={1}/>
      <text x={uartX + 50} y={muxY + muxH/2 + 58} textAnchor="middle" fill={C.teal} fontSize={7.5} fontFamily={M}>RS-485 (state 111)</text>

      {/* ISO7241C note */}
      <rect x={uartX + 8} y={muxY + 4} width={84} height={24} rx={3}
        fill="rgba(163,230,53,0.07)" stroke={`${C.lime}60`} strokeWidth={1}/>
      <text x={uartX + 50} y={muxY + 14} textAnchor="middle" fill={C.lime} fontSize={7} fontFamily={M}>ISO7241C</text>
      <text x={uartX + 50} y={muxY + 23} textAnchor="middle" fill={`${C.lime}70`} fontSize={6.5} fontFamily={M}>4kV UART isolation</text>

      <text x={VW/2} y={14} textAnchor="middle" fill="rgba(0,229,255,0.25)" fontSize={8.5} fontFamily={M} letterSpacing="0.1em">
        ESC TELEM MUX — 74HC4051 8:1 · 5 ESC CHANNELS + RS-485
      </text>
      <text x={VW/2} y={VH-6} textAnchor="middle" fill="rgba(0,229,255,0.2)" fontSize={7} fontFamily={M}>
        Round-robin poll: 5 ESCs × 87µs = 435µs per full cycle · Fault detected within 3 missed frames (300ms)
      </text>
    </svg>
  );
}

// ════════════════════════════════════════════════════════════════
//  THRUST COMPARISON DIAGRAM
// ════════════════════════════════════════════════════════════════
function ThrustComparisonDiagram(){
  const VW=640, VH=220;
  const configs = [
    {label:"Rev K single EDF",  thrust:6450,  dry:2177, c:C.dimmer, fault:null},
    {label:"Dual EDF nominal",  thrust:11250, dry:3197, c:C.green,  fault:null},
    {label:"One EDF fault",     thrust:9150,  dry:3197, c:C.yellow, fault:"1 EDF down (55% nacelle)"},
    {label:"One nacelle fault", thrust:5950,  dry:3197, c:C.orange, fault:"Both nacelle EDFs down"},
  ];
  const maxT = 12000;
  const barH = 32, gap = 8, x0 = 160, barMaxW = 380;
  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {configs.map(({label,thrust,dry,c,fault},i)=>{
        const y = 30 + i * (barH + gap);
        const tw = (thrust / (dry + 410)).toFixed(2);
        const barW = thrust / maxT * barMaxW;
        return(<g key={i}>
          {/* Config label */}
          <text x={x0 - 8} y={y + barH/2 + 4} textAnchor="end" fill={c} fontSize={8.5} fontFamily={M}>{label}</text>
          {/* Thrust bar */}
          <rect x={x0} y={y} width={barW} height={barH} rx={3}
            fill={`${c}20`} stroke={c} strokeWidth={1.5}/>
          {/* T/W label */}
          <text x={x0 + barW + 6} y={y + barH/2 + 4} fill={c} fontSize={9} fontFamily={M} fontWeight="bold">
            {thrust}g  T/W {tw}
          </text>
          {fault&&<text x={x0} y={y + barH + 1} fill={`${c}80`} fontSize={6.5} fontFamily={M}>{fault}</text>}
          {/* T/W=2.0 minimum line */}
          {i===0&&<line x1={x0 + (2.0 * (dry+410)) / maxT * barMaxW} y1={20} x2={x0 + (2.0 * (dry+410)) / maxT * barMaxW} y2={VH - 20} stroke={C.red} strokeWidth={1} strokeDasharray="4 3" opacity={0.5}/>}
        </g>);
      })}
      {/* T/W=2.0 label */}
      <text x={x0 + (2.0 * (2177+410)) / maxT * barMaxW + 3} y={18} fill={C.red} fontSize={7} fontFamily={M} opacity={0.7}>T/W=2.0 (single)</text>
      <text x={VW/2} y={14} textAnchor="middle" fill="rgba(0,229,255,0.28)" fontSize={8.5} fontFamily={M} letterSpacing="0.1em">
        THRUST vs FAULT MODE — DUAL EDF Rev K · 6S 4000mAh
      </text>
    </svg>
  );
}

// ════════════════════════════════════════════════════════════════
//  TAB 1: OVERVIEW
// ════════════════════════════════════════════════════════════════
function OverviewTab(){
  const tw_nom   = (THRUST_TOTAL / AUW_EMPTY).toFixed(2);
  const tw_1edf  = ((THRUST_SINGLE * 1.55 + THRUST_NACELLE + 650) / AUW_EMPTY).toFixed(2);
  const tw_1nac  = ((THRUST_NACELLE + 650) / AUW_EMPTY).toFixed(2);
  return(<div>
    <div style={{background:"rgba(255,107,53,0.07)",border:"1px solid rgba(255,107,53,0.35)",borderRadius:6,padding:"14px 18px",marginBottom:18}}>
      <div style={{color:C.orange,fontFamily:M,fontSize:12,fontWeight:"bold",marginBottom:10}}>
        DUAL 80mm EDF TANDEM SERIES — 2 EDFS + 2 ESCS PER NACELLE · INTRA-NACELLE FAULT TOLERANCE
      </div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:18}}>
        <div>
          <KV k="EDFs per nacelle"          v="2× XRP 3660-2700KV 80mm 6S (FWD + AFT)" vc={C.orange}/>
          <KV k="Pod length"                v="230mm (vs 144mm single-EDF pod)" vc={C.yellow}/>
          <KV k="Pod OD"                    v="93.5mm — canonical silhouette unchanged" vc={C.lime}/>
          <KV k="Per-nacelle thrust (nom.)" v={`${THRUST_NACELLE}g (both EDFs, ~91% of 2×${THRUST_SINGLE}g)`} vc={C.green}/>
          <KV k="Per-nacelle thrust (1 EDF)"v={`~${THRUST_SINGLE}g (fault mode, 55% of nominal)`} vc={C.yellow}/>
          <KV k="Total hover thrust"        v={`${THRUST_TOTAL}g (${(THRUST_TOTAL/453.592).toFixed(2)} lb)`} vc={C.green}/>
        </div>
        <div>
          <KV k="Nacelle ESCs"              v="4 total (one per EDF)" vc={C.accent}/>
          <KV k="ESC model"                 v="Hobbywing Platinum V4 120A 6S"/>
          <KV k="DSHOT channels"            v="4 independent PIO outputs (GP26–GP29)" vc={C.orange}/>
          <KV k="ESC telem mux"             v="74HC4051 8:1 · 3-bit select · 5 channels" vc={C.teal}/>
          <KV k="T/W nominal"               v={`${tw_nom}:1`} vc={parseFloat(tw_nom)>=2.0?C.green:C.red}/>
          <KV k="T/W single-EDF fault"      v={`~${tw_1edf}:1`} vc={parseFloat(tw_1edf)>=2.0?C.green:C.yellow}/>
          <KV k="T/W single-nacelle fault"  v={`~${tw_1nac}:1`} vc={C.orange}/>
        </div>
      </div>
    </div>

    <SH t="Nacelle Pod — Dual EDF Tandem Cross-Section" mt={0}/>
    <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:8,marginBottom:20}}>
      <NacellePodDiagram/>
    </div>

    <SH t="Thrust vs Fault Mode" c={C.green}/>
    <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:8,marginBottom:20}}>
      <ThrustComparisonDiagram/>
    </div>

    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="Why Dual Series EDFs?" mt={0} c={C.orange}/>
        <Note c={C.orange} ch="Two axial EDFs in series in a single duct creates a 2-stage compression system. Stage 1 (FWD) pressurizes the incoming air; Stage 2 (AFT) re-accelerates the already-pressurized flow. Combined thrust is ~91% of arithmetic sum due to inter-stage pressure recovery losses. This is superior to two separate smaller ducts for the same nacelle OD."/>
        <Note c={C.teal} ch="Independent ESCs mean the nacelle continues producing thrust even if one motor, its ESC, or its power lead fails. At fault T/W of 2.29:1 (single EDF out), the aircraft remains well above the 2.0:1 minimum for controlled flight. No landing is forced — return and land at pilot discretion."/>
        <Note c={C.lime} ch="Canonical nacelle silhouette is preserved: OD stays at 93.5mm. Only pod length increases from 144mm to 230mm, which is within the canonical nacelle aspect ratio and not visible from typical viewer angles."/>
      </div>
      <div>
        <SH t="Series Fan Aerodynamics" mt={0} c={C.purple}/>
        <Note c={C.purple} ch="Flow-straightener vane set (6 vanes, 8mm chord, printed integral to pod) removes the tangential velocity component from Stage 1 exhaust before Stage 2 inlet. Without straightener, Stage 2 sees swirl angle reducing effective angle-of-attack on its blades and thrust recovery drops to ~80%. With straightener: ~91%."/>
        <Note c={C.yellow} ch="Fan pitch matching: both XRP units must be within ±0.5° blade pitch. Order from the same production batch where possible. Verify with a pitch gauge before commissioning. Mismatched pitch causes unequal shaft load and vibration."/>
        <Good ch="Power wiring: FWD and AFT ESCs draw from independent XT30 pigtails at the PDB. A hard short on one ESC phase cannot propagate to the other. Use separate poly fuses (100A each) per ESC at the PDB."/>
      </div>
    </div>
  </div>);
}

// ════════════════════════════════════════════════════════════════
//  TAB 2: ESC ASSIGNMENT
// ════════════════════════════════════════════════════════════════
function ESCAssignTab(){
  return(<div>
    <SH t="ESC ID to Physical Assignment" mt={0} c={C.teal}/>
    <div style={{overflowX:"auto",marginBottom:20}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["ESC ID","NACELLE","POSITION","DSHOT GPIO","MUX STATE","TELEM SOURCE","ROLE"]}/>
        <tbody>{ESC_ASSIGN.map((e,i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
            <td style={{padding:"5px 9px",color:C.yellow,fontFamily:"'Courier New',monospace",fontWeight:"bold",whiteSpace:"nowrap"}}>{e.id}</td>
            <td style={{padding:"5px 9px",color:C.accent}}>{e.nac}</td>
            <td style={{padding:"5px 9px",color:i<4?C.orange:C.gold}}>{e.pos}</td>
            <td style={{padding:"5px 9px",color:C.orange,fontFamily:"'Courier New',monospace",fontSize:9}}>{e.dshot}</td>
            <td style={{padding:"5px 9px",color:C.teal,fontFamily:"'Courier New',monospace",fontWeight:"bold"}}>{e.mux}</td>
            <td style={{padding:"5px 9px",color:C.lime,fontSize:9}}>{e.telem}</td>
            <td style={{padding:"5px 9px",color:C.dim,fontSize:9}}>{e.role}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>

    <SH t="ESC Telemetry Mux — 74HC4051" c={C.teal}/>
    <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:8,marginBottom:18}}>
      <MuxDiagram/>
    </div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <KV k="IC"             v="74HC4051 — single 8:1 analog mux" vc={C.yellow}/>
        <KV k="Package"        v="SOIC-16 · 9.9×3.9mm"/>
        <KV k="Supply"         v="2–6V — 3.3V logic compatible"/>
        <KV k="Select bits"    v="S0=GPA6 · S1=GPA7 · S2=GPB1 (MCP23017)"/>
        <KV k="State 000–011"  v="ESC-NAC-L-FWD/AFT · R-FWD/AFT" vc={C.orange}/>
        <KV k="State 100"      v="ESC-Fuse telem" vc={C.gold}/>
        <KV k="State 111"      v="RS-485 / debug UART (default)" vc={C.teal}/>
        <KV k="States 101–110" v="Spare — available for future"/>
        <KV k="Switch time"    v="<10ns — transparent to 115200 UART"/>
        <KV k="Poll cycle"     v="5 ESCs × 87µs = 435µs round-trip"/>
        <KV k="Fault detect"   v="3 missed frames = 300ms timeout"/>
      </div>
      <div>
        <Note c={C.teal} ch="The 74HC4051 replaces the 74HC4052 in the same SOIC-16 footprint. Only one additional select pin (GPB1 on MCP23017) is required. Existing UART1 RX signal path and ISO7241C isolation are unchanged."/>
        <Note c={C.orange} ch="WS2812 nav light chain (previously on GP29 / PIO0-SM3) moves to PCA9685 16-channel I²C PWM driver on the SENSORHAT-1 I²C bus. MCP23017 GPB2 drives the OE̅ pin. PCA9685 at address 0x40 generates 50Hz PWM for each LED data line via level-shifted output. This frees GP29 / PIO0-SM3 for ESC-NAC-R-AFT BDSHOT."/>
        <Good ch="All 4 nacelle DSHOT channels are independent bidirectional (BDSHOT). RPM from each EDF is sampled every DSHOT frame. Governor receives 4 real-time RPM streams and adjusts throttle commands accordingly."/>
      </div>
    </div>
  </div>);
}

// ════════════════════════════════════════════════════════════════
//  TAB 3: FAULT TOLERANCE
// ════════════════════════════════════════════════════════════════
function FaultToleranceTab(){
  return(<div>
    <SH t="Fault Tree — Per-Nacelle EDF / ESC Faults" mt={0} c={C.red}/>
    <div style={{overflowX:"auto",marginBottom:20}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["FAULT","SEVERITY","DETECTION","FC ACTION","NACELLE THRUST","T/W","RECOVERY"]}/>
        <tbody>{FAULT_TREE.map((f,i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent",verticalAlign:"top"}}>
            <td style={{padding:"6px 9px",color:f.c,fontWeight:"bold",fontSize:10,maxWidth:140}}>{f.fault}</td>
            <td style={{padding:"6px 9px"}}><span style={{color:f.c,border:`1px solid ${f.c}55`,padding:"1px 6px",borderRadius:2,fontSize:9,whiteSpace:"nowrap"}}>{f.sev}</span></td>
            <td style={{padding:"6px 9px",color:C.dim,fontSize:8.5,maxWidth:160,lineHeight:1.5}}>{f.detect}</td>
            <td style={{padding:"6px 9px",color:C.text,fontSize:9,maxWidth:180,lineHeight:1.5}}>{f.action}</td>
            <td style={{padding:"6px 9px",color:f.c,fontWeight:"bold",whiteSpace:"nowrap"}}>{f.thrust}</td>
            <td style={{padding:"6px 9px",color:parseFloat(f.tw)>=2.0?C.green:parseFloat(f.tw)>=1.5?C.yellow:C.red,fontWeight:"bold",whiteSpace:"nowrap"}}>{f.tw}</td>
            <td style={{padding:"6px 9px",color:C.dim,fontSize:8.5,maxWidth:160,lineHeight:1.5}}>{f.recovery}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>

    <SH t="Per-Nacelle Governor State Machine" c={C.purple}/>
    <div style={{overflowX:"auto",marginBottom:20}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["STATE","FWD ESC COMMAND","AFT ESC COMMAND","TRIGGER / CONDITION"]}/>
        <tbody>{GOV_STATES.map((g,i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
            <td style={{padding:"5px 9px"}}><span style={{color:g.c,border:`1px solid ${g.c}55`,padding:"1px 6px",borderRadius:2,fontSize:9,fontWeight:"bold"}}>{g.state}</span></td>
            <td style={{padding:"5px 9px",color:g.fwd.includes("DISARMED")?C.red:g.fwd.includes("min(")?C.orange:C.green,fontFamily:"'Courier New',monospace",fontSize:9}}>{g.fwd}</td>
            <td style={{padding:"5px 9px",color:g.aft.includes("DISARMED")?C.red:g.aft.includes("min(")?C.orange:C.green,fontFamily:"'Courier New',monospace",fontSize:9}}>{g.aft}</td>
            <td style={{padding:"5px 9px",color:C.dim,fontSize:9,lineHeight:1.5}}>{g.note}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>

    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="Fault Latch Policy" mt={0} c={C.red}/>
        <Note c={C.red} ch="ESC faults are LATCHED. Once an ESC fault is detected and the ESC is disarmed, it remains disarmed for the rest of the flight. No in-flight auto-reset. Rationale: an ESC fault during a maneuver followed by spontaneous re-arm creates an unpredictable thrust transient that can destabilize the airframe."/>
        <Note c={C.orange} ch="Fault recovery requires: (1) aircraft landed, (2) battery removed and reinserted, (3) GCS explicit fault-clear command on the ground. This prevents accidental re-arm in air after a momentary desync."/>
        <Good ch="Fault ID, ESC temperature, last RPM, flight phase, and battery voltage at fault time are logged to Cape-B microSD immediately on fault detection via CAN FD FAULT_EVENT message."/>
      </div>
      <div>
        <SH t="Asymmetric Thrust Compensation" mt={0} c={C.yellow}/>
        <Note c={C.yellow} ch="When one EDF fails in a nacelle, that nacelle produces less thrust than the other. The FC compensates by: (1) trimming the healthy nacelle throttle down ~10%, (2) adjusting tilt angle to keep thrust vector aligned with CG, (3) increasing fuselage EDF output to maintain altitude. Net effect: yaw trim change <3°, altitude loss <0.5m at fault onset."/>
        <Note c={C.teal} ch="When an entire nacelle fails (both EDFs down), the remaining nacelle is at full throttle and the aircraft must yaw to align thrust axis with CG. The FC applies differential tilt to the surviving nacelle within ±5° to compensate for yaw moment. Fuselage EDF provides remaining lift margin. Descent rate target: <2 m/s."/>
      </div>
    </div>
    <Warn ch="Do NOT fly over crowds or in confined spaces without validating the single-EDF fault recovery on a test stand or open area first. The fault tolerance is designed for controlled field conditions, not urban/critical environments."/>
  </div>);
}

// ════════════════════════════════════════════════════════════════
//  TAB 4: POWER WIRING
// ════════════════════════════════════════════════════════════════
function PowerWiringTab(){
  const WIRING = [
    {ref:"WIRE-BAT-MAIN",  desc:"Main battery bus",           spec:"4 AWG silicone · XT90-S",     note:"Upgrade from 8 AWG — handles 350A peak (2×168A nacelle + 30A fuse)"},
    {ref:"WIRE-NAC-L-FWD", desc:"Port nacelle FWD ESC power", spec:"12 AWG silicone · XT30 · 80mm",note:"Independent from AFT — FWD short cannot pull down AFT bus"},
    {ref:"WIRE-NAC-L-AFT", desc:"Port nacelle AFT ESC power",  spec:"12 AWG silicone · XT30 · 80mm",note:"Independent from FWD"},
    {ref:"WIRE-NAC-R-FWD", desc:"Stbd nacelle FWD ESC power", spec:"12 AWG silicone · XT30 · 80mm",note:""},
    {ref:"WIRE-NAC-R-AFT", desc:"Stbd nacelle AFT ESC power",  spec:"12 AWG silicone · XT30 · 80mm",note:""},
    {ref:"WIRE-PHASE-NAC", desc:"ESC → motor phase leads (×4)", spec:"14 AWG silicone · 80mm × 3", note:"4 ESCs × 3 phases = 12 phase leads inside nacelle pod"},
    {ref:"FUSE-NAC-L",     desc:"Port nacelle poly fuse pair", spec:"2× 100A poly fuse (per ESC)",   note:"At PDB per-nacelle distribution point — not series, parallel"},
    {ref:"FUSE-NAC-R",     desc:"Stbd nacelle poly fuse pair", spec:"2× 100A poly fuse (per ESC)",   note:""},
    {ref:"CAP-NAC-BULK",   desc:"Bulk capacitor per nacelle",  spec:"2× 1000µF 25V electrolytic",    note:"At ESC power input on inter-EDF bulkhead — absorbs current transients"},
  ];
  return(<div>
    <SH t="Power Architecture — Dual-EDF Nacelle" mt={0} c={C.gold}/>
    <div style={{background:"rgba(251,191,36,0.06)",border:`1px solid ${C.gold}44`,borderRadius:4,padding:"10px 14px",marginBottom:14,fontFamily:M,fontSize:11,color:C.dim,lineHeight:1.8}}>
      <span style={{color:C.gold,fontWeight:"bold"}}>Key constraint:</span> Each nacelle now draws up to <span style={{color:C.orange}}>168A peak</span> (2× 84A ESCs). Total aircraft peak current: <span style={{color:C.red}}>~350A</span> (2 nacelles + fuselage). Main bus must be upgraded to <span style={{color:C.yellow}}>4 AWG silicone + 300A copper bus bar</span>. FWD and AFT ESCs in each nacelle draw from <span style={{color:C.lime}}>independent XT30 pigtails</span> for fault isolation.
    </div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:20,marginBottom:14}}>
      <div>
        <KV k="Battery → PDB"         v="4 AWG · XT90-S connector · <100mm" vc={C.gold}/>
        <KV k="PDB → each nacelle"    v="2× 12 AWG XT30 pigtails per nacelle"/>
        <KV k="Nacelle peak current"  v="168A (2× 84A)" vc={C.orange}/>
        <KV k="Total aircraft peak"   v="~350A" vc={C.red}/>
        <KV k="Fuses per ESC"         v="100A poly fuse at PDB output" vc={C.yellow}/>
        <KV k="Phase wires"           v="14 AWG · 80mm · 12 total (4 ESCs × 3 phase)" vc={C.teal}/>
        <KV k="Bulk cap per nacelle"  v="2× 1000µF 25V at ESC inputs"/>
      </div>
      <div>
        <Note c={C.orange} ch="Independent power feeds are the primary electrical fault-containment mechanism. A dead short in the FWD ESC output stage draws on the FWD poly fuse only — the AFT ESC (on its own XT30 and fuse) is unaffected and continues providing thrust."/>
        <Note c={C.yellow} ch="The 100A poly fuse self-resets. This is intentional — at 84A normal draw, the fuse margin is 19%. Only a genuine fault (stall, crash, winding short) triggers the fuse. During normal flight, neither fuse ever trips."/>
      </div>
    </div>
    <SH t="Wiring BOM — Dual EDF Power" c={C.gold}/>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["REF","DESCRIPTION","SPEC","NOTES"]}/>
        <tbody>{WIRING.map((w,i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent",verticalAlign:"top"}}>
            <td style={{padding:"5px 9px",color:C.yellow,whiteSpace:"nowrap",fontFamily:"'Courier New',monospace",fontSize:9}}>{w.ref}</td>
            <td style={{padding:"5px 9px",color:C.text}}>{w.desc}</td>
            <td style={{padding:"5px 9px",color:C.lime,fontSize:9,whiteSpace:"nowrap"}}>{w.spec}</td>
            <td style={{padding:"5px 9px",color:C.dim,fontSize:8.5}}>{w.note}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
    <Crit ch="Do NOT use a single shared XT60 or XT90 to power both FWD and AFT ESCs in a nacelle from one fuse — this defeats the fault isolation. Each ESC MUST have its own fused feed from the PDB."/>
    <Good ch="Use a dedicated 2-position bus bar per nacelle (one stud per ESC) rather than pigtail-to-pigtail chaining. This minimizes resistive drop and ensures equal impedance to both ESCs."/>
  </div>);
}

// ════════════════════════════════════════════════════════════════
//  TAB 5: BOM DELTA
// ════════════════════════════════════════════════════════════════
const BOM_DUAL_EDF = [
  {cat:"EDF",     qty:2, ref:"EDF-ADD",       part:"XRP 3660-2700KV 80mm EDF (added)",               pkg:"80mm housing",       est:"$65ea", col:C.orange, note:"2 additional EDFs — brings total to 4 nacelle EDFs (2 per nacelle)"},
  {cat:"ESC",     qty:2, ref:"ESC-NAC-ADD",   part:"Hobbywing Platinum V4 120A 6S (added)",           pkg:"—",                  est:"$55ea", col:C.teal,   note:"2 additional ESCs — brings total to 4 nacelle ESCs (one per EDF)"},
  {cat:"POD",     qty:2, ref:"NAC-POD-DUAL",  part:"nacelle_pod_dual_80mm.stl (230mm tandem pod)",    pkg:"PETG print",         est:"$3ea",  col:C.lime,   note:"Replaces nacelle_pod_80mm.stl. 93.5mm OD unchanged."},
  {cat:"Mux",     qty:2, ref:"U_MUX_4051",    part:"74HC4051 8:1 analog mux (replaces 74HC4052)",    pkg:"SOIC-16",            est:"$0.50ea",col:C.teal,  note:"One additional select pin (MCP23017 GPB1). Same footprint as 74HC4052."},
  {cat:"PWM-IC",  qty:2, ref:"U_PCA9685",     part:"PCA9685 16-ch I²C PWM (nav lights)",             pkg:"SOIC-28",            est:"$1.10ea",col:C.purple,note:"Frees GP29 for 4th nacelle ESC DSHOT. Nav lights now I²C PWM vs PIO."},
  {cat:"Wiring",  qty:1, ref:"WIRE-4AWG",     part:"4 AWG silicone + 300A bus bar upgrade",          pkg:"—",                  est:"$18",   col:C.gold,   note:"Main bus upgrade for 350A peak. Replaces 8 AWG."},
  {cat:"Wiring",  qty:4, ref:"WIRE-XT30-NAC", part:"XT30 pigtail + 12 AWG 80mm per ESC power feed", pkg:"—",                  est:"$1.50ea",col:C.gold,  note:"2 per nacelle — independent power feeds for FWD/AFT ESC fault isolation"},
  {cat:"Fuse",    qty:4, ref:"FUSE-100A",     part:"100A poly fuse (per ESC at PDB)",                pkg:"—",                  est:"$0.80ea",col:C.yellow,note:"One per ESC — 4 total nacelle fuses. FWD/AFT independent."},
  {cat:"Cap",     qty:4, ref:"CAP-1000U",     part:"1000µF 25V electrolytic bulk cap at ESC input",  pkg:"Radial through-hole", est:"$0.60ea",col:C.teal, note:"2 per nacelle (one per ESC) — absorbs current transients at commutation"},
  {cat:"Conn",    qty:2, ref:"J_ESC_TELEM_5", part:"JST-GH 3-pin ESC telem connector (added ×2)",   pkg:"SMD",                est:"$0.55ea",col:C.orange,note:"Brings total to 5 ESC telem connectors per SENSORHAT-1"},
];
const BOM_CATS=["EDF","ESC","POD","Mux","PWM-IC","Wiring","Fuse","Cap","Conn"];
const CAT_COL={EDF:C.orange,ESC:C.teal,POD:C.lime,Mux:C.teal,"PWM-IC":C.purple,Wiring:C.gold,Fuse:C.yellow,Cap:C.teal,Conn:C.orange};

function BOMDeltaTab(){
  const [cf,setCf]=useState("All");
  const rows=cf==="All"?BOM_DUAL_EDF:BOM_DUAL_EDF.filter(b=>b.cat===cf);
  const totalCost=BOM_DUAL_EDF.reduce((s,b)=>{const u=parseFloat(b.est.replace("$","").replace("ea","").replace("~","").split(" ")[0])||0;return s+b.qty*u;},0);
  return(<div>
    <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:12,marginBottom:16}}>
      {[
        {l:"Additional parts cost",v:`~$${totalCost.toFixed(0)}`,c:C.yellow},
        {l:"Added dry mass",v:"+1020g",c:C.orange},
        {l:"Added thrust",v:"+4800g (+74%)",c:C.green},
      ].map((s,i)=>(
        <div key={i} style={{padding:"10px 12px",border:`1px solid ${s.c}44`,background:`${s.c}07`,borderRadius:4}}>
          <div style={{color:C.dim,fontFamily:M,fontSize:9,marginBottom:3}}>{s.l}</div>
          <div style={{color:s.c,fontFamily:M,fontSize:20,fontWeight:"bold"}}>{s.v}</div>
        </div>
      ))}
    </div>
    <div style={{display:"flex",gap:5,flexWrap:"wrap",marginBottom:12}}>
      {["All",...BOM_CATS].map(c=>(<button key={c} onClick={()=>setCf(c)} style={{background:cf===c?`${CAT_COL[c]||C.accent}20`:"transparent",border:`1px solid ${cf===c?CAT_COL[c]||C.accent:"rgba(0,229,255,0.14)"}`,color:cf===c?CAT_COL[c]||C.accent:C.dimmer,padding:"3px 10px",fontFamily:M,fontSize:9,cursor:"pointer",borderRadius:2}}>{c}</button>))}
    </div>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["CAT","QTY","REF","PART","PKG","UNIT COST","NOTES"]}/>
        <tbody>{rows.map((b,i)=>(<tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.02)":"transparent",verticalAlign:"top"}}>
          <td style={{padding:"5px 8px"}}><span style={{color:CAT_COL[b.cat]||b.col,border:`1px solid ${CAT_COL[b.cat]||b.col}40`,padding:"1px 5px",borderRadius:2,fontSize:9,whiteSpace:"nowrap"}}>{b.cat}</span></td>
          <td style={{padding:"5px 8px",color:C.accent,fontWeight:"bold",textAlign:"center"}}>{b.qty}</td>
          <td style={{padding:"5px 8px",color:C.yellow,fontSize:9,whiteSpace:"nowrap"}}>{b.ref}</td>
          <td style={{padding:"5px 8px",color:C.text}}>{b.part}</td>
          <td style={{padding:"5px 8px",color:C.dimmer,whiteSpace:"nowrap",fontSize:9}}>{b.pkg}</td>
          <td style={{padding:"5px 8px",color:C.green,fontWeight:"bold",whiteSpace:"nowrap"}}>{b.est}</td>
          <td style={{padding:"5px 8px",color:C.dim,fontSize:9}}>{b.note}</td>
        </tr>))}</tbody>
      </table>
    </div>
    <Note c={C.dim} ch="Net cost delta for dual-EDF upgrade: ~$280–320 per aircraft (dominated by 2× EDFs at ~$130 and 2× ESCs at ~$110). Mass penalty: +1020g. Thrust gain: +4800g (+74%). T/W improves from 2.49:1 to 3.12:1 empty. Single-EDF fault T/W: 2.29:1 — above minimum 2.0:1 at all times except complete nacelle loss (1.65:1 — controlled descent)."/>
  </div>);
}

// ════════════════════════════════════════════════════════════════
//  APP
// ════════════════════════════════════════════════════════════════
const TABS = [
  {label:"Overview",      value:"overview"},
  {label:"ESC Assignment",value:"esc_assign"},
  {label:"Fault Tolerance",value:"fault"},
  {label:"Power Wiring",  value:"power"},
  {label:"BOM Delta",     value:"bom"},
];
_ODFontLoader();
export default function App(){
  const [tab,setTab]=useState("overview");
  const tw_nom = (THRUST_TOTAL / AUW_EMPTY).toFixed(2);
  return(<div style={{minHeight:"100vh",background:C.bg,color:C.text,fontFamily:M}}>
    <Grid/>
    <div style={{background:"rgba(163,230,53,0.06)",borderBottom:"1px solid rgba(163,230,53,0.2)",padding:"5px 24px",fontFamily:M,fontSize:8,color:"rgba(163,230,53,0.75)",lineHeight:1.7}}>
      © 2026 Steve Griffing, PE(CSE) [Control Systems Engineering], CISSP-ISSEP, CPP · CC BY 4.0
      · Hull: Peter Farell CC BY 4.0 · Nozzle: BamJr CC BY 4.0
      · Visual inspiration: Firefly/Serenity © Joss Whedon/Mutant Enemy/Universal — Fan engineering work
    </div>
    <div style={{position:"relative",zIndex:1,borderBottom:`1px solid ${C.border}`,padding:"14px 24px 12px"}}>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",flexWrap:"wrap",gap:12}}>
        <div>
          <div style={{color:C.orange,fontSize:9,letterSpacing:"0.2em",marginBottom:4}}>
            SERENITY TILTROTOR · DUAL 80mm 6S EDF PER NACELLE · 4× ESC TELEMETRY · FAULT TOLERANCE
          </div>
          <h1 style={{margin:0,fontSize:18,fontWeight:"normal",color:C.text,letterSpacing:"0.07em",fontFamily:MB}}>
            DUAL-EDF NACELLE — ESC TELEMETRY + FAULT TOLERANCE</h1>
          <div style={{color:"rgba(0,229,255,0.6)",fontSize:10,marginTop:3,fontFamily:M}}>
            2× XRP 3660-2700KV 80mm per nacelle · 4× HW Platinum V4 120A ESC · 74HC4051 8:1 mux · BDSHOT × 4 · {THRUST_TOTAL}g total thrust
          </div>
        </div>
        <div style={{textAlign:"right",fontFamily:M}}>
          <div style={{color:C.orange,fontSize:13,fontWeight:"bold"}}>{THRUST_NACELLE}g per nacelle · {THRUST_TOTAL}g total</div>
          <div style={{color:C.green,fontSize:11,marginTop:2}}>T/W {tw_nom}:1 nominal</div>
          <div style={{color:C.yellow,fontSize:10,marginTop:2}}>Single-EDF fault T/W {((THRUST_SINGLE*1.55+THRUST_NACELLE+650)/AUW_EMPTY).toFixed(2)}:1</div>
        </div>
      </div>
      <div style={{display:"flex",gap:2,marginTop:12,flexWrap:"wrap"}}>
        {TABS.map(t=>(<button key={t.value} onClick={()=>setTab(t.value)} style={{
          background:tab===t.value?"rgba(0,229,255,0.09)":"transparent",
          border:`1px solid ${tab===t.value?C.accent:"rgba(0,229,255,0.12)"}`,
          color:tab===t.value?C.accent:C.dimmer,padding:"4px 12px",fontFamily:M,fontSize:9,
          cursor:"pointer",letterSpacing:"0.06em",transition:"all 0.12s"}}>{t.label}</button>))}
      </div>
    </div>
    <div style={{position:"relative",zIndex:1,padding:"20px 24px",maxWidth:1060,margin:"0 auto"}}>
      {tab==="overview"   && <OverviewTab/>}
      {tab==="esc_assign" && <ESCAssignTab/>}
      {tab==="fault"      && <FaultToleranceTab/>}
      {tab==="power"      && <PowerWiringTab/>}
      {tab==="bom"        && <BOMDeltaTab/>}
    </div>
  </div>);
}
