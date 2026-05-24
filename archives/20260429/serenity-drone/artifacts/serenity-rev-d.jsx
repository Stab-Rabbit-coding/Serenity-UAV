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
  dim:"rgba(255,255,255,0.90)", dimmer:"rgba(255,255,255,0.80)", text:"rgba(255,255,255,0.82)",
};
const M = "'OpenDyslexic Mono','OpenDyslexic','OpenDyslexicMono',monospace";

// ════════════════════════════════════════════════════════════════
//  PHYSICS — Rev D  (70mm primary / 64mm alternate, 40mm fwd)
// ════════════════════════════════════════════════════════════════
// 70mm 12-blade @ 5S: 1100g thrust, 35A max, 72g/unit
// 64mm 12-blade @ 5S:  880g thrust, 30A max, 58g/unit
// 40mm 11-blade @ 5S:  190g thrust, 14A max, 30g
const T70=1100, T64=880, T40=190;
const I70=35, I64=30, I40=14;
const BAT_V=18.5, AV_A=2.0;  // avionics equiv amps

// AUW_BASE without battery (g) — verified by component sum
const BASE_70=582, BASE_64=548;

// hover current model: I ∝ T^1.5
const hovI=(auw,Imax,Tmax)=>Imax*Math.pow(auw/2/Tmax,1.5)*2+AV_A;
const crsA=(I40frac,Imax70,trim)=>I40*I40frac+Imax70*Math.pow(trim,1.5)*2+AV_A;
const CRUISE_A=I40*0.88+I70*Math.pow(0.14,1.5)*2+AV_A;  // primary cruise

function batRow(id,name,brand,mass,cap,Cc,note,base,T_nac,Imax,Tmax,payload=0){
  const auw=base+mass+payload;
  const tw=(T_nac/auw).toFixed(2);
  const ok=T_nac/auw>=2.0;
  const hA=hovI(auw,Imax,Tmax);
  const hMin=(cap/1000*0.8/hA*60).toFixed(1);
  const cMin=(cap/1000*0.8/CRUISE_A*60).toFixed(1);
  const maxA=cap/1000*Cc;
  return{id,name,brand,mass,cap,Cc,note,auw,tw,ok,hA,hMin,cMin,maxA,payload};
}

// ── Battery tables ──────────────────────────────────────────────
// EMPTY — 70mm
const BATS_EMPTY_70=[
  batRow("A","5S 2800mAh 45C","Tattu/GNB",    271,2800,45,"",BASE_70,T70*2,I70,T70),
  batRow("B","5S 3500mAh 45C","Gens Ace",     328,3500,45,"",BASE_70,T70*2,I70,T70),
  batRow("C","5S 4000mAh 35C","Tattu R-Line", 376,4000,35,"",BASE_70,T70*2,I70,T70),
  batRow("D","5S 4500mAh 35C","GNB/CNHL",     420,4500,35,"★ MAX ENDURANCE",BASE_70,T70*2,I70,T70),
  batRow("E","5S 5000mAh 30C","Gens Ace",     465,5000,30,"C-rating marginal",BASE_70,T70*2,I70,T70),
  batRow("F","5S 5500mAh 25C","Various",      520,5500,25,"Exceeds T/W ✗",BASE_70,T70*2,I70,T70),
];
// CARGO 250g — 70mm
const BATS_CARGO_70=[
  batRow("A","5S 1800mAh 75C","Tattu Funfly", 190,1800,75,"Light",BASE_70,T70*2,I70,T70,250),
  batRow("B","5S 2200mAh 75C","CNHL/Tattu",  220,2200,75,"",BASE_70,T70*2,I70,T70,250),
  batRow("C","5S 2500mAh 60C","Tattu R-Line",248,2500,60,"",BASE_70,T70*2,I70,T70,250),
  batRow("D","5S 2800mAh 45C","Tattu/GNB",   271,2800,45,"★ MAX CARGO ENDURANCE",BASE_70,T70*2,I70,T70,250),
  batRow("E","5S 3000mAh 45C","Tattu",       292,3000,45,"T/W marginal",BASE_70,T70*2,I70,T70,250),
];
const REC_EMPTY=BATS_EMPTY_70.find(b=>b.id==="D");
const REC_CARGO=BATS_CARGO_70.find(b=>b.id==="D");

// ── hull geometry ───────────────────────────────────────────────
const SC=(mm)=>mm*1.28, NX=55, xp=(mm)=>NX+SC(mm);
const PROF=[[0,0],[8,10],[22,18],[40,30],[58,36],[88,37],[120,42],[140,42],[165,40],[190,36],[220,29],[252,18],[260,16],[278,24],[305,29],[330,28],[360,22]];
function hullOutline(CY){
  const up=PROF.map(([x,y])=>[xp(x),CY-SC(y)]);
  const lo=[...PROF].reverse().map(([x,y])=>[xp(x),CY+SC(y)]);
  return[...up,...lo].map((p,i)=>i===0?`M${p[0]},${p[1]}`:`L${p[0]},${p[1]}`).join(" ")+"Z";
}
function Arms({CY,rx=SC(35),ry=SC(15)}){
  return[-1,1].map(side=>(
    <g key={side}>
      <line x1={xp(128)} y1={CY+side*SC(50)} x2={xp(160)} y2={CY+side*SC(340)} stroke={C.accent} strokeWidth={1.4}/>
      <ellipse cx={xp(155)} cy={CY+side*SC(340)} rx={rx} ry={ry} fill="rgba(0,229,255,0.04)" stroke={C.accent} strokeWidth={1.1}/>
    </g>
  ));
}

// ── primitives ──────────────────────────────────────────────────
const SH=({t,c=C.accent,mt=22})=>(<div style={{display:"flex",alignItems:"center",gap:10,marginBottom:14,marginTop:mt}}><div style={{width:3,height:17,background:c}}/><span style={{color:c,fontFamily:M,fontSize:13,letterSpacing:"0.13em",textTransform:"uppercase",fontWeight:"normal"}}>{t}</span></div>);
const KV=({k,v,vc=C.text,u=""})=>(<div style={{display:"flex",justifyContent:"space-between",padding:"5px 0",borderBottom:"1px solid rgba(0,229,255,0.07)",alignItems:"baseline"}}><span style={{color:C.dim,fontFamily:M,fontSize:11}}>{k}</span><span style={{color:vc,fontFamily:M,fontSize:11}}>{v}{u&&<span style={{color:C.accent,marginLeft:4,fontSize:10}}>{u}</span>}</span></div>);
const Note=({c=C.dim,ch})=>(<div style={{marginTop:8,marginBottom:6,color:c,fontFamily:M,fontSize:10,lineHeight:1.85,padding:"8px 12px",borderLeft:`2px solid ${c}55`,background:`${c}07`,borderRadius:3}}>{ch}</div>);
const Warn=({ch})=>(<div style={{marginTop:8,color:C.yellow,fontFamily:M,fontSize:10,lineHeight:1.8,padding:"7px 12px",borderLeft:`2px solid ${C.yellow}`,background:"rgba(255,230,0,0.05)",borderRadius:3}}>⚠ {ch}</div>);
const Good=({ch})=>(<div style={{marginTop:8,color:C.green,fontFamily:M,fontSize:10,lineHeight:1.8,padding:"7px 12px",borderLeft:`2px solid ${C.green}`,background:"rgba(74,222,128,0.05)",borderRadius:3}}>✓ {ch}</div>);
function TH({cols}){return(<thead><tr>{cols.map(h=>(<th key={h} style={{padding:"6px 9px",borderBottom:`1px solid ${C.border}`,color:C.accent,textAlign:"left",fontWeight:"normal",fontSize:10,letterSpacing:"0.06em",whiteSpace:"nowrap",opacity:.85}}>{h}</th>))}</tr></thead>);}
function Grid(){return(<svg style={{position:"fixed",inset:0,width:"100%",height:"100%",pointerEvents:"none",zIndex:0}}><defs><pattern id="sg" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0L0 0 0 20" fill="none" stroke="rgba(0,229,255,0.035)" strokeWidth={0.5}/></pattern><pattern id="lg" width="100" height="100" patternUnits="userSpaceOnUse"><rect width="100" height="100" fill="url(#sg)"/><path d="M100 0L0 0 0 100" fill="none" stroke="rgba(0,229,255,0.065)" strokeWidth={1}/></pattern></defs><rect width="100%" height="100%" fill="url(#lg)"/></svg>);}

function BatTable({rows,title,c}){
  return(<div style={{marginBottom:20}}>
    <div style={{color:c,fontFamily:M,fontSize:11,fontWeight:"bold",marginBottom:8,letterSpacing:"0.06em"}}>{title}</div>
    <div style={{overflowX:"auto"}}>
    <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
      <TH cols={["ID","BATTERY","MASS","CAP","C","MAX A","AUW","T/W","HOVER","CRUISE","NOTE"]}/>
      <tbody>{rows.map((b,i)=>(
        <tr key={i} style={{background:b.note.includes("★")?"rgba(74,222,128,0.07)":i%2===0?"rgba(0,229,255,0.02)":"transparent",border:b.note.includes("★")?`1px solid rgba(74,222,128,0.2)`:"none"}}>
          <td style={{padding:"5px 9px",color:C.yellow,fontWeight:"bold"}}>{b.id}</td>
          <td style={{padding:"5px 9px",color:C.text,whiteSpace:"nowrap"}}>{b.name}</td>
          <td style={{padding:"5px 9px",color:C.orange}}>{b.mass}g</td>
          <td style={{padding:"5px 9px",color:C.text}}>{b.cap}</td>
          <td style={{padding:"5px 9px",color:C.text}}>{b.Cc}C</td>
          <td style={{padding:"5px 9px",color:b.maxA>=70?C.green:C.red}}>{b.maxA.toFixed(0)}A</td>
          <td style={{padding:"5px 9px",color:C.text}}>{b.auw}g</td>
          <td style={{padding:"5px 9px",color:b.ok?C.green:C.red,fontWeight:"bold"}}>{b.tw}</td>
          <td style={{padding:"5px 9px",color:b.ok?C.yellow:C.dimmer,fontWeight:b.note.includes("★")?"bold":"normal"}}>{b.ok?b.hMin+" min":"—"}</td>
          <td style={{padding:"5px 9px",color:b.ok?C.teal:C.dimmer}}>{b.ok?b.cMin+" min":"—"}</td>
          <td style={{padding:"5px 9px",color:b.note.includes("★")?C.green:b.ok?C.dim:C.red,fontSize:9}}>{b.note||"OK"}</td>
        </tr>
      ))}</tbody>
    </table></div>
  </div>);
}

// ════════════════════════════════════════════════════════════════
//  TAB 1 — OVERVIEW
// ════════════════════════════════════════════════════════════════
function OverviewTab(){
  return(<div>
    <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:12,marginBottom:20}}>
      {[
        {l:"AUW — Empty (rec.)",v:`${REC_EMPTY.auw}g`,c:C.yellow,s:`${REC_EMPTY.name}`},
        {l:"AUW — Cargo 250g (rec.)",v:`${REC_CARGO.auw}g`,c:C.orange,s:`${REC_CARGO.name}`},
        {l:"T/W (empty, nacelle)",v:`${REC_EMPTY.tw}:1`,c:C.green,s:"70mm @ 5S"},
        {l:"Endurance (empty hover)",v:`${REC_EMPTY.hMin} min`,c:C.teal,s:"80% usable"},
      ].map((s,i)=>(<div key={i} style={{padding:"10px 12px",border:`1px solid ${s.c}44`,background:`${s.c}07`,borderRadius:4}}><div style={{color:C.dim,fontFamily:M,fontSize:9,letterSpacing:"0.08em",marginBottom:3}}>{s.l}</div><div style={{color:s.c,fontFamily:M,fontSize:20,fontWeight:"bold"}}>{s.v}</div><div style={{color:C.dimmer,fontFamily:M,fontSize:9,marginTop:2}}>{s.s}</div></div>))}
    </div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="Rev D Changes" mt={0} c={C.orange}/>
        {[
          ["Nacelle EDFs","65mm → 70mm (primary) · 64mm (alternate) — both widely stocked"],
          ["Fuselage EDF","35mm → 40mm · more thrust + better cruise efficiency"],
          ["Variable nozzle","Remix of BamJr thing:2991269 · servo-actuated flap ring on Serenity engine bell"],
          ["Hull scale","+5mm length (365mm) to accommodate 40mm EDF bell · proportions preserved"],
          ["Battery options","Two scenarios: max empty endurance · max cargo (250g) endurance"],
          ["TWR (70mm empty)","2.00:1 → 2.45:1 range depending on battery choice"],
          ["TWR (70mm cargo)","2.01:1 (2800mAh, tight but meets requirement)"],
        ].map(([k,v],i)=>(<KV key={i} k={k} v={v}/>))}
      </div>
      <div>
        <SH t="System Summary" mt={0}/>
        <KV k="Hull" v="Serenity Firefly-class · 365mm · PETG/CF-PETG · scaled +5mm for 40mm bell"/>
        <KV k="Nacelles (primary)" v="2× 70mm 12-blade EDF · 1100g each · 2200g total" vc={C.green}/>
        <KV k="Nacelles (alt)" v="2× 64mm 12-blade EDF · 880g each · 1760g total"/>
        <KV k="Fuselage EDF" v="40mm 11-blade EDF + variable nozzle · 190g thrust" vc={C.teal}/>
        <KV k="Variable nozzle" v="BamJr remix · SG90 · 80–115% area ratio · Pico GP15"/>
        <KV k="Controllers" v="Pico 2 + TRIHAT-1 · CM4 Lite 4GB + CARRIER + COMMS-HAT-1"/>
        <KV k="Radios" v="SiK 915MHz + 49MHz RCRS TDDS · ETH+CAN FD inter-board"/>
        <KV k="Nav lights" v="6× WS2812C · ICAO+14CFR compliant"/>
        <KV k="Payload" v="250g · winch + release · 70×50×35mm bay"/>
        <KV k="Rec. battery (empty)" v={`${REC_EMPTY.name} · ${REC_EMPTY.auw}g · T/W ${REC_EMPTY.tw}`} vc={C.green}/>
        <KV k="Rec. battery (cargo)" v={`${REC_CARGO.name} · ${REC_CARGO.auw}g · T/W ${REC_CARGO.tw}`} vc={C.yellow}/>
        <KV k="BOM estimate" v="$600–700" vc={C.yellow}/>
      </div>
    </div>
    <SH t="Revision History"/>
    {[
      {r:"Rev A",d:"60mm nacelles + 30mm fwd · T/W 1.87 ✗"},
      {r:"Rev B",d:"65mm nacelles + 35mm fwd · T/W 2.19 ✓ · +36g"},
      {r:"Rev C",d:"Battery analysis · nav lights · antenna · ETH/CAN wiring · BOM/SBOM"},
      {r:"Rev D",d:"70mm (or 64mm) nacelles + 40mm fwd + variable nozzle · dual battery scenario · build guide",cur:true},
    ].map((r,i)=>(<div key={i} style={{display:"flex",gap:10,padding:"6px 0",borderBottom:"1px solid rgba(0,229,255,0.07)"}}><span style={{color:r.cur?C.green:C.dim,fontFamily:M,fontSize:10,minWidth:44,fontWeight:r.cur?"bold":"normal"}}>{r.r}</span><span style={{color:C.dimmer,fontFamily:M,fontSize:10,lineHeight:1.6}}>{r.d}</span></div>))}
  </div>);
}

// ════════════════════════════════════════════════════════════════
//  TAB 2 — BATTERY
// ════════════════════════════════════════════════════════════════
function BatteryTab(){
  const [view,setView]=useState("empty");
  const maxEmpty=Math.floor(T70*2/2-BASE_70);  // max g for T/W=2.0 exactly
  const maxCargo=Math.floor(T70*2/2-BASE_70-250);
  return(<div>
    <SH t="T/W ≥ 2.0 Constraint (70mm EDFs)" mt={0}/>
    <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:12,marginBottom:18}}>
      {[
        {l:"AUW_BASE (no battery/payload)",v:`${BASE_70}g`,c:C.dim},
        {l:"Max battery · empty",v:`${maxEmpty}g`,c:C.green,s:"for T/W = 2.0 min"},
        {l:"Max battery · 250g cargo",v:`${maxCargo}g`,c:C.orange,s:"for T/W = 2.0 min"},
        {l:"Nacelle thrust",v:"2200g",c:C.accent},
      ].map((s,i)=>(<div key={i} style={{padding:"10px 12px",border:`1px solid ${s.c||C.dim}44`,background:`${s.c||C.dim}07`,borderRadius:4}}><div style={{color:C.dim,fontFamily:M,fontSize:9,marginBottom:3}}>{s.l}</div><div style={{color:s.c||C.dim,fontFamily:M,fontSize:18,fontWeight:"bold"}}>{s.v}</div>{s.s&&<div style={{color:C.dimmer,fontFamily:M,fontSize:9,marginTop:2}}>{s.s}</div>}</div>))}
    </div>
    <div style={{display:"flex",gap:6,marginBottom:16}}>
      {[["empty","Max Empty Endurance"],["cargo","250g Cargo Mission"]].map(([v,l])=>(
        <button key={v} onClick={()=>setView(v)} style={{background:view===v?"rgba(0,229,255,0.1)":"transparent",border:`1px solid ${view===v?C.accent:"rgba(0,229,255,0.15)"}`,color:view===v?C.accent:C.dimmer,padding:"5px 14px",fontFamily:M,fontSize:10,cursor:"pointer",borderRadius:2}}>{l}</button>
      ))}
    </div>
    {view==="empty"&&(<>
      <BatTable rows={BATS_EMPTY_70} title="EMPTY — 70mm NACELLES — MAX ENDURANCE" c={C.green}/>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
        <div>
          <SH t={`Recommended (Empty): ${REC_EMPTY.name}`} mt={0} c={C.green}/>
          <KV k="AUW" v={`${REC_EMPTY.auw}g`} vc={C.yellow}/>
          <KV k="T/W" v={`${REC_EMPTY.tw}:1`} vc={C.green}/>
          <KV k="Hover endurance" v={`${REC_EMPTY.hMin} min`} vc={C.yellow}/>
          <KV k="Cruise endurance" v={`${REC_EMPTY.cMin} min`} vc={C.teal}/>
          <KV k="Max discharge" v={`${REC_EMPTY.maxA.toFixed(0)}A`} vc={C.green}/>
          <KV k="Peak draw (all fans)" v="~82A" vc={C.green}/>
          <KV k="Dim (typ)" v="152 × 46 × 34 mm"/>
          <KV k="Connector" v="XT60 · 12AWG leads"/>
          <KV k="Brands" v="Tattu Funfly 4500 · GNB 4500 · CNHL 4500"/>
        </div>
        <div>
          <SH t="Endurance bar (empty, T/W ≥ 2.0)" mt={0} c={C.teal}/>
          {BATS_EMPTY_70.filter(b=>b.ok).map(b=>{
            const maxH=Math.max(...BATS_EMPTY_70.filter(x=>x.ok).map(x=>parseFloat(x.hMin)));
            return(<div key={b.id} style={{display:"flex",alignItems:"center",gap:8,marginBottom:7}}>
              <span style={{color:b.note.includes("★")?C.green:C.yellow,fontFamily:M,fontSize:9,minWidth:18}}>{b.id}</span>
              <span style={{color:C.dim,fontFamily:M,fontSize:9,minWidth:145,whiteSpace:"nowrap"}}>{b.name}</span>
              <div style={{flex:1,background:"rgba(255,255,255,0.05)",borderRadius:2,height:10}}>
                <div style={{width:`${parseFloat(b.hMin)/maxH*100}%`,height:"100%",background:b.note.includes("★")?C.green:C.teal,opacity:.7,borderRadius:2}}/>
              </div>
              <span style={{color:b.note.includes("★")?C.green:C.teal,fontFamily:M,fontSize:9,minWidth:46}}>{b.hMin}m</span>
            </div>);
          })}
          <Warn ch="5S 5000mAh at 30C delivers only 150A peak — just above the 82A worst-case. Use only high-quality cells (Gens Ace G-Tech, Tattu). Upgrade to 35C if aggressive manoeuvres are planned."/>
        </div>
      </div>
    </>)}
    {view==="cargo"&&(<>
      <div style={{background:"rgba(244,114,182,0.05)",border:`1px solid rgba(244,114,182,0.2)`,borderRadius:4,padding:"10px 14px",marginBottom:16,fontFamily:M,fontSize:11,color:C.dim}}>
        Payload mass: <span style={{color:C.pink,fontWeight:"bold"}}>250g</span> · added to AUW. Max battery reduced to <span style={{color:C.orange}}>{maxCargo}g</span> to maintain T/W ≥ 2.0.
      </div>
      <BatTable rows={BATS_CARGO_70} title="250g CARGO — 70mm NACELLES" c={C.orange}/>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
        <div>
          <SH t={`Recommended (Cargo): ${REC_CARGO.name}`} mt={0} c={C.orange}/>
          <KV k="Payload" v="250g" vc={C.pink}/>
          <KV k="AUW" v={`${REC_CARGO.auw}g`} vc={C.yellow}/>
          <KV k="T/W" v={`${REC_CARGO.tw}:1`} vc={parseFloat(REC_CARGO.tw)>=2.0?C.green:C.red}/>
          <KV k="Hover endurance" v={`${REC_CARGO.hMin} min`} vc={C.yellow}/>
          <KV k="Cruise endurance" v={`${REC_CARGO.cMin} min`} vc={C.teal}/>
          <KV k="Max battery mass allowed" v={`${maxCargo}g (for T/W ≥ 2.0)`}/>
          <KV k="Endurance gain from lighter payload" v="~+2 min hover if payload <150g"/>
        </div>
        <div>
          <Note c={C.orange} ch="With 250g payload the T/W margin is tight at 2.01:1. In light wind ≤3 m/s this is comfortable. Above 5 m/s gusts, reduce payload or add a 64mm EDF upgrade note: 64mm provides only 1760g nacelle thrust — T/W with 250g cargo and any meaningful battery drops below 2.0, making 70mm mandatory for full cargo operations."/>
          <Good ch="Battery slide rail allows ±22mm CG trim. With 250g belly payload the CG shifts forward ~8mm — slide battery 10mm rearward to compensate. No structural change needed."/>
          <Warn ch="Winch motor (N20) draws up to 2.5A during load retract. This is drawn from the 5V BEC, not the main pack, but still budget 12.5W during winch ops. Do not winch while simultaneously applying full throttle."/>
        </div>
      </div>
    </>)}
    <SH t="64mm Alternate — Summary"/>
    <Note c={C.dim} ch={`64mm EDFs: 880g each, 1760g total. AUW_BASE_64 = ${BASE_64}g. For T/W ≥ 2.0 empty: max battery = ${Math.floor(880-BASE_64)}g (5S 3200mAh ≈ 310g). For 250g cargo: max battery = ${Math.floor(880-BASE_64-250)}g — only ~80–100g, which is a 5S 850mAh micro pack. 64mm is NOT suitable for 250g cargo missions. Use 64mm for empty survey/inspection work where sourcing simplicity outweighs endurance.`}/>
  </div>);
}

// ════════════════════════════════════════════════════════════════
//  TAB 3 — PROPULSION (70mm + 64mm + 40mm + variable nozzle)
// ════════════════════════════════════════════════════════════════
function VariableNozzleDiagram(){
  const VW=480, VH=320;
  const CX=240, CY=160, ID=SC(20), OD=SC(32); // 40mm ID → 32mm hull-scale
  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:520,display:"block"}}>
      {/* Engine bell outer */}
      <circle cx={CX} cy={CY} r={OD+SC(12)} fill="rgba(255,230,0,0.06)" stroke={C.yellow} strokeWidth={1.8}/>
      {/* Serenity bell ring */}
      <circle cx={CX} cy={CY} r={OD+SC(6)} fill="none" stroke={`${C.yellow}60`} strokeWidth={3} strokeDasharray="8 4"/>
      {/* Outer housing */}
      <circle cx={CX} cy={CY} r={OD+SC(2)} fill="rgba(0,229,255,0.06)" stroke={C.accent} strokeWidth={1.5}/>
      {/* Flaps (8 flaps) — OPEN position */}
      {[0,45,90,135,180,225,270,315].map(a=>{
        const rad=a*Math.PI/180;
        const x1=CX+OD*Math.cos(rad), y1=CY+OD*Math.sin(rad);
        const x2=CX+(OD+SC(10))*Math.cos(rad), y2=CY+(OD+SC(10))*Math.sin(rad);
        return(<g key={a}>
          <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={C.teal} strokeWidth={2.5} strokeLinecap="round"/>
          <circle cx={x1} cy={y1} r={2} fill={C.teal} opacity={0.8}/>
        </g>);
      })}
      {/* Inner rotating ring */}
      <circle cx={CX} cy={CY} r={OD} fill="rgba(45,212,191,0.08)" stroke={C.teal} strokeWidth={1.5}/>
      <circle cx={CX} cy={CY} r={ID} fill="rgba(45,212,191,0.12)" stroke={C.teal} strokeWidth={1}/>
      {/* EDF blades inside */}
      {[0,51,102,153,204,255,306].map(a=>(
        <line key={a} x1={CX} y1={CY}
          x2={CX+ID*0.9*Math.cos(a*Math.PI/180)} y2={CY+ID*0.9*Math.sin(a*Math.PI/180)}
          stroke={`${C.yellow}60`} strokeWidth={1.5} opacity={0.7}/>
      ))}
      {/* Servo arm */}
      <line x1={CX+OD} y1={CY} x2={CX+OD+SC(16)} y2={CY} stroke={C.orange} strokeWidth={2}/>
      <rect x={CX+OD+SC(12)} y={CY-SC(6)} width={SC(14)} height={SC(12)} rx={2} fill="rgba(255,107,53,0.15)" stroke={C.orange} strokeWidth={1}/>
      <text x={CX+OD+SC(19)} y={CY+2} textAnchor="middle" fill={C.orange} fontSize={8} fontFamily={M} fontWeight="bold">SG90</text>
      {/* CLOSED flaps overlay (dashed) */}
      {[22.5,67.5,112.5,157.5,202.5,247.5,292.5,337.5].map(a=>{
        const rad=a*Math.PI/180;
        const x1=CX+OD*Math.cos(rad), y1=CY+OD*Math.sin(rad);
        const x2=CX+(OD+SC(4))*Math.cos(rad), y2=CY+(OD+SC(4))*Math.sin(rad);
        return(<line key={a} x1={x1} y1={y1} x2={x2} y2={y2} stroke="rgba(45,212,191,0.3)" strokeWidth={2} strokeDasharray="3 2"/>);
      })}
      {/* Labels */}
      <text x={CX} y={CY-OD-SC(20)} textAnchor="middle" fill={C.yellow} fontSize={9} fontFamily={M} fontWeight="bold">SERENITY ENGINE BELL</text>
      <text x={CX} y={CY-OD-SC(10)} textAnchor="middle" fill={`${C.yellow}60`} fontSize={7} fontFamily={M}>40mm EDF + Variable-Area Nozzle</text>
      <text x={CX} y={CY+OD+SC(18)} textAnchor="middle" fill={C.teal} fontSize={8} fontFamily={M}>SOLID = open (hover) · DASHED = closed (cruise)</text>
      <text x={CX} y={CY+OD+SC(28)} textAnchor="middle" fill={`${C.teal}60`} fontSize={7} fontFamily={M}>Area ratio: open=115% · closed=82% of duct area</text>
      {/* Dimension arrows */}
      <line x1={CX-ID} y1={CY+OD+SC(45)} x2={CX+ID} y2={CY+OD+SC(45)} stroke={C.accent} strokeWidth={0.6} opacity={0.4}/>
      <text x={CX} y={CY+OD+SC(54)} textAnchor="middle" fill={C.dimmer} fontSize={7} fontFamily={M}>40mm EDF duct</text>
      <line x1={CX-OD-SC(2)} y1={CY+OD+SC(62)} x2={CX+OD+SC(2)} y2={CY+OD+SC(62)} stroke={C.accent} strokeWidth={0.6} opacity={0.4}/>
      <text x={CX} y={CY+OD+SC(72)} textAnchor="middle" fill={C.dimmer} fontSize={7} fontFamily={M}>~70mm outer housing (bell ID)</text>
      <text x={VW/2} y={14} textAnchor="middle" fill="rgba(0,229,255,0.25)" fontSize={9} fontFamily={M} letterSpacing="0.1em">VARIABLE-AREA NOZZLE — FRONT VIEW (aft looking fwd)</text>
    </svg>
  );
}

function PropulsionTab(){
  return(<div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="70mm Nacelle EDF ×2 (Primary)" mt={0} c={C.orange}/>
        <KV k="Duct ID" v="70mm" vc={C.orange}/>
        <KV k="Nacelle OD (fairing)" v="~80mm (was 72mm for 65mm unit)"/>
        <KV k="Blade count" v="12-blade"/>
        <KV k="Motor KV" v="2400–2600KV optimised for 5S"/>
        <KV k="Thrust @ 5S" v="~1100g each · 2200g total" vc={C.green}/>
        <KV k="Max current" v="35A each · 70A total"/>
        <KV k="ESC" v="40A BLHeli32 DSHOT300 (one step up from 35A)"/>
        <KV k="EDF+motor weight" v="72g each · 144g total"/>
        <KV k="Hover throttle" v={`~${Math.round(BASE_70/2/1100*100)}% per nacelle at ${REC_EMPTY.auw}g`} vc={C.green}/>
        <KV k="Sourcing" v="Changesun · Freewing · DYS · HobbyWing — all stock 70mm" vc={C.green}/>
        <KV k="Fairing change" v="+8mm radial vs 65mm — same pivot geometry"/>
        <SH t="64mm Nacelle EDF ×2 (Alternate)" c={C.dim}/>
        <KV k="Duct ID" v="64mm"/>
        <KV k="Nacelle OD" v="~74mm"/>
        <KV k="Thrust @ 5S" v="~880g each · 1760g total"/>
        <KV k="Max current" v="30A each · 60A total"/>
        <KV k="ESC" v="35A BLHeli32"/>
        <KV k="Weight" v="58g each · 116g total"/>
        <KV k="Sourcing" v="Extremely common · Arrows · Freewing · generic" vc={C.green}/>
        <KV k="Limitation" v="Cannot carry 250g payload with any useful battery" vc={C.red}/>
        <Note c={C.dim} ch="Use 64mm only for empty inspection/survey missions where part sourcing ease matters more than cargo capability or maximum endurance."/>
      </div>
      <div>
        <SH t="40mm Fuselage EDF + Variable Nozzle" mt={0} c={C.yellow}/>
        <KV k="Duct ID" v="40mm (was 35mm)" vc={C.yellow}/>
        <KV k="Engine bell ID" v="~70mm outer housing · 46mm duct exit (fixed)"/>
        <KV k="Blade count" v="11-blade"/>
        <KV k="Motor KV" v="4000–4500KV @ 5S"/>
        <KV k="Thrust @ 5S" v="~190g (fixed-area) / 160–220g (variable)" vc={C.green}/>
        <KV k="Max current" v="14A"/>
        <KV k="ESC" v="25A BLHeli32"/>
        <KV k="EDF+motor weight" v="30g"/>
        <KV k="Variable nozzle" v="BamJr thing:2991269 remix · PETG · 8-flap ring"/>
        <KV k="Nozzle servo" v="SG90 · Pico 2 GP15 PWM · 1.0ms=open, 2.0ms=closed"/>
        <KV k="Area ratio open" v="115% of duct area → exit dia 42mm (hover trim, max thrust)"/>
        <KV k="Area ratio closed" v="82% of duct area → exit dia 36mm (cruise, max jet speed)"/>
        <KV k="Thrust gain (open)" v="+8–12% vs fixed nozzle · ~208g max" vc={C.green}/>
        <KV k="Speed gain (closed)" v="+15–20% jet velocity → better propulsive efficiency ≥18m/s" vc={C.teal}/>
        <KV k="Hull scale" v="Hull length +5mm (365mm total) to seat 40mm bell properly"/>
        <div style={{marginTop:16}}>
          <div style={{color:C.dimmer,fontFamily:M,fontSize:10,letterSpacing:"0.08em",marginBottom:8}}>VARIABLE NOZZLE DIAGRAM (aft-looking-fwd)</div>
          <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:8}}>
            <VariableNozzleDiagram/>
          </div>
        </div>
      </div>
    </div>
    <SH t="Variable Nozzle Remix Specification"/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <KV k="Base design" v="BamJr thing:2991269 · Variable-area EDF nozzle"/>
        <KV k="License" v="Thingiverse · CC BY 4.0 (remixable with attribution)"/>
        <KV k="Original intent" v="Prototype variable-area nozzle for RC EDF aircraft"/>
        <KV k="Remix changes" v="Scale inner ring to 40mm ID · outer housing to Serenity bell profile"/>
        <KV k="Flap count" v="8 (matches original) · 10mm chord · 4mm pivot diameter"/>
        <KV k="Inner ring" v="Taller version (BamJr's extended threaded inner ring) for greater expansion"/>
        <KV k="Outer housing" v="Redesigned to integrate with Serenity bell geometry as a drop-in insert"/>
        <KV k="Material" v="CF-PETG for inner ring (structural) · PETG for outer flaps"/>
        <KV k="Print notes" v="Print inner ring vertically · outer flaps flat · 3 walls · 40% infill"/>
        <KV k="Servo mount" v="Added M2.5 boss on outer housing at 3 o'clock for SG90 bracket"/>
        <KV k="Linkage" v="1.5mm pushrod from SG90 horn to cam slot in inner ring · 18mm throw"/>
        <KV k="Actuation time" v="Full open→closed in ~0.35s (SG90 at 5V)"/>
      </div>
      <div>
        <KV k="Control law (Pico 2)" v="GP15 PWM · 50Hz update rate"/>
        <KV k="Hover mode (nacelles 90°)" v="Nozzle open (1.0ms · 115% area) · max thrust"/>
        <KV k="Transition (0–90° sweep)" v="Linear interpolation: nozzle closes as nacelles tilt"/>
        <KV k="Cruise (nacelles 0°)" v="Nozzle closed (2.0ms · 82% area) · max jet speed"/>
        <KV k="Throttle coupling" v="At low throttle ≤20%, nozzle opens 20% regardless of mode"/>
        <KV k="Calibration" v="Measure SWR with nozzle fully open, fully closed; adjust pushrod length"/>
        <Note c={C.teal} ch="The variable nozzle is not required for flight — a fixed nozzle at 100% area works fine. The variable nozzle adds ~15% more useful thrust range and meaningfully improves cruise Isp at speeds above 18 m/s. Consider building fixed first, then adding variable nozzle after initial flight testing."/>
        <Note c={C.yellow} ch="Attribution required: 'Variable-area nozzle based on BamJr / Thingiverse thing:2991269, CC BY 4.0. Remix: [your name], 2025.' Include this on your Printables/Thingiverse remix post."/>
      </div>
    </div>
    <SH t="Thrust Summary — All Configurations"/>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["CONFIG","NAC THRUST","FWD THRUST","TOTAL","AUW (rec)","T/W","HOVER THR","USE CASE"]}/>
        <tbody>{[
          ["70mm + 40mm (primary)","2200g","190g","2390g",`${REC_EMPTY.auw}g`,REC_EMPTY.tw,`~${Math.round(BASE_70/2/1100*100)}%`,"All missions"],
          ["70mm + 40mm + 250g cargo","2200g","190g","2390g",`${REC_CARGO.auw}g`,REC_CARGO.tw,`~${Math.round(REC_CARGO.auw/2/1100*100)}%`,"Cargo delivery"],
          ["64mm + 40mm (alternate)","1760g","190g","1950g","898g","1.96:1","~51%","Survey (empty only)"],
          ["70mm + 40mm variable open","2200g","~208g","2408g",`${REC_EMPTY.auw}g`,REC_EMPTY.tw,"~44%","Hover precision"],
          ["70mm + 40mm variable closed","2200g","~156g","2356g",`${REC_EMPTY.auw}g`,REC_EMPTY.tw,"—","Cruise 18+ m/s"],
        ].map((r,i)=>(
          <tr key={i} style={{background:i===0?"rgba(74,222,128,0.05)":i%2===0?"rgba(0,229,255,0.02)":"transparent"}}>
            {r.map((v,j)=>(<td key={j} style={{padding:"5px 9px",color:j===0?C.text:j===5?parseFloat(v)>=2.0?C.green:C.red:j===3?C.yellow:C.dim,fontWeight:j===5?"bold":"normal",whiteSpace:"nowrap"}}>{v}</td>))}
          </tr>
        ))}</tbody>
      </table>
    </div>
  </div>);
}

// ════════════════════════════════════════════════════════════════
//  TAB 4 — NAV LIGHTS (same as Rev C, preserved)
// ════════════════════════════════════════════════════════════════
function NavLightDiagram(){
  const VW=720,VH=360,CY=180;
  function arc(cx,cy,r,a1,a2,col){
    const s=a1*Math.PI/180,e=a2*Math.PI/180;
    const x1=cx+r*Math.cos(s),y1=cy+r*Math.sin(s),x2=cx+r*Math.cos(e),y2=cy+r*Math.sin(e);
    return<path d={`M${cx},${cy} L${x1},${y1} A${r},${r} 0 ${a2-a1>180?1:0},1 ${x2},${y2} Z`} fill={`${col}18`} stroke={col} strokeWidth={0.8} opacity={0.8}/>;
  }
  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {arc(xp(140),CY-SC(340),SC(52),-145,-35,"#ff2020")}
      {arc(xp(140),CY+SC(340),SC(52),35,145,"#00cc00")}
      {arc(xp(350),CY,SC(52),-70,70,"#ffffff")}
      <circle cx={xp(120)} cy={CY} r={SC(38)} fill="rgba(255,50,50,0.04)" stroke="#ff4444" strokeWidth={0.8} strokeDasharray="4 3" opacity={0.7}/>
      <circle cx={xp(160)} cy={CY} r={SC(33)} fill="rgba(255,255,255,0.02)" stroke="rgba(255,255,255,0.25)" strokeWidth={0.7} strokeDasharray="3 3"/>
      <path d={hullOutline(CY)} fill="rgba(0,229,255,0.05)" stroke={C.accent} strokeWidth={1.5}/>
      <Arms CY={CY} rx={SC(40)} ry={SC(16)}/>
      <ellipse cx={xp(44)} cy={CY} rx={SC(44)} ry={SC(24)} fill="rgba(0,229,255,0.06)" stroke={C.accent} strokeWidth={0.8}/>
      <circle cx={xp(140)} cy={CY-SC(340)} r={7} fill="#ff2020" opacity={0.95}/>
      <text x={xp(140)-22} y={CY-SC(340)-18} textAnchor="middle" fill="#ff2020" fontSize={8} fontFamily={M} fontWeight="bold">PORT ●</text>
      <circle cx={xp(140)} cy={CY+SC(340)} r={7} fill="#00cc00" opacity={0.95}/>
      <text x={xp(140)+22} y={CY+SC(340)+20} textAnchor="middle" fill="#00cc00" fontSize={8} fontFamily={M} fontWeight="bold">STBD ●</text>
      <circle cx={xp(350)} cy={CY} r={7} fill="#eeeeee" opacity={0.95}/>
      <text x={xp(350)+20} y={CY-2} fill="#cccccc" fontSize={7} fontFamily={M}>TAIL ●</text>
      <circle cx={xp(120)} cy={CY} r={7} fill="#ff4444" opacity={0.95}/>
      <text x={xp(120)} y={CY-16} textAnchor="middle" fill="#ff4444" fontSize={7} fontFamily={M} fontWeight="bold">ACOL◆</text>
      <circle cx={xp(160)} cy={CY} r={5} fill="rgba(255,255,200,0.8)" stroke="#ffffaa" strokeWidth={0.8}/>
      <text x={xp(160)} y={CY+16} textAnchor="middle" fill="#ffffaa" fontSize={7} fontFamily={M}>BELLY◆</text>
      <rect x={xp(22)} y={CY-SC(8)} width={SC(16)} height={SC(16)} rx={2} fill="rgba(255,255,120,0.2)" stroke="#ffff80" strokeWidth={1}/>
      <text x={xp(30)} y={CY-SC(14)} textAnchor="middle" fill="#ffff80" fontSize={7} fontFamily={M}>LAND</text>
      {[["#ff2020","Port red (steady)"],["#00cc00","Stbd green (steady)"],["#cccccc","Tail white (steady)"],["#ff4444","Anti-col dorsal (60FPM)"],["#ffffaa","Belly strobe"],["#ffff80","Landing light"]].map(([col,lbl],i)=>(
        <g key={i}><circle cx={14} cy={240+i*18} r={5} fill={col} opacity={0.9}/><text x={24} y={244+i*18} fill={col} fontSize={8} fontFamily={M}>{lbl}</text></g>
      ))}
      <text x={VW/2} y={16} textAnchor="middle" fill="rgba(0,229,255,0.25)" fontSize={9} fontFamily={M} letterSpacing="0.12em">NAVIGATION LIGHTS — TOP VIEW</text>
      <text x={NX-8} y={CY+4} textAnchor="end" fill={C.dimmer} fontSize={7} fontFamily={M}>NOSE</text>
      <text x={xp(365)+6} y={CY+4} fill={C.dimmer} fontSize={7} fontFamily={M}>TAIL</text>
    </svg>
  );
}
function NavLightsTab(){
  const lights=[
    {id:"PORT",col:"#ff2020",name:"Red",   pos:"Left nacelle leading tip",    arc:"≥110°",flash:"Steady",   lum:"≥300cd",reg:"ICAO Ann.2 · 14CFR91.209"},
    {id:"STBD",col:"#00cc00",name:"Green", pos:"Right nacelle leading tip",   arc:"≥110°",flash:"Steady",   lum:"≥300cd",reg:"ICAO Ann.2 · 14CFR91.209"},
    {id:"TAIL",col:"#dddddd",name:"White", pos:"Aft hull, 350mm from nose",   arc:"≥140°",flash:"Steady",   lum:"≥300cd",reg:"ICAO Ann.2 · 14CFR91.209"},
    {id:"ACOL",col:"#ff4444",name:"Red",   pos:"Dorsal hull, 120mm from nose",arc:"360°",flash:"60 FPM",    lum:"≥150cd avg",reg:"14CFR91.209 · AC107-2B"},
    {id:"BELY",col:"#ffffaa",name:"White", pos:"Belly hull, 160mm from nose", arc:"lower",flash:"60 FPM",   lum:"≥100cd avg",reg:"FAA AC91-74"},
    {id:"LAND",col:"#ffff80",name:"White", pos:"Nose underside, 30mm",        arc:"fwd",  flash:"Steady(ops)",lum:"≥600cd",reg:"FAA AC20-74"},
  ];
  return(<div>
    <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:8,marginBottom:18}}><NavLightDiagram/></div>
    <div style={{overflowX:"auto",marginBottom:16}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["LIGHT","COLOR","POSITION","ARC","FLASH","LUMENS","REGULATION"]}/>
        <tbody>{lights.map((l,i)=>(<tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.02)":"transparent"}}>
          <td style={{padding:"5px 9px",color:l.col,fontWeight:"bold"}}>{l.id}</td>
          <td style={{padding:"5px 9px"}}><span style={{background:l.col,color:"#000",padding:"1px 6px",borderRadius:2,fontSize:9}}>{l.name}</span></td>
          <td style={{padding:"5px 9px",color:C.text}}>{l.pos}</td>
          <td style={{padding:"5px 9px",color:C.dim}}>{l.arc}</td>
          <td style={{padding:"5px 9px",color:l.flash.includes("FPM")?C.orange:C.green}}>{l.flash}</td>
          <td style={{padding:"5px 9px",color:C.yellow}}>{l.lum}</td>
          <td style={{padding:"5px 9px",color:C.dimmer,fontSize:9}}>{l.reg}</td>
        </tr>))}</tbody>
      </table>
    </div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="LED Controller" mt={0}/>
        <KV k="LED type" v="WS2812C-2020 · 5V · 2×2mm · 6 total"/>
        <KV k="Pico pin" v="GP26 → PIO0 · 800kHz NZR · single data line"/>
        <KV k="Power" v="5V BEC · ≤180mA · 0.9W · negligible budget"/>
        <KV k="Strobe" v="60 FPM · 50ms ON / 950ms OFF · ICAO compliant"/>
      </div>
      <div>
        <SH t="70mm Nacelle Tip Mounts" mt={0}/>
        <KV k="LED pocket" v="2×2mm recess in 80mm OD clear PETG nacelle tip cap"/>
        <KV k="Coverage" v="Rotates with nacelle · ACOL+belly covers horizontal plane gap"/>
        <KV k="Wiring" v="28AWG 3-core from port tip → stbd tip → tail → dorsal → belly"/>
      </div>
    </div>
  </div>);
}

// ════════════════════════════════════════════════════════════════
//  TAB 5 — ANTENNA (Serenity 365mm hull, same positions)
// ════════════════════════════════════════════════════════════════
function AntennaTab(){
  const VW=720,VH=300,CY=150;
  return(<div>
    <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:8,marginBottom:18}}>
      <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
        <path d={hullOutline(CY)} fill="rgba(0,229,255,0.05)" stroke={C.accent} strokeWidth={1.5}/>
        <Arms CY={CY} rx={SC(40)} ry={SC(16)}/>
        <ellipse cx={xp(44)} cy={CY} rx={SC(44)} ry={SC(22)} fill="rgba(0,229,255,0.06)" stroke={C.accent} strokeWidth={0.8}/>
        <rect x={xp(46)} y={CY-SC(44)} width={SC(24)} height={SC(10)} rx={2} fill="rgba(74,222,128,0.25)" stroke="#4ade80" strokeWidth={1.5}/>
        <text x={xp(58)} y={CY-SC(50)} textAnchor="middle" fill="#4ade80" fontSize={8} fontFamily={M} fontWeight="bold">GPS 58mm</text>
        <circle cx={xp(290)} cy={CY-SC(28)} r={5} fill="rgba(244,114,182,0.25)" stroke={C.pink} strokeWidth={1.5}/>
        <line x1={xp(290)} y1={CY-SC(33)} x2={xp(290)} y2={CY-SC(78)} stroke={C.pink} strokeWidth={2} strokeLinecap="round"/>
        {[0,1,2,3].map(i=>(<ellipse key={i} cx={xp(290)} cy={CY-SC(41+i*8)} rx={4} ry={3} fill="none" stroke={C.pink} strokeWidth={0.9} opacity={0.75}/>))}
        <text x={xp(290)+16} y={CY-SC(76)} fill={C.pink} fontSize={7} fontFamily={M} fontWeight="bold">49MHz 290mm</text>
        <line x1={xp(150)} y1={CY} x2={xp(310)} y2={CY} stroke="rgba(0,229,255,0.18)" strokeWidth={1} strokeDasharray="6 3"/>
        <text x={xp(230)} y={CY-6} textAnchor="middle" fill="rgba(0,229,255,0.3)" fontSize={6} fontFamily={M}>dorsal keel spine</text>
        <circle cx={xp(238)} cy={CY} r={5} fill="rgba(255,107,53,0.2)" stroke={C.orange} strokeWidth={1.3} strokeDasharray="3 2"/>
        <text x={xp(238)} y={CY+18} textAnchor="middle" fill={C.orange} fontSize={8} fontFamily={M} fontWeight="bold">SiK↓ 238mm</text>
        <rect x={xp(195)} y={CY-SC(18)} width={SC(38)} height={SC(36)} rx={3} fill="rgba(192,132,252,0.06)" stroke={C.purple} strokeWidth={0.8} strokeDasharray="4 2"/>
        <text x={xp(214)} y={CY+2} textAnchor="middle" fill={C.purple} fontSize={7} fontFamily={M}>WiFi 210mm</text>
        <line x1={NX} y1={CY} x2={NX-22} y2={CY} stroke={C.teal} strokeWidth={2.5} strokeLinecap="round"/>
        <g opacity={0.28}>
          <line x1={xp(58)} y1={CY+SC(56)} x2={xp(290)} y2={CY+SC(56)} stroke={C.yellow} strokeWidth={0.6}/>
          <text x={(xp(58)+xp(290))/2} y={CY+SC(68)} textAnchor="middle" fill={C.yellow} fontSize={6} fontFamily={M}>232mm (GPS↔49MHz) ✔</text>
        </g>
        <text x={VW/2} y={14} textAnchor="middle" fill="rgba(0,229,255,0.25)" fontSize={9} fontFamily={M} letterSpacing="0.12em">ANTENNA LAYOUT — SERENITY 365mm HULL</text>
        <text x={NX-8} y={CY+4} textAnchor="end" fill={C.dimmer} fontSize={7} fontFamily={M}>NOSE</text>
        <text x={xp(365)+6} y={CY+4} fill={C.dimmer} fontSize={7} fontFamily={M}>TAIL</text>
      </svg>
    </div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="GPS · 58mm · cockpit roof" mt={0} c="#4ade80"/>
        <KV k="Type" v="25×25mm RHCP ceramic patch · 12mm standoff"/>
        <KV k="Mount" v="Cockpit dome top recess · clear PETG lens"/>
        <KV k="Cable" v="U.FL → RG-178 ≤100mm → TRIHAT-1"/>
        <KV k="Keepout" v="≥40mm CF · ≥150mm from 49MHz coil"/>
        <SH t="SiK 915MHz · 238mm · belly" c={C.orange}/>
        <KV k="Type" v="λ/4 monopole 82mm · SMA-RP bulkhead"/>
        <KV k="Mount" v="6.5mm PETG belly hole at 238mm — clear zone 200–255mm"/>
        <KV k="Cable" v="IPEX pigtail → COMMS-HAT-1 SiK U.FL"/>
      </div>
      <div>
        <SH t="49MHz RCRS · 290mm · dorsal" mt={0} c={C.pink}/>
        <KV k="Type" v="250mm whip + 38μH base coil · counterpoise 4× radials"/>
        <KV k="Mount" v="Serenity aft dorsal spine · integrated PETG antenna fin"/>
        <KV k="SWR target" v="≤2.5:1 across 49.83–49.89 MHz"/>
        <KV k="Cable" v="RG-316 120mm → COMMS-HAT-1 U.FL"/>
        <SH t="WiFi · 210mm · internal" c={C.purple}/>
        <KV k="Type" v="CM4 on-board PCB trace antenna · no install steps"/>
        <KV k="Mount" v="Internal to hull · PETG RF-transparent at 210mm"/>
      </div>
    </div>
  </div>);
}

// ════════════════════════════════════════════════════════════════
//  TAB 6 — WIRING (unchanged from Rev C)
// ════════════════════════════════════════════════════════════════
function WiringTab(){
  return(<div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="Ethernet · TRIHAT-1 J3 ↔ COMMS-HAT-1 J2" mt={0} c={C.purple}/>
        <KV k="Connector" v="JST-GH 1.25mm 6-pin (both ends)"/>
        <KV k="Cable" v="Matched twisted-pair 100BASE-T · 150mm"/>
        <KV k="Pin 1" v="GND"/><KV k="Pin 2" v="TX+"/><KV k="Pin 3" v="TX−"/>
        <KV k="Pin 4" v="RX+"/><KV k="Pin 5" v="RX−"/><KV k="Pin 6" v="N/C"/>
        <KV k="Speed" v="100Mbps · auto-MDIX (W5500 hw) · no crossover"/>
        <KV k="MAVLink" v="UDP 14550 · Pico→CM4 attitude/status at 10Hz"/>
        <KV k="Log stream" v="UDP 14551 · Pico→CM4 sensor CSV 50Hz"/>
        <KV k="Config" v="TCP 8080 · CM4→Pico parameter set"/>
        <KV k="IP" v="Pico 192.168.10.1 · CM4 192.168.10.2 (static)"/>
        <KV k="Route" v="Port keel spine · cable-tie 40mm intervals"/>
        <Note c={C.purple} ch="HX1188NL magnetics on both boards — no external transformer. Auto-MDIX handles straight or crossover cable."/>
      </div>
      <div>
        <SH t="CAN FD · TRIHAT-1 J2 ↔ COMMS-HAT-1 J1" mt={0} c={C.orange}/>
        <KV k="Connector" v="JST-GH 1.25mm 4-pin (both ends)"/>
        <KV k="Cable" v="Twisted CANH/CANL + power · 120mm"/>
        <KV k="Pin 1" v="GND"/><KV k="Pin 2" v="+5V bus power"/>
        <KV k="Pin 3" v="CANH"/><KV k="Pin 4" v="CANL"/>
        <KV k="Standard" v="ISO 11898-1:2015 CAN FD"/>
        <KV k="Rate" v="1Mbps nominal / 4Mbps FD data phase"/>
        <KV k="Termination" v="120Ω at TRIHAT-1 only (bridge soldered) · COMMS-HAT-1 open"/>
        <KV k="Pico→CM4" v="AHRS · RPM · sensor health · arm events · nozzle state"/>
        <KV k="CM4→Pico" v="Mission commands · mode · parameter updates"/>
        <KV k="Route" v="Starboard keel spine · ≥20mm from Ethernet cable"/>
        <Warn ch="TRIHAT-1 120Ω bridge MUST be soldered. COMMS-HAT-1 bridge must NOT be soldered. Twist CANH/CANL ≥25 turns/metre."/>
      </div>
    </div>
    <SH t="New Rev D Signal Lines"/>
    <KV k="Variable nozzle servo" v="Pico 2 GP15 → PWM 50Hz → SG90 in engine bell housing"/>
    <KV k="Nozzle servo cable route" v="28AWG 3-core · along keel spine aft · 280mm total"/>
    <KV k="Nozzle cable connector" v="JST-PH 2.0mm 3-pin (servo standard) at SG90 end"/>
    <KV k="LED chain (70mm tips)" v="28AWG 3-core · port tip→stbd tip→tail→dorsal→belly · ~950mm total"/>
  </div>);
}

// ════════════════════════════════════════════════════════════════
//  TAB 7 — BOM
// ════════════════════════════════════════════════════════════════
const BOM=[
  {cat:"Propulsion",qty:2, ref:"EDF-70", part:"70mm EDF + 2500KV BLDC (primary)",      desc:"12-blade · 1100g thrust @ 5S · 35A max",   est:"$26ea"},
  {cat:"Propulsion",qty:2, ref:"EDF-64", part:"64mm EDF + 2800KV (alternate, pick one)",desc:"12-blade · 880g thrust @ 5S · 30A max",    est:"$20ea"},
  {cat:"Propulsion",qty:2, ref:"ESC-40", part:"40A BLHeli32 ESC (for 70mm)",            desc:"DSHOT300 · 2–6S · needed for 35A EDF",     est:"$20ea"},
  {cat:"Propulsion",qty:2, ref:"ESC-35", part:"35A BLHeli32 ESC (for 64mm alt)",        desc:"DSHOT300 · 2–6S",                          est:"$18ea"},
  {cat:"Propulsion",qty:1, ref:"EDF-40", part:"40mm EDF + 4200KV BLDC",                 desc:"11-blade · 190g thrust @ 5S · 14A max",    est:"$16"},
  {cat:"Propulsion",qty:1, ref:"ESC-25", part:"25A BLHeli32 ESC (fwd fan)",             desc:"DSHOT300 · 2–6S",                          est:"$12"},
  {cat:"Propulsion",qty:2, ref:"SRV-T",  part:"MG90S digital servo (nacelle tilt)",     desc:"Metal gear · 1.8kg·cm · 180°",             est:"$4ea"},
  {cat:"Propulsion",qty:1, ref:"SRV-N",  part:"SG90 micro servo (variable nozzle)",     desc:"1.8kg·cm · 1.0ms=open · 2.0ms=closed",    est:"$3"},
  {cat:"Propulsion",qty:1, ref:"NOZZLE", part:"Variable nozzle (BamJr remix, 40mm ID)", desc:"CC BY 4.0 remix · CF-PETG inner · PETG flaps · SG90 bracket",est:"$3 filament"},
  {cat:"Flt Ctrl",  qty:1, ref:"PICO2",  part:"Raspberry Pi Pico 2",                    desc:"RP2350 · 264KB · 4MB flash",               est:"$5"},
  {cat:"Flt Ctrl",  qty:1, ref:"TH1",    part:"TRIHAT-1 (custom 4-layer PCB)",          desc:"65×48mm · IMU+Baro+GPS+CAN+ETH+TPM+FPV",  est:"$75"},
  {cat:"Flt Ctrl",  qty:1, ref:"AIRS",   part:"MS4525DO airspeed sensor",               desc:"I²C · ±1PSI · 0–80m/s",                   est:"$10"},
  {cat:"Flt Ctrl",  qty:1, ref:"PITOT",  part:"CF pitot 3mm + 2mm silicone tubing",     desc:"80mm tube · 2×80mm leads",                est:"$4"},
  {cat:"Companion", qty:1, ref:"CM4",    part:"CM4 Lite 4GB WiFi",                      desc:"BCM2711 · 4×A72 · 4GB LPDDR4X · 802.11ac",est:"$55"},
  {cat:"Companion", qty:1, ref:"CAR1",   part:"CM4-CARRIER-1 (custom PCB)",             desc:"65×40mm · DF40 sockets · μSD OS · WiFi ant",est:"$22"},
  {cat:"Companion", qty:1, ref:"CH1",    part:"COMMS-HAT-1 (custom PCB)",                 desc:"65×48mm · CAN+ETH+TPM+μSD+SiK+RCRS",      est:"$60"},
  {cat:"Companion", qty:1, ref:"SIK",    part:"SiK 915MHz air unit",                    desc:"MAVLink 2.0 · 100mW · UART",               est:"$18"},
  {cat:"Companion", qty:1, ref:"RCRS",   part:"49MHz RCRS transceiver module",          desc:"TDDS · 6-ch · 10mW EIRP",                  est:"$16"},
  {cat:"Nav Lights",qty:6, ref:"WS2812", part:"WS2812C-2020 RGB LED",                   desc:"5V · 2×2mm · addressable · PIO driven",    est:"$0.50ea"},
  {cat:"Nav Lights",qty:6, ref:"LENS",   part:"Clear PETG LED lens diffusers",          desc:"Flush mount · nacelle tips + hull",         est:"<$1 filament"},
  {cat:"Payload",   qty:1, ref:"SRV-R",  part:"SG90 micro servo (release latch)",       desc:"Spring-return closed on power loss",        est:"$3"},
  {cat:"Payload",   qty:1, ref:"WINCH",  part:"N20 6V 100:1 gearmotor",                 desc:"Winch drive",                              est:"$5"},
  {cat:"Payload",   qty:1, ref:"DRV",    part:"DRV8833 H-bridge module",                desc:"Dual 1.5A · current sense on ADC",         est:"$3"},
  {cat:"Payload",   qty:1, ref:"SPOOL",  part:"18mm phenolic spool + 5m Dyneema SK75",  desc:"0.8mm dia · 40kg break strength",          est:"$6"},
  // Battery — show both options
  {cat:"Power",     qty:1, ref:"BAT-E",  part:"★ 5S 4500mAh 35C (empty endurance)",     desc:"GNB/CNHL · 420g · T/W 2.20 · 9.4min hover",est:"$45"},
  {cat:"Power",     qty:1, ref:"BAT-C",  part:"★ 5S 2800mAh 45C (cargo 250g)",         desc:"Tattu/GNB · 271g · T/W 2.01 · 6.2min hover",est:"$38"},
  {cat:"Power",     qty:1, ref:"BEC",    part:"5V 3A switching BEC",                    desc:"Powers CM4+Pico+servos+radios+LEDs",       est:"$5"},
  {cat:"Power",     qty:1, ref:"PDIST",  part:"XT60 power distribution board",          desc:"4× XT30 out · 12AWG mains",               est:"$8"},
  {cat:"Airframe",  qty:1, ref:"HULL",   part:"Serenity hull PETG prints — 365mm",      desc:"11 sections · ~148g · 8% gyroid thin-wall",est:"$19 filament"},
  {cat:"Airframe",  qty:2, ref:"NAC",    part:"70mm nacelle pods CF-PETG · 80mm OD",    desc:"Pivot seat · bearing pocket · LED recess", est:"$7 filament"},
  {cat:"Airframe",  qty:1, ref:"BELL",   part:"Serenity engine bell 365mm PETG",        desc:"70mm ID · nozzle housing · 3 walls",       est:"$5 filament"},
  {cat:"Airframe",  qty:1, ref:"KEEL",   part:"CF keel 6×3mm × 385mm",                 desc:"Dorsal structural spine · scaled +5mm",    est:"$6"},
  {cat:"Airframe",  qty:2, ref:"SPAR",   part:"CF tube 12mm OD × 300mm",               desc:"Outrigger wing spars",                     est:"$8ea"},
  {cat:"Airframe",  qty:4, ref:"SKID",   part:"TPU 95A skid feet",                     desc:"Crash-absorbing landing pads",             est:"$2 filament"},
  {cat:"Airframe",  qty:1, ref:"HW",     part:"M2/M2.5/M3 hardware assortment",        desc:"Standoffs · screws · heat-set inserts",    est:"$8"},
  {cat:"Wiring",    qty:1, ref:"JSTKIT", part:"JST-GH 1.25mm connector kit",           desc:"4+6pin · crimp tool · pre-made cables",    est:"$14"},
  {cat:"Wiring",    qty:1, ref:"ETH-C",  part:"6-pin JST-GH Ethernet cable 150mm",     desc:"Twisted pairs · TRIHAT↔COMMS-HAT",           est:"$4"},
  {cat:"Wiring",    qty:1, ref:"CAN-C",  part:"4-pin JST-GH CAN FD cable 120mm",       desc:"Twisted CANH/CANL · TRIHAT↔COMMS-HAT",       est:"$3"},
  {cat:"Wiring",    qty:1, ref:"WIRE",   part:"Silicone wire assortment",              desc:"12AWG power · 22AWG signal · 28AWG data",  est:"$12"},
  {cat:"Wiring",    qty:1, ref:"XT60P",  part:"XT60 connector pair",                   desc:"Battery to power board",                   est:"$2"},
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
        {cf==="All"&&(<tfoot><tr style={{borderTop:`1px solid ${C.border}`}}><td colSpan={5} style={{padding:"8px 8px",color:C.accent,textAlign:"right",fontSize:11}}>TOTAL ESTIMATED (one battery choice)</td><td style={{padding:"8px 8px",color:C.yellow,fontSize:16,fontWeight:"bold"}}>$600–700</td></tr></tfoot>)}
      </table>
    </div>
    <Note c={C.dim} ch="Pick ONE of BAT-E (empty endurance) or BAT-C (cargo) — not both for the same aircraft unless you intend to swap packs. EDF columns list both 70mm and 64mm — purchase only one. Custom PCBs at 5-piece JLCPCB + LCSC. Filament cost at $25–35/kg."/>
  </div>);
}

// ════════════════════════════════════════════════════════════════
//  TAB 8 — SBOM
// ════════════════════════════════════════════════════════════════
const SBOM=[
  {sys:"Pico 2",layer:"Core",      comp:"Pico SDK 2.x",            ver:"≥2.0",  lic:"BSD-3",  role:"RP2350 HAL · PIO · DMA · multicore"},
  {sys:"Pico 2",layer:"AHRS",      comp:"Mahony AHRS (port)",      ver:"custom",lic:"Apache-2",role:"Complementary filter gyro+accel → quaternion attitude"},
  {sys:"Pico 2",layer:"Control",   comp:"Custom PID cascade",      ver:"v1.0",  lic:"Propr.", role:"Rate/attitude/position PID · 500Hz main loop"},
  {sys:"Pico 2",layer:"Protocol",  comp:"MAVLink 2.0 C lib",       ver:"2.0",   lic:"MIT",    role:"MAVLink encode/decode over UART1 + W5500 UDP"},
  {sys:"Pico 2",layer:"Driver",    comp:"ICM-42688-P SPI driver",  ver:"custom",lic:"BSD-3",  role:"6-DOF IMU · SPI0 24MHz"},
  {sys:"Pico 2",layer:"Driver",    comp:"BMP388 I²C driver",       ver:"custom",lic:"BSD-3",  role:"Barometer · I²C1"},
  {sys:"Pico 2",layer:"Driver",    comp:"MS4525DO airspeed",       ver:"custom",lic:"BSD-3",  role:"Differential pressure → IAS · I²C1"},
  {sys:"Pico 2",layer:"Driver",    comp:"u-blox UBX parser",       ver:"custom",lic:"BSD-3",  role:"GPS binary protocol · UART0"},
  {sys:"Pico 2",layer:"Driver",    comp:"MCP2518FD SPI driver",    ver:"custom",lic:"BSD-3",  role:"CAN FD controller · SPI0"},
  {sys:"Pico 2",layer:"Driver",    comp:"W5500 ioLibrary",         ver:"3.x",   lic:"BSD-3",  role:"Ethernet TCP/IP offload · SPI1"},
  {sys:"Pico 2",layer:"Driver",    comp:"SLB9670 TPM2 driver",     ver:"custom",lic:"BSD-3",  role:"SPI-TPM 2.0 · firmware attestation"},
  {sys:"Pico 2",layer:"Driver",    comp:"WS2812 PIO driver",       ver:"SDK",   lic:"BSD-3",  role:"Nav light RGB chain · GP26 PIO0"},
  {sys:"Pico 2",layer:"Driver",    comp:"DSHOT300 PIO driver",     ver:"custom",lic:"MIT",    role:"Bidirectional DSHOT · 3× ESC + nozzle servo PWM"},
  {sys:"Pico 2",layer:"Algorithm", comp:"TDDS channel selector",   ver:"v1.0",  lic:"Propr.", role:"49MHz RCRS TDDS · SNR scan → clearest channel"},
  {sys:"Pico 2",layer:"Algorithm", comp:"Variable nozzle controller",ver:"v1.0",lic:"Propr.", role:"Area ratio schedule · transition interpolation · GP15 PWM"},
  {sys:"CM4",   layer:"OS",        comp:"RPi OS Lite 64-bit",      ver:"bookworm",lic:"Mixed GPL","role":"Debian Linux headless · kernel 6.6+"},
  {sys:"CM4",   layer:"Middleware",comp:"mavlink-router",          ver:"≥3.0",  lic:"Apache-2",role:"MAVLink router: Pico↔SiK↔GCS↔MAVSDK"},
  {sys:"CM4",   layer:"Middleware",comp:"MAVSDK-Python",           ver:"≥2.0",  lic:"BSD-3",  role:"High-level drone API: missions · params · telemetry"},
  {sys:"CM4",   layer:"Middleware",comp:"python-can",              ver:"≥4.0",  lic:"LGPL-3", role:"CAN bus → MCP2518FD socketcan interface"},
  {sys:"CM4",   layer:"Middleware",comp:"dronecan (Python)",       ver:"≥1.0",  lic:"MIT",    role:"DroneCAN/UAVCANv1 protocol stack"},
  {sys:"CM4",   layer:"Middleware",comp:"pymavlink",               ver:"≥2.4",  lic:"LGPL",   role:"MAVLink serialisation + black-box logging"},
  {sys:"CM4",   layer:"Security",  comp:"tpm2-tools + tpm2-tss",  ver:"≥5.0/4.0",lic:"BSD-2",role:"TPM 2.0 key provisioning · firmware attestation"},
  {sys:"CM4",   layer:"Logging",   comp:"Custom flight logger",    ver:"v1.0",  lic:"Propr.", role:"MAVLink+sensor+nozzle → binary log on COMMS-HAT μSD"},
  {sys:"CM4",   layer:"Driver",    comp:"spi-bcm2835 kernel",      ver:"kernel",lic:"GPL-2",  role:"SPI for MCP2518FD · W5500 · TPM on CM4 GPIO"},
  {sys:"CM4",   layer:"Comms",     comp:"SiK firmware (air unit)", ver:"2.x",   lic:"GPL-3",  role:"915MHz MAVLink radio firmware"},
  {sys:"GCS",   layer:"App",       comp:"QGroundControl",          ver:"≥4.3",  lic:"GPL-3",  role:"Flight planning · telemetry · params"},
  {sys:"GCS",   layer:"App",       comp:"Mission Planner (alt)",   ver:"≥1.3",  lic:"GPL-3",  role:"Windows/Linux GCS alternative"},
];
const SBOM_SYS=[...new Set(SBOM.map(s=>s.sys))];
const LAYER_COL={Core:C.accent,AHRS:C.teal,Control:C.orange,Protocol:C.orange,Driver:C.teal,Algorithm:C.pink,OS:C.green,Middleware:C.purple,Security:C.yellow,Logging:C.lime,Comms:C.accent,App:C.green,Library:C.purple};

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
          <td style={{padding:"5px 8px",color:s.sys==="Pico 2"?C.accent:s.sys==="CM4"?C.green:C.orange,fontWeight:"bold",whiteSpace:"nowrap",fontSize:9}}>{s.sys}</td>
          <td style={{padding:"5px 8px"}}><span style={{color:LAYER_COL[s.layer]||C.dim,border:`1px solid ${LAYER_COL[s.layer]||C.dim}40`,padding:"1px 5px",borderRadius:2,fontSize:8,whiteSpace:"nowrap"}}>{s.layer}</span></td>
          <td style={{padding:"5px 8px",color:C.text,whiteSpace:"nowrap"}}>{s.comp}</td>
          <td style={{padding:"5px 8px",color:C.dimmer,whiteSpace:"nowrap",fontSize:9}}>{s.ver}</td>
          <td style={{padding:"5px 8px",color:C.yellow,whiteSpace:"nowrap",fontSize:9}}>{s.lic}</td>
          <td style={{padding:"5px 8px",color:C.dim,fontSize:9,lineHeight:1.5}}>{s.role}</td>
        </tr>))}</tbody>
      </table>
    </div>
    <Note c={C.accent} ch="Variable nozzle controller added as new Pico 2 algorithm module. GPL-3 (QGC, SiK) must remain open-source if redistributed. Proprietary Pico 2 firmware uses BSD/MIT only. BamJr nozzle remix: CC BY 4.0 — attribution required."/>
  </div>);
}

// ════════════════════════════════════════════════════════════════
//  TAB 9 — BUILD GUIDE
// ════════════════════════════════════════════════════════════════
const BUILD_PHASES=[
  {
    phase:"PHASE 1 · PRINT PREP",c:C.teal,
    steps:[
      {t:"Source filament",d:"PETG (hull, bell, nacelle fairings, skids carrier): min 300g. CF-PETG (nacelle pods, tilt brackets, nozzle inner ring): min 80g. TPU 95A (skid feet): 40g. Dry all filament 6h at 65°C before printing structural parts."},
      {t:"Printer prep",d:"Install hardened steel nozzle (0.4mm) — mandatory for CF-PETG. Calibrate E-steps and PA (Pressure Advance) for each filament. Bed: PEI spring steel sheet. Level after nozzle change."},
      {t:"Slice hull sections",d:"Split hull at four planes: nose cap (0–22mm), cockpit (22–90mm), mid-hull left+right halves (90–230mm split down centreline), aft-hull (230–270mm), engine bell (270–365mm). Print each flat on bed. 8% gyroid infill, 2 perimeters, 0.20mm layer height for all hull sections. Enable seam alignment to dorsal for clean exterior seam."},
      {t:"Print sequence",d:"Print TPU skid feet first (separate job, purge before PETG). Then PETG hull sections (longest jobs, run overnight). Then CF-PETG nacelle pods and tilt brackets last (shorter but critical — zero tolerance on bearing seats). Finally, variable nozzle inner ring (CF-PETG, print vertically) and flap ring (PETG)."},
      {t:"Post-print",d:"Remove supports. Dry-fit all sections before bonding. Nacelle bearing seats: test-fit 8mm OD × 5mm ID × 2.5mm bearing with slight interference (use a M5 bolt and nut to press it). Lightly sand all mating surfaces with 220-grit. Clean with IPA."},
    ]
  },
  {
    phase:"PHASE 2 · CF SKELETON",c:C.accent,
    steps:[
      {t:"Cut CF keel spine",d:"6×3mm flat CF bar · 385mm length (hull 365mm + 20mm aft overhang for engine bell mount). Mark datum lines at 90mm, 130mm, 160mm, 200mm, 290mm, 365mm from nose. Deburr ends with 180-grit on a block."},
      {t:"Cut outrigger spars",d:"12mm OD CF tube · 2 pieces × 300mm. Sand one end of each to 8mm dia × 25mm to create a reduced tenon that inserts into the hull spar pocket at 130–155mm."},
      {t:"Drill keel attachment holes",d:"3mm pilot holes through keel at 95mm, 165mm, 235mm, 295mm, 360mm for M3 standoffs that hold hull sections. Use drill press for perpendicularity. Countersink to accept M3 flat-head screws."},
      {t:"Epoxy mid-hull to keel",d:"Apply 24h West System 105/206 epoxy to keel at hull attachment points. Slide keel through all hull sections. Clamp and cure 12h. Do NOT bond cockpit cap or aft bell yet — they need to be removable for electronics access."},
      {t:"Install spar-to-keel bracket",d:"At 130mm, epoxy the 3D-printed CF-PETG spar junction bracket to the keel. The outrigger spars press-fit into this bracket. Check 90° alignment from hull centreline with a set square. Tape and cure 12h."},
      {t:"Install outrigger spars",d:"Press-fit spar tenons into bracket. Apply Loctite 638 retaining compound at junction. Check span is symmetric (measure tip-to-tip). Cure 4h before attaching any loads. The spars should flex slightly — this is correct for crash absorption."},
    ]
  },
  {
    phase:"PHASE 3 · NACELLE ASSEMBLY",c:C.orange,
    steps:[
      {t:"Press bearings",d:"Press one 8×5×2.5mm ball bearing into each nacelle pod pivot socket using a bearing press jig (3D-print a simple cup jig). The bearing must be flush or ±0.2mm. Press the second bearing into the CF-PETG tilt bracket."},
      {t:"Thread CF pivot rod",d:"8mm CF rod · 52mm long · through spar arm → tilt bracket → nacelle bearing. Secure with M3 set screw on outer face. Apply a drop of Loctite 243 (medium) to the set screw thread."},
      {t:"Install nacelle EDF",d:"For 70mm EDF: slide into nacelle pod from the top (intake face). The motor mount ears align with M2.5 captive nuts pre-inserted into the pod. Torque all 4× M2.5 screws to 0.3 N·m. Route motor leads through the 4mm wire channel in the nacelle wall and through the hollow CF spar toward the ESC."},
      {t:"Install tilt servo",d:"MG90S servo mounts to CF-PETG tilt bracket via M2 screws and 5mm aluminium standoffs. Connect servo horn to nacelle push-rod anchor at 18mm radius. Servo travel: 90° from centrepoint gives full 0°–90° nacelle rotation. Check no binding at endpoints."},
      {t:"LED in nacelle tip",d:"Solder short lead to WS2812C-2020 LED (port = red, stbd = green). Epoxy LED into 2×2mm recess in clear PETG tip cap. Apply a tiny dot of 5-minute epoxy over LED for moisture sealing. Slip-fit cap over nacelle tip."},
      {t:"Final nacelle check",d:"Manually rotate nacelle through full 90° arc. It should turn freely with no binding, return to any position held without servo. Measure nacelle pod edge-to-spar clearance at both extremes — minimum 2mm. Check LED wires do not snag on pivot."},
    ]
  },
  {
    phase:"PHASE 4 · ELECTRONICS INSTALLATION",c:C.purple,
    steps:[
      {t:"Install Pico 2 + TRIHAT-1",d:"Mount Pico 2 on TRIHAT-1 using supplied 2×20 female header. Stack mounts at 60–90mm from nose on 4× M2.5 nylon standoffs (8mm height) on the cockpit CF bulkhead plate (cut from 2mm CF sheet: 55×38mm). Secure with M2.5 nylon nuts — use nylon throughout this bay to reduce RF interference."},
      {t:"Install CM4 stack",d:"CM4 Lite plugs into CM4-CARRIER-1 DF40 underside connectors. COMMS-HAT-1 stacks on top via 2×20 header. This 3-board sandwich mounts at 95–160mm on the avionics bay floor using 4× M2.5 aluminium standoffs (11mm). OS microSD installs in CM4-CARRIER-1 slot (bottom of stack). Log microSD in COMMS-HAT-1 slot (top of stack)."},
      {t:"Install GPS module",d:"TRIHAT-1 onboard M10Q is pre-soldered. The U.FL coax runs from TRIHAT-1 to the GPS patch antenna on the cockpit roof (via 3mm access hole in cockpit bulkhead). Secure coax with a small PLA cable guide. Do not kink the U.FL connector — minimum bend radius 10mm."},
      {t:"Install airspeed sensor",d:"MS4525DO mounts on TRIHAT-1 via the JST-ZH I²C connector included with the board. Route 2×2mm ID silicone tubing from the sensor pressure ports to the pitot tube port at the nose (stagnation line) and a static port on the hull side at 80mm. Colour-code: red=stagnation, white=static."},
      {t:"Install ESCs",d:"Mount 3 ESCs on the keel underside with double-sided foam tape and one M2.5 screw through their mounting tab. ESC-L and ESC-R for the nacelles at 145–155mm from nose. ESC-fwd for the 40mm EDF at 285–295mm. Route motor leads along the spar/keel channels with cable ties every 30mm."},
      {t:"Install SiK and RCRS",d:"SiK 915MHz air unit sits inside the COMMS-HAT-1 radio compartment. Its IPEX pigtail exits through the fuselage to the SMA-RP bulkhead connector at the belly 238mm point. 49MHz RCRS module coax routes from COMMS-HAT-1 to the dorsal antenna fin at 290mm via the starboard keel spine. Secure both pigtails with a P-clip at the keel."},
    ]
  },
  {
    phase:"PHASE 5 · VARIABLE NOZZLE ASSEMBLY",c:C.yellow,
    steps:[
      {t:"Print nozzle parts",d:"Print inner rotating ring in CF-PETG vertically (layer lines perpendicular to ring axis for best hoop strength). Print 8 flaps in PETG flat. Print outer housing in PETG at 25% infill. Test-fit ring inside housing — it should rotate with light finger pressure with no wobble."},
      {t:"Assemble flaps",d:"Insert M1.5×8mm pivot pins through flap hinge holes. Seat pivot pins in outer housing recesses. Each flap should pivot freely around its pin. Apply one drop of light machine oil (sewing machine oil) to each pivot pin."},
      {t:"Install inner ring",d:"Screw inner ring into outer housing — the BamJr design uses a coarse thread to raise/lower the ring, which cams the flaps. Install the taller inner ring variant for greater expansion range. Rotate ring by hand: CCW = flaps open (hover), CW = flaps close (cruise). Verify smooth cam action."},
      {t:"Mount SG90 servo",d:"Secure SG90 to the M2.5 boss on the outer housing using the included servo bracket and M2 screws. Attach servo horn at 12 o'clock (90° centre position). Connect 1.5mm pushrod from horn outer hole to the cam arm on the inner ring — 18mm from ring centre. Adjust pushrod length so horn centre = nozzle 100% area."},
      {t:"Install nozzle in engine bell",d:"Insert assembled nozzle from the aft of the engine bell. The outer housing clips into the bell's 70mm ID recess with a quarter-turn bayonet lock (3D-printed tabs). Servo cable routes along the keel to Pico 2 GP15. The aft LED (tail) mounts in the engine bell ring recess above the nozzle."},
      {t:"Nozzle calibration",d:"Connect Pico 2 to computer via USB. In calibration mode, command GP15 to 1.0ms (open) and measure nozzle exit diameter with calipers: target 42mm. Command 2.0ms (closed): target 36mm. If out of spec, adjust pushrod length at the clevis end. Lock with Loctite 243."},
    ]
  },
  {
    phase:"PHASE 6 · WIRING & POWER",c:C.green,
    steps:[
      {t:"Power bus installation",d:"Mount XT60 power distribution board at 130mm on keel underside. Run 12AWG red/black silicone from battery bay connector to PDB. Run 12AWG silicone from PDB to each ESC. Solder all joints with 60/40 rosin-core solder. Use silicone sleeving over all bare joints — no heat shrink near printed parts."},
      {t:"BEC installation",d:"5V 3A switching BEC takes input from PDB +5V tap. BEC output (5V/GND) connects to: Pico 2 VSYS · CM4 carrier J_PWR · servo rail (shared GND, 5V). Use JST-PH 2-pin for BEC output connectors. Measure BEC output with multimeter: must be 5.0V ± 0.1V with all loads connected."},
      {t:"Ethernet inter-board cable",d:"Route 6-pin JST-GH Ethernet cable (150mm) from TRIHAT-1 J3 along the port keel spine to COMMS-HAT-1 J2. Cable-tie every 40mm. Do not route alongside ESC power cables. Verify no tension on connectors — leave 20mm service loop at each end."},
      {t:"CAN FD inter-board cable",d:"Route 4-pin JST-GH CAN FD cable (120mm) from TRIHAT-1 J2 along the starboard keel spine to COMMS-HAT-1 J1. Maintain ≥20mm separation from the Ethernet cable. Verify TRIHAT-1 120Ω termination solder bridge is populated. Verify COMMS-HAT-1 bridge is NOT populated."},
      {t:"Signal wiring",d:"Connect nacelle servo L/R to TRIHAT-1 GP17/18 (PWM channels). Nozzle servo to TRIHAT-1 GP15. Release servo to TRIHAT-1 GP22. Winch DRV8833 IN1/IN2 to TRIHAT-1 GP22/23. LED chain data to TRIHAT-1 GP26. Label each connector with a Dymo label or colour-coded heat shrink at both ends."},
      {t:"Continuity check",d:"Before applying any power: use multimeter to verify no shorts between +V and GND on: main bus, BEC output, USB5V, 3.3V rails. Verify no continuity between motor phases and ESC power rails (insulation check). Then connect battery via XT60 to a current-limited bench supply at 2A max — verify no smoke, excessive heat, or unexpected current draw."},
    ]
  },
  {
    phase:"PHASE 7 · SOFTWARE SETUP",c:C.pink,
    steps:[
      {t:"Flash Pico 2",d:"Download Pico SDK v2.0+. Clone flight controller repo. Build with cmake targeting RP2350. Flash via USB drag-drop (hold BOOTSEL during power-on). Verify heartbeat LED (GP25) blinks at 1Hz after flash."},
      {t:"Flash CM4 OS",d:"Flash Raspberry Pi OS Lite 64-bit (bookworm) to microSD using rpi-imager. In rpi-imager advanced settings: set hostname=serenity, enable SSH, set WiFi SSID/password for home network. Insert SD into CM4-CARRIER-1 slot. Boot CM4 and SSH in."},
      {t:"Install CM4 software",d:"On CM4: apt install mavlink-router python3-pip. pip install mavsdk pymavlink python-can dronecan. Configure mavlink-router to bridge UART0 (SiK) to UDP 14550 and to Pico 2 W5500 at 192.168.10.1:14550. Enable SPI, CAN interfaces via raspi-config."},
      {t:"Configure TPM",d:"apt install tpm2-tools tpm2-tss. Run: tpm2_getcap properties-fixed to verify SLB9670 is detected. Provision device key: tpm2_createprimary + tpm2_create + tpm2_load. Store key handle for runtime attestation. This enables signed telemetry and encrypted OTA updates."},
      {t:"ESC calibration",d:"With no propellers fitted: connect USB to Pico 2. Enter ESC calibration mode. Full throttle on all three ESC channels simultaneously (WOT signal). Connect battery — ESCs play startup tones. Throttle to zero — ESCs arm. Run full-throttle 2s test per ESC to verify rotation direction. Reverse any motor phase pair as needed to correct direction."},
      {t:"Nacelle servo calibration",d:"Command left nacelle to 0° (cruise) and 90° (hover) via Pico 2 calibration routine. Measure with digital angle gauge. Adjust servo arm position or endpoint in firmware to achieve ±0.5° accuracy at both stops. Verify smooth sweep with no binding. Verify tilt axis is truly perpendicular to airspeed vector."},
    ]
  },
  {
    phase:"PHASE 8 · GROUND TEST",c:C.lime,
    steps:[
      {t:"Static balance check",d:"Mount on precision balance to find actual CG. Target: 152mm from nose tip. Slide battery rail to achieve target. With 250g payload installed, re-measure: expect CG to shift 5–8mm fwd — slide battery 10mm aft to compensate. Verify T/W at actual AUW."},
      {t:"Radio link check",d:"With SiK ground radio connected to GCS laptop and QGroundControl running: verify MAVLink heartbeat at 1Hz. Verify attitude (roll/pitch/yaw) responds to hand-tilt of aircraft. Verify RC input from 49MHz ground transmitter appears in QGC RC calibration screen. Verify TDDS channel selection — unit should auto-select clearest channel within 30s of power-on."},
      {t:"Bench thrust test",d:"WITHOUT PROPELLERS/EDF FANS: verify all ESC outputs respond to throttle from GCS or RC. Slowly advance throttle per ESC to verify correct fan rotation direction and no vibration from duct misalignment. THEN: with fans installed, tether aircraft firmly to bench with 4 straps. Advance to 30% throttle per nacelle. Measure bench thrust with luggage scale if available. Verify ≥180g per 70mm nacelle at 30%."},
      {t:"Nozzle function test",d:"Command nozzle open (hover mode): verify exit dia ~42mm. Command nozzle closed (cruise mode): verify exit dia ~36mm. Verify servo does not bind at either extreme. Verify Pico 2 correctly interpolates nozzle position during a simulated nacelle sweep from 90° to 0°."},
      {t:"Navigation light test",d:"Arm aircraft (motors not running). Verify: port tip = steady red, stbd tip = steady green, tail = steady white, dorsal = flashing red 60FPM, belly = flashing white 60FPM. Disarm: verify port/stbd turn off, tail stays on, strobes continue. Trigger low-battery condition in firmware: verify port+stbd flash alternating red/white 2Hz."},
      {t:"GPS and sensor check",d:"With aircraft outdoors, clear sky view: verify GPS fix within 90s, HDOP ≤1.5, ≥6 satellites in QGC. Spin up EDFs to hover throttle (~46%) — verify GPS HDOP does not degrade >0.3 with fans running. Verify barometer altitude within ±5m of known elevation. Verify airspeed reads 0 ± 0.3 m/s with no pitot flow."},
    ]
  },
  {
    phase:"PHASE 9 · FIRST FLIGHT",c:C.green,
    steps:[
      {t:"Pre-flight checks",d:"ABCD: Airframe (all hatches closed, propellers secure, no loose wires visible externally), Battery (fully charged, XT60 secure, balance lead plugged into checker showing all cells 4.18–4.20V), Communications (RC link active, GCS link active, GPS fix confirmed), Documentation (Part 107 remote pilot cert visible, aircraft registered, location authorised, NOTAMs checked)."},
      {t:"Hover test 1m AGL",d:"Fly to 1m AGL in VTOL hover. Hold 30s. Verify stable attitude, no drift. Land. Inspect all screws, servo linkages, ESC temperatures (should be warm but not hot — under 60°C with IR thermometer). Verify no unusual vibration sounds from ducts."},
      {t:"Hover characterisation",d:"Fly to 3m AGL. Test roll, pitch, yaw inputs gently (±10° excursions). Verify aircraft returns to level when sticks centred. Test altitude hold. Verify landing light activates on command. Record hover amperage from telemetry — should match calculated hover current within ±10%."},
      {t:"Transition test",d:"At ≥8m AGL, command nacelle sweep (hover→cruise transition). Aircraft will accelerate forward. Monitor altitude — expect ±1.5m variation during transition. Verify Pico 2 automatically closes nozzle during sweep. Achieve straight-and-level cruise at ≥15 m/s. Monitor all temperatures and voltages."},
      {t:"Cruise characterisation",d:"In cruise: verify airspeed sensor reads plausibly (±2 m/s of GPS groundspeed in zero wind). Test gentle bank turns ≤20°. Verify nozzle is in closed position. Record cruise amperage — should match calculated value. Command transition back to hover and land."},
      {t:"Cargo mission test",d:"Load 250g payload. Swap to cargo battery (2800mAh). Repeat hover test — confirm aircraft still lifts cleanly (T/W 2.01:1). Test winch deploy: hover at 4m, deploy payload, verify it descends at ~15cm/s. Command winch retract. Land with deployed payload as final test."},
    ]
  },
];

function BuildGuideTab(){
  const [open,setOpen]=useState(0);
  return(<div>
    <div style={{background:"rgba(74,222,128,0.05)",border:`1px solid rgba(74,222,128,0.2)`,borderRadius:4,padding:"10px 14px",marginBottom:20,fontFamily:M,fontSize:11,color:C.dim,lineHeight:1.8}}>
      <span style={{color:C.green,fontWeight:"bold"}}>BUILD SEQUENCE:</span> Follow phases in order. Do not skip ahead — later phases depend on earlier fits being verified. Estimated build time: <span style={{color:C.yellow}}>40–55 hours</span> for an experienced builder. Allow 70+ hours for first-time composite builders.
    </div>
    {BUILD_PHASES.map((p,pi)=>(
      <div key={pi} style={{marginBottom:8}}>
        <div onClick={()=>setOpen(open===pi?-1:pi)} style={{display:"flex",alignItems:"center",gap:12,padding:"10px 14px",background:open===pi?`${p.c}10`:"rgba(255,255,255,0.02)",border:`1px solid ${open===pi?p.c:C.border}`,borderRadius:4,cursor:"pointer",userSelect:"none"}}>
          <div style={{width:8,height:8,background:p.c,borderRadius:"50%",flexShrink:0}}/>
          <span style={{color:p.c,fontFamily:M,fontSize:12,fontWeight:"bold",letterSpacing:"0.06em"}}>{p.phase}</span>
          <span style={{color:C.dimmer,fontFamily:M,fontSize:10,marginLeft:"auto"}}>{p.steps.length} steps · click to {open===pi?"collapse":"expand"}</span>
        </div>
        {open===pi&&(
          <div style={{border:`1px solid ${p.c}33`,borderTop:"none",borderRadius:"0 0 4px 4px",background:`${p.c}05`,padding:"12px 14px"}}>
            {p.steps.map((s,si)=>(
              <div key={si} style={{display:"flex",gap:14,padding:"10px 0",borderBottom:si<p.steps.length-1?"1px solid rgba(255,255,255,0.06)":"none"}}>
                <div style={{display:"flex",flexDirection:"column",alignItems:"center",gap:4,flexShrink:0}}>
                  <div style={{width:24,height:24,background:p.c,borderRadius:"50%",display:"flex",alignItems:"center",justifyContent:"center",color:"#000",fontFamily:M,fontSize:10,fontWeight:"bold"}}>{si+1}</div>
                  {si<p.steps.length-1&&<div style={{width:1,flex:1,background:`${p.c}30`}}/>}
                </div>
                <div style={{flex:1,paddingTop:2}}>
                  <div style={{color:p.c,fontFamily:M,fontSize:11,fontWeight:"bold",marginBottom:4}}>{s.t}</div>
                  <div style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.75}}>{s.d}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    ))}
    <div style={{marginTop:20,padding:"14px 16px",border:`1px solid rgba(255,230,0,0.3)`,background:"rgba(255,230,0,0.04)",borderRadius:4}}>
      <div style={{color:C.yellow,fontFamily:M,fontSize:12,fontWeight:"bold",letterSpacing:"0.06em",marginBottom:10}}>⚠ CRITICAL SAFETY REMINDERS</div>
      {["ALWAYS remove props/fan guards before any programming or calibration session. Treat every EDF as dangerous even when 'not armed'.",
        "Never exceed T/W 2.0 minimum. Always calculate actual AUW before flight with current battery and payload.",
        "GPS lock (HDOP ≤1.5, ≥6 sats) is REQUIRED before transition to cruise. Do not transition below 8m AGL.",
        "LiPo fire: keep a Class D fire extinguisher or LiPo safe bag on site. Charge in a fireproof bag, never unattended.",
        "Part 107 (US): aircraft >250g requires registration. Night ops require anti-collision lights (already installed). Maintain VLOS at all times.",
        "CAN bus: always verify termination before flight. A missing 120Ω terminator causes data corruption that may result in loss of CM4 control link.",
      ].map((s,i)=>(<div key={i} style={{display:"flex",gap:10,padding:"4px 0",borderBottom:"1px solid rgba(255,230,0,0.1)"}}>
        <span style={{color:C.yellow,fontFamily:M,fontSize:11,flexShrink:0}}>!</span>
        <span style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.7}}>{s}</span>
      </div>))}
    </div>
  </div>);
}

// ════════════════════════════════════════════════════════════════
//  APP
// ════════════════════════════════════════════════════════════════
const TABS=["Overview","Battery","Propulsion","Nav Lights","Antenna","Wiring","BOM","SBOM","Build Guide"];

_ODFontLoader();
export default function App(){
  const [tab,setTab]=useState("Overview");
  return(
    <div style={{minHeight:"100vh",background:C.bg,color:C.text,fontFamily:M}}>
      <Grid/>
      <div style={{position:"relative",zIndex:1,borderBottom:`1px solid ${C.border}`,padding:"16px 24px 14px"}}>
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",flexWrap:"wrap",gap:12}}>
          <div>
            <div style={{color:"rgba(0,229,255,0.28)",fontSize:9,letterSpacing:"0.2em",marginBottom:4}}>SERENITY TILTROTOR · MASTER SPECIFICATION · REV D</div>
            <h1 style={{margin:0,fontSize:19,fontWeight:"normal",color:"#fff",letterSpacing:"0.07em"}}>SERENITY DRONE — REV D</h1>
            <div style={{color:"rgba(0,229,255,0.48)",fontSize:10,marginTop:4}}>
              70mm nacelles · 40mm var-nozzle · dual battery scenarios · full build guide
            </div>
          </div>
          <div style={{textAlign:"right",fontFamily:M}}>
            <div style={{color:C.yellow,fontSize:12}}>EMPTY: {REC_EMPTY.auw}g · T/W {REC_EMPTY.tw}</div>
            <div style={{color:C.orange,fontSize:12,marginTop:2}}>CARGO: {REC_CARGO.auw}g · T/W {REC_CARGO.tw}</div>
            <div style={{color:C.dimmer,fontSize:9,marginTop:2}}>empty hover {REC_EMPTY.hMin}m · cargo hover {REC_CARGO.hMin}m</div>
          </div>
        </div>
        <div style={{display:"flex",gap:2,marginTop:12,flexWrap:"wrap"}}>
          {TABS.map(t=>(<button key={t} onClick={()=>setTab(t)} style={{background:tab===t?"rgba(0,229,255,0.09)":"transparent",border:`1px solid ${tab===t?C.accent:"rgba(0,229,255,0.13)"}`,color:tab===t?C.accent:C.dimmer,padding:"4px 12px",fontFamily:M,fontSize:10,cursor:"pointer",letterSpacing:"0.06em",transition:"all 0.12s"}}>{t}</button>))}
        </div>
      </div>
      <div style={{position:"relative",zIndex:1,padding:"20px 24px",maxWidth:1060,margin:"0 auto"}}>
        {tab==="Overview"    && <OverviewTab/>}
        {tab==="Battery"     && <BatteryTab/>}
        {tab==="Propulsion"  && <PropulsionTab/>}
        {tab==="Nav Lights"  && <NavLightsTab/>}
        {tab==="Antenna"     && <AntennaTab/>}
        {tab==="Wiring"      && <WiringTab/>}
        {tab==="BOM"         && <BomTab/>}
        {tab==="SBOM"        && <SbomTab/>}
        {tab==="Build Guide" && <BuildGuideTab/>}
      </div>
      <div style={{position:"relative",zIndex:1,borderTop:`1px solid ${C.border}`,padding:"10px 24px",display:"flex",justifyContent:"space-between",flexWrap:"wrap",gap:6}}>
        <span style={{color:"rgba(0,229,255,0.16)",fontSize:8,letterSpacing:"0.12em"}}>SERENITY TILTROTOR REV D · HULL: PETER FARELL PRINTABLES.COM/548545 · NOZZLE: BAMJR THINGIVERSE.COM/THING:2991269 CC BY 4.0</span>
        <span style={{color:"rgba(0,229,255,0.16)",fontSize:8}}>REFERENCE DESIGN · NOT FOR CERTIFICATION · VERIFY BEFORE FLIGHT</span>
      </div>
    </div>
  );
}
