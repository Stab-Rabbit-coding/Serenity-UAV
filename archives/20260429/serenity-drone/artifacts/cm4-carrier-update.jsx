import { useState } from "react";

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
  bg:"#070a0f", border:"rgba(0,229,255,0.12)", accent:"#00e5ff",
  orange:"#ff6b35", yellow:"#ffe600", purple:"#c084fc", green:"#4ade80",
  red:"#f87171", pink:"#f472b6", teal:"#2dd4bf", lime:"#a3e635",
  dim:"rgba(255,255,255,0.90)", dimmer:"rgba(255,255,255,0.80)", text:"rgba(255,255,255,0.82)",
};
const M = "'OpenDyslexic Mono','OpenDyslexic','OpenDyslexicMono',monospace";

// ── primitives ────────────────────────────────────────────────────
const Tag = ({ch,c=C.accent}) => (
  <span style={{display:"inline-block",padding:"2px 8px",border:`1px solid ${c}`,color:c,
    fontSize:10,fontFamily:M,borderRadius:2,marginRight:5,marginBottom:5,opacity:.85}}>{ch}</span>
);
const SH = ({t,mt=22,c=C.accent}) => (
  <div style={{display:"flex",alignItems:"center",gap:10,marginBottom:14,marginTop:mt}}>
    <div style={{width:3,height:17,background:c,flexShrink:0}}/>
    <span style={{color:c,fontFamily:M,fontSize:13,letterSpacing:"0.13em",textTransform:"uppercase",fontWeight:"normal"}}>{t}</span>
  </div>
);
const KV = ({k,v,u="",vc=C.text,warn=false}) => (
  <div style={{display:"flex",justifyContent:"space-between",alignItems:"baseline",
    padding:"5px 0",borderBottom:"1px solid rgba(0,229,255,0.07)",
    background:warn?"rgba(255,230,0,0.04)":"transparent"}}>
    <span style={{color:C.dim,fontFamily:M,fontSize:11}}>{k}</span>
    <span style={{color:vc,fontFamily:M,fontSize:11}}>{v}{u&&<span style={{color:C.accent,marginLeft:4,fontSize:10}}>{u}</span>}</span>
  </div>
);
const Note = ({c=C.dim,ch}) => (
  <div style={{marginTop:8,marginBottom:4,color:c,fontFamily:M,fontSize:10,lineHeight:1.85,
    padding:"8px 12px",border:`1px solid ${c}22`,borderLeft:`2px solid ${c}55`,
    background:`${c}07`,borderRadius:3}}>{ch}</div>
);
const Warn = ({ch}) => (
  <div style={{marginTop:8,color:C.yellow,fontFamily:M,fontSize:10,lineHeight:1.8,
    padding:"7px 12px",border:`1px solid rgba(255,230,0,0.35)`,borderLeft:`2px solid ${C.yellow}`,
    background:"rgba(255,230,0,0.05)",borderRadius:3}}>⚠ {ch}</div>
);

// ── BG grid ───────────────────────────────────────────────────────
function Grid() {
  return (
    <svg style={{position:"fixed",inset:0,width:"100%",height:"100%",pointerEvents:"none",zIndex:0}}>
      <defs>
        <pattern id="sg" width="20" height="20" patternUnits="userSpaceOnUse">
          <path d="M20 0L0 0 0 20" fill="none" stroke="rgba(0,229,255,0.035)" strokeWidth={0.5}/>
        </pattern>
        <pattern id="lg" width="100" height="100" patternUnits="userSpaceOnUse">
          <rect width="100" height="100" fill="url(#sg)"/>
          <path d="M100 0L0 0 0 100" fill="none" stroke="rgba(0,229,255,0.07)" strokeWidth={1}/>
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#lg)"/>
    </svg>
  );
}

// ═══════════════════════════════════════════════════════════════════
// CM4 CARRIER PCB SVG
// Physical: 65 mm × 40 mm  (vs Pi Zero 65×30 — same length, +10mm width)
// Scale: 8px/mm → 520px × 320px viewBox
// ═══════════════════════════════════════════════════════════════════
function CarrierPCB({selected, onSelect}) {
  const W=560, H=360;
  const bx=20, by=20, bw=520, bh=320; // board rect

  // ── grid lines ──
  const grid=[];
  for(let x=0;x<=bw;x+=16) grid.push(<line key={"gx"+x} x1={bx+x} y1={by} x2={bx+x} y2={by+bh} stroke="rgba(0,229,255,0.04)" strokeWidth={0.5}/>);
  for(let y=0;y<=bh;y+=16) grid.push(<line key={"gy"+y} x1={bx} y1={by+y} x2={bx+bw} y2={by+y} stroke="rgba(0,229,255,0.04)" strokeWidth={0.5}/>);

  // ── components ──
  const comps = [
    // CM4 module footprint (55×40mm → 440×320px but scaled to fit) centred
    // On real board: CM4 sits on underside via DF40 connectors
    // We show it as a ghost overlay on top view
    {id:"CM4", ref:"CM4 Lite 4GB WiFi", note:"55×40mm module (underside)",
      x:bx+40, y:by+40, w:420, h:220, fill:"rgba(74,222,128,0.03)", stroke:"rgba(74,222,128,0.2)",
      dash:"6 3", tx:bx+250, ty:by+145, fc:C.green, fs:10, ghost:true},
    // DF40 connectors (shown as strips on underside but visible in top view as pads)
    {id:"CN1", ref:"DF40C-100 A", note:"CM4 connector A (underside)",
      x:bx+44, y:by+58, w:188, h:14, fill:"rgba(74,222,128,0.07)", stroke:C.green,
      dash:"", tx:bx+138, ty:by+67, fc:C.green, fs:7},
    {id:"CN2", ref:"DF40C-100 B", note:"CM4 connector B (underside)",
      x:bx+44, y:by+248, w:188, h:14, fill:"rgba(74,222,128,0.07)", stroke:C.green,
      dash:"", tx:bx+138, ty:by+257, fc:C.green, fs:7},
    // microSD (OS) — left end
    {id:"SD1", ref:"μSD — CM4 OS", note:"CM4 OS card · SDIO0",
      x:bx+252, y:by+56, w:60, h:44, fill:"rgba(163,230,53,0.08)", stroke:C.lime,
      dash:"", tx:bx+282, ty:by+75, fc:C.lime, fs:8},
    // USB 2.0 via GL850G hub chip
    {id:"U1", ref:"GL850G USB hub", note:"USB2 hub · 4-port · for debug + RCRS",
      x:bx+330, y:by+58, w:70, h:48, fill:"rgba(0,229,255,0.07)", stroke:C.accent,
      dash:"", tx:bx+365, ty:by+79, fc:C.accent, fs:7},
    // USB-C power + debug
    {id:"J_USBC", ref:"USB-C · pwr+OTG", note:"5V power in + USB OTG debug",
      x:bx+414, y:by+60, w:44, h:30, fill:"rgba(255,230,0,0.08)", stroke:C.yellow,
      dash:"", tx:bx+436, ty:by+77, fc:C.yellow, fs:7},
    // PCB WiFi antenna (trace antenna, far from GPIO connector)
    {id:"ANT_WIFI", ref:"PCB WiFi antenna", note:"2.4/5GHz trace antenna · CM4 onboard radio",
      x:bx+445, y:by+160, w:56, h:90, fill:"rgba(0,229,255,0.03)", stroke:"rgba(0,229,255,0.3)",
      dash:"3 2", tx:bx+473, ty:by+207, fc:"rgba(0,229,255,0.5)", fs:7},
    // 40-pin GPIO header (top edge, same position as Pi Zero)
    {id:"HDR40", ref:"40-pin GPIO hdr", note:"2.54mm · to COMMS-HAT-1 · same footprint as Pi Zero",
      x:bx+44, y:by+284, w:376, h:22, fill:"rgba(255,107,53,0.08)", stroke:C.orange,
      dash:"", tx:bx+232, ty:by+297, fc:C.orange, fs:8},
    // AP2112K 3.3V LDO
    {id:"U2", ref:"AP2112K-3.3", note:"3.3V LDO · 600mA for 3.3V carrier peripherals",
      x:bx+330, y:by+120, w:50, h:32, fill:"rgba(255,230,0,0.06)", stroke:C.yellow,
      dash:"", tx:bx+355, ty:by+138, fc:C.yellow, fs:7},
    // Reset + boot buttons
    {id:"SW1", ref:"BOOT + nRST", note:"Boot-select and hard reset buttons",
      x:bx+252, y:by+112, w:64, h:26, fill:"rgba(255,255,255,0.04)", stroke:C.dimmer,
      dash:"", tx:bx+284, ty:by+127, fc:C.dimmer, fs:7},
    // Status LED
    {id:"LED1", ref:"Status LED", note:"GPIO 47 · green · heartbeat / OS ready",
      x:bx+338, y:by+164, w:24, h:24, fill:"rgba(74,222,128,0.1)", stroke:C.green,
      dash:"", tx:bx+350, ty:by+178, fc:C.green, fs:6},
    // Power JST-GH (alt to USB-C)
    {id:"J_PWR", ref:"J1 PWR 4-pin JST-GH", note:"5V · GND×2 · GND · alt power input",
      x:bx+414, y:by+104, w:54, h:18, fill:"rgba(255,230,0,0.08)", stroke:C.yellow,
      dash:"", tx:bx+441, ty:by+115, fc:C.yellow, fs:7},
  ];

  const highlights = {
    CM4:"rgba(74,222,128,0.18)",CN1:"rgba(74,222,128,0.2)",CN2:"rgba(74,222,128,0.2)",
    SD1:"rgba(163,230,53,0.2)",U1:"rgba(0,229,255,0.15)",J_USBC:"rgba(255,230,0,0.18)",
    ANT_WIFI:"rgba(0,229,255,0.1)",HDR40:"rgba(255,107,53,0.18)",
    U2:"rgba(255,230,0,0.15)",SW1:"rgba(255,255,255,0.1)",LED1:"rgba(74,222,128,0.2)",J_PWR:"rgba(255,230,0,0.18)",
  };

  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* Board body */}
      <rect x={bx} y={by} width={bw} height={bh} rx={8}
        fill="rgba(5,25,20,0.7)" stroke={C.green} strokeWidth={1.5}/>
      {/* Grid */}
      <g clipPath="url(#cc)">{grid}</g>
      <defs>
        <clipPath id="cc"><rect x={bx} y={by} width={bw} height={bh} rx={8}/></clipPath>
        <clipPath id="cc2"><rect x={bx} y={by} width={bw} height={bh} rx={8}/></clipPath>
      </defs>
      {/* Copper fill hint */}
      <rect x={bx} y={by} width={bw} height={bh} rx={7}
        fill="none" stroke="rgba(74,222,128,0.05)" strokeWidth={3}/>

      {/* Mounting holes - Pi Zero compatible spacing */}
      {[[bx+24,by+24],[bx+24,by+bh-24],[bx+bw-24,by+24],[bx+bw-24,by+bh-24]].map(([cx,cy],i)=>(
        <g key={i}>
          <circle cx={cx} cy={cy} r={8} fill="#070a0f" stroke={C.green} strokeWidth={1} opacity={0.5}/>
          <circle cx={cx} cy={cy} r={3.5} fill="none" stroke={C.green} strokeWidth={0.6} opacity={0.35}/>
        </g>
      ))}

      {/* GPIO header pin dots */}
      {Array.from({length:20},(_,i)=>(
        <g key={"pa"+i}>
          <circle cx={bx+50+i*19} cy={by+288} r={3} fill="rgba(255,107,53,0.4)" stroke={C.orange} strokeWidth={0.7}/>
          <circle cx={bx+50+i*19} cy={by+300} r={3} fill="rgba(255,107,53,0.4)" stroke={C.orange} strokeWidth={0.7}/>
        </g>
      ))}

      {/* DF40 pad rows */}
      {Array.from({length:25},(_,i)=>(
        <rect key={"da"+i} x={bx+48+i*7} y={by+59} width={4} height={12}
          fill="rgba(74,222,128,0.25)" stroke="none" rx={0.5}/>
      ))}
      {Array.from({length:25},(_,i)=>(
        <rect key={"db"+i} x={bx+48+i*7} y={by+249} width={4} height={12}
          fill="rgba(74,222,128,0.25)" stroke="none" rx={0.5}/>
      ))}

      {/* μSD card slot teeth */}
      {Array.from({length:9},(_,i)=>(
        <rect key={"sd"+i} x={bx+256+i*7} y={by+57} width={4} height={8}
          fill="rgba(163,230,53,0.3)" stroke="none" rx={0.5}/>
      ))}

      {/* WiFi antenna trace squiggle */}
      <path d={`M${bx+446},${by+165} Q${bx+480},${by+175} ${bx+496},${by+185} Q${bx+510},${by+200} ${bx+496},${by+215} Q${bx+480},${by+225} ${bx+470},${by+240}`}
        fill="none" stroke="rgba(0,229,255,0.35)" strokeWidth={2} strokeLinecap="round"/>

      {/* USB-C pins */}
      {Array.from({length:6},(_,i)=>(
        <rect key={"uc"+i} x={bx+417+i*7} y={by+61} width={4} height={10}
          fill="rgba(255,230,0,0.3)" stroke="none" rx={0.5}/>
      ))}

      {/* Components */}
      {comps.map(c => {
        const sel = selected===c.id;
        return (
          <g key={c.id} onClick={()=>onSelect(sel?null:c.id)} style={{cursor:"pointer"}}>
            <rect x={c.x} y={c.y} width={c.w} height={c.h} rx={3}
              fill={sel?highlights[c.id]||`${c.stroke}18`:c.fill}
              stroke={c.stroke} strokeWidth={sel?2:1.1}
              strokeDasharray={c.dash||""}/>
            <text x={c.tx} y={c.ty} textAnchor="middle" fill={c.fc}
              fontSize={c.fs} fontFamily={M} fontWeight="bold">{c.ref}</text>
          </g>
        );
      })}

      {/* Labels */}
      <text x={W/2} y={14} textAnchor="middle" fill="rgba(74,222,128,0.25)"
        fontSize={9} fontFamily={M} letterSpacing="0.12em">CM4-CARRIER-1 · REV A · 65mm × 40mm · 4-LAYER</text>
      <text x={W/2} y={by+bh+14} textAnchor="middle" fill="rgba(74,222,128,0.18)"
        fontSize={8} fontFamily={M}>ENIG · M2.5 HOLES · Pi ZERO–LENGTH COMPATIBLE · CM4 MODULE UNDERSIDE</text>

      {/* Dimension callouts */}
      <line x1={bx} y1={by+bh+26} x2={bx+bw} y2={by+bh+26} stroke={C.accent} strokeWidth={0.5} opacity={0.25}/>
      <line x1={bx} y1={by+bh+23} x2={bx} y2={by+bh+29} stroke={C.accent} strokeWidth={0.5} opacity={0.25}/>
      <line x1={bx+bw} y1={by+bh+23} x2={bx+bw} y2={by+bh+29} stroke={C.accent} strokeWidth={0.5} opacity={0.25}/>
      <text x={bx+bw/2} y={by+bh+38} textAnchor="middle" fill={C.dimmer} fontSize={7} fontFamily={M}>65mm</text>
    </svg>
  );
}

// ── CM4 Carrier detail panel ──────────────────────────────────────
const CARRIER_DETAIL = {
  CM4:{ title:"CM4 Lite 4GB WiFi — module",c:C.green,rows:[
    ["Module","Raspberry Pi Compute Module 4"],["Variant","CM4 Lite — no eMMC, uses SD1 on carrier"],
    ["RAM","4GB LPDDR4X @ 3200 MT/s"],["CPU","BCM2711 · 4× Cortex-A72 @ 1.5GHz"],
    ["GPU","VideoCore VI · OpenGL ES 3.1 · H.265 decode"],
    ["WiFi","802.11b/g/n/ac 2.4+5GHz · Bluetooth 5.0"],
    ["Size","55mm × 40mm × 4.7mm"],["Weight","~7.5g"],
    ["Interface","2× Hirose DF40C-100 (CN1 + CN2 on carrier"],
    ["OS","Raspberry Pi OS Lite (headless) from SD1"],
  ]},
  CN1:{ title:"DF40C-100 Connector A",c:C.green,rows:[
    ["Part","Hirose DF40C-100DS-0.4V(51)"],["Pitch","0.4mm"],
    ["Signals","USB · PCIe · CSI · DSI · power · GPIO 0-27"],
    ["Mating height","1.5mm (low-profile)"],["Underside","Yes — CM4 mounts below carrier"],
  ]},
  CN2:{ title:"DF40C-100 Connector B",c:C.green,rows:[
    ["Part","Hirose DF40C-100DS-0.4V(51)"],["Pitch","0.4mm"],
    ["Signals","GPIO 28-45 · additional power · HDMI · eMMC/SDIO"],
    ["Mating height","1.5mm"],["Underside","Yes"],
  ]},
  SD1:{ title:"μSD — CM4 OS (SDIO0)",c:C.lime,rows:[
    ["Purpose","CM4 operating system boot card"],["Interface","SDIO0 from CM4 via CN2"],
    ["Recommended","≥32GB A2 UHS-I (U3) card"],["Separate from","COMMS-HAT-1 log μSD (SDIO1/SPI)"],
    ["Format","ext4 root + FAT32 boot"],["Note","CM4 Lite has no onboard eMMC — requires this SD"],
  ]},
  U1:{ title:"GL850G USB 2.0 Hub",c:C.accent,rows:[
    ["Purpose","Expands CM4 USB2 to 4 downstream ports"],
    ["Upstream","CM4 USB 2.0 (480Mbps)"],["Downstream ports","J_USBC OTG, internal 49MHz RCRS USB, debug TTY, spare"],
    ["VDD","3.3V from AP2112K"],["Package","QFN-28"],
  ]},
  J_USBC:{ title:"USB-C — Power + OTG",c:C.yellow,rows:[
    ["Power","5V input @ up to 3A (charges via carrier to VSYS)"],["OTG","USB 2.0 FS/HS for host/device debug"],
    ["Alt","Secondary to J_PWR JST-GH power in"],
    ["Note","Not a fast-charge port — use 5V/3A supply only"],
  ]},
  ANT_WIFI:{ title:"PCB WiFi/BT Trace Antenna",c:C.accent,rows:[
    ["Type","Meandered monopole trace, 2.4GHz λ/4 tuned"],["Band","2.4GHz + 5GHz (dual-band with matching network)"],
    ["Gain","~2 dBi (board edge, ground clearance required)"],
    ["Keepout","15mm ground-plane clearance on both sides of antenna"],
    ["BT","Shares antenna via CM4 internal switch"],
    ["Note","Place at far end of board from metallic payload bay"],
  ]},
  HDR40:{ title:"40-pin GPIO Header — to COMMS-HAT-1",c:C.orange,rows:[
    ["Type","2×20 2.54mm male header, tall (11mm) for clearance"],
    ["Pinout","Identical to Pi Zero / Pi 4 GPIO"],
    ["Carries","3.3V · 5V · GND · UART0 · SPI0 · SPI1 · I2C · GPIO"],
    ["Stacks","COMMS-HAT-1 sits directly on top of this header"],
    ["CM4 note","All GPIO functions routed through DF40 connectors → header"],
  ]},
  U2:{ title:"AP2112K-3.3 LDO",c:C.yellow,rows:[
    ["Output","3.3V · 600mA"],["Input","5V VSYS"],["Powers","GL850G · μSD pull-ups · LED · buttons"],
    ["CM4 own 3.3V","CM4 module has internal regulators — does NOT use this LDO"],
    ["COMMS-HAT 3.3V","Supplied by COMMS-HAT-1's own AP2112K LDO"],
  ]},
  SW1:{ title:"BOOT + nRST Buttons",c:C.dimmer,rows:[
    ["BOOT","Pulls CM4 nBOOT_EN low → USB mass-storage boot mode"],
    ["nRST","Active-low hardware reset of CM4"],["Access","Recessed, tool-required (avoid accidental in-flight press)"],
  ]},
  LED1:{ title:"Status LED",c:C.green,rows:[
    ["GPIO","CM4 GPIO 47 (onboard LED net)"],["Color","Green"],
    ["Patterns","Heartbeat = OS running · Fast blink = disk activity · OFF = fault"],
  ]},
  J_PWR:{ title:"J1 — PWR 4-pin JST-GH",c:C.yellow,rows:[
    ["Pin 1","GND"],["Pin 2","GND"],["Pin 3","+5V"],["Pin 4","+5V"],
    ["Rating","3A continuous"],["TVS","SMAJ5.0A on +5V rail"],
    ["Note","Primary power when USB-C is unavailable (drone flight)"],
  ]},
};

function CarrierDetailPanel({id}) {
  if(!id||!CARRIER_DETAIL[id]) return (
    <div style={{padding:"18px 14px",color:C.dimmer,fontFamily:M,fontSize:11,
      border:`1px solid ${C.border}`,borderRadius:4,minHeight:120}}>
      ← click a component to inspect
    </div>
  );
  const d=CARRIER_DETAIL[id];
  return (
    <div style={{padding:"14px",border:`1px solid ${d.c}44`,borderRadius:4,
      background:`${d.c}07`,overflow:"auto"}}>
      <div style={{color:d.c,fontFamily:M,fontSize:12,fontWeight:"bold",
        letterSpacing:"0.06em",marginBottom:10}}>{d.title}</div>
      {d.rows.map(([k,v],i)=>(
        <div key={i} style={{display:"flex",gap:8,padding:"4px 0",
          borderBottom:"1px solid rgba(255,255,255,0.05)",alignItems:"flex-start"}}>
          <span style={{color:C.dim,fontFamily:M,fontSize:10,minWidth:80,flexShrink:0}}>{k}</span>
          <span style={{color:C.text,fontFamily:M,fontSize:10,lineHeight:1.6}}>{v}</span>
        </div>
      ))}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// STACK DIAGRAM
// ═══════════════════════════════════════════════════════════════════
function StackDiagram() {
  const layers = [
    {label:"COMMS-HAT-1", sub:"CAN FD · ETH · TPM · μSD(log) · SiK · RCRS", h:54, c:C.orange, detail:"65×48mm · 4-layer · 20g"},
    {label:"40-pin GPIO header (11mm tall)", sub:"Pi-standard · all GPIO routed through", h:30, c:C.dim, detail:"standoffs+header 4g"},
    {label:"CM4-CARRIER-1", sub:"GL850G · μSD(OS) · WiFi ant · USB-C · power", h:54, c:C.green, detail:"65×40mm · 4-layer · 14g"},
    {label:"CM4 Lite 4GB WiFi", sub:"BCM2711 · 4×A72 · 4GB LPDDR4X · 802.11ac", h:40, c:C.green, detail:"55×40mm · 7.5g (underside of carrier)"},
  ];
  const totalH = layers.reduce((s,l)=>s+l.h+6,0)+20;
  let y = 10;
  return (
    <svg viewBox={`0 0 480 ${totalH}`} width="100%" style={{maxWidth:520,display:"block"}}>
      {layers.map((l,i)=>{
        const ly=y; y+=l.h+6;
        const indent = l.label.includes("header") ? 40 : l.label.includes("CM4 Lite") ? 20 : 0;
        return (
          <g key={i}>
            <rect x={30+indent} y={ly} width={420-indent*2} height={l.h} rx={4}
              fill={`${l.c}0d`} stroke={l.c} strokeWidth={l.label.includes("header")?1:1.5}
              strokeDasharray={l.label.includes("CM4 Lite")?"5 3":""}/>
            <text x={240} y={ly+l.h/2-6} textAnchor="middle" fill={l.c}
              fontSize={11} fontFamily={M} fontWeight="bold">{l.label}</text>
            <text x={240} y={ly+l.h/2+8} textAnchor="middle" fill={`${l.c}80`}
              fontSize={8} fontFamily={M}>{l.sub}</text>
            <text x={460} y={ly+l.h/2+4} textAnchor="end" fill={`${l.c}55`}
              fontSize={8} fontFamily={M}>{l.detail}</text>
          </g>
        );
      })}
      {/* Height callout */}
      <line x1={16} y1={10} x2={16} y2={totalH-10} stroke={C.accent} strokeWidth={0.6} opacity={0.3}/>
      <line x1={12} y1={10} x2={20} y2={10} stroke={C.accent} strokeWidth={0.6} opacity={0.3}/>
      <line x1={12} y1={totalH-10} x2={20} y2={totalH-10} stroke={C.accent} strokeWidth={0.6} opacity={0.3}/>
      <text x={8} y={totalH/2} textAnchor="middle" fill={C.dimmer} fontSize={8} fontFamily={M}
        transform={`rotate(-90 8 ${totalH/2})`}>~22mm stack</text>
    </svg>
  );
}

// ═══════════════════════════════════════════════════════════════════
// WEIGHT & BALANCE
// ═══════════════════════════════════════════════════════════════════
const WEIGHT_DATA = [
  {label:"Propulsion",c:C.orange, items:[
    {n:"2× 60mm EDF + BLDC motors",w:80},{n:"2× ESC 30A BLHeli32",w:28},
    {n:"2× nacelle tilt servos MG90S",w:18},{n:"30mm fwd fan + motor",w:18},{n:"Fwd ESC 20A",w:8},
  ]},
  {label:"Airframe",c:C.accent, items:[
    {n:"CF tube spars + 2mm CF plate",w:55},{n:"3D-printed shell + payload bay",w:35},{n:"CF skid landing gear",w:10},
  ]},
  {label:"Flight control — Pico 2",c:C.teal, items:[
    {n:"Raspberry Pi Pico 2",w:3},{n:"TRIHAT-1 sensor hat",w:15},{n:"MS4525DO airspeed + pitot",w:10},
  ]},
  {label:"Companion — CM4 stack",c:C.green, items:[
    {n:"CM4 Lite 4GB WiFi module",w:8},{n:"CM4-CARRIER-1 PCB",w:14},
    {n:"COMMS-HAT-1 PCB + ICs",w:20},{n:"SiK 915MHz air module",w:14},{n:"49MHz RCRS module",w:16},
  ]},
  {label:"Payload system",c:C.pink, items:[
    {n:"Payload release servo SG90",w:9},{n:"N20 winch motor + gearbox",w:14},
    {n:"Winch spool + 5m Dyneema",w:7},{n:"DRV8833 H-bridge PCB",w:4},
  ]},
  {label:"Power & wiring",c:C.yellow, items:[
    {n:"5S 2200mAh 75C LiPo",w:220},{n:"JST-GH harness + wiring",w:30},{n:"5V 3A switching BEC",w:8},
  ]},
];

const TOTAL_WEIGHT = WEIGHT_DATA.reduce((s,g)=>s+g.items.reduce((ss,i)=>ss+i.w,0),0);
// = 80+28+18+18+8 + 55+35+10 + 3+15+10 + 8+14+20+14+16 + 9+14+7+4 + 220+30+8
// = 152 + 100 + 28 + 72 + 34 + 258 = 644g

const MAX_THRUST = 1300; // 2× 60mm EDF at 5S ~ 650g each
const TW = (MAX_THRUST/TOTAL_WEIGHT).toFixed(2);
const HOVER_THR = Math.round((TOTAL_WEIGHT/MAX_THRUST)*100);

function WeightTab() {
  const groups = WEIGHT_DATA.map(g=>({...g,total:g.items.reduce((s,i)=>s+i.w,0)}));
  const maxG = Math.max(...groups.map(g=>g.total));
  return (
    <div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:16,marginBottom:24}}>
        {[
          {label:"Total AUW",val:`${TOTAL_WEIGHT}g`,sub:"All-up weight",c:C.yellow},
          {label:"Max Thrust",val:`${MAX_THRUST}g`,sub:"2× 60mm EDF @ 5S full throttle",c:C.orange},
          {label:"Thrust / Weight",val:`${TW} : 1`,sub:"Min recommended 1.8 for VTOL",c:TOTAL_WEIGHT/MAX_THRUST<0.56?C.green:C.red},
          {label:"Hover Throttle",val:`~${HOVER_THR}%`,sub:"Of max throttle · comfortable margin",c:C.green},
        ].map((s,i)=>(
          <div key={i} style={{padding:"12px 14px",border:`1px solid ${s.c}44`,
            background:`${s.c}08`,borderRadius:4}}>
            <div style={{color:C.dim,fontFamily:M,fontSize:9,letterSpacing:"0.1em",marginBottom:4}}>{s.label}</div>
            <div style={{color:s.c,fontFamily:M,fontSize:20,fontWeight:"bold"}}>{s.val}</div>
            <div style={{color:C.dimmer,fontFamily:M,fontSize:9,marginTop:3}}>{s.sub}</div>
          </div>
        ))}
      </div>

      <SH t="Mass Breakdown" mt={0}/>
      {groups.map((g,gi)=>(
        <div key={gi} style={{marginBottom:14}}>
          <div style={{display:"flex",justifyContent:"space-between",marginBottom:3}}>
            <span style={{color:g.c,fontFamily:M,fontSize:11,fontWeight:"bold"}}>{g.label}</span>
            <span style={{color:g.c,fontFamily:M,fontSize:11}}>{g.total}g
              <span style={{color:C.dimmer,fontSize:9,marginLeft:6}}>
                ({Math.round(g.total/TOTAL_WEIGHT*100)}%)
              </span>
            </span>
          </div>
          <div style={{background:"rgba(255,255,255,0.05)",borderRadius:2,height:10,marginBottom:5,overflow:"hidden"}}>
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
        <span style={{color:C.accent,fontFamily:M,fontSize:13,fontWeight:"bold"}}>TOTAL AUW</span>
        <span style={{color:C.yellow,fontFamily:M,fontSize:24,fontWeight:"bold"}}>{TOTAL_WEIGHT} g</span>
      </div>

      <SH t="Centre of Gravity Analysis"/>
      {/* CG diagram */}
      <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:12,marginBottom:16}}>
        <CgSvg/>
      </div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:12}}>
        <div>
          <KV k="Wing-spar pivot (neutral point)" v="160mm" u="from nose"/>
          <KV k="Target CG (5% MAC ahead of NP)" v="152mm" u="from nose" vc={C.green}/>
          <KV k="Battery slide to trim" v="+18mm aft" u="(battery on rail)" vc={C.yellow} warn/>
          <KV k="Companion stack CG contribution" v="~+3mm aft vs Zero 2W" vc={C.dim}/>
        </div>
        <div>
          <KV k="Payload-empty CG" v="148mm" u="from nose" vc={C.green}/>
          <KV k="Payload-full CG shift" v="−6mm fwd" u="(200g belly payload)" vc={C.yellow}/>
          <KV k="CG range with fuel burn" v="±8mm" u="(tail-heavy as LiPo depletes)"/>
          <KV k="Recommended battery position" v="175–195mm" u="from nose centroid"/>
        </div>
      </div>
      <Warn ch="The CM4 stack (+12g and +~5mm aft vs Pi Zero 2W) shifts CG slightly rearward. Slide the battery ~18mm aft of the v1 position on the longitudinal rail to restore CG to 152mm. Add a 10g nose ballast slug if battery rail travel is insufficient."/>
    </div>
  );
}

function CgSvg() {
  const sc=1.4, ox=55, W=580, H=160;
  const mm=x=>ox+x*sc;
  const NP=160, CG=152, BATT=185;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* Fuselage */}
      <ellipse cx={mm(160)} cy={78} rx={224} ry={20}
        fill="rgba(0,229,255,0.05)" stroke={C.accent} strokeWidth={1.2}/>
      {/* Wing */}
      <rect x={mm(130)} y={71} width={mm(30)-mm(0)+2} height={14} rx={3}
        fill="rgba(0,229,255,0.04)" stroke={C.accent} strokeWidth={1}/>
      {/* Payload bay */}
      <rect x={mm(130)} y={98} width={mm(60)-mm(0)} height={22} rx={3}
        fill="rgba(244,114,182,0.08)" stroke={C.pink} strokeWidth={1} strokeDasharray="3 2"/>
      <text x={mm(160)} y={113} textAnchor="middle" fill={C.pink} fontSize={7} fontFamily={M}>PAYLOAD BAY</text>
      {/* CM4 stack position */}
      <rect x={mm(185)} y={60} width={mm(60)-mm(0)} height={20} rx={2}
        fill="rgba(74,222,128,0.08)" stroke={C.green} strokeWidth={1} strokeDasharray="2 2"/>
      <text x={mm(215)} y={73} textAnchor="middle" fill={C.green} fontSize={6} fontFamily={M}>CM4 STACK</text>
      {/* Pitot */}
      <line x1={mm(0)} y1={78} x2={mm(-14)} y2={78} stroke={C.teal} strokeWidth={2}/>
      <text x={mm(-14)} y={70} textAnchor="middle" fill={C.teal} fontSize={7} fontFamily={M}>PITOT</text>
      {/* Wing nacelles */}
      {[mm(-12),mm(332)].map((cx,i)=>(
        <ellipse key={i} cx={cx} cy={78} rx={14} ry={14}
          fill="rgba(255,107,53,0.08)" stroke={C.orange} strokeWidth={1} strokeDasharray="2 2"/>
      ))}
      {/* NP line */}
      <line x1={mm(NP)} y1={46} x2={mm(NP)} y2={130} stroke={C.orange} strokeWidth={1} strokeDasharray="4 2" opacity={0.7}/>
      <text x={mm(NP)} y={41} textAnchor="middle" fill={C.orange} fontSize={8} fontFamily={M}>NP/{NP}mm</text>
      {/* Battery zone */}
      <rect x={mm(BATT)-16} y={55} width={32} height={16} rx={2}
        fill="rgba(255,230,0,0.1)" stroke={C.yellow} strokeWidth={1}/>
      <text x={mm(BATT)} y={67} textAnchor="middle" fill={C.yellow} fontSize={6} fontFamily={M}>BATT</text>
      <text x={mm(BATT)} y={49} textAnchor="middle" fill={C.yellow} fontSize={7} fontFamily={M}>{BATT}mm</text>
      {/* CG triangle */}
      <polygon points={`${mm(CG)},50 ${mm(CG)-10},128 ${mm(CG)+10},128`}
        fill={C.green} opacity={0.9}/>
      <text x={mm(CG)} y={43} textAnchor="middle" fill={C.green} fontSize={9} fontFamily={M} fontWeight="bold">CG</text>
      <text x={mm(CG)} y={140} textAnchor="middle" fill={C.green} fontSize={8} fontFamily={M}>{CG}mm</text>
      {/* Dim line */}
      <line x1={mm(0)} y1={150} x2={mm(320)} y2={150} stroke={C.accent} strokeWidth={0.4} opacity={0.25}/>
      <text x={mm(160)} y={158} textAnchor="middle" fill={C.dimmer} fontSize={7} fontFamily={M}>Fuselage 320mm</text>
      <text x={mm(-2)} y={82} fill={C.dimmer} fontSize={7} fontFamily={M} textAnchor="end">NOSE</text>
      <text x={mm(322)} y={82} fill={C.dimmer} fontSize={7} fontFamily={M}>TAIL</text>
    </svg>
  );
}

// ═══════════════════════════════════════════════════════════════════
// POWER BUDGET
// ═══════════════════════════════════════════════════════════════════
// Battery: 5S 2200mAh · 18.5V nom
const BAT_V = 18.5, BAT_CAP = 2.2; // Ah

function toPbat(a,v){ return a*v/BAT_V; }

const HOVER_LOADS = [
  {n:"2× 60mm EDF @ 50% hover throttle",a:20.0,v:BAT_V,c:C.orange},
  {n:"30mm fwd fan — hover trim idle",a:0.4,v:BAT_V,c:C.orange},
  {n:"CM4 Lite 4GB (active flight app)",a:0.85,v:5,c:C.green},
  {n:"GL850G USB hub",a:0.10,v:3.3,c:C.green},
  {n:"COMMS-HAT-1 + sensors",a:0.22,v:3.3,c:C.purple},
  {n:"Pico 2 + TRIHAT-1",a:0.14,v:3.3,c:C.teal},
  {n:"SiK 915MHz (TX burst avg)",a:0.27,v:5,c:C.accent},
  {n:"49MHz RCRS transceiver (RX)",a:0.10,v:5,c:C.pink},
  {n:"2× nacelle servos",a:0.16,v:5,c:C.dim},
  {n:"Airspeed MS4525DO",a:0.01,v:3.3,c:C.dim},
];

const CRUISE_LOADS = [
  {n:"30mm fwd fan — cruise full",a:8.0,v:BAT_V,c:C.yellow},
  {n:"2× 60mm EDF @ 15% trim thrust",a:3.0,v:BAT_V,c:C.orange},
  {n:"CM4 Lite 4GB (active)",a:0.85,v:5,c:C.green},
  {n:"GL850G USB hub",a:0.10,v:3.3,c:C.green},
  {n:"COMMS-HAT-1 + sensors",a:0.22,v:3.3,c:C.purple},
  {n:"Pico 2 + TRIHAT-1",a:0.14,v:3.3,c:C.teal},
  {n:"SiK 915MHz (TX)",a:0.27,v:5,c:C.accent},
  {n:"49MHz RCRS (RX)",a:0.10,v:5,c:C.pink},
  {n:"Servos (nacelles at 0°)",a:0.06,v:5,c:C.dim},
];

function powerSum(loads){ return loads.reduce((s,r)=>s+toPbat(r.a,r.v),0); }

function PowerBars({loads}){
  const total=powerSum(loads);
  const maxA=Math.max(...loads.map(r=>toPbat(r.a,r.v)));
  return (
    <div>
      {loads.map((r,i)=>{
        const bA=toPbat(r.a,r.v);
        return (
          <div key={i} style={{marginBottom:7}}>
            <div style={{display:"flex",justifyContent:"space-between",marginBottom:2}}>
              <span style={{color:r.c,fontFamily:M,fontSize:10}}>{r.n}</span>
              <span style={{color:r.c,fontFamily:M,fontSize:10}}>
                {(r.a*r.v).toFixed(1)}W · {bA.toFixed(2)}A@18.5V
              </span>
            </div>
            <div style={{background:"rgba(255,255,255,0.05)",borderRadius:2,height:6}}>
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
  const hTot=powerSum(HOVER_LOADS), cTot=powerSum(CRUISE_LOADS);
  const hMin=((BAT_CAP*0.8)/hTot*60).toFixed(1);  // 80% usable
  const cMin=((BAT_CAP*0.8)/cTot*60).toFixed(1);
  const h3Min=((3.0*0.8)/hTot*60).toFixed(1);
  const c3Min=((3.0*0.8)/cTot*60).toFixed(1);

  return (
    <div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
        <div>
          <SH t="Hover" mt={0} c={C.orange}/>
          <PowerBars loads={HOVER_LOADS}/>
          <div style={{marginTop:12,padding:"10px 12px",background:"rgba(74,222,128,0.07)",
            border:`1px solid ${C.green}44`,borderRadius:4}}>
            <div style={{color:C.green,fontFamily:M,fontSize:10,marginBottom:4}}>
              5S 2200mAh (80% usable)
            </div>
            <span style={{color:C.yellow,fontFamily:M,fontSize:18,fontWeight:"bold"}}>{hMin} min</span>
            <div style={{color:C.dimmer,fontFamily:M,fontSize:9,marginTop:4}}>
              5S 3000mAh → {h3Min} min hover
            </div>
          </div>
        </div>
        <div>
          <SH t="Cruise" mt={0} c={C.yellow}/>
          <PowerBars loads={CRUISE_LOADS}/>
          <div style={{marginTop:12,padding:"10px 12px",background:"rgba(74,222,128,0.07)",
            border:`1px solid ${C.green}44`,borderRadius:4}}>
            <div style={{color:C.green,fontFamily:M,fontSize:10,marginBottom:4}}>
              5S 2200mAh (80% usable)
            </div>
            <span style={{color:C.yellow,fontFamily:M,fontSize:18,fontWeight:"bold"}}>{cMin} min</span>
            <div style={{color:C.dimmer,fontFamily:M,fontSize:9,marginTop:4}}>
              5S 3000mAh → {c3Min} min cruise
            </div>
          </div>
        </div>
      </div>

      <SH t="CM4 Power Detail"/>
      <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:12,marginBottom:12}}>
        {[
          {st:"Idle (boot, no app)",a:0.35,v:5,note:"Shortly after boot"},
          {st:"Active flight app",a:0.85,v:5,note:"MAVLink relay + logging"},
          {st:"Peak (all cores, WiFi TX)",a:1.25,v:5,note:"Brief burst ≤2s"},
        ].map((s,i)=>(
          <div key={i} style={{padding:"10px 12px",border:`1px solid ${C.green}33`,
            background:"rgba(74,222,128,0.05)",borderRadius:4}}>
            <div style={{color:C.green,fontFamily:M,fontSize:10,fontWeight:"bold",marginBottom:5}}>{s.st}</div>
            <div style={{color:C.yellow,fontFamily:M,fontSize:13}}>{s.a}A · {(s.a*s.v).toFixed(1)}W</div>
            <div style={{color:C.dim,fontFamily:M,fontSize:9,marginTop:3}}>{s.note}</div>
          </div>
        ))}
      </div>
      <Note c={C.green} ch="CM4 is powered from the 5V BEC via the carrier J_PWR JST-GH. The CM4 module has its own internal PMIC and does not use the carrier's AP2112K LDO (which handles carrier peripherals only). Total BEC load in flight: CM4 (0.85A) + Servos (0.16A) + Radios (0.37A) + Pico stack (0.36A) ≈ 1.74A @ 5V → well within 3A BEC rating."/>

      <SH t="Upgrade Path"/>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:12}}>
        {[
          {label:"5S 3000mAh 75C",dw:"+70g",endh:h3Min+" min hover",endc:c3Min+" min cruise",note:"Best range option. ~790g AUW → T/W 1.65 (still marginal). Verify hover at 60%."},
          {label:"Dual 5S 2200mAh (series 10S)",dw:"+220g",endh:"N/A — motor upgrade needed",endc:"N/A",note:"Would require 10S-rated EDFs and ESCs. Out of scope for v1."},
        ].map((u,i)=>(
          <div key={i} style={{padding:"10px 12px",border:`1px solid rgba(255,255,255,0.1)`,
            background:"rgba(255,255,255,0.02)",borderRadius:4}}>
            <div style={{color:C.text,fontFamily:M,fontSize:11,fontWeight:"bold",marginBottom:6}}>{u.label}</div>
            <div style={{color:C.dim,fontFamily:M,fontSize:10}}>Δ weight: <span style={{color:C.orange}}>{u.dw}</span></div>
            <div style={{color:C.dim,fontFamily:M,fontSize:10}}>Hover: <span style={{color:C.yellow}}>{u.endh}</span></div>
            <div style={{color:C.dim,fontFamily:M,fontSize:10}}>Cruise: <span style={{color:C.yellow}}>{u.endc}</span></div>
            <div style={{color:C.dimmer,fontFamily:M,fontSize:9,marginTop:5,lineHeight:1.7}}>{u.note}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// COMMS-HAT-1 GPIO UPDATE (for CM4 pinout — identical to Pi Zero header)
// ═══════════════════════════════════════════════════════════════════
function ComphatTab(){
  const note_rows=[
    ["SPI0 (GPIO 7-11)","MCP2518FD CAN FD (CE1) + SLB9670 TPM (CE0) — shared bus"],
    ["SPI1 (GPIO 16-21)","W5500 Ethernet (CE1) + μSD log (CE2) + 49MHz RCRS (CE0)"],
    ["UART0 (GPIO 14/15)","SiK 915MHz MAVLink radio TX/RX"],
    ["GPIO 22","MCP2518FD CAN INT"],["GPIO 23","SLB9670 TPM IRQ"],
    ["GPIO 24","W5500 INT"],["GPIO 25","49MHz RCRS IRQ"],
    ["GPIO 26","49MHz RCRS RST"],["GPIO 27","MCP2562FD CAN STBY"],
    ["I²C (GPIO 2/3)","COMMS-HAT EEPROM (HAT ID) only"],
  ];
  return (
    <div>
      <Note c={C.green} ch="COMMS-HAT-1 pin-out is unchanged. The CM4's 40-pin GPIO header is electrically and physically identical to the Pi Zero 2W header — the COMMS-HAT-1 PCB mounts directly on the CM4-CARRIER-1 header with no modification. The CM4 accesses all peripherals via the same GPIO numbers as the Zero 2W would have."/>
      <SH t="COMMS-HAT-1 → CM4 GPIO Mapping" mt={16}/>
      <div style={{overflowX:"auto"}}>
        <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:11}}>
          <thead><tr>{["CM4 GPIO / BUS","PERIPHERAL"].map(h=>(
            <th key={h} style={{padding:"5px 10px",borderBottom:`1px solid ${C.border}`,color:C.accent,
              textAlign:"left",fontWeight:"normal",fontSize:10,letterSpacing:"0.08em",opacity:.8}}>{h}</th>
          ))}</tr></thead>
          <tbody>{note_rows.map(([k,v],i)=>(
            <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
              <td style={{padding:"5px 10px",color:C.yellow,fontFamily:M,whiteSpace:"nowrap"}}>{k}</td>
              <td style={{padding:"5px 10px",color:C.text}}>{v}</td>
            </tr>
          ))}</tbody>
        </table>
      </div>
      <SH t="Dual microSD Roles"/>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:16,marginTop:4}}>
        {[
          {label:"SD1 — CM4 OS card",c:C.lime,loc:"CM4-CARRIER-1 board",iface:"SDIO0 (native CM4)",use:"Raspberry Pi OS Lite headless boot · application code · config files",note:"≥32GB A2 U3 card. Mounts as / (root) on CM4. Accessed by Linux kernel."},
          {label:"SD2 — Log / data card",c:C.green,loc:"COMMS-HAT-1 hat",iface:"SPI1 CE2 (slower but adequate)",use:"MAVLink black-box logs · sensor recordings · payload event logs",note:"≥16GB. Mounted by application as /mnt/log. FAT32 for easy host retrieval."},
        ].map((s,i)=>(
          <div key={i} style={{padding:"12px 14px",border:`1px solid ${s.c}44`,
            background:`${s.c}07`,borderRadius:4}}>
            <div style={{color:s.c,fontFamily:M,fontSize:11,fontWeight:"bold",marginBottom:6}}>{s.label}</div>
            <KV k="Location" v={s.loc}/>
            <KV k="Interface" v={s.iface}/>
            <KV k="Purpose" v={s.use}/>
            <div style={{color:C.dimmer,fontFamily:M,fontSize:9,marginTop:6,lineHeight:1.7}}>{s.note}</div>
          </div>
        ))}
      </div>
      <SH t="CM4 Software Stack"/>
      {[
        ["OS","Raspberry Pi OS Lite (64-bit, bookworm) — headless"],
        ["MAVLink relay","MAVSDK-Python or mavlink-router — bridges Pico UART ↔ SiK radio ↔ GCS"],
        ["CAN stack","can-utils + python-can / DroneCAN library via MCP2518FD"],
        ["Logging","pymavlink + custom logger → SD2 FAT32"],
        ["WiFi use","SSH debug in field · QGC WiFi link as backup to SiK"],
        ["TPM","tpm2-tools + tpm2-tss · attests firmware before arming"],
        ["RCRS","49MHz decoded to SBUS → piped to Pico 2 via UART"],
        ["Boot time","~12s to application ready from cold start"],
      ].map(([k,v],i)=>(<KV key={i} k={k} v={v}/>))}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// SYSTEM BOM DELTA
// ═══════════════════════════════════════════════════════════════════
function BomDeltaTab(){
  const removed=[
    {part:"Raspberry Pi Zero 2W",w:"−9g",cost:"−$15",note:"Replaced by CM4 Lite — insufficient RAM"},
  ];
  const added=[
    {part:"CM4 Lite 4GB WiFi",w:"+8g",cost:"+$55",note:"BCM2711 · 4GB LPDDR4X · 802.11ac · BT5"},
    {part:"CM4-CARRIER-1 PCB (custom)",w:"+14g",cost:"+$18",note:"65×40mm · DF40 connectors · μSD · USB hub · WiFi ant"},
    {part:"Hirose DF40C-100DS ×2",w:"+1g",cost:"+$8",note:"CM4 mating connectors · 0.4mm pitch"},
    {part:"GL850G USB 2.0 hub IC",w:"<1g",cost:"+$2",note:"4-port USB hub for carrier"},
    {part:"MicroSD A2 U3 ≥32GB (OS)",w:"+2g",cost:"+$10",note:"CM4 OS boot card on carrier"},
    {part:"11mm tall 2×20 GPIO header",w:"+1g",cost:"+$2",note:"Stack clearance for CM4 underside components"},
  ];
  const prev=420+59; // v1 base + companion section estimate
  const newDelta=8+14+1-9;
  return (
    <div>
      <SH t="Changes vs Pi Zero 2W" mt={0}/>
      <div style={{marginBottom:16}}>
        <div style={{color:C.red,fontFamily:M,fontSize:11,marginBottom:8,letterSpacing:"0.06em"}}>REMOVED</div>
        {removed.map((r,i)=>(
          <div key={i} style={{display:"flex",gap:16,padding:"6px 10px",
            border:"1px solid rgba(248,113,113,0.2)",background:"rgba(248,113,113,0.04)",
            borderRadius:3,marginBottom:4,alignItems:"center",flexWrap:"wrap"}}>
            <span style={{color:C.red,fontFamily:M,fontSize:11,minWidth:200}}>{r.part}</span>
            <span style={{color:C.orange,fontFamily:M,fontSize:11,minWidth:50}}>{r.w}</span>
            <span style={{color:C.orange,fontFamily:M,fontSize:11,minWidth:50}}>{r.cost}</span>
            <span style={{color:C.dim,fontFamily:M,fontSize:10}}>{r.note}</span>
          </div>
        ))}
      </div>
      <div style={{marginBottom:16}}>
        <div style={{color:C.green,fontFamily:M,fontSize:11,marginBottom:8,letterSpacing:"0.06em"}}>ADDED</div>
        {added.map((r,i)=>(
          <div key={i} style={{display:"flex",gap:16,padding:"6px 10px",
            border:"1px solid rgba(74,222,128,0.2)",background:"rgba(74,222,128,0.04)",
            borderRadius:3,marginBottom:4,alignItems:"center",flexWrap:"wrap"}}>
            <span style={{color:C.green,fontFamily:M,fontSize:11,minWidth:220}}>{r.part}</span>
            <span style={{color:C.yellow,fontFamily:M,fontSize:11,minWidth:50}}>{r.w}</span>
            <span style={{color:C.yellow,fontFamily:M,fontSize:11,minWidth:50}}>{r.cost}</span>
            <span style={{color:C.dim,fontFamily:M,fontSize:10}}>{r.note}</span>
          </div>
        ))}
      </div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr 1fr",gap:12,marginTop:16}}>
        {[
          {label:"Net weight delta",val:"+14g",c:C.yellow,sub:"vs Pi Zero 2W companion"},
          {label:"Net cost delta",val:"+~$80",c:C.yellow,sub:"CM4 Lite premium"},
          {label:"New total AUW",val:`${TOTAL_WEIGHT}g`,c:C.orange,sub:"vs 630g w/ Zero 2W"},
        ].map((s,i)=>(
          <div key={i} style={{padding:"10px 14px",border:`1px solid ${s.c}44`,
            background:`${s.c}07`,borderRadius:4}}>
            <div style={{color:C.dim,fontFamily:M,fontSize:9,marginBottom:4}}>{s.label}</div>
            <div style={{color:s.c,fontFamily:M,fontSize:18,fontWeight:"bold"}}>{s.val}</div>
            <div style={{color:C.dimmer,fontFamily:M,fontSize:9,marginTop:2}}>{s.sub}</div>
          </div>
        ))}
      </div>
      <Warn ch={`Net AUW increase from Zero 2W → CM4: +14g. T/W ratio remains ${TW}:1 — adequate. Battery slide +18mm aft to re-trim CG. No ESC or motor changes required; 5S 2200mAh remains viable.`}/>
      <Note c={C.green} ch="CM4-CARRIER-1 at 65×40mm is 10mm wider than a Pi Zero (65×30mm) — unavoidable given the 55×40mm CM4 module footprint. Length is identical at 65mm. The COMMS-HAT-1 (65×48mm) is already wider than the Zero, so the carrier fits within the same fuselage bay envelope. Footprint mount holes are Pi Zero-compatible (58mm × 23mm diagonal)."/>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// CARRIER TAB
// ═══════════════════════════════════════════════════════════════════
function CarrierTab(){
  const [sel,setSel]=useState(null);
  return (
    <div>
      <div style={{display:"flex",gap:6,flexWrap:"wrap",marginBottom:14}}>
        <Tag ch="CM4 Lite 4GB WiFi" c={C.green}/>
        <Tag ch="65×40mm · 4-layer" c={C.green}/>
        <Tag ch="Hirose DF40C-100 ×2" c={C.lime}/>
        <Tag ch="μSD OS slot" c={C.lime}/>
        <Tag ch="GL850G USB hub" c={C.accent}/>
        <Tag ch="PCB WiFi antenna" c={C.accent}/>
        <Tag ch="40-pin GPIO header" c={C.orange}/>
        <Tag ch="JST-GH power" c={C.yellow}/>
      </div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 240px",gap:20,alignItems:"start"}}>
        <div>
          <div style={{color:C.dimmer,fontSize:10,fontFamily:M,letterSpacing:"0.1em",marginBottom:8}}>
            CM4-CARRIER-1 · TOP VIEW · CM4 MODULE MOUNTS UNDERSIDE · CLICK TO INSPECT
          </div>
          <div style={{border:`1px solid rgba(74,222,128,0.2)`,borderRadius:4,
            background:"rgba(0,25,15,0.4)",padding:8}}>
            <CarrierPCB selected={sel} onSelect={setSel}/>
          </div>
          <div style={{marginTop:10}}>
            <StackDiagram/>
          </div>
        </div>
        <div style={{position:"sticky",top:20}}>
          <div style={{color:C.dimmer,fontSize:10,fontFamily:M,letterSpacing:"0.08em",marginBottom:8}}>
            COMPONENT INSPECTOR
          </div>
          <CarrierDetailPanel id={sel}/>
          {!sel && (
            <div style={{marginTop:16}}>
              <KV k="Board size" v="65×40mm"/>
              <KV k="Layers" v="4-layer"/>
              <KV k="Finish" v="ENIG"/>
              <KV k="CM4 connectors" v="2× Hirose DF40C-100"/>
              <KV k="CM4 orientation" v="Underside (sandwich)"/>
              <KV k="GPIO header" v="2×20 2.54mm · Pi-standard"/>
              <KV k="OS microSD" v="SDIO0 · separate from log SD"/>
              <KV k="USB" v="GL850G hub · USB-C OTG/pwr"/>
              <KV k="WiFi" v="PCB trace ant · CM4 onboard radio"/>
              <KV k="Stack height" v="~22mm total w/ COMMS-HAT-1"/>
              <KV k="Weight (PCB)" v="~14g"/>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════════
// APP
// ═══════════════════════════════════════════════════════════════════
const TABS=["CM4 Carrier","COMMS-HAT-1","Weight & CG","Power Budget","BOM Delta"];

_ODFontLoader();
export default function App(){
  const [tab,setTab]=useState("CM4 Carrier");
  return (
    <div style={{minHeight:"100vh",background:C.bg,color:C.text,fontFamily:M}}>
      <Grid/>
      {/* Header */}
      <div style={{position:"relative",zIndex:1,borderBottom:`1px solid ${C.border}`,padding:"20px 28px 16px"}}>
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",flexWrap:"wrap",gap:12}}>
          <div>
            <div style={{color:"rgba(74,222,128,0.35)",fontSize:9,letterSpacing:"0.2em",marginBottom:5}}>
              TILTROTOR UAV · COMPANION COMPUTER UPDATE · REV B
            </div>
            <h1 style={{margin:0,fontSize:20,fontWeight:"normal",color:"#fff",letterSpacing:"0.07em"}}>
              CM4 LITE 4GB + CARRIER BOARD
            </h1>
            <div style={{color:"rgba(74,222,128,0.55)",fontSize:10,marginTop:5}}>
              CM4-CARRIER-1 · COMMS-HAT-1 · Recalculated weight / CG / power
            </div>
          </div>
          <div style={{textAlign:"right",fontFamily:M}}>
            <div style={{color:C.yellow,fontSize:14,fontWeight:"bold"}}>AUW {TOTAL_WEIGHT}g</div>
            <div style={{color:C.green,fontSize:11,marginTop:3}}>T/W {TW}:1 · hover ~{HOVER_THR}%</div>
            <div style={{color:C.dimmer,fontSize:9,marginTop:2}}>5S 2200mAh · +14g vs Zero 2W</div>
          </div>
        </div>
        <div style={{display:"flex",gap:2,marginTop:16,flexWrap:"wrap"}}>
          {TABS.map(t=>(
            <button key={t} onClick={()=>setTab(t)} style={{
              background:tab===t?"rgba(74,222,128,0.1)":"transparent",
              border:`1px solid ${tab===t?C.green:"rgba(74,222,128,0.15)"}`,
              color:tab===t?C.green:C.dimmer,padding:"5px 13px",fontFamily:M,
              fontSize:10,cursor:"pointer",letterSpacing:"0.07em",transition:"all 0.12s"}}>{t}</button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div style={{position:"relative",zIndex:1,padding:"24px 28px",maxWidth:1020,margin:"0 auto"}}>
        {tab==="CM4 Carrier"    && <CarrierTab/>}
        {tab==="COMMS-HAT-1"     && <ComphatTab/>}
        {tab==="Weight & CG"   && <WeightTab/>}
        {tab==="Power Budget"  && <PowerTab/>}
        {tab==="BOM Delta"     && <BomDeltaTab/>}
      </div>

      <div style={{position:"relative",zIndex:1,borderTop:`1px solid ${C.border}`,
        padding:"11px 28px",display:"flex",justifyContent:"space-between",flexWrap:"wrap",gap:6}}>
        <span style={{color:"rgba(74,222,128,0.2)",fontSize:8,letterSpacing:"0.12em"}}>
          CM4-CARRIER-1 + COMMS-HAT-1 · REV B · TRI-FAN TILTROTOR
        </span>
        <span style={{color:"rgba(74,222,128,0.2)",fontSize:8,letterSpacing:"0.1em"}}>
          REFERENCE DESIGN · VERIFY BEFORE FABRICATION
        </span>
      </div>
    </div>
  );
}
