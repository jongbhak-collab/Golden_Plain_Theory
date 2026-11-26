"""Strip all text, legend and title from the Golden River SVG; keep raster, contours, rivers, ticks."""
import sys
from lxml import etree
SRC, OUT = sys.argv[1], sys.argv[2]
NS = "http://www.w3.org/2000/svg"; N = {"s": NS}
tree = etree.parse(SRC); root = tree.getroot()
fig = root.find(".//s:g[@id='figure_1']", N)
ax = fig.find("s:g[@id='axes_1']", N)
removed = []
for gid in ("text_88", "text_89", "text_90"):
    g = fig.find(f"s:g[@id='{gid}']", N)
    if g is not None: fig.remove(g); removed.append(gid)
for g in list(ax):
    gid = g.get("id") or ""
    if gid == "legend_1" or gid.startswith("text_"):
        ax.remove(g); removed.append(gid)
for axis_id in ("matplotlib.axis_1", "matplotlib.axis_2"):
    a = ax.find(f"s:g[@id='{axis_id}']", N)
    for g in a.iter(f"{{{NS}}}g"):
        pass
    for t in [g for g in a.iter(f"{{{NS}}}g") if (g.get("id") or "").startswith("text_")]:
        t.getparent().remove(t); removed.append(t.get("id"))
tree.write(OUT, xml_declaration=True, encoding="utf-8")
print(len(removed), "groups removed")
