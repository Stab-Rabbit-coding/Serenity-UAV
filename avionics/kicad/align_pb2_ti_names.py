#!/usr/bin/env python3
"""Align Pilot and TACCO names with BeagleBoard / TI naming (owner decision 2026-10-17).

Author: Claude Opus 5.5 (AI), 2026-10-17, for S. Griffing (Stab-Rabbit-coding).
License: MIT (repository licence-by-output rule for code).

Two renames, both purely nominal (no connectivity changes):

1. PocketBeagle 2 header symbol pin names "P1".."P36" become the BeagleBoard
   System Reference Manual designators "P1.01".."P1.36" / "P2.01".."P2.36"
   [REF-SENSOR-041 sec 4.2].  Only pins inside the PB2I-P1-2x18 / PB2I-P2-2x18
   symbols (generator name S_PB2-P1 / S_PB2-P2; schematic + project symbol library) and the pads of the PB2-P1 /
   PB2-P2 footprints (pinfunction) are touched.
2. Ethernet ring parts and nets take TI interface names [REF-SENSOR-049 sec 5.3.1]:
   the DP83825I leg is the AM625 CPSW3G port 2 / RMII2 leg, the USB NIC leg is
   USB1.  The old "1/2" and "B" numbering collided with TI's CPSW port numbers.

Every rename is an exact-token substitution: a token only matches when the
characters on both sides are not [A-Za-z0-9_.-], so "ETH_TXP" never matches
inside "ETH2_TXP" and "T-ETH" never matches inside "T-ETH2".

Usage:  python3 align_pb2_ti_names.py [--apply] FILE...
Without --apply the script prints per-file substitution counts only (dry run).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# --- Ethernet line/device-side net suffixes produced by eth_xfmr()/dp83825i() ---
_ETH_SUFFIXES = [
    "BS", "CRD", "CTD", "LINE_CRX", "LINE_CTX", "LINE_RXN", "LINE_RXP",
    "LINE_TXN", "LINE_TXP", "RXN", "RXP", "TXN", "TXP",
]

# --- passive suffixes produced by the DP83825I / USB-NIC support blocks ---------
_PHY_PASSIVES = ["A1", "A2", "A3", "CRD1", "CRD2", "CTD1", "CTD2", "IO1", "IO2", "IO3"]
_USB_PASSIVES = ["A1", "AK", "CRD", "CTD", "DK", "IO", "V5A", "V5B"]


def build_map() -> Dict[str, str]:
    """Return the exact-token rename map shared by Pilot and TACCO."""
    m: Dict[str, str] = {
        # PHY control nets (both boards)
        "PHY1_RSTN": "RMII2_PHY_RSTN",
        "PHY1_INTRN": "RMII2_PHY_INTRN",
        # Pilot RMII2 leg
        "ETH1-PHY": "PHY-RMII2",
        "ETH1-PHY_RBIAS": "PHY-RMII2_RBIAS",
        "T-ETH": "T-RMII2",
        "ETH1": "J-ETH-RMII2",
        "R-BS1T": "R-RMII2-BST",
        "R-BS1R": "R-RMII2-BSR",
        "C-BS1": "C-RMII2-BS",
        "R-P1-RBIAS": "R-RMII2-RBIAS",
        "R-P1-AD0": "R-RMII2-AD0",
        # Pilot USB1 leg
        "ETH2-USB": "NIC-USB1",
        "ETH2-USB_AVDDK": "NIC-USB1_AVDDK",
        "ETH2-USB_DVDDK": "NIC-USB1_DVDDK",
        "T-ETH2": "T-USB1",
        "ETH2": "J-ETH-USB1",
        "R-BS2T": "R-USB1-BST",
        "R-BS2R": "R-USB1-BSR",
        "C-BS2": "C-USB1-BS",
        # TACCO RMII2 leg
        "ETH-PHY": "PHY-RMII2",
        "ETH-PHY_RBIAS": "PHY-RMII2_RBIAS",
    }
    for s in _ETH_SUFFIXES:
        m[f"ETH_{s}"] = f"ETH_RMII2_{s}"    # Pilot RMII2 leg nets
        m[f"ETH2_{s}"] = f"ETH_USB1_{s}"    # Pilot USB1 leg nets
        m[f"ETHB_{s}"] = f"ETH_RMII2_{s}"   # TACCO RMII2 leg nets
    for s in _PHY_PASSIVES:
        m[f"C-P1-{s}"] = f"C-RMII2-{s}"     # Pilot phy_support("1", ...)
        m[f"C-PHY-{s}"] = f"C-RMII2-{s}"    # TACCO PHY passives
    for s in _USB_PASSIVES:
        m[f"C-U2-{s}"] = f"C-USB1-{s}"      # Pilot USB NIC passives
    return m


_EDGE = r"A-Za-z0-9_.\-"


def token_regex(keys: List[str]) -> re.Pattern:
    """One alternation, longest keys first, bounded by non-identifier characters."""
    alt = "|".join(re.escape(k) for k in sorted(keys, key=len, reverse=True))
    return re.compile(rf"(?<![{_EDGE}])(?:{alt})(?![{_EDGE}])")


def rename_tokens(text: str, mapping: Dict[str, str]) -> Tuple[str, int]:
    """Apply the exact-token map; return (new text, substitution count)."""
    rx = token_regex(list(mapping))
    count = 0

    def sub(mo: re.Match) -> str:
        nonlocal count
        count += 1
        return mapping[mo.group(0)]

    text = rx.sub(sub, text)

    # generator symbol-library names "S_<ref>" and their unit sub-symbols
    # "S_<ref>_0_1" / "S_<ref>_1_1" carry the reference designator too
    alt = "|".join(re.escape(k) for k in sorted(mapping, key=len, reverse=True))
    srx = re.compile(rf"(?<![{_EDGE}])S_({alt})(?=(?:_\d+_\d+)?(?![{_EDGE}]))")

    def ssub(mo: re.Match) -> str:
        nonlocal count
        count += 1
        return "S_" + mapping[mo.group(1)]

    return srx.sub(ssub, text), count


def _block_end(text: str, start: int) -> int:
    """Index just past the S-expression that opens at text[start] == '('."""
    depth = 0
    in_str = False
    i = start
    while i < len(text):
        c = text[i]
        if in_str:
            if c == "\\":
                i += 1
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError("unbalanced S-expression")


def rename_header_pins(text: str) -> Tuple[str, int]:
    """Rename PB2 header pins inside the PB2I symbols and PB2-P1/P2 footprints."""
    count = 0
    out: List[str] = []
    pos = 0
    # schematic / symbol-library symbols: (symbol "...PB2I-P1-2x18..." ...)
    # PCB footprints: (footprint "..." ... (property "Reference" "PB2-P1" ...)
    opener = re.compile(r'\((symbol|footprint) "([^"]*)"')
    for mo in opener.finditer(text):
        if mo.start() < pos:
            continue                     # nested inside a block already handled
        kind, name = mo.group(1), mo.group(2)
        end = _block_end(text, mo.start())
        block = text[mo.start():end]
        rail = None
        if kind == "symbol":
            # generator symbols are named "<lib>:S_PB2-P1" (value "PB2I-P1-2x18")
            hit = re.search(r"(?:^|:)S_PB2-(P[12])$|PB2I-(P[12])-2x18", name)
            hit = (hit.group(1) or hit.group(2)) if hit else None
            rail = hit
        else:
            hit = re.search(r'\(property "Reference" "PB2-(P[12])"', block)
            rail = hit.group(1) if hit else None
        if rail is None:
            continue
        if kind == "symbol":
            rx = re.compile(r'\(name "P(\d{1,2})"')
            new = rx.sub(lambda m: f'(name "{rail}.{int(m.group(1)):02d}"', block)
            n = len(rx.findall(block))
        else:
            rx = re.compile(r'\(pinfunction "P(\d{1,2})"\)')
            new = rx.sub(lambda m: f'(pinfunction "{rail}.{int(m.group(1)):02d}")', block)
            n = len(rx.findall(block))
        count += n
        out.append(text[pos:mo.start()])
        out.append(new)
        pos = end
    out.append(text[pos:])
    return "".join(out), count


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--apply", action="store_true", help="write the files (default: dry run)")
    ap.add_argument("files", nargs="+", type=Path)
    args = ap.parse_args(argv)
    mapping = build_map()
    for f in args.files:
        text = f.read_text(encoding="utf-8")
        new, n_tok = rename_tokens(text, mapping)
        n_pin = 0
        if f.suffix in (".kicad_sch", ".kicad_sym", ".kicad_pcb"):
            new, n_pin = rename_header_pins(new)
        print(f"{f}: {n_tok} net/ref tokens, {n_pin} header pin names")
        if args.apply and new != text:
            f.write_text(new, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
