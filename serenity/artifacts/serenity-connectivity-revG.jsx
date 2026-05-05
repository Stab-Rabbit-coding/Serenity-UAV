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
  i2c:"#4ade80",    // green   — I²C
};
const M = "'OpenDyslexic Mono','OpenDyslexic','OpenDyslexicMono',monospace";

// ── primitives ────────────────────────────────────────────────
const SH=({t,c=C.accent,mt=22})=>(<div style={{display:"flex",alignItems:"center",gap:10,marginBottom:14,marginTop:mt}}><div style={{width:3,height:17,background:c}}/><span style={{color:c,fontFamily:M,fontSize:13,letterSpacing:"0.13em",textTransform:"uppercase",fontWeight:"normal"}}>{t}</span></div>);
const KV=({k,v,vc=C.text,u=""})=>(<div style={{display:"flex",justifyContent:"space-between",padding:"5px 0",borderBottom:"1px solid rgba(0,229,255,0.07)",alignItems:"baseline"}}><span style={{color:C.dim,fontFamily:M,fontSize:11}}>{k}</span><span style={{color:vc,fontFamily:M,fontSize:11}}>{v}{u&&<span style={{color:C.accent,marginLeft:4,fontSize:10}}>{u}</span>}</span></div>);
const Note=({c=C.dim,ch})=>(<div style={{marginTop:8,marginBottom:6,color:c,fontFamily:M,fontSize:10,lineHeight:1.85,padding:"8px 12px",borderLeft:`2px solid ${c}55`,background:`${c}07`,borderRadius:3}}>{ch}</div>);
const Warn=({ch})=>(<div style={{marginTop:8,color:C.yellow,fontFamily:M,fontSize:10,lineHeight:1.8,padding:"7px 12px",borderLeft:`2px solid ${C.yellow}`,background:"rgba(255,230,0,0.05)",borderRadius:3}}>⚠ {ch}</div>);
const Good=({ch})=>(<div style={{marginTop:8,color:C.green,fontFamily:M,fontSize:10,lineHeight:1.8,padding:"7px 12px",borderLeft:`2px solid ${C.green}`,background:"rgba(74,222,128,0.05)",borderRadius:3}}>✓ {ch}</div>);
function TH({cols}){return(<thead><tr>{cols.map(h=>(<th key={h} style={{padding:"6px 9px",borderBottom:`1px solid ${C.border}`,color:C.accent,textAlign:"left",fontWeight:"normal",fontSize:10,letterSpacing:"0.06em",whiteSpace:"nowrap",opacity:.85}}>{h}</th>))}</tr></thead>);}
function Grid(){return(<svg style={{position:"fixed",inset:0,width:"100%",height:"100%",pointerEvents:"none",zIndex:0}}><defs><pattern id="sg" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0L0 0 0 20" fill="none" stroke="rgba(0,229,255,0.035)" strokeWidth={0.5}/></pattern><pattern id="lg" width="100" height="100" patternUnits="userSpaceOnUse"><rect width="100" height="100" fill="url(#sg)"/><path d="M100 0L0 0 0 100" fill="none" stroke="rgba(0,229,255,0.065)" strokeWidth={1}/></pattern></defs><rect width="100%" height="100%" fill="url(#lg)"/></svg>);}
function ProtoTag({label,c}){return(<span style={{color:c,border:`1px solid ${c}`,padding:"1px 8px",borderRadius:2,fontFamily:M,fontSize:9,letterSpacing:"0.06em",whiteSpace:"nowrap"}}>{label}</span>);}

// ── protocol config table ────────────────────────────────────
const PROTOCOLS = [
  {
    id:"eth",  label:"Ethernet 100BASE-T", color:C.eth,
    topology:"Star / point-to-point", speed:"100 Mbps",
    maxNodes:"Limited by switch port count", wire:"4-pin JST-GH (TX+,TX−,RX+,RX−)",
    phy:"W5500 HW TCP/IP · HX1188NL magnetics", connectors:1,
    layers:"TCP/IP · UDP · HTTP/REST · MAVLink-over-UDP",
    use:"High-bandwidth log stream · GCS relay · OTA updates · mission upload",
    priority:"High-bandwidth background", latency:"<1ms (LAN)",
    addedRevG:false, weight:"~3g cable", terminators:"auto-MDIX, none needed",
    extensibility:"Add managed switch (e.g. KSZ8795) to enable 5-port star for 4 additional nodes. Each node needs its own W5500 or equivalent. No topology change on existing boards.",
    notes:"Already implemented Rev E. Adding a managed Ethernet switch enables N-node mesh without changing any existing board design.",
    pinout:["GND","TX+","TX−","RX+","RX−","N/C"],
    jst:6,
  },
  {
    id:"can",  label:"CAN FD (ISO 11898-1)", color:C.can,
    topology:"Bus (daisy-chain) — REV G: 2nd connector added", speed:"1 Mbps nominal / 4 Mbps FD",
    maxNodes:"≤128 (CISPR11 limit) · practical ≤32", wire:"4-pin JST-GH (GND,+5V,CANH,CANL) ×2",
    phy:"MCP2518FD + MCP2562FD · 5V bus / 3.3V logic",
    layers:"ISO 11898-1:2015 · DroneCAN / UAVCANv1",
    use:"Real-time AHRS · ESC RPM · arm/disarm · mission commands · safety-critical control",
    priority:"Real-time safety-critical", latency:"<500µs",
    addedRevG:true, weight:"~2g second cable+connector",terminators:"120Ω only at physical endpoints",
    extensibility:"TRUE daisy-chain bus. Adding node N: plug into any J_CAN_IN, out to J_CAN_OUT. Move 120Ω terminator to new last node. No configuration change on other nodes.",
    notes:"Rev G adds J_CAN_IN and J_CAN_OUT (both 4-pin JST-GH) on TRIHAT-1 and COMPHAT-1. Internally connected in parallel — bus topology, not switched.",
    pinout:["GND","+5V","CANH","CANL"],
    jst:4,
  },
  {
    id:"rs4",  label:"RS-485 / EIA-485", color:C.rs4,
    topology:"Bus (daisy-chain) · half-duplex multi-drop", speed:"up to 10 Mbps · practical 1 Mbps",
    maxNodes:"32 per segment · unlimited with repeaters", wire:"4-pin JST-GH (GND,+5V,A+,B−) ×2",
    phy:"MAX3485 SOT-23 · 3.3V logic · 100mW typical",
    layers:"UART framing · MAVLink 2.0 or MODBUS RTU",
    use:"Secondary MAVLink path · distributed sensor aggregation · ESC config · future nacelle sensor nodes",
    priority:"Secondary telemetry + sensor bus", latency:"<2ms at 1Mbps",
    addedRevG:true, weight:"~2g IC+connectors per board", terminators:"120Ω at each physical bus end · biasing resistors at driver",
    extensibility:"Ideal daisy-chain bus. Add any number of nodes by inserting between existing connectors. Direction control (DE/RE) per node on UART GPIO. No master/slave address scheme — all nodes are equal.",
    notes:"Uses existing UART1 on Pico 2 (GP4/GP5) and UART2 on CM4. MAX3485 in SOT-23 is 3mm×3mm — trivial PCB footprint. Two JST-GH connectors (IN and OUT) for through-connection.",
    pinout:["GND","+5V","RS485-A+","RS485-B−"],
    jst:4,
  },
  {
    id:"i2c",  label:"I²C System Expansion Bus", color:C.i2c,
    topology:"Bus (wired-AND open-drain) · multi-master", speed:"400 kHz Standard+ · 1 MHz Fast-mode+ with buffer",
    maxNodes:"127 unique 7-bit addresses · unlimited with mux", wire:"4-pin JST-GH (GND,+3V3,SDA,SCL) ×2",
    phy:"NXP PCA9517 buffer per board · TVS + common-mode choke · 4.7kΩ pullups at master only",
    layers:"I²C protocol · no higher-level framing needed",
    use:"Distributed sensor bus · future nacelle IMUs · battery monitors · GPIO expanders · PWM controllers for additional actuators",
    priority:"Slow sensor / peripheral bus", latency:"<5ms at 400kHz",
    addedRevG:true, weight:"~1.5g buffer IC+connectors per board", terminators:"Pullups only at one point (TRIHAT-1) · no termination resistors",
    extensibility:"Wired-AND bus. Add any I²C device by tapping onto the bus at any point. Expand beyond 127 devices using TCA9548 8-channel mux — one mux can host 64 more unique devices. Repeater (PCA9517) every 1m.",
    notes:"I²C1 on Pico 2 (GP14/GP15 — freed by Rev G nozzle servo change) and CM4 GPIO2/GPIO3. Use PCA9517 active buffer to handle EDF EMI — prevents bus latch-up from voltage spikes. TVS diodes (PRTR5V0U2X) on each board for ESD/transient protection.",
    pinout:["GND","+3V3","SDA","SCL"],
    jst:4,
  },
];

// ── selection rationale data ────────────────────────────────
const REJECTED = [
  {p:"UART TTL (direct)", reason:"Point-to-point only · not extensible beyond 2 nodes · no differential noise immunity · not a bus"},
  {p:"I2S (audio bus)", reason:"Synchronous, clocked — master-slave only · no multi-master · no daisy-chain · wrong use case"},
  {p:"SPI (raw)", reason:"Requires separate CS per device · not bus topology · master-centric · poor extensibility"},
  {p:"USB 2.0", reason:"Hub topology requires host controller + powered hub · adds ~10g · complexity high · latency variable"},
  {p:"LIN Bus", reason:"Single-wire but 20kbps max · too slow for MAVLink backup · automotive-only ecosystem · master-slave architecture"},
  {p:"ARINC 429", reason:"Aviation standard but UNIDIRECTIONAL · requires dedicated hardware · heavy · overkill for sUAS scale"},
  {p:"MIL-STD-1553", reason:"Military avionics · dual-redundant but requires expensive transceivers · 1Mbps max · weight penalty"},
  {p:"FlexRay", reason:"Fault-tolerant but requires dedicated ECU controllers · automotive only · high PCB complexity"},
  {p:"Second Ethernet port", reason:"Already have Ethernet · adds switch hardware · weight of switch (~8g) outweighs benefit · CAN+RS-485 fill the gap more efficiently"},
  {p:"SpaceWire / LVDS", reason:"Aerospace standard · high speed but point-to-point pairs · not bus topology · complex connectors · overkill"},
];

// ── node extensibility matrix ─────────────────────────────
const NODE_MATRIX = [
  {nodes:2,  label:"Current (Pico 2 + CM4)",
   eth:"Point-to-point direct",can:"Pico=node1 CM4=node2 · 120Ω each end",
   rs4:"Pico=master CM4=slave · 120Ω each end",i2c:"Pico=master CM4=sensor client"},
  {nodes:3,  label:"+ 1 nacelle controller",
   eth:"Add W5500 to nacelle · no switch (hub needed beyond 3)",can:"Nacelle taps into chain · move term. to nacelle",
   rs4:"Nacelle taps in · no term. change on interior node",i2c:"Nacelle I²C sensors tap anywhere on bus"},
  {nodes:5,  label:"+ 2 nacelle + 1 payload",
   eth:"Add KSZ8795 5-port switch (7g) · full star",can:"All 5 in chain · terms only at ends",
   rs4:"All 5 on bus · terms only at ends · DE/RE per node",i2c:"Add TCA9548 mux if address conflicts arise"},
  {nodes:12, label:"Full distributed UAV platform",
   eth:"KSZ9896 6-port GbE switch · VLAN per function",can:"Split into 2 buses if >32 nodes or need isolation",
   rs4:"Add RS-485 repeater at midpoint if >32 nodes",i2c:"TCA9548 mux + PCA9517 repeaters every 1m"},
];

// ════════════════════════════════════════════════════════════
// DIAGRAM: 4-bus architecture wiring diagram
// ════════════════════════════════════════════════════════════
function FourBusDiagram(){
  const VW=720, VH=420;
  // Node blocks
  const nodes=[
    {x:60,  y:160, w:120, h:100, label:"PICO 2",    sub:"TRIHAT-1",     c:C.accent, fc:C.teal},
    {x:540, y:160, w:120, h:100, label:"CM4 LITE",  sub:"COMPHAT-1",    c:C.green,  fc:C.lime},
  ];
  // Future node placeholder
  const future={x:280, y:340, w:160, h:50};

  // Bus paths (y-positions between nodes)
  const busY={eth:120, can:180, rs4:220, i2c:260};
  const busC={eth:C.eth,can:C.can,rs4:C.rs4,i2c:C.i2c};
  const busW={eth:3,can:3,rs4:3,i2c:2};
  const busDash={eth:"none",can:"none",rs4:"5 3",i2c:"3 2"};
  const busLabel={eth:"100BASE-T Ethernet",can:"CAN FD 4Mbps",rs4:"RS-485 1Mbps",i2c:"I²C 400kHz"};
  const busPin={eth:"6-pin JST-GH ×1",can:"4-pin JST-GH ×2",rs4:"4-pin JST-GH ×2",i2c:"4-pin JST-GH ×2"};
  const busRole={eth:"High-bandwidth log/config",can:"Safety-critical control",rs4:"Secondary telemetry",i2c:"Sensor expansion"};

  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* Node blocks */}
      {nodes.map((n,i)=>(
        <g key={i}>
          <rect x={n.x} y={n.y} width={n.w} height={n.h} rx={6}
            fill={`${n.c}12`} stroke={n.c} strokeWidth={2}/>
          <text x={n.x+n.w/2} y={n.y+24} textAnchor="middle" fill={n.c}
            fontSize={11} fontFamily={M} fontWeight="bold">{n.label}</text>
          <text x={n.x+n.w/2} y={n.y+40} textAnchor="middle" fill={`${n.c}80`}
            fontSize={9} fontFamily={M}>{n.sub}</text>
          {/* Connector stacks */}
          {Object.entries(busY).map(([bus,by],j)=>{
            const nx = i===0 ? n.x+n.w : n.x;
            const col = busC[bus];
            return(<g key={bus}>
              <rect x={i===0?nx:nx-12} y={by-8} width={12} height={16} rx={2}
                fill={`${col}25`} stroke={col} strokeWidth={1.2}/>
              <text x={i===0?nx-3:nx-6} y={by+3} textAnchor="middle"
                fill={col} fontSize={6} fontFamily={M}
                transform={`rotate(-90,${i===0?nx-3:nx-6},${by+3})`}>{bus.toUpperCase()}</text>
            </g>);
          })}
        </g>
      ))}

      {/* Bus lines */}
      {Object.entries(busY).map(([bus,by])=>{
        const col=busC[bus]; const bw=busW[bus]; const bd=busDash[bus];
        const x1=nodes[0].x+nodes[0].w+12; const x2=nodes[1].x-12;
        return(<g key={bus}>
          <line x1={x1} y1={by} x2={x2} y2={by}
            stroke={col} strokeWidth={bw} strokeDasharray={bd} strokeLinecap="round"/>
          {/* Bus label at midpoint */}
          <rect x={(x1+x2)/2-75} y={by-18} width={150} height={14} rx={3}
            fill={`${col}18`} stroke={`${col}55`} strokeWidth={0.8}/>
          <text x={(x1+x2)/2} y={by-7} textAnchor="middle"
            fill={col} fontSize={8} fontFamily={M} fontWeight="bold">{busLabel[bus]}</text>
          {/* Pin label */}
          <text x={(x1+x2)/2} y={by+12} textAnchor="middle"
            fill={`${col}70`} fontSize={7} fontFamily={M}>{busPin[bus]}</text>
        </g>);
      })}

      {/* Future node tap point on bus */}
      <rect x={future.x} y={future.y} width={future.w} height={future.h} rx={5}
        fill="rgba(255,255,255,0.04)" stroke="rgba(255,255,255,0.2)"
        strokeWidth={1.5} strokeDasharray="6 3"/>
      <text x={future.x+future.w/2} y={future.y+20} textAnchor="middle"
        fill="rgba(255,255,255,0.4)" fontSize={10} fontFamily={M}>FUTURE NODE N</text>
      <text x={future.x+future.w/2} y={future.y+34} textAnchor="middle"
        fill="rgba(255,255,255,0.25)" fontSize={8} fontFamily={M}>Nacelle controller / payload / sensor hub</text>

      {/* Tap lines from bus to future node */}
      {[C.can,C.rs4,C.i2c].map((col,i)=>{
        const by=Object.values(busY)[i+1];
        return(<g key={i}>
          <line x1={VW/2} y1={by} x2={future.x+future.w/2} y2={future.y}
            stroke={col} strokeWidth={1.5} strokeDasharray="4 3" opacity={0.5}/>
          <circle cx={VW/2} cy={by} r={4} fill={col} opacity={0.7}/>
        </g>);
      })}
      {/* Ethernet tap (needs switch) */}
      <line x1={VW/2} y1={busY.eth} x2={future.x+future.w/2} y2={future.y}
        stroke={C.eth} strokeWidth={1.5} strokeDasharray="2 4" opacity={0.3}/>
      <text x={future.x-60} y={future.y-12} textAnchor="middle"
        fill={`${C.eth}60`} fontSize={7} fontFamily={M}>+switch for ETH</text>

      {/* Terminator indicators */}
      {[C.can,C.rs4].map((col,i)=>{
        const by=i===0?busY.can:busY.rs4;
        return(<g key={i}>
          {/* Left end terminator */}
          <rect x={nodes[0].x+nodes[0].w+14} y={by-6} width={10} height={12} rx={2}
            fill={col} opacity={0.7}/>
          <text x={nodes[0].x+nodes[0].w+19} y={by+3} textAnchor="middle"
            fill="rgba(0,0,0,0.8)" fontSize={6} fontFamily={M} fontWeight="bold">Ω</text>
          {/* Right end terminator */}
          <rect x={nodes[1].x-24} y={by-6} width={10} height={12} rx={2}
            fill={col} opacity={0.7}/>
          <text x={nodes[1].x-19} y={by+3} textAnchor="middle"
            fill="rgba(0,0,0,0.8)" fontSize={6} fontFamily={M} fontWeight="bold">Ω</text>
          <text x={(nodes[0].x+nodes[0].w+nodes[1].x)/2} y={by+22}
            textAnchor="middle" fill={`${col}60`} fontSize={6} fontFamily={M}>
            120Ω at endpoints only</text>
        </g>);
      })}

      {/* I2C pullups at master */}
      <rect x={nodes[0].x+nodes[0].w+14} y={busY.i2c-6} width={10} height={12} rx={2}
        fill={C.i2c} opacity={0.7}/>
      <text x={nodes[0].x+nodes[0].w+19} y={busY.i2c+3} textAnchor="middle"
        fill="rgba(0,0,0,0.8)" fontSize={6} fontFamily={M} fontWeight="bold">↑</text>
      <text x={(nodes[0].x+nodes[0].w+nodes[1].x)/2} y={busY.i2c+22}
        textAnchor="middle" fill={`${C.i2c}60`} fontSize={6} fontFamily={M}>
        4.7kΩ pullups at TRIHAT-1 only</text>

      {/* Legend */}
      <rect x={10} y={10} width={200} height={90} rx={4}
        fill="rgba(0,0,0,0.5)" stroke="rgba(255,255,255,0.1)" strokeWidth={0.8}/>
      <text x={110} y={26} textAnchor="middle" fill={C.dimmer} fontSize={8}
        fontFamily={M} letterSpacing="1">BUS ARCHITECTURE</text>
      {Object.entries(busC).map(([bus,col],i)=>(
        <g key={bus}>
          <line x1={20} y1={36+i*18} x2={50} y2={36+i*18}
            stroke={col} strokeWidth={2.5} strokeDasharray={busDash[bus]}/>
          <text x={56} y={40+i*18} fill={col} fontSize={8} fontFamily={M}>
            {busLabel[bus]} — {busRole[bus]}</text>
        </g>
      ))}

      <text x={VW/2} y={14} textAnchor="middle" fill="rgba(0,229,255,0.25)"
        fontSize={9} fontFamily={M} letterSpacing="0.1em">
        4-BUS REDUNDANT DATA ARCHITECTURE — 2-NODE BASELINE</text>
      <text x={VW/2} y={VH-6} textAnchor="middle" fill="rgba(0,229,255,0.2)"
        fontSize={7} fontFamily={M}>
        Future node taps CAN + RS-485 + I²C without modifying existing boards — Ethernet requires managed switch for N>2</text>
    </svg>
  );
}

// ════════════════════════════════════════════════════════════
// DIAGRAM: CAN daisy-chain connector layout on PCB
// ════════════════════════════════════════════════════════════
function CANDaisyDiagram(){
  const VW=580, VH=280;
  // Board outline
  const BX=40,BY=40,BW=500,BH=200;
  const col=C.can;
  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:600,display:"block"}}>
      {/* Board outline */}
      <rect x={BX} y={BY} width={BW} height={BH} rx={6}
        fill="rgba(255,107,53,0.04)" stroke={col} strokeWidth={1.5}/>
      <text x={BX+BW/2} y={BY+20} textAnchor="middle"
        fill={col} fontSize={9} fontFamily={M}>TRIHAT-1 or COMPHAT-1 (65×48mm)</text>

      {/* MCP2518FD IC */}
      <rect x={BX+BW/2-30} y={BY+60} width={60} height={80} rx={4}
        fill="rgba(255,107,53,0.1)" stroke={col} strokeWidth={1.5}/>
      <text x={BX+BW/2} y={BY+97} textAnchor="middle"
        fill={col} fontSize={9} fontFamily={M} fontWeight="bold">MCP2518FD</text>
      <text x={BX+BW/2} y={BY+112} textAnchor="middle"
        fill={`${col}70`} fontSize={7} fontFamily={M}>CAN FD controller</text>
      <text x={BX+BW/2} y={BY+126} textAnchor="middle"
        fill={`${col}50`} fontSize={7} fontFamily={M}>+ MCP2562FD transceiver</text>

      {/* Bus signals from IC */}
      <line x1={BX+BW/2-30} y1={BY+90} x2={BX+BW/2-90} y2={BY+90}
        stroke={col} strokeWidth={2} strokeLinecap="round"/>
      <text x={BX+BW/2-70} y={BY+83} textAnchor="middle"
        fill={`${col}80`} fontSize={7} fontFamily={M}>CANH</text>
      <line x1={BX+BW/2-30} y1={BY+110} x2={BX+BW/2-90} y2={BY+110}
        stroke={col} strokeWidth={2} strokeLinecap="round"/>
      <text x={BX+BW/2-70} y={BY+123} textAnchor="middle"
        fill={`${col}80`} fontSize={7} fontFamily={M}>CANL</text>

      {/* Internal bus trace — connects both connectors */}
      <line x1={BX+60} y1={BY+90} x2={BX+BW-60} y2={BY+90}
        stroke={col} strokeWidth={2.5} strokeLinecap="round"/>
      <line x1={BX+60} y1={BY+110} x2={BX+BW-60} y2={BY+110}
        stroke={col} strokeWidth={2.5} strokeLinecap="round"/>
      <text x={BX+BW/2} y={BY+145} textAnchor="middle"
        fill={`${col}60`} fontSize={7} fontFamily={M}>Internal bus trace — same net both connectors</text>

      {/* J_CAN_IN connector (left edge) */}
      <rect x={BX+18} y={BY+70} width={42} height={60} rx={3}
        fill={`${col}20`} stroke={col} strokeWidth={2}/>
      <text x={BX+39} y={BY+86} textAnchor="middle" fill={col} fontSize={8} fontFamily={M} fontWeight="bold">J_CAN</text>
      <text x={BX+39} y={BY+98} textAnchor="middle" fill={col} fontSize={7} fontFamily={M}>_IN</text>
      {["GND","+5V","CANH","CANL"].map((s,i)=>(
        <text key={s} x={BX+39} y={BY+109+i*10} textAnchor="middle"
          fill={`${col}60`} fontSize={6} fontFamily={M}>{s}</text>
      ))}
      <text x={BX+39} y={BY+170} textAnchor="middle" fill={`${col}60`} fontSize={6} fontFamily={M}>JST-GH 4P</text>

      {/* J_CAN_OUT connector (right edge) */}
      <rect x={BX+BW-60} y={BY+70} width={42} height={60} rx={3}
        fill={`${col}20`} stroke={col} strokeWidth={2}/>
      <text x={BX+BW-39} y={BY+86} textAnchor="middle" fill={col} fontSize={8} fontFamily={M} fontWeight="bold">J_CAN</text>
      <text x={BX+BW-39} y={BY+98} textAnchor="middle" fill={col} fontSize={7} fontFamily={M}>_OUT</text>
      {["GND","+5V","CANH","CANL"].map((s,i)=>(
        <text key={s} x={BX+BW-39} y={BY+109+i*10} textAnchor="middle"
          fill={`${col}60`} fontSize={6} fontFamily={M}>{s}</text>
      ))}
      <text x={BX+BW-39} y={BY+170} textAnchor="middle" fill={`${col}60`} fontSize={6} fontFamily={M}>JST-GH 4P</text>

      {/* 120Ω termination detail */}
      <rect x={BX+18} y={BY+168} width={42} height={22} rx={2}
        fill="rgba(255,230,0,0.1)" stroke={C.yellow} strokeWidth={1}/>
      <text x={BX+39} y={BY+178} textAnchor="middle" fill={C.yellow} fontSize={7} fontFamily={M}>120Ω TERM</text>
      <text x={BX+39} y={BY+187} textAnchor="middle" fill={`${C.yellow}70`} fontSize={6} fontFamily={M}>JP_TERM solder</text>

      {/* Arrows showing through-chain */}
      <path d={`M${BX+4},${BY+100} L${BX+18},${BY+100}`}
        stroke={col} strokeWidth={2} markerEnd="url(#carr)" opacity={0.8}/>
      <path d={`M${BX+BW-18},${BY+100} L${BX+BW-4},${BY+100}`}
        stroke={col} strokeWidth={2} markerEnd="url(#carr)" opacity={0.8}/>
      <defs><marker id="carr" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
        <path d="M0,0 L6,3 L0,6 Z" fill={col}/>
      </marker></defs>
      <text x={BX-2} y={BY+94} textAnchor="end" fill={`${col}70`} fontSize={7} fontFamily={M}>FROM</text>
      <text x={BX-2} y={BY+104} textAnchor="end" fill={`${col}70`} fontSize={7} fontFamily={M}>PREV NODE</text>
      <text x={BX+BW+2} y={BY+94} fill={`${col}70`} fontSize={7} fontFamily={M}>TO</text>
      <text x={BX+BW+2} y={BY+104} fill={`${col}70`} fontSize={7} fontFamily={M}>NEXT NODE</text>

      {/* Note: term only at endpoints */}
      <text x={BX+BW/2} y={BY+210} textAnchor="middle" fill={C.yellow} fontSize={8} fontFamily={M}>
        120Ω solder bridge: CLOSE only on first and last node · OPEN on all interior nodes</text>
      <text x={BX+BW/2} y={VH-8} textAnchor="middle" fill="rgba(0,229,255,0.22)" fontSize={7} fontFamily={M}>
        CAN FD DAISY-CHAIN — DUAL JST-GH — APPLIES EQUALLY TO TRIHAT-1 AND COMPHAT-1</text>
    </svg>
  );
}

// ════════════════════════════════════════════════════════════
// TAB: OVERVIEW
// ════════════════════════════════════════════════════════════
function OverviewTab(){
  return(<div>
    <div style={{background:"rgba(0,229,255,0.04)",border:`1px solid ${C.border}`,borderRadius:4,padding:"14px 16px",marginBottom:20}}>
      <div style={{color:C.lime,fontFamily:M,fontSize:11,fontWeight:"bold",marginBottom:6,letterSpacing:"0.08em"}}>REV G ADDITIONS</div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:16}}>
        <div>
          <KV k="CAN FD daisy-chain" v="2nd JST-GH 4-pin on TRIHAT-1 + COMPHAT-1" vc={C.can}/>
          <KV k="RS-485 (NEW)" v="MAX3485 SOT-23 + 2× JST-GH 4-pin · multi-drop" vc={C.rs4}/>
          <KV k="I²C expansion bus (NEW)" v="PCA9517 buffer + 2× JST-GH 4-pin · sensor bus" vc={C.i2c}/>
          <KV k="Ethernet" v="Unchanged — 1× JST-GH 6-pin point-to-point" vc={C.eth}/>
        </div>
        <div>
          <KV k="Additional PCB area used" v="~14mm width on each hat (RS-485 + I²C ICs + connectors)"/>
          <KV k="Weight delta per board" v="~4g (IC × 2 + connectors × 2 + trace)" vc={C.green}/>
          <KV k="Total weight delta aircraft" v="~8g for both boards" vc={C.green}/>
          <KV k="Extensibility" v="All 4 buses independently extensible to N nodes" vc={C.lime}/>
        </div>
      </div>
    </div>
    <SH t="4-Bus Redundant Architecture" mt={0}/>
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
          {p.addedRevG&&<div style={{marginTop:6,color:C.lime,fontFamily:M,fontSize:8,border:`1px solid ${C.lime}44`,padding:"1px 6px",borderRadius:2,display:"inline-block"}}>NEW Rev G</div>}
        </div>
      ))}
    </div>
    <SH t="Design Principles"/>
    {[["Orthogonal protocols","Each bus was chosen to be technically distinct — different physical layer, topology, and use case. A failure on one bus does not correlate with failure on another. EMI that disrupts Ethernet (common-mode burst) does not affect differential RS-485."],
      ["Separate concerns","Ethernet = high-bandwidth background · CAN FD = safety-critical real-time · RS-485 = secondary MAVLink + sensors · I²C = slow peripheral expansion. No protocol is required to do double duty."],
      ["True daisy-chain on all buses","CAN, RS-485, and I²C are all genuine bus topologies. Adding node N requires only inserting into the chain — no hub, no re-addressing of existing nodes, no firmware changes on other nodes. Ethernet requires a managed switch for N>2 but is already specced."],
      ["Minimum hardware overhead","RS-485 adds one MAX3485 SOT-23 (3×3mm) per board. I²C adds one PCA9517 buffer SOT-23 per board. Neither requires a microcontroller. Total silicon overhead: 2× SOT-23 per hat."],
    ].map(([t,d],i)=>(<div key={i} style={{display:"flex",gap:14,padding:"8px 0",borderBottom:"1px solid rgba(0,229,255,0.07)"}}><span style={{color:C.teal,fontFamily:M,fontSize:10,minWidth:200,flexShrink:0,fontWeight:"bold"}}>{t}</span><span style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.7}}>{d}</span></div>))}
  </div>);
}

// ════════════════════════════════════════════════════════════
// TAB: CAN DAISY-CHAIN
// ════════════════════════════════════════════════════════════
function CANTab(){
  return(<div>
    <SH t="CAN FD Daisy-Chain — Second Connector" mt={0} c={C.can}/>
    <div style={{border:`1px solid ${C.can}33`,borderRadius:4,background:"rgba(255,107,53,0.01)",padding:8,marginBottom:18}}>
      <CANDaisyDiagram/>
    </div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <KV k="Board change" v="Add J_CAN_OUT (4-pin JST-GH) alongside existing J_CAN_IN" vc={C.can}/>
        <KV k="Internal connection" v="J_CAN_IN and J_CAN_OUT share same CANH/CANL net — wired in parallel on PCB"/>
        <KV k="Bus topology" v="Remains linear daisy-chain — no switching, no repeater"/>
        <KV k="Termination" v="120Ω solder bridge (JP_TERM) on each board — close at endpoints only" vc={C.yellow}/>
        <KV k="Max nodes (spec)" v="≤128 (CiA 301) · practical ≤32 at 4Mbps · ≤64 at 1Mbps"/>
        <KV k="Max cable length" v="25m at 1Mbps · 5m at 4Mbps FD · aircraft scale: ≤1m"/>
        <KV k="Pico 2 GPIO" v="GP14 SPI0_CS (MCP2518FD) · unchanged"/>
        <KV k="CM4 GPIO" v="GPIO7 SPI0_CS (MCP2518FD) · unchanged"/>
        <KV k="PCB impact" v="1× JST-GH 4-pin footprint (5.0mm × 5.5mm) · 4 traces to same nets"/>
        <KV k="Weight delta" v="~1g (second JST-GH connector + cable)"/>
      </div>
      <div>
        <Good ch="Adding the second CAN connector requires zero firmware changes on existing nodes. The bus is already a logical bus — the second physical connector simply exposes the 'through' connection that was previously a dead end."/>
        <Warn ch="When adding a 3rd node: open (de-solder) the termination bridge on the previously-last node before connecting the new node. The new last node closes its own termination bridge. Verify with CAN analyser before first arming after topology change."/>
        <Note c={C.can} ch="Why two separate connector labels (IN/OUT) rather than identical connectors? Convention only — helps builders route cables in the correct direction and ensures consistent wiring. Electrically identical. Colour-coded cables recommended: orange for CAN, as established in Rev E."/>
        <SH t="Multi-Node CAN Wiring" c={C.can}/>
        {[["2 nodes (current)","TRIHAT-1 J_CAN_OUT → COMPHAT-1 J_CAN_IN · 120Ω on both (endpoints)"],
          ["3 nodes","TRIHAT-1 OUT → COMPHAT-1 IN; COMPHAT-1 OUT → Node3 IN · 120Ω on TRIHAT-1 and Node3 only; COMPHAT-1 bridge open"],
          ["4+ nodes","Continue chain · only first and last nodes have 120Ω · all interior nodes open"],
        ].map(([n,d],i)=>(<div key={i} style={{display:"flex",gap:10,padding:"6px 0",borderBottom:"1px solid rgba(255,107,53,0.1)"}}><span style={{color:C.can,fontFamily:M,fontSize:9,minWidth:110,flexShrink:0,fontWeight:"bold"}}>{n}</span><span style={{color:C.dim,fontFamily:M,fontSize:9,lineHeight:1.6}}>{d}</span></div>))}
      </div>
    </div>
  </div>);
}

// ════════════════════════════════════════════════════════════
// TAB: RS-485
// ════════════════════════════════════════════════════════════
function RS485Diagram(){
  const VW=580,VH=300;
  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:600,display:"block"}}>
      {/* Board 1 */}
      <rect x={20} y={80} width={130} height={140} rx={5}
        fill="rgba(45,212,191,0.06)" stroke={C.rs4} strokeWidth={1.5}/>
      <text x={85} y={98} textAnchor="middle" fill={C.rs4} fontSize={9} fontFamily={M} fontWeight="bold">TRIHAT-1</text>
      {/* UART tx/rx from Pico */}
      <rect x={32} y={108} width={50} height={24} rx={3} fill="rgba(0,229,255,0.1)" stroke={C.accent} strokeWidth={1}/>
      <text x={57} y={122} textAnchor="middle" fill={C.accent} fontSize={7} fontFamily={M}>UART1 GP4/5</text>
      {/* MAX3485 */}
      <rect x={86} y={104} width={40} height={32} rx={3} fill="rgba(45,212,191,0.15)" stroke={C.rs4} strokeWidth={1.5}/>
      <text x={106} y={118} textAnchor="middle" fill={C.rs4} fontSize={7} fontFamily={M} fontWeight="bold">MAX3485</text>
      <text x={106} y={128} textAnchor="middle" fill={`${C.rs4}70`} fontSize={6} fontFamily={M}>SOT-23-8</text>
      {/* DE/RE from UART GPIO */}
      <line x1={32} y1={124} x2={86} y2={120} stroke={C.accent} strokeWidth={1} strokeDasharray="2 2"/>
      {/* J_RS485_IN */}
      <rect x={24} y={150} width={44} height={50} rx={3} fill="rgba(45,212,191,0.12)" stroke={C.rs4} strokeWidth={1.2}/>
      <text x={46} y={165} textAnchor="middle" fill={C.rs4} fontSize={7} fontFamily={M} fontWeight="bold">J_RS485</text>
      <text x={46} y={175} textAnchor="middle" fill={C.rs4} fontSize={6} fontFamily={M}>_IN</text>
      {["GND","+5V","A+","B−"].map((s,i)=>(<text key={s} x={46} y={184+i*7} textAnchor="middle" fill={`${C.rs4}60`} fontSize={5.5} fontFamily={M}>{s}</text>))}
      {/* J_RS485_OUT */}
      <rect x={82} y={150} width={44} height={50} rx={3} fill="rgba(45,212,191,0.12)" stroke={C.rs4} strokeWidth={1.2}/>
      <text x={104} y={165} textAnchor="middle" fill={C.rs4} fontSize={7} fontFamily={M} fontWeight="bold">J_RS485</text>
      <text x={104} y={175} textAnchor="middle" fill={C.rs4} fontSize={6} fontFamily={M}>_OUT</text>
      {["GND","+5V","A+","B−"].map((s,i)=>(<text key={s} x={104} y={184+i*7} textAnchor="middle" fill={`${C.rs4}60`} fontSize={5.5} fontFamily={M}>{s}</text>))}
      {/* Internal bus trace */}
      <line x1={24} y1={175} x2={20} y2={175} stroke={C.rs4} strokeWidth={2.5}/>
      <line x1={20} y1={175} x2={20} y2={220} stroke={C.rs4} strokeWidth={2.5}/>
      <line x1={20} y1={220} x2={126} y2={220} stroke={C.rs4} strokeWidth={2.5}/>
      <line x1={126} y1={220} x2={126} y2={175} stroke={C.rs4} strokeWidth={2.5}/>
      <text x={73} y={232} textAnchor="middle" fill={`${C.rs4}50`} fontSize={6} fontFamily={M}>bus trace A</text>
      {/* Termination */}
      <rect x={20} y={145} width={12} height={16} rx={2} fill={C.yellow} opacity={0.7}/>
      <text x={26} y={156} textAnchor="middle" fill="rgba(0,0,0,0.8)" fontSize={5.5} fontFamily={M} fontWeight="bold">120Ω</text>
      {/* Biasing resistors */}
      <text x={85} y={145} textAnchor="middle" fill={`${C.rs4}60`} fontSize={5.5} fontFamily={M}>bias R at driver</text>

      {/* Bus cable */}
      <line x1={150} y1={174} x2={220} y2={174} stroke={C.rs4} strokeWidth={3} strokeLinecap="round"/>
      <line x1={150} y1={186} x2={220} y2={186} stroke={C.rs4} strokeWidth={3} strokeLinecap="round"/>
      <text x={185} y={165} textAnchor="middle" fill={`${C.rs4}70`} fontSize={7} fontFamily={M}>twisted pair</text>
      <text x={185} y={198} textAnchor="middle" fill={`${C.rs4}50`} fontSize={6} fontFamily={M}>4-pin JST-GH</text>

      {/* Board 2 */}
      <rect x={220} y={80} width={130} height={140} rx={5}
        fill="rgba(45,212,191,0.06)" stroke={C.rs4} strokeWidth={1.5}/>
      <text x={285} y={98} textAnchor="middle" fill={C.rs4} fontSize={9} fontFamily={M} fontWeight="bold">COMPHAT-1</text>
      <rect x={232} y={108} width={50} height={24} rx={3} fill="rgba(74,222,128,0.1)" stroke={C.green} strokeWidth={1}/>
      <text x={257} y={122} textAnchor="middle" fill={C.green} fontSize={7} fontFamily={M}>UART2 GPIO0/1</text>
      <rect x={286} y={104} width={40} height={32} rx={3} fill="rgba(45,212,191,0.15)" stroke={C.rs4} strokeWidth={1.5}/>
      <text x={306} y={118} textAnchor="middle" fill={C.rs4} fontSize={7} fontFamily={M} fontWeight="bold">MAX3485</text>
      <text x={306} y={128} textAnchor="middle" fill={`${C.rs4}70`} fontSize={6} fontFamily={M}>SOT-23-8</text>
      <rect x={224} y={150} width={44} height={50} rx={3} fill="rgba(45,212,191,0.12)" stroke={C.rs4} strokeWidth={1.2}/>
      <text x={246} y={165} textAnchor="middle" fill={C.rs4} fontSize={7} fontFamily={M} fontWeight="bold">J_RS485</text>
      <text x={246} y={175} textAnchor="middle" fill={C.rs4} fontSize={6} fontFamily={M}>_IN</text>
      {["GND","+5V","A+","B−"].map((s,i)=>(<text key={s} x={246} y={184+i*7} textAnchor="middle" fill={`${C.rs4}60`} fontSize={5.5} fontFamily={M}>{s}</text>))}
      <rect x={282} y={150} width={44} height={50} rx={3} fill="rgba(45,212,191,0.12)" stroke={C.rs4} strokeWidth={1.2}/>
      <text x={304} y={165} textAnchor="middle" fill={C.rs4} fontSize={7} fontFamily={M} fontWeight="bold">J_RS485</text>
      <text x={304} y={175} textAnchor="middle" fill={C.rs4} fontSize={6} fontFamily={M}>_OUT</text>
      {["GND","+5V","A+","B−"].map((s,i)=>(<text key={s} x={304} y={184+i*7} textAnchor="middle" fill={`${C.rs4}60`} fontSize={5.5} fontFamily={M}>{s}</text>))}
      <rect x={338} y={145} width={12} height={16} rx={2} fill={C.yellow} opacity={0.7}/>
      <text x={344} y={156} textAnchor="middle" fill="rgba(0,0,0,0.8)" fontSize={5.5} fontFamily={M} fontWeight="bold">120Ω</text>

      {/* Future node */}
      <line x1={350} y1={174} x2={420} y2={174} stroke={C.rs4} strokeWidth={3} strokeDasharray="5 3" opacity={0.5}/>
      <line x1={350} y1={186} x2={420} y2={186} stroke={C.rs4} strokeWidth={3} strokeDasharray="5 3" opacity={0.5}/>
      <rect x={420} y={150} width={130} height={80} rx={5}
        fill="rgba(255,255,255,0.03)" stroke="rgba(45,212,191,0.3)"
        strokeWidth={1} strokeDasharray="5 3"/>
      <text x={485} y={185} textAnchor="middle" fill="rgba(45,212,191,0.4)"
        fontSize={9} fontFamily={M}>FUTURE NODE N</text>
      <text x={485} y={200} textAnchor="middle" fill="rgba(45,212,191,0.3)"
        fontSize={7} fontFamily={M}>MAX3485 + JST-GH ×2</text>
      {/* move term to future node */}
      <rect x={420} y={145} width={12} height={16} rx={2} fill={C.yellow} opacity={0.4}/>
      <text x={426} y={156} textAnchor="middle" fill="rgba(255,230,0,0.4)" fontSize={5.5} fontFamily={M} fontWeight="bold">120Ω</text>
      <text x={485} y={218} textAnchor="middle" fill={C.yellow} fontSize={6} fontFamily={M}>← moves term here; COMPHAT-1 term opens</text>

      <text x={VW/2} y={14} textAnchor="middle" fill="rgba(0,229,255,0.25)" fontSize={9} fontFamily={M} letterSpacing="0.1em">RS-485 DAISY-CHAIN — MAX3485 SOT-23 — DUAL JST-GH 4-PIN</text>
      <text x={VW/2} y={VH-8} textAnchor="middle" fill="rgba(0,229,255,0.2)" fontSize={7} fontFamily={M}>Direction control (DE/RE): active-high on UART TX GPIO · pull-up default receive</text>
    </svg>
  );
}

function RS485Tab(){
  return(<div>
    <SH t="RS-485 — Secondary Data Bus (NEW Rev G)" mt={0} c={C.rs4}/>
    <div style={{border:`1px solid ${C.rs4}33`,borderRadius:4,background:"rgba(45,212,191,0.01)",padding:8,marginBottom:18}}>
      <RS485Diagram/>
    </div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="Why RS-485?" mt={0} c={C.rs4}/>
        {[["True multi-drop bus","Up to 32 nodes per segment on a 2-wire differential pair. Passive bus — no master required. Any node can transmit (with collision avoidance via DE/RE direction control)."],
          ["Differential noise immunity","RS-485 uses A/B differential signalling. Rejects common-mode noise from EDF motor inverters up to ±7V. Far superior to single-ended UART in drone EMI environment."],
          ["Tiny hardware footprint","MAX3485 SOT-23-8: 2.9×3.0mm. Needs only 2 decoupling capacitors and 2 biasing resistors. No firmware drivers needed beyond existing UART. No clock domain issues."],
          ["Existing UART reuse","Pico 2 UART1 (GP4/GP5) and CM4 UART2 (GPIO0/GPIO1 via expansion) already present. No additional silicon controller needed — MAX3485 is purely a physical-layer device."],
          ["Protocol flexibility","Can carry MAVLink 2.0 (identical to SiK radio protocol), MODBUS RTU (for industrial sensor integration), custom binary framing, or plain ASCII debug. No protocol lock-in."],
        ].map(([t,d],i)=>(<div key={i} style={{marginBottom:10}}><div style={{color:C.rs4,fontFamily:M,fontSize:10,fontWeight:"bold",marginBottom:2}}>{t}</div><div style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.7}}>{d}</div></div>))}
      </div>
      <div>
        <SH t="Technical Specification" mt={0} c={C.rs4}/>
        <KV k="Standard" v="EIA-485 (RS-485) · TIA/EIA-485-A"/>
        <KV k="Transceiver" v="MAX3485 SOT-23-8 · 3.3V · 10Mbps max"/>
        <KV k="Bus type" v="Half-duplex · differential · multi-drop"/>
        <KV k="Max nodes" v="32 per segment (standard) · >32 with repeater"/>
        <KV k="Max cable" v="1,200m at 100kbps · 12m at 10Mbps"/>
        <KV k="Practical rate" v="1Mbps (ample for MAVLink + sensors)"/>
        <KV k="Bus logic" v="A+ > B− = logic 1 (mark) · A+ < B− = logic 0 (space)"/>
        <KV k="Termination" v="120Ω at each physical end · biasing 560Ω pull-up/down at driver"/>
        <KV k="Connectors" v="2× JST-GH 1.25mm 4-pin (IN and OUT)"/>
        <KV k="Pinout" v="GND · +5V · RS485-A+ · RS485-B−"/>
        <KV k="Direction ctrl" v="DE/RE tied together · Pico GP6 / CM4 GPIO4 (UART TX busy detect)"/>
        <KV k="Pico UART" v="UART1 · GP4(TX) · GP5(RX) · GP6(DE/RE)"/>
        <KV k="CM4 UART" v="UART2 · GPIO0(TX) · GPIO1(RX) · GPIO4(DE/RE)"/>
        <KV k="PCB footprint" v="MAX3485 SOT-23-8 + 2× JST-GH: +14mm width on board"/>
        <KV k="Weight per board" v="~1.5g (IC + connectors + cable)"/>
        <KV k="Protocol" v="MAVLink 2.0 (primary) · MODBUS RTU (sensor option)"/>
        <SH t="Use Cases" c={C.rs4}/>
        <Note c={C.rs4} ch="Primary use: secondary MAVLink path. If SiK 915MHz goes down or is jammed, MAVLink continues over RS-485 to a ground-connected tether station (e.g. inspection drone on a power tether). Secondary use: distributed sensor aggregation — future nacelle controller nodes report IMU data, temperature, current over RS-485 at low rates without burdening CAN FD."/>
      </div>
    </div>
  </div>);
}

// ════════════════════════════════════════════════════════════
// TAB: I²C
// ════════════════════════════════════════════════════════════
function I2CDiagram(){
  const VW=580, VH=300;
  const col=C.i2c;
  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:600,display:"block"}}>
      {/* Master board */}
      <rect x={20} y={70} width={140} height={160} rx={5} fill={`${col}07`} stroke={col} strokeWidth={1.5}/>
      <text x={90} y={88} textAnchor="middle" fill={col} fontSize={9} fontFamily={M} fontWeight="bold">TRIHAT-1</text>
      <text x={90} y={100} textAnchor="middle" fill={`${col}60`} fontSize={7} fontFamily={M}>I²C MASTER · GP14/GP15</text>
      {/* PCA9517 buffer */}
      <rect x={40} y={112} width={60} height={36} rx={3} fill={`${col}18`} stroke={col} strokeWidth={1.5}/>
      <text x={70} y={127} textAnchor="middle" fill={col} fontSize={8} fontFamily={M} fontWeight="bold">PCA9517</text>
      <text x={70} y={139} textAnchor="middle" fill={`${col}60`} fontSize={6} fontFamily={M}>Active buffer</text>
      <text x={70} y={147} textAnchor="middle" fill={`${col}50`} fontSize={6} fontFamily={M}>SOT-23-6 · 400kHz</text>
      {/* TVS diodes */}
      <rect x={112} y={116} width={24} height={28} rx={2} fill="rgba(255,230,0,0.1)" stroke={C.yellow} strokeWidth={1}/>
      <text x={124} y={127} textAnchor="middle" fill={C.yellow} fontSize={6} fontFamily={M}>TVS</text>
      <text x={124} y={135} textAnchor="middle" fill={`${C.yellow}70`} fontSize={5.5} fontFamily={M}>PRTR5V0U2X</text>
      <text x={124} y={143} textAnchor="middle" fill={`${C.yellow}60`} fontSize={5.5} fontFamily={M}>ESD + EMI</text>
      {/* Pullups */}
      <text x={90} y={108} textAnchor="middle" fill={`${col}70`} fontSize={5.5} fontFamily={M}>4.7kΩ SDA SCL pullups here only</text>
      {/* J_I2C connectors */}
      <rect x={24} y={165} width={44} height={50} rx={3} fill={`${col}12`} stroke={col} strokeWidth={1.2}/>
      <text x={46} y={180} textAnchor="middle" fill={col} fontSize={7} fontFamily={M} fontWeight="bold">J_I2C_IN</text>
      {["GND","+3V3","SDA","SCL"].map((s,i)=>(<text key={s} x={46} y={190+i*7} textAnchor="middle" fill={`${col}60`} fontSize={5.5} fontFamily={M}>{s}</text>))}
      <rect x={90} y={165} width={44} height={50} rx={3} fill={`${col}12`} stroke={col} strokeWidth={1.2}/>
      <text x={112} y={180} textAnchor="middle" fill={col} fontSize={7} fontFamily={M} fontWeight="bold">J_I2C_OUT</text>
      {["GND","+3V3","SDA","SCL"].map((s,i)=>(<text key={s} x={112} y={190+i*7} textAnchor="middle" fill={`${col}60`} fontSize={5.5} fontFamily={M}>{s}</text>))}
      {/* Local sensors already on bus */}
      <rect x={24} y={234} width={140} height={30} rx={3} fill="rgba(74,222,128,0.06)" stroke={C.green} strokeWidth={0.8}/>
      <text x={94} y={252} textAnchor="middle" fill={C.green} fontSize={7} fontFamily={M}>Existing: ICM-42688 · BMP388 · MS4525DO (I2C1)</text>

      {/* Bus wires */}
      <line x1={160} y1={174} x2={220} y2={174} stroke={col} strokeWidth={2.5}/>
      <line x1={160} y1={186} x2={220} y2={186} stroke={col} strokeWidth={2.5}/>
      <text x={190} y={165} textAnchor="middle" fill={`${col}70`} fontSize={6} fontFamily={M}>SDA</text>
      <text x={190} y={196} textAnchor="middle" fill={`${col}70`} fontSize={6} fontFamily={M}>SCL</text>

      {/* Client board (COMPHAT) */}
      <rect x={220} y={110} width={110} height={100} rx={5} fill={`${col}07`} stroke={col} strokeWidth={1.5}/>
      <text x={275} y={128} textAnchor="middle" fill={col} fontSize={9} fontFamily={M} fontWeight="bold">COMPHAT-1</text>
      <text x={275} y={140} textAnchor="middle" fill={`${col}60`} fontSize={7} fontFamily={M}>I²C CLIENT</text>
      <rect x={234} y={148} width={40} height={24} rx={2} fill={`${col}12`} stroke={col} strokeWidth={1}/>
      <text x={254} y={161} textAnchor="middle" fill={col} fontSize={6} fontFamily={M}>J_I2C_IN</text>
      <rect x={276} y={148} width={40} height={24} rx={2} fill={`${col}12`} stroke={col} strokeWidth={1}/>
      <text x={296} y={161} textAnchor="middle" fill={col} fontSize={6} fontFamily={M}>J_I2C_OUT</text>
      <text x={275} y={200} textAnchor="middle" fill={`${col}50`} fontSize={6} fontFamily={M}>PCA9517 buffer · TVS · no pullups</text>

      {/* Future device tap — GPS at nacelle */}
      <line x1={330} y1={174} x2={400} y2={174} stroke={col} strokeWidth={2} strokeDasharray="4 3" opacity={0.6}/>
      <line x1={330} y1={186} x2={400} y2={186} stroke={col} strokeWidth={2} strokeDasharray="4 3" opacity={0.6}/>
      <rect x={400} y={140} width={140} height={80} rx={4} fill="rgba(74,222,128,0.05)" stroke={`${col}40`} strokeWidth={1} strokeDasharray="5 3"/>
      <text x={470} y={162} textAnchor="middle" fill={`${col}50`} fontSize={8} fontFamily={M}>FUTURE DEVICES</text>
      {[["0x48","ADS1115 ADC (nacelle temp)"],["0x68","MPU-6050 nacelle IMU"],["0x77","BMP388 (alt. FIFO)"],["0x3C","SSD1306 OLED debug"]].map(([addr,name],i)=>(
        <text key={addr} x={410} y={172+i*14} fill={`${col}45`} fontSize={6} fontFamily={M}>{addr} — {name}</text>
      ))}
      <text x={470} y={218} textAnchor="middle" fill={`${col}35`} fontSize={6} fontFamily={M}>TCA9548 mux for address conflicts</text>

      <text x={VW/2} y={14} textAnchor="middle" fill="rgba(0,229,255,0.25)" fontSize={9} fontFamily={M} letterSpacing="0.1em">I²C SYSTEM EXPANSION BUS — PCA9517 BUFFER — EMI PROTECTED</text>
      <text x={VW/2} y={VH-8} textAnchor="middle" fill="rgba(0,229,255,0.2)" fontSize={7} fontFamily={M}>No pullups on client boards · pullups only at master (TRIHAT-1) · PCA9517 isolates bus segments</text>
    </svg>
  );
}

function I2CTab(){
  return(<div>
    <SH t="I²C System Expansion Bus (NEW Rev G)" mt={0} c={C.i2c}/>
    <div style={{border:`1px solid ${C.i2c}33`,borderRadius:4,background:"rgba(74,222,128,0.01)",padding:8,marginBottom:18}}>
      <I2CDiagram/>
    </div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="Why I²C?" mt={0} c={C.i2c}/>
        {[["Already partially implemented","BMP388 (baro), ICM-42688 (IMU), and MS4525DO (airspeed) are already on I²C1 on TRIHAT-1. The new bus simply extends this existing I²C network externally with EMI protection."],
          ["Wired-AND bus — trivially extensible","I²C is an open-drain bus. Any node can be added by connecting to SDA/SCL anywhere on the cable. No direction control pin (unlike RS-485). A TCA9548 8-channel mux handles address conflicts."],
          ["Minimal hardware per node","A future nacelle sensor node needs only: target IC + 4-pin JST-GH socket. No transceiver, no direction logic, no termination resistors. Absolute minimum hardware overhead."],
          ["EMI mitigation — the real engineering challenge","EDF motors create severe differential and common-mode noise. Mitigation: PCA9517 active buffer isolates each board segment · PRTR5V0U2X TVS clamps transients · common-mode choke (BNX002) on cable · all logic runs at 3.3V (lower than bus pullup margin)."],
          ["No master-slave firmware complexity","I²C has a proper addressing scheme built into the protocol. Each device on the bus has a unique 7-bit address. The Pico 2 as master simply reads/writes addresses. No arbitration software needed."],
        ].map(([t,d],i)=>(<div key={i} style={{marginBottom:10}}><div style={{color:C.i2c,fontFamily:M,fontSize:10,fontWeight:"bold",marginBottom:2}}>{t}</div><div style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.7}}>{d}</div></div>))}
      </div>
      <div>
        <SH t="Technical Specification" mt={0} c={C.i2c}/>
        <KV k="Standard" v="I²C · NXP UM10204 · FM+ (Fast-mode Plus)"/>
        <KV k="Speed" v="400kHz Fast-mode · 1MHz FM+ with PCA9517"/>
        <KV k="Max devices" v="127 unique 7-bit addresses · 512 with TCA9548 mux"/>
        <KV k="Buffer IC" v="PCA9517 SOT-23-6 · bidirectional · FM+ capable"/>
        <KV k="ESD protection" v="PRTR5V0U2X SOT-363 · ±8kV HBM · one per board"/>
        <KV k="Common-mode choke" v="BNX002-01 on cable · 2200Ω @ 100MHz · EDF noise rejection"/>
        <KV k="Pullups" v="4.7kΩ to +3V3 · on TRIHAT-1 only (one point only)"/>
        <KV k="Connectors" v="2× JST-GH 1.25mm 4-pin (IN and OUT)"/>
        <KV k="Pinout" v="GND · +3V3 · SDA · SCL"/>
        <KV k="Pico I²C" v="I²C1 · GP14(SDA) · GP15(SCL) [freed by Rev G nozzle change]"/>
        <KV k="CM4 I²C" v="I²C1 · GPIO2(SDA) · GPIO3(SCL)"/>
        <KV k="Cable max length" v="~4m at 400kHz with PCA9517 repeaters"/>
        <KV k="PCB footprint" v="PCA9517 + TVS + BNX002 + 2× JST-GH: +12mm width"/>
        <KV k="Weight per board" v="~1.2g (ICs + connectors)"/>
        <SH t="Future Expansion Devices" c={C.i2c}/>
        {[["0x48","ADS1115 — 4-ch 16-bit ADC (nacelle temp, current sense)"],
          ["0x68","MPU-6050 — nacelle-mounted IMU (vibration, tilt feedback)"],
          ["0x20","PCA9555 — 16-bit GPIO expander (payload actuators, indicators)"],
          ["0x3C","SSD1306 OLED — ground debug display"],
          ["0x40","INA226 — per-ESC power monitor"],
          ["0x77","Second BMP388 — redundant barometer on tail"],
        ].map(([addr,desc],i)=>(<div key={i} style={{display:"flex",gap:10,padding:"4px 0",borderBottom:"1px solid rgba(74,222,128,0.08)"}}><span style={{color:C.i2c,fontFamily:M,fontSize:9,minWidth:44,flexShrink:0}}>{addr}</span><span style={{color:C.dim,fontFamily:M,fontSize:9,lineHeight:1.5}}>{desc}</span></div>))}
        <Warn ch="I²C is not suitable for safety-critical control data. Use CAN FD for all safety-critical messages. I²C is for sensors and peripherals only — slow, non-deterministic latency, no priority arbitration."/>
      </div>
    </div>
  </div>);
}

// ════════════════════════════════════════════════════════════
// TAB: PROTOCOL COMPARISON
// ════════════════════════════════════════════════════════════
function ComparisonTab(){
  const criteria=[
    {c:"Max nodes",       eth:"Switch-limited",can:"32 (bus) · 128 spec",rs4:"32 per seg · unlimited+repeater",i2c:"127 native · 512+ with mux"},
    {c:"Physical layer",  eth:"4-pair diff",    can:"2-wire diff",rs4:"2-wire diff",i2c:"2-wire open-drain"},
    {c:"Speed",           eth:"100Mbps",        can:"4Mbps FD",  rs4:"10Mbps",     i2c:"1MHz FM+"},
    {c:"Topology",        eth:"Star/switch",    can:"Bus linear", rs4:"Bus linear", i2c:"Bus wired-AND"},
    {c:"Master/slave",    eth:"Peer",           can:"Multi-master",rs4:"Multi-master",i2c:"Master/slave"},
    {c:"Latency",         eth:"<1ms",           can:"<500µs",    rs4:"<2ms",       i2c:"<5ms"},
    {c:"EMI immunity",    eth:"Good (Mag.)",    can:"Excellent",  rs4:"Excellent",  i2c:"Fair (buffered)"},
    {c:"Cable weight/m",  eth:"~8g",            can:"~3g",        rs4:"~3g",        i2c:"~2g"},
    {c:"Transceiver IC",  eth:"W5500 (large)",  can:"MCP2562FD",  rs4:"MAX3485",    i2c:"PCA9517"},
    {c:"IC package",      eth:"LQFP-48",        can:"SOIC-8",     rs4:"SOT-23-8",   i2c:"SOT-23-6"},
    {c:"IC footprint",    eth:"already on PCB", can:"already on PCB",rs4:"3×3mm NEW",i2c:"2×2mm NEW"},
    {c:"Direction ctrl",  eth:"none",           can:"none",       rs4:"DE/RE GPIO", i2c:"none"},
    {c:"Termination",     eth:"auto-MDIX",      can:"120Ω ends",  rs4:"120Ω ends",  i2c:"pullups only"},
    {c:"Protocol stack",  eth:"TCP/UDP",        can:"DroneCAN",   rs4:"MAVLink/MB", i2c:"I²C native"},
    {c:"Extendability",   eth:"Add switch",     can:"Insert node",rs4:"Insert node", i2c:"Add device anywhere"},
  ];
  const colC={eth:C.eth,can:C.can,rs4:C.rs4,i2c:C.i2c};
  const colH={eth:"ETHERNET",can:"CAN FD",rs4:"RS-485 ★NEW",i2c:"I²C ★NEW"};
  return(<div>
    <Note c={C.accent} ch="★ NEW = added Rev G. All four buses are available on both TRIHAT-1 and COMPHAT-1. Each protocol is physically and electrically independent — simultaneous full operation on all four buses."/>
    <div style={{overflowX:"auto",marginTop:12}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <thead><tr>
          <th style={{padding:"6px 10px",borderBottom:`1px solid ${C.border}`,color:C.dim,fontWeight:"normal",fontSize:10,textAlign:"left"}}>CRITERION</th>
          {Object.entries(colH).map(([k,v])=>(<th key={k} style={{padding:"6px 10px",borderBottom:`1px solid ${colC[k]}55`,color:colC[k],fontWeight:"bold",fontSize:10,textAlign:"center",whiteSpace:"nowrap"}}>{v}</th>))}
        </tr></thead>
        <tbody>{criteria.map((row,i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.02)":"transparent"}}>
            <td style={{padding:"5px 10px",color:C.dim,fontFamily:M,fontSize:10,whiteSpace:"nowrap"}}>{row.c}</td>
            {["eth","can","rs4","i2c"].map(k=>(
              <td key={k} style={{padding:"5px 10px",color:colC[k],fontFamily:M,fontSize:10,textAlign:"center"}}>{row[k]}</td>
            ))}
          </tr>
        ))}</tbody>
      </table>
    </div>
    <SH t="Rejected Protocol Analysis"/>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["PROTOCOL","REASON REJECTED"]}/>
        <tbody>{REJECTED.map((r,i)=>(<tr key={i} style={{background:i%2===0?"rgba(248,113,113,0.02)":"transparent"}}>
          <td style={{padding:"5px 10px",color:C.red,whiteSpace:"nowrap"}}>{r.p}</td>
          <td style={{padding:"5px 10px",color:C.dim,lineHeight:1.6}}>{r.reason}</td>
        </tr>))}</tbody>
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
    <SH t="N-Node Extensibility Analysis" mt={0}/>
    <div style={{display:"flex",gap:8,marginBottom:18,flexWrap:"wrap"}}>
      {NODE_MATRIX.map(r=>(<button key={r.nodes} onClick={()=>setNodes(r.nodes)} style={{background:nodes===r.nodes?"rgba(0,229,255,0.09)":"transparent",border:`1px solid ${nodes===r.nodes?C.accent:"rgba(0,229,255,0.15)"}`,color:nodes===r.nodes?C.accent:C.dimmer,padding:"5px 14px",fontFamily:M,fontSize:10,cursor:"pointer",borderRadius:2}}>{r.nodes} Nodes — {r.label}</button>))}
    </div>
    {row&&(<div>
      <div style={{display:"grid",gridTemplateColumns:"repeat(2,1fr)",gap:16,marginBottom:20}}>
        {[["eth","ETHERNET",row.eth],["can","CAN FD",row.can],["rs4","RS-485",row.rs4],["i2c","I²C",row.i2c]].map(([k,l,v])=>(
          <div key={k} style={{padding:"12px 14px",border:`1px solid ${C[k]}44`,background:`${C[k]}07`,borderRadius:4}}>
            <div style={{color:C[k],fontFamily:M,fontSize:11,fontWeight:"bold",marginBottom:6}}>{l}</div>
            <div style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.7}}>{v}</div>
          </div>
        ))}
      </div>
    </div>)}

    <SH t="Extensibility Principles"/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        {[["CAN FD bus growth","Insert new node between any two existing nodes. Remove cable between them, replace with cable_old_in → new_node_in and new_node_out → old_node_out. Update termination (remove from previous last node, add to new last node). Zero firmware changes on existing nodes."],
          ["RS-485 bus growth","Identical process to CAN FD. Because RS-485 is half-duplex with direction control, new node must implement DE/RE on its UART TX GPIO — but this is standard in all RS-485 firmware templates. Existing nodes need no changes."],
          ["I²C device addition","Simplest of all: tap anywhere on the SDA/SCL bus. New device brings its own I²C address (selected by hardware address pins on the IC). Master node (Pico 2) adds one I2C.read() call. If address conflict: add TCA9548 mux (one mux enables 8×8=64 extra unique addresses). No changes to existing devices."],
        ].map(([t,d],i)=>(<div key={i} style={{marginBottom:14}}><div style={{color:C.accent,fontFamily:M,fontSize:11,fontWeight:"bold",marginBottom:4}}>{t}</div><div style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.7}}>{d}</div></div>))}
      </div>
      <div>
        {[["Ethernet network growth","Current P2P link (2 nodes) → add KSZ8795 5-port managed switch when 3rd node arrives (~7g, 5-port, 100Mbps, VLAN-capable). Existing nodes plug into switch unchanged. Switch enables: VLAN isolation per data class, port mirroring for debug, QoS for MAVLink priority. For >5 nodes: KSZ9896 6-port GbE."],
          ["Address space remaining","CAN FD: DroneCAN node IDs 1-127 — current usage 2. Remaining: 125. RS-485: No address scheme needed (UART framing with device ID byte in payload) — unlimited. I²C: 7-bit = 127 devices, current usage ~5, remaining: 122 standard + 512 via mux."],
          ["Weight budget for expansion","Per additional node (nacelle controller example): MAX3485 ~0.05g + PCA9517 ~0.05g + MCP2562FD ~0.1g + W5500 (if needed) ~0.5g + JST-GH connectors (8×) ~2g + cables ~3g = total ~6g per node for full 4-bus connectivity. Very light."],
        ].map(([t,d],i)=>(<div key={i} style={{marginBottom:14}}><div style={{color:C.accent,fontFamily:M,fontSize:11,fontWeight:"bold",marginBottom:4}}>{t}</div><div style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.7}}>{d}</div></div>))}
        <Good ch="All four buses are designed such that adding node N requires zero hardware or firmware changes on the existing Rev G nodes. The Serenity 2-node build is already the minimal instance of a scalable N-node architecture."/>
      </div>
    </div>

    <SH t="PCB Layout Impact Summary"/>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["BOARD","CHANGE","PCB AREA","WEIGHT DELTA","CONNECTOR DELTA"]}/>
        <tbody>{[
          ["TRIHAT-1 (65×48mm)","+ J_CAN_OUT 4-pin JST-GH · + MAX3485 SOT-23 + 2× RS-485 JST-GH · + PCA9517 SOT-23 + TVS + BNX + 2× I²C JST-GH","~400mm² (+17%)","~4g","6 → 12 JST-GH connectors"],
          ["COMPHAT-1 (65×48mm)","Same additions as TRIHAT-1","~400mm² (+17%)","~4g","4 → 10 JST-GH connectors"],
          ["CM4-CARRIER-1","No changes — RS-485 and I²C pass through GPIO header to COMPHAT","0","0","0"],
          ["Net PCB size","Both hats may need +8mm width (65→73mm) or tighter component layout","Optional","—","—"],
        ].map((r,i)=>(<tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.02)":"transparent",verticalAlign:"top"}}>
          {r.map((v,j)=>(<td key={j} style={{padding:"5px 10px",color:j===0?C.text:j===3?C.green:C.dim,fontFamily:M,fontSize:10,lineHeight:1.5}}>{v}</td>))}
        </tr>))}</tbody>
      </table>
    </div>
    <Note c={C.yellow} ch="PCB width increase to 65×56mm on TRIHAT-1 and COMPHAT-1 is the cleaner option vs tighter component placement. At 65×56mm both boards still fit within the Serenity avionics bay on existing standoffs — the bay is 68mm wide. Alternatively, the I²C components (PCA9517 + TVS + BNX002) can be placed on the B.Cu back copper layer to stay within 65×48mm with careful 4-layer routing."/>
  </div>);
}

// ════════════════════════════════════════════════════════════
// TAB: BOM DELTA
// ════════════════════════════════════════════════════════════
const BOM_DELTA=[
  // CAN second connector
  {cat:"CAN FD",qty:2,ref:"J_CAN_OUT",part:"JST-GH 1.25mm 4-pin connector (TRIHAT-1+COMPHAT-1)",pkg:"SMD",est:"$0.60ea",col:C.can,note:"Second CAN connector per board"},
  {cat:"CAN FD",qty:1,ref:"CAN-C2",  part:"4-pin JST-GH CAN FD cable 120mm (spare)",pkg:"cable",est:"$3",col:C.can,note:"Second cable for daisy-chain"},
  // RS-485
  {cat:"RS-485",qty:2,ref:"U_RS485_T",part:"MAX3485 RS-485 transceiver (TRIHAT-1)",  pkg:"SOT-23-8",est:"$0.80ea",col:C.rs4,note:"3×3mm · 3.3V · 10Mbps"},
  {cat:"RS-485",qty:2,ref:"U_RS485_C",part:"MAX3485 RS-485 transceiver (COMPHAT-1)", pkg:"SOT-23-8",est:"$0.80ea",col:C.rs4,note:"Same IC both boards"},
  {cat:"RS-485",qty:4,ref:"J_RS485",  part:"JST-GH 1.25mm 4-pin connector ×4 (2 per board)",pkg:"SMD",est:"$0.60ea",col:C.rs4,note:"IN+OUT per board"},
  {cat:"RS-485",qty:2,ref:"RS485-C",  part:"4-pin JST-GH RS-485 cable 150mm",        pkg:"cable",est:"$3ea",col:C.rs4,note:"Twisted pair A/B"},
  {cat:"RS-485",qty:4,ref:"R_BIAS",   part:"560Ω 0402 bias resistors (2 per bus end)",pkg:"0402",est:"$0.05ea",col:C.rs4,note:"Bus termination biasing"},
  {cat:"RS-485",qty:2,ref:"R_TERM",   part:"120Ω 0402 end termination (1 per bus end)",pkg:"0402",est:"$0.05ea",col:C.rs4,note:"Solder bridge JP_RS485_TERM"},
  // I2C
  {cat:"I²C",   qty:2,ref:"U_BUF_T",  part:"PCA9517 I²C buffer (TRIHAT-1)",          pkg:"SOT-23-6",est:"$0.60ea",col:C.i2c,note:"2×2mm · 400kHz/1MHz · bidirectional"},
  {cat:"I²C",   qty:2,ref:"U_BUF_C",  part:"PCA9517 I²C buffer (COMPHAT-1)",         pkg:"SOT-23-6",est:"$0.60ea",col:C.i2c,note:"Same IC both boards"},
  {cat:"I²C",   qty:2,ref:"U_TVS",    part:"PRTR5V0U2X TVS ESD diode (per board)",   pkg:"SOT-363",est:"$0.35ea",col:C.i2c,note:"±8kV HBM · dual rail · SOT-363"},
  {cat:"I²C",   qty:2,ref:"U_CMC",    part:"BNX002-01 common-mode choke (per board)", pkg:"SMD",est:"$0.80ea",col:C.i2c,note:"2200Ω @ 100MHz · EDF EMI rejection"},
  {cat:"I²C",   qty:4,ref:"J_I2C",    part:"JST-GH 1.25mm 4-pin connector ×4",       pkg:"SMD",est:"$0.60ea",col:C.i2c,note:"IN+OUT per board"},
  {cat:"I²C",   qty:2,ref:"I2C-C",    part:"4-pin JST-GH I²C cable 150mm",           pkg:"cable",est:"$3ea",col:C.i2c,note:"GND,+3V3,SDA,SCL"},
  {cat:"I²C",   qty:2,ref:"R_PU",     part:"4.7kΩ 0402 SDA+SCL pullup (TRIHAT-1 only)",pkg:"0402",est:"$0.05ea",col:C.i2c,note:"Only on master board"},
];
const BOM_CATS_D=[...new Set(BOM_DELTA.map(b=>b.cat))];
const CAT_C={CAN:C.can,"RS-485":C.rs4,"I²C":C.i2c};

function BomTab(){
  const [cf,setCf]=useState("All");
  const rows=cf==="All"?BOM_DELTA:BOM_DELTA.filter(b=>b.cat===cf);
  const total=BOM_DELTA.reduce((s,b)=>s+b.qty*(parseFloat(b.est.replace("$","").replace("ea",""))||0),0);
  return(<div>
    <div style={{display:"flex",gap:5,flexWrap:"wrap",marginBottom:12}}>
      {["All",...BOM_CATS_D].map(c=>(<button key={c} onClick={()=>setCf(c)} style={{background:cf===c?`${CAT_C[c]||C.accent}20`:"transparent",border:`1px solid ${cf===c?CAT_C[c]||C.accent:"rgba(0,229,255,0.14)"}`,color:cf===c?CAT_C[c]||C.accent:C.dimmer,padding:"3px 10px",fontFamily:M,fontSize:9,cursor:"pointer",borderRadius:2}}>{c}</button>))}
    </div>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["CAT","QTY","REF","PART","PKG","~UNIT","NOTES"]}/>
        <tbody>{rows.map((b,i)=>(<tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.02)":"transparent",verticalAlign:"top"}}>
          <td style={{padding:"5px 8px"}}><span style={{color:b.col,border:`1px solid ${b.col}40`,padding:"1px 5px",borderRadius:2,fontSize:9,whiteSpace:"nowrap"}}>{b.cat}</span></td>
          <td style={{padding:"5px 8px",color:C.accent,fontWeight:"bold",textAlign:"center"}}>{b.qty}</td>
          <td style={{padding:"5px 8px",color:C.yellow,fontSize:9,whiteSpace:"nowrap"}}>{b.ref}</td>
          <td style={{padding:"5px 8px",color:C.text}}>{b.part}</td>
          <td style={{padding:"5px 8px",color:C.dimmer,whiteSpace:"nowrap",fontSize:9}}>{b.pkg}</td>
          <td style={{padding:"5px 8px",color:C.green,fontWeight:"bold",whiteSpace:"nowrap"}}>{b.est}</td>
          <td style={{padding:"5px 8px",color:C.dim,fontSize:9}}>{b.note}</td>
        </tr>))}</tbody>
        {cf==="All"&&(<tfoot>
          <tr style={{borderTop:`1px solid ${C.border}`}}>
            <td colSpan={5} style={{padding:"8px",color:C.accent,textAlign:"right",fontSize:11}}>REV G DELTA TOTAL</td>
            <td style={{padding:"8px",color:C.yellow,fontSize:16,fontWeight:"bold"}}>~$25–30</td>
            <td/>
          </tr>
          <tr>
            <td colSpan={5} style={{padding:"6px 8px",color:C.green,textAlign:"right",fontSize:10}}>Weight delta (hardware only, exc. cable)</td>
            <td style={{padding:"6px 8px",color:C.green,fontWeight:"bold"}}>~8g</td>
            <td/>
          </tr>
        </tfoot>)}
      </table>
    </div>
    <Note c={C.dim} ch="All new ICs are in 0402 or SOT-23 packages — minimum PCB real estate. The MAX3485 and PCA9517 are commodity parts available from LCSC for JLCPCB assembly at near-zero setup cost. Resistors and capacitors at $0.05ea are standard JLCPCB basic library parts."/>
  </div>);
}

// ════════════════════════════════════════════════════════════
// APP
// ════════════════════════════════════════════════════════════
const TABS=["Overview","CAN Daisy-Chain","RS-485","I²C Bus","Comparison","Extensibility","BOM Delta"];

_ODFontLoader();
export default function App(){
  const [tab,setTab]=useState("Overview");
  return(<div style={{minHeight:"100vh",background:C.bg,color:C.text,fontFamily:M}}>
    <Grid/>
    <div style={{background:"rgba(163,230,53,0.06)",borderBottom:`1px solid ${C.lime}22`,padding:"6px 24px",fontFamily:M,fontSize:8,color:`${C.lime}70`,lineHeight:1.6}}>
      © 2026 Steve Griffing, PE(CSE) [Control Systems Engineering], CISSP-ISSEP, CPP · CC BY 4.0 · Hull: Peter Farell CC BY 4.0 · Nozzle: BamJr CC BY 4.0 · Visual inspiration: Firefly/Serenity © Joss Whedon/Mutant Enemy/Universal — Fan engineering work
    </div>
    <div style={{position:"relative",zIndex:1,borderBottom:`1px solid ${C.border}`,padding:"14px 24px 12px"}}>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",flexWrap:"wrap",gap:12}}>
        <div>
          <div style={{color:"rgba(0,229,255,0.28)",fontSize:9,letterSpacing:"0.2em",marginBottom:4}}>SERENITY TILTROTOR · CONNECTIVITY · REV G</div>
          <h1 style={{margin:0,fontSize:18,fontWeight:"normal",color:"#fff",letterSpacing:"0.07em"}}>MULTI-BUS DATA ARCHITECTURE</h1>
          <div style={{color:"rgba(0,229,255,0.45)",fontSize:10,marginTop:3}}>
            CAN FD daisy-chain (2nd connector) · RS-485 multi-drop · I²C expansion bus · Ethernet unchanged
          </div>
        </div>
        <div style={{textAlign:"right",fontFamily:M}}>
          <div style={{display:"flex",gap:8,justifyContent:"flex-end",flexWrap:"wrap",marginBottom:6}}>
            {[["ETH",C.eth,"100Mbps"],["CAN",C.can,"4Mbps FD"],["RS-485",C.rs4,"10Mbps"],["I²C",C.i2c,"1MHz"]].map(([l,c,s])=>(
              <div key={l} style={{padding:"3px 10px",border:`1px solid ${c}55`,background:`${c}12`,borderRadius:3}}>
                <span style={{color:c,fontFamily:M,fontSize:9,fontWeight:"bold"}}>{l}</span>
                <span style={{color:`${c}80`,fontFamily:M,fontSize:8,marginLeft:6}}>{s}</span>
              </div>
            ))}
          </div>
          <div style={{color:C.green,fontFamily:M,fontSize:10}}>+~$28 · +~8g · N-node extensible</div>
        </div>
      </div>
      <div style={{display:"flex",gap:2,marginTop:12,flexWrap:"wrap"}}>
        {TABS.map(t=>(<button key={t} onClick={()=>setTab(t)} style={{background:tab===t?"rgba(0,229,255,0.09)":"transparent",border:`1px solid ${tab===t?C.accent:"rgba(0,229,255,0.12)"}`,color:tab===t?C.accent:C.dimmer,padding:"4px 11px",fontFamily:M,fontSize:9,cursor:"pointer",letterSpacing:"0.06em",transition:"all 0.12s"}}>{t}</button>))}
      </div>
    </div>
    <div style={{position:"relative",zIndex:1,padding:"20px 24px",maxWidth:1060,margin:"0 auto"}}>
      {tab==="Overview"       && <OverviewTab/>}
      {tab==="CAN Daisy-Chain"&& <CANTab/>}
      {tab==="RS-485"         && <RS485Tab/>}
      {tab==="I²C Bus"        && <I2CTab/>}
      {tab==="Comparison"     && <ComparisonTab/>}
      {tab==="Extensibility"  && <ExtensibilityTab/>}
      {tab==="BOM Delta"      && <BomTab/>}
    </div>
  </div>);
}
