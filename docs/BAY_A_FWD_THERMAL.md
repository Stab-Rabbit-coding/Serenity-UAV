# Bay A Forward — Thermal Budget and Controls

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**AI note:** Drafted by Claude (Claude Opus 5.5, Anthropic) under the
author's direction, 2026-11-01, per `AGENTS.md` §3. AI-generated and not yet
reviewed.
**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Plan:** `docs/plans/2026-11-01-001-feat-bay-a-forward-adoption-plan.md`
U4 (R5; KTD4, KTD5).
**Tool:** `tools/bay_a_thermal_budget.py` (tests:
`tools/tests/test_bay_a_thermal_budget.py`).

## 1. Result

**BLOCKER (owner decision).** No control tier holds CN1 at its sustained
all-radio peak (8.3 W) under the 185 °F (85 °C) limit. The average case (CN1 3
W) first passes at the fan tier, with 32.8 °F (18.2 K) of margin. At the fan
tier, the highest CN1 dissipation that can be sustained is 5.49 W.

Every material property and film coefficient is ASSUMED, so these numbers are
PROVISIONAL (KTD4). The design ambient of 104 °F (40 °C) is ASSUMED, pending
owner confirmation. The 185 °F (85 °C) limit is the PB2-I **module** rating, not
an owner requirement.

The side-by-side Bay A had the same enclosed pouches in the same head, so this
is not a new problem introduced by the forward layout. The forward layout only
made it visible.

## 2. Heat paths (thermal routes)

Tiers are cumulative (KTD5): each tier adds its control to the ones above.

0. **None.** Board → pouch film → bay air → head skin → outside air
   (Bay A, Y 60–170).
1. **Gap pad.** PB2-I → pad → pouch wall → mount floor → bay air (CN1
   drawer floor Z 203–206; FC1 shelf Z 228.5–230.5).
2. **Mount bond.** Floor → bond + skin → outside air. CN1 conducts
   directly through the drawer bonded to the chin skin (Y 60–120). FC1
   conducts through the drawer side walls.
3. **Vent slots.** Through-flow from the bow sensor bay, which is open to
   outside air, raises the internal film (bay insert back wall → Bay A,
   Y 20–60).
4. **Fan.** A thermostatic 5 V fan on the vent path adds forced convection
   (between the bay insert and CN1, Y 40–60).

The vent slots and the fan are **not yet cut or placed**. Their geometry waits
on the blocker decision (§4). The pitot hose turn (Y 46–55) and the Observer to
CN1 trunk (Y 80–86) bound the vent path. Any vent or fan body shall be gated in
`tools/head_layout_fit.py`.

## 3. Budget (tool output, 2026-11-01)

Board-air temperature at a 104 °F (40 °C) ambient, in °C as the tool reports it.
A negative margin is over the 185 °F (85 °C) limit.

| Tier | Case | Node | Temp (°C) | Margin (K) |
| --- | --- | --- | ---: | ---: |
| none | average | CN1 | 178.8 | −93.8 |
| none | average | FC1 | 127.2 | −42.2 |
| none | peak | CN1 | 397.9 | −312.9 |
| none | peak | FC1 | 189.9 | −104.9 |
| pad | average | CN1 | 161.5 | −76.5 |
| pad | average | FC1 | 120.0 | −35.0 |
| pad | peak | CN1 | 350.0 | −265.0 |
| pad | peak | FC1 | 182.7 | −97.7 |
| mount | average | CN1 | 116.9 | −31.9 |
| mount | average | FC1 | 100.5 | −15.5 |
| mount | peak | CN1 | 239.9 | −154.9 |
| mount | peak | FC1 | 131.1 | −46.1 |
| vents | average | CN1 | 87.2 | −2.2 |
| vents | average | FC1 | 75.2 | 9.8 |
| vents | peak | CN1 | 160.0 | −75.0 |
| vents | peak | FC1 | 100.4 | −15.4 |
| fan | average | CN1 | 66.8 | 18.2 |
| fan | average | FC1 | 61.5 | 23.5 |
| fan | peak | CN1 | 105.5 | −20.5 |
| fan | peak | FC1 | 81.9 | 3.1 |

The highest sustained CN1 dissipation (both nodes at the limit) is 0.00 W at
none, 0.05 W at pad, 0.33 W at mount, 2.84 W at vents, and 5.49 W at fan.

The model is steady state. It credits no thermal mass, so a short transmit burst
above 5.49 W is not ruled out. Proving that needs a transient model and measured
pouch time constants.

## 4. Decisions needed

1. **Sustained transmit limit.** Do one of the following:
    - cap CN1's sustained dissipation at or below the fan-tier figure, with
      firmware thermal throttling of TACCO transmit duty driven by an on-board
      temperature sensor; or
    - accept a better heat path, such as a metal heat spreader, which comes
      lower in the owner material order.
2. **Design ambient.** Confirm 104 °F (40 °C), or set the owner's value.
3. **Inputs to cite.** Pouch fabric and contact conductance, the PA12-CF
   through-thickness conductivity, the gap pad, and the film coefficients. Bench
   measurement of a powered pouch in the printed bay is the preferred source.
