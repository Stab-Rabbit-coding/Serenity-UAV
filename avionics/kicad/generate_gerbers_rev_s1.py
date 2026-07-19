#!/usr/bin/env python3
"""
generate_gerbers_rev_s1.py — Generate Gerber files for Rev S1 boards (Emma, Zoë, Kaylee)

Usage:
    python3 generate_gerbers_rev_s1.py [emma|zoë|kaylee]

Generates production Gerber and drill files to:
  - avionics/kicad/gerbers/Emma-S1/
  - avionics/kicad/gerbers/CAPE-B-2-S1/
  - avionics/kicad/gerbers/Kaylee-S1/

Author: Claude Haiku 4.5 (Anthropic) — 2026-07-18
License: CC BY 4.0
"""

import os
import sys
import subprocess
from pathlib import Path

BOARDS = {
    "emma": {
        "pcb": "avionics/kicad/Emma/kicads/Emma.kicad_pcb",
        "pro": "avionics/kicad/Emma/kicads/Emma.kicad_pro",
        "gerber_dir": "avionics/kicad/gerbers/Emma-S1",
        "name": "Emma Rev S1",
    },
    "zoë": {
        "pcb": "avionics/kicad/Zoë/kicads/Zoë.kicad_pcb",
        "pro": "avionics/kicad/Zoë/kicads/Zoë.kicad_pro",
        "gerber_dir": "avionics/kicad/gerbers/CAPE-B-2-S1",
        "name": "Zoë Rev S1",
    },
    "kaylee": {
        "pcb": "avionics/kicad/Kaylee/kicads/Kaylee.kicad_pcb",
        "pro": "avionics/kicad/Kaylee/kicads/Kaylee.kicad_pro",
        "gerber_dir": "avionics/kicad/gerbers/Kaylee-S1",
        "name": "Kaylee Rev S1",
    },
}


def generate_gerbers(board_name, board_info):
    """Generate gerbers for a board using kicad-cli"""
    pcb_file = board_info["pcb"]
    pro_file = board_info["pro"]
    gerber_dir = board_info["gerber_dir"]
    display_name = board_info["name"]

    if not Path(pcb_file).exists():
        print(f"✗ PCB file not found: {pcb_file}")
        return False

    if not Path(pro_file).exists():
        print(f"✗ Project file not found: {pro_file}")
        return False

    # Create output directory
    Path(gerber_dir).mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*70}")
    print(f"Generating gerbers for {display_name}")
    print(f"{'='*70}")
    print(f"PCB file: {pcb_file}")
    print(f"Output directory: {gerber_dir}")

    try:
        # Run kicad-cli to generate gerbers
        result = subprocess.run(
            [
                "kicad-cli",
                "pcb",
                "export",
                "gerbers",
                "--output-dir",
                gerber_dir,
                pcb_file,
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            print(f"✗ Gerber generation failed:")
            print(result.stderr)
            return False

        print(result.stdout)

        # Run kicad-cli to generate drill file
        result = subprocess.run(
            [
                "kicad-cli",
                "pcb",
                "export",
                "drill",
                "--output",
                os.path.join(gerber_dir, f"{board_name}.drl"),
                pcb_file,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            print(f"⚠ Drill file generation had issues:")
            print(result.stderr)
        else:
            print(result.stdout)

        # Verify output files
        gbr_files = list(Path(gerber_dir).glob("*.gbr"))
        drl_files = list(Path(gerber_dir).glob("*.drl"))

        if gbr_files:
            print(f"\n✓ Generated {len(gbr_files)} Gerber files")
            for f in sorted(gbr_files):
                print(f"  • {f.name}")
        else:
            print(f"✗ No Gerber files generated")
            return False

        if drl_files:
            print(f"\n✓ Generated {len(drl_files)} drill file(s)")
            for f in sorted(drl_files):
                print(f"  • {f.name}")
        else:
            print(f"⚠ No drill files generated")

        return True

    except subprocess.TimeoutExpired:
        print(f"✗ Gerber generation timed out")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    if len(sys.argv) > 1:
        board_name = sys.argv[1].lower()
        if board_name not in BOARDS:
            print(f"Unknown board: {board_name}")
            print(f"Available: {', '.join(BOARDS.keys())}")
            return 1

        boards_to_process = {board_name: BOARDS[board_name]}
    else:
        boards_to_process = BOARDS

    print("Rev S1 Gerber Generator")
    print(f"Processing {len(boards_to_process)} board(s)...")

    results = {}
    for board_name, board_info in boards_to_process.items():
        success = generate_gerbers(board_name, board_info)
        results[board_name] = "✓" if success else "✗"

    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    for board_name, status in results.items():
        print(f"{status} {board_name:20s} — {BOARDS[board_name]['name']}")

    failed = [b for b, s in results.items() if s == "✗"]
    if failed:
        print(f"\n✗ {len(failed)} board(s) failed")
        return 1
    else:
        print(f"\n✓ All {len(results)} board(s) completed successfully")
        return 0


if __name__ == "__main__":
    sys.exit(main())
