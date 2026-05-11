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
  pink:"#f472b6", teal:"#2dd4bf", red:"#f87171", lime:"#a3e635", gold:"#fbbf24",
  dim:"rgba(255,255,255,0.90)", dimmer:"rgba(255,255,255,0.80)", text:"rgba(255,255,255,0.82)",
};
const M = "'OpenDyslexic Mono','OpenDyslexic','OpenDyslexicMono',monospace";

// ── Unit converters ─────────────────────────────────────────────
const mToFt   = m  => (m  * 3.2808).toFixed(0);   // metres → feet
const msToKts = ms => (ms * 1.9438).toFixed(1);    // m/s    → knots
const mToYd   = m  => (m  * 1.0936).toFixed(0);    // metres → yards
const mmToIn  = mm => (mm * 0.03937).toFixed(2);   // mm     → inches
const ft  = m  => `${mToFt(m)} ft`;
const kts = ms => `${msToKts(ms)} kts`;
const yd  = m  => `${mToYd(m)} yd`;
const mmi = mm => `${mm} mm (${mmToIn(mm)}")`;      // mm with inches

// ── Key performance numbers (Rev D/E, 70mm primary) ──────────────
const T70=1100, T40=190, BAT_V=18.5, I70=35, I40=14, AV_A=2.0;
const BASE_70=582;
const CRUISE_A=I70*Math.pow(0.14,1.5)*2+I40*0.88+AV_A;
const hovI=(auw)=>I70*Math.pow(auw/2/T70,1.5)*2+AV_A;
function bRow(id,name,mass,cap,Cc,note,payload=0){
  const auw=BASE_70+mass+payload,tw=(T70*2/auw).toFixed(2),ok=T70*2/auw>=2.0;
  const hA=hovI(auw),hMin=(cap/1000*0.8/hA*60).toFixed(1),cMin=(cap/1000*0.8/CRUISE_A*60).toFixed(1);
  return{id,name,mass,cap,Cc,note,auw,tw,ok,hA,hMin,cMin,maxA:cap/1000*Cc,payload};
}
const BATS_E=[bRow("A","5S 2800mAh 45C",271,2800,45,""),bRow("B","5S 3500mAh 45C",328,3500,45,""),
              bRow("C","5S 4000mAh 35C",376,4000,35,""),bRow("D","5S 4500mAh 35C",420,4500,35,"★ MAX ENDURANCE"),
              bRow("E","5S 5000mAh 30C",465,5000,30,"C marginal")];
const BATS_C=[bRow("A","5S 1800mAh 75C",190,1800,75,"",250),bRow("B","5S 2200mAh 75C",220,2200,75,"",250),
              bRow("C","5S 2500mAh 60C",248,2500,60,"",250),bRow("D","5S 2800mAh 45C",271,2800,45,"★ CARGO REC",250),
              bRow("E","5S 3000mAh 45C",292,3000,45,"T/W marginal",250)];
const REC_E=BATS_E.find(b=>b.id==="D"), REC_C=BATS_C.find(b=>b.id==="D");

// ── primitives ────────────────────────────────────────────────
const SH=({t,c=C.accent,mt=22})=>(<div style={{display:"flex",alignItems:"center",gap:10,marginBottom:14,marginTop:mt}}><div style={{width:3,height:17,background:c}}/><span style={{color:c,fontFamily:M,fontSize:13,letterSpacing:"0.13em",textTransform:"uppercase",fontWeight:"normal"}}>{t}</span></div>);
const KV=({k,v,vc=C.text,u=""})=>(<div style={{display:"flex",justifyContent:"space-between",padding:"5px 0",borderBottom:"1px solid rgba(0,229,255,0.07)",alignItems:"baseline"}}><span style={{color:C.dim,fontFamily:M,fontSize:11}}>{k}</span><span style={{color:vc,fontFamily:M,fontSize:11}}>{v}{u&&<span style={{color:C.accent,marginLeft:4,fontSize:10}}>{u}</span>}</span></div>);
const Note=({c=C.dim,ch})=>(<div style={{marginTop:8,marginBottom:6,color:c,fontFamily:M,fontSize:10,lineHeight:1.85,padding:"8px 12px",borderLeft:`2px solid ${c}55`,background:`${c}07`,borderRadius:3}}>{ch}</div>);
const Warn=({ch})=>(<div style={{marginTop:8,color:C.yellow,fontFamily:M,fontSize:10,lineHeight:1.8,padding:"7px 12px",borderLeft:`2px solid ${C.yellow}`,background:"rgba(255,230,0,0.05)",borderRadius:3}}>⚠ {ch}</div>);
const Good=({ch})=>(<div style={{marginTop:8,color:C.green,fontFamily:M,fontSize:10,lineHeight:1.8,padding:"7px 12px",borderLeft:`2px solid ${C.green}`,background:"rgba(74,222,128,0.05)",borderRadius:3}}>✓ {ch}</div>);
function TH({cols}){return(<thead><tr>{cols.map(h=>(<th key={h} style={{padding:"6px 9px",borderBottom:`1px solid ${C.border}`,color:C.accent,textAlign:"left",fontWeight:"normal",fontSize:10,letterSpacing:"0.06em",whiteSpace:"nowrap",opacity:.85}}>{h}</th>))}</tr></thead>);}
function Grid(){return(<svg style={{position:"fixed",inset:0,width:"100%",height:"100%",pointerEvents:"none",zIndex:0}}><defs><pattern id="sg" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0L0 0 0 20" fill="none" stroke="rgba(0,229,255,0.035)" strokeWidth={0.5}/></pattern><pattern id="lg" width="100" height="100" patternUnits="userSpaceOnUse"><rect width="100" height="100" fill="url(#sg)"/><path d="M100 0L0 0 0 100" fill="none" stroke="rgba(0,229,255,0.065)" strokeWidth={1}/></pattern></defs><rect width="100%" height="100%" fill="url(#lg)"/></svg>);}

// ══════════════════════════════════════════════════════════════
//  LICENSE TAB
// ══════════════════════════════════════════════════════════════
const LICENSE_TEXT=`Creative Commons Attribution 4.0 International

Copyright © 2025 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP

You are free to:
  Share  — copy and redistribute in any medium or format
  Adapt  — remix, transform, and build upon for any purpose, even commercially

Under the following terms:
  Attribution — Give appropriate credit, link to the license, and indicate
  if changes were made. You may not suggest the licensor endorses you.

Full text: https://creativecommons.org/licenses/by/4.0/legalcode`;

function LicenseTab(){
  const attribs=[
    {cat:"Hull Model",
     title:"Serenity, Firefly Class",
     author:"Peter Farell",
     src:"printables.com/model/548545",
     lic:"CC BY 4.0",
     use:"Hull outer geometry · scaled to 365 mm (14.4\") · hollowed to 1.5 mm shell · CF skeleton added · proportions preserved",
     tmpl:`Hull: "Serenity, Firefly Class" by Peter Farell, printables.com/model/548545, CC BY 4.0. Adapted by Steve Griffing.`},
    {cat:"Nozzle Mechanism",
     title:"Variable Area EDF Nozzles",
     author:"BamJr",
     src:"thingiverse.com/thing:2991269",
     lic:"CC BY 4.0",
     use:"Nacelle nozzle: scaled to 70 mm (2.76\") ID · servo removed · M0.5 rack teeth added · gear-coupled to nacelle pivot. Fuselage nozzle: scaled to 40 mm (1.57\") ID · SG90 servo retained.",
     tmpl:`Nozzle: "Variable Area EDF Nozzles" by BamJr, thingiverse.com/thing:2991269, CC BY 4.0. Remix by Steve Griffing.`},
    {cat:"Visual Inspiration",
     title:"Firefly (TV Series, 2002) · Serenity (Film, 2005)",
     author:"Joss Whedon — Creator/Executive Producer/Writer\nTim Minear — Co-Executive Producer/Writer\nDavid Solomon — Producer/Director\nCarey Meyer — Production Designer\nMutant Enemy Productions · 20th Century Fox Television · Universal Pictures",
     src:"Non-commercial fan engineering work",
     lic:"All IP rights reserved by rights holders — see notes",
     use:"Visual silhouette and form language of the Firefly-class ship used as aesthetic basis for the UAV hull. No copyrighted artwork, script, music, or character is reproduced.",
     tmpl:`Visual inspiration: Serenity / Firefly-class ship © Joss Whedon / Mutant Enemy / Universal Pictures. Fan build — not officially licensed.`},
  ];
  return(<div>
    {/* CC Badge */}
    <div style={{padding:"22px",border:`1px solid ${C.lime}44`,borderRadius:8,background:"rgba(163,230,53,0.05)",marginBottom:20,textAlign:"center"}}>
      <div style={{color:C.lime,fontFamily:M,fontSize:26,fontWeight:"bold",letterSpacing:"0.04em",marginBottom:8}}>CC BY 4.0</div>
      <div style={{color:C.text,fontFamily:M,fontSize:14,marginBottom:4}}>SERENITY-CLASS TILTROTOR UAV</div>
      <div style={{color:C.dim,fontFamily:M,fontSize:10}}>Steve Griffing, PE(CSE), CISSP-ISSEP, CPP</div>
      <div style={{color:C.dimmer,fontFamily:M,fontSize:10,marginTop:4}}>creativecommons.org/licenses/by/4.0</div>
      <div style={{display:"flex",justifyContent:"center",gap:16,marginTop:14,flexWrap:"wrap"}}>
        {[["Share","Any medium or format"],["Adapt","Remix & build upon"],["Commercial","Even commercially"]].map(([t,d])=>(
          <div key={t} style={{padding:"8px 14px",border:`1px solid ${C.lime}44`,borderRadius:4,maxWidth:160}}>
            <div style={{color:C.lime,fontFamily:M,fontSize:11,fontWeight:"bold",marginBottom:3}}>{t}</div>
            <div style={{color:C.dim,fontFamily:M,fontSize:9}}>{d}</div>
          </div>
        ))}
      </div>
    </div>
    {/* License text */}
    <div style={{background:"rgba(0,0,0,0.35)",borderRadius:4,padding:"12px 14px",fontFamily:M,fontSize:9,color:C.dim,whiteSpace:"pre-line",lineHeight:1.9,border:`1px solid rgba(163,230,53,0.15)`,marginBottom:20}}>{LICENSE_TEXT}</div>

    <SH t="Attribution to Integrated Works"/>
    {attribs.map((a,i)=>(
      <div key={i} style={{marginBottom:16,padding:"14px",border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.02)"}}>
        <div style={{display:"flex",gap:10,alignItems:"baseline",marginBottom:8,flexWrap:"wrap"}}>
          <span style={{color:C.yellow,fontFamily:M,fontSize:9,border:`1px solid ${C.yellow}44`,padding:"1px 7px",borderRadius:2}}>{a.cat}</span>
          <span style={{color:C.text,fontFamily:M,fontSize:12,fontWeight:"bold"}}>{a.title}</span>
          <span style={{color:a.lic.includes("CC")?C.lime:C.orange,fontFamily:M,fontSize:9}}>{a.lic}</span>
        </div>
        <div style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.8,marginBottom:6,whiteSpace:"pre-line"}}>{a.author}</div>
        <div style={{color:C.teal,fontFamily:M,fontSize:9,marginBottom:6}}>{a.src}</div>
        <div style={{color:C.dimmer,fontFamily:M,fontSize:10,lineHeight:1.7,marginBottom:8}}>{a.use}</div>
        <div style={{background:"rgba(0,0,0,0.3)",borderRadius:3,padding:"8px 10px",fontFamily:M,fontSize:9,color:C.text}}>
          <span style={{color:C.dimmer,marginRight:6}}>Attribution template:</span>{a.tmpl}
        </div>
      </div>
    ))}

    <SH t="Firefly / Serenity IP Notice" c={C.orange}/>
    <Note c={C.orange} ch="The Firefly and Serenity names, the Firefly-class ship design, and all associated intellectual property are trademarks and copyrights of Joss Whedon / Mutant Enemy Productions / Universal Pictures / 20th Century Fox / The Walt Disney Company. This UAV project is a non-commercial fan engineering work. It does not reproduce copyrighted artwork, script, music, or characters, and does not claim trademark rights to the Serenity name. Commercial products based on this design must obtain appropriate licensing from rights holders before using the Serenity name or likeness."/>

    <SH t="Unit Conventions (Rev F)"/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:16}}>
      <div>
        <KV k="Altitudes" v="Feet (ft) — e.g. ≥26 ft AGL" vc={C.green}/>
        <KV k="Airspeeds / velocities" v="Knots (kts) — e.g. 35–49 kts cruise" vc={C.green}/>
        <KV k="Ranges / distances" v="Yards (yd) — e.g. ≤1,094 yd SiK link" vc={C.green}/>
      </div>
      <div>
        <KV k="Build dimensions" v="mm primary, inches in parentheses" vc={C.teal}/>
        <KV k="Example" v='365 mm (14.4") hull length' vc={C.teal}/>
        <KV k="Mass" v="Grams (g) throughout" vc={C.dim}/>
      </div>
    </div>
  </div>);
}

// ══════════════════════════════════════════════════════════════
//  OVERVIEW TAB
// ══════════════════════════════════════════════════════════════
function OverviewTab(){
  return(<div>
    {/* Author block */}
    <div style={{padding:"14px 16px",border:`1px solid ${C.lime}33`,borderRadius:4,background:"rgba(163,230,53,0.04)",marginBottom:18,fontFamily:M}}>
      <div style={{color:C.lime,fontSize:9,letterSpacing:"0.15em",marginBottom:4}}>AUTHOR — CC BY 4.0</div>
      <div style={{color:C.text,fontSize:14,fontWeight:"bold",letterSpacing:"0.06em"}}>Steve Griffing</div>
      <div style={{color:C.dim,fontSize:10,marginTop:4}}>PE(CSE) · CISSP-ISSEP · CPP</div>
      <div style={{color:C.dimmer,fontSize:9,marginTop:3}}>Professional Engineer (Computer Science &amp; Engineering) · Information Systems Security Engineering Professional · Certified Protection Professional</div>
    </div>

    <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:12,marginBottom:20}}>
      {[
        {l:"Hull length",v:`${mmi(365)}`,c:C.orange,s:"365 mm (14.4\") Serenity-class"},
        {l:"Wingspan tip-to-tip",v:`${mmi(680)}`,c:C.accent,s:"680 mm (26.8\")"},
        {l:"AUW — empty (rec.)",v:`${REC_E.auw} g`,c:C.yellow,s:"5S 4500mAh 35C"},
        {l:"AUW — cargo 250 g",v:`${REC_C.auw} g`,c:C.orange,s:"5S 2800mAh 45C"},
      ].map((s,i)=>(<div key={i} style={{padding:"10px 12px",border:`1px solid ${s.c}44`,background:`${s.c}07`,borderRadius:4}}><div style={{color:C.dim,fontFamily:M,fontSize:9,letterSpacing:"0.08em",marginBottom:3}}>{s.l}</div><div style={{color:s.c,fontFamily:M,fontSize:15,fontWeight:"bold"}}>{s.v}</div><div style={{color:C.dimmer,fontFamily:M,fontSize:9,marginTop:2}}>{s.s}</div></div>))}
    </div>

    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="System Summary" mt={0}/>
        <KV k="Hull (CC BY 4.0)" v={`Serenity by Peter Farell · ${mmi(365)}`}/>
        <KV k="Nacelles" v="2× 70 mm (2.76\") EDF · 2200 g total thrust · T/W 2.20 (empty rec.)" vc={C.green}/>
        <KV k="Nacelle nozzle" v="BamJr remix CC BY 4.0 · gear-coupled · no servo · 36→42 mm (1.42\"→1.65\")"/>
        <KV k="Fuselage EDF" v="40 mm (1.57\") + variable nozzle (BamJr remix) · 190 g"/>
        <KV k="Cruise speed" v={`${kts(18)}–${kts(25)}`} vc={C.teal}/>
        <KV k="Transition altitude" v={`≥${ft(8)} AGL`} vc={C.yellow}/>
        <KV k="Empty hover endurance" v={`${REC_E.hMin} min (5S 4500mAh)`} vc={C.yellow}/>
        <KV k="Cargo hover endurance" v={`${REC_C.hMin} min (5S 2800mAh + 250 g)`} vc={C.orange}/>
        <KV k="SiK telemetry range" v={`≤${yd(1000)} LOS`} vc={C.accent}/>
        <KV k="RCRS control range" v={`≤${yd(500)}`} vc={C.pink}/>
        <KV k="GPS CEP" v={`&lt;${ft(2.5)} (${mToYd(2.5).toFixed(0)} yd) open sky`}/>
        <KV k="Winch line" v={`5 m (5.5 yd) Dyneema SK75 · 40 kg break`}/>
        <KV k="Controllers" v="Pico 2 + TRIHAT-1 · CM4 Lite 4GB + CARRIER-E + COMMS-HAT-E"/>
        <KV k="Security" v="Write-blocked OS SD · Hardware-NX log SD · TPM 2.0 attestation"/>
        <KV k="Optional radios" v="CC2652P7 Zigbee/BLE/Thread 2.4 GHz · SX1276 LoRa 915 MHz"/>
        <KV k="BOM estimate" v="$640–740" vc={C.yellow}/>
      </div>
      <div>
        <SH t="Performance Envelope" mt={0}/>
        <div style={{overflowX:"auto"}}>
          <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
            <TH cols={["PARAMETER","VALUE","UNIT"]}/>
            <tbody>{[
              ["Hover throttle (empty rec.)","~46","%"],
              ["Hover throttle (cargo rec.)","~50","%"],
              ["Transition altitude minimum",ft(8),"AGL"],
              ["Cruise speed range",`${kts(18)}–${kts(25)}`,""],
              ["Max level speed (est.)",kts(28),""],
              ["Max climb rate (hover)",`~${kts(3)}`,"vertical"],
              ["SiK link range",`≤${yd(1000)}`,"LOS"],
              ["RCRS link range",`≤${yd(500)}`,"LOS"],
              ["WiFi (CM4 SMA external)",`${yd(200)}–${yd(400)}`,"outdoors"],
              ["Zigbee 2.4 GHz range (opt.)",`~${yd(109)}`,"through hull"],
              ["LoRa 915 MHz range (opt.)",`${yd(1094)}–${yd(5468)}`,"outdoor"],
              ["GPS CEP",`<${ft(2.5)}`,"open sky"],
              ["Barometer altitude res.",`±${ft(1.6)}`,""],
              ["Winch descent rate",`~${kts(0.29)} (~0.5 ft/s)`,"loaded"],
              ["Payload capacity","250","g"],
              ["Max AUW (cargo + battery)","1,103","g"],
            ].map(([k,v,u],i)=>(<tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
              <td style={{padding:"4px 9px",color:C.dim,fontFamily:M,fontSize:10}}>{k}</td>
              <td style={{padding:"4px 9px",color:C.yellow,fontFamily:M,fontSize:10,fontWeight:"bold"}}>{v}</td>
              <td style={{padding:"4px 9px",color:C.accent,fontFamily:M,fontSize:9}}>{u}</td>
            </tr>))}</tbody>
          </table>
        </div>
        <SH t="Revision History"/>
        {[{r:"A",d:"60mm+30mm · T/W 1.87 ✗"},{r:"B",d:"65mm+35mm · T/W 2.19 ✓"},{r:"C",d:"Battery/lights/antenna/BOM/SBOM"},{r:"D",d:"70mm/64mm+40mm · variable nozzle · build guide"},{r:"E",d:"CC BY 4.0 · write-blocker · NX · dual WiFi SMA · Zigbee/LoRa · nacelle gear nozzle"},{r:"F",d:"Author attribution · unit conventions (ft/kts/yd/mm+in) · full license compliance",cur:true}].map((r,i)=>(<div key={i} style={{display:"flex",gap:10,padding:"5px 0",borderBottom:"1px solid rgba(0,229,255,0.07)"}}><span style={{color:r.cur?C.lime:C.dim,fontFamily:M,fontSize:10,minWidth:24,fontWeight:r.cur?"bold":"normal"}}>Rev {r.r}</span><span style={{color:C.dimmer,fontFamily:M,fontSize:10,lineHeight:1.6}}>{r.d}</span></div>))}
      </div>
    </div>
  </div>);
}

// ══════════════════════════════════════════════════════════════
//  AIRFRAME TAB
// ══════════════════════════════════════════════════════════════
function AirframeTab(){
  const dims=[
    {part:"Hull overall length",        dim:365, note:"Serenity-class · scaled ×2 + 5mm for 40mm bell"},
    {part:"Fuselage max width",         dim:88,  note:"Main hull beam at 120mm station"},
    {part:"Fuselage max height",        dim:58,  note:"Including cockpit dome"},
    {part:"Wingspan tip-to-tip",        dim:680, note:"Wing spar to spar"},
    {part:"Outrigger arm length",       dim:300, note:"CF 12mm OD spar"},
    {part:"Nacelle pod OD (70mm EDF)",  dim:80,  note:"CF-PETG fairing"},
    {part:"Nacelle pod length",         dim:120, note:"Intake to nozzle exit"},
    {part:"Engine bell housing OD",     dim:76,  note:"Houses 40mm EDF + variable nozzle"},
    {part:"Payload bay L × W × H",      dim:null, note:"70 mm (2.76\") × 50 mm (1.97\") × 35 mm (1.38\")"},
    {part:"CF keel spine",              dim:385, note:"6×3mm (0.24\"×0.12\") flat bar"},
    {part:"Landing skid width",         dim:80,  note:"Per skid pair, aft set"},
    {part:"Landing skid height",        dim:42,  note:"Ground clearance"},
    {part:"Cockpit dome height",        dim:32,  note:"Above fuselage centreline"},
    {part:"TRIHAT-1 PCB",               dim:null, note:"65 mm (2.56\") × 48 mm (1.89\")"},
    {part:"CM4-CARRIER-1 PCB (Rev E)",  dim:null, note:"65 mm (2.56\") × 52 mm (2.05\")"},
    {part:"COMMS-HAT-1 PCB (Rev E)",      dim:null, note:"65 mm (2.56\") × 48 mm (1.89\")"},
  ];
  return(<div>
    <Note c={C.accent} ch="All build dimensions are given in millimetres (mm) as primary units with inches in parentheses. Operational parameters use feet (altitude), knots (speed), and yards (range)."/>
    <SH t="Airframe Dimensions" mt={14}/>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["PART / DIMENSION","mm","(inches)","NOTES"]}/>
        <tbody>{dims.map((d,i)=>(<tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent",verticalAlign:"top"}}>
          <td style={{padding:"5px 9px",color:C.text}}>{d.part}</td>
          <td style={{padding:"5px 9px",color:d.dim?C.yellow:C.dim,fontWeight:d.dim?"bold":"normal"}}>{d.dim?d.dim+"mm":"—"}</td>
          <td style={{padding:"5px 9px",color:d.dim?C.teal:C.dim}}>{d.dim?`(${mmToIn(d.dim)}")`:"—"}</td>
          <td style={{padding:"5px 9px",color:C.dim,fontSize:9,lineHeight:1.5}}>{d.note}</td>
        </tr>))}</tbody>
      </table>
    </div>
    <SH t="Structural Materials"/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <KV k="CF keel" v={`${mmi(385)} · 6×3mm (0.24"×0.12") flat bar`}/>
        <KV k="Outrigger spars" v={`${mmi(300)} × 12 mm (0.47") OD CF tube`}/>
        <KV k="Nacelle pivot" v={`8 mm (0.31") OD CF rod · 52 mm (2.05") long`}/>
        <KV k="Long. nozzle shaft" v={`3 mm (0.12") OD CF rod · per nacelle`}/>
        <KV k="Transverse shaft" v={`3 mm (0.12") OD × 2 mm (0.08") ID brass tube`}/>
        <KV k="Fuselage shell" v="PETG · 1.5 mm (0.06\") walls · 8% gyroid"/>
        <KV k="Nacelle pods" v="CF-PETG · 2.0 mm (0.08\") walls · 25% infill"/>
      </div>
      <div>
        <KV k="Cockpit dome" v="Clear PETG · friction-fit · GPS window"/>
        <KV k="Engine bell" v="PETG · 3 walls · 20% infill · 40mm EDF + nozzle"/>
        <KV k="Dorsal antenna fin" v={`${mmi(35)} tall · PETG · 49 MHz coil cavity`}/>
        <KV k="Payload bay door" v={`${mmi(112)} × ${mmi(42)} · hinged PETG · SG90 latch`}/>
        <KV k="Skid feet" v="TPU 95A · crash-absorbing · 4 per aircraft"/>
        <KV k="M0.5 gear module" v="All nozzle gears: M0.5 · 22° pressure angle"/>
      </div>
    </div>
    <SH t="Centre of Gravity"/>
    <KV k="CG target (from nose)" v={`152 mm (5.98") · ${mToYd(0.152).toFixed(2)} yd from nose tip`}/>
    <KV k="Battery rail travel" v={`±22 mm (±0.87") slide on keel rails`}/>
    <KV k="Empty CG" v={`148 mm (5.83") — battery centroid at 195 mm (7.68") from nose`}/>
    <KV k="Cargo CG shift (250 g belly)" v={`−6 mm (0.24") forward · correct by sliding battery 10 mm (0.39") aft`}/>
  </div>);
}

// ══════════════════════════════════════════════════════════════
//  PROPULSION TAB
// ══════════════════════════════════════════════════════════════
function PropulsionTab(){
  return(<div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="70mm Nacelle EDF ×2 (Primary)" mt={0} c={C.orange}/>
        <KV k="Duct ID" v={mmi(70)} vc={C.orange}/>
        <KV k="Nacelle fairing OD" v={mmi(80)}/>
        <KV k="Thrust @ 5S" v="~1100 g each · 2200 g total" vc={C.green}/>
        <KV k="Max current" v="35 A each · 70 A total"/>
        <KV k="ESC" v="40A BLHeli32 DSHOT300"/>
        <KV k="KV" v="2400–2600 KV @ 5S"/>
        <KV k="Hover throttle (empty rec.)" v="~46%" vc={C.green}/>
        <KV k="Sourcing" v="Changesun · Freewing · DYS · HobbyWing" vc={C.green}/>
        <SH t="Nacelle Variable Nozzle (Gear-Coupled)" c={C.teal}/>
        <KV k="Base remix" v="BamJr thing:2991269 · CC BY 4.0"/>
        <KV k="Scaled to" v={`${mmi(70)} ID · ${mmi(80)} OD`}/>
        <KV k="Closed (cruise, nacelle 0°)" v={`${mmi(36)} exit`}/>
        <KV k="Open (hover, nacelle 90°)" v={`${mmi(42)} exit`}/>
        <KV k="Actuation" v="Passive gear chain — no servo, no power" vc={C.green}/>
        <KV k="Gear module" v="M0.5 · sector R=22mm (0.87\") · ring rack R=28mm (1.10\")"/>
        <KV k="Ring rotation / 90° nacelle" v="70.7°"/>
      </div>
      <div>
        <SH t="40mm Fuselage EDF (Servo Nozzle)" mt={0} c={C.yellow}/>
        <KV k="Duct ID" v={mmi(40)} vc={C.yellow}/>
        <KV k="Engine bell OD" v={`~${mmi(76)}`}/>
        <KV k="Thrust @ 5S" v="~190 g" vc={C.green}/>
        <KV k="Max current" v="14 A"/>
        <KV k="ESC" v="25A BLHeli32"/>
        <KV k="KV" v="4000–4500 KV"/>
        <KV k="Base remix" v="BamJr thing:2991269 · CC BY 4.0"/>
        <KV k="Scaled to" v={`${mmi(40)} ID`}/>
        <KV k="Nozzle closed (cruise)" v={`${mmi(36)} exit`}/>
        <KV k="Nozzle open (hover)" v={`${mmi(42)} exit`}/>
        <KV k="Actuation" v="SG90 servo · Pico 2 GP15 · 50 Hz PWM"/>
        <SH t="Thrust Summary"/>
        <div style={{overflowX:"auto"}}>
          <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
            <TH cols={["CONFIG","NAC THRUST","FWD","AUW","T/W"]}/>
            <tbody>{[
              ["70mm empty (rec.)",   "2200 g","190 g",`${REC_E.auw} g`,REC_E.tw],
              ["70mm cargo 250g (rec.)","2200 g","190 g",`${REC_C.auw} g`,REC_C.tw],
              ["64mm alt (empty only)","1760 g","190 g","≈898 g","1.96"],
            ].map((r,i)=>(<tr key={i} style={{background:i===0?"rgba(74,222,128,0.05)":i%2===0?"rgba(0,229,255,0.02)":"transparent"}}>
              {r.map((v,j)=>(<td key={j} style={{padding:"5px 9px",color:j===0?C.text:j===3?C.yellow:j===4?(parseFloat(v)>=2.0?C.green:C.red):C.dim,fontFamily:M,fontSize:10,fontWeight:j===4?"bold":"normal",whiteSpace:"nowrap"}}>{v}</td>))}
            </tr>))}</tbody>
          </table>
        </div>
        <Note c={C.teal} ch="64mm alternate cannot carry 250g cargo with any useful battery. Recommend 70mm for all cargo missions."/>
      </div>
    </div>
  </div>);
}

// ══════════════════════════════════════════════════════════════
//  BATTERY TAB
// ══════════════════════════════════════════════════════════════
function BatRow2({b}){return(
  <tr style={{background:b.note.includes("★")?"rgba(74,222,128,0.06)":b.id.charCodeAt(0)%2===0?"rgba(0,229,255,0.02)":"transparent"}}>
    {[b.id,b.name,b.mass+"g",b.cap+"",b.Cc+"C",b.maxA.toFixed(0)+"A",b.auw+"g",b.tw,b.ok?b.hMin+" min":"—",b.ok?b.cMin+" min":"—",b.note||"OK"].map((v,i)=>(
      <td key={i} style={{padding:"5px 8px",color:i===0?C.yellow:i===7?(parseFloat(v)>=2.0?C.green:C.red):i===8?C.yellow:i===9?C.teal:i===10?(v.includes("★")?C.green:v.includes("✗")||v.includes("marginal")?C.orange:C.dim):C.text,fontWeight:i===7?"bold":"normal",whiteSpace:"nowrap",fontFamily:M,fontSize:10}}>{v}</td>
    ))}
  </tr>
);}

function BatteryTab(){
  const [v,setV]=useState("empty");
  const maxEmpty=Math.floor(T70*2/2-BASE_70), maxCargo=Math.floor(T70*2/2-BASE_70-250);
  return(<div>
    <div style={{display:"flex",gap:6,marginBottom:14}}>
      {[["empty","Max Empty Endurance"],["cargo","250g Cargo"]].map(([k,l])=>(
        <button key={k} onClick={()=>setV(k)} style={{background:v===k?"rgba(0,229,255,0.09)":"transparent",border:`1px solid ${v===k?C.accent:"rgba(0,229,255,0.14)"}`,color:v===k?C.accent:C.dimmer,padding:"5px 13px",fontFamily:M,fontSize:10,cursor:"pointer",borderRadius:2}}>{l}</button>
      ))}
    </div>
    <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:12,marginBottom:16}}>
      {[
        {l:"Airframe (no battery/payload)",v:`${BASE_70} g`,c:C.dim},
        {l:"Max battery · empty (T/W=2.0)",v:`${maxEmpty} g`,c:C.green},
        {l:"Max battery · 250g cargo",v:`${maxCargo} g`,c:C.orange},
      ].map((s,i)=>(<div key={i} style={{padding:"10px 12px",border:`1px solid ${s.c}44`,background:`${s.c}07`,borderRadius:4}}><div style={{color:C.dim,fontFamily:M,fontSize:9,marginBottom:3}}>{s.l}</div><div style={{color:s.c,fontFamily:M,fontSize:18,fontWeight:"bold"}}>{s.v}</div></div>))}
    </div>
    <div style={{overflowX:"auto",marginBottom:16}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["ID","BATTERY","MASS","CAP","C","MAX A","AUW","T/W","HOVER","CRUISE","NOTE"]}/>
        <tbody>{(v==="empty"?BATS_E:BATS_C).map((b,i)=>(<BatRow2 key={i} b={b}/>))}</tbody>
      </table>
    </div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t={`Recommended (${v==="empty"?"Empty":"Cargo"})`} mt={0} c={C.green}/>
        {v==="empty"
          ?[["AUW",`${REC_E.auw} g`],["T/W",`${REC_E.tw}:1`],["Hover endurance",`${REC_E.hMin} min`],["Cruise endurance",`${REC_E.cMin} min`],["Max discharge",`${REC_E.maxA.toFixed(0)} A`],["Dimensions (typ)","152×46×34 mm (5.98\"×1.81\"×1.34\")"]].map(([k,v2])=>(<KV key={k} k={k} v={v2}/>))
          :[["Payload",`250 g · ${mmi(250).split(" ")[0]} g`],["AUW",`${REC_C.auw} g`],["T/W",`${REC_C.tw}:1`],["Hover endurance",`${REC_C.hMin} min`],["Cruise endurance",`${REC_C.cMin} min`],["Max discharge",`${REC_C.maxA.toFixed(0)} A`]].map(([k,v2])=>(<KV key={k} k={k} v={v2}/>))
        }
      </div>
      <div>
        <Good ch={`Rev F recommended: ${v==="empty"?"5S 4500mAh 35C for empty ops — best endurance at T/W "+REC_E.tw:"5S 2800mAh 45C for 250g cargo — T/W "+REC_C.tw+" with adequate margin"}`}/>
        <Warn ch="5S 5000mAh 30C: verify cell brand — at 70A peak draw, only high-quality cells (Gens Ace G-Tech, Tattu Funfly) reliably deliver rated C continuously. Measure actual voltage sag under load before flight."/>
      </div>
    </div>
  </div>);
}

// ══════════════════════════════════════════════════════════════
//  RADIOS & RANGES TAB
// ══════════════════════════════════════════════════════════════
function RadiosTab(){
  const radios=[
    {id:"SiK",   name:"SiK 915 MHz (MAVLink)",     freq:"915 MHz",power:"100 mW",proto:"MAVLink 2.0",range_m:1000, ant:"λ/4 monopole 82mm (3.23\") belly · SMA-RP",notes:"Primary telemetry link. UART1 on TRIHAT-1. Directs to GCS via COMMS-HAT-1 mavlink-router."},
    {id:"RCRS",  name:"49 MHz RCRS TDDS",           freq:"49.83–49.89 MHz",power:"10 mW EIRP",proto:"TDDS 6-ch",range_m:500, ant:"250mm (9.84\") whip + 38μH coil · dorsal fin · SMA-LR",notes:"Primary RC link. Clearest channel selected by scan on power-on. Control priority over telemetry in TDDS frame."},
    {id:"WiFi24",name:"WiFi 2.4 GHz (CM4)",         freq:"2412–2484 MHz",power:"BCM43455 module",proto:"802.11 b/g/n/ac",range_m:350, ant:"External omni via SMA-1 on carrier · diplexer",notes:"Ground debug SSH / QGC backup. External SMA-1 antenna extends range vs internal PCB trace."},
    {id:"WiFi5", name:"WiFi 5 GHz (CM4)",            freq:"5180–5825 MHz",power:"BCM43455 module",proto:"802.11 a/n/ac",range_m:200, ant:"External gain patch via SMA-2 · diplexer",notes:"High-bandwidth log streaming to ground station laptop."},
    {id:"ZB24",  name:"Zigbee 2.4 GHz (CC2652P7, opt.)",freq:"2.4 GHz",power:"+20 dBm PA",proto:"Zigbee / BLE / Thread / Matter",range_m:100, ant:"2.4 GHz whip via SMA-ZB",notes:"Optional population on COMMS-HAT-1. One protocol image active at a time (SW select). Also supports BLE 5.0, Thread/Matter."},
    {id:"LR915", name:"LoRa 915 MHz (SX1276, opt.)", freq:"902–928 MHz",power:"+20 dBm (100 mW)",proto:"LoRaWAN Class A",range_m:4000, ant:"λ/4 whip via SMA-LR",notes:"Optional. Long-range backup telemetry. Also supports FSK / Zigbee 915MHz via register config."},
  ];
  return(<div>
    <Note c={C.accent} ch="All radio ranges given in yards (yd). Actual range depends on antenna height above ground, terrain, and interference. Ranges stated are typical line-of-sight (LOS) estimates under benign RF conditions."/>
    <div style={{overflowX:"auto",marginBottom:20}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["RADIO","FREQ","POWER","PROTOCOL","RANGE","ANTENNA","NOTES"]}/>
        <tbody>{radios.map((r,i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent",verticalAlign:"top"}}>
            <td style={{padding:"5px 9px",color:C.accent,fontWeight:"bold",whiteSpace:"nowrap"}}>{r.id}</td>
            <td style={{padding:"5px 9px",color:C.teal,whiteSpace:"nowrap"}}>{r.freq}</td>
            <td style={{padding:"5px 9px",color:C.dim,whiteSpace:"nowrap"}}>{r.power}</td>
            <td style={{padding:"5px 9px",color:C.dim,whiteSpace:"nowrap"}}>{r.proto}</td>
            <td style={{padding:"5px 9px",color:C.yellow,fontWeight:"bold",whiteSpace:"nowrap"}}>≤{yd(r.range_m)}</td>
            <td style={{padding:"5px 9px",color:C.dim,fontSize:9}}>{r.ant}</td>
            <td style={{padding:"5px 9px",color:C.dimmer,fontSize:9,lineHeight:1.5}}>{r.notes}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
    <SH t="Antenna Positions on Airframe"/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <KV k="GPS L1 patch" v={`Cockpit roof · ${mmi(58)} from nose tip`}/>
        <KV k="GPS separation from 49MHz" v={`${mmi(232)} (9.13") ✔ (min ${mmi(150)})`} vc={C.green}/>
        <KV k="SiK 915 MHz" v={`Belly hull · ${mmi(238)} from nose · SMA-RP bulkhead`}/>
        <KV k="49 MHz RCRS whip" v={`Dorsal spine · ${mmi(290)} from nose · ${mmi(250)} whip element`}/>
        <KV k="WiFi 2.4/5 GHz" v={`CM4-CARRIER-1 PCB · ${mmi(210)} from nose · external SMA`}/>
      </div>
      <div>
        <KV k="Zigbee 2.4 GHz (opt.)" v={`COMMS-HAT-1 · SMA-ZB on board edge`}/>
        <KV k="LoRa 915 MHz (opt.)" v={`COMMS-HAT-1 · SMA-LR on board edge`}/>
        <Note c={C.pink} ch={`SMA-ZB (Zigbee 2.4 GHz) and SMA-1 (WiFi 2.4 GHz) are both 2.4 GHz — minimum ${mmi(150)} (5.91") physical separation required. Route antennas to opposite hull surfaces if possible.`}/>
        <Note c={C.yellow} ch="All antenna cables: U.FL to SMA/SMA-RP via RG-178 (GPS, ≤100mm/3.94\") or RG-316 (49MHz, 120mm/4.72\"). WiFi from CM4 U.FL: 0.81mm semi-rigid coax ≤25mm (0.98\") to diplexer."/>
      </div>
    </div>
  </div>);
}

// ══════════════════════════════════════════════════════════════
//  NAV LIGHTS TAB
// ══════════════════════════════════════════════════════════════
function NavLightsTab(){
  const lights=[
    {id:"PORT", col:"#ff2020",name:"Red",   pos:`Left nacelle tip · ${mmi(80)} OD fairing`, arc:"≥110°",flash:"Steady",lum:"≥300 cd",reg:"ICAO Annex 2 · 14 CFR 91.209"},
    {id:"STBD", col:"#00cc00",name:"Green", pos:`Right nacelle tip · ${mmi(80)} OD fairing`,arc:"≥110°",flash:"Steady",lum:"≥300 cd",reg:"ICAO Annex 2 · 14 CFR 91.209"},
    {id:"TAIL", col:"#dddddd",name:"White", pos:`Aft hull · ${mmi(350)} from nose`,          arc:"≥140°",flash:"Steady",lum:"≥300 cd",reg:"ICAO Annex 2 · 14 CFR 91.209"},
    {id:"ACOL", col:"#ff4444",name:"Red",   pos:`Dorsal hull · ${mmi(120)} from nose`,        arc:"360°", flash:"60 FPM",lum:"≥150 cd avg",reg:"14 CFR 91.209 · FAA AC 107-2B"},
    {id:"BELLY",col:"#ffffaa",name:"White", pos:`Belly hull · ${mmi(160)} from nose`,         arc:"lower",flash:"60 FPM",lum:"≥100 cd avg",reg:"FAA AC 91-74"},
    {id:"LAND", col:"#ffff80",name:"White", pos:`Nose under · ${mmi(30)} from nose`,           arc:"fwd",  flash:"Steady (ops)",lum:"≥600 cd",reg:"FAA AC 20-74"},
  ];
  return(<div>
    <Note c={C.accent} ch="Navigation lights comply with ICAO Annex 2 and 14 CFR 91.209. For night operations under FAA Part 107, anti-collision lights visible ≥3 statute miles (2,640 yd / 2,414 m) are required. The installed WS2812C-2020 LEDs at full brightness provide this range when diffuser lenses are clear and unobscured."/>
    <div style={{overflowX:"auto",marginBottom:16}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["LIGHT","COLOR","POSITION","ARC","FLASH","LUMENS","REGULATION"]}/>
        <tbody>{lights.map((l,i)=>(<tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.02)":"transparent"}}>
          <td style={{padding:"5px 9px",color:l.col,fontWeight:"bold"}}>{l.id}</td>
          <td style={{padding:"5px 9px"}}><span style={{background:l.col,color:"#000",padding:"1px 6px",borderRadius:2,fontSize:9}}>{l.name}</span></td>
          <td style={{padding:"5px 9px",color:C.text,fontSize:9}}>{l.pos}</td>
          <td style={{padding:"5px 9px",color:C.dim}}>{l.arc}</td>
          <td style={{padding:"5px 9px",color:l.flash.includes("FPM")?C.orange:C.green}}>{l.flash}</td>
          <td style={{padding:"5px 9px",color:C.yellow}}>{l.lum}</td>
          <td style={{padding:"5px 9px",color:C.dimmer,fontSize:9}}>{l.reg}</td>
        </tr>))}</tbody>
      </table>
    </div>
    <SH t="Firmware Light States"/>
    {[["POWER ON (pre-arm)","Tail white ON · belly strobe 60 FPM · all others OFF"],
      ["ARMED","Port red · stbd green · tail white · dorsal+belly strobe 60 FPM"],
      ["LANDING / HOVER OPS","Landing light ON · all nav lights maintained"],
      ["TRANSITION","Port/stbd pulse amber 2 Hz during nacelle sweep"],
      ["LOW BATTERY ≤20%","Port+stbd alternate red/white flash 2 Hz"],
      ["FAILSAFE / RTL","All 6 LEDs flash simultaneously 2 Hz"],
      ["DISARMED","Tail white steady · strobes continue"],
    ].map(([st,desc],i)=>(<div key={i} style={{display:"flex",gap:12,padding:"6px 0",borderBottom:"1px solid rgba(0,229,255,0.07)"}}><span style={{color:C.teal,fontFamily:M,fontSize:10,minWidth:200,flexShrink:0}}>{st}</span><span style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.6}}>{desc}</span></div>))}
  </div>);
}

// ══════════════════════════════════════════════════════════════
//  BOM TAB
// ══════════════════════════════════════════════════════════════
const BOM=[
  {cat:"Propulsion",qty:2,ref:"EDF-70",part:"70mm EDF + 2500KV BLDC",desc:`${mmi(70)} ID duct · 1100g thrust @ 5S · 35A · Changesun/Freewing`,est:"$26ea"},
  {cat:"Propulsion",qty:2,ref:"ESC-40",part:"40A BLHeli32 ESC",desc:"DSHOT300 · 2–6S",est:"$20ea"},
  {cat:"Propulsion",qty:1,ref:"EDF-40",part:"40mm EDF + 4200KV BLDC",desc:`${mmi(40)} ID duct · 190g thrust @ 5S · 14A`,est:"$16"},
  {cat:"Propulsion",qty:1,ref:"ESC-25",part:"25A BLHeli32 ESC",desc:"Fwd fan ESC",est:"$12"},
  {cat:"Propulsion",qty:2,ref:"SRV-T",part:"MG90S digital servo",desc:`Metal gear · 1.8 kg·cm · ${mmi(180)} travel · nacelle tilt`,est:"$4ea"},
  {cat:"Propulsion",qty:1,ref:"SRV-N",part:"SG90 servo (fuselage nozzle)",desc:`Area ratio 82–115% · ${mmi(40)} bell · Pico GP15`,est:"$3"},
  {cat:"Propulsion",qty:2,ref:"NOZZLE-NAC",part:"Nacelle nozzle (BamJr remix CC BY 4.0)",desc:`Gear-coupled · ${mmi(70)} ID · 36→42mm (1.42\"→1.65\") exit · no servo`,est:"$6 filament"},
  {cat:"Propulsion",qty:1,ref:"NOZZLE-FUS",part:"Fuselage nozzle (BamJr remix CC BY 4.0)",desc:`Servo-actuated · ${mmi(40)} ID · SG90`,est:"$3 filament"},
  {cat:"Propulsion",qty:2,ref:"GEAR-SET",part:"Nacelle nozzle gear set (M0.5)",desc:"Sector · pinion A · bevel pair · crown pinion · ring rack",est:"$15–35/nacelle"},
  {cat:"Flt Ctrl",qty:1,ref:"PICO2",part:"Raspberry Pi Pico 2",desc:"RP2350 · 264KB · 4MB flash",est:"$5"},
  {cat:"Flt Ctrl",qty:1,ref:"TH1",part:"TRIHAT-1 (custom PCB)",desc:`${mmi(65)}×${mmi(48)} · IMU+Baro+GPS+CAN+ETH+TPM+FPV`,est:"$75"},
  {cat:"Flt Ctrl",qty:1,ref:"AIRS",part:"MS4525DO airspeed sensor",desc:"I²C · ±1 PSI · 0–155 kts range",est:"$10"},
  {cat:"Flt Ctrl",qty:1,ref:"PITOT",part:`CF pitot ${mmi(3)} + silicone tubing`,desc:`${mmi(80)} tube · 2×${mmi(80)} leads`,est:"$4"},
  {cat:"Companion",qty:1,ref:"CM4",part:"CM4 Lite 4GB WiFi",desc:"BCM2711 · 4×A72 · 4GB LPDDR4X · 802.11ac",est:"$55"},
  {cat:"Companion",qty:1,ref:"CAR1E",part:"CM4-CARRIER-1 Rev E (custom PCB)",desc:`${mmi(65)}×${mmi(52)} · CPLD write-blocker · diplexer · 2× SMA · μSD · USB hub`,est:"$28"},
  {cat:"Companion",qty:1,ref:"CH1E",part:"COMMS-HAT-1 Rev E (custom PCB)",desc:`${mmi(65)}×${mmi(48)} · NX proxy MCU · Zigbee/LoRa footprints`,est:"$68"},
  {cat:"Companion",qty:1,ref:"SIK",part:"SiK 915 MHz air unit",desc:`MAVLink 2.0 · 100 mW · range ≤${yd(1000)}`,est:"$18"},
  {cat:"Companion",qty:1,ref:"RCRS",part:"49 MHz RCRS transceiver",desc:`TDDS · 6-ch · 10 mW EIRP · range ≤${yd(500)}`,est:"$16"},
  {cat:"Companion",qty:1,ref:"CC2652",part:"CC2652P7 (opt — Zigbee/BLE/LoRa 2.4 GHz)",desc:`TI multiprotocol · +20 dBm · range ~${yd(100)}`,est:"$5"},
  {cat:"Companion",qty:1,ref:"SX1276",part:"SX1276 (opt — LoRa/Zigbee 915 MHz)",desc:`100 mW · range ${yd(1094)}–${yd(5468)} outdoor`,est:"$4"},
  {cat:"Nav Lights",qty:6,ref:"WS2812",part:"WS2812C-2020 RGB LED",desc:"5V · 2×2mm (0.08\"×0.08\") · addressable · ICAO compliant",est:"$0.50ea"},
  {cat:"Payload",qty:1,ref:"SRV-R",part:"SG90 release servo",desc:"Spring-return closed · 200g capacity",est:"$3"},
  {cat:"Payload",qty:1,ref:"WINCH",part:"N20 6V 100:1 gearmotor",desc:`Winch drive · descent rate ~0.5 ft/s loaded`,est:"$5"},
  {cat:"Payload",qty:1,ref:"SPOOL",part:`${mmi(18)} spool + Dyneema 5 m (5.5 yd)`,desc:"SK75 0.8mm · 40 kg break · 200g max payload",est:"$6"},
  {cat:"Power",qty:1,ref:"BAT-E",part:"★ 5S 4500mAh 35C (empty endurance)",desc:`420g · T/W 2.20 · ${REC_E.hMin} min hover · ${REC_E.cMin} min cruise`,est:"$45"},
  {cat:"Power",qty:1,ref:"BAT-C",part:"★ 5S 2800mAh 45C (cargo 250g)",desc:`271g · T/W ${REC_C.tw} · ${REC_C.hMin} min hover`,est:"$38"},
  {cat:"Power",qty:1,ref:"BEC",part:"5V 3A switching BEC",desc:"CM4+Pico+servos+radios+LEDs",est:"$5"},
  {cat:"Power",qty:1,ref:"PDIST",part:"XT60 distribution board",desc:"4× XT30 · 12AWG mains",est:"$8"},
  {cat:"Airframe",qty:1,ref:"HULL",part:"Serenity hull PETG (11 prints) — CC BY 4.0",desc:`Peter Farell remix · ${mmi(365)} · ~148g · 8% gyroid`,est:"$19 filament"},
  {cat:"Airframe",qty:2,ref:"NAC",part:`70mm nacelle pods CF-PETG ${mmi(80)} OD`,desc:"LED recess · pivot seat · gear channels",est:"$7 filament"},
  {cat:"Airframe",qty:1,ref:"BELL",part:`Serenity engine bell PETG ${mmi(365)}`,desc:`${mmi(76)} ID housing · nozzle bayonet mount`,est:"$5 filament"},
  {cat:"Airframe",qty:1,ref:"KEEL",part:`CF keel 6×3mm (0.24"×0.12") × ${mmi(385)}`,desc:"Dorsal structural spine",est:"$6"},
  {cat:"Airframe",qty:2,ref:"SPAR",part:`CF tube ${mmi(12)} OD × ${mmi(300)}`,desc:"Outrigger wing spars",est:"$8ea"},
  {cat:"Airframe",qty:4,ref:"SKID",part:"TPU 95A skid feet",desc:"Crash-absorbing landing pads",est:"$2 filament"},
  {cat:"Wiring",qty:1,ref:"JSTKIT",part:"JST-GH 1.25mm connector kit",desc:"4+6pin · crimp tool · pre-made cables",est:"$14"},
  {cat:"Wiring",qty:1,ref:"ETH-C",part:`6-pin JST-GH Ethernet cable ${mmi(150)}`,desc:"Twisted pairs · TRIHAT-1↔COMMS-HAT-1",est:"$4"},
  {cat:"Wiring",qty:1,ref:"CAN-C",part:`4-pin JST-GH CAN FD cable ${mmi(120)}`,desc:"Twisted CANH/CANL · TRIHAT-1↔COMMS-HAT-1",est:"$3"},
  {cat:"Wiring",qty:1,ref:"WIRE",part:"Silicone wire assortment",desc:"12AWG power · 22AWG signal · 28AWG data",est:"$12"},
];
const CAT_COL={Propulsion:C.orange,"Flt Ctrl":C.accent,Companion:C.green,"Nav Lights":C.yellow,Payload:C.pink,Power:C.yellow,Airframe:C.teal,Wiring:C.purple};
const CATS=[...new Set(BOM.map(b=>b.cat))];

function BomTab(){
  const [cf,setCf]=useState("All");
  const rows=cf==="All"?BOM:BOM.filter(b=>b.cat===cf);
  return(<div>
    <Note c={C.lime} ch='CC BY 4.0 items marked in the BOM. "★" = recommended battery option for the mission profile. Select ONE battery option per aircraft build. Both nacelle nozzle sets and fuselage nozzle are BamJr remixes (CC BY 4.0); gear sets are original Steve Griffing design (CC BY 4.0).'/>
    <div style={{display:"flex",gap:5,flexWrap:"wrap",marginBottom:12,marginTop:10}}>
      {["All",...CATS].map(c=>(<button key={c} onClick={()=>setCf(c)} style={{background:cf===c?`${CAT_COL[c]||C.accent}20`:"transparent",border:`1px solid ${cf===c?CAT_COL[c]||C.accent:"rgba(0,229,255,0.14)"}`,color:cf===c?CAT_COL[c]||C.accent:C.dimmer,padding:"3px 10px",fontFamily:M,fontSize:9,cursor:"pointer",borderRadius:2}}>{c}</button>))}
    </div>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["CAT","QTY","REF","COMPONENT","DESCRIPTION","~USD"]}/>
        <tbody>{rows.map((b,i)=>(<tr key={i} style={{background:b.part.includes("★")||b.part.includes("CC BY")||b.ref.includes("NOZZLE")||b.ref.includes("HULL")?"rgba(163,230,53,0.04)":i%2===0?"rgba(0,229,255,0.02)":"transparent",verticalAlign:"top"}}>
          <td style={{padding:"5px 8px"}}><span style={{color:CAT_COL[b.cat]||C.dim,border:`1px solid ${CAT_COL[b.cat]||C.dim}40`,padding:"1px 5px",borderRadius:2,fontSize:9,whiteSpace:"nowrap"}}>{b.cat}</span></td>
          <td style={{padding:"5px 8px",color:C.accent,fontWeight:"bold",textAlign:"center"}}>{b.qty}</td>
          <td style={{padding:"5px 8px",color:C.yellow,fontSize:9,whiteSpace:"nowrap"}}>{b.ref}</td>
          <td style={{padding:"5px 8px",color:C.text}}>{b.part}</td>
          <td style={{padding:"5px 8px",color:C.dim,fontSize:9,lineHeight:1.5}}>{b.desc}</td>
          <td style={{padding:"5px 8px",color:C.green,fontWeight:"bold",whiteSpace:"nowrap"}}>{b.est}</td>
        </tr>))}</tbody>
        {cf==="All"&&(<tfoot><tr style={{borderTop:`1px solid ${C.border}`}}><td colSpan={5} style={{padding:"8px 8px",color:C.accent,textAlign:"right",fontSize:11}}>TOTAL ESTIMATED (one battery · with optional CC2652P7+SX1276)</td><td style={{padding:"8px 8px",color:C.yellow,fontSize:16,fontWeight:"bold"}}>$670–760</td></tr></tfoot>)}
      </table>
    </div>
  </div>);
}

// ══════════════════════════════════════════════════════════════
//  SBOM TAB
// ══════════════════════════════════════════════════════════════
const SBOM=[
  {sys:"Pico 2",layer:"Core",     comp:"Pico SDK 2.x",                        ver:"≥2.0",    lic:"BSD-3",     role:"RP2350 HAL · PIO · DMA · multicore"},
  {sys:"Pico 2",layer:"AHRS",     comp:"Mahony AHRS (port)",                   ver:"custom",  lic:"Apache-2",  role:"Gyro+accel → quaternion · 500 Hz"},
  {sys:"Pico 2",layer:"Control",  comp:"Custom PID cascade (Steve Griffing)",  ver:"v1.0",    lic:"CC BY 4.0", role:"Rate/attitude/position PID · 500 Hz"},
  {sys:"Pico 2",layer:"Protocol", comp:"MAVLink 2.0 C lib",                    ver:"2.0",     lic:"MIT",       role:"MAVLink encode/decode over UART + W5500 UDP"},
  {sys:"Pico 2",layer:"Driver",   comp:"ICM-42688-P · BMP388 · MS4525DO · M10Q · MCP2518FD · W5500 · TPM · WS2812 · DSHOT300",ver:"custom",lic:"BSD-3/MIT",role:"All sensor and peripheral drivers"},
  {sys:"Pico 2",layer:"Algorithm",comp:"TDDS channel selector (Steve Griffing)",ver:"v1.0",   lic:"CC BY 4.0", role:"49 MHz RCRS TDDS · SNR scan · control priority"},
  {sys:"Pico 2",layer:"Algorithm",comp:"Variable nozzle controller (Steve Griffing)",ver:"v1.0",lic:"CC BY 4.0",role:"Gear nozzle estimation · fuselage nozzle GP15 PWM"},
  {sys:"CM4",   layer:"OS",       comp:"RPi OS Lite 64-bit",                   ver:"bookworm",lic:"Mixed GPL", role:"Debian Linux headless · kernel 6.6+"},
  {sys:"CM4",   layer:"Middleware",comp:"mavlink-router + MAVSDK-Python",      ver:"≥3.0/2.0",lic:"Apache-2/BSD-3",role:"MAVLink router · drone API"},
  {sys:"CM4",   layer:"Middleware",comp:"python-can + dronecan + pymavlink",   ver:"≥4.0/1.0/2.4",lic:"LGPL/MIT/LGPL",role:"CAN FD · DroneCAN · MAVLink logging"},
  {sys:"CM4",   layer:"Security", comp:"tpm2-tools + tpm2-tss",                ver:"≥5.0/4.0",lic:"BSD-2",     role:"TPM 2.0 provisioning + attestation"},
  {sys:"CM4",   layer:"Security", comp:"SELinux policy (Steve Griffing)",       ver:"v1.0",    lic:"CC BY 4.0", role:"log_storage_t · noexec enforcement"},
  {sys:"CM4",   layer:"Security", comp:"TrustZone secure monitor",              ver:"custom",  lic:"CC BY 4.0", role:"BCM2711 TrustZone · NX for SPI-SD pages"},
  {sys:"CM4",   layer:"Driver",   comp:"SX1276 LoRaLib",                        ver:"≥5.0",    lic:"MIT",       role:`LoRa 915 MHz · range ${yd(1094)}–${yd(5468)}`},
  {sys:"CM4",   layer:"Comms",    comp:"SiK firmware (air unit)",               ver:"2.x",     lic:"GPL-3",     role:`915 MHz MAVLink · ≤${yd(1000)} range`},
  {sys:"CPLD",  layer:"RTL",      comp:"Write-blocker Verilog (Steve Griffing)",ver:"v1.0",    lic:"CC BY 4.0", role:"MachXO2-256 SDIO CMD filter · NIST SP 800-72"},
  {sys:"STM32", layer:"Firmware", comp:"NX proxy firmware (Steve Griffing)",    ver:"v1.0",    lic:"CC BY 4.0", role:"SPI proxy · SHA-256 audit · CMD write block"},
  {sys:"GCS",   layer:"App",      comp:"QGroundControl",                        ver:"≥4.3",    lic:"GPL-3",     role:"Flight planning · telemetry · parameters"},
];
const SBOM_SYS=[...new Set(SBOM.map(s=>s.sys))];
const LAYER_COL={Core:C.accent,AHRS:C.teal,Control:C.orange,Protocol:C.orange,Driver:C.teal,Algorithm:C.pink,OS:C.green,Middleware:C.purple,Security:C.yellow,Comms:C.accent,App:C.green,RTL:C.lime,Firmware:C.orange};

function SbomTab(){
  const [sf,setSf]=useState("All");
  const rows=sf==="All"?SBOM:SBOM.filter(s=>s.sys===sf);
  return(<div>
    <Note c={C.lime} ch="CC BY 4.0 components are original work by Steve Griffing, PE(CSE), CISSP-ISSEP, CPP. GPL-3 components must remain open-source if redistributed. TI CC2652P7 Z-Stack under TI TSPA — commercial use requires review of TI terms. BamJr nozzle remix: CC BY 4.0 — attribution required in all derivative works."/>
    <div style={{display:"flex",gap:5,flexWrap:"wrap",marginBottom:12,marginTop:10}}>
      {["All",...SBOM_SYS].map(s=>(<button key={s} onClick={()=>setSf(s)} style={{background:sf===s?"rgba(0,229,255,0.09)":"transparent",border:`1px solid ${sf===s?C.accent:"rgba(0,229,255,0.14)"}`,color:sf===s?C.accent:C.dimmer,padding:"3px 10px",fontFamily:M,fontSize:9,cursor:"pointer",borderRadius:2}}>{s}</button>))}
    </div>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["SYSTEM","LAYER","COMPONENT","VERSION","LICENSE","ROLE"]}/>
        <tbody>{rows.map((s,i)=>(<tr key={i} style={{background:s.lic.includes("CC BY")?"rgba(163,230,53,0.04)":i%2===0?"rgba(0,229,255,0.02)":"transparent",verticalAlign:"top"}}>
          <td style={{padding:"5px 8px",color:s.sys==="Pico 2"?C.accent:s.sys==="CM4"?C.green:s.sys==="CPLD"?C.lime:s.sys==="STM32"?C.orange:C.purple,fontWeight:"bold",whiteSpace:"nowrap",fontSize:9}}>{s.sys}</td>
          <td style={{padding:"5px 8px"}}><span style={{color:LAYER_COL[s.layer]||C.dim,border:`1px solid ${LAYER_COL[s.layer]||C.dim}40`,padding:"1px 5px",borderRadius:2,fontSize:8,whiteSpace:"nowrap"}}>{s.layer}</span></td>
          <td style={{padding:"5px 8px",color:s.lic.includes("CC BY")?C.lime:C.text,whiteSpace:"nowrap"}}>{s.comp}</td>
          <td style={{padding:"5px 8px",color:C.dimmer,whiteSpace:"nowrap",fontSize:9}}>{s.ver}</td>
          <td style={{padding:"5px 8px",whiteSpace:"nowrap",fontSize:9}}>
            <span style={{color:s.lic.includes("CC BY")?C.lime:s.lic.includes("GPL")?C.orange:C.yellow,border:`1px solid ${s.lic.includes("CC BY")?C.lime:s.lic.includes("GPL")?C.orange:C.yellow}44`,padding:"1px 5px",borderRadius:2}}>{s.lic}</span>
          </td>
          <td style={{padding:"5px 8px",color:C.dim,fontSize:9,lineHeight:1.5}}>{s.role}</td>
        </tr>))}</tbody>
      </table>
    </div>
  </div>);
}

// ══════════════════════════════════════════════════════════════
//  APP
// ══════════════════════════════════════════════════════════════
const TABS=["Overview","License","Airframe","Propulsion","Battery","Radios & Ranges","Nav Lights","BOM","SBOM"];

const HEADER_NOTE=`© 2025 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP · CC BY 4.0
Hull: Peter Farell (CC BY 4.0) · Nozzle: BamJr (CC BY 4.0)
Visual inspiration: Firefly/Serenity © Joss Whedon / Mutant Enemy / Universal Pictures`;

_ODFontLoader();
export default function App(){
  const [tab,setTab]=useState("Overview");
  return(<div style={{minHeight:"100vh",background:C.bg,color:C.text,fontFamily:M}}>
    <Grid/>
    {/* License header band */}
    <div style={{background:"rgba(163,230,53,0.06)",borderBottom:`1px solid ${C.lime}33`,padding:"6px 24px",fontFamily:M,fontSize:8,color:`${C.lime}70`,lineHeight:1.6,whiteSpace:"pre-line"}}>{HEADER_NOTE}</div>
    <div style={{position:"relative",zIndex:1,borderBottom:`1px solid ${C.border}`,padding:"14px 24px 12px"}}>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",flexWrap:"wrap",gap:12}}>
        <div>
          <div style={{color:"rgba(163,230,53,0.3)",fontSize:9,letterSpacing:"0.2em",marginBottom:4}}>SERENITY-CLASS TILTROTOR UAV · REV F · CC BY 4.0</div>
          <h1 style={{margin:0,fontSize:18,fontWeight:"normal",color:"#fff",letterSpacing:"0.07em"}}>SERENITY DRONE — MASTER SPEC</h1>
          <div style={{color:"rgba(0,229,255,0.45)",fontSize:10,marginTop:3}}>
            Steve Griffing, PE(CSE), CISSP-ISSEP, CPP · 70mm nacelles · 40mm fwd · gear nozzle · ft / kts / yd units
          </div>
        </div>
        <div style={{textAlign:"right",fontFamily:M}}>
          <div style={{color:C.yellow,fontSize:12,fontWeight:"bold"}}>{REC_E.auw}g empty · T/W {REC_E.tw}</div>
          <div style={{color:C.orange,fontSize:11}}>{REC_C.auw}g cargo · T/W {REC_C.tw}</div>
          <div style={{color:C.dimmer,fontSize:9,marginTop:2}}>{mmi(365)} hull · {mmi(680)} span</div>
        </div>
      </div>
      <div style={{display:"flex",gap:2,marginTop:12,flexWrap:"wrap"}}>
        {TABS.map(t=>(<button key={t} onClick={()=>setTab(t)} style={{background:tab===t?"rgba(0,229,255,0.09)":"transparent",border:`1px solid ${tab===t?C.accent:"rgba(0,229,255,0.12)"}`,color:tab===t?C.accent:C.dimmer,padding:"4px 11px",fontFamily:M,fontSize:9,cursor:"pointer",letterSpacing:"0.06em",transition:"all 0.12s"}}>{t}</button>))}
      </div>
    </div>
    <div style={{position:"relative",zIndex:1,padding:"20px 24px",maxWidth:1060,margin:"0 auto"}}>
      {tab==="Overview"       && <OverviewTab/>}
      {tab==="License"        && <LicenseTab/>}
      {tab==="Airframe"       && <AirframeTab/>}
      {tab==="Propulsion"     && <PropulsionTab/>}
      {tab==="Battery"        && <BatteryTab/>}
      {tab==="Radios & Ranges"&& <RadiosTab/>}
      {tab==="Nav Lights"     && <NavLightsTab/>}
      {tab==="BOM"            && <BomTab/>}
      {tab==="SBOM"           && <SbomTab/>}
    </div>
    <div style={{position:"relative",zIndex:1,borderTop:`1px solid ${C.border}`,padding:"10px 24px",display:"flex",justifyContent:"space-between",flexWrap:"wrap",gap:6}}>
      <span style={{color:"rgba(163,230,53,0.2)",fontSize:8,letterSpacing:"0.1em"}}>© 2025 STEVE GRIFFING PE(CSE) CISSP-ISSEP CPP · CC BY 4.0 · HULL: PETER FARELL (CC BY 4.0) · NOZZLE: BAmJr (CC BY 4.0) · VISUAL INSPIRATION: FIREFLY/SERENITY © JOSS WHEDON / MUTANT ENEMY / UNIVERSAL PICTURES</span>
    </div>
  </div>);
}
