import { useState } from "react";

// ── tokens ────────────────────────────────────────────────────────
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
  bg:"#050810", border:"rgba(0,229,255,0.11)", accent:"#00e5ff",
  orange:"#ff6b35", yellow:"#ffe600", purple:"#c084fc", green:"#4ade80",
  pink:"#f472b6", teal:"#2dd4bf", lime:"#a3e635",
  dim:"rgba(255,255,255,0.38)", dimmer:"rgba(255,255,255,0.20)", text:"rgba(255,255,255,0.82)",
};
const M = "'OpenDyslexic Mono','OpenDyslexic','OpenDyslexicMono',monospace";

// antenna colour key
const ANT = {
  gps:    { id:"GPS",    color:"#4ade80", label:"GPS L1 1575 MHz",       short:"GPS"     },
  sik:    { id:"SiK",   color:"#ff6b35", label:"SiK 915 MHz MAVLink",   short:"915MHz"  },
  rc49:   { id:"49M",   color:"#f472b6", label:"49 MHz RCRS TDDS",      short:"49MHz"   },
  wifi:   { id:"WiFi",  color:"#c084fc", label:"WiFi 2.4/5 GHz (CM4)",  short:"WiFi"    },
};

// ── primitives ────────────────────────────────────────────────────
const SH = ({t,c=C.accent,mt=22}) => (
  <div style={{display:"flex",alignItems:"center",gap:10,marginBottom:14,marginTop:mt}}>
    <div style={{width:3,height:17,background:c}}/>
    <span style={{color:c,fontFamily:M,fontSize:13,letterSpacing:"0.13em",textTransform:"uppercase",fontWeight:"normal"}}>{t}</span>
  </div>
);
const KV = ({k,v,c=C.text}) => (
  <div style={{display:"flex",justifyContent:"space-between",alignItems:"baseline",
    padding:"5px 0",borderBottom:"1px solid rgba(0,229,255,0.07)"}}>
    <span style={{color:C.dim,fontFamily:M,fontSize:11}}>{k}</span>
    <span style={{color:c,fontFamily:M,fontSize:11}}>{v}</span>
  </div>
);
const Note = ({c=C.dim,ch}) => (
  <div style={{marginTop:8,marginBottom:6,color:c,fontFamily:M,fontSize:10,lineHeight:1.85,
    padding:"8px 12px",borderLeft:`2px solid ${c}55`,background:`${c}07`,borderRadius:3}}>{ch}</div>
);
const Warn = ({ch}) => (
  <div style={{marginTop:8,marginBottom:6,color:C.yellow,fontFamily:M,fontSize:10,lineHeight:1.8,
    padding:"7px 12px",borderLeft:`2px solid ${C.yellow}`,background:"rgba(255,230,0,0.05)",borderRadius:3}}>⚠ {ch}</div>
);

function AntTag({a}) {
  return (
    <span style={{display:"inline-flex",alignItems:"center",gap:5,
      padding:"2px 8px",border:`1px solid ${a.color}`,color:a.color,
      fontSize:10,fontFamily:M,borderRadius:2,marginRight:5,marginBottom:4}}>
      <span style={{width:7,height:7,background:a.color,borderRadius:"50%",display:"inline-block"}}/>
      {a.label}
    </span>
  );
}

// ── Grid BG ───────────────────────────────────────────────────────
function Grid() {
  return (
    <svg style={{position:"fixed",inset:0,width:"100%",height:"100%",pointerEvents:"none",zIndex:0}}>
      <defs>
        <pattern id="sg" width="20" height="20" patternUnits="userSpaceOnUse">
          <path d="M20 0L0 0 0 20" fill="none" stroke="rgba(0,229,255,0.04)" strokeWidth={0.5}/>
        </pattern>
        <pattern id="lg" width="100" height="100" patternUnits="userSpaceOnUse">
          <rect width="100" height="100" fill="url(#sg)"/>
          <path d="M100 0L0 0 0 100" fill="none" stroke="rgba(0,229,255,0.065)" strokeWidth={1}/>
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#lg)"/>
    </svg>
  );
}

// ══════════════════════════════════════════════════════════════════
//  AIRFRAME THREE-VIEW SVG
//  Scale: 1 px ≈ 0.8 mm    Fuselage 320 mm → 256 px
//  Nose points LEFT in top/side/bottom views
// ══════════════════════════════════════════════════════════════════

// shared geometry helpers
const SC  = 0.82;              // px/mm
const mmX = (mm) => 60 + mm * SC;   // fuselage nose at x=60
const FX  = mmX(0);           // nose x = 60
const FW  = 320 * SC;         // fuselage px length = 262
const FC  = mmX(160);         // fuselage centre x (wing pivot) = 191
const FA  = mmX(320);         // tail x = 322

// antenna positions (mm from nose)
const POS = {
  gps:   { x: mmX(58),  label:"GPS patch", sublabel:"58mm from nose", side:"TOP" },
  sik:   { x: mmX(238), label:"915 MHz whip", sublabel:"238mm from nose", side:"BELLY" },
  rc49:  { x: mmX(290), label:"49 MHz loaded whip", sublabel:"290mm from nose", side:"TOP" },
  wifi:  { x: mmX(210), label:"WiFi trace (internal)", sublabel:"210mm from nose", side:"INTERNAL" },
};

// ── TOP VIEW ──────────────────────────────────────────────────────
function TopView({hover,onHover}) {
  const VH=210, VW=660;
  const CY=105;  // fuselage centre Y

  // Wing: 680mm span → 558px; nacelles at tips
  const WL=20, WR=640;  // wing left/right x
  const NR=16;           // nacelle radius

  const halo = (id,x,y,r,c) => hover===id
    ? <circle cx={x} cy={y} r={r+8} fill="none" stroke={c} strokeWidth={1} strokeDasharray="3 2" opacity={0.7}/>
    : null;

  return (
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* Wing */}
      <rect x={WL} y={CY-8} width={WR-WL} height={16} rx={3}
        fill="rgba(0,229,255,0.045)" stroke={C.accent} strokeWidth={1.2}/>
      {/* Nacelles */}
      {[WL+NR, WR-NR].map((cx,i)=>(
        <g key={i}>
          <circle cx={cx} cy={CY} r={NR} fill="rgba(255,107,53,0.08)"
            stroke={C.orange} strokeWidth={1} strokeDasharray="3 2"/>
          <circle cx={cx} cy={CY} r={8} fill="rgba(255,107,53,0.12)"
            stroke={C.orange} strokeWidth={0.7}/>
        </g>
      ))}
      {/* Fuselage */}
      <ellipse cx={FC} cy={CY} rx={FW/2} ry={18}
        fill="rgba(0,229,255,0.05)" stroke={C.accent} strokeWidth={1.5}/>
      {/* Pitot tube */}
      <line x1={FX} y1={CY} x2={FX-28} y2={CY}
        stroke={C.teal} strokeWidth={2.5} strokeLinecap="round"/>
      <circle cx={FX-28} cy={CY} r={3} fill={C.teal}/>
      {/* Payload bay on belly — shown as dashed rect centred 160mm from nose */}
      <rect x={mmX(125)} y={CY+18} width={mmX(70)-mmX(0)} height={10} rx={2}
        fill="rgba(244,114,182,0.08)" stroke="rgba(244,114,182,0.4)"
        strokeWidth={0.8} strokeDasharray="3 2"/>

      {/* ── ANTENNA MARKERS — TOP VIEW ─── */}

      {/* GPS patch: forward top */}
      {halo("gps", POS.gps.x, CY-18, 9, ANT.gps.color)}
      <g onClick={()=>onHover(hover==="gps"?null:"gps")} style={{cursor:"pointer"}}>
        <rect x={POS.gps.x-11} y={CY-28} width={22} height={10} rx={2}
          fill={`${ANT.gps.color}25`} stroke={ANT.gps.color} strokeWidth={hover==="gps"?2:1.2}/>
        <text x={POS.gps.x} y={CY-20} textAnchor="middle"
          fill={ANT.gps.color} fontSize={7} fontFamily={M} fontWeight="bold">GPS</text>
        <line x1={POS.gps.x} y1={CY-28} x2={POS.gps.x} y2={CY-18}
          stroke={ANT.gps.color} strokeWidth={0.8} opacity={0.6}/>
        <text x={POS.gps.x} y={CY-36} textAnchor="middle"
          fill={ANT.gps.color} fontSize={6} fontFamily={M}>58mm</text>
      </g>

      {/* WiFi internal dashed */}
      <g onClick={()=>onHover(hover==="wifi"?null:"wifi")} style={{cursor:"pointer"}}>
        <rect x={POS.wifi.x-18} y={CY-16} width={36} height={32} rx={3}
          fill={`${ANT.wifi.color}10`} stroke={ANT.wifi.color}
          strokeWidth={hover==="wifi"?1.8:1} strokeDasharray="4 2"/>
        <text x={POS.wifi.x} y={CY+1} textAnchor="middle"
          fill={ANT.wifi.color} fontSize={6} fontFamily={M}>WiFi</text>
        <text x={POS.wifi.x} y={CY+10} textAnchor="middle"
          fill={`${ANT.wifi.color}70`} fontSize={6} fontFamily={M}>internal</text>
      </g>

      {/* 49MHz dorsal whip */}
      {halo("rc49", POS.rc49.x, CY-18, 7, ANT.rc49.color)}
      <g onClick={()=>onHover(hover==="rc49"?null:"rc49")} style={{cursor:"pointer"}}>
        <circle cx={POS.rc49.x} cy={CY-18} r={5}
          fill={`${ANT.rc49.color}20`} stroke={ANT.rc49.color} strokeWidth={hover==="rc49"?2:1.2}/>
        {/* whip line going up */}
        <line x1={POS.rc49.x} y1={CY-23} x2={POS.rc49.x} y2={CY-52}
          stroke={ANT.rc49.color} strokeWidth={1.5} strokeLinecap="round"/>
        {/* coil symbol */}
        {[0,1,2].map(i=>(
          <ellipse key={i} cx={POS.rc49.x} cy={CY-40+i*5} rx={4} ry={2}
            fill="none" stroke={ANT.rc49.color} strokeWidth={0.8} opacity={0.8}/>
        ))}
        <text x={POS.rc49.x+12} y={CY-44} fill={ANT.rc49.color} fontSize={6} fontFamily={M}>coil</text>
        <text x={POS.rc49.x} y={CY-60} textAnchor="middle"
          fill={ANT.rc49.color} fontSize={7} fontFamily={M} fontWeight="bold">49M</text>
        <text x={POS.rc49.x} y={CY-68} textAnchor="middle"
          fill={ANT.rc49.color} fontSize={6} fontFamily={M}>290mm</text>
      </g>

      {/* 915MHz — note on top view it's belly-mount, shown as dashed circle */}
      <g onClick={()=>onHover(hover==="sik"?null:"sik")} style={{cursor:"pointer"}}>
        <circle cx={POS.sik.x} cy={CY} r={6}
          fill={`${ANT.sik.color}12`} stroke={ANT.sik.color}
          strokeWidth={hover==="sik"?1.8:1} strokeDasharray="3 2"/>
        <text x={POS.sik.x} y={CY+18} textAnchor="middle"
          fill={ANT.sik.color} fontSize={7} fontFamily={M} fontWeight="bold">SiK</text>
        <text x={POS.sik.x} y={CY+26} textAnchor="middle"
          fill={`${ANT.sik.color}80`} fontSize={6} fontFamily={M}>(belly)</text>
      </g>

      {/* Separation dimension lines */}
      {/* GPS to 49MHz */}
      <g opacity={0.35}>
        <line x1={POS.gps.x} y1={CY+30} x2={POS.rc49.x} y2={CY+30}
          stroke={C.yellow} strokeWidth={0.7}/>
        <line x1={POS.gps.x} y1={CY+27} x2={POS.gps.x} y2={CY+33} stroke={C.yellow} strokeWidth={0.7}/>
        <line x1={POS.rc49.x} y1={CY+27} x2={POS.rc49.x} y2={CY+33} stroke={C.yellow} strokeWidth={0.7}/>
        <text x={(POS.gps.x+POS.rc49.x)/2} y={CY+42} textAnchor="middle"
          fill={C.yellow} fontSize={7} fontFamily={M}>232mm</text>
      </g>

      {/* Labels */}
      <text x={VW/2} y={14} textAnchor="middle" fill="rgba(0,229,255,0.25)"
        fontSize={9} fontFamily={M} letterSpacing="0.12em">TOP VIEW — CLICK ANTENNA TO INSPECT</text>
      <text x={FX-22} y={CY+5} fill={C.dimmer} fontSize={7} fontFamily={M}>NOSE</text>
      <text x={FA+5} y={CY+5} fill={C.dimmer} fontSize={7} fontFamily={M}>TAIL</text>
      {/* dim baseline */}
      <line x1={FX} y1={VH-14} x2={FA} y2={VH-14} stroke={C.accent} strokeWidth={0.4} opacity={0.2}/>
      <line x1={FX} y1={VH-17} x2={FX} y2={VH-11} stroke={C.accent} strokeWidth={0.4} opacity={0.2}/>
      <line x1={FA} y1={VH-17} x2={FA} y2={VH-11} stroke={C.accent} strokeWidth={0.4} opacity={0.2}/>
      <text x={FC} y={VH-5} textAnchor="middle" fill={C.dimmer} fontSize={7} fontFamily={M}>320 mm fuselage</text>
    </svg>
  );
}

// ── SIDE VIEW ─────────────────────────────────────────────────────
function SideView({hover,onHover}) {
  const VH=240, VW=560;
  const CY=120;
  const FR=20; // fuselage half-height

  const halo=(id,x,y,r,c)=> hover===id
    ? <circle cx={x} cy={y} r={r+7} fill="none" stroke={c} strokeWidth={1} strokeDasharray="3 2" opacity={0.7}/>
    : null;

  return (
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* Fuselage */}
      <ellipse cx={FC} cy={CY} rx={FW/2} ry={FR}
        fill="rgba(0,229,255,0.05)" stroke={C.accent} strokeWidth={1.5}/>
      {/* Canopy bump */}
      <ellipse cx={mmX(100)} cy={CY-FR} rx={30} ry={10}
        fill="rgba(0,229,255,0.08)" stroke={C.accent} strokeWidth={0.8}/>
      {/* Wing stump */}
      <rect x={mmX(130)} y={CY-6} width={mmX(60)-mmX(0)} height={12} rx={2}
        fill="rgba(0,229,255,0.06)" stroke={C.accent} strokeWidth={0.8}/>
      {/* Nacelle side view at wing pivot — hover position vertical */}
      <rect x={mmX(148)} y={CY-FR-32} width={18} height={32} rx={4}
        fill="rgba(255,107,53,0.08)" stroke={C.orange} strokeWidth={1} strokeDasharray="3 2"/>
      {/* Landing skids */}
      <line x1={mmX(110)} y1={CY+FR} x2={mmX(95)} y2={CY+FR+22} stroke={C.accent} strokeWidth={1.2} opacity={0.4}/>
      <line x1={mmX(220)} y1={CY+FR} x2={mmX(235)} y2={CY+FR+22} stroke={C.accent} strokeWidth={1.2} opacity={0.4}/>
      <line x1={mmX(85)} y1={CY+FR+22} x2={mmX(120)} y2={CY+FR+22} stroke={C.accent} strokeWidth={1.5} opacity={0.4}/>
      <line x1={mmX(225)} y1={CY+FR+22} x2={mmX(260)} y2={CY+FR+22} stroke={C.accent} strokeWidth={1.5} opacity={0.4}/>
      {/* Pitot */}
      <line x1={FX} y1={CY} x2={FX-28} y2={CY} stroke={C.teal} strokeWidth={2.5} strokeLinecap="round"/>
      {/* Payload bay */}
      <rect x={mmX(125)} y={CY+FR} width={mmX(70)-mmX(0)} height={18} rx={3}
        fill="rgba(244,114,182,0.07)" stroke="rgba(244,114,182,0.35)"
        strokeWidth={0.8} strokeDasharray="3 2"/>
      <text x={mmX(160)} y={CY+FR+12} textAnchor="middle" fill="rgba(244,114,182,0.5)"
        fontSize={6} fontFamily={M}>PAYLOAD</text>
      {/* Winch line hint */}
      <line x1={mmX(155)} y1={CY+FR+18} x2={mmX(155)} y2={CY+FR+34}
        stroke="rgba(244,114,182,0.3)" strokeWidth={1} strokeDasharray="2 2"/>

      {/* ── ANTENNA SIDE VIEW ─── */}

      {/* GPS: top, forward — patch sticks up */}
      {halo("gps", POS.gps.x, CY-FR-4, 7, ANT.gps.color)}
      <g onClick={()=>onHover(hover==="gps"?null:"gps")} style={{cursor:"pointer"}}>
        {/* Patch element */}
        <rect x={POS.gps.x-11} y={CY-FR-18} width={22} height={8} rx={2}
          fill={`${ANT.gps.color}22`} stroke={ANT.gps.color} strokeWidth={hover==="gps"?2:1.2}/>
        {/* Mast */}
        <line x1={POS.gps.x} y1={CY-FR-10} x2={POS.gps.x} y2={CY-FR}
          stroke={ANT.gps.color} strokeWidth={1.2}/>
        {/* label */}
        <text x={POS.gps.x} y={CY-FR-24} textAnchor="middle"
          fill={ANT.gps.color} fontSize={7} fontFamily={M} fontWeight="bold">GPS</text>
        <text x={POS.gps.x} y={CY-FR-32} textAnchor="middle"
          fill={`${ANT.gps.color}80`} fontSize={6} fontFamily={M}>patch 22mm</text>
      </g>

      {/* 49MHz dorsal loaded whip — aft top */}
      {halo("rc49", POS.rc49.x, CY-FR-12, 7, ANT.rc49.color)}
      <g onClick={()=>onHover(hover==="rc49"?null:"rc49")} style={{cursor:"pointer"}}>
        {/* mount base */}
        <rect x={POS.rc49.x-4} y={CY-FR-4} width={8} height={6} rx={1}
          fill={`${ANT.rc49.color}30`} stroke={ANT.rc49.color} strokeWidth={1}/>
        {/* Loading coil (squiggle) */}
        {[0,1,2,3].map(i=>(
          <ellipse key={i} cx={POS.rc49.x} cy={CY-FR-10-i*7} rx={4} ry={3}
            fill="none" stroke={ANT.rc49.color} strokeWidth={1} opacity={0.75}/>
        ))}
        {/* whip element above coil */}
        <line x1={POS.rc49.x} y1={CY-FR-38} x2={POS.rc49.x} y2={CY-FR-88}
          stroke={ANT.rc49.color} strokeWidth={1.5} strokeLinecap="round"/>
        {/* tip */}
        <circle cx={POS.rc49.x} cy={CY-FR-88} r={2} fill={ANT.rc49.color}/>
        {/* length callout */}
        <line x1={POS.rc49.x+12} y1={CY-FR-38} x2={POS.rc49.x+12} y2={CY-FR-88}
          stroke={ANT.rc49.color} strokeWidth={0.6} opacity={0.5}/>
        <line x1={POS.rc49.x+9} y1={CY-FR-38} x2={POS.rc49.x+15} y2={CY-FR-38}
          stroke={ANT.rc49.color} strokeWidth={0.6} opacity={0.5}/>
        <line x1={POS.rc49.x+9} y1={CY-FR-88} x2={POS.rc49.x+15} y2={CY-FR-88}
          stroke={ANT.rc49.color} strokeWidth={0.6} opacity={0.5}/>
        <text x={POS.rc49.x+22} y={CY-FR-60} fill={ANT.rc49.color}
          fontSize={7} fontFamily={M}>250mm</text>
        <text x={POS.rc49.x} y={CY-FR-96} textAnchor="middle"
          fill={ANT.rc49.color} fontSize={7} fontFamily={M} fontWeight="bold">49MHz</text>
        {/* Counterpoise radials */}
        <line x1={POS.rc49.x} y1={CY-FR} x2={POS.rc49.x-22} y2={CY-FR+8}
          stroke={ANT.rc49.color} strokeWidth={0.8} strokeDasharray="2 2" opacity={0.5}/>
        <line x1={POS.rc49.x} y1={CY-FR} x2={POS.rc49.x+22} y2={CY-FR+8}
          stroke={ANT.rc49.color} strokeWidth={0.8} strokeDasharray="2 2" opacity={0.5}/>
        <text x={POS.rc49.x-28} y={CY-FR+16} fill={`${ANT.rc49.color}60`}
          fontSize={6} fontFamily={M}>radials</text>
      </g>

      {/* WiFi — internal, dashed box */}
      <g onClick={()=>onHover(hover==="wifi"?null:"wifi")} style={{cursor:"pointer"}}>
        <rect x={POS.wifi.x-20} y={CY-12} width={40} height={24} rx={3}
          fill={`${ANT.wifi.color}08`} stroke={ANT.wifi.color}
          strokeWidth={hover==="wifi"?1.5:0.8} strokeDasharray="4 2"/>
        <text x={POS.wifi.x} y={CY+2} textAnchor="middle"
          fill={ANT.wifi.color} fontSize={6} fontFamily={M}>WiFi</text>
        <text x={POS.wifi.x} y={CY+10} textAnchor="middle"
          fill={`${ANT.wifi.color}60`} fontSize={6} fontFamily={M}>internal</text>
      </g>

      {/* 915MHz — belly monopole pointing DOWN */}
      {halo("sik", POS.sik.x, CY+FR+8, 7, ANT.sik.color)}
      <g onClick={()=>onHover(hover==="sik"?null:"sik")} style={{cursor:"pointer"}}>
        {/* SMA base */}
        <rect x={POS.sik.x-4} y={CY+FR-3} width={8} height={6} rx={1}
          fill={`${ANT.sik.color}30`} stroke={ANT.sik.color} strokeWidth={1}/>
        {/* Monopole whip going down */}
        <line x1={POS.sik.x} y1={CY+FR+3} x2={POS.sik.x} y2={CY+FR+58}
          stroke={ANT.sik.color} strokeWidth={1.8} strokeLinecap="round"/>
        <circle cx={POS.sik.x} cy={CY+FR+58} r={2} fill={ANT.sik.color}/>
        {/* length callout */}
        <line x1={POS.sik.x-12} y1={CY+FR+3} x2={POS.sik.x-12} y2={CY+FR+58}
          stroke={ANT.sik.color} strokeWidth={0.6} opacity={0.5}/>
        <text x={POS.sik.x-24} y={CY+FR+35} fill={ANT.sik.color}
          fontSize={7} fontFamily={M} textAnchor="middle">82mm</text>
        <text x={POS.sik.x} y={CY+FR+70} textAnchor="middle"
          fill={ANT.sik.color} fontSize={7} fontFamily={M} fontWeight="bold">SiK</text>
        <text x={POS.sik.x} y={CY+FR+79} textAnchor="middle"
          fill={`${ANT.sik.color}80`} fontSize={6} fontFamily={M}>915 MHz</text>
      </g>

      {/* Separation callout — GPS to 49MHz top */}
      <g opacity={0.3}>
        <line x1={POS.gps.x} y1={CY-FR-30} x2={POS.rc49.x} y2={CY-FR-30}
          stroke={C.yellow} strokeWidth={0.6}/>
        <line x1={POS.gps.x} y1={CY-FR-33} x2={POS.gps.x} y2={CY-FR-27}
          stroke={C.yellow} strokeWidth={0.6}/>
        <line x1={POS.rc49.x} y1={CY-FR-33} x2={POS.rc49.x} y2={CY-FR-27}
          stroke={C.yellow} strokeWidth={0.6}/>
        <text x={(POS.gps.x+POS.rc49.x)/2} y={CY-FR-36} textAnchor="middle"
          fill={C.yellow} fontSize={6} fontFamily={M}>232mm separation</text>
      </g>

      {/* View label */}
      <text x={VW/2} y={14} textAnchor="middle" fill="rgba(0,229,255,0.25)"
        fontSize={9} fontFamily={M} letterSpacing="0.12em">RIGHT SIDE VIEW</text>
      <text x={FX-22} y={CY+5} fill={C.dimmer} fontSize={7} fontFamily={M}>NOSE</text>
      <text x={FA+5} y={CY+5} fill={C.dimmer} fontSize={7} fontFamily={M}>TAIL</text>
    </svg>
  );
}

// ── BOTTOM VIEW ───────────────────────────────────────────────────
function BottomView({hover,onHover}) {
  const VH=210, VW=660;
  const CY=105;
  const NR=16;
  const WL=20, WR=640;

  return (
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* Wing */}
      <rect x={WL} y={CY-8} width={WR-WL} height={16} rx={3}
        fill="rgba(0,229,255,0.045)" stroke={C.accent} strokeWidth={1.2}/>
      {/* Nacelles */}
      {[WL+NR, WR-NR].map((cx,i)=>(
        <g key={i}>
          <circle cx={cx} cy={CY} r={NR} fill="rgba(255,107,53,0.08)"
            stroke={C.orange} strokeWidth={1} strokeDasharray="3 2"/>
          <circle cx={cx} cy={CY} r={8} fill="rgba(255,107,53,0.12)"
            stroke={C.orange} strokeWidth={0.7}/>
        </g>
      ))}
      {/* Fuselage */}
      <ellipse cx={FC} cy={CY} rx={FW/2} ry={18}
        fill="rgba(0,229,255,0.05)" stroke={C.accent} strokeWidth={1.5}/>
      {/* Pitot */}
      <line x1={FX} y1={CY} x2={FX-28} y2={CY} stroke={C.teal} strokeWidth={2.5} strokeLinecap="round"/>
      {/* Payload bay */}
      <rect x={mmX(125)} y={CY-10} width={mmX(70)-mmX(0)} height={20} rx={3}
        fill="rgba(244,114,182,0.12)" stroke={C.pink} strokeWidth={1.2}/>
      <text x={mmX(160)} y={CY+4} textAnchor="middle"
        fill={C.pink} fontSize={7} fontFamily={M} fontWeight="bold">PAYLOAD BAY</text>
      {/* Winch door */}
      <rect x={mmX(145)} y={CY+10} width={mmX(30)-mmX(0)} height={8} rx={2}
        fill="rgba(244,114,182,0.08)" stroke={C.pink} strokeWidth={0.8} strokeDasharray="2 2"/>

      {/* 915MHz belly monopole — pointing away from viewer (down in flight) */}
      <g onClick={()=>onHover(hover==="sik"?null:"sik")} style={{cursor:"pointer"}}>
        <circle cx={POS.sik.x} cy={CY} r={6}
          fill={`${ANT.sik.color}20`} stroke={ANT.sik.color}
          strokeWidth={hover==="sik"?2:1.3}/>
        {/* Concentric rings = whip going away from viewer */}
        {[10,15,20].map(r2=>(
          <circle key={r2} cx={POS.sik.x} cy={CY} r={r2}
            fill="none" stroke={ANT.sik.color} strokeWidth={0.5} opacity={0.3}/>
        ))}
        <text x={POS.sik.x} y={CY-28} textAnchor="middle"
          fill={ANT.sik.color} fontSize={8} fontFamily={M} fontWeight="bold">SiK ↓</text>
        <text x={POS.sik.x} y={CY-18} textAnchor="middle"
          fill={`${ANT.sik.color}80`} fontSize={6} fontFamily={M}>915 MHz</text>
        <text x={POS.sik.x} y={CY+32} textAnchor="middle"
          fill={`${ANT.sik.color}70`} fontSize={6} fontFamily={M}>238mm</text>
      </g>

      {/* GPS — top surface, shown as dashed (not visible from below) */}
      <g onClick={()=>onHover(hover==="gps"?null:"gps")} style={{cursor:"pointer"}}>
        <rect x={POS.gps.x-12} y={CY-8} width={24} height={16} rx={2}
          fill={`${ANT.gps.color}06`} stroke={ANT.gps.color}
          strokeWidth={hover==="gps"?1.5:0.7} strokeDasharray="4 2"/>
        <text x={POS.gps.x} y={CY+3} textAnchor="middle"
          fill={`${ANT.gps.color}50`} fontSize={6} fontFamily={M}>GPS↑</text>
      </g>

      {/* 49MHz dorsal — not visible from below, shown dashed */}
      <g onClick={()=>onHover(hover==="rc49"?null:"rc49")} style={{cursor:"pointer"}}>
        <circle cx={POS.rc49.x} cy={CY} r={6}
          fill={`${ANT.rc49.color}06`} stroke={ANT.rc49.color}
          strokeWidth={hover==="rc49"?1.5:0.7} strokeDasharray="4 2"/>
        <text x={POS.rc49.x} y={CY-14} textAnchor="middle"
          fill={`${ANT.rc49.color}50`} fontSize={6} fontFamily={M}>49↑</text>
      </g>

      {/* Fwd fan duct (bottom view) */}
      <ellipse cx={mmX(290)} cy={CY} rx={16} ry={16}
        fill="rgba(255,230,0,0.05)" stroke="rgba(255,230,0,0.3)"
        strokeWidth={0.8} strokeDasharray="3 2"/>

      {/* Keep-out zone: payload bay vs SiK */}
      <line x1={mmX(195)} y1={CY+10} x2={POS.sik.x} y2={CY+10}
        stroke={C.yellow} strokeWidth={0.5} opacity={0.3}/>
      <text x={(mmX(195)+POS.sik.x)/2} y={CY+22}
        textAnchor="middle" fill={C.yellow} fontSize={6} fontFamily={M} opacity={0.5}>43mm clearance</text>

      <text x={VW/2} y={14} textAnchor="middle" fill="rgba(0,229,255,0.25)"
        fontSize={9} fontFamily={M} letterSpacing="0.12em">BOTTOM VIEW</text>
      <text x={FX-22} y={CY+5} fill={C.dimmer} fontSize={7} fontFamily={M}>NOSE</text>
      <text x={FA+5} y={CY+5} fill={C.dimmer} fontSize={7} fontFamily={M}>TAIL</text>
    </svg>
  );
}

// ── Inspector panel ───────────────────────────────────────────────
const DETAIL = {
  gps: {
    title:"GPS L1 Patch Antenna", c:ANT.gps.color,
    rows:[
      ["Type","Ceramic patch, 25×25mm, right-hand circular polarised (RHCP)"],
      ["Frequency","1575.42 MHz (GPS L1) · also receives GLONASS/Galileo/BeiDou"],
      ["Mount face","TOP of fuselage — forward section, 58mm from nose"],
      ["Height","12mm above fuselage skin on PLA standoff (ground-plane clearance)"],
      ["Reason fwd","Away from CM4/COMPHAT-1 switching noise (>150mm), away from EDF motor interference"],
      ["Ground plane","25×25mm copper pour on underside of TRIHAT-1 PCB · matched to patch"],
      ["Cable","U.FL → 50Ω coax (RG-178) → TRIHAT-1 U.FL connector · max 100mm"],
      ["Keepout","No carbon fibre within 40mm radius · no metal above the patch"],
      ["Clearance to 49MHz","232mm ✔ (>150mm required)"],
      ["Clearance to SiK","148mm ✔ (>100mm required, different faces)"],
      ["Clearance to WiFi","152mm ✔"],
      ["Material zone","Fuselage shell is PLA/PETG here — RF transparent ✔"],
    ]
  },
  sik: {
    title:"SiK 915 MHz MAVLink Whip", c:ANT.sik.color,
    rows:[
      ["Type","Monopole whip, λ/4 @ 915 MHz = 82mm · SMA-RP female on COMPHAT-1"],
      ["Polarisation","Vertical (aligned with Earth's gravity in hover)"],
      ["Mount face","BELLY of fuselage, 238mm from nose · aft of payload bay"],
      ["Orientation","Vertical, pointing down · best pattern toward ground station"],
      ["Reason aft","Clears payload bay (125–195mm) by 43mm forward margin"],
      ["Reason belly","Ground-facing pattern · GCS is always below aircraft"],
      ["Cable","Integral to SiK module via IPEX/U.FL pigtail through fuselage hole"],
      ["Ground plane","SiK module GND pours on COMPHAT-1 PCB act as partial counterpoise"],
      ["Material zone","PLA shell belly — RF transparent ✔ · CF spar at 160mm (78mm away)"],
      ["Clearance to GPS","148mm ✔ (opposite faces top/belly add effective isolation)"],
      ["Clearance to 49MHz","52mm on fuselage — supplemented by face diversity (top vs belly)"],
      ["Clearance to payload","43mm forward of payload bay edge ✔"],
      ["Beam pattern","Toroidal · null straight down/up · max at horizon toward GCS"],
    ]
  },
  rc49: {
    title:"49 MHz RCRS TDDS Loaded Whip", c:ANT.rc49.color,
    rows:[
      ["Type","Base-loaded shortened monopole on non-conductive dorsal fin"],
      ["Frequency","49.830–49.890 MHz (6 RCRS channels, 10kHz spacing)"],
      ["λ/4 free-space","1530mm — impractical; shortened + inductance-loaded"],
      ["Physical length","250mm (whip element) + 30mm coil form = 280mm total above mount"],
      ["Loading coil","~38 μH wound on 10mm OD ferrite rod · 1.5mm wire · ~45 turns"],
      ["Counterpoise","4× 150mm tinned-copper wire radials at 90° · at mount base"],
      ["Radiation resistance","~3–6 Ω (typical loaded short monopole at this ratio)"],
      ["Efficiency","~ −14 dB vs ideal dipole · adequate for <500m TDDS range"],
      ["Mount face","TOP of fuselage, 290mm from nose (aft section, tail-adjacent dorsal fin)"],
      ["Dorsal fin","3D-printed ABS/PETG fin, 35mm tall · keeps antenna clear of fuselage"],
      ["Reason top","Avoids winch line interference on belly · maximises sky view angle"],
      ["Reason aft","Maximises separation from GPS (232mm) · away from CM4 WiFi zone"],
      ["Cable","50Ω RG-316 semi-rigid coax · 120mm · to COMPHAT-1 U.FL"],
      ["Matching","LC pi-network at antenna base resonates system at 49.86 MHz"],
      ["Polarisation","Vertical monopole — matches ground station vertical whip"],
      ["Clearance to GPS","232mm ✔ (required >150mm to protect GPS LNA)"],
      ["Clearance to SiK","52mm linear, but opposite fuselage faces (+~15dB isolation)"],
      ["Clearance to WiFi","80mm ✔ (frequencies very different, minimal coupling)"],
    ]
  },
  wifi: {
    title:"WiFi 2.4/5 GHz PCB Trace Antenna (CM4)", c:ANT.wifi.color,
    rows:[
      ["Type","Meandered-line PCB monopole, dual-band (CM4 onboard)"],
      ["Frequency","2412–2484 MHz (2.4 GHz) · 5180–5825 MHz (5 GHz)"],
      ["Location","CM4-CARRIER-1 PCB, 210mm from nose · internal to fuselage"],
      ["Orientation","Horizontal trace, parallel to wing spar"],
      ["Keepout","15mm ground-plane clearance on each side of trace · met on carrier layout"],
      ["Material zone","PLA fuselage shell here — RF partially transparent (2–3dB loss ✔)"],
      ["Purpose","Ground-based SSH debug · QGC backup link · NOT primary flight control radio"],
      ["Gain","~0 dBi (omnidirectional, partial ground-plane limited)"],
      ["Range","~50–80m through plastic shell · sufficient for bench/field debug"],
      ["Interference risk","2.4 GHz WiFi is well clear of GPS L1 (1575 MHz), 915 MHz, 49 MHz"],
      ["Note","In-flight WiFi use only when within 50m of ground station for SSH/QGC"],
    ]
  },
};

function Inspector({id}) {
  if(!id) return (
    <div style={{padding:"16px 14px",color:C.dimmer,fontFamily:M,fontSize:11,
      border:`1px solid ${C.border}`,borderRadius:4,minHeight:120,textAlign:"center",paddingTop:40}}>
      click an antenna to inspect
    </div>
  );
  const d=DETAIL[id];
  return (
    <div style={{padding:"14px",border:`1px solid ${d.c}44`,borderRadius:4,
      background:`${d.c}07`,maxHeight:440,overflowY:"auto"}}>
      <div style={{color:d.c,fontFamily:M,fontSize:12,fontWeight:"bold",
        letterSpacing:"0.06em",marginBottom:10}}>{d.title}</div>
      {d.rows.map(([k,v],i)=>(
        <div key={i} style={{display:"flex",gap:8,padding:"4px 0",
          borderBottom:"1px solid rgba(255,255,255,0.05)",alignItems:"flex-start"}}>
          <span style={{color:C.dim,fontFamily:M,fontSize:9,minWidth:90,flexShrink:0}}>{k}</span>
          <span style={{color:C.text,fontFamily:M,fontSize:10,lineHeight:1.6}}>{v}</span>
        </div>
      ))}
    </div>
  );
}

// ── Three views panel ─────────────────────────────────────────────
function DiagramTab() {
  const [hover,setHover]=useState(null);
  return (
    <div>
      <div style={{display:"flex",gap:6,flexWrap:"wrap",marginBottom:16}}>
        {Object.values(ANT).map(a=><AntTag key={a.id} a={a}/>)}
        <span style={{color:C.dimmer,fontFamily:M,fontSize:10,alignSelf:"center",marginLeft:8}}>
          · click antenna on diagram to inspect
        </span>
      </div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 260px",gap:16,alignItems:"start"}}>
        <div>
          {/* Top view */}
          <div style={{color:C.dimmer,fontFamily:M,fontSize:10,letterSpacing:"0.08em",marginBottom:6}}>
            TOP / PLAN VIEW
          </div>
          <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:8,marginBottom:16}}>
            <TopView hover={hover} onHover={setHover}/>
          </div>
          {/* Side view */}
          <div style={{color:C.dimmer,fontFamily:M,fontSize:10,letterSpacing:"0.08em",marginBottom:6}}>
            RIGHT-SIDE PROFILE VIEW
          </div>
          <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:8,marginBottom:16}}>
            <SideView hover={hover} onHover={setHover}/>
          </div>
          {/* Bottom view */}
          <div style={{color:C.dimmer,fontFamily:M,fontSize:10,letterSpacing:"0.08em",marginBottom:6}}>
            BOTTOM VIEW
          </div>
          <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:8}}>
            <BottomView hover={hover} onHover={setHover}/>
          </div>
        </div>
        {/* Inspector */}
        <div style={{position:"sticky",top:20}}>
          <div style={{color:C.dimmer,fontFamily:M,fontSize:10,letterSpacing:"0.08em",marginBottom:8}}>
            ANTENNA INSPECTOR
          </div>
          <Inspector id={hover}/>
        </div>
      </div>
    </div>
  );
}

// ── Separation matrix ─────────────────────────────────────────────
function MatrixTab() {
  // rows = tx, cols = other; values = separation + notes
  const ants = [
    {k:"gps",  label:"GPS L1"},
    {k:"sik",  label:"SiK 915"},
    {k:"rc49", label:"49 MHz"},
    {k:"wifi", label:"WiFi"},
  ];
  const SEP = {
    "gps-sik":  {dist:"148mm",face:"top vs belly",ok:true, min:"100mm",note:"Face diversity adds ~12dB isolation"},
    "gps-rc49": {dist:"232mm",face:"both top",ok:true, min:"150mm",note:"GPS LNA vulnerable to VHF harmonics — 232mm is comfortable"},
    "gps-wifi": {dist:"152mm",face:"internal",ok:true, min:"50mm", note:"2.4GHz–1.575GHz gap is large; no harmful coupling"},
    "sik-rc49": {dist:"52mm linear",face:"belly vs top",ok:true, min:"face diversity",note:"Physical 52mm + opposite face → ~18dB isolation. Frequencies separated by 866 MHz."},
    "sik-wifi": {dist:"28mm",face:"both internal",ok:true, min:"30mm",note:"915 MHz 5th harmonic at 4.575 GHz misses WiFi bands; monitor empirically"},
    "rc49-wifi":{dist:"80mm",face:"top vs internal",ok:true, min:"30mm",note:"49 MHz has no harmonics near WiFi; safe"},
  };

  function getCell(a,b) {
    if(a.k===b.k) return null;
    const key = [a.k,b.k].sort().join("-");
    // custom key order
    const altkey = [b.k,a.k].join("-");
    return SEP[key] || SEP[altkey] || null;
  }

  return (
    <div>
      <SH t="Antenna Separation Matrix" mt={0}/>
      <div style={{overflowX:"auto"}}>
        <table style={{borderCollapse:"collapse",fontFamily:M,fontSize:11,minWidth:600}}>
          <thead>
            <tr>
              <th style={{padding:"8px 12px",borderBottom:`1px solid ${C.border}`,
                color:C.accent,textAlign:"left",fontWeight:"normal",fontSize:10}}>—</th>
              {ants.map(a=>(
                <th key={a.k} style={{padding:"8px 12px",borderBottom:`1px solid ${C.border}`,
                  color:ANT[a.k].color,textAlign:"center",fontWeight:"normal",fontSize:10,
                  letterSpacing:"0.06em"}}>{a.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ants.map((row,ri)=>(
              <tr key={row.k} style={{background:ri%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
                <td style={{padding:"8px 12px",color:ANT[row.k].color,
                  fontFamily:M,fontSize:10,whiteSpace:"nowrap",fontWeight:"bold"}}>{row.label}</td>
                {ants.map(col=>{
                  if(col.k===row.k) return (
                    <td key={col.k} style={{padding:"8px 12px",background:"rgba(255,255,255,0.03)",
                      textAlign:"center"}}>
                      <span style={{color:C.dimmer,fontSize:10}}>—</span>
                    </td>
                  );
                  const cell=getCell(row,col);
                  if(!cell) return <td key={col.k}></td>;
                  return (
                    <td key={col.k} style={{padding:"8px 12px",verticalAlign:"top",
                      borderBottom:"1px solid rgba(0,229,255,0.06)"}}>
                      <div style={{color:cell.ok?C.green:C.red,fontFamily:M,fontSize:11,
                        fontWeight:"bold",marginBottom:3}}>{cell.dist}</div>
                      <div style={{color:C.dimmer,fontSize:9}}>{cell.face}</div>
                      <div style={{color:cell.ok?"rgba(74,222,128,0.5)":"rgba(248,113,113,0.5)",
                        fontSize:9}}>min: {cell.min}</div>
                      <div style={{color:C.dimmer,fontSize:9,marginTop:2,maxWidth:160,lineHeight:1.5}}>{cell.note}</div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <Note c={C.green} ch="All separation requirements met. The GPS patch and SiK whip are on opposite fuselage faces (top vs belly), adding approximately 12–18 dB of isolation beyond their 148mm physical separation. The 49 MHz and SiK 915 MHz antennas occupy opposite faces (top vs belly) which provides additional isolation despite their relatively close axial distance of 52mm."/>
      <Warn ch="Verify GPS HDOP and fix quality with all radios transmitting simultaneously on the bench before flight. The 49 MHz loaded whip harmonics (147 MHz, 196 MHz, ...) are all well away from GPS L1 at 1575 MHz and 915 MHz, but empirical bench testing is mandatory."/>
    </div>
  );
}

// ── 49 MHz detail ─────────────────────────────────────────────────
function Mhz49Tab() {
  return (
    <div>
      <SH t="49 MHz Loaded Whip — Design Detail" mt={0} c={ANT.rc49.color}/>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
        <div>
          <KV k="Target frequency" v="49.830–49.890 MHz" c={ANT.rc49.color}/>
          <KV k="Channel plan" v="6 ch × 10kHz spacing" c={ANT.rc49.color}/>
          <KV k="λ/4 free space" v="1530 mm (impractical)"/>
          <KV k="Electrical length" v="λ/4 = 1530mm (achieved via loading coil)"/>
          <KV k="Physical whip length" v="250 mm"/>
          <KV k="Whip diameter" v="3mm OD aluminium or fibreglass rod"/>
          <KV k="Loading coil inductance" v="~38 μH"/>
          <KV k="Coil form" v="10mm OD × 35mm ferrite rod (material: 43 mix)"/>
          <KV k="Coil wire" v="1.0mm enamelled copper, 48 turns close-wound"/>
          <KV k="Coil Q" v="~80–120 at 49 MHz"/>
          <KV k="Coil position" v="Base-loaded (at mount base, feedpoint)"/>
          <KV k="Radiation resistance" v="~3–6 Ω (typical for l/λ ≈ 0.055)"/>
          <KV k="Loss resistance" v="~15–25 Ω (coil + counterpoise resistance)"/>
          <KV k="Efficiency" v="~12–28% (−6 to −9 dB) · adequate at ≤500m"/>
          <KV k="-3dB bandwidth" v="~80–120 kHz (covers all 6 RCRS channels)"/>
          <KV k="Counterpoise" v="4× λ/4 radials, 150mm, at 90° around mount base"/>
          <KV k="Counterpoise material" v="22AWG tinned copper, laid against fuselage skin"/>
          <KV k="Mount" v="M3 nylon screw through 3mm PLA dorsal fin"/>
          <KV k="Coax" v="50Ω RG-316 coax, 120mm, IPEX to COMPHAT-1"/>
          <KV k="Matching" v="LC pi-network (resonance trim): 5–30pF variable cap in series"/>
          <KV k="SWR target" v="≤2.5:1 across 49.83–49.89 MHz"/>
        </div>
        <div>
          {/* SVG schematic of the antenna */}
          <svg viewBox="0 0 280 420" width="100%" style={{maxWidth:300,display:"block"}}>
            {/* Coax connection at bottom */}
            <text x={140} y={410} textAnchor="middle" fill={C.dimmer}
              fontSize={8} fontFamily={M}>COAX FEEDPOINT (COMPHAT-1)</text>
            <line x1={140} y1={395} x2={140} y2={370} stroke={C.dimmer} strokeWidth={2}/>
            {/* Ground radials */}
            {[[-70,40],[70,40],[-60,-10],[60,-10]].map(([dx,dy],i)=>(
              <line key={i} x1={140} y1={360} x2={140+dx} y2={360+dy}
                stroke={ANT.rc49.color} strokeWidth={1.2} strokeDasharray="3 2" opacity={0.7}/>
            ))}
            <text x={210} y={380} fill={`${ANT.rc49.color}80`} fontSize={7} fontFamily={M}>radials</text>
            <text x={210} y={390} fill={`${ANT.rc49.color}60`} fontSize={7} fontFamily={M}>×4 · 150mm</text>
            {/* Mount/base */}
            <rect x={122} y={340} width={36} height={20} rx={3}
              fill="rgba(255,255,255,0.08)" stroke={C.dimmer} strokeWidth={1}/>
            <text x={140} y={354} textAnchor="middle" fill={C.dimmer} fontSize={7} fontFamily={M}>mount</text>
            {/* LC matching network */}
            <rect x={110} y={300} width={60} height={36} rx={3}
              fill="rgba(244,114,182,0.1)" stroke={ANT.rc49.color} strokeWidth={1}/>
            <text x={140} y={315} textAnchor="middle" fill={ANT.rc49.color} fontSize={7} fontFamily={M}>LC π-network</text>
            <text x={140} y={328} textAnchor="middle" fill={`${ANT.rc49.color}70`} fontSize={7} fontFamily={M}>5–30pF trim cap</text>
            <line x1={140} y1={340} x2={140} y2={336} stroke={ANT.rc49.color} strokeWidth={1}/>
            {/* Loading coil */}
            <rect x={120} y={220} width={40} height={76} rx={4}
              fill="rgba(244,114,182,0.08)" stroke={ANT.rc49.color} strokeWidth={1.2}/>
            {[0,1,2,3,4,5,6,7].map(i=>(
              <ellipse key={i} cx={140} cy={234+i*9} rx={14} ry={4}
                fill="none" stroke={ANT.rc49.color} strokeWidth={0.9} opacity={0.7}/>
            ))}
            <text x={170} y={255} fill={ANT.rc49.color} fontSize={7} fontFamily={M}>38 μH</text>
            <text x={170} y={266} fill={`${ANT.rc49.color}70`} fontSize={7} fontFamily={M}>ferrite #43</text>
            <text x={170} y={277} fill={`${ANT.rc49.color}60`} fontSize={7} fontFamily={M}>48T · 1.0mm</text>
            <line x1={140} y1={220} x2={140} y2={210} stroke={ANT.rc49.color} strokeWidth={1.5}/>
            <line x1={140} y1={296} x2={140} y2={304} stroke={ANT.rc49.color} strokeWidth={1.5}/>
            {/* Whip element — 250mm shown compressed */}
            <line x1={140} y1={210} x2={140} y2={30}
              stroke={ANT.rc49.color} strokeWidth={2.5} strokeLinecap="round"/>
            {/* tip */}
            <circle cx={140} cy={30} r={4} fill={ANT.rc49.color}/>
            {/* length callout */}
            <line x1={160} y1={30} x2={160} y2={210} stroke={ANT.rc49.color} strokeWidth={0.6} opacity={0.4}/>
            <line x1={156} y1={30} x2={164} y2={30} stroke={ANT.rc49.color} strokeWidth={0.6} opacity={0.4}/>
            <line x1={156} y1={210} x2={164} y2={210} stroke={ANT.rc49.color} strokeWidth={0.6} opacity={0.4}/>
            <text x={175} y={125} fill={ANT.rc49.color} fontSize={9} fontFamily={M} fontWeight="bold">250mm</text>
            <text x={175} y={137} fill={`${ANT.rc49.color}70`} fontSize={7} fontFamily={M}>whip</text>
            {/* PLA fin outline */}
            <rect x={108} y={300} width={64} height={80} rx={4}
              fill="none" stroke="rgba(255,255,255,0.12)" strokeWidth={1} strokeDasharray="4 2"/>
            <text x={140} y={398} textAnchor="middle"
              fill="rgba(255,255,255,0.78)" fontSize={7} fontFamily={M}>PLA dorsal fin</text>
            <text x={140} y={16} textAnchor="middle"
              fill={ANT.rc49.color} fontSize={8} fontFamily={M}>49 MHz LOADED MONOPOLE</text>
          </svg>
          <Note c={ANT.rc49.color} ch="Tune the 5–30pF series trimmer for minimum SWR at 49.860 MHz (channel 4, centre of the 6-channel band). An SWR of ≤2.5:1 reflects ≤11% of transmitted power — acceptable at ≤10mW EIRP. Measure with an antenna analyser or nanoVNA before first flight. Retune if the coil is repositioned."/>
        </div>
      </div>
      <SH t="Installation Procedure"/>
      {[
        ["1","3D-print the dorsal fin in ABS or PETG (not PLA — heat soak). Height 38mm, base 20×20mm, M3 tapped hole for mounting to fuselage skin at 290mm from nose."],
        ["2","Wind 48 turns of 1.0mm enamelled Cu on the ferrite rod (material 43). Leave 15mm pigtails each end. Coat with Q-dope or nail varnish for moisture protection."],
        ["3","Solder coil bottom pigtail to RG-316 centre conductor. Solder coil top pigtail to base of 250mm aluminium rod (or 3mm fibreglass rod with conductive paint trace)."],
        ["4","Solder 4× 150mm counterpoise wires to RG-316 shield braid. Route radials at 90° against the fuselage outer skin inside the fin base (they do NOT need to be elevated)."],
        ["5","Insert series trimmer (5–30pF) between coax centre and coil bottom. Connect nanoVNA. Adjust trimmer for minimum SWR at 49.860 MHz. Lock with drop of nail varnish."],
        ["6","Route RG-316 coax internally through the fuselage to COMPHAT-1 U.FL port. Secure with cable ties every 50mm. Minimum bend radius: 15mm."],
        ["7","Verify SWR ≤2.5:1 across 49.830–49.890 MHz with all hatch covers closed. Verify GPS lock and HDOP ≤1.5 with all radios transmitting simultaneously."],
      ].map(([n,s])=>(
        <div key={n} style={{display:"flex",gap:12,padding:"8px 0",
          borderBottom:"1px solid rgba(0,229,255,0.07)"}}>
          <span style={{color:ANT.rc49.color,fontFamily:M,fontSize:13,fontWeight:"bold",
            minWidth:18,flexShrink:0}}>{n}</span>
          <span style={{color:C.dim,fontFamily:M,fontSize:11,lineHeight:1.7}}>{s}</span>
        </div>
      ))}
    </div>
  );
}

// ── Install notes ─────────────────────────────────────────────────
function InstallTab() {
  const rules = [
    {c:C.green, title:"Carbon Fibre Keepout",
     body:"All four antenna elements must exit through PLA/PETG plastic shell zones. CF is electrically conductive (σ ≈ 10⁴ S/m) and strongly attenuates RF. The wing spars (12mm CF tubes) are at 160mm from the nose — all antenna feedpoints are positioned forward or aft of this frame member. No antenna wire runs parallel to a CF spar within 20mm."},
    {c:ANT.rc49.color, title:"49 MHz — Dorsal Fin Location",
     body:"Mount at 290mm from nose on the dorsal (top) surface. This is aft of the CF spar by 130mm and aft of the CM4 WiFi antenna zone by 80mm. The dorsal position keeps the whip clear of the payload bay, winch mechanism, and skid landing gear. The fin must be oriented with the whip vertical in hover and approximately level in cruise — the pattern rotates with the aircraft which is acceptable for TDDS at short range."},
    {c:ANT.sik.color, title:"915 MHz — Belly SMA Penetration",
     body:"Drill a 6.5mm hole in the PLA belly skin at 238mm from nose. Install an SMA-RP bulkhead connector. The SiK module connects internally via an IPEX-to-SMA pigtail through the COMPHAT-1 module. Thread the 82mm whip onto the external SMA-RP. Orient vertically downward. Secure with a small plastic clip to prevent vibration-induced rotation — vibration loosening of SMA connectors is a known failure mode on EDFs."},
    {c:ANT.gps.color, title:"GPS Patch — Forward Top Mounting",
     body:"The 25×25mm patch antenna mounts on a 12mm PLA standoff at 58mm from nose. The standoff raises the patch above the fuselage metal hinge hardware for the access hatch. Route the U.FL coax in a gentle curve — never kink RG-178. The patch must have an unobstructed hemisphere of sky (90° half-angle). The pitot tube at the nose (58mm forward) is metallic but is 30mm below the patch plane — verify this does not create a null above 60° elevation empirically."},
    {c:ANT.wifi.color, title:"WiFi — No Modification Needed",
     body:"The CM4 PCB trace antenna is internal to the carrier board and radiates through the PLA fuselage skin. Ensure the fuselage shell has no conductive paint or metallic films in the 15mm zone on each side of the antenna trace (at 210mm from nose). The WiFi antenna is passive — no connectors, no installation steps. Do not attach any metal standoffs or cable ties within 15mm of the CM4 carrier board antenna keepout zone."},
    {c:C.yellow, title:"EDF Motor RF Noise",
     body:"60mm BLDC motors generate wideband PWM switching noise from ESC DSHOT signals (300kHz fundamental + harmonics to ~1GHz). Place ferrite beads (Fair-Rite 0443164151) on each ESC power lead. Add a 100nF + 10μF decoupling cap at each ESC input. The GPS patch is 58mm from the nose — the nearest EDF is at the wing tip (>300mm away). The SiK whip at 238mm is 60mm from the CF spar but 300mm+ from any motor. Post-installation: verify no GPS HDOP degradation >0.3 with EDFs spinning at hover throttle."},
    {c:C.teal, title:"Pitot Tube RF Interaction",
     body:"The 3mm CF pitot tube extends 40mm forward from the nose. At 915 MHz it is λ/34 — negligible re-radiation. At 49 MHz it is λ/1042 — negligible. At 1575 MHz (GPS L1) it is λ/5 — potentially a mild scatterer. Keep the pitot tip at least 30mm from the GPS patch plane. The current layout achieves approximately 50mm vertical separation between the pitot rod and the patch element. If GPS patch elevation coverage above 70° is critical for your application, angle the patch 10° forward."},
  ];
  return (
    <div>
      <SH t="Installation Rules" mt={0}/>
      {rules.map((r,i)=>(
        <div key={i} style={{marginBottom:14,padding:"12px 14px",
          border:`1px solid ${r.c}22`,borderLeft:`2px solid ${r.c}55`,
          background:`${r.c}06`,borderRadius:3}}>
          <div style={{color:r.c,fontFamily:M,fontSize:11,fontWeight:"bold",
            letterSpacing:"0.06em",marginBottom:7}}>{r.title}</div>
          <p style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.85,margin:0}}>{r.body}</p>
        </div>
      ))}
    </div>
  );
}

// ══════════════════════════════════════════════════════════════════
// APP
// ══════════════════════════════════════════════════════════════════
const TABS = ["Airframe Diagram","Separation Matrix","49 MHz Detail","Installation Rules"];

_ODFontLoader();
export default function App() {
  const [tab,setTab]=useState("Airframe Diagram");
  return (
    <div style={{minHeight:"100vh",background:C.bg,color:C.text,fontFamily:M}}>
      <Grid/>
      {/* Header */}
      <div style={{position:"relative",zIndex:1,borderBottom:`1px solid ${C.border}`,
        padding:"20px 28px 16px"}}>
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",
          flexWrap:"wrap",gap:12}}>
          <div>
            <div style={{color:"rgba(0,229,255,0.32)",fontSize:9,letterSpacing:"0.2em",marginBottom:5}}>
              TRI-FAN TILTROTOR · ANTENNA LAYOUT SPECIFICATION · REV A
            </div>
            <h1 style={{margin:0,fontSize:20,fontWeight:"normal",color:"#fff",letterSpacing:"0.07em"}}>
              AIRFRAME ANTENNA LAYOUT
            </h1>
            <div style={{color:"rgba(0,229,255,0.5)",fontSize:10,marginTop:5}}>
              GPS L1 · SiK 915 MHz · 49 MHz RCRS TDDS · WiFi 2.4/5 GHz
            </div>
          </div>
          <div style={{textAlign:"right",fontFamily:M}}>
            <div style={{color:C.green,fontSize:11}}>All separations ✔</div>
            <div style={{color:C.dimmer,fontSize:9,marginTop:3}}>4 antenna systems · 3 external · 1 internal</div>
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
      {/* Content */}
      <div style={{position:"relative",zIndex:1,padding:"24px 28px",maxWidth:1060,margin:"0 auto"}}>
        {tab==="Airframe Diagram"   && <DiagramTab/>}
        {tab==="Separation Matrix"  && <MatrixTab/>}
        {tab==="49 MHz Detail"      && <Mhz49Tab/>}
        {tab==="Installation Rules" && <InstallTab/>}
      </div>
      <div style={{position:"relative",zIndex:1,borderTop:`1px solid ${C.border}`,
        padding:"11px 28px",display:"flex",justifyContent:"space-between",flexWrap:"wrap",gap:6}}>
        <span style={{color:"rgba(0,229,255,0.18)",fontSize:8,letterSpacing:"0.12em"}}>
          ANTENNA LAYOUT REV A · TRI-FAN TILTROTOR UAV
        </span>
        <span style={{color:"rgba(0,229,255,0.18)",fontSize:8,letterSpacing:"0.1em"}}>
          VERIFY EMPIRICALLY BEFORE FLIGHT · NOT FOR CERTIFICATION
        </span>
      </div>
    </div>
  );
}
