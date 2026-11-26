"""Figure 1 (v13): the Golden Plain at 20 ka in one map. Rivers (Figure 3 drainage model), BIOME4 mega-biomes (20 ka),
simulated hunter-gatherer density (Timmermann & Friedrich 2016, 20 ka), and the population-weighted center of the plain."""
import json, csv, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.patheffects as pe, matplotlib.patches as mp
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib import font_manager
for f in ["/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc", "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"]:
    font_manager.fontManager.addfont(f)
plt.rcParams.update({"font.family": "Noto Serif CJK KR", "svg.fonttype": "none", "axes.unicode_minus": False})
MB = np.load("megabiome_117-129.5E_27-41N_50ka-0ka.npy")[30]      # 20 ka
lat = 27 + 0.5 * np.arange(29); lon = 117 + 0.5 * np.arange(26)
NAMES = {2: "난온대림", 3: "온대림", 4: "북방림", 5: "사바나·건조 삼림", 6: "초원·건조 관목지", 9: "툰드라"}
COLS = {2: "#7fae84", 3: "#c3dcae", 4: "#a9bcc6", 5: "#e6cf9f", 6: "#f4ecc0", 9: "#dedbe6"}
codes = [2, 3, 4, 5, 6, 9]
cmap = ListedColormap([COLS[c] for c in codes]); norm = BoundaryNorm([1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 9.5], cmap.N)
HD = np.array([[np.nan if v == "x" else float(v) / 10 for v in L.split()] for L in open("human_density_tf2016_20ka.txt") if not L.startswith("#")])
hlat = 23.5 + np.arange(22); hlon = 112.5 + np.arange(23)
# population-weighted center of the exposed plain (cells that are land at 20 ka and sea at 1 ka in the model; computed on the full-precision grid)
CEN = (123.82, 33.62)

fig = plt.figure(figsize=(9, 10.6)); ax = fig.add_axes([0.07, 0.17, 0.88, 0.80])
ax.set_facecolor("#dfe9ee")
ax.pcolormesh(np.append(lon - 0.25, lon[-1] + 0.25), np.append(lat - 0.25, lat[-1] + 0.25), np.ma.masked_less(MB, 0).astype(float),
              cmap=cmap, norm=norm, shading="flat", zorder=1)
halo = lambda w: [pe.Stroke(linewidth=w, foreground="white"), pe.Normal()]
def lines(geom):
    return [geom["coordinates"]] if geom["type"] == "LineString" else geom["coordinates"]
for ft in json.load(open("ne_10m_coastline.geojson"))["features"]:
    for ln in lines(ft["geometry"]):
        a = np.array(ln)
        if a[:, 0].max() < 115 or a[:, 0].min() > 132 or a[:, 1].max() < 25 or a[:, 1].min() > 43: continue
        ax.plot(a[:, 0], a[:, 1], color="#222", lw=0.7, zorder=3)
for ft in json.load(open("figure3_isobaths_0_50_100_120_140m.geojson"))["features"]:
    if ft["properties"]["elevation_m"] == -120:
        for ln in lines(ft["geometry"]):
            a = np.array(ln); ax.plot(a[:, 0], a[:, 1], color="#555", lw=1.0, ls=(0, (4, 2)), zorder=3)
for ft in json.load(open("literature_paleochannels.geojson"))["features"]:
    if ft["properties"]["evidence"] == "interpreted_channel":
        a = np.array(ft["geometry"]["coordinates"]); ax.plot(a[:, 0], a[:, 1], color="#111", lw=0.9, zorder=4)
RIV = "#0b3d91"
for ft in json.load(open("golden_river_predicted_paths.geojson"))["features"]:
    p = ft["properties"]
    if p["sea_level_m"] != -120 or p["smoothing"] != "10 km Gaussian": continue
    a = np.array(ft["geometry"]["coordinates"]); trunk = "본류" in p["name"]
    ax.plot(a[:, 0], a[:, 1], color=RIV, lw=3.0 if trunk else 1.5, zorder=5, path_effects=halo(4.6 if trunk else 2.6), solid_capstyle="round")
cs = ax.contour(hlon, hlat, np.ma.masked_invalid(HD), levels=[15, 20, 23, 25, 27], colors="#b0121f", linewidths=[0.9, 1.1, 1.3, 1.6, 2.0], zorder=6)
ax.clabel(cs, fmt="%d", fontsize=8.5, inline=True, inline_spacing=2)
ax.plot(*CEN, marker="*", ms=24, mfc="#f5c518", mec="#8b0010", mew=1.6, zorder=9)
def T(x, y, s, size=10, color="#1f2a2c", weight="normal", **k):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=k.pop("ha", "center"), va="center", zorder=10, path_effects=halo(2.6), **k)
T(CEN[0] - 0.15, CEN[1] - 0.75, "황금평원 중심\n(모의 인구 무게중심)", 10.5, "#8b0010", "bold")
T(123.35, 36.6, "황금강", 13, RIV, "bold", rotation=-62)
T(124.6, 29.9, "고장강", 10.5, RIV, "bold", rotation=-48)
for x, y, s in [(121.9, 39.25, "고요하"), (124.3, 38.75, "고압록강"), (125.0, 37.35, "고한강"), (125.75, 35.55, "고금강"), (122.2, 33.85, "고회하"), (119.6, 38.2, "고황하")]:
    T(x, y, s, 8.8, RIV)
T(126.55, 33.38, "제주", 9.5, weight="bold"); T(127.6, 37.0, "한반도", 12, weight="bold"); T(118.6, 36.4, "산둥", 10.5, weight="bold")
T(118.3, 31.0, "중국", 12, weight="bold"); T(129.2, 32.2, "규슈", 10, weight="bold"); T(128.6, 28.6, "오키나와 해곡", 9.5, "#5b7480"); T(129.3, 38.6, "동해", 11, "#5b7480")
ax.set_xlim(116.75, 129.75); ax.set_ylim(26.75, 41.25); ax.set_aspect(1 / np.cos(np.radians(34)))
ax.set_xticks(range(118, 130, 2)); ax.set_xticklabels([f"동경 {v}°" for v in range(118, 130, 2)], fontsize=10)
ax.set_yticks(range(28, 42, 2)); ax.set_yticklabels([f"북위 {v}°" for v in range(28, 42, 2)], fontsize=10)
h = [mp.Patch(fc=COLS[c], ec="#777", lw=0.4, label=NAMES[c]) for c in codes if (MB == c).any()]
h += [plt.Line2D([], [], color=RIV, lw=3, label="황금강 예측 본류(해수면 -120 m)"), plt.Line2D([], [], color=RIV, lw=1.5, label="예측 지류와 고장강"),
      plt.Line2D([], [], color="#111", lw=0.9, label="문헌 하도(Song 등 2016)"), plt.Line2D([], [], color="#555", lw=1.0, ls=(0, (4, 2)), label="2만 년 전 해안선(-120 m 등심선)"),
      plt.Line2D([], [], color="#222", lw=0.7, label="현재 해안선"), plt.Line2D([], [], color="#b0121f", lw=1.6, label="모의 인구 밀도(명/100 km²)"),
      plt.Line2D([], [], marker="*", ms=15, mfc="#f5c518", mec="#8b0010", lw=0, label="황금평원 중심")]
fig.legend(handles=h, loc="lower center", ncol=3, frameon=False, fontsize=9.5, bbox_to_anchor=(0.51, 0.015), handlelength=2.0, columnspacing=1.2)
for e in ("png", "pdf", "svg"): fig.savefig(f"fig1_golden_plain_20ka_summary.{e}", dpi=300)
print("ok")
