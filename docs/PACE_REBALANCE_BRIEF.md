# PACE Re-balance for the Merged Stern Stack — Owner Decision Brief (OD-19)

**Owner / engineer of record:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**Drafted by:** Claude (Anthropic), 2026-11-14, at the owner's direction of the same day: "re-compute PACE based on node capabilities and loading, balancing loading with fallback capacity. No single point of failure and no node having a single PACE tasking."
**License:** CC BY-SA 4.0 — see LICENSES/CC-BY-SA-4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Tool:** `tools/pace_balance.py` (scores every legal assignment; prints its inputs with `--show`)

## Why it has to change

Simon becomes one PB2-I plus a trust-module MCU (OD-18, B+), half the host compute of the other three stacks. Today Simon holds Flight Control A and Payload P, the heaviest standby load on the smallest node.

The two records of the current assignment also disagree. `avionics/WBS.md` §1.9 is a valid square. Root `AGENTS.md` §9 swaps River's and Simon's Watchdog and Comms cells, which leaves Watchdog with two A holders and no E. This brief uses §1.9 as "current".

## Rules applied

1. **No single point of failure:** every role has P, A, C and E on four different stacks.
2. **No single tasking:** every stack holds one level of every role.
3. River keeps Flight Control P (forward EDFs, nacelle sync; `AGENTS.md` §9 tasking).

Rules 1 and 2 together make the assignment a Latin square: 144 squares satisfy all three.

## How load is scored

Each stack's load is the sum of (role weight × level duty) divided by its compute capacity.

| Input | Value | Basis |
|---|---|---|
| Role weight | Flight Control 4, Comms 3, Payload 2, Watchdog 1 | [ASSUMED] relative real-time demand |
| Level duty | P 1.0, A 0.5 (hot standby), C 0.2, E 0.1 | [ASSUMED] |
| Capacity | full stacks 2 PB2-I, Simon 1 PB2-I | OD-18 |

The score is the worst stack load in normal flight and after the loss of any one stack; on a loss, every holder below the lost one moves up a level. The units are relative, not CPU percent. Bench loading replaces the assumptions when it exists.

**Robustness.** I re-ran the search under fifteen weight and duty sets. In every one, the best squares put Simon at Flight Control E or C and give it Watchdog at P or A. The direction of the change does not depend on the assumed numbers; the exact square does.

## Options

| | Current (§1.9) | **A. Keep every Primary** (recommended) | B. Best balance |
|---|---|---|---|
| Shepherd (WD / Comms / FC / Pay) | P / A / C / E | **P / A / E / C** | A / P / C / E |
| Inara | A / P / E / C | **C / P / A / E** | C / E / A / P |
| River | E / C / P / A | **E / C / P / A** | E / A / P / C |
| Simon | C / E / A / P | **A / E / C / P** | P / C / E / A |
| Cells changed | 0 | 7 | 12 |
| Busiest stack, normal | Simon 4.50 | Simon 3.60 | 3.00 (River, Simon) |
| Busiest stack, worst one-stack loss | Simon 6.80 | Simon 5.10 | Simon 4.40 |

**Option A** keeps each stack's Primary, so every stack keeps the job its bay, radios and harness were laid out for: Shepherd watchdog and authentication, Inara comms, River flight control, Simon payload and cargo oversight. Simon gives up Flight Control A (to Inara) and becomes Alternate Watchdog, which matches its old written tasking. Its worst-case load falls by a quarter.

**Option B** balances best but moves 12 of 16 cells: Simon becomes Watchdog P, Shepherd becomes Comms P, Inara becomes Payload P. Those primaries no longer match the hardware placement (cargo is Simon's neighbour; the Wi-Fi ground link and cameras were Inara's).

Simon is the busiest node per PB2-I in every option. Only more compute at the stern removes that.

## Checks (avionics set, `docs/DOC_TEMPLATES.md`)

| Check | Result |
|---|---|
| Electrical engineering | Load is CPU, not electrical: no rail changes in any option. Emissions: unchanged; PACE moves software roles, not radios. |
| Function | All options meet rules 1 to 3. A and B both drop Simon's Flight Control to C or E. Any stack can still fly the aircraft in a benign environment (`avionics/WBS.md` §1.9). |
| Structural integrity | Does not apply: software assignment. |
| Mechanism and component interactions | Inara becomes Flight Control A in option A, so its FC node runs the hot-standby control loop. Inara's FC node is a full Pilot + PB2-I, the same hardware as River's. Bus-end termination at Simon is unchanged. |
| Weight and balance | No change: no part moves. |
| Wire harness, fastener and mounting fit | Does not apply. |
| Thermal load | The hot-standby Flight Control load moves from Simon to Inara in both options. Simon's peak CPU, and so its heat, falls. Not yet quantified in watts. |

## Still unverified

1. Role weights and duties (bench loading on a PB2-I).
2. Whether the trust-module MCU can carry part of the Watchdog role, which would raise Simon's effective capacity. Not credited here.

## Owner decision

- [x] OD-19: PACE assignment — current / A (recommended) / **B**. **Decided 2026-11-14 by the owner: option B.** Applied the same day to root `AGENTS.md` §9 and `avionics/WBS.md` §1.9. On a decision, root `AGENTS.md` §9 and `avionics/WBS.md` §1.9 are both updated to the chosen square in one commit.
