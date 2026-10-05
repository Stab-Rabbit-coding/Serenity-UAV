#!/usr/bin/env python3
"""Commo Rev T 49 MHz radio -- design calculator and self-check.

Computes every component value in the Commo Rev T 49 MHz I/Q receiver and
VCXO-FM transmitter from OEM datasheet figures, verifies each against its
datasheet limit, and prints a Markdown report that is pasted into
``avionics/kicad/Commo/COMMO_REVT_RF_DESIGN.md``.  Re-run it after changing any
value; a failed check exits non-zero so a bad value cannot be committed
silently.

ENGINEERING REVIEW REQUIRED: every result here must be reviewed and accepted by
a licensed PE (or equivalently qualified engineer) before it is built or flown.
No FCC 47 CFR 15.235 numeric limit is asserted here; the TX conducted-power
target below is the project's existing design target (Commo.md "Regulatory
Constraints") and must be confirmed against 47 CFR Part 15 and an accredited
EMC lab [REF-FCC-003].

Frequency plan (all RF results are at the frequency stated beside them):
    RX/TX channel      49.860 MHz   provisional channel inside the 49.82-49.90
                                    MHz band; the owner sets the channel list
    RX LO              49.848 MHz   low-IF: the wanted signal lands at +12 kHz,
                                    clear of DC offset and 1/f noise
Transmission-line regime: at 49.86 MHz a board trace of up to 1 in (25.4 mm)
is about 1/160 wavelength on FR-4 (er ~ 4.3), so every on-board RF path is
electrically short (lumped).  The only distributed element is the off-board
coax to the antenna.

Sources (all in avionics/datasheets/):
    Si5351-B.pdf        Skyworks Si5351A/B/C-B Rev 1.3 (2021-08-27): Table 8
                        crystal requirements, Table 18 16-QFN pinout, VCXO
                        specifications, IDD / IDDOx, PSTEP 333 ps
    SA612A.pdf          NXP SA612A Rev 3 (2014-06-04): VCC 4.5-8 V, ICC 2.4 mA
                        typ / 3.0 max, NF 5.0 dB and Gconv 17 dB at 45 MHz,
                        Ri 1.5 kOhm || 3 pF, Ro 1.5 kOhm, external LO 200-300
                        mVpp into OSC_B (pin 6) through a DC block
    pe4259.pdf          pSemi PE4259 DOC-03694-5.01 (07/2026): 10-3000 MHz,
                        VDD 1.8-3.3 V, CTRL high = RFC-RF1, low = RFC-RF2,
                        RF pins DC-blocked, 25 kHz max switching rate
    tlv9062.pdf         TI TLV9062: 10 MHz GBW, 10 nV/rtHz, 538 uA/channel
    ECX-2236.pdf        ECS ECX-2236 crystal: CL 8 pF, ESR 60 Ohm max at
                        20-29.999 MHz, drive level 100 uW max
    0805cs.pdf          Coilcraft 0805CS: 101 = 100 nH, 181 = 180 nH,
                        221 = 220 nH, SRF 1250 / 920 / 820 MHz
    mspm0g3519-q1.pdf   TI SLASFA6B: DAC_OUT on PA15, A0_7 = PA22 (RGZ 40),
                        A1_7 = PA21 (RGZ 39), two simultaneous-sampling ADCs

Author: Claude Opus 5.5 (2026-09-29); owner sgriffing.  License: CERN-OHL-W-2.0 — see LICENSES/CERN-OHL-W 2.0 (SPDX-License-Identifier: CERN-OHL-W-2.0)
"""

import math
import sys
from typing import List, Tuple

# ---------------------------------------------------------------------------
# frequency plan
# ---------------------------------------------------------------------------
F_CH = 49.860e6            # provisional channel (owner sets final list)
F_IF = 12.0e3              # low-IF offset of the wanted signal
F_LO = F_CH - F_IF         # RX LO, I and Q
F_XTAL = 25.000e6          # ECX-2236 crystal (Si5351-B Table 8: 25-27 MHz)
VCO_MIN, VCO_MAX = 600e6, 900e6   # Si5351 PLL VCO range (datasheet section 3)

CHECKS: List[Tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str) -> None:
    """Record a pass/fail design check for the report."""
    CHECKS.append((name, ok, detail))


def e_series(value: float, series: List[float]) -> float:
    """Nearest standard value from a decade series."""
    decade = 10 ** math.floor(math.log10(value))
    cands = [s * decade * m for s in series for m in (0.1, 1, 10)]
    return min(cands, key=lambda c: abs(c - value))


E24 = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
       3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1]
E96 = [round(10 ** (i / 96), 2) for i in range(96)]


# ---------------------------------------------------------------------------
# 1. Si5351B frequency plan (PLLA = RX I/Q LOs, PLLB = VCXO TX carrier)
# ---------------------------------------------------------------------------
def pll_plan(f_out: float, div: int) -> Tuple[float, int, int, int]:
    """Integer MultiSynth divider -> VCO frequency and a+b/c feedback."""
    f_vco = f_out * div
    ratio = f_vco / F_XTAL
    a = int(ratio)
    c = 1048575               # largest 20-bit denominator
    b = round((ratio - a) * c)
    return f_vco, a, b, c


MS_DIV = 14                 # even integer MultiSynth divider for both PLLs
vco_a, a_a, b_a, c_a = pll_plan(F_LO, MS_DIV)
vco_b, a_b, b_b, c_b = pll_plan(F_CH, MS_DIV)
check("PLLA VCO in range", VCO_MIN <= vco_a <= VCO_MAX, f"{vco_a / 1e6:.4f} MHz")
check("PLLB VCO in range", VCO_MIN <= vco_b <= VCO_MAX, f"{vco_b / 1e6:.4f} MHz")
check("VCXO output <= 112.5 MHz", F_CH <= 112.5e6, "Si5351-B VCXO section")

# 90 degree I/Q offset: phase step = 1 / (4 * fVCO) (PSTEP 333 ps at 750 MHz)
pstep = 1 / (4 * vco_a)
t90 = 1 / (4 * F_LO)
phoff = t90 / pstep
phase_err = (round(phoff) - phoff) * pstep / (1 / F_LO) * 360
check("I/Q offset is an integer step count", abs(round(phoff) - phoff) < 1e-6,
      f"PHOFF = {phoff:.4f} steps (= MS divider), error {phase_err:.4f} deg")

# ---------------------------------------------------------------------------
# 2. VCXO FM deviation from the MCU DAC
# ---------------------------------------------------------------------------
DEV_HZ = 3.0e3              # peak deviation (narrowband FM AFSK; owner/EMC to confirm)
ppm_per_hz = 1e6 / F_CH
dev_ppm = DEV_HZ * ppm_per_hz
KV = 100.0                  # ppm/V chosen from the 18-150 ppm/V configurable range
v_swing = dev_ppm / KV
VDD = 3.3
vc_lo, vc_hi = 0.1 * VDD, 0.9 * VDD      # linear window, Si5351-B VCXO table
vc_mid = VDD / 2
check("Deviation inside pull range", dev_ppm <= 240, f"+/-{dev_ppm:.1f} ppm vs +/-30..240 ppm")
check("VC swing stays in the 10-90 % linear window",
      vc_mid - v_swing >= vc_lo and vc_mid + v_swing <= vc_hi,
      f"{vc_mid - v_swing:.3f}..{vc_mid + v_swing:.3f} V")
dac_lsb = VDD / 4096
lsb_hz = dac_lsb * KV / ppm_per_hz
# DAC reconstruction RC: pass the 2.2 kHz mark tone, stay under the 10 kHz
# VCXO modulation bandwidth, attenuate the 48 ksps DAC image.
R_VC = 1.5e3
C_VC = 8.2e-9
fc_vc = 1 / (2 * math.pi * R_VC * C_VC)
att_2k2 = 20 * math.log10(1 / math.sqrt(1 + (2.2e3 / fc_vc) ** 2))
att_48k = 20 * math.log10(1 / math.sqrt(1 + (48e3 / fc_vc) ** 2))
check("VC RC corner 10-20 kHz", 10e3 <= fc_vc <= 20e3, f"{fc_vc / 1e3:.2f} kHz")

# ---------------------------------------------------------------------------
# 3. SA612A LO injection pad (3.3 V CMOS CLK -> 200-300 mVpp at OSC_B)
# ---------------------------------------------------------------------------
R_LO_SER, R_LO_SH = 2.4e3, 200.0
v_lo = VDD * R_LO_SH / (R_LO_SER + R_LO_SH)
check("LO level at SA612A pin 6", 0.200 <= v_lo <= 0.300, f"{v_lo * 1e3:.0f} mVpp")
i_clk = VDD / (R_LO_SER + R_LO_SH)
check("CLK1/2 load current < 2 mA drive setting", i_clk < 2e-3, f"{i_clk * 1e3:.2f} mA peak")
C_LO = 1e-9
xc_lo = 1 / (2 * math.pi * F_LO * C_LO)

# ---------------------------------------------------------------------------
# 4. Ladder-filter responses (ABCD, lumped, 50 Ohm source and load)
# ---------------------------------------------------------------------------


def series_z(z: complex):
    return ((1, z), (0, 1))


def shunt_y(y: complex):
    return ((1, 0), (y, 1))


def cascade(ms):
    a, b, c, d = 1, 0, 0, 1
    for (m11, m12), (m21, m22) in ms:
        a, b, c, d = a * m11 + b * m21, a * m12 + b * m22, c * m11 + d * m21, c * m12 + d * m22
    return a, b, c, d


def s21_db(elems, f: float, z0: float = 50.0) -> float:
    a, b, c, d = cascade(elems(f))
    s21 = 2 / (a + b / z0 + c * z0 + d)
    return 20 * math.log10(abs(s21))


def l_z(l_h: float, f: float, q: float) -> complex:
    w = 2 * math.pi * f
    return complex(w * l_h / q, w * l_h)


def c_y(c_f: float, f: float) -> complex:
    return complex(0, 2 * math.pi * f * c_f)


Q_L = 40.0   # ASSUMED inductor Q at 50-250 MHz: 0805CS specifies Q min 50-65 only at 250-500 MHz


def lpf(f: float):
    """Rev S 6-element LPF, kept (Commo.md section 4); inductors now real 0805CS parts."""
    return [series_z(l_z(100e-9, f, Q_L)), shunt_y(c_y(120e-12, f)),
            series_z(l_z(180e-9, f, Q_L)), shunt_y(c_y(180e-12, f)),
            series_z(l_z(180e-9, f, Q_L)), shunt_y(c_y(120e-12, f))]


lpf_pass = s21_db(lpf, F_CH)
lpf_h2 = s21_db(lpf, 2 * F_CH)
lpf_h3 = s21_db(lpf, 3 * F_CH)
lpf_h5 = s21_db(lpf, 5 * F_CH)
check("LPF passband loss < 1.5 dB", lpf_pass > -1.5, f"{lpf_pass:.2f} dB at 49.86 MHz")
check("LPF >= 40 dB at 3rd harmonic (square-wave TX)", lpf_h3 <= -40, f"{lpf_h3:.1f} dB at 149.6 MHz")

# 2-pole top-C-coupled RX BPF, 0805CS-221 resonators.
L_BPF = 220e-9
C_RES, C_CPL, C_END = 30e-12, 3.9e-12, 15e-12   # chosen by the E24/E12 sweep in the design note


def bpf(f: float):
    ind = l_z(L_BPF, f, Q_L)
    y_res = 1 / ind + c_y(C_RES, f)
    return [series_z(1 / c_y(C_END, f)), shunt_y(y_res),
            series_z(1 / c_y(C_CPL, f)), shunt_y(y_res),
            series_z(1 / c_y(C_END, f))]


fs = [45e6 + i * 10e3 for i in range(1001)]
resp = [s21_db(bpf, f) for f in fs]
peak = max(resp)
f_peak = fs[resp.index(peak)]
band = [f for f, r in zip(fs, resp) if r >= peak - 3]
bw3 = band[-1] - band[0]
bpf_ch = s21_db(bpf, F_CH)
bpf_fm = s21_db(bpf, 88e6)
check("BPF centre within +/-1.5 MHz of channel", abs(f_peak - F_CH) < 1.5e6,
      f"peak {f_peak / 1e6:.2f} MHz, {peak:.2f} dB")
check("BPF loss at channel < 4 dB", bpf_ch > -4, f"{bpf_ch:.2f} dB at 49.86 MHz")

# ---------------------------------------------------------------------------
# 5. TX attenuator (10 dB 50 Ohm pi pad, E96)
# ---------------------------------------------------------------------------
ATT_DB = 10.0
k = 10 ** (ATT_DB / 20)
r_sh = 50 * (k + 1) / (k - 1)
r_se = 50 * (k * k - 1) / (2 * k)
r_sh_e, r_se_e = e_series(r_sh, E96), e_series(r_se, E96)

# ---------------------------------------------------------------------------
# 6. Baseband I/Q difference amplifier + anti-alias (per channel)
# ---------------------------------------------------------------------------
RO_MIX = 1.5e3              # SA612A mixer output resistance, each pin
R_IN, R_F, C_F = 10e3, 100e3, 68e-12
C_AC = 1e-6
R_POST, C_POST = 1e3, 2.2e-9
FS_ADC = 384e3              # oversample, decimate by 8 in firmware to 48 ksps
gain = R_F / (R_IN + RO_MIX)
fc_bb = 1 / (2 * math.pi * R_F * C_F)
fc_hp = 1 / (2 * math.pi * (R_IN + RO_MIX) * C_AC)
fc_post = 1 / (2 * math.pi * R_POST * C_POST)
f_alias = FS_ADC - 48e3
a_alias = (20 * math.log10(1 / math.sqrt(1 + (f_alias / fc_bb) ** 2))
           + 20 * math.log10(1 / math.sqrt(1 + (f_alias / fc_post) ** 2)))
gbw_needed = gain * fc_bb * 10
check("Channel (IF 12 kHz +/- Carson 5.2 kHz) inside baseband corner", F_IF + 5.2e3 < fc_bb,
      f"corner {fc_bb / 1e3:.1f} kHz")
check("High-pass corner far below IF", fc_hp < 200, f"{fc_hp:.1f} Hz")
check("TLV9062 GBW margin (10x)", gbw_needed < 10e6, f"needs {gbw_needed / 1e6:.2f} MHz of 10 MHz")
check("Alias attenuation at fs-48k >= 35 dB", a_alias <= -35, f"{a_alias:.1f} dB at {f_alias / 1e3:.0f} kHz")

# ---------------------------------------------------------------------------
# 7. Current budget (receive), +5 V bus
# ---------------------------------------------------------------------------
I_SA612 = 2 * 2.4e-3                     # typ, both mixers, from +5V_FILT
I_SI5351 = 24e-3 + 2 * 2.2e-3            # IDD typ + CLK1/CLK2 buffers (CLK0 off in RX)
I_OPAMP = 2 * 538e-6
I_RX_5V = I_SA612 + I_SI5351 + I_OPAMP   # 3V3 loads via TPS7A20 LDO -> same current at 5 V
I_RX_MAX = 2 * 3.0e-3 + 38e-3 + 2 * 5.6e-3 + 2 * 538e-6


def report() -> None:
    p = print
    p("## Computed values (commo_radio_design.py)\n")
    p("| Block | Quantity | Value |")
    p("|---|---|---|")
    p(f"| Plan | RX channel / LO (low-IF +{F_IF / 1e3:.0f} kHz) | {F_CH / 1e6:.3f} MHz / {F_LO / 1e6:.3f} MHz |")
    p(f"| Si5351B PLLA (RX LO) | VCO, feedback a+b/c | {vco_a / 1e6:.4f} MHz = {a_a} + {b_a}/{c_a} |")
    p(f"| Si5351B PLLB (TX, VCXO) | VCO, feedback a+b/c | {vco_b / 1e6:.4f} MHz = {a_b} + {b_b}/{c_b} |")
    p(f"| Si5351B | MultiSynth divider (both), CLK2 PHOFF | {MS_DIV}, {round(phoff)} steps = 90.00 deg |")
    p(f"| VCXO | deviation / Kv / VC swing | +/-{DEV_HZ / 1e3:.1f} kHz = +/-{dev_ppm:.1f} ppm / {KV:.0f} ppm/V / {vc_mid:.2f} +/- {v_swing:.3f} V |")
    p(f"| VCXO | DAC 12-bit LSB | {dac_lsb * 1e3:.3f} mV = {lsb_hz:.1f} Hz |")
    p(f"| VCXO | VC RC {R_VC / 1e3:.1f} kOhm / {C_VC * 1e9:.1f} nF | fc {fc_vc / 1e3:.2f} kHz; {att_2k2:.2f} dB at 2.2 kHz; {att_48k:.1f} dB at 48 kHz |")
    p(f"| LO pad | {R_LO_SER / 1e3:.1f} kOhm series, {R_LO_SH:.0f} Ohm shunt, 1 nF block | {v_lo * 1e3:.0f} mVpp at pin 6 ({xc_lo:.1f} Ohm block at {F_LO / 1e6:.2f} MHz) |")
    p(f"| LPF (0805CS-101/181/181, 120/180/120 pF) | S21 | {lpf_pass:.2f} dB at 49.86; {lpf_h2:.1f} dB at 99.7; {lpf_h3:.1f} dB at 149.6; {lpf_h5:.1f} dB at 249.3 MHz |")
    p(f"| RX BPF (0805CS-221, {C_RES * 1e12:.0f}/{C_CPL * 1e12:.1f}/{C_END * 1e12:.0f} pF) | peak, -3 dB BW, 49.86, 88 MHz | {f_peak / 1e6:.2f} MHz, {bw3 / 1e6:.2f} MHz, {bpf_ch:.2f} dB, {bpf_fm:.1f} dB |")
    p(f"| TX pad | 10 dB pi, shunt / series | {r_sh:.2f} / {r_se:.2f} Ohm -> E96 {r_sh_e:.1f} / {r_se_e:.1f} Ohm |")
    p(f"| Baseband | gain, LPF, HPF, post-RC | x{gain:.2f} ({20 * math.log10(gain):.1f} dB), {fc_bb / 1e3:.1f} kHz, {fc_hp:.1f} Hz, {fc_post / 1e3:.1f} kHz |")
    p(f"| Baseband | alias attenuation at {f_alias / 1e3:.0f} kHz (fs {FS_ADC / 1e3:.0f} ksps) | {a_alias:.1f} dB |")
    p(f"| Power | RX current at 5 V, typ / max | {I_RX_5V * 1e3:.1f} mA / {I_RX_MAX * 1e3:.1f} mA |")
    p("\n## Design checks\n")
    p("| Check | Result | Detail |")
    p("|---|---|---|")
    for name, ok, detail in CHECKS:
        p(f"| {name} | {'PASS' if ok else 'FAIL'} | {detail} |")


if __name__ == "__main__":
    report()
    if not all(ok for _, ok, _ in CHECKS):
        sys.exit(1)
