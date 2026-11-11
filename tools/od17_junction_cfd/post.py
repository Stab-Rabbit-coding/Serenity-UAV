#!/usr/bin/env python3
"""od17_junction_cfd/post.py -- OD-17 fairing-to-wing junction CFD screen. Post-process: averaged drag, reversed-flow area, y+, and pictures (pyvista).

Workflow (S = a work directory holding asm/pod_s2_default.stl and asm/trunnion.stl renders):
    python3 geom.py S ; python3 mkcase.py S glove ; python3 mkcase.py S endplate
    run.sh S/cfd/glove ; run.sh S/cfd/endplate ; python3 post.py S glove endplate
Results and limits: docs/NACELLE_64MM_POWER_CROSSING_BRIEF.md, "Junction CFD".

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (Anthropic, Claude Opus 5.5) under the author's direction, 2026-11-11.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""
import sys
import numpy as np
import pyvista as pv
pv.OFF_SCREEN = True
S = sys.argv[1]
names = sys.argv[2:]
U, RHO = 20.58, 1.225
Q = 0.5 * RHO * U ** 2
out = {}
NU = 1.46e-5


def wall_quantities(mb):
    """Pressure + viscous force on 'body' and per-face wall shear / y+, from near-wall cells.
    tau = (nu + nut_face) * U_tangential / d  (Spalding wall function supplies nut at the face)."""
    mesh = mb['internalMesh']
    body = mb['boundary']['body'].extract_surface().compute_normals(cell_normals=True, point_normals=False,
                                                                    consistent_normals=False, auto_orient_normals=False)
    body = body.compute_cell_sizes()
    cf = body.cell_centers().points
    # OpenFOAM patch normals point out of the fluid
    nrm = body.cell_data['Normals']
    # make sure normals point out of the fluid (into the body): probe both sides
    probe_in = cf - nrm * 2e-5
    cid = mesh.find_containing_cell(probe_in)
    if (cid < 0).mean() > 0.5:
        nrm = -nrm
        cid = mesh.find_containing_cell(cf - nrm * 2e-5)
    ok = cid >= 0
    cc = mesh.cell_centers().points
    Uc = mesh.cell_data['U'][np.where(ok, cid, 0)]
    d = np.abs(np.einsum('ij,ij->i', cc[np.where(ok, cid, 0)] - cf, nrm))
    Ut = Uc - np.einsum('ij,ij->i', Uc, nrm)[:, None] * nrm
    nutf = body.cell_data['nut'] if 'nut' in body.cell_data else np.zeros(len(cf))
    tau = (NU + nutf)[:, None] * Ut / np.maximum(d, 1e-9)[:, None]
    tau[~ok] = 0.0
    pf = body.cell_data['p']
    A = body.cell_data['Area']
    Fp = RHO * (pf[:, None] * nrm * A[:, None]).sum(axis=0)
    Fv = RHO * (tau * A[:, None]).sum(axis=0)
    yplus = d * np.sqrt(np.linalg.norm(tau, axis=1)) / NU
    body.cell_data['tau'] = tau
    return body, Fp, Fv, yplus, ok.mean()


def evaluate(mb):
    body, Fp, Fv, yp, okf = wall_quantities(mb)
    c = body.cell_centers().points
    tau = body.cell_data['tau']
    area = body.cell_data['Area']
    tz = tau[:, 2]
    jx = (c[:, 0] > 0.075) & (c[:, 0] < 0.130)
    ref = (c[:, 0] > 0.130) & (c[:, 0] < 0.160)
    return dict(drag=Fp[2] + Fv[2], Fp=Fp[2], Fv=Fv[2], rev=float(area[jx & (tz < 0)].sum() * 1e6),
                jarea=float(area[jx].sum() * 1e6), ref=float((tz[ref] < 0).mean()), yp=yp, okf=okf, body=body, tz=tz)


for n in names:
    case = f'{S}/cfd/{n}'
    r = pv.OpenFOAMReader(f'{case}/case.foam')
    times = [t for t in r.time_values if t >= 1500]
    snaps = []
    for t in times:
        r.set_active_time_value(t)
        mb = r.read()
        snaps.append((t, evaluate(mb), mb))
    D = np.array([e['drag'] for _, e, _ in snaps])
    R = np.array([e['rev'] for _, e, _ in snaps])
    last_t, e, mb = snaps[-1]
    out[n] = dict(times=(min(times), max(times), len(times)), drag_N=D.mean(), drag_sd=D.std(), drag_lbf=D.mean() / 4.448,
                  CDA_mm2=D.mean() / Q * 1e6, Fp=np.mean([x['Fp'] for _, x, _ in snaps]), Fv=np.mean([x['Fv'] for _, x, _ in snaps]),
                  rev_area_mm2=R.mean(), rev_sd=R.std(), junction_area_mm2=e['jarea'], ref_frac_reversed=e['ref'],
                  yplus=(round(float(np.median(e['yp'])), 1), round(
                      float(np.percentile(e['yp'], 95)), 1)),
                  ncell=mb['internalMesh'].n_cells, probe_ok=round(float(e['okf']), 3), time=last_t)
    e['body'].cell_data['tau_stream'] = e['tz']
    out[n]['mesh'] = mb
    out[n]['body'] = e['body']
for n in names:
    o = out[n]
    print(f"{n:9s} snapshots {o['times']} cells {o['ncell']:,}  mean drag {o['drag_lbf']:.4f} lbf ({o['drag_N']:.4f} N, sd {o['drag_sd']:.4f}; pressure {o['Fp']:.4f}, "
          f"viscous {o['Fv']:.4f})  CdA {o['CDA_mm2']:.0f} mm2  reversed-flow area in the junction strip "
          f"{o['rev_area_mm2']:.0f} (sd {o['rev_sd']:.0f}) of {o['junction_area_mm2']:.0f} mm2  (clean-wing reference reversed fraction "
          f"{o['ref_frac_reversed']:.2f})  y+ median/95% {o['yplus']}  wall probes found {o['probe_ok']}")
# pictures
p = pv.Plotter(off_screen=True, shape=(2, len(names)),
               window_size=(900 * len(names), 1500), border=False)
for i, n in enumerate(names):
    b = out[n]['body'].copy()
    b.points = b.points * 1000 / 25.4
    lim = float(np.percentile(np.abs(b.cell_data['tau_stream']), 95))
    for r_, (vn, d, up) in enumerate((('TOP', (0, -1, 0), (0, 0, -1)), ('BOTTOM', (0, 1, 0), (0, 0, -1)))):
        p.subplot(r_, i)
        p.add_mesh(b, scalars='tau_stream', cmap='coolwarm', clim=(-lim, lim), show_edges=False,
                   scalar_bar_args=dict(title='streamwise wall shear, Pa (blue = reversed flow)', n_labels=3, fmt='%.1f'))
        p.add_text(f"{n.upper()}  {vn} view: flow from the top of the page; nacelle flank at X 1.89 in",
                   font_size=11, position='upper_left')
        f = np.array([4.1, 0, 5.3])
        p.camera.focal_point = f
        p.camera.position = f + 30 * np.array(d, float)
        p.camera.up = up
        p.enable_parallel_projection()
        p.camera.parallel_scale = 3.0
p.screenshot(f'{S}/cfd/junction_shear.png')
p.close()
# velocity sections at three spanwise stations, with vectors
stations = [0.083, 0.095, 0.110]
p = pv.Plotter(off_screen=True, shape=(len(names), len(stations)),
               window_size=(650 * len(stations), 520 * len(names)), border=False)
for i, n in enumerate(names):
    mesh = out[n]['mesh']['internalMesh']
    for j, xs in enumerate(stations):
        p.subplot(i, j)
        sl = mesh.slice(normal='x', origin=(xs, 0, 0.1)).cell_data_to_point_data()
        sl = sl.clip_box((xs - 0.01, xs + 0.01, -0.06, 0.06, 0.05, 0.25), invert=False)
        sl.points[:] = sl.points * 1000 / 25.4
        sl['|U| kt'] = np.linalg.norm(sl['U'], axis=1) / 0.514444
        p.add_mesh(sl, scalars='|U| kt', cmap='viridis', clim=(0, 55),
                   scalar_bar_args=dict(title='|U| kt', n_labels=3, fmt='%.0f'))
        g = sl.glyph(orient='U', scale=False, factor=0.07, tolerance=0.035)
        p.add_mesh(g, color='white')
        p.add_text(f'{n.upper()}  section at X {xs*1000/25.4:.2f} in ({xs*1000:.0f} mm); flow left to right, up is up',
                   font_size=10, position='upper_left')
        f = np.array([xs * 1000 / 25.4, 0, 5.4])
        p.camera.focal_point = f
        p.camera.position = f + np.array([30, 0, 0])
        p.camera.up = (0, -1, 0)
        p.enable_parallel_projection()
        p.camera.parallel_scale = 1.9
p.screenshot(f'{S}/cfd/junction_sections.png')
p.close()
print('pictures written')
