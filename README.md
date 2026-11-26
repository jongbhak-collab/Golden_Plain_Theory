# Golden Plain Theory: supplementary data and code

This repository holds the data and code needed to redraw the four maps in

> 박종화 (Jong Bhak). 2026. 황금평원 이론: 황해 대륙붕에 잠긴 동아시아 인구사의 중심과 한국인의 형성 (The Golden Plain Theory: The Drowned Center of East Asian Population History on the Yellow Sea Shelf and the Formation of Koreans). 『유라시아문화』 16 (submitted).

Repository: https://github.com/jongbhak-collab/Golden_Plain_Theory

The Golden Plain is the continental shelf of the Bohai, the Yellow Sea and the northern East China Sea that lay exposed when glacial sea level fell. The paper treats this drowned lowland as a testable center of East Asian population history and of early dogs.

## What is here

| Figure | Data in this repository | Scripts | External data |
|---|---|---|---|
| 1. Modern bathymetry and literature paleochannels | `data/literature_paleochannels.geojson` | none (map made with the same layers as Figure 3) | ETOPO 2022 |
| 2. Exposure and flooding of the Golden Plain | `data/figure2_paleomist/PaleoMIST_east_asia_50ka.nc`, `exposed_area_timeseries.csv` | `compute_exposed_area.py`, `figure2_plot.py` | none |
| 3. Golden River drainage predicted from modern bathymetry | `data/figure3_golden_river/*` (predicted paths, path summary, confluences, isobaths), `data/literature_paleochannels.geojson` | `download_etopo2022_subset.py`, `run_golden_river.sh`, `golden_river_route.py`, `golden_river_trace.py`, `golden_river_map_original.py`, `figure3_restyle_*.py` | ETOPO 2022 |
| 4. Golden Plain and ancient dogs | `data/figure4_dogs/*` (dog records, Japanese wolf island range, -120 m and -200 m isobaths) | `figure4_restyle_korean.py` | ETOPO1 (base relief only) |

Final figures as printed in the paper are in `figures/` (PNG, PDF and editable SVG). The two source SVGs from which some layers were recovered are in `figures/source/`.

## Key numbers you can check

- Exposed shelf in the analysis box at 20,000 years ago: 867,700 km² (Bohai and Yellow Sea 552,774 km²; northern East China Sea 314,926 km²). Loss between 15,000 and 7,500 years ago: about 650,000 km². See `exposed_area_timeseries.csv`.
- Golden River trunk (sea level -120 m, 10 km Gaussian smoothing): 1,377 km, outlet 127.16 E, 33.50 N. Sea level -130 m: 1,408 km. No smoothing: 1,425 km. Paleo-Changjiang (separate drainage): 661 km. See `golden_river_path_summary.csv`.

## Quick start

```bash
pip install -r scripts/requirements.txt

# Figure 2 and Table 2
python3 scripts/compute_exposed_area.py
python3 scripts/figure2_plot.py data/figure2_paleomist/PaleoMIST_east_asia_50ka.nc build/Figure2.png

# Figure 3 and Table 3 (downloads about 20 MB of ETOPO 2022 from NOAA on first run)
bash scripts/run_golden_river.sh
```

All commands run from the repository root. The routing step needs `pysheds` and a few GB of memory.

## How each dataset was made

**PaleoMIST subset (Figure 2).** Subset of PaleoMIST 1.0 (Gowan et al. 2021), minimal scenario, 0.25 degree grid, 21 time slices from 50,000 years ago to present, 111-136 E and 27-43 N. A cell counts as exposed shelf when it is sea today and land at the time slice. The analysis box is 117-129.5 E, 27-41.25 N, without the East Sea (north of 35 N and east of 128.9 E). Cell areas are spherical. Relative sea level is read at 123.5 E, 36 N.

**Golden River (Figure 3).** ETOPO 2022 30 arc-second surface grid for 116-139 E, 25-42 N. The submarine part was smoothed with a 10 km Gaussian filter (a no-smoothing run is kept as a sensitivity test). Cells at or below the chosen sea level that connect to the open Pacific become ocean; enclosed basins are filled and allowed to overflow. Then priority-flood filling, flat resolution, D8 flow direction and flow accumulation (pysheds), and downstream tracing from twelve modern river mouths. The predicted paths are candidate routes implied by today's seafloor, not surveyed channels. Holocene mud, tidal erosion, glacial isostatic adjustment and tectonics are not removed. Original method notes in Korean: `golden_river_method_notes_ko.txt`.

**Literature paleochannels (Figures 1 and 3).** Channels digitized and generalized from published figures: solid lines from Song et al. (2016); blue dashed lines from Yoo et al. (2016); the blue dotted alternative paleo-Yeongsan route from KORDI (1987). Orange and teal dashed lines are conceptual connections drawn for this study to link the mapped channels to the outer shelf; they rest on no single source. These lines were recovered from the vector layers of the Figure 3 source SVG (`scripts/extract_svg_layers.py`).

**Dog records (Figure 4).** Nine selected records: six from East Asia (mitochondrial-only records from Zhang M. et al. 2024; nuclear records from Zhang S.-J. et al. 2025) and three early western Eurasian nuclear records (Bergström et al. 2026; Marsh et al. 2026). Coordinates were recovered from the marker positions in the Figure 4 source SVG by inverting each panel's lon/lat axes, so they carry about 0.05 degree uncertainty. The three western sites agree with their published locations to within that margin. Ages are rounded calibrated direct dates as printed in the figure. The Chinese name of the site plotted as "Yabeili" is not verified. The Japanese wolf island range (Honshu, Shikoku, Kyushu) is regional context after Gojobori et al. (2024), drawn with Natural Earth 1:10m land outlines; it is not a map of specimens.

## Data sources and licenses

| Data | Source | License |
|---|---|---|
| ETOPO 2022 | NOAA NCEI (2022), doi:10.25921/fd45-gt74 | US Government work, public domain |
| ETOPO1 | Amante and Eakins (2009), doi:10.7289/V5C8276M | US Government work, public domain |
| PaleoMIST 1.0 | Gowan et al. (2021), doi:10.1038/s41467-021-21469-w; data doi:10.1594/PANGAEA.905800 | CC BY 4.0 |
| Natural Earth land | naturalearthdata.com | Public domain |
| Literature channels | Song et al. (2016), doi:10.17559/TV-20160216023828; Yoo et al. (2016), doi:10.1016/j.marpetgeo.2016.03.005; KORDI (1987), report BSPE 00087-137-5 | Generalized traces; cite the original studies |
| Dog records | Zhang M. et al. (2024), doi:10.1093/molbev/msae062; Zhang S.-J. et al. (2025), doi:10.1126/science.adu2836; Bergström et al. (2026), doi:10.1038/s41586-026-10112-7; Marsh et al. (2026), doi:10.1038/s41586-026-10170-x | Cite the original studies |

Code in this repository is released under the MIT License (`LICENSE`). Figures and derived data made by the author (area time series, predicted paths, recovered layers) are released under CC BY 4.0 (`LICENSE-DATA.md`). Third-party data keep their own terms.

## Limits

- PaleoMIST at 0.25 degree is coarse; coastline detail and small islands are not resolved, and areas change with scenario and resolution.
- The Golden River depends on the modern seafloor and on grid resolution. Its test is seismic and borehole confirmation of Last Glacial incised channels along the predicted trunk.
- The dog records are selected examples, not a complete distribution or an absence map.

## 한국어 요약

이 저장소는 『유라시아문화』 16집 투고 논문 「황금평원 이론」의 그림 1~4를 다시 그리는 데 필요한 자료와 코드를 담는다. 그림 2의 노출 면적은 PaleoMIST 1.0 부분 자료와 계산 스크립트로, 그림 3의 황금강은 ETOPO 2022 내려받기 스크립트와 배수망 계산 코드, 예측 경로 GeoJSON으로 재현된다. 문헌 고하천과 개 기록, 일본늑대 분포 범위는 원본 그림의 벡터 레이어에서 좌표를 복원하였다. 예측 경로는 측량된 고하도가 아니라 현재 해저 지형이 예측하는 후보 경로이다.

## How to cite

Please cite the paper above and this repository:

> Bhak, J. (2026). Golden Plain Theory: supplementary data and code. https://github.com/jongbhak-collab/Golden_Plain_Theory

## Contact

Jong Bhak, Department of Biomedical Engineering and Korean Genomics Center, UNIST. jongbhak@unist.ac.kr
