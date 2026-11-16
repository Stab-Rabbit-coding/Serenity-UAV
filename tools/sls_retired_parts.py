#!/usr/bin/env python3
"""sls_retired_parts.py -- printed STLs that are still on disk but are NOT
part of the current airframe, so the SLS tools (sls_dfm_audit.py,
sls_print_orientation.py) neither audit nor orient them.

Each entry cites the decision that retired it.  The BOM / AUW ledger still
list some of these at quantity 1 (stale; WBS 0.13); this list follows the
design decisions, not the stale BOM rows.

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (Stab-Rabbit-coding)
AI note: Written by Claude Opus 5.5 (Anthropic) under the author's direction,
         2026-11-01.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

_MERGE = ("one-piece head+cargo FORWARD hull section (hull = 2 sections joined at "
          "the cargo/middle collar), commit d92c4f14 (2026-10-31), "
          "docs/BATTERY_TRIM_ENDURANCE_OPTIONS.md 'The merge'")
_AFT = ("one-piece middle+rear AFT hull section, tools/merge_middle_rear_shell.py "
        "(owner 2026-11-01: 'merge the middle and aft')")
_HEAD_CELL = ("single head cell replaced by the twin flat pack tray, commit d92c4f14, "
              "docs/BATTERY_TRIM_ENDURANCE_OPTIONS.md 'Printed parts'")

# path under airframe/stls : reason
RETIRED = {
    "fuselage/head_shell24.stl": "pre-2 mm head shell; superseded, then merged -- " + _MERGE,
    "fuselage/head_shell24_2mm_repaired.stl": "merge INPUT, not a print article -- " + _MERGE,
    "fuselage/cargo/cargo_sect_shell24_repaired.stl": "pre-2 mm cargo shell; superseded",
    "fuselage/cargo/cargo_sect_shell24_2mm_repaired.stl": "merge INPUT (and door/hinge "
    "generator source), not a print article -- " + _MERGE,
    "fuselage/head_cargo_splice_collar.stl": "retired -- " + _MERGE,
    "fuselage/cargo/battery_cradle.stl": "retired, hanger bosses removed -- " + _MERGE,
    "fuselage/head/head_cell_rail.stl": "retired -- " + _HEAD_CELL,
    "fuselage/head/head_cell_sled.stl": "retired -- " + _HEAD_CELL,
    "fuselage/head/head_cell_catch.stl": "retired -- " + _HEAD_CELL,
    "fuselage/middle_shell24_2mm_repaired.stl": "merge INPUT, not a print article -- " + _AFT,
    "fuselage/rear_shell24_2mm_repaired.stl": "merge INPUT, not a print article -- " + _AFT,
    "fuselage/middle_rear_splice_collar.stl": "retired -- " + _AFT,
    "fuselage/belly_panel.stl": "BOM qty 0 since the 2026-10-19 weight pass (keel tray, "
    "head battery bay gone)",
    "fuselage/battery_tray.stl": "BOM qty 0 (keel tray superseded by the twin pack tray)",
}
