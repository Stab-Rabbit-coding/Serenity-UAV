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
  bg:"#060810", border:"rgba(0,229,255,0.11)", accent:"#00e5ff",
  orange:"#ff6b35", yellow:"#ffe600", purple:"#c084fc", green:"#4ade80",
  pink:"#f472b6", teal:"#2dd4bf", red:"#f87171", lime:"#a3e635",
  gold:"#fbbf24", dim:"rgba(255,255,255,0.90)", dimmer:"rgba(255,255,255,0.80)",
  text:"rgba(255,255,255,0.82)",
  // protocol identity colours
  eth:"#c084fc",    // purple  — Ethernet
  can:"#ff6b35",    // orange  — CAN FD
  rs4:"#2dd4bf",    // teal    — RS-485
  m53:"#fbbf24",    // gold    — MIL-STD-1553
  i2c:"#4ade80",    // green   — I²C (on-PCB expansion, not counted as 4th bus)
};
const M = "'OpenDyslexic Mono','OpenDyslexic','OpenDyslexicMono',monospace";

const SH=({t,c=C.accent,mt=22})=>(<div style={{display:"flex",alignItems:"center",gap:10,marginBottom:14,marginTop:mt}}><div style={{width:3,height:17,background:c}}/><span style={{color:c,fontFamily:M,fontSize:13,letterSpacing:"0.13em",textTransform:"uppercase",fontWeight:"normal"}}>{t}</span></div>);
const KV=({k,v,vc=C.text})=>(<div style={{display:"flex",justifyContent:"space-between",padding:"5px 0",borderBottom:"1px solid rgba(0,229,255,0.07)",alignItems:"baseline"}}><span style={{color:C.dim,fontFamily:M,fontSize:11}}>{k}</span><span style={{color:vc,fontFamily:M,fontSize:11}}>{v}</span></div>);
const Note=({c=C.dim,ch})=>(<div style={{marginTop:8,marginBottom:6,color:c,fontFamily:M,fontSize:10,lineHeight:1.85,padding:"8px 12px",borderLeft:`2px solid ${c}55`,background:`${c}07`,borderRadius:3}}>{ch}</div>);
const Warn=({ch})=>(<div style={{marginTop:8,color:C.yellow,fontFamily:M,fontSize:10,lineHeight:1.8,padding:"7px 12px",borderLeft:`2px solid ${C.yellow}`,background:"rgba(255,230,0,0.05)",borderRadius:3}}>⚠ {ch}</div>);
const Good=({ch})=>(<div style={{marginTop:8,color:C.green,fontFamily:M,fontSize:10,lineHeight:1.8,padding:"7px 12px",borderLeft:`2px solid ${C.green}`,background:"rgba(74,222,128,0.05)",borderRadius:3}}>✓ {ch}</div>);
function TH({cols}){return(<thead><tr>{cols.map(h=>(<th key={h} style={{padding:"6px 9px",borderBottom:`1px solid ${C.border}`,color:C.accent,textAlign:"left",fontWeight:"normal",fontSize:10,letterSpacing:"0.06em",whiteSpace:"nowrap",opacity:.85}}>{h}</th>))}</tr></thead>);}
function Grid(){return(<svg style={{position:"fixed",inset:0,width:"100%",height:"100%",pointerEvents:"none",zIndex:0}}><defs><pattern id="sg" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0L0 0 0 20" fill="none" stroke="rgba(0,229,255,0.035)" strokeWidth={0.5}/></pattern><pattern id="lg" width="100" height="100" patternUnits="userSpaceOnUse"><rect width="100" height="100" fill="url(#sg)"/><path d="M100 0L0 0 0 100" fill="none" stroke="rgba(0,229,255,0.065)" strokeWidth={1}/></pattern></defs><rect width="100%" height="100%" fill="url(#lg)"/></svg>);}

// ════════════════════════════════════════════════════════════
//  KEY DESIGN DECISION — I²C vs 1553 AS FOURTH BUS
// ════════════════════════════════════════════════════════════
// I²C hardware (PCA9517 buffer + TVS + BNX002 CMC + 2× JST-GH) REMAINS
// on both TRIHAT-1 and COMPHAT-1 PCBs. It is available for on-board
// sensor expansion (BMP388, ICM-42688, MS4525DO are already I²C1).
// I²C is NOT used as an inter-board bus because MIL-STD-1553 fills
// that role with superior noise immunity, deterministic timing, and
// hardware fault tolerance — critical for a UAV avionics bus.
//
// MIL-STD-1553B minimum hardware path on this design:
//   Holt HI-6130  (SPI BC/RT/MT, TQFP-48, 3.3V) — 1 per board
//   Bourns SM-1553-11 isolation xfmr (4.8×8.0mm, SMD) — 1 per board
//   75Ω stub resistors (0402) × 2 per board
//   JST-GH 4-pin connector × 2 per board (Bus-A in/out)
//
//  Leverages EXISTING SPI buses on both boards — no new micro needed.
//  Total new silicon: 2× HI-6130 + 2× SM-1553-11.
// ════════════════════════════════════════════════════════════

const PROTOCOLS = [
  { id:"eth", label:"Ethernet 100BASE-T", color:C.eth,
    topology:"Star / P2P (switch for N>2)", speed:"100 Mbps",
    maxNodes:"Switch-limited", wire:"6-pin JST-GH ×1",
    phy:"W5500 + HX1188NL magnetics", connectors:1,
    use:"High-bandwidth log · GCS relay · OTA · mission upload",
    priority:"High-bandwidth background", latency:"<1ms",
    addedRevH:false, weight:"~3g", terminators:"auto-MDIX",
    pinout:["GND","TX+","TX−","RX+","RX−","N/C"], jst:6 },
  { id:"can", label:"CAN FD (ISO 11898-1)", color:C.can,
    topology:"Bus daisy-chain (2× JST-GH Rev G)", speed:"1/4 Mbps FD",
    maxNodes:"≤32 practical", wire:"4-pin JST-GH ×2",
    phy:"MCP2518FD + MCP2562FD",
    use:"Real-time AHRS · ESC RPM · arm/disarm · mission commands",
    priority:"Real-time safety", latency:"<500µs",
    addedRevH:false, weight:"~2g", terminators:"120Ω endpoints",
    pinout:["GND","+5V","CANH","CANL"], jst:4 },
  { id:"rs4", label:"RS-485 / EIA-485", color:C.rs4,
    topology:"Bus half-duplex multi-drop", speed:"1 Mbps",
    maxNodes:"32 / segment", wire:"4-pin JST-GH ×2",
    phy:"MAX3485 SOT-23-8",
    use:"Secondary MAVLink · sensor aggregation · ESC config",
    priority:"Secondary telemetry", latency:"<2ms",
    addedRevH:false, weight:"~2g", terminators:"120Ω + 560Ω bias",
    pinout:["GND","+5V","A+","B−"], jst:4 },
  { id:"m53", label:"MIL-STD-1553B", color:C.m53,
    topology:"Dual-redundant bus (BC/RT, up to 31 RTs)", speed:"1 Mbps Manchester",
    maxNodes:"31 Remote Terminals + 1 BC", wire:"4-pin JST-GH ×2 (Bus-A dual-ended)",
    phy:"Holt HI-6130 SPI BC/RT/MT + Bourns SM-1553-11 xfmr",
    use:"Deterministic command/response · hard-real-time safety · fault-tolerant MIL-grade link",
    priority:"Deterministic hard-real-time", latency:"<1ms guaranteed",
    addedRevH:true, weight:"~5g per board · ~10g total", terminators:"75Ω stub R + xfmr coupling",
    pinout:["GND","SHIELD","BUS_A+","BUS_A−"], jst:4 },
];

const NODE_MATRIX = [
  {nodes:2, label:"Current (Pico 2 BC + CM4 RT-01)",
   eth:"Direct P2P 192.168.10.1/2", can:"2-node chain 120Ω both ends",
   rs4:"2-node chain 120Ω both ends", m53:"BC (Pico2) ↔ RT-01 (CM4) · deterministic 1ms frame"},
  {nodes:3, label:"+ nacelle controller RT-02",
   eth:"Add KSZ8795 switch or hub", can:"Insert in chain · move terminator",
   rs4:"Insert in chain · move terminator", m53:"BC polls RT-01 and RT-02 · no wiring change needed · just add to schedule"},
  {nodes:6, label:"+ 2 nacelles + 2 payloads",
   eth:"5-port managed switch", can:"5-node chain · terms at ends",
   rs4:"5-node bus · terms at ends", m53:"BC schedules 5 RTs in round-robin · 1ms frame still met at 1MHz"},
  {nodes:31, label:"Full 31-RT platform",
   eth:"GbE switch + VLANs", can:"Split into 2 buses >32",
   rs4:"Repeater at midpoint", m53:"1553 designed for exactly this — 31 RTs native, no protocol change"},
];

// ════════════════════════════════════════════════════════════
// DIAGRAM: 4-bus architecture
// ════════════════════════════════════════════════════════════
function FourBusDiagram(){
  const VW=740, VH=440;
  const busY={eth:110, can:175, rs4:225, m53:285};
  const busC={eth:C.eth, can:C.can, rs4:C.rs4, m53:C.m53};
  const busLabel={eth:"Ethernet 100BASE-T",can:"CAN FD  4Mbps",rs4:"RS-485  1Mbps",m53:"MIL-STD-1553B  1Mbps"};
  const busRole={eth:"High-BW background",can:"Safety-critical RT",rs4:"Secondary telemetry",m53:"Hard-RT deterministic"};
  const busDash={eth:"none",can:"none",rs4:"6 3",m53:"none"};
  const busW={eth:3,can:3,rs4:2.5,m53:4};
  const nodes=[{x:40,y:130,w:130,h:180,label:"PICO 2",sub:"TRIHAT-1 (Rev H)",c:C.accent,role:"BC"},{x:570,y:130,w:130,h:180,label:"CM4 LITE",sub:"COMPHAT-1 (Rev H)",c:C.green,role:"RT-01"}];

  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* Node blocks */}
      {nodes.map((n,i)=>(
        <g key={i}>
          <rect x={n.x} y={n.y} width={n.w} height={n.h} rx={6}
            fill={`${n.c}10`} stroke={n.c} strokeWidth={2}/>
          <text x={n.x+n.w/2} y={n.y+22} textAnchor="middle"
            fill={n.c} fontSize={11} fontFamily={M} fontWeight="bold">{n.label}</text>
          <text x={n.x+n.w/2} y={n.y+37} textAnchor="middle"
            fill={`${n.c}70`} fontSize={9} fontFamily={M}>{n.sub}</text>
          {/* 1553 role badge */}
          <rect x={n.x+(n.w-60)/2} y={n.y+46} width={60} height={16} rx={3}
            fill={`${C.m53}25`} stroke={C.m53} strokeWidth={1}/>
          <text x={n.x+n.w/2} y={n.y+58} textAnchor="middle"
            fill={C.m53} fontSize={8} fontFamily={M} fontWeight="bold">1553 {n.role}</text>
          {/* HI-6130 indicator */}
          <rect x={n.x+10} y={n.y+68} width={n.w-20} height={18} rx={2}
            fill={`${C.m53}12`} stroke={`${C.m53}50`} strokeWidth={0.8}/>
          <text x={n.x+n.w/2} y={n.y+80} textAnchor="middle"
            fill={`${C.m53}90`} fontSize={8} fontFamily={M}>HI-6130 (SPI)</text>
          {/* connector stacks */}
          {Object.entries(busY).map(([bus,by])=>{
            const col=busC[bus];
            const nx=i===0?n.x+n.w:n.x;
            return(<g key={bus}>
              <rect x={i===0?nx:nx-12} y={by-8} width={12} height={16} rx={2}
                fill={`${col}22`} stroke={col} strokeWidth={1.2}/>
            </g>);
          })}
          {/* I²C note (on-PCB only) */}
          <rect x={n.x+8} y={n.y+n.h-34} width={n.w-16} height={26} rx={3}
            fill="rgba(74,222,128,0.05)" stroke="rgba(74,222,128,0.2)"
            strokeWidth={0.8} strokeDasharray="3 2"/>
          <text x={n.x+n.w/2} y={n.y+n.h-21} textAnchor="middle"
            fill="rgba(74,222,128,0.5)" fontSize={7} fontFamily={M}>I²C on-PCB</text>
          <text x={n.x+n.w/2} y={n.y+n.h-10} textAnchor="middle"
            fill="rgba(74,222,128,0.35)" fontSize={7} fontFamily={M}>(local sensors only)</text>
        </g>
      ))}

      {/* Bus lines */}
      {Object.entries(busY).map(([bus,by])=>{
        const col=busC[bus]; const bw=busW[bus]; const bd=busDash[bus];
        const x1=nodes[0].x+nodes[0].w+12; const x2=nodes[1].x-12;
        const mid=(x1+x2)/2;
        return(<g key={bus}>
          <line x1={x1} y1={by} x2={x2} y2={by}
            stroke={col} strokeWidth={bw} strokeDasharray={bd} strokeLinecap="round"
            opacity={bus==="m53"?1:0.85}/>
          {/* 1553 gets double line for dual-redundant visual */}
          {bus==="m53"&&<line x1={x1} y1={by+5} x2={x2} y2={by+5}
            stroke={col} strokeWidth={1.5} strokeDasharray="4 4" opacity={0.4}/>}
          <rect x={mid-80} y={by-18} width={160} height={14} rx={3}
            fill={`${col}18`} stroke={`${col}44`} strokeWidth={0.8}/>
          <text x={mid} y={by-7} textAnchor="middle"
            fill={col} fontSize={8} fontFamily={M} fontWeight="bold">{busLabel[bus]}</text>
          <text x={mid} y={by+12} textAnchor="middle"
            fill={`${col}65`} fontSize={7} fontFamily={M}>{busRole[bus]}</text>
          {/* terminator symbols for buses with physical termination */}
          {(bus==="can"||bus==="rs4"||bus==="m53")&&(<>
            <rect x={x1+2} y={by-6} width={10} height={12} rx={2} fill={col} opacity={0.7}/>
            <text x={x1+7} y={by+3} textAnchor="middle" fill="rgba(0,0,0,0.8)" fontSize={5.5} fontFamily={M} fontWeight="bold">Ω</text>
            <rect x={x2-12} y={by-6} width={10} height={12} rx={2} fill={col} opacity={0.7}/>
            <text x={x2-7} y={by+3} textAnchor="middle" fill="rgba(0,0,0,0.8)" fontSize={5.5} fontFamily={M} fontWeight="bold">Ω</text>
          </>)}
          {/* 1553 transformer symbols */}
          {bus==="m53"&&(<>
            <ellipse cx={x1+26} cy={by} rx={10} ry={8} fill="none" stroke={col} strokeWidth={1.5} opacity={0.6}/>
            <text x={x1+26} y={by+3} textAnchor="middle" fill={col} fontSize={6} fontFamily={M}>T</text>
            <ellipse cx={x2-26} cy={by} rx={10} ry={8} fill="none" stroke={col} strokeWidth={1.5} opacity={0.6}/>
            <text x={x2-26} y={by+3} textAnchor="middle" fill={col} fontSize={6} fontFamily={M}>T</text>
          </>)}
        </g>);
      })}

      {/* Future node */}
      <rect x={290} y={360} width={160} height={50} rx={5}
        fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.15)"
        strokeWidth={1} strokeDasharray="6 3"/>
      <text x={370} y={381} textAnchor="middle" fill="rgba(255,255,255,0.88)"
        fontSize={9} fontFamily={M}>FUTURE NODE  RT-02…RT-31</text>
      <text x={370} y={397} textAnchor="middle" fill="rgba(255,255,255,0.2)"
        fontSize={7} fontFamily={M}>HI-6130 RT mode · tap CAN+RS485+1553 bus</text>
      {/* Tap lines */}
      {[[C.can,175],[C.rs4,225],[C.m53,285]].map(([col,by],i)=>(
        <g key={i}>
          <line x1={370} y1={by} x2={370} y2={360}
            stroke={col} strokeWidth={1.5} strokeDasharray="4 3" opacity={0.4}/>
          <circle cx={370} cy={by} r={4} fill={col} opacity={0.6}/>
        </g>
      ))}

      {/* Legend */}
      <rect x={8} y={8} width={210} height={90} rx={4}
        fill="rgba(0,0,0,0.55)" stroke="rgba(255,255,255,0.08)" strokeWidth={0.8}/>
      <text x={113} y={22} textAnchor="middle" fill={C.dimmer} fontSize={7}
        fontFamily={M} letterSpacing="1">4-BUS ARCHITECTURE  REV H</text>
      {Object.entries(busC).map(([bus,col],i)=>(
        <g key={bus}>
          <line x1={18} y1={32+i*17} x2={48} y2={32+i*17}
            stroke={col} strokeWidth={bus==="m53"?3.5:2.5}/>
          <text x={54} y={36+i*17} fill={col} fontSize={8} fontFamily={M}>
            {busLabel[bus]}</text>
        </g>
      ))}

      <text x={VW/2} y={14} textAnchor="middle" fill="rgba(0,229,255,0.22)"
        fontSize={8} fontFamily={M} letterSpacing="2">SERENITY TILTROTOR · MULTI-BUS · REV H</text>
      <text x={VW/2} y={VH-6} textAnchor="middle" fill="rgba(0,229,255,0.18)"
        fontSize={7} fontFamily={M}>I²C hardware present on both boards (local sensors) — not shown as inter-board bus</text>
    </svg>
  );
}

// ════════════════════════════════════════════════════════════
// DIAGRAM: HI-6130 SPI-to-1553 minimum hardware path
// ════════════════════════════════════════════════════════════
function Mil1553Diagram(){
  const VW=700, VH=380;
  const col=C.m53;
  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* ── Left board: TRIHAT-1 (BC) ── */}
      <rect x={10} y={40} width={170} height={290} rx={6}
        fill={`${col}06`} stroke={col} strokeWidth={1.8}/>
      <text x={95} y={58} textAnchor="middle" fill={col} fontSize={10} fontFamily={M} fontWeight="bold">TRIHAT-1</text>
      <text x={95} y={72} textAnchor="middle" fill={`${col}70`} fontSize={8} fontFamily={M}>PICO 2 — 1553 BC</text>

      {/* Pico SPI */}
      <rect x={20} y={82} width={70} height={40} rx={3}
        fill="rgba(0,229,255,0.08)" stroke={C.accent} strokeWidth={1}/>
      <text x={55} y={99} textAnchor="middle" fill={C.accent} fontSize={8} fontFamily={M} fontWeight="bold">PICO 2</text>
      <text x={55} y={111} textAnchor="middle" fill={`${C.accent}70`} fontSize={7} fontFamily={M}>SPI0 GP16-19</text>

      {/* HI-6130 */}
      <rect x={100} y={78} width={68} height={58} rx={4}
        fill={`${col}18`} stroke={col} strokeWidth={2}/>
      <text x={134} y={96} textAnchor="middle" fill={col} fontSize={9} fontFamily={M} fontWeight="bold">HI-6130</text>
      <text x={134} y={108} textAnchor="middle" fill={`${col}80`} fontSize={7} fontFamily={M}>BC/RT/MT</text>
      <text x={134} y={120} textAnchor="middle" fill={`${col}60`} fontSize={7} fontFamily={M}>TQFP-48</text>
      <text x={134} y={130} textAnchor="middle" fill={`${col}50`} fontSize={6} fontFamily={M}>7×7 mm</text>

      {/* SPI connection */}
      <line x1={90} y1={102} x2={100} y2={102}
        stroke={C.accent} strokeWidth={1.8} strokeDasharray="3 2"/>
      <text x={95} y={97} textAnchor="middle" fill={`${C.accent}60`} fontSize={6} fontFamily={M}>SPI</text>

      {/* 75Ω stub resistors */}
      <rect x={30} y={158} width={48} height={22} rx={2}
        fill="rgba(255,255,255,0.05)" stroke={`${col}50`} strokeWidth={1}/>
      <text x={54} y={168} textAnchor="middle" fill={`${col}70`} fontSize={7} fontFamily={M}>75Ω stub</text>
      <text x={54} y={176} textAnchor="middle" fill={`${col}50`} fontSize={6} fontFamily={M}>0402 ×2</text>

      {/* Isolation transformer SM-1553-11 */}
      <rect x={88} y={152} width={80} height={40} rx={4}
        fill={`${col}15`} stroke={col} strokeWidth={1.8}/>
      <text x={128} y={169} textAnchor="middle" fill={col} fontSize={8} fontFamily={M} fontWeight="bold">SM-1553-11</text>
      <text x={128} y={181} textAnchor="middle" fill={`${col}70`} fontSize={7} fontFamily={M}>Isolation xfmr</text>
      <text x={128} y={190} textAnchor="middle" fill={`${col}50`} fontSize={6} fontFamily={M}>4.8×8.0mm SMD</text>

      {/* J_1553_IN connector */}
      <rect x={20} y={214} width={54} height={56} rx={3}
        fill={`${col}12`} stroke={col} strokeWidth={1.2}/>
      <text x={47} y={229} textAnchor="middle" fill={col} fontSize={7} fontFamily={M} fontWeight="bold">J_1553_IN</text>
      {["GND","SHLD","BUS A+","BUS A−"].map((s,i)=>(
        <text key={s} x={47} y={240+i*8} textAnchor="middle" fill={`${col}60`} fontSize={5.5} fontFamily={M}>{s}</text>
      ))}
      <text x={47} y={265} textAnchor="middle" fill={`${col}50`} fontSize={5.5} fontFamily={M}>JST-GH 4P</text>

      {/* J_1553_OUT connector */}
      <rect x={94} y={214} width={54} height={56} rx={3}
        fill={`${col}12`} stroke={col} strokeWidth={1.2}/>
      <text x={121} y={229} textAnchor="middle" fill={col} fontSize={7} fontFamily={M} fontWeight="bold">J_1553_OUT</text>
      {["GND","SHLD","BUS A+","BUS A−"].map((s,i)=>(
        <text key={s} x={121} y={240+i*8} textAnchor="middle" fill={`${col}60`} fontSize={5.5} fontFamily={M}>{s}</text>
      ))}
      <text x={121} y={265} textAnchor="middle" fill={`${col}50`} fontSize={5.5} fontFamily={M}>JST-GH 4P</text>

      {/* 1553 end terminator note */}
      <rect x={20} y={278} width={148} height={20} rx={2}
        fill="rgba(255,230,0,0.08)" stroke={C.yellow} strokeWidth={0.8}/>
      <text x={94} y={291} textAnchor="middle" fill={C.yellow} fontSize={7} fontFamily={M}>Xfmr acts as termination · no discrete 75Ω term.</text>

      {/* ── Bus cable ── */}
      <line x1={180} y1={240} x2={250} y2={240}
        stroke={col} strokeWidth={4} strokeLinecap="round"/>
      <line x1={180} y1={252} x2={250} y2={252}
        stroke={col} strokeWidth={4} strokeLinecap="round"/>
      <rect x={192} y={228} width={46} height={14} rx={2}
        fill={`${col}20`} stroke={`${col}50`} strokeWidth={0.8}/>
      <text x={215} y={237} textAnchor="middle" fill={col} fontSize={6} fontFamily={M} fontWeight="bold">twisted</text>
      <text x={215} y={245} textAnchor="middle" fill={`${col}70`} fontSize={6} fontFamily={M}>shielded</text>
      <text x={215} y={262} textAnchor="middle" fill={`${col}50`} fontSize={6} fontFamily={M}>4-pin JST-GH</text>

      {/* ── Right board: COMPHAT-1 (RT) ── */}
      <rect x={250} y={40} width={170} height={290} rx={6}
        fill={`${col}06`} stroke={col} strokeWidth={1.8}/>
      <text x={335} y={58} textAnchor="middle" fill={col} fontSize={10} fontFamily={M} fontWeight="bold">COMPHAT-1</text>
      <text x={335} y={72} textAnchor="middle" fill={`${col}70`} fontSize={8} fontFamily={M}>CM4 — 1553 RT-01</text>

      <rect x={260} y={82} width={70} height={40} rx={3}
        fill="rgba(74,222,128,0.08)" stroke={C.green} strokeWidth={1}/>
      <text x={295} y={99} textAnchor="middle" fill={C.green} fontSize={8} fontFamily={M} fontWeight="bold">CM4</text>
      <text x={295} y={111} textAnchor="middle" fill={`${C.green}70`} fontSize={7} fontFamily={M}>SPI0 GPIO9-11</text>

      <rect x={340} y={78} width={68} height={58} rx={4}
        fill={`${col}18`} stroke={col} strokeWidth={2}/>
      <text x={374} y={96} textAnchor="middle" fill={col} fontSize={9} fontFamily={M} fontWeight="bold">HI-6130</text>
      <text x={374} y={108} textAnchor="middle" fill={`${col}80`} fontSize={7} fontFamily={M}>RT-01</text>
      <text x={374} y={120} textAnchor="middle" fill={`${col}60`} fontSize={7} fontFamily={M}>TQFP-48</text>
      <text x={374} y={130} textAnchor="middle" fill={`${col}50`} fontSize={6} fontFamily={M}>addr pins → 0x01</text>
      <line x1={330} y1={102} x2={340} y2={102}
        stroke={C.green} strokeWidth={1.8} strokeDasharray="3 2"/>

      <rect x={270} y={158} width={48} height={22} rx={2}
        fill="rgba(255,255,255,0.05)" stroke={`${col}50`} strokeWidth={1}/>
      <text x={294} y={168} textAnchor="middle" fill={`${col}70`} fontSize={7} fontFamily={M}>75Ω stub</text>
      <text x={294} y={176} textAnchor="middle" fill={`${col}50`} fontSize={6} fontFamily={M}>0402 ×2</text>

      <rect x={328} y={152} width={80} height={40} rx={4}
        fill={`${col}15`} stroke={col} strokeWidth={1.8}/>
      <text x={368} y={169} textAnchor="middle" fill={col} fontSize={8} fontFamily={M} fontWeight="bold">SM-1553-11</text>
      <text x={368} y={181} textAnchor="middle" fill={`${col}70`} fontSize={7} fontFamily={M}>Isolation xfmr</text>

      <rect x={260} y={214} width={54} height={56} rx={3}
        fill={`${col}12`} stroke={col} strokeWidth={1.2}/>
      <text x={287} y={229} textAnchor="middle" fill={col} fontSize={7} fontFamily={M} fontWeight="bold">J_1553_IN</text>
      {["GND","SHLD","BUS A+","BUS A−"].map((s,i)=>(
        <text key={s} x={287} y={240+i*8} textAnchor="middle" fill={`${col}60`} fontSize={5.5} fontFamily={M}>{s}</text>
      ))}

      <rect x={334} y={214} width={54} height={56} rx={3}
        fill={`${col}12`} stroke={col} strokeWidth={1.2}/>
      <text x={361} y={229} textAnchor="middle" fill={col} fontSize={7} fontFamily={M} fontWeight="bold">J_1553_OUT</text>
      {["GND","SHLD","BUS A+","BUS A−"].map((s,i)=>(
        <text key={s} x={361} y={240+i*8} textAnchor="middle" fill={`${col}60`} fontSize={5.5} fontFamily={M}>{s}</text>
      ))}

      <rect x={260} y={278} width={148} height={20} rx={2}
        fill="rgba(255,230,0,0.08)" stroke={C.yellow} strokeWidth={0.8}/>
      <text x={334} y={291} textAnchor="middle" fill={C.yellow} fontSize={7} fontFamily={M}>OPEN terminator — interior node (Rev G: BC was end)</text>

      {/* ── Future RT node ── */}
      <line x1={420} y1={246} x2={510} y2={246}
        stroke={col} strokeWidth={4} strokeLinecap="round" strokeDasharray="8 4" opacity={0.5}/>
      <line x1={420} y1={258} x2={510} y2={258}
        stroke={col} strokeWidth={4} strokeLinecap="round" strokeDasharray="8 4" opacity={0.5}/>
      <rect x={510} y={200} width={170} height={110} rx={6}
        fill="rgba(255,191,36,0.04)" stroke={`${col}35`} strokeWidth={1} strokeDasharray="6 3"/>
      <text x={595} y={222} textAnchor="middle" fill={`${col}50`} fontSize={9} fontFamily={M}>FUTURE RT-02…RT-31</text>
      <text x={595} y={238} textAnchor="middle" fill={`${col}35`} fontSize={8} fontFamily={M}>HI-6130 (RT mode)</text>
      <text x={595} y={252} textAnchor="middle" fill={`${col}35`} fontSize={7} fontFamily={M}>SM-1553-11 xfmr</text>
      <text x={595} y={266} textAnchor="middle" fill={`${col}35`} fontSize={7} fontFamily={M}>2× JST-GH 4P</text>
      <text x={595} y={283} textAnchor="middle" fill={`${col}30`} fontSize={7} fontFamily={M}>address pins set per node</text>
      <text x={595} y={296} textAnchor="middle" fill={C.yellow} fontSize={7} fontFamily={M}>← close term. on last node</text>
      <text x={595} y={309} textAnchor="middle" fill={`${col}30`} fontSize={7} fontFamily={M}>COMPHAT term. re-opens</text>

      {/* Labels */}
      <text x={350} y={14} textAnchor="middle" fill="rgba(255,191,36,0.3)"
        fontSize={9} fontFamily={M} letterSpacing="2">MIL-STD-1553B — MINIMUM HARDWARE — SPI-COUPLED HI-6130</text>
      <text x={350} y={VH-6} textAnchor="middle" fill="rgba(255,191,36,0.2)"
        fontSize={7} fontFamily={M}>No additional microcontroller — HI-6130 connects directly to existing Pico 2 SPI0 and CM4 SPI0</text>
    </svg>
  );
}

// ════════════════════════════════════════════════════════════
// DIAGRAM: 1553 frame timing
// ════════════════════════════════════════════════════════════
function FrameTimingDiagram(){
  const VW=680, VH=200;
  const col=C.m53;
  // 1ms minor frame — BC broadcasts schedule
  const frames=[
    {label:"BC→RT01",sublabel:"CMD word (RT-01 addr, RX, SA 0)",color:col,w:90},
    {label:"RT01→BC",sublabel:"STATUS + 8 data words (AHRS)",color:C.teal,w:110},
    {label:"BC→RT01",sublabel:"CMD word (RT-01, TX, SA 1)",color:col,w:90},
    {label:"RT01→BC",sublabel:"STATUS + 4 data words (RPM)",color:C.teal,w:70},
    {label:"GUARD",sublabel:"Inter-message gap",color:"rgba(255,255,255,0.15)",w:40},
    {label:"BC→RT02",sublabel:"Future node schedule",color:`${col}55`,w:80,dashed:true},
    {label:"...",sublabel:"",color:"rgba(255,255,255,0.08)",w:30},
  ];
  let x=30;
  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* timeline base */}
      <line x1={20} y1={100} x2={VW-20} y2={100} stroke={`${col}30`} strokeWidth={1}/>
      {/* 1ms frame bracket */}
      <line x1={30} y1={70} x2={30} y2={160} stroke={col} strokeWidth={1} opacity={0.4}/>
      <text x={30} y={65} textAnchor="start" fill={col} fontSize={8} fontFamily={M}>← 1ms MINOR FRAME (guaranteed) →</text>
      {frames.map((f,i)=>{
        const fx=x; x+=f.w;
        return(<g key={i}>
          <rect x={fx} y={80} width={f.w-3} height={40} rx={2}
            fill={f.color} stroke={`${col}40`} strokeWidth={0.8}
            strokeDasharray={f.dashed?"5 3":"none"} opacity={f.dashed?0.5:1}/>
          <text x={fx+f.w/2-1} y={96} textAnchor="middle"
            fill={WHITE} fontSize={7} fontFamily={M} fontWeight="bold">{f.label}</text>
          <text x={fx+f.w/2-1} y={108} textAnchor="middle"
            fill="rgba(255,255,255,0.65)" fontSize={5.5} fontFamily={M}>{f.sublabel}</text>
        </g>);
      })}
      {/* 1553 word structure below */}
      <text x={30} y={148} fill={`${col}80`} fontSize={8} fontFamily={M}>1553 word = 20 bits (Manchester) : 3 sync + 16 data + 1 parity · every word takes 20µs at 1MHz</text>
      <text x={30} y={162} fill={`${col}60`} fontSize={8} fontFamily={M}>Command word: RT-addr[4:0] · T/R · SA/MC[4:0] · word-count[4:0]  |  Status word: RT-addr[4:0] + 11 status bits</text>
      <text x={30} y={176} fill={`${col}40`} fontSize={7} fontFamily={M}>BC controls ALL bus traffic — no two nodes transmit simultaneously — hardware-enforced collision-free</text>
      <text x={VW/2} y={14} textAnchor="middle" fill="rgba(255,191,36,0.25)"
        fontSize={8} fontFamily={M} letterSpacing="2">1553B MINOR FRAME SCHEDULE — DETERMINISTIC 1ms</text>
    </svg>
  );
}

const WHITE="rgba(255,255,255,0.9)";

// ════════════════════════════════════════════════════════════
// TAB: OVERVIEW
// ════════════════════════════════════════════════════════════
function OverviewTab(){
  return(<div>
    <div style={{background:"rgba(255,191,36,0.06)",border:`1px solid rgba(255,191,36,0.25)`,borderRadius:4,padding:"14px 16px",marginBottom:20}}>
      <div style={{color:C.m53,fontFamily:M,fontSize:11,fontWeight:"bold",marginBottom:8,letterSpacing:"0.08em"}}>REV H CHANGE — I²C → MIL-STD-1553B AS FOURTH ACTIVE BUS</div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:20}}>
        <div>
          <KV k="4th bus" v="MIL-STD-1553B replaces I²C as inter-board protocol" vc={C.m53}/>
          <KV k="New ICs per board" v="1× HI-6130 (TQFP-48) + 1× SM-1553-11 xfmr" vc={C.m53}/>
          <KV k="SPI reuse" v="HI-6130 connects to existing SPI0 — no new bus" vc={C.green}/>
          <KV k="I²C hardware" v="Stays on PCB — local sensor bus only (not inter-board)" vc={C.i2c}/>
        </div>
        <div>
          <KV k="Weight delta (Rev H)" v="~5g per board · ~10g total aircraft"/>
          <KV k="Cost delta" v="~$18 per board (HI-6130 ~$12 + SM-1553-11 ~$4 + passives)"/>
          <KV k="Max RTs" v="31 Remote Terminals — native to protocol" vc={C.m53}/>
          <KV k="Determinism" v="Hard real-time 1ms frame — BC schedules all traffic" vc={C.lime}/>
        </div>
      </div>
    </div>
    <SH t="4-Bus Architecture (Rev H)" mt={0}/>
    <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:8,marginBottom:20}}>
      <FourBusDiagram/>
    </div>
    <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:12}}>
      {PROTOCOLS.map(p=>(
        <div key={p.id} style={{padding:"10px 12px",border:`1px solid ${p.color}44`,background:`${p.color}07`,borderRadius:4}}>
          <div style={{color:p.color,fontFamily:M,fontSize:11,fontWeight:"bold",marginBottom:6}}>{p.label}</div>
          <div style={{color:C.dim,fontFamily:M,fontSize:9,marginBottom:4}}>{p.topology}</div>
          <div style={{color:p.color,fontFamily:M,fontSize:13,fontWeight:"bold"}}>{p.speed}</div>
          <div style={{color:C.dimmer,fontFamily:M,fontSize:9,marginTop:4}}>{p.use.split("·")[0]}</div>
          {p.addedRevH&&<div style={{marginTop:6,color:C.m53,fontFamily:M,fontSize:8,border:`1px solid ${C.m53}44`,padding:"1px 6px",borderRadius:2,display:"inline-block"}}>★ NEW Rev H</div>}
        </div>
      ))}
    </div>
    <div style={{marginTop:18,padding:"12px 14px",border:`1px solid rgba(74,222,128,0.2)`,background:"rgba(74,222,128,0.04)",borderRadius:4,fontFamily:M,fontSize:10,color:C.dim,lineHeight:1.8}}>
      <span style={{color:C.i2c,fontWeight:"bold"}}>I²C status (Rev H):</span> Both TRIHAT-1 and COMPHAT-1 retain the PCA9517 buffer, PRTR5V0U2X TVS, BNX002 choke, and 2× JST-GH I²C connectors from Rev G. The I²C bus serves its original purpose — connecting on-board sensors (ICM-42688-P, BMP388, MS4525DO) and future expansion peripherals. It is explicitly <span style={{color:C.yellow}}>not</span> used as an inter-board data path; MIL-STD-1553B provides a superior physical and protocol basis for that role.
    </div>
  </div>);
}

// ════════════════════════════════════════════════════════════
// TAB: MIL-STD-1553 DESIGN
// ════════════════════════════════════════════════════════════
function Mil1553Tab(){
  return(<div>
    <SH t="MIL-STD-1553B — Minimum Hardware Path" mt={0} c={C.m53}/>
    <div style={{border:`1px solid ${C.m53}33`,borderRadius:4,background:"rgba(255,191,36,0.01)",padding:8,marginBottom:18}}>
      <Mil1553Diagram/>
    </div>
    <div style={{border:`1px solid ${C.m53}22`,borderRadius:4,background:"rgba(255,191,36,0.01)",padding:8,marginBottom:18}}>
      <FrameTimingDiagram/>
    </div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="HI-6130 — The Minimum Hardware Choice" mt={0} c={C.m53}/>
        <KV k="Manufacturer" v="Holt Integrated Circuits (holtIC.com)"/>
        <KV k="Part number" v="HI-6130" vc={C.m53}/>
        <KV k="Function" v="Full MIL-STD-1553B BC / RT / Bus Monitor — single chip"/>
        <KV k="Host interface" v="SPI — connects directly to Pico 2 SPI0 and CM4 SPI0" vc={C.green}/>
        <KV k="Supply voltage" v="3.3V logic · 5V analog bus (from board +5V rail)"/>
        <KV k="Package" v="TQFP-48 · 7×7mm · 0.5mm pitch"/>
        <KV k="1553 mode" v="Selectable BC / RT / MT via host register write over SPI"/>
        <KV k="RT address" v="Set by hardware pins RA[4:0] — no firmware address config"/>
        <KV k="Internal RAM" v="128 words × 16-bit — stores complete message history"/>
        <KV k="Interrupt output" v="Active-low IRQ → Pico 2 GP18 / CM4 GPIO24"/>
        <KV k="Operating temp" v="−40°C to +85°C commercial · −55°C to +125°C military"/>
        <KV k="Bit error detect" v="Manchester decode · parity · word count · protocol check"/>
        <SH t="SM-1553-11 — Isolation Transformer" c={C.m53}/>
        <KV k="Manufacturer" v="Bourns / Pulse Engineering"/>
        <KV k="Function" v="Dual-port 1553 isolation transformer"/>
        <KV k="Turns ratio" v="1:1 · two separate windings"/>
        <KV k="Footprint" v="4.8×8.0mm SMD · 3mm height"/>
        <KV k="Isolation" v="1500Vrms bus-to-logic"/>
        <KV k="Replaces" v="Discrete transformer + stub resistors — integrated solution"/>
        <KV k="Bus coupling" v="Direct-coupled via SM-1553-11 primary winding"/>
        <Note c={C.m53} ch="The SM-1553-11 integrates the isolation function that MIL-STD-1553 requires between the transceiver and the bus. The HI-6130 drives the transformer primary; the transformer secondary drives the differential bus. No discrete capacitors or large air-core transformers needed — total component count: IC + transformer + 2× 75Ω 0402 + bypass caps."/>
      </div>
      <div>
        <SH t="Why MIL-STD-1553 Over I²C?" mt={0} c={C.m53}/>
        {[["Hard-real-time determinism","1553 is a command/response protocol with a fixed schedule controlled entirely by the Bus Controller. Every message has a defined slot in the 1ms minor frame. No collisions, no retries, no latency jitter — unlike I²C which can be stretched by clock stretching or NAK responses."],
          ["Hardware fault tolerance","Dual redundant bus (Bus A + Bus B) is intrinsic to 1553. If Bus A fails (wire break, transceiver fault), Bus B automatically takes over. I²C has no fault tolerance — a single stuck SDA line halts the entire bus."],
          ["EMI immunity on a UAV","1553 uses 20Vpp differential Manchester encoding with transformer coupling. The isolation transformer provides galvanic separation from the bus. This is far superior to I²C's 3.3V open-drain signalling in the EDF motor noise environment of this drone."],
          ["Proven aerospace pedigree","1553 has been used in F-16, F/A-18, Eurofighter, CH-47, virtually every military aircraft since 1978. Its robustness under vibration, EMI, and temperature extremes is the reason to choose it over I²C for any aerospace application."],
          ["Leverages existing SPI","The HI-6130 uses SPI — already present on both boards. Adding 1553 requires zero new microcontroller silicon, zero new firmware bus drivers beyond SPI register reads/writes. The protocol stack is inside the HI-6130."],
        ].map(([t,d],i)=>(<div key={i} style={{marginBottom:12}}><div style={{color:C.m53,fontFamily:M,fontSize:10,fontWeight:"bold",marginBottom:3}}>{t}</div><div style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.7}}>{d}</div></div>))}
        <Warn ch="MIL-STD-1553 specifies the bus impedance at 70-85Ω (characteristic). The SM-1553-11 transformer and 75Ω stub resistors satisfy this. DO NOT exceed 20m total bus length at 1MHz. At this drone's scale (<1m) this is never a concern."/>
        <Good ch="The HI-6130 passes all 1553B electrical and protocol compliance tests. It is used in aerospace programs including UAVs. The SPI interface means the Pico 2 and CM4 can treat it as a simple peripheral register file."/>
      </div>
    </div>

    <SH t="SPI Pin Assignment (Rev H)"/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <div style={{color:C.accent,fontFamily:M,fontSize:10,fontWeight:"bold",marginBottom:8}}>TRIHAT-1 — Pico 2 SPI0</div>
        <KV k="SCK"  v="GP16 (SPI0 clock)"/>
        <KV k="MOSI" v="GP19 (SPI0 TX → HI-6130 SDI)"/>
        <KV k="MISO" v="GP20 (SPI0 RX ← HI-6130 SDO)" vc={C.green}/>
        <KV k="CSN"  v="GP17 (SPI0 CS → HI-6130 CS̄)"/>
        <KV k="IRQ"  v="GP18 (input, active-low interrupt from HI-6130)"/>
        <KV k="RESET" v="GP21 (output, active-low HI-6130 hardware reset)"/>
        <Note c={C.accent} ch="SPI0 is not shared with any other device on TRIHAT-1 in this configuration. The HI-6130 has its own dedicated CS on GP17, allowing future SPI0 bus sharing if needed."/>
      </div>
      <div>
        <div style={{color:C.green,fontFamily:M,fontSize:10,fontWeight:"bold",marginBottom:8}}>COMPHAT-1 — CM4 SPI0</div>
        <KV k="SCLK"  v="GPIO11 (SPI0 clock)"/>
        <KV k="MOSI"  v="GPIO10 (SPI0 TX → HI-6130 SDI)"/>
        <KV k="MISO"  v="GPIO9  (SPI0 RX ← HI-6130 SDO)" vc={C.green}/>
        <KV k="CE0"   v="GPIO8  (SPI0 CE0 → HI-6130 CS̄)"/>
        <KV k="IRQ"   v="GPIO25 (input, active-low interrupt)"/>
        <KV k="RESET" v="GPIO24 (output, active-low reset)"/>
        <Note c={C.green} ch="CM4 SPI0 is shared with the MCP2518FD CAN controller on CE1 (GPIO7). The HI-6130 uses CE0 (GPIO8). Both devices can coexist on SPI0 with separate chip-selects — standard SPI bus sharing."/>
      </div>
    </div>
  </div>);
}

// ════════════════════════════════════════════════════════════
// TAB: PROTOCOL COMPARISON (updated with 1553, I²C footnoted)
// ════════════════════════════════════════════════════════════
function ComparisonTab(){
  const criteria=[
    {c:"Standard body",     eth:"IEEE 802.3",   can:"ISO 11898",   rs4:"TIA/EIA-485",   m53:"MIL-STD-1553B · DO-160"},
    {c:"Physical layer",    eth:"4-pair diff",  can:"2-wire diff", rs4:"2-wire diff",   m53:"Xfmr-coupled diff · 20Vpp"},
    {c:"Speed",             eth:"100 Mbps",     can:"4 Mbps FD",   rs4:"10 Mbps",       m53:"1 Mbps Manchester"},
    {c:"Topology",          eth:"Star/switch",  can:"Linear bus",  rs4:"Linear bus",    m53:"Linear bus · dual-redundant"},
    {c:"Max nodes",         eth:"Switch-ltd",   can:"32 practical",rs4:"32/segment",    m53:"31 RTs + 1 BC"},
    {c:"Determinism",       eth:"Best-effort",  can:"Priority-based",rs4:"UART frame",  m53:"Hard RT · 1ms frame, guaranteed"},
    {c:"Fault tolerance",   eth:"None",         can:"Error frame",  rs4:"None",         m53:"Dual bus A/B · auto-failover"},
    {c:"EMI immunity",      eth:"Good",         can:"Excellent",    rs4:"Excellent",    m53:"Exceptional · xfmr isolation"},
    {c:"Bus voltage",       eth:"Differential", can:"5V bus",       rs4:"5V bus",       m53:"20Vpp bus · xfmr-coupled"},
    {c:"Galvanic isolation",eth:"Via magnetics", can:"None",        rs4:"None",         m53:"Built-in (SM-1553-11 xfmr)"},
    {c:"Collision handling",eth:"CSMA/CD",      can:"CSMA/CA prio", rs4:"DE/RE turns",  m53:"None — BC owns all turns"},
    {c:"Latency guarantee", eth:"None",         can:"~500µs worst", rs4:"~2ms worst",   m53:"Bounded — 1ms frame hard"},
    {c:"Host interface",    eth:"W5500 SPI",    can:"MCP2518 SPI",  rs4:"UART",         m53:"HI-6130 SPI — same bus"},
    {c:"New ICs / board",   eth:"already on",  can:"already on",   rs4:"1× MAX3485",   m53:"1× HI-6130 + 1× SM-1553-11"},
    {c:"IC package",        eth:"LQFP-48",     can:"SOIC-8",        rs4:"SOT-23-8",     m53:"TQFP-48 + 4.8×8mm xfmr"},
    {c:"Cable weight / m",  eth:"~8g",          can:"~3g",          rs4:"~3g",          m53:"~4g (shielded twisted pair)"},
    {c:"Use case",          eth:"BW, config",  can:"Safety ctrl",  rs4:"Secondary MAV", m53:"Deterministic safety + MIL"},
    {c:"Extensibility",     eth:"Add switch",  can:"Insert node",  rs4:"Insert node",   m53:"Add RT · BC reschedules only"},
  ];
  const colC={eth:C.eth,can:C.can,rs4:C.rs4,m53:C.m53};
  const colH={eth:"ETHERNET",can:"CAN FD",rs4:"RS-485",m53:"MIL-STD-1553B ★"};
  return(<div>
    <div style={{background:"rgba(74,222,128,0.04)",border:`1px solid rgba(74,222,128,0.2)`,borderRadius:4,padding:"10px 14px",marginBottom:16,fontFamily:M,fontSize:10,color:C.dim}}>
      <span style={{color:C.i2c,fontWeight:"bold"}}>I²C (not listed as 4th bus):</span> Hardware remains on both boards (PCA9517 + TVS + CMC + connectors). Used for on-board sensor chain only. For comparison — I²C would score: topology=wired-AND bus, speed=400kHz–1MHz, latency=variable (clock stretch), EMI immunity=poor without buffer, fault tolerance=none, determinism=none. MIL-STD-1553B is categorically superior for inter-board use.
    </div>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <thead><tr>
          <th style={{padding:"6px 10px",borderBottom:`1px solid ${C.border}`,color:C.dim,fontWeight:"normal",fontSize:10,textAlign:"left",minWidth:150}}>CRITERION</th>
          {Object.entries(colH).map(([k,v])=>(<th key={k} style={{padding:"6px 10px",borderBottom:`1px solid ${colC[k]}55`,color:colC[k],fontWeight:"bold",fontSize:10,textAlign:"center",whiteSpace:"nowrap"}}>{v}</th>))}
        </tr></thead>
        <tbody>{criteria.map((row,i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.02)":"transparent"}}>
            <td style={{padding:"5px 10px",color:C.dim,fontFamily:M,fontSize:10,whiteSpace:"nowrap"}}>{row.c}</td>
            {["eth","can","rs4","m53"].map(k=>(
              <td key={k} style={{padding:"5px 10px",color:colC[k],fontFamily:M,fontSize:10,textAlign:"center",lineHeight:1.4}}>{row[k]}</td>
            ))}
          </tr>
        ))}</tbody>
      </table>
    </div>
  </div>);
}

// ════════════════════════════════════════════════════════════
// TAB: EXTENSIBILITY
// ════════════════════════════════════════════════════════════
function ExtensibilityTab(){
  const [nodes,setNodes]=useState(2);
  const row=NODE_MATRIX.find(r=>r.nodes===nodes)||NODE_MATRIX[0];
  return(<div>
    <div style={{display:"flex",gap:6,marginBottom:18,flexWrap:"wrap"}}>
      {NODE_MATRIX.map(r=>(<button key={r.nodes} onClick={()=>setNodes(r.nodes)} style={{background:nodes===r.nodes?"rgba(0,229,255,0.09)":"transparent",border:`1px solid ${nodes===r.nodes?C.accent:"rgba(0,229,255,0.15)"}`,color:nodes===r.nodes?C.accent:C.dimmer,padding:"5px 14px",fontFamily:M,fontSize:10,cursor:"pointer",borderRadius:2}}>{r.nodes} Nodes — {r.label}</button>))}
    </div>
    {row&&(<div style={{display:"grid",gridTemplateColumns:"repeat(2,1fr)",gap:14,marginBottom:20}}>
      {[["eth",C.eth,"ETHERNET",row.eth],["can",C.can,"CAN FD",row.can],["rs4",C.rs4,"RS-485",row.rs4],["m53",C.m53,"MIL-STD-1553B",row.m53]].map(([k,c,l,v])=>(
        <div key={k} style={{padding:"12px 14px",border:`1px solid ${c}44`,background:`${c}07`,borderRadius:4}}>
          <div style={{color:c,fontFamily:M,fontSize:11,fontWeight:"bold",marginBottom:6}}>{l}</div>
          <div style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.7}}>{v}</div>
        </div>
      ))}
    </div>)}

    <SH t="Why 1553 Scales Best"/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <Note c={C.m53} ch="MIL-STD-1553 is the only protocol in this design where N-node scaling requires ZERO hardware changes to existing nodes. Adding RT-02: plug into J_1553_OUT on COMPHAT-1, plug J_1553_OUT of new node to nothing (or next node). Update BC frame schedule table in firmware to poll RT-02. That's it. No termination to move (transformer coupling handles it), no address assignment (hardware pins RA[4:0] on HI-6130), no configuration propagation."/>
        <Note c={C.can} ch="CAN FD scales well but requires moving the 120Ω terminator when adding nodes. Small effort but it is a physical change. 1553 has no such requirement — transformer coupling provides inherent impedance matching at each tap."/>
      </div>
      <div>
        <Note c={C.rs4} ch="RS-485 also requires terminator management when adding nodes. Additionally, the DE/RE direction-control pin adds a firmware responsibility per node. Still excellent, but 1553 requires less operator intervention at scale."/>
        <Note c={C.eth} ch="Ethernet needs a managed switch at N=3. The switch adds cost (~$5), weight (~7g), and PCB area. For N>4 nodes this is the clear winner on bandwidth, but for N<6 nodes the overhead is disproportionate."/>
        <Good ch="For the Serenity drone's target application (2 to 6 avionics nodes), MIL-STD-1553 offers the best combination of determinism, fault tolerance, EMI immunity, and zero-configuration extensibility of any protocol in this set."/>
      </div>
    </div>
  </div>);
}

// ════════════════════════════════════════════════════════════
// TAB: PCB CHANGES
// ════════════════════════════════════════════════════════════
function PCBTab(){
  return(<div>
    <SH t="TRIHAT-1 Rev H — Component Additions" mt={0} c={C.m53}/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24,marginBottom:20}}>
      <div>
        <KV k="U_1553" v="HI-6130 · TQFP-48 · 7×7mm · at 52mm from left edge"/>
        <KV k="T_1553" v="SM-1553-11 · SMD xfmr · 4.8×8mm · next to J_1553_IN"/>
        <KV k="J_1553_IN" v="JST-GH 1.25mm 4-pin · left board edge"/>
        <KV k="J_1553_OUT" v="JST-GH 1.25mm 4-pin · right board edge"/>
        <KV k="R_STUB1/2" v="75Ω 0402 · in series with xfmr primary winding leads"/>
        <KV k="C_DECOUP" v="100nF 0402 + 10µF 0402 at HI-6130 VDD and VDDIO"/>
        <KV k="GPIO added" v="GP18 (IRQ in) · GP17 (CSN) · GP21 (RESET out)"/>
        <KV k="SPI0 reuse" v="GP16/GP19/GP20 — existing SPI0 bus"/>
        <KV k="Board size" v="65×56mm (same as Rev G · I²C components already account for extra width)"/>
        <KV k="I²C stays" v="PCA9517 + TVS + BNX002 + J_I2C_IN/OUT unchanged" vc={C.i2c}/>
      </div>
      <div>
        <KV k="Placement note" v="HI-6130 TQFP-48 should be placed away from the ICM-42688 IMU — 1553 transformer can radiate field harmonics if placed within 5mm of magnetometer or IMU"/>
        <KV k="Layer routing" v="1553 bus traces route on F.Cu · keep ≥2mm from SPI traces · do not route under HI-6130"/>
        <KV k="Transformer placement" v="SM-1553-11 primary side faces HI-6130 · secondary faces board edge connectors"/>
        <KV k="Shield connection" v="JST-GH pin 2 (SHIELD) connects to chassis GND via 10nF cap (AC-coupled) — NOT DC ground · standard 1553 practice"/>
        <KV k="RA address pins" v="HI-6130 RA[4:0] on TRIHAT-1: all pulled low = BC mode (addr 0 = BC by convention)"/>
        <KV k="RA address pins" v="HI-6130 RA[4:0] on COMPHAT-1: RA0 pulled HIGH, rest low = RT address 1"/>
        <Note c={C.m53} ch="TQFP-48 at 0.5mm pitch requires standard 4-layer PCB soldering practice. JLCPCB offers TQFP-48 assembly. The HI-6130 is in JLCPCB's extended parts library — specify part number HI-6130CBI during assembly order."/>
      </div>
    </div>

    <SH t="Cable Specification" c={C.m53}/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:16}}>
      <div>
        <KV k="Cable type" v="Belden 3084A or equivalent · twinax shielded"/>
        <KV k="Impedance" v="78Ω characteristic (closest to 1553 spec 70–85Ω)"/>
        <KV k="Shielding" v="100% foil + braid · drain wire"/>
        <KV k="Gauge" v="24AWG twisted pair"/>
        <KV k="JST-GH crimp" v="Pins 1–4: GND · SHIELD_DRAIN · BUS_A+ · BUS_A−"/>
        <KV k="Cable colour" v="Gold/yellow outer jacket — matches 1553 identity colour"/>
        <KV k="Max length" v="1.0m between nodes at 1MHz (well within 20m spec limit)"/>
      </div>
      <div>
        <KV k="Shield termination" v="Drain wire to JST-GH pin 2 on BOTH ends · grounded via 10nF at each board"/>
        <KV k="Twists" v="Min 12 twists/300mm — cable manufacturer standard" vc={C.green}/>
        <KV k="Bending radius" v="Min 15mm — JST-GH cable standard" vc={C.green}/>
        <KV k="Routing" v="Route along existing keel spine · separate from RS-485 by ≥10mm · separate from CAN by ≥10mm"/>
        <Note c={C.m53} ch="For the Serenity's 2-node 120mm inter-board run, any twisted shielded pair with ≥70Ω impedance will work. Belden 3084A is the precise aviation standard cable, but a quality RC hobby servo extension cable with foil shield is electrically adequate at this length."/>
      </div>
    </div>
  </div>);
}

// ════════════════════════════════════════════════════════════
// TAB: BOM DELTA (Rev H vs Rev G)
// ════════════════════════════════════════════════════════════
const BOM_H=[
  {cat:"1553",qty:2,ref:"U_1553_T",part:"HI-6130 BC/RT/MT (TRIHAT-1)",     pkg:"TQFP-48",est:"$12ea",col:C.m53,note:"Holt IC · SPI BC/RT/MT · 7×7mm"},
  {cat:"1553",qty:2,ref:"U_1553_C",part:"HI-6130 BC/RT/MT (COMPHAT-1)",    pkg:"TQFP-48",est:"$12ea",col:C.m53,note:"Same IC · RA[4:0] pins set to RT-01"},
  {cat:"1553",qty:2,ref:"T_1553_T",part:"SM-1553-11 isolation xfmr (TRIHAT)", pkg:"SMD 4.8×8mm",est:"$4ea",col:C.m53,note:"Bourns · 1500Vrms · dual-port"},
  {cat:"1553",qty:2,ref:"T_1553_C",part:"SM-1553-11 isolation xfmr (COMPHAT)",pkg:"SMD 4.8×8mm",est:"$4ea",col:C.m53,note:"Same part both boards"},
  {cat:"1553",qty:8,ref:"R_STUB",  part:"75Ω 0402 stub resistors (2 per board end × 2 boards)",pkg:"0402",est:"$0.05ea",col:C.m53,note:"Series stub in xfmr primary leads"},
  {cat:"1553",qty:8,ref:"C_1553",  part:"100nF/10µF 0402 decoupling caps (per HI-6130)",pkg:"0402",est:"$0.05ea",col:C.m53,note:"HI-6130 VDD, VDDIO, VDDBUS decoupling"},
  {cat:"1553",qty:4,ref:"J_1553",  part:"JST-GH 1.25mm 4-pin (J_1553_IN + J_1553_OUT × 2 boards)",pkg:"SMD",est:"$0.60ea",col:C.m53,note:"GND · SHIELD · BUS_A+ · BUS_A−"},
  {cat:"1553",qty:1,ref:"CAB_1553",part:"1553 twisted shielded cable JST-GH 4P × 150mm",pkg:"cable",est:"$5",col:C.m53,note:"Belden 3084A equivalent · 78Ω twinax"},
  // I²C hardware retained (moved from Rev G BOM, now labelled as on-PCB only)
  {cat:"I²C (on-PCB)",qty:2,ref:"U_BUF",part:"PCA9517 I²C buffer (both boards, retained Rev G)",pkg:"SOT-23-6",est:"already in BOM",col:C.i2c,note:"Local sensor bus only — not inter-board"},
  {cat:"I²C (on-PCB)",qty:2,ref:"U_TVS",part:"PRTR5V0U2X TVS (both boards, retained)",pkg:"SOT-363",est:"already in BOM",col:C.i2c,note:"ESD protection on I²C lines"},
  {cat:"I²C (on-PCB)",qty:4,ref:"J_I2C",part:"JST-GH I²C connectors (retained, available for expansion)",pkg:"SMD",est:"already in BOM",col:C.i2c,note:"Available for future sensor nodes"},
];
const CAT_D={...{CAN:C.can,"RS-485":C.rs4,"MIL-STD-1553":C.m53},"1553":C.m53,"I²C (on-PCB)":C.i2c};

function BomTab(){
  const [cf,setCf]=useState("All");
  const rows=cf==="All"?BOM_H:BOM_H.filter(b=>b.cat===cf);
  const newCost=BOM_H.filter(b=>!b.est.includes("already")).reduce((s,b)=>{
    const u=parseFloat(b.est.replace("$","").replace("ea",""))||0; return s+b.qty*u;
  },0);
  return(<div>
    <div style={{background:"rgba(255,191,36,0.06)",border:`1px solid rgba(255,191,36,0.2)`,borderRadius:4,padding:"10px 14px",marginBottom:14,fontFamily:M,fontSize:10,color:C.dim}}>
      <span style={{color:C.m53,fontWeight:"bold"}}>Rev H delta over Rev G:</span> Adds 2× HI-6130 + 2× SM-1553-11 + passives + connectors + cable. Rev G RS-485 and CAN hardware unchanged. I²C hardware (PCA9517 etc.) already in Rev G BOM — no additional cost here.
    </div>
    <div style={{display:"flex",gap:5,flexWrap:"wrap",marginBottom:12}}>
      {["All","1553","I²C (on-PCB)"].map(c=>(<button key={c} onClick={()=>setCf(c)} style={{background:cf===c?`${CAT_D[c]||C.accent}20`:"transparent",border:`1px solid ${cf===c?CAT_D[c]||C.accent:"rgba(0,229,255,0.14)"}`,color:cf===c?CAT_D[c]||C.accent:C.dimmer,padding:"3px 10px",fontFamily:M,fontSize:9,cursor:"pointer",borderRadius:2}}>{c}</button>))}
    </div>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["CAT","QTY","REF","PART","PKG","COST","NOTES"]}/>
        <tbody>{rows.map((b,i)=>(<tr key={i} style={{background:b.cat.includes("I²C")?"rgba(74,222,128,0.04)":i%2===0?"rgba(0,229,255,0.02)":"transparent",verticalAlign:"top"}}>
          <td style={{padding:"5px 8px"}}><span style={{color:b.col,border:`1px solid ${b.col}40`,padding:"1px 5px",borderRadius:2,fontSize:9,whiteSpace:"nowrap"}}>{b.cat}</span></td>
          <td style={{padding:"5px 8px",color:C.accent,fontWeight:"bold",textAlign:"center"}}>{b.qty}</td>
          <td style={{padding:"5px 8px",color:C.yellow,fontSize:9,whiteSpace:"nowrap"}}>{b.ref}</td>
          <td style={{padding:"5px 8px",color:b.cat.includes("I²C")?`${C.i2c}80`:C.text}}>{b.part}</td>
          <td style={{padding:"5px 8px",color:C.dimmer,whiteSpace:"nowrap",fontSize:9}}>{b.pkg}</td>
          <td style={{padding:"5px 8px",color:b.est.includes("already")?C.dimmer:C.green,fontWeight:"bold",whiteSpace:"nowrap"}}>{b.est}</td>
          <td style={{padding:"5px 8px",color:C.dim,fontSize:9}}>{b.note}</td>
        </tr>))}</tbody>
        {cf==="All"&&(<tfoot>
          <tr style={{borderTop:`1px solid ${C.border}`}}>
            <td colSpan={5} style={{padding:"8px",color:C.m53,textAlign:"right",fontSize:11}}>REV H NEW HARDWARE TOTAL</td>
            <td style={{padding:"8px",color:C.yellow,fontSize:16,fontWeight:"bold"}}>~${newCost.toFixed(0)}</td>
            <td/>
          </tr>
          <tr>
            <td colSpan={5} style={{padding:"6px 8px",color:C.green,textAlign:"right",fontSize:10}}>Weight delta (new hardware)</td>
            <td style={{padding:"6px 8px",color:C.green,fontWeight:"bold"}}>~10g</td>
            <td/>
          </tr>
        </tfoot>)}
      </table>
    </div>
  </div>);
}

// ════════════════════════════════════════════════════════════
// APP
// ════════════════════════════════════════════════════════════
const TABS=["Overview","MIL-STD-1553","Comparison","Extensibility","PCB Changes","BOM Delta"];

_ODFontLoader();
export default function App(){
  const [tab,setTab]=useState("Overview");
  return(<div style={{minHeight:"100vh",background:C.bg,color:C.text,fontFamily:M}}>
    <Grid/>
    <div style={{background:"rgba(163,230,53,0.06)",borderBottom:`1px solid rgba(163,230,53,0.2)`,padding:"6px 24px",fontFamily:M,fontSize:8,color:"rgba(163,230,53,0.6)",lineHeight:1.6}}>
      © 2026 Steve Griffing, PE(CSE) [Control Systems Engineering], CISSP-ISSEP, CPP · CC BY 4.0 · Hull: Peter Farell CC BY 4.0 · Nozzle: BamJr CC BY 4.0 · Visual inspiration: Firefly/Serenity © Joss Whedon/Mutant Enemy/Universal — Fan engineering work
    </div>
    <div style={{position:"relative",zIndex:1,borderBottom:`1px solid ${C.border}`,padding:"14px 24px 12px"}}>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",flexWrap:"wrap",gap:12}}>
        <div>
          <div style={{color:`${C.m53}55`,fontSize:9,letterSpacing:"0.2em",marginBottom:4}}>SERENITY TILTROTOR · CONNECTIVITY · REV H</div>
          <h1 style={{margin:0,fontSize:18,fontWeight:"normal",color:"#fff",letterSpacing:"0.07em"}}>MULTI-BUS DATA ARCHITECTURE</h1>
          <div style={{color:"rgba(0,229,255,0.45)",fontSize:10,marginTop:3}}>
            Ethernet · CAN FD (daisy-chain) · RS-485 · <span style={{color:C.m53,fontWeight:"bold"}}>MIL-STD-1553B ★</span>
            <span style={{color:`${C.i2c}60`,marginLeft:12,fontSize:9}}> + I²C on-PCB sensor bus (not inter-board)</span>
          </div>
        </div>
        <div style={{textAlign:"right",fontFamily:M}}>
          <div style={{display:"flex",gap:8,justifyContent:"flex-end",flexWrap:"wrap",marginBottom:6}}>
            {[["ETH",C.eth,"100Mbps"],["CAN",C.can,"4Mbps FD"],["RS-485",C.rs4,"1Mbps"],["1553B",C.m53,"1Mbps det."]].map(([l,c,s])=>(
              <div key={l} style={{padding:"3px 10px",border:`1px solid ${c}55`,background:`${c}12`,borderRadius:3}}>
                <span style={{color:c,fontFamily:M,fontSize:9,fontWeight:"bold"}}>{l}</span>
                <span style={{color:`${c}80`,fontFamily:M,fontSize:8,marginLeft:6}}>{s}</span>
              </div>
            ))}
          </div>
          <div style={{color:C.m53,fontFamily:M,fontSize:10}}>+~$45 · +~10g · 31 RT capable</div>
          <div style={{color:`${C.i2c}50`,fontFamily:M,fontSize:8,marginTop:2}}>I²C hw on-PCB (local sensors) · not inter-board bus</div>
        </div>
      </div>
      <div style={{display:"flex",gap:2,marginTop:12,flexWrap:"wrap"}}>
        {TABS.map(t=>(<button key={t} onClick={()=>setTab(t)} style={{background:tab===t?"rgba(0,229,255,0.09)":"transparent",border:`1px solid ${tab===t?C.accent:"rgba(0,229,255,0.12)"}`,color:tab===t?C.accent:C.dimmer,padding:"4px 11px",fontFamily:M,fontSize:9,cursor:"pointer",letterSpacing:"0.06em",transition:"all 0.12s"}}>{t}</button>))}
      </div>
    </div>
    <div style={{position:"relative",zIndex:1,padding:"20px 24px",maxWidth:1060,margin:"0 auto"}}>
      {tab==="Overview"      && <OverviewTab/>}
      {tab==="MIL-STD-1553"  && <Mil1553Tab/>}
      {tab==="Comparison"    && <ComparisonTab/>}
      {tab==="Extensibility" && <ExtensibilityTab/>}
      {tab==="PCB Changes"   && <PCBTab/>}
      {tab==="BOM Delta"     && <BomTab/>}
    </div>
  </div>);
}
