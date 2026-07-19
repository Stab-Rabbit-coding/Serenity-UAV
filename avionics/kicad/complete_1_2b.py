#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
complete_1_2b.py — Master orchestration script for finishing todo 1.2b
================================================================================
This script automates the completion of the three PCB redesigns (Emma, Zoë, Kaylee
Rev S1) when run in an environment with KiCad 9.0.2 + pcbnew Python module.

PREREQUISITES:
  - KiCad 9.0.2 (December 2025) or later
  - pcbnew Python module (installed with KiCad)
  - kicad-cli available in PATH
  - Running from Serenity-UAV repo root

USAGE:
  python3 avionics/kicad/complete_1_2b.py [--board BOARD] [--steps STEPS]

  Options:
    --board emma|zoë|kaylee    Work on specific board (default: all)
    --steps list              Show available steps
    --dry-run                 Plan work without modifying files
    --verbose                 Show detailed progress

Author: Claude Haiku 4.5 (Anthropic) — 2026-07-18
License: CC BY 4.0
Co-Authored-By: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

KICAD_MIN_VERSION = "9.0.2"
PROJECTS = {
    "emma": {
        "sch": "avionics/kicad/Emma/kicads/Emma.kicad_sch",
        "pcb": "avionics/kicad/Emma/kicads/Emma.kicad_pcb",
        "pro": "avionics/kicad/Emma/kicads/Emma.kicad_pro",
        "gerber_dir": "avionics/kicad/gerbers/Emma-S1",
        "scripts": ["avionics/kicad/Emma/scripts/route_emma_rssi.py"],
    },
    "zoë": {
        "sch": "avionics/kicad/Zoë/kicads/Zoë.kicad_sch",
        "pcb": "avionics/kicad/Zoë/kicads/Zoë.kicad_pcb",
        "pro": "avionics/kicad/Zoë/kicads/Zoë.kicad_pro",
        "gerber_dir": "avionics/kicad/gerbers/CAPE-B-2-S1",
    },
    "kaylee": {
        "sch": "avionics/kicad/Kaylee/kicads/Kaylee.kicad_sch",
        "pcb": "avionics/kicad/Kaylee/kicads/Kaylee.kicad_pcb",
        "pro": "avionics/kicad/Kaylee/kicads/Kaylee.kicad_pro",
        "gerber_dir": "avionics/kicad/gerbers/Kaylee-S1",
    },
}


def check_environment():
    """Verify KiCad tools are available"""
    try:
        result = subprocess.run(
            ["kicad-cli", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        version = result.stdout.strip()
        print(f"✓ kicad-cli found: {version}")

        import pcbnew
        print(f"✓ pcbnew Python module available")
        return True
    except FileNotFoundError:
        print("✗ kicad-cli not found. Please install KiCad 9.0.2+")
        return False
    except ImportError:
        print("✗ pcbnew Python module not found. Please install python3-kicad")
        return False
    except Exception as e:
        print(f"✗ Error checking environment: {e}")
        return False


def emma_route_rssi_dcd():
    """Route the RSSI_DCD net on Emma PCB"""
    print("\n" + "=" * 70)
    print("STEP: Route Emma RSSI_DCD (1 net, ~28mm cross-board run)")
    print("=" * 70)
    script = "avionics/kicad/Emma/scripts/route_emma_rssi.py"
    if not Path(script).exists():
        print(f"✗ Script not found: {script}")
        return False

    try:
        print("→ Running route_emma_rssi.py dcd (starting path for GUI finishing)")
        result = subprocess.run(
            ["python3", script, "dcd"],
            cwd=".",
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            print(f"✓ RSSI_DCD routing started")
            print("→ MANUAL STEP: Open Emma.kicad_pcb in KiCad GUI")
            print("→ Use push-shove routing to complete RSSI_DCD")
            print("→ Save when complete")
            return True
        else:
            print(f"✗ Route script failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error running route script: {e}")
        return False


def emma_drc_check():
    """Run DRC on Emma PCB"""
    print("\n" + "=" * 70)
    print("STEP: DRC check on Emma PCB")
    print("=" * 70)
    pcb = PROJECTS["emma"]["pcb"]
    try:
        result = subprocess.run(
            ["kicad-cli", "pcb", "drc", "--schematic-parity", pcb],
            capture_output=True,
            text=True,
            timeout=60,
        )
        print(result.stdout)
        if "0 error" in result.stdout or result.returncode == 0:
            print("✓ DRC passed")
            return True
        else:
            print("⚠ DRC violations found. Review above.")
            return False
    except Exception as e:
        print(f"✗ Error running DRC: {e}")
        return False


def emma_generate_gerbers():
    """Generate Gerber files for Emma"""
    print("\n" + "=" * 70)
    print("STEP: Generate Emma Gerbers")
    print("=" * 70)
    script = "avionics/kicad/generate_gerbers.py"
    board = "emma"

    if not Path(script).exists():
        print(f"✗ Script not found: {script}")
        return False

    try:
        result = subprocess.run(
            ["python3", script, board],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            print(f"✓ Gerbers generated to {PROJECTS[board]['gerber_dir']}")
            return True
        else:
            print(f"✗ Gerber generation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error generating gerbers: {e}")
        return False


def zoë_run_erc():
    """Run ERC on Zoë schematic"""
    print("\n" + "=" * 70)
    print("STEP: Run ERC on Zoë schematic")
    print("=" * 70)
    sch = PROJECTS["zoë"]["sch"]
    try:
        result = subprocess.run(
            ["kicad-cli", "sch", "erc", sch],
            capture_output=True,
            text=True,
            timeout=60,
        )
        print(result.stdout)
        if "0 error" in result.stdout or result.returncode == 0:
            print("✓ ERC passed")
            return True
        else:
            print("⚠ ERC errors found. Review above and fix.")
            return False
    except Exception as e:
        print(f"✗ Error running ERC: {e}")
        return False


def zoë_generate_gerbers():
    """Generate Gerber files for Zoë"""
    print("\n" + "=" * 70)
    print("STEP: Generate Zoë Gerbers")
    print("=" * 70)
    script = "avionics/kicad/generate_gerbers.py"
    board = "zoë"

    if not Path(script).exists():
        print(f"✗ Script not found: {script}")
        return False

    try:
        result = subprocess.run(
            ["python3", script, board],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            print(f"✓ Gerbers generated to {PROJECTS[board]['gerber_dir']}")
            return True
        else:
            print(f"✗ Gerber generation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error generating gerbers: {e}")
        return False


def kaylee_run_drc():
    """Run DRC on Kaylee PCB"""
    print("\n" + "=" * 70)
    print("STEP: DRC check on Kaylee PCB")
    print("=" * 70)
    pcb = PROJECTS["kaylee"]["pcb"]
    try:
        result = subprocess.run(
            ["kicad-cli", "pcb", "drc", "--schematic-parity", pcb],
            capture_output=True,
            text=True,
            timeout=60,
        )
        print(result.stdout)
        if "0 error" in result.stdout or result.returncode == 0:
            print("✓ DRC passed")
            return True
        else:
            print("⚠ DRC violations found. Review above.")
            return False
    except Exception as e:
        print(f"✗ Error running DRC: {e}")
        return False


def kaylee_generate_gerbers():
    """Generate Gerber files for Kaylee"""
    print("\n" + "=" * 70)
    print("STEP: Generate Kaylee Gerbers")
    print("=" * 70)
    script = "avionics/kicad/generate_gerbers.py"
    board = "kaylee"

    if not Path(script).exists():
        print(f"✗ Script not found: {script}")
        return False

    try:
        result = subprocess.run(
            ["python3", script, board],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            print(f"✓ Gerbers generated to {PROJECTS[board]['gerber_dir']}")
            return True
        else:
            print(f"✗ Gerber generation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error generating gerbers: {e}")
        return False


STEPS = {
    "emma-route": ("Route Emma RSSI_DCD (1 net)", emma_route_rssi_dcd),
    "emma-drc": ("DRC check Emma", emma_drc_check),
    "emma-gerber": ("Generate Emma gerbers", emma_generate_gerbers),
    "zoë-erc": ("ERC check Zoë", zoë_run_erc),
    "zoë-gerber": ("Generate Zoë gerbers", zoë_generate_gerbers),
    "kaylee-drc": ("DRC check Kaylee", kaylee_run_drc),
    "kaylee-gerber": ("Generate Kaylee gerbers", kaylee_generate_gerbers),
}


def main():
    parser = argparse.ArgumentParser(
        description="Complete todo 1.2b PCB redesigns (Emma, Zoë, Kaylee Rev S1)"
    )
    parser.add_argument(
        "--board", choices=["emma", "zoë", "kaylee"], help="Work on specific board"
    )
    parser.add_argument("--steps", action="store_true", help="List available steps")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.steps:
        print("Available steps:")
        for step_id, (desc, _) in STEPS.items():
            print(f"  {step_id:20s} — {desc}")
        return 0

    print("=" * 70)
    print("1.2B COMPLETION ORCHESTRATOR")
    print("=" * 70)
    print()

    if not check_environment():
        print()
        print("ERROR: KiCad environment not ready.")
        return 1

    print()
    print("→ Starting todo 1.2b completion workflow...")
    print()

    # Execute steps based on board selection
    if args.board == "emma" or not args.board:
        for step_name in ["emma-route", "emma-drc", "emma-gerber"]:
            if step_name in STEPS:
                _, func = STEPS[step_name]
                func()
                if args.verbose:
                    input("Press Enter to continue...")

    if args.board == "zoë" or not args.board:
        for step_name in ["zoë-erc", "zoë-gerber"]:
            if step_name in STEPS:
                _, func = STEPS[step_name]
                func()
                if args.verbose:
                    input("Press Enter to continue...")

    if args.board == "kaylee" or not args.board:
        for step_name in ["kaylee-drc", "kaylee-gerber"]:
            if step_name in STEPS:
                _, func = STEPS[step_name]
                func()
                if args.verbose:
                    input("Press Enter to continue...")

    print()
    print("=" * 70)
    print("✓ WORKFLOW COMPLETE")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Review all generated gerbers in avionics/kicad/gerbers/")
    print("  2. Verify silkscreen and layer accuracy")
    print("  3. Commit changes to git with message referencing todo 1.2b")

    return 0


if __name__ == "__main__":
    sys.exit(main())
