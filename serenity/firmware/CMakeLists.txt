##
## CMakeLists.txt — Serenity UAV Firmware top-level build
##
## Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
## License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
##
## Target platform: PocketBeagle 2 Industrial (TI AM6254, aarch64 Linux)
## Build system:    CMake 3.18+
##
cmake_minimum_required(VERSION 3.18)
project(SerenityFirmware C)

## ---------------------------------------------------------------------------
## Build options
## ---------------------------------------------------------------------------
option(NATIVE_BUILD "Build for host architecture (unit-test use only)" OFF)

## ---------------------------------------------------------------------------
## Language standard — C17 with POSIX.1-2017 extensions
## ---------------------------------------------------------------------------
set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

## ---------------------------------------------------------------------------
## Warning flags — treat all warnings as errors to enforce coding standards
## ---------------------------------------------------------------------------
add_compile_options(
    -Wall
    -Wextra
    -Wpedantic
    -Wconversion
    -Wshadow
    -Wformat=2
    -Werror
)

## ---------------------------------------------------------------------------
## Preprocessor defines
## ---------------------------------------------------------------------------
## _GNU_SOURCE needed for POSIX extensions used by termios, gpiod, i2c-dev
add_compile_definitions(_GNU_SOURCE)

## ---------------------------------------------------------------------------
## Shared include paths
## ---------------------------------------------------------------------------
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/common/include)

## ---------------------------------------------------------------------------
## Sub-projects
## ---------------------------------------------------------------------------
add_subdirectory(cn)
add_subdirectory(fc)
