# Open-Secure-ESC board fixture

License: CERN-OHL-P-2.0 — see the source repository's `LICENSE` (SPDX-License-Identifier: CERN-OHL-P-2.0).
This README: CC BY-SA 4.0 — see LICENSES/CC-BY-SA-4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)

`open_secure_esc_6s_50a_can485_faraday.kicad_pcb` is an unmodified copy of a board from the
owner's public Open-Secure-ESC repository, vendored so that
`tools/tests/test_nacelle_esc_service.py` runs in CI and in cloud sessions. The test used to read
it from an absolute path on the owner's workstation, so it failed everywhere else (root `WBS.md`
§0.12 "Three tests fail on main", Rev U plan S4).

| Field | Value |
| --- | --- |
| Source | https://github.com/Stab-Rabbit-coding/Open-Secure-ESC |
| Path | `builds/6s/50A/CAN_485_faraday/kicad/open_secure_esc_6s_50a_can485_faraday.kicad_pcb` |
| Commit | `1af3ea4a191f134dd0dc663db491fd515ae5729e` (2026-10-18) |
| Author | Steve Griffing (GitHub `Stab-Rabbit-coding`) |
| Licence | CERN-OHL-P-2.0 (permissive; compatible with this repository's CERN-OHL-W-2.0 hardware licence) |
| Vendored | 2026-11-21 by Claude (Anthropic) under the owner's direction |

This is a measurement fixture, not the flight board: OD-3 (2026-11-12) chose the 70 A
Open-Secure-ESC, whose design is `tools/esc70_design.json` and which has no committed
`.kicad_pcb` yet. Refresh this copy (and the commit above) when the source board changes, or
when a 70 A board exists and the test moves to it.
