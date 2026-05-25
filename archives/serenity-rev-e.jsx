import { useState } from "react";

// ── tokens ─────────────────────────────────────────────────────
const C = {
  bg:"#060810", border:"rgba(0,229,255,0.11)", accent:"#00e5ff",
  orange:"#ff6b35", yellow:"#ffe600", purple:"#c084fc", green:"#4ade80",
  pink:"#f472b6", teal:"#2dd4bf", red:"#f87171", lime:"#a3e635",
  dim:"rgba(255,255,255,0.40)", dimmer:"rgba(255,255,255,0.22)", text:"rgba(255,255,255,0.82)",
};
const M = "'Courier New','Lucida Console',monospace";

// ── primitives ────────────────────────────────────────────────
const SH=({t,c=C.accent,mt=22})=>(<div style={{display:"flex",alignItems:"center",gap:10,marginBottom:14,marginTop:mt}}><div style={{width:3,height:17,background:c}}/><span style={{color:c,fontFamily:M,fontSize:13,letterSpacing:"0.13em",textTransform:"uppercase",fontWeight:"normal"}}>{t}</span></div>);
const KV=({k,v,vc=C.text,u=""})=>(<div style={{display:"flex",justifyContent:"space-between",padding:"5px 0",borderBottom:"1px solid rgba(0,229,255,0.07)",alignItems:"baseline"}}><span style={{color:C.dim,fontFamily:M,fontSize:11}}>{k}</span><span style={{color:vc,fontFamily:M,fontSize:11}}>{v}{u&&<span style={{color:C.accent,marginLeft:4,fontSize:10}}>{u}</span>}</span></div>);
const Note=({c=C.dim,ch})=>(<div style={{marginTop:8,marginBottom:6,color:c,fontFamily:M,fontSize:10,lineHeight:1.85,padding:"8px 12px",borderLeft:`2px solid ${c}55`,background:`${c}07`,borderRadius:3}}>{ch}</div>);
const Warn=({ch})=>(<div style={{marginTop:8,color:C.yellow,fontFamily:M,fontSize:10,lineHeight:1.8,padding:"7px 12px",borderLeft:`2px solid ${C.yellow}`,background:"rgba(255,230,0,0.05)",borderRadius:3}}>⚠ {ch}</div>);
const Good=({ch})=>(<div style={{marginTop:8,color:C.green,fontFamily:M,fontSize:10,lineHeight:1.8,padding:"7px 12px",borderLeft:`2px solid ${C.green}`,background:"rgba(74,222,128,0.05)",borderRadius:3}}>✓ {ch}</div>);
const Secure=({ch})=>(<div style={{marginTop:8,color:C.lime,fontFamily:M,fontSize:10,lineHeight:1.8,padding:"7px 12px",borderLeft:`2px solid ${C.lime}`,background:"rgba(163,230,53,0.05)",borderRadius:3}}>🔒 {ch}</div>);
function TH({cols}){return(<thead><tr>{cols.map(h=>(<th key={h} style={{padding:"6px 9px",borderBottom:`1px solid ${C.border}`,color:C.accent,textAlign:"left",fontWeight:"normal",fontSize:10,letterSpacing:"0.06em",whiteSpace:"nowrap",opacity:.85}}>{h}</th>))}</tr></thead>);}
function Grid(){return(<svg style={{position:"fixed",inset:0,width:"100%",height:"100%",pointerEvents:"none",zIndex:0}}><defs><pattern id="sg" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0L0 0 0 20" fill="none" stroke="rgba(0,229,255,0.035)" strokeWidth={0.5}/></pattern><pattern id="lg" width="100" height="100" patternUnits="userSpaceOnUse"><rect width="100" height="100" fill="url(#sg)"/><path d="M100 0L0 0 0 100" fill="none" stroke="rgba(0,229,255,0.065)" strokeWidth={1}/></pattern></defs><rect width="100%" height="100%" fill="url(#lg)"/></svg>);}

// ── hull geometry ─────────────────────────────────────────────
const SC=(mm)=>mm*1.28, NX=55, xp=(mm)=>NX+SC(mm);
const PROF=[[0,0],[8,10],[22,18],[40,30],[58,36],[88,37],[120,42],[140,42],[165,40],[190,36],[220,29],[252,18],[260,16],[278,24],[305,29],[330,28],[360,22]];
function hullOutline(CY){const up=PROF.map(([x,y])=>[xp(x),CY-SC(y)]);const lo=[...PROF].reverse().map(([x,y])=>[xp(x),CY+SC(y)]);return[...up,...lo].map((p,i)=>i===0?`M${p[0]},${p[1]}`:`L${p[0]},${p[1]}`).join(" ")+"Z";}

// ═══════════════════════════════════════════════════════════════
//  TAB: LICENSE
// ═══════════════════════════════════════════════════════════════
const LICENSE_COMPONENTS=[
  {id:"Hull",   origin:"Peter Farell",   url:"printables.com/model/548545",   lic:"CC BY 4.0","note":"Serenity Firefly-class hull — adapted, scaled, hollowed"},
  {id:"Nozzle", origin:"BamJr",          url:"thingiverse.com/thing:2991269", lic:"CC BY 4.0","note":"Variable-area EDF nozzle — remixed for 40mm ID + Serenity bell integration"},
  {id:"Design", origin:"This project",   url:"—",                             lic:"CC BY 4.0","note":"All original design work: PCBs, firmware spec, wiring, flight system"},
];

function LicenseTab(){
  return(<div>
    <SH t="Creative Commons Attribution 4.0 International" mt={0} c={C.lime}/>
    {/* CC badge */}
    <div style={{padding:"24px",border:`1px solid ${C.lime}44`,borderRadius:8,background:"rgba(163,230,53,0.06)",marginBottom:24,textAlign:"center"}}>
      <div style={{color:C.lime,fontFamily:M,fontSize:28,letterSpacing:"0.04em",fontWeight:"bold",marginBottom:8}}>CC BY 4.0</div>
      <div style={{color:C.text,fontFamily:M,fontSize:14,marginBottom:4}}>SERENITY TILTROTOR DRONE PROJECT</div>
      <div style={{color:C.dim,fontFamily:M,fontSize:11}}>Attribution 4.0 International · creativecommons.org/licenses/by/4.0</div>
      <div style={{display:"flex",justifyContent:"center",gap:20,marginTop:16,flexWrap:"wrap"}}>
        {[["Share","Copy and redistribute in any medium or format"],["Adapt","Remix, transform, and build upon for any purpose"],["Commercial","Even for commercial purposes"]].map(([t,d])=>(
          <div key={t} style={{padding:"10px 16px",border:`1px solid ${C.lime}44`,borderRadius:4,maxWidth:180}}>
            <div style={{color:C.lime,fontFamily:M,fontSize:11,fontWeight:"bold",marginBottom:4}}>{t}</div>
            <div style={{color:C.dim,fontFamily:M,fontSize:9,lineHeight:1.6}}>{d}</div>
          </div>
        ))}
      </div>
    </div>

    <SH t="Condition — Attribution Required" c={C.yellow}/>
    <div style={{padding:"16px",border:`1px solid ${C.yellow}44`,background:"rgba(255,230,0,0.05)",borderRadius:4,marginBottom:20}}>
      <div style={{color:C.yellow,fontFamily:M,fontSize:11,marginBottom:8,fontWeight:"bold"}}>You must give appropriate credit when sharing or adapting this work.</div>
      <div style={{background:"rgba(0,0,0,0.3)",borderRadius:4,padding:"12px 14px",fontFamily:M,fontSize:11,color:C.text,lineHeight:1.9,border:`1px solid rgba(255,255,255,0.1)`}}>
        <div style={{color:C.dimmer,fontSize:9,marginBottom:6,letterSpacing:"0.1em"}}>SUGGESTED ATTRIBUTION TEMPLATE:</div>
        "Serenity Tiltrotor Drone Project, CC BY 4.0, based on:<br/>
        · Serenity Firefly-class hull by Peter Farell (printables.com/model/548545, CC BY 4.0)<br/>
        · Variable-area EDF nozzle by BamJr (thingiverse.com/thing:2991269, CC BY 4.0)<br/>
        Include a link to creativecommons.org/licenses/by/4.0 and indicate if changes were made."
      </div>
    </div>

    <SH t="Component License Map"/>
    <div style={{overflowX:"auto",marginBottom:20}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["COMPONENT","ORIGINAL AUTHOR","SOURCE","LICENSE","DERIVATIVE NOTES"]}/>
        <tbody>{LICENSE_COMPONENTS.map((r,i)=>(<tr key={i} style={{background:i%2===0?"rgba(163,230,53,0.03)":"transparent"}}>
          <td style={{padding:"6px 10px",color:C.lime,fontWeight:"bold"}}>{r.id}</td>
          <td style={{padding:"6px 10px",color:C.text}}>{r.origin}</td>
          <td style={{padding:"6px 10px",color:C.teal,fontSize:9}}>{r.url}</td>
          <td style={{padding:"6px 10px"}}><span style={{color:C.lime,border:`1px solid ${C.lime}44`,padding:"1px 7px",borderRadius:2,fontSize:9}}>{r.lic}</span></td>
          <td style={{padding:"6px 10px",color:C.dim,fontSize:9,lineHeight:1.5}}>{r.note}</td>
        </tr>))}</tbody>
      </table>
    </div>

    <SH t="What This License Covers"/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <div style={{color:C.green,fontFamily:M,fontSize:11,marginBottom:8,fontWeight:"bold"}}>✓ COVERED under CC BY 4.0</div>
        {["3D printable hull, nacelle, bell, and nozzle design files (STL/STEP/F3D)","PCB schematics and Gerber files for TRIHAT-1, CM4-CARRIER-1, COMMS-HAT-1","Circuit diagrams, pinout tables, and wiring specifications","Mechanical drawings and assembly specifications","Firmware architecture specifications and algorithm descriptions","This design document in all its revisions (A–E and beyond)","Any derived works must carry CC BY 4.0 and attribute all upstream authors"].map((s,i)=>(<div key={i} style={{display:"flex",gap:8,padding:"4px 0",borderBottom:"1px solid rgba(74,222,128,0.08)"}}><span style={{color:C.green,fontSize:10,flexShrink:0}}>✓</span><span style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.6}}>{s}</span></div>))}
      </div>
      <div>
        <div style={{color:C.orange,fontFamily:M,fontSize:11,marginBottom:8,fontWeight:"bold"}}>⚠ NOT COVERED / SEPARATE TERMS</div>
        {["Third-party commercial components (EDFs, ESCs, Pico 2, CM4, etc.) — governed by their own terms","SiK radio firmware — GPL-3.0","QGroundControl — GPL-3.0","Raspberry Pi OS — mixed GPL","tpm2-tools / tpm2-tss — BSD-2","CPLD Verilog write-blocker firmware — separately MIT licensed","Proprietary flight controller firmware (your compiled code) — your terms","FAA/ICAO regulatory compliance is YOUR responsibility as operator"].map((s,i)=>(<div key={i} style={{display:"flex",gap:8,padding:"4px 0",borderBottom:"1px solid rgba(255,107,53,0.08)"}}><span style={{color:C.orange,fontSize:10,flexShrink:0}}>!</span><span style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.6}}>{s}</span></div>))}
      </div>
    </div>

    <SH t="Patent Notice"/>
    <Note c={C.dim} ch="This license does NOT grant rights to any patents held by component manufacturers or the design authors. The design uses standard open hardware interfaces (CAN FD, Ethernet, SDIO, SPI, I²C, MAVLink). If you commercialise products based on this design, conduct your own freedom-to-operate analysis. The write-blocker CPLD design follows published NIST SP 800-72 principles; no patent claims are made on the implementation."/>

    <SH t="Forensic Evidence Integrity Note"/>
    <Note c={C.lime} ch="The write-blocker and NX enforcement hardware described in this design are intended to support forensic data integrity in UAV operations contexts. They are NOT certified forensic tools per NIST/SWGDE standards. Do not use this design as the sole mechanism for evidence preservation in legal proceedings without independent verification of the implementation against your jurisdiction's evidence handling requirements."/>
  </div>);
}

// ═══════════════════════════════════════════════════════════════
//  TAB: CM4-CARRIER-1 (Rev E — write blocker + NX + dual WiFi SMA)
// ═══════════════════════════════════════════════════════════════
function WBDiagram(){
  const VW=580,VH=320;
  // CM4 SDIO0 → CPLD → SD card
  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:600,display:"block"}}>
      {/* CM4 block */}
      <rect x={20} y={100} width={110} height={120} rx={5} fill="rgba(74,222,128,0.07)" stroke={C.green} strokeWidth={1.5}/>
      <text x={75} y={122} textAnchor="middle" fill={C.green} fontSize={10} fontFamily={M} fontWeight="bold">CM4</text>
      <text x={75} y={137} textAnchor="middle" fill="rgba(74,222,128,0.5)" fontSize={8} fontFamily={M}>BCM2711</text>
      <text x={75} y={153} textAnchor="middle" fill="rgba(74,222,128,0.5)" fontSize={8} fontFamily={M}>SDIO0 host</text>
      <text x={75} y={168} textAnchor="middle" fill="rgba(74,222,128,0.45)" fontSize={7} fontFamily={M}>CLK · CMD</text>
      <text x={75} y={181} textAnchor="middle" fill="rgba(74,222,128,0.45)" fontSize={7} fontFamily={M}>DAT[3:0]</text>
      <text x={75} y={208} textAnchor="middle" fill="rgba(74,222,128,0.3)" fontSize={7} fontFamily={M}>(via DF40)</text>

      {/* SDIO bus A (CM4→CPLD) */}
      <line x1={130} y1={160} x2={185} y2={160} stroke={C.green} strokeWidth={3} strokeLinecap="round"/>
      <text x={157} y={152} textAnchor="middle" fill="rgba(74,222,128,0.6)" fontSize={7} fontFamily={M}>SDIO0</text>
      <text x={157} y={174} textAnchor="middle" fill="rgba(74,222,128,0.4)" fontSize={6} fontFamily={M}>6 signals</text>

      {/* CPLD block */}
      <rect x={185} y={80} width={120} height={160} rx={5} fill="rgba(163,230,53,0.09)" stroke={C.lime} strokeWidth={2}/>
      <text x={245} y={103} textAnchor="middle" fill={C.lime} fontSize={10} fontFamily={M} fontWeight="bold">MachXO2-256</text>
      <text x={245} y={117} textAnchor="middle" fill="rgba(163,230,53,0.6)" fontSize={8} fontFamily={M}>CPLD WRITE</text>
      <text x={245} y={129} textAnchor="middle" fill="rgba(163,230,53,0.6)" fontSize={8} fontFamily={M}>BLOCKER</text>
      <line x1={195} y1={145} x2={295} y2={145} stroke="rgba(163,230,53,0.2)" strokeWidth={0.7}/>
      {["CMD monitor","Opcode decoder","R1 injector","WP latch","Audit LED ctrl"].map((s,i)=>(
        <text key={i} x={245} y={160+i*14} textAnchor="middle" fill="rgba(163,230,53,0.5)" fontSize={7} fontFamily={M}>{s}</text>
      ))}

      {/* SDIO bus B (CPLD→SD) — color changes based on write detect */}
      <line x1={305} y1={160} x2={365} y2={160} stroke={C.lime} strokeWidth={3} strokeLinecap="round"/>
      <text x={335} y={152} textAnchor="middle" fill="rgba(163,230,53,0.6)" fontSize={7} fontFamily={M}>SDIO0</text>
      <text x={335} y={174} textAnchor="middle" fill="rgba(163,230,53,0.4)" fontSize={6} fontFamily={M}>filtered</text>

      {/* SD card slot */}
      <rect x={365} y={115} width={80} height={90} rx={4} fill="rgba(74,222,128,0.06)" stroke={C.green} strokeWidth={1.2}/>
      <text x={405} y={152} textAnchor="middle" fill={C.green} fontSize={9} fontFamily={M} fontWeight="bold">OS μSD</text>
      <text x={405} y={166} textAnchor="middle" fill="rgba(74,222,128,0.5)" fontSize={7} fontFamily={M}>SDIO0 slot</text>
      <text x={405} y={179} textAnchor="middle" fill="rgba(74,222,128,0.4)" fontSize={6} fontFamily={M}>RPi OS Lite</text>

      {/* Bypass jumper */}
      <rect x={210} y={18} width={72} height={28} rx={3} fill="rgba(255,230,0,0.1)" stroke={C.yellow} strokeWidth={1}/>
      <text x={246} y={28} textAnchor="middle" fill={C.yellow} fontSize={7} fontFamily={M} fontWeight="bold">JP2 FORENSIC</text>
      <text x={246} y={40} textAnchor="middle" fill="rgba(255,230,0,0.6)" fontSize={6} fontFamily={M}>installed=WB active</text>
      <line x1={246} y1={46} x2={246} y2={80} stroke={C.yellow} strokeWidth={1} strokeDasharray="3 2"/>

      {/* LED indicators */}
      <circle cx={460} cy={100} r={8} fill="rgba(74,222,128,0.3)" stroke={C.green} strokeWidth={1}/>
      <text x={460} y={103} textAnchor="middle" fill={C.green} fontSize={6} fontFamily={M}>WB</text>
      <text x={460} y={88} textAnchor="middle" fill={C.green} fontSize={6} fontFamily={M}>GREEN</text>
      <circle cx={500} cy={100} r={8} fill="rgba(248,113,113,0.3)" stroke={C.red} strokeWidth={1}/>
      <text x={500} y={103} textAnchor="middle" fill={C.red} fontSize={6} fontFamily={M}>WR</text>
      <text x={500} y={88} textAnchor="middle" fill={C.red} fontSize={6} fontFamily={M}>RED</text>
      <text x={480} y={76} textAnchor="middle" fill={C.dimmer} fontSize={6} fontFamily={M}>LED indicators</text>

      {/* Blocked write commands arrow */}
      <path d="M245,240 Q245,280 320,280 Q390,280 390,220" fill="none" stroke={C.red} strokeWidth={1.5} strokeDasharray="4 2" markerEnd="url(#arr)"/>
      <defs><marker id="arr" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill={C.red}/></marker></defs>
      <rect x={240} y={248} width={120} height={18} rx={2} fill="rgba(248,113,113,0.08)" stroke={C.red} strokeWidth={0.8}/>
      <text x={300} y={260} textAnchor="middle" fill={C.red} fontSize={7} fontFamily={M}>WRITE BLOCKED (R1·WP_VIOLATION)</text>
      <text x={300} y={300} textAnchor="middle" fill={`${C.red}60`} fontSize={7} fontFamily={M}>CMD24/25/28/29/32-38/42 intercepted</text>

      <text x={VW/2} y={16} textAnchor="middle" fill="rgba(0,229,255,0.25)" fontSize={9} fontFamily={M} letterSpacing="0.1em">OS SD WRITE-BLOCKER ARCHITECTURE (SDIO0 PATH)</text>
    </svg>
  );
}

function NXDiagram(){
  const VW=580,VH=300;
  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:600,display:"block"}}>
      {/* CM4 SPI master */}
      <rect x={20} y={80} width={110} height={140} rx={5} fill="rgba(74,222,128,0.07)" stroke={C.green} strokeWidth={1.5}/>
      <text x={75} y={102} textAnchor="middle" fill={C.green} fontSize={10} fontFamily={M} fontWeight="bold">CM4</text>
      <text x={75} y={116} textAnchor="middle" fill="rgba(74,222,128,0.5)" fontSize={8} fontFamily={M}>SPI1 master</text>
      <text x={75} y={135} textAnchor="middle" fill="rgba(74,222,128,0.45)" fontSize={7} fontFamily={M}>TrustZone</text>
      <text x={75} y={148} textAnchor="middle" fill="rgba(74,222,128,0.45)" fontSize={7} fontFamily={M}>secure world</text>
      <text x={75} y={165} textAnchor="middle" fill="rgba(74,222,128,0.3)" fontSize={7} fontFamily={M}>noexec SELinux</text>
      <text x={75} y={179} textAnchor="middle" fill="rgba(74,222,128,0.3)" fontSize={7} fontFamily={M}>OTP NX fuse</text>
      <text x={75} y={205} textAnchor="middle" fill="rgba(74,222,128,0.25)" fontSize={7} fontFamily={M}>on COMMS-HAT-1 hat</text>

      {/* SPI bus */}
      <line x1={130} y1={150} x2={185} y2={150} stroke={C.green} strokeWidth={2.5} strokeLinecap="round"/>
      <text x={157} y={142} textAnchor="middle" fill="rgba(74,222,128,0.6)" fontSize={7} fontFamily={M}>SPI1</text>

      {/* NX proxy MCU */}
      <rect x={185} y={65} width={130} height={170} rx={5} fill="rgba(255,107,53,0.08)" stroke={C.orange} strokeWidth={2}/>
      <text x={250} y={86} textAnchor="middle" fill={C.orange} fontSize={10} fontFamily={M} fontWeight="bold">STM32F030</text>
      <text x={250} y={100} textAnchor="middle" fill="rgba(255,107,53,0.6)" fontSize={8} fontFamily={M}>SPI PROXY / NX</text>
      <line x1={193} y1={113} x2={307} y2={113} stroke="rgba(255,107,53,0.2)" strokeWidth={0.7}/>
      {["SPI cmd intercept","CMD17/18 → PASS","CMD24/25 → BLOCK","SHA-256 audit log","Tamper detect","NX_LATCH read"].map((s,i)=>(
        <text key={i} x={250} y={126+i*15} textAnchor="middle" fill="rgba(255,107,53,0.5)" fontSize={7} fontFamily={M}>{s}</text>
      ))}
      <text x={250} y={224} textAnchor="middle" fill="rgba(255,107,53,0.3)" fontSize={6} fontFamily={M}>256KB flash (audit) · WP fuses blown</text>

      {/* NX latch */}
      <rect x={200} y={16} width={100} height={32} rx={3} fill="rgba(255,230,0,0.08)" stroke={C.yellow} strokeWidth={1}/>
      <text x={250} y={28} textAnchor="middle" fill={C.yellow} fontSize={7} fontFamily={M} fontWeight="bold">74HC74 NX LATCH</text>
      <text x={250} y={41} textAnchor="middle" fill="rgba(255,230,0,0.5)" fontSize={6} fontFamily={M}>SET at POR · cleared by JP3 only</text>
      <line x1={250} y1={48} x2={250} y2={65} stroke={C.yellow} strokeWidth={1} strokeDasharray="2 2"/>

      {/* JP3 override */}
      <rect x={320} y={16} width={80} height={28} rx={3} fill="rgba(255,230,0,0.06)" stroke={`${C.yellow}60`} strokeWidth={0.8}/>
      <text x={360} y={27} textAnchor="middle" fill={`${C.yellow}80`} fontSize={7} fontFamily={M}>JP3 NX-OVERRIDE</text>
      <text x={360} y={38} textAnchor="middle" fill="rgba(255,230,0,0.4)" fontSize={6} fontFamily={M}>tool-required · recessed</text>
      <line x1={320} y1={28} x2={300} y2={28} stroke={`${C.yellow}40`} strokeWidth={0.8} strokeDasharray="2 2"/>

      {/* SPI bus to SD */}
      <line x1={315} y1={150} x2={370} y2={150} stroke={C.lime} strokeWidth={2.5} strokeLinecap="round"/>
      <text x={342} y={142} textAnchor="middle" fill="rgba(163,230,53,0.6)" fontSize={7} fontFamily={M}>SPI1</text>
      <text x={342} y={166} textAnchor="middle" fill="rgba(163,230,53,0.4)" fontSize={6} fontFamily={M}>read-only</text>

      {/* Log SD */}
      <rect x={370} y={110} width={85} height={80} rx={4} fill="rgba(0,229,255,0.06)" stroke={C.accent} strokeWidth={1.2}/>
      <text x={412} y={143} textAnchor="middle" fill={C.accent} fontSize={9} fontFamily={M} fontWeight="bold">LOG μSD</text>
      <text x={412} y={157} textAnchor="middle" fill="rgba(0,229,255,0.5)" fontSize={7} fontFamily={M}>COMMS-HAT-1</text>
      <text x={412} y={170} textAnchor="middle" fill="rgba(0,229,255,0.4)" fontSize={6} fontFamily={M}>read+nav OK</text>
      <text x={412} y={183} textAnchor="middle" fill="rgba(248,113,113,0.5)" fontSize={6} fontFamily={M}>exec BLOCKED</text>

      {/* OTP arrow */}
      <path d="M75,220 Q75,260 180,260 Q280,260 315,200" fill="none" stroke={C.purple} strokeWidth={1} strokeDasharray="3 2" opacity={0.6}/>
      <text x={195} y={272} textAnchor="middle" fill={`${C.purple}70`} fontSize={6} fontFamily={M}>BCM2711 OTP NX fuse → TrustZone secure monitor enforces noexec</text>

      <text x={VW/2} y={292} textAnchor="middle" fill="rgba(0,229,255,0.2)" fontSize={8} fontFamily={M}>NX enforcement is multi-layer: hardware latch + SPI proxy + TrustZone + SELinux + OTP fuse</text>
      <text x={VW/2} y={14} textAnchor="middle" fill="rgba(0,229,255,0.25)" fontSize={9} fontFamily={M} letterSpacing="0.1em">LOG SD HARDWARE NX ENFORCEMENT ARCHITECTURE</text>
    </svg>
  );
}

function WiFiSMADiagram(){
  const VW=560,VH=220;
  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:580,display:"block"}}>
      {/* CM4 module */}
      <rect x={20} y={70} width={100} height={80} rx={4} fill="rgba(74,222,128,0.07)" stroke={C.green} strokeWidth={1.5}/>
      <text x={70} y={95} textAnchor="middle" fill={C.green} fontSize={9} fontFamily={M} fontWeight="bold">CM4 WiFi</text>
      <text x={70} y={109} textAnchor="middle" fill="rgba(74,222,128,0.5)" fontSize={7} fontFamily={M}>BCM43455</text>
      <text x={70} y={122} textAnchor="middle" fill="rgba(74,222,128,0.45)" fontSize={7} fontFamily={M}>2.4 + 5 GHz</text>
      <text x={70} y={136} textAnchor="middle" fill="rgba(74,222,128,0.3)" fontSize={7} fontFamily={M}>U.FL port</text>
      {/* U.FL from CM4 */}
      <circle cx={120} cy={110} r={5} fill="rgba(74,222,128,0.2)" stroke={C.green} strokeWidth={1}/>
      <text x={120} y={99} textAnchor="middle" fill={C.green} fontSize={6} fontFamily={M}>U.FL</text>
      <line x1={125} y1={110} x2={175} y2={110} stroke={C.green} strokeWidth={2}/>

      {/* RF Switch + Diplexer block */}
      <rect x={175} y={60} width={120} height={100} rx={4} fill="rgba(192,132,252,0.08)" stroke={C.purple} strokeWidth={1.5}/>
      <text x={235} y={80} textAnchor="middle" fill={C.purple} fontSize={9} fontFamily={M} fontWeight="bold">MABD-011028</text>
      <text x={235} y={93} textAnchor="middle" fill="rgba(192,132,252,0.6)" fontSize={8} fontFamily={M}>Diplexer</text>
      <line x1={183} y1={115} x2={295} y2={115} stroke="rgba(192,132,252,0.2)" strokeWidth={0.7}/>
      <text x={235} y={107} textAnchor="middle" fill="rgba(192,132,252,0.45)" fontSize={7} fontFamily={M}>2.4GHz LPF path</text>
      <text x={235} y={120} textAnchor="middle" fill="rgba(192,132,252,0.45)" fontSize={7} fontFamily={M}>5GHz HPF path</text>
      <text x={235} y={133} textAnchor="middle" fill="rgba(192,132,252,0.35)" fontSize={7} fontFamily={M}>0.3dB insertion loss</text>
      <text x={235} y={146} textAnchor="middle" fill="rgba(192,132,252,0.3)" fontSize={6} fontFamily={M}>45dB isolation @ split freq</text>

      {/* 2.4GHz path */}
      <line x1={295} y1={95} x2={380} y2={95} stroke={C.orange} strokeWidth={2}/>
      <text x={337} y={87} textAnchor="middle" fill={C.orange} fontSize={7} fontFamily={M}>2.4GHz</text>
      {/* SMA 2.4 */}
      <rect x={380} y={76} width={44} height={38} rx={3} fill="rgba(255,107,53,0.12)" stroke={C.orange} strokeWidth={1.3}/>
      <text x={402} y={93} textAnchor="middle" fill={C.orange} fontSize={8} fontFamily={M} fontWeight="bold">SMA-1</text>
      <text x={402} y={107} textAnchor="middle" fill="rgba(255,107,53,0.6)" fontSize={6} fontFamily={M}>2.4GHz</text>
      {/* Board edge SMA symbol */}
      <rect x={424} y={80} width={10} height={30} rx={2} fill={C.orange} opacity={0.4}/>
      <text x={455} y={87} fill={C.orange} fontSize={7} fontFamily={M}>SMA</text>
      <text x={455} y={98} fill={`${C.orange}70`} fontSize={6} fontFamily={M}>edge</text>
      <text x={455} y={109} fill={`${C.orange}50`} fontSize={6} fontFamily={M}>mount</text>

      {/* 5GHz path */}
      <line x1={295} y1={130} x2={380} y2={130} stroke={C.purple} strokeWidth={2}/>
      <text x={337} y={122} textAnchor="middle" fill={C.purple} fontSize={7} fontFamily={M}>5GHz</text>
      {/* SMA 5GHz */}
      <rect x={380} y={111} width={44} height={38} rx={3} fill="rgba(192,132,252,0.12)" stroke={C.purple} strokeWidth={1.3}/>
      <text x={402} y={128} textAnchor="middle" fill={C.purple} fontSize={8} fontFamily={M} fontWeight="bold">SMA-2</text>
      <text x={402} y={142} textAnchor="middle" fill="rgba(192,132,252,0.6)" fontSize={6} fontFamily={M}>5GHz</text>
      <rect x={424} y={115} width={10} height={30} rx={2} fill={C.purple} opacity={0.4}/>
      <text x={455} y={122} fill={C.purple} fontSize={7} fontFamily={M}>SMA</text>
      <text x={455} y={133} fill={`${C.purple}70`} fontSize={6} fontFamily={M}>edge</text>
      <text x={455} y={144} fill={`${C.purple}50`} fontSize={6} fontFamily={M}>mount</text>

      {/* PCB trace antenna dotted (disabled when external) */}
      <rect x={120} y={165} width={100} height={30} rx={3} fill="rgba(255,255,255,0.02)" stroke="rgba(255,255,255,0.15)" strokeWidth={0.8} strokeDasharray="4 2"/>
      <text x={170} y={178} textAnchor="middle" fill="rgba(255,255,255,0.25)" fontSize={7} fontFamily={M}>PCB trace antenna</text>
      <text x={170} y={190} textAnchor="middle" fill="rgba(255,255,255,0.18)" fontSize={6} fontFamily={M}>(disabled when SMA fitted)</text>
      {/* note: CM4 auto-selects U.FL when coax attached */}

      <text x={VW/2} y={14} textAnchor="middle" fill="rgba(0,229,255,0.25)" fontSize={9} fontFamily={M} letterSpacing="0.1em">DUAL-BAND WiFi SMA PATH — CM4-CARRIER-1</text>
      <text x={VW/2} y={212} textAnchor="middle" fill="rgba(0,229,255,0.2)" fontSize={8} fontFamily={M}>CM4 senses U.FL load and disables internal PCB trace antenna automatically</text>
    </svg>
  );
}

function CarrierTab(){
  return(<div>
    <div style={{background:"rgba(163,230,53,0.05)",border:`1px solid rgba(163,230,53,0.2)`,borderRadius:4,padding:"10px 14px",marginBottom:18,fontFamily:M,fontSize:11,color:C.dim,lineHeight:1.8}}>
      <span style={{color:C.lime,fontWeight:"bold"}}>Rev E additions to CM4-CARRIER-1:</span> Forensic write-blocker (SDIO path · MachXO2 CPLD) · Dual-band WiFi SMA output (MABD-011028 diplexer · 2× edge SMA connectors) · Board size update 65×52mm (+12mm width for new features).
    </div>

    <SH t="Forensic Write Blocker — OS SD (SDIO0)" mt={0} c={C.lime}/>
    <div style={{border:`1px solid ${C.lime}33`,borderRadius:4,background:"rgba(163,230,53,0.01)",padding:8,marginBottom:16}}>
      <WBDiagram/>
    </div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24,marginBottom:20}}>
      <div>
        <KV k="CPLD" v="Lattice MachXO2-256ZE · TQFP-32"/>
        <KV k="Signals intercepted" v="CLK · CMD · DAT[3:0] — all 6 SDIO0 lines"/>
        <KV k="Write commands blocked" v="CMD24 · CMD25 · CMD26 · CMD27 · CMD28 · CMD29 · CMD32–38 · CMD42" vc={C.lime}/>
        <KV k="Response injection" v="Valid R1 with WP_VIOLATION[bit 19] set"/>
        <KV k="WP pin" v="SD WP line pulled HIGH via 10kΩ when JP2 installed"/>
        <KV k="Bypass jumper" v="JP2 · 2-pin 2.54mm · FORENSIC label · board edge"/>
        <KV k="JP2 installed" v="Write blocking ACTIVE · forensic mode" vc={C.lime}/>
        <KV k="JP2 removed" v="Normal R/W · OS install / firmware update mode" vc={C.yellow}/>
        <KV k="LED indicators" v="LED1 green = WB active · LED2 red = write attempt blocked"/>
        <KV k="Throughput impact" v="&lt;2ns additional latency (combinatorial logic only)"/>
        <KV k="CPLD firmware" v="Open-source Verilog · MIT licensed · in project repo"/>
        <KV k="Compliance basis" v="NIST SP 800-72 hardware write-blocker principles"/>
      </div>
      <div>
        <Secure ch="The CPLD is a fully combinatorial SDIO proxy. It never buffers or stores data — it only pattern-matches the 6-bit CMD opcode field and substitutes a write-protected R1 response. Write attempts are logged by briefly illuminating LED2 (red flash per blocked command)."/>
        <Note c={C.yellow} ch="Remove JP2 (forensic jumper) only when re-flashing the OS. Replace immediately after. The jumper is physically recessed behind a 3D-printed guard tab that requires a 1mm pin to actuate — accidental removal in flight is not possible."/>
        <Note c={C.lime} ch="This implementation matches the logical behaviour of commercial forensic write blockers (Tableau T8, WiebeTech). It is not NIST-certified hardware, but the design is open-source and auditable. For evidentiary chain-of-custody, document jumper state before and after each flight in the mission log."/>
      </div>
    </div>

    <SH t="Dual-Band WiFi SMA — 2.4 GHz + 5 GHz" c={C.purple}/>
    <div style={{border:`1px solid ${C.purple}33`,borderRadius:4,background:"rgba(192,132,252,0.01)",padding:8,marginBottom:16}}>
      <WiFiSMADiagram/>
    </div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24,marginBottom:20}}>
      <div>
        <KV k="Diplexer IC" v="MABD-011028 · SOT-26"/>
        <KV k="Split frequency" v="~3.5 GHz cross-point"/>
        <KV k="2.4GHz insertion loss" v="0.3 dB max · isolation 45 dB"/>
        <KV k="5GHz insertion loss" v="0.4 dB max · isolation 45 dB"/>
        <KV k="Input" v="CM4 module U.FL connector · 50Ω · 10mm microstrip"/>
        <KV k="SMA-1 (2.4GHz)" v="SMA female edge mount · board top edge · orange label"/>
        <KV k="SMA-2 (5GHz)"  v="SMA female edge mount · board top edge · purple label"/>
        <KV k="Cable type" v="U.FL to diplexer: 0.81mm semi-rigid · ≤25mm"/>
        <KV k="PCB trace ant" v="Auto-disabled when CM4 detects U.FL load impedance"/>
        <KV k="Antenna options" v="Any RP-SMA or SMA dual-band patch/dipole · 2dBi min"/>
        <KV k="Board size" v="65×52mm (was 65×40mm — +12mm for diplexer + SMA)"/>
      </div>
      <div>
        <Note c={C.purple} ch="The BCM43455 chip in the CM4 module auto-detects the presence of an external antenna via the U.FL connector. When a cable is attached (VSWR ≠ open), the internal PCB trace antenna is automatically disabled by the chip's antenna-sense circuit. No software configuration needed."/>
        <Note c={C.teal} ch="For field debug (SSH), a 2.4GHz omni antenna on SMA-1 is sufficient. For 5GHz streaming, attach a gain antenna to SMA-2. Both bands are always active simultaneously on the BCM43455; the diplexer routes each band's signal to the appropriate SMA without switching."/>
        <Warn ch="SMA-2 (5GHz) microstrip trace must be ≤12mm with controlled impedance (50Ω). Route on TOP layer as coplanar waveguide with GND pour on both sides. Keep GND stitching vias ≤2mm apart along the trace. Incorrect 5GHz routing will cause significant insertion loss."/>
      </div>
    </div>

    <SH t="Updated CM4-CARRIER-1 Board Spec"/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:16}}>
      <div>
        <KV k="Board size"       v="65×52mm (Rev E) — was 65×40mm"/>
        <KV k="Layers"           v="4-layer · ENIG · 1oz Cu"/>
        <KV k="CM4 connectors"   v="2× Hirose DF40C-100"/>
        <KV k="OS microSD"       v="SDIO0 via write-blocker CPLD"/>
        <KV k="USB hub"          v="GL850G · 4-port USB2"/>
        <KV k="WiFi antenna"     v="MABD-011028 diplexer → SMA-1 (2.4G) + SMA-2 (5G)"/>
      </div>
      <div>
        <KV k="Write blocker"    v="MachXO2-256ZE CPLD · JP2 jumper · 2× LEDs"/>
        <KV k="GPIO header"      v="2×20 2.54mm · Pi-standard"/>
        <KV k="Power"            v="USB-C or JST-GH J_PWR · 5V/3A"/>
        <KV k="Weight"           v="~18g (was 14g — +4g for CPLD + diplexer + SMA)"/>
        <KV k="CM4 mounts"       v="Underside · sandwich orientation"/>
      </div>
    </div>
  </div>);
}

// ═══════════════════════════════════════════════════════════════
//  TAB: COMMS-HAT-1 Rev E (NX enforcement + Zigbee/LoRa)
// ═══════════════════════════════════════════════════════════════
const PROTO_SHARING=[
  {band:"2.4 GHz", ic:"CC2652P7",    proto:["Zigbee (IEEE 802.15.4)","LoRa 2.4GHz (custom RF)","BLE 5.0","Thread / Matter","IEEE 802.15.4 DSSS"],sel:"Software protocol image on CC2652P7 · one protocol active at a time · bootloader-selectable"},
  {band:"Sub-GHz 915MHz/868MHz",ic:"SX1276", proto:["LoRa (LoRaWAN)","FSK/GFSK (Zigbee 915MHz O-QPSK via software)","OOK","AFSK"],sel:"SX1276 is a flexible SDR-style transceiver · modulation set by CM4 register writes via SPI · protocol stack in CM4 userspace"},
];

function ZigbeeDiagram(){
  const VW=580,VH=280;
  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:600,display:"block"}}>
      {/* CM4 / Pico SPI buses */}
      <rect x={10} y={90} width={90} height={100} rx={4} fill="rgba(74,222,128,0.07)" stroke={C.green} strokeWidth={1.2}/>
      <text x={55} y={112} textAnchor="middle" fill={C.green} fontSize={8} fontFamily={M} fontWeight="bold">CM4 / PICO</text>
      <text x={55} y={126} textAnchor="middle" fill="rgba(74,222,128,0.4)" fontSize={7} fontFamily={M}>SPI master</text>
      <text x={55} y={140} textAnchor="middle" fill="rgba(74,222,128,0.4)" fontSize={7} fontFamily={M}>GPIO IRQ</text>
      <text x={55} y={155} textAnchor="middle" fill="rgba(74,222,128,0.4)" fontSize={7} fontFamily={M}>UART OPT</text>
      <text x={55} y={178} textAnchor="middle" fill="rgba(74,222,128,0.25)" fontSize={7} fontFamily={M}>(on COMMS-HAT-1)</text>

      {/* SPI lines to CC2652P7 */}
      <line x1={100} y1={125} x2={155} y2={125} stroke={C.teal} strokeWidth={2}/>
      <text x={127} y={117} textAnchor="middle" fill="rgba(45,212,191,0.6)" fontSize={7} fontFamily={M}>SPI2</text>

      {/* CC2652P7 */}
      <rect x={155} y={50} width={120} height={170} rx={5} fill="rgba(0,229,255,0.08)" stroke={C.accent} strokeWidth={1.8}/>
      <text x={215} y={72} textAnchor="middle" fill={C.accent} fontSize={9} fontFamily={M} fontWeight="bold">CC2652P7</text>
      <text x={215} y={86} textAnchor="middle" fill="rgba(0,229,255,0.5)" fontSize={7} fontFamily={M}>2.4 GHz multiprotocol</text>
      <line x1={163} y1={96} x2={267} y2={96} stroke="rgba(0,229,255,0.18)" strokeWidth={0.7}/>
      {["Zigbee (Z-Stack)","BLE 5.0","Thread/OpenThread","Matter (via Thread)","LoRa 2.4 (custom fw)","IEEE 802.15.4"].map((s,i)=>(
        <g key={i}>
          <text x={218} y={110+i*16} textAnchor="middle" fill="rgba(0,229,255,0.45)" fontSize={7} fontFamily={M}>{s}</text>
          <circle cx={162} cy={106+i*16} r={3} fill={i===0?"rgba(0,229,255,0.4)":"rgba(0,229,255,0.12)"} stroke={C.accent} strokeWidth={0.6}/>
        </g>
      ))}
      <text x={215} y={215} textAnchor="middle" fill="rgba(0,229,255,0.3)" fontSize={6} fontFamily={M}>+20dBm PA · SPI+UART · 704KB</text>

      {/* U.FL for CC2652P7 */}
      <circle cx={275} cy={130} r={5} fill="rgba(0,229,255,0.15)" stroke={C.accent} strokeWidth={1}/>
      <text x={275} y={118} textAnchor="middle" fill={C.accent} fontSize={6} fontFamily={M}>U.FL</text>
      <line x1={280} y1={130} x2={330} y2={130} stroke={C.accent} strokeWidth={1.5}/>
      <rect x={330} y={120} width={44} height={20} rx={3} fill="rgba(0,229,255,0.1)" stroke={C.accent} strokeWidth={1}/>
      <text x={352} y={133} textAnchor="middle" fill={C.accent} fontSize={7} fontFamily={M} fontWeight="bold">SMA-ZB</text>
      <text x={352} y={150} textAnchor="middle" fill="rgba(0,229,255,0.5)" fontSize={6} fontFamily={M}>2.4GHz</text>

      {/* SPI to SX1276 */}
      <line x1={100} y1={155} x2={155} y2={155} stroke={C.pink} strokeWidth={2}/>
      <text x={127} y={147} textAnchor="middle" fill="rgba(244,114,182,0.6)" fontSize={7} fontFamily={M}>SPI3</text>

      {/* SX1276 */}
      <rect x={155} y={230} width={120} height={40} rx={4} fill="rgba(244,114,182,0.08)" stroke={C.pink} strokeWidth={1.5}/>
      <text x={215} y={248} textAnchor="middle" fill={C.pink} fontSize={9} fontFamily={M} fontWeight="bold">SX1276</text>
      <text x={215} y={262} textAnchor="middle" fill="rgba(244,114,182,0.5)" fontSize={7} fontFamily={M}>LoRa · FSK · OOK · 915/868MHz</text>
      {/* U.FL for SX1276 */}
      <circle cx={275} cy={250} r={5} fill="rgba(244,114,182,0.15)" stroke={C.pink} strokeWidth={1}/>
      <line x1={280} y1={250} x2={330} y2={250} stroke={C.pink} strokeWidth={1.5}/>
      <rect x={330} y={240} width={44} height={20} rx={3} fill="rgba(244,114,182,0.1)" stroke={C.pink} strokeWidth={1}/>
      <text x={352} y={253} textAnchor="middle" fill={C.pink} fontSize={7} fontFamily={M} fontWeight="bold">SMA-LR</text>
      <text x={352} y={265} textAnchor="middle" fill="rgba(244,114,182,0.5)" fontSize={6} fontFamily={M}>915MHz</text>

      {/* Protocol switch label */}
      <rect x={415} y={80} width={145} height={130} rx={4} fill="rgba(255,255,255,0.02)" stroke="rgba(255,255,255,0.1)" strokeWidth={0.8} strokeDasharray="4 2"/>
      <text x={487} y={97} textAnchor="middle" fill="rgba(255,255,255,0.4)" fontSize={8} fontFamily={M} fontWeight="bold">PROTOCOL SWITCH</text>
      <text x={487} y={110} textAnchor="middle" fill="rgba(255,255,255,0.25)" fontSize={7} fontFamily={M}>(software, one at a time)</text>
      {[["CC2652P7","Zigbee 2.4G (default)","#00e5ff"],["CC2652P7","BLE 5.0","#00e5ff"],["CC2652P7","Thread","#00e5ff"],["CC2652P7","LoRa 2.4G","#00e5ff"],["SX1276","LoRa 915MHz","#f472b6"],["SX1276","Zigbee 915M","#f472b6"]].map(([ic,p,c],i)=>(
        <g key={i}>
          <circle cx={427} cy={125+i*14} r={3} fill={`${c}30`} stroke={c} strokeWidth={0.8}/>
          <text x={434} y={129+i*14} fill={c} fontSize={7} fontFamily={M}>{ic}:</text>
          <text x={475} y={129+i*14} fill="rgba(255,255,255,0.5)" fontSize={7} fontFamily={M}>{p}</text>
        </g>
      ))}

      <text x={VW/2} y={16} textAnchor="middle" fill="rgba(0,229,255,0.25)" fontSize={9} fontFamily={M} letterSpacing="0.1em">ZIGBEE + LoRa RADIO ARCHITECTURE — COMMS-HAT-1 Rev E</text>
    </svg>
  );
}

function ComphatTab(){
  const [proto,setProto]=useState("zigbee_24");
  const protoDefs={
    zigbee_24:{label:"Zigbee 2.4GHz",ic:"CC2652P7",fw:"Z-Stack 3.x · TI SDK",
      rows:[["Frequency","2405–2480 MHz · 16 channels · channel 11–26"],["Modulation","O-QPSK DSSS · 2.4GHz IEEE 802.15.4"],["Data rate","250 kbps raw · ~100kbps application"],["Range","~100m outdoor · ~25m through hull"],["Network","Mesh topology · coordinator / router / end device"],["Max hops","12 (configurable in Z-Stack)"],["Stack","Z-Stack 3.x (TI) · OpenHAB / Zigbee2MQTT compatible"],["Use on drone","Payload sensor telemetry · ground station sensor mesh · smart battery monitoring"]]},
    lora_24:{label:"LoRa 2.4GHz",ic:"CC2652P7",fw:"LoRa 2.4 custom RF firmware (CC2652P7 RF core)",
      rows:[["Frequency","2400–2500 MHz · ISM"],["Modulation","LoRa CSS (via CC2652P7 RF API)"],["Data rate","0.3–200 kbps (configurable SF/BW)"],["Range","~200–500m with 2dBi antenna"],["Stack","Custom LoRaWAN-like framing · not full LoRaWAN"],["Note","2.4GHz LoRa is non-standard — use only for proprietary sensor links, not LoRaWAN infrastructure"],["Use on drone","Short-range encrypted sensor telemetry alternate to MAVLink"]]},
    ble:{label:"BLE 5.0",ic:"CC2652P7",fw:"SimpleLink BLE5 SDK",
      rows:[["Frequency","2402–2480 MHz · 40 channels"],["Data rate","2 Mbps (LE 2M) · 1 Mbps (LE 1M)"],["Range","~40m · +20dBm PA on CC2652P7"],["Stack","TI SimpleLink BLE5 · compatible with Nordic nRF apps"],["Use on drone","Mobile GCS app pairing · local config · parameter set via phone"]]},
    lora_915:{label:"LoRa 915MHz",ic:"SX1276",fw:"LoRaWAN stack (CM4 userspace · LoRaLib)",
      rows:[["Frequency","902–928 MHz · 64+8 channels (US915)"],["Modulation","LoRa CSS · SF7–SF12 · BW 125/250/500 kHz"],["Data rate","0.018–21.9 kbps (SF12 to SF7, BW500)"],["Max TX power","+20 dBm · 100mW"],["Range","1–5 km outdoor · ~500m urban"],["Stack","LoRaWAN Class A · CM4 userspace LoRaLib + arduino-lmic port"],["Use on drone","Long-range backup telemetry · LoRaWAN sensor data relay · range extension fallback"],["Note","SX1276 also handles FSK mode for legacy sensor integration"]]},
    zigbee_915:{label:"Zigbee 915MHz",ic:"SX1276",fw:"SX1276 custom FSK stack (CM4)",
      rows:[["Frequency","902–928 MHz · US915 sub-GHz channels"],["Modulation","O-QPSK via SX1276 FSK mode (software IEEE 802.15.4 PHY)"],["Data rate","~40 kbps effective"],["Range","~300–800m outdoor"],["Stack","Custom sub-GHz 802.15.4 PHY on CM4 · limited ecosystem"],["Note","Sub-GHz Zigbee is uncommon. Prefer LoRa 915MHz unless specific 915MHz Zigbee sensor interop is needed"],["Use on drone","Long-range sensor mesh · sub-GHz Zigbee coordinator"]]},
  };
  const pd=protoDefs[proto];
  return(<div>
    {/* NX enforcement section */}
    <SH t="Log SD Hardware NX Enforcement (Rev E)" mt={0} c={C.orange}/>
    <div style={{border:`1px solid ${C.orange}33`,borderRadius:4,background:"rgba(255,107,53,0.01)",padding:8,marginBottom:16}}>
      <NXDiagram/>
    </div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24,marginBottom:24}}>
      <div>
        <KV k="NX proxy MCU" v="STM32F030F4P6 · SOIC-8 · runs between CM4 SPI1 and log SD"/>
        <KV k="Allowed SPI commands" v="CMD0 · CMD1 · CMD8 · CMD9 · CMD10 · CMD13 · CMD17 · CMD18 · CMD58 · CMD59" vc={C.green}/>
        <KV k="Blocked commands" v="CMD24 · CMD25 · CMD32–38 (all write/erase)" vc={C.red}/>
        <KV k="Audit log" v="STM32 internal 256KB flash · SHA-256 per read block · tamper-evident"/>
        <KV k="STM32 flash" v="Write-protect OTP fuses blown at manufacture — firmware immutable"/>
        <KV k="NX latch" v="74HC74 D flip-flop · SET at POR via 100kΩ pull-up"/>
        <KV k="NX latch clear" v="JP3 · recessed · tool-required (1mm pin) · not software clearable"/>
        <KV k="OS-level NX" v="noexec,nodev,nosuid,ro mount flags · SELinux type=log_storage_t"/>
        <KV k="TrustZone" v="BCM2711 secure monitor enforces noexec on pages from SPI-SD origin"/>
        <KV k="OTP fuse" v="BCM2711 OTP[66] NX bit · burned at provisioning · hardware permanent"/>
      </div>
      <div>
        <Secure ch="The NX enforcement is multi-layer: (1) STM32 SPI proxy physically prevents write commands reaching the SD. (2) 74HC74 hardware latch enables NX mode at POR — can only be cleared by physical tool action. (3) BCM2711 TrustZone secure monitor denies execute permission to any page flagged as originating from the SPI-SD device. (4) OTP fuse permanently marks the device class as non-executable."/>
        <Note c={C.teal} ch="Filesystem navigation is fully permitted. The CM4 can ls, cat, stat, and read any file on the log SD. Only execute() system calls targeting files on this mount point are blocked — enforced simultaneously by the kernel noexec flag, SELinux policy, and the TrustZone secure monitor. An attacker who corrupts the CM4 OS cannot execute payloads stored on the log SD."/>
        <Warn ch="The STM32 audit log fills at approximately 10,000 read-block hashes. When full, it rolls to a FIFO (oldest entries overwritten). For forensic analysis, retrieve the STM32 audit log via its dedicated UART debug port (JP4 on COMMS-HAT-1) before it rolls."/>
      </div>
    </div>

    {/* Zigbee/LoRa section */}
    <SH t="Optional Zigbee + LoRa Radio Module" c={C.accent}/>
    <div style={{background:"rgba(0,229,255,0.04)",border:`1px solid ${C.border}`,borderRadius:4,padding:"8px 12px",marginBottom:14,fontFamily:M,fontSize:10,color:C.dim,lineHeight:1.8}}>
      Both radio ICs are <span style={{color:C.yellow}}>optional population</span> — COMMS-HAT-1 PCB has footprints for both, populated on request. When not populated, their SPI buses are available as general-purpose GPIO. Software protocol selection switches firmware images on CC2652P7 (2.4GHz) and modulation settings on SX1276 (sub-GHz).
    </div>
    <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:8,marginBottom:16}}>
      <ZigbeeDiagram/>
    </div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:16,marginBottom:16}}>
      {PROTO_SHARING.map((p,i)=>(
        <div key={i} style={{padding:"12px 14px",border:`1px solid rgba(0,229,255,0.15)`,borderRadius:4}}>
          <div style={{color:C.accent,fontFamily:M,fontSize:11,fontWeight:"bold",marginBottom:6}}>{p.band} — {p.ic}</div>
          <div style={{marginBottom:8}}>
            {p.proto.map((pr,j)=>(<span key={j} style={{display:"inline-block",padding:"1px 7px",margin:"2px",border:"1px solid rgba(0,229,255,0.3)",color:C.teal,fontFamily:M,fontSize:9,borderRadius:2}}>{pr}</span>))}
          </div>
          <div style={{color:C.dimmer,fontFamily:M,fontSize:9,lineHeight:1.7}}>{p.sel}</div>
        </div>
      ))}
    </div>

    {/* Protocol selector UI */}
    <SH t="Protocol Inspector"/>
    <div style={{display:"flex",gap:5,flexWrap:"wrap",marginBottom:14}}>
      {[["zigbee_24","Zigbee 2.4G",C.accent],["lora_24","LoRa 2.4G",C.teal],["ble","BLE 5.0",C.purple],["lora_915","LoRa 915M",C.pink],["zigbee_915","Zigbee 915M",C.dimmer]].map(([k,l,c])=>(
        <button key={k} onClick={()=>setProto(k)} style={{background:proto===k?`${c}20`:"transparent",border:`1px solid ${proto===k?c:"rgba(0,229,255,0.15)"}`,color:proto===k?c:C.dimmer,padding:"4px 12px",fontFamily:M,fontSize:9,cursor:"pointer",borderRadius:2}}>{l}</button>
      ))}
    </div>
    {pd&&(<div style={{padding:"14px",border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.02)"}}>
      <div style={{display:"flex",gap:12,marginBottom:10,alignItems:"center"}}>
        <span style={{color:C.accent,fontFamily:M,fontSize:12,fontWeight:"bold"}}>{pd.label}</span>
        <span style={{color:C.dim,fontFamily:M,fontSize:10}}>IC: {pd.ic}</span>
        <span style={{color:C.dimmer,fontFamily:M,fontSize:9}}>FW: {pd.fw}</span>
      </div>
      {pd.rows.map(([k,v],i)=>(<KV key={i} k={k} v={v}/>))}
    </div>)}

    <SH t="Software Protocol Selection Flow"/>
    <Note c={C.teal} ch="For CC2652P7: install the desired protocol firmware image via Uniflash or oad_target over-the-air. Z-Stack (Zigbee), SimpleLink BLE5, and OpenThread images are available from TI. Only one image can be active at a time — flashing a new image takes ~30 seconds and requires the drone to be disarmed. The CM4 manages protocol switching via /dev/ttyUSB0 bootloader commands. For SX1276: the modulation mode (LoRa/FSK/OOK) is set by register writes over SPI — switching is instant, no reflash needed. Protocol stack (LoRaLib, custom Zigbee 915) is a CM4 userspace process that is started/stopped via systemctl."/>
  </div>);
}

// ═══════════════════════════════════════════════════════════════
//  REMAINING TABS — condensed from Rev D (Battery, Propulsion,
//  Nav Lights, Antenna, Wiring, BOM, SBOM, Build Guide)
// ═══════════════════════════════════════════════════════════════
// Rev D performance constants (unchanged)
const BASE_70=582, T70=1100, I70=35, BAT_V=18.5, AV_A=2.0;
const CRUISE_A=I70*Math.pow(0.14,1.5)*2+14*0.88+AV_A;
const hovI=(auw)=>I70*Math.pow(auw/2/T70,1.5)*2+AV_A;
function bRow(id,name,mass,cap,Cc,note,payload=0){
  const auw=BASE_70+mass+payload,tw=(T70*2/auw).toFixed(2),ok=T70*2/auw>=2.0;
  const hA=hovI(auw),hMin=(cap/1000*0.8/hA*60).toFixed(1),cMin=(cap/1000*0.8/CRUISE_A*60).toFixed(1);
  return{id,name,mass,cap,Cc,note,auw,tw,ok,hA,hMin,cMin,maxA:cap/1000*Cc,payload};
}
const BATS_E=[bRow("A","5S 2800mAh 45C",271,2800,45,""),bRow("B","5S 3500mAh 45C",328,3500,45,""),bRow("C","5S 4000mAh 35C",376,4000,35,""),bRow("D","5S 4500mAh 35C",420,4500,35,"★ MAX ENDURANCE"),bRow("E","5S 5000mAh 30C",465,5000,30,"C-rating marginal")];
const BATS_C=[bRow("A","5S 1800mAh 75C",190,1800,75,"",250),bRow("B","5S 2200mAh 75C",220,2200,75,"",250),bRow("C","5S 2500mAh 60C",248,2500,60,"",250),bRow("D","5S 2800mAh 45C",271,2800,45,"★ CARGO REC",250),bRow("E","5S 3000mAh 45C",292,3000,45,"T/W marginal",250)];
const REC_E=BATS_E.find(b=>b.id==="D"),REC_C=BATS_C.find(b=>b.id==="D");

function BatRow({b}){return(
  <tr style={{background:b.note.includes("★")?"rgba(74,222,128,0.06)":b.id.charCodeAt(0)%2===0?"rgba(0,229,255,0.02)":"transparent"}}>
    {[b.id,b.name,b.mass+"g",b.cap+"",b.Cc+"C",b.maxA.toFixed(0)+"A",b.auw+"g",b.tw,b.ok?b.hMin+" min":"—",b.ok?b.cMin+" min":"—",b.note||"OK"].map((v,i)=>(
      <td key={i} style={{padding:"5px 8px",color:i===0?C.yellow:i===7?(parseFloat(v)>=2.0?C.green:C.red):i===8?C.yellow:i===9?C.teal:i===10?(v.includes("★")?C.green:v.includes("✗")?C.red:C.dim):C.text,fontWeight:i===7?"bold":"normal",whiteSpace:"nowrap",fontFamily:M,fontSize:10}}>{v}</td>
    ))}
  </tr>
);}

function BatteryTab(){
  const [v,setV]=useState("empty");
  return(<div>
    <div style={{display:"flex",gap:6,marginBottom:14}}>
      {[["empty","Max Empty Endurance"],["cargo","250g Cargo"]].map(([k,l])=>(
        <button key={k} onClick={()=>setV(k)} style={{background:v===k?"rgba(0,229,255,0.09)":"transparent",border:`1px solid ${v===k?C.accent:"rgba(0,229,255,0.14)"}`,color:v===k?C.accent:C.dimmer,padding:"5px 13px",fontFamily:M,fontSize:10,cursor:"pointer",borderRadius:2}}>{l}</button>
      ))}
    </div>
    <div style={{overflowX:"auto",marginBottom:16}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["ID","BATTERY","MASS","CAP","C","MAX A","AUW","T/W","HOVER","CRUISE","NOTE"]}/>
        <tbody>{(v==="empty"?BATS_E:BATS_C).map((b,i)=>(<BatRow key={i} b={b}/>))}</tbody>
      </table>
    </div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t={`Recommended (${v==="empty"?"Empty":"Cargo"}): ${v==="empty"?REC_E.name:REC_C.name}`} mt={0} c={C.green}/>
        {[["AUW",v==="empty"?REC_E.auw:REC_C.auw,"g"],["T/W",v==="empty"?REC_E.tw:REC_C.tw,""],["Hover endurance",v==="empty"?REC_E.hMin:REC_C.hMin,"min"],["Cruise endurance",v==="empty"?REC_E.cMin:REC_C.cMin,"min"],["Max discharge",v==="empty"?REC_E.maxA.toFixed(0):REC_C.maxA.toFixed(0),"A"]].map(([k,v2,u])=>(<KV key={k} k={k} v={`${v2}${u}`}/>))}
      </div>
      <div>
        <Note c={C.green} ch="70mm nacelles (2200g total thrust) provide substantial T/W margin. The 5S 4500mAh 35C at 420g gives best empty endurance at T/W 2.20:1 — 9.4min hover, ~18min cruise."/>
        <Warn ch="Rev E COMMS-HAT-1 adds ~6g (STM32 NX proxy + 74HC74 latch + CC2652P7 + SX1276 + PCB). AUW increases by 6g. All T/W values remain valid — the margin is within rounding error."/>
      </div>
    </div>
  </div>);
}

function PropulsionTab(){return(<div>
  <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
    <div>
      <SH t="70mm Nacelle EDF ×2 (Primary)" mt={0} c={C.orange}/>
      <KV k="Thrust @ 5S" v="~1100g each · 2200g total" vc={C.green}/><KV k="Max current" v="35A each · 70A total"/><KV k="ESC" v="40A BLHeli32 DSHOT300"/><KV k="KV" v="2400–2600KV @ 5S"/><KV k="Nacelle OD" v="~80mm fairing"/><KV k="Sourcing" v="Changesun · Freewing · DYS · HobbyWing" vc={C.green}/>
      <SH t="64mm Alternate (empty missions only)" c={C.dim}/>
      <KV k="Thrust @ 5S" v="~880g each · 1760g total"/><KV k="ESC" v="35A BLHeli32"/><KV k="Note" v="Cannot carry 250g cargo with useful battery" vc={C.red}/>
    </div>
    <div>
      <SH t="40mm Fuselage EDF + Variable Nozzle" mt={0} c={C.yellow}/>
      <KV k="Thrust @ 5S" v="~190g · 140g–220g with nozzle" vc={C.green}/><KV k="ESC" v="25A BLHeli32"/><KV k="KV" v="4000–4500KV"/><KV k="Nozzle base" v="BamJr thing:2991269 remix · CC BY 4.0"/><KV k="Area ratio" v="82% closed (cruise) → 115% open (hover)"/><KV k="Servo" v="SG90 · Pico 2 GP15 · 50Hz PWM"/><KV k="Hull length" v="365mm (+ 5mm vs Rev C for 40mm bell seat)"/>
      <Note c={C.teal} ch="Variable nozzle is optional. Fixed 100% area nozzle works — add variable after initial flight test. Attribution required on remix: 'BamJr / thingiverse.com/thing:2991269 CC BY 4.0'."/>
    </div>
  </div>
</div>);}

function NavLightsTab(){
  const lights=[["PORT","#ff2020","Red","Left nacelle tip","≥110°","Steady","ICAO Ann.2"],["STBD","#00cc00","Green","Right nacelle tip","≥110°","Steady","ICAO Ann.2"],["TAIL","#dddddd","White","Aft hull 350mm","≥140°","Steady","ICAO Ann.2"],["ACOL","#ff4444","Red","Dorsal hull 120mm","360°","60 FPM","14CFR91.209"],["BELLY","#ffffaa","White","Belly hull 160mm","lower","60 FPM","FAA AC91-74"],["LAND","#ffff80","White","Nose under 30mm","fwd","Ops steady","FAA AC20-74"]];
  return(<div>
    <Note c={C.accent} ch="6× WS2812C-2020 RGB LEDs on single data line (Pico 2 GP26 · PIO0 · 800kHz NZR). All ICAO Annex 2 + 14 CFR 91.209 + FAA AC 107-2B compliant. Total LED power: ≤180mA at full white."/>
    <div style={{overflowX:"auto",marginBottom:16}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["LIGHT","COLOR","POSITION","ARC","FLASH","REGULATION"]}/>
        <tbody>{lights.map(([id,col,name,pos,arc,flash,reg],i)=>(<tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.02)":"transparent"}}>
          <td style={{padding:"5px 9px",color:col,fontWeight:"bold"}}>{id}</td>
          <td style={{padding:"5px 9px"}}><span style={{background:col,color:"#000",padding:"1px 6px",borderRadius:2,fontSize:9}}>{name}</span></td>
          <td style={{padding:"5px 9px",color:C.text}}>{pos}</td>
          <td style={{padding:"5px 9px",color:C.dim}}>{arc}</td>
          <td style={{padding:"5px 9px",color:flash.includes("FPM")?C.orange:C.green}}>{flash}</td>
          <td style={{padding:"5px 9px",color:C.dimmer,fontSize:9}}>{reg}</td>
        </tr>))}</tbody>
      </table>
    </div>
  </div>);
}

function AntennaTab(){
  return(<div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="GPS L1 · 58mm · cockpit roof" mt={0} c="#4ade80"/>
        <KV k="Type" v="25×25mm RHCP ceramic patch · 12mm standoff"/><KV k="Cable" v="U.FL → RG-178 ≤100mm → TRIHAT-1"/><KV k="Separation GPS↔49MHz" v="232mm ✔" vc={C.green}/>
        <SH t="SiK 915MHz · 238mm · belly" c={C.orange}/>
        <KV k="Type" v="λ/4 monopole 82mm · SMA-RP bulkhead"/><KV k="Mount" v="6.5mm hole · PETG belly · clear zone 200–255mm"/>
        <SH t="49MHz RCRS · 290mm · dorsal fin" c={C.pink}/>
        <KV k="Type" v="250mm whip + 38μH coil · 4× 150mm radials"/><KV k="Mount" v="Serenity aft dorsal spine integration · PETG fin"/><KV k="SWR" v="≤2.5:1 across 49.83–49.89MHz"/>
      </div>
      <div>
        <SH t="WiFi 2.4GHz · SMA-1 on CM4-CARRIER-1 (Rev E)" mt={0} c={C.orange}/>
        <KV k="Path" v="CM4 BCM43455 U.FL → MABD-011028 diplexer → SMA-1"/>
        <KV k="Ant. type" v="External 2.4GHz omni · 2–5dBi · SMA female"/>
        <KV k="Replaces" v="Internal PCB trace antenna (auto-disabled when U.FL loaded)"/>
        <KV k="Range improvement" v="~3–5× vs internal trace (50–80m → 200–400m outdoors)"/>
        <SH t="WiFi 5GHz · SMA-2 on CM4-CARRIER-1 (Rev E)" c={C.purple}/>
        <KV k="Path" v="CM4 BCM43455 U.FL → diplexer → SMA-2"/>
        <KV k="Ant. type" v="External 5GHz patch/panel · 3–8dBi · SMA female"/>
        <KV k="Use" v="High-bandwidth log streaming to ground station laptop"/>
        <SH t="Zigbee 2.4GHz · SMA-ZB on COMMS-HAT-1 (opt)" c={C.accent}/>
        <KV k="Path" v="CC2652P7 U.FL → SMA-ZB connector"/><KV k="Ant. type" v="2.4GHz whip/PCB · 2dBi"/>
        <SH t="LoRa 915MHz · SMA-LR on COMMS-HAT-1 (opt)" c={C.pink}/>
        <KV k="Path" v="SX1276 U.FL → SMA-LR connector"/><KV k="Ant. type" v="915MHz λ/4 whip · 2dBi"/>
      </div>
    </div>
    <Warn ch="Four SMA connectors now on the aircraft (SMA-1 WiFi 2.4G on carrier, SMA-2 WiFi 5G on carrier, SMA-ZB Zigbee 2.4G on COMMS-HAT, SMA-LR LoRa 915M on COMMS-HAT). Review separation and verify no inter-antenna interference before first flight. SMA-ZB and SMA-1 are both 2.4GHz — minimum 150mm physical separation required."/>
  </div>);
}

function WiringTab(){
  return(<div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="Ethernet · TRIHAT-1 J3 ↔ COMMS-HAT-1 J2" mt={0} c={C.purple}/>
        <KV k="Connector" v="JST-GH 1.25mm 6-pin · 150mm"/><KV k="Pins" v="GND · TX+ · TX− · RX+ · RX− · N/C"/>
        <KV k="IP" v="Pico 192.168.10.1 · CM4 192.168.10.2"/><KV k="MAVLink" v="UDP 14550 · Log UDP 14551 · Config TCP 8080"/>
        <SH t="CAN FD · TRIHAT-1 J2 ↔ COMMS-HAT-1 J1" c={C.orange}/>
        <KV k="Connector" v="JST-GH 1.25mm 4-pin · 120mm"/><KV k="Pins" v="GND · +5V · CANH · CANL"/>
        <KV k="Termination" v="120Ω at TRIHAT-1 only · COMMS-HAT-1 open"/><KV k="Rate" v="1Mbps / 4Mbps FD"/>
      </div>
      <div>
        <SH t="Rev E New Signal Lines" mt={0} c={C.lime}/>
        <KV k="CPLD write-blocker" v="JP2 jumper on carrier board edge · 2-pin 2.54mm"/>
        <KV k="CPLD LED indicators" v="LED1 (green WB) + LED2 (red blocked) · carrier top face"/>
        <KV k="NX latch" v="74HC74 on COMMS-HAT-1 · SET at POR · JP3 override (recessed)"/>
        <KV k="STM32 NX proxy UART" v="JP4 4-pin JST-GH on COMMS-HAT-1 · audit log readout"/>
        <KV k="CC2652P7 SPI" v="COMMS-HAT-1 SPI2 · GPIO 22-26 · IRQ GPIO 22"/>
        <KV k="SX1276 SPI" v="COMMS-HAT-1 SPI3 · GPIO 27-31 · DIO0 IRQ GPIO 27"/>
        <KV k="Variable nozzle servo" v="Pico 2 GP15 → SG90 in engine bell · 28AWG 3-core"/>
        <KV k="WiFi SMA-1 cable" v="CM4 U.FL → MABD-011028 · 0.81mm coax ≤25mm"/>
        <KV k="WiFi SMA-2 cable" v="MABD-011028 output → SMA-2 · 50Ω microstrip ≤12mm"/>
      </div>
    </div>
  </div>);
}

// ═══════════════════════════════════════════════════════════════
//  BOM — Rev E
// ═══════════════════════════════════════════════════════════════
const BOM=[
  // Propulsion (unchanged from Rev D)
  {cat:"Propulsion",qty:2,ref:"EDF-70",part:"70mm EDF + 2500KV BLDC",desc:"1100g thrust @ 5S · 35A · Changesun/Freewing",est:"$26ea"},
  {cat:"Propulsion",qty:2,ref:"ESC-40",part:"40A BLHeli32 ESC",desc:"DSHOT300 · 2–6S",est:"$20ea"},
  {cat:"Propulsion",qty:1,ref:"EDF-40",part:"40mm EDF + 4200KV BLDC",desc:"190g thrust @ 5S · 14A",est:"$16"},
  {cat:"Propulsion",qty:1,ref:"ESC-25",part:"25A BLHeli32 ESC",desc:"Fwd fan ESC",est:"$12"},
  {cat:"Propulsion",qty:2,ref:"SRV-T",part:"MG90S digital servo",desc:"Nacelle tilt · 1.8kg·cm",est:"$4ea"},
  {cat:"Propulsion",qty:1,ref:"SRV-N",part:"SG90 servo (variable nozzle)",desc:"Area ratio 82–115%",est:"$3"},
  {cat:"Propulsion",qty:1,ref:"NOZZLE",part:"Variable nozzle (BamJr remix CC BY 4.0)",desc:"CF-PETG inner · PETG flaps · 40mm ID",est:"$3 filament"},
  // Flight control
  {cat:"Flt Ctrl",qty:1,ref:"PICO2",part:"Raspberry Pi Pico 2",desc:"RP2350 · 264KB · 4MB flash",est:"$5"},
  {cat:"Flt Ctrl",qty:1,ref:"TH1",part:"TRIHAT-1 (custom PCB)",desc:"65×48mm · IMU+Baro+GPS+CAN+ETH+TPM+FPV",est:"$75"},
  {cat:"Flt Ctrl",qty:1,ref:"AIRS",part:"MS4525DO airspeed sensor",desc:"I²C · ±1PSI · 0–80m/s",est:"$10"},
  {cat:"Flt Ctrl",qty:1,ref:"PITOT",part:"CF pitot 3mm + silicone tubing",desc:"80mm tube · 2×80mm leads",est:"$4"},
  // Companion — CM4-CARRIER-1 Rev E
  {cat:"Companion",qty:1,ref:"CM4",part:"CM4 Lite 4GB WiFi",desc:"BCM2711 · 4×A72 · 4GB LPDDR4X · 802.11ac",est:"$55"},
  {cat:"Companion",qty:1,ref:"CAR1E",part:"CM4-CARRIER-1 Rev E (custom PCB 65×52mm)",desc:"Write-blocker CPLD · diplexer · 2× SMA · DF40 · μSD · USB hub",est:"$28"},
  {cat:"Companion",qty:1,ref:"MXO2",part:"Lattice MachXO2-256ZE CPLD",desc:"TQFP-32 · SDIO write-blocker",est:"$3.50"},
  {cat:"Companion",qty:1,ref:"MABD",part:"MABD-011028 WiFi diplexer",desc:"SOT-26 · 2.4/5GHz split · 0.3dB IL",est:"$2"},
  {cat:"Companion",qty:2,ref:"SMA-W",part:"SMA female edge-mount connector",desc:"SMA-1 (2.4GHz) + SMA-2 (5GHz) · rated to 6GHz",est:"$1.50ea"},
  {cat:"Companion",qty:1,ref:"CH1E",part:"COMMS-HAT-1 Rev E (custom PCB)",desc:"NX latch + STM32 proxy + CC2652P7 + SX1276 footprints",est:"$68"},
  {cat:"Companion",qty:1,ref:"STM32",part:"STM32F030F4P6 (NX proxy MCU)",desc:"SOIC-8 · SPI proxy · SHA-256 audit",est:"$1.20"},
  {cat:"Companion",qty:1,ref:"HC74",part:"74HC74D dual D flip-flop",desc:"NX latch IC · SOT-23-6",est:"$0.30"},
  {cat:"Companion",qty:1,ref:"CC2652",part:"CC2652P7 (opt — Zigbee/BLE/LoRa 2.4GHz)",desc:"TI multiprotocol 2.4GHz · +20dBm PA · SPI",est:"$5"},
  {cat:"Companion",qty:1,ref:"SX1276",part:"SX1276 (opt — LoRa/Zigbee 915MHz)",desc:"Semtech LoRa/FSK/OOK · 100mW · SPI",est:"$4"},
  {cat:"Companion",qty:2,ref:"SMA-R",part:"SMA female edge-mount (radio antennas)",desc:"SMA-ZB (2.4GHz Zigbee) + SMA-LR (915MHz LoRa)",est:"$1.50ea"},
  {cat:"Companion",qty:1,ref:"SIK",part:"SiK 915MHz air unit",desc:"MAVLink 2.0 · 100mW · UART",est:"$18"},
  {cat:"Companion",qty:1,ref:"RCRS",part:"49MHz RCRS transceiver",desc:"TDDS · 6-ch · 10mW EIRP",est:"$16"},
  // Nav lights
  {cat:"Nav Lights",qty:6,ref:"WS2812",part:"WS2812C-2020 RGB LED",desc:"5V · 2×2mm · addressable · ICAO compliant",est:"$0.50ea"},
  // Payload
  {cat:"Payload",qty:1,ref:"SRV-R",part:"SG90 release servo",desc:"Spring-return closed",est:"$3"},
  {cat:"Payload",qty:1,ref:"WINCH",part:"N20 6V 100:1 gearmotor",desc:"Winch drive",est:"$5"},
  {cat:"Payload",qty:1,ref:"DRV",part:"DRV8833 H-bridge module",desc:"Dual 1.5A winch control",est:"$3"},
  {cat:"Payload",qty:1,ref:"SPOOL",part:"18mm spool + 5m Dyneema SK75",desc:"40kg break strength",est:"$6"},
  // Power — dual battery options
  {cat:"Power",qty:1,ref:"BAT-E",part:"★ 5S 4500mAh 35C (empty endurance)",desc:"420g · T/W 2.20 · 9.4min hover",est:"$45"},
  {cat:"Power",qty:1,ref:"BAT-C",part:"★ 5S 2800mAh 45C (cargo 250g)",desc:"271g · T/W 2.01 · 6.2min hover",est:"$38"},
  {cat:"Power",qty:1,ref:"BEC",part:"5V 3A switching BEC",desc:"CM4+Pico+servos+radios+LEDs",est:"$5"},
  {cat:"Power",qty:1,ref:"PDIST",part:"XT60 distribution board",desc:"4× XT30 · 12AWG mains",est:"$8"},
  // Airframe (365mm scale)
  {cat:"Airframe",qty:1,ref:"HULL",part:"Serenity hull 365mm PETG (11 prints)",desc:"CC BY 4.0 hull · ~148g · 8% gyroid",est:"$19 filament"},
  {cat:"Airframe",qty:2,ref:"NAC",part:"70mm nacelle pods CF-PETG 80mm OD",desc:"LED recess · pivot seat",est:"$7 filament"},
  {cat:"Airframe",qty:1,ref:"BELL",part:"Serenity engine bell PETG 365mm",desc:"70mm ID · nozzle housing",est:"$5 filament"},
  {cat:"Airframe",qty:1,ref:"KEEL",part:"CF keel 6×3mm × 385mm",desc:"Dorsal structural spine",est:"$6"},
  {cat:"Airframe",qty:2,ref:"SPAR",part:"CF tube 12mm OD × 300mm",desc:"Outrigger wing spars",est:"$8ea"},
  {cat:"Airframe",qty:4,ref:"SKID",part:"TPU 95A skid feet",desc:"Crash-absorbing pads",est:"$2 filament"},
  {cat:"Airframe",qty:1,ref:"HW",part:"M2/M2.5/M3 hardware assortment",desc:"Standoffs · screws · heat-set inserts",est:"$8"},
  // Wiring
  {cat:"Wiring",qty:1,ref:"JSTKIT",part:"JST-GH 1.25mm kit",desc:"4+6pin · crimp tool",est:"$14"},
  {cat:"Wiring",qty:1,ref:"ETH-C",part:"6-pin JST-GH Ethernet cable 150mm",desc:"TRIHAT↔COMMS-HAT",est:"$4"},
  {cat:"Wiring",qty:1,ref:"CAN-C",part:"4-pin JST-GH CAN FD cable 120mm",desc:"Twisted CANH/CANL",est:"$3"},
  {cat:"Wiring",qty:1,ref:"WIRE",part:"Silicone wire assortment",desc:"12AWG power · 22AWG signal · 28AWG data",est:"$12"},
  {cat:"Wiring",qty:1,ref:"XT60P",part:"XT60 connector pair",desc:"Battery to power board",est:"$2"},
];
const CAT_COL={Propulsion:C.orange,"Flt Ctrl":C.accent,Companion:C.green,"Nav Lights":C.yellow,Payload:C.pink,Power:C.yellow,Airframe:C.teal,Wiring:C.purple};
const CATS=[...new Set(BOM.map(b=>b.cat))];

function BomTab(){
  const [cf,setCf]=useState("All");
  const rows=cf==="All"?BOM:BOM.filter(b=>b.cat===cf);
  return(<div>
    <div style={{display:"flex",gap:5,flexWrap:"wrap",marginBottom:12}}>
      {["All",...CATS].map(c=>(<button key={c} onClick={()=>setCf(c)} style={{background:cf===c?`${CAT_COL[c]||C.accent}20`:"transparent",border:`1px solid ${cf===c?CAT_COL[c]||C.accent:"rgba(0,229,255,0.14)"}`,color:cf===c?CAT_COL[c]||C.accent:C.dimmer,padding:"3px 10px",fontFamily:M,fontSize:9,cursor:"pointer",borderRadius:2}}>{c}</button>))}
    </div>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["CAT","QTY","REF","COMPONENT","DESCRIPTION","~USD"]}/>
        <tbody>{rows.map((b,i)=>(<tr key={i} style={{background:b.part.includes("★")?"rgba(74,222,128,0.06)":i%2===0?"rgba(0,229,255,0.02)":"transparent",verticalAlign:"top"}}>
          <td style={{padding:"5px 8px"}}><span style={{color:CAT_COL[b.cat]||C.dim,border:`1px solid ${CAT_COL[b.cat]||C.dim}40`,padding:"1px 5px",borderRadius:2,fontSize:9,whiteSpace:"nowrap"}}>{b.cat}</span></td>
          <td style={{padding:"5px 8px",color:C.accent,fontWeight:"bold",textAlign:"center"}}>{b.qty}</td>
          <td style={{padding:"5px 8px",color:C.yellow,fontSize:9,whiteSpace:"nowrap"}}>{b.ref}</td>
          <td style={{padding:"5px 8px",color:C.text,whiteSpace:"nowrap"}}>{b.part}</td>
          <td style={{padding:"5px 8px",color:C.dim,fontSize:9,lineHeight:1.5}}>{b.desc}</td>
          <td style={{padding:"5px 8px",color:C.green,fontWeight:"bold",whiteSpace:"nowrap"}}>{b.est}</td>
        </tr>))}</tbody>
        {cf==="All"&&(<tfoot><tr style={{borderTop:`1px solid ${C.border}`}}><td colSpan={5} style={{padding:"8px 8px",color:C.accent,textAlign:"right",fontSize:11}}>TOTAL ESTIMATED (select one battery; CC2652P7+SX1276 optional)</td><td style={{padding:"8px 8px",color:C.yellow,fontSize:16,fontWeight:"bold"}}>$640–740</td></tr></tfoot>)}
      </table>
    </div>
    <Note c={C.dim} ch="Rev E delta vs Rev D: +$40–50 for CPLD write-blocker, diplexer, 2× additional SMA connectors, STM32 NX proxy, 74HC74 latch, and PCB redesign for CM4-CARRIER-1 and COMMS-HAT-1. CC2652P7 + SX1276 are optional and add $9 if populated. Hull: Peter Farell CC BY 4.0. Nozzle: BamJr CC BY 4.0."/>
  </div>);
}

// ─── SBOM Rev E ───────────────────────────────────────────────
const SBOM=[
  {sys:"Pico 2",layer:"Core",     comp:"Pico SDK 2.x",            ver:"≥2.0",  lic:"BSD-3",   role:"RP2350 HAL · PIO · DMA · multicore"},
  {sys:"Pico 2",layer:"AHRS",     comp:"Mahony AHRS (port)",      ver:"custom",lic:"Apache-2", role:"Gyro+accel → quaternion · 500Hz"},
  {sys:"Pico 2",layer:"Control",  comp:"Custom PID cascade",      ver:"v1.0",  lic:"Propr.",  role:"Rate/attitude/position PID · 500Hz"},
  {sys:"Pico 2",layer:"Protocol", comp:"MAVLink 2.0 C lib",       ver:"2.0",   lic:"MIT",     role:"MAVLink over UART1 + W5500 UDP"},
  {sys:"Pico 2",layer:"Driver",   comp:"ICM-42688-P · BMP388 · MS4525DO · M10Q · MCP2518FD · W5500 · TPM · WS2812 · DSHOT300",ver:"custom",lic:"BSD-3/MIT",role:"All sensor and peripheral drivers"},
  {sys:"Pico 2",layer:"Algorithm",comp:"TDDS channel selector",   ver:"v1.0",  lic:"Propr.",  role:"49MHz RCRS TDDS · SNR scan"},
  {sys:"Pico 2",layer:"Algorithm",comp:"Variable nozzle controller",ver:"v1.0",lic:"Propr.",  role:"Area ratio schedule · transition interp · GP15 PWM"},
  {sys:"CM4",   layer:"OS",       comp:"RPi OS Lite 64-bit",      ver:"bookworm",lic:"Mixed GPL","role":"Debian Linux headless · kernel 6.6+"},
  {sys:"CM4",   layer:"Middleware",comp:"mavlink-router + MAVSDK", ver:"≥3.0/2.0",lic:"Apache-2/BSD-3",role:"MAVLink router · drone API"},
  {sys:"CM4",   layer:"Middleware",comp:"python-can + dronecan + pymavlink",ver:"≥4.0/1.0/2.4",lic:"LGPL/MIT/LGPL",role:"CAN FD bus · DroneCAN · MAVLink logging"},
  {sys:"CM4",   layer:"Security", comp:"tpm2-tools + tpm2-tss",   ver:"≥5.0/4.0",lic:"BSD-2", role:"TPM 2.0 provisioning + attestation"},
  {sys:"CM4",   layer:"Security", comp:"SELinux policy (custom)",  ver:"v1.0",  lic:"GPL-2",   role:"log_storage_t type · noexec enforcement · NX policy"},
  {sys:"CM4",   layer:"Security", comp:"TrustZone secure monitor", ver:"custom",lic:"Propr.",  role:"BCM2711 TrustZone · hardware NX for SPI-SD origin pages"},
  {sys:"CM4",   layer:"Driver",   comp:"SX1276 LoRaLib",           ver:"≥5.0",  lic:"MIT",     role:"LoRa/FSK modulation · 915MHz sub-GHz protocol selection"},
  {sys:"CM4",   layer:"Driver",   comp:"CC2652P7 Z-Stack / BLE / Thread", ver:"TI SDK",lic:"TI TSPA",role:"2.4GHz protocol images — one active at a time"},
  {sys:"CM4",   layer:"Comms",    comp:"SiK firmware (air unit)",  ver:"2.x",   lic:"GPL-3",   role:"915MHz MAVLink radio"},
  {sys:"CPLD",  layer:"RTL",      comp:"Write-blocker Verilog",    ver:"v1.0",  lic:"MIT",     role:"MachXO2-256 SDIO CMD filter · WP_VIOLATION response injection"},
  {sys:"STM32", layer:"Firmware", comp:"NX proxy firmware",        ver:"v1.0",  lic:"MIT",     role:"SPI proxy · SHA-256 audit log · CMD24/25/32-38 block · WP OTP fuses"},
  {sys:"GCS",   layer:"App",      comp:"QGroundControl",           ver:"≥4.3",  lic:"GPL-3",   role:"Flight planning · telemetry · params"},
];
const SBOM_SYS=[...new Set(SBOM.map(s=>s.sys))];
const LAYER_COL={Core:C.accent,AHRS:C.teal,Control:C.orange,Protocol:C.orange,Driver:C.teal,Algorithm:C.pink,OS:C.green,Middleware:C.purple,Security:C.yellow,Comms:C.accent,App:C.green,RTL:C.lime,Firmware:C.orange};

function SbomTab(){
  const [sf,setSf]=useState("All");
  const rows=sf==="All"?SBOM:SBOM.filter(s=>s.sys===sf);
  return(<div>
    <div style={{display:"flex",gap:5,flexWrap:"wrap",marginBottom:12}}>
      {["All",...SBOM_SYS].map(s=>(<button key={s} onClick={()=>setSf(s)} style={{background:sf===s?"rgba(0,229,255,0.09)":"transparent",border:`1px solid ${sf===s?C.accent:"rgba(0,229,255,0.14)"}`,color:sf===s?C.accent:C.dimmer,padding:"3px 10px",fontFamily:M,fontSize:9,cursor:"pointer",borderRadius:2}}>{s}</button>))}
    </div>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["SYSTEM","LAYER","COMPONENT","VERSION","LICENSE","ROLE"]}/>
        <tbody>{rows.map((s,i)=>(<tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.02)":"transparent",verticalAlign:"top"}}>
          <td style={{padding:"5px 8px",color:s.sys==="Pico 2"?C.accent:s.sys==="CM4"?C.green:s.sys==="CPLD"?C.lime:s.sys==="STM32"?C.orange:C.purple,fontWeight:"bold",whiteSpace:"nowrap",fontSize:9}}>{s.sys}</td>
          <td style={{padding:"5px 8px"}}><span style={{color:LAYER_COL[s.layer]||C.dim,border:`1px solid ${LAYER_COL[s.layer]||C.dim}40`,padding:"1px 5px",borderRadius:2,fontSize:8,whiteSpace:"nowrap"}}>{s.layer}</span></td>
          <td style={{padding:"5px 8px",color:C.text,whiteSpace:"nowrap"}}>{s.comp}</td>
          <td style={{padding:"5px 8px",color:C.dimmer,whiteSpace:"nowrap",fontSize:9}}>{s.ver}</td>
          <td style={{padding:"5px 8px",color:C.yellow,whiteSpace:"nowrap",fontSize:9}}>{s.lic}</td>
          <td style={{padding:"5px 8px",color:C.dim,fontSize:9,lineHeight:1.5}}>{s.role}</td>
        </tr>))}</tbody>
      </table>
    </div>
    <Note c={C.lime} ch="CPLD Verilog write-blocker and STM32 NX proxy firmware are both MIT licensed and included in the project repository. GPL-3 (SiK, QGC) must remain open if redistributed. TI CC2652P7 Z-Stack uses TI's TSPA license — check terms before commercial distribution. All CC BY 4.0 components (hull, nozzle) require attribution in derivative works."/>
  </div>);
}

// ─── BUILD GUIDE (condensed — key Rev E additions highlighted) ─
const BUILD_ADDITIONS=[
  {t:"Install CPLD write-blocker (CM4-CARRIER-1)",c:C.lime,d:"The MachXO2-256ZE ships unprogrammed. Before board assembly: use a JTAG programmer (USB-Blaster or FT2232H breakout) to flash the write-blocker Verilog bitstream via ispDownload. Verify: insert a microSD, remove JP2 (WB disabled), verify OS installs normally. Replace JP2: verify OS mounts read-only and LED1 (green) lights."},
  {t:"Install diplexer and SMA connectors (CM4-CARRIER-1)",c:C.purple,d:"Solder MABD-011028 diplexer at U_DIP footprint. Solder two SMA edge-mount connectors at J_SMA1 (2.4GHz, orange-marked) and J_SMA2 (5GHz, purple-marked). Route 0.81mm semi-rigid coax from CM4 U.FL to diplexer input (≤25mm). Verify 50Ω impedance with a VNA before attaching antennas."},
  {t:"Install STM32 NX proxy and 74HC74 latch (COMMS-HAT-1)",c:C.orange,d:"Flash STM32F030F4P6 via SWD (ST-LINK V2) with nx_proxy.bin from the project repo. Burn write-protect OTP fuses via STM32CubeProgrammer (OB → Flash protection → set WRP to all sectors). After fuse blow, verify flash is read-protected. Install 74HC74 at U_NX footprint. At POR, NX_Q pin should read HIGH — verify with multimeter before first boot."},
  {t:"Populate CC2652P7 and SX1276 (optional — COMMS-HAT-1)",c:C.accent,d:"If Zigbee/LoRa is required: solder CC2652P7 at U_ZB footprint and SX1276 at U_LR footprint. Flash CC2652P7 with Z-Stack Zigbee image using Uniflash over JTAG. Test SX1276 with LoRaLib example sketch. Fit U.FL pigtails to SMA-ZB and SMA-LR board-edge connectors."},
  {t:"Verify multi-layer NX operation",c:C.lime,d:"Boot CM4. Check /proc/mounts: log-SD should show 'noexec,nodev,nosuid,ro'. Check SELinux context: ls -Z /mnt/log — should show 'system_u:object_r:log_storage_t:s0'. Attempt to execute a test binary copied to log-SD: should fail with EACCES. Read STM32 audit log via JP4 serial at 115200 baud: should show SHA-256 entries for boot reads. Verify TrustZone monitor active: cat /proc/device-tree/secure-chosen."},
];

function BuildGuideTab(){
  const [open,setOpen]=useState(null);
  const phases=[
    {p:"PHASE 1 · PRINT PREP",c:C.teal,steps:["Source PETG (300g), CF-PETG (80g), TPU 95A (40g). Dry all 6h at 65°C.","Install hardened steel 0.4mm nozzle for CF-PETG. Calibrate E-steps and PA.","Slice hull in 5 sections: nose cap (0–22mm), cockpit (22–90mm), mid-hull L+R halves (90–230mm), aft-hull (230–270mm), engine bell (270–365mm). 8% gyroid, 2 perimeters, 0.20mm.","Print TPU skid feet first. Then PETG hull sections overnight. Then CF-PETG nacelle pods and tilt brackets.","Dry-fit all sections. Test nacelle bearing press-fit. Sand mating surfaces 220-grit."]},
    {p:"PHASE 2 · CF SKELETON",c:C.accent,steps:["Cut CF keel 6×3mm × 385mm. Mark datums at 90, 130, 160, 200, 290, 365mm.","Cut 2× 12mm CF tube × 300mm outrigger spars. Sand tenon 8mm dia × 25mm at one end.","Epoxy mid-hull to keel. Cure 12h. Do not bond cockpit cap or engine bell — must be removable.","Epoxy CF-PETG spar junction bracket at 130mm. Check 90° alignment. Press-fit outrigger spars."]},
    {p:"PHASE 3 · NACELLE ASSEMBLY",c:C.orange,steps:["Press 8×5×2.5mm bearings into nacelle pivot sockets.","Thread 8mm CF pivot rod through spar bracket → bearing → nacelle. Secure with M3 set screw + Loctite 243.","Install 70mm EDF into nacelle pod. Route motor leads through hollow CF spar.","Mount MG90S tilt servo to CF-PETG bracket. Connect servo horn to nacelle push-rod at 18mm radius.","Install WS2812C-2020 LED into nacelle tip cap PETG lens recess (port=red, stbd=green). Epoxy, seal."]},
    {p:"PHASE 4 · ELECTRONICS",c:C.purple,steps:["Mount Pico 2 + TRIHAT-1 stack at 60–90mm on cockpit CF bulkhead plate (55×38mm 2mm CF, cut to fit).","Mount CM4 stack (CM4 + CM4-CARRIER-1 Rev E + COMMS-HAT-1 Rev E) at 95–160mm avionics bay floor. Install OS μSD in carrier slot, log μSD in COMMS-HAT slot.","Connect GPS U.FL coax to TRIHAT-1, route to cockpit roof GPS patch antenna.","Install 3× ESCs on keel underside with double-sided foam + M2.5 screw. Route motor leads in channels.","Install SiK radio and 49MHz RCRS. Route coax pigtails to belly SMA and dorsal antenna fin.","Install MABD-011028 diplexer on CM4-CARRIER-1. Fit U.FL coax from CM4 module antenna port. Fit 2× SMA antennas to SMA-1 (2.4G) and SMA-2 (5G) on board edge."]},
    {p:"PHASE 5 · VARIABLE NOZZLE",c:C.yellow,steps:["Print CF-PETG inner ring vertically. Print PETG flaps flat. Test-fit ring in housing.","Insert M1.5×8mm pivot pins through flaps. Lubricate pins with sewing machine oil.","Install taller inner ring variant for greater expansion range.","Mount SG90 to M2.5 boss on outer housing. Attach 1.5mm pushrod (18mm throw).","Bayonet-lock nozzle into engine bell. Route servo cable to Pico 2 GP15.","Calibrate: 1.0ms → target 42mm exit dia. 2.0ms → target 36mm exit dia. Adjust pushrod clevis."]},
    {p:"PHASE 6 · WIRING & SECURITY SETUP",c:C.lime,steps:["Flash CPLD write-blocker bitstream via USB-Blaster. Install JP2. Verify LED1 (green) lights on OS-SD boot.","Flash STM32F030 with nx_proxy.bin via SWD. Burn OTP write-protect fuses. Verify NX_LATCH = HIGH at POR.","If CC2652P7 populated: flash Z-Stack image via Uniflash. If SX1276 populated: verify SPI comms with LoRaLib.","Solder power bus. Install BEC. Verify 5V ± 0.1V under load. Connect JST-GH Ethernet cable (150mm) and CAN FD cable (120mm) between TRIHAT-1 and COMMS-HAT-1.","Install all nav lights. Verify WS2812 chain (GP26 PIO). Test all 6 light states.","First power-on bench test: verify no shorts, all regulators in range, all boards booting, MAVLink heartbeat in QGC."]},
    {p:"PHASE 7 · SOFTWARE & CALIBRATION",c:C.pink,steps:["Flash Pico 2 firmware (USB drag-drop). Verify 1Hz heartbeat LED.","Boot CM4. SSH in. apt install mavlink-router mavsdk pymavlink python-can dronecan tpm2-tools tpm2-tss. Configure mavlink-router.","Configure SELinux: label log-SD mount point as log_storage_t. Mount with noexec,nodev,nosuid,ro. Verify EACCES on test binary exec.","Provision TPM: tpm2_createprimary, tpm2_create, tpm2_load. Store handle for runtime attestation.","Calibrate ESCs (no props). Calibrate nacelle servos to ±0.5° accuracy at 0° and 90°.","Calibrate variable nozzle: verify 36mm (closed) and 42mm (open) exit diameters. Lock pushrod with Loctite 243."]},
    {p:"PHASE 8 · GROUND TEST",c:C.lime,steps:["Static CG balance: 152mm from nose. Slide battery rail to achieve. Load 250g payload: slide battery 10mm aft.","Radio link: verify MAVLink heartbeat, attitude response, RC channels in QGC. Verify TDDS channel selection ≤30s power-on.","Bench thrust tethered: 30% throttle per nacelle. Verify ≥330g per 70mm fan.","Nozzle function: command open (42mm) / closed (36mm). Verify smooth cam action, no servo bind.","Nav lights: verify all 6 lights correct colours and flash patterns per firmware states.","GPS / sensor: outdoors, verify HDOP ≤1.5, ≥6 sats. Spin EDFs: verify HDOP does not degrade >0.3."]},
    {p:"PHASE 9 · FIRST FLIGHT",c:C.green,steps:["Pre-flight ABCD: Airframe · Battery · Communications · Documentation (Part 107 cert, registration, NOTAM).","Hover 1m AGL, 30s. Land. Inspect all fasteners and ESC temps (target <60°C).","Hover 3m: test ±10° roll/pitch/yaw inputs. Verify altitude hold. Record hover amperage (expect within ±10% of calculated).","Transition test ≥8m AGL: nacelle sweep. Monitor altitude (expect ±1.5m). Verify nozzle closes during sweep.","Cargo test: 250g payload. Verify clean lift. Test winch deploy at 4m: payload descends at ~15cm/s. Retract and land."]},
  ];

  return(<div>
    <div style={{background:"rgba(163,230,53,0.05)",border:`1px solid rgba(163,230,53,0.2)`,borderRadius:4,padding:"10px 14px",marginBottom:16,fontFamily:M,fontSize:11,color:C.dim}}>
      <span style={{color:C.lime,fontWeight:"bold"}}>Rev E additions to build sequence</span> are highlighted below. Total build time: <span style={{color:C.yellow}}>45–60 hours</span>.
    </div>
    <SH t="Rev E-Specific Installation Steps" mt={0} c={C.lime}/>
    {BUILD_ADDITIONS.map((s,i)=>(<div key={i} style={{marginBottom:10,padding:"12px 14px",border:`1px solid ${s.c}33`,borderLeft:`3px solid ${s.c}`,background:`${s.c}06`,borderRadius:4}}>
      <div style={{color:s.c,fontFamily:M,fontSize:11,fontWeight:"bold",marginBottom:6}}>{s.t}</div>
      <div style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.8}}>{s.d}</div>
    </div>))}
    <SH t="Full Build Phases (click to expand)"/>
    {phases.map((p,pi)=>(
      <div key={pi} style={{marginBottom:7}}>
        <div onClick={()=>setOpen(open===pi?null:pi)} style={{display:"flex",alignItems:"center",gap:12,padding:"9px 14px",background:open===pi?`${p.c}10`:"rgba(255,255,255,0.02)",border:`1px solid ${open===pi?p.c:C.border}`,borderRadius:4,cursor:"pointer",userSelect:"none"}}>
          <div style={{width:8,height:8,background:p.c,borderRadius:"50%",flexShrink:0}}/>
          <span style={{color:p.c,fontFamily:M,fontSize:12,fontWeight:"bold",letterSpacing:"0.05em"}}>{p.p}</span>
          <span style={{color:C.dimmer,fontFamily:M,fontSize:10,marginLeft:"auto"}}>{p.steps.length} steps · {open===pi?"▲":"▼"}</span>
        </div>
        {open===pi&&(<div style={{border:`1px solid ${p.c}33`,borderTop:"none",borderRadius:"0 0 4px 4px",background:`${p.c}04`,padding:"12px 14px"}}>
          {p.steps.map((s,si)=>(<div key={si} style={{display:"flex",gap:14,padding:"8px 0",borderBottom:si<p.steps.length-1?"1px solid rgba(255,255,255,0.05)":"none"}}>
            <div style={{width:22,height:22,background:p.c,borderRadius:"50%",display:"flex",alignItems:"center",justifyContent:"center",color:"#000",fontFamily:M,fontSize:9,fontWeight:"bold",flexShrink:0}}>{si+1}</div>
            <span style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.75,paddingTop:2}}>{s}</span>
          </div>))}
        </div>)}
      </div>
    ))}
  </div>);
}

// ═══════════════════════════════════════════════════════════════
//  OVERVIEW
// ═══════════════════════════════════════════════════════════════
function OverviewTab(){
  return(<div>
    <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:12,marginBottom:20}}>
      {[
        {l:"AUW — Empty (rec.)",v:`${REC_E.auw}g`,c:C.yellow,s:"5S 4500mAh 35C"},
        {l:"AUW — Cargo 250g (rec.)",v:`${REC_C.auw}g`,c:C.orange,s:"5S 2800mAh 45C"},
        {l:"T/W (empty, nacelle)",v:`${REC_E.tw}:1`,c:C.green,s:"70mm @ 5S"},
        {l:"Endurance (empty hover)",v:`${REC_E.hMin} min`,c:C.teal,s:"80% usable"},
      ].map((s,i)=>(<div key={i} style={{padding:"10px 12px",border:`1px solid ${s.c}44`,background:`${s.c}07`,borderRadius:4}}><div style={{color:C.dim,fontFamily:M,fontSize:9,letterSpacing:"0.08em",marginBottom:3}}>{s.l}</div><div style={{color:s.c,fontFamily:M,fontSize:20,fontWeight:"bold"}}>{s.v}</div><div style={{color:C.dimmer,fontFamily:M,fontSize:9,marginTop:2}}>{s.s}</div></div>))}
    </div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="Rev E Additions" mt={0} c={C.lime}/>
        <KV k="License" v="CC BY 4.0 (hull, nozzle, and all original design)" vc={C.lime}/>
        <KV k="OS SD write-blocker" v="MachXO2-256 CPLD · SDIO CMD filter · NIST SP 800-72" vc={C.lime}/>
        <KV k="Log SD NX enforcement" v="STM32 SPI proxy + 74HC74 latch + TrustZone + SELinux + OTP" vc={C.lime}/>
        <KV k="WiFi SMA output" v="MABD-011028 diplexer → SMA-1 (2.4G) + SMA-2 (5G) on carrier" vc={C.purple}/>
        <KV k="Zigbee 2.4GHz (opt)" v="CC2652P7 · also BLE 5.0 · Thread · Matter · software select" vc={C.accent}/>
        <KV k="LoRa 915MHz (opt)" v="SX1276 · also FSK Zigbee 915MHz · software select" vc={C.pink}/>
        <KV k="CM4-CARRIER-1" v="65×52mm (Rev E) · +12mm width for CPLD + diplexer + SMA"/>
        <KV k="COMMS-HAT-1" v="Rev E · NX proxy MCU · Zigbee/LoRa footprints (opt pop)"/>
      </div>
      <div>
        <SH t="System Summary" mt={0}/>
        <KV k="Hull (CC BY 4.0)" v="Serenity by Peter Farell · 365mm · PETG/CF-PETG"/>
        <KV k="Nacelles" v="2× 70mm EDF · 2200g total thrust · T/W 2.20 (empty rec.)"/>
        <KV k="Fwd EDF" v="40mm + variable nozzle (BamJr remix CC BY 4.0) · 190g"/>
        <KV k="Controllers" v="Pico 2 + TRIHAT-1 · CM4 Lite 4GB + CARRIER-E + COMMS-HAT-E"/>
        <KV k="Radios" v="SiK 915MHz + 49MHz RCRS + optional Zigbee/LoRa"/>
        <KV k="Sec. storage" v="Write-blocked OS SD · Hardware-NX log SD"/>
        <KV k="BOM estimate" v="$640–740" vc={C.yellow}/>
        {[{r:"Rev A",d:"60mm+30mm · T/W 1.87 ✗"},{r:"Rev B",d:"65mm+35mm · T/W 2.19 ✓"},{r:"Rev C",d:"Battery/lights/antenna/BOM/SBOM"},{r:"Rev D",d:"70mm/64mm+40mm · variable nozzle · build guide"},{r:"Rev E",d:"CC BY 4.0 · write-blocker · NX · dual WiFi SMA · Zigbee/LoRa",cur:true}].map((r,i)=>(<div key={i} style={{display:"flex",gap:10,padding:"5px 0",borderBottom:"1px solid rgba(0,229,255,0.07)"}}><span style={{color:r.cur?C.lime:C.dim,fontFamily:M,fontSize:10,minWidth:44,fontWeight:r.cur?"bold":"normal"}}>{r.r}</span><span style={{color:C.dimmer,fontFamily:M,fontSize:10,lineHeight:1.6}}>{r.d}</span></div>))}
      </div>
    </div>
  </div>);
}

// ═══════════════════════════════════════════════════════════════
//  APP
// ═══════════════════════════════════════════════════════════════
const TABS=["Overview","License","Battery","Propulsion","CM4 Carrier","COMMS-HAT-1","Nav Lights","Antenna","Wiring","BOM","SBOM","Build Guide"];

export default function App(){
  const [tab,setTab]=useState("Overview");
  return(<div style={{minHeight:"100vh",background:C.bg,color:C.text,fontFamily:M}}>
    <Grid/>
    <div style={{position:"relative",zIndex:1,borderBottom:`1px solid ${C.border}`,padding:"16px 24px 12px"}}>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",flexWrap:"wrap",gap:12}}>
        <div>
          <div style={{color:"rgba(163,230,53,0.35)",fontSize:9,letterSpacing:"0.2em",marginBottom:4}}>SERENITY TILTROTOR · REV E · CC BY 4.0</div>
          <h1 style={{margin:0,fontSize:18,fontWeight:"normal",color:"#fff",letterSpacing:"0.07em"}}>SERENITY DRONE — REV E</h1>
          <div style={{color:"rgba(0,229,255,0.45)",fontSize:10,marginTop:4}}>CC BY 4.0 · Write-blocker · Hardware NX · Dual WiFi SMA · Zigbee + LoRa</div>
        </div>
        <div style={{textAlign:"right",fontFamily:M}}>
          <div style={{color:C.lime,fontSize:11,fontWeight:"bold"}}>CC BY 4.0</div>
          <div style={{color:C.yellow,fontSize:12}}>{REC_E.auw}g empty · T/W {REC_E.tw}:1</div>
          <div style={{color:C.dimmer,fontSize:9,marginTop:2}}>hull: Peter Farell · nozzle: BamJr</div>
        </div>
      </div>
      <div style={{display:"flex",gap:2,marginTop:12,flexWrap:"wrap"}}>
        {TABS.map(t=>(<button key={t} onClick={()=>setTab(t)} style={{background:tab===t?"rgba(0,229,255,0.09)":"transparent",border:`1px solid ${tab===t?C.accent:"rgba(0,229,255,0.12)"}`,color:tab===t?C.accent:C.dimmer,padding:"4px 11px",fontFamily:M,fontSize:9,cursor:"pointer",letterSpacing:"0.06em",transition:"all 0.12s"}}>{t}</button>))}
      </div>
    </div>
    <div style={{position:"relative",zIndex:1,padding:"20px 24px",maxWidth:1060,margin:"0 auto"}}>
      {tab==="Overview"    && <OverviewTab/>}
      {tab==="License"     && <LicenseTab/>}
      {tab==="Battery"     && <BatteryTab/>}
      {tab==="Propulsion"  && <PropulsionTab/>}
      {tab==="CM4 Carrier" && <CarrierTab/>}
      {tab==="COMMS-HAT-1"   && <ComphatTab/>}
      {tab==="Nav Lights"  && <NavLightsTab/>}
      {tab==="Antenna"     && <AntennaTab/>}
      {tab==="Wiring"      && <WiringTab/>}
      {tab==="BOM"         && <BomTab/>}
      {tab==="SBOM"        && <SbomTab/>}
      {tab==="Build Guide" && <BuildGuideTab/>}
    </div>
    <div style={{position:"relative",zIndex:1,borderTop:`1px solid ${C.border}`,padding:"10px 24px",display:"flex",justifyContent:"space-between",flexWrap:"wrap",gap:6}}>
      <span style={{color:"rgba(163,230,53,0.2)",fontSize:8,letterSpacing:"0.1em"}}>CC BY 4.0 · SERENITY BY PETER FARELL (PRINTABLES.COM/548545) · NOZZLE BY BAMJR (THINGIVERSE.COM/THING:2991269) · THIS DESIGN: CC BY 4.0</span>
      <span style={{color:"rgba(0,229,255,0.16)",fontSize:8}}>REV E · NOT FOR CERTIFICATION · VERIFY BEFORE FLIGHT</span>
    </div>
  </div>);
}
