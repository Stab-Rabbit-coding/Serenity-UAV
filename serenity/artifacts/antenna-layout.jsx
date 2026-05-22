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

// antenna positions (mm from nose — schematic/representative scale)
const POS = {
  gps:   { x: mmX(58),  label:"GPS patch", sublabel:"58mm from nose", side:"TOP" },
  sik:   { x: mmX(238), label:"915 MHz whip", sublabel:"238mm from nose", side:"BELLY" },
  // rc49 is now a top wire; xFwd = nose post, xAft = EDF cone post, x = midpoint for inspector
  rc49:  { x: mmX(200), xFwd: mmX(90), xAft: mmX(308),
           label:"49 MHz top wire (nose → EDF cone)", sublabel:"~90–308mm (schematic)", side:"TOP" },
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

      {/* 49MHz dorsal top wire: nose post → EDF cone post */}
      {halo("rc49", (POS.rc49.xFwd+POS.rc49.xAft)/2, CY-18, 7, ANT.rc49.color)}
      <g onClick={()=>onHover(hover==="rc49"?null:"rc49")} style={{cursor:"pointer"}}>
        {/* Wire line along hull dorsal spine */}
        <line x1={POS.rc49.xFwd} y1={CY-18} x2={POS.rc49.xAft} y2={CY-18}
          stroke={ANT.rc49.color} strokeWidth={hover==="rc49"?2.5:1.8}/>
        {/* Forward insulated mast (nose post) */}
        <line x1={POS.rc49.xFwd} y1={CY-18} x2={POS.rc49.xFwd} y2={CY-30}
          stroke={ANT.rc49.color} strokeWidth={1.5}/>
        <circle cx={POS.rc49.xFwd} cy={CY-30} r={3.5}
          fill="none" stroke={ANT.rc49.color} strokeWidth={1.2}/>
        {/* Loading coil / feed dot at nose post */}
        <circle cx={POS.rc49.xFwd} cy={CY-18} r={4}
          fill={`${ANT.rc49.color}28`} stroke={ANT.rc49.color} strokeWidth={1}/>
        {/* Aft insulated mast (EDF cone post) */}
        <line x1={POS.rc49.xAft} y1={CY-18} x2={POS.rc49.xAft} y2={CY-28}
          stroke={ANT.rc49.color} strokeWidth={1.5}/>
        <circle cx={POS.rc49.xAft} cy={CY-28} r={3}
          fill="none" stroke={ANT.rc49.color} strokeWidth={1.2}/>
        {/* Centre label */}
        <text x={(POS.rc49.xFwd+POS.rc49.xAft)/2} y={CY-48} textAnchor="middle"
          fill={ANT.rc49.color} fontSize={7} fontFamily={M} fontWeight="bold">49MHz top wire</text>
        <text x={POS.rc49.xFwd+4} y={CY-38} textAnchor="start"
          fill={`${ANT.rc49.color}90`} fontSize={6} fontFamily={M}>fwd post ~90mm</text>
        <text x={POS.rc49.xAft-4} y={CY-38} textAnchor="end"
          fill={`${ANT.rc49.color}90`} fontSize={6} fontFamily={M}>aft post ~310mm</text>
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
      {/* GPS to 49MHz wire forward post — now WARNING distance */}
      <g opacity={0.6}>
        <line x1={POS.gps.x} y1={CY+30} x2={POS.rc49.xFwd} y2={CY+30}
          stroke="#f87171" strokeWidth={0.9}/>
        <line x1={POS.gps.x} y1={CY+27} x2={POS.gps.x} y2={CY+33} stroke="#f87171" strokeWidth={0.9}/>
        <line x1={POS.rc49.xFwd} y1={CY+27} x2={POS.rc49.xFwd} y2={CY+33} stroke="#f87171" strokeWidth={0.9}/>
        <text x={(POS.gps.x+POS.rc49.xFwd)/2} y={CY+43} textAnchor="middle"
          fill="#f87171" fontSize={7} fontFamily={M}>~32mm ⚠ verify GPS</text>
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

      {/* 49MHz dorsal top wire — runs nose post → EDF cone along hull spine */}
      {halo("rc49", (POS.rc49.xFwd+POS.rc49.xAft)/2, CY-FR-6, 7, ANT.rc49.color)}
      <g onClick={()=>onHover(hover==="rc49"?null:"rc49")} style={{cursor:"pointer"}}>
        {/* Wire running along hull top surface */}
        <line x1={POS.rc49.xFwd} y1={CY-FR} x2={POS.rc49.xAft} y2={CY-FR}
          stroke={ANT.rc49.color} strokeWidth={hover==="rc49"?2.5:1.8} strokeLinecap="round"/>
        {/* Forward insulated mast (nose post) — feed/coil end */}
        <rect x={POS.rc49.xFwd-3} y={CY-FR-8} width={6} height={9} rx={1}
          fill={`${ANT.rc49.color}28`} stroke={ANT.rc49.color} strokeWidth={1}/>
        {/* Coil symbol at nose post */}
        {[0,1,2].map(i=>(
          <ellipse key={i} cx={POS.rc49.xFwd} cy={CY-FR-14-i*6} rx={3.5} ry={2.5}
            fill="none" stroke={ANT.rc49.color} strokeWidth={0.9} opacity={0.8}/>
        ))}
        <text x={POS.rc49.xFwd-14} y={CY-FR-26} fill={ANT.rc49.color} fontSize={6} fontFamily={M}>coil+feed</text>
        {/* Counterpoise wire at feed post (goes along belly or to keel) */}
        <line x1={POS.rc49.xFwd} y1={CY-FR} x2={POS.rc49.xFwd-20} y2={CY+FR-4}
          stroke={ANT.rc49.color} strokeWidth={0.8} strokeDasharray="2 2" opacity={0.5}/>
        <line x1={POS.rc49.xFwd} y1={CY-FR} x2={POS.rc49.xFwd+20} y2={CY+FR-4}
          stroke={ANT.rc49.color} strokeWidth={0.8} strokeDasharray="2 2" opacity={0.5}/>
        <text x={POS.rc49.xFwd+26} y={CY+FR+2} fill={`${ANT.rc49.color}60`}
          fontSize={6} fontFamily={M}>counterpoise</text>
        {/* Aft insulated mast (EDF cone post) */}
        <rect x={POS.rc49.xAft-3} y={CY-FR-7} width={6} height={8} rx={1}
          fill={`${ANT.rc49.color}18`} stroke={ANT.rc49.color} strokeWidth={1}/>
        {/* Insulator symbol at aft post (open circle) */}
        <circle cx={POS.rc49.xAft} cy={CY-FR-10} r={3}
          fill="none" stroke={ANT.rc49.color} strokeWidth={1.2}/>
        <text x={POS.rc49.xAft+6} y={CY-FR-10} fill={`${ANT.rc49.color}80`}
          fontSize={6} fontFamily={M}>insulator</text>
        {/* Wire length callout */}
        <line x1={POS.rc49.xFwd} y1={CY-FR-36} x2={POS.rc49.xAft} y2={CY-FR-36}
          stroke={ANT.rc49.color} strokeWidth={0.5} opacity={0.35}/>
        <line x1={POS.rc49.xFwd} y1={CY-FR-39} x2={POS.rc49.xFwd} y2={CY-FR-33}
          stroke={ANT.rc49.color} strokeWidth={0.5} opacity={0.35}/>
        <line x1={POS.rc49.xAft} y1={CY-FR-39} x2={POS.rc49.xAft} y2={CY-FR-33}
          stroke={ANT.rc49.color} strokeWidth={0.5} opacity={0.35}/>
        <text x={(POS.rc49.xFwd+POS.rc49.xAft)/2} y={CY-FR-42} textAnchor="middle"
          fill={ANT.rc49.color} fontSize={7} fontFamily={M} fontWeight="bold">49MHz top wire ~470mm</text>
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

      {/* Separation callout — GPS to 49MHz wire forward post ⚠ short */}
      <g opacity={0.7}>
        <line x1={POS.gps.x} y1={CY-FR-32} x2={POS.rc49.xFwd} y2={CY-FR-32}
          stroke="#f87171" strokeWidth={0.8}/>
        <line x1={POS.gps.x} y1={CY-FR-35} x2={POS.gps.x} y2={CY-FR-29}
          stroke="#f87171" strokeWidth={0.8}/>
        <line x1={POS.rc49.xFwd} y1={CY-FR-35} x2={POS.rc49.xFwd} y2={CY-FR-29}
          stroke="#f87171" strokeWidth={0.8}/>
        <text x={(POS.gps.x+POS.rc49.xFwd)/2} y={CY-FR-38} textAnchor="middle"
          fill="#f87171" fontSize={6.5} fontFamily={M}>~32mm ⚠ bench verify GPS</text>
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

      {/* 49MHz dorsal top wire — not visible from below, shown as dashed centre line */}
      <g onClick={()=>onHover(hover==="rc49"?null:"rc49")} style={{cursor:"pointer"}}>
        <line x1={POS.rc49.xFwd} y1={CY} x2={POS.rc49.xAft} y2={CY}
          stroke={ANT.rc49.color} strokeWidth={hover==="rc49"?1.5:0.8} strokeDasharray="5 3" opacity={0.5}/>
        <text x={(POS.rc49.xFwd+POS.rc49.xAft)/2} y={CY-10} textAnchor="middle"
          fill={`${ANT.rc49.color}55`} fontSize={6} fontFamily={M}>49MHz wire ↑ (hidden)</text>
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
      ["Reason fwd","Away from CM4/COMMS-HAT-1 switching noise (>150mm), away from EDF motor interference"],
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
      ["Type","Monopole whip, λ/4 @ 915 MHz = 82mm · SMA-RP female on COMMS-HAT-1"],
      ["Polarisation","Vertical (aligned with Earth's gravity in hover)"],
      ["Mount face","BELLY of fuselage, 238mm from nose · aft of payload bay"],
      ["Orientation","Vertical, pointing down · best pattern toward ground station"],
      ["Reason aft","Clears payload bay (125–195mm) by 43mm forward margin"],
      ["Reason belly","Ground-facing pattern · GCS is always below aircraft"],
      ["Cable","Integral to SiK module via IPEX/U.FL pigtail through fuselage hole"],
      ["Ground plane","SiK module GND pours on COMMS-HAT-1 PCB act as partial counterpoise"],
      ["Material zone","PLA shell belly — RF transparent ✔ · CF spar at 160mm (78mm away)"],
      ["Clearance to GPS","148mm ✔ (opposite faces top/belly add effective isolation)"],
      ["Clearance to 49MHz","52mm on fuselage — supplemented by face diversity (top vs belly)"],
      ["Clearance to payload","43mm forward of payload bay edge ✔"],
      ["Beam pattern","Toroidal · null straight down/up · max at horizon toward GCS"],
    ]
  },
  rc49: {
    title:"49 MHz RCRS TDDS Top Wire Antenna", c:ANT.rc49.color,
    rows:[
      ["Type","End-fed shortened top wire — runs from nose post (~120mm) to EDF cone post (~600mm) along hull dorsal spine"],
      ["Frequency","49.830–49.890 MHz (6 RCRS channels, 10kHz spacing)"],
      ["λ/4 free-space","1530mm — impractical; wire is ~470mm (λ/13), heavily shortened"],
      ["Wire length","~470mm actual (nose post ~120mm to EDF cone ~600mm from nose, 24\" hull)"],
      ["Wire material","0.3mm stainless steel wire or 22AWG enamelled copper"],
      ["Forward post","PETG insulated mast ~10mm tall, bonded to dorsal hull at ~120mm from nose (just aft of bridge)"],
      ["Aft post","PETG hook post ~10mm tall, bonded to top of rear_nozzle_frame.stl at EDF cone"],
      ["Feed end","Forward (nose) post — loading coil + LC pi-network + RG-316 coax to RCRS-49 in Bay A"],
      ["Aft end","Electrically open (insulated) — wire terminates on insulator at aft post"],
      ["Loading coil","~38 μH base-loaded at nose feed post · 10mm ferrite rod (#43 mix) · 1.0mm Cu · ~48 turns"],
      ["Matching","LC pi-network (5–30pF series trim cap) resonates wire at 49.86 MHz"],
      ["Counterpoise","CF keel bar (6×3mm, grounded to RCRS-49 GND at Bay A) acts as partial ground plane; supplement with 2× belly wires ~150mm at feed post if SWR > 3:1"],
      ["Polarisation","Horizontal wire — pattern has max broadside (port/stbd). Ground stations typically vertical; cross-polarisation loss ~6–12dB, acceptable at ≤300m TDDS range"],
      ["Radiation resistance","~2–5 Ω (end-fed wire at this length/λ ratio)"],
      ["Efficiency","~−10 to −16 dB vs ideal dipole — adequate for ≤300m short-range TDDS"],
      ["⚠ GPS clearance","~120mm actual (24\" hull): wire forward post is ~43mm aft of GPS patch (~77mm from nose). 49MHz harmonics (98, 147, 196MHz...) do NOT fall on GPS L1 (1575MHz); near-field coupling/detuning is the risk. VERIFY GPS HDOP ≤1.5 with RCRS-49 transmitting."],
      ["Clearance to SiK","Wire passes directly over SiK station (~260mm) on opposite face (top vs belly) — ~50mm vertical separation at that hull station. Freq. sep. is 866 MHz; face diversity adds ~12dB isolation. ✔"],
      ["Clearance to WiFi","Internal WiFi at ~210mm — wire passes ~50mm above; frequencies very different. ✔"],
      ["Aesthetic note","Top wire running nose-to-tail is visually authentic to the Serenity/Firefly ship — exterior antenna wires are a key detail of the Firefly design language."],
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
    "gps-rc49": {dist:"~43mm (actual)",face:"both top",ok:false,min:"150mm (std)",note:"Wire forward post ~43mm from GPS patch (same face). 49MHz harmonics (98,147… MHz) don't reach GPS L1 (1575MHz) — risk is near-field detuning. BENCH TEST: verify GPS HDOP ≤1.5 with RCRS transmitting. If degraded, move GPS patch to ≥165mm."},
    "gps-wifi": {dist:"152mm",face:"internal",ok:true, min:"50mm", note:"2.4GHz–1.575GHz gap is large; no harmful coupling"},
    "sik-rc49": {dist:"~50mm vertical",face:"belly vs top",ok:true, min:"face diversity",note:"Wire passes over SiK station (opposite faces). ~50mm vertical separation through hull. 866 MHz freq. gap + face diversity (~12dB). ✔"},
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
      <Warn ch="GPS–49MHz clearance reduced: the 49MHz top wire forward post is now ~43mm from the GPS patch (both on dorsal surface). The 49MHz harmonics (98, 147, 196 MHz…) do NOT fall on GPS L1 (1575 MHz), but near-field coupling may detune the GPS patch LNA. MANDATORY bench test: verify GPS HDOP ≤1.5 and fix quality with RCRS-49 transmitting at full power. If GPS degrades, relocate GPS patch aft to ≥165mm from nose."/>
      <Note c={C.green} ch="All other pairs meet separation requirements. GPS↔SiK: opposite faces (top vs belly) add ~12dB isolation beyond 148mm. 49MHz wire↔SiK: wire passes over SiK station with ~50mm vertical separation through hull and face diversity. 49MHz wire↔WiFi: same — wire over internal WiFi, opposite faces."/>
    </div>
  );
}

// ── 49 MHz detail ─────────────────────────────────────────────────
function Mhz49Tab() {
  return (
    <div>
      <SH t="49 MHz Top Wire Antenna — Design Detail" mt={0} c={ANT.rc49.color}/>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
        <div>
          <KV k="Type" v="End-fed shortened top wire — nose post to EDF cone" c={ANT.rc49.color}/>
          <KV k="Frequency" v="49.830–49.890 MHz · 6 RCRS channels · 10kHz spacing" c={ANT.rc49.color}/>
          <KV k="Wire length" v="~470mm (nose post ~120mm to EDF cone ~600mm, 24 inch hull)"/>
          <KV k="Wire material" v="0.3mm stainless steel or 22AWG enamelled copper"/>
          <KV k="Tension" v="Light tautness — spring ~20g to prevent flutter"/>
          <KV k="Forward post" v="PETG mast ~10mm tall · bonded at ~120mm from nose (just aft of bridge)"/>
          <KV k="Aft post" v="PETG hook ~10mm tall · bonded to top of rear_nozzle_frame.stl"/>
          <KV k="Feed end" v="Forward (nose) post — loading coil + LC pi-network + RG-316 to Bay A"/>
          <KV k="Aft end" v="Open/insulated — wire clips to aft post via ceramic bead insulator"/>
          <KV k="Loading coil" v="~38 uH base-loaded at nose post · 10mm ferrite rod #43 · 1.0mm Cu · ~48T"/>
          <KV k="Coil Q" v="~80–120 at 49 MHz"/>
          <KV k="Matching" v="LC pi-network (5–30pF series trim cap) resonates system at 49.86 MHz"/>
          <KV k="Counterpoise" v="CF keel bar (6x3mm) grounded to RCRS-49 GND at Bay A. Add 2x 150mm belly wires if SWR > 3:1"/>
          <KV k="Radiation resistance" v="~2–5 Ohm (end-fed wire at l/lambda ~ 0.077)"/>
          <KV k="Loss resistance" v="~20–35 Ohm (coil + counterpoise contact resistance)"/>
          <KV k="Efficiency" v="~8–18% (−7 to −11 dB) — adequate for ≤300m TDDS range"/>
          <KV k="Polarisation" v="Horizontal wire — broadside (port/stbd) max. Cross-pol loss vs vertical GCS ~6–12dB"/>
          <KV k="-3dB bandwidth" v="~60–100 kHz — covers all 6 RCRS channels (60kHz span)"/>
          <KV k="SWR target" v="≤2.5:1 across 49.830–49.890 MHz"/>
          <KV k="Coax" v="50Ohm RG-316, ≤150mm, IPEX to RCRS-49 module in Bay A"/>
          <KV k="GPS proximity" v="~43mm to GPS patch (same dorsal face). Verify HDOP empirically."/>
          <KV k="Aesthetic" v="Nose-to-tail top wire is authentic Serenity/Firefly ship detail"/>
        </div>
        <div>
          {/* SVG schematic of wire antenna — side view */}
          <svg viewBox="0 0 320 310" width="100%" style={{maxWidth:340,display:"block"}}>
            <text x={160} y={16} textAnchor="middle"
              fill={ANT.rc49.color} fontSize={8} fontFamily={M}>49 MHz TOP WIRE (SIDE VIEW, SCHEMATIC)</text>
            {/* Hull outline */}
            <ellipse cx={160} cy={160} rx={130} ry={28}
              fill="rgba(0,229,255,0.04)" stroke="rgba(0,229,255,0.35)" strokeWidth={1.5}/>
            <text x={30} y={163} fill="rgba(0,229,255,0.35)" fontSize={7} fontFamily={M}>NOSE</text>
            <text x={274} y={163} fill="rgba(0,229,255,0.35)" fontSize={7} fontFamily={M}>TAIL</text>
            {/* Forward mast (nose post) */}
            <line x1={52} y1={132} x2={52} y2={122} stroke={ANT.rc49.color} strokeWidth={2}/>
            <rect x={46} y={130} width={12} height={8} rx={2}
              fill={`${ANT.rc49.color}22`} stroke={ANT.rc49.color} strokeWidth={1}/>
            {/* Loading coil at nose post */}
            {[0,1,2,3].map(i=>(
              <ellipse key={i} cx={52} cy={112-i*7} rx={7} ry={3}
                fill="none" stroke={ANT.rc49.color} strokeWidth={1.1} opacity={0.8}/>
            ))}
            <text x={66} y={108} fill={ANT.rc49.color} fontSize={6.5} fontFamily={M}>38uH loading coil</text>
            {/* LC pi-network box */}
            <rect x={32} y={80} width={42} height={24} rx={3}
              fill="rgba(244,114,182,0.1)" stroke={ANT.rc49.color} strokeWidth={1}/>
            <text x={53} y={91} textAnchor="middle" fill={ANT.rc49.color} fontSize={6} fontFamily={M}>LC pi-net</text>
            <text x={53} y={100} textAnchor="middle" fill={`${ANT.rc49.color}70`} fontSize={6} fontFamily={M}>5–30pF trim</text>
            <line x1={52} y1={84} x2={52} y2={82} stroke={ANT.rc49.color} strokeWidth={1.2}/>
            <line x1={52} y1={104} x2={52} y2={112} stroke={ANT.rc49.color} strokeWidth={1.2}/>
            {/* Coax going down */}
            <line x1={52} y1={80} x2={52} y2={56} stroke={C.dimmer} strokeWidth={2}/>
            <text x={53} y={50} fill={C.dimmer} fontSize={7} fontFamily={M}>RG-316 to Bay A</text>
            {/* Top wire */}
            <line x1={52} y1={132} x2={268} y2={132}
              stroke={ANT.rc49.color} strokeWidth={2.5} strokeLinecap="round"/>
            {/* Wire length callout */}
            <line x1={52} y1={144} x2={268} y2={144}
              stroke={ANT.rc49.color} strokeWidth={0.5} opacity={0.35}/>
            <line x1={52} y1={141} x2={52} y2={147} stroke={ANT.rc49.color} strokeWidth={0.5} opacity={0.35}/>
            <line x1={268} y1={141} x2={268} y2={147} stroke={ANT.rc49.color} strokeWidth={0.5} opacity={0.35}/>
            <text x={160} y={156} textAnchor="middle"
              fill={ANT.rc49.color} fontSize={8} fontFamily={M} fontWeight="bold">~470mm wire</text>
            {/* Aft mast (EDF cone post) */}
            <line x1={268} y1={132} x2={268} y2={122} stroke={ANT.rc49.color} strokeWidth={2}/>
            <rect x={262} y={130} width={12} height={8} rx={2}
              fill={`${ANT.rc49.color}18`} stroke={ANT.rc49.color} strokeWidth={1}/>
            <circle cx={268} cy={119} r={5} fill="none" stroke={ANT.rc49.color} strokeWidth={1.2}/>
            <text x={278} y={114} fill={`${ANT.rc49.color}80`} fontSize={6} fontFamily={M}>insulator</text>
            <text x={268} y={106} textAnchor="middle"
              fill={`${ANT.rc49.color}70`} fontSize={6} fontFamily={M}>EDF cone</text>
            {/* Counterpoise: keel bar */}
            <line x1={30} y1={188} x2={290} y2={188}
              stroke={ANT.rc49.color} strokeWidth={1.5} strokeDasharray="6,3" opacity={0.5}/>
            <text x={160} y={200} textAnchor="middle"
              fill={`${ANT.rc49.color}60`} fontSize={7} fontFamily={M}>CF keel bar (counterpoise ground)</text>
            <line x1={52} y1={188} x2={52} y2={160}
              stroke={ANT.rc49.color} strokeWidth={0.8} strokeDasharray="3,2" opacity={0.45}/>
            <text x={52} y={176} textAnchor="middle" fill={`${ANT.rc49.color}55`} fontSize={6} fontFamily={M}>GND</text>
            {/* GPS proximity warning */}
            <rect x={20} y={216} width={280} height={36} rx={3}
              fill="rgba(248,113,113,0.06)" stroke="#f87171" strokeWidth={0.8}/>
            <text x={160} y={229} textAnchor="middle" fill="#f87171" fontSize={7} fontFamily={M} fontWeight="bold">
              GPS patch ~43mm aft of nose post (same face)
            </text>
            <text x={160} y={241} textAnchor="middle" fill="#f87171" fontSize={6.5} fontFamily={M}>
              Verify GPS HDOP ≤1.5 with RCRS-49 transmitting before flight
            </text>
            {/* Polarisation note */}
            <text x={160} y={270} textAnchor="middle" fill={C.dimmer} fontSize={7} fontFamily={M}>
              Horizontal wire: broadside (port/stbd) max pattern
            </text>
            <text x={160} y={282} textAnchor="middle" fill={`${C.dimmer}80`} fontSize={6.5} fontFamily={M}>
              Cross-pol loss vs vertical GCS ~6–12dB — acceptable at ≤300m
            </text>
          </svg>
          <Note c={ANT.rc49.color} ch="Tune the 5–30pF series trimmer for minimum SWR at 49.860 MHz (channel 4). SWR ≤2.5:1 reflects ≤11% of power — acceptable at ≤10mW EIRP. Measure with nanoVNA before first flight. Re-tune if wire length changes."/>
        </div>
      </div>
      <SH t="Installation Procedure"/>
      {[
        ["1","3D-print two insulated mast posts in PETG: forward post (10mm tall, M3 tapped base, small hook at top, 12x12mm foot) and aft post (same but hook only, no coil). The aft post bonds to the top of rear_nozzle_frame.stl; the forward post bonds to the dorsal hull at ~120mm from nose (just aft of the bridge/cockpit section)."],
        ["2","Bond forward post to dorsal hull at ~120mm from nose with structural epoxy (West System). Bond aft post to top of rear_nozzle_frame.stl. Cure 2h. Both posts must be vertical and aligned on the hull centreline."],
        ["3","Wind 48 turns of 1.0mm enamelled Cu on 10mm ferrite rod (material #43). Leave 15mm pigtails. Coat with Q-dope. Solder bottom pigtail to RG-316 centre conductor (feedpoint). Solder top pigtail to the start of the antenna wire."],
        ["4","Connect RG-316 shield braid to CF keel bar via tinned-copper wire and clip or solder lug at Bay A. This establishes the keel bar as counterpoise ground. If SWR remains >3:1 after tuning, add 2x 150mm tinned-copper belly wires at the nose post laid flat along the belly skin."],
        ["5","Insert series trimmer (5–30pF) between RG-316 centre and coil bottom. Attach nanoVNA. Feed the wire through the forward post hook. Adjust trimmer for minimum SWR at 49.860 MHz. Lock with nail varnish drop. SWR target ≤2.5:1 across 49.830–49.890 MHz."],
        ["6","Pull the wire aft along the hull dorsal spine to the aft post hook. Tension lightly (~20g spring tension to prevent flutter). Clip the aft end to a ceramic bead insulator at the aft post. The aft end is electrically open."],
        ["7","GPS bench test: with all covers closed and RCRS-49 transmitting at full power, verify GPS HDOP ≤1.5 and 3D fix quality. If GPS degrades, relocate GPS patch aft to ≥165mm from nose where the wire feed is further away."],
        ["8","Route RG-316 coax internally from the nose post through Bay A to the RCRS-49 IPEX/U.FL connector. Secure with cable ties every 50mm. Minimum bend radius 15mm."],
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
    {c:ANT.rc49.color, title:"49 MHz — Top Wire, Nose Post to EDF Cone",
     body:"A 0.3mm stainless steel (or 22AWG enamelled copper) wire runs along the dorsal hull spine from a PETG insulated post at ~120mm from nose (just aft of the bridge/cockpit) to a PETG insulated hook post at the top of the rear nozzle cone frame (~600mm). Feed end (nose post): loading coil + LC pi-network + RG-316 coax to RCRS-49 in Bay A. Aft end: electrically open via ceramic bead insulator. Counterpoise: CF keel bar grounded to RCRS-49 GND. Pattern is broadside (port/stbd maximum) — cross-polarisation loss vs vertical ground station is ~6–12dB, acceptable at ≤300m TDDS range. GPS bench test mandatory: forward post is ~43mm from GPS patch, both on dorsal face; verify HDOP ≤1.5 with all radios transmitting."},
    {c:ANT.sik.color, title:"915 MHz — Belly SMA Penetration",
     body:"Drill a 6.5mm hole in the PLA belly skin at 238mm from nose. Install an SMA-RP bulkhead connector. The SiK module connects internally via an IPEX-to-SMA pigtail through the COMMS-HAT-1 module. Thread the 82mm whip onto the external SMA-RP. Orient vertically downward. Secure with a small plastic clip to prevent vibration-induced rotation — vibration loosening of SMA connectors is a known failure mode on EDFs."},
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
