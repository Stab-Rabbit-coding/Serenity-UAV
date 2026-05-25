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
  gold:"#fbbf24", steel:"#94a3b8", indigo:"#818cf8",
  dim:"rgba(255,255,255,0.90)", dimmer:"rgba(255,255,255,0.80)", text:"rgba(255,255,255,0.82)",
};
const M = "'OpenDyslexic Mono','OpenDyslexic','OpenDyslexicMono',monospace";
const mmi = mm => `${mm} mm (${(mm*0.03937).toFixed(2)}")`;

// ── primitives ────────────────────────────────────────────────
const SH=({t,c=C.accent,mt=22})=>(<div style={{display:"flex",alignItems:"center",gap:10,marginBottom:14,marginTop:mt}}><div style={{width:3,height:17,background:c}}/><span style={{color:c,fontFamily:M,fontSize:13,letterSpacing:"0.13em",textTransform:"uppercase",fontWeight:"normal"}}>{t}</span></div>);
const KV=({k,v,vc=C.text,u=""})=>(<div style={{display:"flex",justifyContent:"space-between",padding:"5px 0",borderBottom:"1px solid rgba(0,229,255,0.07)",alignItems:"baseline"}}><span style={{color:C.dim,fontFamily:M,fontSize:11}}>{k}</span><span style={{color:vc,fontFamily:M,fontSize:11}}>{v}{u&&<span style={{color:C.accent,marginLeft:4,fontSize:10}}>{u}</span>}</span></div>);
const Note=({c=C.dim,ch})=>(<div style={{marginTop:8,marginBottom:6,color:c,fontFamily:M,fontSize:10,lineHeight:1.85,padding:"8px 12px",borderLeft:`2px solid ${c}55`,background:`${c}07`,borderRadius:3}}>{ch}</div>);
const Warn=({ch})=>(<div style={{marginTop:8,color:C.yellow,fontFamily:M,fontSize:10,lineHeight:1.8,padding:"7px 12px",borderLeft:`2px solid ${C.yellow}`,background:"rgba(255,230,0,0.05)",borderRadius:3}}>⚠ {ch}</div>);
const Good=({ch})=>(<div style={{marginTop:8,color:C.green,fontFamily:M,fontSize:10,lineHeight:1.8,padding:"7px 12px",borderLeft:`2px solid ${C.green}`,background:"rgba(74,222,128,0.05)",borderRadius:3}}>✓ {ch}</div>);
const Tag=({label,c})=>(<span style={{color:c,border:`1px solid ${c}44`,padding:"1px 7px",borderRadius:2,fontFamily:M,fontSize:9,marginLeft:6,whiteSpace:"nowrap"}}>{label}</span>);
function TH({cols}){return(<thead><tr>{cols.map(h=>(<th key={h} style={{padding:"6px 9px",borderBottom:`1px solid ${C.border}`,color:C.accent,textAlign:"left",fontWeight:"normal",fontSize:10,letterSpacing:"0.06em",whiteSpace:"nowrap",opacity:.85}}>{h}</th>))}</tr></thead>);}
function Grid(){return(<svg style={{position:"fixed",inset:0,width:"100%",height:"100%",pointerEvents:"none",zIndex:0}}><defs><pattern id="sg" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0L0 0 0 20" fill="none" stroke="rgba(0,229,255,0.035)" strokeWidth={0.5}/></pattern><pattern id="lg" width="100" height="100" patternUnits="userSpaceOnUse"><rect width="100" height="100" fill="url(#sg)"/><path d="M100 0L0 0 0 100" fill="none" stroke="rgba(0,229,255,0.065)" strokeWidth={1}/></pattern></defs><rect width="100%" height="100%" fill="url(#lg)"/></svg>);}

// ═══════════════════════════════════════════════════════════════
//  PROTOCOL MATRIX  — all five protocols compared
// ═══════════════════════════════════════════════════════════════
const PROTOCOLS = [
  {
    id:"CAN FD", color:C.orange, status:"existing",
    phy:"ISO 11898-1 CAN FD · differential pair", topo:"Multi-master bus · up to 64 nodes",
    speed:"1 Mbps nom · 4 Mbps FD data", latency:"≤250 µs worst-case", conn:"JST-GH 4-pin × 2 (J2a+J2b)",
    ic:"MCP2518FD + MCP2562FD", newMass:"0g (connectors already budgeted → +0.8g second JST)",
    use:"Flight-critical: AHRS · RPM · arm/disarm · mode cmds",
    failMode:"Bus arbitration loss if >64 nodes or >4m stub",
    notes:"Daisy-chain: Pico TRIHAT-1 ↔ COMMS-HAT-1 ↔ future nodes. 120Ω terminator JP at each chain END only — jumper-selectable on Rev F boards.",
  },{
    id:"Ethernet 100BASE-T", color:C.purple, status:"existing",
    phy:"IEEE 802.3 100BASE-T · transformer-coupled differential pair", topo:"Point-to-point (current) · switch-expandable",
    speed:"100 Mbps full-duplex", latency:"<1 ms typical UDP", conn:"JST-GH 6-pin (J3↔J2)",
    ic:"W5500 + HX1188NL magnetics", newMass:"0g",
    use:"MAVLink UDP 14550 · log stream 14551 · config TCP 8080",
    failMode:"W5500 hardware crash · link-layer framing loss",
    notes:"Already provides the high-bandwidth path. No changes in Rev F connectivity update.",
  },{
    id:"RS-485 (NEW)", color:C.lime, status:"new",
    phy:"EIA-485 half-duplex · differential pair · bias/termination network", topo:"Multi-drop up to 32 nodes · 1200m max at 100kbps",
    speed:"5 Mbps @ 1m (hull is 365mm — no distance penalty)", latency:"<100 µs at 921600 baud",
    conn:"JST-GH 4-pin × 2 per board (RS485-A + RS485-B on chain)",
    ic:"SP485EN (SOIC-8) — one per board · $0.45 ea",
    newMass:"0.3g IC × 2 + 0.4g × 4 connectors = ~2g total",
    use:"MAVLink backup stream · ESC telemetry bus · sensor node expansion",
    failMode:"DE/RE line stuck (transceiver fault) · cable open = bus floating (safe fail — no data)",
    notes:"Completely distinct physical layer from CAN and Ethernet. UART-based so no new protocol stack. Pico GP8/GP9 (UART1 TX/RX) + GP7 (DE/RE). CM4 /dev/ttyAMA2 + GPIO24 DE/RE. Half-duplex — all nodes share A/B pair.",
  },{
    id:"USB CDC-ACM (NEW)", color:C.indigo, status:"new",
    phy:"USB 2.0 Full Speed (12 Mbps) · D+ / D− differential · 5V rail", topo:"Host (CM4) ↔ Device (Pico 2) — point-to-point only",
    speed:"12 Mbps FS · ~1 Mbps effective serial throughput", latency:"1 ms USB frame period + host scheduling",
    conn:"JST-GH 4-pin (VBUS · D+ · D− · GND) on TRIHAT-1 → GL850G hub port on CM4-CARRIER-1",
    ic:"NONE — Pico 2 RP2350 has built-in USB hardware · GL850G hub already fitted on carrier",
    newMass:"0.4g connector on TRIHAT-1 + 100mm (0.7g) 28AWG USB stub cable = ~1.1g",
    use:"OTA firmware flash · high-bandwidth debug · large parameter transfers · fallback serial when CAN+ETH both fail",
    failMode:"USB enumeration failure after CM4 reboot (~2s recovery) · power rail dependency on 5V BEC",
    notes:"Zero new ICs — leverages existing RP2350 USB hardware and GL850G USB hub. Pico appears as /dev/ttyACM0 on CM4. CDC-ACM virtual serial works without drivers on Linux. NOT suitable for latency-critical flight data; ideal for config/OTA/bulk transfer.",
  },
];

// ═══════════════════════════════════════════════════════════════
//  TAB 1 — PROTOCOL ANALYSIS
// ═══════════════════════════════════════════════════════════════
function ProtocolAnalysisTab(){
  const [sel,setSel]=useState("RS-485 (NEW)");
  const detail=PROTOCOLS.find(p=>p.id===sel);
  return(<div>
    <div style={{background:"rgba(163,230,53,0.05)",border:`1px solid ${C.lime}33`,borderRadius:4,padding:"10px 14px",marginBottom:20,fontFamily:M,fontSize:11,color:C.dim,lineHeight:1.8}}>
      <span style={{color:C.lime,fontWeight:"bold"}}>Rev F Connectivity Update · © 2026 Steve Griffing PE(CSE) CISSP-ISSEP CPP · CC BY 4.0</span>
      {" "}· Adds dual CAN JST connectors on both hats, RS-485 multi-drop bus, and USB CDC-ACM backup link. Total new hardware mass: <span style={{color:C.green}}>~3.1g</span> across both boards.
    </div>

    {/* Protocol selector tabs */}
    <div style={{display:"flex",gap:4,flexWrap:"wrap",marginBottom:16}}>
      {PROTOCOLS.map(p=>(<button key={p.id} onClick={()=>setSel(p.id)} style={{background:sel===p.id?`${p.color}18`:"transparent",border:`1px solid ${sel===p.id?p.color:"rgba(0,229,255,0.14)"}`,color:sel===p.id?p.color:C.dimmer,padding:"5px 12px",fontFamily:M,fontSize:10,cursor:"pointer",borderRadius:2,display:"flex",alignItems:"center",gap:6}}>
        {p.id}
        <span style={{fontSize:8,color:sel===p.id?p.color:C.dimmer,opacity:0.7}}>{p.status==="new"?"● NEW":"○ EXISTING"}</span>
      </button>))}
    </div>

    {detail&&(<div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <div style={{padding:"14px",border:`2px solid ${detail.color}`,borderRadius:6,background:`${detail.color}08`,marginBottom:16}}>
          <div style={{color:detail.color,fontFamily:M,fontSize:14,fontWeight:"bold",marginBottom:6}}>{detail.id}</div>
          <div style={{color:C.text,fontFamily:M,fontSize:10,lineHeight:1.8}}>{detail.notes}</div>
        </div>
        <KV k="Physical layer"   v={detail.phy}/>
        <KV k="Topology"         v={detail.topo}/>
        <KV k="Speed"            v={detail.speed} vc={detail.color}/>
        <KV k="Latency"          v={detail.latency}/>
        <KV k="Connector(s)"     v={detail.conn} vc={C.yellow}/>
        <KV k="Interface IC"     v={detail.ic}/>
        <KV k="New mass (Rev F)" v={detail.newMass} vc={detail.status==="new"?C.green:C.dimmer}/>
        <KV k="Primary use"      v={detail.use} vc={C.teal}/>
        <KV k="Failure mode"     v={detail.failMode} vc={C.red}/>
      </div>
      <div>
        <SH t="Why These Two New Protocols?" mt={0} c={C.lime}/>
        <Note c={C.lime} ch="RS-485 and USB CDC-ACM were selected because each is physically and electrically distinct from both CAN FD and Ethernet — meaning a single root-cause failure (PCB trace crack, connector loosening, IC failure) is extremely unlikely to simultaneously affect more than one bus. The four protocols together cover four completely different physical layers, connector types, and software stacks."/>
        <SH t="Protocol Independence Matrix" c={C.accent}/>
        <div style={{overflowX:"auto"}}>
          <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:9}}>
            <TH cols={["ATTRIBUTE","CAN FD","Ethernet","RS-485","USB CDC"]}/>
            <tbody>{[
              ["PHY type",       "Diff. pair","Transformer diff.","Diff. pair","D+/D− diff."],
              ["Framing",        "CAN frame","Ethernet frame","UART async","USB packet"],
              ["Arbitration",    "CSMA/CA","CSMA/CD","Token/DE pin","Host token"],
              ["Topology",       "Bus","Pt-to-pt","Bus","Pt-to-pt"],
              ["Stack depth",    "CAN→DroneCAN","TCP/IP→MAVLink","UART→MAVLink","USB→CDC→UART"],
              ["Failure mode",   "Bit-stuff err","CRC/FCS err","DE stuck","Enum timeout"],
              ["IC vendor",      "Microchip","WIZnet","TI/Renesas","None (RP2350)"],
              ["Power domain",   "5V bus","3.3V AVDD","3.3V DVDD","5V VBUS"],
            ].map(([attr,...cells],i)=>(
              <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
                <td style={{padding:"4px 8px",color:C.dim}}>{attr}</td>
                {cells.map((v,j)=>(<td key={j} style={{padding:"4px 8px",color:j===0?C.orange:j===1?C.purple:j===2?C.lime:C.indigo}}>{v}</td>))}
              </tr>
            ))}</tbody>
          </table>
        </div>
        <SH t="Weight / Complexity Scorecard" c={C.gold}/>
        <div style={{overflowX:"auto"}}>
          <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
            <TH cols={["PROTOCOL","NEW ICs","NEW CONN.","MASS DELTA","COMPLEXITY"]}/>
            <tbody>{[
              {p:"CAN FD daisy (2nd JST)",c:C.orange,ics:"0",conn:"2 (1 per board)",mass:"+0.8g",cx:"Very low"},
              {p:"RS-485",c:C.lime,ics:"2× SP485EN",conn:"4 (2 per board)",mass:"+2.0g",cx:"Low"},
              {p:"USB CDC-ACM",c:C.indigo,ics:"0",conn:"1 (TRIHAT-1)",mass:"+1.1g",cx:"Low (zero-driver on Linux)"},
            ].map((r,i)=>(<tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.02)":"transparent"}}>
              <td style={{padding:"5px 9px",color:r.c,fontWeight:"bold"}}>{r.p}</td>
              <td style={{padding:"5px 9px",color:r.ics==="0"?C.green:C.yellow}}>{r.ics}</td>
              <td style={{padding:"5px 9px",color:C.dim}}>{r.conn}</td>
              <td style={{padding:"5px 9px",color:C.green}}>{r.mass}</td>
              <td style={{padding:"5px 9px",color:C.teal,fontSize:9}}>{r.cx}</td>
            </tr>))}</tbody>
            <tfoot><tr style={{borderTop:`1px solid ${C.border}`}}>
              <td colSpan={3} style={{padding:"6px 9px",color:C.accent,textAlign:"right",fontSize:10}}>TOTAL NEW HARDWARE MASS</td>
              <td style={{padding:"6px 9px",color:C.green,fontWeight:"bold",fontSize:13}}>~3.9g</td>
              <td/>
            </tr></tfoot>
          </table>
        </div>
        <Note c={C.gold} ch="~3.9g total across both boards for four distinct, independent data paths. At an AUW of 1,002g empty that is 0.39% of total weight — extremely favourable for the redundancy gained."/>
      </div>
    </div>)}
  </div>);
}

// ═══════════════════════════════════════════════════════════════
//  TAB 2 — CAN DAISY CHAIN
// ═══════════════════════════════════════════════════════════════
function CANDaisyDiagram(){
  const VW=760, VH=360;
  // Three nodes: TRIHAT-1 (Pico), COMMS-HAT-1 (CM4), future expansion
  const nodes=[
    {label:"TRIHAT-1",sub:"Pico 2 · MCP2518FD",x:80,y:160,c:"#00e5ff",term:true},
    {label:"COMMS-HAT-1",sub:"CM4 · MCP2518FD",x:340,y:160,c:"#4ade80",term:false},
    {label:"NODE-3 (opt.)",sub:"Future expansion",x:600,y:160,c:"rgba(163,230,53,0.5)",term:true},
  ];
  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* Bus line CANH */}
      <line x1="80" y1="230" x2="660" y2="230" stroke="rgba(255,107,53,0.7)" strokeWidth={4} strokeLinecap="round"/>
      {/* Bus line CANL */}
      <line x1="80" y1="248" x2="660" y2="248" stroke="rgba(255,107,53,0.4)" strokeWidth={4} strokeLinecap="round"/>
      <text x="370" y="218" textAnchor="middle" fontFamily={M} fontSize={9} fill="rgba(255,107,53,0.7)" letterSpacing="2">CANH</text>
      <text x="370" y="265" textAnchor="middle" fontFamily={M} fontSize={9} fill="rgba(255,107,53,0.5)">CANL</text>

      {nodes.map((n,i)=>{
        const hasTerm = n.term;
        return(<g key={i}>
          {/* Node box */}
          <rect x={n.x-60} y={n.y-40} width={120} height={80} rx={6}
            fill={`${n.c}12`} stroke={n.c} strokeWidth={hasTerm?2.5:1.5}/>
          <text x={n.x} y={n.y-20} textAnchor="middle" fontFamily={M} fontSize={11}
            fontWeight="bold" fill={n.c}>{n.label}</text>
          <text x={n.x} y={n.y-4} textAnchor="middle" fontFamily={M} fontSize={8}
            fill={`${n.c}80`}>{n.sub}</text>
          {/* Dual JST connectors */}
          <rect x={n.x-42} y={n.y+10} width={36} height={18} rx={3}
            fill={`${n.c}20`} stroke={n.c} strokeWidth={1.2}/>
          <text x={n.x-24} y={n.y+23} textAnchor="middle" fontFamily={M} fontSize={8}
            fill={n.c}>J-A IN</text>
          <rect x={n.x+6} y={n.y+10} width={36} height={18} rx={3}
            fill={`${n.c}20`} stroke={n.c} strokeWidth={1.2}/>
          <text x={n.x+24} y={n.y+23} textAnchor="middle" fontFamily={M} fontSize={8}
            fill={n.c}>J-B OUT</text>
          {/* Stubs down to bus */}
          <line x1={n.x-24} y1={n.y+28} x2={n.x-24} y2="230" stroke={n.c} strokeWidth={2}/>
          <line x1={n.x+24} y1={n.y+28} x2={n.x+24} y2="230" stroke={n.c} strokeWidth={2} strokeDasharray={i<nodes.length-1?"none":"6 3"}/>
          {/* Termination resistor */}
          {hasTerm&&(<>
            <rect x={n.x-14} y="266" width={28} height={14} rx={3}
              fill="rgba(255,230,0,0.2)" stroke="#ffe600" strokeWidth={1.5}/>
            <text x={n.x} y="276" textAnchor="middle" fontFamily={M} fontSize={8}
              fontWeight="bold" fill="#ffe600">120Ω</text>
            <text x={n.x} y="294" textAnchor="middle" fontFamily={M} fontSize={8}
              fill="rgba(255,230,0,0.6)">TERM ●</text>
          </>)}
          {!hasTerm&&(
            <text x={n.x} y="292" textAnchor="middle" fontFamily={M} fontSize={8}
              fill="rgba(255,255,255,0.25)">NO TERM ○</text>
          )}
          {/* Termination jumper label */}
          {hasTerm&&(
            <rect x={n.x-22} y="300" width={44} height={14} rx={2}
              fill="rgba(255,230,0,0.08)" stroke="rgba(255,230,0,0.3)" strokeWidth={0.8}/>
          )}
          <text x={n.x} y="342" textAnchor="middle" fontFamily={M} fontSize={7}
            fill="rgba(255,255,255,0.3)">
            {hasTerm?"JP_TERM soldered":"JP_TERM open"}
          </text>
        </g>);
      })}

      {/* Chain cable labels */}
      <rect x="155" y="265" width="140" height="22" rx={3}
        fill="rgba(255,107,53,0.1)" stroke="rgba(255,107,53,0.4)" strokeWidth={0.8}/>
      <text x="225" y="280" textAnchor="middle" fontFamily={M} fontSize={9}
        fill="rgba(255,107,53,0.8)">JST-GH 4-pin · 120mm</text>
      <rect x="415" y="265" width="140" height="22" rx={3}
        fill="rgba(163,230,53,0.1)" stroke="rgba(163,230,53,0.4)" strokeWidth={0.8}/>
      <text x="485" y="280" textAnchor="middle" fontFamily={M} fontSize={9}
        fill="rgba(163,230,53,0.7)">JST-GH 4-pin · opt. ext.</text>

      {/* Pin legend */}
      <rect x="30" y="30" width="300" height="52" rx={4}
        fill="rgba(255,255,255,0.02)" stroke="rgba(255,255,255,0.08)"/>
      {[["P1","GND"],["P2","+5V bus"],["P3","CANH"],["P4","CANL"]].map(([p,s],i)=>(
        <g key={i}>
          <text x={50+i*72} y="50" fontFamily={M} fontSize={9} fill="#ffe600">{p}</text>
          <text x={50+i*72} y="66" fontFamily={M} fontSize={9} fill="rgba(255,230,0,0.6)">{s}</text>
        </g>
      ))}
      <text x="180" y="40" textAnchor="middle" fontFamily={M} fontSize={8}
        fill="rgba(255,255,255,0.25)" letterSpacing="1">JST-GH 4-PIN PINOUT (all CAN connectors)</text>

      {/* Title */}
      <text x={VW/2} y="16" textAnchor="middle" fontFamily={M} fontSize={9}
        fill="rgba(0,229,255,0.25)" letterSpacing="2">CAN FD DAISY-CHAIN TOPOLOGY — DUAL JST-GH PER BOARD</text>
    </svg>
  );
}

function CANDaisyTab(){
  return(<div>
    <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:8,marginBottom:20}}>
      <CANDaisyDiagram/>
    </div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="Second CAN JST Connector — Both Boards" mt={0} c={C.orange}/>
        <KV k="Connector added" v="1× additional JST-GH 1.25mm 4-pin per board"/>
        <KV k="TRIHAT-1 change" v="J2a (existing) = chain IN · J2b (new) = chain OUT"/>
        <KV k="COMMS-HAT-1 change" v="J1a (existing) = chain IN · J1b (new) = chain OUT"/>
        <KV k="Wiring" v="Both connectors wired in parallel to same CANH/CANL node"/>
        <KV k="Termination" v="Jumper JP_TERM per board · soldered at chain ENDS only" vc={C.yellow}/>
        <KV k="Termination rule" v="Exactly 2 terminators in any chain: first node + last node" vc={C.red}/>
        <KV k="Max nodes" v="32 nodes per ISO 11898-1 segment"/>
        <KV k="Max stub length" v={`Each node stub ≤30mm (${(30*0.03937).toFixed(2)}") — within hull ✔`} vc={C.green}/>
        <KV k="PCB change" v="+1 JST-GH footprint per board · same CANH/CANL traces route to both" vc={C.green}/>
        <KV k="Mass delta" v="+0.4g per board · +0.8g total" vc={C.green}/>
        <Warn ch="NEVER solder both JP_TERM jumpers AND have a middle node. If TRIHAT-1 and COMMS-HAT-1 are the only two nodes, both JP_TERM bridges are soldered. If a third node is added mid-chain, remove the COMMS-HAT-1 bridge and solder the new end node's bridge instead."/>
      </div>
      <div>
        <SH t="Daisy Chain vs. Star Topology" mt={0} c={C.teal}/>
        <Note c={C.teal} ch="The existing single-connector design is functionally a two-node stub connection — fine for just TRIHAT-1 and COMMS-HAT-1. Adding second connectors enables proper daisy-chaining where future peripherals (additional IMU, GPS, ESC telemetry aggregator, rangefinder) can be inserted into the chain without rewiring the primary Pico↔CM4 link."/>
        <SH t="Future Expansion Examples" c={C.accent}/>
        {[
          ["Node 3 (opt.)","Auxiliary IMU board · ICM-42688-P on breakout · vibration-isolated"],
          ["Node 4 (opt.)","Smart battery fuel gauge · MAX17048 or BQ40Z50 · SOC telemetry"],
          ["Node 5 (opt.)","ESC telemetry hub · aggregates RPM+temp from all 3 ESCs over CAN"],
          ["Node 6 (opt.)","Rangefinder · TFmini-S · CAN FD bridge · altitude assist in hover"],
        ].map(([n,d],i)=>(
          <div key={i} style={{display:"flex",gap:10,padding:"6px 0",borderBottom:"1px solid rgba(0,229,255,0.07)"}}>
            <span style={{color:C.lime,fontFamily:M,fontSize:10,minWidth:110,flexShrink:0}}>{n}</span>
            <span style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.6}}>{d}</span>
          </div>
        ))}
        <Good ch="Second JST connector costs 0.4g and enables unlimited future node expansion without any PCB revision to either primary board."/>
      </div>
    </div>
  </div>);
}

// ═══════════════════════════════════════════════════════════════
//  TAB 3 — RS-485 BUS
// ═══════════════════════════════════════════════════════════════
function RS485Diagram(){
  const VW=720, VH=340;
  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* A bus line */}
      <line x1="50" y1="140" x2="670" y2="140" stroke="rgba(163,230,53,0.7)" strokeWidth={3.5} strokeLinecap="round"/>
      {/* B bus line */}
      <line x1="50" y1="158" x2="670" y2="158" stroke="rgba(163,230,53,0.4)" strokeWidth={3.5} strokeLinecap="round"/>
      <text x="360" y="130" textAnchor="middle" fontFamily={M} fontSize={9} fill="rgba(163,230,53,0.7)" letterSpacing="1">A (non-inv.)</text>
      <text x="360" y="175" textAnchor="middle" fontFamily={M} fontSize={9} fill="rgba(163,230,53,0.5)">B (inv.)</text>

      {/* TRIHAT-1 node */}
      {[{label:"TRIHAT-1",sub:"SP485EN · GP8/9 UART1",sub2:"GP7 DE/RE",x:130,y:60},{label:"COMMS-HAT-1",sub:"SP485EN · ttyAMA2",sub2:"GPIO24 DE/RE",x:380,y:60},{label:"NODE-3+",sub:"Future sensor node",sub2:"opt. population",x:590,y:60}].map((n,i)=>(
        <g key={i}>
          <rect x={n.x-70} y={n.y} width={140} height={60} rx={5}
            fill={i<2?"rgba(163,230,53,0.1)":"rgba(163,230,53,0.04)"}
            stroke={i<2?C.lime:"rgba(163,230,53,0.3)"} strokeWidth={i<2?1.8:1}/>
          <text x={n.x} y={n.y+20} textAnchor="middle" fontFamily={M} fontSize={10}
            fontWeight="bold" fill={i<2?C.lime:"rgba(163,230,53,0.5)"}>{n.label}</text>
          <text x={n.x} y={n.y+35} textAnchor="middle" fontFamily={M} fontSize={8}
            fill={`rgba(163,230,53,${i<2?0.6:0.35})`}>{n.sub}</text>
          <text x={n.x} y={n.y+48} textAnchor="middle" fontFamily={M} fontSize={8}
            fill={`rgba(163,230,53,${i<2?0.5:0.25})`}>{n.sub2}</text>
          {/* Dual JST */}
          <rect x={n.x-48} y={n.y+62} width={40} height={16} rx={3}
            fill="rgba(163,230,53,0.1)" stroke={C.lime} strokeWidth={1}/>
          <text x={n.x-28} y={n.y+74} textAnchor="middle" fontFamily={M} fontSize={7}
            fill={C.lime}>RS485-IN</text>
          {i<2&&(<>
            <rect x={n.x+8} y={n.y+62} width={40} height={16} rx={3}
              fill="rgba(163,230,53,0.1)" stroke={C.lime} strokeWidth={1}/>
            <text x={n.x+28} y={n.y+74} textAnchor="middle" fontFamily={M} fontSize={7}
              fill={C.lime}>RS485-OUT</text>
          </>)}
          {/* Stubs */}
          <line x1={n.x-28} y1={n.y+78} x2={n.x-28} y2="140" stroke={C.lime} strokeWidth={1.5}/>
          {i<2&&<line x1={n.x+28} y1={n.y+78} x2={n.x+28} y2="140" stroke={C.lime} strokeWidth={1.5} strokeDasharray="5 3"/>}
          {/* DE/RE control */}
          <path d={`M${n.x},${n.y+62} L${n.x},${n.y+54}`} stroke="rgba(163,230,53,0.4)" strokeWidth={1} strokeDasharray="2 2"/>
          {i<2&&<text x={n.x+52} y={n.y+42} fontFamily={M} fontSize={7} fill="rgba(163,230,53,0.35)">MCU GPIO</text>}
          {i<2&&<text x={n.x+52} y={n.y+52} fontFamily={M} fontSize={7} fill="rgba(163,230,53,0.35)">→ DE/RE</text>}
        </g>
      ))}

      {/* Bias network */}
      <rect x="30" y="200" width="100" height="38" rx={3}
        fill="rgba(163,230,53,0.08)" stroke="rgba(163,230,53,0.3)" strokeWidth={0.8}/>
      <text x="80" y="215" textAnchor="middle" fontFamily={M} fontSize={8}
        fill="rgba(163,230,53,0.6)">BIAS RESISTORS</text>
      <text x="80" y="228" textAnchor="middle" fontFamily={M} fontSize={7}
        fill="rgba(163,230,53,0.4)">560Ω to +3V3/GND</text>
      <text x="80" y="240" textAnchor="middle" fontFamily={M} fontSize={7}
        fill="rgba(163,230,53,0.35)">on TRIHAT-1</text>
      <line x1="80" y1="200" x2="80" y2="158" stroke="rgba(163,230,53,0.3)" strokeWidth={0.8} strokeDasharray="3 2"/>

      {/* Cable label */}
      <rect x="195" y="198" width="150" height="20" rx={3}
        fill="rgba(163,230,53,0.06)" stroke="rgba(163,230,53,0.2)" strokeWidth={0.8}/>
      <text x="270" y="212" textAnchor="middle" fontFamily={M} fontSize={8}
        fill="rgba(163,230,53,0.6)">JST-GH 4-pin · 120mm</text>

      {/* UART mode label */}
      <rect x="460" y="198" width="230" height="50" rx={3}
        fill="rgba(0,0,0,0.3)" stroke="rgba(163,230,53,0.2)" strokeWidth={0.8}/>
      <text x="575" y="214" textAnchor="middle" fontFamily={M} fontSize={8}
        fill="rgba(163,230,53,0.5)" fontWeight="bold">HALF-DUPLEX UART</text>
      <text x="575" y="228" textAnchor="middle" fontFamily={M} fontSize={8}
        fill="rgba(163,230,53,0.4)">5 Mbps · MAVLink framing</text>
      <text x="575" y="242" textAnchor="middle" fontFamily={M} fontSize={8}
        fill="rgba(163,230,53,0.35)">DE=HIGH=transmit · DE=LOW=receive</text>

      {/* Pin legend */}
      {[["P1","GND"],["P2","+3V3"],["P3","A (non-inv)"],["P4","B (inv)"]].map(([p,s],i)=>(
        <g key={i}>
          <text x={30+i*165} y="300" fontFamily={M} fontSize={9} fill={C.lime}>{p}</text>
          <text x={30+i*165} y="315" fontFamily={M} fontSize={9} fill="rgba(163,230,53,0.6)">{s}</text>
        </g>
      ))}
      <text x={VW/2} y="16" textAnchor="middle" fontFamily={M} fontSize={9}
        fill="rgba(0,229,255,0.25)" letterSpacing="2">RS-485 HALF-DUPLEX MULTI-DROP BUS — ALL NODES SHARE A/B PAIR</text>
      <text x={VW/2} y="340" textAnchor="middle" fontFamily={M} fontSize={8}
        fill="rgba(255,255,255,0.2)">Pin 3+4 must be twisted pair · bias resistors at one end only · up to 32 nodes · 1200m max cable run</text>
    </svg>
  );
}

function RS485Tab(){
  return(<div>
    <div style={{border:`1px solid ${C.lime}33`,borderRadius:4,background:"rgba(163,230,53,0.01)",padding:8,marginBottom:20}}>
      <RS485Diagram/>
    </div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="RS-485 Specification" mt={0} c={C.lime}/>
        <KV k="Standard" v="EIA-485 (TIA-485-A) · half-duplex"/>
        <KV k="Transceiver IC" v="SP485EN (Renesas/IXYS) · SOIC-8 · $0.45"/>
        <KV k="Supply" v="3.3V · 0.3mA quiescent"/>
        <KV k="Bus voltage" v="±12V tolerance · 3.3V logic IO → transceiver"/>
        <KV k="Common mode range" v="−7V to +12V → excellent noise immunity"/>
        <KV k="Differential threshold" v="±200mV — very robust to EMI from EDFs"/>
        <KV k="Baud rate" v="921600 baud (default) · up to 5 Mbps over 365mm" vc={C.lime}/>
        <KV k="Cable type" v="Twisted pair A/B + GND · JST-GH 4-pin"/>
        <KV k="Cable route" v="TRIHAT-1 RS485-OUT → COMMS-HAT-1 RS485-IN · along keel"/>
        <KV k="Bias network" v="2× 560Ω on TRIHAT-1 (A to +3V3, B to GND) · pulls bus to known state when idle"/>
        <KV k="Direction control" v="Pico GP7 (DE/RE) · CM4 GPIO24 (DE/RE) · both active-high"/>
        <KV k="Protocol carried" v="MAVLink 2.0 binary framing · identical to SiK link"/>
        <KV k="TRIHAT-1 UART" v="UART1 · GP8 TX · GP9 RX · GP7 DE/RE"/>
        <KV k="CM4 UART" v="/dev/ttyAMA2 · GPIO15 TX · GPIO14 RX · GPIO24 DE"/>
        <KV k="New mass (total)" v="+2× SP485EN (0.3g) + 4× JST-GH (1.6g) + passives (0.1g) = ~2.0g" vc={C.green}/>
      </div>
      <div>
        <SH t="Failure Mode Analysis" mt={0} c={C.red}/>
        <Note c={C.red} ch="RS-485 failure modes are categorically different from CAN FD and Ethernet: (1) DE pin stuck HIGH causes bus monopoly — other nodes cannot transmit, but Ethernet and CAN remain fully functional. (2) Open-circuit A or B wire causes receive loss only — the transmitting side never knows. (3) Short A-to-B causes differential collapse to zero — both ends detect framing errors, bus silent. None of these modes affect CAN FD or Ethernet, which is the point."/>
        <SH t="Software Integration" c={C.teal}/>
        <KV k="Pico firmware" v="UART1 IRQ handler · DMA RX ring buffer · MAVLink parser"/>
        <KV k="CM4 software" v="mavlink-router bridge on /dev/ttyAMA2 · 921600 baud"/>
        <KV k="Protocol mode" v="MAVLink 2.0 — identical framing to SiK 915MHz radio"/>
        <KV k="Activation" v="RS-485 link always active — parallel to CAN and Ethernet"/>
        <KV k="Automatic failover" v="mavlink-router routes any valid MAVLink from any interface"/>
        <KV k="Use case (expansion)" v="Future sensor nodes speak RS-485 MAVLink → CM4 aggregates all"/>
        <Good ch="RS-485 uses the same MAVLink 2.0 message format already parsed by all flight software. Zero new protocol stacks required — just configure UART and DE pin."/>
        <Note c={C.lime} ch="EDF motors (70mm at 35A) generate significant 50kHz–200kHz conducted and radiated noise. RS-485's ±200mV differential threshold and ±12V common-mode tolerance make it inherently EDF-noise-immune — more so than single-ended UART or I2C."/>
      </div>
    </div>
  </div>);
}

// ═══════════════════════════════════════════════════════════════
//  TAB 4 — USB CDC-ACM
// ═══════════════════════════════════════════════════════════════
function USBDiagram(){
  const VW=680, VH=300;
  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* Pico 2 block */}
      <rect x={20} y={60} width={130} height={160} rx={5}
        fill="rgba(129,140,248,0.08)" stroke={C.indigo} strokeWidth={1.8}/>
      <text x={85} y={85} textAnchor="middle" fontFamily={M} fontSize={11}
        fontWeight="bold" fill={C.indigo}>PICO 2</text>
      <text x={85} y={100} textAnchor="middle" fontFamily={M} fontSize={8}
        fill="rgba(129,140,248,0.5)">RP2350</text>
      <line x1={30} y1={110} x2={140} y2={110} stroke="rgba(129,140,248,0.2)" strokeWidth={0.7}/>
      {["USB Device HW","CDC-ACM class","Virtual UART","GP26 (D+/D−)","500mA VBUS","Enum: ~0.5s"].map((s,i)=>(
        <text key={i} x={85} y={125+i*15} textAnchor="middle" fontFamily={M} fontSize={8}
          fill="rgba(129,140,248,0.5)">{s}</text>
      ))}
      {/* JST-GH on TRIHAT-1 */}
      <rect x={150} y={115} width={60} height={30} rx={3}
        fill="rgba(129,140,248,0.12)" stroke={C.indigo} strokeWidth={1.5}/>
      <text x={180} y={129} textAnchor="middle" fontFamily={M} fontSize={8}
        fontWeight="bold" fill={C.indigo}>TRIHAT-1</text>
      <text x={180} y={141} textAnchor="middle" fontFamily={M} fontSize={7}
        fill="rgba(129,140,248,0.6)">J_USB JST-GH 4P</text>
      <line x1={150} y1={130} x2={150} y2={130} stroke={C.indigo} strokeWidth={2}/>
      <line x1={150} y1={130} x2={80} y2={130} stroke={C.indigo} strokeWidth={2}/>

      {/* USB cable */}
      <path d={`M210,130 Q300,80 380,110`}
        fill="none" stroke={C.indigo} strokeWidth={4} strokeLinecap="round"/>
      <rect x={240} y={72} width={100} height={28} rx={3}
        fill={`${C.indigo}18`} stroke={C.indigo} strokeWidth={1}/>
      <text x={290} y={85} textAnchor="middle" fontFamily={M} fontSize={9}
        fontWeight="bold" fill={C.indigo}>USB 2.0 FS</text>
      <text x={290} y={97} textAnchor="middle" fontFamily={M} fontSize={7}
        fill="rgba(129,140,248,0.7)">4-pin JST-GH · 100mm</text>

      {/* GL850G hub on CM4-CARRIER-1 */}
      <rect x={380} y={70} width={110} height={70} rx={4}
        fill="rgba(129,140,248,0.08)" stroke={C.indigo} strokeWidth={1.5}/>
      <text x={435} y={92} textAnchor="middle" fontFamily={M} fontSize={9}
        fontWeight="bold" fill={C.indigo}>GL850G HUB</text>
      <text x={435} y={106} textAnchor="middle" fontFamily={M} fontSize={8}
        fill="rgba(129,140,248,0.5)">CM4-CARRIER-1</text>
      <text x={435} y={119} textAnchor="middle" fontFamily={M} fontSize={7}
        fill="rgba(129,140,248,0.4)">4-port USB2 · already fitted</text>
      <text x={435} y={132} textAnchor="middle" fontFamily={M} fontSize={7}
        fill={C.green}>spare port ← Pico</text>

      {/* CM4 block */}
      <rect x={520} y={50} width={130} height={180} rx={5}
        fill="rgba(74,222,128,0.07)" stroke={C.green} strokeWidth={1.5}/>
      <text x={585} y={73} textAnchor="middle" fontFamily={M} fontSize={11}
        fontWeight="bold" fill={C.green}>CM4</text>
      <line x1={530} y1={82} x2={640} y2={82} stroke="rgba(74,222,128,0.2)" strokeWidth={0.7}/>
      {["USB Host (hub)","GL850G: /dev/bus/usb","Pico → /dev/ttyACM0","CDC-ACM zero-driver","12 Mbps FS","~1 Mbps serial"].map((s,i)=>(
        <text key={i} x={585} y={96+i*15} textAnchor="middle" fontFamily={M} fontSize={8}
          fill="rgba(74,222,128,0.5)">{s}</text>
      ))}
      {/* Hub to CM4 */}
      <line x1={490} y1={105} x2={520} y2={105} stroke={C.green} strokeWidth={2.5}/>

      {/* Highlight: zero new ICs */}
      <rect x={20} y={240} width={640} height={42} rx={4}
        fill="rgba(74,222,128,0.06)" stroke="rgba(74,222,128,0.3)" strokeWidth={1}/>
      <text x={340} y={258} textAnchor="middle" fontFamily={M} fontSize={10}
        fontWeight="bold" fill={C.green}>ZERO NEW ICs REQUIRED</text>
      <text x={340} y={274} textAnchor="middle" fontFamily={M} fontSize={9}
        fill="rgba(74,222,128,0.6)">RP2350 has built-in USB hardware · GL850G USB hub already fitted on CM4-CARRIER-1 · only new part is one JST-GH 4-pin connector on TRIHAT-1</text>

      {/* Pin legend */}
      {[["P1","GND"],["P2","VBUS 5V"],["P3","D−"],["P4","D+"]].map(([p,s],i)=>(
        <g key={i}>
          <text x={220+i*120} y={180} fontFamily={M} fontSize={9} fill={C.indigo}>{p}</text>
          <text x={220+i*120} y={195} fontFamily={M} fontSize={9} fill="rgba(129,140,248,0.6)">{s}</text>
        </g>
      ))}
      <text x={VW/2} y={14} textAnchor="middle" fontFamily={M} fontSize={9}
        fill="rgba(0,229,255,0.25)" letterSpacing="2">USB 2.0 CDC-ACM — PICO 2 DEVICE → GL850G HUB → CM4 HOST</text>
    </svg>
  );
}

function USBTab(){
  return(<div>
    <div style={{border:`1px solid ${C.indigo}33`,borderRadius:4,background:"rgba(129,140,248,0.01)",padding:8,marginBottom:20}}>
      <USBDiagram/>
    </div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="USB CDC-ACM Specification" mt={0} c={C.indigo}/>
        <KV k="USB spec" v="USB 2.0 Full Speed · 12 Mbps"/>
        <KV k="Class" v="CDC (Communications Device Class) · ACM subclass"/>
        <KV k="Pico 2 hardware" v="RP2350 built-in USB controller · no external IC"/>
        <KV k="CM4 host path" v="CM4 USB OTG → GL850G hub port (already fitted on carrier)"/>
        <KV k="New hardware" v="1× JST-GH 4-pin header on TRIHAT-1 · 100mm stub cable" vc={C.green}/>
        <KV k="New ICs" v="NONE" vc={C.green}/>
        <KV k="Pico device path" v="RP2350 USB DP/DM → TRIHAT-1 J_USB → CM4 hub port"/>
        <KV k="CM4 device node" v="/dev/ttyACM0 (auto-appears on enumeration)"/>
        <KV k="Driver required" v="None — CDC-ACM built into Linux kernel (cdc_acm.ko)"/>
        <KV k="Throughput" v="~1 Mbps effective serial (USB FS framing overhead)"/>
        <KV k="Latency" v="~1ms (USB frame period) + OS scheduling"/>
        <KV k="Enumeration time" v="~0.5s from Pico power-on · ~2s after CM4 reboot"/>
        <KV k="VBUS power" v="CM4 hub provides 5V/500mA to Pico via USB (backup power path)"/>
        <KV k="Interrupt mode" v="CDC-ACM supports USB interrupt transfer for low-latency control"/>
        <KV k="New mass" v="+0.4g JST-GH connector + 0.7g 100mm cable = ~1.1g" vc={C.green}/>
      </div>
      <div>
        <SH t="Ideal Use Cases" mt={0} c={C.accent}/>
        {[
          ["OTA firmware updates","CM4 uses dfu-util or picotool over USB to reflash Pico 2 in-field — no physical access to Pico USB port required. Critical for field maintenance."],
          ["Large parameter transfers","Uploading 200+ parameter sets to Pico (mission profiles, PID gains) is slow over CAN FD at 1 Mbps. USB does the same in milliseconds."],
          ["Last-resort MAVLink","If CAN FD jams AND Ethernet fails, USB CDC-ACM provides a third independent MAVLink channel. 12 Mbps FS ≫ enough for heartbeat + attitude."],
          ["High-bandwidth log replay","Pico can stream raw sensor buffers (gyro at 8kHz = ~192kbps) to CM4 for black-box analysis — too fast for CAN FD, ideal for USB."],
          ["Development/debug","USB serial from Pico to CM4 allows real-time printf() debugging without needing a laptop connected — logs appear on CM4 /dev/ttyACM0."],
        ].map(([use,desc],i)=>(
          <div key={i} style={{marginBottom:10,padding:"8px 10px",border:`1px solid rgba(129,140,248,0.2)`,borderLeft:`3px solid ${C.indigo}`,borderRadius:3,background:"rgba(129,140,248,0.03)"}}>
            <div style={{color:C.indigo,fontFamily:M,fontSize:10,fontWeight:"bold",marginBottom:3}}>{use}</div>
            <div style={{color:C.dim,fontFamily:M,fontSize:9.5,lineHeight:1.7}}>{desc}</div>
          </div>
        ))}
        <Warn ch="USB CDC-ACM is NOT suitable for latency-critical flight control data (AHRS, ESC commands) due to 1ms frame latency and enumeration dependency. Use CAN FD for those. USB is the bulk-transfer and fallback path."/>
      </div>
    </div>
  </div>);
}

// ═══════════════════════════════════════════════════════════════
//  TAB 5 — UPDATED HAT SPECS
// ═══════════════════════════════════════════════════════════════
function HatSpecsTab(){
  return(<div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      {/* TRIHAT-1 */}
      <div>
        <SH t="TRIHAT-1 Rev F — Pico 2 Sensor Hat" mt={0} c={C.accent}/>
        <div style={{background:"rgba(0,229,255,0.04)",border:`1px solid ${C.border}`,borderRadius:4,padding:"12px",marginBottom:12}}>
          <KV k="Board size" v={mmi(65)+" × "+mmi(48)+" · 4-layer ENIG"}/>
          <KV k="Layer 1 F.Cu" v="Signal · Pico GPIO + sensor traces"/>
          <KV k="Layer 2 In1.Cu" v="+3.3V power plane"/>
          <KV k="Layer 3 In2.Cu" v="GND plane"/>
          <KV k="Layer 4 B.Cu" v="Signal · inter-board cables + USB stub"/>
        </div>
        <div style={{fontFamily:M,fontSize:10,color:C.teal,marginBottom:6,fontWeight:"bold"}}>CONNECTORS — Rev F</div>
        {[
          ["J1","JST-GH 6-pin","SiK/Telemetry UART"],
          ["J2a","JST-GH 4-pin","CAN FD chain IN ← (existing)"],
          ["J2b","JST-GH 4-pin","CAN FD chain OUT → (NEW Rev F)"],
          ["J3","JST-GH 6-pin","Ethernet 100BASE-T ↔ COMMS-HAT-1"],
          ["J4","JST-GH 6-pin","FPV camera UART/I²C"],
          ["J5","JST-GH 6-pin","External GPS (backup)"],
          ["J6","JST-GH 4-pin","I²C external sensors"],
          ["J7","JST-GH 4-pin","Debug UART / SWD"],
          ["J8","JST-GH 4-pin","Power input 5V/GND"],
          ["J_RS485a","JST-GH 4-pin","RS-485 chain IN ← (NEW Rev F)"],
          ["J_RS485b","JST-GH 4-pin","RS-485 chain OUT → (NEW Rev F)"],
          ["J_USB","JST-GH 4-pin","USB 2.0 FS → CM4 GL850G hub (NEW Rev F)"],
          ["ANT1","U.FL","GPS patch antenna coax"],
        ].map(([ref,conn,desc],i)=>{
          const isNew = desc.includes("NEW Rev F");
          return(<div key={i} style={{display:"flex",gap:8,padding:"4px 0",borderBottom:"1px solid rgba(0,229,255,0.06)",background:isNew?"rgba(163,230,53,0.04)":"transparent"}}>
            <span style={{color:isNew?C.lime:C.yellow,fontFamily:M,fontSize:10,minWidth:72,flexShrink:0,fontWeight:isNew?"bold":"normal"}}>{ref}</span>
            <span style={{color:C.dim,fontFamily:M,fontSize:9,minWidth:110,flexShrink:0}}>{conn}</span>
            <span style={{color:isNew?C.lime:C.dimmer,fontFamily:M,fontSize:9}}>{desc}</span>
          </div>);
        })}
        <div style={{marginTop:10,padding:"8px 10px",background:"rgba(163,230,53,0.05)",border:`1px solid ${C.lime}33`,borderRadius:4,fontFamily:M,fontSize:9,color:C.dim}}>
          <span style={{color:C.lime}}>Rev F additions to TRIHAT-1:</span> J2b (CAN out) · J_RS485a/b (RS-485 chain) · J_USB (USB stub to hub) · SP485EN SOIC-8 IC · 560Ω bias resistors R_B1/R_B2. PCB grows by ~0 mm — components placed in previously unused area near board edge.
        </div>
      </div>

      {/* COMMS-HAT-1 */}
      <div>
        <SH t="COMMS-HAT-1 Rev E+ — CM4 Companion Hat" mt={0} c={C.green}/>
        <div style={{background:"rgba(74,222,128,0.04)",border:`1px solid ${C.lime}33`,borderRadius:4,padding:"12px",marginBottom:12}}>
          <KV k="Board size" v={mmi(65)+" × "+mmi(48)+" · 4-layer ENIG"}/>
          <KV k="RS-485 IC" v="SP485EN SOIC-8 · same transceiver as TRIHAT-1"/>
          <KV k="USB" v="No USB connector on COMMS-HAT — USB is TRIHAT-1→carrier only"/>
        </div>
        <div style={{fontFamily:M,fontSize:10,color:C.teal,marginBottom:6,fontWeight:"bold"}}>CONNECTORS — Rev E+</div>
        {[
          ["J1a","JST-GH 4-pin","CAN FD chain IN ← (existing)"],
          ["J1b","JST-GH 4-pin","CAN FD chain OUT → (NEW Rev E+)"],
          ["J2","JST-GH 6-pin","Ethernet 100BASE-T ↔ TRIHAT-1"],
          ["J3","JST-GH 6-pin","SiK 915MHz telemetry"],
          ["J4","JST-GH 4-pin","Power / audit UART (JP4)"],
          ["J_RS485a","JST-GH 4-pin","RS-485 chain IN ← (NEW Rev E+)"],
          ["J_RS485b","JST-GH 4-pin","RS-485 chain OUT → (NEW Rev E+)"],
          ["SMA-ZB","SMA edge","Zigbee/BLE 2.4GHz (opt.)"],
          ["SMA-LR","SMA edge","LoRa 915MHz (opt.)"],
          ["SMA-SiK","SMA edge","SiK 915MHz whip"],
          ["JP3","2-pin 2.54mm","NX latch override (recessed)"],
          ["JP4","JST-GH 4-pin","STM32 audit log UART debug"],
        ].map(([ref,conn,desc],i)=>{
          const isNew = desc.includes("NEW Rev E+");
          return(<div key={i} style={{display:"flex",gap:8,padding:"4px 0",borderBottom:"1px solid rgba(74,222,128,0.06)",background:isNew?"rgba(163,230,53,0.04)":"transparent"}}>
            <span style={{color:isNew?C.lime:C.yellow,fontFamily:M,fontSize:10,minWidth:72,flexShrink:0,fontWeight:isNew?"bold":"normal"}}>{ref}</span>
            <span style={{color:C.dim,fontFamily:M,fontSize:9,minWidth:110,flexShrink:0}}>{conn}</span>
            <span style={{color:isNew?C.lime:C.dimmer,fontFamily:M,fontSize:9}}>{desc}</span>
          </div>);
        })}
        <div style={{marginTop:10,padding:"8px 10px",background:"rgba(163,230,53,0.05)",border:`1px solid ${C.lime}33`,borderRadius:4,fontFamily:M,fontSize:9,color:C.dim}}>
          <span style={{color:C.lime}}>Rev E+ additions to COMMS-HAT-1:</span> J1b (CAN out) · J_RS485a/b (RS-485 chain) · SP485EN SOIC-8 · 120Ω termination jumper JP_TERM (replaces existing solder bridge with proper 2-pin jumper header). No size change.
        </div>
      </div>
    </div>

    <SH t="PCB Layout Notes for New Connectors"/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <KV k="CAN second JST (J2b / J1b)" v="Place adjacent to existing CAN JST — same CANH/CANL traces simply extend to new footprint. Route on F.Cu, parallel to existing CAN traces, ≤10mm extension."/>
        <KV k="RS-485 JSTs (J_RS485a/b)" v="Place near board edge on opposite side from CAN connectors. SP485EN SOIC-8 placed between the two RS-485 headers — minimises trace length to transceiver A/B pins."/>
        <KV k="SP485EN placement" v="Centre SP485EN between J_RS485a and J_RS485b. Place 100nF bypass cap on VCC pin ≤2mm. Keep A/B differential traces equal length, ≤20mm from transceiver to connectors."/>
      </div>
      <div>
        <KV k="USB JST (J_USB on TRIHAT-1)" v="Place near bottom-right corner of TRIHAT-1 board edge. Route D+/D− as matched-length 90Ω differential pair on F.Cu. No vias on D+/D− — keep on single layer. VBUS trace 0.5mm width (500mA)."/>
        <KV k="Bias resistors (TRIHAT-1 only)" v="R_B1 (560Ω, A to +3V3) and R_B2 (560Ω, B to GND) placed near J_RS485a (the 'first' end of the chain from TRIHAT perspective)."/>
        <KV k="Termination jumper" v="Replace previous solder bridge with proper 2-pin 2.54mm header + shorting jumper on each board. Clearly labelled: 'JP_TERM — SHORT IF CHAIN END'."/>
        <Note c={C.teal} ch="Total new component count across both boards: 2× SP485EN, 2× 560Ω bias resistors, 6× JST-GH 4-pin connectors, 2× termination jumper headers, 1× JST-GH 4-pin USB header, ~8× 100nF bypass caps. All passive SMD components fit in 0402 package — negligible board area."/>
      </div>
    </div>
  </div>);
}

// ═══════════════════════════════════════════════════════════════
//  TAB 6 — FULL WIRING MATRIX
// ═══════════════════════════════════════════════════════════════
function WiringMatrixTab(){
  const buses=[
    {id:"CAN FD (primary)",c:C.orange,speed:"4 Mbps",phy:"Differential 120Ω term.",conn:"JST-GH 4-pin × 2 (chain)",route:"Stbd keel · TRIHAT-1 J2a→J2b → COMMS-HAT-1 J1a→J1b",carries:"AHRS · RPM · arm/mode · sensor health · nozzle state",pico:"SPI0 → MCP2518FD · GP14 CS · GP7 INT",cm4:"SPI0 → MCP2518FD · GPIO7 CS · GPIO8 INT · /dev/spidev0.0"},
    {id:"Ethernet 100BASE-T",c:C.purple,speed:"100 Mbps",phy:"Transformer-coupled diff.",conn:"JST-GH 6-pin × 1",route:"Port keel · TRIHAT-1 J3 → COMMS-HAT-1 J2 · 150mm",carries:"MAVLink UDP 14550 · log stream 14551 · config TCP 8080",pico:"SPI1 → W5500 · GP8-13 · 192.168.10.1",cm4:"SPI1 → W5500 · GPIO17-21 · 192.168.10.2"},
    {id:"RS-485 (NEW)",c:C.lime,speed:"5 Mbps (921600 baud)",phy:"EIA-485 half-duplex diff.",conn:"JST-GH 4-pin × 2 per board",route:"Port keel alongside ETH · 120mm · TRIHAT J_RS485b → COMMS-HAT J_RS485a",carries:"MAVLink backup · ESC telemetry · future sensor nodes",pico:"UART1 · GP8 TX · GP9 RX · GP7 DE/RE",cm4:"/dev/ttyAMA2 · GPIO14 TX · GPIO15 RX · GPIO24 DE/RE"},
    {id:"USB CDC-ACM (NEW)",c:C.indigo,speed:"12 Mbps FS",phy:"USB D+/D− diff. 90Ω",conn:"JST-GH 4-pin × 1 (TRIHAT-1)",route:"TRIHAT-1 J_USB → 100mm stub → GL850G hub port 3 on CM4-CARRIER-1",carries:"OTA firmware · debug serial · bulk config · last-resort fallback",pico:"RP2350 built-in USB HW · /dev/ttyACM0 on CM4 side",cm4:"GL850G hub → USB host → CDC-ACM auto-driver · /dev/ttyACM0"},
  ];
  return(<div>
    <Note c={C.accent} ch="Four physically and electrically independent data paths between Pico 2 and CM4. Each path uses a different IC vendor, different connector type (or pin count), different physical signalling, and different software stack — ensuring no single fault propagates across more than one bus."/>
    {buses.map((b,i)=>(
      <div key={i} style={{marginBottom:16,padding:"14px",border:`1px solid ${b.c}33`,borderLeft:`3px solid ${b.c}`,borderRadius:4,background:`${b.c}06`}}>
        <div style={{display:"flex",gap:10,alignItems:"center",marginBottom:10,flexWrap:"wrap"}}>
          <span style={{color:b.c,fontFamily:M,fontSize:13,fontWeight:"bold"}}>{b.id}</span>
          <Tag label={b.speed} c={b.c}/>
          <Tag label={b.phy} c={b.c}/>
          <Tag label={b.conn} c={C.yellow}/>
        </div>
        <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:16}}>
          <div>
            <KV k="Cable route" v={b.route}/>
            <KV k="Carries" v={b.carries} vc={C.teal}/>
          </div>
          <div>
            <KV k="Pico 2 / TRIHAT-1" v={b.pico} vc={C.accent}/>
            <KV k="CM4 / COMMS-HAT-1" v={b.cm4} vc={C.green}/>
          </div>
        </div>
      </div>
    ))}
    <SH t="Routing Summary (keel spine cross-section)"/>
    <div style={{fontFamily:M,fontSize:10,lineHeight:2,color:C.dim,padding:"12px",border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.02)"}}>
      <span style={{color:C.orange}}>━━━━</span> CANH/CANL (CAN FD) — starboard keel · 4-pin JST-GH chain
      {" · "}<span style={{color:C.purple}}>━━━━</span> ETH TX+/TX−/RX+/RX− — port keel · 6-pin JST-GH
      {" · "}<span style={{color:C.lime}}>━━━━</span> RS-485 A/B — port keel alongside ETH · 4-pin JST-GH
      <br/>
      <span style={{color:C.indigo}}>━━━━</span> USB D+/D− — port keel · 4-pin JST-GH stub to GL850G hub
      {" · "}<span style={{color:C.teal}}>━━━━</span> SiK coax RG-316 — belly · separate from all digital lines
      <br/>
      <span style={{color:C.dim}}>Minimum separation: CAN from ETH/RS485 ≥20mm · RS485 may share port keel with ETH (both differential, low mutual interference) · USB stub ≤100mm (keep short to avoid USB impedance issues)</span>
    </div>
  </div>);
}

// ═══════════════════════════════════════════════════════════════
//  TAB 7 — BOM DELTA
// ═══════════════════════════════════════════════════════════════
function BOMDeltaTab(){
  const adds=[
    {qty:2, ref:"U_485_TH",  part:"SP485EN SOIC-8 RS-485 transceiver",      board:"TRIHAT-1",    mass:"0.15g",est:"$0.45ea",note:"One per board — Renesas/IXYS"},
    {qty:2, ref:"U_485_CP",  part:"SP485EN SOIC-8 RS-485 transceiver",      board:"COMMS-HAT-1",   mass:"0.15g",est:"$0.45ea",note:""},
    {qty:2, ref:"R_B1_B2",   part:"560Ω 0402 bias resistors ×2 set",        board:"TRIHAT-1",    mass:"0.02g",est:"$0.05",note:"A-to-+3V3 and B-to-GND bias"},
    {qty:4, ref:"J_RS485_TH",part:"JST-GH 1.25mm 4-pin RS-485 IN+OUT",     board:"TRIHAT-1",    mass:"0.2g ea",est:"$0.30ea",note:""},
    {qty:4, ref:"J_RS485_CP",part:"JST-GH 1.25mm 4-pin RS-485 IN+OUT",     board:"COMMS-HAT-1",   mass:"0.2g ea",est:"$0.30ea",note:""},
    {qty:1, ref:"J_CAN2_TH", part:"JST-GH 1.25mm 4-pin CAN OUT (J2b)",    board:"TRIHAT-1",    mass:"0.2g",est:"$0.30",note:"Mirrors existing J2a"},
    {qty:1, ref:"J_CAN2_CP", part:"JST-GH 1.25mm 4-pin CAN OUT (J1b)",    board:"COMMS-HAT-1",   mass:"0.2g",est:"$0.30",note:"Mirrors existing J1a"},
    {qty:2, ref:"JP_TERM",   part:"2-pin 2.54mm jumper header + shunt",    board:"Both boards", mass:"0.1g ea",est:"$0.10ea",note:"Replaces solder bridge — proper jumper"},
    {qty:1, ref:"J_USB_TH",  part:"JST-GH 1.25mm 4-pin USB (J_USB)",       board:"TRIHAT-1",    mass:"0.2g",est:"$0.30",note:"VBUS · D+ · D− · GND"},
    {qty:1, ref:"CBL_RS485", part:"JST-GH 4-pin RS-485 cable 120mm",        board:"Cable",       mass:"1.2g",est:"$3.50",note:"Twisted A/B pair · TRIHAT-1↔COMMS-HAT-1"},
    {qty:1, ref:"CBL_USB",   part:"JST-GH 4-pin USB stub 100mm",            board:"Cable",       mass:"0.7g",est:"$2.50",note:"D+/D− matched 90Ω · TRIHAT-1 J_USB → GL850G"},
  ];
  const removes=[
    {ref:"SOLDER_BR_TH", part:"120Ω CAN solder bridge on TRIHAT-1",  note:"Replaced by JP_TERM jumper header"},
    {ref:"SOLDER_BR_CP", part:"120Ω CAN solder bridge on COMMS-HAT-1", note:"Replaced by JP_TERM jumper header"},
  ];
  const totalMassAdded = 0.15*2+0.15*2+0.02+0.2*4+0.2*4+0.2+0.2+0.1*2+0.2+1.2+0.7;
  const totalCost = 0.45*2+0.45*2+0.05+0.30*4+0.30*4+0.30+0.30+0.10*2+0.30+3.50+2.50;

  return(<div>
    <SH t="ADDED — Rev F Connectivity Update" mt={0} c={C.green}/>
    <div style={{overflowX:"auto",marginBottom:20}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["QTY","REF","COMPONENT","BOARD","MASS","~USD","NOTE"]}/>
        <tbody>{adds.map((r,i)=>(<tr key={i} style={{background:i%2===0?"rgba(74,222,128,0.03)":"transparent",verticalAlign:"top"}}>
          <td style={{padding:"5px 8px",color:C.accent,fontWeight:"bold",textAlign:"center"}}>{r.qty}</td>
          <td style={{padding:"5px 8px",color:C.yellow,fontSize:9,whiteSpace:"nowrap"}}>{r.ref}</td>
          <td style={{padding:"5px 8px",color:C.text}}>{r.part}</td>
          <td style={{padding:"5px 8px",color:C.teal,fontSize:9,whiteSpace:"nowrap"}}>{r.board}</td>
          <td style={{padding:"5px 8px",color:C.green,whiteSpace:"nowrap"}}>{r.mass}</td>
          <td style={{padding:"5px 8px",color:C.green,fontWeight:"bold",whiteSpace:"nowrap"}}>{r.est}</td>
          <td style={{padding:"5px 8px",color:C.dimmer,fontSize:9}}>{r.note}</td>
        </tr>))}</tbody>
        <tfoot>
          <tr style={{borderTop:`1px solid ${C.border}`}}>
            <td colSpan={4} style={{padding:"7px 8px",color:C.green,textAlign:"right",fontSize:10}}>TOTAL ADDED MASS</td>
            <td style={{padding:"7px 8px",color:C.green,fontWeight:"bold",fontSize:13}}>{totalMassAdded.toFixed(1)}g</td>
            <td style={{padding:"7px 8px",color:C.green,fontWeight:"bold",fontSize:13}}>${totalCost.toFixed(2)}</td>
            <td/>
          </tr>
        </tfoot>
      </table>
    </div>

    <SH t="REMOVED — Rev F Connectivity Update" c={C.red}/>
    <div style={{overflowX:"auto",marginBottom:20}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["REF","COMPONENT","REASON"]}/>
        <tbody>{removes.map((r,i)=>(<tr key={i} style={{background:"rgba(248,113,113,0.03)",verticalAlign:"top"}}>
          <td style={{padding:"5px 8px",color:C.red,fontSize:9,whiteSpace:"nowrap"}}>{r.ref}</td>
          <td style={{padding:"5px 8px",color:C.text}}>{r.part}</td>
          <td style={{padding:"5px 8px",color:C.dimmer,fontSize:9}}>{r.note}</td>
        </tr>))}</tbody>
      </table>
    </div>

    <SH t="Net Delta Summary" c={C.yellow}/>
    <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:12}}>
      {[
        {l:"Mass added",v:`+${totalMassAdded.toFixed(1)}g`,c:C.green,s:"~0.4% of 1002g AUW"},
        {l:"Cost added",v:`+$${totalCost.toFixed(2)}`,c:C.yellow,s:"One-time BOM increase"},
        {l:"New data paths",v:"2",c:C.accent,s:"RS-485 + USB CDC-ACM"},
        {l:"New ICs",v:"2",c:C.teal,s:"SP485EN × 2 (SOIC-8)"},
      ].map((s,i)=>(<div key={i} style={{padding:"10px 12px",border:`1px solid ${s.c}44`,background:`${s.c}07`,borderRadius:4}}>
        <div style={{color:C.dim,fontFamily:M,fontSize:9,letterSpacing:"0.08em",marginBottom:3}}>{s.l}</div>
        <div style={{color:s.c,fontFamily:M,fontSize:20,fontWeight:"bold"}}>{s.v}</div>
        <div style={{color:C.dimmer,fontFamily:M,fontSize:9,marginTop:2}}>{s.s}</div>
      </div>))}
    </div>
    <Good ch={`Total result: ${totalMassAdded.toFixed(1)}g added for four fully independent, physically distinct data paths (CAN FD · Ethernet · RS-485 · USB). Any single wiring fault, IC failure, or PCB trace crack affects at most one path. The other three remain fully operational.`}/>
  </div>);
}

// ═══════════════════════════════════════════════════════════════
//  APP
// ═══════════════════════════════════════════════════════════════
const TABS=["Protocol Analysis","CAN Daisy Chain","RS-485","USB CDC-ACM","Hat Specs","Wiring Matrix","BOM Delta"];

_ODFontLoader();
export default function App(){
  const [tab,setTab]=useState("Protocol Analysis");
  return(<div style={{minHeight:"100vh",background:C.bg,color:C.text,fontFamily:M}}>
    <Grid/>
    <div style={{position:"relative",zIndex:1,borderBottom:`1px solid ${C.border}`,padding:"16px 24px 12px"}}>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",flexWrap:"wrap",gap:12}}>
        <div>
          <div style={{color:"rgba(163,230,53,0.3)",fontSize:9,letterSpacing:"0.2em",marginBottom:4}}>
            SERENITY TILTROTOR · CONNECTIVITY UPDATE · REV F
          </div>
          <h1 style={{margin:0,fontSize:18,fontWeight:"normal",color:"#fff",letterSpacing:"0.07em"}}>
            DUAL CAN JST · RS-485 · USB CDC-ACM
          </h1>
          <div style={{color:"rgba(0,229,255,0.45)",fontSize:10,marginTop:3}}>
            Four independent data paths · +6.7g total · 2 new ICs · CC BY 4.0 · 2026
          </div>
        </div>
        <div style={{textAlign:"right",fontFamily:M}}>
          <div style={{color:C.lime,fontSize:12,fontWeight:"bold"}}>+6.7g total delta</div>
          <div style={{color:C.green,fontSize:11,marginTop:2}}>~$21 BOM increase</div>
          <div style={{color:C.dimmer,fontSize:9,marginTop:2}}>Steve Griffing PE(CSE) CISSP-ISSEP CPP</div>
        </div>
      </div>
      <div style={{display:"flex",gap:2,marginTop:12,flexWrap:"wrap"}}>
        {TABS.map(t=>(<button key={t} onClick={()=>setTab(t)} style={{background:tab===t?"rgba(0,229,255,0.09)":"transparent",border:`1px solid ${tab===t?C.accent:"rgba(0,229,255,0.12)"}`,color:tab===t?C.accent:C.dimmer,padding:"4px 11px",fontFamily:M,fontSize:9,cursor:"pointer",letterSpacing:"0.06em",transition:"all 0.12s"}}>{t}</button>))}
      </div>
    </div>
    <div style={{position:"relative",zIndex:1,padding:"20px 24px",maxWidth:1060,margin:"0 auto"}}>
      {tab==="Protocol Analysis" && <ProtocolAnalysisTab/>}
      {tab==="CAN Daisy Chain"   && <CANDaisyTab/>}
      {tab==="RS-485"            && <RS485Tab/>}
      {tab==="USB CDC-ACM"       && <USBTab/>}
      {tab==="Hat Specs"         && <HatSpecsTab/>}
      {tab==="Wiring Matrix"     && <WiringMatrixTab/>}
      {tab==="BOM Delta"         && <BOMDeltaTab/>}
    </div>
    <div style={{position:"relative",zIndex:1,borderTop:`1px solid ${C.border}`,padding:"10px 24px",display:"flex",justifyContent:"space-between",flexWrap:"wrap",gap:6}}>
      <span style={{color:"rgba(163,230,53,0.2)",fontSize:8,letterSpacing:"0.1em"}}>
        © 2026 STEVE GRIFFING PE(CSE) [CONTROL SYSTEMS ENGINEERING] CISSP-ISSEP CPP · CC BY 4.0
      </span>
      <span style={{color:"rgba(0,229,255,0.16)",fontSize:8}}>
        HULL: PETER FARELL CC BY 4.0 · NOZZLE: BAmJr CC BY 4.0 · VISUAL: FIREFLY/SERENITY © JOSS WHEDON/MUTANT ENEMY/UNIVERSAL
      </span>
    </div>
  </div>);
}
