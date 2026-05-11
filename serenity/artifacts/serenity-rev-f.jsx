// ── OpenDyslexic font loader ─────────────────────────────────
function _ODFontLoader(){
  if(typeof document==="undefined") return null;
  if(document.getElementById("od-font-link")) return null;
  const l=document.createElement("link");
  l.id="od-font-link";l.rel="stylesheet";
  l.href="https://fonts.cdnfonts.com/css/opendyslexic";
  document.head.appendChild(l);
  const s=document.createElement("style");
  s.id="od-font-style";
  s.textContent=`*,*::before,*::after{font-family:'OpenDyslexic','OpenDyslexicMono',sans-serif!important}
    @media print{body{background:#fff!important;color:#111!important}}`;
  document.head.appendChild(s);
  return null;
}
import { useState } from "react";
_ODFontLoader();

const M="'OpenDyslexic Mono','OpenDyslexicMono',monospace";
const C={bg:"#060810",border:"rgba(0,229,255,0.11)",accent:"#00e5ff",
  orange:"#ff6b35",yellow:"#ffe600",purple:"#c084fc",green:"#4ade80",
  teal:"#2dd4bf",red:"#f87171",lime:"#a3e635",gold:"#fbbf24",pink:"#f472b6",
  text:"rgba(255,255,255,0.90)",dim:"rgba(255,255,255,0.90)",dimmer:"rgba(255,255,255,0.82)"};

// Canon: QMx Blueprints (Mandel/Earls 2007) 269ft x 170ft x 79ft => 457.2mm hull
// 1/3-datum pylon rule: datum=48.2mm, pod centre=103.2mm (biased outward)
// 100mm EDF = minimum meeting T/W>=2.0 empty AND cargo at 18" scale with 8-node avionics
const SP={
  hull_mm:457.2,hull_in:"18.000",sf:1.2526,
  tip_span_mm:288.9,tip_span_in:"11.375",height_mm:134.3,height_in:"5.286",
  max_fuse_mm:82.7,neck_mm:22.5,
  datum_mm:48.2,inboard_mm:5.0,
  edf_id:100,edf_od:120,pod_ctr_mm:103.2,
  c_to_c_mm:206.3,c_to_c_in:"8.123",
  tip_tot_mm:326.3,tip_tot_in:"12.847",arm_stub_mm:61.8,
  thr_each:2200,thr_total:4400,
  base_no_bat:1417,bat_e:420,bat_c:271,payload:250,
  auw_e:1837,auw_c:1938,tw_e:2.39,tw_c:2.27,max_pl:512,max_pl_oz:18.1,
  end_e:8.0,end_c:5.1,
  pos:{gps:75.2,n1:93.9,n2:162.8,n3:244.3,n4:331.9,
       cg:190.4,pay:206.7,bat:244.3,sik:298.1,rcrs:363.3,
       nac0:169.1,nacC:205.4,bell:413.4}
};

function Grid(){return(<svg style={{position:"fixed",inset:0,width:"100%",height:"100%",pointerEvents:"none",zIndex:0}}><defs><pattern id="g" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0L0 0 0 20" fill="none" stroke="rgba(0,229,255,0.035)" strokeWidth={0.5}/></pattern><pattern id="lg" width="100" height="100" patternUnits="userSpaceOnUse"><rect width="100" height="100" fill="url(#g)"/><path d="M100 0L0 0 0 100" fill="none" stroke="rgba(0,229,255,0.065)" strokeWidth={1}/></pattern></defs><rect width="100%" height="100%" fill="url(#lg)"/></svg>);}
const SH=({t,c=C.accent,mt=22})=>(<div style={{display:"flex",alignItems:"center",gap:10,marginBottom:14,marginTop:mt}}><div style={{width:3,height:17,background:c}}/><span style={{color:c,fontFamily:M,fontSize:13,letterSpacing:"0.13em",textTransform:"uppercase"}}>{t}</span></div>);
const KV=({k,v,vc=C.text})=>(<div style={{display:"flex",justifyContent:"space-between",padding:"5px 0",borderBottom:"1px solid rgba(0,229,255,0.07)"}}><span style={{color:C.dim,fontFamily:M,fontSize:11}}>{k}</span><span style={{color:vc,fontFamily:M,fontSize:11}}>{v}</span></div>);
const Note=({c=C.dim,ch})=>(<div style={{marginTop:8,color:c,fontFamily:M,fontSize:10,lineHeight:1.85,padding:"8px 12px",borderLeft:`2px solid ${c}55`,background:`${c}07`,borderRadius:3}}>{ch}</div>);
const Good=({ch})=>(<div style={{marginTop:8,color:C.green,fontFamily:M,fontSize:10,lineHeight:1.8,padding:"7px 12px",borderLeft:`2px solid ${C.green}`,background:"rgba(74,222,128,0.05)",borderRadius:3}}>{"✓ "}{ch}</div>);
const Warn=({ch})=>(<div style={{marginTop:8,color:C.yellow,fontFamily:M,fontSize:10,lineHeight:1.8,padding:"7px 12px",borderLeft:`2px solid ${C.yellow}`,background:"rgba(255,230,0,0.05)",borderRadius:3}}>{"⚠ "}{ch}</div>);
function TH({cols}){return(<thead><tr>{cols.map(h=>(<th key={h} style={{padding:"6px 9px",borderBottom:`1px solid ${C.border}`,color:C.accent,textAlign:"left",fontWeight:"normal",fontSize:10,opacity:.85}}>{h}</th>))}</tr></thead>);}

function OverviewTab(){
  const cards=[
    {l:"Hull",v:`${SP.hull_mm}mm (${SP.hull_in}")`,s:"18\" canonical scale  SF="+SP.sf+"x",c:C.accent},
    {l:"Total thrust",v:`${SP.thr_total}g (${(SP.thr_total/453.6).toFixed(1)}lb)`,s:"2x100mm EDF @ 5S",c:C.orange},
    {l:"T/W empty",v:`${SP.tw_e}:1`,s:`AUW ${SP.auw_e}g`,c:C.green},
    {l:"T/W cargo",v:`${SP.tw_c}:1`,s:`250g payload · ${SP.auw_c}g AUW`,c:C.green},
    {l:"Max payload",v:`${SP.max_pl}g (${SP.max_pl_oz}oz)`,s:"at T/W=2.0",c:C.lime},
    {l:"Hover endurance",v:`${SP.end_e} min empty`,s:`${SP.end_c} min cargo 250g`,c:C.teal},
  ];
  return(<div>
    <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:14,marginBottom:20}}>
      {cards.map((b,i)=>(<div key={i} style={{padding:"12px",border:`1px solid ${b.c}44`,background:`${b.c}08`,borderRadius:4}}>
        <div style={{color:C.dim,fontFamily:M,fontSize:9,marginBottom:4}}>{b.l}</div>
        <div style={{color:b.c,fontFamily:M,fontSize:16,fontWeight:"bold"}}>{b.v}</div>
        <div style={{color:C.dimmer,fontFamily:M,fontSize:8,marginTop:3}}>{b.s}</div>
      </div>))}
    </div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="Canonical Proportions" mt={0}/>
        <KV k="Hull" v={`${SP.hull_mm}mm (${SP.hull_in}")`} vc={C.accent}/>
        <KV k="Source" v="QMx Blueprints — Mandel/Earls 2007" vc={C.lime}/>
        <KV k="Ratio" v="269ft x 170ft beam x 79ft height"/>
        <KV k="Tip-to-tip canonical" v={`${SP.tip_span_mm}mm (${SP.tip_span_in}")`} vc={C.teal}/>
        <KV k="Landed height" v={`${SP.height_mm}mm (${SP.height_in}")`}/>
        <KV k="Max fuselage width" v={`${SP.max_fuse_mm}mm`}/>
        <KV k="Neck width" v={`${SP.neck_mm}mm (0.888")`}/>
        <SH t="1/3-Datum Pylon Rule"/>
        <KV k="Datum from CL" v={`${SP.datum_mm}mm (1/3 half-span)`} vc={C.lime}/>
        <KV k="Inboard clearance" v={`${SP.inboard_mm}mm min datum->pod edge`}/>
        <KV k="EDF selected" v="100mm ID / 120mm OD" vc={C.orange}/>
        <KV k="Pod centre from CL" v={`${SP.pod_ctr_mm}mm`}/>
        <KV k="C-to-C" v={`${SP.c_to_c_mm}mm (${SP.c_to_c_in}")`} vc={C.orange}/>
        <KV k="Tip-to-tip actual" v={`${SP.tip_tot_mm}mm (${SP.tip_tot_in}")`}/>
        <KV k="EDF overhang" v={`+${(SP.tip_tot_mm-SP.tip_span_mm).toFixed(1)}mm over canonical`}/>
        <KV k="Arm stub" v={`${SP.arm_stub_mm}mm hull edge to pod centre`}/>
      </div>
      <div>
        <SH t="Weight" mt={0}/>
        <KV k="Base (no battery)" v={`${SP.base_no_bat}g`}/>
        <KV k="Battery empty rec" v={`${SP.bat_e}g (5S 4500mAh)`}/>
        <KV k="AUW empty" v={`${SP.auw_e}g (${(SP.auw_e/28.35).toFixed(1)}oz)`} vc={C.green}/>
        <KV k="T/W empty" v={`${SP.tw_e}:1`} vc={C.green}/>
        <KV k="Battery cargo rec" v={`${SP.bat_c}g (5S 2800mAh)`}/>
        <KV k="Payload" v={`${SP.payload}g recommended`}/>
        <KV k="AUW cargo" v={`${SP.auw_c}g (${(SP.auw_c/28.35).toFixed(1)}oz)`} vc={C.green}/>
        <KV k="T/W cargo" v={`${SP.tw_c}:1`} vc={C.green}/>
        <KV k="Max payload (T/W=2.0)" v={`${SP.max_pl}g (${SP.max_pl_oz}oz)`} vc={C.lime}/>
        <Good ch={`T/W >= 2.0 on empty AND cargo missions. 100mm EDF is the minimum size meeting this at 18" with 8-node avionics.`}/>
        <Note c={C.teal} ch={`Nacelles expand OUTWARD from 1/3-datum (${SP.datum_mm}mm): inboard pod edge at ${(SP.pod_ctr_mm-60).toFixed(1)}mm (only ${SP.inboard_mm}mm inboard of datum), outboard tip at ${(SP.pod_ctr_mm+60).toFixed(1)}mm. Visual proportions remain canonical.`}/>
      </div>
    </div>
  </div>);
}

function ElectronicsTab(){
  const rows=[
    ["GPS patch (u-blox M10Q)",SP.pos.gps,"2.96\"","Cockpit roof",C.green],
    ["Node-1: SENSORHAT + CARRIER-2 + COMMS-HAT-SWITCH",SP.pos.n1,"3.70\"","Primary FC + Murex ETH switch + 1553 BC",C.purple],
    ["Node-2: SENSORHAT + CARRIER-2 + MICROHAT",SP.pos.n2,"6.41\"","Nav/IMU secondary",C.purple],
    ["Node-3: SENSORHAT + CARRIER-2 + MICROHAT",SP.pos.n3,"9.62\"","Payload/actuator control",C.purple],
    ["Node-4: SENSORHAT + CARRIER-2 + MICROHAT",SP.pos.n4,"13.07\"","Aft telemetry/logging",C.purple],
    ["CG target",SP.pos.cg,"7.50\"","Aero neutral — battery trimmed here",C.green],
    ["Payload bay centre",SP.pos.pay,"8.14\"","Belly cargo bay / SG90 latch door",C.pink],
    ["Battery centroid (nominal)",SP.pos.bat,"9.62\"","Rail ±28mm for CG trim",C.yellow],
    ["SiK 915MHz belly SMA",SP.pos.sik,"11.74\"","Ground-facing telemetry",C.orange],
    ["49MHz RCRS dorsal fin",SP.pos.rcrs,"14.30\"","TDDS RC uplink coil in dorsal fin",C.pink],
    ["Nacelle arm root",SP.pos.nac0,"6.66\"","Pylon start at hull",C.orange],
    ["Nacelle pivot / tilt axis",SP.pos.nacC,"8.09\"","MG90S tilt servo centre",C.orange],
    ["Engine bell centre (40mm EDF)",SP.pos.bell,"16.27\"","Variable-area gear nozzle",C.yellow],
  ];
  return(<div>
    <Note c={C.accent} ch={`All positions × SF=1.2526 from 365mm build. CG target ${SP.pos.cg}mm from nose. Battery rail at ${SP.pos.bat}mm ±28mm for trim.`}/>
    <div style={{overflowX:"auto",marginTop:12}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["COMPONENT","mm","INCHES","NOTES"]}/>
        <tbody>{rows.map(([name,pos,inch,note,col],i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.02)":"transparent",verticalAlign:"top"}}>
            <td style={{padding:"5px 9px",color:col}}>{name}</td>
            <td style={{padding:"5px 9px",color:C.accent,whiteSpace:"nowrap"}}>{pos.toFixed(1)}</td>
            <td style={{padding:"5px 9px",color:C.dimmer,whiteSpace:"nowrap"}}>{inch}</td>
            <td style={{padding:"5px 9px",color:C.dim,fontSize:9}}>{note}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
  </div>);
}

function AirframeTab(){
  const prof=[
    [0,0],[10,6.3],[30.1,13.8],[58.9,21.3],[76.4,30.1],[100.2,36.3],
    [139,40.1],[186.6,41.3],[228,41.3],[263,40.1],[288.1,35.1],
    [313.2,26.3],[330.7,18.8],[339.5,11.3],[348.2,15],[369.5,22.5],
    [390.8,28.8],[419.6,30.1],[442.2,26.3],[457.2,21.3]
  ];
  return(<div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="Hull" mt={0}/>
        <KV k="Basis" v="Peter Farell CC BY 4.0" vc={C.lime}/>
        <KV k="Scale" v={`SF=${SP.sf}x from 365mm (14.37") original`}/>
        <KV k="Length" v={`${SP.hull_mm}mm (${SP.hull_in}")`} vc={C.accent}/>
        <KV k="Max fuselage" v={`${SP.max_fuse_mm}mm at 186.6mm station`}/>
        <KV k="Neck" v={`${SP.neck_mm}mm at 339.5mm station (73.3% from nose)`}/>
        <KV k="Cockpit dome peak" v="64mm above CL at 58.9mm from nose"/>
        <KV k="Cannon source" v="269ft x 170ft x 79ft (QMx 2007)"/>
        <SH t="Nacelle Geometry"/>
        <KV k="Pylon datum (1/3 half-span)" v={`${SP.datum_mm}mm from CL`} vc={C.lime}/>
        <KV k="Inboard gap" v={`${SP.inboard_mm}mm from datum to inboard pod edge`}/>
        <KV k="Pod centre from CL" v={`${SP.pod_ctr_mm}mm (${(SP.pod_ctr_mm-SP.datum_mm).toFixed(1)}mm outboard of datum)`}/>
        <KV k="C-to-C" v={`${SP.c_to_c_mm}mm (${SP.c_to_c_in}")`} vc={C.orange}/>
        <KV k="Pod OD" v={`${SP.edf_od}mm (100mm EDF, 3mm wall each side)`}/>
        <KV k="Arm root" v={`${SP.pos.nac0.toFixed(1)}mm to ${(SP.pos.nac0+82.3).toFixed(1)}mm from nose`}/>
        <KV k="Arm stub" v={`${SP.arm_stub_mm}mm hull edge to pod centre`}/>
      </div>
      <div>
        <SH t="Hull Profile (top view, x/half-width in mm)" mt={0}/>
        <div style={{overflowX:"auto"}}>
          <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:9}}>
            <TH cols={["x mm","x\"","half-w mm","total mm"]}/>
            <tbody>{prof.map(([x,y],i)=>{
              const hi=y===41.3||y===11.3;
              return(<tr key={i} style={{background:hi?"rgba(163,230,53,0.06)":i%2===0?"rgba(0,229,255,0.02)":"transparent"}}>
                <td style={{padding:"3px 8px",color:hi?C.lime:C.accent}}>{x.toFixed(1)}</td>
                <td style={{padding:"3px 8px",color:C.dimmer}}>{(x/25.4).toFixed(2)}"</td>
                <td style={{padding:"3px 8px",color:hi?C.lime:C.text,fontWeight:hi?"bold":"normal"}}>{y.toFixed(1)}</td>
                <td style={{padding:"3px 8px",color:C.dim}}>{(y*2).toFixed(1)}</td>
              </tr>);
            })}</tbody>
          </table>
        </div>
        <Note c={C.lime} ch="Green rows: max width 82.7mm (41.3mm half) at 186.6mm · neck 22.5mm (11.3mm half) at 339.5mm."/>
      </div>
    </div>
  </div>);
}

function PropulsionTab(){
  const edf_compare=[
    ["70mm","2200g","1.44","1.35","✗","Too low — insufficient thrust at 18\" + 8-node weight"],
    ["80mm","2800g","1.74","1.64","✗","Insufficient"],
    ["90mm","3600g","2.10","1.99","≈","Empty OK, cargo borderline — rejected"],
    ["100mm","4400g","2.39","2.27","✔","Selected — minimum meeting both T/W >= 2.0"],
    ["120mm","6400g","3.17","3.02","✔","Excess thrust, heavier, higher cost"],
  ];
  return(<div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="100mm EDF Selection" mt={0} c={C.orange}/>
        <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10,marginBottom:16}}>
          <TH cols={["EDF","Thr","T/W E","T/W C","OK","Rationale"]}/>
          <tbody>{edf_compare.map(([sz,t,twe,twc,ok,note],i)=>(
            <tr key={i} style={{background:sz==="100mm"?"rgba(255,107,53,0.08)":i%2===0?"rgba(0,229,255,0.02)":"transparent"}}>
              <td style={{padding:"4px 8px",color:C.orange,fontWeight:sz==="100mm"?"bold":"normal"}}>{sz}</td>
              <td style={{padding:"4px 8px",color:C.text}}>{t}</td>
              <td style={{padding:"4px 8px",color:C.text}}>{twe}</td>
              <td style={{padding:"4px 8px",color:C.text}}>{twc}</td>
              <td style={{padding:"4px 8px",color:ok==="✔"?C.green:ok==="≈"?C.yellow:C.red,fontWeight:"bold"}}>{ok}</td>
              <td style={{padding:"4px 8px",color:C.dim,fontSize:9}}>{note}</td>
            </tr>
          ))}</tbody>
        </table>
        <KV k="EDF ID" v="100mm"/>
        <KV k="Pod OD" v="120mm (3mm wall each side)" vc={C.orange}/>
        <KV k="Thrust each @ 5S" v={`~${SP.thr_each}g`}/>
        <KV k="Total thrust" v={`${SP.thr_total}g (${(SP.thr_total/453.6).toFixed(1)}lb)`} vc={C.green}/>
        <KV k="Power each" v="~1400W peak"/>
        <KV k="ESC" v="60A minimum · 100A rated recommended"/>
        <KV k="Battery" v="5S LiPo (18.5V nominal)"/>
      </div>
      <div>
        <SH t="Weight Summary" mt={0}/>
        <KV k="Base (no battery)" v={`${SP.base_no_bat}g`}/>
        <KV k="Battery empty" v={`${SP.bat_e}g (5S 4500mAh)`}/>
        <KV k="AUW empty" v={`${SP.auw_e}g (${(SP.auw_e/28.35).toFixed(1)}oz)`} vc={C.green}/>
        <KV k="T/W empty" v={`${SP.tw_e}:1`} vc={C.green}/>
        <KV k="Battery cargo" v={`${SP.bat_c}g (5S 2800mAh)`}/>
        <KV k="Payload" v={`${SP.payload}g`}/>
        <KV k="AUW cargo" v={`${SP.auw_c}g (${(SP.auw_c/28.35).toFixed(1)}oz)`} vc={C.green}/>
        <KV k="T/W cargo" v={`${SP.tw_c}:1`} vc={C.green}/>
        <KV k="Max payload (T/W=2.0)" v={`${SP.max_pl}g (${SP.max_pl_oz}oz)`} vc={C.lime}/>
        <KV k="Hover endurance empty" v={`~${SP.end_e} min`}/>
        <KV k="Hover endurance cargo" v={`~${SP.end_c} min`}/>
        <KV k="CG trim range" v="Battery rail ±28mm from nominal"/>
        <SH t="40mm Fuselage EDF"/>
        <KV k="Position" v={`${SP.pos.bell.toFixed(1)}mm (${(SP.pos.bell/25.4).toFixed(2)}")`}/>
        <KV k="Function" v="Transition + variable-area nozzle trim"/>
        <KV k="Nozzle" v="BamJr CC BY 4.0 gear nozzle (scaled)"/>
      </div>
    </div>
  </div>);
}

function LicenseTab(){
  return(<div>
    <div style={{background:"rgba(163,230,53,0.06)",border:`1px solid ${C.lime}33`,borderRadius:4,padding:"14px",marginBottom:20}}>
      <div style={{color:C.lime,fontFamily:M,fontSize:12,fontWeight:"bold",marginBottom:8,letterSpacing:"0.1em"}}>CC BY 4.0 — Creative Commons Attribution 4.0 International</div>
      <div style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.8}}>Share, adapt, build upon — any purpose including commercial — credit required.<br/><span style={{color:C.lime}}>creativecommons.org/licenses/by/4.0</span></div>
    </div>
    <SH t="Author" mt={0} c={C.lime}/>
    <KV k="Name" v="Steve Griffing"/>
    <KV k="Credentials" v="PE(CSE) [Control Systems Engineering] · CISSP-ISSEP · CPP"/>
    <KV k="Year" v="2026"/>
    <SH t="Third-Party Attribution"/>
    {[
      ["Hull geometry","Peter Farell","CC BY 4.0","printables.com/model/548545","Scaled x1.2526 to 18\""],
      ["Variable-area EDF nozzles","BamJr","CC BY 4.0","thingiverse.com/thing:2991269","Scaled to 100mm ID"],
      ["Canonical proportions","Mandel+Earls/QMx/Universal","(c) 2007 QMx","QMx Official Serenity Blueprints","269ft x 170ft x 79ft ratios used"],
      ["Visual inspiration","Joss Whedon/Mutant Enemy/Universal","(c) reserved","Firefly(2002)/Serenity(2005)","Fan engineering work — not licensed"],
    ].map(([w,who,lic,src,note],i)=>(
      <div key={i} style={{padding:"8px 0",borderBottom:"1px solid rgba(0,229,255,0.07)"}}>
        <div style={{display:"flex",justifyContent:"space-between",marginBottom:3}}>
          <span style={{color:C.accent,fontFamily:M,fontSize:10,fontWeight:"bold"}}>{w}</span>
          <span style={{color:lic.includes("(c)")?C.yellow:C.lime,fontFamily:M,fontSize:9}}>{lic}</span>
        </div>
        <div style={{color:C.text,fontFamily:M,fontSize:10}}>{who}</div>
        <div style={{color:C.dim,fontFamily:M,fontSize:9,marginTop:2}}>{src} · {note}</div>
      </div>
    ))}
    <Warn ch="FAA Registration: Replace N00000 with your actual registration before ANY flight. Required 14 CFR 48.100 for sUAS >=250g."/>
  </div>);
}

const TABS=["Overview","Airframe","Propulsion","Electronics","License"];
export default function App(){
  const [tab,setTab]=useState("Overview");
  return(<div style={{minHeight:"100vh",background:C.bg,color:C.text,fontFamily:M}}>
    <Grid/>
    <div style={{background:"rgba(163,230,53,0.06)",borderBottom:"1px solid rgba(163,230,53,0.2)",padding:"5px 24px",fontFamily:M,fontSize:8,color:"rgba(163,230,53,0.65)"}}>
      {"(c) 2026 Steve Griffing PE(CSE) CISSP-ISSEP CPP · CC BY 4.0 · Hull: Peter Farell CC BY 4.0 · Nozzle: BamJr CC BY 4.0 · Firefly/Serenity (c) Joss Whedon/Mutant Enemy/Universal — Fan engineering work"}
    </div>
    <div style={{position:"relative",zIndex:1,borderBottom:`1px solid ${C.border}`,padding:"14px 24px 12px"}}>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",flexWrap:"wrap",gap:12}}>
        <div>
          <div style={{color:"rgba(0,229,255,0.30)",fontSize:9,letterSpacing:"0.2em",marginBottom:4}}>SERENITY-CLASS TILTROTOR UAV · REV F · 18" CANONICAL BUILD</div>
          <h1 style={{margin:0,fontSize:18,fontWeight:"normal",color:"#fff",letterSpacing:"0.07em"}}>SERENITY <span style={{fontSize:13,opacity:0.5}}>FIREFLY-CLASS 03-K64-FF</span></h1>
          <div style={{color:"rgba(0,229,255,0.50)",fontSize:10,marginTop:4}}>
            {`457.2mm (18.000") · 100mm EDF x2 · 4400g thrust · 8-node avionics · Canon 269ft x 170ft x 79ft (QMx Mandel/Earls 2007)`}
          </div>
        </div>
        <div style={{textAlign:"right",fontFamily:M}}>
          <div style={{display:"flex",gap:8,justifyContent:"flex-end",flexWrap:"wrap",marginBottom:5}}>
            {[["T/W EMPTY",`${SP.tw_e}:1`,C.green],["T/W CARGO",`${SP.tw_c}:1`,C.green],["MAX PAYLOAD",`${SP.max_pl}g`,C.lime],["AUW",`${SP.auw_e}g`,C.accent]].map(([l,v,c])=>(
              <div key={l} style={{padding:"3px 10px",border:`1px solid ${c}55`,background:`${c}10`,borderRadius:3}}>
                <span style={{color:C.dimmer,fontFamily:M,fontSize:8}}>{l+" "}</span>
                <span style={{color:c,fontFamily:M,fontSize:9,fontWeight:"bold"}}>{v}</span>
              </div>
            ))}
          </div>
          <div style={{color:C.dimmer,fontFamily:M,fontSize:9}}>Registry: <span style={{color:C.yellow}}>N00000</span> — Replace before flight</div>
        </div>
      </div>
      <div style={{display:"flex",gap:2,marginTop:12,flexWrap:"wrap"}}>
        {TABS.map(t=>(<button key={t} onClick={()=>setTab(t)} style={{background:tab===t?"rgba(0,229,255,0.09)":"transparent",border:`1px solid ${tab===t?C.accent:"rgba(0,229,255,0.12)"}`,color:tab===t?C.accent:C.dimmer,padding:"4px 12px",fontFamily:M,fontSize:9,cursor:"pointer",letterSpacing:"0.06em"}}>{t}</button>))}
      </div>
    </div>
    <div style={{position:"relative",zIndex:1,padding:"20px 24px",maxWidth:1060,margin:"0 auto"}}>
      {tab==="Overview"    && <OverviewTab/>}
      {tab==="Airframe"    && <AirframeTab/>}
      {tab==="Propulsion"  && <PropulsionTab/>}
      {tab==="Electronics" && <ElectronicsTab/>}
      {tab==="License"     && <LicenseTab/>}
    </div>
  </div>);
}
