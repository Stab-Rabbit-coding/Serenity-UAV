#!/usr/bin/env python3
"""Commit/CI gate: the joint register is structurally valid and covers the BOM.

Runs tools/joint_register.py --check (U1) and tools/allowables.py --check (U3).
Author: Claude Sonnet 5.5 (Anthropic) for S. Griffing, 2026-11-02.
License: MIT (SPDX-License-Identifier: MIT)
"""
import subprocess
import sys
from pathlib import Path

here = Path(__file__).parent
rc = 0
for script in ("joint_register.py", "allowables.py"):
    rc |= subprocess.call([sys.executable, str(here / script), "--check"])
sys.exit(rc)
