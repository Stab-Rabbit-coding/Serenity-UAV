#!/bin/sh
# Minimal reproduction for the kicad-cli 9.0.2 `sch erc` SIGSEGV documented in
# ../KICAD_CLI_ERC_SEGFAULT_BUG.md
#
# Expected on an AFFECTED build (KiCad 9.0.2):
#     A absent / 0 pins            exit=0
#     B present / 0 pins           exit=0
#     C absent / 1 pin             exit=139   <-- SIGSEGV
#     D absent / 2 pins            exit=139   <-- SIGSEGV
#     E present(1) / refs 1,2      exit=0
#
# A FIXED build should report an lib_symbol_issues-class violation for C and D
# (exit 5 with --exit-code-violations, or 0 without) instead of dying, and must
# leave A, B and E at exit 0.
#
# NOTE ON THE `.crashes` SUFFIX: variants C and D are stored as
# `*.kicad_sch.crashes` rather than `*.kicad_sch` on purpose.  This repository
# has a pre-commit guard that refuses any `.kicad_sch` / `.kicad_pcb` file
# kicad-cli cannot load — a guard that exists to catch real design-file
# corruption, and which these two deliberately-unloadable files would otherwise
# trip on every commit.  They are copied to a temp dir with the proper extension
# below, so the reproduction is unaffected.
#
# Author: Claude (Opus 5), 2026-07-28.  License: CC BY 4.0.

set -u
cd "$(dirname "$0")" || exit 1

TMP=$(mktemp -d) || exit 1
trap 'rm -rf "$TMP"' EXIT
cp A_absent_0pins.kicad_sch            "$TMP/A_absent_0pins.kicad_sch"
cp B_present_0pins.kicad_sch           "$TMP/B_present_0pins.kicad_sch"
cp C_absent_1pin.kicad_sch.crashes     "$TMP/C_absent_1pin.kicad_sch"
cp D_absent_2pins.kicad_sch.crashes    "$TMP/D_absent_2pins.kicad_sch"
cp E_present_extra_pin.kicad_sch       "$TMP/E_present_extra_pin.kicad_sch"

run() {
    kicad-cli sch erc -o /dev/null --format json "$TMP/$1" >/dev/null 2>&1
    rc=$?
    if [ "$rc" -eq 139 ]; then
        printf '  %-28s exit=%-4s <-- SIGSEGV\n' "$2" "$rc"
    else
        printf '  %-28s exit=%s\n' "$2" "$rc"
    fi
}

printf 'kicad-cli %s\n\n' "$(kicad-cli --version 2>/dev/null)"
run A_absent_0pins.kicad_sch      "A absent / 0 pins"
run B_present_0pins.kicad_sch     "B present / 0 pins"
run C_absent_1pin.kicad_sch       "C absent / 1 pin"
run D_absent_2pins.kicad_sch      "D absent / 2 pins"
run E_present_extra_pin.kicad_sch "E present(1) / refs 1,2"
