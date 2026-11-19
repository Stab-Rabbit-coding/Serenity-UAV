# Ground Control Station (Skipper) — Agent Instructions

Adds Skipper-specific rules to root `AGENTS.md`, which wins wherever it speaks. Scope: GCS
software (command and control, telemetry display, mission planning), hardware interface and
communications middleware, operator interface, and test harnesses and simulators.

Skipper commands the UAV, receives telemetry, authenticates every command, and keeps a
real-time audit log of every flight operation and command/response transaction.

## Authoritative Files

- **`gcs/SKIPPER_SPEC.md`** is the specification: responsibilities, operator interface,
  operator certification, message format and verification, command priorities, telemetry
  rates, audit-log records, hardware, software modules, and the SITL simulator. Read it before
  designing or changing any Skipper interface, message, or platform behavior.
- External C2 channels: root `AGENTS.md` §1. FCC bands: `avionics/AGENTS.md` "External Communications
  Regulations Compliance".
- Ground-side radio loadout, link roles, and antennas: `gcs/WBS.md` §4.5 and
  `gcs/skipper/README.md`.

## Rules

- Every command Skipper sends shall be cryptographically signed; every message it receives
  shall be verified per `gcs/SKIPPER_SPEC.md` before it is acted on or displayed.
- Every transaction shall be logged; an operator override of automatic failover shall be logged.

## Work Tracking

When developing a Skipper feature:

1. Document the operator workflow (how a user accomplishes the task).
2. Specify the command message format and its authentication steps in `gcs/SKIPPER_SPEC.md`.
3. Define the telemetry output format and its signature verification.
4. Confirm every security and logging requirement is met.
5. Test with the simulator before flight testing.
6. Record deprecated commands or protocols in `gcs/SKIPPER_SPEC.md`, and open work in
   `gcs/WBS.md` (root §10 federation).
