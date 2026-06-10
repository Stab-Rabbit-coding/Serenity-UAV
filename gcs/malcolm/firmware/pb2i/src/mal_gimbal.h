/**
 * @file    mal_gimbal.h
 * @brief   Malcolm GCS — antenna tracking gimbal controller API.
 *
 * Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
 * License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
 * Revision: Q1 (2026-06-10)
 *
 * The gimbal controller drives two DS3218MG servos (pan and tilt) via
 * Cape-B-2 EHRPWM outputs, and reads two AS5600 magnetic encoders (via
 * TCA9548A I²C mux on Cape-B-2) for closed-loop position feedback.
 *
 * Position convention:
 *   Pan  (azimuth)  : 0° = North; +CW from above; range ±170°.
 *   Tilt (elevation): 0° = horizontal horizon; +up; range −10° to +90°.
 *
 * Thread safety:
 *   All public functions are NOT thread-safe.  Call only from the gimbal
 *   control task or after acquiring MAL_GIMBAL_LOCK.
 */

#ifndef MAL_GIMBAL_H
#define MAL_GIMBAL_H

#include <stdint.h>

/* ---------------------------------------------------------------------------
 * Types
 * ---------------------------------------------------------------------------*/

/** Gimbal position in degrees. */
typedef struct {
    float pan_deg;   /**< Azimuth   — 0° = North, +CW, range ±170°.   */
    float tilt_deg;  /**< Elevation — 0° = horizon, + = up, max +90°. */
} mal_gimbal_pos_t;

/** Return codes for gimbal functions. */
typedef enum {
    MAL_GIMBAL_OK          =  0, /**< Operation successful.               */
    MAL_GIMBAL_ERR_INIT    = -1, /**< Initialisation failure.             */
    MAL_GIMBAL_ERR_ENCODER = -2, /**< I²C encoder read failure.           */
    MAL_GIMBAL_ERR_SERVO   = -3, /**< PWM servo write failure.            */
    MAL_GIMBAL_ERR_LIMIT   = -4, /**< Requested position exceeds travel.  */
} mal_gimbal_err_t;

/* ---------------------------------------------------------------------------
 * Initialisation and teardown
 * ---------------------------------------------------------------------------*/

/**
 * @brief  Open PWM and I²C handles; configure EHRPWM period; zero encoders.
 *
 * Must be called once before any other gimbal function.  On failure, the
 * gimbal is left in an undefined state and must not be used.
 *
 * @return MAL_GIMBAL_OK on success; MAL_GIMBAL_ERR_INIT on failure.
 */
mal_gimbal_err_t mal_gimbal_init(void);

/**
 * @brief  Disable servo PWM outputs and release all file descriptors.
 *
 * Safe to call even if mal_gimbal_init() failed (checks open state).
 */
void mal_gimbal_deinit(void);

/* ---------------------------------------------------------------------------
 * Position control
 * ---------------------------------------------------------------------------*/

/**
 * @brief  Command gimbal to a new absolute position.
 *
 * The command is rate-limited to MAL_GIMBAL_MAX_SLEW_DPS.  The function
 * returns immediately; the gimbal reaches the target asynchronously via the
 * background task kicked off by mal_gimbal_update().
 *
 * @param[in] target  Desired position.
 * @return MAL_GIMBAL_OK or MAL_GIMBAL_ERR_LIMIT if target is out of range.
 */
mal_gimbal_err_t mal_gimbal_set_target(const mal_gimbal_pos_t *target);

/**
 * @brief  Advance the servo position one control cycle towards the target.
 *
 * Must be called at a fixed rate (suggested ≥10 Hz) from a timer or loop.
 * Reads encoder feedback, applies rate limiting, writes servo PWM.
 *
 * @param[in] dt_s  Time elapsed since last call (seconds).
 * @return MAL_GIMBAL_OK or error code.
 */
mal_gimbal_err_t mal_gimbal_update(float dt_s);

/* ---------------------------------------------------------------------------
 * Position readback
 * ---------------------------------------------------------------------------*/

/**
 * @brief  Read current encoder positions.
 *
 * @param[out] pos  Populated with current pan and tilt angles.
 * @return MAL_GIMBAL_OK or MAL_GIMBAL_ERR_ENCODER on I²C failure.
 */
mal_gimbal_err_t mal_gimbal_get_position(mal_gimbal_pos_t *pos);

/**
 * @brief  Return the last commanded target position.
 *
 * @param[out] target  Populated with the current target.
 */
void mal_gimbal_get_target(mal_gimbal_pos_t *target);

/**
 * @brief  Return non-zero if the gimbal is within 1° of its target on both axes.
 *
 * @return 1 if on-target; 0 if still slewing.
 */
int mal_gimbal_is_on_target(void);

#endif /* MAL_GIMBAL_H */
