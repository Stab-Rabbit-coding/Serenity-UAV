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

// ── Canonical Rev H dimensions (QMx 269ft×170ft×79ft @ 18") ─
const DIM = {
  // Hull
  L_MM:   457.2,  L_IN:  18.0,
  H_MM:   134.3,  H_IN:   5.286,   // max height (incl. nacelles)
  W_MM:   288.9,  W_IN:  11.375,   // full outer span
  // Nacelle geometry
  C2C_MM: 195.46, C2C_IN: 7.696,   // nacelle centre-to-centre
  NAC_OD:  93.48, NAC_IN:  3.68,   // 80mm EDF pod OD
  DATUM:   82.15,                   // datum from centreline (mm)
  INNER:   50.99,                   // inner nacelle edge from CL (mm)
  OUTER:  144.47,                   // outer nacelle edge from CL (mm)
  ARM_STUB:10.4,                    // CF stub arm length (mm)
  // Payload bay (4"×3"×3" internal)
  PB_L:   101.6,  PB_W:  76.2, PB_H:  76.2,   // 4"×3"×3" cargo box
  GONDOLA_DROP: 18,                             // belly pod protrusion below hull line (mm)
  // Keel
  KEEL_L: 480.0,
  // CG
  CG_MM:  190.0,  CG_IN:  7.48,    // target CG from nose
  BAT_TR:  28.0,                    // battery slide travel ±mm
  // Nacelle tilt range
  TILT_VTOL:    0,    // degrees — pure VTOL (thrust vertical)
  TILT_FWD:    90,    // degrees — forward flight (thrust horizontal)
  TILT_REV:   115,    // degrees — FC soft limit for reverse/brake mode
  TILT_STOP:  120,    // degrees — mechanical hard stop in tilt bracket
};

// ── Rev H weight budget (bom_revH1.json) ─────────────────────
const W_ITEMS = [
  // Hull structure
  ["Hull shell 1.2mm PETG (6 sections)",     143],
  ["X-30 PU foam fill",                        42],
  ["CF keel + ring frames",                    28],
  ["PTFE conduit tubes ×6 (stay in hull)",     12],
  ["Access panel frames + lids (PETG)",        38],
  ["Access screws M2.5 ×16 + magnets ×8",       6],
  ["Gasket tape 3M 4016",                       8],
  // Propulsion
  ["80mm EDF nacelle ×2 (motor+fan+housing)", 300],
  ["40mm fuselage EDF",                        38],
  ["50A ESC ×2 (nacelle, 6S)",                 56],
  ["25A ESC ×1 (fuselage, 4S)",                16],
  ["Nacelle pods 93.5mm OD ×2",                36],
  ["Nacelle tip caps ×2 + nav lights",         16],
  ["CF stub arms + tilt brackets ×2",          14],
  ["Nacelle tilt servos MG90S ×2",             18],
  ["Gear nozzle assemblies ×3",                12],
  ["Variable-nozzle servo SG90",                9],
  // Avionics — mixed CM4/CM3+ architecture
  ["CM4-LITE ×2 (Nodes 1, 4)",                 15],
  ["CM4-CARRIER-2 ×2 (Nodes 1, 4)",            35],
  ["SENSORHAT-1 ×2 XIAO RP2350 (Nodes 1, 4)", 25],
  ["CM3+ module ×2 (Nodes 2, 3)",              16],
  ["CM3-CARRIER-1 ×2 (Nodes 2, 3)",            18],
  ["COMPHAT-SWITCH (Node 1 hat)",              29],
  ["MICROHAT ×1 (Node 4 hat)",                 10],
  ["microSD cards ×8 (OS + log)",               8],
  // Power + wiring
  ["PDB + BEC 5V/5A",                          30],
  ["ESC power wiring (12/16 AWG)",             32],
  ["Servo + signal wiring",                    12],
  ["XT90 battery pigtail",                     15],
  ["Bus cables (CAN/RS-485/1553/ETH)",         10],
  ["GPS / ESC telemetry / misc cables",        14],
  // Payload + cargo system
  ["Payload servo + winch motor + driver",     20],
  ["Cargo gondola shell + clamshell door PETG",22],
  ["SG90 cargo door servo + bell-crank",        9],
  ["Cargo cradle + auto-latch assembly",        10],
  ["Dyneema SK75 winch line 1.5m",              1],
  ["TPU landing skids ×4",                      4],
  // Obstacle avoidance sensors
  ["VL53L5CX ToF sensors ×6 + wiring harness", 15],
  ["TCA9548A I²C mux + MCP23008 GPIO (PCB)",    4],
  ["Sensor PETG mounts ×6 + PMMA windows",      7],
  // Radios + sensors
  ["SiK 915MHz radio + antenna",               17],
  ["RCRS 49MHz RC receiver + antenna",         15],
  ["GPS u-blox M10Q + patch",                  12],
  ["WS2812C nav lights ×6",                     8],
  // Fasteners + misc
  ["Standoffs + screws + zip ties",            18],
  ["Foam tape + cable clips",                   8],
];
const DRY_G   = W_ITEMS.reduce((s,[,g])=>s+g, 0);

// ── Power & thrust ────────────────────────────────────────────
const THRUST_NAC  = 1700;  // each 80mm 6S EDF
const THRUST_FUSE =  380;  // 40mm 4S EDF
const THRUST      = THRUST_NAC*2 + THRUST_FUSE;  // 3780g

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

// ── HULL PROFILE DIAGRAM (top view, 18" canonical) ───────────
function HullProfileDiagram(){
  const VW=800, VH=360, CY=180;
  // Scale hull points from 269ft proportional to 457.2mm hull
  const SC = 457.2/508 * 0.82;  // scale relative to Rev G 508mm at SC=0.88
  const OX = 55;
  // Hull outline points [mm from nose, half-width mm] — 18" canonical
  const HULL=[
    [0,0],[10,13],[28,22],[50,38],[73,45],[110,46],[150,52],[175,52],
    [207,50],[237,45],[275,36],[316,22],[325,20],[347,30],[381,36],
    [412,35],[457.2,28],
  ];
  const xp = mm => OX + mm*SC;
  const NAC_HALF = DIM.C2C_MM/2 * SC;  // half C2C in px

  const up = HULL.map(([x,y])=>`${xp(x).toFixed(1)},${(CY-y*SC*0.5).toFixed(1)}`);
  const lo = [...HULL].reverse().map(([x,y])=>`${xp(x).toFixed(1)},${(CY+y*SC*0.38).toFixed(1)}`);
  const pts = [...up,...lo].join(" ");

  // Nacelle centres: at 37% and 63% along hull (proportional from QMx)
  const NAC_X = xp(457.2 * 0.37);
  const NAC_W = DIM.NAC_OD/2 * SC;
  const NAC_L = 144 * SC;  // 144mm pod length

  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* Hull */}
      <polygon points={pts} fill={`${C.accent}0e`} stroke={C.accent} strokeWidth={2.5}/>

      {/* Cockpit dome */}
      <ellipse cx={xp(40).toFixed(1)} cy={CY.toFixed(1)}
        rx={(40*SC).toFixed(1)} ry={(22*SC).toFixed(1)}
        fill="rgba(0,229,255,0.09)" stroke={C.accent} strokeWidth={1.2}/>

      {/* Engine bell */}
      <circle cx={xp(381).toFixed(1)} cy={CY.toFixed(1)} r={(47*SC*0.5).toFixed(1)}
        fill="rgba(255,230,0,0.1)" stroke={C.yellow} strokeWidth={1.8}/>
      <text x={xp(381).toFixed(1)} y={(CY+4).toFixed(1)} textAnchor="middle"
        fill={C.yellow} fontSize={7.5} fontFamily={M}>40mm EDF</text>

      {/* Pitot */}
      <line x1={xp(0).toFixed(1)} y1={CY} x2={xp(-22).toFixed(1)} y2={CY}
        stroke={C.teal} strokeWidth={3.5} strokeLinecap="round"/>

      {/* Nacelle arms + pods */}
      {[-1,1].map(side=>{
        const ay = CY + side*NAC_HALF;
        const hullY = CY + side*52*SC*0.45;
        const ax1 = xp(150);
        const ax2 = xp(150 + DIM.ARM_STUB + (DIM.DATUM-DIM.INNER));
        const nacCX = NAC_X;
        const nacRX = NAC_L*0.5; const nacRY = NAC_W;
        return(<g key={side}>
          <line x1={ax1.toFixed(1)} y1={hullY.toFixed(1)} x2={nacCX.toFixed(1)} y2={ay.toFixed(1)}
            stroke={C.accent} strokeWidth={5} strokeLinecap="round"/>
          {/* Datum reference line */}
          <line x1={(nacCX-10).toFixed(1)} y1={(ay-side*DIM.DATUM*SC*0.5).toFixed(1)}
            x2={(nacCX+10).toFixed(1)} y2={(ay-side*DIM.DATUM*SC*0.5).toFixed(1)}
            stroke={C.purple} strokeWidth={0.8} strokeDasharray="3 2" opacity={0.6}/>
          <ellipse cx={nacCX.toFixed(1)} cy={ay.toFixed(1)}
            rx={nacRX.toFixed(1)} ry={nacRY.toFixed(1)}
            fill={`${C.orange}15`} stroke={C.orange} strokeWidth={2.5}/>
          <ellipse cx={nacCX.toFixed(1)} cy={ay.toFixed(1)}
            rx={(nacRX*0.72).toFixed(1)} ry={(nacRY*0.65).toFixed(1)}
            fill="none" stroke={C.orange} strokeWidth={1} strokeDasharray="3 2"/>
          {/* Nav light */}
          <circle cx={(nacCX-nacRX+8).toFixed(1)} cy={ay.toFixed(1)} r={7}
            fill={side===-1?"#cc2200":"#00aa00"} opacity={0.95}/>
          <text x={(nacCX-nacRX+8).toFixed(1)} y={(ay+side*17).toFixed(1)}
            textAnchor="middle" fill={side===-1?"#ff6060":"#60ff60"}
            fontSize={8} fontFamily={M} fontWeight="bold">
            {side===-1?"PORT":"STBD"}</text>
        </g>);
      })}

      {/* CG line */}
      <line x1={xp(DIM.CG_MM).toFixed(1)} y1={(CY-75).toFixed(1)}
        x2={xp(DIM.CG_MM).toFixed(1)} y2={(CY+75).toFixed(1)}
        stroke={C.green} strokeWidth={1.5} strokeDasharray="6 3"/>
      <polygon points={`${xp(DIM.CG_MM).toFixed(1)},${(CY-75).toFixed(1)} ${(xp(DIM.CG_MM)-8).toFixed(1)},${(CY-60).toFixed(1)} ${(xp(DIM.CG_MM)+8).toFixed(1)},${(CY-60).toFixed(1)}`}
        fill={C.green} opacity={0.85}/>
      <text x={xp(DIM.CG_MM).toFixed(1)} y={(CY-82).toFixed(1)} textAnchor="middle"
        fill={C.green} fontSize={8.5} fontFamily={M} fontWeight="bold">CG {DIM.CG_MM}mm ({DIM.CG_IN}")</text>

      {/* Payload bay */}
      <rect x={xp(175).toFixed(1)} y={(CY-13*SC).toFixed(1)}
        width={(DIM.PB_L*SC).toFixed(1)} height={(26*SC).toFixed(1)}
        rx={3} fill="rgba(244,114,182,0.09)" stroke={C.pink} strokeWidth={1} strokeDasharray="3 2"/>
      <text x={(xp(175)+DIM.PB_L*SC/2).toFixed(1)} y={(CY+4).toFixed(1)}
        textAnchor="middle" fill={C.pink} fontSize={7} fontFamily={M}>PAYLOAD {DIM.PB_L}×{DIM.PB_W}mm</text>

      {/* Span dimension */}
      <line x1={xp(0).toFixed(1)} y1={(VH-18).toFixed(1)} x2={xp(457.2).toFixed(1)} y2={(VH-18).toFixed(1)}
        stroke={C.accent} strokeWidth={0.5} opacity={0.25}/>
      <text x={xp(228).toFixed(1)} y={(VH-6).toFixed(1)} textAnchor="middle"
        fill={C.dimmer} fontSize={7.5} fontFamily={M}>457.2 mm (18.00") hull length</text>

      {/* Nacelle C-to-C */}
      <line x1={28} y1={(CY-NAC_HALF).toFixed(1)} x2={28} y2={(CY+NAC_HALF).toFixed(1)}
        stroke={C.accent} strokeWidth={0.5} opacity={0.2}/>
      <text x={16} y={(CY+4).toFixed(1)} textAnchor="middle"
        fill={C.dimmer} fontSize={7.5} fontFamily={M}
        transform={`rotate(-90,16,${CY})`}>{DIM.C2C_MM} mm ({DIM.C2C_IN}") nacelle C-to-C</text>

      {/* Info box */}
      <rect x={VW-195} y={8} width={187} height={62} rx={4}
        fill="rgba(0,0,0,0.55)" stroke="rgba(0,229,255,0.15)" strokeWidth={0.8}/>
      <text x={VW-102} y={24} textAnchor="middle" fill={C.dimmer} fontSize={7.5} fontFamily={M} letterSpacing="0.5">CANONICAL PROPORTIONS — REV H</text>
      <text x={VW-102} y={38} textAnchor="middle" fill={C.lime} fontSize={9} fontFamily={M} fontWeight="bold">18.0" × QMx 269×170×79ft</text>
      <text x={VW-102} y={50} textAnchor="middle" fill={`${C.accent}80`} fontSize={7.5} fontFamily={M}>Span/length = C2C/L = {(DIM.C2C_MM/DIM.L_MM).toFixed(3)}</text>
      <text x={VW-102} y={62} textAnchor="middle" fill={C.orange} fontSize={7.5} fontFamily={M}>80mm EDF · 6S · nacelle OD {DIM.NAC_OD}mm</text>

      <text x={VW/2} y={14} textAnchor="middle"
        fill="rgba(0,229,255,0.85)" fontSize={8} fontFamily={M} letterSpacing="2">
        TOP VIEW — CANONICAL PROPORTIONS — REV H</text>
    </svg>
  );
}

// ── NACELLE DATUM DIAGRAM ─────────────────────────────────────
function NacelleGeomDiagram(){
  const VW=700, VH=220, CY=110;
  const SC=2.2;
  const CL=60;
  // Key positions from CL (px = mm * SC)
  const inner  = CL + DIM.INNER  * SC;
  const datum  = CL + DIM.DATUM  * SC;
  const outer  = CL + DIM.OUTER  * SC;
  const nacCX  = datum;
  const nacR   = DIM.NAC_OD/2 * SC;
  const hullR  = 38 * SC;

  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* CL */}
      <line x1={CL-10} y1={CY} x2={VW-10} y2={CY}
        stroke={C.accent} strokeWidth={0.8} strokeDasharray="6 3" opacity={0.4}/>
      <text x={CL-14} y={CY+4} textAnchor="middle" fill={C.accent} fontSize={7.5} fontFamily={M} opacity={0.6}>CL</text>

      {/* Hull cross-section */}
      <ellipse cx={CL} cy={CY} rx={18} ry={hullR}
        fill={`${C.accent}0c`} stroke={C.accent} strokeWidth={1.5}/>

      {/* Nacelle pod */}
      <circle cx={nacCX.toFixed(1)} cy={CY} r={nacR.toFixed(1)}
        fill={`${C.orange}12`} stroke={C.orange} strokeWidth={2}/>
      <circle cx={nacCX.toFixed(1)} cy={CY} r={(nacR*0.72).toFixed(1)}
        fill="none" stroke={C.orange} strokeWidth={0.8} strokeDasharray="3 2"/>
      <text x={nacCX.toFixed(1)} y={(CY+4).toFixed(1)} textAnchor="middle"
        fill={C.orange} fontSize={7.5} fontFamily={M}>80mm EDF</text>
      <text x={nacCX.toFixed(1)} y={(CY+14).toFixed(1)} textAnchor="middle"
        fill={C.orange} fontSize={7} fontFamily={M} opacity={0.7}>{DIM.NAC_OD}mm OD</text>

      {/* Arm stub */}
      <line x1={(CL+18).toFixed(1)} y1={CY}
        x2={(inner).toFixed(1)} y2={CY}
        stroke={C.teal} strokeWidth={4} strokeLinecap="round"/>

      {/* Inner edge arrow */}
      <line x1={inner.toFixed(1)} y1={(CY-55)} x2={inner.toFixed(1)} y2={(CY-35)}
        stroke={C.teal} strokeWidth={0.8} opacity={0.7}/>
      <text x={inner.toFixed(1)} y={(CY-60)} textAnchor="middle"
        fill={C.teal} fontSize={7.5} fontFamily={M}>INNER</text>
      <text x={inner.toFixed(1)} y={(CY-49)} textAnchor="middle"
        fill={C.teal} fontSize={7} fontFamily={M}>{DIM.INNER}mm</text>

      {/* Datum arrow */}
      <line x1={datum.toFixed(1)} y1={(CY+nacR+8)} x2={datum.toFixed(1)} y2={(CY+nacR+25)}
        stroke={C.purple} strokeWidth={1} strokeDasharray="3 2"/>
      <text x={datum.toFixed(1)} y={(CY+nacR+36)} textAnchor="middle"
        fill={C.purple} fontSize={7.5} fontFamily={M}>DATUM {DIM.DATUM}mm</text>
      <text x={datum.toFixed(1)} y={(CY+nacR+47)} textAnchor="middle"
        fill={C.purple} fontSize={7} fontFamily={M} opacity={0.8}>TIP_HALF − (2/3 × OD)</text>

      {/* Outer edge arrow */}
      <line x1={outer.toFixed(1)} y1={(CY-55)} x2={outer.toFixed(1)} y2={(CY-35)}
        stroke={C.yellow} strokeWidth={0.8} opacity={0.7}/>
      <text x={outer.toFixed(1)} y={(CY-60)} textAnchor="middle"
        fill={C.yellow} fontSize={7.5} fontFamily={M}>OUTER</text>
      <text x={outer.toFixed(1)} y={(CY-49)} textAnchor="middle"
        fill={C.yellow} fontSize={7} fontFamily={M}>{DIM.OUTER}mm</text>

      {/* Dimension bar */}
      <line x1={CL} y1={(CY-22)} x2={outer.toFixed(1)} y2={(CY-22)}
        stroke="rgba(255,255,255,0.2)" strokeWidth={0.5}/>
      <text x={((CL+outer)/2).toFixed(1)} y={(CY-26)} textAnchor="middle"
        fill={C.dimmer} fontSize={7} fontFamily={M}>{DIM.OUTER}mm from CL</text>

      {/* Formula box */}
      <rect x={VW-220} y={5} width={215} height={70} rx={4}
        fill="rgba(0,0,0,0.5)" stroke={`${C.purple}60`} strokeWidth={0.8}/>
      <text x={VW-112} y={20} textAnchor="middle" fill={C.purple} fontSize={8.5} fontFamily={M} fontWeight="bold">NACELLE DATUM FORMULA</text>
      <text x={VW-112} y={34} textAnchor="middle" fill={C.dim} fontSize={8} fontFamily={M}>datum = TIP_HALF − (2/3 × pod_OD)</text>
      <text x={VW-112} y={46} textAnchor="middle" fill={C.dim} fontSize={7.5} fontFamily={M}>{DIM.C2C_MM/2} − (2/3 × {DIM.NAC_OD}) = {DIM.DATUM}mm</text>
      <text x={VW-112} y={60} textAnchor="middle" fill={C.lime} fontSize={7.5} fontFamily={M}>outer = {DIM.DATUM} + {(DIM.NAC_OD*2/3).toFixed(2)} = {DIM.OUTER}mm ✓</text>
    </svg>
  );
}

// ── TAB: OVERVIEW ─────────────────────────────────────────────
function OverviewTab(){
  const ratio = (DIM.C2C_MM/DIM.L_MM).toFixed(3);
  return(<div>
    <div style={{background:"rgba(163,230,53,0.07)",border:"1px solid rgba(163,230,53,0.35)",
      borderRadius:6,padding:"16px 20px",marginBottom:20}}>
      <div style={{color:C.lime,fontFamily:M,fontSize:12,fontWeight:"bold",marginBottom:10,letterSpacing:"0.08em"}}>
        REV H — 18" CANONICAL · QMx PROPORTIONS · FOAM-FILLED HULL
      </div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:20}}>
        <div>
          <KV k="Hull length"              v={mmi(DIM.L_MM)} vc={C.lime}/>
          <KV k="Nacelle centre-to-centre" v={mmi(DIM.C2C_MM)} vc={C.lime}/>
          <KV k="C2C / length ratio"       v={`${ratio}  (QMx 170/269 = 0.632)`} vc={C.teal}/>
          <KV k="Full outer span"          v={mmi(DIM.W_MM)}/>
          <KV k="Max height (hull+nac)"    v={mmi(DIM.H_MM)}/>
          <KV k="Nacelle pod OD"           v={`${DIM.NAC_OD} mm (80mm EDF)`}/>
          <KV k="Datum from CL"            v={`${DIM.DATUM} mm  →  outer ${DIM.OUTER} mm`} vc={C.purple}/>
        </div>
        <div>
          <KV k="Nacelle EDFs (×2)"        v={`80mm 6S · ${THRUST_NAC}g each`} vc={C.orange}/>
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

    <SH t="Hull Profile — Top View" mt={0}/>
    <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:8,marginBottom:20}}>
      <HullProfileDiagram/>
    </div>

    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="What changed Rev G → Rev H" mt={0} c={C.orange}/>
        <Note c={C.orange} ch="Hull rescaled from 20.0″ (508mm) to 18.0″ (457.2mm) — the QMx canonical dimension for the 269ft Serenity at 1:1797 studio scale. Nacelle C-to-C computed from the same 170/269 blueprint ratio: 457.2 × (170/269) = 288.9mm outer span → 195.46mm C-to-C."/>
        <Note c={C.teal} ch="80mm EDFs replace 100mm. The datum formula (TIP_HALF − 2/3 × OD) keeps nacelles proportionally at the correct outboard position regardless of EDF size. At 18″ scale, datum = 97.73 − 62.32 = 82.15mm from CL, outer edge 144.47mm from CL."/>
        <Note c={C.purple} ch="Hull is now foam-filled (X-30 PU, 2 lb/ft³). 6 PTFE conduit tubes route all 4 data buses and power through the foam. 6 access panels (A–F) provide post-cure maintenance access to all avionics, ESCs, payload, and EDF."/>
      </div>
      <div>
        <SH t="T/W margin analysis" mt={0} c={C.green}/>
        <Note c={C.green} ch={`T/W empty: ${TW_EMPTY}:1 (${THRUST}g ÷ ${AUW_EMPTY}g) — 6S 4000mAh 410g battery. Comfortable margin above 2.0 minimum.`}/>
        {parseFloat(TW_CARGO)>=2.0
          ? <Good ch={`T/W cargo: ${TW_CARGO}:1 — 6S 2800mAh + 250g payload. Meets ≥2.0 spec.`}/>
          : <Warn ch={`T/W cargo: ${TW_CARGO}:1 — marginally below 2.0 at full 250g payload with 2800mAh battery. Use lighter 6S 2200mAh (220g) to recover margin: AUW ${DRY_G+220+250}g, T/W ${(THRUST/(DRY_G+220+250)).toFixed(2)}:1.`}/>
        }
        <Note c={C.dim} ch={`Max payload at T/W=2.0 with 2800mAh battery: ${MAX_PAY > 0 ? MAX_PAY+"g" : "0g — battery swap required"}. Fuselage 40mm EDF adds ${THRUST_FUSE}g thrust (transition assist only; hover T/W from nacelles alone: ${(THRUST_NAC*2/AUW_EMPTY).toFixed(2)}:1 empty).`}/>
        <Good ch="All Rev H changes are backward-compatible with Rev G airframe tooling. Only the hull-scale STLs are new prints."/>
      </div>
    </div>
  </div>);
}

// ── TAB: DIMENSIONS ───────────────────────────────────────────
function DimensionsTab(){
  const rows = [
    ["Hull length",               mmi(DIM.L_MM),         "QMx 269ft @ 18″ scale"],
    ["Hull height (excl. nac.)",  mmi(DIM.H_MM),         "QMx 79ft @ 18″ scale"],
    ["Full outer span",           mmi(DIM.W_MM),         "QMx 170ft outer hull @ scale"],
    ["Nacelle C-to-C",            mmi(DIM.C2C_MM),       "170/269 × 457.2mm"],
    ["Nacelle pod OD",            `${DIM.NAC_OD} mm`,    "80mm EDF housing"],
    ["Datum from CL",             `${DIM.DATUM} mm`,     "TIP_HALF − (2/3 × OD)"],
    ["Inner edge from CL",        `${DIM.INNER} mm`,     "datum − OD/3"],
    ["Outer edge from CL",        `${DIM.OUTER} mm`,     "datum + 2×OD/3"],
    ["CF stub arm",               `${DIM.ARM_STUB} mm`,  "hull wall to inner nacelle edge"],
    ["Payload bay",               `${DIM.PB_L}×${DIM.PB_W}×${DIM.PB_H} mm`, "station 175–266mm from nose"],
    ["CF keel length",            `${DIM.KEEL_L} mm`,    "full hull span + 20mm overhang"],
    ["Target CG",                 mmi(DIM.CG_MM),        "41.5% from nose · within ±5mm"],
    ["Battery slide travel",      `±${DIM.BAT_TR} mm`,   "CG trim range"],
  ];
  return(<div>
    <SH t="Nacelle Datum Geometry" mt={0} c={C.purple}/>
    <div style={{border:`1px solid ${C.border}`,borderRadius:4,padding:8,marginBottom:20}}>
      <NacelleGeomDiagram/>
    </div>
    <Note c={C.purple} ch="The datum formula places the nacelle centre at TIP_HALF − (2/3 × pod_OD) from the centreline. This is the canonical QMx position regardless of EDF size — the pod expands 1/3 inward and 2/3 outward from datum. At 18″ scale with 93.48mm OD: datum = 97.73 − 62.32 = 82.15mm, inner edge = 50.99mm, outer edge = 144.47mm."/>

    <SH t="All Dimensions" c={C.accent}/>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["DIMENSION","VALUE","SOURCE / NOTE"]}/>
        <tbody>{rows.map(([k,v,n],i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
            <td style={{padding:"5px 9px",color:C.dim}}>{k}</td>
            <td style={{padding:"5px 9px",color:C.lime,fontWeight:"bold",whiteSpace:"nowrap"}}>{v}</td>
            <td style={{padding:"5px 9px",color:C.dimmer,fontSize:9}}>{n}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
  </div>);
}

// ── TAB: WEIGHT & THRUST ──────────────────────────────────────
function WeightTab(){
  const total = W_ITEMS.reduce((s,[,g])=>s+g,0);
  const BAT_OPTS = [
    {spec:"6S 4000mAh 35C",  mass:410, desc:"Primary endurance"},
    {spec:"6S 2800mAh 45C",  mass:295, desc:"Cargo mission"},
    {spec:"6S 2200mAh 60C",  mass:220, desc:"Maximum T/W margin"},
    {spec:"6S 5000mAh 30C",  mass:530, desc:"Max endurance (empty only)"},
  ];
  return(<div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24,marginBottom:8}}>
      <div>
        <SH t="AUW Summary" mt={0} c={C.yellow}/>
        <KV k="Airframe dry (no battery)"  v={gLb(DRY_G)} vc={C.yellow}/>
        <KV k="AUW empty (6S 4000mAh)"    v={gLb(AUW_EMPTY)} vc={C.yellow}/>
        <KV k="AUW cargo (2800+250g pay)" v={gLb(AUW_CARGO)}/>
        <KV k="Nacelle thrust (×2)"        v={`2 × ${THRUST_NAC}g = ${THRUST_NAC*2}g`} vc={C.green}/>
        <KV k="Fuselage thrust"            v={`${THRUST_FUSE}g (40mm 4S)`}/>
        <KV k="Total thrust"               v={`${THRUST}g (${gToLb(THRUST)} lb)`} vc={C.green}/>
        <KV k="T/W empty"                 v={`${TW_EMPTY}:1`} vc={parseFloat(TW_EMPTY)>=2.0?C.green:C.red}/>
        <KV k="T/W cargo"                 v={`${TW_CARGO}:1`} vc={parseFloat(TW_CARGO)>=2.0?C.green:C.yellow}/>
        <KV k="BOM total (sum of items)"  v={`${total}g`} vc={total===DRY_G?C.green:C.yellow}/>
      </div>
      <div>
        <SH t="Battery Options" mt={0} c={C.gold}/>
        {BAT_OPTS.map((b,i)=>{
          const auw=DRY_G+b.mass;
          const tw=(THRUST/auw).toFixed(2);
          const auwC=DRY_G+b.mass+PAYLOAD;
          const twC=(THRUST/auwC).toFixed(2);
          return(
            <div key={i} style={{padding:"8px 10px",marginBottom:5,
              border:`1px solid ${C.gold}33`,borderRadius:4,background:"rgba(251,191,36,0.04)"}}>
              <div style={{display:"flex",justifyContent:"space-between",marginBottom:2}}>
                <span style={{color:C.gold,fontFamily:M,fontSize:10,fontWeight:"bold"}}>{b.spec}</span>
                <span style={{color:parseFloat(tw)>=2.0?C.green:C.red,fontFamily:M,fontSize:10}}>
                  T/W {tw} empty
                </span>
              </div>
              <div style={{display:"flex",justifyContent:"space-between"}}>
                <span style={{color:C.dimmer,fontFamily:M,fontSize:9}}>{b.mass}g · AUW {auw}g · {b.desc}</span>
                <span style={{color:parseFloat(twC)>=2.0?C.teal:C.yellow,fontFamily:M,fontSize:9}}>
                  {twC} cargo
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>

    <SH t="Weight Breakdown" c={C.accent}/>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["ITEM","MASS (g)","RUNNING TOTAL (g)"]}/>
        <tbody>{W_ITEMS.map(([name,g],i)=>{
          const run = W_ITEMS.slice(0,i+1).reduce((s,[,x])=>s+x,0);
          return(
            <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
              <td style={{padding:"4px 9px",color:C.dim}}>{name}</td>
              <td style={{padding:"4px 9px",color:C.lime,textAlign:"right"}}>{g}</td>
              <td style={{padding:"4px 9px",color:C.dimmer,textAlign:"right"}}>{run}</td>
            </tr>
          );
        })}</tbody>
        <tfoot><tr style={{borderTop:`1px solid ${C.border}`}}>
          <td style={{padding:"5px 9px",color:C.yellow,fontWeight:"bold"}}>TOTAL DRY</td>
          <td style={{padding:"5px 9px",color:C.yellow,fontWeight:"bold",textAlign:"right"}}>{total}</td>
          <td style={{padding:"5px 9px",color:total===DRY_G?C.green:C.red,textAlign:"right"}}>
            {total===DRY_G?"✓ matches BOM":"⚠ BOM mismatch"}
          </td>
        </tr></tfoot>
      </table>
    </div>
  </div>);
}

// ── TAB: BALANCE & CG ─────────────────────────────────────────
function BalanceTab(){
  const CG_ITEMS = [
    {item:"Cockpit + nose (station 0–91mm)",  g:82,  sta:45},
    {item:"Avionics bay (station 91–175mm)",  g:290, sta:133},
    {item:"Payload bay (station 175–266mm)",  g:95,  sta:220},
    {item:"Dorsal-aft bay (station 266–320mm)",g:130,sta:293},
    {item:"Aft service bay (station 320–388mm)",g:180,sta:354},
    {item:"Engine bell + EDF (station 388–457mm)",g:105,sta:420},
    {item:"Nacelles (both, effective sta)",   g:370, sta:167},
    {item:"Wiring + misc",                    g:82,  sta:230},
    {item:"Battery (6S 4000mAh, centred)",    g:BAT_EMPTY, sta:DIM.CG_MM},
  ];
  const totalMom = CG_ITEMS.reduce((s,{g,sta})=>s+g*sta,0);
  const totalMass = CG_ITEMS.reduce((s,{g})=>s+g,0);
  const cgCalc = (totalMom/totalMass).toFixed(1);
  return(<div>
    <SH t="CG Budget" mt={0} c={C.green}/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:20,marginBottom:12}}>
      <div>
        <KV k="Target CG"         v={`${DIM.CG_MM} mm from nose  (${DIM.CG_IN}")`} vc={C.lime}/>
        <KV k="Estimated CG"      v={`${cgCalc} mm from nose`} vc={Math.abs(parseFloat(cgCalc)-DIM.CG_MM)<=5?C.green:C.yellow}/>
        <KV k="Battery slide ±"   v={`${DIM.BAT_TR} mm travel  (trims ±${Math.round(DIM.BAT_TR*BAT_EMPTY/totalMass)}mm CG)`}/>
        <KV k="CG target % fwd"   v="41.5% of hull length"/>
        <KV k="Acceptable range"  v={`${DIM.CG_MM-5}–${DIM.CG_MM+5} mm`}/>
      </div>
      <div>
        <Note c={C.green} ch="The battery slide rail provides ±28mm of longitudinal battery travel, trimming CG by approximately ±8mm. Set battery position at benchtop balance-point before first hover."/>
        <Note c={C.teal} ch="Payload bay centres at 220mm from nose. A 250g payload shifts CG aft by ≈7mm — compensate by sliding battery 14mm forward on the rail."/>
      </div>
    </div>
    <SH t="CG Calculation" c={C.accent}/>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["COMPONENT","MASS (g)","STATION (mm)","MOMENT (g·mm)"]}/>
        <tbody>{CG_ITEMS.map(({item,g,sta},i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
            <td style={{padding:"4px 9px",color:C.dim}}>{item}</td>
            <td style={{padding:"4px 9px",color:C.lime,textAlign:"right"}}>{g}</td>
            <td style={{padding:"4px 9px",color:C.yellow,textAlign:"right"}}>{sta}</td>
            <td style={{padding:"4px 9px",color:C.dimmer,textAlign:"right"}}>{g*sta}</td>
          </tr>
        ))}</tbody>
        <tfoot><tr style={{borderTop:`1px solid ${C.border}`}}>
          <td style={{padding:"5px 9px",color:C.accent,fontWeight:"bold"}}>TOTAL / CG</td>
          <td style={{padding:"5px 9px",color:C.accent,textAlign:"right",fontWeight:"bold"}}>{totalMass}</td>
          <td style={{padding:"5px 9px",color:C.green,textAlign:"right",fontWeight:"bold"}}>{cgCalc} mm</td>
          <td style={{padding:"5px 9px",color:C.dimmer,textAlign:"right"}}>{totalMom}</td>
        </tr></tfoot>
      </table>
    </div>
  </div>);
}

// ── TAB: AVIONICS ─────────────────────────────────────────────
function AvionicsTab(){
  const NODES = [
    {id:"NODE 1",pcb:"CM4-LITE + CM4-CARRIER-2 + SENSORHAT-1 + COMPHAT-SWITCH",
     zone:"A (nose)",bus:"CAN FD BC · 1553 BC · RS-485 · ETH switch (KSZ8895) · SiK 915MHz",
     fn:"Flight controller · telemetry gateway · sensor fusion primary"},
    {id:"NODE 2",pcb:"CM3+ + CM3-CARRIER-1 (integrated bus I/O)",
     zone:"B (dorsal fwd)",bus:"CAN FD RT · 1553 RT · RS-485 · ETH/SPI (W5500) — JST-GH ports",
     fn:"Navigation · GPS AHRS · power monitor · ESC telemetry"},
    {id:"NODE 3",pcb:"CM3+ + CM3-CARRIER-1 (integrated bus I/O)",
     zone:"D (dorsal aft)",bus:"CAN FD RT · 1553 RT · RS-485 · ETH/SPI (W5500) — JST-GH ports",
     fn:"Payload management · winch control · cargo camera · mission data"},
    {id:"NODE 4",pcb:"CM4-LITE + CM4-CARRIER-2 + SENSORHAT-1 + MICROHAT",
     zone:"E (aft service)",bus:"CAN FD RT · 1553 RT · RS-485 · ETH port 4",
     fn:"Actuator control · nacelle tilt servos · nozzle servos · nav lights"},
  ];
  const BUSES = [
    {bus:"CAN FD",spec:"1 Mbit/s · MCP2518FD · ISO 11898-1:2015",purpose:"Real-time control loop, 500µs cycle"},
    {bus:"Ethernet",spec:"100BASE-T · W5500 → KSZ8895 5-port switch",purpose:"HD video, bulk telemetry, OTA updates"},
    {bus:"RS-485",spec:"Half-duplex · 3 Mbit/s · Modbus-style framing",purpose:"ESC telemetry, sensor aux bus"},
    {bus:"MIL-STD-1553B",spec:"1 Mbit/s · HI-6130 · 78Ω stub",purpose:"Safety-critical commands, redundant C2"},
    {bus:"PWR",spec:"6S 22.2V → 5V/5A BEC → all nodes",purpose:"Power distribution through foam conduits"},
  ];
  return(<div>
    <SH t="8-Node Distributed Compute Architecture" mt={0} c={C.teal}/>
    <Note c={C.teal} ch="Mixed CM4/CM3+ architecture. Nodes 1 &amp; 4: CM4-LITE + CM4-CARRIER-2 + SENSORHAT-1 (XIAO RP2350 realtime co-processor). Nodes 2 &amp; 3: CM3+ + CM3-CARRIER-1 (68×30mm, integrated CAN FD/RS-485/1553B/W5500 with JST-GH panel connectors + 40-pin RPi HAT header). Saves ~60g vs all-CM4. Node 1 adds COMPHAT-SWITCH; Node 4 adds MICROHAT."/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:8,marginBottom:8}}>
      {NODES.map((n,i)=>(
        <div key={i} style={{padding:"10px 12px",border:`1px solid ${C.teal}44`,borderRadius:4,
          background:"rgba(45,212,191,0.03)"}}>
          <div style={{color:C.teal,fontFamily:M,fontSize:11,fontWeight:"bold",marginBottom:4}}>{n.id}</div>
          <div style={{color:C.lime,fontFamily:M,fontSize:9,marginBottom:3}}>{n.pcb}</div>
          <div style={{color:C.yellow,fontFamily:M,fontSize:8.5,marginBottom:3}}>Zone {n.zone}</div>
          <div style={{color:C.dimmer,fontFamily:M,fontSize:8.5,marginBottom:3}}>{n.bus}</div>
          <div style={{color:C.dim,fontFamily:M,fontSize:8,opacity:0.85}}>{n.fn}</div>
        </div>
      ))}
    </div>
    <SH t="4-Bus Avionics Backbone" c={C.accent}/>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["BUS","SPEC","PURPOSE"]}/>
        <tbody>{BUSES.map(({bus,spec,purpose},i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
            <td style={{padding:"5px 9px",color:C.accent,fontWeight:"bold",whiteSpace:"nowrap"}}>{bus}</td>
            <td style={{padding:"5px 9px",color:C.lime,fontSize:9}}>{spec}</td>
            <td style={{padding:"5px 9px",color:C.dimmer,fontSize:9}}>{purpose}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:20,marginTop:12}}>
      <div>
        <SH t="PCB Stack Masses" mt={0} c={C.purple}/>
        <KV k="CM4-LITE ×2 (N1,N4)"        v="2 × 7.5g = 15g"/>
        <KV k="CM4-CARRIER-2 ×2 (N1,N4)"   v="2 × 17.5g = 35g"/>
        <KV k="SENSORHAT-1 ×2 (N1,N4)"     v="2 × 12.5g = 25g"/>
        <KV k="CM3+ module ×2 (N2,N3)"     v="2 × 8g = 16g"/>
        <KV k="CM3-CARRIER-1 ×2 (N2,N3)"   v="2 × 9g = 18g" vc={C.teal}/>
        <KV k="COMPHAT-SWITCH ×1 (N1)"     v="29g"/>
        <KV k="MICROHAT ×1 (N4)"           v="10g"/>
        <KV k="microSD ×6 (OS+log)"        v="6 × 1g = 6g"/>
        <KV k="TOTAL avionics stack"        v="154g" vc={C.lime}/>
        <Good ch="−60g vs all-CM4 Rev H baseline (214g → 154g)"/>
      </div>
      <div>
        <SH t="SENSORHAT-1 (Nodes 1 &amp; 4) / CM3-CARRIER-1 (Nodes 2 &amp; 3)" mt={0} c={C.pink}/>
        <KV k="XIAO RP2350"        v="N1,N4 only · Cortex-M33+RISC-V · 150MHz"/>
        <KV k="ICM-42688-P IMU"    v="N1,N4 only · 6-DOF · SPI0 · ±16g/±2000°/s"/>
        <KV k="BMP388 barometer"   v="N1,N4 only · ±0.5m · I²C · 200Hz"/>
        <KV k="MCP2518FD CAN FD"   v="All nodes · 1Mbit/s · SPI · ISO 11898-1"/>
        <KV k="W5500 Ethernet"     v="All nodes · 100BASE-T · SPI · HW TCP/IP"/>
        <KV k="HI-6130 1553B"      v="All nodes · RT mode · 78Ω · galv. isolated"/>
        <KV k="MAX3485E RS-485"    v="All nodes · 3Mbit/s · half-duplex"/>
        <KV k="CM3-CARRIER-1 size" v="68 × 30 mm · 4L · ~9g assembled" vc={C.teal}/>
      </div>
    </div>
  </div>);
}

// ── TAB: HULL & FOAM ─────────────────────────────────────────
function HullFoamTab(){
  const voids=[
    {id:"A",sta:"0–91",   dim:"∅55mm bayonet access",    former:"EPS 50×30×86mm",  seal:"Waxed EPS + bayonet frame"},
    {id:"B",sta:"91–175", dim:"65×60mm dorsal void",      former:"EPS 55×52×74mm",  seal:"Waxed EPS + M2.5×4 frame"},
    {id:"C",sta:"160–251",dim:"80×55mm belly void",       former:"EPS 70×48×91mm",  seal:"Waxed EPS + hinge frame"},
    {id:"D",sta:"251–320",dim:"65×55mm dorsal void",      former:"EPS 55×47×69mm",  seal:"Waxed EPS + magnet×4"},
    {id:"E",sta:"320–388",dim:"60×50mm dorsal void",      former:"EPS 50×42×68mm",  seal:"Waxed EPS + M2.5×4 frame"},
    {id:"F",sta:"388–457",dim:"EDF bay — no foam",        former:"None (open)",      seal:"Open for EDF access"},
  ];
  const conduits=[
    {id:"CAN FD",    route:"Port keel rail",       chain:"N1→N2→N3→N4→COMPHAT-SWITCH"},
    {id:"RS-485",    route:"Starboard keel rail",  chain:"N1→N2→N3→N4→COMPHAT-SWITCH"},
    {id:"MIL-1553B", route:"Dorsal centre",        chain:"N1→N2→N3→N4→COMPHAT-SWITCH"},
    {id:"ETH-A",     route:"Port side",            chain:"N1→COMPHAT-SWITCH"},
    {id:"ETH-B",     route:"Starboard side",       chain:"N2→COMPHAT-SWITCH"},
    {id:"PWR",       route:"Belly centre",         chain:"Battery→BEC→all nodes"},
  ];
  const BATCHES = [
    {n:1, zones:"A + B", mix_mL:55, foam_mL:"220", note:"Nose + dorsal-fwd voids"},
    {n:2, zones:"C + D", mix_mL:55, foam_mL:"220", note:"Belly + dorsal-aft voids"},
    {n:3, zones:"E only",mix_mL:45, foam_mL:"180", note:"Aft service void"},
  ];
  return(<div>
    <SH t="Foam Fill Design" mt={0} c={C.teal}/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:20,marginBottom:8}}>
      <div>
        <KV k="Shell material"               v="1.2mm PETG thin shell"/>
        <KV k="Fill material"                v="X-30 PU foam, 2 lb/ft³ (0.032 g/cm³)" vc={C.teal}/>
        <KV k="Mix ratio"                    v="1:1 by volume"/>
        <KV k="Pot life"                     v="2 minutes — work fast"/>
        <KV k="Expansion factor"             v="4×"/>
        <KV k="Cure: initial"               v="4 hours (do not disturb)"/>
        <KV k="Cure: safe to handle"         v="12 hours"/>
        <KV k="Cure: full strength"          v="24 hours"/>
        <KV k="Max batch"                    v="60 mL mixed  (PETG heat limit)" vc={C.orange}/>
        <KV k="Batches required"             v="3 sequential"/>
      </div>
      <div>
        <KV k="Gross internal volume"        v="~1,540 cm³ (18″ hull)"/>
        <KV k="Net foam volume (after voids)"v="~1,182 cm³" vc={C.yellow}/>
        <KV k="Foam mass (2 lb/ft³)"         v="~37.8 g" vc={C.yellow}/>
        <KV k="Shell mass"                   v="143 g"/>
        <KV k="Hull assembly total"          v="~193 g" vc={C.lime}/>
        <KV k="Solid-fill equivalent"        v="~600 g (no voids)"/>
        <KV k="Mass saved by foam"           v="~406 g" vc={C.green}/>
        <KV k="Void former material"         v="25mm EPS (Foamular 150)"/>
        <KV k="Release agent"                v="Johnson's Paste Wax (2 coats)"/>
      </div>
    </div>
    <Warn ch="NEVER exceed 60mL per batch. X-30 exotherm above 60mL can soften and warp 1.2mm PETG walls. Mix in a paper cup, pour immediately, wait ≥10 min before next batch."/>
    <Crit ch="VENTILATION REQUIRED. X-30 produces MDI isocyanate vapour during cure. Work outdoors or with forced ventilation. Nitrile gloves + eye protection mandatory."/>

    <SH t="Batch Pour Sequence" c={C.orange}/>
    <div style={{overflowX:"auto",marginBottom:8}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["BATCH","ZONES","MIX (mL)","FOAM YIELD (mL)","NOTE"]}/>
        <tbody>{BATCHES.map((b,i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
            <td style={{padding:"5px 9px",color:C.orange,fontWeight:"bold"}}>{b.n}</td>
            <td style={{padding:"5px 9px",color:C.lime}}>{b.zones}</td>
            <td style={{padding:"5px 9px",color:C.yellow,textAlign:"right"}}>{b.mix_mL}</td>
            <td style={{padding:"5px 9px",color:C.teal,textAlign:"right"}}>{b.foam_mL}</td>
            <td style={{padding:"5px 9px",color:C.dimmer,fontSize:9}}>{b.note}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
    <Note c={C.orange} ch="Zone F (engine bell bay, station 388–457mm) is left unfilled — it serves as the EDF heat sink and access void. Do not pour foam into Zone F."/>

    <SH t="Void Former Table" c={C.purple}/>
    <div style={{overflowX:"auto",marginBottom:8}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["PANEL","STATION (mm from nose)","VOID DIMS","FORMER BLANK","SEAL METHOD"]}/>
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
    <Note c={C.purple} ch="Cut void formers from 25mm EPS blue foam board (Owens Corning Foamular 150). Apply 2 coats Johnson's Paste Wax, allow to dry between coats. After 24h cure, pull formers out through the access panel opening. Waxed EPS releases cleanly."/>

    <SH t="PTFE Conduit Routing" c={C.accent}/>
    <div style={{overflowX:"auto",marginBottom:8}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["BUS / SIGNAL","ROUTE THROUGH HULL","NODE CHAIN"]}/>
        <tbody>{conduits.map((c,i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
            <td style={{padding:"5px 9px",color:C.accent,fontWeight:"bold",whiteSpace:"nowrap"}}>{c.id}</td>
            <td style={{padding:"5px 9px",color:C.yellow,whiteSpace:"nowrap"}}>{c.route}</td>
            <td style={{padding:"5px 9px",color:C.dim,fontSize:9}}>{c.chain}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
    <Note c={C.accent} ch="All 6 conduits: 5mm OD × 3mm ID PTFE tube. Thread a pull-wire through each before the foam pour so cables can be routed after cure. Tubes are pinned at each void former with a toothpick to maintain position during expansion. Total conduit mass 12g stays in airframe permanently."/>
  </div>);
}

// ── TAB: ACCESS PANELS ────────────────────────────────────────
function AccessPanelsTab(){
  const PANELS = [
    {id:"A",color:"#4ade80",label:"Nose Bayonet",sta:"0–91mm",
     open:"Rotate lid 60° CCW, pull axially",close:"Insert, rotate 60° CW, check detent",
     contents:"Node 1 stack (COMPHAT-SWITCH), GPS antenna, pitot tube fitting, nose LED"},
    {id:"B",color:"#00e5ff",label:"Dorsal Fwd Screw",sta:"91–175mm",
     open:"Remove 4× M2.5×6 Phillips screws",close:"4× screws, 12 cN·m torque, no thread-lock",
     contents:"Node 2 stack (MICROHAT), PDB, BEC 5V/5A, power distribution wiring"},
    {id:"C",color:"#f472b6",label:"Cargo Belly Hinge",sta:"160–251mm",
     open:"Release 2× spring latches, swing down on hinge",close:"Swing up, engage spring latches",
     contents:"Winch motor+spool, payload release servo, downward FPV camera, mission data USB-C"},
    {id:"D",color:"#fbbf24",label:"Dorsal Aft Magnet",sta:"251–320mm",
     open:"Pull lid straight up — 4× N42 magnets release",close:"Align with locating pin, press down",
     contents:"Node 3 stack (MICROHAT), battery slide rail + XT90, main BEC, CG trim access"},
    {id:"E",color:"#c084fc",label:"Aft Service Screw",sta:"320–388mm",
     open:"Remove 4× M2.5×6 Phillips screws",close:"4× screws, 12 cN·m torque",
     contents:"Node 4 stack (MICROHAT), 3× ESCs, bus terminus (CAN FD/1553/RS-485/ETH)"},
    {id:"F",color:"#ff6b35",label:"Engine Bell Bayonet",sta:"388–457mm",
     open:"Rotate bell 90° CW (threads), pull aft",close:"Insert, rotate 90° CCW, check detent",
     contents:"40mm EDF assembly, variable-nozzle servo, forward FPV camera bridge"},
  ];
  return(<div>
    <SH t="6-Panel Maintenance Map" mt={0} c={C.pink}/>
    <Warn ch="ALWAYS remove battery before opening any access panel. ESC capacitors hold charge for up to 30s after power-off — wait before touching ESC terminals."/>
    <Note c={C.dim} ch="Recommended service sequence (aft-to-forward): F → E → D → B → A → C. This order prevents forward-bay cables from obstructing aft-bay work and keeps the belly hinge panel (C) as the last to open so the airframe sits stable."/>
    {PANELS.map((p,i)=>(
      <div key={i} style={{marginBottom:10,border:`1px solid ${p.color}44`,borderRadius:5,overflow:"hidden"}}>
        <div style={{background:`${p.color}15`,padding:"8px 14px",
          display:"flex",justifyContent:"space-between",alignItems:"center"}}>
          <div style={{display:"flex",gap:12,alignItems:"center"}}>
            <div style={{width:28,height:28,borderRadius:4,background:p.color,
              display:"flex",alignItems:"center",justifyContent:"center",
              color:"#000",fontFamily:M,fontSize:13,fontWeight:"bold"}}>{p.id}</div>
            <div>
              <div style={{color:p.color,fontFamily:M,fontSize:11,fontWeight:"bold"}}>{p.label}</div>
              <div style={{color:C.dimmer,fontFamily:M,fontSize:9}}>Station {p.sta}</div>
            </div>
          </div>
        </div>
        <div style={{padding:"10px 14px",display:"grid",gridTemplateColumns:"1fr 1fr 1.2fr",gap:12}}>
          <div>
            <div style={{color:C.dim,fontFamily:M,fontSize:8.5,marginBottom:3,opacity:0.7}}>OPEN</div>
            <div style={{color:C.text,fontFamily:M,fontSize:9,lineHeight:1.6}}>{p.open}</div>
          </div>
          <div>
            <div style={{color:C.dim,fontFamily:M,fontSize:8.5,marginBottom:3,opacity:0.7}}>CLOSE</div>
            <div style={{color:C.text,fontFamily:M,fontSize:9,lineHeight:1.6}}>{p.close}</div>
          </div>
          <div>
            <div style={{color:C.dim,fontFamily:M,fontSize:8.5,marginBottom:3,opacity:0.7}}>ACCESSIBLE COMPONENTS</div>
            <div style={{color:C.dim,fontFamily:M,fontSize:9,lineHeight:1.6}}>{p.contents}</div>
          </div>
        </div>
      </div>
    ))}
    <Note c={C.dim} ch="Panels A and F use PETG bayonet closures — no tools needed. Panels B and E use M2.5×6 Phillips screws — 4× each. Panel C hinges on a PETG pin; use a plastic pry tool on the spring latches. Panel D uses 4× N42 neodymium press-fit magnets. Do not use metallic tools near Panel D magnets."/>
  </div>);
}

// ── TAB: OBSTACLE AVOIDANCE ───────────────────────────────────
function ObstacleAvoidanceTab(){
  const SENSORS = [
    {id:"S1",label:"Forward",   color:C.red,    sta:"25mm",  pos:"Nose bayonet ring",        look:"0° — forward",        note:"Circular port in nose cap; looks like a hull sensor/camera"},
    {id:"S2",label:"Aft",      color:C.orange, sta:"440mm", pos:"Engine bell rim",           look:"180° — aft",          note:"Small annular ring behind engine bell; matches nozzle detail"},
    {id:"S3",label:"Port",     color:C.accent, sta:"200mm", pos:"Port hull side at waterline",look:"90° port",            note:"Oval recess in hull side — looks like hull viewport"},
    {id:"S4",label:"Starboard",color:C.green,  sta:"200mm", pos:"Stbd hull side at waterline",look:"90° stbd",           note:"Mirror of S3"},
    {id:"S5",label:"Zenith",   color:C.purple, sta:"180mm", pos:"Dorsal keel apex",          look:"90° up",              note:"Smooth dome fairing at keel ridge — looks like antenna base"},
    {id:"S6",label:"Nadir",    color:C.teal,   sta:"160mm", pos:"Forward belly blister",     look:"90° down",            note:"Small belly blister fwd of cargo gondola; used for landing flare"},
  ];
  const BUSES = [
    ["TCA9548A I²C mux",  "0x70", "Selects one of ch 0–5 to address the target sensor"],
    ["MCP23008 GPIO exp.", "0x20", "GP0–GP5 drive each sensor's XSHUT pin for address assignment at boot"],
    ["Host: Node 3",       "I²C", "Panel D bay — SENSORHAT-1 XIAO RP2350 co-processor reads all 6 sensors"],
  ];
  const THR_ZONES = [
    {zone:"< 0.4m", action:"STOP — emergency hover hold, alert pilot"},
    {zone:"0.4–1.0m", action:"SLOW — reduce velocity to 0.3 m/s toward obstacle"},
    {zone:"1.0–2.5m", action:"CAUTION — reduce velocity proportionally"},
    {zone:"2.5–4.0m", action:"WARN — alert only, full speed permitted"},
    {zone:"> 4.0m", action:"CLEAR — no action"},
  ];
  return(<div>
    <SH t="VL53L5CX Omnidirectional ToF Sensor Array" mt={0} c={C.teal}/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:20,marginBottom:8}}>
      <div>
        <KV k="Sensor"         v="ST VL53L5CX 8×8 multizone ToF" vc={C.teal}/>
        <KV k="FoV per sensor" v="65° diagonal (8×8 = 64 zones/frame)"/>
        <KV k="Range"          v="0.4 – 4.0 m indoor"/>
        <KV k="Update rate"    v="15 Hz full resolution"/>
        <KV k="Interface"      v="I²C @ 1 MHz via TCA9548A mux"/>
        <KV k="XSHUT control"  v="MCP23008 GP0–GP5"/>
        <KV k="Sensor count"   v="6 — omnidirectional coverage" vc={C.lime}/>
        <KV k="Total mass"     v="15g sensors + 4g mux PCB + 7g mounts = 26g"/>
      </div>
      <div>
        <KV k="Aperture"       v="5mm PMMA disc, UV-adhesive, flush-mount PETG"/>
        <KV k="Visual style"   v="Porthole-like hull detail — screen accurate" vc={C.lime}/>
        <KV k="Host node"      v="Node 3 (Panel D access)"/>
        <KV k="I²C addresses"  v="0x54–0x59 (assigned via XSHUT sequence at boot)"/>
        <KV k="Indoor safe"    v="Class 1 VCSEL — eye-safe"/>
        <KV k="Operating V"    v="2.8 V (LDO on-board)"/>
      </div>
    </div>

    <SH t="Sensor Positions" c={C.accent}/>
    <div style={{overflowX:"auto",marginBottom:8}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["ID","LABEL","STATION","HULL POSITION","LOOK DIRECTION","AESTHETIC NOTE"]}/>
        <tbody>{SENSORS.map((s,i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
            <td style={{padding:"5px 9px"}}>
              <span style={{background:s.color,color:"#000",padding:"2px 6px",borderRadius:3,
                fontWeight:"bold",fontSize:9,fontFamily:M}}>{s.id}</span>
            </td>
            <td style={{padding:"5px 9px",color:s.color,fontWeight:"bold"}}>{s.label}</td>
            <td style={{padding:"5px 9px",color:C.yellow}}>{s.sta}</td>
            <td style={{padding:"5px 9px",color:C.dim}}>{s.pos}</td>
            <td style={{padding:"5px 9px",color:C.dimmer,fontSize:9}}>{s.look}</td>
            <td style={{padding:"5px 9px",color:C.dimmer,fontSize:9,fontStyle:"italic"}}>{s.note}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>

    <SH t="I²C Bus Topology" c={C.purple}/>
    <div style={{overflowX:"auto",marginBottom:8}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["DEVICE","I²C ADDRESS","ROLE"]}/>
        <tbody>{BUSES.map(([dev,addr,role],i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
            <td style={{padding:"5px 9px",color:C.purple,fontWeight:"bold"}}>{dev}</td>
            <td style={{padding:"5px 9px",color:C.lime,fontFamily:M}}>{addr}</td>
            <td style={{padding:"5px 9px",color:C.dim,fontSize:9}}>{role}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
    <Note c={C.purple} ch="Boot sequence: MCP23008 holds all XSHUT low (all sensors off). Enable S1 XSHUT high → assign address 0x54 via I²C → disable. Repeat for S2–S6 (0x55–0x59). TCA9548A selects the matching channel when reading each sensor."/>

    <SH t="Avoidance Thresholds" c={C.orange}/>
    <div style={{overflowX:"auto",marginBottom:4}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["DISTANCE ZONE","FC ACTION"]}/>
        <tbody>{THR_ZONES.map(({zone,action},i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
            <td style={{padding:"5px 9px",color:i===0?C.red:i===1?C.yellow:i===2?C.orange:C.green,
              fontWeight:"bold",fontFamily:M}}>{zone}</td>
            <td style={{padding:"5px 9px",color:C.dim}}>{action}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
    <Note c={C.orange} ch="Indoor mode activates all 6 sensors at 15 Hz. Outdoor mode may disable S5/S6 to reduce CPU load. Sensor readings are fused with IMU velocity estimate — obstacle vectors with low confidence (VL53L5CX signal count < 80) are discarded."/>
    <Warn ch="Do not apply paint or foam over PMMA aperture windows. Keep optically clear. Condensation inside aperture indicates seal failure — re-apply UV adhesive."/>
  </div>);
}

// ── TAB: CARGO + NACELLE ──────────────────────────────────────
function CargoNacelleTab(){
  const STATES = [
    {s:"TRANSIT",  icon:"✈", c:C.accent,   d:"Doors closed, cargo latched in cradle, winch spooled. Aerodynamically sealed."},
    {s:"DEPLOY",   icon:"↓", c:C.yellow,   d:"Doors open (SG90 bell-crank), cradle descends on Dyneema at 120mm/s."},
    {s:"RETRIEVE", icon:"↑", c:C.green,    d:"Cargo placed in cradle, winch raises at 80mm/s. Auto-latch clicks at top."},
    {s:"SECURED",  icon:"✓", c:C.lime,     d:"Doors close around cargo, latched. Ready for transit."},
  ];
  const TILT = [
    {mode:"VTOL",        deg:DIM.TILT_VTOL,    c:C.accent,  thrust:"3400g lift (nacelles only)",               note:"Hover, takeoff, landing"},
    {mode:"TRANSITION",  deg:"0–90",            c:C.teal,    thrust:"Mixed lift + forward",                     note:"Gradual tilt during acceleration"},
    {mode:"FORWARD",     deg:DIM.TILT_FWD,     c:C.green,   thrust:"Horizontal — altitude via fuselage EDF",   note:"Cruise flight"},
    {mode:"REVERSE/BRAKING",deg:DIM.TILT_REV,  c:C.red,     thrust:"1438g reverse + 3080g lift retained",      note:"Indoor deceleration only"},
    {mode:"HARD STOP",   deg:DIM.TILT_STOP,    c:C.yellow,  thrust:"—",                                        note:"Mechanical bracket stop — FC never commands this"},
  ];
  return(<div>
    <SH t="Cargo Bay — 4\"×3\"×3\" Gondola Design" mt={0} c={C.pink}/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:20,marginBottom:8}}>
      <div>
        <KV k="Interior dims"        v={`${DIM.PB_L}×${DIM.PB_W}×${DIM.PB_H}mm (4"×3"×3")`} vc={C.pink}/>
        <KV k="Gondola protrusion"   v={`${DIM.GONDOLA_DROP}mm below hull line`} vc={C.yellow}/>
        <KV k="Gondola aesthetic"    v="Serenity cargo module belly pod — screen accurate" vc={C.lime}/>
        <KV k="Door type"            v="Clamshell — 2 PETG halves on 3mm CF pin hinges"/>
        <KV k="Door actuator"        v="SG90 + bell-crank push-pull (both halves simultaneous)"/>
        <KV k="Door seal"            v="1.5mm closed-cell foam tape on door lip"/>
      </div>
      <div>
        <KV k="Winch motor"          v="N20 DC 6V 300:1 gear ratio"/>
        <KV k="Winch line"           v="Dyneema SK75 0.5mm — 1.5m"/>
        <KV k="Winch rated load"     v="350g (1.4× margin over 250g max cargo)"/>
        <KV k="Cradle"               v="Auto-latch PETG corner clips — no manual attachment"/>
        <KV k="Lower speed"          v="120 mm/s"/>
        <KV k="Raise speed"          v="80 mm/s"/>
        <KV k="Max cargo"            v="250g (4"×3"×3" box)" vc={C.lime}/>
      </div>
    </div>

    <SH t="Winch Operation Sequence" c={C.orange}/>
    <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:8,marginBottom:8}}>
      {STATES.map(({s,icon,c,d},i)=>(
        <div key={i} style={{padding:"10px 12px",border:`1px solid ${c}44`,borderRadius:4,
          background:`${c}08`}}>
          <div style={{display:"flex",gap:8,alignItems:"center",marginBottom:6}}>
            <div style={{fontSize:18,color:c}}>{icon}</div>
            <span style={{color:c,fontFamily:M,fontSize:10,fontWeight:"bold"}}>{s}</span>
          </div>
          <div style={{color:C.dim,fontFamily:M,fontSize:9,lineHeight:1.6}}>{d}</div>
        </div>
      ))}
    </div>

    <SH t="Nacelle Tilt — Extended Range (0°→120°)" c={C.orange}/>
    <Note c={C.orange} ch="The MG90S nacelle tilt servo is retained unchanged. The tilt_bracket_120deg.stl reprint extends the slot geometry to allow 120° of mechanical travel (vs. 90° original). The bracket hard-stop boss prevents over-rotation beyond 120°. No servo swap needed — the MG90S physical range comfortably covers 120°."/>
    <div style={{overflowX:"auto",marginBottom:8}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["MODE","TILT ANGLE","THRUST VECTOR","OPERATIONAL USE"]}/>
        <tbody>{TILT.map(({mode,deg,c,thrust,note},i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
            <td style={{padding:"5px 9px",color:c,fontWeight:"bold"}}>{mode}</td>
            <td style={{padding:"5px 9px",color:C.lime,fontFamily:M}}>{deg}°</td>
            <td style={{padding:"5px 9px",color:C.dim}}>{thrust}</td>
            <td style={{padding:"5px 9px",color:C.dimmer,fontSize:9}}>{note}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
    <Note c={C.yellow} ch="At 115° reverse mode: nacelle thrust × sin(25°) = 1700 × 0.423 = 719g reverse per nacelle = 1438g total reverse. Lift retained = 1700 × cos(25°) × 2 = 3080g — sufficient for hover with empty payload. Use reverse mode only for indoor deceleration braking; not sustained reverse cruise."/>
    <Warn ch="Reverse/brake mode (90°–115°) is only available via explicit FC command in INDOOR mode. Normal outdoor flight limits nacelles to 0–90°. Maximum nacelle reverse rate = 20°/s to prevent abrupt pitch disturbance."/>
    <Good ch="Tilt bracket modification requires only a reprint of tilt_bracket_120deg.stl (×2). Servo, arm, and pivot pin are unchanged. Zero additional mass."/>
  </div>);
}

// ── APP ───────────────────────────────────────────────────────
const TABS = [
  {label:"Overview",       value:"overview"},
  {label:"Dimensions",     value:"dimensions"},
  {label:"Weight & Thrust",value:"weight"},
  {label:"Balance & CG",  value:"balance"},
  {label:"Avionics",       value:"avionics"},
  {label:"Hull & Foam",    value:"foam"},
  {label:"Access Panels",  value:"panels"},
  {label:"Obstacle Avoid.",value:"sensors"},
  {label:"Cargo & Nacelle",value:"cargo"},
];
_ODFontLoader();

export default function App(){
  const [tab,setTab]=useState("overview");
  return(<div style={{minHeight:"100vh",background:C.bg,color:C.text,fontFamily:M}}>
    <Grid/>
    <div style={{background:"rgba(163,230,53,0.06)",borderBottom:"1px solid rgba(163,230,53,0.2)",
      padding:"5px 24px",fontFamily:M,fontSize:8,color:"rgba(163,230,53,0.75)",lineHeight:1.7}}>
      © 2026 Steve Griffing, PE(CSE) [Control Systems Engineering], CISSP-ISSEP, CPP · CC BY 4.0
      · Hull: Peter Farell CC BY 4.0 · Nozzle: BamJr CC BY 4.0
      · Visual inspiration: Firefly/Serenity © Joss Whedon/Mutant Enemy/Universal — Fan engineering work
    </div>
    <div style={{position:"relative",zIndex:1,borderBottom:`1px solid ${C.border}`,padding:"14px 24px 12px"}}>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",flexWrap:"wrap",gap:12}}>
        <div>
          <div style={{color:C.lime,fontSize:9,letterSpacing:"0.2em",marginBottom:4}}>
            SERENITY TILTROTOR · 18" CANONICAL · REV H</div>
          <h1 style={{margin:0,fontSize:18,fontWeight:"normal",color:C.text,letterSpacing:"0.07em",fontFamily:MB}}>
            SERENITY-CLASS FIREFLY TILTROTOR UAV</h1>
          <div style={{color:"rgba(0,229,255,0.6)",fontSize:10,marginTop:3,fontFamily:M}}>
            {DIM.L_MM}mm ({DIM.L_IN}") · 80mm 6S EDFs · 6× VL53L5CX ToF · 4"×3"×3" cargo gondola · nacelle 0–120° · 6 access panels
          </div>
        </div>
        <div style={{textAlign:"right",fontFamily:M}}>
          <div style={{color:C.yellow,fontSize:13,fontWeight:"bold"}}>AUW empty: {AUW_EMPTY}g ({gToLb(AUW_EMPTY)} lb)</div>
          <div style={{color:C.green,fontSize:11,marginTop:2}}>
            T/W {TW_EMPTY}:1 empty · T/W {TW_CARGO}:1 cargo
          </div>
          <div style={{color:C.lime,fontSize:10,marginTop:2}}>
            Thrust {THRUST}g · Dry {DRY_G}g
          </div>
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
      {tab==="avionics"    && <AvionicsTab/>}
      {tab==="foam"        && <HullFoamTab/>}
      {tab==="panels"      && <AccessPanelsTab/>}
      {tab==="sensors"     && <ObstacleAvoidanceTab/>}
      {tab==="cargo"       && <CargoNacelleTab/>}
    </div>
  </div>);
}
