"""立適ヘルスチェック:国土数値情報だけで計算できる指標を、1市について出力する。

使い方:  python src/02_indicators.py 41207      (引数は市区町村コード。鹿島市=41207)
前提:    src/01_download.py で data_raw/ にデータを取得済みであること
出力:    output/indicators_<コード>.csv / .xlsx、output/<コード>_map.png、output/<コード>_population.png、
         data_work/<コード>.gpkg(QGISで開ける)

方法の要点(誤解を避けるための前提):
  * 人口は国土数値情報の500mメッシュ(R6国政局推計)。区域内人口は「メッシュ内で人口が一様」と仮定し、
    メッシュと区域の重なり面積の比で按分する(面積按分)。区域の境界付近では誤差が出る。
  * 年齢別人口は2025年以降の推計のみ(2020年は総数のみ)。
  * 立地適正化計画区域データは2020年12月31日時点。その後の変更は反映されない。
"""
import glob
import sys
import warnings
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
RAW, WORK, OUT = ROOT / "data_raw", ROOT / "data_work", ROOT / "output"
WORK.mkdir(exist_ok=True)
OUT.mkdir(exist_ok=True)

CITY = sys.argv[1] if len(sys.argv) > 1 else "41207"
YEARS = [2020, 2025, 2030, 2035, 2040, 2045, 2050]
BUS_BUFFER_M = 300  # バス停の徒歩圏。評価の目的に応じて変更する。
ZONE_NAME = {1: "立地適正化計画区域", 2: "居住誘導区域", 3: "都市機能誘導区域"}

# ---- 日本語フォント(見つかったものを使う) ----
for cand in ["IPAexGothic", "IPAGothic", "Noto Sans CJK JP", "WenQuanYi Zen Hei", "Unifont JP"]:
    if any(f.name == cand for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.family"] = cand
        break
plt.rcParams["axes.unicode_minus"] = False


def read_one(pattern: str, **kw) -> gpd.GeoDataFrame:
    files = sorted(f for f in glob.glob(str(RAW / pattern), recursive=True) if f.lower().endswith(".geojson"))
    if not files:
        raise FileNotFoundError(pattern)
    return gpd.read_file(files[0], **kw)


rows: list[dict] = []


def add(group, name, year, value, unit, source, note=""):
    rows.append(dict(区分=group, 指標=name, 年=year, 値=None if value is None else float(value), 単位=unit, 出典=source, 注記=note))


# ---------------------------------------------------------------- 入力
n03 = read_one("N03-*/**/*.geojson")
city = n03[n03["N03_007"] == CITY].dissolve()
if city.empty:
    sys.exit(f"市区町村コード {CITY} が行政区域データにありません")
city_name = (n03[n03["N03_007"] == CITY]["N03_004"].iloc[0])
crs_m = city.estimate_utm_crs()
city_m = city.to_crs(crs_m)
city_geom = city_m.geometry.iloc[0]

a50 = read_one(f"A50-20_*/**/A50-20_{CITY}.geojson").to_crs(crs_m)
a50["zone"] = a50["A50_006"].astype(int)
zones = {z: a50[a50["zone"] == z].dissolve()[["geometry"]] for z in ZONE_NAME if (a50["zone"] == z).any()}
if 2 not in zones:
    sys.exit(f"{city_name}は、国土数値情報(2020年12月末時点)に居住誘導区域がありません")
zone_ha = {z: g.geometry.area.sum() / 1e4 for z, g in zones.items()}

mesh = read_one("500m_mesh_2024_*/**/*.geojson").to_crs(crs_m)
pt_cols = [f"PTN_{y}" for y in YEARS] + [f"PTC_{y}" for y in YEARS if y >= 2025] + [f"PTA_{y}" for y in YEARS if y >= 2025]
mesh = mesh[["MESH_ID", "SHICODE"] + pt_cols + ["geometry"]].copy()
mesh[pt_cols] = mesh[pt_cols].fillna(0)
mesh["mesh_area"] = mesh.geometry.area
city_mesh = mesh[mesh["SHICODE"].astype(str) == CITY]

SRC_POP = "国土数値情報 500mメッシュ別将来推計人口(R6国政局推計)"
SRC_A50 = "国土数値情報 立地適正化計画区域データ(2020年12月31日時点)"

# ---------------------------------------------------------------- 面積按分で区域内人口
def pieces_in(zone_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    p = gpd.overlay(mesh, zone_gdf, how="intersection", keep_geom_type=True)
    p["w"] = p.geometry.area / p["mesh_area"]
    return p


piece = {z: pieces_in(g) for z, g in zones.items()}
city_pop = {y: city_mesh[f"PTN_{y}"].sum() for y in YEARS}
zone_pop = {z: {y: (p["w"] * p[f"PTN_{y}"]).sum() for y in YEARS} for z, p in piece.items()}

for y in YEARS:
    add("人口", "全市人口(メッシュ合計)", y, city_pop[y], "人", SRC_POP, "市コードで集計。国勢調査の公表値とは端数が異なる場合がある")
for z, name in ZONE_NAME.items():
    if z not in zones:
        continue
    add("区域", f"{name}の面積", 2020, zone_ha[z], "ha", SRC_A50)
    for y in YEARS:
        add("人口", f"{name}内人口", y, zone_pop[z][y], "人", SRC_POP, "面積按分(近似)")
        add("人口", f"{name}内人口の市全体に占める割合", y, 100 * zone_pop[z][y] / city_pop[y], "%", SRC_POP, "面積按分(近似)")
        add("人口", f"{name}の人口密度", y, zone_pop[z][y] / zone_ha[z], "人/ha", SRC_POP, "面積按分(近似)")

# 高齢化(2025年以降)
for y in [y for y in YEARS if y >= 2025]:
    p2 = piece[2]
    old_in = (p2["w"] * p2[f"PTC_{y}"]).sum()
    pop_in = zone_pop[2][y]
    old_city = city_mesh[f"PTC_{y}"].sum()
    old_out = old_city - old_in
    pop_out = city_pop[y] - pop_in
    add("高齢化", "居住誘導区域内の65歳以上割合", y, 100 * old_in / pop_in, "%", SRC_POP, "面積按分(近似)")
    add("高齢化", "居住誘導区域外の65歳以上割合", y, 100 * old_out / pop_out, "%", SRC_POP, "市全体−区域内(近似)")
    add("高齢化", "全市の65歳以上割合", y, 100 * old_city / city_pop[y], "%", SRC_POP)

# ---------------------------------------------------------------- 生活サービス施設
def points(pattern):
    g = read_one(pattern).to_crs(crs_m)
    return g[g.within(city_geom)].copy()


med = points("P04-*/**/*.geojson")
wel = points("P14-*/**/*.geojson")
bus = points("P11-*/**/*.geojson")
SRC_FAC = {"医療機関": "国土数値情報 医療機関(2020年)", "福祉施設": "国土数値情報 福祉施設(2023年)", "バス停": "国土数値情報 バス停留所(2022年)"}
for label, pts in [("医療機関", med), ("福祉施設", wel), ("バス停", bus)]:
    add("施設", f"{label}数(全市)", 2020, len(pts), "件", SRC_FAC[label], "データ年次は出典欄のとおり。同一施設の重複や廃止は未確認")
    for z in (2, 3):
        if z in zones:
            n = pts.within(zones[z].geometry.iloc[0]).sum()
            add("施設", f"{label}数({ZONE_NAME[z]}内)", 2020, n, "件", SRC_FAC[label])
            add("施設", f"{label}の{ZONE_NAME[z]}内割合", 2020, 100 * n / len(pts) if len(pts) else None, "%", SRC_FAC[label])

# バス停から300m圏の人口カバー率(居住誘導区域内)
bus_buf = gpd.GeoDataFrame(geometry=[bus.buffer(BUS_BUFFER_M).union_all()], crs=crs_m)
p2 = piece[2].copy()
p2["piece_area"] = p2.geometry.area
cov = gpd.overlay(p2[["MESH_ID", "piece_area", "w", "PTN_2020", "geometry"]], bus_buf, how="intersection", keep_geom_type=True)
cov["ratio"] = cov.geometry.area / cov["piece_area"]
pop2020_cov = (cov["w"] * cov["PTN_2020"] * cov["ratio"]).sum()
add("交通", f"居住誘導区域内人口のうち、バス停{BUS_BUFFER_M}m圏内の割合", 2020, 100 * pop2020_cov / zone_pop[2][2020], "%", SRC_FAC["バス停"] + " ×500mメッシュ",
    "直線距離。運行本数・路線の廃止は考慮していない")

# ---------------------------------------------------------------- 災害リスクとの重なり
minx, miny, maxx, maxy = zones[2].to_crs(6668).total_bounds
pad = 0.02
bbox = (minx - pad, miny - pad, maxx + pad, maxy + pad)


def hazard_union(files, label):
    parts = []
    for f in files:
        g = gpd.read_file(f, bbox=bbox)
        if len(g):
            parts.append(g.to_crs(crs_m)[["geometry"]])
    if not parts:
        return None
    return gpd.GeoDataFrame(geometry=[pd.concat(parts).geometry.union_all()], crs=crs_m)


haz = {}
a33_file = sorted(glob.glob(str(RAW / "A33-25_*/**/*.geojson"), recursive=True))[0]
haz["土砂災害警戒区域等"] = (hazard_union([a33_file], "A33"), "国土数値情報 土砂災害警戒区域(2025年)")
# 洪水データのzipはWindows形式で、ファイル名に「20_想定最大規模\」のようなフォルダ名が混ざっている。先頭の * が必要。
fl_max = sorted(glob.glob(str(RAW / "A31b-25_*/**/*A31b-20-25_*.geojson"), recursive=True))
fl_plan = sorted(glob.glob(str(RAW / "A31b-25_*/**/*A31b-10-25_*.geojson"), recursive=True))
if not fl_max or not fl_plan:  # 0件のまま「重なり0%」と出力しないための停止
    sys.exit("洪水浸水想定区域のファイルが見つかりません。src/01_download.py に1次メッシュ番号を指定して取得してください。")
print(f"洪水データ: 想定最大規模 {len(fl_max)}ファイル / 計画規模 {len(fl_plan)}ファイル")
haz["洪水浸水想定区域(想定最大規模)"] = (hazard_union(fl_max, "max"), "国土数値情報 洪水浸水想定区域(2025年度)")
haz["洪水浸水想定区域(計画規模)"] = (hazard_union(fl_plan, "plan"), "国土数値情報 洪水浸水想定区域(2025年度)")

zone2 = zones[2]
haz_clip = {}
for name, (hz, src) in haz.items():
    if hz is None:
        add("災害", f"居住誘導区域と{name}の重なり(面積割合)", 2020, 0, "%", src, "対象データなし(該当の1次メッシュに区域がない)")
        continue
    inter = gpd.overlay(zone2, hz, how="intersection", keep_geom_type=True)
    area_share = 100 * (inter.geometry.area.sum() / zone2.geometry.area.sum()) if len(inter) else 0
    pc = gpd.overlay(p2[["MESH_ID", "piece_area", "w", "PTN_2020", "geometry"]], hz, how="intersection", keep_geom_type=True)
    pc["ratio"] = pc.geometry.area / pc["piece_area"]
    pop_in_h = (pc["w"] * pc["PTN_2020"] * pc["ratio"]).sum()
    add("災害", f"居住誘導区域と{name}の重なり(面積割合)", 2020, area_share, "%", src + " / " + SRC_A50, "浸水深・警戒区域の種別は区別していない")
    add("災害", f"居住誘導区域内人口のうち{name}内の割合", 2020, 100 * pop_in_h / zone_pop[2][2020], "%", src + " / " + SRC_POP,
        "面積按分(近似)。区域内の人口分布が一様と仮定")
    haz_clip[name] = hz

# ---------------------------------------------------------------- 出力(表)
df = pd.DataFrame(rows)
df.insert(0, "市区町村", f"{city_name}({CITY})")
df.to_csv(OUT / f"indicators_{CITY}.csv", index=False, encoding="utf-8-sig")
notes = pd.DataFrame({"注意事項": [
    "人口は国土数値情報の500mメッシュ(R6国政局推計)を面積按分した近似値です。区域の境界付近で誤差が出ます。",
    "立地適正化計画区域データは2020年12月31日時点です。その後の計画変更は反映されません。",
    "災害データは区域・規模の別を区別していない集計です。評価書に使う前に、自治体の最新ハザード情報で確認してください。",
    "出典の利用条件は国土数値情報の利用規約と、市町村ごとの利用条件(立地適正化計画区域データ)に従います。",
]})
with pd.ExcelWriter(OUT / f"indicators_{CITY}.xlsx") as xw:
    df.to_excel(xw, sheet_name="指標", index=False)
    notes.to_excel(xw, sheet_name="注意事項", index=False)

# ---------------------------------------------------------------- 出力(QGIS用)
gpkg = WORK / f"{CITY}.gpkg"
if gpkg.exists():
    gpkg.unlink()
for z, g in zones.items():
    g.assign(zone=ZONE_NAME[z]).to_file(gpkg, layer=f"zone_{z}_{ZONE_NAME[z]}", driver="GPKG")
city_m.to_file(gpkg, layer="city", driver="GPKG")
mesh[mesh.intersects(city_geom)].to_file(gpkg, layer="mesh500", driver="GPKG")
for label, pts in [("medical", med), ("welfare", wel), ("bus", bus)]:
    pts[["geometry"]].to_file(gpkg, layer=label, driver="GPKG")
for i, (name, hz) in enumerate(haz_clip.items()):
    hz.to_file(gpkg, layer=f"hazard_{i}", driver="GPKG")

# ---------------------------------------------------------------- 出力(図)
x0, y0, x1, y1 = zones[2].buffer(2500).total_bounds
fig, ax = plt.subplots(figsize=(8, 8 * (y1 - y0) / (x1 - x0) + 0.8))
m_show = mesh[mesh.intersects(city_geom)].copy()
m_show["dens"] = m_show["PTN_2020"] / (m_show["mesh_area"] / 1e4)
m_show.plot(ax=ax, column="dens", cmap="Blues", linewidth=0, legend=True, legend_kwds=dict(label="人口密度 2020(人/ha)", shrink=0.6))
city_m.boundary.plot(ax=ax, color="#555", linewidth=0.8)
for name, color in [("洪水浸水想定区域(想定最大規模)", "#3b82f6"), ("土砂災害警戒区域等", "#f59e0b")]:
    if name in haz_clip:
        haz_clip[name].plot(ax=ax, color=color, alpha=0.30, linewidth=0)
if 1 in zones:
    zones[1].boundary.plot(ax=ax, color="#6b7280", linewidth=1.0, linestyle="--")
zones[2].boundary.plot(ax=ax, color="#dc2626", linewidth=2.0)
if 3 in zones:
    zones[3].boundary.plot(ax=ax, color="#7c3aed", linewidth=2.0)
bus.plot(ax=ax, color="#111", markersize=3)
ax.set_xlim(x0, x1)
ax.set_ylim(y0, y1)
ax.set_aspect("equal")
ax.set_axis_off()
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ax.legend(handles=[
    Line2D([0], [0], color="#dc2626", lw=2, label="居住誘導区域"),
    Line2D([0], [0], color="#7c3aed", lw=2, label="都市機能誘導区域"),
    Line2D([0], [0], color="#6b7280", lw=1, ls="--", label="立地適正化計画区域"),
    Patch(color="#3b82f6", alpha=0.3, label="洪水浸水想定(想定最大規模)"),
    Patch(color="#f59e0b", alpha=0.3, label="土砂災害警戒区域等"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="#111", markersize=4, label="バス停"),
], loc="lower left", fontsize=7, framealpha=0.9)
ax.set_title(f"{city_name}  居住誘導区域(赤)・都市機能誘導区域(紫)と人口密度、災害想定、バス停(黒点)", fontsize=10)
fig.text(0.01, 0.01, "出典:国土数値情報(人口:500mメッシュR6推計、区域:2020年末時点、災害:2025年度)。面積按分の近似を含む。", fontsize=7)
fig.savefig(OUT / f"{CITY}_map.png", dpi=150, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 4.5))
inn = np.array([zone_pop[2][y] for y in YEARS])
tot = np.array([city_pop[y] for y in YEARS])
ax.bar(YEARS, inn, width=3, color="#dc2626", label="居住誘導区域内")
ax.bar(YEARS, tot - inn, width=3, bottom=inn, color="#cbd5e1", label="区域外")
for y, a, t in zip(YEARS, inn, tot):
    ax.text(y, t + tot.max() * 0.01, f"{100*a/t:.0f}%", ha="center", fontsize=9)
ax.set_xticks(YEARS)
ax.set_ylabel("人口(人)")
ax.set_title(f"{city_name}  人口推計と居住誘導区域内人口の割合(面積按分)", fontsize=11)
ax.legend(loc="lower left")
fig.text(0.01, 0.0, "出典:国土数値情報 500mメッシュ別将来推計人口(R6国政局推計)", fontsize=7)
fig.savefig(OUT / f"{CITY}_population.png", dpi=150, bbox_inches="tight")
plt.close(fig)

print(df.drop(columns=["出典", "注記"]).to_string(index=False))
