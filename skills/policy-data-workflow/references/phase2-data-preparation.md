# PHASE 2：データ準備（STEP 04〜08）の手順とコード

`SKILL.md` の PHASE 2 から読む。コードは Anaconda（JupyterLab）と Google Colab の両方で動く形。APIの仕様・URL・統計表IDは変わるため、実行前に公式の案内で確認する。

### ▶ STEP 04：データ検索

**目的**：RQに答えるために必要なデータを、国内外の幅広いソースから特定・リストアップする。

#### データソース全体マップ（5カテゴリ）

**【カテゴリ1】政府・行政統計ポータル**

| ソース名 | URL | 特徴 | API |
|---|---|---|---|
| e-Stat（政府統計総合窓口） | https://www.e-stat.go.jp | 国勢調査・経済センサス等 全省庁統計 | ✅ |
| DATA.GO.JP（政府オープンデータ） | https://www.data.go.jp | 各省庁の全オープンデータ横断検索 | ✅ |
| RESAS（地域経済分析システム） | https://resas.go.jp | 人口・産業・観光・農業の地域別データ | ✅ |
| V-RESAS（コロナ影響可視化） | https://v-resas.go.jp | 消費・人流・雇用のコロナ影響 | ✅ |
| J-STAT MAP | https://jstatmap.e-stat.go.jp | 統計GIS・地図上で統計を可視化 | ✅ |
| 内閣府 SBIR統計 | https://www8.cao.go.jp/survey | 国民生活・消費実態調査 | ❌ |

**【カテゴリ2】国土・都市・インフラ系**

| ソース名 | URL | 主なデータ | API |
|---|---|---|---|
| 国土数値情報（MLIT） | https://nlftp.mlit.go.jp/ksj | 用途地域・施設・河川・GISデータ | ✅ |
| 不動産情報ライブラリ（国交省） | https://www.reinfolib.mlit.go.jp | 不動産取引価格・地価公示・都市計画 | ✅ |
| 都市計画基礎調査（国交省） | https://www.mlit.go.jp/toshi/tosiko | 土地利用・建物用途・人口集中地区 | ❌ |
| 道路統計年報（国交省） | https://www.mlit.go.jp/road | 道路延長・交通量・事故データ | ❌ |
| 国土地理院 地理院タイル | https://maps.gsi.go.jp/development | 標高・地形・空中写真 | ✅ |
| G空間情報センター | https://www.geospatial.jp | GISデータ横断ポータル | ✅ |
| 建築着工統計（国交省） | e-Stat経由 | 着工棟数・床面積・用途別 | ✅ |

**【カテゴリ3】自治体オープンデータ**

| ソース名 | URL | 主なデータ |
|---|---|---|
| 川崎市オープンデータ | https://www.city.kawasaki.jp/opendata | 人口・財政・施設・福祉 |
| 川崎市統計書 | https://www.city.kawasaki.jp/shisei/category/51-4-0-0-0-0-0-0-0-0.html | 年度版 詳細統計 |
| 横浜市オープンデータ | https://data.city.yokohama.lg.jp | 人口・交通・環境 |
| 東京都オープンデータカタログ | https://catalog.data.metro.tokyo.lg.jp | 都政全般の統計 |
| 神奈川県オープンデータ | https://www.pref.kanagawa.jp/osirase/opendata | 県内市町村横断データ |
| 全国自治体オープンデータ一覧 | https://www.data.go.jp/data/dataset?groups=local | DATA.GO.JP 地方公共団体分 |

**【カテゴリ4】環境・気候・衛星データ**

| ソース名 | URL | 主なデータ | API |
|---|---|---|---|
| Google Earth Engine | https://earthengine.google.com | Sentinel-2・Landsat・MODIS 衛星画像 | ✅ |
| 気象庁（AMeDAS） | https://www.data.jma.go.jp | 気温・降水・風速・日照 | ✅ |
| 環境省 GIS データ | https://www.geospatial.jp/ckan/organization/env | 生態系・大気・騒音・水質 | ✅ |
| NASA Earthdata | https://earthdata.nasa.gov | 全球気候・土地被覆 | ✅ |
| Copernicus（欧州宇宙機関） | https://scihub.copernicus.eu | Sentinel 全シリーズ | ✅ |
| JAXA EORC | https://www.eorc.jaxa.jp | 国産衛星データ（ALOS等） | ✅ |

**【カテゴリ5】社会・経済・国際比較**

| ソース名 | URL | 主なデータ | API |
|---|---|---|---|
| 国立社会保障・人口問題研究所（IPSS） | https://www.ipss.go.jp | 将来人口推計・世帯推計 | ❌ |
| 総務省 地方財政状況調査 | https://www.soumu.go.jp/iken/zaisei.html | 自治体財政指標・財政力指数 | ❌ |
| 厚労省 賃金・雇用統計 | https://www.mhlw.go.jp/toukei | 賃金・雇用・医療・介護 | ✅ |
| 農林水産省 農業センサス | https://www.e-stat.go.jp | 農地・農業就業 | ✅ |
| OECD Data | https://data.oecd.org | 国際比較統計 | ✅ |
| World Bank Open Data | https://data.worldbank.org | 世界各国の開発指標 | ✅ |
| UN Data | https://data.un.org | 国連統計 | ✅ |
| IMF Data | https://www.imf.org/en/Data | 国際金融・経済指標 | ✅ |
| OpenStreetMap（Overpass API） | https://overpass-turbo.eu | 施設・道路・POI（地理情報） | ✅ |

詳細なURL・取得コードは `references/data-sources.md` を参照。

---

#### データ検索の優先順位フロー：

```
① まず DATA.GO.JP または RESAS で横断検索
      ↓ 該当データが見つかれば → ダウンロード or API
② e-Stat で詳細統計データを検索
      ↓ 地域別・時系列の精細データ
③ 自治体オープンデータポータルで補完
      ↓ 川崎市・横浜市・神奈川県など
④ 国土数値情報・不動産情報ライブラリでGIS/空間データを取得
⑤ 衛星データ（GEE）で環境・土地被覆データを補完
⑥ 国際比較が必要なら OECD/World Bank
```

---

#### 各ソースへのアクセスコード：

```python
import requests
import pandas as pd
import os

# ─────────────────────────────────────────────────────
# A. e-Stat API（政府統計全般）
# ─────────────────────────────────────────────────────
ESTAT_APP_ID = "YOUR_APP_ID"  # https://www.e-stat.go.jp で登録

def search_estat(keyword: str, limit: int = 20) -> list:
    """e-Stat でデータセットをキーワード検索する"""
    url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsList"
    params = {"appId": ESTAT_APP_ID, "searchWord": keyword, "limit": limit}
    res = requests.get(url, params=params)
    res.raise_for_status()
    tables = res.json()["GET_STATS_LIST"]["DATALIST_INF"]["TABLE_INF"]
    for t in tables:
        print(f"ID: {t['@id']} | {t['STAT_NAME']['$']} | {t['TITLE']['$']}")
    return tables

# ─────────────────────────────────────────────────────
# B. RESAS API（地域経済分析システム）
# ─────────────────────────────────────────────────────
RESAS_API_KEY = "YOUR_RESAS_KEY"  # https://opendata.resas-portal.go.jp で登録

def get_resas_population(pref_code: int = 14, city_code: str = "14130") -> pd.DataFrame:
    """RESAS から人口構成データを取得する（神奈川県=14, 川崎市=14130）"""
    url = "https://opendata.resas-portal.go.jp/api/v1/population/composition/perYear"
    headers = {"X-API-KEY": RESAS_API_KEY}
    params = {"prefCode": pref_code, "cityCode": city_code}
    res = requests.get(url, headers=headers, params=params)
    res.raise_for_status()
    data = res.json()["result"]["data"]
    # data は [{"label":"総人口","data":[{"year":...,"value":...}]}, ...]
    dfs = []
    for category in data:
        df = pd.DataFrame(category["data"])
        df["区分"] = category["label"]
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)

# ─────────────────────────────────────────────────────
# C. DATA.GO.JP（政府オープンデータ横断検索）
# ─────────────────────────────────────────────────────
def search_datagov(keyword: str, rows: int = 20) -> pd.DataFrame:
    """DATA.GO.JP の CKAN API でデータセットを検索する"""
    url = "https://www.data.go.jp/api/3/action/package_search"
    params = {"q": keyword, "rows": rows}
    res = requests.get(url, params=params)
    res.raise_for_status()
    results = res.json()["result"]["results"]
    rows_data = [{"title": r["title"], "url": r.get("url", ""), "notes": r.get("notes", "")[:80]}
                 for r in results]
    df = pd.DataFrame(rows_data)
    print(df.to_string(index=False))
    return df

# ─────────────────────────────────────────────────────
# D. 不動産情報ライブラリ API（国交省）
# ─────────────────────────────────────────────────────
def get_land_price(pref_code: int = 14, year: int = 2024) -> pd.DataFrame:
    """国交省の不動産取引価格情報を取得する"""
    url = "https://www.reinfolib.mlit.go.jp/ex-api/external/XIT001"
    headers = {"Ocp-Apim-Subscription-Key": "YOUR_REINFOLIB_KEY"}  # 要登録
    params = {"year": year, "area": str(pref_code).zfill(2)}
    res = requests.get(url, headers=headers, params=params)
    res.raise_for_status()
    return pd.DataFrame(res.json().get("data", []))

# ─────────────────────────────────────────────────────
# E. OpenStreetMap Overpass API（施設・POI）
# ─────────────────────────────────────────────────────
def get_osm_facilities(lat: float, lon: float,
                       radius_m: int = 2000,
                       amenity: str = "school") -> pd.DataFrame:
    """
    OpenStreetMap から施設（学校・保育所・病院等）を取得する
    amenity 例: school / kindergarten / hospital / park / supermarket
    """
    query = f"""
    [out:json];
    node["amenity"="{amenity}"](around:{radius_m},{lat},{lon});
    out body;
    """
    res = requests.post("https://overpass-api.de/api/interpreter", data=query)
    res.raise_for_status()
    elements = res.json().get("elements", [])
    rows = [{"name":  e.get("tags", {}).get("name", ""),
             "lat":   e["lat"],
             "lon":   e["lon"],
             "amenity": amenity}
            for e in elements]
    df = pd.DataFrame(rows)
    print(f"{amenity}：{len(df)}件取得（半径{radius_m}m）")
    return df

# ─────────────────────────────────────────────────────
# F. 国土地理院 標高API
# ─────────────────────────────────────────────────────
def get_elevation(lat: float, lon: float) -> float:
    """国土地理院 APIから指定座標の標高（m）を取得する"""
    url = "https://cyberjapandata2.gsi.go.jp/general/dem/scripts/getelevation.php"
    params = {"lon": lon, "lat": lat, "outtype": "JSON"}
    res = requests.get(url, params=params)
    return res.json().get("elevation", None)

# ─────────────────────────────────────────────────────
# G. OECD Data API（国際比較）
# ─────────────────────────────────────────────────────
def get_oecd_data(dataset: str = "HH_DASH", subject: str = "INEQ") -> pd.DataFrame:
    """
    OECD SDMX-JSON API からデータを取得する
    dataset 例: HH_DASH（家計）/ REGION_DEMOGR（地域人口）
    """
    url = f"https://stats.oecd.org/SDMX-JSON/data/{dataset}/{subject}/all"
    params = {"contentType": "csv", "detail": "code"}
    res = requests.get(url, params=params)
    from io import StringIO
    return pd.read_csv(StringIO(res.text))

# ─────────────────────────────────────────────────────
# 利用例
# ─────────────────────────────────────────────────────
# e-Stat 検索
tables = search_estat("人口 川崎市")

# RESAS 人口
# df_pop = get_resas_population(pref_code=14, city_code="14130")

# DATA.GO.JP 検索
# df_gov = search_datagov("川崎市 子育て")

# OSM 保育所取得（川崎市役所付近）
# df_nursery = get_osm_facilities(lat=35.5308, lon=139.7028, amenity="kindergarten")
```

---

### ▶ STEP 05：データダウンロード

**目的**：特定したデータを実際に取得してローカルに保存する。

```python
import requests
import pandas as pd
import os

APP_ID = "YOUR_APP_ID"

def download_estat(stats_data_id: str,
                   area_code: str = None,
                   save_path: str = None) -> pd.DataFrame:
    """
    e-Stat API からデータを取得しDataFrameに変換する。

    Parameters
    ----------
    stats_data_id : str   e-StatのデータセットID（STEP04で確認）
    area_code     : str   地域コード（川崎市="14130", 神奈川県="14"）
    save_path     : str   CSVの保存先パス（例: "data/raw/population.csv"）
    """
    url = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"
    params = {
        "appId": APP_ID,
        "statsDataId": stats_data_id,
        "metaGetFlg": "Y",
        "cntGetFlg": "N",
        "limit": 100000,
    }
    if area_code:
        params["cdArea"] = area_code

    res = requests.get(url, params=params)
    res.raise_for_status()
    stat_data = res.json()["GET_STATS_DATA"]["STATISTICAL_DATA"]

    # 値データをDataFrameに変換
    df = pd.DataFrame(stat_data["DATA_INF"]["VALUE"])

    # コード→名称変換（メタデータを付与）
    cls_list = stat_data["CLASS_INF"]["CLASS_OBJ"]
    if isinstance(cls_list, dict):
        cls_list = [cls_list]
    for cls in cls_list:
        col = "@" + cls["@id"]
        if col in df.columns:
            classes = cls["CLASS"]
            if isinstance(classes, dict):
                classes = [classes]
            mapping = {c["@code"]: c["@name"] for c in classes}
            df[cls["@name"]] = df[col].map(mapping)

    df["value"] = pd.to_numeric(df["$"], errors="coerce")

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        df.to_csv(save_path, index=False, encoding="utf-8-sig")
        print(f"保存完了：{save_path}（{len(df)}行）")

    print(f"取得完了：{len(df)}行 × {len(df.columns)}列")
    return df

# 利用例（国勢調査 川崎市）
df_raw = download_estat(
    stats_data_id="0000010101",
    area_code="14130",
    save_path="data/raw/population_kawasaki.csv"
)
```

---

### ▶ STEP 06：データクレンジング

**目的**：分析に使えるクリーンなデータに整える。

```python
import pandas as pd
import numpy as np

def cleanse_pipeline(df: pd.DataFrame,
                     value_col: str = "value",
                     year_col: str = "年",
                     missing_threshold: float = 0.05) -> pd.DataFrame:
    """
    標準クレンジングパイプライン
    ① 重複削除  ② 欠損値処理  ③ 型変換  ④ 外れ値記録  ⑤ 文字列正規化
    """
    df = df.copy()
    report = {}

    # ① 重複削除
    before = len(df)
    df = df.drop_duplicates()
    report["重複削除"] = before - len(df)

    # ② 欠損値の確認と処理
    missing_rate = df[value_col].isna().mean()
    report["欠損率"] = f"{missing_rate:.1%}"
    if missing_rate < missing_threshold:
        df[value_col] = df[value_col].interpolate(method="linear")
        report["欠損処理"] = "線形補間"
    else:
        print(f"⚠️ 欠損率が{missing_rate:.1%}と高いです。補間方法を確認してください。")
        report["欠損処理"] = "未処理（要確認）"

    # ③ 型変換
    if year_col in df.columns:
        df[year_col] = pd.to_numeric(df[year_col], errors="coerce").astype("Int64")
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")

    # ④ 外れ値の記録（IQR法、削除はしない）
    Q1, Q3 = df[value_col].quantile([0.25, 0.75])
    IQR = Q3 - Q1
    outlier_mask = (df[value_col] < Q1 - 1.5 * IQR) | (df[value_col] > Q3 + 1.5 * IQR)
    df["is_outlier"] = outlier_mask
    report["外れ値候補"] = outlier_mask.sum()

    # ⑤ 文字列の正規化（全角→半角、前後スペース除去）
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip().str.normalize("NFKC")

    print("【クレンジングレポート】")
    for k, v in report.items():
        print(f"  {k}：{v}")
    print(f"  最終行数：{len(df)}")
    return df

df_clean = cleanse_pipeline(df_raw)
df_clean.to_csv("data/processed/clean.csv", index=False, encoding="utf-8-sig")
```

---

### ▶ STEP 07：データ統合

**目的**：複数データソースを結合して分析用マスターデータを作る。

```python
import pandas as pd

def merge_datasets(datasets: dict,
                   join_key: str,
                   how: str = "outer") -> pd.DataFrame:
    """
    複数DataFrameをキー列で結合する。

    Parameters
    ----------
    datasets : {"人口": df_pop, "地価": df_land}  # 結合するDF群と名前
    join_key : "市区町村コード"                    # 結合キー列名
    how      : "outer" / "inner" / "left"
    """
    result = None
    for name, df in datasets.items():
        # 列名にプレフィックスを付けて衝突を防ぐ（キー列は除く）
        rename_map = {c: f"{name}_{c}" for c in df.columns if c != join_key}
        df = df.rename(columns=rename_map)
        if result is None:
            result = df
        else:
            result = pd.merge(result, df, on=join_key, how=how)
        print(f"[{name}] 結合後：{len(result)}行 × {len(result.columns)}列")

    # 結合後の欠損率レポート
    missing_report = (result.isna().sum() / len(result) * 100).round(1)
    print("\n【結合後 欠損率（%）】")
    print(missing_report[missing_report > 0].to_string())
    return result

df_master = merge_datasets(
    datasets={
        "人口":     df_pop,
        "地価":     df_land,
        "用途地域": df_zone,
    },
    join_key="市区町村コード"
)
df_master.to_csv("data/processed/master.csv", index=False, encoding="utf-8-sig")
```

---

### ▶ STEP 08：特徴量エンジニアリング

**目的**：生データから「モデルと分析で使える特徴量」を作る。

```python
import pandas as pd
import numpy as np

def feature_engineering(df: pd.DataFrame,
                        pop_col: str = None,
                        area_col: str = None,
                        year_col: str = None) -> pd.DataFrame:
    """
    政策データ分析でよく使う特徴量を生成する。
    利用する行をコメントアウトから外して使うこと。
    """
    df = df.copy()

    # ── 変化率・増減 ──────────────────────────
    # df["人口増減率"] = df[pop_col].pct_change()          # 前期比増減率
    # df["人口増減数"] = df[pop_col].diff()                # 前期比増減数

    # ── 構成比・割合 ──────────────────────────
    # df["高齢化率"]      = df["65歳以上"] / df[pop_col]
    # df["子育て世帯率"]  = df["18歳未満"] / df[pop_col]
    # df["労働力人口率"]  = df["15_64歳"]  / df[pop_col]

    # ── 密度・強度 ───────────────────────────
    # df["人口密度"]   = df[pop_col]    / df[area_col]   # 人/km²
    # df["住宅密度"]   = df["住宅数"]   / df[area_col]
    # df["地価_log"]   = np.log1p(df["地価"])             # 対数変換（歪み補正）

    # ── 標準化（地域間比較用） ───────────────────
    # from sklearn.preprocessing import StandardScaler
    # scaler = StandardScaler()
    # df["人口密度_z"] = scaler.fit_transform(df[["人口密度"]])

    # ── 空間カテゴリ ─────────────────────────
    # df["駅距離_区分"] = pd.cut(df["駅距離_m"],
    #     bins=[0, 500, 1000, 2000, np.inf],
    #     labels=["徒歩5分圏", "10分圏", "20分圏", "20分超"])

    # ── 時間フラグ ───────────────────────────
    # df["コロナ後"] = (df[year_col] >= 2021).astype(int)
    # df["リーマン後"] = ((df[year_col] >= 2009) & (df[year_col] <= 2012)).astype(int)

    # ── ラグ特徴量（時系列予測用） ────────────────
    # df["pop_lag1"] = df[pop_col].shift(1)   # 1期前の値
    # df["pop_lag5"] = df[pop_col].shift(5)   # 5期前の値

    new_cols = [c for c in df.columns if c not in df.columns]
    print(f"特徴量エンジニアリング完了：{df.shape[1]}列（新規：{len(new_cols)}列）")
    return df

df_featured = feature_engineering(df_master)
df_featured.to_csv("data/processed/featured.csv", index=False, encoding="utf-8-sig")
```
