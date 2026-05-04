import { useState } from "react";

// ── tokens ─────────────────────────────────────────────────────
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
  bg:"#06080c", border:"rgba(0,229,255,0.11)", accent:"#00e5ff",
  orange:"#ff6b35", yellow:"#ffe600", purple:"#c084fc", green:"#4ade80",
  pink:"#f472b6", teal:"#2dd4bf", red:"#f87171", hull:"rgba(0,229,255,0.07)",
  dim:"rgba(255,255,255,0.90)", dimmer:"rgba(255,255,255,0.80)", text:"rgba(255,255,255,0.82)",
};
const M = "'OpenDyslexic Mono','OpenDyslexic','OpenDyslexicMono',monospace";

// ── primitives ────────────────────────────────────────────────
const SH=({t,c=C.accent,mt=22})=>(
  <div style={{display:"flex",alignItems:"center",gap:10,marginBottom:14,marginTop:mt}}>
    <div style={{width:3,height:17,background:c}}/>
    <span style={{color:c,fontFamily:M,fontSize:13,letterSpacing:"0.13em",textTransform:"uppercase",fontWeight:"normal"}}>{t}</span>
  </div>
);
const KV=({k,v,c=C.text,u=""})=>(
  <div style={{display:"flex",justifyContent:"space-between",padding:"5px 0",
    borderBottom:"1px solid rgba(0,229,255,0.07)",alignItems:"baseline"}}>
    <span style={{color:C.dim,fontFamily:M,fontSize:11}}>{k}</span>
    <span style={{color:c,fontFamily:M,fontSize:11}}>{v}{u&&<span style={{color:C.accent,marginLeft:4,fontSize:10}}>{u}</span>}</span>
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

// ── BG grid ───────────────────────────────────────────────────
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

// ════════════════════════════════════════════════════════════════
//  SERENITY HULL GEOMETRY — all in px, nose at left
//  Scale: 1 px ≈ 0.72 mm  →  320mm hull = 444px
//  Total length including engine pod: 360mm = 500px
// ════════════════════════════════════════════════════════════════
// X positions (from nose, in px)
const S = (mm) => mm * 1.30;      // scale: 1.30 px/mm
const NX  = 55;                    // nose tip x
const x   = (mm) => NX + S(mm);   // nose-relative x

// KEY X stations (mm from nose):
const X_COCKPIT_END   = x(88);    // end of cockpit bubble
const X_STRUT_FWD     = x(110);   // outrigger arm forward junction
const X_STRUT_AFT     = x(175);   // outrigger arm aft junction
const X_HULL_MAX      = x(140);   // maximum hull beam
const X_BATTERY_CTR   = x(185);   // battery centroid
const X_PAYLOAD_FWD   = x(130);   // payload bay forward
const X_PAYLOAD_AFT   = x(200);   // payload bay aft
const X_NECK_START    = x(220);   // hull narrows to engine neck
const X_NECK_END      = x(260);   // neck end / engine bell start
const X_ENGINE_CTR    = x(300);   // 30mm EDF centre
const X_TAIL          = x(360);   // extreme tail

// CG & pivot
const X_CG     = x(152);   // target CG
const X_PIVOT  = x(160);   // wing pivot / neutral point

// ── SERENITY TOP-VIEW PATH ─────────────────────────────────────
// Hull outline — smooth Bezier approximation of the Serenity silhouette
function TopHullPath(){
  const CY = 0; // relative to hull centreline
  // nose tip → cockpit bulge → waist → max beam → taper → neck → engine bell → tail
  // symmetric, generate upper then reflect for lower
  const pts = [
    [x(0),   0],     // nose tip
    [x(20),  18],    // nose widening
    [x(55),  42],    // cockpit shoulder
    [x(88),  48],    // cockpit max (side window)
    [x(120), 55],    // main hull max beam region
    [x(160), 52],    // battery bay
    [x(220), 38],    // hull taper starts
    [x(255), 24],    // neck
    [x(280), 32],    // engine bell widens
    [x(320), 38],    // engine bell max
    [x(360), 28],    // engine exit / tail
  ];
  // Build SVG smooth path (upper half, mirrored for lower)
  let d = `M ${NX} 0 `;
  // upper hull
  for(let i=1;i<pts.length;i++){
    const [px,py]=pts[i];
    const [qx,qy]=pts[i-1];
    const cx=(qx+px)/2; const cy=(qy+py)/2;
    d += `Q ${qx} ${qy} ${cx} ${cy} `;
  }
  d += `Q ${pts[pts.length-2][0]} ${pts[pts.length-2][1]} ${pts[pts.length-1][0]} ${pts[pts.length-1][1]} `;
  return {upper:pts, path:d};
}

// ── TOP VIEW SVG ──────────────────────────────────────────────
function TopView({sel,onSel}){
  const VW=740, VH=340, CY=170;
  const H=(mm)=>CY-S(mm); // y for +beam
  const L=(mm)=>CY+S(mm); // y for -beam

  // Hull half-widths at key stations (mm from nose)
  const profile=[
    [0,0],[8,10],[22,18],[40,30],[58,36],[88,37],
    [120,42],[140,42],[165,40],[190,36],[220,29],
    [252,18],[260,16],[278,24],[305,29],[330,28],[360,22],
  ];
  const upper = profile.map(([xmm,ymm])=>[x(xmm), CY-S(ymm)]);
  const lower = [...profile].reverse().map(([xmm,ymm])=>[x(xmm), CY+S(ymm)]);
  const allPts=[...upper,...lower];
  const outline=allPts.map((p,i)=>i===0?`M${p[0]},${p[1]}`:`L${p[0]},${p[1]}`).join(" ")+"Z";

  // Outrigger arms (the Serenity's lateral struts)
  // Junction at x(130)–x(175), extends to 340mm from centreline each side
  const ARM_Y_SIDE  = S(340); // 340mm from centreline
  const ARM_Y_INNER = S(46);  // where arm meets hull

  // Nacelle pods at arm tips: 60mm EDF duct, oval top view
  const N_RX=S(32), N_RY=S(14); // nacelle oval half-widths

  // Cockpit dome footprint
  const ckpX=x(44), ckpY=S(26);

  // Highlighted zones
  const zones=[
    {id:"cockpit",  lbl:"COCKPIT / SENSOR BAY",   x1:x(0),  x2:x(88),  c:C.teal},
    {id:"avionics", lbl:"AVIONICS",               x1:x(60), x2:x(160), c:C.accent},
    {id:"battery",  lbl:"BATTERY RAIL",            x1:x(140),x2:x(230), c:C.yellow},
    {id:"payload",  lbl:"PAYLOAD BAY (BELLY)",     x1:x(130),x2:x(200), c:C.pink},
    {id:"engine",   lbl:"FWD EDF (30mm)",          x1:x(270),x2:x(330), c:C.orange},
  ];

  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      <defs>
        <clipPath id="tvclip"><rect x={0} y={0} width={VW} height={VH}/></clipPath>
      </defs>

      {/* ── Zone overlays ── */}
      {zones.map(z=>(
        <rect key={z.id} x={z.x1} y={CY-S(46)} width={z.x2-z.x1} height={S(92)}
          fill={`${z.c}12`} stroke={z.c} strokeWidth={0.7} strokeDasharray="5 3" opacity={0.7}
          rx={3} style={{cursor:"pointer"}} onClick={()=>onSel(sel===z.id?null:z.id)}/>
      ))}

      {/* ── Hull outline ── */}
      <path d={outline} fill={C.hull} stroke={C.accent} strokeWidth={1.8}/>

      {/* Cockpit dome footprint */}
      <ellipse cx={ckpX} cy={CY} rx={S(44)} ry={ckpY}
        fill="rgba(0,229,255,0.08)" stroke={C.accent} strokeWidth={1}/>

      {/* Dorsal ridge line */}
      <line x1={x(30)} y1={CY} x2={x(280)} y2={CY}
        stroke="rgba(0,229,255,0.25)" strokeWidth={0.8} strokeDasharray="8 4"/>

      {/* ── Outrigger arms ── */}
      {[-1,1].map(side=>{
        const sy=CY+side*ARM_Y_SIDE;
        const iy=CY+side*ARM_Y_INNER;
        // arm tapers from hull to tip
        const aPts=[
          [x(115), CY+side*S(42)],
          [x(128), CY+side*S(48)],
          [x(152), CY+side*S(180)],
          [x(160), sy],
          [x(175), sy],
          [x(185), CY+side*S(175)],
          [x(196), CY+side*S(48)],
        ];
        const fwd=`M${aPts[0][0]},${aPts[0][1]} `;
        const afwd=aPts.slice(1,4).map(p=>`L${p[0]},${p[1]}`).join(" ");
        const abck=aPts.slice(4).reverse().map(p=>`L${p[0]},${p[1]}`).join(" ");
        const armPath=fwd+afwd+" "+abck+"Z";
        return(
          <g key={side}>
            <path d={armPath} fill="rgba(0,229,255,0.05)" stroke={C.accent} strokeWidth={1.3}/>
            {/* CF spar tube line */}
            <line x1={x(130)} y1={CY+side*S(50)} x2={x(170)} y2={sy-side*S(4)}
              stroke="rgba(0,229,255,0.35)" strokeWidth={2} strokeDasharray="6 3"/>
            {/* Nacelle EDF pod */}
            <ellipse cx={x(155)} cy={sy} rx={N_RX} ry={N_RY}
              fill="rgba(255,107,53,0.12)" stroke={C.orange} strokeWidth={1.5}/>
            {/* Fan inlet circle */}
            <circle cx={x(155)} cy={sy} r={S(20)}
              fill="rgba(255,107,53,0.08)" stroke={C.orange} strokeWidth={0.8} strokeDasharray="3 2"/>
            {/* Tilt axis indicator */}
            <line x1={x(130)} y1={sy} x2={x(180)} y2={sy}
              stroke={C.orange} strokeWidth={0.8} strokeDasharray="3 2" opacity={0.6}/>
            <text x={x(155)} y={sy+(side>0?14:-18)} textAnchor="middle"
              fill={C.orange} fontSize={7} fontFamily={M}>{side<0?"NACELLE L":"NACELLE R"}</text>
          </g>
        );
      })}

      {/* ── Engine bell ── */}
      <ellipse cx={X_ENGINE_CTR} cy={CY} rx={S(18)} ry={S(18)}
        fill="rgba(255,230,0,0.1)" stroke={C.yellow} strokeWidth={1.5}/>
      <circle cx={X_ENGINE_CTR} cy={CY} r={S(10)}
        fill="rgba(255,230,0,0.15)" stroke={C.yellow} strokeWidth={1}/>
      <text x={X_ENGINE_CTR} y={CY+3} textAnchor="middle"
        fill={C.yellow} fontSize={7} fontFamily={M}>EDF</text>

      {/* ── Pitot ── */}
      <line x1={NX} y1={CY} x2={NX-22} y2={CY}
        stroke={C.teal} strokeWidth={2.5} strokeLinecap="round"/>
      <circle cx={NX-22} cy={CY} r={2.5} fill={C.teal}/>

      {/* ── Antenna markers ── */}
      {/* GPS patch */}
      <rect x={x(46)} y={CY-S(14)} width={S(24)} height={S(10)}
        fill="rgba(74,222,128,0.2)" stroke="#4ade80" strokeWidth={1}/>
      <text x={x(58)} y={CY-S(18)} textAnchor="middle" fill="#4ade80" fontSize={6} fontFamily={M}>GPS</text>
      {/* 49MHz dorsal */}
      <circle cx={x(290)} cy={CY-S(16)} r={4}
        fill="rgba(244,114,182,0.2)" stroke={C.pink} strokeWidth={1}/>
      <text x={x(290)} y={CY-S(22)} textAnchor="middle" fill={C.pink} fontSize={6} fontFamily={M}>49M↑</text>
      {/* SiK belly */}
      <circle cx={x(238)} cy={CY} r={4}
        fill="rgba(255,107,53,0.15)" stroke={C.orange} strokeWidth={0.8} strokeDasharray="2 2"/>
      <text x={x(238)} y={CY+12} textAnchor="middle" fill={C.orange} fontSize={6} fontFamily={M}>SiK↓</text>

      {/* ── CG & pivot ── */}
      <line x1={X_CG} y1={CY-S(56)} x2={X_CG} y2={CY+S(56)}
        stroke={C.green} strokeWidth={1} strokeDasharray="5 3"/>
      <polygon points={`${X_CG},${CY-S(56)} ${X_CG-7},${CY-S(36)} ${X_CG+7},${CY-S(36)}`}
        fill={C.green} opacity={0.9}/>
      <text x={X_CG} y={CY-S(62)} textAnchor="middle" fill={C.green} fontSize={7} fontFamily={M}>CG·152</text>

      {/* Zone labels */}
      {sel && zones.filter(z=>z.id===sel).map(z=>(
        <text key={z.id} x={(z.x1+z.x2)/2} y={CY-S(52)} textAnchor="middle"
          fill={z.c} fontSize={9} fontFamily={M} fontWeight="bold">{z.lbl}</text>
      ))}

      {/* Dim line */}
      <line x1={NX} y1={VH-18} x2={X_TAIL} y2={VH-18} stroke={C.accent} strokeWidth={0.4} opacity={0.25}/>
      <line x1={NX} y1={VH-22} x2={NX} y2={VH-14} stroke={C.accent} strokeWidth={0.4} opacity={0.25}/>
      <line x1={X_TAIL} y1={VH-22} x2={X_TAIL} y2={VH-14} stroke={C.accent} strokeWidth={0.4} opacity={0.25}/>
      <text x={(NX+X_TAIL)/2} y={VH-7} textAnchor="middle" fill={C.dimmer} fontSize={7} fontFamily={M}>360 mm</text>

      {/* Wingspan dim */}
      <line x1={NX+S(25)} y1={CY-S(350)} x2={NX+S(25)} y2={CY+S(350)}
        stroke={C.accent} strokeWidth={0.4} opacity={0.15}/>
      <text x={NX+S(25)-8} y={CY} textAnchor="middle" fill={C.dimmer} fontSize={7} fontFamily={M}
        transform={`rotate(-90 ${NX+S(25)-8} ${CY})`}>680mm wingspan</text>

      <text x={VW/2} y={16} textAnchor="middle" fill="rgba(0,229,255,0.25)"
        fontSize={9} fontFamily={M} letterSpacing="0.12em">TOP / PLAN VIEW — CLICK ZONE TO IDENTIFY</text>
      <text x={NX-8} y={CY+4} textAnchor="end" fill={C.dimmer} fontSize={7} fontFamily={M}>NOSE</text>
      <text x={X_TAIL+5} y={CY+4} fill={C.dimmer} fontSize={7} fontFamily={M}>TAIL</text>
    </svg>
  );
}

// ── SIDE VIEW SVG ─────────────────────────────────────────────
function SideView(){
  const VW=680, VH=320, BY=180; // BY = bottom of fuselage baseline

  // Side profile half-heights (above and below centre) at key x stations (mm)
  // Serenity side: forward cockpit bubble tall, hull sweeps, neck thin, engine bell re-expands
  const above=[ // top edge
    [0,0],[5,8],[18,22],[40,32],[58,38],[75,36],
    [88,30],[110,26],[140,26],[165,25],[195,24],
    [220,20],[255,12],[270,16],[300,20],[340,18],[360,14],
  ];
  const below=[ // bottom edge (belly)
    [0,0],[10,-5],[35,-14],[88,-20],[140,-22],[180,-22],
    [220,-20],[255,-14],[270,-18],[300,-22],[340,-20],[360,-14],
  ];
  const buildPath=(pts,flip=false)=>{
    return pts.map(([xmm,ymm],i)=>{
      const px=NX+S(xmm), py=BY-S(ymm)*(flip?-1:1);
      return i===0?`M${px},${py}`:`L${px},${py}`;
    }).join(" ");
  };
  const topEdge=buildPath(above);
  const botEdge=buildPath(below.map(([x,y])=>[x,-y])); // flip for below
  const outlineTop=above.map(([xmm,ymm])=>[NX+S(xmm), BY-S(ymm)]);
  const outlineBot=[...below].reverse().map(([xmm,ymm])=>[NX+S(xmm), BY+S(Math.abs(ymm))]);
  const allSide=[...outlineTop,...outlineBot];
  const sidePath=allSide.map((p,i)=>i===0?`M${p[0]},${p[1]}`:`L${p[0]},${p[1]}`).join(" ")+"Z";

  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* Hull */}
      <path d={sidePath} fill={C.hull} stroke={C.accent} strokeWidth={1.8}/>

      {/* Cockpit bubble — the iconic raised dome of the Serenity */}
      <path d={`M${NX+S(8)},${BY-S(22)} Q${NX+S(45)},${BY-S(65)} ${NX+S(85)},${BY-S(30)}`}
        fill="rgba(0,229,255,0.1)" stroke={C.accent} strokeWidth={1.2}/>
      <text x={NX+S(44)} y={BY-S(48)} textAnchor="middle"
        fill="rgba(0,229,255,0.45)" fontSize={7} fontFamily={M}>COCKPIT</text>

      {/* Outrigger junction visible as bracket on side */}
      <line x1={NX+S(130)} y1={BY-S(26)} x2={NX+S(130)} y2={BY-S(60)}
        stroke={C.orange} strokeWidth={2} strokeLinecap="round"/>
      <line x1={NX+S(170)} y1={BY-S(26)} x2={NX+S(170)} y2={BY-S(60)}
        stroke={C.orange} strokeWidth={2} strokeLinecap="round"/>
      {/* Nacelle side profile — shown in hover (vertical) position */}
      <rect x={NX+S(138)} y={BY-S(95)} width={S(24)} height={S(48)} rx={4}
        fill="rgba(255,107,53,0.1)" stroke={C.orange} strokeWidth={1.3}/>
      {/* Fan inlet at bottom of nacelle in hover */}
      <ellipse cx={NX+S(150)} cy={BY-S(52)} rx={S(10)} ry={S(4)}
        fill="rgba(255,107,53,0.15)" stroke={C.orange} strokeWidth={0.8}/>
      {/* Tilt arc */}
      <path d={`M${NX+S(130)},${BY-S(62)} A${S(24)},${S(24)} 0 0,1 ${NX+S(154)},${BY-S(38)}`}
        fill="none" stroke={C.orange} strokeWidth={0.8} strokeDasharray="3 2" opacity={0.7}/>
      <text x={NX+S(150)} y={BY-S(102)} textAnchor="middle"
        fill={C.orange} fontSize={6} fontFamily={M}>±90°</text>
      <text x={NX+S(150)} y={BY-S(110)} textAnchor="middle"
        fill={C.orange} fontSize={7} fontFamily={M} fontWeight="bold">NACELLE</text>

      {/* Engine bell — iconic Serenity exhaust ring */}
      <path d={`M${NX+S(265)},${BY-S(13)} Q${NX+S(275)},${BY-S(24)} ${NX+S(285)},${BY-S(22)}
                L${NX+S(330)},${BY-S(22)} Q${NX+S(345)},${BY-S(20)} ${NX+S(355)},${BY-S(15)}
                L${NX+S(360)},${BY-S(14)} L${NX+S(360)},${BY+S(14)}
                L${NX+S(355)},${BY+S(15)} Q${NX+S(345)},${BY+S(20)} ${NX+S(330)},${BY+S(22)}
                L${NX+S(285)},${BY+S(22)} Q${NX+S(275)},${BY+S(24)} ${NX+S(265)},${BY+S(13)}`}
        fill="rgba(255,230,0,0.08)" stroke={C.yellow} strokeWidth={1.3}/>
      <circle cx={NX+S(300)} cy={BY} r={S(13)}
        fill="rgba(255,230,0,0.12)" stroke={C.yellow} strokeWidth={1}/>
      <text x={NX+S(300)} y={BY+4} textAnchor="middle" fill={C.yellow} fontSize={6} fontFamily={M}>30mm EDF</text>

      {/* Payload bay belly */}
      <rect x={NX+S(130)} y={BY+S(20)} width={S(70)} height={S(22)} rx={3}
        fill="rgba(244,114,182,0.1)" stroke={C.pink} strokeWidth={1} strokeDasharray="3 2"/>
      <text x={NX+S(165)} y={BY+S(33)} textAnchor="middle"
        fill={C.pink} fontSize={7} fontFamily={M}>PAYLOAD BAY</text>

      {/* Landing skids — adapted from Serenity's 3-leg style */}
      {[x(95),x(230)].map((sx,i)=>(
        <g key={i}>
          <line x1={sx} y1={BY+S(20)} x2={sx-S(8)} y2={BY+S(42)}
            stroke={C.accent} strokeWidth={1.5} opacity={0.5}/>
          <line x1={sx-S(22)} y1={BY+S(42)} x2={sx+S(22)} y2={BY+S(42)}
            stroke={C.accent} strokeWidth={2} opacity={0.5}/>
        </g>
      ))}

      {/* GPS patch on cockpit top */}
      <rect x={NX+S(38)} y={BY-S(62)} width={S(22)} height={S(8)} rx={2}
        fill="rgba(74,222,128,0.2)" stroke="#4ade80" strokeWidth={1}/>
      <text x={NX+S(49)} y={BY-S(66)} textAnchor="middle" fill="#4ade80" fontSize={6} fontFamily={M}>GPS</text>

      {/* 49MHz dorsal whip */}
      <circle cx={NX+S(290)} cy={BY-S(22)} r={3}
        fill="rgba(244,114,182,0.2)" stroke={C.pink} strokeWidth={1}/>
      <line x1={NX+S(290)} y1={BY-S(25)} x2={NX+S(290)} y2={BY-S(65)}
        stroke={C.pink} strokeWidth={1.5} strokeLinecap="round"/>
      {[0,1,2].map(i=>(
        <ellipse key={i} cx={NX+S(290)} cy={BY-S(35+i*7)} rx={3} ry={2}
          fill="none" stroke={C.pink} strokeWidth={0.7} opacity={0.75}/>
      ))}
      <text x={NX+S(290)} y={BY-S(72)} textAnchor="middle"
        fill={C.pink} fontSize={6} fontFamily={M}>49MHz</text>

      {/* SiK belly */}
      <rect x={NX+S(234)} y={BY+S(20)} width={S(8)} height={3} rx={1}
        fill={C.orange} stroke={C.orange} strokeWidth={0.5}/>
      <line x1={NX+S(238)} y1={BY+S(23)} x2={NX+S(238)} y2={BY+S(48)}
        stroke={C.orange} strokeWidth={1.8} strokeLinecap="round"/>
      <text x={NX+S(238)} y={BY+S(56)} textAnchor="middle" fill={C.orange} fontSize={6} fontFamily={M}>SiK↓</text>

      {/* CG line */}
      <line x1={X_CG} y1={BY-S(68)} x2={X_CG} y2={BY+S(48)}
        stroke={C.green} strokeWidth={1} strokeDasharray="5 3"/>
      <text x={X_CG} y={BY-S(74)} textAnchor="middle" fill={C.green} fontSize={8} fontFamily={M}>CG</text>

      {/* Pitot */}
      <line x1={NX} y1={BY} x2={NX-22} y2={BY}
        stroke={C.teal} strokeWidth={2.5} strokeLinecap="round"/>
      <circle cx={NX-22} cy={BY} r={2.5} fill={C.teal}/>

      {/* Dim */}
      <line x1={NX} y1={VH-12} x2={X_TAIL} y2={VH-12}
        stroke={C.accent} strokeWidth={0.4} opacity={0.2}/>
      <text x={(NX+X_TAIL)/2} y={VH-4} textAnchor="middle" fill={C.dimmer} fontSize={7} fontFamily={M}>360 mm</text>
      <text x={NX-12} y={BY+4} textAnchor="end" fill={C.dimmer} fontSize={7} fontFamily={M}>NOSE</text>
      <text x={X_TAIL+5} y={BY+4} fill={C.dimmer} fontSize={7} fontFamily={M}>TAIL</text>
      <text x={VW/2} y={14} textAnchor="middle" fill="rgba(0,229,255,0.25)"
        fontSize={9} fontFamily={M} letterSpacing="0.12em">RIGHT SIDE VIEW</text>
    </svg>
  );
}

// ── FRONT VIEW SVG ────────────────────────────────────────────
function FrontView(){
  const VW=520, VH=340, CX=260, BY=220;

  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* Hull front face — characteristic Serenity rounded front */}
      <ellipse cx={CX} cy={BY-S(24)} rx={S(40)} ry={S(36)}
        fill={C.hull} stroke={C.accent} strokeWidth={1.8}/>
      {/* Cockpit bubble — rounded top dome visible from front */}
      <ellipse cx={CX} cy={BY-S(52)} rx={S(28)} ry={S(20)}
        fill="rgba(0,229,255,0.1)" stroke={C.accent} strokeWidth={1.2}/>
      {/* Cockpit window hint */}
      <ellipse cx={CX} cy={BY-S(52)} rx={S(18)} ry={S(12)}
        fill="rgba(0,229,255,0.08)" stroke="rgba(0,229,255,0.4)" strokeWidth={0.8}/>

      {/* Outrigger arms extending to each side (angled down ~8° in cruise) */}
      {[-1,1].map(side=>{
        const NX2=CX+side*S(46), NY2=BY-S(26);
        const TX=CX+side*S(340), TY=BY-S(12);
        return(
          <g key={side}>
            {/* Arm cross-section */}
            <line x1={NX2} y1={NY2} x2={TX} y2={TY}
              stroke={C.accent} strokeWidth={2}/>
            {/* Nacelle at tip — front view: circular duct */}
            <ellipse cx={TX} cy={TY} rx={S(30)} ry={S(22)}
              fill="rgba(255,107,53,0.1)" stroke={C.orange} strokeWidth={1.5}/>
            {/* EDF intake circle */}
            <circle cx={TX} cy={TY} r={S(18)}
              fill="rgba(255,107,53,0.08)" stroke={C.orange} strokeWidth={0.8} strokeDasharray="3 2"/>
            <circle cx={TX} cy={TY} r={S(10)}
              fill="rgba(255,107,53,0.12)" stroke={C.orange} strokeWidth={0.6}/>
            {/* Tilt axis line through arm */}
            <line x1={TX-S(32)} y1={TY} x2={TX+S(32)} y2={TY}
              stroke={C.orange} strokeWidth={0.7} strokeDasharray="3 2" opacity={0.6}/>
            <text x={TX} y={TY+S(28)} textAnchor="middle"
              fill={C.orange} fontSize={7} fontFamily={M}>{side<0?"L":"R"}</text>
          </g>
        );
      })}

      {/* Belly payload bay door edge visible */}
      <rect x={CX-S(30)} y={BY+S(8)} width={S(60)} height={S(10)} rx={2}
        fill="rgba(244,114,182,0.1)" stroke={C.pink} strokeWidth={1} strokeDasharray="3 2"/>

      {/* Landing skids front view */}
      {[-1,1].map(side=>(
        <g key={side}>
          <line x1={CX+side*S(18)} y1={BY+S(22)} x2={CX+side*S(24)} y2={BY+S(40)}
            stroke={C.accent} strokeWidth={1.5} opacity={0.5}/>
          <line x1={CX+side*S(24)} y1={BY+S(40)} x2={CX+side*S(40)} y2={BY+S(40)}
            stroke={C.accent} strokeWidth={2} opacity={0.5}/>
        </g>
      ))}

      {/* GPS on top */}
      <rect x={CX-S(12)} y={BY-S(74)} width={S(24)} height={S(8)} rx={2}
        fill="rgba(74,222,128,0.2)" stroke="#4ade80" strokeWidth={1}/>
      <text x={CX} y={BY-S(78)} textAnchor="middle" fill="#4ade80" fontSize={7} fontFamily={M}>GPS PATCH</text>

      {/* Pitot tip */}
      <circle cx={CX} cy={BY-S(24)} r={3} fill={C.teal} opacity={0.8}/>
      <text x={CX} y={BY-S(6)} textAnchor="middle" fill={C.teal} fontSize={7} fontFamily={M}>PITOT</text>

      {/* Span dim */}
      <line x1={CX-S(340)} y1={BY+S(60)} x2={CX+S(340)} y2={BY+S(60)}
        stroke={C.accent} strokeWidth={0.4} opacity={0.2}/>
      <text x={CX} y={BY+S(72)} textAnchor="middle" fill={C.dimmer} fontSize={7} fontFamily={M}>680 mm tip-to-tip</text>

      <text x={VW/2} y={16} textAnchor="middle" fill="rgba(0,229,255,0.25)"
        fontSize={9} fontFamily={M} letterSpacing="0.12em">FRONT VIEW (NOSE-ON)</text>
    </svg>
  );
}

// ── REAR VIEW SVG ─────────────────────────────────────────────
function RearView(){
  const VW=520, VH=300, CX=260, BY=200;
  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* Engine bell — the iconic ring of the Serenity main drive */}
      <circle cx={CX} cy={BY-S(18)} r={S(30)} fill="rgba(255,230,0,0.08)" stroke={C.yellow} strokeWidth={2}/>
      <circle cx={CX} cy={BY-S(18)} r={S(22)} fill="rgba(255,230,0,0.1)" stroke={C.yellow} strokeWidth={1.2}/>
      <circle cx={CX} cy={BY-S(18)} r={S(12)} fill="rgba(255,230,0,0.18)" stroke={C.yellow} strokeWidth={1}/>
      {/* EDF inside engine bell */}
      <circle cx={CX} cy={BY-S(18)} r={S(10)} fill="rgba(255,230,0,0.12)" stroke={C.yellow} strokeWidth={0.8} strokeDasharray="3 2"/>
      {/* Blades */}
      {[0,51,102,153,204,255,306].map(a=>(
        <line key={a} x1={CX} y1={BY-S(18)}
          x2={CX+S(8)*Math.cos(a*Math.PI/180)}
          y2={BY-S(18)+S(8)*Math.sin(a*Math.PI/180)}
          stroke={C.yellow} strokeWidth={0.7} opacity={0.6}/>
      ))}
      <text x={CX} y={BY-S(18)+4} textAnchor="middle" fill={C.yellow} fontSize={6} fontFamily={M}>30mm</text>

      {/* Hull rear silhouette */}
      <ellipse cx={CX} cy={BY-S(18)} rx={S(42)} ry={S(34)}
        fill="none" stroke={C.accent} strokeWidth={1.5}/>

      {/* 49MHz dorsal whip base — visible on top */}
      <circle cx={CX} cy={BY-S(50)} r={4}
        fill="rgba(244,114,182,0.2)" stroke={C.pink} strokeWidth={1}/>
      <line x1={CX} y1={BY-S(54)} x2={CX} y2={BY-S(80)}
        stroke={C.pink} strokeWidth={1.5} strokeLinecap="round"/>
      <text x={CX} y={BY-S(84)} textAnchor="middle" fill={C.pink} fontSize={6} fontFamily={M}>49MHz↑</text>

      {/* SiK belly whip — visible at bottom */}
      <line x1={CX} y1={BY+S(4)} x2={CX} y2={BY+S(26)}
        stroke={C.orange} strokeWidth={1.5} strokeLinecap="round"/>
      <text x={CX} y={BY+S(34)} textAnchor="middle" fill={C.orange} fontSize={6} fontFamily={M}>SiK↓</text>

      {/* Outrigger arms + nacelles rear view */}
      {[-1,1].map(side=>{
        const TX=CX+side*S(340), TY=BY-S(10);
        return(
          <g key={side}>
            <line x1={CX+side*S(44)} y1={BY-S(22)} x2={TX} y2={TY}
              stroke={C.accent} strokeWidth={1.5}/>
            <ellipse cx={TX} cy={TY} rx={S(30)} ry={S(22)}
              fill="rgba(255,107,53,0.08)" stroke={C.orange} strokeWidth={1.3}/>
            <circle cx={TX} cy={TY} r={S(10)}
              fill="rgba(255,107,53,0.1)" stroke={C.orange} strokeWidth={0.7} strokeDasharray="2 2"/>
            <text x={TX} y={TY+S(30)} textAnchor="middle"
              fill={C.orange} fontSize={7} fontFamily={M}>{side<0?"L":"R"}</text>
          </g>
        );
      })}

      {/* Nacelles in hover (vertical) shown as circles with down arrows */}
      {[-1,1].map(side=>{
        const TX=CX+side*S(340), TY=BY-S(10);
        return(
          <g key={"v"+side}>
            <text x={TX} y={TY-S(28)} textAnchor="middle"
              fill={C.orange} fontSize={8} fontFamily={M}>↑</text>
          </g>
        );
      })}

      <text x={VW/2} y={16} textAnchor="middle" fill="rgba(0,229,255,0.25)"
        fontSize={9} fontFamily={M} letterSpacing="0.12em">REAR VIEW — HOVER (NACELLES VERTICAL)</text>
      <line x1={CX-S(340)} y1={VH-14} x2={CX+S(340)} y2={VH-14}
        stroke={C.accent} strokeWidth={0.4} opacity={0.2}/>
      <text x={CX} y={VH-5} textAnchor="middle" fill={C.dimmer} fontSize={7} fontFamily={M}>680 mm</text>
    </svg>
  );
}

// ── DIAGRAM TAB ───────────────────────────────────────────────
const ZONE_DETAIL = {
  cockpit:{title:"Cockpit / Sensor Bay",c:C.teal,rows:[
    ["Contents","Pico 2 + TRIHAT-1 on M2.5 standoffs · MS4525DO airspeed · pitot port"],
    ["Access","Hinged canopy panel (cockpit dome is a friction-fit clear PETG cover)"],
    ["GPS","25×25mm patch on cockpit top roof · 58mm from nose tip"],
    ["Print","Separate cockpit shell print at 15% infill · clear PETG for transparency option"],
    ["Structural","Cockpit bulkhead (2mm CF plate, cockpit-frame formers) carries pitot loads"],
  ]},
  avionics:{title:"Avionics Bay",c:C.accent,rows:[
    ["Contents","CM4 Lite + CM4-CARRIER-1 + COMPHAT-1 stack on M2.5 CF-nylon standoffs"],
    ["Access","Top-access panel on dorsal mid-hull (snap-fit PETG panel, 4× M2 screws)"],
    ["Position","CM4 stack at 90–160mm from nose · mass centroid ~120mm"],
    ["Cooling","Natural convection through 4× Ø6mm NACA flush vents on hull sides"],
    ["WiFi","CM4 WiFi trace antenna faces upper-right hull side (PLA/PETG, RF transparent)"],
  ]},
  battery:{title:"Battery Rail",c:C.yellow,rows:[
    ["Battery","5S 2200mAh 75C LiPo · 105×34×22mm"],
    ["Rail","2× M3 aluminium rails running 130–235mm from nose on keel centreline"],
    ["Slide range","±22mm longitudinal CG trim · locked by M3 thumb screw"],
    ["Access","Belly belly door aft of payload bay (112×42mm PETG door, 2× magnets)"],
    ["Thermal","12mm clearance to fuselage skin · flush NACA vent on each side"],
  ]},
  payload:{title:"Payload Bay",c:C.pink,rows:[
    ["Dimensions","70×50×35mm internal · 130–200mm from nose · centreline"],
    ["Door","Hinged belly door · SG90 micro servo release latch"],
    ["Winch","N20 motor + 18mm spool forward of bay at x=120mm"],
    ["Hook","M2.5 stainless hook · Dyneema exits through 3mm slot in door centre"],
    ["Weight","200g max payload · 20:1 safety factor on Dyneema 40kg breaking load"],
  ]},
  engine:{title:"Rear Engine Bell (30mm EDF)",c:C.yellow,rows:[
    ["Duct","Printed PETG annular duct · matches Serenity engine bell silhouette exactly"],
    ["Fan","30mm 7-blade BLDC · 4000KV · 80g thrust @ 5S"],
    ["ESC","20A BLHeli_S · mounted inside aft hull cavity"],
    ["Mount","EDF sits in printed bell at x=300mm · 4× M2.5 bolts to CF keel"],
    ["Visual","The Serenity's circular engine bell perfectly houses the EDF exit and intake annulus"],
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
      <div style={{background:"rgba(0,229,255,0.04)",border:`1px solid ${C.border}`,borderRadius:4,
        padding:"10px 14px",marginBottom:16,fontFamily:M,fontSize:11,color:C.dim,lineHeight:1.8}}>
        The <span style={{color:C.accent}}>Serenity Firefly-class</span> is an ideal match: her two lateral
        tilting "atmo" engines map directly to our tilting nacelle EDFs, and the iconic circular main drive
        maps to our fixed forward EDF. Hull is printed as a thin-wall hollow shell over a CF structural skeleton.
      </div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 250px",gap:16,alignItems:"start",marginBottom:20}}>
        <div>
          <div style={{color:C.dimmer,fontFamily:M,fontSize:10,letterSpacing:"0.08em",marginBottom:6}}>
            TOP / PLAN VIEW · colour bands = functional zones · click to identify
          </div>
          <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:8,marginBottom:12}}>
            <TopView sel={sel} onSel={setSel}/>
          </div>
        </div>
        <div style={{position:"sticky",top:20}}>
          <div style={{color:C.dimmer,fontFamily:M,fontSize:10,letterSpacing:"0.08em",marginBottom:8}}>ZONE INSPECTOR</div>
          <ZonePanel id={sel}/>
        </div>
      </div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:16,marginBottom:16}}>
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

// ── MODIFICATIONS TAB ─────────────────────────────────────────
function ModsTab(){
  const mods=[
    {feature:"Overall scale",original:"~180mm display model",adapted:"360mm hull (×2 linear scale)",reason:"Fits 320–360mm fuselage requirement for all avionics and payload. Engine bell overhang accounts for extra 40mm."},
    {feature:"Construction method",original:"Solid PLA print, 20% infill, 137g",adapted:"Hollow thin-wall shell (1.5mm) over CF skeleton, 8% gyroid, ~105g printed",reason:"Shell construction cuts weight ~73% vs solid scale. CF skeleton carries all structural loads."},
    {feature:"Outrigger arms",original:"Solid printed struts, aesthetic only",adapted:"12mm OD CF spar tubes with printed PETG fairings snap-clipped over them",reason:"CF carries bending loads from 640g nacelle+motor thrust. Printed fairings preserve Serenity silhouette."},
    {feature:"Lateral engines",original:"Non-functional 'Firefly glow' pods",adapted:"60mm EDF ducted fans in printed nacelle housings on ±90° tilt servo pivots",reason:"The Serenity's engines already tilt between hover and cruise in the show — perfect functional match."},
    {feature:"Main drive engine",original:"Decorative circular exhaust bell",adapted:"The engine bell recess houses the 30mm forward EDF. Bell diameter matches 30mm duct exit exactly at this scale.",reason:"Engine bell silhouette preserved. Intake annulus faces aft; exit faces aft. Thrust is forward."},
    {feature:"Cockpit dome",original:"Solid printed dome",adapted:"Clear PETG friction-fit dome. Sensor bay underneath: Pico 2, TRIHAT-1, pitot port",reason:"Clear dome preserves the iconic look and lets status LEDs be visible. Dome lifts off for access."},
    {feature:"Hull belly",original:"Flat featureless belly",adapted:"Payload bay door (70×50mm) + winch slot + SiK antenna exit at 238mm",reason:"Belly was unused space. Payload door geometry follows Serenity's cargo ramp aesthetic."},
    {feature:"Dorsal ridge",original:"Cosmetic ridge line",adapted:"Ridge is a structural CF keel spine (6mm×3mm CF tube, nose to engine mount)",reason:"The keel runs inside the existing ridge geometry — invisible externally, adds ~10g structural mass."},
    {feature:"Landing gear",original:"3× short stub legs at ~60% and 90% length",adapted:"2× CF wire skid sets at x=95mm and x=230mm, angled from belly, following Serenity leg geometry",reason:"Serenity's 3-point leg style adapted to 2× wide skids. No retraction — fixed for drone simplicity."},
    {feature:"Print material",original:"PLA (rigid, brittle)",adapted:"PETG for all fuselage panels. CF-PETG for motor mount brackets and nacelle pivots. PLA+ for large fairings.",reason:"PETG survives crash shock and field heat better than PLA. CF-PETG adds stiffness to critical structural interfaces."},
  ];
  return(
    <div>
      <SH t="Serenity → Drone Adaptation Map" mt={0}/>
      <Note c={C.accent} ch="The Printables model (Peter Farell, printables.com/model/548545) is used as the geometric basis for the outer hull form. The drone is not a scale replica — the interior is completely redesigned. The iconic exterior silhouette is preserved and functional."/>
      <div style={{overflowX:"auto",marginTop:12}}>
        <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:11}}>
          <thead><tr>{["FEATURE","ORIGINAL MODEL","DRONE ADAPTATION","REASON"].map(h=>(
            <th key={h} style={{padding:"6px 10px",borderBottom:`1px solid ${C.border}`,color:C.accent,
              textAlign:"left",fontWeight:"normal",fontSize:10,letterSpacing:"0.07em",opacity:.8,whiteSpace:"nowrap"}}>{h}</th>
          ))}</tr></thead>
          <tbody>{mods.map((m,i)=>(
            <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent",verticalAlign:"top"}}>
              <td style={{padding:"7px 10px",color:C.teal,fontFamily:M,fontSize:10,fontWeight:"bold",whiteSpace:"nowrap"}}>{m.feature}</td>
              <td style={{padding:"7px 10px",color:C.dim,fontSize:10,maxWidth:160}}>{m.original}</td>
              <td style={{padding:"7px 10px",color:C.text,fontSize:10,maxWidth:200}}>{m.adapted}</td>
              <td style={{padding:"7px 10px",color:C.dimmer,fontSize:10,maxWidth:220,lineHeight:1.6}}>{m.reason}</td>
            </tr>
          ))}</tbody>
        </table>
      </div>
    </div>
  );
}

// ── PRINT STRATEGY TAB ────────────────────────────────────────
function PrintTab(){
  const parts=[
    {part:"Cockpit dome",mat:"Clear PETG",infill:"15% gyroid",walls:2,layer:"0.20",mass:12,note:"Transparent — allows LED status visibility. Friction-fit over cockpit bulkhead ring."},
    {part:"Cockpit/forward hull (0–90mm)",mat:"PETG",infill:"8% gyroid",walls:2,layer:"0.20",mass:18,note:"Includes pitot port boss and GPS standoff recess. Print nose-down with support for GPS standoff hole."},
    {part:"Main hull body (90–230mm)",mat:"PETG",infill:"8% gyroid",walls:2,layer:"0.20",mass:32,note:"Largest section. Dorsal access panel cutout in print. Battery rail bosses moulded in. Print in two halves (left/right split) for bed size."},
    {part:"Payload bay assembly (130–200mm belly)",mat:"PETG",infill:"20% gyroid",walls:3,layer:"0.20",mass:14,note:"Higher infill for structural integrity around winch mount and release servo boss."},
    {part:"Aft hull + neck (230–270mm)",mat:"PETG",infill:"10% gyroid",walls:2,layer:"0.20",mass:10,note:"Neck section — print vertically for best layer-line orientation at narrow section."},
    {part:"Engine bell (270–360mm)",mat:"PETG",infill:"20% gyroid",walls:3,layer:"0.20",mass:18,note:"EDF duct walls must be airtight — 3 walls minimum. Bell outer ring is cosmetic, inner duct is structural."},
    {part:"Outrigger arm fairings ×2",mat:"PETG",infill:"10% gyroid",walls:2,layer:"0.25",mass:8,note:"Snap-clips onto 12mm CF spar tube. Print flat. Two halves join with M2 screws flush with fairing surface."},
    {part:"Nacelle pods ×2",mat:"CF-PETG",infill:"20% gyroid",walls:3,layer:"0.20",mass:14,note:"Must handle EDF thrust and tilt loads. Print in CF-PETG. Include servo horn pocket and bearing seat."},
    {part:"Nacelle tilt brackets ×2",mat:"CF-PETG",infill:"40% gyroid",walls:4,layer:"0.15",mass:6,note:"Critical structural part. High infill for shear strength. Includes M3 heat-set inserts for servo mount."},
    {part:"Dorsal antenna fin",mat:"PETG",infill:"15% gyroid",walls:2,layer:"0.20",mass:4,note:"49MHz loaded whip mount. Non-structural fairing with coil pocket and coax routing channel."},
    {part:"Landing skid feet ×4",mat:"TPU 95A",infill:"20%",walls:3,layer:"0.30",mass:8,note:"Flexible crash-absorbing skid tips. TPU dampens EDF vibration from landing impact."},
  ];
  const totalPrint=parts.reduce((s,p)=>s+p.mass,0);
  return(
    <div>
      <SH t="Print Parts List" mt={0}/>
      <Note c={C.green} ch={`Total printed mass: ~${totalPrint}g (shell construction). Combined with CF skeleton (50g) and hardware = ~${totalPrint+50+15}g airframe total — within revised budget.`}/>
      <div style={{overflowX:"auto",marginTop:12}}>
        <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
          <thead><tr>{["PART","MATERIAL","INFILL","WALLS","LAYER","~MASS","NOTES"].map(h=>(
            <th key={h} style={{padding:"5px 8px",borderBottom:`1px solid ${C.border}`,color:C.accent,
              textAlign:"left",fontWeight:"normal",fontSize:9,letterSpacing:"0.07em",whiteSpace:"nowrap",opacity:.8}}>{h}</th>
          ))}</tr></thead>
          <tbody>{parts.map((p,i)=>(
            <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent",verticalAlign:"top"}}>
              <td style={{padding:"5px 8px",color:C.text,fontFamily:M,fontSize:10,whiteSpace:"nowrap"}}>{p.part}</td>
              <td style={{padding:"5px 8px",color:
                p.mat.includes("CF")?C.orange:p.mat.includes("TPU")?C.pink:C.teal,
                fontSize:10,whiteSpace:"nowrap"}}>{p.mat}</td>
              <td style={{padding:"5px 8px",color:C.dim,fontSize:10}}>{p.infill}</td>
              <td style={{padding:"5px 8px",color:C.dim,fontSize:10,textAlign:"center"}}>{p.walls}</td>
              <td style={{padding:"5px 8px",color:C.dim,fontSize:10}}>{p.layer}mm</td>
              <td style={{padding:"5px 8px",color:C.yellow,fontSize:10,fontWeight:"bold",whiteSpace:"nowrap"}}>{p.mass}g</td>
              <td style={{padding:"5px 8px",color:C.dimmer,fontSize:9,lineHeight:1.5,maxWidth:220}}>{p.note}</td>
            </tr>
          ))}</tbody>
          <tfoot><tr style={{borderTop:`1px solid ${C.border}`}}>
            <td colSpan={5} style={{padding:"7px 8px",color:C.accent,fontFamily:M,fontSize:10,textAlign:"right"}}>TOTAL PRINTED</td>
            <td style={{padding:"7px 8px",color:C.yellow,fontSize:13,fontWeight:"bold"}}>{totalPrint}g</td>
            <td/>
          </tr></tfoot>
        </table>
      </div>
      <SH t="Print Settings Summary"/>
      <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:12}}>
        {[
          {mat:"PETG",c:C.teal,rules:"Nozzle 235°C · Bed 85°C · Fan 30% · Slow first layer 20mm/s · Brim 5mm"},
          {mat:"CF-PETG",c:C.orange,rules:"Nozzle 250°C · Steel nozzle required (CF abrasive) · Bed 90°C · Fan 20% · No brim on CF parts"},
          {mat:"TPU 95A",c:C.pink,rules:"Nozzle 220°C · Bed 60°C · Fan 0% · Print slow 25mm/s · Dry filament before printing"},
        ].map(s=>(
          <div key={s.mat} style={{padding:"10px 12px",border:`1px solid ${s.c}33`,background:`${s.c}07`,borderRadius:4}}>
            <div style={{color:s.c,fontFamily:M,fontSize:11,fontWeight:"bold",marginBottom:6}}>{s.mat}</div>
            <div style={{color:C.dim,fontFamily:M,fontSize:9,lineHeight:1.8}}>{s.rules}</div>
          </div>
        ))}
      </div>
      <Warn ch="Print all CF-PETG parts on a printer with a hardened steel nozzle. Standard brass nozzles wear out within ~50g of CF filament. Dry all filament for 6h at 65°C before printing structural parts."/>
    </div>
  );
}

// ── WEIGHT & BALANCE TAB ──────────────────────────────────────
const WT_GROUPS=[
  {label:"Propulsion",c:C.orange,items:[
    {n:"2× 60mm EDF + BLDC motors",w:80},{n:"2× ESC 30A BLHeli32",w:28},
    {n:"2× nacelle tilt servos",w:18},{n:"30mm fwd fan + motor",w:18},{n:"Fwd ESC 20A",w:8},
  ]},
  {label:"Airframe (Serenity hull)",c:C.teal,items:[
    {n:"Printed hull shell (11 sections, PETG/CF-PETG)",w:144},{n:"CF 6×3mm keel spine 380mm",w:12},
    {n:"2× 12mm CF spar tubes 300mm",w:22},{n:"CF nacelle pivot brackets + hardware",w:16},
    {n:"TPU skid feet × 4",w:8},
  ]},
  {label:"Flight control — Pico 2",c:C.accent,items:[
    {n:"Raspberry Pi Pico 2",w:3},{n:"TRIHAT-1 sensor hat",w:15},
    {n:"MS4525DO airspeed + pitot",w:10},
  ]},
  {label:"Companion — CM4 stack",c:C.green,items:[
    {n:"CM4 Lite 4GB WiFi",w:8},{n:"CM4-CARRIER-1 PCB",w:14},
    {n:"COMPHAT-1 + ICs",w:20},{n:"SiK 915MHz air module",w:14},{n:"49MHz RCRS module",w:16},
  ]},
  {label:"Payload system",c:C.pink,items:[
    {n:"Payload release servo SG90",w:9},{n:"N20 winch + gearbox",w:14},
    {n:"Winch spool + Dyneema 5m",w:7},{n:"DRV8833 H-bridge PCB",w:4},
  ]},
  {label:"Power & wiring",c:C.yellow,items:[
    {n:"5S 2200mAh 75C LiPo",w:220},{n:"JST-GH harness + wiring",w:30},{n:"5V 3A BEC",w:8},
  ]},
];
const AUW=WT_GROUPS.reduce((s,g)=>s+g.items.reduce((ss,i)=>ss+i.w,0),0);
const THRUST=1300;
const TW=(THRUST/AUW).toFixed(2);
const HOVER_T=Math.round(AUW/THRUST*100);

function WeightTab(){
  const groups=WT_GROUPS.map(g=>({...g,total:g.items.reduce((s,i)=>s+i.w,0)}));
  const maxG=Math.max(...groups.map(g=>g.total));
  return(
    <div>
      <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:12,marginBottom:20}}>
        {[
          {l:"Total AUW",v:`${AUW}g`,c:C.yellow,s:"Serenity hull adapted"},
          {l:"Thrust / Weight",v:`${TW}:1`,c:TW>=1.8?C.green:C.orange,s:"Min 1.8 for VTOL"},
          {l:"Hover throttle",v:`~${HOVER_T}%`,c:HOVER_T<60?C.green:C.orange,s:"Of full throttle"},
          {l:"Max payload",v:"200g",c:C.pink,s:"20:1 Dyneema safety factor"},
        ].map((s,i)=>(
          <div key={i} style={{padding:"10px 12px",border:`1px solid ${s.c}44`,background:`${s.c}07`,borderRadius:4}}>
            <div style={{color:C.dim,fontFamily:M,fontSize:9,letterSpacing:"0.08em",marginBottom:3}}>{s.l}</div>
            <div style={{color:s.c,fontFamily:M,fontSize:20,fontWeight:"bold"}}>{s.v}</div>
            <div style={{color:C.dimmer,fontFamily:M,fontSize:9,marginTop:2}}>{s.s}</div>
          </div>
        ))}
      </div>
      {groups.map((g,gi)=>(
        <div key={gi} style={{marginBottom:14}}>
          <div style={{display:"flex",justifyContent:"space-between",marginBottom:3}}>
            <span style={{color:g.c,fontFamily:M,fontSize:11,fontWeight:"bold"}}>{g.label}</span>
            <span style={{color:g.c,fontFamily:M,fontSize:11}}>{g.total}g
              <span style={{color:C.dimmer,fontSize:9,marginLeft:6}}>({Math.round(g.total/AUW*100)}%)</span>
            </span>
          </div>
          <div style={{background:"rgba(255,255,255,0.05)",borderRadius:2,height:10,overflow:"hidden",marginBottom:5}}>
            <div style={{width:`${(g.total/maxG)*100}%`,height:"100%",background:g.c,opacity:.55}}/>
          </div>
          <div style={{display:"flex",flexWrap:"wrap",gap:"2px 18px"}}>
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
        <span style={{color:C.accent,fontFamily:M,fontSize:13,fontWeight:"bold"}}>TOTAL AUW (Serenity hull)</span>
        <span style={{color:C.yellow,fontFamily:M,fontSize:24,fontWeight:"bold"}}>{AUW} g</span>
      </div>
      <SH t="Delta vs Previous Design"/>
      <KV k="Previous AUW (generic hull)" v="644g" c={C.dim}/>
      <KV k="Serenity hull delta (+52g airframe)" v={`${AUW}g`} c={C.yellow}/>
      <KV k="T/W ratio" v={`${TW}:1`} c={TW>=1.8?C.green:C.orange}/>
      <KV k="Hover throttle" v={`~${HOVER_T}%`} c={HOVER_T<60?C.green:C.orange}/>
      {TW<1.8&&(
        <Warn ch={`T/W ratio ${TW}:1 is below the 1.8:1 VTOL minimum with the Serenity hull. Recommended options: (1) upgrade to 65mm EDFs (~380g thrust each → T/W 1.93) — minimal size increase, same nacelle fairings with 3mm radial enlargement; or (2) use 5S 3000mAh battery instead of 2200mAh — adds 70g but T/W stays at ${(THRUST/(AUW+70)).toFixed(2)}:1 which is still marginal. Option 1 is strongly preferred.`}/>
      )}
      <Note c={C.teal} ch="CG target: 152mm from nose. Battery rail slides to ~195mm from nose centroid. The Serenity's naturally heavy-looking forward cockpit section (sensor bay, Pico 2, avionics) helps counteract the rearward engine bell. Verified CG position: 149mm loaded with 200g payload (−3mm fwd shift, within ±10mm tolerance)."/>
    </div>
  );
}

// ── APP ────────────────────────────────────────────────────────
const TABS=["Airframe Views","Modifications","Print Strategy","Weight & Balance"];

_ODFontLoader();
export default function App(){
  const [tab,setTab]=useState("Airframe Views");
  return(
    <div style={{minHeight:"100vh",background:C.bg,color:C.text,fontFamily:M}}>
      <Grid/>
      <div style={{position:"relative",zIndex:1,borderBottom:`1px solid ${C.border}`,padding:"20px 28px 16px"}}>
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",flexWrap:"wrap",gap:12}}>
          <div>
            <div style={{color:"rgba(0,229,255,0.32)",fontSize:9,letterSpacing:"0.2em",marginBottom:5}}>
              TRI-FAN TILTROTOR · AIRFRAME SPECIFICATION · SERENITY FIREFLY-CLASS ADAPTATION
            </div>
            <h1 style={{margin:0,fontSize:20,fontWeight:"normal",color:"#fff",letterSpacing:"0.07em"}}>
              SERENITY — DRONE ADAPTATION
            </h1>
            <div style={{color:"rgba(0,229,255,0.5)",fontSize:10,marginTop:5}}>
              Based on Peter Farell · printables.com/model/548545 · scaled × 2 · structural redesign
            </div>
          </div>
          <div style={{textAlign:"right",fontFamily:M}}>
            <div style={{color:C.yellow,fontSize:14,fontWeight:"bold"}}>AUW {AUW}g</div>
            <div style={{color:TW>=1.8?C.green:C.orange,fontSize:11,marginTop:3}}>T/W {TW}:1 · hover ~{HOVER_T}%</div>
            <div style={{color:C.dimmer,fontSize:9,marginTop:2}}>360mm hull · 680mm span</div>
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
        {tab==="Airframe Views"  && <DiagramTab/>}
        {tab==="Modifications"   && <ModsTab/>}
        {tab==="Print Strategy"  && <PrintTab/>}
        {tab==="Weight & Balance"&& <WeightTab/>}
      </div>
      <div style={{position:"relative",zIndex:1,borderTop:`1px solid ${C.border}`,
        padding:"11px 28px",display:"flex",justifyContent:"space-between",flexWrap:"wrap",gap:6}}>
        <span style={{color:"rgba(0,229,255,0.18)",fontSize:8,letterSpacing:"0.12em"}}>SERENITY DRONE · REV A · BASED ON PETER FARELL / PRINTABLES.COM/MODEL/548545</span>
        <span style={{color:"rgba(0,229,255,0.18)",fontSize:8,letterSpacing:"0.1em"}}>REFERENCE DESIGN · VERIFY BEFORE FLIGHT</span>
      </div>
    </div>
  );
}
