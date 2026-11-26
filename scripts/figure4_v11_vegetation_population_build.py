"""Golden Plain vegetation 50 ka to present: BIOME4 mega-biomes forced by the CESM1.2 3-Ma transient run
(Zeller et al. 2023 Science; Yun et al. 2023 Clim. Past; dataset doi:10.22741/iccp.20230002, IBS ICCP).
Subset: mega_biome_mask, time index 2950..3000 (50 ka..0 ka, 1-kyr step), 117-129.5E, 27-41N, 0.5 deg."""
import json, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib import font_manager
for f in ["/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc", "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"]:
    font_manager.fontManager.addfont(f)
plt.rcParams.update({"font.family": "Noto Serif CJK KR", "svg.fonttype": "none", "axes.unicode_minus": False})

MB = np.load("megabiome_117-129.5E_27-41N_50ka-0ka.npy")   # [t,lat,lon], t=0 -> 50 ka, t=50 -> 0 ka
lat = 27 + 0.5 * np.arange(29); lon = 117 + 0.5 * np.arange(26)
LON, LAT = np.meshgrid(lon, lat)
AREA = (111.32 * 0.5) ** 2 * np.cos(np.radians(LAT))
EAST = (LON >= 129.0) & (LAT >= 35.5)          # East Sea side excluded, as in Figure 2
NOW = MB[50] >= 0
ages = 50 - np.arange(51)

NAMES = {2: "난온대림", 3: "온대림", 4: "북방림", 5: "사바나·건조 삼림", 6: "초원·건조 관목지", 9: "툰드라"}
COLS = {2: "#2f6b3a", 3: "#8db86a", 4: "#5b7d8c", 5: "#d6ad62", 6: "#efe29a", 9: "#c9c3d6"}
codes = [2, 3, 4, 5, 6, 9]
cmap = ListedColormap([COLS[c] for c in codes]); norm = BoundaryNorm([1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 9.5], cmap.N)

coast = json.load(open("ne_10m_coastline.geojson"))["features"]
def draw_coast(ax):
    for ft in coast:
        g = ft["geometry"]; L = [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"]
        for ln in L:
            a = np.array(ln)
            if a[:, 0].max() < 115 or a[:, 0].min() > 131 or a[:, 1].max() < 25 or a[:, 1].min() > 43: continue
            ax.plot(a[:, 0], a[:, 1], color="black", lw=0.8, zorder=3)

def shelf(t):
    return (MB[t] >= 0) & ~NOW & ~EAST

fig = plt.figure(figsize=(11, 13.2))
HD = np.load("human_density_tf2016_maps.npz"); hlat = 25.5 + np.arange(18); hlon = 114.5 + np.arange(18)
POP = np.genfromtxt("human_pop_box_tf2016.csv", delimiter=",", names=True)
slices = [(10, "(가) 4만 년 전", 40), (29, "(나) 2만 1천 년 전", 21), (38, "(다) 1만 2천 년 전", 12), (49, "(라) 1천 년 전", 1)]
W, H, X0, GAP, Y0 = 0.205, 0.25, 0.085, 0.022, 0.70
for i, (t, title, ka) in enumerate(slices):
    ax = fig.add_axes([X0 + i * (W + GAP), Y0, W, H])
    m = np.ma.masked_less(MB[t], 0).astype(float)
    ax.pcolormesh(np.append(lon - 0.25, lon[-1] + 0.25), np.append(lat - 0.25, lat[-1] + 0.25), m,
                  cmap=cmap, norm=norm, shading="flat", zorder=1)
    sh = shelf(t)
    if sh.any():  # outline of exposed shelf cells (Golden Plain) with light hatching
        ax.contourf(lon, lat, sh.astype(float), levels=[0.5, 1.5], colors="none", hatches=["...."], zorder=2)
    draw_coast(ax)
    hd = np.ma.masked_invalid(HD[f"ka{ka}"])
    cs = ax.contour(hlon, hlat, hd, levels=[10, 15, 20, 25], colors="#8b0010", linewidths=[0.8, 1.0, 1.3, 1.7], zorder=4)
    ax.clabel(cs, fmt="%d", fontsize=7.5, inline=True, inline_spacing=1)
    ax.set_xlim(117, 129.5); ax.set_ylim(27, 41.25); ax.set_aspect(1 / np.cos(np.radians(34)))
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(title, fontsize=13)
    a = AREA[sh].sum()
    if a > 0:
        dom = {c: AREA[sh & (MB[t] == c)].sum() for c in codes}
        fr = 100 * AREA[sh & ((MB[t] == 2) | (MB[t] == 3) | (MB[t] == 4))].sum() / a
        r = POP[POP["age_ka"] == ka][0]
        txt = f"노출 {a/1e4:.0f}만 km², 숲 {fr:.0f}%\n모의 인구 {r['pop_box_A']/1e4:.0f}만 명\n(그중 평원 {r['pop_shelf_A']/1e4:.0f}만 명)"
    else:
        r = POP[POP["age_ka"] == ka][0]
        txt = f"노출 대륙붕 없음\n모의 인구 {r['pop_box_A']/1e4:.0f}만 명"
    ax.text(0.03, 0.03, txt, transform=ax.transAxes, fontsize=8.6, va="bottom", ha="left", zorder=5,
            bbox=dict(fc="white", ec="none", alpha=0.85, pad=1.5))

# legend
lax = fig.add_axes([0.085, 0.645, 0.88, 0.035]); lax.axis("off")
import matplotlib.patches as mp
h = [mp.Patch(fc=COLS[c], ec="#555", lw=0.4, label=NAMES[c]) for c in codes]
h.append(mp.Patch(fc="white", ec="#555", lw=0.4, hatch="....", label="노출 대륙붕(황금평원)"))
h.append(plt.Line2D([], [], color="black", lw=0.9, label="현재 해안선"))
h.append(plt.Line2D([], [], color="#8b0010", lw=1.2, label="모의 인구 밀도(명/100 km²)"))
lax.legend(handles=h, loc="center", ncol=5, frameon=False, fontsize=9.5, handlelength=1.4, columnspacing=1.0)

# (마) stacked area of mega-biomes on the exposed shelf
ax = fig.add_axes([0.085, 0.37, 0.84, 0.22])
stack = np.array([[AREA[shelf(t) & (MB[t] == c)].sum() / 1e4 for t in range(51)] for c in codes])
order = [2, 3, 4, 5, 6, 9]
ax.axvspan(26, 19, color="#e6e6e6", zorder=0)
ax.text(22.5, 107, "최후빙기\n최성기", ha="center", va="top", fontsize=11, color="#333")
ax.stackplot(ages, *[stack[codes.index(c)] for c in order], colors=[COLS[c] for c in order],
             edgecolor="white", linewidth=0.3, zorder=2)
ax.plot(ages, stack.sum(0), color="black", lw=1.4, zorder=3, label="노출 대륙붕 전체")
ax.set_xlim(50, 0); ax.set_ylim(0, 110); ax.set_yticks(range(0, 101, 20))
ax.set_ylabel("면적 (만 km²)", fontsize=12); ax.set_xticklabels([])
ax.tick_params(labelsize=12)
ax.set_title("(마) 황금평원(노출 대륙붕) 위 식생대 면적의 변화, 5만 년 전~현재", fontsize=13)
ax.legend(loc="upper left", frameon=False, fontsize=11)
for s in ("top", "right"): ax.spines[s].set_visible(False)
# (바) simulated population
bx = fig.add_axes([0.085, 0.07, 0.84, 0.25])
ag = POP["age_ka"]; tot = POP["pop_box_A"] / 1e4; sh = POP["pop_shelf_A"] / 1e4
bx.axvspan(26, 19, color="#e6e6e6", zorder=0)
bx.fill_between(ag, 0, sh, color="#c9a227", alpha=0.85, lw=0, label="황금평원(노출 대륙붕) 위", zorder=2)
bx.fill_between(ag, sh, tot, color="#9aa3a6", alpha=0.8, lw=0, label="현재 육지 위", zorder=2)
bx.plot(ag, tot, color="black", lw=1.4, zorder=3, label="분석 영역 전체")
bx.plot(POP["age_ka"], POP["pop_box_B"] / 1e4, color="black", lw=0.9, ls=(0, (3, 2)), zorder=3, label="전체(늦은 출아프리카 시나리오)")
bx.set_xlim(50, 0); bx.set_ylim(0, 48)
bx.set_xlabel("천 년 전 (BP, 1950년 기준)", fontsize=13); bx.set_ylabel("모의 인구 (만 명)", fontsize=12)
bx.tick_params(labelsize=12)
bx.set_title("(바) 분석 영역의 모의 수렵채집 인구 (Timmermann and Friedrich 2016 모형)", fontsize=13)
bx.legend(loc="upper left", frameon=False, fontsize=10, ncol=2)
for s_ in ("top", "right"): bx.spines[s_].set_visible(False)
for ext in ("png", "pdf", "svg"):
    fig.savefig(f"fig_golden_plain_vegetation_population_50ka.{ext}", dpi=300)
np.savetxt("golden_plain_shelf_megabiome_area_50ka_0ka.csv",
           np.column_stack([ages, stack.T, stack.sum(0)]), delimiter=",", fmt="%.2f",
           header="age_ka," + ",".join(f"mb{c}_{NAMES[c]}_10^4km2" for c in codes) + ",total_shelf_10^4km2", comments="")
print("ok")
