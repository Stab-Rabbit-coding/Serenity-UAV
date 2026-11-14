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

## Checks run after the decision (2026-11-14)

| Open item | Finding | Source |
|---|---|---|
| Temperature rating | The CYW4373E silicon is rated −40 to +85 °C; so is the Ezurio USB adapter built on it. The solder-down module's own rating is in its gated data sheet. | [REF-SENSOR-067], [REF-SENSOR-065] |
| USB mode on the solder-down module | The module data sheet's public scope says the series provides "either SDIO or USB2.0 interface for WLAN" and "USB2.0/PCM for Bluetooth". Which order code is the USB build, and its strapping, are in the gated body. | [REF-SENSOR-066] |
| Mainline driver | **Confirmed.** The stock Ubuntu `linux-modules-extra-6.8.0-149-generic` `brcmfmac.ko` lists USB ID `04B4:BD29` and requests `brcm/brcmfmac4373.bin` (the USB firmware; the SDIO build uses `brcmfmac4373-sdio.bin`). Infineon lists CYW4373/4373E as ACTIVE with backports for non-EOL LTS kernels. Whether `brcmfmac4373.bin` ships in `linux-firmware` was not checked. | module read 2026-11-14; [REF-SENSOR-068] |
| Transmit current | Adapter peak at USB VBUS (5 V): 345 mA (5 GHz, VHT80, MCS0); 2.4 GHz peak 300 mA. That is about 1.7 W at the adapter input, an upper bound for the module, which drops the adapter's buck regulator. | [REF-SENSOR-065] |
| Mass | The adapter is about 0.25 oz (7 g) with its case and USB-A plug; the bare module is lighter. Module mass is in the gated data sheet. | [REF-SENSOR-065] |

## Still unverified

1. The USB order code of the solder-down 453-00045 family, its USB strapping, its own temperature rating and its mass: all in the module data sheet behind the Ezurio login.
2. Whether a login-gated data sheet satisfies the sourcing rule's "public, NDA-free" test (owner).
3. `brcmfmac4373.bin` in `linux-firmware`.

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

- [x] OD-20: USB Wi-Fi module — **1** / 2 / 3. **Decided 2026-11-14 by the owner: option 1**, the Sterling-LWB5+ solder-down module in USB mode.
