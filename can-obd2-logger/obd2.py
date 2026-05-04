# OBD2 / ISO 15765-2 (ISO-TP) parser
# Handles single-frame and multi-frame reassembly; decodes Mode 01 PIDs
# and extracts DTCs from Mode 03 (stored), 07 (pending), 0A (permanent).
import time
from dtc_db import decode_dtc
try:
    from dtc_oem import lookup_oem
except ImportError:
    def lookup_oem(_c): return None

# OBD2 CAN addresses
FUNC_REQ_ID  = 0x7DF      # broadcast functional request
PHYS_REQ_BASE= 0x7E0      # ECU 0-7 physical request → 0x7E0..0x7E7
RESP_BASE    = 0x7E8      # ECU 0-7 response         → 0x7E8..0x7EF
RESP_MASK    = 0x7F8

# OBD2 service modes
MODE_CURRENT = 0x01;  MODE_FREEZE  = 0x02
MODE_STORED  = 0x03;  MODE_CLEAR   = 0x04
MODE_PENDING = 0x07;  MODE_VEH_INFO= 0x09
MODE_PERM    = 0x0A

# ISO-TP frame type nibbles
_SF = 0;  _FF = 1;  _CF = 2;  _FC = 3

# ── Mode 01 PID decode table ──────────────────────────────────────────────────
def _pct(b):  return round(b[0]*100/255,1)
def _rpm(b):  return ((b[0]<<8)|b[1])//4
def _temp(b): return b[0]-40
def _maf(b):  return round(((b[0]<<8)|b[1])/100,2)
def _ft(b):   return round((b[1]/1.28)-100,1) if len(b)>1 else None

_PID = {
    0x04:("Engine Load",              "%",    _pct),
    0x05:("Coolant Temperature",      "°C",   _temp),
    0x06:("Short Term Fuel Trim B1",  "%",    _ft),
    0x07:("Long Term Fuel Trim B1",   "%",    _ft),
    0x08:("Short Term Fuel Trim B2",  "%",    _ft),
    0x09:("Long Term Fuel Trim B2",   "%",    _ft),
    0x0A:("Fuel Pressure",            "kPa",  lambda b: b[0]*3),
    0x0B:("Intake Manifold Pressure", "kPa",  lambda b: b[0]),
    0x0C:("Engine RPM",               "rpm",  _rpm),
    0x0D:("Vehicle Speed",            "km/h", lambda b: b[0]),
    0x0E:("Timing Advance",           "°",    lambda b: b[0]/2-64),
    0x0F:("Intake Air Temperature",   "°C",   _temp),
    0x10:("MAF Air Flow Rate",        "g/s",  _maf),
    0x11:("Throttle Position",        "%",    _pct),
    0x1F:("Engine Run Time",          "s",    lambda b: (b[0]<<8)|b[1]),
    0x21:("Distance with MIL On",     "km",   lambda b: (b[0]<<8)|b[1]),
    0x2F:("Fuel Tank Level",          "%",    _pct),
    0x31:("Distance Since Codes Clear","km",  lambda b: (b[0]<<8)|b[1]),
    0x33:("Barometric Pressure",      "kPa",  lambda b: b[0]),
    0x42:("Control Module Voltage",   "V",    lambda b: round(((b[0]<<8)|b[1])/1000,2)),
    0x45:("Relative Throttle Pos",    "%",    _pct),
    0x46:("Ambient Air Temperature",  "°C",   _temp),
    0x49:("Accel Pedal Position D",   "%",    _pct),
    0x4A:("Accel Pedal Position E",   "%",    _pct),
    0x4C:("Commanded Throttle",       "%",    _pct),
    0x5A:("Relative Accel Position",  "%",    _pct),
    0x5C:("Engine Oil Temperature",   "°C",   _temp),
    0x5E:("Engine Fuel Rate",         "L/h",  lambda b: round(((b[0]<<8)|b[1])/20,2)),
    0x67:("Coolant Temperature 2",    "°C",   lambda b: b[1]-40),
}


class OBD2Parser:
    """
    Stateful ISO-TP reassembler and OBD2 frame decoder.

    Usage:
        events = parser.process_frame(can_id, dlc, data, ts_ms)
        parser.poll_dtcs()     # call periodically to request DTCs
    """

    def __init__(self, can_send_fn=None):
        self._send = can_send_fn
        self._reassembly = {}   # ecu_idx → {buf, expected, sn}
        self._dtcs = {}         # code_str → entry dict

    # ── Public ────────────────────────────────────────────────────────────────

    def process_frame(self, can_id, dlc, data, ts_ms):
        """
        Process one received CAN frame.
        Returns list of event dicts (type: 'dtc', 'pid', or 'raw_obd').
        """
        events = []
        if (can_id & RESP_MASK) != RESP_BASE or dlc < 2:
            return events

        ecu = can_id & 0x07
        ft  = (data[0] >> 4) & 0x0F

        if ft == _SF:
            pl_len = data[0] & 0x0F
            events += self._decode(ecu, bytes(data[1:1+pl_len]), ts_ms)

        elif ft == _FF:
            total = ((data[0] & 0x0F) << 8) | data[1]
            self._reassembly[ecu] = {'buf': bytearray(data[2:]),
                                     'expected': total, 'sn': 1}
            if self._send:
                self._send(PHYS_REQ_BASE + ecu, bytes([0x30, 0x00, 0x00]))

        elif ft == _CF:
            sn = data[0] & 0x0F
            r  = self._reassembly.get(ecu)
            if r and sn == (r['sn'] & 0x0F):
                r['buf'] += data[1:]
                r['sn']  += 1
                if len(r['buf']) >= r['expected']:
                    payload = bytes(r['buf'][:r['expected']])
                    del self._reassembly[ecu]
                    events += self._decode(ecu, payload, ts_ms)

        return events

    def poll_dtcs(self, send_fn=None):
        """Send Mode 03/07/0A DTC requests (broadcast)."""
        tx = send_fn or self._send
        if tx is None:
            return
        tx(FUNC_REQ_ID, bytes([0x01, MODE_STORED]))
        time.sleep_ms(50)
        tx(FUNC_REQ_ID, bytes([0x01, MODE_PENDING]))
        time.sleep_ms(50)
        tx(FUNC_REQ_ID, bytes([0x01, MODE_PERM]))

    def request_pid(self, pid, send_fn=None):
        """Request a single Mode 01 PID."""
        tx = send_fn or self._send
        if tx:
            tx(FUNC_REQ_ID, bytes([0x02, MODE_CURRENT, pid]))

    def seen_dtcs(self):
        return dict(self._dtcs)

    def mark_cleared(self, ts_ms):
        for e in self._dtcs.values():
            e['transient'] = True
            e['cleared_ms'] = ts_ms

    # ── Internal ──────────────────────────────────────────────────────────────

    def _decode(self, ecu, payload, ts_ms):
        events = []
        if not payload:
            return events
        svc = payload[0]

        if svc in (0x43, 0x47, 0x4A):
            obd_mode = {0x43: 3, 0x47: 7, 0x4A: 10}[svc]
            n_bytes  = payload[1] if len(payload) > 1 else 0
            for i in range(n_bytes // 2):
                off = 2 + i * 2
                if off + 1 >= len(payload):
                    break
                b1, b2 = payload[off], payload[off+1]
                if b1 == 0 and b2 == 0:
                    continue
                code, desc = decode_dtc(b1, b2)
                oem = lookup_oem(code)
                if oem:
                    desc = oem
                self._track_dtc(code, desc, obd_mode, ts_ms)
                events.append({'type':'dtc','code':code,'desc':desc,
                                'mode':obd_mode,'ts_ms':ts_ms,'ecu':ecu})

        elif svc == 0x41 and len(payload) >= 2:
            pid  = payload[1]
            data = payload[2:]
            info = self._decode_pid(pid, data)
            events.append({'type':'pid','pid':pid,'info':info,
                            'ts_ms':ts_ms,'ecu':ecu})

        else:
            events.append({'type':'raw_obd','mode':svc,'payload':payload,
                            'ts_ms':ts_ms,'ecu':ecu})
        return events

    def _decode_pid(self, pid, data):
        if pid in _PID:
            name, unit, fn = _PID[pid]
            try:
                val = fn(data)
                return f"{name}: {val} {unit}"
            except Exception:
                pass
        return f"PID 0x{pid:02X}: {bytes(data).hex()}"

    def _track_dtc(self, code, desc, mode, ts_ms):
        if code not in self._dtcs:
            self._dtcs[code] = {'first_ms':ts_ms,'last_ms':ts_ms,
                                  'mode':mode,'desc':desc,
                                  'seen_count':1,'transient':False}
        else:
            e = self._dtcs[code]
            e['last_ms']     = ts_ms
            e['seen_count'] += 1
            if mode == 7 and e['mode'] != 3:
                e['transient'] = True


def format_dtc_report(parser, session_n):
    dtcs = parser.seen_dtcs()
    if not dtcs:
        return f"=== Session {session_n} — No DTCs Detected ===\n"

    stored    = [(c,e) for c,e in dtcs.items() if e['mode'] == 3]
    pending   = [(c,e) for c,e in dtcs.items() if e['mode'] == 7]
    permanent = [(c,e) for c,e in dtcs.items() if e['mode'] == 10]
    lines     = [f"=== Session {session_n} DTC Report ===",
                 f"Total unique codes: {len(dtcs)}\n"]

    for label, group in (("STORED (Mode 03)", stored),
                          ("PENDING / TRANSIENT (Mode 07)", pending),
                          ("PERMANENT (Mode 0A)", permanent)):
        if not group:
            continue
        lines.append(f"── {label}  [{len(group)} code(s)] ──")
        for code, e in sorted(group):
            dur = (e['last_ms'] - e['first_ms']) / 1000
            tag = " [TRANSIENT]" if e['transient'] else ""
            lines.append(
                f"  {code}{tag}\n"
                f"    {e['desc']}\n"
                f"    First: {e['first_ms']}ms  Last: {e['last_ms']}ms  "
                f"Seen: {e['seen_count']}x  Duration: {dur:.1f}s\n"
            )
        lines.append("")

    return "\n".join(lines)
