"""Present-day population density around the Yellow Sea (GPW v4.11, 2020), red scale.
Data: GPWv4.11 population density 2020 (30 arc-second), as lossless zoom-6 Web Mercator tiles
from github.com/kevinstadler/gpw-v4.11 (values truncated at 4,096 per km2; higher values wrap)."""
import json
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib import font_manager
from scipy import ndimage

for f in ["/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc", "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"]:
    font_manager.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Serif CJK JP"
plt.rcParams["svg.fonttype"] = "none"

LON0, LON1, LAT0, LAT1 = 98.0, 147.0, 8.0, 46.5
G = np.load("/tmp/wp_mosaic.npy")  # 30 arc-second lon/lat grid, top row at LAT1


def merc_y(lat):
    return math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))


ny = 4800
ys = np.linspace(merc_y(LAT1), merc_y(LAT0), ny)
lats = np.degrees(np.arctan(np.sinh(ys)))
rows = np.clip(((LAT1 - lats) * 120).astype(int), 0, G.shape[0] - 1)
A = G[rows, :].copy()
A[A <= 0] = np.nan
ext = [LON0, LON1, merc_y(LAT0), merc_y(LAT1)]
bounds = [0, 1, 10, 25, 50, 100, 250, 500, 1000, 5000, 1e9]
cols = ["#fbf7f4", "#fde3d6", "#fcc3a8", "#fca07e", "#fb7a57", "#f04a37", "#d1222a", "#a5101f", "#760715", "#3f0008"]
cmap = ListedColormap(cols)
cmap.set_bad((1, 1, 1, 0))
norm = BoundaryNorm(bounds, cmap.N)

W_IN = 9.0
aspect = (ext[3] - ext[2]) / math.radians(ext[1] - ext[0])
fig = plt.figure(figsize=(W_IN, W_IN * aspect * 0.80 + 0.5))
ax = fig.add_axes([0.075, 0.045, 0.70, 0.93])
ax.set_facecolor("#dfe9ee")
import json as _j
for feat in _j.load(open("ne_10m_land.geojson"))["features"]:
    g = feat["geometry"]
    polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
    for poly in polys:
        ring = np.array(poly[0])
        if ring[:, 0].max() < LON0 - 2 or ring[:, 0].min() > LON1 + 2 or ring[:, 1].max() < LAT0 - 2 or ring[:, 1].min() > LAT1 + 2:
            continue
        lat_ = np.clip(ring[:, 1], -85, 85)
        ax.fill(np.radians(ring[:, 0]), np.log(np.tan(np.pi / 4 + np.radians(lat_) / 2)), color="#f7f4f1", lw=0, zorder=0.5)
ax.imshow(A, extent=[math.radians(ext[0]), math.radians(ext[1]), ext[2], ext[3]], cmap=cmap, norm=norm,
          interpolation="nearest", zorder=1)


def draw_geojson(path, **kw):
    g = json.load(open(path))
    for feat in g["features"]:
        geom = feat["geometry"]
        lines = []
        if geom["type"] in ("LineString",):
            lines = [geom["coordinates"]]
        elif geom["type"] == "MultiLineString":
            lines = geom["coordinates"]
        elif geom["type"] == "Polygon":
            lines = geom["coordinates"]
        elif geom["type"] == "MultiPolygon":
            lines = [r for p in geom["coordinates"] for r in p]
        for ln in lines:
            arr = np.array(ln)
            if arr[:, 0].max() < LON0 - 2 or arr[:, 0].min() > LON1 + 2 or arr[:, 1].max() < LAT0 - 2 or arr[:, 1].min() > LAT1 + 2:
                continue
            lat = np.clip(arr[:, 1], -85, 85)
            ax.plot(np.radians(arr[:, 0]), np.log(np.tan(np.pi / 4 + np.radians(lat) / 2)), **kw)


draw_geojson("ne_10m_coastline.geojson", color="#3d4a4f", lw=0.35, zorder=3)
draw_geojson("ne_10m_admin_0_boundary_lines_land.geojson", color="#5c6a70", lw=0.45, ls=(0, (3, 1.5)), zorder=3)

ax.set_xlim(math.radians(LON0), math.radians(LON1))
ax.set_ylim(merc_y(LAT0), merc_y(LAT1))
xt = list(range(100, 147, 10))
yt = [10, 20, 30, 40]
ax.set_xticks([math.radians(v) for v in xt])
ax.set_xticklabels([f"동경 {v}°" for v in xt], fontsize=10)
ax.set_yticks([merc_y(v) for v in yt])
ax.set_yticklabels([f"북위 {v}°" for v in yt], fontsize=10)
for v in xt:
    ax.axvline(math.radians(v), color="#9aa7ab", lw=0.3, zorder=2)
for v in yt:
    ax.axhline(merc_y(v), color="#9aa7ab", lw=0.3, zorder=2)
for s in ax.spines.values():
    s.set_color("#7a878b")
    s.set_linewidth(0.7)


def label(lon, lat, text, size=11, color="#33403f", weight="normal", style="normal"):
    import matplotlib.patheffects as pe
    ax.text(math.radians(lon), merc_y(lat), text, fontsize=size, color=color, ha="center", va="center",
            fontweight=weight, fontstyle=style, zorder=5, path_effects=[pe.withStroke(linewidth=2.6, foreground="white")])


sea = "#5b7480"
label(120.4, 38.9, "발해", 10.5, sea)
label(125.3, 29.5, "동중국해", 11.5, sea)
label(134.0, 40.3, "동해", 12, sea)
label(114.5, 16.5, "남중국해", 12, sea)
label(141.5, 31.0, "태평양", 12, sea)

# Golden Plain population circle (great circle, radius 750 km)
CLON, CLAT, RKM = 123.5, 35.0, 750.0
br = np.radians(np.linspace(0, 360, 721)); d = RKM / 6371.0
p1, l1 = math.radians(CLAT), math.radians(CLON)
p2 = np.arcsin(np.sin(p1) * np.cos(d) + np.cos(p1) * np.sin(d) * np.cos(br))
l2 = l1 + np.arctan2(np.sin(br) * np.sin(d) * np.cos(p1), np.cos(d) - np.sin(p1) * np.sin(p2))
import matplotlib.patheffects as pe
ax.plot(l2, np.log(np.tan(np.pi / 4 + p2 / 2)), color="#8b0010", lw=2.4, zorder=6,
        path_effects=[pe.Stroke(linewidth=4.2, foreground="white"), pe.Normal()])
ax.plot([math.radians(CLON)], [merc_y(CLAT)], marker="+", ms=11, mew=2.0, color="#8b0010", zorder=7)
label(CLON, CLAT + 1.25, "황금평원", 13.5, "#8b0010", "bold")
label(CLON, CLAT - 1.05, "(현재 황해)", 9.5, sea)
ax.annotate("반경 750 km 원 안 인구\n약 4억 7천만 명 (2020년)", xy=(math.radians(129.2), merc_y(30.3)),
            xytext=(math.radians(135.5), merc_y(27.3)), fontsize=10.5, color="#8b0010", fontweight="bold",
            ha="center", va="center", zorder=8,
            arrowprops=dict(arrowstyle="-", color="#8b0010", lw=1.0),
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#8b0010", lw=0.8))
land = "#1f2a2c"
label(108.5, 33.0, "중국", 14, land, "bold")
label(130.0, 41.3, "한반도", 11.5, land, "bold")
label(137.6, 37.4, "일본", 12, land, "bold")
label(122.6, 23.6, "대만", 10.5, land, "bold")
label(108.2, 14.2, "베트남", 11, land, "bold")

# title removed: (0.07, 0.965, "황금평원을 중심으로 한 동아시아의 현재 인구 밀도 (2020년)", fontsize=15, fontweight="bold", ha="left", va="top")

# legend
lax = fig.add_axes([0.80, 0.28, 0.035, 0.55])
labs = ["1 미만(0 제외)", "1~10", "10~25", "25~50", "50~100", "100~250", "250~500", "500~1,000", "1,000~5,000", "5,000 이상"]
for i, (c, t) in enumerate(zip(cols, labs)):
    lax.add_patch(plt.Rectangle((0, i), 1, 1, facecolor=c, edgecolor="#6b777b", lw=0.4))
    lax.text(1.35, i + 0.5, t, va="center", fontsize=10)
lax.set_xlim(0, 1)
lax.set_ylim(0, len(cols))
lax.axis("off")
fig.text(0.80, 0.86, "인구 밀도\n(명/km²)", fontsize=11, fontweight="bold", va="bottom")
pass  # source note moved to caption
for ext_ in ("png", "pdf", "svg"):
    fig.savefig(f"wp_popdensity_golden_plain_circle_2020.{ext_}", dpi=300)
print("saved")
