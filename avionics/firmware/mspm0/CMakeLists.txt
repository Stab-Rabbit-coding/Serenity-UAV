##
## CMakeLists.txt — Serenity UAV MSPM0G3507 trust-node firmware
##
## Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
## Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
## License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
##
## One template, three boards.  Select with:
##
##   cmake -B build -DSERENITY_BOARD=can_periph_gw -DSERENITY_HAL=sim
##   cmake -B build -DSERENITY_BOARD=jayne -DSERENITY_HAL=mspm0 \
##         -DCMAKE_TOOLCHAIN_FILE=cmake/arm-none-eabi.cmake
##
## This is a separate CMake project from `avionics/firmware/`, which builds
## aarch64 Linux daemons for the PocketBeagle nodes.  Two toolchains, two
## projects; they are not subdirectories of one another.
##
cmake_minimum_required(VERSION 3.18)
project(SerenityMSPM0 C)

set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

## ---------------------------------------------------------------------------
## Options
## ---------------------------------------------------------------------------
set(SERENITY_BOARD "can_periph_gw" CACHE STRING
    "Board to build: can_periph_gw | jayne | kaylee")
set_property(CACHE SERENITY_BOARD PROPERTY STRINGS
    can_periph_gw jayne kaylee)

set(SERENITY_HAL "sim" CACHE STRING "HAL port: mspm0 | sim")
set_property(CACHE SERENITY_HAL PROPERTY STRINGS mspm0 sim)

## Gateway build variants — see boards/can_periph_gw/board_config.h
set(GW_STACK_INDEX "1" CACHE STRING "CAN-PERIPH-GW stack index, 1..4")
set(GW_ROLE "1" CACHE STRING "Gateway role: 1=encoder 2=esc 3=servo")

## Jayne install site — see boards/jayne/board_config.h
set(JAYNE_SITE "1" CACHE STRING "Jayne site: 1=nose 2=cargo")

if(NOT EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/boards/${SERENITY_BOARD}")
    message(FATAL_ERROR "Unknown SERENITY_BOARD '${SERENITY_BOARD}'")
endif()

## ---------------------------------------------------------------------------
## Warning flags
##
## Warnings are errors.  This firmware signs flight-critical telemetry; a
## conversion or shadowing warning in the marshalling code is exactly the
## class of defect that produces a valid-looking but wrong MAC.
## ---------------------------------------------------------------------------
add_compile_options(
    -Wall -Wextra -Wpedantic -Wconversion -Wshadow -Wformat=2
    -Wstrict-prototypes -Wmissing-prototypes -Wundef -Wcast-qual
    -Werror
)

## ---------------------------------------------------------------------------
## Micro XRCE-DDS Client (Apache-2.0, eProsima) — vendored, unmodified
## ---------------------------------------------------------------------------
set(SERENITY_UXR_MTU 63 CACHE STRING
    "XRCE transport MTU; must equal SER_LINK_MTU in serenity/link.h")
include(cmake/uxrclient.cmake)

## ---------------------------------------------------------------------------
## Firmware target
## ---------------------------------------------------------------------------
set(TEMPLATE_SRC
    template/src/main.c
    template/src/node.c
    template/src/link.c
    template/src/sec_envelope.c
    template/src/sha256.c
    template/src/tpm2.c
    template/src/tpm_tis.c
)

set(BOARD_SRC
    boards/${SERENITY_BOARD}/board.c
    boards/${SERENITY_BOARD}/app.c
)

if(SERENITY_HAL STREQUAL "mspm0")
    set(HAL_SRC hal/mspm0/hal_mspm0.c hal/mspm0/syscalls.c)
else()
    set(HAL_SRC hal/sim/hal_sim.c)
endif()

add_executable(serenity-node ${TEMPLATE_SRC} ${BOARD_SRC} ${HAL_SRC})

target_include_directories(serenity-node PRIVATE
    template/include
    boards/${SERENITY_BOARD}
)

target_compile_definitions(serenity-node PRIVATE
    GW_STACK_INDEX=${GW_STACK_INDEX}
    GW_ROLE=${GW_ROLE}
    JAYNE_SITE=${JAYNE_SITE}
)

target_link_libraries(serenity-node PRIVATE uxrclient)

if(SERENITY_HAL STREQUAL "mspm0")
    target_link_options(serenity-node PRIVATE
        -T${CMAKE_CURRENT_SOURCE_DIR}/cmake/mspm0g3507.ld
        -Wl,--gc-sections -Wl,-Map=serenity-node.map --specs=nano.specs)
    add_custom_command(TARGET serenity-node POST_BUILD
        COMMAND ${CMAKE_OBJCOPY} -O binary $<TARGET_FILE:serenity-node>
                serenity-node.bin
        COMMAND ${CMAKE_SIZE} $<TARGET_FILE:serenity-node>
        COMMENT "Flash/RAM footprint against 128 KB / 32 KB [REF-SENSOR-004]")
endif()

## ---------------------------------------------------------------------------
## Host tests
## ---------------------------------------------------------------------------
if(SERENITY_HAL STREQUAL "sim")
    enable_testing()
    add_executable(test_crypto
        test/test_crypto.c
        template/src/sha256.c)
    target_include_directories(test_crypto PRIVATE template/include)
    add_test(NAME crypto COMMAND test_crypto)
endif()
