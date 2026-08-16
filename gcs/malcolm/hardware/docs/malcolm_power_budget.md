# Malcolm GCS — Field Power Budget

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Revision:** R (2026-06-11)

---

## Power Rail Summary

Malcolm GCS uses two independent power rails in field configuration:

| Rail    | Voltage | Source                         | Consumers |
|---------|---------|--------------------------------|-----------|
| +5 V    | 5.0 V   | 5 V / 5 A BEC from field pack  | PB2-I + Cape-B-2 + Emma |
| Laptop  | 19–20 V | DC–DC or laptop adapter        | GCS host PC (laptop) |

---

## Per-Component Current Draw (5 V rail)

| Component                       | Typical (mA) | Peak (mA) | Notes |
|---------------------------------|-------------|-----------|-------|
| PocketBeagle 2 Industrial (AM6254) | 350       | 600       | AM6254 quad-core at ~1 GHz; includes LPDDR4 |
| Cape-B-2 (TACCO) digital section  | 120         | 200       | ISOW1044, ADM2795, CPLD, TPM, log microSD |
| RFM95W LoRa (Tx)                | 0 (Rx)      | 120       | +20 dBm Tx burst, 40 mA Rx |
| RFD900x SiK (Tx)                | 0 (Rx)      | 200       | +20 dBm Tx burst, 50 mA Rx |
| TI WL1837MOD WiFi (Tx)          | 80          | 250       | Tx peak at +18 dBm; Rx ~80 mA |
| Emma (Tx)               | 5 (idle)    | 220       | 100 mW PA burst during AX.25 Tx |
| AS5600 encoders × 2             | 3           | 6         | 1.5 mA each @ 3.3 V |
| **Total 5 V rail**              | **~560**    | **~1400** | Peak during simultaneous SiK + WiFi Tx |

**5 V BEC requirement:** ≥5 V / 1.5 A continuous, 3 A peak capable.
A 5 V 5 A switching BEC (e.g., Pololu D24V50F5 or equivalent) provides adequate margin.

---

## Gimbal Servo Power (6 V rail)

Gimbal servos are powered from a separate 6 V rail to avoid switching noise on the 5 V
avionics rail.  If a FlightEngineer PDB is not present at the GCS, use a dedicated 6 V BEC.

| Component                | Typical (mA) | Peak (mA) | Notes |
|--------------------------|-------------|-----------|-------|
| Pan servo DS3218MG       | 100         | 600       | 600 mA stall; normal track ~100 mA |
| Tilt servo DS3218MG      | 100         | 600       | Same |
| **Total 6 V servo rail** | **200**     | **1200**  | Both servos slewing simultaneously |

**6 V BEC requirement:** ≥6 V / 1.5 A continuous, 2 A peak.

---

## Host PC Power

| Computer Class             | Typical Draw | Battery Life (100 Wh pack) |
|----------------------------|-------------|---------------------------|
| Laptop (Core i5 / Ryzen 5) | 15–30 W     | 3–6 h (100 Wh / 20 W avg) |
| Rugged laptop (Panasonic Toughbook class) | 25–40 W | 2.5–4 h |
| Mini PC (Intel NUC class, external display) | 20–35 W | 2.9–5 h |

For ≥8 h field operations, a 200 Wh battery pack is recommended (or two 100 Wh packs
with a DC–DC inverter rated for the laptop's input voltage).

> **Battery note:** Airline carry-on regulations limit lithium battery capacity to 100 Wh
> per pack (checked baggage limits vary by airline).  Plan field transport accordingly.

---

## Field Power System

### Bench Configuration

```
5 V 3 A USB-C supply ──► PB2-I J_USB
Host PC on AC mains
```

### Field Configuration (Minimum 4-Hour Endurance)

```
3S–6S 5000 mAh LiPo field pack
        │
        ├─► 5 V 5 A BEC ──────────────────► PB2-I + Cape-B-2 + Emma  (~2 W avg)
        ├─► 6 V 2 A BEC ──────────────────► Gimbal servos             (~1.2 W avg)
        └─► DC–DC to 19 V (or laptop direct if 6S pack used) ──► GCS host PC (~20 W avg)
```

| Pack Spec           | Capacity  | Est. Endurance | Notes |
|---------------------|-----------|----------------|-------|
| 3S 10,000 mAh LiPo  | 111 Wh    | ~4.8 h         | Lightest; limited PC endurance |
| 4S 10,000 mAh LiPo  | 148 Wh    | ~6.4 h         | Balanced; 16.8 V max for DC-DC |
| 6S 5,000 mAh LiPo   | 111 Wh    | ~4.8 h         | Aircraft-compatible cell chemistry; can share charger |

### Recommended Field Kit

| Item                        | Qty | Notes |
|-----------------------------|-----|-------|
| 4S 10,000 mAh LiPo          | 1   | Main field supply |
| 5 V 5 A switching BEC       | 1   | Pololu D24V50F5 or equiv |
| 6 V 2 A servo BEC           | 1   | Pololu D24V22F6 or equiv |
| DC-DC 16 V → laptop voltage | 1   | Buck/boost per laptop input voltage |
| 100 Wh USB-C power bank (backup) | 1 | Backup laptop power; airline-compliant |
| LiPo field charger          | 1   | AC-powered; charge at base between sorties |
