# Avionics KiCad Archive — Rev Q (2026-06-05)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/
**Archived:** 2026-06-05 (Revision Q)

---

## Archived Files

The following KiCad project files were active through **Revision P** and are archived
at **Revision Q** as the design standardises on EMI-hardened v2 capes at all positions.

| File(s) | Board | Archived Reason |
|---------|-------|-----------------|
| `CAPE-A-1.kicad_{pcb,sch,pro,prl}` | Cape-A-1 (85×55 mm, standard) | Superseded by Cape-A-2 (EMI-hardened) at all FC positions |
| `CAPE-B-1.kicad_{pcb,sch,pro,prl}` | Cape-B-1 (90×60 mm, standard) | Superseded by Cape-B-2 (EMI-hardened) at all CN positions |
| `XCVR-49MHZ-1.kicad_{pcb,sch,pro,prl}` | XCVR-49MHZ-1 (55×35 mm, standard) | Superseded by XCVR-49MHZ-2 (EMI-hardened) at all CN positions |
| `XCVR-49MHZ-1.md` | XCVR-49MHZ-1 design notes | Superseded; v2 design notes in `XCVR-49MHZ-2.md` |

Previously archived (pre-Rev Q):

| File(s) | Board | Archived Reason |
|---------|-------|-----------------|
| `CAPE-A-1-no-comment.*` | Cape-A-1 intermediate | Cleaned up before Rev P |
| `CAPE-B-1a.*` | Cape-B-1a predecessor | Superseded by Cape-B-1 |
| `CM3-CARRIER-1.*` | CM3 carrier | Superseded by PB2-I architecture (Rev K) |
| `CM4-CARRIER-1.*`, `CM4-CARRIER-2.*` | CM4 carriers | Superseded by PB2-I architecture (Rev K) |
| `COMMS-HAT-1.*`, `COMMS-HAT-SWITCH.*` | CM4 comms HATs | Superseded by Cape-B architecture (Rev K) |
| `SENSORHAT-1.*` | CM4 sensor HAT | Superseded by Cape-A architecture (Rev K) |
| `TRIHAT-1.*` | Pico2 triple HAT | Superseded by PB2-I architecture (Rev K) |

---

## Active Designs (Rev Q)

The following KiCad files in `avionics/kicad/` are the sole active avionics designs:

- **Cape-A-2** (`CAPE-A-2.kicad_{pcb,sch,pro,prl}`, `CAPE-A-2.md`) — EMI-hardened FC cape, all 4 FC positions
- **Cape-B-2** (`CAPE-B-2.kicad_{pcb,sch,pro,prl}`, `CAPE-B-2.md`) — EMI-hardened CN cape, all 4 CN positions
- **XCVR-49MHZ-2** (`XCVR-49MHZ-2.kicad_{pcb,sch,pro,prl}`, `XCVR-49MHZ-2.md`) — EMI-hardened 49 MHz RCRS

Gerbers for v2 capes are in `avionics/gerbers/CAPE-A-2/`, `avionics/gerbers/CAPE-B-2/`,
`avionics/gerbers/XCVR-49MHZ-2/` — pending DRC sign-off before fabrication submission.
