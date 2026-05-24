import { useState } from "react";

const SECTIONS = ["Overview", "Airframe", "Propulsion", "Avionics", "Control Logic", "BOM"];

const accent = "#00e5ff";
const accent2 = "#ff6b35";
const gridLine = "rgba(0,229,255,0.07)";

function BlueprintGrid() {
  return (
    <svg style={{ position: "fixed", inset: 0, width: "100%", height: "100%", pointerEvents: "none", zIndex: 0 }} xmlns="http://www.w3.org/2000/svg">
      <defs>
        <pattern id="smallGrid" width="24" height="24" patternUnits="userSpaceOnUse">
          <path d="M 24 0 L 0 0 0 24" fill="none" stroke={gridLine} strokeWidth="0.5" />
        </pattern>
        <pattern id="bigGrid" width="120" height="120" patternUnits="userSpaceOnUse">
          <rect width="120" height="120" fill="url(#smallGrid)" />
          <path d="M 120 0 L 0 0 0 120" fill="none" stroke="rgba(0,229,255,0.12)" strokeWidth="1" />
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#bigGrid)" />
    </svg>
  );
}

function TopView() {
  return (
    <svg viewBox="0 0 400 200" width="100%" style={{ maxWidth: 480 }} xmlns="http://www.w3.org/2000/svg">
      {/* Fuselage */}
      <ellipse cx="200" cy="100" rx="60" ry="18" fill="rgba(0,229,255,0.08)" stroke={accent} strokeWidth="1.5" />
      {/* Wings */}
      <rect x="60" y="93" width="280" height="14" rx="3" fill="rgba(0,229,255,0.05)" stroke={accent} strokeWidth="1.2" />
      {/* Left nacelle ring */}
      <ellipse cx="68" cy="100" rx="18" ry="18" fill="rgba(255,107,53,0.1)" stroke={accent2} strokeWidth="1.5" strokeDasharray="4 2" />
      <ellipse cx="68" cy="100" rx="10" ry="10" fill="rgba(255,107,53,0.15)" stroke={accent2} strokeWidth="1" />
      <text x="68" y="104" textAnchor="middle" fill={accent2} fontSize="7" fontFamily="monospace">FAN L</text>
      {/* Right nacelle ring */}
      <ellipse cx="332" cy="100" rx="18" ry="18" fill="rgba(255,107,53,0.1)" stroke={accent2} strokeWidth="1.5" strokeDasharray="4 2" />
      <ellipse cx="332" cy="100" rx="10" ry="10" fill="rgba(255,107,53,0.15)" stroke={accent2} strokeWidth="1" />
      <text x="332" y="104" textAnchor="middle" fill={accent2} fontSize="7" fontFamily="monospace">FAN R</text>
      {/* Nose fan */}
      <ellipse cx="200" cy="100" rx="9" ry="9" fill="rgba(255,255,0,0.12)" stroke="#ffe600" strokeWidth="1.2" strokeDasharray="3 2" />
      <text x="200" y="103" textAnchor="middle" fill="#ffe600" fontSize="6" fontFamily="monospace">FWD</text>
      {/* Nose */}
      <path d="M200,85 Q230,82 260,100 Q230,118 200,115" fill="rgba(0,229,255,0.06)" stroke={accent} strokeWidth="1" />
      {/* Tail */}
      <path d="M200,85 Q170,82 140,100 Q170,118 200,115" fill="rgba(0,229,255,0.04)" stroke={accent} strokeWidth="0.7" />
      {/* Tilt arc indicators */}
      <path d="M54,82 A18,18 0 0,1 82,82" fill="none" stroke={accent2} strokeWidth="1" strokeDasharray="3 2" />
      <path d="M318,82 A18,18 0 0,1 346,82" fill="none" stroke={accent2} strokeWidth="1" strokeDasharray="3 2" />
      <text x="68" y="76" textAnchor="middle" fill={accent2} fontSize="6" fontFamily="monospace">±90°</text>
      <text x="332" y="76" textAnchor="middle" fill={accent2} fontSize="6" fontFamily="monospace">±90°</text>
      {/* Labels */}
      <text x="200" y="18" textAnchor="middle" fill={accent} fontSize="9" fontFamily="monospace" opacity="0.7">TOP VIEW</text>
      <text x="200" y="190" textAnchor="middle" fill="rgba(0,229,255,0.4)" fontSize="7" fontFamily="monospace">WINGSPAN: 680mm</text>
      {/* dim lines */}
      <line x1="50" y1="165" x2="350" y2="165" stroke={accent} strokeWidth="0.5" opacity="0.3" />
      <line x1="50" y1="162" x2="50" y2="168" stroke={accent} strokeWidth="0.5" opacity="0.3" />
      <line x1="350" y1="162" x2="350" y2="168" stroke={accent} strokeWidth="0.5" opacity="0.3" />
    </svg>
  );
}

function SideView() {
  return (
    <svg viewBox="0 0 400 180" width="100%" style={{ maxWidth: 480 }} xmlns="http://www.w3.org/2000/svg">
      {/* Fuselage side */}
      <ellipse cx="200" cy="95" rx="80" ry="22" fill="rgba(0,229,255,0.06)" stroke={accent} strokeWidth="1.5" />
      {/* Canopy */}
      <ellipse cx="215" cy="85" rx="30" ry="10" fill="rgba(0,229,255,0.12)" stroke={accent} strokeWidth="1" />
      {/* Wing stump */}
      <rect x="165" y="87" width="70" height="8" rx="2" fill="rgba(0,229,255,0.08)" stroke={accent} strokeWidth="1" />
      {/* Nacelle hover position (vertical) */}
      <rect x="103" y="55" width="22" height="38" rx="5" fill="rgba(255,107,53,0.1)" stroke={accent2} strokeWidth="1.5" />
      <text x="114" y="97" textAnchor="middle" fill={accent2} fontSize="6" fontFamily="monospace">HOVER</text>
      {/* Nacelle cruise position (horizontal, dashed) */}
      <rect x="103" y="80" width="38" height="18" rx="5" fill="none" stroke={accent2} strokeWidth="1" strokeDasharray="4 2" opacity="0.5" />
      <text x="122" y="93" textAnchor="middle" fill={accent2} fontSize="6" fontFamily="monospace" opacity="0.5">CRUISE</text>
      {/* Fuselage longitudinal fan */}
      <ellipse cx="280" cy="95" rx="10" ry="10" fill="rgba(255,230,0,0.12)" stroke="#ffe600" strokeWidth="1.2" strokeDasharray="3 2" />
      <text x="280" y="98" textAnchor="middle" fill="#ffe600" fontSize="6" fontFamily="monospace">FWD</text>
      {/* Landing legs */}
      <line x1="160" y1="117" x2="145" y2="138" stroke={accent} strokeWidth="1.2" opacity="0.5" />
      <line x1="240" y1="117" x2="255" y2="138" stroke={accent} strokeWidth="1.2" opacity="0.5" />
      <line x1="135" y1="138" x2="175" y2="138" stroke={accent} strokeWidth="1.5" opacity="0.5" />
      <line x1="235" y1="138" x2="275" y2="138" stroke={accent} strokeWidth="1.5" opacity="0.5" />
      {/* Labels */}
      <text x="200" y="18" textAnchor="middle" fill={accent} fontSize="9" fontFamily="monospace" opacity="0.7">SIDE VIEW</text>
      <text x="200" y="168" textAnchor="middle" fill="rgba(0,229,255,0.4)" fontSize="7" fontFamily="monospace">FUSELAGE LENGTH: 320mm</text>
    </svg>
  );
}

function BlockDiagram() {
  return (
    <svg viewBox="0 0 500 320" width="100%" xmlns="http://www.w3.org/2000/svg" style={{ maxWidth: 560 }}>
      {/* Central Pico 2 */}
      <rect x="195" y="130" width="110" height="60" rx="6" fill="rgba(0,229,255,0.1)" stroke={accent} strokeWidth="2" />
      <text x="250" y="155" textAnchor="middle" fill={accent} fontSize="10" fontFamily="monospace" fontWeight="bold">PICO 2</text>
      <text x="250" y="170" textAnchor="middle" fill={accent} fontSize="8" fontFamily="monospace">RP2350</text>
      <text x="250" y="183" textAnchor="middle" fill="rgba(0,229,255,0.5)" fontSize="7" fontFamily="monospace">264KB RAM / 4MB Flash</text>

      {/* IMU */}
      <rect x="30" y="55" width="90" height="40" rx="4" fill="rgba(0,229,255,0.07)" stroke={accent} strokeWidth="1.2" />
      <text x="75" y="72" textAnchor="middle" fill={accent} fontSize="9" fontFamily="monospace">IMU</text>
      <text x="75" y="86" textAnchor="middle" fill="rgba(0,229,255,0.6)" fontSize="7" fontFamily="monospace">ICM-42688-P</text>
      <line x1="120" y1="75" x2="195" y2="150" stroke={accent} strokeWidth="0.8" opacity="0.4" strokeDasharray="4 2" />
      <text x="145" y="107" fill="rgba(0,229,255,0.5)" fontSize="6" fontFamily="monospace">SPI</text>

      {/* Baro */}
      <rect x="30" y="120" width="90" height="40" rx="4" fill="rgba(0,229,255,0.07)" stroke={accent} strokeWidth="1.2" />
      <text x="75" y="137" textAnchor="middle" fill={accent} fontSize="9" fontFamily="monospace">BARO</text>
      <text x="75" y="151" textAnchor="middle" fill="rgba(0,229,255,0.6)" fontSize="7" fontFamily="monospace">BMP388</text>
      <line x1="120" y1="140" x2="195" y2="160" stroke={accent} strokeWidth="0.8" opacity="0.4" strokeDasharray="4 2" />
      <text x="143" y="147" fill="rgba(0,229,255,0.5)" fontSize="6" fontFamily="monospace">I²C</text>

      {/* GPS */}
      <rect x="30" y="185" width="90" height="40" rx="4" fill="rgba(0,229,255,0.07)" stroke={accent} strokeWidth="1.2" />
      <text x="75" y="202" textAnchor="middle" fill={accent} fontSize="9" fontFamily="monospace">GPS</text>
      <text x="75" y="216" textAnchor="middle" fill="rgba(0,229,255,0.6)" fontSize="7" fontFamily="monospace">M10 / UART</text>
      <line x1="120" y1="205" x2="195" y2="170" stroke={accent} strokeWidth="0.8" opacity="0.4" strokeDasharray="4 2" />
      <text x="141" y="183" fill="rgba(0,229,255,0.5)" fontSize="6" fontFamily="monospace">UART0</text>

      {/* MAVLink Radio */}
      <rect x="30" y="250" width="90" height="40" rx="4" fill="rgba(0,229,255,0.07)" stroke={accent} strokeWidth="1.2" />
      <text x="75" y="267" textAnchor="middle" fill={accent} fontSize="9" fontFamily="monospace">SiK RADIO</text>
      <text x="75" y="281" textAnchor="middle" fill="rgba(0,229,255,0.6)" fontSize="7" fontFamily="monospace">MAVLink 2.0</text>
      <line x1="120" y1="270" x2="195" y2="185" stroke={accent} strokeWidth="0.8" opacity="0.4" strokeDasharray="4 2" />
      <text x="140" y="218" fill="rgba(0,229,255,0.5)" fontSize="6" fontFamily="monospace">UART1</text>

      {/* Left ESC + Fan */}
      <rect x="360" y="40" width="110" height="40" rx="4" fill="rgba(255,107,53,0.1)" stroke={accent2} strokeWidth="1.2" />
      <text x="415" y="57" textAnchor="middle" fill={accent2} fontSize="9" fontFamily="monospace">ESC-L + FAN-L</text>
      <text x="415" y="71" textAnchor="middle" fill="rgba(255,107,53,0.6)" fontSize="7" fontFamily="monospace">BLDC / 40mm duct</text>
      <line x1="305" y1="145" x2="360" y2="60" stroke={accent2} strokeWidth="0.8" opacity="0.5" strokeDasharray="4 2" />
      <text x="340" y="94" fill="rgba(255,107,53,0.6)" fontSize="6" fontFamily="monospace">PWM/DSHOT</text>

      {/* Right ESC + Fan */}
      <rect x="360" y="120" width="110" height="40" rx="4" fill="rgba(255,107,53,0.1)" stroke={accent2} strokeWidth="1.2" />
      <text x="415" y="137" textAnchor="middle" fill={accent2} fontSize="9" fontFamily="monospace">ESC-R + FAN-R</text>
      <text x="415" y="151" textAnchor="middle" fill="rgba(255,107,53,0.6)" fontSize="7" fontFamily="monospace">BLDC / 40mm duct</text>
      <line x1="305" y1="158" x2="360" y2="140" stroke={accent2} strokeWidth="0.8" opacity="0.5" strokeDasharray="4 2" />

      {/* Fwd ESC + Fan */}
      <rect x="360" y="200" width="110" height="40" rx="4" fill="rgba(255,230,0,0.1)" stroke="#ffe600" strokeWidth="1.2" />
      <text x="415" y="217" textAnchor="middle" fill="#ffe600" fontSize="9" fontFamily="monospace">ESC-F + FAN-F</text>
      <text x="415" y="231" textAnchor="middle" fill="rgba(255,230,0,0.6)" fontSize="7" fontFamily="monospace">BLDC / 30mm duct</text>
      <line x1="305" y1="170" x2="360" y2="220" stroke="#ffe600" strokeWidth="0.8" opacity="0.5" strokeDasharray="4 2" />

      {/* Tilt Servos */}
      <rect x="360" y="270" width="110" height="40" rx="4" fill="rgba(180,100,255,0.1)" stroke="#b46fff" strokeWidth="1.2" />
      <text x="415" y="287" textAnchor="middle" fill="#b46fff" fontSize="9" fontFamily="monospace">TILT SERVOS ×2</text>
      <text x="415" y="301" textAnchor="middle" fill="rgba(180,100,255,0.6)" fontSize="7" fontFamily="monospace">MG90S / PWM</text>
      <line x1="305" y1="183" x2="360" y2="285" stroke="#b46fff" strokeWidth="0.8" opacity="0.5" strokeDasharray="4 2" />

      {/* Power Bus */}
      <rect x="195" y="255" width="110" height="40" rx="4" fill="rgba(255,200,0,0.07)" stroke="#ffc800" strokeWidth="1.2" />
      <text x="250" y="272" textAnchor="middle" fill="#ffc800" fontSize="9" fontFamily="monospace">POWER BUS</text>
      <text x="250" y="286" textAnchor="middle" fill="rgba(255,200,0,0.6)" fontSize="7" fontFamily="monospace">4S LiPo / 5V BEC</text>
      <line x1="250" y1="255" x2="250" y2="190" stroke="#ffc800" strokeWidth="0.8" opacity="0.4" strokeDasharray="3 2" />
    </svg>
  );
}

function FlightModeTable() {
  const rows = [
    { mode: "VTOL HOVER", nacelles: "90° (vertical)", fwd: "Trim/Yaw assist", roll: "Diff. thrust L/R", pitch: "Fwd fan ± nacelle tilt", yaw: "Diff. thrust L/R" },
    { mode: "TRANSITION", nacelles: "0–90° sweep", fwd: "Increasing", roll: "Diff. thrust", pitch: "Nacelle angle", yaw: "Nacelle differential" },
    { mode: "CRUISE", nacelles: "0° (horizontal)", fwd: "Primary thrust", roll: "Diff. nacelle thrust", pitch: "Nacelle tilt ±5°", yaw: "Differential" },
  ];
  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontFamily: "monospace", fontSize: 12 }}>
        <thead>
          <tr>
            {["MODE", "NACELLES", "FWD FAN", "ROLL", "PITCH", "YAW"].map(h => (
              <th key={h} style={{ padding: "6px 10px", borderBottom: `1px solid ${accent}`, color: accent, textAlign: "left", fontWeight: "normal", fontSize: 10, letterSpacing: "0.08em", opacity: 0.8 }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} style={{ background: i % 2 === 0 ? "rgba(0,229,255,0.03)" : "transparent" }}>
              <td style={{ padding: "8px 10px", color: accent2, fontWeight: "bold", fontSize: 11, whiteSpace: "nowrap" }}>{r.mode}</td>
              <td style={{ padding: "8px 10px", color: "rgba(255,255,255,0.7)", fontSize: 11 }}>{r.nacelles}</td>
              <td style={{ padding: "8px 10px", color: "rgba(255,255,255,0.7)", fontSize: 11 }}>{r.fwd}</td>
              <td style={{ padding: "8px 10px", color: "rgba(255,255,255,0.7)", fontSize: 11 }}>{r.roll}</td>
              <td style={{ padding: "8px 10px", color: "rgba(255,255,255,0.7)", fontSize: 11 }}>{r.pitch}</td>
              <td style={{ padding: "8px 10px", color: "rgba(255,255,255,0.7)", fontSize: 11 }}>{r.yaw}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function PinoutTable() {
  const pins = [
    { pin: "GP0/1", fn: "UART0 TX/RX", dev: "GPS (u-blox M10)" },
    { pin: "GP4/5", fn: "UART1 TX/RX", dev: "SiK MAVLink Radio" },
    { pin: "GP6/7", fn: "I²C1 SDA/SCL", dev: "BMP388 Barometer" },
    { pin: "GP10/11/12/13", fn: "SPI1", dev: "ICM-42688-P IMU" },
    { pin: "GP14", fn: "PWM7A", dev: "ESC Left (Fan-L)" },
    { pin: "GP15", fn: "PWM7B", dev: "ESC Right (Fan-R)" },
    { pin: "GP16", fn: "PWM0A", dev: "ESC Forward (Fan-F)" },
    { pin: "GP17", fn: "PWM0B", dev: "Servo Left Nacelle" },
    { pin: "GP18", fn: "PWM1A", dev: "Servo Right Nacelle" },
    { pin: "GP25", fn: "LED", dev: "Status / Arm indicator" },
    { pin: "3V3", fn: "3.3V rail", dev: "IMU, Baro logic" },
    { pin: "VSYS", fn: "5V BEC in", dev: "Pico power + Radio" },
  ];
  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontFamily: "monospace", fontSize: 11 }}>
        <thead>
          <tr>
            {["PIN / BUS", "FUNCTION", "DEVICE"].map(h => (
              <th key={h} style={{ padding: "6px 10px", borderBottom: `1px solid ${accent}`, color: accent, textAlign: "left", fontWeight: "normal", fontSize: 10, letterSpacing: "0.08em", opacity: 0.8 }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {pins.map((p, i) => (
            <tr key={i} style={{ background: i % 2 === 0 ? "rgba(0,229,255,0.03)" : "transparent" }}>
              <td style={{ padding: "6px 10px", color: "#ffe600", fontFamily: "monospace", fontSize: 11 }}>{p.pin}</td>
              <td style={{ padding: "6px 10px", color: "rgba(255,255,255,0.6)", fontSize: 11 }}>{p.fn}</td>
              <td style={{ padding: "6px 10px", color: accent2, fontSize: 11 }}>{p.dev}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function BOMTable() {
  const items = [
    { qty: 1, part: "Raspberry Pi Pico 2", spec: "RP2350, dual-core Cortex-M33 / RISC-V, 264KB SRAM", est: "$5" },
    { qty: 2, part: "Ducted Fan 40mm", spec: "11-blade BLDC, ~180g thrust @ 4S, duct shroud + stator", est: "$18 ea" },
    { qty: 1, part: "Ducted Fan 30mm", spec: "7-blade BLDC, ~80g thrust @ 4S, longitudinal fwd mount", est: "$12" },
    { qty: 3, part: "ESC 20A BLHeli_S", spec: "DSHOT300 capable, 2–4S, compact (BLHeli_S or AM32)", est: "$10 ea" },
    { qty: 2, part: "Digital Servo MG90S", spec: "Metal gear, 1.8kg·cm, 180°, for nacelle tilt", est: "$4 ea" },
    { qty: 1, part: "ICM-42688-P IMU", spec: "6-DOF, ±16g / ±2000°/s, SPI up to 24MHz", est: "$8" },
    { qty: 1, part: "BMP388 Barometer", spec: "±0.5m altitude resolution, I²C, up to 200Hz ODR", est: "$4" },
    { qty: 1, part: "u-blox M10 GPS", spec: "10Hz, multi-band GNSS, UART, <2m CEP", est: "$22" },
    { qty: 1, part: "SiK Telemetry 915MHz", spec: "MAVLink 2.0 native, 100mW, UART TTL, air+ground unit", est: "$30" },
    { qty: 1, part: "4S 1300mAh LiPo", spec: "14.8V, 75C burst, XT30 connector, ~100g", est: "$20" },
    { qty: 1, part: "5V 3A BEC", spec: "Switching, low-noise, for Pico + servos + radio", est: "$5" },
    { qty: 1, part: "Carbon fibre tube / sheet", spec: "12mm tubes (wing spars), 2mm plate (frame)", est: "$15" },
    { qty: 1, part: "3D printed PLA/PETG", spec: "Fuselage shell, nacelle pivots, duct mounts", est: "$8" },
  ];
  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontFamily: "monospace", fontSize: 11 }}>
        <thead>
          <tr>
            {["QTY", "COMPONENT", "SPECIFICATION", "~USD"].map(h => (
              <th key={h} style={{ padding: "6px 10px", borderBottom: `1px solid ${accent}`, color: accent, textAlign: "left", fontWeight: "normal", fontSize: 10, letterSpacing: "0.08em", opacity: 0.8 }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {items.map((item, i) => (
            <tr key={i} style={{ background: i % 2 === 0 ? "rgba(0,229,255,0.03)" : "transparent" }}>
              <td style={{ padding: "6px 10px", color: accent, fontSize: 12, fontWeight: "bold" }}>{item.qty}</td>
              <td style={{ padding: "6px 10px", color: "rgba(255,255,255,0.9)", fontSize: 11 }}>{item.part}</td>
              <td style={{ padding: "6px 10px", color: "rgba(255,255,255,0.5)", fontSize: 10 }}>{item.spec}</td>
              <td style={{ padding: "6px 10px", color: "#ffe600", fontSize: 11, whiteSpace: "nowrap" }}>{item.est}</td>
            </tr>
          ))}
          <tr style={{ borderTop: `1px solid rgba(0,229,255,0.3)` }}>
            <td colSpan={3} style={{ padding: "8px 10px", color: accent, fontSize: 11, textAlign: "right" }}>ESTIMATED TOTAL</td>
            <td style={{ padding: "8px 10px", color: "#ffe600", fontWeight: "bold", fontSize: 13 }}>~$170</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}

function Spec({ label, value, unit }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", padding: "6px 0", borderBottom: "1px solid rgba(0,229,255,0.08)" }}>
      <span style={{ color: "rgba(255,255,255,0.45)", fontFamily: "monospace", fontSize: 11, letterSpacing: "0.05em" }}>{label}</span>
      <span style={{ color: "rgba(255,255,255,0.9)", fontFamily: "monospace", fontSize: 12 }}>{value} <span style={{ color: accent, fontSize: 10 }}>{unit}</span></span>
    </div>
  );
}

function Tag({ children, color = accent }) {
  return (
    <span style={{ display: "inline-block", padding: "2px 8px", border: `1px solid ${color}`, color, fontSize: 10, fontFamily: "monospace", borderRadius: 2, marginRight: 6, marginBottom: 6, opacity: 0.85 }}>{children}</span>
  );
}

function Section({ title, children }) {
  return (
    <div style={{ marginBottom: 40 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 20 }}>
        <div style={{ width: 3, height: 20, background: accent, flexShrink: 0 }} />
        <h2 style={{ margin: 0, color: accent, fontFamily: "'Courier New', monospace", fontSize: 14, letterSpacing: "0.15em", textTransform: "uppercase", fontWeight: "normal" }}>{title}</h2>
      </div>
      {children}
    </div>
  );
}

export default function App() {
  const [activeTab, setActiveTab] = useState("Overview");

  return (
    <div style={{ minHeight: "100vh", background: "#060d13", color: "rgba(255,255,255,0.85)", position: "relative", overflowX: "hidden" }}>
      <BlueprintGrid />

      {/* Header */}
      <div style={{ position: "relative", zIndex: 1, borderBottom: "1px solid rgba(0,229,255,0.15)", padding: "24px 32px 20px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 12 }}>
          <div>
            <div style={{ color: "rgba(0,229,255,0.45)", fontFamily: "monospace", fontSize: 10, letterSpacing: "0.2em", marginBottom: 6 }}>DESIGN SPECIFICATION · REV 1.0</div>
            <h1 style={{ margin: 0, fontFamily: "'Courier New', monospace", fontSize: 22, fontWeight: "normal", color: "#fff", letterSpacing: "0.08em" }}>
              TRI-FAN TILTROTOR UAV
            </h1>
            <div style={{ color: "rgba(0,229,255,0.6)", fontFamily: "monospace", fontSize: 11, marginTop: 6 }}>
              2× Tilting Wing Nacelles · 1× Fixed Longitudinal Fan · Pico 2 · MAVLink
            </div>
          </div>
          <div style={{ textAlign: "right" }}>
            <div style={{ color: "rgba(0,229,255,0.35)", fontFamily: "monospace", fontSize: 9, letterSpacing: "0.1em" }}>AIRFRAME CLASS</div>
            <div style={{ color: accent2, fontFamily: "monospace", fontSize: 13, marginTop: 4 }}>VTOL · MICRO UAV</div>
            <div style={{ color: "rgba(255,255,255,0.3)", fontFamily: "monospace", fontSize: 9, marginTop: 4 }}>AUW ≈ 420g</div>
          </div>
        </div>

        {/* Nav tabs */}
        <div style={{ display: "flex", gap: 2, marginTop: 20, flexWrap: "wrap" }}>
          {SECTIONS.map(s => (
            <button key={s} onClick={() => setActiveTab(s)} style={{
              background: activeTab === s ? "rgba(0,229,255,0.12)" : "transparent",
              border: `1px solid ${activeTab === s ? accent : "rgba(0,229,255,0.18)"}`,
              color: activeTab === s ? accent : "rgba(255,255,255,0.4)",
              padding: "6px 14px", fontFamily: "monospace", fontSize: 11, cursor: "pointer",
              letterSpacing: "0.08em", transition: "all 0.15s"
            }}>{s}</button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div style={{ position: "relative", zIndex: 1, padding: "32px", maxWidth: 900, margin: "0 auto" }}>

        {activeTab === "Overview" && (
          <div>
            <Section title="Concept">
              <p style={{ color: "rgba(255,255,255,0.6)", fontFamily: "monospace", fontSize: 12, lineHeight: 1.8, marginTop: 0 }}>
                A micro VTOL UAV combining two wing-tip ducted fans on independent rotating nacelles with a fixed-axis longitudinal fan embedded in the fuselage. The nacelle fans handle lift, roll, and yaw in hover by differential thrust and angle; they transition to forward-thrust propulsors in cruise. The fuselage fan provides supplemental forward thrust in cruise and pitch/yaw trim authority in hover. The three-fan triad eliminates the need for control surfaces entirely.
              </p>
              <div style={{ display: "flex", gap: 32, flexWrap: "wrap", marginTop: 16 }}>
                <div>
                  <div style={{ color: "rgba(0,229,255,0.45)", fontSize: 10, fontFamily: "monospace", marginBottom: 8, letterSpacing: "0.1em" }}>KEY TAGS</div>
                  <div>
                    <Tag>VTOL</Tag><Tag>Tiltrotor</Tag><Tag color={accent2}>Ducted Fan</Tag>
                    <Tag color={accent2}>Thrust-vector</Tag><Tag color="#b46fff">Pico 2</Tag>
                    <Tag color="#b46fff">MAVLink 2.0</Tag><Tag color="#ffe600">No Control Surfaces</Tag>
                  </div>
                </div>
              </div>
            </Section>
            <Section title="Key Specs">
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0 40px" }}>
                <div>
                  <Spec label="Wingspan" value="680" unit="mm" />
                  <Spec label="Fuselage length" value="320" unit="mm" />
                  <Spec label="All-up weight" value="≈ 420" unit="g" />
                  <Spec label="Max thrust (2× wing fans)" value="≈ 360" unit="g" />
                  <Spec label="Fwd fan thrust" value="≈ 80" unit="g" />
                  <Spec label="Hover throttle" value="≈ 58" unit="%" />
                </div>
                <div>
                  <Spec label="Battery" value="4S 1300mAh" unit="LiPo" />
                  <Spec label="Hover endurance" value="≈ 9–12" unit="min" />
                  <Spec label="Cruise speed" value="≈ 18–25" unit="m/s" />
                  <Spec label="Nacelle tilt rate" value="≈ 45" unit="°/s" />
                  <Spec label="Transition altitude" value="≥ 8" unit="m AGL" />
                  <Spec label="Radio range" value="≈ 600–1000" unit="m LOS" />
                </div>
              </div>
            </Section>
          </div>
        )}

        {activeTab === "Airframe" && (
          <div>
            <Section title="Three-View Drawing">
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, flexWrap: "wrap" }}>
                <div>
                  <div style={{ color: "rgba(0,229,255,0.35)", fontSize: 9, fontFamily: "monospace", letterSpacing: "0.12em", marginBottom: 8 }}>TOP VIEW</div>
                  <TopView />
                </div>
                <div>
                  <div style={{ color: "rgba(0,229,255,0.35)", fontSize: 9, fontFamily: "monospace", letterSpacing: "0.12em", marginBottom: 8 }}>SIDE VIEW</div>
                  <SideView />
                </div>
              </div>
            </Section>
            <Section title="Structure">
              <Spec label="Wing spar" value="12mm CF tube" unit="" />
              <Spec label="Fuselage frame" value="2mm CF plate + 3D-printed shell" unit="" />
              <Spec label="Nacelle pivot" value="8mm CF rod + ball bearings × 2" unit="" />
              <Spec label="Servo arm geometry" value="Direct servo-to-nacelle, 1:1 linkage" unit="" />
              <Spec label="Duct material" value="PETG printed, 40mm ID, 4-blade stator" unit="" />
              <Spec label="Landing gear" value="Fixed carbon wire skids, 3-point" unit="" />
              <Spec label="Payload bay" value="60 × 45 × 30mm, belly-mount" unit="" />
            </Section>
            <Section title="Nacelle Pivot Design">
              <p style={{ color: "rgba(255,255,255,0.55)", fontFamily: "monospace", fontSize: 12, lineHeight: 1.8 }}>
                Each nacelle rotates ±95° around the wing spar axis. A single MG90S servo drives a push-rod to a crank arm on the nacelle collar. Rotation range is mechanically limited to 0° (horizontal, cruise) through 90° (vertical, hover). A detent at 0° and 90° provides passive lock in each stable mode. ESC and motor wires route through the hollow CF spar and exit through a rotating slip-ring collar, avoiding winding during tilt.
              </p>
            </Section>
          </div>
        )}

        {activeTab === "Propulsion" && (
          <div>
            <Section title="Fan System">
              <div style={{ marginBottom: 20 }}>
                <div style={{ color: accent2, fontFamily: "monospace", fontSize: 12, marginBottom: 8 }}>■ WING NACELLE FANS (×2)</div>
                <Spec label="Duct inner diameter" value="40" unit="mm" />
                <Spec label="Blade count" value="11-blade" unit="" />
                <Spec label="Motor KV" value="3000–3500" unit="KV @ 4S" />
                <Spec label="Static thrust" value="≈ 180" unit="g each" />
                <Spec label="Max current" value="≈ 12" unit="A each" />
                <Spec label="ESC protocol" value="DSHOT300 / BLHeli_S" unit="" />
                <Spec label="Nacelle rotation" value="0–90°" unit="via MG90S servo" />
              </div>
              <div style={{ marginBottom: 20 }}>
                <div style={{ color: "#ffe600", fontFamily: "monospace", fontSize: 12, marginBottom: 8 }}>■ FUSELAGE LONGITUDINAL FAN (×1)</div>
                <Spec label="Duct inner diameter" value="30" unit="mm" />
                <Spec label="Blade count" value="7-blade" unit="" />
                <Spec label="Motor KV" value="4000–4500" unit="KV @ 4S" />
                <Spec label="Static thrust" value="≈ 80" unit="g" />
                <Spec label="Max current" value="≈ 7" unit="A" />
                <Spec label="Orientation" value="Fixed forward" unit="" />
                <Spec label="Primary function" value="Cruise assist + pitch trim" unit="" />
              </div>
            </Section>
            <Section title="Power Budget">
              <Spec label="2× wing ESC + fan @ hover (58%)" value="≈ 10.4" unit="A" />
              <Spec label="Fwd fan @ cruise" value="≈ 5.5" unit="A" />
              <Spec label="2× servos" value="≈ 0.3" unit="A" />
              <Spec label="Avionics (Pico + sensors + radio)" value="≈ 0.4" unit="A" />
              <Spec label="Peak draw (all-out climb)" value="≈ 32" unit="A" />
              <Spec label="Battery C-rating required" value="≥ 35" unit="C continuous" />
              <Spec label="Hover flight time (1300mAh)" value="≈ 9–12" unit="min" />
            </Section>
          </div>
        )}

        {activeTab === "Avionics" && (
          <div>
            <Section title="System Block Diagram">
              <BlockDiagram />
            </Section>
            <Section title="Pico 2 Pin Assignment">
              <PinoutTable />
            </Section>
            <Section title="MAVLink Configuration">
              <Spec label="Radio module" value="SiK v2 915MHz (or 433MHz)" unit="" />
              <Spec label="Protocol" value="MAVLink 2.0" unit="" />
              <Spec label="Baud rate" value="57600" unit="bps UART1" />
              <Spec label="Air data rate" value="128" unit="kbps" />
              <Spec label="GCS software" value="Mission Planner / QGroundControl" unit="" />
              <Spec label="Messages sent" value="HEARTBEAT, ATTITUDE, GPS_RAW_INT, SYS_STATUS, RC_CHANNELS" unit="" />
              <Spec label="Messages received" value="SET_MODE, COMMAND_LONG, RC_CHANNELS_OVERRIDE, PARAM_SET" unit="" />
              <p style={{ color: "rgba(255,255,255,0.45)", fontFamily: "monospace", fontSize: 11, marginTop: 16, lineHeight: 1.8 }}>
                The Pico 2 implements a lightweight MAVLink 2 encoder/parser in C (or MicroPython). No ArduPilot stack — custom control loop runs at 500Hz with MAVLink telemetry at 10Hz. System ID = 1, Component ID = 1 (autopilot).
              </p>
            </Section>
          </div>
        )}

        {activeTab === "Control Logic" && (
          <div>
            <Section title="Flight Modes & Control Allocation">
              <FlightModeTable />
            </Section>
            <Section title="Control Loop Architecture">
              <p style={{ color: "rgba(255,255,255,0.5)", fontFamily: "monospace", fontSize: 12, lineHeight: 1.9, marginTop: 0 }}>
                The Pico 2 runs a 500Hz main loop on Core 0, with Core 1 dedicated to MAVLink parsing and telemetry packing. Sensor fusion uses a Mahony AHRS filter combining ICM-42688-P gyro/accel with barometer altitude. GPS provides position hold above 3m AGL.
              </p>
              <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: 2, marginTop: 12 }}>
                {[
                  ["Rate loop (inner)", "500 Hz", "PID on gyro rate — direct PWM output to ESCs and servos"],
                  ["Attitude loop (mid)", "100 Hz", "PID on AHRS quaternion error — commands rate setpoints"],
                  ["Position loop (outer)", "25 Hz", "PID on GPS/baro error — commands attitude setpoints"],
                  ["Transition sequencer", "10 Hz", "State machine: HOVER → TRANS → CRUISE with servo sweep profile"],
                  ["MAVLink heartbeat", "1 Hz", "sys_status + heartbeat to GCS"],
                  ["MAVLink telemetry", "10 Hz", "ATTITUDE, GPS_RAW_INT, SYS_STATUS"],
                ].map(([name, rate, desc], i) => (
                  <div key={i} style={{ display: "grid", gridTemplateColumns: "180px 80px 1fr", gap: 12, padding: "8px 0", borderBottom: "1px solid rgba(0,229,255,0.07)", alignItems: "baseline" }}>
                    <span style={{ color: accent, fontFamily: "monospace", fontSize: 11 }}>{name}</span>
                    <span style={{ color: accent2, fontFamily: "monospace", fontSize: 11 }}>{rate}</span>
                    <span style={{ color: "rgba(255,255,255,0.45)", fontFamily: "monospace", fontSize: 11 }}>{desc}</span>
                  </div>
                ))}
              </div>
            </Section>
            <Section title="Transition Logic">
              <p style={{ color: "rgba(255,255,255,0.5)", fontFamily: "monospace", fontSize: 12, lineHeight: 1.8 }}>
                Transition is triggered by GCS mode command or airspeed threshold (&gt;6 m/s). The sequencer sweeps nacelle servos at 45°/s while simultaneously ramping forward fan thrust from 0% to 60%. Wing fan thrust is maintained at hover level during transition to preserve altitude. Full cruise configuration is declared when nacelles reach 0° and airspeed &gt;10 m/s. Reverse transition initiates nacelle sweep to 90° with forward fan cut-off.
              </p>
            </Section>
          </div>
        )}

        {activeTab === "BOM" && (
          <div>
            <Section title="Bill of Materials">
              <BOMTable />
            </Section>
            <Section title="Notes">
              <p style={{ color: "rgba(255,255,255,0.45)", fontFamily: "monospace", fontSize: 11, lineHeight: 1.9 }}>
                · Prices are approximate street prices (AliExpress/Amazon) as of 2024–2025.<br/>
                · 4S LiPo with XT30 is recommended for weight savings over XT60 at this power level.<br/>
                · AM32 open-source firmware is preferred over BLHeli_S for DSHOT300 + telemetry feedback.<br/>
                · ICM-42688-P preferred over MPU6050 due to lower vibration noise floor — critical for ducted fans.<br/>
                · SiK 915MHz preferred for US operation; 433MHz for EU/AU. Check local regulations.<br/>
                · Carbon-fibre frame components available from RDQ, GetFPV, or AliExpress in cut-to-size sheets.
              </p>
            </Section>
          </div>
        )}

      </div>

      {/* Footer */}
      <div style={{ position: "relative", zIndex: 1, borderTop: "1px solid rgba(0,229,255,0.1)", padding: "14px 32px", display: "flex", justifyContent: "space-between", flexWrap: "wrap", gap: 8 }}>
        <span style={{ color: "rgba(0,229,255,0.25)", fontFamily: "monospace", fontSize: 9, letterSpacing: "0.12em" }}>TRI-FAN TILTROTOR · DESIGN REV 1.0</span>
        <span style={{ color: "rgba(0,229,255,0.25)", fontFamily: "monospace", fontSize: 9, letterSpacing: "0.1em" }}>NOT FOR FLIGHT · REFERENCE DESIGN ONLY</span>
      </div>
    </div>
  );
}
