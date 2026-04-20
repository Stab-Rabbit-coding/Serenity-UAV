# Serenity-UAV
## Can't stop the signal and can't take the sky from me
A functional, security conscious, Unmanned Aerial Vehicle based on the Firefly Class spacecraft Serenity from the 2002 show.


here is a design for a functional, flying, tiltrotor edf drone based on Serenity, designed using Claude AI.

The specifications, so far:

2 x 70mm EFDs in the nacelles.
1 x 40mm EFD in the fuselage.
variable diameter thrust tubes remixed from:
Variable-area EDF nozzle
by BamJr
licensed under the Creative Commons - Attribution license.
https://www.thingiverse.com/thing:2991269

the drone is controlled by a raspberry Pico 2 with a custom sensor hat with GPS, imu, barometer, airspeed sensor connection, fpv camera, and control output for ESCs, nacelle and nozzle servos, payload release and winch, and navigation and anti-collision lights, all securedby a tpm.  jst gh connectors expose can fd (with selectable terminal jumper) and ethernet.
it's networked to a raspberry cm4 with 4gb ram on a carrier board with a tpm, 2.4ghz and 5ghz wifi and zigbee, a tf slot for an os micro SD with a forensicly sound write blocker and a pi zero 2 x 20 gpio header, with internal and sma antenna connections.

attached to the header is a comms and recorder hat with its own tpm, 915mhz mavlink mavlink and lora radio, 49mhz rcrs time division dual simplex transceiver with dynamic channel assignment,and a tf slot for a micro sd card with hardware enforced non-executable log storage. the hat has can fd and ethernet with jst gh connectors, which allows dual routes for intra-platform network and signaling. 

Here's the conversation:  https://claude.ai/share/a1e3900e-d2bf-4690-ba63-25178e7de666

Here's the latest design revision: https://claude.ai/public/artifacts/2ffe854e-3fdc-4efc-9c5e-52e73396950a

# Published under Creative Commons With Attribution version 4.0 by Steve Griffing, April 2026. 

Creative Commons Attribution 4.0 International
CC BY 4.0
SERENITY TILTROTOR DRONE PROJECT
Attribution 4.0 International · creativecommons.org/licenses/by/4.0
Share
Copy and redistribute in any medium or format
Adapt
Remix, transform, and build upon for any purpose
Commercial
Even for commercial purposes
Condition — Attribution Required
You must give appropriate credit when sharing or adapting this work.
SUGGESTED ATTRIBUTION TEMPLATE:
"Serenity Tiltrotor Drone Project, CC BY 4.0, based on:
· Serenity Firefly-class hull by Peter Farell (printables.com/model/548545, CC BY 4.0)
· Variable-area EDF nozzle by BamJr (thingiverse.com/thing:2991269, CC BY 4.0)
Include a link to creativecommons.org/licenses/by/4.0 and indicate if changes were made."
Component License Map
COMPONENT	ORIGINAL AUTHOR	SOURCE	LICENSE	DERIVATIVE NOTES
Hull	Peter Farell	printables.com/model/548545	CC BY 4.0	Serenity Firefly-class hull — adapted, scaled, hollowed
Nozzle	BamJr	thingiverse.com/thing:2991269	CC BY 4.0	Variable-area EDF nozzle — remixed for 40mm ID + Serenity bell integration
Design	This project	—	CC BY 4.0	All original design work: PCBs, firmware spec, wiring, flight system
What This License Covers
✓ COVERED under CC BY 4.0
✓3D printable hull, nacelle, bell, and nozzle design files (STL/STEP/F3D)
✓PCB schematics and Gerber files for TRIHAT-1, CM4-CARRIER-1, COMPHAT-1
✓Circuit diagrams, pinout tables, and wiring specifications
✓Mechanical drawings and assembly specifications
✓Firmware architecture specifications and algorithm descriptions
✓This design document in all its revisions (A–E and beyond)
✓Any derived works must carry CC BY 4.0 and attribute all upstream authors
⚠ NOT COVERED / SEPARATE TERMS
!Third-party commercial components (EDFs, ESCs, Pico 2, CM4, etc.) — governed by their own terms
!SiK radio firmware — GPL-3.0
!QGroundControl — GPL-3.0
!Raspberry Pi OS — mixed GPL
!tpm2-tools / tpm2-tss — BSD-2
!CPLD Verilog write-blocker firmware — separately MIT licensed
!Proprietary flight controller firmware (your compiled code) — your terms
!FAA/ICAO regulatory compliance is YOUR responsibility as operator
Patent Notice
This license does NOT grant rights to any patents held by component manufacturers or the design authors. The design uses standard open hardware interfaces (CAN FD, Ethernet, SDIO, SPI, I²C, MAVLink). If you commercialise products based on this design, conduct your own freedom-to-operate analysis. The write-blocker CPLD design follows published NIST SP 800-72 principles; no patent claims are made on the implementation.
Forensic Evidence Integrity Note
The write-blocker and NX enforcement hardware described in this design are intended to support forensic data integrity in UAV operations contexts. They are NOT certified forensic tools per NIST/SWGDE standards. Do not use this design as the sole mechanism for evidence preservation in legal proceedings without independent verification of the implementation against your jurisdiction's evidence handling requirements.
