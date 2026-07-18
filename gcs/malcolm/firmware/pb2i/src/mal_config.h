/**
 * @file    mal_config.h
 * @brief   Malcolm GCS PB2-I firmware — compile-time configuration constants.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 * Revision: R (2026-06-11)
 *
 * All hardware and operational parameters for the Malcolm GCS PocketBeagle 2
 * Industrial comms node are defined here.  Change values only when the physical
 * hardware or operational requirements change; do not embed literals elsewhere.
 *
 * Security note:
 *   TPM key slot assignments (MAL_TPM_KEY_HANDLE) are persistent across
 *   reboots.  Changing the handle after initial provisioning requires
 *   explicit TPM NV clear.  See provisioning procedure in
 *   gcs/malcolm/firmware/pb2i/PROVISIONING.md (to be created in Phase
 * Malcolm-2).
 */

#ifndef MAL_CONFIG_H
#define MAL_CONFIG_H

/* ---------------------------------------------------------------------------
 * MAVLink system identification
 * ---------------------------------------------------------------------------*/

/** GCS reserved MAVLink system ID (per ArduPilot convention). */
#define MAL_MAVLINK_SYS_ID             (255U)

/** MAVLink component ID — GCS master. */
#define MAL_MAVLINK_COMP_ID            (190U)

/** Aircraft MAVLink system ID (Serenity UAV). */
#define MAL_AIRCRAFT_SYS_ID            (1U)

/* ---------------------------------------------------------------------------
 * USB serial link to host PC
 * ---------------------------------------------------------------------------*/

/** CDC-ECM virtual Ethernet interface name on PB2-I. */
#define MAL_USB_IFACE                  "usb0"

/** Host PC IP on CDC-ECM link (assigned by usb_gadget dhcp). */
#define MAL_HOST_IP                    "192.168.7.1"

/** UDP port for mavlink-router input from host PC QGC. */
#define MAL_GCS_UDP_PORT               (14550U)

/** UDP port for MAVLink telemetry forwarded to tracking software. */
#define MAL_TRACKER_UDP_PORT           (14560U)

/* ---------------------------------------------------------------------------
 * SiK 915 MHz radio (RFD900x or compatible, UART2)
 * 902-928 MHz ISM band [REF-FCC-001 §15.247(a)(1)]; conducted power limit
 * [REF-FCC-001 §15.247(b)(3)(i)] applies (see MAL_LORA_TX_POWER_DBM below).
 * ---------------------------------------------------------------------------*/

/** UART device for SiK radio. */
#define MAL_SIK_UART_DEV               "/dev/ttyS2"

/** SiK baud rate. */
#define MAL_SIK_BAUD                   (57600U)

/* ---------------------------------------------------------------------------
 * LoRa 915 MHz (RFM95W on Cape-B-2 SPI1)
 * ---------------------------------------------------------------------------*/

/** SPI device for RFM95W. */
#define MAL_LORA_SPI_DEV               "/dev/spidev1.0"

/**
 * RFM95W output power setting (dBm).  Must be ≤20 dBm conducted (RFM95W
 * hardware maximum); separately bounded by the 1 W (30 dBm) conducted limit
 * for frequency-hopping/direct-sequence systems in the 902-928 MHz ISM band
 * [REF-FCC-001 §15.247(b)(3)(i)].
 */
#define MAL_LORA_TX_POWER_DBM          (20U)

/** LoRa spreading factor (SF7–SF12). */
#define MAL_LORA_SPREADING_FACTOR      (10U)

/** LoRa bandwidth (Hz): 125000, 250000, or 500000. */
#define MAL_LORA_BANDWIDTH_HZ          (125000U)

/* ---------------------------------------------------------------------------
 * WiFi 5 GHz (TI WL1837MOD, controlled via wpa_supplicant)
 * ---------------------------------------------------------------------------*/

/** WiFi interface name. */
#define MAL_WIFI_IFACE                 "wlan0"

/**
 * WiFi transmit power override (dBm).  When using the 14 dBi panel antenna,
 * reduce to 17 dBm to stay within the 30 dBm EIRP limit for UNII-3
 * [REF-FCC-002 §15.407(a)(3)].
 * Set to 0 to use kernel default; set with: iw dev wlan0 set txpower fixed 1700
 * (iw uses mBm units; 17 dBm = 1700 mBm).
 */
#define MAL_WIFI_TX_POWER_MBM          (1700U)

/* ---------------------------------------------------------------------------
 * 49 MHz [REF-FCC-003 §15.235] (XCVR-49MHZ-2, UART5)
 * ---------------------------------------------------------------------------*/

/** UART device for XCVR-49MHZ-2. */
#define MAL_49MHZ_XCVR_UART_DEV        "/dev/ttyS5"

/** XCVR-49MHZ-2 UART baud rate (1200 Bd Bell 202 AFSK). */
#define MAL_49MHZ_XCVR_BAUD            (1200U)

/**
 * Default 49 MHz channel index (0–4 → 49.830, 49.845, 49.860, 49.875, 49.890
 * MHz). Must match aircraft node channel assignment.  River = Channel 0; Simon
 * = Channel 1.
 */
#define MAL_49MHZ_XCVR_DEFAULT_CHANNEL (0U)

/** GPIO chip for XCVR-49MHZ-2 PTT_N line. */
#define MAL_49MHZ_XCVR_GPIO_CHIP       "/dev/gpiochip0"

/** GPIO line offset for XCVR-49MHZ-2 PTT_N (active low). */
#define MAL_49MHZ_XCVR_PTT_LINE        (11U)

/* ---------------------------------------------------------------------------
 * Gimbal servo outputs (via Cape-B-2 J_SERVO, EHRPWM outputs)
 * ---------------------------------------------------------------------------*/

/** PWM chip for pan servo (EHRPWM channel). */
#define MAL_GIMBAL_PAN_PWM_CHIP        (0U)

/** PWM channel for pan servo. */
#define MAL_GIMBAL_PAN_PWM_CHAN        (0U)

/** PWM chip for tilt servo. */
#define MAL_GIMBAL_TILT_PWM_CHIP       (0U)

/** PWM channel for tilt servo. */
#define MAL_GIMBAL_TILT_PWM_CHAN       (1U)

/** Servo PWM period (ns) — 50 Hz standard servo. */
#define MAL_SERVO_PERIOD_NS            (20000000U)

/** Servo neutral pulse width (ns) — 1500 µs = 90° mid-range. */
#define MAL_SERVO_NEUTRAL_NS           (1500000U)

/** Servo minimum pulse width (ns) — 1000 µs = 0°. */
#define MAL_SERVO_MIN_NS               (1000000U)

/** Servo maximum pulse width (ns) — 2000 µs = 180°. */
#define MAL_SERVO_MAX_NS               (2000000U)

/** Pan servo travel limit — maximum azimuth degrees from neutral. */
#define MAL_GIMBAL_PAN_MAX_DEG         (170.0f)

/** Tilt servo upper limit — maximum elevation degrees above horizontal. */
#define MAL_GIMBAL_TILT_UP_DEG         (90.0f)

/** Tilt servo lower limit — maximum depression below horizontal. */
#define MAL_GIMBAL_TILT_DOWN_DEG       (10.0f)

/** Maximum gimbal slew rate (degrees per second). */
#define MAL_GIMBAL_MAX_SLEW_DPS        (90.0f)

/* ---------------------------------------------------------------------------
 * AS5600 magnetic encoders (I²C via TCA9548A mux)
 * ---------------------------------------------------------------------------*/

/** I²C bus number for TCA9548A. */
#define MAL_I2C_BUS                    (2U)

/** TCA9548A I²C address (A0=A1=A2=GND → 0x70). */
#define MAL_TCA9548A_ADDR              (0x70U)

/** TCA9548A channel for pan encoder AS5600. */
#define MAL_ENC_PAN_MUX_CHAN           (0U)

/** TCA9548A channel for tilt encoder AS5600. */
#define MAL_ENC_TILT_MUX_CHAN          (1U)

/** AS5600 fixed I²C address (not configurable in hardware). */
#define MAL_AS5600_ADDR                (0x36U)

/** AS5600 raw register count for 360° (12-bit → 4096 counts). */
#define MAL_AS5600_COUNTS_PER_REV      (4096U)

/* ---------------------------------------------------------------------------
 * GCS GNSS receiver (u-blox, USB or UART on host PC — not on PB2-I)
 * ---------------------------------------------------------------------------*/

/**
 * The GNSS receiver feeds the tracking software on the host PC directly.
 * These constants are referenced by tracker.py, not by PB2-I firmware.
 * GNSS serial device on the host PC (symlink set by udev rule).
 */
#define MAL_GNSS_DEV_HOST              "/dev/gnss_gcs"

/** GNSS baud rate. */
#define MAL_GNSS_BAUD_HOST             (115200U)

/* ---------------------------------------------------------------------------
 * Security
 * ---------------------------------------------------------------------------*/

/** TPM2 HMAC key persistent handle for Malcolm's GCS node. */
#define MAL_TPM_KEY_HANDLE             (0x81000001U)

/** MAVLink HMAC-SHA256 signing key length (bytes). */
#define MAL_HMAC_KEY_LEN               (32U)

/** Heartbeat timeout — if no MAVLink heartbeat from aircraft within this
 *  many milliseconds, log a warning and alert the operator via status LED. */
#define MAL_HEARTBEAT_TIMEOUT_MS       (5000U)

#endif /* MAL_CONFIG_H */
