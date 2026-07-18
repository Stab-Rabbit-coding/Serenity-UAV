#!/usr/bin/env bash
# install_mavlink_router.sh — Build and install mavlink-router from source
#
# Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
# License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
# Revision: Q1 (2026-06-10)
#
# Run as root:
#   sudo bash install_mavlink_router.sh
#
# What this does:
#   1. Installs build dependencies (meson, ninja, python3-gi).
#   2. Clones mavlink-router from GitHub (Intel's fork — most maintained).
#   3. Builds and installs mavlink-router to /usr/local/bin/.
#   4. Installs the Malcolm GCS mavlink-router configuration.
#   5. Creates a systemd service for automatic startup.
#
# mavlink-router reference:
#   https://github.com/mavlink-router/mavlink-router

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_SRC="${SCRIPT_DIR}/../config/mavlink_router.conf"
CONFIG_DEST="/etc/mavlink-router/main.conf"
BUILD_DIR="/tmp/mavlink-router-build"
MAVLINK_ROUTER_REPO="https://github.com/mavlink-router/mavlink-router.git"

# ---------------------------------------------------------------------------
# Build dependencies
# ---------------------------------------------------------------------------

echo "[install_mavlink_router] Installing build dependencies..."
apt-get install -y --no-install-recommends \
    meson \
    ninja-build \
    python3-gi \
    libglib2.0-dev \
    pkg-config

# ---------------------------------------------------------------------------
# Clone and build
# ---------------------------------------------------------------------------

echo "[install_mavlink_router] Cloning mavlink-router..."
rm -rf "${BUILD_DIR}"
git clone --depth=1 "${MAVLINK_ROUTER_REPO}" "${BUILD_DIR}"
cd "${BUILD_DIR}"
git submodule update --init --recursive

echo "[install_mavlink_router] Building mavlink-router..."
meson setup build -Dsystemd=true
ninja -C build
ninja -C build install

echo "[install_mavlink_router] mavlink-router installed at: $(which mavlink-routerd)"

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

echo "[install_mavlink_router] Installing configuration..."
mkdir -p /etc/mavlink-router

if [ -f "${CONFIG_SRC}" ]; then
    cp "${CONFIG_SRC}" "${CONFIG_DEST}"
    echo "[install_mavlink_router] Config installed at: ${CONFIG_DEST}"
else
    echo "[install_mavlink_router] WARNING: Config source not found at ${CONFIG_SRC}"
    echo "[install_mavlink_router] Manually install config to ${CONFIG_DEST}"
fi

# ---------------------------------------------------------------------------
# systemd service
# ---------------------------------------------------------------------------

SYSTEMD_SERVICE='/etc/systemd/system/mavlink-router.service'

cat >"${SYSTEMD_SERVICE}" <<'EOF'
[Unit]
Description=Malcolm GCS mavlink-router
Documentation=https://github.com/mavlink-router/mavlink-router
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/mavlink-routerd -c /etc/mavlink-router/main.conf
Restart=on-failure
RestartSec=5s
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable mavlink-router.service
echo "[install_mavlink_router] systemd service installed and enabled."
echo "[install_mavlink_router] Start with: sudo systemctl start mavlink-router"
echo "[install_mavlink_router] Status:     sudo systemctl status mavlink-router"
echo "[install_mavlink_router] Done."
