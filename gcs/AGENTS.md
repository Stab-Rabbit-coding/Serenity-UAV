# Ground Control Station (Skipper) — Agent Instructions

> *See the root `AGENTS.md` for project-wide policies. This file provides specific guidance for the ground control station (GCS) software, hardware, and operator interface.*

## Scope

Skipper is the ground control station (GCS) for Serenity-UAV. This folder contains:
- GCS software (command and control, telemetry display, mission planning)
- Hardware interface and communications middleware
- Operator interface design and documentation
- Test harnesses and simulation tools

Skipper's role: the boss. He commands the UAV, receives telemetry, authenticates all commands, and maintains a real-time audit log of all flight operations and command/response transactions.

## Ground Control Station Architecture

### Role and Responsibilities

Skipper is responsible for:
- **Command and Control (C2):** Send verified, cryptographically signed commands to all onboard nodes
- **Telemetry Reception:** Receive, verify, and display real-time sensor data and system status
- **Mission Planning:** Design and upload flight missions with autonomous execution capability
- **Failover Management:** Override automatic failover decisions if needed (with audit logging)
- **Data Logging:** Archive all telemetry, commands, and responses for post-flight analysis
- **Security:** Enforce authentication for all operator actions and verify all received telemetry

### External Communications Channels

Skipper communicates with Serenity via:
1. **Wi-Fi (5 GHz):** Primary high-bandwidth channel for telemetry and camera feed
2. **Zigbee (2.4 GHz):** Secondary mesh network for command retry and extended range
3. **SiK / MAVLink (915 MHz):** Backup control channel (900 MHz unlicensed ISM)
4. **49 MHz (Part 15 §15.235):** Ultra-reliable emergency command/response in harsh RF environments

All channels support full command and control capability in both directions. Channel selection is automatic based on signal quality and command priority.

## Operator Interface Design

### Command Authentication

Every operator command to the UAV must be:
- **Verified:** Syntax and scope checked against allowed operations
- **Signed:** Cryptographically signed by the operator's certificate
- **Confirmed:** Operator confirms the action (no accidental commands)
- **Logged:** Command, timestamp, operator ID, and result are recorded

### Telemetry Display

Real-time display shall show:
- **Flight state:** Attitude (pitch, roll, yaw), altitude, airspeed, position (GPS)
- **Power state:** Battery voltage, current draw, estimated runtime
- **System status:** Node health (all 4 stacks), communication link quality, thermal state
- **Payload:** Cargo bay status, hoist state, payload mass
- **Alerts:** Any node failover, communication loss, sensor failure, or anomalous behavior

### Mission Planning Interface

Operators shall be able to:
- Define waypoint sequences with attitude and speed constraints
- Set geofences (keep-out zones) and no-fly regions
- Configure autonomous loiter patterns, survey grids, or search patterns
- Upload mission to the UAV with cryptographic verification
- Monitor mission execution in real time
- Cancel or modify mission in flight (with signed confirmation)

## Communications Protocol

### Message Format

All messages between Skipper and Serenity shall:
- Use a standard message wrapper with:
    - Message type (command, telemetry, acknowledgment, error)
    - Source (ground / node ID)
    - Destination (all / specific node / all flight controllers)
    - Sequence number (for retransmission tracking)
    - Timestamp (synchronized to UAV time)
    - Cryptographic signature (HMAC or public-key)
    - Payload (command or data)

### Command Priority Levels

Commands are prioritized for failover and queuing:

| Level | Type | Example | Channel | Retransmit |
| --- | --- | --- | --- | --- |
| **CRITICAL** | Safety override | "Land now", "Cut power", "Disarm" | All + SiK primary | Yes, every 100ms |
| **HIGH** | Flight control | "Navigate to waypoint", "Change altitude" | Wi-Fi primary, SiK backup | Yes, every 500ms |
| **MEDIUM** | Payload control | "Deploy cargo", "Activate hoist" | Any (best quality) | Yes, on timeout |
| **LOW** | Status query | "Report battery voltage" | Any | No retransmit |

### Telemetry Data Rates

Serenity transmits telemetry at variable rates depending on link quality and priority:

| Data Type | Rate (Nominal) | Rate (Degraded) | Priority |
| --- | --- | --- | --- |
| Flight state (attitude, altitude, airspeed) | 50 Hz | 10 Hz | Critical |
| Position (GPS) | 10 Hz | 2 Hz | High |
| Power and thermal | 5 Hz | 1 Hz | Medium |
| Sensor details (raw IMU, compass, air data) | 1 Hz | On request | Low |
| System status (node health, comms quality) | 2 Hz | 0.5 Hz | High |
| Payload state (cargo bay, hoist position) | 2 Hz | 1 Hz | Medium |
| Event log (errors, failovers, anomalies) | On event | On event | Critical |

## Security and Compliance

### Operator Certification

Each operator must possess:
- A valid operator certificate (stored on a hardware security key if possible)
- Permission tokens for specific command classes (e.g., "may arm", "may disarm", "may deploy payload")
- A revocation status that is checked on every command

### Message Verification

Skipper verifies every received message:
- Signature valid (matches the transmitter's certificate)
- Sequence number in order (detects replay attacks)
- Timestamp within acceptable skew (detects old messages)
- Checksum correct (detects transmission errors)
- Sender is authorized for that message type

### Audit Logging

All transactions are logged:
- Command sent: time, operator, command text, signature
- Command received ACK: time, source node, ACK signature
- Command execution result: time, status (success/error), any side effects
- Unsolicited telemetry: time, source node, data summary, signature

Logs are saved to local storage and optionally uploaded after flight for forensic analysis.

## Hardware Considerations

### Computer Requirements

Skipper can run on:
- **Desktop / laptop:** Windows, macOS, Linux with standard telemetry radio interface
- **Tablet/mobile:** Android or iOS with Wi-Fi or USB radio dongle
- **Embedded SBC:** Raspberry Pi or similar for autonomous ground station operation

### Radio Interface

Skipper must support:
- Standard USB radio dongles (SiK, Wi-Fi USB adapters)
- Integrated Wi-Fi and Bluetooth (for tablet-based operation)
- Multiple radios simultaneously (for redundancy and channel switching)

### Power

Portable operation requires:
- Battery life of at least 4 hours during extended flight operations
- USB power bank capability for extended missions
- Low-power telemetry reception mode (reduced display refresh)

## Software Architecture

### Modular Design

Skipper's software is organized into independent modules:
- **Command Interface:** Operator input, button/keyboard/touch handling
- **Comms Stack:** Manage multiple radio channels, retransmit logic, failover
- **Telemetry Processor:** Parse, verify, and cache incoming telemetry
- **Display Engine:** Render real-time flight data, maps, system status
- **Mission Manager:** Upload, monitor, and execute autonomous missions
- **Data Logger:** Archive all transactions for post-flight analysis
- **Security Module:** Certificate verification, command signing, audit trail

### Testing and Simulation

A software-in-the-loop (SITL) simulator shall support:
- Simulation of all four communication channels
- Synthetic telemetry generation (normal and fault scenarios)
- Command verification without actual hardware
- Operator interface testing

## Work Tracking and Documentation

When developing Skipper features:

1. Document the operator workflow (how a user accomplishes a task)
2. Specify the command message format and any authentication steps
3. Define telemetry output format and verify signature
4. Ensure all security and logging requirements are met
5. Test with the simulator before flight testing
6. Archive any deprecated commands or protocols in documentation

---

For project-wide standards, see the root `AGENTS.md`.
