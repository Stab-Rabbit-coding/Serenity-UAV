# Serenity UAV — MSPM0G3507 Trust-Node Firmware

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**Drafted by:** Claude Opus 5 (Anthropic), 2026-07-28
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Status:** Template complete and building; MSPM0 peripheral drivers are open work

---

## Scope

One firmware template shared by every TI MSPM0G3507 in the fleet:

| Board | MCU ref | Role | Hardware source |
| --- | --- | --- | --- |
| `MAL-CAN-PERIPH-GW-PCB` | U1 (×N stacks) | Encoder / ESC / servo gateway | `avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md` |
| Jayne | U3 | Nose & cargo vision-board control MCU | `avionics/kicad/Jayne/Jayne.md` |
| Kaylee | U_MCU | PDB Section H trust module | `avionics/kicad/Kaylee/Kaylee.md` |

The boards differ only in `boards/<board>/` — identity, pin map, topic table
and application.  Everything else is shared, so a change to the security or
transport behaviour is made once.

## How an MSPM0 joins the ROS 2 domain as a peer

Each node creates its XRCE Participant **by reference**, naming a Fast DDS
participant profile the Agent resolves.  The Agent then calls
`create_participant_with_profile(domain_id, ref)`, giving that node its **own**
Fast DDS DomainParticipant — own GUID, own name, own endpoints, announced by
SPDP and SEDP.  Other nodes discover it as a peer, not as Agent traffic.  Each
profile carries that node's own DDS-Security identity certificate, so peers
authenticate the node's credential.  See [`agent/README.md`](agent/README.md).

```text
 MSPM0G3507                     PocketBeagle 2                  ROS 2 domain
┌────────────┐   CAN-FD /     ┌───────────────┐               ┌────────────┐
│ node + TPM │───RS-485──────►│ XRCE Agent    │──RTPS + DDS──►│ peers      │
│ (SLB9670)  │  (XRCE)        │ + Fast DDS    │   Security    │            │
└─────┬──────┘                └───────────────┘               └─────┬──────┘
      │                                                             │
      └────────── TPM-keyed envelope MAC, end to end ───────────────┘
```

### Why not a full Fast DDS peer on the MCU

Investigated and ruled out on two independent grounds, both measured:

1. **No Ethernet MAC.** The MSPM0G3507 datasheet's peripheral block diagram
   lists 4× UART, 2× SPI, I²C, MCAN, AES, TRNG, CRC and MATHACL — no MAC, MII
   or RMII anywhere in the document [REF-SENSOR-004].  RTPS peers on this
   airframe live on the Ethernet ring, and DDSI-RTPS defines no CAN transport.
2. **Memory.** 128 KB flash / 32 KB SRAM.  mbedTLS 3.6.2 built for
   `cortex-m0plus -Os` with exactly the DDS-Security Authentication (X.509 +
   ECDSA P-256 + ECDH) and Cryptographic (AES-GCM) plugin requirements
   measures **54.9 KB flash and 8.8 KB static RAM** — before any RTPS code, any
   IP stack, or the application.

The part *does* have a hardware AES-128/256 engine and a TRNG, which would
serve a DDS-Security cryptographic plugin; what it lacks is a PKA engine for
the authentication handshake.  Hence the split above: DDS-Security
authenticates the participant, the node's own TPM proves sample origin.

## Layout

```text
mspm0/
├── template/            Shared by all three boards — no hardware access except via hal.h
│   ├── include/serenity/
│   │   ├── hal.h            Hardware abstraction contract
│   │   ├── board.h          What a board must supply
│   │   ├── link.h           Bearer-agnostic transport + failover
│   │   ├── node.h           Lifecycle, QoS topic table, publish path
│   │   ├── sec_envelope.h   TPM-anchored per-sample envelope
│   │   ├── sha256.h         FIPS 180-4
│   │   ├── tpm2.h           TPM 2.0 command layer
│   │   └── tpm_tis.h        SLB9670 TIS-over-SPI transport
│   └── src/                 Implementations + main.c
├── boards/{can_periph_gw,jayne,kaylee}/   board_config.h, board.c, app.c
├── hal/{mspm0,sim}/     Flight port and POSIX host port
├── agent/               Agent-side DDS-Security profiles
├── cmake/               Cross toolchain, link script, vendored client
└── test/                Host tests
```

## Building

Host (POSIX, SocketCAN `vcan0`), which is what the tests run on:

```bash

cmake -B build -DSERENITY_BOARD=can_periph_gw -DSERENITY_HAL=sim
cmake --build build
ctest --test-dir build --output-on-failure

```

Flight target (Cortex-M0+):

```bash

cmake -B build-fw -DCMAKE_TOOLCHAIN_FILE=cmake/arm-none-eabi.cmake \
      -DSERENITY_HAL=mspm0 -DSERENITY_BOARD=can_periph_gw \
      -DCMAKE_BUILD_TYPE=Release
cmake --build build-fw

```

Board variants: `-DGW_ROLE=1|2|3` (encoder/ESC/servo), `-DGW_STACK_INDEX=1..4`,
`-DJAYNE_SITE=1|2` (nose/cargo).

## Verification status

| Check | Result |
| --- | --- |
| Host build, all 3 boards + all 3 gateway roles | Clean under `-Wall -Wextra -Wpedantic -Wconversion -Wshadow -Wformat=2 -Wstrict-prototypes -Wmissing-prototypes -Wundef -Wcast-qual -Werror` |
| SHA-256 against FIPS 180-4 published vectors | 5/5 pass (`ctest`) |
| Cross-link for `cortex-m0plus` | **38 908 B flash (30 % of 128 KB), 2 008 B static RAM (6 % of 32 KB)** |

The cross figure covers the full XRCE client, TPM stack, SHA-256, envelope,
link layer, node lifecycle and one board application.  The MSPM0 peripheral
drivers are not yet in it — see "Open work".

## Vendoring policy

Micro XRCE-DDS Client v3.0.1 and Micro-CDR v2.0.2 (both eProsima, Apache-2.0)
are fetched **by commit hash, not tag**, and compiled **unmodified**.  No
eProsima file is patched.  The two integration points that would normally
require a patch are handled outside their tree:

- `struct uxrCANPlatform` — avoided entirely by binding every bearer to
  upstream's *custom* transport rather than its SocketCAN-only CAN profile.
  One code path for all bearers, and runtime failover becomes possible.
- `clock_gettime()` — supplied by `hal/mspm0/syscalls.c`, backed by
  `ser_hal_time_ns()`.  The feature-test macro that exposes the declaration
  differs by C library (glibc wants `_POSIX_C_SOURCE`, newlib wants
  `_POSIX_TIMERS`, and defining the former on newlib *hides* it again); both
  were verified rather than assumed.

## Security design

Every published sample carries a 40-byte envelope: a 24-byte header plus a
16-byte MAC, which is the leftmost 128 bits of an HMAC-SHA256 computed by the
node's SLB9670 over `SHA-256(header ‖ payload ‖ topic_id)`.  Truncation follows
NIST SP 800-107 Rev 1 §5.3.3 [REF-NIST-006] — leftmost bits, λ ≥ 32; the
default λ = 128 is four times that floor.  `topic_id` is mixed into the MAC but
not transmitted, binding the sample to its topic for free.

Replay protection is `(epoch, counter)`: the epoch is drawn from the TPM's RNG
at each boot, so a node can reboot without every subsequent message looking
like a replay.  Counter wrap is a hard stop, not a rollover.

A node that cannot attest its TPM never reaches the JOIN state, and a signing
failure publishes nothing — the firmware never falls back to unsigned data,
because a subscriber cannot distinguish unsigned telemetry from forged
telemetry.

### Publication rate budget

Envelope (40 B) plus the XRCE submessage and CDR headers costs roughly 60 B
before payload, against a 63-byte CAN-FD MTU, so essentially every signed
sample occupies two or more CAN-FD frames — on the order of 100 µs of bus time
at 1 Mbit/s nominal with a 5 Mbit/s data phase.  A 20 Hz publication from each
of six gateway nodes is a low-single-digit percentage of the trunk.  This is
why fast inner control loops stay local to the MCU and only their *telemetry*
is published; a 400 Hz per-sample-signed loop would not fit and is not
attempted.

## Open work

Tracked in `avionics/firmware/WBS.md` §4.7:

1. **§4.7.2 — MSPM0 peripheral drivers.** `hal/mspm0/hal_mspm0.c` provides the
   reset vector, time base and memory setup, and returns `SER_ENOTSUP` from
   every peripheral entry point.  The drivers must be written against the TI
   MSPM0 SDK DriverLib, which is not installed on the authoring workstation, so
   DriverLib symbol names and the clock-tree sequence could not be verified —
   writing them from memory would produce code that fails on the bench with no
   way to separate a typo from a design error.
2. **§4.7.3–4.7.6 — device drivers.** AK7455 encoder, DSHOT/BDSHOT, servo PWM,
   TFmini-S, BQ76930.  Each application faults deliberately rather than
   publishing a fabricated value.
3. **§4.7.7 — DDS-Security governance and permissions documents.**
4. **Inbound envelope verification on the MCU** is not implemented: it needs
   the sending node's TPM key, and that registry lives on the PocketBeagle
   side.  A subscribing MSPM0 treats the DDS-Security guarantee as its
   authorisation boundary and logs the envelope header.

### Inconsistency found, not silently resolved

`avionics/firmware/dts/README.md` records the CAN FD link as "1/8 Mbps".
8 Mbit/s exceeds the ISOW1044's rated 5 Mbit/s [REF-SENSOR-009] and the
5 Mbit/s figure in `avionics/kicad/Wash/Wash.md`.  This firmware uses
1 Mbit/s nominal / 5 Mbit/s data and rejects anything higher at compile time
(`board.h`).  The DTS document needs a correcting pass — flagged, not edited
here, since it belongs to the PocketBeagle subsystem.

## References

See the repository-root `REFERENCES.md`: REF-SENSOR-004, REF-SENSOR-009,
REF-SENSOR-011, REF-ISO-001, REF-TCG-001, REF-TCG-002, REF-NIST-005,
REF-NIST-006, REF-NIST-001, REF-OMG-002, REF-SW-001, REF-SW-002, REF-FCC-003.
