##
## CMakeLists.txt — FC node daemon (serenity-fc) stub
##
## Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
## License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
##
## Target: PocketBeagle 2 Industrial (AM6254, aarch64 Linux)
## Phase 6: stub only — no external dependencies.
## Phase 7 will add libgpiod (servo/EDF), libspi (IMU), CAN FD libraries.
##

add_executable(serenity-fc
    src/main.c
)

target_include_directories(serenity-fc
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
        ${CMAKE_SOURCE_DIR}/common/include
)

include(GNUInstallDirs)
install(TARGETS serenity-fc
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
