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
      font-family: 'OpenDyslexic Mono','OpenDyslexicMono','Courier New',monospace !important;
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
//  SVG DIAGRAM 1 — 3-LEVEL CONTROL HIERARCHY BLOCK DIAGRAM
// ════════════════════════════════════════════════════════════════
function ControlHierarchyDiagram(){
  const VW=780, VH=340;
  // Arrow marker
  const arr = <defs>
    <marker id="arw" markerWidth="7" markerHeight="7" refX="5" refY="3.5" orient="auto">
      <path d="M0,0 L7,3.5 L0,7 Z" fill={C.accent}/>
    </marker>
    <marker id="arwO" markerWidth="7" markerHeight="7" refX="5" refY="3.5" orient="auto">
      <path d="M0,0 L7,3.5 L0,7 Z" fill={C.orange}/>
    </marker>
    <marker id="arwG" markerWidth="7" markerHeight="7" refX="5" refY="3.5" orient="auto">
      <path d="M0,0 L7,3.5 L0,7 Z" fill={C.green}/>
    </marker>
    <marker id="arwY" markerWidth="7" markerHeight="7" refX="5" refY="3.5" orient="auto">
      <path d="M0,0 L7,3.5 L0,7 Z" fill={C.yellow}/>
    </marker>
  </defs>;

  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {arr}

      {/* Title */}
      <text x={VW/2} y={16} textAnchor="middle" fill="rgba(0,229,255,0.3)" fontSize={8.5} fontFamily={M} letterSpacing="0.12em">
        SERENITY NACELLE PID GOVERNOR — 3-LEVEL CONTROL HIERARCHY
      </text>

      {/* ─── LEVEL 1: FC ATTITUDE LOOP ─── */}
      <rect x={10} y={30} width={140} height={58} rx={4}
        fill="rgba(192,132,252,0.10)" stroke={C.purple} strokeWidth={1.8}/>
      <text x={80} y={47} textAnchor="middle" fill={C.purple} fontSize={9} fontFamily={M} fontWeight="bold">FC ATTITUDE LOOP</text>
      <text x={80} y={59} textAnchor="middle" fill={`${C.purple}90`} fontSize={7.5} fontFamily={M}>ArduPilot/PX4</text>
      <text x={80} y={71} textAnchor="middle" fill={`${C.purple}70`} fontSize={7} fontFamily={M}>50 Hz attitude PID</text>
      <text x={80} y={82} textAnchor="middle" fill={`${C.purple}60`} fontSize={7} fontFamily={M}>roll · pitch · yaw · throttle</text>

      {/* FC → Governor arrow */}
      <line x1={150} y1={59} x2={196} y2={59} stroke={C.accent} strokeWidth={2} markerEnd="url(#arw)"/>
      <text x={173} y={55} textAnchor="middle" fill={C.accent} fontSize={7} fontFamily={M}>throttle_sp</text>
      <text x={173} y={69} textAnchor="middle" fill={`${C.accent}60`} fontSize={6.5} fontFamily={M}>tilt_cmd</text>

      {/* ─── LEVEL 2: NACELLE GOVERNOR (L + R) ─── */}
      {/* Port */}
      <rect x={200} y={28} width={148} height={64} rx={4}
        fill="rgba(0,229,255,0.07)" stroke={C.accent} strokeWidth={2}/>
      <text x={274} y={44} textAnchor="middle" fill={C.accent} fontSize={9} fontFamily={M} fontWeight="bold">PORT NACELLE GOV</text>
      <text x={274} y={56} textAnchor="middle" fill={`${C.accent}80`} fontSize={7.5} fontFamily={M}>M4F @ 500 Hz</text>
      <text x={274} y={67} textAnchor="middle" fill={`${C.accent}70`} fontSize={7} fontFamily={M}>equalization PID</text>
      <text x={274} y={78} textAnchor="middle" fill={`${C.accent}60`} fontSize={7} fontFamily={M}>Kp_eq=0.0001 Ki_eq=3e-6</text>
      <text x={274} y={88} textAnchor="middle" fill={C.orange} fontSize={7} fontFamily={M}>AFT bias +2% velocity deficit</text>

      {/* Stbd */}
      <rect x={200} y={112} width={148} height={64} rx={4}
        fill="rgba(0,229,255,0.07)" stroke={`${C.accent}80`} strokeWidth={1.5} strokeDasharray="5 2"/>
      <text x={274} y={128} textAnchor="middle" fill={`${C.accent}cc`} fontSize={9} fontFamily={M} fontWeight="bold">STBD NACELLE GOV</text>
      <text x={274} y={140} textAnchor="middle" fill={`${C.accent}70`} fontSize={7.5} fontFamily={M}>M4F @ 500 Hz</text>
      <text x={274} y={151} textAnchor="middle" fill={`${C.accent}60`} fontSize={7} fontFamily={M}>equalization PID</text>
      <text x={274} y={162} textAnchor="middle" fill={`${C.accent}50`} fontSize={7} fontFamily={M}>Kp_eq=0.0001 Ki_eq=3e-6</text>
      <text x={274} y={172} textAnchor="middle" fill={C.orange} fontSize={7} fontFamily={M} opacity={0.8}>AFT bias +2% velocity deficit</text>

      {/* FC to stbd governor */}
      <line x1={150} y1={70} x2={182} y2={70} stroke={C.accent} strokeWidth={1.2} opacity={0.5}/>
      <line x1={182} y1={70} x2={182} y2={144} stroke={C.accent} strokeWidth={1.2} opacity={0.5}/>
      <line x1={182} y1={144} x2={200} y2={144} stroke={C.accent} strokeWidth={1.2} opacity={0.5} markerEnd="url(#arw)"/>

      {/* Governor → EDF PID arrows (Port) */}
      <line x1={348} y1={47} x2={394} y2={47} stroke={C.teal} strokeWidth={1.8} markerEnd="url(#arwG)"/>
      <text x={371} y={43} textAnchor="middle" fill={C.teal} fontSize={6.5} fontFamily={M}>RPM_sp_FWD</text>
      <line x1={348} y1={75} x2={394} y2={75} stroke={C.purple} strokeWidth={1.8} markerEnd="url(#arwG)"/>
      <text x={371} y={71} textAnchor="middle" fill={C.purple} fontSize={6.5} fontFamily={M}>RPM_sp_AFT</text>

      {/* Governor → EDF PID arrows (Stbd) */}
      <line x1={348} y1={131} x2={394} y2={131} stroke={C.teal} strokeWidth={1.4} strokeDasharray="4 2" markerEnd="url(#arwG)" opacity={0.7}/>
      <text x={371} y={127} textAnchor="middle" fill={C.teal} fontSize={6.5} fontFamily={M} opacity={0.7}>RPM_sp_FWD</text>
      <line x1={348} y1={159} x2={394} y2={159} stroke={C.purple} strokeWidth={1.4} strokeDasharray="4 2" markerEnd="url(#arwG)" opacity={0.7}/>
      <text x={371} y={155} textAnchor="middle" fill={C.purple} fontSize={6.5} fontFamily={M} opacity={0.7}>RPM_sp_AFT</text>

      {/* ─── LEVEL 3: PER-EDF PID LOOPS ─── */}
      {/* Port FWD */}
      <rect x={398} y={28} width={126} height={56} rx={4}
        fill="rgba(45,212,191,0.09)" stroke={C.teal} strokeWidth={1.8}/>
      <text x={461} y={44} textAnchor="middle" fill={C.teal} fontSize={9} fontFamily={M} fontWeight="bold">EDF-NAC-L-FWD</text>
      <text x={461} y={55} textAnchor="middle" fill={`${C.teal}80`} fontSize={7} fontFamily={M}>RPM PID · Kp=3e-4</text>
      <text x={461} y={65} textAnchor="middle" fill={`${C.teal}70`} fontSize={7} fontFamily={M}>Ki=1e-5 · Kd=8e-5</text>
      <text x={461} y={75} textAnchor="middle" fill={C.yellow} fontSize={7} fontFamily={M}>current lim 80A/105A</text>

      {/* Port AFT */}
      <rect x={398} y={94} width={126} height={56} rx={4}
        fill="rgba(192,132,252,0.09)" stroke={C.purple} strokeWidth={1.8}/>
      <text x={461} y={110} textAnchor="middle" fill={C.purple} fontSize={9} fontFamily={M} fontWeight="bold">EDF-NAC-L-AFT</text>
      <text x={461} y={121} textAnchor="middle" fill={`${C.purple}80`} fontSize={7} fontFamily={M}>RPM PID · Kp=3e-4</text>
      <text x={461} y={131} textAnchor="middle" fill={`${C.purple}70`} fontSize={7} fontFamily={M}>Ki=1e-5 · Kd=8e-5</text>
      <text x={461} y={141} textAnchor="middle" fill={C.yellow} fontSize={7} fontFamily={M}>thermal derate 85°–110°C</text>

      {/* Stbd FWD */}
      <rect x={398} y={165} width={126} height={56} rx={4}
        fill="rgba(45,212,191,0.05)" stroke={`${C.teal}80`} strokeWidth={1.4} strokeDasharray="5 2"/>
      <text x={461} y={181} textAnchor="middle" fill={`${C.teal}cc`} fontSize={9} fontFamily={M} fontWeight="bold">EDF-NAC-R-FWD</text>
      <text x={461} y={192} textAnchor="middle" fill={`${C.teal}70`} fontSize={7} fontFamily={M}>RPM PID · Kp=3e-4</text>
      <text x={461} y={202} textAnchor="middle" fill={`${C.teal}60`} fontSize={7} fontFamily={M}>Ki=1e-5 · Kd=8e-5</text>
      <text x={461} y={212} textAnchor="middle" fill={C.yellow} fontSize={7} fontFamily={M} opacity={0.7}>current lim 80A/105A</text>

      {/* Stbd AFT */}
      <rect x={398} y={231} width={126} height={56} rx={4}
        fill="rgba(192,132,252,0.05)" stroke={`${C.purple}80`} strokeWidth={1.4} strokeDasharray="5 2"/>
      <text x={461} y={247} textAnchor="middle" fill={`${C.purple}cc`} fontSize={9} fontFamily={M} fontWeight="bold">EDF-NAC-R-AFT</text>
      <text x={461} y={258} textAnchor="middle" fill={`${C.purple}70`} fontSize={7} fontFamily={M}>RPM PID · Kp=3e-4</text>
      <text x={461} y={268} textAnchor="middle" fill={`${C.purple}60`} fontSize={7} fontFamily={M}>Ki=1e-5 · Kd=8e-5</text>
      <text x={461} y={278} textAnchor="middle" fill={C.yellow} fontSize={7} fontFamily={M} opacity={0.7}>thermal derate 85°–110°C</text>

      {/* PID → DSHOT arrows */}
      {[47, 122, 193, 259].map((y,i)=>(
        <g key={i}>
          <line x1={524} y1={y} x2={570} y2={y} stroke={C.orange} strokeWidth={1.6} markerEnd="url(#arwO)"/>
          <text x={547} y={y-4} textAnchor="middle" fill={C.orange} fontSize={6} fontFamily={M}>throttle</text>
        </g>
      ))}

      {/* ─── PRU DSHOT ─── */}
      <rect x={574} y={28} width={110} height={56} rx={4}
        fill="rgba(255,107,53,0.09)" stroke={C.orange} strokeWidth={1.8}/>
      <text x={629} y={44} textAnchor="middle" fill={C.orange} fontSize={9} fontFamily={M} fontWeight="bold">PRU DSHOT</text>
      <text x={629} y={55} textAnchor="middle" fill={`${C.orange}90`} fontSize={7.5} fontFamily={M}>DSHOT1200 · 1 kHz</text>
      <text x={629} y={65} textAnchor="middle" fill={`${C.orange}70`} fontSize={7} fontFamily={M}>11-bit throttle</text>
      <text x={629} y={75} textAnchor="middle" fill={`${C.orange}60`} fontSize={7} fontFamily={M}>DSHOT0 GP26 (L-FWD)</text>

      <rect x={574} y={94} width={110} height={56} rx={4}
        fill="rgba(255,107,53,0.07)" stroke={`${C.orange}b0`} strokeWidth={1.5}/>
      <text x={629} y={110} textAnchor="middle" fill={`${C.orange}ee`} fontSize={9} fontFamily={M} fontWeight="bold">PRU DSHOT</text>
      <text x={629} y={121} textAnchor="middle" fill={`${C.orange}80`} fontSize={7.5} fontFamily={M}>DSHOT1200 · 1 kHz</text>
      <text x={629} y={131} textAnchor="middle" fill={`${C.orange}60`} fontSize={7} fontFamily={M}>11-bit throttle</text>
      <text x={629} y={141} textAnchor="middle" fill={`${C.orange}50`} fontSize={7} fontFamily={M}>DSHOT1 GP27 (L-AFT)</text>

      <rect x={574} y={165} width={110} height={56} rx={4}
        fill="rgba(255,107,53,0.05)" stroke={`${C.orange}70`} strokeWidth={1.3} strokeDasharray="5 2"/>
      <text x={629} y={181} textAnchor="middle" fill={`${C.orange}cc`} fontSize={9} fontFamily={M} fontWeight="bold">PRU DSHOT</text>
      <text x={629} y={192} textAnchor="middle" fill={`${C.orange}60`} fontSize={7.5} fontFamily={M}>DSHOT1200 · 1 kHz</text>
      <text x={629} y={202} textAnchor="middle" fill={`${C.orange}50`} fontSize={7} fontFamily={M}>11-bit throttle</text>
      <text x={629} y={212} textAnchor="middle" fill={`${C.orange}40`} fontSize={7} fontFamily={M}>DSHOT2 GP28 (R-FWD)</text>

      <rect x={574} y={231} width={110} height={56} rx={4}
        fill="rgba(255,107,53,0.04)" stroke={`${C.orange}60`} strokeWidth={1.3} strokeDasharray="5 2"/>
      <text x={629} y={247} textAnchor="middle" fill={`${C.orange}bb`} fontSize={9} fontFamily={M} fontWeight="bold">PRU DSHOT</text>
      <text x={629} y={258} textAnchor="middle" fill={`${C.orange}55`} fontSize={7.5} fontFamily={M}>DSHOT1200 · 1 kHz</text>
      <text x={629} y={268} textAnchor="middle" fill={`${C.orange}45`} fontSize={7} fontFamily={M}>11-bit throttle</text>
      <text x={629} y={278} textAnchor="middle" fill={`${C.orange}35`} fontSize={7} fontFamily={M}>DSHOT3 GP29 (R-AFT)</text>

      {/* BDSHOT feedback arrows (RPM back to PID) */}
      {[56, 122, 193, 259].map((y,i)=>(
        <g key={i}>
          <path d={`M574 ${y+6} C556 ${y+22} 540 ${y+22} 524 ${y+6}`}
            fill="none" stroke={C.green} strokeWidth={1.2} strokeDasharray="3 2"
            markerEnd="url(#arwG)"/>
          <text x={549} y={y+28} textAnchor="middle" fill={C.green} fontSize={6} fontFamily={M}>BDSHOT eRPM 1kHz</text>
        </g>
      ))}

      {/* ─── BLHeli serial telem ─── */}
      <rect x={574} y={295} width={110} height={35} rx={3}
        fill="rgba(163,230,53,0.07)" stroke={C.lime} strokeWidth={1.3}/>
      <text x={629} y={311} textAnchor="middle" fill={C.lime} fontSize={8.5} fontFamily={M} fontWeight="bold">BLHeli32 Telem</text>
      <text x={629} y={322} textAnchor="middle" fill={`${C.lime}80`} fontSize={7} fontFamily={M}>UART mux 10 Hz · RPM/I/T/V</text>

      {/* Telem to governor feedback arrows */}
      <line x1={574} y1={308} x2={540} y2={308} stroke={C.lime} strokeWidth={1.2} strokeDasharray="3 2" opacity={0.7}/>
      <line x1={540} y1={308} x2={540} y2={280} stroke={C.lime} strokeWidth={1.2} strokeDasharray="3 2" opacity={0.7}/>

      {/* Level labels */}
      <text x={80} y={26} textAnchor="middle" fill={C.purple} fontSize={7} fontFamily={M} letterSpacing="0.08em">LEVEL 1</text>
      <text x={274} y={26} textAnchor="middle" fill={C.accent} fontSize={7} fontFamily={M} letterSpacing="0.08em">LEVEL 2</text>
      <text x={461} y={26} textAnchor="middle" fill={C.teal} fontSize={7} fontFamily={M} letterSpacing="0.08em">LEVEL 3</text>
      <text x={629} y={26} textAnchor="middle" fill={C.orange} fontSize={7} fontFamily={M} letterSpacing="0.08em">OUTPUT</text>

      {/* Update rate annotations */}
      <text x={80} y={VH-8} textAnchor="middle" fill={`${C.purple}60`} fontSize={6.5} fontFamily={M}>50 Hz</text>
      <text x={274} y={VH-8} textAnchor="middle" fill={`${C.accent}60`} fontSize={6.5} fontFamily={M}>500 Hz</text>
      <text x={461} y={VH-8} textAnchor="middle" fill={`${C.teal}60`} fontSize={6.5} fontFamily={M}>500 Hz PID / 1kHz BDSHOT</text>
      <text x={629} y={VH-8} textAnchor="middle" fill={`${C.orange}60`} fontSize={6.5} fontFamily={M}>1 kHz DSHOT1200</text>
    </svg>
  );
}

// ════════════════════════════════════════════════════════════════
//  SVG DIAGRAM 2 — RPM vs THROTTLE / THRUST CURVE
// ════════════════════════════════════════════════════════════════
function RPMThrustCurveDiagram(){
  const VW=720, VH=260;
  const PL=60, PR=30, PT=30, PB=40;
  const W=VW-PL-PR, H=VH-PT-PB;
  const maxRPM=52000, maxThrottle=100, maxThrust=2900;

  // Throttle axis: 0–100%, RPM axis: 0–52000, Thrust overlay
  // RPM ≈ maxRPM × (throttle/100)^0.9 (empirical, roughly linear with slight convex)
  // Thrust ≈ k × RPM² → normalized to 2900g at 52000 RPM
  const k_T = maxThrust / (maxRPM * maxRPM);

  const pts = Array.from({length:41},(_,i)=>i*2.5); // throttle 0..100 step 2.5
  const rpm_nominal = t => maxRPM * Math.pow(t/100, 0.88);
  const rpm_derate   = t => maxRPM * Math.pow(Math.min(t,65)/100, 0.88); // cap at 65% throttle when derating
  const rpm_fault    = t => maxRPM * Math.pow(Math.min(t,80)/100, 0.88) * 0.95;
  const thrust_of_rpm = r => k_T * r * r;

  const tx = t => PL + (t/maxThrottle)*W;
  const ry = r => PT + H - (r/maxRPM)*H;
  const ty2 = thrust => PT + H - (thrust/maxThrust)*H; // second axis scale (thrust as fraction)

  const pathOf = (fn, col) => {
    const d = pts.map((t,i)=>{
      const r = fn(t);
      return `${i===0?"M":"L"}${tx(t).toFixed(1)},${ry(r).toFixed(1)}`;
    }).join(" ");
    return <path d={d} fill="none" stroke={col} strokeWidth={2}/>;
  };

  // Thrust overlay: secondary y-axis mapped so maxThrust aligns with maxRPM visually
  const thrustOf = (fn) => pts.map((t,i)=>{
    const r = fn(t);
    const thr = thrust_of_rpm(r);
    return `${i===0?"M":"L"}${tx(t).toFixed(1)},${(PT + H - (thr/maxThrust)*H).toFixed(1)}`;
  }).join(" ");

  // Soft-limit line at 80A → ~48000 RPM, dashed vertical
  const rpmSoftLimit = 48000;
  const rpmHardLimit = 52000;
  const thSoft = (rpmSoftLimit/maxRPM)*100;

  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      <defs>
        <marker id="arwD" markerWidth="6" markerHeight="6" refX="4" refY="3" orient="auto">
          <path d="M0,0 L6,3 L0,6 Z" fill="rgba(255,255,255,0.4)"/>
        </marker>
      </defs>

      {/* Title */}
      <text x={VW/2} y={14} textAnchor="middle" fill="rgba(0,229,255,0.3)" fontSize={8.5} fontFamily={M} letterSpacing="0.12em">
        RPM vs THROTTLE COMMAND — NOMINAL · DERATE · FAULT · THRUST OVERLAY
      </text>

      {/* Axes */}
      <line x1={PL} y1={PT} x2={PL} y2={PT+H} stroke="rgba(255,255,255,0.25)" strokeWidth={1}/>
      <line x1={PL} y1={PT+H} x2={PL+W} y2={PT+H} stroke="rgba(255,255,255,0.25)" strokeWidth={1}/>

      {/* Y gridlines (RPM) */}
      {[0,10000,20000,30000,40000,52000].map(r=>(
        <g key={r}>
          <line x1={PL} y1={ry(r)} x2={PL+W} y2={ry(r)} stroke="rgba(255,255,255,0.06)" strokeWidth={0.6}/>
          <text x={PL-4} y={ry(r)+3} textAnchor="end" fill="rgba(255,255,255,0.4)" fontSize={7} fontFamily={M}>{r===0?"0":`${r/1000}k`}</text>
        </g>
      ))}

      {/* X gridlines (throttle %) */}
      {[0,25,50,75,100].map(t=>(
        <g key={t}>
          <line x1={tx(t)} y1={PT} x2={tx(t)} y2={PT+H} stroke="rgba(255,255,255,0.06)" strokeWidth={0.6}/>
          <text x={tx(t)} y={PT+H+12} textAnchor="middle" fill="rgba(255,255,255,0.4)" fontSize={7} fontFamily={M}>{t}%</text>
        </g>
      ))}

      {/* Soft-limit / hard-limit vertical dashes */}
      <line x1={tx(thSoft)} y1={PT} x2={tx(thSoft)} y2={PT+H} stroke={C.yellow} strokeWidth={1} strokeDasharray="4 3" opacity={0.6}/>
      <text x={tx(thSoft)+3} y={PT+12} fill={C.yellow} fontSize={6.5} fontFamily={M} opacity={0.8}>80A soft lim</text>

      <line x1={tx(100)} y1={PT} x2={tx(100)} y2={PT+H} stroke={C.red} strokeWidth={1} strokeDasharray="4 3" opacity={0.5}/>
      <text x={tx(100)-3} y={PT+12} textAnchor="end" fill={C.red} fontSize={6.5} fontFamily={M} opacity={0.8}>84A rated</text>

      {/* RPM curves */}
      {pathOf(rpm_nominal, C.green)}
      {pathOf(rpm_derate,  C.yellow)}
      {pathOf(rpm_fault,   C.orange)}

      {/* Thrust overlay (dashed) */}
      <path d={thrustOf(rpm_nominal)} fill="none" stroke={C.teal} strokeWidth={1.5} strokeDasharray="5 3" opacity={0.8}/>
      <path d={thrustOf(rpm_fault)}   fill="none" stroke={C.red}  strokeWidth={1.4} strokeDasharray="5 3" opacity={0.6}/>

      {/* Axis labels */}
      <text x={PL+W/2} y={VH-2} textAnchor="middle" fill="rgba(255,255,255,0.5)" fontSize={8} fontFamily={M}>THROTTLE COMMAND (%)</text>
      <text x={10} y={PT+H/2} textAnchor="middle" fill="rgba(255,255,255,0.5)" fontSize={8} fontFamily={M}
        transform={`rotate(-90 10 ${PT+H/2})`}>RPM</text>

      {/* Second axis label (thrust) */}
      <text x={VW-PR+8} y={PT} fill={C.teal} fontSize={7} fontFamily={M}>2900g</text>
      <text x={VW-PR+8} y={PT+H/2} fill={C.teal} fontSize={7} fontFamily={M}>1450g</text>
      <text x={VW-PR+8} y={PT+H} fill={C.teal} fontSize={7} fontFamily={M}>0g</text>
      <text x={VW-6} y={PT+H/2-10} fill={C.teal} fontSize={7} fontFamily={M} textAnchor="middle"
        transform={`rotate(90 ${VW-6} ${PT+H/2})`}>THRUST (g, dashed)</text>

      {/* Legend */}
      {[
        {c:C.green,  label:"Nominal RPM",      x:PL+10,  y:PT+14},
        {c:C.yellow, label:"Thermal derate",   x:PL+10,  y:PT+24},
        {c:C.orange, label:"Fault mode (1 EDF down)", x:PL+10, y:PT+34},
        {c:C.teal,   label:"Thrust nominal (--)", x:PL+10, y:PT+44},
        {c:C.red,    label:"Thrust fault (--)", x:PL+10,  y:PT+54},
      ].map(({c,label,x,y})=>(
        <g key={label}>
          <line x1={x} y1={y-3} x2={x+18} y2={y-3} stroke={c} strokeWidth={1.8}/>
          <text x={x+22} y={y} fill={c} fontSize={7} fontFamily={M}>{label}</text>
        </g>
      ))}
    </svg>
  );
}

// ════════════════════════════════════════════════════════════════
//  PID PARAMETER TABLE DATA
// ════════════════════════════════════════════════════════════════
const PID_PARAMS = [
  {loop:"RPM PID (per EDF)",    kp:"0.0003",  ki:"0.00001", kd:"0.00008", rate:"500 Hz M4F",  fb:"BDSHOT eRPM 1kHz", sp:"Nacelle governor RPM setpoint",        aw:"Clamp integral when throttle = 0 or 1"},
  {loop:"Equalization PID (nacelle)", kp:"0.0001", ki:"0.000003", kd:"—",     rate:"500 Hz M4F",  fb:"RPM_FWD − RPM_AFT delta", sp:"0 (AFT_BIAS×mean_RPM − RPM_AFT)", aw:"Clamp at ±0.10 trim authority"},
  {loop:"Current limiter (proportional)", kp:"−0.010", ki:"—",      kd:"—",  rate:"10 Hz serial", fb:"BLHeli32 UART current A",   sp:"80A soft, 105A hard",                aw:"N/A — proportional only + hard cutoff"},
  {loop:"Thermal derate (linear)", kp:"linear",  ki:"—",      kd:"—",     rate:"10 Hz serial", fb:"BLHeli32 UART ESC temp °C", sp:"85°C → 110°C",                       aw:"N/A — continuous scalar cap"},
];

const FAULT_THRESHOLDS = [
  {param:"RPM zero-detect (EDF fail)", value:"< 200 eRPM for 3 consecutive BDSHOT frames",  action:"FAULT_FWD / FAULT_AFT state, disarm EDF", c:C.red},
  {param:"Current soft limit",         value:"> 80A (BLHeli32 serial, 10 Hz)",               action:"Proportional throttle reduction",          c:C.yellow},
  {param:"Current hard limit",         value:"> 105A (BLHeli32 serial, 10 Hz)",              action:"Immediate throttle = 0 + fault latch",      c:C.red},
  {param:"ESC temp derate threshold",  value:"> 85°C (BLHeli32 serial, 10 Hz)",              action:"Linear throttle cap: 100% @ 85°C → 0% @ 110°C", c:C.yellow},
  {param:"ESC temp disable threshold", value:"> 110°C (BLHeli32 serial, 10 Hz)",             action:"Hard throttle = 0 + fault latch DERATE state", c:C.red},
  {param:"RPM delta alert (equalize)", value:"| RPM_FWD − RPM_AFT | > 500 RPM (same throttle)", action:"GCS alert, log event, no thrust change",  c:C.orange},
  {param:"Current imbalance alert",    value:"| I_FWD − I_AFT | > 15A (same throttle)",      action:"GCS alert, log event, inspection flag",     c:C.orange},
  {param:"BDSHOT timeout",             value:"No valid frame for 10ms (10 consecutive misses)", action:"Fall back to BLHeli32 serial RPM estimate", c:C.orange},
];

const EQ_ALGO = [
  {step:"1", action:"Compute mean RPM",          formula:"mean = (RPM_FWD + RPM_AFT) / 2",         note:"From BDSHOT at 1 kHz, low-pass filtered 5-tap moving average"},
  {step:"2", action:"Compute AFT setpoint",      formula:"sp_AFT = AFT_BIAS × mean  (AFT_BIAS=1.02)",note:"AFT runs 2% faster to compensate inlet velocity deficit from FWD stage"},
  {step:"3", action:"Compute error",             formula:"err = sp_AFT − RPM_AFT",                  note:"Negative err → AFT too fast → trim AFT down / FWD up"},
  {step:"4", action:"Equalization PID update",   formula:"trim += Kp_eq×err + Ki_eq×∫err dt",      note:"No derivative term — RPM delta is slow. Integral dominates steady state."},
  {step:"5", action:"Clamp trim authority",      formula:"trim = clamp(trim, −0.10, +0.10)",         note:"Max ±10% throttle trim to preserve nacelle total thrust"},
  {step:"6", action:"Apply trim",                formula:"thr_FWD = governor_cmd − trim  thr_AFT = governor_cmd + trim", note:"Symmetric trim: total nacelle power constant"},
  {step:"7", action:"Anti-windup",              formula:"if |trim| == 0.10: freeze integrator",     note:"Prevents windup during thermal derate or fault states"},
];

// ════════════════════════════════════════════════════════════════
//  TAB 1 — GOVERNOR OVERVIEW
// ════════════════════════════════════════════════════════════════
function GovernorOverviewTab(){
  return(<div>
    <div style={{background:"rgba(0,229,255,0.05)",border:`1px solid ${C.accent}33`,borderRadius:6,padding:"12px 18px",marginBottom:18}}>
      <div style={{color:C.accent,fontFamily:M,fontSize:12,fontWeight:"bold",marginBottom:10,letterSpacing:"0.07em"}}>
        PER-EDF PID CLOSED-LOOP GOVERNOR — SERENITY TILTROTOR NACELLE
      </div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr 1fr",gap:16}}>
        <div>
          <KV k="EDFs per nacelle"       v="2 (FWD + AFT series stages)" vc={C.orange}/>
          <KV k="Nacelles"               v="2 (Port + Stbd) = 4 EDFs total"/>
          <KV k="EDF model"              v="XRP 3660-2700KV 80mm 6S" vc={C.teal}/>
          <KV k="Max RPM (loaded)"       v="~52,000 RPM" vc={C.green}/>
          <KV k="Max EDF current"        v="84A · soft limit 80A · hard 105A" vc={C.yellow}/>
        </div>
        <div>
          <KV k="ESC per EDF"            v="Hobbywing Platinum V4 120A" vc={C.teal}/>
          <KV k="ESC telemetry"          v="BLHeli32/AM32 UART 10 Hz" vc={C.lime}/>
          <KV k="Telem fields"           v="RPM · I · Temp · Voltage · mAh"/>
          <KV k="RPM feedback (fast)"    v="BDSHOT eRPM 1 kHz" vc={C.green}/>
          <KV k="DSHOT protocol"         v="DSHOT1200 · 625 ns/bit" vc={C.orange}/>
        </div>
        <div>
          <KV k="MCU governor"           v="PocketBeagle 2 (AM6232)" vc={C.accent}/>
          <KV k="Governor core"          v="M4F coprocessor" vc={C.purple}/>
          <KV k="Governor rate"          v="500 Hz" vc={C.green}/>
          <KV k="DSHOT output"           v="PRU-ICSS 250 MHz · 1 kHz" vc={C.orange}/>
          <KV k="PRU0 channels"          v="DSHOT0–3 (all 4 nacelle EDFs simultaneously)" vc={C.teal}/>
        </div>
      </div>
    </div>

    <SH t="Control Hierarchy Block Diagram" mt={0}/>
    <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:8,marginBottom:20}}>
      <ControlHierarchyDiagram/>
    </div>

    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="Update Rates — Loop Timing" mt={0} c={C.green}/>
        <KV k="FC attitude PID"              v="50 Hz (ArduPilot/PX4 default)" vc={C.purple}/>
        <KV k="Nacelle governor (M4F)"       v="500 Hz (2 ms period)" vc={C.accent}/>
        <KV k="Per-EDF PID (M4F)"            v="500 Hz (same M4F task)" vc={C.teal}/>
        <KV k="BDSHOT eRPM feedback"         v="1000 Hz (1 ms, every DSHOT frame)" vc={C.green}/>
        <KV k="DSHOT command output (PRU)"   v="1000 Hz (PRU0 all 4 ch simultaneously)" vc={C.orange}/>
        <KV k="BLHeli32 serial telem"        v="10 Hz (mux round-robin)" vc={C.lime}/>
        <KV k="Governor → PID command rate"  v="500 Hz (M4F inner loop)" vc={C.accent}/>
        <Note c={C.teal} ch="The M4F runs governor + PID at 500 Hz. Each 2ms tick: (1) read BDSHOT RPM buffer (latest 1kHz sample), (2) run equalization PID, (3) run 4× RPM PID, (4) write throttle values to PRU shared memory. PRU fires DSHOT at 1kHz independent of M4F, using latest throttle values from shared SRAM."/>
      </div>
      <div>
        <SH t="Governor State Machine" mt={0} c={C.orange}/>
        {[
          {s:"INIT",        c:C.dim,    d:"Power-on: all EDFs held at 0 throttle. ESC arm sequence via DSHOT (3× 0-cmd frames)."},
          {s:"ARMING",      c:C.yellow, d:"DSHOT arm sequence in progress. BLHeli32 beep acknowledged. Waiting for BDSHOT first frame."},
          {s:"NORMAL",      c:C.green,  d:"All 4 EDFs reporting valid BDSHOT RPM. Governor running. Equalization active. RPM PID tracking."},
          {s:"DERATE",      c:C.yellow, d:"One or more ESC temp > 85°C. Thermal cap applied. RPM setpoint reduced proportionally. Alert GCS."},
          {s:"FAULT_FWD",   c:C.orange, d:"Port or Stbd FWD EDF RPM < 200 for 3 frames. FWD ESC disarmed. AFT ESC solo at boosted setpoint."},
          {s:"FAULT_AFT",   c:C.orange, d:"Port or Stbd AFT EDF RPM < 200 for 3 frames. AFT ESC disarmed. FWD ESC solo at boosted setpoint."},
          {s:"FAULT_BOTH",  c:C.red,    d:"Both EDFs in one nacelle failed. Full nacelle disarmed. FC switches to asymmetric emergency mode."},
        ].map(({s,c,d})=>(
          <div key={s} style={{display:"flex",gap:8,marginBottom:5,alignItems:"flex-start"}}>
            <span style={{color:c,border:`1px solid ${c}50`,padding:"1px 7px",borderRadius:2,fontFamily:M,fontSize:8.5,whiteSpace:"nowrap",minWidth:80,textAlign:"center"}}>{s}</span>
            <span style={{color:C.dim,fontFamily:M,fontSize:9,lineHeight:1.6}}>{d}</span>
          </div>
        ))}
      </div>
    </div>

    <SH t="DSHOT1200 Frame Format" c={C.orange}/>
    <div style={{background:"rgba(255,107,53,0.06)",border:`1px solid ${C.orange}33`,borderRadius:4,padding:"10px 14px",fontFamily:M}}>
      <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:12}}>
        <KV k="Protocol"        v="DSHOT1200" vc={C.orange}/>
        <KV k="Bit period"      v="625 ns (1.6 MHz)" vc={C.yellow}/>
        <KV k="Throttle bits"   v="11 bits (0–2047)" vc={C.green}/>
        <KV k="Telem request"   v="1 bit" vc={C.teal}/>
        <KV k="CRC"             v="4 bits (nibble XOR)" vc={C.purple}/>
        <KV k="Frame length"    v="16 bits total" vc={C.dim}/>
        <KV k="PRU output"      v="PRU0 simultaneous 4 channels" vc={C.orange}/>
        <KV k="BDSHOT"          v="eRPM embedded in ESC response telemetry" vc={C.green}/>
      </div>
      <Note c={C.orange} ch="DSHOT throttle 0 = disarm/coast; 1–47 reserved for special commands (3D mode, telem enable, save settings); 48–2047 = throttle range. Governor maps RPM setpoint to throttle via pre-computed inverse RPM table loaded during commissioning. PRU0 at 250 MHz provides bit-perfect timing: 0 bit = 250ns high + 375ns low; 1 bit = 500ns high + 125ns low (DSHOT1200 spec)."/>
    </div>
  </div>);
}

// ════════════════════════════════════════════════════════════════
//  TAB 2 — PER-EDF PID LOOPS
// ════════════════════════════════════════════════════════════════
function PerEDFPIDTab(){
  return(<div>
    <SH t="RPM vs Throttle / Thrust Curve" mt={0}/>
    <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:8,marginBottom:20}}>
      <RPMThrustCurveDiagram/>
    </div>

    <SH t="PID Loop Parameters — All Loops" c={C.teal}/>
    <div style={{overflowX:"auto",marginBottom:20}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["LOOP","Kp","Ki","Kd","RATE","FEEDBACK","SETPOINT","ANTI-WINDUP"]}/>
        <tbody>{PID_PARAMS.map((p,i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent",verticalAlign:"top"}}>
            <td style={{padding:"6px 9px",color:C.accent,fontWeight:"bold",fontSize:9,minWidth:130}}>{p.loop}</td>
            <td style={{padding:"6px 9px",color:C.green,fontFamily:"'Courier New',monospace"}}>{p.kp}</td>
            <td style={{padding:"6px 9px",color:C.teal,fontFamily:"'Courier New',monospace"}}>{p.ki}</td>
            <td style={{padding:"6px 9px",color:C.purple,fontFamily:"'Courier New',monospace"}}>{p.kd}</td>
            <td style={{padding:"6px 9px",color:C.yellow,fontSize:9}}>{p.rate}</td>
            <td style={{padding:"6px 9px",color:C.dim,fontSize:9}}>{p.fb}</td>
            <td style={{padding:"6px 9px",color:C.dim,fontSize:9}}>{p.sp}</td>
            <td style={{padding:"6px 9px",color:C.orange,fontSize:9}}>{p.aw}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>

    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="RPM PID — Per EDF" mt={0} c={C.green}/>
        <KV k="Feedback source"     v="BDSHOT eRPM at 1 kHz" vc={C.green}/>
        <KV k="eRPM → RPM"          v="eRPM / (motor_poles / 2)  =  eRPM / 7 for 14-pole XRP" vc={C.teal}/>
        <KV k="Setpoint source"     v="Nacelle governor output (with equalization trim)" vc={C.accent}/>
        <KV k="Control output"      v="DSHOT throttle value (48–2047)" vc={C.orange}/>
        <KV k="Kp_rpm"              v="0.0003  (units: throttle / RPM)" vc={C.green}/>
        <KV k="Ki_rpm"              v="0.00001  (units: throttle / RPM·s)" vc={C.teal}/>
        <KV k="Kd_rpm"              v="0.00008  (units: throttle·s / RPM)" vc={C.purple}/>
        <KV k="Anti-windup"         v="Clamp integral when throttle saturated (≤ 48 or ≥ 2047)" vc={C.yellow}/>
        <Note c={C.teal} ch="At 52,000 RPM max and Kp=3e-4, a 1,000 RPM error produces a 0.3 throttle correction (on a 0–1 normalized scale). This provides ~1.5% throttle adjustment per 500 RPM error — fast enough to track load transients within 200ms."/>
        <Note c={C.green} ch="BDSHOT runs at 1kHz but M4F PID executes at 500Hz. The M4F reads the latest eRPM sample written by PRU to shared SRAM (ping-pong buffer) each 2ms tick. No interpolation needed — latency is at most 1ms."/>
      </div>
      <div>
        <SH t="Current Limiter + Thermal Derate" mt={0} c={C.yellow}/>
        <KV k="Current source"       v="BLHeli32 UART serial, 10 Hz round-robin mux" vc={C.lime}/>
        <KV k="Soft limit"           v="80A  →  proportional throttle reduction" vc={C.yellow}/>
        <KV k="Hard limit"           v="105A →  immediate throttle = 0 + fault latch" vc={C.red}/>
        <KV k="Current Kp (soft)"    v="−0.010 (units: throttle reduction / A over 80A)" vc={C.yellow}/>
        <KV k="Temp derate start"    v="85°C  →  begin linearly capping max throttle" vc={C.orange}/>
        <KV k="Temp derate end"      v="110°C →  max throttle cap reaches 0" vc={C.red}/>
        <KV k="Derate formula"       v="cap = 1 − (T − 85) / 25   (T in °C, clamp 0–1)" vc={C.orange}/>
        <KV k="Thermal source"       v="BLHeli32 UART temp byte, 10 Hz" vc={C.lime}/>
        <Warn ch="At 10 Hz BLHeli32 serial update rate, current and temp readings are 100ms stale relative to the 500 Hz PID loop. The proportional soft-limit correction must be conservative (Kp small) to avoid oscillation from stale feedback. The hard 105A limit is an immediate cutoff — not PID controlled."/>
        <Good ch="BDSHOT provides eRPM at 1kHz for the fast RPM loop. BLHeli32 UART provides current + temp at 10Hz for slow protection loops. Both are used simultaneously — BDSHOT via PRU, serial telem via 74HC4051 mux + UART1."/>
        <Crit ch="If BLHeli32 UART telem is lost (mux fault, wire break), governor must hold last-known current and temp values and flag a GCS warning within 3 missed frames (300ms). Do not assume zero current if telemetry drops."/>
      </div>
    </div>
  </div>);
}

// ════════════════════════════════════════════════════════════════
//  TAB 3 — NACELLE COOPERATIVE CONTROL
// ════════════════════════════════════════════════════════════════
function NacelleCoopTab(){
  return(<div>
    <SH t="Equalization PID — FWD/AFT RPM Matching" mt={0} c={C.accent}/>
    <div style={{background:"rgba(0,229,255,0.05)",border:`1px solid ${C.accent}33`,borderRadius:4,padding:"10px 14px",marginBottom:16}}>
      <Note c={C.accent} ch="Two EDFs in series create an aerodynamic dependency: the AFT EDF sees reduced inlet velocity because the FWD EDF has already extracted momentum from the airflow. At equal throttle commands the AFT EDF must spin ~2% faster to produce equal thrust increment. The equalization PID enforces this bias while minimizing RPM delta."/>
    </div>

    <SH t="Equalization Algorithm — Step by Step" c={C.teal}/>
    <div style={{overflowX:"auto",marginBottom:20}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["STEP","ACTION","FORMULA / VALUE","NOTES"]}/>
        <tbody>{EQ_ALGO.map((r,i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent",verticalAlign:"top"}}>
            <td style={{padding:"6px 9px",color:C.accent,fontWeight:"bold",textAlign:"center",fontSize:12}}>{r.step}</td>
            <td style={{padding:"6px 9px",color:C.text,fontWeight:"bold",fontSize:10}}>{r.action}</td>
            <td style={{padding:"6px 9px",color:C.green,fontFamily:"'Courier New',monospace",fontSize:9,whiteSpace:"nowrap"}}>{r.formula}</td>
            <td style={{padding:"6px 9px",color:C.dim,fontSize:9,lineHeight:1.6}}>{r.note}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>

    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="Equalization PID Parameters" mt={0} c={C.purple}/>
        <KV k="Kp_eq"           v="0.0001  (throttle trim / RPM error)" vc={C.green}/>
        <KV k="Ki_eq"           v="0.000003  (throttle trim / RPM·s)" vc={C.teal}/>
        <KV k="Kd_eq"           v="None — RPM delta signal too noisy for derivative" vc={C.dim}/>
        <KV k="AFT_BIAS"        v="1.02  (AFT runs 2% higher than mean RPM)" vc={C.orange}/>
        <KV k="Trim authority"  v="±10% throttle (±0.10 on 0–1 scale)" vc={C.yellow}/>
        <KV k="Update rate"     v="500 Hz (M4F, same task as RPM PID)" vc={C.accent}/>
        <KV k="Anti-windup"     v="Freeze integrator when |trim| = 0.10" vc={C.yellow}/>
        <Note c={C.orange} ch="The 2% AFT bias is an empirical estimate for the XRP 3660 in the 93.5mm duct at typical operating RPM (35,000–45,000). Measure actual thrust vs RPM for FWD and AFT individually during bench commissioning and refine the bias accordingly. A bias error of ±0.5% has negligible impact on nacelle efficiency."/>
      </div>
      <div>
        <SH t="Throttle Cross-Coupling Matrix" mt={0} c={C.gold}/>
        <Note c={C.gold} ch="The nacelle governor receives a single collective throttle command from the FC. It distributes this to FWD and AFT via the equalization trim and applies cross-coupling corrections for tilt angle (forward flight vs hover) and nacelle load (temperature derate)."/>
        <div style={{background:"rgba(251,191,36,0.06)",border:`1px solid ${C.gold}44`,borderRadius:4,padding:"10px 12px",fontFamily:"'Courier New',monospace",fontSize:9,lineHeight:1.9,marginTop:8}}>
          <div style={{color:C.gold}}>thr_FWD = FC_throttle − eq_trim − curr_derate_FWD × tilt_scale</div>
          <div style={{color:C.gold}}>thr_AFT = FC_throttle + eq_trim − curr_derate_AFT × tilt_scale</div>
          <div style={{color:`${C.gold}80`,marginTop:6}}>tilt_scale = cos(nacelle_angle)  /* 1.0 hover, ~0.95 forward */</div>
          <div style={{color:`${C.gold}70`}}>curr_derate = max(0, (I − 80A) × 0.010)  /* soft limit */</div>
          <div style={{color:`${C.gold}70`}}>eq_trim = equalization PID output (±0.10)</div>
        </div>
        <Note c={C.teal} ch="In forward flight with nacelle tilted forward, the EDF thrust vector has a reduced vertical component. The tilt_scale factor (cosine of tilt angle) scales the base throttle command so the vertical lift component remains constant as tilt increases. The equalization trim is applied after tilt scaling."/>
        <Good ch="Series-stage efficiency: at 40,000 RPM with AFT bias of +2%, the nacelle generates approximately 91% of the arithmetic sum of two independent EDFs. The equalization PID maintains this operating point automatically. Without equalization, RPM mismatch reduces efficiency to ~85%."/>
      </div>
    </div>

    <SH t="RPM Matching Verification" c={C.green}/>
    <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:12}}>
      {[
        {metric:"Steady-state RPM delta",  target:"< 200 RPM at cruise",  method:"BDSHOT log review",         c:C.green},
        {metric:"Equalization settle time", target:"< 500ms from step",   method:"Step test RPM log",          c:C.teal},
        {metric:"Trim authority usage",    target:"< ±5% at cruise",      method:"Log eq_trim telemetry",      c:C.accent},
        {metric:"Nacelle efficiency ratio",target:"> 90% of 2× single",   method:"Thrust stand dual vs single",c:C.yellow},
        {metric:"AFT bias calibration",    target:"1.015–1.025",          method:"Equal-thrust RPM measurement",c:C.orange},
        {metric:"Windup events per flight",target:"0 in normal flight",    method:"Anti-windup flag in log",    c:C.purple},
      ].map(({metric,target,method,c})=>(
        <div key={metric} style={{padding:"10px 12px",border:`1px solid ${c}33`,background:`${c}07`,borderRadius:4}}>
          <div style={{color:c,fontFamily:M,fontSize:8.5,fontWeight:"bold",marginBottom:4}}>{metric}</div>
          <div style={{color:C.text,fontFamily:M,fontSize:9,marginBottom:3}}>{target}</div>
          <div style={{color:`${C.dim}80`,fontFamily:M,fontSize:8}}>{method}</div>
        </div>
      ))}
    </div>
  </div>);
}

// ════════════════════════════════════════════════════════════════
//  TAB 4 — FAULT RESPONSE
// ════════════════════════════════════════════════════════════════
function FaultResponseTab(){
  return(<div>
    <SH t="Fault Threshold Table" mt={0} c={C.red}/>
    <div style={{overflowX:"auto",marginBottom:20}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["PARAMETER","THRESHOLD","GOVERNOR ACTION","SEVERITY"]}/>
        <tbody>{FAULT_THRESHOLDS.map((f,i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent",verticalAlign:"top"}}>
            <td style={{padding:"6px 9px",color:C.text,fontWeight:"bold",fontSize:9}}>{f.param}</td>
            <td style={{padding:"6px 9px",color:C.yellow,fontFamily:"'Courier New',monospace",fontSize:9}}>{f.value}</td>
            <td style={{padding:"6px 9px",color:C.text,fontSize:9,lineHeight:1.5}}>{f.action}</td>
            <td style={{padding:"6px 9px"}}>
              <span style={{color:f.c,border:`1px solid ${f.c}55`,padding:"1px 7px",borderRadius:2,fontSize:8.5,whiteSpace:"nowrap"}}>{f.c===C.red?"CRITICAL":f.c===C.yellow?"WARNING":"ALERT"}</span>
            </td>
          </tr>
        ))}</tbody>
      </table>
    </div>

    <SH t="Fault State Machine — NORMAL → DERATE → FAULT_FWD → FAULT_AFT → FAULT_BOTH" c={C.orange}/>
    <div style={{overflowX:"auto",marginBottom:16}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["STATE","FWD COMMAND","AFT COMMAND","TRANSITION IN","TRANSITION OUT","NACELLE THRUST"]}/>
        <tbody>{[
          {s:"NORMAL",     c:C.green,  fwd:"governor_cmd − eq_trim",   aft:"governor_cmd + eq_trim",     in_:"Power-on + valid BDSHOT × 4",         out:"Any threshold exceeded",         thrust:"100%"},
          {s:"DERATE",     c:C.yellow, fwd:"governor_cmd × cap_FWD",   aft:"governor_cmd × cap_AFT",     in_:"ESC temp > 85°C",                     out:"Temp < 80°C OR temp > 110°C",   thrust:"50–100% (linear)"},
          {s:"FAULT_FWD",  c:C.orange, fwd:"DISARMED (DSHOT cmd 0)",   aft:"min(governor_cmd × 1.20, 1)",in_:"FWD RPM < 200 × 3 frames",            out:"Latched — ground reset only",   thrust:"~55% (single EDF boosted)"},
          {s:"FAULT_AFT",  c:C.orange, fwd:"min(governor_cmd × 1.20, 1)",aft:"DISARMED (DSHOT cmd 0)",  in_:"AFT RPM < 200 × 3 frames",            out:"Latched — ground reset only",   thrust:"~55% (single EDF boosted)"},
          {s:"FAULT_BOTH", c:C.red,    fwd:"DISARMED (DSHOT cmd 0)",   aft:"DISARMED (DSHOT cmd 0)",     in_:"Both RPM < 200 × 3 frames OR hard 105A",out:"Latched — ground reset only",  thrust:"0% — nacelle dead"},
        ].map((r,i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent",verticalAlign:"top"}}>
            <td style={{padding:"5px 9px"}}><span style={{color:r.c,border:`1px solid ${r.c}55`,padding:"2px 7px",borderRadius:2,fontSize:9,fontWeight:"bold"}}>{r.s}</span></td>
            <td style={{padding:"5px 9px",color:r.fwd.includes("DISARMED")?C.red:C.green,fontFamily:"'Courier New',monospace",fontSize:8.5}}>{r.fwd}</td>
            <td style={{padding:"5px 9px",color:r.aft.includes("DISARMED")?C.red:C.green,fontFamily:"'Courier New',monospace",fontSize:8.5}}>{r.aft}</td>
            <td style={{padding:"5px 9px",color:C.dim,fontSize:8.5,lineHeight:1.5}}>{r.in_}</td>
            <td style={{padding:"5px 9px",color:r.out.includes("Latched")?C.red:C.dim,fontSize:8.5}}>{r.out}</td>
            <td style={{padding:"5px 9px",color:r.c,fontWeight:"bold",fontSize:9}}>{r.thrust}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>

    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="Latch Policy" mt={0} c={C.red}/>
        <Note c={C.red} ch="All FAULT states are HARD LATCHED. Once a FAULT_FWD, FAULT_AFT, or FAULT_BOTH state is entered, it cannot be cleared in flight. The ESC remains disarmed for the remainder of the flight. Rationale: spontaneous re-arm of a faulted ESC during maneuvering creates an unpredictable thrust spike that may destabilize the airframe more severely than the original fault."/>
        <Note c={C.orange} ch="DERATE is NOT latched. If ESC temperature recovers below 80°C (hysteresis 5°C), the governor returns to NORMAL automatically. The DERATE → NORMAL transition is gradual: throttle cap ramps from the derate cap back to 1.0 over 2 seconds to prevent an abrupt thrust jump."/>
        <Good ch="Fault clearing procedure: (1) land aircraft, (2) disarm FC, (3) remove battery for >10s, (4) GCS sends explicit FAULT_CLEAR command on ground after battery reconnection, (5) confirm all 4 ESCs show valid BDSHOT RPM during motor test before flight."/>
        <Warn ch="The 105A hard current limit triggers an immediate DSHOT throttle=0 + fault latch. This is designed for MOSFET protection. At 105A the ESC MOSFETs are near thermal runaway. No gradual ramp — instantaneous cutoff."/>
      </div>
      <div>
        <SH t="Asymmetric Thrust Compensation" mt={0} c={C.yellow}/>
        <Note c={C.yellow} ch="Single EDF fault (FAULT_FWD or FAULT_AFT): surviving EDF throttle boosted to 120% of governor command (hard-capped at 1.0 / 2047). Opposite nacelle trimmed −10% throttle (FC applies differential tilt to compensate yaw moment). Net altitude loss at fault onset < 0.5m. Return-to-land authorized."/>
        <Note c={C.orange} ch="Full nacelle fault (FAULT_BOTH): FC receives NACELLE_DEAD flag on CAN FD. FC switches to asymmetric emergency mode: (1) surviving nacelle at 100% throttle, (2) nacelle tilt differential up to ±5° for yaw balance, (3) fuselage EDF at 100% for supplemental lift, (4) target descent rate < 2 m/s. GCS MAYDAY alert via MAVLink."/>
        <Note c={C.teal} ch="Fault log content (written to SD card on CAN FD FAULT_EVENT): fault state, ESC ID, RPM at fault, current at fault, temp at fault, battery voltage, flight phase (hover/transition/cruise), nacelle tilt angle, FC throttle demand, timestamp in milliseconds since boot."/>
        <Crit ch="Do not attempt to continue a mission after FAULT_BOTH on either nacelle. T/W drops to ~1.6:1 (loaded). Controlled descent only. Declare emergency to ATC if in controlled airspace."/>
      </div>
    </div>
  </div>);
}

// ════════════════════════════════════════════════════════════════
//  TAB 5 — COMMISSIONING & TUNING
// ════════════════════════════════════════════════════════════════
function CommissioningTab(){
  const steps = [
    {
      n:"1", title:"Bench Calibration — Thrust vs RPM Curve", c:C.accent,
      body:[
        "Mount single EDF (with ESC) on thrust stand. Connect BLHeli32 serial telem and BDSHOT to M4F.",
        "Enable governor in BENCH mode (no equalization, direct RPM setpoint from GCS).",
        "Sweep RPM from 15,000 to 52,000 in 2,000 RPM steps. At each step, record: BDSHOT eRPM, BLHeli32 RPM, thrust (g), current (A), voltage (V). Hold each step for 3 seconds.",
        "Fit k_T = thrust / RPM² from data. Expected: k_T ≈ 1.07e-6 g/RPM². Verify R² > 0.99.",
        "Build inverse lookup table: RPM → DSHOT throttle. Store in M4F flash. This replaces the open-loop linear throttle-to-RPM assumption.",
        "Repeat for all 4 EDFs. Compare k_T values — must be within ±3% across all 4 units. If outside 3%, check blade pitch balance.",
      ]
    },
    {
      n:"2", title:"Governor Setup — RPM PID Initial Tuning", c:C.green,
      body:[
        "Load default gains: Kp_rpm=0.0003, Ki_rpm=0.00001, Kd_rpm=0.00008.",
        "Command step from 20,000 RPM to 35,000 RPM setpoint. Record BDSHOT RPM response.",
        "Target: settle to within ±200 RPM of setpoint within 300ms. Overshoot < 5%.",
        "If overdamped (slow, no overshoot): increase Kp_rpm by 20%, repeat. If underdamped (oscillation): reduce Kp_rpm by 15% or add Kd_rpm.",
        "Enable Ki after Kp/Kd are stable. Increase Ki from 0 until steady-state error < 50 RPM. Too high Ki causes windup on step changes.",
        "Verify anti-windup: apply 100% throttle command, confirm integrator freezes when throttle saturates at 2047.",
      ]
    },
    {
      n:"3", title:"Equalization PID Tuning", c:C.teal,
      body:[
        "Install both FWD and AFT EDFs in the nacelle pod on the thrust stand.",
        "Set Kp_eq=0, Ki_eq=0. Command 40,000 RPM on both. Measure actual RPM_FWD and RPM_AFT.",
        "Measure actual velocity deficit: compute ratio RPM_AFT_needed / RPM_FWD for equal thrust. This is AFT_BIAS. Expected ~1.02 but confirm experimentally.",
        "Enable equalization with Kp_eq=0.0001. Step test: force RPM_FWD to 38,000 (reduce FWD setpoint). Observe eq trim response. Target: eq_trim converges within 1 second.",
        "Enable Ki_eq=0.000003. Verify steady-state RPM delta < 100 RPM at cruise (40,000 RPM mean).",
        "Log eq_trim over a 5-minute hover. Trim usage should be < ±3% in calm air. If consistently at ±5–8%, recheck AFT_BIAS calibration.",
      ]
    },
    {
      n:"4", title:"Fault Injection Testing", c:C.yellow,
      body:[
        "With airframe secured to test stand, enter FAULT_FWD by sending governor debug command (FWD_DISARM). Confirm: FWD ESC disarms immediately, AFT ESC boosts to 120%, GCS shows FAULT_FWD state.",
        "Verify latch: send NORMAL command from GCS in flight — confirm governor ignores it (fault is latched).",
        "Test current limiter: throttle FWD EDF until BLHeli32 serial reads >80A (use bench PSU with current meter). Confirm proportional throttle reduction kicks in.",
        "Test thermal derate: inject synthetic temp byte >85°C via serial telem emulator. Confirm throttle cap ramps down. At 97.5°C expect 50% cap.",
        "Test hard current cutoff: inject synthetic current >105A. Confirm immediate throttle=0 and FAULT state entered.",
        "Complete fault log review: download SD card log and verify all fault events recorded with correct RPM/I/T/V/timestamp.",
      ]
    },
    {
      n:"5", title:"Flight Acceptance Criteria", c:C.lime,
      body:[
        "Pre-flight: all 4 EDFs report valid BDSHOT RPM in ground motor test. BDSHOT < 200 RPM zero-detect arm check passes.",
        "Hover at 50% throttle for 2 minutes. Post-flight: RPM log delta FWD−AFT < 200 RPM sustained. Eq trim < ±3%. No thermal events.",
        "Transition to forward flight and back. Confirm tilt_scale compensation maintains hover altitude ±0.3m during transition.",
        "Single-EDF fault simulation (preflight, tethered hover): inject FAULT_FWD via GCS. Confirm aircraft remains stable with <3° attitude change and <0.5m altitude transient.",
        "T/W verification at full throttle on thrust stand: confirm total thrust ≥ 10,800g (nominal 11,250g ×0.96 acceptance threshold). Record all 4 EDF contributions.",
        "Log all commissioning data: k_T per EDF, AFT_BIAS, tuned Kp/Ki/Kd per EDF, fault injection pass/fail, thrust stand results. Archive before first unrestrained flight.",
      ]
    },
  ];

  return(<div>
    <SH t="Commissioning Sequence" mt={0} c={C.accent}/>
    <Note c={C.accent} ch="Complete all steps in order on a workbench with the ESCs connected to a bench PSU (not flight battery) for steps 1–4. Steps 5+ require the full airframe on a thrust stand. Never attempt first flight without completing the full commissioning sequence."/>
    {steps.map(({n,title,c,body})=>(
      <div key={n} style={{marginBottom:18,border:`1px solid ${c}33`,borderRadius:4,background:`${c}05`}}>
        <div style={{padding:"8px 14px",borderBottom:`1px solid ${c}22`,display:"flex",gap:10,alignItems:"center"}}>
          <span style={{color:c,fontFamily:M,fontSize:16,fontWeight:"bold",minWidth:24}}>{n}</span>
          <span style={{color:c,fontFamily:M,fontSize:11,fontWeight:"bold"}}>{title}</span>
        </div>
        <div style={{padding:"10px 14px"}}>
          {body.map((b,i)=>(
            <div key={i} style={{display:"flex",gap:8,marginBottom:6,alignItems:"flex-start"}}>
              <span style={{color:`${c}70`,fontFamily:M,fontSize:10,minWidth:18}}>{i+1}.</span>
              <span style={{color:C.dim,fontFamily:M,fontSize:9.5,lineHeight:1.7}}>{b}</span>
            </div>
          ))}
        </div>
      </div>
    ))}

    <SH t="Acceptance Criteria Summary" c={C.lime}/>
    <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:12,marginBottom:16}}>
      {[
        {label:"Hover RPM delta FWD/AFT",     pass:"< 200 RPM",           fail:"≥ 500 RPM → recheck eq PID",  c:C.green},
        {label:"Equalization settle time",     pass:"< 500ms",             fail:"≥ 1s → reduce Ki_eq",          c:C.teal},
        {label:"Current soft-limit response",  pass:"< 200ms throttle ramp",fail:"No response → check telem",  c:C.yellow},
        {label:"Fault latch (FWD/AFT)",        pass:"Latch holds in flight",fail:"Auto-reset → reflash governor",c:C.orange},
        {label:"Total nacelle thrust",         pass:"> 10,800g (4 EDFs)",  fail:"< 10,000g → inspect blades",  c:C.green},
        {label:"Thermal derate linearity",     pass:"R² > 0.98 vs formula", fail:"Non-linear → check telem byte",c:C.purple},
      ].map(({label,pass,fail,c})=>(
        <div key={label} style={{padding:"10px 12px",border:`1px solid ${c}33`,background:`${c}07`,borderRadius:4}}>
          <div style={{color:c,fontFamily:M,fontSize:8.5,fontWeight:"bold",marginBottom:4}}>{label}</div>
          <div style={{color:C.green,fontFamily:M,fontSize:9,marginBottom:2}}>✓ PASS: {pass}</div>
          <div style={{color:C.red,fontFamily:M,fontSize:8.5}}>✖ FAIL: {fail}</div>
        </div>
      ))}
    </div>
    <Good ch="All commissioning data must be signed and archived by the engineer of record before unrestrained flight operations. Archival includes: thrust stand CSV, PID parameter set (version-controlled), fault injection test report, and governor firmware hash."/>
  </div>);
}

// ════════════════════════════════════════════════════════════════
//  TABS CONFIG
// ════════════════════════════════════════════════════════════════
const TABS = [
  {label:"Governor Overview",        value:"overview"},
  {label:"Per-EDF PID Loops",        value:"pid"},
  {label:"Nacelle Cooperative Ctrl", value:"coop"},
  {label:"Fault Response",           value:"fault"},
  {label:"Commissioning & Tuning",   value:"commission"},
];

// ════════════════════════════════════════════════════════════════
//  APP ROOT
// ════════════════════════════════════════════════════════════════
_ODFontLoader();
export default function App(){
  const [tab,setTab]=useState("overview");
  return(<div style={{minHeight:"100vh",background:C.bg,color:C.text,fontFamily:M}}>
    <Grid/>
    {/* Copyright banner */}
    <div style={{background:"rgba(163,230,53,0.05)",borderBottom:"1px solid rgba(163,230,53,0.18)",padding:"4px 24px",fontFamily:M,fontSize:8,color:"rgba(163,230,53,0.70)",lineHeight:1.7}}>
      © 2026 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP · CC BY 4.0 · Serenity fan engineering
    </div>
    {/* Header */}
    <div style={{position:"relative",zIndex:1,borderBottom:`1px solid ${C.border}`,padding:"14px 24px 12px"}}>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",flexWrap:"wrap",gap:12}}>
        <div>
          <div style={{color:C.orange,fontSize:9,letterSpacing:"0.2em",marginBottom:4}}>
            SERENITY TILTROTOR · POCKETBEAGLE 2 (AM6232) · PRU-ICSS + M4F · DSHOT1200 · BDSHOT × 4
          </div>
          <h1 style={{margin:0,fontSize:18,fontWeight:"normal",color:C.text,letterSpacing:"0.07em",fontFamily:MB}}>
            NACELLE PID GOVERNOR — PER-EDF CLOSED-LOOP RPM CONTROL
          </h1>
          <div style={{color:"rgba(0,229,255,0.6)",fontSize:10,marginTop:3,fontFamily:M}}>
            4× XRP 3660-2700KV 80mm 6S EDF · 4× HW Platinum V4 120A ESC · BDSHOT 1kHz · BLHeli32 UART 10Hz
          </div>
        </div>
        <div style={{textAlign:"right",fontFamily:M}}>
          <div style={{color:C.orange,fontSize:13,fontWeight:"bold"}}>52,000 RPM max · 84A per EDF</div>
          <div style={{color:C.green,fontSize:11,marginTop:2}}>500 Hz governor · 1 kHz DSHOT output</div>
          <div style={{color:C.yellow,fontSize:10,marginTop:2}}>Kp=3e-4 · Ki=1e-5 · Kd=8e-5</div>
          <div style={{color:C.teal,fontSize:10,marginTop:2}}>AFT bias +2% · equalization Kp=1e-4</div>
        </div>
      </div>
      {/* Tab selector */}
      <div style={{display:"flex",gap:2,marginTop:12,flexWrap:"wrap"}}>
        {TABS.map(t=>(<button key={t.value} onClick={()=>setTab(t.value)} style={{
          background:tab===t.value?"rgba(0,229,255,0.09)":"transparent",
          border:`1px solid ${tab===t.value?C.accent:"rgba(0,229,255,0.12)"}`,
          color:tab===t.value?C.accent:C.dimmer,
          padding:"4px 12px",fontFamily:M,fontSize:9,
          cursor:"pointer",letterSpacing:"0.06em",
          transition:"all 0.12s",borderRadius:0,
        }}>{t.label}</button>))}
      </div>
    </div>
    {/* Tab content */}
    <div style={{position:"relative",zIndex:1,padding:"20px 24px",maxWidth:1080,margin:"0 auto"}}>
      {tab==="overview"   && <GovernorOverviewTab/>}
      {tab==="pid"        && <PerEDFPIDTab/>}
      {tab==="coop"       && <NacelleCoopTab/>}
      {tab==="fault"      && <FaultResponseTab/>}
      {tab==="commission" && <CommissioningTab/>}
    </div>
    {/* Footer */}
    <div style={{position:"relative",zIndex:1,borderTop:`1px solid ${C.border}`,padding:"8px 24px",fontFamily:M,fontSize:8,color:"rgba(0,229,255,0.3)",textAlign:"center",marginTop:20}}>
      © 2026 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP · CC BY 4.0 · Serenity fan engineering ·
      PocketBeagle 2 AM6232 · PRU0 DSHOT0–3 · M4F PID governor · BDSHOT 1kHz · BLHeli32/AM32 10Hz telem
    </div>
  </div>);
}
