#!/usr/bin/env python3
"""Set the Value property of reference designators in a .kicad_sch/.kicad_pcb.

Text-level edit of the ``(property "Value" ...)`` inside the placed symbol /
footprint whose Reference matches; used for datasheet-driven value fixes
(e.g. TLV62569 feedback dividers, avionics/WBS.md U7.1e).

Attribution: authored by Claude Opus 5.5 (Anthropic), 2026-09-26.

Usage::

    python3 tools/kicad_set_value.py FILE REF=VALUE [REF=VALUE ...]
"""

import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from kicad_relink import prop, top_blocks  # noqa: E402  pylint: disable=C0413


def main():
    """Apply REF=VALUE pairs to one file; fail if any REF is missing."""
    path = pathlib.Path(sys.argv[1])
    want = dict(a.split("=", 1) for a in sys.argv[2:])
    t = path.read_text(encoding="utf-8")
    head = "footprint" if path.suffix == ".kicad_pcb" else "symbol"
    done = set()
    for s, e in reversed(list(top_blocks(t, head))):
        ref = prop(t[s:e], "Reference")
        if ref in want:
            blk = re.sub(r'(\(property "Value"\s+)"(?:[^"\\]|\\.)*"',
                         lambda m, v=want[ref]: m.group(1) + '"%s"' % v,
                         t[s:e], count=1)
            t = t[:s] + blk + t[e:]
            done.add(ref)
    missing = set(want) - done
    if missing:
        raise SystemExit("%s: not found %s" % (path.name, sorted(missing)))
    path.write_text(t, encoding="utf-8")
    print("%s: set %s" % (path.name, ", ".join(sorted(done))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
