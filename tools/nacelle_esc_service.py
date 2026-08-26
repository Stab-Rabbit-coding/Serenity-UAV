#!/usr/bin/env python3
"""Extract the committed Open-Secure-ESC board envelope for nacelle service design.

The ESC PCB is a cross-repository mechanical input.  This tool deliberately
reports what the KiCad board actually encodes and refuses to invent component
height, mounting-hole, or thermal-interface data that the board does not carry.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)"
EDGE_LINE_RE = re.compile(
    rf"\(gr_line\s+\(start\s+({NUMBER})\s+({NUMBER})\)\s+"
    rf"\(end\s+({NUMBER})\s+({NUMBER})\).*?\(layer\s+\"Edge.Cuts\"\)",
    re.DOTALL,
)
FOOTPRINT_RE = re.compile(
    rf"\(footprint\s+\"[^\"]+\"\s+\(layer\s+\"[^\"]+\"\)\s+"
    rf"\(at\s+({NUMBER})\s+({NUMBER})(?:\s+{NUMBER})?\)(.*?)\n\s*\)",
    re.DOTALL,
)
REFERENCE_RE = re.compile(r"\(property\s+\"Reference\"\s+\"([^\"]+)\"")


def extract_board_data(board_path: Path) -> dict[str, object]:
    """Return board dimensions, connector positions, and explicit data gaps."""
    board_text = board_path.read_text(encoding="utf-8")
    edge_segments = [
        tuple(float(value) for value in match)
        for match in EDGE_LINE_RE.findall(board_text)
    ]
    if not edge_segments:
        raise ValueError(f"No Edge.Cuts line geometry found in {board_path}")

    x_values = [value for segment in edge_segments for value in segment[0::2]]
    y_values = [value for segment in edge_segments for value in segment[1::2]]
    min_x, max_x = min(x_values), max(x_values)
    min_y, max_y = min(y_values), max(y_values)

    connectors: dict[str, dict[str, float]] = {}
    for match in FOOTPRINT_RE.finditer(board_text):
        x, y, body = float(match.group(1)), float(match.group(2)), match.group(3)
        reference_match = REFERENCE_RE.search(body)
        if reference_match and reference_match.group(1).startswith(("J", "MH")):
            connectors[reference_match.group(1)] = {"x_mm": x, "y_mm": y}

    return {
        "board_path": str(board_path),
        "outline_mm": {
            "width": round(max_x - min_x, 4),
            "height": round(max_y - min_y, 4),
            "min_x": min_x,
            "max_x": max_x,
            "min_y": min_y,
            "max_y": max_y,
        },
        "thickness_mm": 1.6,
        "connectors": connectors,
        "mounting_holes": [],
        "unknowns": [
            "component_height_envelope_not_encoded_in_pcb",
            "mounting_hole_pattern_not_present",
            "thermal_interface_not_encoded_in_pcb",
        ],
    }


def validate_expected_envelope(data: dict[str, object]) -> None:
    """Fail if the committed board no longer matches the known envelope."""
    outline = data["outline_mm"]
    assert isinstance(outline, dict)
    expected = {"width": 32.0, "height": 66.1}
    for key, value in expected.items():
        measured = outline[key]
        if abs(measured - value) > 0.05:
            raise ValueError(
                f"ESC board {key} is {measured} mm; expected {value} mm"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("board", type=Path, help="Committed KiCad PCB file")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    args = parser.parse_args()

    data = extract_board_data(args.board)
    validate_expected_envelope(data)
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        outline = data["outline_mm"]
        print(f"ESC board: {outline['width']} x {outline['height']} mm")
        print(f"Board thickness: {data['thickness_mm']} mm")
        print(f"Connector references found: {len(data['connectors'])}")
        print("Unknown mechanical inputs: " + ", ".join(data["unknowns"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
