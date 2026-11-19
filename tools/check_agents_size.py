#!/usr/bin/env python3
# License: MIT — see LICENSES/MIT.txt (SPDX-License-Identifier: MIT)
"""Fail when an AGENTS.md file exceeds its size cap.

Owner decision 2026-11-17 (AGENTS.md review, Q2/Q15): AGENTS.md files carry
standing rules and routing pointers only, and a hard cap keeps them from
regrowing.  Root AGENTS.md: at most 300 lines and 20 KB.  Every other
AGENTS.md: at most 100 lines and 7 KB.  The byte ceiling stops a file from
dodging the line cap with very long lines.

Raising a cap is an owner decision: edit LIMITS below, which shows in review.

Usage:
    python3 tools/check_agents_size.py          # check every tracked AGENTS.md
    python3 tools/check_agents_size.py --help

Exit code 0 when every file is within its cap, 1 otherwise.  Runs from
.githooks/pre-commit and CI.
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (max lines, max bytes) by role.
LIMITS = {
    "root": (300, 20 * 1024),
    "subsystem": (100, 7 * 1024),
}


def agents_files(root):
    """Return every git-tracked AGENTS.md under root (falls back to a walk)."""
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "ls-files", "AGENTS.md", "**/AGENTS.md"],
            check=True, capture_output=True, text=True).stdout
        paths = [root / p for p in out.split()]
    except (OSError, subprocess.CalledProcessError):
        paths = [p for p in root.rglob("AGENTS.md") if ".git" not in p.parts]
    return sorted(p for p in paths if p.is_file())


def check(path, root):
    """Return a list of violation strings for one file."""
    role = "root" if path.parent == root else "subsystem"
    max_lines, max_bytes = LIMITS[role]
    data = path.read_bytes()
    lines = data.count(b"\n") + (0 if data.endswith(b"\n") or not data else 1)
    rel = path.relative_to(root)
    errors = []
    if lines > max_lines:
        errors.append(f"{rel}: {lines} lines > {max_lines} ({role} cap)")
    if len(data) > max_bytes:
        errors.append(f"{rel}: {len(data)} bytes > {max_bytes} ({role} cap)")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check AGENTS.md files against their size caps.",
        epilog="Example: python3 tools/check_agents_size.py")
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="repository root (default: this checkout)")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    errors = []
    for path in agents_files(root):
        errors.extend(check(path, root))
    for err in errors:
        print(f"FAIL  {err}")
    if errors:
        print("Trim the file, or move narrative to its owning document "
              "(root AGENTS.md §10). Raising a cap is an owner decision.")
        return 1
    print("ok    every AGENTS.md is within its size cap")
    return 0


if __name__ == "__main__":
    sys.exit(main())
