##
## CMakeLists.txt — FC node daemon (serenity-fc)
##
## Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
## License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
##
## Target: PocketBeagle 2 Industrial (AM6254, aarch64 Linux)
## Phase 6: adds magnetometer, battery monitor, and SBUS input drivers.
## Phase 7 will add libgpiod (servo/EDF), libspi (IMU), CAN FD libraries.
##

add_executable(serenity-fc
    src/main.c
    src/mag_qmc5883l.c
    src/mag_mmc5983ma.c
    src/bmon_ina2xx.c
)

target_include_directories(serenity-fc
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
        ${CMAKE_SOURCE_DIR}/common/include
)

## serenity-common: SBUS decoder (Cape-A UART2 input) and shared utilities
target_link_libraries(serenity-fc
    PRIVATE
        serenity-common
)

include(GNUInstallDirs)
install(TARGETS serenity-fc
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
