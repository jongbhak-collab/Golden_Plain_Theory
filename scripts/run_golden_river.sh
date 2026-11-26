#!/usr/bin/env bash
# Reproduce the Golden River prediction (Figure 3, Table 3) from ETOPO 2022.
# Run from the repository root:  bash scripts/run_golden_river.sh
set -euo pipefail
mkdir -p build
[ -f data/etopo/ETOPO2022_30s_116E25N_139E42N.tif ] || python3 scripts/download_etopo2022_subset.py
DEM=data/etopo/ETOPO2022_30s_116E25N_139E42N.tif
python3 scripts/golden_river_route.py "$DEM" build/sl120_s10 -120 10   # main condition
python3 scripts/golden_river_route.py "$DEM" build/sl130_s10 -130 10   # sea level -130 m
python3 scripts/golden_river_route.py "$DEM" build/sl120_s0  -120 0    # no smoothing
for run in sl120_s10 sl130_s10 sl120_s0; do python3 scripts/golden_river_trace.py "$run"; done
python3 scripts/golden_river_map_original.py                            # original 2026-11-09 map (build/)
