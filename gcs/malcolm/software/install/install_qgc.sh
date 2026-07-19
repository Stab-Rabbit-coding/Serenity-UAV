#!/usr/bin/env bash
# install_qgc.sh — Install QGroundControl on Debian Linux (AppImage method)
#
# Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
# License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
# Revision: Q1 (2026-06-10)
#
# Run as non-root (installs to ~/Applications/):
#   bash install_qgc.sh
#
# What this does:
#   1. Downloads the latest stable QGroundControl AppImage from the
#      official QGroundControl GitHub releases page.
#   2. Installs it to ~/Applications/QGroundControl.AppImage.
#   3. Creates a desktop entry for the application menu.
#   4. Configures USB rules for MAVLink over serial.
#
# QGroundControl version selection:
#   QGC supports both ArduPilot and PX4.  Malcolm uses QGC with ArduPilot
#   flight stack firmware on the aircraft.  The stable release is preferred
#   over daily builds for operational use.
#
# Reference: https://docs.qgroundcontrol.com/master/en/getting_started/download_and_install.html

set -euo pipefail

QGC_INSTALL_DIR="${HOME}/Applications"
QGC_APPIMAGE="${QGC_INSTALL_DIR}/QGroundControl.AppImage"

# ---------------------------------------------------------------------------
# QGC AppImage download
# ---------------------------------------------------------------------------
# NOTE: Update this URL to the current stable release when upgrading.
# Check https://github.com/mavlink/qgroundcontrol/releases for the latest.
QGC_URL="https://d176tv9ibo4jno.cloudfront.net/latest/QGroundControl.AppImage"

echo "[install_qgc] Creating install directory: ${QGC_INSTALL_DIR}"
mkdir -p "${QGC_INSTALL_DIR}"

echo "[install_qgc] Downloading QGroundControl AppImage..."
echo "[install_qgc] URL: ${QGC_URL}"
curl -L --progress-bar -o "${QGC_APPIMAGE}" "${QGC_URL}"

chmod +x "${QGC_APPIMAGE}"
echo "[install_qgc] QGroundControl installed at: ${QGC_APPIMAGE}"

# ---------------------------------------------------------------------------
# USB serial rules (allows QGC to access /dev/ttyUSB* without sudo)
# ---------------------------------------------------------------------------

UDEV_RULE='/etc/udev/rules.d/99-mavlink-usb.rules'

if [ "$(id -u)" -eq 0 ]; then
    if [ ! -f "${UDEV_RULE}" ]; then
        cat >"${UDEV_RULE}" <<'EOF'
# Malcolm GCS — MAVLink USB serial device access rules
# Allows non-root access to common USB serial adapters used with SiK radios.
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", MODE="0666"   # Silicon Labs CP2102
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", MODE="0666"   # FTDI
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", MODE="0666"   # CH340
EOF
        udevadm control --reload-rules
        udevadm trigger
        echo "[install_qgc] USB serial udev rules installed."
    fi
else
    echo "[install_qgc] Not running as root — USB serial udev rules not installed."
    echo "[install_qgc] Run: sudo bash install_qgc.sh  to install udev rules."
fi

# ---------------------------------------------------------------------------
# Desktop entry (non-root)
# ---------------------------------------------------------------------------

DESKTOP_DIR="${HOME}/.local/share/applications"
DESKTOP_FILE="${DESKTOP_DIR}/qgroundcontrol.desktop"

mkdir -p "${DESKTOP_DIR}"
cat >"${DESKTOP_FILE}" <<EOF
[Desktop Entry]
Name=QGroundControl
Comment=UAV Ground Control Station
Exec=${QGC_APPIMAGE}
Icon=qgroundcontrol
Type=Application
Categories=Science;Engineering;
EOF

echo "[install_qgc] Desktop entry created at: ${DESKTOP_FILE}"
echo "[install_qgc] Launch QGC with: ${QGC_APPIMAGE}"
echo "[install_qgc] Configure QGC: Comm Links > Add > UDP > port 14550 (mavlink-router output)"
echo "[install_qgc] Done.  Next: sudo bash install_mavlink_router.sh"
