import { useState } from "react";

// ─── Design tokens ────────────────────────────────────────────────
const C = {
  bg:      "#07080d",
  panel:   "rgba(255,255,255,0.03)",
  border:  "rgba(0,229,255,0.14)",
  accent:  "#00e5ff",
  orange:  "#ff6b35",
  yellow:  "#ffe600",
  purple:  "#c084fc",
  green:   "#4ade80",
  red:     "#f87171",
  dim:     "rgba(255,255,255,0.38)",
  dimmer:  "rgba(255,255,255,0.22)",
  text:    "rgba(255,255,255,0.82)",
};

const mono = "'Courier New', 'Lucida Console', monospace";

// ─── Shared primitives ────────────────────────────────────────────
const Tag = ({ children, color = C.accent }) => (
  <span style={{ display:"inline-block", padding:"2px 7px", border:`1px solid ${color}`,
    color, fontSize:10, fontFamily:mono, borderRadius:2, marginRight:5, marginBottom:5, opacity:.85 }}>
    {children}
  </span>
);

const Row = ({ label, value, unit="", valueColor=C.text }) => (
  <div style={{ display:"flex", justifyContent:"space-between", alignItems:"baseline",
    padding:"5px 0", borderBottom:`1px solid rgba(0,229,255,0.07)` }}>
    <span style={{ color:C.dim, fontFamily:mono, fontSize:11 }}>{label}</span>
    <span style={{ color:valueColor, fontFamily:mono, fontSize:11 }}>
      {value}{unit && <span style={{ color:C.accent, marginLeft:4, fontSize:10 }}>{unit}</span>}
    </span>
  </div>
);

const SectionHead = ({ title }) => (
  <div style={{ display:"flex", alignItems:"center", gap:10, marginBottom:16, marginTop:28 }}>
    <div style={{ width:3, height:18, background:C.accent, flexShrink:0 }} />
    <span style={{ color:C.accent, fontFamily:mono, fontSize:13, letterSpacing:"0.14em",
      textTransform:"uppercase", fontWeight:"normal" }}>{title}</span>
  </div>
);

// ─── PCB SVG ──────────────────────────────────────────────────────
const COMPS = [
  { id:"U1", ref:"ICM-42688-P", desc:"6-DOF IMU · SPI0 shared bus",    x:105, y:130, w:52,  h:52,  color:C.accent,  bus:"SPI0" },
  { id:"U2", ref:"BMP388",      desc:"Barometer · I²C1",                x:215, y:130, w:44,  h:44,  color:C.accent,  bus:"I²C1" },
  { id:"U3", ref:"M10Q GPS",    desc:"u-blox M10Q module · UART0",      x:305, y:108, w:72,  h:68,  color:C.green,   bus:"UART0" },
  { id:"U4", ref:"MCP2518FD",   desc:"CAN FD controller · SPI0",        x:105, y:220, w:56,  h:48,  color:C.orange,  bus:"SPI0" },
  { id:"U5", ref:"MCP2562FD",   desc:"CAN FD transceiver · drives J3",  x:175, y:228, w:44,  h:36,  color:C.orange,  bus:"CAN" },
  { id:"U6", ref:"W5500",       desc:"Ethernet SPI · SPI1 · hardware TCP/IP", x:308, y:210, w:68,  h:56,  color:C.purple,  bus:"SPI1" },
  { id:"U7", ref:"HX1188NL",    desc:"Ethernet magnetics/transformer",  x:398, y:218, w:50,  h:40,  color:C.purple,  bus:"ETH" },
  { id:"U8", ref:"SLB9670",     desc:"TPM 2.0 · SPI0 shared bus",       x:215, y:220, w:50,  h:44,  color:C.yellow,  bus:"SPI0" },
  { id:"U9", ref:"AP2112K",     desc:"3.3V LDO · 600mA · ultra-low noise", x:116, y:310, w:42,  h:32,  color:C.dim,     bus:"PWR" },
  { id:"Y1", ref:"25MHz XTAL",  desc:"Clock for W5500",                 x:280, y:225, w:30,  h:24,  color:C.dimmer,  bus:"W5500" },
];

const JSTS = [
  // top edge
  { id:"J1", ref:"TELEM",   pins:6,  desc:"MAVLink / SiK radio · UART1",    x:80,  y:52,  horiz:true,  color:C.accent  },
  { id:"J2", ref:"CAN FD",  pins:4,  desc:"CAN FD bus · CANH/CANL",         x:220, y:52,  horiz:true,  color:C.orange  },
  { id:"J3", ref:"ETH",     pins:6,  desc:"100BASE-T Ethernet",              x:320, y:52,  horiz:true,  color:C.purple  },
  // right edge
  { id:"J4", ref:"FPV CAM", pins:6,  desc:"FPV camera · power + video + UART", x:480, y:118, horiz:false, color:C.orange  },
  { id:"J5", ref:"EXT GPS", pins:6,  desc:"External GPS fallback · UART0 alt", x:480, y:210, horiz:false, color:C.green   },
  // left edge
  { id:"J6", ref:"I²C EXT", pins:4,  desc:"External I²C peripherals",       x:52,  y:148, horiz:false, color:C.accent  },
  { id:"J7", ref:"DEBUG",   pins:4,  desc:"UART debug / console",            x:52,  y:240, horiz:false, color:C.yellow  },
  // bottom edge
  { id:"J8", ref:"PWR IN",  pins:4,  desc:"4S BEC in · +5V + GND",          x:230, y:368, horiz:true,  color:C.yellow  },
];

function PcbView({ selected, onSelect }) {
  const BW = 560, BH = 400;

  // Grid
  const gridLines = [];
  for (let x = 0; x <= BW; x += 20) gridLines.push(
    <line key={"gx"+x} x1={x} y1={0} x2={x} y2={BH} stroke="rgba(0,229,255,0.05)" strokeWidth={0.5} />
  );
  for (let y = 0; y <= BH; y += 20) gridLines.push(
    <line key={"gy"+y} x1={0} y1={y} x2={BW} y2={y} stroke="rgba(0,229,255,0.05)" strokeWidth={0.5} />
  );

  // Mounting holes
  const mholes = [[52,52],[52,348],[508,52],[508,348]];

  // Pico 2 socket outline (2×20 headers at bottom-center of board)
  const picoX = 68, picoY = 310, picoW = 380, picoH = 60;

  return (
    <svg viewBox={`0 0 ${BW} ${BH}`} width="100%" style={{ maxWidth:"100%", display:"block" }}>
      {/* Board fill */}
      <rect x={30} y={30} width={500} height={340} rx={8}
        fill="rgba(0,40,50,0.55)" stroke={C.accent} strokeWidth={1.5} />
      {/* Grid */}
      <g clipPath="url(#boardClip)">{gridLines}</g>
      <defs>
        <clipPath id="boardClip">
          <rect x={30} y={30} width={500} height={340} rx={8} />
        </clipPath>
      </defs>

      {/* Mounting holes */}
      {mholes.map(([cx,cy],i) => (
        <g key={i}>
          <circle cx={cx} cy={cy} r={7} fill="#07080d" stroke={C.accent} strokeWidth={1} opacity={0.6} />
          <circle cx={cx} cy={cy} r={3} fill="none" stroke={C.accent} strokeWidth={0.6} opacity={0.4} />
        </g>
      ))}

      {/* Pico 2 socket */}
      <rect x={picoX} y={picoY} width={picoW} height={picoH} rx={4}
        fill="rgba(0,229,255,0.04)" stroke="rgba(0,229,255,0.3)" strokeWidth={1} strokeDasharray="6 3" />
      <text x={picoX + picoW/2} y={picoY + 22} textAnchor="middle" fill="rgba(0,229,255,0.3)"
        fontSize={10} fontFamily={mono} letterSpacing="0.1em">RASPBERRY Pi PICO 2</text>
      <text x={picoX + picoW/2} y={picoY + 36} textAnchor="middle" fill="rgba(0,229,255,0.18)"
        fontSize={8} fontFamily={mono}>2×20 female header socket</text>
      {/* Header pin dots - top row */}
      {Array.from({length:20},(_,i) => (
        <circle key={"pt"+i} cx={picoX+12+i*18} cy={picoY+50} r={3}
          fill="rgba(255,200,0,0.3)" stroke="rgba(255,200,0,0.5)" strokeWidth={0.8} />
      ))}
      {/* Header pin dots - bottom row */}
      {Array.from({length:20},(_,i) => (
        <circle key={"pb"+i} cx={picoX+12+i*18} cy={picoY+10} r={3}
          fill="rgba(255,200,0,0.3)" stroke="rgba(255,200,0,0.5)" strokeWidth={0.8} />
      ))}

      {/* U.FL antenna */}
      <circle cx={460} cy={88} r={10} fill="rgba(76,222,128,0.1)"
        stroke={C.green} strokeWidth={1.2} strokeDasharray="3 2" />
      <text x={460} y={92} textAnchor="middle" fill={C.green} fontSize={7} fontFamily={mono}>U.FL</text>
      <text x={460} y={76} textAnchor="middle" fill="rgba(76,222,128,0.5)" fontSize={7} fontFamily={mono}>GPS ANT</text>

      {/* JST-GH Connectors */}
      {JSTS.map(j => {
        const isSelected = selected === j.id;
        const pw = j.horiz ? j.pins * 10 + 6 : 18;
        const ph = j.horiz ? 18 : j.pins * 10 + 6;
        const ox = j.horiz ? j.x - pw/2 : j.x - pw/2;
        const oy = j.horiz ? j.y - ph/2 : j.y - ph/2;
        return (
          <g key={j.id} onClick={() => onSelect(isSelected ? null : j.id)}
            style={{ cursor:"pointer" }}>
            <rect x={ox} y={oy} width={pw} height={ph} rx={3}
              fill={isSelected ? `${j.color}22` : `${j.color}11`}
              stroke={j.color} strokeWidth={isSelected ? 2 : 1.2} />
            {j.horiz
              ? Array.from({length:j.pins},(_,i) => (
                  <circle key={i} cx={ox+9+i*10} cy={j.y} r={3.5}
                    fill={j.color} opacity={0.4} />
                ))
              : Array.from({length:j.pins},(_,i) => (
                  <circle key={i} cx={j.x} cy={oy+9+i*10} r={3.5}
                    fill={j.color} opacity={0.4} />
                ))
            }
            <text x={j.x} y={j.horiz ? oy-5 : j.y}
              textAnchor="middle" dominantBaseline={j.horiz ? "auto" : "middle"}
              fill={j.color} fontSize={8} fontFamily={mono} fontWeight="bold">{j.ref}</text>
            <text x={j.x} y={j.horiz ? oy-14 : j.y+14}
              textAnchor="middle" dominantBaseline={j.horiz ? "auto" : "middle"}
              fill={j.color} fontSize={7} fontFamily={mono} opacity={0.6}>{j.id}</text>
          </g>
        );
      })}

      {/* ICs */}
      {COMPS.map(c => {
        const isSelected = selected === c.id;
        return (
          <g key={c.id} onClick={() => onSelect(isSelected ? null : c.id)}
            style={{ cursor:"pointer" }}>
            <rect x={c.x} y={c.y} width={c.w} height={c.h} rx={3}
              fill={isSelected ? `${c.color}20` : `${c.color}0d`}
              stroke={c.color} strokeWidth={isSelected ? 2 : 1}
              strokeDasharray={isSelected ? "0" : "0"} />
            {/* Pin-1 marker */}
            <circle cx={c.x+4} cy={c.y+4} r={2} fill={c.color} opacity={0.5} />
            <text x={c.x + c.w/2} y={c.y + c.h/2 - 5} textAnchor="middle"
              fill={c.color} fontSize={8} fontFamily={mono} fontWeight="bold">{c.id}</text>
            <text x={c.x + c.w/2} y={c.y + c.h/2 + 7} textAnchor="middle"
              fill={c.color} fontSize={7} fontFamily={mono} opacity={0.75}>{c.ref}</text>
          </g>
        );
      })}

      {/* Board label */}
      <text x={280} y={22} textAnchor="middle" fill="rgba(0,229,255,0.25)"
        fontSize={9} fontFamily={mono} letterSpacing="0.14em">TRIHAT-1 · PICO 2 SENSOR HAT · REV A</text>
      <text x={280} y={390} textAnchor="middle" fill="rgba(0,229,255,0.18)"
        fontSize={8} fontFamily={mono}>4-LAYER · 65mm × 48mm · 1oz Cu</text>

      {/* Copper area hint */}
      <rect x={31} y={31} width={498} height={338} rx={7}
        fill="none" stroke="rgba(0,229,255,0.06)" strokeWidth={3} />
    </svg>
  );
}

// ─── Detail panel ─────────────────────────────────────────────────
const COMP_DETAIL = {
  U1: { title:"ICM-42688-P IMU", color:C.accent, rows:[
    ["Interface","SPI0 (shared bus, GP16-19)"],["CS","GP17 (hw) – primary"],
    ["INT1","GP20"],["VDD","3.3V"],["Gyro noise","≤0.007°/s/√Hz"],
    ["Accel noise","≤70μg/√Hz"],["ODR","up to 32kHz"],["Notes","Vibration-damped mount recommended"],
  ]},
  U2: { title:"BMP388 Barometer", color:C.accent, rows:[
    ["Interface","I²C1 (GP2 SDA, GP3 SCL)"],["Address","0x76 (SDO → GND)"],
    ["Alt resolution","±0.5m"],["Max ODR","200Hz"],["VDD","3.3V"],
    ["Notes","100nF decoupling cap directly on VDD pin"],
  ]},
  U3: { title:"u-blox M10Q GPS", color:C.green, rows:[
    ["Interface","UART0 (GP0 TX→GPS RX, GP1 RX←GPS TX)"],
    ["Baud","115200 (default 9600, configure at init)"],
    ["PPS","GP6 (1Hz pulse for time sync)"],["nRST","GP7 (active-low reset)"],
    ["Antenna","On-board patch + U.FL for external"],
    ["GNSS","GPS + GLONASS + Galileo + BeiDou"],
    ["Update rate","up to 25Hz"],["CEP","<2.5m open sky"],
    ["Ext GPS","J5 connector routes UART0 when M10Q is depopulated"],
  ]},
  U4: { title:"MCP2518FD CAN FD Controller", color:C.orange, rows:[
    ["Interface","SPI0 shared (GP16-19)"],["CS","GP14 (software)"],
    ["INT","GP21"],["Speed","up to 8Mbps FD data phase"],
    ["Standard","ISO 11898-1:2015 CAN FD"],
    ["VDD","3.3V"],["Notes","32-byte TX/RX FIFO, time-stamp support"],
  ]},
  U5: { title:"MCP2562FD CAN FD Transceiver", color:C.orange, rows:[
    ["Interface","Driven by MCP2518FD"],["Bus","Connects to J2 CANH/CANL"],
    ["VDD","5V (VSYS) + 3.3V logic"],["STBY","GP23 (low = active)"],
    ["Speed","up to 8Mbps"],["ESD","±8kV HBM on bus pins"],
    ["TVS","SMAJ5.0A diodes on CANH/CANL"],
  ]},
  U6: { title:"W5500 Ethernet Controller", color:C.purple, rows:[
    ["Interface","SPI1 (GP8 MISO, GP9 CS, GP10 SCK, GP11 MOSI)"],
    ["INT","GP12"],["RST","GP13"],["Speed","SPI up to 80MHz"],
    ["TCP/IP","Hardware offload: TCP, UDP, ICMP, IPv4, ARP, IGMP, PPPoE"],
    ["Sockets","8 independent hardware sockets"],
    ["VDD","3.3V"],["Clock","25MHz XTAL (Y1 on-board)"],
    ["Notes","For ground-station config upload / log streaming"],
  ]},
  U7: { title:"HX1188NL Ethernet Magnetics", color:C.purple, rows:[
    ["Type","Integrated transformer + common-mode choke"],
    ["Ratio","1:1"],["Isolation","1500Vrms"],
    ["Connects","Between W5500 and J3 ETH connector"],
    ["Notes","Auto-MDIX handled by W5500"],
  ]},
  U8: { title:"SLB9670 TPM 2.0", color:C.yellow, rows:[
    ["Interface","SPI0 shared (GP16-19)"],["CS","GP15 (software)"],
    ["IRQ","GP22"],["Standard","TCG TPM 2.0 · ISO/IEC 11889"],
    ["Algorithms","RSA-2048, ECC P-256, SHA-256, AES-128"],
    ["Use","Firmware attestation, key storage, secure boot chain"],
    ["VDD","3.3V"],["Notes","Requires TPM2-tss or RP2350 secure boot tie-in"],
  ]},
  U9: { title:"AP2112K-3.3 LDO", color:C.dim, rows:[
    ["Output","3.3V ± 1%"],["Current","600mA max"],
    ["Input","5V from VSYS"],["Quiescent","55μA"],
    ["Noise","50μVrms (10Hz–100kHz)"],
    ["Notes","Powers all 3.3V sensors; separate from Pico's own LDO"],
  ]},
  Y1: { title:"25MHz Crystal (W5500 clock)", color:C.dimmer, rows:[
    ["Frequency","25.000MHz"],["Load cap","18pF"],
    ["PPM","±20ppm"],["Package","SMD 3225"],
  ]},
  J1: { title:"J1 · TELEM (6-pin JST-GH)", color:C.accent, rows:[
    ["Pin 1","GND"],["Pin 2","+5V"],["Pin 3","UART1 TX (GP4)"],
    ["Pin 4","UART1 RX (GP5)"],["Pin 5","CTS (GP6 alt / NC)"],
    ["Pin 6","RTS (GP7 alt / NC)"],
    ["Compatible","Pixhawk TELEM standard · SiK radio · ESP-MAVLink"],
  ]},
  J2: { title:"J2 · CAN FD (4-pin JST-GH)", color:C.orange, rows:[
    ["Pin 1","GND"],["Pin 2","+5V"],["Pin 3","CANH"],["Pin 4","CANL"],
    ["Compatible","Pixhawk CAN standard · DroneCAN / UAVCANv1"],
    ["Notes","120Ω termination resistor selectable via solder jumper"],
  ]},
  J3: { title:"J3 · ETH (6-pin JST-GH)", color:C.purple, rows:[
    ["Pin 1","GND"],["Pin 2","+3.3V"],["Pin 3","TX+"],
    ["Pin 4","TX−"],["Pin 5","RX+"],["Pin 6","RX−"],
    ["Notes","100BASE-T · magnetics on-board (U7) · use shielded JST-GH cable"],
  ]},
  J4: { title:"J4 · FPV CAM (6-pin JST-GH)", color:C.orange, rows:[
    ["Pin 1","GND"],["Pin 2","+5V (camera power)"],
    ["Pin 3","VID_IN (camera composite out)"],
    ["Pin 4","VID_OUT (to VTX, passthrough)"],
    ["Pin 5","CAM_TX (GP24 via PIO-UART)"],
    ["Pin 6","CAM_RX (GP25 via PIO-UART)"],
    ["Notes","Analog video passthrough — no ADC on Pico. PIO-UART for OSD/FC control. For digital cams (DJI/HDZero) use UART pins only; video coax goes direct to VTX."],
  ]},
  J5: { title:"J5 · EXT GPS (6-pin JST-GH)", color:C.green, rows:[
    ["Pin 1","GND"],["Pin 2","+3.3V"],["Pin 3","TX (GP0)"],
    ["Pin 4","RX (GP1)"],["Pin 5","PPS (GP6)"],["Pin 6","nRST (GP7)"],
    ["Notes","Solder jumper selects UART0 to on-board M10Q OR this connector. Populate one or the other."],
  ]},
  J6: { title:"J6 · I²C EXT (4-pin JST-GH)", color:C.accent, rows:[
    ["Pin 1","GND"],["Pin 2","+3.3V"],["Pin 3","SDA (GP2)"],["Pin 4","SCL (GP3)"],
    ["Notes","Shared with BMP388. 4.7kΩ pull-ups on board. Max 400kHz."],
  ]},
  J7: { title:"J7 · DEBUG UART (4-pin JST-GH)", color:C.yellow, rows:[
    ["Pin 1","GND"],["Pin 2","+3.3V"],["Pin 3","TX (GP0 or GP4)"],
    ["Pin 4","RX (GP1 or GP5)"],
    ["Notes","Solder jumper selects UART0 or UART1 routing to this port."],
  ]},
  J8: { title:"J8 · PWR IN (4-pin JST-GH)", color:C.yellow, rows:[
    ["Pin 1","GND"],["Pin 2","GND"],["Pin 3","+5V (from BEC)"],["Pin 4","+5V (from BEC)"],
    ["Notes","Reverse-polarity TVS diode on VSYS. Feeds Pico VSYS + LDO U9."],
  ]},
};

function DetailPanel({ id }) {
  if (!id || !COMP_DETAIL[id]) return (
    <div style={{ padding:"20px 16px", color:C.dimmer, fontFamily:mono, fontSize:11,
      border:`1px solid ${C.border}`, borderRadius:4, height:"100%", boxSizing:"border-box" }}>
      ← click a component or connector to inspect
    </div>
  );
  const d = COMP_DETAIL[id];
  return (
    <div style={{ padding:"16px", border:`1px solid ${d.color}44`, borderRadius:4,
      background:`${d.color}08`, height:"100%", boxSizing:"border-box", overflowY:"auto" }}>
      <div style={{ color:d.color, fontFamily:mono, fontSize:12, fontWeight:"bold",
        letterSpacing:"0.06em", marginBottom:12 }}>{d.title}</div>
      {d.rows.map(([k,v],i) => (
        <div key={i} style={{ display:"flex", gap:8, padding:"4px 0",
          borderBottom:`1px solid rgba(255,255,255,0.05)`, alignItems:"flex-start" }}>
          <span style={{ color:C.dim, fontFamily:mono, fontSize:10, minWidth:70, flexShrink:0 }}>{k}</span>
          <span style={{ color:C.text, fontFamily:mono, fontSize:10, lineHeight:1.6 }}>{v}</span>
        </div>
      ))}
    </div>
  );
}

// ─── Schematic block diagram ──────────────────────────────────────
function Schematic() {
  return (
    <svg viewBox="0 0 640 420" width="100%" style={{ maxWidth:"100%", display:"block" }}>
      {/* Central Pico 2 */}
      <rect x={235} y={155} width={170} height={110} rx={6}
        fill="rgba(0,229,255,0.08)" stroke={C.accent} strokeWidth={2} />
      <text x={320} y={180} textAnchor="middle" fill={C.accent} fontSize={11} fontFamily={mono} fontWeight="bold">PICO 2</text>
      <text x={320} y={196} textAnchor="middle" fill={C.accent} fontSize={9} fontFamily={mono}>RP2350 · dual-core</text>
      <text x={320} y={210} textAnchor="middle" fill="rgba(0,229,255,0.5)" fontSize={8} fontFamily={mono}>264KB RAM · 4MB Flash</text>
      <text x={320} y={224} textAnchor="middle" fill="rgba(0,229,255,0.5)" fontSize={8} fontFamily={mono}>3× PIO · 2× SPI · 2× I²C · 2× UART</text>
      <text x={320} y={238} textAnchor="middle" fill="rgba(0,229,255,0.4)" fontSize={8} fontFamily={mono}>ARM Cortex-M33 + RISC-V HAZARD3</text>
      <text x={320} y={252} textAnchor="middle" fill="rgba(0,229,255,0.4)" fontSize={8} fontFamily={mono}>Secure boot · TrustZone</text>

      {/* SPI0 bus line */}
      <line x1={235} y1={190} x2={180} y2={190} stroke={C.accent} strokeWidth={0.8} opacity={0.4} />
      <text x={200} y={185} fill="rgba(0,229,255,0.5)" fontSize={7} fontFamily={mono}>SPI0</text>

      {/* SPI1 bus line */}
      <line x1={405} y1={190} x2={460} y2={190} stroke={C.purple} strokeWidth={0.8} opacity={0.4} />
      <text x={420} y={185} fill="rgba(192,132,252,0.6)" fontSize={7} fontFamily={mono}>SPI1</text>

      {/* UART0 → GPS */}
      <line x1={320} y1={155} x2={320} y2={100} stroke={C.green} strokeWidth={0.8} strokeDasharray="4 2" opacity={0.6} />
      <text x={330} y={128} fill="rgba(74,222,128,0.6)" fontSize={7} fontFamily={mono}>UART0</text>

      {/* I2C1 → Baro */}
      <line x1={270} y1={155} x2={130} y2={90} stroke={C.accent} strokeWidth={0.8} strokeDasharray="4 2" opacity={0.4} />
      <text x={178} y={113} fill="rgba(0,229,255,0.5)" fontSize={7} fontFamily={mono}>I²C1</text>

      {/* UART1 → TELEM */}
      <line x1={280} y1={265} x2={280} y2={340} stroke={C.accent} strokeWidth={0.8} strokeDasharray="4 2" opacity={0.4} />
      <text x={290} y={305} fill="rgba(0,229,255,0.5)" fontSize={7} fontFamily={mono}>UART1</text>

      {/* PIO → FPV */}
      <line x1={405} y1={220} x2={560} y2={270} stroke={C.orange} strokeWidth={0.8} strokeDasharray="4 2" opacity={0.4} />
      <text x={488} y={245} fill="rgba(255,107,53,0.6)" fontSize={7} fontFamily={mono}>PIO-UART</text>

      {/* GPIO: CAN INT, GPS PPS, etc. */}
      <line x1={405} y1={250} x2={540} y2={200} stroke={C.orange} strokeWidth={0.6} strokeDasharray="3 3" opacity={0.3} />

      {/* IMU */}
      <rect x={22} y={155} width={80} height={50} rx={4}
        fill="rgba(0,229,255,0.07)" stroke={C.accent} strokeWidth={1.2} />
      <text x={62} y={176} textAnchor="middle" fill={C.accent} fontSize={9} fontFamily={mono} fontWeight="bold">ICM-42688-P</text>
      <text x={62} y={190} textAnchor="middle" fill="rgba(0,229,255,0.55)" fontSize={7} fontFamily={mono}>IMU · SPI0</text>
      <text x={62} y={202} textAnchor="middle" fill="rgba(0,229,255,0.4)" fontSize={7} fontFamily={mono}>CS: GP17</text>
      <line x1={102} y1={180} x2={130} y2={180} stroke={C.accent} strokeWidth={0.8} opacity={0.4} />

      {/* CAN FD */}
      <rect x={22} y={225} width={80} height={50} rx={4}
        fill="rgba(255,107,53,0.07)" stroke={C.orange} strokeWidth={1.2} />
      <text x={62} y={246} textAnchor="middle" fill={C.orange} fontSize={9} fontFamily={mono} fontWeight="bold">MCP2518FD</text>
      <text x={62} y={260} textAnchor="middle" fill="rgba(255,107,53,0.55)" fontSize={7} fontFamily={mono}>CAN FD · SPI0</text>
      <text x={62} y={272} textAnchor="middle" fill="rgba(255,107,53,0.4)" fontSize={7} fontFamily={mono}>CS: GP14</text>
      <line x1={102} y1={250} x2={130} y2={200} stroke={C.orange} strokeWidth={0.8} opacity={0.4} />

      {/* TPM */}
      <rect x={130} y={225} width={80} height={50} rx={4}
        fill="rgba(255,230,0,0.07)" stroke={C.yellow} strokeWidth={1.2} />
      <text x={170} y={246} textAnchor="middle" fill={C.yellow} fontSize={9} fontFamily={mono} fontWeight="bold">SLB9670</text>
      <text x={170} y={260} textAnchor="middle" fill="rgba(255,230,0,0.55)" fontSize={7} fontFamily={mono}>TPM 2.0 · SPI0</text>
      <text x={170} y={272} textAnchor="middle" fill="rgba(255,230,0,0.4)" fontSize={7} fontFamily={mono}>CS: GP15</text>
      <line x1={170} y1={225} x2={185} y2={190} stroke={C.yellow} strokeWidth={0.8} opacity={0.4} />

      {/* Baro */}
      <rect x={62} y={60} width={76} height={46} rx={4}
        fill="rgba(0,229,255,0.07)" stroke={C.accent} strokeWidth={1.2} />
      <text x={100} y={79} textAnchor="middle" fill={C.accent} fontSize={9} fontFamily={mono} fontWeight="bold">BMP388</text>
      <text x={100} y={93} textAnchor="middle" fill="rgba(0,229,255,0.55)" fontSize={7} fontFamily={mono}>Barometer · I²C1</text>
      <text x={100} y={104} textAnchor="middle" fill="rgba(0,229,255,0.4)" fontSize={7} fontFamily={mono}>addr 0x76</text>

      {/* GPS module */}
      <rect x={268} y={52} width={104} height={60} rx={4}
        fill="rgba(74,222,128,0.07)" stroke={C.green} strokeWidth={1.2} />
      <text x={320} y={73} textAnchor="middle" fill={C.green} fontSize={9} fontFamily={mono} fontWeight="bold">u-blox M10Q</text>
      <text x={320} y={87} textAnchor="middle" fill="rgba(74,222,128,0.55)" fontSize={7} fontFamily={mono}>GPS · UART0</text>
      <text x={320} y={100} textAnchor="middle" fill="rgba(74,222,128,0.4)" fontSize={7} fontFamily={mono}>PPS: GP6 · nRST: GP7</text>

      {/* W5500 */}
      <rect x={460} y={150} width={90} height={56} rx={4}
        fill="rgba(192,132,252,0.07)" stroke={C.purple} strokeWidth={1.2} />
      <text x={505} y={171} textAnchor="middle" fill={C.purple} fontSize={9} fontFamily={mono} fontWeight="bold">W5500</text>
      <text x={505} y={185} textAnchor="middle" fill="rgba(192,132,252,0.55)" fontSize={7} fontFamily={mono}>Ethernet · SPI1</text>
      <text x={505} y={198} textAnchor="middle" fill="rgba(192,132,252,0.4)" fontSize={7} fontFamily={mono}>CS: GP9</text>
      <line x1={460} y1={178} x2={430} y2={178} stroke={C.purple} strokeWidth={0.8} opacity={0.4} />

      {/* Magnetics + ETH connector */}
      <rect x={460} y={220} width={90} height={46} rx={4}
        fill="rgba(192,132,252,0.05)" stroke={C.purple} strokeWidth={1} strokeDasharray="4 2" />
      <text x={505} y={239} textAnchor="middle" fill={C.purple} fontSize={8} fontFamily={mono}>HX1188NL</text>
      <text x={505} y={252} textAnchor="middle" fill="rgba(192,132,252,0.4)" fontSize={7} fontFamily={mono}>Magnetics</text>
      <line x1={505} y1={220} x2={505} y2={206} stroke={C.purple} strokeWidth={0.8} opacity={0.4} />
      <rect x={468} y={278} width={74} height={26} rx={3}
        fill="rgba(192,132,252,0.08)" stroke={C.purple} strokeWidth={1} />
      <text x={505} y={295} textAnchor="middle" fill={C.purple} fontSize={8} fontFamily={mono}>J3 · ETH</text>
      <line x1={505} y1={278} x2={505} y2={266} stroke={C.purple} strokeWidth={0.8} opacity={0.4} />

      {/* TELEM connector */}
      <rect x={220} y={340} width={80} height={26} rx={3}
        fill="rgba(0,229,255,0.07)" stroke={C.accent} strokeWidth={1} />
      <text x={260} y={357} textAnchor="middle" fill={C.accent} fontSize={8} fontFamily={mono}>J1 · TELEM</text>
      <line x1={260} y1={340} x2={275} y2={280} stroke={C.accent} strokeWidth={0.8} opacity={0.4} />

      {/* FPV CAM connector */}
      <rect x={536} y={262} width={80} height={26} rx={3}
        fill="rgba(255,107,53,0.07)" stroke={C.orange} strokeWidth={1} />
      <text x={576} y={279} textAnchor="middle" fill={C.orange} fontSize={8} fontFamily={mono}>J4 · FPV CAM</text>

      {/* Power */}
      <rect x={22} y={330} width={72} height={46} rx={4}
        fill="rgba(255,230,0,0.06)" stroke={C.yellow} strokeWidth={1.2} />
      <text x={58} y={349} textAnchor="middle" fill={C.yellow} fontSize={8} fontFamily={mono} fontWeight="bold">AP2112K</text>
      <text x={58} y={362} textAnchor="middle" fill="rgba(255,230,0,0.5)" fontSize={7} fontFamily={mono}>3.3V LDO</text>
      <text x={58} y={373} textAnchor="middle" fill="rgba(255,230,0,0.35)" fontSize={7} fontFamily={mono}>J8 PWR IN →</text>

      <text x={320} y={415} textAnchor="middle" fill="rgba(0,229,255,0.2)"
        fontSize={8} fontFamily={mono}>TRIHAT-1 · FUNCTIONAL BLOCK DIAGRAM</text>
    </svg>
  );
}

// ─── GPIO Map tab ─────────────────────────────────────────────────
const GPIO_ROWS = [
  { pin:"GP0",     fn:"UART0 TX",   dev:"→ u-blox M10Q RX",         bus:"UART0",  color:C.green  },
  { pin:"GP1",     fn:"UART0 RX",   dev:"← u-blox M10Q TX",         bus:"UART0",  color:C.green  },
  { pin:"GP2",     fn:"I²C1 SDA",   dev:"BMP388 barometer",          bus:"I²C1",   color:C.accent },
  { pin:"GP3",     fn:"I²C1 SCL",   dev:"BMP388 barometer",          bus:"I²C1",   color:C.accent },
  { pin:"GP4",     fn:"UART1 TX",   dev:"J1 TELEM → SiK radio",      bus:"UART1",  color:C.accent },
  { pin:"GP5",     fn:"UART1 RX",   dev:"J1 TELEM ← SiK radio",      bus:"UART1",  color:C.accent },
  { pin:"GP6",     fn:"GPIO IN",    dev:"GPS PPS (1Hz time sync)",    bus:"GPIO",   color:C.green  },
  { pin:"GP7",     fn:"GPIO OUT",   dev:"GPS nRESET (active-low)",    bus:"GPIO",   color:C.green  },
  { pin:"GP8",     fn:"SPI1 RX",    dev:"W5500 MISO",                 bus:"SPI1",   color:C.purple },
  { pin:"GP9",     fn:"SPI1 CSn",   dev:"W5500 CS (hw)",              bus:"SPI1",   color:C.purple },
  { pin:"GP10",    fn:"SPI1 SCK",   dev:"W5500 SCLK",                 bus:"SPI1",   color:C.purple },
  { pin:"GP11",    fn:"SPI1 TX",    dev:"W5500 MOSI",                 bus:"SPI1",   color:C.purple },
  { pin:"GP12",    fn:"GPIO IN",    dev:"W5500 INT (active-low)",      bus:"GPIO",   color:C.purple },
  { pin:"GP13",    fn:"GPIO OUT",   dev:"W5500 RST (active-low)",      bus:"GPIO",   color:C.purple },
  { pin:"GP14",    fn:"GPIO OUT",   dev:"MCP2518FD CS (software)",    bus:"SPI0",   color:C.orange },
  { pin:"GP15",    fn:"GPIO OUT",   dev:"SLB9670 TPM CS (software)",  bus:"SPI0",   color:C.yellow },
  { pin:"GP16",    fn:"SPI0 RX",    dev:"IMU / CAN / TPM shared MISO",bus:"SPI0",   color:C.accent },
  { pin:"GP17",    fn:"SPI0 CSn",   dev:"ICM-42688-P CS (hw)",        bus:"SPI0",   color:C.accent },
  { pin:"GP18",    fn:"SPI0 SCK",   dev:"IMU / CAN / TPM shared CLK", bus:"SPI0",   color:C.accent },
  { pin:"GP19",    fn:"SPI0 TX",    dev:"IMU / CAN / TPM shared MOSI",bus:"SPI0",   color:C.accent },
  { pin:"GP20",    fn:"GPIO IN",    dev:"ICM-42688-P INT1",           bus:"GPIO",   color:C.accent },
  { pin:"GP21",    fn:"GPIO IN",    dev:"MCP2518FD INT",              bus:"GPIO",   color:C.orange },
  { pin:"GP22",    fn:"GPIO IN",    dev:"SLB9670 TPM IRQ",            bus:"GPIO",   color:C.yellow },
  { pin:"GP23",    fn:"GPIO OUT",   dev:"MCP2562FD STBY (low=active)","bus":"GPIO", color:C.orange },
  { pin:"GP24",    fn:"PIO UART TX","dev":"J4 FPV cam OSD TX",        bus:"PIO",    color:C.orange },
  { pin:"GP25",    fn:"PIO UART RX","dev":"J4 FPV cam OSD RX",        bus:"PIO",    color:C.orange },
  { pin:"GP26/A0", fn:"ADC0",       dev:"VBAT monitor (÷11 divider)",  bus:"ADC",    color:C.yellow },
  { pin:"GP27/A1", fn:"ADC1",       dev:"RSSI analog input",          bus:"ADC",    color:C.yellow },
  { pin:"GP28/A2", fn:"ADC2",       dev:"Board temp / spare",         bus:"ADC",    color:C.dim    },
];

function GpioTab() {
  const busColors = {};
  GPIO_ROWS.forEach(r => busColors[r.bus] = r.color);
  return (
    <div style={{ overflowX:"auto" }}>
      <table style={{ width:"100%", borderCollapse:"collapse", fontFamily:mono, fontSize:11 }}>
        <thead>
          <tr>{["GPIO","FUNCTION","CONNECTED TO","BUS"].map(h => (
            <th key={h} style={{ padding:"6px 10px", borderBottom:`1px solid ${C.border}`,
              color:C.accent, textAlign:"left", fontWeight:"normal", fontSize:10,
              letterSpacing:"0.08em", opacity:0.8 }}>{h}</th>
          ))}</tr>
        </thead>
        <tbody>
          {GPIO_ROWS.map((r,i) => (
            <tr key={i} style={{ background: i%2===0 ? "rgba(0,229,255,0.025)" : "transparent" }}>
              <td style={{ padding:"5px 10px", color:C.yellow, fontFamily:mono }}>{r.pin}</td>
              <td style={{ padding:"5px 10px", color:C.dim }}>{r.fn}</td>
              <td style={{ padding:"5px 10px", color:C.text }}>{r.dev}</td>
              <td style={{ padding:"5px 10px" }}>
                <span style={{ color:r.color, border:`1px solid ${r.color}`, padding:"1px 6px",
                  fontSize:9, borderRadius:2 }}>{r.bus}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ─── BOM tab ──────────────────────────────────────────────────────
const BOM_ROWS = [
  { qty:1,  ref:"U1",  part:"ICM-42688-P",           pkg:"LGA-14",     desc:"6-DOF IMU, SPI, ±16g/±2000°/s",              usd:"$8" },
  { qty:1,  ref:"U2",  part:"BMP388",                 pkg:"LGA-8",      desc:"Barometer, I²C/SPI, ±0.5m alt resolution",    usd:"$4" },
  { qty:1,  ref:"U3",  part:"u-blox M10Q",            pkg:"Module",     desc:"GPS/GNSS module, UART, onboard patch ant",     usd:"$22"},
  { qty:1,  ref:"U4",  part:"MCP2518FD",              pkg:"SOIC-20",    desc:"CAN FD controller, SPI, ISO 11898-1:2015",     usd:"$4" },
  { qty:1,  ref:"U5",  part:"MCP2562FD",              pkg:"SOIC-8",     desc:"CAN FD transceiver, 8Mbps, 5V bus",            usd:"$2" },
  { qty:1,  ref:"U6",  part:"W5500",                  pkg:"LQFP-48",    desc:"Ethernet SPI controller, hw TCP/IP",           usd:"$3" },
  { qty:1,  ref:"U7",  part:"HX1188NL",               pkg:"SMD",        desc:"Ethernet magnetics, 1:1, 1500Vrms isolation",  usd:"$2" },
  { qty:1,  ref:"U8",  part:"SLB9670 (Infineon)",     pkg:"SOP-8",      desc:"TPM 2.0, SPI, RSA-2048/ECC/AES/SHA",          usd:"$6" },
  { qty:1,  ref:"U9",  part:"AP2112K-3.3",            pkg:"SOT-25",     desc:"3.3V LDO, 600mA, ultra-low noise",             usd:"$1" },
  { qty:1,  ref:"Y1",  part:"25MHz Crystal",          pkg:"SMD 3225",   desc:"W5500 reference clock, ±20ppm",                usd:"$0.50"},
  { qty:8,  ref:"J1-8",part:"JST-GH (1.25mm pitch)",  pkg:"SMD",        desc:"4/6-pin as per connector spec (assorted)",     usd:"$0.60 ea"},
  { qty:1,  ref:"ANT1",part:"U.FL connector",         pkg:"SMD",        desc:"For external GPS antenna",                     usd:"$0.50"},
  { qty:2,  ref:"TVS1-2",part:"SMAJ5.0A TVS",        pkg:"SMA",        desc:"Bus ESD protection, CAN CANH/CANL lines",      usd:"$0.50 ea"},
  { qty:1,  ref:"R-div",part:"Resistor network",      pkg:"0402 ×4",    desc:"VBAT divider 100k/10k + pull-ups 4.7k ×2",    usd:"$0.50"},
  { qty:1,  ref:"C-dec",part:"Decoupling caps",        pkg:"0402 ×20",   desc:"100nF/1μF/10μF per IC supply pin",             usd:"$1"},
  { qty:1,  ref:"PCB", part:"4-layer PCB 65×48mm",    pkg:"—",          desc:"JLC/OSHPark, 1oz Cu, ENIG finish",             usd:"$12"},
  { qty:1,  ref:"—",   part:"2×20 female header",     pkg:"2.54mm",     desc:"For Pico 2 socket (tall, stackable optional)", usd:"$1"},
];

function BomTab() {
  const total = "~$75";
  return (
    <div style={{ overflowX:"auto" }}>
      <table style={{ width:"100%", borderCollapse:"collapse", fontFamily:mono, fontSize:11 }}>
        <thead>
          <tr>{["QTY","REF","PART","PKG","DESCRIPTION","USD"].map(h => (
            <th key={h} style={{ padding:"6px 10px", borderBottom:`1px solid ${C.border}`,
              color:C.accent, textAlign:"left", fontWeight:"normal", fontSize:10,
              letterSpacing:"0.08em", opacity:0.8, whiteSpace:"nowrap" }}>{h}</th>
          ))}</tr>
        </thead>
        <tbody>
          {BOM_ROWS.map((r,i) => (
            <tr key={i} style={{ background: i%2===0 ? "rgba(0,229,255,0.025)" : "transparent" }}>
              <td style={{ padding:"5px 10px", color:C.accent, fontWeight:"bold" }}>{r.qty}</td>
              <td style={{ padding:"5px 10px", color:C.dim, whiteSpace:"nowrap" }}>{r.ref}</td>
              <td style={{ padding:"5px 10px", color:C.text, whiteSpace:"nowrap" }}>{r.part}</td>
              <td style={{ padding:"5px 10px", color:C.dimmer, whiteSpace:"nowrap" }}>{r.pkg}</td>
              <td style={{ padding:"5px 10px", color:C.dim, fontSize:10 }}>{r.desc}</td>
              <td style={{ padding:"5px 10px", color:C.yellow, whiteSpace:"nowrap" }}>{r.usd}</td>
            </tr>
          ))}
          <tr style={{ borderTop:`1px solid ${C.border}` }}>
            <td colSpan={5} style={{ padding:"8px 10px", color:C.accent, textAlign:"right",
              fontFamily:mono, fontSize:11 }}>ESTIMATED TOTAL (excl. Pico 2)</td>
            <td style={{ padding:"8px 10px", color:C.yellow, fontWeight:"bold", fontSize:14,
              fontFamily:mono }}>{total}</td>
          </tr>
        </tbody>
      </table>
      <div style={{ marginTop:16, color:C.dimmer, fontFamily:mono, fontSize:10, lineHeight:1.9 }}>
        · JLCPCB 4-layer estimate at 5-piece quantity. ENIG finish recommended for QFN/LGA pads.<br/>
        · MCP2518FD + MCP2562FD available as SOIC for hand-soldering; QFN variants exist if space critical.<br/>
        · SLB9670 is Infineon; ATTPM20P (Microchip) is pin-compatible SPI-TPM 2.0 alternative.<br/>
        · u-blox M10Q is a complete module (≈9.6×9.6mm) — no additional matching network needed.<br/>
        · W5500 requires 25MHz XTAL; onboard crystal Y1 handles this. No external clock source needed.
      </div>
    </div>
  );
}

// ─── Notes tab ────────────────────────────────────────────────────
function NotesTab() {
  const notes = [
    { heading:"SPI0 Shared-Bus Design", color:C.accent, body:"ICM-42688-P, MCP2518FD, and SLB9670 share SPI0 (GP16-19). Each gets a dedicated software chip-select (GP14, GP15, GP17). ICM-42688-P uses the hardware CSn (GP17) for fastest transactions; the others use software-toggled GPIOs. Route SPI0 as a short star topology with stubs under 15mm to avoid reflections at 24MHz." },
    { heading:"FPV Camera Interface", color:C.orange, body:"Analog FPV cameras output composite video (NTSC/PAL). The hat is a passive passthrough: VID_IN from the camera JST-GH connects directly to VID_OUT to the VTX JST-GH — no ADC or processing occurs on the Pico. Power (+5V) is switched via a small P-channel FET controlled by GP24 so the camera can be power-cycled in firmware. For OSD or digital camera control (DJI O3, Caddx Vista, HDZero), use the PIO-UART lines (GP24/25)." },
    { heading:"CAN FD Bus", color:C.orange, body:"MCP2518FD supports both Classical CAN (1Mbps) and CAN FD (up to 8Mbps data phase). The MCP2562FD transceiver is a 3.3V-logic / 5V-bus split-supply device. CANH and CANL are protected by SMAJ5.0A TVS diodes. A 120Ω termination resistor is footprinted with a solder bridge JP1 — populate only if this node is a bus endpoint. Supports DroneCAN / UAVCANv1 for ESC, GPS, and airspeed sensor integration." },
    { heading:"Ethernet Use Case", color:C.purple, body:"W5500 provides hardware TCP/IP offload with 8 independent sockets. On a drone, Ethernet is primarily useful for: (1) pre-flight log upload / config over a tethered connection, (2) direct UDP streaming to a ground station laptop on the same subnet, (3) integration with companion computers (RPi, Jetson) over a short cable. Not intended for airborne wireless — pair with a WiFi-to-Ethernet bridge module if needed. The W5500 runs up to 80MHz SPI, leaving most of SPI1 bandwidth headroom." },
    { heading:"TPM 2.0 Integration", color:C.yellow, body:"The SLB9670 provides hardware-backed key storage and attestation. With RP2350's TrustZone-M, the Pico 2 can boot into a secure world, derive keys from the TPM, and attest firmware integrity before running the flight control loop. Practical uses: encrypted MAVLink streams, signed firmware updates, flight log tamper detection. Requires TPM 2.0 software stack — port tpm2-tss lightweight library or use Infineon's embedded TPM API." },
    { heading:"Power Architecture", color:C.yellow, body:"VSYS rail (+5V from BEC via J8) feeds: Pico 2 VSYS pin, MCP2562FD VBUS, and AP2112K-3.3 input. The AP2112K derives a clean 3.3V for all sensors (IMU, baro, GPS, W5500, TPM, CAN controller). A 100μF bulk cap on VSYS and 10μF + 100nF per IC. VBAT (raw LiPo) is monitored via GP26/ADC0 through a 100k/10k divider (×0.091 ratio, 16.8V max → 1.53V at ADC). Never connect raw LiPo to any IC supply pin." },
    { heading:"PCB Stackup", color:C.dim, body:"4-layer: TOP (signals + components), GND plane (layer 2), PWR plane (layer 3), BOTTOM (signals). Keep IMU routing on TOP with ground guard ring. Route SPI0 and SPI1 on separate layers where they cross. Place 100nF decoupling caps within 0.5mm of each IC supply pin on TOP layer. GPS module requires a keepout from digital clock traces to maintain RF sensitivity — place on top-center with U.FL at board edge." },
  ];
  return (
    <div>
      {notes.map((n,i) => (
        <div key={i} style={{ marginBottom:20, padding:"14px 16px",
          border:`1px solid ${n.color}22`, borderLeft:`3px solid ${n.color}`,
          background:`${n.color}06`, borderRadius:4 }}>
          <div style={{ color:n.color, fontFamily:mono, fontSize:11, fontWeight:"bold",
            letterSpacing:"0.08em", marginBottom:8 }}>{n.heading}</div>
          <p style={{ color:C.dim, fontFamily:mono, fontSize:11, lineHeight:1.8, margin:0 }}>{n.body}</p>
        </div>
      ))}
    </div>
  );
}

// ─── App shell ────────────────────────────────────────────────────
const TABS = ["PCB Layout","Schematic","GPIO Map","BOM","Design Notes"];

export default function App() {
  const [tab, setTab] = useState("PCB Layout");
  const [selected, setSelected] = useState(null);

  return (
    <div style={{ minHeight:"100vh", background:C.bg, color:C.text, fontFamily:mono }}>
      {/* BG grid */}
      <svg style={{ position:"fixed", inset:0, width:"100%", height:"100%", pointerEvents:"none", zIndex:0 }}>
        <defs>
          <pattern id="g1" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="rgba(0,229,255,0.04)" strokeWidth={0.5} />
          </pattern>
          <pattern id="g2" width="100" height="100" patternUnits="userSpaceOnUse">
            <rect width="100" height="100" fill="url(#g1)" />
            <path d="M 100 0 L 0 0 0 100" fill="none" stroke="rgba(0,229,255,0.08)" strokeWidth={1} />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#g2)" />
      </svg>

      {/* Header */}
      <div style={{ position:"relative", zIndex:1, borderBottom:`1px solid ${C.border}`,
        padding:"20px 28px 16px" }}>
        <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start",
          flexWrap:"wrap", gap:12 }}>
          <div>
            <div style={{ color:"rgba(0,229,255,0.35)", fontSize:9, letterSpacing:"0.2em", marginBottom:5 }}>
              HARDWARE DESIGN SPECIFICATION · TRIHAT-1 REV A
            </div>
            <h1 style={{ margin:0, fontSize:20, fontWeight:"normal", color:"#fff",
              letterSpacing:"0.07em" }}>PICO 2 SENSOR HAT</h1>
            <div style={{ color:"rgba(0,229,255,0.55)", fontSize:10, marginTop:5 }}>
              IMU · Baro · GPS · FPV · TPM 2.0 · CAN FD · 100BASE-T Ethernet · JST-GH
            </div>
          </div>
          <div style={{ textAlign:"right" }}>
            <div style={{ color:C.orange, fontSize:12, marginBottom:4 }}>65mm × 48mm · 4-layer</div>
            <div style={{ color:C.dimmer, fontSize:9 }}>RP2350 compatible · ENIG finish</div>
          </div>
        </div>
        <div style={{ display:"flex", gap:2, marginTop:16, flexWrap:"wrap" }}>
          {TABS.map(t => (
            <button key={t} onClick={() => setTab(t)} style={{
              background: tab===t ? "rgba(0,229,255,0.1)" : "transparent",
              border: `1px solid ${tab===t ? C.accent : "rgba(0,229,255,0.15)"}`,
              color: tab===t ? C.accent : C.dimmer,
              padding:"5px 13px", fontFamily:mono, fontSize:10, cursor:"pointer",
              letterSpacing:"0.07em", transition:"all 0.12s" }}>{t}</button>
          ))}
        </div>
      </div>

      {/* Body */}
      <div style={{ position:"relative", zIndex:1, padding:"24px 28px",
        maxWidth:980, margin:"0 auto" }}>

        {tab === "PCB Layout" && (
          <div>
            <div style={{ display:"grid", gridTemplateColumns:"1fr 280px", gap:20, alignItems:"start" }}>
              <div>
                <div style={{ color:C.dimmer, fontSize:10, letterSpacing:"0.1em", marginBottom:10 }}>
                  CLICK COMPONENT OR CONNECTOR TO INSPECT · top-down view · not to scale
                </div>
                <div style={{ border:`1px solid ${C.border}`, borderRadius:4,
                  background:"rgba(0,229,255,0.02)", padding:8 }}>
                  <PcbView selected={selected} onSelect={setSelected} />
                </div>
                <div style={{ marginTop:10, display:"flex", flexWrap:"wrap", gap:8 }}>
                  {[
                    [C.accent,"IMU · Baro · Pico"],
                    [C.green, "GPS"],
                    [C.orange,"CAN FD · FPV"],
                    [C.purple,"Ethernet"],
                    [C.yellow,"TPM 2.0 · Power"],
                  ].map(([c,l]) => (
                    <span key={l} style={{ display:"flex", alignItems:"center", gap:5,
                      color:C.dimmer, fontSize:9 }}>
                      <span style={{ width:10, height:10, background:c, opacity:0.7, display:"inline-block" }} />
                      {l}
                    </span>
                  ))}
                </div>
              </div>
              <div style={{ position:"sticky", top:20 }}>
                <div style={{ color:C.dimmer, fontSize:10, letterSpacing:"0.1em", marginBottom:10 }}>
                  COMPONENT INSPECTOR
                </div>
                <DetailPanel id={selected} />
                {!selected && (
                  <div style={{ marginTop:16 }}>
                    <div style={{ color:C.dimmer, fontSize:10, marginBottom:8, letterSpacing:"0.08em" }}>
                      QUICK SPECS
                    </div>
                    <Row label="Board size" value="65 × 48" unit="mm" />
                    <Row label="PCB layers" value="4-layer" unit="" />
                    <Row label="Cu weight" value="1oz" unit="" />
                    <Row label="Min trace" value="0.1" unit="mm" />
                    <Row label="Min via" value="0.2/0.4" unit="mm drill/pad" />
                    <Row label="Finish" value="ENIG" unit="" />
                    <Row label="Mount holes" value="M2.5 × 4" unit="(20×20mm)" />
                    <Row label="Connectors" value="8×" unit="JST-GH 1.25mm" />
                    <Row label="3.3V LDO" value="600" unit="mA" />
                    <Row label="Total ICs" value="9" unit="on-board" />
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {tab === "Schematic" && (
          <div>
            <div style={{ border:`1px solid ${C.border}`, borderRadius:4,
              background:"rgba(0,229,255,0.015)", padding:12 }}>
              <Schematic />
            </div>
            <div style={{ marginTop:16, color:C.dimmer, fontSize:10, lineHeight:1.9 }}>
              SPI0 shared bus (GP16-19) services IMU, CAN FD controller, and TPM via independent software chip-selects.
              SPI1 (GP8-11) is dedicated to W5500 Ethernet at up to 80MHz.
              UART0 connects to the onboard M10Q GPS module (solder-jumper allows re-routing to J5 for external GPS).
              UART1 is routed to J1 for the MAVLink SiK radio.
              PIO state machines on GP24/25 implement a third software UART for FPV camera OSD/control.
            </div>
          </div>
        )}

        {tab === "GPIO Map" && <GpioTab />}
        {tab === "BOM"       && <BomTab />}
        {tab === "Design Notes" && <NotesTab />}
      </div>

      <div style={{ position:"relative", zIndex:1, borderTop:`1px solid ${C.border}`,
        padding:"12px 28px", display:"flex", justifyContent:"space-between",
        flexWrap:"wrap", gap:6 }}>
        <span style={{ color:"rgba(0,229,255,0.2)", fontSize:8, letterSpacing:"0.12em" }}>
          TRIHAT-1 · PICO 2 SENSOR HAT · REV A
        </span>
        <span style={{ color:"rgba(0,229,255,0.2)", fontSize:8, letterSpacing:"0.1em" }}>
          REFERENCE DESIGN ONLY · VERIFY BEFORE FABRICATION
        </span>
      </div>
    </div>
  );
}
