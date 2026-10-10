"""立適ヘルスチェックの数字から、住宅・交通・福祉の政策提言に使う「根拠の数字」を追加で計算する。

使い方:  python src/04_policy_evidence.py 41207
前提:    src/01_download.py、src/02_indicators.py を実行済みであること
出力:    output/policy_evidence_<コード>.csv(ダッシュボード用。列は indicators と同じ)

追加する指標(すべて面積按分の近似。500mメッシュ人口を、メッシュと各区域の重なり面積で按分する):
  住宅: 区域外のハザード区域内人口、区域内で洪水想定外の面積と人口密度
  交通: バス停300m圏外にいる高齢者(65歳以上・75歳以上)の人口
  福祉: 福祉施設・医療機関のうち、浸水想定区域・土砂災害警戒区域内にある数、75歳以上人口の施設アクセス
全市の災害区域は、02_indicators.py(居住誘導区域の周辺だけ)と違い、市全域で作り直す。
"""
import glob
import sys
import warnings
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
RAW, WORK, OUT = ROOT / "data_raw", ROOT / "data_work", ROOT / "output"
CITY = sys.argv[1] if len(sys.argv) > 1 else "41207"
BUS_M, WEL_M = 300, 500  # 徒歩圏の仮定。評価の目的に応じて変更する。

SRC_POP = "国土数値情報 500mメッシュ別将来推計人口(R6国政局推計)"
SRC_HZ = "国土数値情報 土砂災害警戒区域(2025年)、洪水浸水想定区域(2025年度)"
SRC_FAC = {"med": "国土数値情報 医療機関(2020年)", "wel": "国土数値情報 福祉施設(2023年)", "bus": "国土数値情報 バス停留所(2022年)"}
APPROX = "面積按分(近似)。区域内で人が一様に住むと仮定"


def read_one(pattern, **kw):
    files = sorted(f for f in glob.glob(str(RAW / pattern), recursive=True) if f.lower().endswith(".geojson"))
    if not files:
        raise FileNotFoundError(pattern)
    return gpd.read_file(files[0], **kw)


# ------------------------------------------------------------ 入力
n03 = read_one("N03-*/**/*.geojson")
city = n03[n03["N03_007"] == CITY].dissolve()
crs = city.estimate_utm_crs()
city_m = city.to_crs(crs)
city_geom = city_m.geometry.iloc[0]

a50 = read_one(f"A50-20_*/**/A50-20_{CITY}.geojson").to_crs(crs)
zone2 = a50[a50["A50_006"].astype(int) == 2].dissolve()[["geometry"]]

cols = ["PTN_2020", "PTC_2025", "PTC_2040", "PTD_2025", "PTD_2040"]
mesh = read_one("500m_mesh_2024_*/**/*.geojson").to_crs(crs)[["MESH_ID"] + cols + ["geometry"]]
mesh[cols] = mesh[cols].fillna(0)
mesh["a"] = mesh.geometry.area
pc = gpd.overlay(mesh, city_m[["geometry"]], how="intersection", keep_geom_type=True)
pc["w"] = pc.geometry.area / pc["a"]          # メッシュのうち市域に入る割合
pc["pa"] = pc.geometry.area


def pts(pattern):
    g = read_one(pattern).to_crs(crs)
    return g[g.within(city_geom)].copy()


med, wel, bus = pts("P04-*/**/*.geojson"), pts("P14-*/**/*.geojson"), pts("P11-*/**/*.geojson")

# 市全域の災害区域(市の外接矩形で読み、1つに合成)
b = city.to_crs(6668).total_bounds
bbox = (b[0] - 0.005, b[1] - 0.005, b[2] + 0.005, b[3] + 0.005)


def union(files):
    parts = [gpd.read_file(f, bbox=bbox).to_crs(crs)[["geometry"]] for f in files]
    parts = [p for p in parts if len(p)]
    g = gpd.GeoDataFrame(geometry=[pd.concat(parts).geometry.union_all()], crs=crs)
    g["geometry"] = g.intersection(city_geom)
    return g


slide = union(sorted(glob.glob(str(RAW / "A33-25_*/**/*.geojson"), recursive=True)))
fmax_files = sorted(glob.glob(str(RAW / "A31b-25_*/**/*A31b-20-25_*.geojson"), recursive=True))
if not fmax_files:  # 0件のまま計算を進めない(02_indicators.py と同じ理由)
    sys.exit("洪水浸水想定区域のファイルが見つかりません。src/01_download.py に1次メッシュ番号を指定して取得してください。")
fmax = union(fmax_files)

bus_buf = gpd.GeoDataFrame(geometry=[bus.buffer(BUS_M).union_all()], crs=crs)
wel_buf = gpd.GeoDataFrame(geometry=[wel.buffer(WEL_M).union_all()], crs=crs)


# ------------------------------------------------------------ 面積按分
def inter(a, b):
    return gpd.overlay(a, b, how="intersection", keep_geom_type=True)


def pop_in(region, col):
    """市域のうち region に入る人口(col列)を、メッシュの重なり面積で按分して合計する。"""
    p = gpd.overlay(pc[["MESH_ID", col, "w", "pa", "geometry"]], region[["geometry"]], how="intersection", keep_geom_type=True)
    if p.empty:
        return 0.0
    return float((p[col] * p["w"] * (p.geometry.area / p["pa"])).sum())


def pop_total(col):
    return float((pc[col] * pc["w"]).sum())


rows = []


def add(group, iid, name, year, value, unit, source, note=APPROX):
    rows.append(dict(id=iid, group=group, indicator=name, year=year, value=round(float(value), 4), unit=unit, source=source, note=note))


HZ = {"fmax": ("洪水浸水想定区域(想定最大規模)", fmax), "slide": ("土砂災害警戒区域等", slide)}
tot20 = pop_total("PTN_2020")
add("住宅", "h_pop_city", "全市人口(市域で按分)", 2020, tot20, "人", SRC_POP, "02_indicators.py の市コード集計とは端数が異なる")
z2_pop = pop_in(zone2, "PTN_2020")
for k, (label, hz) in HZ.items():
    all_in = pop_in(hz, "PTN_2020")
    in_z2 = pop_in(inter(hz, zone2), "PTN_2020")
    add("住宅", f"h_pop_{k}_city", f"{label}内の人口", 2020, all_in, "人", SRC_POP + " / " + SRC_HZ)
    add("住宅", f"h_pop_{k}_city_share", f"全市人口のうち{label}内の割合", 2020, 100 * all_in / tot20, "%", SRC_POP + " / " + SRC_HZ)
    if k == "fmax":
        fmax_in_z2, fmax_out_z2 = in_z2, all_in - in_z2
    add("住宅", f"h_pop_{k}_out_z2", f"居住誘導区域外の{label}内の人口", 2020, all_in - in_z2, "人", SRC_POP + " / " + SRC_HZ, APPROX + "。区域外=全市−区域内")
    add("住宅", f"h_pop_{k}_out_z2_share", f"全市人口のうち、居住誘導区域外の{label}内にいる割合", 2020, 100 * (all_in - in_z2) / tot20, "%", SRC_POP + " / " + SRC_HZ)

# 居住誘導区域内で、想定最大規模の洪水の浸水想定外の部分(受け皿になりうる部分)
safe = gpd.overlay(zone2, fmax, how="difference", keep_geom_type=True)
safe_ha = safe.geometry.area.sum() / 1e4
safe_pop = pop_in(safe, "PTN_2020")
add("住宅", "h_z2_safe_area", "居住誘導区域のうち、洪水浸水想定(想定最大規模)の外の面積", 2020, safe_ha, "ha", SRC_HZ)
add("住宅", "h_z2_safe_pop", "同、その中の人口", 2020, safe_pop, "人", SRC_POP + " / " + SRC_HZ)
add("住宅", "h_z2_safe_dens", "同、人口密度", 2020, safe_pop / safe_ha, "人/ha", SRC_POP + " / " + SRC_HZ)

# 人口の居場所(4つの区分。合計は全市人口に一致する)
seg = {
    "h_seg_in_safe": ("居住誘導区域内で、洪水浸水想定(想定最大規模)の外にいる人口", safe_pop),
    "h_seg_in_flood": ("居住誘導区域内で、洪水浸水想定(想定最大規模)の中にいる人口", fmax_in_z2),
    "h_seg_out_flood": ("居住誘導区域外で、洪水浸水想定(想定最大規模)の中にいる人口", fmax_out_z2),
    "h_seg_out_safe": ("居住誘導区域外で、洪水浸水想定(想定最大規模)の外にいる人口", tot20 - z2_pop - fmax_out_z2),
}
gap = abs(safe_pop + fmax_in_z2 - z2_pop)
assert gap < 0.01 * z2_pop, f"区域内の内訳が合計と合いません(差{gap:.1f}人)"  # 面積の重なりの端数を超える差が出たら停止
for iid, (name, v) in seg.items():
    add("住宅", iid, name, 2020, v, "人", SRC_POP + " / " + SRC_HZ, APPROX)

# 交通
for y in (2025, 2040):
    for col, lab in (("PTC", "65歳以上"), ("PTD", "75歳以上")):
        c = f"{col}_{y}"
        tot = pop_total(c)
        inn = pop_in(bus_buf, c)
        add("交通", f"t_{col.lower()}_{y}_total", f"{lab}の人口(全市)", y, tot, "人", SRC_POP)
        add("交通", f"t_{col.lower()}_{y}_out", f"{lab}の人口のうち、バス停{BUS_M}m圏の外にいる人", y, tot - inn, "人", SRC_POP + " / " + SRC_FAC["bus"], APPROX + "。直線距離。運行本数は見ていない")
        add("交通", f"t_{col.lower()}_{y}_out_share", f"{lab}の人口のうち、バス停{BUS_M}m圏の外にいる割合", y, 100 * (tot - inn) / tot, "%", SRC_POP + " / " + SRC_FAC["bus"], APPROX + "。直線距離。運行本数は見ていない")
bus_in = pop_in(bus_buf, "PTN_2020")
add("交通", "t_cov_city", f"全市人口のうち、バス停{BUS_M}m圏内にいる割合", 2020, 100 * bus_in / tot20, "%", SRC_POP + " / " + SRC_FAC["bus"], APPROX + "。直線距離")
bus_in_z2 = pop_in(inter(bus_buf, zone2), "PTN_2020")
add("交通", "t_cov_out_z2", f"居住誘導区域外の人口のうち、バス停{BUS_M}m圏内にいる割合", 2020, 100 * (bus_in - bus_in_z2) / (tot20 - z2_pop), "%", SRC_POP + " / " + SRC_FAC["bus"], APPROX + "。区域外=全市−区域内")
add("交通", "t_out_city_share", f"全市人口のうち、バス停{BUS_M}m圏の外にいる割合", 2020, 100 - 100 * bus_in / tot20, "%", SRC_POP + " / " + SRC_FAC["bus"], APPROX + "。直線距離")
add("交通", "t_out_z2_share", f"居住誘導区域内の人口のうち、バス停{BUS_M}m圏の外にいる割合", 2020, 100 - 100 * bus_in_z2 / z2_pop, "%", SRC_POP + " / " + SRC_FAC["bus"], APPROX + "。直線距離")
add("交通", "t_out_outz2_share", f"居住誘導区域外の人口のうち、バス停{BUS_M}m圏の外にいる割合", 2020, 100 - 100 * (bus_in - bus_in_z2) / (tot20 - z2_pop), "%", SRC_POP + " / " + SRC_FAC["bus"], APPROX + "。区域外=全市−区域内")
fm = fmax.geometry.iloc[0]
shapely.prepare(fm)
n_bus_f = int(shapely.intersects(bus.geometry.values, fm).sum())
add("交通", "t_bus_in_fmax", "バス停のうち、洪水浸水想定(想定最大規模)の区域内にある割合", 2022, 100 * n_bus_f / len(bus), "%", SRC_FAC["bus"] + " / " + SRC_HZ, "点が区域内か否か。深さは区別しない")

# 福祉・医療
sl = slide.geometry.iloc[0]
shapely.prepare(sl)
for key, g, lab, yr in (("wel", wel, "福祉施設", 2023), ("med", med, "医療機関", 2020)):
    n = len(g)
    for hk, geom, hl in (("fmax", fm, "洪水浸水想定(想定最大規模)の区域内"), ("slide", sl, "土砂災害警戒区域等の区域内")):
        c = int(shapely.intersects(g.geometry.values, geom).sum())
        add("福祉", f"w_{key}_in_{hk}", f"{lab}のうち、{hl}にある数", yr, c, "件", SRC_FAC[key] + " / " + SRC_HZ, "点が区域内か否か。深さ・種別は区別しない")
        add("福祉", f"w_{key}_in_{hk}_share", f"{lab}のうち、{hl}にある割合", yr, 100 * c / n, "%", SRC_FAC[key] + " / " + SRC_HZ, "点が区域内か否か。深さ・種別は区別しない")
t75 = pop_total("PTD_2040")
add("福祉", "w_old75_2040", "75歳以上の人口(2040年・全市)", 2040, t75, "人", SRC_POP)
add("福祉", "w_old75_z2_share", "75歳以上の人口のうち、居住誘導区域内にいる割合", 2040, 100 * pop_in(zone2, "PTD_2040") / t75, "%", SRC_POP + " / " + "国土数値情報 立地適正化計画区域データ", APPROX)
add("福祉", "w_old75_wel_share", f"75歳以上の人口のうち、福祉施設から{WEL_M}m圏内にいる割合", 2040, 100 * pop_in(wel_buf, "PTD_2040") / t75, "%", SRC_POP + " / " + SRC_FAC["wel"], APPROX + "。施設の種別は区別しない。直線距離")

df = pd.DataFrame(rows)
df.to_csv(OUT / f"policy_evidence_{CITY}.csv", index=False, encoding="utf-8")
pd.set_option("display.width", 220, "display.max_colwidth", 60)
print(df[["group", "id", "year", "value", "unit"]].to_string(index=False))
