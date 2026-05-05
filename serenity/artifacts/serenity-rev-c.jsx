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
  bg:"#060810", border:"rgba(0,229,255,0.11)", accent:"#00e5ff",
  orange:"#ff6b35", yellow:"#ffe600", purple:"#c084fc", green:"#4ade80",
  pink:"#f472b6", teal:"#2dd4bf", red:"#f87171", lime:"#a3e635",
  dim:"rgba(255,255,255,0.90)", dimmer:"rgba(255,255,255,0.80)", text:"rgba(255,255,255,0.82)",
};
const M = "'OpenDyslexic Mono','OpenDyslexic','OpenDyslexicMono',monospace";

// ── performance constants ─────────────────────────────────────
const THRUST_NAC = 1600, THRUST_FWD = 140, THRUST_TOT = 1740;
const AUW_BASE   = 512;   // g without battery
const EDF65_MAX  = 28;    // A each at WOT
const EDF35_MAX  = 12;    // A
const BAT_V      = 18.5;
const AVIONICS_A = 2.0;   // A equiv at battery voltage
const CRUISE_TOT = EDF35_MAX*0.88 + EDF65_MAX*Math.pow(0.14,1.5)*2 + AVIONICS_A;

function hovI(auw){ return EDF65_MAX*Math.pow(auw/2/800,1.5)*2 + AVIONICS_A; }

const BATS = [
  {id:"A",name:"5S 2200mAh 75C",brand:"CNHL/Tattu",    mass:220,cap:2200,Cc:75,note:"Baseline"},
  {id:"B",name:"5S 2500mAh 60C",brand:"Tattu R-Line",  mass:248,cap:2500,Cc:60,note:"Good step-up"},
  {id:"C",name:"5S 2600mAh 45C",brand:"CNHL Minima",   mass:254,cap:2600,Cc:45,note:"Budget option"},
  {id:"D",name:"5S 2800mAh 45C",brand:"Tattu/GNB",     mass:271,cap:2800,Cc:45,note:"★ RECOMMENDED"},
  {id:"E",name:"5S 3000mAh 30C",brand:"Gens Ace",      mass:284,cap:3000,Cc:30,note:"C-rating marginal"},
  {id:"F",name:"5S 3000mAh 45C",brand:"Tattu",         mass:292,cap:3000,Cc:45,note:"Exceeds mass limit"},
];
BATS.forEach(b=>{
  b.auw=AUW_BASE+b.mass; b.tw=(THRUST_NAC/b.auw).toFixed(2); b.ok=THRUST_NAC/b.auw>=2.0;
  b.hA=hovI(b.auw); b.hMin=(b.cap/1000*0.8/b.hA*60).toFixed(1);
  b.cMin=(b.cap/1000*0.8/CRUISE_TOT*60).toFixed(1); b.maxA=b.cap/1000*b.Cc;
});
const REC = BATS.find(b=>b.id==="D");

// ── primitives ────────────────────────────────────────────────
const SH=({t,c=C.accent,mt=22})=>(
  <div style={{display:"flex",alignItems:"center",gap:10,marginBottom:14,marginTop:mt}}>
    <div style={{width:3,height:17,background:c}}/>
    <span style={{color:c,fontFamily:M,fontSize:13,letterSpacing:"0.13em",textTransform:"uppercase",fontWeight:"normal"}}>{t}</span>
  </div>
);
const KV=({k,v,vc=C.text,u=""})=>(
  <div style={{display:"flex",justifyContent:"space-between",padding:"5px 0",
    borderBottom:"1px solid rgba(0,229,255,0.07)",alignItems:"baseline"}}>
    <span style={{color:C.dim,fontFamily:M,fontSize:11}}>{k}</span>
    <span style={{color:vc,fontFamily:M,fontSize:11}}>{v}{u&&<span style={{color:C.accent,marginLeft:4,fontSize:10}}>{u}</span>}</span>
  </div>
);
const Note=({c=C.dim,ch})=>(
  <div style={{marginTop:8,marginBottom:6,color:c,fontFamily:M,fontSize:10,lineHeight:1.85,
    padding:"8px 12px",borderLeft:`2px solid ${c}55`,background:`${c}07`,borderRadius:3}}>{ch}</div>
);
const Warn=({ch})=>(
  <div style={{marginTop:8,color:C.yellow,fontFamily:M,fontSize:10,lineHeight:1.8,
    padding:"7px 12px",borderLeft:`2px solid ${C.yellow}`,background:"rgba(255,230,0,0.05)",borderRadius:3}}>⚠ {ch}</div>
);
const Good=({ch})=>(
  <div style={{marginTop:8,color:C.green,fontFamily:M,fontSize:10,lineHeight:1.8,
    padding:"7px 12px",borderLeft:`2px solid ${C.green}`,background:"rgba(74,222,128,0.05)",borderRadius:3}}>✓ {ch}</div>
);
function TH({cols}){return(<thead><tr>{cols.map(h=>(<th key={h} style={{padding:"6px 10px",borderBottom:`1px solid ${C.border}`,color:C.accent,textAlign:"left",fontWeight:"normal",fontSize:10,letterSpacing:"0.07em",whiteSpace:"nowrap",opacity:.85}}>{h}</th>))}</tr></thead>);}
function Grid(){return(
  <svg style={{position:"fixed",inset:0,width:"100%",height:"100%",pointerEvents:"none",zIndex:0}}>
    <defs>
      <pattern id="sg" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0L0 0 0 20" fill="none" stroke="rgba(0,229,255,0.035)" strokeWidth={0.5}/></pattern>
      <pattern id="lg" width="100" height="100" patternUnits="userSpaceOnUse"><rect width="100" height="100" fill="url(#sg)"/><path d="M100 0L0 0 0 100" fill="none" stroke="rgba(0,229,255,0.065)" strokeWidth={1}/></pattern>
    </defs>
    <rect width="100%" height="100%" fill="url(#lg)"/>
  </svg>
);}

// ── hull geometry helpers ─────────────────────────────────────
const SC=(mm)=>mm*1.28, NX=55, xp=(mm)=>NX+SC(mm);
const PROF=[[0,0],[8,10],[22,18],[40,30],[58,36],[88,37],[120,42],[140,42],[165,40],[190,36],[220,29],[252,18],[260,16],[278,24],[305,29],[330,28],[360,22]];
function hullPath(CY){
  const up=PROF.map(([x,y])=>[xp(x),CY-SC(y)]);
  const lo=[...PROF].reverse().map(([x,y])=>[xp(x),CY+SC(y)]);
  return[...up,...lo].map((p,i)=>i===0?`M${p[0]},${p[1]}`:`L${p[0]},${p[1]}`).join(" ")+"Z";
}
function Arms({CY,stroke=C.accent}){
  return[-1,1].map(side=>(
    <g key={side}>
      <line x1={xp(128)} y1={CY+side*SC(50)} x2={xp(160)} y2={CY+side*SC(340)} stroke={stroke} strokeWidth={1.4}/>
      <ellipse cx={xp(155)} cy={CY+side*SC(340)} rx={SC(32)} ry={SC(13)} fill="rgba(0,229,255,0.04)" stroke={stroke} strokeWidth={1.1}/>
    </g>
  ));
}

// ══════════════════════════════════════════════════════════════
// 1 · OVERVIEW
// ══════════════════════════════════════════════════════════════
function OverviewTab(){
  return(
    <div>
      <div style={{display:"grid",gridTemplateColumns:"repeat(4,1fr)",gap:12,marginBottom:20}}>
        {[
          {l:"AUW (rec. battery)",v:`${REC.auw}g`,c:C.yellow,s:"5S 2800mAh 45C"},
          {l:"Nacelle T/W",v:`${REC.tw}:1`,c:C.green,s:"2× 65mm @ 5S"},
          {l:"Hover endurance",v:`${REC.hMin} min`,c:C.orange,s:"80% usable capacity"},
          {l:"Cruise endurance",v:`${REC.cMin} min`,c:C.teal,s:"35mm fwd + 14% nacelle"},
        ].map((s,i)=>(
          <div key={i} style={{padding:"10px 12px",border:`1px solid ${s.c}44`,background:`${s.c}07`,borderRadius:4}}>
            <div style={{color:C.dim,fontFamily:M,fontSize:9,letterSpacing:"0.08em",marginBottom:3}}>{s.l}</div>
            <div style={{color:s.c,fontFamily:M,fontSize:20,fontWeight:"bold"}}>{s.v}</div>
            <div style={{color:C.dimmer,fontFamily:M,fontSize:9,marginTop:2}}>{s.s}</div>
          </div>
        ))}
      </div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
        <div>
          <SH t="System Summary" mt={0}/>
          <KV k="Hull" v="Serenity Firefly-class · 360mm · PETG/CF-PETG shell"/>
          <KV k="Propulsion" v="2× 65mm EDF nacelles · 1× 35mm fwd EDF"/>
          <KV k="Thrust (nacelles)" v={`${THRUST_NAC}g`} vc={C.green}/>
          <KV k="Flight controller" v="Pico 2 + TRIHAT-1"/>
          <KV k="Companion" v="CM4 Lite 4GB + CM4-CARRIER-1 + COMPHAT-1"/>
          <KV k="Radio" v="SiK 915MHz + 49MHz RCRS TDDS"/>
          <KV k="Inter-board" v="100BASE-T Ethernet + CAN FD 4Mbps · JST-GH"/>
          <KV k="Nav lights" v="6× WS2812C ICAO/14CFR compliant"/>
          <KV k="Payload" v="200g · winch + release · 70×50×35mm bay"/>
          <KV k="Battery (rec.)" v={`5S 2800mAh 45C · ${REC.auw}g AUW`} vc={C.green}/>
          <KV k="Estimated BOM" v="$580–660" vc={C.yellow}/>
        </div>
        <div>
          <SH t="Revision History" mt={0}/>
          {[
            {r:"Rev A",d:"60mm nacelles + 30mm fwd · T/W 1.87 (below 2.0 minimum)"},
            {r:"Rev B",d:"65mm nacelles + 35mm fwd · T/W 2.19 · +36g vs Rev A"},
            {r:"Rev C",d:"Battery optimisation · nav lights · Serenity antenna · ETH+CAN wiring · BOM+SBOM",cur:true},
          ].map((r,i)=>(
            <div key={i} style={{display:"flex",gap:10,padding:"7px 0",borderBottom:"1px solid rgba(0,229,255,0.07)"}}>
              <span style={{color:r.cur?C.green:C.dim,fontFamily:M,fontSize:10,minWidth:44,fontWeight:r.cur?"bold":"normal"}}>{r.r}</span>
              <span style={{color:C.dimmer,fontFamily:M,fontSize:10,lineHeight:1.6}}>{r.d}</span>
            </div>
          ))}
          <Good ch={`Rev C: T/W ${REC.tw} · ${REC.hMin}min hover · ${REC.cMin}min cruise · all systems specified.`}/>
        </div>
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════
// 2 · BATTERY
// ══════════════════════════════════════════════════════════════
function BatteryTab(){
  const maxHov=Math.max(...BATS.filter(b=>b.ok).map(b=>parseFloat(b.hMin)));
  return(
    <div>
      <SH t="T/W ≥ 2.0 Constraint Analysis" mt={0}/>
      <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:12,marginBottom:18}}>
        {[
          {l:"Airframe (no battery)",v:`${AUW_BASE}g`,c:C.dim},
          {l:"Max battery for T/W=2.0",v:`${Math.floor(THRUST_NAC/2-AUW_BASE)}g`,c:C.orange},
          {l:"Nacelle thrust (fixed)",v:`${THRUST_NAC}g`,c:C.green},
        ].map((s,i)=>(<div key={i} style={{padding:"10px 12px",border:`1px solid ${s.c}44`,background:`${s.c}07`,borderRadius:4}}>
          <div style={{color:C.dim,fontFamily:M,fontSize:9,marginBottom:3}}>{s.l}</div>
          <div style={{color:s.c,fontFamily:M,fontSize:18,fontWeight:"bold"}}>{s.v}</div>
        </div>))}
      </div>
      <div style={{overflowX:"auto",marginBottom:20}}>
        <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
          <TH cols={["ID","BATTERY","MASS","CAP","C","MAX A","AUW","T/W","HOVER","CRUISE","NOTE"]}/>
          <tbody>{BATS.map((b,i)=>(
            <tr key={i} style={{background:b.id==="D"?"rgba(74,222,128,0.07)":i%2===0?"rgba(0,229,255,0.02)":"transparent"}}>
              <td style={{padding:"5px 9px",color:C.yellow,fontWeight:"bold"}}>{b.id}</td>
              <td style={{padding:"5px 9px",color:C.text,whiteSpace:"nowrap"}}>{b.name}</td>
              <td style={{padding:"5px 9px",color:C.orange}}>{b.mass}g</td>
              <td style={{padding:"5px 9px",color:C.text}}>{b.cap}</td>
              <td style={{padding:"5px 9px",color:C.text}}>{b.Cc}C</td>
              <td style={{padding:"5px 9px",color:b.maxA>=70?C.green:C.red}}>{b.maxA.toFixed(0)}A</td>
              <td style={{padding:"5px 9px",color:C.text}}>{b.auw}g</td>
              <td style={{padding:"5px 9px",color:b.ok?C.green:C.red,fontWeight:"bold"}}>{b.tw}</td>
              <td style={{padding:"5px 9px",color:b.ok?C.yellow:C.dimmer,fontWeight:b.id==="D"?"bold":"normal"}}>{b.ok?b.hMin+" min":"—"}</td>
              <td style={{padding:"5px 9px",color:b.ok?C.teal:C.dimmer}}>{b.ok?b.cMin+" min":"—"}</td>
              <td style={{padding:"5px 9px",color:b.id==="D"?C.green:b.ok?C.dim:C.red,fontSize:9}}>{b.note}</td>
            </tr>
          ))}</tbody>
        </table>
      </div>
      <SH t="Recommended: 5S 2800mAh 45C" c={C.green}/>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
        <div>
          <KV k="Capacity"         v="2800 mAh" vc={C.green}/>
          <KV k="Voltage"          v="5S · 18.5V nominal · 21.0V fully charged"/>
          <KV k="C-rating"         v="45C continuous"/>
          <KV k="Max continuous"   v={`${REC.maxA}A`} vc={C.green}/>
          <KV k="Peak draw (all fans WOT)" v="~70A" vc={C.green}/>
          <KV k="Mass"             v={`${REC.mass}g`}/>
          <KV k="AUW"              v={`${REC.auw}g`} vc={C.yellow}/>
          <KV k="T/W"              v={`${REC.tw}:1`} vc={C.green}/>
          <KV k="Hover endurance"  v={`${REC.hMin} min`} vc={C.yellow}/>
          <KV k="Cruise endurance" v={`${REC.cMin} min`} vc={C.teal}/>
          <KV k="Connector"        v="XT60 · 12AWG leads · 80mm"/>
          <KV k="Dimensions (typ)" v="118 × 35 × 29 mm"/>
          <KV k="Brands"           v="Tattu Funfly 2800 · GNB 2800 · Gens Ace G-Tech 2800"/>
        </div>
        <div>
          <SH t="Endurance vs Mass (T/W ≥ 2.0 only)" mt={0} c={C.teal}/>
          {BATS.filter(b=>b.ok).map(b=>(
            <div key={b.id} style={{display:"flex",alignItems:"center",gap:8,marginBottom:6}}>
              <span style={{color:b.id==="D"?C.green:C.yellow,fontFamily:M,fontSize:9,minWidth:18}}>{b.id}</span>
              <span style={{color:C.dim,fontFamily:M,fontSize:9,minWidth:140,whiteSpace:"nowrap"}}>{b.name}</span>
              <div style={{flex:1,background:"rgba(255,255,255,0.05)",borderRadius:2,height:10}}>
                <div style={{width:`${parseFloat(b.hMin)/maxHov*100}%`,height:"100%",
                  background:b.id==="D"?C.green:C.teal,opacity:.7,borderRadius:2}}/>
              </div>
              <span style={{color:b.id==="D"?C.green:C.teal,fontFamily:M,fontSize:9,minWidth:46}}>{b.hMin}m</span>
              <span style={{color:C.dimmer,fontFamily:M,fontSize:8,minWidth:44}}>T/W {b.tw}</span>
            </div>
          ))}
          <Note c={C.green} ch="5S 2800mAh 45C maximises hover endurance of any battery keeping T/W ≥ 2.0. 5S 3000mAh 45C (option F) exceeds the 288g mass limit and drops T/W to 1.99 — just outside the requirement."/>
          <Warn ch="Verify 45C rating on selected brand. At 70A peak draw, the 2800mAh at 45C delivers 126A capability — comfortable 1.8× margin. Avoid no-brand cells at this current level."/>
        </div>
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════
// 3 · NAV LIGHTS
// ══════════════════════════════════════════════════════════════
function NavDiagram(){
  const VW=720,VH=360,CY=180;
  const arc=(cx,cy,r,a1,a2,col)=>{
    const s=a1*Math.PI/180,e=a2*Math.PI/180;
    const x1=cx+r*Math.cos(s),y1=cy+r*Math.sin(s),x2=cx+r*Math.cos(e),y2=cy+r*Math.sin(e);
    return<path d={`M${cx},${cy} L${x1},${y1} A${r},${r} 0 ${a2-a1>180?1:0},1 ${x2},${y2} Z`}
      fill={`${col}18`} stroke={col} strokeWidth={0.8} opacity={0.8}/>;
  };
  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* coverage arcs */}
      {arc(xp(140),CY-SC(340),SC(52),-145,-35,"#ff2020")}
      {arc(xp(140),CY+SC(340),SC(52),35,145,"#00cc00")}
      {arc(xp(350),CY,SC(52),-70,70,"#ffffff")}
      <circle cx={xp(120)} cy={CY} r={SC(38)} fill="rgba(255,50,50,0.04)" stroke="#ff4444" strokeWidth={0.8} strokeDasharray="4 3" opacity={0.7}/>
      <circle cx={xp(160)} cy={CY} r={SC(33)} fill="rgba(255,255,255,0.02)" stroke="rgba(255,255,255,0.25)" strokeWidth={0.7} strokeDasharray="3 3"/>
      <circle cx={xp(30)} cy={CY} r={SC(28)} fill="rgba(255,255,100,0.05)" stroke="#ffff80" strokeWidth={0.8} strokeDasharray="3 3" opacity={0.6}/>
      {/* hull */}
      <path d={hullPath(CY)} fill="rgba(0,229,255,0.05)" stroke={C.accent} strokeWidth={1.5}/>
      <Arms CY={CY}/>
      {/* cockpit */}
      <ellipse cx={xp(44)} cy={CY} rx={SC(44)} ry={SC(24)} fill="rgba(0,229,255,0.06)" stroke={C.accent} strokeWidth={0.8}/>
      {/* port LED */}
      <circle cx={xp(140)} cy={CY-SC(340)} r={7} fill="#ff2020" opacity={0.95}/>
      <circle cx={xp(140)} cy={CY-SC(340)} r={16} fill="none" stroke="#ff2020" strokeWidth={0.7} opacity={0.4}/>
      <text x={xp(140)-22} y={CY-SC(340)-18} textAnchor="middle" fill="#ff2020" fontSize={8} fontFamily={M} fontWeight="bold">PORT ●</text>
      {/* stbd LED */}
      <circle cx={xp(140)} cy={CY+SC(340)} r={7} fill="#00cc00" opacity={0.95}/>
      <circle cx={xp(140)} cy={CY+SC(340)} r={16} fill="none" stroke="#00cc00" strokeWidth={0.7} opacity={0.4}/>
      <text x={xp(140)+22} y={CY+SC(340)+20} textAnchor="middle" fill="#00cc00" fontSize={8} fontFamily={M} fontWeight="bold">STBD ●</text>
      {/* tail */}
      <circle cx={xp(350)} cy={CY} r={7} fill="#eeeeee" opacity={0.95}/>
      <text x={xp(350)+20} y={CY-2} fill="#cccccc" fontSize={7} fontFamily={M}>TAIL ●</text>
      {/* anti-collision dorsal */}
      <circle cx={xp(120)} cy={CY} r={7} fill="#ff4444" opacity={0.95}/>
      <text x={xp(120)} y={CY-16} textAnchor="middle" fill="#ff4444" fontSize={7} fontFamily={M} fontWeight="bold">ACOL◆</text>
      {/* belly strobe */}
      <circle cx={xp(160)} cy={CY} r={5} fill="rgba(255,255,200,0.8)" stroke="#ffffaa" strokeWidth={0.8}/>
      <text x={xp(160)} y={CY+16} textAnchor="middle" fill="#ffffaa" fontSize={7} fontFamily={M}>BELLY◆</text>
      {/* landing */}
      <rect x={xp(22)} y={CY-SC(8)} width={SC(16)} height={SC(16)} rx={2} fill="rgba(255,255,120,0.2)" stroke="#ffff80" strokeWidth={1}/>
      <text x={xp(30)} y={CY-SC(13)} textAnchor="middle" fill="#ffff80" fontSize={7} fontFamily={M}>LAND</text>
      {/* legend */}
      {[["#ff2020","Port red (steady)"],["#00cc00","Stbd green (steady)"],
        ["#cccccc","Tail white (steady)"],["#ff4444","Anti-col dorsal (strobe)"],
        ["#ffffaa","Belly strobe"],["#ffff80","Landing light"]].map(([col,lbl],i)=>(
        <g key={i}><circle cx={14} cy={240+i*18} r={5} fill={col} opacity={0.9}/>
        <text x={24} y={244+i*18} fill={col} fontSize={8} fontFamily={M}>{lbl}</text></g>
      ))}
      <text x={VW/2} y={16} textAnchor="middle" fill="rgba(0,229,255,0.25)" fontSize={9} fontFamily={M} letterSpacing="0.12em">NAVIGATION LIGHT LAYOUT — TOP VIEW</text>
      <text x={NX-8} y={CY+4} textAnchor="end" fill={C.dimmer} fontSize={7} fontFamily={M}>NOSE</text>
      <text x={xp(360)+6} y={CY+4} fill={C.dimmer} fontSize={7} fontFamily={M}>TAIL</text>
    </svg>
  );
}

function NavLightsTab(){
  const lights=[
    {id:"PORT", col:"#ff2020",name:"Red",   pos:"Left nacelle leading edge tip",  arc:"≥110°",flash:"Steady",  lum:"≥300cd",reg:"ICAO Ann.2 · 14CFR91.209"},
    {id:"STBD", col:"#00cc00",name:"Green", pos:"Right nacelle leading edge tip", arc:"≥110°",flash:"Steady",  lum:"≥300cd",reg:"ICAO Ann.2 · 14CFR91.209"},
    {id:"TAIL", col:"#dddddd",name:"White", pos:"Aft hull, 340mm from nose",      arc:"≥140°",flash:"Steady",  lum:"≥300cd",reg:"ICAO Ann.2 · 14CFR91.209"},
    {id:"ACOL", col:"#ff4444",name:"Red",   pos:"Dorsal hull, 120mm from nose",   arc:"360°", flash:"60 FPM",  lum:"≥150cd avg",reg:"14CFR91.209 · AC107-2B"},
    {id:"BELY", col:"#ffffaa",name:"White", pos:"Belly hull, 160mm from nose",    arc:"lower",flash:"60 FPM",  lum:"≥100cd avg",reg:"FAA AC91-74"},
    {id:"LAND", col:"#ffff80",name:"White", pos:"Nose underside, 30mm from nose", arc:"fwd",  flash:"Steady (ops)",lum:"≥600cd",reg:"FAA AC20-74 · hover/land"},
  ];
  return(
    <div>
      <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:8,marginBottom:18}}>
        <NavDiagram/>
      </div>
      <div style={{overflowX:"auto",marginBottom:16}}>
        <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
          <TH cols={["LIGHT","COLOR","POSITION","ARC","FLASH","LUMENS","REGULATION"]}/>
          <tbody>{lights.map((l,i)=>(
            <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.02)":"transparent"}}>
              <td style={{padding:"5px 9px",color:l.col,fontWeight:"bold"}}>{l.id}</td>
              <td style={{padding:"5px 9px"}}><span style={{background:l.col,color:"#000",padding:"1px 6px",borderRadius:2,fontSize:9}}>{l.name}</span></td>
              <td style={{padding:"5px 9px",color:C.text}}>{l.pos}</td>
              <td style={{padding:"5px 9px",color:C.dim}}>{l.arc}</td>
              <td style={{padding:"5px 9px",color:l.flash.includes("FPM")?C.orange:C.green}}>{l.flash}</td>
              <td style={{padding:"5px 9px",color:C.yellow}}>{l.lum}</td>
              <td style={{padding:"5px 9px",color:C.dimmer,fontSize:9}}>{l.reg}</td>
            </tr>
          ))}</tbody>
        </table>
      </div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
        <div>
          <SH t="LED Controller" mt={0}/>
          <KV k="LED type"      v="WS2812C-2020 RGB · 5V · 2×2mm package"/>
          <KV k="Chain"         v="6 LEDs on single data line · daisy-chain"/>
          <KV k="Pico 2 pin"    v="GP26 → PIO0 state machine · 800kHz NZR"/>
          <KV k="Current (max)" v="~180mA all white · 60mA per LED"/>
          <KV k="Strobe rate"   v="60 FPM · 50ms ON / 950ms OFF per ICAO"/>
          <KV k="Wire"          v="28AWG silicone · 3-core · port→stbd→tail→dorsal→belly"/>
          <KV k="Power"         v="5V BEC rail · 0.9W max · negligible budget impact"/>
        </div>
        <div>
          <SH t="Serenity Mounting Details" mt={0}/>
          <KV k="Port/Stbd"  v="Recessed 2020 LED in clear PETG nacelle tip cap"/>
          <KV k="Tail"       v="Engine bell aft ring recess · flush with hull surface"/>
          <KV k="Anti-col"   v="Dorsal hull at cockpit-hull junction · clear PETG dome"/>
          <KV k="Belly"      v="Flush mount between payload bay and SiK antenna"/>
          <KV k="Landing"    v="Nose underside · angled 15° down · clear PETG lens"/>
          <Note c={C.orange} ch="Port/stbd LEDs rotate with nacelles. In cruise (0° tilt) they face forward-left/right as required. Anti-collision dorsal + belly strobes maintain 360° coverage in all modes and fill the horizontal plane gap during nacelle rotation."/>
        </div>
      </div>
      <SH t="Firmware Light States"/>
      {[["POWER ON (pre-arm)","Tail white ON · belly strobe 60FPM · all others OFF"],
        ["ARMED","Port red + stbd green steady · tail white · dorsal+belly strobe 60FPM"],
        ["LANDING / HOVER OPS","Landing light ON (full white) · all nav lights maintained"],
        ["TRANSITION","Port/stbd pulse amber 2Hz during nacelle sweep (status only)"],
        ["LOW BATTERY ≤20%","Port+stbd alternate red/white flash 2Hz"],
        ["FAILSAFE / RTL","All 6 LEDs flash simultaneously 2Hz"],
        ["DISARMED","Tail white steady · strobes continue per regulation"],
      ].map(([st,desc],i)=>(
        <div key={i} style={{display:"flex",gap:12,padding:"6px 0",borderBottom:"1px solid rgba(0,229,255,0.07)"}}>
          <span style={{color:C.teal,fontFamily:M,fontSize:10,minWidth:190,flexShrink:0}}>{st}</span>
          <span style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.6}}>{desc}</span>
        </div>
      ))}
    </div>
  );
}

// ══════════════════════════════════════════════════════════════
// 4 · ANTENNA
// ══════════════════════════════════════════════════════════════
function AntennaTab(){
  const VW=700,VH=300,CY=150;
  return(
    <div>
      <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:8,marginBottom:18}}>
        <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
          <path d={hullPath(CY)} fill="rgba(0,229,255,0.05)" stroke={C.accent} strokeWidth={1.5}/>
          <Arms CY={CY}/>
          <ellipse cx={xp(44)} cy={CY} rx={SC(44)} ry={SC(22)} fill="rgba(0,229,255,0.06)" stroke={C.accent} strokeWidth={0.8}/>
          {/* GPS */}
          <rect x={xp(46)} y={CY-SC(44)} width={SC(24)} height={SC(10)} rx={2} fill="rgba(74,222,128,0.25)" stroke="#4ade80" strokeWidth={1.5}/>
          <text x={xp(58)} y={CY-SC(50)} textAnchor="middle" fill="#4ade80" fontSize={8} fontFamily={M} fontWeight="bold">GPS 58mm</text>
          <text x={xp(58)} y={CY-SC(58)} textAnchor="middle" fill="rgba(74,222,128,0.5)" fontSize={6} fontFamily={M}>cockpit roof · 25×25mm RHCP patch</text>
          {/* 49MHz */}
          <circle cx={xp(290)} cy={CY-SC(28)} r={5} fill="rgba(244,114,182,0.25)" stroke={C.pink} strokeWidth={1.5}/>
          <line x1={xp(290)} y1={CY-SC(33)} x2={xp(290)} y2={CY-SC(78)} stroke={C.pink} strokeWidth={2} strokeLinecap="round"/>
          {[0,1,2,3].map(i=>(<ellipse key={i} cx={xp(290)} cy={CY-SC(41+i*8)} rx={4} ry={3} fill="none" stroke={C.pink} strokeWidth={0.9} opacity={0.75}/>))}
          <text x={xp(290)+16} y={CY-SC(76)} fill={C.pink} fontSize={7} fontFamily={M} fontWeight="bold">49MHz 290mm</text>
          <text x={xp(290)+16} y={CY-SC(67)} fill={`${C.pink}70`} fontSize={6} fontFamily={M}>Serenity dorsal aft spine · 250mm whip</text>
          {/* Dorsal ridge line */}
          <line x1={xp(150)} y1={CY} x2={xp(310)} y2={CY} stroke="rgba(0,229,255,0.18)" strokeWidth={1} strokeDasharray="6 3"/>
          <text x={xp(230)} y={CY-6} textAnchor="middle" fill="rgba(0,229,255,0.3)" fontSize={6} fontFamily={M}>Serenity dorsal keel spine</text>
          {/* SiK belly */}
          <circle cx={xp(238)} cy={CY} r={5} fill="rgba(255,107,53,0.2)" stroke={C.orange} strokeWidth={1.3} strokeDasharray="3 2"/>
          <text x={xp(238)} y={CY+18} textAnchor="middle" fill={C.orange} fontSize={8} fontFamily={M} fontWeight="bold">SiK↓ 238mm</text>
          <text x={xp(238)} y={CY+28} textAnchor="middle" fill={`${C.orange}60`} fontSize={6} fontFamily={M}>belly · SMA-RP · 82mm monopole</text>
          {/* WiFi */}
          <rect x={xp(195)} y={CY-SC(18)} width={SC(38)} height={SC(36)} rx={3} fill="rgba(192,132,252,0.06)" stroke={C.purple} strokeWidth={0.8} strokeDasharray="4 2"/>
          <text x={xp(214)} y={CY+2} textAnchor="middle" fill={C.purple} fontSize={7} fontFamily={M}>WiFi 210mm</text>
          <text x={xp(214)} y={CY+12} textAnchor="middle" fill={`${C.purple}55`} fontSize={6} fontFamily={M}>CM4 internal PCB trace</text>
          {/* Pitot */}
          <line x1={NX} y1={CY} x2={NX-22} y2={CY} stroke={C.teal} strokeWidth={2.5} strokeLinecap="round"/>
          {/* Sep dims */}
          <g opacity={0.28}>
            <line x1={xp(58)} y1={CY+SC(56)} x2={xp(290)} y2={CY+SC(56)} stroke={C.yellow} strokeWidth={0.6}/>
            <line x1={xp(58)} y1={CY+SC(53)} x2={xp(58)} y2={CY+SC(59)} stroke={C.yellow} strokeWidth={0.6}/>
            <line x1={xp(290)} y1={CY+SC(53)} x2={xp(290)} y2={CY+SC(59)} stroke={C.yellow} strokeWidth={0.6}/>
            <text x={(xp(58)+xp(290))/2} y={CY+SC(68)} textAnchor="middle" fill={C.yellow} fontSize={6} fontFamily={M}>232mm separation (GPS↔49MHz) ✔</text>
          </g>
          <text x={VW/2} y={14} textAnchor="middle" fill="rgba(0,229,255,0.25)" fontSize={9} fontFamily={M} letterSpacing="0.12em">ANTENNA LAYOUT — SERENITY HULL — TOP VIEW</text>
          <text x={NX-8} y={CY+4} textAnchor="end" fill={C.dimmer} fontSize={7} fontFamily={M}>NOSE</text>
          <text x={xp(360)+6} y={CY+4} fill={C.dimmer} fontSize={7} fontFamily={M}>TAIL</text>
        </svg>
      </div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
        <div>
          <SH t="GPS L1 Patch — 58mm" mt={0} c="#4ade80"/>
          <KV k="Type"    v="25×25mm RHCP ceramic patch · 12mm PLA standoff"/>
          <KV k="Serenity mount" v="Recessed into cockpit dome top flat area" vc={C.teal}/>
          <KV k="Cable"   v="U.FL → RG-178 ≤100mm → TRIHAT-1"/>
          <KV k="Keepout" v="≥40mm from CF · ≥150mm from 49MHz coil"/>
          <KV k="Sep. GPS→49MHz" v="232mm ✔" vc={C.green}/>
          <SH t="SiK 915MHz — 238mm belly" c={C.orange}/>
          <KV k="Type"    v="λ/4 monopole · 82mm · SMA-RP bulkhead"/>
          <KV k="Serenity mount" v="6.5mm hole in PETG belly at 238mm — clear expanse between payload bay edge (200mm) and aft skid strut (255mm)" vc={C.teal}/>
          <KV k="Cable"   v="IPEX pigtail to COMPHAT-1 SiK U.FL"/>
        </div>
        <div>
          <SH t="49MHz RCRS — 290mm dorsal" mt={0} c={C.pink}/>
          <KV k="Type"    v="250mm whip + 38μH base-loading coil"/>
          <KV k="Serenity mount" v="Integrated into Serenity's aft dorsal protrusion at 290mm — the raised spine naturally accommodates a vertical ABS/PETG antenna fin flush with the hull." vc={C.teal}/>
          <KV k="Fin"     v="35mm tall PETG fin · coil cavity inside · 4× radials under skin"/>
          <KV k="Cable"   v="RG-316 120mm → COMPHAT-1 U.FL"/>
          <KV k="SWR"     v="≤2.5:1 across 49.83–49.89MHz (trim with 5–30pF series cap)"/>
          <SH t="WiFi 2.4/5GHz — 210mm internal" c={C.purple}/>
          <KV k="Type"    v="CM4 on-board PCB trace antenna"/>
          <KV k="Serenity mount" v="Internal — hull is PETG at 210mm (RF transparent). No drilling required." vc={C.teal}/>
          <KV k="Keepout" v="15mm ground-plane clearance each side of trace on CM4-CARRIER-1"/>
        </div>
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════
// 5 · WIRING
// ══════════════════════════════════════════════════════════════
function WiringDiagram(){
  const VW=680,VH=370;
  const PX=50,PY=90,PW=180,PH=150;
  const CX2=450,CY2=90,CW=180,CH=150;
  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* Pico block */}
      <rect x={PX} y={PY} width={PW} height={PH} rx={5} fill="rgba(0,229,255,0.07)" stroke={C.accent} strokeWidth={1.5}/>
      <text x={PX+PW/2} y={PY+22} textAnchor="middle" fill={C.accent} fontSize={11} fontFamily={M} fontWeight="bold">PICO 2</text>
      <text x={PX+PW/2} y={PY+37} textAnchor="middle" fill="rgba(0,229,255,0.45)" fontSize={8} fontFamily={M}>flight controller</text>
      <line x1={PX+12} y1={PY+46} x2={PX+PW-12} y2={PY+46} stroke="rgba(0,229,255,0.18)" strokeWidth={0.7}/>
      <text x={PX+PW/2} y={PY+62} textAnchor="middle" fill={C.teal} fontSize={9} fontFamily={M} fontWeight="bold">TRIHAT-1</text>
      <text x={PX+PW/2} y={PY+76} textAnchor="middle" fill="rgba(45,212,191,0.6)" fontSize={8} fontFamily={M}>W5500 · GP8-13 · J3 ETH</text>
      <text x={PX+PW/2} y={PY+90} textAnchor="middle" fill="rgba(45,212,191,0.6)" fontSize={8} fontFamily={M}>MCP2518FD · GP14 · J2 CAN</text>
      <text x={PX+PW/2} y={PY+108} textAnchor="middle" fill="rgba(255,107,53,0.6)" fontSize={8} fontFamily={M}>IMU · Baro · GPS · Airspeed</text>
      <text x={PX+PW/2} y={PY+122} textAnchor="middle" fill="rgba(255,107,53,0.6)" fontSize={8} fontFamily={M}>SiK UART · ESC DSHOT · LEDs</text>
      <text x={PX+PW/2} y={PY+138} textAnchor="middle" fill="rgba(255,230,0,0.55)" fontSize={8} fontFamily={M}>TPM · Airspeed MS4525DO</text>
      {/* CM4 block */}
      <rect x={CX2} y={CY2} width={CW} height={CH} rx={5} fill="rgba(74,222,128,0.07)" stroke={C.green} strokeWidth={1.5}/>
      <text x={CX2+CW/2} y={CY2+22} textAnchor="middle" fill={C.green} fontSize={11} fontFamily={M} fontWeight="bold">CM4 LITE 4GB</text>
      <text x={CX2+CW/2} y={CY2+37} textAnchor="middle" fill="rgba(74,222,128,0.45)" fontSize={8} fontFamily={M}>companion computer</text>
      <line x1={CX2+12} y1={CY2+46} x2={CX2+CW-12} y2={CY2+46} stroke="rgba(74,222,128,0.18)" strokeWidth={0.7}/>
      <text x={CX2+CW/2} y={CY2+62} textAnchor="middle" fill={C.lime} fontSize={9} fontFamily={M} fontWeight="bold">COMPHAT-1</text>
      <text x={CX2+CW/2} y={CY2+76} textAnchor="middle" fill="rgba(163,230,53,0.6)" fontSize={8} fontFamily={M}>W5500 · GPIO17 · J2 ETH</text>
      <text x={CX2+CW/2} y={CY2+90} textAnchor="middle" fill="rgba(163,230,53,0.6)" fontSize={8} fontFamily={M}>MCP2518FD · GPIO7 · J1 CAN</text>
      <text x={CX2+CW/2} y={CY2+108} textAnchor="middle" fill="rgba(192,132,252,0.6)" fontSize={8} fontFamily={M}>TPM · μSD · 915MHz SiK</text>
      <text x={CX2+CW/2} y={CY2+122} textAnchor="middle" fill="rgba(192,132,252,0.6)" fontSize={8} fontFamily={M}>49MHz RCRS transceiver</text>
      <text x={CX2+CW/2} y={CY2+138} textAnchor="middle" fill="rgba(255,230,0,0.55)" fontSize={8} fontFamily={M}>mavlink-router · DroneCAN</text>
      {/* Ethernet cable */}
      <path d={`M${PX+PW},${PY+80} C${PX+PW+60},${PY+80} ${CX2-60},${CY2+80} ${CX2},${CY2+80}`}
        fill="none" stroke={C.purple} strokeWidth={3.5} strokeLinecap="round"/>
      <rect x={(PX+PW+CX2)/2-60} y={195} width={120} height={34} rx={3} fill={`${C.purple}15`} stroke={C.purple} strokeWidth={1}/>
      <text x={(PX+PW+CX2)/2} y={208} textAnchor="middle" fill={C.purple} fontSize={9} fontFamily={M} fontWeight="bold">100BASE-T ETHERNET</text>
      <text x={(PX+PW+CX2)/2} y={222} textAnchor="middle" fill={`${C.purple}80`} fontSize={7} fontFamily={M}>6-pin JST-GH · 150mm · UDP MAVLink</text>
      <text x={PX+PW+8} y={PY+78} fill={C.purple} fontSize={7} fontFamily={M}>J3</text>
      <text x={CX2-22} y={CY2+78} fill={C.purple} fontSize={7} fontFamily={M}>J2</text>
      {/* CAN FD cable */}
      <path d={`M${PX+PW},${PY+118} C${PX+PW+40},${PY+118} ${CX2-40},${CY2+118} ${CX2},${CY2+118}`}
        fill="none" stroke={C.orange} strokeWidth={3.5} strokeLinecap="round"/>
      <rect x={(PX+PW+CX2)/2-60} y={258} width={120} height={34} rx={3} fill={`${C.orange}12`} stroke={C.orange} strokeWidth={1}/>
      <text x={(PX+PW+CX2)/2} y={271} textAnchor="middle" fill={C.orange} fontSize={9} fontFamily={M} fontWeight="bold">CAN FD BUS</text>
      <text x={(PX+PW+CX2)/2} y={285} textAnchor="middle" fill={`${C.orange}80`} fontSize={7} fontFamily={M}>4-pin JST-GH · 120mm · 4Mbps FD</text>
      <text x={PX+PW+8} y={PY+116} fill={C.orange} fontSize={7} fontFamily={M}>J2</text>
      <text x={CX2-22} y={CY2+116} fill={C.orange} fontSize={7} fontFamily={M}>J1</text>
      {/* Pin tables */}
      <rect x={48} y={308} width={270} height={40} rx={3} fill={`${C.purple}10`} stroke={C.purple} strokeWidth={0.8}/>
      {[["1","GND"],["2","TX+"],["3","TX−"],["4","RX+"],["5","RX−"],["6","N/C"]].map(([pin,sig],i)=>(
        <g key={i}>
          <text x={58+i*43} y={322} fill={C.purple} fontSize={7} fontFamily={M}>P{pin}</text>
          <text x={58+i*43} y={337} fill={`${C.purple}80`} fontSize={7} fontFamily={M}>{sig}</text>
        </g>
      ))}
      <rect x={362} y={308} width={200} height={40} rx={3} fill={`${C.orange}10`} stroke={C.orange} strokeWidth={0.8}/>
      {[["1","GND"],["2","+5V"],["3","CANH"],["4","CANL"]].map(([pin,sig],i)=>(
        <g key={i}>
          <text x={372+i*46} y={322} fill={C.orange} fontSize={7} fontFamily={M}>P{pin}</text>
          <text x={372+i*46} y={337} fill={`${C.orange}80`} fontSize={7} fontFamily={M}>{sig}</text>
        </g>
      ))}
      <text x={185} y={358} textAnchor="middle" fill={`${C.purple}55`} fontSize={8} fontFamily={M}>Ethernet JST-GH pinout</text>
      <text x={462} y={358} textAnchor="middle" fill={`${C.orange}55`} fontSize={8} fontFamily={M}>CAN FD JST-GH pinout</text>
      <text x={VW/2} y={14} textAnchor="middle" fill="rgba(0,229,255,0.25)" fontSize={9} fontFamily={M} letterSpacing="0.12em">PICO 2 ↔ CM4 INTER-BOARD CONNECTIONS</text>
    </svg>
  );
}

function WiringTab(){
  return(
    <div>
      <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:8,marginBottom:18}}>
        <WiringDiagram/>
      </div>
      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
        <div>
          <SH t="Ethernet · TRIHAT-1 J3 ↔ COMPHAT-1 J2" mt={0} c={C.purple}/>
          <KV k="Connector" v="JST-GH 1.25mm 6-pin (both ends)"/>
          <KV k="Cable" v="Matched twisted-pair 100BASE-T · 150mm"/>
          <KV k="Pin 1" v="GND"/>
          <KV k="Pin 2" v="TX+ (TRIHAT W5500 TPOUT+)"/>
          <KV k="Pin 3" v="TX− (TRIHAT W5500 TPOUT−)"/>
          <KV k="Pin 4" v="RX+ (TRIHAT W5500 TPIN+)"/>
          <KV k="Pin 5" v="RX− (TRIHAT W5500 TPIN−)"/>
          <KV k="Pin 6" v="N/C (no bus power — each board self-powered)"/>
          <KV k="Magnetics" v="HX1188NL on both boards — no external xfmr"/>
          <KV k="Speed" v="100Mbps full duplex · auto-MDIX (W5500 hw)"/>
          <KV k="MAVLink port" v="UDP 14550 · Pico → CM4 attitude/status"/>
          <KV k="Log stream" v="UDP 14551 · Pico → CM4 sensor CSV 50Hz"/>
          <KV k="Config" v="TCP 8080 · CM4 → Pico parameter set"/>
          <KV k="IP scheme" v="Static: Pico 192.168.10.1 · CM4 192.168.10.2"/>
          <Note c={C.purple} ch="Auto-MDIX handled in W5500 hardware — no crossover cable needed. Route along port keel spine, cable-tie every 40mm, no contact with CF spar."/>
        </div>
        <div>
          <SH t="CAN FD · TRIHAT-1 J2 ↔ COMPHAT-1 J1" mt={0} c={C.orange}/>
          <KV k="Connector" v="JST-GH 1.25mm 4-pin (both ends)"/>
          <KV k="Cable" v="Twisted pair CANH/CANL · 2× power · 120mm"/>
          <KV k="Pin 1" v="GND"/>
          <KV k="Pin 2" v="+5V bus power (from TRIHAT-1 BEC rail)"/>
          <KV k="Pin 3" v="CANH"/>
          <KV k="Pin 4" v="CANL"/>
          <KV k="Standard" v="ISO 11898-1:2015 CAN FD"/>
          <KV k="Data rate" v="1Mbps nominal / 4Mbps FD data phase"/>
          <KV k="Transceivers" v="MCP2562FD on both boards · 5V bus / 3.3V logic"/>
          <KV k="Termination" v="120Ω at TRIHAT-1 only (bridge populated) · none at COMPHAT"/>
          <KV k="Pico→CM4" v="AHRS quaternion · RPM · sensor health · arm events"/>
          <KV k="CM4→Pico" v="Mission commands · mode · param updates"/>
          <KV k="Protocol" v="DroneCAN / UAVCANv1 message framing"/>
          <KV k="Routing" v="Starboard keel · ≥20mm from Ethernet cable"/>
          <Warn ch="Twist CANH/CANL at ≥25 twists/metre before inserting into JST-GH. TRIHAT-1 120Ω termination bridge MUST be soldered. COMPHAT-1 bridge must NOT be populated."/>
        </div>
      </div>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════
// 6 · BOM
// ══════════════════════════════════════════════════════════════
const BOM=[
  {cat:"Propulsion",  qty:2, ref:"EDF-65",  part:"65mm EDF + 2700KV BLDC",          desc:"12-blade · 800g thrust @ 5S · 28A",        est:"$22ea"},
  {cat:"Propulsion",  qty:2, ref:"ESC-35",  part:"35A BLHeli32 ESC",                 desc:"DSHOT300 · 2–6S · BLHeli32",               est:"$18ea"},
  {cat:"Propulsion",  qty:1, ref:"EDF-35",  part:"35mm EDF + 4500KV BLDC",           desc:"7-blade · 140g thrust @ 5S · 12A",         est:"$14"},
  {cat:"Propulsion",  qty:1, ref:"ESC-25",  part:"25A BLHeli32 ESC",                 desc:"DSHOT300 · fwd fan ESC",                   est:"$12"},
  {cat:"Propulsion",  qty:2, ref:"SRV-T",   part:"MG90S digital servo",              desc:"Metal gear · 1.8kg·cm · nacelle tilt",     est:"$4ea"},
  {cat:"Flt Ctrl",    qty:1, ref:"PICO2",   part:"Raspberry Pi Pico 2",              desc:"RP2350 · 264KB · 4MB flash",               est:"$5"},
  {cat:"Flt Ctrl",    qty:1, ref:"TH1",     part:"TRIHAT-1 (custom 4-layer PCB)",    desc:"IMU+Baro+GPS+CAN+ETH+TPM+FPV hat 65×48mm",est:"$75"},
  {cat:"Flt Ctrl",    qty:1, ref:"AIRS",    part:"MS4525DO airspeed sensor",         desc:"I²C · ±1PSI · 0–80m/s",                  est:"$10"},
  {cat:"Flt Ctrl",    qty:1, ref:"PITOT",   part:"CF pitot 3mm + silicone tubing",   desc:"80mm tube · 2×80mm 2mm ID leads",         est:"$4"},
  {cat:"Companion",   qty:1, ref:"CM4",     part:"CM4 Lite 4GB WiFi",                desc:"BCM2711 · 4×A72 · 4GB LPDDR4X · 802.11ac",est:"$55"},
  {cat:"Companion",   qty:1, ref:"CAR1",    part:"CM4-CARRIER-1 (custom PCB)",       desc:"65×40mm · DF40 sockets · μSD · WiFi ant", est:"$22"},
  {cat:"Companion",   qty:1, ref:"CH1",     part:"COMPHAT-1 (custom PCB)",           desc:"65×48mm · CAN+ETH+TPM+μSD+SiK+RCRS",     est:"$60"},
  {cat:"Companion",   qty:1, ref:"SIK",     part:"SiK 915MHz telemetry air unit",    desc:"MAVLink 2.0 · 100mW · UART",              est:"$18"},
  {cat:"Companion",   qty:1, ref:"RCRS",    part:"49MHz RCRS transceiver module",    desc:"TDDS · 6-ch · 10mW EIRP",                 est:"$16"},
  {cat:"Nav Lights",  qty:6, ref:"WS2812",  part:"WS2812C-2020 RGB LED",             desc:"5V · 2×2mm · addressable · PIO driven",   est:"$0.50ea"},
  {cat:"Nav Lights",  qty:6, ref:"LENS",    part:"Clear PETG LED lens diffusers",    desc:"3D printed · flush mount",                 est:"<$1 filament"},
  {cat:"Payload",     qty:1, ref:"SRV-R",   part:"SG90 micro servo (release)",       desc:"Latch release · spring-return closed",     est:"$3"},
  {cat:"Payload",     qty:1, ref:"WINCH",   part:"N20 6V 100:1 gearmotor",           desc:"Winch drive",                              est:"$5"},
  {cat:"Payload",     qty:1, ref:"DRV",     part:"DRV8833 H-bridge module",          desc:"Dual 1.5A · winch control",               est:"$3"},
  {cat:"Payload",     qty:1, ref:"SPOOL",   part:"Phenolic spool 18mm + Dyneema 5m", desc:"Dyneema SK75 0.8mm · 40kg break",         est:"$6"},
  {cat:"Power",       qty:1, ref:"BAT",     part:"★ 5S 2800mAh 45C LiPo",           desc:"Tattu/GNB · 18.5V · XT60 · T/W 2.04",    est:"$38"},
  {cat:"Power",       qty:1, ref:"BEC",     part:"5V 3A switching BEC",              desc:"Low-noise · CM4+Pico+radios+servos",       est:"$5"},
  {cat:"Power",       qty:1, ref:"PDIST",   part:"XT60 power distribution board",    desc:"4× XT30 out · 12AWG mains",               est:"$8"},
  {cat:"Airframe",    qty:1, ref:"HULL",    part:"Serenity hull PETG prints (11 pcs)",desc:"~144g · 8% gyroid · thin-wall shell",    est:"$18 filament"},
  {cat:"Airframe",    qty:2, ref:"NAC",     part:"65mm nacelle pods CF-PETG",        desc:"72mm OD · pivot · bearing seat",          est:"$6 filament"},
  {cat:"Airframe",    qty:1, ref:"BELL",    part:"35mm engine bell PETG fairing",    desc:"Serenity aft bell · 3 walls",             est:"$4 filament"},
  {cat:"Airframe",    qty:1, ref:"KEEL",    part:"CF keel 6×3mm × 380mm",           desc:"Dorsal structural spine",                 est:"$6"},
  {cat:"Airframe",    qty:2, ref:"SPAR",    part:"CF tube 12mm OD × 300mm",         desc:"Outrigger wing spars",                    est:"$8ea"},
  {cat:"Airframe",    qty:4, ref:"SKID",    part:"TPU 95A skid feet",               desc:"Crash-absorbing pads",                    est:"$2 filament"},
  {cat:"Airframe",    qty:1, ref:"HW",      part:"M2/M2.5/M3 hardware assortment",  desc:"Standoffs · screws · heat-set inserts",   est:"$8"},
  {cat:"Wiring",      qty:1, ref:"JSTKIT",  part:"JST-GH 1.25mm kit",               desc:"4+6pin assorted · crimp tool · pre-made", est:"$14"},
  {cat:"Wiring",      qty:1, ref:"ETH-C",   part:"6-pin JST-GH Ethernet cable 150mm",desc:"Twisted pairs · TRIHAT-1 ↔ COMPHAT-1",  est:"$4"},
  {cat:"Wiring",      qty:1, ref:"CAN-C",   part:"4-pin JST-GH CAN FD cable 120mm", desc:"Twisted CANH/CANL · TRIHAT-1 ↔ COMPHAT-1",est:"$3"},
  {cat:"Wiring",      qty:1, ref:"WIRE",    part:"Silicone wire assortment",         desc:"12AWG power · 22AWG signal · 28AWG data", est:"$12"},
  {cat:"Wiring",      qty:1, ref:"XT60P",   part:"XT60 connector pair",              desc:"Battery to power board",                  est:"$2"},
];
const CAT_COL={Propulsion:C.orange,"Flt Ctrl":C.accent,Companion:C.green,"Nav Lights":C.yellow,
  Payload:C.pink,Power:C.yellow,Airframe:C.teal,Wiring:C.purple};
const CATS=[...new Set(BOM.map(b=>b.cat))];

function BomTab(){
  const [cf,setCf]=useState("All");
  const rows=cf==="All"?BOM:BOM.filter(b=>b.cat===cf);
  return(
    <div>
      <div style={{display:"flex",gap:5,flexWrap:"wrap",marginBottom:12}}>
        {["All",...CATS].map(c=>(
          <button key={c} onClick={()=>setCf(c)} style={{
            background:cf===c?`${CAT_COL[c]||C.accent}20`:"transparent",
            border:`1px solid ${cf===c?CAT_COL[c]||C.accent:"rgba(0,229,255,0.14)"}`,
            color:cf===c?CAT_COL[c]||C.accent:C.dimmer,
            padding:"3px 10px",fontFamily:M,fontSize:9,cursor:"pointer",borderRadius:2}}>{c}</button>
        ))}
      </div>
      <div style={{overflowX:"auto"}}>
        <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
          <TH cols={["CAT","QTY","REF","COMPONENT","DESCRIPTION","~USD"]}/>
          <tbody>{rows.map((b,i)=>(
            <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.02)":"transparent",verticalAlign:"top"}}>
              <td style={{padding:"5px 8px"}}><span style={{color:CAT_COL[b.cat]||C.dim,border:`1px solid ${CAT_COL[b.cat]||C.dim}40`,padding:"1px 5px",borderRadius:2,fontSize:9,whiteSpace:"nowrap"}}>{b.cat}</span></td>
              <td style={{padding:"5px 8px",color:C.accent,fontWeight:"bold",textAlign:"center"}}>{b.qty}</td>
              <td style={{padding:"5px 8px",color:C.yellow,fontSize:9,whiteSpace:"nowrap"}}>{b.ref}</td>
              <td style={{padding:"5px 8px",color:C.text,whiteSpace:"nowrap"}}>{b.part}</td>
              <td style={{padding:"5px 8px",color:C.dim,fontSize:9,lineHeight:1.5}}>{b.desc}</td>
              <td style={{padding:"5px 8px",color:C.green,fontWeight:"bold",whiteSpace:"nowrap"}}>{b.est}</td>
            </tr>
          ))}</tbody>
          {cf==="All"&&(<tfoot><tr style={{borderTop:`1px solid ${C.border}`}}>
            <td colSpan={5} style={{padding:"8px 8px",color:C.accent,textAlign:"right",fontSize:11}}>TOTAL ESTIMATED</td>
            <td style={{padding:"8px 8px",color:C.yellow,fontSize:16,fontWeight:"bold"}}>$580–660</td>
          </tr></tfoot>)}
        </table>
      </div>
      <Note c={C.dim} ch="Custom PCBs (TRIHAT-1, CM4-CARRIER-1, COMPHAT-1) include 5-piece JLCPCB + LCSC components. Prices approx. AliExpress/GetFPV/Mouser 2024–2025. Filament at $25/kg PETG, $35/kg CF-PETG, $30/kg TPU."/>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════
// 7 · SBOM
// ══════════════════════════════════════════════════════════════
const SBOM=[
  {sys:"Pico 2",layer:"Core",      comp:"Pico SDK 2.x",              ver:"≥2.0",  lic:"BSD-3",   role:"RP2350 HAL · PIO · DMA · multicore"},
  {sys:"Pico 2",layer:"AHRS",      comp:"Mahony AHRS (port)",        ver:"custom",lic:"Apache-2",role:"Complementary filter gyro+accel → quaternion"},
  {sys:"Pico 2",layer:"Control",   comp:"Custom PID cascade",        ver:"v1.0",  lic:"Propr.",  role:"Rate/attitude/position PID · 500Hz"},
  {sys:"Pico 2",layer:"Protocol",  comp:"MAVLink 2.0 C lib",         ver:"2.0",   lic:"MIT",     role:"Encode/decode MAVLink over UART1 + W5500 UDP"},
  {sys:"Pico 2",layer:"Driver",    comp:"ICM-42688-P SPI driver",    ver:"custom",lic:"BSD-3",   role:"6-DOF IMU · SPI0 24MHz"},
  {sys:"Pico 2",layer:"Driver",    comp:"BMP388 I²C driver",         ver:"custom",lic:"BSD-3",   role:"Barometer · I²C1"},
  {sys:"Pico 2",layer:"Driver",    comp:"MS4525DO airspeed driver",  ver:"custom",lic:"BSD-3",   role:"Differential pressure → IAS · I²C1"},
  {sys:"Pico 2",layer:"Driver",    comp:"u-blox UBX parser",         ver:"custom",lic:"BSD-3",   role:"GPS binary parser · UART0"},
  {sys:"Pico 2",layer:"Driver",    comp:"MCP2518FD SPI driver",      ver:"custom",lic:"BSD-3",   role:"CAN FD controller · SPI0"},
  {sys:"Pico 2",layer:"Driver",    comp:"W5500 ioLibrary",           ver:"3.x",   lic:"BSD-3",   role:"Ethernet TCP/IP offload · SPI1"},
  {sys:"Pico 2",layer:"Driver",    comp:"SLB9670 TPM2 driver",       ver:"custom",lic:"BSD-3",   role:"SPI-TPM 2.0 · firmware attestation"},
  {sys:"Pico 2",layer:"Driver",    comp:"WS2812 PIO driver",         ver:"SDK",   lic:"BSD-3",   role:"RGB nav-light chain · GP26 PIO0"},
  {sys:"Pico 2",layer:"Driver",    comp:"DSHOT300 PIO driver",       ver:"custom",lic:"MIT",     role:"Bidirectional DSHOT · 3× ESC · PIO"},
  {sys:"Pico 2",layer:"Algorithm", comp:"TDDS channel selector",     ver:"v1.0",  lic:"Propr.",  role:"49MHz RCRS TDDS · SNR scan → clearest channel"},
  {sys:"CM4",   layer:"OS",        comp:"RPi OS Lite 64-bit",        ver:"bookworm",lic:"Mixed GPL","role":"Debian Linux headless · kernel 6.6+"},
  {sys:"CM4",   layer:"Middleware",comp:"mavlink-router",            ver:"≥3.0",  lic:"Apache-2",role:"MAVLink router: Pico↔SiK↔GCS↔MAVSDK"},
  {sys:"CM4",   layer:"Middleware",comp:"MAVSDK-Python",             ver:"≥2.0",  lic:"BSD-3",   role:"High-level drone API: missions, params, telem"},
  {sys:"CM4",   layer:"Middleware",comp:"python-can",                ver:"≥4.0",  lic:"LGPL-3",  role:"CAN bus interface → MCP2518FD socketcan"},
  {sys:"CM4",   layer:"Middleware",comp:"dronecan (Python)",         ver:"≥1.0",  lic:"MIT",     role:"DroneCAN/UAVCANv1 protocol stack"},
  {sys:"CM4",   layer:"Middleware",comp:"pymavlink",                 ver:"≥2.4",  lic:"LGPL",    role:"MAVLink serialisation + black-box logging"},
  {sys:"CM4",   layer:"Security",  comp:"tpm2-tools",               ver:"≥5.0",  lic:"BSD-2",   role:"TPM2.0 CLI key provisioning + attestation"},
  {sys:"CM4",   layer:"Security",  comp:"tpm2-tss",                 ver:"≥4.0",  lic:"BSD-2",   role:"TPM Software Stack: FAPI · ESAPI · TCTI"},
  {sys:"CM4",   layer:"Logging",   comp:"Custom flight logger",      ver:"v1.0",  lic:"Propr.",  role:"MAVLink+sensor → binary log on COMPHAT μSD"},
  {sys:"CM4",   layer:"Driver",    comp:"spi-bcm2835 kernel driver", ver:"kernel",lic:"GPL-2",   role:"SPI for MCP2518FD · W5500 · TPM"},
  {sys:"CM4",   layer:"Comms",     comp:"SiK firmware (air unit)",   ver:"2.x",   lic:"GPL-3",   role:"915MHz MAVLink radio firmware"},
  {sys:"GCS",   layer:"App",       comp:"QGroundControl",            ver:"≥4.3",  lic:"GPL-3",   role:"Flight planning · telemetry · params"},
  {sys:"GCS",   layer:"App",       comp:"Mission Planner (alt)",     ver:"≥1.3",  lic:"GPL-3",   role:"Windows/Linux GCS alternative"},
  {sys:"GCS",   layer:"Library",   comp:"pymavlink (GCS side)",      ver:"≥2.4",  lic:"LGPL",    role:"Log analysis · ground-side scripts"},
];
const SBOM_SYS=[...new Set(SBOM.map(s=>s.sys))];
const LAYER_COL={Core:C.accent,AHRS:C.teal,Control:C.orange,Protocol:C.orange,
  Driver:C.teal,Algorithm:C.pink,OS:C.green,Middleware:C.purple,Security:C.yellow,
  Logging:C.lime,Comms:C.accent,App:C.green,Library:C.purple};

function SbomTab(){
  const [sf,setSf]=useState("All");
  const rows=sf==="All"?SBOM:SBOM.filter(s=>s.sys===sf);
  return(
    <div>
      <div style={{display:"flex",gap:5,flexWrap:"wrap",marginBottom:12}}>
        {["All",...SBOM_SYS].map(s=>(
          <button key={s} onClick={()=>setSf(s)} style={{
            background:sf===s?"rgba(0,229,255,0.09)":"transparent",
            border:`1px solid ${sf===s?C.accent:"rgba(0,229,255,0.14)"}`,
            color:sf===s?C.accent:C.dimmer,
            padding:"3px 10px",fontFamily:M,fontSize:9,cursor:"pointer",borderRadius:2}}>{s}</button>
        ))}
      </div>
      <div style={{overflowX:"auto"}}>
        <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
          <TH cols={["SYSTEM","LAYER","COMPONENT","VERSION","LICENSE","ROLE"]}/>
          <tbody>{rows.map((s,i)=>(
            <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.02)":"transparent",verticalAlign:"top"}}>
              <td style={{padding:"5px 8px",color:s.sys==="Pico 2"?C.accent:s.sys==="CM4"?C.green:C.orange,fontWeight:"bold",whiteSpace:"nowrap",fontSize:9}}>{s.sys}</td>
              <td style={{padding:"5px 8px"}}><span style={{color:LAYER_COL[s.layer]||C.dim,border:`1px solid ${LAYER_COL[s.layer]||C.dim}40`,padding:"1px 5px",borderRadius:2,fontSize:8,whiteSpace:"nowrap"}}>{s.layer}</span></td>
              <td style={{padding:"5px 8px",color:C.text,whiteSpace:"nowrap"}}>{s.comp}</td>
              <td style={{padding:"5px 8px",color:C.dimmer,whiteSpace:"nowrap",fontSize:9}}>{s.ver}</td>
              <td style={{padding:"5px 8px",color:C.yellow,whiteSpace:"nowrap",fontSize:9}}>{s.lic}</td>
              <td style={{padding:"5px 8px",color:C.dim,fontSize:9,lineHeight:1.5}}>{s.role}</td>
            </tr>
          ))}</tbody>
        </table>
      </div>
      <Note c={C.accent} ch="GPL-3 components (QGroundControl, SiK firmware) must remain open-source if redistributed. Proprietary Pico 2 firmware uses only BSD/MIT dependencies — no GPL linkage. TPM attestation keys are device-unique, provisioned at final assembly using tpm2-tools."/>
    </div>
  );
}

// ══════════════════════════════════════════════════════════════
// APP
// ══════════════════════════════════════════════════════════════
const TABS=["Overview","Battery","Nav Lights","Antenna","Wiring","BOM","SBOM"];

_ODFontLoader();
export default function App(){
  const [tab,setTab]=useState("Overview");
  return(
    <div style={{minHeight:"100vh",background:C.bg,color:C.text,fontFamily:M}}>
      <Grid/>
      <div style={{position:"relative",zIndex:1,borderBottom:`1px solid ${C.border}`,padding:"18px 28px 14px"}}>
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",flexWrap:"wrap",gap:12}}>
          <div>
            <div style={{color:"rgba(0,229,255,0.28)",fontSize:9,letterSpacing:"0.2em",marginBottom:4}}>SERENITY TILTROTOR · MASTER SPECIFICATION · REV C</div>
            <h1 style={{margin:0,fontSize:19,fontWeight:"normal",color:"#fff",letterSpacing:"0.07em"}}>SERENITY DRONE — FULL SYSTEM SPEC</h1>
            <div style={{color:"rgba(0,229,255,0.48)",fontSize:10,marginTop:4}}>65mm + 35mm EDF · 5S 2800mAh · Nav Lights · Antenna · ETH/CAN Wiring · BOM · SBOM</div>
          </div>
          <div style={{textAlign:"right",fontFamily:M}}>
            <div style={{color:C.yellow,fontSize:13,fontWeight:"bold"}}>AUW {REC.auw}g</div>
            <div style={{color:C.green,fontSize:12,marginTop:2,fontWeight:"bold"}}>T/W {REC.tw}:1</div>
            <div style={{color:C.dimmer,fontSize:9,marginTop:2}}>{REC.hMin}min hover · {REC.cMin}min cruise</div>
          </div>
        </div>
        <div style={{display:"flex",gap:2,marginTop:14,flexWrap:"wrap"}}>
          {TABS.map(t=>(
            <button key={t} onClick={()=>setTab(t)} style={{
              background:tab===t?"rgba(0,229,255,0.09)":"transparent",
              border:`1px solid ${tab===t?C.accent:"rgba(0,229,255,0.13)"}`,
              color:tab===t?C.accent:C.dimmer,padding:"5px 13px",fontFamily:M,
              fontSize:10,cursor:"pointer",letterSpacing:"0.07em",transition:"all 0.12s"}}>{t}</button>
          ))}
        </div>
      </div>
      <div style={{position:"relative",zIndex:1,padding:"22px 28px",maxWidth:1060,margin:"0 auto"}}>
        {tab==="Overview"   && <OverviewTab/>}
        {tab==="Battery"    && <BatteryTab/>}
        {tab==="Nav Lights" && <NavLightsTab/>}
        {tab==="Antenna"    && <AntennaTab/>}
        {tab==="Wiring"     && <WiringTab/>}
        {tab==="BOM"        && <BomTab/>}
        {tab==="SBOM"       && <SbomTab/>}
      </div>
      <div style={{position:"relative",zIndex:1,borderTop:`1px solid ${C.border}`,
        padding:"10px 28px",display:"flex",justifyContent:"space-between",flexWrap:"wrap",gap:6}}>
        <span style={{color:"rgba(0,229,255,0.16)",fontSize:8,letterSpacing:"0.12em"}}>SERENITY TILTROTOR · REV C · HULL: PETER FARELL PRINTABLES.COM/548545</span>
        <span style={{color:"rgba(0,229,255,0.16)",fontSize:8}}>REFERENCE DESIGN · VERIFY BEFORE FLIGHT</span>
      </div>
    </div>
  );
}
