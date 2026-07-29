/** @brief Signing and Encryption context. One per node. */
typedef struct {
    ser_tpm2_t *tpm;            /**< Open TPM context; used for initial handshake[cite: 6]. */
    uint16_t    node_id;        /**< This node's fleet identifier[cite: 6].     */
    uint32_t    epoch;          /**< TPM-random, redrawn every boot[cite: 6].   */
    uint32_t    counter;        /**< Increments per signed message[cite: 6].    */
    uint8_t     key_id[4];      /**< Leading 4 bytes of the TPM key Name[cite: 6]. */
    
    /* Added for Hardware AES-GCM Offload */
    uint8_t     session_key[32];/**< Symmetric key derived from TPM ECDH.        */
    bool        session_active; /**< True once the ECDH handshake is complete.   */
    bool        ready;          /**< Indicates readiness for secure transport[cite: 6]. */
} ser_env_t;

/**
 * @brief Wrap @p payload in an AES-GCM encrypted envelope.
 *
 * Layout: `[24-byte header][ciphertext payload][16-byte GCM Tag]`. 
 * The GCM Tag replaces the HMAC-SHA256[cite: 6]. The header is authenticated 
 * but not encrypted (AAD). The `SER_ENV_FLAG_ENCRYPTED` flag is automatically applied[cite: 6].
 *
 * @param env     Active context containing the symmetric session_key.
 * @param out_cap Must be at least @p len + @ref SER_ENV_TOTAL_LEN[cite: 6].
 * @return SER_OK, or `SER_EBUSY` if the AES engine faults.
 */
int ser_env_seal_gcm(ser_env_t *env,
                     uint16_t topic_id,
                     uint8_t flags,
                     const uint8_t *payload,
                     size_t len,
                     uint8_t *out,
                     size_t out_cap,
                     size_t *out_len);