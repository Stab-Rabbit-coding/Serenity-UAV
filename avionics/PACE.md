# PACE Failover Matrix and Per-Stack Tasking

**Revision:** Rev U, 2026-11-17. **Status:** in force — four-role record (OD-19 option B) until
gate G1 (OD-22) decides the six-role matrix.
**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (owner). Text moved verbatim from root
`AGENTS.md` §9 by Claude (Anthropic) at the owner's direction, 2026-11-17 (AGENTS.md review,
Q16). Root `AGENTS.md` §9 keeps the rule that gates changes to this file.
**License:** CC BY-SA 4.0 — see LICENSES/CC-BY-SA-4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)

Any change to a node's role or failover level shall be checked against this file and approved by
the owner before it is implemented.

## PACE per stack

Primary / Alternative / Contingency / Emergency:

| Stack | Watchdog | Comms | Flight Control | Payload |
| --- | --- | --- | --- | --- |
| Shepherd | A | P | C | E |
| Inara | C | E | A | P |
| River | E | A | P | C |
| Simon | P | C | E | A |

Re-balanced 2026-11-14 (owner, OD-19, option B) for the seven-node fleet: Simon is one PB2-I plus a
trust-module MCU, so it takes the lightest Primary and Flight Control E. Every role has four distinct
holders and every stack holds one level of every role. Basis: `docs/PACE_REBALANCE_BRIEF.md`,
`tools/pace_balance.py`. Corrects the earlier table, whose Watchdog column had two A holders and no E.

Two roles are being added to this matrix (owner direction 2026-11-16, plan
`docs/plans/2026-11-15-002-feat-ramp-intake-edf-cooling-plan.md` R41, NFP-TEDF-5): tail EDF and RCS
control, and thrust monitor and trim compensation. The matrix rules are revised for six roles and
the assignment is decided at gate G1 (OD-22); the table above is the four-role record until then.

## Radio assignment

Radio assignment follows the hardware each stack actually carries, not a fixed link name. The
current per-board radio complement and per-stack link priority are in `avionics/README.md`
"External Comms" and each board's own `.md`. Decisions:

- 2026-09-21 TACCO/Commo radio relocation: every stack's TACCO cape carries Wi-Fi + ZigBee and
  mLRS; Commo hosts 49 MHz and SiK.
- Rev T (approved 2026-09-29): any stack can key either Commo radio over CAN-FD / RS-485 / 1553C,
  and a PACE-aware PTT ownership lease decides which stack transmits. Losing the one Commo node
  drops every stack to Wi-Fi / ZigBee / mLRS.

## Per-stack tasking

- Shepherd: primary comms (high-bandwidth ground link) + alternate watchdog.
- Inara: payload and cargo control (Observer, winch, cameras and external sensors) + alternate
  flight control.
- River: forward EDF + nacelle tilt sync + primary flight control + alternate comms.
- Simon: aft EDF (provisional: which node commands the now flight-critical tail EDF and RCS valves is
  open under NFP-TEDF-2 / OD-22) + primary watchdog/fault-detect/failover/authentication (the
  trust-module MCU keeps its bus presence through a host reboot) + alternate payload.
