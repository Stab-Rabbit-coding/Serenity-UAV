# ============================================================
# Makefile — Serenity UAV airframe build pipeline
# airframe/FreeCAD-scripts/Makefile
#
# Runs the headless FreeCAD assembly, and (optionally) compiles the
# SCAD-sourced nacelle-mechanism / wing / accessory parts to STL.
#
# Usage (run from airframe/FreeCAD-scripts/):
#   make assembly    — run the FreeCAD assembly on the existing STLs (default)
#   make stls        — compile the SCAD-sourced parts to STL
#   make all         — build those STLs, then run the assembly
#   make clean-stls  — remove the SCAD-compiled STLs (see WARNING below)
#   make help        — show this message
#
# IMPORTANT — what this Makefile does and does NOT build:
#   The four PRIMARY fuselage shells (head/cargo/middle/rear
#   *_2mm_repaired.stl), the baked nacelle pods (nacelle_*_revs.stl) and
#   the baked wings are NOT produced here — they come from the Blender
#   hollowing pipeline + interior-merge scripts + the hull-frame bake:
#     - airframe/blender-scripts/  (hollowing sources)
#     - airframe/blender-scripts/merge_cargo_interior.py   (cargo)
#     - airframe/blender-scripts/regen_rear_interior.py    (rear)
#     - airframe/blender-scripts/add_structural_features.py (head/middle)
#     - tools/bake_hull_frame.py   (bake to hull frame)
#   The `assembly` target therefore CONSUMES the STLs already present in
#   airframe/stls/ and does NOT depend on `stls`; run those pipelines first
#   if a primary shell needs regenerating.  The `stls` target here only
#   (re)builds the SCAD-sourced nacelle-mechanism, wing and accessory parts
#   the assembly also imports.
#
# Dependencies: openscad (2021.01+), freecadcmd (FreeCAD 1.0+)
#   Run the assembly with the freecadcmd CONSOLE binary — not
#   `freecad --background --python`, whose GUI event loop may not exit
#   cleanly in a headless/CI context.  (The GUI "Execute macro" path works
#   too; freecadcmd is the scriptable equivalent.)
#
# Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
# License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
# ============================================================

# ---- Tool paths -----------------------------------------------
OPENSCAD  := openscad
FREECADCMD := freecadcmd

# ---- Directory layout (relative to this Makefile) -------------
ROOT     := $(patsubst %/,%,$(dir $(lastword $(MAKEFILE_LIST))))
AIRFRAME := $(ROOT)/..
SCAD     := $(AIRFRAME)/openscad
STLS     := $(AIRFRAME)/stls
SCRIPT   := $(ROOT)/serenity_assembly.py
OUTPUT   := $(AIRFRAME)/Serenity-Assembled.FCStd

# ---- OpenSCAD flags -------------------------------------------
# --hardwarnings: treat parameter warnings as errors
SCAD_FLAGS := --hardwarnings

# ============================================================
# STL build targets — SCAD-sourced parts the assembly imports.
# (Primary shells / baked nacelles / baked wings are built by the
# Blender + bake pipeline, not here — see header.)
# ============================================================

# -- Fuselage accessories (SCAD-sourced) -----------------------
FUSELAGE_STLS := \
    $(STLS)/fuselage/battery_tray.stl \
    $(STLS)/fuselage/belly_panel.stl

# -- Nacelle mechanism parts (SCAD-sourced; imported by the
#    assembly's nacelle_rows() sub-component placements) --------
NACELLE_STLS := \
    $(STLS)/nacelles/edf_stator_sleeve.stl               \
    $(STLS)/nacelles/edf_aft_spider_sleeve.stl           \
    $(STLS)/nacelles/nozzles/nacelle_bevel_housing.stl   \
    $(STLS)/nacelles/nozzles/nacelle_bevel_pair.stl      \
    $(STLS)/nacelles/nozzles/nacelle_nozzle_iris.stl     \
    $(STLS)/nacelles/nozzles/nacelle_nozzle_throat.stl   \
    $(STLS)/nacelles/nozzles/nacelle_nozzle_ring.stl     \
    $(STLS)/nacelles/nozzles/nacelle_nozzle_flap.stl     \
    $(STLS)/nacelles/nacelle_pinion_a.stl                \
    $(STLS)/nacelles/nacelle_drive_pinion.stl            \
    $(STLS)/nacelles/nacelle_sector_gear.stl

# -- Wings (SCAD-sourced part-local prints; the port/stbd wing
#    shells the ASSEMBLY uses are baked elsewhere) --------------
WING_STLS := \
    $(STLS)/wings/wing_nacelle_pylon_revo.stl

ALL_STLS := $(FUSELAGE_STLS) $(NACELLE_STLS) $(WING_STLS)

# ============================================================
# Phony targets
# ============================================================
.PHONY: all stls assembly clean-stls help

# Default: run the assembly on the existing STLs.
all: stls assembly

# ============================================================
# STL target — compile the SCAD-sourced parts above
# ============================================================
stls: $(ALL_STLS)

# ============================================================
# Assembly target — run FreeCAD headlessly on the existing STLs.
# Intentionally does NOT depend on `stls`: the primary shells the
# assembly needs are produced by the Blender + bake pipeline, not
# this Makefile (see header).  Run `make stls` first if you want the
# SCAD-sourced mechanism parts rebuilt beforehand, or `make all`.
# ============================================================
assembly:
	@echo "[assembly] Building $(OUTPUT) with freecadcmd ..."
	$(FREECADCMD) $(SCRIPT)
	@echo "[assembly] Done: $(OUTPUT)"

# ============================================================
# Fuselage accessory rules
# ============================================================
$(STLS)/fuselage/battery_tray.stl: \
        $(SCAD)/fuselage/battery_tray.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) \
	    $(SCAD)/fuselage/battery_tray.scad \
	    -o $@
	@echo "[stl] $@"

$(STLS)/fuselage/belly_panel.stl: \
        $(SCAD)/fuselage/belly_panel.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) \
	    $(SCAD)/fuselage/belly_panel.scad \
	    -o $@
	@echo "[stl] $@"

# ============================================================
# Nacelle mechanism rules
# ============================================================
$(STLS)/nacelles/edf_stator_sleeve.stl: \
        $(SCAD)/nacelles/edf_stator_sleeve.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) \
	    $(SCAD)/nacelles/edf_stator_sleeve.scad \
	    -o $@
	@echo "[stl] $@"

$(STLS)/nacelles/edf_aft_spider_sleeve.stl: \
        $(SCAD)/nacelles/edf_aft_spider_sleeve.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) \
	    $(SCAD)/nacelles/edf_aft_spider_sleeve.scad \
	    -o $@
	@echo "[stl] $@"

$(STLS)/nacelles/nozzles/nacelle_bevel_housing.stl: \
        $(SCAD)/nacelles/nacelle_bevel_housing.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) \
	    $(SCAD)/nacelles/nacelle_bevel_housing.scad \
	    -o $@
	@echo "[stl] $@"

$(STLS)/nacelles/nozzles/nacelle_bevel_pair.stl: \
        $(SCAD)/nacelles/nacelle_bevel_pair.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) \
	    $(SCAD)/nacelles/nacelle_bevel_pair.scad \
	    -o $@
	@echo "[stl] $@"

$(STLS)/nacelles/nozzles/nacelle_nozzle_iris.stl: \
        $(SCAD)/nacelles/nacelle_nozzle_iris.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) \
	    $(SCAD)/nacelles/nacelle_nozzle_iris.scad \
	    -o $@
	@echo "[stl] $@"

# Nozzle print-ready parts pulled from the same iris file via RENDER_PART
# (throat-and-housing, unison ring, and one flap — printed × 8).
$(STLS)/nacelles/nozzles/nacelle_nozzle_throat.stl: \
        $(SCAD)/nacelles/nacelle_nozzle_iris.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) \
	    -D 'RENDER_PART="throat"' \
	    $(SCAD)/nacelles/nacelle_nozzle_iris.scad \
	    -o $@
	@echo "[stl] $@"

$(STLS)/nacelles/nozzles/nacelle_nozzle_ring.stl: \
        $(SCAD)/nacelles/nacelle_nozzle_iris.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) \
	    -D 'RENDER_PART="ring"' \
	    $(SCAD)/nacelles/nacelle_nozzle_iris.scad \
	    -o $@
	@echo "[stl] $@"

$(STLS)/nacelles/nozzles/nacelle_nozzle_flap.stl: \
        $(SCAD)/nacelles/nacelle_nozzle_iris.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) \
	    -D 'RENDER_PART="flap"' \
	    $(SCAD)/nacelles/nacelle_nozzle_iris.scad \
	    -o $@
	@echo "[stl] $@"

# Rev S1 (2026-07-07): the two pinions are variant builds of one SCAD
# (PINION_VARIANT) — Pinion A (M1 17T) and the Nozzle Drive Pinion (M0.5
# 14T, replaces the Crown Pinion; the compound idler is deleted/archived).
$(STLS)/nacelles/nacelle_pinion_a.stl: \
        $(SCAD)/nacelles/nacelle_pinion.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) \
	    -D 'PINION_VARIANT="A"' \
	    $(SCAD)/nacelles/nacelle_pinion.scad \
	    -o $@
	@echo "[stl] $@"

$(STLS)/nacelles/nacelle_drive_pinion.stl: \
        $(SCAD)/nacelles/nacelle_pinion.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) \
	    -D 'PINION_VARIANT="DRIVE"' \
	    $(SCAD)/nacelles/nacelle_pinion.scad \
	    -o $@
	@echo "[stl] $@"

$(STLS)/nacelles/nacelle_sector_gear.stl: \
        $(SCAD)/nacelles/nacelle_sector_gear.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) \
	    $(SCAD)/nacelles/nacelle_sector_gear.scad \
	    -o $@
	@echo "[stl] $@"

# ============================================================
# Wing rules
# ============================================================
$(STLS)/wings/wing_nacelle_pylon_revo.stl: \
        $(SCAD)/wings/wing_nacelle_pylon_revo.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) \
	    $(SCAD)/wings/wing_nacelle_pylon_revo.scad \
	    -o $@
	@echo "[stl] $@"

# ============================================================
# Utility targets
# ============================================================
# WARNING: clean-stls removes ONLY the SCAD-compiled parts listed in
# ALL_STLS.  It does NOT touch the Blender/bake-pipeline primary shells,
# baked nacelles or baked wings (those are not in ALL_STLS).
clean-stls:
	@echo "[clean] Removing SCAD-compiled STLs ..."
	rm -f $(ALL_STLS)
	@echo "[clean] Done."

help:
	@echo "Serenity UAV airframe build pipeline"
	@echo ""
	@echo "Targets:"
	@echo "  assembly    Run FreeCAD headless assembly on existing STLs (freecadcmd)"
	@echo "  stls        Compile the SCAD-sourced mechanism/wing/accessory parts"
	@echo "  all         Build those STLs, then run the assembly"
	@echo "  clean-stls  Remove the SCAD-compiled STLs (not the baked shells)"
	@echo "  help        Show this message"
	@echo ""
	@echo "Primary fuselage shells + baked nacelles/wings come from the"
	@echo "Blender + bake pipeline (see the header of this Makefile), not here."
	@echo ""
	@echo "Tools required:"
	@echo "  openscad (2021.01+)"
	@echo "  freecadcmd (FreeCAD 1.0+)"
