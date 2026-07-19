#!/usr/bin/env bash
# =============================================================================
# slice_all_batches.sh — Serenity-Class UAV Rev T Prototype Slice Runner
# =============================================================================
# Author : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
# License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
# Date   : 2026-06-02
# Slicer : PrusaSlicer (apt) — CLI-compatible fork of Slic3r
# Printer: XYZprinting da Vinci Jr. 1.0 w (150×150×150 mm, 0.4 mm nozzle)
# Output : airframe/gcode/davinci-jr-proto/<batch>/  (one .gcode per part)
#
# Usage:
#   cd /home/user/Serenity-UAV
#   bash airframe/gcode/davinci-jr-proto/slice_all_batches.sh [BATCH_LETTER]
#
#   BATCH_LETTER is optional: A B C D E F G1 G2 H I J K L M N O P Q VISUAL
#   Omit to run all batches.
#
# Note on G-code format:
#   Output is standard RepRap G-code.  To print on a da Vinci Jr. with
#   stock XYZware firmware, convert using xyz_wrap.py in this directory
#   (wrapper adds the 8-byte XYZ header expected by XYZware WiFi upload).
#   If the printer runs Repetier firmware, load .gcode directly via USB.
#
# PrusaSlicer CLI options used in this script:
#   --export-gcode    : required for headless G-code export
#   --load            : printer/filament/print profile (.ini — slic3r format compatible)
#   --layer-height    : mm per layer
#   --fill-density    : infill percentage (e.g. 20%)
#   --perimeters      : shell count
#   --support-material: enable support (flag present = on)
#   --support-material-buildplate-only : support on build plate faces only
#   --raft-layers     : 0=no raft, 1=1-layer raft, 2=full raft
#   --scale           : uniform scale factor (0.86 = 86%)
#   --duplicate       : number of copies to arrange on plate
#   --center          : X,Y centre of bed in mm
#   -o                : output .gcode path
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Paths — all relative to repo root
# ---------------------------------------------------------------------------
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

STL_FUSELAGE="${REPO_ROOT}/airframe/stls/fuselage"
STL_AFT_EDF="${REPO_ROOT}/airframe/stls/fuselage/aft-edf"
STL_CARGO_BAY="${REPO_ROOT}/airframe/stls/fuselage/cargo"
STL_NACELLES="${REPO_ROOT}/airframe/stls/nacelles"
STL_NOZZLES="${REPO_ROOT}/airframe/stls/nacelles/nozzles"
STL_WINGS="${REPO_ROOT}/airframe/stls/wings"

GCODE_ROOT="${REPO_ROOT}/airframe/gcode/davinci-jr-proto"
CFG="${GCODE_ROOT}/davinci_jr_pla.ini"
SLICER="prusa-slicer"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
log() { printf "[%s] %s\n" "$(date +%H:%M:%S)" "$*"; }

# slice STL → gcode with per-call overrides
# Usage: slice <outdir> <scale> <infill%> <raft_layers> <support> <stl_path> [extra_slicer_args...]
slice() {
    local outdir="$1"
    local scale="$2"   # e.g. 1 or 0.86
    local infill="$3"  # e.g. 20%
    local raft="$4"    # integer: 0=none 1=raft
    local support="$5" # "yes" or "no"
    local stl="$6"
    shift 6
    local extras=("$@")

    local base
    base="$(basename "${stl%.stl}")"
    local out="${outdir}/${base}.gcode"

    mkdir -p "$outdir"

    local sup_flag=()
    [[ "$support" == "yes" ]] && sup_flag=(--support-material)

    log "  Slicing: ${base} (scale=${scale}, infill=${infill}, raft=${raft}, support=${support})"

    "$SLICER" \
        --export-gcode \
        --load "$CFG" \
        --layer-height 0.2 \
        --scale "$scale" \
        --fill-density "$infill" \
        --raft-layers "$raft" \
        "${sup_flag[@]}" \
        "${extras[@]}" \
        --center 75,75 \
        -o "$out" \
        "$stl" \
        2>&1 | grep -Ev "^([0-9]+ => |=> |Slicing result exported|Done\.|[[:space:]]*$)" || true

    log "  → ${out##"${REPO_ROOT}/"}"
}

# Convenience: print a batch header
batch_header() {
    local letter="$1"
    local name="$2"
    log "=============================================="
    log "BATCH ${letter} — ${name}"
    log "=============================================="
}

# ---------------------------------------------------------------------------
# Batch runner
# ---------------------------------------------------------------------------
run_batch() {
    local batch="$1"
    local OUT="${GCODE_ROOT}/batch_${batch}"

    case "$batch" in

    # -----------------------------------------------------------------------
    # BATCH A — Small Cargo Hardware (★★★ validation priority)
    # All parts <50 mm — plate them individually; operator arranges in XYZware
    # Infill 20%, no support, raft ON (thin flat parts)
    # -----------------------------------------------------------------------
    A)
        batch_header A "Small Cargo Hardware (7 parts)"
        slice "$OUT" 1 "20%" 1 "no" "${STL_CARGO_BAY}/cargo_door_servo_bracket.stl"
        slice "$OUT" 1 "20%" 1 "no" "${STL_CARGO_BAY}/cargo_release_servo_bracket.stl"
        slice "$OUT" 1 "20%" 1 "no" "${STL_CARGO_BAY}/cargo_drv8833_tray.stl"
        slice "$OUT" 1 "20%" 0 "no" "${STL_CARGO_BAY}/cargo_winch_motor_mount.stl"
        slice "$OUT" 1 "20%" 0 "no" "${STL_CARGO_BAY}/cargo_winch_spool.stl"
        slice "$OUT" 1 "20%" 1 "no" "${STL_CARGO_BAY}/cargo_gps_retention_ring.stl"
        slice "$OUT" 1 "20%" 1 "no" "${STL_CARGO_BAY}/cargo_fpv_bezel.stl"
        ;;

    # -----------------------------------------------------------------------
    # BATCH B — Port Cargo Door (★★★)
    # 108×33.7×87 mm — fits at 1:1; support on hinge tab only (touching bd)
    # -----------------------------------------------------------------------
    B)
        batch_header B "Port Cargo Door"
        slice "$OUT" 1 "20%" 0 "yes" "${STL_CARGO_BAY}/cargo_door_port.stl" \
            --support-material-buildplate-only
        ;;

    # -----------------------------------------------------------------------
    # BATCH C — Starboard Cargo Door (★★★)
    # Mirror of B; same settings
    # -----------------------------------------------------------------------
    C)
        batch_header C "Starboard Cargo Door"
        slice "$OUT" 1 "20%" 0 "yes" "${STL_CARGO_BAY}/cargo_door_stbd.stl" \
            --support-material-buildplate-only
        ;;

    # -----------------------------------------------------------------------
    # BATCH D — Cargo Auto-latch Cradle (★★★)
    # 110×80×72 mm — fits at 1:1; support for latch tab overhang
    # Infill 25% (functional part)
    # -----------------------------------------------------------------------
    D)
        batch_header D "Cargo Auto-latch Cradle"
        slice "$OUT" 1 "25%" 0 "yes" "${STL_CARGO_BAY}/cargo_cradle_autolatch.stl" \
            --support-material-buildplate-only
        ;;

    # -----------------------------------------------------------------------
    # BATCH E — Nacelle Nozzle Iris Petals — 8 off (★★)
    # 31×22.8×19.5 mm each; print 8 copies arranged in 4×2 grid
    # Infill 15% (non-structural verification print)
    # -----------------------------------------------------------------------
    E)
        batch_header E "Nacelle Nozzle Iris Petals (8 off)"
        slice "$OUT" 1 "15%" 0 "no" "${STL_NOZZLES}/nacelle_nozzle_petal.stl" \
            --duplicate 8
        ;;

    # -----------------------------------------------------------------------
    # BATCH F — Nacelle Nozzle Ring + Gear Parts (★★)
    # Ring: 62×62×6 mm; gear parts <30 mm — all fit together
    # Infill 20%, no support
    # Note: pinion_a_bracket removed — engine fold mechanism not in this build
    # -----------------------------------------------------------------------
    F)
        batch_header F "Nacelle Nozzle Ring + Gear Parts"
        slice "$OUT" 1 "20%" 0 "no" "${STL_NOZZLES}/nacelle_nozzle_ring.stl"
        slice "$OUT" 1 "20%" 0 "no" "${STL_NOZZLES}/nacelle_bevel_housing.stl" \
            --duplicate 2
        slice "$OUT" 1 "20%" 0 "no" "${STL_NOZZLES}/nacelle_bevel_pair.stl" \
            --duplicate 2
        slice "$OUT" 1 "20%" 0 "no" "${STL_NACELLES}/nacelle_pinion.stl" \
            --duplicate 2
        # sector_gear_22mm_fixed.stl: repaired binary STL (original ASCII had
        # ~200 k mesh-loop errors at 0.2 mm layer height; fixed via slic3r --repair).
        slice "$OUT" 1 "20%" 0 "no" "${STL_NACELLES}/sector_gear_22mm_fixed.stl" \
            --duplicate 2
        ;;

    # -----------------------------------------------------------------------
    # BATCH G1 — Rear Nozzle Frame (★★)
    # 131×131×20 mm — largest 1:1 single part; fills plate edge-to-edge
    # Raft ON for adhesion; no support (ribs are vertical)
    # -----------------------------------------------------------------------
    G1)
        batch_header G1 "Rear Nozzle Frame"
        slice "$OUT" 1 "20%" 1 "no" "${STL_AFT_EDF}/rear_nozzle_frame.stl"
        ;;

    # -----------------------------------------------------------------------
    # BATCH G2 — Rear Nozzle Petals — 8 off (★★)
    # 65.5×40.7×18.5 mm; print 4 per plate (two plates)
    # -----------------------------------------------------------------------
    G2)
        batch_header G2 "Rear Nozzle Petals (4 per plate)"
        slice "$OUT" 1 "20%" 0 "no" "${STL_AFT_EDF}/rear_nozzle_petal.stl" \
            --duplicate 4
        ;;

    # -----------------------------------------------------------------------
    # BATCH I — 120 mm EDF Motor Mount Spider (★★)
    # 126×126×53 mm — fits 1:1; support for spider arm overhangs
    # Infill 25%
    # -----------------------------------------------------------------------
    I)
        batch_header I "120 mm EDF Motor Mount Spider"
        slice "$OUT" 1 "25%" 0 "yes" "${STL_AFT_EDF}/edf_120_motor_mount.stl" \
            --support-material-buildplate-only
        ;;

    # -----------------------------------------------------------------------
    # BATCH J — 120 mm EDF Thrust Tube (★★)
    # Native: 134×134×167 mm → scale 89% → 119×119×148.6 mm
    # Infill 20%; support off (smooth interior is key verification)
    # -----------------------------------------------------------------------
    J)
        batch_header J "120 mm EDF Thrust Tube (89% scale)"
        slice "$OUT" 0.89 "20%" 0 "no" "${STL_AFT_EDF}/edf_120_thrust_tube.stl"
        ;;

    # -----------------------------------------------------------------------
    # BATCH K — Complete Nacelle Pods — Port & Starboard (★★)
    # Rev T pods integrate EDF bore, stators, and spider mounts in one body.
    # Native: 75.6×83.3×185.2 mm → scale 81% → 61.2×67.5×150.0 mm
    # Each pod on its own plate; support for intake/nozzle face overhangs
    # -----------------------------------------------------------------------
    K)
        batch_header K "Complete Nacelle Pods Port+Stbd (81% scale)"
        slice "$OUT" 0.81 "20%" 0 "yes" \
            "${STL_NACELLES}/s_nacelle_port_revt.stl" \
            --support-material-buildplate-only
        slice "$OUT" 0.81 "20%" 0 "yes" \
            "${STL_NACELLES}/s_nacelle_stbd_revt.stl" \
            --support-material-buildplate-only
        ;;

    # -----------------------------------------------------------------------
    # BATCH L — Landing Gear: Feet + Legs + Wings (★)
    # Feet: 78.2×98.4×9 mm (1:1); Legs: 96.1×150.1×7.5 → 99% → 95×148.6 mm
    # Wings (S1223): 161×85.7×~20 mm → scale 93% → 149.7×79.7×18.6 mm
    #   Port and starboard printed separately (S1223 replaced combined flat-plate)
    # -----------------------------------------------------------------------
    L)
        batch_header L "Landing Gear: Feet + Legs + Wings"
        slice "$OUT" 1 "15%" 0 "no" "${STL_FUSELAGE}/feet_x_4_scaled24.stl"
        slice "$OUT" 0.99 "15%" 0 "no" "${STL_FUSELAGE}/legs_scaled24.stl"
        slice "$OUT" 0.93 "15%" 0 "no" "${STL_WINGS}/wing_port_s1223_revo.stl"
        slice "$OUT" 0.93 "15%" 0 "no" "${STL_WINGS}/wing_stbd_s1223_revo.stl"
        ;;

    # -----------------------------------------------------------------------
    # BATCH M — Head Shell (★ visual reference)
    # Native: 129.4×235.1×140.7 mm → scale 63% → 81.5×148.1×88.6 mm
    # Support: yes (cockpit dome overhang)
    # -----------------------------------------------------------------------
    M)
        batch_header M "Head Shell (63% scale)"
        slice "$OUT" 0.63 "15%" 0 "yes" "${STL_FUSELAGE}/head_shell24.stl" \
            --support-material-buildplate-only
        ;;

    # -----------------------------------------------------------------------
    # BATCH N — Middle Shell (★ visual reference)
    # Native: 177.1×164.8×73.2 mm → scale 84% → 148.8×138.4×61.5 mm
    # No support (wide flat base prints clean)
    # -----------------------------------------------------------------------
    N)
        batch_header N "Middle Shell (84% scale)"
        slice "$OUT" 0.84 "15%" 0 "no" "${STL_FUSELAGE}/middle_shell24.stl"
        ;;

    # -----------------------------------------------------------------------
    # BATCH O — Cargo Section Shell (★ visual reference)
    # Native: 194.7×203.6×163.2 mm → scale 73% → 142.1×148.6×119.1 mm
    # Support: yes (belly door opening overhang)
    # -----------------------------------------------------------------------
    O)
        batch_header O "Cargo Section Shell (73% scale)"
        slice "$OUT" 0.73 "15%" 0 "yes" "${STL_CARGO_BAY}/cargo_sect_shell24.stl" \
            --support-material-buildplate-only
        ;;

    # -----------------------------------------------------------------------
    # BATCH P — Rear Shell (★ visual reference)
    # Native: 140.9×158.0×181.7 mm → scale 82% → 115.5×129.6×149.0 mm
    # Support: yes (engine bell recess overhang)
    # -----------------------------------------------------------------------
    P)
        batch_header P "Rear Shell (82% scale)"
        slice "$OUT" 0.82 "15%" 0 "yes" "${STL_AFT_EDF}/rear_shell24.stl" \
            --support-material-buildplate-only
        ;;

    # -----------------------------------------------------------------------
    # BATCH Q — Nacelle Pods L+R (★ visual reference)
    # Rev T complete pods at 81% scale (max that fits 150 mm bed along Z).
    # Note: EDF bore shrinks to 40.5 mm at 81% — EDF won't fit; visual only.
    # -----------------------------------------------------------------------
    Q)
        batch_header Q "Complete Nacelle Pods L+R (81% scale — visual only)"
        slice "$OUT" 0.81 "15%" 0 "yes" \
            "${STL_NACELLES}/s_nacelle_port_revt.stl" \
            --support-material-buildplate-only
        slice "$OUT" 0.81 "15%" 0 "yes" \
            "${STL_NACELLES}/s_nacelle_stbd_revt.stl" \
            --support-material-buildplate-only
        ;;

    # -----------------------------------------------------------------------
    # BATCH VISUAL — Complete Aircraft Visual Reference — uniform 63% scale
    #
    # 63% is the tightest constraint (head_shell24 Y=235.1 mm → 148.1 mm).
    # Every external and internal-visible part sliced at exactly 63% so the
    # assembled reference model is geometrically consistent.
    #
    # Part list (22 print jobs — complete aircraft):
    #
    #   HULL SECTIONS (4 prints)
    #     head_shell24          129.4×235.1×140.7 → 81.5×148.1×88.6 mm
    #     middle_shell24        177.1×164.8×73.2  → 111.6×103.9×46.1 mm
    #     cargo_sect_shell24    194.7×203.6×163.2 → 122.7×128.3×102.8 mm
    #     rear_shell24          140.9×158.0×181.7 → 88.8×99.5×114.4 mm
    #
    #   NACELLE PODS — COMPLETE (2 prints, port + starboard)
    #     s_nacelle_port_revt     75.6×83.3×185.2   → 47.6×52.5×116.7 mm
    #     s_nacelle_stbd_revt     same
    #     nacelle_nozzle_closed_asm_repaired (×2)    62.0×62.0×19.5 → 39.1×39.1×12.3 mm
    #
    #   WINGS & LANDING GEAR (4 prints)
    #     wing_port_s1223_revo   85.7×161.0×~20 → 54.0×101.4×12.6 mm
    #     wing_stbd_s1223_revo   same
    #     legs_scaled24          96.1×150.1×7.5  → 60.6×94.6×4.7 mm  (raft)
    #     feet_x_4_scaled24      77.6×98.4×9.0   → 48.9×62.0×5.7 mm  (raft)
    #
    #   CARGO BAY (2 prints)
    #     cargo_door_port   108.0×33.7×87.0 → 68.0×21.2×54.8 mm
    #     cargo_door_stbd   108.0×38.2×84.6 → 68.0×24.1×53.3 mm
    #
    #   REAR EDF — COMPLETE (4 prints)
    #     s_middle_intake_shell24  177.1×164.8×73.2  → 111.6×103.9×46.1 mm
    #     edf_120_thrust_tube    134.0×134.0×167.0 → 84.4×84.4×105.2 mm
    #     edf_120_motor_mount    126.0×126.0×53.0  → 79.4×79.4×33.4 mm
    #     rear_nozzle_closed_asm   131.0×131.0×20.0  → 82.5×82.5×12.6 mm
    #
    #   VISUAL DETAILS (4 prints)
    #     dorsal_antenna_fin     20.0×4.0×35.0  → 12.6×2.5×22.1 mm  (raft)
    #     nacelle_tip_cap_port   80.0×80.0×8.0  → 50.4×50.4×5.0 mm  (raft)
    #     nacelle_tip_cap_stbd   same
    #     hull_engine_bell       76.0×76.0×50.0 → 47.9×47.9×31.5 mm
    #
    # Note: cockpit_dome_clear.stl is an open-surface mesh (no bottom face) that
    # crashes slic3r 1.3.0.  Print as a separate clear-resin SLA part or add a
    # base plane in CAD before slicing.
    # -----------------------------------------------------------------------
    VISUAL)
        local SCALE="0.63"
        local INFILL="15%"
        batch_header VISUAL "Complete Aircraft Visual Reference (63% uniform scale — 22 print jobs)"

        # ---- HULL SECTIONS ------------------------------------------------
        slice "$OUT" "$SCALE" "$INFILL" 0 "yes" \
            "${STL_FUSELAGE}/head_shell24.stl" \
            --support-material-buildplate-only

        slice "$OUT" "$SCALE" "$INFILL" 0 "yes" \
            "${STL_FUSELAGE}/middle_shell24.stl" \
            --support-material-buildplate-only

        slice "$OUT" "$SCALE" "$INFILL" 0 "yes" \
            "${STL_CARGO_BAY}/cargo_sect_shell24.stl" \
            --support-material-buildplate-only

        slice "$OUT" "$SCALE" "$INFILL" 0 "yes" \
            "${STL_AFT_EDF}/rear_shell24.stl" \
            --support-material-buildplate-only

        # ---- NACELLE PODS — COMPLETE (port + stbd) -------------------------
        # Rev T pods integrate EDF bore, stator hub, and spider mounts.
        # Replaces separate outer shell + stator shell prints.
        slice "$OUT" "$SCALE" "$INFILL" 0 "yes" \
            "${STL_NACELLES}/s_nacelle_port_revt.stl" \
            --support-material-buildplate-only

        slice "$OUT" "$SCALE" "$INFILL" 0 "yes" \
            "${STL_NACELLES}/s_nacelle_stbd_revt.stl" \
            --support-material-buildplate-only

        # ---- NACELLE NOZZLE ASSEMBLIES (×2 — one per nacelle) --------------
        slice "$OUT" "$SCALE" "$INFILL" 0 "no" \
            "${STL_NOZZLES}/nacelle_nozzle_closed_asm_repaired.stl" \
            --duplicate 2

        # ---- WINGS (port and starboard separately — S1223 airfoil) ---------
        slice "$OUT" "$SCALE" "$INFILL" 0 "no" \
            "${STL_WINGS}/wing_port_s1223_revo.stl"

        slice "$OUT" "$SCALE" "$INFILL" 0 "no" \
            "${STL_WINGS}/wing_stbd_s1223_revo.stl"

        # ---- LANDING GEAR --------------------------------------------------
        slice "$OUT" "$SCALE" "$INFILL" 1 "no" \
            "${STL_FUSELAGE}/legs_scaled24.stl"

        slice "$OUT" "$SCALE" "$INFILL" 1 "no" \
            "${STL_FUSELAGE}/feet_x_4_scaled24_repaired.stl"

        # ---- CARGO BAY DOORS -----------------------------------------------
        slice "$OUT" "$SCALE" "$INFILL" 0 "yes" \
            "${STL_CARGO_BAY}/cargo_door_port.stl" \
            --support-material-buildplate-only

        slice "$OUT" "$SCALE" "$INFILL" 0 "yes" \
            "${STL_CARGO_BAY}/cargo_door_stbd.stl" \
            --support-material-buildplate-only

        # ---- REAR EDF — COMPLETE -------------------------------------------
        slice "$OUT" "$SCALE" "$INFILL" 0 "yes" \
            "${STL_FUSELAGE}/s_middle_intake_shell24.stl" \
            --support-material-buildplate-only

        slice "$OUT" "$SCALE" "$INFILL" 0 "no" \
            "${STL_AFT_EDF}/edf_120_thrust_tube.stl"

        slice "$OUT" "$SCALE" "$INFILL" 0 "yes" \
            "${STL_AFT_EDF}/edf_120_motor_mount.stl" \
            --support-material-buildplate-only

        slice "$OUT" "$SCALE" "$INFILL" 0 "no" \
            "${STL_AFT_EDF}/rear_nozzle_closed_asm.stl"

        # ---- VISUAL DETAIL PARTS ------------------------------------------
        slice "$OUT" "$SCALE" "$INFILL" 1 "no" \
            "${STL_FUSELAGE}/dorsal_antenna_fin.stl"

        slice "$OUT" "$SCALE" "$INFILL" 1 "no" \
            "${STL_NACELLES}/nacelle_tip_cap_port.stl"

        slice "$OUT" "$SCALE" "$INFILL" 1 "no" \
            "${STL_NACELLES}/nacelle_tip_cap_stbd.stl"

        slice "$OUT" "$SCALE" "$INFILL" 0 "no" \
            "${STL_AFT_EDF}/hull_engine_bell.stl"
        ;;

    *)
        log "ERROR: Unknown batch '${batch}'. Valid: A B C D E F G1 G2 I J K L M N O P Q VISUAL"
        exit 1
        ;;
    esac
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
ALL_BATCHES=(A B C D E F G1 G2 I J K L M N O P Q VISUAL)

if [[ $# -eq 0 ]]; then
    log "Running all batches: ${ALL_BATCHES[*]}"
    for b in "${ALL_BATCHES[@]}"; do
        run_batch "$b"
    done
else
    for b in "$@"; do
        run_batch "$b"
    done
fi

log "=============================================="
log "Slicing complete."
log "G-code output: ${GCODE_ROOT}/"
log ""
log "To print via XYZware WiFi, run:"
log "  python3 ${GCODE_ROOT}/xyz_wrap.py <file.gcode>"
log "which produces <file.3w> for XYZware upload."
log "Or load .gcode directly if running Repetier firmware."
log "=============================================="
