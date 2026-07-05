# ============================================================
# Makefile — Serenity UAV airframe build pipeline
# airframe/FreeCAD-scripts/Makefile
#
# Compiles all OpenSCAD source files to STL, then runs the
# FreeCAD assembly script to produce the assembled .FCStd file.
#
# Usage (run from airframe/FreeCAD-scripts/):
#   make stls        — compile all SCAD files to STL
#   make assembly    — build STLs then run FreeCAD assembly
#   make clean-stls  — remove compiled STLs (NOT archived or existing STLs)
#   make help        — show this message
#
# Dependencies: openscad (2021.01+), /usr/bin/freecad (0.20+)
#
# Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
# License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
# ============================================================

# ---- Tool paths -----------------------------------------------
OPENSCAD := openscad
FREECAD  := /usr/bin/freecad

# ---- Directory layout (relative to this Makefile) -------------
ROOT     := $(patsubst %/,%,$(dir $(lastword $(MAKEFILE_LIST))))
AIRFRAME := $(ROOT)/..
SCAD     := $(AIRFRAME)/openscad
STLS     := $(AIRFRAME)/stls
SCRIPT   := $(ROOT)/serenity_assembly.py
OUTPUT   := $(AIRFRAME)/Serenity-Assembled.FCStd

# ---- OpenSCAD flags -------------------------------------------
# --hardwarnings: treat parameter warnings as errors
# --quiet: suppress progress spam on slow renders
SCAD_FLAGS := --hardwarnings

# ============================================================
# STL build targets
# Each SCAD source maps to one output STL in the stls/ tree.
# Wings use the RENDER_SIDE parameter to produce separate
# port (+1) and stbd (-1) halves.
# ============================================================

# -- Fuselage --------------------------------------------------
FUSELAGE_STLS := \
    $(STLS)/fuselage/rear_shell24.stl \
    $(STLS)/fuselage/battery_tray.stl   \
    $(STLS)/fuselage/belly_panel.stl

# -- Nacelles --------------------------------------------------
NACELLE_STLS := \
    $(STLS)/nacelles/nacelle_pod_50mm_tandem_simple.stl \
    $(STLS)/nacelles/nacelle_nozzle_straight.stl         \
    $(STLS)/nacelles/edf_stator_sleeve.stl               \
    $(STLS)/nacelles/edf_aft_spider_sleeve.stl           \
    $(STLS)/nacelles/nozzles/nacelle_bevel_housing.stl   \
    $(STLS)/nacelles/nozzles/nacelle_bevel_pair.stl      \
    $(STLS)/nacelles/nozzles/nacelle_nozzle_iris.stl     \
    $(STLS)/nacelles/nozzles/nacelle_nozzle_throat.stl   \
    $(STLS)/nacelles/nozzles/nacelle_nozzle_ring.stl     \
    $(STLS)/nacelles/nozzles/nacelle_nozzle_flap.stl     \
    $(STLS)/nacelles/nacelle_pinion.stl                  \
    $(STLS)/nacelles/nacelle_sector_gear.stl             \
    $(STLS)/nacelles/nozzles/nacelle_nozzle_idler.stl    \
    $(STLS)/nacelles/nozzles/nacelle_nozzle_idler_bracket.stl

# -- Wings -----------------------------------------------------
WING_STLS := \
    $(STLS)/wings/wing_port_s1223_revo.stl  \
    $(STLS)/wings/wing_stbd_s1223_revo.stl  \
    $(STLS)/wings/wing_nacelle_pylon_revo.stl

ALL_STLS := $(FUSELAGE_STLS) $(NACELLE_STLS) $(WING_STLS)

# ============================================================
# Default target
# ============================================================
.PHONY: all stls assembly clean-stls help
all: stls assembly

# ============================================================
# STL target — compile all SCAD files
# ============================================================
stls: $(ALL_STLS)

# ============================================================
# Assembly target — run FreeCAD headlessly
# ============================================================
assembly: stls
	@echo "[assembly] Building $(OUTPUT) ..."
	$(FREECAD) --background --python $(SCRIPT)
	@echo "[assembly] Done: $(OUTPUT)"

# ============================================================
# Fuselage rules
# ============================================================
$(STLS)/fuselage/rear_shell24.stl: \
        $(SCAD)/fuselage/rear_shell24.scad \
        $(AIRFRAME)/archive/stls/fuselage/rear_shell24_repaired.stl
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) \
	    $(SCAD)/fuselage/rear_shell24.scad \
	    -o $@
	@echo "[stl] $@"

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
# Nacelle rules
# ============================================================
$(STLS)/nacelles/nacelle_pod_50mm_tandem_simple.stl: \
        $(SCAD)/nacelles/nacelle_pod_50mm_tandem_simple.scad \
        $(AIRFRAME)/archive/stls/nacelles/s_eng_left_shell24_50mm_repaired.stl \
        $(AIRFRAME)/archive/stls/nacelles/s_eng_right_shell24_50mm_repaired.stl
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) \
	    $(SCAD)/nacelles/nacelle_pod_50mm_tandem_simple.scad \
	    -o $@
	@echo "[stl] $@"

$(STLS)/nacelles/nacelle_nozzle_straight.stl: \
        $(SCAD)/nacelles/nacelle_nozzle_straight.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) \
	    $(SCAD)/nacelles/nacelle_nozzle_straight.scad \
	    -o $@
	@echo "[stl] $@"

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

$(STLS)/nacelles/nacelle_pinion.stl: \
        $(SCAD)/nacelles/nacelle_pinion.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) \
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

$(STLS)/nacelles/nozzles/nacelle_nozzle_idler.stl: \
        $(SCAD)/nacelles/nacelle_nozzle_idler.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) \
	    -D 'RENDER_PART="gear"' \
	    $(SCAD)/nacelles/nacelle_nozzle_idler.scad \
	    -o $@
	@echo "[stl] $@"

$(STLS)/nacelles/nozzles/nacelle_nozzle_idler_bracket.stl: \
        $(SCAD)/nacelles/nacelle_nozzle_idler.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) \
	    -D 'RENDER_PART="bracket"' \
	    $(SCAD)/nacelles/nacelle_nozzle_idler.scad \
	    -o $@
	@echo "[stl] $@"

# ============================================================
# Wing rules
# Wings use the RENDER_SIDE parameter (-D flag):
#   +1 = port wing, -1 = stbd wing, 0 = both (preview only)
# ============================================================
$(STLS)/wings/wing_port_s1223_revo.stl: \
        $(SCAD)/wings/wings_s1223_revo.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) \
	    -D 'RENDER_SIDE=1' \
	    $(SCAD)/wings/wings_s1223_revo.scad \
	    -o $@
	@echo "[stl] $@"

$(STLS)/wings/wing_stbd_s1223_revo.stl: \
        $(SCAD)/wings/wings_s1223_revo.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) \
	    -D 'RENDER_SIDE=-1' \
	    $(SCAD)/wings/wings_s1223_revo.scad \
	    -o $@
	@echo "[stl] $@"

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
clean-stls:
	@echo "[clean] Removing compiled STLs ..."
	rm -f $(ALL_STLS)
	@echo "[clean] Done."

help:
	@echo "Serenity UAV airframe build pipeline"
	@echo ""
	@echo "Targets:"
	@echo "  all         Build STLs then run FreeCAD assembly (default)"
	@echo "  stls        Compile all SCAD files to STL"
	@echo "  assembly    Run FreeCAD headless assembly (requires stls)"
	@echo "  clean-stls  Remove compiled STLs"
	@echo "  help        Show this message"
	@echo ""
	@echo "Tools required:"
	@echo "  openscad (2021.01+)"
	@echo "  $(FREECAD)  (FreeCAD 0.20+ with Assembly4)"
