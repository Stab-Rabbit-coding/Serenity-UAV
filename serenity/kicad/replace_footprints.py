#!/usr/bin/env python3
"""Replace placeholder IC footprints in KiCad PCB files with proper library footprints."""

import sys
import os
import pcbnew

FP_LIB = '/usr/share/kicad/footprints'
CUSTOM_LIB = '/home/steve/Documents/Vocation/Employers/Griffing.tech/designs/Serenity-UAV/serenity/kicad/Serenity-Custom.pretty'

CAPE_A_MAP = {
    'IMU':      (FP_LIB + '/Package_LGA.pretty',     'LGA-14_3x2.5mm_P0.5mm_LayoutBorder3x4y'),
    'BARO':     (FP_LIB + '/Package_LGA.pretty',     'Bosch_LGA-8_2x2.5mm_P0.65mm_ClockwisePinNumbering'),
    'GPS':      (CUSTOM_LIB,                          'uBlox_SAM-M10Q-00B'),
    'CAN-TR':   (FP_LIB + '/Package_SO.pretty',      'SOIC-8_3.9x4.9mm_P1.27mm'),
    'RS485':    (FP_LIB + '/Package_SO.pretty',      'SOIC-8_3.9x4.9mm_P1.27mm'),
    '1553-DRV': (FP_LIB + '/Package_SO.pretty',      'SOIC-16_3.9x9.9mm_P1.27mm'),
    '1553-RCV': (FP_LIB + '/Package_SO.pretty',      'SOIC-16_3.9x9.9mm_P1.27mm'),
    'ETH1-PHY': (FP_LIB + '/Package_QFP.pretty',     'LQFP-48_7x7mm_P0.5mm'),
    'ETH2-PHY': (FP_LIB + '/Package_QFP.pretty',     'LQFP-48_7x7mm_P0.5mm'),
    'TPM':      (FP_LIB + '/Package_DFN_QFN.pretty', 'QFN-32-1EP_4x4mm_P0.4mm_EP2.65x2.65mm'),
    # 1553-XFM (SM-1553-11): through-hole transformer, no standard footprint
}

CAPE_B_EXTRA = {
    'WIFI-BT':   (CUSTOM_LIB,                         'TI_WL1837MOD'),
    'LORA':      (FP_LIB + '/RF_Module.pretty',       'HOPERF_RFM9XW_SMD'),
    'SD-WB':     (FP_LIB + '/Package_LCC.pretty',     'PLCC-20'),
    'NOR-FLASH': (FP_LIB + '/Package_SO.pretty',      'SOIC-8_3.9x4.9mm_P1.27mm'),
    'WINCH-DRV': (FP_LIB + '/Package_SO.pretty',      'HTSSOP-16-1EP_4.4x5mm_P0.65mm_EP3.4x5mm'),
    'LOAD-ADC':  (FP_LIB + '/Package_SO.pretty',      'SOIC-16_3.9x9.9mm_P1.27mm'),
    'PWM-I2C':   (FP_LIB + '/Package_SO.pretty',      'HTSSOP-28-1EP_4.4x9.7mm_P0.65mm_EP2.75x6.2mm'),
    'J_SD':      (FP_LIB + '/Connector_Card.pretty',  'microSD_HC_Hirose_DM3AT-SF-PEJM5'),
}

CAPE_B_MAP = {**CAPE_A_MAP, **CAPE_B_EXTRA}


def replace_footprints(pcb_path, ref_map, out_path=None):
    if out_path is None:
        out_path = pcb_path

    board = pcbnew.LoadBoard(pcb_path)
    fps_by_ref = {fp.GetReference(): fp for fp in board.GetFootprints()}

    # Phase 1: extract all placement data as plain Python types before any mutation
    plans = []
    for ref, (lib_path, fp_name) in ref_map.items():
        old_fp = fps_by_ref.get(ref)
        if old_fp is None:
            print(f'  skip {ref}: not in PCB')
            continue
        plans.append({
            'ref':      ref,
            'value':    old_fp.GetValue(),
            'x':        old_fp.GetX(),
            'y':        old_fp.GetY(),
            'orient':   float(old_fp.GetOrientationDegrees()),
            'flipped':  bool(old_fp.IsFlipped()),
            'lib_path': lib_path,
            'fp_name':  fp_name,
            'old_fp':   old_fp,   # held only until phase 2
        })

    # Phase 2: remove all old footprints, then clear pointer refs
    for plan in plans:
        board.Remove(plan['old_fp'])
        plan['old_fp'] = None   # drop SWIG ref — object is gone

    # Phase 3: load library footprints and add to board
    replaced, failed = [], []
    for plan in plans:
        fp = pcbnew.FootprintLoad(plan['lib_path'], plan['fp_name'])
        if fp is None:
            failed.append(f"{plan['ref']}: FootprintLoad returned None")
            continue

        fp.SetX(plan['x'])
        fp.SetY(plan['y'])
        fp.SetOrientationDegrees(plan['orient'])
        fp.SetReference(plan['ref'])
        fp.SetValue(plan['value'])
        board.Add(fp)   # must be in board before Flip() is called

        if plan['flipped']:
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        replaced.append(f"{plan['ref']}: {plan['fp_name']} ({len(list(fp.Pads()))} pads)")

    print(f"Replaced ({len(replaced)}):")
    for r in replaced:
        print(f'  {r}')
    if failed:
        print(f"Failed ({len(failed)}):")
        for f in failed:
            print(f'  {f}')

    board.Save(out_path)
    print(f'Saved: {out_path}')


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'both'
    base = os.path.dirname(os.path.abspath(__file__))
    cape_a = os.path.join(base, 'CAPE-A-1.kicad_pcb')
    cape_b = os.path.join(base, 'CAPE-B-1.kicad_pcb')

    if mode in ('a', 'both'):
        print('\n=== CAPE-A ===')
        replace_footprints(cape_a, CAPE_A_MAP)
    if mode in ('b', 'both'):
        print('\n=== CAPE-B ===')
        replace_footprints(cape_b, CAPE_B_MAP)
