# Serenity UAV — Failsafe Threshold Document

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Revision:** Rev S (2026-07-12)

Resolves `TODO.md` Phase 0 pre-print documentation gate item "Failsafe Threshold
Document." Compile-time expression of the thresholds defined here lives in
[`avionics/firmware/common/include/failsafe_config.h`](../avionics/firmware/common/include/failsafe_config.h),
which every FC (Wash) and CN (Zoe) node includes.

**Reconciliation note (important):** the Phase 0 WBS item that requested this
document listed provisional "default" values for the battery and ESC-thermal
rows below. Two of those defaults have since been **superseded by real,
already-implemented firmware/documentation** — `pwr_fault.h`
(`avionics/firmware/fc/src/pwr_fault.h`) and `docs/POWER_DISTRIBUTION.md` S8
predate this document and are the authoritative source for battery
thresholds. This document uses the real implemented values and flags the
WBS defaults that were superseded (see S1 and S4). It does not silently
overwrite the WBS text with different numbers — the discrepancy is called
out explicitly and tracked in `TODO.md`.

---

## 1. Battery Low-Voltage Alert and RTL Trigger

**Authoritative source:** `docs/POWER_DISTRIBUTION.md` S8.1, implemented by
`avionics/firmware/fc/src/pwr_fault.h` (`PWR_FAULT_CELL_*_MV`,
`PWR_FAULT_PACK_*_MV`). **Not redefined in `failsafe_config.h`** — see that
header's scope note.

| State | Per-cell condition | Pack condition | Action |
|---|---|---|---|
| NORMAL | ≥ 3.50 V | ≥ 21.0 V | No action |
| WARN (alert) | < 3.50 V | < 21.0 V | CAN FD `POWER_WARN` broadcast; GCS alert; log entry |
| CRITICAL (**RTL trigger**) | < 3.30 V | < 19.8 V | Shed non-essential loads (`docs/POWER_DISTRIBUTION.md` S8.3); **initiate RTH**; increase log rate |
| EMERGENCY | < 3.00 V | < 18.0 V, or BQ76930 UV hardware latch | All non-propulsion loads off; 70% throttle cap (`PWR_FAULT_EMERGENCY_THROTTLE_PCT`); FC fault latch |

Hysteresis: 100 mV/cell (`PWR_FAULT_HYST_MV`) before stepping down a severity
level, preventing chatter at a threshold boundary.

**Superseded WBS default (correction record):** the originating WBS item
text specified "default 3.7V/cell alert, 3.5V/cell RTL cutoff." Those
figures predate `pwr_fault.h`'s WARN/CRITICAL/EMERGENCY state machine and do
not match any value implemented or documented elsewhere in the repository —
no other file cites a 3.7 V threshold as an operational cutoff (the
Phase 9 WBS "hover until 3.7V/cell cutoff" text refers to a *bench
endurance-test stopping point*, a different context from the in-flight RTL
trigger this document covers). The correct, implemented alert/RTL pair is
**3.50 V WARN / 3.30 V RTL-trigger**, per the table above. TODO.md is
updated accordingly (see closing note).

Hardware backstop, independent of firmware (`docs/POWER_DISTRIBUTION.md`
S8.4): BQ76930 UVP opens the discharge FET at 3.00 V/cell regardless of
firmware state, per [REF-ASTM-002] (ASTM F3005-22, sUAS battery
requirements).

---

## 2. Node Heartbeat Timeout and Radio-Loss RTL Timers

**Defined in:** `failsafe_config.h` — `FAILSAFE_CANFD_HEARTBEAT_TIMEOUT_MS`,
`FAILSAFE_RADIO_LOSS_RTL_SIK_LORA_MS`, `FAILSAFE_RADIO_LOSS_RTL_49MHZ_MS`.

### 2.1 CAN FD node heartbeat re-election

| Parameter | Value |
|---|---|
| Timeout | **100 ms** |

The PACE-prioritized failover architecture (`avionics/AGENTS.md` "Node Workload
Balancing and PACE Failover"; each tier's Primary/Alternative/Contingency/Emergency
assignment) is a runtime-assurance monitor structure consistent with
[REF-ASTM-003] (ASTM F3269-21): each tier bounds and can take over from the
tier above it. The CAN FD heartbeat is the underlying liveness signal for
that takeover, per [REF-ISO-001] (ISO 11898-1:2015+Amd.1, CAN FD data-link
layer) and the existing bus-controller election note in
`avionics/firmware/dts/cape-a/k3-am6254-pocketbeagle2-serenity-cape-a2.dts`
S8 ("BC capability on FC1, elected via CAN FD heartbeat"). At steady state
(post power-up), `docs/POWER_DISTRIBUTION.md` S10 documents heartbeat
election completing by T+30 s; 100 ms is the *in-flight* re-election
timeout once that steady state is established — short enough that a
Primary-tier node failure hands off to the Alternative tier well within a
human-imperceptible fraction of a second, long enough to avoid nuisance
re-election from an isolated dropped CAN FD frame (bus runs 1 Mbps
arbitration / 5 Mbps data phase, so 100 ms represents many missed-frame
opportunities, not a single-frame trigger).

### 2.2 Radio-loss automatic RTL

| Link | Timer | Role |
|---|---|---|
| SiK 915 MHz / LoRa 915 MHz | **5 s** | Primary/secondary comms links (Shepherd primary, Inara secondary comms tier; River/Simon LoRa via Emma) |
| 49 MHz AX.25 [REF-FCC-003 S15.235] | **10 s** | River/Simon Emma-board backup link; slower AFSK/KISS framing legitimately has longer inter-frame gaps |

Matches the Phase 10 WBS pass criterion (`TODO.md` SS3.0 Phase 10):
"Emergency RTL validation ... verify automatic RTL initiates within 5 s of
link loss" — that criterion is the SiK/LoRa case above.

**Open gap (not yet assigned a timer):** Wi-Fi (5 GHz) and Zigbee (2.4 GHz)
are both listed as usable C2 links in root `AGENTS.md`, but neither has an
assigned link-loss RTL timer in the originating WBS item or anywhere else
in the repository. Tracked as a follow-up in `TODO.md` (see closing note)
rather than inventing an unreviewed value here.

**Distinct from:** `MAL_HEARTBEAT_TIMEOUT_MS` (5000 ms,
`gcs/malcolm/firmware/pb2i/src/mal_config.h`) — that constant governs when
Malcolm's GCS *alerts the operator* that it has stopped hearing the
aircraft; it is a ground-side operator-notification timer, not the
aircraft's autonomous RTL trigger defined here. The two happen to be the
same order of magnitude by coincidence of independent design choices, not
because one derives from the other.

---

## 3. ToF Obstacle Avoidance Halt / Resume Clearance

**Defined in:** `failsafe_config.h` — `FAILSAFE_TOF_HALT_CLEARANCE_M`,
`FAILSAFE_TOF_RESUME_CLEARANCE_M`.

| Parameter | Value |
|---|---|
| Halt clearance | **1.0 m (3.3 ft)** |
| Resume clearance | **1.5 m (4.9 ft)** |

Applies to the 12x VL53L5CX obstacle-avoidance array (dual redundant Array
A / Array B, `docs/PHASED_BUILD_GUIDE.md` Phase 5), rated 4 m effective
range (`REFERENCES.md` REF-SENSOR-002 note: "the VL53L5CX obstacle-avoidance
sensors (4 m) used elsewhere in the airframe"). Both thresholds sit well
inside the sensor's rated range, leaving margin for detection latency and
closing-rate response time. The 0.5 m hysteresis band between halt and
resume prevents halt/resume chatter when hovering near a fixed clearance
boundary (e.g., station-keeping near a wall or the delivery platform in the
design mission profile, `README.md`).

**Citation gap (flagged, not fabricated):** no `REFERENCES.md` REF-ID exists
yet for the VL53L5CX part itself (only an informal range comparison inside
the REF-SENSOR-002 entry). Tracked as a follow-up in `TODO.md`.

---

## 4. ESC Thermal Cutback and Shutdown

**Defined in:** `failsafe_config.h` — `FAILSAFE_ESC_THERMAL_CUTBACK_C`,
`FAILSAFE_ESC_THERMAL_SHUTDOWN_C`, `FAILSAFE_ESC_THERMAL_CUTBACK_THROTTLE_PCT`.

| Stage | Threshold | Action |
|---|---|---|
| Cutback | **85°C** | Governor commands 70% throttle on the affected EDF (`FAILSAFE_ESC_THERMAL_CUTBACK_THROTTLE_PCT`, reusing the `PWR_FAULT_EMERGENCY_THROTTLE_PCT` convention already established in `pwr_fault.h`); EDF stays armed |
| Shutdown | **95°C** | Hard fault latch on the affected EDF; no auto-recovery, GCS acknowledgement required to re-arm (same semantics as `FAULT_EDF_MISMATCH` in `governor_config.h`) |

Read from the BDSHOT600 extended telemetry frame already carried by each
EDF's ESC (same telemetry path `governor_config.h`'s existing fault logic
uses).

**Open reconciliation item (flagged, not silently applied):**
`avionics/firmware/fc/src/governor_config.h` already implements a
**single-stage** `EDF_ESC_OVERTEMP_C = 100` hard cutoff — 5°C above this
document's two-stage shutdown threshold, and with no cutback stage at all.
This document's two-stage scheme is the Phase 0 documentation-gate design
target; reconciling it into `governor_config.h`'s live control loop (adding
the cutback stage, and deciding whether to lower the existing hard-fault
threshold from 100°C to 95°C or keep both) is a firmware behavior change to
safety-critical control logic and is deliberately **not** made in this
documentation pass — tracked as a follow-up in `TODO.md`.

---

## Summary Table

| Threshold | Value | Status |
|---|---|---|
| Battery alert (WARN) | 3.50 V/cell, 21.0 V pack | Implemented (`pwr_fault.h`) |
| Battery RTL trigger (CRITICAL) | 3.30 V/cell, 19.8 V pack | Implemented (`pwr_fault.h`) |
| CAN FD heartbeat re-election | 100 ms | Newly defined (`failsafe_config.h`) |
| SiK/LoRa link-loss RTL | 5 s | Newly defined (`failsafe_config.h`) |
| 49 MHz link-loss RTL | 10 s | Newly defined (`failsafe_config.h`) |
| Wi-Fi / Zigbee link-loss RTL | — | **Open gap** — no timer assigned yet |
| ToF halt / resume clearance | 1.0 m / 1.5 m | Newly defined (`failsafe_config.h`) |
| ESC thermal cutback | 85°C, 70% throttle | Newly defined (`failsafe_config.h`); **not yet reconciled with `governor_config.h`** |
| ESC thermal shutdown | 95°C | Newly defined (`failsafe_config.h`); **not yet reconciled with `governor_config.h`'s existing 100°C single-stage cutoff** |

---

*"We are not going anywhere. I don't care what's engaged." — Wash, holding
Serenity level on hydraulics alone. Failsafes exist so no one has to be
Wash in that moment.*
