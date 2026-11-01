"""
build_guide_card_renders.py — per-card highlight renders for the graphical build guide.

Renders one PNG per build-guide card from the placed meshes of the FreeCAD
master assembly (exported by tools/export_assembly_meshes.py).  Each view
lists the assembly labels it is ABOUT; those render in the highlight colour
and every other part renders in a neutral ghost grey, assembly-manual style.
The camera is orthographic and auto-framed on the highlighted parts, so a
card never has to restate coordinates that the assembly already owns.

The view list is written by tools/gen_build_guide_cards.py (the single card
spec); this script only renders it:

    blender --background --python build_guide_card_renders.py -- \
        MESH_DIR VIEWS_JSON OUT_DIR

VIEWS_JSON: [{"name": "card06", "highlight": ["Wing_Root_Flange", ...],
              "hide": ["Dorsal_Antenna_Fin"], "dir": [x, y, z],
              "margin": 1.25}, ...]
A highlight/hide entry matches any label that STARTS with it.  An empty
highlight list renders the whole aircraft in the highlight colour.

Engine: Workbench (flat studio shading + object outlines).  It is fast,
deterministic, and reads like a printed assembly manual; Cycles realism is
for the pngs/ stills (serenity_render_views.py).

Aircraft datum R2 (tools/hull_datums.py): X +port, Y +aft (nose tip Y 0),
Z +dorsal (3.0 in gear ground plane Z 0) — matches Blender world axes.

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, 2026-10-31, per AGENTS.md AI attribution.
License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0
(SPDX-License-Identifier: CERN-OHL-W-2.0)
"""

import json
import os
import sys

import bpy
from mathutils import Vector

HIGHLIGHT = (1.00, 0.36, 0.00)  # safety orange (Workbench studio light washes it toward tan)
GHOST = (0.86, 0.86, 0.85)  # light grey, low contrast against the highlight
RES = (1100, 640)


def parse_args():
    """Return (mesh_dir, views_json, out_dir) from the args after '--'."""
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) != 3:
        raise SystemExit("usage: blender -b -P build_guide_card_renders.py -- MESH_DIR VIEWS_JSON OUT_DIR")
    return args


def setup_scene():
    """Empty the scene and configure the Workbench renderer."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x, scene.render.resolution_y = RES
    scene.render.film_transparent = True  # card background shows through
    shading = scene.display.shading
    shading.light = "STUDIO"
    shading.color_type = "OBJECT"
    shading.show_object_outline = True
    shading.object_outline_color = (0.10, 0.10, 0.12)
    shading.show_cavity = True
    shading.cavity_type = "WORLD"
    scene.display.render_aa = "8"
    scene.view_settings.view_transform = "Standard"
    return scene


def import_parts(mesh_dir):
    """Import every manifest mesh once; return {label: object}."""
    with open(os.path.join(mesh_dir, "manifest.json"), encoding="utf-8") as fh:
        manifest = json.load(fh)
    objs = {}
    for label, entry in sorted(manifest.items()):
        bpy.ops.wm.stl_import(filepath=entry["file"])
        obj = bpy.context.selected_objects[0]
        obj.name = label
        objs[label] = obj
    return objs


def matches(label, prefixes):
    """True if label starts with any prefix."""
    return any(label.startswith(p) for p in prefixes)


def world_bounds(objs):
    """Axis-aligned world bounds of a set of objects."""
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def render_view(scene, objs, view, out_dir):
    """Colour, frame, and render one card view."""
    hide = view.get("hide", [])
    hi_pref = view.get("highlight", [])
    shown, focus = [], []
    for label, obj in objs.items():
        obj.hide_render = matches(label, hide)
        if obj.hide_render:
            continue
        shown.append(obj)
        is_hi = (not hi_pref) or matches(label, hi_pref)
        obj.color = (*(HIGHLIGHT if is_hi else GHOST), 1.0)
        if is_hi:
            focus.append(obj)
    if not focus:
        raise SystemExit(f"{view['name']}: highlight {hi_pref} matched no part")
    lo, hi = world_bounds(focus)
    centre = (lo + hi) / 2
    radius = max((hi - lo).length / 2, 30.0)
    direction = Vector(view.get("dir", (1.0, -1.0, 0.8))).normalized()
    cam_data = bpy.data.cameras.new(view["name"])
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 2.0 * radius * view.get("margin", 1.25)
    cam_data.clip_end = 10000.0
    cam = bpy.data.objects.new(view["name"], cam_data)
    scene.collection.objects.link(cam)
    cam.location = centre + direction * 2500.0
    cam.rotation_euler = (centre - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam
    scene.render.filepath = os.path.join(out_dir, view["name"] + ".png")
    bpy.ops.render.render(write_still=True)
    print(f"[cards] {view['name']}: {len(focus)} highlighted / {len(shown)} shown", flush=True)


def main():
    """Render every view in VIEWS_JSON."""
    mesh_dir, views_json, out_dir = parse_args()
    os.makedirs(out_dir, exist_ok=True)
    scene = setup_scene()
    objs = import_parts(mesh_dir)
    with open(views_json, encoding="utf-8") as fh:
        views = json.load(fh)
    for view in views:
        render_view(scene, objs, view, out_dir)
    print(f"[cards] {len(views)} views -> {out_dir}", flush=True)


if __name__ == "__main__":
    main()
