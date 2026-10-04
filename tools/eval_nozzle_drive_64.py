#!/usr/bin/python3
"""Measurement harness for the 64 mm nozzle-drive optimisation (ce-optimize).

Reads a candidate drive configuration (JSON on argv[1] or stdin keys:
pivot [az, z, r], servo_z, servo_az), runs tools/nozzle_servo_linkage_64.py
into a scratch params file, then tools/dorsal_shroud_resize_64.py
--eval-only on it, and prints ONE JSON object of hard metrics:

  linkage_pass  bool   linkage tool PASS (transmission, monotonic, force)
  enclosed      bool   a pure resize of the canonical dorsal shroud encloses
                       every drive point (owner rule 2026-10-04)
  rise_mm       float  crest-height increase of the resized shroud over the
                       canonical crest (PRIMARY, minimise); 999 when not enclosed
  station_rise_mm      station-wise rise incl. the truncation cliff (diagnostic)
  k_h, k_z, z0  float  resize factors / anchor
  holding_n     float  ear holding force (secondary, maximise)
  rod_deg, link_deg    worst transmission angles

Read-only with respect to the repo (writes only to /tmp).  Author: Claude
(Claude Opus 5.5, Anthropic) under the direction of Stab-Rabbit-coding, per
AGENTS.md AI attribution.  License: MIT — see LICENSES/MIT
(SPDX-License-Identifier: MIT)
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def run(cfg: dict) -> dict:
    out = Path(tempfile.mkstemp(suffix=".scad", prefix="nsl_eval_")[1])
    cmd = [sys.executable, str(REPO / "tools/nozzle_servo_linkage_64.py"), "--out", str(out),
           "--pivot", *map(str, cfg["pivot"]), "--servo-z", str(cfg.get("servo_z", 153.0))]
    if cfg.get("servo_az") is not None:
        cmd += ["--servo-az", str(cfg["servo_az"])]
    lk = subprocess.run(cmd, capture_output=True, text=True, timeout=600).stdout
    m = {"linkage_pass": "PASS" in lk, "enclosed": False, "rise_mm": 999.0,
         "k_h": None, "k_z": None, "z0": None}
    def num(pat):
        g = re.search(pat, lk)
        return float(g.group(1)) if g else None
    m["holding_n"] = num(r"holding ([0-9.]+) N")
    m["rod_deg"] = num(r"rod-to-ear angle ([0-9.]+)")
    m["link_deg"] = num(r"link-to-horn-motion angle ([0-9.]+)")
    if m["linkage_pass"]:
        sr = subprocess.run([sys.executable, str(REPO / "tools/dorsal_shroud_resize_64.py"),
                             "--params", str(out), "--eval-only"],
                            capture_output=True, text=True, timeout=900).stdout
        g = re.search(r"Z0 ([0-9.]+): .*K_H ([0-9.]+).*K_Z ([0-9.]+).*max local rise ([0-9.]+)"
                      r".*crest increase ([0-9.-]+)", sr)
        if g:
            m.update(enclosed=True, z0=float(g.group(1)), k_h=float(g.group(2)),
                     k_z=float(g.group(3)), station_rise_mm=float(g.group(4)),
                     rise_mm=float(g.group(5)))
    out.unlink(missing_ok=True)
    return m


if __name__ == "__main__":
    cfg = json.loads(sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read())
    print(json.dumps(run(cfg)))
