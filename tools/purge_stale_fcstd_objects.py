"""Remove superseded geometry from the archived FreeCAD assembly (LG-10.7).

`airframe/freecad/assembly/SerenityAssembly.FCStd.bak2` is the only FreeCAD
document tracked in the repo -- `.gitignore` excludes `*.FCStd`, so the live
`airframe/Serenity-Assembled.FCStd` is a generated artifact rebuilt by
`airframe/FreeCAD-scripts/serenity_assembly.py`, and this `.bak2` survives only
as the historical placement reference the Rev R1 coordinate standardisation was
extracted from (see `tools/bake_hull_frame.py` COMPONENTS, which is the actual
single source of truth for those placements today).

It still carried three generations of superseded geometry:

  * `leg_1..4_scaled24`, `foot_1..4_scaled24` -- the misubisu Thingiverse
    single-blade legs and their pads (CC BY 4.0), retired by the Rev R6
    one-piece leg frame and the canonical tri-pad foot.
  * `nacelle_port_revq`, `nacelle_stbd_revq` -- Rev Q nacelles, retired by
    Rev S (`nacelles/nacelle_{port,stbd}_revs.stl`).

What remains is exactly the set `bake_hull_frame.py` still recognises: the four
fuselage shells and the two wings.  LG-10.7 named only `leg_4_scaled24` and
`nacelle_port_revq`; purging literally would have left three legs beside four
feet and one Rev Q nacelle, so the whole superseded set goes (owner decision,
2026-08-17).  The `Union`..`Union003` Strong-Leg booleans that item also named
were already gone.

Idempotent: objects that are absent are skipped, so a second run is a no-op.

Author  : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note : Authored by Claude (model: Claude Opus 5, Anthropic) under the
          author's direction, 2026-08-17, per AGENTS.md AI attribution.
License : CC BY-SA 4.0  <https://creativecommons.org/licenses/by-sa/4.0/>

Run: freecadcmd tools/purge_stale_fcstd_objects.py
     (FreeCAD's own interpreter -- the FreeCAD module is not importable from
     system python3)
"""

import os
import sys

import FreeCAD  # noqa: F401  (provided by the FreeCAD interpreter)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DOC_PATH = os.path.join(REPO_ROOT, "airframe", "freecad", "assembly",
                        "SerenityAssembly.FCStd.bak2")

STALE = tuple(
    [f"leg_{i}_scaled24" for i in range(1, 5)]
    + [f"foot_{i}_scaled24" for i in range(1, 5)]
    + ["nacelle_port_revq", "nacelle_stbd_revq"]
)
# Guard: these must survive, or the document has stopped being a placement
# reference and the purge list is wrong.
KEEP = ("Cargo_Shell", "Head_Shell", "Middle_Shell", "Rear_Shell",
        "Wing_Port", "s_wing_stbd_s1223_revo")


def main():
    doc = FreeCAD.openDocument(DOC_PATH)
    before = sorted(o.Name for o in doc.Objects)
    print(f"objects before ({len(before)}): {before}")

    removed = []
    for name in STALE:
        if doc.getObject(name) is not None:
            doc.removeObject(name)
            removed.append(name)

    after = sorted(o.Name for o in doc.Objects)
    missing = [k for k in KEEP if k not in after]
    if missing:
        print(f"ABORT -- purge would drop required objects: {missing}")
        FreeCAD.closeDocument(doc.Name)
        sys.exit(1)

    doc.recompute()
    doc.save()
    print(f"removed ({len(removed)}): {removed}")
    print(f"objects after ({len(after)}): {after}")
    FreeCAD.closeDocument(doc.Name)


main()
