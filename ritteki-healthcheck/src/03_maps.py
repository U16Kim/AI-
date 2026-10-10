"""立適ヘルスチェック:1市の主題図を個別のJPEGで出力する(ダッシュボード用)。

使い方:  python src/03_maps.py 41207 [出力先フォルダ]
前提:    src/02_indicators.py を実行済みで、data_work/<コード>.gpkg があること
出力:    <出力先>/<名前>.jpg(幅880px)。既定の出力先は output/maps/

地図はすべて同じ範囲・同じ凡例の位置で描く(比較しやすくするため)。
"""
import sys
import warnings
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from matplotlib import font_manager

warnings.filterwarnings("ignore")
# 日本語フォント(見つかったものを使う)。指定しないと文字が四角(豆腐)になる。
for cand in ["IPAexGothic", "IPAGothic", "Noto Sans CJK JP", "WenQuanYi Zen Hei", "Unifont JP"]:
    if any(f.name == cand for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = cand
        print("font:", cand)
        break
plt.rcParams["axes.unicode_minus"] = False

ROOT = Path(__file__).resolve().parents[1]
CITY = sys.argv[1] if len(sys.argv) > 1 else "41207"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "output" / "maps"
OUT.mkdir(parents=True, exist_ok=True)
GPKG = ROOT / "data_work" / f"{CITY}.gpkg"

# 02_indicators.py がこの順で hazard_0.. を書き出している
HAZ_LAYERS = {"slide": "hazard_0", "flood_max": "hazard_1", "flood_plan": "hazard_2"}

PAPER = "#eef1f4"      # 地図の地色(寒色寄りの灰)
INK = "#1f2933"
RED, PURPLE, GREY = "#c0392b", "#6d3fc0", "#7b8794"
BLUE, AMBER, TEAL = "#2f6fdd", "#e08a00", "#0f8b8d"

layers = {name: gpd.read_file(GPKG, layer=name) for name in gpd.list_layers(GPKG)["name"]}
crs = layers["city"].crs
zone = {int(n.split("_")[1]): g for n, g in layers.items() if n.startswith("zone_")}
city, mesh = layers["city"], layers["mesh500"]
med, wel, bus = layers["medical"], layers["welfare"], layers["bus"]
haz = {k: layers[v] for k, v in HAZ_LAYERS.items() if v in layers}

x0, y0, x1, y1 = zone[2].buffer(2500).total_bounds
W_IN = 8.8
H_IN = W_IN * (y1 - y0) / (x1 - x0)
mesh["area_ha"] = mesh.geometry.area / 1e4


def base(title_note):
    fig, ax = plt.subplots(figsize=(W_IN, H_IN), dpi=100)
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect("equal")
    ax.set_axis_off()
    fig.subplots_adjust(0, 0, 1, 1)
    return fig, ax


def frame(ax, handles, mesh_label=None):
    city.boundary.plot(ax=ax, color=INK, linewidth=0.8, zorder=5)
    if 1 in zone:
        zone[1].boundary.plot(ax=ax, color=GREY, linewidth=1.0, linestyle="--", zorder=6)
    zone[2].boundary.plot(ax=ax, color=RED, linewidth=2.2, zorder=7)
    if 3 in zone:
        zone[3].boundary.plot(ax=ax, color=PURPLE, linewidth=2.2, zorder=7)
    hs = [Line2D([0], [0], color=RED, lw=2.2, label="居住誘導区域")]
    if 3 in zone:
        hs.append(Line2D([0], [0], color=PURPLE, lw=2.2, label="都市機能誘導区域"))
    hs += handles
    leg = ax.legend(handles=hs, loc="lower left", fontsize=9, frameon=True, framealpha=0.92, facecolor="white", edgecolor="#cbd2d9")
    leg.set_zorder(20)
    # 縮尺(1km)
    sx, sy = x0 + (x1 - x0) * 0.62, y0 + (y1 - y0) * 0.05
    ax.plot([sx, sx + 1000], [sy, sy], color=INK, lw=3, solid_capstyle="butt", zorder=21)
    ax.text(sx + 500, sy + (y1 - y0) * 0.012, "1 km", ha="center", va="bottom", fontsize=9, color=INK, zorder=21)
    ax.text(x1 - (x1 - x0) * 0.012, y0 + (y1 - y0) * 0.012, "出典:国土数値情報", ha="right", va="bottom", fontsize=7.5, color="#52606d", zorder=21)


def save(fig, name):
    p = OUT / f"{name}.jpg"
    fig.savefig(p, dpi=100, format="jpg", pil_kwargs=dict(quality=80, optimize=True), facecolor=PAPER)
    plt.close(fig)
    print("OK", p.name, f"{p.stat().st_size/1024:.0f}KB")


def choropleth(name, values, vmin, vmax, cmap, cbar_label):
    fig, ax = base("")
    m = mesh.assign(v=values)
    m = m[m["v"].notna()]
    m.plot(ax=ax, column="v", cmap=cmap, vmin=vmin, vmax=vmax, linewidth=0.15, edgecolor="#ffffff", zorder=2)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin, vmax))
    cax = fig.add_axes([0.93, 0.18, 0.018, 0.5])
    cb = fig.colorbar(sm, cax=cax)
    cb.set_label(cbar_label, fontsize=9, color=INK)
    cb.ax.tick_params(labelsize=8, colors=INK)
    cb.outline.set_edgecolor("#cbd2d9")
    frame(ax, [])
    save(fig, name)


dens = lambda y: mesh[f"PTN_{y}"] / mesh["area_ha"]
cap = float(np.ceil(max(dens(2020).max(), dens(2050).max())))
choropleth("pop_2020", dens(2020), 0, cap, "Blues", "人口密度 2020年(人/ha)")
choropleth("pop_2050", dens(2050), 0, cap, "Blues", "人口密度 2050年 推計(人/ha)")
share = (mesh["PTC_2040"] / mesh["PTN_2040"].where(mesh["PTN_2040"] > 0)) * 100
choropleth("aging_2040", share, 20, 70, "YlOrBr", "65歳以上割合 2040年 推計(%)")


def hazard(name, key, color, label):
    fig, ax = base("")
    mesh.plot(ax=ax, color="#ffffff", linewidth=0.15, edgecolor="#dde3e8", zorder=1)
    if key in haz:
        haz[key].plot(ax=ax, color=color, alpha=0.55, linewidth=0, zorder=3)
    frame(ax, [Patch(facecolor=color, alpha=0.55, label=label)])
    save(fig, name)


hazard("flood_max", "flood_max", BLUE, "洪水浸水想定(想定最大規模)")
hazard("flood_plan", "flood_plan", TEAL, "洪水浸水想定(計画規模)")
hazard("landslide", "slide", AMBER, "土砂災害警戒区域等")

# バス停300m圏
fig, ax = base("")
mesh.plot(ax=ax, color="#ffffff", linewidth=0.15, edgecolor="#dde3e8", zorder=1)
buf = gpd.GeoDataFrame(geometry=[bus.buffer(300).union_all()], crs=crs)
buf.plot(ax=ax, color=TEAL, alpha=0.35, linewidth=0, zorder=3)
bus.plot(ax=ax, color=INK, markersize=7, zorder=8)
frame(ax, [Patch(facecolor=TEAL, alpha=0.35, label="バス停から300m圏"), Line2D([0], [0], marker="o", color="w", markerfacecolor=INK, markersize=6, label="バス停")])
save(fig, "bus_300")

# 医療・福祉・バス停の分布
fig, ax = base("")
mesh.plot(ax=ax, color="#ffffff", linewidth=0.15, edgecolor="#dde3e8", zorder=1)
bus.plot(ax=ax, color="#9aa5b1", markersize=5, zorder=4)
wel.plot(ax=ax, color=AMBER, marker="s", markersize=24, edgecolor="white", linewidth=0.5, zorder=6)
med.plot(ax=ax, color=BLUE, marker="o", markersize=34, edgecolor="white", linewidth=0.6, zorder=8)
frame(ax, [
    Line2D([0], [0], marker="o", color="w", markerfacecolor=BLUE, markersize=8, label="医療機関(2020年)"),
    Line2D([0], [0], marker="s", color="w", markerfacecolor=AMBER, markersize=7, label="福祉施設(2023年)"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="#9aa5b1", markersize=5, label="バス停(2022年)"),
])
save(fig, "facilities")
