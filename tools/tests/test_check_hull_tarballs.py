"""Tests for tools/check_hull_tarballs.py.

Author: Claude Sonnet 5.5 (Anthropic) for S. Griffing, 2026-11-02.
License: MIT (SPDX-License-Identifier: MIT)
"""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_hull_tarballs as ch  # noqa: E402

STEM = ch.HULL_PIECES[0]


def sh(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


class HullTarballTest(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp())
        sh(self.root, "init", "-q")
        sh(self.root, "config", "user.email", "t@example.com")
        sh(self.root, "config", "user.name", "t")
        (self.root / ch.HULL_DIR).mkdir(parents=True)
        self.raw = self.root / ch.HULL_DIR / f"{STEM}.stl"
        self.tar = self.root / ch.HULL_DIR / f"{STEM}.stl.tar.gz"
        self.raw.write_bytes(b"solid hull\n" * 1000)
        ch.repackage(self.raw, self.tar)
        (self.root / ".gitignore").write_text(f"{ch.HULL_DIR}/{STEM}.stl\n")
        sh(self.root, "add", ".gitignore", str(self.tar.relative_to(self.root)))

    def tearDown(self) -> None:
        shutil.rmtree(self.root)

    def test_clean_tree_passes(self) -> None:
        # Happy path: tarball staged, raw ignored and identical.
        errs, notes = ch.check_piece(self.root, STEM, fix=False)
        self.assertEqual((errs, notes), ([], []))

    def test_changed_raw_is_repackaged_and_staged(self) -> None:
        # Hook mode: a regenerated hull is repackaged, staged, then verifies clean.
        self.raw.write_bytes(b"solid hull v2\n" * 2000)
        errs, notes = ch.check_piece(self.root, STEM, fix=True)
        self.assertEqual(errs, [])
        self.assertTrue(any("repackaged" in n for n in notes))
        self.assertEqual(ch.tar_member_sha256(self.tar, self.raw.name), ch.sha256_file(self.raw))
        self.assertEqual(ch.check_piece(self.root, STEM, fix=False), ([], []))

    def test_changed_raw_fails_in_check_mode(self) -> None:
        # CI mode never writes: a stale tarball is an error.
        self.raw.write_bytes(b"different\n")
        errs, _ = ch.check_piece(self.root, STEM, fix=False)
        self.assertTrue(any("stale" in e for e in errs))

    def test_tracked_raw_stl_fails(self) -> None:
        # Error path: the inflated STL must never be tracked.
        sh(self.root, "add", "-f", str(self.raw.relative_to(self.root)))
        errs, _ = ch.check_piece(self.root, STEM, fix=False)
        self.assertTrue(any("is tracked" in e for e in errs))

    def test_unignored_raw_stl_fails(self) -> None:
        # Error path: dropping the .gitignore line is caught.
        (self.root / ".gitignore").write_text("")
        errs, _ = ch.check_piece(self.root, STEM, fix=False)
        self.assertTrue(any("not gitignored" in e for e in errs))

    def test_missing_or_wrong_tarball_fails(self) -> None:
        # Edge: no raw file locally, tarball missing, or holding the wrong member.
        self.raw.unlink()
        self.tar.unlink()
        self.assertTrue(any("missing" in e for e in ch.check_piece(self.root, STEM, False)[0]))
        other = self.root / "other.bin"
        other.write_bytes(b"x")
        ch.repackage(other, self.tar)
        sh(self.root, "add", str(self.tar.relative_to(self.root)))
        errs, _ = ch.check_piece(self.root, STEM, fix=False)
        self.assertTrue(any("exactly one member" in e for e in errs))

    def test_oversize_staged_blob_fails(self) -> None:
        # Integration: any staged blob over the limit is refused.
        old = ch.BLOB_LIMIT
        ch.BLOB_LIMIT = 100
        try:
            errs = ch.staged_blob_errors(self.root)
        finally:
            ch.BLOB_LIMIT = old
        self.assertTrue(errs)

    def test_committed_tree_passes(self) -> None:
        # The real repository state passes in verify-only mode.
        for stem in ch.HULL_PIECES:
            self.assertEqual(ch.check_piece(ch.ROOT, stem, fix=False)[0], [])


if __name__ == "__main__":
    unittest.main()
