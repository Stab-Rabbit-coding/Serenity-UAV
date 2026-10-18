> **Draft design note — unverified.** Hardware-AES and TPM-offload claims below have not been
> checked against the MSPM0 or SLB 9670/9672 datasheets, and the original source citations were
> lost. Do not cite this file as a design basis until each claim is traced to a datasheet.
> (The header fragments that accompanied it — `hal2.h`, `sec_envelope2.h`, `tpm2_.h` — were not
> compilable, were referenced by nothing, and were removed in the 2026-10-18 reconcile; they
> remain in the history of `don't-let-all-the-air-out`.)

## Security design

The cryptographic workload is divided between the hardware engines available on the PCB to accommodate the 128 KB flash and 32 KB SRAM memory limits:

1. **The Handshake (Asymmetric):** The SLB9670 TPM acts as a Public Key Accelerator (PKA). During the `JOIN` state, the MCU offloads the DDS-Security ECDSA P-256 signing and ECDH key exchange to the TPM over SPI[cite: 1, 8].
2. **The Session Key:** Upon a successful handshake, the TPM yields a symmetric AES session key, which the MCU loads directly into its hardware AES-128/256 engine.
3. **Bulk Encryption (Symmetric):** The TPM returns to a quiescent state. The MCU uses its hardware AES engine to encrypt the XRCE payloads (AES-GCM) at line rate prior to CAN-FD framing. 

Every published sample carries an envelope indicating it is an AES-GCM ciphertext payload, denoted by the `SER_ENV_FLAG_ENCRYPTED` flag.