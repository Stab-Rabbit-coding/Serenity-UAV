##
## arm-none-eabi.cmake — cross toolchain for the MSPM0G3507 (Cortex-M0+).
##
## Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
## Drafted by: Claude Opus 5 (Anthropic), 2026-07-28
## License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
##
## Usage:
##   cmake -B build -DCMAKE_TOOLCHAIN_FILE=cmake/arm-none-eabi.cmake \
##         -DSERENITY_HAL=mspm0 -DSERENITY_BOARD=can_periph_gw
##
set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR arm)

find_program(ARM_GCC arm-none-eabi-gcc REQUIRED)
get_filename_component(ARM_TOOL_DIR "${ARM_GCC}" DIRECTORY)

set(CMAKE_C_COMPILER   "${ARM_TOOL_DIR}/arm-none-eabi-gcc")
set(CMAKE_ASM_COMPILER "${ARM_TOOL_DIR}/arm-none-eabi-gcc")
set(CMAKE_OBJCOPY      "${ARM_TOOL_DIR}/arm-none-eabi-objcopy" CACHE FILEPATH "")
set(CMAKE_SIZE         "${ARM_TOOL_DIR}/arm-none-eabi-size" CACHE FILEPATH "")

## The MSPM0G3507 core: Cortex-M0+, Thumb only, no FPU [REF-SENSOR-004].
set(SERENITY_MCU_FLAGS "-mcpu=cortex-m0plus -mthumb")

set(CMAKE_C_FLAGS_INIT "${SERENITY_MCU_FLAGS} -ffunction-sections -fdata-sections")
set(CMAKE_ASM_FLAGS_INIT "${SERENITY_MCU_FLAGS}")
set(CMAKE_EXE_LINKER_FLAGS_INIT "${SERENITY_MCU_FLAGS}")

## Size, not speed: the constraint on this part is 128 KB of flash, and the
## publication rates are tens of hertz, not kilohertz.
set(CMAKE_C_FLAGS_RELEASE_INIT "-Os -DNDEBUG")

## The compiler cannot link a bare-metal test binary during CMake's own probe,
## so check it by compiling an object instead.
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
