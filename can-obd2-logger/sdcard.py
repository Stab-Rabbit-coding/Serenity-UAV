# MicroPython SPI SD card block device driver
# Standard implementation compatible with os.mount() / FAT filesystem.
# Supports SD v1, SD v2 (SDSC/SDHC/SDXC), and MMC.
from machine import SPI, Pin
import time

_CMD_TIMEOUT = 100
_TOKEN_DATA  = 0xFE
_TOKEN_CMD25 = 0xFC
_TOKEN_STOP  = 0xFD


class SDCard:
    def __init__(self, spi, cs, baudrate=10_000_000):
        self.spi = spi
        self.cs  = cs
        self.cs.value(1)
        self._baudrate = baudrate
        self.sdhc    = False
        self.sectors = 0
        self._init_card()

    def _ck(self, n=1):
        return self.spi.read(n, 0xFF)

    def _cmd(self, cmd, arg, crc=0x01, final=0, release=True, skip1=False):
        self.cs.value(0)
        self.spi.write(bytes([0x40|cmd,
                               arg>>24, (arg>>16)&0xFF,
                               (arg>>8)&0xFF, arg&0xFF, crc]))
        for _ in range(_CMD_TIMEOUT):
            r = self._ck(1)[0]
            if skip1:
                skip1 = False; continue
            if not (r & 0x80):
                for _ in range(final):
                    self.spi.read(1, 0xFF)
                if release:
                    self.cs.value(1); self.spi.read(1, 0xFF)
                return r
        self.cs.value(1); self.spi.read(1, 0xFF)
        return -1

    def _cmd8(self):
        self.cs.value(0)
        self.spi.write(b'\x48\x00\x00\x01\xAA\x87')
        r = -1
        for _ in range(_CMD_TIMEOUT):
            r = self.spi.read(1, 0xFF)[0]
            if not (r & 0x80): break
        rb = bytes(self.spi.read(4, 0xFF))
        self.cs.value(1); self.spi.read(1, 0xFF)
        return r, rb

    def _cmd58(self):
        self.cs.value(0)
        self.spi.write(b'\x7A\x00\x00\x00\x00\xFF')
        r = -1
        for _ in range(_CMD_TIMEOUT):
            r = self.spi.read(1, 0xFF)[0]
            if not (r & 0x80): break
        ocr = bytes(self.spi.read(4, 0xFF))
        self.cs.value(1); self.spi.read(1, 0xFF)
        return r, ocr

    def _init_card(self):
        self.spi.init(baudrate=400_000)
        self.cs.value(1)
        self.spi.read(10, 0xFF)   # 80 clock cycles before CMD0

        r = self._cmd(0, 0, 0x95)
        if r != 0x01:
            raise OSError("SD: no response to CMD0 — check wiring")

        r, rb = self._cmd8()
        if r == 0x01 and rb[3] == 0xAA:
            # SD v2
            for _ in range(100):
                self._cmd(55, 0)
                r = self._cmd(41, 0x40000000)
                if r == 0: break
                time.sleep_ms(10)
            if r: raise OSError("SD: ACMD41 timeout (SDv2)")
            r, ocr = self._cmd58()
            self.sdhc = bool(ocr[0] & 0x40)
        else:
            # SD v1 / MMC
            for _ in range(100):
                self._cmd(55, 0); r = self._cmd(41, 0)
                if r == 0: break
                time.sleep_ms(10)
            if r:
                for _ in range(100):
                    r = self._cmd(1, 0)
                    if r == 0: break
                    time.sleep_ms(10)
            if r: raise OSError("SD: init timeout")
            self.sdhc = False

        if self._cmd(16, 512):   # SET_BLOCKLEN = 512
            raise OSError("SD: SET_BLOCKLEN failed")

        self.spi.init(baudrate=self._baudrate)
        self.sectors = self._get_sectors()

    def _get_sectors(self):
        csd = bytearray(18)
        if self._cmd(9, 0, release=False): self.cs.value(1); return 0
        for _ in range(_CMD_TIMEOUT * 10):
            if self.spi.read(1, 0xFF)[0] == _TOKEN_DATA: break
        self.spi.readinto(csd, 0xFF)
        self.cs.value(1); self.spi.read(1, 0xFF)
        csd_v = (csd[0] >> 6) & 0x03
        if csd_v == 1:
            c = (((csd[7]&0x3F)<<16)|(csd[8]<<8)|csd[9]) + 1
            return c * 1024
        n = (csd[5]&0x0F) + ((csd[9]&0x03)<<1) + ((csd[10]>>7)&1) + 2
        c = ((csd[8]>>6)&0x03) | (csd[7]<<2) | ((csd[6]&0x03)<<10)
        return (c+1) << (n-9)

    def _wait_done(self):
        for _ in range(_CMD_TIMEOUT * 5):
            if self.spi.read(1, 0xFF)[0]: return
        raise OSError("SD: write timeout")

    def readblocks(self, block, buf, offset=0):
        addr = block if self.sdhc else block * 512
        n    = len(buf) // 512
        cmd  = 17 if n == 1 else 18
        r    = self._cmd(cmd, addr, release=False)
        if r: self.cs.value(1); raise OSError(f"SD: read CMD{cmd} r={r}")
        mv = memoryview(buf)
        for i in range(n):
            for _ in range(_CMD_TIMEOUT * 10):
                if self.spi.read(1, 0xFF)[0] == _TOKEN_DATA: break
            self.spi.readinto(mv[i*512:(i+1)*512], 0xFF)
            self.spi.read(2, 0xFF)    # CRC
        if n > 1:
            self._cmd(12, 0, skip1=True)
        else:
            self.cs.value(1); self.spi.read(1, 0xFF)

    def writeblocks(self, block, buf):
        addr = block if self.sdhc else block * 512
        n    = len(buf) // 512
        mv   = memoryview(buf)
        if n == 1:
            r = self._cmd(24, addr, release=False)
            if r: self.cs.value(1); raise OSError(f"SD: WRITE r={r}")
            self.spi.write(bytes([_TOKEN_DATA]))
            self.spi.write(mv)
            self.spi.read(2, 0xFF)
            self._wait_done()
            self.cs.value(1); self.spi.read(1, 0xFF)
        else:
            r = self._cmd(25, addr, release=False)
            if r: self.cs.value(1); raise OSError(f"SD: WRITE_MULTI r={r}")
            for i in range(n):
                self.spi.write(bytes([_TOKEN_CMD25]))
                self.spi.write(mv[i*512:(i+1)*512])
                self.spi.read(2, 0xFF)
                self._wait_done()
            self.spi.write(bytes([_TOKEN_STOP]))
            self._wait_done()
            self.cs.value(1); self.spi.read(1, 0xFF)

    def ioctl(self, op, arg):
        if op == 4: return self.sectors   # block count
        if op == 5: return 512            # block size
        if op == 6: return 0              # erase (no-op)
