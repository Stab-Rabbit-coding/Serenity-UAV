#!/usr/bin/env python3
"""
Automated Project/Archive Index agent for Serenity UAV.

Regenerates PROJECT_INDEX.md (active files) and ARCHIVE_INDEX.md (archived
files) from scratch on every run by walking the current file tree, so the
indexes can never drift from reality and can never accumulate the
orphaned-line corruption the previous append-only generator produced (every
rename/archival dropped an entry's path line but left its wrapped
description lines behind forever; see git history of this file and
docs/DOCUMENTATION_RECONCILIATION_2026-07-28.md item 2). Both index files are
authoritative build output of this script — do not hand-edit them, edit this
generator instead.

Each entry is one line: filename, a short one-line description mined from
the file itself where possible (Markdown H1, Python docstring, OpenSCAD/C
header comment, STL binary header marker, BOM row/item count), and a
bracketed list of tags drawn from a small path/extension keyword table. A
"Tag Index" section at the top of each Markdown file lets an AI agent grep
one tag name and get the exact file list for that topic without reading the
rest of the (much larger) document — this is the low-token access path.
tools/index_tags.json holds the same file -> {description, tags, archived}
data as machine-readable JSON for programmatic (non-grep) lookup.

A file is ARCHIVED if any path component is literally "archive" or
"archives" (matches the repository's existing convention: archives/,
airframe/archive/, avionics/kicad/<board>/archive/,
avionics/firmware/dts/cape-*/archive/). Everything else tracked is ACTIVE,
including deferred/ (Phase 11+ future work — deferred, not superseded).

Only git-TRACKED files are indexed (see git_tracked_paths()). The index is
therefore a deterministic function of the COMMIT, not of the working
directory: a fresh CI clone, a developer's clone full of untracked KiCad
backups and sliced gcode, and a linked git worktree all produce byte-identical
output. Regenerating anywhere is safe, which is what lets the CI job below
auto-correct a stale index instead of failing the build. If git cannot answer
(a source tarball with no .git), the generator falls back to the plain
filesystem walk and may then include untracked files.

Usage:
    python3 tools/precommit_index.py            # regenerate and write
    python3 tools/precommit_index.py --check    # exit 1 if files would change
"""

import argparse
import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PROJECT_INDEX = ROOT / "PROJECT_INDEX.md"
ARCHIVE_INDEX = ROOT / "ARCHIVE_INDEX.md"
TAG_JSON = ROOT / "tools" / "index_tags.json"

# Directories walked for index content. Root-level loose files are handled
# separately below.
TRACKED_DIRS = [
    ".github", ".githooks", "airframe", "archives", "avionics",
    "current-specification", "deferred", "docs", "gcs",
    "graphical-build-guide", "tools", "LICENSES", ".vscode",
]

# Vendor/build noise never indexed (parity with the previous generator,
# plus node_modules — vendored third-party JS, not project content).
IGNORE_DIR_NAMES = {".git", "__pycache__", "venv", "env",
                    ".ipynb_checkpoints", "node_modules"}
IGNORE_FILE_SUFFIXES = (".FCBak", ".rpt", ".pyc")
GENERATED_RELPATHS = {"PROJECT_INDEX.md", "ARCHIVE_INDEX.md", "tools/index_tags.json"}

ARCHIVE_DIR_NAMES = {"archive", "archives"}

# --- Domain tag per top-level directory --------------------------------
DIR_TAGS = {
    "airframe": "structural",
    "avionics": "avionics-hardware",
    "current-specification": "specification",
    "deferred": "deferred-future",
    "docs": "documentation",
    "gcs": "ground-control",
    "graphical-build-guide": "build-guide",
    "tools": "build-tooling",
    "archives": "archive",
    ".github": "repo-infra",
    ".githooks": "repo-infra",
    ".vscode": "repo-infra",
    "LICENSES": "licensing",
}

# --- Cross-functional capability tags: keyword -> tag -------------------
# Matched case-insensitively as a substring against the full relative path.
# A file may collect several of these on top of its one domain tag.
KEYWORD_TAGS = [
    ("security", "security"), ("crypto", "security"), ("tpm", "security"),
    ("auth", "security"), ("sign", "security"), ("zero_trust", "security"),
    ("emi", "emi-hardening"),
    ("failover", "redundancy-failover"), ("redundan", "redundancy-failover"),
    ("watchdog", "redundancy-failover"), ("pace", "redundancy-failover"),
    ("mavlink", "comms-protocol"), ("sik", "comms-protocol"),
    ("lora", "comms-protocol"), ("zigbee", "comms-protocol"),
    ("wifi", "comms-protocol"), ("rs485", "comms-protocol"),
    ("rs-485", "comms-protocol"), ("canfd", "comms-protocol"),
    ("can_fd", "comms-protocol"), ("can-fd", "comms-protocol"),
    ("1553", "comms-protocol"), ("ax25", "comms-protocol"),
    ("ax.25", "comms-protocol"), ("49mhz", "comms-protocol"),
    ("emma", "comms-protocol"), ("xcvr", "comms-protocol"),
    ("power", "power"), ("battery", "power"), ("kaylee", "power"),
    ("esc", "power"),
    ("edf", "propulsion"), ("nacelle", "propulsion"), ("thrust", "propulsion"),
    ("nozzle", "propulsion"), ("propulsion", "propulsion"),
    ("sensor", "sensors-vision"), ("tof", "sensors-vision"),
    ("lidar", "sensors-vision"), ("camera", "sensors-vision"),
    ("vision", "sensors-vision"), ("jayne", "sensors-vision"),
    ("laser", "sensors-vision"),
    ("landing_gear", "landing-gear"), ("landing-gear", "landing-gear"),
    ("kicad", "pcb-design"), ("gerber", "pcb-design"), ("schematic", "pcb-design"),
    ("scad", "cad-mesh"), ("fcstd", "cad-mesh"), ("freecad", "cad-mesh"),
    ("blender", "cad-mesh"), (".stl", "cad-mesh"),
    ("license", "licensing"), ("attribution", "licensing"), ("copyright", "licensing"),
    ("gcs", "ground-control"), ("malcolm", "ground-control"),
    ("dts", "firmware"), ("firmware", "firmware"),
    ("fabricat", "fabrication"), ("petg", "fabrication"), ("infill", "fabrication"),
    ("wash", "flight-control"), ("zoe", "flight-control"), ("zoë", "flight-control"),
    ("bom", "bom"), ("reference", "specification"),
    ("wbs", "project-tracking"), ("todo", "project-tracking"),
]


def _keyword_pattern(keyword):
    """Word-boundary regex for a path keyword.

    Plain substring matching false-positives constantly on engineering
    prose paths — "sign" inside "design", "auth" inside "author" — so
    require non-alphanumeric (or string edge) on both sides, with an
    optional trailing "s" for simple plurals (gerbers, references,
    sensors). A keyword containing a literal "." (extensions, "ax.25")
    already has a natural boundary there and is matched as-is.
    """
    return re.compile(r"(?<![a-z0-9])" + re.escape(keyword) + r"s?(?![a-z0-9])")


COMPILED_KEYWORD_TAGS = [(_keyword_pattern(kw), tag) for kw, tag in KEYWORD_TAGS]

EXT_TAGS = {
    ".kicad_pcb": "pcb-design", ".kicad_sch": "pcb-design",
    ".kicad_mod": "pcb-design", ".kicad_pro": "pcb-design",
    ".kicad_prl": "pcb-design",
    ".gbr": "pcb-design", ".gtl": "pcb-design", ".gts": "pcb-design",
    ".gtp": "pcb-design", ".gto": "pcb-design", ".gbs": "pcb-design",
    ".gbp": "pcb-design", ".gm1": "pcb-design", ".drl": "pcb-design",
    ".gbrjob": "pcb-design",
    ".stl": "cad-mesh", ".scad": "cad-mesh", ".fcstd": "cad-mesh",
    ".blend": "cad-mesh",
    ".c": "firmware", ".h": "firmware", ".dts": "firmware",
    ".md": "documentation",
    ".csv": "bom",
}

GERBER_EXTS = {".gbr", ".gtl", ".gts", ".gtp", ".gto", ".gbs", ".gbp", ".gm1",
               ".gbl", ".gbo", ".gba", ".gta", ".g1", ".g2"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".ico"}


def read_text(path, limit_bytes=8192):
    """Best-effort text read; never raises on binary/garbled content."""
    try:
        with open(path, "rb") as fh:
            raw = fh.read(limit_bytes)
        return raw.decode("utf-8", errors="ignore")
    except OSError:
        return ""


def trim(text, limit=110):
    text = " ".join(text.split())
    if len(text) > limit:
        text = text[:limit - 1].rstrip() + "…"
    return text


def is_boilerplate(text):
    """True for divider bars ("---", "===...") and encoding-cookie comments —
    real content, but useless as a one-line description."""
    if not text or not any(ch.isalnum() for ch in text):
        return True
    return bool(re.match(r"coding[:=]\s*[-\w.]+", text, re.IGNORECASE))


def describe_markdown(path):
    lines = read_text(path).splitlines()
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#") and not is_boilerplate(stripped.lstrip("#").strip()):
            return trim(stripped.lstrip("#").strip())
    for line in lines:
        if line.strip() and not is_boilerplate(line.strip()):
            return trim(line.strip())
    return "Markdown document"


def describe_python(path):
    # Module docstrings in this repo run verbose (project convention); read
    # enough that ast.parse doesn't choke on a docstring truncated mid-string.
    source = read_text(path, limit_bytes=32768)
    try:
        tree = ast.parse(source)
        doc = ast.get_docstring(tree)
        if doc:
            for doc_line in doc.strip().splitlines():
                doc_line = doc_line.strip()
                if doc_line and not is_boilerplate(doc_line):
                    return trim(doc_line)
    except (SyntaxError, ValueError):
        pass
    for line in source.splitlines()[:60]:
        stripped = line.strip()
        if not stripped.startswith("#") or stripped.startswith("#!"):
            continue
        text = stripped.lstrip("#").strip()
        if text and not is_boilerplate(text):
            return trim(text)
    return "Python script"


def describe_line_comment(path, marker):
    for line in read_text(path).splitlines()[:60]:
        stripped = line.strip()
        if stripped.startswith(marker):
            text = stripped.lstrip(marker).strip().strip("*").strip()
            if text and not is_boilerplate(text):
                return trim(text)
    return None


def describe_stl(path):
    try:
        with open(path, "rb") as fh:
            head = fh.read(80)
    except OSError:
        return "STL mesh"
    if head.startswith(b"solid"):
        name = head.split(b"\n", 1)[0][len(b"solid"):].decode("utf-8", "ignore").strip()
        return trim(f"STL mesh (ASCII){': ' + name if name else ''}")
    printable = head.decode("ascii", errors="ignore").strip("\x00 \t")
    printable = "".join(ch for ch in printable if ch.isprintable()).strip()
    if printable:
        return trim(f"STL mesh — header: {printable}")
    return "STL mesh (binary)"


def describe_bom_csv(path):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            rows = sum(1 for _ in fh)
    except OSError:
        return "Bill of materials (CSV)"
    items = max(rows - 1, 0)
    return f"Bill of materials, CSV ({items} items)"


def describe_json(path):
    # JSON must be read whole to parse at all — a byte-capped read just
    # trades "truncated garbage" for "guaranteed parse failure." BOM/config
    # JSON in this repo tops out around 100 KB; guard only against something
    # pathological.
    try:
        if path.stat().st_size > 5_000_000:
            return "JSON data file"
    except OSError:
        return "JSON data file"
    text = read_text(path, limit_bytes=5_000_000)
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return "JSON data file"
    if "bom" in path.name.lower():
        count = len(data) if isinstance(data, list) else len(data.get("items", []))
        return f"Bill of materials, JSON ({count} items)"
    if isinstance(data, list):
        return f"JSON data ({len(data)} entries)"
    if isinstance(data, dict):
        return f"JSON data ({len(data)} top-level keys)"
    return "JSON data file"


def describe_file(path):
    ext = path.suffix.lower()
    name_lower = path.name.lower()
    try:
        if ext == ".md":
            return describe_markdown(path)
        if ext == ".py":
            return describe_python(path)
        if ext == ".scad":
            return describe_line_comment(path, "//") or "OpenSCAD parametric source"
        if ext in (".c", ".h"):
            return describe_line_comment(path, "//") or describe_line_comment(path, "/*") \
                or ("C header" if ext == ".h" else "C source")
        if ext == ".stl":
            return describe_stl(path)
        if ext == ".kicad_pcb":
            return "KiCad PCB layout"
        if ext == ".kicad_sch":
            return "KiCad schematic"
        if ext == ".kicad_mod":
            return "KiCad footprint"
        if ext == ".kicad_pro":
            return "KiCad project file"
        if ext == ".kicad_prl":
            return "KiCad project-local settings"
        if ext in GERBER_EXTS:
            return f"Gerber fabrication layer ({name_lower.rsplit('-', 1)[-1][:-len(ext)]})"
        if ext == ".drl":
            return "Drill file (NC drill data)"
        if ext == ".gbrjob":
            return "Gerber job file (fabrication job spec)"
        if ext in IMAGE_EXTS:
            return "Rendered image / reference photo"
        if ext == ".svg":
            return "Vector diagram"
        if ext == ".pdf":
            return "PDF document"
        if ext == ".zip":
            return "Archived snapshot bundle"
        if ext == ".csv":
            return describe_bom_csv(path) if "bom" in name_lower else "Tabular data (CSV)"
        if ext == ".json":
            return describe_json(path)
        if ext == ".jsx":
            return "React/JSX specification component"
        if ext == ".fcstd":
            return "FreeCAD assembly/document"
        if ext == ".blend":
            return "Blender source scene"
        if ext == ".dts":
            return "Device-tree source (kernel board description)"
        if ext == ".kicad_sym":
            return "KiCad symbol library"
        if ext == ".kicad_dru":
            return "KiCad custom design-rules file"
        if ext == ".net":
            return "KiCad netlist"
        if ext == ".dsn":
            return "Specctra design file (autorouter input)"
        if ext == ".ses":
            return "Specctra session file (autorouter output)"
        if ext == ".brd":
            return "PCB board file (legacy Eagle/KiCad format)"
        if ext == ".step":
            return "3D STEP model"
        if ext == ".obj":
            return "3D OBJ mesh"
        if ext == ".dxf":
            return "2D DXF drawing"
        if ext in (".yml", ".yaml"):
            return "YAML config"
        if ext == ".js":
            return "JavaScript source"
        if ext == ".css":
            return "Stylesheet (CSS)"
        if ext == ".html":
            return "HTML document"
        if ext == ".txt":
            return describe_line_comment(path, "#") or "Text file"
        # No dedicated handler (LICENSE, Makefile, dotfile configs, …):
        # try a leading '#' comment, then just the first real line.
        comment = describe_line_comment(path, "#")
        if comment:
            return comment
        for line in read_text(path, limit_bytes=2048).splitlines():
            stripped = line.strip()
            if stripped and not is_boilerplate(stripped):
                return trim(stripped)
    except Exception:
        pass
    return f"{ext.lstrip('.').upper()} file" if ext else "File"


# These non-negotiable, cross-cutting project requirements (AGENTS.md §1)
# are discussed in prose far more than they're spelled out in filenames, so
# path-only matching leaves them nearly empty. For these three tags only,
# also scan a leading slice of file content — not the full keyword table,
# which would over-tag every broad WBS/TODO doc with dozens of unrelated
# topics and defeat the point of a precise, low-token tag lookup.
CONTENT_SCAN_TAGS = {"security", "emi-hardening", "redundancy-failover"}
CONTENT_SCAN_PATTERNS = [(p, t) for p, t in COMPILED_KEYWORD_TAGS if t in CONTENT_SCAN_TAGS]
CONTENT_SCAN_EXTS = {".md", ".py", ".txt", ".c", ".h", ".scad", ".dts", ".jsx"}


def classify_tags(relpath, full_path=None):
    parts_lower = Path(relpath).parts
    top = parts_lower[0]
    tags = set()
    if top in DIR_TAGS:
        tags.add(DIR_TAGS[top])
    ext = Path(relpath).suffix.lower()
    if full_path is not None and ext in CONTENT_SCAN_EXTS:
        content_lower = read_text(full_path, limit_bytes=16384).lower()
        for pattern, tag in CONTENT_SCAN_PATTERNS:
            if pattern.search(content_lower):
                tags.add(tag)
    if ext in EXT_TAGS:
        tags.add(EXT_TAGS[ext])
    path_lower = relpath.lower()
    for pattern, tag in COMPILED_KEYWORD_TAGS:
        if pattern.search(path_lower):
            tags.add(tag)
    return tags


def is_archived(relpath):
    return any(part.lower() in ARCHIVE_DIR_NAMES for part in Path(relpath).parts)


def git_tracked_paths():
    """
    Repo-relative paths of every git-TRACKED file, or None if git is unavailable.

    This is what makes the index a deterministic function of the COMMIT rather
    than of whatever happens to be sitting in the working directory.  Two real
    failure modes it removes (both cost real CI time in 2026-08):

      1. Untracked local artefacts leaking into the index.  The walk below does
         not consult .gitignore, so regenerating in a working clone silently
         indexed 154 untracked files — KiCad autosave/backup archives
         (*-backups/*.zip), editor lock files (~*.lck), fp-info-cache, sliced
         gcode, and FreeCAD *.FCStd working files.  CI checks out a fresh clone
         that contains none of them, so its regenerated index never matched the
         committed one and "Project/Archive Index sync" failed on a developer
         machine's leftovers.
      2. A git worktree's .git ENTRY being indexed.  In a linked worktree .git
         is a FILE, not a directory, so the root-level loose-file scan below
         picked it up (IGNORE_DIR_NAMES only filters directories).  That is the
         artefact removed in 48eae05; it came back via this hook whenever anyone
         committed from a worktree.  `git ls-files` never lists .git in any
         checkout topology, so the whole class is gone.

    Returns None (not an empty set) when git cannot answer — a source tarball,
    an export with no .git, or git missing from PATH — so the caller can fall
    back to the filesystem walk instead of silently emptying the index.
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "-z"],
            capture_output=True, check=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    paths = {p for p in result.stdout.decode("utf-8").split("\0") if p}
    return paths or None


def collect_files():
    """Walk the tracked tree plus root-level loose files; return sorted relpaths.

    The walk defines WHICH paths are eligible (the TRACKED_DIRS whitelist, the
    ignore rules, root-level loose files).  When git is available its tracked
    set then filters the result, so untracked working-directory noise and the
    worktree .git entry can never reach the index — see git_tracked_paths().
    """
    tracked_paths = git_tracked_paths()
    found = []

    for name in sorted(os.listdir(ROOT)):
        full = ROOT / name
        if full.is_file() and name not in GENERATED_RELPATHS:
            found.append(name)

    for tracked in TRACKED_DIRS:
        base = ROOT / tracked
        if not base.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIR_NAMES]
            for fname in filenames:
                if fname.endswith(IGNORE_FILE_SUFFIXES):
                    continue
                full = Path(dirpath) / fname
                relpath = str(full.relative_to(ROOT))
                if relpath in GENERATED_RELPATHS:
                    continue
                found.append(relpath)

    if tracked_paths is not None:
        found = [p for p in found if p in tracked_paths]

    return sorted(set(found))


def build_index():
    """Return (entries, tag_index) where entries is a list of dicts."""
    entries = []
    for relpath in collect_files():
        full = ROOT / relpath
        archived = is_archived(relpath)
        tags = classify_tags(relpath, full)
        if archived:
            tags.add("archive")
        description = describe_file(full)
        entries.append({
            "path": relpath,
            "description": description,
            "tags": sorted(tags),
            "archived": archived,
        })
    return entries


def group_by_dir(entries):
    groups = {}
    for entry in entries:
        parent = str(Path(entry["path"]).parent)
        groups.setdefault(parent, []).append(entry)
    for items in groups.values():
        items.sort(key=lambda e: Path(e["path"]).name.lower())
    return groups


def render_tag_section(entries, heading):
    by_tag = {}
    for entry in entries:
        for tag in entry["tags"]:
            by_tag.setdefault(tag, []).append(entry["path"])
    lines = [f"## {heading}", "",
             "Grep a tag name below to get every matching file in one line, "
             "without reading the rest of this document.", ""]
    for tag in sorted(by_tag):
        paths = sorted(by_tag[tag])
        lines.append(f"- `{tag}` ({len(paths)}): " + ", ".join(paths))
    lines.append("")
    return lines


def render_directory_sections(entries):
    groups = group_by_dir(entries)
    lines = []
    for parent in sorted(groups, key=lambda p: (p == ".", p.lower())):
        heading = "Repository Root" if parent == "." else f"{parent}/"
        lines.append(f"## {heading}")
        lines.append("")
        lines.append("```text")
        for entry in groups[parent]:
            name = Path(entry["path"]).name
            tagstr = f" [{', '.join(entry['tags'])}]" if entry["tags"] else ""
            lines.append(f"{name} — {entry['description']}{tagstr}")
        lines.append("```")
        lines.append("")
    return lines


def render_index(entries, title, note, tag_heading, generated_date):
    lines = [
        f"# {title}",
        "",
        "<!-- AUTO-GENERATED by tools/precommit_index.py — DO NOT HAND-EDIT.",
        "     Regenerated in full from the current file tree on every commit;",
        "     hand edits are overwritten on the next run. To change how entries",
        "     look, change the generator (tools/precommit_index.py), not this",
        "     file. Machine-readable form: tools/index_tags.json -->",
        f"<!-- {note} -->",
        f"<!-- Last generated: {generated_date} -->",
        "",
    ]
    lines.extend(render_tag_section(entries, tag_heading))
    lines.append("---")
    lines.append("")
    lines.extend(render_directory_sections(entries))
    return "\n".join(lines).rstrip() + "\n"


def render_json(entries, generated_date):
    files = {
        e["path"]: {
            "description": e["description"],
            "tags": e["tags"],
            "archived": e["archived"],
        }
        for e in entries
    }
    by_tag = {}
    for e in entries:
        for tag in e["tags"]:
            by_tag.setdefault(tag, []).append(e["path"])
    for tag in by_tag:
        by_tag[tag].sort()
    payload = {
        "generated": generated_date,
        "files": files,
        "tags": by_tag,
    }
    return json.dumps(payload, indent=2, sort_keys=False) + "\n"


def sync_and_format(check=False):
    from datetime import datetime
    generated_date = datetime.now().date().isoformat()

    entries = build_index()
    active = [e for e in entries if not e["archived"]]
    archived = [e for e in entries if e["archived"]]

    project_text = render_index(
        active, "PROJECT_INDEX.md — Serenity UAV",
        "Archive contents described in ARCHIVE_INDEX.md.",
        "Tag Index", generated_date,
    )
    archive_text = render_index(
        archived, "ARCHIVE_INDEX.md — Serenity UAV",
        "Active file tree described in PROJECT_INDEX.md.",
        "Tag Index", generated_date,
    )
    json_text = render_json(entries, generated_date)

    outputs = {
        PROJECT_INDEX: project_text,
        ARCHIVE_INDEX: archive_text,
        TAG_JSON: json_text,
    }

    changed = []
    for path, text in outputs.items():
        current = path.read_text() if path.exists() else None
        if current != text:
            changed.append(path)

    if check:
        if changed:
            print("Index out of sync, run tools/precommit_index.py: "
                  + ", ".join(str(p.relative_to(ROOT)) for p in changed))
            return 1
        print("Indexes up to date.")
        return 0

    for path, text in outputs.items():
        path.write_text(text)
    print(f"Indexed {len(active)} active files, {len(archived)} archived files "
          f"({len(changed)} file(s) updated).")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--check", action="store_true",
        help="exit 1 if the indexes would change instead of writing them")
    args = parser.parse_args()
    sys.exit(sync_and_format(check=args.check))
