# Manufacturer-specific OBD2 DTC codes — Ford, Jeep/Chrysler/FCA, Volvo
# Coverage: 2008 and newer (P1xxx, B1xxx, C1xxx, U1xxx ranges)
# Source: SAE J2012 manufacturer-defined ranges + OEM service documentation.
# lookup_oem(code_str) → description string or None

# ── Ford (all platforms 2008+: Fusion, F-150, Explorer, Mustang, Edge, etc.) ──
_FORD = {
    "P1000": "OBD-II Readiness Tests Not Complete",
    "P1001": "Key On Engine Running Self Test Cannot Complete",
    "P1039": "Vehicle Speed Signal Missing or Improper",
    "P1051": "Brake Switch Signal Missing or Improper",
    "P1100": "MAF Sensor Intermittent",
    "P1101": "MAF Sensor Out of Self-Test Range",
    "P1102": "MAF Sensor In-Range But Lower Than Expected",
    "P1103": "MAF Sensor In-Range But Higher Than Expected",
    "P1104": "MAF Sensor Ground Malfunction",
    "P1112": "IAT Sensor Intermittent",
    "P1116": "ECT Sensor Out of Self-Test Range",
    "P1117": "ECT Sensor Intermittent",
    "P1120": "TP Sensor Out of Range Low",
    "P1121": "TP Sensor Inconsistent with MAF Sensor",
    "P1124": "TP Sensor Out of Self-Test Range",
    "P1125": "TP Sensor Intermittent",
    "P1127": "Downstream O2 Sensor Not Warm for Catalyst Test",
    "P1128": "Downstream O2 Sensors Swapped Bank to Bank",
    "P1130": "Lack of HO2S Switch — Bank 1 Sensor 1 at Limit",
    "P1131": "HO2S Indicates Lean — Bank 1 Sensor 1",
    "P1132": "HO2S Indicates Rich — Bank 1 Sensor 1",
    "P1133": "HO2S Insufficient Switching — Bank 1 Sensor 1",
    "P1150": "Lack of HO2S Switch — Bank 2 Sensor 1 at Limit",
    "P1151": "HO2S Indicates Lean — Bank 2 Sensor 1",
    "P1152": "HO2S Indicates Rich — Bank 2 Sensor 1",
    "P1153": "HO2S Insufficient Switching — Bank 2 Sensor 1",
    "P1220": "Throttle Position Sensor B Circuit Failure",
    "P1224": "Throttle Position Sensor B Out of Self-Test Range",
    "P1233": "Fuel System Disabled or Offline",
    "P1234": "Fuel System Disabled or Offline (EPAS)",
    "P1235": "Fuel Pump Control Out of Range",
    "P1236": "Fuel Pump Control Out of Range (High Side)",
    "P1237": "Fuel Pump Secondary Circuit Failure",
    "P1238": "Fuel Pump Secondary Circuit Failure (High Side)",
    "P1244": "Alternator Load Input Low",
    "P1245": "Alternator Load Input High",
    "P1250": "Fuel Pressure Relief Valve Open",
    "P1260": "Theft Detected — Vehicle Immobilized (PATS)",
    "P1270": "RPM or Vehicle Speed Limiter Reached",
    "P1285": "Cylinder Head Temperature Sensor High",
    "P1288": "CHT Sensor Out of Self-Test Range",
    "P1289": "Cylinder Head Temperature Sensor Low",
    "P1299": "CHT Sensor — Engine Overheating Condition Detected",
    "P1336": "CKP/CMP Sensor Disagree",
    "P1340": "CMP Sensor B Circuit Malfunction",
    "P1351": "Ignition Diagnostic Monitor (IDM) Circuit Input Malfunction",
    "P1352": "Ignition Coil A Primary Circuit Failure",
    "P1353": "Ignition Coil B Primary Circuit Failure",
    "P1354": "Ignition Coil C Primary Circuit Failure",
    "P1355": "Ignition Coil D Primary Circuit Failure",
    "P1356": "PIP Input with IDM Signal Present While Engine Off",
    "P1357": "IDM Pulse Width Not Defined",
    "P1358": "Ignition Diagnostic Monitor Signal Out of Self-Test Range",
    "P1359": "Spark Output Circuit Malfunction",
    "P1380": "Variable Cam Timing Solenoid A (Bank 1) Malfunction",
    "P1381": "Variable Cam Timing Over-Advanced (Bank 1)",
    "P1383": "Variable Cam Timing Over-Retarded (Bank 1)",
    "P1385": "Variable Cam Timing Solenoid A (Bank 2) Malfunction",
    "P1386": "Variable Cam Timing Over-Advanced (Bank 2)",
    "P1388": "Variable Cam Timing Over-Retarded (Bank 2)",
    "P1390": "Octane Adjust (OCT ADJ) Circuit Out of Self-Test Range",
    "P1400": "Differential Pressure Feedback (DPFE) Sensor Low Voltage",
    "P1401": "DPFE Sensor High Voltage",
    "P1402": "EGR System Malfunction Detected",
    "P1403": "DPFE Sensor Hoses Reversed",
    "P1404": "EGR Valve Stuck Closed",
    "P1405": "DPFE Upstream Hose Off or Plugged",
    "P1406": "DPFE Downstream Hose Off or Plugged",
    "P1407": "EGR No Flow Detected — Valve Stuck Closed or Inoperative",
    "P1408": "EGR Flow Out of Self-Test Range",
    "P1409": "EGR Vacuum Regulator Solenoid Circuit Malfunction",
    "P1436": "EVAP Running Loss Purge Valve Failure",
    "P1440": "EVAP Running Loss System Fault",
    "P1441": "EVAP System Control Valve Circuit",
    "P1443": "EVAP System Control Valve Circuit",
    "P1449": "EVAP Canister Vent Valve Stuck Closed",
    "P1450": "Unable to Bleed Up Fuel Tank Vacuum",
    "P1451": "EVAP Charcoal Canister Vent Control Circuit",
    "P1455": "EVAP System Large Leak",
    "P1460": "Wide Open Throttle A/C Cutout Circuit Malfunction",
    "P1461": "A/C Refrigerant Pressure Sensor High",
    "P1462": "A/C Refrigerant Pressure Sensor Low",
    "P1463": "A/C Refrigerant Pressure Sensor Insufficient Change",
    "P1469": "Low A/C Cycling Period",
    "P1479": "Transmission Control Switch Circuit High",
    "P1481": "Cooling Fan Speed Sensor Malfunction",
    "P1483": "Power to Fan Circuit — Excessive Current Draw",
    "P1500": "Vehicle Speed Sensor Intermittent",
    "P1501": "Vehicle Speed Sensor Out of Self-Test Range",
    "P1504": "IAC Circuit Open",
    "P1505": "IAC System at Adaptive Clip",
    "P1506": "IAC Overspeed Error",
    "P1507": "IAC Underspeed Error",
    "P1516": "TAC Module Throttle Actuator Position Performance",
    "P1518": "Throttle Actuator Control Module Sequential Circuit Failure",
    "P1519": "Throttle Actuator Control Module Stuck Closed",
    "P1520": "Park/Neutral Position Switch Circuit",
    "P1536": "Parking Brake Applied Failure",
    "P1550": "Power Steering Pressure Sensor Out of Self-Test Range",
    "P1566": "Cruise Speed Out of Range",
    "P1567": "Cruise Control Active — Accelerator Pedal Pressed",
    "P1568": "Cruise Control Unable to Maintain Speed",
    "P1571": "Brake Switch Circuit (Traction Control)",
    "P1575": "Brake Switch Circuit — Out of Range",
    "P1579": "P/N to D/R at High Throttle Angle",
    "P1600": "Loss of KAM Power — System Failure",
    "P1601": "Internal Module Communication Failure",
    "P1605": "PCM Keep-Alive Memory Test Failure",
    "P1622": "Controller Area Network (CAN) Bus Circuit Fault",
    "P1626": "Theft Deterrent Fuel Enable Signal Not Received (PATS)",
    "P1629": "Theft Deterrent Signal Not Present, Engine Running",
    "P1630": "Theft Deterrent PCM in Learn Mode",
    "P1631": "Theft Deterrent Learn Disabled",
    "P1632": "Theft Deterrent Fuel Disable Signal Received",
    "P1633": "Keep-Alive Memory (KAM) Voltage",
    "P1635": "Tire/Axle Ratio Out of Range",
    "P1639": "Vehicle ID Block Corrupted or Not Programmed",
    "P1641": "Fuel Pump Primary Circuit — MIL Control",
    "P1660": "Output Circuit Check Signal High",
    "P1661": "Output Circuit Check Signal Low",
    "P1662": "Transmission Shift Light Circuit",
    "P1671": "MIL Circuit Fault",
    "P1672": "Low Engine Oil Level Light Circuit",
    "P1673": "Engine Hot Light Circuit",
    "P1674": "Tach Circuit Malfunction",
    "P1675": "EVAP Vent Solenoid Circuit",
    "P1682": "Charging System Voltage Low (EVTM)",
    "P1683": "Speed Control Power Relay or 8V Reference Circuit",
    "P1684": "Loss of Battery Voltage (Last 50 Starts)",
    "P1685": "Smart Key Immobilizer Module — Invalid Key",
    "P1686": "No SKIM Bus Messages Received",
    "P1700": "Transmission Indeterminate Failure",
    "P1701": "TFT Sensor Signal Intermittent",
    "P1704": "Digital Transmission Range Sensor Failed to Transition",
    "P1705": "Digital Transmission Range Sensor Out of Self-Test Range",
    "P1706": "High Vehicle Speed Observed in Park",
    "P1711": "TFT Sensor Out of Self-Test Range",
    "P1714": "Shift Solenoid A Inductive Signature",
    "P1715": "Shift Solenoid B Inductive Signature",
    "P1720": "Vehicle Speed Sensor Circuit Malfunction (Trans)",
    "P1727": "Coast Clutch Solenoid Inductive Signature",
    "P1728": "Transmission Slip Error",
    "P1729": "4×4 Low Switch Error",
    "P1744": "Torque Converter Clutch System Performance (Ford AT)",
    "P1746": "Electronic Pressure Control Solenoid Open Circuit",
    "P1747": "Electronic Pressure Control Solenoid Short Circuit",
    "P1749": "Pressure Control Solenoid Failed Low",
    "P1780": "Transmission Control Switch Out of Self-Test Range",
    "P1781": "4WD Switch Out of Self-Test Range",
    "P1783": "Transmission Over-Temperature Condition",
    # Ford-specific B codes
    "B1213": "Anti-Theft Number of Attempts Exceeded (PATS)",
    "B1232": "Transceiver Internal Antenna Damaged",
    "B1600": "PATS Ignition Key Transponder Signal Not Received",
    "B1601": "PATS Received Incorrect Key Code from Ignition Key Transponder",
    "B1602": "PATS Received Invalid Format of Key Code",
    "B1681": "PATS Transceiver Signal Not Received",
    "B2103": "Antenna Not Connected",
    "B2141": "NVM Configuration Failure",
    "B2477": "Module Configuration Failure",
    "B2900": "Module VIN Mismatch",
    # Ford-specific U codes (CAN network)
    "U0401": "Invalid Data Received From ECM/PCM (Ford Specific)",
    "U0415": "Invalid Data Received From ABS Module (Ford ABS)",
}

# ── Jeep / Chrysler / FCA (2008+ — Grand Cherokee, Wrangler, Cherokee, Ram, etc.) ──
_JEEP = {
    "P1093": "Fuel Rail Pressure — Loss of Prime",
    "P1094": "Fuel Rail Pressure — Engine Running",
    "P1110": "Manifold Absolute Pressure Sensor Rationality",
    "P1115": "MAP Sensor Intermittent",
    "P1116": "Engine Coolant Temperature Sensor Performance",
    "P1117": "ECT Sensor Rationality",
    "P1118": "Manifold Absolute Temperature Sensor Low",
    "P1119": "Manifold Absolute Temperature Sensor High",
    "P1121": "Pedal Position Sensor 1 Voltage High",
    "P1122": "Pedal Position Sensor 1 Voltage Low",
    "P1123": "Pedal Position Sensor 2 Voltage High",
    "P1124": "Pedal Position Sensor 2 Voltage Low",
    "P1128": "O2 Sensor Upstream Rich — Bank 1",
    "P1129": "O2 Sensor Upstream Rich — Bank 2",
    "P1130": "O2 Sensor (B1S1) Slow Switch — Rich to Lean",
    "P1131": "O2 Sensor (B1S1) Slow Switching",
    "P1176": "O2 Sensor (B1S2) Rich",
    "P1177": "O2 Sensor (B2S2) Rich",
    "P1195": "Slow O2 Sensor (B1S1) During Catalyst Monitor",
    "P1196": "Slow O2 Sensor (B2S1) During Catalyst Monitor",
    "P1197": "Slow O2 Sensor (B1S2) During Catalyst Monitor",
    "P1199": "Fuel Level Sensor Rationality",
    "P1228": "Fuel Rail Pressure — Moderately High",
    "P1229": "Fuel Rail Pressure — High",
    "P1230": "Fuel Pump Low Speed Malfunction",
    "P1231": "Fuel Pump High Speed Malfunction",
    "P1281": "Engine Cold Too Long",
    "P1282": "Fuel Pressure Solenoid Malfunction",
    "P1283": "Idle Select Signal Invalid",
    "P1284": "Fuel Injection Pump Battery Voltage Out of Range",
    "P1285": "Fuel Injection Pump Controller Always On",
    "P1286": "Accelerator Position Sensor Supply Voltage High",
    "P1287": "Fuel Injection Pump Controller Supply Voltage Low",
    "P1289": "Manifold Tune Valve Solenoid Circuit",
    "P1290": "CNG Fuel System Pressure Too High",
    "P1291": "No Temperature Rise from Intake Air Heaters",
    "P1294": "Target Idle Not Reached",
    "P1295": "No 5V Supply to TP Sensor",
    "P1296": "No 5V Supply to MAP Sensor",
    "P1297": "No Change in MAP from Start to Run",
    "P1298": "Lean Operation at Wide Open Throttle",
    "P1299": "Vacuum Leak Found — IAC Fully Seated",
    "P1300": "Turbo Boost Limit Exceeded",
    "P1386": "NVLD Solenoid Resistance Out of Range",
    "P1388": "Sub Processor Failure",
    "P1389": "No ASD Relay Output Voltage at PCM",
    "P1390": "Timing Belt Skipped 1 Tooth or More",
    "P1391": "Intermittent Loss of CMP or CKP Signals",
    "P1392": "Rough Road G-Sensor Circuit Low",
    "P1393": "Rough Road G-Sensor Circuit High",
    "P1394": "Multiple Cylinder Misfire",
    "P1398": "Misfire Adaptive Numerator at Limit",
    "P1399": "Wait to Start Lamp Circuit",
    "P1400": "MAP/Coolant Temperature Correlation Error",
    "P1403": "EGR Solenoid Valve No. 3 Circuit",
    "P1404": "EGR Stuck Open",
    "P1405": "EGR Solenoid Valve No. 5 Circuit",
    "P1406": "EGR Temperature Sensor Failure",
    "P1410": "Secondary Air Injection Pump Motor Circuit",
    "P1411": "Secondary Air Injection System Control Valve Circuit",
    "P1440": "EVAP Large Leak",
    "P1441": "EVAP Small Leak",
    "P1442": "EVAP Vent Solenoid Circuit",
    "P1443": "EVAP Purge Duty Cycle Error",
    "P1480": "Fan Control Relay 1 Circuit",
    "P1481": "Fan Control Relay 2 & 3 Circuit",
    "P1483": "Power to Fan Circuit — Excessive Current Draw",
    "P1486": "EVAP Leak Monitor — Pinched Hose Found",
    "P1488": "Auxiliary Coolant Pump Relay",
    "P1489": "High Speed Fan Control Relay",
    "P1490": "Low Speed Fan Relay Control Circuit",
    "P1491": "Radiator Fan Control Relay Circuit",
    "P1492": "Ambient/Battery Temp Sensor Voltage High",
    "P1493": "Ambient/Battery Temp Sensor Voltage Low",
    "P1494": "EVAP Leak Detection Pump Switch Voltage Low",
    "P1495": "EVAP Leak Detection Pump Solenoid Circuit",
    "P1496": "5V Supply Output 1 — Low",
    "P1499": "Hydraulic Cooling Fan Solenoid",
    "P1500": "Generator Field Not Switching Properly",
    "P1521": "Incorrect Engine Oil Type Detected",
    "P1530": "Timing Belt Skipped 2 or More Teeth",
    "P1536": "Parking Brake Applied Failure",
    "P1545": "Electronic Throttle Control",
    "P1572": "ESC Not Making Proper Correction",
    "P1579": "P/N to D/R at High Throttle Angle",
    "P1594": "Battery Voltage High",
    "P1595": "Speed Control Solenoid Circuits",
    "P1596": "Speed Control Switch Always High",
    "P1597": "Speed Control Switch Always Low",
    "P1598": "A/C Pressure Sensor Volts Too High",
    "P1599": "A/C Pressure Sensor Volts Too Low",
    "P1602": "PCM Not Programmed",
    "P1624": "Anti-Theft Signal Not Received",
    "P1625": "Large Leak Found — EVAP Tank Pressure Sensor",
    "P1626": "Theft Deterrent Fuel Enable Signal Not Received",
    "P1683": "Speed Control Power Relay Circuit",
    "P1684": "Loss of Battery Voltage (Last 50 Starts)",
    "P1685": "Smart Key Immobilizer Module — Invalid Key",
    "P1686": "No SKIM Bus Message Received",
    "P1687": "No MIC Bus Message Received",
    "P1688": "Internal Fuel Injection Pump Failure",
    "P1689": "No Communication Between ECM and Injection Pump Module",
    "P1690": "Fuel Injection Pump CKP Sensor Disagrees with ECM CKP",
    "P1691": "Fuel Injection Pump Controller Calibration Error",
    "P1693": "DTC Detected in Companion Module",
    "P1694": "No CCD Bus Message from ECM/PCM",
    "P1695": "No CCD Bus Message from BCM",
    "P1696": "EEPROM Write Denied",
    "P1697": "EMR Miles Not Stored",
    "P1698": "No CCD Bus Message from TCM",
    "P1699": "No CCD Bus Message from HVAC",
    "P1740": "Transmission Temperature Sensor",
    "P1756": "Governor Pressure Not Equal to Target",
    "P1757": "Governor Pressure Above 3 PSI in Gear With 0 MPH",
    "P1762": "Governor Pressure Offset High",
    "P1763": "Governor Pressure Sensor Voltage High",
    "P1764": "Governor Pressure Sensor Voltage Low",
    "P1765": "Trans 12V Supply Relay Control Circuit",
    "P1776": "Solenoid Switch Valve Latched in Low/Reverse Position",
    "P1777": "Solenoid Switch Valve Latched in Park Position",
    "P1778": "Solenoid Switch Valve Latched in TCC Position",
    "P1781": "4WD Switch Circuit",
    "P1782": "P/N Position Switch Circuit",
    "P1784": "Transmission Mechanical Failure — First and Reverse",
    "P1795": "4WD Low Switch",
    "P1796": "Transfer Case Control Module Communication Fault",
    "P1799": "Torque Management",
    # Jeep/Chrysler B codes (SKREEM / BCM)
    "B1209": "SKREEM — Transponder Communication Error",
    "B1600": "SKREEM — No Response from Transponder",
    "B1601": "SKREEM — Transponder ID Not Programmed",
    "B2103": "SKREEM — Antenna Circuit Open",
    "B2104": "SKREEM — Antenna Circuit Short to Ground",
    # Jeep/Chrysler U codes (CAN-C / PCI bus)
    "U0100": "Lost Communication with ECM/PCM (Chrysler CAN-C)",
    "U0101": "Lost Communication with TCM (Chrysler CAN-C)",
    "U0140": "Lost Communication with BCM (Chrysler CAN-C)",
    "U0155": "Lost Communication with Instrument Cluster (Chrysler CAN-C)",
    "U0164": "Lost Communication with HVAC Module (Chrysler CAN-C)",
    "U0184": "Lost Communication with Radio (Chrysler CAN-C)",
    "U0415": "Invalid Data from ABS/WSS Module (Chrysler CAN-C)",
    "U1110": "Lost Communication with PCI Bus",
    "U1111": "Lost Communication with SCI Bus",
    "U1120": "Lost Wheel Distance Message",
    "U1121": "Lost Wheel Distance Message (Alternate)",
    "U1122": "Lost Brake Switch Message from ABS",
    "U1140": "Lost Ignition Switch Message",
    "U1411": "PCI Bus No Responders",
    "U1412": "Implausible PCI Bus Messages",
    "U1413": "PCI Bus Shorted",
}

# ── Volvo (2008+ — S60, S80, V70, XC60, XC70, XC90, S40, V50, C30, C70) ──
_VOLVO = {
    "P1131": "EGAS — Electronic Throttle Module Fault",
    "P1241": "Turbocharger Bypass Valve — Circuit Fault",
    "P1242": "Turbocharger Bypass Valve — Performance",
    "P1251": "Charge Air Cooler Temperature Sensor",
    "P1300": "Incorrect Fuel Detected",
    "P1311": "EGR Valve Position Sensor — Circuit Low",
    "P1312": "EGR Valve Position Sensor — Circuit High",
    "P1313": "EGR Valve Position Sensor — Range/Performance",
    "P1402": "EGR Valve Solenoid Circuit — Short",
    "P1403": "EGR Valve Solenoid Circuit — Open",
    "P1404": "EGR Valve — Mechanical Fault",
    "P1406": "EGR Cooler Bypass Valve — Fault",
    "P1407": "EGR Cooler Bypass Valve — Performance",
    "P1408": "EGR Cooler Bypass Valve Stuck Open",
    "P1409": "EGR Cooler Bypass Valve Stuck Closed",
    "P1450": "EVAP System — General Fault",
    "P1451": "EVAP Canister Vent Valve — Short",
    "P1452": "EVAP Canister Vent Valve — Open",
    "P1453": "EVAP Canister Vent Valve — Performance",
    "P1454": "EVAP Fuel Level Sensor Reference Voltage",
    "P1455": "EVAP System Leak — Large Leak",
    "P1456": "EVAP Purge Valve — Short",
    "P1457": "EVAP Purge Valve — Open",
    "P1490": "Radiator Fan Speed 1 Control Circuit",
    "P1492": "Radiator Fan Speed 2 Control Circuit",
    "P1560": "Fuel Pump Relay Circuit",
    "P1561": "Fuel Pump Relay — Performance",
    "P1562": "Fuel Pump Relay — Short to Ground",
    "P1563": "Fuel Pump Relay — Short to Voltage",
    "P1600": "Lost Communication with Immobilizer Module",
    "P1601": "Immobilizer Module — Internal Fault",
    "P1602": "Immobilizer Key Not Programmed",
    "P1605": "PCM — Internal Performance",
    "P1610": "Controller Communication Fault (CAN)",
    "P1620": "Lost Communication with Engine Control Module",
    "P1625": "Lost Communication with Throttle Module (EGAS)",
    "P1650": "Active Suspension Control Module — Fault",
    "P1651": "Active Suspension Control Module — Performance",
    "P1680": "Stability Control (DSTC) — Fault",
    "P1681": "Anti-Spin (ASR/TC) — Fault",
    "P1690": "Immobilizer Module — General Fault",
    "P1700": "Transmission Control Module — Fault",
    "P1750": "Gear Selector Position Sensor",
    "P1780": "Transmission Control Switch — Out of Range",
    # Volvo SRS/Safety B codes
    "B0001": "SRS — Driver Airbag Squib 1 Fault",
    "B0010": "SRS — Passenger Airbag Squib 1 Fault",
    "B0071": "SRS — Left Front Side Airbag Fault",
    "B0076": "SRS — Right Front Side Airbag Fault",
    "B0051": "SRS — Crash Sensor Fault",
    # Volvo CEM (Central Electronic Module) U codes
    "U0100": "CEM — Lost Communication with ECM",
    "U0140": "CEM — Lost Communication with BCM/CEM Internal",
    "U0155": "CEM — Lost Communication with DIM (Driver Information Module)",
    "U0164": "CEM — Lost Communication with Climate Control Module (ECC)",
    "U0184": "CEM — Lost Communication with Audio Module",
    "U0197": "CEM — Lost Communication with Bluetooth/Phone Module",
    "U0198": "CEM — Lost Communication with Telematics (OnCall) Module",
    "U0422": "CEM — Invalid Data from BCM/CEM",
}

# ── Merge all into a single lookup dict ───────────────────────────────────────
# Jeep codes take priority over Ford where they overlap (they share some P1xxx)
_OEM_ALL = {}
_OEM_ALL.update(_FORD)
_OEM_ALL.update(_JEEP)   # Jeep overrides Ford for shared codes
_OEM_TAGGED = {}
for code, desc in _FORD.items():
    _OEM_TAGGED[code] = f"[Ford] {desc}"
for code, desc in _JEEP.items():
    _OEM_TAGGED[code] = f"[Jeep/FCA] {desc}"
for code, desc in _VOLVO.items():
    _OEM_TAGGED[code] = f"[Volvo] {desc}"


def lookup_oem(code_str, tag_manufacturer=True):
    """
    Look up a manufacturer-specific DTC.
    Returns a description string with manufacturer tag, or None if not found.
    """
    key = code_str.upper()
    if tag_manufacturer:
        return _OEM_TAGGED.get(key)
    return _OEM_ALL.get(key)


# ── Proprietary OBD2 Connector Pin Reference ──────────────────────────────────
#
# Standard OBD2 (SAE J1962) Connector — 16 pins:
#
# Pin 4:  Chassis Ground                    (MANDATORY)
# Pin 5:  Signal Ground                     (MANDATORY)
# Pin 6:  CAN High (HS-CAN, J2284)         (MANDATORY — connected to your CANH)
# Pin 14: CAN Low  (HS-CAN, J2284)         (MANDATORY — connected to your CANL)
# Pin 16: Battery+ / Switched Power         (MANDATORY — 12V, always hot)
#
# Manufacturer-specific / optional pins — REQUIRE SEPARATE HARDWARE:
#
# Pin 2:  SAE J1850 Bus+
#   Ford (pre-2008 majority, some 2008+ body modules):
#     Standard Corporate Protocol (SCP/J1850-PWM 41.6kbps), differential pair
#     with Pin 10.  Used by BCM, cluster, A/C on older architectures.
#   GM/Jeep (older): J1850-VPW (10.4kbps) single wire.
#
# Pin 3:  Manufacturer Discretionary
#   Ford: SCP Bus A (paired with Pin 11 on some configurations)
#   Jeep/Chrysler: SCI-Receive (Serial Communications Interface, K-line-like,
#     used by DRB-III / wiTECH scan tools for some modules at 62.5kbps)
#
# Pin 7:  ISO 9141-2 K-Line / ISO 14230 KWP2000
#   Ford: Used for module programming (IDS reflash of PCM, TCM).
#   Jeep/Chrysler: Legacy K-line for powertrain & body on pre-2012 models;
#     still present for some modules (SKREEM, BCM) on 2012+ Wrangler JK.
#   Volvo: VIDA/DiCE programming interface; required for ECM flash.
#     Volvo uses a proprietary hand-shake on K-line at 10.4kbps init.
#   BMW/MB: Also on Pin 7 — not relevant here but note cross-contamination.
#
# Pin 8:  Manufacturer Discretionary
#   Ford (2010+ F-150, Explorer, Fusion, Mustang): Medium-Speed CAN bus-
#     MS-CAN at 125kbps (body/comfort modules — APIM, SYNC, ABS).
#     Differential pair with Pin 1 on some vehicles.
#
# Pin 9:  Manufacturer Discretionary
#   Jeep/Chrysler: SCI-Transmit (scan tool output to module)
#
# Pin 10: SAE J1850 Bus-  (Ford SCP differential return for Pin 2)
#
# Pin 11: Manufacturer Discretionary
#   Ford: SCP Bus B (some configurations); MS-CAN+ on some trucks.
#   Jeep/Chrysler: SCI-Receive (body controller channel)
#
# Pin 12: Manufacturer Discretionary
#   Ford: J1850 or proprietary on some pre-2008 models.
#   Volvo: Proprietary diagnostic channel on some P2/P3 platform vehicles
#     (S80 II, XC60 1st gen) — not consistently implemented.
#   Chrysler: Used on some platforms for ISO 9141.
#
# Pin 13: Manufacturer Discretionary
#   Chrysler: Additional serial channel on some TCM configurations.
#
# Pin 15: ISO 9141-2 L-Line (fast-init clock)
#   Present on some older vehicles. Rarely used on 2008+ platforms.
#
# ── What YOUR hardware can currently read ─────────────────────────────────────
# Your RP2350-CAN board reads ONLY pins 6 (CANH) and 14 (CANL), i.e.,
# the HS-CAN bus at 500kbps. This covers:
#   • All OBD2-mandated Mode 01–0A data (Modes 03, 07, 0A for DTCs)
#   • All ISO 15765-4 (CAN-based OBD2) PIDs
#   • Ford MS-CAN body modules ONLY if you rewire to pins 1/8 (add a
#     second MCP2515 on a spare SPI, bus runs at 125kbps)
#   • Chrysler CAN-C (medium speed) body bus ONLY if you rewire to
#     pins 3/11 with a second MCP2515 at 125kbps
#
# To read K-line (Pin 7) protocols you need: an L9637 or MC33290 K-line
# transceiver connected to a UART on the RP2350.
#
# To read J1850 (Pins 2/10) you need: a dedicated J1850 transceiver IC
# (e.g. MC33390) — not available as a generic SPI module.
# ─────────────────────────────────────────────────────────────────────────────
