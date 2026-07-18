#!/usr/bin/env python3
"""
Pre-commit sanitization and delinting hook for Serenity-UAV.

Ensures that code comments, design specifications, and bug reports are:
1. Free of TODO/issue/bug references that should be tracked in TODO.md or GitHub
2. Sanitized of personally identifiable information (PII)
3. Sanitized of full file paths and directory structures (use relative paths)

Detects patterns that indicate exploitable script failures (race conditions,
memory corruption, etc.) and flags them for immediate bug reporting.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

REPO_ROOT = Path(__file__).parent.parent

# Patterns to detect in comments/docstrings that should be in TODO.md instead
DELINT_PATTERNS = [
    (r"#\s*TODO\s*:", "TODO items should be tracked in TODO.md or GitHub issues"),
    (r"#\s*FIXME\s*:", "FIXME items should be tracked in TODO.md"),
    (r"#\s*BUG\s*:", "Bug reports should use a dedicated bug reporting procedure"),
    (r"#\s*HACK\s*:", "Hacks should be documented in design docs, not inline"),
    (r"//\s*TODO\s*:", "TODO items should be tracked in TODO.md or GitHub issues"),
]

# Patterns to sanitize before commit (PII, full paths)
SANITIZE_PATTERNS = [
    # Full absolute paths - should use relative paths or placeholders
    (
        r"/home/\w+/",
        "Full user paths detected; use relative paths or $HOME placeholders",
    ),
    # Email addresses (unless in proper attribution)
    (
        r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b(?!.*Co-Authored-By)",
        "Email addresses detected; remove or use placeholders in bug reports",
    ),
    # Phone patterns
    (r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", "Phone numbers detected; remove from code"),
]

# Patterns indicating exploitable failures that require immediate bug reporting
EXPLOITABLE_PATTERNS = [
    (r"race\s*condition", "race condition detected"),
    (
        r"memory\s*corruption|heap.*overflow|stack.*overflow|buffer.*overflow",
        "memory corruption pattern detected",
    ),
    (r"use.*after.*free|double.*free", "use-after-free or double-free detected"),
    (r"null.*pointer.*dereference", "null pointer dereference pattern detected"),
    (r"privilege\s*escalation|jailbreak", "privilege escalation pattern detected"),
]


def check_staged_files() -> List[str]:
    """Get list of staged files for commit."""
    os.chdir(REPO_ROOT)
    result = os.popen("git diff --cached --name-only").read().strip()
    return result.split("\n") if result else []


def read_file_safe(filepath: Path) -> str:
    """Safely read file content, handle encoding errors."""
    try:
        return filepath.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Binary file or non-UTF-8; skip
        return ""
    except Exception:
        return ""


def should_check_file(filepath: Path) -> bool:
    """Determine if file should be checked for delinting/sanitization."""
    # Check files: Python, Shell, Markdown, CLAUDE.md, design docs
    check_extensions = {".py", ".sh", ".md", ".txt", ".scad"}
    check_names = {"CLAUDE.md", "README.md", "TODO.md", "REFERENCES.md"}

    if filepath.name in check_names:
        return True
    if filepath.suffix in check_extensions:
        return True
    return False


def check_delint(content: str, filepath: Path) -> List[Tuple[int, str]]:
    """Check for TODO/BUG/FIXME that should be in TODO.md."""
    issues: List[Tuple[int, str]] = []
    # Skip archive and third-party code
    if "archive" in str(filepath):
        return issues

    for line_num, line in enumerate(content.split("\n"), 1):
        for pattern, message in DELINT_PATTERNS:
            if re.search(pattern, line):
                issues.append((line_num, f"{message}: {line.strip()[:60]}..."))
                break
    return issues


def check_sanitization(content: str, filepath: Path) -> List[Tuple[int, str]]:
    """Check for PII and full paths that should be sanitized."""
    issues: List[Tuple[int, str]] = []
    # Skip archive
    if "archive" in str(filepath):
        return issues

    for line_num, line in enumerate(content.split("\n"), 1):
        for pattern, message in SANITIZE_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append((line_num, f"{message}: {line.strip()[:60]}..."))
                break
    return issues


def check_exploitable_patterns(content: str, filepath: Path) -> List[Tuple[int, str]]:
    """Detect patterns indicating exploitable failures in implementation code."""
    issues: List[Tuple[int, str]] = []
    # Skip documentation, test files, design specs, and tools that detect these patterns
    skip_dirs = {"test", "docs", "tools", "scripts", ".github"}
    if any(skip_dir in str(filepath) for skip_dir in skip_dirs):
        return issues

    # Skip if this is a documentation/specification file (README, CLAUDE, etc.)
    if filepath.suffix in {".md"} or "spec" in filepath.name.lower():
        return issues

    for line_num, line in enumerate(content.split("\n"), 1):
        # Skip comments and documentation strings that discuss these patterns
        if any(
            marker in line
            for marker in ["#", "//", '"""', "'''", "<!--", "bug report", "Bug"]
        ):
            continue

        for pattern, message in EXPLOITABLE_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append(
                    (line_num, f"EXPLOITABLE: {message}: {line.strip()[:60]}...")
                )

    return issues


def main() -> int:
    """Run pre-commit checks."""
    staged_files = check_staged_files()
    if not staged_files:
        return 0

    all_issues: List[Tuple[str, int, str]] = []
    exploitable_found = False

    for filename in staged_files:
        if not filename:
            continue

        filepath = REPO_ROOT / filename
        if not filepath.exists():
            continue

        if not should_check_file(filepath):
            continue

        content = read_file_safe(filepath)
        if not content:
            continue

        # Check for delinting issues
        for line_num, issue in check_delint(content, filepath):
            all_issues.append((filename, line_num, issue))

        # Check for sanitization issues
        for line_num, issue in check_sanitization(content, filepath):
            all_issues.append((filename, line_num, issue))

        # Check for exploitable patterns
        for line_num, issue in check_exploitable_patterns(content, filepath):
            all_issues.append((filename, line_num, issue))
            exploitable_found = True

    if all_issues:
        print("\n⚠️  Pre-commit sanitization check found issues:", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        for filename, line_num, issue in all_issues:
            print(f"{filename}:{line_num} - {issue}", file=sys.stderr)
        print("=" * 70, file=sys.stderr)

        if exploitable_found:
            print(
                "\n🔴 CRITICAL: Exploitable failure patterns detected!",
                file=sys.stderr,
            )
            print(
                "   Generate a sanitized bug report with the following information:",
                file=sys.stderr,
            )
            print("   1. Failure type (race, overflow, etc.)", file=sys.stderr)
            print("   2. Affected subsystem (generalized, no paths)", file=sys.stderr)
            print(
                "   3. Reproduction steps (without PII or full paths)",
                file=sys.stderr,
            )
            print(
                "   See CLAUDE.md §[X] for full bug reporting procedure.",
                file=sys.stderr,
            )
            return 1

        # For non-exploitable issues, allow commit with warning but suggest fixing
        print(
            "\n✓ Allowing commit (non-critical issues detected).",
            file=sys.stderr,
        )
        print(
            "  Please review and address these in your next commit or TODO.md.",
            file=sys.stderr,
        )
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
