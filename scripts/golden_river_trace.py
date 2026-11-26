"""Trace downstream paths from modern river mouths through the routed shelf, for a given run.
Outputs GeoJSON of the paths and prints confluence info."""
import sys, json, numpy as np, rasterio
run = sys.argv[1]
src = rasterio.open('data/etopo/ETOPO2022_30s_116E25N_139E42N.tif'); dem = src.read(1); tr = src.transform
fdir = np.load(f'build/{run}_fdir.npy'); acc = np.load(f'build/{run}_acc.npy'); land = np.load(f'build/{run}_land.npy')
H, W = dem.shape
dirmap = {64:(-1,0),128:(-1,1),1:(0,1),2:(1,1),4:(1,0),8:(1,-1),16:(0,-1),32:(-1,-1)}
def rc(lon, lat):
    c = int((lon - tr.c)/tr.a); r = int((lat - tr.f)/tr.e); return r, c
def ll(r, c):
    return (tr.c + (c+0.5)*tr.a, tr.f + (r+0.5)*tr.e)
# modern river mouths (approx): name -> (lon, lat). We snap to the max-accumulation cell within a window.
mouths = {
 'Huang He (Yellow R.)': (119.25, 37.75),
 'Hai He': (117.75, 38.98),
 'Luan He': (119.2, 39.4),
 'Liao He': (121.9, 40.85),
 'Yalu': (124.2, 39.85),
 'Taedong': (125.25, 38.72),
 'Han (Korea)': (126.45, 37.72),
 'Geum': (126.55, 36.0),
 'Yeongsan': (126.4, 34.8),
 'Chang Jiang (Yangtze)': (121.9, 31.4),
 'Qiantang': (121.9, 30.4),
 'Huai (Hongze)': (119.4, 33.0),
}
def snap(lon, lat, win=8):
    r, c = rc(lon, lat)
    r0, r1 = max(0, r-win), min(H, r+win+1); c0, c1 = max(0, c-win), min(W, c+win+1)
    sub = np.where(land[r0:r1, c0:c1], acc[r0:r1, c0:c1], -1)
    i = np.unravel_index(np.argmax(sub), sub.shape)
    return r0+i[0], c0+i[1]
paths = {}
for name, (lon, lat) in mouths.items():
    r, c = snap(lon, lat)
    pts = []; cells = []
    for _ in range(20000):
        pts.append(ll(r, c)); cells.append((r, c))
        d = int(fdir[r, c])
        if d not in dirmap: break
        dr, dc = dirmap[d]; r2, c2 = r+dr, c+dc
        if not (0 <= r2 < H and 0 <= c2 < W) or not land[r2, c2]: pts.append(ll(r2, c2)); break
        r, c = r2, c2
    paths[name] = (pts, cells)
    print(f'{name:24s} start {pts[0][0]:.2f},{pts[0][1]:.2f} -> outlet {pts[-1][0]:.2f},{pts[-1][1]:.2f}  n={len(pts)}')
# confluences: first shared cell between pairs
names = list(paths)
sets = {n: {cell: i for i, cell in enumerate(paths[n][1])} for n in names}
print('\nConfluences (first common cell):')
for i, a in enumerate(names):
    for b in names[i+1:]:
        common = [cell for cell in paths[a][1] if cell in sets[b]]
        if common:
            lon, lat = ll(*common[0]); print(f'  {a} + {b}: {lon:.2f}E {lat:.2f}N  depth today {dem[common[0]]:.0f} m')
feats = [{'type':'Feature','properties':{'name':n,'run':run},'geometry':{'type':'LineString','coordinates':[[round(x,4),round(y,4)] for x,y in paths[n][0]]}} for n in names]
json.dump({'type':'FeatureCollection','features':feats}, open(f'build/{run}_paths.geojson','w'))
