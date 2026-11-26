"""Recover map data from the published figure SVGs (matplotlib vector output).

Figure 3 (Golden River map): literature paleochannel polylines and contour lines.
Figure 4 (Yellow Sea plain and ancient dogs): dog record points, Japanese wolf island range,
shoreline-proxy contours. Coordinates are recovered by inverting each panel's linear
lon/lat-to-SVG transform, read from the axes frame and tick positions in the SVG itself.

Usage: python3 extract_svg_layers.py fig3.svg fig4.svg outdir
"""
import json, re, sys, os, csv
from lxml import etree

NS = {'s': 'http://www.w3.org/2000/svg', 'x': 'http://www.w3.org/1999/xlink'}
SVG3, SVG4, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)

def subpaths(d):
    """Split an SVG path (M/L/z, absolute, as written by matplotlib) into point lists."""
    out, cur = [], []
    for cmd, args in re.findall(r'([MLZz])([^MLZz]*)', d):
        nums = list(map(float, re.findall(r'-?\d+(?:\.\d+)?(?:e-?\d+)?', args)))
        if cmd == 'M':
            if len(cur) > 1: out.append(cur)
            cur = [(nums[0], nums[1])]
            nums = nums[2:]
        if cmd in 'ML':
            cur += list(zip(nums[0::2], nums[1::2]))
        if cmd in 'Zz':
            if cur: cur.append(cur[0])
    if len(cur) > 1: out.append(cur)
    return out

def style(el):
    st = re.sub(r'\s+', ' ', el.get('style') or '')
    get = lambda k: (re.search(rf'{k}: ?([^;]+)', st) or [None, None])[1]
    return {'stroke': get('stroke'), 'fill': get('fill'), 'width': get('stroke-width'),
            'dash': get('stroke-dasharray')}

def frame(ax):
    p = ax[0].find('.//s:path', NS)
    xs, ys = zip(*subpaths(p.get('d'))[0])
    return min(xs), max(xs), min(ys), max(ys)

def r5(v): return round(v, 5)

# ---------------- Figure 3 ----------------
r3 = etree.parse(SVG3).getroot()
ax3 = r3.find('.//s:g[@id="axes_1"]', NS)
x0, x1, y0, y1 = frame(ax3)
LON0, LON1, LAT0, LAT1 = 117.0, 131.0, 27.0, 41.0       # set_xlim / set_ylim in finalmap.py
f3 = lambda x, y: (r5(LON0 + (x - x0) / (x1 - x0) * (LON1 - LON0)), r5(LAT0 + (y1 - y) / (y1 - y0) * (LAT1 - LAT0)))
SYSTEM = {'#e07b2a': 'paleo-Yellow River system', '#2a9d8f': 'paleo-Changjiang system', '#3a6fd8': 'Korean west and south coast rivers'}
SYSKEY = {'#e07b2a': 'Huanghe', '#2a9d8f': 'Changjiang', '#3a6fd8': 'Korean'}
feats = []
for g in ax3:
    gid = g.get('id') or ''
    if not gid.startswith('line2d'): continue
    n = int(gid.split('_')[1])
    if not 63 <= n <= 96: continue                      # literature layer, drawn before the routed rivers
    p = g.find('.//s:path', NS); s = style(p)
    col = s['stroke']
    if col not in SYSTEM: continue
    dash = s['dash']
    if dash is None:
        kind, src, ev = 'interpreted channel (solid)', 'Song et al. 2016, doi:10.17559/TV-20160216023828', 'interpreted_channel'
    else:
        a = float(dash.split(',')[0])
        if a > 1.5:
            kind, ev = 'regional connection (dashed)', 'synthesis'
            src = ('Yoo et al. 2016, doi:10.1016/j.marpetgeo.2016.03.005' if col == '#3a6fd8'
                   else 'conceptual connection compiled for this study (not from a single source)')
        else:
            kind, src, ev = 'alternative route (dotted)', 'KORDI 1987, report BSPE 00087-137-5', 'alternative'
    for sp in subpaths(p.get('d')):
        feats.append({'type': 'Feature', 'properties': {'layer_id': gid, 'system': SYSKEY[col], 'evidence': ev, 'river_system': SYSTEM[col], 'line_kind': kind,
                      'source': src, 'figure_color': col},
                      'geometry': {'type': 'LineString', 'coordinates': [f3(x, y) for x, y in sp]}})
json.dump({'type': 'FeatureCollection', 'name': 'literature_paleochannels',
           'note': 'Literature paleochannels digitized and generalized from published figures; recovered from the vector layers of Figure 3. WGS84 lon/lat.',
           'features': feats}, open(f'{OUT}/literature_paleochannels.geojson', 'w'), ensure_ascii=False)
print('literature channels:', len(feats))
for f in feats:
    c = f['geometry']['coordinates']; print('  ', f['properties']['layer_id'], f['properties']['river_system'][:18], f['properties']['line_kind'][:22], c[0], '->', c[-1], len(c))

# contours (modern ETOPO 2022 isobaths as drawn in Figure 3)
LEVELS = {'QuadContourSet_1': [0], 'QuadContourSet_2': [-100, -50], 'QuadContourSet_3': [-120], 'QuadContourSet_4': [-140]}
cfeats = []
for g in ax3:
    gid = g.get('id') or ''
    if gid not in LEVELS: continue
    for lev, p in zip(LEVELS[gid], g.findall('.//s:path', NS)):
        lines = [[f3(x, y) for x, y in sp] for sp in subpaths(p.get('d'))]
        cfeats.append({'type': 'Feature', 'properties': {'elevation_m': lev, 'source': 'NOAA ETOPO 2022 30 arc-second surface (unsmoothed)'},
                       'geometry': {'type': 'MultiLineString', 'coordinates': lines}})
        print('contour', lev, len(lines))
json.dump({'type': 'FeatureCollection', 'name': 'figure3_isobaths', 'features': cfeats},
          open(f'{OUT}/figure3_isobaths_0_50_100_120_140m.geojson', 'w'))

# ---------------- Figure 4 ----------------
r4 = etree.parse(SVG4).getroot()
ax4 = r4.find('.//s:g[@id="axes_1"]', NS)
# ticks give the panel A transform
tx, ty = [], []
for axis in ax4.findall('s:g', NS):
    aid = axis.get('id') or ''
    for tick in axis.findall('s:g', NS):
        u = tick.find('.//s:use', NS); lab = ''.join(t.text or '' for t in tick.iter('{http://www.w3.org/2000/svg}text'))
        if u is None or not lab: continue
        val = float(re.match(r'(\d+)', lab).group(1))
        (tx if lab.endswith('E') else ty).append((val, float(u.get('x')), float(u.get('y'))))
(lo_a, xa, _), (lo_b, xb, _) = tx[0], tx[-1]
(la_a, _, ya), (la_b, _, yb) = ty[0], ty[-1]
fA = lambda x, y: (r5(lo_a + (x - xa) * (lo_b - lo_a) / (xb - xa)), r5(la_a + (y - ya) * (la_b - la_a) / (yb - ya)))
ex = [fA(*p) for p in [(frame(ax4)[0], frame(ax4)[3]), (frame(ax4)[1], frame(ax4)[2])]]
print('panel A extent', ex)
# panel B transform from the dashed rectangle that outlines panel A's extent
ax4b = r4.find('.//s:g[@id="axes_2"]', NS)
rect = None
for g in ax4b:
    p = g.find('.//s:path', NS)
    if p is not None and (style(p)['stroke'] == '#a46b16'):
        xs, ys = zip(*subpaths(p.get('d'))[0]); rect = (min(xs), max(xs), min(ys), max(ys))
(Alon0, Alat0), (Alon1, Alat1) = ex
fB = lambda x, y: (r5(Alon0 + (x - rect[0]) / (rect[1] - rect[0]) * (Alon1 - Alon0)), r5(Alat0 + (rect[3] - y) / (rect[3] - rect[2]) * (Alat1 - Alat0)))
RECORDS = {  # label text in the figure, record type from marker style, age rounded as printed
  'PathCollection_1': ('Harbin (V0726)', '하얼빈', 'China', 12.9, 'mitochondrial only', 'Zhang M. et al. 2024, doi:10.1093/molbev/msae062, Table S1', 'river-bottom find without secure cultural context; point is the published collection locality'),
  'PathCollection_2': ('Xinglong', '싱룽', 'China', 8.5, 'mitochondrial only', 'Zhang M. et al. 2024, doi:10.1093/molbev/msae062, Table S1', ''),
  'PathCollection_3': ('Jingtoushan', '징터우산', 'China', 8.3, 'mitochondrial only', 'Zhang M. et al. 2024, doi:10.1093/molbev/msae062, Table S1', ''),
  'PathCollection_4': ('Zhaojia', '자오자', 'China', 4.8, 'mitochondrial only', 'Zhang M. et al. 2024, doi:10.1093/molbev/msae062, Table S1', ''),
  'PathCollection_5': ('Yabeili', '야베이리', 'China', 5.0, 'nuclear genome', 'Zhang S.-J. et al. 2025, doi:10.1126/science.adu2836, Table S1', 'Chinese site name not verified'),
  'PathCollection_6': ('Jinchankou', '진찬커우', 'China', 3.9, 'nuclear genome', 'Zhang S.-J. et al. 2025, doi:10.1126/science.adu2836, Table S1', ''),
  'PathCollection_7': ("Gough's Cave", '고프 동굴', 'United Kingdom', 14.3, 'nuclear genome', 'Bergström et al. 2026, doi:10.1038/s41586-026-10112-7; Marsh et al. 2026, doi:10.1038/s41586-026-10170-x', ''),
  'PathCollection_8': ('Kesslerloch', '케슬러로흐', 'Switzerland', 14.2, 'nuclear genome', 'Bergström et al. 2026, doi:10.1038/s41586-026-10112-7; Marsh et al. 2026, doi:10.1038/s41586-026-10170-x', ''),
  'PathCollection_9': ('Pinarbasi', '피나르바시', 'Türkiye', 15.8, 'nuclear genome', 'Bergström et al. 2026, doi:10.1038/s41586-026-10112-7; Marsh et al. 2026, doi:10.1038/s41586-026-10170-x', ''),
}
rows, pfeats = [], []
for axg, fx, panel in [(ax4, fA, 'A'), (ax4b, fB, 'B')]:
    for g in axg:
        gid = g.get('id') or ''
        if gid not in RECORDS: continue
        u = g.find('.//s:use', NS); lon, lat = fx(float(u.get('x')), float(u.get('y')))
        name, ko, country, age, rtype, src, note = RECORDS[gid]
        rows.append({'site': name, 'site_ko': ko, 'country': country, 'lon': round(lon, 3), 'lat': round(lat, 3),
                     'age_ka_rounded': age, 'record_type': rtype, 'figure_panel': panel, 'source': src,
                     'coordinate_note': 'digitized from Figure 4 (accuracy about 0.05 degree)' + ('; ' + note if note else '')})
        pfeats.append({'type': 'Feature', 'properties': {k: v for k, v in rows[-1].items() if k not in ('lon', 'lat')},
                       'geometry': {'type': 'Point', 'coordinates': [round(lon, 3), round(lat, 3)]}})
with open(f'{OUT}/dog_records.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
json.dump({'type': 'FeatureCollection', 'name': 'dog_records', 'features': pfeats}, open(f'{OUT}/dog_records.geojson', 'w'), ensure_ascii=False)
for r in rows: print('  ', r['site'], r['lon'], r['lat'], r['age_ka_rounded'], r['record_type'])
# Japanese wolf island range (purple filled outlines: Honshu, Shikoku, Kyushu from Natural Earth 1:10m)
polys = []
for g in ax4:
    gid = g.get('id') or ''
    p = g.find('.//s:path', NS)
    if p is None: continue
    s = style(p)
    if s['stroke'] == '#7c3f83' and s['fill'] not in (None, 'none'):
        rings = [[fA(x, y) for x, y in sp] for sp in subpaths(p.get('d'))]
        polys.append({'type': 'Feature', 'properties': {'layer_id': gid, 'meaning': 'historical island range of the Japanese wolf (Honshu, Shikoku, Kyushu)',
                      'source': 'Natural Earth 1:10m land; range after Gojobori et al. 2024, doi:10.1038/s41467-024-46124-y'},
                      'geometry': {'type': 'Polygon', 'coordinates': rings}})
json.dump({'type': 'FeatureCollection', 'name': 'japanese_wolf_range', 'features': polys}, open(f'{OUT}/japanese_wolf_island_range.geojson', 'w'))
print('wolf range polygons:', len(polys))
# shoreline proxy and shelf-margin guide (ETOPO1 sampled at 2 arc-minutes)
cf = []
for g in ax4:
    gid = g.get('id') or ''
    if not gid.startswith('QuadContourSet'): continue
    for p in g.findall('.//s:path', NS):
        s = style(p)
        if s['fill'] not in (None, 'none'): continue      # skip the gold shelf fill
        lev = -120 if s['dash'] else -200
        lines = [[fA(x, y) for x, y in sp] for sp in subpaths(p.get('d'))]
        cf.append({'type': 'Feature', 'properties': {'elevation_m': lev, 'meaning': '-120 m lowstand shoreline proxy (dashed)' if lev == -120 else '-200 m shelf-margin guide (solid)',
                   'source': 'NOAA ETOPO1 (Amante and Eakins 2009), 2 arc-minute sampling'},
                   'geometry': {'type': 'MultiLineString', 'coordinates': lines}})
        print('fig4 contour', gid, lev, len(lines), s)
json.dump({'type': 'FeatureCollection', 'name': 'figure4_isobaths', 'features': cf}, open(f'{OUT}/figure4_isobaths_120_200m.geojson', 'w'))
