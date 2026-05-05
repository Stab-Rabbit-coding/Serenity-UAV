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

// ── tokens ───────────────────────────────────────────────────
const C = {
  bg:"#060810", border:"rgba(0,229,255,0.11)", accent:"#00e5ff",
  orange:"#ff6b35", yellow:"#ffe600", purple:"#c084fc", green:"#4ade80",
  pink:"#f472b6", teal:"#2dd4bf", red:"#f87171", lime:"#a3e635",
  gold:"#fbbf24", dim:"rgba(255,255,255,0.92)", dimmer:"rgba(255,255,255,0.82)",
  text:"rgba(255,255,255,0.95)",
};
const M = "'OpenDyslexic Mono','OpenDyslexicMono','Courier New',monospace";
const MB_FONT = "'OpenDyslexic Bold','OpenDyslexic',sans-serif";

// ── Unit helpers ──────────────────────────────────────────────
const mmToIn = mm => (mm*0.03937).toFixed(2);
const mmi    = mm => `${mm} mm (${mmToIn(mm)}")`;
const gToLb  = g  => (g/453.592).toFixed(2);
const gLb    = g  => `${g} g (${gToLb(g)} lb)`;
const kts    = ms => `${(ms*1.9438).toFixed(1)} kts`;
const ft     = m  => `${(m*3.2808).toFixed(0)} ft`;
const yd     = m  => `${(m*1.0936).toFixed(0)} yd`;

// ── Canon dimensions (Rev G) ──────────────────────────────────
const DIM = {
  L_MM:   508,   L_IN:  20.00,
  S_MM:   381,   S_IN:  15.00,   // nacelle C-to-C
  W_MM:   117,   W_IN:   4.60,   // max hull width
  H_MM:    81,   H_IN:   3.19,   // max hull height
  ARM_MM: 132,   ARM_IN: 5.20,   // outrigger arm length
  NAC_L:  181,   NAC_IN: 7.12,   // nacelle pod length
  NAC_OD: 120,   NAC_OIN:4.72,   // nacelle pod OD (100mm EDF)
  BELL_D: 106,   BELL_IN:4.17,   // engine bell OD
  PB_L:    97,   PB_W:   70, PB_H: 49,  // payload bay
  KEEL_L: 536,   KEEL_IN:21.10,  // CF keel
  SPAR_L: 142,   SPAR_IN: 5.59,  // each CF spar
  CG_MM:  212,   CG_IN:   8.35,  // target CG from nose
  BAT_TR:  31,   BAT_TIN: 1.22,  // battery rail travel ±mm
};

// ── Weight budget ─────────────────────────────────────────────
const W_ITEMS = [
  ["Hull sections (11× PETG)",           287],
  ["CF keel 6×3mm × 536mm",               21],
  ["CF outrigger spars ×2 × 142mm",       11],
  ["Nacelle pods 120mm OD ×2",             90],
  ["Nozzle hardware + gear sets",          38],
  ["Misc brackets / fasteners",            63],
  ["2× 100mm EDF + motor",               340],
  ["40mm fuselage EDF",                    40],
  ["ESCs (2×75A nacelle + 1×25A fwd)",     75],
  ["Servos + actuation hardware",          55],
  ["BEC 5V 5A + PDB + wiring",             80],
  ["Radios + nav lights + antennas",       33],
  ["8-node electronics stack",            188],
];
const BASE_G = W_ITEMS.reduce((s,[,g])=>s+g, 0);
const BAT_EMPTY = 420;  // 5S 4500mAh
const BAT_CARGO = 271;  // 5S 2800mAh
const PAYLOAD   = 250;
const THRUST    = 4000; // 2× 100mm at 5S, conservative
const AUW_EMPTY = BASE_G + BAT_EMPTY;
const AUW_CARGO = BASE_G + BAT_CARGO + PAYLOAD;
const TW_EMPTY  = (THRUST / AUW_EMPTY).toFixed(2);
const TW_CARGO  = (THRUST / AUW_CARGO).toFixed(2);
const MAX_PAY   = Math.round(THRUST/2.0 - BASE_G - BAT_CARGO);

// ── Primitives ────────────────────────────────────────────────
const SH=({t,c=C.accent,mt=22})=>(
  <div style={{display:"flex",alignItems:"center",gap:10,marginBottom:14,marginTop:mt}}>
    <div style={{width:3,height:17,background:c}}/>
    <span style={{color:c,fontFamily:M,fontSize:13,letterSpacing:"0.1em",textTransform:"uppercase"}}>{t}</span>
  </div>
);
const KV=({k,v,vc=C.text})=>(
  <div style={{display:"flex",justifyContent:"space-between",padding:"5px 0",borderBottom:"1px solid rgba(0,229,255,0.07)",alignItems:"baseline"}}>
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

// ── HULL PROFILE DIAGRAM (top view) ──────────────────────────
function HullProfileDiagram(){
  const VW=800, VH=380, CY=190;
  const SC=0.88, OX=55;
  const HULL=[[0,0],[11,14],[31,25],[56,42],[81,50],[122,51],[167,58],[195,58],
              [230,56],[264,50],[306,40],[351,25],[362,22],[387,33],[424,40],[459,39],[508,31]];
  const xp=mm=>OX+mm*SC;
  const NAC_Y=190.5*SC;

  const up = HULL.map(([x,y])=>`${xp(x).toFixed(1)},${(CY-y*SC*0.5).toFixed(1)}`);
  const lo = [...HULL].reverse().map(([x,y])=>`${xp(x).toFixed(1)},${(CY+y*SC*0.38).toFixed(1)}`);
  const pts = [...up,...lo].join(" ");

  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* Grid */}
      <defs>
        <pattern id="pg" width="16" height="16" patternUnits="userSpaceOnUse">
          <path d="M16 0L0 0 0 16" fill="none" stroke="rgba(0,229,255,0.04)" strokeWidth={0.4}/>
        </pattern>
      </defs>
      <rect width={VW} height={VH} fill="rgba(0,0,0,0)"/>

      {/* Wing arms */}
      {[-1,1].map(side=>{
        const ay=CY+side*NAC_Y;
        const hull_hy=CY+side*58*SC*0.5;
        const ax1=xp(167); const ax2=xp(167+132);
        const nacCX=xp(167+132*0.5+181*0.25);
        const nacRX=181*SC*0.52; const nacRY=60*SC;
        return(<g key={side}>
          <line x1={ax1.toFixed(1)} y1={hull_hy.toFixed(1)} x2={ax2.toFixed(1)} y2={ay.toFixed(1)}
            stroke={C.accent} strokeWidth={6} strokeLinecap="round"/>
          <ellipse cx={nacCX.toFixed(1)} cy={ay.toFixed(1)} rx={nacRX.toFixed(1)} ry={nacRY.toFixed(1)}
            fill={`${C.orange}15`} stroke={C.orange} strokeWidth={2.5}/>
          <ellipse cx={nacCX.toFixed(1)} cy={ay.toFixed(1)} rx={(nacRX*0.75).toFixed(1)} ry={(nacRY*0.68).toFixed(1)}
            fill="none" stroke={C.orange} strokeWidth={1} strokeDasharray="3 2"/>
          {/* Nav light */}
          <circle cx={ax2.toFixed(1)} cy={ay.toFixed(1)} r={8}
            fill={side===-1?"#cc2200":"#00cc00"} opacity={0.95}/>
          <text x={ax2.toFixed(1)} y={(ay+side*20).toFixed(1)} textAnchor="middle"
            fill={side===-1?"#ff6060":"#60ff60"} fontSize={9} fontFamily={M} fontWeight="bold">
            {side===-1?"PORT":"STBD"}</text>
          {/* Arm label */}
          <text x={((ax1+ax2)/2).toFixed(1)} y={(ay+side*34).toFixed(1)} textAnchor="middle"
            fill={`${C.accent}90`} fontSize={8} fontFamily={M}>132mm (5.20")</text>
        </g>);
      })}

      {/* Main hull */}
      <polygon points={pts} fill={`${C.accent}0e`} stroke={C.accent} strokeWidth={2.5}/>

      {/* Cockpit */}
      <ellipse cx={xp(44).toFixed(1)} cy={CY.toFixed(1)} rx={(44*SC).toFixed(1)} ry={(24*SC).toFixed(1)}
        fill="rgba(0,229,255,0.09)" stroke={C.accent} strokeWidth={1.2}/>

      {/* Engine bell */}
      <circle cx={xp(424).toFixed(1)} cy={CY.toFixed(1)} r={(53*SC*0.5).toFixed(1)}
        fill="rgba(255,230,0,0.1)" stroke={C.yellow} strokeWidth={1.8}/>
      <text x={xp(424).toFixed(1)} y={(CY+4).toFixed(1)} textAnchor="middle"
        fill={C.yellow} fontSize={8} fontFamily={M}>40mm EDF</text>

      {/* Pitot */}
      <line x1={xp(0).toFixed(1)} y1={CY} x2={xp(-24).toFixed(1)} y2={CY}
        stroke={C.teal} strokeWidth={3.5} strokeLinecap="round"/>

      {/* CG line */}
      <line x1={xp(212).toFixed(1)} y1={(CY-80).toFixed(1)} x2={xp(212).toFixed(1)} y2={(CY+80).toFixed(1)}
        stroke={C.green} strokeWidth={1.5} strokeDasharray="6 3"/>
      <polygon points={`${xp(212).toFixed(1)},${(CY-80).toFixed(1)} ${(xp(212)-9).toFixed(1)},${(CY-62).toFixed(1)} ${(xp(212)+9).toFixed(1)},${(CY-62).toFixed(1)}`}
        fill={C.green} opacity={0.9}/>
      <text x={xp(212).toFixed(1)} y={(CY-88).toFixed(1)} textAnchor="middle"
        fill={C.green} fontSize={9} fontFamily={M} fontWeight="bold">CG 212mm (8.35")</text>

      {/* Payload bay */}
      <rect x={xp(183).toFixed(1)} y={(CY-14*SC).toFixed(1)} width={(97*SC).toFixed(1)} height={(28*SC).toFixed(1)}
        rx={3} fill="rgba(244,114,182,0.09)" stroke={C.pink} strokeWidth={1} strokeDasharray="3 2"/>
      <text x={xp(231).toFixed(1)} y={(CY+4).toFixed(1)} textAnchor="middle"
        fill={C.pink} fontSize={7.5} fontFamily={M}>PAYLOAD BAY  97×70mm</text>

      {/* Dimension lines */}
      <line x1={xp(0).toFixed(1)} y1={(VH-20).toFixed(1)} x2={xp(508).toFixed(1)} y2={(VH-20).toFixed(1)}
        stroke={C.accent} strokeWidth={0.5} opacity={0.25}/>
      <text x={xp(254).toFixed(1)} y={(VH-7).toFixed(1)} textAnchor="middle"
        fill={C.dimmer} fontSize={8} fontFamily={M}>508 mm (20.00") hull length</text>
      <line x1={28} y1={(CY-NAC_Y).toFixed(1)} x2={28} y2={(CY+NAC_Y).toFixed(1)}
        stroke={C.accent} strokeWidth={0.5} opacity={0.2}/>
      <text x={16} y={(CY+4).toFixed(1)} textAnchor="middle"
        fill={C.dimmer} fontSize={8} fontFamily={M}
        transform={`rotate(-90,16,${CY})`}>381 mm (15.00") nacelle C-to-C</text>

      {/* Scale comparison note */}
      <rect x={VW-190} y={8} width={182} height={56} rx={4}
        fill="rgba(0,0,0,0.55)" stroke="rgba(0,229,255,0.15)" strokeWidth={0.8}/>
      <text x={VW-99} y={24} textAnchor="middle" fill={C.dimmer} fontSize={8} fontFamily={M} letterSpacing="0.5">CANONICAL PROPORTIONS</text>
      <text x={VW-99} y={38} textAnchor="middle" fill={C.lime} fontSize={9} fontFamily={M} fontWeight="bold">Span/Length = 0.75</text>
      <text x={VW-99} y={52} textAnchor="middle" fill={`${C.accent}80`} fontSize={7} fontFamily={M}>vs Rev F: 1.86 (too wide)</text>

      <text x={VW/2} y={14} textAnchor="middle" fill="rgba(0,229,255,0.85)" fontSize={8} fontFamily={M} letterSpacing="2">
        TOP VIEW — CANONICAL PROPORTIONS — REV G</text>
    </svg>
  );
}

// ── TABS ──────────────────────────────────────────────────────
function OverviewTab(){
  const ratio = (DIM.S_MM/DIM.L_MM).toFixed(3);
  return(<div>
    {/* Canon badge */}
    <div style={{background:"rgba(163,230,53,0.07)",border:`1px solid rgba(163,230,53,0.35)`,
      borderRadius:6,padding:"16px 20px",marginBottom:20}}>
      <div style={{color:C.lime,fontFamily:M,fontSize:12,fontWeight:"bold",marginBottom:10,letterSpacing:"0.08em"}}>
        REV G — CANONICAL SERENITY PROPORTIONS
      </div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:20}}>
        <div>
          <KV k="Hull length"          v={`${mmi(DIM.L_MM)}  (20.00")`} vc={C.lime}/>
          <KV k="Nacelle centre-to-centre" v={`${mmi(DIM.S_MM)}  (15.00")`} vc={C.lime}/>
          <KV k="Span/length ratio"    v={`${ratio}  (show ≈0.50 · Rev F was 1.86)`} vc={C.teal}/>
          <KV k="Max hull width"       v={mmi(DIM.W_MM)}/>
          <KV k="Max hull height"      v={mmi(DIM.H_MM)}/>
          <KV k="Outrigger arm"        v={mmi(DIM.ARM_MM)}/>
        </div>
        <div>
          <KV k="EDF upgrade"          v="100mm (required by mass growth)" vc={C.yellow}/>
          <KV k="Total nacelle thrust" v="4000g (2× 2000g @ 5S)" vc={C.green}/>
          <KV k="AUW empty (4500mAh)" v={gLb(AUW_EMPTY)} vc={C.yellow}/>
          <KV k="T/W empty"           v={`${TW_EMPTY}:1`} vc={parseFloat(TW_EMPTY)>=2.0?C.green:C.red}/>
          <KV k="AUW cargo 250g"      v={gLb(AUW_CARGO)}/>
          <KV k="T/W cargo"           v={`${TW_CARGO}:1`} vc={parseFloat(TW_CARGO)>=2.0?C.green:C.yellow}/>
          <KV k="Max payload capacity" v={`${MAX_PAY} g (${gToLb(MAX_PAY)} lb)`} vc={C.lime}/>
        </div>
      </div>
    </div>

    <SH t="Hull Profile — Top View" mt={0}/>
    <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",
      padding:8,marginBottom:20}}>
      <HullProfileDiagram/>
    </div>

    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="Why 100mm EDF?" mt={0} c={C.orange}/>
        <Note c={C.orange} ch="The 39% increase in hull length (365→508mm) scales hull surface area by 1.94×, growing hull mass from ~178g to ~287g. With the 8-node electronics stack (188g unchanged) and other fixed hardware, base mass rises from 741g to 1380g. At this weight, 80mm EDFs (2800g total) give T/W=1.72 — below the 2.0 minimum. 90mm EDFs (3600g) give T/W=2.07 empty but 1.96 cargo. 100mm EDFs at 2000g each (4000g total) give T/W=2.22 empty and 2.10 cargo — comfortable margin at both mission weights."/>
        <Note c={C.lime} ch="Canonical benefit: span/length ratio drops from 1.86 (Rev F) to 0.75 (Rev G). The show's Serenity has a ratio of approximately 0.5–0.57. Ours is 0.75 partly because the nacelles must clear the wider hull body (117mm vs 84mm). The aircraft will look dramatically more like the show's Firefly-class ship."/>
      </div>
      <div>
        <SH t="Revision History" mt={0}/>
        {[
          {r:"A–F","d":"Original design · 70/80mm EDFs · 365×680mm · span/length = 1.86"},
          {r:"G",  "d":"Canonical rescale · 508×381mm (20\"×15\") · 100mm EDFs · span/length = 0.75",cur:true},
        ].map((r,i)=>(
          <div key={i} style={{display:"flex",gap:10,padding:"5px 0",borderBottom:"1px solid rgba(0,229,255,0.07)"}}>
            <span style={{color:r.cur?C.lime:C.dim,fontFamily:M,fontSize:10,minWidth:32,fontWeight:r.cur?"bold":"normal"}}>Rev {r.r}</span>
            <span style={{color:C.dimmer,fontFamily:M,fontSize:10,lineHeight:1.7}}>{r.d}</span>
          </div>
        ))}
        <SH t="Nacelle Arm Change" c={C.accent}/>
        <KV k="Rev F outrigger arm" v="300mm (11.81") each side"/>
        <KV k="Rev G outrigger arm" v={`${DIM.ARM_MM}mm (${mmToIn(DIM.ARM_MM)}") each side`} vc={C.green}/>
        <KV k="Change"              v="−168mm per arm  (56% shorter)" vc={C.lime}/>
        <Note c={C.accent} ch="The dramatically shorter arm (132mm vs 300mm) is what gives Rev G its Serenity-like silhouette. In the show, the nacelles sit close to the hull body — nearly touching the main fuselage. Rev G achieves the same visual relationship at drone scale."/>
      </div>
    </div>
  </div>);
}

function DimensionsTab(){
  const parts = [
    ["Hull length",           DIM.L_MM,   DIM.L_IN,  "20.00\" — canonical target"],
    ["Nacelle C-to-C",       DIM.S_MM,   DIM.S_IN,  "15.00\" — canonical target"],
    ["Max hull width",        DIM.W_MM,   DIM.W_IN,  "at station 167mm from nose"],
    ["Max hull height",       DIM.H_MM,   DIM.H_IN,  "inc. cockpit dome"],
    ["Outrigger arm",         DIM.ARM_MM, DIM.ARM_IN,"hull edge → nacelle centre"],
    ["Nacelle pod length",    DIM.NAC_L,  DIM.NAC_IN,"scaled with hull"],
    ["Nacelle pod OD",        DIM.NAC_OD, DIM.NAC_OIN,"fits 100mm EDF duct"],
    ["Engine bell OD",        DIM.BELL_D, DIM.BELL_IN,"40mm EDF + variable nozzle"],
    ["Payload bay L",         DIM.PB_L,   DIM.PB_L*0.03937, "scaled from 70mm"],
    ["Payload bay W",         DIM.PB_W,   DIM.PB_W*0.03937, "scaled from 50mm"],
    ["Payload bay H",         DIM.PB_H,   DIM.PB_H*0.03937, "scaled from 35mm"],
    ["CF keel length",        DIM.KEEL_L, DIM.KEEL_IN,"6×3mm flat bar"],
    ["CF spar length (ea)",   DIM.SPAR_L, DIM.SPAR_IN,"12mm OD × 2"],
    ["Target CG from nose",   DIM.CG_MM,  DIM.CG_IN, "41.7% of hull length"],
    ["Battery rail travel ±", DIM.BAT_TR, DIM.BAT_TIN,"CG trim adjustment"],
  ];
  return(<div>
    <SH t="Complete Dimension Table" mt={0}/>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["DIMENSION","mm","inches","NOTES"]}/>
        <tbody>{parts.map(([name,mm,inches,note],i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
            <td style={{padding:"5px 9px",color:C.text}}>{name}</td>
            <td style={{padding:"5px 9px",color:C.yellow,fontWeight:"bold"}}>{typeof mm==="number"?mm.toFixed(0):mm}</td>
            <td style={{padding:"5px 9px",color:C.teal}}>{typeof inches==="number"?inches.toFixed(2)+"\"":inches}</td>
            <td style={{padding:"5px 9px",color:C.dim,fontSize:9}}>{note}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
    <SH t="Hull Profile Stations"/>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["STATION (mm from nose)","HALF-WIDTH (mm)","(inches)","FEATURE"]}/>
        <tbody>{[
          [0,0,"-","Nose tip / pitot mount"],
          [11,14,"0.55","Nose cone begin"],
          [31,25,"0.98","Cockpit forward fairing"],
          [56,42,"1.65","Cockpit bay start"],
          [81,50,"1.97","Max cockpit width"],
          [122,51,"2.01","Avionics bay top"],
          [167,58,"2.28","MAX HULL WIDTH — outrigger attach"],
          [195,58,"2.28","Payload bay forward"],
          [230,56,"2.20","Mid-hull"],
          [264,50,"1.97","Aft avionics"],
          [306,40,"1.57","Aft taper begin"],
          [351,25,"0.98","Tail section"],
          [362,22,"0.87","Aft neck narrow"],
          [387,33,"1.30","Engine bell forward"],
          [424,40,"1.57","Engine bell max"],
          [459,39,"1.54","Engine bell aft"],
          [508,31,"1.22","Tail tip / nav light"],
        ].map(([x,y,inches,feat],i)=>(
          <tr key={i} style={{background:x===167?"rgba(163,230,53,0.08)":i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
            <td style={{padding:"5px 9px",color:x===167?C.lime:C.yellow,fontWeight:x===167?"bold":"normal"}}>{x}</td>
            <td style={{padding:"5px 9px",color:x===167?C.lime:C.text,fontWeight:x===167?"bold":"normal"}}>{y}</td>
            <td style={{padding:"5px 9px",color:C.teal}}>{inches}"</td>
            <td style={{padding:"5px 9px",color:x===167?C.lime:C.dim,fontSize:9}}>{feat}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
  </div>);
}

function WeightTab(){
  return(<div>
    <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:12,marginBottom:18}}>
      {[
        {l:"Base mass (no battery)",     v:gLb(BASE_G),     c:C.yellow},
        {l:"AUW empty · 5S 4500mAh",    v:gLb(AUW_EMPTY),  c:C.orange},
        {l:"AUW cargo · 5S 2800mAh",    v:gLb(AUW_CARGO),  c:C.orange},
        {l:"T/W empty",                  v:`${TW_EMPTY}:1`, c:parseFloat(TW_EMPTY)>=2?C.green:C.red},
        {l:"T/W cargo (250g payload)",   v:`${TW_CARGO}:1`, c:parseFloat(TW_CARGO)>=2?C.green:C.yellow},
        {l:"Max payload (T/W≥2.0)",      v:`${MAX_PAY}g (${gToLb(MAX_PAY)} lb)`,  c:C.lime},
      ].map((s,i)=>(
        <div key={i} style={{padding:"10px 12px",border:`1px solid ${s.c}44`,background:`${s.c}07`,borderRadius:4}}>
          <div style={{color:C.dim,fontFamily:M,fontSize:9,marginBottom:3}}>{s.l}</div>
          <div style={{color:s.c,fontFamily:M,fontSize:16,fontWeight:"bold"}}>{s.v}</div>
        </div>
      ))}
    </div>
    <SH t="Full Weight Breakdown" mt={0}/>
    <div style={{overflowX:"auto",marginBottom:18}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["COMPONENT","MASS (g)","(lb)","NOTES"]}/>
        <tbody>{W_ITEMS.map(([name,mass],i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
            <td style={{padding:"5px 9px",color:C.text}}>{name}</td>
            <td style={{padding:"5px 9px",color:C.yellow,fontWeight:"bold"}}>{mass}</td>
            <td style={{padding:"5px 9px",color:C.dimmer}}>{gToLb(mass)}</td>
            <td style={{padding:"5px 9px",color:C.dim,fontSize:9}}>&nbsp;</td>
          </tr>
        ))}
        <tr style={{borderTop:`1px solid ${C.border}`,background:"rgba(163,230,53,0.06)"}}>
          <td style={{padding:"7px 9px",color:C.lime,fontWeight:"bold"}}>BASE MASS (no battery)</td>
          <td style={{padding:"7px 9px",color:C.lime,fontWeight:"bold",fontSize:13}}>{BASE_G}</td>
          <td style={{padding:"7px 9px",color:C.lime,fontWeight:"bold"}}>{gToLb(BASE_G)}</td>
          <td/>
        </tr></tbody>
        <tfoot>{[
          ["+ Battery 5S 4500mAh (empty rec.)", BAT_EMPTY, AUW_EMPTY, TW_EMPTY, C.yellow],
          ["+ Battery 5S 2800mAh + 250g cargo", BAT_CARGO+PAYLOAD, AUW_CARGO, TW_CARGO, C.orange],
        ].map(([label,plus,auw,tw,col],i)=>(
          <tr key={i} style={{borderTop:"1px solid rgba(0,229,255,0.07)",background:`${col}08`}}>
            <td style={{padding:"6px 9px",color:col,fontFamily:M,fontSize:10}}>{label}</td>
            <td style={{padding:"6px 9px",color:col,fontFamily:M,fontSize:10}}>+{plus}</td>
            <td colSpan={2} style={{padding:"6px 9px",color:col,fontFamily:M,fontSize:10}}>
              AUW = {auw}g ({gToLb(auw)} lb)  ·  T/W = {tw}:1
            </td>
          </tr>
        ))}</tfoot>
      </table>
    </div>
    <SH t="vs Rev F Weight Comparison"/>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["PARAMETER","REV F (365mm)","REV G (508mm)","CHANGE"]}/>
        <tbody>{[
          ["Hull length",       "365mm (14.4\")",  "508mm (20.0\")",   "+143mm (+39%)"],
          ["Nacelle C-to-C",   "680mm (26.8\")",  "381mm (15.0\")",   "−299mm (−44%)"],
          ["Span/length ratio","1.86 (too wide)", "0.75 (canonical)", "−1.11 (closer to show)"],
          ["Max hull width",    "84mm (3.31\")",   "117mm (4.60\")",   "+33mm (+39%)"],
          ["Outrigger arm",     "300mm (11.8\")",  "132mm (5.20\")",   "−168mm (−56%)"],
          ["EDF size",          "80mm → 2800g",    "100mm → 4000g",    "+1200g thrust"],
          ["Base mass",         "741g (1.63 lb)",  "1380g (3.04 lb)",  "+639g (+86%)"],
          ["AUW empty",        "1161g (2.56 lb)", "1800g (3.97 lb)",  "+639g (+55%)"],
          ["T/W empty",         "2.41:1",          "2.22:1",           "−0.19 (still ✔)"],
          ["T/W cargo",         "2.22:1",          "2.10:1",           "−0.12 (still ✔)"],
          ["Max payload",       "388g (0.86 lb)",  "349g (0.77 lb)",   "−39g (−10%)"],
        ].map((row,i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
            <td style={{padding:"5px 9px",color:C.dim,whiteSpace:"nowrap"}}>{row[0]}</td>
            <td style={{padding:"5px 9px",color:C.dimmer,fontSize:9}}>{row[1]}</td>
            <td style={{padding:"5px 9px",color:C.text,fontWeight:"bold"}}>{row[2]}</td>
            <td style={{padding:"5px 9px",color:row[3].includes("+")?C.yellow:row[3].includes("✔")?C.green:C.lime,fontSize:9}}>{row[3]}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
    <Good ch="T/W ≥ 2.0 maintained at both empty and cargo missions despite +86% mass growth. The 100mm EDF thrust increase (+43%) more than compensates."/>
  </div>);
}

function BalanceTab(){
  const nodes = [
    {n:1, name:"Node-1 (primary FC+switch)", x1:84, x2:132, mass:71},
    {n:2, name:"Node-2 (nav/IMU)",           x1:178,x2:220, mass:39},
    {n:3, name:"Node-3 (payload ctrl)",       x1:269,x2:310, mass:39},
    {n:4, name:"Node-4 (aft telem)",          x1:366,x2:415, mass:39},
  ];
  const elec_cg = nodes.reduce((s,n)=>{
    const cx=(n.x1+n.x2)/2; return s+cx*n.mass;
  },0) / nodes.reduce((s,n)=>s+n.mass,0);
  return(<div>
    <SH t="Node Placement (scaled from Rev F)" mt={0}/>
    <div style={{overflowX:"auto",marginBottom:18}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["NODE","POSITION","(inches)","MASS","FUNCTION"]}/>
        <tbody>{nodes.map((nd,i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
            <td style={{padding:"5px 9px",color:C.accent,fontWeight:"bold"}}>Node {nd.n}</td>
            <td style={{padding:"5px 9px",color:C.yellow}}>{nd.x1}–{nd.x2}mm</td>
            <td style={{padding:"5px 9px",color:C.teal}}>{(nd.x1*0.03937).toFixed(1)}"–{(nd.x2*0.03937).toFixed(1)}"</td>
            <td style={{padding:"5px 9px",color:C.text}}>{nd.mass}g</td>
            <td style={{padding:"5px 9px",color:C.dim,fontSize:9}}>{nd.name}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="CG Analysis" mt={0} c={C.green}/>
        <KV k="Electronics CG"     v={`${elec_cg.toFixed(0)}mm (${(elec_cg*0.03937).toFixed(2)}")`}/>
        <KV k="Target aero CG"     v={`${DIM.CG_MM}mm (${DIM.CG_IN}") — 41.7% of hull`}/>
        <KV k="CG offset"          v={`${(elec_cg-DIM.CG_MM).toFixed(0)}mm aft of target`} vc={C.yellow}/>
        <KV k="Battery rail ±"     v={`${DIM.BAT_TR}mm (${DIM.BAT_TIN}")`}/>
        <KV k="Correction"         v={`Slide battery ${(elec_cg-DIM.CG_MM).toFixed(0)}mm forward`} vc={C.green}/>
        <KV k="Remaining offset"   v="≈0mm  ✔" vc={C.green}/>
        <Good ch={`Battery rail (±${DIM.BAT_TR}mm) easily compensates the ${(elec_cg-DIM.CG_MM).toFixed(0)}mm electronics CG aft bias.`}/>
      </div>
      <div>
        <SH t="Battery Options" mt={0} c={C.yellow}/>
        {[
          ["5S 4500mAh 35C",420,"Empty/endurance","~7.8 min hover","2.22"],
          ["5S 2800mAh 45C",271,"Cargo 250g","~5.1 min hover","2.10"],
          ["5S 3000mAh 45C",292,"Light cargo","~5.5 min hover","2.06"],
          ["6S 4000mAh 35C",410,"High-perf option","~8.5 min hover","2.47†"],
        ].map(([bat,mass,use,endur,tw],i)=>(
          <div key={i} style={{padding:"8px 10px",marginBottom:6,border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(255,255,255,0.02)"}}>
            <div style={{display:"flex",justifyContent:"space-between",alignItems:"baseline",marginBottom:4}}>
              <span style={{color:C.yellow,fontFamily:M,fontSize:10,fontWeight:"bold"}}>{bat}</span>
              <span style={{color:C.green,fontFamily:M,fontSize:10}}>T/W {tw}</span>
            </div>
            <div style={{display:"flex",justifyContent:"space-between"}}>
              <span style={{color:C.dim,fontFamily:M,fontSize:9}}>{mass}g · {use}</span>
              <span style={{color:C.teal,fontFamily:M,fontSize:9}}>{endur}</span>
            </div>
          </div>
        ))}
        <Note c={C.dim} ch="† 6S option requires verifying 100mm EDF motor KV rating is compatible with 25.2V. Most quality 100mm EDFs accept 4–6S. Verify with manufacturer before use."/>
      </div>
    </div>
  </div>);
}

// ── BOM (changed items only) ──────────────────────────────────
function BomTab(){
  const changed = [
    {ref:"HULL-G",  part:"Hull sections (11× PETG) — 508mm",        pkg:"Print",  est:"$28",  note:"Scaled from 365mm · 287g printed"},
    {ref:"CF-KEEL", part:"CF keel 6×3mm × 536mm (21.1\")",            pkg:"CF bar", est:"$8",   note:"+39% from 385mm"},
    {ref:"CF-SPAR", part:"CF tube 12mm OD × 142mm (5.59\") ×2",       pkg:"CF tube",est:"$4",   note:"56% shorter per arm — saves weight"},
    {ref:"NAC-100", part:"Nacelle pod 100mm EDF — 120mm OD × 181mm",  pkg:"Print",  est:"$12",  note:"Upgraded from 80mm pods"},
    {ref:"EDF-100", part:"100mm EDF + 2600KV BLDC ×2",                pkg:"EDF",    est:"$45ea",note:"~2000g thrust each @ 5S · 5–6S rated"},
    {ref:"ESC-75",  part:"75A BLHeli32 ESC ×2 (nacelle)",             pkg:"ESC",    est:"$28ea",note:"Upgraded from 60A for 100mm EDFs"},
    {ref:"NZL-100", part:"Nozzle inner ring 100mm (BamJr remix)",      pkg:"Print",  est:"$7",   note:"Scaled to 100mm ID"},
    {ref:"NZL-100H",part:"Nozzle outer housing 100mm (BamJr remix)",   pkg:"Print",  est:"$7",   note:"Scaled to 100mm ID"},
    {ref:"PB-97",   part:"Payload bay door 97×70mm",                   pkg:"Print",  est:"$4",   note:"Scaled from 112×42mm"},
    {ref:"TRAY-S",  part:"SENSORHAT-1 mounting tray (46×42mm)",        pkg:"Print",  est:"$2",   note:"Snap-fit in hull"},
    {ref:"TRAY-C",  part:"CM4 node tray (62×52mm)",                    pkg:"Print",  est:"$3",   note:"Per node stack × 4"},
    {ref:"-EDF-80", part:"80mm EDF (removed)",                         pkg:"—",      est:"−$52", note:"Replaced by 100mm"},
    {ref:"-ESC-60", part:"60A ESC (removed)",                          pkg:"—",      est:"−$56", note:"Replaced by 75A"},
    {ref:"-NAC-80", part:"80mm nacelle pods (removed)",                pkg:"—",      est:"−$12", note:"Replaced by 100mm"},
  ];
  const adds = changed.filter(b=>!b.est.startsWith("−"))
    .reduce((s,b)=>{const u=parseFloat(b.est.replace("$","").replace("ea",""))||0; return s+u;},0);
  const subs = changed.filter(b=>b.est.startsWith("−"))
    .reduce((s,b)=>{const u=parseFloat(b.est.replace("−$","").replace("ea",""))||0; return s+u;},0);
  return(<div>
    <Note c={C.accent} ch="Rev G BOM delta — only items that change from Rev F are listed. Electronics stack (8-node), buses, radios, servos, BEC/PDB, and all PCBs are unchanged. Rev G adds hull reprint and propulsion upgrade."/>
    <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:12,marginBottom:14}}>
      {[{l:"New/changed hardware",v:`~$${adds.toFixed(0)}`,c:C.yellow},
        {l:"Removed hardware savings",v:`~−$${subs.toFixed(0)}`,c:C.green},
        {l:"Net delta vs Rev F",v:`~+$${(adds-subs).toFixed(0)}`,c:C.teal}].map((s,i)=>(
        <div key={i} style={{padding:"10px 12px",border:`1px solid ${s.c}44`,background:`${s.c}07`,borderRadius:4}}>
          <div style={{color:C.dim,fontFamily:M,fontSize:9,marginBottom:3}}>{s.l}</div>
          <div style={{color:s.c,fontFamily:M,fontSize:18,fontWeight:"bold"}}>{s.v}</div>
        </div>
      ))}
    </div>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["REF","PART","PKG","COST","NOTES"]}/>
        <tbody>{changed.map((b,i)=>(
          <tr key={i} style={{background:b.est.startsWith("−")?"rgba(248,113,113,0.04)":i%2===0?"rgba(0,229,255,0.02)":"transparent",verticalAlign:"top"}}>
            <td style={{padding:"5px 8px",color:b.est.startsWith("−")?C.red:C.yellow,whiteSpace:"nowrap",fontSize:9}}>{b.ref}</td>
            <td style={{padding:"5px 8px",color:b.est.startsWith("−")?C.red:C.text}}>{b.part}</td>
            <td style={{padding:"5px 8px",color:C.dimmer,whiteSpace:"nowrap",fontSize:9}}>{b.pkg}</td>
            <td style={{padding:"5px 8px",color:b.est.startsWith("−")?C.red:C.green,fontWeight:"bold",whiteSpace:"nowrap"}}>{b.est}</td>
            <td style={{padding:"5px 8px",color:C.dim,fontSize:9}}>{b.note}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
  </div>);
}

// ── HULL & FOAM TAB ───────────────────────────────────────────
function HullFoamTab(){
  const voids=[
    {id:"A",sta:"0–91",dim:"∅ 55 mm bayonet access",former:"EPS 50×30×86 mm",seal:"Waxed EPS + bayonet frame"},
    {id:"B",sta:"91–165",dim:"65×60 mm dorsal void",former:"EPS 55×52×74 mm",seal:"Waxed EPS + M2.5×4 frame"},
    {id:"C",sta:"160–251",dim:"80×55 mm belly void",former:"EPS 70×48×91 mm",seal:"Waxed EPS + hinge frame"},
    {id:"D",sta:"251–320",dim:"65×55 mm dorsal void",former:"EPS 55×47×69 mm",seal:"Waxed EPS + magnet×4 frame"},
    {id:"E",sta:"320–388",dim:"60×50 mm dorsal void",former:"EPS 50×42×68 mm",seal:"Waxed EPS + M2.5×4 frame"},
    {id:"F",sta:"388–457",dim:"EDF bay — no foam",former:"None (open)",seal:"Open for EDF access"},
  ];
  const conduits=[
    {id:"CAN FD",route:"Port keel rail","chain":"Node 1→2→3→4→COMPHAT-SWITCH"},
    {id:"RS-485",route:"Starboard keel rail","chain":"Node 1→2→3→4→COMPHAT-SWITCH"},
    {id:"MIL-STD-1553",route:"Dorsal centre","chain":"Node 1→2→3→4→COMPHAT-SWITCH"},
    {id:"ETH-A",route:"Port side","chain":"Node 1→COMPHAT-SWITCH"},
    {id:"ETH-B",route:"Starboard side","chain":"Node 2→COMPHAT-SWITCH"},
    {id:"PWR",route:"Belly centre","chain":"Battery→BEC→all nodes"},
  ];
  const panels=[
    {id:"A",label:"Nose Bayonet",contents:"Node 1 SENSORHAT-1 + CM4-CARRIER-2, GPS patch antenna, pitot tube fitting"},
    {id:"B",label:"Dorsal Fwd Screw",contents:"Node 2 SENSORHAT-1 + CM4-CARRIER-2, power distribution, pitot line"},
    {id:"C",label:"Cargo Belly Hinge",contents:"Winch motor + spool, payload release servo, downward FPV camera, mission data port"},
    {id:"D",label:"Dorsal Aft Magnet",contents:"Node 3 SENSORHAT-1 + CM4-CARRIER-2, battery slide rail + XT60, main BEC"},
    {id:"E",label:"Aft Service Screw",contents:"Node 4 SENSORHAT-1 + CM4-CARRIER-2, 3× ESCs, bus terminus (CAN/1553/RS485/ETH)"},
    {id:"F",label:"Engine Bell Bayonet",contents:"40 mm EDF assembly, variable nozzle servo, forward FPV bridge camera"},
  ];
  const batOptions=[
    {spec:"6S 4000 mAh 35C",mass:410,auw:1389,tw:"2.45",hover:"~8.5 min hover"},
    {spec:"6S 2800 mAh 45C",mass:295,auw:1274,tw:"2.67",hover:"~5.8 min hover (cargo mission)"},
    {spec:"6S 5000 mAh 30C",mass:530,auw:1509,tw:"2.25",hover:"~10.6 min hover (endurance, empty only)"},
  ];
  return(<div>

    {/* ── Foam Fill Design ── */}
    <SH t="Foam Fill Design" mt={0} c={C.teal}/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:20,marginBottom:4}}>
      <div>
        <KV k="Shell material"         v="1.2 mm PETG thin shell"/>
        <KV k="Fill material"          v="X-30 PU foam, 2 lb/ft³ (0.032 g/cm³)" vc={C.teal}/>
        <KV k="Gross internal volume"  v="1,711 cm³"/>
        <KV k="Net foam volume (after voids)" v="1,309 cm³" vc={C.yellow}/>
        <KV k="Foam mass"              v="41.9 g" vc={C.yellow}/>
        <KV k="Shell mass"             v="143 g"/>
        <KV k="Total hull assembly"    v="213 g" vc={C.lime}/>
      </div>
      <div>
        <KV k="Solid-fill equivalent"  v="~680 g (no voids)"/>
        <KV k="Mass saved by foam fill"v="467 g" vc={C.green}/>
        <KV k="Mix ratio"              v="1:1 by volume"/>
        <KV k="Pot life"               v="2 minutes"/>
        <KV k="Expansion"              v="4× volume"/>
        <KV k="Cure time"              v="24 hours"/>
        <KV k="Max batch size"         v="60 mL (heat-warp limit for PETG)" vc={C.orange}/>
        <KV k="Batches required"       v="3 total"/>
      </div>
    </div>
    <Warn ch="Never exceed 60 mL per mix batch. X-30 exotherm above 60 mL can soften and warp 1.2 mm PETG walls. Mix, pour, wait 10 min before next batch."/>

    {/* ── Void Former Table ── */}
    <SH t="Void Former Table" c={C.purple}/>
    <div style={{overflowX:"auto",marginBottom:4}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["PANEL","STATION (mm from nose)","INTERIOR DIMS","FORMER","FASTENER / SEAL"]}/>
        <tbody>{voids.map((v,i)=>(
          <tr key={i} style={{background:v.id==="F"?"rgba(255,230,0,0.05)":i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
            <td style={{padding:"5px 9px",color:v.id==="F"?C.yellow:C.accent,fontWeight:"bold"}}>{v.id}</td>
            <td style={{padding:"5px 9px",color:C.yellow}}>{v.sta}</td>
            <td style={{padding:"5px 9px",color:C.text}}>{v.dim}</td>
            <td style={{padding:"5px 9px",color:v.id==="F"?C.dim:C.teal}}>{v.former}</td>
            <td style={{padding:"5px 9px",color:C.dimmer,fontSize:9}}>{v.seal}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
    <Note c={C.purple} ch="Void formers are cut from 25 mm EPS blue foam board (Owens Corning Foamular 150 or equiv). Apply 2 coats of Johnson's Paste Wax to all EPS surfaces before placing. Waxed EPS releases cleanly after foam cure — pull out through access panel."/>

    {/* ── Conduit Routing Table ── */}
    <SH t="Conduit Routing — 5 mm OD PTFE Tube" c={C.orange}/>
    <div style={{overflowX:"auto",marginBottom:4}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["BUS / SIGNAL","ROUTE","CHAIN"]}/>
        <tbody>{conduits.map((c,i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
            <td style={{padding:"5px 9px",color:C.orange,fontWeight:"bold",whiteSpace:"nowrap"}}>{c.id}</td>
            <td style={{padding:"5px 9px",color:C.yellow,whiteSpace:"nowrap"}}>{c.route}</td>
            <td style={{padding:"5px 9px",color:C.dim,fontSize:9}}>{c.chain}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
    <Note c={C.orange} ch="All 6 conduits are 5 mm OD × 3 mm ID PTFE tube, installed before foam pour. Tie a pull-wire through each before pouring so cables can be threaded after cure. Total tube weight 12 g stays in airframe."/>

    {/* ── Access Panel Maintenance Map ── */}
    <SH t="Access Panel Maintenance Map" c={C.pink}/>
    {panels.map((p,i)=>(
      <div key={i} style={{display:"flex",gap:12,padding:"7px 10px",marginBottom:4,
        border:`1px solid ${C.border}`,borderRadius:4,
        background:i%2===0?"rgba(244,114,182,0.04)":"rgba(0,229,255,0.015)"}}>
        <div style={{minWidth:130}}>
          <span style={{color:C.pink,fontFamily:M,fontSize:11,fontWeight:"bold"}}>Panel {p.id}</span>
          <div style={{color:C.dimmer,fontFamily:M,fontSize:9,marginTop:2}}>{p.label}</div>
        </div>
        <div style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.7}}>{p.contents}</div>
      </div>
    ))}

    {/* ── 6S Power Notes ── */}
    <SH t="6S Power System Notes" c={C.gold}/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:20,marginBottom:8}}>
      <div>
        <KV k="Nominal voltage (6S)"   v="22.2 V" vc={C.gold}/>
        <KV k="Fully charged (6S)"     v="25.2 V" vc={C.gold}/>
        <KV k="Nacelle ESCs"           v="2× 50 A BLHeli32, 6S rated"/>
        <KV k="Fuselage ESC"           v="1× 25 A BLHeli32, 6S rated"/>
        <KV k="BEC output (avionics)"  v="5 V @ 5 A"/>
        <KV k="3.3 V rail"             v="CM4 carrier on-board regulators"/>
      </div>
      <div>
        <div style={{color:C.gold,fontFamily:M,fontSize:10,marginBottom:6,letterSpacing:"0.05em"}}>BATTERY OPTIONS — T/W ≥ 2.0</div>
        {batOptions.map((b,i)=>(
          <div key={i} style={{padding:"7px 10px",marginBottom:5,border:`1px solid ${C.gold}33`,
            borderRadius:4,background:"rgba(251,191,36,0.04)"}}>
            <div style={{display:"flex",justifyContent:"space-between",alignItems:"baseline",marginBottom:3}}>
              <span style={{color:C.gold,fontFamily:M,fontSize:10,fontWeight:"bold"}}>{b.spec}</span>
              <span style={{color:C.green,fontFamily:M,fontSize:10}}>T/W {b.tw}</span>
            </div>
            <div style={{display:"flex",justifyContent:"space-between"}}>
              <span style={{color:C.dim,fontFamily:M,fontSize:9}}>{b.mass} g · AUW {b.auw} g</span>
              <span style={{color:C.teal,fontFamily:M,fontSize:9}}>{b.hover}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
    <Good ch="All three 6S battery options maintain T/W ≥ 2.0. The 2800 mAh pack offers best T/W ratio (2.67) for cargo missions. 5000 mAh endurance pack restricted to empty payload only."/>
    <Note c={C.gold} ch="This is the first Rev G tab to cover 6S power explicitly. Verify all ESC firmware supports 6S cell count detection. Set low-voltage cutoff to 3.5 V/cell (21.0 V total) in ESC configurator."/>

  </div>);
}

// ── APP ───────────────────────────────────────────────────────
const TABS = [
  {label:"Overview",      value:"overview"},
  {label:"Dimensions",    value:"dimensions"},
  {label:"Weight & Thrust",value:"weight"},
  {label:"Balance & CG", value:"balance"},
  {label:"BOM Delta",    value:"bom"},
  {label:"Hull & Foam",  value:"foam"},
];
_ODFontLoader();

export default function App(){
  const [tab,setTab]=useState("overview");
  return(<div style={{minHeight:"100vh",background:C.bg,color:C.text,fontFamily:M}}>
    <Grid/>
    <div style={{background:"rgba(163,230,53,0.06)",borderBottom:"1px solid rgba(163,230,53,0.2)",
      padding:"6px 24px",fontFamily:M,fontSize:8,color:"rgba(163,230,53,0.75)",lineHeight:1.7}}>
      © 2026 Steve Griffing, PE(CSE) [Control Systems Engineering], CISSP-ISSEP, CPP · CC BY 4.0
      · Hull: Peter Farell CC BY 4.0 · Nozzle: BamJr CC BY 4.0
      · Visual inspiration: Firefly/Serenity © Joss Whedon/Mutant Enemy/Universal — Fan engineering work
    </div>
    <div style={{position:"relative",zIndex:1,borderBottom:`1px solid ${C.border}`,padding:"14px 24px 12px"}}>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",flexWrap:"wrap",gap:12}}>
        <div>
          <div style={{color:C.lime,fontSize:9,letterSpacing:"0.2em",marginBottom:4}}>
            SERENITY TILTROTOR · CANONICAL PROPORTIONS · REV G</div>
          <h1 style={{margin:0,fontSize:18,fontWeight:"normal",color:C.text,letterSpacing:"0.07em",fontFamily:MB_FONT}}>
            RESCALE TO 20" × 15" CANONICAL</h1>
          <div style={{color:"rgba(0,229,255,0.6)",fontSize:10,marginTop:3,fontFamily:M}}>
            508mm (20.0") hull · 381mm (15.0") nacelle C-to-C · 100mm EDFs · span/length = 0.75
          </div>
        </div>
        <div style={{textAlign:"right",fontFamily:M}}>
          <div style={{color:C.yellow,fontSize:13,fontWeight:"bold"}}>AUW empty: {AUW_EMPTY}g ({gToLb(AUW_EMPTY)} lb)</div>
          <div style={{color:C.green,fontSize:11,marginTop:2}}>T/W {TW_EMPTY}:1 empty · T/W {TW_CARGO}:1 cargo</div>
          <div style={{color:C.lime,fontSize:10,marginTop:2}}>Max payload: {MAX_PAY}g ({gToLb(MAX_PAY)} lb)</div>
        </div>
      </div>
      <div style={{display:"flex",gap:2,marginTop:12,flexWrap:"wrap"}}>
        {TABS.map(t=>(<button key={t.value} onClick={()=>setTab(t.value)} style={{
          background:tab===t.value?"rgba(0,229,255,0.09)":"transparent",
          border:`1px solid ${tab===t.value?C.accent:"rgba(0,229,255,0.12)"}`,
          color:tab===t.value?C.accent:C.dimmer,padding:"4px 11px",fontFamily:M,fontSize:9,
          cursor:"pointer",letterSpacing:"0.06em",transition:"all 0.12s"}}>{t.label}</button>))}
      </div>
    </div>
    <div style={{position:"relative",zIndex:1,padding:"20px 24px",maxWidth:1060,margin:"0 auto"}}>
      {tab==="overview"    && <OverviewTab/>}
      {tab==="dimensions"  && <DimensionsTab/>}
      {tab==="weight"      && <WeightTab/>}
      {tab==="balance"     && <BalanceTab/>}
      {tab==="bom"         && <BomTab/>}
      {tab==="foam"        && <HullFoamTab/>}
    </div>
  </div>);
}
