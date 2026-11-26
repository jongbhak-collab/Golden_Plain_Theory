"""Localize 'Yellow_Sea_Plain_Ancient_Canids_v1.svg' into Korean.
- Editable <text> elements: replace strings, switch to a Batang-family font.
- Outlined halo labels (glyph paths): remove and redraw as Korean <text> with halos.
Usage: python3 fig4_korean.py orig.svg out.svg
"""
import re
import sys
from lxml import etree

SRC, OUT = sys.argv[1], sys.argv[2]
NS = "http://www.w3.org/2000/svg"
N = {"s": NS}
FONT = "'바탕', 'Batang', 'Noto Serif CJK KR', serif"

tree = etree.parse(SRC)
root = tree.getroot()

# 1) widen canvas: 18 pt on the left (y tick labels), 30 pt on the right (panel B list)
L, R = 18.0, 30.0
W, H = 993.6, 676.8
root.set("viewBox", f"{-L} 0 {W + L + R} {H}")
root.set("width", f"{W + L + R}pt")
root.set("height", f"{H}pt")
fig = root.find(".//s:g[@id='figure_1']", N)
bg = etree.Element(f"{{{NS}}}rect", x=str(-L), y="0", width=str(W + L + R), height=str(H), style="fill:#ffffff")
fig.insert(0, bg)
title = root.find("s:title", N)
if title is not None:
    title.text = "황해 평원과 고대 개"

# 2) editable text replacements
MAP = {
    "100°E": "동경 100°", "110°E": "동경 110°", "120°E": "동경 120°", "130°E": "동경 130°", "140°E": "동경 140°",
    "25°N": "북위 25°", "30°N": "북위 30°", "35°N": "북위 35°", "40°N": "북위 40°", "45°N": "북위 45°",
    "CHINA": "중국", "KOREA": "한반도",
    "500 km": "500 km",
    "Present land": "현재 육지",
    "Potential exposed shelf": "노출 가능 대륙붕", "(-120 m scenario)": "(해수면 -120 m 시나리오)",
    "-120 m shoreline proxy": "-120 m 해안선 근사선",
    "-200 m contour": "-200 m 등심선", "(shelf-margin guide)": "(대륙붕 가장자리 참고선)",
    "Dog: nuclear DNA": "개: 핵유전체 기록", "Dog: mtDNA only": "개: 미토게놈 기록만",
    "Japanese wolf:": "일본늑대:", "historic island range": "역사적 섬 분포 범위",
    "The Yellow Sea plain and ancient dogs": "황해 평원과 고대 개",
    "A  Exposed shelf scenario and selected dated dog records": "A  노출 대륙붕 시나리오와 연대가 측정된 주요 개 기록",
    "B  Early nuclear-DNA records": "B  초기 핵유전체 개 기록",
    "1  Gough’s Cave  14.3 ka": "1  고프 동굴(영국)  14,300년 전",
    "2  Kesslerloch  14.2 ka": "2  케슬러로흐(스위스)  14,200년 전",
    "3  Pınarbaşı  15.8 ka": "3  피나르바시(튀르키예)  15,800년 전",
    "Map key": "범례",
    "Selected records; ka = thousand years before present": "주요 기록만 골라 표시함. 연대는 1950년을 기준으로 한 '몇 년 전'이다.",
    "1": "1", "2": "2", "3": "3",
}
# multi-line sea names: collapse to one centered Korean label
SEA = {
    "East Sea /": ("동해", 556.6, 253.0),
    "Sea of Japan": None,
    "East China": ("동중국해", 387.0, 490.0),
    "Sea": None,
}

def set_font(el, extra_drop_italic=False):
    st = el.get("style", "")
    st = re.sub(r"font-family:\s*'[^']*'", f"font-family: {FONT}", st)
    if extra_drop_italic:
        st = re.sub(r"font-style:\s*italic;\s*", "", st)
    el.set("style", st)

unhandled = []
for t in root.iter(f"{{{NS}}}text"):
    s = "".join(t.itertext()).strip()
    if s in SEA:
        rep = SEA[s]
        if rep is None:
            t.getparent().remove(t)
            continue
        txt, x, y = rep
        for c in list(t):
            t.remove(c)
        t.text = txt
        t.attrib.pop("transform", None)
        t.set("x", str(x))
        t.set("y", str(y))
        st = t.get("style", "") + "; text-anchor: middle"
        t.set("style", st)
        set_font(t, extra_drop_italic=True)
        continue
    if s in MAP:
        for c in list(t):
            t.remove(c)
        t.text = MAP[s]
        set_font(t)
    else:
        unhandled.append(s)

# 3) outlined halo labels -> remove and redraw
def path_bbox(g):
    xs, ys = [], []
    for p in g.iter(f"{{{NS}}}path"):
        nums = [float(v) for v in re.findall(r"-?\d+\.?\d*(?:e-?\d+)?", p.get("d", ""))]
        xs += nums[0::2]
        ys += nums[1::2]
    return min(xs), min(ys), max(xs), max(ys)

DOG = "fill:#151b20"
HALO_W = "stroke:#ffffff; stroke-width:3.4; stroke-linejoin:round"
labels = {
    # id: (lines, align, fill, halo_color, halo_width, size)
    "text_15": (["황해 평원", "'황금평원'", "(가설)"], "middle", "#65430f", "#f4e9ca", 3.2, 16.5),
    "text_17": (["하얼빈", "12,900년 전"], "start", "#151b20", "#ffffff", 3.4, 15.0),
    "text_18": (["싱룽", "8,500년 전"], "start", "#151b20", "#ffffff", 3.4, 15.0),
    "text_19": (["징터우산", "8,300년 전"], "start", "#151b20", "#ffffff", 3.4, 15.0),
    "text_20": (["자오자", "4,800년 전"], "start", "#151b20", "#ffffff", 3.4, 15.0),
    "text_21": (["야베이리", "5,000년 전"], "start", "#151b20", "#ffffff", 3.4, 15.0),
    "text_22": (["진찬커우", "3,900년 전"], "start", "#151b20", "#ffffff", 3.4, 15.0),
    "text_23": (["일본늑대", "역사적 분포 범위"], "middle", "#7c3f83", "#ffffff", 3.4, 15.0),
}
SHIFT = {"text_20": -34.0, "text_18": -14.0}   # move left to clear leader lines (Korean labels are wider)
new_group = etree.SubElement(fig, f"{{{NS}}}g", id="korean_labels")
for gid, (lines, align, fill, halo, hw, size) in labels.items():
    g = root.find(f".//s:g[@id='{gid}']", N)
    x0, y0, x1, y1 = path_bbox(g)
    g.getparent().remove(g)
    n = len(lines)
    lead = (y1 - y0 - size * 0.72) / max(n - 1, 1) if n > 1 else 0
    first = y0 + size * 0.80
    lead = (y1 - first) / max(n - 1, 1) if n > 1 else 0
    x = (x0 if align == "start" else (x0 + x1) / 2) + SHIFT.get(gid, 0.0)
    for k, line in enumerate(lines):
        y = first + k * lead
        base = f"font-weight:700; font-size:{size}px; font-family:{FONT}; text-anchor:{align}"
        h = etree.SubElement(new_group, f"{{{NS}}}text", x=f"{x:.2f}", y=f"{y:.2f}",
                             style=f"{base}; fill:none; stroke:{halo}; stroke-width:{hw}; stroke-linejoin:round")
        h.text = line
        f_ = etree.SubElement(new_group, f"{{{NS}}}text", x=f"{x:.2f}", y=f"{y:.2f}", style=f"{base}; fill:{fill}")
        f_.text = line

tree.write(OUT, encoding="utf-8", xml_declaration=True)
print("unhandled text:", unhandled)
