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
| 4. Golden Plain, ancient dogs and Japanese wolf samples | `data/figure4_dogs/dog_records.csv` (19 dated dog records), `japanese_wolf_samples.csv` (14 sample localities), `japanese_wolf_island_range.geojson`, -120 m and -200 m isobaths | `figure4_restyle_korean.py`, then `figure4_v8_build.py` (site table in `figure4_v8_sites.py`) | ETOPO1 (base relief only) |

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

# Figure 4 (from the English source SVG)
python3 scripts/figure4_restyle_korean.py figures/source/Figure4_source_en.svg build/fig4_ko.svg
python3 scripts/figure4_v8_build.py build/fig4_ko.svg build/Figure4.svg
```

All commands run from the repository root. The routing step needs `pysheds` and a few GB of memory.

## How each dataset was made

**PaleoMIST subset (Figure 2).** Subset of PaleoMIST 1.0 (Gowan et al. 2021), minimal scenario, 0.25 degree grid, 21 time slices from 50,000 years ago to present, 111-136 E and 27-43 N. A cell counts as exposed shelf when it is sea today and land at the time slice. The analysis box is 117-129.5 E, 27-41.25 N, without the East Sea (north of 35 N and east of 128.9 E). Cell areas are spherical. Relative sea level is read at 123.5 E, 36 N.

**Golden River (Figure 3).** ETOPO 2022 30 arc-second surface grid for 116-139 E, 25-42 N. The submarine part was smoothed with a 10 km Gaussian filter (a no-smoothing run is kept as a sensitivity test). Cells at or below the chosen sea level that connect to the open Pacific become ocean; enclosed basins are filled and allowed to overflow. Then priority-flood filling, flat resolution, D8 flow direction and flow accumulation (pysheds), and downstream tracing from twelve modern river mouths. The predicted paths are candidate routes implied by today's seafloor, not surveyed channels. Holocene mud, tidal erosion, glacial isostatic adjustment and tectonics are not removed. Original method notes in Korean: `golden_river_method_notes_ko.txt`.

**Literature paleochannels (Figures 1 and 3).** Channels digitized and generalized from published figures: solid lines from Song et al. (2016); blue dashed lines from Yoo et al. (2016); the blue dotted alternative paleo-Yeongsan route from KORDI (1987). Orange and teal dashed lines are conceptual connections drawn for this study to link the mapped channels to the outer shelf; they rest on no single source. These lines were recovered from the vector layers of the Figure 3 source SVG (`scripts/extract_svg_layers.py`).

**Dog records (Figure 4, panels A-C).** Nineteen selected dated records: seven from China, three from Korea, six from Japan and three early western Eurasian nuclear records. Nuclear-genome records: Yabeili and Jinchankou (Zhang S.-J. et al. 2025), Neukdo and Bonghwang-dong (low-coverage genomes, Kim H. et al. 2026) and the three western sites (Bergström et al. 2026; Marsh et al. 2026). Mitochondrial records: Harbin, Xinglong, Jingtoushan and Jiaojia (Zhang M. et al. 2024), Dadunzi in Yunnan (Zhang S.-J. et al. 2026), Kamikuroiwa, Odake, Mukaidai and Suwada (Xiaokaiti et al. 2024), Higashimyo (partial control region, Masuda and Sato 2015) and WolseongDog-1 (author's group, unpublished). Natsushima, the oldest dog in Japan (about 9,300 years ago), is a morphological record without DNA. Coordinates are published site coordinates where available; others are site or island representative points, and the precision of each point is stated in `coordinate_basis`. The Harbin dog was recovered from a river bottom without a reported findspot, so it is drawn near Harbin with a dashed ring. Ages are calibrated years before 1950 or archaeological periods, as stated in `age_basis`. The Chinese name of the site plotted as "Yabeili" is not verified.

**Japanese wolf samples (Figure 4A).** Sample localities of Japanese wolves with DNA data, from Matsumura et al. (2021, Table 1) and Ishiguro et al. (2009); the six genome-sequenced localities follow Gojobori et al. (2024), and the 35,000-year-old Pleistocene wolf from Sano, Tochigi follows Segawa et al. (2022). Most localities are recorded only at prefecture level, so each point is a representative point inside the prefecture, chosen to avoid overplotting. Specimens without a recorded locality (Leiden and Berlin collections) are not plotted. The purple island range (Honshu, Shikoku, Kyushu) is regional context, drawn with Natural Earth 1:10m land outlines.

## Data sources and licenses

| Data | Source | License |
|---|---|---|
| ETOPO 2022 | NOAA NCEI (2022), doi:10.25921/fd45-gt74 | US Government work, public domain |
| ETOPO1 | Amante and Eakins (2009), doi:10.7289/V5C8276M | US Government work, public domain |
| PaleoMIST 1.0 | Gowan et al. (2021), doi:10.1038/s41467-021-21469-w; data doi:10.1594/PANGAEA.905800 | CC BY 4.0 |
| Natural Earth land | naturalearthdata.com | Public domain |
| Literature channels | Song et al. (2016), doi:10.17559/TV-20160216023828; Yoo et al. (2016), doi:10.1016/j.marpetgeo.2016.03.005; KORDI (1987), report BSPE 00087-137-5 | Generalized traces; cite the original studies |
| Dog records | Zhang M. et al. (2024), doi:10.1093/molbev/msae062; Zhang S.-J. et al. (2025), doi:10.1126/science.adu2836; Zhang S.-J. et al. (2026), doi:10.1186/s12862-026-02611-y; Kim H. et al. (2026), doi:10.1371/journal.pone.0346864; Xiaokaiti et al. (2024), doi:10.1537/ase.230617; Masuda and Sato (2015), doi:10.1537/ase.150111; Bergström et al. (2026), doi:10.1038/s41586-026-10112-7; Marsh et al. (2026), doi:10.1038/s41586-026-10170-x | Cite the original studies |
| Japanese wolf samples | Ishiguro et al. (2009), doi:10.2108/zsj.26.765; Matsumura et al. (2021), doi:10.2108/zs200019; Segawa et al. (2022), doi:10.1016/j.cub.2022.04.034; Gojobori et al. (2024), doi:10.1038/s41467-024-46124-y | Cite the original studies |

Code in this repository is released under the MIT License (`LICENSE`). Figures and derived data made by the author (area time series, predicted paths, recovered layers) are released under CC BY 4.0 (`LICENSE-DATA.md`). Third-party data keep their own terms.

## Limits

- PaleoMIST at 0.25 degree is coarse; coastline detail and small islands are not resolved, and areas change with scenario and resolution.
- The Golden River depends on the modern seafloor and on grid resolution. Its test is seismic and borehole confirmation of Last Glacial incised channels along the predicted trunk.
- The dog records are selected examples, not a complete distribution or an absence map.

## 한국어 요약

이 저장소는 『유라시아문화』 16집 투고 논문 「황금평원 이론」의 그림 1~4를 다시 그리는 데 필요한 자료와 코드를 담는다. 그림 2의 노출 면적은 PaleoMIST 1.0 부분 자료와 계산 스크립트로, 그림 3의 황금강은 ETOPO 2022 내려받기 스크립트와 배수망 계산 코드, 예측 경로 GeoJSON으로 재현된다. 문헌 고하천은 원본 그림의 벡터 레이어에서 좌표를 복원하였다. 그림 4의 개 기록 19건과 일본늑대 표본 산지 14곳은 문헌 좌표와 대표점으로 정리하였고, 정밀도를 표에 적었다. 예측 경로는 측량된 고하도가 아니라 현재 해저 지형이 예측하는 후보 경로이다.

## How to cite

Please cite the paper above and this repository:

> Bhak, J. (2026). Golden Plain Theory: supplementary data and code. https://github.com/jongbhak-collab/Golden_Plain_Theory

## Contact

Jong Bhak, Department of Biomedical Engineering and Korean Genomics Center, UNIST. jongbhak@unist.ac.kr

## v9 additions (manuscript Figures 4 and 5; dog figure is now Figure 6)

- `data/figure4_vegetation/`: BIOME4 mega-biome subset (117-129.5E, 27-41N, 0.5 deg, 50 ka to 0 ka at 1-kyr steps) from the IBS ICCP 3-Ma CESM1.2/BIOME4 run (Zeller et al. 2023 Science; Yun et al. 2023 Clim. Past; dataset doi:10.22741/iccp.20230002, variable `mega_biome_mask`, time index 2950-3000). Codes: 2 warm-temperate forest, 3 temperate forest, 4 boreal forest, 5 savanna/dry woodland, 6 grassland/dry shrubland, 9 tundra, -1 ocean. `megabiome_enc.txt` is a compact text encoding; `scripts/figure4_v9_vegetation_decode.py` rebuilds the `.npy` (checksum 459023). The CSV gives mega-biome area on the exposed shelf per kyr.
- `data/figure5_population/`: population inside great circles around the Golden Plain center from WorldPop 2020 1 km unconstrained grids (doi:10.5258/SOTON/WP00674). Raw rasters are not included; `scripts/figure5_v9_worldpop_mosaic.py` mosaics the 12 national files.

## v10 additions

- `scripts/shoreline_displacement.py`: horizontal distance between the 20 ka and present shorelines in PaleoMIST 1.0 (minimal, 0.25 deg). Results quoted in the manuscript: inner Bohai coast near Tianjin about 930 km, Korean west coast up to about 290 km, Korean east coast up to about 50 km.
- Folder names follow the figure numbers used when each figure was first added. In manuscript v9/v10, `data/figure4_dogs` is Figure 6, `data/figure4_vegetation` is Figure 4, and `data/figure5_population` is Figure 5.
- Manuscript v10 cites commit `63ace02` as the repository state that matches it.

## v11 additions

- `data/figure4_population_model/`: simulated hunter-gatherer density from the Timmermann and Friedrich (2016, Nature 538:92-95) human dispersal model (IBS ICCP dataset `human-dispersal-simulation/human-density`, 1 deg, 1-kyr snapshots). `human_pop_box_tf2016.csv` sums individuals in the analysis box (117-129.5E, 27-41.5N, East Sea side excluded) for 1-50 ka, split into cells that are sea in the model at 1 ka (exposed shelf) and the rest; scenarios A (early exit) and B (late exit). `human_density_tf2016_enc.txt` holds integer-rounded maps for 40, 21, 12 and 1 ka (scenario A) used in Figure 4.
- Figure 5 circle radius is now 750 km (469 million people in 2020).
