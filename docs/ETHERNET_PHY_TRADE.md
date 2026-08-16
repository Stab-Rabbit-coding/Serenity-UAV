# Onboard Ethernet Interface Trade Study (Rev S, 2026-07-11)

> *"Everything is shiny... right up until you route your flight-control bus over a
> bus that stops to ask the host for permission 8000 times a second." — design
> review, this session.*

## Purpose

This study records the decision to keep the **native-MAC + external-PHY /
managed-switch** Ethernet front end on the Serenity avionics boards, and to
**reject** replacing it with USB-to-Ethernet bridge silicon (Microchip LAN9500A
class). It is written so the rejection is not silently re-litigated in a future
session. Author: AI (Claude, Opus 4.8), reviewed by @reepicheep-hakx.

**Decision: REJECTED — not deferred.** USB-to-Ethernet bridges are not a viable
substitute for the current architecture on any Serenity board. The idea is closed,
not parked.

## Baseline (retained) — what the boards do today

Ethernet on Serenity is a **redundant ring**, not a star. Every participating node
exposes **two** ports (upstream + downstream) so the ring can heal, and the ring
runs HSR/PRP hardware redundancy per IEC 62439-3.

| Board | Ethernet front end | Host attach | Ring role |
| --- | --- | --- | --- |
| **Wash** | 2× TI DP83825I 10/100 PHY | RMII0 + RMII1 to AM6254 CPSW | Two ports = one ring node (in + out) |
| **TACCO** | PHY deleted (Rev R1); rides the stack's Wash/COMMO ports | P1/P2 rails | Shares node ring ports |
| **COMMO** | 1× ADIN1300 gigabit PHY | RMII to the TACCO stack | Adds the stack's 2nd port; also lets COMMO run Ethernet standalone |
| **Observer** | Microchip KSZ9477 7-port managed switch | RGMII to AM62A7 | Hardware **HSR/PRP** ring switching per IEC 62439-3 |

Both host SoCs (PB2-I AM6254, Observer AM62A7) ship a **native Ethernet MAC** already.
The external parts add PHY, magnetic isolation, and (on Observer) managed ring switching
— they do not add a MAC that the silicon lacks.

## Rejected alternative — USB-to-Ethernet bridge (LAN9500A class)

Replace the native-MAC path with a USB 2.0 Hi-Speed → 10/100 bridge (integrated
MAC+PHY, enumerates as a USB netdev). Considered because a single bridge chip drops
the per-PHY support parts (1.8 V SMPS, RBIAS, MDC/MDIO) and removes the
length-matched RMII/RGMII routing.

### Advantages (the honest steelman)

- **Single-chip MAC+PHY** — drops the TPS62933 1.8 V SMPS, RBIAS resistor, and
  MDC/MDIO management bus carried per DP83825I.
- **Easier high-speed routing** — no controlled-impedance RGMII bundle, no 50 MHz
  RMII reference-clock distribution; just one USB differential pair.
- **Frees SoC MAC pins** for other pinmux, and can add Ethernet to a host with no
  free MAC.
- **Software-simple / hotpluggable** — standard USB CDC-ECM / vendor driver.
- **Lower parts cost** for a *single, non-redundant* 10/100 port.

### Why it is rejected

1. **No HSR/PRP → the redundant ring collapses.** LAN9500A-class parts are
   single-port, non-switching endpoints. They cannot do the hardware frame
   duplication/forwarding IEC 62439-3 requires. A ring node would need *two* bridges
   and still could not offload HSR. Observer's KSZ9477 (a 7-port managed switch) has no
   USB-bridge equivalent at all. This alone fails the project's first-class failover
   requirement (root `AGENTS.md`, "redundancy and failover in all systems possible").
2. **Non-deterministic latency/jitter.** USB is host-polled on 125 µs microframes
   with variable queuing/interrupt latency. This is a real-time flight-control bus
   (River/Simon EDF + nacelle sync); native CPSW + RMII gives bounded DMA-driven
   latency, USB does not, and TSN-style deterministic Ethernet over USB is not
   possible.
3. **Adds an EMI ingress path instead of removing one.** The Ethernet-side magnetics
   + CMC + TVS are still required regardless of the bridge, so no hardening is saved;
   meanwhile a 480 Mbps USB pair — an RF-sensitive link with weak error recovery — is
   added into a **200 V/m RS103 / 500 W/m²** design target, plus new RE102 emission
   harmonics to suppress. [REF-MIL-002]
4. **Galvanic isolation gets much harder.** The current path gets 5 kV isolation
   essentially for free from the LAN magnetics. Isolating USB requires a Hi-Speed
   digital isolator (ADuM4165/4166 class — expensive, scarce) or a drop to Full-Speed
   (12 Mbps), which throttles the link below 100 Mbps. The project mandates uniform
   5 kV galvanic isolation on Ethernet at every node (root `AGENTS.md`).
5. **Wastes the SoC's integrated Ethernet.** The AM6254 CPSW and AM62A7 RGMII are
   already paid for in silicon; USB bridges consume USB ports (needed elsewhere) to
   re-implement, worse, what the SoC does natively.
6. **Worse failure/recovery behavior.** USB stacks hang and need bus
   re-enumeration/resets — a single point of failure with no hardware fallback. The
   dual-PHY / managed-ring design degrades gracefully by construction.
7. **Higher CPU overhead.** USB-net is interrupt-and-copy heavy versus the CPSW's
   hardware DMA + switching.

## Comparison

| Criterion | Baseline (native MAC + PHY / KSZ9477) | Rejected (USB-Ethernet bridge) |
| --- | --- | --- |
| HSR/PRP ring redundancy | hardware-offloaded (IEC 62439-3) | **impossible** |
| Ports per ring node | 2 (in + out) | 1 per bridge (needs 2, still no HSR) |
| Latency / jitter | bounded, DMA-driven | host-polled, non-deterministic |
| Galvanic isolation | 5 kV from LAN magnetics (free) | Hi-Speed USB isolator (costly) or 12 Mbps |
| EM robustness (200 V/m) | Ethernet front end only | + fragile 480 Mbps USB pair |
| Uses SoC native MAC | yes | no (wastes it, burns a USB port) |
| Support parts per port | 1.8 V SMPS + RBIAS + MDC/MDIO | fewer (single chip) |
| High-speed routing | controlled-impedance RMII/RGMII | one USB pair |
| Dominant failure mode | tooth-level: PHY/link fault, ring heals | USB stack hang → bus reset, no failover |

## Recommendation

**Keep the DP83825I / ADIN1300 / KSZ9477 architecture. Reject USB-Ethernet
bridges.** The two things a bridge buys here (fewer support parts per port, easier
routing) are small next to what it costs: the redundant ring, timing determinism,
cheap isolation, and EM robustness — all explicit, load-bearing requirements.

If the underlying motivation resurfaces as *"reduce the per-PHY glue on Wash,"* the
on-architecture answer is to consolidate each PB2 node's two ports behind a small
**managed switch with integrated PHYs and HSR/PRP** (the same KSZ9477/KSZ9567 family
already vetted for Observer), which keeps the ring and the isolation while cutting
discrete parts. That is a separate trade, not a reason to adopt USB.

## References

- Root `AGENTS.md` — redundancy/failover requirement; uniform 5 kV galvanic
  isolation on CAN FD, RS-485, and Ethernet at every node; 500 W/m² operating
  objective.
- `avionics/AGENTS.md` — Ethernet ring topology; KSZ9477 selected over LAN9355/
  KSZ9563 for HSR/PRP hardware offload (AN3474); Wash 2× PHY, TACCO PHY-on-stack, COMMO
  ADIN1300, Observer KSZ9477.
- `avionics/kicad/Wash.md` §1 — EMI-hardened dual DP83825I PHY (RMII0/RMII1).
- `avionics/kicad/Observer/Observer.md` — KSZ9477 7-port switch, HSR/PRP per IEC 62439-3.
- [REF-MIL-002] MIL-STD-461G — RE102 radiated emissions / RS103 radiated
  susceptibility (200 V/m).
- Microchip AN3474 — KSZ9477 HSR/PRP hardware offload (IEC 62439-3).
