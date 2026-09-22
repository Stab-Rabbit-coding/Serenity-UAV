##
## Makefile — Serenity UAV device tree overlay compilation
##
## Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
## License: CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0
##
## Target: PocketBeagle 2 Industrial (AM6254), BeagleBone Debian Trixie
## Requires: dtc ≥ 1.7.x (supports -@ for __symbols__ generation)
##
## Usage:
##   make              — compile both current overlays (cape-a2, TACCO2)
##   make install      — install .dtbo files to /boot/firmware/overlays/
##   make clean        — remove compiled .dtbo files
##
## Pilot/TACCO (Rev Q, non-EMI-hardened) are archived under Pilot/archive/
## and TACCO/archive/ — retired, not built by default.

DTC         := dtc
DTC_FLAGS   := -@ -I dts -O dtb -Wno-unit_address_vs_reg

OVERLAY_DIR := /boot/firmware/overlays

##Pilot: EMI-hardened sensor + flight control cape.
CAPE_A2_DTS  := Pilot/k3-am6254-pocketbeagle2-serenity-Pilot2.dts
CAPE_A2_DTBO := Pilot/k3-am6254-pocketbeagle2-serenity-Pilot2.dtbo

## TACCO (XO): EMI-hardened comms + logging + payload cape.
CAPE_B2_DTS  := TACCO/k3-am6254-pocketbeagle2-serenity-cape-b2.dts
CAPE_B2_DTBO := TACCO/k3-am6254-pocketbeagle2-serenity-cape-b2.dtbo

ALL_DTBO    := $(CAPE_A2_DTBO) $(CAPE_B2_DTBO)

## Default target — build all overlays.
.PHONY: all
all: $(ALL_DTBO)

## Compile Pilot overlay (EMI-hardened, Pilot).
$(CAPE_A2_DTBO): $(CAPE_A2_DTS)
	$(DTC) $(DTC_FLAGS) -o $@ $<

## Compile TACCO overlay (EMI-hardened, XO).
$(CAPE_B2_DTBO): $(CAPE_B2_DTS)
	$(DTC) $(DTC_FLAGS) -o $@ $<

## Install compiled overlays to the boot partition.
## Requires root (sudo make install).
.PHONY: install
install: $(ALL_DTBO)
	install -d $(OVERLAY_DIR)
	install -m 0644 $(CAPE_A2_DTBO) $(OVERLAY_DIR)/
	install -m 0644 $(CAPE_B2_DTBO) $(OVERLAY_DIR)/
	@echo ""
	@echo "Overlays installed.  Add the appropriate line to"
	@echo "/boot/firmware/extlinux/extlinux.conf under your LABEL stanza:"
	@echo ""
	@echo "  FC nodes (Pilot): fdtoverlays /overlays/k3-am6254-pocketbeagle2-serenity-Pilot2.dtbo"
	@echo "  CN nodes (XO):    fdtoverlays /overlays/k3-am6254-pocketbeagle2-serenity-cape-b2.dtbo"

## Remove compiled output.
.PHONY: clean
clean:
	rm -f $(ALL_DTBO)
