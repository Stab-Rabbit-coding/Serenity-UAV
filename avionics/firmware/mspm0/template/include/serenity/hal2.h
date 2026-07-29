/* ---------------------------------------------------------------------------
 * Hardware AES-GCM Accelerator
 *
 * Interfaces with the MSPM0G3507 built-in AES-128/256 hardware engine[cite: 1].
 * Used for line-rate bulk encryption after the TPM derives the session key.
 * ---------------------------------------------------------------------------*/

/**
 * @brief Load the symmetric session key derived from the TPM ECDH handshake 
 *        into the hardware AES accelerator.
 *
 * @param key       AES session key (16 or 32 bytes).
 * @param key_len   Length of the key in bytes (16 for AES-128, 32 for AES-256).
 * @return SER_OK, or a negative `SER_E*` code.
 */
int ser_hal_aes_gcm_set_key(const uint8_t *key, size_t key_len);

/**
 * @brief Encrypt a payload using the hardware AES-GCM engine.
 *
 * @param iv        Initialization vector (typically 12 bytes).
 * @param aad       Additional Authenticated Data (the envelope header).
 * @param aad_len   Length of AAD.
 * @param pt        Plaintext payload.
 * @param pt_len    Length of plaintext.
 * @param ct        Out: Ciphertext payload.
 * @param tag       Out: 16-byte GCM authentication tag.
 * @return SER_OK, or SER_EBUSY if the AES engine is locked.
 */
int ser_hal_aes_gcm_encrypt(const uint8_t *iv,
                            const uint8_t *aad,
                            size_t aad_len,
                            const uint8_t *pt,
                            size_t pt_len,
                            uint8_t *ct,
                            uint8_t tag[16]);