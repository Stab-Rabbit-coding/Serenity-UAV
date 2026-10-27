---
title: Mass Diet and Two-Sortie Mission - Plan
type: feat
date: 2026-10-26
artifact_contract: ce-unified-plan/v1
artifact_readiness: requirements-only
product_contract_source: ce-brainstorm
---

# Mass Diet and Two-Sortie Mission - Plan

**Author:** Claude (Claude Opus 5.5, Anthropic), under the direction of Stab-Rabbit-coding, per `AGENTS.md` §3.
**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Sources:** `docs/flight_envelope.md` §6 (endurance model, `tools/flight_envelope_endurance.py`); `current-specification/auw_ledger.json` (mass breakdown); momentum theory as given in the `aeronautical-engineering` skill, `references/propulsion.md` §1.

---

## Goal Capsule

- **Objective.** Make the aircraft's mission flyable on the EDF powerplant. Remove about 555 g, and split the README Nominal Mission Profile into a delivery sortie and a retrieval sortie, each flown on fresh cells.
- **Authority.** Owner decisions recorded below > `AGENTS.md` > this plan.
- **Open blocker.** The retrieval sortie does not fit the available endurance (R9). This plan records it as an unmet requirement with a propulsion decision gate; it does not close it.
- **Not in scope.** A propulsion change (larger fans or open props). That is the decision gate's subject, not this plan's work.

---

## Product Contract

### Problem Frame

The derived endurance target, 318 s airborne on one flight, is not met. Two cells with the payload give about 61 s of hover on the PLANNING case and 85 s on the NOMINAL case (`docs/flight_envelope.md` §6). Battery capacity cannot close the gap, because added cell mass raises hover power faster than it adds energy. Momentum theory puts the tandem 64 mm nacelles at a hover-power floor of about 2.7–3.9 kW. That suggests even 61 s may be optimistic: about 42–59 s is likely at realistic fan and motor efficiency. Hover endurance scales with mass to the −1.5 power, so mass cuts help only modestly. The owner chose to keep the EDFs and the Serenity form, cut mass where the trade-off is acceptable, and re-scope the mission.

### Key Decisions

- KD1. Drop the 500 W/m² EMI design objective and the per-board Faraday hardening: ferrites, the Flight Engineer enclosure, bonding straps and the node foil pouches, about −230 g. (session-settled: user-directed — rejected: keeping the hardening.)
- KD2. Lighten the landing gear and accept a lower crash rating than the 4 ft drop (LG-17), about −150 to −250 g. (session-settled: user-directed — rejected: keeping the 4 ft rating.)
- KD3. Merge two stacks into NoNFO-Pilot boards, giving 2 merged stacks plus 2 Pilot + TACCO stacks, while keeping four-level PACE, about −100 to −150 g. (session-settled: user-directed — rejected: keeping the uniform 8-node set.)
- KD4. Keep the 2 mm hull shells. (session-settled: user-directed — rejected: thinner shells.)
- KD5. Fly the mission as two sorties: delivery, then retrieval on fresh cells. (session-settled: user-approved — rejected: landing beside the platform, a static platform, keeping a single sortie.)
- KD6. Record retrieval as an open gap with a propulsion decision gate. (session-settled: user-approved — rejected: deferring retrieval to a later capability, and dropping the 30 % reserve.)
- KD7. Keep the EDF powerplant for now. (session-settled: user-approved — rejected for this plan: open-prop tilt-rotor, larger single fans.)

### Requirements

**Mass**

- R1. Hover AUW, two cells plus payload, shall fall from 6,318 g to 5,763 g or less (−555 g), measured on the mass ledger.
- R2. The EMI hardening shall be removed without losing signal integrity on board: the boards still pass their own EMC targets for an ordinary electrical environment, and the README and AGENTS design objective is updated to match.
- R3. The lighter landing gear shall still protect the aircraft and cells at a new drop height that the owner names. The gear failure hierarchy (fuse before mount) is kept.
- R4. With the merged stacks, PACE shall still give four independent failover levels for every flight-critical function. Each stack type's isolation boundaries shall be stated.

**Mission**

- R5. Sortie 1 (delivery): take off with the payload already loaded, transit, lower and release, return and land. Budget 72 s airborne at a 30 m stand-off, or 94 s with the 30 % reserve.
- R6. Sortie 2 (retrieval): take off, transit, find, synchronise, attach and lift, reel in, close, return and land. Budget 137 s airborne at a 30 m stand-off, or 178 s with reserve.
- R7. Stand-off is 30 m (98 ft), down from the 150 m assumed in `docs/flight_envelope.md` §6.2.
- R8. Winch speed is raised to 0.3 m/s from 0.1 m/s, subject to the winch specification's load and line limits.
- R9. **Unmet.** The available hover endurance after the diet is about 70 s (PLANNING) or 98 s (NOMINAL). Sortie 1 fits only on NOMINAL. Sortie 2 needs about 150–180 s and does not fit. R9 stays open until the decision gate (R10) closes it.
- R10. **Propulsion decision gate.** After a tandem-pair thrust-stand test measures hover power, the owner decides between: accepting a shortened retrieval, a larger-fan nacelle, or an open-prop tilt-rotor.

> **WARNING**
>
> Neither sortie shall be flown as a full profile until a bench discharge and a
> tandem-pair thrust-stand test confirm hover endurance. First flights are hover
> tests, with their duration set by the measured endurance and ending before the
> RTL trigger.

### Success Criteria

- The mass ledger shows 5,763 g or less for two cells plus payload.
- Sortie 1 is flown within its budget, with reserve, on measured endurance.
- The R10 gate is decided with thrust-stand data in hand.

### Scope Boundaries

- Thinner shells are out (KD4).
- Changing the propulsion is the R10 gate's outcome, not this plan's work.
- The split battery, rail and Flight Engineer plans (`docs/plans/2026-10-26-001-…`, `-002-…`) stand. Dropping the EMI hardening changes the Flight Engineer enclosure line in plan 002; planning reconciles that.

### Outstanding Questions

- Q1 (owner). What new drop height for the lighter gear?
- Q2 (planning). Does the NoNFO-Pilot board's single PocketBeagle 2 Ethernet port (RMII2) still allow the Ethernet ring with two merged stacks, or does the ring change? (From project notes; re-check against the NoNFO requirements branch.)
- Q3 (planning). Which EMC targets replace 500 W/m² (FCC Part 15 class, or a named field strength)?
- Q4 (owner). Is the 30 m stand-off acceptable for the RF-environment leg once that environment is no longer high-field?
