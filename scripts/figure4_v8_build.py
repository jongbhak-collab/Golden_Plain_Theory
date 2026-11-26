"""Figure 4 v8: Golden Plain and ancient dogs.
Starts from the Korean v7 SVG and
  - redraws the East Asian dog records (corrected coordinates, new Korean, Japanese and Chinese records),
  - adds Japanese wolf sample localities,
  - renumbers panel B chronologically,
  - extends the legend,
  - adds panel C: a chronology of dated dog remains (style of Figure 2, bottom panel) with a key list.
Usage: python3 scripts/figure4_v8_build.py build/fig4_ko.svg build/Figure4.svg  (input: output of figure4_restyle_korean.py)
"""
import re
import sys
from lxml import etree
from figure4_v8_sites import DOGS, WOLVES, LABELS

SRC, OUT = sys.argv[1], sys.argv[2]
NS = "http://www.w3.org/2000/svg"
N = {"s": NS}
FONT = "'바탕', 'Batang', 'Noto Serif CJK KR', serif"
TEAL = "#076e95"
PURPLE = "#7c3f83"
GRAY = "#6f7b7d"
REG_COL = {"W": "#5e6a70", "C": "#076e95", "K": "#b3361f", "J": "#c8781e"}
REG_NAME = {"W": "서유라시아(B)", "C": "중국", "K": "한국", "J": "일본"}

tree = etree.parse(SRC)
root = tree.getroot()
fig = root.find(".//s:g[@id='figure_1']", N)
ax1 = root.find(".//s:g[@id='axes_1']", N)
ax2 = root.find(".//s:g[@id='axes_2']", N)


def E(tag, parent=None, text=None, **attrs):
    attrs = {k.rstrip("_").replace("__", "-"): str(v) for k, v in attrs.items()}
    el = etree.SubElement(parent, f"{{{NS}}}{tag}", attrs) if parent is not None else etree.Element(f"{{{NS}}}{tag}", attrs)
    if text is not None:
        el.text = text
    return el


def X(lon):
    return 54.648 + (lon - 100) * 14.256


def Y(lat):
    return 523.734757 - (lat - 25) * 17.734501


# ---------------------------------------------------------------- 1. remove old East Asian dog layer
for gid in [f"PathCollection_{i}" for i in range(1, 7)] + [f"patch_{i}" for i in range(583, 589)]:
    g = ax1.find(f"s:g[@id='{gid}']", N)
    if g is not None:
        ax1.remove(g)
kl = root.find(".//s:g[@id='korean_labels']", N)
KEEP = {"황금평원", "일본늑대", "역사적 분포 범위"}
for t in list(kl):
    if (t.text or "") not in KEEP:
        kl.remove(t)
# the purple range is explained in the legend: drop its on-map label and leader to free space
for t in list(kl):
    if t.text in ("일본늑대", "역사적 분포 범위"):
        kl.remove(t)
    elif t.text == "황금평원":
        t.set("x", "372.00")
        t.set("y", "333.00")
lead = ax1.find("s:g[@id='patch_589']", N)
if lead is not None:
    ax1.remove(lead)
# shift the scale bar right so it does not touch the Yunnan record
for gid in ("line2d_21", "line2d_22", "line2d_23", "text_16"):
    g = ax1.find(f"s:g[@id='{gid}']", N)
    if g is not None:
        g.set("transform", "translate(70 0)")
# remove the old bottom note (redrawn at the new bottom)
old_note = fig.find("s:g[@id='text_41']", N)
fig.remove(old_note)

# ---------------------------------------------------------------- 2. symbols


def sym(parent, kind, x, y, s=1.0, color=TEAL):
    if kind == "nuc":
        E("circle", parent, cx=f"{x:.2f}", cy=f"{y:.2f}", r=f"{4.2*s:.2f}", style=f"fill:{color}; stroke:#ffffff; stroke-width:0.9")
    elif kind == "mt":
        h = 5.4 * s
        E("path", parent, d=f"M {x:.2f} {y-h:.2f} L {x+h:.2f} {y:.2f} L {x:.2f} {y+h:.2f} L {x-h:.2f} {y:.2f} Z",
          style=f"fill:#ffffff; stroke:{color}; stroke-width:1.65; stroke-linejoin:miter")
    elif kind == "morph":
        h = 4.0 * s
        E("rect", parent, x=f"{x-h:.2f}", y=f"{y-h:.2f}", width=f"{2*h:.2f}", height=f"{2*h:.2f}",
          style=f"fill:{GRAY}; stroke:#ffffff; stroke-width:0.9")
    elif kind in ("wolf_g", "wolf_m"):
        h = 5.6 * s
        fill = PURPLE if kind == "wolf_g" else "#ffffff"
        E("path", parent, d=f"M {x:.2f} {y-h:.2f} L {x+h*0.95:.2f} {y+h*0.68:.2f} L {x-h*0.95:.2f} {y+h*0.68:.2f} Z",
          style=f"fill:{fill}; stroke:{PURPLE}; stroke-width:1.2; stroke-linejoin:round")


def halo_text(parent, x, y, s, size=15.0, anchor="start", weight=700, fill="#151b20", halo="#ffffff", hw=3.4):
    base = f"font-weight:{weight}; font-size:{size}px; font-family:{FONT}; text-anchor:{anchor}"
    E("text", parent, s, x=f"{x:.2f}", y=f"{y:.2f}", style=f"{base}; fill:none; stroke:{halo}; stroke-width:{hw}; stroke-linejoin:round")
    E("text", parent, s, x=f"{x:.2f}", y=f"{y:.2f}", style=f"{base}; fill:{fill}")


# ---------------------------------------------------------------- 3. wolves (below dogs)
gw = E("g", fig, id="wolf_samples")
for name, lon, lat, genome, label, note in WOLVES:
    sym(gw, "wolf_g" if genome else "wolf_m", X(lon), Y(lat), s=0.82)

# ---------------------------------------------------------------- 4. dogs and labels
gd = E("g", fig, id="dog_records_v8")
gl = E("g", fig, id="dog_labels_v8")
pos = {}
for num, ko, reg, lon, lat, age, old, young, kind, src in DOGS:
    if reg == "W":
        continue
    x, y = X(lon), Y(lat)
    pos[num] = (x, y)
# Harbin: exact findspot not reported -> dashed ring
hx, hy = pos[4]
E("circle", gd, cx=f"{hx:.2f}", cy=f"{hy:.2f}", r="10.5", style=f"fill:none; stroke:{TEAL}; stroke-width:1.0; stroke-dasharray:2.2,1.8")
drawn = set()
for num, ko, reg, lon, lat, age, old, young, kind, src in DOGS:
    if reg == "W":
        continue
    x, y = pos[num]
    key = (round(x, 0), round(y, 0))
    if key in drawn:
        continue
    drawn.add(key)
    sym(gd, kind, x, y)
for lab in LABELS:
    nums, text, tx, ty, anchor, leader = lab
    mx, my = pos[nums[0]]
    if leader:
        lx, ly = leader
        E("path", gl, d=f"M {mx:.2f} {my:.2f} L {lx:.2f} {ly:.2f}", style=f"fill:none; stroke:{TEAL}; stroke-width:0.9; stroke-linecap:round")
    halo_text(gl, tx, ty, text, size=15.0, anchor=anchor)

# note on ancient wolf samples (Pacific, lower right of panel A)
wn = E("g", fig, id="wolf_note")
for k, line in enumerate(["일본늑대 고대 표본", "도치기 사노: 3만 5천 년 전(홍적세 늑대)", "후쿠시마·가나가와: 조몬", "나가노: 야요이~고훈"]):
    halo_text(wn, 706.0, 474.0 + k * 16.5, line, size=13.0 if k else 13.5, anchor="end",
              weight=700 if k == 0 else 400, fill=PURPLE, hw=3.0)

t35 = fig.find("s:g[@id='text_35']", N).find(".//s:text", N)
for c in list(t35):
    t35.remove(c)
t35.text = "A  노출 대륙붕, 연대가 측정된 주요 개 기록과 일본늑대 표본 산지"
# ---------------------------------------------------------------- 5. panel B renumbering (chronological)
renum = {"text_24": "2", "text_25": "3", "text_26": "1"}
for gid, new in renum.items():
    g = ax2.find(f"s:g[@id='{gid}']", N)
    t = g.find(".//s:text", N)
    for c in list(t):
        t.remove(c)
    t.text = new
blist = {"text_37": "1  피나르바시(튀르키예)  15,800년 전", "text_38": "2  고프 동굴(영국)  14,300년 전",
         "text_39": "3  케슬러로흐(스위스)  14,200년 전"}
for gid, new in blist.items():
    t = fig.find(f"s:g[@id='{gid}']", N).find(".//s:text", N)
    for c in list(t):
        t.remove(c)
    t.text = new

# ---------------------------------------------------------------- 6. legend
leg = root.find(".//s:g[@id='legend_1']", N)
for t in leg.iter(f"{{{NS}}}text"):
    if "".join(t.itertext()).strip() == "개: 미토게놈 기록만":
        for c in list(t):
            t.remove(c)
        t.text = "개: mtDNA 기록만"
LX, SX = 786.6128, 763.3628
lg2 = E("g", fig, id="legend_v8")
rows = [("morph", "개: 형태·층위 연대만"), ("wolf_g", "일본늑대 표본 산지(핵유전체)"), ("wolf_m", "일본늑대 표본 산지(mtDNA)")]
for k, (kind, text) in enumerate(rows):
    yy = 594.0 + k * 24.6
    sym(lg2, kind, SX, yy - 5.4, s=1.0)
    E("text", lg2, text, x=f"{LX}", y=f"{yy:.2f}", style=f"font-size:15.5px; font-family:{FONT}; fill:#151b20")

# ---------------------------------------------------------------- 7. panel C: chronology
H_OLD = 676.8
C_TOP = 612.0
AX_Y = 728.0
XL, XR = 54.648, 710.4
A_MAX = 16000.0
tx_ = lambda a: XL + (A_MAX - a) / A_MAX * (XR - XL)
pc = E("g", fig, id="panel_C")
E("text", pc, "C  고대 개 뼈의 연대", x=f"{XL}", y=f"{C_TOP:.2f}", style=f"font-weight:700; font-size:15.5px; font-family:{FONT}; fill:#151b20")
# region key
kx = 268.0
for reg in ("W", "C", "K", "J"):
    E("circle", pc, cx=f"{kx:.1f}", cy=f"{C_TOP-5:.1f}", r="5.2", style=f"fill:#ffffff; stroke:{REG_COL[reg]}; stroke-width:1.8")
    lab = REG_NAME[reg].replace("(B)", "")
    E("text", pc, lab, x=f"{kx+9:.1f}", y=f"{C_TOP:.2f}", style=f"font-size:14px; font-family:{FONT}; fill:{REG_COL[reg]}; font-weight:700")
    kx += 18 + 14.5 * len(lab) + 12
# axis
E("path", pc, d=f"M {XL:.2f} {AX_Y:.2f} L {XR:.2f} {AX_Y:.2f}", style="fill:none; stroke:#151b20; stroke-width:1.1")
for a in range(0, 16001, 2000):
    x = tx_(a)
    E("path", pc, d=f"M {x:.2f} {AX_Y:.2f} L {x:.2f} {AX_Y+5:.2f}", style="fill:none; stroke:#151b20; stroke-width:1.0")
    E("text", pc, f"{a//1000}", x=f"{x:.2f}", y=f"{AX_Y+21:.2f}", style=f"font-size:15px; font-family:{FONT}; text-anchor:middle; fill:#151b20")
E("text", pc, "천 년 전 (1950년 기준)", x=f"{(XL+XR)/2:.2f}", y=f"{AX_Y+41:.2f}", style=f"font-size:15px; font-family:{FONT}; text-anchor:middle; fill:#151b20")
# events with staggered stems
LEVELS = [AX_Y - 40, AX_Y - 64, AX_Y - 88, AX_Y - 112]
LANE = {"W": 4.0, "C": 9.5, "K": 15.0, "J": 20.5}
ev = sorted(DOGS, key=lambda d: -(d[6] + d[7]) / 2)
last = [-1e9] * len(LEVELS)
MIN_GAP = 20.0
for num, ko, reg, lon, lat, age, old, young, kind, src in ev:
    col = REG_COL[reg]
    x0, x1 = tx_(old), tx_(young)
    xm = (x0 + x1) / 2
    if x1 - x0 < 2.4:
        x0, x1 = xm - 1.2, xm + 1.2
    yl = AX_Y - LANE[reg]
    E("path", pc, d=f"M {x0:.2f} {yl:.2f} L {x1:.2f} {yl:.2f}", style=f"fill:none; stroke:{col}; stroke-width:4.2; stroke-linecap:butt")
    lvl = next((i for i in range(len(LEVELS)) if xm - last[i] >= MIN_GAP), len(LEVELS) - 1)
    last[lvl] = xm
    yc = LEVELS[lvl]
    E("path", pc, d=f"M {xm:.2f} {yl-2.1:.2f} L {xm:.2f} {yc+8.6:.2f}", style=f"fill:none; stroke:{col}; stroke-width:1.0")
    E("circle", pc, cx=f"{xm:.2f}", cy=f"{yc:.2f}", r="8.6", style=f"fill:#ffffff; stroke:{col}; stroke-width:1.5")
    E("text", pc, str(num), x=f"{xm:.2f}", y=f"{yc+4.4:.2f}",
      style=f"font-weight:700; font-size:{12 if num < 10 else 11}px; font-family:{FONT}; text-anchor:middle; fill:{col}")
# key list in two columns
KTOP = AX_Y + 74
LH = 19.0
TYPE = {"nuc": "핵유전체", "mt": "mtDNA", "morph": "형태"}
cols = [("W", "C"), ("K", "J")]
colx = [XL, 548.0]
for ci, regs in enumerate(cols):
    yy = KTOP
    for reg in regs:
        E("text", pc, REG_NAME[reg], x=f"{colx[ci]:.2f}", y=f"{yy:.2f}",
          style=f"font-weight:700; font-size:15.5px; font-family:{FONT}; fill:{REG_COL[reg]}")
        yy += LH
        for num, ko, r_, lon, lat, age, old, young, kind, src in sorted([d for d in DOGS if d[2] == reg], key=lambda d: d[0]):
            E("text", pc, f"{num}", x=f"{colx[ci]+16:.2f}", y=f"{yy:.2f}",
              style=f"font-weight:700; font-size:15px; font-family:{FONT}; text-anchor:end; fill:#151b20")
            E("text", pc, f"{ko}  {age} · {TYPE[kind]}", x=f"{colx[ci]+24:.2f}", y=f"{yy:.2f}",
              style=f"font-size:15px; font-family:{FONT}; fill:#151b20")
            yy += LH
        yy += 6
    if ci == 0:
        yend0 = yy
    else:
        yend1 = yy
NOTE_Y = max(yend0, yend1) + 10
E("text", pc, "주요 기록만 골라 표시함. 연대 범위는 보정 연대나 고고학적 시기이다. 일본늑대 표본 산지는 대부분 현 단위이다.",
  x=f"{XL}", y=f"{NOTE_Y:.2f}", style=f"font-size:14px; font-family:{FONT}; fill:#151b20")
H_NEW = NOTE_Y + 16
# ---------------------------------------------------------------- 8. canvas
vb = root.get("viewBox").split()
root.set("viewBox", f"{vb[0]} {vb[1]} {vb[2]} {H_NEW:.1f}")
root.set("height", f"{H_NEW:.1f}pt")
bg = fig[0]
if bg.tag == f"{{{NS}}}rect":
    bg.set("height", f"{H_NEW:.1f}")
tree.write(OUT, encoding="utf-8", xml_declaration=True)
print("ok; new height", round(H_NEW, 1))
