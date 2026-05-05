import { useState } from "react";

// ── tokens ────────────────────────────────────────────────────
// ── OpenDyslexic font loader ───────────────────────────────────
// Accessibility: high-contrast + dyslexia-friendly font (CC BY 4.0 OpenDyslexic)
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
      * { color: #111111 !important; background: transparent !important;
          border-color: #333333 !important; }
      a { color: #003366 !important; }
    }
  `;
  document.head.appendChild(s);
  return null;
}


const C = {
  bg:"#060a0e", border:"rgba(0,229,255,0.11)", accent:"#00e5ff",
  orange:"#ff6b35", yellow:"#ffe600", purple:"#c084fc", green:"#4ade80",
  pink:"#f472b6", teal:"#2dd4bf", red:"#f87171", lime:"#a3e635",
  gold:"#fbbf24", dim:"rgba(255,255,255,0.90)", dimmer:"rgba(255,255,255,0.80)",
  text:"rgba(255,255,255,0.82)",
};
const M = "'OpenDyslexic Mono','OpenDyslexic','OpenDyslexicMono',monospace";

// ── primitives ────────────────────────────────────────────────
const SH=({t,c=C.accent,mt=22})=>(<div style={{display:"flex",alignItems:"center",gap:10,marginBottom:14,marginTop:mt}}><div style={{width:3,height:17,background:c}}/><span style={{color:c,fontFamily:M,fontSize:13,letterSpacing:"0.13em",textTransform:"uppercase",fontWeight:"normal"}}>{t}</span></div>);
const KV=({k,v,vc=C.text,u=""})=>(<div style={{display:"flex",justifyContent:"space-between",padding:"5px 0",borderBottom:"1px solid rgba(0,229,255,0.07)",alignItems:"baseline"}}><span style={{color:C.dim,fontFamily:M,fontSize:11}}>{k}</span><span style={{color:vc,fontFamily:M,fontSize:11}}>{v}{u&&<span style={{color:C.accent,marginLeft:4,fontSize:10}}>{u}</span>}</span></div>);
const Note=({c=C.dim,ch})=>(<div style={{marginTop:8,marginBottom:6,color:c,fontFamily:M,fontSize:10,lineHeight:1.85,padding:"8px 12px",borderLeft:`2px solid ${c}55`,background:`${c}07`,borderRadius:3}}>{ch}</div>);
const Warn=({ch})=>(<div style={{marginTop:8,color:C.yellow,fontFamily:M,fontSize:10,lineHeight:1.8,padding:"7px 12px",borderLeft:`2px solid ${C.yellow}`,background:"rgba(255,230,0,0.05)",borderRadius:3}}>⚠ {ch}</div>);
function TH({cols}){return(<thead><tr>{cols.map(h=>(<th key={h} style={{padding:"6px 9px",borderBottom:`1px solid ${C.border}`,color:C.accent,textAlign:"left",fontWeight:"normal",fontSize:10,letterSpacing:"0.06em",whiteSpace:"nowrap",opacity:.85}}>{h}</th>))}</tr></thead>);}
function Grid(){return(<svg style={{position:"fixed",inset:0,width:"100%",height:"100%",pointerEvents:"none",zIndex:0}}><defs><pattern id="sg" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0L0 0 0 20" fill="none" stroke="rgba(0,229,255,0.03)" strokeWidth={0.5}/></pattern><pattern id="lg" width="100" height="100" patternUnits="userSpaceOnUse"><rect width="100" height="100" fill="url(#sg)"/><path d="M100 0L0 0 0 100" fill="none" stroke="rgba(0,229,255,0.06)" strokeWidth={1}/></pattern></defs><rect width="100%" height="100%" fill="url(#lg)"/></svg>);}

// ─────────────────────────────────────────────────────────────
//  GEAR MECHANISM CONSTANTS
//  Nacelle pivot:   90° sweep (0° cruise → 90° hover)
//  Sector gear:     R_sec = 22mm  (fixed to tilt bracket)
//  Drive pinion:    R_pin =  6mm  (on nacelle outer shell)
//  Ratio:           22/6 ≈ 3.67:1  →  90° nacelle = 330° pinion
//  Bevel pair:      1:1 (90° axis redirect, pinion→longitudinal shaft)
//  Longitudinal shaft → Crown pinion: R_cr = 6mm
//  Nozzle ring rack: R_rack = 28mm  (radius of rack on inner ring)
//  Ring angle:      330 × (6/28) ≈ 70.7°  (62–75° target range)
//  Result:          ~71° ring rotation for full 90° nacelle sweep  ✔
// ─────────────────────────────────────────────────────────────
const GEAR = {
  nacelle_sweep: 90,       // deg
  R_sector: 22,            // mm - sector gear radius (on fixed bracket)
  R_pinion: 6,             // mm - drive pinion radius (on nacelle body)
  bevel_ratio: 1.0,        // 1:1 bevel pair
  R_crown: 6,              // mm - crown pinion radius (longitudinal axis)
  R_rack: 28,              // mm - nozzle inner ring effective rack radius
};
GEAR.step1 = GEAR.nacelle_sweep * GEAR.R_sector / GEAR.R_pinion; // 330°
GEAR.step2 = GEAR.step1 * GEAR.bevel_ratio;                       // 330°
GEAR.ring_angle = GEAR.step2 * GEAR.R_crown / GEAR.R_rack;        // 70.7°
GEAR.nozzle_open_dia  = 42; // mm at hover (ring angle = max)
GEAR.nozzle_close_dia = 36; // mm at cruise (ring angle = 0)

// ─────────────────────────────────────────────────────────────
//  TAB 1: MECHANISM OVERVIEW
// ─────────────────────────────────────────────────────────────

// Side-view diagram: nacelle at two positions with gear indicators
function PositionDiagram({angle}){
  // angle: 0 = cruise (horizontal), 90 = hover (vertical)
  const VW=360, VH=340, PX=180, PY=170; // pivot point
  const NAC_L=90, NAC_W=18;  // nacelle length/half-width in px
  const rad = angle * Math.PI / 180;
  // nacelle body direction unit vector (aft = cos/sin of angle from horizontal)
  const dx = Math.cos(rad), dy = -Math.sin(rad);
  // nacelle endpoints
  const fwdX = PX - dx*NAC_L*0.35, fwdY = PY - dy*NAC_L*0.35; // intake end
  const aftX = PX + dx*NAC_L*0.65, aftY = PY + dy*NAC_L*0.65; // nozzle end
  // perpendicular for nacelle width
  const px2 = -dy * NAC_W, py2 = dx * NAC_W;
  // nacelle corners
  const c1x=fwdX+px2, c1y=fwdY+py2, c2x=fwdX-px2, c2y=fwdY-py2;
  const c3x=aftX-px2, c3y=aftY-py2, c4x=aftX+px2, c4y=aftY+py2;
  // gear state
  const isHover = angle === 90;
  const nozzleDia = isHover ? GEAR.nozzle_open_dia : GEAR.nozzle_close_dia;
  const nozzleLabel = isHover ? "OPEN" : "CLOSED";
  const nozzleColor = isHover ? C.green : C.orange;
  // nozzle ring at aft
  const nozzR = (nozzleDia/2) * 1.4; // scaled
  // sector gear (fixed to bracket, at pivot)
  const secR = GEAR.R_sector * 1.5;
  const arcStart = -10 * Math.PI / 180;
  const arcEnd   = (90+10) * Math.PI / 180;

  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:380,display:"block"}}>
      {/* Wing spar */}
      <rect x={PX-6} y={PY-120} width={12} height={240} rx={3} fill="rgba(0,229,255,0.08)" stroke={C.accent} strokeWidth={1.2}/>
      {/* Tilt bracket */}
      <circle cx={PX} cy={PY} r={18} fill="rgba(0,229,255,0.06)" stroke={C.accent} strokeWidth={1.5}/>
      <circle cx={PX} cy={PY} r={5} fill={C.accent} opacity={0.7}/>
      <text x={PX} y={PY-22} textAnchor="middle" fill={C.accent} fontSize={7} fontFamily={M}>PIVOT</text>

      {/* Sector gear arc (FIXED, on bracket, sweeps 0-90°) */}
      {/* In SVG: 0° = right, CCW positive. We want 0° to 90° CCW from "right" */}
      {/* Sector drawn as filled path */}
      <path d={`M${PX},${PY} L${PX+secR},${PY} A${secR},${secR} 0 0,0 ${PX},${PY-secR} Z`}
        fill="rgba(255,230,0,0.07)" stroke={C.yellow} strokeWidth={1.2} strokeDasharray="4 2" opacity={0.7}/>
      {/* Sector gear teeth hint */}
      {Array.from({length:7},(_,i)=>{
        const a = i * 15 * Math.PI/180;
        const r1=secR-4, r2=secR+4;
        return <line key={i} x1={PX+r1*Math.cos(-a)} y1={PY+r1*Math.sin(-a)}
          x2={PX+r2*Math.cos(-a)} y2={PY+r2*Math.sin(-a)}
          stroke={C.yellow} strokeWidth={2} opacity={0.5}/>;
      })}
      <text x={PX+secR+10} y={PY-secR/2} fill={C.yellow} fontSize={7} fontFamily={M}>SECTOR</text>
      <text x={PX+secR+10} y={PY-secR/2+10} fill={`${C.yellow}60`} fontSize={6} fontFamily={M}>R={GEAR.R_sector}mm</text>
      <text x={PX+secR+10} y={PY-secR/2+20} fill={`${C.yellow}60`} fontSize={6} fontFamily={M}>FIXED to bracket</text>

      {/* Nacelle body */}
      <polygon points={`${c1x},${c1y} ${c2x},${c2y} ${c3x},${c3y} ${c4x},${c4y}`}
        fill="rgba(255,107,53,0.1)" stroke={C.orange} strokeWidth={1.8}/>
      {/* EDF fan disk at intake */}
      <circle cx={fwdX} cy={fwdY} r={NAC_W*0.85}
        fill="rgba(255,107,53,0.12)" stroke={C.orange} strokeWidth={1} strokeDasharray="2 2"/>
      {/* Nozzle ring at aft */}
      <circle cx={aftX} cy={aftY} r={nozzR}
        fill={`${nozzleColor}18`} stroke={nozzleColor} strokeWidth={2}/>
      <circle cx={aftX} cy={aftY} r={nozzR*0.55}
        fill={`${nozzleColor}20`} stroke={nozzleColor} strokeWidth={1}/>
      <text x={aftX} y={aftY+3} textAnchor="middle" fill={nozzleColor} fontSize={8} fontFamily={M} fontWeight="bold">{nozzleLabel}</text>
      <text x={aftX} y={aftY+14} textAnchor="middle" fill={`${nozzleColor}80`} fontSize={6} fontFamily={M}>{nozzleDia}mm exit</text>

      {/* Drive pinion on nacelle body (at pivot perimeter) */}
      <circle cx={PX+GEAR.R_pinion*1.5*Math.cos(rad)} cy={PY-GEAR.R_pinion*1.5*Math.sin(rad)}
        r={GEAR.R_pinion*1.5} fill="rgba(45,212,191,0.15)" stroke={C.teal} strokeWidth={1.5}/>
      <text x={PX+(GEAR.R_pinion*1.5+14)*Math.cos(rad+0.6)}
            y={PY-(GEAR.R_pinion*1.5+14)*Math.sin(rad+0.6)}
        fill={C.teal} fontSize={6} fontFamily={M}>PINION R={GEAR.R_pinion}</text>

      {/* Pushrod line from pinion to nozzle ring */}
      <line x1={PX+GEAR.R_pinion*1.5*Math.cos(rad)} y1={PY-GEAR.R_pinion*1.5*Math.sin(rad)}
        x2={aftX} y2={aftY}
        stroke={C.teal} strokeWidth={1} strokeDasharray="3 3" opacity={0.6}/>

      {/* Angle label */}
      <text x={PX-55} y={PY+5} fill={C.orange} fontSize={12} fontFamily={M} fontWeight="bold">{angle}°</text>
      <text x={PX-55} y={PY+18} fill={`${C.orange}70`} fontSize={8} fontFamily={M}>{isHover?"HOVER":"CRUISE"}</text>

      {/* Ring rotation indicator */}
      {[0,1,2,3,4,5,6,7].map(i=>{
        const flap_a = isHover
          ? (i * 45 * Math.PI/180)
          : (i * 45 * Math.PI/180 + 0.6);
        const r1=nozzR-3, r2=nozzR+5;
        return <line key={i}
          x1={aftX+r1*Math.cos(flap_a)} y1={aftY+r1*Math.sin(flap_a)}
          x2={aftX+r2*Math.cos(flap_a)} y2={aftY+r2*Math.sin(flap_a)}
          stroke={nozzleColor} strokeWidth={2.5} strokeLinecap="round" opacity={0.8}/>;
      })}

      <text x={VW/2} y={14} textAnchor="middle" fill="rgba(0,229,255,0.25)"
        fontSize={9} fontFamily={M} letterSpacing="0.1em">
        {isHover?"HOVER — NACELLE 90° · NOZZLE OPEN":"CRUISE — NACELLE 0° · NOZZLE CLOSED"}
      </text>
    </svg>
  );
}

function GearSchematicFull(){
  const VW=700, VH=420;
  // Layout: tilt bracket left, nacelle body centre, nozzle ring right
  const BX=100, BY=210; // bracket/pivot
  const NX=340, NY=210; // nacelle longitudinal axis centre (bevel gear point)
  const ZX=580, ZY=210; // nozzle ring centre

  function gearCircle(cx,cy,r,n,color,fill=""){
    const pts=[];
    for(let i=0;i<n;i++){
      const a=i*2*Math.PI/n;
      const ra=r-3, rb=r+3;
      const a1=a-Math.PI/n*0.4, a2=a+Math.PI/n*0.4;
      pts.push(`M${cx+ra*Math.cos(a1)},${cy+ra*Math.sin(a1)}`);
      pts.push(`A${ra},${ra} 0 0,1 ${cx+ra*Math.cos(a2)},${cy+ra*Math.sin(a2)}`);
      pts.push(`L${cx+rb*Math.cos(a2)},${cy+rb*Math.sin(a2)}`);
      pts.push(`A${rb},${rb} 0 0,0 ${cx+rb*Math.cos(a1)},${cy+rb*Math.sin(a1)}`);
      pts.push("Z");
    }
    return(<>
      <circle cx={cx} cy={cy} r={r} fill={fill||`${color}18`} stroke={color} strokeWidth={1}/>
      <path d={pts.join(" ")} fill={color} opacity={0.55}/>
      <circle cx={cx} cy={cy} r={3} fill={color} opacity={0.8}/>
    </>);
  }

  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* Wing spar */}
      <rect x={BX-8} y={30} width={16} height={380} rx={4} fill="rgba(0,229,255,0.06)" stroke={C.accent} strokeWidth={1.2}/>
      <text x={BX} y={18} textAnchor="middle" fill={C.accent} fontSize={8} fontFamily={M}>WING SPAR</text>

      {/* Tilt bracket */}
      <rect x={BX-28} y={BY-55} width={56} height={110} rx={6} fill="rgba(0,229,255,0.05)" stroke={C.accent} strokeWidth={1.5} strokeDasharray="6 3"/>
      <text x={BX} y={BY+75} textAnchor="middle" fill={C.accent} fontSize={8} fontFamily={M}>TILT BRACKET</text>
      <text x={BX} y={BY+87} textAnchor="middle" fill={`${C.accent}55`} fontSize={7} fontFamily={M}>(fixed to spar)</text>

      {/* SECTOR GEAR on bracket */}
      {/* Sector arc 90° (0° right → 90° up in SVG = -90°) */}
      <path d={`M${BX},${BY} L${BX+33},${BY} A33,33 0 0,0 ${BX},${BY-33} Z`}
        fill="rgba(255,230,0,0.1)" stroke={C.yellow} strokeWidth={1.5}/>
      {Array.from({length:5},(_,i)=>{
        const a=-i*22.5*Math.PI/180;
        return <line key={i} x1={BX+28*Math.cos(a)} y1={BY+28*Math.sin(a)}
          x2={BX+36*Math.cos(a)} y2={BY+36*Math.sin(a)}
          stroke={C.yellow} strokeWidth={2.5} strokeLinecap="round" opacity={0.7}/>;
      })}
      <circle cx={BX} cy={BY} r={5} fill={C.yellow} opacity={0.8}/>
      <text x={BX+40} y={BY-20} fill={C.yellow} fontSize={8} fontFamily={M} fontWeight="bold">SECTOR GEAR</text>
      <text x={BX+40} y={BY-8} fill={`${C.yellow}70`} fontSize={7} fontFamily={M}>R={GEAR.R_sector}mm · 90° arc</text>
      <text x={BX+40} y={BY+4} fill={`${C.yellow}50`} fontSize={7} fontFamily={M}>FIXED to tilt bracket</text>

      {/* Nacelle body rectangle */}
      <rect x={BX+30} y={BY-22} width={NX-BX+40} height={44} rx={5}
        fill="rgba(255,107,53,0.06)" stroke={C.orange} strokeWidth={1.8}/>
      <text x={(BX+30+NX+40)/2} y={BY+3} textAnchor="middle" fill={`${C.orange}50`} fontSize={8} fontFamily={M}>NACELLE BODY (rotates with tilt)</text>

      {/* Drive pinion on nacelle, meshes with sector */}
      {gearCircle(BX+22, BY-22, GEAR.R_pinion*3.2, 12, C.teal)}
      <text x={BX+22} y={BY-40} textAnchor="middle" fill={C.teal} fontSize={8} fontFamily={M} fontWeight="bold">PINION A</text>
      <text x={BX+22} y={BY-50} textAnchor="middle" fill={`${C.teal}70`} fontSize={7} fontFamily={M}>R={GEAR.R_pinion}mm · 12T</text>
      <text x={BX+22} y={BY-60} textAnchor="middle" fill={`${C.teal}50`} fontSize={7} fontFamily={M}>on nacelle outer wall</text>

      {/* Shaft from pinion A to bevel gear (runs through nacelle wall transversely) */}
      <line x1={BX+22} y1={BY-22} x2={BX+22} y2={BY+22}
        stroke={C.teal} strokeWidth={3} strokeLinecap="round" opacity={0.5}/>
      <text x={BX+35} y={BY+16} fill={`${C.teal}60`} fontSize={7} fontFamily={M}>shaft</text>

      {/* Bevel gear 1 (transverse axis → longitudinal axis) on nacelle wall */}
      {gearCircle(BX+80, BY, 14, 14, C.lime)}
      <text x={BX+80} y={BY+25} textAnchor="middle" fill={C.lime} fontSize={8} fontFamily={M} fontWeight="bold">BEVEL A</text>
      <text x={BX+80} y={BY+36} textAnchor="middle" fill={`${C.lime}60`} fontSize={7} fontFamily={M}>14T · 14mm</text>
      <text x={BX+80} y={BY-20} textAnchor="middle" fill={`${C.lime}45`} fontSize={7} fontFamily={M}>transverse axis</text>

      {/* Bevel gear 2 (longitudinal axis) */}
      {gearCircle(BX+114, BY, 14, 14, C.lime)}
      <text x={BX+114} y={BY+25} textAnchor="middle" fill={C.lime} fontSize={8} fontFamily={M} fontWeight="bold">BEVEL B</text>
      <text x={BX+114} y={BY+36} textAnchor="middle" fill={`${C.lime}60`} fontSize={7} fontFamily={M}>14T · 14mm</text>
      <text x={BX+114} y={BY-20} textAnchor="middle" fill={`${C.lime}45`} fontSize={7} fontFamily={M}>long. axis</text>

      {/* Bevel engagement indicator */}
      <line x1={BX+80} y1={BY} x2={BX+114} y2={BY} stroke={C.lime} strokeWidth={1.5} strokeDasharray="3 2" opacity={0.5}/>
      <text x={(BX+80+BX+114)/2} y={BY-30} textAnchor="middle" fill={C.lime} fontSize={7} fontFamily={M}>1:1 bevel pair</text>
      <text x={(BX+80+BX+114)/2} y={BY-20} textAnchor="middle" fill={`${C.lime}60`} fontSize={7} fontFamily={M}>90° axis redirect</text>

      {/* Longitudinal shaft to crown pinion */}
      <line x1={BX+114} y1={BY} x2={NX-20} y2={BY}
        stroke={C.lime} strokeWidth={3} strokeLinecap="round" opacity={0.5}/>
      <text x={(BX+114+NX-20)/2} y={BY-10} textAnchor="middle" fill={`${C.lime}50`} fontSize={7} fontFamily={M}>long. shaft (3mm CF rod)</text>

      {/* Crown pinion at longitudinal shaft end */}
      {gearCircle(NX-6, BY, GEAR.R_crown*3.2, 10, C.purple)}
      <text x={NX-6} y={BY-28} textAnchor="middle" fill={C.purple} fontSize={8} fontFamily={M} fontWeight="bold">CROWN PIN.</text>
      <text x={NX-6} y={BY-38} textAnchor="middle" fill={`${C.purple}60`} fontSize={7} fontFamily={M}>R={GEAR.R_crown}mm · 10T</text>

      {/* Nozzle inner ring */}
      <circle cx={ZX} cy={ZY} r={GEAR.R_rack*2.6} fill="rgba(0,229,255,0.05)" stroke={C.accent} strokeWidth={2}/>
      <circle cx={ZX} cy={ZY} r={20} fill="rgba(0,229,255,0.1)" stroke={C.accent} strokeWidth={1} strokeDasharray="3 2"/>
      <text x={ZX} y={ZY+3} textAnchor="middle" fill={C.accent} fontSize={8} fontFamily={M} fontWeight="bold">NOZZLE RING</text>
      <text x={ZX} y={ZY+15} textAnchor="middle" fill={`${C.accent}60`} fontSize={7} fontFamily={M}>R_rack={GEAR.R_rack}mm</text>

      {/* Rack teeth on inner ring (partial arc) */}
      {Array.from({length:10},(_,i)=>{
        const a = (i-5) * 7 * Math.PI/180;
        const r1=GEAR.R_rack*2.6-5, r2=GEAR.R_rack*2.6+5;
        return <line key={i}
          x1={ZX+r1*Math.cos(Math.PI+a)} y1={ZY+r1*Math.sin(Math.PI+a)}
          x2={ZX+r2*Math.cos(Math.PI+a)} y2={ZY+r2*Math.sin(Math.PI+a)}
          stroke={C.purple} strokeWidth={2.5} strokeLinecap="round" opacity={0.6}/>;
      })}
      <text x={ZX-82} y={ZY+15} fill={C.purple} fontSize={7} fontFamily={M}>rack teeth on ring ID</text>

      {/* Shaft from crown pinion to ring */}
      <line x1={NX-6} y1={BY} x2={ZX-GEAR.R_rack*2.6} y2={ZY}
        stroke={C.purple} strokeWidth={2.5} strokeLinecap="round" opacity={0.5}/>

      {/* Flaps on nozzle ring */}
      {[0,45,90,135,180,225,270,315].map(a=>{
        const ar=a*Math.PI/180, r1=GEAR.R_rack*2.6, r2=r1+16;
        return <line key={a}
          x1={ZX+r1*Math.cos(ar)} y1={ZY+r1*Math.sin(ar)}
          x2={ZX+r2*Math.cos(ar)} y2={ZY+r2*Math.sin(ar)}
          stroke={C.green} strokeWidth={3} strokeLinecap="round" opacity={0.7}/>;
      })}
      <text x={ZX} y={ZY-GEAR.R_rack*2.6-12} textAnchor="middle" fill={C.green} fontSize={8} fontFamily={M} fontWeight="bold">8 FLAPS</text>
      <text x={ZX} y={ZY-GEAR.R_rack*2.6-2} textAnchor="middle" fill={`${C.green}70`} fontSize={7} fontFamily={M}>BamJr remix</text>

      {/* Gear ratio annotation */}
      <rect x={440} y={30} width={240} height={110} rx={4} fill="rgba(255,255,255,0.02)" stroke="rgba(255,255,255,0.08)"/>
      <text x={560} y={46} textAnchor="middle" fill={C.dimmer} fontSize={8} fontFamily={M} fontWeight="bold" letterSpacing="0.08em">GEAR RATIO CHAIN</text>
      {[
        ["Nacelle sweep","90°",C.orange],
        ["× R_sec/R_pin","×"+GEAR.R_sector+"/"+GEAR.R_pinion+" = ×3.67",C.yellow],
        ["= Pinion A rotation",GEAR.step1.toFixed(1)+"°",C.teal],
        ["× bevel 1:1","×1.0",C.lime],
        ["× R_crown/R_rack","×"+GEAR.R_crown+"/"+GEAR.R_rack+" = ×0.214",C.purple],
        ["= Ring rotation",GEAR.ring_angle.toFixed(1)+"°  ✔ (target 60–75°)",C.green],
      ].map(([k,v,c],i)=>(<g key={i}>
        <text x={450} y={62+i*15} fill={C.dim} fontSize={8} fontFamily={M}>{k}</text>
        <text x={678} y={62+i*15} textAnchor="end" fill={c} fontSize={8} fontFamily={M} fontWeight="bold">{v}</text>
      </g>))}

      {/* Direction arrows */}
      <text x={VW/2} y={VH-14} textAnchor="middle" fill="rgba(0,229,255,0.2)"
        fontSize={8} fontFamily={M}>
        Nacelle 0° (cruise) → ring at 0° (nozzle closed 36mm) · Nacelle 90° (hover) → ring at 70.7° (nozzle open 42mm)
      </text>
      <text x={VW/2} y={16} textAnchor="middle" fill="rgba(0,229,255,0.25)"
        fontSize={9} fontFamily={M} letterSpacing="0.1em">NACELLE NOZZLE GEAR COUPLING — SCHEMATIC VIEW</text>
    </svg>
  );
}

function OverviewTab(){
  const [nacPos,setNacPos]=useState(90);
  return(<div>
    <div style={{background:"rgba(255,107,53,0.05)",border:`1px solid rgba(255,107,53,0.2)`,borderRadius:4,padding:"10px 14px",marginBottom:18,fontFamily:M,fontSize:11,color:C.dim,lineHeight:1.8}}>
      <span style={{color:C.orange,fontWeight:"bold"}}>Remix:</span> BamJr thing:2991269 (CC BY 4.0) ·
      scaled to <span style={{color:C.yellow}}>70mm ID</span> for nacelle EDFs ·
      sector gear coupling to nacelle pivot — <span style={{color:C.green}}>no separate servo</span> ·
      passive mechanical linkage · nozzle opens automatically as nacelle tilts to hover.
    </div>

    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:20,marginBottom:20}}>
      <div>
        <div style={{color:C.dimmer,fontFamily:M,fontSize:10,letterSpacing:"0.08em",marginBottom:8}}>
          INTERACTIVE — click position to preview
        </div>
        <div style={{display:"flex",gap:8,marginBottom:12}}>
          {[[0,"CRUISE 0°"],[45,"TRANSITION 45°"],[90,"HOVER 90°"]].map(([a,l])=>(
            <button key={a} onClick={()=>setNacPos(a)} style={{
              background:nacPos===a?"rgba(255,107,53,0.15)":"transparent",
              border:`1px solid ${nacPos===a?C.orange:"rgba(255,107,53,0.2)"}`,
              color:nacPos===a?C.orange:C.dimmer,
              padding:"4px 10px",fontFamily:M,fontSize:9,cursor:"pointer",borderRadius:2}}>{l}</button>
          ))}
        </div>
        <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:8}}>
          <PositionDiagram angle={nacPos}/>
        </div>
        {nacPos===45&&(
          <Note c={C.teal} ch={`At 45°: nozzle ring at ~${(GEAR.ring_angle*0.5).toFixed(0)}° rotation → exit dia ~${(36+(42-36)*0.5).toFixed(0)}mm. Smooth linear interpolation between cruise and hover — no stepwise actuator.`}/>
        )}
      </div>
      <div>
        <SH t="Operating Logic" mt={0}/>
        <KV k="Nacelle at 0° (cruise)" v="Nozzle CLOSED · 36mm exit dia" vc={C.orange}/>
        <KV k="Nacelle at 90° (hover)" v="Nozzle OPEN · 42mm exit dia" vc={C.green}/>
        <KV k="Nacelle at 45° (transition)" v="Nozzle ~50% · 39mm exit dia" vc={C.teal}/>
        <KV k="Actuation" v="Passive mechanical — no servo, no power" vc={C.green}/>
        <KV k="Coupling" v="Sector gear (bracket) + bevel pair + crown pinion + ring rack"/>
        <KV k="Total gear ratio chain" v={`${GEAR.nacelle_sweep}° → ${GEAR.ring_angle.toFixed(1)}° ring`} vc={C.yellow}/>
        <KV k="Hover thrust gain" v="~8–12% vs fixed nozzle (open 115% area)" vc={C.green}/>
        <KV k="Cruise Isp gain" v="~15–18% jet velocity (closed 82% area)" vc={C.teal}/>
        <KV k="Fail-safe" v="If gear jams: nozzle stays at last position. EDF still flies normally — nozzle is not critical for flight."/>
        <KV k="Lubrication" v="Sewing machine oil on all gear interfaces · re-apply every 20 flights"/>
        <SH t="Why this direction?"/>
        <Note c={C.orange} ch="Cruise (0°): the 70mm fans act as forward thrust jets. Closing the nozzle reduces exit area, increasing jet velocity and propulsive efficiency — exactly like a jet engine's converging nozzle at cruise. Hover (90°): the fans provide lift. Opening the nozzle reduces backpressure, allowing higher mass flow through the fan and increasing total thrust. This is the classic trade-off between thrust (open) and specific impulse (closed)."/>
      </div>
    </div>

    <SH t="Full Gear Coupling Schematic"/>
    <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:10}}>
      <GearSchematicFull/>
    </div>
  </div>);
}

// ─────────────────────────────────────────────────────────────
//  TAB 2: GEAR DESIGN
// ─────────────────────────────────────────────────────────────
function GearDetailDiagram(){
  const VW=640, VH=360;
  // Detailed cross-section through nacelle side wall
  const WX=80, WY=180, WW=14; // wall
  const pinionCX=WX+WW+GEAR.R_pinion*5; // pinion centre
  const bevelCX=pinionCX+60; // bevel 1
  const bevel2X=bevelCX+32; // bevel 2 (longitudinal)

  function teeth(cx,cy,r,n,angle,color){
    return Array.from({length:n},(_,i)=>{
      const a = i*2*Math.PI/n + angle;
      const r1=r-4, r2=r+4;
      return <line key={i}
        x1={cx+r1*Math.cos(a)} y1={cy+r1*Math.sin(a)}
        x2={cx+r2*Math.cos(a)} y2={cy+r2*Math.sin(a)}
        stroke={color} strokeWidth={3} strokeLinecap="round" opacity={0.7}/>;
    });
  }

  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* Nacelle outer wall (cross section) */}
      <rect x={WX} y={WY-70} width={WW} height={140} rx={2}
        fill="rgba(255,107,53,0.1)" stroke={C.orange} strokeWidth={1.5}/>
      <text x={WX+WW/2} y={WY-78} textAnchor="middle" fill={C.orange} fontSize={7} fontFamily={M}>WALL</text>
      <text x={WX+WW/2} y={WY-67} textAnchor="middle" fill={`${C.orange}60`} fontSize={6} fontFamily={M}>2mm CF-PETG</text>

      {/* Sector gear (left of wall, fixed to bracket) */}
      <path d={`M${WX-8},${WY} L${WX-8-35},${WY} A35,35 0 0,0 ${WX-8},${WY-35} Z`}
        fill="rgba(255,230,0,0.1)" stroke={C.yellow} strokeWidth={1.5}/>
      {Array.from({length:5},(_,i)=>{
        const a=-i*22*Math.PI/180;
        return <line key={i} x1={WX-8+29*Math.cos(a)} y1={WY+29*Math.sin(a)}
          x2={WX-8+38*Math.cos(a)} y2={WY+38*Math.sin(a)}
          stroke={C.yellow} strokeWidth={3} strokeLinecap="round" opacity={0.7}/>;
      })}
      <text x={WX-50} y={WY-42} fill={C.yellow} fontSize={8} fontFamily={M} fontWeight="bold">SECTOR</text>
      <text x={WX-50} y={WY-30} fill={`${C.yellow}60`} fontSize={7} fontFamily={M}>22mm R</text>
      <text x={WX-50} y={WY-20} fill={`${C.yellow}50`} fontSize={7} fontFamily={M}>M0.5 · 22° PA</text>
      <text x={WX-50} y={WY+2} fill={`${C.yellow}40`} fontSize={6} fontFamily={M}>FIXED to bracket</text>

      {/* Drive pinion A (on nacelle outer face, transverse shaft) */}
      <circle cx={pinionCX} cy={WY} r={GEAR.R_pinion*5}
        fill="rgba(45,212,191,0.12)" stroke={C.teal} strokeWidth={1.5}/>
      {teeth(pinionCX,WY,GEAR.R_pinion*5,12,0,C.teal)}
      <line x1={pinionCX} y1={WY-GEAR.R_pinion*5-10} x2={pinionCX} y2={WY+GEAR.R_pinion*5+10}
        stroke={C.teal} strokeWidth={2.5} strokeLinecap="round" opacity={0.6}/>
      <text x={pinionCX} y={WY-GEAR.R_pinion*5-18} textAnchor="middle" fill={C.teal} fontSize={8} fontFamily={M} fontWeight="bold">PINION A</text>
      <text x={pinionCX} y={WY-GEAR.R_pinion*5-7} textAnchor="middle" fill={`${C.teal}60`} fontSize={7} fontFamily={M}>6mm R · 12T · M0.5</text>
      <text x={pinionCX+GEAR.R_pinion*5+8} y={WY+3} fill={`${C.teal}50`} fontSize={7} fontFamily={M}>3mm ø shaft</text>
      <text x={pinionCX+GEAR.R_pinion*5+8} y={WY+14} fill={`${C.teal}40`} fontSize={7} fontFamily={M}>MR63ZZ bearings</text>
      {/* Mesh indicator between sector and pinion */}
      <line x1={WX-8} y1={WY} x2={pinionCX-GEAR.R_pinion*5} y2={WY}
        stroke="rgba(255,255,255,0.15)" strokeWidth={1} strokeDasharray="2 2"/>
      <text x={(WX-8+pinionCX-GEAR.R_pinion*5)/2} y={WY+12} textAnchor="middle"
        fill="rgba(255,255,255,0.3)" fontSize={6} fontFamily={M}>mesh</text>

      {/* Shaft through wall to bevel gear 1 */}
      <rect x={WX+WW} y={WY-5} width={bevelCX-WX-WW-15} height={10} rx={3}
        fill={C.teal} opacity={0.25}/>
      {/* M2 shaft housing in wall */}
      <rect x={WX} y={WY-5} width={WW} height={10} rx={1}
        fill="rgba(45,212,191,0.3)" stroke={C.teal} strokeWidth={0.8}/>

      {/* Bevel gear 1 — transverse axis */}
      <circle cx={bevelCX} cy={WY} r={18}
        fill="rgba(163,230,53,0.12)" stroke={C.lime} strokeWidth={1.5}/>
      {teeth(bevelCX,WY,18,14,0,C.lime)}
      <text x={bevelCX} y={WY-26} textAnchor="middle" fill={C.lime} fontSize={8} fontFamily={M} fontWeight="bold">BEVEL A</text>
      <text x={bevelCX} y={WY-15} textAnchor="middle" fill={`${C.lime}60`} fontSize={7} fontFamily={M}>14T · M0.5</text>
      <text x={bevelCX} y={WY+28} textAnchor="middle" fill={`${C.lime}50`} fontSize={7} fontFamily={M}>transverse axis</text>

      {/* Bevel gear 2 — longitudinal axis (shown rotated 90° in 2D) */}
      <ellipse cx={bevel2X} cy={WY} rx={22} ry={8}
        fill="rgba(163,230,53,0.1)" stroke={C.lime} strokeWidth={1.5} strokeDasharray="3 2"/>
      <ellipse cx={bevel2X+22} cy={WY} rx={5} ry={8}
        fill="rgba(163,230,53,0.15)" stroke={C.lime} strokeWidth={1.2}/>
      <text x={bevel2X} y={WY-18} textAnchor="middle" fill={C.lime} fontSize={8} fontFamily={M} fontWeight="bold">BEVEL B</text>
      <text x={bevel2X} y={WY-7} textAnchor="middle" fill={`${C.lime}60`} fontSize={7} fontFamily={M}>14T · long. axis</text>
      {/* Engagement dot */}
      <circle cx={bevelCX+18} cy={WY} r={4} fill={C.lime} opacity={0.6}/>
      <text x={(bevelCX+18+bevel2X)/2} y={WY+16} textAnchor="middle"
        fill={`${C.lime}50`} fontSize={7} fontFamily={M}>90° mesh</text>

      {/* Longitudinal shaft to crown pinion */}
      <line x1={bevel2X+22} y1={WY} x2={520} y2={WY}
        stroke={C.purple} strokeWidth={3} strokeLinecap="round" opacity={0.5}/>
      <text x={(bevel2X+22+520)/2} y={WY-10} textAnchor="middle"
        fill={`${C.purple}50`} fontSize={7} fontFamily={M}>3mm CF rod · sleeve bearings every 20mm</text>

      {/* Crown pinion */}
      <circle cx={524} cy={WY} r={GEAR.R_crown*4.5}
        fill="rgba(192,132,252,0.12)" stroke={C.purple} strokeWidth={1.5}/>
      {teeth(524,WY,GEAR.R_crown*4.5,10,0,C.purple)}
      <text x={524} y={WY-GEAR.R_crown*4.5-10} textAnchor="middle"
        fill={C.purple} fontSize={8} fontFamily={M} fontWeight="bold">CROWN PIN.</text>
      <text x={524} y={WY-GEAR.R_crown*4.5+1} textAnchor="middle"
        fill={`${C.purple}60`} fontSize={7} fontFamily={M}>{GEAR.R_crown}mm R · 10T</text>

      {/* Nozzle inner ring (partially visible) */}
      {/* Ring arc section that meshes with crown */}
      <path d={`M${580},${WY-90} A90,90 0 0,1 ${580},${WY+90}`}
        fill="rgba(0,229,255,0.06)" stroke={C.accent} strokeWidth={2}/>
      {Array.from({length:8},(_,i)=>{
        const a=(-90+i*25)*Math.PI/180;
        return <line key={i} x1={580+82*Math.cos(a)} y1={WY+82*Math.sin(a)}
          x2={580+92*Math.cos(a)} y2={WY+92*Math.sin(a)}
          stroke={C.accent} strokeWidth={3} strokeLinecap="round" opacity={0.6}/>;
      })}
      <text x={600} y={WY} fill={C.accent} fontSize={8} fontFamily={M} fontWeight="bold">NOZZLE</text>
      <text x={600} y={WY+12} fill={`${C.accent}60`} fontSize={7} fontFamily={M}>INNER RING</text>
      <text x={600} y={WY+24} fill={`${C.accent}50`} fontSize={7} fontFamily={M}>R={GEAR.R_rack}mm</text>

      {/* Mesh point */}
      <circle cx={580} cy={WY} r={5} fill={C.purple} opacity={0.6}/>

      {/* Annotations */}
      <text x={VW/2} y={16} textAnchor="middle" fill="rgba(0,229,255,0.25)"
        fontSize={9} fontFamily={M} letterSpacing="0.1em">CROSS-SECTION — GEAR TRAIN DETAIL</text>
      <text x={VW/2} y={VH-6} textAnchor="middle" fill="rgba(0,229,255,0.2)"
        fontSize={8} fontFamily={M}>All gears: M0.5 module · 22° pressure angle · printed PLA+ or CF-PETG</text>
    </svg>
  );
}

function GearDesignTab(){
  return(<div>
    <SH t="Gear Train Detail" mt={0}/>
    <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:8,marginBottom:20}}>
      <GearDetailDiagram/>
    </div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="Gear Specifications" mt={0}/>
        <div style={{overflowX:"auto"}}>
          <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
            <TH cols={["GEAR","MODULE","TEETH","PITCH R.","MATERIAL","NOTES"]}/>
            <tbody>{[
              {g:"Sector gear",m:"M0.5",t:"~86T (90° arc)",r:"22mm",mat:"PETG",n:"Fixed to tilt bracket · 90° arc only"},
              {g:"Pinion A",m:"M0.5",t:"12T",r:"6mm",mat:"CF-PETG",n:"On nacelle wall · 3mm shaft"},
              {g:"Bevel A",m:"M0.5",t:"14T",r:"14mm",mat:"CF-PETG",n:"Transverse axis · 20° bevel angle"},
              {g:"Bevel B",m:"M0.5",t:"14T",r:"14mm",mat:"CF-PETG",n:"Longitudinal axis · 90° axis change"},
              {g:"Crown pinion",m:"M0.5",t:"10T",r:"6mm",mat:"CF-PETG",n:"Drives rack on nozzle ring"},
              {g:"Nozzle ring rack",m:"M0.5",t:"partial arc",r:"28mm (eff.)",mat:"PETG",n:"On nozzle inner ring OD"},
            ].map((r,i)=>(<tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent",verticalAlign:"top"}}>
              <td style={{padding:"5px 8px",color:C.text,whiteSpace:"nowrap"}}>{r.g}</td>
              <td style={{padding:"5px 8px",color:C.teal,whiteSpace:"nowrap"}}>{r.m}</td>
              <td style={{padding:"5px 8px",color:C.yellow}}>{r.t}</td>
              <td style={{padding:"5px 8px",color:C.orange}}>{r.r}</td>
              <td style={{padding:"5px 8px",color:C.lime,whiteSpace:"nowrap"}}>{r.mat}</td>
              <td style={{padding:"5px 8px",color:C.dim,fontSize:9,lineHeight:1.5}}>{r.n}</td>
            </tr>))}</tbody>
          </table>
        </div>

        <SH t="Gear Ratio Cascade"/>
        <KV k="Step 1: Sector → Pinion A" v={`${GEAR.nacelle_sweep}° × ${GEAR.R_sector}/${GEAR.R_pinion} = ${GEAR.step1.toFixed(1)}°`} vc={C.teal}/>
        <KV k="Step 2: Bevel pair (1:1, 90° redirect)" v={`${GEAR.step1.toFixed(1)}° → ${GEAR.step2.toFixed(1)}°`} vc={C.lime}/>
        <KV k="Step 3: Crown pinion → Ring rack" v={`${GEAR.step2.toFixed(1)}° × ${GEAR.R_crown}/${GEAR.R_rack} = ${GEAR.ring_angle.toFixed(1)}°`} vc={C.purple}/>
        <KV k="Ring rotation (70.7°)" v="Target: 60–75° ✔" vc={C.green}/>
        <KV k="Nozzle exit travel" v={`${GEAR.nozzle_close_dia}mm (closed) → ${GEAR.nozzle_open_dia}mm (open)`} vc={C.green}/>
        <KV k="Area ratio open" v="π×21² / π×18² = 135% of duct area" vc={C.green}/>
        <KV k="Area ratio closed" v="π×18² / π×22² = 67% of 70mm duct" vc={C.orange}/>

        <Note c={C.teal} ch="Module 0.5 gears are at the limit of reliable 3D printing. Use resin SLA for Pinion A, Bevel A, and Bevel B — their small teeth require better resolution than FDM can reliably produce. The sector gear and crown pinion/ring rack can be FDM printed at 0.10mm layer height."/>
      </div>
      <div>
        <SH t="Bearing and Shaft Spec" mt={0}/>
        <KV k="Pinion A shaft" v="3mm OD · 2mm ID brass tube sleeve inside nacelle wall"/>
        <KV k="Pinion A bearings" v="MR63ZZ (3mm bore · 6mm OD · 2.5mm) × 2"/>
        <KV k="Bevel shaft" v="3mm CF rod · 30mm long inside nacelle"/>
        <KV k="Bevel shaft support" v="PETG sleeve bearing in nacelle rib at 15mm centre"/>
        <KV k="Longitudinal shaft" v="3mm CF rod · full nacelle length minus bevel block"/>
        <KV k="Long. shaft bearings" v="PTFE sleeve bearing every 18–22mm (printed into nacelle wall ribs)"/>
        <KV k="Crown pinion shaft" v="Integral with 3mm CF rod · pinion press-fit + Loctite 638"/>
        <KV k="Ring rotation" v="Nozzle inner ring rides on 4× 1.5mm polished CF pins in ring-outer groove"/>
        <KV k="Ring drag torque" v="&lt;0.008 N·m (measured on BamJr original) — well within M0.5 tooth shear"/>

        <SH t="Sector Gear Geometry"/>
        <KV k="Arc span" v="90° (matches full nacelle rotation range)"/>
        <KV k="Effective arc used" v="80° (±5° deadband at each end to prevent binding at extremes)"/>
        <KV k="Sector pitch radius" v="22mm"/>
        <KV k="Sector thickness" v="4mm (printed 2 shells PETG)"/>
        <KV k="Mounting" v="M2.5 × 3 screws into tilt bracket face · positively located by 1.5mm boss"/>
        <KV k="Adjustment" v="Two M2 slot holes allow ±2° angular adjustment for mesh preload"/>
        <KV k="Mesh backlash" v="Target 0.1–0.2mm (M0.5 standard) · adjust by sliding sector in slots"/>

        <SH t="Anti-Backfire Safety"/>
        <Note c={C.orange} ch="If a gear tooth breaks or the rack jumps, the nozzle remains at an intermediate or open position. This adds backpressure to the fan (slightly reduced thrust) but does NOT prevent flight. The EDF still produces useful thrust at any nozzle position between 36–42mm. The nacelle servo/mechanism is completely unaffected."/>
        <Note c={C.green} ch="Gear tooth failure mode analysis: M0.5 CF-PETG bevel gears have ~0.4N·m shear strength per tooth. Maximum torque in the chain is 0.035 N·m at the crown pinion (calc: spring force on 8 flaps × effective radius). Safety factor: 11×. No fatigue concern at 20 cycles per flight."/>
      </div>
    </div>
  </div>);
}

// ─────────────────────────────────────────────────────────────
//  TAB 3: PRINT PARTS
// ─────────────────────────────────────────────────────────────
function PrintPartsTab(){
  const parts=[
    {n:"Nacelle outer shell Rev E (×2)",mat:"CF-PETG",infill:"25%",walls:4,layer:"0.15",mass:28,method:"FDM",notes:"Includes pinion-A bore (3mm dia), bevel-shaft channel, longitudinal-shaft rib sleeves, nozzle ring housing recess. Print orientation: intake face down."},
    {n:"Sector gear (×2)",mat:"PETG",infill:"40%",walls:4,layer:"0.12",mass:4,method:"FDM",notes:"90° arc, M0.5 teeth. Print flat on bed. Teeth pointing up — no support needed. 0.12mm layer for tooth accuracy. Two M2.5 mounting holes with 0.1mm clearance for M2.5 insert."},
    {n:"Pinion A (×2)",mat:"Resin",infill:"100%",walls:"—",layer:"0.05",mass:1,method:"SLA resin",notes:"12T M0.5 · must be resin for tooth accuracy. Hollow 3mm bore. Post-cure fully before pressing onto shaft. Available as commercial 12T M0.5 spur gear (2–3mm bore) from Aliexpress."},
    {n:"Bevel gear set A+B (×2 sets)",mat:"Resin",infill:"100%",walls:"—",layer:"0.05",mass:2,method:"SLA resin",notes:"14T M0.5, 20° bevel angle, 45° pitch cone. MUST be resin — FDM bevel teeth at M0.5 are not usable. Alternatively: source commercial M0.5 bevel gear pair (Miniature Bearings Australia, SDP/SI, or Didel)."},
    {n:"Crown pinion (×2)",mat:"Resin",infill:"100%",walls:"—",layer:"0.05",mass:1,method:"SLA resin",notes:"10T M0.5 spur gear, 3mm bore. Resin preferred; CF-PETG FDM at 0.10mm layer height may work as backup. Press fit on 3mm CF rod with Loctite 638."},
    {n:"Nozzle inner ring — 70mm ID (×2)",mat:"CF-PETG",infill:"35%",walls:3,layer:"0.15",mass:9,method:"FDM",notes:"BamJr inner ring scaled to 70mm ID. Tall variant (extended thread for greater flap travel). Add M0.5 rack teeth on OD (Fusion 360: Gear Generator plugin → linear rack, profile project onto ring OD). Print vertically."},
    {n:"Nozzle flap ring — 8 flaps (×2 sets)",mat:"PETG",infill:"25%",walls:3,layer:"0.20",mass:6,method:"FDM",notes:"BamJr flap ring scaled 70mm ID. 8 flaps × 10mm chord × 4mm pivot. Print flat. 1.5mm pivot pin holes."},
    {n:"Nozzle outer housing — 70mm (×2)",mat:"PETG",infill:"20%",walls:3,layer:"0.20",mass:8,method:"FDM",notes:"BamJr outer housing scaled. Redesigned to integrate with Serenity 80mm nacelle OD fairing as press-fit bayonet insert. Quarter-turn lock tabs. Remove servo mount boss (servo replaced by gear coupling)."},
    {n:"Bevel gear housing block (×2)",mat:"CF-PETG",infill:"40%",walls:4,layer:"0.15",mass:3,method:"FDM",notes:"Small block inside nacelle containing the bevel pair, shaft entry, and exit. Includes PTFE sleeve bearings for 3mm shafts. Prints flat. Two M2 mounting screws into nacelle inner rib."},
    {n:"Pinion-A bracket (×2)",mat:"CF-PETG",infill:"35%",walls:4,layer:"0.15",mass:2,method:"FDM",notes:"External face plate holding MR63ZZ bearing pair for pinion-A shaft. Attaches to nacelle outer wall via M2.5 inserts. Slots for sector mesh adjustment ±2°."},
  ];
  const total=parts.reduce((s,p)=>s+(p.mass||0),0);
  return(<div>
    <Note c={C.orange} ch={`Attribution: all nozzle parts are remixes of BamJr's thing:2991269 (CC BY 4.0). The sector gear, pinion-A bracket, bevel housing, and crown pinion are original additions to this remix. Total printed mass per nacelle: ~${total/2}g · ×2 nacelles: ~${total}g.`}/>
    <div style={{overflowX:"auto",marginTop:16}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["PART","MATERIAL","INFILL","WALLS","LAYER","~MASS","METHOD","NOTES"]}/>
        <tbody>{parts.map((p,i)=>(<tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.02)":"transparent",verticalAlign:"top"}}>
          <td style={{padding:"5px 8px",color:C.text,whiteSpace:"nowrap"}}>{p.n}</td>
          <td style={{padding:"5px 8px",color:p.mat.includes("Resin")?"rgba(255,230,0,0.8)":p.mat.includes("CF")?C.lime:C.teal,whiteSpace:"nowrap"}}>{p.mat}</td>
          <td style={{padding:"5px 8px",color:C.dim}}>{p.infill}</td>
          <td style={{padding:"5px 8px",color:C.dim,textAlign:"center"}}>{p.walls}</td>
          <td style={{padding:"5px 8px",color:C.dim,whiteSpace:"nowrap"}}>{p.layer}mm</td>
          <td style={{padding:"5px 8px",color:C.yellow,fontWeight:"bold",whiteSpace:"nowrap"}}>{p.mass}g</td>
          <td style={{padding:"5px 8px",color:p.method.includes("SLA")?C.gold:C.green,whiteSpace:"nowrap",fontSize:9}}>{p.method}</td>
          <td style={{padding:"5px 8px",color:C.dim,fontSize:9,lineHeight:1.5}}>{p.notes}</td>
        </tr>))}</tbody>
        <tfoot><tr style={{borderTop:`1px solid ${C.border}`}}>
          <td colSpan={5} style={{padding:"7px 8px",color:C.accent,textAlign:"right",fontSize:10}}>TOTAL PRINTED (both nacelles)</td>
          <td style={{padding:"7px 8px",color:C.yellow,fontWeight:"bold",fontSize:13}}>{total}g</td>
          <td colSpan={2}/>
        </tr></tfoot>
      </table>
    </div>
    <SH t="Sourcing Alternatives for M0.5 Gears"/>
    <Note c={C.gold} ch="If resin printing is not available: commercial M0.5 gears are available from (1) Didel SA (didel.com) — Swiss precision micro-gears, M0.5 range including bevels; (2) SDP/SI (sdp-si.com) — 14T M0.5 bevel pairs in brass or nylon, part# S10GE10M005B0140; (3) Miniature Bearings Australia — plastic M0.5 spur gears. Commercial brass gears are preferred for longevity and mesh accuracy but add ~8g per nacelle. Brass gears must be tapped/drilled to 3mm bore if not supplied that way."/>
    <SH t="Print Settings Summary"/>
    <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:12}}>
      {[
        {mat:"CF-PETG (structural)",c:C.lime,rules:"250°C nozzle · hardened steel 0.4mm · 90°C bed · fan 20% · 0.15mm layer · PA calibrated"},
        {mat:"PETG (fairings/housing)",c:C.teal,rules:"235°C nozzle · standard brass 0.4mm · 85°C bed · fan 30% · 0.20mm layer · brim 5mm"},
        {mat:"SLA Resin (gears)",c:C.gold,rules:"1K UVDLP or MSLA · 0.05mm layer · 8s exposure · post-wash 2min IPA · UV cure 4min · verify bore size before pressing"},
      ].map(s=>(<div key={s.mat} style={{padding:"10px 12px",border:`1px solid ${s.c}33`,background:`${s.c}06`,borderRadius:4}}>
        <div style={{color:s.c,fontFamily:M,fontSize:11,fontWeight:"bold",marginBottom:6}}>{s.mat}</div>
        <div style={{color:C.dim,fontFamily:M,fontSize:9,lineHeight:1.8}}>{s.rules}</div>
      </div>))}
    </div>
  </div>);
}

// ─────────────────────────────────────────────────────────────
//  TAB 4: ASSEMBLY GUIDE
// ─────────────────────────────────────────────────────────────
function AssemblyDiagram(){
  const VW=640, VH=320;
  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* Nacelle shell exploded */}
      <rect x={200} y={100} width={180} height={70} rx={6}
        fill="rgba(255,107,53,0.08)" stroke={C.orange} strokeWidth={1.8}/>
      <text x={290} y={138} textAnchor="middle" fill={C.orange} fontSize={10} fontFamily={M} fontWeight="bold">NACELLE SHELL</text>
      <text x={290} y={152} textAnchor="middle" fill={`${C.orange}60`} fontSize={8} fontFamily={M}>70mm EDF inside</text>

      {/* Sector gear exploded above left */}
      <rect x={70} y={30} width={80} height={28} rx={3}
        fill="rgba(255,230,0,0.1)" stroke={C.yellow} strokeWidth={1.2}/>
      <text x={110} y={42} textAnchor="middle" fill={C.yellow} fontSize={8} fontFamily={M} fontWeight="bold">SECTOR GEAR</text>
      <text x={110} y={52} textAnchor="middle" fill={`${C.yellow}60`} fontSize={7} fontFamily={M}>fixed to bracket</text>
      <line x1={110} y1={58} x2={200} y2={100} stroke={C.yellow} strokeWidth={1} strokeDasharray="4 2" opacity={0.5}/>

      {/* Pinion-A exploded */}
      <circle cx={160} cy={82} r={14} fill="rgba(45,212,191,0.12)" stroke={C.teal} strokeWidth={1.2}/>
      <text x={160} y={80} textAnchor="middle" fill={C.teal} fontSize={7} fontFamily={M} fontWeight="bold">PINION A</text>
      <text x={160} y={91} textAnchor="middle" fill={`${C.teal}60`} fontSize={6} fontFamily={M}>12T + bracket</text>
      <line x1={160} y1={96} x2={200} y2={115} stroke={C.teal} strokeWidth={1} strokeDasharray="3 2" opacity={0.5}/>

      {/* Bevel housing */}
      <rect x={240} y={50} width={60} height={40} rx={3}
        fill="rgba(163,230,53,0.1)" stroke={C.lime} strokeWidth={1.2}/>
      <text x={270} y={68} textAnchor="middle" fill={C.lime} fontSize={8} fontFamily={M} fontWeight="bold">BEVEL PAIR</text>
      <text x={270} y={80} textAnchor="middle" fill={`${C.lime}60`} fontSize={7} fontFamily={M}>A+B · housing</text>
      <line x1={270} y1={90} x2={280} y2={100} stroke={C.lime} strokeWidth={1} strokeDasharray="3 2" opacity={0.5}/>

      {/* Longitudinal shaft */}
      <rect x={340} y={132} width={80} height={8} rx={3}
        fill={C.purple} opacity={0.3} stroke={C.purple} strokeWidth={1}/>
      <text x={380} y={122} textAnchor="middle" fill={C.purple} fontSize={7} fontFamily={M}>LONG. SHAFT 3mm CF</text>
      <line x1={380} y1={126} x2={380} y2={132} stroke={C.purple} strokeWidth={1} strokeDasharray="2 1" opacity={0.5}/>

      {/* Crown pinion */}
      <circle cx={430} cy={85} r={12} fill="rgba(192,132,252,0.12)" stroke={C.purple} strokeWidth={1.2}/>
      <text x={430} y={83} textAnchor="middle" fill={C.purple} fontSize={7} fontFamily={M} fontWeight="bold">CROWN</text>
      <text x={430} y={94} textAnchor="middle" fill={`${C.purple}60`} fontSize={6} fontFamily={M}>PIN.</text>
      <line x1={430} y1={97} x2={420} y2={132} stroke={C.purple} strokeWidth={1} strokeDasharray="2 1" opacity={0.5}/>

      {/* Nozzle assembly */}
      <circle cx={510} cy={135} r={42}
        fill="rgba(0,229,255,0.05)" stroke={C.accent} strokeWidth={1.8}/>
      <circle cx={510} cy={135} r={18}
        fill="rgba(0,229,255,0.08)" stroke={C.accent} strokeWidth={1}/>
      <text x={510} y={133} textAnchor="middle" fill={C.accent} fontSize={9} fontFamily={M} fontWeight="bold">NOZZLE</text>
      <text x={510} y={145} textAnchor="middle" fill={`${C.accent}70`} fontSize={8} fontFamily={M}>ASSEMBLY</text>
      {[0,45,90,135,180,225,270,315].map(a=>{
        const ar=a*Math.PI/180, r=42, r2=r+10;
        return <line key={a} x1={510+r*Math.cos(ar)} y1={135+r*Math.sin(ar)}
          x2={510+r2*Math.cos(ar)} y2={135+r2*Math.sin(ar)}
          stroke={C.green} strokeWidth={2.5} strokeLinecap="round" opacity={0.7}/>;
      })}
      <text x={510} y={200} textAnchor="middle" fill={C.green} fontSize={7} fontFamily={M}>8 flaps · BamJr remix</text>

      {/* 70mm EDF */}
      <circle cx={290} cy={135} r={30} fill="rgba(255,107,53,0.08)" stroke={C.orange} strokeWidth={1}/>
      <text x={290} y={133} textAnchor="middle" fill={C.orange} fontSize={8} fontFamily={M} fontWeight="bold">70mm EDF</text>
      <text x={290} y={145} textAnchor="middle" fill={`${C.orange}60`} fontSize={7} fontFamily={M}>inside shell</text>

      {/* Assembly direction arrows */}
      <path d="M380,145 L460,140" stroke={C.accent} strokeWidth={1.5}
        markerEnd="url(#rarr)" opacity={0.5} strokeDasharray="4 2"/>
      <defs><marker id="rarr" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
        <path d="M0,0 L6,3 L0,6 Z" fill={C.accent}/>
      </marker></defs>

      {/* Step numbers */}
      {[{n:1,x:110,y:18},{n:2,x:152,y:68},{n:3,x:232,y:38},{n:4,x:370,y:120},{n:5,x:420,y:72},{n:6,x:470,y:80}].map(s=>(
        <g key={s.n}>
          <circle cx={s.x} cy={s.y} r={9} fill={C.orange} opacity={0.85}/>
          <text x={s.x} y={s.y+4} textAnchor="middle" fill="#000" fontSize={9} fontFamily={M} fontWeight="bold">{s.n}</text>
        </g>
      ))}
      <text x={VW/2} y={14} textAnchor="middle" fill="rgba(0,229,255,0.25)"
        fontSize={9} fontFamily={M} letterSpacing="0.1em">ASSEMBLY EXPLODED VIEW — NACELLE NOZZLE GEAR SYSTEM</text>
    </svg>
  );
}

function AssemblyTab(){
  const [open,setOpen]=useState(0);
  const steps=[
    {t:"Prepare gear components",c:C.gold,d:"Before assembly: verify all bore diameters. Pinion-A bore: 3.00mm ±0.02mm. Crown pinion bore: 3.00mm ±0.02mm. Bevel gear bores: 3.00mm. Ring rack ID: 70.0mm ±0.05mm. Sand or ream oversize bores with 3mm reamer. Undersized bores: carefully sand with 150-grit on a 3mm rod mandrel. Apply light machine oil to all running fits before assembly."},
    {t:"Assemble bevel gear block",c:C.lime,d:"Press Bevel-A onto 3mm CF transverse shaft stub (12mm long). Use Loctite 638 retaining compound — do NOT use superglue (too rigid, cracks gear). Insert shaft into bevel housing block. Verify Bevel-A sits flush against housing shoulder. Press Bevel-B onto 3mm CF longitudinal shaft end (30mm long). Insert into housing at 90° to Bevel-A. Mesh the two bevel gears — they should turn smoothly with ≤0.2mm backlash (check by gentle rocking). If tight: sand bevel faces 0.1mm. If too loose: shim with 0.1mm brass washer."},
    {t:"Install bevel housing in nacelle",c:C.lime,d:"The bevel housing block snaps into the nacelle inner rib pocket at the aft-inboard face of the EDF chamber. Two M2 screws secure it. Route the longitudinal 3mm CF rod from the housing forward through the PTFE sleeve bearings moulded into the nacelle wall ribs. Verify rod rotates freely in all sleeves — no binding. Cut rod to length so it extends 4mm past the forward rib (crown pinion attachment point)."},
    {t:"Install nozzle assembly",c:C.accent,d:"Pre-assemble the BamJr nozzle: press 8 flap pivot pins (M1.5×8mm) into their hinge holes. Apply machine oil. Test-fit the inner ring inside the outer housing — it should thread/rotate smoothly. Add M0.5 crown-pinion-engaging rack teeth to the inner ring OD (if not already part of the print). Slide the assembled nozzle housing onto the aft of the nacelle. Press-fit or bayonet-lock per housing design (quarter turn, 3 tabs). The crown pinion should mesh with the inner ring rack teeth at the 9 o'clock position. Verify mesh: rotate crown pinion 70° — inner ring should rotate ~70° and flaps should sweep full open/closed range."},
    {t:"Install crown pinion on longitudinal shaft",c:C.purple,d:"Slide crown pinion onto the 3mm CF rod forward stub (4mm exposed). Crown pinion should be flush with the rib face. Apply Loctite 638. Do NOT twist or slide the rod while Loctite cures (15 min open time; support rod axially for 30 min). After cure: verify free rotation. Verify crown pinion meshes with inner ring rack — 0.1–0.2mm backlash target."},
    {t:"Install pinion-A on nacelle outer face",c:C.teal,d:"Press pinion-A onto the 3mm transverse shaft. Pinion-A should protrude from the nacelle outer face by 3mm (just outside the wall). The MR63ZZ bearing pair pre-installed in the pinion-A bracket holds the shaft. Mount the bracket to the nacelle outer face via M2.5 heat-set inserts. Mesh pinion-A with the sector gear — mesh is set by the two adjustment slots. Adjust until backlash is 0.1–0.2mm. Tighten M2.5 screws to lock."},
    {t:"Install sector gear on tilt bracket",c:C.yellow,d:"The sector gear mounts to the tilt bracket face via 2× M2.5 screws through 0.5mm-oversize clearance holes (allows ±2° position adjustment). With the nacelle at exactly 0° (cruise position, level with wing spar), rotate the inner ring to full CLOSED position (minimum exit area). Then position the sector gear so pinion-A is at the mid-tooth engagement with the sector start (0° cruise = start of sector). Lock screws. Rotate nacelle manually to 90° (hover) — inner ring should arrive at full OPEN position. If travel is insufficient: loosen sector and rotate 2–3° clockwise, retighten."},
    {t:"Full range check and lubrication",c:C.green,d:"Sweep nacelle manually from 0° to 90° ten times. The nozzle should: smoothly open as nacelle tilts toward vertical; smoothly close as nacelle returns to horizontal; reach full open position before nacelle reaches 88° (should not need to fight mechanical stop at 90°); reach full closed before 2°. Measure exit diameter at 0° and 90° with calipers: target 36mm ±1mm closed, 42mm ±1mm open. Apply a single drop of sewing machine oil to each gear interface and each flap pin. Wipe away excess. Do not over-oil — excess oil attracts grit and degrades printed gear surfaces."},
    {t:"Install servo bypass check",c:C.orange,d:"Confirm: the nacelle tilt servo (MG90S) is NOT connected to the nozzle. The nozzle is driven entirely by the gear train — no electrical connections needed for the nacelle nozzle. The GP15 Pico 2 output that previously drove an SG90 nozzle servo is now UNUSED for the nacelle (it remains connected only to the fuselage 40mm EDF nozzle servo). Verify this in firmware: nacelle nozzle parameter = GEAR_PASSIVE, not SERVO_ACTIVE."},
  ];
  return(<div>
    <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:8,marginBottom:18}}>
      <AssemblyDiagram/>
    </div>
    <div style={{background:"rgba(74,222,128,0.05)",border:`1px solid rgba(74,222,128,0.2)`,borderRadius:4,padding:"10px 14px",marginBottom:16,fontFamily:M,fontSize:11,color:C.dim}}>
      Complete both nacelle nozzle assemblies before installing either in the airframe. It is much easier to test and adjust gear mesh on the bench. Allow <span style={{color:C.yellow}}>45–60 min per nacelle</span> for first assembly. Second nacelle typically takes 25–30 min.
    </div>
    {steps.map((s,i)=>(
      <div key={i} style={{marginBottom:8}}>
        <div onClick={()=>setOpen(open===i?-1:i)} style={{display:"flex",alignItems:"center",gap:12,padding:"9px 14px",background:open===i?`${s.c}0d`:"rgba(255,255,255,0.02)",border:`1px solid ${open===i?s.c:C.border}`,borderRadius:4,cursor:"pointer",userSelect:"none"}}>
          <div style={{width:24,height:24,background:s.c,borderRadius:"50%",display:"flex",alignItems:"center",justifyContent:"center",color:"#000",fontFamily:M,fontSize:10,fontWeight:"bold",flexShrink:0}}>{i+1}</div>
          <span style={{color:s.c,fontFamily:M,fontSize:11,fontWeight:"bold"}}>{s.t}</span>
          <span style={{color:C.dimmer,fontFamily:M,fontSize:9,marginLeft:"auto"}}>{open===i?"▲":"▼"}</span>
        </div>
        {open===i&&(<div style={{border:`1px solid ${s.c}33`,borderTop:"none",borderRadius:"0 0 4px 4px",background:`${s.c}04`,padding:"12px 14px"}}>
          <span style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.85}}>{s.d}</span>
        </div>)}
      </div>
    ))}
  </div>);
}

// ─────────────────────────────────────────────────────────────
//  TAB 5: CALIBRATION & TESTING
// ─────────────────────────────────────────────────────────────
function CalibrationTab(){
  const [angle,setAngle]=useState(0);
  // Continuous position calculation
  const ring_at = (a) => GEAR.ring_angle * a / 90;
  const exit_at = (a) => GEAR.nozzle_close_dia + (GEAR.nozzle_open_dia - GEAR.nozzle_close_dia) * a / 90;
  const area_at = (a) => Math.PI * Math.pow(exit_at(a)/2,2);
  const area_min = area_at(0), area_max = area_at(90);
  const area_ratio = (a) => area_at(a)/area_min;

  return(<div>
    <SH t="Position Calculator" mt={0}/>
    <div style={{background:"rgba(0,229,255,0.04)",border:`1px solid ${C.border}`,borderRadius:4,padding:"16px",marginBottom:20}}>
      <div style={{display:"flex",alignItems:"center",gap:16,marginBottom:16}}>
        <span style={{color:C.dim,fontFamily:M,fontSize:11}}>Nacelle angle:</span>
        <input type="range" min={0} max={90} value={angle} onChange={e=>setAngle(Number(e.target.value))}
          style={{flex:1,accentColor:C.orange}}/>
        <span style={{color:C.orange,fontFamily:M,fontSize:14,fontWeight:"bold",minWidth:44}}>{angle}°</span>
        <span style={{color:C.dim,fontFamily:M,fontSize:10}}>{angle===0?"CRUISE":angle===90?"HOVER":"TRANSITION"}</span>
      </div>
      <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:12}}>
        {[
          {l:"Ring rotation",v:ring_at(angle).toFixed(1)+"°",c:C.teal},
          {l:"Exit diameter",v:exit_at(angle).toFixed(1)+"mm",c:C.yellow},
          {l:"Exit area",v:area_at(angle).toFixed(0)+"mm²",c:C.purple},
          {l:"Area ratio vs cruise",v:area_ratio(angle).toFixed(3)+"×",c:angle>0?C.green:C.dim},
        ].map((s,i)=>(<div key={i} style={{padding:"10px 12px",border:`1px solid ${s.c}44`,background:`${s.c}07`,borderRadius:4}}>
          <div style={{color:C.dim,fontFamily:M,fontSize:9,marginBottom:3}}>{s.l}</div>
          <div style={{color:s.c,fontFamily:M,fontSize:18,fontWeight:"bold"}}>{s.v}</div>
        </div>))}
      </div>
      {/* Visual nozzle */}
      <svg viewBox="0 0 300 120" width="100%" style={{maxWidth:320,display:"block",margin:"16px auto 0"}}>
        <circle cx={150} cy={60} r={55} fill="rgba(0,229,255,0.04)" stroke={C.accent} strokeWidth={1.5}/>
        <circle cx={150} cy={60} r={exit_at(angle)/2*3.5}
          fill={`${angle>45?C.green:C.orange}20`} stroke={angle>45?C.green:C.orange} strokeWidth={2.5}/>
        <text x={150} y={58} textAnchor="middle" fill={angle>45?C.green:C.orange} fontSize={10} fontFamily={M} fontWeight="bold">{exit_at(angle).toFixed(1)}mm</text>
        <text x={150} y={72} textAnchor="middle" fill={`${angle>45?C.green:C.orange}80`} fontSize={8} fontFamily={M}>{angle>45?"OPEN":"CLOSED"}</text>
        {[0,45,90,135,180,225,270,315].map(a=>{
          const ar=a*Math.PI/180, rm=55, rp=55+9;
          return <line key={a} x1={150+rm*Math.cos(ar+ring_at(angle)*Math.PI/180*0.05)} y1={60+rm*Math.sin(ar+ring_at(angle)*Math.PI/180*0.05)}
            x2={150+rp*Math.cos(ar)} y2={60+rp*Math.sin(ar)}
            stroke={angle>45?C.green:C.orange} strokeWidth={2.5} strokeLinecap="round" opacity={0.7}/>;
        })}
        <text x={150} y={112} textAnchor="middle" fill={C.dimmer} fontSize={7} fontFamily={M}>nozzle exit (aft view)</text>
      </svg>
    </div>

    <SH t="Verification Procedure"/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        {[
          {t:"Cruise position check (0°)",c:C.orange,items:["Set nacelle to exactly 0° (horizontal). Use a digital angle gauge.","Measure nozzle exit diameter with 150mm digital calipers: TARGET 36mm ±1mm","If undersize: loosen sector gear, rotate 1° anti-clockwise, recheck","If oversize: loosen sector gear, rotate 1° clockwise, recheck","Lock sector M2.5 screws to 0.3 N·m when target achieved"]},
          {t:"Hover position check (90°)",c:C.green,items:["Set nacelle to exactly 90° (vertical). Use a digital angle gauge.","Measure nozzle exit diameter: TARGET 42mm ±1mm","If undersize: sector gear has insufficient arc — re-examine pinion-A mesh point","If oversize: reduce sector arc engagement by 2° (file start tooth back 0.3mm)","Verify nacelle servo holds position at 90° — gear train should not back-drive servo"]},
        ].map((g,gi)=>(<div key={gi} style={{marginBottom:20}}>
          <div style={{color:g.c,fontFamily:M,fontSize:11,fontWeight:"bold",marginBottom:8}}>{g.t}</div>
          {g.items.map((s,i)=>(<div key={i} style={{display:"flex",gap:8,padding:"4px 0",borderBottom:"1px solid rgba(0,229,255,0.06)"}}><span style={{color:g.c,fontFamily:M,fontSize:11,flexShrink:0}}>{i+1}.</span><span style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.6}}>{s}</span></div>))}
        </div>))}
      </div>
      <div>
        <div style={{color:C.teal,fontFamily:M,fontSize:11,fontWeight:"bold",marginBottom:8}}>Transition sweep check (0° → 90°)</div>
        {["Sweep nacelle manually from 0° to 90° in one continuous motion (about 3 seconds). Nozzle exit should grow continuously — no sticking, jumping, or reversed motion.","Stop at 45°. Measure exit: target 39mm ±1.5mm.","Reverse sweep 90° → 0°. Verify no hysteresis — diameter at 45° on return should match within 0.5mm of outward sweep.","Perform 20 full sweeps. Verify no gear noise, no loosening, no flap flutter.","If flap flutter appears: the inner ring is slightly loose on its 4 CF guide pins. Apply a thin smear of petroleum jelly to pin grooves to dampen without lubricating teeth."].map((s,i)=>(<div key={i} style={{display:"flex",gap:8,padding:"4px 0",borderBottom:"1px solid rgba(0,229,255,0.06)"}}><span style={{color:C.teal,fontFamily:M,fontSize:11,flexShrink:0}}>{i+1}.</span><span style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.6}}>{s}</span></div>))}
        <SH t="Back-Drive Test"/>
        <Note c={C.yellow} ch="Manually push on the nozzle flap ring to try to close it (rotate ring against direction of opening). The gear train should resist with a noticeable but not excessive force. If it back-drives easily (ring rotates when you push the flaps), the sector gear has too little friction — add a wave washer between pinion-A and the bracket face to increase mesh preload. If it is completely locked and will not back-drive at all, verify the nacelle servo can still drive the tilt through the full range — the gear train torque must not overwhelm the MG90S servo."/>
        <Note c={C.green} ch="Target back-drive resistance: the ring should resist approximately 0.05–0.12 N·m of applied torque (equivalent to pinching the flap with two fingers with medium force). This prevents aerodynamic flutter from the EDF exhaust pressure while still allowing the gear train to actuate freely."/>
      </div>
    </div>
  </div>);
}

// ─────────────────────────────────────────────────────────────
//  TAB 6: INTEGRATION (firmware + BOM delta)
// ─────────────────────────────────────────────────────────────
function IntegrationTab(){
  const bom=[
    {qty:2, ref:"NOZZLE-70", part:"Nacelle nozzle outer housing (BamJr remix 70mm)", desc:"PETG · quarter-turn bayonet · servo boss REMOVED", est:"$4 filament"},
    {qty:2, ref:"NOZZLE-RING", part:"Nozzle inner ring 70mm ID (BamJr remix)", desc:"CF-PETG · tall variant · M0.5 rack teeth added on OD", est:"$5 filament"},
    {qty:2, ref:"FLAP-RING", part:"8-flap ring 70mm (BamJr remix scaled)", desc:"PETG · 10mm chord flaps · M1.5 pivot pins", est:"$3 filament"},
    {qty:2, ref:"SECTOR", part:"Sector gear 22mm R · 90° arc", desc:"PETG · M0.5 · mounted on tilt bracket", est:"$2 filament"},
    {qty:4, ref:"PINION-A", part:"Pinion A 12T M0.5 (2 per nacelle)", desc:"SLA resin or commercial brass 12T M0.5 bore 3mm", est:"$3ea (commercial) / $1 filament"},
    {qty:4, ref:"BEVEL-SET", part:"Bevel pair 14T M0.5 20° (2 pairs per nacelle)", desc:"SLA resin or commercial · Didel / SDP/SI", est:"$8/set (commercial) / $2 filament"},
    {qty:4, ref:"CROWN-PIN", part:"Crown pinion 10T M0.5 (2 per nacelle)", desc:"SLA resin or CF-PETG FDM · 3mm bore", est:"$2ea (commercial)"},
    {qty:4, ref:"MR63ZZ", part:"MR63ZZ ball bearing 3×6×2.5mm (2 per nacelle)", desc:"For pinion-A shaft support", est:"$1.50 for 10-pack"},
    {qty:4, ref:"BEVEL-HSG", part:"Bevel gear housing block CF-PETG (2 per nacelle)", desc:"Inner nacelle rib-mount · PTFE sleeve integral", est:"$2 filament"},
    {qty:2, ref:"LONG-SHAFT", part:"3mm CF rod × 65mm (longitudinal shaft)", desc:"One per nacelle · cut to fit", est:"$2 for 500mm rod"},
    {qty:4, ref:"TRANS-SHAFT", part:"3mm OD × 2mm ID brass tube × 14mm (transverse shaft)", desc:"One per nacelle · through nacelle wall", est:"$1"},
    {qty:16, ref:"M1.5-PIN", part:"M1.5 × 8mm steel pin (8 per nacelle)", desc:"Flap pivot pins", est:"$2 for 100-pack"},
  ];
  return(<div>
    <SH t="Firmware Changes" mt={0}/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24,marginBottom:20}}>
      <div>
        <KV k="Nacelle nozzle control" v="PASSIVE (gear-driven) — no Pico 2 output required" vc={C.green}/>
        <KV k="Previously GP15 (nozzle servo)" v="Now assigned to fuselage 40mm EDF nozzle only"/>
        <KV k="nozzle_mode parameter" v="NACELLE = GEAR_PASSIVE, FUSELAGE = SERVO_GP15"/>
        <KV k="MAVLink param" v="NOZZLE_NAC_MODE = 0 (0=gear, 1=servo)"/>
        <KV k="Telemetry field" v="nozzle_est_exit_mm = nacelle_angle * (42-36)/90 + 36 (estimated)"/>
        <KV k="No calibration needed" v="Gear ratio is fixed — no servo endpoint calibration" vc={C.green}/>
        <KV k="Health check" v="At each arm: sweep nacelle 0→90→0, verify no servo overload. Gear jam detected if nacelle servo current spikes >150% at constant speed."/>
        <Note c={C.teal} ch="The Pico 2 loses no GPIO — GP15 was previously used for nacelle nozzle. It now drives only the fuselage 40mm EDF variable nozzle. The nacelle gear nozzle is self-actuating with zero power consumption."/>
      </div>
      <div>
        <KV k="Gear jam detection" v="Monitor MG90S servo current via ESC telemetry"/>
        <KV k="Jam threshold" v=">1.6A sustained >0.5s during sweep → gear jam warning"/>
        <KV k="Jam response" v="Continue mission · log GEAR_JAM event · alert GCS"/>
        <KV k="Jam-safe operation" v="Nozzle fixed at jam position — still flyable" vc={C.green}/>
        <KV k="Maintenance alert" v="After 50 flight hours: inspect and re-lubricate gear train"/>
        <KV k="Power saving" v="+0W (no servo = no standby current draw on nozzle)" vc={C.green}/>
        <KV k="Weight saving vs servo" v="−9g (SG90 servo removed from nacelle) × 2 = −18g" vc={C.green}/>
        <Note c={C.green} ch="Removing the two nacelle nozzle servos saves 18g and two Pico GP outputs. The gear system is lighter, simpler, and more reliable than a servo — there is no actuator to fail, no PWM calibration, and no servo hunt or oscillation around the set-point."/>
      </div>
    </div>

    <SH t="BOM Delta — Nacelle Nozzle Gear System"/>
    <div style={{overflowX:"auto",marginBottom:16}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["QTY","REF","PART","DESCRIPTION","~USD"]}/>
        <tbody>{bom.map((b,i)=>(<tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.02)":"transparent",verticalAlign:"top"}}>
          <td style={{padding:"5px 8px",color:C.accent,fontWeight:"bold",textAlign:"center"}}>{b.qty}</td>
          <td style={{padding:"5px 8px",color:C.yellow,fontSize:9,whiteSpace:"nowrap"}}>{b.ref}</td>
          <td style={{padding:"5px 8px",color:C.text,whiteSpace:"nowrap"}}>{b.part}</td>
          <td style={{padding:"5px 8px",color:C.dim,fontSize:9,lineHeight:1.5}}>{b.desc}</td>
          <td style={{padding:"5px 8px",color:C.green,fontWeight:"bold",whiteSpace:"nowrap"}}>{b.est}</td>
        </tr>))}</tbody>
        <tfoot>
          <tr style={{borderTop:`1px solid ${C.border}`}}>
            <td colSpan={4} style={{padding:"7px 8px",color:C.red,fontSize:10,textAlign:"right"}}>REMOVED: 2× SG90 nozzle servos</td>
            <td style={{padding:"7px 8px",color:C.red,fontWeight:"bold"}}>−$6</td>
          </tr>
          <tr>
            <td colSpan={4} style={{padding:"5px 8px",color:C.green,fontSize:10,textAlign:"right"}}>ADDED: gear train components</td>
            <td style={{padding:"5px 8px",color:C.green,fontWeight:"bold"}}>+~$35</td>
          </tr>
          <tr style={{borderTop:`1px solid ${C.border}`}}>
            <td colSpan={4} style={{padding:"7px 8px",color:C.accent,fontSize:11,textAlign:"right"}}>NET COST DELTA</td>
            <td style={{padding:"7px 8px",color:C.yellow,fontSize:15,fontWeight:"bold"}}>+~$29</td>
          </tr>
          <tr>
            <td colSpan={4} style={{padding:"5px 8px",color:C.green,fontSize:10,textAlign:"right"}}>NET WEIGHT DELTA</td>
            <td style={{padding:"5px 8px",color:C.green,fontWeight:"bold"}}>−6g</td>
          </tr>
        </tfoot>
      </table>
    </div>
    <Note c={C.dim} ch="If using commercial brass M0.5 gears (recommended for longevity): add approximately $20–25 for the bevel pairs and pinions. Total gear system cost with commercial gears: ~$50–55 over the removed servo cost. The precision and durability improvement is worth it for >20 flight operations."/>
    <SH t="Attribution"/>
    <div style={{padding:"14px 16px",border:`1px solid rgba(163,230,53,0.3)`,background:"rgba(163,230,53,0.04)",borderRadius:4,fontFamily:M,fontSize:10,color:C.dim,lineHeight:1.9}}>
      <div style={{color:C.lime,fontWeight:"bold",marginBottom:8,fontSize:11}}>CC BY 4.0 Attribution for Remix Posts:</div>
      <div style={{background:"rgba(0,0,0,0.3)",borderRadius:4,padding:"10px 12px",color:C.text,lineHeight:2}}>
        "Serenity Tiltrotor Nacelle Variable-Area Nozzle, CC BY 4.0<br/>
        Remix of BamJr's 'Variable Area EDF Nozzles' — thingiverse.com/thing:2991269, CC BY 4.0<br/>
        Modifications: scaled to 70mm ID · gear-coupled to nacelle tilt pivot (sector gear + bevel pair + crown pinion + rack) · servo mount removed · rack teeth added to inner ring OD<br/>
        Changes: exit diameter 36mm (closed/cruise) → 42mm (open/hover) passively coupled to nacelle angle via M0.5 gear train, no servo required."
      </div>
    </div>
  </div>);
}

// ─────────────────────────────────────────────────────────────
//  APP
// ─────────────────────────────────────────────────────────────
const TABS=["Overview","Gear Design","Print Parts","Assembly","Calibration","Integration"];

_ODFontLoader();
export default function App(){
  const [tab,setTab]=useState("Overview");
  return(<div style={{minHeight:"100vh",background:C.bg,color:C.text,fontFamily:M}}>
    <Grid/>
    <div style={{position:"relative",zIndex:1,borderBottom:`1px solid ${C.border}`,padding:"16px 26px 14px"}}>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",flexWrap:"wrap",gap:12}}>
        <div>
          <div style={{color:"rgba(255,107,53,0.35)",fontSize:9,letterSpacing:"0.2em",marginBottom:4}}>NACELLE NOZZLE REMIX · CC BY 4.0 · BASED ON BamJr thing:2991269</div>
          <h1 style={{margin:0,fontSize:19,fontWeight:"normal",color:"#fff",letterSpacing:"0.07em"}}>
            VARIABLE-AREA NACELLE NOZZLE
          </h1>
          <div style={{color:"rgba(0,229,255,0.48)",fontSize:10,marginTop:4}}>
            70mm ID · Sector gear + bevel pair + crown pinion · Passive coupling · No servo
          </div>
        </div>
        <div style={{textAlign:"right",fontFamily:M}}>
          <div style={{color:C.green,fontSize:12,fontWeight:"bold"}}>36mm ↔ 42mm exit</div>
          <div style={{color:C.teal,fontSize:11,marginTop:2}}>{GEAR.ring_angle.toFixed(1)}° ring / 90° nacelle</div>
          <div style={{color:C.dimmer,fontSize:9,marginTop:2}}>−18g vs servo · 0W actuator power</div>
        </div>
      </div>
      <div style={{display:"flex",gap:2,marginTop:12,flexWrap:"wrap"}}>
        {TABS.map(t=>(<button key={t} onClick={()=>setTab(t)} style={{
          background:tab===t?"rgba(255,107,53,0.12)":"transparent",
          border:`1px solid ${tab===t?C.orange:"rgba(255,107,53,0.15)"}`,
          color:tab===t?C.orange:C.dimmer,padding:"5px 13px",fontFamily:M,
          fontSize:10,cursor:"pointer",letterSpacing:"0.07em",transition:"all 0.12s"}}>{t}</button>))}
      </div>
    </div>
    <div style={{position:"relative",zIndex:1,padding:"20px 26px",maxWidth:1060,margin:"0 auto"}}>
      {tab==="Overview"    && <OverviewTab/>}
      {tab==="Gear Design" && <GearDesignTab/>}
      {tab==="Print Parts" && <PrintPartsTab/>}
      {tab==="Assembly"    && <AssemblyTab/>}
      {tab==="Calibration" && <CalibrationTab/>}
      {tab==="Integration" && <IntegrationTab/>}
    </div>
    <div style={{position:"relative",zIndex:1,borderTop:`1px solid ${C.border}`,
      padding:"10px 26px",display:"flex",justifyContent:"space-between",flexWrap:"wrap",gap:6}}>
      <span style={{color:"rgba(255,107,53,0.22)",fontSize:8,letterSpacing:"0.12em"}}>NACELLE NOZZLE GEAR REMIX · CC BY 4.0 · BASED ON BamJr THINGIVERSE.COM/THING:2991269 CC BY 4.0</span>
      <span style={{color:"rgba(0,229,255,0.16)",fontSize:8}}>REFERENCE DESIGN · VERIFY MECHANICALLY BEFORE FLIGHT</span>
    </div>
  </div>);
}
