"""Unit tests for tools/wbs_burndown.py (synthetic WBS trees; no dependence on the live record).

Author: Claude Opus 5.5 (Anthropic) for S. Griffing, 2026-11-07.
License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import wbs_burndown as wb  # noqa: E402

WBS_A = """# A
## 1 Section
- [ ] open top
    - [ ] nested under open (not counted)
- [x] closed top
    - [ ] open under closed (counted open)
    - [x] closed under closed (counted closed)
"""


def _tree(tmp_path, a_text, root_text="# Root\n## 0 Index\n- [ ] project item\n"):
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "WBS.md").write_text(a_text, encoding="utf-8")
    (tmp_path / "WBS.md").write_text(root_text, encoding="utf-8")
    return ("WBS.md", "a/WBS.md", "gone/WBS.md")


def test_counts_follow_the_open_nesting_rule(tmp_path):
    pairs = _tree(tmp_path, WBS_A)
    snap = wb.snapshot(tmp_path, pairs)
    assert snap["files"]["a/WBS.md"] == {"open": 2, "closed": 2}
    assert snap["files"]["gone/WBS.md"] == {"open": 0, "closed": 0}   # missing file: no crash
    assert snap["root"] == {"open": 1, "closed": 0}                   # root kept out of total
    assert (snap["total_open"], snap["total_closed"]) == (2, 2)


def test_closures_count_and_new_findings_do_not_cancel_them(tmp_path):
    pairs = _tree(tmp_path, WBS_A)
    base = wb.snapshot(tmp_path, pairs)
    # close "open top", record two new findings
    later = WBS_A.replace("- [ ] open top", "- [x] open top") + "- [ ] finding 1\n- [ ] finding 2\n"
    (tmp_path / "a" / "WBS.md").write_text(later, encoding="utf-8")
    now = wb.snapshot(tmp_path, pairs)
    lines = wb.report(now, base)
    total = next(ln for ln in lines if ln.startswith("TOTAL"))
    d_open, closed_plus = total.split()[-2:]
    assert closed_plus == "+1"
    # open: -1 closed, +1 nested child now under a closed box (federation rule), +2 findings
    assert d_open == "+2"          # net open rose, yet the closure still shows


def test_removed_file_still_reported(tmp_path):
    pairs = _tree(tmp_path, WBS_A)
    base = wb.snapshot(tmp_path, pairs)
    now = wb.snapshot(tmp_path, ("WBS.md",))
    lines = wb.report(now, base)
    row = next(ln for ln in lines if ln.startswith("a/WBS.md"))
    assert row.split()[-2:] == ["-2", "-2"]


def test_bad_baseline_is_rejected(tmp_path):
    bad = tmp_path / "x.json"
    bad.write_text(json.dumps({"date": "2026-11-07"}), encoding="utf-8")
    with pytest.raises(ValueError):
        wb.load_baseline(bad)
    assert wb.main(["--baseline", str(bad)]) == 2
