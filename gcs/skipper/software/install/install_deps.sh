#!/usr/bin/env bash
# install_deps.sh — Install Skipper GCS host PC dependencies (Debian bookworm)
#
# Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
# License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
# Revision: Q1 (2026-06-10)
#
# Run as root:
#   sudo bash install_deps.sh
#
# What this does:
#   1. Updates apt package lists.
#   2. Installs Python 3.11+, pip, git, cmake, build tools.
#   3. Installs Python tracking software dependencies (pymavlink, pyserial, pyyaml).
#   4. Installs iw, wpasupplicant (for WiFi Tx power configuration).
#   5. Creates the /etc/udev/rules.d/99-gnss-gcs.rules symlink for the GCS GNSS receiver.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRACKING_DIR="${SCRIPT_DIR}/../tracking"

# ---------------------------------------------------------------------------
# 1. System packages
# ---------------------------------------------------------------------------

echo "[install_deps] Updating apt package list..."
apt-get update -qq

echo "[install_deps] Installing system packages..."
apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    git \
    cmake \
    ninja-build \
    build-essential \
    iw \
    wpasupplicant \
    screen \
    htop \
    usbutils \
    can-utils \
    minicom

# ---------------------------------------------------------------------------
# 2. Python tracking dependencies
# ---------------------------------------------------------------------------

echo "[install_deps] Installing Python tracking dependencies..."
pip3 install --break-system-packages -r "${TRACKING_DIR}/requirements.txt"

# ---------------------------------------------------------------------------
# 3. udev rule for GCS GNSS receiver (u-blox USB)
# ---------------------------------------------------------------------------

UDEV_RULE='/etc/udev/rules.d/99-gnss-gcs.rules'

if [ ! -f "${UDEV_RULE}" ]; then
    echo "[install_deps] Installing udev rule for GCS GNSS receiver..."
    cat >"${UDEV_RULE}" <<'EOF'
# Skipper GCS — u-blox GNSS receiver symlink
# u-blox USB Vendor ID: 0x1546
SUBSYSTEM=="tty", ATTRS{idVendor}=="1546", SYMLINK+="gnss_gcs", MODE="0666"
EOF
    udevadm control --reload-rules
    udevadm trigger
    echo "[install_deps] udev rule installed at ${UDEV_RULE}"
else
    echo "[install_deps] udev rule already exists — skipping."
fi

echo "[install_deps] Done.  Next: sudo bash install_qgc.sh"
