#!/usr/bin/env python3
"""Commit/CI gate: hull STLs ship as gzip tarballs and the inflated STLs stay ignored.

The two merged fuselage shells are too large for a plain Git blob (GitHub rejects files over
100 MiB; the aft hull was 104 MB, the fused forward hull 115 MB), so the repo carries each as
``<name>.stl.tar.gz`` and gitignores the inflated ``<name>.stl`` (owner 2026-11-02).

Checks, for every hull piece in ``HULL_PIECES``:

  1. the tarball exists and is tracked (or staged), and holds exactly one member named
     ``<name>.stl``;
  2. the inflated STL is gitignored and NOT tracked or staged;
  3. if an inflated STL exists locally and differs from the tarball's member, the tarball is stale.
     By default the tool repackages it and stages the tarball (so a regenerated hull cannot be
     committed with an out-of-date archive); ``--check`` (CI) only reports.

Also refuses any staged blob of 95 MiB or more anywhere (GitHub's hard limit is 100 MiB).

Usage::

    /usr/bin/python3 tools/check_hull_tarballs.py          # hook: repackage stale tarballs, stage
    /usr/bin/python3 tools/check_hull_tarballs.py --check  # CI: verify only, never writes

Adding a new hull piece: append its stem to ``HULL_PIECES`` and gitignore its raw ``.stl``.

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (requirement and direction).
Written by Claude Sonnet 5.5 (Anthropic) under the author's direction, 2026-11-02,
per AGENTS.md section 3 AI attribution.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HULL_DIR = Path("airframe/stls/fuselage")
HULL_PIECES = ["head_cargo_shell24_2mm_merged", "middle_rear_shell24_2mm_merged"]
BLOB_LIMIT = 95 * 1024 * 1024  # GitHub rejects 100 MiB; fail before that


def git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tar_member_sha256(tar_path: Path, member: str) -> str | None:
    """sha256 of ``member`` inside the tarball, or None if the archive is not exactly [member]."""
    with tarfile.open(tar_path, "r:gz") as tz:
        names = tz.getnames()
        if names != [member]:
            return None
        h = hashlib.sha256()
        fobj = tz.extractfile(member)
        if fobj is None:
            return None
        while chunk := fobj.read(1 << 20):
            h.update(chunk)
        return h.hexdigest()


def repackage(raw: Path, tar_path: Path) -> None:
    with tarfile.open(tar_path, "w:gz") as tz:
        tz.add(raw, arcname=raw.name)


def check_piece(root: Path, stem: str, fix: bool) -> tuple[list[str], list[str]]:
    """Return (errors, notes) for one hull piece."""
    errs: list[str] = []
    notes: list[str] = []
    raw_rel = HULL_DIR / f"{stem}.stl"
    tar_rel = HULL_DIR / f"{stem}.stl.tar.gz"
    raw, tar_path = root / raw_rel, root / tar_rel

    if git(root, "ls-files", "--error-unmatch", str(raw_rel)).returncode == 0:
        errs.append(f"{raw_rel} is tracked; run: git rm --cached {raw_rel}")
    if git(root, "check-ignore", "-q", str(raw_rel)).returncode != 0:
        errs.append(f"{raw_rel} is not gitignored; add it to .gitignore")

    if raw.exists():
        if not tar_path.exists() or tar_member_sha256(tar_path, raw.name) != sha256_file(raw):
            if fix:
                repackage(raw, tar_path)
                git(root, "add", str(tar_rel))
                notes.append(f"repackaged {tar_rel} from the regenerated {raw_rel} and staged it")
            else:
                errs.append(
                    f"{tar_rel} is stale or missing versus {raw_rel}; run this tool locally"
                )
    if not tar_path.exists():
        errs.append(f"{tar_rel} is missing")
        return errs, notes
    if tar_member_sha256(tar_path, raw.name) is None:
        errs.append(f"{tar_rel} must contain exactly one member, {raw.name}")
    if git(root, "ls-files", "--error-unmatch", str(tar_rel)).returncode != 0:
        errs.append(f"{tar_rel} is not tracked or staged; run: git add {tar_rel}")
    return errs, notes


def staged_blob_errors(root: Path) -> list[str]:
    errs = []
    out = git(root, "ls-files", "--stage", "-z").stdout
    for ent in [x for x in out.split("\0") if x]:
        meta, _, path = ent.partition("\t")
        sha = meta.split()[1]
        size = int(git(root, "cat-file", "-s", sha).stdout.strip() or 0)
        if size >= BLOB_LIMIT:
            errs.append(f"{path} is {size / 1048576:.1f} MiB (limit 95 MiB): ship it as a tarball")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="verify only; never write (CI)")
    args = ap.parse_args()
    errs: list[str] = []
    for stem in HULL_PIECES:
        piece_errs, notes = check_piece(ROOT, stem, fix=not args.check)
        errs += piece_errs
        for n in notes:
            print(f"check_hull_tarballs: {n}")
    errs += staged_blob_errors(ROOT)
    for msg in errs:
        print(f"check_hull_tarballs: ERROR: {msg}", file=sys.stderr)
    if not errs:
        print("check_hull_tarballs: hull tarballs current, inflated STLs ignored")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
