"""Figure: Golden Plain exposure through time from PaleoMIST 1.0 (minimal scenario, 0.25 deg).
Grayscale, Korean labels (Noto Serif CJK KR). Usage: python3 fig_area.py <pm.nc> <out.png>
"""
import sys
import numpy as np
from netCDF4 import Dataset
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

src, out = sys.argv[1], sys.argv[2]

# Korean serif font
for f in fm.findSystemFonts():
    if "NotoSerifCJK-Regular" in f or "NotoSerifCJK-Medium" in f:
        fm.fontManager.addfont(f)
plt.rcParams["font.family"] = "Noto Serif CJK KR"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.size"] = 9

d = Dataset(src)
t = -d.variables["time"][:]            # age BP
lat = d.variables["lat"][:]
lon = d.variables["lon"][:]
z = d.variables["paleo_topography"][:]
sl = d.variables["sea_level"][:]

R = 6371.0088
dl = np.deg2rad(0.25)
LON, LAT = np.meshgrid(lon, lat)
area = R**2 * dl * (np.sin(np.deg2rad(LAT + 0.125)) - np.sin(np.deg2rad(LAT - 0.125)))
z0 = z[-1]
box = (LON >= 117) & (LON <= 129.5) & (LAT >= 27) & (LAT <= 41.25)
east_sea = (LAT > 35.0) & (LON > 128.9)
mask = box & ~east_sea
water0 = (z0 <= 0) & mask

ages = np.array(t, dtype=float)
A = np.array([area[water0 & (z[k] > 0)].sum() for k in range(len(t))]) / 1e4  # 10^4 km2
ic = int(np.argmin(abs(lat - 36.0)))
jc = int(np.argmin(abs(lon - 123.5)))
rsl = np.array([sl[k, ic, jc] for k in range(len(t))])

fig = plt.figure(figsize=(6.3, 7.6), dpi=300)
gs = fig.add_gridspec(3, 4, height_ratios=[1.05, 1.0, 0.42], hspace=0.45, wspace=0.08)

# --- map panels
snap = [20000, 15000, 12500, 10000]
letters = ["가", "나", "다", "라"]
for i, age in enumerate(snap):
    k = int(np.where(ages == age)[0][0])
    ax = fig.add_subplot(gs[0, i])
    land_t = z[k] > 0
    img = np.where(land_t, np.where(z0 > 0, 2, 1), 0)   # 0 sea, 1 newly exposed shelf, 2 present land
    cmap = matplotlib.colors.ListedColormap(["#ffffff", "#b5b5b5", "#5a5a5a"])
    ax.pcolormesh(lon, lat, img, cmap=cmap, vmin=0, vmax=2, shading="nearest", rasterized=True)
    ax.contour(lon, lat, z0, levels=[0], colors="black", linewidths=0.4)
    ax.set_xlim(116.5, 131.5)
    ax.set_ylim(27.5, 41.8)
    ax.set_aspect(1.2)
    ax.set_xticks([])
    ax.set_yticks([])
    a_k = area[water0 & land_t].sum() / 1e4
    kor = {20000: "2만 년 전", 15000: "1만 5천 년 전", 12500: "1만 2천5백 년 전", 10000: "1만 년 전"}[age]
    ax.set_title(f"({letters[i]}) {kor}", fontsize=8.5, pad=3)
    ax.text(0.04, 0.04, f"해수면 {rsl[k]:.0f} m\n노출 {a_k:.0f}만 km²",
            transform=ax.transAxes, fontsize=6.6, va="bottom",
            bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=1.2))
    for s in ax.spines.values():
        s.set_linewidth(0.5)

# legend for maps (placed below first row)
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
map_handles = [Patch(facecolor="#5a5a5a", edgecolor="none", label="현재 육지"),
               Patch(facecolor="#b5b5b5", edgecolor="none", label="지금은 바다인 노출 대륙붕(황금평원)"),
               Line2D([0], [0], color="black", lw=0.6, label="현재 해안선")]

# --- time series
ax2 = fig.add_subplot(gs[1, :])
ax2.axvspan(26, 19, color="#e6e6e6", lw=0)
ax2.text(22.5, 88, "최후빙기\n최성기", ha="center", va="top", fontsize=7)
ax2.fill_between(ages / 1000, 0, A, color="#c8c8c8", step=None, lw=0, label="노출 대륙붕 면적")
ax2.plot(ages / 1000, A, color="#7a7a7a", lw=0.8)
ax2.set_xlim(50, 0)
ax2.set_ylim(0, 95)
ax2.set_ylabel("노출 면적 (만 km²)")
ax2.set_xlabel("천 년 전 (BP, 1950년 기준)")
ax3 = ax2.twinx()
ax3.plot(ages / 1000, rsl, color="black", lw=1.3, marker="o", ms=2.2, label="황해 중앙 상대해수면")
ax3.set_ylim(-130, 5)
ax3.set_ylabel("상대해수면 (m)")
h1, l1 = ax2.get_legend_handles_labels()
h2, l2 = ax3.get_legend_handles_labels()
ax2.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=7, frameon=False)
ax2.set_title("(마) 황금평원 노출 면적과 황해 중앙(123.5°E, 36°N)의 상대해수면", fontsize=8.5, pad=3)
for s in list(ax2.spines.values()) + list(ax3.spines.values()):
    s.set_linewidth(0.5)

# --- event timeline (numbered markers + list)
ax4 = fig.add_subplot(gs[2, :], sharex=ax2)
events = [
    (40.0, "티안유안인(베이징, 약 4만 년 전)"),
    (33.0, "AR33K(아무르, 약 3만 3천 년 전)"),
    (19.0, "AR19K(아무르), 동아시아 남북 분화"),
    (15.8, "피나르바시 개(튀르키예, 1만 5천8백 년 전)"),
    (14.3, "고프 동굴 개(영국, 1만 4천3백 년 전)"),
    (12.9, "하얼빈 개 미토게놈(1만 2천9백 년 전)"),
    (10.5, "제주 고산리 초창기 토기(연대 논쟁)"),
    (7.7, "악마문 동굴인(연해주, 7천7백 년 전)"),
    (6.0, "욕지도 조몬 관련 조상성(약 6천 년 전)"),
    (5.5, "울산 황성동 고래뼈 작살(기원전 4천~3천 년)"),
]
levels = [1, 1, 1, 1.0, 2.0, 1.0, 2.0, 1.0, 2.0, 3.0]
for n, ((x, lab), y) in enumerate(zip(events, levels), start=1):
    ax4.plot([x, x], [0, y - 0.32], color="black", lw=0.5)
    ax4.plot(x, 0, marker="v", color="black", ms=3)
    ax4.text(x, y, str(n), ha="center", va="center", fontsize=6.5,
             bbox=dict(boxstyle="circle,pad=0.18", facecolor="white", edgecolor="black", lw=0.5))
ax4.set_ylim(0, 3.6)
ax4.set_yticks([])
for side in ["left", "right", "top"]:
    ax4.spines[side].set_visible(False)
ax4.spines["bottom"].set_linewidth(0.5)
ax4.set_xlabel("천 년 전")
ax4.set_title("(바) 본문에서 다루는 주요 관측의 연대", fontsize=8.5, pad=3)

# layout-dependent placements
fig.canvas.draw()
pos0 = fig.axes[0].get_position()
fig.legend(handles=map_handles, loc="upper center", ncol=3, fontsize=7, frameon=False,
           bbox_to_anchor=(0.5, pos0.y0 - 0.004), handlelength=1.2, columnspacing=1.4)
pos4 = ax4.get_position()
col1 = "\n".join(f"{i}  {lab}" for i, (_, lab) in enumerate(events[:5], start=1))
col2 = "\n".join(f"{i}  {lab}" for i, (_, lab) in enumerate(events[5:], start=6))
fig.text(pos4.x0, pos4.y0 - 0.075, col1, fontsize=6.6, va="top", linespacing=1.45)
fig.text(pos4.x0 + 0.47, pos4.y0 - 0.075, col2, fontsize=6.6, va="top", linespacing=1.45)

fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
print("saved", out)
print("A (10^4 km2):", dict(zip(ages.astype(int).tolist(), np.round(A, 1).tolist())))
