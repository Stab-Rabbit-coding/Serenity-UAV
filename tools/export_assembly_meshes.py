"""Export every placed part of the airframe master assembly as a hull-frame STL.

Run under FreeCAD's headless interpreter:

    freecadcmd tools/export_assembly_meshes.py -- OUT_DIR

It executes ``airframe/FreeCAD-scripts/serenity_assembly.py`` UNCHANGED —
the airframe assembly is the authority for where every part sits — except
that the document save is redirected to OUT_DIR so no tracked file is
touched.  Each ``Mesh::Feature`` is written with its Placement applied, as
``OUT_DIR/<Label>.stl``, plus ``OUT_DIR/manifest.json`` (label -> file, source
STL, facet count).  ``tools/airframe_interface_census.py`` consumes the
result.

This is the "airframe rules, local informs" half of the joint analysis
(owner direction 2026-10-03): joints are checked where the AIRFRAME puts the
parts, never where a local context file would like them to be.

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, per AGENTS.md AI attribution.  License: CERN-OHL-W-2.0 —
    see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""

import json
import os
from typing import Any
import sys

import FreeCAD as App  # noqa: N813  (FreeCAD's own import convention)

HERE = os.path.dirname(os.path.abspath(__file__))
ASSEMBLY = os.path.join(HERE, "..", "airframe", "FreeCAD-scripts", "serenity_assembly.py")


def main(out_dir: str) -> None:
    """Run the master assembly and export each placed mesh."""
    os.makedirs(out_dir, exist_ok=True)
    src = open(ASSEMBLY, encoding="utf-8").read()
    # Namespace with a non-entry __name__ so the module does not auto-run;
    # __file__ keeps its own path arithmetic (AIRFRAME, STL_DIR) correct.
    ns: dict[str, Any] = {"__name__": "census_export", "__file__": os.path.abspath(ASSEMBLY)}
    exec(compile(src, ASSEMBLY, "exec"), ns)  # noqa: S102  (trusted repo file)
    ns["OUTPUT"] = os.path.join(out_dir, "SerenityAssembly_census.FCStd")
    ns["assemble"]()
    doc = App.ActiveDocument
    manifest = {}
    for obj in doc.Objects:
        if obj.TypeId != "Mesh::Feature":
            continue
        mesh = obj.Mesh.copy()
        mesh.transform(obj.Placement.toMatrix())
        safe = "".join(c if c.isalnum() or c in "_-" else "_" for c in obj.Label)
        path = os.path.join(out_dir, safe + ".stl")
        mesh.write(path)
        manifest[safe] = {"file": path, "facets": mesh.CountFacets}
    with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
    print(f"[export] {len(manifest)} placed meshes -> {out_dir}", flush=True)


# freecadcmd passes its own args first; take the one after "--".
_args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if not _args:
    raise SystemExit("usage: freecadcmd tools/export_assembly_meshes.py -- OUT_DIR")
main(_args[0])
