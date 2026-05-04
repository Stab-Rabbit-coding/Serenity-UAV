# OBD2 CAN Logger — Waveshare RP2350-CAN
# Records all CAN traffic to microSD; detects and catalogues every DTC
# (stored, pending, permanent, transient) with timestamps and descriptions.
#
# Hardware:
#   CAN controller (XL2515/MCP2515):  SPI1 — SCK=GP10, MOSI=GP11, MISO=GP8, CS=GP9
#   CAN interrupt (optional but fast): GP12
#   SD card:                          SPI0 — SCK=GP2,  MOSI=GP3,  MISO=GP4, CS=GP5
#   Onboard LED:                      GP25 (standard Pico LED)
#
# SD card must be FAT16 or FAT32 formatted before first use.
# OBD2 connector: CANH→Pin6, CANL→Pin14, GND→Pin4/5.

import time
from machine import Pin

from mcp2515   import MCP2515
from sdlogger  import SDLogger
from obd2      import OBD2Parser, format_dtc_report

# ─── Configuration ─────────────────────────────────────────────────────────────

CAN_KBPS         = 500       # 500 kbps standard; change to 250 for older vehicles
CAN_CRYSTAL_MHZ  = 8        # Waveshare RP2350-CAN uses 8 MHz oscillator
CAN_INT_PIN      = 12        # GP12 — interrupt-driven RX (set None to poll)

# How often to actively poll for DTCs (ms). Passive monitoring is continuous.
DTC_POLL_INTERVAL_MS = 30_000    # every 30 s

# How often to write a full DTC summary to the DTC log file
DTC_SUMMARY_INTERVAL_MS = 300_000  # every 5 min

# Log every CAN frame (True) or only OBD2 / DTC frames (False)
LOG_ALL_FRAMES = True

# Blink LED on each received frame
LED_BLINK = True

# ─── Hardware init ─────────────────────────────────────────────────────────────

led = Pin(25, Pin.OUT)

def blink(n=1, ms=30):
    for _ in range(n):
        led.value(1); time.sleep_ms(ms)
        led.value(0); time.sleep_ms(ms)


def init_can():
    can = MCP2515(
        spi_id=1, sck=10, mosi=11, miso=8, cs=9,
        int_pin=CAN_INT_PIN,
        crystal_mhz=CAN_CRYSTAL_MHZ,
    )
    can.init(kbps=CAN_KBPS)
    return can


def init_sd():
    sd = SDLogger(spi_id=0, sck=2, mosi=3, miso=4, cs=5)
    return sd


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("RP2350-CAN OBD2 Logger starting...")

    # Init CAN
    try:
        can = init_can()
        print(f"CAN OK — {CAN_KBPS}kbps")
        blink(2)
    except Exception as e:
        print(f"CAN INIT FAILED: {e}")
        while True:
            blink(5, 100); time.sleep_ms(500)

    # Init SD
    try:
        sd = init_sd()
        print(f"SD OK — session {sd.session}")
        blink(3)
    except Exception as e:
        print(f"SD INIT FAILED: {e}")
        # Continue without SD so the user sees the error, then halt
        while True:
            blink(10, 50); time.sleep_ms(1000)

    # OBD2 parser — pass CAN send callback so it can issue flow control & polls
    obd = OBD2Parser(can_send_fn=lambda cid, data: can.send(cid, data))

    sd.log_note(time.ticks_ms(), f"Logger started — CAN {CAN_KBPS}kbps crystal {CAN_CRYSTAL_MHZ}MHz")

    last_dtc_poll    = time.ticks_ms()
    last_dtc_summary = time.ticks_ms()
    last_error_check = time.ticks_ms()

    # Initial DTC poll after a short settle period
    time.sleep_ms(500)
    print("Polling for DTCs...")
    obd.poll_dtcs()

    print("Logging — press Ctrl+C to stop")

    try:
        while True:
            now = time.ticks_ms()

            # ── Receive CAN frame ────────────────────────────────────────────
            frame = can.recv()
            if frame is not None:
                can_id, is_ext, dlc, data = frame
                ts = time.ticks_ms()

                if LED_BLINK:
                    led.toggle()

                # Parse for OBD2 content
                events = obd.process_frame(can_id, dlc, data, ts)

                if events:
                    for ev in events:
                        ev_type = ev['type']
                        if ev_type == 'dtc':
                            info = f"DTC {ev['code']}: {ev['desc']}"
                            mode_label = {3:'STORED',7:'PENDING',10:'PERMANENT'}.get(ev['mode'], '?')
                            print(f"[{ts}ms] {mode_label} DTC: {ev['code']} — {ev['desc']}")
                            sd.log_dtc_event(ts, ev['code'], ev['desc'],
                                             ev['mode'], ev.get('transient', False))
                            if LOG_ALL_FRAMES or ev_type == 'dtc':
                                sd.log_frame(ts, can_id, is_ext, dlc, data, 'DTC', info)
                        elif ev_type == 'pid':
                            info = ev['info']
                            if LOG_ALL_FRAMES:
                                sd.log_frame(ts, can_id, is_ext, dlc, data, 'PID', info)
                        else:
                            if LOG_ALL_FRAMES:
                                sd.log_frame(ts, can_id, is_ext, dlc, data, 'OBD', '')
                else:
                    # Non-OBD2 CAN frame
                    if LOG_ALL_FRAMES:
                        sd.log_frame(ts, can_id, is_ext, dlc, data, 'CAN', '')

            # ── Periodic DTC poll ────────────────────────────────────────────
            if time.ticks_diff(now, last_dtc_poll) >= DTC_POLL_INTERVAL_MS:
                obd.poll_dtcs()
                last_dtc_poll = now

            # ── Periodic DTC summary ─────────────────────────────────────────
            if time.ticks_diff(now, last_dtc_summary) >= DTC_SUMMARY_INTERVAL_MS:
                report = format_dtc_report(obd, sd.session)
                sd.log_dtc_report(report)
                print(f"[{now}ms] DTC summary written — {sd.frame_count()} frames logged")
                last_dtc_summary = now

            # ── CAN error check ──────────────────────────────────────────────
            if time.ticks_diff(now, last_error_check) >= 10_000:
                eflg = can.error_flags()
                tec, rec = can.error_counts()
                if eflg & 0x20:   # TXBO — bus-off
                    sd.log_note(now, f"CAN BUS-OFF! EFLG=0x{eflg:02X} TEC={tec} REC={rec}")
                    print(f"WARNING: CAN bus-off — EFLG=0x{eflg:02X}")
                    can.init(kbps=CAN_KBPS)   # attempt recovery
                elif eflg & 0x10:
                    sd.log_note(now, f"CAN TX error-passive EFLG=0x{eflg:02X} TEC={tec}")
                last_error_check = now

    except KeyboardInterrupt:
        pass

    finally:
        print("\nShutting down...")
        ts = time.ticks_ms()
        report = format_dtc_report(obd, sd.session)
        print(report)
        sd.log_dtc_report(report)
        sd.log_note(ts, f"Session ended — {sd.frame_count()} frames logged")
        sd.close()
        blink(5, 200)
        print("Done. SD card safe to remove.")


main()
