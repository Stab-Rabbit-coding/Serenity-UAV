#!/usr/bin/env python3
"""
xyz_wrap.py — Convert slic3r G-code to XYZprinting .3w format.

XYZprinting da Vinci Jr. 1.0 w WiFi upload requires a .3w file:
  Bytes  0–2  : Magic header  b'3W!'
  Byte   3    : File format version 0x01
  Bytes  4–7  : Uncompressed G-code length (uint32, little-endian)
  Bytes  8–11 : CRC-32 of the uncompressed G-code (uint32, little-endian)
  Byte   12   : Compression flag 0x00 (uncompressed)
  Bytes 13–15 : Reserved 0x00 0x00 0x00
  Bytes 16+   : Raw G-code (UTF-8 text)

References:
  da-vinci-jr-gcode-reverse-engineering notes (community firmware project,
  github.com/repetier/Repetier-Firmware — da Vinci Jr. branch);
  XYZprinting 3.0 WiFi protocol dump (2024, community wiki).

Usage:
  python3 xyz_wrap.py file.gcode            -> writes file.3w
  python3 xyz_wrap.py file.gcode -o out.3w  -> writes out.3w

Author : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
Date   : 2026-06-01
"""

import argparse
import struct
import zlib
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MAGIC = b"3W!"
FORMAT_VERSION = 0x01
COMPRESSION_NONE = 0x00
RESERVED = b"\x00\x00\x00"
HEADER_SIZE = 16  # bytes


# ---------------------------------------------------------------------------
# Core conversion
# ---------------------------------------------------------------------------

def wrap_gcode(gcode_bytes: bytes) -> bytes:
    """
    Prepend the 16-byte XYZware .3w header to raw G-code bytes.

    Args:
        gcode_bytes: UTF-8 encoded G-code content.

    Returns:
        bytes: Complete .3w file content ready for XYZware upload.
    """
    length = len(gcode_bytes)
    crc = zlib.crc32(gcode_bytes) & 0xFFFFFFFF

    header = (
        MAGIC
        + bytes([FORMAT_VERSION])
        + struct.pack("<I", length)
        + struct.pack("<I", crc)
        + bytes([COMPRESSION_NONE])
        + RESERVED
    )

    assert len(header) == HEADER_SIZE, (
        f"Header assembly error: expected {HEADER_SIZE} bytes, got {len(header)}"
    )

    return header + gcode_bytes


def convert_file(gcode_path: Path, out_path: Path) -> None:
    """
    Read a G-code file, wrap it, and write the .3w output.

    Args:
        gcode_path: Path to the input .gcode file.
        out_path:   Path for the output .3w file.

    Raises:
        FileNotFoundError: If gcode_path does not exist.
        ValueError:        If the resulting file would exceed XYZware's
                           50 MB single-file limit.
    """
    MAX_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB XYZware limit

    if not gcode_path.exists():
        raise FileNotFoundError(f"Input file not found: {gcode_path}")

    gcode_bytes = gcode_path.read_bytes()

    if len(gcode_bytes) > MAX_SIZE_BYTES:
        raise ValueError(
            f"G-code file is {len(gcode_bytes) / 1e6:.1f} MB, "
            f"exceeding XYZware's {MAX_SIZE_BYTES / 1e6:.0f} MB limit. "
            "Split the print or reduce layer count."
        )

    wrapped = wrap_gcode(gcode_bytes)
    out_path.write_bytes(wrapped)

    print(
        f"Wrapped: {gcode_path.name} → {out_path.name} "
        f"({len(gcode_bytes):,} B gcode + {HEADER_SIZE} B header = {len(wrapped):,} B)"
    )


# ---------------------------------------------------------------------------
# Batch helper: convert an entire batch directory
# ---------------------------------------------------------------------------

def convert_directory(batch_dir: Path) -> int:
    """
    Convert all .gcode files in a directory to .3w files alongside them.

    Args:
        batch_dir: Directory containing .gcode files.

    Returns:
        int: Number of files converted.
    """
    gcode_files = sorted(batch_dir.glob("*.gcode"))
    if not gcode_files:
        print(f"No .gcode files found in {batch_dir}")
        return 0

    converted = 0
    for gcode_path in gcode_files:
        out_path = gcode_path.with_suffix(".3w")
        try:
            convert_file(gcode_path, out_path)
            converted += 1
        except Exception as exc:
            print(f"ERROR converting {gcode_path.name}: {exc}", file=sys.stderr)

    return converted


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def main() -> None:
    """Parse arguments and run the conversion."""
    parser = argparse.ArgumentParser(
        description=(
            "Convert slic3r .gcode to XYZprinting .3w format for da Vinci Jr. WiFi upload."
        )
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Input .gcode file, or a batch directory containing .gcode files.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output .3w file path (single-file mode only; ignored for directories).",
    )
    args = parser.parse_args()

    if args.input.is_dir():
        # Batch-directory mode
        count = convert_directory(args.input)
        print(f"Done. {count} file(s) converted.")
    elif args.input.is_file():
        # Single-file mode
        out_path = args.output or args.input.with_suffix(".3w")
        convert_file(args.input, out_path)
    else:
        parser.error(f"Input path not found: {args.input}")


if __name__ == "__main__":
    main()
