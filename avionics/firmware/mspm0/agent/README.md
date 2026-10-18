# Micro XRCE-DDS Agent — DDS-Security configuration for the MSPM0 trust nodes

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**Drafted by:** Claude Opus 5 (Anthropic), 2026-07-28
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0

---

## What this directory does

The Agent runs on a PocketBeagle 2 alongside that bay's Fast DDS peer.  It is
not a proxy: for each MSPM0 client it creates a **separate Fast DDS
DomainParticipant** from the matching profile in [`profiles.xml`](profiles.xml),
so every trust node appears on the domain as its own peer — own GUID, own
participant name, own endpoints, discovered by SPDP/SEDP like any other node.

Each profile carries **that node's own** DDS-Security identity, so peers
authenticate the node's credential rather than the Agent's [REF-OMG-002 §9.3].

## The trust boundary, stated exactly

| Property | Enforced by | Covers |
| --- | --- | --- |
| Participant authentication | DDS-Security `builtin.PKI-DH` | Agent host ↔ every DDS peer |
| Message confidentiality/integrity on RTPS | DDS-Security `builtin.AES-GCM-GMAC` | Every RTPS hop |
| Topic-level authorisation | DDS-Security `builtin.Access-Permissions` | Every participant |
| **Sample origin** | **MSPM0's own SLB9670 TPM** | **MCU → any subscriber, end to end** |

The DDS-Security private key lives on the Agent host, because the ECDSA/ECDH
handshake cannot run on a Cortex-M0+ with no PKA engine.  The envelope MAC
(`template/include/serenity/sec_envelope.h`) is what closes that gap: it is
generated inside the MSPM0 under a key that never leaves that node's TPM, and
it travels inside the DDS sample.  **An attacker who compromises the Agent host
gains the DDS identity but cannot forge a node's telemetry.**

## Running the Agent

CAN-FD bearer (the primary path for every MSPM0 node):

```bash

MicroXRCEAgent canfd -D can0 -r refs.xml -x profiles.xml

```

Serial bearer (the RS-485 standby path, via the isolated ISOW1412 link):

```bash

MicroXRCEAgent serial -D /dev/ttyS4 -b 1000000 -r refs.xml -x profiles.xml

```

The CAN interface must be up in FD mode with the bit timing the nodes use —
1 Mbit/s nominal, 5 Mbit/s data, the ISOW1044's rated maximum
[REF-SENSOR-009]:

```bash

sudo ip link set can0 type can bitrate 1000000 dbitrate 5000000 fd on
sudo ip link set can0 up

```

## Provisioning a node's DDS-Security material

Certificates and keys are **not** in this repository and must never be
committed.  Per node:

1. Issue an identity certificate from the fleet identity CA, with the subject
   name matching the `<name>` element of that node's profile
   (e.g. `serenity/gw/encoder`).  Fast DDS matches the participant name
   against the certificate, and a mismatch fails the handshake with an error
   that does not name the mismatch — check this first when a node will not
   join.
2. Issue a permissions file from the permissions CA granting exactly the
   topics in that board's topic table (`boards/<board>/board.c`) and nothing
   else.  A node that publishes only `tof_range` and `node/health` should not
   be permitted `esc/command`; least privilege is a requirement of
   `avionics/AGENTS.md` "Zero Trust Architecture Compliance"
   [REF-NIST-001 §3.3].
3. Sign the governance and permissions documents into S/MIME form with the
   permissions CA.
4. Install under `/etc/serenity/pki/` on the Agent host with mode 0400, owned
   by the Agent's service user.

## Governance

The governance document is fleet-wide, not per node, and is generated from
`governance.xml.in` by the provisioning procedure above.  The settings this
project requires:

- `allow_unauthenticated_participants`: **false** — an unauthenticated
  participant must not join the domain at all.
- `enable_join_access_control`: **true** — permissions are checked at join.
- `rtps_protection_kind`: **SIGN** — RTPS submessages are authenticated.
- `discovery_protection_kind`: **ENCRYPT** — the topic list of the airframe is
  not public.
- `metadata_protection_kind`: **ENCRYPT**.
- `data_protection_kind`: **SIGN** at minimum; **ENCRYPT** for any topic
  carrying payload or cargo state.

## Open item

`governance.xml.in` and the per-node permissions templates are **not yet
written** — they are tracked as WBS §4.7.7.  The profiles in `profiles.xml`
reference the files they will produce, so a node configured today will fail to
join with a missing-file error rather than silently joining unsecured, which
is the correct failure direction.

## References

See the repository-root `REFERENCES.md`:

- [REF-OMG-002] OMG DDS Security v1.1
- [REF-SW-002] eProsima Micro XRCE-DDS Agent
- [REF-SENSOR-009] TI ISOW1044BDFMR
- [REF-NIST-001] NIST SP 800-207 Zero Trust Architecture
