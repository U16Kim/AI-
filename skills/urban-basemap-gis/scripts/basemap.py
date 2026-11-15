"""urban-basemap-gis：行政区域（国土数値情報 N03）＋ OpenStreetMap → ベースマップ作成・可視化・書き出し

使い方（Anaconda/JupyterLab・Google Colab 共通）:
    import sys; sys.path.append("scripts")
    import basemap as bm
    admin = bm.read_n03("data/N03-20260101_14_GML.zip")          # ① 行政区域を読む
    kawasaki = bm.select_area(admin, code_prefix="1413")         # ② 川崎市の7区を選ぶ
    kawasaki = bm.dissolve_admin(kawasaki, level="ward")         #    飛び地・島を区ごとに1つにまとめる
    osm = bm.fetch_osm_layers(kawasaki, ["roads", "rail", "stations", "water", "parks"])   # ③ OSMを取る
    fig = bm.draw_basemap(kawasaki, osm, title="川崎市 ベースマップ")                       # ④ 描く
    bm.export_layers({"admin": kawasaki, **osm}, "output/gis", "kawasaki")                 # ⑤ QGIS/Tableau用に書き出す

データの出典表記（必須）
- 行政区域：国土数値情報（行政区域データ）。ライセンス CC BY 4.0。原典表示は取得ページの最新の記載に従う。
- OSM：© OpenStreetMap contributors（ODbL）
"""
from __future__ import annotations

import glob
import os
import tempfile
import time
import unicodedata
import zipfile
from typing import Dict, Iterable, List, Optional, Sequence

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

WGS84 = "EPSG:4326"
ATTRIBUTION = "行政区域：国土数値情報（CC BY 4.0）／ 地図データ © OpenStreetMap contributors（ODbL）"

# 平面直角座標系（JGD2011）。首都圏4都県はすべてⅨ系（EPSG:6677）。
# ⚠️ 他の都道府県は系が異なる（北海道・沖縄・島しょ部は複数系にまたがる）。国土地理院の対応表で確認すること。
PLANE_CRS_BY_PREF = {"11": 6677, "12": 6677, "13": 6677, "14": 6677}

# 政令指定都市の市コード（区をまとめて「市」として扱うときに使う）。
# ⚠️ 2026年時点で20市を想定。新設・変更は総務省「全国地方公共団体コード」で要確認。
DESIGNATED_CITY_CODES = {
    "札幌市": "01100", "仙台市": "04100", "さいたま市": "11100", "千葉市": "12100", "横浜市": "14100",
    "川崎市": "14130", "相模原市": "14150", "新潟市": "15100", "静岡市": "22100", "浜松市": "22130",
    "名古屋市": "23100", "京都市": "26100", "大阪市": "27100", "堺市": "27140", "神戸市": "28100",
    "岡山市": "33100", "広島市": "34100", "北九州市": "40100", "福岡市": "40130", "熊本市": "43100",
}

# ─────────────────────────────────────────────────────
# 共通ユーティリティ
# ─────────────────────────────────────────────────────
_FONTS = ["IPAexGothic", "IPAGothic", "Noto Sans CJK JP", "Noto Sans JP", "Yu Gothic",
          "Meiryo", "Hiragino Sans", "TakaoGothic", "VL Gothic"]


def setup_japanese_font(verbose: bool = False) -> Optional[str]:
    """matplotlib の日本語表示を設定する（matplotlib-fontja → japanize → 手持ちフォントの順）。"""
    from matplotlib import font_manager
    for mod in ("matplotlib_fontja", "japanize_matplotlib"):
        try:
            __import__(mod)
            plt.rcParams["axes.unicode_minus"] = False
            return mod
        except Exception:
            continue
    installed = {f.name for f in font_manager.fontManager.ttflist}
    for name in _FONTS:
        if name in installed:
            plt.rcParams["font.family"] = name
            plt.rcParams["axes.unicode_minus"] = False
            return name
    plt.rcParams["axes.unicode_minus"] = False
    if verbose:
        print("⚠️ 日本語フォントなし（地図の文字が□になります）。pip install matplotlib-fontja")
    return None


setup_japanese_font()


def to_jis5(code) -> Optional[str]:
    """自治体コードを5桁文字列にする（6桁なら検査数字を除く／先頭0を補う）。変換できなければ None。"""
    if code is None or (isinstance(code, float) and pd.isna(code)):
        return None
    s = unicodedata.normalize("NFKC", str(code).strip())
    if s.endswith(".0"):
        s = s[:-2]
    if not s.isdigit():
        return None
    if len(s) == 6:
        s = s[:5]
    return s.zfill(5) if len(s) <= 5 else None


def pick_local_crs(gdf: gpd.GeoDataFrame, pref_code: Optional[str] = None):
    """面積・距離を測るための投影座標系を選ぶ。首都圏4都県は平面直角座標系Ⅸ系、他は UTM を推定。"""
    if pref_code is None and "都道府県コード" in gdf.columns:
        pref_code = str(gdf["都道府県コード"].mode().iat[0])
    if pref_code and str(pref_code).zfill(2) in PLANE_CRS_BY_PREF:
        return f"EPSG:{PLANE_CRS_BY_PREF[str(pref_code).zfill(2)]}"
    crs = gdf.to_crs(WGS84).estimate_utm_crs()
    print(f"⚠️ 平面直角座標系の対応が未登録のため UTM（{crs.to_string()}）を使います。精密な面積計算は系を確認してください。")
    return crs


# ─────────────────────────────────────────────────────
# ① 行政区域（国土数値情報 N03）
# ─────────────────────────────────────────────────────
def download_n03(pref_code: str, year: int = 2026, out_dir: str = "data") -> str:
    """国土数値情報の行政区域データ（都道府県別zip）をダウンロードする。

    ファイル名は一次情報で確認済み（例：N03-20260101_14_GML.zip、14＝神奈川県）。
    ⚠️ 実際のダウンロードURLは配布ページから読み取れなかったため、下の形式は推定。
       失敗したら配布ページ（https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2026.html）から
       手動でダウンロードし、read_n03() にそのzipのパスを渡す。
    """
    import requests
    os.makedirs(out_dir, exist_ok=True)
    name = f"N03-{year}0101_{str(pref_code).zfill(2)}_GML.zip"
    url = f"https://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-{year}/{name}"
    path = os.path.join(out_dir, name)
    try:
        res = requests.get(url, timeout=120)
        res.raise_for_status()
        if not res.content.startswith(b"PK"):
            raise ValueError("zipではない応答でした")
    except Exception as e:
        raise RuntimeError(
            f"自動ダウンロードに失敗しました（{e}）。手動で取得してください：\n"
            f"  1) https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-{year}.html を開く\n"
            f"  2) 表の「{name}」をクリックして保存する\n"
            f"  3) bm.read_n03('{path}') で読み込む") from e
    with open(path, "wb") as f:
        f.write(res.content)
    print(f"保存：{path}（{len(res.content) / 1e6:.1f} MB）")
    return path


def _vector_files(path: str, workdir: str) -> List[str]:
    """zip／フォルダ／単一ファイルから、読み込み対象のベクターファイルを探す（.shp → .geojson の順に優先）。"""
    if os.path.isfile(path) and path.lower().endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            z.extractall(workdir)
        path = workdir
    if os.path.isdir(path):
        for pattern in ("**/*.shp", "**/*.geojson", "**/*.json"):
            found = sorted(glob.glob(os.path.join(path, pattern), recursive=True))
            if found:
                return found
        raise FileNotFoundError(f"{path} に .shp / .geojson が見つかりません（GMLのみの場合は Shapefile か GeoJSON 版を取得してください）。")
    return [path]


def _read_vector(p: str) -> gpd.GeoDataFrame:
    try:
        return gpd.read_file(p)
    except UnicodeDecodeError:
        return gpd.read_file(p, encoding="cp932")


_N03_RENAME = {"N03_001": "都道府県", "N03_002": "振興局", "N03_003": "郡政令市", "N03_004": "市区町村", "N03_007": "市区町村コード"}


def read_n03(path: str) -> gpd.GeoDataFrame:
    """N03（行政区域）を読み込み、列名を日本語に整える。

    列：都道府県／振興局／郡政令市／市区町村／市区町村コード（5桁文字列）／都道府県コード／geometry
    - N03_001 都道府県名、N03_003 郡・政令指定都市名、N03_004 市区町村名（政令市の区名を含む）、
      N03_007 行政区域コード（5桁）。出典：国土数値情報 製品仕様書。
    - 「所属未定地」など、コードが空の行は除外する（件数を表示）。
    - 座標系：JGD2011（地理座標）。GeoJSON は CRS 記載がなく EPSG:4326 として扱われる（差は実用上無視できる）。
    """
    with tempfile.TemporaryDirectory() as tmp:
        files = _vector_files(path, tmp)
        gdf = pd.concat([_read_vector(f) for f in files], ignore_index=True)
        gdf = gpd.GeoDataFrame(gdf, geometry="geometry", crs=_read_vector(files[0]).crs)
    if gdf.crs is None:
        gdf = gdf.set_crs(WGS84)
    gdf = gdf.rename(columns=_N03_RENAME)
    if "市区町村コード" not in gdf.columns:
        raise ValueError("N03_007（行政区域コード）列が見つかりません。行政区域データ（N03）か確認してください。")
    for c in ("振興局", "郡政令市", "市区町村", "都道府県"):
        if c not in gdf.columns:
            gdf[c] = None
    gdf["市区町村コード"] = gdf["市区町村コード"].map(to_jis5)
    n_null = int(gdf["市区町村コード"].isna().sum())
    if n_null:
        print(f"コードが空の行を除外：{n_null}件（所属未定地など）")
        gdf = gdf[gdf["市区町村コード"].notna()]
    gdf["都道府県コード"] = gdf["市区町村コード"].str[:2]
    keep = ["都道府県", "振興局", "郡政令市", "市区町村", "市区町村コード", "都道府県コード", "geometry"]
    return gdf[keep].reset_index(drop=True)


def select_area(admin: gpd.GeoDataFrame, name: Optional[str] = None,
                codes: Optional[Iterable[str]] = None, code_prefix: Optional[str] = None) -> gpd.GeoDataFrame:
    """対象の自治体だけを取り出す。

    name        : "川崎市"（政令市名）や "川崎区"（区名）。政令市名なら全区が対象になる
    codes       : ["14131", "14132"] のようにコードを列挙
    code_prefix : "1413" → 川崎市の7区（14131〜14137）。"13" → 東京都
    """
    mask = pd.Series(False, index=admin.index)
    if name:
        mask |= (admin["郡政令市"] == name) | (admin["市区町村"] == name)
    if codes:
        mask |= admin["市区町村コード"].isin([to_jis5(c) for c in codes])
    if code_prefix:
        mask |= admin["市区町村コード"].str.startswith(str(code_prefix))
    out = admin[mask].copy()
    if out.empty:
        raise ValueError("該当する行政区域がありません。名称・コードを確認してください（例：name='川崎市'）。")
    return out.reset_index(drop=True)


def dissolve_admin(admin: gpd.GeoDataFrame, level: str = "ward") -> gpd.GeoDataFrame:
    """同じ自治体に属する複数ポリゴン（飛び地・島）を1つにまとめる。

    level="ward" : 市区町村コード単位（政令市は区単位）。既定。
    level="city" : 政令市の区を市にまとめる（川崎市7区 → 川崎市1つ）。市コードは政令市の表で補う。
    戻り値の列に 表示名（地図ラベル用）を追加する。
    """
    if level not in ("ward", "city"):
        raise ValueError("level は ward か city。")
    g = admin.copy()
    if level == "city":
        is_ward = g["郡政令市"].fillna("").str.endswith("市") & g["市区町村"].fillna("").str.endswith("区")
        g["市区町村"] = np.where(is_ward, g["郡政令市"], g["市区町村"])
        new_code = g["郡政令市"].map(DESIGNATED_CITY_CODES)
        missing = is_ward & new_code.isna()
        if missing.any():
            names = sorted(g.loc[missing, "郡政令市"].unique())
            print(f"⚠️ 政令市コードの表にない市があります：{names}。区のコードのまま扱います。")
        g["市区町村コード"] = np.where(is_ward & new_code.notna(), new_code, g["市区町村コード"])
    out = g.dissolve(by="市区町村コード", aggfunc={"都道府県": "first", "郡政令市": "first",
                                                  "市区町村": "first", "都道府県コード": "first"}).reset_index()
    out["表示名"] = out["市区町村"]
    return gpd.GeoDataFrame(out, geometry="geometry", crs=admin.crs)


# ─────────────────────────────────────────────────────
# ② OpenStreetMap
# ─────────────────────────────────────────────────────
# geom: 取得後に残す形（line / polygon / point）。point は面・線を代表点に変換する。
OSM_LAYERS: Dict[str, dict] = {
    "roads":      {"kind": "graph", "network_type": "drive", "desc": "自動車が通れる道路（高速・幹線・生活道路）"},
    "roads_all":  {"kind": "graph", "network_type": "all", "desc": "歩行者道・自転車道を含む全道路（件数が多い）"},
    "rail":       {"kind": "features", "tags": {"railway": ["rail", "subway", "light_rail", "tram", "monorail"]},
                   "geom": "line", "desc": "鉄道・地下鉄・モノレール・路面電車"},
    "stations":   {"kind": "features", "tags": {"railway": ["station"]}, "geom": "point", "desc": "鉄道駅"},
    "water":      {"kind": "features", "tags": {"natural": ["water"], "waterway": ["riverbank"]},
                   "geom": "polygon", "desc": "池・湖・川の水面"},
    "waterways":  {"kind": "features", "tags": {"waterway": ["river", "canal", "stream"]},
                   "geom": "line", "desc": "河川・水路（線）"},
    "parks":      {"kind": "features", "tags": {"leisure": ["park", "garden", "playground", "pitch"]},
                   "geom": "polygon", "desc": "公園・緑地"},
    "buildings":  {"kind": "features", "tags": {"building": True}, "geom": "polygon",
                   "desc": "建物の形（件数が非常に多い。区ごとに分けて取得する）"},
    "schools":    {"kind": "features", "tags": {"amenity": ["school"]}, "geom": "point", "desc": "学校"},
    "childcare":  {"kind": "features", "tags": {"amenity": ["kindergarten", "childcare"]}, "geom": "point",
                   "desc": "幼稚園・保育施設（OSMでは kindergarten が保育所を含むことがある。網羅性は要確認）"},
    "hospitals":  {"kind": "features", "tags": {"amenity": ["hospital", "clinic"]}, "geom": "point", "desc": "病院・診療所"},
    "supermarkets": {"kind": "features", "tags": {"shop": ["supermarket"]}, "geom": "point", "desc": "スーパー"},
}
_KEEP_COLS = ["osmid", "name", "highway", "railway", "amenity", "leisure", "building", "natural", "waterway",
              "shop", "operator", "ref", "oneway", "bridge", "tunnel", "lanes"]


def _osm_features(poly, tags: dict) -> gpd.GeoDataFrame:
    """OSMnx で地物を取得する（テストで差し替え可能にするため分離）。"""
    import osmnx as ox
    try:
        return ox.features_from_polygon(poly, tags)
    except Exception as e:                                  # 該当なし（InsufficientResponseError）は空で返す
        if "InsufficientResponse" in type(e).__name__ or "No matching features" in str(e):
            return gpd.GeoDataFrame(geometry=[], crs=WGS84)
        raise


def _osm_graph_edges(poly, network_type: str) -> gpd.GeoDataFrame:
    """OSMnx で道路ネットワークの辺（線）を取得する（テストで差し替え可能）。"""
    import osmnx as ox
    try:
        G = ox.graph_from_polygon(poly, network_type=network_type, simplify=True, retain_all=True)
    except Exception as e:
        if "InsufficientResponse" in type(e).__name__ or "empty" in str(e).lower():
            return gpd.GeoDataFrame(geometry=[], crs=WGS84)
        raise
    return ox.graph_to_gdfs(G, nodes=False).reset_index()


def _stringify(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """list などの値を文字列にする（GeoPackage に保存できない型を避ける）。"""
    gdf = gdf.copy()
    for c in gdf.columns:
        if c != "geometry" and gdf[c].dtype == object:
            gdf[c] = gdf[c].map(lambda v: ";".join(map(str, v)) if isinstance(v, (list, tuple, set)) else v)
    return gdf


def _shape(gdf: gpd.GeoDataFrame, geom: str) -> gpd.GeoDataFrame:
    """レイヤーの目的の形だけに揃える（line / polygon / point）。"""
    if gdf.empty:
        return gdf
    gt = gdf.geometry.geom_type
    if geom == "polygon":
        return gdf[gt.isin(["Polygon", "MultiPolygon"])]
    if geom == "line":
        return gdf[gt.isin(["LineString", "MultiLineString"])]
    if geom == "point":
        out = gdf.copy()
        non_point = ~gt.isin(["Point"])
        if non_point.any():
            out.loc[non_point, "geometry"] = out.loc[non_point].geometry.representative_point()
        return out[out.geometry.geom_type == "Point"]
    return gdf


def fetch_osm_layers(admin: gpd.GeoDataFrame, layers: Sequence[str],
                     cache_dir: str = "data/osm", chunk: bool = True, refresh: bool = False,
                     simplify_deg: float = 0.0003, pause_s: float = 2.0, retries: int = 2,
                     user_agent: str = "urban-basemap-gis (research use)") -> Dict[str, gpd.GeoDataFrame]:
    """行政区域の範囲内の OSM データを取得し、GeoPackage にキャッシュする。

    admin     : 行政区域（read_n03 → select_area → dissolve_admin の結果）
    layers    : OSM_LAYERS のキー。例 ["roads", "rail", "stations", "water", "parks"]
    chunk     : True なら行政区域（区）ごとに分けて問い合わせる（大きな市での失敗を防ぐ）
    refresh   : False なら、キャッシュがあれば再取得しない（公開サーバーへの負荷を減らす）
    simplify_deg : 問い合わせ用に境界を単純化する度数（0.0003度≒30m）。取得後に元の境界で切り抜く。
                  境界の頂点が多いと問い合わせが長すぎて失敗するため。

    Overpass 公開サーバーの利用方針（OSM Wiki より）：1日1万クエリ・1GB・処理10分未満の範囲で一回限りの利用、
    並列実行はしない、429/406 が返ったら30秒待つ、結果をキャッシュする。商用利用は自前サーバーか有償サーバーを使う。
    ⚠️ このスキルは「一回取得してファイルに保存し、以降はそのファイルを使う」前提で作っている。
    """
    import osmnx as ox
    ox.settings.use_cache = True
    ox.settings.cache_folder = os.path.join(cache_dir, "_osmnx_cache")
    ox.settings.requests_timeout = 180
    for attr in ("http_user_agent", "default_user_agent"):      # Overpass は User-Agent での自己申告を求めている
        if hasattr(ox.settings, attr):
            setattr(ox.settings, attr, user_agent)
    os.makedirs(cache_dir, exist_ok=True)

    adm = admin.to_crs(WGS84)
    boundary = adm.geometry.union_all() if hasattr(adm.geometry, "union_all") else adm.unary_union
    parts = [(row.get("表示名") or row.get("市区町村") or str(i), row.geometry) for i, row in adm.iterrows()] \
        if chunk else [("all", boundary)]

    out: Dict[str, gpd.GeoDataFrame] = {}
    for layer in layers:
        if layer not in OSM_LAYERS:
            raise KeyError(f"未定義のレイヤー：{layer}。使えるもの：{list(OSM_LAYERS)}")
        spec = OSM_LAYERS[layer]
        path = os.path.join(cache_dir, f"{layer}.gpkg")
        if os.path.exists(path) and not refresh:
            out[layer] = gpd.read_file(path)
            print(f"[{layer}] キャッシュから読み込み：{len(out[layer])}件")
            continue

        frames = []
        for pname, geom in parts:
            q = geom.simplify(simplify_deg, preserve_topology=True) if simplify_deg else geom
            for attempt in range(retries + 1):
                try:
                    if spec["kind"] == "graph":
                        g = _osm_graph_edges(q, spec["network_type"])
                    else:
                        g = _osm_features(q, spec["tags"])
                    break
                except Exception as e:
                    if attempt == retries:
                        raise RuntimeError(f"[{layer}/{pname}] 取得に失敗：{e}") from e
                    print(f"  [{layer}/{pname}] 失敗（{e}）。30秒待って再試行します…")
                    time.sleep(30)
            if len(g):
                g = g.reset_index() if "geometry" in g.columns and isinstance(g.index, pd.MultiIndex) else g
                frames.append(g)
            print(f"  [{layer}/{pname}] {len(g)}件")
            time.sleep(pause_s)

        if frames:
            allg = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), geometry="geometry", crs=WGS84)
            if "osmid" not in allg.columns:                      # 点・線・面でIDが重なるため種別を付ける
                if "id" in allg.columns:
                    elem = allg["element"].astype(str).str[0] if "element" in allg.columns else ""
                    allg["osmid"] = elem + allg["id"].astype(str)
                else:
                    allg["osmid"] = np.arange(len(allg))
            allg = allg.drop_duplicates(subset=["osmid"], keep="first") if spec["kind"] == "features" else allg
            allg = _shape(allg, spec.get("geom", "line"))
            allg = gpd.clip(allg, boundary)                           # 元の境界で切り抜く
            cols = [c for c in _KEEP_COLS if c in allg.columns] + ["geometry"]
            allg = _stringify(allg[cols]).reset_index(drop=True)
        else:
            allg = gpd.GeoDataFrame({"osmid": []}, geometry=[], crs=WGS84)
        if len(allg):
            allg.to_file(path, driver="GPKG")
        out[layer] = allg
        print(f"[{layer}] 取得完了：{len(allg)}件 → {path}")
    return out


# ─────────────────────────────────────────────────────
# ③ 描画
# ─────────────────────────────────────────────────────
_ROAD_STYLE = {            # (線幅, 色, 重なり順)
    "motorway": (1.9, "#E58F3A", 4), "trunk": (1.6, "#E58F3A", 4), "primary": (1.3, "#F0B95F", 3),
    "secondary": (1.0, "#F5D58F", 3), "tertiary": (0.7, "#FFFFFF", 2), "residential": (0.4, "#FFFFFF", 2),
}
_ROAD_DEFAULT = (0.3, "#FFFFFF", 2)


def _road_class(v) -> str:
    v = str(v).split(";")[0]
    return v.replace("_link", "")


def _to_plane(gdf, crs):
    return gdf.to_crs(crs) if len(gdf) else gdf


def add_scalebar(ax, length_m: Optional[float] = None, loc: str = "lower right"):
    """投影座標系（m）の軸に縮尺バーと北矢印を描く。"""
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    width = x1 - x0
    if length_m is None:
        raw = width / 5
        mag = 10 ** np.floor(np.log10(raw))
        length_m = float(min([1, 2, 5, 10], key=lambda m: abs(m * mag - raw)) * mag)
    right = "right" in loc
    xs = x1 - width * 0.04 - length_m if right else x0 + width * 0.04
    ys = y0 + (y1 - y0) * 0.04
    ax.plot([xs, xs + length_m], [ys, ys], color="#222", linewidth=3, solid_capstyle="butt", zorder=20)
    label = f"{length_m / 1000:g} km" if length_m >= 1000 else f"{length_m:g} m"
    ax.text(xs + length_m / 2, ys + (y1 - y0) * 0.012, label, ha="center", va="bottom", fontsize=9, zorder=20)
    nx, ny = (x1 - width * 0.06, y1 - (y1 - y0) * 0.16)
    ax.annotate("N", xy=(nx, ny + (y1 - y0) * 0.1), xytext=(nx, ny), ha="center", fontsize=11, fontweight="bold",
                arrowprops=dict(arrowstyle="-|>", color="#222"), zorder=20)


def _draw_osm(ax, osm: Dict[str, gpd.GeoDataFrame], crs, road_alpha: float = 1.0, muted: bool = False):
    for name, color in (("water", "#BCD9EE"), ("parks", "#CDE6C1")):
        g = osm.get(name)
        if g is not None and len(g):
            _to_plane(g, crs).plot(ax=ax, color=color, linewidth=0, alpha=0.6 if muted else 1, zorder=1.5)
    ww = osm.get("waterways")
    if ww is not None and len(ww):
        _to_plane(ww, crs).plot(ax=ax, color="#A9CBE6", linewidth=0.8, zorder=1.6)
    bd = osm.get("buildings")
    if bd is not None and len(bd):
        _to_plane(bd, crs).plot(ax=ax, color="#E3DED6", linewidth=0, zorder=1.7)
    for rname in ("roads_all", "roads"):
        roads = osm.get(rname)
        if roads is not None and len(roads):
            r = _to_plane(roads, crs)
            cls = r["highway"].map(_road_class) if "highway" in r.columns else pd.Series("", index=r.index)
            for c, grp in r.groupby(cls):
                lw, col, z = _ROAD_STYLE.get(c, _ROAD_DEFAULT)
                grp.plot(ax=ax, color="#BDBDBD" if muted and col == "#FFFFFF" else col,
                         linewidth=lw, alpha=road_alpha, zorder=z)
            break
    rail = osm.get("rail")
    if rail is not None and len(rail):
        r = _to_plane(rail, crs)
        r.plot(ax=ax, color="#555555", linewidth=1.1, zorder=5)
        r.plot(ax=ax, color="white", linewidth=0.5, linestyle=(0, (3, 3)), zorder=5.1)
    st = osm.get("stations")
    if st is not None and len(st):
        _to_plane(st, crs).plot(ax=ax, color="white", edgecolor="#222", markersize=22, linewidth=1.2, zorder=6)


def _finish_axes(ax, admin_plane, title: Optional[str], label_col: Optional[str], attribution: bool):
    admin_plane.boundary.plot(ax=ax, color="#3A3A3A", linewidth=1.1, zorder=8)
    minx, miny, maxx, maxy = admin_plane.total_bounds
    padx, pady = (maxx - minx) * 0.03, (maxy - miny) * 0.03
    ax.set_xlim(minx - padx, maxx + padx); ax.set_ylim(miny - pady, maxy + pady)
    ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlabel(""); ax.set_ylabel("")                      # 投影座標の軸ラベル（Easting/Northing）は不要
    for s in ax.spines.values():
        s.set_visible(False)
    if label_col and label_col in admin_plane.columns:
        for _, r in admin_plane.iterrows():
            p = r.geometry.representative_point()
            ax.annotate(str(r[label_col]), (p.x, p.y), ha="center", fontsize=9, color="#111", zorder=12,
                        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.65))
    if title:
        ax.set_title(title, fontsize=15, fontweight="bold", loc="left")
    add_scalebar(ax)
    if attribution:
        ax.text(0.0, -0.015, ATTRIBUTION, transform=ax.transAxes, fontsize=7, color="#555", va="top")


def draw_basemap(admin: gpd.GeoDataFrame, osm: Optional[Dict[str, gpd.GeoDataFrame]] = None,
                 ax=None, title: Optional[str] = None, label_col: Optional[str] = "表示名",
                 crs=None, figsize=(9, 9), attribution: bool = True,
                 save_path: Optional[str] = None, dpi: int = 200):
    """行政区域＋OSM のベースマップを描く。戻り値は Figure。"""
    crs = crs or pick_local_crs(admin)
    adm = admin.to_crs(crs)
    fig, ax = (plt.subplots(figsize=figsize) if ax is None else (ax.figure, ax))
    ax.set_facecolor("#F4F1EA")
    adm.plot(ax=ax, color="#F4F1EA", linewidth=0, zorder=0)
    if osm:
        _draw_osm(ax, osm, crs)
    _finish_axes(ax, adm, title, label_col, attribution)
    if save_path:
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight")
        print(f"保存：{save_path}")
    return fig


def classify(values: pd.Series, scheme: str = "quantile", k: int = 5,
             bins: Optional[Sequence[float]] = None) -> np.ndarray:
    """値を階級に分ける。戻り値は境界値の配列（長さ k+1）。

    quantile：各階級の件数が同じ（既定）／ equal：値の幅が同じ／ bins：自分で指定。
    ⚠️ 区の数が少ない（7区など）ときは k=3〜4 にする。階級の切り方で印象が変わるため、凡例の数値を必ず示す。
    """
    v = values.dropna().to_numpy(dtype=float)
    if bins is not None:
        return np.asarray(bins, dtype=float)
    if scheme == "equal":
        return np.linspace(v.min(), v.max(), k + 1)
    edges = np.unique(np.quantile(v, np.linspace(0, 1, k + 1)))
    return edges if len(edges) > 2 else np.linspace(v.min(), v.max(), k + 1)


def plot_choropleth(admin: gpd.GeoDataFrame, value_col: str,
                    osm: Optional[Dict[str, gpd.GeoDataFrame]] = None, ax=None,
                    title: Optional[str] = None, legend_title: Optional[str] = None,
                    cmap: str = "YlOrRd", scheme: str = "quantile", k: int = 5,
                    bins: Optional[Sequence[float]] = None, fmt: str = "{:,.1f}",
                    show_values: bool = True, label_col: Optional[str] = "表示名",
                    crs=None, figsize=(9, 9), save_path: Optional[str] = None, dpi: int = 200):
    """行政区域を値で塗り分け、OSM を薄く重ねる（コロプレス図）。欠損は灰色で示す。"""
    crs = crs or pick_local_crs(admin)
    adm = admin.to_crs(crs).copy()
    fig, ax = (plt.subplots(figsize=figsize) if ax is None else (ax.figure, ax))
    edges = classify(adm[value_col], scheme, k, bins)
    n_cls = len(edges) - 1
    adm["_cls"] = pd.cut(adm[value_col], bins=edges, labels=False, include_lowest=True)
    colors = plt.get_cmap(cmap)(np.linspace(0.2, 0.95, n_cls))
    adm["_color"] = adm["_cls"].map(lambda c: colors[int(c)] if pd.notna(c) else (0.87, 0.87, 0.87, 1))
    adm.plot(ax=ax, color=list(adm["_color"]), linewidth=0, zorder=1)
    if osm:
        _draw_osm(ax, osm, crs, road_alpha=0.55, muted=True)
    _finish_axes(ax, adm, title, None, attribution=True)

    if label_col and label_col in adm.columns:
        for _, r in adm.iterrows():
            p = r.geometry.representative_point()
            txt = str(r[label_col])
            if show_values and pd.notna(r[value_col]):
                txt += "\n" + fmt.format(r[value_col])
            ax.annotate(txt, (p.x, p.y), ha="center", fontsize=9, color="#111", zorder=12,
                        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.7))
    # 階級の範囲を「以上・超・以下」で明記する（境界値がどちらの階級に入るか読み取れるように）
    handles = [Patch(fc=colors[i], ec="none",
                     label=(f"{fmt.format(edges[i])}以上〜{fmt.format(edges[i + 1])}以下" if i == 0
                            else f"{fmt.format(edges[i])}超〜{fmt.format(edges[i + 1])}以下"))
               for i in range(n_cls)]
    if adm[value_col].isna().any():
        handles.append(Patch(fc=(0.87, 0.87, 0.87), ec="none", label="データなし"))
    ax.legend(handles=handles, title=legend_title or value_col, loc="upper left", fontsize=8,
              title_fontsize=9, frameon=True, framealpha=0.9)
    if save_path:
        os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
        fig.savefig(save_path, dpi=dpi, bbox_inches="tight")
        print(f"保存：{save_path}")
    return fig


def plot_points(ax, points: gpd.GeoDataFrame, crs, color: str = "#D62728", size: float = 18,
                label: Optional[str] = None, edgecolor: str = "white"):
    """ベースマップの上に点（施設など）を重ねる。plot_choropleth / draw_basemap が返した Figure の軸に使う。"""
    if len(points):
        _to_plane(points, crs).plot(ax=ax, color=color, markersize=size, edgecolor=edgecolor,
                                    linewidth=0.6, zorder=10, label=label)
    return ax


# ─────────────────────────────────────────────────────
# ④ 書き出し（QGIS・Tableau 用）
# ─────────────────────────────────────────────────────
def export_layers(layers: Dict[str, gpd.GeoDataFrame], out_dir: str, basename: str = "basemap") -> Dict[str, str]:
    """レイヤーをまとめて保存する。

    - {basename}.gpkg           : 全レイヤーを1ファイルに（QGISで「レイヤ」→「レイヤを追加」で読める）
    - {basename}_admin.geojson  : 行政区域（"admin" レイヤーがある場合）。Tableau はこの形式を使う
    - {basename}_admin.csv      : 行政区域の属性＋中心点の緯度・経度（Tableau・Excel 用）
    座標系は GPKG・GeoJSON とも WGS84（EPSG:4326）にそろえる。
    """
    os.makedirs(out_dir, exist_ok=True)
    gpkg = os.path.join(out_dir, f"{basename}.gpkg")
    if os.path.exists(gpkg):
        os.remove(gpkg)
    written: Dict[str, str] = {}
    for name, g in layers.items():
        if g is None or not len(g):
            continue
        _stringify(g.to_crs(WGS84)).to_file(gpkg, layer=name, driver="GPKG")
    written["gpkg"] = gpkg
    admin = layers.get("admin")
    if admin is not None and len(admin):
        a = admin.to_crs(WGS84)
        gj = os.path.join(out_dir, f"{basename}_admin.geojson")
        a.to_file(gj, driver="GeoJSON")
        pts = a.to_crs(pick_local_crs(a)).geometry.representative_point().to_crs(WGS84)
        csv = os.path.join(out_dir, f"{basename}_admin.csv")
        a.drop(columns="geometry").assign(経度=pts.x.values, 緯度=pts.y.values).to_csv(
            csv, index=False, encoding="utf-8-sig")
        written.update({"geojson": gj, "csv": csv})
    for k, v in written.items():
        print(f"保存[{k}]：{v}")
    return written


def join_stats(admin: gpd.GeoDataFrame, stats: pd.DataFrame, stats_code_col: str,
               how: str = "left") -> gpd.GeoDataFrame:
    """統計表（e-Stat 等）を行政区域に結合する。結合キーは5桁の自治体コード。

    結合後に「地図に塗れない（結合できなかった）行政区域」と「結合できなかった統計行」を表示する。
    """
    s = stats.copy()
    s["市区町村コード"] = s[stats_code_col].map(to_jis5)
    merged = admin.merge(s.drop(columns=[stats_code_col], errors="ignore"), on="市区町村コード", how=how)
    unmatched_admin = sorted(set(admin["市区町村コード"]) - set(s["市区町村コード"]))
    unmatched_stats = sorted(set(s["市区町村コード"].dropna()) - set(admin["市区町村コード"]))
    if unmatched_admin:
        print(f"⚠️ 統計が結合できなかった行政区域：{unmatched_admin}")
    if unmatched_stats:
        print(f"（参考）地図に対応する区域がない統計行：{unmatched_stats[:10]}{' …' if len(unmatched_stats) > 10 else ''}")
    return gpd.GeoDataFrame(merged, geometry="geometry", crs=admin.crs)
