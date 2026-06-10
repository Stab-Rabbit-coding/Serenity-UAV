/**
 * @file    mal_gimbal.c
 * @brief   Malcolm GCS — antenna tracking gimbal controller implementation.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 * Revision: Q1 (2026-06-10)
 *
 * See mal_gimbal.h for the API and position convention.
 *
 * Hardware path:
 *   Servo PWM: /sys/class/pwm/pwmchip0/pwm{0,1} (EHRPWM on AM6254)
 *   Encoder:   I²C bus 2 → TCA9548A 0x70 → AS5600 0x36 (ch.0=pan, ch.1=tilt)
 *
 * AS5600 register map (datasheet rev 1.09):
 *   0x0C–0x0D  RAW_ANGLE[11:0]   — 12-bit uncompensated angle
 *   0x0E–0x0F  ANGLE[11:0]       — 12-bit filtered angle (preferred)
 *   0x1A       STATUS             — MD/ML/MH magnet status bits
 */

#define _GNU_SOURCE

#include "mal_gimbal.h"
#include "mal_config.h"

#include <errno.h>
#include <fcntl.h>
#include <linux/i2c-dev.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

/* ---------------------------------------------------------------------------
 * Constants
 * ---------------------------------------------------------------------------*/

/** Path template for sysfs PWM period file.  %u = pwmchip index, %u = channel. */
#define PWM_PATH_FMT        "/sys/class/pwm/pwmchip%u/pwm%u"

/** AS5600 ANGLE register high byte (0x0E–0x0F, 12-bit result). */
#define AS5600_REG_ANGLE_H  (0x0EU)

/** AS5600 STATUS register — bit 5 = MD (magnet detected). */
#define AS5600_REG_STATUS   (0x1AU)
#define AS5600_STATUS_MD    (0x20U)

/** On-target threshold (degrees) — both axes must be within this. */
#define ON_TARGET_DEG       (1.0f)

/* ---------------------------------------------------------------------------
 * Internal state
 * ---------------------------------------------------------------------------*/

/** PWM sysfs path strings. */
static char s_pan_pwm_path[128];
static char s_tilt_pwm_path[128];

/** I²C file descriptor (TCA9548A bus). */
static int s_i2c_fd = -1;

/** Current servo PWM duty cycle (ns) — cached to avoid redundant writes. */
static uint32_t s_pan_duty_ns  = MAL_SERVO_NEUTRAL_NS;
static uint32_t s_tilt_duty_ns = MAL_SERVO_NEUTRAL_NS;

/** Last known encoder positions (degrees). */
static mal_gimbal_pos_t s_current_pos = {0.0f, 0.0f};

/** Commanded target position. */
static mal_gimbal_pos_t s_target_pos  = {0.0f, 0.0f};

/** Encoder zero offsets calibrated at init (raw counts). */
static uint16_t s_pan_zero_counts  = 0U;
static uint16_t s_tilt_zero_counts = 0U;

/* ---------------------------------------------------------------------------
 * Internal helpers — PWM sysfs
 * ---------------------------------------------------------------------------*/

/**
 * @brief  Write a numeric value to a sysfs PWM attribute file.
 *
 * @param[in] base   Base path (e.g. "/sys/class/pwm/pwmchip0/pwm0").
 * @param[in] attr   Attribute name (e.g. "duty_cycle").
 * @param[in] val    Value to write.
 * @return 0 on success; -1 on failure (errno set).
 */
static int pwm_write(const char *base, const char *attr, uint32_t val)
{
    char path[200];
    snprintf(path, sizeof(path), "%s/%s", base, attr);

    int fd = open(path, O_WRONLY);
    if (fd < 0) {
        return -1;
    }

    char buf[32];
    int len = snprintf(buf, sizeof(buf), "%u", val);
    int rc = (write(fd, buf, (size_t)len) == len) ? 0 : -1;
    close(fd);
    return rc;
}

/**
 * @brief  Export and configure a PWM channel via sysfs.
 *
 * @param[in] chip    pwmchip index.
 * @param[in] chan    Channel index.
 * @param[out] path   Populated with the channel base path (caller-supplied buf).
 * @param[in]  path_sz Size of path buffer.
 * @return 0 on success; -1 on failure.
 */
static int pwm_export(uint32_t chip, uint32_t chan, char *path, size_t path_sz)
{
    char export_path[64];
    snprintf(export_path, sizeof(export_path),
             "/sys/class/pwm/pwmchip%u/export", chip);

    /* Export channel (may already exist — ignore EBUSY). */
    int fd = open(export_path, O_WRONLY);
    if (fd >= 0) {
        char buf[8];
        int len = snprintf(buf, sizeof(buf), "%u", chan);
        write(fd, buf, (size_t)len);   /* ignore return — EBUSY is OK */
        close(fd);
    }

    snprintf(path, path_sz, PWM_PATH_FMT, chip, chan);

    if (pwm_write(path, "period", MAL_SERVO_PERIOD_NS) != 0) {
        return -1;
    }
    if (pwm_write(path, "duty_cycle", MAL_SERVO_NEUTRAL_NS) != 0) {
        return -1;
    }
    if (pwm_write(path, "enable", 1U) != 0) {
        return -1;
    }
    return 0;
}

/* ---------------------------------------------------------------------------
 * Internal helpers — I²C / AS5600
 * ---------------------------------------------------------------------------*/

/**
 * @brief  Select a TCA9548A mux channel.
 *
 * @param[in] chan  Channel index 0–7.
 * @return 0 on success; -1 on failure.
 */
static int tca9548a_select(uint8_t chan)
{
    if (ioctl(s_i2c_fd, I2C_SLAVE, MAL_TCA9548A_ADDR) < 0) {
        return -1;
    }
    uint8_t mask = (uint8_t)(1U << chan);
    return (write(s_i2c_fd, &mask, 1) == 1) ? 0 : -1;
}

/**
 * @brief  Read 12-bit angle from an AS5600 on the currently selected mux channel.
 *
 * @param[out] angle_counts  Raw 12-bit angle (0–4095 → 0–360°).
 * @return 0 on success; −1 if magnet not detected or I²C error.
 */
static int as5600_read_angle(uint16_t *angle_counts)
{
    /* Switch to AS5600 I²C address. */
    if (ioctl(s_i2c_fd, I2C_SLAVE, MAL_AS5600_ADDR) < 0) {
        return -1;
    }

    /* Check magnet detection status. */
    uint8_t status_reg = AS5600_REG_STATUS;
    if (write(s_i2c_fd, &status_reg, 1) != 1) {
        return -1;
    }
    uint8_t status = 0U;
    if (read(s_i2c_fd, &status, 1) != 1) {
        return -1;
    }
    if ((status & AS5600_STATUS_MD) == 0U) {
        /* Magnet not detected — encoder unusable. */
        return -1;
    }

    /* Read ANGLE register (0x0E high byte, 0x0F low byte). */
    uint8_t reg = AS5600_REG_ANGLE_H;
    if (write(s_i2c_fd, &reg, 1) != 1) {
        return -1;
    }
    uint8_t raw[2] = {0, 0};
    if (read(s_i2c_fd, raw, 2) != 2) {
        return -1;
    }
    *angle_counts = (uint16_t)(((uint16_t)(raw[0] & 0x0FU) << 8U) | raw[1]);
    return 0;
}

/* ---------------------------------------------------------------------------
 * Internal helpers — unit conversions
 * ---------------------------------------------------------------------------*/

/**
 * @brief  Convert an encoder angle (from init zero) to degrees.
 *
 * @param[in] raw_counts   Raw counts from AS5600 (0–4095).
 * @param[in] zero_counts  Zero-reference raw count captured at init.
 * @return Angle in degrees, unwrapped to [−180, +180).
 */
static float counts_to_deg(uint16_t raw_counts, uint16_t zero_counts)
{
    int32_t delta = (int32_t)raw_counts - (int32_t)zero_counts;

    /* Unwrap modular arithmetic around 4096 boundary. */
    if (delta >  (int32_t)(MAL_AS5600_COUNTS_PER_REV / 2U)) {
        delta -= (int32_t)MAL_AS5600_COUNTS_PER_REV;
    } else if (delta < -(int32_t)(MAL_AS5600_COUNTS_PER_REV / 2U)) {
        delta += (int32_t)MAL_AS5600_COUNTS_PER_REV;
    }

    return (float)delta * (360.0f / (float)MAL_AS5600_COUNTS_PER_REV);
}

/**
 * @brief  Map a servo angle in degrees to a PWM duty cycle in nanoseconds.
 *
 * @param[in] angle_deg  Desired servo angle (0° = 1000 µs; 90° = 1500 µs; 180° = 2000 µs).
 * @return PWM duty cycle in nanoseconds, clamped to [MIN, MAX].
 */
static uint32_t angle_to_duty_ns(float angle_deg)
{
    float frac = angle_deg / 180.0f;
    float duty = (float)MAL_SERVO_MIN_NS
                 + frac * (float)(MAL_SERVO_MAX_NS - MAL_SERVO_MIN_NS);

    if (duty < (float)MAL_SERVO_MIN_NS) {
        duty = (float)MAL_SERVO_MIN_NS;
    } else if (duty > (float)MAL_SERVO_MAX_NS) {
        duty = (float)MAL_SERVO_MAX_NS;
    }
    return (uint32_t)duty;
}

/**
 * @brief  Clamp a value to [lo, hi].
 */
static float clampf(float v, float lo, float hi)
{
    return (v < lo) ? lo : ((v > hi) ? hi : v);
}

/* ---------------------------------------------------------------------------
 * Public API
 * ---------------------------------------------------------------------------*/

mal_gimbal_err_t mal_gimbal_init(void)
{
    /* Open I²C bus for TCA9548A and AS5600. */
    s_i2c_fd = open("/dev/i2c-" __STRING(MAL_I2C_BUS), O_RDWR);
    if (s_i2c_fd < 0) {
        perror("mal_gimbal_init: open i2c");
        return MAL_GIMBAL_ERR_INIT;
    }

    /* Export and configure pan servo PWM. */
    if (pwm_export(MAL_GIMBAL_PAN_PWM_CHIP, MAL_GIMBAL_PAN_PWM_CHAN,
                   s_pan_pwm_path, sizeof(s_pan_pwm_path)) != 0) {
        fprintf(stderr, "mal_gimbal_init: pan PWM export failed\n");
        return MAL_GIMBAL_ERR_INIT;
    }

    /* Export and configure tilt servo PWM. */
    if (pwm_export(MAL_GIMBAL_TILT_PWM_CHIP, MAL_GIMBAL_TILT_PWM_CHAN,
                   s_tilt_pwm_path, sizeof(s_tilt_pwm_path)) != 0) {
        fprintf(stderr, "mal_gimbal_init: tilt PWM export failed\n");
        return MAL_GIMBAL_ERR_INIT;
    }

    /* Capture zero-reference encoder readings. */
    uint16_t raw = 0U;
    if (tca9548a_select(MAL_ENC_PAN_MUX_CHAN) != 0 || as5600_read_angle(&raw) != 0) {
        fprintf(stderr, "mal_gimbal_init: pan encoder read failed\n");
        return MAL_GIMBAL_ERR_ENCODER;
    }
    s_pan_zero_counts = raw;

    if (tca9548a_select(MAL_ENC_TILT_MUX_CHAN) != 0 || as5600_read_angle(&raw) != 0) {
        fprintf(stderr, "mal_gimbal_init: tilt encoder read failed\n");
        return MAL_GIMBAL_ERR_ENCODER;
    }
    s_tilt_zero_counts = raw;

    s_current_pos.pan_deg  = 0.0f;
    s_current_pos.tilt_deg = 0.0f;
    s_target_pos           = s_current_pos;

    return MAL_GIMBAL_OK;
}

void mal_gimbal_deinit(void)
{
    /* Disable servo outputs. */
    if (s_pan_pwm_path[0] != '\0') {
        pwm_write(s_pan_pwm_path,  "enable", 0U);
    }
    if (s_tilt_pwm_path[0] != '\0') {
        pwm_write(s_tilt_pwm_path, "enable", 0U);
    }

    if (s_i2c_fd >= 0) {
        close(s_i2c_fd);
        s_i2c_fd = -1;
    }
}

mal_gimbal_err_t mal_gimbal_set_target(const mal_gimbal_pos_t *target)
{
    if (target == NULL) {
        return MAL_GIMBAL_ERR_LIMIT;
    }

    /* Validate limits. */
    if (fabsf(target->pan_deg) > MAL_GIMBAL_PAN_MAX_DEG) {
        return MAL_GIMBAL_ERR_LIMIT;
    }
    if (target->tilt_deg < -MAL_GIMBAL_TILT_DOWN_DEG
        || target->tilt_deg > MAL_GIMBAL_TILT_UP_DEG) {
        return MAL_GIMBAL_ERR_LIMIT;
    }

    s_target_pos = *target;
    return MAL_GIMBAL_OK;
}

mal_gimbal_err_t mal_gimbal_update(float dt_s)
{
    /* Read current encoder positions. */
    uint16_t raw = 0U;

    if (tca9548a_select(MAL_ENC_PAN_MUX_CHAN) != 0 || as5600_read_angle(&raw) != 0) {
        return MAL_GIMBAL_ERR_ENCODER;
    }
    s_current_pos.pan_deg = counts_to_deg(raw, s_pan_zero_counts);

    if (tca9548a_select(MAL_ENC_TILT_MUX_CHAN) != 0 || as5600_read_angle(&raw) != 0) {
        return MAL_GIMBAL_ERR_ENCODER;
    }
    s_current_pos.tilt_deg = counts_to_deg(raw, s_tilt_zero_counts);

    /* Apply rate-limited step toward target. */
    float max_step = MAL_GIMBAL_MAX_SLEW_DPS * dt_s;

    float pan_err  = s_target_pos.pan_deg  - s_current_pos.pan_deg;
    float tilt_err = s_target_pos.tilt_deg - s_current_pos.tilt_deg;

    float pan_step  = clampf(pan_err,  -max_step, max_step);
    float tilt_step = clampf(tilt_err, -max_step, max_step);

    float new_pan  = s_current_pos.pan_deg  + pan_step;
    float new_tilt = s_current_pos.tilt_deg + tilt_step;

    /* Convert commanded angles to servo duty cycles and write PWM. */
    /* Pan: map [-170, +170] degrees → [1000, 2000] µs via mid = 1500 µs. */
    float pan_servo_deg  = 90.0f + (new_pan  / MAL_GIMBAL_PAN_MAX_DEG  * 85.0f);
    float tilt_servo_deg = 90.0f - (new_tilt / MAL_GIMBAL_TILT_UP_DEG  * 85.0f);

    uint32_t pan_duty  = angle_to_duty_ns(pan_servo_deg);
    uint32_t tilt_duty = angle_to_duty_ns(tilt_servo_deg);

    if (pan_duty != s_pan_duty_ns) {
        if (pwm_write(s_pan_pwm_path, "duty_cycle", pan_duty) != 0) {
            return MAL_GIMBAL_ERR_SERVO;
        }
        s_pan_duty_ns = pan_duty;
    }

    if (tilt_duty != s_tilt_duty_ns) {
        if (pwm_write(s_tilt_pwm_path, "duty_cycle", tilt_duty) != 0) {
            return MAL_GIMBAL_ERR_SERVO;
        }
        s_tilt_duty_ns = tilt_duty;
    }

    return MAL_GIMBAL_OK;
}

mal_gimbal_err_t mal_gimbal_get_position(mal_gimbal_pos_t *pos)
{
    if (pos == NULL) {
        return MAL_GIMBAL_ERR_ENCODER;
    }
    *pos = s_current_pos;
    return MAL_GIMBAL_OK;
}

void mal_gimbal_get_target(mal_gimbal_pos_t *target)
{
    if (target != NULL) {
        *target = s_target_pos;
    }
}

int mal_gimbal_is_on_target(void)
{
    return (fabsf(s_target_pos.pan_deg  - s_current_pos.pan_deg)  < ON_TARGET_DEG
         && fabsf(s_target_pos.tilt_deg - s_current_pos.tilt_deg) < ON_TARGET_DEG) ? 1 : 0;
}
