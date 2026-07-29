/* Additional Command codes, Part 2 §6.5.2 (TPM_CC)[cite: 8]. */
#define TPM2_CC_SIGN                (0x0000015DUL)
#define TPM2_CC_VERIFY_SIGNATURE    (0x00000177UL)
#define TPM2_CC_ECDH_KEYGEN         (0x00000156UL)
#define TPM2_CC_ECDH_ZGEN           (0x00000155UL)

/* ... existing definitions ... */

/* ---------------------------------------------------------------------------
 * Asymmetric Handshake Operations (PKA Offload)
 * ---------------------------------------------------------------------------*/

/**
 * @brief Sign a challenge digest using the node's persistent ECDSA P-256 key.
 * 
 * Used during the initial DDS-Security authentication handshake to prove 
 * identity to the ROS 2 domain[cite: 1].
 *
 * @param ctx       Open context with a provisioned asymmetric key.
 * @param digest    32-byte SHA-256 digest of the handshake challenge.
 * @param sig       Out: ECDSA signature structure.
 * @param sig_len   Out: Length of the returned signature.
 * @return SER_OK, or a negative `SER_E*` code.
 */
int ser_tpm2_sign_ecdsa(ser_tpm2_t *ctx,
                        const uint8_t digest[TPM2_SHA256_LEN],
                        uint8_t *sig,
                        size_t *sig_len);

/**
 * @brief Perform an Elliptic Curve Diffie-Hellman (ECDH) key exchange.
 *
 * Recovers the Z coordinate (shared secret) using the node's private key 
 * and the Agent's provided public point. This shared secret is subsequently
 * passed into a KDF to derive the AES session key.
 *
 * @param ctx       Open context.
 * @param pub_x     Agent's public point X coordinate.
 * @param pub_y     Agent's public point Y coordinate.
 * @param out_z     Out: Recovered shared secret.
 * @return SER_OK, or a negative `SER_E*` code.
 */
int ser_tpm2_ecdh_zgen(ser_tpm2_t *ctx,
                       const uint8_t *pub_x,
                       const uint8_t *pub_y,
                       uint8_t out_z[32]);