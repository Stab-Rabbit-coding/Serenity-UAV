"""Read the 64 mm nacelle's single-source shell scale (nacelle_64_scale.scad).

Every tool that places geometry on the 64 mm pod imports its scale and the
stations derived from it from here, so the 2026-10-05 uniform enlargement (and
any later resize) is one edit in the SCAD file.

Also reads PIVOT_Z from the pod wrapper, which is re-iterated to the rotating
assembly's CG whenever the scale changes (tools/nacelle_mass_cg_64.py).

Author: Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding.  License: MIT — see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""
from __future__ import annotations

import ast
import operator
import re
from functools import lru_cache
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCALE_SCAD = REPO / "airframe/openscad/nacelles/nacelle_64_scale.scad"
POD_SCAD = REPO / "airframe/openscad/nacelles/nacelle_pod_64mm_tandem.scad"

_OPS = {ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv}


def _eval(node, env):
    """Evaluate a numeric SCAD expression: numbers, names, + - * /, unary -."""
    if isinstance(node, ast.Expression):
        return _eval(node.body, env)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.Name):
        return env[node.id]
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left, env), _eval(node.right, env))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -_eval(node.operand, env)
    raise ValueError(f"unsupported expression in scale file: {ast.dump(node)}")


@lru_cache(maxsize=None)
def values() -> dict:
    """All `NAME = <numeric expr>;` assignments in nacelle_64_scale.scad."""
    env: dict = {}
    for m in re.finditer(r"^(\w+)\s*=\s*([^;]+);", SCALE_SCAD.read_text(), re.M):
        env[m.group(1)] = _eval(ast.parse(m.group(2), mode="eval"), env)
    return env


def get(name: str) -> float:
    """One scale-file value, e.g. get("P64_K")."""
    return values()[name]


def pivot_z() -> float:
    """PIVOT_Z as set in the pod wrapper (a literal, re-iterated to the CG)."""
    m = re.search(r"^PIVOT_Z\s*=\s*([0-9.]+)\s*;", POD_SCAD.read_text(), re.M)
    if not m:
        raise ValueError("PIVOT_Z literal not found in the pod wrapper")
    return float(m.group(1))
