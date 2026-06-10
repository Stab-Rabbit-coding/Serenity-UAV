# CMakeLists.txt — Malcolm GCS PB2-I firmware
#
# Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
# License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
# Revision: Q1 (2026-06-10)
#
# Cross-compiles for AM6254 (aarch64) on a Linux x86_64 host, or builds
# natively when run directly on the PocketBeagle 2 Industrial.
#
# Usage (cross-compile from x86_64 host):
#   mkdir build && cd build
#   cmake -DCMAKE_TOOLCHAIN_FILE=../toolchain-aarch64.cmake ..
#   make -j$(nproc)
#
# Usage (native build on PB2-I):
#   mkdir build && cd build
#   cmake ..
#   make -j2
#
# Install:
#   sudo make install
#   sudo systemctl enable mal_comms mal_gimbal

cmake_minimum_required(VERSION 3.18)

project(
    malcolm_pb2i_firmware
    VERSION 0.1.0
    DESCRIPTION "Malcolm GCS PocketBeagle 2 Industrial firmware"
    LANGUAGES C
)

# ---------------------------------------------------------------------------
# C standard and compiler flags
# ---------------------------------------------------------------------------

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

# Strict warnings consistent with the project linting standards.
add_compile_options(
    -Wall
    -Wextra
    -Wpedantic
    -Wshadow
    -Wconversion
    -Wsign-conversion
    -Werror
    -fstack-protector-strong
    -D_FORTIFY_SOURCE=2
)

# ---------------------------------------------------------------------------
# MAVLink headers (header-only C library)
# ---------------------------------------------------------------------------

# MAVLINK_INCLUDE_DIR must point to the directory containing mavlink/common/mavlink.h.
# Set via: cmake -DMAVLINK_INCLUDE_DIR=/path/to/mavlink/headers ..
# Default: look for system-installed mavlink2 headers.
if(NOT DEFINED MAVLINK_INCLUDE_DIR)
    set(MAVLINK_INCLUDE_DIR "/usr/include/mavlink/v2.0" CACHE PATH
        "Path to MAVLink C header directory (parent of mavlink/)")
endif()

if(NOT EXISTS "${MAVLINK_INCLUDE_DIR}/mavlink/common/mavlink.h")
    message(FATAL_ERROR
        "MAVLink headers not found at ${MAVLINK_INCLUDE_DIR}/mavlink/common/mavlink.h\n"
        "Install with: sudo apt install pymavlink python3-mavlink\n"
        "or set -DMAVLINK_INCLUDE_DIR=<path>")
endif()

# ---------------------------------------------------------------------------
# Common include directories
# ---------------------------------------------------------------------------

include_directories(
    src
    ${MAVLINK_INCLUDE_DIR}
)

# ---------------------------------------------------------------------------
# mal_gimbal daemon
# ---------------------------------------------------------------------------

add_executable(mal_gimbal
    src/mal_gimbal.c
)

target_link_libraries(mal_gimbal PRIVATE m)

install(TARGETS mal_gimbal
    RUNTIME DESTINATION /usr/local/bin
)

# ---------------------------------------------------------------------------
# mal_telemetry library (shared between mal_comms and tests)
# ---------------------------------------------------------------------------

add_library(mal_telemetry_lib STATIC
    src/mal_telemetry.c
)

target_include_directories(mal_telemetry_lib PUBLIC src ${MAVLINK_INCLUDE_DIR})

# ---------------------------------------------------------------------------
# mal_comms daemon (Phase Malcolm-2 — stub; expand in Phase Malcolm-3)
# ---------------------------------------------------------------------------

# mal_comms.c is a Phase Malcolm-2 deliverable.  When created, add here:
# add_executable(mal_comms
#     src/mal_comms.c
# )
# target_link_libraries(mal_comms PRIVATE mal_telemetry_lib m)
# install(TARGETS mal_comms RUNTIME DESTINATION /usr/local/bin)
