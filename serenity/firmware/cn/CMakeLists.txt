##
## CMakeLists.txt — CN node daemon (serenity-cn)
##
## Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
## License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
##
## Target: PocketBeagle 2 Industrial (AM6254, aarch64 Linux)
## Requires: libgpiod 2.x, pthreads, Linux i2c-dev headers
##

add_executable(serenity-cn
    src/main.c
    src/xcvr_kiss.c
    src/si5351.c
)

target_include_directories(serenity-cn
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
        ${CMAKE_SOURCE_DIR}/common/include
)

## libgpiod 2.x — GPIO character device library (PTT_N control)
find_library(GPIOD_LIB gpiod REQUIRED)
find_path(GPIOD_INCLUDE gpiod.h REQUIRED)
target_include_directories(serenity-cn PRIVATE ${GPIOD_INCLUDE})
target_link_libraries(serenity-cn PRIVATE ${GPIOD_LIB})

## POSIX threads (RX background thread)
find_package(Threads REQUIRED)
target_link_libraries(serenity-cn PRIVATE Threads::Threads)

## Installation target
include(GNUInstallDirs)
install(TARGETS serenity-cn
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
