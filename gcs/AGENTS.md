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

## Interface, Protocol, and Platform Specification

**`gcs/SKIPPER_SPEC.md`** is the authoritative specification for the details an implementation
needs: operator-interface design (command authentication, telemetry display fields, mission
planning capabilities), the message-wrapper format, the command-priority table
(CRITICAL/HIGH/MEDIUM/LOW with channel and retransmit intervals), the telemetry data-rate table
(nominal and degraded rates per data type), computer/radio/power hardware requirements, the
seven software modules, and the SITL simulator requirements. Read it before designing or
changing any Skipper interface, message, or platform behavior.

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
