# SD card session logger
# Mounts a FAT-formatted microSD via SPI0 and writes two files per session:
#   CAN_NNNN.csv  — timestamped frame log
#   DTC_NNNN.txt  — human-readable DTC event log
import os
from machine import SPI, Pin
import time

_MOUNT               = '/sd'
_FLUSH_INTERVAL_MS   = 5_000


class SDLogger:
    def __init__(self, spi_id=0, sck=2, mosi=3, miso=4, cs=5,
                 spi_baudrate=10_000_000):
        import sdcard
        spi    = SPI(spi_id, baudrate=spi_baudrate,
                     sck=Pin(sck), mosi=Pin(mosi), miso=Pin(miso))
        cs_pin = Pin(cs, Pin.OUT, value=1)
        sd     = sdcard.SDCard(spi, cs_pin, baudrate=spi_baudrate)
        try:
            os.mount(sd, _MOUNT)
        except OSError as e:
            if e.args[0] != 19:   # 19 = ENODEV → already mounted is fine
                raise

        self._session     = self._next_session()
        self._can_f       = None
        self._dtc_f       = None
        self._frame_count = 0
        self._last_flush  = time.ticks_ms()
        self._open_session()

    # ── Session ───────────────────────────────────────────────────────────────

    def _next_session(self):
        try:
            nums = []
            for f in os.listdir(_MOUNT):
                if f.startswith('CAN_') and f.endswith('.csv'):
                    try: nums.append(int(f[4:8]))
                    except ValueError: pass
            return max(nums) + 1 if nums else 1
        except OSError:
            return 1

    def _open_session(self):
        n = self._session
        self._can_f = open(f'{_MOUNT}/CAN_{n:04d}.csv', 'w')
        self._dtc_f = open(f'{_MOUNT}/DTC_{n:04d}.txt', 'w')
        self._can_f.write('time_ms,can_id_hex,is_ext,dlc,data_hex,event_type,info\n')
        self._can_f.flush()
        self._dtc_f.write(
            f'=== OBD2 DTC Log — Session {n} ===\n'
            f'[S]=Stored  [P]=Pending  [M]=Permanent  [T]=Transient\n\n'
        )
        self._dtc_f.flush()
        print(f"[SD] Session {n} opened")

    @property
    def session(self): return self._session

    # ── Logging ───────────────────────────────────────────────────────────────

    def log_frame(self, ts_ms, can_id, is_ext, dlc, data,
                  event_type='CAN', info=''):
        hex_d    = ' '.join(f'{b:02X}' for b in data)
        info_s   = info.replace(',', ';').replace('\n', ' ')
        self._can_f.write(
            f'{ts_ms},{can_id:#09x},{"1" if is_ext else "0"},'
            f'{dlc},{hex_d},{event_type},{info_s}\n'
        )
        self._frame_count += 1
        self._maybe_flush()

    def log_dtc_event(self, ts_ms, code, desc, mode, transient=False):
        mt = {3:'S', 7:'P', 10:'M'}.get(mode, '?')
        tt = 'T' if transient else ' '
        self._dtc_f.write(
            f'[{ts_ms:>10}ms] [{mt}][{tt}] {code} — {desc}\n'
        )
        self._dtc_f.flush()

    def log_dtc_report(self, report_str):
        self._dtc_f.write('\n' + report_str + '\n')
        self._dtc_f.flush()

    def log_note(self, ts_ms, message):
        self._dtc_f.write(f'[{ts_ms:>10}ms] NOTE: {message}\n')
        self._dtc_f.flush()

    # ── Maintenance ───────────────────────────────────────────────────────────

    def _maybe_flush(self):
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_flush) >= _FLUSH_INTERVAL_MS:
            self._can_f.flush()
            self._last_flush = now

    def flush(self):
        if self._can_f: self._can_f.flush()
        if self._dtc_f: self._dtc_f.flush()

    def close(self):
        for f in (self._can_f, self._dtc_f):
            if f:
                try: f.flush(); f.close()
                except Exception: pass
        self._can_f = self._dtc_f = None

    def frame_count(self): return self._frame_count
