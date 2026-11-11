#!/bin/bash
# od17_junction_cfd/run.sh -- mesh (serial snappyHexMesh), solve (4-way simpleFoam), reconstruct one case.
# Author: Steve Griffing, PE(CSE), CISSP-ISSEP, CPP. AI note: written by Claude (Anthropic, Claude Opus 5.5), 2026-11-11.
# License: MIT -- see LICENSES/MIT (SPDX-License-Identifier: MIT)
# run one case: mesh (serial snappy), solve (4-way parallel), post-process
set -o pipefail
case=$1
# shellcheck source=/dev/null
source /usr/share/openfoam/etc/bashrc >/dev/null 2>&1 || true
cd "$case" || exit 2
log() { echo "$(date +%H:%M:%S) $*" >>run.status; }
log start
surfaceFeatureExtract >log.sfe 2>&1 || {
    log FAIL sfe
    exit 3
}
blockMesh >log.blockMesh 2>&1 || {
    log FAIL blockMesh
    exit 3
}
snappyHexMesh -overwrite >log.snappy 2>&1 || {
    log FAIL snappy
    exit 3
}
log meshed
checkMesh >log.checkMesh 2>&1
log checkMesh rc=$?
decomposePar -force >log.decompose 2>&1 || {
    log FAIL decompose
    exit 3
}
mpirun --allow-run-as-root --oversubscribe -np 4 simpleFoam -parallel >log.simpleFoam 2>&1 || {
    log FAIL simpleFoam
    exit 4
}
log solved
reconstructPar -latestTime >log.reconstruct 2>&1
reconstructPar -newTimes >log.reconstruct2 2>&1
log finished
