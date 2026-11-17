# License: MIT — see LICENSES/MIT.txt (SPDX-License-Identifier: MIT)
"""Tests for tools/check_agents_size.py."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "check_agents_size", Path(__file__).resolve().parents[1] / "check_agents_size.py")
assert _spec is not None and _spec.loader is not None
cas = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cas)


def _write(path, n_lines, width=10):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(("x" * width + "\n") * n_lines)


def test_root_within_cap_passes(tmp_path):
    _write(tmp_path / "AGENTS.md", 300)
    assert cas.check(tmp_path / "AGENTS.md", tmp_path) == []


def test_root_over_line_cap_fails(tmp_path):
    _write(tmp_path / "AGENTS.md", 301)
    assert "301 lines > 300" in cas.check(tmp_path / "AGENTS.md", tmp_path)[0]


def test_subsystem_uses_tighter_cap(tmp_path):
    _write(tmp_path / "avionics" / "AGENTS.md", 101)
    errs = cas.check(tmp_path / "avionics" / "AGENTS.md", tmp_path)
    assert errs and "subsystem cap" in errs[0]


def test_byte_cap_catches_long_lines(tmp_path):
    _write(tmp_path / "gcs" / "AGENTS.md", 50, width=200)
    errs = cas.check(tmp_path / "gcs" / "AGENTS.md", tmp_path)
    assert any("bytes >" in e for e in errs)


def test_main_reports_failure(tmp_path):
    _write(tmp_path / "AGENTS.md", 10)
    _write(tmp_path / "tools" / "AGENTS.md", 150)
    assert cas.main(["--root", str(tmp_path)]) == 1
