# Skipper Ground Control Station — Interface and Platform Specification

Governing file: `gcs/AGENTS.md` — this document holds the operator-interface detail, message
format, command-priority and telemetry-rate tables, hardware/platform requirements, and
software module list that `gcs/AGENTS.md` points to. For project-wide standards see the root
`AGENTS.md`.

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

All messages between Skipper and Serenity shall use a standard message wrapper with:

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
