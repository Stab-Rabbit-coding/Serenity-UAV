##
## CMakeLists.txt — Serenity UAV common firmware library
##
## Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
## License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
##
## Builds the serenity-common static library shared by serenity-fc and
## serenity-cn.  Contains protocol decoders and utility code that both
## node types require.
##
## Phase 6 contents:
##   - sbus_input: SBUS RC protocol decoder (100 kbaud 8E2 UART)
##
## Dependencies: none (POSIX.1-2017 only; no third-party libraries).
##

add_library(serenity-common STATIC
    src/sbus_input.c
)

target_include_directories(serenity-common
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

## No external link dependencies — pure POSIX.
