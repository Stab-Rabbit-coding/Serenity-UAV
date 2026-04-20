import { useState } from "react";

const C = {
  bg:"#06080c", border:"rgba(0,229,255,0.11)", accent:"#00e5ff",
  orange:"#ff6b35", yellow:"#ffe600", purple:"#c084fc", green:"#4ade80",
  pink:"#f472b6", teal:"#2dd4bf", red:"#f87171", hull:"rgba(0,229,255,0.07)",
  dim:"rgba(255,255,255,0.40)", dimmer:"rgba(255,255,255,0.22)", text:"rgba(255,255,255,0.82)",
};
const M = "'Courier New','Lucida Console',monospace";

// ── KEY PERFORMANCE NUMBERS ────────────────────────────────────
// 65mm EDF @ 5S: 800g thrust, 28A max, ~52g each
// 35mm EDF @ 5S: 140g thrust, 12A max, ~24g
// Nacelle ESC: 35A each (upgraded from 30A)
// Fwd ESC: 25A (upgraded from 20A)
const EDF_65_THRUST = 800;   // g each
const EDF_35_THRUST = 140;   // g
const EDF_65_IMAX   = 28;    // A each at WOT
const EDF_35_IMAX   = 12;    // A at WOT
const BAT_V = 18.5, BAT_CAP = 2.2; // 5S 2200mAh Ah

const WT_GROUPS = [
  {label:"Propulsion",c:C.orange, items:[
    {n:"2× 65mm EDF + BLDC 2700KV",w:104},
    {n:"2× ESC 35A BLHeli32",w:32},
    {n:"2× nacelle tilt servos MG90S",w:18},
    {n:"35mm fwd fan + 4500KV motor",w:24},
    {n:"Fwd ESC 25A",w:10},
  ]},
  {label:"Airframe — Serenity hull",c:C.teal, items:[
    {n:"Printed hull shell (11 sections PETG/CF-PETG)",w:144},
    {n:"CF 6×3mm keel spine 380mm",w:12},
    {n:"2× 12mm CF spar tubes 300mm",w:22},
    {n:"CF nacelle pivot brackets + hardware",w:16},
    {n:"TPU 95A skid feet ×4",w:8},
  ]},
  {label:"Flight control — Pico 2",c:C.accent, items:[
    {n:"Raspberry Pi Pico 2",w:3},
    {n:"TRIHAT-1 sensor hat",w:15},
    {n:"MS4525DO airspeed + pitot",w:10},
  ]},
  {label:"Companion — CM4 stack",c:C.green, items:[
    {n:"CM4 Lite 4GB WiFi",w:8},
    {n:"CM4-CARRIER-1 PCB",w:14},
    {n:"COMPHAT-1 + ICs",w:20},
    {n:"SiK 915MHz air module",w:14},
    {n:"49MHz RCRS module",w:16},
  ]},
  {label:"Payload system",c:C.pink, items:[
    {n:"SG90 release servo",w:9},
    {n:"N20 winch motor + gearbox",w:14},
    {n:"Winch spool + 5m Dyneema",w:7},
    {n:"DRV8833 H-bridge PCB",w:4},
  ]},
  {label:"Power & wiring",c:C.yellow, items:[
    {n:"5S 2200mAh 75C LiPo",w:220},
    {n:"JST-GH harness + wiring",w:30},
    {n:"5V 3A switching BEC",w:8},
  ]},
];
const AUW  = WT_GROUPS.reduce((s,g)=>s+g.items.reduce((ss,i)=>ss+i.w,0),0);
const THRUST_TOTAL = EDF_65_THRUST*2 + EDF_35_THRUST;
const THRUST_NAC   = EDF_65_THRUST*2;
const TW   = (THRUST_NAC/AUW).toFixed(2);
const HVRT = Math.round(AUW/(THRUST_NAC)*100); // hover throttle %

// hover current per 65mm EDF (T∝I^(2/3) inversion → I∝T^1.5)
const hoverThrust65 = AUW/2;                     // g per nacelle
const hoverFrac65   = hoverThrust65/EDF_65_THRUST;
const I_65_HOV      = EDF_65_IMAX * Math.pow(hoverFrac65,1.5);
const I_35_CRUISE   = EDF_35_IMAX * 0.88;         // ~88% at cruise full
const I_65_TRIM     = EDF_65_IMAX * Math.pow(0.14,1.5); // 14% trim thrust in cruise

const HOVER_LOADS = [
  {n:"2× 65mm EDF @ hover ("+HVRT+"%)", a:I_65_HOV*2, v:BAT_V, c:C.orange},
  {n:"35mm fwd fan — hover trim 5%",    a:EDF_35_IMAX*Math.pow(0.05,1.5)*1, v:BAT_V, c:C.orange},
  {n:"CM4 Lite 4GB (active)",            a:0.85, v:5,   c:C.green},
  {n:"GL850G + COMPHAT-1 + sensors",     a:0.32, v:3.3, c:C.purple},
  {n:"Pico 2 + TRIHAT-1",               a:0.14, v:3.3, c:C.teal},
  {n:"SiK 915MHz TX burst avg",          a:0.27, v:5,   c:C.accent},
  {n:"49MHz RCRS (RX)",                  a:0.10, v:5,   c:C.pink},
  {n:"2× nacelle servos",               a:0.16, v:5,   c:C.dim},
];
const CRUISE_LOADS = [
  {n:"35mm fwd fan — cruise full",       a:I_35_CRUISE,  v:BAT_V, c:C.yellow},
  {n:"2× 65mm EDF @ 14% trim",          a:I_65_TRIM*2,  v:BAT_V, c:C.orange},
  {n:"CM4 Lite 4GB (active)",            a:0.85, v:5,   c:C.green},
  {n:"GL850G + COMPHAT-1 + sensors",     a:0.32, v:3.3, c:C.purple},
  {n:"Pico 2 + TRIHAT-1",               a:0.14, v:3.3, c:C.teal},
  {n:"SiK 915MHz TX avg",               a:0.27, v:5,   c:C.accent},
  {n:"49MHz RCRS (RX)",                  a:0.10, v:5,   c:C.pink},
  {n:"Nacelle servos (cruise, idle)",    a:0.06, v:5,   c:C.dim},
];
const toPbat = (a,v) => a*v/BAT_V;
const sumBat = (loads) => loads.reduce((s,r)=>s+toPbat(r.a,r.v),0);
const hTot = sumBat(HOVER_LOADS), cTot = sumBat(CRUISE_LOADS);
const hMin = (BAT_CAP*0.8/hTot*60).toFixed(1);
const cMin = (BAT_CAP*0.8/cTot*60).toFixed(1);
const h3Min= (3.0*0.8/hTot*60).toFixed(1);
const c3Min= (3.0*0.8/cTot*60).toFixed(1);

// ── primitives ─────────────────────────────────────────────────
const SH=({t,c=C.accent,mt=22})=>(
  <div style={{display:"flex",alignItems:"center",gap:10,marginBottom:14,marginTop:mt}}>
    <div style={{width:3,height:17,background:c}}/>
    <span style={{color:c,fontFamily:M,fontSize:13,letterSpacing:"0.13em",textTransform:"uppercase",fontWeight:"normal"}}>{t}</span>
  </div>
);
const KV=({k,v,c=C.text,u="",vc})=>(
  <div style={{display:"flex",justifyContent:"space-between",padding:"5px 0",
    borderBottom:"1px solid rgba(0,229,255,0.07)",alignItems:"baseline"}}>
    <span style={{color:C.dim,fontFamily:M,fontSize:11}}>{k}</span>
    <span style={{color:vc||c,fontFamily:M,fontSize:11}}>{v}{u&&<span style={{color:C.accent,marginLeft:4,fontSize:10}}>{u}</span>}</span>
  </div>
);
const Note=({c=C.dim,ch})=>(
  <div style={{marginTop:8,marginBottom:6,color:c,fontFamily:M,fontSize:10,lineHeight:1.85,
    padding:"8px 12px",borderLeft:`2px solid ${c}55`,background:`${c}07`,borderRadius:3}}>{ch}</div>
);
const Warn=({ch})=>(
  <div style={{marginTop:8,marginBottom:6,color:C.yellow,fontFamily:M,fontSize:10,lineHeight:1.8,
    padding:"7px 12px",borderLeft:`2px solid ${C.yellow}`,background:"rgba(255,230,0,0.05)",borderRadius:3}}>⚠ {ch}</div>
);
const Good=({ch})=>(
  <div style={{marginTop:8,marginBottom:6,color:C.green,fontFamily:M,fontSize:10,lineHeight:1.8,
    padding:"7px 12px",borderLeft:`2px solid ${C.green}`,background:"rgba(74,222,128,0.05)",borderRadius:3}}>✓ {ch}</div>
);

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

// ══════════════════════════════════════════════════════════════
//  GEOMETRY CONSTANTS — shared across all views
// ══════════════════════════════════════════════════════════════
const SC = (mm) => mm * 1.30;
const NX = 55;
const xp = (mm) => NX + SC(mm);

// nacelle geometry (updated for 65mm EDF)
const NAC_RX = SC(36);   // top-view oval half-length  (was 32 for 60mm)
const NAC_RY = SC(16);   // top-view oval half-width   (was 14 for 60mm)
const NAC_ARM_Y = SC(340); // tip-to-tip half

// engine bell geometry (updated for 35mm EDF)
const BELL_R_OUTER = SC(21); // outer ring radius  (was 18)
const BELL_R_DUCT  = SC(15); // duct exit radius   (was 13)
const BELL_X = xp(300);

// CG
const X_CG    = xp(152);
const X_PIVOT = xp(160);
const X_TAIL  = xp(360);

// Hull profile (same as before)
const HULL_PROFILE=[
  [0,0],[8,10],[22,18],[40,30],[58,36],[88,37],
  [120,42],[140,42],[165,40],[190,36],[220,29],
  [252,18],[260,16],[278,24],[305,29],[330,28],[360,22],
];

// ── TOP VIEW ──────────────────────────────────────────────────
function TopView({sel,onSel}){
  const VW=740, VH=360, CY=180;
  const upper=HULL_PROFILE.map(([x,y])=>[xp(x),CY-SC(y)]);
  const lower=[...HULL_PROFILE].reverse().map(([x,y])=>[xp(x),CY+SC(y)]);
  const outline=[...upper,...lower].map((p,i)=>i===0?`M${p[0]},${p[1]}`:`L${p[0]},${p[1]}`).join(" ")+"Z";

  const zones=[
    {id:"cockpit", lbl:"COCKPIT / SENSOR BAY",  x1:xp(0),  x2:xp(88),  c:C.teal},
    {id:"avionics",lbl:"AVIONICS BAY",           x1:xp(60), x2:xp(160), c:C.accent},
    {id:"battery", lbl:"BATTERY RAIL",           x1:xp(140),x2:xp(230), c:C.yellow},
    {id:"payload", lbl:"PAYLOAD BAY (BELLY)",    x1:xp(130),x2:xp(200), c:C.pink},
    {id:"engine",  lbl:"35mm FWD EDF",           x1:xp(270),x2:xp(335), c:C.orange},
  ];

  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* Zone overlays */}
      {zones.map(z=>(
        <rect key={z.id} x={z.x1} y={CY-SC(46)} width={z.x2-z.x1} height={SC(92)}
          fill={`${z.c}10`} stroke={z.c} strokeWidth={0.7} strokeDasharray="5 3"
          rx={3} style={{cursor:"pointer"}} onClick={()=>onSel(sel===z.id?null:z.id)}/>
      ))}
      {/* Hull */}
      <path d={outline} fill={C.hull} stroke={C.accent} strokeWidth={1.8}/>
      {/* Cockpit dome */}
      <ellipse cx={xp(44)} cy={CY} rx={SC(44)} ry={SC(26)}
        fill="rgba(0,229,255,0.08)" stroke={C.accent} strokeWidth={1}/>
      {/* Dorsal ridge */}
      <line x1={xp(30)} y1={CY} x2={xp(280)} y2={CY}
        stroke="rgba(0,229,255,0.22)" strokeWidth={0.8} strokeDasharray="8 4"/>

      {/* Outrigger arms + nacelles — 65mm EDF oval wider */}
      {[-1,1].map(side=>{
        const sy=CY+side*NAC_ARM_Y;
        const aPts=[
          [xp(115), CY+side*SC(42)],
          [xp(128), CY+side*SC(50)],
          [xp(152), CY+side*SC(182)],
          [xp(160), sy],
          [xp(175), sy],
          [xp(186), CY+side*SC(178)],
          [xp(197), CY+side*SC(50)],
        ];
        const armPath=`M${aPts[0][0]},${aPts[0][1]} `
          +aPts.slice(1,4).map(p=>`L${p[0]},${p[1]}`).join(" ")+" "
          +aPts.slice(4).reverse().map(p=>`L${p[0]},${p[1]}`).join(" ")+"Z";
        const nCY=sy;
        return(
          <g key={side}>
            <path d={armPath} fill="rgba(0,229,255,0.05)" stroke={C.accent} strokeWidth={1.3}/>
            {/* CF spar line */}
            <line x1={xp(130)} y1={CY+side*SC(52)} x2={xp(170)} y2={sy}
              stroke="rgba(0,229,255,0.35)" strokeWidth={2} strokeDasharray="6 3"/>
            {/* 65mm nacelle oval (wider than before) */}
            <ellipse cx={xp(155)} cy={nCY} rx={NAC_RX} ry={NAC_RY}
              fill="rgba(255,107,53,0.12)" stroke={C.orange} strokeWidth={1.8}/>
            {/* EDF duct inner circle */}
            <ellipse cx={xp(155)} cy={nCY} rx={SC(22)} ry={SC(10)}
              fill="rgba(255,107,53,0.08)" stroke={C.orange}
              strokeWidth={0.9} strokeDasharray="3 2"/>
            {/* 65mm label */}
            <text x={xp(155)} y={nCY+(side>0?17:-21)} textAnchor="middle"
              fill={C.orange} fontSize={7} fontFamily={M}>65mm EDF{side<0?" L":" R"}</text>
            {/* Tilt axis */}
            <line x1={xp(128)} y1={nCY} x2={xp(182)} y2={nCY}
              stroke={C.orange} strokeWidth={0.8} strokeDasharray="3 2" opacity={0.5}/>
          </g>
        );
      })}

      {/* Engine bell — 35mm EDF (wider) */}
      <circle cx={BELL_X} cy={CY} r={BELL_R_OUTER}
        fill="rgba(255,230,0,0.1)" stroke={C.yellow} strokeWidth={1.8}/>
      <circle cx={BELL_X} cy={CY} r={BELL_R_DUCT}
        fill="rgba(255,230,0,0.15)" stroke={C.yellow} strokeWidth={1.2}/>
      {[0,51,102,153,204,255,306].map(a=>(
        <line key={a} x1={BELL_X} y1={CY}
          x2={BELL_X+BELL_R_DUCT*0.9*Math.cos(a*Math.PI/180)}
          y2={CY+BELL_R_DUCT*0.9*Math.sin(a*Math.PI/180)}
          stroke={C.yellow} strokeWidth={0.8} opacity={0.5}/>
      ))}
      <text x={BELL_X} y={CY-BELL_R_OUTER-6} textAnchor="middle"
        fill={C.yellow} fontSize={7} fontFamily={M}>35mm EDF</text>
      <text x={BELL_X} y={CY+BELL_R_OUTER+12} textAnchor="middle"
        fill={`${C.yellow}70`} fontSize={6} fontFamily={M}>140g thrust</text>

      {/* Pitot */}
      <line x1={NX} y1={CY} x2={NX-22} y2={CY}
        stroke={C.teal} strokeWidth={2.5} strokeLinecap="round"/>
      <circle cx={NX-22} cy={CY} r={2.5} fill={C.teal}/>

      {/* Antenna marks */}
      <rect x={xp(46)} y={CY-SC(14)} width={SC(24)} height={SC(10)}
        fill="rgba(74,222,128,0.2)" stroke="#4ade80" strokeWidth={1}/>
      <text x={xp(58)} y={CY-SC(19)} textAnchor="middle" fill="#4ade80" fontSize={6} fontFamily={M}>GPS</text>
      <circle cx={xp(290)} cy={CY-SC(16)} r={4}
        fill="rgba(244,114,182,0.2)" stroke={C.pink} strokeWidth={1}/>
      <text x={xp(290)} y={CY-SC(23)} textAnchor="middle" fill={C.pink} fontSize={6} fontFamily={M}>49M↑</text>
      <circle cx={xp(238)} cy={CY} r={4}
        fill="rgba(255,107,53,0.15)" stroke={C.orange} strokeWidth={0.8} strokeDasharray="2 2"/>
      <text x={xp(238)} y={CY+14} textAnchor="middle" fill={C.orange} fontSize={6} fontFamily={M}>SiK↓</text>

      {/* CG marker */}
      <line x1={X_CG} y1={CY-SC(58)} x2={X_CG} y2={CY+SC(58)}
        stroke={C.green} strokeWidth={1} strokeDasharray="5 3"/>
      <polygon points={`${X_CG},${CY-SC(58)} ${X_CG-7},${CY-SC(40)} ${X_CG+7},${CY-SC(40)}`}
        fill={C.green} opacity={0.9}/>
      <text x={X_CG} y={CY-SC(65)} textAnchor="middle" fill={C.green} fontSize={7} fontFamily={M}>CG·152mm</text>

      {/* Active zone label */}
      {sel && zones.filter(z=>z.id===sel).map(z=>(
        <text key={z.id} x={(z.x1+z.x2)/2} y={CY-SC(55)} textAnchor="middle"
          fill={z.c} fontSize={9} fontFamily={M} fontWeight="bold">{z.lbl}</text>
      ))}

      {/* Dim */}
      <line x1={NX} y1={VH-16} x2={X_TAIL} y2={VH-16} stroke={C.accent} strokeWidth={0.4} opacity={0.2}/>
      <line x1={NX} y1={VH-20} x2={NX} y2={VH-12} stroke={C.accent} strokeWidth={0.4} opacity={0.2}/>
      <line x1={X_TAIL} y1={VH-20} x2={X_TAIL} y2={VH-12} stroke={C.accent} strokeWidth={0.4} opacity={0.2}/>
      <text x={(NX+X_TAIL)/2} y={VH-5} textAnchor="middle" fill={C.dimmer} fontSize={7} fontFamily={M}>360 mm</text>

      {/* Wingspan */}
      <line x1={NX+SC(24)} y1={CY-NAC_ARM_Y-20} x2={NX+SC(24)} y2={CY+NAC_ARM_Y+20}
        stroke={C.accent} strokeWidth={0.4} opacity={0.13}/>
      <text x={NX+SC(24)-10} y={CY} textAnchor="middle" fill={C.dimmer} fontSize={7} fontFamily={M}
        transform={`rotate(-90 ${NX+SC(24)-10} ${CY})`}>680mm</text>

      <text x={VW/2} y={16} textAnchor="middle" fill="rgba(0,229,255,0.25)"
        fontSize={9} fontFamily={M} letterSpacing="0.12em">TOP / PLAN VIEW — CLICK ZONE</text>
      <text x={NX-8} y={CY+4} textAnchor="end" fill={C.dimmer} fontSize={7} fontFamily={M}>NOSE</text>
      <text x={X_TAIL+5} y={CY+4} fill={C.dimmer} fontSize={7} fontFamily={M}>TAIL</text>
    </svg>
  );
}

// ── SIDE VIEW ────────────────────────────────────────────────
function SideView(){
  const VW=680, VH=330, BY=185;
  const topE=[[0,0],[5,8],[18,22],[40,32],[58,38],[75,36],[88,30],[110,26],[140,26],[165,25],[195,24],[220,20],[255,12],[270,16],[300,20],[340,18],[360,14]];
  const botE=[[0,0],[10,5],[35,14],[88,20],[140,22],[180,22],[220,20],[255,14],[270,18],[300,22],[340,20],[360,14]];
  const outT=topE.map(([x,y])=>[xp(x),BY-SC(y)]);
  const outB=[...botE].reverse().map(([x,y])=>[xp(x),BY+SC(y)]);
  const sidePath=[...outT,...outB].map((p,i)=>i===0?`M${p[0]},${p[1]}`:`L${p[0]},${p[1]}`).join(" ")+"Z";

  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      <path d={sidePath} fill={C.hull} stroke={C.accent} strokeWidth={1.8}/>
      {/* Cockpit bubble */}
      <path d={`M${xp(8)},${BY-SC(22)} Q${xp(45)},${BY-SC(65)} ${xp(85)},${BY-SC(30)}`}
        fill="rgba(0,229,255,0.1)" stroke={C.accent} strokeWidth={1.2}/>
      <text x={xp(44)} y={BY-SC(48)} textAnchor="middle"
        fill="rgba(0,229,255,0.45)" fontSize={7} fontFamily={M}>COCKPIT</text>

      {/* Nacelle side — 65mm, slightly taller */}
      <line x1={xp(130)} y1={BY-SC(26)} x2={xp(130)} y2={BY-SC(64)}
        stroke={C.orange} strokeWidth={2} strokeLinecap="round"/>
      <line x1={xp(170)} y1={BY-SC(26)} x2={xp(170)} y2={BY-SC(64)}
        stroke={C.orange} strokeWidth={2} strokeLinecap="round"/>
      {/* 65mm EDF nacelle hover position */}
      <rect x={xp(138)} y={BY-SC(100)} width={SC(26)} height={SC(52)} rx={5}
        fill="rgba(255,107,53,0.10)" stroke={C.orange} strokeWidth={1.5}/>
      {/* Duct ring */}
      <ellipse cx={xp(151)} cy={BY-SC(54)} rx={SC(11)} ry={SC(4.5)}
        fill="rgba(255,107,53,0.15)" stroke={C.orange} strokeWidth={0.9}/>
      <text x={xp(151)} y={BY-SC(107)} textAnchor="middle"
        fill={C.orange} fontSize={7} fontFamily={M} fontWeight="bold">65mm</text>
      <text x={xp(151)} y={BY-SC(115)} textAnchor="middle"
        fill={`${C.orange}80`} fontSize={6} fontFamily={M}>800g thrust</text>
      {/* Tilt arc */}
      <path d={`M${xp(130)},${BY-SC(66)} A${SC(26)},${SC(26)} 0 0,1 ${xp(156)},${BY-SC(40)}`}
        fill="none" stroke={C.orange} strokeWidth={0.8} strokeDasharray="3 2" opacity={0.6}/>
      <text x={xp(170)} y={BY-SC(66)} fill={C.orange} fontSize={6} fontFamily={M}>±90°</text>

      {/* Engine bell — 35mm EDF (larger) */}
      <path d={`M${xp(265)},${BY-SC(15)} Q${xp(275)},${BY-SC(26)} ${xp(285)},${BY-SC(24)}
        L${xp(330)},${BY-SC(24)} Q${xp(346)},${BY-SC(22)} ${xp(357)},${BY-SC(16)}
        L${xp(362)},${BY-SC(14)} L${xp(362)},${BY+SC(14)}
        L${xp(357)},${BY+SC(16)} Q${xp(346)},${BY+SC(22)} ${xp(330)},${BY+SC(24)}
        L${xp(285)},${BY+SC(24)} Q${xp(275)},${BY+SC(26)} ${xp(265)},${BY+SC(15)}`}
        fill="rgba(255,230,0,0.07)" stroke={C.yellow} strokeWidth={1.5}/>
      <circle cx={xp(300)} cy={BY} r={SC(15)}
        fill="rgba(255,230,0,0.12)" stroke={C.yellow} strokeWidth={1.2}/>
      <text x={xp(300)} y={BY+4} textAnchor="middle" fill={C.yellow} fontSize={7} fontFamily={M} fontWeight="bold">35mm EDF</text>
      <text x={xp(300)} y={BY+14} textAnchor="middle" fill={`${C.yellow}70`} fontSize={6} fontFamily={M}>140g thrust</text>

      {/* Payload bay */}
      <rect x={xp(130)} y={BY+SC(20)} width={SC(70)} height={SC(22)} rx={3}
        fill="rgba(244,114,182,0.1)" stroke={C.pink} strokeWidth={1} strokeDasharray="3 2"/>
      <text x={xp(165)} y={BY+SC(34)} textAnchor="middle"
        fill={C.pink} fontSize={7} fontFamily={M}>PAYLOAD BAY</text>

      {/* Skids */}
      {[xp(95),xp(230)].map((sx,i)=>(
        <g key={i}>
          <line x1={sx} y1={BY+SC(20)} x2={sx-SC(8)} y2={BY+SC(42)}
            stroke={C.accent} strokeWidth={1.5} opacity={0.5}/>
          <line x1={sx-SC(22)} y1={BY+SC(42)} x2={sx+SC(22)} y2={BY+SC(42)}
            stroke={C.accent} strokeWidth={2} opacity={0.5}/>
        </g>
      ))}

      {/* GPS patch */}
      <rect x={xp(38)} y={BY-SC(64)} width={SC(22)} height={SC(8)} rx={2}
        fill="rgba(74,222,128,0.2)" stroke="#4ade80" strokeWidth={1}/>
      <text x={xp(49)} y={BY-SC(68)} textAnchor="middle" fill="#4ade80" fontSize={6} fontFamily={M}>GPS</text>

      {/* 49MHz */}
      <circle cx={xp(290)} cy={BY-SC(24)} r={3}
        fill="rgba(244,114,182,0.2)" stroke={C.pink} strokeWidth={1}/>
      <line x1={xp(290)} y1={BY-SC(27)} x2={xp(290)} y2={BY-SC(67)}
        stroke={C.pink} strokeWidth={1.5} strokeLinecap="round"/>
      {[0,1,2].map(i=>(
        <ellipse key={i} cx={xp(290)} cy={BY-SC(37+i*7)} rx={3} ry={2}
          fill="none" stroke={C.pink} strokeWidth={0.7} opacity={0.75}/>
      ))}
      <text x={xp(290)} y={BY-SC(74)} textAnchor="middle"
        fill={C.pink} fontSize={6} fontFamily={M}>49MHz</text>

      {/* SiK */}
      <rect x={xp(234)} y={BY+SC(20)} width={SC(8)} height={3} rx={1}
        fill={C.orange} stroke={C.orange} strokeWidth={0.5}/>
      <line x1={xp(238)} y1={BY+SC(23)} x2={xp(238)} y2={BY+SC(48)}
        stroke={C.orange} strokeWidth={1.8} strokeLinecap="round"/>
      <text x={xp(238)} y={BY+SC(56)} textAnchor="middle"
        fill={C.orange} fontSize={6} fontFamily={M}>SiK↓</text>

      {/* CG line */}
      <line x1={X_CG} y1={BY-SC(70)} x2={X_CG} y2={BY+SC(50)}
        stroke={C.green} strokeWidth={1} strokeDasharray="5 3"/>
      <text x={X_CG} y={BY-SC(76)} textAnchor="middle" fill={C.green} fontSize={8} fontFamily={M}>CG·152</text>

      {/* Pitot */}
      <line x1={NX} y1={BY} x2={NX-22} y2={BY} stroke={C.teal} strokeWidth={2.5} strokeLinecap="round"/>
      <circle cx={NX-22} cy={BY} r={2.5} fill={C.teal}/>

      <line x1={NX} y1={VH-12} x2={X_TAIL} y2={VH-12} stroke={C.accent} strokeWidth={0.4} opacity={0.2}/>
      <text x={(NX+X_TAIL)/2} y={VH-4} textAnchor="middle" fill={C.dimmer} fontSize={7} fontFamily={M}>360 mm</text>
      <text x={NX-12} y={BY+4} textAnchor="end" fill={C.dimmer} fontSize={7} fontFamily={M}>NOSE</text>
      <text x={X_TAIL+5} y={BY+4} fill={C.dimmer} fontSize={7} fontFamily={M}>TAIL</text>
      <text x={VW/2} y={14} textAnchor="middle" fill="rgba(0,229,255,0.25)"
        fontSize={9} fontFamily={M} letterSpacing="0.12em">RIGHT SIDE VIEW</text>
    </svg>
  );
}

// ── FRONT VIEW ────────────────────────────────────────────────
function FrontView(){
  const VW=560, VH=350, CX=280, BY=225;
  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      <ellipse cx={CX} cy={BY-SC(24)} rx={SC(40)} ry={SC(36)}
        fill={C.hull} stroke={C.accent} strokeWidth={1.8}/>
      <ellipse cx={CX} cy={BY-SC(52)} rx={SC(28)} ry={SC(20)}
        fill="rgba(0,229,255,0.1)" stroke={C.accent} strokeWidth={1.2}/>
      <ellipse cx={CX} cy={BY-SC(52)} rx={SC(18)} ry={SC(12)}
        fill="rgba(0,229,255,0.08)" stroke="rgba(0,229,255,0.4)" strokeWidth={0.8}/>

      {/* Outrigger arms + 65mm nacelles */}
      {[-1,1].map(side=>{
        const TX=CX+side*SC(340), TY=BY-SC(12);
        return(
          <g key={side}>
            <line x1={CX+side*SC(46)} y1={BY-SC(26)} x2={TX} y2={TY}
              stroke={C.accent} strokeWidth={2}/>
            {/* 65mm nacelle — larger oval front-on */}
            <ellipse cx={TX} cy={TY} rx={SC(33)} ry={SC(24)}
              fill="rgba(255,107,53,0.10)" stroke={C.orange} strokeWidth={1.8}/>
            {/* 65mm duct ring */}
            <ellipse cx={TX} cy={TY} rx={SC(24)} ry={SC(17)}
              fill="rgba(255,107,53,0.08)" stroke={C.orange} strokeWidth={1} strokeDasharray="3 2"/>
            {/* Motor hub */}
            <circle cx={TX} cy={TY} r={SC(6)}
              fill="rgba(255,107,53,0.15)" stroke={C.orange} strokeWidth={0.8}/>
            {/* Fan blades */}
            {[0,30,60,90,120,150,180,210,240,270,300,330].map(a=>(
              <line key={a} x1={TX+SC(7)*Math.cos(a*Math.PI/180)} y1={TY+SC(5)*Math.sin(a*Math.PI/180)}
                x2={TX+SC(22)*Math.cos(a*Math.PI/180)} y2={TY+SC(16)*Math.sin(a*Math.PI/180)}
                stroke={C.orange} strokeWidth={0.7} opacity={0.4}/>
            ))}
            <text x={TX} y={TY+SC(30)} textAnchor="middle"
              fill={C.orange} fontSize={8} fontFamily={M} fontWeight="bold">65mm {side<0?"L":"R"}</text>
            <text x={TX} y={TY+SC(40)} textAnchor="middle"
              fill={`${C.orange}70`} fontSize={7} fontFamily={M}>800g</text>
            {/* Tilt axis line */}
            <line x1={TX-SC(35)} y1={TY} x2={TX+SC(35)} y2={TY}
              stroke={C.orange} strokeWidth={0.7} strokeDasharray="3 2" opacity={0.5}/>
          </g>
        );
      })}

      {/* Belly payload door */}
      <rect x={CX-SC(30)} y={BY+SC(8)} width={SC(60)} height={SC(10)} rx={2}
        fill="rgba(244,114,182,0.1)" stroke={C.pink} strokeWidth={1} strokeDasharray="3 2"/>

      {/* Skids */}
      {[-1,1].map(side=>(
        <g key={side}>
          <line x1={CX+side*SC(18)} y1={BY+SC(22)} x2={CX+side*SC(24)} y2={BY+SC(40)}
            stroke={C.accent} strokeWidth={1.5} opacity={0.5}/>
          <line x1={CX+side*SC(24)} y1={BY+SC(40)} x2={CX+side*SC(40)} y2={BY+SC(40)}
            stroke={C.accent} strokeWidth={2} opacity={0.5}/>
        </g>
      ))}

      {/* GPS */}
      <rect x={CX-SC(12)} y={BY-SC(76)} width={SC(24)} height={SC(8)} rx={2}
        fill="rgba(74,222,128,0.2)" stroke="#4ade80" strokeWidth={1}/>
      <text x={CX} y={BY-SC(80)} textAnchor="middle" fill="#4ade80" fontSize={7} fontFamily={M}>GPS</text>

      <circle cx={CX} cy={BY-SC(24)} r={3} fill={C.teal} opacity={0.8}/>
      <text x={CX} y={BY-SC(6)} textAnchor="middle" fill={C.teal} fontSize={7} fontFamily={M}>PITOT</text>

      {/* Span dim */}
      <line x1={CX-SC(340)} y1={BY+SC(62)} x2={CX+SC(340)} y2={BY+SC(62)}
        stroke={C.accent} strokeWidth={0.4} opacity={0.2}/>
      <text x={CX} y={BY+SC(74)} textAnchor="middle" fill={C.dimmer} fontSize={7} fontFamily={M}>680 mm tip-to-tip</text>

      <text x={VW/2} y={16} textAnchor="middle" fill="rgba(0,229,255,0.25)"
        fontSize={9} fontFamily={M} letterSpacing="0.12em">FRONT VIEW</text>
    </svg>
  );
}

// ── REAR VIEW ─────────────────────────────────────────────────
function RearView(){
  const VW=560, VH=310, CX=280, BY=200;
  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* 35mm engine bell */}
      <circle cx={CX} cy={BY-SC(18)} r={BELL_R_OUTER+SC(4)}
        fill="rgba(255,230,0,0.05)" stroke={`${C.yellow}55`} strokeWidth={1.5} strokeDasharray="4 2"/>
      <circle cx={CX} cy={BY-SC(18)} r={BELL_R_OUTER}
        fill="rgba(255,230,0,0.08)" stroke={C.yellow} strokeWidth={2}/>
      <circle cx={CX} cy={BY-SC(18)} r={BELL_R_DUCT}
        fill="rgba(255,230,0,0.12)" stroke={C.yellow} strokeWidth={1.3}/>
      {[0,51,102,153,204,255,306].map(a=>(
        <line key={a} x1={CX} y1={BY-SC(18)}
          x2={CX+BELL_R_DUCT*0.9*Math.cos(a*Math.PI/180)}
          y2={BY-SC(18)+BELL_R_DUCT*0.9*Math.sin(a*Math.PI/180)}
          stroke={C.yellow} strokeWidth={1} opacity={0.55}/>
      ))}
      <text x={CX} y={BY-SC(18)+4} textAnchor="middle" fill={C.yellow} fontSize={7} fontFamily={M} fontWeight="bold">35mm EDF</text>
      {/* Hull silhouette */}
      <ellipse cx={CX} cy={BY-SC(18)} rx={SC(46)} ry={SC(36)}
        fill="none" stroke={C.accent} strokeWidth={1.5}/>

      {/* Outrigger arms + 65mm nacelles */}
      {[-1,1].map(side=>{
        const TX=CX+side*SC(340), TY=BY-SC(12);
        return(
          <g key={side}>
            <line x1={CX+side*SC(46)} y1={BY-SC(22)} x2={TX} y2={TY}
              stroke={C.accent} strokeWidth={1.5}/>
            <ellipse cx={TX} cy={TY} rx={SC(33)} ry={SC(24)}
              fill="rgba(255,107,53,0.08)" stroke={C.orange} strokeWidth={1.5}/>
            <ellipse cx={TX} cy={TY} rx={SC(24)} ry={SC(17)}
              fill="rgba(255,107,53,0.08)" stroke={C.orange}
              strokeWidth={0.8} strokeDasharray="3 2"/>
            <text x={TX} y={TY+SC(34)} textAnchor="middle"
              fill={C.orange} fontSize={7} fontFamily={M}>{side<0?"L":"R"} 65mm</text>
            {/* Hover up arrow */}
            <text x={TX} y={TY-SC(28)} textAnchor="middle"
              fill={C.orange} fontSize={10} fontFamily={M}>↑</text>
          </g>
        );
      })}

      {/* 49MHz dorsal */}
      <circle cx={CX} cy={BY-SC(52)} r={4}
        fill="rgba(244,114,182,0.2)" stroke={C.pink} strokeWidth={1}/>
      <line x1={CX} y1={BY-SC(56)} x2={CX} y2={BY-SC(82)}
        stroke={C.pink} strokeWidth={1.5} strokeLinecap="round"/>
      <text x={CX} y={BY-SC(88)} textAnchor="middle" fill={C.pink} fontSize={6} fontFamily={M}>49MHz↑</text>

      {/* SiK */}
      <line x1={CX} y1={BY+SC(4)} x2={CX} y2={BY+SC(26)}
        stroke={C.orange} strokeWidth={1.5} strokeLinecap="round"/>
      <text x={CX} y={BY+SC(34)} textAnchor="middle" fill={C.orange} fontSize={6} fontFamily={M}>SiK↓</text>

      <line x1={CX-SC(340)} y1={VH-14} x2={CX+SC(340)} y2={VH-14}
        stroke={C.accent} strokeWidth={0.4} opacity={0.2}/>
      <text x={CX} y={VH-5} textAnchor="middle" fill={C.dimmer} fontSize={7} fontFamily={M}>680mm</text>
      <text x={VW/2} y={16} textAnchor="middle" fill="rgba(0,229,255,0.25)"
        fontSize={9} fontFamily={M} letterSpacing="0.12em">REAR VIEW — HOVER</text>
    </svg>
  );
}

// ── ZONE DETAIL ───────────────────────────────────────────────
const ZONE_DETAIL={
  cockpit:{title:"Cockpit / Sensor Bay",c:C.teal,rows:[
    ["Contents","Pico 2 + TRIHAT-1 · MS4525DO airspeed · pitot port at nose tip"],
    ["Access","Hinged clear PETG dome (friction-fit) · lifts off for bench access"],
    ["GPS","25×25mm RHCP patch antenna on cockpit roof · 58mm from nose"],
    ["Structure","2mm CF bulkhead plate at x=88mm carries pitot tube bending loads"],
  ]},
  avionics:{title:"Avionics Bay",c:C.accent,rows:[
    ["Contents","CM4 Lite + CM4-CARRIER-1 + COMPHAT-1 stack"],
    ["Access","Top dorsal panel · snap-fit PETG · 4× M2 screws"],
    ["Cooling","4× Ø6mm NACA flush vents per side · convection"],
    ["WiFi","CM4 trace antenna faces upper-right hull skin (PLA/PETG, RF transparent)"],
  ]},
  battery:{title:"Battery Rail",c:C.yellow,rows:[
    ["Battery","5S 2200mAh 75C · 105×34×22mm"],
    ["Rail","2× M3 aluminium rails · 130–235mm from nose on keel centreline"],
    ["Trim","±22mm slide · M3 thumb screw lock · target 195mm from nose centroid"],
    ["Access","Belly door aft of payload bay · 112×42mm PETG door · 2× magnets"],
  ]},
  payload:{title:"Payload Bay (Belly)",c:C.pink,rows:[
    ["Dimensions","70×50×35mm · 130–200mm from nose"],
    ["Door","Hinged PETG belly door · SG90 latch servo · spring-return closed"],
    ["Winch","N20 gearmotor + 18mm Dyneema spool forward of bay · DRV8833 H-bridge"],
    ["Max payload","200g · 20:1 safety factor on 40kg Dyneema line"],
  ]},
  engine:{title:"35mm Fwd EDF (Fuselage)",c:C.orange,rows:[
    ["Duct ID","35mm · 7-blade BLDC · 4500KV · ~140g thrust @ 5S · 12A max"],
    ["ESC","25A BLHeli32 · DSHOT300 · mounted inside aft hull"],
    ["Bell","PETG annular bell mirrors Serenity engine-bell silhouette at this scale"],
    ["Role hover","Low-power pitch/yaw trim authority (~5% throttle)"],
    ["Role cruise","Primary forward thrust · EDF nacelles tilt to 0° and unload to 14% trim"],
  ]},
};

function ZonePanel({id}){
  if(!id) return(
    <div style={{padding:"16px 14px",color:C.dimmer,fontFamily:M,fontSize:11,
      border:`1px solid ${C.border}`,borderRadius:4,minHeight:100,textAlign:"center",paddingTop:36}}>
      click a zone on the diagram
    </div>
  );
  const d=ZONE_DETAIL[id];
  return(
    <div style={{padding:"14px",border:`1px solid ${d.c}44`,borderRadius:4,background:`${d.c}07`}}>
      <div style={{color:d.c,fontFamily:M,fontSize:12,fontWeight:"bold",letterSpacing:"0.06em",marginBottom:10}}>{d.title}</div>
      {d.rows.map(([k,v],i)=>(
        <div key={i} style={{display:"flex",gap:8,padding:"4px 0",
          borderBottom:"1px solid rgba(255,255,255,0.05)",alignItems:"flex-start"}}>
          <span style={{color:C.dim,fontFamily:M,fontSize:9,minWidth:72,flexShrink:0}}>{k}</span>
          <span style={{color:C.text,fontFamily:M,fontSize:10,lineHeight:1.6}}>{v}</span>
        </div>
      ))}
    </div>
  );
}

function DiagramTab(){
  const [sel,setSel]=useState(null);
  return(
    <div>
      <div style={{background:"rgba(255,107,53,0.05)",border:`1px solid rgba(255,107,53,0.2)`,
        borderRadius:4,padding:"10px 14px",marginBottom:16,fontFamily:M,fontSize:11,color:C.dim,lineHeight:1.8}}>
        <span style={{color:C.orange,fontWeight:"bold"}}>65mm nacelle EDFs</span> · 800g thrust each · 28A max · 72mm OD nacelle pod ·
        &nbsp;&nbsp;<span style={{color:C.yellow,fontWeight:"bold"}}>35mm fuselage EDF</span> · 140g thrust · 12A max · 41mm engine bell ID
      </div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 250px",gap:16,alignItems:"start",marginBottom:20}}>
        <div>
          <div style={{color:C.dimmer,fontFamily:M,fontSize:10,letterSpacing:"0.08em",marginBottom:6}}>TOP / PLAN VIEW · click zones</div>
          <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:8,marginBottom:12}}>
            <TopView sel={sel} onSel={setSel}/>
          </div>
        </div>
        <div style={{position:"sticky",top:20}}>
          <div style={{color:C.dimmer,fontFamily:M,fontSize:10,letterSpacing:"0.08em",marginBottom:8}}>ZONE INSPECTOR</div>
          <ZonePanel id={sel}/>
        </div>
      </div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:16}}>
        <div>
          <div style={{color:C.dimmer,fontFamily:M,fontSize:10,letterSpacing:"0.08em",marginBottom:6}}>RIGHT SIDE VIEW</div>
          <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:8}}>
            <SideView/>
          </div>
        </div>
        <div style={{display:"grid",gridTemplateRows:"1fr 1fr",gap:12}}>
          <div>
            <div style={{color:C.dimmer,fontFamily:M,fontSize:10,letterSpacing:"0.08em",marginBottom:6}}>FRONT VIEW</div>
            <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:8}}>
              <FrontView/>
            </div>
          </div>
          <div>
            <div style={{color:C.dimmer,fontFamily:M,fontSize:10,letterSpacing:"0.08em",marginBottom:6}}>REAR VIEW — HOVER</div>
            <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:8}}>
              <RearView/>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// ── PROPULSION SPEC TAB ───────────────────────────────────────
function PropTab(){
  return(
    <div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
        {/* 65mm nacelle */}
        <div>
          <SH t="65mm Nacelle EDF ×2" mt={0} c={C.orange}/>
          <KV k="Duct inner diameter" v="65mm" c={C.orange}/>
          <KV k="Nacelle OD (with fairing)" v="~72mm" c={C.orange}/>
          <KV k="Blade count" v="12-blade"/>
          <KV k="Motor KV" v="2700KV (5S optimised)"/>
          <KV k="Static thrust @ 5S" v="800g each · 1600g total" vc={C.green}/>
          <KV k="Max current (WOT)" v="28A each · 56A total"/>
          <KV k="ESC rating" v="35A BLHeli32 DSHOT300 (upgraded from 30A)"/>
          <KV k="ESC weight" v="16g each" />
          <KV k="EDF+motor weight" v="52g each · 104g total"/>
          <KV k="Hover thrust per nacelle" v={`${Math.round(AUW/2)}g (${HVRT}% throttle)`} vc={C.green}/>
          <KV k="Hover current per nacelle" v={`${I_65_HOV.toFixed(1)}A`}/>
          <KV k="Tilt range" v="0° (cruise) — 90° (hover) · ±95° mechanical stop"/>
          <KV k="Nacelle fairing" v="CF-PETG · 72mm OD · +3mm radial vs 60mm design"/>
          <Note c={C.orange} ch="65mm fan disc area is 18% larger than 60mm. At the same thrust output, disc loading is lower → higher efficiency. Hover throttle drops from ~55% (60mm) to ~46% (65mm), extending hover endurance and increasing thermal headroom on ESCs."/>
          <Good ch="Nacelle pivot bearing and MG90S servo geometry unchanged. Only the printed fairing outer diameter grows 3mm — no structural redesign required."/>
        </div>
        {/* 35mm fwd */}
        <div>
          <SH t="35mm Fuselage EDF ×1" mt={0} c={C.yellow}/>
          <KV k="Duct inner diameter" v="35mm" c={C.yellow}/>
          <KV k="Engine bell ID" v="~41mm (with duct walls)" c={C.yellow}/>
          <KV k="Blade count" v="7-blade"/>
          <KV k="Motor KV" v="4500KV (5S optimised)"/>
          <KV k="Static thrust @ 5S" v="140g" vc={C.green}/>
          <KV k="Max current (WOT)" v="12A"/>
          <KV k="ESC rating" v="25A BLHeli32 (upgraded from 20A, headroom for 12A)"/>
          <KV k="ESC weight" v="10g"/>
          <KV k="EDF+motor weight" v="24g (upgraded from 30mm 18g)"/>
          <KV k="Hover trim (5%)" v={`${Math.round(EDF_35_THRUST*0.05)}g forward push`}/>
          <KV k="Cruise thrust (88%)" v={`${Math.round(EDF_35_THRUST*0.88)}g forward thrust`} vc={C.green}/>
          <KV k="Cruise current" v={`${I_35_CRUISE.toFixed(1)}A @ 18.5V`}/>
          <KV k="Bell fairing" v="PETG annular · Serenity engine-bell silhouette · 20% infill 3 walls"/>
          <Note c={C.yellow} ch="35mm vs 30mm: +60g thrust (+75%), +5W input power, +6g weight. The larger fan meaningfully improves cruise transition speed and pitch authority in hover. The Serenity engine-bell silhouette at 360mm hull scale accommodates 35mm duct ID with the annular ring still visually accurate."/>
        </div>
      </div>

      <SH t="Total Thrust Summary"/>
      <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:12}}>
        {[
          {l:"Nacelle thrust (WOT)",v:`${THRUST_NAC}g`,c:C.orange,s:"2× 65mm @ 5S full throttle"},
          {l:"Fwd fan thrust (WOT)",v:`${EDF_35_THRUST}g`,c:C.yellow,s:"35mm @ 5S full throttle"},
          {l:"Total max thrust",v:`${THRUST_TOTAL}g`,c:C.green,s:"All three fans combined"},
          {l:"T/W (nacelles only)",v:`${TW}:1`,c:parseFloat(TW)>=1.8?C.green:C.red,s:"Vertical component only"},
        ].map((s,i)=>(
          <div key={i} style={{padding:"10px 12px",border:`1px solid ${s.c}44`,background:`${s.c}07`,borderRadius:4}}>
            <div style={{color:C.dim,fontFamily:M,fontSize:9,letterSpacing:"0.08em",marginBottom:3}}>{s.l}</div>
            <div style={{color:s.c,fontFamily:M,fontSize:18,fontWeight:"bold"}}>{s.v}</div>
            <div style={{color:C.dimmer,fontFamily:M,fontSize:9,marginTop:2}}>{s.s}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── POWER TAB ─────────────────────────────────────────────────
function PowerBars({loads}){
  const total=sumBat(loads);
  const maxA=Math.max(...loads.map(r=>toPbat(r.a,r.v)));
  return(
    <div>
      {loads.map((r,i)=>{
        const bA=toPbat(r.a,r.v);
        return(
          <div key={i} style={{marginBottom:7}}>
            <div style={{display:"flex",justifyContent:"space-between",marginBottom:2}}>
              <span style={{color:r.c,fontFamily:M,fontSize:10}}>{r.n}</span>
              <span style={{color:r.c,fontFamily:M,fontSize:10}}>
                {(r.a*r.v).toFixed(1)}W · {bA.toFixed(2)}A@bat
              </span>
            </div>
            <div style={{background:"rgba(255,255,255,0.05)",borderRadius:2,height:7}}>
              <div style={{width:`${(bA/maxA)*100}%`,height:"100%",background:r.c,opacity:.55}}/>
            </div>
          </div>
        );
      })}
      <div style={{borderTop:`1px solid ${C.border}`,marginTop:10,paddingTop:8,
        display:"flex",justifyContent:"space-between"}}>
        <span style={{color:C.accent,fontFamily:M,fontSize:11}}>TOTAL BATTERY DRAW</span>
        <span style={{color:C.yellow,fontFamily:M,fontSize:14,fontWeight:"bold"}}>
          {total.toFixed(1)}A · {(total*BAT_V).toFixed(0)}W
        </span>
      </div>
    </div>
  );
}

function PowerTab(){
  return(
    <div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
        <div>
          <SH t="Hover" mt={0} c={C.orange}/>
          <PowerBars loads={HOVER_LOADS}/>
          <div style={{marginTop:12,padding:"10px 12px",background:"rgba(74,222,128,0.07)",
            border:`1px solid ${C.green}44`,borderRadius:4}}>
            <div style={{color:C.green,fontFamily:M,fontSize:10,marginBottom:4}}>
              5S 2200mAh (80% usable · 1760mAh)
            </div>
            <span style={{color:C.yellow,fontFamily:M,fontSize:20,fontWeight:"bold"}}>{hMin} min</span>
            <span style={{color:C.dim,fontFamily:M,fontSize:11,marginLeft:12}}>hover endurance</span>
            <div style={{color:C.dimmer,fontFamily:M,fontSize:9,marginTop:5}}>
              5S 3000mAh → <span style={{color:C.teal}}>{h3Min} min</span> hover (+70g, AUW {AUW+70}g, T/W {(THRUST_NAC/(AUW+70)).toFixed(2)})
            </div>
          </div>
        </div>
        <div>
          <SH t="Cruise" mt={0} c={C.yellow}/>
          <PowerBars loads={CRUISE_LOADS}/>
          <div style={{marginTop:12,padding:"10px 12px",background:"rgba(74,222,128,0.07)",
            border:`1px solid ${C.green}44`,borderRadius:4}}>
            <div style={{color:C.green,fontFamily:M,fontSize:10,marginBottom:4}}>
              5S 2200mAh (80% usable · 1760mAh)
            </div>
            <span style={{color:C.yellow,fontFamily:M,fontSize:20,fontWeight:"bold"}}>{cMin} min</span>
            <span style={{color:C.dim,fontFamily:M,fontSize:11,marginLeft:12}}>cruise endurance</span>
            <div style={{color:C.dimmer,fontFamily:M,fontSize:9,marginTop:5}}>
              5S 3000mAh → <span style={{color:C.teal}}>{c3Min} min</span> cruise
            </div>
          </div>
        </div>
      </div>
      <SH t="ESC Thermal Budget (35A ESC on 65mm EDF)"/>
      <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:12}}>
        {[
          {st:"Hover (sustained)",i:I_65_HOV.toFixed(1)+"A",pct:Math.round(I_65_HOV/35*100)+"%",note:"Well within 35A continuous rating. ESC at ~"+(I_65_HOV/35*100).toFixed(0)+"% load — cool running.",c:C.green},
          {st:"Transition climb",i:"20A",pct:"57%",note:"Brief 8–12s burst during transition from hover to cruise. Acceptable for BLHeli32 with adequate airflow.",c:C.yellow},
          {st:"Full throttle (WOT)",i:"28A",pct:"80%",note:"Short burst only. 35A ESC has 20% headroom at WOT. Always run with motor-cooling airflow from the EDF duct.",c:C.orange},
        ].map((s,i)=>(
          <div key={i} style={{padding:"10px 12px",border:`1px solid ${s.c}33`,background:`${s.c}06`,borderRadius:4}}>
            <div style={{color:s.c,fontFamily:M,fontSize:10,fontWeight:"bold",marginBottom:5}}>{s.st}</div>
            <div style={{color:C.yellow,fontFamily:M,fontSize:14}}>{s.i} <span style={{color:C.dim,fontSize:10}}>({s.pct} of 35A)</span></div>
            <div style={{color:C.dimmer,fontFamily:M,fontSize:9,marginTop:4,lineHeight:1.6}}>{s.note}</div>
          </div>
        ))}
      </div>
      <Note c={C.accent} ch={`Max instantaneous draw: 2× 65mm WOT (56A) + 35mm cruise (12A) + avionics (2A) = 70A. Specify the 5S 2200mAh at ≥75C continuous to stay within current rating (2.2Ah × 75C = 165A capability — ample headroom). Wire the power bus with 12AWG silicone from the battery XT60 to the main distribution point.`}/>
    </div>
  );
}

// ── WEIGHT TAB ────────────────────────────────────────────────
function WeightTab(){
  const groups=WT_GROUPS.map(g=>({...g,total:g.items.reduce((s,i)=>s+i.w,0)}));
  const maxG=Math.max(...groups.map(g=>g.total));
  return(
    <div>
      <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:12,marginBottom:20}}>
        {[
          {l:"Total AUW",v:`${AUW}g`,c:C.yellow,s:"65mm + 35mm upgrade"},
          {l:"Nacelle T/W",v:`${TW}:1`,c:parseFloat(TW)>=1.8?C.green:C.red,s:"Vertical lift margin"},
          {l:"Total T/W (all fans)",v:`${(THRUST_TOTAL/AUW).toFixed(2)}:1`,c:C.green,s:"Including fwd EDF"},
          {l:"Hover throttle",v:`~${HVRT}%`,c:HVRT<58?C.green:C.orange,s:"65mm @ AUW"},
        ].map((s,i)=>(
          <div key={i} style={{padding:"10px 12px",border:`1px solid ${s.c}44`,background:`${s.c}07`,borderRadius:4}}>
            <div style={{color:C.dim,fontFamily:M,fontSize:9,letterSpacing:"0.08em",marginBottom:3}}>{s.l}</div>
            <div style={{color:s.c,fontFamily:M,fontSize:18,fontWeight:"bold"}}>{s.v}</div>
            <div style={{color:C.dimmer,fontFamily:M,fontSize:9,marginTop:2}}>{s.s}</div>
          </div>
        ))}
      </div>
      {groups.map((g,gi)=>(
        <div key={gi} style={{marginBottom:13}}>
          <div style={{display:"flex",justifyContent:"space-between",marginBottom:3}}>
            <span style={{color:g.c,fontFamily:M,fontSize:11,fontWeight:"bold"}}>{g.label}</span>
            <span style={{color:g.c,fontFamily:M,fontSize:11}}>{g.total}g
              <span style={{color:C.dimmer,fontSize:9,marginLeft:6}}>({Math.round(g.total/AUW*100)}%)</span>
            </span>
          </div>
          <div style={{background:"rgba(255,255,255,0.05)",borderRadius:2,height:9,overflow:"hidden",marginBottom:4}}>
            <div style={{width:`${(g.total/maxG)*100}%`,height:"100%",background:g.c,opacity:.55}}/>
          </div>
          <div style={{display:"flex",flexWrap:"wrap",gap:"2px 16px"}}>
            {g.items.map((it,ii)=>(
              <span key={ii} style={{color:C.dimmer,fontFamily:M,fontSize:9}}>
                {it.n}: <span style={{color:g.c}}>{it.w}g</span>
              </span>
            ))}
          </div>
        </div>
      ))}
      <div style={{borderTop:`2px solid ${C.accent}`,marginTop:12,paddingTop:12,
        display:"flex",justifyContent:"space-between",alignItems:"baseline"}}>
        <span style={{color:C.accent,fontFamily:M,fontSize:13,fontWeight:"bold"}}>TOTAL AUW</span>
        <span style={{color:C.yellow,fontFamily:M,fontSize:24,fontWeight:"bold"}}>{AUW} g</span>
      </div>
      <SH t="Version Delta"/>
      <div style={{overflowX:"auto"}}>
        <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:11}}>
          <thead><tr>{["ITEM","REV A (60+30mm)","REV B (65+35mm)","DELTA"].map(h=>(
            <th key={h} style={{padding:"5px 10px",borderBottom:`1px solid ${C.border}`,color:C.accent,
              textAlign:"left",fontWeight:"normal",fontSize:10,opacity:.8}}>{h}</th>
          ))}</tr></thead>
          <tbody>{[
            ["2× nacelle EDFs + motors","80g","104g","+24g"],
            ["2× nacelle ESCs","28g","32g","+4g"],
            ["Fwd EDF + motor","18g","24g","+6g"],
            ["Fwd ESC","8g","10g","+2g"],
            ["Nacelle thrust","1300g","1600g","+300g ✓"],
            ["Fwd fan thrust","80g","140g","+60g ✓"],
            ["Total T/W (nacelles)","1.87:1","2.19:1","+0.32 ✓"],
            ["Hover throttle","~55%",`~${HVRT}%`,"−9% ✓"],
            ["Total AUW","696g",`${AUW}g`,`+${AUW-696}g`],
          ].map(([item,a,b,d],i)=>(
            <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
              <td style={{padding:"5px 10px",color:C.text}}>{item}</td>
              <td style={{padding:"5px 10px",color:C.dim}}>{a}</td>
              <td style={{padding:"5px 10px",color:d.includes("✓")?C.green:d.startsWith("+")?C.yellow:C.dim}}>{b}</td>
              <td style={{padding:"5px 10px",color:d.includes("✓")?C.green:d.startsWith("+")?C.orange:C.dim,fontWeight:"bold"}}>{d}</td>
            </tr>
          ))}</tbody>
        </table>
      </div>
      <Good ch={`Rev B net: +36g weight, +300g nacelle thrust, +60g fwd thrust. T/W improves from 1.87 to ${TW}. Hover throttle drops from ~55% to ~${HVRT}%. This is the better operating point — larger margin for wind gusts, payload, and transition manoeuvres.`}/>
    </div>
  );
}

// ── APP ───────────────────────────────────────────────────────
const TABS=["Airframe Views","Propulsion Spec","Power Budget","Weight & Balance"];

export default function App(){
  const [tab,setTab]=useState("Airframe Views");
  return(
    <div style={{minHeight:"100vh",background:C.bg,color:C.text,fontFamily:M}}>
      <Grid/>
      <div style={{position:"relative",zIndex:1,borderBottom:`1px solid ${C.border}`,padding:"20px 28px 16px"}}>
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",flexWrap:"wrap",gap:12}}>
          <div>
            <div style={{color:"rgba(0,229,255,0.32)",fontSize:9,letterSpacing:"0.2em",marginBottom:5}}>
              SERENITY TILTROTOR · PROPULSION UPGRADE · REV B
            </div>
            <h1 style={{margin:0,fontSize:20,fontWeight:"normal",color:"#fff",letterSpacing:"0.07em"}}>
              65mm NACELLE + 35mm FUSELAGE EDF
            </h1>
            <div style={{color:"rgba(255,107,53,0.6)",fontSize:10,marginTop:5}}>
              2× 65mm · 800g each · 1600g nacelle thrust ·&nbsp;
              <span style={{color:C.yellow}}>35mm · 140g fwd thrust</span>
            </div>
          </div>
          <div style={{textAlign:"right",fontFamily:M}}>
            <div style={{color:C.yellow,fontSize:14,fontWeight:"bold"}}>AUW {AUW}g</div>
            <div style={{color:C.green,fontSize:13,marginTop:3,fontWeight:"bold"}}>T/W {TW}:1</div>
            <div style={{color:C.dimmer,fontSize:9,marginTop:2}}>hover ~{HVRT}% · +36g vs Rev A</div>
          </div>
        </div>
        <div style={{display:"flex",gap:2,marginTop:16,flexWrap:"wrap"}}>
          {TABS.map(t=>(
            <button key={t} onClick={()=>setTab(t)} style={{
              background:tab===t?"rgba(0,229,255,0.09)":"transparent",
              border:`1px solid ${tab===t?C.accent:"rgba(0,229,255,0.14)"}`,
              color:tab===t?C.accent:C.dimmer,padding:"5px 14px",fontFamily:M,
              fontSize:10,cursor:"pointer",letterSpacing:"0.07em",transition:"all 0.12s"}}>{t}</button>
          ))}
        </div>
      </div>
      <div style={{position:"relative",zIndex:1,padding:"24px 28px",maxWidth:1060,margin:"0 auto"}}>
        {tab==="Airframe Views"   && <DiagramTab/>}
        {tab==="Propulsion Spec"  && <PropTab/>}
        {tab==="Power Budget"     && <PowerTab/>}
        {tab==="Weight & Balance" && <WeightTab/>}
      </div>
      <div style={{position:"relative",zIndex:1,borderTop:`1px solid ${C.border}`,
        padding:"11px 28px",display:"flex",justifyContent:"space-between",flexWrap:"wrap",gap:6}}>
        <span style={{color:"rgba(0,229,255,0.18)",fontSize:8,letterSpacing:"0.12em"}}>
          SERENITY TILTROTOR · REV B · 65mm NACELLE + 35mm FUSELAGE EDF
        </span>
        <span style={{color:"rgba(0,229,255,0.18)",fontSize:8,letterSpacing:"0.1em"}}>
          REFERENCE DESIGN · VERIFY BEFORE FLIGHT
        </span>
      </div>
    </div>
  );
}
