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

// ── Canonical Rev I dimensions (QMx 269ft×170ft×79ft @ 18") — unchanged Rev J ─
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
  // Nacelle tilt range — 0° datum = longitudinal axis (forward flight)
  TILT_FWD_STOP:  -5,   // mechanical hard stop — forward limit (anti-dive)
  TILT_FWD:        0,   // 0° datum — nacelles horizontal, pure forward thrust
  TILT_VTOL:      90,   // 90° — pure VTOL hover (nacelles pointing up)
  TILT_REV:      120,   // FC soft limit — reverse / brake mode
  TILT_AFT_STOP: 140,   // mechanical hard stop — aft limit in tilt bracket
};

// ── Rev K weight budget (bom_revK.json) ──────────────────────
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
  ["XRP 3660-2700KV 80mm EDF ×4 (2 per nacelle, tandem series)", 1532],  // 383g × 4 — 2 EDFs in series per nacelle
  ["XFLY Galaxy X4 PRO 40mm 12-blade EDF (4S)",  40],
  ["120A ESC ×4 (nacelle, one per EDF, HW Platinum V4 120A)", 428],  // 107g × 4 — one per EDF, fault-tolerant pairs
  ["40A ESC ×1 (fuselage, 4S)",                15],
  ["6S→4S balance tap pigtail (cells 1–4)",     2],
  ["Nacelle pods 93.5mm OD ×2 (tandem 230mm pod)", 52],
  ["Nacelle tip caps ×2 + nav lights",         16],
  ["CF stub arms + tilt brackets ×2",          14],
  ["Nacelle tilt servos MG90S ×2",             18],
  ["Gear nozzle assemblies ×3",                12],
  ["Variable-nozzle servo SG90",                9],
  // Avionics — 8× PocketBeagle 2 + Cape-A/B (Rev K)
  ["PocketBeagle 2 ×8 (AM6232 + PRU-ICSS)",    80],  // 10g × 8
  ["Cape-A Sensor/Flight PCB ×4 (85×55mm 4L)", 112], // 28g × 4
  ["Cape-B Comms/Payload PCB ×4 (90×60mm 4L)", 152], // 38g × 4
  ["RCRS-49 sub-modules ×4",                    48],  // 12g × 4
  ["microSD ×12 (OS×8 + log×4)",                12],
  // Power + wiring
  ["PDB + BEC 5V/5A",                          30],
  ["ESC power wiring (12/16 AWG — 4 nacelle ESCs + fuselage)", 52],
  ["Servo + signal wiring",                    12],
  ["XT90 battery pigtail",                     15],
  ["Bus cables (CAN×7/RS-485×7/1553×7/ETH×8)", 25],  // ring topology — more cable runs
  ["GPS pigtails ×4 + ESC telem ×5 + misc",    22],  // 4 nacelle + 1 fuselage ESC telem
  // Payload + cargo system
  ["Payload servo + winch motor + driver",     20],
  ["Cargo gondola shell + clamshell door PETG",22],
  ["SG90 cargo door servo + bell-crank",        9],
  ["Cargo cradle + auto-latch assembly",        10],
  ["Dyneema SK75 winch line 1.5m",              1],
  ["TPU landing skids ×4",                      4],
  // Obstacle avoidance sensors — dual redundant arrays
  ["VL53L5CX ToF sensors ×6 Array-A + harness",15],
  ["TCA9548A mux-A + MCP23008 GPIO-A (PCB)",    4],
  ["Sensor PETG mounts ×6 Array-A + PMMA",      7],
  ["VL53L5CX ToF sensors ×6 Array-B + harness",15],
  ["TCA9548A mux-B + MCP23008 GPIO-B (PCB)",    4],
  ["Sensor PETG mounts ×6 Array-B + PMMA",      7],
  // Radios + sensors (×4 redundant on Cape-B / Cape-A)
  ["SiK 915MHz modules ×4 + antennas",         36],  // 6g module + 3g ant × 4
  ["LoRa 915MHz RFM95W ×4 + antennas",         20],  // 3g module + 2g ant × 4
  ["TI WL1837MOD WiFi ×4 + antennas",          12],  // 2g module + 1g ant × 4
  ["RCRS-49 sub-modules ×4 — counted in avionics", 0],
  ["GPS u-blox M10Q ×4 + patch antennas",      48],  // 12g each on Cape-A FC1–FC4
  ["WS2812C nav lights ×6",                     8],
  // Fasteners + misc
  ["Standoffs + screws + zip ties (8-node)",   24],
  ["Foam tape + cable clips",                   8],
];
const DRY_G   = W_ITEMS.reduce((s,[,g])=>s+g, 0);

// ── Power & thrust ────────────────────────────────────────────
const THRUST_NAC  = 5300;  // each nacelle — 2× 80mm 6S EDF in tandem series (~91% of 2×2900g), 168A combined
const THRUST_FUSE =  650;  // XFLY Galaxy X4 PRO 5850KV nominal 4S — 30A peak, 12-blade
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
      <text x={VW-102} y={24} textAnchor="middle" fill={C.dimmer} fontSize={7.5} fontFamily={M} letterSpacing="0.5">CANONICAL PROPORTIONS — REV I</text>
      <text x={VW-102} y={38} textAnchor="middle" fill={C.lime} fontSize={9} fontFamily={M} fontWeight="bold">18.0" × QMx 269×170×79ft</text>
      <text x={VW-102} y={50} textAnchor="middle" fill={`${C.accent}80`} fontSize={7.5} fontFamily={M}>Span/length = C2C/L = {(DIM.C2C_MM/DIM.L_MM).toFixed(3)}</text>
      <text x={VW-102} y={62} textAnchor="middle" fill={C.orange} fontSize={7.5} fontFamily={M}>80mm EDF · 6S · nacelle OD {DIM.NAC_OD}mm</text>

      <text x={VW/2} y={14} textAnchor="middle"
        fill="rgba(0,229,255,0.85)" fontSize={8} fontFamily={M} letterSpacing="2">
        TOP VIEW — CANONICAL PROPORTIONS — REV I (PB2 AVIONICS REV K)</text>
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
        REV K — 18" CANONICAL · DUAL 80mm 6S SERIES EDFs PER NACELLE · 8× PocketBeagle 2 · FOAM-FILLED HULL
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
          <KV k="Nacelle EDFs (2+2)"        v={`2× 80mm 6S series per nacelle · ${THRUST_NAC}g/nacelle`} vc={C.orange}/>
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
        <SH t="What changed Rev J → Rev K" mt={0} c={C.orange}/>
        <Note c={C.orange} ch="Avionics redesigned: 4-node CM4/CM3+ mixed architecture replaced by 8× PocketBeagle 2 (AM6232) in two cooperative groups — 4× FC nodes (Cape-A) + 4× CN nodes (Cape-B). All 4 nodes are peer equals; role elected via CAN FD heartbeat priority voting at boot. +293g avionics mass (148g→441g)."/>
        <Note c={C.teal} ch="Cape-A (Sensor/Flight): ICM-42688-P IMU, BMP388 baro, M10Q GPS, ATA6561 CAN FD, MAX3485E RS-485, PRU-native 1553 Manchester II (no HI-6130), DP83825I×2 Ethernet PHY, SLB9670 TPM2, 8×PWM servo rail. One per FC node."/>
        <Note c={C.purple} ch="Cape-B (Comms/Payload): SiK 915MHz, RFM95W LoRa, TI WL1837MOD WiFi/BT, RCRS-49 sub-module header. All 4 radio links on every Cape-B — software-elected masters. ATF16V8BQL CPLD hardware write-block on log microSD (non-executable, append-only). SLB9670 TPM2 on each Cape-B. DRV8833 winch, HX711 load cell, cargo servo PWM."/>
        <Note c={C.lime} ch="Ethernet topology: 8-node ring using CPSW3G + DP83825I PHY (100BASE-TX per link). CAN FD / RS-485: linear bus FC1→FC2→FC3→FC4→CN1→CN2→CN3→CN4 (7 cables, 120Ω at FC1 and CN4). 1553: same linear bus, PRU Manchester II, stub transformers per node."/>
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
    {item:"Nacelles (both, effective sta)",   g:1350, sta:167},  // 4 EDFs + 4 ESCs + pods + arms
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
  const FC_NODES = [
    {id:"FC1",cape:"Cape-A",zone:"Bay A (nose)",
     role:"Primary FC · 1553 BC · CAN FD BC · GNSS primary",
     sensors:"ICM-42688-P · BMP388 · M10Q GPS · MS4525DO airspeed"},
    {id:"FC2",cape:"Cape-A",zone:"Bay A (nose)",
     role:"Navigation · OA Array-B master · standby 1553 BC",
     sensors:"ICM-42688-P · BMP388 · M10Q GPS · VL53L5CX Array-B"},
    {id:"FC3",cape:"Cape-A",zone:"Bay B (dorsal fwd)",
     role:"OA Array-A master · payload sensors · ESC telemetry",
     sensors:"ICM-42688-P · BMP388 · M10Q GPS · VL53L5CX Array-A"},
    {id:"FC4",cape:"Cape-A",zone:"Bay B (dorsal fwd)",
     role:"Actuator control · tilt servos · nozzle · nav lights",
     sensors:"ICM-42688-P · BMP388 · M10Q GPS"},
  ];
  const CN_NODES = [
    {id:"CN1",cape:"Cape-B",zone:"Bay D (dorsal aft)",
     role:"SiK 915MHz master · primary log writer",
     radios:"SiK ★ · LoRa · WiFi · RCRS-49"},
    {id:"CN2",cape:"Cape-B",zone:"Bay D (dorsal aft)",
     role:"LoRa 915MHz master · secondary log · cargo backup",
     radios:"SiK · LoRa ★ · WiFi · RCRS-49"},
    {id:"CN3",cape:"Cape-B",zone:"Bay E (aft)",
     role:"RCRS 49MHz master · cargo primary (winch/doors)",
     radios:"SiK · LoRa · WiFi · RCRS-49 ★"},
    {id:"CN4",cape:"Cape-B",zone:"Bay E (aft)",
     role:"WiFi/BT master · cargo backup · log tertiary",
     radios:"SiK · LoRa · WiFi ★ · RCRS-49"},
  ];
  const BUSES = [
    {bus:"CAN FD",spec:"5 Mbit/s · AM6232 MCAN native · ATA6561 · ISO 11898-1:2015",purpose:"Role election heartbeats, sensor state, real-time control, 1ms cycle"},
    {bus:"Ethernet",spec:"100BASE-T ring · CPSW3G + DP83825I × 2/node · RSTP",purpose:"Bulk telemetry, OTA, video, MAVLink passthrough"},
    {bus:"RS-485",spec:"Half-duplex · 4 Mbit/s · MAX3485E · linear bus",purpose:"ESC config/telemetry, secondary sensor bus, bootloader"},
    {bus:"MIL-STD-1553B",spec:"1 Mbit/s · PRU Manchester II · DS26LV31/32 + PE-68515 · 78Ω",purpose:"Safety-critical C2, redundant flight commands — no HI-6130"},
    {bus:"PWR",spec:"6S → 5V/5A BEC × 2 (FC group + CN group) → all nodes",purpose:"Redundant power rails; FC and CN groups on separate BECs"},
  ];
  return(<div>
    <SH t="Rev K — 8× PocketBeagle 2 · Cape-A (FC) + Cape-B (CN)" mt={0} c={C.teal}/>
    <Note c={C.teal} ch="All 8 nodes identical SoC: AM6232 dual A53 + M4F + PRU-ICSS, 512MB LPDDR4. Role is elected at boot via CAN FD priority arbitration — no hardwired primaries. All roles are hot-standby on any surviving node. PRU-ICSS replaces RP2350 for real-time tasks; native MCAN replaces MCP2518FD; PRU Manchester II replaces HI-6130."/>
    <div style={{marginBottom:8}}>
      <div style={{color:C.accent,fontFamily:M,fontSize:10,fontWeight:"bold",marginBottom:6}}>FC NODES — Cape-A (Sensor + Flight Control)</div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr 1fr 1fr",gap:6,marginBottom:10}}>
        {FC_NODES.map((n,i)=>(
          <div key={i} style={{padding:"8px 10px",border:`1px solid ${C.teal}44`,borderRadius:4,background:"rgba(45,212,191,0.03)"}}>
            <div style={{color:C.teal,fontFamily:M,fontSize:11,fontWeight:"bold",marginBottom:3}}>{n.id} <span style={{color:C.yellow,fontSize:8}}>{n.cape}</span></div>
            <div style={{color:C.dimmer,fontFamily:M,fontSize:7.5,marginBottom:3}}>{n.zone}</div>
            <div style={{color:C.lime,fontFamily:M,fontSize:8,marginBottom:3}}>{n.role}</div>
            <div style={{color:C.dim,fontFamily:M,fontSize:7.5}}>{n.sensors}</div>
          </div>
        ))}
      </div>
      <div style={{color:C.purple,fontFamily:M,fontSize:10,fontWeight:"bold",marginBottom:6}}>CN NODES — Cape-B (Comms + Logging + Payload) · ★ = elected primary</div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr 1fr 1fr",gap:6}}>
        {CN_NODES.map((n,i)=>(
          <div key={i} style={{padding:"8px 10px",border:`1px solid ${C.purple}44`,borderRadius:4,background:"rgba(192,132,252,0.03)"}}>
            <div style={{color:C.purple,fontFamily:M,fontSize:11,fontWeight:"bold",marginBottom:3}}>{n.id} <span style={{color:C.yellow,fontSize:8}}>{n.cape}</span></div>
            <div style={{color:C.dimmer,fontFamily:M,fontSize:7.5,marginBottom:3}}>{n.zone}</div>
            <div style={{color:C.lime,fontFamily:M,fontSize:8,marginBottom:3}}>{n.role}</div>
            <div style={{color:C.dim,fontFamily:M,fontSize:7.5}}>{n.radios}</div>
          </div>
        ))}
      </div>
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
        <SH t="PCB Stack Masses — Rev K" mt={0} c={C.purple}/>
        <KV k="PocketBeagle 2 ×8"          v="8 × 10g = 80g"/>
        <KV k="Cape-A ×4 (85×55mm 4L)"    v="4 × 28g = 112g" vc={C.teal}/>
        <KV k="Cape-B ×4 (90×60mm 4L)"    v="4 × 38g = 152g" vc={C.purple}/>
        <KV k="RCRS-49 sub-modules ×4"    v="4 × 12g = 48g"/>
        <KV k="microSD ×12 (OS×8 + log×4)"v="12 × 1g = 12g"/>
        <KV k="TOTAL avionics stack"       v="404g" vc={C.lime}/>
        <Note c={C.yellow} ch="+256g vs RevJ 148g. T/W remains ≥2.37 in all configs."/>
      </div>
      <div>
        <SH t="Cape-A / Cape-B shared bus section" mt={0} c={C.pink}/>
        <KV k="ATA6561 CAN FD"     v="All 8 nodes · 5Mbit/s · native MCAN"/>
        <KV k="MAX3485E RS-485"    v="All 8 nodes · 4Mbit/s · half-duplex"/>
        <KV k="PRU 1553 + DS26LV31/32" v="All 8 nodes · PRU Manchester II · no HI-6130"/>
        <KV k="DP83825I × 2 ETH"  v="All 8 nodes · 100BASE-TX · CPSW3G ring"/>
        <KV k="SLB9670 TPM 2.0"   v="All 8 nodes (both cape variants) · SPI"/>
        <KV k="ATF16V8BQL CPLD"    v="Cape-B only · microSD write-block latch" vc={C.orange}/>
        <KV k="ICM-42688-P IMU"    v="Cape-A only · 6-DOF · ±16g / ±2000°/s"/>
        <KV k="BMP388 baro"        v="Cape-A only · ±0.5m · 200Hz"/>
        <KV k="M10Q GPS"           v="Cape-A only · 4-constellation L1"/>
        <KV k="Cape-A stack size"  v="85 × 55 × 35 mm" vc={C.teal}/>
        <KV k="Cape-B stack size"  v="90 × 60 × 35 mm" vc={C.purple}/>
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
    {id:"CAN FD",    route:"Port keel rail",       chain:"FC1→FC2→FC3→FC4→CN1→CN2→CN3→CN4 (linear, 120Ω ends)"},
    {id:"RS-485",    route:"Starboard keel rail",  chain:"FC1→FC2→FC3→FC4→CN1→CN2→CN3→CN4 (linear, 120Ω ends)"},
    {id:"MIL-1553B", route:"Dorsal centre",        chain:"FC1→FC2→FC3→FC4→CN1→CN2→CN3→CN4 (78Ω ends, stub xfmrs)"},
    {id:"ETH-A/B",   route:"Port + stbd sides",    chain:"8-node ring: FC1↔FC2↔FC3↔FC4↔CN1↔CN2↔CN3↔CN4↔FC1"},
    {id:"PWR-FC",    route:"Belly centre fwd",     chain:"Battery→BEC-1→FC1+FC2+FC3+FC4"},
    {id:"PWR-CN",    route:"Belly centre aft",     chain:"Battery→BEC-2→CN1+CN2+CN3+CN4"},
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
     contents:"Node 1 stack (COMMS-HAT-SWITCH), GPS antenna, pitot tube fitting, nose LED"},
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
    <Note c={C.dim} ch="Panels A and F use PETG bayonet closures — no tools needed. Panels B and E use M2.5×6 Phillips screws — 4× each. Panel C hinges on a PETG pin; use a plastic pry tool on the spring latches. Panel D uses 4× N42 neodymium press-fit magnets. Do not use metallic tools near Panel D magnets. Panel B bay: Array-B TCA9548A+MCP23008 PCB and Node 2 I²C2 harness. Panel D bay: Array-A TCA9548A+MCP23008 PCB and Node 3 I²C3 harness."/>
  </div>);
}

// ── TAB: OBSTACLE AVOIDANCE ───────────────────────────────────
function ObstacleAvoidanceTab(){
  const SENSORS_A = [
    {id:"S1A",label:"Forward",   color:C.red,    sta:"25mm",  pos:"Nose bayonet ring",          look:"0° — forward",  note:"Circular port in nose cap"},
    {id:"S2A",label:"Aft",       color:C.orange, sta:"440mm", pos:"Engine bell rim",             look:"180° — aft",    note:"Annular ring behind engine bell"},
    {id:"S3A",label:"Port",      color:C.accent, sta:"200mm", pos:"Port hull side at waterline", look:"90° port",      note:"Oval recess in hull side"},
    {id:"S4A",label:"Starboard", color:C.green,  sta:"200mm", pos:"Stbd hull side at waterline", look:"90° stbd",      note:"Mirror of S3A"},
    {id:"S5A",label:"Zenith",    color:C.purple, sta:"180mm", pos:"Dorsal keel apex",            look:"90° up",        note:"Smooth dome fairing"},
    {id:"S6A",label:"Nadir",     color:C.teal,   sta:"160mm", pos:"Forward belly blister",       look:"90° down",      note:"Belly blister fwd of cargo gondola"},
  ];
  const SENSORS_B = [
    {id:"S1B",label:"Forward",   color:C.red,    sta:"40mm",  pos:"Nose ring aft of S1A",        look:"0° — forward",  note:"Second fwd sensor ~15mm aft of S1A"},
    {id:"S2B",label:"Aft",       color:C.orange, sta:"425mm", pos:"Engine bell fore of S2A",     look:"180° — aft",    note:"Second aft sensor ~15mm fwd of S2A"},
    {id:"S3B",label:"Port",      color:C.accent, sta:"150mm", pos:"Port hull, fwd of S3A",       look:"90° port",      note:"50mm fwd of S3A — different axial blind spot"},
    {id:"S4B",label:"Starboard", color:C.green,  sta:"150mm", pos:"Stbd hull, fwd of S4A",       look:"90° stbd",      note:"Mirror of S3B"},
    {id:"S5B",label:"Zenith",    color:C.purple, sta:"260mm", pos:"Dorsal keel, aft of S5A",     look:"90° up",        note:"80mm aft of S5A — different zenith profile"},
    {id:"S6B",label:"Nadir",     color:C.teal,   sta:"220mm", pos:"Belly, aft of S6A",           look:"90° down",      note:"60mm aft of S6A — different nadir profile"},
  ];
  const BUSES_A = [
    ["TCA9548A-A",    "0x70", "Node 3 I²C3 — ch 0–5 for S1A–S6A"],
    ["MCP23008-A",    "0x20", "Node 3 I²C3 — GP0–GP5 → XSHUT S1A–S6A"],
    ["Host: Node 3",  "I²C3", "CM3-CARRIER-1 Panel D bay — Array A primary"],
  ];
  const BUSES_B = [
    ["TCA9548A-B",    "0x70", "Node 2 I²C2 — ch 0–5 for S1B–S6B"],
    ["MCP23008-B",    "0x20", "Node 2 I²C2 — GP0–GP5 → XSHUT S1B–S6B"],
    ["Host: Node 2",  "I²C2", "CM3-CARRIER-1 Panel B bay — Array B primary"],
  ];
  const REDUNDANCY = [
    {dir:"Forward",   a:"S1A sta 25mm",  b:"S1B sta 40mm"},
    {dir:"Aft",       a:"S2A sta 440mm", b:"S2B sta 425mm"},
    {dir:"Port",      a:"S3A sta 200mm", b:"S3B sta 150mm"},
    {dir:"Starboard", a:"S4A sta 200mm", b:"S4B sta 150mm"},
    {dir:"Zenith",    a:"S5A sta 180mm", b:"S5B sta 260mm"},
    {dir:"Nadir",     a:"S6A sta 160mm", b:"S6B sta 220mm"},
  ];
  const THR_ZONES = [
    {zone:"< 0.4m",   action:"STOP — emergency hover hold, alert pilot"},
    {zone:"0.4–1.0m", action:"SLOW — reduce velocity to 0.3 m/s toward obstacle"},
    {zone:"1.0–2.5m", action:"CAUTION — reduce velocity proportionally"},
    {zone:"2.5–4.0m", action:"WARN — alert only, full speed permitted"},
    {zone:"> 4.0m",   action:"CLEAR — no action"},
  ];
  const SensorTable = ({sensors, title, node, color}) => (
    <div style={{marginBottom:8}}>
      <div style={{background:color,padding:"4px 10px",borderRadius:"3px 3px 0 0",
        color:"#fff",fontFamily:M,fontSize:9,fontWeight:"bold",letterSpacing:"0.08em"}}>
        {title} — {node}
      </div>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:9}}>
        <TH cols={["ID","DIR","STATION","POSITION","LOOK","NOTE"]}/>
        <tbody>{sensors.map((s,i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
            <td style={{padding:"4px 8px"}}>
              <span style={{background:s.color,color:"#000",padding:"1px 5px",borderRadius:3,
                fontWeight:"bold",fontSize:8,fontFamily:M}}>{s.id}</span>
            </td>
            <td style={{padding:"4px 8px",color:s.color,fontWeight:"bold"}}>{s.label}</td>
            <td style={{padding:"4px 8px",color:C.yellow}}>{s.sta}</td>
            <td style={{padding:"4px 8px",color:C.dim}}>{s.pos}</td>
            <td style={{padding:"4px 8px",color:C.dimmer,fontSize:8}}>{s.look}</td>
            <td style={{padding:"4px 8px",color:C.dimmer,fontSize:8,fontStyle:"italic"}}>{s.note}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
  );
  return(<div>
    <SH t="Dual Redundant VL53L5CX Obstacle Avoidance — 12 Sensors" mt={0} c={C.teal}/>
    <div style={{background:`${C.teal}18`,border:`1px solid ${C.teal}44`,borderRadius:4,padding:"8px 14px",marginBottom:12}}>
      <div style={{color:C.lime,fontFamily:M,fontSize:10,fontWeight:"bold",marginBottom:4}}>REDUNDANCY DESIGN</div>
      <div style={{color:C.dim,fontSize:9}}>Two fully independent 6-sensor arrays on separate nodes and separate I²C buses.
        Each array alone provides complete omnidirectional coverage (all 6 axes).
        Single-node failure leaves the other array active with no coverage gap.
        Spatial offset between A/B sensors provides different axial blind-spot profiles.
      </div>
    </div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:20,marginBottom:8}}>
      <div>
        <KV k="Sensor"         v="ST VL53L5CX 8×8 multizone ToF" vc={C.teal}/>
        <KV k="FoV per sensor" v="65° diagonal (8×8 = 64 zones/frame)"/>
        <KV k="Range"          v="0.4 – 4.0 m indoor"/>
        <KV k="Update rate"    v="15 Hz full resolution"/>
        <KV k="Total sensors"  v="12 (6 Array-A + 6 Array-B)" vc={C.lime}/>
        <KV k="Array-A mass"   v="15g sensors + 4g PCB + 7g mounts = 26g"/>
        <KV k="Array-B mass"   v="15g sensors + 4g PCB + 7g mounts = 26g"/>
      </div>
      <div>
        <KV k="Array-A host"   v="Node 3 I²C3 (Panel D)" vc={C.accent}/>
        <KV k="Array-B host"   v="Node 2 I²C2 (Panel B)" vc={C.green}/>
        <KV k="I²C addresses"  v="0x54–0x59 (per bus, independently assigned)"/>
        <KV k="Aperture"       v="5mm PMMA disc, UV-adhesive, flush-mount PETG"/>
        <KV k="Visual style"   v="Porthole-like hull detail — screen accurate" vc={C.lime}/>
        <KV k="Indoor safe"    v="Class 1 VCSEL — eye-safe"/>
      </div>
    </div>

    <SH t="Array A — Sensor Positions (Node 3, Panel D)" c={C.accent}/>
    <SensorTable sensors={SENSORS_A} title="ARRAY A" node="Node 3 · I²C3 · Panel D bay" color={C.accent}/>

    <SH t="Array B — Sensor Positions (Node 2, Panel B)" c={C.green}/>
    <SensorTable sensors={SENSORS_B} title="ARRAY B" node="Node 2 · I²C2 · Panel B bay" color={C.green}/>

    <SH t="Coverage Redundancy Matrix" c={C.yellow}/>
    <div style={{overflowX:"auto",marginBottom:8}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:9}}>
        <TH cols={["DIRECTION","ARRAY A (Node 3)","ARRAY B (Node 2)","FAIL-NODE-3","FAIL-NODE-2"]}/>
        <tbody>{REDUNDANCY.map(({dir,a,b},i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
            <td style={{padding:"4px 9px",color:C.text,fontWeight:"bold"}}>{dir}</td>
            <td style={{padding:"4px 9px",color:C.accent,fontFamily:M}}>{a}</td>
            <td style={{padding:"4px 9px",color:C.green,fontFamily:M}}>{b}</td>
            <td style={{padding:"4px 9px",color:C.lime,fontSize:8}}>Array B covers ✓</td>
            <td style={{padding:"4px 9px",color:C.lime,fontSize:8}}>Array A covers ✓</td>
          </tr>
        ))}</tbody>
      </table>
    </div>

    <SH t="I²C Bus Topology — Array A (Node 3)" c={C.accent}/>
    <div style={{overflowX:"auto",marginBottom:4}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["DEVICE","I²C ADDRESS","ROLE"]}/>
        <tbody>{BUSES_A.map(([dev,addr,role],i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
            <td style={{padding:"5px 9px",color:C.accent,fontWeight:"bold"}}>{dev}</td>
            <td style={{padding:"5px 9px",color:C.lime,fontFamily:M}}>{addr}</td>
            <td style={{padding:"5px 9px",color:C.dim,fontSize:9}}>{role}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>

    <SH t="I²C Bus Topology — Array B (Node 2)" c={C.green}/>
    <div style={{overflowX:"auto",marginBottom:8}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["DEVICE","I²C ADDRESS","ROLE"]}/>
        <tbody>{BUSES_B.map(([dev,addr,role],i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
            <td style={{padding:"5px 9px",color:C.green,fontWeight:"bold"}}>{dev}</td>
            <td style={{padding:"5px 9px",color:C.lime,fontFamily:M}}>{addr}</td>
            <td style={{padding:"5px 9px",color:C.dim,fontSize:9}}>{role}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
    <Note c={C.purple} ch="Boot sequence (per array): MCP23008 holds all XSHUT low. Enable XSHUT[0] → assign 0x54 → disable. Repeat for 0x55–0x59. Arrays A and B each run this sequence independently on their own bus — address collision is impossible since the buses are electrically isolated."/>

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
    <Note c={C.orange} ch="FC fuses readings from both arrays. If a sensor on one array returns invalid data, the paired sensor on the other array (same direction, different station) maintains protection. Indoor mode: all 12 sensors at 15 Hz. Outdoor: S5/S6 on both arrays may be throttled to reduce CPU load."/>
    <Warn ch="Do NOT merge Array A and Array B onto the same I²C bus — this defeats the redundancy. Route harnesses through separate conduits. Do not obstruct PMMA apertures with paint, foam, or tape."/>
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
    {mode:"FWD HARD STOP",      deg:DIM.TILT_FWD_STOP,  c:C.yellow, thrust:"—",                                            note:"Bracket boss fwd limit — FC never commands"},
    {mode:"FORWARD",            deg:DIM.TILT_FWD,       c:C.green,  thrust:"5800g fwd (nacelles) + 650g fuse = 6450g",     note:"Cruise — altitude by fuselage EDF only"},
    {mode:"TRANSITION",         deg:"0→90",              c:C.teal,   thrust:"Mixed fwd + lift",                             note:"Gradual tilt during accel / decel"},
    {mode:"VTOL",               deg:DIM.TILT_VTOL,      c:C.accent, thrust:"5800g lift (nacelles) + 650g fuse lift",       note:"Hover, takeoff, landing"},
    {mode:"REVERSE / BRAKE",    deg:DIM.TILT_REV,       c:C.red,    thrust:"2900g reverse + 5024g lift retained",          note:"BRAKE mode only — indoor deceleration"},
    {mode:"AFT HARD STOP",      deg:DIM.TILT_AFT_STOP,  c:C.orange, thrust:"—",                                            note:"Bracket boss aft limit — FC never commands"},
  ];
  return(<div>
    <SH t="Cargo Bay — 4×3×3 in Gondola Design" mt={0} c={C.pink}/>
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
        <KV k="Max cargo"            v="250g (4×3×3 in box)" vc={C.lime}/>
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

    <SH t="Nacelle Tilt — −5° to 140° (Longitudinal Axis Datum)" c={C.orange}/>
    <Note c={C.orange} ch="Datum corrected: 0° = nacelles aligned with longitudinal axis (forward flight). 90° = VTOL hover. FC soft limits: outdoor 0°–90°; BRAKE mode 0°–120°. Hard stops: −5° forward boss (anti-dive), 140° aft boss. MG90S servo retained — reprint tilt_bracket_140deg.stl (×2) with dual stop bosses. No servo or arm change."/>
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
    <Note c={C.yellow} ch="At 120° (BRAKE soft limit): 30° past VTOL. Reverse = 2900×sin(30°)×2 = 2900g aft. Lift retained = 2900×cos(30°)×2 = 5024g — exceeds hover requirement with full payload. At 140° hard stop: reverse = 2900×sin(50°)×2 = 4443g, lift = 2900×cos(50°)×2 = 3731g (structural limit only; FC never commands)."/>
    <Warn ch="BRAKE mode (0°–120° range) available only via explicit FC INDOOR_BRAKE command. Outdoor FC soft-limits nacelles to 0°–90°. Maximum tilt rate: 20°/s in BRAKE mode; 10°/s during normal transition."/>
    <Good ch="Tilt bracket modification: reprint tilt_bracket_140deg.stl (×2). Dual stop bosses at −5° and 140°. Existing MG90S servo, arm, and pivot pin unchanged. Zero additional mass."/>
  </div>);
}

// ── TAB: DUAL-EDF NACELLE ─────────────────────────────────────
const DUAL_EDF_MODES = [
  {mode:"NOMINAL",         c:"#4ade80", edfs:"FWD ✔  AFT ✔", thrust:`${THRUST_NAC}g`,     note:"Both EDFs running — full nacelle thrust. FWD+AFT throttle matched by FC governor."},
  {mode:"FWD FAULT",       c:"#ffe600", edfs:"FWD ✖  AFT ✔", thrust:"~2900g (55%)",        note:"Forward EDF/ESC failed. Aft EDF continues. FC detects via zero RPM telemetry; trims opposite nacelle −10°, increases AFT throttle."},
  {mode:"AFT FAULT",       c:"#ffe600", edfs:"FWD ✔  AFT ✖", thrust:"~2900g (55%)",        note:"Aft EDF/ESC failed. Forward EDF continues. Same trim response as FWD FAULT. T/W ≥2.0 retained."},
  {mode:"BOTH FAULT",      c:"#f87171", edfs:"FWD ✖  AFT ✖", thrust:"0g (nacelle dead)",   note:"Full nacelle loss. Remaining nacelle: 5300g + fuselage 650g = 5950g vs AUW ~3627g — T/W 1.64 — controlled descent."},
];
const DUAL_EDF_TELEM = [
  ["RPM delta (FWD vs AFT)", "BDSHOT both channels", ">500 RPM delta at matched throttle → bearing wear alert"],
  ["Current imbalance",      "BLHeli32/AM32 UART ×4", ">15A delta at matched command → coil fault flag"],
  ["Temperature (per ESC)",  "BLHeli32/AM32 UART ×4", ">95°C either ESC → throttle derate; >110°C → single-EDF mode"],
  ["Voltage (per ESC)",      "BLHeli32/AM32 UART ×4", "Cell sag >0.3V delta → BEC or wiring fault"],
  ["ESC Status flags",       "BLHeli32/AM32 UART ×4", "desync / overcurrent / overtemp flags → fault latch + NOTIFY"],
];
const NACELLE_SERIES_NOTES = [
  {title:"Series fan staging", text:"Two 80mm EDFs in axial series within a single 230mm pod. The forward EDF (FWD) acts as the low-pressure stage; the aft EDF (AFT) as the high-pressure booster. Series staging increases total pressure ratio across the duct. Combined thrust ≈91% of arithmetic sum (5300g vs 5800g) due to inlet recirculation losses between stages. Both fans spin at the same commanded RPM; FC governor trims independently."},
  {title:"Nacelle pod length", text:"Dual-EDF tandem pod is 230mm long (vs 144mm single). OD unchanged at 93.5mm — canonical nacelle silhouette preserved. EDF-to-EDF axial gap: 20mm with flow-straightener printed vane set (6 vanes, 8mm chord). Print nacelle_pod_dual_80mm.stl."},
  {title:"ESC placement", text:"Each nacelle carries two ESCs: one mounted on the forward face of the inter-EDF bulkhead (ESC-FWD, 107g) and one on the aft face (ESC-AFT, 107g). Phase leads are 80mm long. Total nacelle ESC mass: 214g per nacelle, 428g total for both nacelles."},
  {title:"Independent power buses", text:"FWD and AFT ESCs within each nacelle draw from the same 6S main battery but through independent XT30 pigtails soldered at the PDB. A short circuit on one ESC cannot take down the other. PDB fuses: 100A per nacelle ESC pair (two 100A poly fuses per nacelle)."},
  {title:"Throttle governor", text:"FC governor maintains matched RPM between FWD and AFT EDFs within each nacelle under normal conditions (PID loop, setpoint = BDSHOT RPM FWD). On fault detection, governor isolates the failed ESC (DSHOT disarmed), ramps surviving EDF to compensate. Response time <50ms (3 consecutive telemetry failures at 10Hz)."},
  {title:"Fault latch + recovery", text:"Faults are latched per-ESC. Recovery requires ground power cycle + GCS acknowledgment. No in-flight ESC reset — prevents oscillatory fault/recovery during maneuvers. GCS telemetry downlinks fault code, affected ESC ID, last good RPM, temperature, and flight phase at fault."},
];
function DualEDFNacelleTab(){
  return(<div>
    <div style={{background:"rgba(255,107,53,0.07)",border:"1px solid rgba(255,107,53,0.35)",
      borderRadius:6,padding:"14px 18px",marginBottom:18}}>
      <div style={{color:C.orange,fontFamily:M,fontSize:12,fontWeight:"bold",marginBottom:8,letterSpacing:"0.07em"}}>
        DUAL 80mm EDF TANDEM SERIES — PER-NACELLE FAULT TOLERANCE
      </div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:18}}>
        <div>
          <KV k="EDFs per nacelle"       v="2× XRP 3660-2700KV 80mm 6S (FWD + AFT)" vc={C.orange}/>
          <KV k="Pod length"             v="230mm (vs 144mm single-EDF)" vc={C.yellow}/>
          <KV k="Pod OD"                 v="93.5mm — unchanged" vc={C.lime}/>
          <KV k="Inter-EDF gap"          v="20mm · flow-straightener vane set"/>
          <KV k="Nacelle thrust (nom.)"  v={`${THRUST_NAC}g (both EDFs) · ~2900g (single)`} vc={C.green}/>
          <KV k="ESCs per nacelle"       v="2× Hobbywing Platinum V4 120A" vc={C.teal}/>
          <KV k="ESC telemetry"          v="BLHeli32/AM32 UART 115200 · 10Hz per ESC"/>
          <KV k="ESC DSHOT"              v="BDSHOT on 4× independent PIO state machines"/>
        </div>
        <div>
          <KV k="Total nacelle ESCs"     v="4 (2 per nacelle)" vc={C.accent}/>
          <KV k="Total nacelle EDFs"     v="4 (2 per nacelle)" vc={C.accent}/>
          <KV k="Nacelle ESC mass"       v="4 × 107g = 428g"/>
          <KV k="Nacelle EDF mass"       v="4 × 383g = 1532g"/>
          <KV k="Overall total thrust"   v={`${THRUST}g (${(THRUST/453.592).toFixed(2)} lb)`} vc={C.green}/>
          <KV k="T/W empty"              v={`${TW_EMPTY}:1`} vc={parseFloat(TW_EMPTY)>=2.0?C.green:C.red}/>
          <KV k="Fault T/W (1 EDF dead)" v={`${(THRUST/(DRY_G+BAT_EMPTY)).toFixed(2)}:1 → ${((THRUST_NAC+THRUST_FUSE+THRUST_NAC*0.55)/(DRY_G+BAT_EMPTY)).toFixed(2)}:1`} vc={C.yellow}/>
          <KV k="Fault T/W (1 nac dead)" v={`${((THRUST_NAC+THRUST_FUSE)/(DRY_G+BAT_EMPTY)).toFixed(2)}:1`} vc={C.yellow}/>
        </div>
      </div>
    </div>

    <SH t="Fault Tolerance Matrix" mt={0} c={C.orange}/>
    <div style={{overflowX:"auto",marginBottom:18}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["CONDITION","EDF STATUS","NACELLE THRUST","FC RESPONSE"]}/>
        <tbody>{DUAL_EDF_MODES.map((r,i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
            <td style={{padding:"6px 9px",color:r.c,fontWeight:"bold",whiteSpace:"nowrap"}}>{r.mode}</td>
            <td style={{padding:"6px 9px",color:C.text,fontFamily:"'Courier New',monospace",fontSize:10}}>{r.edfs}</td>
            <td style={{padding:"6px 9px",color:r.c,fontWeight:"bold",whiteSpace:"nowrap"}}>{r.thrust}</td>
            <td style={{padding:"6px 9px",color:C.dim,fontSize:9,lineHeight:1.5}}>{r.note}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>

    <SH t="ESC Telemetry — Fault Detection Channels" c={C.teal}/>
    <div style={{overflowX:"auto",marginBottom:18}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["PARAMETER","SOURCE","FAULT TRIGGER"]}/>
        <tbody>{DUAL_EDF_TELEM.map((r,i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
            <td style={{padding:"5px 9px",color:C.accent,fontWeight:"bold"}}>{r[0]}</td>
            <td style={{padding:"5px 9px",color:C.teal}}>{r[1]}</td>
            <td style={{padding:"5px 9px",color:C.yellow,fontSize:9}}>{r[2]}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>

    <SH t="Design Notes" c={C.lime}/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:16}}>
      {NACELLE_SERIES_NOTES.map(({title,text},i)=>(
        <div key={i} style={{padding:"10px 13px",border:`1px solid ${C.lime}22`,borderRadius:4,background:"rgba(163,230,53,0.02)"}}>
          <div style={{color:C.lime,fontFamily:M,fontSize:10,fontWeight:"bold",marginBottom:5}}>{title}</div>
          <div style={{color:C.dim,fontFamily:M,fontSize:9,lineHeight:1.7}}>{text}</div>
        </div>
      ))}
    </div>

    <SH t="ESC Telemetry Wiring — 4 Nacelle ESCs" c={C.purple}/>
    <div style={{overflowX:"auto",marginBottom:8}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["ESC ID","NACELLE","POSITION","DSHOT GPIO","TELEM UART MUX STATE","PHASE LEADS"]}/>
        <tbody>{[
          ["ESC-NAC-L-FWD","Port (L)","Forward",   "PRU DSHOT0","MUX 000","14AWG 80mm × 3-phase"],
          ["ESC-NAC-L-AFT","Port (L)","Aft",        "PRU DSHOT1","MUX 001","14AWG 80mm × 3-phase"],
          ["ESC-NAC-R-FWD","Stbd (R)","Forward",   "PRU DSHOT2","MUX 010","14AWG 80mm × 3-phase"],
          ["ESC-NAC-R-AFT","Stbd (R)","Aft",        "PRU DSHOT3","MUX 011","14AWG 80mm × 3-phase"],
          ["ESC-FUSE",     "Fuselage","Aft bay",    "PRU DSHOT4","MUX 100","16AWG 150mm × 3-phase"],
        ].map((r,i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
            {r.map((v,j)=>(
              <td key={j} style={{padding:"5px 9px",
                color:j===0?C.yellow:j===3?C.orange:j===4?C.teal:C.dim,
                fontFamily:j===3||j===4?"'Courier New',monospace":M,
                fontSize:j===3||j===4?9:10,whiteSpace:"nowrap"}}>{v}</td>
            ))}
          </tr>
        ))}</tbody>
      </table>
    </div>
    <Good ch="Four independent DSHOT lines (one per nacelle EDF) let the FC arm/disarm each EDF individually. A failed ESC is disarmed in firmware within 50ms of telemetry fault detection — the other EDF in the same nacelle continues without interruption."/>
    <Warn ch="Series EDF pairing requires matched fan blade pitch within ±0.5°. Verify fan balance and pitch match before commissioning each nacelle. Mismatched pitch causes pressure recovery loss and unequal loading on the shaft bearings."/>
    <Note c={C.yellow} ch="PDB current derating: each nacelle now draws up to 168A peak (2× 84A) vs 84A previously. Upgrade main bus bar to 4-AWG silicone and verify XT90-S connectors are rated for combined current. Use bus bar distribution point per nacelle rather than series XT30 pigtails."/>
  </div>);
}

// ── APP ───────────────────────────────────────────────────────
const TABS = [
  {label:"Overview",        value:"overview"},
  {label:"Dimensions",      value:"dimensions"},
  {label:"Weight & Thrust", value:"weight"},
  {label:"Balance & CG",   value:"balance"},
  {label:"Avionics",        value:"avionics"},
  {label:"Hull & Foam",     value:"foam"},
  {label:"Access Panels",   value:"panels"},
  {label:"Obstacle Avoid.", value:"sensors"},
  {label:"Cargo & Nacelle", value:"cargo"},
  {label:"Dual-EDF Nacelle",value:"dual_edf"},
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
            SERENITY TILTROTOR · 18" CANONICAL · REV K</div>
          <h1 style={{margin:0,fontSize:18,fontWeight:"normal",color:C.text,letterSpacing:"0.07em",fontFamily:MB}}>
            SERENITY-CLASS FIREFLY TILTROTOR UAV</h1>
          <div style={{color:"rgba(0,229,255,0.6)",fontSize:10,marginTop:3,fontFamily:M}}>
            {DIM.L_MM}mm ({DIM.L_IN}") · 2×80mm 6S series EDFs per nacelle · XFLY X4 PRO 4S fuselage EDF · 12× VL53L5CX ToF dual-array · 4"×3"×3" cargo gondola · nacelle −5°–140° · 4× nacelle ESCs w/telem · 6 access panels
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
      {tab==="dual_edf"    && <DualEDFNacelleTab/>}
    </div>
  </div>);
}
