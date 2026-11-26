"""Final map: predicted Golden River (bathymetry-routed) over ETOPO 2022, with literature channels."""
import json, numpy as np, rasterio, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.colors import LightSource, ListedColormap
from matplotlib.lines import Line2D
from scipy import ndimage
import matplotlib.patheffects as pe

for f in ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc']:
    try: fm.fontManager.addfont(f)
    except Exception as e: print('font', e)
plt.rcParams['font.family'] = ['Noto Sans CJK KR', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

src = rasterio.open('data/etopo/ETOPO2022_30s_116E25N_139E42N.tif'); dem = src.read(1).astype(float); tr = src.transform
H, W = dem.shape
lons = tr.c + tr.a*(np.arange(W)+0.5); lats = tr.f + tr.e*(np.arange(H)+0.5)
ext = [tr.c, tr.c + tr.a*W, tr.f + tr.e*H, tr.f]
MAIN = 'sl120_s10'; RAW = 'sl120_s0'; ALT = 'sl130_s10'
acc = np.load(f'build/{MAIN}_acc.npy'); land = np.load(f'build/{MAIN}_land.npy'); fdir = np.load(f'build/{MAIN}_fdir.npy')
paths_main = json.load(open(f'build/{MAIN}_paths.geojson'))
paths_raw = json.load(open(f'build/{RAW}_paths.geojson'))
paths_alt = json.load(open(f'build/{ALT}_paths.geojson'))
lit = json.load(open('data/literature_paleochannels.geojson'))

SL = -120.0
# Pacific-connected sea at SL
lab, n = ndimage.label(dem <= SL); pac = lab[int((30-tr.f)/tr.e), int((135-tr.c)/tr.a)]; sea120 = lab == pac
lab2, n2 = ndimage.label(dem <= -140); pac2 = lab2[int((30-tr.f)/tr.e), int((135-tr.c)/tr.a)]; sea140 = lab2 == pac2

X0, X1, Y0, Y1 = 117.0, 131.0, 27.0, 41.0
fig = plt.figure(figsize=(13, 14.6), facecolor='white')
ax = fig.add_axes([0.07, 0.17, 0.90, 0.76])
ax.set_facecolor('white')

# hillshade of full relief
ls = LightSource(azdeg=315, altdeg=40)
z_for_shade = np.where(dem < -1500, -1500, dem)
shade = ls.hillshade(z_for_shade, vert_exag=0.02, dx=1, dy=1)
ax.imshow(shade, extent=ext, cmap='gray', vmin=0.2, vmax=1.3, origin='upper', interpolation='bilinear')

# color layers: modern land (light grey-green), exposed shelf at -120 (gold), band -120..-140 (tan), sea (blues by depth)
rgba = np.zeros((H, W, 4))
# sea: depth-shaded blue
d = np.clip(-dem, 0, 3000)
sea_col = plt.get_cmap('Blues')(0.35 + 0.6*np.sqrt(d/3000.0))
rgba[:] = sea_col
rgba[..., 3] = 0.75
shelf = (dem > SL) & (dem < 0)
rgba[shelf] = [0.97, 0.86, 0.50, 0.70]            # exposed shelf (gold)
band = (dem > -140) & (dem <= SL)
rgba[band] = [0.80, 0.68, 0.45, 0.70]              # -120 to -140 m sensitivity band
landmask = dem >= 0
rgba[landmask] = [0.93, 0.94, 0.90, 0.55]          # modern land, let hillshade show
ax.imshow(rgba, extent=ext, origin='upper', interpolation='bilinear')

# contours: modern 0 m, -50, -100, -120, -140
ax.contour(lons, lats, dem, levels=[0], colors='#555555', linewidths=0.5)
cs = ax.contour(lons, lats, dem, levels=[-100, -50], colors='#4a6b8a', linewidths=0.35, linestyles='solid', alpha=0.8)
ax.clabel(cs, fmt=lambda v: f'{int(-v)} m', fontsize=7, colors='#4a6b8a')
ax.contour(lons, lats, dem, levels=[-120], colors='#8a5a1a', linewidths=0.7)
ax.contour(lons, lats, dem, levels=[-140], colors='#8a5a1a', linewidths=0.5, linestyles='dashed')

# routed stream network on the exposed shelf (only cells that are seafloor today), width by accumulation
cell_km2 = (111.2*tr.a*np.cos(np.deg2rad(34)))*(111.2*(-tr.e))
A = acc*cell_km2  # km2 upstream
onshelf = (dem > SL) & (dem < 0)
for thr, lw, col, alph in [(3000, 0.5, '#8a2f0a', 0.55), (15000, 0.9, '#8a2f0a', 0.75), (60000, 1.5, '#7a1f00', 0.9)]:
    m = onshelf & (A >= thr)
    rr, cc = np.where(m)
    ax.scatter(lons[cc], lats[rr], s=lw*1.6, c=col, alpha=alph, linewidths=0, marker='s', rasterized=True)

# trunk: Golden River = path of Huang He (Yellow R.) from Bohai mouth to outlet (main run)
def get(pj, name): return np.array([f['geometry']['coordinates'] for f in pj['features'] if f['properties']['name']==name][0])
trunk = get(paths_main, 'Huang He (Yellow R.)')
trunk_raw = get(paths_raw, 'Huang He (Yellow R.)')
trunk_alt = get(paths_alt, 'Huang He (Yellow R.)')
yz = get(paths_main, 'Chang Jiang (Yangtze)'); yz_raw = get(paths_raw, 'Chang Jiang (Yangtze)')
# tributary paths (main run) until they meet the trunk
trunk_set = set(map(tuple, np.round(trunk, 4)))
trib_names = ['Liao He', 'Yalu', 'Taedong', 'Han (Korea)', 'Geum', 'Yeongsan', 'Huai (Hongze)']
for nm in trib_names:
    p = get(paths_main, nm); keep = []
    for xy in p:
        keep.append(xy)
        if tuple(np.round(xy, 4)) in trunk_set: break
    keep = np.array(keep)
    ax.plot(keep[:, 0], keep[:, 1], color='#1f4e9a', lw=2.0, solid_capstyle='round', zorder=5,
            path_effects=[pe.Stroke(linewidth=3.4, foreground='white'), pe.Normal()])
# sensitivity trunks
ax.plot(trunk_raw[:, 0], trunk_raw[:, 1], color='#c0392b', lw=1.1, ls=(0, (2, 2)), zorder=6, alpha=0.9)
ax.plot(trunk_alt[:, 0], trunk_alt[:, 1], color='#c0392b', lw=1.1, ls=(0, (5, 2)), zorder=6, alpha=0.9)
ax.plot(yz_raw[:, 0], yz_raw[:, 1], color='#0b6e4f', lw=1.1, ls=(0, (2, 2)), zorder=6, alpha=0.9)
# main trunk
ax.plot(trunk[:, 0], trunk[:, 1], color='#b8220f', lw=4.2, solid_capstyle='round', zorder=7,
        path_effects=[pe.Stroke(linewidth=6.2, foreground='white'), pe.Normal()])
ax.plot(yz[:, 0], yz[:, 1], color='#0b6e4f', lw=3.2, solid_capstyle='round', zorder=7,
        path_effects=[pe.Stroke(linewidth=5.0, foreground='white'), pe.Normal()])

# literature channels (muted)
for f in lit['features']:
    xy = np.array(f['geometry']['coordinates']); pr = f['properties']
    col = {'Huanghe': '#e07b2a', 'Changjiang': '#2a9d8f', 'Korean': '#3a6fd8'}[pr['system']]
    if pr['evidence'] == 'interpreted_channel': ax.plot(xy[:, 0], xy[:, 1], color=col, lw=1.0, alpha=0.75, zorder=4)
    elif pr['evidence'] == 'synthesis': ax.plot(xy[:, 0], xy[:, 1], color=col, lw=1.0, ls='--', alpha=0.75, zorder=4)
    else: ax.plot(xy[:, 0], xy[:, 1], color=col, lw=1.0, ls=':', alpha=0.75, zorder=4)

# confluence / key points
def star(x, y, txt, dx=0.15, dy=0.1, ha='left'):
    ax.plot(x, y, marker='o', ms=7, mfc='white', mec='#b8220f', mew=1.8, zorder=9)
    ax.text(x+dx, y+dy, txt, fontsize=9.5, ha=ha, va='bottom', zorder=9, color='#222',
            path_effects=[pe.Stroke(linewidth=2.5, foreground='white'), pe.Normal()])
star(124.76, 35.23, '고황하·고한강 합류\n(현 수심 −91 m)', dx=0.2, dy=0.05)
star(124.20, 37.71, '고황하·고압록강 합류\n(현 수심 −84 m)', dx=-0.2, dy=0.05, ha='right')
star(127.16, 33.50, '황금강 하구 (−120 m 해안선)\n제주 동쪽, 대한해협 골 머리', dx=0.25, dy=-0.75)
star(125.11, 34.25, '고회하 합류', dx=-0.2, dy=-0.5, ha='right')
star(126.27, 28.64, '고장강 하구 (−120 m)', dx=0.2, dy=0.0)

# labels
def lab(x, y, s, fs=11, col='#222', rot=0, w='bold'):
    ax.text(x, y, s, fontsize=fs, color=col, rotation=rot, ha='center', va='center', weight=w, zorder=10,
            path_effects=[pe.Stroke(linewidth=3, foreground='white'), pe.Normal()])
lab(123.1, 36.55, '황 금 강\n(예측 본류)', fs=15, col='#b8220f', rot=0)
lab(123.6, 30.1, '고장강', fs=12, col='#0b6e4f', rot=-25)
lab(122.2, 39.0, '고요하', fs=9.5, col='#1f4e9a', rot=0, w='normal')
lab(124.75, 38.9, '고압록강', fs=9.5, col='#1f4e9a', rot=0, w='normal')
lab(125.6, 36.9, '고한강', fs=9.5, col='#1f4e9a', rot=0, w='normal')
lab(125.9, 35.6, '고금강', fs=9.5, col='#1f4e9a', rot=0, w='normal')
lab(125.5, 34.55, '고영산강', fs=9.5, col='#1f4e9a', rot=0, w='normal')
lab(122.3, 33.6, '고회하', fs=9.5, col='#1f4e9a', rot=0, w='normal')
lab(121.2, 35.9, '황 금 평 원', fs=16, col='#6b4a00', w='bold')
lab(120.2, 36.8, '산둥반도', fs=10, col='#333', w='normal')
lab(127.6, 36.9, '한반도', fs=11, col='#333', w='normal')
lab(119.5, 38.7, '발해', fs=10, col='#333', w='normal')
lab(126.5, 33.4, '제주', fs=9, col='#333', w='normal')
lab(130.7, 32.3, '규슈', fs=10, col='#333', w='normal')
lab(128.6, 30.3, '오키나와\n해곡', fs=9.5, col='#1a3a5a', w='normal')
lab(129.9, 37.3, '동해\n(−120 m에서는 고립 해분,\nETOPO 문턱 −119 m)', fs=9, col='#1a3a5a', w='normal')
lab(128.9, 34.55, '대한해협 골', fs=8.5, col='#1a3a5a', w='normal')
lab(119.0, 31.6, '장강', fs=9, col='#333', w='normal')

ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1)
ax.set_aspect(1/np.cos(np.deg2rad(34)))
ax.set_xticks(range(117, 132)); ax.set_yticks(range(27, 42))
ax.set_xticklabels([f'{v}°E' for v in range(117, 132)], fontsize=9); ax.set_yticklabels([f'{v}°N' for v in range(27, 42)], fontsize=9)
ax.grid(color='white', alpha=0.5, lw=0.5)
for s in ax.spines.values(): s.set_color('#888')
# scale bar at 34N
km = 300; deg = km/(111.2*np.cos(np.deg2rad(34)))
ax.plot([117.4, 117.4+deg], [27.5, 27.5], color='k', lw=2.5); ax.plot([117.4, 117.4+deg/2], [27.5, 27.5], color='k', lw=2.5)
for i, t in enumerate(['0', '150', '300 km']): ax.text(117.4+deg*i/2, 27.62, t, fontsize=8, ha='center')

fig.text(0.07, 0.955, '황금강: 황해 해저 지형으로 예측한 빙하기 고하천 본류', fontsize=20, weight='bold', color='#17324d')
fig.text(0.07, 0.935, 'ETOPO 2022 30초 수심 격자에 해수면 −120 m를 적용하고, 함몰 메움·D8 흐름 방향·유량 누적으로 배수망을 계산한 결과', fontsize=10.5, color='#444')

handles = [
    Line2D([0], [0], color='#b8220f', lw=4, label='황금강 예측 본류 (해수면 −120 m, 10 km 평활 지형)'),
    Line2D([0], [0], color='#c0392b', lw=1.2, ls=(0, (2, 2)), label='본류 민감도: 평활 없는 원 지형'),
    Line2D([0], [0], color='#c0392b', lw=1.2, ls=(0, (5, 2)), label='본류 민감도: 해수면 −130 m'),
    Line2D([0], [0], color='#1f4e9a', lw=2, label='예측 지류 (요하·압록강·대동강·한강·금강·영산강·회하)'),
    Line2D([0], [0], color='#0b6e4f', lw=3, label='고장강 예측 경로 (별도 수계)'),
    Line2D([0], [0], color='#8a2f0a', lw=1.2, label='계산된 배수망 (유역 3,000 km² 이상)'),
    Line2D([0], [0], color='#e07b2a', lw=1, label='문헌: Song et al. 2016 고황하 하도 (실선)'),
    Line2D([0], [0], color='#2a9d8f', lw=1, label='문헌: Song et al. 2016 고장강 하도 (실선)'),
    Line2D([0], [0], color='#3a6fd8', lw=1, ls='--', label='문헌: Yoo et al. 2016 광역 해석 (파선)'),
    Line2D([0], [0], color='#8a5a1a', lw=1, label='현대 −120 m 등심선 (파선: −140 m)'),
]
leg = ax.legend(handles=handles, loc='upper left', bbox_to_anchor=(0.0, -0.045), ncol=2, fontsize=9, frameon=False, borderaxespad=0)
fig.text(0.07, 0.035,
 '금색: 현재 수심 0~−120 m (−120 m 해수면에서 노출되는 대륙붕). 갈색 띠: −120~−140 m. 배수망은 현재 해저 지형을 그대로 육지로 간주해 계산한 것이며, 홀로세 퇴적층 제거·지각 변동·빙하성 지각 조정을 반영하지 않았다.\n'
 '따라서 이 선은 "현재 해저 골짜기를 따라 흐를 때 가장 가능성이 높은 경로"이고, 2만 년 전 실제 강바닥의 실측이 아니다. 제주 서남쪽 외대륙붕 안부(−73 m)보다 제주해협 경로(최소 수심 −96 m)가 깊어 본류가 제주 북쪽으로 빠져나간다.\n'
 '자료: NOAA NCEI ETOPO 2022 (doi:10.25921/fd45-gt74). 문헌 하도: Song et al. 2016; Yoo et al. 2016; KORDI 1987. 제주해협 LGM 하도: Lee, Yoo & Lee 2020 (J. Coastal Res. SI95). 2026-11-09 제작.',
 fontsize=8.2, color='#444', va='bottom')
plt.savefig('build/황금강_예측본류_지도.png', dpi=220, facecolor='white')
plt.savefig('build/황금강_예측본류_지도.svg', facecolor='white')
print('saved')

# ---- longitudinal profile of the trunk (modern depth along path) ----
def profile(p):
    lon, lat = p[:, 0], p[:, 1]
    dx = np.diff(lon)*111.2*np.cos(np.deg2rad(lat[1:])); dy = np.diff(lat)*111.2
    s = np.concatenate([[0], np.cumsum(np.hypot(dx, dy))])
    cc = ((lon - tr.c)/tr.a).astype(int); rr = ((lat - tr.f)/tr.e).astype(int)
    return s, dem[np.clip(rr, 0, H-1), np.clip(cc, 0, W-1)]
fig2, ax2 = plt.subplots(figsize=(13, 4.2), facecolor='white')
for p, col, lw, lbl in [(trunk, '#b8220f', 2.2, '황금강 본류 (−120 m, 평활)'), (trunk_raw, '#c0392b', 1.0, '원 지형 경로'), (yz, '#0b6e4f', 2.0, '고장강 경로')]:
    s, z = profile(p); ax2.plot(s, z, color=col, lw=lw, label=lbl)
ax2.axhline(-120, color='#8a5a1a', lw=1, ls='--'); ax2.text(5, -118, '−120 m', color='#8a5a1a', fontsize=9)
ax2.axhline(0, color='#555', lw=0.8); ax2.set_ylim(-200, 20)
ax2.set_xlabel('하구까지의 거리 (km, 황하 발해 하구 기준)'); ax2.set_ylabel('현재 표고 (m)')
ax2.set_title('예측 본류를 따라 본 현재 해저 종단면 (실제 빙기 하상이 아니라 현재 지형)', fontsize=11)
ax2.legend(frameon=False, fontsize=9); ax2.grid(alpha=0.3)
fig2.tight_layout(); fig2.savefig('build/황금강_종단면.png', dpi=200, facecolor='white')

# ---- stats ----
out_r, out_c = None, None
s, z = profile(trunk); print('trunk length km', round(s[-1]), 'min depth', z.min(), 'mean', z.mean())
# catchment area at the outlet: accumulation at the last land cell of trunk
last = trunk[-2]; c = int((last[0]-tr.c)/tr.a); r = int((last[1]-tr.f)/tr.e)
print('catchment at outlet (km2, within grid only):', round(acc[r, c]*cell_km2))
# shelf-only area draining to the trunk outlet
print('cells on shelf draining (approx) km2:', round(((onshelf)).sum()*cell_km2))
