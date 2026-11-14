# USB Wi-Fi Module for TACCO and NoNFO-Pilot-PB2 — Owner Decision Brief (OD-20)

**Owner / engineer of record:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**Drafted by:** Claude (Anthropic), 2026-11-14, at the owner's request
**License:** CC BY-SA 4.0 — see LICENSES/CC-BY-SA-4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Decision gates:** sprint S35 of `docs/plans/2026-11-14-001-feat-nonfo-pilot-pb2-stern-stack-plan.md`; TACCO fab (`avionics/WBS.md` §1.2a, open since 2026-09-29).

## The decision

The PB2-I brings no SDIO to its headers, so Wi-Fi has to come in over USB1 (owner decision 2026-09-29). On NoNFO-Pilot-PB2 it shares USB1 with the AX88772E ring NIC behind a USB 2.0 hub (OD-18, B+). The part has to be chosen before footprints are drawn.

**Recommendation: option 1, the Ezurio Sterling-LWB5+ solder-down module, in USB mode**, provided the hardware integration guide confirms USB mode on the solder-down part. If it does not, take option 2.

## What the part has to do

| Requirement | Source |
|---|---|
| 5 GHz Wi-Fi (the fleet's 5 GHz C2 path); 2.4 GHz too | BBE plan key decisions; `avionics/emi-hardening/WBS.md` (5 GHz-only spec for the Wi-Fi link) |
| USB 2.0 device interface to the PB2-I USB1 | owner 2026-09-29 |
| −40 to +85 °C operating | every fleet node is industrial-rated (PB2-I) |
| Manufacturer not domiciled or controlled in a restricted country; public, NDA-free datasheet | root `AGENTS.md` §5 sourcing rule (owner 2026-10-17) |
| Driver usable on the PB2-I's Debian kernel, preferably mainline | `avionics/firmware/README.md` (Debian Trixie on the AM6254) |
| Locking connectors only (U.FL for RF); no plug-in consumer dongle | plan R11 |
| Smallest mass and area | plan R2, KD7 |

## Options

| | 1. Sterling-LWB5+ SMT (453-00045 family) | 2. Sterling-LWB5+ M.2 Key E, USB (453-00049) | 3. Sterling-LWB5+ USB dongle (450-00137) | Rejected: Silex SX-USBAC | Rejected: Edimax IEW-7811UTC |
|---|---|---|---|---|---|
| Maker, domicile | Ezurio, Akron, Ohio [1] | same | same | Silex Technology (Japan) | Edimax (Taiwan) |
| Silicon | Infineon CYW4373E (Germany) | same | same | Qualcomm QCA9377-7 | not checked |
| Bands | 2.4 and 5 GHz, 802.11ac 1×1, plus BT 5.2 [2] | same | same [3] | 2.4 and 5 GHz | 2.4 and 5 GHz |
| USB interface | listed (SDIO, Serial, USB) [4]; **USB mode on the SMT part not confirmed** | USB for Wi-Fi and BT per Ezurio; one distributor listing says SDIO [5] | USB 2.0 HS, confirmed [3] | USB | USB-A |
| Operating temperature | **−40 to +85 °C is confirmed for the dongle only** [3]; SMT rating to be read from its datasheet | to be read | −40 to +85 °C [3] | −20 to +85 °C (fails) [6] | −20 to +75 °C (fails) [7] |
| Linux driver | mainline brcmfmac; CYW4373 SDIO/USB support added 2017 [8] (not yet checked against the current kernel's USB device table) | same | same | vendor driver behind an evaluation licence [6] (fails "public") | not checked |
| Fit | solder-down; smallest | M.2 socket and standoff: taller and heavier | USB-A plug and cable: non-locking (fails R11) | — | consumer adapter (fails R11) |

## Checks (avionics set, `docs/DOC_TEMPLATES.md`)

| Check | Result |
|---|---|
| Electrical engineering: load | Transmit current for the CYW4373E is **not yet read**; it sizes the 3V3_RF budget and the hub's port power. TACCO budgeted 550 mA for the old WL1837MOD (`avionics/kicad/TACCO/TACCO.md`). |
| Electrical engineering: emissions | All options are the same radio. Option 1 puts the radio on the cape inside the RF zone, with the antenna on U.FL. Options 2 and 3 move it off the board plane (socket) or onto a cable (dongle), which is worse for the board-level partition. |
| Function | All three carry 2.4 and 5 GHz Wi-Fi and Bluetooth 5.2 over USB. Only option 3 has USB confirmed outright. |
| Structural integrity | Option 1: solder joints, same as every other module. Option 2: a socket and a retention screw under vibration. Option 3: a plug held by friction (fails). |
| Mechanism and component interactions | Shares USB1 through the hub with the AX88772E ring NIC; USB 2.0 HS bandwidth is shared between the ring port and Wi-Fi. Bluetooth over USB could free TACCO's UART1 Bluetooth lines; not proposed here. |
| Weight and balance | Module masses **not yet read**. Option 1 is the lightest by construction (no socket, no cable). |
| Wire harness, fastener and mounting fit | Option 1: one U.FL pigtail to the antenna. Option 2: adds an M.2 socket, standoff and screw. Option 3: adds a cable and a non-locking plug. |
| Thermal load | Not yet computed; the radio's transmit dissipation joins the board budget in S34. |

## Still unverified

1. USB mode and the temperature rating of the solder-down 453-00045 module, from Ezurio's hardware integration guide.
2. Whether the 453-00049 M.2 part is USB (Ezurio) or SDIO (one distributor).
3. The CYW4373E USB ID in the current mainline brcmfmac device table, and its firmware in linux-firmware.
4. Transmit current and module mass.

None of these sources is catalogued in `REFERENCES.md` yet; that is S35 work, before any design file cites them.

## Sources

1. Ezurio, "About Ezurio" (address, Akron, Ohio): <https://www.ezurio.com/about-us>; rename from Laird Connectivity, March 2024: <https://www.ezurio.com/resources/newsroom/laird-connectivity-marks-a-new-phase-of-growth-with-strategic-rebrand-and-name-change>
2. Ezurio, Sterling-LWB5+ product page: <https://www.ezurio.com/wireless-modules/wifi-modules-bluetooth/sterling-lwb5-plus-wifi-5-bluetooth-5-module>
3. Ezurio, Sterling LWB5+ USB Dongle datasheet: <https://www.ezurio.com/documentation/datasheet-sterling-lwb5-usb-dongle>
4. Ezurio, part page 453-00045R: <https://www.ezurio.com/part/453-00045r>
5. Ezurio, Sterling LWB5+ M.2 datasheet: <https://www.ezurio.com/documentation/datasheet-sterling-lwb5-m2>; element14 listing 453-00049: <https://uk.farnell.com/laird/453-00049/wi-fi-bluetooth-module-2-4ghz/dp/3577644>
6. Silex, SX-USBAC product page: <https://www.silextechnology.com/connectivity-solutions/embedded-wireless/sx-usbac>; Mouser, SX-USBAC: <https://www.mouser.in/new/silex-technology/silex-sx-usbac-multiprotocol-modules>
7. Edimax, IEW-7811UTC: <https://www.edimax.com/edimax/merchandise/merchandise_detail/data/edimax/global/smb_embedded_wireless_adapter_industrial/iew-7811utc/>
8. Linux wireless documentation, brcm80211 drivers: <https://wireless.docs.kernel.org/en/latest/en/users/drivers/brcm80211.html>; commit "brcmfmac: Add support for CYW4373 SDIO/USB chipset" (2017), seen in a kernel tree log: <https://git.theobroma-systems.com/lion-linux.git/log/drivers/net/wireless/broadcom/brcm80211/brcmfmac>

## Owner decision

- [ ] OD-20: USB Wi-Fi module — **1 (recommended, after the integration-guide check)** / 2 / 3.
