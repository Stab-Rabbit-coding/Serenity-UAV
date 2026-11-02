#!/usr/bin/env python3
"""Commit/CI gate: the joint register is structurally valid and covers the BOM.

Thin wrapper over tools/joint_register.py --check (plan 2026-11-02-001 U1).
Author: Claude Sonnet 5.5 (Anthropic) for S. Griffing, 2026-11-02.
License: MIT (SPDX-License-Identifier: MIT)
"""
import subprocess
import sys
from pathlib import Path

sys.exit(subprocess.call([sys.executable, str(Path(__file__).with_name("joint_register.py")), "--check"]))
