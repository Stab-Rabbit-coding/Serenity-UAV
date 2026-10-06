#!/usr/bin/env python3
"""Remove stale components (and their orphaned copper) from a KiCad PCB.

"Stale" is decided by KiCad itself, not by guesswork: the script runs
``kicad-cli pcb drc --schematic-parity`` and acts on

* ``extra_footprint``      -- footprint with no schematic symbol, and
* ``duplicate_footprints`` -- two footprints sharing one reference; the
  copy whose footprint ID matches the schematic's Footprint field is
  kept, the other removed (if neither/both match, nothing is removed and
  the pair is reported for a human decision).

Footprints with the ``board_only`` attribute (mounting holes, fiducials,
logos) are never reported by parity and therefore never touched.  After
removal, track segments / vias / arcs whose net no longer reaches any pad
are deleted, so no copper is left stranded.  Owner request 2026-09-26
(avionics/WBS.md U7.3): the relink / swap tooling must clean up stale
PCB components.

Attribution: authored by Claude Opus 5.5 (Anthropic), 2026-09-26.

Usage::

    python3 tools/kicad_prune_stale.py BOARD.kicad_pcb [--dry-run]
"""

import argparse
import json
import pathlib
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
# pylint: disable=wrong-import-position
from kicad_relink import block_end, prop, top_blocks  # noqa: E402


def parity(pcb):
    """Return the schematic_parity list from kicad-cli DRC JSON."""
    with tempfile.TemporaryDirectory() as tmp:
        out = pathlib.Path(tmp) / "drc.json"
        subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json",
                        "--schematic-parity", "-o", str(out), str(pcb)],
                       check=False, capture_output=True)
        if not out.exists():
            raise SystemExit("kicad-cli could not load %s" % pcb)
        return json.loads(out.read_text(encoding="utf-8"))["schematic_parity"]


def sch_footprints(pcb):
    """{reference: Footprint field} from the sibling schematic."""
    sch = pcb.with_suffix(".kicad_sch")
    t = sch.read_text(encoding="utf-8")
    return {prop(t[s:e], "Reference"): prop(t[s:e], "Footprint")
            for s, e in top_blocks(t, "symbol")}


MECH_REF = re.compile(r"^(MH|H|FID|LOGO|MP|MK)\d*", re.I)


def is_mechanical(fpb):
    """True for mounting holes / fiducials / logos: never deleted."""
    if MECH_REF.match(prop(fpb, "Reference") or ""):
        return True
    pads = re.findall(r'\(pad "[^"]*" (\w+)', fpb)
    return all(kind == "np_thru_hole" for kind in pads) or \
        not re.search(r'\(pad [\s\S]*?\(net ', fpb)


def mark_board_only(fpb):
    """Add board_only to the footprint's (attr ...) (create it if absent)."""
    m = re.search(r"\(attr([^)]*)\)", fpb)
    if m:
        if "board_only" in m.group(1):
            return fpb
        return fpb[:m.end() - 1] + " board_only" + fpb[m.end() - 1:]
    i = fpb.index("\n", fpb.index("(layer"))
    return fpb[:i] + "\n\t\t(attr board_only)" + fpb[i:]


def live_nets(text):
    """Set of net names that reach at least one footprint pad."""
    live = set()
    for s, e in top_blocks(text, "footprint"):
        fpb = text[s:e]
        for m in re.finditer(r'\(pad "', fpb):
            pad = fpb[m.start():block_end(fpb, m.start())]
            n = re.search(r'\(net (?:\d+ )?"((?:[^"\\]|\\.)*)"\)', pad)
            if n:
                live.add(n.group(1))
    return live


def copper_net(blk, ids):
    """Net name of a segment/via/arc block (numbered or named form)."""
    m = re.search(r'\(net (\d+)(?: "((?:[^"\\]|\\.)*)")?\)', blk)
    if not m:
        return None
    return m.group(2) if m.group(2) is not None else ids.get(m.group(1))


def main():
    """Prune stale footprints and orphan copper; print what was removed."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pcb")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    pcb = pathlib.Path(args.pcb)
    t = pcb.read_text(encoding="utf-8")
    fps = {}
    for s, e in top_blocks(t, "footprint"):
        u = re.search(r'\(uuid "([^"]+)"\)', t[s:e])
        fps[u.group(1) if u else None] = (s, e)
    want = sch_footprints(pcb)
    before = live_nets(t)

    kill, review, mech, mech_refs = set(), [], set(), {}
    for v in parity(pcb):
        uuids = [i.get("uuid") for i in v.get("items", [])]
        if v["type"] == "extra_footprint":
            for u in (u for u in uuids if u in fps):
                if is_mechanical(t[fps[u][0]:fps[u][1]]):
                    mech.add(u)
                else:
                    kill.add(u)
        elif v["type"] == "duplicate_footprints":
            pair = [u for u in uuids if u in fps]
            ids = {u: re.match(r'\(footprint\s+"([^"]*)"',
                               t[fps[u][0]:fps[u][1]]).group(1) for u in pair}
            ref = prop(t[fps[pair[0]][0]:fps[pair[0]][1]], "Reference")
            good = [u for u in pair if ids[u] == want.get(ref)]
            if all(is_mechanical(t[fps[u][0]:fps[u][1]]) for u in pair):
                mech.update(pair)
            elif len(good) == 1:
                kill.update(u for u in pair if u != good[0])
            else:
                review.append((ref, ids))

    # Mechanical extras (mounting holes, fiducials) are legitimate board
    # items: mark them board_only instead of deleting them.
    marked = []
    used = {prop(t[s:e], "Reference") for s, e in top_blocks(t, "footprint")}
    seen_refs = set()
    for u in sorted(mech, key=lambda k: fps[k][0]):
        s, e = fps[u]
        ref = prop(t[s:e], "Reference") or ""
        if not ref or ref in seen_refs:
            n = 1
            while "MH%d" % n in used:
                n += 1
            ref = "MH%d" % n
            used.add(ref)
        seen_refs.add(ref)
        mech_refs[u] = ref
    for u in sorted(mech, key=lambda k: -fps[k][0]):
        s, e = fps[u]
        blk = re.sub(r'(\(property "Reference"\s+)"(?:[^"\\]|\\.)*"',
                     lambda m, r=mech_refs[u]: m.group(1) + '"%s"' % r,
                     t[s:e], count=1)
        marked.append(mech_refs[u])
        t = t[:s] + mark_board_only(blk) + t[e:]
    fps = {}
    for s, e in top_blocks(t, "footprint"):
        m = re.search(r'\(uuid "([^"]+)"\)', t[s:e])
        fps[m.group(1) if m else None] = (s, e)

    removed = []
    for u in sorted(kill, key=lambda k: -fps[k][0]):
        s, e = fps[u]
        removed.append("%s (%s)" % (prop(t[s:e], "Reference"),
                                    re.match(r'\(footprint\s+"([^"]*)"',
                                             t[s:e]).group(1)))
        t = t[:s] + t[e:]

    # Orphan copper: ONLY routing whose net lost its last pad because a
    # footprint was removed above.  Pre-existing pad-less copper (e.g.
    # routing for parts not yet placed) is reported, never deleted.
    after = live_nets(t)
    killed_nets = before - after
    ids = dict(re.findall(r'^\t\(net (\d+) "((?:[^"\\]|\\.)*)"\)', t, re.M))
    orphan, preexisting = 0, 0
    for head in ("segment", "via", "arc"):
        for s, e in reversed(list(top_blocks(t, head))):
            name = copper_net(t[s:e], ids)
            if name in killed_nets:
                t = t[:s] + t[e:]
                orphan += 1
            elif name and name not in after:
                preexisting += 1
    if preexisting:
        print("NOTE: %d pad-less copper items on nets with no footprint pads "
              "(not removed; likely routing for unplaced parts)" % preexisting)

    for r in removed:
        print("stale footprint removed: %s" % r)
    for r in marked:
        print("mechanical footprint kept, marked board_only: %s" % r)
    for ref, ids_ in review:
        print("REVIEW duplicate %s -- cannot pick automatically: %s"
              % (ref, ids_))
    print("%s: %d stale footprints, %d orphan copper items%s" % (
        pcb.name, len(removed), orphan, " (dry run)" if args.dry_run else ""))
    if not args.dry_run:
        pcb.write_text(t, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
