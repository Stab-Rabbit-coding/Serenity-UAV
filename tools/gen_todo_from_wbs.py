#!/usr/bin/env python3
"""Regenerate a ``TODO.md`` (open work only) from its owning ``WBS.md``.

Implements the root ``AGENTS.md`` §10 "WBS.md / TODO.md Federation" rule that
``TODO.md`` is *generated from* ``WBS.md`` — one line per currently-open
top-level item, <=70 characters, no prose, each section pointing back at its
``WBS.md`` entry — and is never edited as the source of truth.

Rules applied (mirroring ``AGENTS.md`` §10 and ``docs/WBS_FEDERATION.md``):

* A heading is emitted only if at least one open item survives under it.
* An open item is a ``- [ ]`` line whose nearest enclosing checkbox (a less-
  indented checkbox earlier in the same heading section) is either absent or
  already closed ``[x]``.  Open sub-items under an *open* parent fold into
  the parent; open sub-items under a *closed* parent are promoted, because the
  parent no longer represents them in the open list.
* Item text is de-emphasised (``**`` stripped), whitespace-collapsed, and cut
  at a word boundary to at most 70 characters with a trailing ellipsis.
* The existing ``TODO.md`` preamble (everything through the first ``---``
  rule) and its footer (everything after the last ``---`` rule) are kept
  verbatim, so per-file headers, licence stamps and Firefly quotes survive
  regeneration.  A ``**Last updated:**`` stamp in the preamble is refreshed.
* Root ``WBS.md`` headings carry their own ``→ detail:`` pointer line; it is
  copied through.  Subsystem ``WBS.md`` files do not, so a
  ``→ full detail: `WBS.md` §N`` line is synthesised from the heading.

Usage::

    /usr/bin/python3 tools/gen_todo_from_wbs.py                # regenerate all
    /usr/bin/python3 tools/gen_todo_from_wbs.py --check        # diff only, exit 1 on drift
    /usr/bin/python3 tools/gen_todo_from_wbs.py docs/WBS.md    # one pair

Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP.
Written by Claude Opus 5 (Anthropic) under the author's direction, 2026-09-15,
per ``AGENTS.md`` §3 AI attribution.
License: CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0
"""

from __future__ import annotations

import argparse
import datetime as _dt
import difflib
import re
import sys
from pathlib import Path

# Repository root is one level above this file's directory.
REPO_ROOT = Path(__file__).resolve().parent.parent

# Every {WBS,TODO}.md pair in the federation (docs/WBS_FEDERATION.md).  The
# root pair is listed first; ``tools/`` and ``current-specification/`` own no
# WBS branch and are deliberately absent.
PAIRS: tuple[str, ...] = (
    "WBS.md",
    "docs/WBS.md",
    "airframe/WBS.md",
    "airframe/fuselage-joints/WBS.md",
    "airframe/fuselage-covers/WBS.md",
    "airframe/fuselage-mid/WBS.md",
    "airframe/wings-nacelles/WBS.md",
    "airframe/landing-gear/WBS.md",
    "avionics/WBS.md",
    "avionics/rev-s1/WBS.md",
    "avionics/emi-hardening/WBS.md",
    "avionics/observer/WBS.md",
    "avionics/firmware/WBS.md",
    "graphical-build-guide/WBS.md",
    "graphical-build-guide/flight-phases/WBS.md",
    "gcs/WBS.md",
    "deferred/WBS.md",
)

MAX_LEN = 70  # AGENTS.md §10: item text <=70 chars (the `- [ ] ` prefix is not counted)

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
_CHECKBOX_RE = re.compile(r"^(\s*)- \[( |x|X)\]\s*(.*)$")
_DETAIL_RE = re.compile(r"^\s*→\s*(?:full\s+)?detail:", re.IGNORECASE)
_SECTION_RE = re.compile(r"(§\s*[\w.]+|Phase\s*\d+\w*|\b\d+(?:\.\d+)+[a-z]?\b)")
_LAST_UPDATED_RE = re.compile(r"^(\*\*Last updated:\*\*\s*)\S+(.*)$")


def _clean(text: str) -> str:
    """Strip markdown emphasis, a bare ``[OPEN]`` tag, and collapse whitespace."""
    text = text.replace("**", "")
    text = re.sub(r"^\[OPEN\]\s*", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


_SENTENCE_BREAK_RE = re.compile(r"(?<=[.!?])\s")
_CLAUSE_BREAK_RE = re.compile(r"\s—\s|\s--\s|:\s|;\s")


def _first_clause(text: str, limit: int = MAX_LEN) -> str:
    """Shorten ``text`` to its headline clause when the whole item is too long.

    Items in ``WBS.md`` are paragraphs; the first sentence is normally the
    headline and the rest is rationale that does not belong in ``TODO.md``.
    Text that already fits is returned untouched.  Otherwise the first
    sentence break that fits wins; failing that, the *longest* dash/colon/
    semicolon clause that fits (so ``WA-R7..R12 — nacelle side: bore D20 …``
    keeps as much of its payload as the cap allows).  Breaks are honoured only
    when they leave at least 20 characters, so a leading tag such as
    ``[OPEN — VERIFY]`` is never mistaken for the whole item.
    """
    if len(text) <= limit:
        return text
    for match in _SENTENCE_BREAK_RE.finditer(text):
        end = match.start()
        if end > limit:
            break
        if end >= 20:
            return text[:end].rstrip(" .:;")
    best = ""
    for match in _CLAUSE_BREAK_RE.finditer(text):
        end = match.start()
        if end > limit:
            break
        if end >= 20:
            best = text[:end]
    # A clause cut that throws away most of the budget ("ASTM coupon") reads
    # worse than a word-boundary truncation of the full text; require it to
    # keep at least 60 % of the cap before preferring it.
    if best and len(best) >= (limit * 3) // 5:
        return best.rstrip(" .:;")
    return text


def _truncate(text: str, limit: int = MAX_LEN) -> str:
    """Cut ``text`` to ``limit`` chars at a word boundary, adding an ellipsis."""
    if len(text) <= limit:
        return text
    cut = text[: limit - 1]
    # Prefer a word boundary if one lies in the last third of the budget.
    space = cut.rfind(" ")
    if space > (limit * 2) // 3:
        cut = cut[:space]
    return cut.rstrip(" ,;:—-") + "…"


def _section_pointer(heading: str) -> str:
    """Derive the ``§`` label used in a synthesised ``→ full detail`` line."""
    match = _SECTION_RE.search(heading)
    if not match:
        return heading.split("—")[0].strip()
    label = match.group(1).replace(" ", "")
    return label if label.startswith("§") or label.startswith("Phase") else f"§{label}"


def extract_open_items(wbs_text: str, root: bool) -> list[tuple[str, str, list[str]]]:
    """Return ``[(heading_line, detail_line, [items...]), ...]`` for open work.

    ``heading_line`` is the original markdown heading; ``detail_line`` is the
    ``→ detail:`` pointer (copied through for root, synthesised otherwise).
    """
    sections: list[tuple[str, str, list[str]]] = []
    heading = ""
    detail = ""
    items: list = []
    # Stack of (indent, is_open) for enclosing checkboxes in this section.
    stack: list[tuple[int, bool]] = []

    def flush() -> None:
        if heading and items:
            sections.append((heading, detail, list(items)))

    pending: list[str] | None = None  # continuation lines of the last checkbox

    def close_pending() -> None:
        nonlocal pending
        if pending is not None and pending and items and items[-1] is None:
            items[-1] = "- [ ] " + _truncate(_first_clause(_clean(" ".join(pending))))
        pending = None

    for raw in wbs_text.splitlines():
        head = _HEADING_RE.match(raw)
        if head:
            close_pending()
            flush()
            heading = raw.rstrip()
            detail = ""
            items = []
            stack = []
            if not root:
                detail = f"→ full detail: `WBS.md` {_section_pointer(head.group(2))}"
            continue
        if root and _DETAIL_RE.match(raw) and not detail:
            detail = raw.strip()
            continue
        box = _CHECKBOX_RE.match(raw)
        if not box:
            # Indented, non-blank, non-checkbox text continues the last item.
            if pending is not None and raw.strip() and raw[:1].isspace():
                pending.append(raw.strip())
            else:
                close_pending()
            continue
        close_pending()
        indent = len(box.group(1).expandtabs(4))
        is_open = box.group(2) == " "
        # Pop enclosing checkboxes that are not actually enclosing this one.
        while stack and stack[-1][0] >= indent:
            stack.pop()
        enclosed_by_open = any(open_ for _, open_ in stack)
        if is_open and not enclosed_by_open:
            items.append(None)  # placeholder until continuation lines are read
            pending = [box.group(3)]
        stack.append((indent, is_open))
    close_pending()
    flush()
    return sections


def _split_preamble_footer(todo_text: str) -> tuple[list[str], list[str]]:
    """Split an existing TODO into (preamble incl. first ``---``, footer)."""
    lines = todo_text.splitlines()
    rules = [i for i, line in enumerate(lines) if line.strip() == "---"]
    if not rules:
        return lines, []
    preamble = lines[: rules[0] + 1]
    footer = lines[rules[-1] :] if len(rules) > 1 else []  # noqa: E203
    return preamble, footer


def _stamp_date(preamble: list[str], today: str) -> list[str]:
    """Refresh a ``**Last updated:**`` line if the preamble carries one."""
    out = []
    for line in preamble:
        match = _LAST_UPDATED_RE.match(line)
        out.append(f"{match.group(1)}{today}{match.group(2)}" if match else line)
    return out


def render_todo(wbs_path: Path, todo_path: Path, today: str) -> str:
    """Produce the regenerated TODO.md text for one WBS/TODO pair."""
    root = wbs_path.resolve() == (REPO_ROOT / "WBS.md").resolve()
    wbs_text = wbs_path.read_text(encoding="utf-8")
    old = todo_path.read_text(encoding="utf-8") if todo_path.exists() else ""
    preamble, footer = _split_preamble_footer(old)
    if not preamble:
        preamble = [
            f"# {wbs_path.parent.name or 'Serenity UAV'} — TODO (Open Work Only)",
            "",
            "---",
        ]
    preamble = _stamp_date(preamble, today)

    body: list[str] = [""]
    for heading, detail, items in extract_open_items(wbs_text, root):
        # Skip the WBS file's own H1 title — the TODO has its own.
        if heading.startswith("# "):
            continue
        body.append(heading)
        if detail:
            body.append(detail)
        body.append("")
        body.extend(items)
        body.append("")

    out = preamble + body
    if footer:
        out.extend(footer)
    text = "\n".join(out).rstrip("\n") + "\n"
    # Collapse any triple blank lines left by section joins.
    return re.sub(r"\n{3,}", "\n\n", text)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("wbs", nargs="*", help="WBS.md paths (default: every pair)")
    parser.add_argument(
        "--check", action="store_true", help="report drift, write nothing"
    )
    args = parser.parse_args(argv)

    today = _dt.date.today().isoformat()
    targets = [Path(p) for p in args.wbs] or [REPO_ROOT / p for p in PAIRS]
    drift = 0
    for wbs_path in targets:
        if not wbs_path.exists():
            print(f"MISSING  {wbs_path}", file=sys.stderr)
            drift += 1
            continue
        todo_path = wbs_path.with_name("TODO.md")
        new = render_todo(wbs_path, todo_path, today)
        old = todo_path.read_text(encoding="utf-8") if todo_path.exists() else ""
        inside = wbs_path.is_relative_to(REPO_ROOT)
        rel = wbs_path.relative_to(REPO_ROOT) if inside else wbs_path
        n_open = sum(1 for line in new.splitlines() if line.startswith("- [ ]"))
        if new == old:
            print(f"ok       {rel.parent}/TODO.md  ({n_open} open)")
            continue
        drift += 1
        if args.check:
            print(f"DRIFT    {rel.parent}/TODO.md  ({n_open} open)")
            sys.stdout.writelines(
                difflib.unified_diff(
                    old.splitlines(True),
                    new.splitlines(True),
                    "current",
                    "regenerated",
                    n=1,
                )
            )
        else:
            todo_path.write_text(new, encoding="utf-8")
            print(f"WROTE    {rel.parent}/TODO.md  ({n_open} open)")
    return 1 if (args.check and drift) else 0


if __name__ == "__main__":
    sys.exit(main())
