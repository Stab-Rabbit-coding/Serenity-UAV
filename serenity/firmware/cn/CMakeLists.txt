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

##
## libgpiod 2.x — GPIO character device library (PTT_N control).
## Debian Trixie ships libgpiod 2.2.1; ensure the sysroot or pkg-config
## resolves to a 2.x version.  libgpiod 1.x is NOT compatible.
##
find_package(PkgConfig REQUIRED)
pkg_check_modules(GPIOD REQUIRED IMPORTED_TARGET libgpiod>=2.0)
target_link_libraries(serenity-cn PRIVATE PkgConfig::GPIOD)

## POSIX threads (RX background thread)
find_package(Threads REQUIRED)
target_link_libraries(serenity-cn PRIVATE Threads::Threads)

## Installation target
include(GNUInstallDirs)
install(TARGETS serenity-cn
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
