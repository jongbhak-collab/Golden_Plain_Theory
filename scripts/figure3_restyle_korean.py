"""Rebuild Figure 3 (Golden River) in the paper's figure style.
Keeps the original raster, contours and river paths; removes all outlined text;
redraws labels, Korean axis labels and a right-hand legend in a Batang-family font.
Usage: python3 fig3_korean.py clean.svg out.svg
"""
import sys
from lxml import etree

SRC, OUT = sys.argv[1], sys.argv[2]
NS = "http://www.w3.org/2000/svg"; N = {"s": NS}
FONT = "'바탕', 'Batang', 'Noto Serif CJK KR', serif"
tree = etree.parse(SRC); root = tree.getroot()
fig = root.find(".//s:g[@id='figure_1']", N)

# map frame in SVG units (from the matplotlib axes box)
X0, X1, Y0, Y1 = 155.556, 817.884, 73.584, 872.496
LON0, LON1, LAT0, LAT1 = 117.0, 131.0, 27.0, 41.0
def xy(lon, lat):
    return (X0 + (lon - LON0) / (LON1 - LON0) * (X1 - X0),
            Y1 - (lat - LAT0) / (LAT1 - LAT0) * (Y1 - Y0))

# new canvas
VX, VY, VW, VH = 66.0, 60.0, 1172.0, 848.0
root.set("viewBox", f"{VX} {VY} {VW} {VH}")
root.set("width", f"{VW}pt"); root.set("height", f"{VH}pt")
bg = etree.Element(f"{{{NS}}}rect", x=str(VX), y=str(VY), width=str(VW), height=str(VH), style="fill:#ffffff")
fig.insert(0, bg)
layer = etree.SubElement(fig, f"{{{NS}}}g", id="labels_ko")
defs = root.find("s:defs", N)
grad = etree.SubElement(defs, f"{{{NS}}}linearGradient", id="seagrad", x1="0", y1="0", x2="1", y2="0")
etree.SubElement(grad, f"{{{NS}}}stop", offset="0", style="stop-color:#6ea3c6")
etree.SubElement(grad, f"{{{NS}}}stop", offset="1", style="stop-color:#2e669c")

def text(x, y, s, size, fill="#222222", weight=400, anchor="middle", halo="#ffffff", hw=None,
         rotate=0, spacing=0, italic=False):
    hw = size * 0.22 if hw is None else hw
    base = (f"font-family:{FONT}; font-size:{size}px; font-weight:{weight}; text-anchor:{anchor};"
            + (f" letter-spacing:{spacing}px;" if spacing else ""))
    tr = f"rotate({rotate} {x:.2f} {y:.2f})" if rotate else None
    for kind in (("halo",) if halo else ()) + ("fill",):
        st = base + (f" fill:none; stroke:{halo}; stroke-width:{hw:.2f}; stroke-linejoin:round" if kind == "halo"
                     else f" fill:{fill}")
        t = etree.SubElement(layer, f"{{{NS}}}text", x=f"{x:.2f}", y=f"{y:.2f}", style=st)
        if tr: t.set("transform", tr)
        t.text = s

def label(lon, lat, lines, size, lead=1.18, **kw):
    """Center a (multi-line) label on lon/lat."""
    x, y = xy(lon, lat)
    n = len(lines)
    first = y - (n - 1) * size * lead / 2 + size * 0.36
    for i, s in enumerate(lines):
        text(x, first + i * size * lead, s, size, **kw)

C_TRUNK, C_TRIB, C_YZ = "#b8220f", "#1f4e9a", "#0b6e4f"
C_PLACE, C_SEA, C_PLAIN = "#2b2b2b", "#17324d", "#5c3d00"
S_BIG, S_RIVER, S_PLACE, S_SEA, S_PT = 32, 18.5, 19.5, 19, 17.5

# --- map labels ---
label(121.10, 35.64, ["황금평원"], S_BIG, fill=C_PLAIN, weight=700, spacing=6, hw=7)
label(122.30, 36.66, ["황금강"], 27, fill=C_TRUNK, weight=700, spacing=3, hw=5.5)
label(122.30, 36.24, ["(예측 본류)"], 18, fill=C_TRUNK, weight=700, hw=4.5)
label(124.62, 29.92, ["고장강"], 22, fill=C_YZ, weight=700, spacing=2, hw=5, rotate=33)
for lon, lat, s, anc in [(120.95, 39.85, "고요하", "end"), (124.12, 39.35, "고압록강", "end"),
                         (124.95, 38.30, "고대동강", "start"), (125.42, 36.70, "고한강", "end"),
                         (125.98, 35.70, "고금강", "middle"), (126.02, 34.74, "고영산강", "middle"),
                         (120.55, 34.20, "고회하", "start")]:
    x, y = xy(lon, lat); text(x, y + S_RIVER * 0.36, s, S_RIVER, fill=C_TRIB, weight=700, anchor=anc, hw=4.2)
for lon, lat, s, size in [(120.15, 36.85, "산둥반도", S_PLACE), (127.75, 36.75, "한반도", 22),
                          (119.65, 39.05, "발해", S_PLACE), (126.55, 32.98, "제주", 17.5),
                          (130.50, 32.28, "규슈", S_PLACE), (119.05, 31.55, "장강", 17.5),
                          (118.20, 33.40, "중국", 22)]:
    label(lon, lat, [s], size, fill=C_PLACE, weight=400, hw=4.2)
label(129.85, 37.35, ["동해"], 21, fill=C_SEA, hw=4.2)
label(128.62, 30.35, ["오키나와", "해곡"], S_SEA, fill=C_SEA, hw=4.2)
label(128.95, 34.62, ["대한해협 골"], 17.5, fill=C_SEA, hw=4.2)
label(126.35, 34.12, ["제주해협"], 16.5, fill=C_SEA, hw=4.0)
# outlets
x, y = xy(127.16, 33.50); text(x + 14, y + 30, "황금강 하구", S_PT, fill=C_TRUNK, weight=700, anchor="start", hw=4.2)
text(x + 14, y + 30 + S_PT * 1.18, "(-120 m 해안선)", 16, fill=C_PLACE, anchor="start", hw=4.0)
x, y = xy(126.27, 28.64); text(x + 14, y + 6, "고장강 하구", S_PT, fill=C_YZ, weight=700, anchor="start", hw=4.2)
text(x + 14, y + 6 + S_PT * 1.18, "(-120 m 해안선)", 16, fill=C_PLACE, anchor="start", hw=4.0)
# scale bar labels (bar from 117.4 E at 27.5 N, 300 km long)
import math
deg = 300 / (111.2 * math.cos(math.radians(34)))
for i, s in enumerate(["0", "150", "300 km"]):
    x, y = xy(117.4 + deg * i / 2, 27.5)
    text(x, y - 7, s, 16.5, fill="#111111", hw=3.6)

# --- axis labels (Korean, every 2 degrees) ---
TS = 17.5
for lon in range(118, 131, 2):
    x, _ = xy(lon, LAT0); text(x, Y1 + 9 + TS, f"동경 {lon}°", TS, fill="#222222", halo=None)
for lat in range(28, 41, 2):
    _, y = xy(LON0, lat); text(X0 - 9, y + TS * 0.36, f"북위 {lat}°", TS, fill="#222222", anchor="end", halo=None)

# --- legend ---
LX, LT = 846.0, 94.0          # left x, top baseline of heading
SW = 38.0                     # swatch width
TX = LX + SW + 11             # text x
FS = 19.5                     # legend font size
LEAD = FS * 1.22
GAP = 7.5
leg = etree.SubElement(fig, f"{{{NS}}}g", id="legend_ko")
def lt(x, y, s, size=FS, weight=400, fill="#1a1a1a"):
    t = etree.SubElement(leg, f"{{{NS}}}text", x=f"{x:.2f}", y=f"{y:.2f}",
                         style=f"font-family:{FONT}; font-size:{size}px; font-weight:{weight}; fill:{fill}")
    t.text = s
def rect(x, y, w, h, fill, stroke="#7a7a7a", op=1.0):
    etree.SubElement(leg, f"{{{NS}}}rect", x=f"{x:.2f}", y=f"{y:.2f}", width=f"{w:.2f}", height=f"{h:.2f}",
                     style=f"fill:{fill}; fill-opacity:{op}; stroke:{stroke}; stroke-width:0.8")
def line(x1, y1, x2, y2, col, w, dash=None, halo=None, cap="butt"):
    if halo:
        etree.SubElement(leg, f"{{{NS}}}line", x1=f"{x1:.2f}", y1=f"{y1:.2f}", x2=f"{x2:.2f}", y2=f"{y2:.2f}",
                         style=f"stroke:#ffffff; stroke-width:{halo}; stroke-linecap:round")
    st = f"stroke:{col}; stroke-width:{w}; stroke-linecap:{cap}" + (f"; stroke-dasharray:{dash}" if dash else "")
    etree.SubElement(leg, f"{{{NS}}}line", x1=f"{x1:.2f}", y1=f"{y1:.2f}", x2=f"{x2:.2f}", y2=f"{y2:.2f}", style=st)

lt(LX, LT, "범례", 22, weight=700)
y = LT + 14
def item(lines, draw):
    global y
    top = y
    h = len(lines) * LEAD
    cy = top + FS * 0.62          # swatch centre at first text line
    draw(cy)
    for i, s in enumerate(lines):
        lt(TX, top + FS * 0.95 + i * LEAD, s)
    y = top + h + GAP

item(["노출 대륙붕", "(현재 표고 0~-120 m)"], lambda cy: rect(LX, cy - 8, SW, 16, "#d8c486"))
item(["현재 표고 -120~-140 m"], lambda cy: rect(LX, cy - 8, SW, 16, "#b9a57b"))
item(["현재 육지"], lambda cy: rect(LX, cy - 8, SW, 16, "#c3c4bf"))
item(["표고 -140 m 이하의 바다"], lambda cy: rect(LX, cy - 8, SW, 16, "url(#seagrad)"))
def contour_sw(cy):
    line(LX, cy, LX + SW, cy, "#8a5a1a", 1.9, dash="6.5,2.8")
    line(LX, cy + LEAD, LX + SW, cy + LEAD, "#8a5a1a", 1.1, dash="4.2,1.8")
item(["-120 m 등심선(굵은 파선)", "-140 m 등심선(가는 파선)"], contour_sw)
item(["황금강 예측 본류", "(해수면 -120 m, 10 km 평활)"], lambda cy: line(LX + 2, cy, LX + SW - 2, cy, C_TRUNK, 4.6, halo=7.2, cap="round"))
item(["민감도: 평활 없는 원지형"], lambda cy: line(LX, cy, LX + SW, cy, "#c0392b", 1.6, dash="2.4,2.4"))
item(["민감도: 해수면 -130 m"], lambda cy: line(LX, cy, LX + SW, cy, "#c0392b", 1.6, dash="6,2.4"))
item(["예측 지류"], lambda cy: line(LX + 2, cy, LX + SW - 2, cy, C_TRIB, 2.4, halo=4.4, cap="round"))
item(["고장강 예측 경로(별도 수계)"], lambda cy: line(LX + 2, cy, LX + SW - 2, cy, C_YZ, 3.6, halo=5.8, cap="round"))
def dots(cy):
    for k in range(7):
        etree.SubElement(leg, f"{{{NS}}}rect", x=f"{LX + 2 + k * 5.2:.2f}", y=f"{cy - 1.4:.2f}", width="2.8", height="2.8",
                         style="fill:#7a1f00; fill-opacity:0.85")
item(["계산된 배수망", "(유역 3,000 km² 이상)"], dots)
def lit(cy):
    line(LX, cy - 6, LX + SW, cy - 6, "#e07b2a", 1.6)
    line(LX, cy, LX + SW, cy, "#2a9d8f", 1.6)
    line(LX, cy + 6, LX + SW, cy + 6, "#3a6fd8", 1.6)
item(["문헌 하도: 주황 고황하,", "청록 고장강, 파랑 한반도 하천"], lit)
item(["실선: Song 등(2016)"], lambda cy: line(LX, cy, LX + SW, cy, "#555555", 1.4))
item(["파랑 파선: Yoo 등(2016)"], lambda cy: line(LX, cy, LX + SW, cy, "#3a6fd8", 1.4, dash="5,2.4"))
item(["파랑 점선: 해양연구소(1987)"], lambda cy: line(LX, cy, LX + SW, cy, "#3a6fd8", 1.4, dash="1.4,2.4"))
def concept(cy):
    line(LX, cy - 3, LX + SW, cy - 3, "#e07b2a", 1.4, dash="5,2.4")
    line(LX, cy + 3, LX + SW, cy + 3, "#2a9d8f", 1.4, dash="5,2.4")
item(["주황·청록 파선: 개념적 연결선"], concept)
def circ(cy):
    etree.SubElement(leg, f"{{{NS}}}circle", cx=f"{LX + SW / 2:.2f}", cy=f"{cy:.2f}", r="5.2",
                     style=f"fill:#ffffff; stroke:{C_TRUNK}; stroke-width:2.2")
item(["주요 합류점과 하구"], circ)
# short caveat in the free space under the legend
y += 10
for i, s_ in enumerate(["현재 해저 지형으로 계산한 후보 경로이며,", "측량된 고하도가 아니다. 홀로세 퇴적층과", "지각 변동은 반영하지 않았다."]):
    lt(LX, y + FS * 0.95 + i * FS * 1.2, s_, size=17.5, fill="#333333")
print("legend bottom y =", round(y + 3 * FS * 1.2, 1))
tree.write(OUT, xml_declaration=True, encoding="utf-8")
