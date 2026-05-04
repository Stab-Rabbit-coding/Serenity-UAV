# MCP2515 / XL2515 CAN controller driver for MicroPython
# Waveshare RP2350-CAN onboard chip: SPI1, SCK=GP10, MOSI=GP11, MISO=GP8, CS=GP9
from machine import SPI, Pin
import time

# Registers
_CANSTAT  = 0x0E;  _CANCTRL  = 0x0F
_TEC      = 0x1C;  _REC      = 0x1D
_CNF3     = 0x28;  _CNF2     = 0x29;  _CNF1     = 0x2A
_CANINTE  = 0x2B;  _CANINTF  = 0x2C;  _EFLG     = 0x2D
_TXB0CTRL = 0x30;  _TXB0SIDH = 0x31;  _TXB0SIDL = 0x32
_TXB0EID8 = 0x33;  _TXB0EID0 = 0x34;  _TXB0DLC  = 0x35;  _TXB0D0 = 0x36
_RXB0CTRL = 0x60;  _RXB0SIDH = 0x61;  _RXB0SIDL = 0x62
_RXB0DLC  = 0x65;  _RXB0D0   = 0x66
_RXB1CTRL = 0x70;  _RXB1SIDH = 0x71;  _RXB1SIDL = 0x72
_RXB1DLC  = 0x75;  _RXB1D0   = 0x76

# SPI commands
_RESET   = 0xC0;  _READ    = 0x03;  _WRITE   = 0x02
_RTS0    = 0x81;  _STATUS  = 0xA0;  _BITMOD  = 0x05
_LDTX0   = 0x40;  _RDRX0   = 0x90;  _RDRX1   = 0x94

# CANCTRL modes
MODE_NORMAL   = 0x00;  MODE_SLEEP = 0x20;  MODE_LOOPBACK = 0x40
MODE_LISTEN   = 0x60;  MODE_CONFIG= 0x80

# EFLG error bits
EFLG_TXBO  = 0x20   # bus-off
EFLG_TXEP  = 0x10   # TX error-passive
EFLG_RXEP  = 0x08   # RX error-passive
EFLG_EWARN = 0x01   # error warning


class MCP2515:
    """
    XL2515 / MCP2515 CAN controller driver.

    Waveshare RP2350-CAN defaults (SPI1):
        sck=10, mosi=11, miso=8, cs=9, int_pin=12 (optional)
    """

    def __init__(self, spi_id=1, sck=10, mosi=11, miso=8, cs=9,
                 int_pin=None, spi_baudrate=5_000_000, crystal_mhz=8):
        self._spi = SPI(spi_id, baudrate=spi_baudrate,
                        sck=Pin(sck), mosi=Pin(mosi), miso=Pin(miso))
        self._cs  = Pin(cs, Pin.OUT, value=1)
        self._int = Pin(int_pin, Pin.IN, Pin.PULL_UP) if int_pin is not None else None
        self._crystal = crystal_mhz

    # ── SPI primitives ─────────────────────────────────────────────────────────

    def _sel(self):   self._cs.value(0)
    def _desel(self): self._cs.value(1)

    def _rr(self, addr):
        self._sel()
        self._spi.write(bytes([_READ, addr]))
        v = self._spi.read(1)[0]
        self._desel()
        return v

    def _wr(self, addr, val):
        self._sel()
        self._spi.write(bytes([_WRITE, addr, val]))
        self._desel()

    def _bm(self, addr, mask, val):
        self._sel()
        self._spi.write(bytes([_BITMOD, addr, mask, val]))
        self._desel()

    def _qs(self):    # quick status
        self._sel()
        self._spi.write(bytes([_STATUS]))
        v = self._spi.read(1)[0]
        self._desel()
        return v

    # ── Init ───────────────────────────────────────────────────────────────────

    def _set_mode(self, mode, timeout_ms=100):
        self._bm(_CANCTRL, 0xE0, mode)
        t = time.ticks_ms()
        while time.ticks_diff(time.ticks_ms(), t) < timeout_ms:
            if (self._rr(_CANSTAT) & 0xE0) == mode:
                return True
            time.sleep_ms(1)
        return False

    def reset(self):
        self._sel()
        self._spi.write(bytes([_RESET]))
        self._desel()
        time.sleep_ms(10)

    def init(self, kbps=500):
        """Initialise the CAN controller. kbps: 100/125/250/500/1000."""
        self.reset()
        if not self._set_mode(MODE_CONFIG):
            raise RuntimeError("MCP2515: config mode timeout")

        # Bit-timing table (CNF1, CNF2, CNF3)
        _timing = {
            8:  {1000:(0x00,0x80,0x00), 500:(0x00,0x90,0x02),
                  250:(0x01,0x90,0x02), 125:(0x03,0x90,0x02), 100:(0x04,0x90,0x02)},
            16: {1000:(0x00,0xD0,0x82), 500:(0x00,0xF0,0x86),
                  250:(0x41,0xF1,0x85), 125:(0x03,0xF0,0x86)},
        }
        t = _timing.get(self._crystal, {}).get(kbps)
        if t is None:
            raise ValueError(f"No timing for {kbps}kbps @ {self._crystal}MHz")
        self._wr(_CNF1, t[0]); self._wr(_CNF2, t[1]); self._wr(_CNF3, t[2])

        # Accept all frames; RXB0 rolls over to RXB1 on overflow
        self._wr(_RXB0CTRL, 0x64)
        self._wr(_RXB1CTRL, 0x60)

        # Zero acceptance masks/filters → pass everything
        for a in [0x00,0x04,0x08,0x10,0x14,0x18,0x1C,0x20,0x24]:
            self._wr(a, 0x00)

        # Enable RX0/RX1 interrupts
        self._wr(_CANINTE, 0x03)
        self._wr(_CANINTF, 0x00)

        if not self._set_mode(MODE_NORMAL):
            raise RuntimeError("MCP2515: normal mode timeout")

    # ── Receive ────────────────────────────────────────────────────────────────

    def recv(self):
        """
        Read one frame. Returns (can_id, is_ext, dlc, data:bytes) or None.
        Extended 29-bit IDs are returned as-is (no flag bit added).
        """
        if self._int is not None:
            if self._int.value():   # active-low
                return None
        status = self._qs()
        if not (status & 0x03):
            return None

        if status & 0x01:
            rd_cmd = _RDRX0;  d0 = _RXB0D0 = 0x66;  flag = 0x01
        else:
            rd_cmd = _RDRX1;  d0 = _RXB1D0 = 0x76;  flag = 0x02

        self._sel()
        self._spi.write(bytes([rd_cmd]))
        hdr = bytearray(self._spi.read(5))   # SIDH SIDL EID8 EID0 DLC
        self._desel()

        sidh, sidl, eid8, eid0, dlc_byte = hdr
        dlc    = dlc_byte & 0x0F
        is_ext = bool(sidl & 0x08)
        is_rtr = bool(dlc_byte & 0x40) if is_ext else bool(sidl & 0x10)

        if is_ext:
            can_id = (sidh << 21) | ((sidl & 0xE0) >> 3) << 18 \
                     | ((sidl & 0x03) << 16) | (eid8 << 8) | eid0
        else:
            can_id = (sidh << 3) | (sidl >> 5)

        data = b''
        if dlc > 0 and not is_rtr:
            self._sel()
            self._spi.write(bytes([_READ, d0]))
            data = bytes(self._spi.read(dlc))
            self._desel()

        self._bm(_CANINTF, flag, 0x00)   # clear interrupt flag
        return (can_id, is_ext, dlc, data)

    # ── Transmit ───────────────────────────────────────────────────────────────

    def send(self, can_id, data, extended=False):
        """Send a CAN frame. data: bytes/bytearray, max 8 bytes."""
        dlc = min(len(data), 8)
        if extended:
            sidh = (can_id >> 21) & 0xFF
            sidl = ((can_id >> 18) & 0x07) << 5 | 0x08 | ((can_id >> 16) & 0x03)
            eid8 = (can_id >> 8) & 0xFF
            eid0 = can_id & 0xFF
        else:
            sidh = (can_id >> 3) & 0xFF
            sidl = (can_id & 0x07) << 5
            eid8 = eid0 = 0

        pkt = bytearray([_LDTX0, sidh, sidl, eid8, eid0, dlc]) + bytearray(data[:dlc])
        self._sel(); self._spi.write(pkt); self._desel()
        self._sel(); self._spi.write(bytes([_RTS0])); self._desel()

    # ── Diagnostics ────────────────────────────────────────────────────────────

    def error_flags(self):  return self._rr(_EFLG)
    def error_counts(self): return (self._rr(_TEC), self._rr(_REC))
    def available(self):
        if self._int is not None: return not self._int.value()
        return bool(self._qs() & 0x03)
