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
# License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
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
OUTPUT   := $(AIRFRAME)/freecad/assembly/SerenityAssembly.FCStd

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

# -- Nacelle (Rev U: the 64 mm nacelle; part-local prints, handed by PYLON_SIDE / NZ_SIDE) --
# The 50 mm sleeve, spider, trunnion, iris and ESC-cover rules were removed with the 50 mm
# sources (frozen in archives/rev-T-frozen.tar.gz).  The 64 mm ESC bay covers are not built
# here: they wait on the 80 A ESC part selection (WBS NAC-64-ESC-80A), and
# tools/check_nacelle_deps.py lists them as NOT PUBLISHED.  Pods and trunnions are baked
# elsewhere (tools/bake_hull_frame.py).
NACELLE_STLS := \
    $(STLS)/nacelles/edf_motor_mount_64mm_stage2_stbd.stl \
    $(STLS)/nacelles/edf_motor_mount_64mm_stage2_port.stl \
    $(STLS)/nacelles/nozzles/nacelle_nozzle_throat_64mm_stbd.stl \
    $(STLS)/nacelles/nozzles/nacelle_nozzle_throat_64mm_port.stl \
    $(STLS)/nacelles/nozzles/nacelle_nozzle_ring_64mm_stbd.stl \
    $(STLS)/nacelles/nozzles/nacelle_nozzle_ring_64mm_port.stl \
    $(STLS)/nacelles/nozzles/nacelle_nozzle_flap_64mm.stl \
    $(STLS)/nacelles/nozzles/nacelle_nozzle_flap_seal_64mm.stl

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
# Nacelle mechanism rules (64 mm)
# ============================================================
NAC=$(SCAD)/nacelles

$(STLS)/nacelles/edf_motor_mount_64mm_stage2_stbd.stl: $(NAC)/edf_motor_mount_64mm.scad $(NAC)/nacelle_64_scale.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) -D PYLON_SIDE=1 $(NAC)/edf_motor_mount_64mm.scad -o $@
	@echo "[stl] $@"

$(STLS)/nacelles/edf_motor_mount_64mm_stage2_port.stl: $(NAC)/edf_motor_mount_64mm.scad $(NAC)/nacelle_64_scale.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) -D PYLON_SIDE=-1 $(NAC)/edf_motor_mount_64mm.scad -o $@
	@echo "[stl] $@"

# Throat and ring are handed (NZ_SIDE +1 starboard, -1 port: the ring lever azimuth and the
# housing stop pocket mirror).  The flaps are common to both nozzles: 4 master + 4 seal per
# nacelle, the seal lapped 0.2 mm radially outboard of the master.
$(STLS)/nacelles/nozzles/nacelle_nozzle_throat_64mm_stbd.stl: $(NAC)/nacelle_nozzle_iris_64mm.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) -D 'NZ_PART="throat"' -D NZ_SIDE=1 $(NAC)/nacelle_nozzle_iris_64mm.scad -o $@
	@echo "[stl] $@"

$(STLS)/nacelles/nozzles/nacelle_nozzle_throat_64mm_port.stl: $(NAC)/nacelle_nozzle_iris_64mm.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) -D 'NZ_PART="throat"' -D NZ_SIDE=-1 $(NAC)/nacelle_nozzle_iris_64mm.scad -o $@
	@echo "[stl] $@"

$(STLS)/nacelles/nozzles/nacelle_nozzle_ring_64mm_stbd.stl: $(NAC)/nacelle_nozzle_iris_64mm.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) -D 'NZ_PART="ring"' -D NZ_SIDE=1 $(NAC)/nacelle_nozzle_iris_64mm.scad -o $@
	@echo "[stl] $@"

$(STLS)/nacelles/nozzles/nacelle_nozzle_ring_64mm_port.stl: $(NAC)/nacelle_nozzle_iris_64mm.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) -D 'NZ_PART="ring"' -D NZ_SIDE=-1 $(NAC)/nacelle_nozzle_iris_64mm.scad -o $@
	@echo "[stl] $@"

$(STLS)/nacelles/nozzles/nacelle_nozzle_flap_64mm.stl: $(NAC)/nacelle_nozzle_iris_64mm.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) -D 'NZ_PART="flap"' $(NAC)/nacelle_nozzle_iris_64mm.scad -o $@
	@echo "[stl] $@"

$(STLS)/nacelles/nozzles/nacelle_nozzle_flap_seal_64mm.stl: $(NAC)/nacelle_nozzle_iris_64mm.scad
	@mkdir -p $(dir $@)
	$(OPENSCAD) $(SCAD_FLAGS) -D 'NZ_PART="flap_seal"' $(NAC)/nacelle_nozzle_iris_64mm.scad -o $@
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
