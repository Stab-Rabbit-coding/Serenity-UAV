import { useState } from "react";

// ── tokens ─────────────────────────────────────────────────────
const C = {
  bg:"#060810", border:"rgba(0,229,255,0.11)", accent:"#00e5ff",
  orange:"#ff6b35", yellow:"#ffe600", purple:"#c084fc", green:"#4ade80",
  pink:"#f472b6", teal:"#2dd4bf", red:"#f87171", lime:"#a3e635",
  gold:"#fbbf24", dim:"rgba(255,255,255,0.40)", dimmer:"rgba(255,255,255,0.22)",
  text:"rgba(255,255,255,0.82)",
  can:"#ff6b35", rs4:"#2dd4bf", eth:"#c084fc", m53:"#fbbf24",
  i2c:"#4ade80", uart:"#f472b6", iso:"#a3e635",
};
const M = "'Courier New','Lucida Console',monospace";

// ── primitives ────────────────────────────────────────────────
const SH=({t,c=C.accent,mt=22})=>(<div style={{display:"flex",alignItems:"center",gap:10,marginBottom:14,marginTop:mt}}><div style={{width:3,height:17,background:c}}/><span style={{color:c,fontFamily:M,fontSize:13,letterSpacing:"0.13em",textTransform:"uppercase",fontWeight:"normal"}}>{t}</span></div>);
const KV=({k,v,vc=C.text,u=""})=>(<div style={{display:"flex",justifyContent:"space-between",padding:"5px 0",borderBottom:"1px solid rgba(0,229,255,0.07)",alignItems:"baseline"}}><span style={{color:C.dim,fontFamily:M,fontSize:11}}>{k}</span><span style={{color:vc,fontFamily:M,fontSize:11}}>{v}{u&&<span style={{color:C.accent,marginLeft:4,fontSize:10}}>{u}</span>}</span></div>);
const Note=({c=C.dim,ch})=>(<div style={{marginTop:8,marginBottom:6,color:c,fontFamily:M,fontSize:10,lineHeight:1.85,padding:"8px 12px",borderLeft:`2px solid ${c}55`,background:`${c}07`,borderRadius:3}}>{ch}</div>);
const Warn=({ch})=>(<div style={{marginTop:8,color:C.yellow,fontFamily:M,fontSize:10,lineHeight:1.8,padding:"7px 12px",borderLeft:`2px solid ${C.yellow}`,background:"rgba(255,230,0,0.05)",borderRadius:3}}>⚠ {ch}</div>);
const Good=({ch})=>(<div style={{marginTop:8,color:C.green,fontFamily:M,fontSize:10,lineHeight:1.8,padding:"7px 12px",borderLeft:`2px solid ${C.green}`,background:"rgba(74,222,128,0.05)",borderRadius:3}}>✓ {ch}</div>);
const IsoTag=({label})=>(<span style={{color:C.lime,border:`1px solid ${C.lime}66`,padding:"1px 6px",borderRadius:2,fontFamily:M,fontSize:8,letterSpacing:"0.06em",verticalAlign:"middle",marginLeft:6}}>ISO</span>);
function TH({cols}){return(<thead><tr>{cols.map(h=>(<th key={h} style={{padding:"6px 9px",borderBottom:`1px solid ${C.border}`,color:C.accent,textAlign:"left",fontWeight:"normal",fontSize:10,letterSpacing:"0.06em",whiteSpace:"nowrap",opacity:.85}}>{h}</th>))}</tr></thead>);}
function Grid(){return(<svg style={{position:"fixed",inset:0,width:"100%",height:"100%",pointerEvents:"none",zIndex:0}}><defs><pattern id="sg" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0L0 0 0 20" fill="none" stroke="rgba(0,229,255,0.035)" strokeWidth={0.5}/></pattern><pattern id="lg" width="100" height="100" patternUnits="userSpaceOnUse"><rect width="100" height="100" fill="url(#sg)"/><path d="M100 0L0 0 0 100" fill="none" stroke="rgba(0,229,255,0.065)" strokeWidth={1}/></pattern></defs><rect width="100%" height="100%" fill="url(#lg)"/></svg>);}

// ════════════════════════════════════════════════════════════════
//  ESC PROTOCOL DATA
// ════════════════════════════════════════════════════════════════
const ESC_PROTOCOLS = [
  {
    id:"dshot", name:"DSHOT (300/600/1200)", color:C.orange,
    category:"Digital command",
    physical:"Single-wire unidirectional (command) · Same wire bidir for BDSHOT",
    interface:"PIO state machine — 1 GPIO per ESC",
    existing:"✔ GP-ESC-L, GP-ESC-R, GP-ESC-FWD already PIO DSHOT",
    hw_change:"None — already implemented",
    telemetry:"BDSHOT: RPM only embedded in response frame (no extra wire)",
    telem_data:["RPM (eRPM from frame)"],
    baud:"N/A — packet protocol",
    supported_fw:["BLHeli32","BLHeli_S","AM32","KISS (via DSHOT)"],
    notes:"DSHOT is already the primary ESC command protocol. BDSHOT mode flips the PIO state machine to bidirectional on the same GPIO — zero hardware change required. Period.",
  },
  {
    id:"blheli_uart", name:"BLHeli32 / AM32 Serial Telemetry", color:C.teal,
    category:"ESC serial telemetry",
    physical:"Single-wire UART 8N1 · TTL level · one wire per ESC (or shared bus with mux)",
    interface:"UART1 (Pico) or UART2 (CM4) · GPIO for each ESC telem line via PIO UART",
    existing:"✔ UART1 already exists (currently RS-485 direction shared) · needs telem mux or dedicated PIO UARTs",
    hw_change:"Add 74HC4052 4:1 analog mux (SOIC-16, ~$0.40) to select which ESC telem wire connects to UART1 RX",
    telemetry:"Full packet @ 115200 baud · 10Hz update rate",
    telem_data:["Temperature (°C)","Voltage (V)","Current (A)","mAh consumed","eRPM","PWM duty","Status flags"],
    baud:"115200 8N1",
    supported_fw:["BLHeli32","AM32"],
    notes:"BLHeli32 and AM32 share identical serial telemetry frame format (10-byte frame). One UART + a 3-channel 4:1 mux selects which ESC is reporting. Pico firmware cycles through ESCs at 10Hz each. The same UART1 used for RS-485 is time-shared — RS-485 and ESC telem are never concurrent (ESC telem is burst, RS-485 is message-based).",
  },
  {
    id:"bdshot", name:"Bidirectional DSHOT (BDSHOT)", color:C.purple,
    category:"ESC RPM feedback",
    physical:"Same single wire as DSHOT — half-duplex bidir · TTL logic",
    interface:"Same PIO GPIO as DSHOT — zero extra hardware",
    existing:"✔ Fully supported by RP2350 PIO — software-only change to enable",
    hw_change:"None",
    telemetry:"eRPM embedded in DSHOT response frame between command frames",
    telem_data:["eRPM (calculate RPM from pole count)"],
    baud:"N/A — embedded in DSHOT timing",
    supported_fw:["BLHeli32 rev 32.7+","AM32","Bluejay"],
    notes:"BDSHOT is already the preferred mode in this design. The RP2350 PIO handles the precision timing required. RPM accuracy ±1 eRPM. No wiring change. Enable in firmware by setting DSHOT_BIDIR = true. Pair with BLHeli serial telem for current/temp.",
  },
  {
    id:"dronecan", name:"DroneCAN / UAVCANv1", color:C.can,
    category:"CAN-based ESC control + telemetry",
    physical:"CAN FD bus — already existing MCP2518FD + ISO1042",
    interface:"Existing CAN FD bus (MCP2518FD on SPI0)",
    existing:"✔ CAN FD hardware fully present · DroneCAN stack on CM4",
    hw_change:"None — use DroneCAN-capable ESCs (T-Motor Flame, Zubax Myxa, Myxa, Orel 20, Kotleta20)",
    telemetry:"ESC Status message @ configurable 20–100Hz per node",
    telem_data:["RPM","Current (A)","Temperature (°C)","Voltage (V)","Power (W)","Error flags","Input command echo"],
    baud:"1Mbps CAN / 4Mbps FD",
    supported_fw:["DroneCAN ESCs (T-Motor, Zubax, Kotleta, Orel, Myxa)"],
    notes:"If DroneCAN ESCs are fitted, ALL telemetry arrives on the existing CAN FD bus — no additional wiring at all. DroneCAN ESC.Status messages carry RPM, current, temperature per ESC node. This is the highest-fidelity telemetry option and the cleanest electrical integration.",
  },
  {
    id:"kiss", name:"KISS Telemetry", color:C.pink,
    category:"ESC serial telemetry",
    physical:"Single-wire UART 8N1 · TTL · one wire per ESC",
    interface:"Same as BLHeli serial — UART1 + 74HC4052 mux",
    existing:"✔ Same hardware path as BLHeli serial telem",
    hw_change:"None beyond BLHeli serial telem hardware (74HC4052 mux already added)",
    telemetry:"10-byte frame @ 100Hz",
    telem_data:["Temperature (°C)","Voltage (V)","Current (A)","mAh","eRPM","Throttle %"],
    baud:"115200 8N1",
    supported_fw:["KISS ESC 24A","KISS ESC 32A","KISS FC ESCs"],
    notes:"KISS telemetry frame format differs from BLHeli (different byte ordering and CRC) but uses the same physical UART path and mux. Firmware detects connected ESC type at boot by querying device info byte and selects the correct decoder.",
  },
];

// ════════════════════════════════════════════════════════════════
//  ISOLATION ARCHITECTURE
// ════════════════════════════════════════════════════════════════
const ISO_BUSES = [
  {
    bus:"CAN FD", col:C.can, current_ic:"MCP2562FD (non-isolated)",
    iso_ic:"ISO1042 (TI)", iso_pkg:"SOIC-8", iso_size:"5.0×4.0mm",
    iso_kv:"5 kV working · 8 kV peak transient",
    iso_mbps:"5 Mbps CAN FD rated",
    rationale:"Replaces MCP2562FD 1:1. Same footprint family. 5kV galvanic isolation — eliminates ground loop through EDF power bus.",
    weight_delta:"~0g (same IC size)", cost:"$2.20",
    existing:"Already on both boards · swap IC at next rev",
  },
  {
    bus:"RS-485", col:C.rs4, current_ic:"MAX3485 (non-isolated)",
    iso_ic:"ISO3086 (TI) or THVD1410", iso_pkg:"SOIC-16 or SSOP-16", iso_size:"9.9×3.9mm",
    iso_kv:"3 kV working · 7 kV transient",
    iso_mbps:"40 Mbps",
    rationale:"Replaces MAX3485. ISO3086 is a self-contained isolated RS-485 transceiver — one IC, no separate isolator needed. Slightly larger package but eliminates separate isolator chip.",
    weight_delta:"~0.1g", cost:"$3.50",
    existing:"Added Rev G · upgrade IC",
  },
  {
    bus:"Ethernet", col:C.eth, current_ic:"HX1188NL magnetics (already isolated)",
    iso_ic:"HX1188NL (retained)", iso_pkg:"SMD module", iso_size:"12×7mm",
    iso_kv:"1.5 kV (transformer isolation)",
    iso_mbps:"100 Mbps",
    rationale:"Already galvanically isolated by the Ethernet magnetics transformer. No change required.",
    weight_delta:"0g", cost:"$0 (no change)",
    existing:"✔ Fully isolated — no action needed",
  },
  {
    bus:"MIL-STD-1553B", col:C.m53, current_ic:"SM-1553-11 (already isolated)",
    iso_ic:"SM-1553-11 (retained)", iso_pkg:"SMD 4.8×8.0mm", iso_size:"4.8×8.0mm",
    iso_kv:"1.5 kV",
    iso_mbps:"1 Mbps Manchester",
    rationale:"Already galvanically isolated by the SM-1553-11 isolation transformer. No change required.",
    weight_delta:"0g", cost:"$0 (no change)",
    existing:"✔ Fully isolated — no action needed",
  },
  {
    bus:"I²C (on-PCB sensor bus)", col:C.i2c, current_ic:"PCA9517 buffer (non-isolated)",
    iso_ic:"ISO1540 (TI)", iso_pkg:"SO-8", iso_size:"5.0×4.0mm",
    iso_kv:"3 kV working · 5 kV transient",
    iso_mbps:"1 Mbps I²C FM+",
    rationale:"ISO1540 is a bidirectional I²C isolator — replaces PCA9517. Identical function but with galvanic isolation. Protects MCU from external sensor faults or ESD on extended I²C cables.",
    weight_delta:"~0g", cost:"$2.80",
    existing:"Added Rev G · upgrade IC",
  },
  {
    bus:"UART (ESC telem / GPS / debug)", col:C.uart, current_ic:"Direct GPIO (non-isolated)",
    iso_ic:"ISO7241C (TI) — 4-channel", iso_pkg:"SOIC-16", iso_size:"9.9×3.9mm",
    iso_kv:"4 kV working · 8 kV transient",
    iso_mbps:"150 Mbps per channel",
    rationale:"One ISO7241C isolates 4 UART signals simultaneously (TX, RX, DE, RE). Placed between the MCU GPIO and any UART connector going off-board. Internal UARTs (GPS on TRIHAT-1) remain direct. External UART connectors (ESC telem, debug) get isolation.",
    weight_delta:"~0.1g", cost:"$2.50",
    existing:"New · add to ESC telem connector section",
  },
];

// ════════════════════════════════════════════════════════════════
//  GPIO MAP — XIAO RP2350 on SENSORHAT-1
// ════════════════════════════════════════════════════════════════
const XIAO_GPIO = [
  // Direct on XIAO
  {pin:"D0 / GP26",  func:"DSHOT PIO: ESC-L (bidir)",      bus:"PIO0-SM0", note:"Bidirectional DSHOT + BDSHOT RPM"},
  {pin:"D1 / GP27",  func:"DSHOT PIO: ESC-R (bidir)",      bus:"PIO0-SM1", note:"Bidirectional DSHOT + BDSHOT RPM"},
  {pin:"D2 / GP28",  func:"DSHOT PIO: ESC-Fwd (bidir)",    bus:"PIO0-SM2", note:"Bidirectional DSHOT + BDSHOT RPM"},
  {pin:"D3 / GP29",  func:"WS2812 LED chain",               bus:"PIO0-SM3", note:"Nav lights (6 LEDs)"},
  {pin:"D4 / GP6",   func:"I²C1 SDA — sensor bus",          bus:"I2C1 HW",  note:"IMU · Baro · Airspeed · MCP23017"},
  {pin:"D5 / GP7",   func:"I²C1 SCL — sensor bus",          bus:"I2C1 HW",  note:"ISO1540 isolator at connector"},
  {pin:"D6 / GP0",   func:"UART0 TX → GPS M10Q",             bus:"UART0 HW", note:"u-blox UBX binary"},
  {pin:"D7 / GP1",   func:"UART0 RX ← GPS M10Q",             bus:"UART0 HW", note:"u-blox UBX binary"},
  {pin:"D8 / GP2",   func:"SPI0 SCK (shared bus)",           bus:"SPI0 HW",  note:"ICM-42688 · MCP2518FD · TPM · HI-6130"},
  {pin:"D9 / GP3",   func:"SPI0 MISO",                       bus:"SPI0 HW",  note:""},
  {pin:"D10 / GP4",  func:"SPI0 MOSI",                       bus:"SPI0 HW",  note:""},
  {pin:"D11 / GP5",  func:"UART1 TX → RS-485 (ISO3086)",     bus:"UART1 HW", note:"Secondary MAVLink / ESC telem TX"},
  {pin:"D12 / GP8",  func:"UART1 RX ← RS-485 + ESC telem",  bus:"UART1 HW", note:"74HC4052 mux selects ESC or RS-485"},
  {pin:"D13 / GP9",  func:"RS-485 DE/RE direction",           bus:"GPIO out", note:"ISO3086 direction control"},
  {pin:"D14 / GP10", func:"SPI1 SCK (Ethernet W5500)",        bus:"SPI1 HW",  note:""},
  {pin:"D15 / GP11", func:"SPI1 MOSI",                        bus:"SPI1 HW",  note:""},
  {pin:"D16 / GP12", func:"SPI1 MISO",                        bus:"SPI1 HW",  note:""},
  {pin:"D17 / GP13", func:"W5500 CS̄",                         bus:"GPIO out", note:"SPI1 CS Ethernet"},
  {pin:"D18 / GP14", func:"W5500 IRQ (input)",                 bus:"GPIO in",  note:"Ethernet interrupt"},
  {pin:"D19 / GP15", func:"MCP2518FD CS̄",                     bus:"GPIO out", note:"SPI0 CS CAN FD"},
  {pin:"D20 / GP16", func:"SPI0 CS: IMU ICM-42688",            bus:"GPIO out", note:""},
  {pin:"D21 / GP17", func:"SPI0 CS: TPM SLB9670",              bus:"GPIO out", note:""},
  {pin:"D22 / GP18", func:"SPI0 CS: HI-6130 (1553)",           bus:"GPIO out", note:""},
  {pin:"D23 / GP19", func:"HI-6130 IRQ (input)",                bus:"GPIO in",  note:"1553 interrupt"},
  {pin:"D24 / GP20", func:"HI-6130 RST (output)",               bus:"GPIO out", note:"1553 reset"},
  {pin:"D25 / GP21", func:"MCP2518FD IRQ (input)",               bus:"GPIO in",  note:"CAN interrupt"},
  // MCP23017 expander handles non-time-critical outputs
  {pin:"MCP23017 GPA0", func:"Nacelle servo L PWM",            bus:"I²C expdr",note:"Via ISO1540 · 50Hz PWM from expander"},
  {pin:"MCP23017 GPA1", func:"Nacelle servo R PWM",            bus:"I²C expdr",note:"Via ISO1540 · 50Hz PWM from expander"},
  {pin:"MCP23017 GPA2", func:"Fuselage nozzle servo",           bus:"I²C expdr",note:"Servo PWM"},
  {pin:"MCP23017 GPA3", func:"Payload release servo",           bus:"I²C expdr",note:"Servo PWM"},
  {pin:"MCP23017 GPA4", func:"Winch DRV8833 IN1",              bus:"I²C expdr",note:"Winch motor H-bridge"},
  {pin:"MCP23017 GPA5", func:"Winch DRV8833 IN2",              bus:"I²C expdr",note:"Winch motor H-bridge"},
  {pin:"MCP23017 GPA6", func:"ESC telem mux SEL-A (74HC4052)", bus:"I²C expdr",note:"Selects ESC-L/R/Fwd telem"},
  {pin:"MCP23017 GPA7", func:"ESC telem mux SEL-B (74HC4052)", bus:"I²C expdr",note:"Selects ESC-L/R/Fwd telem"},
  {pin:"MCP23017 GPB0", func:"LED status / heartbeat",          bus:"I²C expdr",note:"Board health indicator"},
  {pin:"MCP23017 GPB1", func:"Spare GPIO",                      bus:"I²C expdr",note:"Future expansion"},
];

// ════════════════════════════════════════════════════════════════
//  BOARD SIZE COMPARISON
// ════════════════════════════════════════════════════════════════
const BOARD_COMPARE = [
  {board:"TRIHAT-1 (Rev G)",           w:65, h:56, area:3640, mcu:"Pico 2 header",    weight:22, note:"Current design"},
  {board:"SENSORHAT-1 (Rev H.1)",      w:46, h:36, area:1656, mcu:"XIAO RP2350 SMD", weight:11, note:"XIAO direct-solder · 55% smaller"},
  {board:"CM4-CARRIER-1 Rev E",        w:65, h:52, area:3380, mcu:"CM4 module",       weight:18, note:"Current design"},
  {board:"CARRIER-2 (Rev H.1)",        w:57, h:44, area:2508, mcu:"CM4 module",       weight:13, note:"Min CM4 footprint · 26% smaller"},
  {board:"COMPHAT-1 Rev E",            w:65, h:48, area:3120, mcu:"CM4 hat",           weight:16, note:"Unchanged — already well-optimised"},
];

// ════════════════════════════════════════════════════════════════
//  TAB 1: ESC PROTOCOL MATRIX
// ════════════════════════════════════════════════════════════════
function ESCProtocolTab(){
  const [sel,setSel]=useState("dshot");
  const p=ESC_PROTOCOLS.find(x=>x.id===sel)||ESC_PROTOCOLS[0];
  return(<div>
    <div style={{background:"rgba(0,229,255,0.04)",border:`1px solid ${C.border}`,borderRadius:4,padding:"10px 14px",marginBottom:16,fontFamily:M,fontSize:11,color:C.dim,lineHeight:1.8}}>
      <span style={{color:C.accent,fontWeight:"bold"}}>Design principle:</span> One UART (shared with RS-485 via firmware time-division) + the existing DSHOT PIO outputs + the existing CAN FD bus covers ALL ESC/motor-driver telemetry protocols. No new dedicated interface ICs needed beyond a <span style={{color:C.yellow}}>74HC4052 analog mux</span> (~$0.40) to route ESC serial telem lines.
    </div>

    {/* Protocol selector */}
    <div style={{display:"flex",gap:6,flexWrap:"wrap",marginBottom:16}}>
      {ESC_PROTOCOLS.map(x=>(<button key={x.id} onClick={()=>setSel(x.id)} style={{
        background:sel===x.id?`${x.color}20`:"transparent",
        border:`1px solid ${sel===x.id?x.color:"rgba(0,229,255,0.15)"}`,
        color:sel===x.id?x.color:C.dimmer,
        padding:"5px 14px",fontFamily:M,fontSize:9,cursor:"pointer",borderRadius:2,lineHeight:1.4
      }}>{x.name}</button>))}
    </div>

    {p&&(<div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24,marginBottom:24}}>
      <div>
        <div style={{color:p.color,fontFamily:M,fontSize:13,fontWeight:"bold",marginBottom:12}}>{p.name}</div>
        <KV k="Category"          v={p.category}/>
        <KV k="Physical layer"    v={p.physical}/>
        <KV k="MCU interface"     v={p.interface}/>
        <KV k="Existing on board" v={p.existing} vc={p.hw_change==="None"?C.green:C.yellow}/>
        <KV k="Hardware change"   v={p.hw_change} vc={p.hw_change==="None"?C.green:C.yellow}/>
        <KV k="Baud / rate"       v={p.baud}/>
        <KV k="Compatible FW"     v={p.supported_fw.join(" · ")} vc={C.teal}/>
        <div style={{marginTop:12}}>
          <div style={{color:C.dim,fontFamily:M,fontSize:10,marginBottom:6,letterSpacing:"0.08em"}}>TELEMETRY DATA AVAILABLE:</div>
          {p.telem_data.map((d,i)=>(<div key={i} style={{display:"flex",gap:8,padding:"3px 0",borderBottom:"1px solid rgba(0,229,255,0.06)"}}>
            <span style={{color:p.color,fontFamily:M,fontSize:10}}>→</span>
            <span style={{color:C.text,fontFamily:M,fontSize:10}}>{d}</span>
          </div>))}
        </div>
      </div>
      <div>
        <Note c={p.color} ch={p.notes}/>
        {p.id==="dronecan"&&<Good ch="DroneCAN ESCs (Zubax Myxa, T-Motor Flame, Kotleta20) report full telemetry on the existing CAN FD bus with zero additional wiring. This is the highest-fidelity and lowest-overhead integration path."/>}
        {p.id==="blheli_uart"&&<Note c={C.yellow} ch="The 74HC4052 is a 4-channel analog mux in SOIC-16 (9.9×3.9mm). One package handles all 3 ESC telem lines with 2 GPIO select pins (from MCP23017 expander). The mux is transparent — signal integrity identical to direct connection."/>}
        {p.id==="bdshot"&&<Good ch="BDSHOT is enabled in firmware only. The RP2350 PIO state machine handles the timing with nanosecond precision. Zero additional hardware compared to the current DSHOT implementation."/>}
      </div>
    </div>)}

    <SH t="Telemetry Comparison Matrix"/>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["PROTOCOL","RPM","CURR (A)","TEMP (°C)","VOLT (V)","mAh","WIRE ΔHARDWARE","FW EXAMPLES"]}/>
        <tbody>{[
          ["BDSHOT",           "✔","—","—","—","—","None (bidir mode)",    "BLHeli32 / AM32 / Bluejay"],
          ["BLHeli/AM32 UART", "✔","✔","✔","✔","✔","74HC4052 mux ~$0.40","BLHeli32 / AM32"],
          ["KISS UART",        "✔","✔","✔","✔","✔","Same mux as above",   "KISS ESC"],
          ["DroneCAN",         "✔","✔","✔","✔","—","None (existing CAN)", "T-Motor / Zubax / Kotleta"],
          ["DSHOT (cmd only)", "—","—","—","—","—","None (existing)",     "All DSHOT ESCs"],
        ].map((row,i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.02)":"transparent"}}>
            {row.map((v,j)=>(<td key={j} style={{padding:"5px 9px",color:j===0?C.teal:v==="✔"?C.green:v==="—"?C.dimmer:v.includes("None")?C.green:C.yellow,fontFamily:M,fontSize:10,fontWeight:j===0?"bold":"normal",whiteSpace:"nowrap"}}>{v}</td>))}
          </tr>
        ))}</tbody>
      </table>
    </div>

    <SH t="Recommended ESC Telemetry Strategy"/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <Note c={C.green} ch="RECOMMENDED: Enable BDSHOT on all three DSHOT lines (zero hardware) for real-time RPM on every control loop cycle. Add BLHeli32/AM32 serial telem (74HC4052 mux, one IC) for current and temperature at 10Hz. Total hardware addition: one SOT or SOIC mux IC."/>
        <Note c={C.teal} ch="IF using DroneCAN ESCs: disable DSHOT entirely. DroneCAN ESC command replaces DSHOT command, and ESC Status telemetry replaces all serial telem — arriving on the existing CAN FD bus already in the design."/>
      </div>
      <div>
        <Note c={C.yellow} ch="Individual motor temperature monitoring requires serial telemetry (BDSHOT alone does not carry temperature). If BLHeli32/AM32 ESCs are used, the 74HC4052 mux enables per-ESC temperature polling at 10Hz — sufficient for thermal protection decisions."/>
        <Warn ch="KISS ESCs are less common in the BLHeli32 era. If the operator uses KISS firmware: the same mux hardware works. Firmware detects the connected ESC type at boot via the device-info query byte and switches the decoder automatically."/>
      </div>
    </div>
  </div>);
}

// ════════════════════════════════════════════════════════════════
//  TAB 2: GPIO / INTERFACE AUDIT
// ════════════════════════════════════════════════════════════════
function GPIOAuditTab(){
  const direct=XIAO_GPIO.filter(g=>!g.pin.startsWith("MCP"));
  const expdr=XIAO_GPIO.filter(g=>g.pin.startsWith("MCP"));
  const busColors={"PIO0-SM0":C.orange,"PIO0-SM1":C.orange,"PIO0-SM2":C.orange,"PIO0-SM3":C.purple,
    "I2C1 HW":C.i2c,"SPI0 HW":C.teal,"SPI1 HW":C.eth,"UART0 HW":C.green,"UART1 HW":C.rs4,
    "GPIO out":C.dim,"GPIO in":C.dimmer,"I²C expdr":C.gold};
  return(<div>
    <div style={{background:"rgba(163,230,53,0.05)",border:`1px solid ${C.lime}33`,borderRadius:4,padding:"10px 14px",marginBottom:16,fontFamily:M,fontSize:11,color:C.dim}}>
      <span style={{color:C.lime,fontWeight:"bold"}}>SENSORHAT-1 (Rev H.1):</span> XIAO RP2350 replaces Pico 2. Direct-solder castellated pads — no headers, no socket. GPIO expander MCP23017 handles 10 non-time-critical outputs over I²C. All 26 direct XIAO GPIO accounted for; 6 MCP23017 GPA pins carry servos, winch, ESC mux select.
    </div>
    <SH t="XIAO RP2350 — Direct GPIO Assignments" mt={0}/>
    <div style={{overflowX:"auto",marginBottom:20}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["XIAO PIN","FUNCTION","BUS / TYPE","NOTES"]}/>
        <tbody>{direct.map((g,i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
            <td style={{padding:"4px 9px",color:C.yellow,whiteSpace:"nowrap",fontFamily:"'Courier New',monospace",fontSize:10}}>{g.pin}</td>
            <td style={{padding:"4px 9px",color:C.text}}>{g.func}</td>
            <td style={{padding:"4px 9px",whiteSpace:"nowrap"}}><span style={{color:busColors[g.bus]||C.dim,border:`1px solid ${busColors[g.bus]||C.dim}44`,padding:"1px 5px",borderRadius:2,fontSize:8}}>{g.bus}</span></td>
            <td style={{padding:"4px 9px",color:C.dim,fontSize:9}}>{g.note}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>

    <SH t="MCP23017 I²C GPIO Expander — Non-Time-Critical Outputs"/>
    <div style={{overflowX:"auto",marginBottom:16}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["EXPANDER PIN","FUNCTION","TYPE","NOTES"]}/>
        <tbody>{expdr.map((g,i)=>(
          <tr key={i} style={{background:"rgba(255,191,36,0.025)"}}>
            <td style={{padding:"4px 9px",color:C.gold,whiteSpace:"nowrap",fontFamily:"'Courier New',monospace",fontSize:10}}>{g.pin}</td>
            <td style={{padding:"4px 9px",color:C.text}}>{g.func}</td>
            <td style={{padding:"4px 9px"}}><span style={{color:C.gold,border:`1px solid ${C.gold}44`,padding:"1px 5px",borderRadius:2,fontSize:8}}>I²C expander</span></td>
            <td style={{padding:"4px 9px",color:C.dim,fontSize:9}}>{g.note}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>
    <Note c={C.gold} ch="MCP23017 is an I²C 16-bit GPIO expander in QFN-28 (4×4mm). At 400kHz I²C, a full 16-bit write takes ~200µs — adequate for servo PWM updates (50Hz = 20ms period). For servo PWM precision, the MCP23017 drives the servo via a hardware PWM signal from a small dedicated PWM IC (PCA9685, also I²C) if sub-1ms accuracy is needed. Alternatively, the XIAO's 24 PWM channels can handle servos directly if GPIO budget allows reallocation."/>

    <SH t="ESC Telemetry Mux — 74HC4052"/>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <KV k="IC" v="74HC4052 — dual 4:1 analog mux" vc={C.yellow}/>
        <KV k="Package" v="SOIC-16 · 9.9×3.9mm (or TSSOP-16 for smaller)"/>
        <KV k="Function" v="Routes one of 3 ESC serial telem wires to UART1 RX"/>
        <KV k="Select pins" v="S0 = MCP23017 GPA6 · S1 = MCP23017 GPA7"/>
        <KV k="State 00" v="ESC-L telem → UART1 RX"/>
        <KV k="State 01" v="ESC-R telem → UART1 RX"/>
        <KV k="State 10" v="ESC-Fwd telem → UART1 RX"/>
        <KV k="State 11" v="RS-485 / debug UART (default)"/>
        <KV k="Switching time" v="&lt;10ns — transparent to UART"/>
        <KV k="Isolation" v="ISO7241C on UART external signals" vc={C.lime}/>
      </div>
      <div>
        <Note c={C.teal} ch="The 74HC4052 allows the single UART1 to serve dual purpose: inter-board RS-485 data bus (state 11) and ESC telemetry polling (states 00/01/10). The Pico firmware never switches mid-byte — it completes any RS-485 transaction, idles the bus, switches mux state, waits for ESC telem frame, then returns to RS-485. Total ESC poll cycle per ESC: ~87µs at 115200 baud for a 10-byte frame."/>
      </div>
    </div>
  </div>);
}

// ════════════════════════════════════════════════════════════════
//  TAB 3: ISOLATION ARCHITECTURE
// ════════════════════════════════════════════════════════════════
function IsoArchDiagram(){
  const VW=680, VH=360;
  // MCU block, each bus with isolation barrier symbol
  const buses=[
    {name:"CAN FD",  col:C.can,  y:60,  ic:"ISO1042",   pkg:"SOIC-8", kv:"5kV"},
    {name:"RS-485",  col:C.rs4,  y:110, ic:"ISO3086",   pkg:"SSOP-16",kv:"3kV"},
    {name:"Ethernet",col:C.eth,  y:160, ic:"HX1188NL",  pkg:"SMD mod",kv:"1.5kV ✔"},
    {name:"1553B",   col:C.m53,  y:210, ic:"SM-1553-11",pkg:"4.8×8mm",kv:"1.5kV ✔"},
    {name:"I²C",     col:C.i2c,  y:260, ic:"ISO1540",   pkg:"SO-8",   kv:"3kV"},
    {name:"UART ext",col:C.uart, y:310, ic:"ISO7241C",  pkg:"SOIC-16",kv:"4kV"},
  ];
  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* MCU block */}
      <rect x={20} y={40} width={120} height={300} rx={6}
        fill="rgba(0,229,255,0.06)" stroke={C.accent} strokeWidth={1.5}/>
      <text x={80} y={58} textAnchor="middle" fill={C.accent} fontSize={9} fontFamily={M} fontWeight="bold">MCU</text>
      <text x={80} y={70} textAnchor="middle" fill={`${C.accent}60`} fontSize={7} fontFamily={M}>XIAO RP2350</text>
      <text x={80} y={82} textAnchor="middle" fill={`${C.accent}50`} fontSize={7} fontFamily={M}>or CM4</text>
      {buses.map(b=>(
        <text key={b.name} x={80} y={b.y+8} textAnchor="middle" fill={b.col} fontSize={8} fontFamily={M}>{b.name}</text>
      ))}

      {/* Buses from MCU → isolator → connector */}
      {buses.map(b=>{
        const alreadyIso=b.kv.includes("✔");
        return(<g key={b.name}>
          {/* Wire from MCU */}
          <line x1={140} y1={b.y} x2={200} y2={b.y} stroke={b.col} strokeWidth={2.5}/>
          {/* Isolator block */}
          <rect x={200} y={b.y-16} width={100} height={32} rx={3}
            fill={alreadyIso?`${b.col}15`:`${C.lime}12`}
            stroke={alreadyIso?b.col:C.lime} strokeWidth={1.8}/>
          {/* ISO barrier symbol */}
          {!alreadyIso&&<>
            <line x1={245} y1={b.y-14} x2={245} y2={b.y+14} stroke={C.lime} strokeWidth={1.5} strokeDasharray="2 2"/>
            <text x={246} y={b.y-6} fill={C.lime} fontSize={6} fontFamily={M}>⊥ ISO</text>
          </>}
          <text x={250} y={b.y+3} textAnchor="middle" fill={alreadyIso?b.col:C.lime} fontSize={7} fontFamily={M} fontWeight="bold">{b.ic}</text>
          <text x={250} y={b.y+13} textAnchor="middle" fill={`${b.col}70`} fontSize={6} fontFamily={M}>{b.kv}</text>
          {/* Wire from isolator to connector */}
          <line x1={300} y1={b.y} x2={360} y2={b.y} stroke={b.col} strokeWidth={2.5}/>
          {/* Connector */}
          <rect x={360} y={b.y-12} width={44} height={24} rx={3}
            fill={`${b.col}18`} stroke={b.col} strokeWidth={1.2}/>
          <text x={382} y={b.y+4} textAnchor="middle" fill={b.col} fontSize={7} fontFamily={M} fontWeight="bold">JST-GH</text>
          {/* External label */}
          <text x={414} y={b.y+4} fill={`${b.col}70`} fontSize={7} fontFamily={M}>{b.pkg}</text>
          {/* Ground plane break illustration */}
          <rect x={192} y={b.y-16} width={8} height={32} fill={`${C.lime}30`}/>
        </g>);
      })}

      {/* Ground plane break labels */}
      <rect x={190} y={20} width={12} height={330} fill={`${C.lime}08`} stroke={C.lime} strokeWidth={0.5} strokeDasharray="4 4"/>
      <text x={196} y={14} textAnchor="middle" fill={C.lime} fontSize={7} fontFamily={M} fontWeight="bold">ISO BARRIER</text>

      {/* Legend */}
      <rect x={430} y={40} width={230} height={130} rx={4} fill="rgba(0,0,0,0.45)" stroke="rgba(255,255,255,0.1)"/>
      <text x={545} y={56} textAnchor="middle" fill={C.dimmer} fontSize={7} fontFamily={M} letterSpacing="1">ISOLATION TYPES</text>
      {[["ISO1042 (CAN)",   C.can,  "NEW — replaces MCP2562FD"],
        ["ISO3086 (RS-485)",C.rs4,  "NEW — replaces MAX3485"],
        ["ISO1540 (I²C)",   C.i2c,  "NEW — replaces PCA9517"],
        ["ISO7241C (UART)", C.uart, "NEW — external UART lines"],
        ["HX1188NL (ETH)",  C.eth,  "EXISTING — unchanged"],
        ["SM-1553-11 (1553)",C.m53, "EXISTING — unchanged"],
      ].map(([label,col,note],i)=>(
        <g key={label}>
          <rect x={440} y={64+i*17} width={10} height={10} rx={2} fill={col} opacity={0.7}/>
          <text x={456} y={73+i*17} fill={col} fontSize={7} fontFamily={M}>{label}</text>
          <text x={540} y={73+i*17} fill={C.dimmer} fontSize={6} fontFamily={M}>{note}</text>
        </g>
      ))}

      <text x={VW/2} y={14} textAnchor="middle" fill="rgba(0,229,255,0.25)" fontSize={9} fontFamily={M} letterSpacing="0.1em">FULL BUS ISOLATION ARCHITECTURE — ALL INTER-BOARD SIGNALS</text>
      <text x={VW/2} y={VH-6} textAnchor="middle" fill="rgba(163,230,53,0.2)" fontSize={7} fontFamily={M}>Every inter-board bus is galvanically isolated · MCU ground domain separated from bus ground domain</text>
    </svg>
  );
}

function IsolationTab(){
  return(<div>
    <div style={{background:"rgba(163,230,53,0.05)",border:`1px solid ${C.lime}33`,borderRadius:4,padding:"10px 14px",marginBottom:16,fontFamily:M,fontSize:11,color:C.dim,lineHeight:1.8}}>
      <span style={{color:C.lime,fontWeight:"bold"}}>Policy (Rev H.1):</span> Every signal that crosses a PCB-to-board or board-to-external-device boundary is galvanically isolated. The MCU's local ground domain is separated from every bus ground domain. This extends the existing MIL-STD-1553 transformer isolation philosophy uniformly to all six inter-board buses.
    </div>
    <SH t="Isolation Architecture Diagram" mt={0}/>
    <div style={{border:`1px solid ${C.border}`,borderRadius:4,background:"rgba(0,229,255,0.01)",padding:8,marginBottom:20}}>
      <IsoArchDiagram/>
    </div>
    <div style={{overflowX:"auto",marginBottom:20}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["BUS","CURRENT IC","NEW ISO IC","PKG","ISOLATION","CHANGE","COST/BOARD"]}/>
        <tbody>{ISO_BUSES.map((b,i)=>(<tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent",verticalAlign:"top"}}>
          <td style={{padding:"5px 9px",color:b.col,fontWeight:"bold",whiteSpace:"nowrap"}}>{b.bus}</td>
          <td style={{padding:"5px 9px",color:C.dim,fontSize:9}}>{b.current_ic}</td>
          <td style={{padding:"5px 9px",color:b.existing.includes("✔")?C.green:C.lime,fontWeight:"bold",whiteSpace:"nowrap"}}>{b.iso_ic}</td>
          <td style={{padding:"5px 9px",color:C.dimmer,fontSize:9,whiteSpace:"nowrap"}}>{b.iso_pkg}</td>
          <td style={{padding:"5px 9px",color:C.yellow,whiteSpace:"nowrap"}}>{b.iso_kv}</td>
          <td style={{padding:"5px 9px",color:b.existing.includes("✔")?C.green:C.lime,fontSize:9}}>{b.rationale.split(".")[0]}.</td>
          <td style={{padding:"5px 9px",color:C.green,fontWeight:"bold",whiteSpace:"nowrap"}}>{b.cost}</td>
        </tr>))}</tbody>
      </table>
    </div>
    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="Why Full Isolation?" mt={0}/>
        {[["Ground loop elimination","EDF motors at full throttle sink up to 35A through the airframe. Without isolation, this creates ground potential differences that appear as common-mode noise on all buses. At 1Mbps, a 50mV ground shift introduces bit errors."],
          ["ESD protection","An ESC connector plugged in live can deliver transients exceeding 2kV to the MCU GPIO. ISO1042, ISO3086, and ISO7241C are rated for 4–8kV HBM ESD — the MCU survives the transient."],
          ["Fault containment","A short or overvoltage on any external bus cannot propagate to the MCU domain. An ESC fire, a failed motor driver, or a shorted RS-485 cable cannot take down the flight controller."],
          ["MIL-STD-1553 consistency","1553 has always required galvanic isolation via the SM-1553-11 transformer. Extending this requirement to all buses makes the design uniform and eliminates the weakest-link problem."],
        ].map(([t,d],i)=>(<div key={i} style={{marginBottom:10}}><div style={{color:C.lime,fontFamily:M,fontSize:10,fontWeight:"bold",marginBottom:2}}>{t}</div><div style={{color:C.dim,fontFamily:M,fontSize:10,lineHeight:1.7}}>{d}</div></div>))}
      </div>
      <div>
        <SH t="ISO1042 — CAN FD Drop-In" mt={0} c={C.can}/>
        <KV k="Part" v="ISO1042DGKR (TI) · SOIC-8"/>
        <KV k="Replaces" v="MCP2562FD — identical pin-compatible function"/>
        <KV k="Isolation" v="5000 Vrms working · 8000 Vpk transient"/>
        <KV k="Data rate" v="5 Mbps CAN FD rated (>4Mbps needed)"/>
        <KV k="Supply" v="3.3V logic side · 5V bus side (same as MCP2562FD)"/>
        <SH t="ISO3086 — RS-485 Drop-In" c={C.rs4}/>
        <KV k="Part" v="ISO3086DW (TI) · SOIC-16"/>
        <KV k="Replaces" v="MAX3485 + separate isolator IC → single part"/>
        <KV k="Isolation" v="3000 Vrms working"/>
        <KV k="Data rate" v="40 Mbps (>1Mbps needed)"/>
        <SH t="ISO7241C — UART (4-channel)" c={C.uart}/>
        <KV k="Part" v="ISO7241CDWR (TI) · SOIC-16"/>
        <KV k="Channels" v="4 directional isolators — covers TX + RX + DE + RE"/>
        <KV k="Isolation" v="4000 Vrms working · 8000 Vpk transient"/>
        <KV k="Data rate" v="150 Mbps per channel"/>
        <KV k="Use" v="ESC telem connector · debug UART connector"/>
      </div>
    </div>
  </div>);
}

// ════════════════════════════════════════════════════════════════
//  TAB 4: XIAO RP2350 EVALUATION
// ════════════════════════════════════════════════════════════════
function BoardDiagram(){
  const VW=640, VH=320;
  // TRIHAT-1 current (65×56mm scaled)
  const S=4.0;
  const old_w=65*S, old_h=56*S;
  const new_w=46*S, new_h=36*S;
  const old_x=20, old_y=40;
  const new_x=360, new_y=70;

  return(
    <svg viewBox={`0 0 ${VW} ${VH}`} width="100%" style={{maxWidth:"100%",display:"block"}}>
      {/* Old board outline */}
      <rect x={old_x} y={old_y} width={old_w} height={old_h} rx={4}
        fill="rgba(0,229,255,0.06)" stroke={C.accent} strokeWidth={2}/>
      {/* Pico 2 module on old board */}
      <rect x={old_x+10} y={old_y+8} width={51*S} height={21*S} rx={3}
        fill="rgba(0,229,255,0.12)" stroke={C.accent} strokeWidth={1}/>
      <text x={old_x+10+51*S/2} y={old_y+22} textAnchor="middle" fill={C.accent} fontSize={8} fontFamily={M} fontWeight="bold">PICO 2</text>
      <text x={old_x+10+51*S/2} y={old_y+33} textAnchor="middle" fill={`${C.accent}60`} fontSize={7} fontFamily={M}>51×21mm · 2× 20-pin header</text>
      <text x={old_x+old_w/2} y={old_y+old_h+16} textAnchor="middle" fill={C.dimmer} fontSize={8} fontFamily={M}>TRIHAT-1 Rev G  65×56mm  ~22g</text>
      {/* Area fill */}
      <text x={old_x+old_w/2} y={old_y+old_h/2+30} textAnchor="middle" fill="rgba(0,229,255,0.15)" fontSize={32} fontFamily={M}>3640</text>
      <text x={old_x+old_w/2} y={old_y+old_h/2+46} textAnchor="middle" fill="rgba(0,229,255,0.2)" fontSize={10} fontFamily={M}>mm²</text>
      {/* New board */}
      <rect x={new_x} y={new_y} width={new_w} height={new_h} rx={4}
        fill="rgba(163,230,53,0.08)" stroke={C.lime} strokeWidth={2}/>
      {/* XIAO module */}
      <rect x={new_x+6} y={new_y+5} width={21*S} height={17.5*S} rx={2}
        fill="rgba(163,230,53,0.18)" stroke={C.lime} strokeWidth={1.5}/>
      <text x={new_x+6+21*S/2} y={new_y+19} textAnchor="middle" fill={C.lime} fontSize={8} fontFamily={M} fontWeight="bold">XIAO</text>
      <text x={new_x+6+21*S/2} y={new_y+29} textAnchor="middle" fill={`${C.lime}70`} fontSize={6} fontFamily={M}>21×17.5mm</text>
      <text x={new_x+6+21*S/2} y={new_y+38} textAnchor="middle" fill={`${C.lime}50`} fontSize={6} fontFamily={M}>direct solder</text>
      {/* MCP23017 expander */}
      <rect x={new_x+new_w-6-16} y={new_y+5} width={16} height={14} rx={2}
        fill="rgba(255,191,36,0.15)" stroke={C.gold} strokeWidth={1}/>
      <text x={new_x+new_w-6-8} y={new_y+15} textAnchor="middle" fill={C.gold} fontSize={6} fontFamily={M}>MCP23017</text>
      {/* Space savings annotation */}
      <text x={new_x+new_w/2} y={new_y+new_h+16} textAnchor="middle" fill={C.lime} fontSize={8} fontFamily={M} fontWeight="bold">SENSORHAT-1 Rev H.1  46×36mm  ~11g</text>
      <text x={new_x+new_w/2} y={new_y+new_h/2+16} textAnchor="middle" fill="rgba(163,230,53,0.2)" fontSize={24} fontFamily={M}>1656</text>
      <text x={new_x+new_w/2} y={new_y+new_h/2+32} textAnchor="middle" fill="rgba(163,230,53,0.25)" fontSize={10} fontFamily={M}>mm²</text>

      {/* Reduction arrows and label */}
      <line x1={old_x+old_w+10} y1={old_y+old_h/2} x2={new_x-10} y2={new_y+new_h/2}
        stroke={C.green} strokeWidth={2} strokeDasharray="6 3"/>
      <text x={(old_x+old_w+10+new_x-10)/2} y={(old_y+old_h/2+new_y+new_h/2)/2-10}
        textAnchor="middle" fill={C.green} fontSize={10} fontFamily={M} fontWeight="bold">−55% area</text>
      <text x={(old_x+old_w+10+new_x-10)/2} y={(old_y+old_h/2+new_y+new_h/2)/2+6}
        textAnchor="middle" fill={C.green} fontSize={9} fontFamily={M}>−11g · same RP2350</text>

      <text x={VW/2} y={14} textAnchor="middle" fill="rgba(0,229,255,0.25)" fontSize={9} fontFamily={M} letterSpacing="0.1em">PCB FOOTPRINT COMPARISON — TRIHAT-1 vs SENSORHAT-1</text>
      <text x={VW/2} y={VH-6} textAnchor="middle" fill="rgba(0,229,255,0.2)" fontSize={7} fontFamily={M}>Both use RP2350A silicon — 100% firmware compatible · No capability loss</text>
    </svg>
  );
}

function XIAOEvalTab(){
  return(<div>
    <SH t="XIAO RP2350 vs Pico 2 — Decision Matrix" mt={0}/>
    <div style={{overflowX:"auto",marginBottom:20}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["CRITERION","PICO 2","XIAO RP2350","VERDICT"]}/>
        <tbody>{[
          ["MCU silicon","RP2350B (RP2350A on XIAO)","RP2350A","Same core · same PIO · same SPI/UART/I2C"],
          ["CPU speed","150MHz dual Cortex-M33","150MHz dual Cortex-M33","Identical"],
          ["SRAM","520 KB","520 KB","Identical"],
          ["Flash","4 MB","2 MB","⚠ Verify firmware fits · current FW ~180KB · OK"],
          ["GPIO on silicon","26","26","Identical"],
          ["GPIO exposed","26 (all)","26 (via castellated pads)","Identical with expander"],
          ["Package for hat","2× 20-pin header (through-hole)","Castellated SMD direct solder","XIAO wins — no headers · lower Z-height"],
          ["Board area (MCU only)","51×21mm = 1071mm²","21×17.5mm = 368mm²","XIAO: −66% area"],
          ["Hat board area","65×56mm = 3640mm²","46×36mm = 1656mm²","XIAO hat: −55% area"],
          ["Weight (MCU module)","~3g","~1.5g","XIAO: −1.5g"],
          ["Weight (total hat)","~22g","~11g","XIAO: −11g"],
          ["PIO state machines","3 blocks × 4 SM = 12 SM","3 blocks × 4 SM = 12 SM","Identical"],
          ["USB","Micro-USB","USB-C","XIAO better"],
          ["ADC","3× 12-bit","4× 12-bit","XIAO better (ESC telem ADC possible)"],
          ["Cost (MCU only)","$5","$6.30","XIAO +$1.30 — offset by smaller PCB"],
          ["Availability","Widely available","Widely available","Equal"],
          ["Firmware compat.","—","100% RP2350 compatible","Zero rewrite needed"],
          ["GPIO expander needed","No","Yes (MCP23017, $1.80)","Minor · +1 IC"],
        ].map((row,i)=>(
          <tr key={i} style={{background:i%2===0?"rgba(0,229,255,0.025)":"transparent"}}>
            <td style={{padding:"4px 9px",color:C.dim,whiteSpace:"nowrap"}}>{row[0]}</td>
            <td style={{padding:"4px 9px",color:C.accent,fontSize:9}}>{row[1]}</td>
            <td style={{padding:"4px 9px",color:C.lime,fontSize:9}}>{row[2]}</td>
            <td style={{padding:"4px 9px",color:row[3].includes("wins")||row[3].includes("better")||row[3].includes("XIAO")?C.green:row[3].includes("⚠")?C.yellow:C.dim,fontSize:9}}>{row[3]}</td>
          </tr>
        ))}</tbody>
      </table>
    </div>

    <SH t="Board Size Comparison" c={C.lime}/>
    <div style={{border:`1px solid ${C.lime}33`,borderRadius:4,background:"rgba(163,230,53,0.01)",padding:8,marginBottom:18}}>
      <BoardDiagram/>
    </div>

    <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:24}}>
      <div>
        <SH t="XIAO RP2350 Verdict: VIABLE ✔" mt={0} c={C.lime}/>
        <Good ch="XIAO RP2350 uses the identical RP2350A silicon as the Pico 2. Firmware is 100% compatible — same SDK, same PIO programs, same SPI/UART/I²C drivers. No rewrite needed."/>
        <Good ch="Adding MCP23017 I²C GPIO expander (4×4mm QFN, $1.80) handles the 7 non-time-critical outputs (servos, winch, ESC mux). Total GPIO coverage is identical to Pico 2, no functional regression."/>
        <Good ch="Flash at 2MB is sufficient. Current firmware estimate: MAVLink (~60KB) + PID (~30KB) + drivers (~80KB) + buffers (~10KB) = ~180KB total. 2MB provides 11× margin."/>
        <Note c={C.yellow} ch="One caution: the XIAO RP2350's 2MB flash has no external flash upgrade path without board modification. If firmware grows significantly (e.g., full DroneCAN stack + extensive logging), re-evaluate. As of Rev H.1 this is not a concern."/>
      </div>
      <div>
        <SH t="CM4 Carrier Minimization" mt={0} c={C.teal}/>
        <KV k="Minimum CM4 carrier width" v="57mm (CM4 module is 55mm + 1mm clearance each side)"/>
        <KV k="Current carrier (Rev E)" v="65×52mm = 3380mm²"/>
        <KV k="Target carrier (Rev H.1)" v="57×44mm = 2508mm² (−26%)"/>
        <KV k="Removable features" v="USB hub (GL850G) — not needed for flight operation"/>
        <KV k="Move to COMPHAT-1" v="CPLD write-blocker — already close to log μSD"/>
        <KV k="Shrink approach" v="Remove USB hub · tighten component placement · use 0402 everywhere"/>
        <KV k="Weight savings" v="~18g → ~13g (−5g)"/>
        <Note c={C.teal} ch="The CM4 module itself is 55×40mm, making 57mm the practical minimum carrier width. Length can be reduced by removing the USB hub (only needed for initial setup via development PC) and using a compact DC-DC instead of LDO for 5V→3.3V conversion."/>
        <Warn ch="The 2× Hirose DF40C-100 connectors are fixed at the CM4 module pin pitch and cannot be moved. They dominate the carrier length — minimum length with both DF40 connectors is ~44mm including edge clearance."/>
      </div>
    </div>
    <SH t="All Board Size Summary"/>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["BOARD","DIMENSIONS","AREA","WEIGHT","CHANGE","NOTES"]}/>
        <tbody>{BOARD_COMPARE.map((b,i)=>(
          <tr key={i} style={{background:b.note.includes("current")?"rgba(0,229,255,0.04)":b.note.includes("smaller")||b.note.includes("smaller")||b.note.includes("Min")?"rgba(163,230,53,0.04)":"rgba(0,229,255,0.02)",verticalAlign:"top"}}>
            <td style={{padding:"5px 9px",color:b.note.includes("smaller")||b.note.includes("Min")?C.lime:C.text,fontWeight:"bold",whiteSpace:"nowrap"}}>{b.board}</td>
            <td style={{padding:"5px 9px",color:C.yellow,whiteSpace:"nowrap"}}>{b.w}×{b.h}mm ({(b.w*0.03937).toFixed(1)}"×{(b.h*0.03937).toFixed(1)}")</td>
            <td style={{padding:"5px 9px",color:C.teal}}>{b.area.toLocaleString()}mm²</td>
            <td style={{padding:"5px 9px",color:C.green}}>{b.weight}g</td>
            <td style={{padding:"5px 9px",color:b.note.includes("smaller")||b.note.includes("Min")?C.lime:C.dim,fontSize:9}}>{b.note}</td>
            <td style={{padding:"5px 9px",color:C.dimmer,fontSize:9}}>{b.mcu}</td>
          </tr>
        ))}</tbody>
        <tfoot><tr style={{borderTop:`1px solid ${C.border}`}}>
          <td colSpan={2} style={{padding:"7px 9px",color:C.accent,textAlign:"right",fontSize:10}}>Net weight saved (SENSORHAT-1 + CARRIER-2)</td>
          <td colSpan={4} style={{padding:"7px 9px",color:C.green,fontWeight:"bold",fontSize:13}}>−16g total stack</td>
        </tr></tfoot>
      </table>
    </div>
  </div>);
}

// ════════════════════════════════════════════════════════════════
//  TAB 5: BOM DELTA
// ════════════════════════════════════════════════════════════════
const BOM_H1=[
  // XIAO swap
  {cat:"MCU",    qty:2, ref:"U_XIAO",   part:"Seeed XIAO RP2350",                   pkg:"21×17.5mm castell.",est:"$6.30ea",col:C.lime,note:"Replaces 2× Pico 2 ($5ea) · −55% PCB area · 100% FW compat"},
  {cat:"MCU",    qty:2, ref:"U_MCP23017",part:"MCP23017 I²C GPIO expander",          pkg:"QFN-28 4×4mm",est:"$1.80ea",col:C.gold,note:"16-bit expander · servos+winch+ESC mux select over I²C"},
  // ESC telemetry mux
  {cat:"ESC-Telem",qty:2,ref:"U_MUX",  part:"74HC4052 dual 4:1 analog mux",         pkg:"SOIC-16",est:"$0.40ea",col:C.teal,note:"Routes 3× ESC telem UART lines to single UART1 RX"},
  // Isolation ICs — replace existing
  {cat:"Isolation",qty:2,ref:"U_ISO_CAN",part:"ISO1042 isolated CAN FD transceiver", pkg:"SOIC-8",est:"$2.20ea",col:C.can, note:"Replaces MCP2562FD · 5kV · 5Mbps · pin-compatible"},
  {cat:"Isolation",qty:2,ref:"U_ISO_RS4",part:"ISO3086 isolated RS-485 transceiver", pkg:"SOIC-16",est:"$3.50ea",col:C.rs4, note:"Replaces MAX3485 · 3kV · integrated isolator"},
  {cat:"Isolation",qty:2,ref:"U_ISO_I2C",part:"ISO1540 isolated I²C bus buffer",     pkg:"SO-8",   est:"$2.80ea",col:C.i2c, note:"Replaces PCA9517 · 3kV · FM+ 1MHz"},
  {cat:"Isolation",qty:2,ref:"U_ISO_UART",part:"ISO7241C quad digital isolator",     pkg:"SOIC-16",est:"$2.50ea",col:C.uart,note:"4ch · 4kV · covers TX+RX+DE+RE on ESC/debug UART"},
  // Connectors — ESC telem (3 per SENSORHAT)
  {cat:"ESC-Telem",qty:6,ref:"J_ESC_TELEM",part:"JST-GH 1.25mm 3-pin ESC telem connector",pkg:"SMD",est:"$0.55ea",col:C.orange,note:"One per ESC · GND+TELEM_TX — 3 per SENSORHAT-1"},
  // Board cost savings (estimated)
  {cat:"PCB",    qty:1, ref:"PCB-SENSOR",part:"SENSORHAT-1 PCB 46×36mm 4-layer",    pkg:"JLCPCB",est:"~$4 for 5pcs",col:C.lime,note:"vs TRIHAT-1 65×56mm ~$6 for 5pcs · saves on area"},
  {cat:"PCB",    qty:1, ref:"PCB-CARRIER",part:"CARRIER-2 PCB 57×44mm 4-layer",     pkg:"JLCPCB",est:"~$5 for 5pcs",col:C.teal,note:"vs CM4-CARRIER-1 65×52mm ~$6 for 5pcs"},
  // Removed (credits)
  {cat:"REMOVED",qty:2, ref:"-PICO2",   part:"Raspberry Pi Pico 2 (removed)",        pkg:"—",est:"−$5ea",col:C.red,note:"Replaced by XIAO RP2350"},
  {cat:"REMOVED",qty:2, ref:"-MCP2562", part:"MCP2562FD CAN transceiver (removed)",  pkg:"—",est:"−$1ea",col:C.red,note:"Replaced by ISO1042"},
  {cat:"REMOVED",qty:2, ref:"-MAX3485", part:"MAX3485 RS-485 transceiver (removed)", pkg:"—",est:"−$0.80ea",col:C.red,note:"Replaced by ISO3086"},
  {cat:"REMOVED",qty:2, ref:"-PCA9517", part:"PCA9517 I²C buffer (removed)",         pkg:"—",est:"−$0.60ea",col:C.red,note:"Replaced by ISO1540"},
  {cat:"REMOVED",qty:1, ref:"-GL850G",  part:"GL850G USB hub (removed from carrier)", pkg:"—",est:"−$1.50",col:C.red,note:"Moved to lab setup tool only"},
];
const BOM_CATS_H1=[...new Set(BOM_H1.map(b=>b.cat))];
const CAT_COL_H1={MCU:C.lime,"ESC-Telem":C.teal,Isolation:C.iso,PCB:C.accent,REMOVED:C.red};

function BomTab(){
  const [cf,setCf]=useState("All");
  const rows=cf==="All"?BOM_H1:BOM_H1.filter(b=>b.cat===cf);
  const adds=BOM_H1.filter(b=>b.cat!=="REMOVED").reduce((s,b)=>{const u=parseFloat(b.est.replace("$","").replace("ea","").replace("~","").split(" ")[0])||0;return s+b.qty*u;},0);
  const subs=BOM_H1.filter(b=>b.cat==="REMOVED").reduce((s,b)=>{const u=parseFloat(b.est.replace("−$","").replace("ea",""))||0;return s+b.qty*u;},0);
  return(<div>
    <div style={{display:"grid",gridTemplateColumns:"repeat(3,1fr)",gap:12,marginBottom:16}}>
      {[{l:"New hardware cost",v:`~$${adds.toFixed(0)}`,c:C.yellow},{l:"Removed hardware savings",v:`~−$${subs.toFixed(0)}`,c:C.green},{l:"Net BOM delta",v:`~+$${(adds-subs).toFixed(0)}`,c:(adds-subs)<0?C.green:C.yellow}].map((s,i)=>(
        <div key={i} style={{padding:"10px 12px",border:`1px solid ${s.c}44`,background:`${s.c}07`,borderRadius:4}}>
          <div style={{color:C.dim,fontFamily:M,fontSize:9,marginBottom:3}}>{s.l}</div>
          <div style={{color:s.c,fontFamily:M,fontSize:20,fontWeight:"bold"}}>{s.v}</div>
        </div>
      ))}
    </div>
    <div style={{display:"flex",gap:5,flexWrap:"wrap",marginBottom:12}}>
      {["All",...BOM_CATS_H1].map(c=>(<button key={c} onClick={()=>setCf(c)} style={{background:cf===c?`${CAT_COL_H1[c]||C.accent}20`:"transparent",border:`1px solid ${cf===c?CAT_COL_H1[c]||C.accent:"rgba(0,229,255,0.14)"}`,color:cf===c?CAT_COL_H1[c]||C.accent:C.dimmer,padding:"3px 10px",fontFamily:M,fontSize:9,cursor:"pointer",borderRadius:2}}>{c}</button>))}
    </div>
    <div style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",fontFamily:M,fontSize:10}}>
        <TH cols={["CAT","QTY","REF","PART","PKG","UNIT COST","NOTES"]}/>
        <tbody>{rows.map((b,i)=>(<tr key={i} style={{background:b.cat==="REMOVED"?"rgba(248,113,113,0.04)":i%2===0?"rgba(0,229,255,0.02)":"transparent",verticalAlign:"top"}}>
          <td style={{padding:"5px 8px"}}><span style={{color:CAT_COL_H1[b.cat]||b.col,border:`1px solid ${CAT_COL_H1[b.cat]||b.col}40`,padding:"1px 5px",borderRadius:2,fontSize:9,whiteSpace:"nowrap"}}>{b.cat}</span></td>
          <td style={{padding:"5px 8px",color:b.cat==="REMOVED"?C.red:C.accent,fontWeight:"bold",textAlign:"center"}}>{b.cat==="REMOVED"?"−":""}{b.qty}</td>
          <td style={{padding:"5px 8px",color:C.yellow,fontSize:9,whiteSpace:"nowrap"}}>{b.ref}</td>
          <td style={{padding:"5px 8px",color:b.cat==="REMOVED"?C.red:C.text}}>{b.part}</td>
          <td style={{padding:"5px 8px",color:C.dimmer,whiteSpace:"nowrap",fontSize:9}}>{b.pkg}</td>
          <td style={{padding:"5px 8px",color:b.cat==="REMOVED"?C.red:C.green,fontWeight:"bold",whiteSpace:"nowrap"}}>{b.est}</td>
          <td style={{padding:"5px 8px",color:C.dim,fontSize:9}}>{b.note}</td>
        </tr>))}</tbody>
      </table>
    </div>
    <Note c={C.dim} ch="Net BOM delta is approximately +$15–20 per aircraft after XIAO savings. The majority of cost is the four isolation ICs ($11 total). Size and weight savings (−16g total, −55% sensor hat area) and the improved fault tolerance justify this cost."/>
  </div>);
}

// ════════════════════════════════════════════════════════════════
//  APP
// ════════════════════════════════════════════════════════════════
const TABS=["ESC Protocols","GPIO Audit","Bus Isolation","XIAO Evaluation","BOM Delta"];

export default function App(){
  const [tab,setTab]=useState("ESC Protocols");
  return(<div style={{minHeight:"100vh",background:C.bg,color:C.text,fontFamily:M}}>
    <Grid/>
    <div style={{background:"rgba(163,230,53,0.06)",borderBottom:`1px solid ${C.lime}22`,padding:"6px 24px",fontFamily:M,fontSize:8,color:`${C.lime}70`,lineHeight:1.6}}>
      © 2026 Steve Griffing, PE(CSE) [Control Systems Engineering], CISSP-ISSEP, CPP · CC BY 4.0 · Hull: Peter Farell CC BY 4.0 · Nozzle: BamJr CC BY 4.0 · Firefly/Serenity © Joss Whedon/Mutant Enemy/Universal — Fan engineering work
    </div>
    <div style={{position:"relative",zIndex:1,borderBottom:`1px solid ${C.border}`,padding:"14px 24px 12px"}}>
      <div style={{display:"flex",justifyContent:"space-between",alignItems:"flex-start",flexWrap:"wrap",gap:12}}>
        <div>
          <div style={{color:"rgba(0,229,255,0.28)",fontSize:9,letterSpacing:"0.2em",marginBottom:4}}>SERENITY TILTROTOR · ESC TELEMETRY + ISOLATION + BOARD REFACTOR · REV H.1</div>
          <h1 style={{margin:0,fontSize:18,fontWeight:"normal",color:"#fff",letterSpacing:"0.07em"}}>ESC TELEMETRY · FULL BUS ISOLATION · XIAO RP2350</h1>
          <div style={{color:"rgba(0,229,255,0.45)",fontSize:10,marginTop:3}}>
            BLHeli/AM32/BDSHOT/DroneCAN/KISS · ISO1042/ISO3086/ISO1540/ISO7241C · XIAO RP2350 · −16g · −55% hat area
          </div>
        </div>
        <div style={{textAlign:"right",fontFamily:M}}>
          <div style={{color:C.lime,fontSize:11,fontWeight:"bold"}}>SENSORHAT-1: 46×36mm · 11g</div>
          <div style={{color:C.teal,fontSize:11,marginTop:2}}>CARRIER-2: 57×44mm · 13g</div>
          <div style={{color:C.dimmer,fontSize:9,marginTop:2}}>All 6 buses isolated · ESC telem: all protocols via UART mux</div>
        </div>
      </div>
      <div style={{display:"flex",gap:2,marginTop:12,flexWrap:"wrap"}}>
        {TABS.map(t=>(<button key={t} onClick={()=>setTab(t)} style={{background:tab===t?"rgba(0,229,255,0.09)":"transparent",border:`1px solid ${tab===t?C.accent:"rgba(0,229,255,0.12)"}`,color:tab===t?C.accent:C.dimmer,padding:"4px 12px",fontFamily:M,fontSize:9,cursor:"pointer",letterSpacing:"0.06em",transition:"all 0.12s"}}>{t}</button>))}
      </div>
    </div>
    <div style={{position:"relative",zIndex:1,padding:"20px 24px",maxWidth:1060,margin:"0 auto"}}>
      {tab==="ESC Protocols"   && <ESCProtocolTab/>}
      {tab==="GPIO Audit"      && <GPIOAuditTab/>}
      {tab==="Bus Isolation"   && <IsolationTab/>}
      {tab==="XIAO Evaluation" && <XIAOEvalTab/>}
      {tab==="BOM Delta"       && <BomTab/>}
    </div>
  </div>);
}
