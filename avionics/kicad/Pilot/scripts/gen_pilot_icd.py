#!/usr/bin/env python3
"""gen_pilot_icd.py — Generate the Pilot Interface Control Documents from the design data.

Usage:
    python3 gen_pilot_icd.py [--out DIR]       (default: avionics/kicad/Pilot/docs)

Writes ``Pilot-ICD-External.md`` (the cape's seven cable / field connectors) and
``Pilot-ICD-PB2I.md`` (the two PocketBeagle 2 Industrial expansion rails).  The pin and net
tables are read from the two authoritative sources and never typed by hand:

* connector pin -> net:  ``kicads/Pilot.net``  (kicad-cli export of ``Pilot.kicad_sch``)
* header pin -> net and ball: ``PB2_P1`` / ``PB2_P2`` and their comments in
  ``gen_pilot_sch.py`` (the generator is the schematic's source of truth)

The kidoc scaffold (``kidoc_scaffold.py --type icd``) lists ICs as "connectors", leaves every
direction and voltage level blank and prints ``__unnamed_n`` nets, so it is used here only for
its figure renders; the ICD text is written by this script.  Narrative cells that need an
engineer's decision are written as ``OPEN:`` items, never filled with guesses.

Author: Claude Sonnet 5.5, 2026-10-19.  Owner: sgriffing.
License: CC BY-SA 4.0 (documentation; SPDX-License-Identifier: CC-BY-SA-4.0)
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple

HERE = Path(__file__).resolve().parent
KICADS = HERE.parent / "kicads"
SCH_GEN = HERE / "gen_pilot_sch.py"

# connector ref -> (title, mating part, rating source, electrical class, notes)
# Ratings are quoted only where a document in avionics/datasheets/ states them.
EXTERNAL = {
    "PWR-IN": ("Power input", "Molex Nano-Fit 105313-1204, 2.5 mm, 4 circuits (header)",
               "OPEN: Molex 105313 drawing not on file (WBS 1.2a open gap); land not verified",
               "5 V DC supply, both +5V_IN pins paralleled, both GND pins paralleled"),
    "CAN-FD": ("CAN FD field port (isolated)", "JST SM04B-GHS-TB, 1.25 mm, 4 circuits",
               "JST GH: 1.0 A, 50 V AC/DC per contact, AWG 26-30 (eGH.pdf)",
               "Galvanically isolated, 5 000 Vrms (ISOW1044, REF-SENSOR-009), bus fault +/-58 V"),
    "RS-485": ("RS-485 field port (isolated)", "JST SM04B-GHS-TB, 1.25 mm, 4 circuits",
               "JST GH: 1.0 A, 50 V AC/DC per contact, AWG 26-30 (eGH.pdf)",
               "Galvanically isolated, 5 000 Vrms (ISOW1412, REF-SENSOR-010), 500 kbps"),
    "MIL-1553": ("MIL-STD-1553B bus port (bus A)", "JST SM04B-GHS-TB, 1.25 mm, 4 circuits",
                 "JST GH: 1.0 A, 50 V AC/DC per contact, AWG 26-30 (eGH.pdf)",
                 "Direct-coupled stub: PM-DB2791S 1:2.5 transformer, 2 x 55 R, 2 x SMAJ33CA "
                 "(REF-MIL-001 sec 4.5.1.5.2, REF-SENSOR-025)"),
    "J-ETH-RMII2": ("Ethernet port, RMII2 leg", "JST SM04B-GHS-TB, 1.25 mm, 4 circuits",
                    "JST GH: 1.0 A, 50 V AC/DC per contact, AWG 26-30 (eGH.pdf)",
                    "10/100BASE-TX line side of the TC1G00 magnetics (1500 Vac, REF-SENSOR-061); "
                    "Bob-Smith termination to PGND"),
    "J-ETH-USB1": ("Ethernet port, USB1 leg", "JST SM04B-GHS-TB, 1.25 mm, 4 circuits",
                   "JST GH: 1.0 A, 50 V AC/DC per contact, AWG 26-30 (eGH.pdf)",
                   "10/100BASE-TX line side of the TC1G00 magnetics (1500 Vac, REF-SENSOR-061); "
                   "Bob-Smith termination to PGND"),
    "J-SPI": ("Expansion port (SPI2 / UART1 / UART6)", "JST SM06B-GHS-TB, 1.25 mm, 6 circuits",
              "JST GH: 1.0 A, 50 V AC/DC per contact; cape fuse limits VCC to 0.35 A hold "
              "(Bourns MF-PSMF035X, REF-PWR-013)",
              "3.3 V logic, ESD on all four signals (TPD4E05U06, REF-SENSOR-044)"),
    "J-PWM": ("Servo / ESC signal block", "Samtec TSM-108-01-L-DV, 2 x 8, 2.54 mm (SMT male strip)",
              "Samtec TSM series; no rating cited (REF-CONN-001 covers the land only)",
              "3.3 V logic from PRU balls; 4 channels x (SIG, +5V, GND, PGND shield)"),
}

# direction as seen from the Pilot cape; only signals whose role is unambiguous
DIRECTION = {
    "PWR-IN": {"+5V_IN": "In (power)", "GND": "Return"},
    "CAN-FD": {"GND2_CAN": "Isolated return", "CAN_H_F": "Bidirectional",
               "CAN_L_F": "Bidirectional",
               "VCC2_CAN": "Passive (isolated rail)", "PGND": "Chassis"},
    "RS-485": {"GND2_RS485": "Isolated return", "RS485_A_F": "Bidirectional",
               "RS485_B_F": "Bidirectional", "VCC2_RS485": "Passive (isolated rail)",
               "PGND": "Chassis"},
    "MIL-1553": {"BUS_1553_P": "Bidirectional", "BUS_1553_N": "Bidirectional", "GND": "Return",
                 "PGND": "Chassis"},
    "J-SPI": {"EXT_SPI_5V": "Out (fused 5 V)", "EXT_SPI_SCK": "Out (SPI mode)",
              "EXT_SPI_MISO": "In (SPI mode)", "EXT_SPI_MOSI": "Out (SPI mode)",
              "EXT_SPI_SS1": "Out (SPI mode)", "GND": "Return", "PGND": "Chassis"},
    "J-PWM": {"DSHOT0": "Out", "DSHOT1": "Out", "DSHOT2": "Out", "DSHOT3": "Out",
              "+5V": "Out (5 V rail)", "GND": "Return", "PGND": "Chassis"},
}

NET_V = {"+5V_IN": "5 V", "+5V": "5 V", "EXT_SPI_5V": "5 V (0.35 A fuse)",
         "VCC2_CAN": "isolated 5 V (VISOIN)", "VCC2_RS485": "isolated 5 V (VISOIN)"}


def read_netlist() -> Dict[str, Dict[str, Tuple[str, str]]]:
    """ref -> pin -> (net, pinfunction) from the kicad-cli netlist."""
    text = (KICADS / "Pilot.net").read_text()
    out: Dict[str, Dict[str, Tuple[str, str]]] = {}
    net_re = re.compile(r'\(net \(code "\d+"\) \(name "([^"]+)"[^\n]*\n((?:\s+\(node[^\n]*\n?)+)')
    node_re = re.compile(
        r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)(?: \(pinfunction "([^"]*)"\))?')
    for m in net_re.finditer(text):
        for ref, pin, fn in node_re.findall(m.group(2)):
            out.setdefault(ref, {})[pin] = (m.group(1), fn)
    return out


def pin_key(p: str) -> Tuple[int, str]:
    return (0, f"{int(p):03d}") if p.isdigit() else (1, p)


def header_rows(name: str) -> List[Tuple[int, str, str]]:
    """(pin, net, ball comment) for PB2_P1 / PB2_P2 from the generator source."""
    src = SCH_GEN.read_text()
    body = src[src.index(f"{name} = ["):]
    body = body[:body.index("\n]\n")]
    rows = []
    for i, line in enumerate((ln for ln in body.splitlines()[1:] if ln.strip()), start=1):
        m = re.match(r'\s*(None|"[^"]*"),\s*#\s*\d+\s*(.*)', line)
        if not m:
            raise SystemExit(f"{name} line {i}: cannot parse {line!r}")
        net = "" if m.group(1) == "None" else m.group(1).strip('"')
        rows.append((i, net, m.group(2).strip()))
    return rows


def external_icd(nets: Dict[str, Dict[str, Tuple[str, str]]]) -> str:
    o = ["# Pilot Interface Control Document: External Connectors", "",
         "**Document:** Pilot-ICD-EXT, Revision A (draft for engineer review)  ",
         "**Applies to:** Pilot cape (CAPE-A-2) schematic `Pilot.kicad_sch`, 136 parts, ERC 0  ",
         "**Date:** 2026-10-19  ",
         "**Owner:** sgriffing (Griffing Technology LLC)  ",
         "**Prepared by:** Claude Sonnet 5.5 (Anthropic), via `scripts/gen_pilot_icd.py`  ",
         "**License:** CC BY-SA 4.0", "",
         "> **Status:** the pin and net tables are generated from the netlist and are exact for",
         "> the committed schematic. Items marked **OPEN** need an engineering decision or a",
         "> document that is not on file. The PCB is not fully routed (130 connections open);",
         "> this ICD describes the schematic, which is the controlling design.", "",
         "## 1. Scope", "",
         "This document defines every connector that crosses the Pilot cape's boundary except the",
         "two PocketBeagle 2 Industrial rails, which are in `Pilot-ICD-PB2I.md`. Pin 1 is the pin",
         "named `1` on the part's schematic symbol; physical pin-1 orientation is on the land",
         "pattern (`Serenity-Custom.pretty`, `Connector_JST.pretty`).", "",
         "Conventions: signal direction is from the Pilot cape's point of view. Voltage levels are",
         "quoted only where a datasheet in `avionics/datasheets/` states them. Units are SI",
         "for electrical quantities and imperial-primary for dimensions.", "",
         "## 2. Interface summary", "",
         "| Ref | Interface | Mating part | Pins |", "| --- | --- | --- | ---: |"]
    for ref, (title, mate, _, _) in EXTERNAL.items():
        n = len([p for p in nets[ref] if p != "MP"])
        o.append(f"| {ref} | {title} | {mate} | {n} |")
    o += ["", "## 3. Connector definitions"]
    for i, (ref, (title, mate, rating, elec)) in enumerate(EXTERNAL.items(), start=1):
        o += ["", f"### 3.{i} {ref}: {title}", "",
              f"* **Mating part:** {mate}",
              f"* **Contact rating:** {rating}",
              f"* **Electrical class:** {elec}", "",
              "| Pin | Symbol function | Net | Direction | Level |",
              "| --- | --- | --- | --- | --- |"]
        for pin in sorted(nets[ref], key=pin_key):
            net, fn = nets[ref][pin]
            d = DIRECTION.get(ref, {}).get(net, DIRECTION.get(ref, {}).get(net.split("_")[0], ""))
            if net.startswith("ETH_"):
                d = "Out (TX pair)" if "_TX" in net else "In (RX pair)"
            label = "shield / mounting tab" if pin == "MP" else pin
            o.append(f"| {label} | {fn} | `{net}` | {d or 'OPEN'} | {NET_V.get(net, '')} |")
        if ref in ("CAN-FD", "RS-485"):
            o += ["", "Termination: 120 R footprint (`R-CANT` / `R-485T`) is **DNP by default**; "
                  "populate only at a bus end node."]
        if ref.startswith("J-ETH"):
            o += ["", "Each Ethernet pair is one `TC1G00` chip transformer (`T-<leg>-TX`, `-RX`); "
                  "the pair is 100 ohm differential, 100BASE-TX."]
        if ref == "MIL-1553":
            o += ["", "Bus A only is populated; bus B is parked (REF-SENSOR-025)."]
    o += ["", "## 4. Open items", "",
          "1. **OPEN:** Molex 105313-1204 (PWR-IN) is not datasheet-verified (WBS 1.2a).",
          "2. **OPEN:** JST GH and Samtec TSM ratings are quoted from `eGH.pdf`; neither is yet "
          "catalogued in `REFERENCES.md` with a verified URL (open: not yet catalogued).",
          "3. **OPEN:** CAN-FD and RS-485 connector pin 4 (isolated VCC) current limit is not "
          "analysed; the ISOW DC-DC output budget has not been written down.",
          "4. **OPEN:** mating-harness drawing and pin-1 marking convention for the cable ends.",
          "5. **OPEN (owner):** J-PWM signal levels are 3.3 V from the AM625 PRU; confirm ESC "
          "inputs accept 3.3 V logic.", ""]
    return "\n".join(o)


def pb2_icd() -> str:
    o = ["# Pilot Interface Control Document: PocketBeagle 2 Industrial Headers", "",
         "**Document:** Pilot-ICD-PB2I, Revision A (draft for engineer review)  ",
         "**Date:** 2026-10-19  ",
         "**Prepared by:** Claude Sonnet 5.5 (Anthropic), via `scripts/gen_pilot_icd.py`  ",
         "**License:** CC BY-SA 4.0", "",
         "## 1. Scope", "",
         "Pilot is a cape for the PocketBeagle 2 Industrial (AM625). Two 2 x 18, 2.54 mm Samtec",
         "TSM-118-04-L-DV-LC SMT male strips (`PB2-P1`, `PB2-P2`) mate with the PB2-I's female",
         "receptacles. Pin names follow the BeagleBoard SRM designators `P1.01` to `P2.36`",
         "[REF-SENSOR-041 sec 4.2]. The cape drives none of: P1-14 / P2-23 (PB2 3.3 V out),",
         "P1-24 / P2-13 (VSYS), P2-14 (VBAT), P2-16 (BAT_TS), P2-12 (PWR_BTN), P2-26 (RESET#),",
         "P1-7 (VIN.USB), P1-17/18 (AIN references), P1-30/32 (UART0 console).", "",
         "The source of every row below is `PB2_P1` / `PB2_P2` in `gen_pilot_sch.py`; the ball",
         "text is that table's own comment. Full mux options per ball are in",
         "`../PB2I_AM625_HEADER_CAPABILITIES.md` section 4 [REF-SENSOR-049].", "",
         "> **Firmware rule:** where a header pin carries two AM625 balls, the second ball must be",
         "> held as a GPIO input with no pull by the device tree. P1-19/21/23/25/27 and P2-35/36",
         "> are also MSPM0L1105 AIN inputs; wiring never depends on firmware state alone.", ""]
    for rail in ("P1", "P2"):
        o += [f"## {rail}", "", "| Pin | Net | Ball / function (from schematic generator) |",
              "| --- | --- | --- |"]
        for pin, net, text in header_rows(f"PB2_{rail}"):
            shown = f"`{net}`" if net else "(not connected)"
            o.append(f"| {rail}.{pin:02d} | {shown} | {text} |")
        o.append("")
    o += ["## Open items", "",
          "1. **OPEN:** P1-31 (`NIC-USB1_VBUS`, GPIO0_59) must idle as a high-impedance input; "
          "the device-tree overlay does not exist yet (WBS 1.2a Pilot firmware items).",
          "2. **OPEN:** RMII2 timing with the MSPM0 AIN load (5 pF per pin) is verified at "
          "bring-up, not by analysis (owner decision 2026-10-17).", ""]
    return "\n".join(o)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(HERE.parent / "docs"))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    nets = read_netlist()
    (out / "Pilot-ICD-External.md").write_text(external_icd(nets))
    (out / "Pilot-ICD-PB2I.md").write_text(pb2_icd())
    print(f"wrote {out}/Pilot-ICD-External.md and Pilot-ICD-PB2I.md")


if __name__ == "__main__":
    main()
