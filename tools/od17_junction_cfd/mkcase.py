#!/usr/bin/env python3
"""od17_junction_cfd/mkcase.py -- OD-17 fairing-to-wing junction CFD screen. Write an OpenFOAM v1912 simpleFoam case (k-omega SST, 40 kt) for one body.

Workflow (S = a work directory holding asm/pod_s2_default.stl and asm/trunnion.stl renders):
    python3 geom.py S ; python3 mkcase.py S glove ; python3 mkcase.py S endplate
    run.sh S/cfd/glove ; run.sh S/cfd/endplate ; python3 post.py S glove endplate
Results and limits: docs/NACELLE_64MM_POWER_CROSSING_BRIEF.md, "Junction CFD".

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
AI note: Written by Claude (Anthropic, Claude Opus 5.5) under the author's direction, 2026-11-11.
License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
"""
import os
import sys
import shutil
S, name = sys.argv[1], sys.argv[2]
U = 20.58          # 40 kt
NU = 1.46e-5       # ISA SL (docs/WING_ATTACH_INTERFACE.md)
K = 1.5 * (U * 0.005) ** 2
OMEGA = K / (NU * 10.0)
case = f'{S}/cfd/{name}'
shutil.rmtree(case, ignore_errors=True)
for d in ('0', 'constant/triSurface', 'system'):
    os.makedirs(f'{case}/{d}', exist_ok=True)
shutil.copy(f'{S}/cfd/{name}.stl', f'{case}/constant/triSurface/body.stl')
H = 'FoamFile { version 2.0; format ascii; class dictionary; object %s; }\n'


def w(path, obj, body, cls='dictionary'):
    open(f'{case}/{path}', 'w').write((H % obj).replace('dictionary', cls) + body)


# domain (m): X 0.048 (nacelle flank) .. 0.165 (inboard cut); Y +-0.12; Z -0.25 .. 0.55 (flow +Z)
x0, x1, y0, y1, z0, z1 = 0.048, 0.165, -0.12, 0.12, -0.25, 0.55
dx = 0.006
nx, ny, nz = round((x1 - x0) / dx), round((y1 - y0) / dx), round((z1 - z0) / dx)
w('system/blockMeshDict', 'blockMeshDict', f'''convertToMeters 1;
vertices ( ({x0} {y0} {z0}) ({x1} {y0} {z0}) ({x1} {y1} {z0}) ({x0} {y1} {z0})
           ({x0} {y0} {z1}) ({x1} {y0} {z1}) ({x1} {y1} {z1}) ({x0} {y1} {z1}) );
blocks ( hex (0 1 2 3 4 5 6 7) ({nx} {ny} {nz}) simpleGrading (1 1 1) );
boundary (
  inlet  {{ type patch; faces ((0 1 2 3)); }}
  outlet {{ type patch; faces ((4 5 6 7)); }}
  flank  {{ type slip;  faces ((0 3 7 4)); }}
  root   {{ type slip;  faces ((1 2 6 5)); }}
  far    {{ type slip;  faces ((0 1 5 4) (3 2 6 7)); }}
);
''')
w('system/surfaceFeatureExtractDict', 'surfaceFeatureExtractDict', '''body.stl { extractionMethod extractFromSurface; extractFromSurfaceCoeffs { includedAngle 150; } writeObj no; }
''')
w('system/snappyHexMeshDict', 'snappyHexMeshDict', f'''castellatedMesh true; snap true; addLayers true;
geometry {{
  body.stl {{ type triSurfaceMesh; name body; }}
  junction {{ type searchableBox; min (0.048 -0.045 0.06); max (0.135 0.045 0.25); }}
  wake {{ type searchableBox; min (0.048 -0.03 0.15); max (0.135 0.03 0.35); }}
}};
castellatedMeshControls {{
  maxLocalCells 3000000; maxGlobalCells 9000000; minRefinementCells 10; maxLoadUnbalance 0.10; nCellsBetweenLevels 3;
  features ( {{ file "body.eMesh"; level 4; }} );
  refinementSurfaces {{ body {{ level (3 4); patchInfo {{ type wall; }} }} }}
  resolveFeatureAngle 30;
  refinementRegions {{ junction {{ mode inside; levels ((1E15 2)); }} wake {{ mode inside; levels ((1E15 2)); }} }}
  locationInMesh (0.06 0.10 -0.20);
  allowFreeStandingZoneFaces true;
}}
snapControls {{ nSmoothPatch 3; tolerance 2.0; nSolveIter 50; nRelaxIter 5; nFeatureSnapIter 10; implicitFeatureSnap false; explicitFeatureSnap true; multiRegionFeatureSnap false; }}
addLayersControls {{
  relativeSizes true; layers {{ body {{ nSurfaceLayers 3; }} }}
  expansionRatio 1.2; finalLayerThickness 0.4; minThickness 0.1; nGrow 0; featureAngle 60; slipFeatureAngle 30;
  nRelaxIter 3; nSmoothSurfaceNormals 1; nSmoothNormals 3; nSmoothThickness 10; maxFaceThicknessRatio 0.5;
  maxThicknessToMedialRatio 0.3; minMedianAxisAngle 90; nBufferCellsNoExtrude 0; nLayerIter 50;
}}
meshQualityControls {{
  maxNonOrtho 65; maxBoundarySkewness 20; maxInternalSkewness 4; maxConcave 80; minVol 1e-13; minTetQuality 1e-15;
  minArea -1; minTwist 0.02; minDeterminant 0.001; minFaceWeight 0.05; minVolRatio 0.01; minTriangleTwist -1;
  nSmoothScale 4; errorReduction 0.75;
}}
mergeTolerance 1e-6;
''')
w('system/decomposeParDict', 'decomposeParDict',
  'numberOfSubdomains 4; method hierarchical; hierarchicalCoeffs { n (2 2 1); delta 0.001; order xyz; }\n')
# No function objects: in the Ubuntu 24.04 openfoam 1912 package every function object fails at the
# first iteration with an IOstream "sha1" error, so forces, wall shear and y+ are computed by post.py
# from the near-wall cells.  2000 iterations, written every 50 so post.py can average 1500..2000.
w('system/controlDict', 'controlDict', '''application simpleFoam; startFrom latestTime; startTime 0; stopAt endTime; endTime 2000; deltaT 1;
writeControl timeStep; writeInterval 50; purgeWrite 0; writeFormat binary; writePrecision 8; writeCompression off;
timeFormat general; timePrecision 6; runTimeModifiable true;
functions { }
''')
w('system/fvSchemes', 'fvSchemes', '''ddtSchemes { default steadyState; }
gradSchemes { default Gauss linear; grad(U) cellLimited Gauss linear 1; grad(k) cellLimited Gauss linear 1; grad(omega) cellLimited Gauss linear 1; }
divSchemes { default none; div(phi,U) bounded Gauss linearUpwind grad(U); div(phi,k) bounded Gauss upwind; div(phi,omega) bounded Gauss upwind; div((nuEff*dev2(T(grad(U))))) Gauss linear; }
laplacianSchemes { default Gauss linear limited corrected 0.5; }
interpolationSchemes { default linear; }
snGradSchemes { default limited corrected 0.5; }
wallDist { method meshWave; }
''')
w('system/fvSolution', 'fvSolution', '''solvers {
  p { solver GAMG; tolerance 1e-7; relTol 0.05; smoother GaussSeidel; }
  "(U|k|omega)" { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-8; relTol 0.1; }
}
SIMPLE { nNonOrthogonalCorrectors 1; consistent yes; residualControl { p 1e-5; U 1e-6; "(k|omega)" 1e-6; } }
relaxationFactors { equations { U 0.7; ".*" 0.5; } fields { p 0.5; } }
''')
w('constant/transportProperties', 'transportProperties',
  f'transportModel Newtonian; nu [0 2 -1 0 0 0 0] {NU};\n')
w('constant/turbulenceProperties', 'turbulenceProperties',
  'simulationType RAS; RAS { RASModel kOmegaSST; turbulence on; printCoeffs on; }\n')


def field(fn, cls, dim, internal, inlet, outlet, wall):
    w(f'0/{fn}', fn, f'''dimensions {dim};
internalField {internal};
boundaryField {{
  inlet {{ {inlet} }}
  outlet {{ {outlet} }}
  "(flank|root|far)" {{ type slip; }}
  body {{ {wall} }}
}}
''', cls)


field('U', 'volVectorField', '[0 1 -1 0 0 0 0]', f'uniform (0 0 {U})', f'type fixedValue; value uniform (0 0 {U});',
      f'type inletOutlet; inletValue uniform (0 0 0); value uniform (0 0 {U});', 'type noSlip;')
field('p', 'volScalarField', '[0 2 -2 0 0 0 0]', 'uniform 0',
      'type zeroGradient;', 'type fixedValue; value uniform 0;', 'type zeroGradient;')
field('k', 'volScalarField', '[0 2 -2 0 0 0 0]', f'uniform {K}', f'type fixedValue; value uniform {K};',
      f'type inletOutlet; inletValue uniform {K}; value uniform {K};', f'type kqRWallFunction; value uniform {K};')
field('omega', 'volScalarField', '[0 0 -1 0 0 0 0]', f'uniform {OMEGA}', f'type fixedValue; value uniform {OMEGA};',
      f'type inletOutlet; inletValue uniform {OMEGA}; value uniform {OMEGA};', f'type omegaWallFunction; value uniform {OMEGA};')
field('nut', 'volScalarField', '[0 2 -1 0 0 0 0]', 'uniform 0', 'type calculated; value uniform 0;', 'type calculated; value uniform 0;',
      'type nutUSpaldingWallFunction; value uniform 0;')
open(f'{case}/case.foam', 'w').close()
print('case', case, 'background cells', nx * ny * nz, 'k', K, 'omega', OMEGA)
