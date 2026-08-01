# AK7455 Nacelle Tilt-Angle Feedback — Firmware Calibration Specification

**Task:** 1.9.1 — Nacelle Tilt-Angle Feedback (Hall encoder)  
**Subtask:** Firmware: zero-calibration over the −5..90° sweep  
**Reference:** REF-SENSOR-008 (AK7455 datasheet 200800064-E-00)  
**Target Nodes:** River (FC3), Simon (FC4)  
**Date:** 2026-08-01

---

## 1. Overview

Each nacelle carries a CAN-PERIPH-GW-1 trust-module gateway (TI MSPM0G3507 + Infineon SLB9670 TPM) that reads the AK7455 magnetic angle encoder mounted at the wing/nacelle joint. The encoder measures nacelle tilt angle (−5° to 90°), independent of tilt-spar torsional wind-up.

The encoder's output compensates for residual ferrous-spar field distortion that may shift the zero point or introduce non-linearity over the sweep range. This specification defines the zero-calibration procedure and servo-feedback integration.

---

## 2. Hardware Context

### 2.1 Encoder Placement
- **Encoder:** AK7455 SPI angle sensor, off-axis-capable, Ø22 diametric magnet ring
- **Magnet:** Attached to rotating spar hub at wing/nacelle joint
- **Sensor Location:** Fixed wing structure (non-rotating); no slip ring required
- **Data Link:** CAN-PERIPH-GW-1 gateway reads AK7455 via SPI; publishes angle on isolated CAN-FD and RS-485

### 2.2 Tilt Range and Physical Constraints
- **Commanded Range:** −5° (backing/vertical) to 90° (horizontal/forward cruise)
- **Hard Stops:** CF-PETG stops at −5° and 140° (servo stall protection)
- **Feedback Purpose:** Close the tilt-servo loop on **true nacelle angle** (compensates for spar wind-up)

### 2.3 Distortion Sources
- **Ferrous Spar Material:** Tilt spar is 4130 steel (ferromagnetic); creates residual field at magnet location
- **Field Strength Variation:** Changes with spar orientation as nacelle tilts
- **Impact:** Zero-point shift of ±0.5–2° over full sweep; possible non-linearity in center range

---

## 3. Calibration Procedure

### 3.1 Pre-Calibration Setup
1. **Airframe Assembly State:** Hull complete; nacelles mounted at pivot; no foam pour yet
2. **Spar Alignment:** Both nacelles set to 0° (horizontal/forward) via servo commands
3. **Field Baseline:** Record ambient magnetic field (compass, EMI meter) to document environment
4. **Sensor Check:** Verify AK7455 communication (SPI handshake, sample reads) on both port and starboard gateways

### 3.2 Zero-Point Calibration Procedure

**Goal:** Establish the AK7455 raw-to-angle conversion table that absorbs ferrous-spar field effects.

**Process:**

1. **Park nacelle at mechanical 0° (horizontal/forward):**
   - Manually position nacelle by hand until visually aligned to reference edge (e.g., fuselage keel line)
   - **Do not** rely on servo position; use physical alignment
   - Record AK7455 raw angle reading (SPI register 0x03, resolution 0.00549°/LSB)
   - **Assign: `RAW_ANGLE_0DEG`** — the raw reading at true 0°

2. **Sweep tilt over full range (−5° to 90°):**
   - Manually tilt nacelle in 5° increments (using hand over appropriate range)
   - At each 5° step:
     - Verify position with angle gauge or reference mark
     - Sample AK7455 raw angle (average 10 reads to reduce noise)
     - Record: `{nominal_tilt_degrees, raw_angle_counts}`
   - Generate calibration table: `AK7455_CAL_TABLE[20]` (−5, 0, 5, 10, ..., 90°)

3. **Fit calibration curve:**
   - Verify monotonicity: `CAL_TABLE[i] < CAL_TABLE[i+1]` for all i
   - If non-monotonic, flag measurement error and re-measure
   - Fit polynomial (e.g., cubic spline) or use lookup table + linear interpolation
   - **Acceptance Criterion:** Fit error < 0.25° RMS over full range

4. **Cross-check servo feedback:**
   - Set servo to 0° via PWM command; verify AK7455 angle matches ±0.5°
   - Set servo to 90° via PWM command; verify AK7455 angle matches ±0.5°
   - If discrepancy > 0.5°, investigate servo linearity vs. mechanical friction

### 3.3 On-Board Calibration (Firmware Implementation)

**Firmware Module:** `CAN-PERIPH-GW-1/src/tilt_encoder.c`

```c
// Calibration data structure
struct AK7455_Calibration {
    int16_t raw_at_0deg;          // RAW_ANGLE_0DEG from procedure above
    struct {
        int16_t tilt_deg_x100;    // Nominal angle in 0.01° units (−500 to 9000)
        int16_t raw_angle_counts;  // Raw AK7455 reading at this angle
    } cal_table[20];              // −5° to 90° in 5° steps
    uint16_t crc16;               // CRC-16-CCITT for integrity
};

// Calibration application
int16_t ak7455_calibrated_angle(uint16_t raw_counts) {
    // Convert raw AK7455 reading to calibrated tilt angle (0.01° resolution)
    // Using stored calibration table + interpolation
    // Returns: tilt angle in units of 0.01° (e.g., 2750 = 27.50°)
    // Range: −500 to 9000
}

// Monotonicity check
bool ak7455_validate_calibration(const struct AK7455_Calibration *cal) {
    for (int i = 0; i < 19; i++) {
        if (cal->cal_table[i].raw_angle_counts >= cal->cal_table[i+1].raw_angle_counts) {
            return false; // Non-monotonic
        }
    }
    return true;
}
```

---

## 4. Runtime Feedback Integration

### 4.1 Servo Loop Architecture

**Control Loop (River or Simon firmware, CAN-PERIPH-GW-1 input):**

```
[Commanded Tilt Angle] → [PWM → Servo] → [Mechanical Linkage]
                              ↓
                      [Nacelle Rotates]
                              ↓
                      [AK7455 Reads Magnet]
                              ↓
                      [CAN-PERIPH-GW-1: Calibration]
                              ↓
                      [Measured Tilt Angle] → [CAN-FD Published]
                              ↓
                      [River/Simon FC: feedback to servo controller]
```

### 4.2 Feedback Message Format

**CAN-FD Message (ID: TBD, published by CAN-PERIPH-GW-1 gateway):**

| Byte(s) | Field | Type | Range | Unit |
|---------|-------|------|-------|------|
| 0–1     | `TILT_ANGLE_MEAS` | int16_t | −500 to 9000 | 0.01° |
| 2–3     | `TILT_RATE` | int16_t | −3600 to 3600 | 1.0°/s |
| 4       | `FLAGS` | uint8_t | — | bit 0: valid, bit 1: OOB |
| 5–6     | `RAW_COUNTS` | uint16_t | 0 to 4096 | LSBs |
| 7       | `TPM_SIGNATURE` | uint8_t (first 8 bits) | — | HMAC-SHA256 truncated |

- **Bit 0 (VALID):** Set if calibration valid and angle within expected range
- **Bit 1 (OOB):** Set if angle outside −10° to 100° (flag for anomalies)
- **TILT_RATE:** Computed via low-pass filter on angle delta between consecutive CAN frames

### 4.3 Servo Command Cross-Check

**River/Simon firmware input validation:**

```c
// River's primary servo controller
bool servo_update_with_feedback(
    int16_t commanded_angle_x100,  // 0.01° units, −500 to 9000
    int16_t measured_angle_x100,   // From CAN-PERIPH-GW-1
    uint16_t feedback_timeout_ms   // e.g., 500 ms
) {
    int16_t error = measured_angle_x100 - commanded_angle_x100;

    // Cross-check: measured angle should follow commanded within tolerance
    if (abs(error) > 200) {  // 2° tolerance
        // Log warning; check for spar wind-up or servo stall
        increment_servo_error_counter();
    }

    if (is_feedback_stale(feedback_timeout_ms)) {
        // Fallback to PWM-only open-loop control
        // (servo position is no longer guaranteed)
        fallback_to_pwm_control();
        return false;
    }

    return true;
}
```

---

## 5. Range Check and Anomaly Handling

### 5.1 Monotonicity Validation

At runtime, confirm that successive encoder reads are monotonically increasing (or decreasing during rapid tilt):

```c
bool ak7455_is_monotonic(int16_t prev_angle, int16_t curr_angle, int16_t angle_rate_limit) {
    int16_t delta = curr_angle - prev_angle;
    // If tilt rate is commanded at 90°/s, delta per CAN frame (10 ms) should be ≈0.9°
    return abs(delta) <= angle_rate_limit;  // Reject spikes; accept valid rates
}
```

### 5.2 Out-of-Bounds Handling

- **Expected Range:** −10° to 100° (includes ±5° margin beyond hard stops)
- **Out-of-Bounds Action:**
  - Set `FLAGS.OOB` bit in CAN message
  - Log to forensic microSD (write-blocked)
  - If sustained OOB for > 100 ms: alert flight controller
  - **Do not** apply calibration correction outside learned range; return raw angle instead

---

## 6. Testing and Validation

### 6.1 Bench Test (Before Flight)

1. **Calibration Verification:**
   - Run calibration procedure with airframe on bench
   - Generate calibration table
   - Verify fit error < 0.25° RMS

2. **Servo Feedback Loop:**
   - Command servo to 0°, 45°, 90°
   - Confirm measured angle follows within 0.5° and settles within 500 ms

3. **CAN Message Validation:**
   - Capture CAN-FD frames during tilt sweep
   - Verify message rate (e.g., 100 Hz)
   - Verify HMAC signatures (once TPM key distribution is complete)

4. **EMI Susceptibility (Phase 5+):**
   - Operate airframe near radiating RF source (test fixture or approved environment)
   - Confirm encoder reads remain monotonic and within 1° of calibration (vs. 0.25° bench)

### 6.2 Flight Test (Phases 5–9)

1. **Tethered Hover (Phase 5):**
   - Monitor tilt feedback during manual nacelle sweep
   - Confirm servo tracks commanded angle within 1°

2. **Free Hover + Transition (Phase 5–6):**
   - Autonomous nacelle sweep (90° forward to 0° hover to 90° aft)
   - Verify smooth angle feedback; no dropouts
   - Check for spar wind-up by comparing commanded vs. measured over 10-second hold

3. **Extended Flight (Phase 9–10):**
   - Sustained forward flight with pitch/yaw maneuvers
   - Monitor angle variance; detect spar fatigue or bearing wear

---

## 7. Documentation & References

- **Hardware:** `avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md`  
    "Deployment" mode 1 — Nacelle tilt encoder gateway
- **Airframe:** `docs/TILT_SPAR_ANALYSIS.md` §1, §3.5 — Spar wind-up analysis
- **Datasheet:** REF-SENSOR-008 — AK AK7455 SPI angle encoder, 200800064-E-00
- **REFERENCES.md:** REF-SENSOR-008

---

## 8. Firmware Implementation Owner

**Assigned to:** River firmware team (FC3) — primary tilt control  
**Secondary:** Simon firmware team (FC4) — failover tilt control  
**Start Date:** Upon task 1.9 approval  
**Milestone:** Calibration procedure + firmware ready for Phase 3 (Tilt Mechanism) integration

---

*Drafted by Claude Haiku 4.5 (2026-08-01) for hardware integration testing.*
